> 原文链接: https://www.anquanke.com//post/id/160249 


# 如何在启用虚拟安全模式（VSM）的系统上进行内存采集


                                阅读量   
                                **118233**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者rekall-forensic，文章来源：rekall-forensic.com
                                <br>原文地址：[http://blog.rekall-forensic.com/2018/09/virtual-secure-mode-and-memory.html](http://blog.rekall-forensic.com/2018/09/virtual-secure-mode-and-memory.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/dm/1024_672_/t01a6597d66ef07b6bd.jpg)](https://p2.ssl.qhimg.com/dm/1024_672_/t01a6597d66ef07b6bd.jpg)



## 概述

本文主要是我最近对于开源内存获取实用程序WinPmem的漏洞发现与分析成果。读者可以在Velocidex/c-aff4发布页面（ [https://github.com/Velocidex/c-aff4](https://github.com/Velocidex/c-aff4) ）上找到最新版本的WinPmem，需要注意的是近期该软件已经从Rekall框架迁移到了AFF4框架。

这个故事一开始起源于有人询问我如何在受虚拟安全模式（VSM）保护的计算机上实现内存采集。现在，想要进行内存采集，有很多可以选择的工具，但我们有一个最爱，那就是WinPmem。WinPmem是AFAIK唯一的开源内存采集工具。该工具在几年前发布，并且直到目前没有更新过。但是，我们已经发现，这一工具会在启用了虚拟安全模式的Windows系统上崩溃。

2017年，Jason Hale在DFRWS上发表了精彩的演讲（ [https://www.dfrws.org/conferences/dfrws-usa-2017/sessions/virtualization-based-security-forensics-perspective](https://www.dfrws.org/conferences/dfrws-usa-2017/sessions/virtualization-based-security-forensics-perspective) ），在演讲中他提出了大量的内存采集工具，并发现大多数工具在启用虚拟安全模式的系统上都会出现蓝屏（ [https://df-stream.com/2017/08/memory-acquisition-and-virtual-secure/](https://df-stream.com/2017/08/memory-acquisition-and-virtual-secure/) ）。随后，其中的一些工具进行了修复，但我没有找到任何关于它们具体修复方式的信息。目前，WinPmem是仍然还在崩溃的工具之一。



## 打印物理内存范围

在我听到这些情况之后，我立刻吹了吹我Windows主机上面的灰尘，并启用了虚拟安全模式。然后，我尝试运行已发布版本的WinPmem（V3.0.rc3）。果不其然，我立刻就遇到了BSOD，真是糟糕。

起初，我认为物理内存范围检测是问题所在。也许在虚拟安全模式下，我们用WinPmem检测到的内存范围是错误的，这样一来使得我们读入了无效的物理内存范围。大多数工具会使用未公开的内核函数MmGetPhysicalMemoryRanges()来获取物理内存范围，但它只能在内核模式下访问。

为了确认，我在WinPmem中只需要使用-L标志，打印出从该函数获得的范围。这个标志表示WinPmem只会加载驱动程序、报告内存范围并退出，不会实际读取任何内存，所以我推测应该也不会崩溃。

[![](https://lh5.googleusercontent.com/lJJc2Eksf39SH3KADzpHxnGq03I5DTE3JDmVhT6NfN09rXMMWVfG7IKDOSJWAf7rq1wkhuUPTO50X1hk9L51X4xXl7qLxWdBtaR2B60thmrWYMFw9O3NcNh0Jwi2CzAM-YcOhklr)](https://lh5.googleusercontent.com/lJJc2Eksf39SH3KADzpHxnGq03I5DTE3JDmVhT6NfN09rXMMWVfG7IKDOSJWAf7rq1wkhuUPTO50X1hk9L51X4xXl7qLxWdBtaR2B60thmrWYMFw9O3NcNh0Jwi2CzAM-YcOhklr)

这些内存范围实际上看起来有点奇怪，它们与没有启用虚拟安全模式情况下同一台主机的内存情况看起来有明显不同。

现在，我尝试从另外一个途径来检查物理内存范围。我编写了一个Velociraptor工具来收集注册表中硬件管理器所显示的物理内存范围。由于无法从用户空间访问MmGetPhysicalMemoryRanges()（ [http://www.reactos.org/pipermail/ros-diffs/2009-June/031391.html](http://www.reactos.org/pipermail/ros-diffs/2009-June/031391.html) ），因此系统会在每次启动时将内存范围写入注册表中。在这里，我们其实还可以使用Alex Ionescu的meminfo（ [http://www.alex-ionescu.com/?p=51](http://www.alex-ionescu.com/?p=51) ）从内存空间中转储（Dump）出内存范围。

[![](https://lh4.googleusercontent.com/o9FMKSQ2vKURVxJI7g7LG_OfTAiWnaAGw2ReyBI-z1716PAG1PkX9EnD0ukr86YCEpzp2rKt-Oz_m5crXnU2OcxhZtK-JokalU2iofPm4VaDD1XxFctKP2LP_R13qCMr4CUYbE_n)](https://lh4.googleusercontent.com/o9FMKSQ2vKURVxJI7g7LG_OfTAiWnaAGw2ReyBI-z1716PAG1PkX9EnD0ukr86YCEpzp2rKt-Oz_m5crXnU2OcxhZtK-JokalU2iofPm4VaDD1XxFctKP2LP_R13qCMr4CUYbE_n)

结果表明，其范围似乎与驱动程序报告的内容一致。

最后，我试图用DumpIt（ [https://www.comae.com/](https://www.comae.com/) ）取得内存镜像，这是一个优秀的内存镜像取证工具，它运行时也没有发生崩溃：

[![](https://lh6.googleusercontent.com/ePY7b9qtrxYetIgehdJZw6tWjxikOkHHvozYpRSJsdQtx9LJ3c0omfchk3857kV-UBspGL_HrWTf1Jg8Wis2S_1QHZfjmkQW2CgGGxlEkZDIZyg_KAL6CgX__vG9aB7rsOOIgqRY)](https://lh6.googleusercontent.com/ePY7b9qtrxYetIgehdJZw6tWjxikOkHHvozYpRSJsdQtx9LJ3c0omfchk3857kV-UBspGL_HrWTf1Jg8Wis2S_1QHZfjmkQW2CgGGxlEkZDIZyg_KAL6CgX__vG9aB7rsOOIgqRY)

DumpIt程序产生了一个Windows崩溃转储镜像格式。令我们激动的是，DumpIt显示的CR3值与WinPmem上显示的一致。尽管DumpIt没有明确显示出其使用的物理内存范围，但由于它使用了crashdump格式文件，我们可以借助Rekall看到编码到崩溃转储（Crashdump）中的范围：

[![](https://lh4.googleusercontent.com/whN-3hi9b8RktKjVQPJfBQyxKBaDA5McHmuxSnCGPZem3inDqPFJjfyj5rV2nJA_ZOzat7s74J_cXGkgaMghWOesAkcqjw0_z6uZNQR9xe5RGWAYEzC0rY7GqrHm3OS5VbgByYYE)](https://lh4.googleusercontent.com/whN-3hi9b8RktKjVQPJfBQyxKBaDA5McHmuxSnCGPZem3inDqPFJjfyj5rV2nJA_ZOzat7s74J_cXGkgaMghWOesAkcqjw0_z6uZNQR9xe5RGWAYEzC0rY7GqrHm3OS5VbgByYYE)

因此，在这里我们能够确认，这一问题并不是由于WinPmem在有效物理内存范围之外进行读取而产生的，DumpIt也对相同的范围进行了读取，但它并不会崩溃。

显然，要修复任何错误，都会涉及到更新驱动程序组件，因为所有镜像取证工具的用户控件组件都是读取相同的范围。我进行了多年的内核开发，而我的代码签名证书已经过期好几年了。由于这些代码签名证书需要EV，因此它们非常贵。我比较担心不知情的用户会尝试在支持虚拟安全模式的系统上使用WinPmem并导致蓝屏，这种系统正在变得越来越普遍，由此就带来了非常大的风险。<br>
我更新了DFIR列表，并公布了我发现的需要修复内核驱动程序的问题，由于我的代码签名证书过期，我将无法对其进行修复。我觉得目前来说，唯一负责任的做法就是给予用户充分的提示，并建议用户考虑使用其他同类工具。

接下来发生的事情令我感到惊讶，我收到了DFIR社区的积极回应，收到了许多电子邮件，大家慷慨地为我赞助了代码签名证书，并且对WinPmem出现的问题表示遗憾。最后，来自Binalyze的Emre Tinaztepe提出将会签署新的驱动，并分享到社区。能看到开源社区的大家如此团结，这感觉真是不错。



## 问题修复

至此，我开始研究WinPmem崩溃的原因。要进行内核开发，我们需要使用Drive Development Kit（DDK）安装Visual Studio。这个过程需要很长的时间，并且需要下载很多个GB的软件。<br>
经过一段时间后，我成功部署了开发环境，检查了WinPmem代码，并尝试使用新构建的驱动程序对崩溃进行复现。但令我惊讶的是，崩溃这次没有出现，并且工具完全正常运行。这一点令我非常困惑。

事实证明，这一问题在2016年已经得到了修复，但我完全忘记了这件事。然后，我寻找了我的邮件，并发现在2016年10月与Jason Hale的对话。我的代码签名证书是在2016年8月到期的，因此虽然修复程序已经开发完成，但我没能将其重新编译到驱动程序中并发布。

我们仔细研究问题修复的过程，关键在于这段代码：

这段代码尝试读取映射页，但如果发生了段错误（Segfault），则会捕获错误，并用零填充页，不会导致BSOD。当时，我认为这种修复方式有点逃避问题，因为我们完全不知道为什么会发生崩溃。但是，如果真的发生了崩溃，那我们还是更希望零填充（Zero Pad），而不是BSOD。但是，为什么从物理RAM中读取页会产生内存错误呢？

要理解这一点，我们首先需要了解什么是基于虚拟化的安全性。Microsoft Windows是通过虚拟安全模式（VSM）实现的：

VSM是利用CPU片上的虚拟化扩展来对关键进程和内存实现隔离，从而防止恶意篡改。这些保护是由硬件辅助的，管理程序会请求硬件以不同的方式处理这些内存页。

在实际中，这就意味着，属于敏感进程的某些页实际上在正常的操作系统上是不可读的。如果尝试读取这些页，就会产生一个段错误。当然，在正常的执行过程中，VSM容器永远不会访问这些物理页，因为这些物理页不属于它。但是，虚拟机管理程序会额外进行基于硬件的检查，以确保无法访问这些页。上面的修复方法之所以有效，是因为捕获到了段错误，并使WinPmem移动到下一页，从而变了BSOD。

所以，我修改了WinPmem，并报告其无法读取的所有PFN。现在，WinPmem会在查询结束后，打印出所有不可读页的列表：

[![](https://lh6.googleusercontent.com/nSWRXdbyJgwsqUmgt2X_2pxdASqcKd3Ignp5Fm4L7aGtQPHRu4tNNDVaddMpF2S0-3suRNBOacJ5E5hPTXNv-iNACkbGtG3TtCZGE4Sn5fQ1692QtQmIThTm24sRKE5eUq3qsJx8)](https://lh6.googleusercontent.com/nSWRXdbyJgwsqUmgt2X_2pxdASqcKd3Ignp5Fm4L7aGtQPHRu4tNNDVaddMpF2S0-3suRNBOacJ5E5hPTXNv-iNACkbGtG3TtCZGE4Sn5fQ1692QtQmIThTm24sRKE5eUq3qsJx8)

大家可以看到，受管理程序保护的页数量其实不多，总计约25MB大小。这些页不包含在特定区域中，它们被喷射在所有物理内存周围。这实际上非常有道理，但我们还需要认真确认一下。

于是，我们运行了内核调试器（Windbg），并看看它是否可以读取WinPmem无法读取的物理页。实际上，Windbg有!db命令来读取物理内存。

[![](https://lh4.googleusercontent.com/eXUxTWWHXINxwXAltMK2ywoMRcIljblm9zPLbfVoYAqiSnUzAoWzvPcV2huucqyrJmQH-v4hB0OGjULIQhsWU0I5FecsCt7orPD77T0BP6RxwAnUYwvZuQctwtFvYwhuB7cD7s03)](https://lh4.googleusercontent.com/eXUxTWWHXINxwXAltMK2ywoMRcIljblm9zPLbfVoYAqiSnUzAoWzvPcV2huucqyrJmQH-v4hB0OGjULIQhsWU0I5FecsCt7orPD77T0BP6RxwAnUYwvZuQctwtFvYwhuB7cD7s03)

将这里的输出与之前的屏幕截图进行比较，我们可以发现，WinPmem无法读取PFN 0x2C7和0x2C9，但它可以读取0x2C8。Windbg完全相同，它也无法读取那些可能受到VSM保护的页。



## 尝试读取不可读的页

实际上，这是一个有趣的开发过程。磁盘映像很长时间以来都有一个扇区能够读取错误，并且磁盘映像格式已经对这种可能性进行了证明。当某个扇区不可读时，我们可以对该扇区进行零填充，大多数磁盘映像取证工具都有方法来指示扇区的不可读状态。但针对内存来说，这样的情况在内存镜像中从未发生过，因为我们即使有正确的权限，也无法从RAM中读取。

WinPmem默认使用AFF4格式，而AFF4专门设计了“诊断镜像” （Forensic Imaging）功能。目前，AFF4库使用“UNREADABLE”字符串来填充不可读的页，以指示该页已受到保护。

请注意，如果镜像格式不支持这种情况（例如RAW镜像或故障转储），那么我们就只能对不可读的页进行零填充，我们并不知道这些页原本就是零，还是不可读。



## PTE重映射 VS MmMapIoSpace

对于熟悉WinPmem的用户来说，可能都知道WinPmem使用了一种名为PTE重映射的技术。所有内存获取工具都必须将物理内存映射到内核的虚拟地址空间，所有软件只能读取虚拟地址空间，并且无法直接访问物理内存。

通常，有4种技术可以将物理内存映射到虚拟内存：

1、使用.PhysicalMemory设备，这是一种将物理内存导出到用户控件的老方法，并且已经被Windows禁用了很长时间。

2、使用未公开的MmMapMemoryDumpMdl()函数，将任意物理页映射到内核空间。

3、使用MmMapIoSpace()函数，该函数通常用于将PCI设备DMA缓冲区映射到内核空间。

4、直接进行PTE重映射，这也是WinPmem所使用的技术。

从操作系统稳定性的角度来看，获取内存在定义上是不正确的操作。例如，在驱动程序验证程序运行WinPmem的MmMapIoSpace()模式，将会产生代码为0x1233的0x1a错误检查，错误信息为：“有一个驱动程序试图映射未锁定的物理内存页。由于页的内容或属性可能随时发生变化，因此该操作非法”。

但在技术上来说，这是正确的，我们将系统物理内存的一些随机页映射到虚拟内存空间，但我们实际上并不是这些页的所有者，所以任何人都可以随时继续使用这些页。显然，如果我们想要编写一个内核驱动程序，映射实际上并非我们拥有的物理内存不是一个好的行为，但这正是内存采集的意义所在。

另一个有趣的问题是缓存属性。大多数人可能都认为直接PTE操作不太可靠，因为它会绕过操作系统，直接映射物理页面，而忽略内存缓存属性。但实际上，操作系统其实执行了许多额外的检查，目的就是为了捕获到错误的API使用。例如，如果缓存属性不正确，那么对MmMapIoSpace()函数的请求可能就会失败。如果我们想读取并写入内存，那么需要考虑缓存的一致性，但在这里我们只想获取内存，因此在这里是没关系的。不管无论如何，我们都只会对镜像进行操作，缓存是不可能以任何方式影响到镜像的。

WinPmem同时具有PTE重映射和MmMapIoSpace()模式。MmMapIoSpace()模式通常情况下无法收集更多页。下图分别是PTE重映射方法和MmMapIoSpace()方法所获得的输出结果。<br>
PTE重映射方法：

[![](https://lh5.googleusercontent.com/FMTrYFnzRR3M8wpm6F605y044muBn1Jf80nh5ygMSqsP7puyR5dxcPFKf4eXVnVXILuG2MgDdCIZyQT2dUeSBmqJW8Dg68gzW7fDSO_b7IlIZn6Fl1gEYU3OJZX22OPMd9bKuTp5)](https://lh5.googleusercontent.com/FMTrYFnzRR3M8wpm6F605y044muBn1Jf80nh5ygMSqsP7puyR5dxcPFKf4eXVnVXILuG2MgDdCIZyQT2dUeSBmqJW8Dg68gzW7fDSO_b7IlIZn6Fl1gEYU3OJZX22OPMd9bKuTp5)

[![](https://lh5.googleusercontent.com/LgyoiJ3Xn6ZmPmNtfVLhzBGBljsv75rDqQOT0L9YaUCY0kRbqOEq8rttbz7GAAEOt5v0rJ-bunmc1PB8dDcFqQIkbZ4fcXEUtuOGgWi0IYj2_s2kHQqCRdGYYie-SJdM5tW_79V7)](https://lh5.googleusercontent.com/LgyoiJ3Xn6ZmPmNtfVLhzBGBljsv75rDqQOT0L9YaUCY0kRbqOEq8rttbz7GAAEOt5v0rJ-bunmc1PB8dDcFqQIkbZ4fcXEUtuOGgWi0IYj2_s2kHQqCRdGYYie-SJdM5tW_79V7)<br>
MmMapIoSpace()方法：<br>[![](https://lh6.googleusercontent.com/IYBohw1bHuFYXSllRMB_UvFsadIsrfpacKz6bIucGONezWX1h7MMLFvxqeEZs0PyGOHBP6aeeJIlmlRoT0d0ONB5e-vtqtiKTn2kj6YsAZcJ6BfquCmEIQJI1NPQnLqWFEUU_KpR)](https://lh6.googleusercontent.com/IYBohw1bHuFYXSllRMB_UvFsadIsrfpacKz6bIucGONezWX1h7MMLFvxqeEZs0PyGOHBP6aeeJIlmlRoT0d0ONB5e-vtqtiKTn2kj6YsAZcJ6BfquCmEIQJI1NPQnLqWFEUU_KpR)<br>[![](https://lh4.googleusercontent.com/LUwBEaLoNNfsihIk9doIzwuUP0jRSFPuOIpLSk5lNOqNuD-jNTgJl5COZlCS92ZZ8gr9UwVbzZs8dvkLdg0VBYCUlcTqw9HG18OgahnNppi0hbX6UlojH072wAzq1wsFuM4p_nee)](https://lh4.googleusercontent.com/LUwBEaLoNNfsihIk9doIzwuUP0jRSFPuOIpLSk5lNOqNuD-jNTgJl5COZlCS92ZZ8gr9UwVbzZs8dvkLdg0VBYCUlcTqw9HG18OgahnNppi0hbX6UlojH072wAzq1wsFuM4p_nee)

如我们所见，MmMapIoSpace()方法无法读取更多的页，并且内核调试器证明了有一些它无法读取的页仍然可以访问。



## 总结

本文是我在进行虚拟安全模式系统内存采集工作原理研究过程中的记录。如果读者发现其中存在任何错误，欢迎在DFIR/Rekall/Winpmem邮件列表中发表评论。在我看来，WinPmem无法读取受保护的页面是有道理的，甚至内核调试器也无法读取相同的页面。但是，我检查了DumpIt生成的镜像，它居然包含了本应不可读的这些页面的数据（并不是全零）。另一个有趣的事情时，DumpIt会报告没有读取页面的错误（如上文截图所示），因此该工具会声称已经读取了所有页面（包括那些受VSM保护的页面）。但实际上，DumpIt是否以其他的方法实现了读取，或者它是否存在诸如未初始化缓冲区的问题从而导致读取失败的页返回了随机垃圾数据？我们还需要进一步进行测试，才能对上述问题有一个准确的回答。



## 致谢

感谢Binalyze的Emre Tinaztepe进行的测试工作，同时感谢Matt Suiche的反馈以及进行的深入研究和工具制作。
