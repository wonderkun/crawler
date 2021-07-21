> 原文链接: https://www.anquanke.com//post/id/151761 


# SSH 暴力破解趋势：从云平台向物联网设备迁移 | 云鼎实验室出品


                                阅读量   
                                **141332**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01356e4fb8041c44c3.jpg)](https://p1.ssl.qhimg.com/t01356e4fb8041c44c3.jpg)



## 导语

近日，腾讯云发布2018上半年安全专题系列研究报告，该系列报告围绕云上用户最常遭遇的安全威胁展开，用数据统计揭露攻击现状，通过溯源还原攻击者手法，让企业用户与其他用户在应对攻击时有迹可循，并为其提供可靠的安全指南。上篇报告从 DDoS 攻击的角度揭示了云上攻击最新趋势，本篇由同一技术团队云鼎实验室分享：「SSH 暴力破解趋势：从云平台向物联网设备迁移 」， 以下简称《报告》。



## 一、基本概念

### SSH 暴力破解是什么？

SSH 暴力破解是一种对远程登录设备（比如云服务器）的暴力攻击，该攻击会使用各种用户名、密码尝试登录设备，一旦成功登录，便可获得设备权限。本篇报告内容云鼎实验室从攻击现状、捕获样本、安全建议等方面展开。

近些年，新出现了众多入侵系统的手法，比如 Apache Struts2 漏洞利用、Hadoop Yarn REST API 未授权漏洞利用，但是古老的 SSH 暴力破解攻击手段不仅没有消亡，反而愈演愈烈。云鼎实验室在本篇《报告》中，对 SSH 暴力破解攻击从攻击者使用的攻击字典、攻击目标、攻击源地域分布、恶意文件等维度，以及捕获的攻击案例进行趋势分析。由于虚拟货币的兴起，攻击者不再仅仅利用通过 SSH 暴力破解控制的设备来进行 DDoS 攻击，还用来挖矿，牟取利益。

### 为什么 SSH 暴力破解攻击手段愈演愈烈？

主要原因：

➢ SSH 暴力破解工具已十分成熟，比如 Medusa、 Hydra 等，且下载渠道众多；

➢ SSH 暴力破解已经成为恶意程序（如 Gafgyt[1]、 GoScanSSH[2][3] 等）自动传播的主要方式之一。

大部分自动化 SSH 暴力破解攻击并不检测设备类型，只要发现开放的 SSH 服务就会进行攻击。由于这种无差别自动化攻击，开放 SSH 服务的 Linux 服务器（包括传统服务器、云服务器等）、物联网设备等自然就成为主要攻击目标。



## 二、攻击现状分析

### 1. 攻击者所使用的 SSH 暴力破解攻击字典分析

云鼎实验室针对近期统计的 SSH 暴力破解登录数据分析发现：

➢ 接近99%的 SSH 暴力破解攻击是针对 admin 和 root 用户名；

➢ 攻击最常用弱密码前三名分别是 admin、 password、 root，占攻击次数的98.70%；

➢ 约85%的 SSH 暴力破解攻击使用了 admin / admin 与 admin / password 这两组用户名密码组合。

[![](https://p2.ssl.qhimg.com/t01f36c61b9ea770867.png)](https://p2.ssl.qhimg.com/t01f36c61b9ea770867.png)

△ 表1 攻击者所使用的 SSH 暴力破解攻击字典 Top 20

### 2. SSH 暴力破解攻击目标分析

云鼎实验室通过分析数据发现， SSH 暴力破解攻击目标主要分为 Linux 服务器（包括传统服务器、云服务器等）与物联网设备。

1）Linux 服务器（包括传统服务器、云服务器等）

➢ 大部分攻击都是针对 Linux 服务器默认管理账号 root，攻击者主要使用 admin、 root、 123456等常见弱密码进行暴力破解；

➢ 少部分攻击是针对 tomcat、 postgres、 hadoop、 mysql、 apache、 ftpuser、 vnc 等 Linux 服务器上常见应用程序使用的用户名。攻击者不仅使用常见通用弱密码，还会将用户名当作密码进行攻击。

➢ 另外，还发现针对 CSGO 游戏服务端（目前该服务端程序只能在 Linux 系统上安装）[4]的默认用户名 csgoserver 的攻击。攻击者同样也是使用常见弱密码进行暴力破解。

2）物联网设备

根据攻击者所使用的 SSH 暴力破解攻击字典分析结果，大量 SSH 暴力破解攻击使用了 admin / admin 与 admin / password 这两组用户名密码组合，而这两组用户名密码组合，正是路由器最常用的默认用户名密码组合[5][6]。由此可知，使用上述默认配置的路由器设备已成为攻击的主要目标。

除此之外，还发现针对特定物联网设备（比如摄像头、路由器、防火墙、树莓派等）的 SSH 暴力破解攻击。这些攻击使用了表2所示的用户名密码组合。

[![](https://p5.ssl.qhimg.com/t01b8471c99bffd5f57.png)](https://p5.ssl.qhimg.com/t01b8471c99bffd5f57.png)△ 表2 特定物联网设备的用户名密码组合

### 3. SSH 暴力破解攻击次数地域分布情况

云鼎实验室最近统计到来自160多个国家的攻击，其中来自荷兰的攻击最多，占总攻击次数的76.42%；接着是来自保加利亚的攻击，占10.55%；排第三的是中国，占3.89%。由于欧洲部分国家，比如荷兰、保加利亚，VPS 监管宽松[7]，攻击者可以很方便地租用到 VPS 进行大量攻击。

[![](https://p2.ssl.qhimg.com/t0173b6f0fb72e9a8f2.jpg)](https://p2.ssl.qhimg.com/t0173b6f0fb72e9a8f2.jpg)

来自国内的攻击中，接近60%的攻击来自于互联网产业发达的广东、北京、上海。

[![](https://p5.ssl.qhimg.com/t0179cb15ce3b4cf171.jpg)](https://p5.ssl.qhimg.com/t0179cb15ce3b4cf171.jpg)

### 4. 发起 SSH 暴力破解攻击的源 IP 地域分布情况

根据对攻击源中各国的 IP 数量统计，中国的攻击源 IP 最多，占26.70%，巴西、越南、美国不相上下。

[![](https://p2.ssl.qhimg.com/t019b32f4c24214c080.jpg)](https://p2.ssl.qhimg.com/t019b32f4c24214c080.jpg)

国内的攻击源 IP 分布广泛，全国各地都有，且地域分布较为平均，没有出现攻击源 IP 数量特别多的省市，这是因为攻击者为了隐藏自己真实位置，躲避追踪，使用了不同地区的 IP 进行攻击。

[![](https://p1.ssl.qhimg.com/t0145f7b4ec46c85276.jpg)](https://p1.ssl.qhimg.com/t0145f7b4ec46c85276.jpg)

### 5. 植入恶意文件所使用的命令分析

分析发现，攻击者最爱搭建 HTTP 服务器来用于恶意文件的植入，因此自动化暴力破解攻击成功后，常使用 wget / curl 来植入恶意文件。不过，相比 curl 命令，Linux 的命令 wget，适用范围更广，因此攻击者会首选 wget 命令来植入恶意文件。

而少部分攻击者还会在 HTTP 服务器上，同时运行 TFTP 和 FTP 服务，并在植入恶意文件时，执行多个不同的植入命令。这样即使在 HTTP 服务不可用的情况下，仍可以通过 TFTP 或 FTP 植入恶意文件。

[![](https://p1.ssl.qhimg.com/t01c491ef2fd4b056f3.jpg)](https://p1.ssl.qhimg.com/t01c491ef2fd4b056f3.jpg)

### 6. 恶意文件服务器地域分布情况

由于采集的大部分节点在国内，因此统计到67%的恶意文件服务器部署在国内，且没有完全集中在互联网产业发达的地区，广东、上海占比就比较少。这是因为这些地区对服务器监管严格，因此攻击者选用其他地区的服务器存放恶意文件。

[![](https://p1.ssl.qhimg.com/t01238f4698b6b0c561.jpg)](https://p1.ssl.qhimg.com/t01238f4698b6b0c561.jpg)

[![](https://p4.ssl.qhimg.com/t0109d3aae271d55abe.jpg)](https://p4.ssl.qhimg.com/t0109d3aae271d55abe.jpg)

### 7. 植入的恶意文件分析

对攻击后直接植入的恶意文件进行文件类型识别，超过50%的文件是 ELF 可执行文件；在这些 ELF 文件当中，x86 CPU 架构的文件最多，有63.33%；除x86和x64 CPU 架构的 ELF 文件以外，还有适用于 ARM 和 MIPS CPU 架构的 ELF 文件。而其余恶意文件的文件类型有 Shell 脚本、Perl、 Python 等（详情见下图）。因为 SSH 暴力破解是针对 Linux 系统的攻击，因此攻击成功后多数都是植入 ELF 可执行文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015e2d62e5ed1d7a02.jpg)

[![](https://p0.ssl.qhimg.com/t0159e2a8625870960d.jpg)](https://p0.ssl.qhimg.com/t0159e2a8625870960d.jpg)

植入的恶意文件中反病毒引擎检测到病毒占比43.05%，病毒文件中属 DDoS 类型的恶意文件最多，接近70%，包括 Ganiw、 Dofloo、 Mirai、 Xarcen、 PNScan、 LuaBot、 Ddostf 等家族。另外，仅从这批恶意文件中，就发现了比特币等挖矿程序占5.21%，如下图所示：

[![](https://p2.ssl.qhimg.com/t016751ffb253312be6.jpg)](https://p2.ssl.qhimg.com/t016751ffb253312be6.jpg)

[![](https://p4.ssl.qhimg.com/t01263dd0ec2758eb9f.jpg)](https://p4.ssl.qhimg.com/t01263dd0ec2758eb9f.jpg)



## 三、案例分析

### 1. SSH 暴力破解攻击案例整体流程

云鼎实验室于2018年06月10日7点12分发现的一次 SSH 暴力破解攻击，攻击者攻击成功后进行了以下操作：

[![](https://p0.ssl.qhimg.com/t010e67fad0571558f6.jpg)](https://p0.ssl.qhimg.com/t010e67fad0571558f6.jpg)

### 2. 恶意样本1分析[11][12] ——「DDoS 家族 Ddostf 的僵尸程序」

攻击者植入的第一个恶意样本是 DDoS 家族 Ddostf 的僵尸程序。简要的样本信息如下：

➢ 样本对应URL：http://210.*.*.165:22/nice

➢ 样本的MD5值：0dc02ed587676c5c1ca3e438bff4fb46

➢ 文件类型：ELF 32-bit LSB executable,  Intel 80386,  version 1 (GNU/Linux),  statically linked,  for GNU/Linux 2.6.32,  not stripped

➢ C&amp;C地址：112.*.*.191:88

➢ 该样本共有6个功能函数，详情如下表3：

[![](https://p3.ssl.qhimg.com/t017fc0fe0c400c20f7.png)](https://p3.ssl.qhimg.com/t017fc0fe0c400c20f7.png)

△ 表3 恶意样本1 的功能函数

➢ 该样本具有7种 DDoS 攻击类型，13个 DDoS 攻击函数，详情如下表：

[![](https://p4.ssl.qhimg.com/t011bd27264799991b3.png)](https://p4.ssl.qhimg.com/t011bd27264799991b3.png)

△ 表4 恶意样本1 的 DDoS 攻击类型

### 3. 恶意样本2分析 ——「一路赚钱」挖矿恶意程序」

攻击者植入的第二个恶意样本是挖矿相关的。由于虚拟货币的兴起，攻击者开始利用被控制的设备进行挖矿来牟取利益。简要的样本信息如下：

植入的恶意样本是「一路赚钱」的64位 Linux 挖矿恶意程序部署脚本，脚本执行后会植入「一路赚钱」 64位 Linux 版本的挖矿恶意程序压缩包，并解压到 /opt 目录下，然后运行主程序 mservice，注册为 Linux 系统服务，服务名为 YiluzhuanqianSer。该文件夹中有三个可执行文件 mservice / xige / xig，均被反病毒引擎检测出是挖矿类的恶意样本。根据配置文件可知， mservice 负责账号登录/设备注册/上报实时信息，而xige 和 xig负责挖矿， xige 挖以太币 ETH，xig 挖门罗币 XMR。

➢ 样本的MD5值：6ad599a79d712fbb2afb52f68b2d7935

➢ 病毒名：Win32.Trojan-downloader.Miner.Wskj

➢ 「一路赚钱」的64位 Linux 版本挖矿恶意程序文件夹内容如下：

[![](https://p0.ssl.qhimg.com/t011f731b9fef722c50.png)](https://p0.ssl.qhimg.com/t011f731b9fef722c50.png)

△ 表5 「一路赚钱」的64位 Linux 版本挖矿恶意程序文件夹内容

➢ 挖矿使用的矿池地址：

xcn1.yiluzhuanqian.com:80

ecn1.yiluzhuanqian.com:38008



## 四、总结与建议

### 1. 整体现状
- 由于物联网的蓬勃发展，设备数量暴增，因此物联网设备渐渐成为主要的攻击目标。
- 过去攻击者使用大量的弱密码进行攻击，而现在则使用少量的默认密码，对特定设备进行攻击。
- 过去更多是攻击者利用自动化 SSH 暴力破解工具发动攻击，植入僵尸程序，组建自己的僵尸网络。而现在僵尸程序可以自己发动攻击，自动传播感染新的设备，逐步壮大僵尸网络。
- 过去攻击者更多是利用已控制的服务器进行攻击，而现在攻击者会租用国外监管宽松的 VPS 进行大量的攻击。
- 攻击成功后的植入的恶意样本还是以 DDoS 家族为主，并开始出现挖矿程序[13]。
### 2. 未来趋势
- 随着联网设备的不断增多[14]，SSH 暴力破解攻击会越来越多；
- 攻击者继续租用廉价国外 VPS，躲避监管，进行大规模的攻击；
- 日益增多的云服务依旧会被攻击者锁定，但攻击的整体趋势将从云平台向物联网设备迁移，物联网设备将成为最主要攻击目标。
### 3. 安全建议
- 技术型用户，可根据下列建议提高 SSH 服务的安全性：- 普通用户可选择腾讯云云镜专业版提高云服务器的整体安全性。
腾讯云云镜基于腾讯安全积累的海量威胁数据，利用机器学习为用户提供黑客入侵检测和漏洞风险预警等安全防护服务，主要包括密码破解拦截、异常登录提醒、木马文件查杀、高危漏洞检测等安全功能，解决当前服务器面临的主要网络安全风险，帮助企业构建服务器安全防护体系，防止数据泄露，为企业有效预防安全威胁，减少因安全事件所造成的损失。

第一篇专题报告阅读链接：

[https://www.anquanke.com/post/id/147700](https://www.anquanke.com/post/id/147700)

参考链接：

[1] [http://www.freebuf.com/articles/wireless/160664.html](http://www.freebuf.com/articles/wireless/160664.html)

[2] [https://threatpost.com/goscanssh-malware-targets-ssh-servers-but-avoids-military-and-gov-systems/130812/](https://threatpost.com/goscanssh-malware-targets-ssh-servers-but-avoids-military-and-gov-systems/130812/)

[3] [https://blog.talosintelligence.com/2018/03/goscanssh-analysis.html](https://blog.talosintelligence.com/2018/03/goscanssh-analysis.html)

[4] [http://www.csteams.net/Servers/](http://www.csteams.net/Servers/)

[5] [https://portforward.com/router-password/tp-link.htm](https://portforward.com/router-password/tp-link.htm)

[6] [https://www.lifewire.com/netgear-default-password-list-2619154](https://www.lifewire.com/netgear-default-password-list-2619154)

[7] [https://www.lehaigou.com/2017/1219209295.shtml](https://www.lehaigou.com/2017/1219209295.shtml)

[8] [https://www.leiphone.com/news/201801/GLmAX9VzPhN17cpr.html](https://www.leiphone.com/news/201801/GLmAX9VzPhN17cpr.html)

[9] [http://www.freebuf.com/articles/paper/162404.html](http://www.freebuf.com/articles/paper/162404.html)

[10] [https://coinidol.com/ionchain-future-of-iot-mining-tool-for-all-things/](https://coinidol.com/ionchain-future-of-iot-mining-tool-for-all-things/)

[11] [http://blog.malwaremustdie.org/2016/01/mmd-0048-2016-ddostf-new-elf-windows.html](http://blog.malwaremustdie.org/2016/01/mmd-0048-2016-ddostf-new-elf-windows.html)

[12] [https://larry.ngrep.me/2018/01/17/malwaremustdie-ddostf-analysis/](https://larry.ngrep.me/2018/01/17/malwaremustdie-ddostf-analysis/)

[13] [http://www.freebuf.com/articles/network/161986.html](http://www.freebuf.com/articles/network/161986.html)

[14] [http://www.freebuf.com/articles/terminal/128148.html](http://www.freebuf.com/articles/terminal/128148.html)

审核人：yiwang   编辑：边边
