> 原文链接: https://www.anquanke.com//post/id/96307 


# Heap Safari-线程本地缓存


                                阅读量   
                                **89643**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者_py ，文章来源：0x00sec.org
                                <br>原文地址：[https://0x00sec.org/t/heap-safari-thread-local-caching/5054/1](https://0x00sec.org/t/heap-safari-thread-local-caching/5054/1)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01d92240dd378d1f9c.jpg)](https://p0.ssl.qhimg.com/t01d92240dd378d1f9c.jpg)



## 介绍

在今天这篇文章中，我们将跟大家讨论关于堆（Heap）利用方面的内容。实际上，我们近期还对刚刚更新的glibc堆分配器（(pt)malloc）进行了研究/逆向分析，我们在这篇文章中也会跟大家介绍这方面的内容，因为网上目前还没有很多相关资料。我之所以要不断强调glibc，是因为在实际场景中，不同平台下（libc/操作系统/硬件/浏览器）堆的实现是不同的。在很多Linux发行版（并非全部）中，ptmalloc是比较常见的堆分配器，而且这在很多CTF比赛中也是非常重要的一个方面。因此，今天我们将围绕着所谓的tcache结构来展开我们的内容，而这是一种线程缓存机制，可用于加速内存的分配/释放，并且在Ununtu 17.10及其以上版本中是默认强制开启的。



## 要求的知识储备

1） 指针Gymnastics<br>
2） ELF加载进程<br>
3） Linux内存组织<br>
4） 堆利用相关知识<br>
5） 决心+耐心<br>
最后的第五点是我们必须要具备的，剩下的倒是可以忽略了。话虽如此，但第四点多多少少还是要知道一些的好。虽然我也很想从头开始给大家介绍堆的内部结构，但考虑到文章篇幅有限，所以我这里给大家提供了一些参考资料：
<li>了解glibc malloc：【传送门】[https://sploitfun.wordpress.com/2015/02/10/understanding-glibc-malloc/](https://sploitfun.wordpress.com/2015/02/10/understanding-glibc-malloc/)
</li>
1. 堆利用知识：【传送门】https://heap-exploitation.dhavalkapil.com/introduction.html
1. 了解堆的内部结构：【传送门】http://www.blackhat.com/presentations/bh-usa-07/Ferguson/Whitepaper/bh-usa-07-ferguson-WP.pdf
这些参考资料可以帮助你充分了解堆的内部结构以及内存管理方面的内容，不过最终你还是要自己动手（用调试器进行编译调试）才能更加深入了解。



## 配置安装
1. Ubuntu 17.10 x64：我建议使用vagrant。它的速度很快，可以帮我们加快进度。
1. gdb：没gdb可就没意思了，我个人使用的是peda，但是你也可以使用你自己习惯的工具。
<li>调试符号：虽然这不是必须的，但是这可以给逆向工程师的分析任务提供很大的帮助。Linux平台（用户空间）下的堆调试工具包安装代码如下：<br><code>sudo apt-get install glibc-source<br>
sudo apt-get install libc6-dbg<br>
sudo tar xf /usr/src/glibc/glibc-2.26.tar.xz</code><br>
在你的gdb命令行中输入下列命令：<br><code>gdb-peda$ directory /usr/src/glibc/glibc-2.26/<br>
gdb-peda$ b __libc_malloc<br>
gdb-peda$ b _int_malloc<br>
gdb-peda$ b _int_free</code><br>
上述的gdb命令将会显示出调试函数的源代码，如果你想在调试的过程中查看完整的源代码，你可以用自己喜欢的文本编辑器打开/usr/src/glibc/glibc-2.26/malloc/malloc.c并添加进去。<br>
请注意：在本文中，我们所指的分配器并不是指malloc，因为在glibc的世界中，malloc并不仅仅只是一个函数，而是一个负责处理动态内存块分配的函数包。这部分内容我待会儿会在逆向分析的过程中跟大家介绍，就算你之前不了解关于堆利用方面的内容，我也会尽可能地讲解清楚，请大家不用担心。</li>
<a class="reference-link" name="__libc_malloc"></a>

## __libc_malloc

假设你已经仔细阅读了上述资源以及代码了，你现在应该知道当你的程序调用malloc时，实际上调用的应该是**libc_malloc。<br>**

```
void *
__libc_malloc (size_t bytes)
`{`
  mstate ar_ptr;
  void *victim;

  void *(*hook) (size_t, const void *)
    = atomic_forced_read (__malloc_hook);
  if (__builtin_expect (hook != NULL, 0))
    return (*hook)(bytes, RETURN_ADDRESS (0));
#if USE_TCACHE
  /* int_free also calls request2size, be careful to not pad twice.  */
  size_t tbytes;
  checked_request2size (bytes, tbytes);
  size_t tc_idx = csize2tidx (tbytes);

  MAYBE_INIT_TCACHE ();

  DIAG_PUSH_NEEDS_COMMENT;
  if (tc_idx &lt; mp_.tcache_bins
      /*&amp;&amp; tc_idx &lt; TCACHE_MAX_BINS*/ /* to appease gcc */
      &amp;&amp; tcache
      &amp;&amp; tcache-&gt;entries[tc_idx] != NULL)
    `{`
      return tcache_get (tc_idx);
    `}`
  DIAG_POP_NEEDS_COMMENT;
#endif

  if (SINGLE_THREAD_P)
    `{`
      victim = _int_malloc (&amp;main_arena, bytes);
      assert (!victim || chunk_is_mmapped (mem2chunk (victim)) ||
	      &amp;main_arena == arena_for_chunk (mem2chunk (victim)));
      return victim;
    `}`

  arena_get (ar_ptr, bytes);

  victim = _int_malloc (ar_ptr, bytes);
  /* Retry with another arena only if we were able to find a usable arena
     before.  */
  if (!victim &amp;&amp; ar_ptr != NULL)
    `{`
      LIBC_PROBE (memory_malloc_retry, 1, bytes);
      ar_ptr = arena_get_retry (ar_ptr, bytes);
      victim = _int_malloc (ar_ptr, bytes);
    `}`

  if (ar_ptr != NULL)
    __libc_lock_unlock (ar_ptr-&gt;mutex);

  assert (!victim || chunk_is_mmapped (mem2chunk (victim)) ||
          ar_ptr == arena_for_chunk (mem2chunk (victim)));
  return victim;
`}`
libc_hidden_def (__libc_malloc)
```

第一个针对malloc的调用其代码路径如下：

```
if (builtin_expect (hook != NULL, 0))
return (hook)(bytes, RETURN_ADDRESS (0));
```

**``**而__libc_malloc所要做的就是检查全局函数指针变量的内容（值），也就是__malloc_hook。

```
gdb-peda$ x/gx &amp;malloc_hook
0x7ffff7dcfc10 &lt;malloc_hook&gt;: 0x00007ffff7a82830
gdb-peda$ x/5i 0x00007ffff7a82830
0x7ffff7a82830 &lt;malloc_hook_ini&gt;: mov eax,DWORD PTR [rip+0x34ca0e] # 0x7ffff7dcf244 &lt;__libc_malloc_initialized&gt;
0x7ffff7a82836 &lt;malloc_hook_ini+6&gt;: push r12
0x7ffff7a82838 &lt;malloc_hook_ini+8&gt;: push rbp
0x7ffff7a82839 &lt;malloc_hook_ini+9&gt;: push rbx
0x7ffff7a8283a &lt;malloc_hook_ini+10&gt;: mov rbp,rdi
```



```
static void 
malloc_hook_ini (size_t sz, const void *caller)
`{`
malloc_hook = NULL;
ptmalloc_init ();
return libc_malloc (sz);
`}`
```

malloc_hook_ini首先会对全局变量进行归零操作，然后再触发一系列函数调用来初始化main函数中的arena结构体。你可以把这个结构体当作堆分配器的roadmap，而它将帮助我们追踪已释放的内存区块以及其他的关键信息。虽然这些调用序列对我们来说并不重要，但是我仍然建议大家使用调试器来了解这个过程。



## 线程本地缓存

此时的main-arena已经设置完成了，并且随时可以将内存信息反馈给用户。当初始化过程完成之后，tcache_ini将会接管这个过程：

```
# define MAYBE_INIT_TCACHE() 
if (__glibc_unlikely (tcache == NULL)) 
tcache_init();

static void
tcache_init(void)
`{`
mstate ar_ptr;
void *victim = 0;
const size_t bytes = sizeof (tcache_perthread_struct);

…
victim = _int_malloc (ar_ptr, bytes);

if (ar_ptr != NULL)
__libc_lock_unlock (ar_ptr-&gt;mutex);

/* In a low memory situation, we may not be able to allocate memory

 - in which case, we just keep trying later.  However, we
 typically do this very early, so either there is sufficient
 memory, or there isn't enough memory to do non-trivial
 allocations anyway.  */
if (victim)
`{`
tcache = (tcache_perthread_struct *) victim;
memset (tcache, 0, sizeof (tcache_perthread_struct));
`}`
`}`
```

`线程本地缓存结构才是本文的重中之重，我们先将上述代码拆分成小的代码段，我们可以看到代码中有很多针对tcache_perthread_struct的引用：`

```
static __thread tcache_perthread_struct *tcache = NULL;

typedef struct tcache_entry
`{`
struct tcache_entry *next;
`}` tcache_entry;

/ There is one of these for each thread, which contains the
per-thread cache (hence “tcache_perthread_struct”). Keeping
overall size low is mildly important. Note that COUNTS and ENTRIES
are redundant (we could have just counted the linked list each
time), this is for performance reasons. /
typedef struct tcache_perthread_struct
`{`
char counts[TCACHE_MAX_BINS];
tcache_entry *entries[TCACHE_MAX_BINS];
`}` tcache_perthread_struct;
```

tcache_perthread_struct由两个数组构成：
1. counts是一个字节数组，它主要用来表示tcache_entry*在enrties数组中相对应的索引数字。
<li>entries是一个存储tcache_entry**的数组（malloc_chunk**），它们共同组成了一个已释放区块的链接列表。需要注意的是，每一个链接列表都可以存储最多七个已释放区块，如果超过这个数量，剩下的将会被存储到“老式”的fastbin/smallbin列表中。而每一个索引相对应的是不同大小的区块。<br>
从漏洞利用开发的角度来看，tcache结构体是存储在堆内存中的！</li>
```
victim = _int_malloc (ar_ptr, bytes);
tcache = (tcache_perthread_struct *) victim;
gdb-peda$ parseheap
addr prev size status fd bk
0x602000 0x0 0x250 Used None None
```

所以说，当__libc_malloc被首次调用之后，它将会在堆内存中每一个段的开始部分分配一个tcache。



## tcache内部结构

理论部分已经介绍完毕，现在我们需要亲自动手实践一下才行。我已经写好了一个简单的PoC【点我获取】来对我们的假设进行测试。除此之外，我们也建议同学们实现一个类似的PoC来在gdb中查看这些数据区块。<br>
下面给出的是在首次调用释放区块之前的堆内存状态：

```
gdb-peda$ parse
addr prev size
tcache --&gt; 0x602000 0x0 0x250
a --&gt; 0x602250 0x0 0x30
b --&gt; 0x602280 0x0 0x30
c --&gt; 0x6022b0 0x0 0x30
d --&gt; 0x6022e0 0x0 0x30
e --&gt; 0x602310 0x0 0x30
f --&gt; 0x602340 0x0 0x30
g --&gt; 0x602370 0x0 0x30
h --&gt; 0x6023a0 0x0 0x30
i --&gt; 0x6023d0 0x0 0x30
j --&gt; 0x602400 0x0 0x30
k --&gt; 0x602430 0x0 0x30
```

需要注意的是，出于性能方面的考虑，**libc_malloc首先会尝试从tcache-&gt;entries[]列表中获取数据块，而不是从fastbin列表中获取。由于进行内存分配时系统不会释放区块空间，因此**libc_malloc将会调用_int_malloc来获取区块空间。

```
/* When "x" is from chunksize().  */
# define csize2tidx(x) (((x) - MINSIZE + MALLOC_ALIGNMENT - 1) / MALLOC_ALIGNMENT)

void *
__libc_malloc (size_t bytes)
`{`
  ...
#if USE_TCACHE
  /* int_free also calls request2size, be careful to not pad twice.  */
  size_t tbytes;
  checked_request2size (bytes, tbytes);
  size_t tc_idx = csize2tidx (tbytes);

  MAYBE_INIT_TCACHE ();

  DIAG_PUSH_NEEDS_COMMENT;
  if (tc_idx &lt; mp_.tcache_bins
      /*&amp;&amp; tc_idx &lt; TCACHE_MAX_BINS*/ /* to appease gcc */
      &amp;&amp; tcache
      &amp;&amp; tcache-&gt;entries[tc_idx] != NULL)
    `{`
      return tcache_get (tc_idx);
    `}`
    ...

  victim = _int_malloc (ar_ptr, bytes);
```

接下来，我们看一看在分配区块空间时tcache的情况：

```
/ Fill in the tcache for size 0x30. /
free(a);
free(b);
free(c);
free(d);
free(e);
free(f);
free(g);
/ Place the rest in the corresponding fastbin list. /
free(h);
free(i);
free(j);
free(k);
```

只要下列条件符合，那么_int_free将会尝试在相应的tcache索引存储最近释放的区块：
1. tcache已初始化。
1. csize2tidx(size)返回的索引需要小于64。
<li>counts[idx]需要小于或等于7.<br>
下面给出的是tcache_put的调用过程：</li>
```
// rcx will contain a kernel address
mov    rcx,QWORD PTR [rip+0x34f744]        # 0x7ffff7dced78
lea    rdx,[r13-0x11]
shr    rdx,0x4
mov    rcx,QWORD PTR fs:[rcx]
// Check if tcache is initialized
test   rcx,rcx
# If it's not, take the fastbin route
je     0x7ffff7a7f663 &lt;_int_free+147&gt;
// Make sure the chunk's size is within the tcache boundaries
cmp    rdx,QWORD PTR [rip+0x34fc64]        # 0x7ffff7dcf2b0 &lt;mp_+80&gt;
jae    0x7ffff7a7f663 &lt;_int_free+147&gt;
movsx  rdi,BYTE PTR [rcx+rdx*1]
// Make sure counts[idx] is less than 7
cmp    rdi,QWORD PTR [rip+0x34fc66]        # 0x7ffff7dcf2c0 &lt;mp_+96&gt;
mov    rsi,rdi
jb     0x7ffff7a7f940 &lt;_int_free+880&gt;
gdb-peda$ x/gx 0x7ffff7dcf2b0
0x7ffff7dcf2b0 &lt;mp_+80&gt;:	0x0000000000000040
gdb-peda$ x/gx 0x7ffff7dcf2c0
0x7ffff7dcf2c0 &lt;mp_+96&gt;:	0x0000000000000007
```

下面给出的是源代码版本：

```
static void
_int_free (mstate av, mchunkptr p, int have_lock)
`{`
 ...
#if USE_TCACHE
  `{`
    size_t tc_idx = csize2tidx (size);

    if (tcache
	&amp;&amp; tc_idx &lt; mp_.tcache_bins
	&amp;&amp; tcache-&gt;counts[tc_idx] &lt; mp_.tcache_count)
      `{`
	tcache_put (p, tc_idx);
	return;
      `}`
  `}`
#endif
  ...
```



## tcache_put

tcache_put负责往相应的entries[]索引中存放已释放的区块，并更新counts[idx]的值。

```
// Make sure the chunk's size is within the tcache boundaries
cmp    rdx,0x3f
// tcache_entry *e = (tcache_entry *) chunk2mem (chunk);
lea    rdi,[rbx+0x10]
ja     0x7ffff7a80334
// &amp;counts[idx]
lea    rax,[rcx+rdx*8]
add    esi,0x1
// tcache-&gt;entries[tc_idx]
mov    r8,QWORD PTR [rax+0x40]
// e-&gt;next = tcache-&gt;entries[tc_idx];
mov    QWORD PTR [rbx+0x10],r8
// tcache-&gt;entries[tc_idx] = e
mov    QWORD PTR [rax+0x40],rdi
// counts[idx]++
mov    BYTE PTR [rcx+rdx*1],sil
/* Caller must ensure that we know tc_idx is valid and there's room
   for more chunks.  */
static void
tcache_put (mchunkptr chunk, size_t tc_idx)
`{`
  tcache_entry *e = (tcache_entry *) chunk2mem (chunk);
  assert (tc_idx &lt; TCACHE_MAX_BINS);
  e-&gt;next = tcache-&gt;entries[tc_idx];
  tcache-&gt;entries[tc_idx] = e;
  ++(tcache-&gt;counts[tc_idx]);
`}`
```

下面给出的是ASCII版本：

```
Before:
                  gdb-peda$ x/80gx 0x602000
                      0x602000:	0x0000000000000000	0x0000000000000251
tcache--&gt;counts[] --&gt; 0x602010:	0x0000000000000000	0x0000000000000000
                      0x602020:	0x0000000000000000	0x0000000000000000
                      0x602030:	0x0000000000000000	0x0000000000000000
                      0x602040:	0x0000000000000000	0x0000000000000000
                      0x602050:	0x0000000000000000	0x0000000000000000 &lt;-- tcache&gt;entries[]
                      0x602060:	0x0000000000000000	0x0000000000000000
                                        ...                ...
                      0x602240:	0x0000000000000000	0x0000000000000000
                      0x602250:	0x0000000000000000	0x0000000000000031 &lt;-- chunk a
                                        ...                ...


free(a);

tcache-&gt;counts[]

   0       1       2            63
+------++------++------+     +------+ 
|   0  ||  1   ||  0   | ... |  0   |
|      ||      ||      |     |      |
+------++------++------+     +------+

tcache-&gt;entries[]

   0       1       2            63
+------++------++------+     +------+ 
| NULL ||  a   || NULL | ... | NULL |
|      ||      ||      |     |      |
+------++------++------+     +------+
           |
           |
          NULL

After:
                  gdb-peda$ x/80gx 0x602000
                      0x602000:	0x0000000000000000	0x0000000000000251 
tcache--&gt;counts[] --&gt; 0x602010:	0x0000000000000100	0x0000000000000000
                      0x602020:	0x0000000000000000	0x0000000000000000
                      0x602030:	0x0000000000000000	0x0000000000000000
                      0x602040:	0x0000000000000000	0x0000000000000000
                      0x602050:	0x0000000000000000	0x0000000000602260 &lt;-- tcache&gt;entries[]
                      0x602060:	0x0000000000000000	0x0000000000000000
                                        ...                ...
                      0x602240:	0x0000000000000000	0x0000000000000000
                      0x602250:	0x0000000000000000	0x0000000000000031 &lt;-- chunk a
                                        ...                ...
```

entries[idx]和counts[idx]已经更新完毕，接下来我们一起看一看其他已释放的区块情况：

```
free(b);

tcache-&gt;counts[]

   0       1       2            63
+------++------++------+     +------+ 
|   0  ||  2   ||  0   | ... |  0   |
|      ||      ||      |     |      |
+------++------++------+     +------+

tcache-&gt;entries[]

   0       1       2            63
+------++------++------+     +------+ 
| NULL ||  b   || NULL | ... | NULL |
|      ||      ||      |     |      |
+------++------++------+     +------+
            |
            |
        +------+
        |   a  |
        |      |
        +------+
            |
            |
           NULL

After:
                   gdb-peda$ x/80gx 0x602000
                      0x602000:	0x0000000000000000	0x0000000000000251 
tcache--&gt;counts[] --&gt; 0x602010:	0x0000000000000200	0x0000000000000000
                      0x602020:	0x0000000000000000	0x0000000000000000
                      0x602030:	0x0000000000000000	0x0000000000000000
                      0x602040:	0x0000000000000000	0x0000000000000000
                      0x602050:	0x0000000000000000	0x0000000000602290 &lt;-- tcache&gt;entries[]
                      0x602060:	0x0000000000000000	0x0000000000000000
                                        ...                ...
                      0x602240:	0x0000000000000000	0x0000000000000000
                      0x602250:	0x0000000000000000	0x0000000000000031 &lt;-- chunk a
                                        ...                ...

gdb-peda$ x/gx 0x0000000000602290 &lt;-- (tcache_entry *)b
0x602290:	0x0000000000602260
gdb-peda$ x/gx 0x0000000000602260 &lt;-- a == (tcache_entry *)b-&gt;next
0x602260:	0x0000000000000000    &lt;-- NULL
```

需要注意的是，系统会在列表开头插入数据：

```
...
free(g);


tcache-&gt;counts[]

   0       1       2            63
+------++------++------+     +------+ 
|   0  ||  7   ||  0   | ... |  0   |
|      ||      ||      |     |      |
+------++------++------+     +------+

tcache-&gt;entries[]

   0       1       2            63
+------++------++------+     +------+ 
| NULL ||  g   || NULL | ... | NULL |
|      ||      ||      |     |      |
+------++------++------+     +------+
            |
            |
        +------+
        |  f   |
        |      |
        +------+
            |
            |
        +------+
        |  e   |
        |      |
        +------+
            |
            |
        +------+
        |  d   |
        |      |
        +------+
            |
            |
        +------+
        |  c   |
        |      |
        +------+
            |
            |
        +------+
        |  b   |
        |      |
        +------+
            |
            |
        +------+
        |  a   |
        |      |
        +------+
            |
            |
           NULL
```

如果tcache检测失败的话，系统将采用fastbin路径运行：

```
static void
_int_free (mstate av, mchunkptr p, int have_lock)
`{`
  ...
  size = chunksize (p);

  ...

  check_inuse_chunk(av, p);

#if USE_TCACHE
  `{`
    size_t tc_idx = csize2tidx (size);

    if (tcache
	&amp;&amp; tc_idx &lt; mp_.tcache_bins
	&amp;&amp; tcache-&gt;counts[tc_idx] &lt; mp_.tcache_count)
      `{`
	tcache_put (p, tc_idx);
	return;
      `}`
  `}`
#endif

  /*
    If eligible, place chunk on a fastbin so it can be found
    and used quickly in malloc.
  */

  if ((unsigned long)(size) &lt;= (unsigned long)(get_max_fast ())

    ...

    atomic_store_relaxed (&amp;av-&gt;have_fastchunks, true);
    unsigned int idx = fastbin_index(size);
    fb = &amp;fastbin (av, idx);

    /* Atomically link P to its fastbin: P-&gt;FD = *FB; *FB = P;  */
    mchunkptr old = *fb, old2;

    ...
      do
	`{`
	  /* Check that the top of the bin is not the record we are going to
	     add (i.e., double free).  */
	  if (__builtin_expect (old == p, 0))
	    malloc_printerr ("double free or corruption (fasttop)");
	  p-&gt;fd = old2 = old;
	`}`
      while ((old = catomic_compare_and_exchange_val_rel (fb, p, old2))
	     != old2);
      ...
free(h);
free(i);
free(j);
free(k);

fastbinsY[NFASTBINS]

   0       1       2            
+------++------++------+     
| NULL ||  k   || NULL | ...
|      ||      ||      |     
+------++------++------+     
            |
            |
        +------+
        |  j   |
        |      |
        +------+
            |
            |
        +------+
        |  i   |
        |      |
        +------+
            |
            |
        +------+
        |  h   |
        |      |
        +------+
            |
            |
           NULL

gdb-peda$ printfastbin 
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x602430 --&gt; 0x602400 --&gt; 0x6023d0 --&gt; 0x6023a0 --&gt; 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x0
```

如果区块的分配大小为0x20，tcache_get将会运行：

```
// Allocate the chunks out of tcache. 
// returns g
malloc(0x20);
// returns f
malloc(0x20); 
// returns e
malloc(0x20); 
// returns d
malloc(0x20);
// returns c
malloc(0x20);
// returns b
malloc(0x20); 
// returns a
malloc(0x20);
```



## tcache_get

正如我们之前所说的，当系统接收到了新的分配请求之后，__libc_malloc首先会检查tcache-&gt;entries[idx]中是否有符合条件的可用区块。如果有的话，tcache_get<br>
将会从列表头部获取区块地址。

```
cmp    rbx,0x3f
ja     0x7ffff7a840c3
// Remove chunk at the head of the list
mov    rsi,QWORD PTR [rdx]
// Place its fd at the head of the list
mov    QWORD PTR [rcx+0x40],rsi
// --(tcache-&gt;counts[tc_idx]);
sub    BYTE PTR [rax+rbx*1],0x1
static void *
tcache_get (size_t tc_idx)
`{`
  tcache_entry *e = tcache-&gt;entries[tc_idx];
  assert (tc_idx &lt; TCACHE_MAX_BINS);
  assert (tcache-&gt;entries[tc_idx] &gt; 0);
  tcache-&gt;entries[tc_idx] = e-&gt;next;
  --(tcache-&gt;counts[tc_idx]);
  return (void *) e;
`}`
```

gdb调试信息如下所示：

```
Before:
                  gdb-peda$ x/80gx 0x602000
                      0x602000:	0x0000000000000000	0x0000000000000251
tcache--&gt;counts[] --&gt; 0x602010:	0x0000000000000700	0x0000000000000000
                      0x602020:	0x0000000000000000	0x0000000000000000
                      0x602030:	0x0000000000000000	0x0000000000000000
                      0x602040:	0x0000000000000000	0x0000000000000000
                      0x602050:	0x0000000000000000	0x0000000000602380 &lt;-- tcache&gt;entries[]
                      0x602060:	0x0000000000000000	0x0000000000000000
                                        ...                ...

// returns g
malloc(0x20);

tcache-&gt;counts[]

   0       1       2            63
+------++------++------+     +------+ 
|   0  ||  6   ||  0   | ... |  0   |
|      ||      ||      |     |      |
+------++------++------+     +------+

tcache-&gt;entries[]

   0       1       2            63
+------++------++------+     +------+ 
| NULL ||  f   || NULL | ... | NULL |
|      ||      ||      |     |      |
+------++------++------+     +------+
            |
            |
        +------+
        |  e   |
        |      |
        +------+
            |
            |
        +------+
        |  d   |
        |      |
        +------+
            |
            |
        +------+
        |  c   |
        |      |
        +------+
            |
            |
        +------+
        |  b   |
        |      |
        +------+
            |
            |
        +------+
        |  a   |
        |      |
        +------+
            |
            |
           NULL

After:
                  gdb-peda$ x/80gx 0x602000
                      0x602000:	0x0000000000000000	0x0000000000000251
tcache--&gt;counts[] --&gt; 0x602010:	0x0000000000000600	0x0000000000000000
                      0x602020:	0x0000000000000000	0x0000000000000000
                      0x602030:	0x0000000000000000	0x0000000000000000
                      0x602040:	0x0000000000000000	0x0000000000000000
                      0x602050:	0x0000000000000000	0x0000000000602350 &lt;-- tcache&gt;entries[]
                      0x602060:	0x0000000000000000	0x0000000000000000
                                        ...                ...
```

大家可以看到，0x602380已经从列表中移除了，计数器也更新成功：

```
// returns f
malloc(0x20); 


tcache-&gt;counts[]

   0       1       2            63
+------++------++------+     +------+ 
|   0  ||  5   ||  0   | ... |  0   |
|      ||      ||      |     |      |
+------++------++------+     +------+

tcache-&gt;entries[]

   0       1       2            63
+------++------++------+     +------+ 
| NULL ||  e   || NULL | ... | NULL |
|      ||      ||      |     |      |
+------++------++------+     +------+
            |
            |
        +------+
        |  d   |
        |      |
        +------+
            |
            |
        +------+
        |  c   |
        |      |
        +------+
            |
            |
        +------+
        |  b   |
        |      |
        +------+
            |
            |
        +------+
        |  a   |
        |      |
        +------+
            |
            |
           NULL

                  gdb-peda$ x/80gx 0x602000
                      0x602000:	0x0000000000000000	0x0000000000000251
tcache--&gt;counts[] --&gt; 0x602010:	0x0000000000000500	0x0000000000000000
                      0x602020:	0x0000000000000000	0x0000000000000000
                      0x602030:	0x0000000000000000	0x0000000000000000
                      0x602040:	0x0000000000000000	0x0000000000000000
                      0x602050:	0x0000000000000000	0x0000000000602320 &lt;-- tcache&gt;entries[]
                      0x602060:	0x0000000000000000	0x0000000000000000
                                        ...                ...
```

0x602350已经从列表中被删除了，在第七次空间分配之后，tcache将会被清空，而__libc_malloc将调用_int_malloc，它将会检测fastbin数组中的可用区块。

```
gdb-peda$ x/80gx 0x602000
0x602000: 0x0000000000000000 0x0000000000000251
tcache—&gt;counts[] —&gt; 0x602010: 0x0000000000000000 0x0000000000000000
0x602020: 0x0000000000000000 0x0000000000000000
0x602030: 0x0000000000000000 0x0000000000000000
0x602040: 0x0000000000000000 0x0000000000000000
0x602050: 0x0000000000000000 0x0000000000000000 &lt;— tcache&gt;entries[]
0x602060: 0x0000000000000000 0x0000000000000000
… …
0x602240: 0x0000000000000000 0x0000000000000000
0x602250: 0x0000000000000000 0x0000000000000031 &lt;— chunk a
… …

gdb-peda$ printfastbin
(0x20) fastbin[0]: 0x0
(0x30) fastbin[1]: 0x602430 --&gt; 0x602400 --&gt; 0x6023d0 --&gt; 0x6023a0 --&gt; 0x0
(0x40) fastbin[2]: 0x0
(0x50) fastbin[3]: 0x0
(0x60) fastbin[4]: 0x0
(0x70) fastbin[5]: 0x0
(0x80) fastbin[6]: 0x0
```



## _int_malloc

_int_malloc还有一个新添加的功能，如果fastbin列表中相应索引存有可用区块的话，_int_malloc将会返回fastbin列表中的第一个区块，并将fastbin列表中剩余区块存放到tcache-entries[idx]中相应的条目，前提是数组中有足够的空间（小于7）。

```
static void *
_int_malloc (mstate av, size_t bytes)
`{`
...

#define REMOVE_FB(fb, victim, pp)			\
  do							\
    `{`							\
      victim = pp;					\
      if (victim == NULL)				\
	break;						\
    `}`							\
  while ((pp = catomic_compare_and_exchange_val_acq (fb, victim-&gt;fd, victim)) \
	 != victim);					\

  if ((unsigned long) (nb) &lt;= (unsigned long) (get_max_fast ()))
    `{`
      idx = fastbin_index (nb);
      mfastbinptr *fb = &amp;fastbin (av, idx);
      mchunkptr pp;
      victim = *fb;

      if (victim != NULL)
	`{`
	  if (SINGLE_THREAD_P)
	    *fb = victim-&gt;fd;
	  else
	    REMOVE_FB (fb, pp, victim);
          ...
#if USE_TCACHE
	      /* While we're here, if we see other chunks of the same size,
		 stash them in the tcache.  */
	      size_t tc_idx = csize2tidx (nb);
	      if (tcache &amp;&amp; tc_idx &lt; mp_.tcache_bins)
		`{`
		  mchunkptr tc_victim;

		  /* While bin not empty and tcache not full, copy chunks.  */
		  while (tcache-&gt;counts[tc_idx] &lt; mp_.tcache_count
			 &amp;&amp; (tc_victim = *fb) != NULL)
		    `{`
		      if (SINGLE_THREAD_P)
			*fb = tc_victim-&gt;fd;
		      else
			`{`
			  REMOVE_FB (fb, pp, tc_victim);
			  if (__glibc_unlikely (tc_victim == NULL))
			    break;
			`}`
		      tcache_put (tc_victim, tc_idx);
		    `}`
		`}`
#endif
...
```

接下来就是见证奇迹的时候了，我们希望0x602430 是由_int_malloc返回的，而剩下的数据区块仍需要在tcache-&gt;entries[idx]之中。

```
/*
	 Retrieve chunk from fastbin.
	 The rest of the chunks (h, i, j, k) will be allocated
	 out of their fastbin list and will be placed back into tcache-&gt;entries[idx].
*/
malloc(0x20);

gdb-peda$ printfastbin 
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x0

                  gdb-peda$ x/80gx 0x602000
                      0x602000:	0x0000000000000000	0x0000000000000251
tcache--&gt;counts[] --&gt; 0x602010:	0x0000000000000300	0x0000000000000000
                      0x602020:	0x0000000000000000	0x0000000000000000
                      0x602030:	0x0000000000000000	0x0000000000000000
                      0x602040:	0x0000000000000000	0x0000000000000000
                      0x602050:	0x0000000000000000	0x00000000006023b0 &lt;-- tcache&gt;entries[]
                      0x602060:	0x0000000000000000	0x0000000000000000
                                        ...                ...

gdb-peda$ x/gx 0x00000000006023b0 &lt;-- head of the linked list
0x6023b0:	0x00000000006023e0
gdb-peda$ x/gx 0x00000000006023e0 &lt;-- (tcache_entry *)0x6023b0-&gt;next
0x6023e0:	0x0000000000602410
gdb-peda$ x/gx 0x0000000000602410 &lt;-- (tcache_entry *)0x6023e0-&gt;next
0x602410:	0x0000000000000000
```

我们所有的假设现在都已经被证明是正确的了。fastbin列表已经被清空了，而相应的tcache索引也已经被剩下的fastbin区块填充满了。由于fastbin列表头部的数据会被删除，你将会发现列表尾部的区块会变成tcache-&gt;entries[idx]的头部。



## 总结

在本文中，我们对近期刚刚更新的glibc malloc进行了简单介绍，如果你对16.x或17.04版本的实现比较熟悉的话，理解线程本地缓存这方面的内容其实也并不困难。除此之外，我们希望大家能够自己动手亲自去逆向一下堆结构的实现。最后，感谢大家的耐心阅读。
