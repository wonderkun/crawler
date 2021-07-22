> 原文链接: https://www.anquanke.com//post/id/85425 


# 【技术分享】使用AT调制解调器命令解锁LG Android屏幕


                                阅读量   
                                **112062**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：articles.forensicfocus.com
                                <br>原文地址：[https://articles.forensicfocus.com/2017/02/03/unlocking-the-screen-of-an-lg-android-smartphone-with-at-modem-commands/](https://articles.forensicfocus.com/2017/02/03/unlocking-the-screen-of-an-lg-android-smartphone-with-at-modem-commands/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0137ee2f51a6aa9aa0.jpg)](https://p5.ssl.qhimg.com/t0137ee2f51a6aa9aa0.jpg)



翻译：[胖胖秦](http://bobao.360.cn/member/contribute?uid=353915284)

预估稿费：100RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



现代智能手机不仅仅是用于语音呼叫的设备。现在，他们包含了大量的个人数据 – 联系人列表，通信历史，照片，视频，地理坐标等。大多数智能手机也可以作为一个调制解调器。

几乎每个调制解调器都是Hayes兼容的，这意味着它支持Hayes在1977年开发的AT语言的命令。每个型号都支持一些由制造商定义的基本命令集。有时这个命令集可以扩展,并可以包含非常有趣的命令。

让我们研究LG智能手机的行为。当您通过USB将其连接到计算机时，您可以自动访问调制解调器（图1）。LG特有的是，即使手机的屏幕被锁定，调制解调器也可用。

[![](https://p1.ssl.qhimg.com/t012da6c826812a29ad.png)](https://p1.ssl.qhimg.com/t012da6c826812a29ad.png)

图片1

因此，即使手机受密码保护，我们也可以使用AT命令了解有关手机的一些有用信息。（图2）。

[![](https://p5.ssl.qhimg.com/t01c4e98e5c02b40b6a.png)](https://p5.ssl.qhimg.com/t01c4e98e5c02b40b6a.png)

图片2

要了解这个模式支持什么命令，我们必须检查其固件。例如，对于Android智能手机，我们只需要研究文件/ system / bin / atd。图片3-5演示了在LG G3 D855手机上找到的一些AT命令。

[![](https://p2.ssl.qhimg.com/t018df08b3f9f0e42ab.png)](https://p2.ssl.qhimg.com/t018df08b3f9f0e42ab.png)

图片3

[![](https://p0.ssl.qhimg.com/t01ea3e306e873a11c6.png)](https://p0.ssl.qhimg.com/t01ea3e306e873a11c6.png)

图片4

[![](https://p5.ssl.qhimg.com/t01dc59ab8da2daf7c7.png)](https://p5.ssl.qhimg.com/t01dc59ab8da2daf7c7.png)

图片5

很明显，手机支持大多数基本的AT +命令集，可以用于提取关于它的公共信息（图5）。但最感兴趣的是LG专有命令（AT％类型的命令）。这些命令（如AT％IMEIx，AT％SIMID，AT％SIMIMSI，AT％MEID，AT％HWVER，AT％OSCER，AT％GWLANSSID）返回有关手机的基本信息。其中包括一个命令AT％KEYLOCK（图4）。你可能猜到这个命令允许你管理屏幕锁定状态。为了研究这个命令行为，我们可以运行一个调试器并使用交叉引用来找到它的处理函数代码。如图6所示。

[![](https://p2.ssl.qhimg.com/t01a3f6179ee1598e5b.png)](https://p2.ssl.qhimg.com/t01a3f6179ee1598e5b.png)

图片6

当调用命令AT％KEYLOCK时，根据参数数量，会从/system/lib/libatd_common.so库中调用lge_set_keylock（）或lge_get_keylock（）函数。图7显示出了函数lge_set_keylock（）的代码。

[![](https://p0.ssl.qhimg.com/t013aca965770dbf0e1.png)](https://p0.ssl.qhimg.com/t013aca965770dbf0e1.png)

图片7

正如你从图片8中看到的，如果你传递给函数lge_set_keylock（）的值为“0”= 0x30，它将最终调用该函数，这将移除屏幕锁,无论你是用什么方法来锁定它（你可以使用PIN，密码，模式或指纹来锁定屏幕）。然后它将返回字符串“[0] KEYLOCK OFF”（图8）。

[![](https://p0.ssl.qhimg.com/t01bf96eeb8068a0f77.png)](https://p0.ssl.qhimg.com/t01bf96eeb8068a0f77.png)[![](https://p1.ssl.qhimg.com/t01f176c856e4c4d458.png)](https://p1.ssl.qhimg.com/t01f176c856e4c4d458.png)

图片8

很明显，命令AT％KEYLOCK = 0允许您删除屏幕锁定，而无需任何额外的操作。

值得一提的是，此命令只会删除屏幕锁定，而不会影响用户设置。该命令的工作原理如下：它将零值（意味着解锁）写入特殊RAM区域，该区域存储着负责屏幕锁定的值。这意味着该命令不以任何方式修改ROM。此行为是可以用来取证的，因为不访问任何用户数据，并且重新启动智能手机后将返回锁定状态。该命令不允许调查员找到屏幕锁定PIN /模式/密码; 它只是删除它一段时间。

为了进行此分析，我们使用了LG G3 D855型号（带有V20g-SEA-XX固件）。然而，上述AT命令已经被证明在其他LG智能手机（LG G4 H812，LG G5 H860，LG V10 H960等）上也可以正常工作。所有这些模型支持这种方法。

因此，它是很容易解锁手机的。所有你需要只是拥有一个LG Android智能手机，然后通过USB连接到一台电脑。这个后门显然是LG的服务软件，但也可以用于取证目的。但要记住，罪犯也可以使用这种方法。

<br style="text-align: left">
