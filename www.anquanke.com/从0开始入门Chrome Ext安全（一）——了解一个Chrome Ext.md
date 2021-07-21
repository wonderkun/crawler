> 原文链接: https://www.anquanke.com//post/id/193666 


# 从0开始入门Chrome Ext安全（一）——了解一个Chrome Ext


                                阅读量   
                                **1080982**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01d167f302936761b3.jpg)](https://p2.ssl.qhimg.com/t01d167f302936761b3.jpg)



作者：LoRexxar’@知道创宇404实验室

在2019年初，微软正式选择了Chromium作为默认浏览器，并放弃edge的发展。并在19年4月8日，Edge正式放出了基于Chromium开发的Edge Dev浏览器，并提供了兼容Chrome Ext的配套插件管理。再加上国内的大小国产浏览器大多都是基于Chromium开发的，Chrome的插件体系越来越影响着广大的人群。

在这种背景下，Chrome Ext的安全问题也应该受到应有的关注，《从0开始入门Chrome Ext安全》就会从最基础的插件开发开始，逐步研究插件本身的恶意安全问题，恶意网页如何利用插件漏洞攻击浏览器等各种视角下的安全问题。

第一部分我们就主要来聊聊关于Chrome Ext的一些基础。



## 获取一个插件的代码

Chrome Ext的存在模式类似于在浏览器层新加了一层解释器，在我们访问网页的时候，插件会加载相应的html、js、css，并解释执行。

所以Chrome Ext的代码也就是html、js、css这类，那我们如何获取插件的代码呢？

当我们访问扩展程序的页面可以获得相应的插件id

[![](https://p1.ssl.qhimg.com/t012521d01c77249b87.png)](https://p1.ssl.qhimg.com/t012521d01c77249b87.png)

然后我们可以在[https://chrome-extension-downloader.com/](https://chrome-extension-downloader.com/)中下载相应的crx包。

把crx改名成zip之后解压缩就可以了

[![](https://p2.ssl.qhimg.com/t01c62ff23f60696c20.png)](https://p2.ssl.qhimg.com/t01c62ff23f60696c20.png)



## manifest.json

在插件的代码中，有一个重要的文件是manifest.json，在manifest.json中包含了整个插件的各种配置，在配置文件中，我们可以找到一个插件最重要的部分。

首先是比较重要的几个字段
<li>browser_action
<ul>
- 这个字段主要负责扩展图标点击后的弹出内容，一般为popup.html- matches 代表scripts插入的时机，默认为document_idle，代表页面空闲时
- js 代表插入的scripts文件路径
- run_at 定义了哪些页面需要插入scripts- 这个字段定义了插件的权限，其中包括从浏览器tab、历史纪录、cookie、页面数据等多个维度的权限定义- 这个字段定义了插件页面的CSP
- 但这个字段不影响content_scripts里的脚本- 这个字段定义插件的后台页面，这个页面在默认设置下是在后台持续运行的，只随浏览器的开启和关闭
- persistent 定义了后台页面对应的路径
- page 定义了后台的html页面
- scripts 当值为false时，background的页面不会在后台一直运行
在开始Chrome插件的研究之前，除了manifest.json的配置以外，我们还需要了解一下围绕chrome建立的插件结构。



## Chrome Ext的主要展现方式

### browserAction – 浏览器右上角

[![](https://p5.ssl.qhimg.com/t010c72b4a4e07f2655.png)](https://p5.ssl.qhimg.com/t010c72b4a4e07f2655.png)

浏览器的右上角点击触发的就是mainfest.json中的browser_action

```
"browser_action": `{`
      "default_icon": "img/header.jpg",
      "default_title": "LoRexxar Tools",
      "default_popup": "popup.html"
    `}`,
```

其中页面内容来自popup.html

### pageAction

pageAction和browserAction类似，只不过其中的区别是，pageAction是在满足一定的条件下才会触发的插件，在不触发的情况下会始终保持灰色。

[![](https://p3.ssl.qhimg.com/t016c38905e75a0e558.png)](https://p3.ssl.qhimg.com/t016c38905e75a0e558.png)

### contextMenus 右键菜单

通过在chrome中调用chrome.contextMenus这个API，我们可以定义在浏览器中的右键菜单。

当然，要控制这个api首先你必须申请控制contextMenus的权限。

```
`{`"permissions": ["contextMenus"]`}`
```

一般来说，这个api会在background中被定义，因为background会一直在后台加载。

```
chrome.contextMenus.create(`{`
    title: "测试右键菜单",
    onclick: function()`{`alert('您点击了右键菜单！');`}`
`}`);
```

[https://developer.chrome.com/extensions/contextMenus](https://developer.chrome.com/extensions/contextMenus)

### override – 覆盖页面

chrome提供了override用来覆盖chrome的一些特定页面。其中包括历史记录、新标签页、书签等…

```
"chrome_url_overrides":
`{`
    "newtab": "newtab.html",
    "history": "history.html",
    "bookmarks": "bookmarks.html"
`}`
```

比如Toby for Chrome就是一个覆盖新标签页的插件

### devtools – 开发者工具

chrome允许插件重构开发者工具，并且相应的操作。

[![](https://p2.ssl.qhimg.com/t0155c8cad9c1bf1370.png)](https://p2.ssl.qhimg.com/t0155c8cad9c1bf1370.png)

插件中关于devtools的生命周期和F12打开的窗口时一致的，当F12关闭时，插件也会自动结束。

而在devtools页面中，插件有权访问一组特殊的API，这组API只有devtools页面中可以访问。

```
chrome.devtools.panels：面板相关；
chrome.devtools.inspectedWindow：获取被审查窗口的有关信息；
chrome.devtools.network：获取有关网络请求的信息；
`{`
    // 只能指向一个HTML文件，不能是JS文件
    "devtools_page": "devtools.html"
`}`
```

[![](https://p4.ssl.qhimg.com/t018f3736c20f0192c8.png)](https://p4.ssl.qhimg.com/t018f3736c20f0192c8.png)

[https://developer.chrome.com/extensions/devtools](https://developer.chrome.com/extensions/devtools)

### option – 选项

option代表着插件的设置页面，当选中图标之后右键选项可以进入这个页面。

[![](https://p1.ssl.qhimg.com/t018f289f4678796751.png)](https://p1.ssl.qhimg.com/t018f289f4678796751.png)

```
`{`
    "options_ui":
    `{`
        "page": "options.html",
        "chrome_style": true
    `}`,
`}`
```

### omnibox – 搜索建议

在chrome中，如果你在地址栏输入非url时，会将内容自动传到google搜索上。

omnibox就是提供了对于这个功能的魔改，我们可以通过设置关键字触发插件，然后就可以在插件的帮助下完成搜索了。

```
`{`
    // 向地址栏注册一个关键字以提供搜索建议，只能设置一个关键字
    "omnibox": `{` "keyword" : "go" `}`,
`}`
```

这个功能通过chrome.omnibox这个api来定义。

### notifications – 提醒

notifications代表右下角弹出的提示框

```
chrome.notifications.create(null, `{`
    type: 'basic',
    iconUrl: 'img/header.jpg',
    title: 'test',
    message: 'i found you!'
`}`);
```

[![](https://p2.ssl.qhimg.com/t01b5ccefa92dccd70f.png)](https://p2.ssl.qhimg.com/t01b5ccefa92dccd70f.png)



## 权限体系和api

在了解了各类型的插件的形式之后，还有一个比较重要的就是Chrome插件相关的权限体系和api。

Chrome发展到这个时代，其相关的权限体系划分已经算是非常细致了，具体的细节可以翻阅文档。

[https://developer.chrome.com/extensions/declare_permissions](https://developer.chrome.com/extensions/declare_permissions)

抛开Chrome插件的多种表现形式不谈，插件的功能主要集中在js的代码里，而js的部分主要可以划分为5种injected script、content-script、popup js、background js和devtools js.
- injected script 是直接插入到页面中的js，和普通的js一致，不能访问任何扩展API.
- content-script 只能访问extension、runtime等几个有限的API，也可以访问dom.
- popup js 可以访问大部分API，除了devtools，支持跨域访问
- background js 可以访问大部分API，除了devtools，支持跨域访问
- devtools js 只能访问devtools、extension、runtime等部分API，可以访问dom
|JS|是否能访问DOM|是否能访问JS|是否可以跨域
|------
|injected script|可以访问|可以访问|不可以
|content script|可以访问|不可以|不可以
|popup js|不可直接访问|不可以|可以
|background js|不可直接访问|不可以|可以
|devtools js|可以访问|可以访问|不可以

同样的，针对这多种js，我们也需要特殊的方式进行调试
- injected script： 直接F12就可以调试
- content-script：在F12中console选择相应的域
[![](https://p5.ssl.qhimg.com/t01b2cee4a3e757db3c.png)](https://p5.ssl.qhimg.com/t01b2cee4a3e757db3c.png)
- popup js: 在插件右键的列表中有审查弹出内容
- background js: 需要在插件管理页面点击背景页然后调试


## 通信方式

在前面介绍过各类js之后，我们提到一个重要的问题就是，在大部分的js中，都没有给与访问js的权限，包括其中比较关键的content script.

那么插件怎么和浏览器前台以及相互之间进行通信呢？

|–|injected-script|content-script|popup-js|background-js
|------
|injected-script|–|window.postMessage|–|–
|content-script|window.postMessage|–|chrome.runtime.sendMessage chrome.runtime.connect|chrome.runtime.sendMessage chrome.runtime.connect
|popup-js|–|chrome.tabs.sendMessage chrome.tabs.connect|–|chrome.extension. getBackgroundPage()
|background-js|–|chrome.tabs.sendMessage chrome.tabs.connect|chrome.extension.getViews|–
|devtools-js|chrome.devtools.inspectedWindow.eval|–|chrome.runtime.sendMessage|chrome.runtime.sendMessage

### popup 和 background

popup和background两个域互相直接可以调用js并且访问页面的dom。

popup可以直接用chrome.extension.getBackgroundPage()获取background页面的对象，而background可以直接用chrome.extension.getViews(`{`type:’popup’`}`)获取popup页面的对象。

```
// background.js
function test()
`{`
    alert('test');
`}`

// popup.js
var bg = chrome.extension.getBackgroundPage();
bg.test(); // 访问bg的函数
alert(bg.document.body.innerHTML); // 访问bg的DOM
```

### popupbackground 和 content js

popupbackground 和 content js之间沟通的方式主要依赖chrome.tabs.sendMessage和chrome.runtime.onMessage.addListener这种有关事件监听的交流方式。

发送方使用chrome.tabs.sendMessage,接收方使用chrome.runtime.onMessage.addListener监听事件。

```
chrome.runtime.sendMessage(`{`greeting: '发送方！'`}`, function(response) `{`
    console.log('接受：' + response);
`}`);
```

接收方

```
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse)
`{`
    console.log(request, sender, sendResponse);
    sendResponse('回复：' + JSON.stringify(request));
`}`);
```

### injected script 和 content-script

由于injected script就相当于页面内执行的js，所以它没权限访问chrome对象，所以他们直接的沟通方式主要是利用window.postMessage或者通过DOM事件来实现。

injected-script中：

```
window.postMessage(`{`"test": 'test！'`}`, '*');
```

content script中：

```
window.addEventListener("message", function(e)
`{`
    console.log(e.data);
`}`, false);
```

### popupbackground 动态注入js

popupbackground没办法直接访问页面DOM，但是可以通过chrome.tabs.executeScript来执行脚本，从而实现对页面DOM的操作。

要注意这种操作要求必须有页面权限

```
"permissions": [
        "tabs", "http://*/*", "https://*/*"
    ],
```

js

```
// 动态执行JS代码
chrome.tabs.executeScript(tabId, `{`code: 'document.body.style.backgroundColor="red"'`}`);
// 动态执行JS文件
chrome.tabs.executeScript(tabId, `{`file: 'some-script.js'`}`);
```

### chrome.storage

chrome 插件还有专门的储存位置，其中包括chrome.storage和chrome.storage.sync两种，其中的区别是：
- chrome.storage 针对插件全局，在插件各个位置保存的数据都会同步。
- chrome.storage.sync 根据账户自动同步，不同的电脑登陆同一个账户都会同步。
插件想访问这个api需要提前声明storage权限。



## 总结

这篇文章主要描述了关于Chrome ext插件相关的许多入门知识，在谈及Chrome ext的安全问题之前，我们可能需要先了解一些关于Chrome ext开发的问题。

在下一篇文章中，我们将会围绕Chrome ext多个维度的安全问题进行探讨，在现代浏览器体系中，Chrome ext到底可能会带来什么样的安全问题。



## re
- [https://www.cnblogs.com/liuxianan/p/chrome-plugin-develop.html](https://www.cnblogs.com/liuxianan/p/chrome-plugin-develop.html)
- [https://developer.chrome.com/extensions/content_scripts](https://developer.chrome.com/extensions/content_scripts)
本文由 Seebug Paper 发布，如需转载请注明来源。
