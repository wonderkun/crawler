> 原文链接: https://www.anquanke.com//post/id/186424 


# 深入探索在野外发现的iOS漏洞利用链（六）


                                阅读量   
                                **462386**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者googleprojectzero，文章来源：googleprojectzero.blogspot.com
                                <br>原文地址：[https://googleprojectzero.blogspot.com/2019/08/jsc-exploits.html](https://googleprojectzero.blogspot.com/2019/08/jsc-exploits.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t013ea5d7d4c6cd018b.jpg)](https://p4.ssl.qhimg.com/t013ea5d7d4c6cd018b.jpg)



在这篇文章中，我们会分析在iOS设备上获得普通权限shell的WebKit漏洞利用方法，这里的所有漏洞都可以在iOS上的沙盒渲染器进程（WebContent）中实现shellcode代码执行。虽然iOS上的Chrome也会受到这些浏览器漏洞的攻击，但攻击者只是使用它们来定位Safari和iPhone的位置。

这篇文章首先会简要介绍每个被利用的WebKit漏洞以及攻击者是如何从中构建内存读/写原语的，然后概述了用于进行shellcode代码执行的技术以及是如何绕过现有的JIT代码注入缓解措施的。

有意思的是，这些漏洞中没有一个漏洞绕过了在A12设备上启用的基于PAC的JIT强化缓解措施。漏洞利用会按漏洞支持的最新iOS版本进行，如果漏洞利用中缺少该版本检查，则会根据修复日期和之前的漏洞猜测支持的版本范围。

沙盒渲染器进程利用首先获得内存读/写功能，然后将shellcode注入JIT的区域来获得本机的代码执行权限。看起来似乎每次爆出新的重大可利用漏洞，新的漏洞就会被加入框架进行利用来做读/写检查，然后插入到现有的漏洞利用框架中。对漏洞的利用使用的也是常见的漏洞利用技术，例如首先创建addrof和fakeobj原语，然后伪造JS对象以实现读/写。

对于许多漏洞利用程序，目前还不清楚它们是否已经在一些0day或1day上进行过成功的利用。现在也还不知道攻击者是如何首先获得这些漏洞信息的。通常，他们都是使用修复完发布后的公共漏洞来利用的。WebKit在将修复版本发送给用户之前会发布漏洞的详细信息。[CVE-2019-8518](https://bugs.chromium.org/p/project-zero/issues/detail?id=1775)是在2019年2月9日的WebKit HEAD中公开修复的，提交时为[4a23c92e6883](https://github.com/WebKit/webkit/commit/4a23c92e6883b230a437bcc09f94422d7df8756c)。此提交包含一个测试用例，该测试用例触发了漏洞并导致对JSArray的越界访问，这种情况通常很容易被利用。但是，该修复程序仅在2019年3月25日发布iOS 12.2的用户中发布，是在有关漏洞的详细信息公开后一个半月才发布的。技术能力突出的利用者可以在几天时间内替换底层漏洞，从而获得利用最新设备的能力，而无需自行挖掘新漏洞。这可能至少发生在以下某些漏洞中。

为了做比较，以下列出了其他浏览器供应商是如何处理这种漏洞窗口问题的：
- Google与Chromium存在同样的问题（例如，提交的[52a9e67a477b](https://chromium.googlesource.com/v8/v8.git/+/52a9e67a477bdb67ca893c25c145ef5191976220)修复了[CVE-2018-17463](http://www.phrack.org/papers/jit_exploitation.html)）。但是，似乎最近的一些漏洞发布不再包含JavaScript测试用例。例如，我们的团队成员Sergey Glazunov报告的以下两个针对漏洞的修复：[aa00ee22f8f7](https://chromium.googlesource.com/v8/v8.git/+/aa00ee22f8f7722b505fc24acf7e544dfe59ce77)（针对漏洞[1784](https://bugs.chromium.org/p/project-zero/issues/detail?id=1784)）和[4edcc8605461](https://chromium.googlesource.com/v8/v8.git/+/4edcc860546157cb35940663afb9af568595888f)（针对漏洞[1793](https://bugs.chromium.org/p/project-zero/issues/detail?id=1793)）。
- Microsoft将开源Chakra引擎中的安全修复程序保密处理，直到修复程序已发送给用户才公开。然后发布修复后的程序并发布CVE编号。有关此示例，请参阅commit [7f0d390ad77d](https://github.com/microsoft/ChakraCore/commit/7f0d390ad77d838cbb81d4586c83ec822f384ce8)。但是，应该注意的是Chakra将很快被Edge中的V8（Chromium的JavaScript引擎）所取代。
- Mozilla直接禁止了公共存储库中的安全修复，他们会直接发布下一个版本。此外，也不会公开用于触发漏洞的JavaScript测试用例。
但是，值得注意的是，即使拿不到JavaScript测试用例，仍然可以通过代码补丁中编写PoC并最终利用漏洞。



## 0x01 漏洞利用1：iOS 10.0~10.3.2

此漏洞利用的目标是CVE-2017-2505，最初由lokihardt报告为Project Zero issue [1137，](https://bugs.chromium.org/p/project-zero/issues/detail?id=1137)并于2017年3月11日在WebKit HEAD中通过提交[4a23c92e6883](https://github.com/WebKit/webkit/commit/4a23c92e6883b230a437bcc09f94422d7df8756c)修复。该修复程序随后于5月15日发布给iOS 10.3.2用户。有趣的是，漏洞利用exp几乎与WebKit存储库中的漏洞报告和测试文件完全相同。可以在下图中看到，左边的图像显示在WebKit代码存储库中发布的测试用例，右边显示了触发漏洞的在野漏洞利用代码的一部分。

[![](https://p0.ssl.qhimg.com/t01b1b783e4eeb94ea4.png)](https://p0.ssl.qhimg.com/t01b1b783e4eeb94ea4.png)

该漏洞会导致使用受控数据写入会实现JSC堆越界。攻击者利用破坏受控JSObject的第一个QWord，改变其结构ID（将运行时类型信息与JSCell相关联）来使其显示为Uint32Array。这样，它们实际上创建了一个假的TypedArray，会直接允许它们构造一个内存读/写原语。



## 0x02 漏洞利用2：iOS 10.3~10.3.3

该漏洞是针对CVE-2017-7064或者其变体的，其最初由lokihardt发现并报告为问题[1236](https://bugs.chromium.org/p/project-zero/issues/detail?id=1236)。该漏洞已于2017年4月18日在WebKit HEAD中通过提交[ad6d74945b13修复](https://github.com/WebKit/webkit/commit/ad6d74945b13a8ca682bffe5b4e9f1c6ce0ae692)，并在2017年7月19日发布给了iOS 10.3.3的用户。 该漏洞会导致未初始化的内存被视为JS数组的内容，通过堆操作技术，可以控制未初始化的数据，此时可以通过双精度和JSValues之间的类型混淆构造addrof和fakeobj原语，从而通过构造伪造的TypedArray获得内存读/写。



## 0x03 漏洞利用3：iOS 11.0~11.3

此漏洞利用是WebKit漏洞[181867](https://bugs.webkit.org/show_bug.cgi?id=181867)，CVE编号可能是CVE-2018-4122。它于2018年1月19日在WebKit HEAD中修复，并且在2018年3月29日发布给了iOS 11.3用户。该漏洞是典型的JIT side-effect问题。目前还不清楚攻击者是否在2018年初就知道了这个漏洞。该漏洞通过混淆未初始化的double和JSValue数组构建addrof和fakeobj原语，然后通过再次伪造获得内存读/写一个类型化的数组对象。



## 0x04 漏洞利用4：iOS 11.3~11.4.1

此漏洞利用是针对2018年5月16日提交中[b4e567d371fd中](https://github.com/WebKit/webkit/commit/b4e567d371fde84474a56810a03bf3d0719aed1e)修复的漏洞，并对应于WebKit漏洞报告[185694](https://bugs.webkit.org/show_bug.cgi?id=185694)。不幸的是，我们无法确定分配给此问题的CVE，但似乎该补丁程序在2018年7月9日发布给了iOS 11.4.1的用户。这是另一个JIT side-effect问题，类似于前一个漏洞，再次构造fakeobj原语来伪造JS对象。但是，现在已经发布了Gigacage缓解措施。因此，构造伪ArrayBuffers / TypedArrays不再有用了。

该漏洞利用构造了一个fake unboxed double Array，并获得了一个初始的，有限的内存读/写原语。然后使用该初始原语来禁用Gigacage缓解措施，然后继续使用TypedArrays来执行后面的的漏洞利用。



## 0x05 漏洞利用5：iOS 11.4.1

该漏洞利用是针对CVE-2018-4438漏洞的，lokihardt报告为[1649](https://bugs.chromium.org/p/project-zero/issues/detail?id=1649)。这个漏洞是在2018年10月26日使用commit [8deb8bd96f4a](https://github.com/WebKit/webkit/commit/8deb8bd96f4a27bf8bb60334c9247cc14ceab2eb)修复的，[并](https://github.com/WebKit/webkit/commit/8deb8bd96f4a27bf8bb60334c9247cc14ceab2eb)在2018年12月5日发布给了iOS 12.1.1用户。该错漏洞可以构建一个具有代理原型的数组，然后，可以通过在JIT编译代码中触发更改，将此漏洞转换为JIT side-effect问题。该漏洞与之前的漏洞非常相似，首先使用有限的JS阵列读/写禁用Gigacage缓解措施，然后通过TypedArrays执行完全读/写的shellcode进行注入。



## 0x06 漏洞利用6：iOS 12.0~12.1.1

此漏洞利用的目标是CVE-2018-4442，此漏洞最初由lokihardt发现，并在2018年10月17日提交为[1699](https://bugs.chromium.org/p/project-zero/issues/detail?id=1699)，并在HEAD中使用commit [1f1683cea15c](https://github.com/WebKit/webkit/commit/1f1683cea15c2af14710b4b73f89b55004618295)修复了此漏洞，随后于2018年12月5日发布到了iOS 12.1.1的用户手机上 。相较于其他漏洞，这个漏洞是一个在JavaScript引擎中的UAF漏洞。攻击者通过释放butterfly对象的属性就可以利用UAF漏洞，然后使用JSBoundFunction的m_boundArgs回收内存空间，数组会反复调用func.bind（）。

如果成功的话，攻击者可以释放butterfly对象加载属性来访问内部对象m_boundArgs。这样，就可以通过使m_boundArgs稀疏数组调用绑定函数来构造OOB访问。

这个漏洞已经被利用过，这就是为什么m_boundArgs的定义边上会出现注释：`// DO NOT allow this array to be mutated!`。



## 0x07 漏洞利用7：iOS 12.1.1~12.1.3

最后的这个漏洞利用和Linus Henze在此处利用的方法是相同的：[https](https://github.com/LinusHenze/WebKit-RegEx-Exploit)：[//github.com/LinusHenze/WebKit-RegEx-Exploit](https://github.com/LinusHenze/WebKit-RegEx-Exploit)，这又是一个JIT side-effect问题。它的WebKit [bugtracker](https://bugs.webkit.org/show_bug.cgi?id=191731) id是[191731](https://bugs.webkit.org/show_bug.cgi?id=191731)。目前还不清楚分配的CVE编号是什么，可能是CVE-2019-6217，这是在那一年由Flouroacetate团队在Mobile Pwn2Own期间披露的。该漏洞似乎已于2018年11月16日修复，并于2019年1月22日发布给了iOS 12.1.3的用户。

不是像Linus那样使用WASM对象获取内存读/写，攻击者将新漏洞加入之前的漏洞利用框架并再次创建假JS数组以获得初始内存读/写权限，然后以相同方式继续利用。



## 0x08 执行Shellcode

可以进行内存读/写后，渲染器执行shellcode进行权限提升。实现shellcode执行的方式在所有漏洞中都是相同的：通过绕过JIT缓解措施来覆盖现有函数的JIT代码然后调用该函数。

主要是通过创建可写JIT区域的第二个“隐藏”映射，然后保持JIT区域的第一个映射不可写。然而，这种方法有一个问题，就是必须有一个“jit_memcpy”函数被调用来将生成的代码复制到JIT区域中。因此，执行ROP或JOP代码使受控shellcode作为参数执行此功能仍然可行。攻击者确实也是这么做的，通过在代码生成期间签名JIT代码并稍后验证签名，这个漏洞在启用了PAC的设备被缓解了。

更详细地说，攻击者构造一个JOP链，由三个不同的gadget组成，这些gadget使用受控参数执行任意函数的函数调用。为了启动JOP链，他们用JOP链的第一个gadget替换`escape` JS函数的函数指针。然后，JOP链执行对“jit_memcpy”函数的调用，以使shellcode覆盖先前编译的函数的JIT代码。最后替换了`escape`的函数指针，并将其指向JIT区域内的shellcode。
