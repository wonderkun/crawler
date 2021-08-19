> 原文链接: https://www.anquanke.com//post/id/246092 


# 梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之客户端漏洞篇 - WebSocket专题


                                阅读量   
                                **40171**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t013afed2ad16b11371.jpg)](https://p5.ssl.qhimg.com/t013afed2ad16b11371.jpg)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 客户端漏洞篇介绍

> 相对于服务器端漏洞篇，客户端漏洞篇会更加复杂，需要在我们之前学过的服务器篇的基础上去利用。



## 客户端漏洞篇 – WebSocket专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFWebSocket%EF%BC%9F"></a>什么是WebSocket？

WebSocket是一种通过HTTP发起的双向、全双工通信协议。它通常用于现代Web应用程序，用于异步传输。经过测试，burp经典版本1.7只支持查看WebSockets History，并不能对WebSocket包进行重放等操作，所以建议大家一步到位直接更新到最新版哦。

### <a class="reference-link" name="HTTP%E4%B8%8EWebSocket%E6%9C%89%E4%BB%80%E4%B9%88%E5%8C%BA%E5%88%AB%EF%BC%9F"></a>HTTP与WebSocket有什么区别？

从传输模式上就有区别，HTTP是只能由客户端发出请求，然后服务器返回响应，而且是立即响应。而WebSockets是异步传输的，即双方随时都可以向对方发送消息，一般可以用于对数据有实时传输需求的应用程序中。

### <a class="reference-link" name="WebSocket%E8%BF%9E%E6%8E%A5%E6%98%AF%E5%A6%82%E4%BD%95%E5%BB%BA%E7%AB%8B%E7%9A%84%EF%BC%9F"></a>WebSocket连接是如何建立的？

WebSocket连接通常由客户端的JS脚本发起<br>`var ws = new WebSocket("wss://normal-website.com/chat");`<br>
这里的wss协议是经过TLS加密的，而ws就是未加密的。首先会通过HTTP发起一个WebSocket握手请求

```
GET /chat HTTP/1.1
Host: normal-website.com
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: wDqumtseNBJdhkihL6PW7w==
Connection: keep-alive, Upgrade
Cookie: session=KOsEJNuflw4Rd9BDNrVmvwBF9rEijeE2
Upgrade: websocket
```

如果服务器接收了握手请求，则会返回一个WebSocket握手响应

```
HTTP/1.1 101 Switching Protocols
Connection: Upgrade
Upgrade: websocket
Sec-WebSocket-Accept: 0FFP+2nmNIf/h+4BP36k9uzrYGk=
```

建立WebSocket握手后将保持打开状态，这样双方就能随时向另一方发送消息了。WebSocket握手消息有以下值得关注的特性
- 请求和响应中的Connection和Upgrade头表明这是一次WebSocket握手。
- Sec-WebSocket-Version请求头指定客户端希望使用的WebSocket协议版本。通常是13。
- Sec-WebSocket-Key请求头包含一个Base64编码的随机值，是在每个握手请求中随机生成的。
- Sec-WebSocket-Accept响应头包含在Sec-WebSocket-Key请求头中提交的值的哈希值，并与协议规范中定义的特定字符串连接。这样做是为了防止错误配置的服务器或缓存代理导致误导性响应。
### <a class="reference-link" name="WebSocket%E6%B6%88%E6%81%AF%E9%95%BF%E4%BB%80%E4%B9%88%E6%A0%B7%EF%BC%9F"></a>WebSocket消息长什么样？

在双端建立连接以后，就可以异步发送消息了。比如可以从客户端的JS脚本发出这样的消息<br>`ws.send("Peter Wiener");`<br>
一般情况下，WebSocket消息使用JSON格式进行传输数据，例如<br>``{`"user":"Hal Pline","content":"I wanted to be a Playstation growing up, not a device to answer your inane questions"`}``

### <a class="reference-link" name="%E6%93%8D%E7%BA%B5WebSocket%E4%BC%A0%E8%BE%93"></a>操纵WebSocket传输

我们可以通过新版的Burp操纵WebSocket传输，例如
- 拦截和修改WebSocket消息
- 重放并生成新的WebSocket消息
- 操纵WebSocket连接
### <a class="reference-link" name="%E6%8B%A6%E6%88%AA%E5%92%8C%E4%BF%AE%E6%94%B9WebSocket%E6%B6%88%E6%81%AF"></a>拦截和修改WebSocket消息

我们开启了拦截按钮以后，就可以拦截到WebSocket消息，然后直接修改。我们还可以在Proxy的设置里设置拦截哪个方向的WebSocket消息

### <a class="reference-link" name="%E9%87%8D%E6%94%BE%E5%B9%B6%E7%94%9F%E6%88%90%E6%96%B0%E7%9A%84WebSocket%E6%B6%88%E6%81%AF"></a>重放并生成新的WebSocket消息

WebSocket消息也是可以发到Repeater进行重放的。只不过界面和HTTP包不太一样。我们可以在WebSockets History里找到历史接收到的WebSocket消息，然后进行重放。

### <a class="reference-link" name="%E6%93%8D%E7%BA%B5WebSocket%E8%BF%9E%E6%8E%A5"></a>操纵WebSocket连接

有的时候会因为某些原因WebSocket连接断开了，这时候我们可以点击Repeater中的小铅笔图标，里面可以选择新建、克隆、重新连接，经过这样操作以后我们就可以继续攻击了。

### <a class="reference-link" name="WebSocket%E5%AE%89%E5%85%A8%E6%BC%8F%E6%B4%9E"></a>WebSocket安全漏洞

理论上，几乎所有的Web安全漏洞都可能与WebSocket相关，比如
- 数据被以不安全的方式发送到服务器导致如Sql注入、XXE等
- 一些需要通过带外技术触发的WebSocket盲打漏洞
- 也可以通过WebSocket发消息给其他用户导致如XSS等客户端漏洞
### <a class="reference-link" name="%E6%93%8D%E7%BA%B5WebSocket%E6%B6%88%E6%81%AF%E5%88%A9%E7%94%A8%E6%BC%8F%E6%B4%9E"></a>操纵WebSocket消息利用漏洞

如果我们发送这样一条消息给其他用户<br>``{`"message":"Hello Carlos"`}``<br>
这个用户接收到这条消息时会被这样被浏览器解析<br>`&lt;td&gt;Hello Carlos&lt;/td&gt;`<br>
这样的话我们就可以利用这个触发XSS<br>``{`"message":"&lt;img src=1 onerror='alert(1)'&gt;"`}``

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E6%93%8D%E7%BA%B5WebSocket%E6%B6%88%E6%81%AF%E5%88%A9%E7%94%A8%E6%BC%8F%E6%B4%9E"></a>配套靶场：操纵WebSocket消息利用漏洞

我们在聊天框中插入xss payload，但是在WebSocket消息看到尖括号被HTML编码了

[![](https://p1.ssl.qhimg.com/t01239a2a2b17e44e1e.png)](https://p1.ssl.qhimg.com/t01239a2a2b17e44e1e.png)

然后我们将其发到Rpeater中，将其手动修改回来，重放

[![](https://p2.ssl.qhimg.com/t01e35e0a65611f1d46.png)](https://p2.ssl.qhimg.com/t01e35e0a65611f1d46.png)

这样就能成功在对方浏览器触发XSS了

[![](https://p1.ssl.qhimg.com/t017e5e01f5b43b06e6.png)](https://p1.ssl.qhimg.com/t017e5e01f5b43b06e6.png)

### <a class="reference-link" name="%E6%93%8D%E7%BA%B5WebSocket%E6%8F%A1%E6%89%8B%E5%88%A9%E7%94%A8%E6%BC%8F%E6%B4%9E"></a>操纵WebSocket握手利用漏洞

有些漏洞可以通过篡改WebSocket握手请求来触发，例如
- 利用信任关系错误执行某些策略，如篡改X-Forwarded-For头以伪造IP等
- 篡改WebSocket握手上下文以篡改WebSocket消息
- 注入自定义HTTP头触发的攻击
### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E6%93%8D%E7%BA%B5WebSocket%E6%8F%A1%E6%89%8B%E5%88%A9%E7%94%A8%E6%BC%8F%E6%B4%9E"></a>配套靶场：操纵WebSocket握手利用漏洞

我们还是试试能不能触发XSS

[![](https://p2.ssl.qhimg.com/t01975f1a1eb692b47a.png)](https://p2.ssl.qhimg.com/t01975f1a1eb692b47a.png)

发现服务端发现了我们的意图关闭了WebSocket连接，并且试着重连也会马上断开，所以我们要伪装成别的IP，并且得想办法处理一下XSS payload才行

[![](https://p5.ssl.qhimg.com/t019b8ecfe82c12ee1a.png)](https://p5.ssl.qhimg.com/t019b8ecfe82c12ee1a.png)

我们使用X-Forwarded-For伪装IP，并且通过大小写处理绕过了检测成功触发XSS

[![](https://p3.ssl.qhimg.com/t01f5bd3c128c16acbb.png)](https://p3.ssl.qhimg.com/t01f5bd3c128c16acbb.png)

### <a class="reference-link" name="%E8%B7%A8%E7%AB%99WebSocket%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81"></a>跨站WebSocket点击劫持

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E8%B7%A8%E7%AB%99WebSocket%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81%EF%BC%9F"></a>什么是跨站WebSocket点击劫持？

顾名思义，就是利用WebSocket触发的点击劫持，一般点击劫持的目的和CSRF是相同的，所以叫跨站WebSocket点击劫持。但是与常规的CSRF不同的是，跨站WebSocket点击劫持可以实现与受害者双向交互的效果。

### <a class="reference-link" name="%E8%B7%A8%E7%AB%99WebSocket%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81%E5%8F%AF%E4%BB%A5%E5%AE%9E%E7%8E%B0%E5%93%AA%E4%BA%9B%E6%95%88%E6%9E%9C%EF%BC%9F"></a>跨站WebSocket点击劫持可以实现哪些效果？
- 与常规CSRF类似，执行额外的违规操作。
- 与常规CSRF不同的是，跨站WebSocket点击劫持因为可以实现双向交互，所以可以从受害者那获取敏感数据
### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E5%8F%91%E5%8A%A8%E8%B7%A8%E7%AB%99WebSocket%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何发动跨站WebSocket点击劫持攻击？

因为跨站WebSocket点击劫持其实就是通过WebSocket握手触发的CSRF漏洞，所以我们要检查是否存在CSRF防护。例如这样的WebSocket握手请求就可以

```
GET /chat HTTP/1.1
Host: normal-website.com
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: wDqumtseNBJdhkihL6PW7w==
Connection: keep-alive, Upgrade
Cookie: session=KOsEJNuflw4Rd9BDNrVmvwBF9rEijeE2
Upgrade: websocket
```

Sec-WebSocket-Key头包含一个随机值，以防止缓存代理出错，并不是用于身份验证或会话处理的。下面我们通过一道靶场深入理解

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E8%B7%A8%E7%AB%99WebSocket%E7%82%B9%E5%87%BB%E5%8A%AB%E6%8C%81"></a>配套靶场：跨站WebSocket点击劫持

我们发现每次重新进入聊天室都会发送一条消息获取历史聊天记录，并且没有CSRF Token，所以我们在Eploit Server构造这样的payload

[![](https://p3.ssl.qhimg.com/t01e2bfb916adf627af.png)](https://p3.ssl.qhimg.com/t01e2bfb916adf627af.png)

然后当受害者接收到后就会发送历史聊天记录到burp collaborator中

[![](https://p1.ssl.qhimg.com/t01c738de8acb8158c0.png)](https://p1.ssl.qhimg.com/t01c738de8acb8158c0.png)

发现历史聊天记录中的用户名和密码

[![](https://p2.ssl.qhimg.com/t01ece5fc90ee63aac7.png)](https://p2.ssl.qhimg.com/t01ece5fc90ee63aac7.png)

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E5%8A%A0%E5%9B%BAWebSocket%E8%BF%9E%E6%8E%A5%EF%BC%9F"></a>如何加固WebSocket连接？
- 使用wss://协议加密WebSocket连接
- 硬编码WebSocket的端点URL，然后不要将用户可控的数据拼接到URL中
- 对WebSocket握手消息进行CSRF防护
- 在服务端和客户端均安全地处理数据，以防止基于输入的漏洞


## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之客户端漏洞篇 – WebSocket专题的全部内容啦，本专题主要讲了WebSocket的通信原理、以及可能出现的利用WebSocket触发的漏洞及其利用还有WebSocket连接如何加固，WebSocket对于我们还很陌生，所以这个专题还是很有趣的，感兴趣的同学可以在评论区进行讨论，嘻嘻嘻。
