> 原文链接: https://www.anquanke.com//post/id/103070 


# 门罗币挖矿的恶意家族HiddenMiner导致手机设备管理器功能故障


                                阅读量   
                                **79951**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者Lorin Wu，文章来源：blog.trendmicro.com
                                <br>原文地址：[https://blog.trendmicro.com/trendlabs-security-intelligence/monero-mining-hiddenminer-android-malware-can-potentially-cause-device-failure/](https://blog.trendmicro.com/trendlabs-security-intelligence/monero-mining-hiddenminer-android-malware-can-potentially-cause-device-failure/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01a319f9b4e07f79e7.jpg)](https://p2.ssl.qhimg.com/t01a319f9b4e07f79e7.jpg)



**针对Monero****挖矿的恶意家族HiddenMiner****能够导致手机设备管理器功能故障**

趋势科技发现了一种新的Android恶意软件，它可以暗中使用受感染设备的计算能力来窃取Monero。趋势科技将其检测为ANDROIDOS_HIDDENMINER。这个Monero挖掘Android应用程序的自我保护和持久性机制包括将自己从不知情的用户身上隐藏起来，并滥用设备管理器功能（通常在SLocker Android勒索软件中看到的技术）。

我们进一步钻研HiddenMiner，发现Monero矿池和钱包与恶意软件连接，并获悉其中一家运营商从其中一家钱包中提取了26 XMR（或截至2018年3月26日的5,360美元）。这表明利用受感染设备来挖掘加密货币的活动非常活跃。

HiddenMiner使用该设备的CPU功率来挖掘Monero。HiddenMiner的代码中没有开关，控制器或优化器，这意味着它将持续挖掘Monero，直到设备资源耗尽。鉴于HiddenMiner的本质，它可能会导致受影响的设备过热并可能失败。

这与其他安全研究人员观察到的导致设备电池膨胀的Loapi Monero挖掘Android恶意软件类似。事实上，取消激活设备管理权限后Loapi锁定屏幕的技术与HiddenMiner类似。

HiddenMiner位于第三方应用程序市场。到目前为止，它影响着印度和中国的用户，但如果它扩展到两国之外，这并不意外。

[![](https://p2.ssl.qhimg.com/t0159f291ef242faf8e.png)](https://p2.ssl.qhimg.com/t0159f291ef242faf8e.png)

图1.一个Monero钱包地址状态的屏幕截图



## 感染链

HiddenMiner伪装成合法的Google Play更新应用程序，随着 com.google.android.provider弹出，并附带Google Play图标。它要求用户以设备管理员身份激活它。它会持续弹出，直到受害者点击激活按钮。一旦获得许可，HiddenMiner将在后台开始挖掘Monero。

[![](https://p1.ssl.qhimg.com/t010b386d7e2fd773ab.png)](https://p1.ssl.qhimg.com/t010b386d7e2fd773ab.png)

图2.恶意应用程序的屏幕要求用户以设备管理员身份激活它



## 技术分析

HiddenMiner使用多种技术将自己隐藏在设备中，例如清空应用程序名称标签并在安装后使用透明图标。一旦作为设备管理员激活，它将通过调用**setComponentEnableSetting****（）**从应用程序启动器隐藏应用程序。请注意，恶意软件会自行隐藏并自动以设备管理员权限运行，直到下一次设备引导。[DoubleHidden](https://www.symantec.com/blogs/threat-intelligence/doublehidden-android-malware-google-play) 恶意家族采用了类似的技术。

[![](https://p1.ssl.qhimg.com/t0138340543d77adf93.png)](https://p1.ssl.qhimg.com/t0138340543d77adf93.png)

图3. HiddenMiner如何隐藏自身的图例：安装后的空应用程序名称标签和透明图标（左），然后一旦授予设备管理权限就会消失（右图）

HiddenMiner还具有反模拟器功能，可绕过检测和自动分析。它会通过滥用Github上的Android模拟器检测器来检查它是否在模拟器上运行。

[![](https://p1.ssl.qhimg.com/t013f879d0e6570f33c.png)](https://p1.ssl.qhimg.com/t013f879d0e6570f33c.png)

图4.代码片段显示了HiddenMiner如何绕过基于我们的沙箱检测和分析的Android模拟器

[![](https://p3.ssl.qhimg.com/t016dd674e528ce8737.png)](https://p3.ssl.qhimg.com/t016dd674e528ce8737.png)

图5.代码片段显示了HiddenMiner如何挖掘Monero



## 滥用设备管理权限

用户无法卸载激活设备管理器的软件包，除非首先删除设备管理员权限。在HiddenMiner的案例中，受害者无法将其从设备管理器中删除，因为当用户想要禁用其设备管理员权限时，恶意软件会利用Nougat（Android 7.0）和更高版本之外的Android操作系统中发现的缺陷来锁定设备的屏幕。

[![](https://p0.ssl.qhimg.com/t01dad4e29596208cbd.png)](https://p0.ssl.qhimg.com/t01dad4e29596208cbd.png)

图6.显示HiddenMiner如何防止移除设备管理员权限的代码片段

Google通过减少设备管理员应用程序的权限，解决了Nougat及其后的Android操作系统中的安全问题，使他们无法再锁定屏幕（如果它是应用程序功能的一部分）。设备管理器将不再通过onDisableRequested()通知设备管理应用。这些策略并不罕见：某些Android勒索软件和信息窃取器（即Fobus）利用这些技术在设备中立足。
