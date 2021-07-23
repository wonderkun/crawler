> 原文链接: https://www.anquanke.com//post/id/86756 


# 【技术分享】禁用WiFi就能阻止安卓手机发送数据？太天真了少年！


                                阅读量   
                                **123083**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：hal.inria.fr
                                <br>原文地址：[https://hal.inria.fr/hal-01575519/document](https://hal.inria.fr/hal-01575519/document)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01b59fc538bdbf6cfe.jpg)](https://p5.ssl.qhimg.com/t01b59fc538bdbf6cfe.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

有研究结果表明[5，7]，智能手机发出的Wi-Fi信号可以用来被动追踪用户的生活轨迹。通常情况下，人们会关闭设备的Wi-Fi开关，以此阻止这种跟踪行为（参考链接[1](http://lifehacker.com/how-retail-stores-track-you-using-your-smartphone-and-827512308)，[2](https://nakedsecurity.sophos.com/2014/06/12/apples-ios-8-will-help-keep-out-wi-fi-marketers-and-snoops-but-not-totally/)）。事实上，Wi-Fi跟踪行业的从业者也建议用户使用这种方法来避免被跟踪。

Android系统在设备上提供了启用或禁用Wi-Fi功能的选项。然而，通过这个选项禁用Wi-Fi并不足以**完全阻止**设备的Wi-Fi活动。我们做了多项测量实验，最终确认多个Android设备存在这一行为。

**<br>**

**二、Android上的Wi-Fi**

**2.1 Android Wi-Fi扫描**

Android系统支持Wi-Fi协议以提供网络连接功能。与其他启用Wi-Fi的系统一样，Android需要依赖Wi-Fi服务探测机制来探测附近可用的Wi-Fi接入点。与普遍观念[4]不同的是，Android与大多数移动系统一样，使用了主动服务探测机制来主动搜索附近的接入点。为了做到这一点，Android设备会进行主动扫描，在扫描过程中，设备会发送无线**探测请求**（probe requests）报文，请求报文中包含设备自己的（通常也是唯一的）**MAC**地址信息。接入点会通过**探测响应**（probe responses）报文来通知设备。

如今，Wi-Fi服务发现也被用来**获取位置信息**。Wi-Fi接入点可以通过唯一的**BSSID**（MAC地址）进行标识，**作为地标来获取位置信息**。在基于Wi-Fi的定位引擎的帮助下，人们可以在Wi-Fi扫描过程中获得一份接入点清单，从这个清单中推测具体的地理位置信息。在Android中，系统使用Wi-Fi扫描来启用网络连接功能以及定位功能[3]。

然而，设备不单单使用Wi-Fi扫描来推测位置信息，分析公司现在也利用Wi-Fi探测请求报文来估计商场及商店中的用户数量，并记录用户的流动性。实际上，通过统计探测请求报文中不同的MAC地址数，零售商可以得出商店中智能手机的数量。由于许多地方都能获得用户设备的MAC地址，因此可以通过跟踪这些MAC地址来实现对用户地理位置的跟踪。

**2.2 Android中与Wi-Fi有关的设置**

Android系统中有很多配置选项可以影响设备的Wi-Fi功能。其中最为明显的一个选项是Wi-Fi开关（如图1a所示）。当这个开关处于激活状态时，操作系统以及应用程序（只要程序具备足够的权限）就可以使用Wi-Fi接口的全部功能。当开关处于关闭状态时，Wi-Fi网络连接不可用，应用程序无法获得Wi-Fi扫描的结果。

另一个选项是“**始终允许扫描**（Always allow scanning）”选项（如图1b所示），启动这个选项后，即使设备的Wi-Fi开关处于关闭状态，也能执行Wi-Fi扫描。在搭载Android 4.4.4版的三星Galaxy S3以及搭载Android 4.3版的Nexus S中，这个选项的具体路径为“**System-&gt;Wi-Fi-&gt;Advanced**”中，在搭载Android 7.0的联想Moto G 5上，这个选项的具体路径为“**Settings-&gt;Location-&gt;Scanning**”，在搭载Android 6.0.1的一加1（OnePlus One）上，我们没有找到这个选项。然而，我们在测试中发现，这个选项处于激活状态，测试结果会在下文中展示。

图1(a).Android 4.4.4中的Wi-Fi开关选项

[![](https://p4.ssl.qhimg.com/t0166580b2cd1eca13b.png)](https://p4.ssl.qhimg.com/t0166580b2cd1eca13b.png)

图1(b).Android 4.4.4中的"始终允许扫描"选项

[![](https://p0.ssl.qhimg.com/t018dd8e4deb1ea12cd.png)](https://p0.ssl.qhimg.com/t018dd8e4deb1ea12cd.png)

**<br>**

**[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/2.png)三、分析设备产生的Wi-Fi活动**

我们对5个设备进行了测试，所涉及的Android系统范围从2.2.1到6.0.1。实验设备具体如下：

**Galaxy S3**：Samsung Galaxy S3（GT-I9…），Android 4.4.4

**HTC wildfire**，Android 2.3.7，CyanogenMod 7.2.0

**Samsung Galaxy Spica**，Android 2.2.1，CyanogenMod 6.1.1

**Nexus S**，Android 4.3，CyanogenMod 10.2.1.1

**OnePlus One**，Android 6.0.1，CyanogenMod 13.1.2

**3.1 实验方案**

我们对每个智能手机在不同的设置以及不同的活动下产生的Wi-Fi流量进行了监控。设备与接入点之间没有关系。为了监控Wi-Fi活动，我们使用了一个**处于监控模式下的Wi-Fi无线网卡**，在固定信道上捕获流量。我们从收集到的Wi-Fi帧中提取源MAC地址，以识别某个设备生成的流量。事实上，这些设备发出的所有Wi-Fi帧的头部中都包含设备的MAC地址（这些设备并不支持MAC地址随机化）。

我们考虑了如下几个选项：

**Wi-Fi开关**：这个选项可以控制Wi-Fi是否处于激活状态。

**始终允许扫描**（Always allow scanning）：当Wi-Fi处于关闭状态时，这个选项可以允许设备进行Wi-Fi扫描。

**定位**（Location）：这个选项能够控制定位功能。在某些设备中，这个选项分为两个选项：基于GPS的地理位置选项以及基于蜂窝数据/Wi-Fi的地理位置选项。我们只考虑后一种情况。

我们测试了以下几种活动状态，我们认为这几种状态可以反映设备的常见用途：

**点亮屏幕**（Screen on）：屏幕点亮，在设备上切换多个面板，在几分钟内保持这个状态。

**空闲**（Idle）：5分钟内没有接触设备，使屏幕自动关闭。

**退出空闲状态**（Leaving idle）：按下电源键，使设备离开空闲状态。

**Google Maps**：设备正在运行Google Maps。

**启动Google Maps**：用户启动Google Maps。

**不相关状态**（Uncorrelated）：此事件发生时，与用户的具体活动没有任何明显的关联性。

对于每个设备，我们尝试了前面提到过的所有选项，然后遍历了上面提及的所有活动状态，捕捉不同状态下设备的Wi-Fi流量。

除了OnePlus One以及Galaxy S3之外，其他所有设备都没有其他互联网连接渠道。

**3.2 测量结果**

我们将测量结果以表格进行展示，在测量期间，设备只产生了**探测请求**（probe request）类型的帧。

**3.2.1 Galaxy S3**

经过测量后，我们发现此设备的Wi-Fi行为由三个参数共同决定，即：“**Wi-Fi开关**”、“**始终允许扫描**”以及“**定位**”选项。显然，当Wi-Fi处于激活状态时，设备可以随时发送Wi-Fi帧，特别是当设备离开空闲模式时更加明显。

启动Google Maps时，如果定位选项同时处于激活状态，那么设备同样会发送探测请求。不论Google Maps是否处于运行状态，我们都可以观察到探测报文。

从以上观测结果中，我们可以发现，**简单禁用掉Wi-Fi并足以完全阻止Wi-Fi的活动**。比如，**如果“始终允许扫描”以及“定位”选项处于启用状态，那么只要使用Google Maps，设备就会产生Wi-Fi流量。这很有可能与使用基于Wi-Fi的Google定位引擎有关。**

表1.Galaxy S3在各种设置下产生的Wi-Fi活动

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/3.png)[![](https://p0.ssl.qhimg.com/t018c1c197b5428e78f.png)](https://p0.ssl.qhimg.com/t018c1c197b5428e78f.png)

只有当Wi-Fi以及“**始终允许扫描**”选项处于禁用状态时，此时不论定位选项是否启用，我们都观察不到设备的Wi-Fi活动。

当定位及Wi-Fi处于禁用状态，而始终允许扫描处于启用状态时，我们观测到了Wi-Fi扫描事件，而这个事件无法与设备上的任何具体的行为联系在一起。也就是说，无论手机上如何操作，这些扫描事件似乎总是会出现。我们并不清楚这些扫描动作的目的何在。

**3.2.2 OnePlus One**

OnePlus One的观测结果如表2所示，这款设备与上一款设备的结果相似，不同的是，我们无法停用OnePlus One的“始终允许扫描”选项。不同之处在于：当Wi-Fi开关以及定位选项全部关闭时，每当离开空闲模式时，该设备仍然会发送一大串探测请求报文。这一行为的具体原因尚未理清，但给我们带来了很麻烦的事情：这意味着除非我们使用设备的飞行模式，或者完全关闭这个设备，否则我们无法阻止设备发送探测请求报文。

表2.OnePlus One在各种设置下产生的Wi-Fi活动

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/4.png)[![](https://p3.ssl.qhimg.com/t015eeaafcd0f431a51.png)](https://p3.ssl.qhimg.com/t015eeaafcd0f431a51.png)

注：在这款设备上，我们无法在设置面板中找到“始终允许扫描”选项。

**3.2.3 Nexus S**

Nexus S的测量结果如表3所示，只与Galaxy S3的结果有些许不同。我们可以注意到，即便Wi-Fi开关以及定位选项处于关闭状态，只要我们切换“始终允许扫描”选项，设备就会发送一大串探测请求报文。

表3. Nexus S在各种设置下产生的Wi-Fi活动

[![](https://p4.ssl.qhimg.com/t0175b25408c9a4e903.png)](https://p4.ssl.qhimg.com/t0175b25408c9a4e903.png)

注：

*：设备会马上提示用户激活定位功能，点击“OK”按钮即可。

**：只要切换“始终允许扫描”选项，设备就会发送一大串探测请求报文。

**3.2.4 HTC WildFire以及Galaxy Spica**

HTC WildFire的测量结果如表4所示，我们对这个结果并不会感到意外。在早期版本的Android系统中，“始终允许扫描”这个选项并不存在，只有Wi-Fi开关处于打开状态时，设备才会发送探测请求报文。我们没有展示Samsung Galaxy Spica的测量结果，因为这一结果与WildFire的结果非常相近，唯一的区别在于，当处于或离开空闲模式时，设备不会发送探测请求报文。

表4.HTC WildFire在各种设置下产生的Wi-Fi活动

[![](https://p2.ssl.qhimg.com/t01e7d6a26e35255e54.png)](https://p2.ssl.qhimg.com/t01e7d6a26e35255e54.png)

注：这个设备搭载的是早期版本的Android系统，不存在“始终允许扫描”选项。

**3.2.5 Moto G5 Plus**

联想Moto G5 Plus的测量结果如表5所示。这个设备搭载了经过稍微定制的Android 7.0系统，并且设备的随机化行为也非常奇怪：只有处于空闲模式时，设备才会在探测报文中使用随机化的MAC地址。只有当Wi-Fi处于禁用状态下，我们才可以通过Wi-Fi设置面板来访问“始终允许扫描”选项，或者我们也可以通过“定位设置”面板来访问这个选项。

表5.Moto G5 Plus在各种设置下产生的Wi-Fi活动

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/7.png)[![](https://p0.ssl.qhimg.com/t01012404ed70963b2c.png)](https://p0.ssl.qhimg.com/t01012404ed70963b2c.png)

注：

*：当处于空闲状态时，设备会持续发送探测请求报文，并且在报文中使用随机化MAC地址，其他情况下会使用真实的MAC地址。

**3.2.6 对测量结果的总结**

当Wi-Fi处于激活状态时，所有设备都会发送Wi-Fi报文，这点与我们的预期相符。当Wi-Fi处于禁用状态时，根据设备搭载的Android系统版本的不同，我们观察到两种不同的行为。对于老版本系统而言（2.2.1以及2.3.7版），当关闭Wi-Fi时，我们没有观察到Wi-Fi报文。对较新的版本而言（4.3以及更高版本），Wi-Fi行为取决于“始终允许扫描”选项是否启用。当“始终允许扫描”选项激活时，不论设备的Wi-Fi开关是否关闭，设备都会发送Wi-Fi报文。为了完全禁止设备发送Wi-Fi报文，我们需要同时禁用Wi-Fi以及“始终允许扫描”选项。我们注意到OnePlus One这款设备中没有“始终允许扫描”选项，因此，使用这款设备时，只有关闭手机或者使用飞行模式，否则我们无法阻止手机发送Wi-Fi报文。

**3.3 探测频率**

探测频率与具体设备、配置以及使用场景有关。虽然我们的研究目的并不是想找出具体的差别，我们可以发现，在某些场景下，设备发送信号的频率会处于较高水平。在这种情况下，对设备进行跟踪的可能性就会大大提高。比如，对于OnePlus One这款设备来说，如果Wi-Fi开关或者定位选项处于启用状态，当用户打开Google Maps应用时，设备就会以每5秒一次的频率来发送探测请求报文。

**<br>**

**4、提示激活定位功能**

在某些版本的Android系统上，启动Google Maps时，如果定位功能处于未激活状态，设备就会立刻提示用户激活定位功能。在HTC WildFire上，用户会被重定向到相应的设置面板。在OnePlus One上，只要点击弹出消息中的“OK”按钮，就会马上激活这个选项。如果用户忽略掉这条消息，后续再启动Google Maps时不会再次弹出相应的对话框。然而，如果用户再次点击定位按钮（图2右下角那个按钮），那么这个对话框会再次弹出。在Nexus S上，我们发现有两种情况可能会出现（如图2所示）：

如果Wi-Fi开关处于**禁用**状态，并且定位选项以及“始终允许扫描”选项也处于禁用状态，那么设备会提示用户激活这两个选项，如果用户点击“Yes”按钮，那么就会激活这两个选项。

如果Wi-Fi开关处于**激活**状态，而定位选项以及“始终允许扫描”选项处于禁用状态，设备只会弹出对话框提示用户激活定位选项，没有提示激活“始终允许扫描”选项。

图2(a).启用“始终允许扫描”选项时，Nexus S上的Google Maps提示用户激活Wi-Fi

[![](https://p3.ssl.qhimg.com/t01539b5e890a62bf96.png)](https://p3.ssl.qhimg.com/t01539b5e890a62bf96.png)

图2(b).禁用“始终允许扫描”选项时，Nexus S上的Google Maps提示用户激活Wi-Fi

[![](https://p2.ssl.qhimg.com/t01c3d8734276884634.png)](https://p2.ssl.qhimg.com/t01c3d8734276884634.png)

在OnePlus One上，Google Mpas会弹出对话框，请求用户激活Wi-Fi，如图3所示。

图3(a).简略信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010f6a4cc281fccc7d.png)

图3(b).点击展开按钮后显示详细信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f35df4c0bf719869.png)

**<br>**

**五、总结**

在Android系统上，禁用Wi-Fi并不足以阻止设备发送Wi-Fi报文，某些设备在Wi-Fi被禁用后依然会产生Wi-Fi报文。因此，禁用Wi-Fi后，我们并不能够完全躲避Wi-Fi追踪系统对用户的数据收集行为。为了阻止设备发送Wi-Fi报文，我们需要同时禁用设备上的两个功能：我们必须同时禁用Wi-Fi开关以及“始终允许扫描”选项，才能保证设备处于静默状态。在某些设备上，我们甚至无法看到那个选项，这意味着用户无法阻止手机发送Wi-Fi报文。

虽然Android在较新版的系统中引入了MAC地址随机化机制[1]，还是有一些设备不支持这个功能。从6.0版起，Android开始支持MAC地址随机化功能，而目前54.2%的Android设备依然在使用老版本的系统[2]。此外，只要硬件支持MAC地址随机化，MAC地址随机化就应该处于激活状态，然而这种情况在2017年还非常少见。

**<br>**

**六、参考资料**

[1] [Android 6.0改动](https://developer.android.com/about/versions/marshmallow/android-6.0-changes.html)

[2] [Android平台版本说明](https://developer.android.com/about/dashboards/index.html#Platform)

[3] [Android定位策略](https://developer.android.com/guide/topics/location/strategies.html)

[4] [Android扫描论坛](https://android.stackexchange.com/questions/131414/do-android-devices-make-active-or-passive-scan-when-looking-for-wifi-ap)

[5] [华盛顿时报：商店如何使用用户的WiFi来跟踪用户购物习惯](https://www.washingtonpost.com/news/the-switch/wp/2013/10/19/how-stores-use-your-phones-wifi-to-track-your-shopping-habits/?utm_term=.f1c5d20d116d)

[6] A study of mac address randomization in mobile devices and when it fails. arXiv preprint arXiv:1703.02874, 2017。

[7] Tracking Unmodified Smartphones Using Wi-fi Monitors. In Proceedings of the 10th ACM Conference on Embedded Network Sensor Systems, SenSys ’12, pages 281–294, New York, NY, USA, 2012. ACM。
