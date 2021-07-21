> 原文链接: https://www.anquanke.com//post/id/207046 


# 红队战术：在C#中使用syscall之背景知识介绍


                                阅读量   
                                **238442**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Jack Halon，文章来源：jhalon.github.io
                                <br>原文地址：[https://jhalon.github.io/utilizing-syscalls-in-csharp-1/](https://jhalon.github.io/utilizing-syscalls-in-csharp-1/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0130b4360a2c04a3f6.png)](https://p1.ssl.qhimg.com/t0130b4360a2c04a3f6.png)



## 前言

这篇文章介绍了一些在中使用syscall需要了解的基本概念，其中触及了一些比较深入的主题，例如Windows内部结构及系统调用的概念，还讨论了.NET 框架的工作原理以及如何在C#中利用非托管代码执行syscall汇编代码。

在过去的一年，安全社区，特别是在红队的渗透以及蓝队的防御中，发现有大量Windows恶意软件公开或私有地利用了[System Calls(系统调用)](https://docs.microsoft.com/en-us/cpp/c-runtime-library/system-calls?view=vs-2019)，有些是用于post-exploitation，还有的是为了绕过[EDR(终端检测与响应)](https://www.crowdstrike.com/epp-101/what-is-endpoint-detection-and-response-edr/)。

目前，该技术的使用对于一些人来说可能比较陌生，但事实并非如此。 这些年来，许多恶意软件作者，开发人员甚至游戏黑客都一直在内存加载过程中使用系统调用技术。 他们最初的目的是为了绕过反病毒或反作弊引擎等工具带来的特定限制或安全措施。

在一些博客文章中已经很好地介绍了如何利用这些syscall技术，比如说[Hoang Bui](https://twitter.com/SpecialHoang)的这篇文章&lt;a href=”https://medium.com/[@fsx30](https://github.com/fsx30)/bypass-edrs-memory-protection-introduction-to-hooking-2efb21acffd6″&gt;Bypass EDR’s Memory Protection, Introduction to Hooking，还有[Cneelis](https://twitter.com/Cneelis)的[Red Team Tactics: Combining Direct System Calls and sRDI to bypass AV/EDR](https://outflank.nl/blog/2019/06/19/red-team-tactics-combining-direct-system-calls-and-srdi-to-bypass-av-edr/)，这篇文章主要聚焦于如何利用syscall转储LSASS中的信息并且不会被检测到。这些技术的使用在红队的秘密行动中十分重要，因为它能够让我们在网络中不受监视地进行post exploitation。

大多数人在实现这些技术时使用了C++语言，这样能够更好地和[Win32 API](https://docs.microsoft.com/en-us/windows/win32/apiindex/windows-api-list)以及系统进行交互。不过在用C++编写工具的时候总会出现一个问题，那就是代码编译完成之后会生成一个EXE文件。而我们为了让秘密行动能够成功进行，总是希望能避免“接触硬盘”，也就是说我们不想盲目地复制或者执行系统上的文件。所以说，我们要找到一种更安全的方法将这些工具注入到内存中。

尽管C ++对于任何恶意软件相关技术都是一个很棒的语言，但由于我已经开始使用C#编写post-exploitation工具了，所以我打算在C#中实现syscall的使用。而在[FuzzySec](https://twitter.com/FuzzySec)和[The Wover](https://twitter.com/TheRealWover)发布了他们在BlueHatIL 2020上的演讲（[Staying # and Bringing Covert Injection Tradecraft to .NET](https://github.com/FuzzySecurity/BlueHatIL-2020%5D)）之后，我更加迫切地想要实现这一目标。

为此，我进行了很多艰苦的研究，也经历了很多失败，在无数个与咖啡相伴的夜晚之后，我终于成功地让syscall在C＃中正常工作了。虽然这一技术对于红队的行动来说十分有帮助的，但是代码却有些复杂，你很快就会明白我为什么这么说了。

总的来说，这次系列博客的重点是探讨如何在C#中利用非托管代码直接进行系统调用，从而绕过EDR以及API Hooking。

但在开始编写代码之前，我们必须先了解一些基础知识。比如说系统调用的工作原理以及一些.NET中的概念（特别是托管和非托管代码的区别，P/Invoke以及delegate）。 只有理解了这些基础内容，才能明白我们最终编写的C＃代码的工作原理以及其正常工作的原因。

好吧，闲话少说，现在开始基础知识的介绍！



## 理解系统调用的概念

在Windows中，进程的体系结构分为两种处理器访问模式——**用户模式(user mode)**和**内核模式(kernel mode)**。 这两种模式是为了保护用户应用程序免于访问和修改任何重要的系统数据。 用户应用程序（例如Chrome，Word等）均在用户模式下运行，而系统代码（例如系统服务和设备驱动程序）均在内核模式下运行。

[![](https://p0.ssl.qhimg.com/t018b48b2f04cb38ccd.png)](https://p0.ssl.qhimg.com/t018b48b2f04cb38ccd.png)

在内核模式下，处理器允许程序访问**所有系统内存**以及**所有CPU指令**。有一些x86和x64的处理器也使用**ring levels**这样的术语来区分这两种模式。

使用ring level特权模式的处理器定义了四个特权级别（**rings**）来保护系统代码和数据。下图是一个ring levels的示例。

[![](https://p3.ssl.qhimg.com/t0173b3f7658f0bb4e4.png)](https://p3.ssl.qhimg.com/t0173b3f7658f0bb4e4.png)

Windows只使用其中的两个级别：Ring0表示内核模式，Ring3表示用户模式。在处理器正常运行期间，处理器会根据其上运行的代码类型在这两种模式之间进行切换。

那么，这种ring level背后的安全机制是什么呢？当你启动了一个用户模式下的应用程序时，Windows会为该程序创建一个新进程，并提供一个私有的[虚拟地址空间](https://docs.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/virtual-address-spaces)以及一个私有的[句柄表(handle table)](https://flylib.com/books/en/4.419.1.29/1/)。

该“**句柄表**”是一个包含了[句柄](https://docs.microsoft.com/en-us/windows/win32/sysinfo/handles-and-objects)的**内核对象**。句柄是对特定系统资源（例如内存区域/位置，打开的文件或管道）的抽象引用值，它最初的目的是为了向使用API的用户隐藏真实的内存地址，这样就能让系统执行某些管理功能，比如说重组物理内存。

总的来说，句柄的工作为了指代内部结构，例如：令牌，进程，线程等。下图是一个句柄的示例。

[![](https://p1.ssl.qhimg.com/t012058caef41ee0ef3.png)](https://p1.ssl.qhimg.com/t012058caef41ee0ef3.png)

因为应用程序的虚拟地址空间是私有的，所以一个程序不能修改另一个程序的数据，除非后者通过[文件映射](https://docs.microsoft.com/en-us/windows/win32/memory/file-mapping)或[VirtualProtect](https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect?redirectedfrom=MSDN)函数将其一部分私有地址空间用作共享内存，或者前者有权限打开另一个进程并使用跨进程内存函数，例如[ReadProcessMemory](https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-readprocessmemory)和[WriteProcessMemory](https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory)。

[![](https://p2.ssl.qhimg.com/t01b38886af1341567e.png)](https://p2.ssl.qhimg.com/t01b38886af1341567e.png)

和用户模式不同，所有在内核模式下运行的代码都共享一个称为**系统空间**的虚拟地址空间。这就表明内核模式下的驱动程序和其他驱动程序以及操作系统本身之间并不是隔离的。因此，如果有一个驱动程序不小心写入了错误的地址空间或执行了恶意操作，就可能会损害系统或其他驱动程序。尽管也存在一些防止上述操作的保护手段，例如[Kernel Patch Protection](https://en.wikipedia.org/wiki/Kernel_Patch_Protection)，即Patch Guard，但现在先不考虑这些内容。

由于内核中包含了大部分操作系统的内部数据结构（比如或句柄表），所以用户模式下的应用程序在访问这些数据结构或调用内部Windows例程以执行特权操作（例如读取文件）的时候，必须先从用户模式切换到内核模式。这里就需要用到**系统调用**了。

为了让用户应用程序能够在内核模式下访问这些数据结构，进程使用了一个特殊的处理器指令触发器，叫做“ **syscall**”。该指令触发了处理器访问模式的转换，并允许处理器访问内核中的系统服务调用代码。该代码会调用[Ntoskrnl.exe](https://en.wikipedia.org/wiki/Ntoskrnl.exe)或者**Win32k.sys**中相应的内部函数，这两者包含了内核和系统程序级别的执行逻辑。

这种“转换”的例子可以在任何应用程序中观察到。比如说，如果使用[Process Monitor](https://docs.microsoft.com/en-us/sysinternals/downloads/procmon)观察Notepad程序，我们可以查看特定读/写操作的属性以及它们的调用堆栈。

[![](https://p5.ssl.qhimg.com/t0100ba41a12b0892f2.jpg)](https://p5.ssl.qhimg.com/t0100ba41a12b0892f2.jpg)

上图中，我们可以看到从用户模式到内核模式的转换。注意到Win32 API [CreateFile](https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea)函数的调用就在Native(原生) API [NtCreateFile](https://docs.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntcreatefile)的调用之前的。

但是如果我们仔细观察的话，会发现一些奇怪的现象。注意里面有两个不同的**NtCreateFile**函数调用。一个来自**ntdll.dll**模块，另一个来自**ntoskrnl.exe**模块。为什么会这样呢？

其实答案很简单。**ntdll.dll**导出了Windows [Native API](https://en.wikipedia.org/wiki/Native_API)，而这些来自ntdll的Native API的具体实现则存在于ntoskrnl中，你可以把它们当作“内核API”。Ntdll专门支持用于执行功能的函数以及系统服务调用存根。

简而言之，这两个模块内部包含了“**syscall**”的逻辑，让处理器能够从用户模式转换到内核模式！

那么这个CPU指令syscall在ntdll中是什么样子的呢？我们可以使用[WinDBG](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/debugger-download-tools)来反汇编并检查ntdll中的调用函数。

首先，启动WinDBG并打开一个类似notepad或cmd这样的进程。打开之后，在命令窗口中键入以下内容：

```
x ntdll!NtCreateFile
```

这句话告诉WinDBG我们想要**检查**（x, examine）已加载的**ntdll**模块中的**NtCreateFile**符号。这句命令执行完后，会得到输出：

```
00007ffd`7885cb50 ntdll!NtCreateFile (NtCreateFile)
```

该输出指的是NtCreateFile在已加载进程中的内存地址。如果想要查看这里的反汇编代码，需要键入以下命令：

```
u 00007ffd`7885cb50
```

该命令告诉WinDBG我们想要**反汇编**（u, unassemble）指定的内存范围开头处的指令。 如果运行正确，我们现在应该可以看到以下输出。

[![](https://p4.ssl.qhimg.com/t01f034cc02c6ba1b71.jpg)](https://p4.ssl.qhimg.com/t01f034cc02c6ba1b71.jpg)

总的来说，ntdll中的NtCreateFile函数首先负责在堆栈上设置函数调用参数。完成后，该函数需要将其相关的系统调用号移入`eax`中，如第二条指令`mov eax 55`所示。在此例中，NtCreateFile的系统调用号为0x55。

每个原生函数都有一个特定的系统调用号，目前该数字通常会随着每次更新发生变化，所以有时很难对其进行追踪。不过要感谢来自Google Project Zero的[j00ru](https://twitter.com/j00ru)，他在持续更新一份[Windows X86-64系统调用表](https://j00ru.vexillium.org/syscalls/nt/64/)。因此如果出现新的更新后，你可以把该表作为参考。

系统调用号移入`eax`之后，会执行**syscall**指令，CPU会在这里进入内核模式并执行指定的特权操作。

为此，它会把函数调用参数从用户模式堆栈复制到内核模式堆栈，然后执行内核版本的函数调用，即[ZwCreateFile](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-zwcreatefile)。执行完后，该例程会反向，并且所有返回值都会返回到用户模式下的程序中。syscall到这里就结束了！



## 直接使用系统调用

现在我们知道系统调用的工作原理以及结构了，但你可能会问自己……我们如何执行这些系统调用呢？

其实很简单。为了能够直接引入系统调用，我们可以使用汇编语言对其进行构建，并在程序内存空间中进行执行！这样我们就能绕过EDR或反病毒软件监控的所有挂钩函数。 当然，这并不是说syscall就不能被监控了，而且使用C#执行syscall仍旧会留下一些足迹，但这些内容不在本篇文章的讨论范围之内。

比如说，如果我们想编写一个调用**NtCreateFile**函数的syscall程序，就可以构建下述汇编代码：

```
mov r10, rcx
mov eax, 0x55 &lt;-- NtCreateFile Syscall Identifier
syscall
ret
```

现在我们有了syscall的汇编代码…接下来呢？ 我们如何在C#中执行它呢？

使用C ++执行该代码很简单，直接将其添加到一个新的`.asm`文件中，启用[masm](https://docs.microsoft.com/en-us/cpp/assembler/masm/masm-for-x64-ml64-exe?view=vs-2019)依赖，定义该代码的C函数原型(prototype)，并初始化调用该syscall所需的变量以及结构即可。

听起来似乎很简单，但在C#中却并不容易。为什么呢？ 四个字——**托管代码**。



## 理解C#以及.NET框架

在深入了解“**托管代码**”的含义以及它为什么会带来这么大的麻烦之前，我们需要理解C#是什么及其如何在.NET框架上运行。

简单来说，C#是一种类型安全的面向对象语言，开发人员能够用它构建各种安全而强大的应用程序。它的语法简化了C++的复杂性，并提供了很多强大的功能，例如nullable类型，枚举（enumeration），委托（delegate），lambda表达式以及直接内存访问。C#还可以在.NET框架上运行，该框架是Windows中一个不可或缺的组件，它包含一个叫做“[公共语言运行时环境(CLR, Common Language Runtime)](https://docs.microsoft.com/en-us/dotnet/standard/clr)”的虚拟运行系统以及一组统一的类库。CLR是Microsoft的[公共语言基础结构（CLI, Common Language Infrastructure）](https://en.wikipedia.org/wiki/Common_Language_Infrastructure)的一个商业实现。

用C#编写的源代码会被编译成符合CLI规范的[中间语言（IL）](https://docs.microsoft.com/en-us/dotnet/standard/managed-code)。IL代码和资源（例如位图和字符串）存储在磁盘上的可执行文件中，该可执行文件称为程序集(assembly)，扩展名通常为`.exe`或`.dll`。

在执行C#程序的时候，程序集被加载到CLR中，CLR进行[即时（JIT）](https://docs.microsoft.com/en-us/dotnet/standard/managed-execution-process)编译，把IL代码转换为机器码。 CLR还提供其他服务，例如自动[垃圾收集](https://docs.microsoft.com/en-us/dotnet/standard/garbage-collection/fundamentals)，异常处理和资源管理。与“**非托管代码**”相对，CLR执行的代码有时被称为“**托管代码**”，前者直接编译成了特定系统的机器码。

简单来说，托管代码就是由运行时环境管理执行的代码。在这种情况下，运行时环境指的是**公共语言运行时环境**。

在非托管代码中，它只和C/C++有关，程序员几乎负责所有事情。最后得到的程序本质上是一个二进制文件，操作系统负责将其加载到内存中并启动。其他涉及到内存管理到安全方面的问题，都是程序员的责任。

下图是.NET框架结构的可视化示例，它展示框架如何将C#编译为IL，然后转变成机器码的过程。

[![](https://p0.ssl.qhimg.com/t016665a087fbd255e7.png)](https://p0.ssl.qhimg.com/t016665a087fbd255e7.png)

如果你真的阅读了上面的所有内容，你可能会注意到我提到了CLR还提供其他服务，例如“**垃圾收集**”。在CLR中，垃圾收集器（**GC**）实质上是通过“释放垃圾”（即已使用的内存）来实现自动内存管理器的。 除此之外，它还能够在托管堆上分配和回收对象，清除内存，并阻止已知的内存泄露问题（如[Use After Free](https://cwe.mitre.org/data/definitions/416.html)）从而保证内存安全。

尽管C#是一门伟大的语言，并且提供了许多很棒的功能并且具有和Windows的互操作性（例如in-memory execution），但是在编写恶意软件或尝试与系统进行交互的时候，它确实存在一些问题，比如说：
1. 使用类似[dnSpy](https://github.com/0xd4d/dnSpy)的工具可以很容易地反汇编C#程序集并对其进行逆向工程，因为它们被编译成了IL代码而不是原生的机器码。
1. 它只有系统上存在.NET时才能执行。
1. 在.NET中应用反调试技巧比在机器码中更加困难。
1. 需要更多的精力，编写更多的代码才能在托管代码和非托管代码之间进行互操作。
上述第四点在这次使用C#编写syscall的过程中带来了最多的麻烦。

不管我们在C#中做任何事都是“托管”的，那我们如何才能和Windows系统以及处理器进行有效交互呢？

因为我们要执行汇编代码，所以这个问题非常重要。但不幸的是，和C++不同，C#中不支持内联汇编以及masm依赖。

不过Microsoft为我们提供了一种能够做到这一点的方法！这一切都要归功于CLR！由于CLR的构造方式，它让我们能够越过托管与非托管世界之间的边界。这个过程就叫做**互操作性(interoperability)**或简称**互操作(interop)**。通过互操作，C#就能够支持指针以及“不安全”代码的概念，可以直接进行内存的访问了，也就是我们这里需要的功能！ 😉

总的来说，这就表示我们现在可以实现和C++一样的功能并使用相同的Windows API函数了……不过过程中可能存在很多……我的意思是……轻微的困难和不便之处…… 😅

还有一点需要注意，一旦代码越过了运行时环境的边界，对执行的实际管理会再次落在非托管代码的手上，因此将受到与使用C++进行编程时相同的限制。所以，我们需要在分配、回收以及管理内存和其他对象时格外地小心。

知道了这一点之后，我们如何在C#中启用这种互操作性呢？这时就需要[Platform Invoke(P/Invoke)](https://docs.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke)了！



## 通过P/Invoke理解互操作

P/Invoke是一项允许你从托管代码中访问非托管库（即DLL这样的文件）中的结构、回调以及函数的技术。大多数允许这种互操作性的P/Invoke API都包含在两个命名空间中，即[System](https://docs.microsoft.com/en-us/dotnet/api/system?view=netframework-4.8)和[System.Runtime.InteropServices](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.interopservices?view=netframework-4.8)。

我们看一个简单的例子：假设你想在C#代码中使用[MessageBox](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messagebox)函数——一般来说，除非你正在构建一个[UWP](https://docs.microsoft.com/en-us/windows/uwp/get-started/universal-application-platform-guide)应用，否则是无法调用该函数的。

首先，先创建一个新的`.cs`文件，并确保包含了上面的两个P/Invoke命名空间。

```
using System;
using System.Runtime.InteropServices;

public class Program
`{`
    public static void Main(string[] args)
    `{`
        // TODO
    `}`
`}`
```

现在，看一下我们要使用的MessageBox在C中的语法。

```
int MessageBox(
  HWND    hWnd,
  LPCTSTR lpText,
  LPCTSTR lpCaption,
  UINT    uType
);
```

对于初学者来说，你必须知道C++和C#中使用的数据类型并不匹配。这就表示，类似[HWND](https://docs.microsoft.com/en-us/windows/win32/winprog/windows-data-types)（窗口句柄）和[LPCTSTR](https://docs.microsoft.com/en-us/windows/win32/winprog/windows-data-types)（指向常量TCHAR字符串的长指针）这样的数据类型在C#中是无效的。

为了方便理解，接下来简单介绍一下怎样转换MessageBox中的这些数据类型。如果你想了解更多信息，那么我建议你阅读这篇文章[C# Types and Variables](https://docs.microsoft.com/en-us/dotnet/csharp/tour-of-csharp/types-and-variables)。

对于C++中的任何句柄对象（例如HWND），C#中和该数据类型（以及C++中的指针）等效的是[IntPtr结构](https://docs.microsoft.com/en-us/dotnet/api/system.intptr?view=netframework-4.8)，它是一种针对特定平台的类型，用于表示指针或句柄。

C++中的任意字符串或指向字符串的指针都能被设置为该等效结构（其实就是[字符串](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/strings/)）。至于UINT或无符号整数类型，在C#中保持不变。

现在我们已经知道了不同的数据类型，接下来需要在代码中调用非托管的MessageBox函数。

代码如下所示：

```
using System;
using System.Runtime.InteropServices;

public class Program
`{`
    [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern int MessageBox(IntPtr hWnd, string lpText, string lpCaption, uint uType);

    public static void Main(string[] args)
    `{`
        // TODO
    `}`
`}`
```

注意到，在导入非托管函数之前，我们还使用了[DllImport](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.dllimportattribute?view=netframework-4.8)属性。该属性十分重要，因为它告诉了运行时环境应该加载非托管DLL。传入的字符串表示要加载的目标DLL，在此例中为**user32.dll**，该文件包含了MessageBox的函数逻辑。

除此之外，我们还指定了用于编码该字符串的[字符集](https://docs.microsoft.com/en-us/dotnet/standard/native-interop/charset)，设置了[SetLastError](https://docs.microsoft.com/en-us/windows/desktop/api/errhandlingapi/nf-errhandlingapi-setlasterror)参数，这样如果函数执行失败，运行时环境能够捕获该错误代码，以便用户之后通过[Marshal.GetLastWin32Error()](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.getlastwin32error#System_Runtime_InteropServices_Marshal_GetLastWin32Error)检索错误信息。

最后，我们使用[extern](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/extern)关键字创建了一个私有的静态MessageBox函数。该`extern`修饰符用于声明在外部实现的方法。它告诉了运行时环境，在调用这个函数的时候，应在`DllImport`属性中指定的DLL中寻找该函数，在此例中函数位于**user32.dll**。

有了上述代码，我们就能够在主程序中调用`MessageBox`函数了。

```
using System;
using System.Runtime.InteropServices;

public class Program
`{`
    [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern int MessageBox(IntPtr hWnd, string lpText, string lpCaption, uint uType);

    public static void Main(string[] args)
    `{`
        MessageBox(IntPtr.Zero, "Hello from unmanaged code!", "Test!", 0);
    `}`
`}`
```

如果运行正常，上述代码应该会弹出一个标题为“**Test!**”，内容为“**Hello from unmanaged code!**”的消息框。

现在我们已经学会了如何在C#中导入并调用非托管代码！如果只是看代码的话，这个方法看起来非常简单……但是不要让它蒙骗了你！

这只是一个简单的函数，如果我们要调用一个更加复杂的函数呢？比如说[CreateFileA](https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea)函数，这时会发生什么？

先来看一下该函数在C中的语法。

```
HANDLE CreateFileA(
  LPCSTR                lpFileName,
  DWORD                 dwDesiredAccess,
  DWORD                 dwShareMode,
  LPSECURITY_ATTRIBUTES lpSecurityAttributes,
  DWORD                 dwCreationDisposition,
  DWORD                 dwFlagsAndAttributes,
  HANDLE                hTemplateFile
);
```

先看一下`dwDesiredAccess`参数，该参数使用通用值（如**GENERIC_READ**和**GENERIC__WRITE**）指定了要创建文件的访问权限。在C++中，只要使用这些通用值，系统就会知道我们的意思，但在C#中就不行。

在文档中，我们发现用于`dwDesiredAccess`参数的[通用访问权限(Generic Access Rights)](https://docs.microsoft.com/en-us/windows/win32/secauthz/generic-access-rights)使用了某种[访问掩码格式(Access Mask Format)](https://docs.microsoft.com/en-us/windows/win32/secauthz/access-mask-format)来指定赋予该文件的权限。由于该参数的类型为[DWORD](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-dtyp/262627d8-3418-4627-9218-4ffe110850b2)，即32位无符号整数，因此该**GENERIC- **格式的常量实际上就是用来和特定的访问掩码位值进行匹配的标志。

要想在C#中实现相同的目的，我们必须使用[FLAGS](https://docs.microsoft.com/en-us/dotnet/api/system.flagsattribute?view=netframework-4.8)枚举属性创建一个新的[结构类型(structure type)](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/struct)，该类型中包含了与C++相同的常量以及数值，这样该函数才能正常工作。

现在你可能会问我，我在哪里能够获取到这些详细信息呢？如果想要在.NET中进行非托管代码的管理，最适合的资源就是[PInvoke Wiki](https://www.pinvoke.net/)。你几乎可以在这里找到所需的任何信息。

如果我们要在C#中调用该非托管函数并使其正常工作，代码示例如下所示：

```
using System;
using System.Runtime.InteropServices;

public class Program
`{`
    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    public static extern IntPtr CreateFile(
        string lpFileName,
        EFileAccess dwDesiredAccess,
        EFileShare dwShareMode,
        IntPtr lpSecurityAttributes,
        ECreationDisposition dwCreationDisposition,
        EFileAttributes dwFlagsAndAttributes,
        IntPtr hTemplateFile);

    [Flags]
    enum EFileAccess : uint
    `{`
        Generic_Read = 0x80000000,
        Generic_Write = 0x40000000,
        Generic_Execute = 0x20000000,
        Generic_All = 0x10000000
    `}`

    public static void Main(string[] args)
    `{`
        // TODO Code Here for CreateFile
    `}`
`}`
```

现在你知道我之前为什么会说在C#中使用非托管代码很麻烦了吧？很好，现在我们的观点一致了😁。

到目前为止，我们已经介绍了很多内容。我们知道了系统调用的工作原理，了解了C#和.NET框架在较低级层次上的工作方式，现在我们也学会了如何在C#中调用非托管代码以及Win32 API。

但是我们仍然缺少一个重要信息，是什么呢…🤔

哦，对了！即使我们能够在C#中调用Win32 API函数，但还是不知道怎么执行我们的汇编“[native code](https://stackoverflow.com/questions/3434202/what-is-the-difference-between-native-code-machine-code-and-assembly-code)（原生代码）“。

好吧，正如古人所说，有志者事竟成！尽管不能像C++那样在C#中使用内联汇编，我们也可以通过可爱的[Delegates](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/delegates/)来达到类似的目的！



## 理解Delegates以及native code回调的概念

在此之前，我们可以停一秒钟，然后欣赏一下CLR到底有多酷吗？ 我的意思它既能管理代码，也能允许垃圾收集器和Windows API之间的互操作。

除此之外，它还允许双向地通信，这就表示你可以使用函数指针从原生函数回调到托管代码！在托管代码中最接近函数指针这一概念的就是[委托(delegate)](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/delegates/)，该类型代表了对具有特定参数列表和返回类型的方法的引用。在从原生代码回调到托管代码的时候就要使用该类型。

简单来说，委托用于将方法作为参数传递给其他方法。该功能的使用和从托管代码进入非托管代码的过程类似。Microsoft对此给出了一个很好的例子。

```
using System;
using System.Runtime.InteropServices;

namespace ConsoleApplication1
`{`
    public static class Program
    `{`
        // Define a delegate that corresponds to the unmanaged function.
        private delegate bool EnumWindowsProc(IntPtr hwnd, IntPtr lParam);

        // Import user32.dll (containing the function we need) and define
        // the method corresponding to the native function.
        [DllImport("user32.dll")]
        private static extern int EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

        // Define the implementation of the delegate; here, we simply output the window handle.
        private static bool OutputWindow(IntPtr hwnd, IntPtr lParam)
        `{`
            Console.WriteLine(hwnd.ToInt64());
            return true;
        `}`

        public static void Main(string[] args)
        `{`
            // Invoke the method; note the delegate as a first parameter.
            EnumWindows(OutputWindow, IntPtr.Zero);
        `}`
    `}`
`}`
```

这段代码看起来可能有些复杂，但相信我，事实并非如此！在研究该代码之前，首先确保我们已经了解了需要使用的非托管函数的签名。

如你所见，我们在代码中导入原生代码函数[EnumWindows](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-enumwindows)，该函数会枚举屏幕上的所有顶级窗口，这些窗口的句柄会依次传递给应用程序定义的回调函数。

该函数在C中的语法如下所示：

```
BOOL EnumWindows(
  WNDENUMPROC lpEnumFunc,
  LPARAM      lParam
);
```

如果查看文档中的`lpEnumFunc`参数，会发现它接收一个指向应用程序定义的回调函数的指针，该函数的结构与[EnumWindowsProc](https://docs.microsoft.com/en-us/previous-versions/windows/desktop/legacy/ms633498(v=vs.85))回调函数相同。由于这里只是对程序定义函数的一个占位名称，所以我们可以在程序中任意对其进行命名。

该函数在C中的语法如下所示：

```
BOOL CALLBACK EnumWindowsProc(
  _In_ HWND   hwnd,
  _In_ LPARAM lParam
);
```

该函数接受一个HWND（窗口句柄）以及一个LPARAM（长指针）作为参数。该回调函数的返回值是一个布尔值，用true或false表示枚举何时停止。

现在回到示例代码，在第9行我们定义了与非托管代码中的回调函数签名一致的**delegate**。由于代码是用C#编写的，因此需要把C++指针替换为**IntPtr**，该类型在C#中与指针等效。

第13行和第14行从**user32.dll**中引入了EnumWindows函数。

接下来，第17-20行实现了这个**delegate**。在这里，我们真正告诉了C#要如何处理从非托管代码返回的数据。在此例中，只是简单地把返回的值打印到控制台上。

最后，第24行调用了导入的原生方法，并将定义并实现好的delegate传入其中，用于处理返回的数据。

很简单吧！

好的，这很酷。而且我也知道……你可能会问我，“**杰克，这和在C#中执行原生汇编代码有什么关系呢？我还是不知道怎么做！**”

在这里，我只想说…

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019b1d9390e67b4e03.jpg)

我之所以想先介绍委托(delegate)和原生代码回调这两个概念，是因为在接下来的介绍中，委托非常重要。

现在我们已经知道委托和C++的函数指针类似，但是委托是完全面向对象的，而且与指向成员函数的C++指针不同，它既封装了对象实例也封装了方法。除此之外，我们还知道它可以让方法作为参数传递，也可以用于定义回调方法。

由于委托十分善于处理接收到的数据，因此我们可以对这些数据进行进一步的处理。

比如说，假设我们执行一个原生Windows函数，像是[VirtualAlloc](https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualalloc)，该函数可以保留，提交或更改调用进程虚拟地址空间中部分页区域的状态，并会返回已分配内存区域的基地址。

这时，如果我们分配的空间中包含了shellcode呢😏？接下来会发生什么？没懂！？好…让我解释一下。

所以，如果我们能够在包含shellcode的进程中分配一个内存区域并将其返回给**delegate**，那么我们就可以利用一种叫做[type marshaling](https://docs.microsoft.com/en-us/dotnet/standard/native-interop/type-marshaling)的方法让传入的数据类型在托管代码和原生代码之间进行转换。这就表示我们可以从一个非托管的函数指针转换到委托类型！也就是说我们可以通过这种方式来执行汇编代码或shellcode的字节数组！

接下来在上述思路的基础上，进行进一步的探讨。



## Type Marshaling &amp; 不安全代码以及指针

正如之前所说，**marshaling**是一个在托管代码和原生代码发生转换时对类型进行转换的过程。 因为托管和非托管代码中的类型不同，所以需要进行marshaling。

默认情况下，P/Invoke子系统会根据默认行为尝试进行type marshaling。但是，如果你需要对非托管代码进行额外控制，就可以使用[Marshal](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal?view=netframework-4.8)类完成类似分配非托管内存，复制非托管内存块，将托管类型转换为非托管类型等操作，以及在与非托管代码进行交互时需要的其他复杂操作。

下面给出了marshaling工作原理的一个示例。

[![](https://p5.ssl.qhimg.com/t0158da06b41aca2972.png)](https://p5.ssl.qhimg.com/t0158da06b41aca2972.png)

在本文想要讨论的问题中，最重要的Marshal方法就是[Marshal.GetDelegateForFunctionPointer](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.getdelegateforfunctionpointer?view=netframework-4.8#System_Runtime_InteropServices_Marshal_GetDelegateForFunctionPointer_System_IntPtr_System_Type_)，该方法可以把非托管函数指针转换为指定类型的委托。

可以使用marshaling在很多类型间进行转换，我强烈建议你仔细阅读这部分内容，因为它是.NET框架中不可或缺的一部分。而且在编写红队或者蓝队使用的工具时，都会很方便。

现在我们已经知道可以把内存指针转换为委托了，但问题在于，我们怎样才能创建出指向汇编代码的内存指针呢？事实上这很容易，只需要进行一些简单的指针运算就能得到ASM代码的内存地址了。

由于C#默认情况下不支持指针算术，因此我们需要把代码的一部分声明为[不安全的](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/unsafe)。该操作只表示一个不安全的上下文，只要内容涉及到指针，都需要进行该操作。总的来说，这样我们就能够进行指针操作了，比如说指针解引用。

现在唯一的问题就是，如果想要编译不安全的代码，就必须在编译时使用`-unsafe`选项。

因此，让我们来看一个简单的例子。

如果我们想对[NtOpenProcess](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-ntopenprocess)执行syscall，首先要做的就是像下面这样将汇编代码写入字节数组。

```
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;

namespace SharpCall
`{`
    class Syscalls
    `{`

        static byte[] bNtOpenProcess =
        `{`
            0x4C, 0x8B, 0xD1,               // mov r10, rcx
            0xB8, 0x26, 0x00, 0x00, 0x00,   // mov eax, 0x26 (NtOpenProcess Syscall)
            0x0F, 0x05,                     // syscall
            0xC3                            // ret
        `}`;
    `}`
`}`
```

在填写完该字节数组之后，我们需要使用`unsafe`关键字指出出现不安全上下文的代码区域。

我们可以在该不安全上下文中进行一些指针运算。在下面的代码中，我们初始化了一个名为`ptr`的字节指针，并将其设置为`syscall`的值，该位置包含了汇编字节数组。之后还使用了[fixed](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/fixed-statement)语句，该语句能够防止垃圾回收器重新定位可移动变量，在本例中指的就是syscall字节数组。

如果没有使用`fixed`语句，垃圾回收器可能会对变量进行重定位，导致执行过程中出错。

接下来，我们把字节数组指针转换为一个叫做`memoryAddress`的C# IntPtr类型。这样我们就能够获取到syscall字节数组所在的内存位置了。

这时就可以做很多事情了，比如说在原生API调用中使用该内存区域，或者可以将其传递给其他托管C#函数，甚至可以在委托中使用该内存区域！

针对以上内容，给出一个示例代码。

```
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;

namespace SharpCall
`{`
    class Syscalls
    `{`
        // NtOpenProcess Syscall ASM
        static byte[] bNtOpenProcess =
        `{`
            0x4C, 0x8B, 0xD1,               // mov r10, rcx
            0xB8, 0x26, 0x00, 0x00, 0x00,   // mov eax, 0x26 (NtOpenProcess Syscall)
            0x0F, 0x05,                     // syscall
            0xC3                            // ret
        `}`;

        public static NTSTATUS NtOpenProcess(
            // Fill NtOpenProcess Paramters
            )
        `{`
            // set byte array of bNtOpenProcess to new byte array called syscall
            byte[] syscall = bNtOpenProcess;

            // specify unsafe context
            unsafe
            `{`
                // create new byte pointer and set value to our syscall byte array
                fixed (byte* ptr = syscall)
                `{`
                    // cast the byte array pointer into a C# IntPtr called memoryAddress
                    IntPtr memoryAddress = (IntPtr)ptr;
                `}`
            `}`
        `}`
    `}`
`}`
```

到此为止，我们已经知道如何在C#程序中从字节数组获取并执行Shellcode了，该过程使用了非托管代码，不安全上下文，委托以及marshaling等技术。

我知道涉及到的内容有点多，而且老实讲，一开始看到的时候也会比较复杂。所以请花些时间阅读这篇文章并确保你已经理解了这些概念。

在下一篇文章中，我们会专注于实际编写代码，利用在本文中学到的内容，实现一个有效的syscall。 除了编写代码外，我们也会介绍如何对“工具”代码进行管理，以及如何为之后与其他工具的集成做准备。

感谢阅读，敬请关注第2部分！
