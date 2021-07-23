> 原文链接: https://www.anquanke.com//post/id/86934 


# 【技术分享】Red Alert 2:不会用新技术的银行木马不是好程序


                                阅读量   
                                **77600**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：phishlabs.com
                                <br>原文地址：[https://info.phishlabs.com/blog/redalert2-mobile-banking-trojan-actively-updating-its-techniques](https://info.phishlabs.com/blog/redalert2-mobile-banking-trojan-actively-updating-its-techniques)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t013d85ab58f0e841dc.png)](https://p5.ssl.qhimg.com/t013d85ab58f0e841dc.png)

译者：[Janus情报局](http://bobao.360.cn/member/contribute?uid=2954465307)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**简介**



自上周开始，Android银行木马程序[Red Alert 2](https://clientsidedetection.com/new_android_trojan_targeting_over_60_banks_and_social_apps.html)受到了相当多的关注。引发广大吃瓜群众围观的原因可能大家已经知道了，这个木马程序的代码库看起来是全新的，而且木马的部分功能也很独特。PhishLabs情报分析研究部门(R.A.I.D)最近发现了一个Red Alert 2的新样本，这个样本与以前的样本相比，在策略、技术和程序上都有进行修改。那么我们在对这些变化分析之前，先对Red Alert 2的一些有趣的功能进行回顾。



**旧物换新颜**

****

Red Alert 2与现有Android银行木马在功能上有很多共同点。Red Alert 2在后台运行，监视应用程序的活动，当检测到目标相关的活动时，会在设备屏幕上覆盖钓鱼页面。除了之外，它还会窃取系统信息，窃取用户数据，包括联系人、短信、通话记录、窃听或拦截短信/通话，发送短信和USSD请求，以及启动其他应用程序。

[![](https://p4.ssl.qhimg.com/t01d84f240b9924eb6d.png)](https://p4.ssl.qhimg.com/t01d84f240b9924eb6d.png)

图1 指令表

Red Alert 2的独特之处在于，与很多现有的Android银行木马不同，Red Alert 2似乎并不是像BankBot或AceCard一样，是源代码泄露的银行木马的变体，它是全新的。除此之外，它在任务上也与其他的Android木马不同：确定前台应用，更新C&amp;C服务器，获取配置数据。

**1、确定正在运行的应用**

****

 Android银行木马最重要的任务之一就是确定当前在前台运行的应用程序是什么。这个很关键的任务可以帮助银行木马选择基于包名的合适的覆盖层。从一些过去的报告可以看到，银行木马使用过ActivityManager类的getrunningtasks或getrecenttasks方法来确定运行中的应用程序。但是，从Android Lollipop（API Level 21）开始，这些方法已被弃用。所以，这种技术对于Android 5.0和更高版本的设备不适用。为了解决这一问题，Red Alert 2的作者利用了Android Toolbox(一组Linux命令行程序)，以确定当前正在运行的应用程序。图2中的注释显示了用于确定当前运行的应用程序的控制流，图3显示了使用Android Toolbox的代码片段。

[![](https://p4.ssl.qhimg.com/t01c4998b679eb7687a.png)](https://p4.ssl.qhimg.com/t01c4998b679eb7687a.png)

图2 确定正在运行的应用

[![](https://p1.ssl.qhimg.com/t0148f12de8c9437ebc.png)](https://p1.ssl.qhimg.com/t0148f12de8c9437ebc.png)

图3 Android Toolbox调用

值得注意的是，对于API Level 20，Android Wear设备独有的KitKat 4.4W，Red Alert 2要使用UsageStatsManager来确定当前运行的应用程序。 这也就可以解释为什么这款木马需要PACKAGE_USAGE_STATS权限。 方然，这也是很有意思的了，木马开发人员居然为这些Android Wear设备做了特定的调整。

[![](https://p2.ssl.qhimg.com/t015058dde03b067989.png)](https://p2.ssl.qhimg.com/t015058dde03b067989.png)

图4 Android 4.4w usagestatsmanager方法

**2、更新C&amp;C服务器**

长期以来，聊天客户端和社交媒体一直被用于桌面恶意软件的命令和控制，但这些技术尚未广泛应用于移动领域。而Red Alert 2通过利用twitter来更新C&amp;C服务器，将上述技术移植到了移动领域。在刚开始传输的过程中，C&amp;C服务器为在应用的resources中指定的样本服务，如下图5所示：

[![](https://p2.ssl.qhimg.com/t011025f13a3499e4b4.png)](https://p2.ssl.qhimg.com/t011025f13a3499e4b4.png)

图5 应用Resources中的基础配置数据

如果该C&amp;C服务器脱机了，那么样本将计算一个Twitter用户名并查询该帐户的帖子，以检索更新的C2。图6中所示代码片段的代码检查了该帐户的推文，并使用正则表达式来确认推文是否为一个IP地址，格式为4个字节，前两个和最后两个字节由一个空格分隔。这种推文的内容可能是像“10.19 142.7”这种的。IP一旦确认后，这个IP地址将被重新构建，添加HTTP协议，添加端口8060，然后将其保存为样本的新的C&amp;C服务器。

[![](https://p0.ssl.qhimg.com/t014b6d69221b990a1b.png)](https://p0.ssl.qhimg.com/t014b6d69221b990a1b.png)

图6 Twitter C&amp;C服务器更新代码

**3、获取配置数据**

很多Android银行木马将其配置信息硬编码到APK中，或者在安装完成后从C&amp;C服务器下载配置文件。为了避免成为安全研究人员的目标，Red Alert 2利用了“Go Fish”的方法传输配置文件。所有配置数据都存储在C&amp;C服务器上，只有设备“证明”设备中已经安装了目标应用，才会向受感染的设备传输配置文件。

安装后，Red Alert 2利用一个Bot ID来跟踪设备的感染情况，并与C&amp;C服务器通信。然后，受感染的设备将设备中安装的应用程序列表发送到C2。图7展示了一个受感染的设备向C&amp;C服务器发送POST请求。这里base64编码的数据包含了一个已安装应用列表。C&amp;C服务器在接收到已安装程序列表后，响应与已安装应用对应的目标应用的列表。并提供与已安装的目标应用对应的覆盖层HTML代码。该代码保存在设备存储中，当木马检测到目标应用程序在前台运行时才会显示。这个木马的完整配置数据从未提供给受感染的设备，这使得分析非常艰难。

[![](https://p2.ssl.qhimg.com/t01fe830ba8a8b44021.png)](https://p2.ssl.qhimg.com/t01fe830ba8a8b44021.png)

图7 发送给C2服务器的已安装程序列表

<br>

**持续发展态势**

****

正如文章开头所提到的，PhishLabs R.A.I.D.团队最近观察到新的样本在策略、技术和程序方面都有改变，这些手段与最初版本Red Alert 2的分析报告中的样本有关。

**1、目标**

R.A.I.D.对Red Alert 2的最初样本进行了分析。经过分析，我们观察到，该样本的目标是某些金融机构、社交媒体网站、支付网站和零售业务。如前文所述，在没有直接访问C&amp;C的情况下，想要获取目标应用程序的完整列表具有挑战性;然后，我们采取了新的手段，对每一个初始样本进行64个目标程序检测。而最新的样本的目标高达66个，其中有4个目标被移除，6个目标被新添加。被移除的目标包括：西太平洋银行、圣乔治银行、Skype和阿尔斯特银行。新增的目标包括五家俄罗斯银行和Uber。新的目标应用程序详见表1。图8显示了针对新目标Tinkoff银行的覆盖页面。

[![](https://p3.ssl.qhimg.com/t01b8c14954cd2e4a8f.png)](https://p3.ssl.qhimg.com/t01b8c14954cd2e4a8f.png)

表1 新版本Red Alert 2的新目标

[![](https://p2.ssl.qhimg.com/t019b613737a1fc4653.png)](https://p2.ssl.qhimg.com/t019b613737a1fc4653.png)

图8 Tinkoff银行覆盖层

Red Alert 2已经成为目标分布地理多样化的移动银行木马之一。以往情况下，银行木马会针对自己熟悉的领域，制定相应的木马，但是Red Alert 2一点也不按照套路出牌，它的胃口也是特别的大，不先定个小目标，直接想搞全球化。图9展示了Red Alert 2的目标地理分布图。

[![](https://p1.ssl.qhimg.com/t01a77883e134b4be17.png)](https://p1.ssl.qhimg.com/t01a77883e134b4be17.png)

图9 根据目标国家分布的数量统计

**2、基于域名的C2和Cloudflare**

这个新样本，是我们团队观察到的第一个不利用硬编码的IP地址，而利用域名进行命令控制的样本。其实，用不用域名进行命令和控制不重要，但是它打开了使用像CloudFlare这样的CND代理的窗口。我们本文中分析的这个样本就是这么做的，选择了一个带有CloudFlare服务的a.club的域名(我们已经向CloudFlare报告了此事)。进而，利用CloudFlare提供的服务，及多项保护措施，包括反机器人措施和C2服务器真实IP混淆等。这些反机器人措施对安全研究人员的自动分析造成了很大的困扰，C2的IP混淆也让分析人员无法成功定位。

[![](https://p0.ssl.qhimg.com/t01d29c5a2f4c553bcb.png)](https://p0.ssl.qhimg.com/t01d29c5a2f4c553bcb.png)

图10 Cloudflare代理背后的C2域名

**3、服务器端目标标识符**

另一个观察到的变化，是一个很小的改动，是用于从C&amp;C服务器获取覆盖层的惟一标识符的更改。受感染的设备提供给C&amp;C服务器已安装程序列表后，服务器会响应一个应用程序列表以及其对应的唯一ID。接下来，包含这个唯一ID的设备会发送POST请求提示C&amp;C服务器返回响应的覆盖页面HTML代码。在Red Alert 2的初始版本中，这个惟一的ID是一个十六进制字符串，如图11所示。

[![](https://p2.ssl.qhimg.com/t016ac8c97658018f31.png)](https://p2.ssl.qhimg.com/t016ac8c97658018f31.png)

图11 十六进制唯一ID

在最近的样本中，这个惟一标识符被修改为解码后为目标包名称的base64编码的字符串。在某些情况下，会请求第二个屏幕覆盖层，这个时候，唯一标识符是包名和数字2加在一起。这种新格式如图12所示。

[![](https://p1.ssl.qhimg.com/t0147c78e42c58c9675.png)](https://p1.ssl.qhimg.com/t0147c78e42c58c9675.png)

图12  新型base64编码的惟一ID



**总结**

****

虽然这些变化在本质上都不是特别大，但这也说明了Red Alert 2的幕后黑手一直在“积极”运作试图开发出更加“完美”的银行木马。其短期内更新的目标更是显示了快速扩展木马的能力。最终，我们希望Red Alert 2的开发者能够对木马进行更加良好的优化，以保持在日益饱和的移动银行木马市场上保持较高水平的态势。

最后，样本信息及样本分析可在Janus查看，点击这里。

或检索SHA256：**05888c0f55d23c8c4f3b1ad0fe478c3d1610449f45abb9247f59563ac12ff82c**
