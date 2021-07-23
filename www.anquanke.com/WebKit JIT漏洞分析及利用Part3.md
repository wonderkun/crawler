> 原文链接: https://www.anquanke.com//post/id/216609 


# WebKit JIT漏洞分析及利用Part3


                                阅读量   
                                **108105**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者googleprojectzero，文章来源：googleprojectzero.blogspot.com
                                <br>原文地址：[https://googleprojectzero.blogspot.com/2020/09/jitsploitation-three.html](https://googleprojectzero.blogspot.com/2020/09/jitsploitation-three.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t012c6b49a5314b7ea7.png)](https://p2.ssl.qhimg.com/t012c6b49a5314b7ea7.png)



## iOS JIT 加固的变化

在过去的浏览器利用中，在渲染器进程中具有读/写能力的攻击者只需要在JIT rwx区域中编写任意的shellcode就可以了。

2016年，在WebKit中部署了针对这种技术的首个基于软件的缓解:“Bulletproof JIT”。它的工作原理是将JIT区域映射两次，一次作为r-x用于执行，一次作为rw-用于写入。可写映射设置在内存中的一个隐秘位置，然后Bulletproof JIT依赖于包含jit_memcpy函数的—x区域，该函数将指定数据复制到JIT可写映射中，而不泄露其地址。但是由于缺乏CFI，这种缓解很容易失败，例如通过ROP。此外，如果攻击者能够通过某种方式泄露可写映射的位置，那么他们可以轻松地向其写入shellcode。

随着iPhone Xs引入的硬件缓解，即APRR和PAC, OS JIT的加固变得更加强大，为了更全面地了解各种iOS exploit缓解，感兴趣的读者可以参考Siguza的演讲“[Evolution of iOS mitigations](https://papers.put.as/papers/ios/2019/Siguza_-_Mitigations.pdf)”。



### <a class="reference-link" name="APRR"></a>APRR

虽然这个缩写词的扩展名在苹果之外并不为人所知，但它的功能却是众所周知的。无需过多讨论技术细节，感兴趣的读者可以参考[Siguza’s blog post on APRR](https://siguza.github.io/APRR/)，APRR本质上是启用每个线程的页面权限。这是通过使用专用的CPU寄存器将页表输入权限映射到其实际权限来实现的。这样一来，页面权限就可以成为APRR寄存器的索引，而APRR寄存器现在拥有实际的页面权限。作为一个简化的示例，考虑以下APRR映射：

[![](https://p3.ssl.qhimg.com/t012ba9ca3a34cca9fc.png)](https://p3.ssl.qhimg.com/t012ba9ca3a34cca9fc.png)

通过以这种方式设置APRR寄存器，它将有效地执行严格的W ^ X策略：任何页面都不能同时可写和可执行。

在WebKit中，APRR现在用于保护JIT区域:JIT区域的页表权限是rwx，但是如上面所示，W^X是强制执行的。因此，JIT区域实际上是r-x，直接写入它将会触发segfault。由于JIT区域需要不断地写入（当编译新代码或更新现有代码时），因此有必要更改该区域的权限。这是通过一个“unlock”函数完成的，该函数将索引7处的APRR寄存器的值（对应于页表权限rwx）更改为rw-。但是，这只会发生在将数据复制到JIT区域的线程上，而对于所有其他线程，该区域仍然是r-x。这可以防止攻击者在JIT编译器线程解锁该区域时与之竞争。下面是performJITMemcpy函数的简化的代码，它负责将代码复制到JIT区域：

```
ALWAYS_INLINE void* 
performJITMemcpy(void *dst, const void *src, size_t n)
`{`
    os_thread_self_restrict_rwx_to_rw();
    memcpy(dst, src, n);
    os_thread_self_restrict_rwx_to_rx();
    return dst;
`}`
```

还要注意ALWAYS_INLINE的使用，它强制在每个调用callsite内联该函数。稍后会详细介绍。

APRR非常容易绕过。两种主要的攻击类型是:
- 1.在performJITMemcpy函数(或者实际上是一个内联的函数)中执行ROPing、JOPing等操作，然后将任意代码复制到JIT区域中。
- 由于编译器将机器码汇编到一个[临时堆缓冲区中](https://github.com/WebKit/webkit/blob/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/JavaScriptCore/assembler/AssemblerBuffer.h#L146)，然后将其复制到JIT区域，因此攻击者可能在复制之前就破坏了堆上的机器码。
### <a class="reference-link" name="PAC"></a>PAC

PAC是Pointer Authentication Codes的缩写，是另一种硬件特性，它允许将加密签名存储在指针的高位中，否则就不用了。它已经成为很多研究的主题，并且现在已经有了很好的文档，比如Brandon Azad的一篇[文章](https://googleprojectzero.blogspot.com/2019/02/examining-pointer-authentication-on.html)。在PAC启用的情况下，每个代码指针都必须具有一个有效的签名，在将控制流传递给它之前要检查这个签名。由于PAC密钥保存在寄存器中，攻击者无法访问它们，因此攻击者无法伪造有效的指针。PAC因此可以立即阻止攻击者执行上述攻击1，另外，由于performJITMemcpy函数被标记为ALWAYS_INLINE，因此将不存在指向该函数的函数指针，使攻击者能够使用可控参数调用此函数。

攻击2)需要额外的工作来缓解。这个问题主要在LinkBuffer::copyCompactAndLinkCode函数内部，该函数负责将之前汇编的机器码复制(并链接和压缩)到JIT区域。如果攻击者能够在此函数将机器码复制到JIT区域之前破坏包含机器码的堆缓冲区，则攻击者将获得任意代码执行。通过在汇编过程中对机器码计算基于PAC hash,然后在复制过程中重新计算和验证该hash，可以缓解这种攻击。通过这种方式，可以确保将汇编程序发出的任何内容也复制到JIT区域中，而不进行修改。虽然有可能欺骗编译器来发出某种程度上可控的代码，但通常不再可能执行任意的指令，因为汇编器只支持有限的指令集。

### <a class="reference-link" name="Summary"></a>Summary

APRR和PAC共同实现以下目标：
- JIT区域被有效地映射为r-x，并且只在很短的一段时间内“解锁（unlocked）”，并且只在更新JIT代码时对单个线程“解锁”。这可以防止攻击者直接写入JIT区域。
- PAC用于强制执行CFI，从而防止攻击者执行经典的代码重用攻击，如ROP，JOP等。也无法直接调用performJITMemcpy 函数，因为它总是内联到其调用方中
- PAC用于确保将发出的JIT代码复制到JIT区域之前的完整性
这篇文章的剩余部分将讨论不同的bypass方法。



## 绕过 JIT 加固

接下来介绍的各种不同的攻击将设法对程序的执行流进行一定程度的控制，这种控制可以实现第二阶段的exploit（最有可能是某种形式的沙箱逃逸），这很可能是攻击者通常试图实现的目标。但是要记住，如果没有站点隔离之类的东西，在渲染器进程中具有内存读/写功能的攻击者通常能够构造UXSS攻击，从而获得对各种web credentials和sessions的访问，甚至可能通过web workers获得持久性。这些问题在过去已经得到证明，因此将不作进一步讨论。

### <a class="reference-link" name="Shellcode-less%20Exploitation"></a>Shellcode-less Exploitation

首先，需要要注意的是攻击者并不一定需要执行shellcode。例如，滥用ObjectiveC和JavaScriptCore runtime 是有可能的，这样就可以通过JavaScript执行任意的函数和系统调用。这进而可以用于实现利用链的下一阶段，从而避免完全绕过JIT加固。这一点已经被证明，因此在本文中没有进一步的研究。

同样，尽管JIT最终输出的机器代码通过PAC保护，但它的中间输出，特别是各种IRs，DFG, B3 和 AIR，以及其他支持的数据结构没有受到保护，因此容易受到攻击者的操纵。因此，一种可能的方法是破坏JIT的IR代码，例如欺骗编译器生成对带有控制参数的任意函数的调用。这可能会授予一个与上面的非常相似的原语，即能够执行可控的系统调用，因此在本文中没有进一步研究。

### <a class="reference-link" name="%E6%9D%A1%E4%BB%B6%E7%AB%9E%E4%BA%89%EF%BC%88Race%20Conditions%EF%BC%89"></a>条件竞争（Race Conditions）

竞态条件似乎在PAC+APRR边界上广泛存在。下面是一个典型的performJITMemcpy调用示例，在本例中是在JIT生成的代码中重新获得指针大小的立即数：

```
int buffer[4];
buffer[0] = moveWideImediate(Datasize_64, MoveWideOp_Z, 0,  
                             getHalfword(value, 0), rd);
buffer[1] = moveWideImediate(Datasize_64, MoveWideOp_K, 1, 
                             getHalfword(value, 1), rd);
buffer[2] = moveWideImediate(Datasize_64, MoveWideOp_K, 2, 
                             getHalfword(value, 2), rd);
if (NUMBER_OF_ADDRESS_ENCODING_INSTRUCTIONS &gt; 3)
    buffer[3] = moveWideImediate(Datasize_64, MoveWideOp_K, 3, 
                                 getHalfword(value, 3), rd);
performJITMemcpy(address, buffer, sizeof(int) * 4);
```

在这里，首先将加载立即值所需的机器指令发送到栈分配的缓冲区中，然后通过performJITMemcpy将该缓冲区复制到JIT区域。因此，如果另一个线程在将栈分配的缓冲区复制到JIT区域之前破坏了它，攻击者将获得任意代码的执行。但是，这里的竞争窗口非常小，输掉竞争可能会导致正在使用的栈内存被损坏，可能导致崩溃。(这段代码还存在另一个理论上的bug:如果NUMBER_OF_ADDRESS_ENCODING_INSTRUCTIONS小于4，那么它将把未初始化的栈内存复制到JIT区域……)

最后，我决定从这个研究中排除不可能安全丢失的竞争条件，因为可以说，迫使攻击者在冒着进程崩溃的风险同时赢得竞争的缓解机制在某些方面如预期有效。

### <a class="reference-link" name="%E4%B8%8D%E5%8F%97%E4%BF%9D%E6%8A%A4%E7%9A%84%E4%BB%A3%E7%A0%81%E7%9A%84%E6%8C%87%E9%92%88"></a>不受保护的代码的指针

另一个可能的攻击途径是PAC使用不当的情况。例如：
- 1.设置为可能被攻击者破坏的原始指针签名的位置
- 2.调用可由攻击者控制的无符号函数指针的位置
通过对汇编代码进行静态分析，可以找到这样的情况。虽然我最初希望使用binary ninja的各种ILs来实现这一点，因为它们支持各种数据流分析，但由于缺少对PAC指令的支持，这使得这一点变得更加困难，我转而使用一个简单的IDAPython脚本，该脚本将输出以PAC签名指令（如PACIZA）结尾的指令序列。在DyldSharedCache映像上运行时，该脚本将输出数千行，例如

```
libz.1:__text:0x1b6ba1444  ADRL X16, sub_1B6BA9434; PACIZA X16
```

这个“gadget”本质上接受一个常量(sub_1B6BA9434的地址)，并使用一个密钥和一个context对其进行签名。因此，对于攻击者来说，并不是很关系这些，因为有符号的值是无法控制的。过滤掉这些安全的代码片段后，剩下的一个经常出现的代码模式如下:

```
ADRP            X16, #_pow_ptr_3@PAGE
LDR             X16, [X16,#_pow_ptr_3@PAGEOFF]
PACIZA          X16
```

此代码片段从可写页面加载一个原始指针，然后使用PACIZA指令对其签名。因此，攻击者可以通过覆盖内存中的原始指针来绕过PAC，然后以某种方式执行该代码。似乎每次来自不同编译单元的函数作为指针被引用而不是被直接调用时，编译器都会发出这种易受攻击的代码。这个特殊的代码片段是JavaScriptCore中下列c++代码的机器代码：

```
LValue Output::doublePow(LValue xOperand, LValue yOperand)
`{`
    double (*powDouble)(double, double) = pow;
    return callWithoutSideEffects(B3::Double, powDouble, xOperand, yOperand);
`}`
```

当对已知的double值调用Math.pow进行优化时，JIT编译器将使用此函数。在这种情况下，编译器发出对C pow函数的调用，并为此加载该函数的地址并使用该函数签名。由于编译器的bug，导入的函数指针被放在了一个可写的部分，但是也没有被PAC保护。这个问题的PoC很简单:

```
// offset from iOS 13.4.1, iPhone Xs
let powImportAddr = Add(jscBase, 0x34e1d570);
memory.writePtr(powImportAddr, new Int64('0x41414141'));

function trigger(x) `{`
    return Math.pow(x, 13.37);
`}`
for (let i = 0; i &lt; 10000000; i++) `{`
    trigger(i + 0.1);
`}`
```

这将导致PC=0x41414141的崩溃，说明PAC被绕过了。

使用稍微修改过的IDAPython脚本搜索第二种漏洞类型(调用未保护指针)，也得到了一个代码片段:

```
MOV             W9, #0x6770
ADRP            X16, #___chkstk_darwin_ptr_19@PAGE
LDR             X16, [X16,#___chkstk_darwin_ptr_19@PAGEOFF]
BLR             X16
```

这段代码位于许多大型函数的开头，它分支到`__chkstk_darwin`函数，该函数可能负责防止超大的stackframe在栈溢出时“跳过”栈保护页。但是，由于某些原因，该函数的指针是从一个可写的内存区域加载的，也没有被PAC保护。因此，它再次可以执行任意代码，如以下代码所示:

```
// offset from iOS 13.4.1, iPhone Xs
let __chkstk_darwin_ptr = Add(jscBase, 0x34e1d430);
memory.writePtr(__chkstk_darwin_ptr, new Int64('0x42424242'));

// Just need to trigger FTL compilation now, we'll crash in FTL::lowerDFGToB3
function foo(x) `{`
    return Math.pow(x, 13.37);
`}`
for (let i = 0; i &lt; 10000000; i++) `{`
    foo(i + 0.1);
`}`
```

这之所以能够工作，是因为基本上在任何大栈帧的函数中都广泛使用__chkstk_darwin，，其中一个栈帧(即FTL::lowerDFGToB3)是在JIT编译期间执行的。

这两个问题被报告给苹果作为[Project Zero issue #2044](https://bugs.chromium.org/p/project-zero/issues/detail?id=2044)，随后在7月15日iOS 13.6中被修复，分配为CVE-2020-9870。用于查找这些gadget的IDAPython脚本也可以在[issue #2044](https://bugs.chromium.org/p/project-zero/issues/detail?id=2044)的报告中找到。

### <a class="reference-link" name="%E6%8E%A7%E5%88%B6%20Mach%20Messages"></a>控制 Mach Messages

受到与Project Zero团队成员Brandon Azad多次聊天的启发，这个bypass的思路是在mach message结构通过mach_msg系统调用发送出去之前破坏它。在iOS和macOS上，内核接口的很大一部分，整个IOKIT驱动接口，以及基本上所有用户空间的IPC都是通过mach message实现的，这使它成为一个完美的exploit原语。例如，通过改变内存保护或重新映射页面，可以使用与虚拟内存相关的mach系统调用来绕过PAC或APRR。另外，控制mach消息将再次允许从JavaScript实现阶段2的exploit，除非需要执行BSD系统调用的能力。

找到发送mach消息的代码的一个简单但不完美的方法是将mach_msg函数与一个Frida脚本挂钩，然后根据调用栈删除它的调用。这是不完美的，因为它会错过在正常操作期间很少执行的代码路径，但实现起来非常快。在WebKit渲染程序中这样做将大致显示以下对mach_msg的相关调用:
- IPC与浏览器进程通信
- XPC与其他系统进程通信
- Mach对内核的系统调用
最终，所有这些情况看起来都是条件竞争，因为构造的mach消息大部分会立即发送出去，而不会在内存中停留一段时间(理想情况下攻击者可以控制)，在这段时间内它可能会被破坏。由于在这些情况下失去竞争会导致堆（在IPC和XPC通信的情况下）或栈（在mach syscall的情况下）损坏，因此这些情况无法满足稳定的bypass的要求。

### <a class="reference-link" name="%E6%BB%A5%E7%94%A8%E4%BF%A1%E5%8F%B7%E5%A4%84%E7%90%86%E7%A8%8B%E5%BA%8F"></a>滥用信号处理程序

PAC（和许多其他缓解机制一样）依赖于使进程崩溃来阻止攻击者。因此，一个值得关注的目标是可以中断进程崩溃的信号处理机制。

WebKit支持渲染程序内部的信号处理，它使用一些JavaScriptCore优化。例如，JSC支持WASM代码的执行模式，其中省略了所有边界检查，但WASM堆后面有一个32GB的保护区域。由于WASM内存访问使用32位索引，如果在WASM中发生无效访问，它将始终访问一个保护页，导致segfault，然后运行WASM信号处理程序。然后，处理程序将重新匹配WASM代码，这样出错的线程将在恢复时引发JavaScript异常。

WebKit中的异常处理基于mach异常处理，而不是UNIX信号处理，以下是它工作原理的概述:
- 1.当一个异常在某些渲染器线程中发生时，一个GCD工作线程会被内核唤醒来处理这个异常
- 2.线程执行mach_msg_server_once，它从内核获取描述异常的mach消息，分配应答消息，然后将这两个消息传递给处理程序函数
- 3._Xmach_exception_raise_state_identity是自动生成的MIG函数，是为异常消息注册的处理程序。它将解析输入的mach消息，在崩溃时提取寄存器内容之类的值，然后执行“real”处理函数
- 4.catch_mach_exception_raise_state现在将遍历已注册处理程序的链表，并执行每个处理程序，还将它们可以修改的输出寄存器状态传递给它们。根据处理程序是否处理了异常，这个函数将返回KERN_SUCCESS或KERN_FAILURE
- 5.回到_Xmach_exception_raise_state_identity中，返回值和输出寄存器状态用于填充应答消息
- 6.mach_msg_server_once 最后将应答消息发送到内核，然后将控制权返回给GCD
- 7.如果返回值是KERN_SUCCESS，那么内核现在要么继续使用输出寄存器状态恢复崩溃的线程，要么终止它
下图显示了该过程：

[![](https://p2.ssl.qhimg.com/t0172d9a63177572251.png)](https://p2.ssl.qhimg.com/t0172d9a63177572251.png)

现在启用以下攻击:
- 1.单链表的处理程序列表被破坏并变成一个循环。这是可能的，因为与处理程序函数指针相反，列表元素的下一个指针不受PAC保护
- 2.访问冲突是在单独的线程中造成的。这将导致GCD线程“陷入” catch_mach_exception_raise_state ，由于循环而无限循环
- 3.攻击者控制下的线程现在搜索所有线程栈（它们在内存中连续分配），寻找catch_mach_exception_raise_state的返回地址。一旦找到，它现在也可以访问reply mach消息，因为指向它的指针会溢出到栈上。然后，攻击者可以直接控制应答消息。特别是，现在可以设置新的寄存器状态(PC除外，PC受PAC保护)和指示是否处理异常的返回值。
- 4.栈上溢出的指针被替换为另一个指针，从而导致_Xmach_exception_raise_state_identity将信号处理程序的实际返回值（将是KERN_FAILURE）写入不同的内存位置，而其调用者mach_msg_server_once会将攻击者控制的应答消息发送回内核
- 5.该线程修复了处理程序列表，导致处理程序线程脱离循环并从catch_mach_exception_raise_state 返回。内核现在将接收到完全由攻击者控制的应答消息，因此将通过攻击者控制的寄存器（和栈）上下文恢复崩溃的线程
这是一个非常强大的利用原语，本质上允许构造一个小型“调试器”，能够中断程序中的大多数数据访问，并且能够在这些点上任意地更改执行上下文。这可以用多种方式绕过PAC或APRR。可能的想法包括：
- 破坏AssemblerBuffer，使LinkBuffer将任意指令复制到JIT区域中。这将导致计算出的hash不匹配并使链接器崩溃，但这仅在复制指令后才发生，然后可以简单地捕获崩溃
- 在向LinkBuffer::copyCompactAndLinkCode中的JIT区域写入一次时发生崩溃（通过破坏之前的目标指针），并更改源寄存器的内容，以便在使用原始指令时将任意指令写入JIT区域用于hash计算
- 在LinkBuffer::copyCompactAndLinkCode期间崩溃，并在其他地方恢复执行。这将使JIT区域对该线程保持可写(尽管不是可执行)
- 暴力破解PAC代码(例如，通过反复访问、崩溃，然后更改PAC受保护的指针)，然后将JOP转换为内联performJITMemcpy的一个函数
在pwn.js文件中发布的Poc代码中，可以找到一个简单的PoC，它演示了这项技术是如何工作的。它通过破坏受PAC保护的缓冲区指针，在访问期间捕获异常，然后更改保存原始指针的寄存器并恢复执行，从而为TypedArrays实现了一个简单的PAC bypass。

此问题已报告给Apple，作为 Project Zero [issue #2042](https://bugs.chromium.org/p/project-zero/issues/detail?id=2042)。当JavaScript引擎被初始化时，通过初始化信号处理程序，然后将保存信号处理程序的内存区域标记为只读，在WebKit HEAD中使用commit [014f1fa8c2](https://github.com/WebKit/webkit/commit/014f1fa8c22d9227f8a7d877dbb3673e5a4f6e02)对其进行修复。这可以防止攻击者修改列表。7月15日，iOS 13.6的用户得到了修复，被分配为CVE-2020-9910。

### <a class="reference-link" name="%E5%8F%98%E4%BD%93"></a>变体

这种“bug”模式更为通用，并且与信号处理没有严格的关系。作为一个示例，考虑以下来自LinkBuffer::copyCompactAndLinkCode的代码:

```
if (verifyUncompactedHash.finalHash() != expectedFinalHash) `{`
    dataLogLn("Hashes don't match: ", ...);
    dataLogLn("Crashing!");
    CRASH();
`}`
```

如果在链接和复制汇编代码的过程中，JSC确定机器代码已损坏，因为加密哈希不匹配，则执行此代码。这里的问题是，攻击者可能会破坏数据，从而导致dataLogLn无限地阻塞，例如通过破坏锁或使某个循环永久运行。在那种情况下，攻击者控制的机器代码将已经被复制到JIT区域中，然后可以由攻击者在另一个线程中执行，而不用担心在与CRASH()的竞争中失败。在最初的问题被报告给苹果后不久，这个潜在的变种被发现，然后在WebKit中通过commit [e87946b7a8](https://github.com/WebKit/webkit/commit/e87946b7a86e0e0c1b11bcaf19c46ff384e5579d#diff-f751db5d3640969ae224c602ca5eba3f)修复。

再举一个例子，当JSC遇到一个错误的PAC签名时(WebKit的PtrTag机制是基于PAC的)，它在即将CRASH()之前调用了以下函数，表明攻击者破坏了关键数据:

```
void reportBadTag(const void* ptr, PtrTag expectedTag)
`{`
    dataLog("PtrTag ASSERTION FAILED on pointer ", RawPointer(ptr), ", actual tag = ", tagForPtr(ptr));
    ...
`}`
```

实际上，tagForPtr 调用最终遍历了一个链表：

```
static const char* tagForPtr(const void* ptr)
`{`
    PtrTagLookup* lookup = s_ptrTagLookup;
    while (lookup) `{`
        const char* tagName = lookup-&gt;tagForPtr(ptr);
        if (tagName)
            return tagName;
        lookup = lookup-&gt;next;
    `}`

    ...
```

因此，通过将这个列表转化为一个循环，就可以再次防止由于PAC故障而导致的崩溃。这反过来又允许对PAC进行暴力破解，或者可能泄漏一个有效签名的任意的指针，就像报告中为这个变体所记录的那样。已向 Apple报告了此变体，作为Project Zero issue #2042,然后通过提交[13e30ec7a5](https://github.com/WebKit/webkit/commit/13e30ec7a58077dfded00d722d9d9b5e71bd5e01)和[db8b3982f2](https://github.com/WebKit/webkit/commit/db8b3982f245d681677f6e8ecf72bbcc011d2058)进行了修复。

最后,甚至“广泛”的变体可能存在这个问题:如果在执行攻击者可以阻止的操作（例如循环或锁定操作）之前，有代码将敏感值（例如身份验证后的原始指针）临时泄漏到栈中，那么攻击者可能无需赢得竞争就可以破坏敏感数据。尽管在整个研究过程中没有发现这样的地方。



## 总结

从本质上说，在检测到failure条件之后，但在进程最终终止之前执行的每一段代码都应该被视为一个攻击面，如果攻击者能够生成此代码块，则攻击者有可能“获胜”。对于信号处理，这将变得更加复杂，例如：

```
if (security_failure) `{`
    CRASH();
`}`
```

实际上更像：

```
if (security_failure) `{`
    signal_handler();
    CRASH();
`}`
```

理想情况下，信号处理将因此完全从关键进程中移除，或者至少限制在较少的信号中。总而言之，这些修复程序的实现速度表明，苹果致力于PAC和APRR作为严重安全问题的缓解机制。



## 结论

这篇文章介绍了绕过WebKit的JIT加固的多种方法。虽然有些方法不起作用，或者由于各种原因没有进一步尝试，但两个之前未知的问题，以及它的多个变体，可以进行稳定的bypass。它们已报告给Apple，随后在iOS 13.6中修复，分配为CVE-2020-9870和CVE-2020-9910。

总而言之，首先要找到一个合适的漏洞，然后绕过各种缓解机制，这需要投入大量的时间。但是，对于攻击者来说，这种努力的很大一部分是一次性的，这是第一次开发exploit所必需的。之后，攻击者可能会将以前的大部分exploit工作重新用于后续漏洞。除了被利用的漏洞，苹果还迅速修复了PAC bypass，并为其分配了CVE编号。很高兴看到苹果公司承诺迅速修复，我希望他们今后继续这样做。

尽管逻辑漏洞可能会在未来允许沙箱逃逸，并且在很大程度上不受exploit缓解技术的影响，但是，一个典型的攻击链仍然需要执行渲染器shellcode，这似乎是合理的。由于这可能需要某种形式的内存破坏，因此要在不同级别上开发和维护缓解内存的漏洞，一般来说，通过PAC和APRR实现，以及更强大的沙箱似乎是值得投资的。
