
# 【技术分享】ASLR保护机制被突破的攻击技术分析


                                阅读量   
                                **131500**
                            
                        |
                        
                                                                                                                                    ![](./img/85540/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：cs.vu.nl
                                <br>原文地址：[http://www.cs.vu.nl/~herbertb/download/papers/revanc_ir-cs-77.pdf](http://www.cs.vu.nl/~herbertb/download/papers/revanc_ir-cs-77.pdf)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](./img/85540/t01543cafc9f3ac3a9d.png)](./img/85540/t01543cafc9f3ac3a9d.png)

作者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：300RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**摘要**

最近，基于硬件的攻击已经开始通过Rowhammer内存漏洞或旁路地址空间布局随机化保护机制来攻击系统了，这些攻击方式都是基于处理器的内存管理单元（MMU）与页表的交互交互方式的。这些攻击通常需要重复加载页表，以观察目标系统行为的变化情况。为了提高MMU的页表查找速度，现代处理器都使用了多级缓存，例如转译查找缓存（translation lookaside buffers，TLB）、专用页表缓存，甚至通用数据缓存。要想攻击得手，需要在访问页表之前可靠地刷新这些缓存。为了从非特权进程中刷新这些缓存，攻击者需要基于这些缓存的内部体系结构、大小以及缓存交互方式来创建专门的内存访问模式。虽然关于TLB和数据高速缓存的信息通常都会在供应商的处理器手册中发布，但是关于不同处理器上的页表高速缓存的特性方面的信息却鲜有提及。在本文中，我们改进了最近提出的针对MMU的EVICT + TIME攻击，对来自Intel、ARM和AMD的20种不同微架构中页表缓存与其他缓存的内部架构，大小以及其交互方式。同时，我们以代码库的形式将我们的发现公之于众，该代码库不仅提供了一个方便的接口来刷新这些缓存，同时还可以用来在新的体系结构上自动逆向页表缓存。

<br>

**引言**

由于添加到系统中的高级防御日益增加，致使针对软件的攻击的难度也是与日俱增，因此，针对硬件的攻击反而成为一种更有吸引力的替代方案。在这些攻击也是五花八门，既有利于Rowhammer漏洞攻击系统的，也有使用旁路攻击破坏地址空间布局随机化来泄漏加密密钥的，甚至还有用来跟踪鼠标移动的。

在这些针对硬件的攻击中，有许多攻击都是通过滥用现代处理器与内存来实现的。目前，所有的处理器的核心都是存储器管理单元（MMU），它通过在多个进程之间提供虚拟化内存来简化可用物理存储器的管理工作。MMU使用称为页表的数据结构来执行虚拟存储器到物理存储器之间的转换。页表是基于硬件的攻击的目标所在。例如，由Rowhammer漏洞导致的页表页中的单个位翻转，将会授予攻击者某种访问权限来访问本来无法访问的物理内存，从而进一步获得超级用户权限。此外，诸如ASLR和其他使用ASLR引导的安全防御机制都依赖于代码或数据都是被随机存储到虚拟存内存中这一特性的。由于这个（秘密）信息被嵌入在页表中，攻击者可以利用MMU与页表的交互方式进行旁路攻击，以获取这些机密信息。

从虚拟内存到物理内存的转换通常会很慢，因为它需要进行多次内存访问来解析原始虚拟地址。为了提高性能，现代处理器都使用多级缓存，例如转译查找缓存（TLB）、专用页表缓存，甚至通用数据缓存。为了成功攻击页表，攻击者经常需要重复刷新这些缓存，以观察系统在处理页表时的行为。通过参阅处理器手册，人们可以很容易找到TLB和数据高速缓存的各种详细信息。然而，关于页表缓存的信息，例如它们的大小和行为，通常是很难找到的。因为没有这些信息，攻击者需要借助于试错法，所以，如果他们要想打造可以适用于多种体系结构上的攻击的话，难度可想而知。

在本文中，我们对现有的AnC进行了重大的升级改造。AnC是一种针对MMU的EVICT + TIME旁路攻击，它能够对Intel、ARM和AMD等公司的20多种微架构的处理器的页表缓存的大小、内部体系结构以及它们与其他缓存的交互方式进行逆向。AnC依赖于以下事实：MMU查找的页表将被存储在最后一级高速缓存（LLC）中，以供下一次查找时使用，从而提高地址转换速度。通过刷新LLC的部分内容和对页表查找进行定时，AnC可以识别出LLC的哪些部分是用来存储页表的。除了刷新LLC，AnC还需要刷新TLB以及页表缓存。由于有关TLB和LLC的大小的信息是可知的，所以攻击者可以使用AnC来逆向自己感兴趣的页表缓存的特性，如其内部结构和大小等。

简而言之，我们做出了以下贡献：

我们描述了一种新技术，可以用来对现代处理器中非常常见却无文档说明的页表缓存进行逆向工程。

我们利用Intel、ARM和AMD的20种不同微结构处理器对我们的技术进行了深入评估。

我们以开源软件的形式发布了用于刷新缓存的框架实现。我们实现的框架提供了一个方便的接口，可以方便地应用于我们已经测试的各种微架构上，来刷新页表缓存，并且它还可以用来自动检测新处理器上的页表缓存。更多信息，请访问： [https://www.vusec.net/projects/anc](https://www.vusec.net/projects/anc) 

<br>

**背景和动机 **

在本节中，我们讨论分页内存管理机制和它在大多数现代处理器上的实现。此外，我们还将考察MMU是如何进行虚拟地址转换的，以及用于提高这种转换性能的各种缓存。

**页式技术和MMU**

页面技术已经成为现代处理器架构的一个组成部分，因为它能够通过虚拟化技术来简化物理内存的管理：由于地址空间有限，操作系统不再需要重新分配应用程序的整个内存，并且不再需要处理物理内存碎片。此外，操作系统可以限制进程访问的内存空间，防止恶意代码或故障代码干扰其他进程。

它所带来的直接后果，就是许多现代处理器架构都采用了MMU，一个负责将虚拟地址转换为相应物理地址的硬件组件。转换信息被存储在页表中——一种多级单向树，每个级别都可以由虚拟地址的一部分进行索引，从而选择下一级页表，或者在叶级别，也就是物理页面。因此，每个虚拟地址都能够从树的根节点到叶节点唯一地选出一条路径以找到对应的物理地址。

图1详细展示了MMU是如何在x86_64上执行虚拟地址转换的。首先，MMU读取CR3寄存器以找到顶级页表的物理地址。然后，用虚拟地址的前9位作为索引在该页表中选择页表项（PTE）。这个PTE包含对下一级页表的引用，然后用虚拟地址中接下来9位的作为索引继续选择页表项。通过对下两个级别重复该操作，MMU就可以在最低级页表中找到对应于0x644b321f4000的物理页了。

[![](./img/85540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0160dec3ffed79a683.png)

图1：在x86_64架构上，将0x644b321f4000转换成其对应的内存页的MMU的页表查询过程。

**缓存MMU的操作**

如果MMU可以避免从头开始解析其最近已解析过的虚拟地址的话，那么内存的访问性能就会得到极大的改善。为此，CPU会将解析过的地址映射存储到TLB高速缓存中。因此，如果在TLB中命中的话，就无需查询各个页表了，而这个过程是需要花费许多时间的。此外，为了提高TLB未命中时的性能，处理器会将页表数据存储到数据高速缓存中。

现代处理器还可以进一步提高TLB未命中情况下的地址转换性能，方法是使用页表缓存或转译缓存来缓存不同级别页表的PTE。虽然页表缓存使用物理地址和PTE索引进行索引，但是转换缓存使用的是已经过部分解析的虚拟地址。通过转译缓存，MMU可以查找虚拟地址并选择具有最长匹配前缀的页表，即选择存在于给定虚拟地址的高速缓存内的最低级页表。虽然这允许MMU免去部分页表的查询工作，但是转译缓存的实现同时也带来了额外的复杂性。

此外，这些高速缓存在实现方式也可以多种多样，不仅可以实现多个专用的高速缓存供不同的页表级使用，而且还可以实现单个高速缓存来供不同的页表级共享，或者甚至可以作为一个可以缓存PTE的TLB来加以实现。例如，AMD的Page Walking Caches（就像在AMD K8和AMD K10微架构中发现的那样）采用的是统一页表缓存的方式，而Intel的Page-Structure Caches的实现采用的是专用的转译缓存的方式。类似地，ARM在针对低功耗和硅利用率而优化的设计中实现了统一的页表缓存（页表查询缓存），同时它们在针对高性能而优化的设计中实现了统一的转换缓存（中间页表查找缓存）。

图2展示了当MMU翻译虚拟地址时不同高速缓存的交互方式。虽然TLB和缓存具有完整的文档说明，但是关于页表和翻译缓存的诸多细节仍然缺乏相关的文档说明。

[![](./img/85540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019def034f041288b0.png)

图2：MMU的通用实现以及将虚拟地址转换为物理地址的所有组件。

**研究动机**

最近的基于页表滥用的硬件攻击，都要求能够正确刷新页表缓存，才能完成相应的操作。例如，预取攻击依赖于一个正确的时机，届时虚拟地址转换恰好在一个页表缓存中部分成功，借以了解内核中随机化地址方面的信息。而Rowhammer攻击在处理页表时则需要重复刷新TLB和页表缓存，以扫描物理内存中的敏感信息 

另一个需要刷新页表缓存的例子是AnC攻击。MMU的页表查询结果会被缓存到LLC中。AnC利用这个事实来完成FLUSH + RELOAD攻击，以确定出MMU在页表查询期间访问的页表内存页中的偏移量。知道这个偏移量后，就能找到经过随机化处理后的虚拟地址，从而攻陷ASLR防御机制。但是，为了完成一次可靠的攻击，AnC需要尝试多种不同的访问模式，并且每种模式都需要尝试许多次，并且每次都需要有效地刷新页表缓存以便触发完整的页表查询流程。因此，关于页表缓存的内部工作机制的知识，对于完成正确高效的AnC攻击来说是非常必要的。

在某些情况下，TLB用作页表缓存。在这些情况下，cpuid指令可以用来了解不同TLB的大小，这样就知道了不同页表缓存的大小了。但是，在一些x86_64微体系结构上，cpuid指令并不会给出所有TLB的大小。例如，尽管在Intel Sandy Bridge和Ivy Bridge处理器上存在可以缓存1 GB页面的TLB，但这些信息根本无法通过cpuid指令获取。此外，在其他CPU体系结构上，可能没有办法获取TLB的大小，或者页表缓存可能已经实现为完全独立的单元。因此，我们需要一个更通用的方法来探索页表缓存的重要属性。

<br>

**页表缓存逆向技术**

我们现在开始讨论如何改造AnC技术，以探测页表缓存的各种属性。实际上，我们需要克服许多挑战，才能使AnC适用于不同的架构，这些将在后面展开详细的讨论。

**使用MMU的缓存信号 **

[![](./img/85540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0157edf8ac3bdb1710.png)

代码清单1：设计原理示意代码

在了解页表缓存时，我们依赖于这样一个事实，即MMU的页表查询结束于目标处理器的数据缓存处。下面以Intel x86 64为例进行说明，这里假设使用了四个页表级别，那么给定虚拟地址v的MMU的页表查询会将来自4个页表内存页的4个缓存行放入L1数据缓存以及L3，假设L3包括L1。这样一来，如果高速缓存行仍然位于数据缓中的话，那么再次对虚拟地址v进行页面查询的时候，就会变得相当快。

CPU数据缓存被分为不同的缓存集。每个缓存组可以存储多达N个缓存行，这被称为N路组相关缓存。Oren等人发现，给定两个不同的（物理）内存页面，如果它们的第一个缓存行属于同一缓存组，那么页面中的其他缓存行也会共享（不同的）缓存组，即如果我们在一个与缓存行边界对齐的页面内选择了偏移t，那么另一内存页中的偏移t处的缓存行就会共享相同的缓存组。这是因为：为了让两个内存页的第一个缓存行位于同一个缓存组中，那么决定缓存组和切片（slice）的两个页面的物理地址的所有位必须是相同的，并且两个页面内的偏移将共享相同的低位。

利用缓存的这个特性，我们可以轻松利用一些内存页来用作驱逐缓冲区。假设用于转换虚拟地址v的四个页表项中的一个正好位于页表内存页的偏移零处。当我们访问驱逐缓冲区中所有页面的第一个缓存行的时候，我们将从缓存中驱逐掉MMU的最近转换虚拟地址v时的页表查询结果。因此，虚拟地址v的下一次页表查询将会变得稍微慢一些，因为它需要从内存获取前面提到过的页表项。这就是一个EVICT + TIME攻击的例子，通过它，AnC就能够在存储页表项的内存页面中，从潜在的64个缓存行中找出4个缓存行。注意，通过尝试来自虚拟地址v之外的各种偏移，我们可以弄清楚每个级别中的页表项对应于哪些缓存行中。例如，如果我们在v + 32 KB上执行EVICT + TIME，与在v上执行EVICT + TIME时相比发生变化的缓存行对应于级别1页表的缓存行。

这是因为在x86 64架构上，每个缓存行可以存储8个页表项，映射32 KB的虚拟内存。

假设一个页表缓存对应于一个页表级别，若不刷新该级别的页表缓存的话，我们就无法观察MMU在该级别上的活动。举例来说，假设有一个页表缓存，它用来缓存具有32个表项的2级页表。假设2级页表中的每个表项可以映射2 MB的虚拟内存，当我们访问连续的64 MB虚拟缓冲区（以2MB为边界）的时候，我们将刷新该页表缓存。因此，我们可以轻松地通过蛮力方式穷举每个级别的潜在页表缓存的大小。例如，如果在x86 64架构的Intel处理器上我们无法通过AnC观察到上面三级页表的信号，那是因为该页面（转译）缓存位于2级页表中。然后，我们可以蛮力破解该缓存的大小，然后移动到上一级。代码清单1为我们展示了具体的实现过程。注意，与AnC不同，我们采用了一个已知的虚拟地址，所以我们可以准确知道MMU信号应该出现在缓存中的什么地方。当然，为了提高清单1中代码的鲁棒性，使其适用于多种处理器架构，我们还需要解决许多问题，具体将在后文中详细展开。

**确保存取顺序**

许多现代CPU架构都实现了乱序执行技术，其中指令的执行顺序取决于输入数据的可用性，而不是它们在原始程序中的顺序。在应用乱序执行技术之后，指令在解码之后被插入等待队列中，直到它们的输入操作数可用为止。一旦输入操作数可用，该指令就会被发送到相应的执行单元，这样的话，这条指令就会先于前面的指令由该单元执行了。此外，这种CPU架构通常都是超标量的，因为它们具有多个执行单元，并且允许将多条指令调度到这些不同的执行单元中并行执行。在指令执行完成之后，它们的结果将被写入另一个现已“退休的”队列中，该队列以原始程序的顺序进行排序，以保证正确的逻辑顺序。此外，有些现代CPU架构不仅具有针对指令的乱序执行的能力，而且它们还具有对内存操作进行重新排序的能力。为了测量这种CPU体系结构上单个指令的执行时间，我们必须在定时指令之前和之后注入内存屏障，并目标代码之前和之后插入代码屏障，以清除正在运行的指令和内存操作。为了串行化内存存取顺序，我们可以在ARMv7-A和ARMv8-A上面使用dsb指令，而在x86_64上，可以通过rdtscp和mfence指令保证串行化的内存存取顺序。为了串行化指令顺序，我们可以在x86_64上使用cpuid指令，在ARMv7-A和ARMv8-A上使用isb sy指令。

**定时**

在缓存命中和缓存未命中的情况下，存在从几百纳秒或甚至几十纳秒的性能差异，因此我们需要高精度的定时源才能能够区分缓存是否命中。虽然在兼容POSIX的操作系统上可以通过clock_gettime（）来获取定时信息，但是在各种ARMv7-A和ARMv8-A平台上，它们提高的定时信息却不够精确。

许多现代处理器架构都提供了专用寄存器来计数处理器的周期数，从而提供高精度的定时源。虽然这些寄存器可通过各种rdtscp指令中的非特权rdtsc进行访问，但默认情况下，ARMv7-A和ARMv8-A上的性能监视单元（PMU）提供的PMCCNTR寄存器是无法访问的。此外，当最初引入这些寄存器时，没有确保它们在内核之间是同步的，并且直接利用处理器时钟使其计数进行递增。在这些情况下，进程迁移和动态频率调整会对定时造成一定程度的影响，甚至让它变得不再可靠。

考虑到当今大多数处理器都具有多个内核，在循环中简单递增全局变量的线程可以提供一个基于软件的周期计数器。我们发现这种方法在各种平台上都能够可靠地工作，并且可以提供很高的精度度。请注意，JavaScript版本的AnC也采用了类似的技术来构建高精度的计时器。

**讨论**

利用x86_64平台上的cpuid以及ARMv7-A和ARMv8-A上的扁平设备树（FDT），我们可以检测包括处理器属性（如TLB、缓存、处理器和供应商的名称）和微架构的等处理器拓扑信息。有了这些信息，我们就可以构建一个适当的驱逐组，以便在缺少页表和转译缓存的架构上成功地自动执行AnC攻击。因此，在带有页表或转译缓存的体系结构上，我们可以通过构建驱逐组并尝试渐进式执行AnC攻击来逆向这些缓存的大小。

<br>

**评测**

我们使用Intel、ARM和AMD等公司从2008年到2016年期间发布的20个不同的CPU对我们的技术进行了全面的评估，并发现了每个页表级的页表缓存的具体大小（我们称2级页表为PL2），以及利用我们的技术逆向这个信息所需要的时间。同时，我们还提供了每种CPU的缓存和TLB的大小。

我们的研究结果总结见表1。下面，我们将逐一介绍各个供应商产品在这些方面的特点和差异。

[![](./img/85540/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0199001842b2ddad50.png)

表1：22种不同微架构的规格和逆向结果

**Intel**

在英特尔的处理器中，最后一级缓存是包含型的，这意味着最后一级缓存中可用的数据必须在较低级别的缓存中可用。由于这个特性，只要从最后一级缓存中逐出缓存行就足够了，因为这将导致它们将被从较低级别的缓存中逐出。我们发现，英特尔的页面结构缓存或切片转译缓存是在Intel Core和Xeon处理器上实现的，至少是Nehalem微架构。在Intel Core和Xeon处理器上，具有可供24-32个PL2表项和4-6个PL3表项的高速缓存，而在Silvermont处理器上，只有一个高速缓存，仅仅可以供12-16个PL2表项使用。在我们的多次测试期间，我们注意到，它们主要集中于几个彼此接近的数字。保守的攻击者可以总是选择更大的数字。在Intel Core和Xeon处理器以及Silvermont处理器上，我们发现cpuid报告的TLB的大小正好适用于完全刷新这些缓存，这很可能是因为用于缓存巨型页面的TLB也包含了缓存中间页面查询的逻辑。最后，我们发现，当Sandy Bridge和Ivy Bridge实现一个TLB来缓存1G页面时，cpuid指令不会报告这个TLB的存在，并且Nehalem和Westmere都实现了一个PL3页面结构缓存，但是没有提供这样的TLB实现。

**AMD**

在AMD的处理器上，LLC是独占型的，这意味着数据最多可以放入一个高速缓存中，以便可以一次存储更多的数据。为了能够正确驱逐缓存行，我们必须分配一个驱逐组，其大小等于高速缓存大小的总和。我们经测试发现，AMD K10微体系结构实现了AMD的页面查询缓存具有24个表项。此外，我们的测试表明，AMD的页面查询缓存没有被Bulldozer微体系结构的设计和该微体系结构的后代所采用。因此，AMD的Bulldozer架构似乎没有提供任何页表或转译缓存。

最后，AMD的Bobcat架构似乎实现了一个带有8到12个表项的页面目录缓存。

**ARMv7-A**

与Intel和AMD的处理器不同，根据片上系统的供应商的不同，有些ARM处理器上的L2缓存可以配置为包含型、独占型或非包含型。

然而，对于大多数ARMv7-A处理器来说，这些缓存都是配置为非包含型的。在ARMv7-A上，有两个页面级别可用，其中的页表分别提供256和4096个表项，分别可以映射4K和1M空间。对于支持大容量物理内存地址扩展（LPAE）的处理器，则使用三个页面级别，其中每个页表分别提供了512、512和4个表项，可以映射4K、1M和1G空间。即使最后一级页表仅由适合单个缓存行的四个表项组成，但是AnC攻击仍然可以应用于其他两个页面级别，以确定页表和转译缓存的存在性。此外，其低功耗版本（例如ARM Cortex A7）则实现了统一的页表缓存，而面向高性能的版本（例如ARM Cortex A15和A17）则实现了统一的转译缓存。但是，较旧的设计，如ARM Cortex A8和A9，却根本没有任何MMU缓存。同时，我们发现带有64个表项的页表缓存和带有16个表项的转译缓存分别可用于ARM Cortex A7和ARM Cortex A15。此外，我们的程序可以可靠地确定出所有支持和不支持LPAE的ARMv7-A的这些高速缓存的大小，即使在启用所有核心的ARM big.LITTLE处理器上，也可以透明地在不同类型的核心之间来回切换。

**ARMv8-A**

ARMv8-A处理器也实现了类似于Intel和AMD的包含型LLC。此外，ARMv8-A使用与x86_64类似的模型，提供了四个页面级别，每级512个表项。然而，在Linux系统上，仅使用了三个页面级别来提高页表查找的性能。与ARMv7-A类似，ARMv8-A在其低功耗版本（例如ARM Cortex A53）上实现了4路关联64项统一页表缓存，并在注重性能的版本，例如ARM Cortex A57， A72和A73中实现了一个统一的转译缓存。此外，我们还发现ARM Cortex A53实现了一个具有64个表项的页表缓存。

**讨论**

如代码清单2所示，我们可以通过分配与缓存项一样多的页面，然后“触动”每个页面级别中的每个页面来刷新TLB和页面结构。通过触动这些页面，MMU就会被迫执行虚拟地址转换以替换缓存中的现有的表项。此外，通过使用页面大小作为每个页面级别的步幅，我们可以利用巨型页面来刷新页面结构缓存或TLB。



```
1 /* Flush the TLBs and page structure caches. */
2 for (j = 0, level = fmt-&gt;levels; j &lt;= page_level; ++level, ++j)
3 {
4 p = cache-&gt;data + cache_line * cache-&gt;line_size;
5 6
for (i = 0; i &lt; level-&gt;ncache_entries; ++i) {
7 *p = 0x5A;
8 p += level-&gt;page_size;
9 }
10 }
```

代码清单2：刷新TLB和页面结构缓存。

<br>

**相关工作**



**针对页表的硬件攻击**

AnC攻击可以根据MMU将PTE缓存到LLC中的方式来发动EVICT + TIME攻击，从而利用JavaScript给用户空间ASLR去随机化。而使用预取指令的硬件攻击则依赖于缓存的TLB表项和部分转译来实现内核空间ASLR的去随机化。页表是Rowhammer攻击最有吸引力的目标。Drammer和Seaborn的硬件攻击会破坏PTE，使其指向页表页面。但是，如果不能正确刷新页表缓存的话，所有这些攻击都将失败。本文提供了一种用于在各种体系结构上刷新这些缓存的通用技术。

**逆向硬件**

针对商品化硬件的逆向工程已经随着对硬件的攻击的增加而变得日益流行。Hund等人对英特尔处理器如何将物理内存地址映射到LLC进行了逆向工程。Maurice 等人则使用性能计数器来简化了该映射功能的逆向过程。DRAMA则使用DRAM总线的被动探测以及对DRAM行缓冲器的定时攻击，对内存控制器将数据放置在DRAM模块上的原理进行了逆向工程。在本文中，我们对现有处理器的MMU中常见的页表缓存的各种未公开的特性进行了相应的逆向工程。



**结束语**

当前，基于硬件的攻击（如缓存或Rowhammer攻击）开始变得越来越流行，因为针对软件的攻击已经变得越来越具有挑战性。对于跨处理器的鲁棒性攻击方法来说，掌握各种处理器内缓存的相关特性是至关重要的。由于这些缓存通常对软件来说是不可见的，因此通常很难找到相关的文档说明。在本文中，我们改进了针对MMU的现有EVICT + TIME攻击，使其能够逆向最新处理器上常见的页表缓存的各种特性。我们将该技术应用于20个不同的微架构，发现其中17个实现了这样的页表缓存。我们的开源实现提供了一个便利的接口，可以用于在这16个微体系结构上刷新这些缓存，并可以在未来的微架构上自动检测页表缓存。更多信息，请访问： [https://www.vusec.net/projects/anc](https://www.vusec.net/projects/anc) 

<br>

**参考文献**

[1] M. Abadi, M. Budiu, U. Erlingsson, and J. Ligatti.Control-flow Integrity. CCS’05.

[2] T. W. Barr, A. L. Cox, and S. Rixner. Translation caching: skip, don’t walk (the page table). ISCA’10.

[3] A. Bhattacharjee. Large-reach memory management unit caches. MICRO’13.

[4] E. Bosman, K. Razavi, H. Bos, and C. Giuffrida.Dedup Est Machina: Memory Deduplication as an Advanced Exploitation Vector. SP’16.

[5] X. Chen, A. Slowinska, D. Andriesse, H. Bos, and C. Giuffrida. StackArmor: Comprehensive Protection From Stack-based Memory Error Vulnerabilities for Binaries. NDSS.

[6] D. Cock, Q. Ge, T. Murray, and G. Heiser. The Last Mile: An Empirical Study of Timing Channels on seL4. CCS’14.

[7] S. Crane, C. Liebchen, A. Homescu, L. Davi, P. Larsen, A.-R. Sadeghi, S. Brunthaler, and M. Franz. Readactor: Practical Code Randomization Resilient to Memory Disclosure. NDSS’15.

[8] T. H. Dang, P. Maniatis, and D. Wagner. The performance cost of shadow stacks and stack canaries. ASIA CCS’15.

[9] D. Evtyushkin, D. Ponomarev, and N. Abu-Ghazaleh.Jump Over ASLR: Attacking Branch Predictors to Bypass ASLR. MICRO’16. 

[10] C. Giuffrida, A. Kuijsten, and A. S. Tanenbaum.Enhanced Operating System Security Through Efficient and Fine-grained Address Space Randomization. SEC’12.

[11] B. Gras, K. Razavi, E. Bosman, H. Bos, and C. Giuffrida. ASLR on the Line: Practical Cache Attacks on the MMU. NDSS’17.

[12] D. Gruss, C. Maurice, A. Fogh, M. Lipp, and S. Mangard. Prefetch Side-Channel Attacks: Bypassing SMAP and Kernel ASLR. CCS’16.

[13] R. Hund, C. Willems, and T. Holz. Practical Timing Side Channel Attacks Against Kernel Space ASLR. SP’13.

[14] AMD64 Architecture Programmer’s Manual, Volume 2: System Programming. Publication No.: 24593, May 2013.

[15] Intel 64 and IA-32 Architectures Optimization Reference Manual. Order Number: 248966-032, January 2016.

[16] Y. Jang, S. Lee, and T. Kim. Breaking kernel address space layout randomization with intel tsx. CCS’16.

[17] K. Koning, H. Bos, and C. Giuffrida. Secure and Efficient Multi-Variant Execution Using Hardware-Assisted Process Virtualization. DSN’16.

[18] V. Kuznetsov, L. Szekeres, M. Payer, G. Candea, R. Sekar, and D. Song. Code-pointer integrity. OSDI’14.

[19] M. Lipp, D. Gruss, R. Spreitzer, C. Maurice, and S. Mangard. Armageddon: Cache attacks on mobile devices. SEC’16.

[20] K. Lu, C. Song, B. Lee, S. P. Chung, T. Kim, and W. Lee. ASLR-Guard: Stopping Address Space Leakage for Code Reuse Attacks. CCS’15.

[21] C. Maurice, N. L. Scouarnec, C. Neumann, O. Heen, and A. Francillon. Reverse Engineering Intel Last-Level Cache Complex Addressing Using Performance Counters. RAID’15.

[22] Y. Oren, V. P. Kemerlis, S. Sethumadhavan, and A. D. Keromytis. The Spy in the Sandbox: Practical Cache Attacks in JavaScript and their Implications. CCS’15.

[23] P. Pessl, D. Gruss, C. Maurice, M. Schwarz, and S. Mangard. DRAMA: Exploiting DRAM Addressing for Cross-CPU Attacks. SEC’16.

[24] K. Razavi, B. Gras, E. Bosman, B. Preneel,C. Giuffrida, and H. Bos. Flip Feng Shui: Hammering a Needle in the Software Stack. SEC’16.

[25] M. Seaborn. Exploiting the DRAM Rowhammer Bug to Gain Kernel Privileges. In Black Hat USA, BH-US’15.

[26] V. van der Veen, Y. Fratantonio, M. Lindorfer, D. Gruss, C. Maurice, G. Vigna, H. Bos, K. Razavi, and C. Giuffrida. Drammer: Deterministic Rowhammer Attacks on Mobile Platforms. CCS’16.

[27] Y. Yarom and K. Falkner. FLUSH+RELOAD: A High Resolution, Low Noise, L3 Cache Side-channel Attack. SEC’14.

[28] X. Zhang, Y. Xiao, and Y. Zhang. Return-Oriented Flush-Reload Side Channels on ARM and Their Implications for Android Devices. CCS’16. 
