> 原文链接: https://www.anquanke.com//post/id/84915 


# 【技术分享】Windows更新服务-WSUS中间人劫持


                                阅读量   
                                **157610**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：sixdub
                                <br>原文地址：[https://www.sixdub.net/?p=623](https://www.sixdub.net/?p=623)

译文仅供参考，具体内容表达以及含义原文为准

****

**[![](https://p5.ssl.qhimg.com/t018cac174391f01a84.jpg)](https://p5.ssl.qhimg.com/t018cac174391f01a84.jpg)**

**翻译：**[**t0stmail**](http://bobao.360.cn/member/contribute?uid=138185681)

**稿费：170RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



**前言**

本文介绍了wpad攻击与wsus攻击的原理，并结合已有的工具进行攻击演示。

<br>

**WPAD <strong>攻击**</strong>

Web代理自动发现（WPAD）是Microsoft Windows客户端用于自动配置本地代理设置的协议.协议允许用户客户端（例如IE）自动定位和使用适当的代理设置以访问企业网络出口。 协议使用过程如下：

1. DHCP时是否获得去了代理配置

2. 如果没有，解析“wpad.domain.com”，并从该服务器获取配置。

3. 如果我们没有得到结果，使用NetBIOS（NBT-NS）广播来解析名称“WPAD”

4. 如果找到服务器，请从该服务器请求具有uri“/wpad.dat（http：// &lt;SERVER&gt; /wpad.dat）”的资源，其中将包含代理的设置

由于在NBT-NS回复（步骤3）期间缺乏验证，客户请求的广播域或本地子网中的任何其他客户端都可以响应并声称自己是WPAD服务器。然后恶意的WPAD服务器可以提供一个恶意的配置文件来配置目标的代理设置，且可以拦截所有客户流量进行篡改。

<br>

**WSUS <strong>中间人攻击**</strong>

Windows Server Update Services（WSUS）是一种允许企业集中管理和部署更新补丁或修补程序的系统。 在Blackhat USA 2015，来自Context的一组安全研究人员Paul Stone（@pdjstone）和Alex Chapman介绍了企业在不加密网络上进行更新的问题。 他们明确指出，没有SSL，任何人都可以对WSUS进行中间人攻击，以提供恶意的更新包。 顺便说一下，HTTP是WSUS的默认值。 另外一个问题：更新文件必须有Microsoft签名。 解决方案是： PsExec.exe具有微软签名，可以用来执行任意Windows命令。

**<br>**

**<strong>结合攻击**</strong>

对于本节，我假设我们已从外部获得对加入域的主机的初始访问。

**1.  Identify the Possibilities**

第一步是识别任何WSUS错误配置。我们可以通过查询注册表来确定系统的WSUS设置。我们可以查询Internet Explorer的当前代理配置，如果WSUS的URL是“HTTP：// &lt;SERVER&gt;”，并且浏览器设置为自动配置代理，则我们可以继续！

可能的注册表键值：



```
HKLMSoftwarePoliciesMicrosoftWindowsWindowsUpdateWUServer
HKLMSoftwarePoliciesMicrosoftWindowsWindowsUpdateAUUseWUServer
HKCUSoftwareMicrosoftWindowsCurrentVersionInternet SettingsConnectionsDefaultConnectionSettings
```

注意：如果第5个字节是偶数，则Internet Explorer中设置了wpad代理

[![](https://p0.ssl.qhimg.com/t01b3a765af297d0e36.png)](https://p0.ssl.qhimg.com/t01b3a765af297d0e36.png)

WSUS Settings

[![](https://p5.ssl.qhimg.com/t01708ea37ec97ba6ae.png)](https://p5.ssl.qhimg.com/t01708ea37ec97ba6ae.png)

Automatic Settings Selected (5th byte)

我们可以使用ARP找到我们要定位的子网上的另一个主机

[![](https://p0.ssl.qhimg.com/t0177da51ef2996dbfd.png)](https://p0.ssl.qhimg.com/t0177da51ef2996dbfd.png)

**2. Network Bending Kung-fu**

我们使用Cobalt Strike’s Beacon功能进行反向端口转发。在WPAD投毒中，我们可以将受害者的浏览器指向我们的“代理”，这是目标网络到我们的C2服务器的反向隧道。然后，使用SOCKS转发，将浏览流量推送回环境中，以接收除了篡改包之外的WSUS操作更新。

[![](https://p2.ssl.qhimg.com/t01a1b841125241495c.png)](https://p2.ssl.qhimg.com/t01a1b841125241495c.png)

**3. Poison**

首先，配置我的恶意载荷和启动WSUSpectProxy。WSUSpectProxy接收其payload.ini文件中定义的自定义内容（示例如下所示）。 像研究人员在他们的白皮书推荐的一样，我使用PsExec.exe利用参数启动powershell.exe运行“net user”和“net localgroup”添加一个后门用户“bob”。

（WSUSpectProxy项 目：[https://github.com/ctxis/wsuspect-proxy](https://github.com/ctxis/wsuspect-proxy)）

[![](https://p1.ssl.qhimg.com/t01432fbf99a86087f1.png)](https://p1.ssl.qhimg.com/t01432fbf99a86087f1.png)

其次启动Invoke-Inveigh，有以下参数设置：



```
-IP &lt;IP OF POISON VICTIM&gt; : Set the IP to bind the raw socket to
-NBNS Y : Set NBNS spoofing to be enabled
-LLMNR Y : Set LLMNR spoofing to be enabled
-HTTP Y : Turn on the HTTP server for serving up WPAD.dat files
-SMB N : Do not do any sort of SMB relay kind of stuff
-StatusOutput Y : Print status outputs
-Tool 2 : Configure the settings to run this in a certain tool. The Empire setting works well for Cobalt Strike
-SpooferIPsReply &lt;TARGET IP&gt; : IP of the target or CSV list of targets
-WPADAuth Anonymous : Do not pop a creds box for the WPAD
-WPADIp &lt;ProxyHost&gt; : IP of poison host where the rportfwd command is run
-WPADPort 8080 : port of the rportfwd command
```

[![](https://p1.ssl.qhimg.com/t01fa2df4fb6da22466.png)](https://p1.ssl.qhimg.com/t01fa2df4fb6da22466.png)

此命令将执行对目标的WPDA投毒，并提供一个WPAD.dat，指向目标浏览器，该端口将转发回我们的C2服务器的8080端口。

**4. MITM Updates**

一旦满足MITM条件，目标的更新请求就被拦截，我的恶意数据包就会被传递给客户端。 由于是关键更新，因此会被执行，添加一个本地用户。

[![](https://p5.ssl.qhimg.com/t01c0072d2d7632d783.png)](https://p5.ssl.qhimg.com/t01c0072d2d7632d783.png)

[![](https://p0.ssl.qhimg.com/t0121598e869ccdbf04.png)](https://p0.ssl.qhimg.com/t0121598e869ccdbf04.png)

现在我们可以访问并且可以使用新添加的用户部署Beacon代理。

**<strong><br>**</strong>

**<strong>修复**</strong>

这个攻击的成功包含了很多的缺陷，他们必须在网络中被修复，但是我还是看到很多对这个攻击链过程中的很多错误的配置与控制。除了进行控制以防止漏洞外，有很多方法，像SOC和CIRT可以在网络中与复杂的攻击者中检测出恶意活动，前提是检测是可信的。

**Wpad控制/修复**



要修复WPAD配置错误，应在内部DNS服务器中添加名称为“wpad”的DNS A或CNAME记录，以防止主机进入执行MDNS / LLMNR广播的步骤。 此外，如果不需要该功能，可以通过GPO取消选中自动设置功能。

[https://technet.microsoft.com/en-us/library/cc995062.aspx](https://technet.microsoft.com/en-us/library/cc995062.aspx)

[http://tektab.com/2012/09/26/setting-up-web-proxy-autodiscovery-protocol-wpad-using-dns/](http://tektab.com/2012/09/26/setting-up-web-proxy-autodiscovery-protocol-wpad-using-dns/)

**WSUS修复**

任何更新软件包或软件都应始终通过安全连接（至少为SSL）进行部署。有很多项目如后门软件和应用程序都在网络中传输。很多人利用这种技术获得初始访问和横向渗透。对于WSUS后门，这个网站有助于你进行正确的配置： [https://technet.microsoft.com/en-us/library/hh852346.aspx#bkmk_3.5.ConfigSSL](https://technet.microsoft.com/en-us/library/hh852346.aspx#bkmk_3.5.ConfigSSL) 



**检测**

预防控制是一个最低限度的检测，随着组织架构的成长，审计能力是必须的。

**PowerShell v5**

PowerShell v4和v5引入了许多值得欣赏的功能。在这里特别提到他们，因为我在我的攻击链中使用了Inveigh.ps1，但是与底层技术的检测不直接相关，只有“武器化矢量”。PowerShell攻击频率正在上升，任何正在改进网络检测的人都应该寻找并引入一定的措施来应对PowerShell攻击。

**事件日志**

尽管在大型网络中，日志的存储转发很困难，但从监测和收集这些日志所获得的价值来说我认为是完全值得的。在这种攻击链的情况下，似乎最好的日志记录是添加集合是c: windows  windowsupdate.log文件。“WindowsUpdateClient”源和17或19的系统事件日志将显示已下载/安装的更新的名称。

在这种情况下，DNS日志的记录也将非常有用。假设组织怀疑被wpad投毒，在没有控制的情况下将新工作站引入环境，或者当前工作站被禁用，则他们将告警。

**WMI事件描述**

****

我们的团队是一个对WMI的进攻和防守巨大的支持者。 你可能已经看到了马特•格雷伯最近的twitter，如这里，他提供WMI签名，将提供周围值得监测的警报事件。 ATD的Hunt能力主管Jared Atkinson开发了一个名为Uproot的工具，它实际上是一个使用WMI Event Subscription的无代理IDS主机。

在我们这个例子下，我们可以创建WMI事件过滤器：“HKEY_USERS  &lt;USER-GUID&gt;  Software  Microsoft  Windows  CurrentVersion  Internet Settings  Wpad”下的网络配置文件。此外，你可以在创建或修改wpad.dat文件时，获取临时删除的 &lt;USER APP DATA&gt;  Local  Microsoft  Windows  Temporary Internet Files  Content.IE5 ”文件。



**<strong style="font-size: 18px">结论**</strong>

虽然我没有在这篇文章中介绍任何新工具，我的目标是拼凑几个不错的工具，以展示一个有趣的攻击链和鼓励创造性的技术。 此外，我希望能够阐明我在大型企业环境中仍然常见的几种错误配置。
