> 原文链接: https://www.anquanke.com//post/id/85858 


# 【技术分享】如何检测Edge浏览器中已安装的扩展应用


                                阅读量   
                                **91354**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：brokenbrowser.com
                                <br>原文地址：[https://www.brokenbrowser.com/microsoft-edge-detecting-installed-extensions/](https://www.brokenbrowser.com/microsoft-edge-detecting-installed-extensions/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p0.ssl.qhimg.com/t019a45a577da300065.jpg)](https://p0.ssl.qhimg.com/t019a45a577da300065.jpg)

作者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：160RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

对攻击者来说，如果能够收集受害者的指纹信息是最好不过的事情。在前面的文章中，我们已经知道攻击者可以利用漏洞来检[测特定文件](https://www.brokenbrowser.com/detecting-local-files-to-evade-analysts/)的存在（以规避安全分析人员的检测），也可以[将mimeTypes与应用程序相关联](https://www.brokenbrowser.com/detecting-apps-mimetype-malware/)。微软及时修复了这两个漏洞，也封堵了与之相关的[其他漏洞](https://twitter.com/magicmac2000/status/790614692364517376)。今天，我们将向读者展示如何检测Edge浏览器中已安装的扩展应用。

4月5日，Nataliia Bielova发布了一条[推文](https://twitter.com/nataliabielova/status/849629018756444160)，介绍了[某个网站](https://extensions.inrialpes.fr/)如何检测多个浏览器上已安装的扩展应用，但微软的Edge并不包括在内。

[![](https://p0.ssl.qhimg.com/t010d9470d5fa3231f4.png)](https://p0.ssl.qhimg.com/t010d9470d5fa3231f4.png)

如果读者希望进一步了解如何检测Firefox和Chrome浏览器的扩展应用，可以参考[这篇文章](http://www.cse.chalmers.se/research/group/security/publications/2017/extensions/codaspy-17.pdf)以获取更多知识。本文我们将在Edge浏览器上完成同样任务。

<br>

**二、安装扩展**

在Edge浏览器的[扩展商店](https://www.microsoft.com/en-us/store/collections/edgeextensions/pc)中，我随机选择一款名为[AdGuard blocker](https://www.microsoft.com/en-us/store/p/adguard-adblocker/9mz607gwkbs7)的扩展应用。两次鼠标点击后，扩展已安装完毕，自动打开了一个感谢页面。正是这个页面给了我研究的灵感，如下图所示：

[![](https://p5.ssl.qhimg.com/t01fe82ad47879823bf.png)](https://p5.ssl.qhimg.com/t01fe82ad47879823bf.png)

我们可以利用上面的URL信息开始研究。如果我们能够在一个iframe内部中加载该URL，通过onload或onreadystatechange事件（或者其他事件），判断获取的是Edge浏览器的标准404页面（即扩展未安装）还是该扩展的thankyou.html页面，那么我们基本上就可以判断该扩展是否存在。不幸的是，iframe拒绝加载该扩展的URL。

```
&lt;iframe src="ms-browser-extension://EdgeExtension_AdguardAdguardAdBlocker_m055xr0c82818/pages/thankyou.html"&gt;&lt;/iframe&gt;
```

[![](https://p3.ssl.qhimg.com/t01122d090b3a582c51.png)](https://p3.ssl.qhimg.com/t01122d090b3a582c51.png)

如果使用windows.open方法，结果如何呢？我们可以尝试在脚本中打开扩展的URL：



```
win = window.open("ms-browser-extension://EdgeExtension_AdguardAdguardAdBlocker_m055xr0c82818/pages/thankyou.html");
// win returns null when the URL is ms-browser-extension
```

[![](https://p5.ssl.qhimg.com/t01fa2981316a8141f1.png)](https://p5.ssl.qhimg.com/t01fa2981316a8141f1.png)

页面打开成功！不过对我们来说这个结果用处不大，因为不管扩展是否安装，windows对象返回值始终为空（null）。换句话说，当我们试图使用ms-browser-extension扩展协议打开一个新建窗口时，返回结果始终为null。因此即使我们的确能够打开浏览器窗口（当然这是个丑陋的解决方案），我们也无法判断获取的结果是否准确。

我们是否可以利用扩展中的图片来判断呢？扩展中的图片有可能会暴露在主页面中，我们可以使用onload或onerror事件检测扩展是否安装。首先，我们需要找出扩展文件存放在文件系统中具体位置。

<br>

**三、定位扩展文件**

运行Process Monitor，将MicrosoftEdgeCP.exe添加到过滤规则中。打开Edge浏览器，在地址栏中输入AdGuard扩展的URL，载入扩展的感谢页面。在Process Monitor中，我们很快就可以定位到扩展文件所处的具体位置。记住我们的目标是找出扩展中的图片，判断是否可以通过onload或onerror事件检测图片的存在。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0137b5c7aab1a1c02b.png)

看起来扩展文件存放在如下位置：

```
C:Program FilesWindowsAppsAdguard.AdguardAdBlocker_2.5.18.0_neutral__m055xr0c82818ExtensionPages
```

访问上一层目录，我们可以看到其中存在一个manifest.json文件，定义了某些资源可以被任何网站加载，与Chrome或Firefox浏览器类似。



```
"web_accessible_resources": [
   "elemhidehit.png", 
   "lib/content-script/assistant/css/assistant.css", 
   "lib/content-script/assistant/i/close.svg", 
   "lib/content-script/assistant/i/logo.svg", // Let's use this one!
   "lib/content-script/assistant/i/logo-white.svg"
]
```

这些资源大多数都是图片资源，我们可以尝试使用下面这个脚本加载logo.svg图片，如果触发onload事件，则表明该扩展已安装，否则表明用户并没有安装该扩展。



```
var img = new Image();
img.onload = function()`{`alert("Extension Detected")`}`
img.onerror = function()`{`alert("Extension NOT Detected")`}`
img.src = "ms-browser-extension://EdgeExtension_AdguardAdguardAdBlocker_m055xr0c82818/lib/content-script/assistant/i/logo.svg";
```

[![](https://p3.ssl.qhimg.com/t014c2a55768ceb4b51.png)](https://p3.ssl.qhimg.com/t014c2a55768ceb4b51.png)

这种方法并没有让我眼前一亮，因为我们还是重复以前检测的老套路（与Chrome和FireFox浏览器上的方法类似），我们过度依赖于扩展的积极配合，允许我们加载其内部资源。如果某个扩展在manifest文件中不存在Web可以访问的资源，这种情况下我们如何检测它的存在呢？

<br>

**四、检测扩展的通用方法**

经过了短暂的尝试后，我决定借鉴Soroush提出的IE DTD技巧，这类技巧尝试使用微软的XMLDOM对象加载资源，通过错误号来判断资源文件的存在与否。在Edge浏览器上，我们没有XMLDOM对象，但我们可以使用与之类似的XMLHttpRequest对象。

使用XMLHttpRequest对象打开资源时，如果扩展存在，它会抛出拒绝访问异常，否则会抛出未指定错误异常。为了表示对Soroush成果的尊重，我们同样采用异常错误号来判断所抛出的异常类别。代码如下所示：



```
var extension = "ms-browser-extension://EdgeExtension_AdguardAdguardAdBlocker_m055xr0c82818";
try
`{`
     var xhr = new XMLHttpRequest();
     xhr.open("GET", extension, false);
     xhr.send(null);
`}`
catch(e)
`{`
     if (e.number == -2147024891) alert("Exists");
     else alert("Does not exist");
`}`
```

[![](https://p4.ssl.qhimg.com/t01b620391906453bed.png)](https://p4.ssl.qhimg.com/t01b620391906453bed.png)

结果非常不错，感谢Soroush的伟大发现。

顺便提一下，你是否注意到我们使用的URL并没有指向任何一个资源文件？这涉及到XML的一些技巧。对XML来说，使用目录名就已足够，我们不需要指向某个特定资源，只需要掌握扩展的ID信息就足以检测扩展是否存在。如果我们希望实现一个通用的检测工具，查找所有的扩展信息，我们首先需要在自己的Edge浏览器上安装所有的扩展，记录这些扩展的ID。我们只需要在安装扩展后，打开一个空白页面，按下F12，就可以找到扩展的ID信息。如下图所示：

[![](https://p0.ssl.qhimg.com/t013dd485ad37bb5b96.png)](https://p0.ssl.qhimg.com/t013dd485ad37bb5b96.png)

我们现在可以利用这些信息为Edge浏览器创建一个通用的扩展检测工具。已禁用的扩展不会在开发者工具中加载，但我们还是可以在注册表中找到它们。

```
HKEY_CLASSES_ROOTLocal SettingsSoftwareMicrosoftWindowsCurrentVersionAppContainerStoragemicrosoft.microsoftedge_8wekyb3d8bbweMicrosoftEdgeExtensions
```

即使用户禁用了扩展，我们的检测方法仍然行之有效。我们利用PoC检测出来的20个已安装的扩展信息，如下图所示。

[![](https://p2.ssl.qhimg.com/t01405b085ef53e8ea0.png)](https://p2.ssl.qhimg.com/t01405b085ef53e8ea0.png)

检测已安装扩展的PoC可以在[这里](https://www.cracking.com.ar/demos/edgeinstalledextensions/)找到。
