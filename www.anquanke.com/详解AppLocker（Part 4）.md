> 原文链接: https://www.anquanke.com//post/id/193664 


# 详解AppLocker（Part 4）


                                阅读量   
                                **1130175**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者tyranidslair，文章来源：tyranidslair.blogspot.com
                                <br>原文地址：[https://tyranidslair.blogspot.com/2019/11/the-internals-of-applocker-part-4.html](https://tyranidslair.blogspot.com/2019/11/the-internals-of-applocker-part-4.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0118db7262dfabea7a.jpg)](https://p0.ssl.qhimg.com/t0118db7262dfabea7a.jpg)



## 0x00 前言

前几篇文章中，我介绍了AppLocker（AL）如何阻止进程创建操作的一些基本知识，在本文中，我将分析AL如何阻止DLL加载。如果我们深入研究过Windows的组策略编辑器，在为AL启用DLL规则时，就可以看到如下警告信息：

[![](https://p2.ssl.qhimg.com/t0108bcee455b4e70f6.png)](https://p2.ssl.qhimg.com/t0108bcee455b4e70f6.png)

似乎微软并不推荐启用DLL阻止规则，但由于我已知找不到阻止DLL加载的官方文档，并且我们也要避免“知其然，不知其所以然”的问题，因此我们还是应当深入研究一下。



## 0x01 技术分析

根据[Part 1](https://tyranidslair.blogspot.com/2019/11/the-internals-of-applocker-part-1.html)我们可知，`DLL.Applocker`文件中包含适用于DLL的策略。我们可以按照[Part 3](https://tyranidslair.blogspot.com/2019/11/the-internals-of-applocker-part-3.html)的方式，使用`Format-AppLockerSecurityDescriptor`函数从文件中dump出安全描述符，验证其是否符合我们的预期。对应的DACL如下所示：

```
- Type  : AllowedCallback
 - Name  : Everyone
 - Access: Execute|ReadAttributes|ReadControl|Synchronize
 - Condition: APPID://PATH Contains "%WINDIR%\*"

 - Type  : AllowedCallback
 - Name  : Everyone
 - Access: Execute|ReadAttributes|ReadControl|Synchronize
 - Condition: APPID://PATH Contains "%PROGRAMFILES%\*"

 - Type  : AllowedCallback
 - Name  : BUILTIN\Administrators
 - Access: Execute|ReadAttributes|ReadControl|Synchronize
 - Condition: APPID://PATH Contains "*"

 - Type  : Allowed
 - Name  : APPLICATION PACKAGE AUTHORITY\ALL APPLICATION PACKAGES
 - Access: Execute|ReadAttributes|ReadControl|Synchronize

 - Type  : Allowed
 - Name  : APPLICATION PACKAGE AUTHORITY\ALL RESTRICTED APPLICATION PACKAGES
 - Access: Execute|ReadAttributes|ReadControl|Synchronize
```

这里一切正常，可以在安全描述符中看到我们的规则。然而从结果中我们可以猜测，内核驱动可能会负责某些工作。如果查看`APPID`中的函数，可以找到一个`SrpVerifyDll`函数，我们可以以此为切入点开展研究。

通过跟踪函数引用信息，我们可以发现某个Device IO Control代码会调用`SrpVerifyDll`来处理`APPID`驱动对外提供的一个设备对象（`\Device\SrpDevice`）。经过一番逆向分析后，我们可以找到控制代码及对应的输入/输出结构，如下所示：

```
// 0x225804
#define IOCTL_SRP_VERIFY_DLL CTL_CODE(FILE_DEVICE_UNKNOWN, 1537, \
            METHOD_BUFFERED, FILE_READ_DATA)

struct SRP_VERIFY_DLL_INPUT `{`
    ULONGLONG FileHandle;
    USHORT FileNameLength;
    WCHAR FileName[ANYSIZE_ARRAY];
`}`;

struct SRP_VERIFY_DLL_OUTPUT `{`
    NTSTATUS VerifyStatus;
`}`;
```

`SrpVerifyDll`函数本身并没有太多需要注意的地方，基本逻辑与Part 2与Part 3介绍的AL对进程创建的验证逻辑类似：

1、获取并复制访问检查令牌。如果令牌为受限令牌，则查询登录会话令牌；

2、检查令牌是否能通过检查策略，查看令牌中是否包含`SANDBOX_INERT`，或者对应某个服务；

3、调用`AiGetFileAttributes`函数，处理传入的文件句柄，获取安全属性；

4、使用`AiSetTokenAttributes`在令牌上设置安全属性；

5、使用策略安全描述符以及返回给Device IO Control输出的状态结果来执行访问权限检查。

之所以需要重新创建安全属性，是因为访问检查过程中AL需要了解正在加载的DLL（而不是原始的可执行文件）的相关信息。虽然文件名作为输入结构参数传入，但目前我发现文件名仅用于日志记录。

与Part 3中分析的过程相比，这里步骤1中有比较大的一个不同点。在Part 3介绍的阻止进程创建过程中，如果当前令牌为未提升的UAC令牌，那么代码就会查询完整的令牌，然后使用该令牌来检查访问权限。这意味着即使我们以非提升用户权限来创建进程，访问权限检查过程中AL仍会把我们看成管理员来处理。然而在DLL阻止过程中并没有包含这个步骤，因此这里可能存在一种奇怪的情况：我们可以在任意位置创建进程，但没办法在同一个目录中加载任何DLL。我不知道这是微软故意为之还是没有考虑到的一种情况。

那么谁调用Device IO Control来验证DLL？为了节省时间，我使用内核调试器在`SrpVerifyDll`上设置断点，然后dump栈布局，寻找调用方：

```
Breakpoint 1 hit
appid!SrpVerifyDll:
fffff803`38cff100 48895c2410      mov     qword ptr [rsp+10h],rbx
0: kd&gt; kc
 # Call Site
00 appid!SrpVerifyDll
01 appid!AipDeviceIoControlDispatch
02 nt!IofCallDriver
03 nt!IopSynchronousServiceTail
04 nt!IopXxxControlFile
05 nt!NtDeviceIoControlFile
06 nt!KiSystemServiceCopyEnd
07 ntdll!NtDeviceIoControlFile
08 ADVAPI32!SaferpIsDllAllowed
09 ADVAPI32!SaferiIsDllAllowed
0a ntdll!LdrpMapDllNtFileName
0b ntdll!LdrpMapDllFullPath
0c ntdll!LdrpProcessWork
0d ntdll!LdrpLoadDllInternal
0e ntdll!LdrpLoadDll
```

非常简单，看来`SaferiIsDllAllowed`是调用方，而该函数由`LdrLoadDll`调用。这一点非常正常，然而有趣的是`NTDLL`正在调用`ADVAPI32`中的函数，微软难道没考虑到分层隔离机制吗？让我们看一下`LdrpMapDllNtFileName`函数，这是系统转到`ADVAPI32`前使用的最后一个`NTDLL`函数。调用`SaferiIsDllAllowed`的代码如下所示：

```
NTSTATUS status;

if ((LoadInfo-&gt;LoadFlags &amp; 0x100) == 0 
        &amp;&amp; LdrpAdvapi32DllHandle) `{`
  status = LdrpSaferIsDllAllowedRoutine(
        LoadInfo-&gt;FileHandle, LoadInfo-&gt;FileName);
`}`
```

对`SaferiIsDllAllowed`的调用实际上用到了某个全局函数指针，这是因为`NTDLL`无法直接链接到`ADVAPI32`。负责初始化这些值的函数为`LdrpCodeAuthzInitialize`，任何非系统代码在新进程中运行之前，系统会调用这个初始化函数。函数首先会检查某些注册表键值（最重要的是`\Registry\Machine\System\CurrentControlSet\Control\Srp\GP\DLL`），判断是否存在任何子项。如果满足条件，代码就会使用`LdrLoadDll`加载`ADVAPI32`库，查询`SaferiIsDllAllowed`导出函数。代码会将DLL句柄存放在`LdrpAdvapi32DllHandle`中，将函数指针经过“异或”加密处理后，存放在`LdrpSaferIsDllAllowedRoutine`中。

调用`SaferiIsDllAllowed`后，AL会检查返回状态。如果状态码不等于`STATUS_SUCCESS`，那么加载程序将退出，拒绝继续加载DLL。需要再次强调的是，这个处理过程与WDAC有所不同。WDAC会在内核映像映射过程中检查操作安全性，如果已启用WDAC且不符合已设置的策略时，我们甚至无法成功创建映射映像区块（image section）。然而对于AL，如果想加载DLL，我们只需要在用户模式组件中绕过检查机制即可。

回头看`LdrpMapDllNtFileName`中的调用代码，可以发现其中存在两个条件：`LoadFlags`必须未设置`0x100`标志且`LdrpAdvapi32DllHandle`必须不为`0`，在执行检查操作之前必须满足这两个条件。

这里最明显可以被修改的是`LdrpAdvapi32DllHandle`。如果我们已经运行了某些代码（比如VBA代码），那么可以使用`WriteProcessMemory`，将`LdrpAdvapi32DllHandle`对应的内存位置修改为`0`。这样处理后，对`LoadLibrary`的任何调用都不会被检查，我们可以绕过策略来加载任意DLL。从理论上讲，我们可能还可以让`ADVAPI32`加载失败，然而除非`LdrLoadDll`在DLL加载过程中返回`STATUS_NOT_FOUND`，这种错误才能让进程在初始化阶段加载失败。由于`ADVAPI32`属于KnownDLLs（系统已知的一些DLL），因此我找不到特别简单的解决办法（我已经尝试过之前在AMSI绕过技术中使用过[技巧](https://tyranidslair.blogspot.com/2018/06/disabling-amsi-in-jscript-with-one.html)）。

另一个条件（`LoadFlags`）则更为有趣。在官方文档中提到过一个标志：`LOAD_IGNORE_CODE_AUTHZ_LEVEL`，我们可以将该标志传入`LoadLibraryEx`来绕过AppLocker的DLL验证过程。然而与`SANDBOX_INERT`类似，打上KB2532445补丁后，从理论上讲这种操作只适用于`System`或者`TrustedInstaller`（然而根据[Stefan Kanthak](https://seclists.org/fulldisclosure/2017/Mar/69)的研究，这种行为可能还不会被阻止）。也就是说，在Windows 10 1909上，我无法使用该标志来执行各种操作，并且跟踪`LdrLoadDll`的处理流程后，我也找不到该标志被使用的痕迹。那么`0x100`标志源自何处？似乎`LdrLoadDll`会在刚开始时调用`LDrpDllCharacteristicsToLoadFlags`函数来设置该标志，代码如下所示：

```
int LdrpDllCharacteristicsToLoadFlags(int DllCharacteristics) `{`
  int load_flags = 0;
  // ...
  if (DllCharacteristics &amp; 0x1000)
    load_flags |= 0x100;

  return load_flags;
`}`
```

如果我们将`0x1000`以`DllCharacteristics`参数形式传入（这也是`LdrLoadDll`的第二个参数），那么AL就不会验证DLL是否匹配策略。根据[官方文档](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format#dll-characteristics)，`0x1000`这个值对应的是`IMAGE_DLLCHARACTERISTICS_APPCONTAINER`，但我不知道哪个API在调用`LdrLoadDll`时设置了该标志。最初我猜测的是[LoadPackagedLibrary](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-loadpackagedlibrary)，然而事实并非如此。

测试该标志的简单PowerShell脚本如下所示：

```
Import-Module NtObjectManager

function Start-Dll `{`
    Param(
        [Parameter(Mandatory, Position = 0)]
        [string]$Name,
        [Parameter(Position = 1)]
        [int]$DllChars = 0
    )

    $src = @'
using NtApiDotNet;
using System;
using System.Runtime.InteropServices;

public static class DllLoader
`{`
    [DllImport("ntdll.dll")]
    static extern NtStatus LdrLoadDll(int dwFlags, ref int DllCharacteristics,
        [In] UnicodeString DllName, out IntPtr BaseAddress);

    public static IntPtr Load(string path, int dll_chars)
    `{`
        IntPtr base_address;
        LdrLoadDll(1, ref dll_chars, new UnicodeString(path), out base_address).ToNtException();
        return base_address;
    `}`
`}`
'@
    $asm = [NtApiDotNet.NtFile].Assembly.Location
    Add-Type -TypeDefinition $src -ReferencedAssemblies $asm
    [DllLoader]::Load($Name, $DllChars)
`}`
```

如果我们执行`Start-Dll "Path\To\Any.DLL"`命令，且目标DLL不在策略允许的位置中，那么DLL会加载失败。然而如果我们执行`Start-Dll "Path\To\Any.DLL" 0x1000`命令，可以发现DLL能被正常加载。



## 0x02 总结

从实际层面来看，DLL阻止机制还有更多细节，不单单是通过DLL加载程序绕过进程阻止策略这么简单。如果没办法调用`LdrLoadDll`或者写入进程内存，我们就没有那么容易绕过DLL验证机制（但这并非不可完成的任务）。

这是详解AppLocker的最后一篇文章，回头我可能会继续讨论AppX支持、SmartLocker以及其他一些有趣的技巧。
