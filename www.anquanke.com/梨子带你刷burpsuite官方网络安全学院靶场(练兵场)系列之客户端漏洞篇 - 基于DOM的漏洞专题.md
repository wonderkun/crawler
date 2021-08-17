> 原文链接: https://www.anquanke.com//post/id/246090 


# 梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之客户端漏洞篇 - 基于DOM的漏洞专题


                                阅读量   
                                **38943**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t012178213768346220.jpg)](https://p5.ssl.qhimg.com/t012178213768346220.jpg)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 客户端漏洞篇介绍

> 相对于服务器端漏洞篇，客户端漏洞篇会更加复杂，需要在我们之前学过的服务器篇的基础上去利用。



## 客户端漏洞篇 – 基于DOM的漏洞专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFDOM%EF%BC%9F"></a>什么是DOM？

DOM，全称document object model，译为文档对象模型。是浏览器对页面元素的分层表示。网站可以使用JS操作DOM的节点和对象以及它们的属性。在DOM的概念中有两个专有名词source和sink，目前梨子还找不到合适的中文翻译。我们暂且理解为DOM操作的入口点和出口点。如果当不安全的payload从入口点传递给出口点则可能存在基于DOM的漏洞。

### <a class="reference-link" name="source"></a>source

source是一个JS属性，可以接收用户输入。比如location.search，它可以从查询字符串中获取数据，这也是攻击者比较容易利用的点。还有其他的也是容易被攻击者控制的source，例如document.referrer、document.cookie还有Web消息等。

### <a class="reference-link" name="sink"></a>sink

既然source是接收用户输入，那么sink就是使用危险的方式处理source的函数或DOM对象。比如eval()就是一种sink，可以处理JS传递给它的参数值。还有一种sink是document.body.innerHTML，攻击者可以向其注入恶意的HTML和JS脚本并执行。

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E6%B1%A1%E7%82%B9%E6%B5%81(Taint-flow)%EF%BC%9F"></a>什么是污点流(Taint-flow)？

当网站将数据从source传递给sink，然后sink以不安全的方式处理该数据，则可能出现基于DOM的漏洞。危险的数据由source流向sink，所以叫做污点流(Taint-flow)。最常见的source就是URL，通常使用location对象访问。攻击者可以构造一个链接，然后让受害者跳转到指定的页面。例如

```
goto = location.hash.slice(1)
if (goto.startsWith('https:')) `{`
  location = goto;
`}`
```

上面这段代码会检查URL，如果包含以https开头的哈希片段则提取location.hash属性的值并将其设置为window对象的location属性。所以攻击者可以构造这样的URL来利用这个基于DOM的开放重定向漏洞。<br>`https://www.innocent-website.com/example#https://www.evil-user.net`<br>
经过上面那段代码处理以后，会将[https://www.evil-user.net](https://www.evil-user.net) 设置为location属性的值，这会自动将受害者重定向到该站点。一般可以用于钓鱼攻击。

### <a class="reference-link" name="%E5%B8%B8%E8%A7%81%E7%9A%84source"></a>常见的source

下面列出一些常见的可能触发污点流(Taint-flow)漏洞的source
- document.URL
- document.documentURI
- document.URLUnencoded
- document.baseURI
- location
- document.cookie
- document.referrer
- window.name
- history.pushState
- history.replaceState
- localStorage
- sessionStorage
- IndexedDB (mozIndexedDB, webkitIndexedDB, msIndexedDB)
- Database
下面几种数据也是可能触发污点流(Taint-flow)漏洞的source
- 反射型数据(已在XSS专题中讲解)
- 存储型数据(已在XSS专题中讲解)
- Web消息
### <a class="reference-link" name="%E4%BB%A5Web%E6%B6%88%E6%81%AF%E4%B8%BAsource%E7%9A%84%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%BC%8F%E6%B4%9E"></a>以Web消息为source的基于DOM的漏洞

如果网站以不安全的方式传递Web消息，例如，未在事件侦听器中正确验证传入的Web消息的源，则事件侦听器调用的属性和函数可能会成为sink。攻击者可以托管恶意iframe并使用postMessage()方法将Web消息数据传递给事件监听器，然后将payload发送到父页面上的sink。这就以为着攻击者可以以Web消息为source将恶意数据传递到这些所有的sink。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E4%BB%A5Web%E6%B6%88%E6%81%AF%E4%B8%BAsource%E6%9E%84%E9%80%A0%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何以Web消息为source构造攻击？

首先我们考虑这样的代码

```
&lt;script&gt;
window.addEventListener('message', function(e) `{`
  eval(e.data);
`}`);
&lt;/script&gt;
```

这段代码添加了一个事件监听器，在接收到消息时执行里面的data部分。这里我们通过iframe注入这个消息<br>`&lt;iframe src="//vulnerable-website" onload="this.contentWindow.postMessage('alert(1)','*')"&gt;`<br>
因为事件监听器不验证消息的源，并且postMessage也指定了targetOrigin “*”，所以事件监听器会接收它并且将payload传递到sink(eval())中执行。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E4%BD%BF%E7%94%A8Web%E6%B6%88%E6%81%AF%E7%9A%84DOM%20XSS"></a>配套靶场1：使用Web消息的DOM XSS

我们留意到页面中有这样的代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ccc97b029bc05e27.png)

我们看到这段代码与上面的还是有点区别的，这里有innerHTML，所以应该使用img搭配onerror这一款XSS payload

[![](https://p1.ssl.qhimg.com/t0178a3b922e4262a7a.png)](https://p1.ssl.qhimg.com/t0178a3b922e4262a7a.png)

经过代码处理以后就会触发XSS

[![](https://p1.ssl.qhimg.com/t012a476f050301a7e7.png)](https://p1.ssl.qhimg.com/t012a476f050301a7e7.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E4%BD%BF%E7%94%A8Web%E6%B6%88%E6%81%AF%E5%92%8CJS%20URL%E7%9A%84DOM%20XSS"></a>配套靶场2：使用Web消息和JS URL的DOM XSS

我们注意到这样的代码

[![](https://p3.ssl.qhimg.com/t0137d0ef25949634b6.png)](https://p3.ssl.qhimg.com/t0137d0ef25949634b6.png)

这段代码就是在Web消息中检测是否有http或https字样，如果有，就将其赋给location.href属性，看到href，我们就知道是要用JS伪协议去触发XSS了

[![](https://p3.ssl.qhimg.com/t0140f9047c19a3570d.png)](https://p3.ssl.qhimg.com/t0140f9047c19a3570d.png)

经过上面代码处理以后就会触发XSS了

[![](https://p2.ssl.qhimg.com/t01d9ddc8eb1a031660.png)](https://p2.ssl.qhimg.com/t01d9ddc8eb1a031660.png)

### <a class="reference-link" name="%E6%BA%90%E9%AA%8C%E8%AF%81"></a>源验证

即使事件监听器会验证源，也会在验证过程中发现一些缺陷。例如

```
window.addEventListener('message', function(e) `{`
  if (e.origin.indexOf('normal-website.com') &gt; -1) `{`
    eval(e.data);
  `}`
`}`);
```

这种验证方式有很大缺陷，因为它只检查是否包含指定的域，但是并没有检查是否还包含其他的，例如<br>`http://www.normal-website.com.evil.net`<br>
类似这种URL就可以轻松绕过。这种验证缺陷也会出现在使用startsWith()和endsWith()函数的情况中。例如

```
window.addEventListener('message', function(e) `{`
  if (e.origin.endsWith('normal-website.com')) `{`
    eval(e.data);
  `}`
`}`);
```

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8Web%E6%B6%88%E6%81%AF%E5%92%8CJSON.parse%E7%9A%84DOM%20XSS"></a>配套靶场：使用Web消息和JSON.parse的DOM XSS

我们可以看到这样的代码

[![](https://p4.ssl.qhimg.com/t018b112b7e4dcc4533.png)](https://p4.ssl.qhimg.com/t018b112b7e4dcc4533.png)

从上面代码得知代码会首先创建一个iframe元素，然后利用JSON.parse解析Web消息，然后根据其中的type字段的值有三种不同的处理方式，为了触发DOM XSS，我们需要进入第二种处理方式，所以我们构造这样的payload

[![](https://p2.ssl.qhimg.com/t0165d34053fca83e0a.png)](https://p2.ssl.qhimg.com/t0165d34053fca83e0a.png)

经过代码处理以后就会触发XSS了

[![](https://p2.ssl.qhimg.com/t01f82300fbb2b9bf69.png)](https://p2.ssl.qhimg.com/t01f82300fbb2b9bf69.png)

### <a class="reference-link" name="%E9%82%A3%E4%BA%9Bsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>那些sink可以导致基于DOM的漏洞？

burp列举出一些可以导致基于DOM漏洞的sink

<th style="text-align: center;">基于DOM的漏洞类型</th><th style="text-align: center;">sink</th>
|------
<td style="text-align: center;">DOM XSS(已在XSS专题中讲解)</td><td style="text-align: center;">document.write()</td>
<td style="text-align: center;">开放重定向</td><td style="text-align: center;">window.location</td>
<td style="text-align: center;">操纵cookie</td><td style="text-align: center;">document.cookie</td>
<td style="text-align: center;">JS注入</td><td style="text-align: center;">eval()</td>
<td style="text-align: center;">操纵文档域</td><td style="text-align: center;">document.domain</td>
<td style="text-align: center;">WebSocket-URL投毒</td><td style="text-align: center;">WebSocket()</td>
<td style="text-align: center;">操纵链接</td><td style="text-align: center;">element.src</td>
<td style="text-align: center;">操纵Web消息</td><td style="text-align: center;">postMessage()</td>
<td style="text-align: center;">操纵Ajax请求头</td><td style="text-align: center;">setRequestHeader()</td>
<td style="text-align: center;">操纵本地文件路径</td><td style="text-align: center;">FileReader.readAsText()</td>
<td style="text-align: center;">客户端SQL注入</td><td style="text-align: center;">ExecuteSql()</td>
<td style="text-align: center;">操纵HTML5存储</td><td style="text-align: center;">sessionStorage.setItem()</td>
<td style="text-align: center;">客户端XPath注入</td><td style="text-align: center;">document.evaluate()</td>
<td style="text-align: center;">客户端JSON注入</td><td style="text-align: center;">JSON.parse()</td>
<td style="text-align: center;">操纵DOM数据</td><td style="text-align: center;">element.setAttribute()</td>
<td style="text-align: center;">拒绝服务</td><td style="text-align: center;">RegExp()</td>

下面我们一个一个地介绍

### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E5%BC%80%E6%94%BE%E9%87%8D%E5%AE%9A%E5%90%91"></a>基于DOM的开放重定向

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E5%BC%80%E6%94%BE%E9%87%8D%E5%AE%9A%E5%90%91%EF%BC%9F"></a>什么是基于DOM的开放重定向？

基于DOM的开放重定向就是将输入传递给可以触发跨域跳转的sink时触发的漏洞。例如下面代码以不安全方式处理location.hash

```
let url = /https?:\/\/.+/.exec(location.hash);
if (url) `{`
  location = url[0];
`}`
```

它可以触发跳转到任意域。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E5%BC%80%E6%94%BE%E9%87%8D%E5%AE%9A%E5%90%91"></a>配套靶场：基于DOM的开放重定向

我们在任意文章页面发现这样的代码

[![](https://p0.ssl.qhimg.com/t01a8fce4efe1d6dae4.png)](https://p0.ssl.qhimg.com/t01a8fce4efe1d6dae4.png)

这段代码会检测当前请求URL中是否包含url=http(s)开头的字符串，如果包含则将URL赋给location.href属性，于是我们可以这样构造开放重定向的payload

[![](https://p2.ssl.qhimg.com/t019446e53b121aec68.png)](https://p2.ssl.qhimg.com/t019446e53b121aec68.png)

这样当点击返回首页时就会触发开放重定向跳转到url参数指定的页面

[![](https://p0.ssl.qhimg.com/t018c743056f6377f4a.png)](https://p0.ssl.qhimg.com/t018c743056f6377f4a.png)

### <a class="reference-link" name="%E5%93%AA%E4%BA%9Bsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E5%BC%80%E6%94%BE%E9%87%8D%E5%AE%9A%E5%90%91%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪些sink可以导致基于DOM的开放重定向漏洞？
- location
- location.host
- location.hostname
- location.href
- location.pathname
- location.search
- location.protocol
- location.assign()
- location.replace()
- open()
- element.srcdoc
- XMLHttpRequest.open()
- XMLHttpRequest.send()
- jQuery.ajax()
- $.ajax()
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5cookie"></a>基于DOM的操纵cookie

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5cookie%EF%BC%9F"></a>什么是基于DOM的操纵cookie？

burp的原话感觉比较啰嗦，通俗来讲，就是利用DOM函数，如document.cookie向cookie注入恶意数据。例如

```
document.cookie = 'cookieName='+location.hash.slice(1);
```

下面我们通过一道靶场来看看是如何操纵cookie

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5cookie"></a>配套靶场：基于DOM的操纵cookie

我们发现了这样一段代码

[![](https://p3.ssl.qhimg.com/t0168b80283470305fe.png)](https://p3.ssl.qhimg.com/t0168b80283470305fe.png)

发现存在一个DOM操作，得知cookie由一个参数lastViewProduct构成，其值是window.location，即当前窗口的完整的URL，所以我们这样构造payload

[![](https://p0.ssl.qhimg.com/t015ceef7efa2c20829.png)](https://p0.ssl.qhimg.com/t015ceef7efa2c20829.png)

这样当构造cookie时就会注入JS脚本进去，为了不被受害者发现，在加载时会立即跳转到首页。

[![](https://p5.ssl.qhimg.com/t013c1a83dc75efd27e.png)](https://p5.ssl.qhimg.com/t013c1a83dc75efd27e.png)

### <a class="reference-link" name="%E5%93%AA%E4%B8%AAsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5cookie%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪个sink可以导致基于DOM的操纵cookie漏洞？
- document.cookie
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84JS%E6%B3%A8%E5%85%A5"></a>基于DOM的JS注入

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84JS%E6%B3%A8%E5%85%A5%EF%BC%9F"></a>什么是基于DOM的JS注入？

JS注入就是用户输入可以被当成一个JS脚本执行

### <a class="reference-link" name="%E5%93%AA%E4%BA%9Bsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84JS%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪些sink可以导致基于DOM的JS注入漏洞？
- eval()
- Function()
- setTimeout()
- setInterval()
- setImmediate()
- execCommand()
- execScript()
- msSetImmediate()
- range.createContextualFragment()
- crypto.generateCRMFRequest()
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5%E6%96%87%E6%A1%A3%E5%9F%9F"></a>基于DOM的操纵文档域

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5%E6%96%87%E6%A1%A3%E5%9F%9F%EF%BC%9F"></a>什么是基于DOM的操纵文档域？

当浏览器采用同源策略时会使用document.domain属性，如果两个站点的值是相同的则会被认为是同源，就可以不受限制地互相访问资源，从而发动跨域攻击。

### <a class="reference-link" name="%E5%93%AA%E4%B8%AAsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5%E6%96%87%E6%A1%A3%E5%9F%9F%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪个sink可以导致基于DOM的操纵文档域漏洞？
- document.domain
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84WebSocket-URL%E6%8A%95%E6%AF%92"></a>基于DOM的WebSocket-URL投毒

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84WebSocket-URL%E6%8A%95%E6%AF%92%EF%BC%9F"></a>什么是基于DOM的WebSocket-URL投毒？

就是把用户输入作为一个WebSocket连接的目标URL并发出请求。

### <a class="reference-link" name="%E5%93%AA%E4%B8%AAsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84WebSocket-URL%E6%8A%95%E6%AF%92%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪个sink可以导致基于DOM的WebSocket-URL投毒漏洞？
- WebSocket构造器
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5%E9%93%BE%E6%8E%A5"></a>基于DOM的操纵链接

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5%E9%93%BE%E6%8E%A5%EF%BC%9F"></a>什么是基于DOM的操纵链接？

就是在当前页面将用户输入的数据写入一个跳转目标中

### <a class="reference-link" name="%E5%93%AA%E4%BA%9Bsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5%E9%93%BE%E6%8E%A5%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪些sink可以导致基于DOM的操纵链接漏洞？
- someDOMElement.href
- someDOMElement.src
- someDOMElement.action
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5Web%E6%B6%88%E6%81%AF"></a>基于DOM的操纵Web消息

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5Web%E6%B6%88%E6%81%AF%EF%BC%9F"></a>什么是基于DOM的操纵Web消息？

就是将用户输入作为Web消息传递给一个文档中，当用户访问时发出恶意请求。

### <a class="reference-link" name="%E5%93%AA%E4%B8%AAsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5Web%E6%B6%88%E6%81%AF%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪个sink可以导致基于DOM的操纵Web消息漏洞？
- postMessage()
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5Ajax%E8%AF%B7%E6%B1%82%E5%A4%B4"></a>基于DOM的操纵Ajax请求头

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5Ajax%E8%AF%B7%E6%B1%82%E5%A4%B4%EF%BC%9F"></a>什么是基于DOM的操纵Ajax请求头？

就是将用户输入写入一个使用XmlHttpRequest对象发出ajax的请求的请求头中

### <a class="reference-link" name="%E5%93%AA%E4%BA%9Bsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5Ajax%E8%AF%B7%E6%B1%82%E5%A4%B4%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪些sink可以导致基于DOM的操纵Ajax请求头漏洞？
- XMLHttpRequest.setRequestHeader()
- XMLHttpRequest.open()
- XMLHttpRequest.send()
- jQuery.globalEval()
- $.globalEval()
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5%E6%9C%AC%E5%9C%B0%E6%96%87%E4%BB%B6%E8%B7%AF%E5%BE%84"></a>基于DOM的操纵本地文件路径

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5%E6%9C%AC%E5%9C%B0%E6%96%87%E4%BB%B6%E8%B7%AF%E5%BE%84%EF%BC%9F"></a>什么是基于DOM的操纵本地文件路径？

就是将用户输入作为一个filename参数传递到一个文件处理API中

### <a class="reference-link" name="%E5%93%AA%E4%BA%9Bsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5%E6%9C%AC%E5%9C%B0%E6%96%87%E4%BB%B6%E8%B7%AF%E5%BE%84%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪些sink可以导致基于DOM的操纵本地文件路径漏洞？
- FileReader.readAsArrayBuffer()
- FileReader.readAsBinaryString()
- FileReader.readAsDataURL()
- FileReader.readAsText()
- FileReader.readAsFile()
- FileReader.root.getFile()
- FileReader.root.getFile()
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E5%AE%A2%E6%88%B7%E7%AB%AFSQL%E6%B3%A8%E5%85%A5"></a>基于DOM的客户端SQL注入

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E5%AE%A2%E6%88%B7%E7%AB%AFSQL%E6%B3%A8%E5%85%A5%EF%BC%9F"></a>什么是基于DOM的客户端SQL注入？

就是以一种不安全的方式把用户输入拼接到一个客户端的sql查询语句中，然后获取意外的结果。

### <a class="reference-link" name="%E5%93%AA%E4%B8%AAsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E5%AE%A2%E6%88%B7%E7%AB%AFSQL%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪个sink可以导致基于DOM的客户端SQL注入漏洞？
- executeSql()
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5HTML5%E5%AD%98%E5%82%A8"></a>基于DOM的操纵HTML5存储

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5HTML5%E5%AD%98%E5%82%A8%EF%BC%9F"></a>什么是基于DOM的操纵HTML5存储？

就是把用户输入存储到浏览器的H5存储中

### <a class="reference-link" name="%E5%93%AA%E4%BA%9Bsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5HTML5%E5%AD%98%E5%82%A8%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪些sink可以导致基于DOM的操纵HTML5存储漏洞？
- sessionStorage.setItem()
- localStorage.setItem()
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E5%AE%A2%E6%88%B7%E7%AB%AFXPath%E6%B3%A8%E5%85%A5"></a>基于DOM的客户端XPath注入

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E5%AE%A2%E6%88%B7%E7%AB%AFXPath%E6%B3%A8%E5%85%A5%EF%BC%9F"></a>什么是基于DOM的客户端XPath注入？

就是将用户输入拼接到一个XPath查询语句中，与前面的客户端Sql注入类似。

### <a class="reference-link" name="%E5%93%AA%E4%BA%9Bsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E5%AE%A2%E6%88%B7%E7%AB%AFXPath%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪些sink可以导致基于DOM的客户端XPath注入漏洞？
- document.evaluate()
- someDOMElement.evaluate()
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E5%AE%A2%E6%88%B7%E7%AB%AFJSON%E6%B3%A8%E5%85%A5"></a>基于DOM的客户端JSON注入

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E5%AE%A2%E6%88%B7%E7%AB%AFJSON%E6%B3%A8%E5%85%A5%EF%BC%9F"></a>什么是基于DOM的客户端JSON注入？

就是将用户输入拼接到一个可被解析为json数据结构并由应用程序处理的字符串中，然后构造异常的解析结果。

### <a class="reference-link" name="%E5%93%AA%E4%BA%9Bsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E5%AE%A2%E6%88%B7%E7%AB%AFJSON%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪些sink可以导致基于DOM的客户端JSON注入漏洞？
- JSON.parse()
- jQuery.parseJSON()
- $.parseJSON()
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5DOM%E6%95%B0%E6%8D%AE"></a>基于DOM的操纵DOM数据

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5DOM%E6%95%B0%E6%8D%AE%EF%BC%9F"></a>什么是基于DOM的操纵DOM数据？

就是将用户输入写入一个使用透明UI或客户端逻辑的DOM区域然后执行异常的DOM操作。

### <a class="reference-link" name="%E5%93%AA%E4%BA%9Bsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%93%8D%E7%BA%B5DOM%E6%95%B0%E6%8D%AE%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪些sink可以导致基于DOM的操纵DOM数据漏洞？
- scriptElement.src
- scriptElement.text
- scriptElement.textContent
- scriptElement.innerText
- someDOMElement.setAttribute()
- someDOMElement.search
- someDOMElement.text
- someDOMElement.textContent
- someDOMElement.innerText
- someDOMElement.outerText
- someDOMElement.value
- someDOMElement.name
- someDOMElement.target
- someDOMElement.method
- someDOMElement.type
- someDOMElement.backgroundImage
- someDOMElement.cssText
- someDOMElement.codebase
- document.title
- document.implementation.createHTMLDocument()
- history.pushState()
- history.replaceState()
### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%8B%92%E7%BB%9D%E6%9C%8D%E5%8A%A1"></a>基于DOM的拒绝服务

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%8B%92%E7%BB%9D%E6%9C%8D%E5%8A%A1%EF%BC%9F"></a>什么是基于DOM的拒绝服务？

就是将用户输入以不安全的方式传入一个有可能会消耗大量计算资源的API中

### <a class="reference-link" name="%E5%93%AA%E4%BA%9Bsink%E5%8F%AF%E4%BB%A5%E5%AF%BC%E8%87%B4%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%8B%92%E7%BB%9D%E6%9C%8D%E5%8A%A1%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>哪些sink可以导致基于DOM的拒绝服务漏洞？
- requestFileSystem()
- RegExp()
### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E7%BC%93%E8%A7%A3%E5%9F%BA%E4%BA%8EDOM%E7%9A%84%E6%B1%A1%E7%82%B9%E6%B5%81(taint-flow)%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>如何缓解基于DOM的污点流(taint-flow)漏洞？

上面那么多种情况，总结一点，想要缓解这种漏洞只能对传递到sink的值进行严格地审查，设置白名单，然后根据上下文严格对其进行编码。没有很容易的防护手段。

### <a class="reference-link" name="DOM%20clobbering"></a>DOM clobbering

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFDOM%20clobbering%EF%BC%9F"></a>什么是DOM clobbering？

梨子目前还并未找到关于这个专有名词比较贴切的中文翻译。DOM clobbering就是注入HTML利用DOM篡改页面中的JS脚本。常见做法就是通过锚点元素覆盖全局变量，当应用程序使用该变量时触发。起名clobbering意为利用DOM覆盖现有的JS脚本，有捣乱的含义。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E5%88%A9%E7%94%A8DOM%20clobbering%EF%BC%9F"></a>如何利用DOM clobbering？

JS开发者比较常用这样的模式<br>`var someObject = window.someObject || `{``}`;`<br>
如果我们可以控制HTML，则可以利用DOM节点去破坏对someObject的引用。例如

```
&lt;script&gt;
  window.onload = function()`{`
    let someObject = window.someObject || `{``}`;
    let script = document.createElement('script');
    script.src = someObject.url;
    document.body.appendChild(script);
  `}`;
&lt;/script&gt;
```

想要利用这段代码我们可以构造这样的payload<br>`&lt;a id=someObject&gt;&lt;a id=someObject name=url href=//malicious-website.com/evil.js&gt;`<br>
这条payload可以通过插入id相同的节点覆盖原有的节点，然后利用值为url的name属性破坏指向外部脚本的someObject对象的url属性。

另外一种手段就是使用form元素搭配一个如input元素去破坏DOM属性。例如破坏attributes让过滤器失去作用，这样就可以让之前无法注入的属性重新可以注入了。例如<br>`&lt;form onclick=alert(1)&gt;&lt;input id=attributes&gt;Click me`<br>
因为我们将id也设置为attributes，过滤器会在input属性中进入死循环，则会允许执行后面本来应被过滤的危险属性。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E5%88%A9%E7%94%A8DOM%20clobbering%E5%8F%91%E5%8A%A8XSS"></a>配套靶场1：利用DOM clobbering发动XSS

我们找到形如上面的一条代码<br>[![](https://p0.ssl.qhimg.com/t01e0d35f8aa032f309.png)](https://p0.ssl.qhimg.com/t01e0d35f8aa032f309.png)<br>
从上面得知我们可以对defaultAvatar发动DOM clobbering，经过burp提示，cid协议没有被resources/js/domPurify-2.0.15.js过滤掉，所以可以利用cid协议绕过对双引号的转义，于是我们可以构造如下payload

[![](https://p3.ssl.qhimg.com/t014435132526b73fc0.png)](https://p3.ssl.qhimg.com/t014435132526b73fc0.png)

这样我们就可以成功发动XSS了

[![](https://p4.ssl.qhimg.com/t017051449481b5a098.png)](https://p4.ssl.qhimg.com/t017051449481b5a098.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E5%88%A9%E7%94%A8DOM%20clobbering%E7%BB%95%E8%BF%87HTML%E8%BF%87%E6%BB%A4%E5%99%A8"></a>配套靶场2：利用DOM clobbering绕过HTML过滤器

首先我们在评论区注入消除掉过滤器作用的XSS payload

[![](https://p1.ssl.qhimg.com/t01e704504ec9796756.png)](https://p1.ssl.qhimg.com/t01e704504ec9796756.png)

然后在Eploit Server设置一个延时的操作，为了保证能够有充足时间执行JS，延时结束后会在src后加一个锚点x，此时会访问id为x的表单，触发里面的XSS payload

[![](https://p0.ssl.qhimg.com/t017d43dabbcca5a8ec.png)](https://p0.ssl.qhimg.com/t017d43dabbcca5a8ec.png)

至此，成功绕过HTML过滤器发动XSS

[![](https://p5.ssl.qhimg.com/t017a34c128791d0e06.png)](https://p5.ssl.qhimg.com/t017a34c128791d0e06.png)

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E7%BC%93%E8%A7%A3DOM%20clobbering%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何缓解DOM clobbering攻击？

可以检查DOM 节点的attributes属性是否实际上是NamedNodeMap的实例，确保attributes是一个属性，而不是一个被clobbering的元素。而且还要避免使用全局OR逻辑运算符(||)。使用DOM审查库，如DOMPurify，进行严格的审查。



## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之客户端漏洞篇 – 基于DOM的漏洞专题的全部内容啦，本专题主要讲了基于DOM的漏洞形成原理，以及多种由不同source和sink导致的污点流漏洞的利用、防护，最后还介绍了高级的DOM clobbering攻击的利用及防护，感兴趣的同学可以在评论区进行讨论，嘻嘻嘻。
