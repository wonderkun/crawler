> 原文链接: https://www.anquanke.com//post/id/198009 


# 对Avira VPN权限提升漏洞的分析及存疑


                                阅读量   
                                **820332**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01220421d8bc61afe6.jpg)](https://p1.ssl.qhimg.com/t01220421d8bc61afe6.jpg)



## 逻辑漏洞及分析方法

区别于常规的内存型漏洞，逻辑漏洞通常是指通过滥用系统机制，歪曲程序设计者意图，实现设计者意料之外目的的严重的软件缺陷。逻辑漏洞通常源于程序设计逻辑的不完备、验证的的不严格或者是由于系统测试的不充分而导致的。

关注逻辑漏洞一方面是这种类型的漏洞广泛存在，满足一定的条件时漏洞利用非常简单、稳定；另一方面也是因为由于软件安全性的增强、各种内存防护措施的加入使得内存性漏洞的发现、利用都很困难。因此，目前逻辑漏洞的挖掘和利用越来越引起人们的注意。

逻辑漏洞通常都与系统资源操作权限管理上的缺陷有关。常见的逻辑挖掘模型是通过研究目标与系统交互的接口与方法（也就是通常所说的攻击界面），筛查对这些接口的访问权限的分配及管理是否存在安全缺陷，结合存在问题的上下文环境研究漏洞的利用方法。形成了逻辑类漏洞挖掘的基本流程和挖掘模型。

[![](https://p4.ssl.qhimg.com/t010e0d9e078347bcc5.png)](https://p4.ssl.qhimg.com/t010e0d9e078347bcc5.png)

目前，已经有一些成熟的工具可用于执行系统攻击界面的查找，如[NtObjectManager](https://www.powershellgallery.com/packages/NtObjectManager)、[OleViewDotNet](https://github.com/tyranid/oleviewdotnet/releases)等。由于Powershell具有脚本编写方便灵活点，同时又能够充分利用.Net类型和COM对象特性，能简单地与各种系统交互，完成各种复杂的、自动化操作的特点，以上工具都使用PowerShell来实现。在理解windows系统内部对象管理方法的基础上，灵活应用这些挖掘工具和PoweShell提供的一些内置命令就能够方便地完成对目标系统攻击界面的查找，并且辅助研究者确定是否存在潜在的安全漏洞。

最近网上公布了[Avira VPN服务存在权限提升漏洞](https://enigma0x3.net/2020/01/15/avira-vpn-local-privilege-escalation-via-insecure-update-location/)，初略看了一些觉得文章对漏洞的成因说得很清楚，很符合逻辑漏洞的特点，研究者对漏洞的分析、利用方面也有自己的特点。但是细想来对文章部分内容也存有一定的疑惑，于是准备对这个漏洞进行一番验证。验证环境为

OS:Windows 7 6.1 Build 7601

Avira：Phant Vpn 2.28.3.20557



## 漏洞基本描述

漏洞存在的主要成因是，当Avira VPNService启动时，会检查是否要安装升级程序。服务更新程序位于C:\ProgramData\Avira\VPN\Update目录下，而该目录可以被低权限用户写。

同时，VPNServices实现的一些反利用措施能够被绕过，从而造成攻击者通过放置一个有效的Avira可执行程序及一个恶意的dll文件到“C:\ProgramData\Avira\VPN\Update”目录下。在VPN服务执行更新的过程中，借助dll劫持实现以System权限执行代码。

在Windows各对象的访问权限中，安全研究人员通常较为关心攻击者是否拥有目标对象的写权限。NtObjectManager模块提供了用于查证目标对象访问权限的Cmdlet—GetAccessibleFile，并且还特别提供了Pid参数用于查证进程的访问权限。通常情况下，该参数可以指定一个沙箱进程或者低权限进程。如，以下命令可以列举出对Windows\System32目录下具备写权限的所有目录及文件对象。

```
Get-AccessibleFile \??\c:\windows\system32 -AccessRights WriteData -DirectoryAccessRights AddFile -Recurse -ProcessIds 1234
```

在笔者的实验环境中，新安装的Avira默认情况下VPN下并不存在Update目录。而当Update目录出现时，只有Administer/system/Service才具有对该目录的控制权限，普通用户根本无法访问。

[![](https://p5.ssl.qhimg.com/t01778d52228dbd26ad.png)](https://p5.ssl.qhimg.com/t01778d52228dbd26ad.png)

[![](https://p5.ssl.qhimg.com/t01b56e671bbeb90def.png)](https://p5.ssl.qhimg.com/t01b56e671bbeb90def.png)

笔者估计是Avira版本较新，补丁已经被修补的原因。网上下载的其他Avira版本及单独的Avira.VpnService安装程序，在安装过程中都会先到官方网站上下载最新的Avira.VpnService，从而使得复现这个漏洞比较困难。



## 关于漏洞查证的基本步骤

逆向Avira.VpnService时，发现该程序是使用解释型语言编写的，使用Reflector或者IL 5.0可以得到很好的反编译效果。在IL中选择使用C#语言进行反编译，可以得到可读性非常好的源代码，稍微具备C#的知识都能完成该代码的阅读与分析。

当Phantom VPN Service启动的时候，首先会对检查当前是否存在更新文件，通常更新文件存放在C:\ProgramData 目录下。执行文件检查的函数是VPNUpdater.UpdateProduct()，该函数最终会调用“Updater.UpdateToNewPackageIfValid()”处理与升级相关的逻辑。

[![](https://p2.ssl.qhimg.com/t0163164616eac0553b.png)](https://p2.ssl.qhimg.com/t0163164616eac0553b.png)

首先调用Updater.CheckForDownloadedUpdatePackage()对升级文件进行检查，检查是否在update目录下存在一个名为AviraVPNInstaller.exe的升级文件，然后再检查该文件是否已经完成安装。

[![](https://p5.ssl.qhimg.com/t01369a8acb3dfe211d.png)](https://p5.ssl.qhimg.com/t01369a8acb3dfe211d.png)

如果更新程序的版本大于“Avira.VPNService.exe”的版本，那么说明文件没有被安装，要执行安装过程。否则说明无需安装，直接删除下载的安装程序包。

[![](https://p2.ssl.qhimg.com/t01a7f76a317c96682c.png)](https://p2.ssl.qhimg.com/t01a7f76a317c96682c.png)

如果升级文件存在且还未被安装，那么服务将执行升级文件夹锁闭过程，使得低权限用户不具有对该目录的写权限（确保在升级前不被修改）。函数“Updater.IsUpdateFolderAccessRestricted()”首先检查目录的所有者是否为如下三个用户NT AUTHORITY\SYSTEM, NT  AUTHORITY\SERVICE或者 Administrators之一（以下称三个特定用户）。

[![](https://p1.ssl.qhimg.com/t0151e829ffbfb1903e.png)](https://p1.ssl.qhimg.com/t0151e829ffbfb1903e.png)

如果目录的所有者不是三个特定用户之一（NT AUTHORITY\SYSTEM、NT  AUTHORITY\SERVICE、Administrators），AcceptedSIDS.Any返回False，最终导致IsUpdateFolderAccessRestricted返回False。随后程序流程调用RestoreUpdateFolder()函数。

RestoreUpdateFolder()函数的主要流程就是删除Update目录，调用CreateUpdateFolder重新创建该目录并设置该目录的访问权限信息。

[![](https://p5.ssl.qhimg.com/t01115625ad2cfca651.png)](https://p5.ssl.qhimg.com/t01115625ad2cfca651.png)

SetAccessRulesForUpdateFolder函数先删除创建该目录时继承下来的原有的访问控制规则，然后为上面提到的三个用户添加到控制规则中。（这一点似乎与原文提到的，低权限用户拥有对该目录的读写权限有冲突。目录创建时已经删除了其他用户的DACL，而仅添加三个特定用户的DACL，为什么低权限用户还能访问该目录）

继续IsUpdateFolderAccessRestricted函数流程。

[![](https://p1.ssl.qhimg.com/dm/1024_192_/t01685629d4e7df76f7.png)](https://p1.ssl.qhimg.com/dm/1024_192_/t01685629d4e7df76f7.png)

From …in循环逐一检查目录DACL列表的每一条规则，查看该目录的DACL列表中是否存在除以上三个特定用户之外的DACL规则。如果存在返回Flase，否则返回True。（也就是说目录只能由以上三个特定用户控制目录内容）。



## 访问控制规则绕过方法

按照原文的说明，对update目录属主的检查可以使用向目录“C:\ProgramData\Avira\Update” 移动特定属性的文件来绕过。Logfiles目录的属主为SYSTEM用户，且低权限用户具有完成的访问控制权限，在同一个文件卷下移动文件或目录可以保持相同的属性。那么先将恶意文件放置在Logfiles目录中再移动到Update目录下就可以实现对文件属主检查的绕过。

使用Get-Acl查看目录C:\Programdata\Avira\Launcher\Logfiles的访问权限如下：

[![](https://p3.ssl.qhimg.com/t01f9a327249a32599d.png)](https://p3.ssl.qhimg.com/t01f9a327249a32599d.png)

但是，在实际验证过程中发现执行Move-item操作时会发生错误。原因还是目录C:\ProgramData\Avira\Update被设置为只有三个特定用户具备访问控制，低权限用户无法实现对该目录的写操作。

接下来还要设置Update目录的DACL属性。

[![](https://p1.ssl.qhimg.com/t01239ed434022aaca6.png)](https://p1.ssl.qhimg.com/t01239ed434022aaca6.png)

执行以上命令后即完整设置了对象的安全访问属性。因为SDDL的内容可读性较差，可以使用以下操作查看一下权限设置的具体内容。

[![](https://p5.ssl.qhimg.com/t01d5e275a6e6819394.png)](https://p5.ssl.qhimg.com/t01d5e275a6e6819394.png)

可见，实现绕过的核心还是低权限用户对Update目录的读写能力。



## 文件完整性检查绕过

验证文件签名的函数是IsUpdatePackageAuthentic。函数首先检验文件是否具有有效的数字签名，在检验是否经过Avira的签名。如果文件没有被Avira签名或者签名信息错误，升级操作将中止。

[![](https://p0.ssl.qhimg.com/t0143fa211788e2b13d.png)](https://p0.ssl.qhimg.com/t0143fa211788e2b13d.png)

绕过方法签名验证的方法是寻找一个文件版本大于Avira.VPNService.exe且已经经过Avira签名的文件。在这里作者选择了CefSharp.BrowserSubprocess.exe，该程序版本信息为“65.0.0.0”。

[![](https://p2.ssl.qhimg.com/t01edb4f78b2c2a6e79.png)](https://p2.ssl.qhimg.com/t01edb4f78b2c2a6e79.png)

查看Avira.VPN的版本情况，有如下信息：

[![](https://p2.ssl.qhimg.com/t01517796a32b667c44.png)](https://p2.ssl.qhimg.com/t01517796a32b667c44.png)

因此使用CefSharp.BrowserSubprocess.exe程序作为宿主能够有效绕过Avira的完成性校验。需要说明的是，CefSharp.BrowserSubprocess.exe程序在启动时会加载当前目录下名为version.dll的文件。这种情况在自研软件中是较为常见的情况，因为开发者通常会编写一些dll供自己使用。

按照作者的说明，将CefSharp.BrowserSubprocess.exe及恶意version.dll文件拷贝到C:\Programdata\Avira\Launcher\Logfiles目录中，并将CefSharp.BrowserSubprocess.exe更名为AviraVPNInstaller.exe，然后再移动到Update目录下。执行以上操作后就可以绕过Avira的安全防护检查，当执行更新操作时就会加载恶意version.dll文件。



## 后记

在实际验证过程中，由于C:\ProgramData\Avira\VPN\ Update目录的访问权限问题，无法在本地实际验证漏洞利用的全部过程。也发推向作者咨询过，但没有回音。发此除讨论逻辑漏洞的挖掘、分析方法，同时也希望大家能一起讨论。

其次，作者对于一些验证措施的绕过也具有一定的借鉴意义。
