> 原文链接: https://www.anquanke.com//post/id/83443 


# 新型DDOS攻击分析取证


                                阅读量   
                                **127812**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.netfort.com/blog/forensic-analysis-of-a-ddos-attack/#.VrLPfPmrShe](https://www.netfort.com/blog/forensic-analysis-of-a-ddos-attack/#.VrLPfPmrShe)

译文仅供参考，具体内容表达以及含义原文为准

在最近这10天，爱尔兰的服务器和公共网络遭受了大量的DDOS攻击。通过BBC的调查我们发现，这些攻击是从2016年开始逐步上升的。

我们发现，大量的DDOS请求都是通过NTP协议发送的数据包。NTP协议在DDOS攻击里面属于向量攻击。这个有点像DNS。一个标准的NTP协议可以发送一小段数据包，从而得到更大的数据包。

在这篇文章中，我们要对NTP协议类型的DDOS进行分析和取证，并且制定出一个解决方案。在下面这幅图里面，我们展示了从LANGuardian系统上捕捉到几个POST数据包，捕捉的端口为SPAN端口。

下面这些截图就是我们捕捉到的数据部走向。从开始攻击的时间到2016年的一月份。

让我们先看未开始攻击的数据部走向。

1.我们可以看到大部分的流量都是IPV4的。

2.百分之97的流量都是TCP协议的数据部，只有少量的UDP。这个和我期望的一样。

3.我们可以看到，里面所有的UDP流量都指向了正确的DNS服务器地址。没有什么问题。

[![](https://p0.ssl.qhimg.com/t01a1e8ed22566610e0.png)](https://p0.ssl.qhimg.com/t01a1e8ed22566610e0.png)

接下来的截图和上面的就大不相同了。从这个网络流量分布图我们可以看到，UDP数据包占据了大部分的流量。这是一个典型的基于UDP数据包放大DDOS攻击的经典例子。大家可以参考下面的连接来知晓原理。

[https://blog.cloudflare.com/understanding-and-mitigating-ntp-based-ddos-attacks/](https://blog.cloudflare.com/understanding-and-mitigating-ntp-based-ddos-attacks/)

[http://www.computerworld.com/article/2487573/network-security/attackers-use-ntp-reflection-in-huge-ddos-attack.html](http://www.computerworld.com/article/2487573/network-security/attackers-use-ntp-reflection-in-huge-ddos-attack.html)

[![](https://p0.ssl.qhimg.com/t01d1c171e461804554.png)](https://p0.ssl.qhimg.com/t01d1c171e461804554.png)

让我们再继续对这些UDP数据包进行分析，发现他们大部分都是NTP和DNS流量。这两个流量都是十分重要的，所以你不能完全的阻止这两个流量访问你的服务器或者网络。还有一个不能使用防火墙的原因就是伪造的IP地址。这些数据包里面包含的IP地址都是伪造的，所以你开防火墙也没多大卵用。

这些请求数据包和合法的数据包基本没什么两样。虽然我们知道它是通过僵尸网络或者各种“肉鸡”发送过来的请求，但是防火墙对它已经毫无用处了。

[![](https://p1.ssl.qhimg.com/t0105125a8f070cd9c2.png)](https://p1.ssl.qhimg.com/t0105125a8f070cd9c2.png)

通过进一步的调查，我们发现这些IP都是来自不同的4700个NTP服务器发送过来的。随后我们又实用WHOIS对这些IP进行核查，发现这些IP都属于一些合法的组织。

等等！这里有些不对劲。不可能4700个NTP服务器都被黑了，并且把流量全部发送到这里。一定有什么事情是我们没注意到的。

先让我们对NTP 协议进行分析。NTP协议是基于UDP协议的。可以说它属于一个单向协议。只发送数据包，不管接受(不懂的麻烦请查看TCP/IP和UDP/IP的不同)。那么也就是说，一个恶意客户端可以一个NTP请求，并且使用的不是自己的IP。这个黑客很聪明，它把IP伪造成目标的IP地址。随后发送数据包给NTP服务器。NTP服务器接收到数据包后，会再一次发送更加庞大的数据包到伪造的IP地址。

我这么说可能有点绕。我来举个例子。假设我的IP地址为192.0.0.1， NTP服务器的IP地址为192.0.0.2，而我要攻击的服务器为192.0.0.3. 因为NTP协议属于一个单向协议，所以我伪造了大量的NTP数据包发送到NTP服务器（192.0.0.2），而且，在这些数据包里面，我伪造的IP地址为192.0.0.3。NTP服务器收到数据包后以为是192.0.0.3发送的，随后发送了大量的返回包给目标服务器。这样就造成了DDOS攻击。

我们可以确定这位黑客使用的攻击方式了。因为我查看DNS日志发现，我们根本没有发送大量的NTP请求。那么只可能是黑客发送的。

[![](https://p2.ssl.qhimg.com/t012046b43ce882bf78.png)](https://p2.ssl.qhimg.com/t012046b43ce882bf78.png)

[![](https://p4.ssl.qhimg.com/t012046b43ce882bf78.png)](https://p4.ssl.qhimg.com/t012046b43ce882bf78.png)

随后我又对返回的NTP数据包进行分析。平均下来，每个返回过来的NTP数据包大概是440 bytes。而我们平常接收到的NTP数据包大概是90 bytes。显然要大了许多。那么基本可以确定这440字节的数据包属于一个monlist请求。而monlist请求是目前已知返回最大的NTP数据包。发送一个很小的请求数据包，就会发送一段很大的返还数据包。

[![](https://p2.ssl.qhimg.com/t014391f8a62dd07e5b.jpg)](https://p2.ssl.qhimg.com/t014391f8a62dd07e5b.jpg)

那么究竟是谁在控制这些僵尸网络，又是怎么控制的? 悲哀的是我们无从知晓。这个黑客完美更地改了NTP请求数据包的IP。别说是得到C&amp;C服务器的IP了，就连僵尸网络的IP地址我们也得不到。

下面这张图展示了黑客是怎么控制这些僵尸网络，并且发送NTP数据包的。

[![](https://p5.ssl.qhimg.com/t01e91a3ab53cb8e813.png)](https://p5.ssl.qhimg.com/t01e91a3ab53cb8e813.png)

[![](https://p3.ssl.qhimg.com/t01e91a3ab53cb8e813.png)](https://p3.ssl.qhimg.com/t01e91a3ab53cb8e813.png)

**防御：**

当你遇到这类攻击时，你有多种防御手段。当你正在遇到这种攻击时，首先你得冷静地分析和思考，从而避免仓促的决定。在受到这类DDOS攻击后，你首先应该查看网络流量分析系统，从而知道攻击目标IP是哪些。

1.如果你的ISP可以阻止可疑的流量，你可以先不用去理会。但是如果这些可疑的流量都指向教育或者政府的服务器，那么你就需要在ISP层面上解决这一问题。

2.如果你使用的web服务器，那么可以考虑搭建一个硬件防火墙。它会对所有流量进行分析，阻断可疑的流量，放行合法的数据，从而防止数据阻塞。

3.如果你的网站是由运营商托管，那么可以使用软件防火墙。

4.在某些极端的情况下，我听说一些公司会改变他们的ISP来摆脱这个问题。

**翻译总结：**

就目前来说，我们没有一个完美的办法来防御这种DDOS攻击。因为它发送的数据包和正常的数据包没有什么不同。只能期望以后有更好的协议出现来完全的代替NTP协议。
