> 原文链接: https://www.anquanke.com//post/id/86434 


# 【系列分享】ARM 汇编基础速成7：栈与函数


                                阅读量   
                                **192132**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：azeria-labs.com
                                <br>原文地址：[ https://azeria-labs.com/functions-and-the-stack-part-7/](https://azeria-labs.com/functions-and-the-stack-part-7/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0151ebcaed6e2f5317.png)](https://p4.ssl.qhimg.com/t0151ebcaed6e2f5317.png)



译者：[arnow117](http://bobao.360.cn/member/contribute?uid=941579989)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

传送门

[【系列分享】ARM 汇编基础速成1：ARM汇编以及汇编语言基础介绍](http://bobao.360.cn/learning/detail/4070.html)

[【系列分享】ARM 汇编基础速成2：ARM汇编中的数据类型](http://bobao.360.cn/learning/detail/4075.html)

[【系列分享】ARM 汇编基础速成3：ARM模式与THUMB模式](http://bobao.360.cn/learning/detail/4082.html)

[【系列分享】ARM 汇编基础速成4：ARM汇编内存访问相关指令](http://bobao.360.cn/learning/detail/4087.html)

[【系列分享】ARM 汇编基础速成5：连续存取](http://bobao.360.cn/learning/detail/4097.html)

[**【系列分享】ARM 汇编基础速成6：条件执行与分支**](http://bobao.360.cn/learning/detail/4104.html)

<br>

在这部分我们将研究一篇独特的内存区域叫做栈，讲解栈的目的以及相关操作。除此之外，我们还会研究ARM架构中函数的调用约定。

<br>

**栈**

一般来说，栈是一片在程序/进程中的内存区域。这部分内存是在进程创建的时候被创建的。我们利用栈来存储一些临时数据比如说函数的局部变量，环境变量等。在之前的文章中，我们讲了操作栈的相关指令PUSH和POP。

在我们开始之前，还是了解一下栈的相关知识以及其实现方式吧。首先谈谈栈的增长，即当我们把32位的数据放到栈上时候它的变化。栈可以向上增长(当栈的实现是负向增长时)，或者向下增长(当栈的实现是正向增长时)。具体的关于下一个32位的数据被放到哪里是由栈指针来决定的，更精确的说是由SP寄存器决定。不过这里面所指向的位置，可能是当前(也就是上一次)存储的数据，也可能是下一次存储时的位置。如果SP当前指向上一次存放的数据在栈中的位置(满栈实现)，SP将会递减(降序栈)或者递增(升序栈)，然后再对指向的内容进行操作。而如果SP指向的是下一次要操作的数据的空闲位置(空栈实现)，数据会先被存放，而后SP会被递减(降序栈)或递增(升序栈)。

[![](https://p3.ssl.qhimg.com/t014590833dddab2d06.gif)](https://p3.ssl.qhimg.com/t014590833dddab2d06.gif)

不同的栈实现，可以用不同情形下的多次存取指令来表示(这里很绕…):

[![](https://p1.ssl.qhimg.com/t01992f4f147ff35a38.png)](https://p1.ssl.qhimg.com/t01992f4f147ff35a38.png)

我们的例子中，使用的是满栈降序的栈实现。让我们看一个栈相关的例子。



```
/* azeria@labs:~$ as stack.s -o stack.o &amp;&amp; gcc stack.o -o stack &amp;&amp; gdb stack */
.global main
main:
     mov   r0, #2  /* 设置R0 */
     push  `{`r0`}`    /* 将R0存在栈上 */
     mov   r0, #3  /* 修改R0 */
     pop   `{`r0`}`    /* 恢复R0为初始值 */
     bx    lr      /* 程序结束 */
```

在一开始，栈指针指向地址0xbefff6f8,代表着上一次入栈数据的位置。可以看到当前位置存储了一些值。



```
gef&gt; x/1x $sp
0xbefff6f8: 0xb6fc7000
```

在执行完第一条指令MOV后，栈没有改变。在只执行完下一条PUSH指令后，首先SP的值会被减4字节。之后存储在R0中的值会被存放到SP指向的位置中。现在我们在看看SP指向的位置以及其中的值。



```
gef&gt; x/x $sp
0xbefff6f4: 0x00000002
```

之后的指令将R0的值修改为3。然后我们执行POP指令将SP中的值存放到R0中，并且将SP的值加4，指向当前栈顶存放数据的位置。z最终R0的值是2。



```
gef&gt; info registers r0
r0       0x2          2
```

(下面的动图展示了低地址在顶部的栈的变化情况)

[![](https://p1.ssl.qhimg.com/t018545d02c878c205c.gif)](https://p1.ssl.qhimg.com/t018545d02c878c205c.gif)

栈被用来存储局部变量，之前的寄存器状态。为了统一管理，函数使用了栈帧这个概念，栈帧是在栈内用于存储函数相关数据的特定区域。栈帧在函数开始时被创建。栈帧指针(FP)指向栈帧的底部元素，栈帧指针确定后，会在栈上申请栈帧所属的缓冲区。栈帧(从它的底部算起)一般包含着返回地址(之前说的LR)，上一层函数的栈帧指针，以及任何需要被保存的寄存器，函数参数(当函数需要4个以上参数时)，局部变量等。虽然栈帧包含着很多数据，但是这其中不少类型我们之前已经了解过了。最后，栈帧在函数结束时被销毁。

下图是关于栈帧的在栈中的位置的抽象描述(默认栈，满栈降序):

[![](https://p3.ssl.qhimg.com/t01782dc78dba895411.png)](https://p3.ssl.qhimg.com/t01782dc78dba895411.png)

来一个例子来更具体的了解下栈帧吧:



```
/* azeria@labs:~$ gcc func.c -o func &amp;&amp; gdb func */
int main()
`{`
 int res = 0;
 int a = 1;
 int b = 2;
 res = max(a, b);
 return res;
`}`
int max(int a,int b)
`{`
 do_nothing();
 if(a&lt;b)
 `{`
 return b;
 `}`
 else
 `{`
 return a;
 `}`
`}`
int do_nothing()
`{`
 return 0;
`}`
```

在下面的截图中我们可以看到GDB中栈帧的相关信息:

[![](https://p1.ssl.qhimg.com/t0150390ed226a6f437.png)](https://p1.ssl.qhimg.com/t0150390ed226a6f437.png)

可以看到上面的图片中我们即将离开函数max(最下面的反汇编中可以看到)。在此时，FP(R11)寄存器指向的0xbefff254就是当前栈帧的底部。这个地址对应的栈上(绿色地址区域)位置存储着0x00010418这个返回地址(LR)。再往上看4字节是0xbefff26c。可以看到这个值是上层函数的栈帧指针。在0xbefff24c和0xbefff248的0x1和0x2是函数max执行时产生的局部变量。所以栈帧包含着我们之前说过的LR，FP以及两个局部变量。



**函数**

在开始学习ARM下的函数前，我们需要先明白一个函数的结构:

序言准备(Prologue)

函数体

结束收尾(Epilogue)

序言的目的是为了保存之前程序的执行状态(通过存储LR以及R11到栈上)以及设定栈以及局部函数变量。这些的步骤的实现可能根据编译器的不同有差异。通常来说是用PUSH/ADD/SUB这些指令。举个例子:



```
push   `{`r11, lr`}`    /* 保存R11与LR */
add    r11, sp, #4  /* 设置栈帧底部,PUSH两个寄存器,SP加4后指向栈帧底部元素 */
sub    sp, sp, #16  /* 在栈上申请相应空间 */
```

函数体部分就是函数本身要完成的任务了。这部分包括了函数自身的指令，或者跳转到其它函数等。下面这个是函数体的例子。



```
mov    r0, #1       /* 设置局部变量(a=1),同时也是为函数max准备参数a */
mov    r1, #2       /* 设置局部变量(b=2),同时也是为函数max准备参数b */
bl     max          /* 分支跳转调用函数max */
```

上面的代码也展示了调用函数前需要如何准备局部变量，以为函数调用设定参数。一般情况下，前四个参数通过R0-R3来传递，而多出来的参数则需要通过栈来传递了。函数调用结束后，返回值存放在R0寄存器中。所以不管max函数如何运作，我们都可以通过R0来得知返回值。而且当返回值位64位值时，使用的是R0与R1寄存器一同存储64位的值。

函数的最后一部分即结束收尾，这一部分主要是用来恢复程序寄存器以及回到函数调用发生之前的状态。我们需要先恢复SP栈指针，这个可以通过之前保存的栈帧指针寄存器外加一些加减操作做到(保证回到FP,LR的出栈位置)。而当我们重新调整了栈指针后，我们就可以通过出栈操作恢复之前保存的寄存器的值。基于函数类型的不同，POP指令有可能是结束收尾的最后一条指令。然而，在恢复后我们可能还需要通过BX指令离开函数。一个收尾的样例代码是这样的。



```
sub    sp, r11, #4  /* 收尾操作开始，调整栈指针，有两个寄存器要POP，所以从栈帧底部元素再减4 */
pop    `{`r11, pc`}`    /* 收尾操作结束。恢复之前函数的栈帧指针，以及通过之前保存的LR来恢复PC。 */
```

总结一下：

序言设定函数环境

函数体实现函数逻辑功能，将结果存到R0

收尾恢复程序状态，回到调用发生的地方。

关于函数，有一个关键点我们要知道，函数的类型分为叶函数以及非叶函数。叶函数是指函数中没有分支跳转到其他函数指令的函数。非叶函数指包含有跳转到其他函数的分支跳转指令的函数。这两种函数的实现都很类似，当然也有一些小不同。这里我们举个例子来分析一下:



```
/* azeria@labs:~$ as func.s -o func.o &amp;&amp; gcc func.o -o func &amp;&amp; gdb func */
.global main
main:
    push   `{`r11, lr`}`    /* Start of the prologue. Saving Frame Pointer and LR onto the stack */
    add    r11, sp, #4  /* Setting up the bottom of the stack frame */
    sub    sp, sp, #16  /* End of the prologue. Allocating some buffer on the stack */
    mov    r0, #1       /* setting up local variables (a=1). This also serves as setting up the first parameter for the max function */
    mov    r1, #2       /* setting up local variables (b=2). This also serves as setting up the second parameter for the max function */
    bl     max          /* Calling/branching to function max */
    sub    sp, r11, #4  /* Start of the epilogue. Readjusting the Stack Pointer */
    pop    `{`r11, pc`}`    /* End of the epilogue. Restoring Frame pointer from the stack, jumping to previously saved LR via direct load into PC */
max:
    push   `{`r11`}`        /* Start of the prologue. Saving Frame Pointer onto the stack */
    add    r11, sp, #0  /* 设置栈帧底部,PUSH一个寄存器,SP加0后指向栈帧底部元素 */
    sub    sp, sp, #12  /* End of the prologue. Allocating some buffer on the stack */
    cmp    r0, r1       /* Implementation of if(a&lt;b) */
    movlt  r0, r1       /* if r0 was lower than r1, store r1 into r0 */
    add    sp, r11, #0  /* 收尾操作开始，调整栈指针，有一个寄存器要POP，所以从栈帧底部元素再减0 */
    pop    `{`r11`}`        /* restoring frame pointer */
    bx     lr           /* End of the epilogue. Jumping back to main via LR register */
```

上面的函数main以及max函数，一个是非叶函数另一个是叶函数。就像之前说的非叶函数中有分支跳转到其他函数的逻辑，函数max中没有在函数体逻辑中包含有这类代码，所以是叶函数。

除此之外还有一点不同是两类函数序言与收尾的实现是有差异的。来看看下面这段代码，是关于叶函数与非叶函数的序言部分的差异的:



```
/* A prologue of a non-leaf function */
push   `{`r11, lr`}`    /* Start of the prologue. Saving Frame Pointer and LR onto the stack */
add    r11, sp, #4  /* Setting up the bottom of the stack frame */
sub    sp, sp, #16  /* End of the prologue. Allocating some buffer on the stack */
/* A prologue of a leaf function */
push   `{`r11`}`        /* Start of the prologue. Saving Frame Pointer onto the stack */
add    r11, sp, #0  /* Setting up the bottom of the stack frame */
sub    sp, sp, #12  /* End of the prologue. Allocating some buffer on the stack */
```

一个主要的差异是，非叶函数需要在栈上保存更多的寄存器，这是由于非叶函数的本质决定的，因为在执行时LR寄存器会被修改，所以需要保存LR寄存器以便之后恢复。当然如果有必要也可以在序言期保存更多的寄存器。

下面这段代码可以看到，叶函数与非叶函数在收尾时的差异主要是在于，叶函数的结尾直接通过LR中的值跳转回去就好，而非叶函数需要先通过POP恢复LR寄存器，再进行分支跳转。



```
/* An epilogue of a leaf function */
add    sp, r11, #0  /* Start of the epilogue. Readjusting the Stack Pointer */
pop    `{`r11`}`        /* restoring frame pointer */
bx     lr           /* End of the epilogue. Jumping back to main via LR register */
/* An epilogue of a non-leaf function */
sub    sp, r11, #4  /* Start of the epilogue. Readjusting the Stack Pointer */
pop    `{`r11, pc`}`    /* End of the epilogue. Restoring Frame pointer from the stack, jumping to previously saved LR via direct load into PC */
```

最后，我们要再次强调一下在函数中BL和BX指令的使用。在我们的示例中，通过使用BL指令跳转到叶函数中。在汇编代码中我们使用了标签，在编译过程中，标签被转换为对应的内存地址。在跳转到对应位置之前，BL会将下一条指令的地址存储到LR寄存器中这样我们就能在函数max完成的时候返回了。

BX指令在被用在我们离开一个叶函数时，使用LR作为寄存器参数。刚刚说了LR存放着函数调用返回后下一条指令的地址。由于叶函数不会在执行时修改LR寄存器，所以就可以通过LR寄存器跳转返回到main函数了。同样BX指令还会帮助我们切换ARM/Thumb模式。同样这也通过LR寄存器的最低比特位来完成，0代表ARM模式，1代表Thumb模式。

最后，这张动图阐述了非叶函数调用叶函数时候的内部寄存器的工作状态。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0154458b040cfb4749.gif)

**原作者在后续叶函数和非叶函数相关样例代码中将设置与恢复栈帧指针时的偏移写错了，根据栈帧设置的逻辑已经修复。**

**<br>**

****

传送门

[【系列分享】ARM 汇编基础速成1：ARM汇编以及汇编语言基础介绍](http://bobao.360.cn/learning/detail/4070.html)

[【系列分享】ARM 汇编基础速成2：ARM汇编中的数据类型](http://bobao.360.cn/learning/detail/4075.html)

[【系列分享】ARM 汇编基础速成3：ARM模式与THUMB模式](http://bobao.360.cn/learning/detail/4082.html)

[【系列分享】ARM 汇编基础速成4：ARM汇编内存访问相关指令](http://bobao.360.cn/learning/detail/4087.html)

[【系列分享】ARM 汇编基础速成5：连续存取](http://bobao.360.cn/learning/detail/4097.html)

[**【系列分享】ARM 汇编基础速成6：条件执行与分支**](http://bobao.360.cn/learning/detail/4104.html)

**<br>**
