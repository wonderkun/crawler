> 原文链接: https://www.anquanke.com//post/id/238641 


# NAT Slipstreaming悄无声息的穿透你的内网


                                阅读量   
                                **173351**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01d8216d5d0ade810f.jpg)](https://p1.ssl.qhimg.com/t01d8216d5d0ade810f.jpg)



## 前言

2021年10月份，[SamyKamkar](https://samy.pl)公开了NAT Slipstreaming攻击利用手法，属于对协议漏洞的组合巧妙利用，仅仅只需要victim访问网站，便可以实现attacker访问在victim的NAT服务之后的系统的任意TCP/UDP端口。作者提供了详实的文档记录以及攻击发现思路分享，并且提供了poc源码以供复现使用，多重组合利用不禁感慨作者扎实的功底与硬核的能力。github地址[https://github.com/samyk/slipstream](https://github.com/samyk/slipstream)



## 概述

NAT Slipstreaming结合对内置在NATs、防火墙、路由器中的ALG的利用，来达成对用户浏览器的利用，对ALG的利用具体有通过WebRTC或时间攻击来提取内部IP，自动远程MTU和IP分段的发现，TCP保温篡改，TURN认证的滥用，精确的包边界控制，通过浏览器滥用的协议混淆。并且这个利用是通过NAT或者防火墙来打开目标端口，因为他绕过了浏览器的端口限制。

这个攻击需要对TCP/UDP报文精确控制，并且报文内不包含HTTP或者其他报文。这个攻击进行的新的报文注入技术可以在主流的浏览器中奏效，并且是&lt;a target=_blank href=”https://samy.pl/natpin/”&gt;NAT Pinning technique from 2010&lt;/a&gt;的现代版本。

这个**攻击要求NAT/防火墙支持ALG**，ALG对于使用多端口协议是必需的（控制信道+数据信道），比如SIP、H232、FTP、IRC、DCC。

[![](https://p4.ssl.qhimg.com/t01676ca405febbc7e9.png)](https://p4.ssl.qhimg.com/t01676ca405febbc7e9.png)

上图表示的是网络拓扑，内网—&gt;NAT/防火墙—-&gt;网站服务器。内网中的victim如果在浏览器中访问攻击者的网站或者访问网站中含有恶意链接，那么攻击者便可以与受害者的任意端口链接。

[![](https://p4.ssl.qhimg.com/t019cad19c8df2a2b37.png)](https://p4.ssl.qhimg.com/t019cad19c8df2a2b37.png)

上图是最终达成利用的报文结构，报文长度太长时报文会进行分段，达成利用时报文头部必须是特定的字节才能符合要求，因此通过**对报文进行填充，进而可以控制第二三个报文的内容**，构造符合利用条件的报文。



## Application Level Gateway(ALG)

ALGs允许NAT追踪多端口协议，比如FTP协议，从你的系统中发出到FTP服务器，并且当你请求文件发送到你的内部IP时可以进行追踪，ALG可以重写报文使其包括你的公网IP，并且将FTP服务器的连接传回内网。

From [Wikipedia](https://www.wikiwand.com/en/Application-level_gateway):

```
In the context of computer networking, an application-level 
gateway consists of a security component that augments a 
firewall or NAT employed in a computer network. It allows 
customized NAT traversal filters to be plugged into the 
gateway to support address and port translation for certain 
application layer "control/data" protocols such as FTP, 
BitTorrent, SIP, RTSP, file transfer in IM applications, etc. 
In order for these protocols to work through NAT or a 
firewall, either the application has to know about an address/
port number combination that allows incoming packets, or the 
NAT has to monitor the control traffic and open up port 
mappings (firewall pinhole) dynamically as required. 
Legitimate application data can thus be passed through the 
security checks of the firewall or NAT that would have 
otherwise restricted the traffic for not meeting its limited 
filter criteria.
```



## 挖掘协议缺陷过程

挖掘过程中体现了作者的不仅对网络协议，而是整个网络方面的知识，同时又具有逆向固件的能力。这里仅作简单梳理，帮助整体学习挖掘过程，具体细节移步官网链接。
<li>
**固件下载。**首先下载了固件[recent firmware](http://www.downloads.netgear.com/files/GDC/R7000/R7000-V1.0.9.64_10.2.64.zip)，然后利用binwalk解压，binwalk -Me xxx，得到具体的程序文件。</li>
<li>
**函数定位。**然后紧接着作者利用工具搜索二进制文件内的字符串ftp，找到可疑文件/lib/modules/tdts.ko，然后在此文件内匹配ftp字符串，发现了ftp_decode_port_cmd，其中的port很有可能是关联到ALG的。并且它的参数是32bit地址和16位port，分别以8b进行存储。</li>
<li>
**端口限制绕过。**现在浏览器中对端口的屏蔽很严格，许多端口都被屏蔽，但是现在浏览器大多数采用uint32来存储端口，但是协议中是16bit存储的端口号，因此可以利用正数溢出绕过判断。比如想要利用6667端口，但是6667端口被浏览器限制，我们可以传递6667+65536=72203，浏览器判断时发现没有对72203进行限制，但是传递到协议中由于16位溢出实际处理的时6667端口。</li>
<li>
**程序逆向。**接下来开始逆向tdts.ko，起初是通过ftp_decode定位到这个内核文件，那么在函数中所有decode关键字，找到sip_decode函数。</li>
[![](https://p2.ssl.qhimg.com/t010862b048983fc8fd.png)](https://p2.ssl.qhimg.com/t010862b048983fc8fd.png)

**尝试在HTTP POST中加入SIP报文。**选择sip的理由是绝大多数ALG都支持sip协议，根据作者之前在2010年黑帽大会上分享的关于IRC DCC的利用经验来看，当NAT逐行读取SIP协议，会直接忽略HTTP报文头部，并且当读取到REGISTER时会认为这是一个合法的SIP报文。报文内容如下，但是经过测试，发现这并没有奏效，某些地方出现了问题，继续开始逆向固件。

```
POST / HTTP/1.1
Host: samy.pl:5060
Connection: keep-alive
Content-Length: 191
Cache-Control: max-age=0
Origin: http://samy.pl
Upgrade-Insecure-Requests: 1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryhcoAd2iSAx3TJA7A
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.66 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Referer: http://samy.pl/o/sp.html
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9

------WebKitFormBoundaryhcoAd2iSAx3TJA7A
Content-Disposition: form-data; name="textname"

REGISTER sip:samy.pl;transport=TCP SIP/2.0
Contact: &lt;sip:samy@192.168.0.109:1234;transport=TCP&gt;


------WebKitFormBoundaryhcoAd2iSAx3TJA7A--
```

**深入逆向固件。**继续深入逆向的过程中，根据“SIP/2.0”定位到SIP协议大致处理的地方，然后分析过程中，发现了对于INVITE字段的处理，发现对于INVITE字段有一个判断处理，如果INVITE字段位于报文开始，那么正常解析，否则不可以。

同时INVITE与REGISTER是同类型字段，REGISTER字段同样应该也满足类似条件。现在明白了sip报文不被解析的原因是REGISTER必须在报文开始位置，但是如何达到这个条件呢？虽然我们可以利用浏览器生成报文(TCP via HTTP(S), UDP via TURN w/WebRTC)，但是我们无法精确的控制报文的各个结构。如果使用TLS，加密的header位于起始位置，使用HTTP的话，起始是GET、POST等。

**分析linux网络协议栈源码。**直接粘贴作者给的解释，最重要的部分已经加粗。

We’ll take a quick look at the [SIP connection tracking module](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c)
<li>
[`module_init(nf_conntrack_sip_init)`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1698) initialize this connection tracker, calling [`nf_conntrack_sip_init`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1662)
</li>
<li>
[`nf_ct_helper_init(...AF_INET, IPPROTO_TCP, "sip", SIP_PORT...)`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1676) we expect signaling to come in from IPv4 `AF_INET` TCP `IPPROTO_TCP` port 5060 `SIP_PORT`…this occurs for UDP, TCP, IPv4 &amp; IPv6</li>
<li>
[`sip_help_tcp(...)`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1524) called when matching TCP SIP packet comes in
<ul>
<li>
[`process_sip_msg(...)`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1500) if this looks like a potential SIP packet
<ul>
<li>
[`process_sip_request(...)`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1444) is this is a request</li>
<li>
[`strncasecmp(*dptr, handler-&gt;method, ...)`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1476-L1478) **the handler will bail unless the method (eg, REGISTER) occurs at the **start** of the data portion of the packet (TCP or UDP)** like we saw with INVITE up above…[REGISTER](https://tools.ietf.org/html/rfc2543#section-4.2.6) is just another SIP command</li>
- this is a challenge as if we’re only using a web browser, we can’t produce a raw TCP connection and start any packet with our own data, as it will be filled with HTTP/TLS headers…or can we?
<li>
[`process_register_request(...)`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1216)[`nf_ct_expect_init(...)`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1289) via [`sip_handlers`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1391) we initialize the firewall pinhole (port to allow remote person to connect back in), but we don’t open it just yet</li>
<li>
[`nf_nat_sip_hooks`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1295) -&gt; [`nf_nat_sip(...)`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_nat_sip.c#L144) the NAT also mangles (rewrites) the internal IP address of the client to the NAT’s public IP so the destination can properly reach it</li><li>
[`process_sip_response(...)`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1400) now we’re looking at SIP response from the SIP server
<ul>
<li>
[`process_register_response(...)`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1314) -&gt; [`refresh_signalling_expectation(...)`](https://github.com/samyk/linux/blob/29b0b5d56589d66bd5793f1e09211ce7d7d3cd36/net/netfilter/nf_conntrack_sip.c#L1381) the port is forwarded by the NAT only once a valid SIP response is sent by the SIP server</li>
**使REGISTER出现在报文头部。**报文有最大长度范围，如果我们可以发送长报文长度，并且控制其余部分报文内容，那么我们是不是可以使得REGISTER出现在报文头部呢？需要解决几个问题，浏览器将要发送多长的报文，每个浏览器是否不同，每个用户之间是否不同。并且HTTPS由于会加密报文不可控制。

我们在浏览器端发送6000byte大小的HTTP POST到攻击者服务器，带有ID和padding data。并且在攻击者服务端，进行流量嗅探，确定报文的MTU size，IP header size, potential IP options, TCP header size, potential TCP options, data packet size, 和我们实际可控的报文部分。同时我们在攻击者服务端运行服务监听5060端口，同时对浏览器的发送的报文进行正常的回复。如果SIP仅允许UDP报文的话，那么可以利用TURN协议。

**IP地址发现。**如果防火墙/NAT可以正常解析的SIP的话，那么会按照SIP报文中的端口来打开victim的端口， 从而使得攻击者服务器可以和victim链接，但是目前构造保温情况仍未奏效。因为为了是ALG能够将SIP报文认定为是合法报文解析来看来看，请求数据回到的IP地址必须是内网IP地址，但是目前我们还不知道内网IP地址是什么。

在chrome上可以使用WebRTC来提取IP地址，并且这个过程中必须使用HTTPS，而后续攻击步骤必须使用HTTP，所以我们首先将流量重定向到HTTPS，获取IP地址之后在重定向到HTTP进行后续步骤。

如果使用Safari，IE=11，不支持WebRTC的情况，可以使用timing attack攻击来获取内部ip地址。简单来说，就是在页面上附上&lt;img&gt;标签,对应的是不同的网关192.168.*.1等，同时带有onsuccess、onerror的javascript事件，根据onsuccess、onerror触发与否与出发时间长短，判断是否存在对应网关。得到网关地址之后可以同理探测子网内victim地址。

然后所有的利用条件都已达到，我们已经能够成功使得NAT/防火墙解析SIP报文，victim的端口可以在不知情的情况被攻击者打开。



## 实验测试

实验测试首先需要搭建环境，我只有一台PC，所以开两台虚拟机，一台虚拟机是ubuntu 16.04模拟内网主机，另一台虚拟机是pfsense防火墙，ubuntu 16.04用仅主机模式网卡，pfsense有两张网卡对应LAN口、WAN口，LAN口网卡为仅主机模式，WAN口网卡为NAT桥接，这样pfsense的LAN口和ubuntu网卡在同一网段，模拟内网环境，同时设置ubuntu 16.04网关为pfsnese LAN口地址，pfsense WAN口模拟外网接口，然后利用在线poc测试网站[http://samy.pl/slipstream/server进行测试。拓扑图如下。](http://samy.pl/slipstream/server%E8%BF%9B%E8%A1%8C%E6%B5%8B%E8%AF%95%E3%80%82%E6%8B%93%E6%89%91%E5%9B%BE%E5%A6%82%E4%B8%8B%E3%80%82)

[![](https://p1.ssl.qhimg.com/t017d37b1ff2f9aef16.png)](https://p1.ssl.qhimg.com/t017d37b1ff2f9aef16.png)

当我们在ubuntu16.04的firefox中访问恶意浏览器时，在pfsense的流量监控界面可以观察到有大量内网ip出现，对应的是针对内网网关、内网节点的ip地址的探测。

[![](https://p3.ssl.qhimg.com/t019b9341d73877e829.png)](https://p3.ssl.qhimg.com/t019b9341d73877e829.png)

下图是用wireshark抓包，可以看到在探测内网网关地址。

下图是探测到内网网关地址192.168.19.x/24、192.168.174.x/24后开始对D段进行探测，对应的2778条为实际存在的ip地址，所以回送ack报文。

[![](https://p5.ssl.qhimg.com/t017ef48232e21d128f.png)](https://p5.ssl.qhimg.com/t017ef48232e21d128f.png)

前端界面如下所示，在你不知情的情况下探测到你的内网信息，下图所示是首先尝试通过webrtc攻击获取ip地址，但是没有奏效转而进行timing attack攻击(利用js的onsuccess/onerror事件)进行ip地址探测。

[![](https://p4.ssl.qhimg.com/t010f627f6177567149.png)](https://p4.ssl.qhimg.com/t010f627f6177567149.png)

再贴一张利用webrtc攻击获取ip地址的前端效果图，webrtc攻击比起timing atk攻击速度快、准确率高。

[![](https://p1.ssl.qhimg.com/t01be5071d4e59fc014.png)](https://p1.ssl.qhimg.com/t01be5071d4e59fc014.png)

最终一步应该是在外网直接打开内网端口，同时在内网监听端口也可以看到对应显示，在线poc也给了这个功能，但是按钮无法点击，有兴趣的人可以自行探索，也可以观看此研究员的演示视频。



## 总结

最后以两张图做个总结吧

[![](https://p2.ssl.qhimg.com/t0105925f94e3cdeece.jpg)](https://p2.ssl.qhimg.com/t0105925f94e3cdeece.jpg)



## reference

[https://samy.pl/slipstream/](https://samy.pl/slipstream/)<br>[https://www.6cloudtech.com/portal/article/index/id/349/cid/3.html](https://www.6cloudtech.com/portal/article/index/id/349/cid/3.html)<br>[https://blog.51cto.com/fxn2025/2447266](https://blog.51cto.com/fxn2025/2447266)
