> 原文链接: https://www.anquanke.com//post/id/204332 


# 恶意软件开发 Part 2


                                阅读量   
                                **125035**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者0xPat，文章来源：0xpat.github.io
                                <br>原文地址：[https://0xpat.github.io/Malware_development_part_3/](https://0xpat.github.io/Malware_development_part_3/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0133a24fb9aa83471f.png)](https://p5.ssl.qhimg.com/t0133a24fb9aa83471f.png)



## 简介

本文是恶意软件开发系列文章的第二篇。在本系列文章中，我们将探索并尝试实现多个恶意软件中使用的技术，恶意软件使用这些技术实现代码执行，绕过防御，以及持久化。

在本系列的上一篇文章中，我们讨论了用于沙箱检测，虚拟机检测和自动分析检测的方法。

这次，我们看看应用程序是怎么检测到它正在被分析人员调试或检查的。

注意：假定的执行环境为64位，所以部分代码示例可能无法在32位环境下工作（比如说代码里面有硬编码的8字节指针或者PE和PEB的内部布局不同）。除此之外，下面的代码示例中省略了错误检查。



## 检测并阻止手工分析

存在一些特定的特征可以表明恶意软件分析人员正在对程序进行手工查验。 为了保护我们的恶意软件，我们可以对这些特征进行检查，也可以让分析人员更加难以对软件进行逆向分析。

### <a class="reference-link" name="%E8%B0%83%E8%AF%95%E5%99%A8%E6%A3%80%E6%B5%8B"></a>调试器检测

首先要做的是检查程序是否是在连接了调试器的情况下执行的。目前有很多调试器检测技术，我们会讨论其中的一部分。 当然，每种技术都能被分析人员所预防，但有些技术会比其他的技术更复杂。

#### <a class="reference-link" name="%E6%9F%A5%E8%AF%A2%E4%BF%A1%E6%81%AF"></a>查询信息

可以直接“询问”操作系统程序是否连接了任何调试器。`IsDebuggerPresent`函数可以用来检查PEB中的`BeingDebugged`标志：

```
if (IsDebuggerPresent()) return;

// same check
PPEB pPEB = (PPEB)__readgsqword(0x60);
if (pPEB-&gt;BeingDebugged) return;
```

另一个类似的函数是`CheckRemoteDebuggerPresent`，它会调用`NtQueryInformationProcess`：

```
BOOL isDebuggerPresent = FALSE;
CheckRemoteDebuggerPresent(GetCurrentProcess(), &amp;isDebuggerPresent);
if (isDebuggerPresent) return;

// same check
typedef NTSTATUS(WINAPI *PNtQueryInformationProcess)(IN  HANDLE, IN  PROCESSINFOCLASS, OUT PVOID, IN ULONG, OUT PULONG);
PNtQueryInformationProcess pNtQueryInformationProcess = (PNtQueryInformationProcess)GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtQueryInformationProcess");
DWORD64 isDebuggerPresent2 = 0;
pNtQueryInformationProcess(GetCurrentProcess(), ProcessDebugPort, &amp;isDebuggerPresent2, sizeof DWORD64, NULL);
if (isDebuggerPresent2) return;
```

#### <a class="reference-link" name="%E6%A0%87%E5%BF%97%E4%BB%A5%E5%8F%8A%E5%85%B6%E4%BB%96%E5%80%BC"></a>标志以及其他值

在对程序进行调试的时候，会在进程地址空间中设置一些特定的标志。`NtGlobalFlag`是一个位于PEB中的标志集合，可以用来表示调试器是否存在。

注意：该方法无法检测到Visual Studio调试器（`msvsmon`）。

```
#define FLG_HEAP_ENABLE_TAIL_CHECK   0x10
#define FLG_HEAP_ENABLE_FREE_CHECK   0x20
#define FLG_HEAP_VALIDATE_PARAMETERS 0x40
#define NT_GLOBAL_FLAG_DEBUGGED (FLG_HEAP_ENABLE_TAIL_CHECK | FLG_HEAP_ENABLE_FREE_CHECK | FLG_HEAP_VALIDATE_PARAMETERS)
PDWORD pNtGlobalFlag = (PDWORD)(__readgsqword(0x60) + 0xBC);
if ((*pNtGlobalFlag) &amp; NT_GLOBAL_FLAG_DEBUGGED) return false;
```

进程的堆中有两个受调试器影响的有趣的标志`Flags`和`ForceFlags`。如果进程正在被调试，这些标志会具有特定的值。堆位置和标志位置（相对于堆）是和系统以及体系结构有关。

注意：该方法无法检测到Visual Studio调试器（`msvsmon`）。

```
PDWORD pHeapFlags = (PDWORD)((PBYTE)GetProcessHeap() + 0x70);
PDWORD pHeapForceFlags = (PDWORD)((PBYTE)GetProcessHeap() + 0x74);
if (*pHeapFlags ^ HEAP_GROWABLE || *pHeapForceFlags != 0) return false;
```

之前提到的`NtQueryInformationProcess`函数可以用来检查其他值：`ProcessDebugObjectHandle`和`ProcessDebugFlags`。

```
#define ProcessDebugObjectHandle 0x1E
#define ProcessDebugFlags 0x1F
HANDLE hProcessDebugObject = NULL;
DWORD processDebugFlags = 0;
pNtQueryInformationProcess(GetCurrentProcess(), (PROCESSINFOCLASS)ProcessDebugObjectHandle, &amp;hProcessDebugObject, sizeof HANDLE, NULL);
pNtQueryInformationProcess(GetCurrentProcess(), (PROCESSINFOCLASS)ProcessDebugFlags, &amp;processDebugFlags, sizeof DWORD, NULL);
if (hProcessDebugObject != NULL || processDebugFlags == 0) return;
```

#### <a class="reference-link" name="%E9%80%9A%E8%BF%87%E6%A3%80%E6%9F%A5%E4%BB%A3%E7%A0%81%E4%B8%AD%E7%9A%84%E5%8F%98%E5%8C%96%E6%9D%A5%E6%A3%80%E6%B5%8B%E6%96%AD%E7%82%B9"></a>通过检查代码中的变化来检测断点

当调试器在函数中设置**软件断点**时，会同时把一个中断指令注入函数代码（`INT 3`，操作码`0xCC`）。我们可以在运行时扫描函数代码，比较每个字节是否与`0xCC`操作码相同，或者直接计算函数字节的校验和并与正确的值（根据“有效”函数计算得到）做比较，以检查代码中是否存在`0xCC`操作码。但是我们需要知道函数的起始位置，可以在`CrucialFunction`之后使用存根函数，同时也要确保链接器不会对对象文件和库文件进行增量链接。可以使用`#pragma auto_inline(off)`阻止编译器对函数进行内联扩展。

```
#pragma comment(linker, "/INCREMENTAL:YES")

DWORD CalculateFunctionChecksum(PUCHAR functionStart, PUCHAR functionEnd)
`{`
    DWORD checksum = 0;
    while(functionStart &lt; functionEnd)
    `{`
        checksum += *functionStart;
        functionStart++;
    `}`
    return checksum;
`}`
#pragma auto_inline(off)
VOID CrucialFunction()
`{`
    int x = 0;
    x += 2;
`}`
VOID AfterCrucialFunction()
`{`
`}`;
#pragma auto_inline(on)

void main()
`{`
    DWORD originalChecksum = 3429;
    DWORD checksum = CalculateFunctionChecksum((PUCHAR)CrucialFunction, (PUCHAR)AfterCrucialFunction);
    if (checksum != originalChecksum) return;

    wprintf_s(L"Now hacking...n");
`}`
```

可以通过检查调试寄存器`DR0`到`DR3`来检测**硬件断点**：

```
CONTEXT context = `{``}`;
context.ContextFlags = CONTEXT_DEBUG_REGISTERS;
GetThreadContext(GetCurrentThread(), &amp;context);
if (context.Dr0 || context.Dr1 || context.Dr2 || context.Dr3) return;
```

#### <a class="reference-link" name="%E9%80%9A%E8%BF%87%E6%A3%80%E6%9F%A5%E5%86%85%E5%AD%98%E9%A1%B5%E9%9D%A2%E6%9D%83%E9%99%90%E6%9D%A5%E6%A3%80%E6%B5%8B%E6%96%AD%E7%82%B9"></a>通过检查内存页面权限来检测断点

检查内存页面权限可以帮助我们检测调试器设置的软件断点。首先需要确定进程工作集中的页面数，并分配足够大的缓冲区来存储所有信息。然后遍历所有内存页面并检查其权限，我们只关注有执行权限的页面。对于每个可执行页面，检查该页面是否[与其他进程共享](https://waleedassar.blogspot.com/2014/06/sharecount-as-anti-debugging-trick.html)（除非有人修改了内存，例如在代码中注入`INT 3`指令，否则**不应共享**）。

**（译者注：斜体部分我认为应该的“应共享”，已与作者联系，还未得到回复）**

```
BOOL debugged = false;

PSAPI_WORKING_SET_INFORMATION workingSetInfo;
QueryWorkingSet(GetCurrentProcess(), &amp;workingSetInfo, sizeof workingSetInfo);
DWORD requiredSize = sizeof PSAPI_WORKING_SET_INFORMATION * (workingSetInfo.NumberOfEntries + 20);
PPSAPI_WORKING_SET_INFORMATION pWorkingSetInfo = (PPSAPI_WORKING_SET_INFORMATION)VirtualAlloc(0, requiredSize, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
BOOL s = QueryWorkingSet(GetCurrentProcess(), pWorkingSetInfo, requiredSize);
for (int i = 0; i &lt; pWorkingSetInfo-&gt;NumberOfEntries; i++)
`{`
    PVOID physicalAddress = (PVOID)(pWorkingSetInfo-&gt;WorkingSetInfo[i].VirtualPage * 4096);
    MEMORY_BASIC_INFORMATION memoryInfo;
    VirtualQuery((PVOID)physicalAddress, &amp;memoryInfo, sizeof memoryInfo);
    if (memoryInfo.Protect &amp; (PAGE_EXECUTE | PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY))
    `{`
        if ((pWorkingSetInfo-&gt;WorkingSetInfo[i].Shared == 0) || (pWorkingSetInfo-&gt;WorkingSetInfo[i].ShareCount == 0))
        `{`
            debugged = true;
            break;
        `}`
    `}`
`}`

if (debugged) return;

wprintf_s(L"Now hacking...n");
```

#### <a class="reference-link" name="%E5%BC%82%E5%B8%B8%E5%A4%84%E7%90%86%E7%A8%8B%E5%BA%8F"></a>异常处理程序

一般来说，异常首先由调试器进行处理。如果我们可以添加新的异常或者修改异常处理的过程（以执行任意代码），那我们就可以发现调试器的存在，因为只有在没有调试器率先捕获异常的情况下，我们的代码才会执行。

结构化异常处理（SEH）是一种Windows异常处理机制。当异常出现而没有其他措施能够进行处理时，该异常会被传递给SEH。在运行时使用SEH可用于调试器检测。

在32位的环境中，异常处理程序以链表的形式出现，并且第一个元素的地址会被存储在TEB的开头。我们可以添加一个自定义处理程序并将其链接到列表的开头，该自定义异常处理程序可以表明程序并未进行调试。

但在64位的环境中，SEH操作是在内核模式下完成的（这可以防止栈上的SEH数据因为缓冲区溢出攻击而被覆盖），因此一般无法使用上述技术。但是，如果没有任何处理程序能够处理该异常，就会把它传递给`kernel32.UnhandledExceptionFilter`函数（这是异常处理的最后手段）。

可以设置一个自定义的过滤函数，该函数将使用`SetUnhandledExceptionFilter`函数从`UnhandledExceptionFilter`中调用。有趣的是，程序只有在不被调试的情况下，才会调用这个自定义的未处理异常过滤器。这是因为`UnhandledExceptionFilter`会使用带有`ProcessDebugPort`标志的`pNtQueryInformationProcess`函数来检查调试器的存在（与之前介绍的技术相同）。

所以我们可以注册任意的未处理异常过滤器函数，该函数可以说明程序未使用调试器。

```
BOOL isDebugged = TRUE;

LONG WINAPI CustomUnhandledExceptionFilter(PEXCEPTION_POINTERS pExceptionPointers)
`{`
    isDebugged = FALSE;
    return EXCEPTION_CONTINUE_EXECUTION;
`}`

void main()
`{`
    PTOP_LEVEL_EXCEPTION_FILTER previousUnhandledExceptionFilter = SetUnhandledExceptionFilter(CustomUnhandledExceptionFilter);
    RaiseException(EXCEPTION_FLT_DIVIDE_BY_ZERO, 0, 0, NULL);
    SetUnhandledExceptionFilter(previousUnhandledExceptionFilter);
    if (isDebugged) return;

    wprintf_s(L"Now hacking...n");
`}`
```

#### <a class="reference-link" name="%E5%88%9B%E5%BB%BA%E4%B8%AD%E6%96%AD"></a>创建中断

我们可以在代码中创建断点中断，调试器会将其解释为软件断点（就像是用户设置的断点）。接下来创建一个简单的SEH处理程序：

```
BOOL isDebugged = TRUE;
__try
`{`
    DebugBreak();
`}`
__except (GetExceptionCode() == EXCEPTION_BREAKPOINT ? EXCEPTION_EXECUTE_HANDLER : EXCEPTION_CONTINUE_SEARCH)
`{`
    isDebugged = FALSE;
`}`
if (isDebugged) return;
```

这种方法可以用于检测VS调试器（`msvsmon`）和`WinDbg`，但不能检测`x64dbg`。 后者似乎把“断点“异常传递给了SEH。

如果不使用`DebugBreak`而是使用`RaiseException`函数，可能会引发一些未定义的行为，调试器可能会让代码流变得混乱，并且让程序跳转到错误的地址，生成`EXCEPTION_ILLEGAL_INSTRUCTION`异常的循环。在增加程序的分析难度方面，这个方法可能很有用。

```
BOOL isDebugged = TRUE;
__try
`{`
    RaiseException(EXCEPTION_BREAKPOINT, 0, 0, NULL);
`}`
__except (GetExceptionCode() == EXCEPTION_BREAKPOINT ? EXCEPTION_EXECUTE_HANDLER : EXCEPTION_CONTINUE_SEARCH)
`{`
    isDebugged = FALSE;
`}`
if (isDebugged) return;
```

另一种查看调试器如何处理此类断点中断的方法是注册一个向量化的异常处理程序。

向量化异常处理是SEH的扩展。向量化异常处理程序并不会替代SEH，它们可以并行工作，但是VEH比SEH的优先级高，VEH处理程序在SEH处理程序之前被调用。无论如何，在调试器处理（或不处理）断点异常之后，VEH可能会被调用，也可能不会被调用。

使用`DebugBreak`函数可以重现与上面使用SEH的代码类似的情况（只有调试器不存在时才执行VEH）。这种方法可以用于检测VS调试器（`msvsmon`）和`WinDbg`，但不能检测`x64dbg`。

```
BOOL isDebugged = TRUE;

LONG WINAPI CustomVectoredExceptionHandler(PEXCEPTION_POINTERS pExceptionPointers)
`{`
    if (pExceptionPointers-&gt;ExceptionRecord-&gt;ExceptionCode == EXCEPTION_BREAKPOINT)
    `{`
        pExceptionPointers-&gt;ContextRecord-&gt;Rip++;
        return EXCEPTION_CONTINUE_EXECUTION;
    `}`
    return EXCEPTION_CONTINUE_SEARCH; // pass on other exceptions
`}`

void main()
`{`
    AddVectoredExceptionHandler(1, CustomVectoredExceptionHandler);
    DebugBreak();
    RemoveVectoredExceptionHandler(CustomVectoredExceptionHandler);
    if (isDebugged) return;

    wprintf_s(L"Now hacking...n");
`}`
```

同样，使用`RaiseException`函数会引发一些未定义的行为，生成`EXCEPTION_ILLEGAL_INSTRUCTION`异常的循环。可以使用该方法阻止对程序的分析：

```
LONG WINAPI CustomVectoredExceptionHandler(PEXCEPTION_POINTERS pExceptionPointers)
`{`
    // process all exceptions, including EXCEPTION_ILLEGAL_INSTRUCTION
    printf("xD");
    return EXCEPTION_CONTINUE_EXECUTION;
`}`

void main()
`{`
    AddVectoredExceptionHandler(1, CustomVectoredExceptionHandler);
    RaiseException(EXCEPTION_BREAKPOINT, 0, 0, NULL);
    RemoveVectoredExceptionHandler(CustomVectoredExceptionHandler);

    wprintf_s(L"Now hacking...n");
`}`
```

#### <a class="reference-link" name="%E8%87%AA%E8%B0%83%E8%AF%95"></a>自调试

如果进程已经在被调试，就不可能在该进程上再附加另一个调试器。如果想要使用这个方法检查程序是否在被调试，我们需要启动另一个进程，尝试把该进程附加到我们的程序上。

```
if (!DebugActiveProcess(pid))
`{`
    HANDLE hProcess = OpenProcess(PROCESS_TERMINATE, FALSE, pid);
    TerminateProcess(hProcess, 0);
`}`
```

### <a class="reference-link" name="%E4%B8%80%E8%88%AC%E7%9A%84%E5%88%86%E6%9E%90%E6%A3%80%E6%B5%8B"></a>一般的分析检测

通过遍历正在运行的进程或者已加载的库文件等资源，我们可能会发现分析人员正在试图对我们的程序进行逆向工程。关于这方面的更多信息，请查看此系列的上一篇文章（**文件、目录、进程以及窗口名称**小节）。

#### <a class="reference-link" name="%E6%89%A7%E8%A1%8C%E6%97%B6%E9%97%B4"></a>执行时间

上一篇文章中介绍的时间检查（用于沙箱检测）还可以用于检测程序是否正在被分析或调试。我们可以在执行某个指令块之前和之后检查系统时间，并假设该时间差应该小于某个限值。如果程序正在被分析，则该指令块中可能被设置了断点，这时候指令块的执行时间会超过假设的限值。

```
int t1 = GetTickCount64();
Hack(); // should take less than 5 seconds
int t2 = GetTickCount64();
if (((t2 - t1) / 1000) &gt; 5) return; 

wprintf_s(L"Now hacking more...n");
```

`GetTickCount64`函数可能会被劫持。为了解决该问题，我们可以使用上一篇文章中介绍的技术（请参阅**延迟执行**和**函数劫持(hooking)**小节）。

### <a class="reference-link" name="%E5%8A%A0%E5%A4%A7%E5%88%86%E6%9E%90%E7%9A%84%E9%9A%BE%E5%BA%A6"></a>加大分析的难度

#### <a class="reference-link" name="%E8%AE%A9%E8%B0%83%E8%AF%95%E5%99%A8%E6%97%A0%E6%B3%95%E5%8F%91%E7%8E%B0"></a>让调试器无法发现

我们可以使用Windows自带的功能让调试器无法发现线程，该线程会停止发送任何事件。这个过程中使用的函数（`NtSetInformationThread`）可能会被劫持，为了验证这一点，我们可以使用一些伪参数调用该函数并检查返回状态（参数错误时不应该返回`STATUS_SUCCESS`）。

```
typedef NTSTATUS(WINAPI *NtSetInformationThread)(IN HANDLE, IN THREADINFOCLASS, IN PVOID, IN ULONG);
NtSetInformationThread pNtSetInformationThread = (NtSetInformationThread)GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtSetInformationThread");
THREADINFOCLASS ThreadHideFromDebugger = (THREADINFOCLASS)0x11;
pNtSetInformationThread(GetCurrentThread(), ThreadHideFromDebugger, NULL, 0);
```

当然，这个方法不会影响隐藏线程之前发送的事件。

同样，我们也可以使用`NtCreateThreadEx`函数创建一个新线程，并让调试器无法发现该线程。 这个新线程不会把事件发送到调试器。

```
typedef NTSTATUS(WINAPI *NtCreateThreadEx)(OUT PHANDLE, IN ACCESS_MASK, IN PVOID, IN HANDLE, IN PTHREAD_START_ROUTINE, IN PVOID, IN ULONG, IN SIZE_T, IN SIZE_T, IN SIZE_T, OUT PVOID);
NtCreateThreadEx pNtCreateThreadEx = (NtCreateThreadEx)GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtCreateThreadEx");
#define THREAD_CREATE_FLAGS_HIDE_FROM_DEBUGGER 0x4
HANDLE hThread;
pNtCreateThreadEx(&amp;hThread, 0x1FFFFF, NULL, GetCurrentProcess(), (PTHREAD_START_ROUTINE)shellcode_exec, NULL, THREAD_CREATE_FLAGS_HIDE_FROM_DEBUGGER, NULL, NULL, NULL, NULL);
WaitForSingleObject(hThread, INFINITE);
```

创建新线程本身就可以让程序的分析更加复杂。 因为除非在适当的位置设置了断点，否则新线程中的代码可以任意执行。

#### <a class="reference-link" name="%E6%89%A7%E8%A1%8C%E8%B7%AF%E5%BE%84"></a>执行路径

让代码执行路径复杂化也可以使程序分析更加困难。在前面提到的异常处理程序中执行恶意代码就很好，而且不容易被人发现。也可以利用使用回调的Windows API函数（还记得`EnumDisplayMonitors`吗？）。有[许多使用回调的函数](https://secrary.com/Random/HinderMalwareAnalyst/)，比如说下面这个扩展的文件读写操作：

```
VOID CALLBACK MyCallback(DWORD errorCode, DWORD bytesTransferred, POVERLAPPED pOverlapped)
`{`
    MessageBoxW(NULL, L"Catch me if you can", L"xD", 0);
`}`

void main()
`{`
    HANDLE hFile = CreateFileW(L"C:\Windows\win.ini", GENERIC_READ, 0, NULL, OPEN_EXISTING, FILE_FLAG_OVERLAPPED, NULL);
    PVOID fileBuffer = VirtualAlloc(0, 64, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    OVERLAPPED overlapped = `{`0`}`;
    ReadFileEx(hFile, fileBuffer, 32, &amp;overlapped, MyCallback);

    WaitForSingleObjectEx(hFile, INFINITE, true); // wait for the asynchronous operation to finish
    wprintf_s(L"Already pwned...n");
`}`
```

#### <a class="reference-link" name="TLS%E5%9B%9E%E8%B0%83"></a>TLS回调

TLS（线程本地存储）回调是一种Windows机制，它允许在进程/线程开始和终止的时候执行任意代码。可以用它在`main`函数（或其他入口点）开始之前运行一些反调试代码。但是，大多数调试器会自动放置一个断点在`main`之前（“系统断点”，`ntdll.LdrpDoDebuggerBreak`），有的甚至直接放置在回调开始的地方。无论如何，回调的实现需要一些链接器指令：

```
void NTAPI TlsCallback(PVOID DllHandle, DWORD dwReason, PVOID)
`{`
    if (dwReason == DLL_PROCESS_ATTACH)
    `{`
        if (CheckIfDebugged()) exit(0);
    `}`
`}`

#pragma comment (linker, "/INCLUDE:_tls_used")
#pragma comment (linker, "/INCLUDE:tls_callback_function")

#pragma const_seg(".CRT$XLA")
EXTERN_C const PIMAGE_TLS_CALLBACK tls_callback_function = TlsCallback;
#pragma const_seg()

void main()
`{`
    wprintf_s(L"Now hacking...n");
`}`
```

在比较旧的Windows版本上，可以使用TLS回调检测调试器在进程中创建的新线程。从Windows 7开始，`DebugActiveProcess`在调用`NtCreateThreadEx`函数时会带有一个标志，该标志会在新线程的环境块中设置`SkipThreadAttach`标志，从而阻止TLS回调的执行。

#### <a class="reference-link" name="%E9%98%BB%E6%AD%A2%E7%94%A8%E6%88%B7%E8%BE%93%E5%85%A5"></a>阻止用户输入

如果程序是以管理员的身份运行，我们就可以阻止键盘和鼠标事件。但是安全提示序列（`CTRL + ALT + DEL`）可以绕过这种阻止，因为内核会捕获这个事件。

```
BlockInput(true);
```



## 总结

本文就到这里，我们已经可以在代码中实现一些调试器检测技术了。 当然，熟练的逆向人员可以禁用上面介绍的所有技巧，我们不可能让调试器完全无法调试我们的程序，但是我们可以让这个过程更加困难。这也是本文的重点，反病毒引擎或者检测人员在理解代码并提取IoC上花的时间越长，我们就有越多的时间攻击用户并占领系统。

下一篇文章中，我们将讨论恶意软件的静态分析和混淆，重点关注PE格式。



## 链接

请确保你查看了下面这些和此次主题有关的资源：

[https://www.apriorit.com/dev-blog/367-anti-reverse-engineering-protection-techniques-to-use-before-releasing-software](https://www.apriorit.com/dev-blog/367-anti-reverse-engineering-protection-techniques-to-use-before-releasing-software)

[https://anti-reversing.com/Downloads/Anti-Reversing/The_Ultimate_Anti-Reversing_Reference.pdf](https://anti-reversing.com/Downloads/Anti-Reversing/The_Ultimate_Anti-Reversing_Reference.pdf)

[http://antukh.com/blog/2015/01/19/malware-techniques-cheat-sheet/](http://antukh.com/blog/2015/01/19/malware-techniques-cheat-sheet/)

[https://github.com/LordNoteworthy/al-khaser/tree/master/al-khaser/AntiDebug](https://github.com/LordNoteworthy/al-khaser/tree/master/al-khaser/AntiDebug)

[https://secrary.com/Random/HinderMalwareAnalyst/](https://secrary.com/Random/HinderMalwareAnalyst/)
