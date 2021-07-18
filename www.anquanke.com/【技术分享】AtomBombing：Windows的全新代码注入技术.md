
# 【技术分享】AtomBombing：Windows的全新代码注入技术


                                阅读量   
                                **109390**
                            
                        |
                        
                                                                                                                                    ![](./img/85675/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：endgame.com
                                <br>原文地址：[https://www.endgame.com/blog/chakra-exploit-and-limitations-modern-mitigation-techniques](https://www.endgame.com/blog/chakra-exploit-and-limitations-modern-mitigation-techniques)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](./img/85675/t01cdc22054ce063acc.jpg)](./img/85675/t01cdc22054ce063acc.jpg)

翻译：[knight](http://bobao.360.cn/member/contribute?uid=162900179)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**前言**

通过利用缓解技术中的弱点，绕过HA-CFI和CFG进行代码注入。

<br>

**正文**

去年11月，Microsoft发布了Microsoft Edge的安全更新程序，其中就包含了Google Project Zero团队发现的漏洞补丁CVE-2016-7200和CVE-2016-7201。今年早些时候，Brian Pak发表了一个概念验证（POC）漏洞，证明这两个漏洞可以一起被使用。 不久之后，这两个漏洞被包括在几个流行的开发包中。漏洞的利用似乎主要是通过POC的剪切/粘贴来实现的。

POC存在弱点，我将会讨论它，然而在它的原始形式下，它却设法绕过所有的微软的漏洞缓解。POC演示了如何正确的抵消漏洞补丁中复杂的反攻击技术和并获得执行权限。CVE-2016-7200是指chakra.dll中的array.filter函数类型混淆错误漏洞。在这个帖子里，它允许攻击者确定在堆上创建的对象的地址。CVE-2016-7201是chakra.dll中的另一个类型混淆错误漏洞，这一次是在JavascriptArray :: FillFromPrototypes当中。它使攻击者可以在任意内存上进行读/写。

微软有一个稳定的实施利用缓解技术的跟踪记录，从EMET（利用防护工具的行业标准），到嵌入Windows 10和Edge的内置缓解。利用漏洞绕过这些技术 – 甚至是利用未被破坏漏洞 – 这都是很有趣的事，可以帮助我们了解当前状态。

在Endgame，我们不断测试我们检测漏洞和预防攻击的能力，使我们可以应对最新的威胁，确保我们可以继续提供最强大的防御机制。 我们对这个POC非常感兴趣，因为它为我们进一步研究提供了方向，并且为我们的客户带来了更周全的保护。

在这篇文章中，我不会深入研究漏洞，而是会将重点放在最小POC中所强调的利用缓解技术中的弱点上。 我将通过一个适用于Chakra POC的攻击链来说明研究这个问题，并介绍我们是如何通过创新一些预防方法来提高黑客攻击的代价的。

[![](./img/85675/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d338685deec454c4.png)

<br>

**开发阶段**

**存储器的准备**

大多数漏洞在获得执行权限之前，都需要进行准备步骤，将攻击者控制的东西（例如，ROP，shellcode）放到已知位置的存储器中。 该步骤可以以多种形式实行，并且通常称该步骤为堆修整，或其子集之一的堆喷射。虽然这些技术大多数很难检测到一些有用的东西，但它往往可以给防御者提供第一次检测恶意事件的机会。

堆喷射主要设施有两个–探测器和干扰物。探测器，如NOZZLE，监视内存的分配和检查内存中恶意行为的指标。干扰器，如BuBBle和DieHarder，试图通过增加配置随机化 的方法来降低堆喷出的可靠性，阻塞NOP-sleds或保护exploit常用的地址（0x0c0c0c0c等）。

整个博客链可以专门用于猫和鼠标游戏的内存的开发和检测。由CVE-2016-7200启用的解决方案是：如果攻击者选择存储器，系统就会停止使用该存储器。

从技术上讲，在最广泛的意义上说CVE-2016-7200的作用就是准备存储器，由于它使用解剖刀的精度，使得当前缓解技术不太可能会注意到它。

CVE-2016-7200的实现如下图所示：

[![](./img/85675/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018b10a3fd3ea5d966.png)

putdataandgetaddr()一次性使用的内存泄漏（稍后讨论）：

[![](./img/85675/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cdd90ce813d21dd8.png)

并再次放置shellcode：

[![](./img/85675/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f404f247ce203995.png)

你可以看到，有一些分配，NOP-sled是不必需的，并且大多数据是良性的（shellcode数据可以被检测为代码，但很少会被标记为恶意代码）。

**漏洞的配置**

在这一步没有任何缓解措施，也没有什么可写的，因为这里所采取的行动取决于所涉及的漏洞和攻击者选择的执行路径。

Chakra POC使用CVE-2016-7201创建读取/写入的功能，稍后会使用到。

**内存泄露**

随着地址空间布局随机化（ASLR）的引入，而且现在ASLR被使用的很普遍，攻击者需要在他们的开发中采取一个额外的步骤。 他们需要通过在内存中查找目标模块的地址来定位自己。

由于Chakra POC已经具有对象和读/写原语的地址，因此获取chakra.dll的原地址只需要从我们的对象中获取vtable，找到它的一个函数的地址，然后减去适当的基于dll版本偏移。

[![](./img/85675/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ea13acb856df6c47.png)

**Payload的配置**

为了在大多数的操作系统和目标版本中有效的，许多漏洞都是通过动态的方法来定位开发功能的位置（例如，VirtualProtect，VirtualAlloc等）。 这种查找通常是通过搜索目标dll的导出地址表来完成。 一个很好的例子就是用Flash漏洞来开发PE.as模块：

[![](./img/85675/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0184e8e61c1607ca6f.png)

诸如Microsoft EMET中的EAF / EAF +之类的缓解措施就是阻止那些对DLL头的位置进行未经授权的访问的行为。

Chakra POC通过修改需要查找的硬编码地址来避免检查。

[![](./img/85675/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01953736f73af2e5cb.png)

这种方法有一个固有的弱点。在漏洞利用中，使用硬编码偏移在破坏一些现有漏洞缓解方面是一种有效的办法。但总的来说，这种做法有局限性。 硬编码地址增加了漏洞开发的时间，而且还需要不断更新以使目标可以在动态环境中生存下去。

<br>

**代码执行**

接下来，攻击者必须中断预定的执行流程，并开始执行自己的议程。传统上，这是通过将堆栈指针旋转到攻击者控制的内存来完成的。在这一点上，有一个常见的缓解就是安全产品会偶尔验证堆栈指针是否指向当前线程的堆栈。

Chakra POC通过将它的ROP直接放在堆栈上来绕过这些检查。

Endgame采用HA-CFI，它有助于确保代码执行的完整性，并且在抵御大多数攻击方面非常成功。 HA-CFI可以检测异常的控制流，并在堆栈指针被修改之前阻止大多数攻击。通常，堆栈支点是ROP的第一个小工具（下面讨论），同样也是执行流程中的第一个异常。

Microsoft利用控制流保护（CFG）来达到类似的目地。CFG对间接调用添加了一个附加检查，以确保它们被定向到有效目标。

Chakra POC在很大程度上得益于硬编码地址，劫持ScriptEngine :: ExecutePendingScripts的返回地址，并在exploit脚本完成时获得对堆栈的控制。通过不间接调用和避免异常的代码流，从而来绕过HA-CFI和CFG。

<br>

**返回定向编程（ROP）**

ROP是一个过渡到执行控制标准的方法。当攻击者的shellcode保存在不可执行的内存中时，通常需要执行此步骤。

在检测ROP的过程中已经进行过大量的研究，这导致几个技术被部署在了安全产品上。

1.关键功能的正确性检查。这里的想法是，如果一个攻击者被迫使用ROP，他/她可能需要使用一个简短的函数列表，如CreateProcess或virtualprotect来移动到payload进行执行。当调用这些函数，可以执行一系列检查来检测程序的好坏。

a.	 堆栈指针的完整性

b.	堆叠的完整性

c.	返回地址优先呼叫

d.	 VirtualProtect不会尝试使堆栈可执行

2.代码模拟。 Microsoft的EMET和ROPGuard采用的缓解模拟在检测类ROP行为上，在当前处于领先地位。

3.硬件。 kBouncer利用硬件性能监视器来检测类似ROP的行为。

[![](./img/85675/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019ab546dfb4f922f7.png)

Chakra POC确实是使用了ROP（如上所示），但是它有几个特性，使得这些技术都很难检测到它。首先，ROP只包含两个小工具和一个返回shellcode。这避免了硬件辅助小工具链的检测，如kBouncer，需要更长的ROP链才可以达到硬件辅助小工具链的检测标准。第二，VirtualProtect调用是一个合法的函数，它包装了VirtualProtect。 这使得堆栈在到达VirtualProtect的任何检查时都会显示正常。

之所以第二个ROP gadget和APIHook_VirtualProtect的组合代码用于模拟技术检查感觉非常良好，是因为他们检查VirtualProtect后的代码都是合法的代码。

<br>

**总结**

Chakra POC是一个很好的利用缓解规避技术的研究案例，我研究的还很基础。在这个POC中使用的技术不是最新的，事实上，大多数技术已经发布了一段时间。使用它们的两个原因：1）漏洞本身允许它们的使用; 2）内置到Windows 10和Edge中的缓解需要使用它们。 我们知道，漏洞会一直存在，我们应该把重点放在攻击的检测和预防上。诸如Microsoft，Google，Adobe等许多软件供应商已经在检测/预防战中投入了大量资源。像英特尔这样的硬件厂商也加入了斗争。 像Endgame这样的安全公司将提供更多有效的方法来阻止对手。每个缓解都可能给攻击者增加一些代价。 我们的工作是使这个成本尽可能高。

Chakra POC和已被发现的攻击显示，代价还不够高，攻击者仍然可以进行攻击。它表明Windows 10和Edge不能为大家提供安全港湾。在Endgame，我们不断创新开发检测攻击/预防攻击的能力，通过分析最新的漏洞和综合防治技术来使最具创造性的攻击者的攻击链停在最早阶段。
