> 原文链接: https://www.anquanke.com//post/id/86522 


# 【技术分享】二道贩子也能发财！犯罪分子正在模仿EternalMiner进行挖矿


                                阅读量   
                                **82411**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：intezer.com
                                <br>原文地址：[http://www.intezer.com/eternalminer-copycats/](http://www.intezer.com/eternalminer-copycats/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01c2727683310a29ba.png)](https://p0.ssl.qhimg.com/t01c2727683310a29ba.png)

<br>

****

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：170RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**写在前面的话**

大概在八个星期之前，研究人员在Samba中发现了一个严重的安全漏洞，该漏洞提交之后不久便被成功修复，但值得一提的是，从2010年起的每一个Samba版本都存在这个漏洞。这个漏洞名叫“SambaCry”，在WannaCry席卷了全球的Windows系统（永恒之蓝的SMB漏洞利用部分）之后，SambaCry也浮出了水面。这个漏洞属于逻辑漏洞，它将允许只拥有写入权限的攻击者加载恶意Samba模块并执行任意代码。

<br>

**安全客小百科:Samba和SMB**

Samba是在Linux和UNIX系统上实现SMB协议的一个免费软件，它由服务器端及客户端程序构成。而SMB（Server Messages Block，即信息服务块）是一种在局域网上共享文件和打印机的一种通信协议，它可以为局域网内的不同计算机之间提供文件及打印机等资源的共享服务。SMB协议是客户机/服务器型协议，客户机通过该协议可以访问服务器上的共享文件系统、打印机及其他资源。用户可以通过对“NetBIOS over TCP/IP”进行配置来让Samba不但能与局域网内的主机分享资源，而且还能与整个互联网上的电脑分享资源。

[![](https://p5.ssl.qhimg.com/t0161d8226411054c61.png)](https://p5.ssl.qhimg.com/t0161d8226411054c61.png)

就在针对该漏洞的POC代码首次发布之后，我立刻编写了一个可以匹配针对潜在Payload的Yara签名（规则），然后开始监测针对该漏洞的威胁信息。观察了一段时间之后，我们发现了无数的反向Shell以及恶意Payload Dropper，其中绝大多数都是Metasploit Payload或其他一些公开可用的恶意代码植入。

在今年的六月九号，卡巴斯基实验室发布了一篇关于“[EternalMiner](https://securelist.com/sambacry-is-coming/78674/)”的文章，这是一款以经济利益为目的的加密货币挖矿恶意软件，它可以将目标用户的设备变成一台矿机，并利用受感染设备来为攻击者挖比特币之类的加密货币。不到一个星期之后，我们还发现了很多模仿这种操作模式的网络犯罪分子在改进了漏洞利用代码之后，能够更好地控制目标设备进行挖矿了。根据这种攻击的性质，我们决定将这种威胁取名为“CopyMinner”!

<br>

**1. 概述**

正如我们之前所提到的那样，网络犯罪分子们正在改进原本的“EternalMiner”，并且使用更加高级的“CopyMinner”来实施攻击。这些攻击者会采用多种灵活的方法配合多台备份服务器来实现恶意软件的每日定期更新，这样不仅可以实现更加持久化的后门，而且还可以帮助攻击者更好地控制目标设备并充分利用目标用户的资源来为他们挖矿。这些网络犯罪分子们已经将原来的EternalMiner升级到了另一个境界，而且现在甚至还可以同时控制多台目标设备。在接下来的章节中，我们将会对下图中的每一个组件进行详细的分析，并分析CopyMiner和EternalMiner之间的区别。

[![](https://p2.ssl.qhimg.com/t015f81186411425180.png)](https://p2.ssl.qhimg.com/t015f81186411425180.png)

<br>

**2.CopyMinner Dropper**

在今年的六月十四号，我们向VirusTotal提交了一个小型的Dropper样本。这个Dropper首先会执行其中的“samba_init_module”输出模块，然后尝试从攻击者所控制的后台服务器获取Payload，最后以root权限在目标设备的后台运行恶意代码。整个过程是通过一个经过混淆处理的硬编码bash代码完成的，具体如下图所示:

[![](https://p2.ssl.qhimg.com/t01eb6c5e4253b02cff.png)](https://p2.ssl.qhimg.com/t01eb6c5e4253b02cff.png)

样本哈希：

444d0fae73e1221b81dc6c5d53cf087afa88248fc22ef36e756841ab04df24a

<br>

**3.Payload**

恶意Payload其实是一个非常短小精悍的Bash脚本，它需要依赖于目标设备的系统工具来完成以下三个主要任务：

（1）使用crontab命令完成恶意程序的每日定期更新，这个过程需要使用到三台不同的备份服务器：

[http://update.sdgndsfajfsdf.info/upd](http://update.sdgndsfajfsdf.info/upd) 

[http://update.sdgsafdsf.pw/upd2](http://update.sdgsafdsf.pw/upd2) 

[http://update.omfg.pw/upd3](http://update.omfg.pw/upd3) 

（2）在后台下载并执行Tsunami后门以及CPUMiner。

（3）防止其他的攻击者攻击这台用户设备（修复smb.conf），目的是避免出现资源竞争的情况，因为挖矿需要消耗大量的计算资源。

我们还可以从其中一台在线服务器（http://update.sdgndsfajfsdf.info/upd）中获取到负责处理每日更新任务的脚本。但是看起来这个脚本是一个精简版本的Payload脚本，因为它缺少了每日更新补丁的安装功能：

[![](https://p0.ssl.qhimg.com/t019c47e53c85248434.png)](https://p0.ssl.qhimg.com/t019c47e53c85248434.png)

<br>

**4.CPUMiner**

CPUMiner是一款开源的加密货币挖矿工具，它是命令行工具，支持多种加密货币和算法。从目前收集到的信息来看，攻击者貌似使用的是一款多线程的“CPUMiner”（c[puminer-multi](https://github.com/tpruvot/cpuminer-multi)），这个版本相比于EternalMiner之前使用的cpuminner挖矿效率要高得多。除此之外，相较于EternalMiner而言，这个升级版的样本可以在不需要任何命令行参数的情况下单独运行。启动之后，升级版的CPUMiner会自动登录到攻击者的私人矿池服务器（p.theywant[.]in:8080），而不是像EternalMiner一样登录到公共矿池服务器（xmr.crypto-pool[.]fr:3333）。

[![](https://p0.ssl.qhimg.com/t01d000ce2e9a6e1065.png)](https://p0.ssl.qhimg.com/t01d000ce2e9a6e1065.png)

<br>

**5.Tsunami后门**

除了CPUMiner之外，Payload脚本还会从服务器下载并执行Tsunami后门（也叫Kaiten）。这是一种旧版本Linux后门，在此之前攻击者一般使用这种后门来感染[物联网设备](https://researchcenter.paloaltonetworks.com/2017/04/unit42-new-iotlinux-malware-targets-dvrs-forms-botnet/)以及[OSX系统](https://www.welivesecurity.com/2011/10/25/linux-tsunami-hits-os-x/)。Tsunami后门的源代码现在已经开源了【[点我获取](https://dl.packetstormsecurity.net/irc/kaiten.c)】，任何人都可以随意使用并根据自己的需要来进行修改。这个样本（d8e93252f41e8b0d10cffa92923eeab94c6c42e8acc308e91340df102042c8c8）中嵌入有硬编码的C2 IRC服务器（asdgsd.uselesslongdomain[.]info），我们甚至还可以直接使用恶意软件中的硬编码凭证来登录这台IRC服务器。在下面这张图片中，你可以看到两个近期登录过该服务器的受害用户（拥有root访问权限）：

[![](https://p5.ssl.qhimg.com/t01faaba77a149bbd06.png)](https://p5.ssl.qhimg.com/t01faaba77a149bbd06.png)

<br>

**6.迅速上线**

我们发现，这些用来托管Payload文件的后台主机和服务器所使用的域名都是在今年的六月十三号注册的，而第二天便有恶意CPUMiner以及Tsunami样本上传到了VirusTotal，也就是六月十四日，这也就意味着攻击者在原始的EternalMiner版本发布之后的四到五天时间里便开始了CopyMinner活动。

<br>

**7.入侵威胁指标IoC**

[![](https://p5.ssl.qhimg.com/t019a330696f18049c9.png)](https://p5.ssl.qhimg.com/t019a330696f18049c9.png)


