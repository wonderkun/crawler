> 原文链接: https://www.anquanke.com//post/id/149402 


# 分析杀毒软件BitDefender中的整数溢出漏洞（第一部分）


                                阅读量   
                                **87315**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：zerodayinitiative.com
                                <br>原文地址：[https://www.zerodayinitiative.com/blog/2018/6/19/analyzing-an-integer-overflow-in-bitdefender-av-part-1-the-vulnerability](https://www.zerodayinitiative.com/blog/2018/6/19/analyzing-an-integer-overflow-in-bitdefender-av-part-1-the-vulnerability)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01b3f4a2db5cc7fc82.jpg)](https://p1.ssl.qhimg.com/t01b3f4a2db5cc7fc82.jpg)

在软件漏洞的“万神殿”中，安全软件中出现的漏洞被认为比其他软件中的漏洞更加严重。我们依靠安全软件来抵御攻击者，因此我们的防御系统中的漏洞不仅允许攻击者造成伤害，还会给我们带来错误的安全感。我们以为自己是受保护的，其实不然。这也是我们为什么特别关注有关于Bitdefender Internet Security一个被披露的[漏洞案例](https://www.zerodayinitiative.com/advisories/ZDI-17-942/)的原因之一，如果该漏洞被利用，Bitdefender Internet Security可能允许远程代码执行。这个现在已经被修复的漏洞是由于整数溢出引起的，并值得我们仔细观察。

接下来是提交案例的研究者的评论。这名研究人员的笔名为plume Pagefault，他出色地描述了这个漏洞，我们认为其他人会有兴趣看到一种方法来利用现代软件中的整数溢出，尽管有DEP和ASLR。下面是他对这个漏洞的描述，这个漏洞允许在受影响的系统上远程执行代码。



## Bitdefender的简介

Bitdefender提供了多种具有防病毒（AV）功能的产品，并且所有这些AV产品都安装了vsserv.exe SYSTEM服务。该服务用于处理AV扫描请求。正如你所期望的AV引擎一样，它通过一系列具有.xmd或.cvd扩展名的压缩可执行文件（位于%PROGRAMFILES%Common FilesBitdefenderBitdefender Threat ScannerAntivirus_XXXXPlugins目录下）来处理各种文件类型（如PDF、JPG、DOC、EXE）和EXE包。然而，该引擎还有一个不太为人知的功能是模拟遇到的可执行代码，用于检测未知或混淆的病毒。

当遇到x86可移植可执行文件（PE）时，Bitdefender通过包含在cevakrnl.xmd和ceva_emu.cvd文件中的高度复杂的代码仿真器来虚拟执行PE 。仿真器创建一个私有虚拟地址空间，处理字节码解释，提供各种Windows API的实现，并为频繁执行的地址创建实时（JIT）代码。



## 漏洞的简介

当仿真器检测到对函数的调用时，cevakrnl.xmd!sub_366F4D0()会被调用。该函数处理仿真函数中的第一条指令，通过一个常量表搜索匹配项。在处理以下指令时，算法会考虑解释器的当前状态。换句话来说，对于每个匹配的指令，都将搜索另一个匹配表以查找以下指令。

[![](https://p4.ssl.qhimg.com/t0108a0d5a34b2e9003.png)](https://p4.ssl.qhimg.com/t0108a0d5a34b2e9003.png)

当函数中的前16个字节被仿真器匹配时，或者当指令序列未知时，初始搜索结束。

常量表中最后的匹配项会提供函数起始位置之前的许多已知字节，以及函数起始位置之后的16字节。

[X bytes before]

FUNCTIONSTART:

16 bytes already matched

[Y bytes after]

然后，读取和检查字节，以确定它们是否匹配已知的AV签名。如果匹配，则调用检测到的代码签名对应的处理程序以进行进一步处理。



## 深入分析

当遇到Themida 加壳工具代码序列时，将调用sub_36906D0()函数，以便对匹配的序列执行代码解释。[![](https://p5.ssl.qhimg.com/t019e1d441e5c4898d7.png)](https://p5.ssl.qhimg.com/t019e1d441e5c4898d7.png)

在解释代码中，唯一的变量是读取ebx的值的ebp偏移量“X”。该函数从代码流中提取偏移量，并使用它从仿真堆栈中获取ebx的值。

[![](https://p0.ssl.qhimg.com/t01191bb15059cdce4f.png)](https://p0.ssl.qhimg.com/t01191bb15059cdce4f.png) 

接下来将解释mov ecx, [ebx]指令，并从ebx保存的模拟地址中提取ecx的值。[![](https://p1.ssl.qhimg.com/t01851c273495709314.png)](https://p1.ssl.qhimg.com/t01851c273495709314.png)

接下来解释下面的代码序列：[![](https://p1.ssl.qhimg.com/t01787c8ca4269c8f8b.png)](https://p1.ssl.qhimg.com/t01787c8ca4269c8f8b.png)

该进程会根据ecx + dword[ecx + 0x78 + word[ecx+0x3c]] 计算出仿真esi。

[![](https://p2.ssl.qhimg.com/t0146a7350472e65a13.png)](https://p2.ssl.qhimg.com/t0146a7350472e65a13.png) 

接下来从仿真esi中提取总共0x28字节，并且在偏移0x18处读取dword（对应仿真代码中的mov edi，[esi + 18h]）。[![](https://p1.ssl.qhimg.com/t01b982c0821a9cf44c.png)](https://p1.ssl.qhimg.com/t01b982c0821a9cf44c.png)

该dword(N)乘以4，但没有进行整数边界检查，并在malloc()的调用中传递。这导致了一个大小不足的缓冲区的分配。[![](https://p4.ssl.qhimg.com/t01aea9504bbaa4d251.png)](https://p4.ssl.qhimg.com/t01aea9504bbaa4d251.png)

接下来进入一个循环，在该循环中，缓冲区填充了在仿真堆栈上的偏移处找到的N个字符串的CRC32校验和。当字符串的偏移量过大时，循环也会中止。[![](https://p2.ssl.qhimg.com/t01ebb71dda50b9c874.jpg)](https://p2.ssl.qhimg.com/t01ebb71dda50b9c874.jpg)

这提供了我们执行代码所需的一切，第一个是可以用我们自己的内容覆盖任意数量字节的能力。这需要包含所计算出的CRC具有期望值（例如反向CRC）的字符串。所包含的CRC32算法是非标准的，因为它考虑了每个字符串的终止零字节。然而，通过蛮力攻击，逆向分析它是可能的。[![](https://p2.ssl.qhimg.com/t01576b118372c6d2a6.png)](https://p2.ssl.qhimg.com/t01576b118372c6d2a6.png)

当调用匹配的函数时，漏洞会被触发，期望数量的字节随任意内容溢出。



## 结论（第一部分）

通过深入分析，我们可以看到，攻击者可以在受影响的Bitdefender版本上执行任意代码。供应商使用更新[73447](https://www.bitdefender.com/site/view/Desktop-Products-Updates.html)解决了此漏洞（及其他漏洞）。对于Bitdefender的用户而言，应该确保自己的系统使用的是更新后的版本或可用于系统的更新。Pagefault的分析并没有在这里结束。在我们的下一篇博客中，我们将讨论漏洞利用本身，以及如何避免受到DEP和ALSR的影响。



 审核人：yiwang   编辑：少爷
