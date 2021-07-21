> 原文链接: https://www.anquanke.com//post/id/170078 


# 利用Marvell Avastar Wi-Fi中的漏洞远程控制设备：从零知识入门到RCE漏洞挖掘利用（下）


                                阅读量   
                                **189709**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者embedi，文章来源：embedi.org
                                <br>原文地址：[https://embedi.org/blog/remotely-compromise-devices-by-using-bugs-in-marvell-avastar-wi-fi-from-zero-knowledge-to-zero-click-rce/](https://embedi.org/blog/remotely-compromise-devices-by-using-bugs-in-marvell-avastar-wi-fi-from-zero-knowledge-to-zero-click-rce/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t016644b138c07d1cee.jpg)](https://p4.ssl.qhimg.com/t016644b138c07d1cee.jpg)



## 前文回顾

在上一篇的文章中介绍了关于无线设备如何工作和启动，Wi-Fi SoC与驱动程序之间的交互以及Marvell Avastar Wi-Fi固件文件的静态动态分析的内容，本文将介绍漏洞的挖掘和利用方法



## 寻找漏洞

尽管我们在固件内存转储和Wi-Fi SoC上使用了各种类型的二进制分析方法对其进行了剖析（静态和动态），但是我们依然难以直接通过上面的分析来找到漏洞，我们还需要进行一些测试来发现漏洞

### <a class="reference-link" name="%E6%A8%A1%E7%B3%8A%E6%B5%8B%E8%AF%95"></a>模糊测试

fuzz是我们常用的一种漏洞挖掘手法，在这里也不例外。<br>
我们进行两方面的fuzz尝试
1. 无线环境下的随机fuzz
1. 对仿真环境中的固件进行fuzz
第一种类型的模糊测试可以直接对Wi-Fi SoC进行fuzz。这种类型的测试的缺点在于：由于边缘覆盖不足使得输入帧变异算法无法达到极致。[注:边缘覆盖不足指测试过程中对于控制流图中的每条边的测试不足，没有全覆盖到]通常，我们可以通过使用JTAG(Joint Test Action Group)，ARM ETM(Embedded Trace Macrocell)或Intel Process Tracing技术等CPU的功能来实现收集边缘覆盖的目标。但是，这需要芯片本身的硬件和对于硬件的黑客技能来支持我们在工业级设备中使用硬件调试功能。这是一项非常重要的工程任务。

第二种类型的模糊测试依赖于固件仿真，因此在一些反馈驱动算法的帮助下收集突变输入的边缘覆盖较为容易。这对于无线设备来说是一种较为智能的fuzz方法。但是会让你感到惊讶的事实是，应用这种方法的fuzz工具已经被实现了。请看这里：afl-unicorn([https://github.com/Battelle/afl-unicorn](https://github.com/Battelle/afl-unicorn)) ,这是原始的AFL fuzzer和Unicorn(独角兽公司)的CPU仿真器集成的，最初由Nathan Voss所创建的。你应该看一下它的源代码来理解它如何进行fuzz。要使用afl-unicorn工具来fuzz Wi-Fi固件，你需要识别解析例程（例如，使用我们的Wi -Fi SoC DBI工具）并编写一个将突变输入（Wi-Fi帧）输入到这些例程中的fuzzer（fuzz器）。基本上，你的fuzzer应该可以做到：
1. 使用Unicorn的修改版本映射必要的内存区域。
1. 设置寄存器上下文。
1. 读取突变的输入文件并将其映射到仿真器的内存​​中。
1. 开始执行代码。
1. 通过发送适当的信号正确模拟固件的崩溃。
这是一种简单有效的技术，但仍存在一些缺点。最应该引起注意的是，该技术效果的好坏依赖于在创建Wi-Fi SoC内存转储时捕获的全局状态。该状态可以包含一些已保存的全局变量，这些变量可能会阻止fuzzer访问某些执行路径。除此之外，该技术没有动态内存访问清理，很难找到和删除校验和验证代码，无法实现RTOS任务之间的通信。因此这也会导致无法访问某些执行路径。但是使用这种fuzz技术可以获得一些结果：

[![](https://p3.ssl.qhimg.com/t01a0b39c374b430dd3.jpg)](https://p3.ssl.qhimg.com/t01a0b39c374b430dd3.jpg)

通过这种技术，我在固件的某些部分分析出大约4个总内存损坏问题。尽管如此，因为AFL的输入可能会因为某种方式被改变而无法传递给fuzzed function模糊函数（比如，在调用模糊函数之前进行了对输入的过滤整形等），因此很难研究可能由此引起的潜在影响。这些问题。我还尝试在不同版本的固件和不同版本的无线SoC上复现这些错误，这里面看起来有很多漏洞



## 最有意思的漏洞

其中一个漏洞是ThreadX块池溢出的特例。在扫描可用网络期间，无需用户交互即可触发此漏洞。无论设备是否连接到某个Wi-Fi网络，此过程每5分钟启动一次。这就是为什么我认为这个漏洞最有意思，并且该漏洞可在任何无线连接状态下（即无论是否连上wifi或没有）都可以不需要任何交互来控制设备（也就是说你只要点一下启动设备按钮就好了）。例如，只需启动三星Chromebook即可完成RCE。总结一下这个漏洞：
1. 它不需要任何用户交互。
1. 在GNU/Linux操作系统下，它可以每5分钟触发一次。
1. 它不需要知道Wi-Fi网络名称或密码/密钥。
<li>即使设备未连接到任何Wi-Fi网络，只需打开电源即可触发。<br>
在这里，我将描述如何在Wi-Fi SoC上实现这个RCE攻击。</li>
### <a class="reference-link" name="%E5%9F%BA%E6%9C%ACThreadX%E5%9D%97%E6%B1%A0%E6%BA%A2%E5%87%BA%E5%88%A9%E7%94%A8"></a>基本ThreadX块池溢出利用

ThreadX块池只是一个连续的内存区域，分成较小的块。每个块池都由运行时结构表示，可以在上面描述的IDA脚本的帮助下在内存转储中找到它。在每个块的开头，有一个指向下一个空闲块的指针。在最后一个空闲块之前，NULL指针驻留。第一个空闲指针存储在ThreadX块池管理结构中。指向此结构的指针用于块池分配和销毁功能。

[![](https://p5.ssl.qhimg.com/t01e86fdac7132b967b.png)](https://p5.ssl.qhimg.com/t01e86fdac7132b967b.png)

TX-BP 很容易注意到，攻击者可以覆盖指向下一个空闲块和控制位置的指针，下一个块将被分配。通过控制下一个块分配的位置，攻击者可以将此块放置到某些关键运行时结构或指针所在的位置，从而实现攻击者的代码执行。

[![](https://p0.ssl.qhimg.com/t01f7e0289f09ef19bb.png)](https://p0.ssl.qhimg.com/t01f7e0289f09ef19bb.png)

### <a class="reference-link" name="Marvell%20Avastar%20ThreadX%E5%9D%97%E6%B1%A0%E6%BA%A2%E5%87%BA%E5%88%A9%E7%94%A8"></a>Marvell Avastar ThreadX块池溢出利用

Marvell Avastar固件中的大多数内存管理例程都依赖于特殊的包装函数。此函数在每个ThreadX块的开头使用特殊元数据头。通过对此函数进行逆向工程，可以发现这些头可以包含特殊指针，这些指针在释放块之前被调用。因此，对于Marvell Avastar的固件，攻击者可以轻松地在无线SoC上执行任意代码。下图是允许执行任意指针的块解除分配器的伪代码：

[![](https://p4.ssl.qhimg.com/t017971fbf5352818f8.png)](https://p4.ssl.qhimg.com/t017971fbf5352818f8.png)

为了执行代码，攻击者只需要覆盖下一个块的更多额外空间

[![](https://p1.ssl.qhimg.com/t01bc6d48ef09a2e8c7.png)](https://p1.ssl.qhimg.com/t01bc6d48ef09a2e8c7.png)

### <a class="reference-link" name="%E7%BB%BC%E5%90%88%E4%B8%A4%E7%A7%8D%E5%88%A9%E7%94%A8%E6%96%B9%E6%B3%95"></a>综合两种利用方法

因此，我们有两种技术可以利用ThreadX块池溢出。一个是通用的，可以应用于任何基于ThreadX的固件（如果它有块池溢出错误，下一个块是空闲的）。第二种技术特定于Marvell Wi-Fi固件的实现，并且如果下一个块忙，则可以工作。换句话说，通过将它们组合在一起，我们可以实现可靠的溢出利用。（无论下一个块是free还是busy都有方法可以利用）



## Valve Steamlink的示例

Valve Steamlink是一款简单的桌面流媒体设备，可让你在计算机上玩PC游戏，并将游戏桌面流式传输到电视盒，使得你可以在电视上玩PC游戏。该设备的固件基于一些类似Debinan的GNU/Linux操作系统，Linux内核版本为”3.8.13-mrvl”，可在arm7l 应用处理器上运行。它有Marvell 88W8897无线芯片组，它与SDIO总线和专有的mlan.ko和mlinux.ko设备驱动程序相连。有趣的是：这个设备在ZeroNights 2018前一天就停止了生产。也许你会发现，大多数使用Marvell Wi-Fi的设备都是游戏设备，比如PS 4（可能是因为他们都是高性能的802.11ac和蓝牙的结合体）。但是由于DRM（数字版权管理）保护，我们很难对它们进行研究分析。所以，我选择了SteamLink，因为它没有DRM，并且可以轻松启动他们的工具和内核模块来研究无线SoC。Microsoft Surface和三星Chromebook也使用Marvell Wi-Fi。

### <a class="reference-link" name="%E6%8F%90%E6%9D%83"></a>提权

要在SteamLink的应用程序处理器上执行代码，我们需要进行提权，因为SteamLink所使用的SDIO总线没有设计DMA（Direct Memory Access,直接内存存取）。如果是使用PCIe这样的总线则升级技术比较简单，因为PCIe允许DMA。在这种情况下，我们进行提权类似于利用RCE。他们唯一的区别是攻击者通过SDIO总线从受我们控制的Wi-Fi SoC发送数据，而不是通过网络发送数据。您可以将典型的设备驱动程序视为设备与应用程序或操作系统之间的桥梁。因此，设备驱动程序应该从设备接收数据，解析它，将其发送到应用程序（操作系统），反之亦然。它包含着解析从设备接收的数据的代码。Marvell Wi-Fi驱动程序在特定情况下，这部分代码应该处理由信息元素（IE）组成的许多类型的消息。事实上，提权非常广泛。

[![](https://p4.ssl.qhimg.com/t01fbee0aa449cc2986.png)](https://p4.ssl.qhimg.com/t01fbee0aa449cc2986.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8AP%E8%AE%BE%E5%A4%87%E9%A9%B1%E5%8A%A8%E7%A8%8B%E5%BA%8F%E6%BC%8F%E6%B4%9E"></a>利用AP设备驱动程序漏洞

这个漏洞非常易于利用，它基于堆栈的缓冲区溢出。Linux内核”3.8.13-mrvl”中也没有二进制的防御措施。然而，因为I/D-cache不连贯的and/or回写缓冲区的deffer commit，我们需要一些准备时间。此外，由于函数epilogues，它无法控制堆栈，它会从堆栈本身弹出堆栈指针：

```
LDMFD           SP, `{`R4-R11,SP,PC`}`
```

要成功提权，应执行以下操作：
1. 调用v7_flush_kern_cache_louislinux内核函数。
1. 执行shellcode。
由于堆栈指针丢失，我们无法将代码放在堆栈上。相反，我们可能依赖于寄存器R4-R11，这些寄存器也会在执行将在恢复的PC位置继续执行之前从堆栈中恢复。首先，我们需要在一个基本块中找到一个包含两个不同寄存器调用的特殊代码块。这个代码块需要表示两个主要操作的调用：刷新缓存和调用shellcode。下面是一个例子

```
BLX             R3
MOV             R1, R4
MOV             R2, R5
SUBS            R3, R0, #0
MOV             R0, R10
BNE             loc_C00E7678
BLX             R9
```

虽然它包含一个条件分支，但它永远不会被占用，因为它v7_flush_kern_cache_louis总是返回0。它也不会破坏R9，因此可以由攻击者控制。但是，第一次调用是通过R3寄存器进行的，寄存器不会从堆栈中恢复。在这种情况下，应该R3在调用主要值之前搜索我们先前放入的代码块来放置我们的控制值。例如，像这样：

```
MOV             R3, R8
BLX             R7
```

最终的代码块应该计算shellcode的位置并将执行转移给它。在这种情况下，R0，R1，R2，R3和R12可被使用，因为它们可能含有一些堆栈指针。而对于Marvell的驱动程序，R12确实包含堆栈中的地址。因此，应该找到一个将使用受控寄存器并R12计算实际shellcode位置和传输执行的代码块，如下所示：

```
LDR             R6, [R12,R4,LSL#4]
MOV             R7, R0
ADD             R4, R12, R4,LSL#4
MOV             R8, R2
BLX             R6
```

还应注意，攻击者可以通过使用Thumb指令（thumb instruction,比如通常使用32位的指令，则16位的指令被称为Thumb指令）编码显着增加可用代码块的数量。实际上，R12在溢出期间有几种指针位置的情况。我认为这取决于当前的扫描状态。我们可以研究的是如何正确地将事件缓冲区从Wi-Fi SoC发送到AP，因此堆栈布局将始终相同。总体来说利用成功率约为50-60％。



## 漏洞利用条件

在这项研究中，我在监控模式下使用ALFA网络无线适配器，这是基于Realtek 8187无线芯片组。该漏洞可以使用python Scapy框架实现。但由于某种原因，Ubuntu GNU/Linux发行版不能快速地注入Wi-Fi帧，因此最好使用Kali。你可以在下面的视频中看到全链漏洞利用演示。演示的有效负载是定期在内核日志中打印消息。

[https://www.youtube.com/watch?v=syWIn62M72Y&amp;feature=youtu.be](https://www.youtube.com/watch?v=syWIn62M72Y&amp;feature=youtu.be)



## 总结

从本次的分析中可以学到的是：

无线设备暴露出了巨大的攻击面，我们可以更多的关注无线设备上的漏洞
