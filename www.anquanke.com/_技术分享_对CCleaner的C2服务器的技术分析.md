> 原文链接: https://www.anquanke.com//post/id/86908 


# 【技术分享】对CCleaner的C2服务器的技术分析


                                阅读量   
                                **154179**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：talosintelligence.com
                                <br>原文地址：[http://blog.talosintelligence.com/2017/09/ccleaner-c2-concern.html](http://blog.talosintelligence.com/2017/09/ccleaner-c2-concern.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p5.ssl.qhimg.com/t016667b6d2534a30f1.png)](https://p5.ssl.qhimg.com/t016667b6d2534a30f1.png)**

****

译者：[blueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**简介**

TALOS团队最近发表了一篇关于**CCleaner**应用软件后门的技术[分析](http://blog.talosintelligence.com/2017/09/avast-distributes-malware.html)文章。在调查过程中，我们获得了木马软件C&amp;C服务器上的一个压缩文件。最初，我们认为这些文件是不安全的。然而，通过对Web服务器配置文件，以及对归档文件中包含的MySQL数据库内容的研究，我们能够验证这些文件并不具有恶意行为。

通过分析从C&amp;C服务器上获取到的代码，我们获取到木马软件正在攻击的一个组织列表，其中包括了Cisco。通过对C&amp;C服务器数据库（9月份4天的数据）的审查，我们可以确认至少**20台**受害者的机器下载第二阶段有效载荷并执行其它恶意软件。下面是攻击者试图攻击的域名列表，这些域名中包含了**思科**的域名（Cisco com）以及其他**高知名度的科技公司**。

[![](https://p5.ssl.qhimg.com/t01fd0c3ff859f97774.png)](https://p5.ssl.qhimg.com/t01fd0c3ff859f97774.png)

这些新发现提高了我们对这些事件的关注程度，因为我们研究的内容指向了一个未知的、复杂的网络攻击组织。这些研究结果也支持和加强我们以前针对CCleaner的修复建议：针对供应链攻击的防御措施，不应该只是简单地删除机器上受影响的CCleaner版本或更新到最新版本，而应该从备份中恢复或重装系统以确保它们完全被删除，因为CCleaner带来的不仅是CCleaner后门也可能是驻留在系统中的其他恶意软件。

**<br>**

**技术细节**

**Web服务器**

从C&amp;C服务器获取到的Web目录中包括了许多PHP文件，这些PHP文件负责控制与受感染系统的通信。攻击者使用符号链接将请求“index.php”的所有正常流量**重定向**到包含恶意PHP脚本的“x.php”文件，具体如下图所示：

[![](https://p4.ssl.qhimg.com/t014c8473aa8199f77b.png)](https://p4.ssl.qhimg.com/t014c8473aa8199f77b.png)

在分析了PHP文件的内容之后，我们发现C&amp;C服务器实施了一系列的检查以确定是否继续进行攻击操作或者简单地重定向到合法的Piriform网站。C&amp;C服务器会对请求报文的HTTP头、请求方法类型以及服务器端口进行检查，以确认这些请求来自于受感染的主机。

[![](https://p2.ssl.qhimg.com/t01f0b3e2f4dc195b96.png)](https://p2.ssl.qhimg.com/t01f0b3e2f4dc195b96.png)

PHP中包含对所定义的“x.php”变量中信息存储所需表的引用，如下图所示：

[![](https://p0.ssl.qhimg.com/t01adb3c81f6d5d1ebd.png)](https://p0.ssl.qhimg.com/t01adb3c81f6d5d1ebd.png)

在init.php文件中声明了db_table变量，该变量允许在攻击者的基础设施上插入所需的数据库。以下是“Server”数据库的定义：

[![](https://p2.ssl.qhimg.com/t01e9fcbcbc07dbd62b.png)](https://p2.ssl.qhimg.com/t01e9fcbcbc07dbd62b.png)

Web服务器中还包含第二个PHP文件（init.php），在该文件中定义了核心变量、可以使用的操作、数据库配置文件的使用以及变量$ x86dllname使用的文件名和目录的位置。

下面的信息是从受感染的系统收集的，攻击者往往依靠这些数据来确定如何处理这些受感染的主机，这些数据包括操作系统的版本信息，系统架构信息，用户是否拥有管理员权限以及与系统相关的主机名和域名。

[![](https://p4.ssl.qhimg.com/t015233974f79d06439.png)](https://p4.ssl.qhimg.com/t015233974f79d06439.png)

系统配置信息是相当有用的，其中包括了受害者机器上安装的软件列表以及当前正在运行的进程列表，系统配置信息存储在MySQL数据库。

[![](https://p0.ssl.qhimg.com/t01b00f04dbf1708b1f.png)](https://p0.ssl.qhimg.com/t01b00f04dbf1708b1f.png)

还有一些功能负责在满足预定需求的系统上装载和执行第2阶段的有效负载，类似于我们之前在第1阶段分析中的功能。虽然shellcode能够在x86和x64 PE系统上运行，但C&amp;C 服务器实际上只使用了x86 PE加载功能。

[![](https://p3.ssl.qhimg.com/t016ec8cf8ed03c9b3c.png)](https://p3.ssl.qhimg.com/t016ec8cf8ed03c9b3c.png)

以下是与PE loader x64版本相关的shellcode。

[![](https://p1.ssl.qhimg.com/t0121120c4764051c3b.png)](https://p1.ssl.qhimg.com/t0121120c4764051c3b.png)

PHP脚本将系统ID和C&amp;C服务器上的$DomainList, $IPList, and $HostList这三个值进行比较，以确定感染的系统是否应该被交付第2阶段的有效载荷。php代码如下图所示：

[![](https://p1.ssl.qhimg.com/t01470b047f90b3c86a.jpg)](https://p1.ssl.qhimg.com/t01470b047f90b3c86a.jpg)

使用基于域的过滤方法可以进一步表明该攻击组织的目标性质。基于存储在MySQL数据库中的系统信息，我们能够确认受到后门影响的系统数量是巨大的，以及攻击者特意控制哪些被感染的系统用于传递第2阶段的有效载荷。之前关于目前还没有系统执行阶段2的有效载荷这一报道并不准确，通过分析数据库表中存储的有关第二阶段有效载荷的系统信息，我们可以确定目前为止受此有效载荷影响的一共有20个主机，我们将在下文对第2阶段有效载荷进行介绍。

**MySQL数****据库**

C&amp;C服务器的MySQL数据库中一共有两个表：一个表描述了所有与服务器进行通信的机器，另一个描述了所有接收第二阶段有效载荷的机器，这两个表中保存的数据项的日期都在9月12号至9月16号之间。通过分析数据表我们发现超过700000台机器在这段时间与C&amp;C服务器有过通信，超过20台机器接收了第二阶段的有效载荷。

在恶意软件执行期间，恶意软件会定时与C&amp;C服务器通信，并发送有关受感染系统的系统信息。这些信息包括IP地址、在线时间、主机名、域名、进程列表以及更多信息等。攻击者很可能会利用这些信息来确定在攻击的最后阶段应该使用哪些机器。

连接数据存储在“Server”表中。 以下是该数据库表中Talos主机的示例：

[![](https://p5.ssl.qhimg.com/t01d9cd8744aeb48ccf.png)](https://p5.ssl.qhimg.com/t01d9cd8744aeb48ccf.png)

此外，受感染的机器会共享已安装程序的列表，具体如下图所示。

[![](https://p3.ssl.qhimg.com/t015a43b7e844707755.png)](https://p3.ssl.qhimg.com/t015a43b7e844707755.png)

也会获取进程列表，如下图所示。

[![](https://p5.ssl.qhimg.com/t01f9e67214287d2cb5.png)](https://p5.ssl.qhimg.com/t01f9e67214287d2cb5.png)

网络攻击者可以结合上述收集到的数据信息，决定是否启动后期的有效负载，以保证payloads能够在给定的系统上无法被安全工具检测以及稳定的运行。

与“Server”数据库表分开存储的第二个数据库表中包含了一个数据集，该数据集与第2阶段接收到有效负载的系统相关。该表与“Server”数据库中的表结构比较类似，其结构如下所示：

[![](https://p5.ssl.qhimg.com/t01cedc279a293f5163.png)](https://p5.ssl.qhimg.com/t01cedc279a293f5163.png)

经过对第二个数据库中的“OK”表进行分析，我们可以肯定的是20台机器成功接收到了第2阶段的有效载荷。Talos小组第一时间与受影响的企业取得联系，并通报其可能遭遇的安全违规问题。

[![](https://p5.ssl.qhimg.com/t016067698291f261ad.png)](https://p5.ssl.qhimg.com/t016067698291f261ad.png)

通过对“Server”数据库表的分析，我们发现攻击者能够对各种不同的目标发起网络攻击。考虑到C&amp;C服务器上的过滤，攻击者可以根据他们选择的环境或组织在任何给定的时间添加或删除域名。为了进一步提供关于攻击者选择攻击类型的更多视图，下面的截图显示了数据库表中受感染机器的总条目：

[![](https://p2.ssl.qhimg.com/t01a4e91cc737cc2a95.png)](https://p2.ssl.qhimg.com/t01a4e91cc737cc2a95.png)

下面的截图显示了世界各地受影响的政府系统的数量。

[![](https://p5.ssl.qhimg.com/t01fb7aa183e9e0055b.png)](https://p5.ssl.qhimg.com/t01fb7aa183e9e0055b.png)

同样，下图显示了世界各地受影响的银行系统的数量：

[![](https://p5.ssl.qhimg.com/t0124ee8aeab545d47d.png)](https://p5.ssl.qhimg.com/t0124ee8aeab545d47d.png)

Talos小组的研究人员解释称，通过利用基础设施与相关恶意软件的组合，攻击者能够实现上述级别的破坏能力，此次攻击的严重性与潜在影响不言而喻。

**第2阶段的有效载荷**

geesetup_x86.dll是第2阶段的安装程序，此安装程序首先检查操作系统的版本，然后释放一个32位或64位版本的木马工具。x86版本使用tsmsisrv.dll木马工具，该工具使用与CCleaner后门工具相同的方法释放virtcdrdrv。x64版本使用efacli64.dll木马工具释放木马文件并命名为symefa，该名称来自于合法的可执行文件Symantec Endpoint中的一部分，他们还在恶意软件中打包了一个合法的二进制程序。此外，安装程序将一个编码的PE文件放入注册表中：



```
HKLMSoftwareMicrosoftWindows NTCurrentVersionWbemPerf01
HKLMSoftwareMicrosoftWindows NTCurrentVersionWbemPerf02
HKLMSoftwareMicrosoftWindows NTCurrentVersionWbemPerf03
HKLMSoftwareMicrosoftWindows NTCurrentVersionWbemPerf04
```

这样做的目的是想在注册表中解码和执行此PE文件，该PE会对其他C&amp;C服务器执行查询操作，并执行内存中的PE文件。这可能使某些系统的检测复杂化，因为可执行文件不会直接存储在文件系统上。注册表中是一个由木马病毒文件执行的轻量级的后门模块，这个后门会从github.com或WordPress.com上获取一个IP地址，并从该IP地址上下载一个PE模块运行，具体如下图所示：

[![](https://p0.ssl.qhimg.com/t010cde74a89756158a.png)](https://p0.ssl.qhimg.com/t010cde74a89756158a.png)

**代码重用**

结合卡巴斯基研究人员和Talos小组的分析，Cleaner事件当中发现的种种证据同Group 72这一网络间谍组织连接起来，虽然目前并不确定这一切的幕后黑手就是Group 72黑客组织，但二者确实共享部分代码，如下图所示：

**左边:**

2bc2dee73f9f854fe1e0e409e1257369d9c0a1081cf5fb503264aa1bfe8aa06f       (CCBkdr.dll)

**右边:**

0375b4216334c85a4b29441a3d37e61d7797c2e1cb94b14cf6292449fb25c7b2 (Missl backdoor – APT17/Group 72)

[![](https://p2.ssl.qhimg.com/t0170a385ed784c16ed.png)](https://p2.ssl.qhimg.com/t0170a385ed784c16ed.png)

**<br>**

**结论**

供应链攻击在速度和复杂性方面似乎都在增加，但安全公司在对待尚未完全了解的安全事件在严重程度上经常被淡化，这可能不利于保护受害者的利益。因此作为安全公司，我们必须认真对待这些攻击。在这个特殊的例子中，一个相当复杂的攻击组织设计了一个系统，该系统似乎专门针对科技公司，通过使用供应链攻击给大量的受害者造成损害，并希望在目标网络的计算机上放置一些有效载荷。

**<br>**

**Indicators of Compromise (IOCs)**

dc9b5e8aa6ec86db8af0a7aa897ca61db3e5f3d2e0942e319074db1aaccfdc83   (GeeSetup_x86.dll)

128aca58be325174f0220bd7ca6030e4e206b4378796e82da460055733bb6f4f   (EFACli64.dll)

07fb252d2e853a9b1b32f30ede411f2efbb9f01e4a7782db5eacf3f55cf34902   (TSMSISrv.dll)

f0d1f88c59a005312faad902528d60acbf9cd5a7b36093db8ca811f763e1292a
