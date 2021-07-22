> 原文链接: https://www.anquanke.com//post/id/239860 


# 具有重金属风格的调试艺术：如何在IBM大型机上面进行逆向分析


                                阅读量   
                                **109199**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者f-secure，文章来源：f-secure.com
                                <br>原文地址：[https://labs.f-secure.com/blog/heavy-metal-debugging/﻿](https://labs.f-secure.com/blog/heavy-metal-debugging/%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01eb6ca2b6be0a439c.jpg)](https://p5.ssl.qhimg.com/t01eb6ca2b6be0a439c.jpg)



## 相关术语
- zOS：IBM的大型机操作系统；
- TSO：分时选择程序，用于对zOS系统进行交互式访问；
- PDS：zOS文件夹；
- HLASM：高级汇编语言，z/架构上的汇编语言；
- TSO TEST: 预装在zOS上的终端调试器，它并非真正用于逆向工程；
- AMBLIST: 用于映射加载模块和程序对象的批处理程序；
- JCL：作业控制语言，用于提交批处理程序；
- USS：Unix子系统，类似wsl，只不过运行在zOS上。


## 简介

在zOS系统上进行逆向工程时，会面临诸多挑战，其中最大的挑战是如何迈出第一步。

首先，zOS系统上可用的工具并不适合逆向工程，因为IBM创建它们的初衷，是为了调试应用程序。在本文中，我选择使用的应用程序是TSO TEST，因为它是免费的（前提是您能访问zOS，我是通过zPDT的许可副本来访问它的），并且会默认安装在每台IBM大型机上（甚至是TK4上面，它是20世纪80年代的开源zOS系统的前身）。

在如何使用TSO TEST和HLASM方面，IBM的文档介绍的相当详尽。然而，IBM并没有提供快速入门指南，所以需要花很多时间去翻阅IBM的文档；所以，本文就应运而生了，我们旨在提供一份逆向分析zOS应用程序的快速入门资料。



## 如何在zOS系统上编译和运行C程序

为了便于学习逆向分析技术，我们首先要准备好一个编译好的程序。为此，我们将以下面的示例代码为例，来演示如何编译和运行C程序；当然，这份代码中明显含有溢出漏洞。

```
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;

void special()
`{`
    printf ("H4CK3D TH3 M41NFR4M3");
`}`


int main()
`{`
    char buff[15];
    int pass = 0;

    printf("\n Enter the password : \n");
    gets(buff);

    if(strcmp(buff, "fsecure"))
    `{`
        printf ("\n Wrong Password \n");
    `}`
    else
    `{`
        printf ("\n Correct Password \n");
        pass = 1;
    `}`

    if(pass)
    `{`
        special();
    `}`

    return 0;
`}`
```

现在，我们有了C语言的源代码，接下来我们要对其进行编译。为此，这里将使用USS，因为我发现它比提交批处理JCL要更容易一些，但两者的作用是一样的。之后，目标文件被编译成一个MVS PDS数据集。

```
c89 -o "//'JAKE.TSOTEST.LOADE(OVERFLOW)'" overflow.c
```

下面是通过批处理文件运行的、用于编译、绑定和运行C程序的作业。

```
//COMPC  JOB (JOBNAME),'XSS',CLASS=A,NOTIFY=&amp;SYSUID
//PROC JCLLIB ORDER=(CBC.SCCNPRC)
//*-------------------------------------------------------------------
//* Compile and bind step
//*-------------------------------------------------------------------
//COMP     EXEC EDCCB,
//         OUTFILE='JAKE.TSOTEST.LOADE(OVERFLOW),DISP=SHR',
//         CPARM='ASM'
//STEPLIB  DD DSN=CBC.SCCNCMP,DISP=SHR
//         DD DSN=CEE.SCEERUN,DISP=SHR
//         DD DSN=CEE.SCEERUN2,DISP=SHR
//COMPILE.SYSIN DD DSN=JAKE.SOURCE.C(OVERFLOW),DISP=SHR
//*-------------------------------------------------------------------
//* Run step
//*-------------------------------------------------------------------
//GO       EXEC PGM=OVERFLOW
//STEPLIB  DD DSN=JAKE.TSOTEST.LOADE,DISP=SHR
```

现在，我们就可以通过TSO来调用该程序了。

```
call 'JAKE.TSOTEST.LOADE(OVERFLOW)'

  Enter the password : 
testtest

  Wrong Password
```

要对该程序进行静态分析，可以使用AMBLIST；同样，我们也可以利用批处理方式来运行它，不过，使用USS命令会更简单一些。

```
echo " LISTLOAD OUTPUT=MAP MEMBER=(OVERFLOW)" | amblist "//'JAKE.TSOTEST.LOADE'" &gt; /tmp/overflow_amblist
```

同样，下面的JCL用于处理同样的事情，只不过它使用了批处理方式。

```
//AMBLIST JOB (ACCT),MSGCLASS=H,NOTIFY=&amp;SYSUID
//AMBL       EXEC   PGM=AMBLIST,REGION=64M
//SYSPRINT   DD     DSN=JAKE.AMBLIST(OVERFLOW),DISP=OLD
//AMBLIB     DD     DSN=JAKE.TSOTEST.LOADE,DISP=SHR
//SYSIN      DD     *
    LISTLOAD  DDN=AMBLIB,OUTPUT=MAP,MEMBER=OVERFLOW
/*

```

实际上，这些输出内容是非常冗长的，但这里仅摘录了重要信息的片段，例如使用了哪些外部函数，以及函数在编译后的overflow.c二进制文件中的位置；这里显示的是关于SPECIAL和MAIN函数的信息。

```
-**    END OF MAP AND CROSS-REFERENCE LISTING                                                                            
1                                  *  M O D U L E   S U M M A R Y  *                                             
0    MEMBER NAME:  OVERFLOW                                                               MAIN ENTRY POINT:    00000000  
0    LIBRARY:      SYSLIB                                                                 AMODE OF MAIN ENTRY POINT: 31  

-                 CONTROL SECTION                                        ENTRY                                           
                   LMOD LOC     NAME      LENGTH  TYPE  RMODE             LMOD LOC  CSECT LOC      NAME                                
                       A0    @ST00001       348   SD    31                                                              
                                                                              138        98      SPECIAL                 
                                                                              1B8       118      MAIN
                       338    CEEMAIN         0C   SD    31                                                                        
                      15A8    gets            0A   SD    31                                                              
                                                                             15A8        00      GETS                            
0                     15B8    printf          0A   SD    31                                                              
                                                                             15B8        00      PRINTF                                                    
0LENGTH OF LOAD MODULE    1D58
```

现在开始实际调试；为此，可以从TSO运行下面的命令：

```
test 'JAKE.TSOTEST.LOADE(OVERFLOW)'
```

现在，我们位于TEST终端；要想离开该终端，可以键入“end”命令。当我们被一条指令卡住的时候，可以按PA1来取消该指令。



## TSO测试指南

下面是一个TSO测试的例子。

[![](https://p1.ssl.qhimg.com/t01d235bfa490c36d7e.png)](https://p1.ssl.qhimg.com/t01d235bfa490c36d7e.png)

在TEST中，有多种方法来表示地址：
- 15r：寄存器15中的地址；
- OVERFLOW.MAIN：使用符号表示地址；
- +12：相对于基地址的偏移量（以字节为单位；同时，可以使用qualify来改变基地址）；以入口点为起始位置；
- 1FAA12F8：绝对地址。
另外，下面是常用的TEST子命令，我们最好熟悉一下：
<li>
`LIST &lt;ADDRESS&gt; &lt;DATA_TYPE&gt; m(&lt;multiple&gt;)`<br>
其中，比较重要的数据类型为i（指令）、b（二进制）、x（十六进制）、c（字符），这里的m表示想显示多少种数据类型。</li>
<li>
`LISTPSW`<br>
显示PSW，以查看条件标志。</li>
<li>
`AT &lt;ADDRESS&gt; , AT &lt;ADDRESS:ADDRESS&gt;`<br>
在一个地址或多个地址上设置断点；对于多个地址，对应位置存放的必须都是指令。</li>
<li>`off &lt;address&gt; , off &lt;address:address&gt;.<br>
删除断点</li>
<li>GO<br>
运行程序，直到出现断点为止。</li>
<li>
`QUALIFY &lt;ADDRESS&gt;`<br>
改变基地址。</li>
<li>
`WHERE`<br>
输出当前位置以及您所在的函数。</li>


## 逆向分析之旅

### <a class="reference-link" name="%E5%AF%BB%E6%89%BE%E5%AF%86%E7%A0%81"></a>寻找密码

以下是HLASM中的寄存器的典型用途：
- 寄存器1→参数列表指针
- 寄存器13→指向调用方提供的寄存器保存区的指针
- 寄存器14→返回地址
- 寄存器15→子程序的地址
首先，我们需要在MAIN函数处设置一个断点并跳转到该函数。同时，让我们修改一下基地址，具体如下所示：

```
at OVERFLOW.MAIN
go
qualify OVERFLOW.MAIN
```

让我们看看接下来要运行哪个指令：

```
list +0 i
        +0    BC      15,36(,R15)
```

TSO TEST在显示指令时，竟然使用了十进制，但地址通常都是用十六进制表示的。这说明这是一个条件分支指令，掩码1111（总是这个值）用于处理0x24+寄存器15的值。所以，让我们将基地址设为从main函数的起始地址+24字节处，并显示main函数中的所有汇编指令。

```
qualify +24
list +0 i m(200)
        +0    STM     R14,R5,12(R13)
        +4    L       R14,76(,R13)
        +8    LA      R0,208(,R14)
        +C    CL      R0,788(,R12)
       +10    BRC     2,*-32
       +14    L       R15,640(,R12)
       +18    STM     R15,R0,72(R14)
       +1C    MVI     0(R14),16
       +20    ST      R13,4(,R14)
       +24    LR      R13,R14
       +26    LARL    R3,*+210
       +2C    LARL    R5,*+216
       +32    MVHI    176(R13),0
       +38    L       R15,0(,R3)
       +3C    LA      R0,22(,R5)
       +40    LA      R1,152(,R13)
       +44    ST      R0,152(,R13)
       +48    BASR    R14,R15
       +4A    LA      R0,160(,R13)
       +4E    L       R15,4(,R3)
       +52    LA      R1,152(,R13)
       +56    ST      R0,152(,R13)
       +5A    BASR    R14,R15
       +5C    LA      R2,160(,R13)
       +60    LA      R1,48(,R5)
       +64    LA      R0,0
       +68    CLST    R2,R1
       +6C    LA      R0,0
       +70    ST      R2,180(,R13)
       +74    ST      R1,184(,R13)
       +78    ST      R0,188(,R13)
       +7C    BRC     8,*+30
       +80    L       R2,180(,R13)
       +84    L       R1,184(,R13)
       +88    LLC     R0,0(,R2)
       +8E    LLC     R1,0(,R1)
       +94    SLR     R0,R1
       +96    ST      R0,188(,R13)
       +9A    L       R0,188(,R13)
       +9E    LTR     R0,R0
       +A0    BRC     8,*+26
       +A4    L       R15,0(,R3)
       +A8    LA      R0,56(,R5)
       +AC    LA      R1,152(,R13)
       +B0    ST      R0,152(,R13)
       +B4    BASR    R14,R15
       +B6    BRC     15,*+28
       +BA    L       R15,0(,R3)
       +BE    LA      R0,76(,R5)
       +C2    LA      R1,152(,R13)
       +C6    ST      R0,152(,R13)
       +CA    BASR    R14,R15
       +CC    MVHI    176(R13),1
       +D2    L       R0,176(,R13)
       +D6    LTR     R0,R0
       +D8    BRC     8,*+10
       +DC    L       R15,8(,R3)
       +E0    BASR    R14,R15
       +E2    LA      R15,0
       +E6    LR      R0,R13
       +E8    L       R13,4(,R13)
       +EC    L       R14,12(,R13)
       +F0    LM      R2,R5,28(R13)
       +F4    BALR    R1,R14
       +F6    BCR     0,R7
       +F8    SLR     R10,R0
       +FA    LDR     FR6,FR0
       +FC    SLR     R10,R0
       +FE    LDR     FR5,FR0
      +100    SLR     R10,R0
      +102    LCR     R3,R0
      +104    LPD     R15,978(R12),964(R15)
      +10A    STH     R14,2291(R3,R12)
      +10E    STH     R13,1265(R4,R15)
      +112    CLC     2548(199,R13),1267(R13)
 IKJ57245I INVALID INSTRUCTION CODE AT +118
```

为了更好地理解程序中发生的事情，让我们看看对外部函数的调用。下面的代码的意思是跳转到寄存器15中存放的地址处，并将函数的返回存储在寄存器14中。

```
+48 BASR R14,R15
```

所以，让我们在这个地址上设一个断点，并找出寄存器15中的内容。

```
at +48
go
list 15r
 15R  1FA02860
```

好了，我们知道它跳转到什么位置了，现在设置一个断点，然后运行“where”指令，来看看最后进入哪个函数中。

```
at 1FA02860.
go
where
  1FA02860. LOCATED AT +0      IN OVERFLOW.printf   UNDER TCB LOCATED AT 8B9E88.
```

所以，我们知道这是printf函数，为此，可以在下一个地址处设置一个断点，以便进行相应的验证。

```
at +4A
go
  Enter the password :
```

让我们对下一个函数做同样的处理，我们的研究发现，会进行如下所示的函数调用：

```
+5A    BASR    R14,R15
```

接下来的C函数称为strcmp，它的情况略有不同。实际上，HLASM有点像CISC，它有一条用于比较字符串的汇编指令“CLST”，如果字符串相同，则设置条件代码。下面的汇编代码显示了要比较的字符串，如果它们相等，就进行条件分支转移。

```
+68    CLST    R2,R1
+6C    LA      R0,0
+70    ST      R2,180(,R13)
+74    ST      R1,184(,R13)
+78    ST      R0,188(,R13)
+7C    BRC     8,*+30
```

让我们在CLST指令上设置断点，以便看看正在比较的两个字符串。

```
at +68
list 1r:2r
  1R  1FA01508   2R  1FAA02E8


list 1FA01508. c m(30)
 1FA01508.  f                     
 1FA01509.  s
 1FA0150A.  e
 1FA0150B.  c
 1FA0150C.  u
 1FA0150D.  r
 1FA0150E.  e
 1FA0150F.  .

list 1FAA02E8. c m(30)
 1FAA02E8.  a               
 1FAA02E9.  b
 1FAA02EA.  c
 1FAA02EB.  d
```

从这里我们看到，它将我们输入的字符串“abcd”与“fsecure”字符串进行了比较。

让我们再次调用该程序，并尝试将fsecure作为输入的密码。

```
call 'JAKE.TSOTEST.LOADE(OVERFLOW)'

  Enter the password : 
fsecure

  Correct Password 
 H4CK3D TH3 M41NFR4M3
```

### <a class="reference-link" name="%E7%BC%93%E5%86%B2%E5%8C%BA%E6%BA%A2%E5%87%BA"></a>缓冲区溢出

现在，让我们看看如何在没有输入正确的密码的情况下，如何攻破这个大型机。显然，这里将利用缓冲区利用漏洞，不过在此之前，先让我们看看它在HLASM中是如何工作的。

为此，我们可以在main函数的每条指令上设置一个断点。这样的话，输入go指令，就能实现单步跳过（step over）功能。

```
at +0:+112
```

注意下面的指令，无论密码是错是对，它都会被运行。MVHI是“MoVe fullword from Halfword Immediate”的意思，并将pass的值设置为0，随后如果程序将该内存加载到寄存器中，运行“LTR”来加载并测试寄存器，将第二个寄存器的值放入第一个寄存器，并检查其内容是否为0。

```
+32    MVHI    176(R13),0
...
+D2    L       R0,176(,R13)
+D6    LTR     R0,R0
```

如果密码正确，就将该变量的值设置为1。

```
+CC    MVHI   176(R13),1
```

然后，让我们转到D2，来看看寄存器13的值是多少。

```
at +D2 
go
list 13r
 13R  1FAA1248
```

现在，让我们让1FAA1248与176相加，得到1FAA12F8，并查看这个地址所在的二进制到代码。正如我们所看到的，当密码输入正确时，该值被设置为1。

```
list 1FAA12F8. B m(4)
 1FAA12F8.  00000000    
 1FAA12F9.  00000000
 1FAA12FA.  00000000
 1FAA12FB.  00000001
```

从上一节我们知道，我们获取的数据存储在1FAA12E8处。由于每个字符占1个字节，所以要覆盖这个数据，我们需要由1FAA12FB – 1FAA12E8 = 20个字符组成的密码。

```
call 'JAKE.TSOTEST.LOADE(OVERFLOW)'

  Enter the password : 
aaaaaaaaaaaaaaaaaaaa

  Wrong Password 
 H4CK3D TH3 M41NFR4M3
```

注意事项1：在整个过程中，绝对地址可能已经改变了。

注意事项2：zOS编译器似乎没有实现金丝雀、ASLR或NX位等内存保护机制，但虚拟地址的工作方式为zOS提供了很多保护。对于大多数地址间的通信，用户都被要求处于Modeset 0状态，这是一个用户可以拥有的最大特权。面是关于zOS的虚拟内存映射的进一步信息，请参阅[http://zseries.marist.edu/pdfs/ztidbitz/29%20zNibbler%20%28zOS%27%20Address%20Space%20%20-%20Virtual%20Storage%20Layout%29.pdf。](http://zseries.marist.edu/pdfs/ztidbitz/29%20zNibbler%20%28zOS%27%20Address%20Space%20%20-%20Virtual%20Storage%20Layout%29.pdf%E3%80%82)

注意事项3：zOS系统并没有提供堆栈。按照惯例，zOS系统上的C和其他IBM编译器，会创建相应的DSA（https://www.ibm.com/docs/en/zos/2.2.0?topic=conventions-language-environment-dynamic-storage-area-non-xplink），就像其他系统中的每个函数都有一个堆栈一样。



## 未来的工作

为了实现权限升级，我们将需要滥用管理程序状态。在zOS系统上，这可以通过某些方法来实现，即SVC、APF库和跨内存服务。在接下来的文章中，将介绍如何利用这些方法实现提权。



## 参考资料

POoP（操作原则）：
- Introduction to Assembler Programming SHARE Boston 2013
- Mainframe [z/OS] reverse engineering and exploit development