> 原文链接: https://www.anquanke.com//post/id/169892 


# 利用Marvell Avastar Wi-Fi中的漏洞远程控制设备：从零知识入门到RCE漏洞挖掘利用（上）


                                阅读量   
                                **199609**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者embedi，文章来源：embedi.org
                                <br>原文地址：[https://embedi.org/blog/remotely-compromise-devices-by-using-bugs-in-marvell-avastar-wi-fi-from-zero-knowledge-to-zero-click-rce/](https://embedi.org/blog/remotely-compromise-devices-by-using-bugs-in-marvell-avastar-wi-fi-from-zero-knowledge-to-zero-click-rce/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t016644b138c07d1cee.jpg)](https://p4.ssl.qhimg.com/t016644b138c07d1cee.jpg)



## 研究背景

我想通过本次研究来回答一个长期以来萦绕在我脑海中的问题：到底Marvell WiFi FullMAC SoC(system-on-chip系统芯片)在多大程度上是安全的。由于具有可分析性芯片的无线设备未被完全研究透彻，它们可能包含大量未经审计的代码。应用这些WLAN卡的大量设备很有可能存在严重漏洞。这篇文章是基于原作者在ZeroNights 2018演讲中[所谈及的内容](https://2018.zeronights.ru/en/)。 所以可以跟随着PPT来学习这篇文章的内容([ppt链接](https://embedi.org/wp-content/uploads/files/(Ed)ZN2018_Denis_v2.0.pdf))。 除此之外,互联网上还有一些关于无线SoC安全主题的著名研究。例如，Google Project Zero于2017年4月发布了一系列文章描述在智能手机上利用[Broadcom Wi-Fi堆栈](https://googleprojectzero.blogspot.com/2017/04/over-air-exploiting-broadcoms-wi-fi_4.html)。 在[BlackHat 2017会议上也讨论了这个主题](https://www.blackhat.com/us-17/briefings.html#broadpwn-remotely-compromising-android-and-ios-via-a-bug-in-broadcoms-wi-fi-chipsets)。 一些智能手机基带(频率范围非常窄的信号)exploits的[write-ups](https://github.com/comsecuris/shannonRE)有助于更好理解用于反向设计无线SoC固件的技术。

Marvell(迈威科技集团有限公司，现更名美满。全球顶尖的无晶圆厂半导体公司之一，全球发展最快的半导体公司之一)



## 无线设备如何工作和启动

一般来说，Wi-Fi加密狗有两大类：FullMAC和SoftMAC。它们都需要固件镜像，这些镜像会在每次设备启动时被上传。设备制造商提供适当的固件镜像和操作系统设备驱动程序，使得在启动期间，驱动程序可以上传固件镜像，使镜像应用于Wi-Fi SoC中。下面这一张图片说明了这个过程。

[![](https://p3.ssl.qhimg.com/t0129fa7c69372cd5e6.png)](https://p3.ssl.qhimg.com/t0129fa7c69372cd5e6.png)

SoftMAC和FullMAC加密狗之间的主要区别在于其固件功能。此外，FullMAC加密狗的固件具有MLME（MAC层管理实体）功能。换句话说，它能够在SoC上处理一些Wi-Fi管理帧和事件，而不需要操作系统驱动程序的任何支持。（这里提到的MAC指的是MAC层，Media Access Control layer）

[![](https://p0.ssl.qhimg.com/t018931c8b64cd5eb48.png)](https://p0.ssl.qhimg.com/t018931c8b64cd5eb48.png)

显然，FullMAC加密狗的攻击面更大，所以我们对FullMAC更感兴趣



## Wi-Fi SoC与驱动程序之间的交互

Linux内核有两个版本的驱动程序，用于处理Marvell Wi-Fi：
<li>
`mwifiex` 驱动程序（源代码可以在官方的linux repo中找到）</li>
<li>
`mlan`和`mlinux`驱动程序（可以在官方的steamlink-sdk repo中找到）<br>
这两类驱动程序都有一些调试功能，允许我们读/写SoC内存。驱动程序使用内部格式将信息发送到Wi-Fi SoC或从SoC接收事件或响应。我们使用Marvell开源驱动程序mwifiex的源代码来研究这种内部格式。Wi-Fi SoC有几种定义类型的数据。</li>
1. COMMAND
1. EVENT
1. DATA
<li>SINGLE PORT AGGREGATED DATA<br>
Wi-Fi SoC和设备驱动程序之间的交互模式可以在下图中看到</li>
[![](https://p5.ssl.qhimg.com/t013692d4777aa8efbc.png)](https://p5.ssl.qhimg.com/t013692d4777aa8efbc.png)

我们更喜欢去考虑比如固件的API这样的命令。这些命令我们将其分为几组：
1. SoC存储器的 READ/WRITE 命令
1. 固件扩展版本信息（如SteamLink中的`w8897o-B0, RF8XXX, FP68, 15.68.7.p206`）
与Wi-Fi相关的东西（如Association，scanning……,这里的association指设备之间的关联和记录，比如wifi信息在手机上保存等等）<br>
其中一些可以使用驱动程序实现的IOCTL(输入输出控制)或特殊的debugfs文件从用户态进行访问。驱动程序最有用的功能之一是它拥有固件内存转储机制。这有助于调试我们的动态检测或利用。超时机制是在操作系统驱动程序中实现的。因此，当命令响应超时时，驱动程序将尝试转储Wi-Fi SoC内存并将其存储在主机文件系统中。内存转储在mwifiex和mlan+mlinx驱动程序中具有不同的格式。我研究了mwifiexPCI驱动程序，发现它以类似于固件镜像的格式存储完整的Wi-Fi SoC内存转储的数据。SDIO-Wifi版本的mlan+mlinx驱动程序仅以原始二进制格式存储ITCM，DTCM和SQRAM区域。



## 固件分析

如前所述，Marvell Avastar Wi-Fi芯片组系列使用固件文件，这些固件承载了大部分设备功能。<br>
除此之外还有ROM，ROM包含启动代码和在将主固件加载到芯片RAM之前与主机交互的功能。<br>
官方linux-firmware git repo提供了几个版本的固件。因此，我们首先研究驱动程序初始化Wi-Fi SoC所使用的固件镜像

### <a class="reference-link" name="%E9%9D%99%E6%80%81%E5%9B%BA%E4%BB%B6%E6%96%87%E4%BB%B6%E5%88%86%E6%9E%90"></a>静态固件文件分析

为了获取有关固件RAM镜像结构的一些基本逻辑，我们可以查看Marvell Wi-Fi驱动程序代码，该代码将固件加载到Wi-Fi SoC（[https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git/tree/drivers/net/wireless/marvell/mwifiex/fw.h）。](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git/tree/drivers/net/wireless/marvell/mwifiex/fw.h%EF%BC%89%E3%80%82)

```
...

struct mwifiex_fw_header `{`
    __le32 dnld_cmd;
    __le32 base_addr;
    __le32 data_length;
    __le32 crc;
`}` __packed;

struct mwifiex_fw_data `{`
    struct mwifiex_fw_header header;
    __le32 seq_num;
    u8 data[1];
`}` __packed;

...
```

注意到固件文件包含一些带有头部和检验和的内存块。内存将会被加载到内存块头部中的Soc地址。根据这些知识，我们使用IDA Pro对Marvell Avastar的固件文件进行进一步的研究。

[![](https://p4.ssl.qhimg.com/t013692d4777aa8efbc.png)](https://p4.ssl.qhimg.com/t013692d4777aa8efbc.png)

我们可以发现88W8897是具有8个MPU区域的ARM946微控制器。所有内存都是RWX。固件文件还包含对ROM功能的引用。因此，为了进一步研究，我们需要一个ROM转储文件。下图是88W8897 Wi-Fi芯片的存储器映射关系。未知的存储器区域似乎是存储器映射关系中的寄存器区域。

[![](https://p2.ssl.qhimg.com/t01c5bb55dbebe60d1c.png)](https://p2.ssl.qhimg.com/t01c5bb55dbebe60d1c.png)

### <a class="reference-link" name="%E5%8A%A8%E6%80%81%E5%9B%BA%E4%BB%B6%E5%88%86%E6%9E%90&amp;ThreadX%E8%BF%90%E8%A1%8C%E7%BB%93%E6%9E%84%E6%81%A2%E5%A4%8D"></a>动态固件分析&amp;ThreadX运行结构恢复

我们可以利用READ和WRITE命令创建一个可以转储内存和仪器固件的简单工具。通过这个工具，我们可以获得一些运行时信息。值得注意的是，固件看起来像一个很大的不透明二进制文件。它只包含几个字符串，没有任何提示关于这些设备如何运行以及我们应该在何处或如何开始寻找错误。但是，在研究了ROM转储之后(通过我们制造的工具获得)，我们可以发现这是一个基于ThreadX的固件。<br>
ThreadX是一种广泛用于智能设备的专有RTOS。可以根据license来获取此RTOS的源代码。ThreadX基本上只是一个运行时的环境。它包含用于管理线程之间的动态内存，线程和通信的函数。它是最受欢迎的RTOS之一，部署超过60亿。通过ID字段，我们可以在内存中搜索ThreadX运行时的结构。我们发现如果搜索出的结构有效，则ID字段应该是一个特定值。比如在下面这个线程结构体中

```
typedef  struct TX_THREAD_STRUCT
`{`
    /* The first section of the control block contains critical
       information that is referenced by the port-specific 
       assembly language code.  Any changes in this section could
       necessitate changes in the assembly language.  */
    ULONG       tx_thread_id;           /* Control block ID         */

    ...
`}`
```

第一个4字节字段`tx_thread_id`必须包含值`0x54485244`或`THRD`。这提供给我们更多的信息，因为其中一些ThreadX对象包含名称，这使得我们可以通过名称来猜测它们的用途。我们通过编写一个IDA脚本将ThreadX运行时的结构重构。该脚本还可用于研究另一个基于ThreadX的设备内存转储文件。ThreadX结构重建的一些摘要如下表所示（表中的地址对于版本号位`w8897o-B0, RF8XXX, FP68, 15.68.7.p206`的steamlink固件有效）：

[![](https://p5.ssl.qhimg.com/t0137459962eaafc976.png)](https://p5.ssl.qhimg.com/t0137459962eaafc976.png)

### <a class="reference-link" name="%E5%8A%A8%E6%80%81%E5%9B%BA%E4%BB%B6%E5%88%86%E6%9E%90&amp;%E5%8A%A8%E6%80%81%E5%9B%BA%E4%BB%B6%E6%A3%80%E6%B5%8B"></a>动态固件分析&amp;动态固件检测

在刚开始寻找固件中的漏洞时，我们只有以下几条已知信息：
1. 源代码不可用
1. 处理或解析帧的代码未知
1. Wi-Fi SoC包含少量内存，足以满足其目的，我们无法在Wi-Fi SoC内使用我们的脚本进行模糊测试或变量覆盖测试。
由于我们找不到对于第1点和第3点的任何深入研究的方法，因此我们只能通过研究运行固件来查找负责处理Wi-Fi帧的函数。使用`READ/WRITE`命令可以在Wi-Fi SoC上进行以下几种类型的热分析。
1. 我们可以hook一个函数（使用一些拼接技术）。
1. 我们可以替换一些类似调试或日志的例程的指针。
1. 我们可以跟踪块池分配/释放。
1. 我们甚至可以使用static thumb函数调用（例如具有函数级粒度的DBI）来检测整个代码区域。
在我们的Wi-Fi SoC研究工具中，实现前三点非常简单。但实现最后一个有一定难度。基本上，我们的工具使用capstone反汇编引擎来查找thumb BL指令（该指令在函数调用中使用），并将其替换为对instrumentation stub的调用[原文为instrumentation sub,应该是写错了]。该 instrumentation stub负责调用我们的自定义DBI工具(含有正确参数的原始固件函数)，并返回调用引用。该算法非常简单：

[![](https://p3.ssl.qhimg.com/t0101e634e24f0c91fb.png)](https://p3.ssl.qhimg.com/t0101e634e24f0c91fb.png)

可以从下图中获得有关instrumentation stub 工作流程的更多详细信息：

[![](https://p4.ssl.qhimg.com/t016922c7bd632b9d89.png)](https://p4.ssl.qhimg.com/t016922c7bd632b9d89.png)

因此，为了在Wi-Fi SoC上应用我们的脚本，我们需要：
1. 从Wi-Fi SoC读取待检测的存储区域。
1. 用capstone对它进行反编译。
1. 创建patch程序代码将用于patch内存中的固件并调用检测用户定义例程的结构体。
1. 将这些结构体，特殊的patch程序代码， stubs(上文提到的instrumentation stub)和用户定义的例程复制到Wi-Fi SoC。
1. 通过hook扩展版本例程并使用常规固件API调用它来执行patch程序。驱动程序很少调用此固件功能。这将确保我们可以安全地禁用中断处理和过程检测。
1. 在我们的检测工具收集必要的运行时信息后，通过固件/驱动程序从Wi-Fi SoC存储器中复制运行结果
值得注意的是，该类型instrumentation stub存在一些微架构问题。因为我们用覆盖了Wi-Fi SoC上的新的指令BL来调用instrumentation stub。因此，在I/D-cache输入输出缓存器不一致的情况下，我们可能会丢失一些结果（某些调用可能无法执行，因为来自I-cache输入缓存器的旧原始指令仍然有效）。它看起来像是为了初始化后的写入而执行的固件锁定ARM CP15协处理器寄存器的操作，因此在Wi-Fi SoC上刷新I-cache并不是一件轻而易举的事。<br>
另一种可以研究Wi-Fi SoC的技术是静态固件instrumentation。但是每次应用新的分析payload时，它需要重建Wi-Fi固件，还需要重新启动设备来启动已检测的固件。这里有几种类型的DBI工具值得一试：
1. 搜索功能参数（如BSSID或MAC）中的签名的工具。
1. 收集有关调用堆栈信息的工具（此信息可以帮助RE或固件模糊测试）。
1. 监视ThreadX块池状态的工具。
所有这些都为我们提供了代码处理框架的信息，因为我们可以使用不同的客户端二进制文件自定义我们的DBI工具 在没有源代码和任何RE提示（如记录字符串或导出的函数名称）的情况下，这是我们向寻找漏洞迈出的一大步。在将这种类型的动态分析应用于运行固件之后，我们可以了解哪些函数用于解析输入帧和参数，其中输入数据被传递给这些函数。之后，可以应用多种类型的二进制分析和错误搜寻技术。



## 小结

本文介绍了关于无线设备如何工作和启动，Wi-Fi SoC与驱动程序之间的交互以及Marvell Avastar Wi-Fi固件文件的静态动态分析的内容，下一篇文章将会带来关于如何进行fuzz找到漏洞和漏洞利用，攻击面扩大以及其中的一些思考的内容
