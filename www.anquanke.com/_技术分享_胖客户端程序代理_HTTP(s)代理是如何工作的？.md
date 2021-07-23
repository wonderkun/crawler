> 原文链接: https://www.anquanke.com//post/id/86168 


# 【技术分享】胖客户端程序代理：HTTP(s)代理是如何工作的？


                                阅读量   
                                **110808**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：parsiya.net
                                <br>原文地址：[https://parsiya.net/blog/2016-07-28-thick-client-proxying---part-6-how-https-proxies-work/](https://parsiya.net/blog/2016-07-28-thick-client-proxying---part-6-how-https-proxies-work/)

译文仅供参考，具体内容表达以及含义原文为准

翻译：[h4d35](http://bobao.360.cn/member/contribute?uid=1630860495)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**译者序**



**本文是Thick Client Proxying系列文章中的第6篇，前几篇主要介绍了Burp的使用，而这一篇则详细介绍了代理的工作原理，因此单独挑出本文进行了翻译。**

为了编写我们自己的可定制的代理程序，首先我们需要知道代理是如何工作的。在[**Proxying Hipchat Part 3: SSL Added and Removed Here**](https://parsiya.net/blog/2015-10-19-proxying-hipchat-part-3-ssl-added-and-removed-here/)一文中，我想编写一个自定义代理工具（一个简单的Python脚本即可实现），因此我不得不回过头去学习它们的工作原理。我在网上没有找到从信息安全角度分析代理的文章。大多数文章只是在说如何配置缓存或转发代理，但是关于**中间人（Man-in-the-Middle，MitM）**代理的内容则寥寥无几。我在[**那篇文章**](https://parsiya.net/blog/2015-10-19-proxying-hipchat-part-3-ssl-added-and-removed-here/)的第二节中简要介绍了这一点。在本文中，我将对此进行深入分析。实际上我还读了一些RFC，令人惊讶的是这些RFC写得相当好。

如果您想跳过简介，可以直接跳至第3节。



**0. 为什么我需要知道代理是如何工作的？**

这个问题问得好。大多数情况下，我们只需要将浏览器的代理设置为Burp，就能开箱即用。但是，如果出现一点小意外，我们将进入恐慌模式。如果Web应用使用了Java或Silverlight组件，并且它有一些古怪的东西怎么办？另一个原因是，我还想使用Burp代理胖客户端程序（Thick client application），因为Burp不仅仅能够代理Web应用程序。我的意见是：“ 如果应用程序使用了HTTP协议，你就能够使用Burp进行代理 ”。为胖客户端程序设置代理不是一件容易的事（通常情况下，仅仅将流量重定向到代理服务器就让人痛苦不堪了）。如果我们不知道代理的工作原理，我们就无法解决这些问题。

现在你确定你需要看下去了吗？确确确确确……定吗？



**1. ”变成“一个代理**

在阅读本文时，尝试从代理的角度看问题有助于理解，至少对我来说是有用的。代理其实像一个观察者，它不知道系统内部发生的任何事情。作为观察者，我们只能决定代理自身的行为。”当用户在浏览器中输入google.com时，代理程序必须将请求发送到google.com”，那么代理是如何知道这一点的呢？毕竟代理程序还不能神通广大到能够“看到”浏览器的地址栏。

**1.1 这是什么意思？**

假设我们是代理程序。我们唯一能够看到的是客户端（例如浏览器）和目标端点（Endpoint）发送给我们的请求/数据包，除此之外其他信息我们一概不知。作为一个代理，我们必须依靠所知道的有限信息，决定如何处理收到的请求数据。

现在希望我们能够专注一点，开始吧！

<br>

**2. 两种代理简介**

接下来我将讨论两种类型的代理。

**转发代理（Forwarding proxies）**

**TLS终止代理（TLS terminating proxies）**

这些描述不完全准确或详细，但对我们的目的来说足够了。当然这不是详尽的列表，还有其他类型的代理，但我们只对这两种代理感兴趣。讲真，其实我们只对TLS终止代理感兴趣。

**2.1 转发代理**

我们之前应该都遇到过，例如我们每天都能见到和使用的企业代理。如果您在企业环境中，请检查代理自动配置（proxy auto-config, pac）脚本。本质上它是一个文本文件，它告诉应用程序应该向哪里发送流量，并根据目标端点重新路由流量。通常，如果目标端点在内网，则流量通过内部网络正常传输；反之，那些通过互联网发送的请求则被发送至转发代理服务器。你可以在[Microsoft Technet](https://technet.microsoft.com/en-us/library/cc985335.aspx)中看到一些示例。从应用程序的角度来看，转发代理位于企业内网和互联网之间。

由**转发代理**的名称可知，这种代理只转发数据包，却看不到加密的有效内容（例如TLS）。从典型的转发代理的角度来看，一个建立的TLS连接只是一堆含有随机的TCP有效载荷的数据包。

**2.2 TLS终止代理**

Burp就是典型TLS终止代理。如果你知道Burp做了什么（可能是因为你正在阅读本文），你就会明白什么是TLS终止代理。这种代理通常是网络连接的**中间人**，代理程序会解开TLS数据包来查看有效载荷。

这种代理可以是像Burp或Fiddler等这类通常用于（安全）测试的应用程序，或者也可以是像Bluecoat这样的设备或Palo Alto Networks的“thing” （不管它它叫什么名字）的[SSL解密模块]([https://live.paloaltonetworks.com/t5/Configuration-Articles/How-to-Implement-and-Test-SSL-Decryption/ta-p/59719](https://live.paloaltonetworks.com/t5/Configuration-Articles/How-to-Implement-and-Test-SSL-Decryption/ta-p/59719) )。这些设备通常用于深度包检测。

您可以通过将所有目标端点添加到Burp的[SSL Pass Through](https://parsiya.net/blog/2016-03-27-thick-client-proxying—part-1-burp-interception-and-proxy-listeners/#1-4-ssl-pass-through)配置项中来使Burp像转发代理一样工作，这对于排除连接错误非常有用。

**2.2.1 并不总是TLS**

是的。有时我们的代理会解密（或解码）非TLS加密（或编码）层。我将这一类别中的所有代理也划归为TLS终止代理，因为TLS已成为保护传输中数据的最常用方法。



**3. HTTP(s)代理如何工作**

现在我们终于聊到正题了。在所有示例中，我们有一个使用代理（通过一些代理设置）的浏览器，浏览器知道它连接到一个代理（稍后我会谈到这一点）。

**3.1 HTTP代理**

在这种情况下，浏览器正在使用纯HTTP（意味着没有TLS）。在这种情况下，转发代理和TLS终止代理的工作方式类似。

假设我们在浏览器中输入了[http://www.yahoo.com](http://www.yahoo.com) 。实际情况下，这里会产生一个302重定向，让我们暂时忽略这一点，并假设yahoo.com可以通过HTTP进行访问。或许我应该使用example.com举例，但是我比较懒，不想重新画图了。

浏览器和代理之间建立了一个TCP连接（著名的三次握手），然后浏览器发送GET请求。

[![](https://p4.ssl.qhimg.com/t01c44c0b7070574375.png)](https://p4.ssl.qhimg.com/t01c44c0b7070574375.png)

Wireshark中看到的GET如下图所示（我们可以看到数据明文，因为这里没有TLS）。

[![](https://p4.ssl.qhimg.com/t01a95a92817744c0de.png)](https://p4.ssl.qhimg.com/t01a95a92817744c0de.png)

现在，我们（代理）必须决定将这个GET请求发送到哪里。请注意，代理（Burp）和浏览器都位于同一台电脑上，所示上图中的源IP和目标IP均为127.0.0.1。因此，我们无法根据目标IP地址转发请求。

这个GET请求与不设置代理情况下的GET请求有何不同呢？我禁用浏览器的代理设置并重新捕获相同的GET请求，如下图所示。

[![](https://p0.ssl.qhimg.com/t014bdab3daa1b39284.png)](https://p0.ssl.qhimg.com/t014bdab3daa1b39284.png)

注意上图中的高亮部分。发送到代理的请求具有`absoluteURI`。简单来说，发送到代理的GET请求的第二个参数是完整的URI（或URL），代理程序据此发现目标端点。`absoluteURI`最早在RFC2616（讨论HTTP/1.1）中被讨论。在[**5.1.2节 请求URI**](https://tools.ietf.org/html/rfc2616#section-5.1.2)中，我们可以看到：

当请求目标是代理程序时，需要采用**absoluteURI**的形式。

… 

例如以下GET请求：

GET http://www.w3.org/pub/WWW/TheProject.html HTTP/1.1

在较新的RFC中，您可以通过`absolute-URI`关键词查找到相关内容。此格式被称为`absolute-form`。在*[RFC7230  –  HTTP/1.1：消息语法和路由](RFC7230  –  HTTP / 1.1：消息语法和路由)*中，*[第5.3.2节 absolute-form](https://tools.ietf.org/html/rfc7230#section-5.3.2)*中可以看到：

当向代理程序发出请求时，除了`CONNECT`或服务器范围的`OPTIONS`请求（如下所述）之外，客户端**必须**以`absolute-form`的形式发送目标URI。

<br>

absolute-form = absolute-URI

请注意，RFC要求客户端无论什么请求均发送`absolute-URI`（即使他们正在使用`CONNECT`请求）。

代理程序根据`absolute-URI`将请求转发到目标端点（在本例中为Yahoo!）。在这种情况下，转发代理和TLS终止代理的均以类似方式工作，因为它们都可以看到请求报文内部的HTTP有效载荷。

[![](https://p3.ssl.qhimg.com/t01c7c45c8411883591.png)](https://p3.ssl.qhimg.com/t01c7c45c8411883591.png)

**HTTP代理流程如下：**

1、浏览器建立和代理之间的TCP连接。

2、浏览器将HTTP请求（使用`absolute-URI`）发送到代理。

3、代理建立与yahoo.com之间的TCP连接（使用`absolute-URI`）。

4、代理转发HTTP请求。

5、代理收到响应。

6、代理关闭与yahoo.com的连接。

7、代理将响应转发给浏览器。

8、代理通知关闭连接（使用`FIN`）。

9、浏览器和代理之间的连接关闭。

**3.1.1 为什么不使用`Host`请求头（Host Header）？**

如果您已经进行过一些HTTP安全测试（或看过一些HTTP请求），那么您可能会问：“为什么不使用`Host`请求头？”这是一个非常好的问题，我也存在这个疑问。作为代理，我们能够看到`Host`请求头，为什么我们需要使用`absolute-URI`？

答案是为了向后兼容`HTTP/1.0`代理。在RFC7230的*[5.4节 **Host**请求头](https://tools.ietf.org/html/rfc7230#section-5.4)* 中有暗示：

即使请求目标是`absolute-form`的，客户端也**必须**在`HTTP/1.1`请求中发送`Host`请求头字段，因为这样允许Host信息通过旧的`HTTP/1.0`代理进行转发，这类旧的代理可能没有实现`Host`请求头。

后来，它指示代理依赖于`absolute-URI`并忽略`Host`请求头。如果`Host`请求头与`URI`不同，那么代理必须生成正确的`Header`并发送请求。

**3.2 转发代理和HTTPs**

但是HTTP(s)请求如何通过代理进行转发呢？代理是如何工作的？

让我们再次进入转发代理的视角。我们不做TLS握手，只是转发数据包。用户在浏览器中键入https://www.google.com后，会创建一个与我们的TCP连接，然后启动TLS握手。[**RFC5246的第7.4.1.2**](https://tools.ietf.org/html/rfc5246#section-7.4.1.2)节对TLS握手的第一步`ClientHello`进行了讨论（[**RFC5246**](https://tools.ietf.org/html/rfc5246)本质上讨论的是TLS 1.2）。

[![](https://p3.ssl.qhimg.com/t012e22a512b0213c1d.png)](https://p3.ssl.qhimg.com/t012e22a512b0213c1d.png)

到现在为止，我确实没有读过TLS 1.2的RFC，我怀疑你也不需要看。作为代理，我们将看到`ClientHello`报文如下：

[![](https://p5.ssl.qhimg.com/t01718614f231f54db2.png)](https://p5.ssl.qhimg.com/t01718614f231f54db2.png)

但是我们作为代理，我们应该知道这些数据是什么意思。有些工具应该能够为我们做到这一点。这里我使用Netmon，它将`ClientHello`数据包解码如下：

[![](https://p2.ssl.qhimg.com/t013ba067c9c61dabfc.png)](https://p2.ssl.qhimg.com/t013ba067c9c61dabfc.png)

现在，我们要决定往哪里发送**ClientHello**。通过以上信息，我们如何找到目标端点？

其实，答案是：**臣妾做不到啊！**

**3.2.1 CONNECT请求**

简单来说，浏览器需要告诉代理向哪里转发请求，而这一过程应该在TLS握手之前发生（显然在TCP连接建立之后）。这里就需要`CONNECT`方法登场了。

在TLS握手之前，浏览器会将目标端点的域名随`CONNECT`请求发送至代理程序。此请求包含目标端点和端口，形式为`HOST:PORT`。对请求目标而言，这叫做`authority-form`格式。我们可以在*[RFC7230的第5.3.3节 **authority-form**](https://tools.ietf.org/html/rfc7230#section-5.3.3)*中看到相关描述：

请求目标的`authority-form`形式仅用于`CONNECT`请求

… 

客户端**必须**只发送目标URI的授权部分（不包括任何用户信息及其“@”分隔符）作为请求目标。例如，



CONNECT www.example.com:80 HTTP/1.1

在RFC7231  –  HTTP/1.1：语义和内容 第4.3.6节 –  CONNECT中对CONNECT方法进行了讨论：

CONNECT方法请求接收方建立一条连接至由请求目标标识的、目标原始服务器的隧道，如果成功，则将其行为限制在对两个方向上的分组数据的盲目转发，直到隧道关闭。

**客户端说明如下：**

发送`CONNECT`请求的客户端**必须**发送请求目标的授权形式。

… 

例如，

<br>

CONNECT server.example.com:80 HTTP/1.1 

Host: server.example.com:80

代理应该建立到目标站点的连接，如果成功则响应`2xx`(成功) 。在阅读RFC之前，我认为代理会立即发送`2xx`响应，然后创建到目标站点的连接。但我错了，代理只能在连接到端点时进行回复，否则我们如何告诉应用程序无法建立隧道。应用程序在收到`2xx`响应时启动TLS握手。

[![](https://p4.ssl.qhimg.com/t016030c916b0eba9f0.png)](https://p4.ssl.qhimg.com/t016030c916b0eba9f0.png)

**转发代理程序代理HTTPs的流程如下：**

1、浏览器创建与转发代理的TCP连接。

2、浏览器将`CONNECT google.com:443`请求发送给代理。

3、代理尝试连接到`google.com:443`。

4、如果成功，代理返回响应`200 connection established`。

5、现在浏览器知道代理可以和目标端点建立连接并启动TLS握手。

6、转发代理只是传递请求，直到一方关闭连接，然后关闭其他连接。

**3.3 Burp和HTTPs**

Burp（或任何TLS终止代理）的工作方式与上述情况类似。唯一的区别是，Burp通过与浏览器进行TLS握手然后成为连接的中间人，从而能够得到明文的请求数据。默认情况下，Burp使用`CONNECT`请求中的目标端点名称自动生成证书（由其根CA签名）并将其呈现给客户端。

**3.3.1 更正 – 2016年7月30日**

注意：下图是错误的！！！。正如朋友们在评论中所说的那样，从Burp到服务器有两个TCP连接。我的想法是，Burp首先检查与服务器的连接，然后返回`200`响应并根据RFC进行操作。再建立与服务器的新连接，然后将两侧的数据进行转发。

[![](https://p4.ssl.qhimg.com/t0155fa08cbf6f391ae.png)](https://p4.ssl.qhimg.com/t0155fa08cbf6f391ae.png)

注意：上图有误！上图有误！上图有误！

实际情况是，Burp在`CONNECT`请求之后没有建立与目标端点初始TCP连接，只是仅仅向浏览器返回`200`响应。我使用Microsoft Message Analyzer（MMA）捕获流量进行分析。它使我能够捕获从浏览器到Burp的本地流量以及从Burp到Google.com的流量。下图截取了MMA所捕获的部分流量，其中展示了TLS握手过程：

[![](https://p5.ssl.qhimg.com/t013264cc6f02f56e37.png)](https://p5.ssl.qhimg.com/t013264cc6f02f56e37.png)

如上图所示，上边的红框中是浏览器和Burp之间的本地流量，下边的绿框中是Burp和Google.com之间的流量。数据包是按时间先后顺序排列的。正如你所看到的，Burp接收到`CONNECT`请求时并不会进行连接检查。它继续进行TLS握手，然后只有在收到第一个请求（在这种情况下是GET请求）后才连接Google.com。所以实际上**正确的**流程图应该是这样的：

[![](https://p5.ssl.qhimg.com/t01016ee4f5b1bb973c.png)](https://p5.ssl.qhimg.com/t01016ee4f5b1bb973c.png)

**3.3.2 Burp的隐形模式（Invisible Mode）**

这一内容我可能说了[**上百次**](https://parsiya.net/blog/2016-07-28-thick-client-proxying---part-6-how-https-proxies-work/#2-2-1-burp-s-invisible-proxying)了。我们知道RFC阻止代理使用`Host`头来重新路由流量。现在，如果我们有一个使用HTTP但不是`proxy-aware`的客户端（或者我们已经将流量重定向到Burp而不使用代理设置），那么我们可以开启Burp的隐形模式，该模式使用`Host`头来重定向流量。这是HTTP的一个优点，它使得HTTP协议比自定义协议（例如包装在TLS中的二进制blob）更容易进行代理。



**4. Cloudfront和服务器名称指示（Server Name Indication）**

如果您捕获到`ClientHello`请求，以查看代理流程（或者一般情况下），您会注意到您的请求可能和前述的不一样。你可以在`ClienHello`请求报文中看到目标服务器的名字。实际上，如果这里没有服务器名称，那你就很难在其他地方看到它。对于我图中的例子来说，我不得不通过IP地址导航到一个网站。

那么服务器名称是什么？这是一个称为`Server Name Indication`或`SNI`的TLS扩展。我们可以在*[RFC6066的第3节 Server Name Indication](https://tools.ietf.org/html/rfc6066#page-6)*中看到相关描述：

客户端可能希望提供此信息，以实现与在单个底层网络地址上托管多个“虚拟主机”的服务器的安全连接。

我将以我的网站为例。`Parsiya.net`是使用[Hugo](https://gohugo.io/)生成的静态网站。它托管在`Amazon S3 bucket`中。S3不支持通过TLS（或者你也可以称为HTTPs）访问静态托管网站（它支持通过TLS访问单个文件）。为了获得TLS，我在前端使用了Cloudfront。Cloudfront是Amazon的内容分发网络（CDN），并支持自定义TLS证书。如果您使用Cloudfront，您可以免费获得网站的TLS证书。在这种情况下，Cloudfront充当了许多资源的目标端点。

浏览器应该有一种方式告诉Cloudfront所要连接的目标端点，以便Cloudfront可以获取正确的TLS证书并将其呈现给浏览器。SNI能够实现这一功能。典型的发送至`parsiya.net`的`ClientHello`请求如下图所示（其中SNI已解码）：

[![](https://p5.ssl.qhimg.com/t010414e1a06315fcd2.png)](https://p5.ssl.qhimg.com/t010414e1a06315fcd2.png)

现在我们可以看看Cloudfront是如何工作的（简化版）：

[![](https://p2.ssl.qhimg.com/t0187925c0740dc6390.png)](https://p2.ssl.qhimg.com/t0187925c0740dc6390.png)

在这种情况下，Cloudfront的作用就像是一个TLS终止代理。一方面，它有HTTPs请求（浏览器 &lt;–&gt; Cloudfront）；另一方面，它也含有HTTP请求（Cloudfront &lt;–&gt; S3）。这里使用了SNI，而不是`CONNECT`请求。这是能够说得通的，因为Cloudfront并不是浏览器的代理。



**5. 代理感知型客户端**

现在我可以讨论一下代理感知型客户端（proxy-aware clients）。这类客户端程序我们已经见过了，并且也知道它们的工作原理。

代理感知型客户端知道自己何时连接到代理程序。如果发现连接到了代理程序，会执行以下操作：

在HTTP(s)请求中包含`absolute-URI`并发送给代理程序。

在TLS握手之前发送`CONNECT`请求，以便将目标端点告知代理程序。

通常代理感知型客户端具有代理设置功能，或遵循某些操作系统中特定客户端程序的代理设置（例如，IE代理设置）。一旦设置了代理，会通知示浏览器已连接到代理，浏览器则会执行相应地连接行为。几乎所有的浏览器都是代理感知型的客户端。



**6. 结论及未来计划**

以上是所有内容。希望本文对大家有所帮助。现在我们知道了代理程序的内部工作原理。以后如果遇到客户端设置Burp代理后出现异常情况，可以尝试捕获客户端和Burp之间的本地流量进行分析。注意Burp的Alert标签页中的异常信息，通常TLS问题也会出现在这里。

我下一步的计划是讨论一下流量重定向技术。

和往常一样，如果您有任何问题/意见/反馈，您知道在哪里找到我。


