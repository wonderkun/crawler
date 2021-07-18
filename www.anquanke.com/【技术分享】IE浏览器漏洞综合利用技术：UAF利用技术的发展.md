
# 【技术分享】IE浏览器漏洞综合利用技术：UAF利用技术的发展


                                阅读量   
                                **159066**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/85797/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](./img/85797/t0156774c66493b3aab.jpg)](./img/85797/t0156774c66493b3aab.jpg)**



作者：[Ox9A82](http://bobao.360.cn/member/contribute?uid=2676915949)

稿费：400RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

传送门

[【技术分享】IE浏览器漏洞综合利用技术：堆喷射技术](http://bobao.360.cn/learning/detail/3656.html)

<br>

**前言**

在前一部分中，我们介绍了从IE6到IE11的堆喷射方法，其实堆喷射只是一种手段目的还是为了实现最后的漏洞利用。在这一篇文章中，我们会根据时间顺序来讲解IE浏览器漏洞利用技术的发展，我们会把主要精力放在UAF漏洞的利用上面，同时会涉及一些其它类型的漏洞作为辅助以绕过漏洞缓解措施，这篇文章主要介绍技术发展脉络，实际的漏洞调试会放在下一章，期间我阅读了大量的文档、会议PPT和博客文章，在此也对前辈们的分享表示感谢。同时给大家分享两句我很喜欢的话，一句来自大家应该都很熟悉的陈皓大牛，一句来自charles petzold大家应该都有读过他的书

要了解技术就一定需要了解技术的历史发展和进化路线。因为，你要朝着球运动的轨迹去，而不是朝着球的位置去，要知道球的运动轨迹，你就需要知道它历史上是怎么跑的。

学习技术发展史的重要意义正在于此：追溯的历史越久远，技术的脉络就变得越清晰。因此，我们需要做的就是确定某些关键的历史阶段，在这些阶段，技术最天然、最本质的一面将清晰可见。

首先简单介绍一下本篇文章将要提到的漏洞类型，我们这篇文章主要会针对两类漏洞进行描述，即越界访问漏洞和释放后重引用漏洞。这两种漏洞的英文名称分别为Out-of-Bound和Use-After-Free，因此我们通常简称这类漏洞为OOB和UAF。

**1.越界访问漏洞**

越界访问漏洞，个人认为越界访问漏洞应该是按照漏洞造成的效果进行划分的，而不是依照漏洞成因进行的划分。我认为如果是从成因的分类上来讲，像堆溢出、整数溢出、类型混淆等都可以造成越界访问漏洞。

越界访问，所谓的访问就是指越界读和越界写，在后面我们可以看出越界漏洞是比较容易利用，也是比较好用的一类漏洞，这里好用指的是效果比较好，一般通过这种OOB漏洞可以在IE浏览器中轻易的实现绕过ASLR的保护。

而这种漏洞的利用，一个共通点是要进行内存布局（或称为Feng shui技术）。即把一些特殊的对象或者结构布置在漏洞对象附近，否则读写都无从谈起，我们会在后面展开来说这些内容。

**2.释放重引用漏洞**

Use-After-Free漏洞中文名为释放后重引用漏洞，这种漏洞估计大家都比较熟悉。

所谓的“释放重引用”是指在一块内存被释放后在某处还保存有指向这块内存的悬垂指针，之后对悬垂指针进行了解引用(所谓的重引用)导致了漏洞的触发。

我们分析UAF漏洞一般要搞清楚几个关键点：

1.是什么对象发生的UAF？

2.UAF对象何时被分配、何时被释放？

3.导致crash的流程是什么？

4.为什么会存在悬垂指针？

但是在早期的UAF漏洞利用来说，一些Hacker们往往只需要知道步骤2、3就可以实现漏洞利用。这是因为早期的UAF一般都是通过占位和堆喷射来进行利用的，比较简单粗暴。

<br>

**1.为什么IE中会存在大量的Use-After-Free漏洞？**

我们的第一个问题是IE浏览器中为什么会爆出大量的UAF漏洞？

这个问题的提出并不奇怪，因为其它的软件诸如Office Word的漏洞可能基本上都是一些堆栈溢出，而UAF则是凤毛麟角。

IE浏览器中并不是没有存在过栈溢出这些类型的漏洞，而是经过了十余年的发展基本都已消耗绝迹，但是UAF漏洞“络绎不绝”的本质原因在于IE浏览器中存在着大量的各种类型的对象和其间互相关联的关系，包括各种标签和各种内部数据结构比如CElement就是代表元素对象的父类，举例来看CButton是CElement的子类代表&lt;Button&gt;标签。

这些html标签和DOM Tree是由IE浏览器中的渲染引擎mshtml(就是所谓的Trident)负责解析的。html标签在mshtml内部就是由一个个的C++对象来进行表示的，同样DOM树也是通过一些数据结构来进行描述(比如CTreeNode、CTreePos)，这些对象之间存在复杂的相互关系。并且mshtml使用了引用计数的方法来跟踪对象的使用情况。

我们可以通过泄漏的IE5.5源代码来观察这一点，虽然IE5.5版本对于我们来说已经是相当的古老了，但是其实一些核心的部分还是相当相近的。

如下是IPrivateUnknown接口，这个接口在我们源码中存在着如下的继承关系CElement-&gt;CBase-&gt;IPrivateUnknown。



```
interface IPrivateUnknown
{
public:
    STDMETHOD(PrivateQueryInterface)(REFIID riid, void** ppv) = 0;
    STDMETHOD_(ULONG, PrivateAddRef)() = 0;
    STDMETHOD_(ULONG, PrivateRelease)() = 0;
};
```

在此我推荐阅读以下两篇文章，可以增进对IE浏览器的了解：

《IE安全系列：IE浏览器的技术变迁（上）》

[http://www.infoq.com/cn/articles/Internet-Explorer-Security1](http://www.infoq.com/cn/articles/Internet-Explorer-Security1) 

《IE安全系列：IE浏览器的技术变迁（下）》

[http://www.infoq.com/cn/articles/InternetExplorer-Security2](http://www.infoq.com/cn/articles/InternetExplorer-Security2) 

<br>

**2.如何利用IE中的Use-After-Free漏洞**

如何利用UAF漏洞是我们这篇文章的主题，在分门别类的进行讨论之前，我们首先介绍一些基础知识。我们在前面介绍了UAF漏洞的一些信息，对于UAF漏洞的利用无论在什么时期，一个通用的步骤就是在UAF对象被释放之后马上去分配一个相同大小的内存块，我们称这一步操作为“占位”。占位的原理在于堆分配的机制，当一块堆内存被释放后出于效率的考虑会被保存在一些结构中以便于再次的分配。占位就是利用这一点，通过分配相同大小的堆内存试图重用UAF对象的内存，对Linux堆有了解或是打过CTF的同学应该都比较熟悉这一点了。为了成功实现占位，一般是多次分配相同大小的内存以保证成功率。

需要说明的一点是，不是所有的UAF漏洞都是可以利用的，因为一些漏洞无法进行占位。比如有的漏洞它的对象释放和重用操作就在同一个函数中，刚刚释放完马上就重用了，这种情况根本没有机会去进行占位，从而无法进行利用。

我们说了这么久的占位，其实占位的目的是为了控制对象的内容。同样目的的操作，还有挖坑法(make hole)，挖坑法是指在布局好的内存中释放一个指定大小的块，好让目的对象落在我们布局的内存中，我们会在后文提到这一点。还有内存未初始化漏洞的利用也与之类似，内存未初始化漏洞是指分配一块内存后未经初始化就直接进行使用，我们为了控制未初始化对象的内容会先释放一些与之相同大小的已布置好内容的内存，然后让未初始化对象来重用我们的内存。

接下来我们就根据历史发展来讨论利用技术，可以看出随着历史的向前漏洞利用技术有了很大的发展，相比早期的利用技术现在无论是在思路还是在手法上都是发生了质的飞跃。

<br>

**3.IE6漏洞利用(史前时代)**

我们把IE6作为IE漏洞利用的开端，我们称之为史前时代，说到史前我们可能会想到刀耕火种、茹毛饮血。此时的IE漏洞就是处于这样一个野蛮生长的时代，漏洞利用技术简单粗暴导致网马大量横行。主要原因在于IE6时代的浏览器版本不支持DEP等漏洞缓解措施(虽然此时操作系统已经支持DEP)，导致漏洞利用的成本低廉，但是也因此流传下来一些“远古神话”，比如经典的0x0C0C0C0C。

这一时期由于Active X插件作者的水平参差不齐，因此大量的控件存在有诸如栈溢出之类的简单漏洞，利用方式也极为简单粗暴配合堆喷就可以实现利用，这些漏洞我们简单略过不再详述。

我们把关注重点放到此时的UAF漏洞上面，通过我们前面对UAF漏洞的简单介绍就可以看出，UAF漏洞与栈溢出有着本质不同。栈溢出可以简单直接的控制返回地址从而劫持执行流程，但是UAF往往是处于堆上并没有直接劫持流程的途径。为了能够在堆上劫持指令执行流程，前辈们想出了劫持虚函数调用的方法。

我们首先简单介绍一下虚函数，在C++程序中，如果一个类存在虚函数那么当这个类实例化对象后，对象的前4个字节就是虚函数表的指针，当我们调用虚函数时实际上是到虚函数表中寻找函数指针。接下来，我们就通过这一点来进行利用。

我们首先通过占位来控制UAF对象的内容(如果你不理解这一步，可以往前看一看)，控制了对象的内容就相当于控制了虚函数表的指针。接下来我们需要一个稳定可达的地址，因此我们使用上一篇文章讲过的堆喷射，然后把虚表指针指向我们喷射的内存地址，这样一旦触发漏洞就会把我们的喷射内存当作虚表来执行了。

为什么一触发漏洞就会把喷射内存当作虚表来执行呢？如果没有调试过IE漏洞可能会提出这个问题，因为我们实际去调试漏洞就会发现事实上UAF漏洞触发后基本都会crash在虚函数调用处，如果你发现windbg停在一个莫名其妙的地方很可能是因为没有开启页堆，可以使用!gflags.exe -i +hpa进行开启，关于页堆可以学习一下张银奎老师的《软件调试》。(此外新手可能会发现明明异常了却没有停下来，可能是没开启子进程调试，主要是对于IE8以后这种多进程浏览器来说。)

根据我们上面的描述可以看出，我们是在把喷射的内存当成虚表。但是当我们调用虚函数时，往往是下面这个样子的：



```
mov eax,[ecx]
call [eax+4]
```

这两条指令意味着，喷射的内存不仅会被当成虚表还会被当成指令来执行。并且更糟糕的情况是：这里我们不能确定堆喷射的准确分配地址，就是说我们不能确定堆表指针到底喷射在哪里。这时就对我们的喷射提出了要求，我们需要寻找一个既可当作地址解释又可以当作无意义指令解释的值。

在这种情况下“上古传说"0x0C0C0C0C就诞生了，如果我们使用0x0C0C0C0C作为喷射的内容的话，当mov eax,[ecx]时就会取到0x0C0C0C0C作为指针来进行跳转，call [eax+4]会把0x0C0C0C0C的0x4处偏移取出并call，当然其结果依然为0x0C0C0C0C，这样call 0x0C0C0C0C会执行指令0x0C，而0x0C相当于nop就会最终执行到shellcode了。当年有很多这样的通用地址存在比如0x0D0D0D0D、0x06060606。

这种利用方式简单粗暴却又有效，因此我们称为史前时代，就像TK教主说的一样：

在当年无 DEP 的环境下，几乎完全不懂漏洞原理的人，知道去 Heap Spary 0x0C0C0C0C 就能搭积木一样写出 Exploit，而且还很通用。

当然，对于不涉及虚表访问的利用来说，使用0x0c0c0c0c是完全没有意义的。不过这个地址已经成为一个"上古神话"了，所以我们还是会经常看得到它，甚至于一些安全软件一旦发现这个值就会报警。

[![](./img/85797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c51dce9c8fac61f1.png)

<br>

**4.IE8早期漏洞利用(石器时代)**

前面我们说IE6时期是史前时期，因为那时的漏洞利用简单粗暴。相比于当时，IE8时代的利用技术向前走了一大步，不过因为安全体系的问题早期的IE8利用依然只能称为是石器时代，还是相当的原始。

自IE8开始，DEP和ASLR成为浏览器中默认启用的缓解措施，如何bypass ASLR和DEP成为了攻击者首要面对的问题。我们简单介绍一下DEP和ASLR，如果是熟悉Linux的同学，那么Linux下的NX保护与DEP是很类似的，都是把一些非代码段内存设为不可执行来阻止攻击者运行shellcode。在其它的软件中bypass DEP通常使用ROP技术，但是由于IE几乎都是基于堆的漏洞不存在直接进行ROP的条件所以并不能通过简单的ROP实现bypass DEP。而ASLR会使得模块装载的地址变得不确定，对漏洞利用有一些了解的同学肯定知道Rop技术是依赖于一些rop gadgets来进行不断的跳转利用的，ASLR的启用会直接妨碍我们获取rop gadgets。

不过对于早期的利用，ASLR并没有对利用者造成太大的困扰。因为ASLR早就在诸如Office Word之类的软件中启用了，Hacker们直接套用了在这些软件中的做法即利用一些未开启ASLR的模块进行利用。因为当时很多的模块并不支持ASLR因此加载在固定基地址。这种方法也是比较简单粗暴的而且通用性比较差，比如以前在IE中常用的Java6的msvcr71.dll，如果目标并没有安装JRE或者版本不对利用都不能成功。

因为此时仍然比较原始，所以我们称之为石器时代。事实上，今天的应用程序不支持ASLR的已经非常少见了，想通过不支持ASLR的模块来实现ROP已经不大可能了。所以我们把完整的利用方法放到下一章中详述。

<br>

**5.IE8浏览器结合信息泄漏利用(铁器时代)**

据说人类跟动物的区别是人类会使用工具，那么这一时期利用技术的进步堪比从石器进化到铁器。

这一时期的标志事件是Peter Vreugdenhil在Pwn2Own2010中攻破IE8项目，这一过程中的技术手段对后来的利用技术发展有着重要的作用。Peter Vreugdenhil利用IE8的手段是把一个OOB漏洞与一个UAF漏洞相互结合，我们首先来说OOB漏洞。Peter Vreugdenhil通过内存布局把BSTR布置在存在OOB的对象后面，目的是进行信息泄漏，通过越界写来改变BSTR的长度，实现了越界读。

我们在前面说过BSTR不是简单的Unicode字符串，BSTR的结构由4字节的长度（size）域、2字节的结束符（x00x00）加上Unicode字符串构成。通过我们精心构造内存布局，使BSTR对象紧随漏洞对象的后面。之后再在BSTR后面再放置目标对象，这样当触发漏洞对象发生越界访问的时候就可以覆盖掉BSTR结构的size域。一旦我们把size域覆盖为更大的数值，我们就能够使得BSTR发生越界读(因为BSTR只可读不可写)。然后通过js脚本读取BSTR字符串，就能够读到BSTR之后的对象。我们的目的是获取后面对象的虚表地址（首4个字节）。如果你想了解的更详细可以参见([http://vreugdenhilresearch.nl/Pwn2Own-2010-Windows7-InternetExplorer8.pdf](http://vreugdenhilresearch.nl/Pwn2Own-2010-Windows7-InternetExplorer8.pdf) )

为什么获得虚表地址就可以bypass ASLR呢？因为对于C++程序来说虚函数表是被编译在全局数据段的，就是说对于模块的基地址的偏移是固定的。我们通过泄漏的虚函数表的地址减去偏移就可以知道对象所处的dll模块的基地址，也就可以使用这个模块中的gadgets了。

这种方法有两个需要解决的问题：第一是如何构造稳定的内存布局使我们上述的内容得以实现。第二是当我们覆盖成功后，如何通过javascript脚本层面上的操作把值获取到。其实我们后面要讲到的方法都面临着这两个问题。

由于这种利用较为简单，可以直接参考泉哥的著作《漏洞战争：软件漏洞分析精要》里面第三章的CVE-2012-1876的利用分析，其使用的方法就是通过BSTR进行泄漏，我们也会在下一篇中给出实际的漏洞调试。

单单绕过ASLR是无法实现漏洞利用的，因为DEP的存在我们没有办法在堆上执行指令。为此Hacker们想了很多办法，其中我认为最早实现成功利用的依然是Pwn2Own 2010上Peter Vreugdenhil使用的方法，虽然与我们这里讲的不完全相同，但是我觉得是Peter Vreugdenhil方法的进化版。我们忽略Peter Vreugdenhil的方法(感兴趣的可以查看上面的连接)，我们使用的手段是stack pivot，所谓stack pivot就是通过mov esp,eax、xchg esp eax等指令来实现把栈转移到堆上，因为一般的UAF漏洞触发时我们都可以控制至少一个寄存器的值。通过把esp指向我们喷射的内存，我们就可以把堆伪造成栈，从而像普通的栈溢出一样进行ROP，通过执行ROP最终实现代码执行。

但是这一利用方法首先要确保的是我们要能够精准的计算堆喷射的地址，因为堆不可执行所以我们不能再依赖于用于缓冲的nop指令了。好消息是我们在前一篇文章中已经讲过准确计算的原理和实现了，这里再简单复述一下。当我们大量分配堆块时可以发现地址的最低几位是一直不变的，地址改变的熵只是固定的地址高位并且堆块的分配相当的稳定。这样如果我们使偏移都落在地址的高位，那么我们的指向就会是整块进行偏移，从而保证了每次指向的都是计算好的准确的地址。

举个例子：我们可以以每个块为单位计算出ROP链第一条地址的偏移，然后其实我们可以想一下0x0C0C0C0C这个地址还有没有用？在这种利用环境下，第一不需要跳板指令，第二我们跳转目的地址是精确的，那么0x0C0C0C0C这种地址就根本没有存在的价值了。我们要的就只是一个堆喷射可达的稳定的地址。

无堆喷射，通过ANIMATECOLOR对象实现利用

这种方法不需要进行堆喷射就可以实现利用，堆喷射其实并不能说是一种优雅的利用方法，因为分配内存需要一定的时间，而且如果目标机器的配置较低的话可能会导致卡顿从而被目标察觉。我之前在binvul上看到过一些所谓的“不弹不卡不喷射不风水”的样本其实指的就是这种技术。

ANIMATECOLOR是IE8版本起提供的一种对象，由于这种对象的特殊构造所以可以不使用堆喷射来实现利用，我们在下一篇实际漏洞调试时再来进行分析。

<br>

**6.结合Flash的利用(中世纪)**

到这里浏览器利用技术又是一个飞跃，结合flash利用虽然不能说特别优雅(因为要依靠第三方)，但中世纪是文艺复兴的先声，可以说自此之后利用技术又进入了一个发展的新巅峰。

这种利用技术不是来自于Pwn2Own也不是来自于某次会议的分享，相反，随着时间的发展，在2013年网上流传出了一些无需多漏洞结合使用，通过单一漏洞就可以bypass缓解措施+执行代码的exp样本，这些exp样本应该是用于实际攻击的武器。其主要特点是结合了flash进行漏洞利用，这种利用技术最早应该是由李海飞前辈在《Smashing the Heap with Vector:Advanced Exploitation Technique in Recent Flash Zero-day Attack》这文章中提出的(CVE-2013-0634)。

```
This is in fact a somehow new technique which leverages the custom heap management on Flash Player to gain highly-reliable exploitation bypassing both the ASLR and DEP.
```

就像李海飞前辈所说，这完全是一种新技术。并且这种新技术可以只凭借一个单一的漏洞实现bypass全部的缓解措施并且执行最终的shellcode，这一点是以前的exploit所做不到的事情。

我们简单的概括一下利用的方法，我们先忽略漏洞的细节简单的认为它是一个0x90个字节的堆块发生的溢出。我们首先分配一系列0x90大小的Vector对象，对于储存数字的Vector来说每个数字占8个字节，16个数字加上16字节的固定结构正好满足0x90的大小。

[![](./img/85797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010c813fc1b5a571b0.png)

我们在vector对象布置完成之后，通过代码来释放一些0x90大小的vector，再触发漏洞。之后会分配具有溢出的0x90大小的堆块，因为尺寸与我们之前释放的vector尺寸相同，根据堆的特性漏洞堆块会重用我们之前释放的vector对象内存。这一步操作称为挖坑（make holes），挖坑的目的是为了使得漏洞堆块处于vector对象的包围之中。

[![](./img/85797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0103fccc1f7c932652.png)

[![](./img/85797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012fdcf7bc159c43e8.png)

下一步，我们只需要利用溢出就可以覆盖掉相邻vector对象的“Number_of_elements”域。

覆盖的结果是使得相邻的vector可以发生越界访问，通过操作这个越界的vector我们又可以覆盖下一个vector的“Number_of_elements”域，但这次我们可以直接把“Number_of_elements”域改的很大，从而实现了整个进程地址空间的任意读写。

[![](./img/85797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e4e81070d2fe0781.png)

[![](./img/85797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01866c3fe2d80add57.png)

一旦实现了整个内存空间的进程读写，就可以做到bypass DEP和ASLR了。

如果说这次利用只是因为漏洞本身有比较合适的尺寸便于布局、有直接的溢出便于覆盖结构。那么陈小波前辈发布的《ASLR Bypass Apocalypse in Recent Zero-Day Exploits》中就给出了一个通用的思路，其中提到了很重要的一点就是：如何把一个常规的UAF漏洞往我们上面说的Flash vector越界写上面进行转化。对于这个问题作者提供了如下的思路：以CVE-2013-0634为例，这是一个在IE浏览器中常见的UAF漏洞，在利用这个漏洞时exp作者在代码执行路径上发现了一条指令：

```
or dword ptr [esi+8],20000h
```

其中esi的值是我们可控的(来自UAF对象，可以通过占位进行控制)，作者把它指向布置好了的Vector对象的长度域，在执行了or之后长度域会变大从而使得这个vector可以进行越界操作。之后可以通过这个vector越界写紧邻的下一个vector的长度域从而实现了整个进程地址空间的任意读写。此外还要解释一下为什么可以知道Vector对象的长度域的地址，

之后的IE浏览器利用从基本思想上发生了转变，攻击者不再追求结合多个漏洞泄漏信息再进行堆上ROP，而是继承了flash vector的任意读写转化思路，试图从UAF转化到任意地址读写，再通过任意地址读写来实现绕过缓解措施。

<br>

**7.UAF转化与Element Attribute(启蒙时代) **

之后漏洞利用进入启蒙时代，相比flash利用这一时期的优点是不再依赖于flash模块。这样可以提高漏洞利用的成功率和降低成本，因为此时一个漏洞就可以实现多个漏洞的利用效果并且在flash利用爆发后安全软件对夹杂flash的页面十分敏感，不依赖flash可以提高漏洞利用的成功率。

在《A BROWSER IS ONLY AS STRONG AS ITS WEAKEST BYTE》这篇文章中，作者以CVE-2013-3147为基础详细讲解了如何从crash地点进行分析来寻找一条合适的代码路径把UAF转化成inc [address]（绝对地址加），并且避开虚函数调用以免引发crash。简单的概括就是查找crash附近的代码流程，寻找有没有写原语，如果存在这样的原语就想办法满足逻辑条件把执行流程引导写原语上去。

值得注意的是作者在利用这个任意地址加的过程中并没有依靠flash vector，而是通过喷射Element Attribute来实现利用。首先简单介绍一下Attribute是什么，如果你有看过HTML那么应该知道一些标签是具有属性的，比如每个标签都有id属性用做唯一的标识。对应于底层实现来说，每个DOM元素对应的CElement结构中也会有指针指向Attribute Array，每个属性占其中一项。那么Element Attribute是如何实现利用的呢？

首先我们忽略漏洞的细节，只看漏洞导致的效果，经过转化操作这个UAF漏洞可以引导到如下的路径上

```
inc     dword ptr [esi+0A0h]
```

其中esi寄存器的值我们可以直接控制，因此这个漏洞相当于一个任意地址加1的效果。

接下来我们要来看下Element Attribute的结构，这就是我们前面所说的Attribute Array中的一项。



```
dword flag
dword Name_hex
dword ptr or value
dword ptr or value
```

其中flag代表这个属性类型，作者总结了一下这些可选值



```
VT_EMPTY = 0x0000,
VT_NULL = 0x0001,
VT_I2 = 0x0002,
VT_I4 = 0x0003,
VT_R4 = 0x0004,
VT_R8 = 0x0005,
VT_CY = 0x0006,
VT_DATE = 0x0007,
VT_BSTR = 0x0008,
VT_DISPATCH = 0x0009,
VT_ERROR = 0x000A,
VT_BOOL = 0x000B,
VT_VARIANT = 0x000C,
VT_UNKNOWN = 0x000D,
VT_DECIMAL = 0x000E,
VT_I1 = 0x0010,
VT_UI1 = 0x0011,
VT_UI2 = 0x0012,
VT_UI4 = 0x0013,
VT_I8 = 0x0014,
VT_UI8 = 0x0015,
VT_INT = 0x0016,
VT_UINT = 0x0017,
VT_VOID = 0x0018,
VT_HRESULT = 0x0019,
VT_PTR = 0x001A,
VT_SAFEARRAY = 0x001B,
VT_CARRAY = 0x001C,
VT_USERDEFINED = 0x001D,
VT_LPSTR = 0x001E,
VT_LPWSTR = 0x001F,
VT_RECORD = 0x0024,
VT_INT_PTR = 0x0025,
VT_UINT_PTR = 0x0026,
VT_ARRAY = 0x2000,
VT_BYREF = 0x4000
```

而第二个DWORD的值为属性名的哈希值，第三和第四个值为实际的属性内容，如果属性内容是诸如字符串这样的值，那么它会是一个指针。

作者的核心思路是对第三个DWORD那个指针进行加1操作，因为是以字节为单位进行加1，所以实际的操作效果可能是指针偏移0x1、0x100、0x10000、0x1000000。在这种思路之下作者进行了内存布局，通过构造相同大小的BSTR字符串和一个元素来使得它们彼此相邻的分配(相同大小通过计算可以轻易的得到，而且也正是因为它们大小相同所以才会发生彼此相邻的分配)，在布局完成之后对指针进行加1操作就可以读出后面元素的内容，在实际利用过程中布局要更加复杂一些不过原理是一致的。

实际利用过程中作者一次性创建了含有0x7FFE个属性的元素，然后复制它直到大小为0x800000个字节。然后对这些元素进行遍历，每隔0x1000个属性就把它的值设置为一个0x8A大小的字符串，这个设置会导致在内存中分配0x8A字节的字符串，然后马上创建一个body元素并添加9个默认属性(大小正好是0x8A)这样就做到了BSTR和元素的紧邻分配。接下来就像我们上面所说的对指针加1就能读到body元素的内容了。因为body默认属性中包含一些域，通过读取它就可以算出mshtml.dll的基地址。

然后作者在这个基础上继续进行改进，因为作者认为mshtml.dll的版本变化比较多对于利用不是很理想，而且现在我们做的还只是泄漏操作没有实际的进行执行流劫持，而我们这一阶段的主题就是只通过单个漏洞来实现完整的利用。作者为了实现流程控制对属性表进行了覆盖操作，但是又会受到低碎片堆机制的限制，为此又要伪造堆头结构。可见这种利用方法还是比较麻烦的，但是对Element Attribute结构的利用思路对后来的漏洞利用思路有很大的帮助。

之后在2014年，这个时候Ivan Fratric的《Exploiting Internet Explorer 11 64-bit on Windows 8.1 Preview》发布出来。这篇文章的意义在于，作者针对javascript array对象进行了分析，然后对array对象进行Feng shui布局并且通过它的capacity域实现了利用。由于js引擎是根据capacity域对数组大小进行判断的，因此我们一旦篡改了capacity域就可以对数组进行越界访问。在下一阶段的利用中，我们就会看到array object在漏洞利用中起到的作用。

此外在2015年的Pwn2Own上，360 vulcan团队就是通过Element Attribute对IE11浏览器进行的利用。不过与我们这里的情形不同，vulcan利用的漏洞恰好就是在处理Element Attribute时出现的未初始化问题，由于与文章主题无关这里就不赘述了，不过相信读完本文之后你就可以理解古河讲的利用思路了，利用的详情可以查看http://www.ichunqiu.com/course/52149。

<br>

**8.IE11与针对jscript9引擎的攻击(近现代)**

CanSecWest2014上，ga1ois在议题《The Art of Leaks》中讨论了几个很关键的问题。

第一是自IE9以后引入的jscript9引擎——jscript9.dll使用与以前不同的custom heap，而且这个custom heap并没有做任何的分配随机化措施，这一点给我们进行内存布局提供了可能。

第二是从UAF转化为任意地址读写的过程中可能因为虚表访问而导致crash和如何避免发生这种crash。

在IE9之前的版本中，javascript是由javascript解析引擎——jscript.dll负责解析的，这个dll在分配内存时使用的是系统的进程堆。而在最新的javascript解析引擎——jscript9.dll中，在分配一些对象时引擎会使用custom heap，这个custom heap是由jscript9自己负责管理和维护的。并且这个custom heap在分配时没有进行随机化处理，以至于攻击者可以通过布局一些对象（所谓的feng shui技术）来预估出对象所处的地址。

[![](./img/85797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0135af14075a02ddf1.png)

其中直到0xf000之前的都是我们的array object填充数据，而自0xf000起是我们想要的目标对象，这里以int32Array作为目标对象的例子。

因为后续我们还会涉及到int32Array这个对象，所以我们这里详细的介绍一下。int32Array属于Typed array的一种，根据MDN的介绍Typed array有以下几种

[![](./img/85797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01952dca14d4ee5547.png)

我们知道javascript是一种脚本语言，是难以像C语言一样表示一些底层数据类型的，Typed array的设计就是为了解决这个问题。我们虽然可以直接使用new来创建一个Typed array对象，诸如

```
new Int32Array(32);
```

但是还有一种特有的用法如下：



```
var a= new ArrayBuffer(8);  
var b= new Uint8Array(a);
```

这与Typed array的底层结构是息息相关的，其结构分为解释数据类型的视图对象和实际储存数据的缓冲区对象。



```
Struct Int32Array     allocated at Custom Heap
{
    void* pvftable;
    DOWRD var_2;
    DOWRD var_3;
    DOWRD var_4;
    DOWRD var_5;
    DOWRD var_6;
    DOWRD size;            //条目的个数，字节数等于这项的值*4
    void* pTypeArrayData;     //Arraybuffer Data
    void* pArrayBuffer;   //Arraybuffer Object
    DWORD var_10;
    DWORD var_11;
    DWORD var_12;
}
Struct ArrayBuffer      allocated at Custom Heap
{
    void* pvftable;
    DOWRD var_2;
    DOWRD var_3;
    DOWRD var_4;
    void* pTypeArrayData;       //Arraybuffer Data
    DWORD size;                 //array bytes
    DWORD var_10;
    DWORD var_11;
}
```

其中Arraybuffer Data就是直接保存数据的区域，并且这块内存是分配在process Heap上的。

一旦可以预估出对象的地址那么就可以通过把UAF转化为绝对地址写去篡改Int32Array对象的长度域，来实现Arraybuffer Data的越界读写。因为Arraybuffer Data是储存在process Heap中的因此需要一个分配在process Heap上的对象来配合利用。这里作者使用的是LargeHeapBlock，因为这个对象处于process Heap中，并且恰好存在合适的域来实现任意地址读写。我们可以看出这种利用jscript9的方法明显比之前的做法要更稳定和易于操作。

至于UAF到读写的转化，与我们前面提过的大体相同就是跟踪漏洞触发附近的执行流程寻找有没有合适的转化原语(opcode)。在转化过程中可能会导致crash的问题，成功利用写入原语之后会发生虚函数调用，如果虚表被破坏的话虚函数调用就会导致crash。对此ga1ois给出了解决方案：

[![](./img/85797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a2fcb3028b7e7348.png)

之后，在同年的Hitcon上exp-sky进一步发展了这一技术，代码和文档可以在作者github中找到(https://github.com/exp-sky)。与ga1ois的不同之处在于exp-sky没有使用typed array进行布局，而是将IntArray Object作为目标对象进行布局。这一操作的优点在于IntArray全部都是基于custom heap进行操作的，如果你还记得我们上面讲的内容的话，你应该知道我们在对typed array进行篡改操作后进行越界编辑的是Arraybuffer Data，而这块内存是存放于process heap中的，这就意味着我们还要进一步的对process heap进行布局，而这种方法则完全没有这个必要。



```
Struct Array_Head 
{ 
    void * p_viable; 
    DOWRD var_2; 
    DOWRD var_3; 
    DOWRD var_4; 
    DOWRD size; 
    DOWRD p_first_buffer; 
    DOWRD p_last_buffer; 
    DOWRD var_8; 
    DOWRD var_9; 
    DOWRD var_10; 
}
Struct ArrayBuffer 
{ 
    DWORD var_11; 
    DWORD size; 
    DWORD buffer_size; 
    DWORD next_buffer; 
    DWORD data[buffer_size]; //data 
}
```

注意这两个结构都处于Custom Heap并且是分配在一起的。

因此喷射IntArray相比前面的方法要更方便也更容易控制，由于ArrayBuffer对象存在有保存当前缓冲区大小的域(buffer_size)，只要通过绝对地址写改写这个域为很大就可以转化为任意内存读写了，之后再修改相邻块的域这一点与前面的技术是相同的。

总体来说，这一时期的利用思路基本都在于喷射一些关键的对象，并结合各种feng shui技术（尤其是jscript9中的）进行布局。然后试图把UAF转化为绝对地址写，来写我们喷射对象的关键域从而实现从UAF到任意地址读写的跨越。

一旦获得了任意地址读写就相当于可以让攻击者进行随意利用，这时各种漏洞缓解措施就不再能够阻挡攻击者的脚步了。

这里我使用了一张demi6od在《Smashing the Browser》议题中使用的图，这张图很好的说明了我们所讲的思路。

[![](./img/85797/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c1aff6cc9c269992.png)

<br>

**后记**

其实这一系列的文章，我在去年10月份的时候就已经写完了，但是一直在硬盘里放了近半年都没有投出来。我主要是考虑到这系列文章涉及的话题太广、内容太多、历史又太悠久，考虑到自己仅是个大二学生水平较低、接触漏洞方面也不久，唯恐内容中出现错误和纰漏。但是做了一番修改后我还是鼓起勇气发出来了，希望大家能够帮忙修正文章中错误和提出修改建议，可以通过微博私信给我 id:Ox9A82。

<br>

**Reference**

《The Art of Leaks – The Return of Heap Feng Shui》Gaois

[https://cansecwest.com/slides/2014/The%20Art%20of%20Leaks%20‐%20read%20version% 20‐%20Yoyo.pdf](https://cansecwest.com/slides/2014/The%20Art%20of%20Leaks%20%E2%80%90%20read%20version%%2020%E2%80%90%20Yoyo.pdf)     

《IE 11 0day &amp; Windows 8.1 Exploit》exp-sky

《Smashing the Browser》demi6od

《浏览器漏洞攻防对抗的艺术》仙果

[http://bbs.pediy.com/thread-211277.htm](http://bbs.pediy.com/thread-211277.htm) 

《Exploiting Internet Explorer11 64-bit on Windows 8.1 Preview》

[http://ifsec.blogspot.com/2013/11/exploiting-internet-explorer-11-64-bit.html](http://ifsec.blogspot.com/2013/11/exploiting-internet-explorer-11-64-bit.html) 

《ASLR BYPASS APOCALYPSE IN RECENT ZERO-DAY EXPLOITS》

[https://www.fireeye.com/blog/threat-research/2013/10/aslr-bypass-apocalypse-in-lately-zero-day-exploits.html](https://www.fireeye.com/blog/threat-research/2013/10/aslr-bypass-apocalypse-in-lately-zero-day-exploits.html) 

《A BROWSER IS ONLY AS STRONG AS ITS WEAKEST BYTE》

[http://blog.exodusintel.com/2013/11/26/browser-weakest-byte/](http://blog.exodusintel.com/2013/11/26/browser-weakest-byte/) 

《A browser is only as strong as its weakest byte – Part 2》

[https://blog.exodusintel.com/2013/12/09/a-browser-is-only-as-strong-as-its-weakest-byte-part-2/](https://blog.exodusintel.com/2013/12/09/a-browser-is-only-as-strong-as-its-weakest-byte-part-2/) 

《Smashing the Heap with Vector:Advanced Exploitation Technique in Recent Flash Zero-day Attack》

[https://sites.google.com/site/zerodayresearch/smashing_the_heap_with_vector_Li.pdf?attredirects=0](https://sites.google.com/site/zerodayresearch/smashing_the_heap_with_vector_Li.pdf?attredirects=0) 

《IE安全系列：IE浏览器的技术变迁（上）》

[http://www.infoq.com/cn/articles/Internet-Explorer-Security1](http://www.infoq.com/cn/articles/Internet-Explorer-Security1) 

《IE安全系列：IE浏览器的技术变迁（下）》

[http://www.infoq.com/cn/articles/InternetExplorer-Security2](http://www.infoq.com/cn/articles/InternetExplorer-Security2) 

《攻破Windows 8.1的64位IE – 分享Pwn2Own黑客大赛成果》

《Pwn2Own 2010 Windows 7 Internet Explorer 8 exploit》

[http://vreugdenhilresearch.nl/Pwn2Own-2010-Windows7-InternetExplorer8.pdf](http://vreugdenhilresearch.nl/Pwn2Own-2010-Windows7-InternetExplorer8.pdf) 

《Flash Vector漏洞利用的蜕变》

[http://www.cnetsec.com/article/14571.html](http://www.cnetsec.com/article/14571.html) 

《Array Object Heap Spraying》

[http://www.cnblogs.com/wal613/p/3958692.html](http://www.cnblogs.com/wal613/p/3958692.html) 

<br>



传送门

[【技术分享】IE浏览器漏洞综合利用技术：堆喷射技术](http://bobao.360.cn/learning/detail/3656.html)

<br>
