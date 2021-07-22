> 原文链接: https://www.anquanke.com//post/id/86583 


# 【技术分享】内核池溢出漏洞利用实战之Windows 10篇


                                阅读量   
                                **97503**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[http://trackwatch.com/kernel-pool-overflow-exploitation-in-real-world-windows-10/](http://trackwatch.com/kernel-pool-overflow-exploitation-in-real-world-windows-10/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01db22cbe35e703fd8.jpg)](https://p1.ssl.qhimg.com/t01db22cbe35e703fd8.jpg)

译者：[an0nym0u5](http://bobao.360.cn/member/contribute?uid=578844650)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

****

本文是内核池溢出漏洞利用实战之Windows 7篇的续集，我们将会在Windows 10系统中实现相同漏洞的利用，这将更加充满挑战因为微软公司自从Windows 8后采取了大量针对内核池攻击的防御措施。本文将更加深入地分析池相关的内容，因此建议读者先阅读第一篇文章以作铺垫。

**1.1Windows 8系统的防护措施**

Windows 8系统在池中采取了一系列安全改善措施，在这里我不作详尽的列举，不过我们可以关注这几点：

**a.真正安全的链接/断开链接**

**b.池索引验证：池索引覆盖攻击早已不是什么难事**

**c.不执行非分页池（No-Execute）：这是一种新式的非分页池，可以说是非分页池的不执行（NX）版，Windows默认使用该类型的池而不是以往的非分页池**

**d.SMEP：管理模式执行保护**

**e.MIN_MAP_ADDR：内存首地址0x1000是保留地址不能被分配，这可以防御空引用类漏洞的攻击，这种防护已经在Windows 7系统和64位的Vista系统中被攻破**

**f. NtQuerySystemInformation()缺陷：该缺陷在低完整性场景下（通常是浏览器沙箱）不再可以被利用**

关于我们利用的配额进程指针覆盖漏洞说明如下：

**a.进程指针目前通过cookie进行了编码：**

1）.进程指针在分配块时进行如下编码：ExpPoolQuotaCookie 异或 ChunkAddress 异或 ProcessPointer

2）.块空闲时进程指针被用作canary并进行如下编码：ExpPoolQuotaCookie 异或 ChunkAddress

**b.进程指针被解码后必须指向内核空间否则会触发异常检测**

如果你想了解详尽的Windows 8关于这方面的缓解措施你可以读一下这篇文章[1]（Windows 8系统堆内部解析），另外该文作者Tarjei Mandt的另外一篇文章[2]（在windows 7系统中利用内核池漏洞）提到的每一种攻击手法都已经得到了有效缓解。Windows 8系统中确实有通过控制RIP协议来获取数据的漏洞可利用，但是这些漏洞在Windows 10系统中已经通过在_OBJECT_HEADER中设置cookie的方式被修复。所以如果你想实现利用配额进程指针覆盖漏洞这种在Windows 7系统中使用过的攻击手段，我们需要做到：

1）池Cookie（PoolCookie）：用它来正确编码指针

2）溢出块地址：也需要用它来编码指针

3）已知地址内核空间的任意数据：我们不仅要正确编码指针，该指针指向内核空间的同时还要指向我们伪造的一个结构。

让我们来尝试一下吧！

<br>

**二、获取溢出块指针**

****

这一部分会很简短，前提是你还记得Windows 7系统下的基本利用方式池喷射技术，好了，是时候放大招了，我们将采用高级池喷射技术，该技术在这篇文章[3]（Windows内核池喷射技术）中有阐述。运用该文中的方法，我们可以预测任何可能的分配行为，当然有了IOCTL的漏洞我们很容易就能知道输入输出管理器分配给系统缓冲区（SystemBuffer）的地址，由于系统缓冲区（SystemBuffer）是溢出的，我们溢出的块在系统缓冲区（SystemBuffer）之后，因此我们可以得到块地址。注意：我之前提过几次，NtQuerySystemInformation漏洞在低完整性场景下不可利用，因此我们不能在低完整性层面拿到这个地址而是至少要在中等完整性层面。

<br>

**三、获取已知地址内核空间的一些任意数据**

****

有好几种方式可以实现这个目标，过去很长时间，我都是利用池喷射技术并结合随机IOCTL系统调用来往空闲的内核空间存放数据，但这种方式并不可靠，从那以后我找到了更加可靠的方法。

CreatePrivateNamespace函数用于在分页池中分配一个目录对象，以下是该函数的定义：



```
HANDLE WINAPI CreatePrivateNamespace(
  _In_opt_ LPSECURITY_ATTRIBUTES lpPrivateNamespaceAttributes,
  _In_     LPVOID                lpBoundaryDescriptor,
  _In_     LPCTSTR               lpAliasPrefix
);
```

吸引人眼球的地方：

1）该函数返回一个句柄，这很正常因为这只是一个对象，不过这意味着我们可以在分页池中获取该目录对象的地址。

2）该函数第二个参数是一个边界描述符，它必须唯一，所以你可以利用CreateBoundaryDescriptor函数创建它：

**a.函数定义**



```
HANDLE WINAPI CreateBoundaryDescriptor(
  _In_ LPCTSTR Name,
  _In_ ULONG   Flags
);
```

**b.调用函数后赋值给一个变量，我们姑且起个HelloWorld!**

关键点来了：边界描述符名直接存储在分页池中的对象中，因此以下代码

 [![](https://p4.ssl.qhimg.com/t01166656f4cf3352f2.png)](https://p4.ssl.qhimg.com/t01166656f4cf3352f2.png)

给出了分页池块：

 [![](https://p1.ssl.qhimg.com/t0151c2e82dcb84c8cc.png)](https://p1.ssl.qhimg.com/t0151c2e82dcb84c8cc.png)

《Hello World!》名存储在对象地址+0x1A8偏移处，看起来对名字没啥限制：

 [![](https://p3.ssl.qhimg.com/t018a72ac7aaf16e23b.png)](https://p3.ssl.qhimg.com/t018a72ac7aaf16e23b.png)

这里块大小变成了之前的两倍大，然而只是用来存储边界描述符名！顺便提一点，既然该对象的大小可控，它就变成了让分页池喷射的强大工具。不管怎样我们已经能够往内核空间存放一些任意数据了，并且还可以利用NtQuerySystemInformation漏洞获取它的地址。

<br>

**四、获取池Cookie**

****

气氛好像一下子紧张起来了。ExpPoolQuotaCookie是由驱动产生的一个指针大小的8字节Cookie（64位系统下），它的熵足够安全，我们没有办法猜测或者计算出它的值。乍看上去唯一获取池cookie的方式是发现强大但很少见的任意读取漏洞，于是我研究了ExpPoolQuotaCookie的利用过程。当在进程的配额管理过程中有池块被利用时，池类型（PoolType）会设置配额位(Quota Bit)，并且有一个位于池头后8个字节（64位系统）的编码过的指针指向它：

 [![](https://p1.ssl.qhimg.com/t013dc28a86bcb774af.png)](https://p1.ssl.qhimg.com/t013dc28a86bcb774af.png)

但是在分配块时问题来了，块被释放后它看起来变了：

 [![](https://p5.ssl.qhimg.com/t01e6212db95f55972a.png)](https://p5.ssl.qhimg.com/t01e6212db95f55972a.png)

这里Process Billed值只是池Cookie和块地址的异或，这个值用于canary来检测池溢出攻击，因此如果成功读取到Process Billed值的话没准能得到池Cookie！假想有如下攻击：

1）运用池喷射技术分配一些可控的块，块地址已知并且随时可释放

2）先释放其中一个块

3）然后释放它前面的块

4）在之前的两个块地址处重新分配一个块，这可以通过IOCTL漏洞实现，要确保系统缓冲区（SystemBuffer）在这里已经分配

5）即使有了空闲空间和块的重新分配，前一个池头也不会重写，这意味着池Cookie和块地址的异或值仍然在块数据中

       [![](https://p1.ssl.qhimg.com/t0138c87ab4111a071f.png)](https://p1.ssl.qhimg.com/t0138c87ab4111a071f.png)[![](https://p5.ssl.qhimg.com/t0173dd80a28a07bbae.png)](https://p5.ssl.qhimg.com/t0173dd80a28a07bbae.png)[![](https://p4.ssl.qhimg.com/t017b991364b3a9f4e4.png)](https://p4.ssl.qhimg.com/t017b991364b3a9f4e4.png)

[![](https://p1.ssl.qhimg.com/t01753b11c01ec92ea6.png)](https://p1.ssl.qhimg.com/t01753b11c01ec92ea6.png)[![](https://p4.ssl.qhimg.com/t01942c972557924b78.png)](https://p4.ssl.qhimg.com/t01942c972557924b78.png)

这里可以假想一个返回的数据多于写入数据的IOCTL漏洞：带外读取漏洞，用最小的一次带外读取就可以获取到池Cookie，因此我们从刚开始的任意读取转换成了带外读取来获取池Cookie，这是一种更常见的手段，之所以这么说是因为我在同样的驱动中发现了带外读取漏洞！

**4.1关于CVE-2017-7441**

以下是编号为0x22E1C0的IOCTL漏洞的伪代码：

 [![](https://p4.ssl.qhimg.com/t016e8fe8d5cea561cf.png)](https://p4.ssl.qhimg.com/t016e8fe8d5cea561cf.png)

获取我们的输入后驱动器在系统缓冲区中调用了RtlLookupElementGenericTableAvl函数，如果该函数执行成功的话，它会在系统缓冲区中通过memcpy指令复制返回值，在复制前会检查空间大小，因此这次memcpy不存在问题，不过在计算驱动器写入多少字节时会出错，多返回2个多余的字节。如果想定位到有漏洞的代码，函数RtlLookupElementGenericTableAvl必须执行成功并且至少还要能够控制它返回值的长度，做到这一点的唯一方式是在系统缓冲区中写入当前进程id，RtlLookupElementGenericTableAvl函数运行正常且将路径返回到当前进程的可执行文件。或多或少我可以控制可执行文件的路径长度，Windows下最大路径长度为255字节。为了获取8字节的池Cookie需要用4个不同的可执行文件（路径长度不同）创建4个不同进程来触发4次该漏洞。

<br>

**五、结论**

****

至此我们已经完美实现了从Windows 7系统到Windows 10系统的内核池漏洞利用过程，在Windows 10系统下利用池溢出漏洞比在windows 7下只差一个小漏洞的距离。池喷射技术和NtQuerySystemInformation漏洞提供给攻击者太多内核态的信息，使得攻击者发动针对池的攻击依然可靠。你可以在github上找到我利用的[代码](https://github.com/cbayet/Exploit-CVE-2017-6008)。

<br>

**六、参考文献**

****

[1] [https://media.blackhat.com/bh-us-12/Briefings/Valasek/BH_US_12_Valasek_Windows_8_Heap_Internals_Slides.pdf](https://media.blackhat.com/bh-us-12/Briefings/Valasek/BH_US_12_Valasek_Windows_8_Heap_Internals_Slides.pdf) – Windows 8 Heap internals

[2] [http://www.mista.nu/research/MANDT-kernelpool-PAPER.pdf](http://www.mista.nu/research/MANDT-kernelpool-PAPER.pdf) – Kernel Pool Exploitation on Windows 7

[3] [http://trackwatch.com/windows-kernel-pool-spraying/ ](http://trackwatch.com/windows-kernel-pool-spraying/)– Pool Spraying article

[4][ https://github.com/cbayet/Exploit-CVE-2017-6008](https://github.com/cbayet/Exploit-CVE-2017-6008) – Source code of the exploit
