> 原文链接: https://www.anquanke.com//post/id/86335 


# 【技术分享】分析Firefox的shared array buffer的UAF漏洞利用


                                阅读量   
                                **95979**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：phoenhex.re
                                <br>原文地址：[https://phoenhex.re/2017-06-21/firefox-structuredclone-refleak](https://phoenhex.re/2017-06-21/firefox-structuredclone-refleak)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0152e461b58e26a0da.jpg)](https://p1.ssl.qhimg.com/t0152e461b58e26a0da.jpg)

译者：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**0x00 前言<br>**



本文探讨了在结构化克隆算法处理shared array buffer时发生的引用泄漏的问题。同时缺少溢出检查，能被利用来执行任意代码。

分为下面几个部分：

背景，漏洞，利用，总结

我们的漏洞利用的目标是linux平台的Firefox Beta 53。请注意发布版本不受这个bug的影响，因为由于这个bug，shared array buffer从Firefox 52开始被禁用了，在Firefox53中默认禁用。完整的漏洞利用代码在这里。

<br>

**0x01 背景**



这个漏洞和利用需要对于结构化克隆算法和shared array buffer有基本的理解，这些将在本节介绍。

1. 结构化克隆算法

Mozilla开发者文档描述：

[![](https://p4.ssl.qhimg.com/t018f7256d3a17d337e.png)](https://p4.ssl.qhimg.com/t018f7256d3a17d337e.png)

SCA用于Spidermonkey-internal序列化以便在不同的上下文传递对象。与json相反，它能够解决循环引用。在浏览器中，postMessage()使用序列化和反序列化的功能：

postMessage()函数在下面两种场景使用；

1. 通过window.postMessage()通信时

2. 和web workers通信时，其是并行执行JavaScript代码的捷径。

一个worker的简单流程如下：

[![](https://p4.ssl.qhimg.com/t01db71a841f679c366.png)](https://p4.ssl.qhimg.com/t01db71a841f679c366.png)

相应的worker脚本worker_script.js能通过注册一个onmessage监听器接收obj：

[![](https://p0.ssl.qhimg.com/t0130c92e2edccc9bac.png)](https://p0.ssl.qhimg.com/t0130c92e2edccc9bac.png)

在不同的窗口通信的过程是类似的。在这些情况中，接收脚本执行于不同的全局上下文中，并且无法访问发送者上下文的对象。因此对象需要传递并且在接收脚本的上下文中重新创建。为了实现这个，SCA将在发送者的上下文中序列化obj，并在接收者的上下文中反序列化，从而创建了个拷贝。

SCA的代码能在js/src/vm/StructuredClone.cpp。两个主要的结构定义：JSStructuredCloneReader和JSStructuredCloneWriter。JSStructuredCloneReader在接收线程上下文处理反序列化对象，JSStructuredCloneWriter在发送者线程上下文中处理序列化对象。处理序列化对象的主要函数是JSStructuredCloneWriter::startWrite()：

[![](https://p4.ssl.qhimg.com/t012e5f5195f781252e.png)](https://p4.ssl.qhimg.com/t012e5f5195f781252e.png)

根据对象的类型，如果是原始类型直接序列化，或者基于对象类型调用函数进一步序列化。这些函数确保了任何属性或者数组元素被递归序列化了。这种情况下当obj是一个SharedArrayBufferObject并且函数执行最终会调用JSStructuredCloneWriter::writeSharedArrayBuffer()。

最后，如果提供的既不是原始类型也不是序列化的对象，它将抛出错误。反序列化使用相同方式，它将序列化作为输入、创建新的对象并为他们分配内存。

2. Shared array buffer

Shared array buffer提供了一种方式来创建共享内存，其能跨上下文传递。他们通过SharedArrayBufferObjectC++类实现，其继承于NativeObject，是表示大部分JavaScript对象的基类。下面是抽象描述（如果你看源代码，你将看见它不像这个这么定义明确，但是这将帮助你理解下文描述的内存布局）：

[![](https://p1.ssl.qhimg.com/t01a403aac84e84197f.png)](https://p1.ssl.qhimg.com/t01a403aac84e84197f.png)

Rawbuf是一个SharedArrayRawBuffer对象的指针，其存储底层的内存缓冲区。当通过postMessage()发送时，SharedArrayBufferObjects将在接收者上下文中重新创建新的对象。另外，SharedArrayRawBuffers在不同上下文之间共享。因此SharedArrayBufferObject的单一拷贝有他们的rawbuf属性指向相同的SharedArrayRawBuffer对象。为了内存管理，SharedArrayRawBuffer保存了一个引用计数器refcount_：

[![](https://p2.ssl.qhimg.com/t016bf8aa4ba4dab520.png)](https://p2.ssl.qhimg.com/t016bf8aa4ba4dab520.png)

引用计数器refcount_记录了有多少SharedArrayBufferObjects的引用。当序列化一个SharedArrayBufferObject时，在JSStructuredCloneWriter::writeSharedArrayBuffer()它会递增，并且在SharedArrayBufferObject终结中递减：

[![](https://p2.ssl.qhimg.com/t01d105e2cc7092a2e9.png)](https://p2.ssl.qhimg.com/t01d105e2cc7092a2e9.png)

[![](https://p3.ssl.qhimg.com/t0169183cd6aecd4006.png)](https://p3.ssl.qhimg.com/t0169183cd6aecd4006.png)

然后SharedArrayRawBuffer::dropReference()将检查是否有更多的引用，并释放底层内存。

<br>

**0x02 漏洞**



有两种bug，单独都不太可能利用，但是组合起来能执行任意代码。

1. SharedArrayRawBuffer::refcount_的整型溢出

SharedArrayRawBuffer的refcount_属性没有整型溢出保护：

[![](https://p2.ssl.qhimg.com/t01a04ff2f817371940.png)](https://p2.ssl.qhimg.com/t01a04ff2f817371940.png)

在反序列化时在JSStructeredCloneWriter::writeSharedArrayBuffer调用这个函数：

[![](https://p3.ssl.qhimg.com/t0108216eb90d73e03d.png)](https://p3.ssl.qhimg.com/t0108216eb90d73e03d.png)

代码简单的递增了refcount_，并且SharedArrayRawBuffer::addReference()没有验证它溢出了并变成了0。回顾下refcount_，被定义成uint32_t整型，意味着上面的代码需要触发2^32次才能溢出。在这里的主要问题是每次调用postMessage()将创建一个SharedArrayBufferObject的拷贝，从而分配0x20字节的内存。Firefox目前堆的限制是4GB，溢出需要128G，使得不可能被利用。

2. 在SCA中的引用泄漏

然而不幸的是，有另一个bug使得我们能绕过内存限制。回顾下postMessage()首先序列化，然后反序列化对象。在反序列化过程中创建对象的拷贝，但是refcount_在序列化期间已经递增了。如果postMessage()在序列化SharedArrayBufferObject之后并在反序列化之前失败，将不创建SharedArrayBufferObject的拷贝，但是refcount_能递增。

看下序列化，有很简单的方式使其失败：

[![](https://p5.ssl.qhimg.com/t01fc300f1e66e20c4d.png)](https://p5.ssl.qhimg.com/t01fc300f1e66e20c4d.png)

如果被序列化的对象既不是原始类型也不是SCA支持的对象，序列化将抛出一个JS_SCERR_UNSUPPORTED_TYPE的错误，将不会发生反序列化（包括内存分配）。下面是简单的PoC，能递增refcount_但不拷贝SharedArrayBuffer：

[![](https://p0.ssl.qhimg.com/t01dcfd083cbcca1853.png)](https://p0.ssl.qhimg.com/t01dcfd083cbcca1853.png)

一个数组包含一个SharedArrayBuffer和一个序列化的函数。SCA首先序列化数组，然后递归序列化SharedArrayBuffer（从而递增它的原始缓冲区的refcount_），最终是函数。然而，函数序列化不支持，将抛出错误，不允许创建对象拷贝的反序列化过程。现在refcount_是2，但是只要一个SharedArrayBuffer指向原始缓冲区。使用这个引用泄漏refcount_能不分配任何内存实现溢出。

<br>

**0x03 利用**



虽然内存限制解决了，但是触发bug需要调用2^32次postMessage()。在现代机器上将要花几个小时执行。为了一个合理的执行时间，bug需要更快的触发。

1. 提高性能

简单的方法是每次调用postMessage()序列化多个sab：

[![](https://p3.ssl.qhimg.com/t01a5bf04fd738fb1b7.png)](https://p3.ssl.qhimg.com/t01a5bf04fd738fb1b7.png)

不幸的是，SCA支持反向引用，将不会增长refcount_超过1，而是作为第一个的反向引用。因此sab的拷贝是需要的。实际上，他们也能使用postMessage()创建：

[![](https://p3.ssl.qhimg.com/t015683e7d21fc22d4d.png)](https://p3.ssl.qhimg.com/t015683e7d21fc22d4d.png)

一个数组包含一个sab，被发送给脚本自身，并且当被接收时，被添加到存在的拷贝数组中。现在在拷贝中有两种不同的对象指向相同的SharedArrayRawBuffer。通过重复拷贝拷贝的数组，我们能获得大量的拷贝。在我们的漏洞利用中，我们创建了0x10000个拷贝（只需要16次调用postMessage()）。然后我们使用这些拷贝完成引用泄漏，使得调用postMessage的次数达到2^32/0x10000=65536。

进一步的性能提高能通过多个web workers充分利用所有的CPU核心并行利用引用泄漏。每个worker接收一个0x10000个shared array buffer的拷贝，然后在一个循环中执行引用泄漏：

[![](https://p0.ssl.qhimg.com/t01c279dbfa0345b3bb.png)](https://p0.ssl.qhimg.com/t01c279dbfa0345b3bb.png)

一旦执行了需要的次数，将报告给主脚本已完成你。如果所有的worker已经完成，refcount_将溢出，保存值为1.通过删除一个sab，refcount_将变为0，共享原始缓冲区将在下个垃圾回收的时候被释放。在漏洞利用中，一个SharedArrayBufferObject被垃圾回收将继而调用dropReference()。这将影响将引用计数置为0，将触发原始缓冲区的释放：

[![](https://p3.ssl.qhimg.com/t011fb31bb83f22eb4d.png)](https://p3.ssl.qhimg.com/t011fb31bb83f22eb4d.png)

Do_gc()的一种实现在这里。

此时，SharedArrayRawBuffer被释放了，但是引用还一直在sab中，允许对释放的内存读写访问，导致UAF利用。

2. 将UAF变为读写原语

因为我们有了释放的内存的引用，我们能分配大量的对象以便在内存中分配目标对象给我们的引用。分配器通过mmap请求更多的内存，将返回SharedArrayRawBuffer的munmaped的内存。为了将这变为ArrayBuffer对象的任意读写原语。这些对象包含真实数组内容的内存区域的一个指针。如果一个ArrayBuffer分配在之前释放的内存中，指针将被覆盖指向我们想要的任意内存。

为了做到这个，我们分配0x60个ArrayBuffer。这是底层缓冲区的最大值，将在ArrayBuffer头后直接内敛存储。将每个都标记0x13371337值，然后在第一次发生时搜索那个值，我们能找到ArrayBuffer的位置：

[![](https://p4.ssl.qhimg.com/t01236c40c7ef2af20e.png)](https://p4.ssl.qhimg.com/t01236c40c7ef2af20e.png)

此时，一些缓冲区应该分配在之前释放的SharedArrayRawBuffer内存中。使用那个引用我们搜索0x13371337。一旦找到，我们用另一个值0x13381338标记并保存偏移：

[![](https://p5.ssl.qhimg.com/t01b57105948bc98763.png)](https://p5.ssl.qhimg.com/t01b57105948bc98763.png)

我们遍历所有分配的ArrayBuffer，搜索0x13381338以便找到确切的ArrayBuffer：

[![](https://p0.ssl.qhimg.com/t01c68b4ba1fc691133.png)](https://p0.ssl.qhimg.com/t01c68b4ba1fc691133.png)

最后buffers[ptr_access_idx]是我们能控制（通过加减一些偏移修改sab_view[ptr_overwrite_idx]）的ArrayBuffer的内存。

回顾下数组内容位于头后面，意味着头开始于sab_view[ptr_overwrite_idx-16]。指向数组缓冲区的指针能通过写sab_view[ptr_overwrite_idx-8] 和 sab_view[ptr_overwrite_idx-7]来覆盖（写64位的指针为两个32位的值）。一旦指针被覆盖了，buffers[ptr_access_idx][0]允许读写被指定位置的32位的值。

3. 实现任意代码执行

一旦能任意读写内存，我们需要一种控制RIP的方法。因为libxul.so包含了大部分的浏览器的代码，包括Spidermonkey（没有使用全部的RELRO编译），全局偏移表（GOT）能被覆盖用来改变代码执行。

首先，我们需要泄漏libxul.so的位置。我们简单的泄漏任意原生函数（如Data.now()）的指针。函数内部使用JSFunction对象表示，并存储了原生实现的地址。为了泄漏那个指针，函数被设置为ArrayBuffer（能读写内存）的一个属性。接着一串指针，原生指向libxul.so的指针能被泄漏。我们不详细讨论对象属性的内存组织，因为在Phrack paper中有完美的描述。。现在我们有了libxul.so的Date.now()的地址，我们能硬编码Firefox beta53中的libxul.so的偏移，以便得到GOT的地址。

最后，我们使用system()（同样使用libxul.so泄漏）覆盖GOT中的一个函数。在利用中，我们使用Uint8Array.copyWithin()继而针对我们控制的字符串调用memmove，因此覆盖memmove@GOT将执行system：

[![](https://p3.ssl.qhimg.com/t0178529eaeb2060725.png)](https://p3.ssl.qhimg.com/t0178529eaeb2060725.png)

这个技术是受到saelo的启发“exploit for the feuerfuchs challenge from the 33C3 CTF. “。

运行利用，弹出计算器：

[![](https://p1.ssl.qhimg.com/t0180f2305f96fade11.png)](https://p1.ssl.qhimg.com/t0180f2305f96fade11.png)

<br>

**0x04 总结**



这个溢出的修复很快，在commit d4b0fe7948中实现了。代码添加了捕获溢出，并检测到报错。在commit c86b9cb593中修复了引用泄漏。

这个bug的触发原本估计要4个小时才能溢出。然而，使用多个worker能加快进程，在8核机器上只要大约6-7分钟能稳定的弹出计算器。完整的利用能在这找到。


