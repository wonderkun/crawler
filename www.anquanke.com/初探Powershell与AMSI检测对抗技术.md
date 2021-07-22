> 原文链接: https://www.anquanke.com//post/id/168210 


# 初探Powershell与AMSI检测对抗技术


                                阅读量   
                                **447212**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t0124a2c4d177d90417.png)](https://p5.ssl.qhimg.com/t0124a2c4d177d90417.png)

作者：counsellors

> 作为Windows系统内置工具， Powershell脚本的功能十分强大，同时作为系统的功能组件不会被常规杀毒引擎查杀。兼具这两个有点，Powershell的恶意利用程序得到快速发展，从2012年Powershell 攻击利用工具成型化以来，互联网中的通过无文件与Powershell的攻击事件数量逐年递增。无文件攻击在感染计算机时，不需写入磁盘即可从事恶意活动，绕过那些基于签名和文件检测的传统安全软件。 如何检测这些恶意行为成了安全厂商和企业用户与个人更为关心的问题。微软在2015年中旬开始提出了针对无文件攻击和Powershell脚本攻击的检测缓解方案-AMSI。
本文以Powershell行为日志审计为切入点， 展开介绍AMSI的功能，工作机制与现有绕过方法。

## 0x00 Powershell 攻击

Powershell作为内网渗透的利器， 在Windows环境下被广泛使用。利用Poweshell可以降低软件的查杀概率，同时也是无文件攻击的常用手段。在内网渗透中Powershell扮演着重要角色。

### 一般渗透攻击过程

[![](https://p3.ssl.qhimg.com/t012c5df043317b20c7.png)](https://p3.ssl.qhimg.com/t012c5df043317b20c7.png)

Powershell可以用于入侵，下载，权限维持，横向移动等攻击阶段。

### 常用利用工具

Powersploit和Nishang是老牌后渗透利用框架，集成了后门，提权，信息收集，RCE等功能。

Powershell Empire和PSAttack都是不依赖于powershell.exe的PowerShell利用框架。它们分别使用python和.NET重新封装了脚本解释器，执行相关渗透脚本。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016217245c3400efa9.png)

### Powershell与.NET攻击利用时间线

传统安全软件对Powershell的防御不甚完善，通过Powershell进行网络勒索，挖矿的恶意软件越来越多，攻击方式也越来越复杂。

[![](https://p0.ssl.qhimg.com/t01ff12afbe482eb149.png)](https://p0.ssl.qhimg.com/t01ff12afbe482eb149.png)



## 0x01 Powershell 日志与版本

本文不对Powershell语法做阐述，攻击利用的命令与代码可以参考开源工具。除了攻击利用，本文将关注点放在Powershell日志和版本上。

### Powershell日志

#### 日志类型

##### 模块(module)日志

Event ID: 4103

路径： Microsoft &gt; Windows &gt; PowerShell/Operational

作用：可以为 Windows PowerShell 模块启用日志记录

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0170d59b3a14267761.png)

[![](https://p2.ssl.qhimg.com/t015df620272df32c1d.png)](https://p2.ssl.qhimg.com/t015df620272df32c1d.png)

使用下面命令可以获取或有可用的模块名称：

Get-Module -ListAvailable

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0159b98749eba18a84.png)

##### 管道执行(pipeline execute)日志

Event ID: 800

作用：记录Powershell管道执行过程的事件简介

[![](https://p0.ssl.qhimg.com/t01eb501cc1cbb17fd7.png)](https://p0.ssl.qhimg.com/t01eb501cc1cbb17fd7.png)

##### 脚本块(script block)日志

Event ID: 4104

路径：Microsoft-Windows-PowerShell/Operational

作用：Windows PowerShell 将记录命令、脚本块、函数和脚本的处理，无论是以交互方式调用还是通过自动方式处理

[![](https://p3.ssl.qhimg.com/t01a6152073b9bd00fb.png)](https://p3.ssl.qhimg.com/t01a6152073b9bd00fb.png)

##### 脚本转换(transcription)日志

可以将 Windows PowerShell 命令的输入和输出捕获到基于文本的脚本中。

[![](https://p1.ssl.qhimg.com/t0168bf329f26509ec8.png)](https://p1.ssl.qhimg.com/t0168bf329f26509ec8.png)

当然，开启 transcription有个bug

[![](https://p1.ssl.qhimg.com/t01ad560a669ad96032.png)](https://p1.ssl.qhimg.com/t01ad560a669ad96032.png)

#### 如何打开日志记录功能

这四种日志功能默认不开启，需要手工开启

[![](https://p2.ssl.qhimg.com/t01f59459de312ee317.png)](https://p2.ssl.qhimg.com/t01f59459de312ee317.png)

#### 4种日志记录内容对比
<td valign="top" width="111">日志详情</td><td valign="top" width="111">模块日志</td><td valign="top" width="111">管道执行日志</td><td valign="top" width="111">脚本块日志</td><td valign="top" width="111">脚本转换日志</td>
<td valign="top" width="111">执行命令</td><td valign="top" width="111">有</td><td valign="top" width="111">有</td><td valign="top" width="111">有（包括脚本内容）</td><td valign="top" width="111">有</td>
<td valign="top" width="111">上下文信息</td><td valign="top" width="111">有</td><td valign="top" width="111">有</td><td valign="top" width="111">无</td><td valign="top" width="111">有</td>
<td valign="top" width="111">参数绑定详情</td><td valign="top" width="111">有</td><td valign="top" width="111">有</td><td valign="top" width="111">无</td><td valign="top" width="111">无</td>
<td valign="top" width="111">解码/解混淆代码</td><td valign="top" width="111">无</td><td valign="top" width="111">无</td><td valign="top" width="111">有</td><td valign="top" width="111">有</td>
<td valign="top" width="111">命令输出</td><td valign="top" width="111">无</td><td valign="top" width="111">无</td><td valign="top" width="111">无</td><td valign="top" width="111">有</td>

### Powershell版本

#### Powershell个版本对日志的支持度
<td valign="top" width="111">日志类型</td><td valign="top" width="78">V2版本</td><td valign="top" width="66">V3版本</td><td valign="top" width="123">V4版本</td><td valign="top" width="175">V5版本</td>
<td valign="top" width="111">模块日志</td><td valign="top" width="78">无</td><td valign="top" width="66">支持</td><td valign="top" width="123">支持（V3增强）</td><td valign="top" width="175">支持</td>
<td valign="top" width="111">管道执行日志</td><td valign="top" width="78">支持</td><td valign="top" width="66">支持</td><td valign="top" width="123">支持</td><td valign="top" width="175">支持</td>
<td valign="top" width="111">脚本块日志</td><td valign="top" width="78">无</td><td valign="top" width="66">无</td><td valign="top" width="123">支持</td><td valign="top" width="175">支持（自动记录恶意命令）</td>
<td valign="top" width="111">脚本转换日志</td><td valign="top" width="78">无</td><td valign="top" width="66">无</td><td valign="top" width="123">支持</td><td valign="top" width="175">支持（V4增强）</td>

#### 不同操作系统的默认Powershell版本
<td valign="top" width="250">操作系统</td><td valign="top" width="152">默认Powershell版本</td><td valign="top" width="184">可支持Powershell版本</td>
<td valign="top" width="217">Windows Server 2008(SP2)</td><td valign="top" width="152">2.0</td><td valign="top" width="184">3.0</td>
<td valign="top" width="217">Windows Server 2008 R2(SP1)</td><td valign="top" width="152">5.1</td><td valign="top" width="184">5.1</td>
<td valign="top" width="217">Windows Server 2012</td><td valign="top" width="152">3.0</td><td valign="top" width="184">5.1</td>
<td valign="top" width="217">Windows Server 2012(R2)</td><td valign="top" width="152">4.0</td><td valign="top" width="184">5.1</td>
<td valign="top" width="217">Windows 7(SP1)</td><td valign="top" width="152">5.1</td><td valign="top" width="184">5.1</td>
<td valign="top" width="217">Windows 8</td><td valign="top" width="152">3.0</td><td valign="top" width="184">5.1</td>
<td valign="top" width="217">Windows 8.1</td><td valign="top" width="152">4.0</td><td valign="top" width="184">5.1</td>
<td valign="top" width="217">Windows 10</td><td valign="top" width="152">5.0</td><td valign="top" width="184">5.1</td>



## 0x02 关于AMSI

### 简介

AMSI（Antimalware Scan Interface）， 即反恶意软件扫描接口。在Windows Server 2016和Win10上默认安装并启用。

使用案例：通过远程URL访问，在不落地的情况下执行PS代码，但是会被AMSI检测拦截。

[![](https://p5.ssl.qhimg.com/t0117ca0616ba42d5f9.png)](https://p5.ssl.qhimg.com/t0117ca0616ba42d5f9.png)

大家在使用Powershell脚本进行Windows环境渗透测试时，可能会遇到上图中的报错情况，比如Nishang、Empire、PowerSploit和其他比较知名的PowerShell脚本。而这一错误的产生原因即为AMSI防护的结果。

[![](https://p0.ssl.qhimg.com/t01e2bbaf5ed5d0bb73.png)](https://p0.ssl.qhimg.com/t01e2bbaf5ed5d0bb73.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01af321a014c75f665.png)

### 说明

Win10 AMSI标准允许系统上安装的杀毒软件对系统进行深度的监控扫描，而且无需用户参与。允许基于AMSI接口的安全软件，通过AMSI接口扫描文件，内存、数据流等，进行内容源的URL/IP认证检查，并采用技术手段识别恶意行为。帮助用户更加方便有效地防范基于动态脚本的恶意软件和其他攻击行为。

### 检测对象
- 文件
<li style="list-style-type: none;">
</li>- 内存
- 数据流
### 检测目的
- 对抗基于脚本的攻击检测
- 对抗无文件攻击检测
### 可检测到的攻击手段
1. Powershell.exe执行的脚本
1. 不使用powershell.exe的情况下运行脚本
1. 使用单独的runspace（[p0wnedshell](https://github.com/Cn33liz/p0wnedShell)，[psattack](https://github.com/jaredhaight/PSAttack)）
1. System.Automation.Dll（[nps](https://github.com/Ben0xA/nps)，[Powerpick](https://github.com/PowerShellEmpire/PowerTools/tree/master/PowerPick)）
1. 从WMI命名空间、注册表键和事件记录日志中加载脚本
1. 应用白名单绕过方式－InstallUtil,，regsrv32和rundll32。
### 配置AMSI

Win10 与Windows Server 2016默认是AMSI默认杀毒软件是Windows Defender。

[![](https://p0.ssl.qhimg.com/t0135162557c782d489.png)](https://p0.ssl.qhimg.com/t0135162557c782d489.png)

如果已经安装360安全卫士，请在“设置中心”-“开启Defender”中，勾选开启Windows Defender防护。

[![](https://p2.ssl.qhimg.com/t0181118f1b5c7b99ea.png)](https://p2.ssl.qhimg.com/t0181118f1b5c7b99ea.png)

### 软件支持
<td valign="top" width="277">安全产品</td><td valign="top" width="277">支持状况</td>
<td valign="top" width="277">Microsoft Defender</td><td valign="top" width="277">支持</td>
<td valign="top" width="277">AVG Protection 2016.7496</td><td valign="top" width="277">支持</td>
<td valign="top" width="277">ESET Version 10</td><td valign="top" width="277">支持</td>
<td valign="top" width="277">BitDefender</td><td valign="top" width="277">支持</td>
<td valign="top" width="277">Avast</td><td valign="top" width="277">支持</td>
<td valign="top" width="277">McAfee Endpoint Security 10.6.0</td><td valign="top" width="277">支持</td>
<td valign="top" width="277">Trend Micro</td><td valign="top" width="277">支持</td>
<td valign="top" width="277">Kaspersky 2019</td><td valign="top" width="277">支持</td>
<td valign="top" width="277">Avira</td><td valign="top" width="277">准备支持</td>
<td valign="top" width="277">F-Secure</td><td valign="top" width="277">不支持</td>



## 0x03 AMSI工作原理

AMSI不是独立运行的，而是一种可交互接口。

### AMSI与Windows Defender的关系

[![](https://p3.ssl.qhimg.com/t0197b280e613217305.jpg)](https://p3.ssl.qhimg.com/t0197b280e613217305.jpg)

Windows Defender ATP主要使用机器学习，通过模型发现威胁。

AMSI是与Windows Defender相对独立的模块，Windows Defender是默认的 AMSI Provider。

### 整体框架



[![](https://p2.ssl.qhimg.com/t0169e15919206755a2.jpg)](https://p2.ssl.qhimg.com/t0169e15919206755a2.jpg)

### 主要执行流程
1. 应用开发者使用AMSI API检测
[![](https://p2.ssl.qhimg.com/t01cad9839a66c9b15e.png)](https://p2.ssl.qhimg.com/t01cad9839a66c9b15e.png)

图中红色表示订阅AMSI事件的安全软件，也就是AMSI提供器。在脚本引擎Powershell( System.Management.Automation.dll) 和 Windows Script Host(Jscript.dll)执行内容时，他们会通过amsi.dll的导出函数把内容传给AMSI提供器。

这里曾经出现一个安全漏洞，零字符截断绕过AMSI检测，流程如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ad70cb6c49b90583.png)

恶意代码evilcode由于字符串截断没有送入到ASMI Provider中进行安全检查。
1. 安全产品供应商使用的检测接口
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b7efd6797b70efcb.png)



## 0x04 如何绕过AMSI

### 降级攻击

PowerShell v2版不支持AMSI，作为常用手段，将目标主机中的PowerShell降级至PowerShell v2简单快捷。

### 混淆

虽然文章开始给的脚本经过base64编码后依然能被AMSI检测，但是增强混淆程度也是绕过AMSI的有效方法之一。

以下是绕过字符串检测，执行“被禁止”代码的3种方法：

[![](https://p1.ssl.qhimg.com/t0123cb4266d599391f.png)](https://p1.ssl.qhimg.com/t0123cb4266d599391f.png)

简单地将单词分成两部分，就足以欺骗这种检测方案。我们在混淆过程中，发现了很多这样的情况。但在大多数情况下，这种方法可能会失败。

[![](https://p1.ssl.qhimg.com/t011740ec0ba1d13a13.png)](https://p1.ssl.qhimg.com/t011740ec0ba1d13a13.png)

当然，也可以使用XOR来欺骗AMSI，并在运行时将字符串解码到内存中。这是更为有效的方式，因为需要更高级的技术来对其进行检测。

### 禁用AMSI
- 修改注册表，将HKCU\Software\Microsoft\Windows Script\Settings\AmsiEnable的表项值置为0。
- 关闭Windows Defender使系统自带的AMSI检测无效化。
[![](https://p2.ssl.qhimg.com/t011d93e830937a3659.png)](https://p2.ssl.qhimg.com/t011d93e830937a3659.png)

执行完结果

[![](https://p1.ssl.qhimg.com/t010d9df88705ef1295.png)](https://p1.ssl.qhimg.com/t010d9df88705ef1295.png)
- 利用反射将内存中AmsiScanBuffer方法的检测长度置为0。
[![](https://p3.ssl.qhimg.com/t0195c2ae8bf077c01f.png)](https://p3.ssl.qhimg.com/t0195c2ae8bf077c01f.png)

### COM劫持

寻找优先加载并无效的COM表项，在注册表中将Provider的路径指向到无效路径。这样，Powershell中的AMSI功能将无法加载，从而失效。

[![](https://p1.ssl.qhimg.com/t01f5e22eefc7d11210.png)](https://p1.ssl.qhimg.com/t01f5e22eefc7d11210.png)

劫持之后的效果

[![](https://p1.ssl.qhimg.com/t01b7f382cdad8ecffb.png)](https://p1.ssl.qhimg.com/t01b7f382cdad8ecffb.png)

当然这个漏洞在2017年5月份的16232已经修复了，不过还可以通过DLL劫持绕过AMSI。

### DLL劫持

首先，我们先看下应用程序导入DLL优先级（Windows XP SP2以后版本）
1. 进程对应的应用程序所在目录；
1. 系统目录（通过 GetSystemDirectory 获取）；
1. 16位系统目录；
1. Windows目录（通过 GetWindowsDirectory 获取）；
1. 当前目录；
1. PATH环境变量中的各个目录；
可以看到第一条，与应用程序同级的目录的dll会被优先加载。利用这一点。我们在C:\Windows\System32\WindowsPowerShell\v1.0下放置一个伪造AMSI.dll，就可以实现DLL劫持，而不会调用系统的amsi.dll（C:\Windows\System32\asmi.dll, 如下）。

系统AMSI.dll路径，如下：

[![](https://p0.ssl.qhimg.com/t01e125bca32c8986b3.png)](https://p0.ssl.qhimg.com/t01e125bca32c8986b3.png)



## 0x05 缓解方案
1. 开启全部系统日志并分析;
1. 至少开启Powershell脚本块，Sysmon和进程创建日志;
1. 安装4.0以上版本Powershell;
1. 卸载或者禁用2.0版本Powershell;
1. 开启Powershell的相关安全机制如APPLocker，Device Guard, Credential Guard 等;
1. 使用AMSI并关注绕过技术.


## 0x06 参考文献

[https://www.anquanke.com/post/id/107097](https://www.anquanke.com/post/id/107097)

[https://blogs.msdn.microsoft.com/daviddasneves/2017/05/25/powershell-security-at-enterprise-customers/](https://blogs.msdn.microsoft.com/daviddasneves/2017/05/25/powershell-security-at-enterprise-customers/)

[https://www.anquanke.com/post/id/84618](https://www.anquanke.com/post/id/84618)

[https://blogs.technet.microsoft.com/mmpc/2015/06/09/windows-10-to-offer-application-developers-new-malware-defenses](https://blogs.technet.microsoft.com/mmpc/2015/06/09/windows-10-to-offer-application-developers-new-malware-defenses)
