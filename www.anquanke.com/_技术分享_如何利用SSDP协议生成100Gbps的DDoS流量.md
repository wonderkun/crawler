> 原文链接: https://www.anquanke.com//post/id/86539 


# 【技术分享】如何利用SSDP协议生成100Gbps的DDoS流量


                                阅读量   
                                **198998**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.cloudflare.com
                                <br>原文地址：[https://blog.cloudflare.com/ssdp-100gbps](https://blog.cloudflare.com/ssdp-100gbps)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t017dbba12fa69a137d.jpg)](https://p1.ssl.qhimg.com/t017dbba12fa69a137d.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

****

上一个月，我们发表了一篇分析[文章](https://blog.cloudflare.com/reflections-on-reflections/)，与大家分享了常见的反弹式攻击的统计信息。当时SSDP攻击的平均流量大约为12 Gbps，被我们记录在案的规模最大的SSDP（Simple Service Discovery Protocol，简单服务发现协议）反弹式攻击有以下几点统计数据：

1、30 Mpps（每秒发送上百万个包）

2、80 Gbps（每秒发送数十亿个比特）

3、大约使用了94万个IP用于反弹攻击

几天以前，我们发现了一个规模异常巨大的SSDP放大攻击，再次刷新了这些记录。这次攻击值得好好深入研究一番，因为它的规模已经超过了100Gbps这个阈值。

整个攻击过程中，每秒发送的数据包走向大致如下图所示：

 [![](https://p3.ssl.qhimg.com/t01b6db7a51193aab15.png)](https://p3.ssl.qhimg.com/t01b6db7a51193aab15.png)

带宽占用情况如下图所示：

 [![](https://p4.ssl.qhimg.com/t0167cb9bb07b196c0e.png)](https://p4.ssl.qhimg.com/t0167cb9bb07b196c0e.png)

整个数据包洪泛攻击持续了38分钟。根据我们采样的网络数据流，我们发现这次攻击用到了93万个反弹服务器。我们估计在时长38分钟的攻击中，每个反弹服务器往Cloudflare发送了11.2万个数据包。

反弹服务器遍布全球，其中以阿根廷、俄罗斯以及中国的服务器占比最大。以IP数统计的话，反弹服务器在每个国家或地区的分布情况如下所示：

```
$ cat ips-nf-ct.txt|uniq|cut -f 2|sort|uniq -c|sort -nr|head
 439126 CN
 135783 RU
  74825 AR
  51222 US
  41353 TW
  32850 CA
  19558 MY
  18962 CO
  14234 BR
  10824 KR
  10334 UA
   9103 IT
   ...
```

反弹服务器所在的IP分布与ASN的规模成正比，这些服务器通常位于全世界最大的家用ISP（Internet Service Provider，互联网服务提供商）网络中，如下所示：

```
$ cat ips-nf-asn.txt |uniq|cut -f 2|sort|uniq -c|sort -nr|head
 318405 4837   # CN China Unicom
  84781 4134   # CN China Telecom
  72301 22927  # AR Telefonica de Argentina
  23823 3462   # TW Chunghwa Telecom
  19518 6327   # CA Shaw Communications Inc.
  19464 4788   # MY TM Net
  18809 3816   # CO Colombia Telecomunicaciones
  11328 28573  # BR Claro SA
   7070 10796  # US Time Warner Cable Internet
   6840 8402   # RU OJSC "Vimpelcom"
   6604 3269   # IT Telecom Italia
   6377 12768  # RU JSC "ER-Telecom Holding"
   ...
```



**二、何为SSDP**

****

攻击所用的报文为UDP报文，源端口为1900。[SSDP](https://en.wikipedia.org/wiki/Simple_Service_Discovery_Protocol)协议使用的正是这个端口，而SSDP协议是UPnP的核心协议之一。UPnP是[零配置（zero-configuration）网络协议](https://en.wikipedia.org/wiki/Zero-configuration_networking#UPnP)的一种。大众使用的家庭设备一般都支持这个协议，以便用户的主机或手机能够轻松发现这些设备。当一个新的设备（比如说笔记本）加入到网络中时，它可以向本地网络查询特定设备是否存在，这些设备包括互联网网关、音频系统、TV或者打印机等。读者可以参考[此处](http://www.zeroconf.org/zeroconfandupnp.html)阅读UPnP与Bonjour的详细对比。

[UPnP](http://www.upnp-hacks.org/upnp.html)协议的标准化做的不尽如人意，在有关M-SEARCH请求报文的[规范文档](https://web.archive.org/web/20151107123618/http:/upnp.org/specs/arch/UPnP-arch-DeviceArchitecture-v2.0.pdf)中，部分内容摘抄如下（这也是UPnP在探测设备时使用的主要方法）：

“当某个控制节点（control point）加入到网络中时，控制节点可以根据需要使用UPnP探测协议搜索网络中的其他设备。在搜索过程中，控制节点通过在保留地址及相关端口（239.255.255.250:1900）上广播请求来查找其他设备，所使用的搜索消息包含特定的模式，不同的设备或服务具有不同的类型和标识符”。

规范中关于M-SEARCH报文的应答有如下说明：

“为了能被网络搜索发现，目标设备应该向发起多播请求的源IP地址及端口发送单播UDP响应。如果M-SEARCH请求报文的ST头部字段以“ssdp:all”、“upnp:rootdevice”或者“uuid:”开头，后面跟着与设备相匹配的UUID信息，或者如果M-SERCH请求与设备支持的设备类型或服务类型相匹配，那么该设备就会应答M-SEARCH请求报文”。

这种策略在实际环境中能够正常工作。例如，我的Chrome浏览器经常会请求搜索智能电视：

```
$ sudo tcpdump -ni eth0 udp and port 1900 -A
IP 192.168.1.124.53044 &gt; 239.255.255.250.1900: UDP, length 175  
M-SEARCH * HTTP/1.1  
HOST: 239.255.255.250:1900  
MAN: "ssdp:discover"  
MX: 1  
ST: urn:dial-multiscreen-org:service:dial:1  
USER-AGENT: Google Chrome/58.0.3029.110 Windows
```

这个报文被发往一个多播IP地址。监听这一地址的其他设备如果与报文头部中指定的ST（search-target，搜索目标）多屏幕类型设备相匹配，那么这些设备应该会响应这个请求报文。

除了请求具体的设备类型，请求报文中还可以包含两类“通用的”ST查询类型：

1、upnp:rootdevice：搜索root设备

2、ssdp:all：搜索所有的UPnP设备以及服务

你可以运行以下python脚本（在[另一脚本](https://www.electricmonk.nl/log/2016/07/05/exploring-upnp-with-python/)的基础上修改而得），使用前面提到的这些ST查询类型来枚举网络中的设备列表：

```
#!/usr/bin/env python2
import socket  
import sys

dst = "239.255.255.250"  
if len(sys.argv) &gt; 1:  
    dst = sys.argv[1]
st = "upnp:rootdevice"  
if len(sys.argv) &gt; 2:  
    st = sys.argv[2]

msg = [  
    'M-SEARCH * HTTP/1.1',
    'Host:239.255.255.250:1900',
    'ST:%s' % (st,),
    'Man:"ssdp:discover"',
    'MX:1',
    '']

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  
s.settimeout(10)  
s.sendto('rn'.join(msg), (dst, 1900) )

while True:  
    try:
        data, addr = s.recvfrom(32*1024)
    except socket.timeout:
        break
    print "[+] %sn%s" % (addr, data)
```

在我个人的家庭网络中，我总共发现了两个设备：

```
$ python ssdp-query.py
[+] ('192.168.1.71', 1026)
HTTP/1.1 200 OK  
CACHE-CONTROL: max-age = 60  
EXT:  
LOCATION: http://192.168.1.71:5200/Printer.xml  
SERVER: Network Printer Server UPnP/1.0 OS 1.29.00.44 06-17-2009  
ST: upnp:rootdevice  
USN: uuid:Samsung-Printer-1_0-mrgutenberg::upnp:rootdevice

[+] ('192.168.1.70', 36319)
HTTP/1.1 200 OK  
Location: http://192.168.1.70:49154/MediaRenderer/desc.xml  
Cache-Control: max-age=1800  
Content-Length: 0  
Server: Linux/3.2 UPnP/1.0 Network_Module/1.0 (RX-S601D)  
EXT:  
ST: upnp:rootdevice  
USN: uuid:9ab0c000-f668-11de-9976-000adedd7411::upnp:rootdevice
```



**三、防火墙配置不当**

****

现在我们对SSDP的基本概念有了一定程度的了解，那么理解反弹式攻击也不是件难事了。我们可以使用两种方式发送M-SEARCH报文：

1、如前文所述，我们可以使用多播地址发送这个报文

2、使用普通单播地址上的启用UPnP/SSDP协议的主机

第二种方法也是行之有效的，例如，我们可以将我的打印机所在的IP地址作为目标：

```
$ python ssdp-query.py 192.168.1.71
[+] ('192.168.1.71', 1026)
HTTP/1.1 200 OK  
CACHE-CONTROL: max-age = 60  
EXT:  
LOCATION: http://192.168.1.71:5200/Printer.xml  
SERVER: Network Printer Server UPnP/1.0 OS 1.29.00.44 06-17-2009  
ST: upnp:rootdevice  
USN: uuid:Samsung-Printer-1_0-mrgutenberg::upnp:rootdevice
```

现在问题已经变得非常明朗了：SSDP协议并没有检查请求报文是否来自于设备所在的那个网络。即便M-SEARCH报文来自于互联网，设备也会积极应答这个报文。如果防火墙配置不当，将1900这个UDP端口暴露在互联网中，那么这个端口就会成为UDP放大攻击的绝佳目标。

如果目标配置不当，我们的脚本就可以在互联网中畅通无阻：

```
$ python ssdp-query.py 100.42.x.x
[+] ('100.42.x.x', 1900)
HTTP/1.1 200 OK  
CACHE-CONTROL: max-age=120  
ST: upnp:rootdevice  
USN: uuid:3e55ade9-c344-4baa-841b-826bda77dcb2::upnp:rootdevice  
EXT:  
SERVER: TBS/R2 UPnP/1.0 MiniUPnPd/1.2  
LOCATION: http://192.168.2.1:40464/rootDesc.xml
```

**<br>**

**四、报文放大**

****

ST类型中，ssdp:all这个类型所造成的破坏更加明显，这个类型的响应报文体积上更为庞大：

```
$ python ssdp-query.py 100.42.x.x ssdp:all
[+] ('100.42.x.x', 1900)
HTTP/1.1 200 OK  
CACHE-CONTROL: max-age=120  
ST: upnp:rootdevice  
USN: uuid:3e55ade9-c344-4baa-841b-826bda77dcb2::upnp:rootdevice  
EXT:  
SERVER: TBS/R2 UPnP/1.0 MiniUPnPd/1.2  
LOCATION: http://192.168.2.1:40464/rootDesc.xml

[+] ('100.42.x.x', 1900)
HTTP/1.1 200 OK  
CACHE-CONTROL: max-age=120  
ST: urn:schemas-upnp-org:device:InternetGatewayDevice:1  
USN: uuid:3e55ade9-c344-4baa-841b-826bda77dcb2::urn:schemas-upnp-org:device:InternetGatewayDevice:1  
EXT:  
SERVER: TBS/R2 UPnP/1.0 MiniUPnPd/1.2  
LOCATION: http://192.168.2.1:40464/rootDesc.xml

... 6 more response packets....
```

在这个特定的场景中，一个SSDP M-SEARCH报文就能触发8个响应报文。tcpdump结果如下所示：

```
$ sudo tcpdump -ni en7 host 100.42.x.x -ttttt
 00:00:00.000000 IP 192.168.1.200.61794 &gt; 100.42.x.x.1900: UDP, length 88
 00:00:00.197481 IP 100.42.x.x.1900 &gt; 192.168.1.200.61794: UDP, length 227
 00:00:00.199634 IP 100.42.x.x.1900 &gt; 192.168.1.200.61794: UDP, length 299
 00:00:00.202938 IP 100.42.x.x.1900 &gt; 192.168.1.200.61794: UDP, length 295
 00:00:00.208425 IP 100.42.x.x.1900 &gt; 192.168.1.200.61794: UDP, length 275
 00:00:00.209496 IP 100.42.x.x.1900 &gt; 192.168.1.200.61794: UDP, length 307
 00:00:00.212795 IP 100.42.x.x.1900 &gt; 192.168.1.200.61794: UDP, length 289
 00:00:00.215522 IP 100.42.x.x.1900 &gt; 192.168.1.200.61794: UDP, length 291
 00:00:00.219190 IP 100.42.x.x.1900 &gt; 192.168.1.200.61794: UDP, length 291
```

这个目标完成了8倍的报文放大作用，以及26倍的带宽放大作用。不幸的是，这种情况对SSDP来说普遍存在。

<br>

**五、IP地址欺骗**

****

攻击所需的最后一个步骤就是欺骗存在漏洞的服务器，让它代替攻击者向目标IP发起洪泛攻击。为了做到这一点，攻击者需要在请求报文中使用[源IP地址欺骗](https://en.wikipedia.org/wiki/IP_address_spoofing)技术。

我们对此次攻击中使用的反弹式IP地址进行了探测。我们发现在92万个反弹IP中，只有35万个IP（约占38%）会响应我们的SSDP探测报文。

有响应的反弹IP节点中，平均每个节点发送了7个数据包：

```
$ cat results-first-run.txt|cut -f 1|sort|uniq -c|sed -s 's#^ +##g'|cut -d " " -f 1| ~/mmhistogram -t "Response packets per IP" -p
Response packets per IP min:1.00 avg:6.99 med=8.00 max:186.00 dev:4.44 count:350337  
Response packets per IP:  
 value |-------------------------------------------------- count
     0 |                    ****************************** 23.29%
     1 |                                              ****  3.30%
     2 |                                                **  2.29%
     4 |************************************************** 38.73%
     8 |            ************************************** 29.51%
    16 |                                               ***  2.88%
    32 |                                                    0.01%
    64 |                                                    0.00%
   128 |                                                    0.00%
```

响应报文平均大小为321字节（正负29字节）。我们的请求报文大小为110字节。

根据我们的测量结果，攻击者使用包含ssdp:all头部的M-SEARCH报文能够达到以下效果：

1、7倍的数据包放大效果

2、20倍的带宽放大效果

据此，我们可以推测出，生成43 Mpps/112 Gbps的攻击大概需要：

1、6.1 Mpps的伪造报文容量

2、5.6 Gbps的伪造报文带宽

换句话说，一个连接稳定的具备10 Gbps带宽的服务器就可以通过IP地址欺骗技术发起这种规模的SSDP攻击。

<br>

**六、关于SSDP服务器的更多说明**

****

根据我们对SSDP服务器的探测结果，我们从响应报文的Server头部中，梳理出最常见的几个设备信息，如下所示：

```
104833 Linux/2.4.22-1.2115.nptl UPnP/1.0 miniupnpd/1.0
  77329 System/1.0 UPnP/1.0 IGD/1.0
  66639 TBS/R2 UPnP/1.0 MiniUPnPd/1.2
  12863 Ubuntu/7.10 UPnP/1.0 miniupnpd/1.0
  11544 ASUSTeK UPnP/1.0 MiniUPnPd/1.4
  10827 miniupnpd/1.0 UPnP/1.0
   8070 Linux UPnP/1.0 Huawei-ATP-IGD
   7941 TBS/R2 UPnP/1.0 MiniUPnPd/1.4
   7546 Net-OS 5.xx UPnP/1.0
   6043 LINUX-2.6 UPnP/1.0 MiniUPnPd/1.5
   5482 Ubuntu/lucid UPnP/1.0 MiniUPnPd/1.4
   4720 AirTies/ASP 1.0 UPnP/1.0 miniupnpd/1.0
   4667 Linux/2.6.30.9, UPnP/1.0, Portable SDK for UPnP devices/1.6.6
   3334 Fedora/10 UPnP/1.0 MiniUPnPd/1.4
   2814  1.0
   2044 miniupnpd/1.5 UPnP/1.0
   1330 1
   1325 Linux/2.6.21.5, UPnP/1.0, Portable SDK for UPnP devices/1.6.6
    843 Allegro-Software-RomUpnp/4.07 UPnP/1.0 IGD/1.00
    776 Upnp/1.0 UPnP/1.0 IGD/1.00
    675 Unspecified, UPnP/1.0, Unspecified
    648 WNR2000v5 UPnP/1.0 miniupnpd/1.0
    562 MIPS LINUX/2.4 UPnP/1.0 miniupnpd/1.0
    518 Fedora/8 UPnP/1.0 miniupnpd/1.0
    372 Tenda UPnP/1.0 miniupnpd/1.0
    346 Ubuntu/10.10 UPnP/1.0 miniupnpd/1.0
    330 MF60/1.0 UPnP/1.0 miniupnpd/1.0
    ...
```

最常见的ST头部值如下所示：

```
298497 upnp:rootdevice
 158442 urn:schemas-upnp-org:device:InternetGatewayDevice:1
 151642 urn:schemas-upnp-org:device:WANDevice:1
 148593 urn:schemas-upnp-org:device:WANConnectionDevice:1
 147461 urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1
 146970 urn:schemas-upnp-org:service:WANIPConnection:1
 145602 urn:schemas-upnp-org:service:Layer3Forwarding:1
 113453 urn:schemas-upnp-org:service:WANPPPConnection:1
 100961 urn:schemas-upnp-org:device:InternetGatewayDevice:
 100180 urn:schemas-upnp-org:device:WANDevice:
  99017 urn:schemas-upnp-org:service:WANCommonInterfaceConfig:
  98112 urn:schemas-upnp-org:device:WANConnectionDevice:
  97246 urn:schemas-upnp-org:service:WANPPPConnection:
  96259 urn:schemas-upnp-org:service:WANIPConnection:
  93987 urn:schemas-upnp-org:service:Layer3Forwarding:
  91108 urn:schemas-wifialliance-org:device:WFADevice:
  90818 urn:schemas-wifialliance-org:service:WFAWLANConfig:
  35511 uuid:IGD`{`8c80f73f-4ba0-45fa-835d-042505d052be`}`000000000000
   9822 urn:schemas-upnp-org:service:WANEthernetLinkConfig:1
   7737 uuid:WAN`{`84807575-251b-4c02-954b-e8e2ba7216a9`}`000000000000
   6063 urn:schemas-microsoft-com:service:OSInfo:1
    ...
```

根据结果，存在漏洞的IP似乎都是未经保护的家用路由器。

<br>

**七、开放式SSDP已经成为突破口**



为了能从互联网访问家用打印机而开放1900 UDP端口，这并不是件多么新奇的事情，但并不是个好主意。早在2013年，已经有[研究结果](https://community.rapid7.com/community/infosec/blog/2013/01/29/security-flaws-in-universal-plug-and-play-unplug-dont-play)指出了相关问题的存在。

SSDP的作者显然没有考虑UDP报文放大攻击可能造成的破坏性。人们已经提了若干个建议，以便在未来安全地使用SSDP协议，如下：

1、SSDP的作者应该明确真实世界中使用单播地址发起M-SEARCH查询报文的必要性。根据我的理解，只有在本地局域网中以多播方式查询时M-SEARCH报文才有实际意义。

2、单播形式的M-SEARCH应该被废弃，或者在查询速率上有所限制，与[DNS响应速率限制方案](http://www.redbarn.org/dns/ratelimits)类似。

3、M-SEARCH响应报文只能投递到本地网络中。发往外网的响应报文不仅意义不大，而且容易存在漏洞。

与此同时，我们有如下提议：

1、网络管理员应当确认防火墙会阻拦使用UDP 1900端口的入站请求。

2、互联网服务商绝对不应该允许IP地址欺骗技术横行其道。IP地址欺骗技术是这个问题的根本原因，读者了解臭名昭著的[BCP38](http://www.bcp38.info/index.php/Main_Page)就能理解这一点。

3、互联网服务商应该允许他们的客户使用BGP Flowspec功能来限制从来自于UDP 1900源端口的入站流量。

4、互联网服务商应该在内部收集netflow协议样本。我们需要使用netflow来识别发起攻击的真正来源。通过netflow，我们可以快速得出问题的答案，类似问题包括“哪些客户向1900端口发送了6.4Mpps的网络流量？”等。由于隐私保护问题，我们建议服务商在隐私保护前提下尽可能地收集netflow样本数据，比如6.4万个报文中抽样1个报文来收集信息。这种采样频率对跟踪DDoS而言已经足够，同时也能保留单个客户的隐私信息。

5、开发者在没有考虑UDP报文放大问题时，不要过于着急推出自己的UDP协议。UPnP协议应当经过适当的标准化和审查。

6、我们倡导终端用户使用如上脚本在他们的网络中扫描支持UPnP的设备，然后决定哪些设备可以连接互联网。

此外，我们推出了一个在线检查网站。如果你想知道你的公共IP地址是否暴露存在漏洞的SSDP服务，你可以访问[此链接](https://badupnp.benjojo.co.uk/)进行检测。

令人遗憾的是，此次攻击中我们看到大量路由器来自于中国、俄罗斯以及阿根廷，我们对这些地方的互联网状况不是特别了解。

<br>

**八、总结**

****

我们的客户能够完全免疫此类SSDP攻击以及其他的L3放大攻击，我们的[基础设施](https://blog.cloudflare.com/how-cloudflares-architecture-allows-us-to-scale-to-stop-the-largest-attacks/)足以抵御此类这些攻击，客户不需要做特别的操作。不幸的是，对其他互联网公众而言，这种大规模的SSDP攻击可能是一个严峻的问题。我们应该建议ISP在内部网络中禁用IP伪装技术，提供BGP Flowspec功能，配置netflow数据收集选项。

感谢Marek Majkowski以及Ben Cartwright-Cox的辛勤劳动成果。
