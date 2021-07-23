> 原文链接: https://www.anquanke.com//post/id/85172 


# 【技术分享】Android Doze机制与木马的绕过方式


                                阅读量   
                                **164708**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01a26b7d1925a36bf0.jpg)](https://p5.ssl.qhimg.com/t01a26b7d1925a36bf0.jpg)

**一、   概述**

Android 6.0引入的Doze机制本意在于节省系统耗电量，延长电池的使用时间，但是却在抑制恶意软件对系统资源的占用上发挥了神奇的效果，恶意软件因此也开始探索绕过Doze机制的手段。文本将为大家简要介绍Doze的功能，并从安全的角度解读Doze的奇效，最后揭露一款绕过Doze机制的恶意软件。

[![](https://p4.ssl.qhimg.com/t01cbfe6433610b7577.png)](https://p4.ssl.qhimg.com/t01cbfe6433610b7577.png)

**二、  Doze简介**

**(一)  Doze功能详情**

Android 6.0(API 23)为用户和开发者带来了许多新功能，Doze（打盹）即为其中的一项。**Doze的主要目的是节省设备的耗电量**，即当设备未连接至电源，且长时间处于闲置状态时，系统会将应用置于“打盹”模式。在这个模式下，不在白名单中的应用将无法连接网络和占用CPU资源，并且其作业、同步和标准闹铃的运行时间将被推迟。由于该模式与API版本无关，因此未适配API 23及其后版本的应用只要运行在Android 6.0及更高版本的系统下，就会受到Doze模式影响。

如图1所示，应用了Doze模式的Android系统在满足了上述进入Doze状态的条件后，会周期性地退出Doze状态进入一段时长为30秒的，被称为maintenance window的时间段。在此期间，系统会退出Doze模式以使得应用完成被延时的任务。从图中可以看出随着Doze状态的持续，设备距离下一次被唤醒的等待时间会越来越长。

[![](https://p2.ssl.qhimg.com/t01e12a5a86080ae034.png)](https://p2.ssl.qhimg.com/t01e12a5a86080ae034.png)

图1 Doze模式下的maintenance window状态示意

(图片来源：[https://developer.android.com/training/monitoring-device-state/doze-standby.html?hl=en](https://developer.android.com/training/monitoring-device-state/doze-standby.html?hl=en))

**当系统处于Doze模式下，系统和白名单之外的应用将受到以下限制**：

1.无法访问网络；

2.Wake Locks被忽略；

3.AlarmManager闹铃会被推迟到下一个maintenance window响应，除非使用setAndAllowWhileIdle()或SetExactAndAllowWhileIdle()设置闹铃。与此同时，setAlarmClock()设置的闹铃在Doze模式下仍然生效，但系统会在闹铃生效前退出Doze；

4.系统不执行Wi-Fi扫描；

5.系统不允许同步适配器运行；

6.系统不允许JobScheduler运行；

需要注意的是，开发者仍然可以使用官方提供的GCM服务（Google Cloud Messaging）使得应用可以在Doze模式下传递消息并被允许临时访问网络服务和部分Wake Locks，这一机制通过高优先级GCM消息启用，且不会影响Doze模式。

<br>

**(二)  Doze模式下的白名单**

Google官方认为，开发者通过合理安排任务和使用官方提供的GCM高优先级消息，大部分应用应该能与Doze模式兼容。对于剩下的那一小部分应用，系统则提供了一份可配置的白名单。位于白名单中的应用可以继续使用网络并保留部分wake lock，但作业和同步仍然会被推迟，常规的AlarmManager闹铃也不会被触发。Android developers提供了一个列表来指导开发者确定自己的应用需要使用哪些方式。

[![](https://p4.ssl.qhimg.com/t0117276c39f7af7ad6.png)](https://p4.ssl.qhimg.com/t0117276c39f7af7ad6.png)

表1 对GCM和白名单的使用指导

(图片来源：[https://developer.android.com/training/monitoring-device-state/doze-standby.html?hl=en](https://developer.android.com/training/monitoring-device-state/doze-standby.html?hl=en))

对于用户，可以直接进入设置-&gt;电池-&gt;电池优化中进行设置：

[![](https://p4.ssl.qhimg.com/t01b65f013c558c41df.png)](https://p4.ssl.qhimg.com/t01b65f013c558c41df.png)

图2 白名单设置界面

开发者可以调用PowerManager.isIgnoringBatteryOptimizations方法检测应用是否在白名单中。若应用不在白名单中，开发者可以在AndroidManifest.xml中申请REQUEST_IGNORE_BATTERY_OPTIMIZATIONS权限，并使用一个包含了ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS的 Intent弹出对话框让用户选择将本应用加入白名单中。在用户对应用设置了白名单之后，可以根据需要从白名单中移除应用。

[![](https://p2.ssl.qhimg.com/t0134626d080cb52e3d.png)](https://p2.ssl.qhimg.com/t0134626d080cb52e3d.png)

图3 通过发送Intent触发对话框

<br>

**三、  Doze对恶意软件的影响**

现在我们抛开Doze的省电功效，从安全的角度来探讨Doze的奇效。Doze实现省电的方式本质上是系统通过全局调控的方式限制应用程序对资源的占用，这种调控方式的产生表明了系统对于应用程序在资源占用方式上的态度转变——从“放任自由”到开始强有力的“调控”，调控产生了两种神奇的效果：

1.在Android 6.0以前，内核通过任务调度机制来决定应用程序对资源的占用，而Doze的产生意味着在内核之上产生了一层优先“调度”机制，**这层“调度”机制能够改变应用程序对于系统资源的占用比例**；

[![](https://p2.ssl.qhimg.com/t01d206e0e8319fe96d.png)](https://p2.ssl.qhimg.com/t01d206e0e8319fe96d.png)

图4  Android 6.0以前任务调度方式

[![](https://p2.ssl.qhimg.com/t01e71d0f77490229f0.png)](https://p2.ssl.qhimg.com/t01e71d0f77490229f0.png)

图5  引入Doze后任务“调度”方式

2.在Android 6.0以前，恶意软件对资源的占用权利同其他同级应用一样，均由内核统一调度。而引入Doze之后，应用程序对资源的占用权利将按功能的需要予以适当分配（详情见“Doze模式下的白名单”），这意味着**正常的应用程序由于其功能的“正当性”将更容易获得系统资源**，而恶意软件将由于其功能的“非法性”而更难获得系统资源。

Doze机制对恶意软件资源占用产生的不利影响极有可能遏制恶意软件在用户机器上的表现，使其达不到预期的不良意图，因而我们推断必将产生多种绕过Doze的手段，下文将为大家揭露近期发现的一种。

<br>

**四、  恶意软件伪装成合法应用绕过Doze限制**

从上文的介绍中我们可以看出，Doze机制极大地限制了白名单外应用对网络，CPU和系统其它资源的占用比例。这意味着对于木马等恶意软件来说，利用设备闲置时段进行私自下载，窃取用户隐私数据等行为以防止用户感知的企图落空。随着使用Android 6.0及更高版本的设备数量不断增加，恶意软件设法绕过Doze势在必行。

**360烽火实验室最新发现一款伪装成Chrome绕过Doze的应用，该恶意软件从图标到名称与正版Chrome完全一致**。如图6，该病毒运行后会隐藏其图标并释放运行子包，通过发送Intent诱使用户将其加入白名单。

[![](https://p0.ssl.qhimg.com/t01b2b000a257286810.png)](https://p0.ssl.qhimg.com/t01b2b000a257286810.png)

图6 恶意软件通过发送Intent诱使用户将其加入白名单

[![](https://p2.ssl.qhimg.com/t01dcfff3f657ae107b.png)](https://p2.ssl.qhimg.com/t01dcfff3f657ae107b.png)

图7 相关利用代码

除使用欺骗手段绕过Doze外，该恶意软件将会在后台私自联网，通过精心构造的手段获取、拼接URL，私自下载其他应用并提示用户安装。此外，该恶意软件注册BroadcastReceiver监听多个事件并进行处理，涵盖短信发送与接收、安装与卸载软件等，对用户数据安全造成危害。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01824792c566cbe275.png)

图8 私自下载其他软件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ee0cc821ac135c57.png)

图9 注册BroadcastReceiver监听多种事件

<br>

**五、 小结**

从Google官方对Android系统的更新上我们可以看出Google对于规范Android生态圈的决心，但正如本报告所揭示的，恶意应用开发者的脚步也从未止歇。因此，我们从开发者与用户的角度提出了一些安全建议与方法，希望能对保护Android用户的安全起到一定作用。

对于开发者，我们建议多参考官方开发者手册，并积极调整自己的应用程序使之符合官方标准，避免对权限和功能的滥用。

对于用户，我们建议尽量养成以下良好习惯：

1.从可信任的平台下载、安装应用程序；

2.谨慎授予应用程序请求的权限；

3.及时执行系统与软件版本更新；

4.养成备份重要信息的习惯；

5.安装安全软件，在疑似遭遇恶意软件侵害时积极反馈；

<br>

**360烽火实验室**

360烽火实验室，**致力于Android病毒分析、移动黑产研究、移动威胁预警以及Android漏洞挖掘等移动安全领域及Android安全生态的深度研究**。作为全球顶级移动安全生态研究实验室，360烽火实验室在全球范围内首发了多篇具备国际影响力的Android木马分析报告和Android木马黑色产业链研究报告。实验室在为360手机卫士、360手机急救箱、360手机助手等提供核心安全数据和顽固木马清除解决方案的同时，也为上百家国内外厂商、应用商店等合作伙伴提供了移动应用安全检测服务，全方位守护移动安全。
