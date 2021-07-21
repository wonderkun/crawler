> 原文链接: https://www.anquanke.com//post/id/228269 


# 三星手机内核防护技术RKP深度剖析（一）


                                阅读量   
                                **119180**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者longterm，文章来源：blog.longterm.io
                                <br>原文地址：[https://blog.longterm.io/samsung_rkp.html](https://blog.longterm.io/samsung_rkp.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01cfc8691d635a4be5.png)](https://p5.ssl.qhimg.com/t01cfc8691d635a4be5.png)



在本文中，我们的第一个目标是全面介绍三星RKP防护机制的内部原理，以便为大家考察该设备上以高特权级别执行的晦涩代码打好理论基础。在解释其原理过程中，尽管我们会以大量通过反编译而得到的代码片段为例进行演示，不过，读者也可以随意跳过这些代码。

第二个目标，也可能是更多人感兴趣的目标，是分析一个目前已经得到修复的漏洞，该漏洞允许在三星RKP的EL2上执行代码。这是一个很好的例子，说明即使一个简单的漏洞，也会危及平台安全性——因为利用漏洞只需一个调用，其作用是使在EL1处的管理程序内存进入可写状态。

在第一部分中，我们将简要地讨论Samsungs的内核缓解机制（如果完全说清楚，可能需要单独撰写一篇文章）。在第二部分中，我们将解释如何获得适用于您的设备的RKP二进制文件。

在第三部分中，我们将开始剖析Exynos设备上支持RKP的管理程序框架，然后，在第四部分中深入考察RKP的内部结构。我们将详细介绍它是如何启动的，它是如何处理内核页表的，如何保护敏感数据结构的，以及如何启用内核缓解措施的。

在第五部分也是最后一部分中，我们将为读者剖析one-liner漏洞，并考察其修复方法。 



## 引言

在移动设备领域，安全性在传统上都依赖于内核机制。但历史经验表明，内核也绝不是坚不可摧的。对于大多数Android设备来说，只要曝出内核漏洞，攻击者就可以利用它们来修改敏感的内核数据结构，提升权限，执行恶意代码。

另外，单靠在启动时确保内核完整性（使用验证启动机制）也是远远不够的。内核完整性还必须在运行时进行验证。这就是安全管理程序（security hypervisor）的设计初衷。RKP，即“Real-time Kernel Protection”，是三星管理程序实现的名称，它是三星KNOX的组成部分。

目前，已经有很多关于三星RKP的精彩研究文章，特别是Gal Beniamini的文章“Lifting the (Hyper) Visor: Bypassing Samsung’s Real-Time Kernel Protection”，以及Aris Thallas的文章“On emulating hypervisors: a Samsung RKP case study ”，都是研究该主题的必读资料。 



## 内核漏洞的利用过程

在Android系统上，典型的本地权限升级（LPE）流程为：
1. 通过泄露内核指针绕过KASLR；
1. 获得一次性的任意内核内存读/写原语；
1. 通过该原语来覆盖一个内核函数指针；
1. 调用函数将address_limit设置为-1；
1. 通过对selinux_(enable|enforcing)执行写操作绕过SELinux；
1. 通过对uid、gid、sid、capabilities执行写操作实现提权。
三星已经实现了相应的缓解措施，旨在尽可能阻止攻击者完成上述任务。例如，JOPP、ROPP和KDP就是其中的三种缓解措施。不过，需要注意的是并非所有的三星设备都具有相同的缓解措施。

以下是我们在下载各种固件更新后观察到的结果： 

[![](https://p0.ssl.qhimg.com/t013a3a44877244d441.png)](https://p0.ssl.qhimg.com/t013a3a44877244d441.png)



## JOPP机制

JOPP（Jump-Oriented Programming Prevention）机制旨在防御JOP攻击。它是三星自己实现的一种CFI解决方案。对于该防御机制，首先会通过修改版的编译器工具链，在每个函数启动前放置一个NOP指令。然后，它会使用Python脚本（Kernel/scripts/rkp_cfp/instrument.py）来处理编译后的内核二进制文件，并用一个魔力值（0xbe7bad）来替换NOP，并使用指向helper函数的直接分支替换间接分支。

其中，helper函数jopp_springboard_bl_rX（位于Kernel/init/rkp_cfp.S中）会检查目标函数前的值是否匹配魔力值，如果匹配则进行跳转，否则将会发生崩溃： 

```
.macrospringboard_blr, reg

jopp_springboard_blr_\reg:

pushRRX, xzr

ldr RRX_32, [\reg, #-4]

subsRRX_32, RRX_32, #0xbe7, lsl #12

cmp RRX_32, #0xbad

b.eq1f

...

inst0xdeadc0de //crash for sure

...

1:

pop RRX, xzr

br\reg

.endm
```



## ROPP机制

ROPP（Return-Oriented Programming Prevention）机制旨在防御ROP攻击。实际上，它就是三星自家实现的“堆栈金丝雀”。同样，该机制也会使用修改版的编译器工具链，在stp x29、x30指令之前以及ldp x29、x30指令之后放置NOP指令，并防止分配寄存器X16和X17。然后，它使用同样的Python脚本来替换汇编后的C函数的序言和尾声，具体如下所示： 

```
nop

stp x29, x30, [sp,#-&lt;frame&gt;]!

(insns)

ldp x29, x30, ...

nop
```

将被替换为：

```
eor RRX, x30, RRK

stp x29, RRX, [sp,#-&lt;frame&gt;]!

(insns)

ldp x29, RRX, ...

eor x30, RRX, RRK
```

其中RRX是X16的别名，RRK是X17的别名。

RRK被称为“线程密钥”，它们对于每个内核任务来说都是唯一的。所以，这里并不是直接把返回地址压入栈，而是先用这个密钥进行XOR处理，以防止攻击者在不知道线程密钥的情况下篡改返回地址。

线程密钥本身存储在thread_info结构体的rrk字段中，并使用RRMK进行了XOR处理。 

```
struct thread_info `{`

// ...

unsigned long rrk;

`}`;
```

RRMK被称为“主密钥”。在手机设备上，该密钥存储在DBGBCR5_EL1（Debug Breakpoint Value Register 5）系统寄存器中。它由管理程序（hypervisor）在内核初始化时设置，这一点将在后面介绍。



## KDP机制

KDP（Kernel Data Protection）是另一种支持管理程序的缓解措施。它实际上就是自家实现的数据流完整性（DFI）解决方案。该机制借助于管理程序（hypervisor）让许多敏感的内核数据结构（如页表、struct cred、struct task_security_struct、struct vfsmount、SELinux状态等）处于只读状态。



## 关于管理程序（Hypervisor）

为了理解三星的RKP缓解机制，需要先了解一些关于ARMv8平台上虚拟化扩展的基本知识。为此，我们建议您阅读“Lifting the (Hyper) Visor”一文中的“HYP 101”一节，或“ On emulating hypervisors”一文中的“ARM Architecture &amp; Virtualization Extensions”一节。

套用这些章节的说法，由于管理程序的权限级别高于内核，因此，管理程序可以完全控制内核。下面是ARMv8平台上的架构示意图：

[![](https://p5.ssl.qhimg.com/t01239c0ded6b3c4b73.png)](https://p5.ssl.qhimg.com/t01239c0ded6b3c4b73.png)

管理程序可以通过HVC（HyperVisor Call）指令接收来自内核的调用。此外，通过使用HCR（Hypervisor Configuration Register）寄存器，管理程序不仅可以捕获通常由内核处理的关键操作（如访问虚拟内存控制寄存器等），还可以处理一般的异常。

最后，管理程序使用的是第二层地址转换，又称为“第二阶段转换”。在标准的“第一阶段转换”中，一个虚拟地址（VA）被转换成中间物理地址（IPA）。然后，这个IPA由第二阶段转换成最终的物理地址（PA）。

以下是启用2阶段地址转换后的地址转换示意图：

[![](https://p5.ssl.qhimg.com/t0181e12a79a6430782.png)](https://p5.ssl.qhimg.com/t0181e12a79a6430782.png)

管理程序对自己的内存访问仍然只进行单级地址转换。 



## 小结

在系列文章中，我们将为读者深入讲解三星手机的内核防护技术。在本文中，我们为读者介绍了内核漏洞的利用流程，三星手机内建的三种防御机制，并简要介绍了管理程序，在后续的文章中，会有更多精彩内容呈现给大家，敬请期待！

**（未完待续）**
