> 原文链接: https://www.anquanke.com//post/id/87004 


# 【技术分享】如何利用SysInternals Suite来隐藏你的进程


                                阅读量   
                                **126144**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：riscybusiness.wordpress.com
                                <br>原文地址：[https://riscybusiness.wordpress.com/2017/10/07/hiding-your-process-from-sysinternals/](https://riscybusiness.wordpress.com/2017/10/07/hiding-your-process-from-sysinternals/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0125b531daee256cf8.png)](https://p4.ssl.qhimg.com/t0125b531daee256cf8.png)

<br>

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：190RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**写在前面的话**

****

我所做的研究不仅是“反分析”，而且我还想绕过安全分析并执行恶意代码。因此， 通过研究我发现了一种能够绕过常见安全分析工具的方法，今天给大家介绍的就是Sysinternals Suite。简而言之，在Sysinternals Suite的帮助下，我可以在不需要管理员权限或SEDebug权限的情况下完成我的“反分析”操作。最终实现的效果就是：恶意程序正在运行，但不会显示在Procexp.exe之中。

<br>

**Sysinternals Suite**

****

Sysinternals Suite是微软发布的一套非常强大的免费工具程序集，一共包括将近70款Windows工具。用好Windows Sysinternals Suite里的工具,你将更有能力处理Windows的各种问题,而且不用花一分钱。Sysinternals 之前为Winternals公司提供的免费工具，Winternals原本是一间主力产品为系统复原与资料保护的公司，为了解决工程师平常在工作上遇到的各种问题，便开发出许多小工具。之后他们将这些工具集合起来称为Sysinternals，并放在网络供人免费下载，其中也包含部分工具的源代码，该工具集一直以来都颇受IT专家社群的好评。

<br>

**Procexp的“隐藏复活节彩蛋”-“HiddenProcs”**

****

首先我研究的是Procexp（Procexp是windows系统进程管理的一个比较方便的工具,能快速的发现病毒,结束不必要的进程。除此之外，它还可以详尽地显示计算机信息：CPU、内存使用情况、DLL和句柄等信息）。我在IDA中对Procexp进行了分析，并且发现了一段非常有意思的代码，具体如下图所示：

[![](https://p5.ssl.qhimg.com/t0148c67f0cdf4a8dda.png)](https://p5.ssl.qhimg.com/t0148c67f0cdf4a8dda.png)

这段代码会搜索一个名叫“HiddenProcs”的MULIT_SZ寄存器值。如果这个值存在的话，它将会对一系列新生成的进程名进行解析操作。我原本打算将这些代码提取出来进行进一步分析，但不幸的是，我发现负责隐藏这些进程名的实际代码其实并不存在（不知道是不是IDA的问题），所以我其实发现的是一个无效的注册表键，于是我只能换一种办法了。

<br>

**Procexp镜像劫持一（结果：失败）**

****

如果我们可以劫持procexp的话，那么我们就可以控制它显示给用户的内容了。当你在64位操作系统中运行Procexp32.exe（或者其他的32位 Sysinternal工具）的时候，它将会在本地磁盘中导出一个64位版本的进程，然后再自动运行这个64位的版本。这样一来，如果我们能能够劫持这个进程的话，会怎么样呢？

[![](https://p2.ssl.qhimg.com/t0165cfb7c7a87806e5.png)](https://p2.ssl.qhimg.com/t0165cfb7c7a87806e5.png)

实际上，我们的目标就是如何利用Procomon32来注入Payload或运行恶意代码。这个程序负责向本地磁盘写入目标进程的64位版本并在64位操作系统中运行该进程。请大家先看看上面这张图片，注意图片顶部绿色的节点（Drop64bitProcExp函数）以及图片底部粉色的节点（CreateProcessW），这两段程序在执行的过程中，两者之间有一定的时间间隔。因此，如果我们能够保证让ProExp32.exe在上图中红色部分的地方运行得尽可能的久，我们就可以不断地尝试写入恶意进程了，但我们能不能在CreateProcess被调用之前劫持整个进程呢？

接下来我便对此进行了尝试，我开发了一个简单的PoC，然后将我的线程设置成了TIME_PRIORITY_TIME_CRITICAL，并尝试向目标程序写入我自己的代码。我的目标就是在上图所示的那两个节点之间执行我自己的恶意代码。

[![](https://p1.ssl.qhimg.com/t01f411a5a7b3d85da0.png)](https://p1.ssl.qhimg.com/t01f411a5a7b3d85da0.png)

当这个程序正在运行并且用户尝试打开ProcExp时，我得到了如下图所示的错误信息。就此看来，我的镜像劫持方法并没有成功，我还得尝试其他的方法。

[![](https://p1.ssl.qhimg.com/t012b94cf1f66715806.png)](https://p1.ssl.qhimg.com/t012b94cf1f66715806.png)

<br>

**Procexp镜像劫持二（结果：成功）**

****

在对文件生成代码（负责生成进程64位版本的代码）进行了深入分析之后，我们发现如果“wfopen_s(“ProcExp64.exe”, “wb”)”无法成功的话，ProcExp并不会立刻退出执行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010ddc8d92073eda8f.png)

那么这里肯定就存在安全漏洞了，只要“GetFileAttributes”能够成功执行，那么它将会忽略fopen可能会返回的错误信息。

[![](https://p2.ssl.qhimg.com/t01289181a866dffeee.png)](https://p2.ssl.qhimg.com/t01289181a866dffeee.png)

这样一来，镜像劫持很容易就能够实现了。我们只需要将我们自己的“ProcExp64.exe”写入到临时目录之中，然后将该程序的属性修改为“只读”。接下来，“fopen(“ProcExp64.exe” ,”wb”)”将会失败，但是当程序尝试执行“GetFileAttributes”时将会成功，而程序的执行流程将会带领我们正确地“走”到CreateProcess。

如下图所示，我们的进程在本地磁盘的临时目录%temp%中生成了一个伪造的ProcessExplorer，文件名称为“PROCEXP64.exe”，该文件的属性为“只读”属性（你可以自己在家动手尝试一下）。我生成的是一个很简单的程序，它只会在命令控制台中输出字符串“Hijacked”。具体如下图所示:

[![](https://p4.ssl.qhimg.com/t016a1238c031f6f019.png)](https://p4.ssl.qhimg.com/t016a1238c031f6f019.png)

接下来，当我们尝试运行Procexp.exe时，它便会触发其中的安全漏洞，并且运行我们所生成的“PROCEXP64.exe”。

劫持效果如下图所示：

[![](https://p1.ssl.qhimg.com/t01646b0d2639a9afd1.png)](https://p1.ssl.qhimg.com/t01646b0d2639a9afd1.png)

我设计的这个PoC只是想告诉大家这种劫持方法其实是可行的，但我认为我们其实可以做得更加好，因为上面给出的这种劫持方法只能适用于在64位操作系统中运行32位Sysinternals工具的场景。

<br>

**DLL劫持（最终的解决方案）**

****

接下来给大家介绍的就是我最终的解决方案了，即最终的PoC。首先我们来看一看Sysinternal的注册表键，大家可以看到其中一个名叫“DbghelpPath”的注册表键。这个注册表键对于绝大多数应用程序来说都是可写的（USER注册表单元）：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019e0729cbde8e5b40.png)

DbghelpPath注册表键指向的是一个存放“dbghelp.dll”文件的可信路径。非常好，我所要做的就是劫持这个路径。我给出的PoC代码可以让这个注册表键指向临时目录%TEMP%，然后我再向临时目录(%TEMP%/DbgHelp.dll)中存放一个我自己的恶意dbghelp.dll文件就可以了。当Procexp开始运行之后，它将会加载这个路径下的DLL文件。当它成功加载了我的恶意DLL文件之后，我们就可以利用ProcExp程序来隐藏我们的恶意进程了。点击【[这里](https://github.com/RISCYBusiness/Jadoube/blob/master/AntiSysInternals/AntiSysInternals/Procexp.cpp)】获取我的PoC代码。

整个劫持过程需要涉及到对ProcExp进程的运行逻辑以及链表结构进行逆向分析，下图显示的就是我们的PoC代码成功利用ProcExp运行了一个名叫“Malicious.exe”的恶意进程：

[![](https://p3.ssl.qhimg.com/t01377a985aaac0dfab.png)](https://p3.ssl.qhimg.com/t01377a985aaac0dfab.png)



**总结**

****

整个劫持过程其实并不难，而最棒的一点就在于，几乎每一款SysInternal工具都拥有这样一个可写的DbgHelp路径注册表键，所以从理论上来说，你可以利用任何一款Sysinternal Suite工具来实现本文所介绍的攻击技术。
