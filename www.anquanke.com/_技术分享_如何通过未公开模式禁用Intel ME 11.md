> 原文链接: https://www.anquanke.com//post/id/86740 


# 【技术分享】如何通过未公开模式禁用Intel ME 11


                                阅读量   
                                **198873**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.ptsecurity.com
                                <br>原文地址：[http://blog.ptsecurity.com/2017/08/disabling-intel-me.html](http://blog.ptsecurity.com/2017/08/disabling-intel-me.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t016359e1c2ed128277.jpg)](https://p0.ssl.qhimg.com/t016359e1c2ed128277.jpg)

<br>

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：260RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**



Positive Technologies研究团队对**英特尔管理引擎**（Intel Management Engine，Intel ME）11的内部构造深入研究后，找到了在硬件初始化及主处理器启动后禁用Intel ME的一种方法。在本文中，我们会介绍发现这个未公开模式的详细过程，也会介绍这一模式与美国政府的**高保证平台**（High Assurance Platform，HAP）之间的具体关系。

免责声明：本文介绍的方法存在一定的风险，可能会损坏或损毁你的计算机。我们对用户的任何实验行为不承担任何责任，也不保证整个过程能顺利完成。如果有人了解相关风险后想继续实验，建议在**SPI**（Serial Peripheral Interface，串行外设接口）编程器的帮助下进行。

**<br>**

**二、简介**

Intel ME是一项专有技术，由集成在平台控制单元（Platform Controller Hub，PCH）中的一个微控制器以及一组内置的外部设备所组成。PCH承担了处理器与外部设备之间的绝大部分通信，因此，Intel ME可以访问计算机上的几乎所有数据。如果攻击者可以在Intel ME上执行第三方代码，他就能完全控制整个平台。世界各地的研究人员对Intel ME的内部构造越来越感兴趣，其中一个原因在于这个子系统已经迁移到了新的硬件（x86）以及软件（操作系统为修改版的MINIX）平台上。在x86平台上，研究者可以使用得心应手的二进制代码分析工具。在此之前，对相关固件的分析非常困难，因为早期版本的ME使用了ARCompact微控制器，指令集完全不同。

不幸的是，之前我们无法分析Intel ME 11，因为其中的可执行模块经过霍夫曼（Huffman）编码的压缩，使用了未知的压缩表。尽管如此，我们的研究团队（Dmitry Sklyarov、Mark Ermolov以及Maxim Goryachy三名成员）还是成功恢复了这些压缩表，开发了一个工具来解压镜像。大家可以在[GitHub](https://github.com/ptresearch/unME11)上下载这个工具。

解压可执行模块之后，我们继续研究Intel ME的内部软件及硬件结构。我们的团队一直在这方面开展研究，也累积了大量研究成果，这些成果将于未来逐步公开。本文也是分析Intel ME内部构造及禁用ME核心功能系列文章的第一篇文章。一直以来，研究人员致力于找到禁用该功能的具体方法，以减轻Intel ME中的任何零日漏洞可能带来的数据泄露风险。

**<br>**

**三、如何禁用ME**

某些x86计算机用户曾经问过这样一个问题：如何禁用Intel ME？包括[Positive Technologies专家](https://hardenedlinux.github.io/firmware/2016/11/17/neutralize_ME_firmware_on_sandybridge_and_ivybridge.html)在内的许多人已经多次提出过这个问题。基于Intel ME的[英特尔主动管理技术（Intel Active Management Technology，AMT）](https://nvd.nist.gov/vuln/detail/CVE-2017-5689)最近出现了一个严重漏洞（评分为9.8/10），随着这个漏洞的披露，找到这个问题的答案也愈加紧迫。

令人失望的是，在现代计算机上，我们无法完全禁用ME。原因主要是因为这项技术负责初始化、管理电源以及启动主处理器。另一个复杂原因在于，某些数据被集成在PCH芯片内部，而PCH正是现代主板上的南桥。某些爱好者尝试在维持计算机可操作性的前提下，移除了ME镜像中的所有“冗余”部分，实现对ME的禁用，这也是之前采用的主要方法。但这种方法没有那么简单，因为如果内置的PCH代码没有在闪存中找到ME模块，或者检测到相关模块处于损坏状态，那么系统将无法启动。

经过多年的研发，[me_cleaner](https://github.com/corna/me_cleaner)项目已经开发了一个实用工具，可以删掉ME镜像中的大部分组件，只保留对主系统来说至关重要的组件。但这样处理后，即使系统成功启动，留给我们的时间也非常短，大约30秒之后系统就可能会自动关机。原因在于，一旦出现故障，ME就会进入恢复模式（Recovery Mode），在这个模式下，系统只能运行一段时间。这样一来，“瘦身”过程就会变得非常复杂。比如，在早期版本的Intel ME中，我们可以将镜像大小缩小到90KB，但Intel ME 11的镜像只能缩小到650KB。

[![](https://p1.ssl.qhimg.com/t01ffbdab293dd4b56d.png)](https://p1.ssl.qhimg.com/t01ffbdab293dd4b56d.png)

<br>

**四、隐藏在QResource中的秘密**

Intel允许主板厂商设置少量ME参数。Intel为硬件厂商提供了特殊的软件来实现这一点，这些软件包括用于配置ME参数的闪存镜像工具（Flash Image Tool，FIT），以及通过内置的SPI控制器来直接对闪存进行编程的闪存编程工具（Flash Programming Tool，FPT）。这些程序并没有提供给最终用户，但我们很容易就能在网上找到这些工具的下载地址。

[![](https://p5.ssl.qhimg.com/t017a8afc8ab3969547.png)](https://p5.ssl.qhimg.com/t017a8afc8ab3969547.png)

我们可以从这些工具中提取出大量XML文件（详细过程请点击[此链接](https://www.troopers.de/downloads/troopers17/TR17_ME11_Static.pdf)）。这些文件包含许多有趣的信息，包括ME固件的结构、PCH strap的描述以及集成在PCH芯片中的各种子系统的特殊配置信息。其中名为“reserve_hap”的某个字段引起了我们的注意，因为这个字段后紧跟着一行注释：“启用高保证平台（HAP）”。

[![](https://p2.ssl.qhimg.com/t01b69c7c695c541bd8.png)](https://p2.ssl.qhimg.com/t01b69c7c695c541bd8.png)

使用Google搜索后，我们很快就找到了一些信息。根据搜索结果，该字段与美国国家安全局（NSA）的可信平台计划（trusted platform program）有关。关于这个计划，大家可以访问[此链接](http://fm.csl.sri.com/LAW/2009/dobry-law09-HAP-Challenges.pdf)了解详细信息。首先，我们第一反应是设置一下这个比特位，看设置完毕后会发生什么情况。只要掌握SPI编程器或者可以访问闪存描述符（Flash Descriptor），我们就可以设置这个比特（许多主板通常没有正确设置对闪存区域的访问权限）。

[![](https://p2.ssl.qhimg.com/t01587d4b13b6625a45.png)](https://p2.ssl.qhimg.com/t01587d4b13b6625a45.png)

平台加载后，MEInfo工具报告了一个非常奇怪的状态：“Alt Disable Mode.（Alt禁用模式）”。经过快速检查，我们发现ME没有响应命令，也没有对操作系统发出的请求做出反应。我们决定找出系统进入这个模式的原因，以及当前这种情况的具体意义。当时，我们已经分析了BUP模块的主要部分，这个模块用于平台的初始化，也用于设置MEInfo所显示的状态。为了了解BUP的工作机制，我们需要详细介绍一下Intel ME软件环境的具体信息。

**<br>**

**五、Intel ME 11架构概览**

从PCH 100系列开始，Intel完全重新设计了PCH芯片。嵌入式微控制器的架构由ARC的ARCompact切换到x86架构。Intel选择Minute IA（MIA）32位微控制器作为基础单元，该微控制器在Intel Edison微机以及SoC Quark上使用，结合使用了Intel 486微处理器以及奔腾处理器的一组指令集（ISA）。然而，对于PCH来说，Intel使用22纳米半导体技术制造了核心组件，使得微控制器具备更高的能效。在新的PCH中有三个这样的核心组件：管理引擎（ME）、集成传感器中心（Integrated Sensors Hub，ISH）以及创新引擎（Innovation Engine，IE）。后两者可根据PCH模型以及目标平台启用或者禁用，而ME核心始终处于启用状态。

[![](https://p3.ssl.qhimg.com/t011b30707e490c287b.png)](https://p3.ssl.qhimg.com/t011b30707e490c287b.png)

这种大范围的修改同样涉及到ME软件的修改。具体说来，MINIX被选择作为基础操作系统（之前使用的是ThreadX RTOS）。现在的ME固件包含全功能版的操作系统，包括进程、线程、内存管理、硬件总线驱动、文件系统以及其他许多组件。ME中也集成了一个硬件加密处理器，支持SHA256、AES、RSA以及HMAC。用户进程可以通过本地描述符表（local descriptor table ，LDT）来访问硬件。进程的地址空间由LDT进行管理，该空间只是内核的全局地址空间的一部分，内核全局地址空间也由本地描述符来指定。因此，与Windows或Linux系统不同的是，内核不需要在不同进程的内存之间进行切换（修改页表目录）。

了解Intel ME软件的背景知识后，现在我们可以分析操作系统以及模块的具体加载过程。

**<br>**

**六、Intel ME加载过程的各个阶段**

整个加载过程从ROM程序开始，ROM程序位于内置的PCH只读存储区中。不幸的是，普通用户无法掌握读取或重写这部分存储区的方法。然而，我们可以在网上找到ME固件的预发行版，这个版本包含ROMB（ROM BYPASS）组件，我们假定这个组件与ROM的功能有所重复。因此，检查这个固件后，我们就可能重现初始化程序的基本功能。

通过检查ROMB，我们可以确定ROM执行一系列操作的目的，这些操作包括初始化硬件（比如，初始化SPI控制器）、验证FTPR头部的数字签名、加载闪存中的RBE模块。然后，RBE会验证KERNEL、SYSLIB以及BUP模块的校验和，并将控制权交给内核入口点。

需要注意的是，ROM、RBE以及KERNEL的执行位于MIA内核的0权限（ring-0）级别下。

[![](https://p0.ssl.qhimg.com/t01fcd13a2017bb8b66.png)](https://p0.ssl.qhimg.com/t01fcd13a2017bb8b66.png)

内核创建的第一个进程是BUP，这个进程运行在ring-3级别的自身地址空间中。内核本身并不会启动其他任何进程，这些动作由BUP来完成，还有另一个独立的模块（LOADMGR），后面我们会专门讨论。BUP（BringUP平台）的目的是初始化平台（包括处理器）的整个硬件环境，执行主电源管理功能（比如，当按下电源键时启动平台），并且启动所有其他ME进程。因此，可以肯定的是，如果缺少有效的ME固件，PCH 100以及更高版本系列物理上就无法从启动。首先，BUP会初始化电源管理控制器（PMC）以及ICC控制器。其次，BUP会根据某些字符串来启动某些进程，其中某些字符串硬编码在固件中（如SYNCMAN、PM、VFS），其他字符串包含在InitScript中（InitScript类似于autorun，保存在FTPR卷标头中，经过数字签名）。

[![](https://p2.ssl.qhimg.com/t01d860645d6535028e.png)](https://p2.ssl.qhimg.com/t01d860645d6535028e.png)

因此，BUP会读取InitScript，启动符合ME启动类型的所有IBL进程。

[![](https://p3.ssl.qhimg.com/t01753bd81bc33caf3d.png)](https://p3.ssl.qhimg.com/t01753bd81bc33caf3d.png)

[![](https://p3.ssl.qhimg.com/t017efbae68f6be2c40.png)](https://p3.ssl.qhimg.com/t017efbae68f6be2c40.png)

如果某个进程无法启动，BUP就不会启动系统。如图9所示，LOADMGR是列表中的最后一个IBL进程。该进程会启动剩余的进程，但与BUP不同的是，如果模块启动过程中出现错误，LOADMGR会继续执行下一个模块。

这意味着给Intel ME“瘦身”的第一种方法是删除InitScript中没有IBL标志的所有模块，这样就能显著减少固件的大小。但我们最初的任务是找到HAP模式下的ME出现了什么状况。为了找到问题的答案，我们可以看一下BUP软件模型。

[![](https://p5.ssl.qhimg.com/t01df62790b2e5d71ae.png)](https://p5.ssl.qhimg.com/t01df62790b2e5d71ae.png)

**<br>**

**七、BringUP**

如果你仔细研究BUP模块的工作方式，你会发现BUP中实现了一个经典的有限状态机。执行过程从功能上分为两个部分：初始化阶段（有限状态机）以及在系统初始化后根据其他进程的请求来执行服务。根据平台以及SKU（TXE、CSME、SPS、消费者以及企业）的不同，初始化阶段的数量也会有所不同，但对于所有版本来说，主要的阶段都是相同的。

**7.1 阶段1**

初始化阶段会创建sfs内部诊断文件系统（SUSRAM FS，位于非易失性存储区中的一个文件系统），读取配置信息，最关键的是，会向PMC查询哪个动作触发了启动过程：是平台插电、整个平台的重启、ME重启还是从睡眠中唤醒。这个阶段称之为启动流确定阶段。有限状态机初始化的后续阶段需要依赖这一阶段。此外，这一阶段还支持多种模式：普通模式以及一组服务模式，后一个模式中，主ME功能处于禁用状态（如HAP、HMRFPO、TEMPDISABLE、RECOVERY、SAFEMODE、FWUPDATE以及FDOVERRIDE功能）。

**7.2 阶段2**

这个阶段会初始化ICC控制器，加载ICC配置文件（负责主要消费者的时钟频率）。同时，这个阶段会初始化Boot Guard，开启处理器启动确认的轮询过程。

**7.3 阶段3**

BUP等待来自PMC的一则信息，以确认主处理器已启动。随后，BUP启动电源事件的PMC异步轮询过程（平台的重启或关闭），然后进入下一阶段。如果这类事件发生，那么BUP就会执行初始化阶段所请求的动作。

**7.4 阶段4**

这个阶段会初始化内部硬件。与此同时，BUP启动heci轮询（heci是个特殊设备，用来接收来自BIOS或操作系统的命令），查询BIOS中的DID（DRAM Init Done，DRAM初始化完成）信息。这个消息可以让ME确定主BIOS是否已完成RAM的初始化并为ME保留一个特殊的区域（UMA），之后会进入下一个阶段。

**7.5 阶段5**

一旦收到DID消息，根据具体的模式不同（这个模式由多种因素决定），BUP会（以正常模式）启动InitScript中的IBL进程，或者会在循环中挂起，只有收到来自PMC的消息（例如收到重启或关闭系统的请求）才会退出循环。

正是在这个阶段，我们找到了HAP处理过程。在这个模式中，BUP会挂起，不会执行InitScript。这意味着正常模式中的后续动作与HAP没有关系，因此也不需要去考虑。我们需要重点关注的是，在HAP模式下，BUP会初始化整个平台（ICC、Boot Gurad），但不会启动主ME进程。

[![](https://p4.ssl.qhimg.com/t01b425823a21cca65f.png)](https://p4.ssl.qhimg.com/t01b425823a21cca65f.png)

[![](https://p1.ssl.qhimg.com/t0178e82cf873ce319d.png)](https://p1.ssl.qhimg.com/t0178e82cf873ce319d.png)

[![](https://p4.ssl.qhimg.com/t018d0ff196dd23bd6e.png)](https://p4.ssl.qhimg.com/t018d0ff196dd23bd6e.png)

**<br>**

**八、设置HAP比特**

根据前面的分析，我们可以找到第二种方法来禁用Intel ME：

1、设置HAP比特。

2、在FTPR的CPD区中，删除或破坏除BUP启动需要用到的模块之外的其他所有模块，BUP启动需要用到如下模块：

**RBE**

**KERNEL**

**SYSLIB**

**dBUP**

3、修复CPD头部的校验值（可访问[此链接](https://www.troopers.de/downloads/troopers17/TR17_ME11_Static.pdf)了解ME固件结构的详细信息）。

那么，我们如何设置HAP比特？我们可以使用FIT配置文件，确定镜像中该比特的具体位置，但还有另一种更为简单的方法。在FIT的ME内核区中，我们可以找到一个保留参数。这个比特可以启动HAP模式。

[![](https://p4.ssl.qhimg.com/t019cea33375380f02e.png)](https://p4.ssl.qhimg.com/t019cea33375380f02e.png)

**<br>**

**九、HAP以及Boot Guard**

此外，我们还在BUP中找到某些代码，当HAP模式处于启用状态时，这些代码会在Boot Guard策略中设置一个额外的比特。不幸的是，我们还没有找到这个比特所控制的具体对象。

[![](https://p3.ssl.qhimg.com/t01f67681bfb9451708.png)](https://p3.ssl.qhimg.com/t01f67681bfb9451708.png)

**<br>**

**十、me_cleaner中对ME 11的支持**

当我们在准备这篇文章时，me_cleaner开发者更新了他们的程序。现在，这个程序也可以删除镜像中除RBE、KERNEL、SYSLIB以及BUP之外的所有模块，但没有设置HAP比特，这样就会迫使ME进入TemporaryDisable（临时禁用）模式。我们很好奇这种做法会导致什么情况出现。

我们发现删除分区以及ME文件系统后，会导致cfgrules文件读取过程中出现错误。这个文件包含许多不同的系统设置。正如我们猜测的那样，这些系统设置中包含一个名为“bupnottemporarydisable”的标志。如果没有设置这个标志，整个子系统就会切换到TemporaryDisable模式，此外，由于这个标志为初始化为0的全局变量，因此读取错误会被当成已断开的配置请求错误。

此外，我们还检查了服务器版以及移动版的ME固件（SPS 4.x以及TXE 3.x）。在服务器版本中，这个标志总是设为1；在移动版本中，这个标志会被忽略。这意味着这种方法在服务器版以及移动版（Apollo Lake）的ME中无法奏效。

[![](https://p1.ssl.qhimg.com/t014299f2d4bd877657.png)](https://p1.ssl.qhimg.com/t014299f2d4bd877657.png)

**<br>**

**十一、尾声**

在本文中，我们找到了一个未公开的PCH strap，可以切换到一种特殊的模式，在早期阶段就能禁用Intel ME的主要功能。之所以能得出这个结论，主要依据有三点：

1、依据对Intel ME固件的二进制分析过程，如前文所述。

2、如果我们移除某些关键的ME模块并启动HAP模式，Intel ME并不会崩溃。这足以证明HAP在早期阶段就禁用了ME。

3、我们非常肯定Intel ME无法退出这个模式，因为我们没有在RBE、KERNEL以及SYSLIB模块中找到能够执行此操作的相关代码。

同样，我们可以确定的是，集成到PCH中的ROM实际上与ROMB相同，ROMB中也没有包含退出HAP模式的任何代码。

因此，HAP可以防护除RBE、KERNEL、SYSLIB、ROM以及BUP模块之外的所有模块中可能存在的漏洞。然而，不幸的是这个模式无法防止攻击者利用早期阶段中存在的错误。

Intel表示他们已得知我们的研究细节。从他们的回应中，证实了我们对HAP程序未公开模式的猜想。在Intel的许可下，我们摘抄了部分回应内容，如下所示：

“致Mark/Maxim：

为了响应具有特殊要求的客户请求，我们有时候会修改或禁用某些功能。在这种情况下，我们会根据设备制造商的要求进行修改，以响应客户对美国政府的“高保证平台”计划的支持。这些修改的验证周期较为有限，并不是官方支持的配置。”

我们可以肯定的是，这种机制旨在满足政府机构的典型需求，以减少侧信道数据泄露的风险。但主要的问题仍然没有得到解决：那就是HAP如何影响Boot Guard？由于HAP是一项封闭性技术，我们无法回答这个问题，但我们希望不久的将来这个问题能够得到解答。
