> 原文链接: https://www.anquanke.com//post/id/85034 


# 【技术分享】内网穿透——Android木马进入高级攻击阶段


                                阅读量   
                                **117220**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01a718c07749dfae93.jpg)](https://p0.ssl.qhimg.com/t01a718c07749dfae93.jpg)

**一．	概述**

近日，360烽火实验室发现有数千个样本感染了一种名为“DressCode”的恶意代码，该恶意代码利用实下流行的SOCKS代理反弹技术突破内网防火墙限制，窃取内网数据。这种通过代理穿透内网绕过防火墙的手段在PC上并不新鲜，然而以手机终端为跳板实现对企业内网的渗透还是首见[1]。

SOCKS是一种网络传输协议，SOCKS协议位于传输层与应用层之间，所以能代理TCP和UDP的网络流量，SOCKS主要用于客户端与外网服务器之间数据的传递，那么SOCKS是怎么工作的呢，举个例子：A想访问B站点，但是A与B之间有一个防火墙阻止A直接访问B站点，在A的网络里面有一个SOCKS代理C，C可以直接访问B站点，于是A通知C访问B站点，于是C就为A和B建立起信息传输的桥梁。其工作流程大致分为以下5步：

（1）	代理方向代理服务器发出请求信息。

（2）	代理服务器应答。

（3）	代理方需要向代理服务器发送目的IP和端口。

（4）	代理服务器与目的进行连接。

（5）	连接成功后将需要将代理方发出的信息传到目的方，将目的方发出的信息传到需要代理方。代理完成。

由于SOCKS协议是一种在服务端与客户端之间转发TCP会话的协议，所以可以轻易的穿透企业应用层防火墙；它独立于应用层协议，支持多种不同的应用层服务，如TELNET，FTP，HTTP等。SOCKS协议通常采用1080端口进行通信，这样可以有效避开普通防火墙的过滤，实现墙内墙外终端的连接[2]。

<br>

**二．	地域分布**

360互联网安全中心数据显示，截止目前，“DressCode”恶意代码传播量已达24万之多，在世界范围内分布相当广泛，感染了该恶意代码的手机在全世界的分布情况如下图所示：

[![](https://p0.ssl.qhimg.com/t01b2702802b3a6f82e.png)](https://p0.ssl.qhimg.com/t01b2702802b3a6f82e.png)

图1 “DressCode”木马在世界各地的分布情况

数据显示，已有200多个国家的用户手机安装了带有“DressCode”恶意代码的应用，该恶意代码大多寄宿在时下流行的手机游戏中，其扩散能力很强，其中美国、俄罗斯，德国、法国等欧美发达国家属于重灾区，中国的形势也不容乐观，企业内网安全正在遭受前所未有的挑战。

<br>

**三．	详细分析**

该木马的主要攻击过程如下[3]：

（1）	木马运行时主动连接到攻击者主机（SOCKS客户端），建立一个与攻击者对话的代理通道。

（2）	作为SOCKS服务端的木马根据攻击者传来的目标内网服务器的IP地址和端口，连接目标应用服务器。

（3）	木马在攻击者和应用服务器之间转发数据，进行通信。

当木马安装上手机后，首先会连接C&amp;C服务器，连接成功后，那么木马就与C&amp;C服务器建立了一个对话通道， 木马会读取C&amp;C服务器传送过来的指令， 当木马收到以“CREATE”开头的指令后，就会连接攻击者主机上的SOCKS客户端，攻击者与处于内网中的木马程序建立了信息传输的通道了。

 SOCKS服务端读取SOCKS客户端发送的数据，这些数据包括目标内网应用服务器的IP地址和端口、客户端指令。如下图所示：

[![](https://p0.ssl.qhimg.com/t01b54fb13e603026ae.png)](https://p0.ssl.qhimg.com/t01b54fb13e603026ae.png)

图2 SOCKS服务端获取客户端指令等信息

客户端传递过来的命令主要有CONNECT与BIND两种指令。

**（一）	CONNECT指令**

当SOCKS客户端要与目标应用服务器建立连接时，首先会发送一个CONNECT指令，SOCKS服务端接收到CONNECT指令后，会根据读取到的IP地址和端口连接目标应用服务器，连接成功后，会将请求结果发送给SOCKS客户端，此时目标应用服务器与SOCKS服务端，SOCKS服务端与SOCKS客户端都建立起了会话通道，木马作为数据中转站，可以在攻击者和应用服务器转发任意数据了，其转发过程如图所示：

[![](https://p0.ssl.qhimg.com/t01482ae45007550999.jpg)](https://p0.ssl.qhimg.com/t01482ae45007550999.jpg)

图3 木马转发数据过程

SOCKS协议对数据转发的实现代码如下：

[![](https://p2.ssl.qhimg.com/t0107be8c281d173dc3.png)](https://p2.ssl.qhimg.com/t0107be8c281d173dc3.png)

图4 木马转发数据的代码

那么通过这两条已连接的数据传输通道如何窃取数据的呢？以HTTP协议为例，假设攻击者要访问位于内网的HTTP服务器，那么攻击者首先通过SOCKS客户端将HTTP请求数据发送给SOCKS服务端，SOCKS服务端读取到这些数据后，马上将这些数据转发给应用服务器，应用服务器收到HTTP请求后，将HTTP应答数据发送给木马，木马检查到应答数据，马上转发给攻击者，这样攻击者就通过木马完成了对内网HTTP服务器的访问。

**（二）BIND指令**

当攻击者需要访问内网FTP应用服务器时， SOCKS代理客户端需要向服务端发送BIND指令。SOCKS协议支持采用PORT模式传输FTP数据，PORT模式[4]传输数据的主要过程如下：

FTP客户端首先和FTP服务器建立控制连接，用来发送命令，客户端需要接收数据的时候在这个通道上发送PORT命令。FTP服务器必须和客户端建立一个新的连接用来传送数据。PORT命令包含了客户端用什么端口接收数据。在传送数据的时候，服务端通过自己的端口（默认是20）连接至客户端的指定端口发送数据。

SOCKS代理服务端接收到BIND指令后，木马会利用本地IP和匿名端口生成一个服务端Socket A，并通过建立的数据转发通道，将本地IP和端口发送给攻击者；等待目标应用服务器连接（多为FTP服务器）。

**（三）攻击FTP服务器的过程**

攻击者想要窃取内网FTP服务器数据时，会首先发送CONNECT指令，处于内网中的SOCKS服务端接收到此命令后，会试图和FTP服务器建立一个控制流，如果FTP服务器响应此请求，最终FTP控制流建立；攻击者建立新的到SOCKS服务端的TCP连接，并在新的TCP连接上发送BIND请求，SOCKS 服务端接收到BIND请求后，创建新的Socket，等待目标FTP服务器的连接，并向SOCKS客户端发送第一个BIND响应包；SOCKS客户端收到第一个BIND响应包后，攻击者通过FTP控制流向FTP服务器发送PORT命令，通知FTP服务器主动建立到Socket A的连接；FTP服务器收到PORT命令，主动连接到Socket A；SOCKS服务端接收到来自FTP服务器的连接请求，向SOCKS客户端发送第二个响应包，然后SOCKS服务端开始转发数据流。这样攻击者就通过木马完成了对内网文件服务器的数据窃取。

以上攻击过程如下图所示：

[![](https://p0.ssl.qhimg.com/t01b1d3b2337915fdec.jpg)](https://p0.ssl.qhimg.com/t01b1d3b2337915fdec.jpg)

图4黑客攻击FTP服务器，窃取数据的过程

<br>

**四．总结建议**

“DressCode”恶意代码穿透能力强，地域分布广泛，已成为对内网安全的一种新的潜在威胁，减除接入企业内网的智能终端设备所带来的安全威胁客不容缓。针对此种情况，企业应做好如下两点防范措施：

（1）	严格限制不可信的智能终端设备接入公司内部网络，对要接入公司内网的终端设备进行身份认证。

（2）	智能终端设备不应该与企业内部服务器处于同一个局域网段内。

与此同时，手机用户应该提高安全意识，要从正规的安卓应用商店下载应用，不要安装来历不明的应用软件。

<br>

**引用**

[1] DressCode and its Potential Impact for Enterprises:

[http://blog.trendmicro.com/trendlabs-security-intelligence/dresscode-potential-impact-enterprises/](http://blog.trendmicro.com/trendlabs-security-intelligence/dresscode-potential-impact-enterprises/)

[2] SOCKS: A protocol for TCP proxy across firewalls:

[http://ftp.icm.edu.pl/packages/socks/socks4/SOCKS4.protocol](http://ftp.icm.edu.pl/packages/socks/socks4/SOCKS4.protocol)

[3] Fast Introduction to SOCKS Proxy:

[http://etherealmind.com/fast-introduction-to-socks-proxy/](http://etherealmind.com/fast-introduction-to-socks-proxy/)

[4] FTP协议分析:

[http://kendy.blog.51cto.com/147692/33480](http://kendy.blog.51cto.com/147692/33480)

<br>

**360烽火实验室**

360烽火实验室，致力于Android病毒分析、移动黑产研究、移动威胁预警以及Android漏洞挖掘等移动安全领域及Android安全生态的深度研究。作为全球顶级移动安全生态研究实验室，360烽火实验室在全球范围内首发了多篇具备国际影响力的Android木马分析报告和Android木马黑色产业链研究报告。实验室在为360手机卫士、360手机急救箱、360手机助手等提供核心安全数据和顽固木马清除解决方案的同时，也为上百家国内外厂商、应用商店等合作伙伴提供了移动应用安全检测服务，全方位守护移动安全。
