> 原文链接: https://www.anquanke.com//post/id/167870 


# 新型 Android 银行木马可绕过 PayPal 双因素认证窃取用户资金


                                阅读量   
                                **200217**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Welivesecurity，文章来源：welivesecurity.com
                                <br>原文地址：[https://www.welivesecurity.com/2018/12/11/android-trojan-steals-money-paypal-accounts-2fa/](https://www.welivesecurity.com/2018/12/11/android-trojan-steals-money-paypal-accounts-2fa/)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p5.ssl.qhimg.com/dm/1024_292_/t0186d1f366388108bf.png)](https://p5.ssl.qhimg.com/dm/1024_292_/t0186d1f366388108bf.png)



## 前言

ESET研究人员发现了一种新的Android木马，它使用了一种新的辅助功能滥用技术，该技术针对的是官方的PayPal应用程序，并且能够绕过PayPal的双因素身份验证。

该恶意软件最早于2018年11月被ESET检测到，它结合了远程控制的银行木马和一种新的滥用Android辅助功能的功能，以官方PayPal应用程序的用户为目标。

截至撰写本文时，恶意软件伪装成电池优化工具，并通过第三方应用商店分发。

[![](https://p3.ssl.qhimg.com/t0137b8dd684055508b.png)](https://p3.ssl.qhimg.com/t0137b8dd684055508b.png)



## 它是如何运作的？

该恶意软件启动后终止且不提供任何功能，并隐藏其图标。从那时起，它的功能可以分为两个主要部分，如下节所述。



## 针对PayPal的恶意辅助功能

恶意软件的第一个功能是从受害者的PayPal账户窃取金钱，需要激活恶意辅助服务功能。如图2所示，该请求是以看似无害的“Enable statistics”服务呈现给用户的。

[![](https://p0.ssl.qhimg.com/t019a73284ecbfeb7ac.png)](https://p0.ssl.qhimg.com/t019a73284ecbfeb7ac.png)

如果官方的PayPal应用安装在受害设备上，恶意软件会显示一个通知窗口，提示用户启动它。一旦用户打开PayPal应用并登录，恶意辅助功能(如果先前由用户启用)就会进入并模拟用户的单击，将钱发送到攻击者的PayPal地址。

在我们的分析中，该恶意软件试图窃取1000欧元，但是使用的货币取决于用户的位置。整个过程大约需要5秒，对于一个毫无戒心的用户来说，没有可行的及时阻止的方法。

由于恶意软件不依赖窃取PayPal登录凭据，而是等待用户自己登录官方PayPal应用，所以它也绕过了PayPal的双因素身份验证(2FA)。启用2FA的用户只需完成一个额外的步骤，作为登录的一部分——就像他们通常会做的那样，但最终会与不使用2FA的用户一样容易受到该木马的攻击。

下面的视频演示了这一过程：

视频地址：[https://youtu.be/yn04eLoivX8](https://youtu.be/yn04eLoivX8)

只有当用户没有足够的PayPal余额并且没有连接到帐户的支付卡时，攻击才会失败。每次PayPal应用程序启动时，恶意辅助功能都会被激活，这意味着攻击可能会多次发生。



## 基于Overlay攻击的银行木马

恶意软件的第二个功能是利用钓鱼界面在目标合法的应用程序上秘密显示。

默认情况下，恶意软件下载5个应用程序(Google Play、WhatsApp、Skype、Viber和Gmail)的基于HTML的覆盖界面，但这个初始列表可以随时动态更新。

五个覆盖界面中有四个显示信用卡详细信息(图3)；以Gmail为目标的界面是在Gmail登录凭据之后(图4)。我们怀疑这与PayPal的目标定位功能有关，因为PayPal为每个已完成的交易发送电子邮件通知。通过访问受害者的Gmail账户，攻击者可以删除这些邮件，从而保持更长时间不引起注意。

[![](https://p5.ssl.qhimg.com/t012df8ce90566510a1.png)](https://p5.ssl.qhimg.com/t012df8ce90566510a1.png)

[![](https://p5.ssl.qhimg.com/t0198ed21cfe5104fc9.png)](https://p5.ssl.qhimg.com/t0198ed21cfe5104fc9.png)

我们还看到了合法银行应用程序的覆盖界面，这些应用程序请求向受害者的网上银行帐户提供登录凭据(图5)。

[![](https://p0.ssl.qhimg.com/t01947521db8d22bc62.png)](https://p0.ssl.qhimg.com/t01947521db8d22bc62.png)

与大多数Android银行木马使用的覆盖不同，它们显示在锁定屏幕上，这一技术也被Android勒索软件所使用。这将防止受害者通过点击“后退”按钮或“主页”按钮来移除覆盖层。通过这个覆盖界面的唯一方法是填写假表单，但幸运的是，即使是随机的、无效的输入也会使这些界面消失。

根据我们的分析，这个木马的作者一直在寻找这种屏幕覆盖机制的进一步用途。恶意软件的代码包含字符串，声称受害者的手机因为儿童色情内容已经被锁定，并且可以通过向指定地址发送电子邮件来解锁。这种说法让人想起早期的移动勒索软件，受害者们害怕自己的设备因为受到警方的制裁而被锁定了。尚不清楚该木马背后的攻击者是否也计划向受害者勒索金钱，或者该功能是否仅用来掩饰后台发生的其他恶意行为。

除了上述两个核心功能之外，根据从C&amp;C服务器接收的命令，恶意软件还可以：
- 拦截和发送SMS消息；删除所有SMS消息；更改默认SMS应用程序(以绕过基于SMS的双因素身份验证)
- 获取联系人列表
- 拨打和转接电话
- 获取已安装的应用程序列表
- 安装应用，运行应用
- 启动socket通信


## Google Play中的辅助功能木马

我们还在Google Play中发现了5个具有类似功能的恶意应用程序，目标是巴西用户。

这些应用程序，其中一些也是由[Dr. Web](https://news.drweb.com/show/?i=12980&amp;lng=en)报道的，现在已经从Google Play中删除了，它们被伪装成跟踪其他Android用户位置的工具。实际上，这些应用程序使用恶意的辅助功能在几家巴西银行的合法应用程序中导航。除此之外，木马还通过在多个应用程序上覆盖钓鱼网站来获取敏感信息。目标应用程序列表请查看在本文的IoC部分。

[![](https://p4.ssl.qhimg.com/t010031355157c51d26.png)](https://p4.ssl.qhimg.com/t010031355157c51d26.png)

有趣的是，这些木马还利用辅助功能阻止卸载尝试，每次启动目标杀毒应用程序或应用程序管理器时，或在前台检测到建议卸载的字符串时，反复单击“返回”按钮。



## 如何防范

那些安装了这些恶意应用程序的用户可能已经成为了他们的受害者。

如果你安装了针对PayPal用户的木马程序，我们建议你检查银行帐户是否存在可疑交易，并考虑更改网上银行密码/PIN代码以及Gmail密码。如果发生未经授权的PayPal交易，可以在PayPal的服务中心报告问题。

对于由于该木马显示的锁定屏幕覆盖而无法使用的设备，我们建议使用Android的安全模式，并继续卸载Settings &gt; (General) &gt; Application manager/Apps名为“Optimization Android”的应用程序。

为了避免Android恶意软件，我们建议：
- 下载应用程序时，请坚持使用官方的Google Play
- 在从Google Play下载应用程序之前，一定要检查下载次数、应用程序评级和评论内容。
- 注意你为安装的应用程序授予的权限。
- 更新Android设备并使用可靠的移动安全解决方案；ESET产品检测这些威胁为Android/Spy.Banker.AJZ和Android/Spy.Banker.AKB


## IoC

针对PayPal用户的Android木马

<th style="text-align: left;">SHA-1</th><th style="text-align: left;">ESET detection name</th>
|------
<td style="text-align: left;">1C555B35914ECE5143960FD8935EA564</td><td style="text-align: left;">Android/Spy.Banker.AJZ</td>

针对巴西用户的Android银行木马

<th style="text-align: left;">Package Name</th><th style="text-align: left;">SHA-1</th><th style="text-align: left;">ESET detection name</th>
|------
<td style="text-align: left;">service.webview.kiszweb</td><td style="text-align: left;">FFACD0A770AA4FAA261C903F3D2993A2</td><td style="text-align: left;">Android/Spy.Banker.AKB</td>
<td style="text-align: left;">service.webview.webkisz</td><td style="text-align: left;">D6EF4E16701B218F54A2A999AF47D1B4</td><td style="text-align: left;">Android/Spy.Banker.AKB</td>
<td style="text-align: left;">com.web.webbrickd</td><td style="text-align: left;">5E278AAC7DAA8C7061EE6A9BCA0518FE</td><td style="text-align: left;">Android/Spy.Banker.AKB</td>
<td style="text-align: left;">com.web.webbrickz</td><td style="text-align: left;">2A07A8B5286C07271F346DC4965EA640</td><td style="text-align: left;">Android/Spy.Banker.AKB</td>
<td style="text-align: left;">service.webview.strongwebview</td><td style="text-align: left;">75F1117CABC55999E783A9FD370302F3</td><td style="text-align: left;">Android/Spy.Banker.AKB</td>

目标应用程序(钓鱼界面)
- com.uber
- com.itaucard
- com.bradesco
- br.com.bb.android
- com.netflix
- gabba.Caixa
- com.itau
- 任何包含“twitter”字符串的应用
目标应用程序(应用程序内导航)
- com.bradesco
- gabba.Caixa
- com.itau
- br.com.bb
- 任何包含“santander”字符串的应用
目标杀毒应用程序和应用程序管理器
- com.vtm.uninstall
- com.ddm.smartappunsintaller
- com.rhythm.hexise.uninst
- com.GoodTools.Uninstalle
- mobi.infolife.uninstaller
- om.utils.uninstalle
- com.jumobile.manager.systemapp
- com.vsrevogroup.revouninstallermobi
- oo.util.uninstall
- om.barto.uninstalle
- om.tohsoft.easyuninstalle
- vast.android.mobile
- om.android.cleane
- om.antiviru
- om.avira.andro
- om.kms.free