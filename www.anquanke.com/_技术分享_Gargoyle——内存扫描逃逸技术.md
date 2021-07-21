> 原文链接: https://www.anquanke.com//post/id/85682 


# 【技术分享】Gargoyle——内存扫描逃逸技术


                                阅读量   
                                **85126**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：jlospinoso.github.io
                                <br>原文地址：[https://jlospinoso.github.io/security/assembly/c/cpp/developing/software/2017/03/04/gargoyle-memory-analysis-evasion.html](https://jlospinoso.github.io/security/assembly/c/cpp/developing/software/2017/03/04/gargoyle-memory-analysis-evasion.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01e25d0d24dd1b83b7.png)](https://p0.ssl.qhimg.com/t01e25d0d24dd1b83b7.png)

****

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**0x00 前言**

Gargoyle是一种在非可执行内存中隐藏可执行代码的技术。在一些程序员定义的间隔，gargoyle将苏醒，且一些ROP标记它自身为可执行，且做一些事：

[![](https://p4.ssl.qhimg.com/t01cc4f850e08dcc746.png)](https://p4.ssl.qhimg.com/t01cc4f850e08dcc746.png)

这个[技术](https://github.com/JLospinoso/gargoyle)是针对32位的Windows阐述的。在本文中，我们将深入探讨其实现细节。<br>

**<br>**

**0x01 实时内存分析**

执行实时内存分析是一个相当大代价的操作，如果你使用Windows Defender，你可能在这个问题上就到头了（谷歌的反恶意软件服务）。因为程序必须在可执行的内存中，用于减少计算负担的一种常用技术是只限制可执行代码页的分析。在许多进程中，这将数量级的减少要分析的内存数量。

Gargoyle表明这是个有风险的方式。通过使用Windows异步过程调用，读写内存能被作为可执行内存来执行一些任务。一旦它完成任务，它回到读写内存，直到定时器过期。然后重复循环。

当然，没有Windows API InvokeNonExecutableMemoryOnTimerEx。得到循环需要做一些操作。

<br>

**0x02 Windows异步过程调用（APC）**

[异步编程](https://msdn.microsoft.com/en-us/library/windows/desktop/ms681951(v=vs.85).aspx)使一些任务延迟执行，在一个独立的线程上下文中执行。每个线程有它自己的APC队列，并且当一个线程进入[alertable状态](https://msdn.microsoft.com/en-us/library/windows/desktop/aa363772(v=vs.85).aspx)，Windows将从[APC队列](https://msdn.microsoft.com/en-us/library/windows/desktop/ms684954(v=vs.85).aspx)中分发任务到等待的线程。

有一些方法来插入APC：

[ReadFileEx](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365468(v=vs.85).aspx)

[SetWaitableTimer](https://msdn.microsoft.com/en-us/library/windows/desktop/ms686289(v=vs.85).aspx)

[SetWaitableTimerEx](https://msdn.microsoft.com/en-us/library/windows/desktop/dd405521(v=vs.85).aspx)

[WriteFileEx](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365748(v=vs.85).aspx)

进入alertable状态的方法：

[SleepEx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms686307(v=vs.85).aspx)

[SignalObjectAndWait](https://msdn.microsoft.com/en-us/library/windows/desktop/ms686293(v=vs.85).aspx)

[MsgWaitForMultipleObjectsEx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms684245(v=vs.85).aspx)

[WaitForMultipleObjectsEx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms687028(v=vs.85).aspx)

[WaitForSingleObjectEx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms687036(v=vs.85).aspx)

我们要使用的组合是用CreateWaitableTimer创建一个定时器，然后使用SetWaitableTimer插入APC队列：

[![](https://p5.ssl.qhimg.com/t0148a9073a93149525.png)](https://p5.ssl.qhimg.com/t0148a9073a93149525.png)

默认的安全属性是fine，我们不想手动重置，并且我们不想要一个命名的定时器。因此对于CreateWaitableTimer所有的参数是0或者nullptr。这个函数返回一个HANDLE，表示我们新的定时器。接下来，我们必须配置它：

[![](https://p3.ssl.qhimg.com/t015349fbb1401d0c25.png)](https://p3.ssl.qhimg.com/t015349fbb1401d0c25.png)

第一个参数是我们从CreateWaitableTimer得到的句柄。参数pDueTime是一个指向LARGE_INTEGER的指针，指定第一个定时器到期的时间。例如，我们简单的设为0（立即过期）。lPeriod定义了过期间隔（毫秒级）。这个决定了gargoyle调用的频率。

下个参数pfnCompletionRoutine将是我们要努力的主题。这是来自等待线程的Windows调用的地址。听起来很简单，除非在可执行内存中分发的APC没有一个gargoyle代码。如果我们将pfnCompletionRoutine指向gargoyle，我们将[触发数据执行保护（DEP）](https://msdn.microsoft.com/en-us/library/windows/desktop/aa366553(v=vs.85).aspx)。

取而代之，我们使用一些[ROP gadget](https://en.wikipedia.org/wiki/Return-oriented_programming)，将重定向执行线程的栈到lpArgToCompletionRoutine指向的地址。当ROP gadget执行，指定的栈在调用gargoyle第一条指令前调用VirtualProtectEx来标记gargoyle为可执行。

最后一个参数与在定时器到期后是否唤醒计算机有关。我们设置为false。

<br>

**0x03 Windows数据执行保护和VirtualProtectEx**

最后是[VirtualProtectEx](https://msdn.microsoft.com/en-us/library/windows/desktop/aa366899(v=vs.85).aspx)，用来修改各种内存保护属性：

[![](https://p5.ssl.qhimg.com/t01f75ab14528f606fb.png)](https://p5.ssl.qhimg.com/t01f75ab14528f606fb.png)

我们将在两种上下文中调用VirtualProtectEx：在gargoyle完成执行后（在我们触发线程alertable之前）和在gargoyle开始执行之前（在线程分发APC之后）。看资料了解详情。

在这个PoC中，我们将gargoyle，跳板，ROP gadget和我们的读写内存都放进同一个进程中，因此第一个参数hProcess设置为[GetCurrentProcess](https://msdn.microsoft.com/en-us/library/windows/desktop/ms683179(v=vs.85).aspx)。下一个参数lpAddress与gargoyle的地址一致，dwSize与gargoyle的可执行内存大小一致。我们提供期望的[保护属性](https://msdn.microsoft.com/en-us/library/windows/desktop/aa366786(v=vs.85).aspx)给flNewProtect。我们不关心老的保护属性，但是不幸的是lpflOldProtect不是一个可选的参数。因此我们将将它设为一些空内存。

唯一根据上下文不同的参数是flNewProtect。当gargoyle进入睡眠，我们想修改它为PAGE_READWRITE或0x04。在gargoyle执行前，我们想标记它为PAGE_EXECUTE_READ或0x20。

<br>

**0x04 栈跳板**

注意：如果你不熟悉x86调用约定，本节将比较难以理解。对于新人，可以参考我的文章x86调用约定。

通常，ROP gadget被用来对抗DEP，通过构建调用VirtualProtectEx来标记栈为可执行，然后调用到栈上的一个地址。这在利用开发中经常很有用，当一个攻击者能写非可执行内存。可以将一定数量的ROP gadget放在一起做相当多的事。

不幸的是，我们不能控制我们的alerted线程的上下文。我们能通过pfnCompletionRoutine控制eip，并且线程栈中的指针位于esp+4，即调用函数的第一个参数（WINAPI/__stdcall调用约定）。

幸运的是，我们已经在APC入队前就执行了，因此我们能在我们的alerted线程中小心的构建一个新的栈（栈跳板）。我们的策略是找到代替esp指向我们栈跳板的ROP gadget。下面的形式的就能工作：

[![](https://p5.ssl.qhimg.com/t01cfa68ec75fae7794.png)](https://p5.ssl.qhimg.com/t01cfa68ec75fae7794.png)

有点诡异，因为函数通常不以pop esp/ret结束，但是由于[可变长度的操作码](https://cseweb.ucsd.edu/~hovav/dist/rop.pdf)，Intel x86汇编过程会产生非常密集的可执行内存。不管怎样，在32位的mshtml.dll的偏移7165405处有这么一个gadget：

[![](https://p4.ssl.qhimg.com/t0112f7a986fef070c0.png)](https://p4.ssl.qhimg.com/t0112f7a986fef070c0.png)

注意：感谢[Sascha Schirra](https://github.com/sashs)的[Ropper](https://github.com/sashs/Ropper)工具。

在我们调用SetWaitableTimer时，这个gadget将设置esp为我们放入lpArgToCompletionRoutine中的任何值。剩下的事就是将lpArgToCompletionRoutine指向一些构造的栈内存。栈跳板看起来如下：

[![](https://p1.ssl.qhimg.com/t01120e94abb90cac22.png)](https://p1.ssl.qhimg.com/t01120e94abb90cac22.png)

我们设置lpArgToCompletionRoutine为void* VirtualProtectEx参数，以便ROP gadget能ret到执行VirtualProtectEx。当VirtualProtectEx得到这个调用，esp将指向void* return_address。我们可以设置这个为我们的gargoyle。

<br>

**0x05 gargoyle**

让我们暂停片刻，看下在我们创建定时器和启动循环之前创建的读写Workspace。这个Workspace包含3个主要内容：一些配置帮助gargoyle启动自身，栈空间和StackTrampoline：

[![](https://p1.ssl.qhimg.com/t010fba175f45ececf8.png)](https://p1.ssl.qhimg.com/t010fba175f45ececf8.png)

你已经看见了StackTrampoline，和stack是一个内存块。SetupConfiguration：

[![](https://p3.ssl.qhimg.com/t01e81dd21ac4bb9cd1.png)](https://p3.ssl.qhimg.com/t01e81dd21ac4bb9cd1.png)

在PoC的main.cpp中，SetupCOnfiguration这么设置：

[![](https://p4.ssl.qhimg.com/t016c084582779f135f.png)](https://p4.ssl.qhimg.com/t016c084582779f135f.png)

非常简单。简单的指向多个Windows函数和一些有用的参数。

现在你有了Workspace的大概印象，让我们回到gargoyle。一旦栈跳板被VirtualProtectEx调用，gargoyle将执行。这一刻，esp指向old_protections，因为VirtualProtect使用WINAPI/__stdcall约定。

注意我们放入了一个参数（void* setup_config）在StackTrampoline的末尾。这是方便的地方，因为如果它是以__cdecl/__stdcall约定调用gargoyle的第一个参数。

这将使得gargoyle能在内存中找到它的读写配置：

[![](https://p0.ssl.qhimg.com/t01bcf2cecd67d577b4.png)](https://p0.ssl.qhimg.com/t01bcf2cecd67d577b4.png)

现在我们准备好了。Esp指向了Workspace.stack。我们在ebx中保存了Configuration对象。如果这是第一次调用gargoyle，我们将需要建立定时器。我们通过Configuration的initialized字段来检查这个：

[![](https://p2.ssl.qhimg.com/t01cb01d839a9daeef7.png)](https://p2.ssl.qhimg.com/t01cb01d839a9daeef7.png)

如果gargoyle已经初始化了，我们跳过定时器创建。

[![](https://p4.ssl.qhimg.com/t01f8efed6063a7e2d9.png)](https://p4.ssl.qhimg.com/t01f8efed6063a7e2d9.png)

注意，在reset_trampoline中，我们重定位了跳板中VirtualProtectEx的地址。在ROP gadget ret后，执行VirtualProtectEx。当它完成后，它在正常的函数执行期间将破环栈上的地址。

你能执行任意代码。对于PoC，我们弹出一个对话框：

[![](https://p2.ssl.qhimg.com/t018563756c73bd8eff.png)](https://p2.ssl.qhimg.com/t018563756c73bd8eff.png)

一旦我们完成了执行，我们需要构建调用到VirtualProtectEx，然后WaitForSingleObjectEx。我们实际上构建了两个调用到WaitForSingleObjectEx，因为APC将从第一个返回并继续执行。这启动了我们定义的循环APC：

[![](https://p2.ssl.qhimg.com/t01ae805e605db2b5a7.png)](https://p2.ssl.qhimg.com/t01ae805e605db2b5a7.png)

<br>

**0x06 测试**

PoC的代码在[github](https://github.com/JLospinoso/gargoyle)上，且你能简单的测试，但是你必须安装：

[Visual studio](https://www.visualstudio.com/downloads/) 2015 Community，但是其他版本也能用

[Netwide Assembler](http://www.nasm.us/pub/nasm/releasebuilds/?C=M;O=D) v2.12.02 x64，但是其他版本也能用。确保nasm.exe在你的路径中。

克隆gargoyle：

```
git clone https://github.com/JLospinoso/gargoyle.git
```

打开Gargoyle.sln并构建。

你必须在和setup.pic相同的目录运行gargoyle.exe。默认解决方案的输出目录是Debug或release。

每15秒，gargoyle将弹框。当你点击确定，gargoyle将完成VirtualProtectEx/WaitForSingleObjectEx调用。

有趣的是，使用Systeminternal的[VMMap](https://technet.microsoft.com/en-us/sysinternals/vmmap.aspx)能验证gargoyle的PIC执行。如果消息框是激活的，gargoyle将被执行。反之则没有只想能够。PIC的地址在执行前使用stdout打印。
