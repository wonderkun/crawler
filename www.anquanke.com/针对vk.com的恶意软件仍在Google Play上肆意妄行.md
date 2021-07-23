> 原文链接: https://www.anquanke.com//post/id/90557 


# 针对vk.com的恶意软件仍在Google Play上肆意妄行


                                阅读量   
                                **66570**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者Roman Unuchek，文章来源：securelist.com
                                <br>原文地址：[https://securelist.com/still-stealing/83343/](https://securelist.com/still-stealing/83343/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/dm/1024_577_/t014534e1741db4a19f.jpg)](https://p3.ssl.qhimg.com/dm/1024_577_/t014534e1741db4a19f.jpg)



## 一、前言

2015年10月，我们发表了一篇[博文](https://securelist.com/stealing-to-the-sound-of-music/72458/)介绍通过Google Play商店传播的一款流行的恶意软件。在接下来的两年中，我们在Google Play上陆续检查到了几款类似的恶意应用，但在2017年10月及11月期间，我们在Google Play上发现了85款新型恶意应用，这些应用可以窃取`VK.com`的凭据信息。卡巴斯基实验室产品将这些应用全部标记为`Trojan-PSW.AndroidOS.MyVk.o`。我们向Google报告了其中72款应用，官方从Google Play商店上删除了这些恶意应用（另外13款应用已经从官方应用商店中移除）。此外，我们也将这些应用及相关技术细节一并报告给了`VK.com`。其中某款应用伪装成一款游戏应用，根据Google Play商店的统计结果，该应用的安装量已超过100万次，如下图所示。

[![](https://p3.ssl.qhimg.com/t01ae0ef8d1eaf0c3b8.png)](https://p3.ssl.qhimg.com/t01ae0ef8d1eaf0c3b8.png)

图1. 伪装成游戏应用的某款**Trojan-PSW.AndroidOS.MyVk.o**恶意应用



## 二、技术细节

这些恶意应用中还包含一些非常流行的应用，根据Google Play的统计结果，其中有7款应用的安装量为10,000-100,000次，9款应用的安装量为1,000-10,000次。剩下的所有应用安装量均小于1,000次。

[![](https://p1.ssl.qhimg.com/t01b0c3080addfc2304.png)](https://p1.ssl.qhimg.com/t01b0c3080addfc2304.png)

图2. Google Play商店中发现的**Trojan-PSW.AndroidOS.MyVk**恶意应用

这些应用中，大部分于2017年10月上传至Google Play，但其中有几款的上传时间为2017年7月，因此这些应用传播的时间跨度已长达3个月。此外，最受欢迎的那款应用最初于2017年3月上传到Google Play商店中，但当时该应用不包含任何恶意代码，只是单纯的游戏应用。网络犯罪分子在2017年10月份将该其更新为恶意应用，他们的等待时间长达7个月，非常有耐心。

这些应用中，表面看上去大部分是为`VK.com`开发的应用，用户可以通过这些应用收听音乐或者查看用户页面访问记录（以随时随地和好友保持联络）。

[![](https://p5.ssl.qhimg.com/t01d0bf6073f0282f29.png)](https://p5.ssl.qhimg.com/t01d0bf6073f0282f29.png)

图3. Google Play商店中发现的**Trojan-PSW.AndroidOS.MyVk.o**恶意应用

当然，这类应用会要求用户登录账户，这也是这些应用看起来并不可疑的原因所在。这些应用中只有一款应用是与VK无关的游戏应用。由于VK在CIS（独联体）国家中非常流行，因此网络犯罪分子会检查设备语言环境，只有发现设备环境匹配特定的几种语言时才会要求用户输入凭据信息，这些语言为：俄语、乌克兰语、哈萨克语、亚美尼亚语、阿塞拜疆语、白俄罗斯语、吉尔吉斯斯坦语、罗马尼亚语、塔吉克语以及乌兹别克语。

[![](https://p3.ssl.qhimg.com/t01cd36c2a9c133f65d.png)](https://p3.ssl.qhimg.com/t01cd36c2a9c133f65d.png)

图4. 木马中检查设备语言的代码片段

犯罪分子通过Google Play来传播恶意软件已超过两年多时间，因此他们必须修改应用代码以绕过官方检测机制。在这些应用中，犯罪分子使用了修改版的VK SDK以及一些“巧妙”的代码来完成这一任务：用户登录的的确是正常页面，但犯罪分子使用了恶意的JS代码从登录页面中窃取凭据信息，并将这些信息传递回应用程序。

[![](https://p0.ssl.qhimg.com/t01e98041af7d47c7a9.png)](https://p0.ssl.qhimg.com/t01e98041af7d47c7a9.png)

图5. 木马执行JS代码以获取VK凭据信息

随后，恶意应用加密这些凭据信息，将其上传至恶意站点。

[![](https://p0.ssl.qhimg.com/t01a01fe298557f6027.png)](https://p0.ssl.qhimg.com/t01a01fe298557f6027.png)

图6. 木马解密恶意URL，加密并上传已窃取的凭据信息

有趣的地方在于，虽然这些恶意应用的功能特点与前面介绍的相符，但其中一些应用稍有不同：这些应用在`OnPageFinished`方法中同样使用了恶意JS代码，这些代码不仅负责提取VK凭据信息，也可以上传这些信息。

[![](https://p2.ssl.qhimg.com/t01c055ba5e15d2e8d9.png)](https://p2.ssl.qhimg.com/t01c055ba5e15d2e8d9.png)

图7. 某个木马执行JS代码以提取并上传VK凭据信息

我们认为网络犯罪分子主要使用窃取的凭据信息来推广`VK.com`中的小组（group）。他们悄悄添加用户到小组中，以推广各种小组，提高这些小组的知名度。我们之所以得出这个结论，原因之一在于被感染的某些用户曾经抱怨过他们的账户被悄悄添加到这些小组中。

另一个原因是，我们在Google Play上找到了其他几款应用，这些应用的发布者与`Trojan-PSW.AndroidOS.MyVk.o`的发布者为同一波人。这些应用伪装成Telegram的非官方客户端（Telegram是一款流行的聊天应用）。卡巴斯基实验室将这些应用全部标记为`not-a-virus:HEUR:RiskTool.AndroidOS.Hcatam.a`。我们向Google报告了这些应用，随后他们从Google Play商店中删除了这些应用。

[![](https://p5.ssl.qhimg.com/t0114e0bb63c661f3d0.png)](https://p5.ssl.qhimg.com/t0114e0bb63c661f3d0.png)

图8. Google Play商店中被**not-a-virus:HEUR:RiskTool.AndroidOS.Hcatam.a**感染的应用

这些应用不单单是伪装成Telegram应用那么简单，实际上这些应用使用了开源的[Telegram SDK](https://github.com/DrKLO/Telegram)来开发，与其他类似应用非常类似，但有一点不同：这些应用会将用户添加到推广的群组（groups）或者聊天频道（chats）中。应用程序会收到服务器返回的群组或聊天频道列表。此外，这些应用可以随时将用户添加到群组中，为了做到这一点，应用窃取了一个GCM令牌，网络犯罪分子可以通过该令牌7×24小时不间断发送控制命令。

关于`extensionsapiversion.space`这个恶意站点，我们还发现了一个有趣的信息。根据KSN的统计结果，在某些情况下，该网站还会使用[http://coinhive.com](http://coinhive.com/)的API来提供加密货币（cryptocurrency）挖矿服务。



## 三、IOC

**C2服务器地址**

```
extensionsapiversion.space
guest-stat.com
```

**应用哈希**

|包名|MD5
|------
|com.parmrp.rump|F5F8DF1F35A942F9092BDE9F277B7120
|com.weeclient.clientold|6B55AF8C4FB6968082CA2C88745043A1
|com.anocat.stelth|C70DCF9F0441E3230F2F338467CD9CB7
|com.xclient.old|6D6B0B97FACAA2E6D4E985FA5E3332A1
|com.junglebeat.musicplayer.offmus|238B6B7069815D0187C7F39E1114C38
|com.yourmusicoff.yourmusickoff|1A623B3784256105333962DDCA50785F
|com.sharp.playerru|1A7B22616C3B8223116B542D5AFD5C05
|com.musicould.close|053E2CF49A5D818663D9010344AA3329
|com.prostie.dvijenija|2B39B22EF2384F0AA529705AF68B1192
|com.appoffline.musicplayer|6974770565C5F0FFDD52FC74F1BCA732
|com.planeplane.paperplane|6CBC63CBE753B2E4CB6B9A8505775389


