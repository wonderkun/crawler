
# 【技术分享】使用结构化异常处理绕过CFG


                                阅读量   
                                **79517**
                            
                        |
                        
                                                                                                                                    ![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：improsec.com
                                <br>原文地址：[https://improsec.com/blog//back-to-basics-or-bypassing-control-flow-guard-with-structured-exception-handler](https://improsec.com/blog//back-to-basics-or-bypassing-control-flow-guard-with-structured-exception-handler)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85820/t011ff18867674802bd.jpg)](./img/85820/t011ff18867674802bd.jpg)**

****

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：160RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**0x00 前言**

本文所讲的技术基于泄漏栈地址并覆盖结构化异常处理，从而绕过CFG。

为了方便绕过，我再次选择了使用IE11的漏洞（MS16-063），在我之前的绕过CFG的文章中使用过（[1](https://improsec.com/blog/bypassing-control-flow-guard-in-windows-10)，[2](https://improsec.com/blog/bypassing-control-flow-guard-on-windows-10-part-ii)）。

<br>

**0x01 泄漏栈**

我已经有了PoC文件Clean_PoC.html，其利用漏洞获得一个读写原语，但是不够深入。在下个PoC文件Leaking_Stack.html中能泄漏当前线程的堆栈限制，这个可以通过使用kernelbase.dll中的GetCurrentThreadStackLimits做到。它执行的方法是，通过覆盖TypedArray对象的虚函数表，并使用下面的调用：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ed4d9a7bff4c4326.png)

在虚表偏移0x188处，能直接在javascript代码中调用，并且有两个参数，这是重要的，因为这个函数必须有相同数量的参数，否则堆栈不会平衡会触发异常。

GetCurrentThreadStackLimits满足Javascript的调用要求，MSDN中介绍如下：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0132e711424607436f.png)

它有两个参数，并返回栈基址和栈的最大保留地址。通过两步能找到GetCurrentThreadStackLimits的地址，首先泄漏一个kernelbase.dll的指针，然后在DLL中定位函数。第一部分能通过在定位jscript9中的Segment：：Initialize函数来完成，因为他使用了kernel32！VirtualAllocStub，继而调用kernelbase!VirtualAlloc。我通过扫描jscript9的虚函数地址并计算哈希找到了这个函数，然后使用读原语。算法如下：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0124e8f074a8fba061.png)

通过5个DWORD相加，每次向前一个字节遍历直到正确的哈希被找到。调用Kernel32！VirtualAlloc的位置在Segment：：Initialize中偏移0x37处：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019d7e5e432872d6a0.png)

读取指针得到：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ee5b62ad578f3458.png)

在偏移0x6处包含了跳转向kernelbase！VirtualAlloc：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016788ef90efdec0f2.png)

现在我们有了kernelbase.dll的地址，然后我们使用和Segment：：Initialize一样的方法找到GetCurrentThreadStackLimits的地址，代码如下：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011f9ed23fc09bb651.png)

我们现在像Theori的原始利用中一样创建一个假的虚表，并在这个函数指针的偏移0x188处覆盖虚表入口，同时记住增大TypedArray的参数大小，代码如下：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e65d55d8f22de316.png)

运行并在GetCurrentThreadStackLimits中打断点：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fefea02daa48bc25.png)

上图显示了栈的上下限制。为了从这得到能控制的指令指针，我定位了栈中的SEH链，并覆盖了一个入口，然后触发异常。虽然做了这些，但是需要记住的是Windows 10开启了SEHOP。因为SEH指针不被CFG保护，这将能绕过CFG和RFG。这些实现在文件Getting_Control.html中。

为了实现这个，我需要定位栈中的SEH链，泄漏栈限制后的SEH链如下：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ffe181cb7e785adb.png)

调试异常将变得很清晰，5个异常处理指针指向jscript9，同时MSHTML！_except_handler4似乎是个死循环。因此如果我们能覆盖5个javascript异常中的任意一个，并触发一个异常，我们将得到可控制的指令指针。在古老过时的SEH覆盖利用中通常是通过栈缓冲区溢出来覆盖SEH链，但是这将触发SEHOP，因此我们只想覆盖一个异常处理的SEH记录同时保持NSEH完整。因此这个覆盖必须精确，且SEH记录的栈地址必须泄漏。为了完成这次泄漏，我们将扫描栈，搜索SEH链，为了确保我们找到它，我们能验证最后一个异常处理是ntdll!FinalExceptionHandlerPadXX。因为最后一个异常处理函数会随着程序重启而改变，因此泄漏分为两步，首先找到正确的最后一个异常处理函数，然后再是SEH链。为了完成第一个泄漏，搜索栈中ntdll！_except_handler4，因为在栈中上下搜索它只会遇到一次：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0116d7d2c002435dc8.png)

剩下的问题是，找到ntdll!_except_handler4的地址，但是这非常简单，因为能从任何被CFG保护的函数中找到ntdll.dll的指针并包含一个间接调用。CFG的验证包含ntdll!LdrpValidateUserCallTarget的调用，并且jscript9被CFG保护，任意间接调用的函数都包含ntdll.dll的指针。在TypedArray对象虚表中偏移0x10处就有这么一个函数：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0165149e099fe269bc.png)

使用读原语，找到ntdll.dll的指针的代码如下：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011929a9d0327b8136.png)

通过使用读原语搜索特征或哈希能从ntdll.dll中能得到_except_handler4的地址，_except_handler4看起来如下：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0197a77261a8c3dd60.png)

头0x10个字节总是相同的且非常特别，因此可以使用哈希搜索：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01859f52adbdf4cb29.png)

上面的函数使用了ntdll.dll的指针作为参数。一旦我们找到了函数指针，我们能搜索栈：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019adcfda9f0ed4de3.png)

在这个地址，有如下：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01aea8f1f54147eaf1.png)

因为这在那之前的DWORD能被读取并包含：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ed86aa27595830f5.png)

找到了最后一个异常处理的函数指针。然后可以进行第二步泄露了，现在我们能看到来自jscript9的异常处理，因此它的函数指针一定位于PE代码段中，能从DLL的PE头中找到这些地址：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f19890095d3ecb7f.png)

现在有了这个，上下搜索栈，能看到栈的所有内容。算法如下：

如果一个DWORD小于0x10000000，它不在jscript9.dll中，因此移到下一个DWORD。

如果大于0x10000000，检查是否在jscript9.dll的代码段中

如果在，则栈上的4字节DWORD是指向栈的指针

如果上面两步正确，我们可能找到了SEH，因此我们尝试校验是否以最后一个异常处理结尾

如果指针中的某个不在指向栈，或者超过8个引用，它不是SEH链

在我的测试中，第一次指向jscript9.dll的指针，其中的DWORD是一个栈指针，它是SEH链，算法如下：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0170ae04165cc4f21d.png)

有了这个算法，意味着精确覆盖SEH记录是可能的，并且不会中断下一个异常处理，因此绕过SEHOP。

最后，触发异常，获得可控制的指令指针：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0132d25e713b493bf2.png)

运行结果如下：

[![](./img/85820/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ddc6d3035ce32223.png)

上图展示了调试器捕捉到的异常，并且用我们想要的0x42424242覆盖成功。这阐述了这个技术如何绕过CFG获得执行控制。它同样也能绕过RFG的实现。代码在[github](https://github.com/MortenSchenk/Bypassing_CFG_SEH)中。
