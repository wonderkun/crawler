
# 【技术分享】通过内核地址保护措施，回顾Windows安全加固技术


                                阅读量   
                                **107824**
                            
                        |
                        
                                                                                                                                    ![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：samdb.xyz
                                <br>原文地址：[https://samdb.xyz/revisiting-windows-security-hardening-through-kernel-address-protection/](https://samdb.xyz/revisiting-windows-security-hardening-through-kernel-address-protection/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85614/t0196df22e3a2374d37.jpg)](./img/85614/t0196df22e3a2374d37.jpg)

**翻译：shan66**

**预估稿费：200RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投**

 

**前言**

在2011年的时候，Windows 7 Service Pack 1如日中天，那时我才开始接触编程，而j00ru则发布了一个介绍在用户模式下通过各种方式访问Windows内核指针的白皮书：Windows Security Hardening Through Kernel Address Protection。

我决定重新回味一下这篇白皮书中讨论的各种技术，搜罗可用于Windows 7上的相应版本，然后调查它们能否在Windows 8 / 8.1 / 10上奏效。遇到无法在Windows 8 / 8.1 / 10上工作的时候，我会进一步研究相应的函数在新版本的Windows中发生了怎样的变化。这方面的工作，虽然很多都被别人做过了，但通过动手实践，我还是学到了很多东西；同时，作为一个有趣的逆向工程的练习，或许对大家也会有所帮助。

对于每个例子，我都会提供一个可用于Windows 7 32位的实现，然后将其移植到64位Windows，如果发现无法用于新版本的Windows 的话，则说明原来用到的某些特性在新版本操作系统中已经发生了变化。

 本文中讨论的每一种技术，在Github上都可以下载到相应的Visual Studio项目。

 

**Windows System Information classes**

**** NtQuerySystemInformation是一个经典的和众所周知的未公开函数，利用逆向工程的获得的各种细节，人们发现它可以用来收集关Windows内核的状态信息。 它在MSDN上的定义如下：

```
NTSTATUS WINAPI NtQuerySystemInformation(
  _In_      SYSTEM_INFORMATION_CLASS SystemInformationClass,
  _Inout_   PVOID                    SystemInformation,
  _In_      ULONG                    SystemInformationLength,
  _Out_opt_ PULONG                   ReturnLength
);
```

第一个参数是SYSTEM_INFORMATION_CLASS的值，这个值决定返回什么信息。 这些值可以在winternl.h中找到，其他的值也被人通过逆向工程找到了（例如在wine项目实现中就可以找到这些值）。 在j00ru的论文中，他考察了4个枚举值，我们将在后文中单独加以解释。

第二个参数是指向输出数据的结构的指针，它会随着SystemInformationClass值的不同而变化，第三个参数是其长度。 最后一个参数用于返回写入输出结构的数据量。

为了避免为各个SystemInformationClass值重复编码，我将在这里给出实际定义和调用NtQuerySystemInformation的代码。 首先，我们将包含标准的Visual Studio项目头文件，同时要完整导入Windows.h文件，因为它定义了我们需要用到的许多Windows特有的结构和函数。

```
#include "stdafx.h"
#include &lt;windows.h&gt;
```

我们还需要定义NyQuerySystemInformation函数，以便让一个指针指向它，从而便于调用。

```
typedef NTSTATUS(WINAPI *PNtQuerySystemInformation)(
    __in SYSTEM_INFORMATION_CLASS SystemInformationClass,
    __inout PVOID SystemInformation,
    __in ULONG SystemInformationLength,
    __out_opt PULONG ReturnLength
);
```

最后，我们还需要在ntdll中找到NtQuerySystemInformation函数，方法是获取一个ntdll的HANDLE，然后再其中寻找该函数的地址，然后快速检查它是否已成功找到。

```
HMODULE ntdll = GetModuleHandle(TEXT("ntdll"));
PNtQuerySystemInformation query = (PNtQuerySystemInformation)GetProcAddress(ntdll, "NtQuerySystemInformation");
if (query == NULL) {
    printf("GetProcAddress() failed.n");
    return 1;
}
```

上述代码一旦运行，我们就可以像调用函数一样来查询变量了。

**<br>**

**Windows 7 32 bit  SystemModuleInformation**

这里介绍的第一个SystemInformationClass值是SystemModuleInformation，当使用此值时，返回当前已经加载到内核空间的地址的所有驱动程序的相关数据，包括它们的名称和大小。

首先，我们需要定义枚举值SYSTEM_INFORMATION_CLASS，稍后我们将其传递给NtQuerySystemInformation，这里其值为11，如下所示。



```
typedef enum _SYSTEM_INFORMATION_CLASS {
    SystemModuleInformation = 11
} SYSTEM_INFORMATION_CLASS;
```

接下来，我们需要定义引用SystemModuleInformation时NtQuerySystemInformation会将信息加载到其中的结构。

```
#define MAXIMUM_FILENAME_LENGTH 255
 
typedef struct SYSTEM_MODULE {
    ULONG                Reserved1;
    ULONG                Reserved2;
    PVOID                ImageBaseAddress;
    ULONG                ImageSize;
    ULONG                Flags;
    WORD                 Id;
    WORD                 Rank;
    WORD                 w018;
    WORD                 NameOffset;
    BYTE                 Name[MAXIMUM_FILENAME_LENGTH];
}SYSTEM_MODULE, *PSYSTEM_MODULE;
 
typedef struct SYSTEM_MODULE_INFORMATION {
    ULONG                ModulesCount;
    SYSTEM_MODULE        Modules[1];
} SYSTEM_MODULE_INFORMATION, *PSYSTEM_MODULE_INFORMATION;
```

如您所见，SYSTEM_MODULE结构包括ImageBaseAddress、ImageSize和Name字段，这些正是我们感兴趣的东西。为了弄清楚我们需要分配多少内存，我们必须调用NtQuerySystemInformation SystemModuleInformation枚举值和一个NULL输出指针，这样的话，它就会加载所需的字节数到ReturnLength参数。

```
ULONG len = 0;
query(SystemModuleInformation, NULL, 0, &amp;len);
```

现在我们知道了需要多少内存，那么就可以分配一个适当大小的SYSTEM_MODULE_INFORMATION结构了，然后，再次调用NtQuerySystemInformation。

```
PSYSTEM_MODULE_INFORMATION pModuleInfo = (PSYSTEM_MODULE_INFORMATION)GlobalAlloc(GMEM_ZEROINIT, len);
if (pModuleInfo == NULL) {
    printf("Could not allocate memory for module info.n");
    return 1;
}
 
query(SystemModuleInformation, pModuleInfo, len, &amp;len);
if (len == 0) {
    printf("Failed to retrieve system module information.rn");
    return 1;
}
```

在检查一切都返回都没有任何错误后，我们就可以使用ModulesCount字段来遍历SYSTEM_MODULE数组，从而打印每个模块的关键细节信息了。

```
for (int i = 0; i &lt; pModuleInfo-&gt;ModulesCount; i++) {
    PVOID kernelImageBase = pModuleInfo-&gt;Modules[i].ImageBaseAddress;
    PCHAR kernelImage = (PCHAR)pModuleInfo-&gt;Modules[i].Name;
    printf("Module name %st", kernelImage);
    printf("Base Address 0x%Xrn", kernelImageBase);
}
```

构建并运行上述代码，我们将得到以下输出结果。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e0fd78bbb58a18b8.png)

这个例子的完整代码（包括后面讨论的在64位Windows上运行的版本）可以从Github上面下载。 

 

**SystemHandleInformation**

在j00ru的论文中提到的第二个SystemInformationClass值是SystemHandleInformation，它给出了内核内存中所有进程的每个对象的HANDLE和指针，其中包括所有Token对象。在这里，我们将使用SystemHandleInformation的扩展版本，因为原始版本只给出16位的HANDLE值，这在某些情况下可能是不够的。 首先，我们需要再次定义正确的SYSTEM_INFORMATION_CLASS值。

```
typedef enum _SYSTEM_INFORMATION_CLASS {
    SystemExtendedHandleInformation = 64
} SYSTEM_INFORMATION_CLASS;
```

接下来，我们需要定义输出结构（取自Process Hacker，从第1595行开始）。

```
typedef struct _SYSTEM_HANDLE
{
    PVOID Object;
    HANDLE UniqueProcessId;
    HANDLE HandleValue;
    ULONG GrantedAccess;
    USHORT CreatorBackTraceIndex;
    USHORT ObjectTypeIndex;
    ULONG HandleAttributes;
    ULONG Reserved;
} SYSTEM_HANDLE, *PSYSTEM_HANDLE;
 
typedef struct _SYSTEM_HANDLE_INFORMATION_EX
{
    ULONG_PTR HandleCount;
    ULONG_PTR Reserved;
    SYSTEM_HANDLE Handles[1];
} SYSTEM_HANDLE_INFORMATION_EX, *PSYSTEM_HANDLE_INFORMATION_EX;
```

正如您看到的，输出结构包含每个对象的HandleValue和Object字段，它是一个指向对象在内存中的位置的指针。

```
typedef struct _SYSTEM_HANDLE
{
    PVOID Object;
    HANDLE UniqueProcessId;
    HANDLE HandleValue;
    ULONG GrantedAccess;
    USHORT CreatorBackTraceIndex;
    USHORT ObjectTypeIndex;
    ULONG HandleAttributes;
    ULONG Reserved;
} SYSTEM_HANDLE, *PSYSTEM_HANDLE;
 
typedef struct _SYSTEM_HANDLE_INFORMATION_EX
{
    ULONG_PTR HandleCount;
    ULONG_PTR Reserved;
    SYSTEM_HANDLE Handles[1];
} SYSTEM_HANDLE_INFORMATION_EX, *PSYSTEM_HANDLE_INFORMATION_EX;
```

为了使用这个SystemInformationClass值，NtQuerySystemInformation提供了一个奇怪的API，当使用NULL指针调用它时，它不是返回所需的内存，而只是返回NTSTATUS代码0xC0000004。 这是STATUS_INFO_LENGTH_MISMATCH的代码，当为待写入的输出分配的内存不足时，就会返回该代码。为了处理这个问题，我为输出分配了很少的内存，然后不断调用NtQuerySystemInformation，每次将内存量加倍，直到它返回一个不同的状态代码为止。

```
ULONG len = 20;
NTSTATUS status = (NTSTATUS)0xc0000004;
PSYSTEM_HANDLE_INFORMATION_EX pHandleInfo = NULL;
do {
    len *= 2;
    pHandleInfo = (PSYSTEM_HANDLE_INFORMATION_EX)GlobalAlloc(GMEM_ZEROINIT, len);
 
    status = query(SystemExtendedHandleInformation, pHandleInfo, len, &amp;len);
 
} while (status == (NTSTATUS) 0xc0000004);
```

一旦分配了足够的内存，该函数就会成功返回，然后我们就可以像前面介绍的那样来遍历输出，并打印我们感兴趣的值了。

```
for (int i = 0; i &lt; pHandleInfo-&gt;HandleCount; i++) {
    PVOID object = pHandleInfo-&gt;Handles[i].Object;
    HANDLE handle = pHandleInfo-&gt;Handles[i].HandleValue;
    HANDLE pid = pHandleInfo-&gt;Handles[i].UniqueProcessId;
    printf("PID: %dt", pid);
    printf("Object 0x%Xt", object);
    printf("Handle 0x%Xrn", handle);
}
```

构建并运行上述代码，我们将得到以下输出结果。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e4fadea7bbf69058.png)

这个例子的完整代码（包括后面在64位Windows上运行的相应版本）可以从Github上面下载。 

**<br>**

**SystemLockInformation**

在j00ru的论文中考察的第三个SystemInformationClass值是SystemLockInformation，它返回当前存在于内核内存中的每个Lock对象的详细信息和地址。 同样的，我们首先要定义正确的SYSTEM_INFORMATION_CLASS值。



```
typedef enum _SYSTEM_INFORMATION_CLASS {
    SystemLockInformation = 12
} SYSTEM_INFORMATION_CLASS;
```

接下来，我们需要定义输出结构，为此，我引用了j00ru的文件中的结构定义，并假设提供LocksCount信息的容器结构也采用其他结构的模式。

```
typedef struct _SYSTEM_LOCK {
    PVOID   Address;
    USHORT  Type;
    USHORT  Reserved1;
    ULONG   ExclusiveOwnerThreadId;
    ULONG   ActiveCount;
    ULONG   ContentionCount;
    ULONG   Reserved2[2];
    ULONG   NumberOfSharedWaiters;
    ULONG   NumberOfExclusiveWaiters;
} SYSTEM_LOCK, *PSYSTEM_LOCK;
 
typedef struct SYSTEM_LOCK_INFORMATION {
    ULONG              LocksCount;
    SYSTEM_LOCK        Locks[1];
} SYSTEM_LOCK_INFORMATION, *PSYSTEM_LOCK_INFORMATION;
```

在SYSTEM_LOCK结构中，需要注意的关键值是Address字段，它是指向内核内存中的对象的指针。

就像SystemExtendedHandleInformation的用法那样，无法直接让NtQuerySystemInformation提供我们所需的输出缓冲区大小，我们需要在一个循环中调用它，直至给出长度不匹配错误代码为止。

```
PSYSTEM_LOCK_INFORMATION pLockInfo = NULL;
ULONG len = 20;
NTSTATUS status = (NTSTATUS)0xc0000004;
 
do {
    len *= 2;
    pLockInfo = (PSYSTEM_LOCK_INFORMATION)GlobalAlloc(GMEM_ZEROINIT, len);
    status = query(SystemLockInformation, pLockInfo, len, &amp;len);
} while (status == (NTSTATUS)0xc0000004);
```

一旦分配了足够的内存，该函数就会成功返回，然后我们就可以像前面介绍的那样来遍历输出，并打印我们感兴趣的值了。

```
for (int i = 0; i &lt; pLockInfo-&gt;LocksCount; i++) {
    PVOID lockAddress = pLockInfo-&gt;Locks[i].Address;
    USHORT lockType = (USHORT)pLockInfo-&gt;Locks[i].Type;
    printf("Lock Address 0x%Xt", lockAddress);
    printf("Lock Type 0x%Xrn", lockType);
}
```

它可以在32位Windows 7 上成功运行：

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0137a7341c5889798f.png)

完整代码，包括64位Windows的相应版本，可以从Github下载。 

**<br>**

**SystemExtendedProcessInformation**

在j00ru的论文中提到的最后一个SystemInformationClass值是SystemExtendedProcessInformation，它返回在系统中运行的所有进程和线程的详细信息，包括每个线程用户和内核模式堆栈的地址。 首先，我们需要定义正确的SYSTEM_INFORMATION_CLASS值。

```
typedef enum _SYSTEM_INFORMATION_CLASS {
    SystemSessionProcessInformation = 57
} SYSTEM_INFORMATION_CLASS;
```

接下来，我们需要定义所有的输出结构，这些结构取自伯克利的BOINC项目。借助于逆向工程，人们已经对该结构有了全面的了解，所以我们不妨使用完整的结构定义。 



```
typedef LONG       KPRIORITY;
typedef struct _CLIENT_ID {
    DWORD          UniqueProcess;
    DWORD          UniqueThread;
} CLIENT_ID;
 
typedef struct _UNICODE_STRING {
    USHORT         Length;
    USHORT         MaximumLength;
    PWSTR          Buffer;
} UNICODE_STRING;
 
typedef struct _VM_COUNTERS {
    SIZE_T         PeakVirtualSize;
    SIZE_T         VirtualSize;
    ULONG          PageFaultCount;
    SIZE_T         PeakWorkingSetSize;
    SIZE_T         WorkingSetSize;
    SIZE_T         QuotaPeakPagedPoolUsage;
    SIZE_T         QuotaPagedPoolUsage;
    SIZE_T         QuotaPeakNonPagedPoolUsage;
    SIZE_T         QuotaNonPagedPoolUsage;
    SIZE_T         PagefileUsage;
    SIZE_T         PeakPagefileUsage;
} VM_COUNTERS;
 
typedef enum _KWAIT_REASON
{
    Executive = 0,
    FreePage = 1,
    PageIn = 2,
    PoolAllocation = 3,
//SNIP
    WrRundown = 36,
    MaximumWaitReason = 37
} KWAIT_REASON;
 
typedef struct _SYSTEM_THREAD_INFORMATION{
    LARGE_INTEGER KernelTime;
    LARGE_INTEGER UserTime;
    LARGE_INTEGER CreateTime;
    ULONG WaitTime;
    PVOID StartAddress;
    CLIENT_ID ClientId;
    KPRIORITY Priority;
    LONG BasePriority;
    ULONG ContextSwitches;
    ULONG ThreadState;
    KWAIT_REASON WaitReason;
} SYSTEM_THREAD_INFORMATION, *PSYSTEM_THREAD_INFORMATION;
 
typedef struct _SYSTEM_EXTENDED_THREAD_INFORMATION
{
    SYSTEM_THREAD_INFORMATION ThreadInfo;
    PVOID StackBase;
    PVOID StackLimit;
    PVOID Win32StartAddress;
    PVOID TebAddress;
    ULONG Reserved1;
    ULONG Reserved2;
    ULONG Reserved3;
} SYSTEM_EXTENDED_THREAD_INFORMATION, *
PSYSTEM_EXTENDED_THREAD_INFORMATION;
 
typedef struct _SYSTEM_EXTENDED_PROCESS_INFORMATION
{
    ULONG NextEntryOffset;
    ULONG NumberOfThreads;
    LARGE_INTEGER SpareLi1;
    LARGE_INTEGER SpareLi2;
    LARGE_INTEGER SpareLi3;
    LARGE_INTEGER CreateTime;
    LARGE_INTEGER UserTime;
    LARGE_INTEGER KernelTime;
    UNICODE_STRING ImageName;
    KPRIORITY BasePriority;
    ULONG UniqueProcessId;
    ULONG InheritedFromUniqueProcessId;
    ULONG HandleCount;
    ULONG SessionId;
    PVOID PageDirectoryBase;
    VM_COUNTERS VirtualMemoryCounters;
    SIZE_T PrivatePageCount;
    IO_COUNTERS IoCounters;
    SYSTEM_EXTENDED_THREAD_INFORMATION Threads[1];
} SYSTEM_EXTENDED_PROCESS_INFORMATION, *PSYSTEM_EXTENDED_PROCESS_INFORMATION;
```

在这些结构中，我们感兴趣的关键值是StackBase和StackLimit字段，它们提供了线程内核模式堆栈的起始地址及其边界。

再次重申，NtQuerySystemInformation不会告诉我们需要分配多少内存，所以我们需要利用循环来调用它。



```
ULONG len = 20;
NTSTATUS status = NULL;
PSYSTEM_EXTENDED_PROCESS_INFORMATION pProcessInfo = NULL;
do {
    len *= 2;  
    pProcessInfo = (PSYSTEM_EXTENDED_PROCESS_INFORMATION)GlobalAlloc(GMEM_ZEROINIT, len);
    status = query(SystemSessionProcessInformation, pProcessInfo, len, &amp;len);
} while (status == (NTSTATUS)0xc0000004);
```

一旦函数成功调用，我们就可以为系统上运行的每个线程打印出相应的StackBase和StackLimit值了。为此，我们需要遍历所有的ProcessInfo结构，然后遍历其中的每个线程，并打印我们感兴趣的值。

```
while (pProcessInfo-&gt;NextEntryOffset != NULL) {
    for (unsigned int i = 0; i &lt; pProcessInfo-&gt;NumberOfThreads; i++) {
        PVOID stackBase = pProcessInfo-&gt;Threads[i].StackBase;
        PVOID stackLimit = pProcessInfo-&gt;Threads[i].StackLimit;
        printf("Stack base 0x%Xt", stackBase);
        printf("Stack limit 0x%Xrn", stackLimit);
    }
    pProcessInfo = (PSYSTEM_EXTENDED_PROCESS_INFORMATION)((ULONG_PTR)pProcessInfo + pProcessInfo-&gt;NextEntryOffset);
}
```

下面是它在32位Windows 7上面的运行结果：

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013a306d6eb5e040e3.png)

这个示例的完整代码（包括用于64位系统的相应版本）可以在Github上找到。 

**<br>**

**Windows 8 64 bit**

所有这些代码，要想用于64位Windows 8上，都需要稍作修改。当然，具体需要做出怎样的修改，则需要借助于调试代码本身来完成。

**<br>**

**SystemModuleInformation**

只有两处需要稍作修改，首先位于system_module结构之后的ImageBaseAddress指针是32位的，所以需要加入一个填充变量，至于填充的额外32位所包含的内容则是无所谓的。

```
typedef struct SYSTEM_MODULE {
    ULONG           Reserved1;
    ULONG           Reserved2;
#ifdef _WIN64
    ULONG       Reserved3;
#endif
    PVOID           ImageBaseAddress;
```

此外，一旦NtQuerySystemInformation被调用，用于打印基地址的printf语句需要进行相应的更新，以便打印64位指针。

```
printf("Base Addr 0x%llxrn", kernelImageBase);
```

编译之后，就可以成功运行在64位Windows 8上面了：

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01152ab4826e6b0022.png)

此外，编译后的代码也可以从Github上下载。 

**<br>**

**SystemHandleInformation**

对于SystemHandleInformation来说，只需要改动print语句，其他一切正常。

```
#ifdef _WIN64
    printf("Object 0x%llxt", object);
#else
    printf("Object 0x%Xt", object);
#endif
```

在64位Windows 8上的运行结果：

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d49dd5d8c51c0c8b.png)

最终的代码也可以从Github上下载。 

**<br>**

**SystemLockInformation**

为了让SystemLockInformation可用于64位Windows，必须添加另一个填充变量，当我测试时，这个变量里面好像没有任何东西，不过，也可能还有其他用途，只是我没有注意到罢了。字段大小不会相加，因为还要考虑对齐问题。

```
ULONG   Reserved2[2];
#ifdef _WIN64
    ULONG   Reserved3;
#endif
```

此外，还必须修修改打印锁地址的printf语句，使其支持64位地址。 

```
#ifdef _WIN64
    printf("Lock Address 0x%llxt", lockAddress);
#else
    printf("Lock Address 0x%Xt", lockAddress);
#endif
```

之后，它就可以在64位Windows 8上面正常使用了：



[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016397c8631299af30.png)

最终的代码也可以从Github上下载。 

**<br>**

**SystemExtendedProcessInformation**

SystemExtendedProcessInformation所需的改动也很少，只要在SYSTEM_THREAD_INFORMATION结构中填充128位即可——它肯定是有用处的，但具体我还不太清楚。

```
#ifdef _WIN64
    ULONG Reserved[4];
#endif
}SYSTEM_THREAD_INFORMATION, *PSYSTEM_THREAD_INFORMATION;
```

另外，处理地址的printf语句需要像前面介绍的那样进行相应的更新。



```
#ifdef _WIN64
    printf("Stack base 0x%llxt", stackBase);
    printf("Stack limit 0x%llxrn", stackLimit);
#else
    printf("Stack base 0x%Xt", stackBase);
    printf("Stack limit 0x%Xrn", stackLimit);
#endif
```

完成上述修改之后，代码就可以在64位Windows 8上面正常运行了：

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010813f5455f059ad6.png)

最终的代码也可以从Github上下载。 

**<br>**

**Windows 8.1 64 bit onward**

至于在Windows 8.1上修改这些代码方面，我还是多少有点优势的：毕竟我早就阅读过Alex Ionescu的一篇文章，因此我知道可通过一种稍微不同的方式来运行二进制代码。 在Windows Vista中引入了完整性级别的概念，这将导致所有进程在下面所示的六个完整性级别之一上面运行。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011b6eeda36eb29600.png)

完整性级别较高的进程可以访问更多的系统资源，例如沙盒进程通常是在较低的完整性级别上面运行，并且对系统其余部分的访问权限是最小的。 更多的细节可以在上面链接的MSDN页面上找到。

我创建了一个完整性水平较低的cmd.exe副本，具体方法请参见这里。当我试图在这个命令提示符下面运行NtQuerySystemInformation的二进制代码时，就会得到错误代码0xC0000022：

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0195738dc8515f0776.png)

STATUS_ACCESS_DENIED的这个NTSTATUS代码定义如下：

进程已请求访问对象，但尚未授予这些访问权限。

但是，如果在中等完整性级别的命令提示符下运行该二进制代码话，则一切正常： 

这意味着必须向函数添加完整性级别检查。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01694ea340adde888b.png)

您可以使用SysInternals中的procexp查看完整性级别进程（见最后一列）：

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018c166ad5cb628098.png)

这时我开始研究，为了添加了该项检查，NtQuerySystemInformation在Windows 8和8.1之间发生了哪些变化。利用IDA考察NtQuerySystemInformation函数后，我发现它依赖于调用“ExpQueryInformationProcess”函数。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015f1181d53b19aed4.png)

通过Diaphora检查这两个版本的ntoskrnl.exe的差异，我发现这个函数在两个操作系统版本之间发生了重大变化。 

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014bcfaaa25809e120.png)

通过比较两个实现汇编代码的不同之处，很容易就可以看出，这里添加了一个对“ExIsRestrictedCaller”的调用，通过交叉引用可以获悉，它主要是从ExpQuerySystemInformation中调用的，并且在相关函数中也被调用了几次。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0177b9b79d9cb6d123.png)

我还看了一下函数本身，我注释的汇编代码见下文。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01be516d71c25bfba4.png)

**根据我的理解，该函数的工作机制为：**

1、检查在ecx中传递给它的未知值是否为0，如果是的话就返回0

2、使用PsReferencePrimaryToken增加调用进程令牌的引用计数

3、使用SeQueryInformationToken将调用进程令牌的TokenIntegrityLevel读入一个局部变量

4、使用ObDereferenceObject减少调用进程令牌的引用计数

5、检查SeQueryInformationToken是否返回错误代码，如果是就返回1

6、如果SeQueryInformationToken成功，将读取令牌完整性级别，并与0x2000（这个值表示中等完整性级别）进行比较

7、如果令牌完整性级别低于0x2000则返回1，否则返回0

Alex Ionescu在他的博客上提供了这个函数的逆向版本。 每次该函数被调用时，它就返回1，然后调用函数将返回前面提到的错误代码。

<br>

**Win32k.sys系统调用信息泄露  ****Windows 7 32 bit**

这个问题最初是由j00ru在发布白皮书几个月前发现的，并在原始博客文章中有更深入的讨论。

问题是，win32k.sys中的一些系统调用的返回值是小于32位的，例如VOID或USHORT，所以，在返回之前没有清除eax寄存器。 由于各种原因，在调用返回之前，内核地址在eax中结束，因此在调用之后立即读取eax，这些地址就会被完全暴露或部分暴露。

例如NtUserModifyUserStartupInfoFlags就完全暴露了ETHREAD结构的地址，下面你可以看到，在该函数返回之前调用了UserSessionSwitchLeaveCrit，这似乎向eax中加载了一个指向ETHREAD的指针，但是，由于函数返回之前没有清空寄存器的内容，导致这个地址完整保留了下来。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01845d258b5a9bb93d.png)

要想使用这些系统调用来泄漏地址，我们首先需要添加标准include和Winddi，因为它们定义了将要调用的函数使用的一些GDI（图形设备接口）的结构。

```
#include "stdafx.h"
#include &lt;Windows.h&gt;
#include &lt;Winddi.h&gt;
```

我决定，通过使用其用户空间包装器（在这种情况下是user32.dll和gdi32.dll）来调用这些系统调用，因此我需要获取DLL中的函数的偏移量。为此，我把该dll拖拽到IDA中，将反汇编重定位到0，然后过滤函数列表以寻找目标函数。这样，找到的函数的起始地址是我需要的dll的偏移量。

我选择了一个完全泄漏ETHREAD的函数，以及一个部分泄漏它的函数。类似的方法同样适用于W32THREAD。

```
//0x64D4B - NtUserModifyUserStartupInfoFlags
typedef DWORD(NTAPI * lNtUserModifyUserStartupInfoFlags)(DWORD Set, DWORD Flags);
//0xA2F4 - NtUserGetAsyncKeyState
typedef DWORD(NTAPI *lNtUserGetAsyncKeyState)(DWORD key);
 
//0x47123 - NtGdiFONTOBJ_vGetInfo
typedef VOID(NTAPI * lNtGdiFONTOBJ_vGetInfo)(FONTOBJ *pfo,ULONG cjSize,FONTINFO *pfi);
//0x47263 - NtGdiPATHOBJ_vEnumStartClipLines
typedef VOID(NTAPI * lNtGdiPATHOBJ_vEnumStartClipLines)(PATHOBJ *ppo, CLIPOBJ *pco, SURFOBJ *pso, LINEATTRS *pla);
```

为了调用这些函数，我们首先需要一个处理它们所在的DLL的句柄，所以，我们首先设法得到user32.dll的句柄。

```
HMODULE hUser32 = LoadLibraryA("user32.dll");
if (hUser32 == NULL) {
    printf("Failed to load user32");
    return 1;
}
```

如果上述代码成功运行，我们就可以把第一个函数的偏移量与HMODULE的值相加，从而获得函数入口点，然后就可以将其转换为正确的类型了。

```
lNtUserGetAsyncKeyState pNtUserGetAsyncKeyState = (lNtUserGetAsyncKeyState)((DWORD_PTR)hUser32 + 0xA2F4);
```

然后，我们调用该函数并使用内联汇编来获取在eax中留下的值，并打印出来。

```
pNtUserGetAsyncKeyState(20);
unsigned int ethread = 0;
__asm {
    mov ethread, eax;
}
printf("NtUserGetAsyncKeyState ETHREAD partial disclosure: 0x%Xrn", ethread);
```



然后，我们对NtUserModifyUserStartupInfoFlags进行同样的处理。

```
lNtUserModifyUserStartupInfoFlags pNtUserModifyUserStartupInfoFlags = (lNtUserModifyUserStartupInfoFlags)((DWORD_PTR)hUser32 + 0x64D4B);
 
pNtUserModifyUserStartupInfoFlags(20, 12);
unsigned ethread_full = 0;
__asm {
    mov ethread_full, eax;
}
printf("NtUserModifyUserStartupInfoFlags ETHREAD full disclosure: 0x%Xrn", ethread_full);
```

接下来，我们需要调用暴露W32THREAD指针的函数，它们都是在gdi32.dll中定义的，所以我们需要得到该DLL的句柄，然后就可以像前面那样来调用这些函数了。



```
HMODULE hGDI32 = LoadLibraryA("gdi32.dll");
if (hGDI32 == NULL) {
    printf("Failed to load gdi32");
    return 1;
}
 
lNtGdiFONTOBJ_vGetInfo pNtGdiFONTOBJ_vGetInfo = (lNtGdiFONTOBJ_vGetInfo)((DWORD_PTR)hGDI32 + NtGdiFONTOBJ_vGetInfoAddress);
FONTOBJ surf = { 0 };
FONTINFO finfo = { 0 };
pNtGdiFONTOBJ_vGetInfo(&amp;surf, 123, &amp;finfo);
 
long int w32thread = 0;
__asm {
    mov w32thread, eax;
}
 
printf("NtGdiEngUnLockSurface W32THREAD full disclosure: 0x%Xrn", w32thread);
 
lNtGdiPATHOBJ_vEnumStartClipLines pNtGdiPATHOBJ_vEnumStartClipLines = (lNtGdiPATHOBJ_vEnumStartClipLines)((DWORD_PTR)hGDI32 + 0x47263);
PATHOBJ pathobj = { 0 };
CLIPOBJ pco = { 0 };
SURFOBJ pso = { 0 };
LINEATTRS pla = { 0 };
pNtGdiPATHOBJ_vEnumStartClipLines(&amp;pathobj, &amp;pco, &amp;pso, &amp;pla);
w32thread = 0;
__asm {
    mov w32thread, eax;
}
printf("NtGdiPATHOBJ_vEnumStartClipLines W32THREAD full disclosure: 0x%Xrn", w32thread);
```

编译并运行代码，我们就可以看到被暴露的地址了。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01112f1daefde8e324.png)

 <br>

**Windows 8 64 bit onward**

要使代码在Windows 8上运行，必须首先更新函数偏移量来匹配新的主机VM的二进制代码。 请注意，这里缺少NtGdiFONTOBJ_vGetInfo函数的地址，因为该函数在Windows 8 VM的gdi32版本中没有相应的定义。

```
//win8, 64bit
#define NtUserModifyUserStartupInfoFlagsAddress 0x263F0
#define NtUserGetAsyncKeyStateAddress 0x3B30
#define NtGdiPATHOBJ_vEnumStartClipLinesAddress 0x67590
```

第二个问题是，Visual Studio不支持针对amd64代码的内联汇编，所以我添加了一个名为“asm_funcs.asm”的简短文件，具体内容如下所示：

```
_DATA SEGMENT
_DATA ENDS
_TEXT SEGMENT
 
PUBLIC get_rax
 
get_rax PROC
ret
get_rax ENDP
_TEXT ENDS
END
```

所有这些实际上就是定义了一个名为“get_rax”的函数，虽然它什么都不做，但却会返回，并且根据调用约定，返回值将保存在rax中。

此外，我们还必须对Visual Studio项目的配置稍作修改，以使其编译所包含的汇编代码，为此，可以在solution explorer中右键单击项目，转到“Build Dependencies” – &gt;“Build Customizations..”，然后在对话窗口中勾选'masm'选项。 Elias Bachaalany提供了更为详细的介绍，请访问这里。

然后，通过将这个函数声明为一个外部函数，将该函数导入到主文件中。

```
extern "C" unsigned long long get_rax();
```

最后，将相应的变量的长度改为64位，同时所有的printf语句也要进行相应的修改。

最终的代码可以从Github上下载。

忙活半天，终于可以在64位系统上运行我们的代码了，并且这个问题在Windows 8中也得到了修复！ 

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01cfcc99f3b16f4ced.png)

Matt Miller在Black Hat USA 2012上的演讲的内核部分中讨论Windows 8漏洞利用缓解改进情况的时候，曾经引用了这个修复： 

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0102e3befb3b91ad62.png)

解决这些问题的方法非常简单，观察一下的从Windows 7和Windows 8中的win32.sys（如下图所示），我们可以看到，现在这些函数的实现方式中，调用敏感函数后所有的RAX被设置为一个新值。例如，在我考察过的两个泄露ETHREAD的函数中，UserSessionSwitchLeaveCrit导致返回前将泄露的地址放入RAX/ EAX中，这个问题已得到修复。

NtUserGetAsyncKeyState：Windows 8的实现在左边，Windows 7的实现在右边。 以前，这会导致泄漏ETHREAD的部分地址，因为在函数返回之前，只有eax的前16位被修改，现在使用movsx后，它将对较高的位进行清零。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0104a6c0eeef692a01.png)

NtUserModifyUserStartupInfoFlags：Windows 8的实现在左边，Windows 7的实现在右边。 以前，这会泄漏完整的ETHREAD地址，因为eax在返回之前根本没有被修改，现在eax被显式地设置为1。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010491f3e8d2e83d8c.png)

**<br>**

**描述符表  Windows 7 32 bit**

x86描述符表有各种用途，在j00ru的论文中考察的是中断描述符表（IDT），处理器用它查找处理中断和异常的代码，而全局描述符表（GDT） 由处理器使用以定义内存段。

关于描述符表的更多细节请参考j00ru的论文，它们主要在内存隔离和特权隔离中扮演关键角色。全局描述符表寄存器（GDTR）定义了GDT的起始地址及其大小，它可以通过sgdt x86指令读取：

SGDT仅对操作系统软件有用; 但是，它可以在应用程序中使用，并且不会生成异常。

这意味着在Ring 3中运行的代码可以读取GDTR的值且不会引起异常，但无法对它进行写入操作。 GDTR的格式如下：

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a9f2121aaab2a21f.png)

中断描述符表寄存器（IDTR）定义了IDT的起始地址及其大小，它可以使用sidt x86指令读取，并且与sgdt类似，也可以从ring 3调用，这一点真是带来了极大的便利性。IDTR的格式如下所示：

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0121cc6be9e6674ce8.png)

此外，Windows允许使用GetThreadSelectorEntry函数读取GDT中的特定表项。 在j00ru的论文中，他使用它来读取几个潜在的敏感表项，但是我将通过它来读取任务状态段（TSS）描述符。

我们可以使用内联汇编以6字节缓冲区作为参数来执行sidt指令。

```
unsigned char idtr[6] = { 0 };
__asm {
    sidt idtr;
}
```

读取idtr后，我们只需要从内存中提取相应的值，就可以打印它们了。

```
unsigned int idtrBase = (unsigned int)idtr[5] &lt;&lt; 24 |
        (unsigned int)idtr[4] &lt;&lt; 16 |
        (unsigned int)idtr[3] &lt;&lt; 8 |
        (unsigned int)idtr[2];
unsigned short idtrLimit = (unsigned int)idtr[1] &lt;&lt; 8 |
        (unsigned int)idtr[0];
printf("Interrupt Descriptor Table Register base: 0x%X, limit: 0x%Xrn", idtrBase, idtrLimit);
```

同样，我们可以很容易地使用内联汇编来调用sgdt指令，然后提取基地址和极限值。

```
unsigned char gdtr[6] = { 0 };
__asm {
    sgdt gdtr;
}
unsigned int gdtrBase = (unsigned int)gdtr[5] &lt;&lt; 24 |
        (unsigned int)gdtr[4] &lt;&lt; 16 |
        (unsigned int)gdtr[3] &lt;&lt; 8 |
        (unsigned int)gdtr[2];
unsigned short gdtrLimit = (unsigned int)gdtr[1] &lt;&lt; 8 |
        (unsigned int)gdtr[0];
printf("Global Descriptor Table Register base: 0x%X, limit: 0x%Xrn", gdtrBase, gdtrLimit);
```

接下来，我们要使用GetThreadSelectorEntry来读取TSS内容。

```
BOOL WINAPI GetThreadSelectorEntry(
  _In_  HANDLE      hThread,
  _In_  DWORD       dwSelector,
  _Out_ LPLDT_ENTRY lpSelectorEntry
);
```

首先，我们使用Store Task Register / str指令为tss获取正确的段选择符。

```
WORD tr;
 
__asm str tr
```

接下来，我们创建一个空的LDT_ENTRY表项结构，并使用当前线程作为线程参数调用GetThreadSelectorEntry函数。 

```
LDT_ENTRY tss;
GetThreadSelectorEntry(GetCurrentThread(), tr, &amp;tss);
```

然后，我们就可以从下面已填充的LDT_ENTRY结构中读取TSS的基址和限制了。

```
unsigned int  tssBase = (tss.HighWord.Bits.BaseHi &lt;&lt; 24) +
    (tss.HighWord.Bits.BaseMid &lt;&lt; 16) +
    tss.BaseLow;
unsigned int tssLimit = tss.LimitLow;
printf("TSS base: 0x%X, limit: 0x%Xrn", tssBase, tssLimit);
```

完成所有这些工作后，我们就可以编译并运行代码来查看地址了：

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f9933c7f45ad43f4.png)

包括用于64位Windows的完整代码都可以从Github下载。

**<br>**

**Windows 8 64 bit**

我们的代码只要稍作修改，就可以在64位Windows上正常使用。最重要的是，Visual Studio无法在面向amd64的项目中使用内联汇编。对于sidt/sgdt来说，我们可以通过Visual Studio定义Compiler Intrinsic来解决这个问题。我们可以通过下列代码来读取GDTR。



```
unsigned char gdtr[10] = { 0 };
_sgdt(gdtr);
unsigned long long gdtrBase = (unsigned long long)gdtr[9] &lt;&lt; 56 |
    (unsigned long long)gdtr[8] &lt;&lt; 48 |
    (unsigned long long)gdtr[7] &lt;&lt; 40 |
    (unsigned long long)gdtr[6] &lt;&lt; 32 |
    (unsigned long long)gdtr[5] &lt;&lt; 24 |
    (unsigned long long)gdtr[4] &lt;&lt; 16 |
    (unsigned long long)gdtr[3] &lt;&lt; 8 |
    (unsigned long long)gdtr[2];
unsigned short gdtrLimit = (unsigned int)gdtr[1] &lt;&lt; 8 |
    (unsigned int)gdtr[0];
printf("Global Descriptor Table Register base: 0x%llx, limit: 0x%Xrn", gdtrBase, gdtrLimit);
```

_sgdt的作用与使用内联汇编调用sgdt完全相同。 gdtr的大小也必须进行更新以反映64位系统上的指针。读取IDTR的代码也需要进行类似的修改。 

```
unsigned char idtr[10] = { 0 };
__sidt(idtr);
unsigned long long idtrBase = (unsigned long long)idtr[9] &lt;&lt; 56 |
    (unsigned long long)idtr[8] &lt;&lt; 48 |
    (unsigned long long)idtr[7] &lt;&lt; 40 |
    (unsigned long long)idtr[6] &lt;&lt; 32 |
    (unsigned long long)idtr[5] &lt;&lt; 24 |
    (unsigned long long)idtr[4] &lt;&lt; 16 |
    (unsigned long long)idtr[3] &lt;&lt; 8 |
    (unsigned long long)idtr[2];
unsigned short idtrLimit = (unsigned int)idtr[1] &lt;&lt; 8 |
    (unsigned int)idtr[0];
printf("Interrupt Descriptor Table Register base: 0x%llx, limit: 0x%Xrn", idtrBase, idtrLimit);
```

 最后，需要包含头文件intrin.h，因为Compiler Intrinsics都是定义在这个文件中的。

```
#include &lt;intrin.h&gt;
```

GetThreadSelectorEntry似乎没有读取TSS的64位简单实现代码，因此将其弃用。

因为从Ring 3执行sidt/sgdt指令是amd64指令集的特性，而非操作系统特性，所以在Windows 8中仍然可以读取这些值： 

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01413f88e71429cdcc.png)

Windows 8.1:

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015c1960a59ef706c8.png)

Windows 10:

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010ebd33d7f7d342d5.png)

与进程所在的完整性级别或用户具有的权限无关。 

**<br>**

**Hyper-V**

根据Dave Weston和Matt Miller的Black Hat关于Windows 10的漏洞利用缓解进展方面的演讲来看，如果在系统上启用Hyper-V，并执行sidt或sgdt指令的话，管理程序将捕获它们并拦截返回值。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e87295d45592b709.png)

但是，这一点我还没有亲自验证过。 

**<br>**

**Win32k.sys Object Handle Addresses  Windows 7 32 bit**

Win32k是一个重要的驱动程序，提供将图形输出到Windows上的显示器、打印机等的相关功能。它维护会话（会话由表示单个用户的登录会话的所有进程和其他系统对象组成。）和存储所有GDI（图形设备接口）和用户句柄的句柄表。

为了降低访问此表的性能开销，通常将其映射到用户空间中的所有GUI进程。 用户空间中该表的地址可通过user32.dll导出为gSharedInfo。

这允许从用户模式寻找内核内存空间中所有GDI和用户对象的地址。 首先，我们需要定义这个表在内存中的结构，下面的结构取自ReactOS。

```
typedef struct _HANDLEENTRY {
    PVOID   phead;
    ULONG   pOwner;
    BYTE    bType;
    BYTE    bFlags;
    WORD    wUniq;
}HANDLEENTRY, *PHANDLEENTRY;
 
typedef struct _SERVERINFO {
    DWORD   dwSRVIFlags;
    DWORD   cHandleEntries;
    WORD    wSRVIFlags;
    WORD    wRIPPID;
    WORD    wRIPError;
}SERVERINFO, *PSERVERINFO;
 
typedef struct _SHAREDINFO {
    PSERVERINFO psi;
    PHANDLEENTRY    aheList;
    ULONG       HeEntrySize;
    ULONG_PTR   pDispInfo;
    ULONG_PTR   ulSharedDelta;
    ULONG_PTR   awmControl;
    ULONG_PTR   DefWindowMsgs;
    ULONG_PTR   DefWindowSpecMsgs;
}SHAREDINFO, *PSHAREDINFO;
```

接下来，我们需要获取user32 DLL的句柄，并找到gSharedInfo变量的偏移量。 

```
HMODULE hUser32 = LoadLibraryA("user32.dll");
PSHAREDINFO gSharedInfo = (PSHAREDINFO)GetProcAddress(hUser32, "gSharedInfo");
```

一旦解析出了用户空间中的表位置，我们就可以遍历句柄表，打印每个对象的内核地址、它的所有者和对象类型。

```
for (unsigned int i = 0; i &lt; gSharedInfo-&gt;psi-&gt;cHandleEntries; i++) {
    HANDLEENTRY entry = gSharedInfo-&gt;aheList[i];
    if (entry.bType != 0) { //ignore free entries
        printf("Head: 0x%X, Owner: 0x%X, Type: 0x%Xrn", entry.phead, entry.pOwner, entry.bType);
    }
}
```

下面是它在32位Windows 7上的运行情况：

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0148116247d483f35f.png)

**<br>**

**Windows 8/8.1 64 bits**

为了将代码移植到64位系统，我们需要对代码稍作修改。 首先将SERVERINFO结构扩展为64位，方法是对dwSRVIFlags和cHandleEntries字段的大小进行相应的调整。

```
typedef struct _SERVERINFO {
#ifdef _WIN64
    UINT64 dwSRVIFlags;
    UINT64 cHandleEntries;
#else
    DWORD dwSRVIFlags;
    DWORD cHandleEntries;
#endif
```

同样，记录地址的printf语句也需要进行相应的修改，以便可以处理64位指针。

```
#ifdef _WIN64
    printf("Head: 0x%llx, Owner: 0x%llx, Type: 0x%Xrn", entry.phead, entry.pOwner, entry.bType);
#else
    printf("Head: 0x%X, Owner: 0x%X, Type: 0x%Xrn", entry.phead, entry.pOwner, entry.bType);
#endif
```

完成这些修改之后，它就可以在Windows 8.1上正常运行了。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011cd2e6fca8c84d23.png)

 <br>

**Windows 10?**

根据Dave Weston和Matt Miller在黑帽大会上的演讲，已经无法通过GDI共享句柄表获得内核地址。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01535298fade84777c.png)

但是当这个二进制代码在64位Windows 10 周年版虚拟机中运行时，我找到了一些像内核指针的东西：

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e834555e51daaf08.png)

通过考察这些地址，发现它们与内核空间中的预期会话空间地址范围相吻合，也就是都位于正确的取值范围内——至少对于64位的Windows 7来说的确如此。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01969b3a239ba460c9.png)

接下来，我加载了一个64位Windows 8机器，连接内核调试器并转储了句柄表，并将其与我在调试器中看到的值进行了相应的比较。下面的几个匹配值已经高亮显示，我们期望的值都能从用户模式代码中找到。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014951daf29d4360f8.png)

然后，我在64位的Windows 10上面进行了同样的试验。

[![](./img/85614/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0134cdd9bafd864a6e.png)

我发现句柄表的结构和指向的值，在不同的操作系统版本之间非常一致。我现在没有更多的时间来深入研究这些，所以这里先打一个问号，留待以后继续探索。
