> 原文链接: https://www.anquanke.com//post/id/167566 


# 疑似朝鲜APT组织发起针对学术界目标的钓鱼攻击


                                阅读量   
                                **379909**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者arbornetworks，文章来源：asert.arbornetworks.com
                                <br>原文地址：[https://asert.arbornetworks.com/stolen-pencil-campaign-targets-academia/](https://asert.arbornetworks.com/stolen-pencil-campaign-targets-academia/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0141f49708ae8fa5b1.jpg)](https://p5.ssl.qhimg.com/t0141f49708ae8fa5b1.jpg)



## 摘要

近日，ASERT发现了可能来自朝鲜的APT活动，该攻击活动应发生在2018年5月及以前，活动一直瞄准学术机构，被命名为“STOLEN PENCIL”。攻击的动机尚不明确，但攻击者很擅长隐藏行踪而不被发现。攻击者通过向目标用户发送鱼叉式网络钓鱼电子邮件，而将其引导至包含诱饵文档的网站，并提示用户安装恶意Google Chrome扩展程序。一旦用户下载该程序，攻击者就会使用现成的工具来确保它可以长久的驻留在用户设备中，包括远程桌面协议（RDP）访问。



## 攻击特征
1. 钓鱼邮件的目的为诱导用户安装位于学术界的网站的恶意Chrome扩展软件。
1. 许多大学的受害者都拥有生物医学工程专业知识，这可能表明了攻击者瞄准的动机。
1. 由于该组织使用的OPSEC非常糟糕，用户在打开浏览器时显示的是韩语，英韩互译翻译工具也打开了，输入法也是韩语。
1. 攻击者使用内置的Windows管理工具和商业化的软件来明目张胆的进行攻击行为。例如使用RDP（远程桌面协议）来访问受感染的系统，而不是使用后门或远程访问特洛伊木马（RAT）。
1. 恶意程序会通过各种来源（如进程内存，Web浏览器，网络嗅探和键盘记录程序）获取密码。
1. 暂时没有发现数据被盗的证据，因此无法确定STOLEN PENCIL背后的动机。


## 钓鱼行为

[![](https://p5.ssl.qhimg.com/t01a1b3aa47b8fef23e.png)](https://p5.ssl.qhimg.com/t01a1b3aa47b8fef23e.png)<br>
STOLEN PENCIL攻击者使用鱼叉式网络钓鱼作为他们的攻击起点，邮件中包含了几个恶意域名中的其中一个。目前确定的恶意域名包括：

```
client-message[.]com
world-paper[.]net
docsdriver[.]com
grsvps[.]com
coreytrevathan[.]com
gworldtech[.]com
```

除了以上的顶级域名（TLD）之外，还有一些恶意子域名：

```
aswewd.docsdriver[.]com
facebook.docsdriver[.]com
falken.docsdriver[.]com
finder.docsdriver[.]com
government.docsdriver[.]com
keishancowan.docsdriver[.]com
korean-summit.docsdriver[.]com
mofa.docsdriver[.]com
northkorea.docsdriver[.]com
o365.docsdriver[.]com
observatoireplurilinguisnorthkorea.docsdriver[.]com
oodwd.docsdriver[.]com
twitter.docsdriver[.]com
whois.docsdriver[.]com
www.docsdriver[.]com
```

针对学术界的钓鱼页面会在IFRAME中显示正常的PDF。然后，它会重定向用户到Chrome Web Store中安装“Font Manager”扩展程序。

[![](https://p2.ssl.qhimg.com/t01ecd85bd66679be97.png)](https://p2.ssl.qhimg.com/t01ecd85bd66679be97.png)

现已从Chrome Web Store里面下架的的恶意扩展程序还保留着攻击者使用被感染账户留下的评论。评论的内容是从其他类似的程序评论里复制粘贴过来的，并且都给该扩展程序打了五星好评，即使文本是差评。有些用户说他们在误下载恶意程序后立即删除了它们，因为它阻止了Chrome浏览器正常运行。这可能表明，错误或编写粗糙的代码使用了太多资源来保障其恶意功能和隐蔽功能。

恶意的Chrome扩展程序声明了在浏览器中的每个URL上运行的权限：

[![](https://p3.ssl.qhimg.com/t01b94dc53e39b4f84f.png)](https://p3.ssl.qhimg.com/t01b94dc53e39b4f84f.png)

恶意扩展程序会从一个单独的站点加载JavaScript，但目前只发现一个合法的jQuery代码的文件，这可能是攻击者为了阻止被分析所做出的行为。但是其实从外部站点加载此jQuery.js是没有意义的，因为软件本身也包含了这段代码。

[![](https://p1.ssl.qhimg.com/t015f406cdf1a32072c.png)](https://p1.ssl.qhimg.com/t015f406cdf1a32072c.png)

鉴于恶意扩展允许攻击者从受害者访问的所有网站读取数据，而且在一些受害者的帐户上也观察到了电子邮件转发，因此分析人员认为攻击者的攻击目的是窃取浏览器cookie和密码。

# <a class="reference-link" name="%E6%94%BB%E5%87%BB%E5%B7%A5%E5%85%B7"></a>攻击工具

一旦恶意软件入侵用户设备，STOLEN PENCIL攻击者就会使用微软的远程桌面协议（RDP）进行远程点击访问，攻击者使用命令行和服务器控制受害者设备。通过观察，研究人员发现RDP访问时间集中在UTC时间06：00-09：00（美国东部时间01：00-04：00）。在其中一个案例中，攻击者将受害者的键盘布局改为了韩语。

STOLEN PENCIL攻击者还使用受损或被盗的证书签署了该活动中使用的多个PE文件。
<li>MECHANICAL<br>
该文件将键击记录到%userprofile%appdataroamingapach.`{`txt,log`}`，并且具备类似于“cryptojacker”的功能，该功能的主要作用是用0x33883E87807d6e71fDc24968cefc9b0d10aC214E替换以太坊钱包地址，此以太坊钱包地址目前无余额且无交易。</li>
<li>GREASE<br>
该文件用于添加具有特定用户名/密码的Windows管理员帐户并启用RDP的工具，可以绕过任何防火墙规则。目前发现的用户名/密码组合为：<br>
LocalAdmin/Security1215!<br>
dieadmin1/waldo1215!<br>
dnsadmin/waldo1215!<br>
DefaultAccounts/Security1215!<br>
defaultes/1qaz2wsx#EDC</li>
大多数MechanicalICAL和GREASE样本中使用的证书如下所示：

[![](https://p5.ssl.qhimg.com/t01868f715df43b3ec5.png)](https://p5.ssl.qhimg.com/t01868f715df43b3ec5.png)

攻击者使用了一些工具来自动化入侵，同时，研究人员还发现了一个工具集的ZIP，证明了攻击者有盗窃密码并传播的意图。在zip文件中，有以下工具：
1. KPortScan – 基于GUI的portscanner
1. PsExec – 在Windows系统上远程执行命令的工具
1. 用于启用RDP和绕过防火墙规则的批处理文件
1. Procdump – 转储进程内存的工具，以及用于转储lsass进程以进行密码提取的批处理文件
1. Mimikatz – 转储密码和哈希的工具
1. 用于留存在受害设备中的攻击套件，以及用于快速扫描和利用的批处理文件
1. Nirsoft Mail PassView – 转储已保存邮件密码的工具
1. Nirsoft网络密码恢复 – 转储已保存的Windows密码的工具
1. Nirsoft远程桌面PassView – 转储已保存的RDP密码的工具
1. Nirsoft SniffPass – 一种嗅探网络以查找通过不安全协议发送的密码的工具
1. Nirsoft WebBrowserPassView – 一种转储存储在各种浏览器中的密码的工具
显然，此工具集用于清除存储在各种位置的密码。攻击者在使用被盗密码后，后门帐户和强制开放RDP服务的组合使攻击者在受损系统上保持长久存在。



## 建议
1. 建议用户不要点击电子邮件中的任何可疑链接，即使他们来自他们信任的人。
1. 建议用户警惕安装浏览器扩展软件的提示，即使它们托管在官方扩展站点上。
1. 谨慎对待包含网络钓鱼域链接的电子邮件。
1. 使用防火墙将RDP访问限制设置为仅需要它的系统，并随时监控可能的RDP连接。
1. 查找可疑的、新创建的管理帐户。


## 结论

虽然研究人员已经能够深入了解STOLEN PENCIL背后攻击者的TTP（工具，技术和程序），但这显然只是攻击活动其中的一小部分而已，攻击者所使用的技术相对基础。他们使用的大部分工具为现成的软件和一些设备本身所具有的权限，而朝鲜攻击者恰好惯用此攻击手法。此外，攻击者在浏览过的网站记录和键盘选择中都暴露了他们使用韩语。攻击者花费了大量时间和资源对目标进行侦察，甚至在恶意Chrome程序下载页面上留下的评论。他们的主要目的似乎是通过窃取的凭据以获取对受害者系统的访问权并试图长期利用。



## IOC

### <a class="reference-link" name="MECHANICAL%20hashes"></a>MECHANICAL hashes

```
9d1e11bb4ec34e82e09b4401cd37cf71
8b8a2b271ded23c40918f0a2c410571d
```

### <a class="reference-link" name="GREASE%20hashes"></a>GREASE hashes

```
2ec54216e79120ba9d6ed2640948ce43
6a127b94417e224a237c25d0155e95d6
fd14c377bf19ed5603b761754c388d72
1d6ce0778cabecea9ac6b985435b268b
ab4a0b24f706e736af6052da540351d8
f082f689394ac71764bca90558b52c4e
ecda8838823680a0dfc9295bdc2e31fa
1cdb3f1da5c45ac94257dbf306b53157
2d8c16c1b00e565f3b99ff808287983e
5b32288e93c344ad5509e76967ce2b18
4e0696d83fa1b0804f95b94fc7c5ec0b
af84eb2462e0b47d9595c21cf0e623a5
75dd30fd0c5cf23d4275576b43bbab2c
98de4176903c07b13dfa4849ec88686a
09fabdc9aca558bb4ecf2219bb440d98
1bd173ee743b49cee0d5f89991fc7b91
e5e8f74011167da1bf3247dae16ee605
0569606a0a57457872b54895cf642143
52dbd041692e57790a4f976377adeade
```

### <a class="reference-link" name="DOMAINS"></a>DOMAINS

```
bizsonet.ayar[.]biz
bizsonet[.]com
client-message[.]com
client-screenfonts[.]com
.coreytrevathan[.]com (possibly compromised legitimate site)
docsdriver[.]com
grsvps[.]com
.gworldtech[.]com (possibly compromised legitimate site)
itservicedesk[.]org
pqexport[.]com
scaurri[.]com
secozco[.]com
sharedriver[.]pw
sharedriver[.]us
tempdomain8899[.]com
world-paper[.]net
zwfaxi[.]com
```

### <a class="reference-link" name="IP"></a>IP

```
104.148.109[.]48
107.175.130[.]191
132.148.240[.]198
134.73.90[.]114
172.81.132[.]211
173.248.170[.]149
5.196.169[.]223
74.208.247[.]127
92.222.212[.]0
```
