> 原文链接: https://www.anquanke.com//post/id/185335 


# 在Bleichenbacher '06 十年后 RSA签名伪造攻击仍然有效


                                阅读量   
                                **387660**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者blackhat，文章来源：i.blackhat.com
                                <br>原文地址：[http://i.blackhat.com/USA-19/Wednesday/us-19-Chau-A-Decade-After-Bleichenbacher-06-RSA-Signature-Forgery-Still-Works-wp.pdf](http://i.blackhat.com/USA-19/Wednesday/us-19-Chau-A-Decade-After-Bleichenbacher-06-RSA-Signature-Forgery-Still-Works-wp.pdf)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01899fed1fc1aad5eb.png)](https://p5.ssl.qhimg.com/t01899fed1fc1aad5eb.png)



RSA签名，尤其是其PKCS＃1 v1.5方案，被TLS中的X.509证书以及SSH，DNSSEC和IKE等许多重要的网络安全协议广泛使用。不幸的是，当输入异常时，许多PKCS＃1 v1.5 RSA签名验证的实现将错误地输出验证通过的结果。

本白皮书将探讨该主题，回顾历史缺陷和已知攻击，讨论我们如何将动态符号执行应用于各种RSA签名验证实现并发现其中多种实现仍然不能抵御多种类型的非正常验证通过攻击，导致在签名伪造攻击被披露的十年后新型签名伪造攻击仍然存在。

我还将剖析该缺陷的根本原因，并为需要实现类似协议的开发人员提供建议。本白皮书基于最近出版的学术研究论文“分析符号执行的语义正确性：PKCS＃1 v1.5签名验证的案例研究”[1]，由本人与MoosaYahyazadeh (University of Iowa)、 Omar Chowdhury (University of Iowa)、 Aniket Kate (Purdue University)、Ninghui Li (Purdue University)共同撰写。



## PKCS#1 v1.5

RSA签名被如此广泛使用的原因之一大概是由于其简单性。在“教科书”的描述中，给定消息m和公钥(n, e)，简单计算S e mod n ?= H(m)就能验证签名S。其中H是选择的散列函数。

然而，在实践中，遵循PKCS＃1 v1.5签名方案描述的要求，S e mod n的输出将包含H(m) 之外的信息。这是因为典型的散列输出（例如：160位的SHA-1）往往比n的长度（现在的常为2048位或4096位）短得多，并且为了使该方案是自包含的，签名者需要能够将选择的散列函数H传达给验证器。因此，PKCS＃1 v1.5签名方案描述了应该如何填充，以及用于指示散列函数H的元数据的格式。

简而言之，S e mod n应该如下所示：0x00 || 0x01 || PB || 0x00 || AS，其中PB必须填充至至少8字节长，以0xFF字节填充，AS是由DER编码的ASN.1结构，包含指示H和实际H(m)的元数据。



## 历史背景介绍

Daniel Bleichenbacher 在2006CRYPTO会议的尾部首次披露，PKCS＃1 v1.5签名验证实现中的缺陷可用于签名伪造攻击[2]。

他发现一些实现不会拒绝在AS之后额外的尾随字节，并且那些尾随字节可以任意取任何值。由于验证器的这种无根据的宽容，当e很小时（例如，e = 3），可以伪造签名。实现成功伪造的难度取决于n的大小和H的选择，这两者都会影响攻击者可以使用的尾随字节数。

实际上，面对这样的实现缺陷，使用更长的模数（被相信更难以分解）实际上会给攻击者带来更多的好处。Bleichenbacher 给出的原始签名伪造攻击示例基于3072位模数。2008年，K¨uhn 等人给出了在较短模数下对攻击的后续分析[3]，以及利用验证器中其他缺陷的攻击的变种。

例如，在其披露中，旧版本的GnuTLS 和OpenSSL 没有正确检查AS的算法参数部分，这允许AS中间的某些字节任意取任何值。如果未验证的字节数足够长，这也可以用于签名伪造。2014年的英特尔安全报告披露，Mozilla NSS存在类似的问题，该缺陷可被用于伪造证书[4]。2016年晚些时候，Filippo Valsorda披露，用python- rsa 实现PKCS＃1 v1.5签名验证没有强制要求所有填充字节需要为0xFF [5]，这又可以被利用于签名伪造和另一个对Bleichenbacher ‘06 家族的变种攻击。

### <a class="reference-link" name="%E6%96%B0%E5%8F%91%E7%8E%B0"></a>新发现

然而，Bleichenbacher ‘06带来的后续影响并未止于此。在我们的研究中，我们重新审视了PKCS＃1 v1.5实现的问题，并发现一些开源软件仍然存在签名验证的变种漏洞，这可能被利用于伪造攻击。下表显示了我们调查过的软件列表，并提供了我们的调查结果摘要。

|名称、版本|限制条件过分宽容|实际开发中e取值小
|------
|axTLS 2.1.3|YES|YES
|BearSSL – 0.4|No|–
|BoringSSL – 3112|No|–
|Dropbear SSH – 2017.75|No|–
|GnuTLS – 3.5.12|No|–
|LibreSSL – 2.5.4|No|–
|libtomcrypt – 1.16|YES|YES
|MatrixSSL – 3.9.1 (Certificate)|YES|No
|MatrixSSL – 3.9.1 (CRL)|YES|No
|mbedTLS – 2.4.2|YES|No
|OpenSSH – 7.7|No|–
|OpenSSL – 1.0.2l|No|–
|Openswan – 2.6.50 *|YES|YES
|PuTTY – 0.7|No|–
|strongSwan – 5.6.3 *|YES|YES
|wolfSSL – 3.11.0|No|–

*使用它们内部的PKCS＃1 v1.5实现

综上，我们发现有6个软件在PKCS＃1 v1.5签名验证方面限制过于宽松。在我们发现的所有缺陷中，有6个在新的CVE中被利用，3个用于axTLS ，2个用于strongSwan ，1个用于Openswan 。

### <a class="reference-link" name="CVE-2018-16150%EF%BC%9A"></a>CVE-2018-16150：

我们发现axTLS 也接受AS之后的尾随字节，就像最初的Bleichenbacher ‘06中披露的[2]一样，这意味着原始攻击也会起作用。事实上，我们分析发现axTLS 同样忽略了S e mod n的前10个字节，这将可以被串联使用，使得伪造更容易成功（减少暴力试验的次数）。

### <a class="reference-link" name="CVE-2018-16253%EF%BC%9A"></a>CVE-2018-16253：

如代码片段1所示，axTLS 忽略AS中用于指示哈希算法的元数据（包括算法对象标识符和参数），这甚至比先前发现的不检查算法参数的缺陷更疏于限制。因此，在先前的工作[3,4]中给出的伪造算法可以适用于此处。这个缺陷之所以存在，可能是因为axTLS中的签名验证码主要用于X.509证书的验证，而X.509证书有一个单独的字段用于指示签名算法和散列函数的选择，进而可能错误地认为检查AS中的元数据是多余的。

代码片段1：在axTLS 2.1.3中跳过了大部分ASN.1元数据

[![](https://p2.ssl.qhimg.com/t01d9195e86860d7aad.png)](https://p2.ssl.qhimg.com/t01d9195e86860d7aad.png)

### <a class="reference-link" name="CVE-2018-16149%EF%BC%9A"></a>CVE-2018-16149：

此外，我们发现axTLS 信任AS中长度变量的声明值而没有任何健全性检查，这意味着攻击者可以在那里放置荒谬的大值来欺骗axTLS 使用的解析器，执行非法内存访问。作为概念验证攻击，我们设法通过声明不正确的长H(m)来使签名验证器崩溃。这种攻击非常实用，因为axTLS 以自下而上的方式执行证书验证，这意味着即使现在在X.509生态系统中很少使用e=3，任何MITM都可能使用e= 3向链中注入无效的CA证书，同时阻止在验证器根据信任锚进行验证链（例如，一些根CA证书）。

### <a class="reference-link" name="CVE-2018-15836%EF%BC%9A"></a>CVE-2018-15836：

我们的分析表明，Openswan 有一个简单的缺陷，即不检查填充字节的实际值，这类似于先前在python- rsa中发现的问题。因此，攻击者可以利用Bleichenbacher 式的低指数伪造签名。

### <a class="reference-link" name="CVE-2018-16151%EF%BC%9A"></a>CVE-2018-16151：

我们发现strongSwan 不会拒绝在AS的算法参数部分中隐藏额外字节的签名，这也是之前在GnuTLS [6]和Mozilla Firefox [7]中发现的经典缺陷。

### <a class="reference-link" name="CVE-2018-16152%EF%BC%9A"></a>CVE-2018-16152：

此外，我们的分析发现strongSwan 使用最长前缀匹配的变体匹配AS中的算法对象标识符，该变量接受在有效对象标识符之后隐藏的尾随垃圾字节。换句话说，只要找到有效的前缀，它就不会完全消耗对象标识符字节，这意味着利用前期工作[3,4]中给出的不正确检查算法参数的缺陷的伪造算法也可以适用于这里。

其他：我们在几个软件中发现了其他特性，但并非所有不必要的宽容（限制条件）都能立即应用于实际攻击。例如，我们发现MatrixSSL 有两种不同的签名验证功能，一种用于验证X.509证书，一种用于验证证书撤销列表（CRL）。有趣的是，MatrixSSL 中CRL的签名验证不会拒绝无效的算法对象标识符。另外，当涉及DER长度检查时，MatrixSSL 有点宽容，这意味着几个可能的长度值都被认为是可接受的，同时，mbedTLS 和libtomcrypt也有这个变体问题。我们注意到libtomcrypt 还包含一些其他缺陷，它们使Bleichenbacher 式签名伪造成为可能，其他研究人员已独立发现并披露（CVE-2016-6129）



## 修复漏洞

多个解决上述问题的修复方案已经被发布了。自版本2.6.50.1 [8]以来，Openswan中的问题已得到修复。实际上，我们与开发人员共享的一种伪造签名已作为新的单元测试用例并入Openswan 源代码树[9]。strongSwan 修复了5.7.0 版以来的问题，并发布了旧版本的补丁[10]。为Openswan 和strongSwan 修复这些问题是有意义的，因为IPSec生态系统中仍有密钥生成程序迫使e = 3 [11]。自1.18.0版本以来，libtomcrypt 修复了可利用的缺陷[12]。我们为axTLS 开发了一个补丁，2.1.5版本后，该补丁被已经整合到源代码树中[13]。



## 分析技术

我们依靠动态符号执行（DSE）来帮助推动我们的分析，而不是手动代码审查。前提，弄清楚如何使用和验证输入字节是一个非常适合用DSE解决的问题，而在PKCS＃1 v1.5中，构成输入缓冲区的几个组件表现出良好的线性关系（例如，它们的位数之和必须与模数的位数一样长，并且在良性情况下，AS中节点的长度是从叶片到根部的总和），这可以用于在运行中自动生成有意义的模仿测试用例。此外，我们还为KLEE设计并实现了约束起源跟踪机制，使人们能够识别导致路径约束条款的代码行，从而使根本原因分析更加容易。有关我们的分析设置以及签名伪造算法的详细信息，我们为读者引用了参考原文[1]。



## 解析困难

总而言之，十分震惊，Bleichenbacher 风格的低指数签名伪造在原始披露发布十多年后仍然有效。一个主要的原因是，许多软件仍当基于解析的方法实现签名验证，即，某种ASN.1语法分析器仍被用于从H(m)抽取S e mod n。出于两个理由，这可能存在问题。首先，鉴于ASN.1具有高度灵活性但是有一些复杂的语法和编码规则，一些解析器，特别是如果它主要是为PKCS＃1 v1.5编写的，它的制作者往往尝试偷工减料使制作更简单、编写更容易。其次，一般的解析器的健壮性要求可能与安全关键的代码段的健壮性要求完全不同。人们可能会理所当然地期望一个强大的解析器不会在格式错误的输入上出现硬故障，并且仍能够挽救有用的信息并让计算继续进行（例如，参见[RFC 761]，Sect.2.10鲁棒性原则），但对于安全性至关重要的任务，例如：签名验证，这种缺乏限制的过于宽容的处理通常会带来可利用的漏洞，而且在许多情况下，硬故障实际上是正确的反应和处理方式。

一个更好的实现PKCS＃1 v1.5签名验证的方法是使用所谓的基于构造的方法，即在计算S e mod n之后，通过验证器构造“预期输出”，而不是从中提取H(m)。就像签名者所做的那样。然后比较整个字节块。鉴于签名验证现在不再依赖于解析，上述方法可以避免实现完整ASN.1解析器的艰难任务。这类似于解决几年前发现的问题的修复方案 [14 ]，也是我们如何修复axTLS中新发现的问题的办法[15]。

从长远来看，也许我们确实应该重新考虑在数字签名等安全关键对象中加入灵活但复杂的结构的设计，这很有价值。但同时，尽管像AS这样的ASN.1 DER结构具有高度可扩展性并且可以轻松容纳新的哈希算法，但事实上，新的标准化算法很少被引入，从这个角度考虑，为了获得偶尔一次的灵活性，复杂化一个每天多次调用的常见的关键的例程，似乎不值得。



## 参考

[1] S. Y. Chau, M. Yahyazadeh, O. Chowdhury, A. Kate, and N. Li, “Analyzing Semantic Correctness with Symbolic Execution: A Case Study on PKCS#1 v1.5 Signature Verification,” in The Network and Distributed System Security Symposium (NDSS) 2019.<br>
[2] H. Finney, Bleichenbacher’s RSA signature forgery based on implementation error, 2006 (accessed Jul 14, 2019), [https://www.ietf.org/mail-archive/web/openpgp/current/msg00999.html](https://www.ietf.org/mail-archive/web/openpgp/current/msg00999.html).<br>
[3] U. K¨uhn, A. Pyshkin, E. Tews, and R. Weinmann, “Variants of bleichenbacher’s low-exponent attack on PKCS#1 RSA signatures,” in Sicherheit 2008: Sicherheit, Schutz und Zuverl¨assigkeit. Konferenzband der 4. Jahrestagung des FachbereichsSicherheit der Gesellschaft f¨urInformatike.V. (GI), 2.-4. April 2008 imSaarbr¨ucker Schloss., 2008, pp. 97–109.<br>
[4] Intel Security: Advanced Threat Research, BERserk Vulnerability – Part 2: Certificate Forgery in Mozilla NSS, 2014 (accessed Jul 14, 2019), [https://bugzilla.mozilla.org/attachment.cgi?id=](https://bugzilla.mozilla.org/attachment.cgi?id=) 8499825.<br>
[5] F. Valsorda, Bleichenbacher’06 signature forgery in python-rsa, 2016 (accessed Jul 14, 2019), https: //blog.filippo.io/bleichenbacher-06-signature-forgery-in-python-rsa/.<br>
[6] S. Josefsson, [gnutls-dev] Original analysis of signature forgery problem, 2006 (accessed Jul 21, 2018), [https://lists.gnupg.org/pipermail/gnutls-dev/2006-September/001240.html](https://lists.gnupg.org/pipermail/gnutls-dev/2006-September/001240.html).<br>
[7] Bugzilla, RSA PKCS#1 signature verification forgery is possible due to too-permissive SignatureAlgorithm parameter parsing, 2014 (accessed Jul 18, 2018), [https://bugzilla.mozilla.org/](https://bugzilla.mozilla.org/) show bug.cgi?id=1064636.<br>
[8] [Openswan Users] Xelerance has released Openswan 2.6.50.1, 2018 (accessed Jul 16, 2019), https: //lists.openswan.org/pipermail/users/2018-August/023761.html.<br>
[9] wo#7449 . test case for Bleichenbacher-style signature forgery, 2018 (accessed Jul 16, 2019),[https://github.com/xelerance/Openswan/commit/937d24f88566702d72a549e9e8650320cb4f95cf](https://github.com/xelerance/Openswan/commit/937d24f88566702d72a549e9e8650320cb4f95cf).<br>
[10] strongSwan Vulnerability (CVE-2018-16151, CVE-2018-16152), 2018 (accessed Jul 16, 2019), [https://www.strongswan.org/blog/2018/09/24/strongswan-vulnerability-(cve-2018-16151,-cve2018-16152).html](https://www.strongswan.org/blog/2018/09/24/strongswan-vulnerability-(cve-2018-16151,-cve2018-16152).html).<br>
[11] Ubuntu Manpage: ipsecrsasigkey – generate RSA signature key, 2018 (accessed Jul 16, 2019), [http://manpages.ubuntu.com/manpages/bionic/man8/ipsec](http://manpages.ubuntu.com/manpages/bionic/man8/ipsec) rsasigkey.8.html.<br>
[12] libtomcrypt 1.18.0 Release Note, 2017 (accessed Jul 16, 2019), [https://www.libtom.net/news/](https://www.libtom.net/news/) LTC 1.18.0/.<br>
[13] [axtls-general] v2.1.5 of axTLS released, 2019 (accessed Jul 16, 2019), [https://sourceforge.net/p/](https://sourceforge.net/p/) axtls/mailman/message/36613862/.<br>
[14] PKCS#1 signature validation, 2014 (accessed Jul 16, 2019), [https://www.imperialviolet.org/2014/](https://www.imperialviolet.org/2014/) 09/26/pkcs1.html.<br>
[15] Apply CVE fixes for X509 parsing, 2018 (accessed Jul 16, 2019), [https://github.com/igrr/axtls8266/commit/5efe2947ab45e81d84b5f707c51d1c64be52f36c](https://github.com/igrr/axtls8266/commit/5efe2947ab45e81d84b5f707c51d1c64be52f36c).
