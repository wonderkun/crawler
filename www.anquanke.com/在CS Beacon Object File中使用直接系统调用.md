> 原文链接: https://www.anquanke.com//post/id/226754 


# 在CS Beacon Object File中使用直接系统调用


                                阅读量   
                                **256750**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Cornelis de Plaa，文章来源：outflank.nl
                                <br>原文地址：[https://outflank.nl/blog/2020/12/26/direct-syscalls-in-beacon-object-files/﻿](https://outflank.nl/blog/2020/12/26/direct-syscalls-in-beacon-object-files/%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01103f0a1ebcfe487b.jpg)](https://p2.ssl.qhimg.com/t01103f0a1ebcfe487b.jpg)



本篇文章将探究Cobalt Strike Beacon Object Files（BOF）中直接系统调用的应用。具体涵盖以下内容：
- 1.阐述如何在CS BOF使用直接系统调用来逃避常见的AV和EDR的检测
- 2.发布 **InlineWhispers** 脚本文件：使BOF代码更加方便地使用直接系统调用
- 3.提供BOF Poc代码，代码可启用WDigest凭证缓存，并通过修补LSASS进程内存绕过凭证保护
Poc源代码链接：

[https://github.com/outflanknl/WdToggle](https://github.com/outflanknl/WdToggle)

InlineWhispers源代码链接：

[https://github.com/outflanknl/InlineWhispers](https://github.com/outflanknl/InlineWhispers)



## BOF

Cobalt Strike最近引入了一个新的代码执行概念，称之为Beacon Object Files（缩写为BOF）。这使得Cobalt Strike operator能够在Beacon进程中执行一小段编译的C代码。

这样做的好处是什么？最重要的就是，摒弃了fork &amp; run的概念。在Beacon Object Files之前，fork &amp; run是CS中执行任务的默认机制。这意味着，在执行大多数后渗透功能时，会启动一个牺牲进程（通过spawnto参数指定），然后将渗透攻击功能作为反射DLL注入到该进程中。从AV/EDR角度，该过程有多种可被检测的特征，例如进程派生、进程注入和进程中反射DLL的内存artifacts。在许多现代场景中，fork &amp; run很容易变成OPSEC灾难。通过Beacon Object Files，我们可以在Beacon当前进程的上下文中运行编译后、位置无关的代码，这样就更加隐蔽。

尽管BOF的概念对于Cobalt Strike后渗透活动，在躲避AV/EDR方面向前迈出了重要的一步，但我们仍然会面临AV/EDR产品HOOK API调用的问题。2019年6月，我们发表了一篇关于直接系统调用的[博文](https://outflank.nl/blog/2019/06/19/red-team-tactics-combining-direct-system-calls-and-srdi-to-bypass-av-edr/)，文章通过示例展示了如何通过它来绕过AV/EDR软件。迄今为止，我们还没有看到在Beacon Object files中使用直接系统调用，因此我们决定编写我们自己的实现，并在本篇文章中分享我们的经验。



## 直接系统调用和BOF可行性

如今很多红队对于通过系统调用来绕过API钩子和躲避AV/EDR检测已烂熟于心。

在我们之前的[系统调用文章](https://outflank.nl/blog/2019/06/19/red-team-tactics-combining-direct-system-calls-and-srdi-to-bypass-av-edr/)中，我们展示了如何通过Visual Studio中的Microsoft Assembler （MASM）来包含C/C++项目中的系统调用。当我们创建一个包含汇编代码的Visual Studio项目时，它会通过汇编器和C编译器产生两个object文件，并将所有部分链接到一起，形成一个单独的可执行文件。

为了创建一个BOF文件，我们使用C编译器生成一个单独的object文件。如果想要在BOF项目中包含汇编代码，我们需要内联汇编来生成单个object文件。遗憾的是，Visual Studio并[不支持](https://docs.microsoft.com/en-us/cpp/assembler/inline/inline-assembler?view=msvc-160&amp;viewFallbackFrom=vs-2019)x64处理器的内联汇编，因此我们需要另一个支持x64处理器内联汇编的C编译器。



## Mingw-w64 和 内联汇编

[Mingw-w64](http://mingw-w64.org/doku.php)是GCC编译器的Windows版本，可用于创建32位和64位Windows应用程序。它可运行在Windows、Linux或其他基于Unix的操作系统上。最棒的是，它甚至支持x64处理器的内联汇编。所以，现在我们需要了解如何在BOF源代码中包含汇编代码。

[![](https://p4.ssl.qhimg.com/t0178d611972f6d3688.png)](https://p4.ssl.qhimg.com/t0178d611972f6d3688.png)

如果我们查看Mingw-w64或GCC编译器的手册页面，我们会注意到它通过 **-masm=dialect** 来支持汇编。

[![](https://p5.ssl.qhimg.com/t0131c7da41097e8787.png)](https://p5.ssl.qhimg.com/t0131c7da41097e8787.png)

使用intel语法，我们可以通过与在Visual Studio中使用Microsoft Assembler相同的语法编写汇编代码。要在代码中包含内联汇编，我们可以简单地使用以下汇编程序模板语法：

```
asm("nop \n  "
            "nop \n  "
            "nop")
```
<li>起始的汇编关键字是 asm 或 `__asm__`
</li>
- 指令必须用换行符隔开 （\n）
有关GCC汇编程序语法的更多信息，请参阅以下指南：

[https://www.felixcloutier.com/documents/gcc-asm.html#assembler-template](https://www.felixcloutier.com/documents/gcc-asm.html#assembler-template)



## 从asm到BOF

[![](https://p5.ssl.qhimg.com/t010987841315eac08d.png)](https://p5.ssl.qhimg.com/t010987841315eac08d.png)

我们把上述这些整合到以下示例中，该示例展示了使用内联汇编的[NtCurrentTeb()](https://docs.microsoft.com/en-us/windows/win32/api/winnt/nf-winnt-ntcurrentteb)函数的自定义版本，此函数可返回指向当前线程的线程环境块（TEB）的指针，然后可用于解析指向进程环境块（PEB）的指针：

为了使这个汇编函数在我们的C代码中可用，并声明它的名称、返回类型和参数，我们使用 **EXTERN_C** 关键字。此预处理器宏指定函数在其他地方定义，具有C链接并使用C语言调用约定。这种方法也可以用于在代码中包含汇编系统调用函数。只需将汇编编写的系统调用转换为汇编程序模板语法，使用 **EXTERN_C** 关键字添加函数定义并将其保存在头文件中，并将该文件包含在我们的项目中。

尽管在头文件中实现函数是完全有效的，但这不是最佳实践。但是，使用 **-o** 选项编译一个object文件只允许使用一个源文件，因此为了避免使主源文件带有汇编功能，我们将它们放在一个单独的头文件中。

要编译包含内联汇编的BOF源代码，我们使用以下编译器语法：

```
x86_64-w64-mingw32-gcc -o bof.o -c bof.c -masm=intel
```



## WdToggle

为了演示整个概念，我们编写了POC代码，其中包括使用内联汇编的直接系统调用，并且可以编译为Beacon Object File。

此代码显示了如何通过在Lsass进程（wdigest.dll模块）中将 **g_fParameter_UseLogonCredential** 全局参数切换为1来启用WDigest凭据缓存。 此外，可以通过在Lsass进程中将 **g_IsCredGuardEnabled** 变量切换为0来绕过凭据保护（如果已启用）。

这两个技巧都使我们能够在LSASS中再次显示明文密码，因此可以使用Mimikatz显示它们。 使用 **UseLogonCredential** 补丁后，您只需要用户锁定和解锁其会话，即可再次获得明文凭据。

[![](https://p0.ssl.qhimg.com/t0131474089eba3a7fa.png)](https://p0.ssl.qhimg.com/t0131474089eba3a7fa.png)

此PoC基于Hydra团队**xpn**和N4kedTurtle的以下出色博文。 这些博客是必读且包含所有必要的详细信息：

[Exploring Mimikatz – Part 1 – WDigest](https://blog.xpnsec.com/exploring-mimikatz-part-1/)

[Bypassing Credential Guard](https://teamhydra.blog/2020/08/25/bypassing-credential-guard/)

这两篇博文都包含用于修补LSASS的PoC代码，因此从这个角度来看，我们的代码并不是什么新鲜事物。 我们的PoC以此工作为基础，并且仅演示了如何利用Beacon Object File 中的直接系统调用来提供一种更为OPSEC安全的方式，来与LSASS进程交互并绕过Cobalt Strike的API钩子。



## 补丁限制

使用此PoC应用的内存补丁不能实现重启后驻留的，因此重启后必须重新运行代码。 此外，wdigest.dll模块中 **g_fParameter_UseLogonCredential** 和 **g_IsCredGuardEnabled** 全局变量的内存偏移量可能会在Windows版本和修订版之间发生变化。 我们为代码中的不同内部版本提供了一些偏移量，但是这些偏移量会在将来的版本中更改。 您也可以使用Windows调试器工具找到该偏移量，从而添加自己的版本偏移量。



## 检测

为了通过LSASS内存访问来检测凭证盗窃，我们可以使用Sysmon之类的工具来监视打开LSASS句柄的处理过程。 我们可以监视访问LSASS进程的可疑进程，从而检测可能的凭证转储活动。

当然，还有很多可选方法来检测凭据盗窃，例如使用Windows Defender ATP之类的高级检测平台。 但是，如果您没有足够的预算来使用这些前卫的平台，那么Sysmon是可以帮助你弥补功能空白的免费工具。



## InlineWhispers

在我们发布直接系统调用博文几个月后，@ Jackson_T发布了一个名为[SysWhispers](https://github.com/jthuraisamy/SysWhispers)的出色工具。SysWhispers Git存储库提到：

> “ SysWhispers通过生成头文件/汇编文件、并植入直接系统调用来帮助躲避检测 ”。

这是一个很棒的工具，它可以自动为任何系统调用生成头文件/汇编文件对，然后可以在定制的红队工具中使用它。

该工具生成的.asm输出文件可以在Visual Studio中通过微软宏汇编器使用。如果要在BOF项目中使用从SysWhispers输出生成的系统调用函数，则需要做一些转换，以便它们与汇编器模板语法匹配。

我们的同事[@_DaWouw](https://github.com/_DaWouw)编写了一个Python脚本，可用于将SysWhispers生成的.asm输出文件转换为适合BOF项目的输出文件。

它会转换输出以匹配汇编模板语法，因此你可以在BOF代码中使用这些函数。我们可以手动输入在BOF中使用哪些系统调用，以防止包括未使用的系统功能。该脚本可在Github页面上的InlineWhispers存储库中找到：

[https://github.com/outflanknl/InlineWhispers](https://github.com/outflanknl/InlineWhispers)



## 总结

在本博客中，我们展示了如何在 Cobalt Strike Beacon Object File 中使用直接系统调用。 要使用直接系统调用，我们需要使用汇编器模板语法编写汇编恒旭，这样我们可以将汇编函数包括在内联汇编中。 Visual Studio不支持x64处理器的内联汇编，但是幸运的是Mingw-w64支持。

为了演示 Beacon Object File 中直接系统调用的用法，我们编写了Poc代码，可用于启用WDigest凭据缓存。 此外，我们编写了一个名为InlineWhispers的脚本，该脚本可用于将SysWhispers生成的.asm输出转换为适合BOF项目的内联汇编头文件。

希望本博文有助于理解如何在BOF项目中使用直接系统调用以提高OPSEC安全性。
