> 原文链接: https://www.anquanke.com//post/id/85411 


# 【技术分享】在macOS内存中运行可执行文件


                                阅读量   
                                **111379**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.cylance.com
                                <br>原文地址：[https://blog.cylance.com/running-executables-on-macos-from-memory](https://blog.cylance.com/running-executables-on-macos-from-memory)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t012834ad5ce31bff4b.png)](https://p0.ssl.qhimg.com/t012834ad5ce31bff4b.png)



翻译：[胖胖秦](http://bobao.360.cn/member/contribute?uid=353915284)

预估稿费：150RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

作为一名安全研究员，我一直在研究恶意软件攻击设备时使用到的新兴技术。虽然Windows是最常见的目标，但是对于macOS（以前称为OS X），并不缺乏新兴的技术。在这篇文章中，我将讨论一些在macOS（直到Sierra）上执行多级攻击载荷的技术。

用于执行多级攻击载荷的常见技术是拥有一个可以从内存中载入可执行文件而不是从计算硬盘上载入的初始攻击载荷，它可以降低被检测的风险。一般来说，当尝试从macOS的内存中加载代码时，第一步是找到动态加载器dyld，以便于加载第二级攻击载荷。一旦你在内存中找到dyld，你可以解析它的Mach-O头来定位函数NSCreateObjectFileImageFromMemory（创建一个NSObjectFileImage）和NSLinkModule（链接库到当前进程和运行构造函数）来加载可执行文件。

<br>

**深入了解dyld**

你在MacOS执行一个动态链接的二进制文件时，内核会做的第一件事就是从二进制Mach-O的加载命令中检索动态加载器的位置，并加载它。因此，dyld是第一个被加载到进程的地址空间的Mach-O。内核通过二进制文件的vmaddr和ASLR slide来确定dyld的候选地址。然后内核将Mach-O的sections映射到第一个可用未分配的内存地址中，内存地址要大于或等于到候选地址。<br>

如下所示，在Sierra之前的macOS版本中，dyld的vmaddr是0x7fff5fc00000（DYLD_BASE）：

MacOS的10.10.5（Yosemite）

```
$ otool -l /usr/lib/dyldx
/usr/lib/dyld:
Load command 0
      cmd LC_SEGMENT_64
    cmdsize 552
    segname __TEXT
      vmaddr 0x00007fff5fc00000
...
```

在内存中定位dyld是很容易的; 从DYLD_BASE开始搜索,找到的第一个Mach-O映像就是dyld。然后可以通过内存中的dyld地址减去DYLD_BASE来计算用于dyld的ASLR slide。确定ASLR slide对于解析符号很重要，因为符号表的nlist_64结构中的n_value包含需要被偏移的基地址。

在Sierra中,dyld变成了动态映射（vmaddr为0）：

macOS 10.12.2 (Sierra)

```
$ otool -l /usr/lib/dyld
/usr/lib/dyld:
Mach header
magic cputype cpusubtype caps    filetype ncmds sizeofcmds      flags
  0xfeedfacf 16777223          3  0x00           7    14       1696 0x00000085
Load command 0
    cmd LC_SEGMENT_64
  cmdsize 552
  segname __TEXT
    vmaddr 0x0000000000000000
...
```

这意味着,现在,在内存中已加载的可执行映像相邻处可以找到dyld，而不是DYLD_BASE中的第一个Mach-O映像。因为没有固定的基地址，我们现在不能再轻松计算ASLR slide。幸运的是，我们不再关心这个值，因为符号表的nlist_64结构的n_value现在包含了从dyld开始的偏移; 一旦你在内存中找到dyld的地址，你可以解析它的符号。我们将在下面的解析符号部分详细讨论这一点。

<br>

**dyld在内存中的位置**



那么我们如何在内存中搜索dyld呢？在地址空间中搜索特定映像的正确方法是递归地使用vm_region。然而，通过这种方法产生的shellcode是冗长和繁琐的。幸运的是，有一个选择; 如果我们发现一个系统调用，它接受一个指针并根据地址是否被映射返回不同的返回值，我们可以使用它。chmod系统调用就是这样。

如果路径指针在进程分配的地址空间的之外,chmod返回EFAULT; 如果路径不存在，则返回ENOENT。因此，我们可以使用以下函数来找到dyld：

```
int find_macho(unsigned long addr, unsigned long *base) `{`
    *base = 0;
    while(1) `{`
        chmod((char *)addr, 0777);
        if(errno == 2 &amp;&amp; /*ENOENT*/
          ((int *)addr)[0] == 0xfeedfacf /*MH_MAGIC_64*/) `{`
            *base = addr;
            return 0;
        `}` 
        addr += 0x1000;
    `}`  
    return 1;
`}`
```

在Sierra之前的macOS版本中，可以这样做：

```
unsigned long dyld;
if(find_macho(DYLD_START, &amp;dyld)) return
```

在Sierra，我们必须调用find_macho两次：一次找到已加载的二进制，一次找到dyld：

```
unsigned long binary, dyld;
if(find_macho(EXECUTABLE_BASE_ADDR, &amp;binary)) return 1;
if(find_macho(binary + 0x1000, &amp;dyld)) return 1;
```



**解析符号**



找到dyld的字符串表可以通过解析其加载命令，并使用以下代码（基址是内存中的dyld地址）查找符号表以及内存中的linkedit和text segments 来完成：

```
lc = (struct load_command *)(base + sizeof(struct mach_header_64));
for(int i=0; i&lt;((struct mach_header_64 *)base)-&gt;ncmds; i++) `{`
    if(lc-&gt;cmd == 0x2/*LC_SYMTAB*/) `{`
        symtab = (struct symtab_command *)lc;
    `}` else if(lc-&gt;cmd == 0x19/*LC_SEGMENT_64*/) `{`
        switch(*((unsigned int *)&amp;sc-&gt;segname[2])) `{` //skip __
        case 0x4b4e494c:    //LINK
            linkedit = (struct segment_command_64 *)lc;
            break;
        case 0x54584554:    //TEXT
            text = (struct segment_command_64 *)lc;
            break; 
`}` 
`}` 
lc = (struct load_command *)((unsigned long)lc + lc-&gt;cmdsize);
`}`
```

上面的代码略过内存中的mach_header_64结构，然后遍历各种加载命令结构。我们保存LC_SYMTAB的地址和与__LINKEDIT和__TEXT段相关的两个LC_SEGMENT_64命令。使用指向这些结构体的指针，我们现在可以计算内存中的字符串表的地址：

```
unsigned long file_slide = linkedit-&gt; vmaddr - text-&gt; vmaddr - linkedit-&gt; fileoff; 
strtab =（char *）（base + file_slide + symtab-&gt; stroff）;
```

要遍历字符串表，我们需要遍历符号表的nlist_64结构。每个nlist_64结构体包含一个到字符串表（n_un.n_strx）的偏移量：

```
char * name = strtab + nl [i] .n_un.n_strx;
```

并不是使用传统的哈希算法来匹配字符串表中的符号名，我写了一个帮助脚本（symbolyzer.py）生成唯一offset/ int对，通过以下方式识别：

```
$ nm / usr / lib / dyld | cut -d“”-f3 | 排序| uniq | 蟒蛇symbolyzer.py
$ nm /usr/lib/dyld | cut -d" " -f3 | sort | uniq | python symbolyzer.py
...
_NSCreateObjectFileImageFromFile[25] = 0x466d6f72
...
```

symbolyzer.py的代码（[https://github.com/CylanceVulnResearch/osx_runbin/blob/master/symbolyzer.py](https://github.com/CylanceVulnResearch/osx_runbin/blob/master/symbolyzer.py)）可以在GitHub上找到这里。

正如你可以看到，NSCreateFileImageFromMemory的offset / int对是25＆0x466d6f72。这意味着如果我们字符串表中的给定字符串索引为25，并且它等于0x466d6f72，则我们发现了一个匹配。在我们的匹配对中包含一个逻辑终止符NULL就可以匹配所有符号字符串。

<br>

**加载可执行文件**

在MacOS的内存中加载代码的最常见的方法就是在macOS bundle上调用NSCreateObjectFileImageFromMemory,随后调用NSLinkModule,然后调用NSAddressOfSymbol来查找已知函数。 “The Mac Hacker's Handbook”中为NSLinkModule指出：“目前的实现仅限用于插件的Mach-O MH_BUNDLE类型。” dyld的头文件进一步说明“NSObjectFileImage只能用于MH_BUNDLE文件”。经过快速证实,这是真的; 如果文件类型的mach_header_64结构不是MH_BUNDLE（0x8），NSCreateObjectFileImageFromMemory会失败。幸运的是，使用以下两行代码可以很容易改变结构的文件类型：

```
int type = ((int *)binbuf)[3];
if(type != 0x8) ((int *)binbuf)[3] = 0x8; //change to mh_bundle type
```

然后我们可以在Mach-O映象内解析NSLinkModule返回的NSModule对象来找到入口点; 在Sierra中，Mach-O映象从偏移0x48变为0x50。通过迭代该映像的加载命令，我们可以找到LC_MAIN命令并获取入口点的偏移量。只需将此偏移量添加到Mach-O基址中即可得到入口点：

```
unsigned long execute_base = *(unsigned long *)((unsigned long)nm + 0x50);
struct entry_point_command *epc;  
if(find_epc(execute_base, &amp;epc)) `{`  //loops over commands and finds LC_MAIN
fprintf(stderr, "Could not find entry point command.n");
goto err;
`}`
int(*main)(int, char**, char**, char**) = (int(*)(int, char**, char**, char**))(execute_base+ epc-&gt;entryoff);
char *argv[]=`{`"test", NULL`}`;
int argc = 1;
char *env[] = `{`NULL`}`;  
char *apple[] = `{`NULL`}`;
return main(argc, argv, env, apple);
```

这篇文章的所有的POC代码（[https://github.com/CylanceVulnResearch/osx_runbin](https://github.com/CylanceVulnResearch/osx_runbin)）都可以在GitHub上找到。 

<br>

**引用**

1. [http://phrack.org/issues/64/11.html](http://phrack.org/issues/64/11.html)  <br>

2. [http://www.blackhat.com/presentations/bh-dc-09/Iozzo/BlackHat-DC-09-Iozzo-let-your-mach0-fly-whitepaper.pdf](http://www.blackhat.com/presentations/bh-dc-09/Iozzo/BlackHat-DC-09-Iozzo-let-your-mach0-fly-whitepaper.pdf) 

3. [https://lowlevelbits.org/parsing-mach-o-files/](https://lowlevelbits.org/parsing-mach-o-files/) 

4. [https://www.mikeash.com/pyblog/friday-qa-2012-11-09-dyld-dynamic-linking-on-os-x.html](https://www.mikeash.com/pyblog/friday-qa-2012-11-09-dyld-dynamic-linking-on-os-x.html) 

5. [https://opensource.apple.com/source/xnu/xnu-2782.1.97/bsd/kern/kern_exec.c](https://opensource.apple.com/source/xnu/xnu-2782.1.97/bsd/kern/kern_exec.c) 

6. [https://developer.apple.com/legacy/library/documentation/Darwin/Reference/ManPages/man2/chmod.2.html](https://developer.apple.com/legacy/library/documentation/Darwin/Reference/ManPages/man2/chmod.2.html) 

7. [https://www.amazon.com/Mac-Hackers-Handbook-Charlie-Miller/dp/0470395362](https://www.amazon.com/Mac-Hackers-Handbook-Charlie-Miller/dp/0470395362) 

8. [https://opensource.apple.com/source/cctools/cctools-384.1/man/NSModule.3.auto.html](https://opensource.apple.com/source/cctools/cctools-384.1/man/NSModule.3.auto.html) 


