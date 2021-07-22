> 原文链接: https://www.anquanke.com//post/id/238145 


# 多款浏览器WebDriver安全性分析


                                阅读量   
                                **113009**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者starlabs，文章来源：starlabs.sg
                                <br>原文地址：[https://starlabs.sg/blog/2021/04/you-talking-to-me/﻿](https://starlabs.sg/blog/2021/04/you-talking-to-me/%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t015c02217140508f66.jpg)](https://p1.ssl.qhimg.com/t015c02217140508f66.jpg)



## 0x00 WebDriver背景介绍

WebDriver是用于浏览器自动化的一种协议，可以像真实用户操作浏览器一样，驱动浏览器在网页上来执行各种测试。该协议可以用来模拟用户操作，如点击链接、输入文本以及提交表单，便于测试网站是否正常工作。WebDriver通常用于headless（无头）环境下的前端测试以及web爬虫，WebDriver客户端（如Selenium WebDriver）会与WebDriver服务端（如chromedriver、geckodriver）交互，以便启动及控制浏览器。在CTF比赛中，WebDriver客户端通常扮演受害者的角色（比如XSS bot），模拟用户交互动作，以触发XSS payload。

[![](https://p2.ssl.qhimg.com/t01d34f57d456afebf4.png)](https://p2.ssl.qhimg.com/t01d34f57d456afebf4.png)

图. python脚本使用Selenium Webdriver启动Chrome，执行`example.com`上的JavaScript

让我们以简单代码为例展示WebDriver的工作过程。在上图第4行，Selenium WebDriver客户端与chromedriver通信，启动Chrome实例，指导Chrome访问`example.com`，执行一段JavaScript代码，然后退出浏览器，结束运行。

[![](https://p0.ssl.qhimg.com/t01583bb9eca6e13e39.png)](https://p0.ssl.qhimg.com/t01583bb9eca6e13e39.png)

图. WebDriver、chromedriver及Chrome的交互过程

在这个过程中，WebDriver通过驱动（driver）将命令传递给浏览器，也通过相同的路径接收信息。驱动负责使用浏览器内置的自动化功能来控制实际的浏览器。比如，chromedriver使用`–remote-debugging-port=0`选项来启动Chrome实例，使Chrome在随机端口上启动远程调试功能，方便chromedriver进行控制。

由于浏览器厂商自己会创建大多数驱动，因此驱动和浏览器之间使用的协议可能会有所不同。基于Chrome的浏览器使用的是Chrome DevTools Protocol，默认情况下会有一些HTTP及WebSocket端点在`9222`端口上监听。Firefox使用的是自己的Marionette Protocol，通过TCP socket发送和接收JSON数据，如果没有特殊指定，默认会在`2828`端口上监听。

这些驱动必须遵循WebDriver Protocol的W3C标准，提供一致的REST API。

[![](https://p1.ssl.qhimg.com/t01f18cb68ec75c88e2.png)](https://p1.ssl.qhimg.com/t01f18cb68ec75c88e2.png)

上图显示了在手动启动的情况下，驱动/浏览器默认监听的端口。其他情况下使用WebDriver时，将采用随机端口，避免冲突。

总而言之，当我们使用WebDriver启动浏览器访问某些网页时，通常情况下localhost上将打开2个端口，其中至少1个端口承载的是用来提供REST API的HTTP服务（Safari比较特殊，它的驱动及浏览器本身在macOS上高度集成，通过XPC服务相互通信）。

为了让文章可读性更强，在下文中，“WebDriver”这个词用来指代WebDriver服务端，也就是特定于浏览器的驱动（如chromedriver、geckodriver）。



## 0x01 Chromedriver

了解基本知识后，我决定暂时不去区别这些WebDriver，先从安全性角度来看能研究多远。首先从一个非常简单的脚本开始：

[![](https://p5.ssl.qhimg.com/t01794cf36cbf9c1435.png)](https://p5.ssl.qhimg.com/t01794cf36cbf9c1435.png)

脚本中只有2个条件：

1、由WebDriver初始化的浏览器访问我们的web页面；

2、浏览器在页面上停留足够长的时间。

经过2周的努力后，我终于在Windows和Linux系统上，在Chrome（或者更确切地说，基于Chromium的浏览器，包括MS Edge及Opera）和Firefox上实现了任意文件读取和RCE。

让我们从Chrome开始。我首先检查了能否从自动化Chrome实例访问随机化端口，答案是肯定的。chromedriver REST API以及Chrome DevTools Protocol（CDP）服务端会向Chrome实例开放。

[![](https://p4.ssl.qhimg.com/t01ab7fc6b79eafd88c.png)](https://p4.ssl.qhimg.com/t01ab7fc6b79eafd88c.png)

### <a class="reference-link" name="Chrome%20DevTools%20Protocol%E6%BD%9C%E5%9C%A8%E7%9A%84%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96"></a>Chrome DevTools Protocol潜在的任意文件读取

根据[CDP文档](https://chromedevtools.github.io/devtools-protocol/)，`/json/list`端点会返回一些调试信息。如果我们能通过某种方式从这些信息中读取`webSocketDebuggerUrl`的值，那么就可以执行CDP能执行的各类操作。比如，我可以使用`Page.navigate`来访问任意URL（甚至在`file://`里的也可以），然后使用`Runtime.evaluate`来执行任意JavaScript。结合这两点，攻击者可以枚举本地目录列表，将任意文件内容提交给远程服务器。

[![](https://p5.ssl.qhimg.com/t01e7eb9d53d0399fc7.png)](https://p5.ssl.qhimg.com/t01e7eb9d53d0399fc7.png)

但我们如何才能从`http://127.0.0.1:&lt;CDP Port&gt;/json/list`读取`webSocketDebuggerUrl`呢？响应头很简单，只包含`Content-Length`以及`Content-Type: application/json; charset=UTF-8`。对于JSON而言，如果端点实现了JSONP回调功能，我们可以在任意web页面的`script`标签中加载，然后通过回调函数接收数据。我快速过了一些常见的参数，比如`callback`、`cb`以及`_callback`，但一无所获。深入分析[源码](https://source.chromium.org/chromium/chromium/src/+/master:content/browser/devtools/devtools_http_handler.cc;l=603)后，我可以确认这里并没有实现回调方法。

那么DNS重绑定（rebinding）呢？如果CDP服务端没有检查`Host`头，那么我们可以使用DNS重绑定技术来访问所有的CDP端点。我尝试将主机更改为`127.0.0.1.xip.io`域名（解析到`127.0.0.1`），然而服务端返回的响应为“Host头未指定，且不是IP地址或者localhost”。检查对应的源码后，我确定服务端会检查每个请求的Host头，但我发现无法通过DNS重绑定来绕过。

### <a class="reference-link" name="chromedriver%20REST%20API%E4%B8%AD%E7%9A%84RCE"></a>chromedriver REST API中的RCE

由于我无法对CDP采取更有效措施，我继续研究chromedriver的REST API。读取相关文档和源码后，我发现了有些有趣的端点，可能构成利用链：

1、`GET /session/`{`sessionid`}`/source`。WebDriver的W3C标准中描述过这个端点，可以返回当前活动文档的源代码。

2、`GET /sessions`。这是chromedriver自己实现的非W3C标准命令，会返回当前chromedriver进程启动的每个会话。我们可以通过该端点找到所有的``{`sessionid`}``。

3、`POST /session`。这是用来创建新会话的W3C标准命令，通过提供`goog:chromeOptions`对象，我们可以指定Chrome程序文件路径，甚至可以指定用来启动新Chrome实例的chromedriver参数。

第3个端点似乎很诱人。在`strace`的帮助下，我们很快就可以弄清楚如何通过POST请求来执行任意命令。如下图所示，我们的`-c&lt;python codes&gt;`参数会被成功解析及执行。chromedriver会附加其他一些Chrome参数，但这些参数会被Chrome程序忽略。

[![](https://p0.ssl.qhimg.com/t0170feee91104b9543.png)](https://p0.ssl.qhimg.com/t0170feee91104b9543.png)

多么简单的RCE！我们只需要扫描chromedriver的端口，然后通过表单或者JS fetch API发送POST请求即可！但很快我就发现情况没那么简单。浏览器发起的POST请求始终包含`Origin`头，表明该请求从何处发送，而chromedriver会对`Host`和`Origin`头进行安全检查。

[![](https://p1.ssl.qhimg.com/t013f5f260490625b06.png)](https://p1.ssl.qhimg.com/t013f5f260490625b06.png)

[RequestIsSafeToServe](https://source.chromium.org/chromium/chromium/src/+/master:chrome/test/chromedriver/server/http_server.cc;l=28)这个检查函数的工作流程如下：
<li>如果chromedriver没有通过`--allowed-ips`参数启动：
<ul>
- 对于所有请求，`Host`头应当通过`net::IsLocalhost`检查
- 如果存在`Origin`头，那么主机名应当通过`net::IsLocalhost`检查- 没有对GET请求检查`Host`头
<li>对于POST请求：
<ul>
- 如果`Origin`头不存在，则不检查`Host`。因此我们有可能通过浏览器发送不包含`Origin`头的POST请求。
- 如果`Origin`头的格式为`IP:port`，那么IP必须为本地IP或者`allowed_ips`列表中的IP，这种情况下不会检查`Host`头。因此，浏览器无法发送不包含`scheme://`的`Origin`头。
<li>
`Host`头以及`Origin`头的主机名部分需要通过`net::IsLocalhost`检查。</li>
### <a class="reference-link" name="DNS%E9%87%8D%E7%BB%91%E5%AE%9A%E6%9E%84%E5%BB%BA%E5%88%A9%E7%94%A8%E9%93%BE"></a>DNS重绑定构建利用链

在我们能通过浏览器发送的所有请求中，如果chromedriver使用`--allowed-ips`选项启动，那么我们就有可能使用DNS重绑定攻击绕过`RequestIsSafeToServe`。这意味着我们可以访问接受GET请求的所有chromedriver REST API，包括`GET /sessions`以及`GET /session/`{`sessionid`}`/source`。结合这些点，现在我们可以读取CDP的`/json/list`内容。

[![](https://p2.ssl.qhimg.com/t013e4103827c18b550.png)](https://p2.ssl.qhimg.com/t013e4103827c18b550.png)

上图演示了攻击者读取`webSocketDebuggerUrl`的完整过程，`9515`端口和`9222`端口只用于演示场景，实际端口为随机端口，可以通过JavaScript探测。搞定`webSocketDebuggerUrl`后，我们不仅可以读取任意文件，也可以导航至`http://127.0.0.1:&lt;open port&gt;/`，发送POST请求，触发RCE。这是因为从`RequestIsSafeToServe`的角度来看，`Host`以及`Origin`头是合法的。

### <a class="reference-link" name="%E6%BC%94%E7%A4%BA%E8%A7%86%E9%A2%91"></a>演示视频

可以参考[演示视频1](https://www.youtube.com/watch?v=6y1i6C-RAsE)及[视频2](https://www.youtube.com/watch?v=yl7tbfbIGYA)。



## 0x02 Geckodriver

研究完chromedriver后，我开始研究其他WebDriver是否存在类似漏洞。[Geckodriver](https://firefox-source-docs.mozilla.org/testing/geckodriver/)是Mozilla Firefox的WebDriver，与Chrome DevTools Protocol不同的是，并没有太多[文档](https://firefox-source-docs.mozilla.org/testing/marionette/Protocol.html#protocol)描述它用来与Firefox通信的协议。该协议名为`Marionette`，是由TCP数据承载的JSON编码文本。

[![](https://p1.ssl.qhimg.com/t01531995a46f23abf6.png)](https://p1.ssl.qhimg.com/t01531995a46f23abf6.png)

我们无法通过Firefox发送这类TCP报文，毕竟这只是个浏览器，不是pwntool。我还试了一下Marionette是否会像Redis那样忽略未识别的消息，因此我在Firefox可以发送的HTTP请求中夹带了payload，但并没有奏效。

### <a class="reference-link" name="%E5%A2%9E%E5%BC%BA%E5%9E%8BREST%20API"></a>增强型REST API

我花了点时间来测试geckodriver的REST API。不幸的是，geckodriver一次只能启动一个会话，因此我们不能从web页面启动一个新会话，更不用去想篡改Firefox程序路径来执行命令了。尽管geckodriver并没有检查`Host`头，但还是对`Origin`和`Content-Type`头实现了更为严格的检查机制。

[![](https://p5.ssl.qhimg.com/t01be3c7ec9730b6a76.png)](https://p5.ssl.qhimg.com/t01be3c7ec9730b6a76.png)

`Origin`头必须为本地地址，`Content-Type`不能被纳入CORS安全列表中。这种机制可以阻止通过DNS重绑定攻击技术发送的POST请求。对于GET请求，没有任何端点可以返回`sessionid`（chromedriver中的`GET /sessions`不是标准的W3C命令），因此我们无法利用DNS重绑定攻击。

### <a class="reference-link" name="%E5%88%86%E5%89%B2body"></a>分割body

目前为止，geckodriver以及Marionette似乎都无法被攻击。就在我准备放弃时，出现了一些意料之外的情况。我尝试过在HTTP请求中夹带Marionette命令，当我把payload字符串重复100,000次时，geckodriver记录到向Marionette发起过2次连接。

```
&lt;body&gt;
  &lt;form action="#" method="post" enctype="text/plain"&gt;
    &lt;textarea name="aaaaaa0" value=""&gt;&lt;/textarea&gt;
  &lt;/form&gt;
    &lt;script&gt;
        let params = new URL(location.href).searchParams,

        port = 1 * params.get('port')

        document.forms[0].action = `http://127.0.0.1:$`{`port`}`/`

        document.forms[0].aaaaaa0.value = '54:[0,1,"WebDriver:NewSession",`{`"browserName":"firefox"`}`]55:[0,2,"WebDriver:Navigate",`{`"url":"http://example.com"`}`]'.repeat(100000)

        document.forms[0].submit()
  &lt;/script&gt;
&lt;/body&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010fe674f82673fdc9.png)

第1个连接很正常，这是我们发起的POST请求。由于该请求无法解析成Marionette的命令格式长度：`[type, message ID, command, parameters]`，因此会抛出一个错误。但第2个连接来自何处呢？为什么报文会在我们重复payload字符串操作的中间出现？我第一时间打开Wireshark，观察具体情况。事实证明，Firefox会为我们的POST请求创建2个TCP连接，第1个连接只包含32KB的HTTP请求body，第2个请求用来发送剩余部分，并且不包含任何HTTP头！

[![](https://p0.ssl.qhimg.com/t01c34213031962377a.png)](https://p0.ssl.qhimg.com/t01c34213031962377a.png)

一开始我认为这是我不熟悉的一些浏览器背景知识，比如会将大型HTTP请求body拆分成独立的TCP连接，然而事实并非如此。经过一些测试后，只有Firefox存在这种行为，因此这个bug很可能威力巨大，可以允许攻击者从受害者浏览器发送任意TCP报文，只需要访问恶意web页面即可。

[![](https://p5.ssl.qhimg.com/t01d25ee0e5ea7b4c76.png)](https://p5.ssl.qhimg.com/t01d25ee0e5ea7b4c76.png)

在发送文本数据时，我们可以通过`text/plain`格式来轻松设置32KB偏移，当我们针对Redis服务端进行测试时，一切工作非常完美。由于第1个报文没有以“POST”字符串作为开头，因此Redis服务端会丢弃该报文，并且Redis有针对这类请求的保护机制。Redis会接收第2个报文中的payload。如果我们想发送二进制数据，可以选择`multipart/form-data`。尽管随机生成的`boundary`字符串可能会对偏移值计算造成影响，但还是可以通过多次尝试来暴力枚举。

### <a class="reference-link" name="%E5%AE%9E%E7%8E%B0RCE"></a>实现RCE

具备发送Marionette命令的能力后，我们可以使用之前在chromedriver中用过的相同技术，通过Firefox来读取文件。那么RCE呢？在Google上搜索Firefox RCE时我找到了一篇[文章](https://frederik-braun.com/firefox-ui-xss-leading-to-rce.html)，很快我就了解到，Firefox在“chrome特权文档”中提供了一个内置的JS子流程模块。我们只需要导航至`hrome://`文档，执行一行JavaScript代码即可。

[![](https://p1.ssl.qhimg.com/t015e5944170e9ff1a5.png)](https://p1.ssl.qhimg.com/t015e5944170e9ff1a5.png)

### <a class="reference-link" name="%E6%BC%94%E7%A4%BA%E8%A7%86%E9%A2%91"></a>演示视频

参考[RCE on Linux (Firefox 86.0.1)](https://www.youtube.com/watch?v=ZzGqr5LOJhk)及[RCE on Windows (Firefox 86.0.1)](https://www.youtube.com/watch?v=lMZZOQ0HV08)这两个视频。



## 0x03 其他WebDriver

由于MS Edge及Opera都是基于Chromium的浏览器，它们的驱动都源自于chromedriver。稍加修改后，前面适用于chromedriver的payload同样适用于这两个浏览器。对于safaridriver，由于该浏览器会严格检查`Host`及`Origin`头，因此我们认为它不容易受类似攻击影响。



## 0x04 总结

DNS重绑定攻击自问世到现在已经14年，时至今日，这项技术依然在漏洞利用链中占有一席之地。通常情况下，只在本地地址上监听的HTTP服务更容易受DNS重绑定攻击影响。我们呼吁开发者在处理传入的请求时，要验证`Host`及`Origin`头。正确的验证流程可以避免攻击者通过访问恶意站点来攻击本地HTTP服务。



## 0x05 时间线

23/03/2021 Firefox 87.0发布，修复TCP连接拆分bug

05/04/2021 向Google反馈ChromeDriver特权提升问题

08/04/2021 问题报告被标记为与未解决的issue #3389重复

12/04/2021 本文发布



## 0x06 参考资料

[https://labs.detectify.com/2017/10/06/guest-blog-dont-leave-your-grid-wide-open/](https://labs.detectify.com/2017/10/06/guest-blog-dont-leave-your-grid-wide-open/)

[https://bluec0re.blogspot.com/2018/03/cve-2018-7160-pwning-nodejs-developers.html](https://bluec0re.blogspot.com/2018/03/cve-2018-7160-pwning-nodejs-developers.html)

[https://bugs.chromium.org/p/project-zero/issues/detail?id=1471](https://bugs.chromium.org/p/project-zero/issues/detail?id=1471)

加成券.JPG
