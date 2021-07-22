> 原文链接: https://www.anquanke.com//post/id/92907 


# 趋势科技关于Janus漏洞最新利用情况的分析


                                阅读量   
                                **105544**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Veo Zhang，文章来源：trendmicro.com
                                <br>原文地址：[http://blog.trendmicro.com/trendlabs-security-intelligence/janus-android-app-signature-bypass-allows-attackers-modify-legitimate-apps/](http://blog.trendmicro.com/trendlabs-security-intelligence/janus-android-app-signature-bypass-allows-attackers-modify-legitimate-apps/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01dc2195a8d874c77a.jpg)](https://p4.ssl.qhimg.com/t01dc2195a8d874c77a.jpg)



## 一、前言

Android在2017年12月发布的[安全更新](https://source.android.com/security/bulletin/2017-12-01)中修复了一个严重漏洞，利用该漏洞时，攻击者可以在不影响已安装应用签名的前提下对应用进行修改。这样一来，攻击者就能（间接）获得受影响设备的访问权限。研究人员在[7月份](https://www.guardsquare.com/en/blog/new-android-vulnerability-allows-attackers-modify-apps-without-affecting-their-signatures)首次发现了这一情况，该漏洞（编号为CVE-2017-13156，也称为Janus漏洞）影响5.1.1到8.0版本的Android系统，全世界约有[74%](https://developer.android.com/about/dashboards/index.html)的Android设备安装了这些系统，覆盖范围极广。

在实际环境中，我们发现至少已经有一个app在利用这种技术。使用该漏洞后，移动安全解决方案更加难以检测到这个恶意应用。在不久的将来，攻击者可能会利用该漏洞危害其他应用，获取用户的隐私信息。



## 二、漏洞分析

Android应用的安装包（`.APK`文件）实际上是`.ZIP`文件，而`.ZIP`文件格式中有一些特性会导致这种攻击条件成立。典型的`.ZIP`文件结构如下图所示：

[![](https://p1.ssl.qhimg.com/t0104c39ab0013935c5.png)](https://p1.ssl.qhimg.com/t0104c39ab0013935c5.png)

图1. `.ZIP`文件结构

文件结构包含3个部分：File Entries、Central Directory以及End of Central Directory。Central Directory中包含压缩文件中每个文件的相关信息，应用程序可以使用该目录来定位内存位置，以访问所需的文件。

然而，ZIP文件并不要求每个file entry紧挨在一起，我们甚至可以在两个file entry之间插入任意数据，如下图所示：

[![](https://p0.ssl.qhimg.com/t018f9a7d9781b56ee3.png)](https://p0.ssl.qhimg.com/t018f9a7d9781b56ee3.png)

图2. `.ZIP`文件结构（红色区域为任意数据）

攻击者可以将恶意DEX文件放在APK文件开头处，如下图所示。如果Android系统存在该漏洞，那么系统就会将其识别成有效的APK文件并尝试执行该文件。

[![](https://p2.ssl.qhimg.com/t013ba0f6304859f50d.png)](https://p2.ssl.qhimg.com/t013ba0f6304859f50d.png)

图3. 将DEX插入APK文件中

Android Runtime（ART）负责从APK文件中加载DEX代码。在检查该文件时，由于DEX代码位于文件头部，因此ART会将其识别为DEX文件并直接执行。ART会将后面的代码（即原始的APK文件内容）当成垃圾数据并忽略这些数据。尽管如此，ART还是认为这是一个有效的APK文件，访问这个APK数据（如resources以及assets）的过程与普通app类似。



## 三、漏洞影响

一般而言，恶意软件可以通过两种方式来滥用这个漏洞。

首先，攻击者可以利用该漏洞来隐藏攻击载荷。恶意软件可以将恶意载荷存放在APK文件中，借此伪装成一个无害的DEX文件，以待后续被加载。前面提到过的那个应用使用的就是这种方法，下文会详细介绍这一点。

其次，攻击者不需要原始开发者的帮助就可以更新设备上已安装的某个应用。攻击者可以利用这个漏洞来访问原始应用中受保护的数据，如用户凭据信息以及个人隐私信息。此外，冒用合法应用的身份也可以绕过某些安全防护产品。



## 四、实际攻击活动

漏洞细节公之于众后，我们检查了已有的一些恶意软件样本，想验证是否已经有些恶意软件样本使用了这个漏洞。我们发现的确有一个恶意软件样本用到了这个漏洞，但漏洞的利用方法与我们原来设想的并不相同。我们将这个样本标记为`ANDROIDOS_JANUS.A`。我们还与Google合作，采取了适当的措施，提醒用户相关风险（Google已将该应用标记为恶意应用）。

这个应用之前在Google Play上为一款垃圾清理程序，但更新后变成了一款新应用，并没有在Play商店中上架。

[![](https://p3.ssl.qhimg.com/t01d0ba5cbc12268f92.png)](https://p3.ssl.qhimg.com/t01d0ba5cbc12268f92.png)

图4. 利用Janus漏洞的新版app的图标

这款恶意软件利用该漏洞来实现动态代码加载。嵌入的DEX文件只包含一小段攻击载荷，这段载荷从各种资源中解密真正的载荷，然后动态加载真正的载荷。攻击者利用Janus漏洞构造了一个异常的应用，应用头部为DEX文件，真正的载荷隐藏在之后的APK代码中。之所以这么做是为了绕过恶意软件扫描程序，这些安防产品可能会将这个文件当成DEX文件，判断其为无害文件，忽略掉其中的恶意代码。

恶意软件会在Android设备启动时以后台服务形式运行，连接到C&amp;C服务器，接收服务器返回的命令以安装更多恶意软件，这些是我们目前观察到的恶意行为。

[![](https://p3.ssl.qhimg.com/t01897e1edb953244f9.png)](https://p3.ssl.qhimg.com/t01897e1edb953244f9.png)

图5. 下载其他恶意软件的代码片段

攻击者可以使用Janus漏洞来恶意更新设备上已安装的应用。分析这款恶意软件代码后，我们发现它并没有更新任何应用，只是使用Janus漏洞来规避安防产品。然而，恶意软件可能会使用这种攻击方法来化身成下载器（downloader），我们不能排除这种可能性。



## 五、开发者如何防护

Android 7.0（Nougat）中引入了一种新的签名机制（signature scheme v2）。新的签名机制中，签名证书及摘要不再位于meta区域中，而是位于APK文件中的一个APK签名区域中，新的签名区域位于File Entries以及Central Directory之间。这样就能保护其他3个区域的完整性。

[![](https://p0.ssl.qhimg.com/t014c0280ff290c4536.png)](https://p0.ssl.qhimg.com/t014c0280ff290c4536.png)

图6. APK文件中的签名区域

新的签名机制中，file entry之间仍然可以存在间隙。然而，系统会检查从文件头开始到APK签名区域之间的一整段数据，这意味着任何篡改动作都会破坏签名的完整性。这种情况下，攻击者还是有可能将DEX文件插入头部中，然而如果想成实施攻击，攻击者还是需要重新签名APK签名区域。

出于兼容性考虑，开发者通常更倾向于采用混合签名方案（同时使用v1及v2方案），此时的防护效果因设备而异。在支持这种特性的设备上，由于存在回滚保护（rollback protection）特性，设备会强制使用v2签名机制。

[![](https://p3.ssl.qhimg.com/t0129cbdbc3cb879bc5.png)](https://p3.ssl.qhimg.com/t0129cbdbc3cb879bc5.png)

图7. 回滚保护

在搭载老版本Android系统的设备上，如果这些系统只支持v1版的签名机制，那么攻击者仍然可能针对这些设备发起攻击。话虽如此，在Nougat系统普及到更多设备之前，我们还是建议开发者继续使用混合签名方案。



## 六、总结

这个漏洞在影响力方面与几年前Android系统的[Master Key漏洞](https://blog.trendmicro.com/trendlabs-security-intelligence/master-key-android-vulnerability-used-to-trojanize-banking-app/)不相上下。这两个漏洞都可以让攻击者在不引起用户注意的情况下修改合法应用。

如果利用该漏洞的恶意应用成功混入应用商店，那么用户将同时面临两个安全风险：要么恶意应用会伪装成合法应用成功传播，要么恶意应用通过应用商店安装到用户设备上，修改大量合法应用。

并非所有的移动安全解决方案都能从容应付这个挑战。嵌入在普通应用程序中的恶意DEX代码能够成功规避许多安全解决方案。企业级MDM（移动设备管理）解决方案同样有可能检测不到这类应用，并且这些安全应用本身也有可能被这类应用所篡改。应用厂商应该进一步提升自身实力，才能更好地扫描并检测恶意Android应用。

趋势科技提供的安全解决方案（如[Mobile Security for Android](https://www.trendmicro.com/us/home/products/mobile-solutions/android-security/)™，可从[Google Play](https://play.google.com/store/apps/details?id=com.trendmicro.tmmspersonal)上下载）可以检测到这类安全威胁。[Mobile Security for Enterprise](https://www.trendmicro.com/us/enterprise/product-security/mobile-security/)支持各种安全功能，如设备合规性检查、应用程序管理、数据保护、安全设置等，也能保护设备免受漏洞利用攻击、阻止未授权访问应用、检测并阻止恶意软件及欺诈网站。

趋势科技的移动应用信誉服务（[Mobile App Reputation Service](https://mars.trendmicro.com/)，MARS）同时支持Android以及iOS平台，采用了顶尖的沙盒及机器学习技术。MARS可以保护用户免受恶意软件、0Day漏洞以及已知漏洞的威胁，避免泄露隐私信息，免受应用漏洞影响。



## 七、IoC

该应用的攻击特征如下所示：

|SHA256|包名|标签
|------
|a28a10823a9cc7d7ebc1f169c544f2b14afc8b756087b5f2c3a50c088089f07d|com.fleeeishei.erabladmounsem|World News



## 八、拓展阅读
- [PUA Operation Spreads Thousands of Explicit Apps in the Wild and on Legitimate App Stores](http://blog.trendmicro.com/trendlabs-security-intelligence/pua-operation-spreads-thousands-explicit-apps-wild-legitimate-app-stores/)
- [ZNIU: First Android Malware to Exploit Dirty COW Vulnerability](http://blog.trendmicro.com/trendlabs-security-intelligence/zniu-first-android-malware-exploit-dirty-cow-vulnerability/)
- [BankBot Found on Google Play and Targets Ten New UAE Banking Apps](http://blog.trendmicro.com/trendlabs-security-intelligence/bankbot-found-google-play-targets-ten-new-uae-banking-apps/)
- [Vulnerability in F2FS File System Leads To Memory Corruption on Android, Linux](http://blog.trendmicro.com/trendlabs-security-intelligence/vulnerability-f2fs-file-system-leads-memory-corruption-android-linux/)