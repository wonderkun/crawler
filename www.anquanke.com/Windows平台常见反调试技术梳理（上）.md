> 原文链接: https://www.anquanke.com//post/id/179709 


# Windows平台常见反调试技术梳理（上）


                                阅读量   
                                **255454**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者apriorit，文章来源：apriorit.com
                                <br>原文地址：[https://www.apriorit.com/dev-blog/367-anti-reverse-engineering-protection-techniques-to-use-before-releasing-software](https://www.apriorit.com/dev-blog/367-anti-reverse-engineering-protection-techniques-to-use-before-releasing-software)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01994c5e221f0608d2.png)](https://p1.ssl.qhimg.com/t01994c5e221f0608d2.png)



## 0x00 前言

在软件领域，逆向工程是针对应用程序的研究过程，目的是获取应用程序未公开的工作原理及使用的具体算法。虽然软件逆向可以用于[合法场景](https://www.apriorit.com/competences/reverse-engineering)（比如恶意软件分析或者未公开文档的系统研究），但也可能被黑客用于非法活动。

Apriorit的[研究及逆向团队](https://www.apriorit.com/competences/reverse-engineering)决定与大家分享在这方面的专业经验，也会分享常用的一些简单和高级技术，大家可以使用这些技术避免自己的软件被非法逆向。当然，这些小伙伴们是最纯粹的黑客，他们可以借此机会展示自己的实力，让大家了解经验丰富的逆向工程如何绕过这些防护机制（他们也提供了几个代码示例）。

我们的小伙伴们给出了一些防护技术，包括效果一般以及效果较好的几种技术，大家可以根据自己情况决选择具体的方案。

本文适用于对反逆向技术感兴趣的所有软件开发者以及逆向工程师。为了理解本文介绍的所有示例及反调试技术，大家需要具备汇编知识、一些WinDbg经验以及使用API函数在Windows平台上开发的经验。



## 0x01 反调试方法

为了分析软件，我们可以使用多种方法：

1、数据交换过程中使用报文嗅探软件来分析网络上交换的数据；

2、反汇编软件二进制代码，获取对应的汇编语言；

3、反编译二进制数据或者字节码，以便在高级编程语言中重构源代码。

本文介绍了常用的反破解和反逆向保护技术，也就是Windows平台中的反调试方法。这里我们需要注意的是，我们不可能完全避免软件被逆向分析。各种反逆向技术的主要目标只是尽可能地提高逆向分析过程的复杂度。

想要成功防护逆向分析，最好的方法就是了解逆向分析的切入点。本文介绍了常用的反调试技术，从最简单的开始讲解，也介绍了如何绕过这些技术。我们不会关注不同的软件保护理论，只立足于具体的例子。

### <a class="reference-link" name="IsDebuggerPresent"></a>IsDebuggerPresent

也许最简单的反调试方法就是调用`IsDebuggerPresent`函数，该函数会检查用户模式调试器是否正在调试该进程。示例代码如下：

```
int main()
`{`
    if (IsDebuggerPresent())
    `{`
        std::cout &lt;&lt; "Stop debugging program!" &lt;&lt; std::endl;
        exit(-1);
    `}`
    return 0;
`}`
```

如果进一步观察`IsDebuggerPresent`函数，我们可以找到如下代码：

```
0:000&lt; u kernelbase!IsDebuggerPresent L3
KERNELBASE!IsDebuggerPresent:
751ca8d0 64a130000000    mov     eax,dword ptr fs:[00000030h]
751ca8d6 0fb64002        movzx   eax,byte ptr [eax+2]
751ca8da c3              ret
```

对于x64进程：

```
0:000&lt; u kernelbase!IsDebuggerPresent L3
KERNELBASE!IsDebuggerPresent:
00007ffc`ab6c1aa0 65488b042560000000 mov   rax,qword ptr gs:[60h]
00007ffc`ab6c1aa9 0fb64002           movzx eax,byte ptr [rax+2]
00007ffc`ab6c1aad c3                 ret
```

观察相对`fs`段`30h`偏移的PEB（Process Environment Block）结构（对于x64系统则是相对`gs`段`60h`的偏移）。如果我们观察PEB中的offset为2的数据，就可以找到`BeingDebugged`字段：

```
0:000&lt; dt _PEB
ntdll!_PEB
   +0x000 InheritedAddressSpace : UChar
   +0x001 ReadImageFileExecOptions : UChar
   +0x002 BeingDebugged    : UChar
```

换句话说，`IsDebuggerPresent`函数会读取`BeingDebugged`字段的值。如果该进程正在被调试，那么这个值为1，否则为0。

**PEB（Process Environment Block）**

PEB是Windows操作系统内部使用的一个封闭结构。根据具体环境的不同，我们需要通过不同方法获取PEB结构指针。比如，我们可以使用如下代码获取x32及x64系统的PEB指针：

```
// Current PEB for 64bit and 32bit processes accordingly
PVOID GetPEB()
`{`
#ifdef _WIN64
    return (PVOID)__readgsqword(0x0C * sizeof(PVOID));
#else
    return (PVOID)__readfsdword(0x0C * sizeof(PVOID));
#endif
`}`
```

`WOW64`机制适用于在x64系统上启动的x32进程，此时会创建另一个PEB结构。在`WOW64`环境中，我们可以使用如下代码获取PEB结构指针：

```
// Get PEB for WOW64 Process
PVOID GetPEB64()
`{`
    PVOID pPeb = 0;
#ifndef _WIN64
    // 1. There are two copies of PEB - PEB64 and PEB32 in WOW64 process
    // 2. PEB64 follows after PEB32
    // 3. This is true for versions lower than Windows 8, else __readfsdword returns address of real PEB64
    if (IsWin8OrHigher())
    `{`
        BOOL isWow64 = FALSE;
        typedef BOOL(WINAPI *pfnIsWow64Process)(HANDLE hProcess, PBOOL isWow64);
        pfnIsWow64Process fnIsWow64Process = (pfnIsWow64Process)
            GetProcAddress(GetModuleHandleA("Kernel32.dll"), "IsWow64Process");
        if (fnIsWow64Process(GetCurrentProcess(), &amp;isWow64))
        `{`
            if (isWow64)
            `{`
                pPeb = (PVOID)__readfsdword(0x0C * sizeof(PVOID));
                pPeb = (PVOID)((PBYTE)pPeb + 0x1000);
            `}`
        `}`
    `}`
#endif
    return pPeb;
`}`
```

检查操作系统版本的示例代码如下所示：

```
WORD GetVersionWord()
`{`
    OSVERSIONINFO verInfo = `{` sizeof(OSVERSIONINFO) `}`;
    GetVersionEx(&amp;verInfo);
    return MAKEWORD(verInfo.dwMinorVersion, verInfo.dwMajorVersion);
`}`
BOOL IsWin8OrHigher() `{` return GetVersionWord() &gt;= _WIN32_WINNT_WIN8; `}`
BOOL IsVistaOrHigher() `{` return GetVersionWord() &gt;= _WIN32_WINNT_VISTA; `}`
```

**如何绕过**

为了绕过`IsDebuggerPresent`检查机制，我们可以在检查代码执行之前，将`BeingDebugged`设置为0。我们可以使用DLL注入来完成该任务：

```
mov eax, dword ptr fs:[0x30]  
mov byte ptr ds:[eax+2], 0
```

对于x64进程：

```
DWORD64 dwpeb = __readgsqword(0x60);
*((PBYTE)(dwpeb + 2)) = 0;
```

### <a class="reference-link" name="TLS%E5%9B%9E%E8%B0%83"></a>TLS回调

检查main函数中是否存在调试器并不是最好的方法，并且逆向人员在分析反汇编代码时首先就会观察这个位置。在main中设置的检查机制可以通过`NOP`指令擦除，从而解除防护机制。如果使用了CRT库，main线程在将控制权交给main函数之前已经有个调用栈。因此我们也可以在TLS回调中检查是否存在调试器。可执行模块入口点调用之前会调用这个回调函数。

```
#pragma section(".CRT$XLY", long, read)
__declspec(thread) int var = 0xDEADBEEF;
VOID NTAnopPI TlsCallback(PVOID DllHandle, DWORD Reason, VOID Reserved)
`{`
    var = 0xB15BADB0; // Required for TLS Callback call
    if (IsDebuggerPresent())
    `{`
        MessageBoxA(NULL, "Stop debugging program!", "Error", MB_OK | MB_ICONERROR);
        TerminateProcess(GetCurrentProcess(), 0xBABEFACE);
    `}`
`}`
__declspec(allocate(".CRT$XLY"))PIMAGE_TLS_CALLBACK g_tlsCallback = TlsCallback;
```

### <a class="reference-link" name="NtGlobalFlag"></a>NtGlobalFlag

在Windows NT中，`NtGlobalFlag`全局变量中存放着一组标志，整个系统都可以使用这个变量。在启动时，系统会使用注册表中的值来初始化`NtGlobalFlag`全局系统变量：

```
[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\GlobalFlag]
```

这个变量的值可以用于系统跟踪、调试以及控制场景。变量标志没有公开文档，但SDK中包含`gflags`工具，我们可以使用该工具来编辑一个全局标志值。PEB结构同样包含`NtGlobalFlag`字段，并且在位结构上没有与`NtGlobalFlag`全局系统变量对应。在调试过程中，`NtGlobalFlag`字段会设置如下标志：

```
FLG_HEAP_ENABLE_TAIL_CHECK (0x10)
FLG_HEAP_ENABLE_FREE_CHECK (0x20)
FLG_HEAP_VALIDATE_PARAMETERS (0x40)
```

为了判断进程是否由调试器所启动，我们可以检查PEB结构中的`NtGlobalFlag`字段。在x32及x64系统中，这个字段分别相对PEB结构的偏移地址为`0x068`以及`0x0bc`。

```
0:000&gt; dt _PEB NtGlobalFlag @$peb 
ntdll!_PEB
   +0x068 NtGlobalFlag : 0x70
```

对于x64进程：

```
0:000&gt; dt _PEB NtGlobalFlag @$peb
ntdll!_PEB
   +0x0bc NtGlobalFlag : 0x70
```

如下代码片段演示了基于`NtGlobalFlag`字段的反调试技术：

```
#define FLG_HEAP_ENABLE_TAIL_CHECK   0x10
#define FLG_HEAP_ENABLE_FREE_CHECK   0x20
#define FLG_HEAP_VALIDATE_PARAMETERS 0x40
#define NT_GLOBAL_FLAG_DEBUGGED (FLG_HEAP_ENABLE_TAIL_CHECK | FLG_HEAP_ENABLE_FREE_CHECK | FLG_HEAP_VALIDATE_PARAMETERS)
void CheckNtGlobalFlag()
`{`
    PVOID pPeb = GetPEB();
    PVOID pPeb64 = GetPEB64();
    DWORD offsetNtGlobalFlag = 0;
#ifdef _WIN64
    offsetNtGlobalFlag = 0xBC;
#else
    offsetNtGlobalFlag = 0x68;
#endif
    DWORD NtGlobalFlag = *(PDWORD)((PBYTE)pPeb + offsetNtGlobalFlag);
    if (NtGlobalFlag &amp; NT_GLOBAL_FLAG_DEBUGGED)
    `{`
        std::cout &lt;&lt; "Stop debugging program!" &lt;&lt; std::endl;
        exit(-1);
    `}`
    if (pPeb64)
    `{`
        DWORD NtGlobalFlagWow64 = *(PDWORD)((PBYTE)pPeb64 + 0xBC);
        if (NtGlobalFlagWow64 &amp; NT_GLOBAL_FLAG_DEBUGGED)
        `{`
            std::cout &lt;&lt; "Stop debugging program!" &lt;&lt; std::endl;
            exit(-1);
        `}`
    `}`
`}`
```

**绕过方法**

为了绕过`NtGlobalFlag`检查，只需要在检查操作前执行我们的操作即可。换句话说，我们需要在反调试保护机制检查这个值之前，将被调试进程PEB结构中的`NtGlobalFlag`字段设置为0。

**NtGlobalFlag以及IMAGE_LOAD_CONFIG_DIRECTORY**

可执行文件中可以包含`IMAGE_LOAD_CONFIG_DIRECTORY`结构，该结构中包含系统加载程序所需的其他配置参数。默认情况下这个结构体并不会内置于可执行文件中，但可以使用patch方式进行添加。该结构中包含一个`GlobalFlagsClear`字段，用来标识PEB结构`NtGlobalFlag`字段中哪个标志需要被重置。如果可执行文件在最初创建时没有使用该结构，或者`GlobalFlagsClear`的值为0，那么不管在磁盘上还是在内存中，该字段值为0则表示系统中存在一个隐藏的调试器。如下示例代码会检查正在运行进程以及磁盘文件中的`GlobalFlagsClear`字段值，从而发现常见的一种反调试技术：

```
PIMAGE_NT_HEADERS GetImageNtHeaders(PBYTE pImageBase)
`{`
    PIMAGE_DOS_HEADER pImageDosHeader = (PIMAGE_DOS_HEADER)pImageBase;
    return (PIMAGE_NT_HEADERS)(pImageBase + pImageDosHeader-&gt;e_lfanew);
`}`
PIMAGE_SECTION_HEADER FindRDataSection(PBYTE pImageBase)
`{`
    static const std::string rdata = ".rdata";
    PIMAGE_NT_HEADERS pImageNtHeaders = GetImageNtHeaders(pImageBase);
    PIMAGE_SECTION_HEADER pImageSectionHeader = IMAGE_FIRST_SECTION(pImageNtHeaders);
    int n = 0;
    for (; n &lt; pImageNtHeaders-&gt;FileHeader.NumberOfSections; ++n)
    `{`
        if (rdata == (char*)pImageSectionHeader[n].Name)
        `{`
            break;
        `}`
    `}`
    return &amp;pImageSectionHeader[n];
`}`
void CheckGlobalFlagsClearInProcess()
`{`
    PBYTE pImageBase = (PBYTE)GetModuleHandle(NULL);
    PIMAGE_NT_HEADERS pImageNtHeaders = GetImageNtHeaders(pImageBase);
    PIMAGE_LOAD_CONFIG_DIRECTORY pImageLoadConfigDirectory = (PIMAGE_LOAD_CONFIG_DIRECTORY)(pImageBase
        + pImageNtHeaders-&gt;OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG].VirtualAddress);
    if (pImageLoadConfigDirectory-&gt;GlobalFlagsClear != 0)
    `{`
        std::cout &lt;&lt; "Stop debugging program!" &lt;&lt; std::endl;
        exit(-1);
    `}`
`}`
void CheckGlobalFlagsClearInFile()
`{`
    HANDLE hExecutable = INVALID_HANDLE_VALUE;
    HANDLE hExecutableMapping = NULL;
    PBYTE pMappedImageBase = NULL;
    __try
    `{`
        PBYTE pImageBase = (PBYTE)GetModuleHandle(NULL);
        PIMAGE_SECTION_HEADER pImageSectionHeader = FindRDataSection(pImageBase);
        TCHAR pszExecutablePath[MAX_PATH];
        DWORD dwPathLength = GetModuleFileName(NULL, pszExecutablePath, MAX_PATH);
        if (0 == dwPathLength) __leave;
        hExecutable = CreateFile(pszExecutablePath, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
        if (INVALID_HANDLE_VALUE == hExecutable) __leave;
        hExecutableMapping = CreateFileMapping(hExecutable, NULL, PAGE_READONLY, 0, 0, NULL);
        if (NULL == hExecutableMapping) __leave;
        pMappedImageBase = (PBYTE)MapViewOfFile(hExecutableMapping, FILE_MAP_READ, 0, 0,
            pImageSectionHeader-&gt;PointerToRawData + pImageSectionHeader-&gt;SizeOfRawData);
        if (NULL == pMappedImageBase) __leave;
        PIMAGE_NT_HEADERS pImageNtHeaders = GetImageNtHeaders(pMappedImageBase);
        PIMAGE_LOAD_CONFIG_DIRECTORY pImageLoadConfigDirectory = (PIMAGE_LOAD_CONFIG_DIRECTORY)(pMappedImageBase 
            + (pImageSectionHeader-&gt;PointerToRawData
                + (pImageNtHeaders-&gt;OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG].VirtualAddress - pImageSectionHeader-&gt;VirtualAddress)));
        if (pImageLoadConfigDirectory-&gt;GlobalFlagsClear != 0)
        `{`
            std::cout &lt;&lt; "Stop debugging program!" &lt;&lt; std::endl;
            exit(-1);
        `}`
    `}`
    __finally
    `{`
        if (NULL != pMappedImageBase)
            UnmapViewOfFile(pMappedImageBase);
        if (NULL != hExecutableMapping)
            CloseHandle(hExecutableMapping);
        if (INVALID_HANDLE_VALUE != hExecutable)
            CloseHandle(hExecutable);
    `}` 
`}`
```

在示例代码中，`CheckGlobalFlagsClearInProcess`函数通过当前运行进程的加载地址来查找`PIMAGE_LOAD_CONFIG_DIRECTORY`结构，检查`GlobalFlagsClear`字段的值。如果这个值不等于0，那么进程很有可能正在被调试中。`CheckGlobalFlagsClearInFile`函数会针对磁盘上的可执行文件采用相同检查操作。

### <a class="reference-link" name="%E5%A0%86%E6%A0%87%E5%BF%97%E4%BB%A5%E5%8F%8AForceFlags"></a>堆标志以及ForceFlags

PEB结构中包含指向进程堆（`_HEAP`结构）的一个指针：

```
0:000&gt; dt _PEB ProcessHeap @$peb
ntdll!_PEB
   +0x018 ProcessHeap : 0x00440000 Void
0:000&gt; dt _HEAP Flags ForceFlags 00440000 
ntdll!_HEAP
   +0x040 Flags      : 0x40000062
   +0x044 ForceFlags : 0x40000060
```

对于x64进程：

```
0:000&gt; dt _PEB ProcessHeap @$peb
ntdll!_PEB
   +0x030 ProcessHeap : 0x0000009d`94b60000 Void
0:000&gt; dt _HEAP Flags ForceFlags 0000009d`94b60000
ntdll!_HEAP
   +0x070 Flags      : 0x40000062
   +0x074 ForceFlags : 0x40000060
```

如果进程正在被调试，那么`Flags`和`ForceFlags`字段都会被设置成与调试相关的值：

1、如果`Flags`字段没有设置`HEAP_GROWABLE`（`0x00000002`标志），那么该进程正在被调试；

2、如果`ForceFlags`的值不为0，那么该进程正在被调试。

需要注意的是，`_HEAP`结构并没有公开，并且不同操作系统版本中`Flags`和`ForceFlags`字段的偏移值也有所不同。如下代码演示了基于堆标志的反调试技术：

```
int GetHeapFlagsOffset(bool x64)
`{`
    return x64 ?
        IsVistaOrHigher() ? 0x70 : 0x14: //x64 offsets
        IsVistaOrHigher() ? 0x40 : 0x0C; //x86 offsets
`}`
int GetHeapForceFlagsOffset(bool x64)
`{`
    return x64 ?
        IsVistaOrHigher() ? 0x74 : 0x18: //x64 offsets
        IsVistaOrHigher() ? 0x44 : 0x10; //x86 offsets
`}`
void CheckHeap()
`{`
    PVOID pPeb = GetPEB();
    PVOID pPeb64 = GetPEB64();
    PVOID heap = 0;
    DWORD offsetProcessHeap = 0;
    PDWORD heapFlagsPtr = 0, heapForceFlagsPtr = 0;
    BOOL x64 = FALSE;
#ifdef _WIN64
    x64 = TRUE;
    offsetProcessHeap = 0x30;
#else
    offsetProcessHeap = 0x18;
#endif
    heap = (PVOID)*(PDWORD_PTR)((PBYTE)pPeb + offsetProcessHeap);
    heapFlagsPtr = (PDWORD)((PBYTE)heap + GetHeapFlagsOffset(x64));
    heapForceFlagsPtr = (PDWORD)((PBYTE)heap + GetHeapForceFlagsOffset(x64));
    if (*heapFlagsPtr &amp; ~HEAP_GROWABLE || *heapForceFlagsPtr != 0)
    `{`
        std::cout &lt;&lt; "Stop debugging program!" &lt;&lt; std::endl;
        exit(-1);
    `}`
    if (pPeb64)
    `{`
        heap = (PVOID)*(PDWORD_PTR)((PBYTE)pPeb64 + 0x30);
        heapFlagsPtr = (PDWORD)((PBYTE)heap + GetHeapFlagsOffset(true));
        heapForceFlagsPtr = (PDWORD)((PBYTE)heap + GetHeapForceFlagsOffset(true));
        if (*heapFlagsPtr &amp; ~HEAP_GROWABLE || *heapForceFlagsPtr != 0)
        `{`
            std::cout &lt;&lt; "Stop debugging program!" &lt;&lt; std::endl;
            exit(-1);
        `}`
    `}`
`}`
```

**如何绕过**

为了绕过基于堆标志的反调试防护机制，我们可以将`Flags`字段的`HEAP_GROWABLE`标志设置为0，以及将`ForceFlags`字段的值设置为0。显然，这些字段应当在堆标志检查之前重新设置才有效。

### <a class="reference-link" name="Trap%E6%A0%87%E5%BF%97"></a>Trap标志

Trap标志（TF）位于[EFLAGS](https://en.wikipedia.org/wiki/FLAGS_register)寄存器中。如果TF被设置为1，那么CPU就会在每次执行指令后生成`INT 01h`中断或者“单步”（Single Step）异常。如下代码演示了基于TF设置以及异常调用检查的反调试技术：

```
BOOL isDebugged = TRUE;
__try
`{`
    __asm
    `{`
        pushfd
        or dword ptr[esp], 0x100 // set the Trap Flag 
        popfd                    // Load the value into EFLAGS register
        nop
    `}`
`}`
__except (EXCEPTION_EXECUTE_HANDLER)
`{`
    // If an exception has been raised – debugger is not present
    isDebugged = FALSE;
`}`
if (isDebugged)
`{`
    std::cout &lt;&lt; "Stop debugging program!" &lt;&lt; std::endl;
    exit(-1);
`}`
```

其中设置TF来生成异常。如果进程正在被调试，那么调试器就会捕获到异常。

**如何绕过**

如果想在调试过程中绕过TF检查，我们可以跳过`pushfd`指令，在其后设置断点并继续执行程序，这样在断点后我们就可以继续跟踪。

### <a class="reference-link" name="CheckRemoteDebuggerPresent%E4%BB%A5%E5%8F%8ANtQueryInformationProcess"></a>CheckRemoteDebuggerPresent以及NtQueryInformationProcess

与`IsDebuggerPresent`函数不同，[CheckRemoteDebuggerPresent](https://msdn.microsoft.com/en-us/library/windows/desktop/ms679280(v=vs.85).aspx)会检查进程是否被另一个并行进程调试。基于`CheckRemoteDebuggerPresent`的反调试技术示例代码如下所示：

```
int main(int argc, char *argv[])
`{`
    BOOL isDebuggerPresent = FALSE;
    if (CheckRemoteDebuggerPresent(GetCurrentProcess(), &amp;isDebuggerPresent ))
    `{`
        if (isDebuggerPresent )
        `{`
            std::cout &lt;&lt; "Stop debugging program!" &lt;&lt; std::endl;
            exit(-1);
        `}`
    `}`
    return 0;
`}`
```

`CheckRemoteDebuggerPresent`中会调用`NtQueryInformationProcess`函数：

```
0:000&gt; uf kernelbase!CheckRemotedebuggerPresent
KERNELBASE!CheckRemoteDebuggerPresent:
...
75207a24 6a00            push    0
75207a26 6a04            push    4
75207a28 8d45fc          lea     eax,[ebp-4]
75207a2b 50              push    eax
75207a2c 6a07            push    7
75207a2e ff7508          push    dword ptr [ebp+8]
75207a31 ff151c602775    call    dword ptr [KERNELBASE!_imp__NtQueryInformationProcess (7527601c)]
75207a37 85c0            test    eax,eax
75207a39 0f88607e0100    js      KERNELBASE!CheckRemoteDebuggerPresent+0x2b (7521f89f)
...
```

如果我们查看[NtQueryInformationProcess](https://msdn.microsoft.com/en-us/library/windows/desktop/ms684280(v=vs.85).aspx)文档，就可知上面汇编代码中，因为`ProcessInformationClass`参数（第2个参数）值为7，`CheckRemoteDebuggerPresent`函数会被赋予`DebugPort`值。如下反调试示例代码就调用了`NtQueryInformationProcess`：

```
typedef NTSTATUS(NTAPI *pfnNtQueryInformationProcess)(
    _In_      HANDLE           ProcessHandle,
    _In_      UINT             ProcessInformationClass,
    _Out_     PVOID            ProcessInformation,
    _In_      ULONG            ProcessInformationLength,
    _Out_opt_ PULONG           ReturnLength
    );
const UINT ProcessDebugPort = 7;
int main(int argc, char *argv[])
`{`
    pfnNtQueryInformationProcess NtQueryInformationProcess = NULL;
    NTSTATUS status;
    DWORD isDebuggerPresent = 0;
    HMODULE hNtDll = LoadLibrary(TEXT("ntdll.dll"));

    if (NULL != hNtDll)
    `{`
        NtQueryInformationProcess = (pfnNtQueryInformationProcess)GetProcAddress(hNtDll, "NtQueryInformationProcess");
        if (NULL != NtQueryInformationProcess)
        `{`
            status = NtQueryInformationProcess(
                GetCurrentProcess(),
                ProcessDebugPort,
                &amp;isDebuggerPresent,
                sizeof(DWORD),
                NULL);
            if (status == 0x00000000 &amp;&amp; isDebuggerPresent != 0)
            `{`
                std::cout &lt;&lt; "Stop debugging program!" &lt;&lt; std::endl;
                exit(-1);
            `}`
        `}`
    `}`
    return 0;
`}`
```

**如何绕过 **

为了绕过`CheckRemoteDebuggerPresent`以及`NTQueryInformationProcess`，我们需要替换`NtQueryInformationProcess`函数的返回值。我们可以使用[mhook](https://github.com/martona/mhook)来完成这个任务。为了设置hook，我们需要将DLL注入被调试的进程，然后使用mhook在`DLLMain`中设置hook。使用mhook的示例代码如下：

```
#include &lt;Windows.h&gt;
#include "mhook.h"
typedef NTSTATUS(NTAPI *pfnNtQueryInformationProcess)(
    _In_      HANDLE           ProcessHandle,
    _In_      UINT             ProcessInformationClass,
    _Out_     PVOID            ProcessInformation,
    _In_      ULONG            ProcessInformationLength,
    _Out_opt_ PULONG           ReturnLength
    );
const UINT ProcessDebugPort = 7;
pfnNtQueryInformationProcess g_origNtQueryInformationProcess = NULL;
NTSTATUS NTAPI HookNtQueryInformationProcess(
    _In_      HANDLE           ProcessHandle,
    _In_      UINT             ProcessInformationClass,
    _Out_     PVOID            ProcessInformation,
    _In_      ULONG            ProcessInformationLength,
    _Out_opt_ PULONG           ReturnLength
    )
`{`
    NTSTATUS status = g_origNtQueryInformationProcess(
        ProcessHandle,
        ProcessInformationClass,
        ProcessInformation,
        ProcessInformationLength,
        ReturnLength);
    if (status == 0x00000000 &amp;&amp; ProcessInformationClass == ProcessDebugPort)
    `{`
        *((PDWORD_PTR)ProcessInformation) = 0;
    `}`
    return status;
`}`
DWORD SetupHook(PVOID pvContext)
`{`
    HMODULE hNtDll = LoadLibrary(TEXT("ntdll.dll"));
    if (NULL != hNtDll)
    `{`
        g_origNtQueryInformationProcess = (pfnNtQueryInformationProcess)GetProcAddress(hNtDll, "NtQueryInformationProcess");
        if (NULL != g_origNtQueryInformationProcess)
        `{`
            Mhook_SetHook((PVOID*)&amp;g_origNtQueryInformationProcess, HookNtQueryInformationProcess);
        `}`
    `}`
    return 0;
`}`
BOOL WINAPI DllMain(HINSTANCE hInstDLL, DWORD fdwReason, LPVOID lpvReserved)
`{`
    switch (fdwReason)
    `{`
    case DLL_PROCESS_ATTACH:
        DisableThreadLibraryCalls(hInstDLL);
        CreateThread(NULL, NULL, (LPTHREAD_START_ROUTINE)SetupHook, NULL, NULL, NULL);
        Sleep(20);
    case DLL_PROCESS_DETACH:
        if (NULL != g_origNtQueryInformationProcess)
        `{`
            Mhook_Unhook((PVOID*)&amp;g_origNtQueryInformationProcess);
        `}`
        break;
    `}`
    return TRUE;
`}`
```

### <a class="reference-link" name="%E5%9F%BA%E4%BA%8ENtQueryInformationProcess%E7%9A%84%E5%85%B6%E4%BB%96%E5%8F%8D%E8%B0%83%E8%AF%95%E6%8A%80%E6%9C%AF"></a>基于NtQueryInformationProcess的其他反调试技术

有些反调试技术还用到了`NtQueryInformationProcess`提供的信息，包括如下技术：
<li>
`ProcessDebugPort 0x07` – 前面已讨论过</li>
- `ProcessDebugObjectHandle 0x1E`
- `ProcessDebugFlags 0x1F`
- `ProcessBasicInformation 0x00`
接下来我们详细讨论下后3种技术。

**ProcessDebugObjectHandle**

从Windows XP开始，系统会为被调试进程创建一个“调试对象”。检查当前进程是否存在“调试对象”的代码如下所示：

```
status = NtQueryInformationProcess(
            GetCurrentProcess(),
            ProcessDebugObjectHandle,
            &amp;hProcessDebugObject,
            sizeof(HANDLE),
            NULL);
if (0x00000000 == status &amp;&amp; NULL != hProcessDebugObject)
`{`
    std::cout &lt;&lt; "Stop debugging program!" &lt;&lt; std::endl;
    exit(-1);
`}`
```

如果调试对象存在，那么当前进程正在被调试。

**ProcessDebugFlags**

检查该标志时，会返回`EPROCESS`内核结构中`NoDebugInherit`位的取反值。如果`NtQueryInformationProcess`函数的返回值为0，那么该进程正在被调试。使用这种原理的反调试代码如下所示：

```
status = NtQueryInformationProcess(
    GetCurrentProcess(),
    ProcessDebugObjectHandle,
    &amp;debugFlags,
    sizeof(ULONG),
    NULL);
if (0x00000000 == status &amp;&amp; NULL != debugFlags)
`{`
    std::cout &lt;&lt; "Stop debugging program!" &lt;&lt; std::endl;
    exit(-1);
`}`
```

**ProcessBasicInformation**

当使用`ProcessBasicInformation`标志来调用`NtQueryInformationProcess`函数时，就会返回`PROCESS_BASIC_INFORMATION`结构体：

```
typedef struct _PROCESS_BASIC_INFORMATION `{`
    NTSTATUS ExitStatus;
    PVOID PebBaseAddress;
    ULONG_PTR AffinityMask;
    KPRIORITY BasePriority;
    HANDLE UniqueProcessId;
    HANDLE InheritedFromUniqueProcessId;
`}` PROCESS_BASIC_INFORMATION, *PPROCESS_BASIC_INFORMATION;
```

这个结构体中最有意思的就是`InheritedFromUniqueProcessId`字段。这里我们需要获取父进程的名称，然后将其与常用的调试器进行对比。使用这种方法的反调试技术代码如下所示：

```
std::wstring GetProcessNameById(DWORD pid)
`{`
    HANDLE hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hProcessSnap == INVALID_HANDLE_VALUE)
    `{`
        return 0;
    `}`
    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);
    std::wstring processName = L"";
    if (!Process32First(hProcessSnap, &amp;pe32))
    `{`
        CloseHandle(hProcessSnap);
        return processName;
    `}`
    do
    `{`
        if (pe32.th32ProcessID == pid)
        `{`
            processName = pe32.szExeFile;
            break;
        `}`
    `}` while (Process32Next(hProcessSnap, &amp;pe32));

    CloseHandle(hProcessSnap);
    return processName;
`}`
status = NtQueryInformationProcess(
    GetCurrentProcess(),
    ProcessBasicInformation,
    &amp;processBasicInformation,
    sizeof(PROCESS_BASIC_INFORMATION),
    NULL);
std::wstring parentProcessName = GetProcessNameById((DWORD)processBasicInformation.InheritedFromUniqueProcessId);
if (L"devenv.exe" == parentProcessName)
`{`
    std::cout &lt;&lt; "Stop debugging program!" &lt;&lt; std::endl;
    exit(-1);
`}`
```

**如何绕过**

绕过`NtQueryInformationProcess`检查的方法非常简单。我们需要修改`NtQueryInformationProcess`函数的返回值，修改成调试器不存在的值即可：

1、将`ProcessDebugObjectHandle`设置为0；

2、将`ProcessDebugFlags`设置为1；

3、对于`ProcessBasicInformation`，将`InheritedFromUniqueProcessId`的值修改为其他进程的ID，如`explorer.exe`。
