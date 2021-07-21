> 原文链接: https://www.anquanke.com//post/id/86406 


# 【系列分享】ARM 汇编基础速成4：ARM汇编内存访问相关指令


                                阅读量   
                                **236133**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：azeria-labs.com
                                <br>原文地址：[https://azeria-labs.com/memory-instructions-load-and-store-part-4/](https://azeria-labs.com/memory-instructions-load-and-store-part-4/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t015701a8baad972e61.png)](https://p4.ssl.qhimg.com/t015701a8baad972e61.png)



译者：[arnow117](http://bobao.360.cn/member/contribute?uid=941579989)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

传送门

[【系列分享】ARM 汇编基础速成1：ARM汇编以及汇编语言基础介绍](http://bobao.360.cn/learning/detail/4070.html)

**[【系列分享】ARM 汇编基础速成2：ARM汇编中的数据类型](http://bobao.360.cn/learning/detail/4075.html)**

[**【系列分享】ARM 汇编基础速成3：ARM模式与THUMB模式**](http://bobao.360.cn/learning/detail/4082.html)



ARM使用加载-存储模式控制对内存的访问，这意味着只有加载/存储(LDR或者STR)才能访问内存。尽管X86中允许很多指令直接操作在内存中的数据，但ARM中依然要求在操作数据前，必须先从内存中将数据取出来。这就意味着如果要增加一个32位的在内存中的值，需要做三种类型的操作(加载，加一，存储)将数据从内存中取到寄存器，对寄存器中的值加一，再将结果放回到内存中。

为了解释ARM架构中的加载和存储机制，我们准备了一个基础的例子以及附加在这个基础例子上的三种不同的对内存地址的便宜访问形式。每个例子除了STR/LDR的偏移模式不同外，其余的都一样。而且这个例子很简单，最佳的实践方式是用GDB去调试这段汇编代码。

第一种偏移形式：立即数作为偏移

地址模式：用作偏移

地址模式：前向索引

地址模式：后向索引

第二种偏移形式：寄存器作为偏移

地址模式：用作偏移

地址模式：前向索引

地址模式：后向索引

第三种偏移形式：寄存器缩放值作为偏移

地址模式：用作偏移

地址模式：前向索引

地址模式：后向索引

<br>

**基础样例代码**

通常，LDR被用来从内存中加载数据到寄存器，STR被用作将寄存器的值存放到内存中。

[![](https://p2.ssl.qhimg.com/t01012ba153662843a0.png)](https://p2.ssl.qhimg.com/t01012ba153662843a0.png)



```
LDR R2, [R0]   @ [R0] - 数据源地址来自于R0指向的内存地址
@ LDR操作：从R0指向的地址中取值放到R2中
STR R2, [R1]   @ [R1] - 目的地址来自于R1在内存中指向的地址
@ STR操作：将R2中的值放到R1指向的地址中
```

样例程序的汇编代码及解释如下：



```
.data          /* 数据段是在内存中动态创建的，所以它的在内存中的地址不可预测*/
var1: .word 3  /* 内存中的第一个变量 */
var2: .word 4  /* 内存中的第二个变量 */
.text          /* 代码段开始 */ 
.global _start
_start:
    ldr r0, adr_var1  @ 将存放var1值的地址adr_var1加载到寄存器R0中 
    ldr r1, adr_var2  @ 将存放var2值的地址adr_var2加载到寄存器R1中 
    ldr r2, [r0]      @ 将R0所指向地址中存放的0x3加载到寄存器R2中  
    str r2, [r1]      @ 将R2中的值0x3存放到R1做指向的地址 
    bkpt             
adr_var1: .word var1  /* var1的地址助记符 */
adr_var2: .word var2  /* var2的地址助记符 */
```

在底部我们有我们的文字标识池(在代码段中用来存储常量，字符串，或者偏移等的内存，可以通过位置无关的方式引用)，分别用adr_var1和adr_var2存储着变量var1和var2的内存地址(var1和var2的值在数据段定义)。第一条LDR指令将变量var1的地址加载到寄存器R0。第二条LDR指令同样将var2的地址加载到寄存器R1。之后我们将存储在R0指向的内存地址中的值加载到R2，最后将R2中的值存储到R1指向的内存地址中。

当我们加载数据到寄存器时，方括号“[]”意味着：将其中的值当做内存地址，并取这个内存地址中的值加载到对应寄存器。

当我们存储数据到内存时，方括号“[]”意味着：将其中的值当做内存地址，并向这个内存地址所指向的位置存入对应的值。

听者好像有些抽象，所以再来看看这个动画吧：

[![](https://p3.ssl.qhimg.com/t011cd9a1d94d9ea474.gif)](https://p3.ssl.qhimg.com/t011cd9a1d94d9ea474.gif)

同样的再来看看的这段代码在调试器中的样子。



```
gef&gt; disassemble _start
Dump of assembler code for function _start:
 0x00008074 &lt;+0&gt;:      ldr  r0, [pc, #12]   ; 0x8088 &lt;adr_var1&gt;
 0x00008078 &lt;+4&gt;:      ldr  r1, [pc, #12]   ; 0x808c &lt;adr_var2&gt;
 0x0000807c &lt;+8&gt;:      ldr  r2, [r0]
 0x00008080 &lt;+12&gt;:     str  r2, [r1]
 0x00008084 &lt;+16&gt;:     bx   lr
End of assembler dump.
```

可以看到此时的反汇编代码和我们编写的汇编代码有出入了。前两个LDR操作的源寄存器被改成了[pc,#12]。这种操作叫做PC相对地址。因为我们在汇编代码中使用的只是数据的标签，所以在编译时候编译器帮我们计算出来了与我们想访问的文字标识池的相对便宜，即PC+12。你也可以看汇编代码中手动计算验证这个偏移是正确的，以adr_var1为例，执行到8074时，其当前有效PC与数据段还有三个四字节的距离，所以要加12。关于PC相对取址我们接下来还会接着介绍。

PS：如果你对这里的PC的地址有疑问，可以看外面第二篇关于程序执行时PC的值的说明，PC是指向当前执行指令之后第二条指令所在位置的，在32位ARM模式下是当前执行位置加偏移值8，在Thumb模式下是加偏移值4。这也是与X86架构PC的区别之所在。

[![](https://p2.ssl.qhimg.com/t01a8c6034e8ea5c2d2.png)](https://p2.ssl.qhimg.com/t01a8c6034e8ea5c2d2.png)

<br>

**第一种偏移形式：立即数作偏移**



```
STR    Ra, [Rb, imm]
LDR    Ra, [Rc, imm]
```

在这段汇编代码中，我们使用立即数作为偏移量。这个立即数被用来与一个寄存器中存放的地址做加减操作(下面例子中的R1)，以访问对应地址偏移处的数据。



```
.data
var1: .word 3
var2: .word 4
.text
.global _start
_start:
    ldr r0, adr_var1  @ 将存放var1值的地址adr_var1加载到寄存器R0中 
    ldr r1, adr_var2  @ 将存放var2值的地址adr_var2加载到寄存器R1中 
    ldr r2, [r0]      @ 将R0所指向地址中存放的0x3加载到寄存器R2中  
    str r2, [r1, #2]  @ 取址模式：基于偏移量。R2寄存器中的值0x3被存放到R1寄存器的值加2所指向地址处。
    str r2, [r1, #4]! @ 取址模式：基于索引前置修改。R2寄存器中的值0x3被存放到R1寄存器的值加4所指向地址处，之后R1寄存器中存储的值加4,也就是R1=R1+4。
    ldr r3, [r1], #4  @ 取址模式：基于索引后置修改。R3寄存器中的值是从R1寄存器的值所指向的地址中加载的，加载之后R1寄存器中存储的值加4,也就是R1=R1+4。
    bkpt
adr_var1: .word var1
adr_var2: .word var2
```

让我们把上面的这段汇编代码编译一下，并用GDB调试起来看看真实情况。



```
$ as ldr.s -o ldr.o
$ ld ldr.o -o ldr
$ gdb ldr
```

在GDB(使用GEF插件)中，我们对_start下一个断点并继续运行程序。



```
gef&gt; break _start
gef&gt; run
...
gef&gt; nexti 3     /* 向后执行三条指令 */
```

执行完上述GDB指令后，在我的系统的寄存器的值现在是这个样子(在你的系统里面可能不同)：



```
$r0 : 0x00010098 -&gt; 0x00000003
$r1 : 0x0001009c -&gt; 0x00000004
$r2 : 0x00000003
$r3 : 0x00000000
$r4 : 0x00000000
$r5 : 0x00000000
$r6 : 0x00000000
$r7 : 0x00000000
$r8 : 0x00000000
$r9 : 0x00000000
$r10 : 0x00000000
$r11 : 0x00000000
$r12 : 0x00000000
$sp : 0xbefff7e0 -&gt; 0x00000001
$lr : 0x00000000
$pc : 0x00010080 -&gt; &lt;_start+12&gt; str r2, [r1]
$cpsr : 0x00000010
```

下面来分别调试这三条关键指令。首先执行基于地址偏移的取址模式的STR操作了。就会将R2(0x00000003)中的值存放到R1(0x0001009c)所指向地址偏移2的位置0x1009e。下面一段是执行完对应STR操作后对应内存位置的值。



```
gef&gt; nexti
gef&gt; x/w 0x1009e 
0x1009e &lt;var2+2&gt;: 0x3
```

下一条STR操作使用了基于索引前置修改的取址模式。这种模式的识别特征是(!)。区别是在R2中的值被存放到对应地址后，R1的值也会被更新。这意味着，当我们将R2中的值0x3存储到R1(0x1009c)的偏移4之后的地址0x100A0后，R1的值也会被更新到为这个地址。下面一段是执行完对应STR操作后对应内存位置以及寄存器的值。



```
gef&gt; nexti
gef&gt; x/w 0x100A0
0x100a0: 0x3
gef&gt; info register r1
r1     0x100a0     65696
```

最后一个LDR操作使用了基于索引后置的取址模式。这意味着基础寄存器R1被用作加载的内存地址，之后R1的值被更新为R1+4。换句话说，加载的是R1所指向的地址而不是R1+4所指向的地址，也就是0x100A0中的值被加载到R3寄存器，然后R1寄存器的值被更新为0x100A0+0x4也就是0x100A4。下面一段是执行完对应LDR操作后对应内存位置以及寄存器的值。



```
gef&gt; info register r1
r1      0x100a4   65700
gef&gt; info register r3
r3      0x3       3
```

下图是这个操作发生的动态示意图。

[![](https://p4.ssl.qhimg.com/t01020f63d0eebbf90d.gif)](https://p4.ssl.qhimg.com/t01020f63d0eebbf90d.gif)

<br>

**第二种偏移形式：寄存器作偏移**



```
STR    Ra, [Rb, Rc]
LDR    Ra, [Rb, Rc]
```

在这个偏移模式中，寄存器的值被用作偏移。下面的样例代码展示了当试着访问数组的时候是如何计算索引值的。



```
.data
var1: .word 3
var2: .word 4
.text
.global _start
_start:
    ldr r0, adr_var1  @ 将存放var1值的地址adr_var1加载到寄存器R0中 
    ldr r1, adr_var2  @ 将存放var2值的地址adr_var2加载到寄存器R1中 
    ldr r2, [r0]      @ 将R0所指向地址中存放的0x3加载到寄存器R2中  
    str r2, [r1, r2]  @ 取址模式：基于偏移量。R2寄存器中的值0x3被存放到R1寄存器的值加R2寄存器的值所指向地址处。R1寄存器不会被修改。 
    str r2, [r1, r2]! @ 取址模式：基于索引前置修改。R2寄存器中的值0x3被存放到R1寄存器的值加R2寄存器的值所指向地址处，之后R1寄存器中的值被更新,也就是R1=R1+R2。
    ldr r3, [r1], r2  @ 取址模式：基于索引后置修改。R3寄存器中的值是从R1寄存器的值所指向的地址中加载的，加载之后R1寄存器中的值被更新也就是R1=R1+R2。
    bx lr
adr_var1: .word var1
adr_var2: .word var2
```

下面来分别调试这三条关键指令。在执行完基于偏移量的取址模式的STR操作后，R2的值被存在了地址0x1009c + 0x3 = 0x1009F处。下面一段是执行完对应STR操作后对应内存位置的值。



```
gef&gt; x/w 0x0001009F
 0x1009f &lt;var2+3&gt;: 0x00000003
```

下一条STR操作使用了基于索引前置修改的取址模式，R1的值被更新为R1+R2的值。下面一段是执行完对应STR操作后寄存器的值。



```
gef&gt; info register r1
 r1     0x1009f      65695
```

最后一个LDR操作使用了基于索引后置的取址模式。将R1指向的值加载到R2之后，更新了R1寄存器的值(R1+R2 = 0x1009f + 0x3 = 0x100a2)。下面一段是执行完对应LDR操作后对应内存位置以及寄存器的值。



```
gef&gt; info register r1
 r1      0x100a2     65698
gef&gt; info register r3
 r3      0x3       3
```

下图是这个操作发生的动态示意图。

[![](https://p4.ssl.qhimg.com/t0103caa85b564f13e5.gif)](https://p4.ssl.qhimg.com/t0103caa85b564f13e5.gif)

<br>

**第三种偏移形式：寄存器缩放值作偏移**



```
LDR    Ra, [Rb, Rc, &lt;shifter&gt;]
STR    Ra, [Rb, Rc, &lt;shifter&gt;]
```

在这种偏移形式下，第三个偏移量还有一个寄存器做支持。Rb是基址寄存器，Rc中的值作为偏移量，或者是要被左移或右移的次的值。这意味着移位器shifter被用来用作缩放Rc寄存器中存放的偏移量。下面的样例代码展示了对一个数组的循环操作。同样的，我们也会用GDB调试这段代码。



```
.data
var1: .word 3
var2: .word 4
.text
.global _start
_start:
    ldr r0, adr_var1         @ 将存放var1值的地址adr_var1加载到寄存器R0中 
    ldr r1, adr_var2         @ 将存放var2值的地址adr_var2加载到寄存器R1中 
    ldr r2, [r0]             @ 将R0所指向地址中存放的0x3加载到寄存器R2中  
    str r2, [r1, r2, LSL#2]  @ 取址模式：基于偏移量。R2寄存器中的值0x3被存放到R1寄存器的值加(左移两位后的R2寄存器的值)所指向地址处。R1寄存器不会被修改。
    str r2, [r1, r2, LSL#2]! @ 取址模式：基于索引前置修改。R2寄存器中的值0x3被存放到R1寄存器的值加(左移两位后的R2寄存器的值)所指向地址处，之后R1寄存器中的值被更新,也就R1 = R1 + R2&lt;&lt;2。
    ldr r3, [r1], r2, LSL#2  @ 取址模式：基于索引后置修改。R3寄存器中的值是从R1寄存器的值所指向的地址中加载的，加载之后R1寄存器中的值被更新也就是R1 = R1 + R2&lt;&lt;2。
    bkpt
adr_var1: .word var1
adr_var2: .word var2
```

下面来分别调试这三条关键指令。在执行完基于偏移量的取址模式的STR操作后，R2被存储到的位置是[r1,r2,LSL#2]，也就是说被存储到R1+(R2&lt;&lt;2)的位置了，如下图所示。

[![](https://p3.ssl.qhimg.com/t01cd63de08fe83550b.png)](https://p3.ssl.qhimg.com/t01cd63de08fe83550b.png)

下一条STR操作使用了基于索引前置修改的取址模式，R1的值被更新为R1+(R2&lt;&lt;2)的值。下面一段是执行完对应STR操作后寄存器的值。



```
gef&gt; info register r1
r1      0x100a8      65704
```

最后一个LDR操作使用了基于索引后置的取址模式。将R1指向的值加载到R2之后，更新了R1寄存器的值(R1+R2 = 0x100a8 + (0x3&lt;&lt;2) = 0x100b4)。下面一段是执行完对应LDR操作后寄存器的值。



```
gef&gt; info register r1
r1      0x100b4      65716
```



**小结**

LDR/STR的三种偏移模式：

立即数作为偏移

```
ldr   r3, [r1, #4]
```

寄存器作为偏移

```
ldr   r3, [r1, r2]
```

寄存器缩放值作为偏移

```
ldr   r3, [r1, r2, LSL#2]
```

如何区分取址模式：

如果有一个叹号!，那就是索引前置取址模式，即使用计算后的地址，之后更新基址寄存器。



```
ldr   r3, [r1, #4]!
ldr   r3, [r1, r2]!
ldr   r3, [r1, r2, LSL#2]!
```

如果在[]外有一个寄存器，那就是索引后置取址模式，即使用原有基址寄存器重的地址，之后再更新基址寄存器



```
ldr   r3, [r1], #4
ldr   r3, [r1], r2
ldr   r3, [r1], r2, LSL#2
```

除此之外，就都是偏移取址模式了



```
ldr   r3, [r1, #4]
ldr   r3, [r1, r2]
ldr   r3, [r1, r2, LSL#2]
```

地址模式：用作偏移

地址模式：前向索引

地址模式：后向索引

<br>

**关于PC相对取址的LDR指令**

有时候LDR并不仅仅被用来从内存中加载数据。还有如下这操作:



```
.section .text
.global _start
_start:
   ldr r0, =jump        /* 加载jump标签所在的内存位置到R0 */
   ldr r1, =0x68DB00AD  /* 加载立即数0x68DB00AD到R1 */
jump:
   ldr r2, =511         /* 加载立即数511到R2 */ 
   bkpt
```

这些指令学术上被称作伪指令。但我们在编写ARM汇编时可以用这种格式的指令去引用我们文字标识池中的数据。在上面的例子中我们用一条指令将一个32位的常量值放到了一个寄存器中。为什么我们会这么写是因为ARM每次仅仅能加载8位的值，原因倾听我解释立即数在ARM架构下的处理。

<br>

**在ARM中使用立即数的规律**

是的，在ARM中不能像X86那样直接将立即数加载到寄存器中。因为你使用的立即数是受限的。这些限制听上去有些无聊。但是听我说，这也是为了告诉你绕过这些限制的技巧(通过LDR)。

我们都知道每条ARM指令的宽度是32位，所有的指令都是可以条件执行的。我们有16中条件可以使用而且每个条件在机器码中的占位都是4位。之后我们需要2位来做为目的寄存器。2位作为第一操作寄存器，1位用作设置状态的标记位，再加上比如操作码(opcode)这些的占位。最后每条指令留给我们存放立即数的空间只有12位宽。也就是4096个不同的值。

这也就意味着ARM在使用MOV指令时所能操作的立即数值范围是有限的。那如果很大的话，只能拆分成多个部分外加移位操作拼接了。

所以这剩下的12位可以再次划分，8位用作加载0-255中的任意值，4位用作对这个值做0~30位的循环右移。这也就意味着这个立即数可以通过这个公式得到：v = n ror 2*r。换句话说，有效的立即数都可以通过循环右移来得到。这里有一个例子

有效值:



```
#256        // 1 循环右移 24位 --&gt; 256
#384        // 6 循环右移 26位 --&gt; 384
#484        // 121 循环右移 30位 --&gt; 484
#16384      // 1 循环右移 18位 --&gt; 16384
#2030043136 // 121 循环右移 8位 --&gt; 2030043136
#0x06000000 // 6 循环右移 8位 --&gt; 100663296 (十六进制值0x06000000)
Invalid values:
#370        // 185 循环右移 31位 --&gt; 31不在范围内 (0 – 30)
#511        // 1 1111 1111 --&gt; 比特模型不符合
#0x06010000 // 1 1000 0001.. --&gt; 比特模型不符合
```

看上去这样并不能一次性加载所有的32位值。不过我们可以通过以下的两个选项来解决这个问题：

用小部分去组成更大的值。

比如对于指令 MOV r0, #511

将511分成两部分：MOV r0, #256, and ADD r0, #255

用加载指令构造‘ldr r1,=value’的形式，编译器会帮你转换成MOV的形式，如果失败的话就转换成从数据段中通过PC相对偏移加载。

```
LDR r1, =511
```

如果你尝试加载一个非法的值，编译器会报错并且告诉你 invalid constant。如果在遇到这个问题，你现在应该知道该怎么解决了吧。唉还是举个栗子，就比如你想把511加载到R0。



```
.section .text
.global _start
_start:
    mov     r0, #511
    bkpt
```

这样做的结果就是编译报错:



```
azeria@labs:~$ as test.s -o test.o
test.s: Assembler messages:
test.s:5: Error: invalid constant (1ff) after fixup
```

你需要将511分成多部分，或者直接用LDR指令。



```
.section .text
.global _start
_start:
 mov r0, #256   /* 1 ror 24 = 256, so it's valid */
 add r0, #255   /* 255 ror 0 = 255, valid. r0 = 256 + 255 = 511 */
 ldr r1, =511   /* load 511 from the literal pool using LDR */
 bkpt
```

如果你想知道你能用的立即数的有效值，你不需要自己计算。我这有个小脚本，看你骨骼惊奇，传给你呦 [rotator.py](https://raw.githubusercontent.com/azeria-labs/rotator/master/rotator.py)。用法如下。



```
azeria@labs:~$ python rotator.py
Enter the value you want to check: 511
Sorry, 511 cannot be used as an immediate number and has to be split.
azeria@labs:~$ python rotator.py
Enter the value you want to check: 256
The number 256 can be used as a valid immediate number.
1 ror 24 --&gt; 256
```

**译者注：这作者真的是用心良苦，我都看累了，但是怎么说，反复练习加实践，总归是有好处的。**

**<br>**

****

传送门

[【系列分享】ARM 汇编基础速成1：ARM汇编以及汇编语言基础介绍](http://bobao.360.cn/learning/detail/4070.html)

**[【系列分享】ARM 汇编基础速成2：ARM汇编中的数据类型](http://bobao.360.cn/learning/detail/4075.html)**

[**【系列分享】ARM 汇编基础速成3：ARM模式与THUMB模式**](http://bobao.360.cn/learning/detail/4082.html)

**<br>**
