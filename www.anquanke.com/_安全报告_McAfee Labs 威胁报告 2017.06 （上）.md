> 原文链接: https://www.anquanke.com//post/id/86409 


# 【安全报告】McAfee Labs 威胁报告 2017.06 （上）


                                阅读量   
                                **102972**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：mcafee.com
                                <br>原文地址：[https://www.mcafee.com/us/resources/reports/rp-quarterly-threats-jun-2017.pdf](https://www.mcafee.com/us/resources/reports/rp-quarterly-threats-jun-2017.pdf)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p4.ssl.qhimg.com/t011e88d76cdbd6fe8d.jpg)](https://p4.ssl.qhimg.com/t011e88d76cdbd6fe8d.jpg)**



译者：[ureallyloveme](http://bobao.360.cn/member/contribute?uid=2586341479)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**概要**

**恶意软件规避技术和发展趋势**

当第一款恶意软件成功将自己的代码部分加密，使内容无法被安全分析师所读取的时候，那些恶意软件开发者早在上世纪 80 年代就开始尝试如何规避安全产品了。如今，有成百上千的反安全、反沙盒、反分析的规避类技术被恶意软件作者所采用。在这的主题中，我们来研究一些最为强大的规避技术、拥有现成规避技术的大型黑市、当代的一些恶意软件家族如何利用规避技术，以及将来如何发展，也包括机器学习类的规避和基于硬件的规避。

**不识庐山真面目： 隐写术面对的隐蔽威胁**

隐写术已存在几个世纪了。从古希腊人到现代的网络攻击者，人们总在看似平常的对象中隐藏秘密消息。在数字世界里，各种消息常常隐藏在图像、音频轨道、视频剪辑或文本文件之中。攻击者使用隐写术，避开安全系统的检查来传递信息。在这的主题中，我们来探索隐写术的一个有趣领域。我们将涵盖其历史、隐藏信息的普通方法、和它在流行恶意软件中的使用、以及它在网络中的变形。最后，我们提供防止这种形式攻击的策略和程序。

**密码盗用程序”Fareit”的增长性危险**

人们、企业和政府越来越多地依赖于那些仅靠密码所保护的系统与设备。通常情况下，这些密码比较脆弱或者容易被盗，它们吸引着各种网络罪犯。在这的主题中，我们将仔细分析Fareit，这一最为著名的密码窃取类恶意程序。我们将涉及它从2011年的起源和它是如何演变至今的，包括其典型的感染载体，其体系结构、内部运作机制和盗窃行为、以及它是如何规避检测的。当然也有它在2016年美国总统选举之前的民主党全国委员会中所起到的作用。我们也提供一些规避被Fareit和其他密码盗用工具感染的实用建议。

**恶意软件的规避技术和发展趋势— —Thomas Roccia**

在过去的十年间，技术进步显著地改变了我们的生活。即使是最简单的日常任务，我们也会依靠计算机去完成。而当它们不再可用、或是不能如我们所预期的执行操作时，我们会倍感压力。而正是因为我们所创建、使用和交换的数据信息是如此的有价值连城、且经常涉及到个人隐私，因此对数据偷窃的各种尝试也正在世界各处以几何式增长着。

恶意软件最初被研发出来是作为一项技术挑战的，但攻击者很快就意识到了其对于数据窃取的价值，网络犯罪行业随即诞生。各个信息安全公司，包括 McAfee在内，很快就组建了信息保卫团队和使用反恶意软件技术的系统。作为回应，恶意软件开发者也开始了尝试如何规避各类安全产品的方法。

最初的规避技术是很简单的，因为其对应的反恶意软件产品也是同样的简单。例如，更改恶意文件中的一个字节就足以绕过安全产品的特征码检测。当然之后也发展出了更为复杂的机制，例如多态性或混淆机制。

如今恶意软件已是非常强了，它们不再是由孤立的群体或是青少年们开发出了为了证明什么，而是由某些政府、犯罪集团和黑客开发出来，用以刺探、窃取或破坏数据。

本主题将详细介绍当今最强大和常见的规避技术，并解释恶意软件作者是如何尝试着使用它们来实现其目标的。

**为什么要使用规避技术？**

为了执行恶意操作，攻击者需要创建恶意软件。然而，除非他们的尝试未被发现，否则他们无法实现目标。可见，这是一场安全供应商和攻击者之间猫和老鼠般的游戏，其中包括了攻击者对安全技术的操作和实践的监测。

”规避技术”这一术语包括了：恶意软件用来规避自身被检测、分析和解读的所有方法。

我们可以把规避技术分为三大类：

**反安全技术：**用于规避那些保护环境的工具，如反恶意软件引擎、防火墙、应用控制或其他工具的检测。

**反沙箱技术：**用于检测到自动化分析，并规避那些恶意软件行为报告的引擎。检测注册表项、文件或与虚拟环境相关的进程，让恶意软件知道自己是否正运行在沙箱之中。

**反分析技术：**用来检测和迷惑恶意软件分析师。例如，通过识别出监测类工具，如Process Explorer或Wireshark，以及一些进程监控的tricks、packers，或者使用混淆处理来规避逆向工程。

一些先进的恶意软件样本会综合采用两个或三个此类技术。例如，恶意软件可以使用RunPE（在内存中本来的进程中运行另一个进程）的技术来规避反恶意软件、沙箱或分析。一些恶意软件能检测到虚拟环境中的特殊注册表键值，以允许威胁规避自动化的沙盒,以及规避分析员试图在虚拟机中动态运行可疑的恶意二进制文件。

因此，对于安全研究人员来说，了解这些规避技术，以确保安全技术仍然可用是很重要的。

通过下图，我们来看频繁使用的几种类型的规避技术：

恶意软件使用到的规避技术

[![](https://p3.ssl.qhimg.com/t010256615f731030fe.png)](https://p3.ssl.qhimg.com/t010256615f731030fe.png)

反沙箱已更为突出，因为更多的企业正在使用沙箱来检测恶意软件。

**定义**

在网络安全躲避领域中，有许多热门的术语。这里为大家列举一些经常被攻击者所使用到的工具和术语。

**Crypters：**恶意软件在其执行过程中进行加密和解密。使用这种技术，恶意软件经常不会被反恶意软件引擎或静态分析所检测到。加密器通常可以被定制，并能在地下市场里买到。定制的加密器会使得解密或反编译更具挑战性。Aegis Crypter、Armadillo、和RDG Tejon都是先进加密器的代表。

**Packer：**类似于加密器。Packer对恶意软件文件进行压缩而非加密。UPX是一种典型的Packer。

**Binder：**将一个或多个恶意软件文件捆绑成一个。一个可执行的恶意软件可以与JPG 文件绑定，但其扩展名仍为EXE。恶意软件作者通常将恶意软件文件与合法的EXE文件相捆绑。

**Pumper：**增加文件的大小，以使恶意软件有时能够绕过反恶意软件的引擎。

**FUD：**使反恶意软件完全无法被探测。恶意软件的卖家用来 描述和推广其工具。一个成功的 FUD程序结合了scantime和runtime因素，从而达到100%不会被检测到的效果。我们当前知道有两种类型的FUD：

–	FUD scantime：在恶意软件运行之前，保护其不被反恶意引擎检测到。

–	FUD runtime：在恶意软件运行期间，保护其不被反恶意引擎检测到。

**Stub：**通常包含用于加载（解密或减压）原始的恶意文件到内存所需的例程。

**Unique stub generator：**为每个正在运行的实例创建独特的stub，以使检测和分析更为困难。

**Fileless malware：** 通过将自身插入到内存而并非向磁盘写入文件的方式来感染系统。

**Obfuscation：**使得恶意软件代码难以为人类所理解。将编码过的纯文本字符串（XOR、Base64等）插入恶意文件，或无用功能添加到该文件中。

**Junk code ：**添加无用代码或假指令到二进制文件，以迷惑反汇编视图或耗废分析时间。

**Anti’s：**有时候地下论坛或黑市,用来定义所有用于绕过、禁用、或干掉保护和监测工具的技术。

**Virtual machine packer：**一些先进的packers采用了虚拟机的概念。当恶意软件的EXE文件被打包后，原始代码被转化成虚拟机的字节代码，并会模拟处理器的行为,VMProtect和CodeVirtualizer就使用的是这种技术。

[![](https://p4.ssl.qhimg.com/t01adbdc274861853fd.png)](https://p4.ssl.qhimg.com/t01adbdc274861853fd.png)

图 1：规避软件样本。

**无需编码的规避技术**

恶意软件作者要想成功的基础是使用规避技术。网络罪犯，甚至是那些业余爱好者都能理解到这一点。所以规避技术发展出了一个既活跃又能被轻易访问到的市场。

[![](https://p3.ssl.qhimg.com/t01160e9761069ab450.png)](https://p3.ssl.qhimg.com/t01160e9761069ab450.png)

图 2：在互联网上发现的加密器工具的样本。

**规避技术的黑市**

一些卖家已经将多种规避技术编译成了一种工具，并且将它们在地下市场上出售给有经验的恶意软件创建者或是通过负责传播恶意软件来支持大型的商业活动。

[![](https://p5.ssl.qhimg.com/t01781d1df16bfbbbb1.png)](https://p5.ssl.qhimg.com/t01781d1df16bfbbbb1.png)

图 3： 规避工具有时会被低价发售。一些卖家已经从互联网上购买或偷窃了多个crypters和packers然后打包出售。

[![](https://p1.ssl.qhimg.com/t0154c8c109cf17f881.png)](https://p1.ssl.qhimg.com/t0154c8c109cf17f881.png)

图 4：其他卖家也会自己开发一些工具，并保留源代码以规避分析和检测。这些价格会因为其工具（据推测）不能被他人分销而比较昂高。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0183032a9ce1e08001.png)

图 5：有些卖家会提供生产FUD文件的服务。服务会可能因为提供商使用的是高级的代码控制、高度混淆处理或其他自定义的加密器技巧而更昂贵。

[![](https://p5.ssl.qhimg.com/t019759f47d87e2a892.png)](https://p5.ssl.qhimg.com/t019759f47d87e2a892.png)

图6：也有可能是购买一张证书来签发任何恶意软件，从而绕过操作系统的安全机制。

我们发现，如今在价格和销售服务上已发生了巨大的变化。某项服务会比那些只能提供一款容易被反恶意软件产品所检测到的编译工具，要昂贵许多。

**规避工具销售的黑市**

[![](https://p0.ssl.qhimg.com/t01eee8bca982aef766.png)](https://p0.ssl.qhimg.com/t01eee8bca982aef766.png)

[![](https://p2.ssl.qhimg.com/t014d041dd28a3f4312.png)](https://p2.ssl.qhimg.com/t014d041dd28a3f4312.png)

[![](https://p1.ssl.qhimg.com/t01c13ac7c409edb1c9.png)](https://p1.ssl.qhimg.com/t01c13ac7c409edb1c9.png)

[![](https://p4.ssl.qhimg.com/t0144f731ba037f851f.png)](https://p4.ssl.qhimg.com/t0144f731ba037f851f.png)

[![](https://p1.ssl.qhimg.com/t01b74ab84bbc869207.png)](https://p1.ssl.qhimg.com/t01b74ab84bbc869207.png)

**被有组织的犯罪分子和安全公司所利用的规避技术**

黑客组织也对规避技术感兴趣。2015年，Hacking team透露了一些用于感染和监视系统的技术。他们强大的UEFI/BIOS rootkit可以在不被检测的情况下进行传播。此外，Hacking team也开发了他们自己的FUD工具core-packer。

提供的渗透测试服务的安全公司了解并能使用这些技术，以允许其渗透测试人员模拟真正的黑客入侵。

Metasploit suite、Veil-Evasion和Shellter都允许渗透测试人员保护他们“恶意”的二进制文件。安全研究人员抢在攻击者发现之前，找到此类技术。我们已经发现最近的威胁”DoubleAgent”触发反恶意软件的解决方案。。

**规避技术正在行动**

在过去一年中，我们分析了很多具有规避能力的恶意软件样本。在典型的攻击中，攻击者在其攻击流程的许多步骤中会使用到规避技术。

下图是在一个典型的攻击序列中用到的规避技术：

[![](https://p1.ssl.qhimg.com/t017d78bb6091187f5e.png)](https://p1.ssl.qhimg.com/t017d78bb6091187f5e.png)

**Dridex 银行木马**

Dridex（也被称为 Cridex）首次在2014年出现的知名的银行木马。这种恶意软件窃取银行凭据并通过包含恶意宏的Word文件，以电子邮件附件的形式进行传播。自2014 以来，发生过多起Dridex事件。在其每一次大获成功后，其对应的规避技术也相应的得到了增强。

Dridex深度依赖于病毒载体的免杀。我们分析了它的几个样本。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fc1ba46924e811bd.png)

图 7： 我们可以看到函数名称和数据的混淆。这种混淆是很细微的，因为它使用ASCII数字。（哈希：610663e98210bb83f0558a4c904a2f5e）

其他变种则会用到更多先进的技术。

[![](https://p1.ssl.qhimg.com/t0119073407f665d655.png)](https://p1.ssl.qhimg.com/t0119073407f665d655.png)

图8：这个样本使用字符串的规避和内容混淆技术，PowerShell绕过策略执行，并在maxmind.com上检查ip地址是否是反病毒软件供应商的黑名单。（哈希：e7a35bd8b5ea4a67ae72decba1f75e83）

在另一个样本中，Dridex的感染载体试图检测通过检查注册表的键值“HKLM SYSTEMControlSet001ServicesDiskEnum”来搜索虚拟环境或沙箱的字符串“VMWARE”或“VBOX”。当虚拟机或沙箱被检测到时，Dridex就停止运行，伪装成无害的，或试图导致系统崩溃。

规避技术广泛用于感染载体，以避免检测和被分析师识别。在攻击的多个阶段，Dridex通过结合多种技术来避免检测和分析。

[![](https://p3.ssl.qhimg.com/t01421f8a8243eb5be3.png)](https://p3.ssl.qhimg.com/t01421f8a8243eb5be3.png)

图9：在这个例子中，Dridex使用进程挖空的规避技术，将恶意代码注入到一个挂起的进程中。然后一个新的进程去调用rundll32.exe，将恶意的DLL加载到explorer.exe。

最近的”Dridex”样本使用了新的规避技术“AtomBombing”。这种技术使用Atom表，由操作系统提供，允许应用程序存储和访问数据。 Atom表也可用于在应用程序之间共享数据。。

将恶意代码注入Atom表，并强制使用合法的应用程序执行该代码。因为用于注入恶意代码的技术是众所周知、且容易被发现的，所以攻击者现在改变了他们的技术。

最后，Dridex的最终载荷通常使用混淆和加密来保护数据，例如控制服务器的URL、僵尸网络的信息和恶意二进制代码中包含的PC名称。

**Locky勒索软件**

在2016年新近加入的勒索软件家族之中，当属Locky最为突出。它使用许多方法感染系统。它的一些规避技术与Dridex类似。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012b477af96c5be35a.png)

图 10：Locky的感染载体用统一编码与随机字符串函数的基本混淆处理。（哈希： 2c01d031623aada362d9cc9c7573b6ab）

在前面的例子中，抗混淆几乎不起作用，因为它很容易会被反Unicode，即一种用于不同格式打印文本的编码标准。此代码段中的每个统一编码字符都对应一个ASCII字符。

[![](https://p3.ssl.qhimg.com/t0169a0cb59df4aaa05.png)](https://p3.ssl.qhimg.com/t0169a0cb59df4aaa05.png)

图11— 12：在这个抗混淆的感染载体中，其代码从一个外部URL下载EXE文件到TEMP文件夹中。

其他Locky的样本在多个阶段使用XOR加密，来规避检测并绕过邮件过滤和web网关。

一些Locky的变种还使用到了Nullsoft Scriptable Install System(NSIS)压缩文件。在恶意软件试图绕过反恶意软件引擎时，该合法的应用程序经常被使用到。NSIS文件可以直接被解压缩以获取其内容。

[![](https://p3.ssl.qhimg.com/t01618d24c21cc0fd98.png)](https://p3.ssl.qhimg.com/t01618d24c21cc0fd98.png)

图 13：在此Locky样本中，我们可以看到很多旨在浪费分析时间的垃圾文件。所有这些文件被NSIS程序所压缩。其中只有一些被用来在目标系统上执行恶意操作。（哈希： 5bcbbb492cc2db1628985a5ca6d09613）

除了混淆可执行的格式，Locky还使用tricks来绕过防火墙和控制服务器的网络。一些Locky的变种会使用到Domain generation algorithm，即一种允许动态创建域的技术。Locky作者在每一次攻击活动中都会更改和更新其规避技术。

在2016年8月，Locky开始使用一个命令行参数来规避自动化的沙盒分析。如果没有命令行，此样本将不会运行在系统之上和其载荷也将不会被解码成到内存之中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c24663daac092ce6.png)

图 14：在此样本中，命令行参数"123"通过感染载体被传递到JavaScript文件。然后，由 Windows API — GetCommandLine和 CommandLineToArgvW读取命令行参数。（哈希： 0fed77b29961c0207bb4b7b033ca3fd4）

此样本的参数被用于解密并解压载荷到内存之中。如果该参数不正确，该样本只会在其试图运行加密的代码时崩溃。

Locky和其他恶意软件的另一个技巧是通过读Read Time Stamp Counter(RDTSC)的x86指令来检测虚拟环境。时间戳计数器记录着被重置以来的处理器周期的数量。RDTSC指令只是返回存储在寄存器edx:eax中的该计数器的数值。

在物理主机上，两个连续的RDTSC指令只占有少量的周期。而在虚拟主机上，此数量的周期将会变大。如果返回的值不是预期的值，该样本会进入休眠状态。

[![](https://p4.ssl.qhimg.com/t010345bf74b44b91d3.png)](https://p4.ssl.qhimg.com/t010345bf74b44b91d3.png)

图 15： Windows API调用GetProcessHeap和CloseHandle的指令用于增加处理器的周期（基于周期的指令IPC，可估算处理器的性能）。Locky比较其数值，如果执行CloseHandle比GetProcessHeap多10倍的周期，恶意软件则得出结论自己是运行在虚拟机中。（哈希： 0bf7315a2378d6b051568b59a7a0195a）

**Nymain下载者**

Nymain提供木马或勒索类型的恶意软件。Nymain使用多种规避机制以规避分析和检测。它是具有混淆处理和沙箱检测，以及活动计时器等多种反逆向工程技术的组合。

大多数恶意软件使用假的metadata以假装合法。metadata包括文件版本、公司名称和语言等程序有关的信息。而其他样本则使用被盗的证书来假装合法。

[![](https://p5.ssl.qhimg.com/t01ebf1a03cc31b4ded.png)](https://p5.ssl.qhimg.com/t01ebf1a03cc31b4ded.png)

图 16：Nymain使用的metadata。（哈希： 98bdab0e8f581a3937b538d73c96480d）

[![](https://p3.ssl.qhimg.com/t012bda8de660d876af.png)](https://p3.ssl.qhimg.com/t012bda8de660d876af.png)

图 17：Nymain使用反调试技巧，来规避调试器的动态分析。

最常见、也是最容易绕过的函数是IsDebuggerPresent。其代码调用Windows API，并在寄存器中设置一个值。如果该值不是等于零，则该程序目前正在被调试。在这种情况下，恶意软件将很快终止与API TerminateProcess的进程。另一种旁路调试器的技巧叫做 FindWindow。如果一个窗口与调试器有关，例如OllyDbg或Immunity Debugger，则此API会检测到它并关闭其恶意软件。

Nymain还执行如下额外的检查，以规避分析：

检查日期，并在攻击结束后不再执行。

检查系统上是否有恶意软件文件名的哈希值。如果有，则分析可能正在进行中。

检查与虚拟环境相关的 MAC 地址。

检查注册表项HKLMHARDWAREDescriptionSystem”SystemBiosVersion”的键值，以查找字符串"VBOX"。

插入垃圾代码，导致反汇编"code spaghetti"。

使用Domain generation algorithm来规避网络检测。

**Necurs木马**

Necurs 是一个木马程序，它可以控制系统并传递给其他恶意软件。Necurs是最大的僵尸网络之一，在2016年已拥有超过600万个节点。Necurs于2016年开始传播Locky。

[![](https://p4.ssl.qhimg.com/t0179c3127bb01791de.png)](https://p4.ssl.qhimg.com/t0179c3127bb01791de.png)

图18：Necurs采用多种机制来规避检测和分析。（哈希： 22d745954263d12dfaf393a802020764）

[![](https://p2.ssl.qhimg.com/t01ee3549c2e2190990.png)](https://p2.ssl.qhimg.com/t01ee3549c2e2190990.png)

图 19：CPUID指令返回有关CPU的信息，并允许恶意软件来检测它自己是否运行在虚拟环境之中。如果是的话，该恶意软件肯定不会运行了。

[![](https://p1.ssl.qhimg.com/t016f5deba1b9101e94.png)](https://p1.ssl.qhimg.com/t016f5deba1b9101e94.png)

图 20： 第二种规避技术使用Windows API调用GetTickCount来检索系统已启动的时间。它然后执行几个操作并再次检索消耗的时间。这种技术用于检测调试工具。如果检索的时间比预期要长，那么该文件目前正在被调试。恶意软件将终止该进程或导致系统崩溃。

[![](https://p2.ssl.qhimg.com/t0150b77b8aa1c51d01.png)](https://p2.ssl.qhimg.com/t0150b77b8aa1c51d01.png)

图 21： 一种老但仍然有效的规避技术是查询VMware所使用的输入/输出的通信端口。恶意软件可以使用magic number “VMXh”与x86“IN”指令来查询这个端口。在执行期间，该IN指令被限制在虚拟机中进行仿真。从指令返回的结果被存储在寄存器ebx中，然后与magic number "VMXh"相比较。如果结果匹配，恶意软件则是运行在VMware之上，它将终止该进程或试图导致系统崩溃。

[![](https://p5.ssl.qhimg.com/t014ef389e4468175c9.png)](https://p5.ssl.qhimg.com/t014ef389e4468175c9.png)

图 22：VMCPUID 指令类似于CPUID，不过该指令只执行在某些虚拟机之上。如果不执行VMCPUID指令，它会导致系统崩溃，以防止虚拟机的分析。

[![](https://p0.ssl.qhimg.com/t010e0b30f3eb566748.png)](https://p0.ssl.qhimg.com/t010e0b30f3eb566748.png)

图23：VPCEXT指令（可视属性的容器扩展器）是另一种被Necurs用来检测虚拟系统的抗虚拟机的技巧。这种技术并无相关记录，且只有几个僵尸主机使用。如果该指令的执行不生成异常的话，则判定恶意软件运行虚拟机之上。

**Fileless malware**

一些恶意软件感染系统并非将文件写入磁盘，并以此来规避许多类型的检测。我们曾在 McAfee Labs威胁报告：2015年11月首次提及Fileless malware。

现在，我们发现了被用作感染载体的PowerShell。在一个样本中，一个简单的JavaScript 文件运行一个经过混淆处理的PowerShell命令，从一个外部的IP地址下载已经包装过的文件。该文件绕过所有保护将恶意的DLL注入到合法的进程之中。这种恶意软件类型并非完全没有文件，但它是仍然非常有效。

下面的样本（哈希： f8b63b322b571f8deb9175c935ef56b4）显示了感染的过程：

[![](https://p0.ssl.qhimg.com/t0175f643b371d36b23.png)](https://p0.ssl.qhimg.com/t0175f643b371d36b23.png)

图24：PowerShell 命令下载NSIS的打包文件（agzabf.exe、哈希： c52950316a6d5bb7ecb65d37e8747b46），将monkshood.dll（哈希： 895c6a498afece5020b3948c1f0801a2） 注入到进程explorer.exe中。在这里使用的规避技术是DLL注入，它将代码注入到正在运行的进程中。

**规避技术趋势**

最常见的规避技术包括：

混淆处理：保护数据、变量和网络通信，随机化变量或函数的名称。它可以使用XOR或任何其他编码技术来执行。

环境检查：规避分析，恶意软件检测与虚拟环境相关的工具或工序。

沙箱检测：恶意软件执行磁盘检查，以检测与沙箱相关的文件或进程。

以下的统计来自Virus Total和McAfee，这些样本取自已知的、含有沙盒规避的技术。

**沙箱规避技术**

[![](https://p3.ssl.qhimg.com/t013d898b105dc7bc31.png)](https://p3.ssl.qhimg.com/t013d898b105dc7bc31.png)

恶意软件使用许多其他技术以规避检查。检测监测和Windows钩子（更改内部Windows 功能的行为）十分常见。提升权限对于禁用反恶意软件的工具、或是需要管理员权限来执行其他操作来说十分普遍。

**其他规避技术**

[![](https://p3.ssl.qhimg.com/t01210e515d3f3d506d.png)](https://p3.ssl.qhimg.com/t01210e515d3f3d506d.png)

信息安全行业正在开发出新的、基于机器学习的检测技术。它能够检验行为，并对可执行文件是否恶意进行了预测。

[![](https://p4.ssl.qhimg.com/t01e4a08e4158a8e09e.png)](https://p4.ssl.qhimg.com/t01e4a08e4158a8e09e.png)

图 25：对机器学习的兴趣一直在稳步增长。 资料来源： 谷歌趋势。

信息安全行业对机器学习高度感兴趣，攻击者亦然。今年3月，安全研究人员观察到了第一个恶意软件样本–Cerber勒索软件， 其规避检测就是基于机器学习的。Cerber在感染的每个阶段都使用到多个文件，动态地将它们注入正在运行的进程之中。这些攻击者所面临的挑战是：机器学习用来检测恶意文件的方式是基于特征，而非签名。在此样本中，Cerber使用单独的加载器来注入载荷，而不是在其中运行一个例程。虽然不是靠传统的反恶意软件引擎，但是这种技术却能允许Cerber通过机器学习，以未被发现的方式运行。

另一个日益增长的规避技术是固件感染，我们预测：攻击物联网的设备将会非常的普遍。

将恶意代码插入固件是一直非常有效的、规避检测的方式。固件的恶意软件可以控制许多系统组件，包括键盘、麦克风和文件系统。操作系统不能检测到它，因为感染发生在Ring-1，即内核的最深处，恶意软件可以享有许多特权，而且几乎没有什么对安全的检查。

[![](https://p0.ssl.qhimg.com/t015f49e00d8c2cd783.png)](https://p0.ssl.qhimg.com/t015f49e00d8c2cd783.png)

为了检测到这种威胁，并轻松地分析固件，McAfee高级威胁研究（McAfee Advanced Threat Research）发布了开源工具–Chipsec。你可以通过检查白名单，来查找固件是否已被如下的命令所破坏：

[![](https://p3.ssl.qhimg.com/t015b03bbb218cdd1c6.png)](https://p3.ssl.qhimg.com/t015b03bbb218cdd1c6.png)

图26：用Chipsec框架来扫描转存固件。

[![](https://p5.ssl.qhimg.com/t01c624ac7670a7b3d8.png)](https://p5.ssl.qhimg.com/t01c624ac7670a7b3d8.png)

图 27： 用比对白名单，来检查扫描转存的固件，以检测任何被修改之处。

**<br>**

**针对规避类恶意软件的保护**

为了更好地应对规避类恶意软件，首当其冲就是要学习有关恶意软件的规避技术。

我们要基于如下三个基本部分，来建立安全的程序，以防护规避类恶意软件。

人员：安全从业人员必须接受培训，正确应对安全事件并正确的掌握当前的安全技术。攻击者通常使用社会工程来感染用户。如果没有内部的宣传和培训，用户很可能会将自己的Windows系统留给攻击者胡作非为。

流程：结构清晰，内部流程必须到位，以提高安全从业人员的效率。安全最佳实践（更新、备份、治理、情报、事件响应计划等）是造就一个强大且有效的安全团队的关键要素。

技术：技术能给团队和流程提供支持。为了能够适应新的威胁，技术应持续培训和增强。

**<br>**

**有效的策略和程序，以保护免受恶意软件的攻击**

应对恶意软件的感染，最重要防御来自用户。用户必须意识到，下载和安装来自具有潜在风险资源的应用程序，所带来的风险。用户也必须认识到，恶意软件可能会在浏览网页时被无意中进行下载。

始终保持web浏览器和其加载项的更新，不断升级终端和网关上的反病毒软件到最新的版本。

不许将那些并非来自企业IT安全团队，或是未被其认证过系统连接到受信任的网络之中。规避类恶意软件会很容易从未受保护的系统扩散到受信任的网络中。

规避类恶意软件可以被攻击者用木马的方式隐藏在合法的软件之内。为了防止此类攻击的得逞，我们强烈建议使用加强的软件交付和分发机制。企业建立一个应用程序的中央存储库，以便用户从中下载已批准的软件。这种方式始终是一种最佳实践。

如果碰到用户要求被授权去安装那些未被IT安全团对事先验证过的应用程序的情况，应该教育用户只安装那些来自已知的卖家、且有受信任的签名的应用程序。网上提供的、许多看似"无害的"应用程序，其进程往往会嵌入了规避类恶意软件。

避免应用程序下载一下非web类型的资源。从Usenet组、IRC频道、即时通讯的客户端或端对端系统等途径，下载到恶意软件的可能性是非常高的。IRC和即时通讯软件中的网站链接也经常会指向一些恶意软件的下载。

实施针对网络钓鱼攻击的预防教育方案，因为恶意软件通常通过网络钓鱼攻击来进行传播。

利用威胁情报源与反恶意软件技术相结合。这种结合将有助于加快威胁的检测。

<br>

**结论**

恶意软件为了执行其恶意操作，必须保持隐蔽且不会被检测到。随着信息安全技术变得越来越复杂，规避技术的复杂程度也有所跟进。这种竞争催生了一个强大的、且具有最好规避技术的地下市场，同时也包括一些完全无法被检测到的恶意软件。它们其中一些服务甚至使用到了信息安全行业至今所未知的规避技术。

恶意软件的规避技术将继续发展，而且如今已经被部署到了攻击的任何阶段。如前面的Dridex和Locky所示，它们中的一些虽使用相同的技术来传播，但都能够规避分析与检测。而传统的规避技巧仍被一些知名的恶意软件所广泛使用着，并发挥着效力。

为了防止规避类恶意软件，我们必须首先了解它们。我们必须研究每一个案例，以探究安全技术为什么没能成功阻止攻击的深层原因。
