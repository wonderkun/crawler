> 原文链接: https://www.anquanke.com//post/id/187895 


# Windows访问令牌窃取攻防技术研究


                                阅读量   
                                **632023**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Justin Bui，文章来源：https://posts.specterops.io/
                                <br>原文地址：[https://posts.specterops.io/understanding-and-defending-against-access-token-theft-finding-alternatives-to-winlogon-exe-80696c8a73b](https://posts.specterops.io/understanding-and-defending-against-access-token-theft-finding-alternatives-to-winlogon-exe-80696c8a73b)

译文仅供参考，具体内容表达以及含义原文为准

# [![](https://p5.ssl.qhimg.com/t015775193a0c680736.png)](https://p5.ssl.qhimg.com/t015775193a0c680736.png)

## 0x00 前言

在本文中，我们介绍了访问令牌窃取的相关概念，以及如何在`winlogon.exe`上利用该技术从管理员上下文中模拟`SYSTEM`访问令牌。MITRE ATT&amp;CK将该技术归为[**Access Token Manipulation**](https://attack.mitre.org/techniques/T1134/)（访问令牌操控）类别。

如果本地管理员账户因为某些组策略（Group Policy）设置无法获取某些权限，此时模仿`SYSTEM`访问令牌是非常有用的一种技术。比如，本地管理员组可能不具备`SeDebugPrivilege`权限，这样就能加大攻击者转储凭据或者与其他进程内存交互的难度。然而，管理人员无法从`SYSTEM`账户中撤销相关权限，因为这是操作系统正常运行的基础。因此，在加固环境中，`SYSTEM`访问令牌对攻击者而言具有非常高的价值。

了解操控访问令牌的概念后，我将介绍如何使用系统访问控制列表（SACL）来审计进程对象，以便检测恶意操控访问令牌的攻击行为。这种检测技术有一个缺点：防御方必须清楚哪些进程是攻击者的目标。

最后，本文探索了还有哪些`SYSTEM`进程可以替代`winlogon.exe`，用来实施访问令牌模拟攻击，我也介绍了寻找这些进程的方法以及相关知识点。



## 0x01 窃取访问令牌

**备注：**如果大家对访问令牌控制技术比较了解，想深入了解如何寻找其他可用的`SYSTEM`进程，那么可以直接跳过这一节。

我们可以使用如下Windows API来窃取并滥用访问令牌：`OpenProcess()`、`OpenProcessToken()`、`ImpersonateLoggedOnUser()`、`DuplicateTokenEx()`以及`CreateProcessWithTokenW()`。

[![](https://p0.ssl.qhimg.com/t01f53f263795d32ea8.png)](https://p0.ssl.qhimg.com/t01f53f263795d32ea8.png)

图. 使用Windows API窃取访问令牌

`OpenProcess()`以进程标识符（PID）为参数，返回一个进程句柄，打开句柄时必须使用`PROCESS_QUERY_INFORMATION`、`PROCESS_QUERY_LIMITED_INFORMATION`或者`PROCESS_ALL_ACCESS`访问权限，这样`OpenProcessToken()`才能使用返回的进程句柄。

[![](https://p1.ssl.qhimg.com/t0191e16be4af37e93b.png)](https://p1.ssl.qhimg.com/t0191e16be4af37e93b.png)

图. OpenProcess文档

`OpenProcessToken()`以进程句柄及访问权限标志作为参数，用来打开访问令牌所关联进程的句柄。我们必须使用`TOKEN_QUERY`以及`TOKEN_DUPLICATE`访问权限打开令牌句柄，才能与`ImpersonateLoggedOnUser()`配合使用。我们也可以只使用`TOKEN_DUPLICATE`访问权限打开令牌句柄，与`DuplicateTokenEx()`配合使用。

[![](https://p2.ssl.qhimg.com/t014b079beeef0290b0.png)](https://p2.ssl.qhimg.com/t014b079beeef0290b0.png)

图. OpenProcessToken文档

利用`OpenProcessToken()`获取令牌句柄后，我们可以使用`ImpersonatedLoggedOnUser()`，使当前进程可以模拟已登录的另一个用户。该进程会继续模拟已登录的该用户，直到线程退出或者我们显示调用`RevertToSelf()`。

[![](https://p5.ssl.qhimg.com/t01e3b00f8881e1ee8e.png)](https://p5.ssl.qhimg.com/t01e3b00f8881e1ee8e.png)

图. ImpersonateLoggedOnUser文档

如果想以另一个用户身份运行进程，我们必须在`OpenProcessToken()`返回的令牌句柄上使用`DuplicateTokenEx()`，创建新的访问令牌。我们必须使用`TOKEN_ADJUST_DEFAULT`、`TOKEN_ADJUST_SESSIONID`、`TOKEN_QUERY`、`TOKEN_DUPLICATE以及TOKEN_ASSIGN_PRIMARY`访问权限来调用`DuplicateTokenEx()`，才能与`CreateProcessWithTokenW()`配合使用。`DuplicateTokenEx()`创建的访问令牌可以传入`CreateProcessWithTokenW()`，通过复制的令牌运行目标进程。

[![](https://p2.ssl.qhimg.com/t010085093c92d55591.png)](https://p2.ssl.qhimg.com/t010085093c92d55591.png)

图. DuplicateTokenEx文档

[![](https://p1.ssl.qhimg.com/t01c6208655d8d4aaf0.png)](https://p1.ssl.qhimg.com/t01c6208655d8d4aaf0.png)

图. CreateProcessWithTokenW文档

我整理了一些代码演示令牌操作过程，大部分代码借鉴了@[kondencuotas](https://twitter.com/kondencuotas)发表过的一篇[文章](https://ired.team/offensive-security/privilege-escalation/t1134-access-token-manipulation)。

大家可以访问[此处](https://github.com/justinbui/PrimaryTokenTheft)下载我的测试代码。



## 0x02 利用winlogon.exe提升至SYSTEM权限

在今年早些时候，[Nick Landers](https://twitter.com/monoxgas)介绍了从本地管理员提升到`NT AUTHORITY\SYSTEM`的一种简单[方法](https://t.co/gQdLHtmu98)。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fef5bd604dbbd63a.png)



在本地管理员（高完整性，high-integrity）上下文中，我们可以从`winlogon.exe`中窃取访问令牌，在当前线程中模拟`SYSTEM`，或者以`SYSTEM`运行新的进程。

[![](https://p2.ssl.qhimg.com/t01f21a22fea2786fde.png)](https://p2.ssl.qhimg.com/t01f21a22fea2786fde.png)

图. 从`winlogon.exe`中窃取`SYSTEM`令牌



## 0x03 检测技术

根据[官方描述](https://docs.microsoft.com/en-us/windows/win32/secauthz/access-control-lists)：

> [访问控制列表](https://docs.microsoft.com/windows/desktop/SecGloss/a-gly)（ACL）是包含[访问控制项](https://docs.microsoft.com/en-us/windows/win32/secauthz/access-control-entries)（ACE）的一个列表。ACL中的每个ACE都标识了一个[trustee](https://docs.microsoft.com/en-us/windows/win32/secauthz/trustees)结构，指定与trustee对应的[访问权限](https://docs.microsoft.com/en-us/windows/win32/secauthz/access-rights-and-access-masks)（允许、拒绝或者审核）。[可保护对象](https://docs.microsoft.com/en-us/windows/win32/secauthz/securable-objects)的[安全描述符](https://docs.microsoft.com/en-us/windows/win32/secauthz/security-descriptors)可以包含两种类型的ACL：DACL以及SACL。

我们的检测技术基于SACL（系统访问控制列表）构建。我们可以在进程对象上设置SACL，在Windows Security Log中记录成功/失败的访问操作。

我们可以使用[James Forshaw](https://twitter.com/tiraniddo)开发的[NtObjectManager](https://www.powershellgallery.com/packages/NtObjectManager/1.1.22)来轻松完成这个任务。在下文中，我们大量借鉴了James Forshaw的[研究成果](https://tyranidslair.blogspot.com/2017/10/bypassing-sacl-auditing-on-lsass.html)，文中提到了如何绕过对LSASS的SACL审计。在这篇文章的帮助下，我深入理解了SACL，也了解了如何使用`NtObjectManager`来控制SACL。

```
auditpol /set /category:"Object Access" /success:enable /failure:enable
$p = Get-NtProcess -name winlogon.exe -Access GenericAll,AccessSystemSecurity
Set-NtSecurityDescriptor $p “S:(AU;SAFA;0x1400;;;WD)” Sacl
```

来逐行分析上述代码。第一行启用系统审核功能，记录成功以及失败的对象访问操作。第二行以`GenericAll`及`AccessSystemSecurity`访问权限获得`winlogon.exe`进程的句柄。我们需要`AccessSystemSecurity`权限才能访问SACL。

第三行应用`ACE`类型（`AU`）审核策略，为来自`Everyone`（`WD`）组的成功/失败（`SAFA`）访问生成安全事件。这里需要注意`0x1400`，这是对`0x400`（`PROCESS_QUERY_INFORMATION`）以及`0x1000`（`PROCESS_QUERY_LIMITED_INFORMATION`）进行按位取或（`OR`）后的结果。这些访问权限（以及`PROCESS_ALL_ACCESS`）可以用来从指定进程对象中获取访问令牌。

部署完SACL后，当使用特定访问权限访问`winlogon.exe`时我们应该能看到一些警告信息。

### <a class="reference-link" name="%E5%9C%BA%E6%99%AF1%EF%BC%9APROCESS_QUERY_INFORMATION"></a>场景1：PROCESS_QUERY_INFORMATION

运行测试程序后，可以看到系统会生成EID（Event ID）4656，其中包括所请求的进程对象、发起访问请求的进程以及所请求的权限。“Access Mask”之所以为`0x1400`，是因为具备`PROCESS_QUERY_INFORMATION`访问权限的句柄也会被自动授予`PROCESS_QUERY_LIMITED_INFORMATION`访问权限。

[![](https://p5.ssl.qhimg.com/t016c0876824b9be4e3.png)](https://p5.ssl.qhimg.com/t016c0876824b9be4e3.png)

### <a class="reference-link" name="%E5%9C%BA%E6%99%AF2%EF%BC%9APROCESS_QUERY_LIMITED_INFORMATION"></a>场景2：PROCESS_QUERY_LIMITED_INFORMATION

我重新编译了测试程序，只请求`PROCESS_QUERY_LIMITED_INFORMATION`权限，然后重新运行程序。这次我们可以看到EID 4656事件，其中访问权限为`0x1000`，代表`PROCESS_QUERY_LIMITED_INFORMATION`访问权限。

[![](https://p1.ssl.qhimg.com/t01f6b932a58bdce6f6.png)](https://p1.ssl.qhimg.com/t01f6b932a58bdce6f6.png)



此外，我们还可以看到EID 4663，表示我们的测试程序在请求句柄后，会尝试访问进程对象。因此，我们能通过搜索EID 4656以及EID 4663，以较高的准确率检测利用访问令牌的操作。

[![](https://p2.ssl.qhimg.com/t014fe0a0bb67e08384.png)](https://p2.ssl.qhimg.com/t014fe0a0bb67e08384.png)

### <a class="reference-link" name="%E5%9C%BA%E6%99%AF3%EF%BC%9APROCESS_ALL_ACCESS"></a>场景3：PROCESS_ALL_ACCESS

重新编译测试程序，使用`PROCESS_ALL_ACCESS`访问权限后，我们能看到与场景2相同的EID，其中在EID 4656中，可以看到有程序在请求其他访问权限。

[![](https://p2.ssl.qhimg.com/t0159b67c06e2b373e9.png)](https://p2.ssl.qhimg.com/t0159b67c06e2b373e9.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012f87603154d1d500.png)

这里值得注意的是，EID 4663中的“Access Mask”为`0x1000`，这代表`PROCESS_QUERY_LIMITED_INFORMATION`访问权限。此外，当我们使用`PROCESS_QUERY_INFORMATION`访问权限运行测试程序时，系统会生成EID 4656，但不会生成EID 4663.



## 0x04 寻找其他进程

除了`winlogon.exe`之外，我比较好奇是否有其他`SYSTEM`进程能够作为令牌窃取的目标。如果存在这种进程，那它们与无法被窃取令牌的其他`SYSTEM`进程相比有什么不同？

### <a class="reference-link" name="%E9%AA%8C%E8%AF%81%E7%8C%9C%E6%83%B3"></a>验证猜想

首先，我想看一下是否有其他进程可以用来窃取`SYSTEM`令牌。我以运行在高完整性上下文的本地管理员身份暴力枚举了所有`SYSTEM`进程（包括`svchost.exe`），找到了能够窃取`SYSTEM`令牌的其他一些进程。这些进程为`lsass.exe`、`OfficeClickToRun.exe`、`dllhost.exe`以及`unsecapp.exe`。我将这些进程标识为“友好型”进程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d02b2d6d21b70758.png)

图. 从`unsecapp.exe`中窃取`SYSTEM`令牌

在遍历`SYSTEM`进程的过程中，我注意到对有些进程执行`OpenProcess()`操作时会返回拒绝访问错误（“System Error – Code 5”），导致后续执行失败。

对于某些`SYSTEM`进程，`OpenProcess()`会执行成功，但执行`OpenProcessToken()`时会出现拒绝访问错误。后面我将研究一下为什么会出现这种问题。

[![](https://p2.ssl.qhimg.com/t01c3aca431547bbd22.png)](https://p2.ssl.qhimg.com/t01c3aca431547bbd22.png)

### <a class="reference-link" name="%E6%BE%84%E6%B8%85%E5%8E%9F%E5%9B%A0"></a>澄清原因

我的目标是找到允许令牌操作的`SYSTEM`进程在安全设置上存在哪些不同，我决定比较一下`winlogon.exe`以及`spoolsv.exe`。这两个进程都是`SYSTEM`进程，但我只能从`winlogon.exe`中窃取`SYSTEM`访问令牌。

**Session ID**

我使用[Process Explorer](https://docs.microsoft.com/en-us/sysinternals/downloads/process-explorer)打开这两个进程，尝试手动探索这两者之间的不同点。我记得Nick在推特中提到过`winlogon.exe`的“Session ID”为`1`，这是最大的不同。

我将该进程与其他“友好型”进程作比较，发现其他进程的Session ID都为`0`。不幸的是，这并不是我想寻找的不同点。

[![](https://p5.ssl.qhimg.com/t01e34d78b9388a5763.png)](https://p5.ssl.qhimg.com/t01e34d78b9388a5763.png)

图. 比较两个“友好型”进程的Session ID

**Process Explorer中的高级安全设置**

我决定深入分析`winlogon.exe`以及`spoolsv.exe`在高级安全设置（Advanced Security Settings）上的区别。我注意到这两者在管理员组的高级权限上有所不同。对于`winlogon.exe`，管理员组具备“Terminate”、“Read Memory”以及“Read Permissions”权限，而`spoolsv.exe`上的管理员组并不具备这些权限。

[![](https://p2.ssl.qhimg.com/t0193b4fdd3d5c24155.png)](https://p2.ssl.qhimg.com/t0193b4fdd3d5c24155.png)

我试着在`spoolsv.exe`上应用所有权限，然后尝试窃取访问令牌。不幸的是，这种方法并不能弹出`SYSTEM`命令行窗口。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b17b1f9a556ac6c0.png)

我试着再次启动/停止进程，想看一下进程启动时能否应用这些权限，同样以失败告终。

**Get-ACL**

我决定在PowerShell中使用[Get-ACL](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl?view=powershell-6)来观察`winlogon.exe`以及`spoolsv.exe`所对应的安全描述符。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0179f1c99fdb30c9dd.png)

图. `winlogon.exe`及`spoolsv.exe`对应的Get-ACL结果

这两个进程对应的`Owner`、`Group`以及`Access`似乎完全相同。接下来我决定使用[ConvertFrom-SddlString](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/convertfrom-sddlstring?view=powershell-6)来解析`SDDL`（Security Descriptor Definition Language，安全描述符定义语言），来分析其中的不同点。

[![](https://p0.ssl.qhimg.com/t01106996b232ad8da5.png)](https://p0.ssl.qhimg.com/t01106996b232ad8da5.png)

图. `winlogon.exe`及`spoolsv.exe`对应的SDDL

`BUILTIN\Administrators`组对应的`DiscretionaryAcl`似乎相同。这里我有点无计可施，但还是想最后看一下Process Explorer。

**TokenUser以及TokenOwner**

再次在Process Explorer中观察高级安全设置，我发现所有“友好型”进程的`Owner`字段对应的都是本地管理员组。

[![](https://p4.ssl.qhimg.com/t0114ed66ce8cb355c8.png)](https://p4.ssl.qhimg.com/t0114ed66ce8cb355c8.png)

图. `winlogon.exe`及`unsecapp.exe`对应的`TokenOwner`字段

我将这个字段与无法窃取访问令牌的其他`SYSTEM`进程作比较，我发现`Owner`的确是一个不同的因素。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011f1cfb1b8940e452.png)

图. `spoolsv.exe`及`svchost.exe`的`TokenOwner`字段

我的小伙伴（@[jaredcatkinson](https://twitter.com/jaredcatkinson)）还提到一点，Process Explorer中的`Owner`字段实际上对应的是`TokenOwner`，并且我们可以使用[GetTokenInformation()](https://docs.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-gettokeninformation)来提取该信息。

我还在GitHub上找到一个非常方便的PowerShell脚本（[Get-Token.ps1](https://gist.github.com/vector-sec/a049bf12da619d9af8f9c7dbd28d3b56)），可以用来枚举所有进程以及线程令牌。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011a8539088de92f14.png)

图. 利用`Get-Token.ps1`解析出来的`winlogon.exe`所对应的令牌对象

观察`winlogon.exe`，我们可以看到`UserName`以及`OwnerName`字段的值有所不同。分析该脚本的具体实现，我发现这些字段对应的是[`TOKEN_USER`](https://docs.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-token_user?redirectedfrom=MSDN) 以及[ `TOKEN_OWNER` ](https://docs.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-token_owner?redirectedfrom=MSDN)结构。

`TOKEN_USER`结构标识与访问令牌相关的用户，`TOKEN_OWNER`标识利用该访问令牌创建的进程的所有者。这似乎是允许我们从某些`SYSTEM`进程中窃取访问令牌的主要不同点。

前面提到过，对于某些`SYSTEM`进程，`OpenProcess()`可以执行成功，但`OpenProcessToken()`会返回拒绝访问错误。现在我可以回答这个问题，这是因为我并不是这些进程的`TOKEN_OWNER`。

如下一行代码可以用来解析`Get-Token`的输出，寻找`UserName`为`SYSTEM`，但`OwnerName`不为`SYSTEM`的对象。然后抓取每个对象的`ProcessName`及`ProcessID`信息。

```
Get-Token | Where-Object `{`$_.UserName -eq ‘NT AUTHORITYSYSTEM’ -and $_.OwnerName -ne ‘NT AUTHORITY\SYSTEM’`}` | Select-Object ProcessName,ProcessID | Format-Table
```

[![](https://p1.ssl.qhimg.com/t01a11bd2dae43722eb.png)](https://p1.ssl.qhimg.com/t01a11bd2dae43722eb.png)

非常棒，我们应该能够从这些`SYSTEM`进程中窃取访问令牌，模拟`SYSTEM`访问令牌。接下来让我们验证一下这个猜想。

我手动遍历了这个PID列表，发现大多数进程的确能够用于控制访问令牌，然而还是存在一些例外进程。

[![](https://p4.ssl.qhimg.com/t011f3f32e0acfa98d2.png)](https://p4.ssl.qhimg.com/t011f3f32e0acfa98d2.png)

图. 对`wininit.exe`和`csrss.exe`执行`OpenProcess()`时会返回拒绝访问错误

**Protected Process Light**

前面提到过，某些`SYSTEM`进程在我调用`OpenProcess()`时，会返回拒绝访问错误，无法窃取令牌。我使用Process Explorer观察这些进程，发现了可能解释该行为的一个共同属性：`PsProtectedSignerWinTcb-Light`。

[![](https://p3.ssl.qhimg.com/t01ac2efaa6397daf09.png)](https://p3.ssl.qhimg.com/t01ac2efaa6397daf09.png)

仔细阅读[Alex Ionescu](https://twitter.com/aionescu?lang=en)发表的一篇[研究文章](http://www.alex-ionescu.com/?p=34)以及StackOverflow上的一篇[文章](https://stackoverflow.com/questions/40698608/openprocess-is-it-possible-to-get-error-access-denied-for-process-query-limited)，我了解到这个`Protected`属性与PPL（Protected Process Light）有关。

如果指定的访问权限为`PROCESS_QUERY_LIMITED_INFORMATION`，那么PPL只允许我们在该进程上调用`OpenProcess()`。我们的测试程序需要以`PROCESS_QUERY_INFORMATION`访问权限来调用`OpenProcess()`，以便返回的句柄能够与`OpenProcessToken()`配合使用，因此这样就会出现“System Error — Code 5”（拒绝访问）错误。

在测试检测机制时，我了解到`OpenProcessToken()`所需的最小访问权限为`PROCESS_QUERY_LIMITED_INFORMATION`，这与微软提供的[官方描述](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocesstoken)有所不同。我修改了调用`OpenProcess()`期间所需的访问权限，最终成功拿到了`SYSTEM`级别的命令提示符。

[![](https://p4.ssl.qhimg.com/t01b9c6037d63b8ed04.png)](https://p4.ssl.qhimg.com/t01b9c6037d63b8ed04.png)



## 0x05 测试结果

当我们使用`PROCESS_QUERY_INFORMATION`访问权限对某些`SYSTEM`进程调用`OpenProcess()`时，我们可以成功窃取这些进程的访问令牌。这些进程包括：

```
dllhost.exe
lsass.exe
OfficeClickToRun.exe
svchost.exe（只适用于某些PID）
Sysmon64.exe
unsecapp.exe
VGAuthService.exe
vmacthlp.exe
vmtoolsd.exe
winlogon.exe
```

对于受PPL保护的某些`SYSTEM`进程，如果我们以`PROCESS_QUERY_LIMITED_INFORMATION`访问权限调用`OpenProcess()`，还是能够窃取访问令牌，这些进程包括：

```
csrss.exe
Memory Compression.exe
services.exe
smss.exe
wininit.exe
```

其中有些进程可能与我的Windows开发环境有关，我建议大家在自己的环境中进行测试。



## 0x06 总结

稍微总结一下，我们可以从`winlogon.exe`中窃取访问令牌，模拟`SYSTEM`上下文。在本文中，我深入介绍了如何利用SACL以及Windows安全日志来检测对访问令牌的操作行为。

我也尝试寻找与`winlogon.exe`包含相似属性的其他`SYSTEM`进程，本文重点介绍了寻找这些进程的方法，最终找到了能够窃取访问令牌的其他`SYSTEM`进程。此外，我还深入研究了为什么某些进程能够用于操控访问令牌，而有些令牌无法完成该任务的具体原因。

为了从`SYSTEM`进程中窃取访问令牌，该进程必须满足如下条件：
- 如果想在某个进程上调用`OpenProcessToken()`，那么`BUILTIN\Administrator`必须为`TokenOwner`；
- 如果`SYSTEM`进程受PPL（Protected Process Light）保护，那么我们必须使用`PROCESS_QUERY_LIMITED_INFORMATION`访问权限来调用`OpenProcess()`。
希望大家能从本文中了解关于Windows API、SACL、Windows进程、Windows令牌以及控制访问令牌的一些知识
