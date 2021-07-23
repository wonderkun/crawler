> 原文链接: https://www.anquanke.com//post/id/181097 


# 如何黑掉EA游戏的所有游戏用户账号


                                阅读量   
                                **280005**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者checkpoint，文章来源：research.checkpoint.com
                                <br>原文地址：[https://research.checkpoint.com/ea-games-vulnerability/](https://research.checkpoint.com/ea-games-vulnerability/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0120812647b3ebc33e.jpg)](https://p1.ssl.qhimg.com/t0120812647b3ebc33e.jpg)



在过去的几周里，Check Point Research与Cyber​​Int合作发掘出一系列漏洞，这一系列漏洞可以导致全球第二大游戏公司EA Games数百万玩家账户被盗。最终导致的危害程度取决于攻击者利用被盗用户中信用卡信息的能力以及游戏虚拟货币的购买力。



## EA游戏平台

EA Games 拥有超过3亿用户，收入约50亿美元，是全球第二大游戏公司，拥有许多家庭游戏，如FIFA，Maden NFL，NBA Live，UFC，模拟人生，战场，命令与征服和荣誉勋章。所有这些游戏都依赖于其自行开发的 Origin游戏平台，Origin允许用户在PC和移动设备上购买和玩EA游戏。

Origin还包含社交功能，例如个人资料管理，在游戏中与好友聊天以及与Facebook，Xbox Live，PlayStation Network和Nintendo Network等社交平台的关联功能。



## 漏洞简介

与Check Point Research之前发现的另一个非常流行的在线游戏Fortnite类似，EA平台上发现的漏洞不需要用户提供任何登录过程中的信息(账号密码等)。相反，该漏洞利用了EA Games结合oAuth单点登录(SSO)和内置在EA Game用户登录过程中的TRUST机制来盗用身份验证令牌。

介绍一些相关背景：EA Games是一家基于云的公司，它使用Microsoft Azure托管多个域名，如ea.com和origin.com，以便为其玩家提供全球访问各种服务，包括创建新游戏帐户，连接进入Origin社交网络，在EA在线商店购买游戏等服务。



## 技术细节

### <a class="reference-link" name="1.Eaplayinvite.ea.com%E5%AD%90%E5%9F%9F%E5%90%8D%E5%8A%AB%E6%8C%81"></a>1.Eaplayinvite.ea.com子域名劫持

EA游戏运营多个域名，如ea.com和origin.com，以便为其玩家提供全球访问各种服务，包括创建新的Apex Legend帐户，连接到Origin社交网络，以及在EA游戏在线商店购买新的EA游戏。

通常，基于云的公司（如EA Games）提供的每项服务都在一个唯一的子域名地址上注册。举个例子，eaplayinvite.ea.com，它具有指向特定云服务提供商主机的DNS记录（A或CNAME记录）：ea-invite-reg.azurewebsites.net，该云服务提供商主机在后台运行eaplayinvite.ea.com站点所需的服务，在本例中它是一个Web应用程序服务器。

[![](https://p2.ssl.qhimg.com/t01830f644d282bd7f9.png)](https://p2.ssl.qhimg.com/t01830f644d282bd7f9.png)

Azure是由Microsoft提供支持的云服务提供商解决方案，允许一个公司注册新服务（例如Web应用程序，REST API，虚拟机，数据库等），以便向全球的在线客户提供这些服务。

每个Azure用户帐户都可以请求注册一个由用户指定的服务名称（Service-Name.azurewebsites.net），该名称的CNAME记录在Azure子域验证过程中成功验证后，将会被连接到相关的特定域或子域。

然而在我们的信息收集过程中，我们发现EA公司的ea-invite-reg.azurewebsites.net服务在Azure云服务中不再被使用，但是EA公司的一个子域eaplayinvite.ea.com仍然使用CNAME配置重定向到该被弃用的云服务。

eaplayinvite.ea.com的CNAME重定向允许我们在我们自己的Azure帐户中申请一个新服务，并将被弃用的ea-invite-reg.azurewebsites.net注册为我们的新Web服务。这使得我们基本上成功劫持了eaplayinvite.ea.com并监控EA有效用户的请求

[![](https://p1.ssl.qhimg.com/t012551b04e3dcaa650.png)](https://p1.ssl.qhimg.com/t012551b04e3dcaa650.png)

如下所示，劫持过程后的DNS记录状态现在显示eaplayinvite.ea.com重定向到我们申请的Azure云Web服务：

[![](https://p1.ssl.qhimg.com/t01b24cf3dd5682b10e.png)](https://p1.ssl.qhimg.com/t01b24cf3dd5682b10e.png)

### <a class="reference-link" name="2.%E7%BB%95%E8%BF%87%E9%99%90%E5%88%B6%E6%88%90%E5%8A%9F%E6%8E%A7%E5%88%B6SSO%E4%BB%A4%E7%89%8C"></a>2.绕过限制成功控制SSO令牌

控制eaplayinvite.ea.com让我们的研究团队找到一个新的目标，即弄清楚我们如何滥用TRUST机制。TRUST机制存在于ea.com和origin.com域及其子域之间。如果我们能够成功滥用该机制，则我们能够操纵oAuth协议的实施来实现对所有EA游戏账户的盗取。

我们首先需要确定EA游戏如何配置oAuth协议并为其用户提供单点登录（SSO）机制。SSO机制通过唯一的SSO令牌交换用户凭证（用户和密码），然后使用该令牌对EA网络的任何平台（例如accounts.origin.com）进行身份验证，而用户则无需再次输入其用户凭据。

研究分析EA游戏的Q&amp;A站点（如answers.ea.com，help.ea.com和accounts.ea.com）对于oAuth SSO的解释阐述可以有效帮助我们了解EA身份验证流程，并了解有关TRUST机制的更多信息，这也是信息收集的工作之一。

answers.ea.com是使用EA游戏中单点登录机制的站点的一部分我们以其为例子阐述EA身份验证流程。首先oAauth HTTP请求将发送到accounts.ea.com以获取新的用户SSO令牌，然后通过singin.ea.com.com上访问记录（记录你想要访问的站点，在此例中为answers.ea.com）将用户重定向到answers.ea.com上。

[![](https://p0.ssl.qhimg.com/t018c6668012225e2c2.png)](https://p0.ssl.qhimg.com/t018c6668012225e2c2.png)

[![](https://p0.ssl.qhimg.com/t01bb610e913eda669d.png)](https://p0.ssl.qhimg.com/t01bb610e913eda669d.png)

然而，我们发现，实际上，可以通过在HTTP请求中修改returnURI参数来调整oAuth令牌生成的EA服务地址，即修改oAuth令牌分发的对象。在这里修改为被我们劫持的EA子域eaplayinvite.ea.com，如顺利的话，oAtuh令牌将分发到eaplayinvite.ea.com上，利用该令牌，我们可实现EA全域单点登录，如下图

[![](https://p0.ssl.qhimg.com/t01fe3eafffea1cf234.png)](https://p0.ssl.qhimg.com/t01fe3eafffea1cf234.png)

[![](https://p0.ssl.qhimg.com/t01fd91d9773839fc90.png)](https://p0.ssl.qhimg.com/t01fd91d9773839fc90.png)

但是，由于EA公司在该操作上还有一些限制，因此我们除了将SSO令牌重定向到eaplayinvite.ea.com外，还需要绕过一些限制从而达到最终的账号盗取效果。

以下为EA的一些防御措施以及我们如何成功绕过它们的描述：

### <a class="reference-link" name="1.%E5%8F%97%E4%BF%A1%E5%9F%9F%E6%A3%80%E6%9F%A5%E7%BB%95%E8%BF%87"></a>1.受信域检查绕过

为了盗取EA帐户，研究团队需要将之前提到的请求发送到accounts.ea.com，包括修改相关参数来伪装对应的EA账号。

但是，accounts.ea.com的后端服务器会通过检查HTTP Referer头来验证请求是否最初来自受信任的Origin域。

[![](https://p1.ssl.qhimg.com/t01af1eaac3cb18c62a.png)](https://p1.ssl.qhimg.com/t01af1eaac3cb18c62a.png)

为了绕过该限制，我们需要令受害者从EA受信任域或子域发出请求。因此，我们在我们劫持的eaplayinvite.ea.com上制造了一个钓鱼页面，诱引用户点击，产生从EA受信任域发起的HTTP请求。

[![](https://p5.ssl.qhimg.com/t01e0731f4b7af751ba.png)](https://p5.ssl.qhimg.com/t01e0731f4b7af751ba.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01000f3932cfb744e9.png)

### <a class="reference-link" name="2.jQuery%E5%87%BD%E6%95%B0%E6%A3%80%E6%B5%8B%E7%BB%95%E8%BF%87"></a>2.jQuery函数检测绕过

在向signin.ea.com发送请求以完成我们的恶意身份验证过程并将受害者的令牌发送到eaplayinvite.ea.com上的被劫持子域后，会生成一个新的jQuery函数并返回给客户端以重定向令牌。

[![](https://p3.ssl.qhimg.com/t014a33eff06059cc35.jpg)](https://p3.ssl.qhimg.com/t014a33eff06059cc35.jpg)

但是，由于目标服务器（eaplayinvite.ea.com）不是当前Origin服务器（signin.ea.com）的一部分，因此jQuery $.postMessage函数将无法成功执行。因此，该函数将向浏览器控制台发送错误并停止向我们发送令牌。

[![](https://p0.ssl.qhimg.com/t01c7d9989f5b115101.png)](https://p0.ssl.qhimg.com/t01c7d9989f5b115101.png)

为了解决这个问题，我们需要在signin.ea.com上寻找一个新的令牌重定向方法，因为jQuery函数阻止它们将受害者的令牌发送到非Origin服务器上。

经过多次尝试，我们捕获了一个包含redirectback参数的signin.ea.com的不同请求。此参数令服务器使用returnuri值并直接将页面重定向到它上面，而不需要将受害者的访问令牌附加到其上。

[![](https://p5.ssl.qhimg.com/t019d63a48c9a7f1da3.png)](https://p5.ssl.qhimg.com/t019d63a48c9a7f1da3.png)

[![](https://p2.ssl.qhimg.com/t0164af96b78eb112a2.png)](https://p2.ssl.qhimg.com/t0164af96b78eb112a2.png)

到目前为止，我们设法将经过身份验证的EA游戏用户的令牌重定向到我们的服务器。我们能够在受害者访问钓鱼页面之后获取到令牌，因此我们可以在我们的服务器上捕获到受害者的请求及其令牌！

[![](https://p3.ssl.qhimg.com/t016fc8ecf9ec187aa4.jpg)](https://p3.ssl.qhimg.com/t016fc8ecf9ec187aa4.jpg)

在受害者通过钓鱼页面完成SSO验证后，其令牌将会伴随HTTP Referer验证通过HTTP请求发送到我们的服务器上。signin.ea.com上的最后一次重定向使用window.location JavaScript函数将受害者重定向到我们的服务器。该访问包含受害者的SSO令牌，我们可以利用该令牌实施账号盗用。（译者注：老外真啰嗦）

[![](https://p5.ssl.qhimg.com/t011c4bf5f537fce767.png)](https://p5.ssl.qhimg.com/t011c4bf5f537fce767.png)

[![](https://p4.ssl.qhimg.com/t01e5ce80eaab18a626.png)](https://p4.ssl.qhimg.com/t01e5ce80eaab18a626.png)
