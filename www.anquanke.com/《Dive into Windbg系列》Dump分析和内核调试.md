> 原文链接: https://www.anquanke.com//post/id/185951 


# 《Dive into Windbg系列》Dump分析和内核调试


                                阅读量   
                                **376169**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/dm/1024_576_/t01046f75101c73b87d.jpg)](https://p3.ssl.qhimg.com/dm/1024_576_/t01046f75101c73b87d.jpg)


- 作者：BlackINT3
<li>联系：[blackint3@gmail.com](mailto:blackint3@gmail.com)
</li>
<li>网站：[https://github.com/BlackINT3](https://github.com/BlackINT3)
</li>
> 《Dive into Windbg》是一系列关于如何理解和使用Windbg的文章，主要涵盖三个方面：
<ul>
- 1、Windbg实战运用，排查资源占用、死锁、崩溃、蓝屏等，以解决各种实际问题为导向。
- 2、Windbg原理剖析，插件、脚本开发，剖析调试原理，便于较更好理解Windbg的工作机制。
- 3、Windbg后续思考，站在开发和逆向角度，谈谈软件开发，分享作者使用Windbg的一些经历。
</ul>

## 第五篇 《Dump分析和内核调试》

> 涉及知识点：Dump分析技巧、内核杂谈、双机调试、调试内核启动过程。



## Dump分析

调试是程序员的必备能力，而dump分析又是调试领域中极其重要的部分。dump经常用于还原现场，事后分析问题原因，但其作用远不止此，后文会具体说明。

#### <a class="reference-link" name="Minidump%E4%BB%8B%E7%BB%8D"></a>Minidump介绍

这里的Minidump主要指应用程序dump，以下统称dump。简言之，dump就是一个快照，一堆状态的集合，就好比一个犯罪现场，信息越多越容易找到原因。dump一般包括系统、内存、模块、线程信息以及异常上下文等，我们想把所有信息都保存下来，但受限于文件大小和数据收集的时间，所以产生了Minidump和FullDump两种类型（这里只是简单的区别，信息多的叫Full，信息少的叫Mini）。

Windows提供了生成dump的API，即[MiniDumpWriteDump](https://docs.microsoft.com/en-us/windows/win32/api/minidumpapiset/nf-minidumpapiset-minidumpwritedump)函数：

```
BOOL MiniDumpWriteDump(
  HANDLE                            hProcess,
  DWORD                             ProcessId,
  HANDLE                            hFile,
  MINIDUMP_TYPE                     DumpType,
  PMINIDUMP_EXCEPTION_INFORMATION   ExceptionParam,
  PMINIDUMP_USER_STREAM_INFORMATION UserStreamParam,
  PMINIDUMP_CALLBACK_INFORMATION    CallbackParam
);
```

参数DumpType就是dump类型，调用者可按自己需求收集数据、定制dump。

```
typedef enum _MINIDUMP_TYPE `{`
  MiniDumpNormal,
  MiniDumpWithDataSegs,
  MiniDumpWithFullMemory,
  MiniDumpWithHandleData,
  MiniDumpFilterMemory,
  MiniDumpScanMemory,
  MiniDumpWithUnloadedModules,
  MiniDumpWithIndirectlyReferencedMemory,
  MiniDumpFilterModulePaths,
  MiniDumpWithProcessThreadData,
  MiniDumpWithPrivateReadWriteMemory,
  MiniDumpWithoutOptionalData,
  MiniDumpWithFullMemoryInfo,
  MiniDumpWithThreadInfo,
  MiniDumpWithCodeSegs,
  MiniDumpWithoutAuxiliaryState,
  MiniDumpWithFullAuxiliaryState,
  MiniDumpWithPrivateWriteCopyMemory,
  MiniDumpIgnoreInaccessibleMemory,
  MiniDumpWithTokenInformation,
  MiniDumpWithModuleHeaders,
  MiniDumpFilterTriage,
  MiniDumpWithAvxXStateContext,
  MiniDumpWithIptTrace,
  MiniDumpValidTypeFlags,
  MiniDumpScanInaccessiblePartialPages
`}` MINIDUMP_TYPE;
```

根据命名就能大致知道其含义，详细说明可参考[官方文档](https://docs.microsoft.com/zh-cn/windows/win32/api/minidumpapiset/ne-minidumpapiset-minidump_type)。

关于Minidump的文件结构，Windows公开了一部分，dbghelp.h头文件里有具体定义(Windows SDK 10已把相关定义单独放到minidumpapiset.h中)。

首先是Minidump文件头：

```
#define MINIDUMP_SIGNATURE ('PMDM')
#define MINIDUMP_VERSION   (42899)
typedef struct _MINIDUMP_HEADER `{`
    ULONG32 Signature;
    ULONG32 Version;
    ULONG32 NumberOfStreams;    // Stream个数
    RVA StreamDirectoryRva;     // Stream偏移
    ULONG32 CheckSum;
    union `{`
        ULONG32 Reserved;
        ULONG32 TimeDateStamp;
    `}`;
    ULONG64 Flags;
`}` MINIDUMP_HEADER, *PMINIDUMP_HEADER;
```

接下来就是各个Stream（通过个数和偏移定位），dump的整体结构可参考[windows_minidump.svg](https://formats.kaitai.io/windows_minidump/windows_minidump.svg)。

我们也可以用010Editor的MiniDumpTemplate.bt模板来查看，例如查看某应用程序的dmp，运行模板后：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013d4a2d31feec06fc.png)

从上图我们可以看到各个Stream，这里我们介绍一些常用的数据，其它的可参考[Windows文档](https://docs.microsoft.com/en-us/windows/win32/api/minidumpapiset/ne-minidumpapiset-minidump_stream_type)：

```
Module、Thread、Memory List是模块列表、线程列表、内存数据。lm、~、dd等查看命令就从这里读取数据。

ExceptionStream是异常记录，这在分析崩溃时很有用（下文会详细说明），我们常用的.excr命令便是从中得到的数据。

SystemInfo包含系统信息，CPU核数、系统版本等。

MiscInfo包含进程ID、CPU时间、启动时间等，加载Dump分析时会输出相关信息。

HandleData包含句柄信息，!handle命令会用到。

MemoryInfoList包含内存vad区域列表，!address会用到。

ThreadInfoList包含线程信息，例如CPU时间（内核/用户态时间），这在分析CPU占有时很有用，!runaway命令便是从中获取的数据。
```

看到这里是不是感觉MINIDUMP_TYPE和MINIDUMP_STREAM_TYPE几乎一致？没错，从设计上讲采集和解析是对应的。

此外我们还可以通过扩展dump类型来自定义数据格式结构，从而收集额外数据。结构扩展不会影响兼容性，用windbg还是可以继续分析。

看一段breakpad的扩展的结构：

```
https://github.com/google/breakpad/blob/88d8114fda3e4a7292654bd6ac0c34d6c88a8121/src/google_breakpad/common/minidump_format.h

/* For (MDRawDirectory).stream_type */
typedef enum `{`
  MD_UNUSED_STREAM               =  0,
  MD_RESERVED_STREAM_0           =  1,
  MD_RESERVED_STREAM_1           =  2,
  MD_THREAD_LIST_STREAM          =  3,  /* MDRawThreadList */
  MD_MODULE_LIST_STREAM          =  4,  /* MDRawModuleList */
  MD_MEMORY_LIST_STREAM          =  5,  /* MDRawMemoryList */
  MD_EXCEPTION_STREAM            =  6,  /* MDRawExceptionStream */
  MD_SYSTEM_INFO_STREAM          =  7,  /* MDRawSystemInfo */
  MD_THREAD_EX_LIST_STREAM       =  8,
  MD_MEMORY_64_LIST_STREAM       =  9,
  MD_COMMENT_STREAM_A            = 10,
  MD_COMMENT_STREAM_W            = 11,
  MD_HANDLE_DATA_STREAM          = 12,
  MD_FUNCTION_TABLE_STREAM       = 13,
  MD_UNLOADED_MODULE_LIST_STREAM = 14,
  MD_MISC_INFO_STREAM            = 15,  /* MDRawMiscInfo */
  MD_MEMORY_INFO_LIST_STREAM     = 16,  /* MDRawMemoryInfoList */
  MD_THREAD_INFO_LIST_STREAM     = 17,
  MD_HANDLE_OPERATION_LIST_STREAM = 18,
  MD_TOKEN_STREAM                = 19,
  MD_JAVASCRIPT_DATA_STREAM      = 20,
  MD_SYSTEM_MEMORY_INFO_STREAM   = 21,
  MD_PROCESS_VM_COUNTERS_STREAM  = 22,
  MD_LAST_RESERVED_STREAM        = 0x0000ffff,

  /* Breakpad extension types.  0x4767 = "Gg" */
  MD_BREAKPAD_INFO_STREAM        = 0x47670001,  /* MDRawBreakpadInfo  */
  MD_ASSERTION_INFO_STREAM       = 0x47670002,  /* MDRawAssertionInfo */
  /* These are additional minidump stream values which are specific to
   * the linux breakpad implementation. */
  MD_LINUX_CPU_INFO              = 0x47670003,  /* /proc/cpuinfo      */
  MD_LINUX_PROC_STATUS           = 0x47670004,  /* /proc/$x/status    */
  MD_LINUX_LSB_RELEASE           = 0x47670005,  /* /etc/lsb-release   */
  MD_LINUX_CMD_LINE              = 0x47670006,  /* /proc/$x/cmdline   */
  MD_LINUX_ENVIRON               = 0x47670007,  /* /proc/$x/environ   */
  MD_LINUX_AUXV                  = 0x47670008,  /* /proc/$x/auxv      */
  MD_LINUX_MAPS                  = 0x47670009,  /* /proc/$x/maps      */
  MD_LINUX_DSO_DEBUG             = 0x4767000A,  /* MDRawDebug`{`32,64`}`  */

  /* Crashpad extension types. 0x4350 = "CP"
   * See Crashpad's minidump/minidump_extensions.h. */
  MD_CRASHPAD_INFO_STREAM        = 0x43500001,  /* MDRawCrashpadInfo  */
`}` MDStreamType;  /* MINIDUMP_STREAM_TYPE */
```

可以看到breakpad自己扩充了多种类型，例如融入了linux的core dump，将两者设计成统一的dump格式（Google确实喜欢做这种事情），对这部分感兴趣的读者可自行阅读。

#### <a class="reference-link" name="CrashDump%E4%BB%8B%E7%BB%8D"></a>CrashDump介绍

CrashDump也叫Kernel Dump，一般由内核在蓝屏崩溃时生成，由于内核和应用层的差异，Minidump和Crashdump结构也不同，相比之下Crashdump设计地更紧凑。

按照惯例，首先应该是Header（32位和64位有些许区别）：

```
// 32位：https://bbs.pediy.com/thread-63048-1.htm
typedef struct _DUMP_HEADER32 /* sizeof = 0x1000 */
`{`
/* 000 */   ULONG       ulSignature;
/* 004 */   ULONG       ulValidDump;
/* 008 */   ULONG       ulMajorVersion;
/* 00C */   ULONG       ulMinorVersion;
/* 010 */   ULONG       ulDirectoryTableBase;
/* 014 */   ULONG       ulPfnDataBase;
/* 018 */   PLIST_ENTRY PsLoadedModuleList;
/* 01C */   PLIST_ENTRY PsActiveProcessHead;
/* 020 */   ULONG       ulMachineImageType;
/* 024 */   ULONG       ulNumberProcessors;
/* 028 */   ULONG       ulBugCheckCode;
/* 02C */   ULONG       ulBugCheckParameter1;
/* 030 */   ULONG       ulBugCheckParameter2;
/* 034 */   ULONG       ulBugCheckParameter3;
/* 038 */   ULONG       ulBugCheckParameter4;
/* 03C */   char        szVersionUser[32];
/* 05C */   BOOLEAN     bPaeEnabled;
/* 05D */   UCHAR       uchKdSecondaryVersion;
/* 05E */   char        chUnused1[2];
/* 060 */   ULONG       ulKdDebuggerDataBlock;
/* 064 */   PHYSICAL_MEMORY_DESCRIPTOR  stPhysMemDesc;
/* 074 */   char        chUnused2[684];
/* 320 */   CONTEXT     stContext;
/* 5EC */   char        chUnused3[484];
/* 7D0 */   EXCEPTION_RECORD32  stExceptionRecord;
/* 820 */   char        szComment[1896];
/* F88 */   ULONG       ulDumpType;
/* F8C */   ULONG       ulMiniDumpFields;
/* F90 */   ULONG       ulSecondaryDataState;
/* F94 */   ULONG       ulProductType;
/* F98 */   ULONG       ulSuiteMask;
/* F9C */   ULONG       ulWriterStatus;
/* FA0 */   ULONG64     ulFileSize;
/* FA8 */   char        chUnused4[16];
/* FB8 */   ULONG64     ulSystemUptime;
/* FC0 */   ULONG64     ulDebugSessionTime;
/* FC8 */   char        chUnused5[56];
`}` DUMP_HEADER32, *PDUMP_HEADER32;
// 64位参考：https://github.com/larytet/parse_minidump/blob/master/parse_minidump.py
```

010editor也提供了CrashDump的模板—[DMP.bt](https://www.sweetscape.com/010editor/repository/templates/file_info.php?file=DMP.bt&amp;type=0&amp;sort=)，不过这个模板只适用32位，运行结果如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0184ac22843db25017.png)

关于CrashDump的生成可参考《Windows.Internals.6th.Part2》-Crash Dump Generation，因为蓝屏时dump是先写到Pagefile中，重启时再由smss写到WindowsMinidump目录里，如果遇到开机蓝屏，进PE系统发现没有dump文件生成，可以看看Pagefile是否写入了dump数据。

对于32位系统，我们可以通过Hook KeBugCheck和读取KD_DEBUGGER_DATA_BLOCK来生成dump数据。64位大多使用[KeRegisterBugCheckReasonCallback](https://docs.microsoft.com/windows-hardware/drivers/ddi/content/wdm/nf-wdm-keregisterbugcheckreasoncallback)注册回调来操作dump，关于这块可参考[《Writing a Bug Check Reason Callback Routine》](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/writing-a-bug-check-callback-routine)。

#### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E5%88%86%E6%9E%90Dump%EF%BC%9F"></a>如何分析Dump？

首先配置Windbg符号路径，新手经常遇到符号配置问题，例如：

```
1、路径配置不正确。
解决方法：!sym noisy开启详细输出（!sym quiet关闭），可以清楚看到符号搜索以及下载情况，再做对应调整。

2、访问服务器超时，导致无法下载符号。
解决方法：使用.reload /f 模块 强制加载，如果还失败，到符号目录去删掉download.error文件，再加载。
```

分析问题常采用从整体到局部的方法，对于分析dump也适用。首先通过栈回溯我们能对问题有整体认识，接着再从局部出发，追踪异常点的内存数据和指令代码。

**程序崩溃**：我们首先使用.ecxr定位到异常点，有时候会有如下提示：

```
Minidump doesn't have an exception context
Unable to get exception context, HRESULT 0x80004002

```

说明是dump没有保存上面提到的ExceptionStream，因此只能查看所有线程的栈回溯来定位（寻找WER、SEH等关键函数调用）。

我们通常用kb来查看栈回溯，但有时候调用栈也会分析出错，总结下来有几种情况：

```
1 符号文件错误，函数偏移明显不对
2 栈被破坏（溢出）
3 调用点被inline hook
4 函数优化
```

遇到这种情况需要自己修复，这里说个实用方法：首先找到异常分发点KiUserExceptionDispatcher（关于异常，可参考笔者绘制的[异常处理流程图](https://github.com/BlackINT3/awesome-debugging/blob/master/windbg/exception-handling-flow.png)），用dps rsp/esp查看栈中的符号，以此为界，回溯寻找最可能的调用函数，这里32位因调用约定不一样，验证方式不一样。

```
32位，根据调用约定，通过栈帧ebp入手，验证函数地址addr，k=addr，最后修复栈回溯。
64位，根据调用约定，通过.fnent查看UnwindInfo，补齐对应的栈大小，验证调用函数地址，接着同上。
```

再说说资源占用的情况，CPU、内存、句柄占用比较常见（注意：要使用下面的命令，需要dump中包含相应的信息）。

**CPU占用**：使用!runaway找到各线程CPU时间（上节提到过ThreadInfoStream），找到占用时间最多的线程，再通过栈回溯分析，原因多是一些大循环，在第一篇文章里有分析wireshark假死问题。一般CPU占用高的线程不会处于等待状态，因此可以从栈上看出来。又或者在内核里转圈导致内核占用时间长，这种只能靠调用链和Native这层函数来猜了，毕竟应用层dump没有内核信息。

**内存占用**：使用!address来看内存分布，一般都是堆未释放（有些shell api本身也存在内存泄露），堆还可以用!heap来分析，查看头、堆块以及堆中数据等，进而排查原因。

**句柄占用**：使用!handle找到最多的句柄类型，根据类型来推测是哪里的代码导致，例如Process可能循环调用了OpenProcess后忘记CloseHandle。

相比之下，资源占用问题很难从一个dump中找到原因，更好的方式还是动态监控，用WPA、VTune等工具来分析。

dump还可以用来对内存做个快照，结合函数符号写一些脚本来解密数据，比如笔者多年前就用脚本从dump中解密过许多数据，这种方式有几个好处：
- 无需写代码注入进程
- 利用符号获取函数和变量很容易，例如虚函数，未公开API等
- 搜索各种内存方便
- 操作成本低，脚本开发迅速
**蓝屏分析**：对于CrashDump一般只存核心数据，大小只有几百KB，因此dump中能访问的数据不多，异常上下文、程序代码段、内核栈，以及内核模块链表等，具体可参考CrashDump结构。

Windbg的帮助文档《Bug Check Code Reference》包含了所有蓝屏错误代码、字段含义、错误分析等，分析前结合!analyze -v使用。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01711e5b0bbbe77061.png)

初步了解错误原因后（比如常见的IRQL不匹配、页面异常等），再查看栈回溯来定位问题，可能还要走读异常的汇编代码，结合当前上下文状态来分析，自己写的驱动建议先跑一遍Verifier。



## 内核调试

#### <a class="reference-link" name="Windows%E5%86%85%E6%A0%B8%E6%9E%B6%E6%9E%84"></a>Windows内核架构

[《Windows三十年进化史，你还记得自己最初使用的系统吗？》](https://baijiahao.baidu.com/s?id=1591891752071867827&amp;wfr=spider&amp;for=pc)

```
Windows 9x kernel, used in Windows 95, 98 and ME
Windows NT kernel, used in all Windows NT systems (including Windows NT, 2000, XP, Vista, 7, 8, 8.1 and 10)
```

[![](https://p2.ssl.qhimg.com/t01bb42af2c1bf47991.jpg)](https://p2.ssl.qhimg.com/t01bb42af2c1bf47991.jpg)

沉思两分钟…

#### <a class="reference-link" name="%E5%86%85%E6%A0%B8%E8%B0%83%E8%AF%95%E6%96%B9%E6%B3%95"></a>内核调试方法

内核支持的调试方式很多，常用三种：

虚拟机调试内核

```
VMware/VirtualBox用虚拟串口调试，这个不用多说了，到处都是资料教你怎么配置...

推荐用VirtualKD来配置调试，速度快、方便管理，建议使用SSD硬盘并创建快照。
http://sysprogs.com/legacy/virtualkd/
```

网络双机调试

```
有时候需要调试物理机，目前最方便的就是网络调试。
微软官方给了详细说明：https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/setting-up-a-network-debugging-connection
简言之：
先约定，调试机是Host，被调试机是Target
1、前提：Host必须是Win7以上，Target必须是Win8以上，Target需要网卡芯片支持，文档里有详细说明，大多都支持。
2、连到一个局域网（如交换机），先得到Target的IP（例如192.168.1.109）。
3、Target执行以下下命令，port任选（例如50009）：
bcdedit /debug on
bcdedit /dbgsettings net hostip:192.168.1.109 port:50009
执行后会拿到一个key，例如Key=xxxxxxxx
4、Host打开Windbg的Kernel Debugging，选择NET，填好端口和Key(xxxxxxxx)，确定即可调试。
```

本地内核调试

```
说到本地内核调试LKD，印象中XP是用NtSystemDebugControl，Vista之后dbgeng.dll会执行LocalLiveKernelTargetInfo :: InitDriver安装kldgbdrv.sys驱动，调用KdSystemDebugControl来实现调试，因此需要bcdedit /debug on。Windbg在Kernel Debugging选择Local即可调试。

推荐用livekd（文件过滤+Dump实现）来调试内核，使用及其方便，之前的文章已提过如何使用，这里就不再赘述了。
livekd.exe -w -k c:windbg.exe
```

#### <a class="reference-link" name="%E8%B0%83%E8%AF%95%E5%86%85%E6%A0%B8%E5%90%AF%E5%8A%A8%E8%BF%87%E7%A8%8B"></a>调试内核启动过程

调试启动过程是研究内核的绝佳方式，我们不追究细节，只关注一些关键函数，关于详细的启动流程可参考《Windows.Internals.6.part2》-Startup and Shutdown。

我们来跟踪64位Win10的内核启动过程，首先挂上调试器，断在DebugService2：

```
Windows 10 Kernel Version 18362 MP (1 procs) Free x64
Built by: 18362.1.amd64fre.19h1_release.190318-1202
Machine Name:
Kernel base = 0xfffff807`50e09000 PsLoadedModuleList = 0xfffff807`5124c290
System Uptime: 0 days 0:00:00.007
nt!DebugService2+0x5:
fffff807`50fcd5d5 cc              int     3
kd&gt; k
 # Child-SP          RetAddr           Call Site
00 fffff807`53a78de8 fffff807`50f599b5 nt!DebugService2+0x5
01 fffff807`53a78df0 fffff807`51759bf8 nt!DbgLoadImageSymbols+0x45
02 fffff807`53a78e40 fffff807`5139b17c nt!KdInitSystem+0xaa8
03 fffff807`53a78fc0 00000000`00000000 nt!KiSystemStartup+0x16c

```

通过栈回溯可知在初始化KD，KdInitSystem的实现可参考ReactOS，其它函数则参考WRK。走到这里，我们已经错过了BIOS、Bootmgr、Winload的启动过程，直接进入了NT内核初始化的阶段。如果要调试Bootmgr或Winload可参考文档[bootdebug](https://docs.microsoft.com/en-us/windows-hardware/drivers/devtest/bcdedit--bootdebug)，这里不再说明。

Winload传递参数LoaderBlock给KiSystemStartup，KiSystemStartup把它赋值给KeLoaderBlock。

```
PLOADER_PARAMETER_BLOCK KeLoaderBlock;

VOID
KiSystemStartup(
    IN PVOID LoaderBlock
);

nt!KiSystemStartup:
fffff807`5139b010 4883ec38        sub     rsp,38h
fffff807`5139b014 4c897c2430      mov     qword ptr [rsp+30h],r15
fffff807`5139b019 4c8bfc          mov     r15,rsp
fffff807`5139b01c 48890db5d3fdff  mov     qword ptr [nt!KeLoaderBlock (fffff807`513783d8)],rcx  //保存KeLoaderBlock。

kd&gt; dt poi(nt!KeLoaderBlock) nt!_LOADER_PARAMETER_BLOCK
   +0x000 OsMajorVersion   : 0xa
   +0x004 OsMinorVersion   : 0
   +0x008 Size             : 0x160
   +0x00c OsLoaderSecurityVersion : 1
   +0x010 LoadOrderListHead : _LIST_ENTRY [ 0xfffff807`4f91fc00 - 0xfffff807`4fa7aed0 ]
   +0x020 MemoryDescriptorListHead : _LIST_ENTRY [ 0xfffff807`4fae0000 - 0xfffff807`4fae23c8 ]
   +0x030 BootDriverListHead : _LIST_ENTRY [ 0xfffff807`4fa19150 - 0xfffff807`4fa17130 ]
   +0x040 EarlyLaunchListHead : _LIST_ENTRY [ 0xfffff807`4fa1bbc0 - 0xfffff807`4fa1bbc0 ]
   +0x050 CoreDriverListHead : _LIST_ENTRY [ 0xfffff807`4fa1bd70 - 0xfffff807`4fa19990 ]
   +0x060 CoreExtensionsDriverListHead : _LIST_ENTRY [ 0xfffff807`4fa17df0 - 0xfffff807`4fa1c460 ]
   +0x070 TpmCoreDriverListHead : _LIST_ENTRY [ 0xfffff807`4fa09f10 - 0xfffff807`4fa09f10 ]
   +0x080 KernelStack      : 0xfffff807`53a80000
   +0x088 Prcb             : 0xfffff807`4fc66180
   +0x090 Process          : 0xfffff807`513929c0
   +0x098 Thread           : 0xfffff807`51395400
   +0x0a0 KernelStackSize  : 0x6000
   +0x0a4 RegistryLength   : 0xc80000
   +0x0a8 RegistryBase     : 0xfffff807`4fce0000 Void
   +0x0b0 ConfigurationRoot : 0xfffff807`4f9362c0 _CONFIGURATION_COMPONENT_DATA
   +0x0b8 ArcBootDeviceName : 0xfffff807`4f8f4460  "multi(0)disk(0)rdisk(0)partition(3)"
   +0x0c0 ArcHalDeviceName : 0xfffff807`4f8f4360  "multi(0)disk(0)rdisk(0)partition(1)"
   +0x0c8 NtBootPathName   : 0xfffff807`4f924110  "WINDOWS"
   +0x0d0 NtHalPathName    : 0xfffff807`4f924a20  ""
   +0x0d8 LoadOptions      : 0xfffff807`4f924440  " TESTSIGNING  NOEXECUTE=OPTIN  DEBUG  DEBUGPORT=COM1  BAUDRATE=115200  NOVGA  DISABLE_INTEGRITY_CHECKS"
   +0x0e0 NlsData          : 0xfffff807`4fa62040 _NLS_DATA_BLOCK
   +0x0e8 ArcDiskInformation : 0xfffff807`4f9255a0 _ARC_DISK_INFORMATION
   +0x0f0 Extension        : 0xfffff807`4f8f4760 _LOADER_PARAMETER_EXTENSION
   +0x0f8 u                : &lt;anonymous-tag&gt;
   +0x108 FirmwareInformation : _FIRMWARE_INFORMATION_LOADER_BLOCK
   +0x148 OsBootstatPathName : (null) 
   +0x150 ArcOSDataDeviceName : (null) 
   +0x158 ArcWindowsSysPartName : (null)

```

KiSystemStartup的流程在新版本中改动不大，查看源码`{`wrk`}`basentoskeamd64start.asm：

```
mov     rcx, KeLoaderBlock      ; set loader block address
call    KiInitializeBootStructures ; initialize boot structures // HAL

xor     ecx, ecx                ; set phase to 0
mov     rdx, KeLoaderBlock      ; set loader block address
call    KdInitSystem            ; initialize debugger   // &lt;- 中断在此

mov     ecx, HIGH_LEVEL         ; set high IRQL
SetIrql                         ;

mov     rax, KeLoaderBlock      ; set loader block address
mov     rcx, LpbProcess[rax]    ; set idle process address
mov     rdx, LpbThread[rax]     ; set idle thread address
mov     r8, gs:[PcTss]          ; set idle stack address
mov     r8, TssRsp0[r8]         ;
mov     gs:[PcRspBase], r8      ; set initial stack address in PRCB
mov     r9, LpbPrcb[rax]        ; set PRCB address
mov     r10b, PbNumber[r9]      ; set processor number
mov     SsFrame.P5[rsp], r10    ;
mov     SsFrame.P6[rsp], rax    ; set loader block address
call    KiInitializeKernel      ; Initialize kernel
```

KiInitializeBootStructures会初始化当前CPU，虽然我们已经错过了CPU0的初始化，但还可以调试其它CPU的初始化。

接着用!irql查看，当前处于LOW_LEVEL(0)，继续调试代码，来到KiInitializeKernel，IRQL已经变成HIGH_LEVEL(15)。

```
VOID
KiInitializeKernel (
    IN PKPROCESS Process,
    IN PKTHREAD Thread,
    IN PVOID IdleStack,
    IN PKPRCB Prcb,
    IN CCHAR Number,  // CPU编号
    PLOADER_PARAMETER_BLOCK LoaderBlock
)
```

执行uf /c nt!KiInitializeKernel，发现其调用了nt!InitBootProcessor，执行uf /c nt!InitBootProcessor，可以看到在阶段0初始化各个组件：

```
// 部分组件
hal!HalInitSystem // HAL层内核相关的初始化，阶段0
nt!CmInitSystem0 // 配置管理初始化，阶段0
nt!ExInitSystem // Executive层初始化
nt!MmInitSystem // 内存管理器初始化
nt!ObInitSystem // 对象管理器初始化
nt!SeInitSystem  // 安全管理器初始化
nt!PspInitPhase0 // 进程管理器初始化
nt!DbgkInitialize // 用户态调试系统初始化
nt!PpInitSystem // PNP初始化
```

来到PspInitPhase0函数，设置当前进程为Idle，创建System进程和Phase1Initialization线程：

```
// 创建System进程
if (!NT_SUCCESS (PspCreateProcess (&amp;PspInitialSystemProcessHandle,
                                  PROCESS_ALL_ACCESS,
                                  &amp;ObjectAttributes,
                                  NULL,
                                  0,
                                  NULL,
                                  NULL,
                                  NULL,
                                  0))) `{`
  return FALSE;
`}`

strcpy((char *) &amp;PsIdleProcess-&gt;ImageFileName[0], "Idle"); // 当前进程名设置成Idle
strcpy((char *) &amp;PsInitialSystemProcess-&gt;ImageFileName[0], "System"); // 设置System进程名

// 创建线程，执行阶段1的初始化
if (!NT_SUCCESS (PsCreateSystemThread (&amp;ThreadHandle,
                                        THREAD_ALL_ACCESS,
                                        &amp;ObjectAttributes,
                                        0L,
                                        NULL,
                                        Phase1Initialization,
                                        (PVOID)LoaderBlock))) `{`
    return FALSE;
`}`
```

PspInitPhase0执行完后，当前线程（Idle线程）返回到nt!KiSystemStartup，开始执行nt!KiIdleLoop。

```
nt!KiSystemStartup+0x284:
fffff807`5139b294 e8a7dfc2ff      call    nt!KiIdleLoop (fffff807`50fc9240)
```

nt!KiIdleLoop会执行DPC、调用SwapContext进行线程切换，一直循环做此类工作。

正是由于KiIdleLoop主动让出了CPU，上面的系统线程Phase1Initialization才得以执行，我们跟踪到该函数：

```
nt!Phase1Initialization:
fffff807`515618e0 48895c2408      mov     qword ptr [rsp+8],rbx ss:0018:fffff984`39406c10=ffff850e38868300
kd&gt; k
 # Child-SP          RetAddr           Call Site
00 fffff984`39406c08 fffff807`50f39925 nt!Phase1Initialization
01 fffff984`39406c10 fffff807`50fccd5a nt!PspSystemThreadStartup+0x55
02 fffff984`39406c60 00000000`00000000 nt!KiStartSystemThread+0x2a
```

阶段1的主要工作由Phase1InitializationDiscard完成，这个函数工作量极大，也是最内核初始化最核心的部分。

执行uf /c nt!Phase1InitializationDiscard，查看调用的函数：

```
nt!HalInitSystem // HAL层内核相关的初始化，阶段1
nt!PoInitSystem // 电源管理器初始化
nt!KeStartAllProcessors // 让所有CPU开始干活
nt!ObInitSystem  // 对象管理器初始化
nt!KeInitSystem // Kernel层相关初始化，对应Executive
nt!KdInitSystem // 内核态调试组件初始化
nt!DbgkInitialize // 用户态调试组件初始化
nt!SeInitSystem // 安全管理器初始化
nt!MmInitSystem // 内存管理器初始化
nt!CcInitializeCacheManager // 缓存管理器初始化
nt!CmInitSystem1 // 配置管理器初始化，阶段1
nt!EmInitSystem // Errata管理器初始化
nt!MfgInitSystem // Manufacturer管理器初始化
nt!PfInitializeSuperfetch // Prefeacther初始化
nt!SmInitSystem // 存储管理器初始化
nt!FsRtlInitSystem // 全局文件系统相关结构初始化
nt!PpInitSystem // PNP初始化
nt!AlpcpInitSystem // ALPC初始化
nt!ExInitSystemPhase2 //Executive第二次初始化
nt!ExInitializeNls // NLS初始化
nt!IoInitSystem // 初始化I/O管理器，加载系统驱动，这个函数在Phase1Initialization中被调用
nt!Phase1InitializationIoReady，这是I/O管理器初始化的后续部分，这个函数在Phase1Initialization中被调用。
  nt!CmInitSystem2 // 跟I/O相关的初始化
  nt!EmInitSystem // 同上
  nt!MmInitSystem // 同上
  nt!PoInitSystem // 同上
  nt!PspInitPhase2 // 同上
  nt!SeRmInitPhase1 // 同上
  nt!PspInitPhase3 // 同上
  nt!StartFirstUserProcess // 启动SMSS进程
  nt!KeInitSystem // 
  nt!InitSafeBoot // 安全模式
```

阶段1的最后，各个组件初始化完成，开始启动SMSS进程。最后再来看下CrashDump的初始化，在nt!IoInitializeCrashDump下断点：

```
bp nt!IoInitializeCrashDump
00 fffff880`009a9628 fffff800`043a2aee nt!IoInitializeCrashDump
01 fffff880`009a9630 fffff800`041b0a7c nt!IopInitCrashDumpRegCallback+0x10e
02 fffff880`009a9700 fffff800`04134d0e nt! ?? ::NNGAKEGL::`string'+0x13c61
03 fffff880`009a9780 fffff800`043a2b92 nt!RtlQueryRegistryValues+0x17e
04 fffff880`009a9850 fffff800`043ac467 nt!IopInitCrashDumpDuringSysInit+0x72
05 fffff880`009a9900 fffff800`043af610 nt!IoInitSystem+0x837
06 fffff880`009a9a00 fffff800`042ffe29 nt!Phase1InitializationDiscard+0x1270
07 fffff880`009a9bd0 fffff800`0411673a nt!Phase1Initialization+0x9
08 fffff880`009a9c00 fffff800`03e6b8e6 nt!PspSystemThreadStartup+0x5a
09 fffff880`009a9c40 00000000`00000000 nt!KxStartSystemThread+0x16

```

可以看到IoInitializeCrashDump在IoInitSystem下面被调用，同时会打开Pagefile.sys文件对象（蓝屏时会写dump数据到Pagefile，前面已介绍过）。



## 结束

内核代码相对于应用程序来说，逻辑较简单，流程也更清晰，反正你不听话就BSOD，搞内核首先要对系统架构、底层硬件有清晰的认识，Windows这种的还要熟练掌握逆向，时不时还要反汇编分析各种结构（尽管有了WRK，Windows也算个半开源系统）。

关于这些总（luo）结（suo）的话，以后有时间再说，Thanks for reading。

```
参考资料：
Google
Windbg Help
MSDN
WRK
Windows Internals
```
