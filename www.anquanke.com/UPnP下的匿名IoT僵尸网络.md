> 原文链接: https://www.anquanke.com//post/id/167058 


# UPnP下的匿名IoT僵尸网络


                                阅读量   
                                **204575**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者0day，文章来源：blog.0day.rocks
                                <br>原文地址：[https://blog.0day.rocks/hiding-through-a-maze-of-iot-devices-9db7f2067a80](https://blog.0day.rocks/hiding-through-a-maze-of-iot-devices-9db7f2067a80)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/dm/1024_576_/t01fe6609b3a98e399e.jpg)](https://p5.ssl.qhimg.com/dm/1024_576_/t01fe6609b3a98e399e.jpg)



## Inception Framework组织

2018年3月，赛门铁克对Inception Framework组织滥用易受攻击的UPnP服务来隐藏攻击行为的事件进行了报道。Inception Framework是一个来源不明的APT组织，自2014年以来，一直使用这种手法来发动隐身攻击。基于他们攻击手段的特殊性，赛门铁克在报道中建议用户对注入路由设备的定制恶意软件进行防范。接下来让我们深入了解一下。



## 什么是UPnP

UPnP即为：即插即用，可以将其视为一组协议。它允许设备在局域网中相互发现并使用一些网络功能（如数据共享）且无需做任何配置（因此称为“即插即用”） 。这个是一个年代悠久的协议，在上个世纪90年代后期被设计，并于2000初完成。是用最多的版本是2008年发布的1.1和2015年发布的最新版本（UPnP Device Architecture 2.0）。

根据UPnP规范，它共有6层协议，其中以下三个在本文中需要特别说明：
- 发现：也称为简单服务发现协议（[SSDP](https://en.wikipedia.org/wiki/Simple_Service_Discovery_Protocol)），用来使开启UPnP的设备发现彼此;
- 描述：通过远程URL以XML格式对设备进行描述；
- 控制：控制消息使用SOAP协议，也以XML表示，看起来和RPC类似（但没有任何身份验证）;
下图对这些层如何协作进行了说明：

[![](https://p2.ssl.qhimg.com/t0131123325c9a37847.png)](https://p2.ssl.qhimg.com/t0131123325c9a37847.png)

有关UPnP的详细内容可参考UPnP规范[1.1](http://upnp.org/specs/arch/UPnP-arch-DeviceArchitecture-v1.1.pdf)和[2.0](http://upnp.org/specs/arch/UPnP-arch-DeviceArchitecture-v2.0.pdf)。



## UPnP非法滥用

滥用UPnP的方法有很多种，且不说与之相关的[众多CVE](https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=upnp)。在过去的十年中，已经多次曝出UPnP由于设计上的缺陷而产生的[漏洞](http://www.upnp-hacks.org/)，这些其中大多数漏洞是由于服务配置错误或实施不当造成的。本文对其中一个：Open Forward攻击进行说明，详细分析见下文。

通常UPnP应该在本地局域网内工作，如下图所示：

[![](https://p5.ssl.qhimg.com/t01e90965f547244720.png)](https://p5.ssl.qhimg.com/t01e90965f547244720.png)

UPnP在P2P服务中的典型使用

SSDP在1900端口上使用UDP，它会将M-SEARCH HTTPU数据包（基于UDP的HTTP）发送到239.255.255.250(IPv4组播地址地址）或ff0X::c（IPv6地址）。

[![](https://p2.ssl.qhimg.com/t017e0750c0c9f2dcfc.png)](https://p2.ssl.qhimg.com/t017e0750c0c9f2dcfc.png)

IGD发现M-SEARCH包（1900端口/udp协议)

现在，如果通过Internet向一些易受攻击的UPnP设备发送M-SEARCH数据包，实际上可以收到回复，即使它本该只在局域网内传播！这是第一步：使用路由器作为代理。

[![](https://p2.ssl.qhimg.com/t01779b44b8934e7dab.png)](https://p2.ssl.qhimg.com/t01779b44b8934e7dab.png)

远程UPnP功能

这是此处的第一个漏洞，发现服务不应该在WAN接口上侦听。那么攻击者发送M-SEARCH数据包将得到什么呢？

配置错误的设备实际响应如下图：

[![](https://p3.ssl.qhimg.com/t017b68d388169e5e40.png)](https://p3.ssl.qhimg.com/t017b68d388169e5e40.png)

SSDP在互联网上传播

M-SEARCH服务器的响应包含Location，指向XML设备描述的HTTP标头。

[![](https://p2.ssl.qhimg.com/t0181af29daf4bb0e4c.png)](https://p2.ssl.qhimg.com/t0181af29daf4bb0e4c.png)

在这里，可以看到URL跳转到私有IP地址，可以再次（在大多数情况下）通过其公共IP地址上的WAN访问Web服务器。获得SCPD（服务控制协议文档），这是一个XML文档，它定义了服务实现的动作和状态变量集。

[![](https://p5.ssl.qhimg.com/t018511cfdda453cb4a.png)](https://p5.ssl.qhimg.com/t018511cfdda453cb4a.png)

UPnP的SCPD XML

通过这个文档可以看到该设备提供哪些服务。XML还包含ControlURL，这是与该特定服务进行通信的SOAP端点（实质上，该URL的GET / POST将触发操作）。

WANIPConnection是我们研究中很有趣的一项服务，它遭到了滥用。表面上看起来是UPnP服务，然而攻击者邪恶的目的隐藏其中。



## WANIPConnection服务

根据UPnP标准中的[描述](http://upnp.org/specs/gw/UPnP-gw-WANIPConnection-v2-Service.pdf):

此服务类型使UPnP控制点能够配置和控制符合UPnP的InternetGatewayDeviceWAN接口上的IP连接。可以支持IP连接任何类型的WAN接口，例如，DSL或电缆均可使用此服务。

为WANConnectionDevice上每个Internet连接激活WANIPConnection服务（请参阅状态变量表）。WANIPConnection服务为LAN上的联网客户端提供与ISP的IP级连接。

更简单地说，这是UPnP标准的NAT遍历工具箱。在文档中，您将找到一个名为的函数AddPortMapping()，用于请求路由器（IGD）将TCP / IP流量重定向到LAN中的特定主机/端口。这在需要打开“NATing”设备端口的P2P服务或游戏设备上经常使用。

[![](https://p3.ssl.qhimg.com/t017c62ed93cc20fa70.png)](https://p3.ssl.qhimg.com/t017c62ed93cc20fa70.png)

上图源自WANIPConnection规范

下面我们对滥用UPnP进行演示。



## Open Forward攻击

正如预想的那样，可以无需任何类型的身份验证就启用WAN接口上的UPnP SOAP功能。发送AddPortMapping恶意请求，可以做到：
- 访问NAT内部的本地计算机
- 通过路由器访问远程计算机
第一种攻击被Akamai称为UPnProxy：EternalSilence，有威胁组织曾使用此技巧访问Windows的445端口（SMB服务），来利用臭名昭著的永恒之蓝漏洞。

在研究中（受赛门铁克的启发），我对第二种选择更感兴趣。想弄清楚它如何实现的？

[![](https://p2.ssl.qhimg.com/t01bcd2279f40f1d800.png)](https://p2.ssl.qhimg.com/t01bcd2279f40f1d800.png)

攻击实际上非常简单，你只需发出询问，就像你在局域网一样，路由器用适当的参数添加端口映射。不是将流量重定向到本地客户端，而是指定到任意公网IP地址。在大多数实现过程中，UPnP守护进程将只生成具有指定参数的iptables进程，而不进行任何检查。

这样，您可以将路由器用作哑代理并隐藏IP地址。这就是Inception Framework组织使用3层路由做代理进行攻击的过程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0166a5700477f0b19f.png)

Inception Framework攻击活动



## 影响

根据Shodan[查询结果](https://www.shodan.io/search?query=port%3A1900)，有2,200,000（截至2018年11月）支持UPnP的设备响应M-SEARCH请求……这个数量是巨大的，并且至今仍然存在。

通过主动扫描，我们发现暴露的UPnP设备中，有13％容易受到前面提到的Open Forward攻击。这涉及80个国家约29万台设备。

[![](https://p2.ssl.qhimg.com/t01827a035aa26f9b4e.png)](https://p2.ssl.qhimg.com/t01827a035aa26f9b4e.png)

Open Forward攻击热图

受影响最大的四家运营商：
- 越南FTP Telecom
- 韩国电信
- 中国台湾中华电信
- ChinaNet（上海）
[![](https://p4.ssl.qhimg.com/t0118bd99caa8d21041.png)](https://p4.ssl.qhimg.com/t0118bd99caa8d21041.png)

Open Forward东南亚攻击热图

[![](https://p3.ssl.qhimg.com/t010a2e9130ba565a0b.png)](https://p3.ssl.qhimg.com/t010a2e9130ba565a0b.png)

欧洲也受到影响



## 结论

这说明攻击者有一大批潜在的攻击目标和代理节点。实际上，脆弱节点的数量是Tor中继的44倍。它的攻击痕迹很难捕捉：因为它不需要植入恶意软件，并且通常很难获取日志（大多数是专有的ISP盒子）。

使用该攻击的一个优点是攻击者是“匿名”的，因为大多数IP地址都是住宅IP，既没有被列入黑名单，也不是代理服务器（例如VPN或Tor中继）。但也有缺点：速度非常慢（由于大量的SOAP开销），而且流量未经过加密。

许多威胁组织正在使用UPnP“Open Forward”进行攻击，而且在我们发布研究报告时该服务仍在遭到滥用。
