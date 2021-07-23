> 原文链接: https://www.anquanke.com//post/id/240026 


# 漏洞自动化利用（AEG）研究进展


                                阅读量   
                                **179157**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01ee28aa134236d3e3.jpg)](https://p1.ssl.qhimg.com/t01ee28aa134236d3e3.jpg)



## 前言

自从DARPA在2016搞了一个CGC比赛之后，关于漏洞自动利用工作的研究也在随后几年多了起来。国内近几年也有类似的RHG比赛出现。此外，随着软件趋于复杂，模糊测试技术的成熟，漏洞数量也越来越多。要修补所有的漏洞不太现实，而人工去判断漏洞的危害性也是耗时耗力的过程。因此，这也就带动了漏洞自动利用生成（Automatic Exploit Generation）的发展。本文将基于近几年安全顶会上的研究，首先介绍漏洞自动化利用的研究进展，并给出一个漏洞自动利用的基本框架，最后讨论漏洞自动利用的未来研究方向。



## 1. 背景

近几年来，漏洞的CVE数量越来越多。一方面是因为模糊测试在漏洞挖掘领域取得了比较好的效果，另一方面是软件的越来越复杂，不可避免导致了很多安全漏洞。面对如此多数量的漏洞，对于一个安全团队是很难能够及时修复的。相关研究表明，漏洞修复的周期长达几周或几个月。因此，需要对漏洞修复的优先级进行排序。常用的策略是基于漏洞的可利用性来确定漏洞的优先级。然而，手工确定漏洞的可利用性也是耗时耗力的事情。这也就是漏洞自动化利用工具的意义所在，自动化地评估漏洞的可利用性，进而确定漏洞修复的优先级。

除了确定漏洞修复优先级以外，漏洞自动化利用也能对现有的防御机制进行评估，产生新的防御思路。此外，这类工具也能对CTF比赛或者渗透测试过程提供很大帮助。企业也能使用这类工具来对其系统安全风险预警。

总的来说，研究意义主要分为以下三点。

a. 确定漏洞可利用性<br>
b. 自动化地去评估防御机制，促进防御的研究发展。<br>
c. 辅助渗透测试，比如CTF等等。



## 2. 研究时间线

最早关于漏洞利用自动生成的研究是2008年的APEG[1]。这篇工作是基于一个打过补丁的程序，来自动生成没打过补丁的程序漏洞利用。应用到实际会有很多受限之处，但是开创了漏洞利用自动生成这个领域。随后，2009年，Heelan[2]的硕士论文是第一个提出给定一个程序的崩溃输入，然后自动生成这个漏洞的利用。后续的工作基本上也是按这个套路不断延申开来。2011年后，先前研究APEG的David团队先后发表了AEG[3]，Mayhem[4]等工作。早期的漏洞自动化利用工作基本都是由这个团队做的。到2016年，DARPA开了一个CGC的比赛（自动攻防），Mayhem取得了第一名。之后几年内，相关工作如春笋一般涌出。2016年算是个奇妙的时间点，2016之前的工作大都是围绕栈溢出，格式化字符串漏洞来做。2016年之后大多工作都开始尝试去实现堆漏洞（堆溢出、UAF）的自动化利用。

[![](https://p1.ssl.qhimg.com/t01568b2f86e0234b12.png)](https://p1.ssl.qhimg.com/t01568b2f86e0234b12.png)

总结一下，漏洞自动化利用的发展的研究趋势，目前应该还有一些重要的工作需要去做。近几年的工作大都是将符号执行和模糊测试相结合来实现的，仿佛成为了一种范式。自然辩证法里有提到过科学是在范式下解难题。现在看来确实蛮符合科学发展的规律。



## 3. 基本方法

这里简单介绍几篇论文里是如何实现AEG。并且大家可能会发现，思路都差不多，但研究的侧重点都不尽相同。

### <a class="reference-link" name="3.1%20%E9%92%88%E5%AF%B9%E6%A0%88%E6%BA%A2%E5%87%BA%E7%9A%84AEG"></a>3.1 针对栈溢出的AEG

早期的工作主要是针对栈溢出漏洞进行自动化利用，这些研究有Heelan的硕士论文[2], AEG[3]，Mayhem[4]，CRAX[5]等等

Heelan的工作需要给定一个已知漏洞的崩溃输入和跳转的寄存器，基于动态符号执行来自动化地劫持程序控制流。<br>
具体来说，他使用二进制插桩来做污点传播并收集运行时信息，并通过检查EIP寄存器是否被污点影响来生成exp，同时也考虑了间接影响EIP寄存器的指针损坏的情况。

AEG这篇论文写得很清晰。文章的总体框架如下图所示。首先用gcc和llvm对源码进行预处理，生成能用GCC运行的二进制Bgcc和LLVM分析的字节码Bllvm。基于字节码，AEG用条件符号执行去找漏洞函数，被溢出覆盖的对象，触发bug的路径。同时用动态二进制分析去Bgcc里提取运行时信息，最后生成payload。生成payload后再进行验证，最后输出exploit。（下图来自于论文。）

[![](https://p1.ssl.qhimg.com/t0199c81b8a545384ce.png)](https://p1.ssl.qhimg.com/t0199c81b8a545384ce.png)

mayhem这篇文章就是上面AEG在二进制上的逻辑扩展。核心技术是混合符号执行和基于索引的内存模型。用混合符号执行主要是在运行速度和内存要求之间找平衡点。mayhem引入了具体执行来缓解符号执行带来的路径爆炸问题。具体来说，具体执行插桩，做动态污点分析，然后把污点指令流传给SES。SES编译这些指令为中间语言，并且符号化地去执行。简单来说就是具体执行缩小了符号执行需要执行的范围。而基于索引的内存模型主要是去解决产生exploit由于具体的约束条件而不可行，因此引入整个模型来避免索引的约束。（下图来自于论文。）

[![](https://p0.ssl.qhimg.com/t017b0a944dad97abf2.png)](https://p0.ssl.qhimg.com/t017b0a944dad97abf2.png)

CRAX主要是针对AEG中的一个缺陷做的改进。AEG收集运行时信息，并且只在漏洞触发的时候计算exp。产生的exp可能会由于漏洞点和触发exp点的传播距离而失效。比如下面的代码。漏洞点在第四行的strcpy，触发漏洞是在第六行函数返回的时候，而这个时候第五行修改了之前计算的exp，就会导致最后的exp失效。（下图来自于论文。）

[![](https://p4.ssl.qhimg.com/t01589702622804eb46.png)](https://p4.ssl.qhimg.com/t01589702622804eb46.png)

CRAX的方法和angr文档里的simple AEG的思路很像。第一步是去找符号化的EIP，也就是看输入能否控制程序指针PC。第二步是找到符号化的内存，看看能否注入shellcode。当确定了shellcode的位置后，CRAX会在shellcode前面放很多的滑板指令NOP来扩充shellcode的入口。最后，所有的约束，包括shellcode，NOP sled，EIP寄存器的约束都会送到solver去求解，得到最终的exp。如果得不到解，就会去改变shellcode的位置，直到求出解或者没有可用的符号buffer了。（下图来自于论文。）

[![](https://p4.ssl.qhimg.com/t0185da4ee5ad336355.png)](https://p4.ssl.qhimg.com/t0185da4ee5ad336355.png)

### <a class="reference-link" name="3.2%20%E9%92%88%E5%AF%B9%E5%A0%86%E6%BA%A2%E5%87%BA%E7%9A%84AEG"></a>3.2 针对堆溢出的AEG

针对堆漏洞的自动化利用工作到2016年以后才陆续开始出现。这也是近几年来的研究热点。我认为有几个原因：

a. 相比栈漏洞，堆漏洞的利用更为复杂，更需要自动化利用工具来对其进行评估<br>
b. 先前的工作主要是针对栈上的漏洞，做堆漏洞的工作在2016年前没有<br>
c. 堆漏洞在这几年增加的要比栈漏洞快

由于堆利用复杂性，有些工作聚焦于堆布局的自动化。比如Usenix18 的SHRIKE[6]和CCS 19 的slake[7]，分别是针对解释器和内核的堆漏洞的自动化操纵布局。

SHRIKE是第一个堆布局自动化操纵的研究，其方法是基于伪随机黑盒搜索。SLAKE使用动态和静态分析来分析内核对象和相应的系统调用。然后，对常用的利用方法进行建模，最后实现了一种slab布局调整的方法。

下面介绍的针对各类应用场景堆漏洞的AEG工作，比如浏览器、内核、解释器等。

**REVERY**[8]

现有的AEG方法通常是探索crashing path来找到可利用的状态，比如由PoC触发的漏洞的路径和生成的利用通常是在一条路径上。然而，1.可利用的状态不一定总在crashing path上。2.并且，现有的方法严重依赖符号执行，并且在路径扩展和利用生成的扩展性不好。

为了解决这两个问题，revery使用了三种技术：

0x1. layout-contributor digraph 来描述漏洞的内存布局和指令<br>
0x2. layout-oriented fuzzing去探索和crashing paths有相同内存布局的路径<br>
0x3. control-flow stitching 来连接crashing paths和diverging path，最后生成利用。

（下图来自于论文。）

[![](https://p4.ssl.qhimg.com/t0155f8a4f6a73d666d.png)](https://p4.ssl.qhimg.com/t0155f8a4f6a73d666d.png)

**HEAPG**[9]

由于现有的方法都是通过破坏一个敏感指针然后实现一个内存读写或者间接调用，也就是说敏感指针是劫持控制流的关键。在这个例子里，一旦堆布局准备好，攻击者只要一次就可以构造利用原语。然后实际很多漏洞需要多个步骤才能实现利用。为了实现这点，HEAPG利用专家知识来指导利用生成。具体来说，HEAPG，以crashing input,二进制程序和专家知识作为输入，然后通过利用堆分配器内部的特性，能够对很难利用的漏洞生成利用。（下图来自于论文。）

[![](https://p3.ssl.qhimg.com/t013543f5923d897172.png)](https://p3.ssl.qhimg.com/t013543f5923d897172.png)

**PrimGen**[10]

针对浏览器这类有广大用户人群，且极为复杂的软件，其漏洞利用过程通常是个耗时耗力，多步骤的过程。为了减轻安全人员的工作量，PrimGen自动化了部分浏览器漏洞的利用过程。对于给定的一个漏洞，PrimGen能够自动构造数据对象喂给浏览器导致执行恶意行为。

PrimGen主要分为两部分，第一部分预处理，基于二进制程序生成CFG和SSA，并且收集一些数据，比如函数的entry，寄存器的定义/使用，内存读写和控制流信息。更进一步，PrimGen利用动态分析来获取控制流和内存信息（利用debugger在控制点下断点来执行crashing input。）然后就可以提取动态踪迹和内存信息。

第二部分用datalog-based方法去找控制点后的可控数据。在确定了控制点的位置后，开启分析去找到可到达的sink。基于这些信息，构造了一个图来描述从一个基本块到另外一个基本块的控制流。有了这些图，再利用符号执行去执行到skin的路径，并过滤掉不可解的路径。在这个步骤中，会收集所有与控制数据相关的约束，并且用于构建内存映射表。基于映射表可以指导如何构造对象。基于前面动态分析获得的memory dump，PrimGen可以验证每条与内存映射绑定的路径是否满足利用条件。最后，给定一个VUT的堆喷射模板，PrimGen的模型可以生成喂给浏览器的脚本。（下图来自于论文。）

[![](https://p4.ssl.qhimg.com/t01700ea9ffdd1e4fb4.png)](https://p4.ssl.qhimg.com/t01700ea9ffdd1e4fb4.png)

**Gollum**[11]

gollum是第一个针对解释器堆溢出漏洞的AEG研究。文章提到大多数的AEG系统针对的是命令行的程序或者类似文件解析器的系统。而解释器和这些程序不一样，并且打破了现有AEG系统的假设。一个假设是利用符号执行可以推断输入文件和目标行为的关系。而解释器的状态空间很大，并且输入程序的值和程序状态有很多非直接的关系。解释器有很多漏洞，但这里针对堆溢出漏洞有2个原因，一是堆漏洞比较常见，二是现有AEG系统做的还不够完善。

文章关于堆布局的自动操作是基于作者之前工作SHRIKE的基础上。另外文章的亮点还在于用了遗传算法来代替之前的伪随机搜索算法。感兴趣的可以去看论文。（下图来自于论文。）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016333ef271d400ef1.png)

**FUZE**[12]

FUZE针对的是内核的UAF漏洞。这是篇将符号执行与模糊测试结合的AEG文章。具体来说，从漏洞触发点开始用模糊测试探索路径。然后在指针解引用的地方用符号执行再去探索路径。（下图来自于论文。）

[![](https://p4.ssl.qhimg.com/t016e61f74b05b56ca1.png)](https://p4.ssl.qhimg.com/t016e61f74b05b56ca1.png)

**KOOBE**[13]

KOOBE针对是内核的Out-of-Bound(OOB)漏洞。针对现有的方法无法完全挖掘漏洞的能力，KOOBE定义了OOB漏洞的能力为三点：能写多远、能写多少、能写什么。并利用OOB漏洞的能力来指导模糊测试。（下图来自于论文。）

[![](https://p1.ssl.qhimg.com/t01c63b8f7c9d13b70e.png)](https://p1.ssl.qhimg.com/t01c63b8f7c9d13b70e.png)

### <a class="reference-link" name="3.3%20%E9%92%88%E5%AF%B9%E5%85%B6%E4%BB%96%E6%BC%8F%E6%B4%9E%E7%9A%84AEG"></a>3.3 针对其他漏洞的AEG

这篇文章[14]提出了一个完整的自动化目标栈喷射方法来自动化利用内核的未初始化漏洞。目标栈喷射技术包含两点：

a. 确定的栈喷射技术，结合定制的符号执行和模糊测试来识别内核输入，这个内核输入指的是攻击者利用用户程序在确定地执行内核代码路径，从而在内核栈上留下攻击者控制的数据。<br>
b. 内存喷射技术，使用内存占用和污染来可靠地控制内核栈上的一大块空间。

所以，这两个技术概括来说，一个是精准定位，一个是大面积覆盖。并且作者利用这个技术和未初始化漏洞可以实现提权。此外，作者还提供了一种基于编译器的防御机制，来初始化可能不安全的指针类型，并且没有太多的额外性能。文章的结果显示，未初始化使用是一个很严重的攻击，所以未来的防御系统需要考虑这种漏洞，并且系统软件不应该使用未初始化内存来作为随机源。（下图来自于论文。）

[![](https://p4.ssl.qhimg.com/t01d855f583c51d0565.png)](https://p4.ssl.qhimg.com/t01d855f583c51d0565.png)



## 4. 评估方法

目前的评估数据集主要有三类：

​ a. CVE漏洞

​ b. syzbot平台上的漏洞（谷歌用fuzzer找到的内核漏洞）

​ c. CTF比赛程序

CVE漏洞的优点在于其是真实存在的漏洞。用CVE来做测试集，工具的实际意义比较大。

大部分的工作用的都是实际的CVE来做评估测试。一些内核漏洞的工作会用到syzbot平台。因为syzbot平台上的漏洞还没经过评估成为CVE，有比较大的评估价值。

Revery[8]和KEPLER[15]用到了一些CTF比赛的数据集。这类数据集的优点前期测试工具比较方便，网上也有相应的exploit。但存在问题是这类程序的规模一般不大，可能无法评估工具能否实用。

[![](https://p3.ssl.qhimg.com/t013dacba2351f80675.png)](https://p3.ssl.qhimg.com/t013dacba2351f80675.png)



## 5. 未来可能研究方向

如何对漏洞进行建模是这个领域的一个难点。建模时需要考虑漏洞的类型，漏洞程序的类型（浏览器，内核），漏洞的能力（能写多远，能写多少字节，能写什么值）。因为现有的漏洞自动化利用的实现主要是基于符号执行和模糊测试，而这两种技术都存在搜索空间很大的弊病。因此，充分利用漏洞的信息能够在一定程度上降低搜索空间。比如KOOBE这篇文章就是将漏洞能力融入到模糊测试中去，进而提高了模糊测试的效率。

未来的研究可能会针对更多更难利用的漏洞去实现AEG，比如竞争？或者针对更广的应用场景，比如嵌入式设备、固件？此外漏洞自动利用还有个难以解决的问题，就是如何确定漏洞的可利用性的边界。现有的工作对这个问题的回答还不是很好。因为目前的工具不能生成一个漏洞的利用，并不代表这个漏洞是否不可利用，有可能是工具自身的问题。当然这也是个很困难的问题。



## 6. 开源工具

**劫持控制流**

PrimGen：浏览器堆漏洞自动化利用(目前只有结果，作者说code will follow)

> [https://github.com/RUB-SysSec/PrimGen](https://github.com/RUB-SysSec/PrimGen)

FUZE：内核UAF漏洞自动化利用

> [https://github.com/ww9210/Linux_kernel_exploits](https://github.com/ww9210/Linux_kernel_exploits)

Gollum：解释器堆溢出漏洞自动化利用（有链接但暂未开源）

> [https://github.com/SeanHeelan/ShapeShifter](https://github.com/SeanHeelan/ShapeShifter)

KOOBE：内核越界写（OOB）漏洞自动化利用

> [https://github.com/seclab-ucr/KOOBE](https://github.com/seclab-ucr/KOOBE)

rex：angr参加CGC比赛的工具

> [https://github.com/angr/rex](https://github.com/angr/rex)

Zeratool：栈溢出自动化利用工具

> [https://github.com/ChrisTheCoolHut/Zeratool](https://github.com/ChrisTheCoolHut/Zeratool)

**堆布局操作**

SHRIKE：堆溢出漏洞布局操作自动化

> [https://github.com/SeanHeelan/HeapLayout](https://github.com/SeanHeelan/HeapLayout)

SLAKE：四种漏洞的堆布局操作自动化(暂时不完善)

> [https://github.com/chenyueqi/SLAKE](https://github.com/chenyueqi/SLAKE)

**绕过防御机制**

BOPC：绕过防御机制（数据流攻击自动化）

> [https://github.com/HexHive/BOPC](https://github.com/HexHive/BOPC)

KEPLER：绕过防御机制（内核ROP）

> [https://github.com/ww9210/kepler-cfhp](https://github.com/ww9210/kepler-cfhp)

**一些相关资料，及几篇最近的综述**

github上关于AEG论文的整理：[https://github.com/SCUBSRGroup/Automatic-Exploit-Generation](https://github.com/SCUBSRGroup/Automatic-Exploit-Generation)

赵尚儒,李学俊,方越,余媛萍,黄伟豪,陈恺,苏璞睿,张玉清.安全漏洞自动利用综述[J].计算机研究与发展,2019,56(10):2097-2111.

苏璞睿,黄桦烽,余媛萍,张涛.软件漏洞自动利用研究综述[J].广州大学学报(自然科学版),2019,18(03):52-58.



## 参考资料

[1] Brumley D, Poosankam P, Song D, et al. Automatic patch-based exploit generation is possible: Techniques and implications[C]//2008 IEEE Symposium on Security and Privacy (sp 2008). IEEE, 2008: 143-157.

[2] Heelan S. Automatic generation of control flow hijacking exploits for software vulnerabilities[D]. University of Oxford, 2009.

[3] Avgerinos T, Cha S K, Rebert A, et al. Automatic exploit generation[C]//NDSS. 2011.

[4] Cha S K, Avgerinos T, Rebert A, et al. Unleashing mayhem on binary code[C]//2012 IEEE Symposium on Security and Privacy. IEEE, 2012: 380-394.

[5] Huang S K, Huang M H, Huang P Y, et al. Crax: Software crash analysis for automatic exploit generation by modeling attacks as symbolic continuations[C]//2012 IEEE Sixth International Conference on Software Security and Reliability. IEEE, 2012: 78-87.

[6] Heelan S, Melham T, Kroening D. Automatic heap layout manipulation for exploitation[C]//27th `{`USENIX`}` Security Symposium (`{`USENIX`}` Security 18). 2018: 763-779.

[7] Chen Y, Xing X. Slake: facilitating slab manipulation for exploiting vulnerabilities in the Linux kernel[C]//Proceedings of the 2019 ACM SIGSAC Conference on Computer and Communications Security. 2019: 1707-1722.

[8] Wang Y, Zhang C, Xiang X, et al. Revery: From proof-of-concept to exploitable[C]//Proceedings of the 2018 ACM SIGSAC Conference on Computer and Communications Security. 2018: 1914-1927.

[9] Zhao Z, Wang Y, Gong X. HAEPG: An Automatic Multi-hop Exploitation Generation Framework[C]//International Conference on Detection of Intrusions and Malware, and Vulnerability Assessment. Springer, Cham, 2020: 89-109.

[10] Garmany B, Stoffel M, Gawlik R, et al. Towards automated generation of exploitation primitives for web browsers[C]//Proceedings of the 34th Annual Computer Security Applications Conference. 2018: 300-312.

[11] Heelan S, Melham T, Kroening D. Gollum: Modular and greybox exploit generation for heap overflows in interpreters[C]//Proceedings of the 2019 ACM SIGSAC Conference on Computer and Communications Security. 2019: 1689-1706.

[12] Wu W, Chen Y, Xu J, et al. `{`FUZE`}`: Towards facilitating exploit generation for kernel use-after-free vulnerabilities[C]//27th `{`USENIX`}` Security Symposium (`{`USENIX`}` Security 18). 2018: 781-797.

[13] Chen W, Zou X, Li G, et al. `{`KOOBE`}`: Towards Facilitating Exploit Generation of Kernel Out-Of-Bounds Write Vulnerabilities[C]//29th `{`USENIX`}` Security Symposium (`{`USENIX`}` Security 20). 2020: 1093-1110.

[14] Lu K, Walter M T, Pfaff D, et al. Unleashing Use-Before-Initialization Vulnerabilities in the Linux Kernel Using Targeted Stack Spraying[C]//NDSS. 2017.

[15] Wu W, Chen Y, Xing X, et al. `{`KEPLER`}`: Facilitating Control-flow Hijacking Primitive Evaluation for Linux Kernel Vulnerabilities[C]//28th `{`USENIX`}` Security Symposium (`{`USENIX`}` Security 19). 2019: 1187-1204.
