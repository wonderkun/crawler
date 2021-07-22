> 原文链接: https://www.anquanke.com//post/id/86415 


# 【安全报告】McAfee Labs 威胁报告 2017.06 （下）


                                阅读量   
                                **89523**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：mcafee.com
                                <br>原文地址：[https://www.mcafee.com/us/resources/reports/rp-quarterly-threats-jun-2017.pdf](https://www.mcafee.com/us/resources/reports/rp-quarterly-threats-jun-2017.pdf)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p0.ssl.qhimg.com/t0197a4fa473262cfd4.jpg)](https://p0.ssl.qhimg.com/t0197a4fa473262cfd4.jpg)**



译者：[ureallyloveme](http://bobao.360.cn/member/contribute?uid=2586341479)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

传送门

[【安全报告】McAfee Labs 威胁报告 2017.06 （上）](http://bobao.360.cn/learning/detail/4090.html)

[**【安全报告】McAfee Labs 威胁报告 2017.06 （中）**](http://bobao.360.cn/learning/detail/4095.html)

**<br>**

**密码盗用程序Fareit的增长性危险 — — RaviKant Tiwari 和 Yashashree Gund**

我们生活的这个时代，越来越多的人正在越来越多地依赖于他们的个人电子设备。此趋势使得我们对保护这种依赖关系免受威胁，比以往更加重要了。信任凭据是我们的主要安全方法，因而也成为了籍此牟利的网络犯罪的主要攻击途径。

不幸的是，人类的行为是在这些关系中最薄弱的一环。大多数人只有极低安全习惯，他们在创建密码的时候不够注意，从而将自己暴露于暴力破解的攻击之中。甚至更糟糕的是，他们有时根本不去保护自己，包括根本不设置或更改默认密码等。这种行为所招致的诸如Mirai botnet的攻击，我们已在McAfee Labs威胁报表：2017年4月刊里强调过。 

云计算正在逐渐地改变着我们使用电脑的方式。各类消费者和商家越来越多地将重要的信息和服务存储到云端。然而我们却通常使用相同的认证方案，而且基于相似的人类行为弱点，去访问着那些基于云计算的信息和服务。因此，因为数据和计算资源的集中，云计算已经成为了越来越对网络犯罪分子具有吸引力的目标。

正如我们在《McAfee Labs2017年威胁预测报表》中所预见的，恶意软件以信任凭据为目标进行盗窃，其形势日趋严重，我们需要开发出更好的方法予以应对。

<br>

**使用密码盗用工具来盗窃信任凭据**

几乎所有主要的APT都会在早期阶段使用到密码盗用工具。这种类型的恶意软件增加了在整体攻击生命周期中的经济收益。网络侧恶意软件的攻击活动主要依赖于由密码盗用工具所截获到的信任凭据。

新的密码窃取类恶意软件的变种增强了其从抓取银行信任凭据到比特币和游戏币的能力。Fareit，也被称为Pony，是目前用于窃取密码的顶级恶意软件家族成员之一。它可以从超过100种包括电子邮件、FTP、即时消息、 VPN、 web 浏览器和更多的应用程序中夺取信任凭据。

以下图表显示了McAfee Labs在过去三年期间里收到的专注Fareit事件的数量。

<br>

**Fareit 客户事件**

[![](https://p2.ssl.qhimg.com/t01498e58c5d42eac46.png)](https://p2.ssl.qhimg.com/t01498e58c5d42eac46.png)

**起源**

Fareit在2011年被微软首次发现。Fareit 的稳健性和较强的功能，使之成为最受欢迎的密码窃取类恶意软件长达五年之久。

以下图表显示了从 2011年到2017 年，McAfee 和微软对Fareit的检测。

<br>

**新的Fareit检测**

[![](https://p2.ssl.qhimg.com/t01aa43a842024b3d7c.png)](https://p2.ssl.qhimg.com/t01aa43a842024b3d7c.png)

以下的热度图显示了2017 年第一季度Fareit所控制的服务器的分布。

Fareit 控制服务器的热度图

[![](https://p3.ssl.qhimg.com/t01f294f669354b31e4.png)](https://p3.ssl.qhimg.com/t01f294f669354b31e4.png)

Fareit 被跟踪到的最早版本是1.7，其中的大多数功能为如今的最新版本2.2所拥有。

Fareit（我们将把Fareit 和Pony作为此类恶意软件族的例子） 是有史以来最成功的密码窃取软件。这个成功案例已导致它在几乎所有主要的、旨在窃取敏感信息的网络攻击中被频繁使用到。

在本报表中，我们将讨论Fareit和其关联的其他恶意软件在不同平台的演化。我们还将讨论到去年秋天对民主党全国委员会 (DNC)的攻击，就可能使用到了这个“不老的”恶意软件。

<br>

**感染途径**

Fareit通过网络钓鱼/垃圾邮件、DNS投毒和漏洞套件等机制进行传播。

<br>

**垃圾邮件**

下图显示了垃圾邮件是如何传播Fareit的。受害者收到恶意的、以Word文档、JavaScript或归档文件作为附件的垃圾邮件。一旦用户打开附件，Fareit就感染到系统中。然后它下载额外的、基于其当前活动状态的恶意软件，并且将窃取到的信任凭据发送到其控制服务器上。

[![](https://p0.ssl.qhimg.com/t0104a70d72302fc5cb.png)](https://p0.ssl.qhimg.com/t0104a70d72302fc5cb.png)

<br>

**DNS 投毒**

在此技术中，诸如Rbrut的恶意软件通过暴力攻击，获取路由器的管理员访问权限。然后它更改主DNS的设置，并将被感染的系统重定向到一个“流氓”DNS 服务器上。

“流氓”DNS服务器将用户重定向到提供Fareit的恶意网站。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e5def2122edfd8f7.png)

<br>

**Bot和控制服务器的体系结构**

不同于大多数由特定的群体和集中控制服务器的僵尸网络，任何攻击者都可以从黑市网（dark web）上购买到Pony。买家搭建个人的控制服务器，以开始攻击的过程；或是购买另一个攻击者的控制面板服务。购买来的控制面板能够提供被盗的信任凭据报表。

Pony项目分为三个部分：

Pony生成器 (PonyBuilder.exe): 一组用于创建编译客户端–"Pony Bot"的程序，编译包括其调用包，它使用的是masm32编译器。

Pony Bot： 客户端必须被下载到目标系统中，来收集并将密码发送给控制服务器。

一组服务器端的PHP脚本：包括一个管理面板和脚本门 (gate.php)，用户发送窃取的密码。

[![](https://p1.ssl.qhimg.com/t01312fc392b24cc3d4.png)](https://p1.ssl.qhimg.com/t01312fc392b24cc3d4.png)

Pony生成器（Builder）： 此工具允许攻击者创建自己的Pony Bot。他们可以指定控制服务器的地址，让Bot发送窃取到的信任凭据和其他统计数据。

[![](https://p3.ssl.qhimg.com/t011093268b525bbe90.png)](https://p3.ssl.qhimg.com/t011093268b525bbe90.png)

图 1： Pony生成器的源代码文件。

[![](https://p4.ssl.qhimg.com/t018b015ab1ebe5898d.png)](https://p4.ssl.qhimg.com/t018b015ab1ebe5898d.png)

图 2： Pony生成器的用户界面。

Pony Bot： 这是网络犯罪分子用于传播恶意软件客户端的程序，可以从受害者处窃取密码。Pony Bot有几项功能：

窃取密码

下载和执行任意的恶意软件

执行 DDoS 攻击

盗取加密的货币钱包

盗取FTP的信任凭据

Pony Bot 大多是由汇编语言进行编码的，它可以释放成DLL或EXE格式。这为Fareit提供了服务于各种用途的变种，以及灵活性。

为收集密码，Pony Bot 使用了非标准的方法。在客户端启动时，它自动收集被盗密码和把必要的数据加密成特殊的容器文件，称为报告,并将它们传输到用于解密的服务器。每个报表可以包含几十个，甚至上百个密码，以及其他支持类的信息。

Pony Bot 客户端不包含任何解密算法，只用简单函数来读取文件和注册表里的数据。所有密码的解密是由 web 服务器来执行的。因为大多数加密算法占比很小，因此这并非是一个资源密集型的操作。解密服务器平均花费少于10ms的时间来处理包含一份密码的报表。

[![](https://p3.ssl.qhimg.com/t01da47674242c0bc82.png)](https://p3.ssl.qhimg.com/t01da47674242c0bc82.png)

图 3： Pony Bot 客户端的不同模块。

[![](https://p2.ssl.qhimg.com/t01da8cab585231231e.png)](https://p2.ssl.qhimg.com/t01da8cab585231231e.png)

图 4： 这些模块包含Pony Bot能够成功编译所需的必要代码。

许多攻击活动的作者都将Fareit纳入他们的攻击方法之中。例如，我们发现的Andromeda僵尸网络（也称为 Gamarue） 就将Fareit称为“神奇作者的杰作(Fareit Bot) ” 。特别是在有人请他为Andromeda创建窃取密码的程序时，Andromeda作者就会演示如何将Pony植入Andromeda的僵尸网络。

Pony的变体有着不同的目的。我们稍后将讨论Pony是如何被精心设计到DNC攻击中，以及如何仅通过封隔代码来窃取用户和FTP密码的。

<br>

**内部运作**

Fareit bot 在每个模块的开始处执行反卸载和反仿真技术。然后它初始化API地址，以执行各种不同的操作。Fareit 试图通过获取当前正在执行的、本地帐户的令牌，来模拟特权的进程。在稍后的阶段，该用户会被执行的暴力破解过程所忽略。下一步，Fareit解密已存储的单词列表，以通过使用暴力来破解受害者系统上的其他可用账户。一旦解密完成，它开始在当前用户的环境中使用ScanAndSend这一窃取例程，并将所有窃取到的信任凭据发送到控制服务器上。在那之后，它会运行bot的加载器组件，下载并执行更多的恶意软件，这会成为其“按照安装的进行支付”类型的攻击活动的一部分。

下一步，Fareit 终止其当前的模拟，进而冒充受害者系统上的其他用户。为实现这一目标，Fareit尝试着运用“username: username”和“username: lowercase username”的组合模拟该账户进行登录，最后用单词列表破译出该用户名的密码。一旦登录成功，Fareit 进程会模拟该登录的用户，再次在该额外的用户环境中执行 ScanAndSend。

[![](https://p5.ssl.qhimg.com/t01cb19d8379091b04c.png)](https://p5.ssl.qhimg.com/t01cb19d8379091b04c.png)

图 5: 暴力攻击本地用户名的部分单词列表。

<br>

**盗窃行为**

Fareit会试图窃取保存在浏览器里的密码。它也会试图窃取存储的帐号信息，如服务器名称、端口号、登录ID和从下列FTP客户端以及云存储程序里的密码：

[![](https://p1.ssl.qhimg.com/t01d0dc0ab45c045ee0.png)](https://p1.ssl.qhimg.com/t01d0dc0ab45c045ee0.png)

Fareit的执行流程

[![](https://p0.ssl.qhimg.com/t010439457229b450a1.png)](https://p0.ssl.qhimg.com/t010439457229b450a1.png)

控制面板: Pony控制面板使攻击者能够查看和管理由 bot 发送来的信息。

[![](https://p0.ssl.qhimg.com/t0129af0c87070b6103.png)](https://p0.ssl.qhimg.com/t0129af0c87070b6103.png)

图 6： 控制面板上有不同的选项卡，用以访问从Pony Bot收集到的统计数据中不同的信息。

各个选项卡能执行的功能如下：

首页：关于服务器上正在进行工作的基本信息。

FTP 列表：通过FTP/SFTP获得的下载或清除列表。

HTTP 密码：通过HTTP获得的下载或清除密码列表。

其他：接收到的、证书的下载或清除的列表。

统计数据：当前收集到的数据量。（清除FTP列表，以重置统计报表）。

域：为可访问的操作测试添加一个备用的域采集器。

日志：查看关键错误和通知的服务器。

报表：当前密码的列表。

管理：服务器设置和帐户管理。

帮助：显示由各种bot和控制面板提供的功能。

注销：从管理面板上退出。

[![](https://p5.ssl.qhimg.com/t014ec9cd20b4a1bb23.jpg)](https://p5.ssl.qhimg.com/t014ec9cd20b4a1bb23.jpg)

图 7-9： 控制服务器上，其他操作系统和新被盗取的密码相关统计。

Pony控制面板有管理员和一般用户两种模式，并允许Pony botnet作为一种服务被交付。

管理员模式可以做任何事情： 删除或添加新用户，更改服务器设置 （包括报表的加密密码），更改特权或其他用户的密码，清除各个密码的列表。当然只可以有一个管理员。

其他用户，根据他们的特权，可以查看数据 (user_view_only)，或浏览并清除FTP/SFTP列表、报表和日志。用户还可以更改他们的密码。用户不能看到那些只为管理员可用的功能。

[![](https://p0.ssl.qhimg.com/t016fbca1cf75337666.jpg)](https://p0.ssl.qhimg.com/t016fbca1cf75337666.jpg)

[![](https://p1.ssl.qhimg.com/t01c902018f8626c73a.png)](https://p1.ssl.qhimg.com/t01c902018f8626c73a.png)

图 10-11：两个销售中的Pony控制面板的示例。

<br>

**Fareit报表内容**

一个加密的报表文件包含各种被窃取的信任凭证。另外每个报表还包含额外的信息:

操作系统：Windows版本。

IP地址：发送者的地址。

HWID：不可更改的用户唯一性标识符。使用此ID，你可以在一个特定的系统中找到所有的报表。

特权：启动Pony Bot进程的权限(用户或管理员)。

架构：Pony.exe 运行在x86和32 – 64位的CPU架构。

版本：Pony Bot的客户端版本。

[![](https://p2.ssl.qhimg.com/t0167c744617cb559a4.jpg)](https://p2.ssl.qhimg.com/t0167c744617cb559a4.jpg)

图 12：来自被感染系统的、被盗取信息的报表文件所产生的攻击者视图。这些包括FTP信任凭据，浏览器、电子邮件和其他地方保存的密码。

<br>

**进化**

2011年末，微软发现和命名了新的密码盗用程序PWS：Win32/Fareit。我们认为当时的Fareit并不完整，可能还只是处于测试开发阶段。

Fareit，又名Pony的进化

[![](https://p2.ssl.qhimg.com/t015ddfcd66ec1fd55d.png)](https://p2.ssl.qhimg.com/t015ddfcd66ec1fd55d.png)

[![](https://p3.ssl.qhimg.com/t01af1a5944d694bb17.png)](https://p3.ssl.qhimg.com/t01af1a5944d694bb17.png)

[![](https://p4.ssl.qhimg.com/t01b58049dad4541fdb.png)](https://p4.ssl.qhimg.com/t01b58049dad4541fdb.png)

图 13-14：在2011年被检测到的、Fareit恶意软件的屏幕截图，它显示了从被感染的终端上窃取来的信息。

在其被发现后的不久，其作者将Fareit V1.7 在许多地下论坛上发售。它被加载了许多强大的功能，并且导致了快速成长。

<br>

**规避检测**

随着 Fareit 的进化，恶意软件作者实施了许多的反汇编和反调试技术，用以防止对bot的简单分析。

除了Fareit作者实现的、基本的规避检测机制，个别所有者还能添加诸如ASProtect和自定义的packers，以防止反恶意软件签名的检测。

反汇编： 以下是一个反汇编技术的示例，它用到了混淆递归遍历的算法，并且试图遵循程序控制流，和在某一位置上的汇编指令。

在这个片段中，"jb"指令将控制转移到地址0x41062e。反汇编程序认定此位置上包含代码，并且试图编译它。攻击者有时会在此代码的位置放置不能编译的垃圾字节，以造成编译的失败。

代码中的实际控制转移，分别通过在0x00410625和0x0041062d处的"push"和"retn"指令来实现。

[![](https://p1.ssl.qhimg.com/t0185b1fb36f50df227.jpg)](https://p1.ssl.qhimg.com/t0185b1fb36f50df227.jpg)

反仿真: Fareit 还采用反仿真来绕过许多反恶意软件的启发式检测机制。这种技术通过引入大型循环来消耗仿真的周期。先导的循环保持执行，直到计算机被启动所消耗的毫秒数除以10并非剩下5的时候。因为获得剩下值为5是一个小概率事件，因此该循环将继续拖延执行一段较长的时间。

[![](https://p2.ssl.qhimg.com/t0110bbb57bf802d0bc.png)](https://p2.ssl.qhimg.com/t0110bbb57bf802d0bc.png)

Packers:

我们已经发现有使用unique stub generation (USG)的加密器来加密Pony Bot的可执行文件，并进一步将其封装到AsProtect和自定义的Packers中。（自定义的Packers可以使用许多编译器来生成可执行的文件。常见的编译器包括Visual Basic和.Net）。我们也发现Pony Bot用AutoIt脚本来编译可执行的文件.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015ebe5c2cdcec8961.png)

图 15： 我们发现USG 加密器为新用户标价45美元，以及25美元每月的续费服务。

<br>

**DNC 攻击**

2016 年美国民主党全国委员会（DNC）的泄漏事件已认定是名为Grizzly Steppe恶意软件所为。

Grizzly Steppe的目标常是政府组织、关键基础设施公司、智囊团、政治组织，以及世界各地的公司。它使用缩写网址、鱼叉式网络钓鱼、横向移动和提升特权的战术，来感染系统和网络。

根据已公布的报告，Grizzly Steppe的攻击分为两个阶段。2015年，它通过鱼叉式钓鱼攻击发送恶意链接，以重定向到恶意软件的下载。然后在 2016 年，它通过山寨的假域名，诱使人们更改密码。信任凭据和其他信息（包括电子邮件）就从受害者的系统中被窃取，并公布在了公共领域上。

在美国政府公布的Grizzly Steppe报表中，我们从攻击特征指示列表里发现了Fareit的散列。

[![](https://p5.ssl.qhimg.com/t010eafe10978b088f5.png)](https://p5.ssl.qhimg.com/t010eafe10978b088f5.png)

Fareit很可能与DNC攻击的其他技术一起被使用，来窃取电子邮件、FTP和其他重要的信任凭据，以用于进一步的攻击。

我们怀疑，Fareit也被用来下载Onion Duke和Vawtrak之类的APT威胁到受害者的系统上，以进行进一步的攻击。我们发现了被Fareit的加载组件所用于下载并执行的如下URLs：



```
hxxp://one2shoppee.com/system/logs/xtool.exe
hxxp://insta.reduct.ru/system/logs/xtool.exe
hxxp://editprod.waterfilter.in.ua/system/logs/xtool.exe
```

通过分析，我们发现Fareit恶意软件在被Word恶意文档访问到的时候，特别适用于DNC攻击。而这些文件经常是通过钓鱼类电子邮件在网上被广泛传播的。

下面是被发现的很可能被用于DNC攻击的Fareit 样本，其代码显示了信任凭据盗取类型的子程序或模块。在此示例中，信任凭据盗取模块的数量明显低于大多数的Fareit样本。攻击者可能已经得出结论：其中一些与这种攻击毫不相干。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019d07f798bd04408b.png)

图 16：可能被用于DNC攻击的Fareit 样本，它包含信任凭据盗取类模块的硬编码地址。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cadfc2e9ad534579.png)

图17：自然的信任凭据盗取类模块。

[![](https://p2.ssl.qhimg.com/t011269444c4a7521b8.png)](https://p2.ssl.qhimg.com/t011269444c4a7521b8.png)

图18：这段代码调用了图12里的所有信任凭据盗取类型的子程序。该代码虽不是DNC攻击里特有的Fareit样本，但它在其他Fareit样本中很常见。

<br>

**在 DNC 攻击中的网络活动**

让我们来看两段在DNC攻击中可能使用到的Fareit样本代码。每个控制服务器的地址被一个循环所调用，它会检查控制服务器响应中的"STATUS-IMPORT-OK"字符串。如果未收到此响应，该循环将去往下一个URL。

[![](https://p5.ssl.qhimg.com/t019e3fa1658350bdcb.png)](https://p5.ssl.qhimg.com/t019e3fa1658350bdcb.png)

图 19：该子程序被发现来自可能被用于DNC攻击的Fareit 样本。它负责在当前的URL无响应时连接到不同控制服务器。

可能被用于DNC攻击的Fareit恶意软件会引用那些在自然情况下不常被观察到的多个控制服务器地址：



```
hxxp://wilcarobbe.com/zapoy/gate.php
hxxp://littjohnwilhap.ru/zapoy/gate.php
hxxp://ritsoperrol.ru/zapoy/gate.php
```

[![](https://p2.ssl.qhimg.com/t0180aff649b913101a.png)](https://p2.ssl.qhimg.com/t0180aff649b913101a.png)

图 20： 该子程序被发现来自可能被用于DNC攻击的Fareit 样本。它被用于下载其他的恶意软件。

可能被用于DNC攻击的Fareit恶意软件从如下位置下载额外的恶意软件：



```
hxxp://one2shoppee.com/system/logs/xtool.exe
hxxp://insta.reduct.ru/system/logs/xtool.exe
hxxp://editprod.waterfilter.in.ua/system/logs/xtool.exe
```



**策略和流程**

你可以采取如下的步骤，以避免来自Fareit等方面的威胁。

创建复杂的密码，并定期更换。密码越长越多样化，它就越安全。密码可以包括数字、大写字母、小写字母和特殊字符。我们还建议每年更改密码两到三次，并在任何泄漏发生后立即修改。如果此举听起来太难跟进的话，请考虑使用密码管理工具。

不同的帐号或服务使用不同的密码。这将阻止在一个帐号被盗后，它对其他帐号和服务的访问。

采用多因素的身份验证。在帐号发生泄漏时，攻击者只有在下一个身份验证因素被核实后，才能访问该帐号。

不在公共电脑上进行任何需要密码的操作。 避免在咖啡厅、 图书馆或其他无线上网的公共场所使用系统，因为这些网络很容易受到击键记录类软件与其他类型恶意软件的攻击。

打开邮件附件时要格外小心。 这是一个大“坑”！不要打开任何“长相奇怪”的附件，也不要点击从可疑或未知发件人发来的链接。即使是来自朋友的附件或链接，也请确保在点开之前，那些电子邮件或社交网络不是从此人已被攻击的帐号所发出的。

在所有设备上安装全面安全防御。持续更新安全软件是最佳的安全实践。 这个简单的步骤会大幅减少被Fareit或其他恶意软件感染的机会。

<br>



传送门

[【安全报告】McAfee Labs 威胁报告 2017.06 （上）](http://bobao.360.cn/learning/detail/4090.html)

[**【安全报告】McAfee Labs 威胁报告 2017.06 （中）**](http://bobao.360.cn/learning/detail/4095.html)

<br>
