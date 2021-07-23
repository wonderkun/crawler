> 原文链接: https://www.anquanke.com//post/id/86635 


# 【安全报告】谍影重重：中国DDoS产业现状大揭秘


                                阅读量   
                                **110734**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：talosintelligence.com
                                <br>原文地址：[http://blog.talosintelligence.com/2017/08/chinese-online-ddos-platforms.html](http://blog.talosintelligence.com/2017/08/chinese-online-ddos-platforms.html)

译文仅供参考，具体内容表达以及含义原文为准



**[![](https://p1.ssl.qhimg.com/t016071464d0dc332ef.jpg)](https://p1.ssl.qhimg.com/t016071464d0dc332ef.jpg)**

****

译者：[nstlBlueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

****

在过去的几个月中，Talos团队监测到提供在线DDoS服务的中国网站数量在不断的增加。这些网站中的许多网站几乎都有相同的布局和设计，基本上都提供了一些简单的用户界面，这个界面上有一些诸如目标主机、端口、攻击方法以及攻击持续时间等功能。而且，**这些网站大多数都是在过去六个月内注册的**，但是，这些网站以不同的组织名称运营，并且拥有不同的注册人。此外，Talos团队还检测到这些网站的管理员之间经常会相互发动攻击，Talos团队试图去研究创建这些平台的工作人员，并分析为什么这些提供DDOS服务的平台最近这么流行。

在这篇博文中，我们将首先看看中国DDoS行业的发展趋势，并阐述它们向在线DDoS平台转变的原因。然后，我们将检测最近创建的这些DDoS平台的类型，并分析它们的相似之处和差异。最后，我们将对这些几乎相同的DDoS平台网站的源代码进行分析。

<br>

**中国的DDoS行业现状**

****

在中国，DDoS工具和服务在黑客市场中仍然是最受欢迎的产品之一，DuTe（独特）就是其中之一，该黑客工具包含了各种不同的DDoS相关工具、各种网络攻击工具以及多种网络协议的爆破工具，例如用于不同网络协议（SSH和RDP）的爆破工具。另外，中国的社交应用（例如微信群、QQ群等）中有数百个关于DDoS工具相关的群，这些社交软件群专门用于分享DDoS工具或者恶意软件等，在这些群中的人有黑客群体，客户以及可以充当媒介的代理商乃至广告商等。

以前，这些群聊中的主要产品是用户可以购买和下载的工具，在这类工具中，具有代表性的就是“天罚集群压力测试系统”了，如下图所示。这些工具通常用于管理用户的僵尸网络，允许用户自定义攻击事件、选择攻击目标以及攻击方法。通常来说，用户需要首先购买该工具，下载副本，然后再使用自己的服务器或者僵尸网络对目标进行攻击，但有时，黑客团体也会捆绑一些服务器或一定数量的僵尸主机卖给购买者，例如其中包括用来帮助用户增长自己僵尸网络的黑客工具。但是，用户都将需要自己去负责维护和部署这些购买的黑客工具。

 [![](https://p2.ssl.qhimg.com/t01fc411758c0415db7.png)](https://p2.ssl.qhimg.com/t01fc411758c0415db7.png)

<br>

**在线DDoS平台的兴起**

****

最近，Talos团队已经注意到这些ddos小组聊天中正逐渐发生变化。在这些群聊中，在线DDoS平台的广告出现频率已经开始越来越高了。

 [![](https://p0.ssl.qhimg.com/t011739a7aae6f8c6fa.png)](https://p0.ssl.qhimg.com/t011739a7aae6f8c6fa.png)

经过对其中几个DDoS服务网站的分析之后，Talos团队注意到许多网站具有相同的登录和注册页面以及同样的背景图片：

 [![](https://p0.ssl.qhimg.com/t0188de7ef3cd178712.png)](https://p0.ssl.qhimg.com/t0188de7ef3cd178712.png)

 [![](https://p1.ssl.qhimg.com/t01eb5871e19e1593ef.png)](https://p1.ssl.qhimg.com/t01eb5871e19e1593ef.png)

此外，Talos团队还检测到，这些网站中有许多网站的设计和布局几乎相同，例如这些提供DDOS服务网站都会显示在线活动用户和服务器的数量以及已执行的攻击总数（尽管这些数字在不同组之间可能有所不同）。 此外，这些站点还包含了组管理员关于DDOS工具的最新更新、功能介绍以及使用限制的通知。在侧栏中，用户可以注册一个帐户，购买激活码，之后便可以开始发起网络攻击，攻击方法是通过网站上的图形界面或通过命令行调用的方式来攻击目标，使用方法如下所示：

http://website_name/api.php?username=&amp;password=&amp;host=&amp;port=&amp;time=&amp;method=

  [![](https://p4.ssl.qhimg.com/t01bc61cac081db4e3e.png)](https://p4.ssl.qhimg.com/t01bc61cac081db4e3e.png)

[![](https://p2.ssl.qhimg.com/t01f82f9f5ad5f79e5d.png)](https://p2.ssl.qhimg.com/t01f82f9f5ad5f79e5d.png)

除了设计和功能方面有相似之处以外，大多数网站在其域名中都包含有“**ddos**”这个字眼，例如“shashenddos.club”或“87ddos.cc”。由于这些网站都是最近注册的，除了依靠中国社交软件来发现这些ddos域名，Talos团队通过使用Cisco Umbrella这款工具可以对新注册网站进行检测，检测方法是通过包含有“ddos”字串的正则表达式对最近注册的域名进行搜索。通过使用多种检测方法，**Talos团队能够识别32个几乎完全相同的中文在线DDoS网站**（可能还有更多的网站，因为这些网站并不是所有的域名都有“ddos”）。

基于ddos服务网站页面的相似之处，以及一些个人为同一个群体注册了多个站点的事实，我们最初猜测这些提供ddos服务的多个网站都是由同一个人使用不同别名注册的，为了测试我们的理论，我们在每个站点注册了一个帐户，并且还使用Cisco Umbrella的调查工具来检查每个站点的注册信息。

但是，我们很快否定了我们的猜测，因为在各个网站注册账号后我们发现，许多用户都是通过不同的第三方中文支付网站购买软件激活码的（典型的，一个软件激活码的价格范围从每天20元左右到每月400元左右不等）。此外，这些网站页面上的公告显示了不同的工具功能（一些ddos攻击强度为30-80gbps，而其他则有高达300gbps的）以及不同的联系人信息（包括各种不同的客服QQ帐户以及各种不同的社交软件群号）。另外，在用户量和攻击次数上，这些网站也存在很大的差异，例如**www.dk.ps88.Org**这个网站，它拥有44,538位用户，而**www.pc4.Tw**这个网站则只有13个用户，发起的攻击数据也只有24次。

此外，网站的注册信息也存在很大的差异，大多数网站的注册人姓名、电子邮件以及注册商都是不同的。但也有一些相似之处：**几乎所有人都使用过中国注册商，其中大多数是在过去3个月内注册的，而且几乎全部都是在过去一年内登记的**。另外，一半以上的服务器都托管在Cloudflare IP上。

我们最后确认，这些网站背后有不同的管理员。因为从Talos团队正在监视的一个QQ群聊天记录中我们注意到，这个小组中的一个成员呼吁群内的成员使用“无名哥”这款ddos平台对[http://87ddos.cc](http://87ddos.cc)这样一个提供在线ddos服务的网站进行攻击，而这个网站我们的研究人员之前注册过帐号。

 [![](https://p0.ssl.qhimg.com/t011d628d21666c4dbe.png)](https://p0.ssl.qhimg.com/t011d628d21666c4dbe.png)

Talos团队加入了一些与在线DDoS平台相关的群聊中，并观察到多个小组成员讨论对对手ddos平台发起DDoS攻击的聊天记录。 事实上，通过观察这些在线DDoS网站的一些流量可以发现他们的网站之前的确遭受了DDoS攻击。

 [![](https://p3.ssl.qhimg.com/t015d9ba1cf8f43673a.png)](https://p3.ssl.qhimg.com/t015d9ba1cf8f43673a.png)

**一探究竟**

****

基于我们的研究发现，多个小组正在创建几乎相同的在线DDoS平台，但仍然不知道为什么他们使用相同的布局，或者为什么这些网站最近才开始出现。 我们开始深入了解这些问题背后的故事，从一个中国黑客组织的团队聊天中，我们发现了这个组织使用的在线DDoS平台管理页面的截图：

 [![](https://p5.ssl.qhimg.com/t01bc12fc6aa7a6a051.png)](https://p5.ssl.qhimg.com/t01bc12fc6aa7a6a051.png)

从截图中可以看到一个设置页面，页面中管理员可以填写网站名称、网站说明、服务条款以及网站URL链接，这些发现为我们的研究提供了一些线索。首先，我们在左上角注意到“双子座”一词，第二，我们注意到URL中“**/yolo/admin /settings**”这个字串。最后，我们注意到屏幕底部有一个按钮，管理员可以选择“Cloudflare模式”，这提示我们有多少网站被托管在Cloudflare IP中。

<br>

**查找和分析源代码**

****

我们现在有一个猜测：这些看起来相同的ddos网站是使用某种共享的源代码搭建起来的，这些代码可能来自于中国地下黑客论坛或者某些黑客市场。我们去了几个论坛，并搜索屏幕截图中发现的“**/yolo/admin/settings**”这个URL串。我们发现，这几个论坛都有一个销售在线DDoS平台源代码的帖子，这套源代码是国外某DDoS平台的汉化版。

这些帖子大都发布于2017年初或2016年底，这与DDoS平台兴起的时间相对应，而且广告中的图片看起来与我们看到的网站相同：

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c92b04aa35f32ef8.png)

Talos团队拿到这套ddos平台的源代码并进行了分析。 很明显，那些我们观察到的DDoS网站使用的就是这套源代码，例如文件夹中包含的PHP文件以及相同的网站图标，而且，这些网站中使用的背景图片大多数也能够在源码图片文件夹中找到：

 [![](https://p3.ssl.qhimg.com/t0155b5be0847eeead4.png)](https://p3.ssl.qhimg.com/t0155b5be0847eeead4.png)

通过分析源代码我们发现，这些平台使用Bootstrap进行前端设计以及使用ajax来加载网站内容。在CSS文件中，我们发现这个文件是一个名为**Pixelcave**的作者写的。通过搜索Pixelcave，我们发现他们提供了基于Bootstrap的网站设计，这些设计看起来跟我们检查过的在线中文DDoS网站一样。我们还注意到，Pixelcave的标志出现在我们发现的许多DDoS网站的右上角。

 [![](https://p1.ssl.qhimg.com/t0127d2ac47d21a5e2e.png)](https://p1.ssl.qhimg.com/t0127d2ac47d21a5e2e.png)

Pixelcave的标志，它出现在我们确定的所有DDoS网站上。

通过对源代码的分析我们发现，该平台具有从mysql数据库提取信息并根据用户的支付来评估用户身份（即攻击次数，攻击持续时间，以及允许用户的并发攻击次数）的功能。然后，它允许用户输入主机，选择攻击方法（即NTP，L7）和持续时间。如果ddos平台支持该功能，并且用户输入的目标未被列入黑名单，那么平台就会调用服务器开始执行ddos攻击。

有趣的是，源代码提供了站点黑名单功能，用以说明哪些站点默认是不允许被攻击的，其中包含以“**.gov**”和“**.edu**”结尾的站点，但是这个黑名单是可以修改的。此外，它附带了一个预先加载的服务条款（中文），以免除网站管理员对“非法”攻击行为的任何法律责任，并声称该平台服务仅用于测试目的。该代码还允许管理员监控用户已付款、未付款、登录和攻击总次数以及有关攻击的详细信息，如主机，攻击持续时间以及哪个服务器正在执行攻击。源代码原来是用英文写的，经过修改后可以在ddos平台上显示中文图片（例如广告）。源代码中支持PayPal和Bitcoin这两种第三方支付系统，但中国的管理员很可能会将其切换到中国的第三方支付系统，如第三方支付网站或支付宝等。我们调查发现，一个图片文件夹中的Paypal图标被更改为了支付宝的图标。

关于源代码的始末，本文并不是很清楚。但是，有几个提供在线DDoS服务的英文网站，例如DataBooter这个ddos工具站点。这些网站与中国DDoS平台有一些相似之处。例如，它们具有基于bootstrap的设计，托管在Cloudflare上，并使用相似的图像来表示攻击次数，用户数和服务器数量。

 [![](https://p1.ssl.qhimg.com/t01a5d0fa4c8f3711af.png)](https://p1.ssl.qhimg.com/t01a5d0fa4c8f3711af.png)

过去几年来，Talos团队已经监测到在某些黑客论坛上，一些网络黑客销售英文版DDoS平台源代码的行为，中国黑客可能通过购买获得这个源代码并基于它的源代码，并将其汉化以销售给更多的中国用户。

<br>

**结论**

****

近期，关于中国在线DDoS平台数量上升似乎与中国黑客论坛出售ddos平台源代码相关。该源代码似乎最初由国外的黑客编写，之后被中国的黑客汉化。

在线DDoS平台能够提供易于使用的界面，并且可以为用户提供了所有必要的基础设施，因此不需要用户构建僵尸网络或购买额外的服务。因此，用户可以通过可信支付站点购买激活码，然后简单地输入其想要攻击的目标，这样即使是新入门的管理员也能够发起强大的ddos攻击。

**Talos团队将继续监控中国黑客论坛和社交软件群聊，持续研究和分析新建的在线中文DDoS平台以及中国DDoS行业的发展趋势。**

**<br>**

**IOCS**

****

**在线DDoS网站**

www[.]794ddos[.]cn

www[.]dk.ps88[.]org

www[.]tmddos[.]top

www[.]wm-ddos[.]win

www[.]tc4[.]pw

www[.]hkddos[.]cn

www[.]ppddos[.]club

www[.]lnddos[.]cn

www[.]711ddos[.]cn

www[.]830ddos[.]top

www[.]bbddos[.]com

www[.]941ddos[.]club

www[.]123ddos[.]net

www[.]the-dos[.]com

www[.]etddos[.]cn

www[.]jtddos[.]me

www[.]ccddos[.]ml

www[.]87ddos[.]cc

www[.]ddos[.]cx

www[.]hackdd[.]cn

www[.]shashenddos[.]club

www[.]minddos[.]club

www[.]caihongtangddos[.]cn

www[.]zfxcb[.]top

www[.]91moyu[.]top

www[.]xcbzy[.]club

www[.]this-ddos[.]cn

www[.]aaajb[.]top

www[.]ddos[.]qv5[.]pw

www[.]tdddos[.]com

www[.]ddos[.]blue

**IP**

104[.]18.54.93

104[.]18.40.150

115[.]159.30.202

104[.]27.161.160

104[.]27.174.49

104[.]27.128.111

144[.]217.162.94

104[.]27.130.205

103[.]255.237.138

45[.]76.202.77

104[.]27.177.67

104[.]31.86.177

103[.]42.212.68

142[.]4.210.15

104[.]18.33.110

104[.]27.154.16

104[.]27.137.58

23[.]230.235.62

104[.]18.42.18

162[.]251.93.27

104[.]18.62.202

104[.]24.117.44

104[.]28.4.180

104[.]31.76.30
