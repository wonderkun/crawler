> 原文链接: https://www.anquanke.com//post/id/160948 


# 如何利用COM绕过AppLocker CLM


                                阅读量   
                                **136151**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：mdsec.co.uk
                                <br>原文地址：[https://www.mdsec.co.uk/2018/09/applocker-clm-bypass-via-com/](https://www.mdsec.co.uk/2018/09/applocker-clm-bypass-via-com/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t013c92bf726483ae3e.jpg)](https://p2.ssl.qhimg.com/t013c92bf726483ae3e.jpg)

## 一、前言

约束语言模式（Constrained Language Mode，CLM）是限制PowerShell的一种方法，可以限制PowerShell访问类似`Add-Type`之类的功能或者许多反射（reflective）方法（攻击者可以通过这些方法，在后续渗透工具中利用PowerShell运行时作为攻击媒介）。

结合微软的描述，这个功能通常可以作为一种安全控制方案，防御方能够利用该功能阻止运行类似`Invoke-Mimikatz`之类的工具，因为这些工具非常依赖于反射技术。

当我准备渗透部署了CLM的目标环境时，我需要快速了解有哪些潜在方法能够绕过这种保护措施。我搭建了一个Windows 10测试环境，通过默认设置的规则来部署CLM。在本文中，我会与大家分享我的研究结果，介绍如何以非管理员用户身份绕过这种保护机制。



## 二、进入正题

在测试环境中，我们要做的第一件事就是启用AppLocker。在本文中我们将使用Windows默认部署的规则来限制脚本执行。运行Application Identity服务后，我们可以使用如下命令确保本机已启用CLM：

```
$ExecutionContext.SessionState.LanguageMode
```

这里我们可以看到该命令的返回结果为`ConstrainedLanguage`，表明现在我们处于受限环境中。我们可以尝试使用PowerShell中的受限命令来验证这一点：

```
Add-Type "namespace test `{` `}`"
```

[![](https://p0.ssl.qhimg.com/t01ec23a104cc1c0329.png)](https://p0.ssl.qhimg.com/t01ec23a104cc1c0329.png)

系统的确启用了CLM，那么我们如何才能绕过这个障碍？



## 三、AppLocker CLM中的New-Object

令人惊讶的是，当我开始搜寻CLM存在的攻击面时，我发现当通过AppLocker启用CLM时，`New-Object`依然可用（尽管仍受到一些限制）。这似乎与预期的场景不一致，但我们的确可以使用如下命令来确认这一点：

```
New-Object -ComObject WScript.Shell
```

这给我留下了一种完美方式，可以从PowerShell内部来操控PowerShell进程，这是因为COM对象由DLL托管，而DLL会被加载到调用进程中。那么我们如何才能创建可以被加载的COM对象？如果我们使用ProcMon工具来观察`New-Object -ComObject xpntest`的调用过程时，我们可以看到该过程会多次请求`HKEY_CURRENT_USER`注册表项：

[![](https://p1.ssl.qhimg.com/t010394a8700d23804d.png)](https://p1.ssl.qhimg.com/t010394a8700d23804d.png)

仔细观察后，我们可以使用如下脚本来创建`HKCU`中所需的注册表键值：

[![](https://p1.ssl.qhimg.com/t012a6a51496f1505e0.png)](https://p1.ssl.qhimg.com/t012a6a51496f1505e0.png)

现在如果尝试加载我们的COM对象，可以看到我们的DLL已被加载到PowerShell进程空间中：

[![](https://p4.ssl.qhimg.com/t01cef48cb16ca234d9.png)](https://p4.ssl.qhimg.com/t01cef48cb16ca234d9.png)

[![](https://p4.ssl.qhimg.com/t01cf446f87d9733c0a.png)](https://p4.ssl.qhimg.com/t01cf446f87d9733c0a.png)

非常好，现在我们已经可以在受限的上下文环境中，将任意DLL载入PowerShell进程中，无需调用动作太大的`CreateRemoteThread`或者`WriteProcessMemory`。但我们的目标是绕过CLM，如何利用我们的非托管（unmanaged）DLL加载方式来完成这个任务？我们可以利用.NET CLR，或者更确切一点，我们可以通过非托管DLL加载.NET CLR来调用.NET assembly（程序集）。



## 四、从非托管DLL到托管DLL到反射

现在我们可以使用类似Cobalt Strike之类的工具，该工具提供了`Execute-Assembly`功能，可以将CLR加载到非托管进程中，操作起来非常方便。之前我在[GIST](https://gist.githubusercontent.com/xpn/e95a62c6afcf06ede52568fcd8187cc2/raw/f3498245c8309d44af38502a2cc7090c318e8adf/clr_via_native.c)上公开了一份代码，可以不依赖Cobalt Strike来完成这个任务：

[![](https://p3.ssl.qhimg.com/t01281f3763d4ef4967.png)](https://p3.ssl.qhimg.com/t01281f3763d4ef4967.png)

这里我不会讨论代码的详细内容（如果大家感兴趣可以去阅读微软的官方[示例](https://code.msdn.microsoft.com/windowsdesktop/CppHostCLR-e6581ee0)），该代码可以让DLL加载.NET CLR，然后加载.NET assembly，然后将执行权传递给特定的方法。

该过程完成后，我们就可以访问.NET，更重要的一点是，我们可以访问.NET的反射功能。接下来我们需要找到启用/关闭CLM的具体位置。

反汇编组成PowerShell的.NET assembly（即`System.Management.Automation.dll`）后，我们可以看到程序集的`System.Management.Automation.Runspaces.RunspaceBase.LanguageMode`属性中有一个地方可以标识当前的语言模式。由于我们要使用反射技术，因此需要找到引用`Runspace`的变量，在运行时修改该变量。我发现要完成该任务，最好的[办法](https://gist.githubusercontent.com/xpn/e95a62c6afcf06ede52568fcd8187cc2/raw/f3498245c8309d44af38502a2cc7090c318e8adf/clr_via_native.c)就是通过`Runspaces.Runspace.DefaultRunspace.SessionStateProxy.LanguageMode`，如下所示：

[![](https://p4.ssl.qhimg.com/t010bdb4a698585025f.png)](https://p4.ssl.qhimg.com/t010bdb4a698585025f.png)

将代码编译成.NET assembly，现在我们就可以通过反射方式禁用CLM，然后只需要创建一个[PowerShell脚本](https://gist.githubusercontent.com/xpn/1e9e879fab3e9ebfd236f5e4fdcfb7f1/raw/ceb39a9d5b0402f98e8d3d9723b0bd19a84ac23e/COM_to_registry.ps1)加以运行即可：

[![](https://p0.ssl.qhimg.com/t015f5b82b58947d4fd.png)](https://p0.ssl.qhimg.com/t015f5b82b58947d4fd.png)

这样就能大功告成，详细过程可参考[演示视频](https://youtu.be/ghi2M80fiMU)。



## 五、背后原理

那么为什么COM可以绕过这种保护机制，PowerShell如何处理COM加载过程？

我们可以在`SystemPolicy.IsClassInApprovedList`方法中找到答案，该方法用来检查是否允许我们向`New-Object`提供的CLSID。深入分析该方法，我们可以看到主要工作由如下关键代码负责：

```
if (SystemPolicy.WldpNativeMethods.WldpIsClassInApprovedList(ref clsid, ref wldp_HOST_INFORMATION, ref num, 0u) &gt;= 0 &amp;&amp; num == 1) `{` ... `}`
```

该调用只是`WldpIsClassInApprovedList`函数（位于`wldp.dll`中）的一个封装函数，而后者用来检查CLSID是否匹配DeviceGuard（现在为Windows Defender Application Control）策略。由于该方法没有考虑到AppLocker，这意味着通过检查的任何CLSID都可以畅行无阻。



## 六、奇怪的场景

结合前面分析，当我测试这种技术时，我陷入了一个奇怪的场景，当我们使用如下方法设置CLM时，这种技术将无法正常工作：

```
$ExecutionContext.SessionState.LanguageMode = "ConstrainedLanguage"
```

这让我有点困惑，因为之前我经常使用如上命令来测试载荷，此时我们面临的环境又有什么不同呢？回到我们的反汇编代码上，我们可以在`Microsoft.Powershell.Commands.Utility.dll`程序集中找到问题的答案，具体路径位于`NewObjectCommand`类的`BeginProcessing`方法中：

[![](https://p2.ssl.qhimg.com/t01b77beefb8822da1d.png)](https://p2.ssl.qhimg.com/t01b77beefb8822da1d.png)

这里我们可以看到代码中存在2条路径，具体取决于CLM的启用方式。如果`SystemPolicy.GetSystemLockdownPolicy`返回`Enfore`，那么就会执行第1条路径，此时AppLocker或者DeviceGuard处于启用状态（并非我们使用`ExecutionContext.SessionState.LanguageMode`的场景）。如果直接设置这个属性，我们会直接进入`if (!flag)…`代码段，此时就会抛出异常。从这里我们可以看到，CLM的行为实际上会根据具体的启用方法（是通过AppLocker、DeviceGuard启用还是通过`LanguageMode`属性来启用）而有所不同。

本文介绍的方法并不是绕过CLM的唯一方法，即使粗略分析PowerShell，我们也能找到实现类似效果的其他潜在方法。如果大家想了解其他技巧，可以参考Oddvar Moe在Debycon上的精彩[演讲](https://docs.google.com/spreadsheets/d/1XCKWHuXrVNcmmL1HsXklMT9ati8WSxGZkV_79Jh7gqA/edit#gid=1460396465)。
