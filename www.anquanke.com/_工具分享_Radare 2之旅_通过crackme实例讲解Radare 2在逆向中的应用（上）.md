> 原文链接: https://www.anquanke.com//post/id/86850 


# 【工具分享】Radare 2之旅：通过crackme实例讲解Radare 2在逆向中的应用（上）


                                阅读量   
                                **273767**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：megabeets.net
                                <br>原文地址：[https://www.megabeets.net/a-journey-into-radare-2-part-1/](https://www.megabeets.net/a-journey-into-radare-2-part-1/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p1.ssl.qhimg.com/t01934ee5ade16bd902.jpg)](https://p1.ssl.qhimg.com/t01934ee5ade16bd902.jpg)

译者：[**Kp_sover**](http://bobao.360.cn/member/contribute?uid=2899451914)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**序言**

在过去的一年里我研究了 radare2 很久，无论是参加CTF、逆向工程或是漏洞挖掘，我发现 radare2都能很好的提升我的工作效率， 有时候它也是我用来分析恶意软件（如溯源）的工具,不幸的是很少有人听过它，可能是因为大多数人习惯了使用 IDA Pro，OllyDBG, gdb,不管怎样，我都觉得 radare2 应该成为你工具箱中的一部分.

因为我真的特别喜欢这个项目，因此为了让大家能更好的了解并使用它，我决定专门创建一个有关 r2 系列的文章来介绍它的特点和功能，希望能让大家更好的利用它去解决工作中的问题.

[![](https://p0.ssl.qhimg.com/t01d0e172bbfbd720e8.png)](https://p0.ssl.qhimg.com/t01d0e172bbfbd720e8.png)

欢迎来到 IDA 10.0

<br>

**radare2**

radare2是一个开源的逆向工程和二进制分析框架，它的强大超出你的想象，包括反汇编、分析数据、打补丁、比较数据、搜索、替换、虚拟化等等，同事具备超强的脚本加载能力，它可以运行在几乎所有主流的平台（GNU/Linux, .Windows *BSD, iOS, OSX, Solaris…）并且支持很多的cpu架构以及文件格式，我认为所有它的这些特征恰好能表达出一个意思–那就是给予你的使用以极大的自由.

radare2工程是由一系列的组件构成，这些组件可以在 radare2 界面或者单独被使用–比如我们将要了解的rahash2, rabin2, ragg2三个组件，所有这些组件赋予了 radare2 强大的静态或动态分析、十六进制编辑以及溢出漏洞挖掘的能力.

在这之前，我们有必要知道学习使用 radare2 是一个比较艰难的过程，尽管它有直观的GUI界面，但坦白的说，它确实没有IDA用起来方便，它的学习曲线我认为大致是这样的

[![](https://p2.ssl.qhimg.com/t01c3033e941563d379.png)](https://p2.ssl.qhimg.com/t01c3033e941563d379.png)

当然我们不用因为它很复杂就退怯，我会竭尽所能让每个知识点都更清晰易懂!

在开始前，你可以在[这儿](http://rada.re/r/cmp.html)去了解我们当前正面对并试图解决的问题.

这里是有关 radare2 最新的介绍文章<br>

 Check it out @ [https://t.co/MybNPqq2CH](https://t.co/MybNPqq2CH)[@radareorg](https://twitter.com/radareorg)[#radare2](https://twitter.com/hashtag/radare2?src=hash)

— Itay Cohen (@Megabeets_Blog) [March 27, 2017](https://twitter.com/Megabeets_Blog/status/846314627059400704)

<br>

**获得radare2**

**安装**

因为 我们每天都在更新Radare2的开发，因此建议你使用最新的github版本，不要使用 stable版，因为有时候 stable版可能还没有 最新的 github 版稳定.



```
$ git clone https://github.com/radare/radare2.git
$ cd radare2
$ ./sys/install.sh
```

如果你不想使用github版，或者想要每个平台相对应的二进制文件，那就点击这里去下载吧！[download page at the radare2 website.](http://radare.org/r/down.html)

**更新**

正如我之前所说，我极力推荐你使用github上的最新版，如果你需要更新，那就太简单了，只需要下面这条命令,我每天习惯在早上更新一下 radare2 ，在这期间，你可以去喝杯咖啡..

```
$ ./sys/install.sh
```

**卸载**

oh…说实话我实在想不到任何理由，你会在看这篇文章的时候需要去卸载  radare2 ，哈哈，不过如果你随时需要，那就这样吧



```
$ make uninstall
$ make purge
```

下面正式进入正题，let's go…

这里是crackme的下载地址[here](https://github.com/ITAYC0HEN/A-journey-into-Radare2/blob/master/Part%201%20-%20Simple%20crackme/megabeets_0x1)

好的，现在假设你们已经安装好 radare2 ，crackme 文件也已经下载到机器上，我现在开始介绍 radare2 的基本用法，我将在 [Remnux](https://remnux.org/) 系统上进行操作，但是大多数命令和说明在 windows或者其他系统上都一样的.

**命令行参数**

正如大多数软件的使用一样，最好的了解它的方式就是在它后面加一个 -h 参数

```
$ r2 -h
```

在这里我不会展示它所有的用法，我只会展示平常我使用的比较多并且很重要的参数:



```
Usage: r2 [-ACdfLMnNqStuvwz] [-P patch] [-p prj] [-a arch] [-b bits] [-i file]
          [-s addr] [-B baddr] [-M maddr] [-c cmd] [-e k=v] file|pid|-|--|=
  
-d: Debug the executable 'file' or running process 'pid'
-A: Analyze executable at load time (xrefs, etc)
-q: Quiet mode, exit after processing commands
-w: Write mode enabled
-L: List of supported IO plugins
-i [file]: Interprets a r2 script
-n: Bare load. Do not load executable info as the entrypoint
-c 'command; command; ...': Run r2 and execute commands (eg: r2 's main; px 60')
-p [prj]: Creates a project for the file being analyzed
-: Opens r2 with the malloc plugin that gives a 512 bytes memory area to play with
```

**二进制信息**<br>

当我拿到一个二进制文件，首先就会去获取它的基本信息，这里将会用到 r2 框架里最强的一个工具 ：rabin2.

rabin2 可以获取包括ELF, PE, Mach-O, Java CLASS文件的区段、头信息、导入导出表、字符串相关、入口点等等，并且支持几种格式的输出文件.<br>

使用下面的命令获取更多的用法

```
man rabin2
```

我们可以通过 -I 参数 来让 rabin2 打印出二进制文件的系统属性、语言、字节序、框架、以及使用了哪些 加固技术（canary, pic, nx）.



```
$ rabin2 -I megabeets_0x1
havecode true
pic      false
canary   false
nx       false
crypto   false
va       true
intrp    /lib/ld-linux.so.2
bintype  elf
class    ELF32
lang     c
arch     x86
bits     32
machine  Intel 80386
os       linux
minopsz  1
maxopsz  16
pcalign  0
subsys   linux
endian   little
stripped false
static   false
linenum  true
lsyms    true
relocs   true
rpath    NONE
binsz    6220
```

这里你可以清晰地看到这是一个32位的 elf 文件，没有剥离符号表并且是动态链接的，它没有使用溢出隔离技术-这对于下一篇我们利用 radare2 去溢出它是很有利的信息，现在我们来运行它看看这个程序到底做了啥。

注意：尽管我让你们直接运行，但建议任何时候对一个不清楚的二进制文件都不要直接运行，最好放在一个隔离的环境，比如虚拟机下运行！



```
$ ./megabeets_0x1
 
  .:: Megabeets ::.
Think you can make it?
Nop, Wrong argument.
 
$ ./megabeets_0x1 abcdef
 
  .:: Megabeets ::.
Think you can make it?
Nop, Wrong argument.
```

开始来我们需要给它一些参数，这里输入 "abcdef"，然后还是错了，很明显，我们需要给它密码，这就是这次crackme要做的事.

下面我们用 radare2来测试这个程序：



```
$ r2 ./megabeets_0x1
 — Thank you for using radare2. Have a nice night!
[0x08048370]&gt;
```

当我们运行它的时候，它会给我们一个欢迎界面，同时给我们一个shell操作符，在这里有很多有趣和有用的命令，现在 r2 在等我们给它下一步的命令，当前它输出了一个地址 (0x08048370)，这就是它自动识别的程序入口点，我们来验证一下：



```
[0x08048370]&gt; ie
[Entrypoints]
vaddr=0x08048370 paddr=0x00000370 baddr=0x08048000 laddr=0x00000000 haddr=0x00000018 type=program1 entrypoints
```

我们用 ie 命令可以打印出程序的入口点， ie 的意思就是 info &gt;&gt; entrypoint，是不是很好记，当然我们不需要刻意去记住它，因为我们可以在任何一个命令后面添加 ? 来获得更多的子命令信息：

```
[0x08048370]&gt; i?
|Usage: i Get info from opened file (see rabin2’s manpage)
| Output mode:
| ‘*’                Output in radare commands
| ‘j’                Output in json
| ‘q’                Simple quiet output
| Actions:
| i|ij               Show info of current file (in JSON)
| iA                 List archs
| ia                 Show all info (imports, exports, sections..)
| ib                 Reload the current buffer for setting of the bin (use once only)
| ic                 List classes, methods and fields
| iC                 Show signature info (entitlements, …)
| id                 Debug information (source lines)
| iD lang sym        demangle symbolname for given language
| ie                 Entrypoint
| iE                 Exports (global symbols)
| ih                 Headers (alias for iH)
| iHH                Verbose Headers in raw text
| ii                 Imports
| iI                 Binary info
| ik [query]         Key-value database from RBinObject
| il                 Libraries
| iL                 List all RBin plugins loaded
| im                 Show info about predefined memory allocation
| iM                 Show main address
| io [file]          Load info from file (or last opened) use bin.baddr
| ir|iR              Relocs
| is                 Symbols
| iS [entropy,sha1]  Sections (choose which hash algorithm to use)
| iV                 Display file version info
| iz                 Strings in data sections
| izz                Search for Strings in the whole binary
| iZ                 Guess size of binary program
```

i 开头的命令主要是用来获取各种信息。<br>

<br>

**分析**

radare2 不会主动去分析一个文件，因为这样做的代价太大了，它需要花费很多的时间，尤其是大文件，有关分析的操作或者设置启动时不分析可以去 radare2 的博客看看 [this post](http://radare.today/posts/analysis-by-default/).

当然分析是一个必要的功能，r2 也提供了很多与之相关的功能，就像之前说的，我们可以在 'a' 后面加 '?' 来探索这个系列的命令：



```
[0x08048370]&gt; a?
|Usage: a[abdefFghoprxstc] […]
| ab [hexpairs]    analyze bytes
| abb [len]        analyze N basic blocks in [len] (section.size by default)
| aa[?]            analyze all (fcns + bbs) (aa0 to avoid sub renaming)
| ac[?] [cycles]   analyze which op could be executed in [cycles]
| ad[?]            analyze data trampoline (wip)
| ad [from] [to]   analyze data pointers to (from-to)
| ae[?] [expr]     analyze opcode eval expression (see ao)
| af[?]            analyze Functions
| aF               same as above, but using anal.depth=1
| ag[?] [options]  output Graphviz code
| ah[?]            analysis hints (force opcode size, …)
| ai [addr]        address information (show perms, stack, heap, …)
| ao[?] [len]      analyze Opcodes (or emulate it)
| aO               Analyze N instructions in M bytes
| ar[?]            like ‘dr’ but for the esil vm. (registers)
| ap               find prelude for current offset
| ax[?]            manage refs/xrefs (see also afx?)
| as[?] [num]      analyze syscall using dbg.reg
| at[?] [.]        analyze execution traces
Examples:
f ts @ S*~text:0[3]; f t @ section..text
f ds @ S*~data:0[3]; f d @ section..data
.ad t t+ts @ d:ds
```

通常我会使用 'aa' 命令来分析文件，当然使用 'aa?'可以获得更多的用法，这里由于文件很小的原因，我选择用 'aaa' 来尽可能的分析出更多更细致的信息，当然你也可以在运行 radare2的使用 -A 参数来直接分析一个文件(例如 r2 -A megabeets_0x1)



```
[0x08048370]&gt; a?
[x] Analyze all flags starting with sym. and entry0 (aa)
[0x08048370]&gt; aaa
[x] Analyze all flags starting with sym. and entry0 (aa)
[x] Analyze len bytes of instructions for references (aar)
[x] Analyze function calls (aac)
[*] Use -AA or aaaa to perform additional experimental analysis.
[x] Constructing a function name for fcn.* and sym.func.* functions (aan)
```



**Flags**

分析完成之后， r2会将所有有用的信息和特定的名字绑定在一起，比如区段、函数、符号、字符串，这些都被称作 'flags', flags 被整合进 &lt;flag spaces&gt;，一个 flag 是所有类似特征的集合，展示所有的 flag ，用 'fs' 命令：



```
[0x08048370]&gt; fs
0    4 . strings
1   35 . symbols
2   82 . sections
3    5 . relocs
4    5 . imports
5    1 . functions
```

我们可以使用 'fs &lt;flagspaces&gt;' 加 'f' 来打印出 这个 flags 下面包含的信息，使用分号来间隔多条命令(‘cmd1;cmd2;cmd3;…’).



```
[0x08048370]&gt; fs imports; f
0x08048320 6 sym.imp.strcmp
0x08048330 6 sym.imp.strcpy
0x08048340 6 sym.imp.puts
0xffffffff 16 loc.imp.__gmon_start__
0x08048350 6 sym.imp.__libc_start_main
```

我们看到 r2 列出了这个二进制文件的导出表–熟悉的 ‘strcmp’, ‘strcpy’, ‘puts’,等函数，并和它们的真实地址相关联，同样我们可以列出 字符串 flagspace:



**<br>**

**Strings**

我们看到 r2 标记出了 字符串的偏移地址、变量名.现在我们来看看字符串吧，这里有几种方式可以查看文件的字符串，你可以根据自己的需要来选择.

iz – 列出数据段里的字符串

izz – 在整个二进制文件中搜索字符串.



```
[0x08048370]&gt; iz
vaddr=0x08048700 paddr=0x00000700 ordinal=000 sz=21 len=20 section=.rodata type=ascii string=n .:: Megabeets ::.
vaddr=0x08048715 paddr=0x00000715 ordinal=001 sz=23 len=22 section=.rodata type=ascii string=Think you can make it?
vaddr=0x0804872c paddr=0x0000072c ordinal=002 sz=10 len=9 section=.rodata type=ascii string=Success!n
vaddr=0x08048736 paddr=0x00000736 ordinal=003 sz=22 len=21 section=.rodata type=ascii string=Nop, Wrong argument.n
```

还记得吗，在之前运行程序的时候就见过这些字符串了，看到 ‘success’ 了没，它可能就是我们最终成功后想要见到的字符串，现在我们知道了这个字符串的名字，那我们来看看在哪里调用了它：



```
[0x08048370]&gt; axt @@ str.*
data 0x8048609 push str._n__.::_Megabeets_::. in main
data 0x8048619 push str.Think_you_can_make_it_ in main
data 0x8048646 push str._n_tSuccess__n in main
data 0x8048658 push str._n_tNop__Wrong_argument._n in main
```

这条命令又给我们展示了另一个 r2 的功能，'axt' 命令用来在 data/code段里找寻某个地址相关的引用（更多的操作，请看 'ax?'）.'@@'就像一个迭代器，用来在地址空间里不断地匹配后面一系列相关的命令（更多操作，请看 '@@?'）， 'str.*' 是一个通配符，用来标记所有以 'str.'开头的信息，这个不光会列出字符串标志，同时也包括函数名，找到它们到底在哪里以及何处被调用。

未完待续…         
