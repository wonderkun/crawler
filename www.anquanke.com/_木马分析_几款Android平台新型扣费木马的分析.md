> 原文链接: https://www.anquanke.com//post/id/86726 


# 【木马分析】几款Android平台新型扣费木马的分析


                                阅读量   
                                **100293**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securelist.com
                                <br>原文地址：[https://securelist.com/wap-billing-trojan-clickers-on-rise/81576/](https://securelist.com/wap-billing-trojan-clickers-on-rise/81576/)

译文仅供参考，具体内容表达以及含义原文为准

 [![](https://p2.ssl.qhimg.com/t01a3c07373e8650e5a.png)](https://p2.ssl.qhimg.com/t01a3c07373e8650e5a.png)



译者：[blueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**简介**

****

在编写“[2017年第二季度IT威胁与演变](https://securelist.com/it-threat-evolution-q2-2017/79354/)”报告的过程中，我发现“前20名移动恶意软件程序”列表中有几种常见的木马程序，这些木马程序使用[WAP计费服务](https://en.wikipedia.org/wiki/WAP_billing)（WAP计费是一种移动支付形式，通过话费的形式直接生成用户手机账单）的方式从用户的账户窃取资金。在这种情况下，木马软件不需要发送任何的短信，用户只要[点击](https://securelist.com/threats/trojan-clicker/?utm_source=securelist&amp;utm_medium=blog)网页上的按钮木马软件就会产生WAP计费。

从用户的角度来看，具有WAP计费的页面跟常规的网页看起来没什么区别，通常这些页面都包含一个按钮以及关于付款的完整信息。通过点击此按钮，用户将被重定向到移动网络运营商服务器，该服务器会给用户显示一些其他网页信息，用户最终通过点击网页上的另一个按钮来决定是否向运营商付款。如果用户通过移动数据连接到互联网，移动网络运营商可以通过IP地址识别他/她，移动网络运营商只有在成功识别并且点击按钮后才向用户收费。从计费的角度来看，这种机制类似于短信服务-收费是直接通过用户电话账单的形式收取。然而，在这种情况下，木马软件是不需要发送任何短信的，只要用户点击网页上的按钮，木马便开始WAP计费。

我们已经很长时间没有捕获到这样的木马样本了，但有几个木马软件在这段时间却突然出现，几乎在同一时间，来自不同网络犯罪团体的不同特洛伊木马针对不同国家（俄罗斯和印度）展开了网络攻击。这些木马软件中的大多数自2016年底-2017年初以来一直在发展，但其在2017年第二季度开始有上升趋势，所以我们决定仔细研究一下这些木马。

一般来说，这些木马软件通常都具有相似的功能。首先，它们会**关闭WiFi并开启移动互联网**，它们这样做是因为**WAP计费只能通过移动互联网进行**。然后它们打开一个能够重定向到WAP计费页面的URL。通常，木马加载这些页面并使用[JavaScript（JS）文件](https://securelist.com/threats/javascript-glossary/?utm_source=securelist&amp;utm_medium=blog)点击按钮。之后，木马软件将**删除从移动网络运营商发来的有关WAP计费的短信消息**。此外，它们中的一些还有能力发送短信，另外一些木马还能通过利用设备管理员权限使得木马软件难以被检测和删除。

**<br>**

**Clicker.AndroidOS.Ubsod木马软件**

****

在这篇文章中，我将以**Trojan.AndroidOS.Boogr.gsh**这款木马软件为例来详细分析这些WAP计费木马，这些恶意软件是我们的系统基于机器学习算法识别到的，通过机器学习算法，我们的系统发现**2017年第二季度最流行的木马软件是WAP计费木马**，通过分析，我发现它们属于**Trojan-Clicker.AndroidOS.Ubsod**恶意软件系列。

 [![](https://p2.ssl.qhimg.com/t0107f29bd373014d70.png)](https://p2.ssl.qhimg.com/t0107f29bd373014d70.png)

**Trojan.AndroidOS.Boogr.gsh**是一个小而简单的特洛伊木马，该木马从其命令和控制服务器（C&amp;C）接收URL然后打开。这些网址只是一些广告网址，木马通过使用“**ViewAdsActivity**”等类名称使其伪装成一款广告软件。但是，它可以删除手机收到的那些包含文本“**ubscri**”（“订阅”的一部分）或“одпи”（俄语中的“Подписка”的一部分）的所有短信消息。此外，它可以关闭WiFi并打开移动网络数据。木马软件这样做的原因是因为**WAP计费仅在通过移动互联网访问该页面时才起作用**，而不是通过WiFi。

 [![](https://p5.ssl.qhimg.com/t01ee6177f665c734de.png)](https://p5.ssl.qhimg.com/t01ee6177f665c734de.png)

在分析这些木马样本之后，我发现其中一些木马样本（MD5 A93D3C727B970082C682895FEA4DB77B）也包含其他功能，例如其中一些木马软件包含了解密和加载（执行）其他可执行文件的功能，这些特洛伊木马除了通过WAP计费服务窃取资金外，还执行一个命名为**Trojan-Banker.AndroidOS.Ubsod**的木马软件。

 [![](https://p5.ssl.qhimg.com/t0162cb9ad4a0806348.png)](https://p5.ssl.qhimg.com/t0162cb9ad4a0806348.png)

**Trojan-Banker.AndroidOS.Ubsod**是一个功能强大的木马程序，它不仅通过其他木马软件进行传播，而且还可以作为独立的特洛伊木马（MD5 66FE79BEE25A92462A565FD7ED8A03B4）进行传播。它可以下载和安装应用程序，覆盖其他应用程序的窗口（主要用于窃取用户登录凭据或信用卡的信息）、显示广告、发送短信、窃取收到的短消息，**甚至能够在设备命令行中执行命令**。此外，它还具有通过WAP计费服务窃取用户资金的功能。**Trojan-Banker.AndroidOS.Ubsod**是WAP计费木马中最为流行。根据KSN统计，2017年7月的感染该木马软件的用户接近8,000人，这些用户来自82个国家，其中72％的用户来自于俄罗斯。

 [![](https://p4.ssl.qhimg.com/t0140991c4737a7a7b1.png)](https://p4.ssl.qhimg.com/t0140991c4737a7a7b1.png)

<br>

**Xafekopy木马软件**

****

在已经过去的几个月时间里，另一个特别流行的恶意软件家族当属**Trojan-Clicker.AndroidOS.Xafekopy**。该木马使用JS文件点击包含WAP计费网页上的按钮，并以静默地方式窃取用户的资金。最有趣的是这些JS文件看起来和Ztorg木马软件中JS文件看起来很像，它们甚至有一些功能具有相同的名称，这个木马程序主要攻击印度（37％）和俄罗斯（32％）的用户。

 [![](https://p2.ssl.qhimg.com/t01da58644e8b197158.png)](https://p2.ssl.qhimg.com/t01da58644e8b197158.png)

该木马软件通过广告伪装成正常的应用程序，例如伪装成电池优化器应用。用户安装之后，它的从行为上来看，也像是一个正常的应用程序，但它跟正常应用程序有一点区别：就是该恶意软件会去加载一个恶意程序库。该库文件解密安装包并从安装包的**assets**文件夹中加载恶意文件，这些恶意文件在解密之后会加载assets文件夹中的另一些恶意文件，这些恶意文件包含了木马软件的主要恶意功能。木马软件通过使用解密后的JS文件，可以绕过验证码表单，并点击WAP网页中的计费按钮，以此来从用户的移动帐户中窃取金钱。它也可以通过点击一些广告页面，从广告中赚钱。

 [![](https://p0.ssl.qhimg.com/t01d09bf646ccc8111c.png)](https://p0.ssl.qhimg.com/t01d09bf646ccc8111c.png)

据KSN统计，几乎40％的受感染用户在印度，但总体来看，2017年7月份共有来自48个不同国家的5000多名用户感染了该木马软件。

<br>

**Autosus木马软件**

****

**Trojan-Clicker.AndroidOS.Autosus.a**木马软件主要是通过使用WAP计费的劫持页面来窃取用户的金钱，木马软件首先从C&amp;C服务器中接收JS文件和恶意URL网址，之后加载这些页面并使用JavaScript（JS）文件点击页面上的恶意按钮，它还可以使用从C&amp;C服务器收到的规则来隐藏用户收到的短信。

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01827210717223a963.png)

启动之后，木马软件会要求用户激活该木马的设备管理员权限。之后，该木马将**从应用程序列表中删除其图标**，因此用户将无法轻松找到它。同时，木马将继续在后台运行，从C&amp;C服务器接收命令，打开恶意URL并点击恶意网页上的计费按钮。

 [![](https://p3.ssl.qhimg.com/t018891d308bfedfa71.png)](https://p3.ssl.qhimg.com/t018891d308bfedfa71.png)

该特洛伊木马在2017年7月袭击了1400多名用户，其中大多数来自印度（38％），南非（31％）和埃及（15％）。

<br>

**结论**

****

在过去的几个月时间里，我们发现木马软件针对不同国家的WAP计费业务攻击趋势在不断的增长。尽管具有这种功能的木马多年来一直存在，但我们发现了几种新的木马，而且最近几个月受这些新木马感染的用户数量正在显著的增长。此外，以前的WAP计费服务大都发生在俄罗斯，但现在我们已经在不同的国家（包括印度和南非）发现了这种攻击，甚至针对其他攻击的特洛伊木马也开始通过劫持WAP计费服务来窃取用户的钱。

**木马样本MD5**

F3D2FEBBF356E968C7310EC182EE9CE0

9E492A6FB926E1338DADC32463196288

A93D3C727B970082C682895FEA4DB77B

66FE79BEE25A92462A565FD7ED8A03B4

AEAE6BFDD18712637852C6D824955859

DA07419994E65538659CD32BF9D18D8A
