> 原文链接: https://www.anquanke.com//post/id/87086 


# 【技术分享】HydraPOS活动：巴西黑客已经收集了至少140万信用卡数据


                                阅读量   
                                **79723**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：tempestsi.com
                                <br>原文地址：[https://sidechannel.tempestsi.com/hydrapos-operation-of-brazilian-fraudsters-has-accumulated-at-least-1-4-million-card-data-b05d88ad3be0](https://sidechannel.tempestsi.com/hydrapos-operation-of-brazilian-fraudsters-has-accumulated-at-least-1-4-million-card-data-b05d88ad3be0)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01c32c109841c8e20c.png)](https://p4.ssl.qhimg.com/t01c32c109841c8e20c.png)

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**写在前面的话**

****

网络犯罪领域目前正在经历着大规模攻击武器逐渐积累增长的过程，这些大规模网络攻击武器一般都与国家和政府有关，他们往往会使用这些网络武器来进行网络间谍活动。

在某些情况下，你可能会认为那些只是电影里的场景，现实中并不存在，但事实并非你所想象的那样，电影中的场景也有可能出现在你的现实生活里。比如说之前曾掀起轩然大波的方程式组织（**Equation Group**），作为一个情报机构，他们不仅会使用大规模攻击工具以及高质量的恶意软件来进行网络间谍活动，而且还会有针对性地窃取目标的支付卡数据。

<br>

**HydraPOS活动被发现**

****

在一次常规的安全分析过程中，安全公司Tempest的威胁情报团队发现了一系列恶意软件样本。乍看之下，这些恶意软件似乎与一个针对巴西商人的普通攻击活动（**利用了POS系统**）有关。大家需要注意的是，这有可能是攻击者所采用的一种策略，因为某些有特殊目的的攻击者会利用看似平常的攻击活动来掩盖自己的大规模网络攻击。研究人员在进行了进一步挖掘之后，终于发现了他们的主要活动：在这四年里，他们不仅**收集了数十款网络攻击工具以及上百款恶意软件**，而且他们还积累了超过140万条支付卡数据，其中包括信用卡、借记卡和购物礼品卡等等。

Tempest的研究人员将此恶意活动标记为了**HydraPOS**，这个活动的目的非常多。在攻击的初始阶段，HydraPOS的目的是通过利用超市系统的漏洞来收集支付卡数据。但是随着时间的推移，HydraPOS开始将银行数据以及电子商务访问凭证添加进了自己的“目标名单”之中。

HydraPOS活动中涉及到了多款恶意软件，这些恶意软件拥有好几百种不同的构建版本，其中最著名的第三方恶意软件工具当属Kaptoxa（又名[Trojan.POSRAM](http://artemonsecurity.com/20140116_POS_Malware_Technical_Analysis.pdf)），而这款工具曾在2014年攻击了大型零售商塔吉特公司。除此之外，HydraPOS恶意活动所使用的其他恶意程序至今尚未公布。

<br>

**感染技术细节**

****

HydraPOS所使用的恶意软件感染技术是基于大规模扫描实现的，这种方式通常会涉及到巴西电信通讯公司整个宽带服务的覆盖范围。该活动所使用的扫描工具为**VNC-Scanner**（或由攻击者开发的其他功能类似的软件），这些工具可以搜索包含错误配置的常用远程访问服务以及已过期的软件版本，例如VNC、RDP、Radmin和SSH。攻击者一般会对这一阶段中所识别出的目标进行暴力破解攻击（或利用已知漏洞进行攻击）以获取访问密码。除此之外，HydraPOS背后的操作者还会使用网络钓鱼攻击来感染目标用户。

<br>

**HydraPOS能对目标网络做什么？**

****

当攻击者获取到目标用户计算机的访问权之后，HydraPOS攻击者可以使用多种方法来安装新型恶意软件并提取数据。除此之外，他们还可以实现对目标系统环境的持久化感染。

利用远程管理工具与目标系统建立网络连接还允许他们对目标系统进行各种非法操作，但具体所能执行的活动还取决于攻击者所能拿到的访问权限等级。

当攻击者通过钓鱼攻击来实现感染payload时，需要将恶意文件发送给目标用户，然后激活恶意软件，之后攻击者就可以通过远程桌面（以管理员权限）开启一条通信信道并实现其他的恶意操作。

HydraPOS所使用的钓鱼信息样本如下图所示：

[![](https://p3.ssl.qhimg.com/t012d655b8ddb0648d6.png)](https://p3.ssl.qhimg.com/t012d655b8ddb0648d6.png)

根据不同目标环境的特性，最新版本HydraPOS代码的逻辑定义了具体使用哪一款工具来收集访问凭证以及支付卡数据。研究人员通过分析之后，已经发现了Kaptoxa恶意软件（可以在目标计算机进行资金交易的过程中从内存提取数据）从2013年开始所收集到的数据集，**而这些数据早已在暗网论坛中被出售了**。

虽然在交易通信处理的过程中，支付卡数据是经过加密的，但POS软件本身就需要对交易认证过程中的信息进行解密。像Kaptoxa这种专门收集内存数据的恶意软件，就是用来帮助攻击者确定最有价值的信息到底位于内存中的哪一个部分。这样一来，这种恶意软件就可以在获取到有价值的数据之后将它们保存在文件中，然后发送给攻击者的命令控制（C&amp;C）服务器。

但是研究人员还发现，在HydraPOS近期的攻击活动中，内存数据收集的行为似乎已经整合进了HydraPOS的代码之中，这也就意味着攻击者对于Kaptoxa的依赖将会减少，甚至会彻底抛弃Kaptoxa。

HydraPOS还使用了其他的第三方恶意软件来收集数据，例如“**Track 2 sniier.exe**”（一款键盘记录工具和内存数据收集工具）。除此之外，攻击者还是用了自己开发的恶意软件，例如名叫“**pdv.exe**”的键盘记录器、文件名为“**explorer.exe**”的内存收集工具和文件名为“**win.exe**”的电子商务凭证收集器。

这些恶意软件可以直接将收集到的数据发送到攻击者的命令控制服务器，也可以通过电子邮件或根据攻击者的远程指令来进行发送，具体取决于目标系统的环境以及架构。

<br>

**命令控制服务器（C&amp;C）**

****

Tempest的威胁情报团队已经发现了七台攻击者在HydraPOS活动中所使用的服务器，其中有一部分存储了1,454,291条支付卡数据记录，而最早的记录收集于2015年。因此，HydraPOS活动所收集到的支付卡数据数量可能会更加庞大，而根据开源情报数据和调查显示，有证据可以证明HydraPOS攻击活动至少从2013年就已经开始了。

其他的C&amp;C服务器中包含有攻击者所使用的网络武器，其中包括远程管理工具、暴力破解工具以及用于收集电子邮件地址的工具等等。除此之外，服务器中还存储了HydraPOS攻击者自行研发的工具，例如“FindInfoTxt”（该工具可根据服务码来对支付卡数据进行归类，并筛选出额度最高的以及最容易攻击的支付卡）以及“Gerenciador Sitef”（该工具可以检测受感染系统的状态并向其发送控制命令，功能类似一个管理后台）。

Gerenciador Sitef的运行界面如下图所示：

[![](https://p2.ssl.qhimg.com/t015ebca4ec33efb62f.png)](https://p2.ssl.qhimg.com/t015ebca4ec33efb62f.png)

有关HydraPOS武器库的更多详细数据请参考本文末尾给出的附录。

<br>

**附录 &amp; IoC**

****

**攻击者所使用的合法远程管理工具**

-RealVNC: 客户端/ 服务器端VNC.

-ThighVNC: 客户端/ 服务器端VNC.

-NVNC: 服务器端VNC.

-Ammyy: 客户端/ 服务器端（用于远程管理）

-Bitvise: 客户端/ 服务器端SSH.

**第三方恶意工具**

-VNC-Scanner:搜索存在VNC漏洞的设备，并利用漏洞实施攻击。

-Fast RDP Brute: 使用暴力破解攻击获取RDP系统的访问凭证。

-VUBrute: 使用暴力破解攻击获取VNC系统的访问凭证。

-DUBrute: 使用暴力破解攻击获取RDP系统的访问凭证。

-LameScan: 使用暴力破解攻击获取Radmin系统的访问凭证。

-Advanced IP Scanner: 针对RDP和Radmin系统的网络扫描器及木马安装器。

-Sanmao Email Collector: 收集网站中的电子邮件地址。

-Sanmao Email Scraper: 收集扫描工具中的电子邮件地址。

-Sanmao SMTP Mail Cracker: 针对电子邮件的暴力破解工具。

**HydraPOS攻击者开发的工具**

-FindInfoTxt：根据服务码（Service Code）对支付卡数据进行分类，可提取银行识别码（BIN），**VirusTotal目前还无法检测到**。

**MD5:**

3d05a4d2ddf9fa1674579b15d5980c26

**SHA1:**

24ce8i328b44658f0db21dac25f109c57eeea5e

**SHA256:**

d88b82e936adf47778826dd23886c9288e807f389a242bfb5a0f6e4fdc8674ac

-Gerenciador Sitef:可对受感染主机进行实时分析与监控的控制面板，并且还可以向目标主机发送控制命令，**VirusTotal目前还无法检测到**。

**MD5:**

e4755ce3c7ee50a08a8902e9fa978588

9f82da18f8591749e212efe6dccca45b

7c513ea612f05774593c916487791bb7

31dbef6f3027a4048d8dabc756172043

a172ebf8d867282027db1ef0cd08a815

8805d1d9530c1b9943d1089715e81faf

**SHA1:**

903e41db1daa11665b28d06e8b7a417e367b5fe9

637820e583b5de7f17fa674341e2fc0448269758

f809c37bb465a69d37b46cfb902ef9336c3bef19 fce01e84cdca3315e1955ec7a97261546a530ca7

c29e69d088f6836506d529d51dbd6960f6e173c2

385026cc6e70621820db13d475a24292aa72bdeb

**SHA256:**

90d0ccb265b27fe8e656058927e044424652c9086e42f93fdb112

744e5ea4170

bca53f93de2ad7421781190846ba9e980e1fcfc6b9d9e9dfbb8bb9

0c142b7510

bba21698e0463cf11cb4ee3c50b85be3cc435ccbf3d95a42e866dc

6afc1c4426

c336a423dce1a1a9189d4dd1810f91d2556eac89df3b2a9988052

30104f1cfb0

fbda9405800022dfb2fb774812204dc757b56857c646c65e6d60

3ib7bd38066

3a654e636c27b724398a878dcab074888870d7fa97208bca1caf2

5cideb7078

-LRemoto：可对受感染主机中的恶意软件进行下载更新，**VirusTotal目前还无法检测到**。

**MD5:**

331b0647df20c7522ceee719a040bacc

f4792f398c11f658247ee1a74f4edb49

**SHA1:**

a0957bf849a3095767abe42fb38404c245290dca

78b0c3a3b8290f94689b4d29dd24b29b260113a1

**SHA256:**

9df8233c78ced7e05d8a55781378901091d364ccdfb6b9d25a6e1

8eb7a72d9c4

6e7cd73ddad3644dd3b485857040d8d300323941e5712304c53f

a5118feab871

HydraPOS攻击者开发的恶意软件

Adobe.exe：支付卡数据及电子商务凭证收集器。

**MD5:**

bd0aca51fbde462328cafab83dd9d619

**SHA1:**

b9a2c27b9e72c6ee38927f2a8ba9bf20725dbic

**SHA256:**

8709cc4ee0a0c3040a173f58521dda0fe436af7e0fbb69f59169ceb

bf3c1ddac

pdv.exe：键盘记录器，VirusTotal目前还无法检测到。

**MD5:**

8c745dd89a6de372a49fe9faa6d614a2

**SHA1:**

7d1d7a490ba1362d90dc569d2471af56b38ac8b0

**SHA256:**

5bf208da4e4bb3a1c6403f370badb30f50ic0d26b11744bb66d34

50a68e51fd

explorer.exe：进行内存数据收集的恶意软件。

**MD5:**

d4127862bf705de3debbdbce99b70bed

**SHA1:**

54f10b1c505183459b47da596a02863de619a22d

**SHA256:**

d1255ac2458c778de0268281ea2f2e54b55af69418aa86f8ba3f61

a746cc9988

Anexo Pdf（167371371）.exe：可下载或激活其他的恶意软件。

**MD5:**

8b0fb09fb1ed82a88e9e5f1e69823afa

**SHA1:**

3d28362bde5f1e99131a2107df80462a58fa00f7

**SHA256:**

2a2af38cbfa51d56aa7bebb357825d8e661a532e043ef614bf9c47

3df6a8e8b8

**IP地址**

66[.]220[.]9[.]50—端口: 21/TCP

216[.]244[.]71[.]135—端口: 1/TCP

216[.]244[.]95[.]10—端口: 1和7

**命令控制服务器URL**

hxxp://m4godoc.esy.es

hxxp://envioip.esy.es

hxxp://infectbbb.esy.es

hxxp://www.gidlinux.ninja
