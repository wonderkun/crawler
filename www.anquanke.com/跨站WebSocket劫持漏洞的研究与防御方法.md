> 原文链接: https://www.anquanke.com//post/id/229486 


# 跨站WebSocket劫持漏洞的研究与防御方法


                                阅读量   
                                **128120**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ieee，文章来源：ieeexplore.ieee.org
                                <br>原文地址：[https://ieeexplore.ieee.org/document/9182458﻿](https://ieeexplore.ieee.org/document/9182458%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01a133135a132751b2.png)](https://p0.ssl.qhimg.com/t01a133135a132751b2.png)



摘要：WebSocket协议是HTML5标准规范的一部分。它是一种新的网络通信协议，提供了客户端与服务器之间的全双工通信机制。WebSocket的出现为实时网络通信带来了利好消息，但相应的WebSocket漏洞也逐渐暴露出来，其中跨站点WebSocket劫持的危害性比较大，容易被忽视。本文主要探讨了WebScoket跨站劫持漏洞的原理，并提出了一种基于混合加密的一次性随机令牌方案来解决WebSocket跨站劫持漏洞，最后对该方案进行了测试，验证其有效性。



## 第一节. 导言

HTML5中的WebSocket协议是基于TCP的应用层通信协议，它参考了套接字的思想，在Web客户端和服务器之间建立了一个全双工的通信通道。在WebSocket通道上，客户端和服务器可以相互通信。WebSocket协议最大的特点是服务器可以主动向客户端发送数据，这对于HTTP协议来说基本上是不可能的，而且它的小头信息非常适合实时通信方案[1]。目前，主流浏览器已经支持WebSocket通信。

随着Internet的快速发展，B/S(Browser/Server)模式已经成为现代应用的主流，Web通信的安全性近年来逐渐受到开发者的重视[2]。WebSocket的诞生主要是为了解决传统B/S模式的实时性问题，因此通信的安全性对于WebSocket应用尤为重要[3]。

在Web即时通信中，WebSocket可以提高网络吞吐量，减少延迟，减轻服务器负担，但也带来了相应的安全隐患。例如，攻击者试图删除和修改用户数据，恶意拦截和窃取数据等。参考文献[4]指出，WebSocket的安全特性可以缓解一些特性的攻击，但近年来Websocket相关的安全漏洞频频曝光，其中最常见的漏洞是CSWSH(Cross-Site WebSocket Hijacking)。该漏洞由德国黑客Christian Schneider于2013年发现并披露，并命名为Cross-Site WebSocket Hijacking[5]。该漏洞容易被研究人员忽视，危害极大。



## 第二节 Websocket协议介绍

2011年，IEFI将WebSocket协议定义为国际标准RFC6455，并由RFC7936进行了补充。WebSocket 后来被纳入 HTML5 规范，其 API 也被 W3C 设定为标准。现在所有主流浏览器都支持它。WebSocket协议是一种基于TCP的应用层协议，它可以在客户端和服务器之间建立全双工通信通道，使双方能够更高效地相互发送和接收数据信息。WebSocket连接的建立需要经过连接请求、握手、连接建立三个步骤[6]，如图1所示。

[![](https://p5.ssl.qhimg.com/t019e55a65c926b28c0.gif)](https://p5.ssl.qhimg.com/t019e55a65c926b28c0.gif)

图1.Websocket连接流程图 – Websocket连接流程图

WebSocket 连接握手是通过 HTTP 完成的。首先，浏览器客户端调用 WebSocket API 以启动连接请求。虽然请求地址以’ws’开头，但它本质上是一个HTTP请求，只是与普通的HTTP请求不同。图 2 是 WebSocket 连接请求消息的部分报头，其中 sec-websocket-key 字段是由客户端生成的 24 位基于 64 字符的随机序列，用于握手验证。

[![](https://p4.ssl.qhimg.com/t01c40b10e5aee7e4ff.gif)](https://p4.ssl.qhimg.com/t01c40b10e5aee7e4ff.gif)

图2.Websocket请求消息的部分头颅

当服务器收到请求后，解析请求头并作出响应，如图3所示。响应状态码101表示连接成功，服务器被替换为WebSocket协议。其他状态码表示连接失败。响应报文中的Sec-Web Socket-Accept是由请求报文中的Sec-WebSocket-Key字段值按照相应算法生成的新字符序列。

[![](https://p4.ssl.qhimg.com/t0192955b5990fce86f.gif)](https://p4.ssl.qhimg.com/t0192955b5990fce86f.gif)

图3.websocket握手响应消息的报头

浏览器客户端在收到响应后，确认服务器已经升级协议，然后按照同样的算法计算出之前的Sec-WebSocket-Key值，再与返回的Sec-Web Socket-Accept进行比较。如果两者一致，则握手成功，客户端升级到WebSocket协议，连接建立，双方可以互相发送数据。否则，连接失败。连接建立后，会一直保持到一方主动发送关闭请求或发生网络错误。浏览器客户端和服务器都可以主动关闭连接。



## 第三节.跨站点Websocket劫持

A. 脆弱性原则

[![](https://p4.ssl.qhimg.com/t01baf8143e64a0ec97.gif)](https://p4.ssl.qhimg.com/t01baf8143e64a0ec97.gif)

图 4 跨网站网络插口劫持漏洞示意图。

WebSocket协议在握手阶段是基于HTTP的。它没有规定服务器在握手期间如何验证客户端的身份。因此，服务器一般采用HTTP客户端认证机制，如cookie、http基本认证等[5]、[7]。这就导致攻击者可以利用恶意网页伪装用户的身份，与服务器建立WebSocket连接。其攻击原理如图4所示。

首先，用户登录并浏览受信任的网站A，登录成功后，浏览器将用户认证信息保存在Cookie中。此后，用户的每次HTTP请求都会自动带上cookie来验证客户端用户的身份。如果恶意网站B在页面中植入与网站A建立WebSocket连接的握手请求，当用户在没有退出网站A的情况下访问恶意网站时，A网站的Cookie会自动添加到请求头中，而服务器并不知道。所以恶意网站可以冒充用户的身份，成功与服务器建立连接，然后窃取服务器消息或发送伪造的请求来篡改数据。

该漏洞的原理与跨站请求伪造(CSRF)[8]、[9]非常相似，但CSRF漏洞只能发送伪造请求，而跨站WebSocket劫持漏洞建立了完整的读/写双向通道，且不受同源策略的限制，所以跨站WebSocket劫持漏洞的危害更大。为此，Christian Schneider将该漏洞命名为 “劫持 “而非 “请求伪造”。

B. 漏洞防御

由于CSWSH和CSRF的原理相似，其解决的核心在于验证客户端的身份[8]，[9]。常见的解决方案有以下几种。

图形验证码。在每次连接请求前，向服务器请求一个图像验证码，然后手动输入，并附在请求中，以验证客户端的身份。这种方法安全性高，但每次都需要人工输入验证码，对用户的体检效果极差。

起源验证[5]，[7]。图2中的Origin字段表示请求的源地址。服务器可以检查请求头中的Origin字段，避免恶意连接请求。然而，Origin字段仅由浏览器提供。对于非浏览器客户端来说，这个字段是空的，攻击者可以伪造Origin头信息。

随机令牌。随机令牌是由服务器生成的随机序列，并在登录完成后发给客户端。客户端在每次请求时都会带上token。服务器设置一个拦截器来验证该值，以确定请求者的身份。这种方法效果很好，但是令牌的安全性难以保证，所以还存在令牌泄露[9]和重放攻击的问题。

参考文献[10]提出了一种随机参数名的CSRF防御方法。虽然可以防止攻击者伪造请求参数，但如果请求参数要由用户动态生成，这种方法就不适用了。特别是对于websocket，只有一次连接操作。所以随机化参数和随机令牌的区别不大，这种方法不适合防御CSWSH漏洞。



## 第四节.防御策略

本文提出了一种基于混合加密的一次性随机令牌方案。该方案可以使用协商加密的一次性令牌来验证客户端的身份，并能成功防止令牌泄露和重放攻击。

A. 混合加密

加密技术[11]、[12]一般分为对称加密和非对称加密两种。对称加密是用一个密钥将明文加密成密文，密文只有通过相同的密钥才能解密得到明文。非对称加密有一对用于加密和解密的密钥对：公钥和私钥。两者必须成对使用，一个用于加密，另一个用于解密。所谓公钥是公知的，私钥只有持有者才能知道。用公钥加密的密文，只能用相应的私钥来解密。或者用私钥加密的密文只能由相应的公钥解密。

对称加密和非对称加密，各有各的优缺点。将它们结合起来使用是一个不错的选择，可以弥补它们的不足。本文所采用的混合加密方法，就是利用非对称加密传输对称加密的密钥，再利用对称加密传输随机Token。这样可以保证客户端和服务器拥有相同的密钥，即使Token被泄露，攻击者也不知道加密密钥，因此无法伪造用户请求。

B. 设计方案

WebSocket连接是在HTTP握手的基础上完成的。本文设计的方案是在此基础上改为六次握手阶段。前四次握手用于登录和协商密钥，后两次握手用于建立WebSocket连接并返回新的令牌。

[![](https://p5.ssl.qhimg.com/t010ff60ef5d79bcf64.gif)](https://p5.ssl.qhimg.com/t010ff60ef5d79bcf64.gif)

图5.防御方案流程图

如图5所示，步骤如下。

1.客户端向服务器请求公钥信息。

2.服务器将公钥信息返回给客户端。

3.客户端随机生成对称加密密钥，然后使用服务器的公钥对密钥和用户登录信息进行加密，最后发送给服务器。

4.服务器接收后，使用私钥对密文进行解密。获得客户端密钥和表单登录信息后，如果登录信息正确，则随机生成一串令牌，服务器将此令牌和客户端密钥保存起来。最后，将令牌和确认信息返回给客户端，协商完成。

5.当客户端建立连接时，用协商密钥对Token进行加密，并与WebSocket连接请求一起发送给服务器。

6.服务器使用协商密钥解密 Token 值，验证身份信息，并决定是否接受连接。如果确认身份信息，则同时销毁之前的Token，并生成新的Token，一起返回给客户端。

本方案首先采用公钥加密，保证登录信息和客户端密钥的安全。之后，利用协商好的密钥对Token Token进行加密，这样即使Token被泄露，如果没有密钥加密，服务器也无法验证Token信息，防止了Token泄露的风险。最后，在验证完成后，销毁之前的Token，发放新的Token，可以有效避免重放攻击。



## 第五节 实验结果与分析

本节主要检验所提出的设计方案的效果。

A. 实验平台和检测工具

测试实验以Ubuntu为服务器系统，node.js为Web容器，360安全浏览器为客户端。在防御方案的实现上，非对称加密采用RSA加密算法，对称加密采用AES加密算法。AES密钥长度和随机令牌长度统一规定为16位字符长度。

采用OW ASP ZAP软件作为实验检测工具。设置浏览器代理后，OW ASP ZAP可以抓取浏览器与服务器之间的数据包进行分析、渗透性检测等。实验主要利用ZAP抓取WebSocket请求连接数据包，修改参数后重新发送连接请求，看是否能成功连接到服务器。

B. 效果测试

图6显示了没有采取任何防御措施的实验结果。原点字段被修改，但连接仍然成功建立，说明存在跨站点WebSocket劫持漏洞。

[![](https://p0.ssl.qhimg.com/t016624c0ae3cf5a72d.gif)](https://p0.ssl.qhimg.com/t016624c0ae3cf5a72d.gif)

图6.在没有任何防御措施的情况下成功建立劫持连接

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a85f87e168d4d670.gif)

图7.使用防御方案后，请求被重放，但连接失败。

图7是使用本文防御方案的实验结果。可以看出，WebSocket连接失败是因为服务器的Token值发生了变化。当重播请求时，服务器验证失败。

之后，取出捕获的响应数据包中的Token值，替换成请求数据包中的Token。而后再次发送请求，但连接再次失败，如图8所示。这是因为Token没有加密，服务器验证还是失败了。

[![](https://p5.ssl.qhimg.com/t016ddee5dc1c502b7b.gif)](https://p5.ssl.qhimg.com/t016ddee5dc1c502b7b.gif)

图8.防御方案

使用防御方案后，Token被篡改，但连接失败。

从以上实验结果可以看出，本文提出的防御方案可以有效抵抗跨站WebSocket劫持漏洞。



## 引用

1.Jiahao Qin “Research and performance analysis of instant messaging based on WebSocket [J]” Mobile Communication vol. 41 no. 12 pp. 44-48 2017.

2.Xuejie Tong and Xufu Peng “Research on Security Algorithms of Web Communication [J]” Information Communication vol. 12 pp. 126-127 2018.

3.Chaoju Hu and Cong Gao “Research on New Features and Security of WebSocket [J]” Network Security Technology and Application vol. 11 pp. 55-56 2015.

4.Cong Gao Research on Application of Information Security Technology in WebSocket Real-Time Communication [D] North China Electric Power University 2016.

5.Jun Zhu Design and Implementation of WebSocket Security Subprotocol Based on Node Platform [D] Huazhong University of Science and Technology 2016.

6.Renwei Yi Research on Real-time Web Application Based on WebSocket [D] Wuhan University of Technology 2013.

7.Deyu Zeng “WebSocket Security Vulnerability and Its Repair [J]” Digital Technology and Application vol. 09 pp. 198 2016.

8.Dong Lu and Tong Zhou “Research on CSRF Attack and Defense Methods [J]” Electronic World vol. 12 pp. 139-140 2017.

9.Xinxin Zheng Research on CSRF Attack and Defense Technology [D] Beijing University of Posts and Telecommunications 2016.

10.Yingjun Wang Jianming Fu and Lily Jiang “Cross-site request forgery defense method based on randomized parameter names [J]” Computer Engineering vol. 44 no. 11 pp. 158-164 2018.

11.Haiyang Wei “Analysis of Information Security Application of Hybrid Encryption Technology in Network Communication [J]” Information Communication vol. 07 pp. 181-182 2018.

12.Pingping Shao “Research on Hybrid Encryption Technology in Computer Network Security [J]” Information Technology and Informatization vol. 12 pp. 123-125 2018.
