> 原文链接: https://www.anquanke.com//post/id/84932 


# 【技术分享】A year of Windows kernel font fuzzing


                                阅读量   
                                **102168**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：googleprojectzero
                                <br>原文地址：[https://googleprojectzero.blogspot.ch/2016/06/a-year-of-windows-kernel-font-fuzzing-1_27.html](https://googleprojectzero.blogspot.ch/2016/06/a-year-of-windows-kernel-font-fuzzing-1_27.html)

译文仅供参考，具体内容表达以及含义原文为准



**[![](https://p3.ssl.qhimg.com/t01d500b3b091e1bf59.jpg)](https://p3.ssl.qhimg.com/t01d500b3b091e1bf59.jpg)**

**翻译：**[**Ox9A82**](http://bobao.360.cn/member/contribute?uid=2676915949)

**稿费：200RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



在过去这一年内，我们通过大量的Fuzzing测试发现并报告了总计16个Windows内核在处理TrueType和OpenType字体时引发的漏洞。在这篇文章中，我们首先概述一下字体漏洞的背景，然后对我们所进行的Fuzzing测试工作做一个深入解析，其中包括整体的结果和2个案例的研究。在即将到来的第二篇文章里，我们将分享项目的具体技术细节，以及我们如何最大限度地优化过程的每个部分，并且是如何颠覆了Windows内核字体Fuzzing技术的现有状态。

<br>

**背景**

对于这篇文章的大多数读者而言，字体这个攻击面的重要性已经是不言而喻。在我们日常的使用中存在着大量的文件格式，这些格式在结构和语义上都非常复杂。因此，它们相应的难以正确的被实现，而这进一步由于以下事实而被放大：当前使用的大多数字体格式可以追溯到90年代早期，并且使用C或C++这种本地语言编写。控制的字体文件也是通过各种远程渠道如：文档，网站，脱机文件等方式交付的。最后很重要的是，负责执行程序来解释TrueType和OpenType字体格式的两个强大的虚拟机已经被证明可以用来创建可靠的利用链，因为它们能够对内存中的数据执行任意的四则运算，位运算和还有一些其他操作。基于以上所有原因，字体一直是内存破坏类漏洞的具有吸引力的来源。 

字体处理漏洞被许多实际攻击场合所使用，比如Duqu恶意软件的Windows内核TTF字体 0day漏洞（大量的这一类型的漏洞被紧急修复），comex通过一个FreeType类型的漏洞实现的iOS越狱，并且成功的挑战了pwn2own2015（Joshua Drake – Java 7 SE – 2013，Keen Team – Windows内核 – 2015）。

在过去的十年中，微软单独为其字体引擎发布了几十个安全公告，其他厂商和项目在这方面并没有比微软做的更好。现在，安全会议中已经充满了关于字体Fuzzing测试、已发现漏洞的细节的讨论。从用户安全的角度来看，这是一个非常不利的情况。如果一个系列的软件这么脆弱，但却被如此广泛的部署和使用，甚至大多数的安全人员都可以很容易的找到一个易用的0day漏洞，并将其用于实际的攻击中，那么显然是什么地方出现了问题。

<br>

**解决字体程序的安全问题**

如图所示，我们意识到这个情况需要在更一般的层面上来解决，而不是在整体的记录里再添加一两个漏洞，来获得一些虚假的安全感。让我们来直接面对它，我们目前使用的字体实现不会很快就被淘汰，因为性能仍然是字体光栅化的一个重要因素，并且代码库经过多年发展已经达到了很高的成熟度。一种通用的方法是限制字体处理代码在其各自环境中的特权，例如强制执行FreeType库的沙盒，或将字体引擎移出Windows内核（这也是微软从Windows10开始尝试去做的）。然而，这些方法大多是超出我们能力范围的。

那么，什么是在我们的能力范围之内的呢？我们可以增加漏洞挖掘的成本，并且完全清除一些程序中的简单漏洞来提高在相关代码中挖掘漏洞的门槛。自2012年初以来，我们一直使用内部的Fuzzing测试工具和一些可用资源来大规模地对FreeType项目进行Fuzzing测试。直到今天，我们已经得到超过50个错误报告，其中许多是可利用的内存破坏漏洞（见Project Zero bug列表）。一些手动的代码审计也同样发现了一些问题。我们希望这些努力已经清除了大部分或全部的通过简单的Fuzzing测试就可以发现的低级漏洞。

然而，对漏洞挖掘而言，FreeType依然是一个相对容易的目标 – 它的开源性使得可以非常方便的进行源代码审计，通过充分理解底层逻辑使得我们可以采用静态分析算法，并允许我们把它编译成任何平台的二进制文件，它具有较低的运行时间开销（与DBI相比）。例如，我们广泛使用了AddressSanitizer，MemorySanitizer和SanitizerCoverage工具，大大提高了错误检测率，并为我们提供了代码覆盖率信息，可以用于覆盖驱动的Fuzzing测试。

与之相反的是，对Windows内核及其字体实现的测试被认为是比平均目标更难的。源代码不可用，并且调试符号仅对于引擎的一部分（位图和TTF处理在win32k.sys，但是OTF处理在ATMFD.DLL中）来说是公共的。这使得任何手工工作都变得更难，因为它必须涉及对于以间接方式对字体数据进行操作的代码部分的逆向工程。此外，代码是在与图形子系统的其余部分共享的同一个模块中执行的，这使得所有类型的交互都是至关重要的。当然有办法来提高错误发现能力（例如特殊池），但同时也存在着阻碍，例如通用异常处理会潜在地掩盖一些错误。

在2015年初，我们通过手工拆开ATMFD中的Type1/CFF虚拟机，这是最完美的审计目标。完全独立，足够复杂，但又大小适中，充满了遗留的代码并且似乎在过去没有进行过适当审查 – 这是一个不可低估的混合物。该审计产生了向Microsoft报告的8个在Windows内核中漏洞，其中一些极为关键。有关该研究和最有趣的BLEND漏洞的详细描述，请看"One font vulnerability to rule them all"这篇博客。

CharString可以作为一个整体有效地进行审计，但是同样的策略不能应用于整个win32k.sys和ATMFD.DLL中字体相关的代码库。庞大的代码量和不同的程序状态使得我们几乎不可能去理解这些代码，更不用说保持整体的思考和寻找所有潜在的漏洞了。另一个选择当然是进行Fuzz测试 – 这种方法不能让我们对代码覆盖状态具有足够的自信，但是它的效率很高，只需要在初始设置时花费一点时间就可以，并且Fuzz技术已在过去被证明是高效的。事实上，根据公开的记录我们发现，超过90％的字体漏洞都是被Fuzzing技术发现的。这带来的额外的优点是报告通过Fuzzing获得的漏洞可以提高漏洞挖掘者的门槛，因为如果他们再使用类似的简单技术，将不再能找到任何漏洞。

考虑到这一点，我们在2015年5月开始了一个Windows内核字体Fuzz测试工作，试图采取以前对这个方面已知的技术来推进整个过程整体向前，并且进行优化来试图实现最高的效率。经过大约一年的时间，对于我们现在使用的Fuzz技术而言内核已经被清理干净了，而且我们相信我们获得的结果和使用的方法对于大众来说可能是很有趣的，这一系列文章会进行总结。

<br>

**结果**

下面是在去年通过Fuzzing测试发现的Windows内核所有漏洞的列表：

[![](https://p0.ssl.qhimg.com/t0150e0b232eafb9550.png)](https://p0.ssl.qhimg.com/t0150e0b232eafb9550.png)

错误条目的链接包括了崩溃的简要说明，启用了特殊池的Windows 7 x86中的崩溃日志样本，以及概念文件的强制性证明。 为了重现一些崩溃，可能还需要使用Microsoft提供的专用字体加载程序（但在下一篇文章中还将详细讨论）。

如表所示，崩溃通过三次迭代报告：第一次显然包含了大部分问题，因为Fuzzing工具从一开始就碰到了很多不同的状态和代码路径。第二和第三次迭代运行的时间更长，以防止漏洞被其他更频繁的崩溃所掩盖。每次运行（3-4个月）之间的时间段是Microsoft为报告的漏洞发布补丁的时间，并与Project Zero的90天披露日期（Microsoft在所有情况下都满足）相关联。一个案例更新了报告的时间，因为我们必须告诉Microsoft复现崩溃所必需的系统设置。

漏洞存在于处理SFNT表的代码中，在处理TTF和OTF文件时产生了编程错误。绝大多数的问题可以用于进行本地权限提升（进行沙箱逃逸等），甚至可以进行远程代码执行（对于将用户控制的文件直接传递到GDI的应用程序而言），这与Microsoft对这些漏洞的危害性评估一致。虽然我们是在Windows 7上进行的Fuzzing，但是报告的所有错误几乎仍然存在于较新版本的系统中。而且值得注意的是，虽然在Windows 10中通过在具有受限特权的用户模式进程中执行字体光栅化操作，来减轻特权提升场景，但是在该过程的上下文中的RCE仍然是可行的选项（尽管这比直接危及r0的安全更好一些）。

<br>

**撞洞**

没有什么更好的检验防御性漏洞挖掘的价值的方法，比得上观察到你上报的漏洞与在实际攻击中使用的exp（针对0day攻击）出现撞洞的情况了。尽管这些漏洞及其使用在过去有很多的记录，但是新发现是否会与2015年仍然流传的漏洞相冲突的问题仍有待解决。

事实证明我们不需要等待很久，我们最先提交的两个漏洞中的一个很快被证明就是Keen Team在2015年Pwn2own期间使用的TTF漏洞，并且一个OTF漏洞在2015年7月Hacking Team泄露的数据中被发现存在相同的（甚至包含了完整的利用代码），随后由Microsoft在紧急公告中修复。

有趣的是，这两个发生撞洞的漏洞其实是很难挖掘的。我们的Fuzzing工具在第一次运行期间不断地触发程序的崩溃，通过一些简单的分析，我们确定这两个条件确实可以通过在许多合法字体中执行微小的改变（比如单比特翻转，单字节交换）来触发。这似乎验证了我们通过挖掘上报漏洞来提高漏洞利用门槛的追求，因为它确认了这些漏洞通常会被其他研究人员发现和利用。

**与HackingTeam的0day撞洞**

在2015年5月向微软报告了第一批漏洞（7个OpenType和4个TrueType错误）后，我们耐心等待厂商发布相应的修补程序。很快，我们被告知他们重现了所有的问题，并安排在八月的补丁日进行修复。然而在7月20日当时我正在休假，我突然发现微软当天发布了一个临时的MS15-078安全公告：

[![](https://p2.ssl.qhimg.com/t0191d90b3da7299639.png)](https://p2.ssl.qhimg.com/t0191d90b3da7299639.png)

有趣的是，我是被致谢的三个人之一

[![](https://p0.ssl.qhimg.com/t013f10361fb9e279e6.png)](https://p0.ssl.qhimg.com/t013f10361fb9e279e6.png)

它迅速的证明了，我们之前报告的一个漏洞与Hacking Team泄漏文件中的两个独立研究人员发现的exp发生了撞洞。在2015年7月5日，Hacking Team公司的千兆数据文件被公布在Twitter帐户上。安全行业中的绝大多数人都急于调查这些突然出现的有价值的资源，其中不仅发现了监控产品的源代码和有争议的业务操作信息，而且还存在多个软件中的0day漏洞，例如Flash Player（4个exp），Windows 内核（2个exp），Internet Explorer，SELinux等。然而直到7月20日，都没有公开的信息表明CVE-2015-2426曾被暗地里报告给了微软。

这个exp利用漏洞来实现在Windows（最高8.1）平台的本地权限提升。有关漏洞和利用技术的详细分析可以在360 Vulcan团队的博客文章中找到，但实质上，这个漏洞是由OpenType驱动程序中的ATMFD.DLL做出的无效假设引起的，如图所示，在伪代码中表示如下：



```
LPVOID lpBuffer = EngAllocMem(8 + GPOS.Class1Count * 0x20);
if (lpBuffer != NULL) `{`
 // Copy the first element.
 memcpy(lpBuffer + 8, ..., 0x20);
 // Copy the remaining Class1Count - 1 elements.
`}`
```

这里，代码假定Class1Count（GPOS表中的16位字段）的值始终非零，并复制第一个表项，而不考虑实际值。 因此，如果字段等于0x0000，则动态分配的缓冲区会发生32（0x20）字节的溢出。通过适当的布局内核内存池（pool），可以将win32k.sys的CHwndTargetProp对象直接布置在发生溢出的内存区域之后，然后用一个用户模式的地址去修改它的vtable（虚函数表）。在那里，它只是泄漏了win32k.sys模块的基地址，之后构造了一个ROP链来禁用SMEP和调用实现权限提升的shellcode。

更重要的是，如果要通过Fuzz来触发漏洞，那么只需要将文件中特定位置（对应于Class1Count字段）的两个连续字节的值设置为0即可。换句话说，它可以被一个最简单的随机Fuzz工具测试出来，但是令人惊讶的是，在这么多安全机制被加入的情况下，这样的漏洞甚至可以存活到2015年。

出于好奇，原来HT的exp随后被NCC集团的Cedric Halbronn移植到64位的Windows 8.1中(见本文）。

**与pwn2own的漏洞撞洞**

三周后，2015年8月11日，第一批漏洞的补丁按计划发布。我再一次对致谢部分感到了惊讶，这次是把其中一个漏洞归功给了另一个研究人员。

[![](https://p2.ssl.qhimg.com/t016da1856be4429f2e.png)](https://p2.ssl.qhimg.com/t016da1856be4429f2e.png)

这一次是Keen Team的人，如果你查找CVE-2015-2455，其中的一个结果将是一个ZDI-15-388的页面，在页面的标题中就说明了这是pwn2own上使用的漏洞，并提到它是与“IUP”TrueType指令相关的。是的，这就是编号为368的漏洞。在pwn2own期间，该漏洞确实被利用来实现沙盒逃逸和通过“Adobe Reader”或“Adobe Flash Player”两者之一（具体不太清楚，因为在比赛期间曾使用了两个不同的TTF漏洞）获得对目标系统的完全控制。比赛发生在2015年3月19、20日。有一点疑问的是，对其他Team Keen的TTF漏洞的公开是在2015年REcon的“This Time Font hunting you down in 4 bytes”演讲上。值得注意的是，自打他们通过ZDI报告这个漏洞后，微软花了几乎5个月的时间来进行修复，但仍然满足Project Zero的90天披露时限（开始日期是5月21日）。

至于技术细节是在执行“IUP”指令时存在一个漏洞，它转换为通过TrueType指令集规范中的大纲插值未触及点：

[![](https://p0.ssl.qhimg.com/t0178bbab3ee9f7287c.png)](https://p0.ssl.qhimg.com/t0178bbab3ee9f7287c.png)

如果仔细观察，可以发现在末尾有一个重要说明：将IUP应用于区域0是一个错误。是的，就像你猜的那样这就是漏洞所在。win32k！itrp_IUP上的指令处理程序没有验证当前区域是不是区域0，因此它可以直接把区域0当成区域1去操作，这最终导致了基于内核内存池（pool）的缓冲区溢出，而且溢出的内容和长度都可控。下面的三个TrueType指令就足以触发崩溃：



```
PUSH [] / * 压入一个值* /
0
SZP2 [] / * SetZonePointer2 * /
IUP [0] / * InterpolateUntPts * /
```

更重要的是，当正常改变字体时，崩溃也很容易被触发 – 单个bit的翻转就足以将SZP2/SZPS指令的参数从1更改为0。因此，这是在我第一次运行Fuzzing测试时最先触发的崩溃。在我后来添加一个TrueType程序生成器之后，这个问题会出现在每一个测试用例身上，这迫使我们在生成器中通过绕过一些特定的结构来避免这个问题，直到bug被修复。

这个案例或许是一个很好的例子，即不需要Fuzz测试也不需要进行审计，仅仅通过仔细阅读官方文档就可以获得关键的漏洞点。

<br>

**最后的一些想法**

我们的成果和努力证明了正确的Fuzz测试仍然是一个非常有效的漏洞挖掘方法，即使是针对在理论上已经很成熟的和经过了严格测试的代码库而言。此外，这两个漏洞的撞洞现象证明了Windows内核字体漏洞仍然存在，至少是在2015年依然在野外被积极使用。在本系列的第二篇文章里，我们将对关键技术部分进行讨论，包括：我们是如何准备输入数据的，如何去变异和生成字体样本，大规模的Fuzzing Windows内核，如何复现漏洞和减少它们。
