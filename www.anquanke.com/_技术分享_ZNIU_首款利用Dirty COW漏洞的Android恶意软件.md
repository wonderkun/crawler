> 原文链接: https://www.anquanke.com//post/id/86930 


# 【技术分享】ZNIU：首款利用Dirty COW漏洞的Android恶意软件


                                阅读量   
                                **107204**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：trendmicro.com
                                <br>原文地址：[http://blog.trendmicro.com/trendlabs-security-intelligence/zniu-first-android-malware-exploit-dirty-cow-vulnerability/](http://blog.trendmicro.com/trendlabs-security-intelligence/zniu-first-android-malware-exploit-dirty-cow-vulnerability/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t015689398d19c9a625.png)](https://p4.ssl.qhimg.com/t015689398d19c9a625.png)



译者：[Shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

我们已经向Google披露了本文提到的安全问题，同时Google已经检测确认Google Play Protect已能够针对**ZNIU**提供相应的保护了。

2016年，被称为**Dirty COW**（CVE-moles195）的Linux漏洞被首次公开曝光。同时安全研究人员发现，诸如Redhat和Android之类的主流Linux平台中也存在该漏洞，因为这些平台的内核都是基于Linux。这个漏洞被认定为严重的提权漏洞，允许攻击者在目标系统上获得root访问权限。不过从该漏洞被发现以来，一直没有听说过针对Android平台的Dirty COW攻击的传闻，也许是因为攻击者正在憋大招：多花些时间搞出超级稳定的漏洞利用代码。近一年后，趋势科技研究人员收集到了ZNIU（即AndroidOS_ZNIU）的样本，这是第一个针对Android平台的Dirty COW漏洞的恶意软件系列。

上个月，安全研究人员在四十多个国家发现了ZNIU恶意软件，其中大多数受害者都位于**中国**和**印度**。我们在**美国**，**日本**，**加拿大**，**德国**和**印度尼西亚**等国也检测到了该恶意软件。截止撰写本文时，我们检测到的感染用户已经超过了5000人。同时，我们在各种恶意网站上发现，有超过**1,200**多种恶意应用程序都携带ZNIU代码，其中包括一个利用Dirty COW漏洞的现有rootkit，这些程序通常都会伪装成色情和游戏软件。

[![](https://p4.ssl.qhimg.com/t015a6c60c50e9f3963.jpg)](https://p4.ssl.qhimg.com/t015a6c60c50e9f3963.jpg)

图1：暗藏ZNIU代码的色情程序

去年，我们曾经针对Dirty COW漏洞开发了一个PoC，经测试发现所有版本的Android操作系统都易受该漏洞的侵害，但是，这次发现的利用Dirty COW漏洞的ZNIU代码却仅适用于64位的ARM/X86架构的Android设备。然而，这个漏洞却可以绕过SELinux并生成root后门，而我们的PoC则只能修改系统的服务代码。

我们监测了六个ZNIU rootkit，其中四个利用了Dirty COW漏洞。另外两个分别是KingoRoot（一个rooting程序）和Iovyroot漏洞利用代码（CVE-2015-1805）。 ZNIU用到了KingoRoot和Iovyroot，因为它们可以获取ARM 32位CPU设备的root权限，其他针对该Dirty COW漏洞的Rootkit则没有这个功能。

**<br>**

**感染过程**

ZNIU恶意软件通常伪装成色情应用程序，放在恶意网站上工人们下载，当用户被诱骗而点击相应的恶意URL后，它就会被安装到用户的手机上。一旦启动，ZNIU就开始与其C＆C服务器进行通信。如果有相应的更新代码可用，则从C＆C服务器下载相应的代码，并将其加载到系统中。同时，Dirty COW漏洞利用代码将用于提权，并成相应的后门，以便将来可以发动隐蔽的远程控制攻击。

[![](https://p4.ssl.qhimg.com/t010914bd5d43bb28fa.jpg)](https://p4.ssl.qhimg.com/t010914bd5d43bb28fa.jpg)

图2：ZNIU感染链

进入设备的主UI后，该恶意软件将收集用户的运营商信息，然后该恶意软件的操纵者将冒充受害者通过SMS支付服务与运营商进行交易。这样，利用受害者的移动设备，ZNIU的幕后操纵者就可以通过运营商的支付服务来“吸金”。我们从其中一个样本发现，用户的钱是根据网络流量支付给一个虚拟公司的，从下图可以看出，该公司位于中国的一个城市。 当SMS交易结束后，该恶意软件会从设备中删除付款信息，从而抹去运营商与该恶意软件操纵者之间的交易痕迹。如果运营商位于中国境外，它虽然不会与运营商进行短信交易，但该恶意软件仍将在系统中植入后门。 

[![](https://p2.ssl.qhimg.com/t01d724e926cf50c10c.jpg)](https://p2.ssl.qhimg.com/t01d724e926cf50c10c.jpg)

图3：恶意软件发送给运营商的交易请求

根据我们的分析，这个恶意软件只会使中国运营商的用户蒙受金钱损失。此外，虽然该恶意软件操纵者可以设置更高的交易金额，从而捞更多的钱，但是为了避免被用户发现，实际上每一笔交易金额都是很少的（每月20元或3美元），以免引起受害者的注意。 

[![](https://p0.ssl.qhimg.com/t0196fdafedddc97e6a.png)](https://p0.ssl.qhimg.com/t0196fdafedddc97e6a.png)

图4：SMS业务的截图

对于Android OS来说，当授予其他应用程序访问设备的SMS功能的权限时，会强制用户介入，所以ZNIU需要root权限才能实现上述功能。此外，该恶意软件还可以安装后门程序，并远程加载其他恶意代码，从而继续从受害者那里榨取钱财。

**<br>**

**深入分析ZNIU Rootkit**

ZNIU rootkit可以通过一个独立的广播接收者(Broadcast Receiver)集成到恶意应用程序中。

[![](https://p2.ssl.qhimg.com/t01f5c38fc89197698a.png)](https://p2.ssl.qhimg.com/t01f5c38fc89197698a.png)

图5：通过网络激活ZNIU代码

该恶意软件可以轻松地将rootkit注入第三方应用程序，而无需更改其他组件，这将有助于进行大规模的传播。

该恶意软件的操纵者还为ZNIU的DEX代码提供了加密和打包等保护措施，以对抗静态逆向工程。 经过进一步调查后发现，一旦用户将设备连接到网络或插入电源，它就会使用广播接收者(Broadcast Receiver)激活漏洞代码。然后，该恶意软件会直接传输并执行其本地代码。 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0193be4efee9263ab2.png)

图6：ZNIU的本地代码

ZNIU的本地代码的主要逻辑如下所示：

**1.    收集设备的型号信息。**

**2.    从远程服务器下载相应的rootkit。**

**3.    对漏洞利用代码进行解密。**

**4.    逐个触发各漏洞利用代码，检查结果，并删除漏洞利用文件。**

**5.    报告漏洞利用代码的运行是否成功。**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fae878f0eaee01e8.png)

图7：ZNIU的网络活动

经过研究，我们还发现远程利用代码服务器的URL以及客户端和服务器之间的通信都经过了加密处理。但使用字符串解密后，我们进一步研究该漏洞利用代码服务器发现，其域名和服务器主机都位于中国境内。此外，恶意漏洞利用代码服务器的相关链接可以在附录中找到。 

[![](https://p4.ssl.qhimg.com/t01d25c78989f76e72e.png)](https://p4.ssl.qhimg.com/t01d25c78989f76e72e.png)

图8：漏洞利用代码服务器的后台

一旦下载完成，该rootkit就会借助ZLIB将“exp * .ziu”解压为“exp * .inf”。 

[![](https://p4.ssl.qhimg.com/t01c6fcf6d43e14a82c.png)](https://p4.ssl.qhimg.com/t01c6fcf6d43e14a82c.png)

图9：利用ZLIB解压ziu文件

这个rootkit所需的所有文件都封装在一个.inf文件中，文件名以“ulnz”开头，其中含有多个ELF或脚本文件。 

[![](https://p3.ssl.qhimg.com/t017b368d35b94e967d.png)](https://p3.ssl.qhimg.com/t017b368d35b94e967d.png)

图10：inf文件的结构

ZNIU rootkit可以写入到**vDSO**（虚拟动态链接共享对象）中，从而将一组内核空间的函数导出到用户空间，以利于应用程序更好地执行。vDSO代码可以在不受SELinux限制的内核上下文中运行。

ZNIU使用公开的漏洞利用代码将shellcode写入vDSO并创建反向shell。 然后，它会篡改SELinux策略以解除限制，并植入一个后门性质的root shell。 

[![](https://p5.ssl.qhimg.com/t01af221e69613ac3e7.png)](https://p5.ssl.qhimg.com/t01af221e69613ac3e7.png)

图11：Dirty COW用于篡改vDSO的代码

**<br>**

**应对措施**

用户只应安装来自Google Play或可信的第三方应用商店的应用程序，并使用杀毒软件来提供相应的保护。此外，用户还可以与其设备制造商和/或电话运营商联系，以获得此漏洞的补丁。

我们正在监测ZNIU的活动，并且会根据事态的发展进一步更新本文。本附录（https://documents.trendmicro.com/assets/pdf/Appendix-ZNIUFirstAndroidMalwaretoExploitDirtyCOWVulnerability.pdf）中列出了相关软件的哈希值（SHA256）、包名称和应用标签。
