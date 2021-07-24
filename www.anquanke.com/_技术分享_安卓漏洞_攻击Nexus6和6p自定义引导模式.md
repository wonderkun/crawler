> 原文链接: https://www.anquanke.com//post/id/85288 


# 【技术分享】安卓漏洞：攻击Nexus6和6p自定义引导模式


                                阅读量   
                                **87543**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securityintelligence.com
                                <br>原文地址：[https://securityintelligence.com/android-vulnerabilities-attacking-nexus-6-and-6p-custom-boot-modes/](https://securityintelligence.com/android-vulnerabilities-attacking-nexus-6-and-6p-custom-boot-modes/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0103632bb0d44c02f3.jpg)](https://p2.ssl.qhimg.com/t0103632bb0d44c02f3.jpg)

****

**作者：**[**胖胖秦******](http://bobao.360.cn/member/contribute?uid=353915284)

**预估稿费：140RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

**<br>**

**前言**

在最近几个月，X-Force安全研究小组发现了一些之前从未公开的Android漏洞。在2016年11月和2017年1月之间,Android安全简报里包含了这些高危漏洞的补丁：Nexus 6和6P的CVE-2016-8467。我们的新文章,“攻击Nexus 6&amp;6P自定义引导模式”讨论了此漏洞和CVE-2016-6678。

<br>

**自定义引导模式**

本文介绍了攻击者如何利用PC恶意软件或恶意充电器重启一台Nexus 6或6P设备并实现一个特殊的引导配置或引导模式，它会命令Android开启多种额外的USB接口。

[![](https://p5.ssl.qhimg.com/t01334b2208d30db037.png)](https://p5.ssl.qhimg.com/t01334b2208d30db037.png)

<br>

**访问Nexus 6调制解调器诊断**

这些接口，特别是调制解调器诊断接口，使攻击者能够访问其他功能。这允许他们接管Nexus 6调制解调器，从而对机密性和完整性造成威胁。

例如，访问调制解调器可以使攻击者能够拦截电话。下图显示了成功拦截电话接收通道的波形：

[![](https://p5.ssl.qhimg.com/t01a6f8f3986ab410dd.png)](https://p5.ssl.qhimg.com/t01a6f8f3986ab410dd.png)

攻击者也可以嗅探移动数据包。下图显示了我们如何成功地侦听LTE数据:

[![](https://p2.ssl.qhimg.com/t01d923a2df54b19ac6.png)](https://p2.ssl.qhimg.com/t01d923a2df54b19ac6.png)

此外，对Nexus 6调制解调器的这种访问级别允许攻击者查找精确的GPS坐标，详细的卫星信息，拨打电话，窃取通话信息，访问或更改NV条目和EFS分区。

<br>

**触发Android漏洞**

如果设备上已启用ADB，那么PC恶意软件或恶意充电器可以使用特殊引导模式配置来引导Nexus 6 / 6P设备。开发人员使用ADB进行调试，用户可以利用它将Android应用程序包（APK）安装到他们的设备上。如果在攻击前未被永久授权,进行连接时,受害者必须要对设备上的PC或充电器进行授权。然后，攻击者可以简单地发出以下命令：



```
adb reboot bootloader
fastboot oem config bootmode bp-tools (N6)
fastboot oem bp-tools-on (N6, option 2)
fastboot oem enable-bp-tools (N6P)
fastboot reboot
```

这些命令使用特殊引导模式来重新启动设备, 启用接口。以后每次重启都将使用这种特殊的引导模式配置。这意味着攻击是持久的，不再需要ADB运行，虽然它仍然需要USB访问。因此，攻击者只需要受害者启用一次ADB。另外，幸运的攻击者可能会等待设备处于快速引导模式，这种模式不需要受害者授权。但是，这不太可能。

除了上述修改引导模式技术之外，对于物理攻击者,使用定制引导模式来引导设备是另一种方式。具有对设备的物理访问权限的攻击者可以将其重新引导到快速引导模式，并选择BP-Tools或Factory设置相关的引导模式配置，如下所示：

[![](https://p2.ssl.qhimg.com/t0170658258afb8ded2.png)](https://p2.ssl.qhimg.com/t0170658258afb8ded2.png)

<br>

**访问调制解调器AT接口**

该漏洞对Nexus 6P的影响没有那么严重，因为调制解调器诊断在调制解调器固件上是禁用，这将阻止上述的恶意行为。但是，攻击者可以访问额外的USB接口，如调制解调器AT接口，这也是Nexus6易被攻击的地方。通过这个接口,攻击者可以发送或窃取短信，并可能绕过双因素认证。

[![](https://p5.ssl.qhimg.com/t01051fa9fea35fff1e.png)](https://p5.ssl.qhimg.com/t01051fa9fea35fff1e.png)

攻击者还可以访问电话信息，更改各种无线设置等。

<br>

**ADB访问**

即使在开发者界面中禁用ADB接口，6P中的漏洞也会启用ADB接口。即使PC被锁定，通过访问经过ADB授权的电脑，物理攻击者可以打开一个设备的ADB会话，运行在受害者PC下的ADB会对ADB授权令牌进行RSA签名，这种ADB连接允许攻击者在设备上安装恶意软件。在一台ADB授权机器上的PC恶意软件也可以利用CVE-2016-8467来启用ADB并安装Android恶意软件。PC恶意软件等待受害者开启设备的快速引导模式,然后触发漏洞。

<br>

**Nexus 6中未初始化的内核内存泄漏**

经过进一步分析，我们发现在使用自定义引导模式引导时，Nexus 6还启用了另一个可疑USB接口。该接口将自身标识为“Motorola测试命令”。负责此接口的内核驱动程序叫作f_usbnet。有趣的是，这个驱动程序带有一个可以从主机端配置并基于USB的以太网适配器，这将导致网络流量的泄漏。

我们在f_usbnet驱动上还发现了一个名为CVE-2016-6678的漏洞，通过USB, 4-5个字节未初始化内核数据将被填充到每一个以太网帧中。这种泄漏可能包含敏感数据，可以授权网络犯罪分子利用系统。下图显示了一个包含泄漏数据的ICMP帧：

[![](https://p1.ssl.qhimg.com/t0155af8135b0295748.png)](https://p1.ssl.qhimg.com/t0155af8135b0295748.png)

<br>

**协调披露**

在此博客发布之前,X-Force团队负责任的向Google报告了这些Android漏洞。

Google将 CVE-2016-8467定义为高危漏洞，通过禁止已锁的引导加载器以危险的引导模式来引导系统,可以减少此漏洞的发生。Nexus 6的第一个安全加载器的版本是71.22，于2016年11月发布在Android安全简报上。Nexus 6P的第一个安全加载器版本是03.64，于2017年1月作为安全简报的一部分发布。

Google将CVE-2016-6678定义为中危漏洞，通过将未初始化的字节置零来阻止此漏洞，以防止数据泄漏。该补丁于2016年10月作为安全简报的一部分发布。
