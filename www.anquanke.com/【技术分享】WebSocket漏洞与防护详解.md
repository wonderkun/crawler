
# 【技术分享】WebSocket漏洞与防护详解


                                阅读量   
                                **350699**
                            
                        |
                        
                                                                                                                                    ![](./img/85999/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securelayer7.net
                                <br>原文地址：[http://blog.securelayer7.net/owasp-top-10-penetration-testing-soap-application-mitigation/](http://blog.securelayer7.net/owasp-top-10-penetration-testing-soap-application-mitigation/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85999/t011eb1e324a7ded646.jpg)](./img/85999/t011eb1e324a7ded646.jpg)**

****

翻译：[**Legendervi**](http://bobao.360.cn/member/contribute?uid=2535754239)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**socket简介**

一个socket是一次网络通信中的一个端点。socket总是分为两部分：一个IP地址和一个端口。

例如:当您访问www.securelayer7.net时，你的计算机和网站的服务器正在使用socket（端点）进行通信。网站的端点将是：www.securelayer7.net:80，你的计算机的端点将是你的IP地址，后跟任何随机端口号，如192.168.0.111:6574

<br>

**关于WebSocket**

传统上，HTTP活动是由客户端请求资源而服务器来提供服务。服务器不能自己与客户端通话。但这个限制已经被新技术WebSocket消除了。

WebSockets提供持久连接，也称为客户端和服务器之间的全双工连接，双方可以随时使用该连接开始发送数据。

<br>

**它是如何工作的？**

客户端，如浏览器，加载具有WebSocket功能的网页。

[![](./img/85999/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010f8eb2887fb560fe.png)

页面的源代码负责创建WebSocket连接。

[![](./img/85999/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01af70e2ee02a08e7f.png)

该脚本通过WebSocket握手建立WebSocket连接。此过程从客户端向服务器发送常规HTTP请求开始。此请求中包含upgrade请求头，通知服务器客户端希望建立WebSocket连接。

请求如下所示：

[![](./img/85999/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cdc88b67e33d6c0a.png)

值得注意的是，WebSocket使用ws作为访问方案而不是http。所以，上面的请求访问了：ws：//127.0.0.1：9000 / websocket

如果服务器支持WebSocket（针对上述请求），则它将在其响应中使用upgrade请求头进行回复。

响应如下所示：

[![](./img/85999/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0189954543cd6fe3fc.png)

在这个阶段，协议将从HTTP切换到WS。并且在浏览器和服务器之间建立全双工连接。

在这个例子中，我们有一个WebSocket功能，它回传客户端发送的所有单词。例如：如果用户键入单词“Hiii”，那么服务器也会用“Hiii”来回复。

请求：

[![](./img/85999/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018ebb21689fed977b.png)

响应：

[![](./img/85999/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0107f8eca48fbc34ad.png)

用户界面：

[![](./img/85999/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01363f2062fa26b1ba.png)

<br>

**WebSockets的安全隐患**

**A.跨站WebSocket劫持**

注意下面的请求。Origin头有不同的来源127.0.0.1:5555。该请求是使用受害者的cookie发送到WebSocket服务器。这意味着可以使用WebSocket发送类似于CSRF的攻击。

[![](./img/85999/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019c4b38efd0c6a292.png)

但是，这种攻击不止像CSRF将POST数据发送到WebSocket服务器，它还会读取服务器响应。这是因为默认情况下WebSocket服务器不检查“Origin”头，它只是使用cookies检查经过身份验证的用户会话，并将响应发送回请求的“Origin”。

因此，在上述情况下，攻击者也可以读取响应，从而代表受害者控制双向通信。

**防护：**

检查请求的“Origin”头。既然，这个标题是为了防止跨源攻击。如果“Origin”不被信任，那么只需拒绝该请求。例如：如果您的网站的域名为www.example.com，请检查请求是否源自该来源，如果是，则处理该请求。如果否，则拒绝。

另一个解决方案是使用基于会话的个人随机令牌（就像CSRF-Tokens）。生成服务器端，并将它们放在客户端的隐藏字段中。并要求验证。

**B.网络敏感信息泄露**

就像HTTP是纯文本协议一样，WebSockets协议也称为纯文本。这导致攻击者捕获和修改网络上的流量。

**防护：**

建议使用加密（TLS）WebSockets连接。它的URI方案是wss：//。默认端口为443。

如下演示，请求访问ws://127.0.0.1:900/websocket/。如果它是一个安全连接，那么请求将访问wss://127.0.0.1:900/websocket/。

**C.拒绝服务**

默认情况下，WebSockets允许无限制的连接导致DOS。以下是无限次连接到WebSocket服务器的小脚本。

[![](./img/85999/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01666361bcb7e4a355.png)

执行此脚本后，让我们看看WebSocket服务器的日志：

[![](./img/85999/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017e279cb13d3791f6.png)

我们可以看到，几秒钟内就已经完成了475个连接。这将耗尽服务器资源，最终导致DOS攻击。

**防护：**

使用基于IP的速率限制将有助于解决这个问题。

速率限制应允许5-10连接自由，即不进行任何安全检查。但在10个连接之后，如果同一个IP尝试连接，那么应该向用户显示验证码，以确保自动化工具不会产生恶意请求，同时合法用户不会被拒绝服务。

<br>

**结论**

WebSockets非常适合全双工通信，有许多聊天应用程序和社交网站使用。实现WebSockets使应用程序更具可用性和吸引力。但就像任何其他技术一样，也需要在考虑安全性的情况下使用。

<br>

**参考文献**

演示代码取自：[https://github.com/ghedipunk/PHP-Websockets](https://github.com/ghedipunk/PHP-Websockets)

关于WebSockets：[https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications)

安全隐患：[https://www.owasp.org/index.php/Testing_WebSockets_(OTG-CLIENT-010）](https://www.owasp.org/index.php/Testing_WebSockets_(OTG-CLIENT-010))
