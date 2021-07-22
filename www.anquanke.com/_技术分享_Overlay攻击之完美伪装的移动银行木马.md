> 原文链接: https://www.anquanke.com//post/id/87226 


# 【技术分享】Overlay攻击之完美伪装的移动银行木马


                                阅读量   
                                **95165**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：riskiq.com
                                <br>原文地址：[https://www.riskiq.com/blog/labs/mobile-bankbot/](https://www.riskiq.com/blog/labs/mobile-bankbot/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0127bc81de5c80dabf.jpg)](https://p0.ssl.qhimg.com/t0127bc81de5c80dabf.jpg)



译者：[Janus情报局](http://bobao.360.cn/member/contribute?uid=2954465307)

预估稿费：130RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

****提到移动银行木马，一些应用其实暗藏玄机。

很多智能手机用户越来越倾向于在生活中利用投资类应用理财。移动应用开发者为了满足智能用户对于这类应用快捷、方便的需求，开发了适用于多种场合的应用，支持多种资金模式。然而，有一些恶意应用，借着该类应用的外壳，请求着本不应该涉及的权限。



**检测**

RISKIQ最近在谷歌商店发现了一款名为“**Cryptocurrencies Market Prices**”的应用。表面来看，这款应用承诺，会及时为关注加密货币市场的用户提供资讯。然而，这些用户并没有意识到，他们的账户信息已经被别人看的一清二楚。“Cryptocurrencies Market Prices”属于移动木马的[银行木马](https://www.riskiq.com/blog/labs/marcher-android-bankbot/)家族，利用[overlay](https://threatpost.com/android-overlay-and-accessibility-features-leave-millions-at-risk/125888/)技术，伪造各种金融和零售行业相关的移动应用页面，钓鱼获取敏感数据。

通过使用社会工程学，驱动下载，和其他安装方法，应用程序会授予自身权限，特别是针对目标Android设备。一旦安装该应用，银行木马会监视该设备的目标应用列表。如果设备中存在目标应用，银行木马会在合法应用的最上方打开一个窗口，利用伪造钓鱼页面，诱导用户输入数据，通常情况下这些数据是银行客户的登录凭证。这些被窃取的凭证接下来就会被不法分子用于恶意交易。这个恶意应用也可以劫持TAN(Transaction Authentication Number)(交易验证码)消息和双因素授权使用的文本信息，用于让不法分子授权进行交易。

下面是一个银行木马利用社会工程学分发的实例。用户在他们的Android设备上手动下载和安装功能齐全的应用程序，将加密货币市场价格与法定货币价值进行比较。一旦安装完毕，呈现给用户的是一个看似可以对加密货币的汇率进行监控的应用：

[![](https://p4.ssl.qhimg.com/t0112bdb675b0a3e1d4.png)](https://p4.ssl.qhimg.com/t0112bdb675b0a3e1d4.png)

图1 看似合法的应用

然而，银行木马用看似合法应用的外表隐藏了它真实的目的。通过提供给受害者一个真实有用的应用程序，用户是不太会对此类应用进行过多怀疑的。



**移动应用木马权限&amp;意图**

上面我们说的那个木马在安装的过程中请求了以下权限(根据应用假定的功能，红色标注的为可疑的权限)：

**android.permission.RECEIVE_SMS**

**android.permission.READ_PHONE_STATE**

**android.permission.READ_SMS**

**android.permission.RECEIVE_MMS**

**android.permission.INTERNET**

**android.permission.SEND_SMS**

**android.permission.WRITE_EXTERNAL_STORAGE**

**android.permission.WRITE_SMS**

**com.crypto.theapp.permission.C2D_MESSAGE**

**android.permission.READ_EXTERNAL_STORAGE**

**android.permission.ACCESS_NETWORK_STATE**

**android.permission.WAKE_LOCK**

**com.google.android.c2dm.permission.RECEIVE**

除了上述权限，应用也有很多过滤器。这些过滤器允许应用响应或请求某些功能。我们对com.sws和com.google.firebase的过滤器进行了一些分析：

[![](https://p1.ssl.qhimg.com/t0103eed2a364a27be0.png)](https://p1.ssl.qhimg.com/t0103eed2a364a27be0.png)

图2 意图过滤器列表

基于已获得的权限，应用可以拦截和编写短信内容。另一个有趣的点是，应用修改了一个名为Firebase的开发平台，这个平台允许监视例如存储、身份验证和分析等活动。



**应用分析**

这个应用，正如本文“检测”部分描述的那样，是一个捆绑应用，它是合法功能和银行木马的结合体。合法功能——将加密货币价格与全球货币价值进行比较。在下面的分析中，它并未使用混淆技术，代码是可读的。我们可以追踪到短信接收功能的调用，这里暴露了最初的C2信息：

[![](https://p4.ssl.qhimg.com/t01380132d2c1b4c9c9.png)](https://p4.ssl.qhimg.com/t01380132d2c1b4c9c9.png)

图3 可疑代码

[![](https://p2.ssl.qhimg.com/t01e0273338f64fe37f.png)](https://p2.ssl.qhimg.com/t01e0273338f64fe37f.png)

图4 C2服务器的足迹

通过观察相关函数的调用，在合法的Firebase库中有一些修改的迹象：

[![](https://p4.ssl.qhimg.com/t0114e808fe89efd814.png)](https://p4.ssl.qhimg.com/t0114e808fe89efd814.png)

图5 Firebase库的修改痕迹

该应用似乎针对波兰的各大银行。以下是代码中目标银行的包名：

**“com.comarch.mobile”**

**“pl.ing.mojeing”**

**“eu.eleader.mobilebanking.pekao”**

**“eu.eleader.mobilebanking.raiffeisen”**

**“pl.bzwbk.bzwbk24”**

**“pl.fmbank.smart”**

**“pl.mbank”**

**“wit.android.bcpBankingApp.millenniumPL”**

**“pl.pkobp.iko”**

**“pl.plus.plusonline”**

C2服务器托管在91[.]226[.]11[.]200。它主要是提供波兰各银行的钓鱼覆盖页面，记录从受感染设备中发送的信息，并充当黑客的管理平台。以下是对应的WHOIS信息，它显示了一个俄罗斯的地址。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a922f655ccb89ccb.png)

图6 WHOIS信息



**结论**

在检测到该应用的恶意行为后，谷歌商店迅速将“Cryptpocurrencies Market Prices”下架。然而，这也提醒了广大吃瓜群众，在下载应用前需要对应用进行评估，即使应用来自可信的应用市场。下图所示，你可以看到它最初在谷歌市场，该应用即使包含了恶意代码，但是仍然被打上了“verified”的标记。

[![](https://p1.ssl.qhimg.com/t01c7e381e5482fb940.png)](https://p1.ssl.qhimg.com/t01c7e381e5482fb940.png)

图7 被标记为“verified”也可能暗藏玄机



**IOCs**

**MD5**：ce8c3d0a4c71eff3e83879e3002e01ea

**SHA1**：fc34bbb131e464efd630836cfe6c07aa51aa5c44

**SHA256**：75759cc9af54e71ac79fbdc091e30b4a6e5d5862d2b1c0decfb83c9a3d99b01b

**IP**：91.226.11.200

**应用样本**：[http://cloud.appscan.io/search-app.html#type=app&amp;q=all:&amp;page=1&amp;val=ce8c3d0a4c71eff3e83879e3002e01ea](http://cloud.appscan.io/search-app.html#type=app&amp;q=all:&amp;page=1&amp;val=ce8c3d0a4c71eff3e83879e3002e01ea)

**规则匹配：**[https://www.appscan.io/monitor.html?id=5a0a6ba702723830409eec19](https://www.appscan.io/monitor.html?id=5a0a6ba702723830409eec19)
