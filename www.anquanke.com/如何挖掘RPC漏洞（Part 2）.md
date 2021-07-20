> 原文链接: https://www.anquanke.com//post/id/176034 


# 如何挖掘RPC漏洞（Part 2）


                                阅读量   
                                **385903**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者fortinet，文章来源：fortinet.com
                                <br>原文地址：[https://www.fortinet.com/blog/threat-research/rpc-bug-hunting-case-studies---part-2.html](https://www.fortinet.com/blog/threat-research/rpc-bug-hunting-case-studies---part-2.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t015771d9367abf00eb.gif)](https://p5.ssl.qhimg.com/t015771d9367abf00eb.gif)



## 一、前言

在之前的一篇[文章](https://www.fortinet.com/blog/threat-research/the-case-studies-of-microsoft-windows-remote-procedure-call-serv.html)中（[译文](https://www.anquanke.com/post/id/167427)），FortiGuard实验室与大家分享了如何使用RPCView来寻找RPC服务器中的逻辑漏洞，最终我们在Microsoft Universal Telemetry服务中发现了一个潜在问题。

大家可能还记得，在上篇文章中我们讨论了如何通过RPCView寻找输入参数为字符串的RPC API。然而，使用RPCView时有一些限制条件，比如RPCView不会显示Windows没有在默认情况下自动启动的RPC服务（如Data Sharing Service）。之前我们无法识别这个服务，现在我们可以使用另一种方法来识别该服务（下文会介绍）。经过分析后我们发现，这个服务同样存在一些权限提升问题，而使用我们增强版的方法可以发现这些问题。

Google安全研究员James Forshaw最终反馈了4个安全漏洞，MSRC已于去年12月份修复这些漏洞。此外，虽然RPCView非常有用，但使用起来也比较耗时，我们需要逐项审核接收字符串参数的所有API。因此，我们希望能找到节省时间的其他办法。

我们首先分析了之前发现的一些bug，这些bug非常相似，都有一个共同点：这些服务都会调用`SetNamedSecurityInfo`这个Windows API，该API允许应用程序通过对象名称，在指定对象的安全描述符中设置指定的安全信息。例如，如果操作目标为文件对象，那么应用程序就可以指定文件名。

这里我们想强调一点，这个Windows API并没有存在任何安全问题，然而当我们使用自己开发的静态分析工具来搜索RPC服务时，可以将该API当成过滤器来使用。了解到这一点后，我们创建了一个简单工具，可以静态解析所有的RPC服务程序，寻找感兴趣的Windows API，进一步缩小需要深入研究的RPC服务范围。

经过分析后，我们发现了一些比较有趣的RPC服务。比如Storage Service（也称为StorSvc），该服务中存在之前尚未发现的多个权限提升问题；还有AppX Deployment Server，该服务可能存在竞争条件问题，最终导致权限提升。FortiGuard实验室随后向微软安全响应中心（MSRC）反馈了这些漏洞，微软及时修复了这些漏洞，对应的编号为[CVE-2019-0569](https://fortiguard.com/zeroday/FG-VD-18-145)以及[CVE-2019-0766](https://fortiguard.com/zeroday/FG-VD-18-151)。

接下来我们将与大家分享我们发现这些漏洞的具体过程。

```
[+] Target: appidsvc.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary DACL modification: appidsvc.dll
[+] Target: AppVEntSubsystemController.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: AppVEntSubsystemController.dll
[+] Target: AppXDeploymentServer.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: AppXDeploymentServer.dll
       [*] Potential DLL with arbitrary deletion: AppXDeploymentServer.dll
       [*] Potential executable with arbitrary file modification with move: AppXDeploymentServer.dll
       [*] Potential DLL with arbitrary DACL modification: AppXDeploymentServer.dll
[+] Target: bdesvc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: bdesvc.dll
[+] Target: bisrv.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary DACL modification: bisrv.dll
[+] Target: combase.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary deletion: combase.dll
       [*] Potential executable arbitrary deletion: combase.dll
[+] Target: cryptcatsvc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: cryptcatsvc.dll
       [*] Potential executable with arbitrary file modification with move: cryptcatsvc.dll
[+] Target: cryptsvc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: cryptsvc.dll
[+] Target: dhcpcore.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: dhcpcore.dll
[+] Target: dhcpcore6.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: dhcpcore6.dll
[+] Target: DiagSvc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: DiagSvc.dll
[+] Target: diagtrack.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary deletion: diagtrack.dll
       [*] Potential executable arbitrary deletion: diagtrack.dll
       [*] Potential executable with arbitrary file modification with move: diagtrack.dll
       [*] Potential DLL with arbitrary DACL modification: diagtrack.dll
[+] Target: DmApiSetExtImplDesktop.dll
       [*] Is RPC server file
[+] Target: dot3svc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: dot3svc.dll
[+] Target: dpapisrv.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: dpapisrv.dll
[+] Target: dssvc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: dssvc.dll
       [*] Potential DLL with arbitrary deletion: dssvc.dll
       [*] Potential executable with arbitrary file modification with move: dssvc.dll
       [*] Potential DLL with arbitrary DACL modification: dssvc.dll
[+] Target: dusmsvc.dll
       [*] Is RPC server file
[+] Target: edgehtml.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: edgehtml.dll
       [*] Potential DLL with arbitrary deletion: edgehtml.dll
       [*] Potential executable with arbitrary file modification with move: edgehtml.dll
       [*] Potential DLL with arbitrary DACL modification: edgehtml.dll
[+] Target: eeprov.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: eeprov.dll
[+] Target: efslsaext.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary deletion: efslsaext.dll
       [*] Potential executable arbitrary deletion: efslsaext.dll
[+] Target: FXSAPI.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: FXSAPI.dll
[+] Target: FXSSVC.exe
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: FXSSVC.exe
       [*] Potential DLL with arbitrary deletion: FXSSVC.exe
       [*] Potential executable with arbitrary file modification with move: FXSSVC.exe
[+] Target: iphlpsvc.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary DACL modification: iphlpsvc.dll
[+] Target: LogonController.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: LogonController.dll
[+] Target: lsasrv.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: lsasrv.dll
       [*] Potential executable with arbitrary file modification with move: lsasrv.dll
[+] Target: mispace.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary deletion: mispace.dll
       [*] Potential executable arbitrary deletion: mispace.dll
[+] Target: modernexecserver.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary DACL modification: modernexecserver.dll
[+] Target: msdtcprx.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: msdtcprx.dll
       [*] Potential executable with arbitrary file modification with move: msdtcprx.dll
       [*] Potential DLL with arbitrary DACL modification: msdtcprx.dll
       [*] Potential executable with arbitrary file modification with move: msdtcprx.dll
[+] Target: netlogon.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: netlogon.dll
       [*] Potential executable with arbitrary file modification with move: netlogon.dll
[+] Target: p2psvc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: p2psvc.dll
[+] Target: PackageStateRoaming.dll
       [*] Is RPC server file
[+] Target: pcasvc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: pcasvc.dll
       [*] Potential executable with arbitrary file modification with move: pcasvc.dll
[+] Target: PeerDistSvc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: PeerDistSvc.dll
       [*] Potential DLL with arbitrary deletion: PeerDistSvc.dll
       [*] Potential executable with arbitrary file modification with move: PeerDistSvc.dll
[+] Target: PhoneProviders.dll
       [*] Is RPC server file
[+] Target: pla.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary DACL modification: pla.dll
       [*] Potential executable arbitrary deletion: pla.dll
       [*] Potential DLL with arbitrary deletion: pla.dll
[+] Target: pnrpsvc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: pnrpsvc.dll
[+] Target: profsvc.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary deletion: profsvc.dll
       [*] Potential executable arbitrary deletion: profsvc.dll
       [*] Potential DLL with arbitrary DACL modification: profsvc.dll
[+] Target: rasmans.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: rasmans.dll
       [*] Potential executable with arbitrary file modification with move: rasmans.dll
       [*] Potential DLL with arbitrary DACL modification: rasmans.dll
[+] Target: rdpclip.exe
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: rdpclip.exe
[+] Target: scesrv.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: scesrv.dll
       [*] Potential DLL with arbitrary DACL modification: scesrv.dll
[+] Target: schedsvc.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary deletion: schedsvc.dll
       [*] Potential executable arbitrary deletion: schedsvc.dll
       [*] Potential DLL with arbitrary DACL modification: schedsvc.dll
[+] Target: SessEnv.dll
       [*] Is RPC server file
       [*] Potential executable with arbitrary file modification with move: SessEnv.dll
       [*] Potential executable arbitrary deletion: SessEnv.dll
       [*] Potential DLL with arbitrary deletion: SessEnv.dll
[+] Target: Spectrum.exe
       [*] Is RPC server file
       [*] Potential DLL with arbitrary deletion: Spectrum.exe
[+] Target: spoolsv.exe
       [*] Is RPC server file
       [*] Potential executable with arbitrary file modification with move: spoolsv.exe
       [*] Potential executable arbitrary deletion: spoolsv.exe
[+] Target: sstpsvc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: sstpsvc.dll
[+] Target: StorSvc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: StorSvc.dll
       [*] Potential DLL with arbitrary deletion: StorSvc.dll
       [*] Potential DLL with arbitrary DACL modification: StorSvc.dll
[+] Target: sysmain.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: sysmain.dll
       [*] Potential executable with arbitrary file modification with move: sysmain.dll
       [*] Potential DLL with arbitrary DACL modification: sysmain.dll
[+] Target: SystemEventsBrokerServer.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: SystemEventsBrokerServer.dll
       [*] Potential executable with arbitrary file modification with move:
[+] Target: tapisrv.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: tapisrv.dll
[+] Target: taskcomp.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: taskcomp.dll
       [*] Potential DLL with arbitrary DACL modification: taskcomp.dll
[+] Target: tellib.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary deletion: tellib.dll
       [*] Potential executable arbitrary deletion: tellib.dll
       [*] Potential executable with arbitrary file modification with move: tellib.dll
       [*] Potential DLL with arbitrary DACL modification: tellib.dll
[+] Target: termsrv.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary DACL modification: termsrv.dll
[+] Target: trkwks.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: trkwks.dll
       [*] Potential executable with arbitrary file modification with move: trkwks.dll
[+] Target: tttracer.exe
       [*] Is RPC server file
       [*] Potential executable with arbitrary file modification with move: tttracer.exe
       [*] Potential DLL with arbitrary DACL modification: tttracer.exe
[+] Target: uireng.dll
       [*] Is RPC server file
       [*] Potential executable with arbitrary file modification with move: uireng.dll
       [*] Potential DLL with arbitrary deletion: uireng.dll
       [*] Potential executable arbitrary deletion: uireng.dll
[+] Target: usermgr.dll
       [*] Is RPC server file
       [*] Potential executable with arbitrary file modification with move: usermgr.dll
       [*] Potential DLL with arbitrary DACL modification: usermgr.dll
[+] Target: vaultsvc.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary deletion: vaultsvc.dll
       [*] Potential executable arbitrary deletion: vaultsvc.dll
       [*] Potential executable with arbitrary file modification with move: vaultsvc.dll
[+] Target: vmrdvcore.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary deletion: vmrdvcore.dll
       [*] Potential executable arbitrary deletion: vmrdvcore.dll
       [*] Potential executable with arbitrary file modification with move: vmrdvcore.dll
[+] Target: w32time.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary DACL modification: w32time.dll
[+] Target: wevtsvc.dll
       [*] Is RPC server file
       [*] Potential executable with arbitrary file modification with move: wevtsvc.dll
       [*] Potential executable arbitrary deletion: wevtsvc.dll
       [*] Potential DLL with arbitrary DACL modification: wevtsvc.dll
[+] Target: wiaservc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: wiaservc.dll
[+] Target: wifinetworkmanager.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: wifinetworkmanager.dll
       [*] Potential DLL with arbitrary deletion: wifinetworkmanager.dll
[+] Target: wimserv.exe
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: wimserv.exe
       [*] Potential DLL with arbitrary deletion: wimserv.exe
[+] Target: Windows.Internal.Bluetooth.dll
       [*] Is RPC server file
[+] Target: wininit.exe
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: wininit.exe
       [*] Potential executable with arbitrary file modification with move: wininit.exe
[+] Target: winlogon.exe
       [*] Is RPC server file
       [*] Potential executable with arbitrary file modification with move: winlogon.exe
[+] Target: wlansvc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: wlansvc.dll
       [*] Potential executable with arbitrary file modification with move: wlansvc.dll
[+] Target: wwansvc.dll
       [*] Is RPC server file
       [*] Potential executable arbitrary deletion: wwansvc.dll
       [*] Potential executable with arbitrary file modification with move: wwansvc.dll
[+] Target: XblGameSave.dll
       [*] Is RPC server file
       [*] Potential DLL with arbitrary deletion: XblGameSave.dll
       [*] Potential executable arbitrary deletion: XblGameSave.dll
       [*] Potential executable with arbitrary file modification with move: XblGameSave.dll
```

清单1. 静态解析器过滤出的RPC可执行文件



## 二、Microsoft Windows Storage Service任意文件覆盖漏洞：CVE-2019-0569

分析解析器的输出结果时（参考清单1），我们发现`StorSvc.dll`包含我们需要的导入API。逆向分析DLL组件后，我们找到了一个接口：`BE7F785E-0E3A-4AB7-91DE-7E46E443BE29`。逆向分析该接口对外公开的RPC API时，我们发现`SvcSetStorageSettings`较为有趣。这个API会创建目录名能够预测的一些Windows目录。当我们将正确的参数传递给该API时，外部驱动器卷的根目录中将创建如下文件夹：

```
Documents
Videos
Pictures
Downloads
Music
```

大家可能已经注意到，这些目录名与用户根目录（即`%USERPROFILE%`）下的默认目录名相同。然而问题是，只有当外部硬盘驱动器卷存在时，这个RPC API才会创建这些目录。当RPC API被触发时，我们可以看到与下图类似的Process Monitor输出结果：

[![](https://p1.ssl.qhimg.com/t0164f66aed4c5de590.png)](https://p1.ssl.qhimg.com/t0164f66aed4c5de590.png)

图1. `SvcSetStorageSettings`创建文件名已知的多个目录

根据Process Monitor的输出结果，因为这个RPC API会创建能够预测的一些目录，因此容易受到符号链接攻击影响。根据Process Monitor的调用栈信息，我们可以精确定位特定`CreateFile`事件中涉及到的相关函数。当分析这些函数时，我们很快就发现`StorageService::CreateStorageCardDirectory`中存在问题，该函数在创建认证用户所能访问的文件和目录时缺少模拟（impersonation）机制，允许攻击者通过符号链接（symlink）修改任意文件对象的ACL。

我们来分析如下代码片段：

```
StorageService::CreateStorageCardDirectory()
`{`
       dwFileAttributes = GetFileAttributesW(&amp;FileName);
       if ( dwFileAttributes != -1 &amp;&amp; !(dwFileAttributes &amp; FILE_ATTRIBUTE_DIRECTORY) ) // -- (1)
       `{`
               DeleteFileW(&amp;FileName);                            
               dwFileAttributes = -1;
       `}`

       if (CreateDirectoryW(&amp;FileName, lpSecurityAttributes) )     // -- (2)
       `{`
               if (dwFileAttributes != -1 &amp;&amp; (ExistingFileAttributes | 0x10) != (dwFileAttributes &amp; 0xFFFFFFDF) )
                      SetFileAttributesW(&amp;FileName, ExistingFileAttributes | 0x10)
       `}`
       else if (GetLastError() == ERROR_ALREADY_EXISTS)
       `{`
result = SetNamedSecurityInfoW(&amp;FileName, SE_FILE_OBJECT, SECURITY_DACL_INFORMATION, 0, 0, NewAcl, 0);                                                        // -- (3)
               boolSetNameddSecInfo = result &lt; 0;
               if ( result &gt; 0 )
               `{`
                      result = (unsigned __int16)result | 0x80070000;
                      boolSetNameddSecInfo = result &lt; 0;
               `}`
               if (!boolSetNameddSecInfo)
               `{`
                      dwFileAttributes = GetFileAttributesW(&amp;FileName);
                      SetFileAttributesW(&amp;FileName, ExistingFileAttributes | 0x10)
               `}`
       `}`
`}`
```

清单2. `StorageService::CreateStorageCardDirectory`中缺乏模拟机制

如果攻击者成功创建了一个符号链接，将`FileName`重定向到攻击者所需的文件对象，那么就可以在上述代码标签(3)处使用`NewAcl`来修改被重定向文件对象的ACL（`NewAcl`为当前登录用户的ACL）。

在发起符号链接攻击之前，我们需要满足代码中标签（2）和标签（3）的检查条件。简而言之，如果出现文件名冲突，那么这几行代码就会删除文件，尝试创建名称相同的目录。需要注意的是，在创建目录之前，代码首先会执行`DeleteFileW`，删除指向目标文件的符号链接。那么我们如何避免符号链接被删除呢？

事实证明，如果调用方进程以独占方式打开了`FileName`对应的文件句柄，那么就可以轻松绕过这个限制。这样操作后，即使`DeleteFileW`调用失败、返回拒绝访问错误，整个代码也会继续执行，因为代码并没有检查API调用返回时是否存在错误。

设置指向目标文件的符号链接并创建该文件的独占句柄后，我们可以触发`SvcSetStorageSettings`修改任意文件对象的ACL。如下图所示，我们使用`SvcSetStorageSettings`中的漏洞来修改Windows目录中文件的ACL，而正常情况下非特权用户无法修改该文件的ACL。

[![](https://p2.ssl.qhimg.com/t011566d5e1aa0aba0c.png)](https://p2.ssl.qhimg.com/t011566d5e1aa0aba0c.png)

图2. 利用`SvcSetStorageSettings` RPC API漏洞



## 三、Microsoft AppX Deployment Server任意文件创建漏洞：CVE-2019-0766

继续研究解析器的输出结果，我们找到了存在同样符号攻击漏洞的另一个服务：Windows AppX Deployment Service，该服务同样缺乏模拟机制。

在安装从Microsoft Store上下载的AppX软件包时，我们发现AppX Deployment Service会将AppX可执行文件及对应的资源存放到如下可预测的文件路径中：

```
E:\WpSystem\&lt;current_logged_in_user_sid&gt;\AppData\Local\Packages\Microsoft.AppX.Package.Name
```

因此，如果该服务会修改释放出的文件的ACL，那么我们就可以采用相同的符号攻击操作（请注意，这里`E:`驱动器为我们测试系统上的外部驱动器）。大家可能会注意到这与前面的场景有些类似，但我们首先需要确定这个文件路径的可访问性。

我们可以使用`icacls`命令来确定文件和目录的可访问性，结果表明当前登录用户具备该目录的完整访问权限：

```
C:\&gt;icacls E:\WpSystem\S-1-5-21-2264505789-2271452246-4192020221-1001\AppData\Local\Packages\Microsoft.MicrosoftMahjong_8wekyb3d8bbwe
E:\WpSystem\S-1-5-21-2264505789-2271452246-4192020221-1001\AppData\Local\Packages\Microsoft.MicrosoftMahjong_8wekyb3d8bbwe
NT AUTHORITY\SYSTEM:(CR)(F)
NT AUTHORITY\SYSTEM:(OI)(CI)(IO)(CR)(F)
DESKTOP-A7ABC1O\researcher:(CR)(F)
DESKTOP-A7ABC1O\researcher:(OI)(CI)(IO)(CR)(F)
BUILTIN\Administrators:(CR)(F)
BUILTIN\Administrators:(OI)(CI)(IO)(CR)(F)
NT AUTHORITY\SYSTEM:(I)(OI)(CI)(F)
BUILTIN\Administrators:(I)(OI)(CI)(F)
DESKTOP-A7ABC1O\researcher:(I)(OI)(CI)(F)

C:\&gt;icacls E:\WpSystem\S-1-5-21-2264505789-2271452246-4192020221-1001\AppData\Local\Packages
E:\WpSystem\S-1-5-21-2264505789-2271452246-4192020221-1001\AppData\Local\Packages
NT AUTHORITY\SYSTEM:(I)(OI)(CI)(F)
BUILTIN\Administrators:(I)(OI)(CI)(F)
DESKTOP-A7ABC1O\researcher:(I)(OI)(CI)(F)

C:\&gt;icacls E:\WpSystem\S-1-5-21-2264505789-2271452246-4192020221-1001\AppData\Local
E:\WpSystem\S-1-5-21-2264505789-2271452246-4192020221-1001\AppData\Local        
NT AUTHORITY\SYSTEM:(I)(OI)(CI)(F)
BUILTIN\Administrators:(I)(OI)(CI)(F)
DESKTOP-A7ABC1O\researcher:(I)(OI)(CI)(F)

C:\&gt;icacls E:\WpSystem\S-1-5-21-2264505789-2271452246-4192020221-1001\AppData            
E:\WpSystem\S-1-5-21-2264505789-2271452246-4192020221-1001\AppData     
NT AUTHORITY\SYSTEM:(I)(OI)(CI)(F)
BUILTIN\Administrators:(I)(OI)(CI)(F)
DESKTOP-A7ABC1O\researcher:(I)(OI)(CI)(F)

C:\&gt;icacls E:\WpSystem\S-1-5-21-2264505789-2271452246-4192020221-1001                                     
E:\WpSystem\S-1-5-21-2264505789-2271452246-4192020221-1001    
NT AUTHORITY\SYSTEM:(OI)(CI)(F)
BUILTIN\Administrators:(OI)(CI)(F)
DESKTOP-A7ABC1O\researcher:(OI)(CI)(F)
```

显然，普通用户账户可以修改高权限服务所共享的资源。我们有多种方法来验证该问题的确存在：如前文所示，我们可以使用Process Monitor来捕捉在AppX软件包安装过程中生成的事件，然后查找`SetSecurityFile`事件来确定具体的代码路径。这里我们换种思路，采用静态分析方法来分析`AppXDeploymentServer.dll`，这个DLL组件中包含该服务处理逻辑的具体实现。

最终我们找到了如下代码片段，这些代码与目录创建操作有关。

```
// After created its parent directories, try to create E:\WpSystem\&lt;SID&gt;\AppData\Local\Packages\&lt;AppX.PackageName&gt;
        if ( CreateDirectoryW(*(LPCWSTR *)(this - 28), 0) )           // -- (1)
          v16 = 0;
        else
          v16 = getlasterror();
        v15 = *(void **)(this + 4);
        if ( v16 &lt; 0 )
        `{`
          v17 = 0x4C8;
          goto exit;
        `}`
      `}`
      v15 = *(void **)(this + 4);
      if ( v16 &gt;= 0 )
      `{`
        if ( v13 == 1
          || sub_102335C9(v15)
            // Set security descriptor on e:\WPSystem and its sub-directories to allow Administrator and System user access only
          || (v19 = wpsystem_setnamedsecurityinfo((int)v12, *(WCHAR **)(this - 16)),
              v15 = *(void **)(this + 4),
              v16 = v19,
              v19 &gt;= 0) )
        `{`
          // Encrypt and compress the files in Appx.Package
          v20 = EncryptFile((int)v12, *(WCHAR **)(this - 16));     // -- (2)
          v15 = *(void **)(this + 4);
          v16 = v20;
          if ( v20 &gt;= 0 )
          `{`
            // Reset security descriptor on \\?\E:\WpSystem\&lt;SID&gt;\AppData\Local\Packages\&lt;AppX.PackageName&gt; to allow full access
           // however, neither no verification is done on the assigned object name therefore it can be replaced with file object instead of directory object and impersonation here
            v21 = SetNamedSecurityInfoW(*(LPWSTR *)(this - 28), SE_FILE_OBJECT, DACL_SECURITY_INFORMATION, 0, 0, *(PACL *)(this - 20), 0);            // -- (3)
```

清单3. `AppXDeploymentServer.dll`中缺乏用户模拟机制

如上代码所示，标签（1）处会创建AppX软件包目录，标签（3）处会通过`SetNamedSecurityInfoW`设置安全描述符，这两处可能存在竞争条件，如果竞争成功，攻击者就可以修改任意文件对象的ACL。

为了验证这一点，我们的目标是重定向AppX目录名（`SetNamedSecurityInfoW`的第一个参数，参考标签（3）处），利用符号链接将其重定向至我们选择的任意文件对象。

在执行该操作之前，我们需要将默认保存位置设置为外部驱动器，这一点非常重要。在Windows 10中，我们可以通过“控制面板”的“默认保存位置”来设置该选项，但我们希望通过程序来完成该操作。在前面一个例子中，我们可以使用`SvcSetStorageSettings` RPC API来直接修改默认保存位置，但在程序中定义RPC接口是非常繁琐的操作，因此我们想要更加简单的实现方法。

事实上，大多数RPC API都是封装在一个DLL组件中，通过DLL导出函数对外提供服务。由于微软并没有公开文档描述已封装的RPC API导出函数，并且这些API大多数由Windows系统组件来实现，因此为了寻找这个DLL，我们需要在`%WINDIR\SYSTEM32`目录中搜索对应的RPC UUID。当我们使用对应的UUID（`BE7F785E-0E3A-4AB7-91DE-7E46E443BE29`）搜索`SvcSetStorageSettings`接口时，我们找到了`StorageUsage.dll`，从中找到了一个未公开的API：`SetStorageSettings`。因此，现在我们可以使用`LoadLibrary()`和`GetProcAddress()`来动态调用这个API。

最终，我们构造并运行PoC，使用Process Monitor来分析竞争条件，如下图所示：

[![](https://p4.ssl.qhimg.com/t011e71152c64c4a0a6.png)](https://p4.ssl.qhimg.com/t011e71152c64c4a0a6.png)

图3. 无限循环线程PoC

a）PoC正在执行无限循环线程操作，尝试删除清单3标签（1）处代码所创建的AppX文件夹

b）AppX Deployment Service成功创建AppX文件夹

c）随后，我们的PoC线程成功删除该文件夹

[![](https://p0.ssl.qhimg.com/t015eb7ff824e821b7b.png)](https://p0.ssl.qhimg.com/t015eb7ff824e821b7b.png)

图4. PoC修改ACL

d）此时，AppX Deployment Server尝试调用`wpsystem_setnamedsecurityinfo`修改目录及子目录的安全描述符。然而，由于a）处准备删除该文件，因此该操作无法执行成功。

e）此时执行清单3标签（2）处代码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d4df7a7599087159.png)

图5. 成功利用竞争条件

成功利用竞争条件后，在清单3标签（3）处代码执行前，我们的PoC就可以创建指向任意文件（这里为`C:\Windows\system32\license.rtf`）的符号链接。

g）最终，目标文件的安全描述符会被特权服务成功修改。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01af19106b83b8c9d1.png)

图6. 成功利用竞争条件覆盖任意文件对象



## 四、总结

在本文中，我们与大家分享了如何进一步缩小待分析的RPC服务范围，寻找是否存在本地提权问题。到目前为止这种方法非常有效，已经帮助我们在多个组件中发现了类似漏洞。

FortiGuard实验室已经发布相应的IPS特征（`MS.RPC.AppXSvc.Privilege.Escalation`以及`MS.RPC.AppXSvc.Privilege.Escalation`），能够检测到这类问题，可以帮助我们的客户免受此类问题影响。
