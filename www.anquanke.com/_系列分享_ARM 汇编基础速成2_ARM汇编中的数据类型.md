> 原文链接: https://www.anquanke.com//post/id/86393 


# 【系列分享】ARM 汇编基础速成2：ARM汇编中的数据类型


                                阅读量   
                                **221319**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：azeria-labs.com
                                <br>原文地址：[https://azeria-labs.com/arm-data-types-and-registers-part-2/](https://azeria-labs.com/arm-data-types-and-registers-part-2/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01c81e5f5c9bfbd03a.png)](https://p2.ssl.qhimg.com/t01c81e5f5c9bfbd03a.png)



译者：[arnow117](http://bobao.360.cn/member/contribute?uid=941579989)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

传送门：[【系列分享】ARM 汇编基础速成1：ARM汇编以及汇编语言基础介绍](http://bobao.360.cn/learning/detail/4070.html)



这是ARM汇编速成系列的第二部分，将学习到ARM汇编基础，数据类型及寄存器。

<br>

**ARM汇编数据类型基础**



与高级语言类似，ARM也支持操作不同的数据类型。

[![](https://p4.ssl.qhimg.com/t016d1649041548e14e.png)](https://p4.ssl.qhimg.com/t016d1649041548e14e.png)

被加载或者存储的数据类型可以是无符号（有符号）的字(words，四字节)，半字(halfwords，两字节)，或者字节(bytes)。这些数据类型在汇编语言中的扩展后缀为**-h**或者**-sh**对应着半字，**-b**或者**-sb**对应着字节，但是对于字并没有对应的扩展。无符号类型与有符号类型的差别是：

符号数据类型可以包含正负数所以数值范围上更低些

无符号数据类型可以放得下很大的正数但是放不了负数

这有一些要求使用对应数据类型做存取操作的汇编指令示例：



```
ldr = 加载字，宽度四字节
ldrh = 加载无符号的半字，宽度两字节
ldrsh = 加载有符号的半字，宽度两字节
ldrb = 加载无符号的字节
ldrsb = 加载有符号的字节
str = 存储字，宽度四字节
strh = 存储无符号的半字，宽度两字节
strsh = 存储有符号的半字，宽度两字节
strb = 存储无符号的字节
strsb = 存储有符号的字节
```



**字节序**



在内存中有两种字节排布顺序，大端序(BE)或者小端序(LE)。两者的主要不同是对象中的每个字节在内存中的存储顺序存在差异。一般X86中是小端序，最低的字节存储在最低的地址上。在大端机中最高的字节存储在最低的地址上。

[![](https://p1.ssl.qhimg.com/t01b6d7f41b02b0a58d.png)](https://p1.ssl.qhimg.com/t01b6d7f41b02b0a58d.png)

在版本3之前，ARM使用的是小端序，但在这之后就都是使用大端序了，但也允许切换回小端序。在我们样例代码所在的ARMv6中，指令代码是以[[小端序排列对齐]](http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.ddi0301h/Cdfbbchb.html)。但是数据访问时采取大端序还是小端序使用程序状态寄存器(CPSR)的第9比特位来决定的。

[![](https://p4.ssl.qhimg.com/t013129fa945eb6905e.png)](https://p4.ssl.qhimg.com/t013129fa945eb6905e.png)

**<br>**

**ARM寄存器**



寄存器的数量由ARM版本决定。根据[[ARM参考手册]](http://infocenter.arm.com/help/topic/com.arm.doc.dui0473c/Babdfiih.html)，在ARMv6-M与ARMv7-M的处理器中有30个32bit位宽度的通用寄存器。前16个寄存器是用户层可访问控制的，其他的寄存器在高权限进程中可以访问（但ARMv6-M与ARMv7-M除外）。我们仅介绍可以在任何权限模式下访问的16个寄存器。这16个寄存器分为两组：通用寄存器与有特殊含义的寄存器。

[![](https://p3.ssl.qhimg.com/t01190e4f9d967388fb.jpg)](https://p3.ssl.qhimg.com/t01190e4f9d967388fb.jpg)

下面这张表是ARM架构与寄存器与Intel架构寄存器的关系：

[![](https://p0.ssl.qhimg.com/t01a8e5d24fa91f9f0f.jpg)](https://p0.ssl.qhimg.com/t01a8e5d24fa91f9f0f.jpg)

R0-R12：用来在通用操作中存储临时的值，指针等。R0被用来存储函数调用的返回值。R7经常被用作存储系统调用号，R11存放着帮助我们找到栈帧边界的指针（之后会讲）。以及，在ARM的函数调用约定中，前四个参数按顺序存放在R0-R3中。

R13：SP(栈指针）。栈指针寄存器用来指向当前的栈顶。栈是一片来存储函数调用中相关数据的内存，在函数返回时会被修改为对应的栈指针。栈指针用来帮助在栈上申请数据空间。比如说你要申请一个字的大小，就会将栈指针减4，再将数据放入之前所指向的位置。

R14：LR(链接寄存器)。当一个函数调用发生，链接寄存器就被用来记录函数调用发生所在位置的下一条指令的地址。这么做允许我们快速的从子函数返回到父函数。

R15：PC(程序计数器)。程序计数器是一个在程序指令执行时自增的计数器。它的大小在ARM模式下总是4字节对齐，在Thumb模式下总是两字节对齐。当执行一个分支指令时，PC存储目的地址。在程序执行中，ARM模式下的PC存储着当前指令加8(两条ARM指令后)的位置，Thumb(v1)模式下的PC存储着当前指令加4(两条Thumb指令后)的位置。这也是X86与ARM在PC上的主要不同之处。

我们可以通过调试来观察PC的行为。我们的程序中将PC的值存到R0中同时包含了两条其他指令，来看看会发生什么。



```
.section .text
.global _start
_start:
 mov r0, pc
 mov r1, #2
 add r2, r1, r1
 bkpt
```

在GDB中，我们开始调试这段汇编代码：



```
gef&gt; br _start
Breakpoint 1 at 0x8054
gef&gt; run
```

在开始执行触发断点后，首先会在GDB中看到:

```
$r0 0x00000000   $r1 0x00000000   $r2 0x00000000   $r3 0x00000000 
$r4 0x00000000   $r5 0x00000000   $r6 0x00000000   $r7 0x00000000 
$r8 0x00000000   $r9 0x00000000   $r10 0x00000000  $r11 0x00000000 
$r12 0x00000000  $sp 0xbefff7e0   $lr 0x00000000   $pc 0x00008054 
$cpsr 0x00000010 
0x8054 &lt;_start&gt; mov r0, pc     &lt;- $pc
0x8058 &lt;_start+4&gt; mov r0, #2
0x805c &lt;_start+8&gt; add r1, r0, r0
0x8060 &lt;_start+12&gt; bkpt 0x0000
0x8064 andeq r1, r0, r1, asr #10
0x8068 cmnvs r5, r0, lsl #2
0x806c tsteq r0, r2, ror #18
0x8070 andeq r0, r0, r11
0x8074 tsteq r8, r6, lsl #6
```

可以看到在程序的开始PC指向0x8054这个位置即第一条要被执行的指令，那么此时我们使用GDB命令si，执行下一条机器码。下一条指令是把PC的值放到R0寄存器中，所以应该是0x8054么？来看看调试器的结果。

```
$r0 0x0000805c   $r1 0x00000000   $r2 0x00000000   $r3 0x00000000 
$r4 0x00000000   $r5 0x00000000   $r6 0x00000000   $r7 0x00000000 
$r8 0x00000000   $r9 0x00000000   $r10 0x00000000  $r11 0x00000000 
$r12 0x00000000  $sp 0xbefff7e0   $lr 0x00000000   $pc 0x00008058 
$cpsr 0x00000010
0x8058 &lt;_start+4&gt; mov r0, #2       &lt;- $pc
0x805c &lt;_start+8&gt; add r1, r0, r0
0x8060 &lt;_start+12&gt; bkpt 0x0000
0x8064 andeq r1, r0, r1, asr #10
0x8068 cmnvs r5, r0, lsl #2
0x806c tsteq r0, r2, ror #18
0x8070 andeq r0, r0, r11
0x8074 tsteq r8, r6, lsl #6
0x8078 adfcssp f0, f0, #4.0
```

当然不是，在执行0x8054这条位置的机器码时，PC已经读到了两条指令后的位置也就是0x805c(见R0寄存器)。所以我们以为直接读取PC寄存器的值时，它指向的是下一条指令的位置。但是调试器告诉我们，PC指向当前指令向后两条机器码的位置。这是因为早期的ARM处理器总是会先获取当前位置后两条的机器码。这么做的原因也是确保与早期处理器的兼容性。



**当前程序状态寄存器（CPSR）**



当你用GDB调试ARM程序的的时候你能会可以看见Flags这一栏（GDB配置插件GEF后就可以看见了，或者直接在GDB里面输入flags也可以）。

[![](https://p2.ssl.qhimg.com/t016efaff2f0227e3dc.png)](https://p2.ssl.qhimg.com/t016efaff2f0227e3dc.png)

图中寄存器“`$CSPR“`显示了当前状态寄存器的值，Flags里面出现的thumb，fast，interrupt，overflow，carry，zero，negative就是来源于CSPR寄存器中对应比特位的值。ARM架构的N，Z，C，V与X86架构EFLAG中的SF，ZF，CF，OF相对应。这些比特位在汇编级别的条件执行或者循环的跳出时，被用作判断的依据。

[![](https://p2.ssl.qhimg.com/t016ecca6915848b771.png)](https://p2.ssl.qhimg.com/t016ecca6915848b771.png)

上图展示了32位的CPSR寄存器的比特位含义，左边是最大比特位，右边是最小比特位。每个单元代表一个比特。这一个个比特的含义都很丰富：

[![](https://p2.ssl.qhimg.com/t015325453014a5aaaf.jpg)](https://p2.ssl.qhimg.com/t015325453014a5aaaf.jpg)



假设我们用CMP指令去比较1和2，结果会是一个负数因为1-2=-1。然而当我们反过来用2和1比较，C位将被设定，因为在一个较大的数上减了较小的数，没有发生借位。当我们比较两个相同的数比如2和2时，由于结果是0，Z标志位将被置一。注意CMP指令中被使用的寄存器的值并不会被修改，其计算结果仅仅影响到CPSR寄存器中的状态位。

在开了GEF插件的GDB中，计算结果如下图：在这里我们比较的两个寄存器是R1和R0，所以执行后的flag状态如下图。

[![](https://p1.ssl.qhimg.com/t01cb99526de00b408f.png)](https://p1.ssl.qhimg.com/t01cb99526de00b408f.png)

Carry位Flag被设置的原因是CMP R1,R0会去拿4和2做比较。因为我们用以个较大的数字去减一个较少的数字，没有发生借位。Carry位便被置1。相反的，如果是CMP R0,R1那么Negative位会被置一。

<br>


