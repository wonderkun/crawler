
# 【木马分析】XcodeGhost或重出江湖，Google Play大量APP被植入恶意代码


                                阅读量   
                                **112469**
                            
                        |
                        
                                                                                                                                    ![](./img/85636/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：paloaltonetworks.com
                                <br>原文地址：[http://researchcenter.paloaltonetworks.com/2017/03/unit42-google-play-apps-infected-malicious-iframes/](http://researchcenter.paloaltonetworks.com/2017/03/unit42-google-play-apps-infected-malicious-iframes/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](./img/85636/t011f4f01e73baef2fd.jpg)](./img/85636/t011f4f01e73baef2fd.jpg)

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**一、前言**

最近，我们发现Google Play应用商店上有132款安卓应用感染了隐藏的小型恶意IFrame，这些IFrame会在应用的本地HTML页面中嵌入到恶意域名的链接，这些被感染的应用最多有超过10,000频次的安装记录。我们的调查表明，此次感染并不能归咎于应用开发人员，他们其实也是受害者，我们认为最有可能的原因应该是应用开发者的开发平台感染了恶意软件，恶意软件会搜寻应用内的HTML页面，在找到的页面末尾插入恶意内容。如果事实的确如此，那么还需要了解这些应用是如何在不引起开发者警觉的前提下经由已感染的开发者平台开发而成。我们已将调查结果提交给Google安全团队，所有受感染的应用已经从Google Play中移除。

[![](./img/85636/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fface05a78344e2a.png)

图1. Google Play上部分受感染应用

如上图所示，我们观察到受感染的应用程序使用场景涉及芝士蛋糕、园艺以及咖啡桌的设计。这些应用的共同点是它们都使用[Android WebView](https://developer.android.com/reference/android/webkit/WebView.html)来显示静态HTML页面。从表面上看，每个HTML页面作用只是加载本地存储的图片及显示硬编码的文本信息，然而经过深度分析，我们可以发现HTML页面中包含一个链接到恶意域名的隐藏的小型IFrame。虽然在调查过程中，这些域名已经停止对外服务，但Google Play上有这么多应用受到影响还是应该引起我们的重视。

调查结果中更应该引起重视的一点是，某个被感染的页面会试图在加载网页时下载并安装Windows可执行文件，但由于手机运行系统不兼容，使得此类攻击无法奏效。这种行为与Google Android安全报告中最近提及的[非Andorid威胁](https://static.googleusercontent.com/media/source.android.com/en/security/reports/Google_Android_Security_PHA_classifications.pdf)类别非常契合，非Android威胁指的是应用无法直接对用户或Android设备造成危害，但可能对其他平台造成潜在危害。

<br>

**二、感染机制分析**

所有受感染的应用目前只需要请求INTERNET权限，同时使用两个activity，一个用来加载插页式广告，另一个用来加载主程序，后者包含一个Android WebView组件，显示一个本地HTML页面（如图2所示）。WebView组件启用了JavaScriptInterface功能，我们分析的样本中没有使用该功能，但这个接口的存在使得页面可以通过加载JavaScript代码来访问应用的原生功能。

[![](./img/85636/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cdd3b87dba191b12.png)

图2. 受感染应用的界面及内部代码示例

每个HTML页面仅用来显示图片及文本信息，但在每个HTML页面末尾都嵌入了一个小型的隐蔽性IFrame组件。我们观察到了两种对该IFrame进行隐藏的技术，一种是将IFrame的高度和宽度都设为1像素，另一种是将IFrame的display属性设为None。最后，为了规避基于简单文本匹配的检测技术，恶意URL源通过使用HTML编码进行了混淆处理。在图3的示例中，浏览器会对以下混淆编码进行自动转换处理：

```
‘.’ → ‘.’
‘i’ → ‘i’
‘u’ → ‘u’
```

[![](./img/85636/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b309163caec77644.png)

图3. 受感染样本中对IFrame进行隐藏的两种技术

最后，所有的IFrame代码都会收敛到以下两个域名：

```
www.Brenz.pl/rc/
jL.chura.pl/rc/
```

波兰CERT（cert.pl）于2013年接管了这两个域名并将其直接部署到污水渠服务器（sinkhole server），以避免后续有用户受到攻击影响（如图4所示）。因此，这两个域名在我们调查时已经不再为恶意软件提供托管服务，但它们的黑历史可是臭名昭著[见参考链接1~5]。

[![](./img/85636/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0197f4fd5fe5a4c16c.png)

图4. 两个恶意域名已指向污水渠服务器

在我们调查中，我们还定位了一个不包含恶意IFrame的样本，但其HTML中却嵌入了一个完整的VBScript脚本（如图5所示）。脚本包含一段Base64编码的Windows可执行文件，在Windows系统上，脚本会对该文件进行解码，写入到文件系统中并加以执行。由于VBScript是Windows专有的脚本语言，该页面无法在Android平台上开展恶意行为，因此无法对Android用户造成危害。这段代码首先会被附加到&lt;HTML&gt;标签外部，构成一个格式错误的HTML页面，但这并不影响浏览器对它进行渲染。浏览器总是尽量去渲染收到的任何代码，无论其错误与否，以便给普通用户提供一个良好的显示页面。

我们从脚本下载到的PE文件中探测到了多种恶意行为，其中包括：

1、修改系统hosts文件

2、修改Windows防火墙设置

3、向其他进程中注入代码

4、恶意文件自我复制

[![](./img/85636/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0163c08b255ec6c74a.png)

图5. 受感染样本试图下载一个Windows可执行文件

<br>

**三、感染来源**

我们发现的132个应用属于7个不同的开发者。这7个开发者之间存在着地理位置的联系：都与印度尼西亚有关。最直接的一个线索就来自于应用名。很多样本的应用名中都包含“印度尼西亚”关键词，此外，其中一个开发者页面链接到一个个人博客，博客使用的是印尼语。而最清晰的线索来自于证书信息，其中某个开发者证书明确指出了国别为印度尼西亚。

[![](./img/85636/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019e947fe535408edb.png)

图6. 受感染样本与印度尼西亚的关系

HTML文件被恶意IFrame感染的一种途径是通过病毒的文件感染，比如之前的Ramnit病毒。感染Windows主机后，这些病毒会查找硬盘上的HTML文档，将IFrame嵌入到每个HTML文档中。如果某个开发者感染了这类病毒，他们应用的HTML文件就可能被感染。鉴于开发者可能都来自于印度尼西亚，也有可能他们从同一个网站中下载了被感染的IDE环境，或者他们使用了同样一款在线应用程序生成平台。

不管是哪一种情况，我们相信开发者在此次攻击中充当的是受害者角色。我们调查中有其他证据可以支撑这一论点：

1、所有样本中的代码结构有些类似，表明它们可能源自于相同的平台；

2、两个恶意域名都已被指向污水渠服务器，如果开发者就是这些攻击背后的始作俑者，他们应该早就将其替换为可用域名，以获得攻击效果。

3、某个被感染样本试图下载Windows可执行文件，表明攻击者不知道目标平台环境，这显然不是应用开发人员会犯的错误。

<br>

**四、潜在的安全风险及应对办法**

目前，受感染的应用不会对Andorid用户造成损害。然而，本次攻击的确反应了开发平台可以作为恶意软件的“载体”，可以在不引起警觉的前提下将恶意软件散播到其他平台中。与此类似的是我们在2015年发现的XcodeGhost攻击事件，该事件向我们展示了恶意软件如何通过攻击开发者而最终影响终端用户。

从此次事件中我们很容易想象一种更为成功的攻击方式：攻击者可以将当前恶意域名替换为广告URL链接，以获得不菲收入。这种攻击不仅可以窃取开发者的收入，也可以损害开发者的信誉。其次，攻击者可以在远程服务器上部署恶意脚本，利用JavaScriptInterface功能访问受感染应用程序的原生功能。通过这种攻击方法，攻击者可以获取并控制应用内部的所有资源。攻击者也可以悄无声息地替换开发者指定的服务器，拦截所有发往开发者的流量。高级攻击者也可以直接修改应用的内部逻辑，比如添加root功能、请求额外权限、或者下载恶意APK文件等。

用户可以使用Palo Alto的WildFire安全解决方案来自动免疫此次攻击，WildFire内部的APK分析引擎也可以对隐藏型IFrame及相应的域名进行安全分析检测。

<br>

**五、致谢**

感谢来自于Palo Alto网络的Zhi Xu及Claud Xiao在调查过程中提供的帮助支持，同时感谢Google安全团队对受感染应用采取的快速响应措施。

<br>

**六、附录**

恶意域名：

```
www.Brenz.pl/rc/
jL.chura.pl/rc/
```

受感染样本的哈希及包名：

```
c6e27882060463c287d1a184f8bc0e3201d5d58719ef13d9ab4a22a89400cf61, com.aaronbalderapps.awesome3dstreetart
a49ac5a97a7bac7d437eed9edcf52a72212673a6c8dc7621be22c332a1a41268, com.aaronbalderapps.awesomecheesecakeideas
1d5878dce6d39d59d36645e806278396505348bddf602a8e3b1f74b0ce2bfbe8, com.aaronbalderapps.babyroomdesignideas
db95c87da09bdedb13430f28983b98038f190bfc0cb40f4076d8ee1c2d14dae6, com.aaronbalderapps.backyardwoodprojects
28b16258244a23c82eff82ab0950578ebeb3a4947497b61e3b073b0f5f5e40ed, com.aaronbalderapps.bathroominteriordesigns
b330de625777726fc1d70bbd5667e4ce6eae124bde00b50577d6539bca9d4ae5, com.aaronbalderapps.beautifulbotanicalgardens
d6289fa1384fab121e730b1dce671f404950e4f930d636ae66ded0d8eb751678, com.aaronbalderapps.bedroomdesign5d
```

<br>

**七、参考链接**

[1] [https://blog.sucuri.net/2011/03/brenz-pl-is-back-with-malicious-iframes.html](https://blog.sucuri.net/2011/03/brenz-pl-is-back-with-malicious-iframes.html) 

[2] [http://thehackernews.com/2016/04/home-security-system.html](http://thehackernews.com/2016/04/home-security-system.html) 

[3] [http://www.webhostingtalk.com/showthread.php?t=1010284](http://www.webhostingtalk.com/showthread.php?t=1010284) 

[4] [https://www.computerforum.com/threads/virus-blocked-jl-chura-pl-rc.147256/](https://www.computerforum.com/threads/virus-blocked-jl-chura-pl-rc.147256/) 

[5] [https://forum.avast.com/index.php?topic=44657.0](https://forum.avast.com/index.php?topic=44657.0) 
