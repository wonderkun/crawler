> 原文链接: https://www.anquanke.com//post/id/96967 


# TheMoon : 一个僵尸网络的老皇历和新变种


                                阅读量   
                                **118501**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01a05d50f75ff45a6a.jpg)](https://p3.ssl.qhimg.com/t01a05d50f75ff45a6a.jpg)

> TheMoon 是一个恶意代码家族的代号。早在2014年2月，该恶意代码家族就引起了安全研究人员的普遍关注。在当时，TheMoon是一个针对 Linksys 路由器的、有类似蠕虫式传播行为的僵尸网络。由于其感染传播能力较强，安全社区里的讨论较多。

2014～2017年期间，又陆续有各安全厂商对TheMoon恶意代码家族做了分析。报告反应了当时 TheMoon 家族的演化情况。

从2017年开始，我们也对 TheMoon 家族做了持续跟踪，并注意到以下的新发现：
- 感染阶段： TheMoon 集成了最近的一组漏洞利用代码，提高其感染能力；
- 运营阶段： TheMoon 的代理网络，由正向代理改为反向代理，避免被安全研究人员探测度量；
- 样本特征： TheMoon 开始使用压缩外壳，提高安全研究人员分析的难度
下文仅仅是我们对 TheMoon 恶意代码家族监控结果的概括描述，详细的技术分析文档可见 [TheMoon-botnet.pdf](http://blog.netlab.360.com/file/TheMoon-botnet.pdf)



## 2017年以前的 TheMoon

2014-02-13 ，这是我们能查到的 TheMoon 相关最早记录。当时，SANS 安全研究机构的博士 Johannes B. Ullrich [报告发现](https://isc.sans.edu/forums/diary/Linksys+Worm+TheMoon+Captured/17630) 了该恶意代码，并在随后给出了[更新](https://isc.sans.edu/diary/Linksys+Worm+%22TheMoon%22+Summary%3A+What+we+know+so+far/17633) 。TheMoon家族的一些关键特点，在最初被发现的这个阶段就已经确定下来了：
- 攻击目标：最初是 Linksys E1000 系列路由器，后续发展也是以 IoT 设备、特别是家用路由器为主。设备目标常见是 MIPS 架构
- 蠕虫式的感染传播：被感染的设备，会在一个较短的时间窗口期内提供二进制下载。这种蠕虫式的感染，这使得其传播能力大大增强
- 简单的自我保护：会设定 iptables 规则限制漏洞利用端口的访问，仅允许作者控制的几个IP地址所在地址段访问，减少被其他攻击者利用相同漏洞的风险
- 命名来源：样本文件内嵌了几张图片，加上文件中的一些其他字符串 “lunar”, “moon”, “planets”，这些共同的信息指向一部2009年的电影 [“Moon”](http://www.imdb.com/title/tt1182345/)，这是这个家族被命名为 TheMoon 的原因。
由于该恶意代码家族被定位是蠕虫，这引起了安全社区的广泛讨论。几天之内，相关的设备漏洞和利用代码就被各大安全厂商收录，例如 [securityfocus](https://www.securityfocus.com/bid/65585)， [packetstormsecurity](https://packetstormsecurity.com/files/125253), [flexerasoftware](https://secuniaresearch.flexerasoftware.com/advisories/56994)， [vulnerabilitycenter](https://www.vulnerabilitycenter.com/#!vul=43986)， [exploit-db](https://www.exploit-db.com/exploits/31683/)， [IBM X-force](https://exchange.xforce.ibmcloud.com/vulnerabilities/91196?spm=0.0.0.0.SsE6B5)，等等。

2015-07-16，阿里安全的谢君，在 [解密“智魁”攻击行动——针对路由器蠕虫攻击事件分析报告](https://security.alibaba.com/blog/blog?id=26&amp;type=security) 中，分析了该恶意代码家族当时的变种。这个阶段 TheMoon 家族表现出来的新特征包括：
- socks代理：开始利用被感染节点搭建 Socks 代理网络；上述代理网络是主动式的，被感染节点上开启的代理节点有特征可循，文章中根据该特征，对全网扫描并给出了度量；
- 感染手段：开始使用华硕路由器漏洞 [CVE-2014-9583](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-9583)，UDP 9999 ，以及 [TP-Link路由器漏洞](https://sekurak.pl/tp-link-httptftp-backdoor/?spm=0.0.0.0.aOpRH8)。2014年版本所使用的原有 Linksys 漏洞仍然在利用。
- 文中还列出了若干打码后的 C2 服务器IP地址
虽然文章中通篇没有提及 TheMoon 的名字，但是恶意代码的二进制特征一致，可以判定是 TheMoon 家族。另外，文章中还将攻击行为追溯到具体人，但是这部分的归因过程没有给出具体分析过程，故而这部分的结论待考。

2016-10-20 Fortinet 的 Bing Liu 在 [TheMoon A P2P botnet targeting Home Routers](https://blog.fortinet.com/2016/10/20/themoon-a-p2p-botnet-targeting-home-routers) 中分析了当时的 TheMoon 恶意代码变种。文中提及了一些新特性：
- P2P 特性：代码中集成了P2P 特性（但不成熟，也未启用）
- C2通信协议：详细的分析了恶意代码的 C2 通信协议
- 下载服务器：hxxp://78.128.92.137/.nttpd
<li>若干硬编码的 NTP IP 地址：
<ul>
- 207.46.232.182 (未显式标注)
- 82.68.206.125
- 194.25.252.5
- 129.6.15.28
- 129.6.15.28- 185.53.8.22 (未显式标注)
- 185.56.30.189
- 217.79.182.212
- 85.114.135.20
- 95.213.143.220
- 46.148.18.154
值得一提是，尽管这份恶意代码中集成了 P2P 特性，但相关代码是不成熟的，未能遵循应用密码学最佳实践，存在被接管的可能性。这部分代码特性并未启用，作者与 bot 的通信仍主要主要基于硬编码的 C2 IP 地址。



## 2017年以来我们观测到的 TheMoon 家族

从 2017年4月 以来，我们开始持续观察到 TheMoon 家族。我们监控到的新变化包括：
- 样本特征：TheMoon 开始使用压缩外壳，提高安全研究人员分析的难度
- 感染手段：集成了至少 6 种 IoT 设备漏洞利用手段，扩大感染基数
- 代理网络：从正向改为反向。感染节点通过咨询上联节点得知需要访问的网页和参数，感染节点上不再直接开放端口。这样我们也无法通过全网扫描的方式来度量僵尸网络的规模。
- 代理流量：代理网络中流传的流量大致分为有明文和密文两部分，流量均不高。明文部分，经人肉筛选，和色情、赌博、挖矿等内容有关，另有一小部分看起来像门户网站；密文部分的流量推测与电商或者在线邮箱有关。时间分布不明显，似乎24小时都有流量发生。
- P2P 机制：仍然存在，仍然存在被接管可能，仍然没有启用
C2 IP 地址方面，我们累计观察到以下 IP 地址被攻击者以年为单位长期占用：
- 149.202.211.227
- 173.208.219.26
- 173.208.219.42
- 173.208.219.50
- 173.208.219.58
- 185.53.8.22
- 185.56.30.189
- 185.56.30.189
- 208.110.66.34
- 217.79.182.212
- 46.148.18.154
- 69.197.128.34
- 85.114.135.20
- 91.215.158.118
- 95.213.143.220
值得一提的是之前其他文章中披露的 C2 IP 地址已经被作者放弃使用，但是 185.53.8.22 这个IP地址没有被显式披露，作者就一直使用并未放弃。

感染过程中至少使用了6种 IoT 设备漏洞利用，相关的设备类型和漏洞利用如下：
- Linksys E-series 的 [漏洞利用](https://www.exploit-db.com/exploits/31683/) ，这是 2014 年首次被批露时使用的漏洞
- ASUS WRT UDP 9999的 [漏洞利用](https://github.com/jduck/asus-cmd)，这是 TheMoon从2015年至2017年主要使用的漏洞利用
<li>D-Link 850L的 [漏洞利用](https://blogs.securiteam.com/index.php/archives/3364)
</li>
<li>D-Link 815的 [漏洞利用](https://github.com/Cr0n1c/dlink_shell_poc/blob/master/dlink_auth_rce)
</li>
<li>VIVOTEK Network Cameras的 [漏洞利用](http://blog.cal1.cn/post/An%20easy%20way%20to%20pwn%20most%20of%20the%20vivotek%20network%20cameras)
</li>
<li>D-Link DIR-890L D-Link DIR-645的 [漏洞利用](http://www.devttys0.com/2015/04/hacking-the-d-link-dir-890l/)
</li>


## 详细技术分析文档

[TheMoon-botnet.pdf](http://blog.netlab.360.com/file/TheMoon-botnet.pdf)

#### IoC

样本MD5和下载URL

```
2017-04-02 7bca40bba278b0021a87bcbc35b2e144  hxxp://domstates.su/nmlt1.sh  
2017-04-02 70461da8b94c6ca5d2fda3260c5a8c3b  hxxp://domstates.su/.nttpd  
2017-04-02 c8f17d7403ac5ff2896a713a7175ed19  hxxp://domstates.su/archi.txt  
2017-04-06 bc56979a0b381a791dd59713198a87fb  hxxp://domstates.su/nmlt1.sh  
2017-04-06 bc56979a0b381a791dd59713198a87fb  hxxp://domstates.su/archi.txt  
2017-04-09 11f060ffd8a87f824c1df3063560bc9e  hxxp://domstates.su/.nttpd,19-mips-le-t1  
2017-04-09 c0c1d535d5f76c5a69ad6421ff6209fb  hxxp://domstates.su/.nttpd,17-mips-be-t2  
2017-04-09 4d90e3a14ebb282bcdf3095e377c8d26  hxxp://domstates.su/.nttpd,18-arm-le-t1  
2017-08-11 106d9eb6a7c14f4722898b89ccacb17e  hxxp://domstates.su/nmlt1.sh  
2017-08-11 6f2fabf40ad39a5738e40dbe2c0a1b53  hxxp://domstates.su/.nttpd,20-mips-le-t1  
2017-08-11 b731e5136f0ced58618af98c7426d628  hxxp://domstates.su/.nttpd,19-arm-le-t1  
2017-10-03 9c79b0a54e70cf0a65ba058e57aee6f1  hxxp://domstates.su/nmlt1.sh  
2017-10-03 27002860c26c2298a398c0a8f0093ef6  hxxp://domstates.su/.nttpd,19-arm-le-t1  
2017-10-03 54631bbc01b934ee3dbcafdc6055599c  hxxp://domstates.su/.nttpd,18-mips-be-t2  
2017-10-05 e2673d513125bcae0865ccf0139cef0c  hxxp://domstates.su/nmlt1.sh  
2017-10-05 b8e16a37997ada06505667575f8577d6  hxxp://domstates.su/.nttpd,19-arm-le-t1  
2017-10-05 98c678ee656325b0aee1fe98f2ca6f55  hxxp://domstates.su/.nttpd,18-mips-be-t2  
2017-10-09 96219e644bf69ff7359ecc5e9687bcd0  hxxp://domstates.su/nmlt1.sh  
2017-10-09 f9d87043d2e99098f35a27237925992f  hxxp://domstates.su/.nttpd,20-arm-le-t1-z  
2017-10-09 089d304877930d3dfe232a2e98e63f6f  hxxp://domstates.su/.nttpd,19-mips-be-t2-z  
2017-10-14 275cc8ed50368fa72e46551e41824683  hxxp://domstates.su/nmlt1.sh  
2017-10-14 7fa47de462e743607eb9a2f93b7193ce  hxxp://domstates.su/.nttpd,20-mips-be-t2-z  
2017-10-16 810ea41f35f9fe40855900db9406d7a0  hxxp://domstates.su/nmlt1.sh  
2017-10-21 dbf24da7b27c12ae65c98675eb435c81  hxxp://domstates.su/nmlt1.sh  
2017-11-12 8ad5b160dd7a976044d6a2dd631efc4b  hxxp://domstates.su/nmlt1.sh  
2017-11-12 20f9f7ae0c6d385b0bedcdd618c478dc  hxxp://domstates.su/.nttpd,21-arm-le-t1-z  
2017-11-12 53494b8867654d06ea1b5aec0ed981c1  hxxp://domstates.su/.nttpd,21-mips-be-t2-z  
2017-11-12 016cc0097560bbbb07b4891256600eb8  hxxp://domstates.su/d8ug.sh  
2017-11-27 2ceb4822e1e0f72e8b88968165d9a99f  hxxp://domstates.su/nmlt1.sh  
2017-11-27 057d56b7de1e9460bd13c5c6eafd4559  hxxp://domstates.su/.nttpd,21-mips-le-t1
```

C2 IP

```
149.202.211.227  
173.208.219.26  
173.208.219.42  
173.208.219.50  
173.208.219.58  
185.53.8.22  
185.56.30.189  
185.56.30.189  
208.110.66.34  
217.79.182.212  
46.148.18.154  
69.197.128.34  
85.114.135.20  
91.215.158.118  
95.213.143.220
```
