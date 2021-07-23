> 原文链接: https://www.anquanke.com//post/id/230449 


# 从CPU到内核/到用户态全景分析异常分发机制——内核接管[1]


                                阅读量   
                                **180676**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01fd8b5a3784db1246.jpg)](https://p4.ssl.qhimg.com/t01fd8b5a3784db1246.jpg)



## 0、引言

继前一篇《从CPU到内核/到用户态全景分析异常分发机制——硬件基础及Hook》讲完硬件部分的内容之后，现在来看看OS如何和CPU“相亲相爱”合谋完成这一伟大壮举的。别高兴太早，这才是软件层面着手开始处理的万里长城第一步。好在第一步还是迈出去了，本篇将详细分析OS如何接管，如何管理异常的。注意我们这里分析的是基于Win10 16299版本，IA64架构的CPU。

整个系列涉及到的知识：

0、内核栈与用户栈隔离机制；

1、权限切换时，栈顶位置提供方式【有点拗口。。。】

2、CPU异常与中断概念与区别；

3、Intel架构中的IDT表与ISR；

4、Windows内核中内核异常分发；

5、Windows内核中用户态异常分发；

6、在调试器里查看PIC中断和APIC中断；

7、KPCR,KPRCB,KTRAP_FRAME；

## 1、简析硬件基础——IDT表及表结构——在内核调试器中手动解析之

### 1.1 IDT表结构分析

异常是谁先发现的？【注意，此处说的是异常不是中断，中断和异常最好当作两个不同的对象处理，是有本质区别的】当然是CPU，以断点为例子简单说明其过程。CPU内部的取指单元从总线中取到下一条将要执行的指令，交友译码单元进行译码，然后交给EU单元即执行单元进行执行，EU单元一看，喔嚯，是0xcc，这是个断点异常啊，赶紧的，把这个情况给OS报告下？咋报告？当然是用软硬件协商好的IDT表了，先看下intel cpu定义的这张表，

[![](https://p4.ssl.qhimg.com/t0125ed272b97a905f3.png)](https://p4.ssl.qhimg.com/t0125ed272b97a905f3.png)

三号异常被安排的妥妥的，是Breakpoint，Type也是Trap，Trap的意思就是“明知山有虎，偏往虎山行”。Source是int 3指令，所谓的源就是cpu可能通过什么方式触发其进入到这里。看到这么个简单的表应该还不满足，还应该看看这个表的每个表项的”结构“，其实很多逆向啊，破解啊之类的事情都是在分析结构，具体讲就是分析处哪些字段，各自什么意思。IDT表的表项如下：

[![](https://p1.ssl.qhimg.com/t01187fd3201bd22993.png)](https://p1.ssl.qhimg.com/t01187fd3201bd22993.png)

着重看下Trap Gate门描述符，简单说明下各个字段的含义，

1、Offset31:16+Offset15:0 共计32bit位，组成了一个4Byte的指针，这个4Byte的指针指向的正是OS里边负责接管的具体的异常处理函数。

2、DPL描述了可以访问该描述符的最低权限，比较肯定会涉及到两方，DPL是以防，那另一方呢？大家可还记得CS段选择子的最后两个bit位，他们称之为CPL，即当前权限级别，指的就是当前CPU的权限级别，2个bit位共计四种权限状态，就是所谓的Ring0，Ring1，Ring2，Ring3。然Windows和Linux亦或其他各种OS都只使用了两个Ring。Intel想象很美好，现实就是这么骨干。不买账。

3、P表明当前这个段是否存在，段不存在是啥意思呢？有一种情况是该IDT表被倒到硬盘上去了。

4、D这个bit位表明的是当前的段大小，32位或者16位，这也就解释了为啥32位的Fun地址被拆分开来，那是因为Intel需要兼容之前的16位的CPU即80286，80286可是个“伪”的保护模式CPU；

5、Segment Selector：这个用以说明当前这个段所属的是数据段，还是代码段，向上增长还是向下增长？这个去看下GDT表即可知道。

好了，基本的字段解释完毕了，可有个问题，我们今年分析的是64位的CPU，内核当然是64位的，你这里的Offset是32位的，当然不对，确实，上边给大家看的是32位的CPU中IDT表的结构，下边再来看看64位的IDT结构：

[![](https://p4.ssl.qhimg.com/t01f36c94dc851d22e0.png)](https://p4.ssl.qhimg.com/t01f36c94dc851d22e0.png)

只有一个字段需要解释，那就是IST，解释这个之前大家先考虑一下这个问题：用户态中断发生时，CPU需要切回到内核态，而内核态的栈必然与用户态的栈是隔离的。【大家伙考虑下，如果栈不隔离，会不会有安全问题？】既然需要切换栈，那么栈地址的位置是怎么找到的呢？提示下大家int 2e陷阱门进内核时，内核栈是怎么提供的，syscall快速指令进内核是，内核栈是如何通过MSR寄存器提供的，留作大家的作业吧。这里的IST是另外一种方式提供内核栈。

至此，理论部分全部讲解完毕，下边我们来做实验看看内核和调试器如何配合完成这项壮举的。

### 1.2 调试器是如何配合的

好了，下边调试一个实际的程序看下，调试器又是如何配合的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010a86855530f1e347.png)

[![](https://p3.ssl.qhimg.com/t01d44e6acb34654297.png)](https://p3.ssl.qhimg.com/t01d44e6acb34654297.png)

大家意不意外，惊不惊喜，居然不是0xcc，也不是int  3；太意外了把。调试器失灵了？当然不是，要是真的失灵了，程序就不会在这断下来了。那又是为何？别急，祭出我们的杀器——Windbg，来一探究竟。再次附加到当前这个被调试进程，别紧张，我知道你以前没这么玩过——一个进程可可以被两个调试器同时调。这是假象，另一个调试器只是看看数据，调不了的。如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019817d65ce937097e.png)

真相了，原来是VS2010的调试器“玩阴的”，故意不给你显示，其实所有调试器内部都会维护一个断点列表之类的数据结构，当你查询某些指令空间时，他会遍历这个结构，还原出原来的真是指令数据给你看。为什么他要这么做？因为intel的CPU时CISC架构的，如果某一个字节错了，可能导致后边整个解码到反汇编都错了，这样的话你还不砸锅了。比如下边的图所示：

[![](https://p3.ssl.qhimg.com/t019bdec716d5086d4c.png)](https://p3.ssl.qhimg.com/t019bdec716d5086d4c.png)

哎，各个调试器之间相互拆台，哈哈。

### 1.3 内核调试器手动解析IDT表结构

第一个蹦出来的问题是：怎么找到IDT表？熟读intel白皮书300遍，不会写来一会找，哈哈。有个寄存器，IDTR专门负责记录IDT表的位置。里边的值是OS填进去的，因为IDT表是OS负责构建的，当然只有它知道具体的地址罗。另外，问大家一个问题，IDTR中的地址是物理地址还是虚拟地址啊？

如下：

```
1: kd&gt; r idtr

idtr=ffffc581e9ad1000

1: kd&gt; dq ffffc581e9ad1000

ffffc581`e9ad1000  30728e00`00100100 00000000`fffff802

ffffc581`e9ad1010  30728e04`00100180 00000000`fffff802

ffffc581`e9ad1020  30728e03`00100200 00000000`fffff802

ffffc581`e9ad1030  3072ee00`00100280 00000000`fffff802

ffffc581`e9ad1040  3072ee00`00100300 00000000`fffff802

ffffc581`e9ad1050  30728e00`00100380 00000000`fffff802

ffffc581`e9ad1060  30728e00`00100400 00000000`fffff802

ffffc581`e9ad1070  30728e00`00100480 00000000`fffff802
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bcab8653463c1640.png)

按照之前的64位模式的IDT表结构进行拆分可得处理函数的地址为：0xfffff80230720280，验证下，看看这个地址到底是啥：

[![](https://p5.ssl.qhimg.com/t01d6360732d1ff86f0.png)](https://p5.ssl.qhimg.com/t01d6360732d1ff86f0.png)

嗯，到这CPU硬件做的事情就基本告一段落了。下边我们迈入内核的大门。继续前行。

## 2.Windows内核中对异常的处理

### 2.1 KiBreakpointTrapShadow 分析

KiBreakpointTrapShadow的源码如下

```
KVASCODE:0000000140292280 KiBreakpointTrapShadow proc near

KVASCODE:0000000140292280

KVASCODE:0000000140292280 arg_0           = byte ptr  8

KVASCODE:0000000140292280 arg_20          = byte ptr  28h

KVASCODE:0000000140292280

KVASCODE:0000000140292280                 test    [rsp+arg_0], 1

KVASCODE:0000000140292285                 jz      short loc_1402922C6

KVASCODE:0000000140292287                 push    rax

KVASCODE:0000000140292289                 push    rsi

KVASCODE:000000014029228A                 swapgs

KVASCODE:000000014029228D                 mov     rsi, gs:7000h   ; KPCR.KPRCB.KernelDirectoryTableBase

KVASCODE:0000000140292296                 bt      dword ptr gs:7018h, 1 ; KPCR.KPRCB.ShadowFlags

KVASCODE:00000001402922A0                 jb      short loc_1402922A5

KVASCODE:00000001402922A2                 mov     cr3, rsi

KVASCODE:00000001402922A5

KVASCODE:00000001402922A5 loc_1402922A5:                          ; CODE XREF: KiBreakpointTrapShadow+20↑j

KVASCODE:00000001402922A5                 lea     rsi, [rsp+10h+arg_20]

KVASCODE:00000001402922AA                 mov     rsp, gs:7008h   ; KPCR.KPRCB.RspBaseShadow

KVASCODE:00000001402922B3                 push    qword ptr [rsi-8] ; SS

KVASCODE:00000001402922B6                 push    qword ptr [rsi-10h] ; RSP

KVASCODE:00000001402922B9                 push    qword ptr [rsi-18h] ; EFLAGS

KVASCODE:00000001402922BC                 push    qword ptr [rsi-20h] ; CS

KVASCODE:00000001402922BF                 push    qword ptr [rsi-28h] ; RIP

KVASCODE:00000001402922C2                 mov     rsi, [rsi-38h]

KVASCODE:00000001402922C6

KVASCODE:00000001402922C6 loc_1402922C6:                          ; CODE XREF: KiBreakpointTrapShadow+5↑j

KVASCODE:00000001402922C6                 jmp     KiBreakpointTrap
```

[![](https://p5.ssl.qhimg.com/t01d6c7cec17e707cb7.png)](https://p5.ssl.qhimg.com/t01d6c7cec17e707cb7.png)

该函数需要仔细分析下，如下：

1、当中断或者异常发生时，CPU硬件都会自动的往栈里边压入SS,RSP,EFLAGS,CS,RIP的值,所以第一行指令：

test    [rsp+arg_0], 1

取出的是CS的值，注意此时的rsp的值。也即是判断cs的值的最后一位是否为1：

若为1：则说明是从Ring3进入Ring0的；

若为0：则说明原先就是Ring0的；

区分这两个的原因是：内核栈与用户态栈是分开的，需要做栈的切换。这个从代码中 就可看出。

2、执行swapgs指令，swapgs指令的作用就是从MSR中读取出GS段的基地址。因为GS在用户态中指向的数据结构是TEB，而进入内核之后，GS需要指向KPCR，那这个地址在哪呢？在MSR中，如下所示：

[![](https://p2.ssl.qhimg.com/t01f83cda4ca92af794.png)](https://p2.ssl.qhimg.com/t01f83cda4ca92af794.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012c132f2838fa0fa8.png)

下边做实验看下MSR中0xC000_0101处的值到底是多少。

[![](https://p2.ssl.qhimg.com/t0179a97a63a4a9b758.png)](https://p2.ssl.qhimg.com/t0179a97a63a4a9b758.png)

那这个KPCR是啥嘞，在内核中，每个逻辑核都有这么一个结构体，代表着CPU核心。下边简单看下这个 结构：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012388fa22a0e296d9.png)

多么熟悉的结构啊，多么熟悉的字段啊

可能眼尖的朋友已经看到了，源码中取的gs:7000数据，这里的结构体才最多偏移0x180不够呀。其实最后一个KPRCB才是KPCR最重要的，它记录了相当多的数据。如下：

[![](https://p1.ssl.qhimg.com/t017ac04f0c1d25dd81.png)](https://p1.ssl.qhimg.com/t017ac04f0c1d25dd81.png)

好了，这里减去180的原因是将其转换为相对于KPRCB的偏移。这与代码中的取内核的页表机制就对上了。这里需要特别说明下，Win10中同一个进程用户态页表和内核态页表是不同的，做了页表隔离。

3、KPCR.KPRCB.ShadowFlags当然就是决定是否启用这种隔离机制罗。启用的话就直接切换页表基地址了，也即切换CR3的值；

4、最后几行代码很简单了，切换到指定的内核栈，然后讲中断时记录的5个寄存器的值压栈，然后跳去执行KiBreakpointTrap；

### 2.2 KiBreakpointTrap分析

KiBreakpointTrap代码如下：

```
.text:00000001401812C0 KiBreakpointTrap proc near              ; CODE XREF: KiBreakpointTrapShadow:loc_1402922C6↓j

.text:00000001401812C0

.text:00000001401812C0 var_13D         = byte ptr -13Dh

.text:00000001401812C0 var_138         = qword ptr -138h

.text:00000001401812C0 var_130         = qword ptr -130h

.text:00000001401812C0 var_128         = qword ptr -128h

.text:00000001401812C0 var_120         = qword ptr -120h

.text:00000001401812C0 var_118         = qword ptr -118h

.text:00000001401812C0 var_110         = qword ptr -110h

.text:00000001401812C0 var_108         = qword ptr -108h

.text:00000001401812C0 arg_0           = byte ptr  8

.text:00000001401812C0

.text:00000001401812C0                 sub     rsp, 8

.text:00000001401812C4                 push    rbp

.text:00000001401812C5                 sub     rsp, 158h

.text:00000001401812CC                 lea     rbp, [rsp+80h]

.text:00000001401812D4                 mov     [rbp+0E8h+var_13D], 1

.text:00000001401812D8                 mov     [rbp+0E8h+var_138], rax

.text:00000001401812DC                 mov     [rbp+0E8h+var_130], rcx

.text:00000001401812E0                 mov     [rbp+0E8h+var_128], rdx

.text:00000001401812E4                 mov     [rbp+0E8h+var_120], r8

.text:00000001401812E8                 mov     [rbp+0E8h+var_118], r9

.text:00000001401812EC                 mov     [rbp+0E8h+var_110], r10

.text:00000001401812F0                 mov     [rbp+0E8h+var_108], r11

.text:00000001401812F4                 test    [rbp+0E8h+arg_0], 1

.text:00000001401812FB                 jnz     short loc_140181329

.text:00000001401812FD                 test    word ptr gs:278h, 40h

.text:0000000140181308                 jnz     short loc_140181312

.text:000000014018130A                 lfence

.text:000000014018130D                 jmp     loc_1401815A8

.text:0000000140181312 ; ---------------------------------------------------------------------------

.text:0000000140181312

.text:0000000140181312 loc_140181312:                          ; CODE XREF: KiBreakpointTrap+48↑j

.text:0000000140181312                 movzx   eax, byte ptr gs:27Ah

.text:000000014018131B                 mov     ecx, 48h

.text:0000000140181320                 xor     edx, edx

.text:0000000140181322                 wrmsr

.text:0000000140181324                 jmp     loc_1401815A8

.text:0000000140181329 ; ---------------------------------------------------------------------------

.text:0000000140181329

.text:0000000140181329 loc_140181329:                          ; CODE XREF: KiBreakpointTrap+3B↑j

.text:0000000140181329                 test    cs:KiKvaShadow, 1

.text:0000000140181330                 jnz     short loc_140181335

.text:0000000140181332                 swapgs

.text:0000000140181335

.text:0000000140181335 loc_140181335:                          ; CODE XREF: KiBreakpointTrap+70↑j

.text:0000000140181335                 mov     r10, gs:188h

.text:000000014018133E                 mov     rcx, gs:188h

.text:0000000140181347                 mov     rcx, [rcx+220h]

.text:000000014018134E                 mov     rcx, [rcx+838h]

.text:0000000140181355                 mov     gs:270h, rcx

.text:000000014018135E                 movzx   edx, word ptr gs:278h

.text:0000000140181367                 test    edx, 20h

.text:000000014018136D                 jz      short loc_1401813C6

.text:000000014018136F                 test    edx, 200h

.text:0000000140181375                 jz      short loc_14018137F

.text:0000000140181377                 lfence

.text:000000014018137A                 jmp     loc_14018141D

.text:000000014018137F ; ---------------------------------------------------------------------------

.text:000000014018137F

.text:000000014018137F loc_14018137F:                          ; CODE XREF: KiBreakpointTrap+B5↑j

.text:000000014018137F                 test    rcx, rcx

.text:0000000140181382                 jnz     short loc_1401813CE

.text:0000000140181384                 test    edx, 100h

.text:000000014018138A                 jnz     short loc_1401813C6

.text:000000014018138C                 test    edx, 3

.text:0000000140181392                 jz      short loc_1401813C6

.text:0000000140181394                 mov     eax, 2

.text:0000000140181399                 test    edx, 2

.text:000000014018139F                 jnz     short loc_1401813A6

.text:00000001401813A1                 mov     eax, 1

.text:00000001401813A6

.text:00000001401813A6 loc_1401813A6:                          ; CODE XREF: KiBreakpointTrap+DF↑j

.text:00000001401813A6                 cmp     al, gs:27Ah

.text:00000001401813AE                 jz      short loc_1401813C6

.text:00000001401813B0                 mov     gs:27Ah, al

.text:00000001401813B8                 mov     ecx, 48h

.text:00000001401813BD                 xor     edx, edx

.text:00000001401813BF                 wrmsr

.text:00000001401813C1                 jmp     loc_14018154A

.text:00000001401813C6 ; ---------------------------------------------------------------------------

.text:00000001401813C6

.text:00000001401813C6 loc_1401813C6:                          ; CODE XREF: KiBreakpointTrap+AD↑j

.text:00000001401813C6                                         ; KiBreakpointTrap+CA↑j ...

.text:00000001401813C6                 lfence

.text:00000001401813C9                 jmp     loc_14018154A

.text:00000001401813CE ; ---------------------------------------------------------------------------

.text:00000001401813CE

.text:00000001401813CE loc_1401813CE:                          ; CODE XREF: KiBreakpointTrap+C2↑j

.text:00000001401813CE                 test    edx, 1

.text:00000001401813D4                 jnz     short loc_140181407

.text:00000001401813D6                 test    edx, 2

.text:00000001401813DC                 jz      short loc_1401813F4

.text:00000001401813DE                 mov     eax, 2

.text:00000001401813E3                 mov     gs:27Ah, al

.text:00000001401813EB                 mov     ecx, 48h

.text:00000001401813F0                 xor     edx, edx

.text:00000001401813F2                 wrmsr

.text:00000001401813F4

.text:00000001401813F4 loc_1401813F4:                          ; CODE XREF: KiBreakpointTrap+11C↑j

.text:00000001401813F4                 mov     eax, 1

.text:00000001401813F9                 xor     edx, edx

.text:00000001401813FB                 mov     ecx, 49h

.text:0000000140181400                 wrmsr

.text:0000000140181402                 jmp     loc_14018154A

.text:0000000140181407 ; ---------------------------------------------------------------------------

.text:0000000140181407

.text:0000000140181407 loc_140181407:                          ; CODE XREF: KiBreakpointTrap+114↑j

.text:0000000140181407                 mov     eax, 1

.text:000000014018140C                 mov     gs:27Ah, al

.text:0000000140181414                 mov     ecx, 48h

.text:0000000140181419                 xor     edx, edx

.text:000000014018141B                 wrmsr

.text:000000014018141D

.text:000000014018141D loc_14018141D:                          ; CODE XREF: KiBreakpointTrap+BA↑j

.text:000000014018141D                 test    word ptr gs:278h, 4

.text:0000000140181428                 jnz     short loc_1401813C6

.text:000000014018142A                 call    sub_14018153D

.text:000000014018142A KiBreakpointTrap endp ;
```

这段代码的主要作用是构建出一个KTRAP_FRAME结构。KTRAP_FRAME这个结构详细记录了从Ring3进来时，Ring3的上下文，可以直接理解为Ring3中的CONTEXT结构体，只不过记录的数据要多很多。结构体如下：

```
1: kd&gt; dt _KTRAP_FRAME

nt!_KTRAP_FRAME

   +0x000 P1Home           : Uint8B

   +0x008 P2Home           : Uint8B

   +0x010 P3Home           : Uint8B

   +0x018 P4Home           : Uint8B

   +0x020 P5               : Uint8B

   +0x028 PreviousMode     : Char

   +0x029 PreviousIrql     : UChar

   +0x02a FaultIndicator   : UChar

   +0x02a NmiMsrIbrs       : UChar

   +0x02b ExceptionActive  : UChar

   +0x02c MxCsr            : Uint4B

   +0x030 Rax              : Uint8B

   +0x038 Rcx              : Uint8B

   +0x040 Rdx              : Uint8B

   +0x048 R8               : Uint8B

   +0x050 R9               : Uint8B

   +0x058 R10              : Uint8B

   +0x060 R11              : Uint8B

   +0x068 GsBase           : Uint8B

   +0x068 GsSwap           : Uint8B

   +0x070 Xmm0             : _M128A

   +0x080 Xmm1             : _M128A

   +0x090 Xmm2             : _M128A

   +0x0a0 Xmm3             : _M128A

   +0x0b0 Xmm4             : _M128A

   +0x0c0 Xmm5             : _M128A

   +0x0d0 FaultAddress     : Uint8B

   +0x0d0 ContextRecord    : Uint8B

   +0x0d8 Dr0              : Uint8B

   +0x0e0 Dr1              : Uint8B

   +0x0e8 Dr2              : Uint8B

   +0x0f0 Dr3              : Uint8B

   +0x0f8 Dr6              : Uint8B

   +0x100 Dr7              : Uint8B

   +0x108 DebugControl     : Uint8B

   +0x110 LastBranchToRip  : Uint8B

   +0x118 LastBranchFromRip : Uint8B

   +0x120 LastExceptionToRip : Uint8B

   +0x128 LastExceptionFromRip : Uint8B

   +0x130 SegDs            : Uint2B

   +0x132 SegEs            : Uint2B

   +0x134 SegFs            : Uint2B

   +0x136 SegGs            : Uint2B

   +0x138 TrapFrame        : Uint8B

   +0x140 Rbx              : Uint8B

   +0x148 Rdi              : Uint8B

   +0x150 Rsi              : Uint8B

   +0x158 Rbp              : Uint8B

   +0x160 ErrorCode        : Uint8B

   +0x160 ExceptionFrame   : Uint8B

   +0x168 Rip              : Uint8B

   +0x170 SegCs            : Uint2B

   +0x172 Fill0            : UChar

   +0x173 Logging          : UChar

   +0x174 Fill1            : [2] Uint2B

   +0x178 EFlags           : Uint4B

   +0x17c Fill2            : Uint4B

   +0x180 Rsp              : Uint8B

   +0x188 SegSs            : Uint2B

   +0x18a Fill3            : Uint2B

   +0x18c Fill4            : Uint4B
```

代码中test    [rbp+0E8h+arg_0], 1用于判断先前模式是否为Ring3.是的话则接着跑到KiKvaShadow处，判断该值，如下：

```
1: kd&gt; dd KiKvaShadow

fffff802`308a1840  00000001 00000000 302cf000 fffff802

fffff802`308a1850  00000000 00000000 00000000 00000000

fffff802`308a1860  00000000 00000000 00000000 00000000

fffff802`308a1870  00000000 00000000 00000000 00000000

fffff802`308a1880  307db180 fffff802 00000000 00000000

fffff802`308a1890  000001cc 00000000 307db8b4 fffff802

fffff802`308a18a0  00000000 00000000 00000000 00000000

fffff802`308a18b0  00000000 00000000 00000000 00000000
```

接着执行movzx   edx, word ptr gs:278h，如下：

[![](https://p5.ssl.qhimg.com/t01a64548e44e9233f9.png)](https://p5.ssl.qhimg.com/t01a64548e44e9233f9.png)

为0，则.text:000000014018136D                 jz      short loc_1401813C6指令跳转，执行，经跳转之后，最终执行以下代码：

```
.text:00000001401815A9                 stmxcsr dword ptr [rbp-54h]

.text:00000001401815AD                 ldmxcsr dword ptr gs:180h

.text:00000001401815B6                 movaps  xmmword ptr [rbp-10h], xmm0

.text:00000001401815BA                 movaps  xmmword ptr [rbp+0], xmm1

.text:00000001401815BE                 movaps  xmmword ptr [rbp+10h], xmm2

.text:00000001401815C2                 movaps  xmmword ptr [rbp+20h], xmm3

.text:00000001401815C6                 movaps  xmmword ptr [rbp+30h], xmm4

.text:00000001401815CA                 movaps  xmmword ptr [rbp+40h], xmm5

.text:00000001401815CE                 test    dword ptr [rbp+0F8h], 200h;_KTRAP_FRAME.EFlags

.text:00000001401815D8                 jz      short loc_1401815DB

.text:00000001401815DA                 sti

.text:00000001401815DB

.text:00000001401815DB loc_1401815DB:                          ; CODE XREF: sub_140181546+92↑j

.text:00000001401815DB                 mov     ecx, 80000003h

.text:00000001401815E0                 mov     edx, 1

.text:00000001401815E5                 mov     r8, [rbp+0E8h]

.text:00000001401815EC                 dec     r8

.text:00000001401815EF                 mov     r9d, 0

.text:00000001401815F5                 call    KiExceptionDispatch

.text:00000001401815FA                 nop

.text:00000001401815FB                 retn
```

test    dword ptr [rbp+0F8h], 200h这行代码在判断EFLAGS.IF标志位,即判断是否允许开中断。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0165973723bbeac1e3.png)

经过上边这一系列的操作，终于到了下边这几个关键的代码了，如下：

```
.text:00000001401815DB                 mov     ecx, 80000003h

.text:00000001401815E0                 mov     edx, 1

.text:00000001401815E5                 mov     r8, [rbp+0E8h];nt!_KTRAP_FRAME.Rip

.text:00000001401815EC                 dec     r8;由于断点执行执行的时候,Rip指向了下一条指令,这边做了减一操作就是返回到触发中断的指令处

.text:00000001401815EF                 mov     r9d, 0

.text:00000001401815F5                 call    KiExceptionDispatch

.text:00000001401815FA                 nop

.text:00000001401815FB                 retn
```

KiExceptionDispatch的具体分析，见后续文章。精彩将会继续。
