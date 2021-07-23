> 原文链接: https://www.anquanke.com//post/id/83710 


# 网络侦查(Recon)技术入门


                                阅读量   
                                **160027**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://resources.infosecinstitute.com/snort-network-recon-techniques/](http://resources.infosecinstitute.com/snort-network-recon-techniques/)

译文仅供参考，具体内容表达以及含义原文为准

在这篇文章中,我们将学习一些流行的网络侦查技术,以及实践编写一些Snort的检测规则。

练习一:网络发现

Nmap是至今为止世界上信息安全领域中最受欢迎的工具之一。这种受欢迎的程度可以归因于很多因素。其中之一当然是因为它的高效。虽然一般介绍Nmap都是作为端口扫描器,但它远远不止这些功能。我们将使用这个来练习基本的网络发现。下面的例子中,我们进行了一次ping扫描,用于发现网络中的设备。你的实验环境可能是其他的网络范围,因此注意不要输错你的实际目标网络范围。

```
nmap - sp 192.168.x.0/24
```

[![](https://p0.ssl.qhimg.com/t018475e3ab81427120.png)](https://p0.ssl.qhimg.com/t018475e3ab81427120.png)

在这个例子中,我们可以看到似乎有六个存活主机(你得到的结果可能不同,这取决于你的实验环境)。这就是一次最基本的Nmap扫描。接下来我们将Snort修改为IDS模式,通过sudo gedit /etc/snort/rules/local.rules来编辑相应规则,然后启动它:



```
sudo snort -A console -q -c /etc/snort/snort.conf -i eth0
```

现在再次进行Nmap ping扫描:



```
nmap - sp 192.168.x.0/24
```

你有没有在Snort中看到警报信息?没有?我们可以看下Nmap具体做了什么,我们可以运行相同的命令,增加一个-packet-trace选项。这个选项有利于我们学习各种不同的Nmap扫描方式,它会将Nmap发送的所有请求和收到的响应都输出到屏幕上。我们在终端中输入这条命令:

```
nmap -sp 192.168.95.0/24 -packet-trace
```

[![](https://p2.ssl.qhimg.com/t01138a3fa3895f4b13.png)](https://p2.ssl.qhimg.com/t01138a3fa3895f4b13.png)

如图所示,我们可以看到Nmap发送的是ARP请求而不是ping所使用的ICMP。这是因为你扫描的是实验环境中的内部网络,Nmap足够聪明,它认为在这种情况下ARP就足够工作了。我们接着向下翻,会看到来自网络上的机器的响应信息,如图:

[![](https://p2.ssl.qhimg.com/t0146c1d6f2c9fab220.png)](https://p2.ssl.qhimg.com/t0146c1d6f2c9fab220.png)

如果你使用以下命令强制Nmap使用ping:

这些选项告诉Nmap使用ICMP ping并且禁用ARP。检查你的Snort输出,我们会看到这样的结果:

[![](https://p0.ssl.qhimg.com/t015eb06181be2251ba.png)](https://p0.ssl.qhimg.com/t015eb06181be2251ba.png)

这里可能会有一个假阳性问题,因为当前的Snort规则会对所有的ping进行警报,这样正常的ICMP请求也会被误报。比如这样:

[![](https://p4.ssl.qhimg.com/t0113888544c3958a81.png)](https://p4.ssl.qhimg.com/t0113888544c3958a81.png)

因此我们需要筛选出Nmap的ping不同于正常ping的地方(也就是进行指纹识别),我们可以使用wireshark捕获一些流量,然后对其进行分析

[![](https://p4.ssl.qhimg.com/t010d743e2595fe63dd.png)](https://p4.ssl.qhimg.com/t010d743e2595fe63dd.png)

我们使用Nmap制造一部分ping流量



```
nmap -sP 192.168.x.0/24 –-disable-arp-ping
```

然后在你的其他机器上发送一些正常的ping流量



```
ping 192.168.x.x
```

然后回到wireshark停止捕获,对流量进行过滤以便于分析



```
ip.dst==192.168.x.x &amp;&amp; icmp
```

过滤之后的结果应该是这样

[![](https://p4.ssl.qhimg.com/t011ad5663be9049dd2.png)](https://p4.ssl.qhimg.com/t011ad5663be9049dd2.png)

我们可以看到,正常ping的长度是60,而Nmap发送的是74;并且Nmap发送的 ICMP Echo请求包中没有payload数据。我们可以基于这些修改我们的Snort规则:



```
icmp any any -&gt; $HOME_NET any (msg:”Possible Nmap ping sweep”; dsize:0; sid:1000005; rev:1;)
```

之后我们再次进行上述测试,我们将会看到正确的运行结果。

练习二:使用Nmap进行端口扫描

我们使用如下命令进行基本的TCP扫描:



```
nmap -sT 192.168.x.x –-packet-trace
```

你应该可以再结果中看到一系列开放的端口,这些端口是你的目标服务器上所开放的,比如21是ftp端口,15是smtp端口,53是dns端口。

现在试着进行一次TCP连接扫描,使用如下命令:



```
nmap -sT 192.168.x.y,z
```

需要注意的是,Nmap并不是试图扫描所有端口。默认值会扫描常用的1000个端口,比如web服务所使用的80端口

[![](https://p4.ssl.qhimg.com/t01dc37cd08a45340b3.png)](https://p4.ssl.qhimg.com/t01dc37cd08a45340b3.png)

如果我们要针对这种扫描进行Snort规则的编写,比如我们要检测telnet所使用的23端口,我们可以使用这样的规则:



```
tcp any any -&gt; $HOME_NET 23 (msg:”TCP Port Scanning”; sid:1000006; rev:1;)
```

之后如果你对目标服务器进行扫描



```
nmap -sT 192.168.x.x
```

在Snort中你应该会看到这些:

[![](https://p0.ssl.qhimg.com/t016a052ba7ba334a34.png)](https://p0.ssl.qhimg.com/t016a052ba7ba334a34.png)

针对端口扫描的另一种报警方式是根据单位时间内的请求数量进行识别。我们可以使用Snort德尔detection_filter 规则选项,例如使用这样的规则:



```
tcp any any -&gt; $HOME_NET any (msg:”TCP Port Scanning”;detection_filter:track by_src, count 30, seconds 60; sid:1000006; rev:2;)
```

这条规则的意思是当检测到60秒内有超过30次TCP连接时进行报警

接下来我们注释条其他的规则,避免干扰,再次尝试扫描,我们只扫描21端口:



```
nmap -sT 192.168.x.x -p 21
```

在Snort中应该不会有报警信息

我们再次进行一次完整的扫描:



```
nmap -sT 192.168.x.x
```

现在Snort应该会输出这样的信息:

[![](https://p2.ssl.qhimg.com/t0164605b77d303c8ce.png)](https://p2.ssl.qhimg.com/t0164605b77d303c8ce.png)

很明显,我们的规则生效了,但看起来警报信息太多了,我们需要做一下优化,我们可以这样修改规则,添加如下语句:



```
event_filter gen_id 1, sig_id 1000006, type limit, track by_src, count 1, seconds 60
```

就像这样

[![](https://p3.ssl.qhimg.com/t0126794f062fa9f752.png)](https://p3.ssl.qhimg.com/t0126794f062fa9f752.png)

这条规则的意思是对于 sid为1000006的警报每60秒只输出一次,我们重新运行Snort,再次进行扫描,这次应该会是如下输出结果

[![](https://p5.ssl.qhimg.com/t016057877a532db4c1.png)](https://p5.ssl.qhimg.com/t016057877a532db4c1.png)

很好,没有太多的输出干扰精力,这就是我们要的结果。

练习三:隐蔽扫描

第一步——时间

Nmap是非常快的扫描器,这是优点也是缺点,因为在很短的时间内发送大量数据包会被IDS所识别。

当然Nmap本身也提供有一些用于调节速度的选项,我们可以使用—T来进行制定,例如这条命令:



```
nmap -sT 192.168.x.x –p 80,135 –T sneaky
```

注意这次扫描的时间(例子使用了大概45秒):

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bd482d63fb7b1fce.png)

如果我们使用insane类型,这会快得多,但很明显,也更容易被识别。除此之外,我们也可以-scan-delay来指定扫描延迟时间,例如使用这样的命令延时5秒:



```
nmap –sT 192.168.x.x –p 80,135 –scan-delay 5s
```

两个端口的5秒以及一个初始延迟5秒,用时应该是在15秒左右

我们也可以指定单位为毫秒,例如这样:



```
nmap –sT 192.168.x.x –p 80,135 –scan-delay 5ms
```

这是5毫秒,它完成得非常快,实际速度可能会受网络环境以及配置的影响。

第二步——隐蔽的TCP扫描

Nmap提供了一些方式用于隐蔽TCP扫描,例如SYN扫描:



```
nmap –sS 192.168.x.x
```

此外还有其他一些方式,都是利用了TCP协议中的微妙行为实现

针对这类扫描的指纹识别非常容易,只需要通过wireshark进行简单的流量分析,我们制造这些流量



```
nmap -sF 192.168.x.x
nmap -sX 192.168.x.x
nmap –sN 192.168.x.x
```



然后过滤出这些流量



```
ip.src==192.168.x.x &amp;&amp; ip.dst==192.168.yy &amp;&amp; tcp.port eq 21
```

可以在结果中看到我们的扫描流量

[![](https://p4.ssl.qhimg.com/t01bce769f4d8084843.png)](https://p4.ssl.qhimg.com/t01bce769f4d8084843.png)

通过对这些流量进行分析,我们应该能够写出这样的检测规则:



```
tcp any any -&gt; $HOME_NET any (msg:”Nmap XMAS Tree Scan”; flags:FPU; sid:1000007; rev:1;)
```

使用这条规则,然后我们再次进行扫描



```
nmap -sX 192.168.x.x -p 80
```

在Snort中我们会看到这样的信息:

[![](https://p0.ssl.qhimg.com/t013555ca3be12db29d.png)](https://p0.ssl.qhimg.com/t013555ca3be12db29d.png)

步骤三——伪装扫描

一般的伪装扫描会伪造源地址,这使得日志难以分析,例如我们使用这样的扫描命令:



```
nmap -sS 192.168.x.x -D10.10.10.10,11.11.11.11,1.1.1.1,8.8.8.8
```

如果你使用wireshark捕获流量,你得到的结果会是这样的

[![](https://p1.ssl.qhimg.com/t01649540b6298e5cf7.png)](https://p1.ssl.qhimg.com/t01649540b6298e5cf7.png)

很明显这些信息都是伪造的

通过分析,我们可以写出这样的检测规则:



```
tcp !192.168.x.0/24 any -&gt; $HOME_NET 80 (msg:”Suspicious IP address”; sid:1000008; rev:1;)
```

之后如果再次进行这样的扫描,Snort中会输出如下信息:

[![](https://p0.ssl.qhimg.com/t014a2d66d419896b60.png)](https://p0.ssl.qhimg.com/t014a2d66d419896b60.png)

以上就是一些基于Snort规则所做的侦查检测技术,如果我们能够熟练的定制相应的规则,我们就可以更好地做网络侦查。
