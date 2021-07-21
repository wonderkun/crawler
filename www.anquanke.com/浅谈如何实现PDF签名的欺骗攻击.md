> 原文链接: https://www.anquanke.com//post/id/173669 


# 浅谈如何实现PDF签名的欺骗攻击


                                阅读量   
                                **267865**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者web-in-security，文章来源：web-in-security.blogspot.com
                                <br>原文地址：[https://web-in-security.blogspot.com/2019/02/how-to-spoof-pdf-signatures.html](https://web-in-security.blogspot.com/2019/02/how-to-spoof-pdf-signatures.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01e6f9634a42b1758a.jpg)](https://p5.ssl.qhimg.com/t01e6f9634a42b1758a.jpg)



## 前言

本文对PDF文件及其数字签名机制进行了分析，并提出了三种针对PDF签名的攻击方式。



一年前，我们收到一份PDF合同，包含有数字签名。我们查看文档内容的时候，忽略了其“证书不可信”的警告。不禁令人心生疑惑：

“PDF签名机制如何工作？”

我们对于类似xml和json信息格式的安全性非常熟悉了，但是似乎很少有人了解，PDF的安全机制是如何工作的。因此我们决定围绕此问题展开研究。

时至今日，我们很高兴的公布我们的研究成果。本篇文章中，我们简要概述了PDF签名的工作机理，重要的是我们揭示了三个新的攻击方式，用于实现对PDF文档数字签名的欺骗。我们对22款PDF阅读器进行测试评估，结果发现有21个是存在安全性风险的。我们还对8个在线验证服务进行测试，结果发现有6个是易受攻击的。

通过与BSI-CERT合作，我们联系了所有的开发商，向他们提供PoC，并帮助修复漏洞。对每一种攻击方式均取得了CVE：[CVE-2018-16042](https://nvd.nist.gov/vuln/detail/CVE-2018-16042), [CVE-2018-18688](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-18688), [CVE-2018-18689](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-18689)。

完整的结果可参考**Karsten Meyer zu Selhausen**的[论文](https://www.nds.ruhr-uni-bochum.de/media/ei/arbeiten/2019/02/12/DIGITALVERSION_KMeyerZuSelhausen_SecurityOfPDFSignatures_2018-11-25.pdf)，我们的[研究报告](https://www.nds.ruhr-uni-bochum.de/research/publications/vulnerability-report-attacks-bypassing-signature-v/)或者我们的[网站](https://www.pdf-insecurity.org/index.html)



## 究竟何人在用PDF签名？

也许你会心生疑问：既然PDF签名如此重要，那么究竟谁在使用？

事实上，也许你自己早就使用过PDF签名。

你是否曾经打开过诸如Amazon、Sixt 或是 Decathlon 公司开具的发票？

这些PDF文件都是经过数字签名保护的，以防止被篡改。

实际上，PDF签名在我们身边具有广泛的应用。2000年，Bill Clinton总统颁布了一项联邦法律，推广在各州间和国际间数字签名的使用，以确保合同的有效性和法律效力。[他通过数字签名签署了此项法案](https://www.govinfo.gov/content/pkg/PLAW-106publ229/pdf/PLAW-106publ229.pdf)。

自2014年起，[在欧盟成员国内提供公共数字服务的组织必须支持数字签名文档](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32014R0910)，这些文档甚至可以作为法律诉讼的证据。

在奥地利，每个政府机构都会对所有官方文档进行数字签名。此外，任何新颁布的法律只有在其文档经过数字签名后，才算在法律上生效。

像巴西、加拿大、俄罗斯和日本等国也都广泛使用数字签名文档。

据Adobe官方声称，[公司仅在2017年就处理了80亿个数字签名](https://www.adobe.com/about-adobe/fast-facts.html)。



## PDF文件及其签名速览

### <a class="reference-link" name="PDF%E6%96%87%E4%BB%B6%E6%A0%BC%E5%BC%8F"></a>PDF文件格式

为更好的理解数字签名欺骗，我们首先不得不解释一些基本概念。首先对PDF文件进行概述。

PDF文件其本质是ASCII文件。利用普通的文本编辑器打开，即可观察到源代码。

[![](https://p0.ssl.qhimg.com/t01c4815a6abfe6a382.png)](https://p0.ssl.qhimg.com/t01c4815a6abfe6a382.png)
<li>
**PDF header**：**header**是PDF文件的第一行，定义了所需解释器的版本。示例中的版本是PDF1.7.</li>
<li>
**PDF body**：**body**定义了PDF文件的内容，包括文件自身的文本块、字体、图片和其他数据。**body**的主体部分是对象。每个对象以一个对象编号开头，后面跟一个代号（generation number）。如果对相应的对象进行了更改，则应该增加代号。</li>
在所给示例中，**Body**包含4个对象：**Catalog, Pages, Page, stream**。Catalog对象是PDF文件的根对象，定义了文档结构，还可以声明访问权限。Catalog对象应用了Pages对象，后者定义了页数以及对每个Pages对象的引用信息。Pages对象包含有如何构建一个单独页面的信息。在给定的示例中，它包含一个单独的字符串对象“hello world!”
<li>
**Xref table**：包含文件内所有PDF对象的位置信息（字节偏移量）</li>
<li>
**Trailer**：当一个PDF文件读入内存，将从尾到头进行处理。这就意味着，Trailer是PDF文档中首先处理的内容，它包含对Catalog和Xref table的引用。</li>
### <a class="reference-link" name="PDF%E7%AD%BE%E5%90%8D%E5%A6%82%E4%BD%95%E5%B7%A5%E4%BD%9C"></a>PDF签名如何工作

PDF签名依赖于PDF一项特定功能，称之为增量存储（也称增量更新），其允许修改PDF文件而不必改变之前的内容。

[![](https://p3.ssl.qhimg.com/t01a5525c47909777da.png)](https://p3.ssl.qhimg.com/t01a5525c47909777da.png)

从图中观察可知，原始的文档和这里的文档是一样的。通过对文档进行签名，利用增量存储来添加以下内容：一个新的Catalog，一个签名对象，一个新的Xref table引用了新对象，和一个新的Trailer。其中，新Catalog通过添加对Signature对象的引用，来扩展旧Catalog。Signature对象（5 0 obj）包含有哈希和签名文档的密码算法信息。它还有一个Contents参数，其包含一个16进制编码的PKCS7 blob，该blob存有证书信息，以及利用证书中公钥对应私钥创建签名值。ByteRange 参数指定了PDF文件的哪些字节用作签名计算的哈希输入，并定义了2个整数元组：
- a,b： 从字节偏移量a开始，后续的b个字节作为哈希运算的第一个输入。通常，a取值为0表示起始位置为文件头部，偏移量b则取值为**PKCS#7 blob**的起始位置。
- c,d：通常，偏移量c为**PKCS#7 blob**的结束位置，而c d则指向PDF文件的最后一个字节的范围，用作哈希运算的第二个输入。
根据相应的规范，建议对文件进行签名时，并不计算**PKCS#7 blob**部分（位于b和c之间）。



## 攻击方式

根据研究，我们发现了针对PDF签名的三种新型攻击方式：
1. 通用签名伪造（Universal Signature Forgery ，USF）
1. 增量存储攻击（Incremental Saving Attack ，ISA）
1. 签名包装攻击（Signature Wrapping Attack ，SWA）
在本篇文章中，我们仅对各攻击进行概述，并不阐述详细的技术细节。如果读者对此感兴趣，可参考我们总结的资源。

### <a class="reference-link" name="%E9%80%9A%E7%94%A8%E7%AD%BE%E5%90%8D%E4%BC%AA%E9%80%A0%20USF"></a>通用签名伪造 USF

[![](https://p0.ssl.qhimg.com/t016ff2ac2326955fea.png)](https://p0.ssl.qhimg.com/t016ff2ac2326955fea.png)

通用签名伪造的主体思想就是控制签名中的原始数据信息，通过这种方式，使目标阅读器程序在打开PDF文件寻找签名时，无法找到其验证所需的所有数据信息。

这种操作并不会导致将缺失的信息认定为错误，相反其会显示签名的验证是有效的。例如，攻击者控制Signature对象中的**Contents**或**ByteRange**的数值，对其控制操作的具体内容：我们要么直接移除签名值，要么删除签名内容的起始位置信息。这种攻击似乎微不足道，但即使是诸如Adobe Reader DC这样优秀的开发程序，能够阻止其他多种功能类型的攻击，却也容易遭受USF攻击。

### <a class="reference-link" name="%E5%A2%9E%E9%87%8F%E5%AD%98%E5%82%A8%E6%94%BB%E5%87%BB%20ISA"></a>增量存储攻击 ISA

增量存储攻击滥用了PDF规范中的合法功能，该功能允许PDF文件通过追加内容来实现文件更新。这项功能很有用处，例如存储PDF注释或者在编辑文件时添加新的页面。

[![](https://p3.ssl.qhimg.com/t010682a34a76411fbf.png)](https://p3.ssl.qhimg.com/t010682a34a76411fbf.png)

**ISA**的主要思想是利用相同的技术来将签名PDF文件中的元素更改为攻击者所需内容，例如文本、或是整个页面。

换而言之，一个攻击者可以通过**Body Updates**重新定义文档的结构和内容。PDF文件内的数字签名可以精确保护**ByteRange**定义的文件内容。由于增量存储会将**Body Updates**追加保存到文件的结尾，其不属于**ByteRange**定义的内容，因此也就不受数据签名的完整性保护。总而言之，签名仍然有效，而**Body Updates**也更改了文件的内容。

PDF规范并没有禁止此操作，但签名验证应指明已签名的文档已经被篡改。

### <a class="reference-link" name="%E7%AD%BE%E5%90%8D%E5%8C%85%E8%A3%85%E6%94%BB%E5%87%BB%20SWA"></a>签名包装攻击 SWA

独立于PDF，签名包装攻击的主体思想是迫使验证逻辑处理与应用逻辑不同的数据。

[![](https://p3.ssl.qhimg.com/t0164242484af43f14f.png)](https://p3.ssl.qhimg.com/t0164242484af43f14f.png)

在PDF文件中，SWA将原始的签名内容重定位到文档内的不同位置，并在已分配的位置处插入新的内容，以此来定位签名验证逻辑。攻击的起始点是控制ByteRange值，使其允许签名内容转移到文件内的不同位置。

在技术层面上，攻击者使用有效的签名文档（如图所示），并按以下方式执行操作：

[![](https://p3.ssl.qhimg.com/t0145dd8e838f83f169.png)](https://p3.ssl.qhimg.com/t0145dd8e838f83f169.png)
- step 1 （可选）：攻击者删除Contents参数内的零字节填充，以增加注入操作对象的可用空间。
- step 2：攻击者通过操控c的值来定义新的`ByteRange [a b c* d]`，使其指向文件中处于不同位置的第二个签名部分。
- step 3：攻击者创建指向新对象的新的**Xref table**，必须保持新插入的**Xref table**的字节偏移与前一个**Xref table**的相同。该位置不可更改，因为它是由已签名的**Trailer**所引用的。正因如此，攻击者可以在新的**Xref table**前增加一个填充块（例如，可用空格），以此来填满未用空间。
- step 4：攻击者注入不受签名保护的恶意对象。对这些对象而言，有多种不同的注入点。它们可以放置于恶意**Xref table**之前或之后。如果step 1没有执行，则只能将其放置于恶意**Xref table**之后。
- step 5（可选）：一些PDF阅读器需要在操控的**Xref table**之后加入**Trailer**，否则将无法打开PDF文件或者检测到修改并提示错误信息。拷贝最后部分的**Trailer**，从而绕过其限制。
- step 6：攻击者删除在字节偏移c*处、由c和d定义的已签名内容。当然，也可以选择删除封装在流对象中的内容。值得注意的是，被操控的PDF文件并没有以%%EOF结尾。一些验证程序之所以会提示已签名文件被修改，是由于签名后面的%%EOF。为了绕过此需求，PDF文件无法正常关闭。但是，它仍然可以由其他阅读器处理。


## 测试评估

在我们的测试评估阶段，我们搜索了验证PDF文件签名的桌面应用程序。我们针对这3种攻击方式，验证了其签名验证流程的安全性。有22个应用程序满足要求。我们在所有支持的平台上（Windows, MacOS, and Linux），对这些应用程序的最新版本进行了评估，结果如下所示：

[![](https://p4.ssl.qhimg.com/t01f4ef449030988544.png)](https://p4.ssl.qhimg.com/t01f4ef449030988544.png)
