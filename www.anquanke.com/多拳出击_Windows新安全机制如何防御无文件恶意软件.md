> 原文链接: https://www.anquanke.com//post/id/160962 


# 多拳出击：Windows新安全机制如何防御无文件恶意软件


                                阅读量   
                                **180273**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：microsoft.com
                                <br>原文地址：[https://cloudblogs.microsoft.com/microsoftsecure/2018/09/27/out-of-sight-but-not-invisible-defeating-fileless-malware-with-behavior-monitoring-amsi-and-next-gen-av/](https://cloudblogs.microsoft.com/microsoftsecure/2018/09/27/out-of-sight-but-not-invisible-defeating-fileless-malware-with-behavior-monitoring-amsi-and-next-gen-av/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01a2b647becd28c559.jpg)](https://p4.ssl.qhimg.com/t01a2b647becd28c559.jpg)

## 一、概述

在我们的日常监测过程中，发现有两个前所未见、经过严重混淆的脚本，成功通过了基于文件的反病毒检测，并且动态地将信息窃取Payload加载到内存中。这些脚本通过社会工程的方式实现分发，诱导目标用户运行脚本，脚本的文件名分别是install_flash_player.js和BME040429CB0_1446_FAC_20130812.XML.PDF.js。

其中，Payload非常复杂，难以分析，其原因在于：
1. Payload不存储于磁盘上，因此不会触发文件反病毒扫描；
1. Payload是在执行脚本的合法进程上下文中加载的（wscript.exe）；
1. 在磁盘上没有找到任何痕迹，因此取证分析所发现的证据非常有限。
实际上，这些都属于无文件威胁。针对这类威胁，实际上Windows Defender高级威胁防护的反病毒功能仍然可以检测到Payload并阻止攻击。这是怎么做到的呢？<br>
在此场景中，反恶意软件扫描接口（Antimalware Scan Interface）会对其进行检测。AMSI是一个开放式的接口，允许反病毒产品调用，以检查未经加密和未经混淆的脚本代码行为。

AMSI是动态下一代（Dynamic Next-gen）功能的一部分，使得Windows Defender ATP中的反病毒功能不再仅仅是进行文件扫描。其中的功能还包括行为监控、内存扫描和引导扇区保护。通过这些功能，可以捕获到各种威胁，包括未知威胁（例如上面所说的这两个脚本）、无文件威胁（例如这里的Payload）以及其他恶意软件。



## 二、通用无文件检测技术

上面所说的两个混淆后的脚本，是Windows Defender ATP反病毒功能在野外成功检测并阻止的真实恶意软件。在去掉第一层混淆后，我们得到了一段代码，尽管其中部分仍然经过了混淆，但其中显示了一些与无文件恶意软件技术相关的函数，称为Sharpshooter。2017年，我们监测到Sharpshooter技术，并在MDSec上公布（ [https://www.mdsec.co.uk/2018/03/payload-generation-using-sharpshooter/](https://www.mdsec.co.uk/2018/03/payload-generation-using-sharpshooter/) ）。此后不久，就发现了这两个脚本，它们是同一个恶意软件的变种。

Sharpshooter技术允许攻击者使用脚本，直接从内存执行.NET二进制文件，而无需保存在磁盘上。该技术提供了一个框架，可以使攻击者轻松地在脚本中重新打包相同的二进制Payload。正如这两个样本，使用Sharpshooter技术的文件可以用于社会工程学攻击，从而诱导用户运行承载了无文件Payload的脚本。<br>
install_flash_player.js中混淆后的代码如下：<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig1-800x319.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig1-800x319.png)去混淆后，我们发现脚本中包含了使用Sharpshooter技术的痕迹：<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig2-800x121.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig2-800x121.png)在Sharpshooter技术公开之后，我们清楚该技术只是用于攻击发生之前的一段时间。为了保护用户免受此类攻击，我们基于运行时活动，实现了一个检测算法。换而言之，该检测方式是针对Sharpshooter技术本身，因此可以抵御使用该技术的新型威胁和未知威胁。这就是Windows Defender ATP发现并阻止了这两个恶意脚本的方法，最终防止无文件Payload被加载。

检测算法利用脚本引擎对AMSI的支持，将通用的恶意行为（恶意无文件技术的指纹）作为检测目标。脚本引擎在运行时能够记录脚本调用的API，这一API日志记录是动态的，因此不会受到混淆处理的影响。脚本可以隐藏它的代码，但不能隐藏它的行为。然后，当调用某些危险的API（也就是检测过程中的触发器），反病毒解决方案就可以通过AMSI扫描日志。<br>
这是脚本生成的动态日志，由Windows Defender ATP在运行时通过AMSI检测到：<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig3-800x276.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig3-800x276.png)使用AMSI辅助检测，Windows Defender ATP在2018年6月期间，有效阻止了两个不同恶意软件的活动，同时能保证日常监测的稳定。<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/fileless-Sharpshooter-4-800x292.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/fileless-Sharpshooter-4-800x292.png)此外，借助Sharpshooter技术，我们还发现了一种非常复杂的攻击。Windows Defender ATP的终端检测响应（EDR）功能捕获到了使用Sharpshooter技术的VBScript文件。<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig5-800x400.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig5-800x400.png)我们对脚本进行了分析，并成功提取无文件Payload，这是一个非常隐秘的.NET可执行文件。恶意软件Payload通过DNS查询的TXT记录，从其命令和控制（C&amp;C）服务器下载数据。

其中，它还会下载解码恶意软件核心功能的初始化向量和解密密钥。恶意软件的核心功能也是无文件的，它会直接在内存中执行，不会向磁盘写入任何内容。因此，这次攻击包含两个无文件阶段。

下图是恶意软件核心组件解密后的代码，这部分代码会在内存中执行：<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig6-800x238.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig6-800x238.png)针对这一起恶意软件攻击事件，我们获得了充分的证据，并进行了分析。最终的结论是，这可能是一次渗透测试，或者是运行实际恶意软件的尝试，并不是有针对性的攻击行为。

尽管如此，使用无文件技术以及将网络通信隐藏在DNS查询之中的这两点特性，使得这种恶意软件本质上类似于复杂的真实攻击。同时，它还证明了Windows Defender ATP动态防护功能的有效性。

在之前的文章（ [https://cloudblogs.microsoft.com/microsoftsecure/2017/12/04/windows-defender-atp-machine-learning-and-amsi-unearthing-script-based-attacks-that-live-off-the-land/](https://cloudblogs.microsoft.com/microsoftsecure/2017/12/04/windows-defender-atp-machine-learning-and-amsi-unearthing-script-based-attacks-that-live-off-the-land/) ）中，我们已经分析了这些功能是如何抵御KRYPTON攻击和其他一些高级恶意软件的。



## 三、无文件攻击的发展趋势

消除对文件的需求，是攻击者的下一个努力目标。目前，反病毒解决方案在检测恶意可执行文件的领域已经非常有效。通过实时保护功能，每个磁盘上新增的文件都能被及时地检测。此外，文件活动也留下了取证分析所需要的痕迹。正因如此，为了防范现有的检测和取证手段，越来越多的恶意软件都在致力于采用无文件的攻击方式。

站在更高的一个位置，无文件恶意软件直接在内存中运行其Payload，而无需将可执行文件首先投放在磁盘上。这与传统恶意软件不同，传统恶意软件的Payload总是需要一些初始可执行文件或DLL来执行其任务。一个常见的例子就是Kovter恶意软件，它将可执行的Payload完全存储在注册表项之中。无文件让攻击者改变了不得不依赖于物理文件的限制，并且能有效增强隐蔽性和持久性。<br>
对于攻击者来说，如何能进行一次无文件攻击是一个挑战。一个问题就是，如果没有文件，那么如何来执行代码？实际上，攻击者通过感染其他组件的方式找到了这个问题的答案，恶意内容可以在其他组件的环境中实现执行，这些组件通常是合法的工具，默认情况下就存在于计算机上，它们的功能可以被滥用，以完成恶意操作。

这样的技术通常被称为“living off the land”，因为恶意软件仅使用了操作系统中已有的资源。一个例子是Trojan:Win32/Holiks.A恶意软件对mshta.exe工具的滥用：<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig7-768x141.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig7-768x141.png)恶意脚本仅驻留在命令行中，它从注册表项加载并执行后续代码部分。整个执行过程，都发生在mshta.exe的上下文中。该进程是一个正常的可执行文件，并且通常被视为是操作系统中的合法组件。除此之外，其他类似的工具，例如cmstp.exe、regsvr32.exe、powershell.exe、odbcconf.exe和rundll3.exe，都在被攻击者滥用。当然，并不仅仅局限于脚本，这些工具可能也允许执行DLL和可执行文件，甚至在某些情况下，会允许从远程位置执行。

通过“Living off the land”，无文件恶意软件可以掩盖它的行踪，因为反病毒软件没有可以扫描的文件，只会将恶意软件所处的位置视为合法的进程。而Windows Defender ATP通过监视系统中的异常行为，或监视是否存在已知合法工具被恶意软件所使用的特有模式，来突破这一挑战。例如，识别为Trojan:Win32/Powemet.A!attk的恶意软件检测就是一种基于行为的通用检测方式，旨在防止利用regsvr32.exe工具进行恶意脚本的攻击。<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/fileless-Powermet-4-768x570.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/fileless-Powermet-4-768x570.png)



## 四、无文件的本质

所谓“无文件”，表示不存在于文件中的威胁，例如仅存在于计算机内存中的后门。但是，这一定义还没有被普遍接受。这一名词正在被广泛使用，有时还被用于描述依赖文件操作的恶意软件。在Sharpshooter示例中，尽管Payload本身是无文件的，担起入口点依赖于需要在目标计算机上投放并执行的脚本，但这也被称之为无文件攻击。

考虑到一条完整的攻击链包括执行、持久化、信息窃取、横向移动、与C&amp;C的通信等多个阶段，而在攻击链中的某个部分可能是无文件的，而其他部分可能涉及到某种形式的文件系统。<br>
为了对这个名词进行更好的区分，我们将无文件威胁分为下面几个不同的类别。<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/taxonomy-fileless-threats.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/taxonomy-fileless-threats.png)我们可以通过它们的入口点（即执行和注入、漏洞利用、硬件）、入口点的形式（例如文件、脚本等）和感染源（例如Flash、Java、文档等）对无文件威胁进行分类。<br>
根据上述分类原则，我们可以根据威胁在被感染主机上留下痕迹的多少，来将无文件威胁分为三类。

类型I：没有进行任何文件活动。完全无文件的恶意软件永远不会在磁盘上写入文件。<br>
类型II：没有将文件写入磁盘，但间接地使用了一些文件。恶意软件还可以通过其他方式在计算机上以无文件的方式存在，不直接在文件系统中写入，但有可能会间接使用文件。<br>
类型III：为了实现无文件的持久性，需要一些文件。某些恶意软件可以具有无文件持久性，但运行是需要依赖于文件的。

在描述了大类之后，接下来我们就能够深入了解细节，并对被感染主机进行详细的划分。有了全面的分类，我们才能够覆盖无文件恶意软件的全景，从而有助于我们研究和开发新的保护功能。这些新功能可以缓解攻击，并确保恶意软件不会占据上风。

1、漏洞利用方式：<br>
（1）基于文件（类型III，可执行文件、Flash、Java、文档）；<br>
（2）基于网络（类型I）；<br>
2、硬件：<br>
（1）基于设备（类型I，网卡、硬盘）；<br>
（2）基于CPU（类型I）；<br>
（3）基于USB（类型I）；<br>
（4）基于BIOS（类型I）；<br>
（5）基于管理程序（类型I）；<br>
3、执行或注入：<br>
（1）基于文件（类型III，可执行文件、DLL、链接文件、计划任务）；<br>
（2）基于宏（类型III，Office文档）；<br>
（3）基于脚本（类型II，文件、服务、注册表、WMI库、Shell）；<br>
（4）基于磁盘（类型II，引导记录）。

有关这些类别的详细说明和示例，请参考：[https://docs.microsoft.com/en-us/windows/security/threat-protection/intelligence/fileless-threats](https://docs.microsoft.com/en-us/windows/security/threat-protection/intelligence/fileless-threats) 。



## 五、使用下一代防护击败无文件恶意软件

基于文件的检测方式无法防范无文件恶意软件，因此Windows Defender ATP中的反病毒功能使用了基于动态行为的防御层，并与其他Windows的技术相结合，从而在运行时实现对威胁活动的检测与终止。

Windows Defender ATP的下一代动态防御能有效保护用户免受无文件恶意软件日益复杂的攻击。在此前的文章（ [https://cloudblogs.microsoft.com/microsoftsecure/2018/01/24/now-you-see-me-exposing-fileless-malware/](https://cloudblogs.microsoft.com/microsoftsecure/2018/01/24/now-you-see-me-exposing-fileless-malware/) ）中，我们曾经介绍了一些与无文件攻击相关的攻防技术以及解决方案。我们以基于文件的扫描方法作为模型，不断演变，最终形成了基于行为的检测模型，实现对通用恶意行为的检测，从而彻底消除攻击。

### <a class="reference-link" name="5.1%20AMSI"></a>5.1 AMSI

反恶意软件扫描接口（AMSI）是一个开放的框架，应用程序可以使用它来请求对任何数据进行反病毒扫描。Windows在JavaScript、VBScript和PowerShell中广泛使用了AMSI。此外，Office 365客户端也集成了AMSI，使得防病毒软件和其他安全解决方案能在运行过程中对宏及其他脚本进行扫描，从而检查恶意行为。在上面的例子中，我们已经展现了AMSI是如何成为防御无文件恶意软件的强大武器的。

Windows Defender ATP整合了AMSI，并使用AMSI的告警信息进行防护，这些告警信息对于混淆后的恶意代码非常有效，能够阻止例如Nemucod这样的恶意软件活动。在最近的一次分析中，我们偶然发现了一些经过严重混淆的恶意脚本。我们收集了三个不包含已有静态恶意签名的样本，它们是一些几乎无法识别的脚本代码和二进制的垃圾数据。<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig11-800x703.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig11-800x703.png)然而，在人工反混淆之后，我们看到这些样本解码后与一个已知的Downloader代码完全相同，是同一个.js 脚本的Payload：<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig12.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig12.png)

其Payload没有进行任何混淆，非常容易被检测到，但由于它没有存储到磁盘上，因此可以逃避基于文件的检测。但是，脚本引擎能够拦截Payload执行解码的这一过程，并确保Payload能通过AMSI传递给已安装的反病毒软件进行检查。Windows Defender ATP能够发现真实的Payload，因为它会在运行过程中进行解码，从而可以轻松识别已知的恶意软件模式，并在攻击造成任何损害之前及时阻止攻击。

我们并没有根据样本中混淆的规律来编写通用检测算法，而是根据行为日志去训练ML模型，并编写启发式检测以通过AMSI捕获到解密后的脚本。结果证明是有效的，在两个月的时间内，我们捕获到大量新型变种和未知变种，保护近两千台主机，而传统的检测方法往往不会那么有效。<br>
通过AMSI 捕获的Nemucod.JAC攻击活动：<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/fileless-NemucodJAC-4-800x292.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/fileless-NemucodJAC-4-800x292.png)

### <a class="reference-link" name="5.2%20%E8%A1%8C%E4%B8%BA%E7%9B%91%E6%8E%A7"></a>5.2 行为监控

Windows Defender ATP的行为监控引擎为无文件恶意软件提供了额外的检测方式。行为监控引擎会过滤出可疑的API调用。然后，检测算法可以将使用特定API序列的动态行为与特定参数进行匹配，从而阻止发生已知恶意行为的进程。行为监控不仅仅适用于无文件恶意软件，也适用于传统的恶意软件，原因在于其相同的恶意代码库不断被重新打包、重新加密和重新混淆。

事实证明，行为监控有效阻止了通过DoublePulsar后门分发的WannaCry，这一恶意软件可归类为第I类无文件恶意软件。尽管WannaCry二进制文件的几个变种都是在大规模攻击中发布的，但勒索软件的行为还是保持不变，因此Windows Defender ATP反病毒功能也可以对新版本的勒索软件进行阻止。

行为监控对于“Living off the land”的无文件攻击非常有效。Meterpreter的PowerShell反向TCP Payload就是一个例子，它可以在命令行上运行，并且能够为攻击者提供PowerShell会话方式。<br>
Meterpreter可能生成的命令行：<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig14-768x110.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig14-768x110.png)针对这个攻击，我们无法扫描文件，但通过行为监控，Windows Defender ATP可以通过恶意软件所需的特定命令行来监测PowerShell进程，并阻止此类攻击。<br>
检测PowerShell反向TCP Payload的情况：<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/fileless-PowerShell-4-800x292.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/fileless-PowerShell-4-800x292.png)

除了按照进程查看事件之外，行为监控功能还可以跨多个进程聚合事件。即使它们通过从一个进程到另一个进程的代码注入（不仅仅是父子进程）之类的技术实现连接，该功能也可以成功检测到。此外，它可以保持并协调不同组件之间的安全信号共享（例如终端检测和响应），并通过分层防御的其他机制触发保护。

跨多个进程的行为监控，不仅仅能有效防御无文件恶意软件，它也是通常用来捕获攻击技术的工具。举例来说，Pyordono.A是基于多进程事件的检测，目的在于阻止尝试执行cmd.exe或powershell.exe的脚本引擎（JavaScript、VBScript、Office宏）带有可疑参数。Windows Defender ATP的这一算法可保护用户免受多个恶意活动的影响。<br>
Pyordono.A在野外检测的统计数据：<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/fileless-Pyordono-4-800x292.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/fileless-Pyordono-4-800x292.png)近期，我们发现Pyordono.A的检测数量突然增加，达到了高于平均值的水平。针对这一情况，我们开展了调查，最终发现一个影响范围广泛的恶意活动，该恶意活动在9月8日到9月12日期间，针对意大利的用户，使用了恶意Excel进行攻击。<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig16-800x690.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig16-800x690.png)该文档中包含恶意宏，并使用社会工程学诱骗潜在的受害者来运行恶意代码。需要强调的是，近期我们在Office 365客户端集成了AMSI，使得反病毒解决方案能在运行时扫描宏，从而发现文档中的恶意内容。

经过混淆后的宏代码尝试运行经过混淆后的cmd命令，该命令会运行经过混淆后的PowerShell脚本，最后投放Ursnif木马。<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_figx-800x387.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_figx-800x387.png)其中，宏使用了混淆处理来执行cmd命令，该命令的内容也被混淆。在cmd命令执行PowerShell脚本后，该脚本会依次下载数据，并传递Payload，向Ursnif进行信息传输。通过多进程行为监控，我们使用通用检测算法成功检测并阻止了针对意大利用户的新型恶意活动。

### <a class="reference-link" name="5.3%20%E5%86%85%E5%AD%98%E6%89%AB%E6%8F%8F"></a>5.3 内存扫描

Windows Defender ATP中的反病毒功能还使用内存扫描来检测正在运行的进程其内存中是否存在恶意代码。即使恶意软件可以在不使用物理文件的情况下运行，它也需要驻留在内存中才能运行，因此可以通过对内存进行扫描来实现对恶意文件的检测。

举例来说，根据报道，GandCrab已经属于无文件威胁。其Payload DLL是以字符串形式编码，然后通过PowerShell进行动态解码和运行。DLL文件本身不会在磁盘中保存。通过内存扫描，我们可以扫描到正在运行进程的内存，从而检查到有DLL正在隐蔽运行的勒索软件常用模式。

正是由于内存扫描、行为监控以及其他动态防御方式的结合，才帮助我们击败了Dofoil的大规模恶意活动。Dofoil是一个令人讨厌的Downloader，它使用了一些复杂的技术来逃避检测，例如进程镂空（Process Hollowing, [https://attack.mitre.org/wiki/Technique/T1093](https://attack.mitre.org/wiki/Technique/T1093) ），这样一来就允许恶意软件在合法进程（例如explorer.exe）的上下文中执行。直到现在，内存扫描还能检测到Dofoil的活动。

针对Dofoil Payload的检测：<br>[![](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/fileless-Dofoil-4-800x291.png)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/fileless-Dofoil-4-800x291.png)<br>
内存扫描是一个多功能的工具，当在运行过程中发现可疑API或可疑行为时，Windows Defender ATP的反病毒功能会在关键位置触发内存扫描，从而提升发现解码后Payload的可能性，并且这一发现的时间点往往是在恶意软件开始运行之前。每天，内存扫描这一功能都在保护数千台主机免受Mimilkatz和WannaCry等恶意软件的威胁。

### <a class="reference-link" name="5.4%20%E5%BC%95%E5%AF%BC%E6%89%87%E5%8C%BA%E4%BF%9D%E6%8A%A4"></a>5.4 引导扇区保护

通过Windows 10“受控文件夹访问”（Controlled Folder Access），Windows Defender ATP不允许对引导扇区进行写入操作，从而防止了Petty、BadRabbit和Bootkits使用的危险无文件攻击方式。引导感染技术适用于无文件威胁，因为它们可以允许恶意软件驻留在文件系统之外，并在加载操作系统之前获得对主机的控制。

使用Rootkit技术，可以使恶意软件具有相当高的隐蔽性，并且极难检测和删除。通过受控文件夹访问技术，可以有效减少攻击面，从而将这一整套感染技术彻底拒之门外。<br>
受控文件夹访问能阻止Petya对引导扇区的感染：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cloudblogs.microsoft.com/uploads/prod/sites/13/2018/09/OutOfSight_fig17-800x172.png)

### <a class="reference-link" name="5.5%20Windows%2010%E7%9A%84S%E6%A8%A1%E5%BC%8F%EF%BC%9A%E8%87%AA%E8%BA%AB%E5%8F%AF%E4%BB%A5%E9%98%B2%E8%8C%83%E6%97%A0%E6%96%87%E4%BB%B6%E6%94%BB%E5%87%BB"></a>5.5 Windows 10的S模式：自身可以防范无文件攻击

在S模式下的Windows 10自带一组预先配置好的限制和策略，可以保护系统免受绝大多数无文件技术（通常是恶意软件）的攻击。在其启用的安全功能中，以下功能对于无文件威胁非常有效：

1、针对可执行文件：仅允许Microsoft Store中经过Microsoft验证的应用程序运行。此外，Device Guard提供用户模式代码完整性（UMCI）以防止加载未经签名的二进制文件。<br>
2、针对脚本：不允许运行脚本引擎（包括JavaScript、VBScript和PowerShell）。<br>
3、针对宏：Office 365不允许在来自Internet的文档中执行宏（例如在组织外部的电子邮件附件中下载的文档）。<br>
4、针对漏洞利用：Windows 10在S模式下也可以使用漏洞利用保护和攻击面减少规则。

有了上述这些限制，S模式下的Windows 10已经具有强大的保护，能够消除无文件恶意软件所使用的关键攻击向量。



## 六、总结

随着反病毒解决方案不断提升对恶意文件的检测率，恶意软件如今自然在朝着使用尽可能少的文件这一方向去发展。尽管在过去几年，无文件技术只用于复杂的网络攻击，但随着技术的提升，近期它们也普遍出现在普通的恶意软件中。

Microsoft针对目前安全现状，积极监控态势，同时开发各种保证Windows安全性并能够减轻威胁的解决方案。采用了通用的检测方法，能够有效抵御各种威胁。此外，通过AMSI、行为监控、内存扫描和引导扇区保护，甚至可以检查经过严重混淆后的威胁。通过云平台上机器学习技术，能够及时针对新出现的威胁实现防护能力的扩展。
