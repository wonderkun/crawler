> 原文链接: https://www.anquanke.com//post/id/83610 


# 利用TFTP协议来进行DDoS放大攻击


                                阅读量   
                                **104180**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://securityaffairs.co/wordpress/45159/hacking/tftp-ddos-amplification-attacks.html](http://securityaffairs.co/wordpress/45159/hacking/tftp-ddos-amplification-attacks.html)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p3.ssl.qhimg.com/t0159fb51dee47521ea.jpg)](https://p3.ssl.qhimg.com/t0159fb51dee47521ea.jpg)

**近期，一群来自爱丁堡龙比亚大学的安全研究专家们发现了一种基于TFTP协议的新型DDoS放大技术。**

据有关媒体报道，有几位来自爱丁堡龙比亚大学的安全研究专家（Boris Sieklik, Richard Macfarlane以及Prof. William Buchanan）发现了一种能够进行DDoS放大攻击的新方法。在此之前，安全社区中的安全专家们就已经发现他们可以利用一些存在错误配置的服务协议（例如[DNS](http://securityaffairs.co/wordpress/22928/cyber-crime/dns-amplification-botnet.html)或者[网络时间协议NTP](http://securityaffairs.co/wordpress/20934/cyber-crime/symantec-network-time-protocol-ntp-reflection-ddos-attacks.html)等）来进行放大攻击。现在，安全专家又发现了，他们还可以利用TFTP协议来进行放大攻击。

无论是基于 DNS 还是基于 NTP，其最终都是基于 UDP 协议的。在 UDP 协议中，正常情况下客户端会发送请求包到服务端，服务端再将响应包返回至客户端，但是 UDP 协议是面向无连接的，所以客户端发送请求包的源 IP 地址很容易进行伪造，当把源 IP地址修改为受害者的 IP地址之后，最终服务端返回的响应包就会返回到受害者的 IP地址。这就形成了一次反射攻击。

放大攻击指的就是一次小的请求包最终会收到一个或者多个多于请求包许多倍的响应包，这样就达到了四两拨千斤的效果。

TFTP协议（Trivial File Transfer Protocol），即简单文本传输协议。该协议是TCP/IP协议族中的一个用来在客户机与服务器之间进行简单文件传输的协议，它可以为用户提供简单的、开销不大的文件传输服务。TFTP协议是基于UDP协议实现的，而且此协议设计的时候是为了进行小文件传输而设计的，所以它不具备通常FTP的许多功。除此之外，它只能从文件服务器上下载或写入文件，而且不能列出目录，不进行认证。

安全专家们发现，攻击者可以利用TFTP协议来在他们的攻击过程中获得一个显著放大的攻击向量。而且不幸的是，根据[相关的端口扫描研究报告](http://internetcensus2012.bitbucket.org/paper.html)显示，目前的互联网中存在有大约599600个开放的TFTP服务器。

[![](https://p1.ssl.qhimg.com/t01c9f8a586973b66c3.png)](https://p1.ssl.qhimg.com/t01c9f8a586973b66c3.png)

相关安全研究人员已经确认，这项技术将帮助攻击者获得相较于原始攻击向量六十倍的放大攻击向量。

[安全研究人员Boris Sieklik表示](http://www.theregister.co.uk/2016/03/09/trivial_ddos_amplification_method/)：“协议中所存在的这个漏洞将允许攻击者利用这些开放的TFTP服务器来对他们的DDoS攻击向量进行放大。如果所有条件均满足的话，攻击者所获得的攻击向量将会是原始攻击向量的六十倍之多。”

除此之外，该研究人员还说到：“我对这类攻击可能产生的影响进行了研究，在对几个不同的TFTP软件进行了研究之后，我发现大多数的软件都会自动对相同的信息进行至少六次转发，而这也将有助于攻击者放大攻击向量。”

正如我们在文中所介绍的那样，TFTP协议（简单文本传输协议）是一个简化版的FTP协议（即文本传输协议，该协议主要用于局域网的文件传输）。因此，TFTP协议则更加简单，实现起来也非常的容易，所以很多组织和机构都会选择使用TFTP服务器。

当然了，我们也可以利用TFTP协议来传输任何类型的文件。为了实现DDoS攻击向量的放大效果，攻击者可以专门伪造一个发送至服务器端的请求信息，然后再伪造一个返回地址。这样一来，服务器所发送的响应信息将会比原始的请求信息更大，攻击者也就成功地实现了放大攻击向量的目的了。

目前，互联网中存在有大量错误配置的服务，攻击者还可以利用这些服务来对某一特定的网站进行攻击。攻击者可以利用伪造的请求信息和响应信息来向这些网站发送垃圾信息，以实现攻击。

安全研究人员表示，他们将会在三月份的计算机安全技术杂志中[发表](http://www.sciencedirect.com/science/article/pii/S0167404815001285)他们的研究成果，并且他们还会向广大用户提供检测和缓解这类攻击的方法。敬请期待！
