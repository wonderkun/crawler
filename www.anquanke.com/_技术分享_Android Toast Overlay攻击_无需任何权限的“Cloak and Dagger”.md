> 原文链接: https://www.anquanke.com//post/id/86880 


# 【技术分享】Android Toast Overlay攻击：无需任何权限的“Cloak and Dagger”


                                阅读量   
                                **89664**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01a1cd348dd0ab70d1.png)](https://p0.ssl.qhimg.com/t01a1cd348dd0ab70d1.png)

**简介**

****

Palo Alto Networks公司Unit 42实验室研究人员在Android overlay系统中发现一个高危漏洞，它允许使用"Toast类型"叠加层，可以发起新型的Android overlay攻击。所有OS版本&lt;8.0的Android设备都受到这个漏洞的影响，在[2017年9月份Android安全公告](https://source.android.com/security/bulletin/2017-09-01)中发布了该漏洞的补丁。Android 8.0版本刚刚发布，不受此漏洞的影响。正因为Android 8.0刚刚发布，所以这个漏洞几乎影响到目前市面上所有的Android设备(见表1)，用户应尽快更新补丁。

Overlay攻击允许攻击者在受影响的设备上运行其他窗口和应用程序。要发起这样的攻击，恶意软件通常需要请求“draw on top”权限。然而，这个新发现的overlay攻击不需要任何特定的权限或条件才有效。发起此攻击的恶意软件不需要拥有overlay权限,或者从谷歌市场下载安装。利用这种新的overlay攻击方式，恶意软件可以诱使用户启用Android可访问性服务，并授予设备管理员权限或执行其他危险的操作。如果这些权限被授予，那么就可以在设备上发起一系列强大的攻击，包括窃取证书、静默安装应用程序，以及为了勒索赎金将设备锁定。

 这项研究的灵感来自于“[Cloak and Dagger: From Two Permissions to Complete Control of the UI Feedback Loop](http://iisp.gatech.edu/sites/default/files/documents/ieee_sp17_cloak_and_dagger_final.pdf)”。这篇论文于2017年5月在IEEE Security &amp; Privacy 2017年会议上发表。论文中提出了几种创新的可访问性攻击方法，但前提是恶意应用程序必须显式请求两个特殊权限，并从谷歌商店中下载安装。我们的新研究表明，即使应用程序不是来自谷歌商店，而且只声明了一个权限“**BIND_ACCESSIBILITY_SERVICE**”，也可以成功地启动本文中提到的可访问性攻击。

与“Cloak and Dagger”一样，这种overlay攻击通过修改屏幕的区域来改变用户看到的内容，诱使用户授予额外的权限或识别输入内容。

这种攻击的演示视频地址：



该漏洞被收录为CVE-2017-0752，并在今年9月份的Android安全公告中披露。



**一、无条件Overlay攻击**

****

**利用Toast进行新型overlay攻击**

“Toast”窗口(**TYPE_TOAST**)是Android上支持的overlay类型之一。Toast overlay通常用来在所有其他应用程序上显示一个快讯。例如，当用户未发送邮件，邮件自动保存为草稿时会有一个消息提示。它继承了其他windows类型的所有配置选项。然而，我们的研究发现，使用Toast窗口作为一个覆盖窗口，允许应用程序在另一个应用程序的界面上写入，而不需要特殊请求SYSTEM_ALERT_WINDOW权限。

这个发现允许一个安装的应用程序在屏幕上用一个Toast窗口制作一个覆盖层。通过这种方式，应用程序可以在没有任何特殊权限的情况下启动overlay攻击。精心制作的overlay包括两种类型的视图(图1)，它们都被嵌入在Toast窗口中。在下面的示例中，view1覆盖了底部的GUI，并监视用户单击行为以推断攻击的进展，而view2是一个可点击的视图，攻击者试图引诱受害者点击。

[![](https://p2.ssl.qhimg.com/t0178e302768f8057f4.png)](https://p2.ssl.qhimg.com/t0178e302768f8057f4.png)

图1  使用Toast窗口制作一个overlay

**Android OS &lt;= 7.0**

此漏洞是由于缺少权限检查造成的。在Android的AOSP相关代码段（版本&lt;= 7）中可以看到，是如图2所示。通常，将窗口覆盖在其他应用程序的顶部需要进行权限检查和操作检查。然而，在TYPE_TOAST案例中，那些检查并不到位。请求将自动被授予。根据图2中的注释，该应用程序将被授予对TYPE_TOAST窗口的完全控制权。

[![](https://p5.ssl.qhimg.com/t01071d91e8e975dd06.png)](https://p5.ssl.qhimg.com/t01071d91e8e975dd06.png)

图2  TYPE_TOAST未进行权限检查

**Android OS 7.1**

Android 7.1引入了两层缓解措施：一次超时和每个UID的单个toast窗口（见表1）。 第一个缓解强制为每个Toast窗口分配最大超时（3.5秒）（图3）。 超时后，Toast窗口将消失，以模拟Android上的正常Toast行为。 z毫无意外，这可以被故意设计的重复弹出的Toast窗口击破。对于第二次缓解，Android 7.1只允许每个应用程序一次显示一个Toast窗口（图4）。 这两种防御机制对使用Toast窗口发动overlay攻击欺骗受害者构成了挑战。 但是，它并没有解决基本原因：应用程序不需要任何权限在任何其他应用程序之上显示Toast窗口。

[![](https://p1.ssl.qhimg.com/t01856f6686efed96dc.png)](https://p1.ssl.qhimg.com/t01856f6686efed96dc.png)

图3 Toast窗口超时缓解措施（缓解措施1）

[![](https://p1.ssl.qhimg.com/t0131665c97ccf0b36f.png)](https://p1.ssl.qhimg.com/t0131665c97ccf0b36f.png)

图4 每个UID允许一个Toast窗口（缓解措施2）

对于Android 7.1版本，想要达到同样的overlay攻击，恶意软件需要利用LooperThread去不停地展示Toast窗口（图5）。但是在同一时间，只有一个overlay可以使用，所以，恶意程序无法监控用户是否淡季了覆盖区域中的预期区域。另一种方法是展示一个overlay，诱导用户去单击它，休眠几秒钟，然后切换到另外的一个overlay进行其他的步骤。显然，通过这种缓解措施，overlay攻击的成功几率微乎甚微。这种方法同样适用于Android2.3.7~4.3。因为在上述版本中，Toast窗口中移除了FLAG“FLAG_WATCH_OUTSIDE_TOUCH”（图6）。

[![](https://p5.ssl.qhimg.com/t01f8b8cf8d76944424.png)](https://p5.ssl.qhimg.com/t01f8b8cf8d76944424.png)

图5 利用循环绕过超时缓解

[![](https://p4.ssl.qhimg.com/t014d3ce8ffbd76eb72.png)](https://p4.ssl.qhimg.com/t014d3ce8ffbd76eb72.png)

图6  版本2.3.7~4.3中移除了FLAG_WATCH_OUTSIDE_TOUCH

[![](https://p3.ssl.qhimg.com/t01cfa61c1b2137ca0f.png)](https://p3.ssl.qhimg.com/t01cfa61c1b2137ca0f.png)

表1 各个Android版本中的overlay攻击缓解措施



**二、可能的后续overlay攻击**

通过上面描述的漏洞，“Cloak and Dagger”中涉及的所有可访问性攻击都可以成功执行。此外，我们还演示了一些实际使用TYPE_TOAST浮动窗口的攻击。

**通过设备管理员进行攻击**

通过overlay攻击，一个已安装的恶意应用程序可以欺骗用户授权app设备管理员权限。有了这个，它就有能力发动破坏性的攻击，包括:

**锁定设备的屏幕**

**重置设备PIN**

**清除设备的数据**

**阻止用户卸载App**

恶意软件变体已经发动了这种攻击。如图7所示，该恶意软件呈现“安装完成”对话框，并带有“Continue”按钮。然而，这个对话框实际上是一个TYPE_SYTEM_OVERLAY窗口，其中有设备管理员激活对话框。Android API文档中描述，TYPE_SYSTEM_OVERLAY的描述是“系统覆盖窗口，显示在其他所有东西之上”和“这些窗口不能接收输入焦点”。因此，一旦用户单击“Continue”按钮，单击事件实际上被发送到真实设备管理员激活窗口的“激活”按钮。

使用TYPE_TOAST窗口的攻击也实现了这一点，将视图flag设置为FLAG_NOT_FOCUSABLE和FLAG_NOT_TOUCHABLE，我们可以在没有任何特殊权限的情况下发起类似的攻击。

[![](https://p1.ssl.qhimg.com/t01583079c5d7b0036e.png)](https://p1.ssl.qhimg.com/t01583079c5d7b0036e.png)

图7 Android恶意软件使用点击劫持overlay来激活设备管理员



**三、恶意锁屏和勒索软件攻击**

Android恶意锁屏和勒索软件已经在黑市流行很多年了。大多数Android 勒索软件通过以下方法实现屏幕锁定：

**SYSTEM_ALERT_WINDOW**：一个带有这个权限的Android应用程序可以在任何其他应用程序的顶部显示一个浮动窗口。通过设置适当的窗口类型和视图标志，例如，TYPE_SYSTEM_ERROR、TYPE_SYSTEM_OVERLAY和FLAG_FULLSCREEN，这种浮动窗口将无法被用户移动。这种技术可以阻止用户访问他们的设备。

**设备管理员**：使用此特权的Android应用程序可以重置屏幕密码，然后锁定设备屏幕。如果屏幕被锁定，PIN被重置，受害者的设备就和板砖一样了。

我们不需要任何额外的权限，使用TYPE_TOAST类型窗口和默认的视图标志，通过显示全屏的浮动窗口就实现屏幕锁定的效果，而这种窗口无法被用户移动。虽然在Android 7.1上有一个时间限制来显示TYPE_TOAST窗口，但是我们可以像前面介绍的那样，可以在一个循环中不断弹出Toast窗口进行绕过。因此，我们可以绕过Android 7.1的限制。
