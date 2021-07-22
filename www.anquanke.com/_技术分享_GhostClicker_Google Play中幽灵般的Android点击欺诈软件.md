> 原文链接: https://www.anquanke.com//post/id/86705 


# 【技术分享】GhostClicker：Google Play中幽灵般的Android点击欺诈软件


                                阅读量   
                                **98947**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.trendmicro.com
                                <br>原文地址：[http://blog.trendmicro.com/trendlabs-security-intelligence/ghostclicker-adware-is-a-phantomlike-android-click-fraud/](http://blog.trendmicro.com/trendlabs-security-intelligence/ghostclicker-adware-is-a-phantomlike-android-click-fraud/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01941861c02254fd6f.jpg)](https://p1.ssl.qhimg.com/t01941861c02254fd6f.jpg)

****

<br>

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**写在前面的话**

近期，趋势科技的安全研究专家在Google Play应用商店中发现了一款自动点击型恶意软件，这款恶意广告软件名叫**GhostClicker**，它的影响范围非常大，目前在大约有Google Play应用商店中大约有340多款移动端应用程序感染了GhostClicker。

值得注意的是，其中有一款感染了GhostClicker的应用程序名叫“Aladdin’s Adventure’s World”，而这款App的下载次数目前已经达到了**五百万次**。除此之外，嵌入了这款恶意广告软件的应用程序种类还包括休闲游戏、设备性能工具（例如清理工具或加速工具）、文件管理器、二维码/条形码扫描工具、多媒体录音器/播放器、以及一些与GPS定位导航相关的应用程序。

虽然绝大部分感染了GhostClicker的应用程序目前均已从Google Play应用商店下架，但是在2017年8月7日时仍然有**101**个相关App仍可从Google Play应用商店中下载获取。根据我们的检测工具以及传感器数据显示，目前GhostClicker的活动主要在**巴西、日本、台湾、俄罗斯、意大利、美国和部分东南亚国家**比较频繁。

**<br>**

**GhostClicker分析**

根据这款恶意广告软件的特性，即它不仅能够完成自动点击任务并隐藏在Google移动设备服务（GSM）之中，而且它还使用了Google当前最流行的应用程序编程接口（API），趋势科技的研究人员将这种恶意软件标记为了GhostClicker（**ANDROIDOS_GHOSTCLICKER.AXM**）。除此之外研究人员还发现，GhostClicker甚至还可以隐藏在Facebook的广告软件开发套件（Facebook Ad SDK）之中。为了避免自己被安全产品检测到，它会将自己伪装成一个合法的应用程序组件（伪装成一个名叫“logs”的包），然后将自己嵌入在这两个服务（即Google的API以及Facebok的SDK）之中。

下图显示的是Google Play应用商店中的一款嵌入了GhostClicker的应用程序，我们可以看到其下载量/安装量已经达到了**五百万次**：

[![](https://p1.ssl.qhimg.com/t01ce30af76012ed09c.png)](https://p1.ssl.qhimg.com/t01ce30af76012ed09c.png)

下图显示的是GhostClicker隐藏在GMS以及Facebook Ad SDK之中的代码：

[![](https://p3.ssl.qhimg.com/t01a29cf061a255c4d8.png)](https://p3.ssl.qhimg.com/t01a29cf061a255c4d8.png)

虽然GhostClicker感染范围比较大，而且其持久化感染的能力也比较强，但是它也非常“**挑食**”，因为它在运行的过程中还有各种各样的要求。比如说在启动的时候，受感染的应用程序需要获取设备的系统属性（http.agent），而这个属性是用来配置安卓设备的**User-Agent**字符串的。如果这个字符串中包含“**nexus**”字样的话，GhostClicker进程将不会被触发。趋势科技的研究人员则认为，这种运行机制的目的是为了**逃避沙盒检测**，例如安卓操作系统内置的安卓应用程序沙箱（Android Application Sandbox），因为安卓模拟器或沙盒环境一般都命名为“Nexus XXX”。

下图显示的是当设备http.agent属性中不包含字符串“**nexus**”时，GhostClicker的触发和运行过程：

[![](https://p2.ssl.qhimg.com/t01e108582c613b8997.png)](https://p2.ssl.qhimg.com/t01e108582c613b8997.png)

在趋势科技所分析的受感染应用程序中，某些感染了GhostClicker的App在第一次运行时还会请求获取设备的管理员权限，但是它们并不会给用户声明程序的安全策略以及管理员权限的用途（例如擦除数据或重置密码）。除此之外，GhostClicker还会增加卸载应用程序的难度，并通过这种方式来阻止用户删除那些感染了GhostClicker的应用程序。研究人员表示，当用户想卸载这些App时，卸载的过程会非常的不友好：首先，卸载App不仅需要用户拥有管理员权限，而且在卸载之前还需要先禁用App才行。

下图显示的是感染了GhostClicker的应用程序在请求设备管理员权限时的界面：

[![](https://p1.ssl.qhimg.com/t012893b6315ecce586.png)](https://p1.ssl.qhimg.com/t012893b6315ecce586.png)

从下图中可以看到，某些用户在Google Play应用商店中报告称自己无法卸载App（感染了GhostClicker）：

[![](https://p1.ssl.qhimg.com/t01ccdfea8e9382a144.png)](https://p1.ssl.qhimg.com/t01ccdfea8e9382a144.png)

研究人员表示，GhostClicker目前主要通过自动点击欺诈来获取非法收入。但是与其他类型的恶意广告软件不同，GhostClicker在定位、获取和点击广告时并没有使用JavaScript代码，它主要通过向AdMob（Google自己的移动广告平台）注入自己的代码来获取到广告所在的位置。在获取到设备的屏幕尺寸（屏幕的宽度和高度）之后，它会计算出合适的X、Y坐标，然后使用**dispatchTouchEvent** API来模拟用户的点击行为。

为了赚取更多的收入，GhostClicker还会生成虚假流量。当用户点击Google Store中其他App的下载链接时它会弹出自己的窗口，而且它还可以通过后台的命令控制服务器（C&amp;C）在受感染设备的浏览器中打开YouTube视频链接。在获取到了设备的管理员权限之后，GhostClicker每分钟都会重复执行这些自动点击操作。

下图显示的是GhostClicker注入在AdMob中的代码，这段代码用于获取AdMob的Context View：

[![](https://p5.ssl.qhimg.com/t01e5c3c06142102c97.png)](https://p5.ssl.qhimg.com/t01e5c3c06142102c97.png)

下图显示的是GhostClicker计算生成的坐标信息：

[![](https://p1.ssl.qhimg.com/t01b6cdea448a5b8d46.png)](https://p1.ssl.qhimg.com/t01b6cdea448a5b8d46.png)

下图显示的是GhostClicker根据X、Y坐标构建MotionEvent（模拟用户的点击行为）的相关代码：

[![](https://p1.ssl.qhimg.com/t01a37fdf98ed444bf7.png)](https://p1.ssl.qhimg.com/t01a37fdf98ed444bf7.png)

下图显示的是GhostClicker使用dispatchTouchEvent API实现自动点击广告的代码：

[![](https://p2.ssl.qhimg.com/t013d055090fbc02b88.png)](https://p2.ssl.qhimg.com/t013d055090fbc02b88.png)

**<br>**

**本文所分析的GhostClicker样本仍为初级版本**

趋势科技的研究人员通过对GhostClicker的跟踪分析后发现，GhostClicker当前的版本仍为初级版本。GhostClicker后来的版本似乎移除了自动点击功能以及设备管理员权限请求，这样做很可能是为了增加这款恶意广告软件的隐蔽性。当用户解锁手机屏幕之后，只要该设备接入了网络，那么GhostClicker将会定时（间隔一定的时间）弹出广告界面，而且我们在Aladdin’s Adventure’s World应用程序中发现的正是这种更新版本的GhostClicker。

在对这款恶意广告软件的活动时间线进行分析之后，我们还发现早在一年多以前就已经有应用程序感染了GhostClicker，而GhostClicker最早在2016年的8月份就已经感染了GMS的SDK了。从2017年3月份开始，GhostClicker去掉了自动点击功能，转而开始利用Admob、Startapp和Facebook Ads并通过接收C&amp;C命令来弹出间隙广告。到2017年5月份，GhostClicker又将自动点击功能重新整合了进来，并且感染了Facebook Ad的SDK。

**<br>**

**缓解方案以及最佳实践**

虽然广告在移动端生态系统中是一种很容易被人们忽略的因素，但是GhostClicker的存在充分证明了广告也可以成为网络犯罪分子的攻击向量。恶意广告软件的侵略性不言而喻，再加上这些恶意软件会消耗掉目标设备的大量资源（CPU、电池和流量等等），因此恶意广告软件也逐渐成为了一种非常严重的安全威胁。除此之外，它们还会在用户毫不知情的情况下收集目标用户的个人数据，并使用户的隐私暴露在安全风险之中。最最重要的是，恶意广告软件还有可能让用户感染上真正的恶意软件，而此时用户面临的将不仅仅是恶意广告那么“简单”的问题了。

首先，我们可以通过限制设备管理员功能/权限来缓解GhostClicker所带来的威胁。一般来说，设备管理员功能主要适用于一些安全程序，例如反病毒产品，而一般的用户基本上是不需要使用这些权限和功能的。

其次，用户需要定期更新设备的操作系统，并遵循设备制造商给出的安全使用建议。企业用户在使用公司设备或在BYOD环境中时同样需要做到这些。除此之外，当你在下载一款应用程序时，请一定要先看一看其他用户对这款应用程序的评论，如果这款应用程序有问题的话，你肯定能够在评论区中发现的。

**<br>**

**总结**

目前，趋势科技的研究人员已经将该威胁上报给了Google的安全团队，并且正在与Google的技术人员配合将Google Play上的受感染App下架。

注：关于GhostClicker的入侵威胁指标（IoC）、相关哈希（SHA256）、包名以及App标签等内容，请参考【[附录](https://documents.trendmicro.com/assets/Appendix-GhostClicker-Adware-is-a-Phantomlike-Android-Click-Fraud.pdf)】。
