> 原文链接: https://www.anquanke.com//post/id/182201 


# SWEED组织：恶意软件Agent Tesla行为演变研究分析


                                阅读量   
                                **191074**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Edmund Brumaghin and other Cisco Talos researchers，文章来源：blog.talosintelligence.com
                                <br>原文地址：[https://blog.talosintelligence.com/2019/07/sweed-agent-tesla.html](https://blog.talosintelligence.com/2019/07/sweed-agent-tesla.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01261e3a72a37d49cb.jpg)](https://p0.ssl.qhimg.com/t01261e3a72a37d49cb.jpg)



## 0x01 摘要

我们最近发现了大量正在进行的恶意软件传播活动，这些活动与一个名为“SWEED”的组织有关，传播的恶意软件包括著名的恶意软件Formbook、Lokibot和Agent Tesla。根据我们的研究，SWEED组织至少从2017年就开始运作了，主要使用偷窃者和远程访问木马的方法攻击受害者。

对于带有恶意附件的鱼叉式网络钓鱼邮件的不同样本，SWEED组织的行为是一致的。虽然这些活动中包含了大量不同类型的恶意文档，但主要的恶意行为是通过恶意软件Agent Tesla感染其受害者，该版本是最晚从2014年以来就一直进行信息窃取活动。SWEED使用的Agent Tesla版本由于其打包的方式和感染系统的方式与我们看到的略有不同。在这篇文章中，我们将追溯与SWEED相关的每个活动，并讨论一些参与者的策略，技术和程序（TTPs）。



## 0x02 SWEED活动时间及其使用的方法

### <a name="1.2017%E5%B9%B4%EF%BC%9A%E9%9A%90%E5%86%99%E6%9C%AF"></a>1.2017年：隐写术

最早被发现的SWEED活动之一可以追溯到2017年。在这次攻击中，参与者将恶意软件植入ZIP文件中，然后将这些ZIP文件作为邮件的附件。附件的文件名通常类似于“Java_Updater.zip”或“P-O of june 2017.zip”。以下是与此次活动相关的一封邮件的例子:

[![](https://p2.ssl.qhimg.com/t015cfe2f7402b7d181.png)](https://p2.ssl.qhimg.com/t015cfe2f7402b7d181.png)

所附的ZIP文件包含Agent Tesla的打包版。打包器使用.NET后缀并利用隐写术来隐匿自身，接下来解码第二个.NET可执行文件，该文件使用相同的技术来检索最终的Agent Tesla payload。这是存储在资源中的文件：

[![](https://p0.ssl.qhimg.com/t015ffadadefa7fa2fd.png)](https://p0.ssl.qhimg.com/t015ffadadefa7fa2fd.png)

下面是解码图像中的PE的算法:

[![](https://p2.ssl.qhimg.com/t01c51c620c6e4291cf.png)](https://p2.ssl.qhimg.com/t01c51c620c6e4291cf.png)

解码后的二进制文件存储在数组中。

### <a name="2.2018%E5%B9%B41%E6%9C%88%EF%BC%9AJAVA%20DROPPERS"></a>2.2018年1月：JAVA DROPPERS

在2018年初，我们观察到SWEED开始利用基于Java的droppers。与之前的活动类似，JAR文件是直接附在邮件上，其使用的文件名如“Order_2018.jar”。JAR文件的目的是获取有关受感染系统的信息，并便于下载恶意软件Agent Tesla的打包版。有趣的是，在这些活动开始前几个月，一个用户名为“Sweed”的HackForums用户积极地寻找了一个Java加密器，其中原因稍后我们会进行解释。

### <a name="3.2018%E5%B9%B44%E6%9C%88%EF%BC%9AOffice%20exploit%20(CVE-2017-8759)"></a>3.2018年4月：Office exploit (CVE-2017-8759)

在2018年4月，SWEED开始利用已公开的Microsoft Office漏洞。这些邮件活动中的一个附件值得注意，因为它是一个PowerPoint文档（.ppxs）。其中一个幻灯片中包含的代码触发了CVE-2017-8759的漏洞利用，这是Microsoft .NET框架中的一个远程执行代码漏洞。

[![](https://p0.ssl.qhimg.com/t018f5bad5cc4521c73.png)](https://p0.ssl.qhimg.com/t018f5bad5cc4521c73.png)

您可以使用文件名“chuks.png”查看托管在攻击者控制的Web服务器上的外部内容的执行情况。正如所料，PNG实际上并不是一个图像。相反，它是XML中的Soap定义，如下面的截图所示：

[![](https://p4.ssl.qhimg.com/t011df520f6345068e9.png)](https://p4.ssl.qhimg.com/t011df520f6345068e9.png)

此代码的目的是解码URL并下载托管在攻击者控制的Web服务器上的PE32。其生成的可执行文件是Agent Tesla的打包版。

### <a name="4.2018%E5%B9%B45%E6%9C%88%EF%BC%9AOffice%20exploit%EF%BC%88CVE-2017-11882%EF%BC%89"></a>4.2018年5月：Office exploit（CVE-2017-11882）

在2018年5月，SWEED开展的活动开始利用Microsoft Office中的另一个漏洞：CVE-2017-11882，这是Microsoft Office中的一个远程代码执行错误，通常在商品类恶意软件分发的恶意文档中被利用。

当我们在ThreatGrid中执行这个例子时，可以看到漏洞如何滥用Office中的Equation Editor ：

[![](https://p2.ssl.qhimg.com/t012a70e81e2bf81cbb.png)](https://p2.ssl.qhimg.com/t012a70e81e2bf81cbb.png)

如下所示，恶意文档的设计看起来好像是一张发票。

[![](https://p0.ssl.qhimg.com/t01d1681cd6f7f3d90c.png)](https://p0.ssl.qhimg.com/t01d1681cd6f7f3d90c.png)

与之前的活动一样，此恶意文档的目的是下载并执行恶意软件Agent Tesla的打包版。

### <a name="5.2019%E5%B9%B4%EF%BC%9AOFFICE%E5%AE%8F%E5%92%8CAUTOIT%20DROPPERS"></a>5.2019年：OFFICE宏和AUTOIT DROPPERS

从2019年开始，与SWEED相关的活动开始利用恶意Office宏。与之前的攻击一样，他们利用鱼叉式网络钓鱼邮件和恶意附件来启动感染过程。

[![](https://p4.ssl.qhimg.com/t01a89f45a8ee2cfe8a.png)](https://p4.ssl.qhimg.com/t01a89f45a8ee2cfe8a.png)

附加的XLS包含一个被混淆的VBA宏，它使用WMI调用执行PowerShell脚本。PowerShell脚本也使用XOR操作进行混淆处理以隐匿其代码。解码后，它显示是.NET文件。

[![](https://p0.ssl.qhimg.com/t0102dd798a4175a598.png)](https://p0.ssl.qhimg.com/t0102dd798a4175a598.png)

这个.NET代码负责执行某些检查并下载另一个可执行文件，其中使用的混淆方案与前面描述的PowerShell中使用的相同。然后下载的可执行文件被保存并执行。

[![](https://p5.ssl.qhimg.com/t01f14a81ea6977597d.png)](https://p5.ssl.qhimg.com/t01f14a81ea6977597d.png)

上述下载的二进制文件是AutoIT-compiled脚本。该脚本具有大量无用垃圾代码，这使得我们的分析变得更加困难和耗时。

[![](https://p0.ssl.qhimg.com/t0155a76fadb59b249c.png)](https://p0.ssl.qhimg.com/t0155a76fadb59b249c.png)

AutoIT脚本中包含的字符串和一些命令已使用XOR操作进行了混淆处理，如下图所示：

[![](https://p0.ssl.qhimg.com/t010fff8f2569352f52.png)](https://p0.ssl.qhimg.com/t010fff8f2569352f52.png)

解码器接收两个十六进制字符串：第一个是反混淆的字符串，第二个确定XOR操作的数次。根据第二个参数的长度对每个字符执行XOR运算，然后将该操作重复多次，次数等于长度和位置的乘积。例如，如果长度值是1，则使用相同的密钥重复操作两次，生成十六进制字符串的明文。

执行环境检查后，恶意软件将重构汇编代码，该代码在十六进制字符串中进行混淆处理。接着使用AutoIT脚本语言<br>
Dll* 系列函数将该代码加载到当前进程的地址空间。

[![](https://p5.ssl.qhimg.com/t01c48c1bcaa4b05bc9.png)](https://p5.ssl.qhimg.com/t01c48c1bcaa4b05bc9.png)

最后，恶意软件使用两个参数执行汇编代码。第一个参数是可执行文件的路径。此程序集将使用可执行文件创建进程，并将payload注入此进程。

[![](https://p5.ssl.qhimg.com/t0150ebe9d44e7382a0.png)](https://p5.ssl.qhimg.com/t0150ebe9d44e7382a0.png)

和预期一样，此活动中的payload是Agent Tesla的另一个打包版本。

[![](https://p3.ssl.qhimg.com/t0171b555bd9dd6bab9.png)](https://p3.ssl.qhimg.com/t0171b555bd9dd6bab9.png)



## 0x03 SWEED活动的特征：UAC绕过

与SWEED相关的活动的一个共同特征是使用各种技术绕过被感染系统上的User Account Control（UAC）。在2019年观察到的活动中存在这样的例子：当恶意软件首次在系统上执行时，它执行高运行完整性的Windows进程“fodhelper.exe”。在执行之前，恶意软件会设置以下注册表项：

```
HKCUSoftwareClassesms-settingsshellopencommand
```

此注册表项指向恶意可执行文件的位置，如图所示：

[![](https://p1.ssl.qhimg.com/t01f583beb9f209812d.png)](https://p1.ssl.qhimg.com/t01f583beb9f209812d.png)

“fodhelper.exe”使用这一注册表项，其设置以管理员身份执行fodhelper.exe。此功能只允许恶意软件绕过UAC而不是权限提升，因为权限提升的前提是用户必须已拥有系统的管理访问权限，而它只是用于避免向用户显示UAC提示。第二个恶意软件实例的执行将通过对受感染系统的管理访问来实现。



## 0x04 SWEED活动的基础设施

与SWEED特性相关的各种散布活动使用有限数量的散布和C2基础设施，很长一段时间内在许多不同的散布活动中使用相同的服务器。与SWEED使用的域名相关的大多数注册人列出以下邮件地址：

```
aaras480@gmail[.]com
sweed.[redacted]@gmail[.]com
```

用于注册大多数域的注册人联系信息也是一致的：

[![](https://p2.ssl.qhimg.com/t01b9b145a50b5a3a67.png)](https://p2.ssl.qhimg.com/t01b9b145a50b5a3a67.png)

2018年4月，一名安全研究人员发布了一份RDP服务器的截图（[https://twitter.com/mrglaive/status/987780707551469569](https://twitter.com/mrglaive/status/987780707551469569) ），该服务器是被SWEED(84.38.134[.]121)充分利用的：

[![](https://p2.ssl.qhimg.com/t016fc010ffc104b9f3.png)](https://p2.ssl.qhimg.com/t016fc010ffc104b9f3.png)

如上图所示，可以看到在RDP服务器上建立的用户帐户列表，其中包括名为“sweed”的帐户。多个用户当前处于活动状态的这个现象表明该服务器正在以多用户的身份使用，并提供SWEED成员可以协作运行的平台。这也可能表明负责这些持续恶意软件散布活动的个人之间存在着业务关系。

我们还确定了几个DDNS域，这些域用于促进与共享RDP服务器之间的连接，该服务器具有许多与RDP用户帐户相同的值：
- sweedoffice[.]duckdns[.]org
- sweedoffice-olamide[.]duckdns[.]org
- sweedoffice-chuks[.]duckdns[.]org
- www.sweedoffice-kc.duckdns[.]org
- sweedoffice-kc.duckdns[.]org
- sweedoffice-goodman.duckdns[.]org
- sweedoffice-bosskobi.duckdns[.]org
- www.sweedoffice-olamide.duckdns[.]org
- www.sweedoffice-chuks.duckdns[.]org
在我们分析与SWEED相关的各种活动时，我们确定了几个常见的元素，这些元素也反映了与RDP服务器用户相关的不同值。在许多情况下，用于托管由SWEED散布的恶意PE32的分发服务器包含一个目录结构，其中包含多个目录和正在分发的二进制文件，其使用的二进制文件名以及用于托管恶意内容的目录名反映了RDP服务器上存在的相同用户。

例如，在2019年6月，以下URLs托管与这些活动相关的恶意内容：
- hxxp://aelna[.]com/file/chuks.exe
- hxxp://aelna[.]com/file/sweed.exe
- hxxp://aelna[.]com/file/duke.exe
同样，在调查与受感染系统中泄露敏感信息的已知域相关的样本时，我们可以看到下列二进制文件名很长一段时间内在相关活动中重复使用：
- dadi.exe
- kelly.exe
- chuks.exe
- olamide.exe
- sweed.exe
- kc.exe
- hero.exe
- goodman.exe
- duke.exe
- hipkid.exe
在某些情况下，分发服务器上的目录结构包含多个托管恶意文件的目录，下面使用域sodismodisfrance[.]cf列出：
- sodimodisfrance[.]cf/2/chuks.exe
- sodimodisfrance[.]cf/6/chuks.exe
- sodimodisfrance[.]cf/5/goodman.exe
- sodimodisfrance[.]cf/1/chuks.exe
- sodimodisfrance[.]cf/1/hipkid.exe
- sodimodisfrance[.]cf/5/sweed.exe
- sodimodisfrance[.]cf/2/duke.boys.exe
这些目录与SWEED相关的参与者使用的句柄相匹配。另一个用于泄露Agent Tesla收集的敏感信息的已知域名是sweeddehacklord[.]us。对与此域通信的已知恶意软件的分析保持着类似的操作模式。

在分析与SWEED相关的恶意软件活动时，我们还研究了与恶意软件分发的各种RAT和窃取者相关的管理面板在托管时使用的有趣的路径。实际上，在单个C2服务器上，我们确定了几个具有以下URL的面板：
- sweed-office.comie[.]ru/goodman/panel
- sweed-office.comie[.]ru/kc/panel/
- wlttraco[.]com/sweed-office/omee/panel/login.php
- wlttraco[.]com/sweed-client/humble1/panel/post.php
- wlttraco[.]com/sweed-client/sima/panel/post.php
- wlttraco[.]com/sweed-office/omee/panel/post.php
- wlttraco[.]com/sweed-office/kc/panel/post.php
- wlttraco[.]com/sweed-office/olamide/panel/post.php
- wlttraco[.]com/sweed-office/jamil/panel/post.php
- wlttraco[.]com/sweed-client/niggab/panel/post.php
- wlttraco[.]com/sweed-client/humble2/panel/post.php
- wlttraco[.]com/sweed-office/harry/panel/post.php
根据我们的研究以及面板托管的位置，我们认为wiki，olamide，chuks，kc，goodman，bosskobi，dadi，hipkid等等都是SWEED的客户或商业伙伴。使用二进制文件名，目录结构和其他部件，我们已经能够识别在各种黑客论坛，IRC服务器中表现出将用户与恶意软件分发活动的各种元素联系起来的网上行为和兴趣特点。

此外，还有其他几个可以链接到SWEED的域，其似乎与各种恶意软件系列和散布活动相关。这些被观察到的域还被解析为与前面提到的RDP服务器相关的IP。
- sweeddehacklord[.]us
- sweed-office.comie[.]ru
- sweed-viki[.]ru


## 0x05 虚假域名的利用

与SWEED相关的许多活动中的另一个有趣的元素是使用误植域名的域来托管过去几年散布的打包版Agent Tesla二进制文件。

[![](https://p2.ssl.qhimg.com/t01ce15d33162b123fd.jpg)](https://p2.ssl.qhimg.com/t01ce15d33162b123fd.jpg)

从国家的角度来看待受害者学，很明显SWEED在选择目标时没有地理方面的集中。SWEED的目标公司遍布全球。

[![](https://p3.ssl.qhimg.com/t0138eabd696a176f4c.jpg)](https://p3.ssl.qhimg.com/t0138eabd696a176f4c.jpg)

然而，按活动细分确实显示出制造类和物流类的公司受害的明显趋势。

如下图所示是这些域名的概述格式，包括它们的目标公司以及与公司相关的行业。在某些情况下，我们无法确定来自误植域名的域的目标组织。

[![](https://p2.ssl.qhimg.com/t01b35e918884b9ad9e.jpg)](https://p2.ssl.qhimg.com/t01b35e918884b9ad9e.jpg)

在上面列出的所有域中，与这些域相关的注册人帐户信息与我们识别出与SWEED活动相关的信息一致。



## 0x06 运营安全（OPSEC）

我们在黑客论坛，IRC频道和其他网站上发现了各种行为，这些行为与我们观察到的散布此恶意软件的参与者的TTP一致。

### <a name="%E2%80%9CSWEE%20D%E2%80%9D"></a>“SWEE D”

在我们的分析过程中，我们通过昵称“SWEE D”在HackForums上识别了一个用户。在与该用户相关的大多数在线帖子中，他们的联系信息包含在帖子中，并列出了Skype地址”sweed.[redacted]”。

在2018年1月活动之前的几个月中，我们观察到这个用户发帖要求访问一个Java加密器。通常，加密器用于帮助规避防病毒检测，因为它们“加密”正在散布的恶意payload的内容。

[![](https://p5.ssl.qhimg.com/t011f7f5a0e8693d08f.png)](https://p5.ssl.qhimg.com/t011f7f5a0e8693d08f.png)

同一个用户在与Java加密器相关的线程中反复发布帖子，甚至让其他用户对他们发布的频率感到愤怒：

[![](https://p1.ssl.qhimg.com/t01b864bce4b985392d.png)](https://p1.ssl.qhimg.com/t01b864bce4b985392d.png)

HackForums帖子中列出的相同Skype帐户在2016年被名为“Daniel”的人使用，该用户同时评论了与Facebook网络钓鱼页面的创建有关的博客：

[![](https://p4.ssl.qhimg.com/t01c85294f41d08df58.png)](https://p4.ssl.qhimg.com/t01c85294f41d08df58.png)

同样的Skype帐户也在2015年被名为”[redacted] Daniel.”的人使用。

[![](https://p5.ssl.qhimg.com/t018747e00959ffde5a.png)](https://p5.ssl.qhimg.com/t018747e00959ffde5a.png)

注意：[redacted]是与域wlttraco[.]com（sweed.[redacted][@gmail](https://github.com/gmail).com）的注册人帐户相关的邮件地址中使用的名称。

我们还找到了在Twitter帐户上发布的截图.sS!.!（[https://twitter.com/sS55752750](https://twitter.com/sS55752750) ），其显示Discord服务器“Agent Tesla Live”，其中列出了sweed ([redacted] Daniel)是一名工作人员。

[![](https://p4.ssl.qhimg.com/t01cae8eb7525897989.png)](https://p4.ssl.qhimg.com/t01cae8eb7525897989.png)

值得注意的是，此Discord用户（SWEE D）使用的头像与Skype用户（sweed.[redacted].）使用的头像相同。

[![](https://p2.ssl.qhimg.com/t0109dbffa99387c2b8.png)](https://p2.ssl.qhimg.com/t0109dbffa99387c2b8.png)

如图所示，我们在Skype上联系了SWEE D并且能够确认是同一个用户操作Discord和Skype帐户：

[![](https://p3.ssl.qhimg.com/t0158a9f08d166eaf28.png)](https://p3.ssl.qhimg.com/t0158a9f08d166eaf28.png)

在我们与SWEE D的互动中，他们提到他们是学习道德黑客的学生，在各公司的IT部门工作，为了移除恶意软件并提高系统的安全性。

[![](https://p0.ssl.qhimg.com/t019de4b337465b8731.png)](https://p0.ssl.qhimg.com/t019de4b337465b8731.png)

如下图所示，这与在IRC交易中观察到的活动相反。其中名为“sweed”的用户正在向监听机器人提交信用卡信息以试图检查可能被盗的信用卡信息的有效性和可用性。

[![](https://p5.ssl.qhimg.com/t01ac48415780aeb94d.png)](https://p5.ssl.qhimg.com/t01ac48415780aeb94d.png)

IRC频道似乎是专门为此目的而创建和使用的，名为“chkViadex24”的机器人返回与提交的信用卡相关的信息：

[![](https://p0.ssl.qhimg.com/t019dd3ae10cb632a71.png)](https://p0.ssl.qhimg.com/t019dd3ae10cb632a71.png)

这个例子说明了如何使用被盗的信用信息来确定他们是否可以从这些信息中获利。

“SWEE D”，“sweed”和[redacted] Daniel可能是同一个人。我们还识别了具有相同名称的用户在LinkedIn上的个人资料：

[![](https://p0.ssl.qhimg.com/t01f8b24d9f1b8c59e1.png)](https://p0.ssl.qhimg.com/t01f8b24d9f1b8c59e1.png)

此帐户将尼日利亚列为其所在地，而”[redacted]”是一部尼日利亚小说。此外，我们在分析“sweed”时发现了许多细节，例如LinkedIn个人资料中的信息， “[redacted]”的引用，所使用的注册人信息以及Skype帐户中列出的位置表明这个人可能位于在尼日利亚。我们认为“sweed”是该集团的关键成员，其他账户很有可能是其客户或与其存在业务合作关系。



## 0x07 总结

SWEED从2015年开始，已经至少活跃了三年，具有该名称的用户一直活跃在各种论坛，IRC频道和Discord服务器上。目前，SWEED正在积极瞄准全球的中小型公司。根据其使用的TTP，SWEED应被视为相对业余的参与者。他们使用众所周知的漏洞，商品窃取者和RATs（Pony，Formbook，UnknownRAT，Agent Tesla等），并且似乎依赖于黑客论坛上随时可用的工具包。SWEED一直利用打包和加密，以最大限度地避免反恶意软件解决方案的检测。我们评估SWEED也没有有效的运营安全性，因为他们大约五年一直使用了几个相同的在线账户，并且允许他们的许多信息，运营和员工被发现。

目前，我们无法肯定地说，与SWEED相关的其他账户和相关人员是商业伙伴还是客户。但是，它们都以跨域协调的方式使用相同的基础设施，依赖于相同的恶意软件和打包程序，并且所有操作都非常相似。SWEED在安全研究界相对知名，这项研究使我们深入了解这些网络犯罪组织为了最大限度地提高其收入和逃避检测的能力，是如何运作和发展的。我们预计SWEED将在可预见的未来继续运营，我们也将继续监控其活动，以确保客户受到保护。



## IOCs

### <a name="2017%E5%B9%B4"></a>2017年

Java_Updater.zip -&gt; 59b15f6ace090d05ac5f7692ef834433d8504352a7f45e80e7feb05298d9c2dd<br>
P-O of Jun2017.zip -&gt; e397ba1674a6dc470281c0c83acd70fd4d772bf8dcf23bf2c692db6575f6ab08<br>
Agent Tesla: 8c8f755b427b32e3eb528f5b59805b1532af3f627d690603ac12bf924289f36f

### <a name="2018%E5%B9%B41%E6%9C%88"></a>2018年1月

Java sample=&gt; d27a29bdb0492b25bf71e536c8a1fae8373a4b57f01ad7481006f6849b246a97

### <a name="2018%E5%B9%B44%E6%9C%88"></a>2018年4月

New Order For Quotation.ppsx -&gt; 65bdd250aa4b4809edc32faeba2781864a3fee7e53e1f768b35a2bdedbb1243b

### <a name="2018%E5%B9%B45%E6%9C%88"></a>2018年5月

SETTLEMENT OF OUTSTANDING.xlsx -&gt; 111e1fff673466cedaed8011218a8d65f84bee48d5ce6d7e8f62cb37df75e671

### <a name="2019%E5%B9%B4"></a>2019年

Request and specification of our new order.xls -&gt; 1dd4ac4925b58a2833b5c8969e7c5b5ff5ec590b376d520e6c0a114b941e2075<br>
Agent Tesla -&gt; fa6557302758bbea203967e70477336ac7a054b1df5a71d2fb6d822884e4e34f

### <a name="Domains"></a>Domains

sweeddehacklord[.]us<br>
sweed-office.comie[.]ru<br>
sweed-viki[.]ru<br>
sweedoffice.duckdns[.]org<br>
sweedoffice-olamide.duckdns[.]org<br>
sweedoffice-chuks.duckdns[.]org<br>
www.sweedoffice-kc.duckdns[.]org<br>
sweedoffice-kc.duckdns[.]org<br>
sweedoffice-goodman.duckdns[.]org<br>
sweedoffice-bosskobi.duckdns[.]org<br>
www.sweedoffice-olamide.duckdns[.]org<br>
www.sweedoffice-chuks.duckdns[.]org<br>
aelna[.]com<br>
candqre[.]com<br>
spedaqinterfreight[.]com<br>
worldjaquar[.]com<br>
zurieh[.]com<br>
aiaininsurance[.]com<br>
aidanube[.]com<br>
anernostat[.]com<br>
blssleel[.]com<br>
bwayachtng[.]com<br>
cablsol[.]com<br>
catalanoshpping[.]com<br>
cawus-coskunsu[.]com<br>
crosspoiimeri[.]com<br>
dougiasbarwick[.]com<br>
erieil[.]com<br>
etqworld[.]com<br>
evegreen-shipping[.]com<br>
gufageneys[.]com<br>
hybru[.]com<br>
intermodaishipping[.]net<br>
jltqroup[.]com<br>
jyexports[.]com<br>
kayneslnterconnection[.]com<br>
kn-habour[.]com<br>
leocouriercompany[.]com<br>
lnnovalues[.]com<br>
mglt-mea[.]com<br>
mti-transt[.]com<br>
profbuiiders[.]com<br>
quycarp[.]com<br>
regionaitradeinspections[.]com<br>
repotc[.]com<br>
rsaqencies[.]com<br>
samhwansleel[.]com<br>
serec[.]us<br>
snapqata[.]com<br>
sukrltiv[.]com<br>
supe-lab[.]com<br>
usarmy-mill[.]com<br>
virdtech[.]com<br>
willistoweswatson[.]com<br>
xlnya-cn[.]com<br>
zarpac[.]us<br>
Oralbdentaltreatment[.]tk<br>
wlttraco[.]com
