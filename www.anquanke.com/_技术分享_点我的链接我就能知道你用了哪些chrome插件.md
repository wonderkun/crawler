> 原文链接: https://www.anquanke.com//post/id/85314 


# 【技术分享】点我的链接我就能知道你用了哪些chrome插件


                                阅读量   
                                **119192**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t016a55361b4c21d7d3.webp)](https://p5.ssl.qhimg.com/t016a55361b4c21d7d3.webp)

咳咳，我知道干货一般阅读量会比较低，所以我借用了安全圈段子讲的最好的人惯用的漏洞标题风格。

由YSRC安全研究员evi1m0和neargle挖掘并编写poc，测试链接在文末。需要指出的是这是一个p(标)o(题)c(党)，探测不全是正常的，本身就有很多插件不可以利用文中的方式探测，要不然就变成发chrome的0day了~

<br>

**0x01 About**

编写过 Chrome 扩展的开发人员都应该清楚在 crx 后缀的包中， manifest.json 配置清单文件提供了这个扩展的重要信息，crx 后缀文件可以直接使用 unzip 解压，Windows 下的安装后解压的路径在：C:UsersAdministratorAppDataLocalGoogleChromeUser DataDefaultExtensions ，MacOS 在：cd ~/Library/Application Support/Google/Chrome/Default/Extensions ，其中 manifest.json 的样例：

```
➜  0.7.0_0 cat manifest.json
```

```
`{`
  "background": `{`
    "scripts": [ "background.js" ]
  `}`,
  "content_scripts": [ `{`
    "all_frames": true,
    "js": [ "content.js" ],
    "matches": [ "http://*/*", "https://*/*", "ftp://*/*", "file:///*" ],
    "run_at": "document_end"
  `}` ],
  "description": "Validates and makes JSON documents easy to read. Open source.",
  "homepage_url": "https://github.com/teocci/JSONView-for-Chrome",
  "icons": `{`
    "128": "assets/images/jsonview128.png",
    "16": "assets/images/jsonview16.png",
    "48": "assets/images/jsonview48.png"
  `}`,
  "key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApA/pG/flimvWWAeUelHGaQ+IJajQm01JkfK0EYOJPyfsdTkHLwD3Aw16N3zuFkmwz09DcGDT+ehww7GSpW7RpbX5kHrovsqyHXtwt+a2Sp8bYFFdpRPj3+HG6366kNkwttDHMtsDkwuKaBtrQofQe5Ud9mKu9h1FDPwc2Qql9vNtvOqKFhV+EOD0vD2QlliB6sKCteu4nYBlFEkh6pYWRaXdAYSKYdE1SYIuQzE3dk11+KCaAC1T6GffL3sia8n5brVX7Qd+XtXyBzuM54w5e3STwK7uLMhLGDIzHoTcldzWUUflfwuI86VQIFBxPbvXJKqFFFno+ZHs/S+Ra2SPmQIDAQAB",
  "manifest_version": 2,
  "minimum_chrome_version": "21",
  "name": "JSON Viewer",
  "permissions": [ "clipboardWrite", "http://*/", "contextMenus", "https://*/", "ftp://*/" ],
  "short_name": "JSONViewer",
  "update_url": "https://clients2.google.com/service/update2/crx",
  "version": "0.7.0",
  "web_accessible_resources": [ "assets/options.html", "assets/csseditor.html", "assets/css/jsonview.css", "assets/css/jsonview-core.css", "assets/css/content_error.css", "assets/images/options.png", "assets/images/close_icon.gif", "assets/images/error.gif" ]
`}`
```

可以看到关于这个扩展的 content_scripts, desc, homepage, icons 等等配置信息，其中 manifest_version 字段标明现在的 rule 为 2.0 版本，在 2012 年 Chrome 便将 1.0 manifest.json 配置版本的扩展禁止新建在应用市场中，但允许更新，直到 2014 年彻底禁用所有的 version 1.0 版本扩展/应用并更新至 2.0，其中一大部分原因是由于新版规则上安全性的提升。

<br>

**0x02 Manifest**

2.0 中关于 CSP 的强制应用，要求开发者配置 content_security_policy ，如果未设置的话则使用 Chrome 的默认 manifest csp 规则；

不同于老版本的规则，crx 下的资源文件不再是默认可用（直接访问）的图像、资源、脚本。如果想让网站能够加载其资源就必须配置 web_accessible_resources 清单；

删除 chrome.self API ，使用 chrome.extension 替代；

…

<br>

**0x03 script &lt;–&gt; onload / onerror**

在多年前的 ChromeExtensions 探测中我们可以直接探测静态资源文件来判断是否存在，在上面的更新变动中可以看到，如果访问资源则必须在 web_accessible_resources 中声明 LIST （可以使用通配符），拿 json-view 举例：

```
"web_accessible_resources": [ "assets/options.html", "assets/csseditor.html", "assets/css/jsonview.css", "assets/css/jsonview-core.css", "assets/css/content_error.css", "assets/images/options.png", "assets/images/close_icon.gif", "assets/images/error.gif" ]
```

访问他们资源的 URL 格式如下：

```
'chrome-extension://' + id + web_accessible_resources
```

在测试的过程中我们发现大量的扩展禁止了 iframe 内嵌访问，这里我们可以使用 script 加载页面的差异化来判断是否存在文件：

```
&lt;script src="chrome-extension://aimiinbnnkboelefkjlenlgimcabobli/assets/options.html" onload="('json-view!')" onerror="(':(')"&gt;&lt;/script&gt;
```

<br>

**0x04 Chrome Extensions Spider**

我们编写了爬虫获取整个[谷歌商店](https://chrome.google.com/webstore/category/extensions?hl=en-US)中的扩展应用（id, name, starts, users, category, url），分类如下：

```
'ext/10-blogging',
  'ext/15-by-google',
  'ext/12-shopping',
  'ext/11-web-development',
  'ext/1-communication',
  'ext/7-productivity',
  'ext/38-search-tools',
  'ext/13-sports',
  'ext/22-accessibility',
  'ext/6-news',
  'ext/14-fun',
  'ext/28-photos'
```

截至 2017年初 谷歌商店扩展应用总数量为 42658 ，我们将这些 crx 全部进行下载分析其 manifest.json 的编写规则，发现 12032 个扩展可以探测，在之后的实际测试过程中也发现探测应用的成功率为 1/3 ~ 1/4 ，比较客观，保存的 JSON 格式如下：

```
`{`
  "web_accessible_resources": [
    "19.png",
    "48.png",
    "i/4000.png"
  ],
  "name": "Facepad for Facebooku2122",
  "stars": 497,
  "id": "cgaknhmchnjaphondjciheacngggiclo",
  "url": "https://chrome.google.com/webstore/detail/facepad-for-facebook/cgaknhmchnjaphondjciheacngggiclo",
  "category": "ext/10-blogging",
  "users": "11,686"
`}`,
`{`"web_accessible_resources": ["reload.js"], "name": "Refresh for Twitter", "stars": 184, "id": "hdpiilkeoldobfomlhipnnfanmgfllmp", "url": "https://chrome.google.com/webstore/detail/refresh-for-twitter/hdpiilkeoldobfomlhipnnfanmgfllmp", "category": "ext/10-blogging", "users": "31,796"
`}`,
`{`
"web_accessible_resources": ["main.css", "lstr.js", "script.js", "images/close.png", "images/back.png", "images/icon19.png", "images/play.png", "images/stop.png", "images/prev.png", "images/down.png", "images/next.png", "images/delete.png", "classes/GIFWorker.js"], "name": "MakeGIF Video Capture", "stars": 309, "id": "cnhdjbfjheoohmhpakglckehdcgfffbl", "url": "https://chrome.google.com/webstore/detail/makegif-video-capture/cnhdjbfjheoohmhpakglckehdcgfffbl", "category": "ext/10-blogging", "users": "55,360"
`}`,
`{`
"web_accessible_resources": ["js/move.js"], "name": "Postagens Megafilmes 2.1", "stars": 0, "id": "ekennogbnkdbgejohplipgcneekoaanp", "url": "https://chrome.google.com/webstore/detail/postagens-megafilmes-21/ekennogbnkdbgejohplipgcneekoaanp", "category": "ext/10-blogging", "users": "2,408"
`}`,
...
```

<br>

**0x05 ProbeJS**

通过编写脚本可以加载并探测本地扩展是否存在，虽然需要触发大量的请求来探测，但由于是访问本地资源其速度仍然可以接受，我们过滤出 users 1000 以上的扩展来进行筛选探测（ testing 函数动态创建并删除不成功的 dom 探测节点）：

```
https://sec.ly.com/poc/ext_probe.html
 // json data parse
$.get("ext1000up.json" + "?_=" + new Date().valueOf(), function(ext)`{`
    for (let n in ext.data) `{`
        var id = ext.data[n].id;
        var name = ext.data[n].name;
        var war = ext.data[n].web_accessible_resources;
        var curl = ext.data[n].url;
        testing(id, name, war, curl);
    `}`
    $('#loading').remove();
`}`)
...
```

[![](https://p0.ssl.qhimg.com/t01682c0664ee56837f.webp)](https://p0.ssl.qhimg.com/t01682c0664ee56837f.webp)

搜索“同程安全”或者扫描下方二维码关注YSRC公众号，招各种安全岗，欢迎推荐。

[![](https://p4.ssl.qhimg.com/t0184e3939b55d173b7.jpg)](https://p4.ssl.qhimg.com/t0184e3939b55d173b7.jpg)
