
# 【木马分析】Ewind：披着合法应用外衣的广告软件


                                阅读量   
                                **86118**
                            
                        |
                        
                                                                                                                                    ![](./img/85915/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：paloaltonetworks.com
                                <br>原文地址：[http://researchcenter.paloaltonetworks.com/2017/04/unit42-ewind-adware-applications-clothing/](http://researchcenter.paloaltonetworks.com/2017/04/unit42-ewind-adware-applications-clothing/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85915/t010c5cd0d34119df9a.jpg)](./img/85915/t010c5cd0d34119df9a.jpg)**

****

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

自2016年年中以来，我们捕获到了Andorid广告软件“Ewind”的多个全新变种。隐藏在广告软件背后的攻击者使用了一种简单但行之有效的方法，他们下载流行的、合法的Android应用，对其反编译，添加恶意代码，然后重新封装为APK包。攻击者通过俄语Android应用网站分发这些木马应用。

Ewind的目标应用包括一些广受欢迎的Android应用，比如侠盗猎车-罪恶都市（GTA Vice City）、AVG Cleaner、Minecraft口袋版、Avast!勒索软件专杀工具、VKontakte以及Opera移动版。

虽然Ewind本质上是个广告软件，可以通过受害者设备向用户显示广告来谋取利益，但它也包括其他功能，比如收集设备数据、向攻击者转发用户短信。该广告软件实际上可以允许攻击者通过远程方式完全控制已感染的设备。

我们认为Ewind所涉及的应用软件、插入的广告以及托管网站背后的攻击者是俄罗斯人。

<br>

**二、初步分析**

我们通过[**AutoFocus**](https://www.paloaltonetworks.com/products/secure-the-network/subscriptions/autofocus)观察到大量重新封装的APK，使用了相同的可疑证书进行签名。通过“keytool”工具，我们识别出一些不同的签名证书元素，所有样本中的证书存放位置一致，位于“META-INF/APP.RSA”处，证书信息如下所示：



```
owner=CN=app
issuer=CN=app
md5=962C0C32705B3623CBC4574E15649948
sha1=405E03DF2194D1BC0DDBFF8057F634B5C40CC2BD
sha256=F9B5169DEB4EAB19E5D50EAEAB664E3BCC598F201F87F3ED33DF9D4095BAE008
```

这些重新封装的APK包括反病毒应用以及其他著名的应用，这也进一步引起我们的警觉。

<br>

**三、技术分析**

Ewind存在多个变种，我们对其中一个“AVG Cleaner”样本进行分析，样本哈希值如下：

```
9c61616a66918820c936297d930f22df5832063d6e5fc2bea7576f873e7a5cf3
```

该样本下载自“88.99.112[.]169”，这个地址也承载了多个Android应用商店网站。

我们可以在AndroidManifest.xml中快速识别出已添加的木马组件，因为这些组件的前缀都是“b93478b8cdba429894e2a63b70766f91”，如下所示：



```
b93478b8cdba429894e2a63b70766f91.ads.Receiver
b93478b8cdba429894e2a63b70766f91.ads.admin.AdminReceiver
b93478b8cdba429894e2a63b70766f91.ads.AdDialogActivity
b93478b8cdba429894e2a63b70766f91.ads.AdActivity
b93478b8cdba429894e2a63b70766f91.ads.admin.AdminActivity
b93478b8cdba429894e2a63b70766f91.ads.services.MonitorService
b93478b8cdba429894e2a63b70766f91.ads.services.SystemService
```

Ewind通过注册ads.Receiver广播接收器来接收以下事件：

1、启动完成事件（“android.intent.action.BOOT_COMPLETED”）。

2、屏幕关闭事件（“android.intent.action.SCREEN_OFF”）。

3、用户活动事件（“android.intent.action.USER_PRESENT”）。

ads.Receiver首次被调用时，它会收集设备环境信息，并将收集结果发往C2服务器。所收集的信息如图1所示。Ewind为每个安装实例生成一个唯一的ID，并将其作为URL参数进行传输。URL中如果包含“type=init”参数则表示Ewind首次运行。

[![](./img/85915/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0185dcf26b9c30c23d.png)

图1. Ewind将受害者信息发往C2服务器

C2服务器按下述命令语法返回纯文本的HTTP响应报文：



```
[{"id":"0","command":"OK"},
{"id":15826273,"command":"changeMonitoringApps","params":{"apps":["com.android.chrome","com.yandex.browser","com.UCMobile.intl","org.mozilla.firefox","com.opera.mini.native","com.opera.browser","com.opera.mini.native.beta","com.uc.browser.en","com.ksmobile.cb","com.speedupbrowser4g5g","com.gl9.cloudBrowser","appweb.cloud.star"]}},
{"id":15826274,"command":"wifiToMobile","params":{"enable":true}},
{"id":15826275,"command":"sleep","params":{"time":720}},
{"id":15826276,"command":"adminActivate","params":{"tryCount":3}}]
```

Ewind将收到的每个信息存储在本地一个名为“main”的SQLite数据库中，然后依次处理每条命令。命令逐一执行完毕后，Ewind将执行结果送回C2服务器。执行结果的URL中包含“type=response”参数，如图2所示。

[![](./img/85915/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ae5df39aece59ac1.png)

图2. C2服务器命令的执行结果报文

我们观察到受害者设备只有在初始化阶段才会收到“adminActivate”命令，该命令指示Ewind打开“AdminActivity”界面，试图诱骗受害者允许Ewind获得设备的管理员权限。该界面中的俄文信息翻译过来就是“点击‘Active’按钮以正确安装应用”，如图3所示。

[![](./img/85915/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01aa4490c0058794b7.png)

图3. Ewind试图欺骗受害者以获取管理员权限

我们不清楚为何Ewind试图获取设备的管理员权限。这样做的一个好处就是让非专业用户难以卸载这个木马应用。Ewind使用的另一种技术是，当用户点击设备管理界面的“deactive”按钮时，Ewind会将屏幕锁定5秒，在用户解锁时将屏幕切换回正常的设置界面。

这样做的确会让用户难以卸载Ewind，然而本文分析的样本在调用“lockscreen”函数时犯了个错误。为了锁定屏幕，Ewind创建了一个AsyncTask任务，该任务始终处于死循环状态。Ewind无法再次执行这个AsyncTask任务，直到前一个任务执行完毕（这是Android平台的限制策略）。

虽然Ewind会检查设备是否处于越狱状态，但我们并没有观察到任何利用越狱功能的代码片段。

Ewind的目的不仅仅是展示广告。Ewind使用了一个名为“ads.Monitor”的服务，该服务可以监控前台应用（此功能仅适用于Android 4.4及更低版本，因为后续版本限制了“getRunningTasks” API的使用）。如果某个应用的包名与Ewind的目标应用包名相匹配（可以参考这里的[**详细列表**](https://github.com/pan-unit42/iocs/blob/master/ewind/apps.csv)），那么Ewind会向C2服务器发送一个带有“type=event”参数的报文（如图4所示）。应用不再处于前台状态时，Ewind也会向C2服务器发送一个“stopApp”事件。其他的事件包括“userPresent”、“screenOff”、“install”（应用包已存在）、“uninstall”、“adminActivated”、“adminDisabled”、“click”（用户点击广告）、“receive.sms”以及“sms.filter”。

[![](./img/85915/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0182f38e71a0fd73dd.png)

图4. Ewind向C2服务器报告应用活动情况

C2服务器可以通过响应报文（如图5所示），指导Ewind进行后续操作，通常是展示广告。C2服务器同时提供了待展示广告的URL地址，广告通过简单的webview组件进行展示。

[![](./img/85915/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0144898ce788dc2587.png)

图5. 展示广告的C2命令

在我们的测试过程中，只有当财务类应用处于前台时，受害者才会收到一个显示广告的命令（目标浏览器处于前台时并不会收到控制命令）。此外，不论应用是启动还是停止，总会触发“showFullScreen”命令。这条命令涉及到的参数是“URL”（代表广告的地址）以及“delay”（代表Ewind在显示广告前需要等待多少秒）。

我们的测试设备收到的唯一一条广告来自于“mobincome[.]org/banners/banner-720×1184-24.html”这个URL，如图6所示。当用户点击该广告后，Ewind试图从“androidsky[.]ru”这个应用商店下载一个“mobCoin”应用。在我们对样本进行分析时，此下载链接已经失效。我们同时也发现了一个经过Ewind定制的MobCoin应用（哈希值为393ffeceae27421500c54e1cf29658869699095e5bca7b39100bf5f5ca90856b），该应用具备木马功能，但我们不清楚这个文件是否就是“androidsky[.]ru”提供的那个文件。

[![](./img/85915/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016320b3fbc0a2848a.png)

图6. Ewind展示的广告

Ewind的最后一类通信是“type=timer”，用于保活功能。Ewind以预定义的间隔（通常为180秒再加上或减去一个随机秒数）发送该报文，如图7所示。通常这个报文除了保活之外没有其他功能，但我们观察到服务器某一天响应了这个请求，响应报文包括目标应用程序的最新列表。

[![](./img/85915/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010297ca36548976dd.png)

图7. Ewind发送的保活请求

<br>

**四、窃取短信**

Ewind收到“smsFilters”命令后，可以将符合某些过滤条件的短信发往C2服务器。过滤条件包括电话号码匹配或消息文本匹配。如果设备收到符合号码或文本匹配条件的短信，Ewind会通过“receive.sms”事件，将整个短信文本和短信发送者信息发给C2服务器。如果电话号码和消息文本同时匹配成功，那么Ewind会使用“sms.filter”事件通知C2服务器。

这个功能的目的可能是想破解基于短信的双因素身份认证。我们没有捕捉到攻击者使用这个命令，但当我们手动将过滤条件插入受害者设备的Ewind数据库中时，我们就可以观察到这种攻击行为。

[![](./img/85915/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0109145a62a0a8a1dc.png)

<br>

**五、目标应用**

如果应用的包名匹配Ewind的目标应用列表，那么每当应用被切换到前台或后台时，Ewind就会通知C2服务器。C2服务器可以通知Ewind执行命令，通常用来展示一则广告。Ewind首次在受害者设备执行时会收到服务器返回的目标应用列表，该列表每天都会更新。列表的存放地址为“{data_dir_of_the_app}/shared_prefs/a5ca9525-c9ff-4a1d-bb42-87fed1ea0117.xml”。

就我们目前所看到情况，目标应用列表包含主流浏览器以及财务类应用。我们还注意到C2服务器在浏览器启动时并不会发送控制命令（至少目前依然如此），只有财务类应用才会触发控制命令。

<br>

**六、字符串混淆**

Ewind使用简单的异或算法，对某些字符串与Ewind的共享首选项（即“a5ca9525-c9ff-4a1d-bb42-87fed1ea0117”）进行处理，完成字符串混淆过程。经过去混淆处理后，我们获得了一个json数据，转化为字符串数组后如下所示：



```
["internal: close","internal: too many redirects","click: ","send: ","http",
"Referer","javascript:","internal: timeout","null","internal: timeoutconnect",
"receive.sms","web.click.end","sms.filter","js.data","phone","text","phoneExp",
"textExp","loadProgress","errorUrl","errorDescription","id","timeout","data","filters"
,"[%d].","invalid, null or empty","invalid regular expression","invalid, null",
"test","enable","already enabled","already disabled","end","[%d]",
"actions","urlExp","js","start","turnOffWifi","userAgent"]
```



**七、控制命令**

Ewind的控制命令包含我们前面提到过的一些功能，也包含我们尚未观察到的一些功能，如下所示：

showFullscreen – 展示广告

showDialog – 弹出一个对话框，点击后会展示广告

showNotification – 在通知栏展示一个通知

createShortcut – 下载一个APK并创建快捷方式

openUrl – 使用webview打开URL

changeTimerInterval – 修改保活间隔

sleep – sleep一段时间

getInstalledApps – 获取已安装应用列表

changeMonitoringApps – 定义目标应用程序

wifiToMobile – 启用或断开连接，虽然看起来啥事都没干

openUrlInBackground – 后台打开一个URL

webClick – 在某个web页面的webview中执行指定的javascript脚本

receiveSms – 启用或禁用短信监控功能

smsFilters – 定义电话号码和短信文本的匹配规则

adminActivate – 显示激活设备管理器的界面

adminDeactivate – 停用设备管理器

<br>

**八、其他样本**

我们经过进一步研究，发现其他一千多个Ewind样本同样与相同的C2服务器“mobincome[.]org”进行通信，但所使用的APK服务名为“com.maxapp”。其他使用“com.maxapp”服务的样本所用的C2服务器有所不同，但这些样本应该都属于相同作者开发的不同恶意软件族群。

<br>

**九、基础设施及追踪溯源**

最开始我们认为木马作者以及承载木马应用的Android应用网站之间没有任何联系，因为攻击者通常会将木马应用上传到分享破解应用的网站上，然而对于本文分析的样本而言，这两者看上去有比较紧密的联系。

我们分析的样本下载自“88.99.112[.]169”，该样本与C2服务器“mobincome[.]org”通信。我们注意到该服务器的地址为“88.99.71[.]89”，属于同一个B类网。一个B类网范围相当大，因此这种联系相对较弱，但还是引起了我们的注意。

我们随后注意到“mobincome[.]org”的WHOIS记录目前处于隐私保护状态，然而该域名历史上曾被伏尔加格勒的“Maksim Mikhailovskii”所拥有，我们发现攻击者在某些APK样本的服务名使用过“Max”字符串。

“Mobincome[.]org”网页中的某个资源链接（img src）指向了“apkis[.]net”域名。“Apkis[.]net”域名的所有者同样为“Maksim Mikhailovskii”。“Apkis[.]net”地址为“88.99.112[.]168”，这与样本的下载地址相邻。我们还在“88.99.112[.]168”上找到了Ewind样本的下载链接。这表明C2服务器“mobincome[.]org”、下载地址“88.99.112[.]169”以及攻击者三者之间存在紧密的联系。

“88.99.112[.]169”地址托管了几个网站，全部都是Android应用商店网站：



```
mob-corp[.]com
appdecor[.]org
playlook[.]ru
android-corp[.]ru
androiddecor[.]ru
```

这些域名的WHOIS记录都已经被隐去，但基于上述联系以及后续的基础设施分析工作（如图8所示），我们确定该木马应用背后的攻击者控制了这些应用商店。另一个应用商店“apptoup[.]com”与“88.99.99[.]25”属于同一个B类网，之前的WHOIS记录显示其持有者也为“Maksim Mikhailovskii”，但该域名最近也更换为匿名的WHOIS记录。

[![](./img/85915/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0102dd81ca9425519e.png)

图8. 基础设施分析

我们对图8中的下载地址和C2服务器做了高亮处理，同时也重点标出了域名持有者“Maksim”与其他Android应用商店域名之间的联系。

攻击者目前主要使用的C2服务器地址是“mobincome[.]org”，我们还观察到少数样本使用“androwr[.]ru”作为C2服务器（地址为88.99.99[.]25，与“apptoup[.]com”地址相同）。在[**AutoFocus**](https://www.paloaltonetworks.com/products/secure-the-network/subscriptions/autofocus)中搜索后，我们发现上千个Android恶意软件和木马连接到这些域名。

通过基础设施、APK签名密钥哈希值以及APK服务名分析，我们可以将几年前的非Ewind样本与该攻击者关联起来。这些样本都是通过广告谋利的Android应用。

WHOIS电子邮箱地址指向了其他几个域名，如下所示：



```
Appwarm[.]com
mobcoin[.]org
android-corp[.]su
z-android[.]com
apkis[.]net
```

对这些域名的IP进行调查后，我们找到了更多域名使用相同的基础设施，如下所示：



```
appdisk[.]ru
vipsmart[.]org
vipandroid[.]ru
vipandroid[.]org
1lom[.]com
mobcompany[.]com
greenrobot-apps[.]net
9apps.ru[.]com
ontabs[.]com
ontabfile[.]com
andromobi[.]ru
bammob[.]com
apkforward[.]ru
mobrudiment[.]ru
mob0esd[.]ru
mob1leprof[.]ru
mob4ad[.]ru
mob2ads[.]ru
mob1lihelp[.]ru
mob1help[.]ru
```

这些域名并没有广泛共享IP地址，这表明控制这些域名的某个攻击者会根据特定用途使用某些域名，而不是单纯将这些域名指向相同IP。

<br>

**十、总结**

Ewind不仅仅是一个简单的广告软件，它至少是一个真正的木马，可以篡改合法的Android应用。Ewind可以将短信内容转发给C2服务器，表明它的目的不仅仅是展示广告。真正值得注意的是，尽管我们现在观察到这些木马仅仅用来向被害者推送广告，但就如我们文章中所分析的，Ewind背后的攻击者可以通过访问设备管理器，在用户设备上执行任意文件，从而完全控制受害者设备。

恶意软件背后的黑手是俄罗斯人并不奇怪，奇怪的是这个样本明显针对的是俄罗斯人，这是有些不同寻常的。

我们发现Ewind的开发者不仅可以通过开发恶意软件谋取利益，也会经营Android应用商店网站，经过几年的经营，提供了成千上万次Android下载，以支持其广告谋利行为。

<br>

**十一、攻击指示器**

Ewind的C2服务器域名：



```
mobincome[.]org
androwr[.]ru
```

APK服务特征字符串：

```
b93478b8cdba429894e2a63b70766f91
```
