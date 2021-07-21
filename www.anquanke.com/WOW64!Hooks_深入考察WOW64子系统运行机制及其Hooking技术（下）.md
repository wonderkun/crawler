> 原文链接: https://www.anquanke.com//post/id/222248 


# WOW64!Hooks：深入考察WOW64子系统运行机制及其Hooking技术（下）


                                阅读量   
                                **228521**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Stephen Eckels，文章来源：fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2020/11/wow64-subsystem-internals-and-hooking-techniques.html](https://www.fireeye.com/blog/threat-research/2020/11/wow64-subsystem-internals-and-hooking-techniques.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01f477c609ce775f96.jpg)](https://p3.ssl.qhimg.com/t01f477c609ce775f96.jpg)



在上一篇文章中，我们为读者详细介绍了WOW64子系统的内部运行机制，在本文中，我们将继续为读者介绍WOW64子系统的Hooking技术。



## 绕过Inline Hook

如这篇文章所述，Windows为32位应用程序提供了一种使用WOW64层在64位系统上执行64位系统调用的方法。但是，我们前面提到的分段机制的切换可以手动执行，并且可以编写64位shellcode来设置syscall。这项技术通常称为“天堂之门”。实际上，我们可以参考一下JustasMasiulis的作品call_function64，以了解具体的实现方法。当以这种方式执行系统调用时，在执行链中将完全跳过WOW64层使用的32位syscall stub。对于安全产品或跟踪工具来说，打击还是很大的，因为这些stub上的所有内联hook也会一起被绕过。实际上，恶意软件作者早就知道这一点了，并在某些情况下利用“天堂之门”作为绕过技术。图14和图15分别显示了通过WOW64层的常规syscall stub的执行流程，以及恶意软件利用“天堂之门”实现hooked的syscall stub的执行流程。

[![](https://p5.ssl.qhimg.com/t0125cd16411ceba9c5.png)](https://p5.ssl.qhimg.com/t0125cd16411ceba9c5.png)

图14 NtResumeThread通过WOW64层实现模式切换

[![](https://p5.ssl.qhimg.com/t0143bd5d8e933ad587.png)](https://p5.ssl.qhimg.com/t0143bd5d8e933ad587.png)

图15 NtResumeThread通过WOW64层实现模式切换之前的内联hook

如图15所示，当使用“天堂之门”技术时，在经过内联hook和WOW64层之后才开始执行。这是一种有效的绕过技术，但是很容易从较低级别（例如驱动程序或系统管理程序）检测到。内联hook的最简单绕过方法是简单地恢复原始函数的字节，通常是利用磁盘上的字节进行恢复。众所周知，诸如AgentTesla和Conti之类的恶意软件就利用这种绕过技术。



## 通过内联Hook来Hooking WOW64

作为一个恶意软件分析师，能够检测到样本何时试图绕过WOW64层是非常有用的。最容易想到的一种检测技术，就是同时在64位syscall stub和32位syscall stub上放置内联hook。如果64位hook检测到一个没有同时通过32位hook的调用，那么就知道一个样本正在利用“天堂之门”。这种技术可以检测到前面详细介绍的两种绕过技术。然而，在实际操作中，这是很难实现的。通过考察hook 64位syscall stub必须满足的要求，我们得到了下面的挑战列表：
1. 从32位模块中安装64位hook
1. 如何从32位模块中读/写64位地址空间？
1. 从32位模块中实现64位回调函数。
1. 通常情况下，内联hook使用C函数作为回调stub，但我们正在编译一个32位的模块，所以我们会得到一个32位的回调函数，而不是所需的64位回调函数。
为了解决第一个挑战，可以使用从ntdll中导出的NtWow64ReadVirtualMemory64、NtWow64WriteVirtualMemory64和NtWow64QueryInformationProcess64函数。通过这些函数，我们可以从32位进程中读取内存、写入内存、检索64位模块的PEB。然而，第二个挑战要难得多，因为无论是shellcode还是JIT都需要创建一个具有合适位数的回调stub。在实践中，我们可以利用ASMJIT来实现这一点。然而，这需要跟踪大量的API，因此，这是一种非常繁琐的技术。此外，这种技术也面临其他的挑战。例如，在现代Windows 10系统中，ntdll64的基本地址被设置为高64位地址，而不是像Windows 7中那样设置为低32位地址。由于这一点，实现从回调函数返回到原始hook的stub，并在所需的内存范围内分配一个蹦床（trampoline ）是很困难的，因为标准的ret指令在堆栈上没有足够的位来表示64位的返回地址。

另外，需要注意的是，WOW64层在处理NtWow64*函数时，可能存在一些安全问题。这些API都以HANDLE作为第一个参数，它应该以带符号的方式扩展为64位。然而，这些API并没有这样做，因此，当使用伪句柄-1时，调用会因STATUS_INVALID_HANDLE错误而失败。这个错误是在一个未知的Windows 10版本中引入的。要成功使用这些API，必须使用OpenProcess来检索一个真实的、正值的句柄。 

由于文章篇幅的原因，这里就不深入介绍如何利用内联hook来钩取syscall stub了。相反，我将展示如何使用这些Windows API扩展我的hooking库PolyHook2以支持跨体系结构的hooking技术，并将其余事情留给读者自己。这种方法之所以可行，一是PolyHook的蹦床没有+-2GB的限制，而是它不会破坏寄存器。至于具体的实现方法，我们将专门用一篇文章进行详细介绍。图16描述了如何使用上述WinAPI重载polyhook的C++ API来读/写内存。

[![](https://p4.ssl.qhimg.com/t01b8de36b4ef71b927.png)](https://p4.ssl.qhimg.com/t01b8de36b4ef71b927.png)

图16 重载内存操作以读/写/保护64位内存

一旦这些内联hook在64位syscall stub上就位，任何利用天堂之门的应用程序都会被正确拦截。虽然这种钩子技术具有非常高的侵入性和先进性，但是，如果样本是直接执行syscall指令，而不是使用64位模块的syscalls stub，那么这种技术仍然可以被绕过。因此，驱动程序或hypervisor程序更适合用于检测这种绕过技术。相反，我们可以关注更常见的字节还原绕过技术，并寻找一种方法来钩住WOW64层本身。这样的话，就完全不涉及汇编代码的修改了。



## 通过LogService来Hooking WOW64

回想一下WOW64层的执行流程，我们知道如果加载了日志DLL，所有通过Wow64SystemServiceEx例程发送的调用都可能调用例程Wow64LogSystemService。因此，我们可以利用这个日志DLL和例程来实现hook，并且，这些hook的编写方式与内联hook完全相同，却不需要修改任何汇编代码。

实现这个方法的第一步是强制所有API调用路径都通过Wow64SystemServiceEx例程，这样就可以调用日志例程了。记得前面说过，那些支持TurboThunks的程序不会通过这个路径。幸运的是，我们知道任何指向TurboDispatchJumpAddressEnd的TurboThunk条目都会通过这个路径。因此，通过将TurboThunk表中的每个条目指向该地址，就可以实现所需的行为。Windows系统可以通过wow64cpu!BTCpuTurboThunkControl实现这个表的修改，具体如图17所示。

[![](https://p1.ssl.qhimg.com/t01ba2f2639cbafc621.png)](https://p1.ssl.qhimg.com/t01ba2f2639cbafc621.png)

图17 针对TurboThunk表修改方法 

请注意，在以前的Windows版本中，导出这这些内容的模块以及导出方式都与Windows10，version 2004有所不同。在调用这个补丁例程后，所有通过WOW64的syscall路径都会经过Wow64SystemServiceEx，因此，我们只需精心构造一个日志DLL，就能中转所有的调用。不过，我们还面临几个挑战：
1. 我们如何从日志DLL中确定当前运行的是哪个系统调用？
1. 如何编写回调函数？别忘了，Wow64log可是一个64位的DLL，而我们却想要得到一个32位的回调函数。
1. 是否需要shellcode，或者我们编写一个C语言风格的函数回调？
1. 我们可以调用哪些API？
第一个问题相当简单，在wow64log DLL中，我们可以从syscall stub中读取syscall编号，以创建一个从编号到名字的映射。之所以能够做到这一点，是因为syscall stub都是以相同的汇编代码开始，而且syscall编号的静态偏移量为0x4。图18显示了我们应该如何将该映射中的值与传递给Wow64LogSystemService的参数结构WOW64_LOG_SERVICE的syscall编号进行比较。 

```
typedef uint32_t* WOW64_ARGUMENTS;
struct WOW64_LOG_SERVICE
`{`
      uint64_t BtLdrEntry;
      WOW64_ARGUMENTS Arguments;
      ULONG ServiceTable;
      ULONG ServiceNumber;
      NTSTATUS Status;
      BOOLEAN PostCall;
`}`;

EXTERN_C
__declspec(dllexport)
NTSTATUS
NTAPI
Wow64LogSystemService(WOW64_LOG_SERVICE* service)
`{`
     for (uint32_t i = 0; i &lt; LAST_SYSCALL_ID; i++) `{`
        const char* sysname = SysCallMap[i].name;
        uint32_t syscallNum = SysCallMap[i].SystemCallNumber;
        if (ServiceParameters-&gt;ServiceNumber != syscallNum)
            continue;
        //LOG sysname
     `}`
`}`
```

代码18：确定运行了哪个系统调用的最小例子——在实践中，还必须检查服务表

在这里，回调函数的编写是一个比较大的挑战。我们知道，wow64log DLL是在64位模式下执行的，而我们希望能够在32位模式下编写回调函数，因为将其他32位模块加载到WOW64进程中是非常容易的。处理这个问题的最好方法，就是编写能够切换到32位模式的shellcode，执行回调函数，然后切换回64位模式，继续在wow64log DLL中执行。这时，分段机制的切换本身是相当简单的，因为只需要在跳转时使用0x23或0x33段选择器就可以了。但是，我们还需要处理64位和32位调用约定之间的差异。因此，我们的shellcode需要把64位参数的寄存器/栈槽移到32位参数的寄存器/栈槽中。此外，我们还可以强制规定32位的回调函数只能是__cdecl，这样就更容易了，因为所有的参数都在栈上，而且shellcode可以完全控制栈的布局和清理。图19显示了每种调用约定的参数位置。重新定位前四个参数后，所有其他参数都可以依次移动，因为这里只是将堆栈值移动到较低的槽中。实际上，在MSVC中使用外部的masm文件来实现这一点是比较容易的。由于涉及两者架构，需要使用相应架构下的原始字节，而不是使用汇编器。另外，也可以使用GCC或Clang内联汇编。在ReWolf的作品中，已经实现了32位-&gt;64位的逆向过程，并通过msvc inline asm实现了相关的shellcode。但是，X64 MSVC还不支持这种方法，而且在使用该方法时，会面临REX前缀的复杂问题。因此，通过外部的masm文件，依靠链接器来实现这个shellcode是比较好的选择。 

[![](https://p4.ssl.qhimg.com/t011893c17be1b4834c.png)](https://p4.ssl.qhimg.com/t011893c17be1b4834c.png)

图19 Cdecl与Fastcall的参数位置

一旦写好shellcode并将其封装成一个漂亮的C++函数，wow64log DLL就可以通过图20所示的一个简单的C风格函数指针调用来调用回调函数。

[![](https://p2.ssl.qhimg.com/t01dbc88fbc83a6906d.png)](https://p2.ssl.qhimg.com/t01dbc88fbc83a6906d.png)

图20 call_function32调用shellcode，进而调用64位日志DLL的32位回调函数

在32位回调函数中，虽然可以执行任何所需的MITM操作，但是在可调用的API上存在限制。这是因为，由于该上下文会保存WOW64层的相关内容，所以调用重新进入WOW64层的32位API的话，会破坏上下文中相应的值。因此，我们只能调用不会重新进入WOW64的API，也就是那些从64位ntdll中导出的API。NtWriteFile导出函数可以用来对stdout或文件执行写操作，但我们必须重新进入64位执行模式，并像之前一样进行逆向参数映射。这个日志例程可以从32位回调函数内部进行调用，具体如图21和图22所示：

[![](https://p4.ssl.qhimg.com/t0178db867f1cca74c6.png)](https://p4.ssl.qhimg.com/t0178db867f1cca74c6.png)

图21 call_function64调用shellcode，通过32位回调函数来调用64位的WriteFile。

[![](https://p3.ssl.qhimg.com/t0117ed7bfcf35fa696.png)](https://p3.ssl.qhimg.com/t0117ed7bfcf35fa696.png)

图22 32位回调函数只能通过调用非重入式WOW64 API的例程来完成日志操作 

这样，我们就得到了简洁的回调stub，其功能与内联hook的功能完全相同，但不需要修改汇编代码。其实，参数也可以很容易被操纵，但返回状态可能无法修改，除非对堆栈的访问做了手脚。另外需要注意的是，wow64log DLL本身需要精心设计，以避免用到任何CRT机制：
1. 通过/NODEFAULT LIB禁用CRT（这样的话，所有的C API就都不可用了），设置一个新的入口点名称，以避免启动CRT NtDllMain；
1. 禁用所有CRT安全例程/GS-；
1. 禁用C++异常；
1. 删除默认的链接器库，只链接ntdll.lib；
1. 使用extern “C” __declspec(dllimport) &lt;typedef&gt;来链接到正确的NtApis。
图23中显示了一个通过wow64log内联hook钩住自己的系统调用的示例程序。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0104d24c9cda817f1d.gif)

图23 内联hook示例



## 小结

借助于内联WOW64 hook、wow64log hook和内核/hypervisor hook，我们可以轻松地自动地识别所有用户模式hook绕过技术。实际上，我们只需检测哪些层级的hook被跳过或绕过，就能深入了解攻击者采用的是哪种绕过技术： 



## 附录：相关的结构体代码

```
struct _WOW64_CPURESERVED
`{`
  USHORT Flags;
  USHORT MachineType;
  WOW64_CONTEXT Context;
  char ContextEx[1024];
`}`;

typedef ULONG *WOW64_LOG_ARGUMENTS;
struct _WOW64_SYSTEM_SERVICE
`{`
  unsigned __int32 SystemCallNumber : 12;
  unsigned __int32 ServiceTableIndex : 4;
  unsigned __int32 TurboThunkNumber : 5;
  unsigned __int32 AlwaysZero : 11;
`}`;
#pragma pack(push, 1)
struct _WOW64_FLOATING_SAVE_AREA
`{`
  DWORD ControlWord;
  DWORD StatusWord;
  DWORD TagWord;
  DWORD ErrorOffset;
  DWORD ErrorSelector;
  DWORD DataOffset;
  DWORD DataSelector;
  BYTE RegisterArea[80];
  DWORD Cr0NpxState;
`}`;
#pragma pack(pop)

#pragma pack(push, 1)
struct _WOW64_CONTEXT
`{`
  DWORD ContextFlags;
  DWORD Dr0;
  DWORD Dr1;
  DWORD Dr2;
  DWORD Dr3;
  DWORD Dr6;
  DWORD Dr7;
  WOW64_FLOATING_SAVE_AREA FloatSave;
  DWORD SegGs;
  DWORD SegFs;
  DWORD SegEs;
  DWORD SegDs;
  DWORD Edi;
  DWORD Esi;
  DWORD Ebx;
  DWORD Edx;
  DWORD Ecx;
  DWORD Eax;
  DWORD Ebp;
  DWORD Eip;
  DWORD SegCs;
  DWORD EFlags;
  DWORD Esp;
  DWORD SegSs;
  BYTE ExtendedRegistersUnk[160];
  M128A Xmm0;
  M128A Xmm1;
  M128A Xmm2;
  M128A Xmm3;
  M128A Xmm4;
  M128A Xmm5;
  M128A Xmm6;
  M128A Xmm7;
  M128A Xmm8;
  M128A Xmm9;
  M128A Xmm10;
  M128A Xmm11;
  M128A Xmm12;
  M128A Xmm13;
  M128A Xmm14;
  M128A Xmm15;
`}`;
#pragma pack(pop)
```
