> 原文链接: https://www.anquanke.com//post/id/168117 


# Charming Kitten王者归来


                                阅读量   
                                **362827**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者certfa，文章来源：blog.certfa.com
                                <br>原文地址：[https://blog.certfa.com/posts/the-return-of-the-charming-kitten/](https://blog.certfa.com/posts/the-return-of-the-charming-kitten/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t014b054be5bfd319d9.jpg)](https://p1.ssl.qhimg.com/t014b054be5bfd319d9.jpg)



## 前言概述

网络钓鱼攻击是受伊朗政府支持的黑客惯用的攻击手段。我们对最新的网络钓鱼攻击进行了跟踪，并将其命名为“The Return of The Charming Kitten”。

这起攻击的目标是那些曾参与对伊朗的经济和军事进行制裁的人士以及世界各国的政治家、公民、人权倡导者和新闻工作者。

根据分析，我们认为攻击者将那些开启2步验证的用户的email账户和验证码作为目标。防范此类攻击，使用Yubikey等加密设备是很有效的。



## 简介

在2018年10月初，推特用户MD0ugh揭露了一起伊朗黑客针对美国金融机构基础设施的网络钓鱼攻击。他推测这可能是伊朗遭受美国新的制裁后进行的反击。

该用户还提到了一个域名：accounts[-]support[.]services。这个域名与一些由伊朗政府支持的黑客有联系。我们认为这些黑客和之前曾报道过的伊斯兰革命卫队（IRGC）存在关联。

距这些活动发生一个月后，运营accounts-support[.]services的黑客们扩大了攻击规模，开始针对民权和人权活动家、政治人士以及伊朗和西方的新闻工作者攻击。



## 攻击手段

根据我们的调查，攻击者采用不同的手段实施攻击，主要分为以下2种：
1. 通过未知邮件、社交媒体及消息账户进行钓鱼攻击
1. 通过已经被黑客入侵的公众人物的邮箱、社交媒体及消息账户进行钓鱼攻击
我们还发现在进行网络钓鱼攻击之前，黑客会搜集目标的个人信息。黑客会根据目标的网络安全水平、联系人、活动、工作时间、地理位置等信息为每个目标设计具体的攻击计划。

我们注意到，不同于以往的钓鱼攻击，在最新的攻击活动中黑客并不会修改受害者的账户密码，这使他们能在不被发现的同时保持对受害者的电子邮件通信进行实时监控。



## 虚假的未授权访问警告

对网络钓鱼攻击样本进行分析，这些黑客主要使用电子邮件发送虚假警报对目标进行欺骗，例如通过notifications.mailservices[@gmail](https://github.com/gmail)[.]com, noreply.customermails[@gmail](https://github.com/gmail)[.]com, customer]email-delivery[.]info等向目标发出信息，提示说有未经授权的个人试图登陆他们的帐户。

[![](https://p3.ssl.qhimg.com/t01dc665e85d1cce2f5.png)](https://p3.ssl.qhimg.com/t01dc665e85d1cce2f5.png)<br>
图1：真假页面链接对比

通过使用这种方法，攻击者伪装成邮件服务商向目标发送安全警报，用户会立即点击“目标链接”查看详细信息，来对可疑访问进行限制。



## Google Drive虚假文件共享

发送带有标题的链接（例如来自Google Drive的共享文件）是近年来黑客使用的最常见的技巧之一。与之前的攻击相比，这些攻击的独特之处在于他们使用了看似为Google 站点的页面，黑客构造虚假的Google Drive下载页面来欺骗用户，使受害者认为这一个真正的Google Drive页面，不存在安全问题。

[![](https://p5.ssl.qhimg.com/t01b1fd2e3a44cce426.png)](https://p5.ssl.qhimg.com/t01b1fd2e3a44cce426.png)

图2：虚假Google Drive文件共享页面

例如，黑客使用hxxps://sites.google[.]com/view/sharingdrivesystem来欺骗用户，用户会因为在浏览器的地址栏中看到了google.com而相信该网页是真正的 Google Drive。

**通过伪造具有相同界面的Google Drive文件共享页面，黑客假装与用户共享文件，用户本应该下载并运行共享的文件。然而该页面没有任何文件，他们使用入侵的Twitter，Facebook和Telegram帐户发送这些链接来寻找新的受害者。通过此页面将目标用户定向到虚假的谷歌登录页面，诱使用户输入身份验证信息。**



## 攻击流程

### <a class="reference-link" name="%E6%81%B6%E6%84%8F%E9%93%BE%E6%8E%A5"></a>恶意链接

**受信任阶段：**互联网用户都认为谷歌的主域（google.com）是安全可靠的，攻击者正是利用用户的这种心理，在sites.google.com（Google的子域）上构造虚假页面来欺骗用户。Google提供的网站服务使用户能够在其上显示各种内容。攻击者使用此功能发送虚假警报并将受害者重定向到不安全的网站或嵌入网络钓鱼链接的页面。

[![](https://p5.ssl.qhimg.com/t018903c07a5eed3f15.png)](https://p5.ssl.qhimg.com/t018903c07a5eed3f15.png)

图4：攻击者如何滥用site.google.com

**非受信任阶段：**由于Google可以快速识别并删除sites.google.com上的可疑链接和恶意链接，所以黑客会使用自己的网站进行伪造，进行攻击。钓鱼网站的链接几年前的网络钓鱼活动曾使用的链接非常类似。例如，攻击者在域名或网络钓鱼URL中使用诸如“management”, “customize”, “service”, “identification”, “session”, “confirm” 等关键词来欺骗那些想要验证自己网址的用户。

### <a class="reference-link" name="%E9%82%AE%E4%BB%B6%E4%B8%AD%E7%9A%84%E5%8F%AF%E7%82%B9%E5%87%BB%E5%9B%BE%E7%89%87"></a>邮件中的可点击图片

黑客在电子邮件正文中并不是文本，而是使用图片来绕过谷歌的安全检测和反网络钓鱼系统。为此，攻击者还使用第三方服务（如Firefox屏幕截图）来对图片进行托管。<br>[![](https://p2.ssl.qhimg.com/t01be010547a29e7e40.png)](https://p2.ssl.qhimg.com/t01be010547a29e7e40.png)

图5：虚假警报图片示例

### <a class="reference-link" name="%E9%9A%90%E8%97%8F%E7%9A%84%E8%B7%9F%E8%B8%AA%E5%9B%BE%E7%89%87"></a>隐藏的跟踪图片

攻击者在邮件正文中单独隐藏了其他图片，以便在受害者打开电子邮件时收到通知。通过这种技巧，黑客可以在目标打开电子邮件并点击网络钓鱼链接后立即采取行动。



## 钓鱼页面

除了恶意邮件和钓鱼链接之外，攻击者还在定制化平台创建相应条目来存储受害者的凭据信息。我们还注意到他们针对Google和Yahoo!，设计了PC和移动端的钓鱼页面，可能在将来进行下一系列的攻击。

在最近的攻击中，攻击者使用了一种有趣的技术，一旦受害者输入了用户名和密码，攻击者将立即对这些凭据进行验证，如果信息正确无误，那么他们就会要求提供2步验证码。

换句话说，他们会在自己的服务器上实时验证受害者的用户名和密码，即使启用了2步身份验证（例如短信，验证应用或one-tap），他们也可以欺骗目标并窃取该信息。

图6至图9展示了一些由伊朗黑客发送给目标的网络钓鱼页面。

[![](https://p2.ssl.qhimg.com/t01655570fe9a3c62b8.png)](https://p2.ssl.qhimg.com/t01655570fe9a3c62b8.png)

图6 ：获取Gmail帐户密码的虚假页面

[![](https://p1.ssl.qhimg.com/t01504dbd08c24a1066.png)](https://p1.ssl.qhimg.com/t01504dbd08c24a1066.png)<br>
图7:获取Gmail 2步验证码的虚假页面

[![](https://p5.ssl.qhimg.com/t01b50cd81078c9e9e8.png)](https://p5.ssl.qhimg.com/t01b50cd81078c9e9e8.png)<br>
图8:获取Yahoo!账户密码的虚假页面

[![](https://p5.ssl.qhimg.com/t01efbab344be031cf1.png)](https://p5.ssl.qhimg.com/t01efbab344be031cf1.png)<br>
图9:获取Yahoo!2步验证码的虚假页面



## 追踪

通过我们对这些网络钓鱼攻击的分析可以得知：黑客已经注册了大量的域名。根据最新的调查结果显示，在相对较短的时间内（2018年9月至11月），黑客就已经使用了20多个域名。

在撰写本文时，用于网络钓鱼攻击的域名数量有所增加。通过对这些服务器更深入的调查，我们揭示了在最近的攻击中这些域名是如何被使用的。

[![](https://p3.ssl.qhimg.com/t01541c87f4493f2034.png)](https://p3.ssl.qhimg.com/t01541c87f4493f2034.png)

图10:网络钓鱼活动中攻击者所用域名关联分析

根据相关技术分析，我们认为参与此活动的攻击者通过虚拟专用网络（VPN）和代理，使用荷兰和法国IP地址来隐藏自己。尽管如此，我们还是通过足够的细节，找到了攻击者的真实IP地址位于伊朗。（IP：89.198.179 [。] 103和31.2.213 [。] 18）

此外，这些攻击中对域名和服务器的命名方式，所用的技巧，针对的目标都与拥有伊朗政府背景的黑客组织——Charming Kitten非常相似。因此，我们认为这是Charming Kitten组织的伊朗黑客发起了新一轮的网络攻击，并且将以色列公民和美国公民作为重点目标。



## 结论

网络钓鱼攻击是伊朗黑客窃取数据最常用的手段，但对于此次活动，最应该重视的是它的发生时间。这次攻击活动在2018年11月4日前几周开始进行，当时美国正对伊朗实施了新一轮的制裁。因此该运动试图对他国政治人士以及对伊朗实施经济和军事制裁的当局进行渗透，来窃取信息。

换句话说，这群受伊朗政府支持的黑客根据伊朗政府的政策和国际利益需求来选择目标，对其造成影响。

因此，我们向科技公司，政府官员，社会人士以及互联网用户提出了一系列建议，来防御此类威胁。

对科技公司，政府人员的建议：
- 停止使用基于纯文本的2步身份验证。
- 使用安全密钥（如YubiKey）对个人敏感操作进行2步身份验证。
- 不使用单击登录验证。
对社会人士及海外伊朗人士：
- 及时了解网络钓鱼威胁活动，建议使用Yubikey等安全密钥进行2步身份验证并激活Google的Advanced Protection Program。
- 始终使用公司邮箱收发机密信息，而不是个人邮箱 。根据公司邮箱策略，限制从工作网络外部接收电子邮件。例如，G Suite允许管理员拒收来自未授权地址或域名的电子邮件。
- 建议在帐户中使用Google Authenticator等移动应用进行2步身份验证。
对互联网用户的建议：
- 不点击未知链接。要查看帐户中的可疑警报或更改密码，可以直接从电子邮件转到“我的帐户”进行设置，而不是点击任何链接。
- 使用PGP对敏感邮件进行加密，防止黑客窃取邮件信息。
- 不将敏感信息以纯文本形式存储在邮箱中。
- URL域名之前的HTTPS只是HTTP协议的安全扩展，并不意味着网站的内容是安全的或可信的 。要知道许多钓鱼网站也使用了HTTPS。


## IOCs
- 178.162.132[.]65
- 190.2.154[.]34
- 190.2.154[.]35
- 190.2.154[.]36
- 190.2.154[.]38
- 46.166.151[.]211
- 51.38.87[.]64
- 51.38.87[.]65
- 51.68.185[.]96
- 51.38.107[.]113
- 95.211.189[.]45
- 95.211.189[.]46
- 95.211.189[.]47
- 213.227.139[.]148
- 54.37.241[.]221
- 54.38.144[.]250
- 54.38.144[.]251
- 54.38.144[.]252
- 85.17.127[.]172
- 85.17.127[.]173
- 85.17.127[.]174
- 85.17.127[.]175
- 89.198.179[.]103
- 31.2.213[.]18
- accounts-support[.]services
- broadcast-news[.]info
- broadcastnews[.]pro
- com-identifier-servicelog[.]info
- com-identifier-servicelog[.]name
- com-identifier-userservicelog[.]com
- confirm-session-identification[.]info
- confirm-session-identifier[.]info
- confirmation-service[.]info
- customer-recovery[.]info
- customize-identity[.]info
- document-share[.]info
- document.support-recoverycustomers[.]services
- documentofficupdate[.]info
- documents.accounts-support[.]services
- documentsfilesharing[.]cloud
- email-delivery[.]info
- mobile-sessionid.customize-identity[.]info
- mobiles-sessionid.customize-identity[.]info
- my-scribdinc[.]online
- myyahoo.ddns[.]net
- notificationapp[.]info
- onlinemessenger.com-identifier-servicelog[.]name
- podcastmedia[.]online
- recoveryusercustomer[.]info
- session-management[.]info
- support-recoverycustomers[.]services
- continue-session-identifier[.]info
- mobilecontinue[.]network
- session-identifier-webservice.mobilecontinue[.]network
- com-messengersaccount[.]name
- invitation-to-messenger[.]space
- confirm-identification[.]name
- mobilecontinue[.]network
- mobile.confirm-identification[.]name
- services.confirm-identification[.]name
- mobile-messengerplus[.]network
- confirm.mobile-messengerplus[.]network
- com-messengercenters[.]name
- securemail.mobile-messengerplus[.]network
- documents.mobile-messengerplus[.]network
- confirm-identity[.]net
- identifier-sessions-mailactivityid[.]site
- activatecodeoption.ddns[.]net
- broadcastpopuer.ddns[.]net
- books.com-identifier-servicelog[.]name
- mb.sessions-identifier-memberemailid[.]network
- sessions-identifier-memberemailid[.]network
- sessions.mobile-messengerplus[.]network
- confirm-verification-process[.]systems
- accounts.confirm-verification-process[.]systems
- broadcastnews.ddns[.]net
- account-profile-users[.]info
- us2-mail-login-profile[.]site
- us2.login-users-account[.]site
- login-users-account[.]site
- live.account-profile-users[.]info
- signin.account-profile-users[.]info
- aol.account-profile-users[.]info
- users-account[.]site