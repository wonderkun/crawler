> 原文链接: https://www.anquanke.com//post/id/236483 


# Android可信执行环境安全研究（一）：TEE、TrustZone和TEEGRIS


                                阅读量   
                                **132851**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者riscure，文章来源：riscure.com
                                <br>原文地址：[https://www.riscure.com/blog/samsung-investigation-part1﻿](https://www.riscure.com/blog/samsung-investigation-part1%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01098fe9eecf1113ec.jpg)](https://p4.ssl.qhimg.com/t01098fe9eecf1113ec.jpg)



## 0x00 前言

在过去的几年内，可信执行环境（TEE，Trusted Execution Environment）在Android生态系统中实现了普及。在这一系列文章中，我们将分析三星Galaxy S10中实现的TEEGRIS TEE操作系统的安全性，分析其中存在的漏洞和修复方式。本文涉及到的全部漏洞均已在当时报告给三星，并且已经在2019年年底完成修复。<br>
我们此次研究的目标是评估三星TEE OS的安全性，分析是否可以对其进行攻击以获取运行时控制并提取所有受保护的数据，例如对用户数据进行解密。在分析过程中，我们并没有考虑完整的漏洞利用链，而是假设攻击者已经控制了Android环境，仅仅关注TEE的安全性。<br>
这一系列文章基于我们先前在2020年9月Riscure Workshop的演讲。<br>
1、在第一篇文章中，我们将分析TEE、TrustZone和TEEGRIS；<br>
2、在第二篇文章中，我们将研究在TEEGRIS中运行的TA所存在的漏洞，我们将利用其中一个TA来获得运行时控制。<br>
3、在最后一篇文章，我们将展示如何进一步提升特权，并获得对完整TEE内存的访问权限。



## 0x01 可信执行环境（TEE）

可信执行环境是为了在执行对敏感任务（例如：付款、用户身份验证、用户数据保护）时提供安全的环境。<br>
安全环境与名为富执行环境（REE，Rich Execution Environment）的非安全或不受信任的环境相互隔离。在我们所分析的案例中，也就是Android OS，在后续文章中REE可以等价为Android。TEE操作系统通常由具有较高特权的内核和具有较低特权的多个应用程序（称为可信应用程序，TA，Trusted Applications）组成。TA之间彼此隔离，且与TEE内核隔离。这样一来，如果有应用程序被攻陷，它就无法危害到其他应用程序或TEE内核。简而言之，一个强大的TEE机制可以实现下述三类隔离：<br>
1、TEE与REE之间的隔离；<br>
2、TA和TEE内核之间的隔离；<br>
3、TA之间的隔离。<br>
为了达到这些安全需求，TEE需要硬件原语的支持，以强制进行隔离。硬件和软件之间的配合是至关重要的，并且需要持续配合。<br>
广义上来说，TEE由多个组件组成，具体包括：<br>
1、TEE感知硬件；<br>
2、强大的安全启动（Secure Boot）链，用于初始化TEE软件；<br>
3、TEE OS内核，用于管理安全区域和可信应用程序；<br>
4、可信应用程序，用于向TEE提供功能。<br>
在我们的系列文章中，将聚焦在1、3和4上面，并且我们假设平台已经正确实施了安全启动。我们假设攻击者已经控制REE，从而可以与TEE进行通信，其攻击目标是完整攻陷TEE。<br>
TEE内核通常仅向Android OS暴露非常有限的接口，大多数功能都是由TA实现的。所以我们的计划是首先在TA中找到可以利用的漏洞，然后提升权限到内核。但是，在进入到反汇编程序之前，我们首先要看一下用于实现TEE的ARM扩展——TrustZone。



## 0x02 ARM的TrustZone

TrustZone技术是ARM开发的一种硬件体系结构，它允许软件在安全与非安全的两个域中执行。这是使用“NS”位来进行标识的，这一位可以指示master是在安全模式下还是非安全模式下运行。这里所说的master可以是CPU内核，也可以是硬件外设（例如DMA或加密引擎）。master是否安全，可以在设计中通过硬连线来定义，也可以通过配置定义。例如，可以通过调用SMC指令（稍后详细介绍）或切换SCR寄存器中的NS位来切换CPU内核的安全状态。<br>
为了定义slave（例如外围设备或内存）的访问限制，TrustZone通常包括两个组件，分别是TrustZone地址空间控制器（TZASC）和TrustZone保护控制器（TZPC）。<br>
TZASC可以用于定义DRAM中的安全范围。ARM提供了两种不同的实现方式，最新的是TZC-400。下图概述了其通常情况下在SoC中的实现方式，引自官方技术文档。<br>
TZASC概述：

[![](https://p5.ssl.qhimg.com/t01b1d912311c46e18a.png)](https://p5.ssl.qhimg.com/t01b1d912311c46e18a.png)

可以看出，任何对DRAM存储器的访问都会首先通过TZASC，然后转发给内存控制器。TZASC可以基于一组内部规则来判断是否允许访问内存。<br>
TZASC包含一个始终启用的基础区域（区域0），能够跨越整个DRAM内存范围。此外，还定义了许多其他安全区域，可以限制对其的访问。详细来说，在其他区域可以设置以下内容：<br>
1、起始地址和结束地址。<br>
2、安全读取和写入的权限。这些权限将应用在尝试访问内存范围的任何安全master上。请注意，TZASC没有委派给MMU的执行许可和强制执行的概念。<br>
3、非安全ID过滤。可以将区域配置为允许访问非安全的master。对于TZC-400来说，可以为读取和写入权限来设置位掩码，以便对允许哪些非安全master访问内存范围进行精细化控制。<br>
TZPC实现了类似的概念，但适用于内部外围设备和SRAM，不适用于外部DRAM。其中包含一个寄存器（R0size），以4KB为单位指定安全分片上SPAM的大小。与TZASC相比，它不太灵活，因为它只允许定义一个安全区域和一个非安全区域，安全区域是从0开始直到指定的大小，剩余的SRAM直接被视为非安全区域。<br>
然后，还有很多其他的寄存器，用于为每个外围设备指定其安全性（只能由安全的master访问）。TZPC寄存器中的不同位对应哪些外设并没有定义，并且它是完全针对不同的SoC。<br>
通常，TZASC和TZPC的大多数设置都是在初始化期间配置的，并且永远不会更改。但是，其中有一些需要在运行时动态修改。这里的一个示例是用于执行安全付款的可信用户界面（TUI）。以S10手机的三星支付为例，当用户需要输入PIN来授权付款时，TEE将会接管，并直接控制显示屏和触摸传感器。这里的底层逻辑是，由于PIN是一个敏感数据，因此交由TEE来处理整个过程，而不再使用不受信任的Android OS。因此，必须使用TZPC将显示器和触摸控制器重新配置为“安全”，这样一来，即使是在Android中运行内核级代码的攻击者也无法获取到PIN。要在屏幕中显示图像，需要在DRAM中存储一个安全的帧缓冲区，因此TEE还会使用TZASC将DRAM中的一部分重新配置为“安全”，并将其作为帧缓冲区。在用户输入完PIN后，TZASC和TZPC将其恢复为之前的值，然后Android再次接管。<br>
安全和非安全模式之间的转换由名为“安全监视器”（Secure Monitor）的组件来管理。这个监视器是TEE和REE之间的主要接口，并且是唯一可以修改内核安全状态的组件。<br>
与在REE中一样，TEE在内核和TA之间保持用户模式与内核模式之间的隔离。TEE OS还负责加载TA，并在REE和TA之间传递参数。TA在安全区域的用户空间中运行，并为REE提供服务。<br>
ARMv8-A CPU在每个区域中支持四个特权级别，也将其称为异常级别，分别是：<br>
(S-)EL0 – 用户模式/APP<br>
(S-)EL1 – 内核<br>
EL2 – 管理程序（Hypervisor）<br>
EL3 – 安全监视器（Secure Monitor）

[![](https://p1.ssl.qhimg.com/t01f201c979e35a1afd.png)](https://p1.ssl.qhimg.com/t01f201c979e35a1afd.png)

在REE中，我们的Android应用程序在EL0上运行，而Linux内核则在EL1上运行。<br>
EL2仅以非安全模式存在（在ARMv8.4-A版本之前），称之为管理程序（Hypervisor）。它最初被设计为一种处理以较低特权级别并行运行的多个虚拟环境的方法，但是在Android环境中，通常将其用作内核加固机制。在三星手机中也是如此，管理程序组件被称为实时内核保护（RKP，Real-time Kernel Protection），除了这些用途之外，它还限制了内核可以访问的内存，并将某些内核结构设置为只读，从而增加了内核漏洞利用的难度。在系列文章的第三篇中，我们将详细分析RKP。<br>
最后，我们来分析安全组件，我们研究的目标是EL3（始终以安全模式运行）、S-EL0和S-EL1。关于TEE的实现方式，有多种方式，但是目前最常见的示例是：在EL3上运行一个非常小的组件，负责在两个区域之间进行切换；在EL1上运行一个成熟的内核；在EL0上运行多个TA。三星的TEE OS TEEGRIS也采用了这样的设计方式。<br>
尽管完全隔离的环境非常安全，但在使用的过程中，它还是需要与Android中运行的其他不受信任的组件进行通信。REE和TEE之间的通信使用名为“安全监视器调用”（SMC）的专用指令触发。两个指令都可以在EL &gt; 0时调用该指令，这意味着Android应用程序无法直接启动与TEE的通信。通常的情况是Linux内核充当代理并公开驱动程序，应用程序可以使用该驱动程序与TEE进行交互。这种设计的优势在于，可以将访问限制策略（例如使用SELinux）应用于访问驱动程序的场景中，以确保只有部分应用程序可以与TEE通信，从而收敛了攻击面。对于S10手机来说，情况也是如此，仅允许有限的应用程序和服务与TEE通信。<br>
请注意，在我们的后续研究中，我们假设攻击者具有与TEE进行通信的能力。在使用Magisk这样的工具对手机进行root时就是这种情况，或者，也可以获取Linux内核的运行时控制，还可以获取允许与TEE通信的Android应用/服务的运行时控制。<br>
一旦执行了SMC指令，就会在EL3中运行的安全监视器中生成一个中断。SMC处理机制会将SMC路由到相应组件。如果监视器可以直接处理SMC，那么就进行处理并立即返回。否则，会将请求转发到TEE内核（在S-EL1运行），然后在其内部进行处理，或者继续将其转发到在S-EL0运行的TA。<br>
现在，我们已经了解TrustZone的工作原理，接下来来分析一下三星的实现方式。



## 0x03 TEEGRIS

TEEGRIS是一个相对较新的TEE操作系统，由三星在Galaxy S10机型上首次推出。从2019年开始，大多数使用Exynos芯片的三星新款手机也开始在TEE中运行TEEGRIS。<br>
在2019年3月推出S10之前，Exynos芯片使用的是另一个由Trustonic开发的、名为Kinibi的TEE OS，此前的一些研究文章对这个操作系统进行了充分分析。不过，由于TEEGRIS是一个相对较新的操作系统，因此网上没有太多的公开信息。实际上，我们只能从一篇网上的文章中找到一些可用信息，这篇文章对TEEGRIS及其内核进行了很好地介绍，主要说明了如何设置QEMU以进行fuzzing。尽管我们主要聚焦在逆向工程的方向，但这篇文章仍然为我们提供了一些有用的信息，例如引导映像布局（存储TEEGRIS的位置），以及如何识别内核中处理的系统调用等。<br>
基于这些信息，我们来分析一下TEEGRIS的主要组件：内核、TA、驱动程序。如前所述，监视器代码在TrustZone中扮演着非常重要的角色，但是在三星的实现中，监视器以加密的方式存储在内存中。因此，我们没有对它进行分析，而是专注于其他组件，这些组件都是以明文存储的。



## 0x04 TEEGRIS内核

TEEGRIS内核是一个在安全EL1中运行的小型组件。即使小，但它从严格意义上说并不是微内核。举例来说，其中集成了很多可以由TA使用的驱动程序。它以64位模式运行，并支持在用户空间中运行的64位和32位TA和驱动程序。由于内核以明文存储在引导分区中，因此我们可以轻松提取它并进行反汇编。<br>
内核实现了许多POSIX兼容的系统调用，还添加了一些TEEGRIS特定的系统调用。在Alexander Tarasikov的文章中我们注意到，有两个共享库中实现的系统调用包装器（请参考下面的TA章节，详细介绍了如何处理共享库），分别是`libtzsl.so`和`libteesl.so`。这让我们可以快速地识别内核中的两个表，分别适用于64位和32位TA的系统调用处理程序。<br>
64位和32位系统调用表：

[![](https://p3.ssl.qhimg.com/t016b3659e4eea14d5d.png)](https://p3.ssl.qhimg.com/t016b3659e4eea14d5d.png)

通过对系统调用进行分析，我们发现三星充分利用了两个在Linux中比较熟悉的例程——`copy_to`和`from_user`。使用这些例程来访问来自用户区域的数据，以确保TA不能引用内部内核结构。<br>`copy_from_user`反编译的代码：

[![](https://p4.ssl.qhimg.com/t012cd20678cc059466.png)](https://p4.ssl.qhimg.com/t012cd20678cc059466.png)

上图中的代码首先验证标志位，以判断是否忽略其他任何检查。当内核使用已知的安全参数直接调用系统调用处理程序时，就会启用这个标志位。如果设置了标志位，这个函数就变成了`memcpy`的包装。<br>
而在其它情况下，代码将调用`check_address`，如下图所示。<br>
地址检查例程：

[![](https://p2.ssl.qhimg.com/t01d939c400ce53fca2.png)](https://p2.ssl.qhimg.com/t01d939c400ce53fca2.png)

上图中的代码片段为我们提供了一些重要的信息，一定不能映射TA的第一页（第10行，可能是为了防止NULL指针解引用），有效的TA地址应该小于`0x40000000`（第12行）。任何比它大的值都将被视为无效，并且会被丢弃。此外需要注意的一点是，复制是使用`LDTR*`指令执行的。`LDTR*`的行为与常规`LDR*`指令相同，但会导致使用EL0特权执行内存访问。这是因为PAN被启用，即使`check_address`函数漏掉了某些边界情况，对内核内存的非特权访问也会导致访问冲突。<br>
TA地址空间的上限`0x40000000`可能意味着ASLR的随机性相对较小，特别是考虑到支持64位TA的情况。为了确认这个假设是否成立，我们分析了如何加载TA映像的过程。请注意，在TEEGRIS中，TA是经过略微修改后的ELF文件，因此我们可以在代码中查找用于解析标准ELF格式的函数。最终，我们找到了`map_elf32_image`函数，在64位TA中也存在等价的函数。<br>
代码和数据段的随机化：

[![](https://p5.ssl.qhimg.com/t013182c502636472ac.png)](https://p5.ssl.qhimg.com/t013182c502636472ac.png)

需要注意的是，该代码强制只能加载PIE可执行文件（第120行）。随后，它生成2个字节的随机数（第132行），用0x7FFF作为掩码（第134行），并将其作为要添加到入口点的页面偏移量（和基址，稍后会在同一函数中完成）。这意味着ASLR偏移最多只能有32768个值，并且它应用于ELF中指定的所有段。<br>
动态内存（例如：用于堆和REE共享的映射内存）在“派生”系统调用时会使用不同的值，但还是采用类似的方法进行随机化。<br>
动态内存随机化：

[![](https://p2.ssl.qhimg.com/t01f93fdf26f9315080.png)](https://p2.ssl.qhimg.com/t01f93fdf26f9315080.png)

请注意，ASLR不仅适用于TA，并且也会在内核中使用（通常称为KASLR）。在这里我们不会过多介绍细节，但是，如果我们最终想要实现内核利用，则需牢记这一点。在入口函数中，内核生成另一个随机值，并相应地修改页和重定位表。<br>
如前所述，在内核中内置了许多驱动程序。驱动程序主要用于和外围设备（例如SPI和I2C）进行通信或执行加密操作。<br>
内核中实现的驱动程序的部分列表：

[![](https://p5.ssl.qhimg.com/t01e153e5984b56b450.png)](https://p5.ssl.qhimg.com/t01e153e5984b56b450.png)

考虑到三星是遵循POSIX规范来实现TEEGRIS的，那么这种与驱动程序进行交互的方式就不足为奇了。驱动程序的名称通常以“dev://”开头，可以从TA打开相应的文件进行访问。随后，TA就可以使用许多系统调用（例如：read、write、ioctl、mmap）与驱动程序进行交互。在内核内部，使用一种结构来存储每个驱动程序的系统调用实现。<br>
在这里，并不是一直向每个TA授予堆驱动程序和系统调用的访问权限。实际上，根据TA所属不同的组，每个组都有不同的权限级别。内核会跟踪向每个TA授予了哪些权限，并执行检查，以确保只有允许的TA才能访问受限制的功能。下面的两张图就展示了授予两个不同组的权限，分别是`samsung_ta`和`samsung_drv`。<br>`samsung_ta`组的访问权限：

[![](https://p4.ssl.qhimg.com/t014e244657fb24c888.png)](https://p4.ssl.qhimg.com/t014e244657fb24c888.png)

`samsung_drv`组的访问权限：

[![](https://p2.ssl.qhimg.com/t01cb708342219bcdec.png)](https://p2.ssl.qhimg.com/t01cb708342219bcdec.png)

如图所示，每个TA有19个权限。其中值为0就表示未授予权限，其他值表示授予了部分或完整权限。其中大多数只是标记已授予和未授予，但有几个（MMAP）还包含一个特定的掩码用以确定是否可以使用读/写/执行特权来映射内存。在上面的两个示例中，`samsung_ta`受到了较多限制，只能访问几个权限，但`samsung_drv`组就具有更大的权限。除此之外，其他组也具有不同的权限，但到目前为止，我们发现上述两个是最为常见的。



## 0x05 TA和用户区域驱动程序

至此，我们对内核工作原理以及与内核的交互方式进行了分析，接下来看看TA。通常，在TEE中使用TA的方式有两种。一种是与TEE OS绑定的不可变的blob，始终在初始化时加载；另一种是可以在运行时由Android加载。三星的TEEGRIS采用了混合的方式，同时支持这两种选择。<br>
引导分区中包含一个特殊的压缩包（`startup.tzar`），其中包含TA所需的所有共享库以及在Android完全引导之前早期系统所需的一些特殊TA和驱动程序，包括TSS（用于管理共享内存）、ACSD（用于支持TA身份验证的驱动程序）和root_task（用于加载TA，与ACSD共同对其进行验证）。tzar压缩包中的二进制文件是标准的ELF文件，可以直接加载到反汇编程序中进行分析。由于压缩包是启用映像的一部分，因此在启动时会验证它的签名。<br>
TA也可以在运行时从Android加载。可加载的TA存储在`/vendor/tee`和`/system/tee`分区中。在S10系列中，大约有30种不同的TA可供加载，其格式如下：

[![](https://p3.ssl.qhimg.com/t0122b4c465fffa2fcc.png)](https://p3.ssl.qhimg.com/t0122b4c465fffa2fcc.png)

1、标头长度为8个字节，包含4个字节的版本信息（SEC2、SEC3或SEC4）和4个字节的内容。<br>
2、内容部分是包含实际TA内容的常规ELF文件。如果TA的类型为SEC4，则内容是加密的，否则内容以明文形式存在。<br>
3、元数据部分包含TA组。从SEC3版本开始，还有一个包含版本号的附加字段。root_task和ACSD会利用这个版本号来管理TA，防止其回滚。当加载SEC3或SEC4版本的TA时，都会提取版本号，并将其与RPMB存储中存储的版本号进行比较。如果低于存储的版本号，则不能加载TA并报错。如果高于存储的版本号，则增加RPMB中的版本号以匹配TA版本，从而不再加载同一TA的较旧副本。这也意味着，从现在开始，SEC2版本的TA将无法使用。这个功能对于防护包含已知漏洞的旧版本TA至关重要，我们将在第二篇文章中对此进行详细介绍。<br>
4、签名部分包含其余映像的RSA签名。它遵循X.509格式，并由ACSD进行解析。<br>
从这个简短的描述中，我们可以看出，如果删除初始标头并将其作为ELF文件加载到反汇编程序中，我们就可以轻松地对TA进行反汇编。唯一比较麻烦的就是SEC4格式，因为其中的ELF已加密，但是实际上，我们发现Galaxy S10和S20中仅使用SEC2和SEC3。然后，TA可以从tzar压缩包中导入库。库也是常规的ELF文件，实现C库函数和Global Platform（GP）API和TEEGRIS特定功能。<br>
TEEGRIS中的TA实现了GP API，在这个API中指定了TA需要实现以与REE交互的5个接口：<br>
1、`TA_CreateEntryPoint`，在加载TA时调用。<br>
2、`TA_OpenSessionEntryPoint`，在REE中运行的客户端应用程序（CA，在我们的场景中为Android应用程序）首次建立与TA的连接时调用。<br>
3、`TA_InvokeCommandEntryPoint`，其中包含将被CA发送的每个命令调用的主命令处理程序。这是大多数TA功能实现的位置。<br>
4、`TA_CloseSessionEntryPoint`，在CA结束与TA的会话时调用。<br>
5、`TA_DestroyEntryPoint`，在从内存中卸载TA时执行。<br>
即使TA是可执行文件，由于实际的`main()`函数位于`libteesl.so`库内部，因此它的执行也比较复杂。启动TA时，实际上会发生以下情况：<br>
1、执行TA内部的start()函数。这个函数通常情况下只是`main()`的包装。<br>`start()`函数的示例：

[![](https://p4.ssl.qhimg.com/t014500be20104b7788.gif)](https://p4.ssl.qhimg.com/t014500be20104b7788.gif)

2、主要函数实际上不在TA内部，而是在`libteesl.so`库中。这里是配置TEEGRIS内核与REE通信的大多数逻辑的地方。建立了一个基于POSIX epoll的标准机制，用于与根TA进行通信。在下面的代码段中，主函数首先调用`TA_CreateEntryPoint()`，然后跳转到`start_event_loop()`。<br>
libteesl主要函数的代码片段：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014f42d1a38655d668.png)

3、在`start_event_loop()`中，该库随后将接收事件，例如来自CA的请求。随后将时间转发到对应的GP API入口点。<br>
这一章的标题是“TA和用户区域驱动程序”，但到目前为止我们说得都是TA。那么，驱动程序在哪里呢？实际上，驱动程序与TA相同。它们具有相同的格式，实现相同的GP API，但调用的是TEEGRIS特定的API，名为`TEES_InitDriver`。该函数允许驱动程序指定驱动程序名称和结构，可用于与用户区域驱动程序进行交互，方式类似于与内核区域驱动程序进行交互的方式。默认情况下，用户区域驱动程序不具有任何特殊权限，但它们通常属于特权较高的组。



## 0x06 漏洞利用缓解措施

总结一下我们对内核和TA的分析，就可以明确在内核和TA中实现的漏洞利用缓解措施。其中的一些已经在前面的内核分析中介绍过了。在这里，我们汇总措施如下：<br>
1、内核和TA中都使用了XN（eXecute Never）。这意味着数据内存永远不可执行，代码永远不可写。<br>
2、内核和TA中使用了栈金丝雀保护（Stack Canaries），以防止栈缓冲区溢出。<br>
3、ASLR和KASLR用于随机化TA和内核的地址空间。<br>
4、使用PAN和PXN可以防止内核访问或执行用户模式内存。<br>
从历史上看，与其他流行的OS相比，此前TEE OS中的漏洞利用缓解措施还是比较少的。之前针对三星TEE的攻击主要针对仅使用XN来防护的旧款机型，所以缓解措施比较少。S10无疑是朝着正确方向迈出了一步，如果攻击者再想要完整攻陷TEE，可能需要结合利用多个漏洞。



## 0x07 与TA通信

现在，我们对TA已经有更多的了解，我们需要了解如何从Android环境中与TA进行通信。幸运的是，GP标准不仅为TA定义了一组API，而且还为希望与TA进行通信的CA定义了一组API。每一个入口点都有一个可供CA使用的对应调用，例如`TEEC_OpenSession`可以用于打开会话，`TEEC_InvokeCommand`可以用于发送命令等等。<br>
对于TEEGRIS来说，`libteecl.so`库实现了GP API，因此与TA进行通信就像使用`dlopen`/`dlsym`来解析GP API所需的符号一样简单。要打开会话，需要指定目标TA的UUID。然后，库会在`/vendor/tee`或`/system/tee`中查找具有该UUID的TA（UUID是文件名），并将整个TA映像都传递给TEE，然后TEE将对其进行身份验证后加载。所有操作都是对CA透明进行的，因此CA并不知道实际通信是如何发生的。<br>
前面我们也提到过，并非每个Android应用都被允许与TEE进行通信。这里存在限制，完整的漏洞利用链需要攻击者首先获得对可以与TEE通信的应用程序的运行时控制。



## 0x08 后续工作

到这里，系列文章的第一部分就已经结束了。在下篇文章中，我们将展示如何识别和利用TA中的漏洞，从而在TA的上下文中得到运行时控制。在最后一篇文章中，我们将分析如何利用它来提升特权并攻陷整个TEE。



## 0x09 参考文章

[1] [https://developer.arm.com/documentation/ddi0504/c/](https://developer.arm.com/documentation/ddi0504/c/)<br>
[2] [https://medium.com/taszksec/unbox-your-phone-part-i-331bbf44c30c](https://medium.com/taszksec/unbox-your-phone-part-i-331bbf44c30c)<br>
[3] [https://labs.bluefrostsecurity.de/blog/2019/05/27/tee-exploitation-on-samsung-exynos-devices-introduction/](https://labs.bluefrostsecurity.de/blog/2019/05/27/tee-exploitation-on-samsung-exynos-devices-introduction/)<br>
[4] [https://blog.quarkslab.com/a-deep-dive-into-samsungs-TrustZone-part-1.html](https://blog.quarkslab.com/a-deep-dive-into-samsungs-TrustZone-part-1.html)<br>
[5] [http://allsoftwaresucks.blogspot.com/2019/05/reverse-engineering-samsung-exynos-9820.html](http://allsoftwaresucks.blogspot.com/2019/05/reverse-engineering-samsung-exynos-9820.html)<br>
[6] [https://globalplatform.org/wp-content/uploads/2018/06/GPD_TEE_Internal_Core_API_Specification_v1.1.2.50_PublicReview.pdf](https://globalplatform.org/wp-content/uploads/2018/06/GPD_TEE_Internal_Core_API_Specification_v1.1.2.50_PublicReview.pdf)
