> 原文链接: https://www.anquanke.com//post/id/86883 


# 【技术分享】iXintpwn/YJSNPI滥用iOS配置文件，可以导致设备崩溃


                                阅读量   
                                **123344**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：trendmicro.com
                                <br>原文地址：[http://blog.trendmicro.com/trendlabs-security-intelligence/ixintpwn-yjsnpi-abuses-ioss-config-profile-can-crash-devices/](http://blog.trendmicro.com/trendlabs-security-intelligence/ixintpwn-yjsnpi-abuses-ioss-config-profile-can-crash-devices/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01c5f1f6ab61b803dc.png)](https://p4.ssl.qhimg.com/t01c5f1f6ab61b803dc.png)



译者：[Janus情报局](http://bobao.360.cn/member/contribute?uid=2954465307)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**简介**



由于iOS系统技术门槛高，封闭性强，针对iOS设备的威胁相对较少。但是这并不意味着iOS设备坚不可摧。[2016年](http://blog.trendmicro.com/trendlabs-security-intelligence/2016-mobile-threat-landscape/)，我们也看到了一些成功的威胁事件，从[滥用企业证书](http://blog.trendmicro.com/trendlabs-security-intelligence/ios-masque-attack-spoof-apps-bypass-privacy-protection/)到利用漏洞[突破](https://www.trendmicro.com/vinfo/us/security/research-and-analysis/predictions/2017)iOS平台的限制。

这在iXintpwn/YJSNPI中得到了进一步的体现(Trend Micro标记为TROJ_YJSNPI.A)，在这个案例中，利用恶意配置文件使iOS设备崩溃无响应。这是今年6月初[被逮捕](http://d.hatena.ne.jp/Kango/20170611/1497198757#20170611fn1)的一个日本脚本小子的部分作品。

虽然现在iXintpwn/YJSNPI只在日本传播，但是社交网络如此便捷的现在，想要全球传播也不是个难事。

iXintpwn/YJSNPI最早于2016年11月下旬在twitter出现，一个名为“iXintpwn”的iOS越狱者声称其可以对iOS设备进行越狱，随后YouTube和其他社交网站上也开始相继传播。iXintpwn也是发布恶意文件的网站名称。而在受感染的设备中各种图标都会显示为“YJSNPI”，这也被称为“Beast Senpai”(Senpai在日本一般指的是老师或导师)，这个图片经常在日本论坛上的默认图片。

不管它是想搞恶作剧还是想出名，这都不重要，重要的是它的攻击手段。因为在这个案例中，攻击者可以利用iXintpwn/YJSNPI滥用iOS的特性：未签名的iOS配置文件。

YJSNPI可以通过访问包含恶意文件的网站来扩散，主要通过Safari。当用户访问网站时，恶意网站的JavaScript文件会响应一个blob对象(恶意配置文件)。而在iOS设备上，最新的Safari接收到服务器的响应信息并将自动下载配置文件。

[![](https://p3.ssl.qhimg.com/t0100ccb366eb73e504.png)](https://p3.ssl.qhimg.com/t0100ccb366eb73e504.png)

[![](https://p3.ssl.qhimg.com/t016f38b7b92c084109.png)](https://p3.ssl.qhimg.com/t016f38b7b92c084109.png)



**滥用iOS配置文件**

[iOS配置文件](https://developer.apple.com/library/content/featuredarticles/iPhoneConfigurationProfileRef/Introduction/Introduction.html)能够帮助开发者简化大量设备的设置，包括电子邮件和exchange、网络和证书。例如，企业利用这些配置文件来简化对自研应用和企业设备的管理。配置文件还可以自义定设备限制，Wi-Fi、虚拟专用网络(VPN)、轻量目录访问协议(LDAP)目录、日历扩展到WebDAV(CalDAV)、web剪辑、证书和密钥。

很显然，可以利用恶意配置文件来修改这些设置，即转移设备的流量。这种恶意行为的典型例子包括[窃取信息的Wirelurker](http://blog.trendmicro.com/trendlabs-security-intelligence/staying-safe-from-wirelurker-the-combined-macios-threat/)和来自[Haima的重打包广告软件](http://blog.trendmicro.com/trendlabs-security-intelligence/how-a-third-party-app-store-abuses-apples-developer-enterprise-program-to-serve-adware/)。

在iXintpwn/YJSNPI这个例子中，它使用未签名的配置文件，并将其设置为“不能被删除”，让用户无法卸载，如下图所示。

对于持续性，“PayloadIdentifier”字符串的值是通过JavaScript随机生成的(很机智)。需要注意的事，iOS在安装签名或未签名的配置文件时采取了相应的措施，需要用户直接进行交互。唯一的区别是这些配置文件的显示方式，例如，签名的文件被表示为“已验证”。

[![](https://p5.ssl.qhimg.com/t0150dcae4884b2fbb7.png)](https://p5.ssl.qhimg.com/t0150dcae4884b2fbb7.png)



[![](https://p2.ssl.qhimg.com/t01f624cc7f2202f28d.png)](https://p2.ssl.qhimg.com/t01f624cc7f2202f28d.png)

[![](https://p3.ssl.qhimg.com/t01caa6d31a10ef7d0c.png)](https://p3.ssl.qhimg.com/t01caa6d31a10ef7d0c.png)

[![](https://p4.ssl.qhimg.com/t01d7870c0a0a69f660.png)](https://p4.ssl.qhimg.com/t01d7870c0a0a69f660.png)

[![](https://p1.ssl.qhimg.com/t018fdfb4bee66ab1ca.png)](https://p1.ssl.qhimg.com/t018fdfb4bee66ab1ca.png)



**iOS SpringBoard图标溢出**

在iXintpwn/YJSNPI的配置文件安装后，主屏幕上会叠加很多同样的图标。点击它会导致满是YJSNPI图标的屏幕溢出，并且桌面SpringBoard崩溃。此时，YJSNPI图标是可点击的，但只会显示图标更大的分辨率。在图标溢出期间，设备无任何响应。

[![](https://p2.ssl.qhimg.com/t01af486e6cd1a4a78c.png)](https://p2.ssl.qhimg.com/t01af486e6cd1a4a78c.png)



**缓解措施**

比较幸运，这个YJSNPI是可以从设备中卸载的，虽然它被设置为不可移除。已经受影响的用户可以利用苹果公司提供的[Apple Configurator 2](https://support.apple.com/apple-configurator)，或者官方的iOS帮助软件利用[Mac](https://itunes.apple.com/us/app/apple-configurator-2/id1037126344?mt=12)管理Apple设备，找到并删除恶意配置文件。

但是，有些步骤需要注意下。YJSNPI必须完整安装，否则图标无法被移除。——也就是说，如果未完整安装，那么当Apple Configurator 2运行时，恶意配置文件不会显示出来。还有就是，Apple Configurator 2并没有Windows版本。

提升移动设备安全性是非常必要的，尤其当iOS设备在BYOD环境中运行时。

定期对iOS系统和应用程序进行更新和打补丁，只从应用商店或可信的来源下载应用程序。越狱有风险，安装需谨慎。应充分意识到授权的重要性，对于可疑应用所请求的可疑权限应理智判断。同样建议应用开发人员采取一定的措施保护所开发的应用程序，这样可以在一定程度上降低其被利用而进行恶意传播的几率。
