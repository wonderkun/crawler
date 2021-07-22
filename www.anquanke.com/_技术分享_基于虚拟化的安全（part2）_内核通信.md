> 原文链接: https://www.anquanke.com//post/id/85496 


# 【技术分享】基于虚拟化的安全（part2）：内核通信


                                阅读量   
                                **91474**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：amossys.fr
                                <br>原文地址：[http://blog.amossys.fr/virtualization-based-security-part2.html](http://blog.amossys.fr/virtualization-based-security-part2.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t01a979755ff4f422b2.jpg)](https://p1.ssl.qhimg.com/t01a979755ff4f422b2.jpg)**

****

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：140RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**传送门**

[**【技术分享】基于虚拟化的安全（part1）：引导过程******](http://bobao.360.cn/learning/detail/3493.html)



**0x00 前言**

本文是基于虚拟化的安全和设备保护功能的第二篇文章。在[第一篇](http://bobao.360.cn/learning/detail/3493.html)中，我们涵盖了系统引导过程，从Windows bootloader到VTL0启动。在本文中，我们将解释在VTL0和VTL1之间如何内核通信。因为他们使用hypercall来通信，我们将首先介绍Hyper-V的hypercall的实现，然后是内核如何使用他们来通信。最终，我列出了在这个工作中我们确定的所有的不同的hypercall和安全服务调用。

<br>

**0x01 Hyper-V hypercall**

在VTL0和VTL1之间的内核通信使用Hyper-V hypercall。这些hypercall通过VMCALL指令执行，同时hypercall调用号存储在RCX寄存器，且RDX指向一个包含参数的Guest物理页（GPA）。如果RCX是0x10000，这个hypercall是一个“快速”hypercall，参数和返回值存储在XMM寄存器中。为了执行这个调用，Windows使用一个hypercall跳板，它是一个小的执行VMCALL和RET的fastcall例程。

这个例程存储在“hypercall页“。这个页包含5个跳板，并且在它启动时由Hyper-V提供给winload.efi，其将在VTL0和VTL1地址空间中复制它。这5个跳板的主要不同点是第一个只有VMCALL/RET，但是下面四个（他们连续存储）都是将RCX存储到RAX，然后将一个固定的值存入RCX。第二和第三个的固定值是0x11，其他的是0x12。

这四个跳板被不同的VTL使用。每个内核可能使用一个专门的hypercall向Hyper-V请求0xD0002虚拟处理器寄存器的值（Hyper-V内部值，可以用来查询或设置标识符），这将返回两个偏移。这些偏移与hypercall页相关，并且在内核调用正确的跳板时使用。实际上，VTL1和VTL0使用0x11跳板来相互通信，VTL1使用0x12跳板来完成它的初始化。

Hypercall页的内容如下：

[![](https://p4.ssl.qhimg.com/t0114b8c64a6f54dffc.png)](https://p4.ssl.qhimg.com/t0114b8c64a6f54dffc.png)

可以看到5个跳板，分别在偏移0x00，0x04，0x0F，0x1D和0x28处。注意他们的内容可以使用WinDbg在崩溃转储时获得，或者从Hyper-V二进制（适用于Intel / AMD的Hvix64.exe / hvax64.exe）内部码中获得。

注意：几个hypercall可以指定RCX的高位的DWORD的12个最低有效位中的数据大小。这个大小不是以字节为单位的数据大小，但是与当前调用有关，可能表示入口次数等。

对于一个hypercall的例子，VTL1的ShvlProtectContiguousPages的hypercall（12）的参数是下面的一个结构体：

[![](https://p1.ssl.qhimg.com/t01e698b656f1856789.png)](https://p1.ssl.qhimg.com/t01e698b656f1856789.png)

为了告诉Hyper-V pfn的参数大小，RCX的高位DWORD必须包含它的元素数量。对于只有一个入口和快速hypercall来说，RCX的值将是0x10010000C。

<br>

**0x02 安全内核的hypercall**

两个VTL能够执行多个hypercall，以便和Hyper-V通信。他们可能执行相同的hypercall，但是Hyper-V将拒绝一些来自VTL0调用的hypercall。两个VTL也使用一个专门的hypercall来相互通信。总结见下图：

[![](https://p3.ssl.qhimg.com/t016afb34cb5308e1e6.png)](https://p3.ssl.qhimg.com/t016afb34cb5308e1e6.png)

让我们首先描述“VTL1到Hyper-V“的hypercall（绿色的）。我们将描述0x11的hypercall。

VTL1使用3种hypercall跳板：

ShvlpHypercallCodePage，等价于NTOS的HvlpHypercallCodePage（偏移0），并且指向第一个跳板

ShvlpVtlReturn，将0x11传给RCX，使得VTL0和VTL1可以通信

ShvlpVtlCall，将0x12传给RCX，只在VTL1初始化时使用

后两个使用0xD0002虚拟寄存器得到（ShvlpGetVpRegister返回值的低24位，每个偏移是一个12位的长度）。这两个偏移指向0x11和0x12跳板。

顺便说一句，VTL0 NTOS内核使用同一进程得到它的HvlpVsmVtlCallCodeVa值（用来VTL0和VTL1通信的hypercall跳板），但是得到的是颠倒的结果。这是为什么我们相信使用这些跳板，任何VM能从Hyper-V得到相同的hypercall页，并且能请求到虚拟寄存器的值。Hyper-V将根据VTL或VM返回不同的偏移。

下表是可能的VTL1 hypercall：

[![](https://p2.ssl.qhimg.com/t01b1d23689b52a9ef0.png)](https://p2.ssl.qhimg.com/t01b1d23689b52a9ef0.png)

<br>

**0x03 VTL0和VTL1的转换**

几乎所有的NTOS 的“Vsl“前缀的函数都以VslpEnterIumSecureMode结尾，伴随着一个安全服务调用号（SSCN）。这个函数调用HvlSwitchToVsmVtl1，它使用HvlpVsmVtlCallVa hypercall跳板（通常的hypercall使用HvcallCodeVa跳板）。SSCN被复制到RAX，RCX设置为0x11。

Hyper-V分发0x11 hypercall到securekernel.exe的函数SkpReturnFromNormalMode，然后调用IumInvokeSecureService（实际上我们不确定IumInvokeSecureService有没有被直接调用，我们认为SkpReturnFromNormalMode一定被调用了，以便在安全服务调用完成后使IumInvokeSecureService返回到VTL0）。IumInvokeSecureService是一个大的switch/case块，处理所有的SSCN。

最后，SkCallNormalMode被调用，以SkpPrepareForReturnToNormalMode结尾。实际上，安全内核的NTOS调用被认为是“假的返回“到VTL0，因为他们也包含了0x11的hypercall。

我们已经确认了所有的可能的SSCN。对于每一个，我们都指出了调用函数名。但是相应的参数必须通过逆向VTL0的调用者或VTL1的调用源来确定。

[![](https://p0.ssl.qhimg.com/t01eca09cc1816ec46a.png)](https://p0.ssl.qhimg.com/t01eca09cc1816ec46a.png)

如你所见，几个调用函数是未知的。这是因为他们没有执行明显的调用，我们没有花大量时间去继续分析。

<br>

**0x04 总结**

本文描述了基于虚拟化的安全的VTL0-VTL1的内核通信。

如果你想知道更多的关于Hyper-V的信息，你能读下面两篇文章：

[http://hvinternals.blogspot.fr/2015/10/hyper-v-debugging-for-beginners.html](http://hvinternals.blogspot.fr/2015/10/hyper-v-debugging-for-beginners.html)

[http://hvinternals.blogspot.fr/2015/10/hyper-v-internals.html](http://hvinternals.blogspot.fr/2015/10/hyper-v-internals.html)

下面的计划，我们将发布第三篇关于VBS的文章，将聚焦于HVCI内部，尤其是[W^X](https://en.wikipedia.org/wiki/W%5EX)VTL0内核保护。

<br>



**传送门**

[**【技术分享】基于虚拟化的安全（part1）：引导过程******](http://bobao.360.cn/learning/detail/3493.html)

<br>
