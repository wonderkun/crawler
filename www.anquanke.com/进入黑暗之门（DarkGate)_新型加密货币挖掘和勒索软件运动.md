> 原文链接: https://www.anquanke.com//post/id/164674 


# 进入黑暗之门（DarkGate)：新型加密货币挖掘和勒索软件运动


                                阅读量   
                                **168664**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Ensilo，文章来源：ensilo.com
                                <br>原文地址：[https://blog.ensilo.com/darkgate-malware](https://blog.ensilo.com/darkgate-malware)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/dm/1024_576_/t01546fa10cfbad9716.jpg)](https://p5.ssl.qhimg.com/dm/1024_576_/t01546fa10cfbad9716.jpg)

一场活跃且隐秘的加密货币挖掘和勒索软件活动正在感染西班牙和法国的目标用户，该软件利用多种绕过技术来逃避传统AV的检测。

## 恶意软件活动概要

最近，enSilo研究员Adi Zeligson发现了一个名为DarkGate的，从未被侦测到过且高度复杂的恶意软件活动。DarkGate恶意软件针对Windows工作站并由反应式命令和控制系统提供支持，该软件通过Torrent文件传播。当用户运行时，DarkGate恶意软件能够避免多个AV产品的检测并执行多个有效负载，包括加密货币挖掘，加密窃取，[勒索软件](https://www.ensilo.com/faq/ransomware-faq)以及远程控制端点的能力。

DarkGate恶意软件的关键元素如下：
- 利用隐藏在包括Akamai CDN和AWS在内的合法服务的合法DNS记录中的C＆C基础架构，帮助其避免基于信誉的检测技术。
- 使用多种方法绕过传统AV具有厂商特性的检查规则和操作（包括使用process hollowing技术）。
- 能够通过几种已知的恢复工具来避免关键文件被查杀。
- 使用两种不同的用户帐户控制（UAC）绕过技术来提权。
- 能够触发多个有效载荷，其功能包括加密货币挖掘，加密窃取（盗窃与加密钱包相关的凭证），勒索软件和远程控制。
下面对DarkGate恶意软件的技术分析演示了高级恶意软件如何避免传统AV产品的检测，并强调了[enSilo端点安全平台](https://www.ensilo.com/product/)的感染后保护功能的重要性。



## 技术分析

恶意软件被作者命名为DarkGate，其旨在感染整个欧洲的受害者目标，特别是在西班牙和法国。DarkGate具有多种功能，包括加密挖掘，窃取加密钱包凭证（加密窃取），勒索软件和远程访问及控制。

enSilo观察到，这个恶意软件背后的作者建立了一个反应性的命令和控制基础设施，由人工操作员配备，他们根据收到的加密钱包的新感染通知采取行动。当操作员通过其中一个恶意软件检测到任何有趣的活动时，他们会去在机器上安装自定义远程访问工具以进行手动操作。

作为我们正常研究活动的一部分，我们偶尔会对看似合法的用户端点进行受控感染。进行受控感染是为了研究恶意软件的几个方面，以及恶意软件操作员的反应性。例如，在一次不期而遇的碰撞中，我们的[研究团队](https://www.ensilo.com/services/)能够确定操作员检测到了我们的活动，并通过使用定制的勒索软件感染测试机器，从而立即做出响应。

看来，这个恶意软件背后的作者投入了大量的时间和精力，通过利用多种逃避技术来保持不被发现。使用的技术之一是用户模式挂钩绕过，这使得恶意软件能够在很长一段时间内逃避各种AV解决方案的识别。

enSilo研究团队追踪“DarkGate”及其变种，并发现大多数AV供应商未能检测到它。正是这一发现促使我们开始研究技术分析部分中描述的恶意软件的独特特征。很明显，DarkGate正在不断发展，因为它正在通过每个新变体进行改进。

我们还需要进一步调查以确定恶意软件背后的最终动机。虽然加密货币挖掘，加密窃取和勒索软件功能表明该软件的目标是获取经济利益，但目前尚不清楚作者是否有另一个动机。



## 家族纽带

在DarkGate中，我们能够识别其与之前检测到的名为[Golroted](https://www.bankinfosecurity.asia/cert-in-warns-info-stealing-trojan-a-8444)的密码窃取程序恶意软件的关系。Golroted恶意软件因其使用Nt * API调用来执行process hollowing而引人注目。此外，Golroted使用第二种技术—UAC绕过，基于称为SilentCleanup的计划任务。而DarkGate都用到了这两种技术。

在Golroted和DarkGate之间进行二进制差异比较后，我们发现了大量重叠代码。如图1所示，两个恶意软件变体都在进程vbc.exe上执行process hollowing方法。但是，DarkGate包含一个稍微修改过的process hollowing函数版本。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/image12.png?t=1542570764041&amp;width=960&amp;name=image12.png)

图1 GOLRATED和DARKGATE间的二进制差异



## 感染策略和方法

我们辨别出了DarkGate作者以及Golroted作者都使用了的两种不同的感染方法。这两种感染方法都是通过Torrent文件传播的，这些文件是一部受欢迎的电影和一部会在受害者机器上执行VBscript的电视连续剧。

第二个文件，the-walking-dead-9-5-hdtv-720p.torrent.vbe，使用一种更为琐碎的方法来感染受害者。它从具有欺骗性的地址来分发包含恶意附件的电子邮件。其示例如图3所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/Fig%202%20.png?t=1542570764041&amp;width=793&amp;name=Fig%202%20.png)

图2 种子文件的截屏

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/figure%203%20.png?t=1542570764041&amp;width=895&amp;name=figure%203%20.png)

图3 通过the-walking-dead-9-5-hdtv-720p.torrent.vbe分发的邮件示例



## 解开DARKGATE恶意软件的四个阶段

DarkGate恶意软件使用的独特技术之一在于其多阶段解包方法。被执行的第一个文件是一个混淆过的VBScript文件，它起到一个dropper的作用并执行多个操作。在第一阶段，几个文件被放入隐藏文件夹“C： `{`username`}`”。这些文件是autoit3.exe，在某些版本中伪装成随机名称test.au3，pe.bin和shell.txt。接下来，使用放入的autoit3.exe实例来执行test.au3 AutoIt脚本。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/figure%204-8.png?t=1542570764041&amp;width=974&amp;name=figure%204-8.png)

图4 去混淆的VBS

在第二阶段，AutoIt代码在startup文件夹下创建名称为“bill.ink”的其自身的快捷方式。一旦完成，它将触发第三阶段，其中存储在文件“C： `{`username`}` shell.txt”中的二进制代码将被解密并得到执行。AutoIt脚本使用一种相当不寻常的技术来执行二进制代码。该技术涉及的步骤是：
- 将二进制代码从shell.txt加载到进程内存中。
- 将数据复制到可执行的内存空间（DLLStructCreate和DllStructSetData）。
- 调用CallWindowProc并引用我们的二进制代码作为lpPrevWndFunc参数。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/image8.jpg?t=1542570764041&amp;width=1302&amp;name=image8.jpg)

图5 去混淆的AUTOIT脚本

最后，在解包技术的第四个也是最后一个阶段，最初从shell.txt加载的二进制代码执行以下操作：
- 搜索可执行文件，该文件也是Kaspersky AV中可执行文件的名称。
- 读取放入的文件“pe.bin”并解密它。
- 使用[process hollowing](https://attack.mitre.org/techniques/T1093/)技术，将pe.bin解密后的代码注入进程“vbc.exe”。
我们发现，如果DarkGate检测到卡巴斯基AV的存在，它会将恶意软件作为shellcode的一部分加载，而不是使用process hollowing方法。解密的pe.bin文件是DarkGate的核心。核心负责与C＆C（命令和控制）服务器的通信以及执行从其接收的命令。

让我们总结一下这个分为四阶段的拆包技术

1.使用VBScript提供初始dropper代码，将所有相关文件写入受害者的机器：
- autoit3.exe
- test.au3
- pe.bin
- shell.txt
一旦完成，然后就开始运行AutoIt脚本。

2.AutoIt脚本使用AutoIt解释器运行，解释器解密二进制代码并将其加载到内存中。

3.然后二进制代码得到执行，并尝试避免卡巴斯基AV的检测。

4.最后的二进制文件被解密并执行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/image11.png?t=1542570764041&amp;width=900&amp;name=image11.png)

图6 解包技术的四个阶段

最终的二进制文件将所有文件从“C:`{`computer_name`}`”复制到“C:Program data”下的新文件夹，文件夹的名称是用户生成的id的前八位数字（ID2 – 稍后解释）。

最终的二进制文件在注册表中安装了一个键，从而使得该文件在键值“SOFTWAREMicrosoftWindowsCurrentVersionRun”的帮助下保持持久性：。

键的名称是用户生成id的前八位，值是从C:`{`computer_name`}`复制到“program data”文件夹的AutoIt脚本，如下面的图7所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/figure7.png?t=1542570764041&amp;width=974&amp;name=figure7.png)

图7 用于建立持久性的注册键值示例



## 加密货币挖掘

恶意软件与C＆C服务器建立的第一个连接的目的就是获取启动加密货币挖掘进程所需的文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/image13.png?t=1542570764041&amp;width=800&amp;name=image13.png)

图8 检索文件

如图9所示，指令“startminer”作为响应的一部分被发送，以告知恶意软件开始挖掘并分离消息的不同部分。第一部分被加密写入config.bin-该部分是矿工命令行。第二部分被写入cpu.bin，当解密时是矿工可执行文件。挖掘本身是借助process hollowing技术，通过“systeminfo.exe”进程完成的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/figure%2012.png?t=1542570764041&amp;width=949&amp;name=figure%2012.png)

图9 检索加密矿工payload



## 窃取加密钱包凭据

恶意软件的另一个功能是它可以搜索和窃取加密钱包的凭据。恶意软件在前台窗口的名称中查找与不同类型的加密钱包相关的特定字符串，如果找到匹配的字符串，则向服务器发送适当的消息。

下表包含目标钱包网站/应用程序的列表：

|搜索的字符串|目标
|------
|sign-in / hitbtc|[https://hitbtc.com/](https://hitbtc.com/)
|binance – log in|[https://www.binance.com/login.html](https://www.binance.com/login.html)
|litebit.eu – login|[https://www.litebit.eu/en/login](https://www.litebit.eu/en/login)
|binance – iniciar sesi|[https://www.binance.com/login.html](https://www.binance.com/login.html)
|cryptopia – login|[https://www.cryptopia.co.nz/Login](https://www.cryptopia.co.nz/Login)
|user login – zb spot exchange|
|sign in | coinEx|[https://www.coinex.com/account/signin?lang=en_US](https://www.coinex.com/account/signin?lang=en_US)
|electrum|[https://electrum.org/#home](https://electrum.org/#home)
|bittrex.com – input|[https://international.bittrex.com/](https://international.bittrex.com/)
|exchange – balances|
|eth) – log in|
|blockchain wallet|[https://www.blockchain.com/wallet](https://www.blockchain.com/wallet)
|bitcoin core|[https://bitcoincore.org/](https://bitcoincore.org/)
|kucoin|[https://www.kucoin.com/#/](https://www.kucoin.com/#/)
|metamask|[https://metamask.io/](https://metamask.io/)
|factores-Binance|
|litecoin core|[https://litecoin.org/](https://litecoin.org/)
|myether|[https://www.myetherwallet.com/](https://www.myetherwallet.com/)

表一：目标加密钱包和字符串值



## 命令与控制

从目前为止看到的情况来看，似乎DarkGate的作者利用了复杂的技术来避免端点和网络安全产品的检测。<br>
该恶意软件包含六个硬编码域，如下所示，它将在感染时尝试与之通信。看起来域名是谨慎选择出来的，以将C＆C服务器伪装成Akamai CDN或AWS等已知合法服务，并避免使得可能正在监控网络流量的任何人产生怀疑。
- akamai.la
- hardwarenet.cc
- ec2-14-122-45-127.compute-1.amazonaws.cdnprivate.tel
- awsamazon.cc
- battlenet.la
- a40-77-229-13.deploy.static.akamaitechnologies.pw
此外，似乎作者采用了另一种技巧，使用看起来像来自Akamai或亚马逊的合法rDNS记录的NS记录。使用rDNS背后的想法是，任何监控网络流量的人都会忽略并且不对它们做处理。



## 避免检测的两种方法

看起来DarkGate的作者最担心的是AV软件的检测。他们在反VM和用户验证技术方面投入了大量精力，而不是反调试措施方面。



## 反VM：机器资源检查

DarkGate用来避免AV软件检测的第一种方法判定恶意软件是否已落入沙箱/虚拟机内。基于所使用的策略，我们认为作者假设沙箱/虚拟机（VMs）通常资源较少，这通常是正确的，因为沙箱通常会经过优化以包含尽可能多的VM。

在图10中，我们可以看到使用Delphi的Sysutils :: DiskSize和GlobalMemoryStatusEx来收集磁盘大小和物理内存。如果机器包含的磁盘空间少于101GB或者等于4GB RAM，则将其视为VM，恶意软件将自动终止。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/figure9.png?t=1542570764041&amp;width=974&amp;name=figure9.png)

图10 检查机器硬盘和内存



## 反-AV

DarkGate会尝试检测表2中列出的任何AV解决方案是否存在于受感染的计算机上。对于大多数AV解决方案，如果恶意软件检测到任何的这些AV解决方案，它只会通知服务器，但对卡巴斯基，Trend Micro和IOBIt除外。

|进程名称|解决方案
|------
|astui.exe|Avast
|avpui.exe|Kaspersky
|avgui.exe|AVG
|egui.exe|Nod32
|bdagent|Bitdefender
|avguard.exe|Avira
|nis.exe|Norton
|ns.exe|Norton
|nortonsecurity.exe|Norton
|uiseagnt.exe|Trend Micro
|bytefence.exe|ByteFence
|psuaconsole.exe|Panda
|sdscan.exe|Search &amp; Destroy
|mcshield.exe|McAfee
|mcuicnt.exe|McAfee
|mpcmdrun.exe|Windows Defender
|superantispyware.exe|SUPER AntiSpyware
|vkise.exe|Comodo
|mbam.exe|MalwareBytes
|cis.exe|Comodo
|msascuil.exe|Windows Defender

表2 DARKGATE恶意软件搜索的AV可执行文件

卡巴斯基，IOBit或TrendMicro存在AV解决方案会触发特殊情况：
- IOBit：如果路径“C:Program Files(x86)IObit”存在，恶意软件将尝试通过终止它来处理名为“monitor.exe”的进程。此外，它将生成一个新线程，该线程将重复查找进程“smBootTime.exe”并终止它（如果存在）。
- Trend Micro：如果检测到Trend Micro的AV进程名称，则代码将不会执行键盘记录线程。
<li>卡巴斯基：恶意软件在执行期间会进行多次检查，无论是在解包过程中还是在恶意软件本身，都会对卡巴斯基AV是否存在进行检测。
<ul>
<li>如果在最终的可执行文件中检测到卡巴斯基AV且机器启动时间不到5分钟，那么它将不会启动键盘记录线程和负责以下内容的更新线程：
<ul>
- 将所有与恶意软件相关的文件复制到“C:Program Data”下的文件夹中。
- 执行下一节将描述的恢复工具检查。


## 恢复工具

恶意软件还尝试使用表3中列出的进程名称检测多个已知的恢复工具：

|进程名|目标
|------
|adwcleaner.exe|MalwareBytes Adwcleaner
|frst64.exe|Farbar Recovery Scan Tool
|frst32.exe|Farbar Recovery Scan Tool
|frst86.exe|Farbar Recovery Scan Tool

表3：恢复工具进程名和目标

如果发现此类进程，恶意软件将启动一个新线程，该线程将每20秒重新分配生成恶意软件文件，确保如果文件在恢复工具的生命周期内被删除，则将重新创建并重新定位到其他位置。



## 直接的SYSCALL调用

为了隐藏process hollowing技术的使用，DarkGate使用了一种特殊功能，使其能够直接调用内核模式下的函数。这可以潜在地帮助恶意软件逃避调试器设置的任何断点，以及避免由不同安全产品设置的用户区挂钩。



## 它是如何工作的？

使用ntdll.dll中的函数时，会对内核进行系统调用。调用的方式在32位和64位系统之间是不同的，但它们最终都调用了在两个体系结构之间不同的函数“KiFastSystemCall”。“KiFastSystemCall”函数用于在RING3和RING0之间切换。Darkgate恶意软件避免以正常的方式加载ntdll.dll函数，而是创建自己的“KiFastSystemCall”函数来进行系统调用。

DarkGate是一个32位进程，由于切换到内核时系统之间存在差异，因此在64位系统上运行时可能会遇到困难。为了在进程中使用正确的“KiFastSystemCall”函数，Darkgate恶意软件通过搜索路径“C:WindowsSysWOW64ntdll.dll”来检查它正在运行的架构。如果此路径存在，则表示该进程正在64位系统上运行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/figure%2015.png?t=1542570764041&amp;width=974&amp;name=figure%2015.png)

图11：根据体系结构分配正确的函数

在32位系统中，“KiFastSystemCall”函数将如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/figure%2016.png?t=1542570764041&amp;width=525&amp;name=figure%2016.png)

图12：32位系统下的KIFASTSYSTEMCALL函数

在64位系统中，以下代码用于从32位进程调用“KiFastSystemCall”64位函数：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/figure%2017.png?t=1542570764041&amp;width=522&amp;name=figure%2017.png)

图13：64位系统下KIFASTSYSTEMCALL函数

偏移“fs：0C0h”是wow64中TEB（线程信息块）中指向“FastSysCall”的指针。该指针指向“wow64cpu.dll”中的地址，该地址跳转到64位“KiFastSystemCall”函数。DarkGate恶意软件将ntdll请求的函数系统调用号和所需的参数传递给指定的函数。这样就可以调用内核函数，而无需从ntdll.dll中调用该函数。最后，DarkGate恶意软件创建了自己的“KiFastSystemCall”以绕过ntdll.dll。

我们发现了类似的[代码](https://cybercoding.wordpress.com/2012/12/01/union-api/)，可能是DarkGate代码的来源。



## UAC绕过功能

DarkGate使用两种不同的UAC绕过技术来尝试提升权限。

### <a name="%E7%A3%81%E7%9B%98%E6%B8%85%E7%90%86%E7%BB%95%E8%BF%87"></a>磁盘清理绕过

第一个UAC绕过技术利用名为DiskCleanup的计划任务。此计划任务使用路径%windir% system32cleanmgr.exe来执行实际的二进制文件。因此，恶意软件使用注册表项“HKEY_CURRENT_USEREnviromentwindir”来覆盖%windir%环境变量，其中包含将执行AutoIt脚本的备用命令。这个绕过过程可以参考[Tyranid的巢穴](https://tyranidslair.blogspot.com/2017/05/exploiting-environment-variables-in.html)。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/figure%2018.png?t=1542570764041&amp;width=974&amp;name=figure%2018.png)

图14：磁盘清理UAC绕过

### <a name="EVENTVWR%20UAC%E7%BB%95%E8%BF%87"></a>EVENTVWR UAC绕过

另一个UAC绕过漏洞利用eventvwr.exe默认以高完整性运行的特性，将会执行mmc.exe二进制文件（Microsoft管理控制台）。mmc.exe命令取自注册表项“HKCUSoftwareClassesmscfileshellopencommand”。此注册表项也可从较低的完整性级别写入，这使其能够以更高的完整性执行AutoIt脚本。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/figure%2019.png?t=1542570764041&amp;width=974&amp;name=figure%2019.png)

图片15：EVENTVWR UAC绕过



## 键盘记录

将会启动一个线程，负责捕获所有键盘事件并将它们记录到预定义的日志文件中。除了记录密钥日志之外，它还记录前台窗口和剪贴板。日志以下面列出的目录中的名称“current date.log”保存：

“C:\users\`{`username`}`\appdata\roaming\`{`ID1`}`”.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/image15.png?t=1542570764041&amp;width=443&amp;name=image15.png)

图16：键盘记录日志

## 信息窃取

DarkGate使用一些NirSoft工具来窃取受感染机器的凭据或信息。使用的工具集使其能够窃取用户凭据，浏览器cookie，浏览器历史记录和Skype聊天记录。所有工具都通过process hollowing技术执行到新创建的vbc.exe或regasm.exe实例中。

DarkGate使用以下应用程序来窃取凭据：
- 邮件PassView
- WebBrowserPassView
- ChromeCookiesView
- IECookiesView
- MZCookiesView
- BrowsingHistoryView
- SkypeLogView
从工具收集的结果数据是从主机进程存储器中提取的。DarkGate恶意软件首先使用FindWindow API函数查找工具的窗口。然后它使用SysListView32控件和sendMessage API函数来检索工具所需的信息。检索的工作原理是首先在图17所示的挖空的(hollowed)进程中分配一个内存缓冲区。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/figure%2020.png?t=1542570764041&amp;width=974&amp;name=figure%2020.png)

图17：在中空的(hollowed)进程中的内存分配

然后它将使用“GetItem”函数使其将项目写入分配的缓冲区。通过使用消息“LVM_GETITEMA”和分配的缓冲区作为参数，调用API函数“SendMessage”来使用“GetItem”函数：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ensilo.com/hs-fs/hubfs/figure%2021.png?t=1542570764041&amp;width=974&amp;name=figure%2021.png)

图18：GETITEM消息以及从中空的(hollowed)进程中检索项目

将项目写入分配的缓冲区后，它将读取此内存区域并获取被盗信息。



## 删除还原点

恶意软件能够删除所有还原点，包括“cmd.exe /c vssadmin delete shadows /for=c：/all /quiet”



## RDP安装

此命令将使用process hollowing方法解密并执行接收的文件，该文件可能是rdp连接工具。在这种情况下，中空(hollowed)进程是%temp%目录中的systeminfo.exe的副本。

此外，将使用cmd.exe执行以下命令：
- exe /c net user /add SafeMode Darkgate0！
- exe /c net localgroup administrators SafeMode /add
- exe /c net localgroup administradores SafeMode /add
- exe /c net localgroup administrateurs SafeMode /add
有趣的是，新创建的用户被添加到西班牙语和法语管理组。



## GETBOTDATA

服务器可以请求以下有关受害者的详细信息：
- 语言环境
- 用户名
- 电脑名称
- 窗口名称
- 自主机上次输入以来经过的时间段
- 处理器类型
- 显示适配器说明
- RAM大小
- 操作系统类型和版本
- 是否为用户管理员
- config.bin的加密内容
- 新纪元时间
- AV类型 – 按进程名称搜索，如果未找到此字段将包含文本“Unknown”。
在某些版本中 – 还会查找文件夹“c:Program Filese-Carte Bleue”（我们认为可能是DarkGate保存其屏幕截图的文件夹）。然后将数据加密并发送到服务器。此外，它在%appdata% path下创建文件Install.txt，并在其中写入新纪元时间。
- 恶意软件版本
- 连接使用的端口


## IOCS

|DOMAINS
|------
|akamai.la
|hardwarenet.cc
|ec2-14-122-45-127.compute-1.amazonaws.cdnprivate.tel
|awsamazon.cc
|battlenet.la
|a40-77-229-13.deploy.static.akamaitechnologies.pw

|SAMPLE HASHES
|------
|3340013b0f00fe0c9e99411f722f8f3f0baf9ae4f40ac78796a6d4d694b46d7b
|0c3ef20ede53efbe5eebca50171a589731a17037147102838bdb4a41c33f94e5
|3340013b0f00fe0c9e99411f722f8f3f0baf9ae4f40ac78796a6d4d694b46d7b
|0c3ef20ede53efbe5eebca50171a589731a17037147102838bdb4a41c33f94e5
|52c47a529e4ddd0778dde84b7f54e1aea326d9f8eeb4ba4961a87835a3d29866
|b0542a719c6b2fc575915e9e4c58920cf999ba5c3f5345617818a9dc14a378b4
|dadd0ec8806d506137889d7f1595b3b5447c1ea30159432b1952fa9551ecfba5
|c88eab30fa03c44b567bcb4e659a60ee0fe5d98664816c70e3b6e8d79169cbea
|2264c2f2c2d5a0d6d62c33cadb848305a8fff81cdd79c4d7560021cfb304a121
|3c68facf01aede7bcd8c2aea853324a2e6a0ec8b026d95c7f50a46d77334c2d2
|a146f84a0179124d96a707f192f4c06c07690e745cffaef521fcda9633766a44
|abc35bb943462312437f0c4275b012e8ec03899ab86d353143d92cbefedd7f9d
|908f2dfed6c122b46e946fe8839feb9218cb095f180f86c43659448e2f709fc7
|3491bc6df27858257db26b913da8c35c83a0e48cf80de701a45a30a30544706d
