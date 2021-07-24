> 原文链接: https://www.anquanke.com//post/id/149782 


# linux_ptmalloc下malloc()的过程：有 ptmalloc 源码


                                阅读量   
                                **140635**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01ab22ed40c453714a.jpg)](https://p1.ssl.qhimg.com/t01ab22ed40c453714a.jpg)

## 文章描述

本文将尽量详细地给出 ptmalloc 下调用 malloc() 进行内存分配的实现过程

### <a class="reference-link" name="__libc_malloc()%20%E5%92%8C%20_int_malloc()"></a>__libc_malloc() 和 _int_malloc()

实际上，在glibc中没有 malloc(), 只能找到 __libc_malloc() 和 _int_malloc(),而 _int_malloc()才是进行内存分配的函数

### __libc_malloc()

对 _int_malloc() 的简单封装
1. 检查是否有内存分配钩子
1. 寻找 arena 来分配内存： arena_get(ar_ptr, bytes);
1. 调用 _int_malloc() （进行内存的分配）：victim = _int_malloc(ar_ptr, bytes);


## 特殊情况的处理

### 找不到可以用的 arena

<a class="reference-link" name="_int_malloc()"></a>_int_malloc()

> 进行内存分配的核心函数
1. 根据请求内存块的大小以及对应大小的 chunk 所在的 bins/bin 实现了不同的分配算法
1. 检查 空闲chunk 能否符合需要，符合则分配
1. 如果所有的 空闲chunk 都不能符合需要，会进行一系列操作，如合并chunk，考虑 top chunk
1. 当 top chunk 也无法满足时，向操作系统申请内存
<a class="reference-link" name="_int_malloc()%20%E7%9A%84%E5%8F%98%E9%87%8F"></a>_int_malloc() 的变量

```
static void *_int_malloc(mstate av, size_t bytes) `{`
    INTERNAL_SIZE_T nb;  /* normalized request size */
    unsigned int    idx; /* associated bin index */
    mbinptr         bin; /* associated bin */

    mchunkptr       victim;       /* inspected/selected chunk */
    INTERNAL_SIZE_T size;         /* its size */
    int             victim_index; /* its bin index */

    mchunkptr     remainder;      /* remainder from a split */
    unsigned long remainder_size; /* its size */

    unsigned int block; /* bit map traverser */
    unsigned int bit;   /* bit map traverser */
    unsigned int map;   /* current word of binmap */

    mchunkptr fwd; /* misc temp for linking */
    mchunkptr bck; /* misc temp for linking */

    const char *errstr = NULL;

    /*
       Convert request size to internal form by adding SIZE_SZ bytes
       overhead plus possibly more to obtain necessary alignment and/or
       to obtain a size of at least MINSIZE, the smallest allocatable
       size. Also, checked_request2size traps (returning 0) request sizes
       that are so large that they wrap around zero when padded and
       aligned.
     */

    checked_request2size(bytes, nb);
```

fast bin 和 small bin 分配图[![](https://p0.ssl.qhimg.com/t018064f1be191220ca.jpg)](https://p0.ssl.qhimg.com/t018064f1be191220ca.jpg)

<a class="reference-link" name="fast%20bin:LIFO"></a>fast bin:LIFO

> 如果申请的内存在 fast bin 范围内
1. 获得对应的 fast bin 的下标： idx
1. 获得对应的 fast bin 的头指针：fb
<li>遍历对应的 fast bin ，检查是否有空闲chunk：
<ul>
1. 如果有空闲chunk，检查该 空闲chunk 的大小与索引是否一致
1. 如果没有空闲chunk，去对应的 small bin 中寻找，如果 small bin 中也没有，则进入大循环
</ul>
</li>
1. 有空闲chunk，获得 头部chunk指针，检查其大小是否符合在对应 fast bin 的范围
1. 大小符合将其取出，并将获得的 chunk 转换为 mem模式
1. 如果设置了perturb_type, 则将获取到的chunk初始化为 perturb_type ^ 0xff
```
/*
       If the size qualifies as a fastbin, first check corresponding bin.
       This code is safe to execute even if av is not yet initialized, so we
       can try it without checking, which saves some time on this fast path.
     */

    if ((unsigned long) (nb) &lt;= (unsigned long) (get_max_fast())) `{`
        // 得到对应的fastbin的下标
        idx             = fastbin_index(nb);
        // 得到对应的fastbin的头指针
        mfastbinptr *fb = &amp;fastbin(av, idx);
        mchunkptr    pp = *fb;
        // 利用fd遍历对应的bin内是否有空闲的chunk块，
        do `{`
            victim = pp;
            if (victim == NULL) break;
        `}` while ((pp = catomic_compare_and_exchange_val_acq(fb, victim-&gt;fd,
                                                            victim)) != victim);
        // 存在可以利用的chunk
        if (victim != 0) `{`
            // 检查取到的 chunk 大小是否与相应的 fastbin 索引一致。
            // 根据取得的 victim ，利用 chunksize 计算其大小。
            // 利用fastbin_index 计算 chunk 的索引。
            if (__builtin_expect(fastbin_index(chunksize(victim)) != idx, 0)) `{`
                errstr = "malloc(): memory corruption (fast)";
            errout:
                malloc_printerr(check_action, errstr, chunk2mem(victim), av);
                return NULL;
            `}`
            // 细致的检查。。只有在 DEBUG 的时候有用
            check_remalloced_chunk(av, victim, nb);
            // 将获取的到chunk转换为mem模式
            void *p = chunk2mem(victim);
            // 如果设置了perturb_type, 则将获取到的chunk初始化为 perturb_type ^ 0xff
            alloc_perturb(p, bytes);
            return p;
        `}`
    `}`
```

<a class="reference-link" name="small%20bin:FIFO"></a>small bin:FIFO

> 如果申请的内存在 small bin 范围内
1. 获取对应的 small bin 的索引
1. 获取对应的 small bin 的头指针：bin
1. 获取对应的 small bin 中的最后一个 chunk 的指针： victim
<li>判断 bin 是否等于 victim
<ul>
<li>如果 bin == victim, 说明 small bin 为空
<ul>
1. 如果 bin!=victim, 则有两种情况:
1. small bin 还没有初始化：初始化，将 fast bins 中的 chunk 合并
1. small bin 有空闲chunk：
</ul>
</li>
</ul>
<ol>
<li>如果有空闲chunk：
<ul>
1. 获得倒数第二个chunk：bck=victim-&gt;bk
1. 检查bck-&gt;fd 是否为 victim, 防止伪造
1. 设置 victim 的 inuse位
1. unlink：将 victim 指向的 chunk 取下分配，并将获得的 chunk 转换为 mem模式
</ul>
</li>- 获得倒数第二个chunk：bck=victim-&gt;bk
- 检查bck-&gt;fd 是否为 victim, 防止伪造
- 设置 victim 的 inuse位
- unlink：将 victim 指向的 chunk 取下分配，并将获得的 chunk 转换为 mem模式
```
/*
       If a small request, check regular bin.  Since these "smallbins"
       hold one size each, no searching within bins is necessary.
       (For a large request, we need to wait until unsorted chunks are
       processed to find best fit. But for small ones, fits are exact
       anyway, so we can check now, which is faster.)
     */

    if (in_smallbin_range(nb)) `{`
        // 获取 small bin 的索引
        idx = smallbin_index(nb);
        // 获取对应 small bin 中的 chunk 指针
        bin = bin_at(av, idx);
        // 先执行 victim = last(bin)，获取 small bin 的最后一个 chunk
        // 如果 victim = bin ，那说明该 bin 为空。
        // 如果不相等，那么会有两种情况
        if ((victim = last(bin)) != bin) `{`
            // 第一种情况，small bin 还没有初始化。
            if (victim == 0) /* initialization check */
                // 执行初始化，将 fast bins 中的 chunk 进行合并
                malloc_consolidate(av);
            // 第二种情况，small bin 中存在空闲的 chunk
            else `{`
                // 获取 small bin 中倒数第二个 chunk 。
                bck = victim-&gt;bk;
                // 检查 bck-&gt;fd 是不是 victim，防止伪造
                if (__glibc_unlikely(bck-&gt;fd != victim)) `{`
                    errstr = "malloc(): smallbin double linked list corrupted";
                    goto errout;
                `}`
                // 设置 victim 对应的 inuse 位
                set_inuse_bit_at_offset(victim, nb);
                // 修改 small bin 链表，将 small bin 的最后一个 chunk 取出来
                bin-&gt;bk = bck;
                bck-&gt;fd = bin;
                // 如果不是 main_arena，设置对应的标志
                if (av != &amp;main_arena) set_non_main_arena(victim);
                // 细致的检查，非调试状态没有作用
                check_malloced_chunk(av, victim, nb);
                // 将申请到的 chunk 转化为对应的 mem 状态
                void *p = chunk2mem(victim);
                // 如果设置了 perturb_type , 则将获取到的chunk初始化为 perturb_type ^ 0xff
                alloc_perturb(p, bytes);
                return p;
            `}`
        `}`
    `}`
```

[![](https://p0.ssl.qhimg.com/t019e80f1dc6a66c413.jpg)](https://p0.ssl.qhimg.com/t019e80f1dc6a66c413.jpg)

<a class="reference-link" name="large%20bin"></a>large bin

> 如果申请的内存在 large bin 范围内
1. 调用 malloc_consolidate: 合并能合并的 fast bin 并放到 unsorted bin 中，对于不能合并的 fast bin 则直接放到 unsorted bin 中
1. 进行大循环


## 问题

为什么不直接从相应的 bin 中取出 large chunk: 这是ptmalloc 的机制，它会在分配 large chunk 之前对堆中碎片 chunk 进行合并，以便减少堆中的碎片。

```
/*
       If this is a large request, consolidate fastbins before continuing.
       While it might look excessive to kill all fastbins before
       even seeing if there is space available, this avoids
       fragmentation problems normally associated with fastbins.
       Also, in practice, programs tend to have runs of either small or
       large requests, but less often mixtures, so consolidation is not
       invoked all that often in most programs. And the programs that
       it is called frequently in otherwise tend to fragment.
     */

    else `{`
        // 获取large bin的下标。
        idx = largebin_index(nb);
        // 如果存在fastbin的话，会处理 fastbin 
        if (have_fastchunks(av)) malloc_consolidate(av);
    `}`
```

[![](https://p2.ssl.qhimg.com/t013d0deb4c1a1bff88.jpg)](https://p2.ssl.qhimg.com/t013d0deb4c1a1bff88.jpg)

<a class="reference-link" name="%E5%A4%A7%E5%BE%AA%E7%8E%AF"></a>大循环

> 执行到这里有两种情况
<ol>
- 申请 fast/small bin 范围内的内存并且在 fast bin 和 small bin 中找不到大小正好一致的空闲chunk
- 申请 large bin 范围内的内存,在大循环中将会处理对 large chunk 的申请
</ol>
1. 尝试从 unsorted bin 中分配用户所需内存
1. 尝试从 large bin 中分配用户所需内存
1. 尝试从 top chunk 中分配用户所需内存
<a class="reference-link" name="%E7%94%B3%E8%AF%B7%20fast%20chunk%20%E5%B9%B6%E6%89%A7%E8%A1%8C%E5%88%B0%E4%BA%86%E5%A4%A7%E5%BE%AA%E7%8E%AF"></a>申请 fast chunk 并执行到了大循环
1. 尝试合并 fast chunk
<li>先考虑 unsorted bin 再考虑 last remainder
<ul>
<li>遍历 unsorted bin（FIFO）
<ul>
1. 获得 unsorted bin 中最后一个 chunk 的指针：victim
1. 获得 unsorted bin 中倒数第二个 chunk 的指针 ：bck
1. 判断 victim 指向的 chunk 是否符合要求：av-&gt;system_mem &lt; chunk_size(victim) &lt;= 2*SIZE_SZ
<li>获得 victim 指向的 chunk 的大小
<ul>
1. 大小刚好符合，取出，分配
<li>大小不刚好符合，将 chunk 放到对应的 fast bin、small bin、large bin<br><blockquote>实际上在遍历时会把 unsorted bin 清空，将其中的 chunk 放到对应的 bin 中</blockquote>
</li>
</ul>
</li>
</ul>
</li>
<li>考虑last remainder
<ul>
1. 切割 last remainder，用 victim 指向符合要求的部分；剩下部分称为新的 last remainder
1. 更新所有记录了与 last remainder 有关的数据结构的内容，如：新的 last remainder 的大小、位置、指针，更新 unsorted bin，更新 av 中记录的 remainder 的位置
1. 设置 victim 的头部，设置新的 remainder 的头部、prev_size字段
1. 将 victim 指向的 chunk 取下，分配并设置为 mem模式
1. 如果设置了perturb_type, 则将获取到的chunk初始化为 perturb_type ^ 0xff
</ul>
</li>
</ul>
</li>- 切割 last remainder，用 victim 指向符合要求的部分；剩下部分称为新的 last remainder
- 更新所有记录了与 last remainder 有关的数据结构的内容，如：新的 last remainder 的大小、位置、指针，更新 unsorted bin，更新 av 中记录的 remainder 的位置
- 设置 victim 的头部，设置新的 remainder 的头部、prev_size字段
- 将 victim 指向的 chunk 取下，分配并设置为 mem模式
- 如果设置了perturb_type, 则将获取到的chunk初始化为 perturb_type ^ 0xff
<a class="reference-link" name="%E7%94%B3%E8%AF%B7%20small%20chunk%20%E5%B9%B6%E6%89%A7%E8%A1%8C%E5%88%B0%E4%BA%86%E5%A4%A7%E5%BE%AA%E7%8E%AF"></a>申请 small chunk 并执行到了大循环
1. 尝试合并 fast chunk
<li>先考虑 last remainder（如果它是 unsorted 中唯一的一个chunk，并且其大小足够分割出所需的空间） 再考虑 unsorted bin
<ul>
<li>考虑last remainder
<ul>
1. 切割 last remainder，用 victim 指向符合要求的部分；剩下部分称为新的 last remainder
1. 更新所有记录了与 last remainder 有关的数据结构的内容，如：新的 last remainder 的大小、位置、指针，更新 unsorted bin，更新 av 中记录的 remainder 的位置
1. 设置 victim 的头部，设置新的 remainder 的头部、prev_size字段
1. 将 victim 指向的 chunk 取下，分配并设置为 mem模式
1. 如果设置了perturb_type, 则将获取到的chunk初始化为 perturb_type ^ 0xff
</ul>
</li>
<li>遍历 unsorted bin（FIFO）
<ul>
1. 获得 unsorted bin 中最后一个 chunk 的指针：victim
1. 获得 unsorted bin 中倒数第二个 chunk 的指针 ：bck
1. 判断 victim 指向的 chunk 是否符合要求：av-&gt;system_mem &lt; chunk_size(victim) &lt;= 2*SIZE_SZ
<li>获得 victim 指向的 chunk 的大小
<ul>
1. 大小刚好符合，取出，分配
1. 大小不刚好符合，将 chunk 放到对应的 fast bin、small bin、large bin
</ul>
</li>
</ul>
</li>
</ul>
</li>- 获得 unsorted bin 中最后一个 chunk 的指针：victim
- 获得 unsorted bin 中倒数第二个 chunk 的指针 ：bck
- 判断 victim 指向的 chunk 是否符合要求：av-&gt;system_mem &lt; chunk_size(victim) &lt;= 2*SIZE_SZ
<li>获得 victim 指向的 chunk 的大小
<ul>
- 大小刚好符合，取出，分配
- 大小不刚好符合，将 chunk 放到对应的 fast bin、small bin、large bin- 遍历 unsorted bin
```
// 如果 unsorted bin 不为空
        // First In First Out
        while ((victim = unsorted_chunks(av)-&gt;bk) != unsorted_chunks(av)) `{`
            // victim 为 unsorted bin 的最后一个 chunk
            // bck 为 unsorted bin 的倒数第二个 chunk
            bck = victim-&gt;bk;
            // 判断得到的 chunk 是否满足要求，不能过小，也不能过大
            // 一般 system_mem 的大小为132K
            if (__builtin_expect(chunksize_nomask(victim) &lt;= 2 * SIZE_SZ, 0) ||
                __builtin_expect(chunksize_nomask(victim) &gt; av-&gt;system_mem, 0))
                malloc_printerr(check_action, "malloc(): memory corruption",
                                chunk2mem(victim), av);
            // 得到victim对应的chunk大小。
            size = chunksize(victim);
```
- 考虑 last remainder
```
/*
               If a small request, try to use last remainder if it is the
               only chunk in unsorted bin.  This helps promote locality for
               runs of consecutive small requests. This is the only
               exception to best-fit, and applies only when there is
               no exact fit for a small chunk.
             */

            if (in_smallbin_range(nb) &amp;&amp; bck == unsorted_chunks(av) &amp;&amp;
                victim == av-&gt;last_remainder &amp;&amp;
                (unsigned long) (size) &gt; (unsigned long) (nb + MINSIZE)) `{`
                /* split and reattach remainder */
                // 获取新的 remainder 的大小
                remainder_size          = size - nb;
                // 获取新的 remainder 的位置
                remainder               = chunk_at_offset(victim, nb);
                // 更新 unsorted bin 的情况
                unsorted_chunks(av)-&gt;bk = unsorted_chunks(av)-&gt;fd = remainder;
                // 更新 av 中记录的 last_remainder
                av-&gt;last_remainder                                = remainder;
                // 更新last remainder的指针
                remainder-&gt;bk = remainder-&gt;fd = unsorted_chunks(av);
                if (!in_smallbin_range(remainder_size)) `{`
                    remainder-&gt;fd_nextsize = NULL;
                    remainder-&gt;bk_nextsize = NULL;
                `}`
                // 设置victim的头部，
                set_head(victim, nb | PREV_INUSE |
                                     (av != &amp;main_arena ? NON_MAIN_ARENA : 0));
                // 设置 remainder 的头部
                set_head(remainder, remainder_size | PREV_INUSE);
                // 设置记录 remainder 大小的 prev_size 字段，因为此时 remainder 处于空闲状态。
                set_foot(remainder, remainder_size);
                // 细致的检查，非调试状态下没有作用
                check_malloced_chunk(av, victim, nb);
                // 将 victim 从 chunk 模式转化为mem模式
                void *p = chunk2mem(victim);
                // 如果设置了perturb_type, 则将获取到的chunk初始化为 perturb_type ^ 0xff
                alloc_perturb(p, bytes);
                return p;
            `}`
```

<a class="reference-link" name="%E7%94%B3%E8%AF%B7%20large%20chunk%20%E5%B9%B6%E6%89%A7%E8%A1%8C%E5%88%B0%E4%BA%86%E5%A4%A7%E5%BE%AA%E7%8E%AF"></a>申请 large chunk 并执行到了大循环
1. 在 large bins 中从小到大进行扫描，找到合适的 large bin
1. 获得当前 bin 中最大的 chunk 的指针：victim
1. 遍历链表，直到找到最后一个不小于所需空间大小的 chunk ，找到符合大小的最前面的那个chunk
<li>切割，计算剩余部分的大小
<ul>
1. unlink
1. 剩余部分作为 remainder 放入 unsorted bin 中，并设置好相关信息
1. 将获得 chunk 设置为 mem模式
</ul>
</li>
```
/*
           If a large request, scan through the chunks of current bin in
           sorted order to find smallest that fits.  Use the skip list for this.
         */
        if (!in_smallbin_range(nb)) `{`
            bin = bin_at(av, idx);
            /* skip scan if empty or largest chunk is too small */
            // 如果对应的 bin 为空或者其中的chunk最大的也很小，那就跳过
            // first(bin)=bin-&gt;fd 表示当前链表中最大的chunk
            if ((victim = first(bin)) != bin &amp;&amp;
                (unsigned long) chunksize_nomask(victim) &gt;=
                    (unsigned long) (nb)) `{`
                // 反向遍历链表，直到找到第一个不小于所需chunk大小的chunk
                victim = victim-&gt;bk_nextsize;
                while (((unsigned long) (size = chunksize(victim)) &lt;
                        (unsigned long) (nb)))
                    victim = victim-&gt;bk_nextsize;

                /* Avoid removing the first entry for a size so that the skip
                   list does not have to be rerouted.  */
                // 如果最终取到的chunk不是该bin中的最后一个chunk，并且该chunk与其前面的chunk
                // 的大小相同，那么我们就取其前面的chunk，这样可以避免调整bk_nextsize,fd_nextsize
                //  链表。因为大小相同的chunk只有一个会被串在nextsize链上。
                if (victim != last(bin) &amp;&amp;
                    chunksize_nomask(victim) == chunksize_nomask(victim-&gt;fd))
                    victim = victim-&gt;fd;
                // 计算分配后剩余的大小
                remainder_size = size - nb;
                // 进行unlink
                unlink(av, victim, bck, fwd);

                /* Exhaust */
                // 剩下的大小不足以当做一个块
                // 很好奇接下来会怎么办？
                if (remainder_size &lt; MINSIZE) `{`
                    set_inuse_bit_at_offset(victim, size);
                    if (av != &amp;main_arena) set_non_main_arena(victim);
                `}`
                /* Split */
                //  剩下的大小还可以作为一个chunk，进行分割。
                else `{`
                    // 获取剩下那部分chunk的指针，称为remainder
                    remainder = chunk_at_offset(victim, nb);
                    /* We cannot assume the unsorted list is empty and therefore
                       have to perform a complete insert here.  */
                    // 插入unsorted bin中
                    bck = unsorted_chunks(av);
                    fwd = bck-&gt;fd;
                    // 判断 unsorted bin 是否被破坏。
                    if (__glibc_unlikely(fwd-&gt;bk != bck)) `{`
                        errstr = "malloc(): corrupted unsorted chunks";
                        goto errout;
                    `}`
                    remainder-&gt;bk = bck;
                    remainder-&gt;fd = fwd;
                    bck-&gt;fd       = remainder;
                    fwd-&gt;bk       = remainder;
                    // 如果不处于small bin范围内，就设置对应的字段
                    if (!in_smallbin_range(remainder_size)) `{`
                        remainder-&gt;fd_nextsize = NULL;
                        remainder-&gt;bk_nextsize = NULL;
                    `}`
                    // 设置分配的chunk的标记
                    set_head(victim,
                             nb | PREV_INUSE |
                                 (av != &amp;main_arena ? NON_MAIN_ARENA : 0));

                    // 设置remainder的上一个chunk，即分配出去的chunk的使用状态
                    // 其余的不用管，直接从上面继承下来了
                    set_head(remainder, remainder_size | PREV_INUSE);
                    // 设置remainder的大小
                    set_foot(remainder, remainder_size);
                `}`
                // 检查
                check_malloced_chunk(av, victim, nb);
                // 转换为mem状态
                void *p = chunk2mem(victim);
                // 如果设置了perturb_type, 则将获取到的chunk初始化为 perturb_type ^ 0xff
                alloc_perturb(p, bytes);
                return p;
            `}`
        `}`
```

<a class="reference-link" name="%E5%9C%A8%E6%9B%B4%E5%A4%A7%E7%9A%84%20bin%20%E4%B8%AD%E5%AF%BB%E6%89%BE%20chunk"></a>在更大的 bin 中寻找 chunk

> 程序运行到了这里，说明在所需空间对应的 bin 中找不到对应大小的 chunk，需要到储存了更大的chunk 的 bin 中寻找空间
1. 获取对应的 bin
1. 获取当前索引在 binmap 中的 block 索引，检查 map（获取当前 block 对应的映射，可以得知对应的 bin 是否有空闲块）
1. 遍历 block，直到找到符合条件的 map
1. 根据 map 找到合适的 chunk
1. 切割chunk，取出；剩余部分如果够最小chunk的大小，放入 unsorted bin；剩余部分不够最小chunk会怎样？？？？？？？？？？？？？？？？？？？？？？？？？？？
1. 将获得的chunk设置为 mem 模式
<a class="reference-link" name="%E8%80%83%E8%99%91%20top%20chunk"></a>考虑 top chunk

> 如果上面的所有方法都无法获得符合条件的 chunk
<li>获得当前 top chunk 的位置与大小
<ul>
<li>如果大于所需空间
<ul>
<li>切割：
<ul>
1. 切割剩余部分大于最小chunk要求：切割，分配，剩余部分放入 unsorted bin
1. 切割剩余部分小于最小chunk要求：检查是否可以合并 fast chunk，如果可以则合并，并放入对应的 bin 中，否则需要执行 sysmalloc()向操作系统再申请一点内存
</ul>
</li>
</ul>
</li>
<li>如果小于所需空间
<ul>
1. 向操作系统申请内存
</ul>
</li>
</ul>
</li>- 向操作系统申请内存


## 本文参考

[https://ctf-wiki.github.io/ctf-wiki/pwn/heap/heap_structure/#malloc_chunk](https://ctf-wiki.github.io/ctf-wiki/pwn/heap/heap_structure/#malloc_chunk)

审核人：yiwang   编辑：边边
