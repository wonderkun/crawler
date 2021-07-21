> 原文链接: https://www.anquanke.com//post/id/86664 


# 【技术分享】在远程沙箱中自由翱翔：Adobe Flash Windows用户凭据泄漏漏洞


                                阅读量   
                                **77082**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：bjornweb.nl
                                <br>原文地址：[https://blog.bjornweb.nl/2017/08/flash-remote-sandbox-escape-windows-user-credentials-leak/](https://blog.bjornweb.nl/2017/08/flash-remote-sandbox-escape-windows-user-credentials-leak/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p1.ssl.qhimg.com/t013ba990bd637233f9.jpg)](https://p1.ssl.qhimg.com/t013ba990bd637233f9.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

最近一段时间，我发表了关于Flash沙箱逃逸漏洞的一篇[**文章**](https://blog.bjornweb.nl/2017/02/flash-bypassing-local-sandbox-data-exfiltration-credentials-leak/)，最终导致已存活十多年的Flash Player本地安全沙箱寿终正寝。

之前的这个漏洞向我们展示了对输入数据进行正确性验证的重要性。攻击者只需要向运行时的Flash输入混合的UNC以及文件URI，就足以[**提取本地数据**](https://blog.bjornweb.nl/2017/02/flash-bypassing-local-sandbox-data-exfiltration-credentials-leak/#whats-in-a-scheme-exfiltrating-local-data)，并可以将[**Windows用户凭证**](https://blog.bjornweb.nl/2017/02/flash-bypassing-local-sandbox-data-exfiltration-credentials-leak/#smb-at-play-leaking-windows-user-credentials)发往远程SMB服务器。

Flash Player在23版本中移除了本地文件系统（local-with-filesystem）沙箱，从本地角度来看，这样处理有效解决了这两个问题。然而非常有趣的是，官方的[**发行注记**](https://forums.adobe.com/thread/2209269)中忽略了剩下的两个沙箱：本地网络（local-with-networking）沙箱以及远程（remote）沙箱。因此我想了解这两个沙箱的问题是否得到了修复。

实际上，根据最初的测试结果，Flash会拒绝任何UNC或者文件形式的路径。这两个沙箱似乎都不会接受任何非HTTP形式的URL。因此，这就带来一个非常有趣的问题：如果我们能以另一种方法来绕过这个限制呢？我们能否在通过输入验证后，修改输入表达式的含义呢？

简而言之，Adobe Flash可能会受到某个已知Windows漏洞的影响。虽然我们可以通过运行时的安全解决方案来削弱该漏洞所能造成的影响，但这些安全方案原本是用于不同的目的，因此还是可以被针对性地绕过。因此，我们可以绕过Flash Player新引入的输入验证机制，让攻击者恢复获取Windows用户凭证的能力。

本文分析了我最近向Adobe报告的一个安全漏洞，Adobe对该漏洞的编号为[**APSB17-23**](https://helpx.adobe.com/security/products/flash-player/apsb17-23.html)，对应的CVE编号为[**CVE-2017-3085**](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-3085)。

<br>

**二、HTTP重定向问题**

****

再次重申一下，之前那个漏洞利用的关键点是将我们的恶意Flash应用连接到我们的SMB服务器上。在不对客户端进行身份认证的前提下，通过拒绝客户端的访问请求，服务器可以使得Windows客户端向其发送用户的凭证信息。

Adobe似乎非常了解这种攻击方法。之前版本的Flash会从所有SMB服务器上加载资源，但在23版中，Flash会拒绝掉任何UNC以及文件形式的路径，这两种路径是SMB主机的表示方法。现在许多路径会被Flash拒绝掉，如\10.0.0.1somefile.txt路径，以及等效的file://///10.0.0.1/some/file.txt路径。

然而，我们可以根据微软提供的URI列表，构造各种富有创造力的URL，但依然无法获得任何突破。在这两个沙箱中，不论哪个沙箱的URLLoader似乎都不会接受没有使用HTTP或者HTTPS作为前缀的那些路径。看上去Adobe似乎使用白名单机制来加固他们的产品。

这种情况下，如果我们可以在通过输入验证后，修改请求路径，那么会发生什么事情呢？根据前面的分析，我们必须使用HTTP形式的地址，因此我们需要利用HTTP重定向功能来访问SMB主机。

幸运的是，SMB以及HTTP还是可以组合在一起的。首先映入我脑海的就是一个Windows漏洞，名为[**重定向到SMB（Redirect-to-SMB）漏洞**](https://blog.bjornweb.nl/2017/02/flash-bypassing-local-sandbox-data-exfiltration-credentials-leak/#by-definition-not-so-local)。通过设置HTTP头部中的Location信息，以及提供一个适当的响应代码（比如301或者302代码），攻击者就可以利用这个漏洞将HTTP请求重定向到一个恶意的SMB服务器。攻击场景如下图所示：

[![](https://p0.ssl.qhimg.com/t013ba38cc3219689a7.png)](https://p0.ssl.qhimg.com/t013ba38cc3219689a7.png)

<br>

**三、漏洞复现**

在我们的攻击场景中，恶意Flash应用以及SMB服务器都托管于一台主机上，主机IP地址为23.100.122.2。这个Flash应用会运行在受害者本地主机的远程（remote）沙箱中。也就是说，Flash运行时会阻止访问本地文件系统，但允许远程连接。

跟踪Win32 API后，我们发现受Redirect-to-SMB漏洞影响的[**函数**](https://www.kb.cert.org/vuls/id/672268)位于urlmon.dll中。因此，Internet Explorer以及任何使用IE浏览器的第三方应用都会受到该漏洞影响。

这个漏洞吸引了许多媒体的关注，很多厂商发布了修复补丁来修复他们的产品。那么，Adobe Flash的表现如何呢？我们可以尝试重定向某个出站请求GET /somefile.txt，结果如下所示：

[![](https://p1.ssl.qhimg.com/t01508357167738584b.png)](https://p1.ssl.qhimg.com/t01508357167738584b.png)

#2032错误代码是Flash用来表示流错误（Stream Error）的代码。根据之前的研究成果，我们知道除了#2048代码以外，其他代码都可以用来表示成功状态。我们来看看实际出现了什么情况：

[![](https://p4.ssl.qhimg.com/t017d93a6e5376a6025.png)](https://p4.ssl.qhimg.com/t017d93a6e5376a6025.png)

额，看起来Flash Player并没有受到任何影响：我们返回的HTTP/1.1 302响应没有触发SMB流量。然而，我们注意到，抓取的报文中出现一个GET报文请求crossdomain.xml。这个文件是跨域策略的[**配置文件**](http://www.adobe.com/devnet/adobe-media-server/articles/cross-domain-xml-for-streaming.html)，当Flash客户端被允许从另一个域中加载资源时就会涉及到这个文件。比如，如果没有经过domain-b.com的明确许可，那么托管在domain-a.com上的Flash应用就不会加载domain-b.com上的图片。

细心的读者可能会注意到Adobe的有关定义，与[**HTTP CORS**](https://www.w3.org/TR/cors/#terminology)（读者可以阅读[**RFC6454**](https://tools.ietf.org/html/rfc6454#section-5)了解更多细节）不同的是，Adobe会将自身限制在跨域（cross-domain）数据处理上。更具体地说，Adobe不会去考虑不同协议的区分问题。因此，我们的攻击被阻止应该与这种安全机制无关：因为我们正在尝试重定向到SMB，这是同一主机上的不同协议。

有趣的是，根据Wireshark的记录，我们发现应用正在请求某台主机上的crossdomain.xml，而这台主机正是运行Flash应用的同一台主机。因此，我们可以来构造一个最为宽松的跨域策略。根据Adobe开发者指南中的语法，我们构造的策略如下：



```
&lt;?xml version="1.0"?&gt;
&lt;!DOCTYPE cross-domain-policy SYSTEM "http://www.adobe.com/xml/dtds/cross-domain-policy.dtd"&gt;
&lt;cross-domain-policy&gt;
    &lt;site-control permitted-cross-domain-policies="all"/&gt;
    &lt;allow-access-from domain="*" secure="false"/&gt;
    &lt;allow-http-request-headers-from domain="*" headers="*" secure="false"/&gt;
&lt;/cross-domain-policy&gt;
```

最后，我们重新加载我们的Flash应用，观察执行情况：

[![](https://p5.ssl.qhimg.com/t019ba2e593a61a2c91.png)](https://p5.ssl.qhimg.com/t019ba2e593a61a2c91.png)

成功了！我们最终建立了从受害主机（23.100.122.3）到我们的远程服务器（23.100.122.2）的SMB连接。此时此刻，我们只需要重复我们之前做的[**工作**](https://blog.bjornweb.nl/2017/02/flash-bypassing-local-sandbox-data-exfiltration-credentials-leak/#smb-at-play-leaking-windows-user-credentials)就可以了。我们可以使用一个名为SMBTrap的脚本来承担我们恶意SMB服务器的角色，用来捕捉传入的任何请求，其中也包括受害者的用户凭证信息：

[![](https://p1.ssl.qhimg.com/t0161471b8400607238.png)](https://p1.ssl.qhimg.com/t0161471b8400607238.png)

<br>

**四、受影响的环境**

有趣的是，与上一个漏洞相比，Edge以及Chrome浏览器并不会受到这个漏洞影响（这些浏览器都启用了Flash功能）。尽管这两个浏览器都存在类似的行为，比如跨域策略文件的请求行为，但两者貌似都会阻止Flash连接到SMB主机。

也就是说，Firefox以及Internet Explorer会受到漏洞影响。同时这也会影响到当前Microsoft Office的所有版本。此外，这个漏洞同时会影响远程（remote）以及本地网络（local-with-networking）沙箱。



**五、总结**

在引入新的输入验证机制后，Flash Player 23就已经通过拒绝任何非HTTP URL形式的出站请求，来尽可能地降低潜在的攻击方法的成功率。然而，非常意外的是，Adobe只做了一次输入验证过程：即只检查初始的HTTP请求是否有效，没有检查后续的重定向请求是否有效。同时因为Flash仍然会受到某个已知的Windows漏洞的影响，因此结合这个事实，我们就能绕过看起来坚不可摧的防御机制。这是非常不幸的一件事情，也许通过这件事情，我们会意识到在必要的时候还是应该考虑特定平台漏洞所会造成的潜在危害。

Flash Player 26.0.0.151修复了这个问题，我们可以通过Windows Update或者Adobe的[**官网**](https://get.adobe.com/flashplayer/)下载新的版本。



**六、附录**

**6.1 受影响的主机环境**

Firefox

Internet Explorer

Microsoft Office 2010、2013以及2016

**6.2 受影响的平台**

Flash Player 23.0.0.162到26.0.0.137

Windows XP、Vista、7、8.x以及10

**6.3 时间线**

11-02-2017：向趋势科技零日倡议项目报告漏洞。

21-04-2017：ZDI承认该漏洞，并分配编号ZDI-17-634。

05-06-2017：请求状态更新。Adobe回复他们会于2017年7月发布Flash Player 26，修复这个漏洞。

12-07-2017：请求状态更新。Adobe回复他们仍在做修复工作，新版与预期于2017年8月份发布。

08-08-2017：Adobe在Flash Player 26.0.0.151中修复了这个漏洞。

08-08-2017：漏洞信息公布。

**6.4 参考资料**

[Adobe Security Bulletin APSB17-23](https://helpx.adobe.com/security/products/flash-player/apsb17-23.html)

[CVE-2017-3085](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-3085)

[ZDI-17-634](http://www.zerodayinitiative.com/advisories/ZDI-17-634/)

[Threatpost – Patched Flash Player Sandbox Escape Leaked Windows Credentials](https://threatpost.com/patched-flash-player-sandbox-escape-leaked-windows-credentials/127378/)

[Security.NL – Radboud-student ontdekt opnieuw lek in Adobe Flash Player](https://www.security.nl/posting/527299/Radboud-student+ontdekt+opnieuw+lek+in+Adobe+Flash+Player)

[ComputerBild – Adobe Patchday: Updates gegen über 80 Sicherheitslücken](http://www.computerbild.de/artikel/cb-Aktuell-Software-Adobe-Sicherheits-Update-Flash-Player-7408005.html)

[WCCFTech – Adobe Addresses Several Vulnerabilities in Flash Player, Acrobat Reader](http://wccftech.com/adobe-bugs-flash-player-acrobat-reader/)

[SecurityWeek – Adobe Patches 69 Flaws in Flash, Reader, Acrobat](http://www.securityweek.com/adobe-patches-69-flaws-reader-acrobat)

[Blorge – Adobe Flash Player and Acrobat Reader Security Updates](https://tech.blorge.com/2017/08/10/adobe-flash-player-and-acrobat-reader-security-updates/161970)

[SecurityTracker – Adobe Flash Player Bugs Let Remote Users Obtain Potentially Sensitive Information and Execute Arbitrary Code](http://www.securitytracker.com/id/1039088)
