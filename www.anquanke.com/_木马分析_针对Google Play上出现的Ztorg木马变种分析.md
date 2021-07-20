> 原文链接: https://www.anquanke.com//post/id/86219 


# 【木马分析】针对Google Play上出现的Ztorg木马变种分析


                                阅读量   
                                **223977**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securelist.com
                                <br>原文地址：[https://securelist.com/analysis/publications/78325/ztorg-money-for-infecting-your-smartphone/](https://securelist.com/analysis/publications/78325/ztorg-money-for-infecting-your-smartphone/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p2.ssl.qhimg.com/t01272372a88a10e411.jpg)](https://p2.ssl.qhimg.com/t01272372a88a10e411.jpg)**

****

翻译：[**興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

我们对Ztory变种的[研究](https://securelist.com/blog/mobile/76081/rooting-pokemons-in-google-play-store/)始于在Google Play上所发现的某个恶意软件，该软件伪装成Pokemon GO的指南应用，在Google Play上存活了几周的时间，下载量达到500,000多次。我们将该恶意软件标记为Trojan.AndroidOS.Ztorg.ad。经过一番搜索，我发现Google Play商店中还存在其他类似的恶意应用，第一个应用就是“Privacy Lock”应用，该恶意应用于2016年12月15日上传到Google Play中，是最流行的Ztorg变种之一，有超过1百万次的安装量。

在跟踪这类被感染的应用程序一段时间之后，有两个现象让我非常吃惊，那就是这些应用传播非常迅速而且应用的评论比较特别。

<br>

**二、流行性分析**

这些被感染的应用扩散速度非常快，每天都有超过上千个新用户激活。

比如，在我将com.fluent.led.compass报告给Google的那天，这个应用有10,000-50,000次安装量。

[![](https://p2.ssl.qhimg.com/t0110c9c7d7ddad0fe7.png)](https://p2.ssl.qhimg.com/t0110c9c7d7ddad0fe7.png)

然而，第二天Google Play上还是能看到这个应用的身影，并且这个应用的安装次数增加了十倍，达到了100,000–500,000。这意味着在短短一天内，至少有5万名新用户被感染。

<br>

**三、应用评论**

在这些应用的评论中，很多人提到他们是为了赚取信用、金币等等才下载这些应用。

[![](https://p1.ssl.qhimg.com/t013ecb5633fac7205c.png)](https://p1.ssl.qhimg.com/t013ecb5633fac7205c.png)

[![](https://p4.ssl.qhimg.com/t0199a778dcb75ddba9.png)](https://p4.ssl.qhimg.com/t0199a778dcb75ddba9.png)

[![](https://p5.ssl.qhimg.com/t01154b5ef308efa73f.png)](https://p5.ssl.qhimg.com/t01154b5ef308efa73f.png)

在某些评论中，用户还提到了其他应用，比如Appcoins、Advertapp等。

综合这些原因，我着手开始研究这些应用。

<br>

**四、广告**

**4.1 付费推广的应用**

大多数评论中提到的应用为Appcoins，因此我安装了这个应用。安装完毕后，它推荐我安装其他一些应用来赚取0.05美元，其中包括某个恶意应用。

[![](https://p3.ssl.qhimg.com/t01e39991ab4b3cb702.png)](https://p3.ssl.qhimg.com/t01e39991ab4b3cb702.png)

说实话，我比较惊讶的是只有一个应用是恶意的，其他应用都是干净的。

有趣的是这些应用会检查它们是否具备目标设备的root权限，如果已具备目标设备的root权限，它们就不会付给用户酬劳。感染目标设备后，Ztorg变种干的第一件事情就是获取超级用户（superuser）权限。

我联系过Appcoins的开发者，想知道这些恶意广告的来源，然而他们只是删除了这些推广广告，然后告诉我他们没有发现恶意软件，因此他们没有做错什么。

之后我分析了被感染用户所安装的那些应用，整理了一份向用户付费以推广应用的列表，进入这个列表的应用安装量都比较大。列表中包含以下应用：

[![](https://p5.ssl.qhimg.com/t01ab0abd8f2f5926f8.png)](https://p5.ssl.qhimg.com/t01ab0abd8f2f5926f8.png)

[mobi.appcoins](https://play.google.com/store/apps/details?id=mobi.appcoins)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01335e32a52330fd8c.png)

[com.smarter.superpocket](https://play.google.com/store/apps/details?id=com.smarter.superpocket)

[![](https://p1.ssl.qhimg.com/t01af5f376c43d749ae.png)](https://p1.ssl.qhimg.com/t01af5f376c43d749ae.png)

[com.moneyreward.fun](https://play.google.com/store/apps/details?id=com.moneyreward.fun)

当然，这些应用也都在推广其他恶意应用：

[![](https://p4.ssl.qhimg.com/t013a18e349a74d79ba.png)](https://p4.ssl.qhimg.com/t013a18e349a74d79ba.png)

[![](https://p0.ssl.qhimg.com/t013c9c3b0b032a535c.png)](https://p0.ssl.qhimg.com/t013c9c3b0b032a535c.png)

每当用户从Google Play上下载及安装被Ztorg感染的应用后，这些应用都会向用户支付0.04-0.05美元。

**4.2 广告联盟**

因此我决定好好研究一下这些应用，导出并分析这些应用的流量。

一个广告应用变成一个恶意应用的典型流程如下：

1、应用程序从服务器接收推广命令（包括恶意推广在内，如moneyrewardfun[.]com）。恶意推广都来自于著名的广告服务商（通常为supersonicads.com以及aptrk.com）。

2、经过广告服务商域名的几次重定向之后（在某个案例中，重定向次数达到了27次），应用会访问global.ymtracking.com或者avazutracking.net，这两个URL也与广告有关系。

3、应用再次重定向到track.iappzone.net。

4、最终指向Google Play应用商店的URL为app.adjust.com。

在我导出的所有推广链接中，都会包含track.iappzone.net以及app.adjust.com这两个URL。

adjust.com是一个著名的“商务智能平台”；恶意广告联盟中使用的URL地址如下所示：

```
https://app.adjust.com/4f1lza?redirect=https://play.google.com/store/apps/details?id=com.game.puzzle.green&amp;install_callback=http://track.iappzone.net
```

我们能够通过这类URL地址，识别出Google Play上被感染的那些应用程序。

**4.3 恶意服务器**

来自于iappzone.net的URL如下所示：

```
http://track.iappzone.net/click/click?offer_id=3479&amp;aff_id=3475&amp;campaign=115523_201%7C1002009&amp;install_callback=http://track.supersonicads.com/api/v1/processCommissionsCallback.php?advertiserId=85671&amp;password=540bafdb&amp;dynamicParameter=dp5601581629793224906
```

在这个URL中，“offer_id=..&amp;aff_id=..&amp;campaign=..”与OffersLook跟踪系统有关。URL中包含许多有趣的部分，比如推广ID（offer id）、归属ID（affiliate id）等。我发现不同的攻击者所使用的这些字段值也不一样，因此我们没法使用这些参数，但install_callback这个参数对我们而言是有价值的，这个参数包含广告服务商的名字。

在搜索iappzone.net时，我发现某些APK文件包含了这个URL，这些应用都被卡巴斯基实验室标记为Ztorg恶意软件。有趣的是iappzone.net的IP地址为52.74.22.232，这个地址也被aedxdrcb.com所使用，后者出现在CheckPoint的gooligan研究报告中。这个报告公布几周之后，iappzone.net迁移到了一个新的地址上：139.162.57.41，新的这个地址没有在报告中出现过。

**4.4 广告模块**

幸运的是，我不仅能在APK文件中找到iappzone.net，也能在干净应用的网络流量中找到这个特征。所有的这些应用都包含广告模块，大多数情况下为Batmobi或者Mobvista。这些广告模块的网络流量与付费推广应用的网络流量看起来非常相似。

以某个使用Batmobi广告模块的应用为例。这个模块从api2.batmobil.net服务器接收一个包含推广信息的JSON文件，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b2cfc36f1e0afdf8.png)

用户会看到如下所示的一个推广应用列表：

[![](https://p5.ssl.qhimg.com/t01c32f4ed5f79c0433.png)](https://p5.ssl.qhimg.com/t01c32f4ed5f79c0433.png)

用户点击这些广告后，会被重定向到Google Play商店中：

[![](https://p4.ssl.qhimg.com/t01e05092224cefa3c0.png)](https://p4.ssl.qhimg.com/t01e05092224cefa3c0.png)

在这个例子中，重定向过程如下所示：

```
api2.batmobil.net -&gt; global.ymtracking.com-&gt;tracking.acekoala.com -&gt; click.apprevolve.com -&gt;track.iappzone.net -&gt;app.adjust.com -&gt; play.google.com
```

在分析了包含iappzone.net的广告应用后，我发现Google Play上有将近100个被感染的应用被推广过。

这些广告软件比较有趣的另一点就是，它们的URL地址都包含我前面提到过的install_callback参数。结果表明，攻击者只使用了4个广告网络。

**4.5 广告源**

通过track.iappzone.net，我们发现有4个不同的install_callback参数，占比如下：

[![](https://p5.ssl.qhimg.com/t01b1267da889575a65.png)](https://p5.ssl.qhimg.com/t01b1267da889575a65.png)

但这并不意味着恶意软件只通过这4个网络进行分发。这些广告网络向许多广告公司售卖他们的广告。在我的研究中，我看到某些恶意广告来自于其他广告网络，如DuAd或者Batmobi，但经过几次重定向之后，这些广告总会指向上表列出的4个广告网络中的某一个。

此外，我跟踪了几个恶意的广告软件，发现有如下的重定向过程：

```
Batmobi -&gt; Yeahmobi-&gt; SupersonicAds
```

这意味着这些网络之间也会向彼此重新分发广告。

截至2017年3月底，我没有在install_callback参数中发现其他的广告网路。

**4.6 其他源**

在研究过程中，我发现某些已感染的应用没有通过这些广告网络进行推广。经过分析，我发现这些应用的文件路径中包含某些特征。这些应用所在的文件路径（除了安装路径“/data/app”之外）主要如下所示：



```
[sdcard]/.android/ceroa/play/
[sdcard]/.nativedroid/download/
[sdcard]/.sysAndroid/download/
[sdcard]/.googleplay_download/
[sdcard]/.walkfree/apks/583737491/
[sdcard]/Android/data/TF47HV2VFKD9/
[sdcard]/Android/Data/snowfoxcr/
[sdcard]/DownloadProvider/download/
```

我分析了包含以上路径的那些应用，发现它们都被卡巴斯基实验室的产品标记为广告软件或恶意软件。然而，下载到这些路径的应用不全为恶意软件，其实这些应用大部分都是干净的。<br>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01393453f1f443fe19.png)

注：占比指的是下载到同一目录中的恶意软件在全部应用中的比例。

<br>

**五、已感染的应用**

**5.1 类似应用**

我分析了所有被感染的应用，令我惊讶的是，这些应用看起来并不是因为被恶意代码篡改而被感染的。在许多情况下，攻击者会将恶意代码添加到干净的应用中，但本文分析的这些应用不属于这类情况。貌似这些应用就是专门为分发恶意软件而创建的。

**5.2 Google Play上的应用发布者**

其中部分应用在Google Play上的发布者信息如下所示：

[![](https://p0.ssl.qhimg.com/t0127fb43289511111e.png)](https://p0.ssl.qhimg.com/t0127fb43289511111e.png)

经过一番搜索，我发现大部分邮箱都与越南有关。

比如：

1、trantienfariwuay -&gt; tran tien [fariwuay] – 某个越南歌手

2、liemproduction08 -&gt; liem production [08] – Thuat Liem Production，为越南胡志明市的一家公司

3、nguyenthokanuvuong -&gt; nguyen [thokanu] vuong – 中文名“Wang Yuan”的越南版

**5.3 恶意模块**

这些来自于Google Play的所有被感染的应用都包含同样的功能，那就是下载并执行主功能模块。在分析过程中，我发现有三个模块具备此功能。

**5.3.1 Dalvik**

使用此类型恶意模块的Google Play应用都使用加壳器进行保护。以包名为“com.equalizer.goods.listener”的应用为例，这个应用使用了奇虎加壳器进行处理。这个应用有许多不同的类，但只有一部分类与恶意模块有关。PACKAGE_ADDED以及PACKAGE_REMOVED这两个系统事件会触发恶意代码执行。这意味着只有在用户安装、更新或者删除某个应用后，恶意代码才会开始执行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01541bbb3a8710375b.png)

开始运行时，恶意模块会检查自己是否运行在虚拟机、模拟器或者沙箱中。为了完成这一检测过程，它会检查不同机器上的数十个文件，同时也会检查数十个不同的系统属性。如果这个检查过程通过，木马将会启动一个新的线程。

在这个新的线程中，木马会随机等待一段时间，大约为1到1个半小时。等待时间结束后，它会向C2服务器（em.kmnsof.com/only）发起一个HTTP GET请求，然后会收到服务器返回的一个经过DES加密的JSON文件。这个JSON文件包含一个URL，通过这个URL可以下载某个文件。所下载的这个文件经过异或处理，包含恶意的class.dex模块，也就是主功能模块。

**5.3.2 Native**

自2016年10月以来，我已经向Google报告了许多使用该恶意模块的应用，因此Google得以改进他们的探测系统，拦截了大多数恶意应用。这意味着攻击者必须绕过官方的检测机制。最开始的时候，攻击者通过修改源代码中的某些方法以及使用商业加壳器来绕过检测。但在2017年2月，他们重写了这个代码，将所有的功能迁移到ELF库中（native模式，.so库）。

以com.unit.conversion.use为例（MD5为92B02BB80C1BC6A3CECC321478618D43）。

恶意代码会在应用的onCreate方法中执行：

[![](https://p1.ssl.qhimg.com/t01b829a792670fb7ac.png)](https://p1.ssl.qhimg.com/t01b829a792670fb7ac.png)

已感染的classes.dex中的恶意代码比较简单，恶意代码会启动一个新的线程，加载MyGame库，代码包含两个检测沙箱的方法，这两个方法会通过库加载执行。

[![](https://p2.ssl.qhimg.com/t01f070e696a0502415.png)](https://p2.ssl.qhimg.com/t01f070e696a0502415.png)

这个版本所使用的等待时间比上一个版本小得多，它在执行代码前只等待了82秒。

MyGame库在执行后，会执行classes.dex中的两个方法，以检查自己是否运行在沙箱中。其中一个方法会尝试注册BATTERY_CHANGED事件的接收器，检查是否注册成功。另一个方法会尝试使用MATCH_UNINSTALLED_PACKAGES标志获取com.android.vending package（即Google Play商店）的应用信息。如果这两个方法都返回“false”，这个恶意库就会向命令服务器发起一个GET请求：

[![](https://p2.ssl.qhimg.com/t0171e85b2068fa4fdc.png)](https://p2.ssl.qhimg.com/t0171e85b2068fa4fdc.png)

服务器返回的信息为“BEgHSARIB0oESg4SEhZcSUkCCRFICAUSHwoLEhZIBQkLSQ4fSQ4fVlZVSQEWVlZVSAcWDUpeVg==”。

[![](https://p5.ssl.qhimg.com/t01256885f5c821ee9c.png)](https://p5.ssl.qhimg.com/t01256885f5c821ee9c.png)

这个库会使用0x66作为异或密钥，用来解码这个响应消息

解码后的结果为：

```
b.a.b.a,b,http://dow.nctylmtp.com/hy/hy003/gp003.apk,80
```

与代码中对应的变量为：



```
g_class_name = b.a.b.a
g_method_name = b
g_url = http://dow.nctylmtp.com/hy/hy003/gp003.apk
g_key = 80
```

g_url所指向的.apk文件会被下载到app缓存目录中（/data/data/&lt;package_name&gt;/cache）。这个库会使用g_key作为密钥，对apk文件进行异或处理，然后使用DexClassLoader类中的ClassLoad方法加载解密后的apk文件。

正如我们所看到的，攻击者对恶意代码做了大量修改，将Java代码替换为C代码。但恶意功能得以保留，比如依然能够连接到C2服务器、下载和执行主模块。

在我成功提取这些恶意软件的包ID之后，我在测试设备上通过Google Play安装了已感染的应用，但没有观察到任何现象。经过一番调查，我发现攻击者只会向用户提供一个恶意载荷，通过广告来安装应用。然而，我在测试设备上通过Google Play安装其他一些被感染应用后，它们会立刻感染我的测试设备，甚至不需要我点击任何广告。

**5.3.3 下载器**

2017年4月，攻击者再次更改了Ztorg的代码。在第三种恶意模块中，攻击者将所有的功能再次迁回到classes.dex。这个版本的模块与之前版本的主要区别在于它再也不是一个木马下载器。这个版本的恶意模块不会从恶意服务器上下载主功能模块，而是在安装包的Assets文件夹中包含一个加密的模块。这个加密模块使用0x12密钥进行异或解密，再使用ClassLoad方法加载执行。

[![](https://p4.ssl.qhimg.com/t01064403d432e94998.png)](https://p4.ssl.qhimg.com/t01064403d432e94998.png)

**5.3.4 载荷（主模块）**

在我所分析的所有的攻击活动中，它们使用的主模块功能都具备相同的功能。以最新的变种（2dac26e83b8be84b4a453664f68173dd）为例，这个变种由某个应用（“com.unit.conversion.use”）通过恶意的MyGame库下载所得。

载荷模块由已感染的模块下载，使用ClassLoad方法加载运行。载荷模块的主要目的是获取root权限并安装其他模块，该模块通过下载或释放其他模块方式达到这一目标。

某些文件没有对应的URL地址，只能由该模块释放得到。

在研究过程中，使用“down.118pai.com”域名的某些URL已经失效，使用这些URL的所有文件都可以通过载荷释放而得。其他使用“sololauncher.mobi”以及“freeplayweb.com”作为URL的文件只能通过远程方式下载得到，这些URL在研究过程中都是有效的。

在2016年9月版本的主模块中，所有的URL使用的都是“down.118pai.com”域名，并且这些URL当时处于活跃状态。

载荷所释放或下载的某些恶意文件会添加到“/system/etc/install-recovery.sh”文件中。这意味着即使目标设备恢复为出厂设置状态，这些文件依然存在。

载荷释放和下载的文件可以归为以下几类：

1、非恶意文件及工具

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f112c008194fabad.png)

2、漏洞利用相关工具

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0101e38efad7201362.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0136720390eb145adb.png)

这些文件中大多数都是通过木马下载而得，但某些文件只能通过木马文件释放。然而，大多数下载的文件与7个月之前（即2016年9月）的版本相同。

3、原生（ELF）恶意模块

[![](https://p5.ssl.qhimg.com/t0127975cac8a3a68cf.png)](https://p5.ssl.qhimg.com/t0127975cac8a3a68cf.png)

所有的这类文件只能通过木马文件释放，不能通过下载方式获取。

4、恶意应用

[![](https://p0.ssl.qhimg.com/t01566231eb421be269.png)](https://p0.ssl.qhimg.com/t01566231eb421be269.png)

这四个恶意应用的分析如下：

（1）.gmtgp.apk (7d7247b4a2a0e73aaf8cc1b5c6c08221)

该恶意应用被检测为Trojan.AndroidOS.Hiddad.c，它会（从C2服务器http://api.ddongfg.com/pilot/api/上）下载另外一个加密模块，经过解密处理后再加载该模块。在分析过程中，该样本下载的模块为Trojan-Clicker.AndroidOS.Gopl.a（af9a75232c83e251dd6ef9cb32c7e2ca）。

木马的C2服务器为“http://g.ieuik.com/pilot/api/”，还可以使用“g.uikal.com”以及“api.ddongfg.com”作为C2服务器的域名。

该木马使用无障碍辅助服务（accessibility services）从Google Play应用商店上安装（甚至购买）应用。

[![](https://p1.ssl.qhimg.com/t0106db7850fe597170.png)](https://p1.ssl.qhimg.com/t0106db7850fe597170.png)

木马将应用下载到SD卡上的“.googleplay_download”目录，使用无障碍辅助服务，模拟点击按钮来安装下载的应用。“.googleplay_download”文件夹是Ztorg木马传播所使用的文件夹之一。木马能够识别13种语言的按钮，包括英语、西班牙语、阿拉伯语、印地语，印尼语、法语、波斯语、俄语、葡萄牙语、泰语、越南语、土耳其语以及马来语。

（2）dpl.apk (87030AE799E72994287C5B37F6675667)

这个模块用来检测模拟器、沙箱以及虚拟机的方法与原始的模块一样。

该木马会从C2服务器（api.jigoolng.com/only/gp0303/12.html）上下载一个加密的文件，保存为目标设备的“/.androidsgqmdata/isgqm.jar”文件。文件解密完成后会被木马会加载。

dpl.apk的主要功能是下载及安装应用，它可以从以下几个C2服务器上接收指令：

1、log.agoall.com/gkview/info/,

2、active.agoall.com/gnview/api/,

3、newuser.agoall.com/oversea_adjust_and_download_write_redis/api/download/,

4、api.agoall.com/only/

该模块会将下载的应用保存到SD卡上的DownloadProvider目录，该目录也是Ztorg木马所使用的目录之一。

我所研究的样本下载了5个恶意的APK文件，其中4个安装成功，并且会出现在设备的已安装应用列表中。

（3）.gma.apk (6AAD1BAF679B42ADB55962CDB55FB28C)

该木马会尝试下载isgqm.jar模块，这个模块的主要功能与其他模块的相同。不幸的是，木马的C2服务器（a.gqkao.com/igq/api/，d.oddkc.com/igq/api/，52.74.240.149/igq/api，api.jigoolng.com/only/）没有返回任何响应，因此我没办法了解这个应用的主要目的。

这个应用会修改目标设备上的“/system/etc/install-recovery.sh”，将下载的应用保存到SD卡的“/.androidgp/”文件夹中，并将这些应用安装到系统文件夹中（/system/app/或者/system/priv-app/）。

我认为这个木马的功能是用来更新其他的模块。

（4）.gmq.apk (93016a4a82205910df6d5f629a4466e9)

该木马无法通过C2服务器（a.apaol.com/igq/api，c.oddkc.com/igq/api，52.74.240.149/igq/api）下载它所用的isgq.jar模块。

**5.3.5安装的应用**

设备感染木马后，会静默下载及安装以下应用。这些应用都包含非常著名的广告服务。

[![](https://p0.ssl.qhimg.com/t01b31551d317c9907c.png)](https://p0.ssl.qhimg.com/t01b31551d317c9907c.png)

这些应用还包含其他恶意模块，在成功接收C2服务器的指令后，会开始下载广告及其他应用。

但使用干净的广告网络（如Mobvista以及Batmobi）也会出现递归广告现象，因为最开始被感染的应用也是通过这些广告网络进行投递。

成功感染目标设备后，木马会创建一些新的文件夹，如下所示：

1、.googleplay_download

2、.nativedroid

3、.sysAndroid

4、DownloadProvider

某些恶意软件会使用这几个文件夹来传播Ztorg木马，木马感染成功后会使用这些文件夹来投递其他应用，其中包含某些恶意应用。

**5.4 其他木马**

在这次研究过程中，我们发现从Google Play上下载的每个木马基本都包含前文描述的三个恶意模块之一，但我们还是发现了其他一些不同的木马。

其中一个木马名为Money Converter（com.countrys.converter.currency，55366B684CE62AB7954C74269868CD91），这个木马已经通过Google Play渠道安装了超过10,000次。它的目的与.gmtgp.apk模块类似，会使用无障碍辅助服务从Google Play上安装应用。因此，即使无法获取设备的root权限，这个木马也可以不需要跟用户交互，静默安装及运行推广应用。

[![](https://p5.ssl.qhimg.com/t01f7044c68be344339.png)](https://p5.ssl.qhimg.com/t01f7044c68be344339.png)

该木马的C2服务器地址与.gmtgp.apk所使用的C2服务器地址相同。

<br>

**六、总结**

在本次研究过程中，我发现Trojan.AndroidOS.Ztorg木马以不同的应用（超过100个应用）上传到Google Play商店中。第一个与之相关的应用是Privacy Lock，于2015年12月中旬上传到Google Play商店中，有超过1百万次的安装量。从2016年9月份起，我就开始跟踪这个木马，之后我发现Google Play上至少还有3个新的已感染的应用。我最近发现的木马应用于2017年4月份上传到Google Play上，我相信还有会其他的木马应用被上传上去。

这些木马应用都非常受欢迎，它们的扩散速度非常快，每天都有成百上千个新用户被感染。

我发现这些木马会通过广告网络实时投放。与之相关的广告地址都包含相同的URL，因此我们可以借此跟踪有哪些新感染的应用被下载。

[![](https://p3.ssl.qhimg.com/t01b84d387eea9a2dd6.png)](https://p3.ssl.qhimg.com/t01b84d387eea9a2dd6.png)

让我非常惊讶的是，某些应用会向用户支付酬劳以推广应用，进而投递这些木马。事实证明，某些用户会收到几美分的酬劳，代价是他们的设备会在毫不知情的情况下被感染。

在木马投递方面，还有一件事情比较有趣，那就是感染成功后，木马会使用某些广告网络向用户展示广告，以便安装推广应用。这种情况下，在已感染的设备上会出现广告递归现象，即设备因为某个广告网络投递的某个恶意广告而被感染，感染之后，设备上的木马及木马模块会再次使用相同的广告网络来向用户展示广告。

攻击者之所以能够成功将被感染的应用在Google Play上发布，是因为他们使用了许多技术来绕过官方的检测。攻击者始终不断地在他们的木马中研发和应用新的技术。这个木马拥有模块化的架构，使用了多个具有不同功能的模块，这些模块都可以通过互联网进行更新。在感染过程中，Ztorg会使用多个本地root漏洞利用工具来获取设备的root权限。获取root权限后，木马就能实现在目标设备上的驻留，也可以更加粗暴地投递广告。
