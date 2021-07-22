> 原文链接: https://www.anquanke.com//post/id/171358 


# 看我如何绕过 iPhone XS 中指针验证机制 (上)


                                阅读量   
                                **249112**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者googleprojectzero，文章来源：googleprojectzero.blogspot.com
                                <br>原文地址：[https://googleprojectzero.blogspot.com/2019/02/examining-pointer-authentication-on.html](https://googleprojectzero.blogspot.com/2019/02/examining-pointer-authentication-on.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0104789561e931d9eb.jpg)](https://p3.ssl.qhimg.com/t0104789561e931d9eb.jpg)



在这篇文章中，我将研究苹果在 iPhone XS 中使用的 A12 芯片上实现的指针验证技术，重点是苹果在ARM标准上的改进。然后，我演示了一种伪造内核指针的 PAC 签名的方法，借助于JOP(Jump-Oriented Programming)，这足以在内核中执行任意代码。遗憾的是，这项技术都在 12.1.3 中基本上被修复。事实上，针对这个漏洞的修复最初是出现在 16D5032a beta 版中，而当时我的研究已经在进行中了。

## ARMv8.3-A 指针验证

在ARMv8.3-A中，引入最大的防护机制是指针验证功能。引入指针验证后，当前大部的 POC 脚本都会失效。这个功能主要是利用指针的高位来存储**指针验证码**(PAC, Pointer Authentication Code)。它本质上就是一个指针值和一段附加信息的密码签名。在ARMv8.3-A中引入了一些特殊的指令，用于对指针 PAC 的添加，验证以及恢复。这使系统能够在密码层面确保某些指针不被攻击者篡改，从而极大地提高应用程序的安全性。

[![](https://github.com/bizky/Images/raw/master/PAC.png)](https://github.com/bizky/Images/raw/master/PAC.png)

指针验证的基本想法是，尽管指针的长度是64比特，大部分的系统的虚拟地址空间是远远比这个小的，这样会在指针中留下一些没有使用的位，而这些位可以用来存储额外的信息。在指针验证中，这些空闲位被用来存储一个比较短的验证码，这个验证码就是指的对原始的 64 位指针和 64 位上下文的签名。我们可以在将指针写入内存之前向每个想要保护的指针中插入 PAC，并在使用它之前验证它的完整性。攻击者想要修改受保护指针，必须找到或猜解正确的 PAC 才能控制程序流。

在系统的实现中，系统可以定义自己的算法来实现 PAC 的签名与验证，但是白皮书中建议使用 QARMA 分组密码。白皮书称，QARMA 是专门为指针验证设计的“一种轻量级可调整的块密码家族”，它能够接受一个128位密钥、一个64位明文值(指针)和一个64位tweak(上下文)作为输入，并生成一个64位的密文。最后，将密文截断后成为 PAC, PAC 被插入到指针未使用的扩展位中。

已经有许多文章来描述指针验证了，所以我在这里也只需要粗略的描述一些原理。<br>
感兴趣的读者可以参考[Qualcomm的白皮书](https://www.qualcomm.com/media/documents/files/whitepaper-pointer-authentication-on-armv8-3.pdf)、Mark Rutland在2017年Linux安全峰会上的[幻灯片](https://events.static.linuxfound.org/sites/events/files/slides/slides_23.pdf)、Jonathan Corbet的[LWN文章](https://lwn.net/Articles/718888/)以及[ARM A64指令集架构](https://static.docs.arm.com/ddi0596/a/DDI_0596_ARM_a64_instruction_set_architecture.pdf)以获得更多细节。

在PAC机制中，系统提供了 5 个 128 比特的密钥。其中两个密钥（ APIAKey 和 APIBKey ）用于指令指针。另外两个（ APDAKey 和 APDBKey ）用与数据指针。最后还有一个密钥（ APGAKey ）是一个特殊的通用密钥，用于通过 PACGA 指令对较大的数据块进行签名。提供多个密钥能够使系统对指针替换攻击具有一些基本的保护能力。

这些密钥的值会写入了一个特殊的系统寄存器中。这个寄存器在 EL0 中是无法访问的，意味着用户空间的进程不能读取或者修改它们。然而，在硬件层面没有提供任何其他的密钥管理功能：由每个异常级别(EL, Exception Level)运行的代码来管理较低异常级别的密钥。

为了处理 PAC, ARMv8.3-A 新引入了三类指令：
1. PAC* 类指令可以向指针中生成和插入 PAC。 比如，PACIA X8，X9 可以在寄存器X8中以 X9 为上下文，APIAKey 为密钥，为指针计算 PAC，并且将结果写回到 X8 中。同样的 PACIZA 跟 PACIA 类似，不过上下文固定为0。
1. AUT* 类指令可以验证一个指针的 PAC。 如果PAC是合法的，将会还原原始的指针。否则，将会在指针的扩展位中将会被写入错误码，在指针被简接引用时，会触发错误。比如，AUTIA X8,X9 可以以 X9 为上下文，验证 X8 寄存器中的指针。当验证成功时会将指针写回 X8，失败时则写回一个错误码。
1. XPAC* 类指令可以移除一个指针的 PAC 并且在不验证指针有效性的前提下恢复指针的原始值。
为了将指针认证与现有的操作结合起来，除了这些一般的指针认证指令外，还引入了一些特殊的变体指令：
1. BLRA* 类指令实现了一个 “authenticate-and-branch” 的操作：如果指针是合法的，则会直接branch到该地址。比如，BLRAA X8,X9 可以用指令密钥A（APIAKey），并且以 X9 作为上下文验证 X8 指针的合法性，如果合法则会 branch 到结果地址上。
1. LDRA* 类指令实现了一个 “authenticate-and-load” 的操作：如果指针是合法的，则会直接load到该地址。比如，LDRAA X8,X9 可以用数据密钥A（APDAKey），验证指针 X9, 上下文为 0，如果合法，则会将结果load到X8中。
1. RETA* 类指令实现了一个 “authenticate-and-return” 的操作：如果LR寄存器合法，则会执行RET指令。比如，RETAB 将会利用指令密钥B（APIBKey）验证 LR 的合法性，并且返回。


## 一个缺陷:签名组件

在我们开始分析 PAC 之前，我需要首先提一下一个已知的缺陷：如果一个攻击者有读写权限，可以调用系统的签名组件(signing gadgets)，那么 PAC 是可以被绕过的。签名组件指的是一组可用于对任意指针签名的指令序列。如果攻击者可以触发一个函数的执行，签名组件就从内存中读取指针、添加PAC并将其写回，那么攻击者就可以利用这个过程来伪造任意指针的PAC。



## 面对内核层攻击者的设计缺陷

就像Qualcomm白皮书中所说的那样，ARMv8.3 中指针验证设计的目的是，在攻击者具有任意内存读写权限的情况下来为系统提供一定程度的保护。然而我们的威胁模型中，内核攻击者已经有了读写权限，并且希望通过在内核指针上伪造 PAC 来执行任意代码。在面对内核层次攻击者时，我指出了设计中的三个潜在弱点:

攻击者从内存中读取PAC密钥、在用户空间中对内核指针进行签名，以及使用 B 类密钥对 A 类密钥的指针进行签名(反之亦然)。接下来我们将依次讨论每个问题。



### <a class="reference-link" name="%E4%BB%8E%E5%86%85%E6%A0%B8%E5%B1%82%E7%9A%84%E5%86%85%E5%AD%98%E4%B8%AD%E8%AF%BB%E5%8F%96PAC%E5%AF%86%E9%92%A5"></a>从内核层的内存中读取PAC密钥

首先，我们考虑一下最主要的攻击形式：攻击者从内核空间的内存中读取PAC密钥，然后计算任意内核指针的PAC。以下是白皮书中关于这类攻击者部分的摘录:

```
指针验证的目的是抵抗内存泄露攻击。PAC 是使用强加密算法保护的，因此从内存中读取加密后的指针都不比伪造指针简单。

PAC 密钥存储在寄存器中，这些寄存器不能从用户态(EL0)直接访问。因此，普通的内存泄露漏洞是不能用于提取 PAC 密钥的。
```

虽然这个描述是正确的，但是它仅仅适用于攻击用户空间程序，而不是攻击内核本身。最近的 iOS 设备似乎没有运行 hypervisor (EL2)或 secure monitor(EL3)，这意味着在系统内核(EL1)必须管理自己的 PAC 密钥。由于存储密钥的系统寄存器在内核休眠时将被清除，PAC密钥不得不存储在内核的内存中。因此，具有内核空间内存访问权限的攻击者可能会读取密钥，并使用密钥来算出任意指针的 PAC。

当然，这种攻击方法是假定了我们能够知道生成PAC是使用了什么算法，我们能够在用户态中实现它。<br>
但是，按照苹果的一贯作风，他们有很大的可能会实现一个自己的算法来替代 QARMA，而不是直接使用 QARMA。<br>
如果是这样的话，那么即使攻击者知道了 PAC 密钥，还是不足以伪造指针的 PAC: 要么我们对苹果的芯片进行逆向来还原签名算法，要么我们必须找到一种方法来利用现有的机制来为我们的伪造指针签名。

### <a class="reference-link" name="%E8%B7%A8%20EL%20%E5%B1%82%E7%9A%84PAC%E4%BC%AA%E9%80%A0"></a>跨 EL 层的PAC伪造

一种可能的方法是通过在用户空间中执行相应的PAC*指令来伪造内核指针的PAC。虽然这听起来不太可能，但有几个原因可以说明这是可行的。

苹果可能已经决定对EL0和EL1使用相同的PAC密钥，在这种情况下，我们可以直接从用户空间对内核空间的指针执行 PACIA 指令，来伪造一个内核的指针的 PAC。在文档中可以看出来，描述 PAC* 指令的伪代码并不区分该指令是在EL0还是在EL1上执行的，因此内核态与用户态应该具有相同的调用方式。

下面就是 AddPACIA() 函数的伪代码，描述了类似 PACIA 指令的实现:

```
// AddPACIA()
// ==========
// Returns a 64-bit value containing X, but replacing the pointer
// authentication code field bits with a pointer authentication code, where the
// pointer authentication code is derived using a cryptographic algorithm as a
// combination of X, Y, and the APIAKey_EL1.

bits(64) AddPACIA(bits(64) X, bits(64) Y)

    boolean TrapEL2;
    boolean TrapEL3;
    bits(1)  Enable;
    bits(128) APIAKey_EL1;

    APIAKey_EL1 = APIAKeyHi_EL1&lt;63:0&gt;:APIAKeyLo_EL1&lt;63:0&gt;;

    case PSTATE.EL of
        when EL0
            boolean IsEL1Regime = S1TranslationRegime() == EL1;
            Enable = if IsEL1Regime then SCTLR_EL1.EnIA else SCTLR_EL2.EnIA;
            TrapEL2 = (EL2Enabled() &amp;&amp; HCR_EL2.API == '0' &amp;&amp;
                        (HCR_EL2.TGE == '0' || HCR_EL2.E2H == '0'));
            TrapEL3 = HaveEL(EL3) &amp;&amp; SCR_EL3.API == '0';
        when EL1
            Enable = SCTLR_EL1.EnIA;
            TrapEL2 = EL2Enabled() &amp;&amp; HCR_EL2.API == '0';
            TrapEL3 = HaveEL(EL3) &amp;&amp; SCR_EL3.API == '0';
        ...

    if Enable == '0' then return X;
    elsif TrapEL2 then TrapPACUse(EL2);
    elsif TrapEL3 then TrapPACUse(EL3);
    else return AddPAC(X, Y, APIAKey_EL1, FALSE);
```

下面是 AddPAC() 函数的伪代码：

```
/ AddPAC()
// ========
// Calculates the pointer authentication code for a 64-bit quantity and then
// inserts that into pointer authentication code field of that 64-bit quantity.

bits(64) AddPAC(bits(64) ptr, bits(64) modifier, bits(128) K, boolean data)

   bits(64) PAC;
   bits(64) result;
   bits(64) ext_ptr;
   bits(64) extfield;
   bit selbit;
   boolean tbi = CalculateTBI(ptr, data);
   integer top_bit = if tbi then 55 else 63;

   // If tagged pointers are in use for a regime with two TTBRs, use bit&lt;55&gt; of
   // the pointer to select between upper and lower ranges, and preserve this.
   // This handles the awkward case where there is apparently no correct
   // choice between the upper and lower address range - ie an addr of
   // 1xxxxxxx0... with TBI0=0 and TBI1=1 and 0xxxxxxx1 with TBI1=0 and
   // TBI0=1:
   if PtrHasUpperAndLowerAddRanges() then
       ...
   else selbit = if tbi then ptr&lt;55&gt; else ptr&lt;63&gt;;

   integer bottom_PAC_bit = CalculateBottomPACBit(selbit);

   // The pointer authentication code field takes all the available bits in
   // between
   extfield = Replicate(selbit, 64);

   // Compute the pointer authentication code for a ptr with good extension bits
   if tbi then
       ext_ptr = ptr&lt;63:56&gt;:extfield&lt;(56-bottom_PAC_bit)-1:0&gt;:ptr&lt;bottom_PAC_bit-1:0&gt;;
   else
       ext_ptr = extfield&lt;(64-bottom_PAC_bit)-1:0&gt;:ptr&lt;bottom_PAC_bit-1:0&gt;;

   PAC = ComputePAC(ext_ptr, modifier, K&lt;127:64&gt;, K&lt;63:0&gt;);

   // Check if the ptr has good extension bits and corrupt the pointer
   // authentication code if not;
   if !IsZero(ptr&lt;top_bit:bottom_PAC_bit&gt;) &amp;&amp; !IsOnes(ptr&lt;top_bit:bottom_PAC_bit&gt;) then
       PAC&lt;top_bit-1&gt; = NOT(PAC&lt;top_bit-1&gt;);

   // Preserve the determination between upper and lower address at bit&lt;55&gt;
   // and insert PAC
   if tbi then
       result = ptr&lt;63:56&gt;:selbit:PAC&lt;54:bottom_PAC_bit&gt;:ptr&lt;bottom_PAC_bit-1:0&gt;;
   else
       result = PAC&lt;63:56&gt;:selbit:PAC&lt;54:bottom_PAC_bit&gt;:ptr&lt;bottom_PAC_bit-1:0&gt;;
   return result;
```

由此可以看出，在执行 PACIA 时，无论运行在 EL0 和 EL1，在操作上并没有太大的区别。这意味着如果苹果对两个不同级别的指针使用了相同的 PAC 密钥，那么我们就可以在用户空间中执行 PACIA 函数来为内核空间中指针生成 PAC。

当然，苹果似乎不太可能在它们的系统中留下如此明显的漏洞。但即使如此，由于 EL0 与 EL1 的对称性，我们仍然可以在用户空间中生成内核空间指针的签名，只不过需要函数需要的密钥替换为内核空间的密钥即可。在苹果使用新算法替代QARMA的情况下，这个方法会非常有用，因为我们可以重用现有的签名算法，而不必对其进行反向工程。

### <a class="reference-link" name="%E4%BA%A4%E5%8F%89%E5%AF%86%E9%92%A5%E4%BC%AA%E9%80%A0%20PAC"></a>交叉密钥伪造 PAC

除了 EL0 与 EL1 之间算法的对称性，我们还可以利用它们密钥之间的对称性来生成伪造的 PAC : PACIA, PACIB, PACDA, and PACDB 这些密钥都可以看作为相同算法的不同参数。因此，如果我们可以用一个 PAC 密钥来替换另一个 PAC 密钥(A 与 B交换)，那么我们就可以将一个密钥签名的过程替换成了另一个密钥的签名过程。

虽然这种方案并不是特别强大，但是这个方法在某些情况下十分有用。比如，如果 PAC 算法是未知的，并且有一些机制能阻止我们将用户空间 PAC 密钥设置为与内核 PAC 密钥相等，我们将不能进行跨 EL 伪造，但是我们却可以利用这种方案。虽然我们还是需要依赖 PAC 签名工具，但是这种技术将使我们摆脱签名工具使用固定密钥进行签名的限制，可能会使我们的签名工具多样化。



## 小结

在本文中，我们介绍了指针验证的原理，分析了指针验证的一些缺陷，并在理论上提出了一些可能的方案来绕过以及伪造指针验证机制。在下一篇文章中，我们会根据真实的场景，利用几个已知的漏洞来绕过 A12 芯片中的指针验证，并伪造指针验证码。
