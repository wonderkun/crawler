> 原文链接: https://www.anquanke.com//post/id/87050 


# 【技术分享】Kerberoasting：一种Kerberos活动目录攻击方法


                                阅读量   
                                **215740**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：xpnsec.com
                                <br>原文地址：[https://blog.xpnsec.com/kerberos-attacks-part-1/](https://blog.xpnsec.com/kerberos-attacks-part-1/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0139d03d1c52d69d58.jpg)](https://p2.ssl.qhimg.com/t0139d03d1c52d69d58.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

最近一段时间，我一直在探索活动目录（Active Directory）**Kerberos**攻击技术方面有何改进，以确保自己在这些领域能跟上时代的节奏，我发现这方面技术的确有不少的进步。这周我终于能挤出一点时间，卷起袖子大干一场，深入分析其中某些攻击技术的内部原理，希望能够整理出一些参考资料，供大家交流学习。

本文是这一系列文章中的第一篇。众所周知，我们可以使用**Powerview**或**Mimikatz**命令，通过Kerberos来攻击活动目录，本文的目的就是介绍这个攻击过程背后的原理，希望能借此给大家带来使用其他方法的灵感，或者至少帮助大家理解攻击过程，而不是只是停留在表面，认为一条“Invoke-RedTeaml33t”命令就能获得域管（DA）账户。

**<br>**

**二、实验环境**

在开始实验之前，搭建一个能自由操作的实验环境非常重要。在本文中，我所搭建的实验环境包含以下几个服务器：

**Windows Server 2016：域控制器**

**Windows Server 2016：Web服务器**

**Windows Server 2016：攻击主机**

这三个服务器都是通过VirtualBox部署的虚拟机。我曾多次尝试使用Vagrant所支持的WinRM功能来自动化创建实验环境，然而经过多个夜晚的努力，碰到过许多大坑，最终我还是决定创建一个基础的Windows Server 2016虚拟机镜像，然后使用如下Powershell命令分别创建三个角色：

**1、Windows Server 2016：域控制器**



```
# Add our static IP address for this domain controller
New-NetIPAddress -InterfaceIndex 9 -IPAddress 172.16.14.1 -PrefixLength 24
# Add the domain controller role
Install-WindowsFeature AD-Domain-Services
Install-ADDSForest -DomainName lab.local -InstallDNS
# Restart our machine
Restart-Computer
# Create our IIS service account
New-ADUser -Name "IIS Service Account” `
    -SamAccountName iis_svc -UserPrincipalName iis_svc@lab.local `
    -ServicePrincipalNames "HTTP/iis.lab.local” `
    -AccountPassword (convertto-securestring "Passw0rd" -asplaintext -force) `
    -PasswordNeverExpires $True `
    -PassThru | Enable-ADAccount
```

**2、Windows Server 2016：Web服务器**



```
# Add our static IP address for this domain controller
New-NetIPAddress -InterfaceIndex 9 -IPAddress 172.16.14.2 -PrefixLength 24
# Point our DNS resolver to the DC
Set-DnsClientServerAddress -InterfaceIndex 2 -ServerAddresses 172.16.14.1
# Set our machine to be "iis.lab.local"
Rename-Computer -NewName “iis”
# Add our machine to the domain
Add-Computer -DomainName lab.local
# Restart to join the domain
Restart-Computer
# Set up our IIS server configuration
Import-Module WebAdministration
# Remove the default website
Remove-Item 'IIS:SitesDefault Web Site' -Confirm:$false -Recurse
# Create our new app pool, and set to use our IIS service account
$appPool = New-WebAppPool -Name iis.lab.local_pool
$appPool.processModel.identityType = 3
$appPool.processModel.userName = “LABiis_svc”
$appPool.processModel.password = “Passw0rd”
$appPool | Set-Item
# Create our new website and enable Windows Authentication
$WebSite = New-Website -Name iis.lab.local -PhysicalPath “C:InetPubWWWRoot” -ApplicationPool ($appPool.Name) -HostHeader iis.lab.local
Set-WebConfigurationProperty -Filter /system.WebServer/security/authentication/anonymousAuthentication `
    -Name enabled -Value $false -Location $Fqdn
Set-WebConfigurationProperty -Filter /system.WebServer/security/authentication/windowsAuthentication `
    -Name enabled -Value $true -Location $Fqdn
Set-WebConfigurationProperty -Filter /system.webServer/security/authentication/windowsAuthentication `
    -Name useAppPoolCredentials -Value $true -Location $Fqdn
```

**3、Windows Server 2016：攻击主机**



```
# Add our static IP address for this domain controller
New-NetIPAddress -InterfaceIndex 9 -IPAddress 172.16.14.3 -PrefixLength 24
# Point our DNS resolver to the DC
Set-DnsClientServerAddress -InterfaceIndex 2 -ServerAddresses 172.16.14.1
# Add our machine to the domain
Add-Computer -DomainName lab.local
# Restart to join the domain
Restart-Computer
```

我还对Virtualbox做了些设置，为每个虚拟机分配一个网络接口，以连接内部的“域”网络，因此，一旦所有虚拟环境构建完毕，我们就能得到一个拓扑简单的网络，其中包含3个IP地址，这些IP已全部加入到“lab.local”域中。<br>

现在我们已经拥有一个训练环境，可以自由尝试基于Kerberos的攻击技术，接下来我们先来看看第一种攻击技术：Kerberoasting。

**<br>**

**三、什么是Kerberoasting**

Kerberos协议在请求访问某个服务时存在一个缺陷，Kerberoasting正是利用这个缺陷的一种攻击技术。最近一段时间，这种方法的“名气”越来越大，今年的[Derbycon](https://www.irongeek.com/i.php?page=videos/derbycon7/t107-return-from-the-underworld-the-future-of-red-team-kerberos-jim-shaver-mitchell-hennigan)上会有一个演讲专门讨论这个话题。

人们开发了许多工具，以简化Windows域上完成Kerberoasting攻击所需的过程。这里我准备使用的是“Invoke-Kerberoast”，这是PowerSploit工具集中的一个Powershell commandlet，由[HarmJ0y](https://twitter.com/harmj0y?lang=en)开发。你可以先看看他写的[博客](https://www.harmj0y.net/blog/powershell/kerberoasting-without-mimikatz/)，了解更多背景知识，此外，记得订阅他的博客。

在深入分析这种方法的原理之前，我们可以先直观感受一下合适的工具如何简化我们的攻击过程：



从这段视频中，我们可以了解到如何使用这个简单的commandlet来攻击活动目录，然而，作为一名真正的黑客，你应该迫切希望了解漏洞利用背后的具体细节。首先，我们来整体了解一下实际用户请求访问某个服务时会经过哪些步骤：

1、用户将AS-REQ数据包发送给KDC（Key Distribution Centre，密钥分发中心，此处为域控），进行身份认证。

2、KDC验证用户的凭据，如果凭据有效，则返回TGT（Ticket-Granting Ticket，票据授予票据）。

3、如果用户想通过身份认证，访问某个服务（如IIS），那么他需要发起（Ticket Granting Service，票据授予服务）请求，请求中包含TGT以及所请求服务的SPN（Service Principal Name，服务主体名称）。

4、如果TGT有效并且没有过期，TGS会创建用于目标服务的一个服务票据。服务票据使用服务账户的凭据进行加密。

5、用户收到包含加密服务票据的TGS响应数据包。

6、最后，服务票据会转发给目标服务，然后使用服务账户的凭据进行解密。

整个过程比较简单，我们需要注意的是，服务票据会使用服务账户的哈希进行加密，这样一来，Windows域中任何经过身份验证的用户都可以从TGS处请求服务票据，然后离线暴力破解。

在继续工作之前，我们还需要了解一下SPN的相关知识，这是在域环境中搜索账户的关键一环。

**<br>**

**四、服务主体名称（SPN）**

微软对**SPN**的描述如下：

“SPN是服务实例的唯一标识符。Kerberos身份认证过程中需要使用SPN，以便将服务实例与服务登录账户相关联。”

也就是说，SPN是唯一标识符，用于将域账户与服务及主机关联起来。Windows域环境中的SPN格式如下所示：

```
SERVICE/host.name
```

比如，在我们的实验环境中，所使用的IIS实例如下所示：

```
HTTP/iis.lab.local
```

这个SPN与服务所对应的账户相关联，在演示环境中，所关联的账户为“LABiis_svc”。在LDAP中，通过将“servicePrincipalName”属性的值设为目标SPN，就能实现这种绑定关系：

[![](https://p1.ssl.qhimg.com/t01610469512ef42952.png)](https://p1.ssl.qhimg.com/t01610469512ef42952.png)

这里我们还需要注意到一点，活动目录中的计算机账户本质上也是服务账户，其在LDAP中也有关联的SPN。这一点不难理解，因为系统经常会使用Kerberos来请求以LOCAL SYSTEM身份运行的服务，如SMB或者远程注册表服务等。不幸的是，对攻击者而言，计算机账户的密码长度较长，比较复杂，并且每30天会进行重置，也就是说攻击者无法暴力破解这些账户凭证。

现在我们已经了解账户如何与Kerberos服务相关联，接下来我们可以继续分析Kerberoasting攻击技术的内部工作原理。

**<br>**

**五、Kerberoasting工作原理**

在实验环境中，我们可以在请求IIS网站的过程中运行抓包程序，以查看网络中传输的数据包。为了生成网络流量，我们可以使用如下命令，使用Kerberos对IIS服务进行身份验证：

```
Invoke-WebRequest http://iis.lab.local -UseDefaultCredentials -UseBasicParsing
```

通信完成后，在Wireshark中我们可以看到如下数据包：

[![](https://p0.ssl.qhimg.com/t01ffb28408cf122db5.png)](https://p0.ssl.qhimg.com/t01ffb28408cf122db5.png)

如前文所述，最开始的两个数据包为AS-REQ以及AS-REP，用户通过这两个数据包与KDC进行身份认证，以获取TGT。对Kerberoasting而言最为重要的部分为TGS-REQ以及TGS-REP数据包。

首先，我们来观察一下TGS-REQ数据包的内容：

[![](https://p1.ssl.qhimg.com/t01ee9cd1c4d9467810.png)](https://p1.ssl.qhimg.com/t01ee9cd1c4d9467810.png)

我们可以看到，这个数据包正在请求LAB.LOCAL域中的HTTP/iis.lab.local SPN，根据我们前面所执行的操作，这些信息理解起来非常直观。我们可以使用Windows自带的SetSPN.exe工具来定位提供这个SPN的具体账户，具体命令如下：

```
setspn.exe /Q HTTP/iis.lab.local
```

[![](https://p2.ssl.qhimg.com/t01aa8f9ebab5bd1ea7.png)](https://p2.ssl.qhimg.com/t01aa8f9ebab5bd1ea7.png)

这条命令会返回我们在实验环境中建立的“IIS Service Account”账户。

接下来，观察TGS-REP数据包，我们可以发现一个服务票据，该服务票据使用LABiis_svc服务账户的密码来加密（这个例子中使用的是RC4加密算法）：

[![](https://p4.ssl.qhimg.com/t014c6e5b8c93c09377.png)](https://p4.ssl.qhimg.com/t014c6e5b8c93c09377.png)

正是这段数据可以让我们在离线状态下进行暴力破解，因为我们知道服务账户密码是解密服务票据数据的唯一密钥。

这基本上就是整个攻击过程的所有过程。总结一下，Kerberoasting攻击涉及如下步骤：

1、攻击者在活动目录中搜索带有servicePrincipalName属性的账户。

2、攻击者向域控制器发起请求，请求特定服务的服务票据。

3、随后，攻击者收集服务票据，在离线环境中进行破解，得到服务账户的密码。

接下来还需要做的事情，就是将这段数据移交给密码破解工具进行处理，如JTR（John the Ripper）工具。如果我们观察JTR所使用的哈希格式，可知我们需要提供如下格式的数据：

```
$krb5tgs$&lt;ENCRYPTION_TYPE&gt;$*&lt;USERNAME&gt;$&lt;REALM&gt;$&lt;SPN&gt;*$&lt;FIRST_16_BYTES_TICKET&gt;$&lt;REMAINING_TICKET_BYTES&gt;
```

为了完成攻击过程，我们需要手动填充这个字符串，我们可以在Wireshark抓包结果中提取相应字段加以填充，最终得到如下字符串：

```
$krb5tgs$23$*iis_svc$LAB.LOCAL$HTTP/iis.lab.local*$0F6FC474DB169AA8CE9B5E626DAACC9D$1A346CE3F66C52976F53831AA24A1B217CDF0D68A0EB87FEE00CFD32F544BF83EBB6416732522B12232DD6935EAC076B439F56E6CB7FA6C37D984D132E2D2CB65CA399CD5E44EB2EB41F12C40F9044B40E3EA914278C8A3098BABACF49AB46E776D1413EF63ABCDF6418D2DB9241B2FDD9309346EC59AF20A82FD6DAEA9510C1DFD1A9E8D99C59FF72E985057BA0D18394B0A7CB1BD74F8D436A3DD780175A0C6BCAD9E46570A476AB9913B561EE481AD8C33A3C81CED055E959F08A52EBA7A342F53183E1531BE8EC2D28C7ECFA32F98DBC7FF87B4E5C79824F3868D38CE09010960726D58CFBFC88C9D34AB199169F39010AA4AAB92B6EA40F875963D518311B3F079D97B65FE9768C9A4EE50F7C16D525FDC081CE359A0B0FE5FB18D8D8690D8F88B010BEF4F28DC151A4137272AE9EACA9053406C0DDEAE453196E3B6C28B8359724BFC089B772CBAE093BF88ABC070D12B0FF2E721D7B8B10B822BFB514091EFFAF3F5FA8C286A9E45BF76BA171E6CABEB3DDADC297185C51A295855B8CFA8062BD6770093355C32690FD184D6EAE2B66EA1F553CBC7679681DB5089FDB23329EFE59DE807E657A98CCC0C2D95EAAC9F363D5B8C9B8A23AAB680C328B019AE99440A5D8795014BE22F6739A4F77874E94196F010C012F9A4A587570C38874AD7F8B9EC554FB865752A5F3DD4F785C9AF54031100CE580DFADF4C70FF11839647FC288FCE8D00BBCB680E02A46230ECB0530BA1771FB8485BA17F5218852C5CDFC769B89D77B37802CC6D22E6BA944F6E4B565D8D04418C44BF10E06294FD58913CA6D206BB6E46F15B3ABFC09695F5FBAB81D2E743AC19B24716D9D6CB6BAE65674F5CDF1935D1413A4BE6D96EAFAF65CFA361DECC0AB1E12998B5C26B6AD38C8077FD149CDEDA227C4C68F19FBF22B23E7E84581A64A413C1C983E01B56C2000656B4AAD8C67260FC0142EECCD96D624FA284B619D11E797AF2D730A5998D9E6D9F4FEF58A847D7D9B804BE2925BEAE627A0A9F335072F97F214A24DB58CF5E2E74F0EEFF1A43F1EC1B88C0110F3C2ABAAC0D3E954A42B550C37CF84BABE6E85EC4E0885EB8309A4C5E2A1BB473B332FF5C31C0B4C32DB507C1ECA5B7AE607D2423EE1E7F07361229E0AB2678CFBD07AFFFC5E989C5AB1821AC2F524083258D3F0CA7E7F8250BE3F7CC72CF636B098A3C9B3F4E289FD81A9B3C33BFA63ED8813BBC12205134ADD9FB8548312B734C921A2CF8A1687AF7EE022B0F57BBF0F8D8F17952614CB288B95DF3FE4F03D20B83227328603DAFB264537EB0CACDA18DE21AA99E07600030424EDB41FC3C8161238971BF62AF99DB8E2D438AF06F9D8FEEFF3EDB6A4D4F0A6FB5DFDBE99B1ED454D6FF3DC508C45ED430923212A088E6200B2076DA509888EDD32FCA946A215C8934DB7A3B5AC6BED10E4A114F2F132608DBE236CBA73CBCFFC024FB500E96C3D766CA7F4083DED3666C2B7DCD290F65F7E80FF70FA575777A845FBF7AF05B38DFB1CCD7ACCC0398F8DBF532E28DC6BC0EC49D18F2753CAEC5912693A0B6050F2BFCE72F5160847DCFC78D580609007DDBDF1F338C61C13E7B62FCEC6E51D1C0CD1EC0167E40042`
```

将这段数据传递给JTR处理，可以得到所需的密码，解密结果如下所示：

[![](https://p0.ssl.qhimg.com/t016aab5c487947af01.png)](https://p0.ssl.qhimg.com/t016aab5c487947af01.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://publish.adlab.corp.qihoo.net:8360/ueditor/themes/default/images/spacer.gif)

**六、总结**

本文手动梳理了一遍Kerberoasting的攻击过程，希望你能对这种攻击方法有所理解。接下来，我们会介绍与之类似的一些攻击方法及相应的工作原理，比如AS-REP Roasting攻击方法，这种攻击方法与Kerberoasting攻击方法非常相似。

还是那句话，如果你有任何反馈意见或建议，欢迎随时跟[我](https://blog.xpnsec.com/about/)联系


