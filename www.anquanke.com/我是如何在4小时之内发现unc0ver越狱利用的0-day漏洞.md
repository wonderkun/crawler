> 原文链接: https://www.anquanke.com//post/id/210337 


# 我是如何在4小时之内发现unc0ver越狱利用的0-day漏洞


                                阅读量   
                                **217878**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者blogspot，文章来源：googleprojectzero.blogspot.com
                                <br>原文地址：[https://googleprojectzero.blogspot.com/2020/07/how-to-unc0ver-0-day-in-4-hours-or-less.html](https://googleprojectzero.blogspot.com/2020/07/how-to-unc0ver-0-day-in-4-hours-or-less.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01e0e76a4f55b0b670.jpg)](https://p5.ssl.qhimg.com/t01e0e76a4f55b0b670.jpg)



## 前言

2020年5月23日下午3点，unc0ver针对iOS 13.5（当时的最新版本）发布了越狱方法，其中利用了0-day漏洞并经过严重混淆。当天晚上7点，我已经成功定位到越狱过程中利用的0-day漏洞，并将漏洞报告给Apple。次日凌晨1点，我已经向Apple发送了PoC和分析信息。而这篇文章将详细介绍我的整个漏洞探索过程。



## 初步定位

我想要找到unc0ver利用的漏洞，并迅速将其报告给Apple，以证明对漏洞利用进行混淆，并不能有效地防止漏洞利用方法落入攻击者的手中。

在下载并解压缩unc0ver IPA之后，我将主要可执行文件加载到IDA中进行查看。但遗憾的是，二进制文件被严重混淆了，因此静态分析中出现的问题已经超出了我的能力范围。

[![](https://p2.ssl.qhimg.com/t013ce2f5d56429ef53.png)](https://p2.ssl.qhimg.com/t013ce2f5d56429ef53.png)

接下来，我将unc0ver应用程序加载到运行iOS 13.2.3的iPod Touch 7上，尝试运行漏洞利用程序。通过探索应用程序界面，用户无法控制可以利用哪个漏洞来实现设备的越狱，因此我希望unc0ver仅利用了一个0-day漏洞，并且没有在iOS 13.3或更低版本上利用oob_timestamp漏洞。

当我单击“越狱”按钮时，我突然产生了一个想法：之前我写过一些内核漏洞利用程序，当时了解到大多数基于内存损坏的漏洞利用程序都有一个“关键段”，在此期间内核状态被破坏，如果漏洞利用程序的其余部分没有继续运行，那么系统将会不稳定。因此，我灵机一动，双击Home键打开应用程序切换器，并关闭了unc0ver应用程序。

设备立即就出现了错误（Panic）。

```
panic(cpu 1 caller 0xfffffff020e75424): "Zone cache element was used after free! Element 0xffffffe0033ac810 was corrupted at beginning; Expected 0x87be6c0681be12b8 but found 0xffffffe003059d90; canary 0x784193e68284daa8; zone 0xfffffff021415fa8 (kalloc.16)"
Debugger message: panic
Memory ID: 0x6
OS version: 17B111
Kernel version: Darwin Kernel Version 19.0.0: Wed Oct  9 22:41:51 PDT 2019; root:xnu-6153.42.1~1/RELEASE_ARM64_T8010
KernelCache UUID: 5AD647C26EF3506257696CF29419F868
Kernel UUID: F6AED585-86A0-3BEE-83B9-C5B36769EB13
iBoot version: iBoot-5540.40.51
secure boot?: YES
Paniclog version: 13
Kernel slide:     0x0000000019cf0000
Kernel text base: 0xfffffff020cf4000
mach_absolute_time: 0x3943f534b
Epoch Time:        sec       usec
  Boot    : 0x5ec9b036 0x0004cf8d
  Sleep   : 0x00000000 0x00000000
  Wake    : 0x00000000 0x00000000
  Calendar: 0x5ec9b138 0x0004b68b

Panicked task 0xffffffe0008a4800: 9619 pages, 230 threads: pid 222: unc0ver
Panicked thread: 0xffffffe004303a18, backtrace: 0xffffffe00021b2f0, tid: 4884
  lr: 0xfffffff007135e70  fp: 0xffffffe00021b330
  lr: 0xfffffff007135cd0  fp: 0xffffffe00021b3a0
  lr: 0xfffffff0072345c0  fp: 0xffffffe00021b450
  lr: 0xfffffff0070f9610  fp: 0xffffffe00021b460
  lr: 0xfffffff007135648  fp: 0xffffffe00021b7d0
  lr: 0xfffffff007135990  fp: 0xffffffe00021b820
  lr: 0xfffffff0076e1ad4  fp: 0xffffffe00021b840
  lr: 0xfffffff007185424  fp: 0xffffffe00021b8b0
  lr: 0xfffffff007182550  fp: 0xffffffe00021b9e0
  lr: 0xfffffff007140718  fp: 0xffffffe00021ba30
  lr: 0xfffffff0074d5bfc  fp: 0xffffffe00021ba80
  lr: 0xfffffff0074d5d90  fp: 0xffffffe00021bb40 
  lr: 0xfffffff0075f10d0  fp: 0xffffffe00021bbd0
  lr: 0xfffffff00723468c  fp: 0xffffffe00021bc80
  lr: 0xfffffff0070f9610  fp: 0xffffffe00021bc90
  lr: 0x00000001bf085ae4  fp: 0x0000000000000000
```

这看上去似乎很有希望，我得到的错误消息中描述，`kalloc.16`分配区（大小最大为16个字节的通用分配）中有一处释放后使用（UAF）。但是，这表明可能存在内存损坏。为了进行进一步调查，我需要分析回溯。

在等待IDA处理iPod的内核缓存的过程中，我尝试了一些现成的实验。由于许多漏洞利用都使用Mach端口作为基本原语，因此我编写了一个会搅乱`ipc.ports`区域，创建碎片，并混合可利用空间表（freelist）的应用程序。当我随后运行unc0ver应用程序时，该漏洞利用仍然有效，这表明它可能不依赖于对Mach端口分配的堆。

接下来，由于panic日志中提到了`kalloc.16`，因此我决定编写一个应用程序，该应用程序在unc0ver漏洞利用期间在后台连续分配，并释放给`kalloc.16`。这个想法在于，如果unc0ver依赖于重新分配`kalloc.16`的分配，那么我的应用程序可能会抢占该Slot，这可能会导致漏洞利用策略失败，并且可能导致内核崩溃。可以肯定的是，我的应用程序在后台对`kalloc.16`进行操作的过程中，如果点击“越狱”按钮，将会立即引起内核崩溃。

在进行健全性检查的过程中，我尝试更改应用程序，以尝试不同区域，这次选择的是`kalloc.32`而不再是`kalloc.16`。在这一次，漏洞利用成功运行，那么也就证明了，`kalloc.16`实际上才是漏洞利用的关键分配区域。

最后，一旦IDA完成对iPod内核缓存的分析后，我开始抽象地表示从崩溃日志中收集的堆栈跟踪。

```
Panicked task 0xffffffe0008a4800: 9619 pages, 230 threads: pid 222: unc0ver
Panicked thread: 0xffffffe004303a18, backtrace: 0xffffffe00021b2f0, tid: 4884
  lr: 0xfffffff007135e70
  lr: 0xfffffff007135cd0
  lr: 0xfffffff0072345c0
  lr: 0xfffffff0070f9610
  lr: 0xfffffff007135648
  lr: 0xfffffff007135990
  lr: 0xfffffff0076e1ad4  # _panic
  lr: 0xfffffff007185424  # _zcache_alloc_from_cpu_cache
  lr: 0xfffffff007182550  # _zalloc_internal
  lr: 0xfffffff007140718  # _kalloc_canblock
  lr: 0xfffffff0074d5bfc  # _aio_copy_in_list
  lr: 0xfffffff0074d5d90  # _lio_listio
  lr: 0xfffffff0075f10d0  # _unix_syscall
  lr: 0xfffffff00723468c  # _sleh_synchronous
  lr: 0xfffffff0070f9610  # _fleh_synchronous
  lr: 0x00000001bf085ae4
```

其中，对`lio_listio()`的调用立刻引起了我的注意。在我近期研究iOS内核漏洞利用的不久之前，我记得在之前LightSpeed的漏洞利用中，所使用的易受攻击的系统调用正是`lio_listio()`。于是，我重新阅读了Synacktiv的博客文章，以回顾该漏洞，随即发现了另一个问题：在LightSpeed竞争条件中被双重释放的目标对象是一个驻留在`kalloc.16`中的`aio_lio_context`对象。另外，unc0ver应用程序中存在的大量线程，进一步支持了竞争条件的这个思路。

到现在，我认为我已经有足够的证据可以联系Apple。经过初步分析，我发现该漏洞就是LightSpeed，可能是它的变体，或者就是本身。



## 编写PoC证明漏洞存在

接下来，我想通过编写PoC来触发漏洞，从而验证漏洞确实存在。我先尝试了LightSpeed文章中使用的原始PoC，但是在经过一分钟的运行后，没有出现崩溃。这表明，也许这里的0-day漏洞，是原始LightSpeed漏洞的变体。

为了找到更多信息，我开始进行更深入地调查。我查看XNU源代码，以尝试发现漏洞，同时我还使用checkra1n/pongoOS在内核缓存中修补`lio_listio()`，然后运行漏洞利用程序。从源代码上，我根本看不出来原始漏洞是如何修复的，这对我来说毫无意义。因此，我准备将精力集中在内核修补上。

要查看引导修补的内核高速缓存，这一过程非常复杂，但我们可以利用checkm8。我下载了checkra1n，并将iPod引导到pongoOS Shell中。以pongoOS repo中的示例为指导，我创建了一个可加载的pongo模块，该模块将禁用checkra1n内核补丁，而是应用我自己的补丁。在这里，之所以禁用checkra1n内核补丁，是因为我担心unc0ver会检测到checkra1n，并采取反分析措施。

我的第一个测试只是将无效的指令操作码插入到`lio_listio()`函数中，以便在调用时会出现崩溃。但没有想到的是，设备启动正常，然后在我点击“越狱”时，出现了崩溃。这意味着，unc0ver是唯一调用了`lio_listio()`函数的进程。

接下来，我修补了负责分配`aio_lio_context`对象的代码，该对象在原始LightSpeed漏洞中被双重释放，通过这样，我们可以让`kalloc.48`来进行分配，而不再是`kalloc.16`。

```
FFFFFFF0074D5D54     MOV     W8, #0xC ; patched to #0x23
FFFFFFF0074D5D58     STR     X8, [SP,#0x40] ; alloc size
FFFFFFF0074D5D5C     ADRL    X2, _lio_listio.site.5
FFFFFFF0074D5D64     ADD     X0, SP, #0x40
FFFFFFF0074D5D68     MOV     W1, #1 ; can block
FFFFFFF0074D5D6C     BL      kalloc_canblock
FFFFFFF0074D5D70     CBZ     X0, loc_FFFFFFF0074D6234
FFFFFFF0074D5D74     MOV     X19, X0 ; lio_context
FFFFFFF0074D5D78     MOV     W1, #0xC ; size_t
FFFFFFF0074D5D7C     BL      _bzero
```

这个想法在于，通过增加对象的分配大小，导致unc0ver的漏洞利用策略失败，因为它尝试用`kalloc.16`中的替换对象去替换意外释放的`kalloc.48`上下文中的对象，而这根本不会成功。可以肯定的是，有了这个补丁程序，unc0ver停在了“漏洞利用内核”阶段，而没有产生崩溃。

然后，我又进行了更多的实验，对函数的各个位置进行了修补，以转储传递给`lio_listio()`的参数和数据缓冲区，以便可以与原始LightSpeed PoC中使用的值进行比较。我的想法是，如果我发现任何实质性差异，那么我就可以考虑使用源代码的变体。但是，除了将字段`aio_reqprio`设置为`gang`之外，unc0ver传递给`lio_listio()`的参数与原始PoC中的参数之间没有差别。

此时，看来这个0-day可能就是原始的LightSpeed漏洞，而不是变体。因此，我又开始分析原始的PoC，查看未触发漏洞利用的原因是否由于特定的技术已经被缓解。负责重新分配`kalloc.16`分配的代码引起了我的关注：

```
/* not mandatory but used to make the race more likely */
/* this poll() will force a kalloc16 of a struct poll_continue_args */
/* with its second dword as 0 (to collide with lio_context-&gt;io_issued == 0) */
/* this technique is quite slow (1ms waiting time) and better ways to do so exists */
int n = poll(NULL, 0, 1);
```

我以前从来没有见过使用`poll()`作为重新分配原语。从直观上看，使用基于Mach端口的重新分配策略似乎更有希望，因此我用从`oob_timestamp`复制的Out-of-line Mach端口喷射替换了这部分代码。果然，在几秒钟之内，我们的PoC就成功触发了。而这里就是需要对PoC进行的唯一修改。



## 补丁历史

在有了可以使用的PoC之后，我重试了原始的LightSpeed PoC，发现如果将其运行足够长的时间，最终还是能导致崩溃。因此，这是重新引入漏洞的另一种情况，该漏洞可以通过简单的回归测试来确定。

因此，让我们回到源头，看看是否可以弄清楚发生了什么。如前所述，当我第一次检查XNU源代码并查看`lio_listio()`是如何被破坏的时候，我实际上根本无法确定该漏洞最初是如何修补的。但是现在回想，似乎并不是毫无踪迹可寻。

最初的LightSpeed文章很好地描述了该漏洞，我在这里就不做赘述，我强烈建议各位读者阅读这篇文章。从更高的角度来看，我们尚不清楚是哪个函数释放的`aio_lio_context`对象，因为执行异步I/O的辅助线程和`lio_listio()`函数自身都可以做到这一点。

正如在文章中提到的那样，该漏洞的原始修补程序只是在可能双重释放的情况下不再释放`aio_lio_context`对象：

“该修补程序将潜在的UaF固定在`lio_context`上。但是，这样的修复方式忽略了在修复之前处理的错误情况。最终的结果导致可以使用`lio_listio()`分配`aio_lio_context`，而内核将永远不会释放`aio_lio_context`。这样一来，我们就获得了一个愚蠢的DoS，还会导致最新版本的内核（包括iOS 12）崩溃。

对于剩下的这部分，我们可以在以后看到，Apple是否愿意修复补丁中引入的DoS风险。”

事实证明，Apple最终决定在iOS 13中修复了内存泄漏漏洞，但是这样做似乎导致重新引入了双重释放的竞争条件：

```
case LIO_NOWAIT:
+       /* If no IOs were issued must free it (rdar://problem/45717887) */
+       if (lio_context-&gt;io_issued == 0) `{`
+           free_context = TRUE;
+       `}`
        break;
```

iOS 13中的代码与iOS 11并不完全相同，但是在语义上是等效的。如果我们理解原始LightSpeed漏洞，就可以通过查看XNU源代码之间的差异，轻松地判断出二者之间的关联性。进行简单的回归测试后，就可以轻松发现这个漏洞。

总而言之，LightSpeed漏洞已经在iOS 12中实现了修复，但是补丁没有解决根本问题，只是将竞争条件双重释放转换为内存泄漏。此后，在iOS 13中，发现了这个内存泄漏漏洞，并通过重新引入原始漏洞实现了“修复”，但在此过程中仍然没有解决问题的根本原因。通过执行博客文章的原始PoC，可以证明其安全性的降低。

我们可以在Synacktiv博客的后续文章中，阅读有关这一漏洞的更多信息。



## 总结

iOS 12.4中的SockPuppet和iOS 13中的LightSpeed都表明，Apple至少没有针对这些旧的安全漏洞进行有效的回归测试。开展有效的回归测试是基本软件测试的必要条件，也是漏洞利用的一个共同起点。

不过，在漏洞利用程序公开后，Apple及时地修复了这个问题。现在的情况在于，在公开发布PoC之前很久，攻击者就已经发现了这些问题。因此，攻击者可能正在积极地开展漏洞利用的回归测试。

另外，在此次研究中，我们也证明了，混淆处理并不会阻止攻击者迅速发现漏洞利用方法。事实证明，我的分析过程中非常幸运，依靠我之前编写内核漏洞利用的经验，我迅速找到了该漏洞利用的替代方案，并且由于我一直在关注过去出现的漏洞，所以我也刚好熟悉所利用的特定漏洞。但是，对于持续关注Apple设备的攻击者或组织，他们也很可能拥有与我相同的优势。
