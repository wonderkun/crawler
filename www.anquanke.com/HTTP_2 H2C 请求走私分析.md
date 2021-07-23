> 原文链接: https://www.anquanke.com//post/id/220996 


# HTTP/2 H2C 请求走私分析


                                阅读量   
                                **254421**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者bishopfox，文章来源：labs.bishopfox.com
                                <br>原文地址：[https://labs.bishopfox.com/tech-blog/h2c-smuggling-request-smuggling-via-http/2-cleartext-h2c](https://labs.bishopfox.com/tech-blog/h2c-smuggling-request-smuggling-via-http/2-cleartext-h2c)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0193ecb9c35dcdd91c.jpg)](https://p2.ssl.qhimg.com/t0193ecb9c35dcdd91c.jpg)



## 0x01 前言

HTTP走私是bug bounty 项目中经常被关注的点。通过HTTP走私，攻击者可以访问内部的服务器甚至是获得各种提权的机会。当前HTTP/1.1被广泛应用，但也暴露出一些问题，比如容易出现请求走私，使用HTTP/2可能是一个解决走私的一个方案。但HTTP/2就能完全防止走私吗？本文就对HTTP/2 h2c 走私进行一个简要的研究。



## 0x02 HTTP/2协议与H2C交换

通常HTTP/2协议在第一个HTTP请求之前，使用h2字符串进行标识，h2c是在Web协议从HTTP/1.1升级到HTTP/2的步骤中使用的标头。根据[RFC-7540](https://tools.ietf.org/html/rfc7540)文档的描述，仅当客户端和服务器均支持HTTP/2时，才能使用HTTP / 2协议。如果有一个如下请求：

```
GET / HTTP/1.1
Host: test.example.com
Connection: Upgrade, HTTP2-Settings
Upgrade: h2c
```

如果是不支持HTTP/2的服务器，则响应：

```
Server ignored
```

如果是支持HTTP/2的服务器，则响应：

```
HTTP/1.1 101 Switching Protocols
Connection: Upgrade
Upgrade: h2c
[ HTTP/2 connection ...
```

通过阅读RFC-7540文档发现，HTTP/2通信与websocket通信有些类似。客户端（Web浏览器）询问服务器是否支持HTTP/2与Web服务器通信，并相应地决定使用HTTP/2还是HTTP/1.x通信。<br>
HTTP/2通信是在第7层（应用程序）中执行的协议，使用TCP连接，由于它与现有的HTTP通信不同，`101 Switching protocol`会像websocket一样检查是否支持之后，才使用协议转换器。并且HTTP/2使用与HTTP/1.1相同的 “http “和 “https “URI方案，HTTP/2共享相同的默认端口号，比如在http-&gt;80，https-&gt;443上与HTTP相同。

> <p>An HTTP/2 connection is an application-layer protocol running on top of a TCP connection ([TCP]). The client is the TCP connection initiator.<br>
HTTP/2 uses the same “http” and “https” URI schemes used by HTTP/1.1. HTTP/2 shares the same default port numbers: 80 for “http” URIs and 443 for “https” URIs. As a result, implementations processing requests for target resource URIs like “[http://example.org/foo](http://example.org/foo)“ or “[https://example.com/bar](https://example.com/bar)“ are required to first discover whether the upstream server (the immediate peer to which the client wishes to establish a connection) supports HTTP/2.<br>
The means by which support for HTTP/2 is determined is different for “http” and “https” URIs. Discovery for “http” URIs is described in Section 3.2. Discovery for “https” URIs is described in Section 3.3.</p>

当HTTP/1.x要升级到HTTP/2，标识符、`HTTP2-Settings`标头和Upgrade标头需要出现在http请求中。标识符的类型包括HTTP的`h2c`和HTTPS的`h2`。当`Upgrade: h2c`时，则以纯文本形式传递HTTP/2：

```
GET / HTTP/1.1
Host: test.example.com
Connection: Upgrade, HTTP2-Settings
Upgrade: h2c
HTTP2-Settings: &lt;base64url encoding of HTTP/2 SETTINGS payload&gt;
```

在服务器支持HTTP/2时，它将`101 Switching protocol`转发到客户端并建立TLS连接（HTTP/2）与客户端进行通信。在这种情况下，使用TLS-ALPN协议。在此过程中，使用APLN扩展名，客户端向服务器提供版本列表，然后服务器选择一个版本。同理，使用https时，HTTP/2选择`h2`。

当直接使用HTTP/2时，通过TLS-ALPN进行协议协商之后，进行TLS连接。



## 0x03 H2C走私

许多Web服务都使用反向代理。在此过程中，当需要进行`101 Switching`时，代理服务器将充当中介，无需任何操作。通过阅读RFC文档和TLS中关于的HTTP/2配置文档，里面声明只有明文连接才可以使用`h2c`升级，并且转发时不应包含`HTTP2-Settings`头。

在RFC7540#section-3.2.1中指出：

> <p>HTTP2-Settings = token68<br>
A server MUST NOT upgrade the connection to HTTP/2 if this header<br>
field is not present or if more than one is present. A server MUST<br>
NOT send this header field.</p>

在[http2-spec](https://http2.github.io/http2-spec/#discover-https)中还指出：

> <p>3.3 Starting HTTP/2 for “https” URIs<br>
A client that makes a request to an “https” URI uses TLS [TLS12] with the application-layer protocol negotiation (ALPN) extension [TLS-ALPN].<br>
HTTP/2 over TLS uses the “h2” protocol identifier. The “h2c” protocol identifier MUST NOT be sent by a client or selected by a server; the “h2c” protocol identifier describes a protocol that does not use TLS.<br>
Once TLS negotiation is complete, both the client and the server MUST send a connection preface (Section 3.5).</p>

在TLS上使用HTTP/2时，被告知使用`h2`协议标识符，而不是`h2c`。正如上一节提到的，`h2c`是一个用在http上的标识，而`h2`则是用于https的标识。如果代理通过TLS将`h2c`转发到后端进行协议升级，会出现什么情况呢？

我个人理解：在反向代理环境中，后端服务器仅知道客户端是Cleartext还是TLS（具有`h2c`和`h2`等标识），因此它将TLS连接确定为HTTP，并在TLS连接上创建TCP隧道。在这种情况下，由于客户端不是HTTP，但仍可以通过TLS使用现有连接。换句话说，由于它是已连接的连接而不是HTTP通信，因此不受Proxy的ACL策略的影响，并且由于TCP Tunnel中的请求可以进行HTTP操作，因此可以访问被阻止的资源。个人感觉整个走私行为与WebSocket连接走私非常相似。

具体走私流程如下：<br>
1 .客户端将HTTP/1.1升级请求发送到反向代理（发送了错误的标头）

2 .代理将请求转发到后端，后端返回101 Swiching协议的响应，并准备接收HTTP/2通信

3 .代理从后端服务器收到101响应时，将创建TCP隧道

4 .客户端从代理接收到101响应时，将重新用现有TCP连接并执行HTTP/2初始化

5 .客户端使用HTTP/2多路复用，发送针对受限资源的违法请求

6 .由于代理服不监视TCP通信（HTTP通过策略），因此它违法求发送到受限页面

7 .服务器响应，转发到TLS隧道，实现走私

[![](https://labs.bishopfox.com/hs-fs/hubfs/h2c%20Sequence%20Diagrams%20v-01.png?width=671&amp;name=h2c%20Sequence%20Diagrams%20v-01.png)](https://labs.bishopfox.com/hs-fs/hubfs/h2c%20Sequence%20Diagrams%20v-01.png?width=671&amp;name=h2c%20Sequence%20Diagrams%20v-01.png)



## 0x04 如何检测

以下代理可能存在这一走私问题：

1 .默认支持（默认存在问题）：

HAProxy v2.2.2

Traefik v2.2

Nuster v5.2

2 .需要配置（只有不恰当设置才会有问题）:

AWS ALB / CLB

NGINX

Apache

Squid

Varnish

Kong

Envoy

Apache Traffic Server

那么如何进行检测测试呢？这里提供[h2csmuggler工具](https://github.com/BishopFox/h2csmuggler)

安装配置：

```
$ git clone https://github.com/BishopFox/h2csmuggler
$ cd h2csmuggler
$ pip3 install h2
```

扫描：

```
$ python3 h2csmuggler.py --scan-list urls.txt --threads 5
```

获取内部端点：

```
$ python3 h2csmuggler.py -x https://edgeserver -X POST -d '`{`"user":128457 "role": "admin"`}`' -H "Content-Type: application/json" -H "X-SYSTEM-USER: true" http://backend/api/internal/user/permissions
```

暴破端点：

```
$ python3 h2csmuggler.py -x https://edgeserver -i dirs.txt http://localhost/
```

这个过程中使用了HTTP/2的多路复用。复用是HTTP/2的主要功能，这意味着可以同时请求多个资源，可以理解为`Connection: keep-alive , pipeline`的改进版。

获取AWS 源数据 api:

```
$ python3 h2csmuggler.py -x https://edgeserver -X PUT -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" http://169.254.169.254/latest/api/token`

```

更多使用细节参见：[https://github.com/BishopFox/h2csmuggler](https://github.com/BishopFox/h2csmuggler)



## 0x05 如何预防

对于HTTP请求走私/ WebSocket连接走私可能有多种应对对策，但从原则上讲，按照RFC文档中的说明，限制在TLS连接中使用`h2c`升级应该是最为有效的方法。当然，如果可能的话，也可以通过限制代理服务器中传递标头，仅处理由服务使用的标头来减小风险。

我个人认为，重要的是要防止使用未使用的标头，限制可以查看其他主机（例如host，x-forward-for等）的标头，以使私有路径无法被直接访问。与所有走私活动一样，防护方了解每一步消息传递的差异比依靠单纯补丁更有预防效果。对于这类通过请求走私或请求伪造攻击进行的任意用户控制的请求，应当维持纵深防御策略，减少架构中走私标头的重要性，在后端识别和拒绝可疑请求，才能有助于减小这类攻击的影响。



## 参考文献

[https://github.com/BishopFox/h2csmuggler](https://github.com/BishopFox/h2csmuggler)

[https://www.hahwul.com/2019/10/30/websocket-connection-smuggling/](https://www.hahwul.com/2019/10/30/websocket-connection-smuggling/)

[https://zh.wikipedia.org/wiki/HTTP/2](https://zh.wikipedia.org/wiki/HTTP/2)

[https://tools.ietf.org/html/rfc7540](https://tools.ietf.org/html/rfc7540)

[https://tools.ietf.org/html/rfc7301](https://tools.ietf.org/html/rfc7301)

[https://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml#alpn-protocol-ids](https://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml#alpn-protocol-ids)

[http://vlambda.com/wz_7iw9mXKwx3W.html](http://vlambda.com/wz_7iw9mXKwx3W.html)
