> 原文链接: https://www.anquanke.com//post/id/248670 


# 『P2P僵尸网络漏洞研究——mozi』 netgear路由器漏洞复现


                                阅读量   
                                **25491**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01725a7a92867c481f.png)](https://p0.ssl.qhimg.com/t01725a7a92867c481f.png)



## 0x0 前言

> IBM的研究人员指出，Mozi的代码与Mirai及其变体重叠，并重用Gafgyt代码，在过去的一年里迅速“登上王座”，在2019年10月至2020年6月期间观察到的物联网网络攻击流量中占90%。——《新的僵尸物联网攻击流量之王：Mozi》；作者：安全牛

Mozi的传播利用了许多设备的漏洞，其中就包括了CVE-2016-6277，如下图1、图2所示。

[![](https://p5.ssl.qhimg.com/t01c3bfdf7aeecafef2.png)](https://p5.ssl.qhimg.com/t01c3bfdf7aeecafef2.png)

图1

[![](https://p4.ssl.qhimg.com/t01ad9b4a10129c5bbc.png)](https://p4.ssl.qhimg.com/t01ad9b4a10129c5bbc.png)

图2



## 0x1 简介

NETGEAR R6250在1.0.4.6.Beta之前，R6400在1.0.1.18.Beta之前，R6700在1.0.1.14.Beta，R6900，R7000在1.0.7.6.Beta之前，R7100LG在1.0.0.28.Beta之前，R7300DST在1.0.0.46.Beta之前，1.0.1.8.Beta之前的R7900、1.0.3.26.Beta，D6220，D6400，D7000之前的R8000，以及可能的其他路由器，允许远程攻击者通过shell在 cgi-bin/ 的路径中执行任意命令。

以Netgear R7000，版本V1.0.7.02_1.1.93为例，复现CVE-2016-6277。



## 0x2 准备

版本 V1.0.7.02_1.1.93：[http://support.netgear.cn/doucument/More.asp?id=2251](http://support.netgear.cn/doucument/More.asp?id=2251)

调试的程序：httpd

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ebab01af257a0e71.png)

图3



## 0x3 工具

静态分析：IDA<br>
获取文件系统：binwalk



## 0x4 测试环境

Netgear R7000路由器真机测试，可以在某宝上或者某鱼上购买（价格不贵）。



## 0x5 漏洞分析

使用 binwalk -Me R7000-V1.0.7.2_1.1.93.chk 即可解包成功（固件没有加密，可直接分析）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d0a93909c4cbdee7.png)

图4

将要分析的httpd，拖到IDA中分析，并通过CVE给出的部分信息，大概可以知道，漏洞点出现在图5中。在Mozi程序中，也可以分析出，该漏洞是一个命令执行漏洞，那么只需要找system等命令执行函数即可。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0169e8e2e06764a493.png)

图5

sprintf(cmd, “/www/cgi-bin/%s &gt; /tmp/cgi_result”, v41); 通过该命令可以看出，如果将 %s 换成 ;ls 的话，/www/cgi-bin/;ls &gt; /tmp/cgi_result 那么就会将ls的结果存放到 /tmp/cgi_result，假设 /tmp/cgi_result 可以看到ls的结果，那么证明漏洞就存在此处。如图6是通过开放telnet端口进入之后，查看 /tmp/cgi_result，最终发现和预想的一样。如图5所示，如果需要cmd参数执行成功，那么v41参数就必须可以控制。

[![](https://p5.ssl.qhimg.com/t01757395263aa16f26.png)](https://p5.ssl.qhimg.com/t01757395263aa16f26.png)

图6

往上溯源，发现v41的值来自v14的值，而v14的值来自v10。继续溯源。

[![](https://p4.ssl.qhimg.com/t01afd1c3d6ebe1518e.png)](https://p4.ssl.qhimg.com/t01afd1c3d6ebe1518e.png)

图7

如图8可以看到v10的值来自a3，根据多年经验得出a3是路径。

[![](https://p3.ssl.qhimg.com/t01c53dd2312c6605bd.png)](https://p3.ssl.qhimg.com/t01c53dd2312c6605bd.png)

图8

从此处可以看出a3是个url，那么不就是Mozi程序中的，/cgi-bin 了吗？从图8中可以看出 cgi-bin 后面也可以加 ? ，因为v41参数也可以再次出获取到。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013acad87b17a16173.png)

图9



## 0x6 小结

这个漏洞相对来说比较简单，适合入门的大白。如果有兴趣调试的话，可以参考 复现影响79款Netgear路由器高危漏洞 。
