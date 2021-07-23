> 原文链接: https://www.anquanke.com//post/id/225191 


# Windows内存破坏漏洞的现代探索，Part I：堆栈溢出（二）


                                阅读量   
                                **193808**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者forrest-orr，文章来源：forrest-orr.net
                                <br>原文地址：[https://www.forrest-orr.net/post/a-modern-exploration-of-windows-memory-corruption-exploits-part-i-stack-overflows](https://www.forrest-orr.net/post/a-modern-exploration-of-windows-memory-corruption-exploits-part-i-stack-overflows)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t010dfb3d3a992c8000.jpg)](https://p0.ssl.qhimg.com/t010dfb3d3a992c8000.jpg)



在上一篇文章中，我们为读者介绍了堆栈溢出漏洞，以及当前系统提供的针对该类漏洞的缓解措施，在本文中，我们将继续为读者详细介绍SEH劫持技术。



## SEH劫持技术

进程中的每个线程都可以注册handler函数（默认情况下也是如此），以便在触发异常时进行调用。这些handler函数的指针通常存储在堆栈上的EXCEPTION_REGISTRATION_RECORD结构体中。在任何版本的Windows上启动一个32位应用程序时，都至少会注册一个这样的handler，并将相关数据存储在堆栈中，具体如下图所示：

[![](https://p2.ssl.qhimg.com/t01cdb85cee263938d2.png)](https://p2.ssl.qhimg.com/t01cdb85cee263938d2.png)

图6 在线程初始化过程中，NTDLL默认注册的一个SEH帧

上面高亮显示的EXCEPTION_REGISTRATION_RECORD结构体包含一个指向下一个SEH记录的指针（也存储在堆栈上），后面是指向handler函数的指针（在本例中是NTDLL.DLL库中的函数）。 

```
typedef struct _EXCEPTION_REGISTRATION_RECORD `{`

PEXCEPTION_REGISTRATION_RECORD Next;

PEXCEPTION_DISPOSITION Handler;

`}` EXCEPTION_REGISTRATION_RECORD, *PEXCEPTION_REGISTRATION_RECORD;
```

在内部，指向SEH handler列表的指针都存储在每个线程的TEB的偏移量0处，并且每个EXCEPTION_REGISTION_RECORD都链接到下一个。如果handler不能正确处理抛出的异常，它会将执行权移交给下一个handler，以此类推。

[![](https://p2.ssl.qhimg.com/t01eb2a440dfbfd1769.png)](https://p2.ssl.qhimg.com/t01eb2a440dfbfd1769.png)

图7 SEH链的堆栈布局

因此，SEH实际上为攻击者提供了绕过堆栈Cookie的理想方法。我们可以利用堆栈溢出，覆盖现有的SHE handler(肯定至少会有一个)，然后让应用程序崩溃(考虑到我们有能力破坏堆栈内存，这肯定不在话下)。这将导致在易受攻击函数最后调用__SECURITY_CHECK_COOKIE之前，EIP被重定向到EXCEPTION_REGISTION_RECORD结构体中被覆盖后的handler地址。因此，在执行shellcode之前，应用程序根本没有机会发现其堆栈已被破坏。 

```
#include

#include

#include



void Overflow(uint8_t* pInputBuf, uint32_t dwInputBufSize) `{`

char Buf[16] = `{` 0 `}`;

memcpy(Buf, pInputBuf, dwInputBufSize);

`}`



EXCEPTION_DISPOSITION __cdecl FakeHandler(EXCEPTION_RECORD* pExceptionRecord, void* pEstablisherFrame, CONTEXT* pContextRecord, void* pDispatcherContext) `{`

printf("... fake exception handler executed at 0x%p\r\n", FakeHandler);

system("pause");

return ExceptionContinueExecution;

`}`



int32_t wmain(int32_t nArgc, const wchar_t* pArgv[]) `{`

uint32_t dwOverflowSize = 0x20000;

uint8_t* pOverflowBuf = (uint8_t*)HeapAlloc(GetProcessHeap(), 0, dwOverflowSize);



printf("... spraying %d copies of fake exception handler at 0x%p to the stack...\r\n", dwOverflowSize / 4, FakeHandler);



for (uint32_t dwOffset = 0; dwOffset &lt; dwOverflowSize; dwOffset += 4) `{`

*(uint32_t*)&amp;pOverflowBuf[dwOffset] = FakeHandler;

`}`



printf("... passing %d bytes of data to vulnerable function\r\n", dwOverflowSize);

Overflow(pOverflowBuf, dwOverflowSize);

return 0;

`}`
```

图8 用自定义的SEH handler喷射堆栈，覆盖现有的EXCEPTION_REGISTRATION_RECORD结构体

[![](https://p2.ssl.qhimg.com/t01c54a523b6b56fe8e.png)](https://p2.ssl.qhimg.com/t01c54a523b6b56fe8e.png)

图9 溢出堆栈并覆盖现有默认SEH handler EXCEPTION_REGISTRATION

我们得到的不是EXE中FakeHandler函数上的断点，而是得到一个STATUS_INVALID_EXCEPTION_HANDLER异常(代码0xC00001A5)。这是一个源于SafeSEH的安全缓解异常。SafeSEH是一个安全缓解措施，仅适用于32位PE文件。在64位PE文件中，一个名为IMAGE_DIRECTORY_ENTRY_EXCEPTION的永久性（非可选）数据目录取代了原来在32位PE文件中的IMAGE_DIRECTORY_ENTRY_RIGHT数据目录。SafeSEH与GS特性都是在Visual Studio 2003版本中发布的，随后在Visual Studio 2005版本中成为了默认设置。 

[![](https://p5.ssl.qhimg.com/t01bff7e18ffae2bb4c.png)](https://p5.ssl.qhimg.com/t01bff7e18ffae2bb4c.png)

什么是SafeSEH，它是如何工作的？
1. 在Visual Studio 2019中，SafeSEH是默认设置的。它通过使用/SAFESEH标志进行配置，我们可以在Project -&gt; Properties -&gt; Linker -&gt; Advanced -&gt; Image Has Safe Exception Handlers中进行相应的设置。
1. SafeSEH编译的PE文件含有一个有效的SEH handler地址列表，位于名为SEHandlerTable的表中，我们可以在其IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG数据目录中指定。
1. 每当触发异常时，在执行EXCEPTION_REGISTRATION_RECORD链表中的每个handler的地址之前，Windows会检查该handler是否位于映像内存的范围内（表明它与加载的模块有关），如果是的话，就会用它的SEHandlerTable检查这个handler地址对有关模块是否有效。
在图8中，我们是通过堆栈溢出的方式来注册handler的，通过这种方式创建的handler是无法被编译器所识别的（因此，也不会添加到SEHandlerTable中）。通常情况下，编译器会将作为__try __except语句的副作用而创建的handler添加到这个表中。在禁用SafeSEH后，再次运行这段代码会导致堆栈溢出，执行被喷入的handler。

[![](https://p1.ssl.qhimg.com/t013779995f151f87f7.png)](https://p1.ssl.qhimg.com/t013779995f151f87f7.png)

图10 堆栈溢出，导致执行了伪造的SEH handler，该handler被编译为PE EXE映像的主映像

当然，虽然自2005年以来Visual Studio就默认启用了SafeSEH，但是，在现代应用程序中是否仍然存在禁用了SafeSEH的已加载PE代码呢？在自己探索这个问题的时候，我写了一个PE文件扫描工具，以便在系统范围内检测每个文件是否存在（或缺乏）漏洞缓解措施。当我使用这个扫描工具处理我的Windows 10虚拟机上的SysWOW64文件夹（并对非SafeSEH PEs进行过滤）后，结果令人大跌眼镜。

[![](https://p4.ssl.qhimg.com/t010b86e2695ffbb582.png)](https://p4.ssl.qhimg.com/t010b86e2695ffbb582.png)

图11Windows 10 VM上的SysWOW64文件夹中的SafeSEH的PE缓解措施的扫描统计信息 

看来，微软本身也有相当多的非SafeSEH PE，特别是至今仍在随Windows10一起提供的DLL。扫描我的Program Files文件夹后，得到的结果则更有说服力，大约有7%的PE文件缺乏SafeSEH保护。事实上，尽管我的虚拟机上安装的第三方应用程序很少，但从7-zip、Sublime Text到VMWare Tools，几乎每个应用程序都至少含有一个非SafeSEH模块。即使在进程的地址空间中只有一个这样的模块，也足以绕过其堆栈Cookie缓解措施，进而使用本文中探讨的技术利用堆栈溢出漏洞。

值得注意的是，在如下所示两种不同的情况下，SafeSEH可以被认为对PE生效的，它们是我的工具在扫描中使用的标准：
1. 在IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG数据目录中存在上述的SEHandlerTable以及SEHandlerCount大于零的情况。
1. IMAGE_DLLCHARACTERISTICS_NO_SEH标志被设置在IMAGE_OPTIONAL_HEADER.DllCharacteristics的header字段。
假设一个没有采用SafeSEH措施的模块被加载到一个易受攻击的应用程序中，对于exploit编写者来说，仍然还面临令一个重要的障碍。回到图10，尽管一个伪造的SEH HANDLER通过堆栈溢出被成功执行，但是这个handler被编译到了PE EXE映像本身中。所以，为了实现任意代码执行，我们需要执行一个存储在堆栈上的伪造SEH HANDLER（一个shellcode）。 



## DEP &amp; ASLR

由于存在DEP和ASLR防御机制，在堆栈上将我们的shellcode用作伪异常handler存在多个障碍：
1. 由于存在ASLR机制，我们不知道Shellcode在堆栈上的地址，因此无法将其嵌入到我们的溢出内容中以喷射到堆栈中。
1. 由于存在DEP机制，在默认情况下，堆栈本身以及扩展的shellcode是不可执行的。
随着2004年Windows XP SP2的问世，DEP首次在Windows世界得到了广泛的采用，并且从那时起，DEP已经成为当今使用的几乎所有现代应用程序和操作系统的普遍特性。它是通过使用硬件层内存页的PTE头部中的一个特殊位（NX，也就是不可执行位）来实现的，默认情况下，该位将在Windows中所有新分配的内存上被设置。这意味着攻击者必须显式创建可执行内存区域，方法是通过诸如KERNEL32.DLL!VirtualAlloc之类的API分配具有可执行权限的新内存，或者通过使用诸如KERNEL32.DLL!VirtualProtect之类的API将现有的非可执行内存修改为可执行的。这样做的一个副作用是，由于栈和堆在默认情况下都是不可执行的，因此，我们无法直接从这些位置执行shellcode，换句话说，我们必须首先为它开辟一个可执行的内存区域。 

从exploit编写的角度来看，理解DEP的关键在于，DEP是一种要么全有要么全无的缓解措施：要么应用于进程内的所有内存，要么不应用于进程内的所有内存。如果使用/NXCOMPAT标志编译生成进程的主EXE，则整个进程将启用DEP。与诸如SafeSEH或ASLR之类的缓解措施形成鲜明对比的是，并不存在非DEP DLL模块之类的东西。

[![](https://p2.ssl.qhimg.com/t01feb51202872454cb.png)](https://p2.ssl.qhimg.com/t01feb51202872454cb.png)

从exploit编写的角度来看，DEP的解决方案早已被理解为面向返回的编程（ROP）。原则上，现有的可执行内存将与攻击者提供的堆栈一起以小片段的形式回收，以实现为我们的shellcode划分可执行区域的目标。创建自己的ROP链时，我选择使用KERNEL32.DLL!VirtualProtect API，以便使存放shellcode的堆栈区域是可执行的。该API的原型如下所示： 

```
BOOL VirtualProtect(

LPVOID lpAddress,

SIZE_T dwSize,

DWORDflNewProtect,

PDWORD lpflOldProtect

);
```

在ASLR问世之前，如果可以通过溢出来控制堆栈，就可以将这五个参数作为常量植入堆栈，然后触发一个EIP重定向，使其指向KERNEL32.DLL中的VirtualProtect函数（其基地址是静态的）。在这里，唯一的障碍是——我们不知道作为第一个参数传递或作为返回地址使用的shellcode的确切地址。后来，攻击者利用NOP sledding技术（在shellcode的前面填充一大段NOP指令，即0x90）解决了这个问题。然后，exploit编写者可以推断出shellcode在堆栈中的大致区域，并在这个范围内选取一个地址并将其直接植入溢出内容中，从而通过NOP sled将这个猜测转化为精确的代码执行。

随着2006年Windows Vista中ASLR的出现，ROP链的创建变得有些棘手，因为现在：
1. DLL的基址和VirtualProtect的基址变得不可预测。
1. shellcode的地址难以猜测。
1. 包含可执行代码片段的模块的地址变得不可预测。 
[![](https://p0.ssl.qhimg.com/t014aa62e52aae3455a.png)](https://p0.ssl.qhimg.com/t014aa62e52aae3455a.png)

这不仅对ROP链提出了更多的要求，同时，还要求其实现要更加精确，因此，NOP sled（1996年左右的经典形式）成为ASLR时代的牺牲品。这也导致了ASLR绕过技术成为了DEP绕过技术的前提条件。如果不绕过ASLR，从而至少定位含有漏洞的进程中一个模块的基地址，就无法知道ROP Gadget的地址，从而无法执行ROP链，也就无法调用VirtualProtect函数来绕过DEP。

要创建一个现代的ROP链，我们首先需要这样一个模块：我们可以在运行时预测其基地址的模块。在大多数现代漏洞利用技术中，这是通过使用内存泄漏漏洞来实现的（这个主题将在本系列的字符串格式错误和堆损坏续集中加以探讨）。为了简单起见，我选择在易受攻击进程的地址空间中引入一个非ASLR模块（来自我的Windows 10虚拟机的SysWOW64目录）。在继续之前，必须了解非ASLR模块背后的概念（以及在exploit编写过程中的作用）。

从exploit编写的角度来看，以下是我认为最有价值的ASLR概念：
1. 在Visual Studio 2019中，ASLR是默认设置的。它使用/DYNAMICBASE标志进行配置，我们可以在项目设置的Project -&gt; Properties -&gt; Linker -&gt; Advanced -&gt; Randomized Base Address字段中进行配置。
1. 当使用该标志编译PE文件时，它（在默认情况下）总是导致创建一个IMAGE_DIRECTORY_ENTRY_BASERELOC数据目录（存储在PE文件的.reloc段中）。如果没有这些重定位信息，Windows就无法重建模块的基地址并执行ASLR。
1. 编译后的PE将在其IMAGE_OPTIONAL_HEADER.DllCharacteristics头部中设置IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE标志。
1. 当PE被加载时，将为其选择一个随机的基地址，并且其代码/数据中的所有绝对地址都将使用重定位部分进行重定位。这个随机地址在每次启动时都是不同的。
1. 如果用于启动进程的主PE(EXE)启用了ASLR，也会导致栈和堆被随机化。 
您可能会注意到，这实际上会导致两种不同的情况，其中可能会出现非ASLR模块。第一种情况是显式编译模块以排除ASLR标志(或在该标志存在之前编译)，第二种情况是设置了ASLR标志，但由于缺少重新定位而无法应用。

开发人员的一个常见错误是，在他们的编译器中联合使用ASLR标志和“strip relocations”选项，他们认为这样生成的二进制文件是受ASLR保护的，而实际上它仍然是易受攻击的。从历史上看，非ASLR模块非常常见，甚至在Windows7+ Web浏览器攻击中被滥用，并在商业恶意软件中大获成功。现在，这类模块已经逐渐变得稀缺，这在很大程度上是因为ASLR已经成为诸如Visual Studio之类的IDE中默认启用的一种安全缓解措施。令人惊讶的是，我的扫描软件在我的Windows10虚拟机上发现了大量非ASLR模块，许多位于在System32和SysWOW64目录中。

[![](https://p2.ssl.qhimg.com/t017d9447786e9c958c.png)](https://p2.ssl.qhimg.com/t017d9447786e9c958c.png)

图12 在我的Windows 10虚拟机的SysWOW64目录中找到的非ASLR模块 

值得注意的是，图12中显示的所有非ASLR模块都具有非常不同（且唯一）的基地址。这些都是Microsoft编译的PE文件，其本意就是不使用ASLR，之所以这么做，很可能是出于性能或兼容性的原因。它们将始终加载到image_optional_header.imageBase中指定的映像基地址处（图12中突出显示的值）。显然，这些独特的映像基地址是编译器在创建时随机选择的。通常情况下，PE文件都会在其PE头部中包含默认映像基地址值，如0x00400000（用于EXE）和0x1000000（用于DLL）。这种专门创建的非ASLR模块与因失误而创建的非ASLR模块（如下面图13所示）形成了鲜明的对比。

[![](https://p0.ssl.qhimg.com/t011c6eefdf03d0c27e.png)](https://p0.ssl.qhimg.com/t011c6eefdf03d0c27e.png)

图13 在我的Windows 10 VM的“Program Files”目录中找到的非ASLR模块 

这是在最新版本的HXD Hex Editor中作为重定位剥离(不知情的开发人员的旧优化习惯)副作用而创建的非ASLR模块的一个主要例子。值得注意的是，您可以在上面的图13中看到，与图12中的模块(具有随机基地址)不同，这些模块都具有相同的默认映像基地址0x00400000（已经被编译到它们的PE头部中）。这与其PE头部中存在的IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE标志相结合，表明编译它们的开发人员假设它们将使用随机地址进行加载，而不是在0x00400000处进行加载，并认为它们会受到ASLR机制的保护。然而，在实践中，我们可以肯定它们总是被加载到地址0x00400000处，尽管已经启用了ASLR——因为在没有重新定位数据的情况下，操作系统是无法在初始化期间重新设置它们的基地址的。

通过回收非ASLR模块的可执行段(通常是它们的.text段)中的代码，我们能够构造相应的ROP链来调用KERNEL32.DLL!VirtualProtect API，并为堆栈上shellcode禁用DEP保护机制。

在图12中可以看出，我选择了SysWOW64中的非ASLR模块msvbvm60.dll作为ROP链，因为它不仅缺少ASLR保护，而且还缺少SafeSEH(考虑到我们必须知道在溢出时写入堆栈的伪造SEH handler/stack pivot gadget的地址，这是一个至关重要的细节)。此外，这里还通过IAT导入了KERNEL32.DLL!VirtualProtect，这一细节极大地简化了ROP链的创建过程，下一篇文章将对此进行深入的探讨。 



## 小结

在本文中，我们为读者详细介绍了SEH劫持技术，以及DED和ASLR防御机制，在接下来的文章中，我们将继续为读者讲解如何创建ROP链。
