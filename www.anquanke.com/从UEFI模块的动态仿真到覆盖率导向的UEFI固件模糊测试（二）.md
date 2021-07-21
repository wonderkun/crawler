> 原文链接: https://www.anquanke.com//post/id/222541 


# 从UEFI模块的动态仿真到覆盖率导向的UEFI固件模糊测试（二）


                                阅读量   
                                **112458**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Assaf Carlsbad，文章来源：sentinelone.com
                                <br>原文地址：[https://labs.sentinelone.com/moving-from-dynamic-emulation-of-uefi-modules-to-coverage-guided-fuzzing-of-uefi-firmware/](https://labs.sentinelone.com/moving-from-dynamic-emulation-of-uefi-modules-to-coverage-guided-fuzzing-of-uefi-firmware/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01369c172a98146588.jpg)](https://p1.ssl.qhimg.com/t01369c172a98146588.jpg)



在本文中，我们将为读者详细介绍覆盖率导向的UEFI固件模糊测试技术。

在本文上一部分中，我们对UEFI的攻击面进行了全面的分析，接下来，我们将为读者介绍内存池Sanitizer。



## 内存池Sanitizer

基于突变的模糊测试技术，主要是由下面一组观察结果驱动的：
1. 有效输入发生突变后可能会变成无效输入；
1. 如果目标没有对这些无效输入进行正确处理，可能会触发内存破坏问题；
1. 内存破坏问题通常表现为崩溃。
[![](https://p5.ssl.qhimg.com/t0128f23fd75f540b76.jpg)](https://p5.ssl.qhimg.com/t0128f23fd75f540b76.jpg)

图6 基于突变的模糊测试技术示意图

就其本身而言，这些假设是相当简单化的，而且并不总是成立的。作为一个例子，让我们考虑一个简单的，基于堆栈的缓冲区溢出漏洞。如果溢出不够“深”，很可能它不会覆盖保存的返回地址，因此不会表现为崩溃。即便如此，也有两个原因使侦测这些情况变得极其重要：
1. 首先，如果运气好的话，fuzzer可能会发现其他一些突变，从而帮助将“deep”“浅”溢出转换为“深”溢出漏洞。
1. 其次，如果构建得当，即使是“浅”溢出漏洞也可能对攻击者非常有用。例如，在堆栈溢出的情况下，我们可以覆盖其他局部变量的值，从而影响程序的执行。 
为了帮助fuzzer将这些情况与实际崩溃一样对待，我们需要sanitizer助一臂之力。简单地说，sanitizer是一个非常笼统的术语，用来表示任何对执行中的代码实施更严格检查的检测策略。如果这些检查中有一项在运行时失败了，sanitizer就会故意使进程崩溃，从而通知fuzzer刚刚发现了一个潜在易受攻击的路径。

sanitizer的应用并不只限于模糊测试技术。事实上，大多数sanitizer都被开发人员用到。通过将这些工具融入到他们的工作流程中，开发人员可以快速暴露各种编程错误，否则这些编程错误可能会在很长一段时间内无法被发现。这些sanitizer的著名例子包括Google的sanitizer套件（AddressSanitizer、MemorySanitizer、LeakSanitizer等）、微软的ApplicationVerifier以及老牌的、深受欢迎的Valgrind。 

对于我们的UEFI NVRAM fuzzer来说，我们主要是对AllocatePool()和FreePool()等内存池服务进行“消毒处理（sanitization）”。和其他动态内存分配器一样，UEFI内存池也容易受到一些滥用模式的影响，例如：
1. 内存池上溢/下溢（Pool overflow/underflow）：一段行为不当的代码将数据写到了给定内存池缓冲区的边界之外，从而破坏相邻的内存。
1. 越界访问（Out-of-bounds access）：试图读取超出给定内存池缓冲区边界的数据。
1. 双重释放（Double-frees）：在这种情况下，同一个内存池块被释放两次。
1. 无效释放（Invalid frees）：试图释放一些本来就不属于内存池的内存。根据特定的内存池的实现方式，这种模式也可能导致内存破坏。
1. 释放后使用（Use after free）：在内存池块被释放后，一段代码又访问了它。
在开发sanitizer的过程中，我们从包含类似功能的BaseSAFE项目中获得了一些灵感，并借鉴了一些巧妙的想法。我们恳请您查看他们的项目，并阅读附带的论文（尤其是4.7节–Drop-In Heap Sanitizer）。本质上将，内存池sanitizerhook了许多重要的内存池服务，如allocate()和free()，并对它们进行如下处理：
1. allocate(size)：对于每一个内存分配请求，sanitizer首先会增加8个字节的辅助数据。也就是说，如果用户请求了X个字节，那么实际的内存块的大小将是X+8。接下来，要返回给调用者的指针将被移位4个字节。这样就给我们留下了两个“填充”区域，每个区域长4个字节。借助于Qiling框架提供的内存API，我们可以使这些“填充”区域变成既不可读也不可写的内存区域。因此，任何访问这些“填充”区域的尝试都会被捕获并导致异常。通过这个方案，我们可以检测到大多数的内存池上溢和下溢的情况，甚至包括是那些off-by-one漏洞所致、通常很难发现的内存池上溢和下溢情况。
[![](https://p5.ssl.qhimg.com/t01a5d5a2875a5d8c62.jpg)](https://p5.ssl.qhimg.com/t01a5d5a2875a5d8c62.jpg)

图7 一个精心构造的内存池块，用于检测内存池上溢/下溢。 
1. free(ptr)：当一个内存块被释放时，我们首先将用户可访问的部分（从P+4开始，到P+4+size结束）标记为不可访问。因此，任何试图在释放内存块后访问它的行为都会被检测到。此外，与现实世界中的堆不同（它应该考虑到性能和内存需求问题），我们必须确保不会再次分配这个内存块。这样我们就省去了维护空闲列表和管理不同内存块状态之间转换的麻烦。
[![](https://p3.ssl.qhimg.com/t01bc9b131ae38389e6.jpg)](https://p3.ssl.qhimg.com/t01bc9b131ae38389e6.jpg)

图8 一个内存池中的内存块被释放后的情况。通过让用户可见的部分也无法访问，我们就能“捕获”所有针对该内存块的UAF问题

我们要解决的另一个重大挑战是源于库函数的溢出漏洞和其他漏洞。根据设计，Unicorn引擎支持的所有hook类型只能由模拟的CPU指令触发，而不是由框架本身触发。反过来，这也会带来一些有趣而又有悖常理的东西。

作为一个具体的例子，让我们考虑一个简单的UEFI应用程序，它调用一个引导服务，如CopyMem()，其中一个缓冲区是一个标记为不可访问的内存区域。现在，假设CopyMem()的实现是由应用程序自己给出的，就像编译器选择内联这个函数一样。这种情况显然会在运行时引发异常，所以没有什么特殊的地方。 

现在，考虑一下CopyMem()的实现从来没有在二进制层面明确给出的情况。取而代之的是，对CopyMem()函数的调用被拦截，并在Qiling之上模拟其效果。这样的实现可能会利用框架特有的API来直接写入内存，从而绕过为目标内存缓冲区安装的任何hook。

[![](https://p3.ssl.qhimg.com/t0117ac99d7c5c1f7ce.jpg)](https://p3.ssl.qhimg.com/t0117ac99d7c5c1f7ce.jpg)

图9 CopyMem()服务的可能实现。通过直接写入内存，这样的实现不会触发安插在目标缓冲区上的任何hook。

为了纠正这种情况，我们扩展了sanitizer，以利用金丝雀值（canary values）。总的来说，在内存池缓冲区的一部分被标记为不可访问之前，它会被一些已知的魔术值（默认情况下为0xCD）所填充。然后，在执行结束时，sanitizer会遍历所有这些块，并验证它们没有以任何方式被破坏。使用这种技术时，我们只能在事后检查缓冲区溢出漏洞（即我们不会立即得到通知），但这比让这些漏洞逃之夭夭要好得多。

[![](https://p1.ssl.qhimg.com/t018506a6c99d41d4d9.jpg)](https://p1.ssl.qhimg.com/t018506a6c99d41d4d9.jpg)

图10 一个释放的内存池块，其中填充了金丝雀值。金丝雀值可以帮助我们检测源自被仿真的库函数的漏洞。 

然而，另一种缓解这个问题的方法源于这样一个事实，即CopyMem()和SetMem()都可以通过手工编写汇编代码的方式来轻松实现。虽然memcpy()和memset()的顶级实现确实不简单，但只需少量的x86指令就可以构造出一个简陋的、非性能导向的版本。正因为如此，一个可能的解决方案是为这些服务引入汇编版本，将它们编译并注入到仿真环境中，然后强制所有CopyMem()和SetMem()的调用方都使用它们。这样一来，所有的字节传输都变成了Unicorn引擎支持的实际CPU指令，因此，它们就很容易被各种类型的hook所拦截。

[![](https://p2.ssl.qhimg.com/t01db474280e59c1ebe.jpg)](https://p2.ssl.qhimg.com/t01db474280e59c1ebe.jpg)

图11 SetMem()的手写汇编实现。虽然它很简陋，性能也不高，但它完全实现了应有的功能——这才是最重要的。



## 小结

在本文中，我们为读者介绍了内存池Sanitizer，接下来，我们将为读者演示如何检测未初始化的内存泄露。

**（未完待续）**
