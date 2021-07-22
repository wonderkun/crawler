> 原文链接: https://www.anquanke.com//post/id/209911 


# 滥用方法VS检测手段：深入探究Windows硬件断点和异常


                                阅读量   
                                **156545**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ling，文章来源：ling.re
                                <br>原文地址：[https://ling.re/hardware-breakpoints/](https://ling.re/hardware-breakpoints/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t012a4833505918258a.png)](https://p4.ssl.qhimg.com/t012a4833505918258a.png)



## 0. 前言

与常规断点不同，硬件断点主要用于调试目的，它们不需要任何代码修改，并且具有更多功能。因此，在对使用了反调试策略的目标进行调试的过程中，会经常用到这种方法。在本文中，将详细介绍Windows上硬件断点的内部工作原理，并介绍一些常用用法和检测方法。

本文中的研究过程是在64位Windows 10 20H1上进行的。在32位Windows上，某些技术可能非常相似，但不作为本文的重点进行阐述。并且，由于体系结构的差异，这些技术在其他操作系统上（例如Linux和macOS）可能会相差较大。



## 1. 调试寄存器快速入门

熟悉调试寄存器的读者可以跳至2.0章。

硬件断点同时适用于x86和x64架构，它是通过8个调试寄存器（分别称为DR0到DR7）来实现的。这些寄存器在x86和x64架构上的长度分别为32位和64位。下图展示了x64架构上的寄存器布局。如果大家觉得这个布局有些难懂，请不要担心，我们将在后面详细介绍每个寄存器。如果想要了解有关调试寄存器的更多信息，建议参考Intel SDM和AMD APM，这些都是不错的资源。

x64上调试寄存器的布局：

[![](https://p1.ssl.qhimg.com/t012d2279d5b31ea48a.jpg)](https://p1.ssl.qhimg.com/t012d2279d5b31ea48a.jpg)

### <a class="reference-link" name="1.1%20DR0-DR3"></a>1.1 DR0-DR3

DR0到DR3被称为“调试地址寄存器”或“地址断点寄存器”，它们非常简单，其中仅包含断点的线性地址。当该地址与指令或数据引用匹配时，将发生中断。调试寄存器DR7可用于对每个断点的条件进行更细粒度的控制。因为寄存器需要填充线性地址，所以即使关闭分页，它们也可以正常工作。在这种情况下，线性地址将与物理地址相同。

由于这些寄存器中只有4个是可用的，因此每个线程最多只能同时具有4个断点。

### <a class="reference-link" name="1.2%20DR4-DR5"></a>1.2 DR4-DR5

DR4和DR5被称为“保留的调试寄存器”。尽管它们的名称中有“保留”字样，但实际上却不总是保留的，仍然可以使用。它们的功能取决于控制寄存器CR4中`DE`字段的值。在启用此位后，将启用I/O断点，如果尝试访问其中一个寄存器将会导致`#UD`异常。但是，如果未启用`DE`位时，调试寄存器DR4和DR5分别映射到DR6和DR7.这样做的目的是为了与旧版本处理器的软件相兼容。

### <a class="reference-link" name="1.3%20DR6"></a>1.3 DR6

在触发硬件断点时，调试状态存储在调试寄存器DR6中。也正因如此，该寄存器被称为“调试状态寄存器”。其中包含用于快速检查某些事件是否被触发的位。<br>
第0-3位是根据触发的硬件断点而进行设置，可以用于快速检查触发了哪个断点。

第13位称为`BD`，如果由于访问调试寄存器而触发当前异常，则会将其置为1。必须在DR7中启用`GD`位，才能触发此类异常。

第14位称为`BS`，如果由于单个步骤而触发当前异常，则会设置这一位。必须在`EFLAGS`寄存器中启用TF标志，才能触发此类异常。

第15位称为`TS`，如果由于当前任务切换到了启用调试陷阱标志的任务而触发了当前异常，则会设置这一位。

### <a class="reference-link" name="1.4%20DR7"></a>1.4 DR7

DR7被称为“调试控制寄存器”，允许对每个硬件断点进行精细控制。其中，前8位控制是否启用了特定的硬件断点。偶数位（0、2、4、6）称为L0-L3，在本地启用了断点，这意味着仅在当前任务中检测到断点异常时才会触发。奇数位（1、3、5、7）称为G0-G3，在全局启用了断点，这意味着在任何任务中检测到断点异常时都会触发。如果在本地启用了断点，则在发生硬件任务切换时会删除相应的位，以避免新任务中出现不必要的断点。在全局启用时不会清除这些位。<br>
第8位和第9位分别称为`LE`和`GE`，是沿用的传统功能，在现代处理器上无法执行任何操作。这些位用于指示处理器检测断点发生的确切指令。在现代处理器上，所有断点条件都是精确的。为了与旧硬件兼容，建议始终将这两个位都设置为1。

第13位被称为`GD`，这一位非常值得关注。如果这一位被启用，则当每一条指令尝试访问调试寄存器时，都会生成调试异常。为了将这种类型的异常与普通的硬件断点异常区分开来，在调试寄存器DR6中设置了`BD`标志。这一位通常用于阻止程序干扰调试寄存器。关键点在于，异常发生在指令执行之前，并且当进入调试异常处理程序时，该标志会被处理器自动删除。但是，这样的解决方案并不完美，因为它只能使用MOV指令来访问调试寄存器。这些在用户模式下是不可访问的，并且根据我的测试，`GetThreadContext`和`SetThreadContext`函数不会触发该事件。这样一来，这种检测就无法在用户模式下使用。

第16-31位用于控制每个硬件断点的条件和大小。每个寄存器有4位，分为4个2位字段。前2位用于确定硬件断点的类型。仅能在指令执行、数据写入、I/O读写、数据读写时才能生成调试异常。仅有在启用了控制寄存器CR4的`DE`字段时，才启用I/O读写功能，否则这种情况是不确定的。大小可以使用后2位来控制，并用于指定特定地址处内存位置的大小。可用的大小有1字节、2字节、4字节和8字节。

### <a class="reference-link" name="1.5%20%E7%94%A8%E6%B3%95"></a>1.5 用法

调试寄存器的用法非常简单。有一些特定的指令，可以将内容从通用寄存器移动到调试寄存器，反之亦然。但是，这些指令只能在特权级别0上执行，否则会生成`#GP(0)`异常。为了允许用户模式应用程序更改调试寄存器，Windows使用`SetThreadContext`和`GetThreadContext`API以支持对这些寄存器的更改。下面的代码片段演示了这些函数的示例用法。

```
/* Initialize context structure */
CONTEXT context = `{` 0 `}`;
context.ContextFlags = CONTEXT_ALL;

/* Fill context structure with current thread context */
GetThreadContext(GetCurrentThread(), &amp;context);

/* Set a local 1-byte execution hardware breakpoint on 'test_func' */
context.Dr0 = (DWORD64)&amp;test_func;
context.Dr7 = 1 &lt;&lt; 0;
context.ContextFlags = CONTEXT_DEBUG_REGISTERS;

/* Set the context */
SetThreadContext(GetCurrentThread(), &amp;context);
```



## 2. Windows异常

在分析了如何使用硬件断点之后，我们来看看Windows如何处理它们。

`ntoskrnl`中的中断表片段：

[![](https://p4.ssl.qhimg.com/t01d754fddc166510fa.png)](https://p4.ssl.qhimg.com/t01d754fddc166510fa.png)

在触发硬件断点时，无论是什么原因，都会触发`#DB`异常。这对应着（interrupt #1），会将执行重定向到中断处理程序1。想了解有关如何处理异常的更多信息，我建议参考阅读Daax撰写的这篇文章：[https://revers.engineering/applied-re-exceptions/](https://revers.engineering/applied-re-exceptions/) 。

在Windows中，每个中断处理程序在启动时都会初始化。而对我们来说，如何完成这个操作并不重要。每个中断处理程序都可以在`ntoskrnl.exe`中名为`KiDebugTrapOrFault`的表中找到。其中，我们看到，`KiDebugTrapOrFault`是中断#1的中断处理程序。目前，每一项的第二个函数都可以忽略，它与添加到Windows中的Meltdown缓解方法有关。

`KiDebugTrapOrFault`首先通过进行一些健全性检查，来确保`GS`是正确的。这些检查是为了缓解CVE-2018-88974漏洞。如果一切正确，则会调用`KxDebugTrapOrFault`。这个函数等价于添加缓解措施之前的`KiDebugTrapOrFault`。该函数用于将指定的寄存器保存到`TrapFrame`。这个函数的其余部分对于我们来说不是很有帮助，但它会检查SMAP等内容。在函数的最后，将会调用`KiExceptionDispatch`。

`KiExceptionDispatch`比以前的函数要更加有趣。首先，会在堆栈上分配一个`ExceptionFrame`并进行填充。随后，它将保存一些非易失性寄存器。完成此操作后，该函数将创建一个`ExceptionRecord`，并使用有关当前异常的信息来填充。之后，将会调用`KiDispatchException`。

```
.text:00000001403EF940     KiExceptionDispatch proc near
.text:00000001403EF940
.text:00000001403EF940     ExceptionFrame  = _KEXCEPTION_FRAME ptr -1D8h
.text:00000001403EF940     ExceptionRecord = _EXCEPTION_RECORD ptr -98h
.text:00000001403EF940
.text:00000001403EF940                 sub     rsp, 1D8h
.text:00000001403EF947                 lea     rax, [rsp+1D8h+ExceptionFrame._Rbx]
.text:00000001403EF94F                 movaps  xmmword ptr [rsp+1D8h+ExceptionFrame._Xmm6.Low], xmm6
.text:00000001403EF954                 movaps  xmmword ptr [rsp+1D8h+ExceptionFrame._Xmm7.Low], xmm7
.text:00000001403EF959                 movaps  xmmword ptr [rsp+1D8h+ExceptionFrame._Xmm8.Low], xmm8
.text:00000001403EF95F                 movaps  xmmword ptr [rsp+1D8h+ExceptionFrame._Xmm9.Low], xmm9
.text:00000001403EF965                 movaps  xmmword ptr [rsp+1D8h+ExceptionFrame._Xmm10.Low], xmm10
.text:00000001403EF96B                 movaps  xmmword ptr [rax-80h], xmm11
.text:00000001403EF970                 movaps  xmmword ptr [rax-70h], xmm12
.text:00000001403EF975                 movaps  xmmword ptr [rax-60h], xmm13
.text:00000001403EF97A                 movaps  xmmword ptr [rax-50h], xmm14
.text:00000001403EF97F                 movaps  xmmword ptr [rax-40h], xmm15
.text:00000001403EF984                 mov     [rax], rbx
.text:00000001403EF987                 mov     [rax+8], rdi
.text:00000001403EF98B                 mov     [rax+10h], rsi
.text:00000001403EF98F                 mov     [rax+18h], r12
.text:00000001403EF993                 mov     [rax+20h], r13
.text:00000001403EF997                 mov     [rax+28h], r14
.text:00000001403EF99B                 mov     [rax+30h], r15

[...]

.text:00000001403EF9BD                 lea     rax, [rsp+1D8h+ExceptionFrame.Return]
.text:00000001403EF9C5                 mov     [rax], ecx
.text:00000001403EF9C7                 xor     ecx, ecx
.text:00000001403EF9C9                 mov     [rax+4], ecx
.text:00000001403EF9CC                 mov     [rax+8], rcx
.text:00000001403EF9D0                 mov     [rax+10h], r8
.text:00000001403EF9D4                 mov     [rax+18h], edx
.text:00000001403EF9D7                 mov     [rax+20h], r9
.text:00000001403EF9DB                 mov     [rax+28h], r10
.text:00000001403EF9DF                 mov     [rax+30h], r11
.text:00000001403EF9E3                 mov     r9b, [rbp+0F0h]
.text:00000001403EF9EA                 and     r9b, 1          ; PreviousMode
.text:00000001403EF9EE                 mov     byte ptr [rsp+1D8h+ExceptionFrame.P5], 1 ; FirstChance
.text:00000001403EF9F3                 lea     r8, [rbp-80h]   ; TrapFrame
.text:00000001403EF9F7                 mov     rdx, rsp        ; ExceptionFrame
.text:00000001403EF9FA                 mov     rcx, rax        ; ExceptionRecord

[...]

.text:00000001403EFA67 SkipExceptionStack:
.text:00000001403EFA67                 call    KiDispatchException
```

`KiDispatchException`是一个相当长的函数，在该函数中，异常最终被分派到异常处理程序。简而言之，该函数将会对异常代码进行一些转换，将`TrapFrame`和`ExceptionFrame`组合到`ContextRecord`中，并通过调用`KiPreprocessFault`预处理异常。接下来的操作，要取决于异常是来自用户模式还是内核模式。但在这两种情况下，它都将允许调试器将其作为第一次和第二次机会进行处理。

如果异常来自内核模式，则会调用`RtlDispatchException`，将会搜索任何SEH处理程序并进行调用。如果没有找到SEH处理程序或者没能正确处理异常，则系统将通过调用`KeBugCheckEx`进行错误检查。如果异常来自用户模式，则会纠正`TrapFrame`中的某些字段，例如堆栈指针。最后，`TrapFrame`中的指令指针将被`KeUserExceptionDispatcher`的地址覆盖。我们将在稍后介绍此函数的作用。将`ExceptionRecord`和`ContextRecord`复制到用户堆栈后，函数将返回。

一旦回到`KiExceptionDispatch`，我们将简单地清理堆栈，恢复先前保存的volatile状态，并在iretq的帮助下返回用户模式。因为我们较早地重写了用户堆栈，所以可以从`KeUserExceptionDispatcher`恢复执行流。

```
.text:00000001403EFA6C                 lea     rcx, [rsp+1D8h+ExceptionFrame._Rbx] ; rcx = _KTRAP_FRAME
.text:00000001403EFA74                 movaps  xmm6, xmmword ptr [rsp+1D8h+ExceptionFrame._Xmm6.Low]
.text:00000001403EFA79                 movaps  xmm7, xmmword ptr [rsp+1D8h+ExceptionFrame._Xmm7.Low]
.text:00000001403EFA7E                 movaps  xmm8, xmmword ptr [rsp+1D8h+ExceptionFrame._Xmm8.Low]
.text:00000001403EFA84                 movaps  xmm9, xmmword ptr [rsp+1D8h+ExceptionFrame._Xmm9.Low]
.text:00000001403EFA8A                 movaps  xmm10, xmmword ptr [rsp+1D8h+ExceptionFrame._Xmm10.Low]
.text:00000001403EFA90                 movaps  xmm11, xmmword ptr [rcx-80h]
.text:00000001403EFA95                 movaps  xmm12, xmmword ptr [rcx-70h]
.text:00000001403EFA9A                 movaps  xmm13, xmmword ptr [rcx-60h]
.text:00000001403EFA9F                 movaps  xmm14, xmmword ptr [rcx-50h]
.text:00000001403EFAA4                 movaps  xmm15, xmmword ptr [rcx-40h]
.text:00000001403EFAA9                 mov     rbx, [rcx]
.text:00000001403EFAAC                 mov     rdi, [rcx+8]
.text:00000001403EFAB0                 mov     rsi, [rcx+10h]
.text:00000001403EFAB4                 mov     r12, [rcx+18h]
.text:00000001403EFAB8                 mov     r13, [rcx+20h]
.text:00000001403EFABC                 mov     r14, [rcx+28h]
.text:00000001403EFAC0                 mov     r15, [rcx+30h]

[...]

.text:00000001403EFBEC                 mov     rdx, [rbp-40h]
.text:00000001403EFBF0                 mov     rcx, [rbp-48h]
.text:00000001403EFBF4                 mov     rax, [rbp-50h]
.text:00000001403EFBF8                 mov     rsp, rbp
.text:00000001403EFBFB                 mov     rbp, [rbp+0D8h] 
.text:00000001403EFC02                 add     rsp, 0E8h

[...]

.text:00000001403EFC17                 swapgs
.text:00000001403EFC1A                 iretq
```

还记得我们之前设置的`KeUserExceptionDispatcher`的地址吗？这实际上是位于`ntdll.dll`中的`KiUserExceptionDispatcher`。该函数负责处理异常的用户模式部分，它将从异常获取`ExceptionRecord`和`Context`并将执行传递给`RtlDispatchException`。在这里，我们先不做详细介绍，但它最终会检查`SEH`和`VEH`异常处理程序，如果存在，会进行调用。

```
.text:000000018009EBF0 KiUserExceptionDispatcher proc near
.text:000000018009EBF0                 cld
.text:000000018009EBF1                 mov     rax, cs:Wow64PrepareForException
.text:000000018009EBF8                 test    rax, rax
.text:000000018009EBFB                 jz      short loc_18009EC0C
.text:000000018009EBFD                 mov     rcx, rsp
.text:000000018009EC00                 add     rcx, 4F0h
.text:000000018009EC07                 mov     rdx, rsp
.text:000000018009EC0A                 call    rax ; Wow64PrepareForException
.text:000000018009EC0C
.text:000000018009EC0C loc_18009EC0C:
.text:000000018009EC0C                 mov     rcx, rsp
.text:000000018009EC0F                 add     rcx, 4F0h
.text:000000018009EC16                 mov     rdx, rsp
.text:000000018009EC19                 call    RtlDispatchException
.text:000000018009EC1E                 test    al, al
.text:000000018009EC20                 jz      short loc_18009EC2E
.text:000000018009EC22                 mov     rcx, rsp
.text:000000018009EC25                 xor     edx, edx
.text:000000018009EC27                 call    RtlGuardRestoreContext
.text:000000018009EC2C                 jmp     short loc_18009EC43
.text:000000018009EC2E ; ---------------------------------------------------------------------------
.text:000000018009EC2E
.text:000000018009EC2E loc_18009EC2E:
.text:000000018009EC2E                 mov     rcx, rsp
.text:000000018009EC31                 add     rcx, 4F0h
.text:000000018009EC38                 mov     rdx, rsp
.text:000000018009EC3B                 xor     r8b, r8b
.text:000000018009EC3E                 call    ZwRaiseException
.text:000000018009EC43
.text:000000018009EC43 loc_18009EC43:
.text:000000018009EC43                 mov     ecx, eax
.text:000000018009EC45                 call    RtlRaiseStatus
.text:000000018009EC45 KiUserExceptionDispatcher endp
```



## 3. 常见攻击方法

### <a class="reference-link" name="3.1%20%E8%B0%83%E8%AF%95"></a>3.1 调试

顾名思义，调试寄存器主要用于调试的目的。尽管一般的断点都需要编辑程序集以添加断点指令，但硬件断点却可以在无需修改任何程序集的情况下进行调试。在处理自修改代码或进行完整性检查时，这特别有帮助。

### <a class="reference-link" name="3.2%20%E6%81%B6%E6%84%8F%E8%BD%AF%E4%BB%B6"></a>3.2 恶意软件

由于其用法较为谨慎，并且内置了安全控制措施（例如DR7，第13位），因此它们也成为了恶意软件作者最喜欢的工具，特别是Rootkit。这种技术允许恶意软件以静默的方式对函数进行挂钩。可以用来挂钩重要的系统例程，例如Windows上的`KiSystemCall64`或Linux上的`do_debug`。

### <a class="reference-link" name="3.3%20%E6%B8%B8%E6%88%8F%E4%BD%9C%E5%BC%8A"></a>3.3 游戏作弊

当然，对于一些研究如何对抗反作弊机制的游戏玩家也可以利用这些技术。调试寄存器可用于对重要的游戏函数进行挂钩，并实现自定义逻辑。其中的一个例子就是EBFE针对守望先锋（Overwatch）游戏设计的Outlines VEH挂钩。调试寄存器放置在负责绘制播放器轮廓的函数上，并使用`AddVectoredExceptionHandler`注册异常处理程序。当游戏调用`Outlines`函数时，硬件断点将触发，并将控制流重定向到已注册的异常处理程序。在这里，它会检查异常是否来自outlines函数，并编辑其中的一些数据，以使游戏位所有玩家绘制轮廓。根据推测，暴雪似乎无法检测到该技术，因此这种方法可以有效地被一些作弊玩家使用。



## 4. 常用检测手段

在最后一章中，我们将介绍一些硬件断点的常用检测维度。为了简化本章的内容，我们在这里展示的示例均没有使用混淆技术，这部分将留给读者练习。

### <a class="reference-link" name="4.1%20GetThreadContext"></a>4.1 GetThreadContext

检测硬件断点的最简单方法之一，就是使用`GetThreadContext` Win API。这个函数将返回指定线程的`CONTEXT`结构。该结构中包括每个调试寄存器的值，这使我们可以轻松地检查是否有任何寄存器被填充。

这种检测非常容易实现，但也很容易被绕过。例如，攻击者只需对`GetThreadContext`进行挂钩，即可返回去掉调试寄存器字段的虚假结构。

```
/* Prepare the context structure */
CONTEXT context = `{` 0 `}`;
/* CONTEXT_ALL will fill all the fields in the structure, this can be changed depending on your needs. */
context.ContextFlags = CONTEXT_ALL;

/* Call GetThreadContext with the current thread */
BOOL result = GetThreadContext(GetCurrentThread(), &amp;context);
if (!result)
`{`
    /* GetThreadContext failed, use GetLastError to find out why */
    return;
`}`

/* Check each debug register field */
if (context.Dr0 != 0 /* ... */)
`{`
    /* Debug register detected */
`}`
```

### <a class="reference-link" name="4.2%20%E5%BC%82%E5%B8%B8%E5%A4%84%E7%90%86%E7%A8%8B%E5%BA%8F"></a>4.2 异常处理程序

获取包含调试寄存器`CONTEXT`结构的另一种方法是注册异常处理程序。`VEH`异常处理程序中的第一个也是唯一的参数，就是指向`EXCEPTION_POINTERS`结构的指针。在这里，我们可以轻松地检查是否有任何调试寄存器已满。有多种方法可以实现此检测，其中最简单的方法就是使用`AddVectoredExceptionHandler`和`RaiseException`。

```
/* Our exception handler */
long debug_veh(struct _EXCEPTION_POINTERS* ExceptionInfo)
`{`
    /* Only check if it is our exception */
    if (ExceptionInfo-&gt;ExceptionRecord-&gt;ExceptionCode == 0x1337)
    `{`
        /* Check each debug register field */
        if (ExceptionInfo-&gt;ContextRecord-&gt;Dr0 != 0 /* ... */)
        `{`
            /* Debug register detected */
        `}`

        /* Fix the divide by zero error (see below). The second argument should be stored in rcx, simply change it to 100 / 10 before continuing */
        /* ExceptionInfo-&gt;ContextRecord-&gt;Rcx = 10; */

        /* Exception is handled, we can continue normal execution */
        return EXCEPTION_CONTINUE_EXECUTION;
    `}`

    /* Try the next exception handler if it is not our exception */
    return EXCEPTION_CONTINUE_SEARCH;
`}`

[...]

/* Somewhere in an initialization function, register our exception handler */
AddVectoredExceptionHandler(1, debug_veh);

[...]

/* The detection can be triggered whenever you want by raising an exception */
RaiseException(0x1337, 0, 0, nullptr);

/* Alternatively, if the above does not work properly, simply trigger a divide by zero error. 
   Make sure to change the exception code and fix the error (see above) */
volatile int b = 0;
volatile int a = 100 / b;
```

攻击者可以让他们的异常处理程序在我们的异常处理程序之前运行，从而绕过这种检测方式。为了解决这个问题，需要尽可能早地在将异常转移到用户模式时就进行挂钩。如上所述，这是在`ntdll.dll`中实现的`KiUserExceptionDispatcher`。可以使用各种方法对这个函数进行挂钩，其中最简单的方法是将`Wow64PrepareForException`指针替换为我们自己的函数。需要进行一些前置工作，才能正确获取两个参数，但这将允许我们的异常处理程序可以在其他任何参数之前运行。

### <a class="reference-link" name="4.3%20MOV%20DRx%E6%8C%87%E4%BB%A4"></a>4.3 MOV DRx指令

这种检测只适用于以内核模式运行的情况，因为这里使用的MOV指令在其他地方不可用。通过使用`__readdr`和`__writedr`，可以直接操纵调试寄存器的内容。我们可以使用这些内置函数来检查是否设置了任何调试寄存器。这里的关键之处在于，攻击者可能已经在DR7中启用了通用检测位。这会导致每次访问调试寄存器时都会生成`#DB`异常。当我们尝试检查寄存器时，这可以用于快速清除寄存器。

```
/* Check each debug register field */
if (__readdr(0) != 0)
`{`
    /* Debug register detected */
`}`
```

### <a class="reference-link" name="4.4%20%E6%A3%80%E6%9F%A5DR6"></a>4.4 检查DR6

在触发硬件断点时，DR6会填充有关事件的信息，这可以用来对当前情况进行更明确的决定。而重点就在于，在处理完硬件断点后，不会自动清除DR6。在Intel SDM中对这一部分进行了更详细的描述：

某些调试异常可能会清除第0-3位。处理器永远不会清除DR6寄存器的其余内容。为避免在识别调试异常时产生混淆，调试处理程序应该在返回中断的任务之前清除寄存器（除了应该设置的第16位之外）。

如果我们确定某个程序没有使用硬件断点，那么就可以使用前面提到的任何一种技术来检查DR6值，因为攻击者可能没有清除寄存器。

### <a class="reference-link" name="4.5%20%E4%BD%BF%E7%94%A8%E6%89%80%E6%9C%89%E8%B0%83%E8%AF%95%E5%AF%84%E5%AD%98%E5%99%A8"></a>4.5 使用所有调试寄存器

最简单的技术之一，就是亲自使用所有可用的调试寄存器。这种技术仅仅会受到我们的创造力的限制，将允许我们在使用硬件时进行检测或导致崩溃。该技术的一个简单实现就是将所有硬件断点放置在重要函数上。一旦调用了断点，就可以在返回原始函数之前处理一些数据。如果攻击者覆盖了任何调试寄存器，那么就不会进行数据操作，并且程序将会崩溃。下面的示例更改了程序集，并在执行之前将其还原。我们可以对所有4个调试寄存器重复此操作，因此删除其中的一个将会导致程序崩溃。

```
/* Change page permissions to RWX so we can change the assembly */
DWORD old_protect = 0;
BOOL result = VirtualProtect((void*)test_func, 0x1000, PAGE_EXECUTE_READWRITE, &amp;old_protect);
if (!result)
`{`
    /* VirtualProtect failed, call GetLastError to find out why */
    return;
`}`


/* Change the assembly to some garbage */
*(byte*)test_func ^= 0x42;


/* Register our VEH */
AddVectoredExceptionHandler(1, debug_veh);


/* Set the hardware breakpoint on our function */
CONTEXT context = `{` 0 `}`;
context.ContextFlags = CONTEXT_ALL;

GetThreadContext(GetCurrentThread(), &amp;context);

context.Dr0 = (DWORD64)test_func;
context.Dr7 = 1 &lt;&lt; 0;
context.ContextFlags = CONTEXT_DEBUG_REGISTERS;

SetThreadContext(GetCurrentThread(), &amp;context);


[...]


long debug_veh(struct _EXCEPTION_POINTERS* ExceptionInfo)
`{`
    /* Check if the exception came from us */
    if (ExceptionInfo-&gt;ExceptionRecord-&gt;ExceptionCode == STATUS_SINGLE_STEP)
    `{`
        /* Restore the assembly before executing it so we don't crash. 
           We do not change it back to garbage here so subsequent calls will crash.
           This can be achieved in a second hardware breakpoint. */
        *(byte*)test_func ^= 0x42;

        /* Set Resume Flag (RF) so we don't get stuck in an infinite loop */
        ExceptionInfo-&gt;ContextRecord-&gt;EFlags |= 0x10000;

        return EXCEPTION_CONTINUE_EXECUTION;
    `}`

    return EXCEPTION_CONTINUE_SEARCH;
`}`
```



## 5. 致谢

感谢下面这些研究人员对我的帮助，排名不分先后：

Derek Rynd ([@daax_rynd](https://github.com/daax_rynd))<br>
Can Bölük ([@_can1357](https://github.com/_can1357))<br>
Nemi ([@0xNemi](https://github.com/0xNemi))



## 6. 参考

[1] [https://software.intel.com/en-us/articles/intel-sdm](https://software.intel.com/en-us/articles/intel-sdm)<br>
[2] [https://developer.amd.com/resources/developer-guides-manuals/](https://developer.amd.com/resources/developer-guides-manuals/)<br>
[3] [https://revers.engineering/applied-re-exceptions/](https://revers.engineering/applied-re-exceptions/)<br>
[4] [https://www.triplefault.io/2017/08/detecting-debuggers-by-abusing-bad.html](https://www.triplefault.io/2017/08/detecting-debuggers-by-abusing-bad.html)<br>
[5] [https://blog.can.ac/2019/10/19/byepg-defeating-patchguard-using-exception-hooking/](https://blog.can.ac/2019/10/19/byepg-defeating-patchguard-using-exception-hooking/)
