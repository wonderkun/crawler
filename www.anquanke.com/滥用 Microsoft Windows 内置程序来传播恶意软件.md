> 原文链接: https://www.anquanke.com//post/id/154371 


# 滥用 Microsoft Windows 内置程序来传播恶意软件


                                阅读量   
                                **166232**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者MAX GANNON，文章来源：cofense.com
                                <br>原文地址：[https://cofense.com/abusing-microsoft-windows-utilities-deliver-malware-fun-profit/](https://cofense.com/abusing-microsoft-windows-utilities-deliver-malware-fun-profit/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01084ead0aa1e48b12.jpg)](https://p3.ssl.qhimg.com/t01084ead0aa1e48b12.jpg)

去年, 我们观察到滥用平台内置功能进行攻击的恶意活动有所增加, 而整个业界普遍都会在各自平台中内置一些功能. 我们发布的报告[2018年恶意软件回顾](https://cofense.com/whitepaper/malware-review-2018/)中, 着重阐述了滥用Microsoft功能（如OLE和DDE）传播恶意软件的相关内容. 从去年开始, 随着黑客们开始利用更多类型的平台内置功能并在一个活动中组合使用多种技术, 这种趋势一直在持续。

攻击者滥用Microsoft Windows内置程序进行网络钓鱼活动, 是因为相对于附加或嵌入恶意软件, 这种战术更难以识别和检测. 其原因就在于, 在许多情况下, 即使被恶意软件利用, 这些内置程序的实际运行方式与其原本设计的运行方式, 依然完全相同. 我们当前了解到的一些Windows系统种被滥用的内置程序包括Certutil, Schtasks, Bitsadmin和MpCmdRun。



## Certutil

Certutil是一个简单的命令行工具, 早在2015年就开始被黑客们利用了[2], 今年3月份爆发的大规模僵尸软件Dreambot行动中也露过脸[1]. Certutil可以用来在中间人攻击（MITM）中轻松的安装假证书, 以及下载并解码以base64或十六进制编码的伪装成证书的的文件. 这一点尤为重要, 因为防火墙规则一般被可执行文件或恶意二进制文件触发, 不太可能把看起来是被编码的证书文件识别为恶意软件[3].

[![](https://cofense.com/wp-content/uploads/2018/08/Picture-1-480x29.jpg)](https://cofense.com/wp-content/uploads/2018/08/Picture-1-480x29.jpg)图1: 使用Certutil下载编码的证书文件

[![](https://cofense.com/wp-content/uploads/2018/08/Picture2-2-480x155.jpg)](https://cofense.com/wp-content/uploads/2018/08/Picture2-2-480x155.jpg)图2: 由Certutil下载的伪装的“证书”文件

[![](https://cofense.com/wp-content/uploads/2018/08/Picture3-1-480x47.jpg)](https://cofense.com/wp-content/uploads/2018/08/Picture3-1-480x47.jpg)图3: 使用Certutil解码下载的证书文件

[![](https://cofense.com/wp-content/uploads/2018/08/Picture4-1-480x108.jpg)](https://cofense.com/wp-content/uploads/2018/08/Picture4-1-480x108.jpg)图4: 使用图3的命令解码图2“证书”文件的结果

Certutil执行HTTP请求的方式导致其被进一步滥用. Certutil连续使用两个具有不同User-Agents的HTTP GET请求（参见图5）, 于是黑客可以设置只允许在接收到正确的User-Agents时才能下载托管文件. 除非提供了正确的User-Agents, 否则服务器通过回复虚假的“Not Found”进行响应（参见图6）, 以此阻止研究人员和防御者访问Payload. 这个虚假的“Not Found”响应还可以帮助服务器避免被某些自动URL扫描程序检测到, 因为自动URL扫描器一般会将“Not Found”响应判定为没有恶意文件.

[![](https://cofense.com/wp-content/uploads/2018/08/Picture5-1-480x41.jpg)](https://cofense.com/wp-content/uploads/2018/08/Picture5-1-480x41.jpg)图5: Certutil发起的HTTP GET请求使用的独特的User-Agents

[![](https://cofense.com/wp-content/uploads/2018/08/Picture6-1-480x249.jpg)](https://cofense.com/wp-content/uploads/2018/08/Picture6-1-480x249.jpg)图6: 虚假的“Not Found”响应



## Schtasks

另一个常被滥用的合法Windows内置程序是schtasks. 这个程序最初只是设计来简单的安排计划任务. 不幸的是, 黑客们最知道如何安排计划任务和识别执行目标, 从而在被攻克系统上实现驻留.

[![](https://cofense.com/wp-content/uploads/2018/08/Picture7-1-480x27.jpg)](https://cofense.com/wp-content/uploads/2018/08/Picture7-1-480x27.jpg)图7: 使用Schtasks创建每两天运行一次指定文件的任务

攻击者可以安排在特定时间运行其脚本或二进制文件, 例如当用户登录时, 或满足其他什么条件时. 有许多可用于触发任务运行的条件, 例如仅当主机可访问互联网且系统处于空闲状态时; 或者(对于挖矿软件)只在主机接入电源时，因为如果被攻击主机是笔记本电脑, 挖矿时电池消耗不会引起注意. （附加条件见图8.）这些条件可用于简单的躲避检测.

这种策略比另一种流行的实现驻留的方式更隐蔽: 在Startup文件夹中放置脚本或可执行文件, 在用户登录时自动运行. 由于Startup文件夹可以浏览, 因此更容易被识别到（图9）,而且Startup文件夹是AV检查的首要位置之一.

[![](https://cofense.com/wp-content/uploads/2018/08/Picture8-1-582x675.jpg)](https://cofense.com/wp-content/uploads/2018/08/Picture8-1-582x675.jpg)图8: 图7的命令创建的任务配置文件

[![](https://cofense.com/wp-content/uploads/2018/08/Picture9.jpg)](https://cofense.com/wp-content/uploads/2018/08/Picture9.jpg)图9: 浏览被放置了文件的Startup文件夹

通过使用schtasks而不是依赖Startup文件夹中的文件, 攻击者能够更好地伪装他们的活动, 并对恶意软件的行为施加更多控制. 另一个好处是用于保存任务信息的文件不需要具有扩展名, 这一点足以使某些防病毒解决方案忽略该配置文件。



## BITSAdmin

BITSAdmin（或后台智能传输服务）是Windows文件传输工具, 自2007以来就一直存在, 并且通常被利用作为CVE漏洞或Office宏漏洞利用过程的一部分, 通过PowerShell执行, 用于下载文件. （参见图10.）Powershell命令通常会被记录, 并且通过Powershell直接下载文件会触发行为检测系统, 而BITSadmin实际上使用已经存在的svchost.exe进程来执行其操作, 结果看起来好像执行文件创建和下载操作的是svchost.exe. 而svchost.exe创建文件及连接互联网再正常不过, 例如下载Windows更新. 于是利用BITSAdmin下载文件就被会认为是正常行为, 于是就被一些本地防病毒解决方案忽略掉了[4].

[![](https://cofense.com/wp-content/uploads/2018/08/Picture10.jpg)](https://cofense.com/wp-content/uploads/2018/08/Picture10.jpg)图10: 使用bitsadmin命令下载文件

BITSAdmin的另一个与Certutil类似好处是, BITSAdmin有一种独特的下载文件的方式. BITSAdmin使用特定的User-Agent（Microsoft BITS / 7.5）来请求文件, 而且它会首先执行HTTP HEAD请求以检查资源是否可用, 而不是直接执行HTTP GET请求获取资源. 如果资源可用, BITSAdmin才接着发送HTTP GET请求. （参见图11.）User-Agent唯一的特性可以像Certutil一样使用, 服务器只有在接收到正确的User-Agent时, 才允许下载托管的文件, 并且HTTP HEAD请求本身就少见, 攻击者也可以使用它达到同样的目的[5].

[![](https://cofense.com/wp-content/uploads/2018/08/Picture11-671x439.jpg)](https://cofense.com/wp-content/uploads/2018/08/Picture11-671x439.jpg)图11: BITSAdmin下载过程的数据包



## MpCmdRun

MpCmdRun是一个允许用户与Windows Defender Antivirus进行交互的命令行工具. MpCmdRun对于某些自动化任务非常有用 – 例如, 如果用户不能更新本地计算机上的Windows Defender, 系统管理员可以使用MpCmdRun进行远程更新. 特别的是, 此功能通常用于强制Windows Defender回滚, 然后在自动更新不起作用时更新签名定义. 但是, 此功能会引入一些缺陷.

攻击者可以使用此工具重置AV签名, 并修改Windows Defender的行为. 最近就出现过使用此技术进行攻击的实际案例: 攻击者在Office宏脚本执行中MpCmdRun命令, 用于在关闭所有打开的Office程序（这对于修改相关注册表项是必需的）之前对Windows Defender进行更改, 并通过注册表项禁用Microsoft Office中的各种安全设置[6]. 在下面的图12的案例中, 与MpCmdRun组合使用的命令删除动态签名, 但不删除所有签名. 通过使用MpCmdRun, 攻击者可以在不禁用Windows Defender的情况下绕过Windows Defender的检测, 从而进一步控制攻克的主机.

[![](https://cofense.com/wp-content/uploads/2018/08/Picture12-480x74.jpg)](https://cofense.com/wp-content/uploads/2018/08/Picture12-480x74.jpg)图12: 使用MpCmdRun的Office宏脚本



## 我们之前就已经讲过啦

这种趋势并不新鲜, 但滥用平台内置功能的激增, 表明在可预见的未来, 通过滥用内置功能进行网络钓鱼来直接传播Payload的攻击方式, 将会继续存在. 要查看网络钓鱼活动中突出的其他类型的功能滥用, 请参阅我们之前发布的成果:
<li>DDE – 2017年11月21日: [滥用Microsoft Word DDE传播Locky, Trickbot和Pony恶意软件](https://cofense.com/microsoft-word-dde-abuse-tactics-spreads-locky-trickbot-pony-malware-campaigns/)
</li>
- 多个CVE – 2018年3月8日: [三重威胁: 使用了3个单独的攻击向量的网络钓鱼活动](https://cofense.com/triple-threat-phishing-campaign-used-3-separate-vectors/).
<li>OLE – 2017年4月10日: [2017年利用OLE包传播的恶意软件占据了一定的市场份额](https://cofense.com/malware-delivery-ole-packages-carve-market-share-2017-threat-landscape/)
</li>
- 恶意软件回顾 – 2018年3月22日: 我们发布的[2018:恶意软件回顾](https://cofense.com/whitepaper/malware-review-2018/)报告
<li>CVE-2017-11882 – 2018年4月6日: [.XLSX网络钓鱼是否会卷土重来?](https://cofense.com/xlsx-phishing-making-comeback/)
</li>
通过滥用对企业运营不可或缺的合法功能, 黑客能够绕过AV和行为分析检测系统, 以便成功传播恶意软件. 这种趋势不会消失, 只会越来越大. 鉴于攻击者者能够通过滥用企业(为业务正常运行)无法禁用的功能来绕过防御, 因此必须[培训](https://cofense.com/product-services/simulator-2/)企业员工识别最初的威胁并进行上报. 将此种培训与人工验证相结合, 有助于确保防御策略是成功的, 而不仅仅依赖于那些黑客们不断研究如何去绕过的自动化系统.

如需回顾和展望主要恶意软件趋势, 请[查看](https://cofense.com/malware-review-2018/) 2018年Cofense恶意软件回顾.



## 参考引用
1. 有关更多详细信息, 请参阅TID 11170和11136, 以及2018年3月29 日的战略分析“Nefarious Use of Legitimate Platforms to Deliver Malware Extends to KeyCDN.”.
1. [https://researchcenter.paloaltonetworks.com/2015/08/retefe-banking-trojan-targets-sweden-switzerland-and-japan/](https://researchcenter.paloaltonetworks.com/2015/08/retefe-banking-trojan-targets-sweden-switzerland-and-japan/)
1. [https://www.bleepingcomputer.com/news/security/Certutilexe-could-allow-attackers-to-download-malware-while-bypassing-av/](https://www.bleepingcomputer.com/news/security/Certutilexe-could-allow-attackers-to-download-malware-while-bypassing-av/)
1. [https://virusbulletin.com/virusbulletin/2016/07/journey-evasion-enters-behavioural-phase/](https://virusbulletin.com/virusbulletin/2016/07/journey-evasion-enters-behavioural-phase/)
1. [https://isc.sans.edu/diary/Microsoft+BITS+Used+to+Download+Payloads/21027](https://isc.sans.edu/diary/Microsoft+BITS+Used+to+Download+Payloads/21027)
1. 有关更多详细信息, 请参阅TID 11979, 和2018年2月15日战略分析“When Features and Exploits Collide”.