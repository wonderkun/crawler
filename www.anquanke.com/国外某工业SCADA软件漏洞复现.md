> 原文链接: https://www.anquanke.com//post/id/222680 


# 国外某工业SCADA软件漏洞复现


                                阅读量   
                                **150892**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t012357cabbb09731e8.png)](https://p4.ssl.qhimg.com/t012357cabbb09731e8.png)



## 概述

近年来随着网络安全形势的日渐严峻，国内外越来越重视工业信息安全的研究。“等保2.0”专门加入了工业控制系统扩展要求，呼之欲出的“关保”中，大多数涉及国计民生的关键信息基础设施也属于工业控制系统。工业信息安全属于一门混合学科，既要了解工业基本知识，也需要掌握网络安全攻防知识，故该领域人才还存在较大缺口。本文编写的初衷是希望工业领域和网络安全领域能碰撞出更多的火花，以涌现更多的工业信息安全从业人员，故针对SCADA软件的安装和漏洞利用的每一步均采用了大量的图文介绍，以达到科普的目的。



## 一、软件介绍

LAquis SCADA 是LCDS-巴西咨询与发展公司（官网：http//:www.lcds.com.br）开发的一款监视控制和数据采集软件，可在工业控制系统（ICS）或分布式控制系统（DCS）中工作，从数据采集到应用程序开发。<br>
LCDS在巴西的12个州与客户一起使用。除了获得认可的RBC实验室和自动化集成商外，它还应用于以下领域：纺织，机械金属，汽车，食品，农艺师，能源，房地产，引擎，机械加工，木材，检验，液压，化学，铸造，医院，造纸，教学，运输，建筑等…

[![](https://p0.ssl.qhimg.com/t01896f5d41cb4897d5.png)](https://p0.ssl.qhimg.com/t01896f5d41cb4897d5.png)



## 二、漏洞复现环境搭建

### <a class="reference-link" name="2.1%E8%BD%AF%E4%BB%B6%E4%B8%8B%E8%BD%BD%EF%BC%9A"></a>2.1软件下载：

由于LAquis官网不提供历史版本下载，幸好手头还有一枚存货，软件版本为4.1.0.2385，可以用于复现大部分漏洞。<br>
关注我获取软件下载链接^_^。

[![](https://p5.ssl.qhimg.com/t0174218a9a8c40815e.png)](https://p5.ssl.qhimg.com/t0174218a9a8c40815e.png)

### <a class="reference-link" name="2.2%E3%80%81%E8%BD%AF%E4%BB%B6%E5%AE%89%E8%A3%85"></a>2.2、软件安装

LAquis scada支持大多数版本的windows系统，包括（WinXP，Win7 x32，Win7 x64， Windows2000，Windows 2003等）

双击运行安装程序,安装过程，一路点击下一步即可。

[![](https://p1.ssl.qhimg.com/t012a588a2168841e88.png)](https://p1.ssl.qhimg.com/t012a588a2168841e88.png)

[![](https://p5.ssl.qhimg.com/t01810f3e65fe98ff2d.png)](https://p5.ssl.qhimg.com/t01810f3e65fe98ff2d.png)

[![](https://p5.ssl.qhimg.com/t016b0a9e206397b973.png)](https://p5.ssl.qhimg.com/t016b0a9e206397b973.png)

[![](https://p1.ssl.qhimg.com/t0168c34bfef6fe4c45.png)](https://p1.ssl.qhimg.com/t0168c34bfef6fe4c45.png)

[![](https://p3.ssl.qhimg.com/t010e54e9baf8cc6027.png)](https://p3.ssl.qhimg.com/t010e54e9baf8cc6027.png)

[![](https://p4.ssl.qhimg.com/t019158d0074b90b217.png)](https://p4.ssl.qhimg.com/t019158d0074b90b217.png)

[![](https://p3.ssl.qhimg.com/t019ac8c1811eba7555.png)](https://p3.ssl.qhimg.com/t019ac8c1811eba7555.png)

安装完成后，在桌面生成快捷方式：

[![](https://p2.ssl.qhimg.com/t017ce2768abe55a702.png)](https://p2.ssl.qhimg.com/t017ce2768abe55a702.png)

查看软件版本，为4.1.0.2385

[![](https://p4.ssl.qhimg.com/t01afcba07a2b3e4e35.png)](https://p4.ssl.qhimg.com/t01afcba07a2b3e4e35.png)

[![](https://p3.ssl.qhimg.com/t01567f7beba535783b.png)](https://p3.ssl.qhimg.com/t01567f7beba535783b.png)

### <a class="reference-link" name="2.3%E3%80%81%E8%BD%AF%E4%BB%B6%E4%BD%BF%E7%94%A8"></a>2.3、软件使用

为了复现漏洞，我们需要启动软件并开启相关服务。

双击桌面上的软件图标，软件打开后会弹出一个窗口，可以新建空白工程，也可打开样例程序。这里我们选择不创建。

[![](https://p4.ssl.qhimg.com/t01d353cbd454d202c4.png)](https://p4.ssl.qhimg.com/t01d353cbd454d202c4.png)

然后在路径：C:\Program Files\LAquis\Apls\Examples\ExemplosCLPs\MODBUS下，打开下图所示工程。

[![](https://p3.ssl.qhimg.com/t01a53d1994ea734e0b.png)](https://p3.ssl.qhimg.com/t01a53d1994ea734e0b.png)

[![](https://p1.ssl.qhimg.com/t01ee4845952d7c2a1b.png)](https://p1.ssl.qhimg.com/t01ee4845952d7c2a1b.png)

下面是最关键的一步，启动webserver<br>
点击软件左上方的Menu，在下拉菜单中点击File,然后选择WEB Server

[![](https://p5.ssl.qhimg.com/t01f989ed4e35d8b825.png)](https://p5.ssl.qhimg.com/t01f989ed4e35d8b825.png)

[![](https://p4.ssl.qhimg.com/t014c9a1154f4555409.png)](https://p4.ssl.qhimg.com/t014c9a1154f4555409.png)

在弹出的窗口中，点击Activate WEB server

[![](https://p1.ssl.qhimg.com/t01b564fc40aa29e0ef.png)](https://p1.ssl.qhimg.com/t01b564fc40aa29e0ef.png)

点击后提示需要先保存，选择是

[![](https://p0.ssl.qhimg.com/t016372e78d0dc832b1.png)](https://p0.ssl.qhimg.com/t016372e78d0dc832b1.png)

如果第一次使用，系统防火墙会提示，选择允许即可。然后会自动弹出WEB页面：

[![](https://p4.ssl.qhimg.com/t0116ce7b0f54719de7.png)](https://p4.ssl.qhimg.com/t0116ce7b0f54719de7.png)

查看本机IP地址，我这里是192.168.178.150，

[![](https://p0.ssl.qhimg.com/t0131ca5d94257deead.png)](https://p0.ssl.qhimg.com/t0131ca5d94257deead.png)

远程访问直接输入网址：http:192.168.178.150:1234即可访问该WEB页面，这样漏洞复现环境就搭建好了。

[![](https://p2.ssl.qhimg.com/t0169f797eca72287e5.png)](https://p2.ssl.qhimg.com/t0169f797eca72287e5.png)



## 三、漏洞利用

### <a class="reference-link" name="3.1%E3%80%81%E5%87%86%E5%A4%87%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8%E5%B7%A5%E5%85%B7"></a>3.1、准备漏洞利用工具

下载并安装kali linux (官网下载[https://www.kali.org/downloads/](https://www.kali.org/downloads/))

Kali Linux是基于Debian的Linux发行版，旨在进行高级渗透测试和安全审核。Kali Linux包含数百种工具，可用于各种信息安全任务，例如渗透测试，安全性研究，计算机取证和逆向工程。Kali Linux由领先的信息安全培训公司Offensive Security开发，资助和维护。(官方帮助文档[https://www.kali.org/docs/）](https://www.kali.org/docs/%EF%BC%89)<br>
可以选择自己安装，也可使用制作好的iso镜像，新手建议直接使用iso镜像.

关于如何安装kali linux和如何使用metasploit的文章网络一搜一大把，这里就不再赘述。

### <a class="reference-link" name="3.2%E3%80%81%E5%87%86%E5%A4%87%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8%E8%84%9A%E6%9C%AC"></a>3.2、准备漏洞利用脚本

首先通过cve查询到LAquis scada的相关漏洞信息，

[![](https://p0.ssl.qhimg.com/t01c8377cc4b02842b4.png)](https://p0.ssl.qhimg.com/t01c8377cc4b02842b4.png)

通过https://www.exploit-db.com/下载漏洞利用脚本：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018fdbb589eb71a337.png)

[![](https://p2.ssl.qhimg.com/t01308cbc4558763313.png)](https://p2.ssl.qhimg.com/t01308cbc4558763313.png)

[![](https://p4.ssl.qhimg.com/t011845cc51eb4668ec.png)](https://p4.ssl.qhimg.com/t011845cc51eb4668ec.png)

下载完成后，把文件放入metasploit中，为了便于归类和查找，建议放入到下列路径：/usr/share/metasploit-framework/modules/exploits/windows/scada/ ,文件名可以修改以便于记忆和使用。

[![](https://p1.ssl.qhimg.com/t0116687094a30bdd67.png)](https://p1.ssl.qhimg.com/t0116687094a30bdd67.png)

在终端中，输入命令msfconsole，打开metasploit程序，在msf中输入命令：reload_all

[![](https://p4.ssl.qhimg.com/t01359809f6b437cb5f.png)](https://p4.ssl.qhimg.com/t01359809f6b437cb5f.png)

注：这里用到了kali linux中的metasploit，关于kali linux的使用、metasploit的使用这里不专门进行介绍了。

### <a class="reference-link" name="3.3%E3%80%81%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>3.3、漏洞利用

直接输入命令使用该模块：use exploit/windows/scada/LAquis_cve_2017_6020，

[![](https://p4.ssl.qhimg.com/t0120be219c03d7eb5a.png)](https://p4.ssl.qhimg.com/t0120be219c03d7eb5a.png)

输入命令：show options查看模块参数

[![](https://p0.ssl.qhimg.com/t016bb1a09d56599ea5.png)](https://p0.ssl.qhimg.com/t016bb1a09d56599ea5.png)

参数说明：

DEPTH 到达基本目录的级别，(也就是有多少个../)，如果安装时未更改路径，默认就是向上跳转10级。如果更改路径漏洞利用不成功，可以根据实际情况调整此参数。<br>
FILE 这是要下载的文件,与上面的DEPTH参数结合组成完整的文件路径。<br>
Proxies 端口[，类型：主机：端口] […]的代理链<br>
RHOSTS 目标主机，范围CIDR标识符或具有语法’file：&lt;path&gt;‘的主机文件<br>
RPORT 目标端口（TCP），软件默认安装是1234，不排除更改的可能。<br>
SSL 协商出站连接的SSL / TLS<br>
VHOST HTTP服务器虚拟主机<br>
本实验中我们只需要修改FILE和RHOSTS这两个参数即可<br>
为了使漏洞表现更明显，我们在服务器：192.168.178.150上是windows/system32下新建一个命名为6020.txt的文件。里面输入内容 cve-2017-6020 by Gootime

[![](https://p4.ssl.qhimg.com/t017467c26bb2cb25d1.png)](https://p4.ssl.qhimg.com/t017467c26bb2cb25d1.png)

然后回到msf中，设置FILE和RHOSTS这两个参数；<br>
输入命令：set FILE windows/system32/cve6020.txt<br>
输入命令：set RHOSTS 192.168.178.150<br>
输入命令：show options查看是否输入成功

[![](https://p2.ssl.qhimg.com/t01f264f01a99df791f.png)](https://p2.ssl.qhimg.com/t01f264f01a99df791f.png)

最后，输入命令run，利用漏洞获取服务器上的文件（在执行的时候，可以打开wireshark进行抓包，以便获得更详细的漏洞利用细节）<br>
漏洞利用成功，把目标服务器上的文件下载到了下列路径中，<br>
‘windows/system32/cve6020.txt’<br>
to<br>
‘/root/.msf4/loot/20201116065026_default_192.168.178.150_laquis.file_780688.txt’

[![](https://p3.ssl.qhimg.com/t0109a4c0fd54cf72a1.png)](https://p3.ssl.qhimg.com/t0109a4c0fd54cf72a1.png)

进入下列文件路径/root/.msf4/loot/，找到文件并双击打开，找到我们输入的文件内容：cve-2017-2020 by Gootime.再次证实漏洞效果。

[![](https://p3.ssl.qhimg.com/t010cbfc6e314f9a83d.png)](https://p3.ssl.qhimg.com/t010cbfc6e314f9a83d.png)

[![](https://p1.ssl.qhimg.com/t01f292d08da1981d61.png)](https://p1.ssl.qhimg.com/t01f292d08da1981d61.png)

除了我们指定的文件，我们也可以任意遍历服务器上的任何文件。

### <a class="reference-link" name="3.4%E3%80%81%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>3.4、漏洞分析

通过流量分析，我们发现，该漏洞指向文件listagem.laquis中的NOME参数

[![](https://p2.ssl.qhimg.com/t01fa741a8820e17753.png)](https://p2.ssl.qhimg.com/t01fa741a8820e17753.png)

该文件位于当前工程文件目录下，

[![](https://p0.ssl.qhimg.com/t01aae908d495a76a19.png)](https://p0.ssl.qhimg.com/t01aae908d495a76a19.png)

[![](https://p0.ssl.qhimg.com/t0100c0b2e9a327b166.png)](https://p0.ssl.qhimg.com/t0100c0b2e9a327b166.png)



## 四、漏洞影响

该软件在国内应用较少，主要目标用户在巴西。公开漏洞利用细节的仅有cve-2017-6020，另外还存在众多高危漏洞需要国内用户引起重视。如有使用该软件的用户，建议更新到版本4.1.0.4150，可以在[https://laquisscada.com找到该版本：](https://laquisscada.com%E6%89%BE%E5%88%B0%E8%AF%A5%E7%89%88%E6%9C%AC%EF%BC%9A)<br>
NCCIC建议用户采取防御措施，以最大程度地利用此漏洞。具体来说，用户应：<br>
最小化所有控制系统设备和/或系统的网络暴露，并确保不能从Internet访问它们。<br>
在防火墙后面找到控制系统网络和远程设备，并将其与业务网络隔离。<br>
当需要进行远程访问时，请使用安全方法，例如虚拟专用网（VPN），并确认VPN可能存在漏洞，应将其更新为可用的最新版本。还应认识到VPN仅与连接的设备一样安全。

参考：

[https://us-cert.cisa.gov/ics/advisories/ICSA-19-015-01](https://us-cert.cisa.gov/ics/advisories/ICSA-19-015-01)<br>[https://www.kali.org/docs/](https://www.kali.org/docs/)
