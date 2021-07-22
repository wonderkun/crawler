> 原文链接: https://www.anquanke.com//post/id/86975 


# 【技术分享】利用WinDbg脚本对抗反调试技术


                                阅读量   
                                **121373**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：vallejo.cc
                                <br>原文地址：[https://vallejo.cc/2017/07/16/anti-antidebugging-windbg-scripts/](https://vallejo.cc/2017/07/16/anti-antidebugging-windbg-scripts/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0105cc2393e6bed4a6.jpg)](https://p3.ssl.qhimg.com/t0105cc2393e6bed4a6.jpg)

译者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**简介**



在这篇文章中，我将向读者分享一些WinDbg脚本，它们在逆向采用了反调试技术的恶意软件的时候，非常有用——至少对我来说非常有用。当然，我不是Windows内核方面的专家，所以一方面在脚本中难免会发现错误，另一方面，我正在做的事情确实非常疯狂，所以极有可能会对计算机造成损害。

这些脚本适用于WinDbg（不是本地的）内核调试。您需要一台机器来运行WinDbg，并将其连接到被调试的另一台机器上。就我而言，我使用Windows主机来运行WinDbg，然后用它来调试VMware机器（我使用VirtualKD作为调试器连接，因为这样的话，连接速度要快得多），当然，您也可以使用其他配置。

关于环境的搭设，各位可以参考下列文章： 

[VirtualKD – Installation](http://virtualkd.sysprogs.org/tutorials/install/)

[Starting with Windows Kernel Exploitation – part 1 – setting up the lab](https://hshrzd.wordpress.com/2017/05/28/starting-with-windows-kernel-exploitation-part-1-setting-up-the-lab/)

[Setting Up Kernel-Mode Debugging of a Virtual Machine Manually](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/attaching-to-a-virtual-machine--kernel-mode-)

好了，下面开始对各个脚本逐一介绍。 

<br>

**Anti-rdtsc-trick 脚本**

****

参数：**$$&gt;a&lt;anti_antidebug_rdtsc.wdbg**

脚本：

[anti_antidebug_rdtsc.wdbg](https://github.com/vallejocc/Reversing-Arsenal/blob/master/WinDbg/anti_antidebug_rdtsc.wdbg)

有关这个技巧的信息在互联网上有很多。利用它，您可以读取pafish代码： 

[https://github.com/a0rtega/pafish/blob/master/pafish/cpu.c](https://github.com/a0rtega/pafish/blob/master/pafish/cpu.c) 

有一些工具会安装一个驱动程序来对付它。 WinDbg脚本以类似的方式工作，但它不需要驱动程序，它可以同时在x86和x64中运行（不知道是否有相应的工具可以在64位上使用）。

它的工作原理：它启用cr4的标志2（TSD时间戳禁用）。RDTSC是一种特权指令。之后，它会启用Windbg中的相应选项，以便在用户模式异常发生时停下来（gflag + sue + soe，gflags 0x20000001）。

然后它开始捕获0xc0000096异常（执行特权指令）。通过这种方式，当应用程序执行RDTSC时，会发生异常，而windbg则会捕获该异常。这时，脚本会检查RDTSC的内容，0x310f。 如果是RDTSC指令，则跳过该指令，ip = ip + 2。 最后，它完成下列设置工作：edx = 0，eax = last_counter + 1。对于执行RDTSC的应用程序来说，将看到RDTSC每执行一次，相应的值就增1。 

脚本： 



```
$$set rdtsc as priv instruction, then catch 
    $$exceptions for priv instructions and skip 
    $$rdtsc(eip=eip+2) and set edx:eax = last rdtsc 
    $$returned value +1
    $$use $t9 for counter
    r $t9 = 0
    $$rdtsc = privileged instruction
    r cr4 = cr4 | 4
    $$Stop on exception
    !gflag +soe
    $$Stop on unhandled user-mode exception
    !gflag +sue
    $$disable access violation (we have enabled exception 
    $$in user mode, and access violation will cause lot of 
    $$exceptions)
    sxd av
    $$we enable to catch privileged instructions execution 
    $$(we have converted rdtsc in priv ins with cr4)
    $$in this moment we check if it is rdtsc, and in this case, 
    $$we jump over the instruction and we set eax=0 edx=0
    sxe -c ".if((poi(eip)&amp;0x0000ffff)==0x310f)`{`.printf "rdtscrn";r eip = eip+2;r eax=@$t9;r edx=0;r $t9=@$t9+1; gh;`}`" c0000096
```

<br>

**对运行中进程重命名的脚本**

****

参数： ** $$&gt;a&lt;change_process_name.wdbg &lt;main module of the process&gt;**

脚本： 

[change_process_name.wdbg](https://github.com/vallejocc/Reversing-Arsenal/blob/master/WinDbg/change_process_name.wdbg)

如果我们想给一个进程改名的话，则需要修改**EPROCESS-&gt; SeAuditProcessCreationInfo.ImageFileName**： 

[![](https://p1.ssl.qhimg.com/t010b5ffd9dcf1f47e9.png)](https://p1.ssl.qhimg.com/t010b5ffd9dcf1f47e9.png)

该脚本需要以进程的主映像的名称作为其参数。它使用该imagename搜索进程，找到后，修改其名称最后一个字母，具体来说就是将相应的编码+1。例如： 

**$$&gt;a&lt;change_process_name.wdbg vmtoolsd.exe**

就本例来说，该脚本将重命名**vmtoolsd.exe – &gt; vmtoolse.exe**。 当恶意软件搜索这个进程时，就找不到它了。但是，重命名的进程可以继续运行而不会出现任何问题。 

脚本： 

```
aS stage @$t19
    .block
    `{`
     .sympath "SRV*c:symcache*http://msdl.microsoft.com/download/symbols";
     .reload
    `}`
    .block
    `{`
       r stage = 2
       .printf "xxxx"
       .foreach (processes_tok `{` !process /m $`{`$arg1`}` 0 0 `}`)
       `{`
         .if($scmp("$`{`processes_tok`}`","PROCESS")==0)
         `{`
           .if($`{`stage`}`==2)
           `{`
             $$stage==2 is used to skip the first apparition of 
             $$PROCESS string in the results of !process 0 0
             r stage = 0
           `}`
           .else
           `{` 
             r stage = 1
           `}`
         `}`
         .elsif($`{`stage`}`==1)
         `{`
           .printf /D "&lt;b&gt;Renaming process $`{`processes_tok`}`&lt;/b&gt;n"
           r stage = 0
           r $t4 = $`{`processes_tok`}`
           r $t0 = @@c++( ( ( nt!_EPROCESS * ) @$t4 )-&gt;SeAuditProcessCreationInfo.ImageFileName )
           r $t1 = (poi @$t0)&amp;0xffff
           r $t2 = (poi (@$t0+2))&amp;0xffff
           r $t3 = (poi (@$t0+@@c++(#FIELD_OFFSET(nt!_UNICODE_STRING, Buffer))))
           db ($t3 + $t1 - a)
           $$go to end of buffer of _UNICODE_STRING, and go back 0xa bytes.
           $$For example &lt;filepath....&gt;&lt;lastbyte&gt;.exe. We locate on 
           $$lastbyte, and we increase 1 the value of last byte
           $$For example &lt;fullpath&gt;vmtoolsd.exe, will be modified to 
           $$&lt;fullpath&gt;vmtoolse.exe
           eb ($t3 + $t1 - a) ((poi($t3 + $t1 - a)&amp;0xff)+1)
           !process @$t4 0
         `}`
       `}`
    `}`
```



**用于重命名内核对象的脚本**

****

参数： ** $$&gt;a&lt;change_object_name.wdbg &lt;full object path + name&gt;**

脚本： 

[change_object_name.wdbg](https://github.com/vallejocc/Reversing-Arsenal/blob/master/WinDbg/change_object_name.wdbg)

这个脚本可以用来重命名内核中的对象。

首先，它获取与对象相关联的_OBJECT_HEADER结构的地址（它从 !object 命令的结果获取地址）。

获取**_OBJECT_HEADER**后，可以在_OBJECT_HEADER – 0x10（x86）或-0x20（x64）的地址中获取**_OBJECT_HEADER_NAME_INFO**结构： 

[![](https://p2.ssl.qhimg.com/t014503e9134bfd9a53.png)](https://p2.ssl.qhimg.com/t014503e9134bfd9a53.png)

为了修改对象的名称，我们必须将_UNICODE_STRING改为_OBJECT_HEADER_NAME_INFO。

下面是取自pafish一个实际的例子： 

 [![](https://p0.ssl.qhimg.com/t01573c5f9f1c1dc51f.png)](https://p0.ssl.qhimg.com/t01573c5f9f1c1dc51f.png)

它会尝试打开一些设备。实际上，vmci是一个设备，而hgfs是设备的符号链接。无论如何，这两个都是内核对象，它们有一个_OBJECT_HEADER和一个_OBJECT_HEADER_NAME_INFO。

我们调用该脚本： 

**$$&gt;a&lt;change_object_name.wdbg global??hgfs -&gt; new name global??agfs**

**$$&gt;a&lt;change_object_name.wdbg devicesvmci -&gt; new name devicesamci**

当pafish尝试CreateFileA这些设备时，它会失败，并且基于这种技术的VM检测也会失效。

脚本： 

```
aS stage @$t19
    aS x64arch $t18
    aS objhnameinfodisp $t17
    .block
    `{`
       .sympath "SRV*c:symcache*http://msdl.microsoft.com/download/symbols";
       .reload
    `}`
    .block
    `{`
       $$is x64?
       r x64arch = 0; 
       r objhnameinfodisp = 0x10;
       .foreach( tok `{` .effmach `}` ) 
       `{`
         .if($scmp("$`{`tok`}`","x64")==0)
         `{`
           r x64arch = 1;
           r objhnameinfodisp = 0x20;
           .break;
         `}`;
       `}`;
    `}`
    r stage = 0
    .foreach( tok `{` !object "$`{`$arg1`}`" `}` )
    `{`
       .printf "$`{`tok`}`rn"
       .if($`{`stage`}`==1)
       `{`
         .echo $`{`tok`}`
         dt _OBJECT_HEADER $`{`tok`}` 
         r $t0 = $`{`tok`}` 
         dt _OBJECT_HEADER_NAME_INFO (@$t0-$`{`objhnameinfodisp`}`)
        
         $$ $t0 -&gt; OBJECT_HEADER_NAME_INFO
         r $t0 = @$t0 - $`{`objhnameinfodisp`}`
         $$ $t0 -&gt; OBJECT_HEADER_NAME_INFO.UNICODE_STRING
         r $t0 = @$t0 + @@c++(#FIELD_OFFSET(_OBJECT_HEADER_NAME_INFO, Name))
     
         $$ $t0 -&gt; OBJECT_HEADER_NAME_INFO.UNICODE_STRING.Buffer
         r $t0 = @$t0 + @@c++(#FIELD_OFFSET(_UNICODE_STRING, Buffer))
         db poi $t0
        
         $$change the first letter for 'a'
         eb (poi $t0) 'a'
         .printf "--------------------rn"
         db poi $t0
         .break
       `}` 
     
       .if($`{`stage`}`==0)
       `{`
         .if($scmp("$`{`tok`}`","ObjectHeader:")==0)
         `{`
             r stage = 1
         `}`
       `}`
    `}`
```



**未完待续…**

****

对于诸如注册表项（HKLM  SOFTWARE  VMware，Inc.  VMware Tools，…）或文件（vmmouse.sys，…）来说，逃避检测最简单的方法是删除/重命名所检测的注册表项或文件。pafish也使用乐VMware MAC地址，但vmware允许您修改适配器的MAC。

将来，我们还会为其他类似的东西些脚本，例如内存中的设备或进程等等，也许它们更难以隐藏。当然，一旦写好了，我会专门发文张贴。

希望本文对读者有所帮助。 
