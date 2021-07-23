> 原文链接: https://www.anquanke.com//post/id/215434 


# Windows漏洞利用开发现状Part2


                                阅读量   
                                **235443**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者crowdstrike，文章来源：crowdstrike.com
                                <br>原文地址：[https://www.crowdstrike.com/blog/state-of-exploit-development-part-2/](https://www.crowdstrike.com/blog/state-of-exploit-development-part-2/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01f6a76fa58d0722a0.jpg)](https://p0.ssl.qhimg.com/t01f6a76fa58d0722a0.jpg)



## 简介

在第一篇文章中，我们介绍了Windows系统上的二进制漏洞利用，包括一些传统的和现代的缓解机制，利用这些机制，研究者必须在当今的环境中应对。在本文中，我们将详细介绍Microsoft采用的更多缓解机制。



## 现代缓解机制1：页表随机化（Page Table Randomization）

正如上篇文章中所介绍的，对于现代的漏洞利用来说，PTE非常重要。您可能还记得，PTE负责强制执行内存的各种权限和属性。从历史上看，计算一个虚拟地址的PTE非常简单，因为PTE的base在很长一段时间内都是静态的。获取虚拟地址的PTE的过程是：
- 通过除以分页大小(通常为4KB)，将虚拟地址转换为虚拟页码(VPN)
- 将VPN乘以一个PTE的大小(64位系统上是8个字节)
- 将PTE的base添加到上一操作的结果中
用编程术语来说，这实质上等同于按索引引用的数组，例如PteBase[VirtualPageNumber]。

在早期的Windows版本中，PTE的base位于静态虚拟地址fffff680`00000000。但是，在Windows 10 1607（RS1）之后，PTE的base是随机的，也就是说这个过程现在不是那么简单了。

恢复指定虚拟地址的PTE的一种简单方法是取消PTE base的随机化。Windows API公开了一个名为nt!MiGetPteAddress的函数，Morten Schenk在2017年的BlackHat中提到已经在之前的漏洞利用研究中使用到。

这个函数执行与上面描述的完全相同的routine来访问虚拟地址的PTE。但是，它在函数内部以0x13的偏移量动态填充PTEs的base。

[![](https://p2.ssl.qhimg.com/t016d6e6272b37733a0.png)](https://p2.ssl.qhimg.com/t016d6e6272b37733a0.png)

利用任意读原语，可以使用此技术提取页表项的base。有了PTE的base，上述繁琐的计算原语仍然有效。

注意，Windows 10 1607（RS1）不仅随机化了PTE base，而且还随机化了内核内存的其他14个区域的base。虽然PTE base是最重要的变化，但这些其他的随机化也有助于阻止某些类型的内核利用，这超出了本文的范围。



## 现代缓解机制2：ACG

Windows 10中引入的任意代码保护（ACG）是一种可选的内存破坏缓解机制，旨在阻止任意代码执行。尽管ACG的设计考虑到了Microsoft Edge，但它可以应用于大多数进程。

ROP是绕过DEP的技术，最常用于返回Windows API函数，例如VirtualProtect()。利用这个函数和用户提供的参数，攻击者可以动态地将shellcode所在的内存权限更改为RWX；使用ACG，这将变为不可能。

[![](https://p2.ssl.qhimg.com/t01b49f1c89583188b5.png)](https://p2.ssl.qhimg.com/t01b49f1c89583188b5.png)

ACG防止修改现有代码，例如，生成RWX的恶意shellcode。如果一个人具有读写原语并且绕过CFG和ASLR，则ACG通过动态操纵内存权限，缓解了利用ROP绕过DEP的能力。

另外，ACG阻止分配新的可执行内存。用于ROP的另一个常用API VirtualAlloc()不能为其分配可执行内存。本质上，内存不能动态地更改为PAGE_EXECUTE_READWRITE。

尽管ACG是一个用户模式缓解机制，但它是通过一个名为nt!MiArbitraryCodeBlocked的Windows API函数在内核中实现的。这个函数主要检查进程是否启用了ACG。

[![](https://p5.ssl.qhimg.com/t013e147a99b06bb6c3.png)](https://p5.ssl.qhimg.com/t013e147a99b06bb6c3.png)

进程的EPROCESS对象是进程的内核表示形式，它有一个名为MitigationFlags的联合数据类型成员，用于跟踪进程启用的各种缓解。EPROCESS还包含另一个名为MitigationFlagsValues的成员，它提供了可读的MitigationFlags变体。

让我们研究一下启用ACG的Edge content进程（MicrosoftEdgeCP.exe)）。

[![](https://p0.ssl.qhimg.com/t016fa36d4d23ad6eb5.png)](https://p0.ssl.qhimg.com/t016fa36d4d23ad6eb5.png)

在引用EPROCESS成员MitigationFlagsValues时，我们可以看到DisableDynamicCode(即ACG)被设置为0x1，这表示该进程启用了ACG。

[![](https://p0.ssl.qhimg.com/t010dc16d44c90a1cb2.png)](https://p0.ssl.qhimg.com/t010dc16d44c90a1cb2.png)

此时，如果为进程动态创建了可执行代码，并且设置了此标志，那么函数检查将返回STATUS_DYNAMIC_CODE_BLOCKED失败，从而导致崩溃。

此外，通过解析所有EPROCESS对象，可以获得启用ACG的所有运行进程的列表。

[![](https://p5.ssl.qhimg.com/t0113fb888a277e2c57.png)](https://p5.ssl.qhimg.com/t0113fb888a277e2c57.png)

尽管绕过ACG的方法不多，但逻辑导致研究员攻击JIT (just-in-time)编译器。JavaScript是一种解释性语言，也就是说它不会直接被编译成机器码。相反，JavaScript使用“字节码”。但是，在某些情况下，浏览器使用JIT编译器将JavaScript字节码动态编译为实际的机器码，以提高性能。这表示，通过设计，JIT编译器总是在创建动态可执行代码。由于这个功能，ACG与JIT不兼容，而且在windows1703（RS2）之前，Edge内部的功能有限。

Alex Ionescu在Ekoparty的一次演讲中提到，在1703 (RS2)更新之前，由于ACG的原因，Edge有一个线程负责JIT。因为JIT与ACG不兼容，所以这个“JIT线程”没有启用ACG，那也就是说如果可以破坏这个线程，那么就有可能绕过ACG。为了解决这个问题，Microsoft在Windows 1703 (RS2)中为Edge JIT编译创建了一个单独的进程。为了让Edge content进程(非JIT进程)利用JIT编译，JIT进程使用Edge进程的句柄，以便在每个非JIT进程中执行JIT工作。

ACG有一个“universal bypass”，即研究员可以完全远离代码执行。通过使用代码重用技术，可以用ROP、JOP或COP编写整个payload，这将“遵循”ACG的规则。与使用代码重用技术返回API不同，一种选择是使用它来构造整个payload，另外，被破坏的浏览器需要利用完整的代码重用来沙盒逃逸。这并不理想，因为用ROP、JOP或COP编写payload非常耗时。

使用Edge的JIT结构也绕过了ACG。Google Project Zero 的Ivan Fratic 在Infiltrate 2018 上发表了一篇演讲，解释了Edge的Content进程获取JIT进程句柄的方式是有风险的。

Edge Content进程利用Windows API函数DuplicateHandle()来创建JIT进程可以利用的自己的句柄。这样做的问题是，DuplicateHandle()函数需要已经具有PROCESS_DUP_HANDLE权限的目标进程的句柄。Content Edge进程利用这些权限获取具有大量访问权限的JIT进程的句柄，因为PROCESS_DUP_HANDLE允许具有另一个进程句柄的进程复制具有最大访问权限的伪句柄，这将允许从禁用ACG的Content Edge进程访问JIT进程。这可能会对系统造成破害，因为它利用Content进程，然后转向不受ACG保护的JIT进程加以利用。

这些问题最终在Windows 10 RS4中得到了解决，很明显，Edge现在使用的是Chromium引擎，需要注意的是，它还利用了ACG和进程外JIT编译器。



## 现代缓解机制3：CET

由于CFG没有考虑返回的边界情况，Microsoft需要快速开发一个解决方案来保护返回地址。正如微软安全响应中心的Joe Bialek在OffensiveCon 2018演讲中提到，微软最初使用一种名为RFG的基于软件的缓解机制来解决这个问题。

RFG的目的是解决这个问题，通过在函数prologue中使用额外的代码将函数的返回地址推送到一个称为“shadow stack”的东西上，它仅包含函数的合法返回指针的副本，并且不包含任何参数。这个shadow stack不能从用户模式访问，因此“受内核保护”。在函数的尾部，将shadow stack的返回地址副本与作用域内返回地址进行比较。如果它们不同，就会发生崩溃。RFG虽然是一个不错的概念，但最终被微软内部的红队击败了，他们发现了一个通用的bypass，可以在软件中实现任何shadow stack解决方案。由于控制流劫持的任何软件实现都存在局限性，因此需要一种基于硬件的解决方案。

进入英特尔CET或控制流保护技术。CET是一种基于硬件的缓解机制，它实现了一个shadow stack来保护栈上的返回地址，以及前向边界情况，比如通过跟踪间接分支(IBT)的调用/跳转。根据Alex Ionescu和Yarden Shafir的说法，微软选择使用CFG和XFG来保护向前边界情况，而不是CET的IBT功能，它的工作原理类似于Clang的CFI实现。

CET的主要论点是它对返回地址的保护，从根本上阻止了ROP。CET具有类似于RFG的方法，其中使用了shadow stack。

当CET确定目标返回地址与其在shadow stack上与其关联的返回地址不匹配时，会产生一个错误。

[![](https://p0.ssl.qhimg.com/t01f394048aefc39d1e.png)](https://p0.ssl.qhimg.com/t01f394048aefc39d1e.png)



## 现代缓解机制4：XFG

XFG的Xtended控制流保护是Microsoft的CFG“增强”实现。根据设计，CFG只验证函数是否存在于CFG bitmap中,从技术上讲，如果一个函数指针被存在于CFG bitmap中的另一个函数覆盖，那么它将是一个有效的目标。下图显示了[nt!HalDispatchTable+0x8]，它通常指向hal!HaliQuerySystemInformation,但已经被nt!RtlGetVersion覆盖了。

[![](https://p4.ssl.qhimg.com/t0176646b2ccda006f7.png)](https://p4.ssl.qhimg.com/t0176646b2ccda006f7.png)

就在执行之前，kCFG bitmap接受RAX的值，它将是nt!RtlGetVersion而不是[nt!HalDispatchTable+0x8]，以确定函数是否有效。

[![](https://p5.ssl.qhimg.com/t01574f37627d1e05b2.png)](https://p5.ssl.qhimg.com/t01574f37627d1e05b2.png)

[![](https://p1.ssl.qhimg.com/t012e89d33c10dfb91d.png)](https://p1.ssl.qhimg.com/t012e89d33c10dfb91d.png)

按位检查发生时，仍然允许函数调用发生，即使[nt!HalDispatchTable+0x8]已经被另一个函数覆盖。

[![](https://p2.ssl.qhimg.com/t01d4023e60f8711135.png)](https://p2.ssl.qhimg.com/t01d4023e60f8711135.png)

[![](https://p3.ssl.qhimg.com/t01a787352ff2d41f78.png)](https://p3.ssl.qhimg.com/t01a787352ff2d41f78.png)

尽管CFG确实阻止了对重写函数的一些间接函数调用，但是精心设计的函数调用仍然有可能产生恶意的调用。

正如微软的David Weston所提到，XFG解决了这种安全问题。David在BlueHat shanghai2019的演讲中，他解释说XFG实现了一个受保护函数的“基于类型的hash”，该hash被设置在对一个XFG派遣函数调用之上的0x8字节。

XFG本质上是一个函数的函数原型，该函数原型由返回值和函数参数组成，并创建该原型的〜55位hash,调用派遣函数时，函数hash将设置在函数本身上面8个字节处。在控制流转移之前，此hash将用作附加检查。

[![](https://p2.ssl.qhimg.com/t01aa078c726b736f7c.png)](https://p2.ssl.qhimg.com/t01aa078c726b736f7c.png)

如果编译器生成的XFG函数hash不完整，则hash可能不是唯一的。这表示，如果构成hash的字节序列不是唯一的，例如，在调用函数过程时，位于hash下8个字节的操作码可能包含相同的字节。虽然不太可能，但这可能导致XFG声明一个被覆盖的函数是“有效的”，因为hash和函数之间的比较在分解为操作码时可能为真,导致XFG被绕过。但是，编译器团队已专门实现了代码，以试图避免这种情况的发生。同样，由于C函数的hash使用原始类型，例如void*，函数可能会被具有相同/相似原型的函数覆盖。



## 现代缓解机制5：VBS和HVCI

为了为Windows 操作系统提供额外的安全边界，Microsoft选择使用现代硬件的现有虚拟化功能。这些缓解机制包括受Hypervisor保护的代码完整性（HVCI）和基于虚拟化的安全性（VBS）。

VBS负责启用HVCI，默认情况下，在Windows 10 1903（19H1）系统上之后，在兼容的硬件上启用VBS。对于通过系统配置选择进入的厂商，如果硬件足够现代，符合微软的“Security Level 3”标准，也可以在Windows 10 2003 (20H1)系统中默认打开它。VBS的目标是通过在Hyper-V Hypervisor之上运行来隔离用户模式和内核模式代码。

下图来自Windows Internals, Part 1, 7th Edition ，概述了VBS的实现。

[![](https://p0.ssl.qhimg.com/t0194d0e7ca1d3f53d1.png)](https://p0.ssl.qhimg.com/t0194d0e7ca1d3f53d1.png)

VTLs或虚拟信任级别阻止在一个VTL中运行的进程访问另一个VTL的资源。这是因为位于普通内核中的资源实际上是由一个更“可信”的边界VTL 1管理的。

本文中提到的VBS的主要组件之一是HVCI。HVCI本质上是内核中的ACG。HVCI在内核中动态创建可执行代码。此外，HVCI防止分配RWX内核池内存，类似于ACG通过VirtualAlloc()针对RWX页面的用户模式保护。

HVCI利用SLAT（Second Layer Address Translation）来强制增强页表或EPT, EPT是附加的不可变位(在VTL 0上下文中)，在VTL 0页面上设置VTL 1权限。这表示，即使安全研究员可以在VTL 0内核模式下控制PTE控制位，VTL 1 EPT位仍然不允许在VTL 0内核模式下执行被控制的分页。

HVCI的绕过方法可能包含ACG类似的data-only攻击技术。避免执行代码，而是使用不会导致PTE操作或其他禁止操作的代码重用技术，这仍然是一个可行的选择。此外，如果攻击者/研究者可以利用hypervisor或VTL1中运行的安全内核中的漏洞，则可能会破坏VTL 1的完整性。



## 总结

这两篇文章中的漏洞分类和缓解机制绝对不是一个完整的列表。上述的这些缓解机制通常在Windows上默认启用，并且从对抗或研究的角度出发，必须至少考虑这些缓解机制。

许多对手通常选择“阻力最小的路径”，向毫无防备的目标用户发送恶意文档或恶意HTA。一般来说，这就足够完成工作了。然而，与之相对的是，在SMB、RDP或DNS等常见服务中，有没有什么比无用户交互，未经身份验证的内核远程代码执行漏洞更重要的呢？利用社会工程技术依赖于其他无法控制的因素，如安全意识强的用户收到这样的钓鱼邮件。

一个安全研究员可能会花几个星期或几个月的时间来开发一个可靠的、可移植的exploit，从而绕过现有的所有缓解措机制，例如一个浏览器漏洞，可能需要一个用户模式任意读取0-day来绕过ASLR;任意写0-day绕过DEP、CFG、ACG等缓解机制;内核任意读取0-day来绕过受限制的kASLR/页表随机化，以准备内核利用来突破浏览器沙箱；并且一个内核任意写0-day给内核利用。总共是4个0-day，投资值得吗？这些都是必须考虑的问题。
