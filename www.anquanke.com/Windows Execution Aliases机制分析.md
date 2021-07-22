> 原文链接: https://www.anquanke.com//post/id/186708 


# Windows Execution Aliases机制分析


                                阅读量   
                                **434546**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者tyranidslair，文章来源：tyranidslair.blogspot.com
                                <br>原文地址：[https://tyranidslair.blogspot.com/2019/09/overview-of-windows-execution-aliases.html](https://tyranidslair.blogspot.com/2019/09/overview-of-windows-execution-aliases.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0104698f3b2b755b61.jpg)](https://p3.ssl.qhimg.com/t0104698f3b2b755b61.jpg)



## 0x00 前言

[Bruce Dawson](https://twitter.com/BruceDawson0xB)最近发过一则[推文](https://twitter.com/tiraniddo/status/1171369360763609088)，表示微软在一些Windows 10 1903系统上安装了某种“虚假的”Python副本，本文对这方面内容做了一些研究。根据我的观察，被安装的Python可执行文件大小为`0`字节，本文分析了这种情况的背后原理，介绍了如何利用这种方式启动进程，最后介绍了系统中仍然存在的一个TOCTOU问题，攻击者可能在EOP（权限提升）过程中利用到该缺陷。



## 0x01 Execution Aliases机制解析

微软在Windows 10 Fall Creators Update（1709/RS3）中引入了针对UWP应用的[Execution Aliases](https://blogs.windows.com/windowsdeveloper/2017/07/05/command-line-activation-universal-windows-apps/#QBVyMPUOpI9SMbFI.97)（执行别名）机制。应用开发者可以在程序的manifest信息中添加[AppExecutionAlias](https://docs.microsoft.com/en-us/uwp/schemas/appxpackage/uapmanifestschema/element-uap5-appexecutionalias) XML元素来对外提供这个功能，AppX安装程序会根据这个manifest信息将别名释放到`%LOCALAPPDATA%\Microsoft\WindowsApps`目录中，而该目录通常会添加到用户的`PATH`环境变量中。因此，我们可以像运行命令行应用一样来启动UWP应用，并且可以传递命令行参数。这里我们以WinDbgX的manifest信息为例：

```
&lt;uap3:Extension Category="windows.appExecutionAlias" 
                Executable="DbgX.Shell.exe" 
                EntryPoint="Windows.FullTrustApplication"&gt;
  &lt;uap3:AppExecutionAlias&gt;
    &lt;desktop:ExecutionAlias Alias="WinDbgX.exe" /&gt;
  &lt;/uap3:AppExecutionAlias&gt;
&lt;/uap3:Extension&gt;
```

其中指定了一个Execution Aliases，以便通过`WinDbgX.exe`来运行`DbgX.Shell.exe`。如果我们转到`WindowsApps`目录，可以看到有个`WinDbgX.exe`文件，并且与推文中提到的情况一致，这个文件大小为`0`字节。如果我们尝试打开该文件（比如使用`type`）命令，就会看到错误信息。

[![](https://p3.ssl.qhimg.com/t01fd96d4c981b8b398.png)](https://p3.ssl.qhimg.com/t01fd96d4c981b8b398.png)

那么为什么一个空文件可以实现进程创建效果呢？如果我们在shell中执行`WinDbgX.exe`，就可以在Process Monitor中看到一些有趣的信息，如下图高亮框所示：

[![](https://p1.ssl.qhimg.com/t01f08833cdd7ec72ba.png)](https://p1.ssl.qhimg.com/t01f08833cdd7ec72ba.png)

首先可以注意到有一个`CreateFile`调用，该调用返回一个`REPARSE`结果。这是一个很好的线索，表明该文件包含一个reparse point（重解析点）。大家可能会猜测这个文件是指向真实目标的一个符号链接，然而即便是符号链接，我们也能正常打开，但这种情况下打开时却会出错。还有另一种解释，这个重解析点采用自定义类型，无法被内核所解析。随后程序会使用`FSCTL_GET_REPARSE_POINT`代码来调用`FileSystemControl`，这表明某些用户模式代码正在请求关于该解析点的相关信息。观察调用栈，我们可以看到哪个模块在请求重解析点数据，如下图所示：

[![](https://p3.ssl.qhimg.com/t01d64d7c1a8d96b445.png)](https://p3.ssl.qhimg.com/t01d64d7c1a8d96b445.png)

在调用栈中，我们可以看到`CreateProcess`会通过`LoadAppExecutionAliasInfoEx`导出函数来查询重解析点，我们可以深入`CreateProcessInternal`来分析内部原理：

```
HANDLE token = ...;
NTSTATUS status = NtCreateUserProcess(ApplicationName, 
                                      ..., token);

if (status == STATUS_IO_REPARSE_TAG_NOT_HANDLED) `{`
  LPWSTR alias_path = ResolveAlias(ApplicationName);
  PEXEC_ALIAS_DATA alias;
  LoadAppExecutionAliasInfoEx(alias_path, &amp;alias);

  status = NtCreateUserProcess(alias.ApplicationName, 
                               ..., alias.Token);
`}`
```

`CreateProcessInternal`首先会尝试直接执行该路径，然而由于该文件使用未知的重解析点，因此内核无法打开该文件，返回`STATUS_IO_REPARSE_TAG_NOT_HANDLED`。根据这个状态码，`CreateProcessInternal`会选择另一个分支，使用`LoadAppExecutionAliasInfoEx`从文件的重解析标签中加载别名信息，然后根据新的应用程序路径以及访问令牌来启动新的进程。

那么这个重解析点数据的格式是什么？我们可以dump相关数据，使用十六进制编辑器来查看：

[![](https://p3.ssl.qhimg.com/t01ec35154604e40d6f.png)](https://p3.ssl.qhimg.com/t01ec35154604e40d6f.png)

前4个字节为重解析标签，这里为`0x8000001B`，根据Windows SDK文档，这个值代表`IO_REPARSE_TAG_APPEXECLINK`。不幸的是，我们并没有找到对应的结构，但经过一些逆向分析工作后，我们可以梳理出如下格式：

```
Version: &lt;4字节整数&gt;
Package ID: &lt;以NUL结尾的Unicode字符串&gt;
Entry Point: &lt;以NUL结尾的Unicode字符串&gt;
Executable: &lt;以NUL结尾的Unicode字符串&gt;
Application Type: &lt;以NUL结尾的Unicode字符串&gt;

```

我们之所以没找到对应的结构，可能是因为这种数据采用了序列化格式。`Version`字段目前的值为`3`，我不确定在之前的Windows 10中是否存在其他版本值，但我的确没有找到其他值。`Package ID`以及`Entry Point`是用来标识包的特征信息，Execution Aliases无法以正常应用的快捷方式来使用，只能解析成系统上已安装的应用程序包（packaged application）。`Executable`是被实际执行的文件（而不是前面我们看到的大小为`0`字节的别名文件），`Application Type`是正在创建的应用程序类型，这个字符串实际上是由整数格式化成的一个字符串。整数值为`0`代表Desktop Bridge应用，非零值则代表正常的沙箱化UWP应用。我在`NtApiDotNet`中实现了重解析数据的一个解析程序，大家可以在`NtObjectManager`中使用`Get-ExecutionAlias` cmdlet来解析这类重解析点。

[![](https://p3.ssl.qhimg.com/t0117b64daa9c28c1a7.png)](https://p3.ssl.qhimg.com/t0117b64daa9c28c1a7.png)

现在我们已经知道新进程创建过程中如何指定`Executable`文件，但对应的访问令牌呢？实际上我曾在Zer0Con 2018会议上发表过关于[Desktop Bridge](https://github.com/tyranid/Zer0Con_2018/blob/master/A%20Bridge%20too%20Far.pdf)的一次演讲，其中就提到了访问令牌。（UAC相关的）`AppInfo`服务中有一个RPC服务，可以通过Execution Aliases文件来创建访问令牌，整个处理过程位于`LoadAppExecutionAliasInfoEx`中，主要流程如下图所示：

[![](https://p2.ssl.qhimg.com/t01b58b29000f43c470.png)](https://p2.ssl.qhimg.com/t01b58b29000f43c470.png)

`RAiGetPackageActivationToken` RPC函数的参数为Execution Aliases文件的具体路径以及一个模板令牌（通常为当前进程令牌，如果`CreateProcessAsUser`被调用则为显式令牌）。`AppInfo`服务会从Execution Aliases中读取重解析信息，基于该信息构造一个激活令牌。该令牌随后会被返回给调用方，用来创建新进程。这里需要注意的是，如果`Application Type`为非零值，那么这个过程实际上并不会创建`AppContainer`令牌来运行UWP应用。这是因为在`CreateProcess`中激活UWP应用要复杂得多，因此Execution Aliases的可执行文件会被指定为`system32`中的`SystemUWPLauncher.exe`文件，后者会根据令牌中的包信息来完成激活过程。

那么激活令牌中包含哪些信息？这里主要是应用包对应的`Security Attribute`（安全属性）信息，用户模式的应用程序通常无法修改该信息，需要TCB权限。因此微软选择在系统服务中设置令牌。与`WinDbgX`别名对应的示例令牌如下图所示：

[![](https://p1.ssl.qhimg.com/t0198da5e0ef94a7de0.png)](https://p1.ssl.qhimg.com/t0198da5e0ef94a7de0.png)

对我们来说，后续的激活过程实际上并不重要。如果大家想了解更多细节，可以参考之前我关于[Desktop Bridge](https://github.com/tyranid/Zer0Con_2018)以及[Windows Runtime](https://github.com/tyranid/WindowsRuntimeSecurityDemos)的演讲。



## 0x02 TOCTOU

接下来分析下如何实现TOCTOU（time-of-check-to-time-of-use）攻击效果。从理论上讲，我们可以为已安装的任何应用程序包创建Execution Aliases，但如果我们无法使用`RAiGetPackageActivationToken`来获得带有显式安全属性的新令牌，那么就无法启动所需的进程，也就无法进一步利用。比如，我们可以尝试使用如下PowerShell脚本，为Calculator应用包创建一个Execution Aliases（注意这里使用了1903 x64系统上的版本信息）：

```
Set-ExecutionAlias -Path C:\winapps\calc.exe `
     -PackageName "Microsoft.WindowsCalculator_8wekyb3d8bbwe" `
     -EntryPoint "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App" `
     -Target "C:\Program Files\WindowsApps\Microsoft.WindowsCalculator_10.1906.53.0_x64__8wekyb3d8bbwe\Calculator.exe" `
     -AppType UWP1
```

如果我们调用`RAiGetPackageActivationToken`，那么就能成功创建一个新的令牌，然而这里创建的是一个简化权限的UWP令牌（并不是`AppContainer`令牌，但所有权限都被剥除，`Security Attribute`认为该应用位于沙箱中）。如果我们想创建Desktop Bridge令牌，不受这个限制，那么该如何操作呢？我们可以试着将`AppType`改成`Desktop`，然而此时我们发现调用`RAiGetPackageActivationToken`时会返回拒绝访问错误。深入分析后，我们发现系统在调用`daxexec!PrepareDesktopAppXActivation`时会返回失败，其中会检查程序包中是否包含Centennial （现在称为Desktop Bridge）应用。

```
HRESULT PrepareDesktopAppXActivation(PACTIVATION_INFO activation_info) `{`
  if ((activation_info-&gt;Flags &amp; 1) == 0) `{`
    CreatePackageInformation(activation_info, &amp;package_info);

    if (FAILED(package_info-&gt;ContainsCentennialApplications())) `{`
      return E_ACCESS_DENIED; // &lt;-- Fails here.
    `}`
  `}`

  // ...
`}`
```

这一点非常正常，系统没必要为不包含桌面应用的程序包创建桌面激活令牌。然而我们要注意上述代码中的`1`这个比特位，如果没有设置这个标志位，那么系统就会执行检查操作，反之则直接绕过检查过程。那么这个标志位来自于哪里？我们需要回溯到`PrepareDesktopAppXActivation`函数的调用方，也就是`RAiGetPackageActivationToken`。

```
ACTIVATION_INFO activation_info = `{``}`;
bool trust_label_present = false;
HRESULT hr = IsTrustLabelPresentOnReparsePoint(path, 
                                      &amp;trust_label_present);
if (SUCCEEDED(hr) &amp;&amp; trust_label_present) `{`
  activation_info.Flags |= 1;
`}`

PrepareDesktopAppXActivation(&amp;activation_info);
```

根据这段代码，我们发现该标志位的值取决于`IsTrustLabelPresentOnReparsePoint`的结果值。虽然我们可以推测处该函数的内部逻辑，但还是可以来做一些逆向分析：

```
HRESULT IsTrustLabelPresentOnReparsePoint(LPWSTR path, 
                                          bool *trust_label_present) `{`
  HANDLE file = CreateFile(path, READ_CONTROL, ...);
  if (file == INVALID_HANDLE_VALUE)
    return E_FAIL;

  PSID trust_sid;
  GetWindowsPplTrustLabelSid(&amp;trust_sid);

  PSID sacl_trust_sid;
  GetSecurityInfo(file, 
                  SE_FILE_OBJECT, 
                  PROCESS_TRUST_LABEL_SECURITY_INFORMATION, 
                  &amp;sacl_trust_sid);
  *trust_label_present = EqualSid(trust_sid, sacl_trust_sid);
  return S_OK;
`}`
```

这段代码的主要操作就是查询文件对象所对应的Process Trust Label。只有Protected Process才能设置这个标签，但通常情况我们并不是这种进程。我们有各种方法能够注入这类进程，除此之外我们无法设置信任标签。如果没有信任标签，系统就会执行额外的检查操作，阻止我们为Calculator程序包创建桌面激活令牌。

然而这里我们要注意到系统会再次打开这个文件，当系统完成重解析点读取后会再次执行打开操作。因此这里会有个TOCTOU问题，如果我们能让服务在第一次读取时，读取带有包信息的Execution Aliases，然后将该文件切换到带有有效信任标签的另一个文件，那么就能禁用系统附加的检查操作。这也是我开发的[BaitAndSwitch](https://github.com/googleprojectzero/symboliclink-testing-tools/tree/master/BaitAndSwitch)工具的攻击场景。如果大家使用这款工具，运行如下命令，那么就能使用`c:\x\x.exe`路径来调用`RAiGetPackageActivationToken`，成功绕过检查机制：

```
BaitAndSwitch c:\x\x.exe c:\path\to\no_label_alias.exe c:\path\to\valid_label_alias.exe x
```

注意到上述命令的最后一个`x`，这并不是拼写错误，只是为了能以独占模式打开oplock，确保系统在第一次打开文件读取包信息时会触发oplock。实现这种效果后我们还能进一步利用吗？可能效果没那么好，但我觉得这个研究过程比较有意思。如果通过这种方式能禁用掉其他更为重要的安全机制那就更好，但貌似我们只能通过这种方式创建一个桌面激活令牌而已。
