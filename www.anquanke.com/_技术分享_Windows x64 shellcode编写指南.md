> 原文链接: https://www.anquanke.com//post/id/86175 


# 【技术分享】Windows x64 shellcode编写指南


                                阅读量   
                                **272668**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：tophertimzen.com
                                <br>原文地址：[https://www.tophertimzen.com/blog/windowsx64Shellcode/](https://www.tophertimzen.com/blog/windowsx64Shellcode/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t018b22c7256d3ae774.jpg)](https://p5.ssl.qhimg.com/t018b22c7256d3ae774.jpg)

****

翻译：[xgxgxggx](http://bobao.360.cn/member/contribute?uid=2830254841)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

最近我重写了几个shellcode，将之前32位平台下实现的shellcode移植到64位平台。在向64位平台移植过程，我发现很难在网上找到相关资料，因此我将我的移植过程写成一篇博客（我的第一篇），希望能帮到像我一样需要移植64位shellcode的人。<br>

网上已经有几篇教程介绍关于shellcode的相关基础知识了，因此我不会介绍这些。虽然我会介绍关于调用约定、register clobbering和寄存器相关知识，但是我不会讨论很多汇编基础知识。

请参考Skape的[Understanding Windows Shell code](https://publish.adlab.corp.qihoo.net:8360/contribute/www.nologin.com/Downloads/Papers/win32-shellcode.pdf)等文章，或者资源[project-shellcode](http://www.projectshellcode.com/)进行深入学习(Understanding Windows Shell code原始链接失效，这里替换了，原始链接为[http://repo.hackerzvoice.net/depot_madchat/windoz/vulns/win32-shellcode.pdf)。](http://repo.hackerzvoice.net/depot_madchat/windoz/vulns/win32-shellcode.pdf)%E3%80%82)

 我将介绍32位汇编与64位汇编的差异，以及如何利用Windows系统中的结构体用于开发64位shellcode。我还将介绍我开发的2种漏洞利用辅助开发工具。

在开始之前需要说明的是我仍然在学习漏洞利用开发的初级阶段，为简单化，本文实验的系统为Window 7 x64版本。为简化叙述，x86指Win32平台，x64指Win64平台。

<br>

**寄存器(Registers)**

**x86**

x86处理器中有8个32位的通用寄存器

– eax-累加器

– ecx-计数寄存器

– edx-数据寄存器

– ebx-基地址寄存器

– esp-堆栈指针

– ebp-基址指针

– esi-源索引寄存器

– edi-目标索引寄存器

– eip-指令寄存器

由于向后兼容原因，其中4个寄存器（eax,ebx,ecx,edx）可以拆分16位和8位寄存器

– AX-EAX的低16位

– AH-AX的高8位

– AL-AX的低8位

– BX-EBX的低16位

– BH-EBX的高8位

– BL-EBX的低8位

ECX和EDX也使用字母（C,D）和后缀（X,H或L）表示16位和8位寄存器。

**x64**

64位处理器使用前缀“R”扩展上述8个寄存器，RAX,RCX,RDX等。需要注意的是x86平台下的寄存器表示方式仍然可用（eax,ax,al等）。

还引入了8个新的寄存器，r8、r9、r10、r11、r12、r13、r14和r15。这些寄存器也可以分为32位、16位和8位的版本。

– r#=64位

– r#d=低32位

– r#w=低16位

– r#b=8位

不幸的是，这些新的8位扩展寄存器不能够使用像eax中的低16位的高8位

<br>

**Clobber寄存器(Clobber Registers)**

Clobber寄存器是一些可能在函数（如Windows API）中被覆盖修改的寄存器。在汇编代码中不应该使用这些寄存器，容易引发程序不稳定，但是如果明确知道在api函数中那些寄存器会别修改还是可以使用这些寄存器的。

在Win32 API中,EAX、ECX和EDX都是Clobber寄存器，在Win64 API中，除了RBP、RBX、RDI、RSI、R12、R13、R14和R15，其他的寄存器都是Clobber寄存器。<br>RAX和EAX分别用于x64和x86函数的返回值。

<br>

**调用约定(Calling Convention)**

**x86**

Win32 API一般使用__stdcall调用约定，从右到左向堆栈上传递参数。

如调用函数有两个参数int x和int y的函数foo

```
foo(int x,int y)<br>
```

在堆栈上传递为

```
push y<br>push x<br>
```

**x64**

Win64平台下函数调用约定不同，但与Win32平台下的__fastcall相似，均使用寄存器传参，前四个参数分别使用RCX、RDX、R8和R9传递，其他多余的参数使用堆栈传递。需要注意的是，使用寄存器传参时从右到左传递参数。

如对Windows函数MessageBox的调用声明如下：

```
int WINAPI MessageBox(<br>_In_opt_  HWND hWnd,<br>_In_opt_  LPCTSTR lpText,<br>_In_opt_  LPCTSTR lpCaption,<br>_In_      UINT uType<br>);
```

在Win64调用预定下，参数为:

```
r9 = uType<br>r8 = lpCaption<br>rdx = lpText<br>rcx = hWnd
```

<br>

**Shellcode**

****让我们开始吧，现在Win64下的Shellcode与Win32的关键区别我们已经知道了，开始我们的文章吧。<br>

为显示运行Win64 shellcode，我将编写代码弹出MessageBox对话框。当shellcode最终完成后，我将使用我编写的工具将shellcode代码注入到calc进程中，验证shellcode能够在另一个进程中运行。

<br>

**注释**

我将使用NASM编译汇编代码，使用Jeremy Gordon编写的golink链接程序。使用你最喜欢的文本编辑器编辑汇编代码，我使用Windows平台下的Notepad++,然后开始编写代码。

<br>

**开始**

**1).声明NASM指令**

```
bits 64 
section .text
global start
```

**2).设置堆栈**

```
start: 
    sub rsp, 28h                ;reserve stack space for called functions
    and rsp, 0fffffffffffffff0h ;make sure stack 16-byte aligned
```

**3).得到Kernel32的基地址**

Win64与Win32平台的PEB结构位置是不同的，在Win32中，PEB为[fs:30h]指向的地址，而在Win64为[gs:60h]

虽然PEB结构发生了巨大变化，但是我们只关心LDR链表(PEB_LDR_DATA)所在的未知，在Windbg中使用&amp;rdquo;!peb&amp;rdquo;命令可以得到LDR所在的位置。

在Windbg输出的PEB结构中，Ldr.InMemoryOrderModuleList中包含Kernel32.dll,在链表第三个未知，此列表显示了进程中各个内存模块（PE文件，可执行文件和dll文件）在内存中所在的位置。

```
Ldr.InMemoryOrderModuleList:         00000000002b3150 . 00000000002b87d0
        Base TimeStamp                     Module
    ff600000 4a5bc9d4 Jul 13 16:57:08 2009 C:WindowsSystem32calc.exe
    77b90000 4ce7c8f9 Nov 20 05:11:21 2010 C:WindowsSYSTEM32ntdll.dll
    77970000 4ce7c78b Nov 20 05:05:15 2010 C:Windowssystem32kernel32.dll
```

通过在Windbg中使用dt命令填充PEB结构，确定Ldr链表所在的位置。

```
0:000&gt; dt _PEB 000007fffffd4000
ntdll!_PEB
   +0x000 InheritedAddressSpace : 0 ''
   +0x001 ReadImageFileExecOptions : 0 ''
   +0x002 BeingDebugged    : 0x1 ''
   +0x003 BitField         : 0x8 ''
   +0x003 ImageUsesLargePages : 0y0
   +0x003 IsProtectedProcess : 0y0
   +0x003 IsLegacyProcess  : 0y0
   +0x003 IsImageDynamicallyRelocated : 0y1
   +0x003 SkipPatchingUser32Forwarders : 0y0
   +0x003 SpareBits        : 0y000
   +0x008 Mutant           : 0xffffffff`ffffffff Void
   +0x010 ImageBaseAddress : 0x00000000`ff600000 Void
   +0x018 Ldr              : 0x00000000`77cc2640 _PEB_LDR_DATA
```

Ldr链表位于PEB的0x18位置

现在，我们还需要做一下步骤：

– 通过在PEB偏移0x18处获得Ldr链表，获得Ldr链表后，访问位于Ldr结构偏移0x20处的InMemoryOrderModuleList，如下输出

```
0:000&gt; dt _PEB_LDR_DATA 77cc2640
ntdll!_PEB_LDR_DATA
   +0x000 Length           : 0x58
   +0x004 Initialized      : 0x1 ''
   +0x008 SsHandle         : (null) 
   +0x010 InLoadOrderModuleList : _LIST_ENTRY [ 0x00000000`002b3140 - 0x00000000`002b87c0 ]
   +0x020 InMemoryOrderModuleList : _LIST_ENTRY [ 0x00000000`002b3150 - 0x00000000`002b87d0 ]
   +0x030 InInitializationOrderModuleList : _LIST_ENTRY [ 0x00000000`002b3270 - 0x00000000`002b87e0 ]
   +0x040 EntryInProgress  : (null) 
   +0x048 ShutdownInProgress : 0 ''
   +0x050 ShutdownThreadId : (null)
```

– 偏移0x20处为InMemoryOrderModuleList，由InMemoryOrderModule列表的输出的图中可以看出，Kernel32.dll是第3个内存模块。在_LIST_ENTRY结构包含向前和向后的指针，所有_LIST_ENTRY组成一个循环链表，通过这个链表可以找到Kernel32的基地址。

```
0:000&gt; dt _LIST_ENTRY
ntdll!_LIST_ENTRY
   +0x000 Flink            : Ptr64 _LIST_ENTRY
   +0x008 Blink            : Ptr64 _LIST_ENTRY
```

在Windbg中，使用!list可以遍历遍历_LIST_ENTRY结构组成的链表。!lis -x可以用于为每个位置的元素指定一个命令。我们用它去解析_PEB_LDR_DATA结构中的0x20偏移量，并通过_LIST_ENTRY元素进行解析。

将列出所有InMemoryOrderModule链表并显示相关的_LDR_DATA_TABLE_ENTRY

```
0:000&gt; dt _LDR_DATA_TABLE_ENTRY
ntdll!_LDR_DATA_TABLE_ENTRY
   +0x000 InLoadOrderLinks : _LIST_ENTRY
   +0x010 InMemoryOrderLinks : _LIST_ENTRY
   +0x020 InInitializationOrderLinks : _LIST_ENTRY
   +0x030 DllBase          : Ptr64 Void
   +0x038 EntryPoint       : Ptr64 Void
   +0x040 SizeOfImage      : Uint4B
   +0x048 FullDllName      : _UNICODE_STRING
   +0x058 BaseDllName      : _UNICODE_STRING
   +0x068 Flags            : Uint4B
   +0x06c LoadCount        : Uint2B
   +0x06e TlsIndex         : Uint2B
   +0x070 HashLinks        : _LIST_ENTRY
   +0x070 SectionPointer   : Ptr64 Void
   +0x078 CheckSum         : Uint4B
   +0x080 TimeDateStamp    : Uint4B
   +0x080 LoadedImports    : Ptr64 Void
   +0x088 EntryPointActivationContext : Ptr64 _ACTIVATION_CONTEXT
   +0x090 PatchInformation : Ptr64 Void
   +0x098 ForwarderLinks   : _LIST_ENTRY
   +0x0a8 ServiceTagLinks  : _LIST_ENTRY
   +0x0b8 StaticLinks      : _LIST_ENTRY
   +0x0c8 ContextInformation : Ptr64 Void
   +0x0d0 OriginalBase     : Uint8B
   +0x0d8 LoadTime         : _LARGE_INTEGER
```

在_LDR_DATA_TABLE_ENTRY结构中，InLoadOrderLinks指向下一个模块结构，DllBase是模块的基地址，FullDllName是它模块名称的Unicode字符串。

因为我们知道kenel32.dll是第三个模块

```
0:000&gt; !list -t ntdll!_LIST_ENTRY.Flink  -x "dt _LDR_DATA_TABLE_ENTRY @$extret" 002b3270
---CUT
ntdll!_LDR_DATA_TABLE_ENTRY
   +0x000 InLoadOrderLinks : _LIST_ENTRY [ 0x00000000`002b3830 - 0x00000000`002b3260 ]
   +0x010 InMemoryOrderLinks : _LIST_ENTRY [ 0x00000000`002b4980 - 0x00000000`002b3840 ]
   +0x020 InInitializationOrderLinks : _LIST_ENTRY [ 0x00000000`77970000 - 0x00000000`77985ea0 ]
   +0x030 DllBase          : 0xbaadf00d`0011f000 Void
   +0x038 EntryPoint       : 0x00000000`00420040 Void
   +0x040 SizeOfImage      : 0x2b35c0
   +0x048 FullDllName      : _UNICODE_STRING "kernel32.dll"
   +0x058 BaseDllName      : _UNICODE_STRING "ꩀ矌"
   +0x068 Flags            : 0x77ccaa40
   +0x06c LoadCount        : 0
   +0x06e TlsIndex         : 0
   +0x070 HashLinks        : _LIST_ENTRY [ 0xbaadf00d`4ce7c78b - 0x00000000`00000000 ]
   +0x070 SectionPointer   : 0xbaadf00d`4ce7c78b Void
   +0x078 CheckSum         : 0
   +0x080 TimeDateStamp    : 0
   +0x080 LoadedImports    : (null) 
   +0x088 EntryPointActivationContext : 0x00000000`002b4d20 _ACTIVATION_CONTEXT
   +0x090 PatchInformation : 0x00000000`002b4d20 Void
   +0x098 ForwarderLinks   : _LIST_ENTRY [ 0x00000000`002b36e8 - 0x00000000`002b36e8 ]
   +0x0a8 ServiceTagLinks  : _LIST_ENTRY [ 0x00000000`002b3980 - 0x00000000`002b3750 ]
   +0x0b8 StaticLinks      : _LIST_ENTRY [ 0x00000000`77c95124 - 0x00000000`78d20000 ]
   +0x0c8 ContextInformation : 0x01d00f7c`80e29f8e Void
   +0x0d0 OriginalBase     : 0xabababab`abababab
   +0x0d8 LoadTime         : _LARGE_INTEGER 0xabababab`abababab
   ---CUT
```

现在知道加载的模块基地址在_LDR_DATA_TABLE_ENTRY的0x30偏移处。

a.通过访问[gs:60h]找到PEB

b.通过在PEB中偏移0x18进入LDR链表。

c.偏移0x20是InMemoryOrderModuleList。

d.InMemoryOrderModuleList中的第3个元素是Kernel32，0x30th offset是模块的基地址。

e.我们要调用ExitProcess，这实际上是来自ntdll.dll的RtlExitUserProcess。Ntdll.dll是InMemoryOrderModuleList中的第二个条目，我也将获取它的基地址并将其存储在r15中供以后使用。我发现这个方法比依靠Kernel32在ntdll中正确执行一个函数更容易和更可靠

[![](https://p5.ssl.qhimg.com/t0184c5a130aac69ea6.jpg)](https://p5.ssl.qhimg.com/t0184c5a130aac69ea6.jpg)

从dependency walker中可以看出ExitProcess指向Ntdll.RtlExitUserProcess。

**<br>**

**开始编写汇编代码**

```
mov r12, [gs:60h]       ;peb
mov r12, [r12 + 0x18]   ;Peb --&gt; LDR
mov r12, [r12 + 0x20]   ;Peb.Ldr.InMemoryOrderModuleList
mov r12, [r12]          ;2st entry
mov r15, [r12 + 0x20]   ;ntdll.dll base address!
mov r12, [r12]          ;3nd entry
mov r12, [r12 + 0x20]   ;kernel32.dll base address! We go 20 bytes in here as we are already 10 bytes into the _LDR_DATA_TABLE_ENTRY from the InMemoryOrderModuleList
```

这里将Kernel32的地址放入r12寄存器(r12寄存器不是Clobber寄存器),在shellcode执行期间需要已知保留Kernel32的地址。现在找到了kernel32模块的地址，可以通过kernel32加载其他模块和获取其他函数的地址。

```
HMODULE WINAPI LoadLibrary(
_In_  LPCTSTR lpFileName
);
```

LoadLibraryA用于将其他dll模块加载到当前进程，因为shellcode需要与地址无关，不能依赖任何已经在目标进程中的dll。在本例中需要加载user32.dll。<br>为了使用LoadLibraryA函数，它必须在kernel32.dll中找它的地址，这就需要GetProcAddress函数了。

```
FARPROC WINAPI GetProcAddress(
_In_  HMODULE hModule,
_In_  LPCSTR lpProcName
);
```

GetProcAddress需要两个参数，需要获得的函数模块句柄以及函数名。

```
;find address of loadLibraryA from kernel32.dll which was found above. 
mov rdx, 0xec0e4e8e  ;lpProcName (loadLibraryA hash from ror13)
mov rcx, r12         ;hModule
call GetProcessAddress
```

一旦我们知道LoadLibraryA的地址，我们可以使用它来加载user32.dll。

&amp;ldquo;0xec0e4e8e&amp;rdquo;为函数名称的hash,将该hash赋值给rdx作为函数名参数。

0xec0e4e8e是LoadLibraryA的每个字母ROR 0x13相加所得的总和。这在Shellcode中是常见的，在MetaSploit等项目使用。我写了一个简单的C程序来用来计算这些hash。

```
#./rot13.exe LoadLibraryA
LoadLibraryA
ROR13 of LoadLibraryA is: 0xec0e4e8e
```

现在加载user32.dll

```
;import user32
lea rcx, [user32_dll]
call rax                ;load user32.dll
user_32dll: db 'user32.dll', 0
```

现在可以获得MessageBox函数的地址了

```
mov rdx, 0xbc4da2a8     ;hash for MessageBoxA from rot13
mov rcx, rax
call GetProcessAddress
```

然后执行MessageBox

```
;messageBox
xor r9, r9            ;uType
lea r8, [title_str]   ;lpCaptopn
lea rdx, [hello_str]  ;lpText
xor rcx, rcx          ;hWnd
call rax              ;display message box  
title_str:  db  '0xdeadbeef',   0
hello_str:  db  'This is fun!', 0
```

最后使用ExitProcess函数结束进程

```
VOID WINAPI ExitProcess(
_In_  UINT uExitCode
);
```

需要注意的是ExitProcess是kernel32所导出的函数，但是这里使用RtlExitUserProcess。

```
;ExitProcess
mov rdx, 0x2d3fcd70             
mov rcx, r15            ;base address of ntdll
call GetProcessAddress
xor  rcx, rcx           ;uExitCode
call rax
```

完整的shellcode与GetProcess函数实现如下:

这里使用call/pop指令实现&amp;rdquo;lea&amp;rdquo;指令

```
bits 64
section .text
global start
start:
;get dll base addresses
    sub rsp, 28h                     ;reserve stack space for called functions
    and rsp, 0fffffffffffffff0h      ;make sure stack 16-byte aligned   
    mov r12, [gs:60h]                ;peb
    mov r12, [r12 + 0x18]            ;Peb --&gt; LDR
    mov r12, [r12 + 0x20]            ;Peb.Ldr.InMemoryOrderModuleList
    mov r12, [r12]                   ;2st entry
    mov r15, [r12 + 0x20]            ;ntdll.dll base address!
    mov r12, [r12]                   ;3nd entry
    mov r12, [r12 + 0x20]            ;kernel32.dll base address!
;find address of loadLibraryA from kernel32.dll which was found above. 
    mov rdx, 0xec0e4e8e
    mov rcx, r12
    call GetProcessAddress         
;import user32
    jmp getUser32
returnGetUser32:
    pop rcx
    call rax                        ;load user32.dll
;get messageBox address
    mov rdx, 0xbc4da2a8
    mov rcx, rax
    call GetProcessAddress  
    mov rbx, rax
;messageBox
    xor r9, r9                     ;uType
    jmp getText
returnGetText:
    pop r8                         ;lpCaption
    jmp getTitle
returnGetTitle:
    pop rdx                        ;lpTitle
    xor rcx, rcx                   ;hWnd
    call rbx                       ;display message box 
;ExitProcess
    mov rdx, 0x2d3fcd70             
    mov rcx, r15
    call GetProcessAddress
    xor  rcx, rcx                  ;uExitCode
    call rax       
;get strings    
getUser32:
    call returnGetUser32
    db  'user32.dll'
    db  0x00
getTitle:
    call returnGetTitle
    db  'This is fun!'
    db  0x00
getText:
    call returnGetText
    db  '0xdeadbeef'
    db  0x00
;Hashing section to resolve a function address  
GetProcessAddress:      
    mov r13, rcx                     ;base address of dll loaded 
    mov eax, [r13d + 0x3c]           ;skip DOS header and go to PE header
    mov r14d, [r13d + eax + 0x88]    ;0x88 offset from the PE header is the export table. 
    add r14d, r13d                  ;make the export table an absolute base address and put it in r14d.
    mov r10d, [r14d + 0x18]         ;go into the export table and get the numberOfNames 
    mov ebx, [r14d + 0x20]          ;get the AddressOfNames offset. 
    add ebx, r13d                   ;AddressofNames base. 
find_function_loop: 
    jecxz find_function_finished   ;if ecx is zero, quit :( nothing found. 
    dec r10d                       ;dec ECX by one for the loop until a match/none are found
    mov esi, [ebx + r10d * 4]      ;get a name to play with from the export table. 
    add esi, r13d                  ;esi is now the current name to search on. 
find_hashes:
    xor edi, edi
    xor eax, eax
    cld         
continue_hashing:   
    lodsb                         ;get into al from esi
    test al, al                   ;is the end of string resarched?
    jz compute_hash_finished
    ror dword edi, 0xd            ;ROR13 for hash calculation!
    add edi, eax        
    jmp continue_hashing
compute_hash_finished:
    cmp edi, edx                  ;edx has the function hash
    jnz find_function_loop        ;didn't match, keep trying!
    mov ebx, [r14d + 0x24]        ;put the address of the ordinal table and put it in ebx. 
    add ebx, r13d                 ;absolute address
    xor ecx, ecx                  ;ensure ecx is 0'd. 
    mov cx, [ebx + 2 * r10d]      ;ordinal = 2 bytes. Get the current ordinal and put it in cx. ECX was our counter for which # we were in. 
    mov ebx, [r14d + 0x1c]        ;extract the address table offset
    add ebx, r13d                 ;put absolute address in EBX.
    mov eax, [ebx + 4 * ecx]      ;relative address
    add eax, r13d   
find_function_finished:
    ret
```

有关GetProcAddress函数的magic请参考[Skape](https://publish.adlab.corp.qihoo.net:8360/contribute/www.nologin.com/Downloads/Papers/win32-shellcode.pdf)的教程。

现在我们编译链接我们的shellcode，然后测试是否可以执行

```
nasm -f win64 messageBox64bit.asm -o messageBox64bit.obj  
golink /console messageBox64bit.obj
./messageBox64bit.exe
```

[![](https://p3.ssl.qhimg.com/t010ef5ac1739cd893b.jpg)](https://p3.ssl.qhimg.com/t010ef5ac1739cd893b.jpg)

通过这种方式编译出来的shellcode是一个PE可执行文件，这里在将他编译成一个纯shellcode文件。

```
nasm -f bin messageBox64bit.asm -o messageBox64bit.sc 
xxd -i messageBox64bit.sc
xxd -i messageBox64bit.sc
unsigned char messageBox64bit_sc[] = `{`
  0x48, 0x83, 0xec, 0x28, 0x48, 0x83, 0xe4, 0xf0, 0x65, 0x4c, 0x8b, 0x24,
  0x25, 0x60, 0x00, 0x00, 0x00, 0x4d, 0x8b, 0x64, 0x24, 0x18, 0x4d, 0x8b,
  0x64, 0x24, 0x20, 0x4d, 0x8b, 0x24, 0x24, 0x4d, 0x8b, 0x7c, 0x24, 0x20,
  0x4d, 0x8b, 0x24, 0x24, 0x4d, 0x8b, 0x64, 0x24, 0x20, 0xba, 0x8e, 0x4e,
  0x0e, 0xec, 0x4c, 0x89, 0xe1, 0xe8, 0x68, 0x00, 0x00, 0x00, 0xeb, 0x34,
  0x59, 0xff, 0xd0, 0xba, 0xa8, 0xa2, 0x4d, 0xbc, 0x48, 0x89, 0xc1, 0xe8,
  0x56, 0x00, 0x00, 0x00, 0x48, 0x89, 0xc3, 0x4d, 0x31, 0xc9, 0xeb, 0x2c,
  0x41, 0x58, 0xeb, 0x3a, 0x5a, 0x48, 0x31, 0xc9, 0xff, 0xd3, 0xba, 0x70,
  0xcd, 0x3f, 0x2d, 0x4c, 0x89, 0xf9, 0xe8, 0x37, 0x00, 0x00, 0x00, 0x48,
  0x31, 0xc9, 0xff, 0xd0, 0xe8, 0xc7, 0xff, 0xff, 0xff, 0x75, 0x73, 0x65,
  0x72, 0x33, 0x32, 0x2e, 0x64, 0x6c, 0x6c, 0x00, 0xe8, 0xcf, 0xff, 0xff,
  0xff, 0x54, 0x68, 0x69, 0x73, 0x20, 0x69, 0x73, 0x20, 0x66, 0x75, 0x6e,
  0x21, 0x00, 0xe8, 0xc1, 0xff, 0xff, 0xff, 0x30, 0x78, 0x64, 0x65, 0x61,
  0x64, 0x62, 0x65, 0x65, 0x66, 0x00, 0x49, 0x89, 0xcd, 0x67, 0x41, 0x8b,
  0x45, 0x3c, 0x67, 0x45, 0x8b, 0xb4, 0x05, 0x88, 0x00, 0x00, 0x00, 0x45,
  0x01, 0xee, 0x67, 0x45, 0x8b, 0x56, 0x18, 0x67, 0x41, 0x8b, 0x5e, 0x20,
  0x44, 0x01, 0xeb, 0x67, 0xe3, 0x3f, 0x41, 0xff, 0xca, 0x67, 0x42, 0x8b,
  0x34, 0x93, 0x44, 0x01, 0xee, 0x31, 0xff, 0x31, 0xc0, 0xfc, 0xac, 0x84,
  0xc0, 0x74, 0x07, 0xc1, 0xcf, 0x0d, 0x01, 0xc7, 0xeb, 0xf4, 0x39, 0xd7,
  0x75, 0xdd, 0x67, 0x41, 0x8b, 0x5e, 0x24, 0x44, 0x01, 0xeb, 0x31, 0xc9,
  0x66, 0x67, 0x42, 0x8b, 0x0c, 0x53, 0x67, 0x41, 0x8b, 0x5e, 0x1c, 0x44,
  0x01, 0xeb, 0x67, 0x8b, 0x04, 0x8b, 0x44, 0x01, 0xe8, 0xc3
`}`;
unsigned int messageBox64bit_sc_len = 258;
```

shellcode以16进制字符返回，然后通过我编写的另一个小程序在calc进程中执行该shellcode。需要说明的是这个小程序现在仅仅还是一个测试版，编写这个小程序的目的主要是为了测试另一个开源反汇编项目[BeaEngine](http://www.beaengine.org/home)

[![](https://p4.ssl.qhimg.com/t016ced206151058211.jpg)](https://p4.ssl.qhimg.com/t016ced206151058211.jpg)

启动这个小程序，将16进制数据拷贝到左边文本框中，选择64位版本，点击Fire Shellcode后，汇编代码将出现在右侧文本框中。实现汇编功能主要为了让这个小程序功能更加完整，通过这个功能也可以反编译一些不知道功能的shellcode。

点击fire后，小程序将运行calc并注入一个线程执行shellcode。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01df47450a8881af05.jpg)

成功！

<br>

**后记**

我希望这篇文章有助于帮助开发Win64 Shellcode，我刚开始写我在研究中学到的东西，希望以后能够继续坚持写。可以在这里下载我使用的一些程序，我将它压缩并放到这里:[资源](http://www.tophertimzen.com/resources/win64BlogPost/Windows-x64-Shellcode-resources.zip)。

更新2015年3月18日：我开源的我开发的shellcode Tester，将它放在github:[shellcodeTester](https://github.com/tophertimzen/shellcodeTester)。

写于2014年12月4日
