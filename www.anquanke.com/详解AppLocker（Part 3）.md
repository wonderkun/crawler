> 原文链接: https://www.anquanke.com//post/id/193567 


# 详解AppLocker（Part 3）


                                阅读量   
                                **1076619**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者tyranidslair，文章来源：tyranidslair.blogspot.com
                                <br>原文地址：[https://tyranidslair.blogspot.com/2019/11/the-internals-of-applocker-part-3.html](https://tyranidslair.blogspot.com/2019/11/the-internals-of-applocker-part-3.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0118db7262dfabea7a.jpg)](https://p0.ssl.qhimg.com/t0118db7262dfabea7a.jpg)



## 0x00 前言

在上一篇[文章](https://tyranidslair.blogspot.com/2019/11/the-internals-of-applocker-part-2.html)中，我大概介绍了AL如何阻止进程创建操作，但没有解释AL如何处理相关规则，以确定特定用户是否可以创建进程。这方面内容其实非常重要，这里我们将按照与上一篇文章相反的顺序来介绍。我们先来研究下`SrppAccessCheck`如何实现访问检查机制。



## 0x01 访问检查及安全描述符

`SrppAccessCheck`函数实际上只是内核导出函数`SeSrpAccessCheck`的一个封装函数，尽管该API有一些比较特殊的功能，但这里我们还是可以将其当成普通的[SeAccessCheck](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-seaccesscheck) API来看待。

Windows的访问检查函数主要接受4个参数：
<li>
[SECURITY_SUBJECT_CONTEXT](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_security_subject_context)，用来标识调用方的访问令牌；</li>
- 所请求的访问权限位掩码；
<li>
[GENERIC_MAPPING](https://docs.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-generic_mapping)结构，允许函数将通用的访问权限转换为对象特定的访问权限；</li>
- 安全描述符，这个最重要，用来描述待检查资源的安全属性。
现在来看一下代码：

```
NTSTATUS SrpAccessCheckCommon(HANDLE TokenHandle, BYTE* Policy) `{`

    SECURITY_SUBJECT_CONTEXT Subject = `{``}`;
    ObReferenceObjectByHandle(TokenHandle, &amp;Subject.PrimaryToken);

    DWORD SecurityOffset = *((DWORD*)Policy+4)
    PSECURITY_DESCRIPTOR SD = Policy + SecurityOffset;

    NTSTATUS AccessStatus;
    if (!SeSrpAccessCheck(&amp;Subject, FILE_EXECUTE, 
                          &amp;FileGenericMapping, 
                          SD, &amp;AccessStatus) &amp;&amp;
        AccessStatus == STATUS_ACCESS_DENIED) `{`
        return STATUS_ACCESS_DISABLED_BY_POLICY_OTHER;
    `}`

    return AccessStatus;
`}`
```

代码不是特别复杂，首先利用以句柄参数传入的访问令牌构建一个`SECURITY_SUBJECT_CONTEXT`结构。代码使用传入的策略指针来查找检查时所需使用的安全描述符。最后，代码会调用`SeSrpAccessCheck`来请求文件的执行访问权。如果没通过检查，返回访问拒绝错误，那么代码就会转成AL特定的策略错误，否则就会返回其他成功或者错误结果。

这个过程中，我们并不清楚策略的值以及对应的安全描述符的值。我们可以跟踪代码流程，查找策略值的设置方式，但有时候我们可以直接通过内核调试器，在感兴趣的函数上设置断点，dump目标位置的内存数据。通过这种调试方法，我们可以看到如下信息：

[![](https://p3.ssl.qhimg.com/t01e39fcb7c1d1bb2f9.png)](https://p3.ssl.qhimg.com/t01e39fcb7c1d1bb2f9.png)

这里我们可以看到Part 1中曾出现过的前4个字符，这是磁盘上策略文件的特征字符串。`SeSrpAccessCheck`正在从offset 16处提取一个值，然后将该值作为同一个缓冲区的偏移量，用来获取安全描述符。那么是否策略文件中已经包含我们所需的安全描述符呢？快速开发一个PowerShell脚本，处理`Exe.AppLocker`策略文件后，我们能看到如下结果：

[![](https://p2.ssl.qhimg.com/t01359276095c5a8484.png)](https://p2.ssl.qhimg.com/t01359276095c5a8484.png)

非常棒，看来策略文件中的确包含安全描述符信息！如下脚本中包含2个函数：`Get-AppLockerSecurityDescriptor`以及`Format-AppLockerSecurityDescriptor`，这两个函数都以策略文件作为输入，返回安全描述符对象或者格式化后的结果：

```
Import-Module NtObjectManager

function Get-AppLockerSecurityDescriptor `{`
    Param(
        [Parameter(Mandatory, Position = 0)]
        [string]$Path
    )
    $Path = Resolve-Path $Path -ErrorAction Stop

    Use-NtObject($stm = [System.IO.File]::OpenRead($Path)) `{`
        $reader = New-Object System.IO.BinaryReader -ArgumentList $stm
        $magic = $reader.ReadInt32()      
        if ($magic -ne 0x46507041) `{`
            Write-Error "Invalid Magic Value"
            return
        `}`
        $reader.BaseStream.Position = 16
        $ofs = $reader.ReadInt32()
        $size = $reader.ReadInt32()
        $reader.BaseStream.Position = $ofs
        New-NtSecurityDescriptor -Bytes $reader.ReadBytes($size)
    `}`
`}`

function Format-AppLockerSecurityDescriptor `{`
    Param(
        [Parameter(Mandatory, Position = 0)]
        [string]$Path
    )

    $sd = Get-AppLockerSecurityDescriptor -Path $Path
    $type = Get-NtType File
    Format-NtSecurityDescriptor $sd $type
`}`
```

如果我们在`Exe.Applocker`文件上运行`Format-AppLockerSecurityDescriptor`，可以看到如下DACL结果（经过精简处理）：

```
- Type  : AllowedCallback
 - Name  : Everyone
 - Access: Execute|ReadAttributes|ReadControl|Synchronize
 - Condition: APPID://PATH Contains "%WINDIR%\*"

 - Type  : AllowedCallback
 - Name  : BUILTIN\Administrators
 - Access: Execute|ReadAttributes|ReadControl|Synchronize
 - Condition: APPID://PATH Contains "*"

 - Type  : AllowedCallback
 - Name  : Everyone
 - Access: Execute|ReadAttributes|ReadControl|Synchronize
 - Condition: APPID://PATH Contains "%PROGRAMFILES%\*"

 - Type  : Allowed
 - Name  : APPLICATION PACKAGE AUTHORITY\ALL APPLICATION PACKAGES
 - Access: Execute|ReadAttributes|ReadControl|Synchronize

 - Type  : Allowed
 - Name  : APPLICATION PACKAGE AUTHORITY\ALL RESTRICTED APPLICATION PACKAGES
 - Access: Execute|ReadAttributes|ReadControl|Synchronize
```

可以看到这里有两个ACE，一个适用于`Everyone`组，一个适用于`Administrators`组，这与我们在Part 1中的默认配置相符。最后两个ACE用来确保检测过程能在App Container中顺利完成。

这里最有趣的是`Condition`字段，这是内核在检查安全访问权限时很少使用的一个功能（至少在消费者版本系统中是如此），该功能允许通过条件表达式来判断ACE是否需要启用。在这种情况下，我们看到的是SDDL格式（可参考[此处文档](https://docs.microsoft.com/en-us/windows/win32/secauthz/security-descriptor-definition-language-for-conditional-aces-)），但实际上这是一种二进制结构。如果我们假设`*`的作用是充当通配符，那么这再次与我们的规则相匹配。前面我们设置的规则如下：
- 允许`Everyone`组运行`%WINDIR%`及`%PROGRAMFILES%`目录下的任何可执行文件；
- 允许`Administrators`组从任意位置运行可执行文件。
当我们配置某个规则时，我们指定了某个组，该组会作为SID添加到策略文件的安全描述符的ACE中。ACE类型设置为`Allow`或者`Deny`，然后AL会构造一个条件来应用该规则，具体规则与文件路径、文件哈希或者发布者有关。

接下来试着使用哈希及发布者信息来添加策略条目，看一下AL会如何设置对应的条件。我们可以从[此处](https://gist.github.com/tyranid/f5337c4f9a79f9d2afb52729e8e448fb)下载新的策略文件，然后在管理员PowerShell控制台中运行`Set-AppLockerPolicy`命令，然后重新运行`Format-ApplockerSecurityDescriptor`：

```
- Type  : AllowedCallback
 - Name  : Everyone
 - Access: Execute|ReadAttributes|ReadControl|Synchronize
 - Condition: (Exists APPID://SHA256HASH) &amp;&amp; (APPID://SHA256HASH Any_of `{`#5bf6ccc91dd715e18d6769af97dd3ad6a15d2b70326e834474d952753
118c670`}`)

 - Type  : AllowedCallback
 - Name  : Everyone
 - Access: Execute|ReadAttributes|ReadControl|Synchronize
 - Flags : None
 - Condition: (Exists APPID://FQBN) &amp;&amp; (APPID://FQBN &gt;= `{`"O=MICROSOFT CORPORATION, L=REDMOND, S=WASHINGTON, C=US\MICROSOFT® WINDOWS
® OPERATING SYSTEM\*", 0`}`)
```

现在我们可以看到新增了两个条件ACE，涉及到SHA256哈希以及发布者的名称。如果在策略中添加更多规则及条件，那么安全描述符中就会添加对应的ACE。需要注意的是，规则的顺序非常重要。比如，`Deny`型ACE优先级始终较高。我认为策略文件生成代码可以正确处理安全描述符的生成过程，但大家可以自己去验证一下。

现在我们已经了解了规则的处理方式，但还不知道具体条件对应的值（比如`APPID://PATH`）源自何处。如果我们查看官方提供的关于条件型ACE的（较不完善的）文档，就会发现这些值实际上为安全属性（Security Attribute）。这些属性可以全局定义，也可以分配到某个访问令牌。每个属性都有一个名称，以及带有一个或多个值的一个列表（这些值包括字符串、证书、二进制数据等）。AL可以通过这种方式在访问检查令牌中存放数据。

接下来让我们回头看看`AiSetAttributesExe`的工作机制，了解这些安全属性的生成方式。



## 0x02 设置令牌属性

`AiSetAttributesExe`函数接受4个参数：
- 可执行文件的一个句柄；
- 指向当前策略的一个指针；
- 新进程主令牌的一个句柄；
- 用于访问权限检查的令牌的一个句柄。
代码看上去不是特别复杂，如下所示：

```
NTSTATUS AiSetAttributesExe(
            PVOID Policy, 
            HANDLE FileHandle, 
            HANDLE ProcessToken, 
            HANDLE AccessCheckToken) `{`

    PSECURITY_ATTRIBUTES SecAttr;
    AiGetFileAttributes(Policy, FileHandle, &amp;SecAttr);
    NTSTATUS status = AiSetTokenAttributes(ProcessToken, SecAttr);
    if (NT_SUCCESS(status) &amp;&amp; ProcessToken != AccessCheckToken)
        status = AiSetTokenAttributes(AccessCheckToken, SecAttr);
    return status;
`}`
```

如上代码会调用`AiGetFileAttributes`来填充`SECURITY_ATTRIBUTES`结构，然后调用`AiSetTokenAttributes`，在`ProcessToken`以及`AccessCheckToken`上设置对应的属性（如果这两个令牌不一致的话）。`AiSetTokenAttributes`实际上是对已导出的（且未公开的）`SeSetSecurityAttributesToken`内核API的一个封装函数，以生成的安全属性列表为参数，然后将这些属性添加到访问令牌中，以便后续在访问权限检查中使用。

`AiGetFileAttributes`首先会查询文件句柄所对应的完整路径，然而这是本机路径，采用`\Device\Volume\Path\To\File`的格式。如果我们希望生成一个简单的策略，在整个公司中部署（比如通过组策略方式），那么采用这种格式的路径不能提供太多帮助。因此，代码会将路径转换为Win32样式的路径（如`c:\Path\To\File`）。但如果目标系统盘不使用`C:`盘符、U盘，或者当其他可移动驱动器上有可执行文件，盘符会发生变化，这种情况下该如何处理？

为了覆盖尽可能多的情况，系统还会维护一个固定的“宏”列表，类似于环境变量扩展。这些“宏”用来替代系统盘组件、为可移动设备设置占位符。之前我们已经在dump安全描述符时看到过一些字符串组件，比如`%WINDIR%`，大家可以访问[此处](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-application-control/applocker/understanding-the-path-rule-condition-in-applocker)了解这些宏，具体包括如下项目：
<li>
`%WINDIR%`：`Windows`目录；</li>
<li>
`%SYSTEM32%`：`System32`及`SysWOW64`目录（x64系统上）；</li>
<li>
`%PROGRAMFILES%`：`Program Files`及`Program Files (x86)`目录；</li>
<li>
`%OSDRIVE%`：系统所在驱动器；</li>
<li>
`%REMOVABLE%`：可移动驱动器，如CD或者DVD；</li>
<li>
`%HOT%`：热插拔设备，比如U盘。</li>
需要注意的是，在64位系统上运行时，`SYSTEM32`及`PROGRAMFILES`会映射到32位或64位目录（可能同样适用于ARM版Windows系统上的ARM相关目录）。如果我们想使用特定的目录，需要配置规则不使用这些宏。

为了应付各种情况，AL会在`APPID://PATH`安全属性中以字符串值形式来配置所有可能的路径，包括本地路径、Win32路径以及所有可能的宏路径。

随后，`AiGetFileAttributes`会收集文件的发布者信息。在Windows 10上，系统会通过各种方式检查签名及证书。首先系统会检查内核代码完整性（CI）模块，然后执行某些内部操作，最后调用RPC运行`APPIDSVC`。收集到的信息以及程序文件的版本信息会被存放到`APPID://FQBN`属性中（FQBN全称为Fully Qualified Binary Name）。

最后一步是生成文件哈希，哈希存放在一个二进制属性中。AL支持三种类型的哈希算法，对应的属性名如下：
<li>
`PPID://SHA256HASH`：Authenticode SHA256</li>
<li>
`APPID://SHA1HASH`：Authenticode SHA1</li>
<li>
`APPID://SHA256FLATHASH`：整个文件的SHA256</li>
由于这些属性会应用到这两个令牌上，因此我们应当能在普通用户进程的主令牌上看到这些属性。运行如下PowerShell命令后，我们可以看到当前进程令牌中已经添加的安全属性：

```
PS&gt; $(Get-NtToken).SecurityAttributes | ? Name -Match APPID

Name       : APPID://PATH
ValueType  : String
Flags      : NonInheritable, CaseSensitive
Values     : `{`
   %SYSTEM32%\WINDOWSPOWERSHELL\V1.0\POWERSHELL.EXE,
   %WINDIR%\SYSTEM32\WINDOWSPOWERSHELL\V1.0\POWERSHELL.EXE,  
    ...`}`

Name       : APPID://SHA256HASH
ValueType  : OctetString
Flags      : NonInheritable
Values     : `{`133 66 87 106 ... 85 24 67`}`

Name       : APPID://FQBN
ValueType  : Fqbn
Flags      : NonInheritable, CaseSensitive
Values     : `{`Version 10.0.18362.1 - O=MICROSOFT CORPORATION, ... `}`
```

需要注意的是，AL始终会添加`APPID://PATH`属性，然而只有当存在对应的规则时，AL才会生成并添加`APPID://FQBN`及`APPID://*HASH`属性。



## 0x03 双令牌之谜

现在我们已经知道AL如何生成安全属性以及将这些属性应用到两个访问令牌中，现在的问题是，这里为什么会涉及到两个令牌：一个进程令牌和一个仅用于访问权限检查的令牌？

答案都在`AiGetTokens`中，简化版的代码如下所示：

```
NTSTATUS AiGetTokens(HANDLE ProcessId, 

                     PHANDLE ProcessToken,

                     PHANDLE AccessCheckToken)

`{`

  AiOpenTokenByProcessId(ProcessId, &amp;TokenHandle);

  NTSTATUS status = STATUS_SUCCESS;
   *Token = TokenHandle;
   if (!AccessCheckToken)
    return STATUS_SUCCESS;

  BOOL IsRestricted;
  status = ZwQueryInformationToken(TokenHandle, TokenIsRestricted, &amp;IsRestricted);
  DWORD ElevationType;
  status = ZwQueryInformationToken(TokenHandle, TokenElevationType, 
                          &amp;ElevationType);

  HANDLE NewToken = NULL;
  if (ElevationType != TokenElevationTypeFull)
      status = ZwQueryInformationToken(TokenHandle, TokenLinkedToken, 
                                       &amp;NewToken);

  if (!IsRestricted
    || NT_SUCCESS(status)
    || (status = SeGetLogonSessionToken(TokenHandle, 0, 
                 &amp;NewToken), NT_SUCCESS(status))
    || status == STATUS_NO_TOKEN) `{`
    if (NewToken)
      *AccessCheckToken = NewToken;
    else
      *AccessCheckToken = TokenHandle;
  `}`

  return status;
`}`
```

稍微梳理一下上述代码。首先，`ProcessToken`句柄是代码根据进程PID打开的进程令牌。如果没有指定`AccessCheckToken`，那么代码将结束运行。否则，代码会将`AccessCheckToken`设置为如下3个值之一：

1、如果令牌为未提升（UAC）令牌，那么就使用完整的提升令牌；

2、如果令牌处于“受限模式”且不是UAC令牌，那么就会使用登录会话令牌；

3、否则，就使用新进程的主令牌。

现在我们可以理解为什么AL会将管理员规则应用于未提升UAC的管理员。如果我们以未提升用户令牌运行，那么就满足第一种情况，AL会将`AccessCheckToken`设置为完整管理员令牌，因此可以通过适用于`Administrators`组的检查规则。

第二种情况同样比较有趣，这里的“受限”令牌指的是通过[CreateRestrictedToken](https://docs.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-createrestrictedtoken) API获得的令牌，且令牌中附加了受限的SID，许多沙箱（比如Chromium沙箱以及Firefox）会使用这种令牌。在这种情况下，如果进程令牌为受限令牌，并且没有通过访问权限检查（比如规则禁用了`Everyone`组），那么AL就会使用登录会话的令牌来执行访问权限检查，其他令牌都派生自登录会话。

如果不满足这两种情况，那么就会将主令牌赋值给`AccessCheckToken`。这几条规则中存在一些边缘情况，比如我们可以使用`CreateRestrictedToken`来创建新的、带有被禁用组的访问令牌，但该令牌同时不包含受限SID。此时AL不会应用第二种情况，会针对受限令牌执行访问权限检查，这种情况下很容易无法通过检查，导致进程被结束。

如果查看代码，我们还能发现有个更微妙的边缘情况。如果我们创建UAC管理员令牌的一个受限令牌，那么进程创建操作通常不会通过策略检查。当UAC令牌为完整管理员令牌时，代码不会再次调用`ZwQueryInformationToken`，此时`NewToken`的值为`NULL`。然而在后面的检查逻辑中，`IsRestricted`的值为`TRUE`，因此代码会检查第二个条件。由于`status`的值为`STATUS_SUCCESS`（第一次调用`ZwQueryInformationToken`返回的结果），因此可以通过第二个条件，在不调用`SeGetLogonSessionToken`的情况下进入`if`中的代码段。此时由于`NewToken`仍然为`NULL`，因此`AccessCheckToken`会被设置为主进程令牌，而该令牌为受限令牌，会导致后续检查失败。这实际上是Chromium中长期存在的一个[bug](https://bugs.chromium.org/p/chromium/issues/detail?id=740132)，如果系统中设置了AppLocker，那么我们就不能以UAC管理员运行Chromium。

以上就是AL对已设置条件的处理流程，后面我们会继续深入研究DLL条件的工作原理。



## 0x04 限制特定进程访问特定资源

在继续下文分析前，这里我还想提一个小问题，比如我们是否可以将资源（比如文件）的访问权限制在特定进程中？在AL以及安全属性的帮助下，我们可以完成该任务。我们只需要将同样的条件ACE语法应用于目标文件中，内核就可以帮我们应用这种限制策略。比如，我们可以创建`C:\TEMP\ABC.TXT`，然后通过如下PowerShell命令，只允许notepad打开该文件：

```
Set-NtSecurityDescriptor \??\C:\TEMP\ABC.TXT `
     -SecurityDescriptor 'D:(XA;;GA;;;WD;(APPID://PATH Contains "%SYSTEM32%\NOTEPAD.EXE"))' `
     -SecurityInformation Dacl
```

这里要确保路径全部使用大写字母，运行命令后，我们会发现PowerShell（以及其他应用）都无法打开这个文本文件，但notepad可以畅行无阻。当然这种限制不能跨越网络边界，很容易被绕过，但这就不是我考虑的范围了 🙂
