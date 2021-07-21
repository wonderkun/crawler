> 原文链接: https://www.anquanke.com//post/id/149119 


# Olympic Destroyer仍旧活跃


                                阅读量   
                                **82350**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securelist.com
                                <br>原文地址：[https://securelist.com/olympic-destroyer-is-still-alive/86169/](https://securelist.com/olympic-destroyer-is-still-alive/86169/)

译文仅供参考，具体内容表达以及含义原文为准

#### [![](https://p5.ssl.qhimg.com/t0168eb81d0207f9d41.jpg)](https://p5.ssl.qhimg.com/t0168eb81d0207f9d41.jpg)



2018年3月，我们发表了一篇关于[Olympic Destroyer的研究](https://securelist.com/olympicdestroyer-is-here-to-trick-the-industry/84295/)，它是攻击了在韩国平昌举办的2018年冬奥会的组织者、供应商和合作伙伴的高级威胁攻击。Olympic Destroyer是基于破坏性网络蠕虫传播的网络破坏(cyber-sabotage)攻击。在破坏开始之前，Olympic Destroyer会进行侦察并渗透到目标网络中以选择用于自我复制和自我修改的破坏性恶意软件的最佳启动板。

我们之前强调过，Olympic Destroyer的故事与其他威胁者的故事不同，因为整个攻击是一场精心策划的欺骗行为。尽管如此，攻击者仍犯下了一些严重的错误，这些错误使我们发现并证明伪造罕见的归属物。Olympic Destroyer背后的攻击者伪造自动生成的签名——Rich Header，并使其看起来像是由被广泛认为与朝鲜有关的攻击者Lazarus APT组织制作的恶意软件。如果您对Rich Header觉得很陌生，我们建议阅读另一个专门分析这种伪造行为的[博客](https://securelist.com/the-devils-in-the-rich-header/84348/)。

我们注意到，Olympic Destroyer的欺骗行为，以及过度使用各种假flag来欺骗了信息安全行业的许多研究人员。根据恶意软件的相似性，Olympic Destroyer恶意软件被其他研究人员与三名讲中文的APT攻击者和据称是朝鲜Lazarus APT的人联系在一起; 一些代码有EternalRomance漏洞的exp的迹象，而其他代码与Netya（[Expetr / NotPetya](https://securelist.com/schroedingers-petya/78870/)）和[BadRabbit](https://securelist.com/bad-rabbit-ransomware/82851/)目标勒索软件类似。卡巴斯基实验室设法找到横向移动工具和最初的感染后门，并且追逐了其中一名被Olympic Destroyer控制的韩国受害者的基础设施。

Olympic Destroyer使用的一些TTP和操作安全性与[Sofacy APT组织活动](https://securelist.com/a-slice-of-2017-sofacy-activity/83930/)有一定的相似性。说到这些错误的flag，模仿TTP比用技术进行篡改要困难得多。这意味着对模仿攻击者的操作以及对这些新TTP的操作适应都需要有深刻的知识背景。然而，重要的是要记住，Olympic Destroyer可以被视为使用虚假flag的大师：现在我们用低信度和中信度来评估这种联系。<br>
我们决定继续跟踪这个团队，并设置了我们的虚拟“网络”，以企图在Olympic Destroyer出现类似的资源库时再次追捕它。但令我们惊讶的是，它最近又出现了新的活动。

在2018年5月至6月，我们发现了新的鱼叉式钓鱼文件，这些文件与Olympic Destroyer过去使用的武器文件非常相似。这些文件和其他TTP让我们相信我们又一次看到了同一个攻击者。但是，这次攻击者有新的目标。根据我们的遥测和对鱼叉式网络钓鱼文件的特点分析，我们认为Olympic Destroyer背后的攻击者这次针对的是俄罗斯的金融机构以及欧洲和乌克兰的生化威胁预防实验室。他们继续使用非二进制可执行感染向量和混淆脚本来逃避检测。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071536/olympic-destroyer-is-still-alive_01.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071536/olympic-destroyer-is-still-alive_01.png)

简化后的感染过程



## 感染分析

实际上，感染过程稍微复杂一些，而且依赖于多种不同的技术，它将VBA代码，Powershell，MS HTA，JScript和其他Powershell混合在一起。让我们更仔细地研究一下，让事件响应者和安全研究人员在将来的任何时候都能识别出这种攻击。

我们发现的最近文件之一有以下属性：

MD5：0e7b32d23fbd6d62a593c234bafa2311<br>
SHA1：ff59cb2b4a198d1e6438e020bb11602bd7d2510d<br>
文件类型：Microsoft Office Word<br>
最后保存的日期：2018-05-14 15:32:17（GMT）<br>
已知文件名：**Spiez CONVERGENCE.doc**

嵌入式宏被严重混淆。它有一个随机生成的变量和函数名称。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071540/olympic-destroyer-is-still-alive_02.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071540/olympic-destroyer-is-still-alive_02.png)

混淆后的VBA宏

其目的是执行Powershell命令。这个VBA代码用到的混淆技术和Olympic Destroyer鱼叉式网络钓鱼攻击中使用的相同。

它通过命令行启动一个新的混淆的Powershell脚本。混淆器使用基于数组的重新排列来改变原始代码，并保护所有命令和字符串，例如命令和控制（C2）服务器地址。

有一种已知的混淆工具可以产生这样的效果：Invoke-Obfuscation。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071545/olympic-destroyer-is-still-alive_03.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071545/olympic-destroyer-is-still-alive_03.png)

混淆的命令行Powershell脚本

此脚本禁用Powershell脚本日志记录以避免留下痕迹：

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/20140034/olympic-destroyer-is-still-alive_sc-1.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/20140034/olympic-destroyer-is-still-alive_sc-1.png)

它具有内联实现的Powershell中的RC4例行程序，该程序用于解密从Microsoft OneDrive下载的额外payload。解密依赖于硬编码的32字节ASCII十六进制字母表密码。这是在过去的其他Olympic Destroyer鱼叉式网络钓鱼文件和位于平昌的Olympic Destroyer受害者基础设施中发现的Powershell后门中都可见到的熟悉的技术。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/20140038/olympic-destroyer-is-still-alive_sc-2.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/20140038/olympic-destroyer-is-still-alive_sc-2.png)

下载的第二阶段payload是一个HTA文件，它也执行Powershell脚本。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071554/olympic-destroyer-is-still-alive_04.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071554/olympic-destroyer-is-still-alive_04.png)

已下载的access.log.txt

该文件具有与由矛型钓鱼附件中宏执行的Powershell脚本类似的结构。在对其进行反混淆后，我们可以看到该脚本还会禁用Powershell日志记录，并从相同的服务器地址下载下一阶段的payload。它还使用RC4和预定义的密码：

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/20140043/olympic-destroyer-is-still-alive_sc-3.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/20140043/olympic-destroyer-is-still-alive_sc-3.png)

最终的payload是Powershell Empire代理。下面我们会提供一部分下载的Empire代理的http stager scriptlet。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/20140046/olympic-destroyer-is-still-alive_sc-4.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/20140046/olympic-destroyer-is-still-alive_sc-4.png)

Powershell Empire是一个利用Python和Powershell编写的免费开源框架，允许对被感染主机进行无文件控制，它具有模块化体系结构并依赖于加密通信。渗透测试公司在横向移动和信息收集的合法安全测试中曾广泛使用该框架。



## 基础设施

我们认为攻击者使用受损的合法Web服务器来托管和控制恶意软件。根据我们的分析，发现的C2服务器的URI路径包括以下路径：
- /components/com_tags/views
- /components/com_tags/views/admin
- /components/com_tags/controllers
- /components/com_finder/helpers
- /components/com_finder/views/
- /components/com_j2xml/
- /components/com_contact/controllers/
这些是流行的开源内容管理系统[Joomla](https://github.com/joomla/joomla-cms)使用的已知目录结构：

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071558/olympic-destroyer-is-still-alive_05.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071558/olympic-destroyer-is-still-alive_05.png)

Github上的Joomla组件路径

不幸的是，我们不知道在Joomla CMS中究竟利用了哪些漏洞。众所周知的是，其中一个payload托管服务器使用Joomla v1.7.3，这是该软件于2011年11月发布的一个非常老的版本。



## 受害者和目标

根据多个目标概况和有限的受害者报告，我们认为Olympic Destroyer最近的行动针对了俄罗斯，乌克兰和其他几个欧洲国家。根据我们的遥测数据，一些受害者是来自俄罗斯金融部门的实体。此外，我们发现的几乎所有样本都上传到来自欧洲国家（如荷兰，德国和法国）以及乌克兰和俄罗斯的批量扫描服务器。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19094736/OlympicDestroyer_still_alive_infographic.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19094736/OlympicDestroyer_still_alive_infographic.png)

最近Olympic Destroyer袭击目标的位置分布

由于我们的可视性有限，因此我们只能根据所选诱饵文档的内容，电子邮件主题或攻击者挑选的文件名所提供的配置文件推测潜在目标。

以下这样一个诱饵文件引起了我们的注意，它提到了由[SPIEZ LABORATORY](https://www.labor-spiez.ch/en/lab/)组织的瑞士举办的生化威胁研究会议’Spiez Convergence’，该会议不久前参与了[索尔兹伯里袭击事件调查](https://www.theguardian.com/uk-news/2018/apr/15/salisbury-attack-russia-claims-chemical-weapons-watchdog-manipulated-findings)。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071617/olympic-destroyer-is-still-alive_08.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071617/olympic-destroyer-is-still-alive_08.png)

Decoy文档使用了Spiez Convergence主题

在攻击中观察到的另一个诱饵文档（’Investigation_file.doc’）提到了用于毒害Sergey Skripal和他在索尔兹伯里的女儿的神经毒剂：

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071624/olympic-destroyer-is-still-alive_09-780x1024.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071624/olympic-destroyer-is-still-alive_09-780x1024.png)

其他一些鱼叉式钓鱼文件的名称中包括俄文和德文的文字：
- 9bc365a16c63f25dfddcbe11da042974 Korporativ.doc
- da93e6651c5ba3e3e96f4ae2dd763d94 Korporativ_2018.doc
- e2e102291d259f054625cc85318b7ef5 E-Mail-Adressliste_2018.doc
其中一份文件包括一张带有完全的俄语的诱饵图片。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071631/olympic-destroyer-is-still-alive_10.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071631/olympic-destroyer-is-still-alive_10.png)

俄语中的消息鼓励用户启用宏（54b06b05b6b92a8f2ff02fdf47baad0e）

其中一份最新的武器文件被上传到来自乌克兰的恶意软件扫描服务器中，文件名为’nakaz.zip’，其中包含’nakaz.doc’（乌克兰语翻译为’order.doc’）。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071638/olympic-destroyer-is-still-alive_11.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071638/olympic-destroyer-is-still-alive_11.png)

另一个鼓励用户启用宏的诱导消息

根据元数据，该文件于6月14日进行了编辑。本文和以前的文件中的Cyrillic信息都是完全的俄文，表明它可能是在母语人士的帮助下编写的，而不是自动翻译软件。

一旦用户启用宏，就会显示最近从乌克兰国家机构获取的诱饵文件（日期显示2018年6月11日）。该文件的文本与乌克兰卫生部[官方网站](http://moz.gov.ua/article/ministry-mandates/nakaz-moz-ukraini-vid-11062018--1103-pro-vnesennja-zmin-do-rozpodilu-likarskih-zasobiv-dlja-hvorih-u-do--ta-pisljaoperacijnij-period-z-transplantacii-zakuplenih-za-koshti-derzhavnogo-bjudzhetu-ukraini-na-2016-rik)上的相同。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071644/olympic-destroyer-is-still-alive_12.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071644/olympic-destroyer-is-still-alive_12.png)

对其他相关文件的进一步分析表明，本文件的目标是在生物和流行威胁预防领域开展工作。



## 归属

虽然不全面，但以下的发现可以作为寻求这一运动与以往Olympic Destroyer活动之间更好联系的提示。更多重叠和可靠追踪Olympic Destroyer攻击的信息可订阅巴斯基智能报告服务（参见下文）。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071651/olympic-destroyer-is-still-alive_13.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071651/olympic-destroyer-is-still-alive_13.png)

类似的混淆宏结构

上面的文档显示出明显的结构相似性，好像它们是由同一个工具和混淆器生成的一样。新一轮的攻击中突出显示的函数名称实际上并不新鲜，虽然也不常见，但在Olympic Destroyer鱼叉钓鱼文件（MD5：5ba7ec869c7157efc1e52f5157705867）中也找到了名为“MultiPage1_Layout”的函数。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071657/olympic-destroyer-is-still-alive_14.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/06/19071657/olympic-destroyer-is-still-alive_14.png)

旧版活动中使用过的相同MultiPage1_Layout函数名称



## 结论

尽管对Olympic Destroyer最初的预测是会保持在低水平活跃度甚至消失，但它已经在欧洲、俄罗斯和乌克兰的全新攻击中重新出现。2017年底，一个较大的网络破坏行为之前发生过类似的侦察行为，企图摧毁和瘫痪冬季奥运会的基础设施以及相关供应链、合作伙伴甚至会场的场地。可能在这种情况下，我们已经观察到了一个侦察行为，接下来可能会是一系列具有新动机的破坏性攻击。这就是为什么欧洲所有生物化学威胁预防和研究的公司或组织都必须加强其安全性并开展不定期的安全审计。

各种各样的财务和非财务目标可能表明相同的恶意软件被多个利益不同的组织使用，也就是说，一个组织主要通过网络窃取金钱，而另一个或多个组织却对寻找间谍活动目标感兴趣。这也可能是网络攻击外包的结果，这在国家之间的攻击体系中并不罕见。另一方面，财务目标可能是另一个在平昌奥运期间已经擅长这一点的攻击者的虚假flag操作，以重新引导研究人员的注意力。

根据攻击动机和本次活动的目标选择可以得出一些结论，然而，当试图在只有研究人员可以看到一些图片碎片的情况下试图回答这个活动背后的攻击者的身份会很难。今年年初，Olympic Destroyer以其复杂的欺骗行为出现，永远地改变了归属游戏。我们认为，不可能根据定期调查中发现的少数归属媒介就得出结论。对Olympic Destroyer等威胁的抵制和威慑应以私营部门与跨国界政府之间的合作为基础。但不幸的是，目前世界上的地缘政治局势只会推动互联网的全球分化，并为研究人员和调查人员带来更多障碍，这也将鼓励APT袭击者继续进入外国政府和商业公司的受保护网络。

作为研究人员，我们可以做的最好的事情就是继续追踪这样的威胁。我们将继续对Olympic Destroyer进行监测，并报告新发现的关于该组织的活动。

卡巴斯基智能报告服务的用户可以获得有关Olympic Destroyer和相关活动的更多详细信息。联系方式：<a>intelreports@kaspersky.com</a>



## IoC

### <a class="reference-link" name="%E6%96%87%E4%BB%B6Hash"></a>文件Hash

9bc365a16c63f25dfddcbe11da042974 Korporativ .doc da93e6651c5ba3e3e96f4ae2dd763d94 Korporativ_2018.doc 6ccd8133f250d4babefbd66b898739b9 corporativ_2018.doc abe771f280cdea6e7eaf19a26b1a9488 Scan-2018-03-13.doc.bin b60da65b8d3627a89481efb23d59713a Corporativ_2018.doc b94bdb63f0703d32c20f4b2e5500dbbe bb5e8733a940fedfb1ef6b0e0ec3635c recommandation.doc 97ddc336d7d92b7db17d098ec2ee6092 recommandation.doc 1d0cf431e623b21aeae8f2b8414d2a73 Investigation_file.doc 0e7b32d23fbd6d62a593c234bafa2311 Spiez CONVERGENCE.doc e2e102291d259f054625cc85318b7ef5 E-Mail-Adressliste_2018.doc 0c6ddc3a722b865cc2d1185e27cef9b8 54b06b05b6b92a8f2ff02fdf47baad0e 4247901eca6d87f5f3af7df8249ea825 nakaz.doc

### <a class="reference-link" name="%E5%9F%9F%E5%90%8D%E5%92%8CIP"></a>域名和IP

79.142.76[.]40:80/news.php 79.142.76[.]40:8989/login/process.php 79.142.76[.]40:8989/admin/get.php 159.148.186[.]116:80/admin/get.php 159.148.186[.]116:80/login/process.php 159.148.186[.]116:80/news.php **<strong>.**</strong>.edu[.]br/components/com_finder/helpers/access.log **<strong>.**</strong>.edu[.]br/components/com_finder/views/default.php narpaninew.linuxuatwebspiders[.]com/components/com_j2xml/error.log narpaninew.linuxuatwebspiders[.]com/components/com_contact/controllers/main.php mysent[.]org/access.log.txt mysent[.]org/modules/admin.php 5.133.12[.]224:333/admin/get.php

审核人：yiwang   编辑：少爷
