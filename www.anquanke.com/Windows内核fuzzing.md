> 原文链接: https://www.anquanke.com//post/id/205577 


# Windows内核fuzzing


                                阅读量   
                                **195990**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Netanel Ben-Simon、Yoav Alon，文章来源：research.checkpoint.com
                                <br>原文地址：[https://research.checkpoint.com/2020/bugs-on-the-windshield-fuzzing-the-windows-kernel/](https://research.checkpoint.com/2020/bugs-on-the-windshield-fuzzing-the-windows-kernel/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t018cdaf450febbed40.jpg)](https://p1.ssl.qhimg.com/t018cdaf450febbed40.jpg)



## 背景

在[先前的研究](https://research.checkpoint.com/2018/50-adobe-cves-in-50-days/)中，我们使用[WinAFL](https://github.com/googleprojectzero/winafl)对Windows上运行的用户空间应用程序进行fuzz，并在Adobe Reader和Microsoft Edge中发现了50多个漏洞。

对于下一个挑战，我们决定追求更大的目标： Windows内核模糊测试。作为额外的好处，我们可以利用已有的用户空间漏洞，并将它们与我们发现的任何内核漏洞一起使用，以创建完整攻击链——因为没有沙箱逃逸/特权提升的RCE如今几乎毫无价值。

有了目标，我们开始着手探索内核fuzzer领域，看看在追求目标的过程中有哪些选择，也许会大量修改现有工具以更好地满足我们的需求。

本白皮书引用了我们今年早些时候在[OffensiveCon](https://www.offensivecon.org/speakers/2020/netanel-ben-simon-yoav-alon.html)和[BlueHatIL](https://www.bluehatil.com/abstracts#collapse-FuzzingWindowsKernel)上进行的演讲。

视频链接：[https://youtu.be/kJmuvjPDOOo](https://youtu.be/kJmuvjPDOOo)



## 探索内核fuzzer

我们在[AFL](https://github.com/google/AFL)和[WinAFL](https://github.com/googleprojectzero/winafl)方面拥有丰富的经验，因此我们开始寻找可用于攻击Windows内核的类似模糊测试工具。

我们使用Google搜索到了[kAFL](https://github.com/RUB-SysSec/kAFL)，即带有前缀’k’的AFL，看起来完全符合我们的需要。

### <a class="reference-link" name="kAFL"></a>kAFL

[kAFL](https://www.usenix.org/system/files/conference/usenixsecurity17/sec17-schumilo.pdf)是德国波鸿鲁尔大学的研究性fuzzer，它利用AFL样式fuzzing来攻击OS内核。看上去这似乎正是我们想要的。kAFL支持Linux、macOS和Windows，并被用来查找Linux内核Ext4文件系统和macOS中的漏洞。

kAFL具有与AFL相似的原理，但是由于它以OS内核为目标，因此它需要围绕fuzzing循环做更多的工作。Fuzzing循环是一个过程，在该过程中，每个循环周期中的测试用例都针对其目标进行测试，并处理反馈（参见图1）。

[![](https://p4.ssl.qhimg.com/t0153fb766e20c847a1.png)](https://p4.ssl.qhimg.com/t0153fb766e20c847a1.png)

图1：fuzzing循环周期

当kAFL首次启动时，fuzzer(1)会从保存状态生成运行目标OS的多个虚拟机。在VM快照中，VM内部运行着一个预加载的代理agent(2)。

代理agent(2)和fuzzer(1)协同以推动fuzzing处理过程。代理运行在用户空间，通过[hypercalls](https://wiki.xenproject.org/wiki/Hypercall)与fuzzer进行通信，并将目标驱动程序的地址范围发送给fuzzer，这些地址仅限制代理提供范围内的代码覆盖率跟踪。

在循环开始时，fuzzer通过共享内存将输入input(3)发送到代理。kAFL使用类似于AFL的突变策略来生成新的输入。

接下来，代理通知hypervisor开始(4)收集覆盖率。然后，代理将输入发送(5)到目标内核组件：例如，如果我们以负责解析压缩映像的名为test.sys的驱动程序(6)为目标，则代理将生成的输入发送到驱动程序以对其进行测试。

最后，代理要求停止(7)从[KVM](https://www.linux-kvm.org/page/Main_Page)(8)收集覆盖率，而fuzzer将处理覆盖率跟踪。kAFL的覆盖率实现使用 [Intel Processor Trace](https://software.intel.com/en-us/blogs/2013/09/18/processor-tracing)（IntelPT或IPT）作为覆盖率反馈机制。<br>
当guest OS尝试启动、停止或(9)收集覆盖率时，它将向[KVM](https://www.linux-kvm.org/page/Main_Page)发出hypercall。

kAFL崩溃检测机制（参见图2）的工作方式如下：

[![](https://p0.ssl.qhimg.com/t017a30e296ce589f9c.png)](https://p0.ssl.qhimg.com/t017a30e296ce589f9c.png)

图2： kAFL崩溃检测

VM内的agent(1)使用**BugCheck**和**BugCheckEx**的地址向KVM发出hypercall(2)，KVM(3)使用shellcode(5)依次对这些地址进行打补丁(4)，该shellcode在执行时会发出hypercall。

因此，当机器遇到bug时，内核会调用补丁版本的**BugCheck**或**BugCheckEx**发出hypercall，以通知(6)fuzzer产生了崩溃。

现在，我们了解了这些机制，考虑如何根据Windows环境的需要进行调整。



## 攻击什么？

Windows内核非常庞大，有[几千万行代码](https://techcommunity.microsoft.com/t5/Windows-Kernel-Internals/One-Windows-Kernel/ba-p/267142)和[数百万的源文件](https://github.com/dwizzzle/Presentations/blob/master/David%20Weston%20-%20Keeping%20Windows%20Secure%20-%20Bluehat%20IL%202019.pdf)。我们的重点是那些可以从用户空间访问的部分，这些部分相当复杂，并且可以用于本地特权提升（PE）。

根据我们的经验，AFL适合以下目标：

• 快速目标，每秒可以执行100次以上的迭代；

• 解析器，特别是针对二进制格式。

这与Michał Zalewski 在[AFL的README](https://github.com/google/AFL/blob/master/README.md#9-fuzzer-dictionaries)中所写的内容一致：“默认情况下，afl-fuzz突变引擎针对紧凑的数据格式进行了优化，例如图像、多媒体、压缩数据、正则表达式语法或shell脚本。它不太适合具有格式繁琐和冗余数据的语言，特别是包括HTML、SQL或JavaScript等的语言。”<br>
在Windows内核（图3）中寻找合适的目标。

[![](https://p4.ssl.qhimg.com/t01ee74aa52ada99c95.png)](https://p4.ssl.qhimg.com/t01ee74aa52ada99c95.png)

图3： Windows内核组件

这些是我们考虑的目标：

• 文件系统，例如NTFS、FAT、VHD等。<br>
• 注册表配置单元。<br>
• 加密/代码完整性（CI）。<br>
• PE格式。<br>
• 字体（从Windows 10开始已迁移到用户空间）。<br>
• 图形驱动程序。

### <a class="reference-link" name="Windows%E4%B8%AD%E7%9A%84%E5%85%B8%E5%9E%8B%E5%86%85%E6%A0%B8%E6%BC%8F%E6%B4%9E"></a>Windows中的典型内核漏洞

我们退后一步，研究了一个非常典型的内核漏洞：[CVE-2018-0744](https://crbug.com/project-zero/1389)。

[![](https://p1.ssl.qhimg.com/t015e3f4867fc3d3625.png)](https://p1.ssl.qhimg.com/t015e3f4867fc3d3625.png)

图4： win32k中的典型漏洞

该程序包含多个系统调用，这些系统调用将高度结构化的数据作为输入，例如结构体、常量（魔数）、函数指针、字符串和标志。

此外，系统调用之间存在依赖性：一个系统调用的输出用作其他系统调用的输入。这种类型的结构在内核缺陷的情况下非常常见，在这种情况下，使用一系列的系统调用来达到触发漏洞的错误状态。

可以在[此处](https://github.com/google/fuzzing/blob/master/docs/structure-aware-fuzzing.md)找到结构感知型fuzzing的重要性和示例。

### <a class="reference-link" name="Windows%E5%86%85%E6%A0%B8%E6%94%BB%E5%87%BB%E9%9D%A2%EF%BC%9AkAFL%20VS%20Syscall%20fuzzer"></a>Windows内核攻击面：kAFL VS Syscall fuzzer

在观察到上述bug之后，我们意识到使用AFL样式的fuzzer将会限制我们使用相对较小的内核部分。Windows内核的大部分内容可以通过涉及高度结构化数据的系统调用来访问，但是使用kAFL会将我们限制在内核中的二进制解析器中，例如设备驱动程序、文件系统、PE格式、注册表等。与可以从系统调用中访问的代码量相比，这些部分相对较少。因此，如果我们有一个系统调用fuzzer（syscall fuzzer），就可能会接触到更多的攻击面，例如虚拟内存管理、进程管理器、图形、user winapi、gdi、安全性、网络等等。

至此，我们意识到需要寻找一个系统调用fuzzer。

### <a class="reference-link" name="Syzkaller%E7%AE%80%E4%BB%8B"></a>Syzkaller简介

[Syzkaller](https://github.com/google/syzkaller)是一个覆盖率引导的结构感知型内核fuzzer（又名智能系统调用fuzzer）。它支持多种操作系统，并且可以在多种机器类型（Qemu、GCE、手机等）和多种架构（x86-64、aarch64）上运行。

到目前为止，Syzkaller 已经在Linux内核中[发现](https://syzkaller.appspot.com/upstream)了3700个bug，并且保守估计有六分之一是安全漏洞。

Syzkaller是结构感知的fuzzer，这意味着它具有每个系统调用的描述。系统调用描述以类似于go的[语法](https://github.com/google/syzkaller/blob/master/docs/syscall_descriptions_syntax.md#syscall-description-language)写入文本文件。Syz-sysgen是Syzkaller工具之一，用于解析和格式化系统调用描述。成功完成此过程后，它将文本文件转换为”go”代码，并将其与fuzzer代码一起编译到一个名为syz-fuzzer的可执行文件中。

Syz-fuzzer是驱动guest VM内部的fuzzing处理过程的主要可执行文件。Syzkaller具有自己的语法来描述程序、系统调用、结构体、联合等等，生成的程序也称为syz程序。这里有一个[示例](https://github.com/google/syzkaller/blob/master/docs/syscall_descriptions.md#syscall-descriptions)。

Syzkaller采用了一些[突变策略](https://github.com/google/syzkaller/blob/ed8812ac86c117831a001923d3048b0acd04ed3e/prog/mutation.go#L33)来对现有程序进行突变。以[syz格式](https://github.com/google/syzkaller/blob/master/docs/syscall_descriptions.md#programs)提供新代码覆盖的程序被Syzkaller保存在数据库中，这个数据库也称为语料库。这允许我们停止fuzzer，进行更改，然后从停止的位置继续。

[![](https://p2.ssl.qhimg.com/t01c66eaa31bbc041da.png)](https://p2.ssl.qhimg.com/t01c66eaa31bbc041da.png)

图5： Syzkaller架构（Linux）

Syzkaller的主要二进制文件是syz-manager(1)，当它启动时执行以下操作：

从之前的运行中加载程序的语料库(2)，启动多个测试(3)机器，使用ssh(4)将executor(6)和fuzzer(5)二进制文件复制到机器中，执行Syz-fuzzer(5)。

然后，Syz-fuzzer(5)从管理器中获取语料库并开始生成程序。每个程序都被送回管理器保护起来以防崩溃。然后，Syz-fuzzer通过IPC(7)将程序发送到executor(6)，该executor运行系统调用(8)并从内核(9)收集覆盖率（如果是Linux，则为KCOV）。

[KCOV](https://www.kernel.org/doc/html/v4.17/dev-tools/kcov.html)具有编译时插桩功能，它使我们可以从用户空间获取整个内核中每个线程的代码覆盖率。如果检测到新的覆盖率跟踪，则fuzzer(11)报告给管理器。

Syzkaller的目标是成为一个无监督的fuzzer，这意味着它试图使整个fuzzing过程自动化。这个属性的一个例子是，在发生崩溃的情况下，Syzkaller会生成多个复制的机器，以从程序日志中分析崩溃的syz程序。这些复制的机器尝试尽可能地最小化崩溃的程序。该过程完成后， Syzkaller通常会重新生成一个syz程序或一段C代码用于复现崩溃。Syzkaller还能够从git中提取维护者列表，并通过电子邮件将崩溃的详细信息发送给他们。

Syzkaller支持Linux内核，并有令人印象深刻的结果。看着Syzkaller，我们想：如果能在Windows上对Linux内核进行模糊测试就好了。这促使我们探索WSL。

### <a class="reference-link" name="WSLv1%E8%83%8C%E6%99%AF%E7%9F%A5%E8%AF%86"></a>WSLv1背景知识

[Windows下的Linux子系统（WSL）](https://docs.microsoft.com/en-us/windows/wsl/install-win10)是一个在Windows上运行原生Linux二进制可执行文件的兼容层，它在Linux系统调用和Windows API之间进行转换。第一个版本于2016年发布，其中包含2个驱动程序：lxcore和lxss。

它是旨在为开发人员运行bash和核心Linux命令而设计的。

WSLv1使用一个称为pico process的轻量级进程来托管Linux二进制文件，并使用称为pico provider的专用驱动程序处理来自pico process的系统调用（有关更多信息，请参见这里：[1](https://channel9.msdn.com/Blogs/Seth-Juarez/Windows-Subsystem-for-Linux-Architectural-Overview)，[2](https://docs.microsoft.com/en-us/archive/blogs/wsl/windows-subsystem-for-linux-overview)）。

### <a class="reference-link" name="%E4%B8%BA%E4%BB%80%E4%B9%88%E9%80%89%E6%8B%A9WSL"></a>为什么选择WSL

由于WSL比较类似于Linux内核，因此我们可以重用Linux的大多数现有语法以及与Linux环境兼容的syz-executor和syz-fuzzer二进制文件。

我们想找到特权提升（PE）的漏洞，但WSL v1默认情况下不提供，而且可能很难从沙箱中利用它，因为它运行在不同类型的进程（PICO process）中。但是我们认为最好在 Windows 上以最少的改动获得 Syzkaller 的使用经验。



## 移植

首先，我们从Microsoft商店安装Linux发行版，选择Ubuntu系统。使用”**apt install openssh-server**“命令添加ssh服务器，并配置ssh密钥。接下来，我们想添加覆盖率跟踪支持。不幸的是，Windows内核是闭源的，不提供像Linux中的KCOV这样的编译时插桩。

我们想到了一些可以帮助我们获得覆盖率跟踪的替代方法:

• 使用QEMU/BOCHS之类的模拟器并添加覆盖率检测。

• 使用像[pe-afl](https://github.com/wmliang/pe-afl)中一样的静态二进制插桩。

• 使用像[apple-pie](https://github.com/gamozolabs/applepie)中一样具有覆盖率采样的hypervisor虚拟机管理程序。

• 使用像Intel-PT一样的覆盖率硬件支持。

我们决定使用[Intel-PT](https://software.intel.com/en-us/blogs/2013/09/18/processor-tracing)，因为它提供运行时编译二进制文件的跟踪，而且速度相对较快，并且可以提供完整的覆盖率信息，这意味着我们可以按原始顺序获取访问的每个基本块的起始指令指针（IP）。

从运行目标OS的VM内部使用Intel-PT，需要对KVM进行一些修改。我们使用了大部分的kAFL kvm补丁来支持Intel-PT的覆盖率。

另外，我们通过hypercalls创建了一个类KCOV的接口，因此当executor尝试启动、停止或收集覆盖率时，它会发出hypercalls。

### <a class="reference-link" name="%E7%AC%A6%E5%8F%B7%E5%99%A8%EF%BC%831"></a>符号器＃1

我们需要一个可预见的bug，以使我们能够检测出崩溃。Syzkaller崩溃检测机制读取VM控制台的输出，并依赖于预定义的正则表达式来检测内核错误、警告等。

我们需要一个用于移植的崩溃检测机制，这样我们就可以向输出控制台打印Syzkaller捕捉到的警告。

为了检测BSOD，我们使用了kAFL的技术。我们使用一段shellcode对BugCheck和BugCheckEx进行补丁修补，该shellcode会发出hypercall并通过向QEMU输出控制台写入一条唯一的消息来通知发生了崩溃。

我们在syz-manager中添加了一个正则表达式用来检测来自QEMU输出控制台的崩溃消息。为了改进对内核错误的检测，我们还使用了带有特殊池的[Driver Verifier](https://docs.microsoft.com/en-us/windows-hardware/drivers/devtest/driver-verifier)来检测池损坏(“verifier /flags 0x1 /driver lxss.sys lxcore.sys”)。

Fuzzer的一个常见问题是会多次遇到同一bug。为了避免重复的bug，对于每次崩溃Syzkaller都需要唯一的输出。我们的第一种方法是从跟踪的模块范围内的堆栈中提取一些相对地址，并将它们打印到QEMU输出控制台。

[![](https://p0.ssl.qhimg.com/t017295d12c11f596f3.png)](https://p0.ssl.qhimg.com/t017295d12c11f596f3.png)

图6：符号器1的结果

### <a class="reference-link" name="%E5%AE%8C%E6%95%B4%E6%80%A7%E6%A3%80%E6%9F%A5"></a>完整性检查

在运行fuzzer之前，我们想确保它确实能够找到一个真实的漏洞，否则我们只是在浪费CPU时间。不幸的是，当时我们还找不到真实漏洞的公开PoC来执行此测试。<br>
因此，我们决定在其中一个系统调用中为特定的流程打上补丁以模拟漏洞。Fuzzer确实能够找到这个模拟出来的漏洞，这是个好迹象，我们可以运行fuzzer了。



## 第一次fuzzing尝试

启动fuzzer后不久，我们注意到一个崩溃，其错误消息是：CRITICAL_STRUCTURE_CORRUPTION。我们很快发现这是由于内核补丁保护Patch Guard造成的。我们的崩溃检测机制基于kAFL，在其中我们用shellcode对BugCheck和BugCheckEx进行补丁修补，该shellcode在崩溃时发出hypercall，而这正是PatchGuard的[设计初衷](https://en.wikipedia.org/wiki/Kernel_Patch_Protection#Technical_overview)。

为了解决这个问题，我们添加了一个驱动程序，该驱动程序在系统引导时启动，并使用[KeRegisterBugCheckCallback](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-keregisterbugcheckcallback)向ntos注册错误检查回调函数。现在，当内核崩溃时，它将调用我们的驱动程序，该驱动程序将发出hypercall通知fuzzer产生了崩溃。

再次运行fuzzer，这次得到了一个不同错误代码的新bug。我们尝试重现崩溃以帮助我们理解它，但发现从偏移量和随机无用堆栈中执行根本原因分析很困难。我们决定需要一种更好的方法来获取崩溃信息。

### <a class="reference-link" name="%E7%AC%A6%E5%8F%B7%E5%99%A8%EF%BC%832"></a>符号器＃2

我们试图在安装[Wine](https://www.winehq.org/)的宿主机上运行”kd”来产生调用堆栈，但是效果不佳，因为大约需要5分钟才能生成调用堆栈。

这种方法给我们的fuzzer造成了瓶颈。在复现过程中，Syzkaller尝试尽可能地最小化崩溃程序，并且每次最小化尝试时它都将等待调用堆栈，以确定是否是相同的崩溃。

因此，我们决定使用带有KD（kernel debug）的远程Windows机器，并在那里建立所有udp连接的隧道。实际效果很好，但是当我们将其扩展到38台机器时，连接断开了，Syzkaller将其解释为“挂起”。

### <a class="reference-link" name="%E7%AC%A6%E5%8F%B7%E5%99%A8%EF%BC%833"></a>符号器＃3

这时我们思考一下，KD和WinDBG是如何能够生成调用堆栈的？

答案是使用DbgHelp.dll中的StackWalk。要生成调用堆栈，我们需要StackFrame、ContextRecord和ReadMemoryRoutine。

[![](https://p3.ssl.qhimg.com/t013fd780d0221a2a14.png)](https://p3.ssl.qhimg.com/t013fd780d0221a2a14.png)

图7：符号器架构

图7显示了该架构：

1.通过KVM返回到QEMU，从guest中获取堆栈、寄存器和驱动程序地址。

2.QEMU将其发送到远程Windows机器，机器中的符号器使用所有相关参数调用StackWalk，并获取调用堆栈。

3.将调用堆栈打印回控制台。

该体系架构受到[Bochspwn for Windows](https://github.com/googleprojectzero/bochspwn)的极大启发。

现在，当我们遇到新的崩溃时，它看起来像这样：

[![](https://p2.ssl.qhimg.com/t016cb6cafe24ffdf81.png)](https://p2.ssl.qhimg.com/t016cb6cafe24ffdf81.png)

### <a class="reference-link" name="%E7%AC%A6%E5%8F%B7%E5%99%A8%EF%BC%834"></a>符号器＃4

让Windows机器与fuzzer一起运行并不理想，而且我们认为在’go’中实现最小的内核调试器并将其编译为Syzkaller将会非常困难。

我们从PDB解析器和提取器开始，之后，我们使用存储在PE中的展开信息实现了x64堆栈展开器。

最后一部分是实现KD串口通信，它的工作非常缓慢，因此我们开始在KDNET上工作，完成后将其集成到Syzkaller。

这个解决方案比之前的方案好得多。重复数据删除机制现在基于故障框架，我们还得到了BugCheck错误代码、寄存器和调用堆栈。

### <a class="reference-link" name="%E8%A6%86%E7%9B%96%E7%8E%87%E7%A8%B3%E5%AE%9A%E6%80%A7"></a>覆盖率稳定性

我们遇到的另一个问题是覆盖率稳定性。

Syzkaller使用多个线程来查找数据竞争。例如，当生成的程序有4个系统调用时，它可以将其分为两个线程，一个线程运行系统调用1和2，另一个线程运行系统调用3和4。

在覆盖率实现中，每个进程使用一个缓冲区。实际上，多次运行同一程序将导致每次运行的覆盖率跟踪不同。

覆盖率的不稳定性会影响fuzzer发现新的、有意思的代码路径和漏洞的能力。

我们希望通过将覆盖率实现方式更改为类似于KCOV的实现来解决此问题。我们知道KCOV跟踪每个线程的覆盖率，因此我们希望能够有这样的机制。

要创建类似KCOV的跟踪，我们需要：

• 跟踪KVM中的线程以交换缓冲区。<br>
• 将线程句柄感知添加到KCOV hypercall API。

为了跟踪线程，我们需要一个用于上下文切换的hook。我们可以从全局段中获取当前线程：

[![](https://p4.ssl.qhimg.com/t01c12b16ae49443916.png)](https://p4.ssl.qhimg.com/t01c12b16ae49443916.png)

图8： KeGetCurrentThread函数

我们查看了在上下文切换期间发生的情况，并在处理上下文切换的函数中找到了swapgs指令。当执行swapgs指令时，会引起可被hypervisor捕获的VMExit。

[![](https://p4.ssl.qhimg.com/t01d78f35d6af129366.png)](https://p4.ssl.qhimg.com/t01d78f35d6af129366.png)

图9： SwapContext函数内部的swapgs

这意味着如果我们可以跟踪swapgs，那么也可以监控KVM中的线程交换。这似乎是监控上下文切换和处理跟踪线程IntelPT的一个很好的hooking位置。

因此，我们删除了MSR_KERNEL_GS_BASE的拦截禁用。

[![](https://p3.ssl.qhimg.com/t0110be8daf50bb47f2.png)](https://p3.ssl.qhimg.com/t0110be8daf50bb47f2.png)

图10： MSR拦截

这使我们可以在每个上下文切换时使用hook并切换ToPa缓冲区，ToPa条目向Intel-PT描述了它可以在其中写入跟踪输出的物理地址。

我们还有一些小问题要处理：

• 禁用服务和自动加载的程序以及不必要的服务，以加快启动速度。<br>
• Windows更新随机重启机器并消耗大量CPU。<br>
• Windows defender随机杀死fuzzer。

总的来说，我们[调整](https://support.microsoft.com/en-us/help/15055/windows-7-optimize-windows-better-performance)了guest机器以实现最佳性能。

### <a class="reference-link" name="WSL%20fuzzing%E7%BB%93%E6%9E%9C"></a>WSL fuzzing结果

总体而言，我们用38个vCPU对WSL进行了4周的模糊测试。最后，我们有了一个工作原型，并更好地理解了Syzkaller的工作原理。

我们发现了4个DoS错误和一些死锁，然而却没有发现任何安全漏洞，这令我们感到失望，但我们决定转向真正的PE目标。



## 迈向真实目标

Fuzzing WSL是在Windows上理解Syzkaller的很好的方式。但此时我们想回到一个真正的特权提升目标上——一个默认随Windows一起提供并可从各种沙箱访问的目标。

我们研究了Windows内核攻击面，并决定从Win32k开始。Win32k是Windows子系统的内核端，它是操作系统的GUI基础结构。它也是本地特权提升（LPE）的常见目标，因为可以从许多沙箱中访问它。

它包括两个子系统的内核端：

• 窗口管理器，也称为User。

• 图形设备接口，也称为GDI。

它有许多系统调用（约1200个），意味着它是基于语法的fuzzer的理想目标（如先前所示的[CVE-2018-0744](https://crbug.com/project-zero/1389)）。从Windows 10开始，win32k分为多个驱动程序：win32k、win32kbase和win32kfull。

为了使Syzkaller适用于win32k，我们还必须做一些改动：

• 将fuzzer和executor二进制文件编译到Windows。

• 与OS相关的更改。

• 向fuzzer公开Windows 系统调用。

• 为方便起见，使用mingw++进行交叉编译。

### <a class="reference-link" name="Win32k%E8%B0%83%E6%95%B4"></a>Win32k调整

从fuzzer源代码开始，我们添加了Windows的相关实现，例如管道、共享内存等。

语法是fuzzer 的关键部分，稍后我们将对其进行深入说明。

然后，我们使用MinGW将executor修复为交叉编译。我们还必须修复共享内存和管道，并禁用fork模式，因为它在Windows中不存在。

作为语法编译的一部分，syz-sysgen会生成一个头文件（syscalls.h），其中包括所有系统调用的名称数字。对于Windows，我们选定导出的系统调用封装和WinAPI（例如CreateWindowExA和NtUserSetSystemMenu）。

大多数系统调用封装都在**win32u.dll**和**gdi32.dll**中被导出。要将它们公开给executor二进制程序，我们使用[gendef](https://sourceforge.net/p/mingw-w64/wiki2/gendef/)从dll中生成定义文件。然后，使用mingw-dlltool生成库文件，最终将它们链接到executor。

### <a class="reference-link" name="%E5%AE%8C%E6%95%B4%E6%80%A7%E6%A3%80%E6%9F%A5"></a>完整性检查

如前所述，我们想确保fuzzer能够复现旧的漏洞，否则就是在浪费CPU时间。

这次我们有了一个真实的漏洞（CVE-2018-0744，参见图4），并且想复现它。我们添加了相关的系统调用，运行fuzzer去寻找漏洞，但不幸的是它失败了。我们怀疑出现了错误，所以写了一个syz程序，并使用syz-execprog，Syzkaller直接执行syz程序，以查看它是否正常工作。系统调用已成功调用执行，但机器还是没有崩溃。

短时间后，我们意识到fuzzer正在会话0下运行。所有服务（包括ssh服务）都是运行在会话0下的[控制台应用程序](https://docs.microsoft.com/en-us/windows/win32/services/interactive-services)，并不是为运行GUI而设计的。因此，我们将其更改为在会话1下以普通用户身份运行。之后，Syzkaller能够成功复现该漏洞。

由此可得出结论，必须通过模拟漏洞或复现旧漏洞来测试新代码。

### <a class="reference-link" name="%E7%A8%B3%E5%AE%9A%E6%80%A7%E6%A3%80%E6%9F%A5"></a>稳定性检查

我们总共添加了15个API，然后再次运行fuzzer。

我们在win32kfull!_OpenClipboard中遇到了第一个崩溃，该崩溃是UAF引起的。但是由于某种原因，此崩溃没有在其他机器上重现。起初，我们以为这是由于我们创建的另一个bug引起的，但是它可以在没有运行fuzzer的同一台机器上重现。

调用堆栈和崩溃的程序无法帮助我们理解问题所在。因此，我们把引起崩溃的部分放到IDA中查看：

[![](https://p1.ssl.qhimg.com/t0137ffa226d65f2b8b.png)](https://p1.ssl.qhimg.com/t0137ffa226d65f2b8b.png)

图11：崩溃位置–win32kfull!_OpenClipboard

我们注意到，崩溃发生在条件块内，该条件块是否执行取决于ETW provider的标志：Win32kTraceLoggingLevel。

此标志在某些机器上是打开状态，在其他机器上是关闭状态，因此我们推断可能得到了A/B测试机器。我们报告了此崩溃，并再次重新安装了Windows。

再次运行fuzzer，我们得到了一个新的漏洞，这次是RegisterClassExA中的拒绝服务。此时，我们积极性大涨，因为如果15个系统调用导致2个漏洞，那么意味着1500个系统调用将导致200个漏洞。



## Win32k中的语法

因为之前没有关于syscall fuzzing win32k的公开研究，所以我们必须从头开始创建正确的语法。

我们最初的想法是，也许可以使这个过程自动化，但却遇到了两个问题：

首先，Windows头文件不足以生成语法，因为它们无法为系统调用fuzzer提供关键信息（如唯一字符串），一些DWORD参数实际上是标志位，许多结构体被定义为LPVOID。

其次，许多系统调用根本没有文档（例如NtUserSetSystemMenu）。

幸运的是，Windows的许多部分在技术上都是开源的：

• Windows NT泄漏的源码– [https://github.com/ZoloZiak/WinNT4](https://github.com/ZoloZiak/WinNT4)

• Windows 2000泄漏的源码-[https://github.com/pustladi/Windows-2000](https://github.com/pustladi/Windows-2000)

• ReactOS（泄漏的w2k3源码？）– [https://github.com/reactos/reactos](https://github.com/reactos/reactos)

• Windows Research Kit –[https://github.com/Zer0Mem0ry/ntoskrnl](https://github.com/Zer0Mem0ry/ntoskrnl)

我们在MSDN和泄漏的源码中寻找每个系统调用，并且使用IDA和WinDBG对其进行验证。

我们制作的许多API签名都易于生成，但有些却相当棘手——涉及大量结构体、未公开的参数、一些具有15个参数的系统调用等。

经过几百次系统调用后，再次运行fuzzer，我们得到了3个GDI漏洞和一些DoS错误！

至此，我们覆盖到了win32k中的数百个系统调用。我们想继续找到更多的bug。因此，是时候更深入地寻找有关Win32k的更多信息并达到更复杂的攻击面了。<br>
Fuzzer并不神奇，为了发现bug，我们需要确保覆盖了目标中的绝大部分攻击面。我们回头查看了Win32k的更多先前的工作，理解了老的漏洞和漏洞分类。然后，我们尝试使fuzzer支持新学习的攻击面。

一个示例是GDI共享句柄。_PEB！GdiSharedHandleTable是指向结构体的指针数组，该结构体具有所有进程之间关于共享GDI句柄的信息。我们通过添加伪系统调用GetGdiHandle(type, index)将它添加到Syzkaller中，该伪系统调用需要句柄类型和索引。这个函数遍历GDI共享句柄表数组，从初始化一直到**索引**，并返回与请求类型相同的最后一个句柄。

这导致[CVE-2019-1159](https://cpr-zero.checkpoint.com/vulns/cprid-2132/)，由在启动时创建的具有全局GDI句柄的一个系统调用触发的UAF漏洞。

[![](https://p5.ssl.qhimg.com/t0122b399f126873df4.png)](https://p5.ssl.qhimg.com/t0122b399f126873df4.png)

### <a class="reference-link" name="%E7%BB%93%E6%9E%9C"></a>结果

我们用60个vCPU进行了1个半月的模糊测试，发现了10个漏洞（3个待处理，1个重复）:

[CVE-2019-1014](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1014)，[CVE-2019-1096](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1096)，[CVE-2019-1159](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1159)，

[CVE-2019-1164](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1164)，[CVE-2019-1256](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1256)，[CVE-2019-1286](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1286)

另外还发现了3个DoS错误，1个WinLogon中的崩溃和一些死锁。



## LPE→RCE？

本地特权提升漏洞很酷，那远程代码执行怎么样呢？

Windows图元文件格式（WMF）简介。

WMF是图形文件格式。它的设计可追溯到1990年代，同时支持矢量图形和位图。Microsoft多年来将该格式扩充为以下格式

• EMF<br>
• EMF+<br>
• EMFSPOOL

Microsoft还为该格式增加了一项功能，允许添加可回放的记录，以重现图形输出。当回放这些记录时，图像解析器会调用NtGdi系统调用。可以在[j00ru的PPT](https://j00ru.vexillium.org/slides/2016/pacsec.pdf)中了解有关此格式的更多信息。

接受EMF文件的系统调用数量是有限的，但很幸运，我们在接受EMF文件的StretchBlt中发现了一处漏洞。

视频链接：

[https://research.checkpoint.com/wp-content/uploads/2020/05/EMF-Crash.mp4](https://research.checkpoint.com/wp-content/uploads/2020/05/EMF-Crash.mp4)



## 总结

我们的目标是使用fuzzer发现Windows内核bug。

我们开始在Windows内核中探索fuzzer领域，由于我们有使用AFL样式fuzzer的经验，因此我们寻找性能类似的工具并找到了kAFL。

我们分析了kAFL，并搜索Windows内核中的攻击面，但是很快发现，系统调用fuzzer可以达到更多的攻击面。

搜索系统调用fuzzer后，我们找到了Syzkaller。

至此，我们开始将其移植到WSL，因为WSL与Linux内核最为相似，并且我们可以获得在Windows上使用Syzkaller的一些经验；我们使用IntelPT实现了Windows内核的覆盖率检测；分享了一种崩溃检测机制，即崩溃符号器方法，并用于错误重复数据删除；发现了一些覆盖率稳定性问题，并为此分享了我们的解决方案。

在发现一些DoS错误后，我们决定转向一个真正的PE目标——win32k，但必须在Syzkaller中实现缺失的部分。然后，我们进行了完整性检查和压力测试，以确保fuzzer没有浪费CPU时间。之后，我们投入了大量时间来编写语法，阅读分析目标，并最终向fuzzer中添加对Win32k中新学习部分的支持。

总体而言，我们的研究使我们在Windows 10内核中发现了8个漏洞、DoS错误和死锁。
