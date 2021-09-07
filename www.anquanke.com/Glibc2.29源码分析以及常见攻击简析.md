> 原文链接: https://www.anquanke.com//post/id/252548 


# Glibc2.29源码分析以及常见攻击简析


                                阅读量   
                                **16131**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t015fb416053144bb5a.jpg)](https://p2.ssl.qhimg.com/t015fb416053144bb5a.jpg)



## 零：前言

对glibc2.29的源码分析及一些攻击方式的介绍



## 一：整体介绍

我们平常做pwn题大概所利用的漏洞都是经过malloc，free等一些对内存进行操作的函数。下面我会对一些函数进行分析（如有错误，请师傅们直接指出）

libc_malloc,libc_free,int_malloc,int_free等一些函数分析

二：基本结构和定义的介绍

### <a class="reference-link" name="1.malloc_chunk"></a>1.malloc_chunk

```
struct malloc_chunk `{`

  INTERNAL_SIZE_T      mchunk_prev_size;  /* Size of previous chunk (if free).  */
  INTERNAL_SIZE_T      mchunk_size;       /* Size in bytes, including overhead. */

  struct malloc_chunk* fd;         /* double links -- used only if free. */
  struct malloc_chunk* bk;

  /* Only used for large blocks: pointer to next larger size.  */
  struct malloc_chunk* fd_nextsize; /* double links -- used only if free. */
  struct malloc_chunk* bk_nextsize;
`}`;
/*
malloc_chunk details:

    (The following includes lightly edited explanations by Colin Plumb.)

    Chunks of memory are maintained using a `boundary tag' method as
    described in e.g., Knuth or Standish.  (See the paper by Paul
    Wilson ftp://ftp.cs.utexas.edu/pub/garbage/allocsrv.ps for a
    survey of such techniques.)  Sizes of free chunks are stored both
    in the front of each chunk and at the end.  This makes
    consolidating fragmented chunks into bigger chunks very fast.  The
    size fields also hold bits representing whether chunks are free or
    in use.

    An allocated chunk looks like this:


    chunk-&gt; +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |             Size of previous chunk, if unallocated (P clear)  |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |             Size of chunk, in bytes                     |A|M|P|
      mem-&gt; +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |             User data starts here...                          .
        .                                                               .
        .             (malloc_usable_size() bytes)                      .
        .                                                               |
nextchunk-&gt; +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |             (size of chunk, but used for application data)    |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |             Size of next chunk, in bytes                |A|0|1|
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    Where "chunk" is the front of the chunk for the purpose of most of
    the malloc code, but "mem" is the pointer that is returned to the
    user.  "Nextchunk" is the beginning of the next contiguous chunk.

    Chunks always begin on even word boundaries, so the mem portion
    (which is returned to the user) is also on an even word boundary, and
    thus at least double-word aligned.

    Free chunks are stored in circular doubly-linked lists, and look like this:

    chunk-&gt; +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |             Size of previous chunk, if unallocated (P clear)  |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    `head:' |             Size of chunk, in bytes                     |A|0|P|
      mem-&gt; +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |             Forward pointer to next chunk in list             |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |             Back pointer to previous chunk in list            |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |             Unused space (may be 0 bytes long)                .
        .                                                               .
        .                                                               |
nextchunk-&gt; +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    `foot:' |             Size of chunk, in bytes                           |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |             Size of next chunk, in bytes                |A|0|0|
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    The P (PREV_INUSE) bit, stored in the unused low-order bit of the
    chunk size (which is always a multiple of two words), is an in-use
    bit for the *previous* chunk.  If that bit is *clear*, then the
    word before the current chunk size contains the previous chunk
    size, and can be used to find the front of the previous chunk.
    The very first chunk allocated always has this bit set,
    preventing access to non-existent (or non-owned) memory. If
    prev_inuse is set for any given chunk, then you CANNOT determine
    the size of the previous chunk, and might even get a memory
    addressing fault when trying to do so.

    The A (NON_MAIN_ARENA) bit is cleared for chunks on the initial,
    main arena, described by the main_arena variable.  When additional
    threads are spawned, each thread receives its own arena (up to a
    configurable limit, after which arenas are reused for multiple
    threads), and the chunks in these arenas have the A bit set.  To
    find the arena for a chunk on such a non-main arena, heap_for_ptr
    performs a bit mask operation and indirection through the ar_ptr
    member of the per-heap header heap_info (see arena.c).

    Note that the `foot' of the current chunk is actually represented
    as the prev_size of the NEXT chunk. This makes it easier to
    deal with alignments etc but can be very confusing when trying
    to extend or adapt this code.

    The three exceptions to all this are:

     1. The special chunk `top' doesn't bother using the
    trailing size field since there is no next contiguous chunk
    that would have to index off it. After initialization, `top'
    is forced to always exist.  If it would become less than
    MINSIZE bytes long, it is replenished.  
     top chunk永远存在，且没有prev size字段


     2. Chunks allocated via mmap, which have the second-lowest-order
    bit M (IS_MMAPPED) set in their size fields.  Because they are
    allocated one-by-one, each must contain its own trailing size
    field.  If the M bit is set, the other bits are ignored
    (because mmapped chunks are neither in an arena, nor adjacent
    to a freed chunk).  The M bit is also used for chunks which
    originally came from a dumped heap via malloc_set_state in
    hooks.c.

     3. Chunks in fastbins are treated as allocated chunks from the
    point of view of the chunk allocator.  They are consolidated
    with their neighbors only in bulk, in malloc_consolidate.
*/   fastbin中的chunk的p位不会置零，是为了防止合并
```

### <a class="reference-link" name="2.malloc_stats"></a>2.malloc_stats

```
void
__malloc_stats (void)
`{`
  int i;
  mstate ar_ptr;
  unsigned int in_use_b = mp_.mmapped_mem, system_b = in_use_b;

  if (__malloc_initialized &lt; 0)
    ptmalloc_init ();
  _IO_flockfile (stderr);
  int old_flags2 = stderr-&gt;_flags2;
  stderr-&gt;_flags2 |= _IO_FLAGS2_NOTCANCEL;
  for (i = 0, ar_ptr = &amp;main_arena;; i++)
    `{`
      struct mallinfo mi;

      memset (&amp;mi, 0, sizeof (mi));
      __libc_lock_lock (ar_ptr-&gt;mutex);
      int_mallinfo (ar_ptr, &amp;mi);
      fprintf (stderr, "Arena %d:\n", i);
      fprintf (stderr, "system bytes     = %10u\n", (unsigned int) mi.arena);
      fprintf (stderr, "in use bytes     = %10u\n", (unsigned int) mi.uordblks);
#if MALLOC_DEBUG &gt; 1
      if (i &gt; 0)
        dump_heap (heap_for_ptr (top (ar_ptr)));
#endif
      system_b += mi.arena;
      in_use_b += mi.uordblks;
      __libc_lock_unlock (ar_ptr-&gt;mutex);
      ar_ptr = ar_ptr-&gt;next;
      if (ar_ptr == &amp;main_arena)
        break;
    `}`
  fprintf (stderr, "Total (incl. mmap):\n");
  fprintf (stderr, "system bytes     = %10u\n", system_b);
  fprintf (stderr, "in use bytes     = %10u\n", in_use_b);
  fprintf (stderr, "max mmap regions = %10u\n", (unsigned int) mp_.max_n_mmaps);
  fprintf (stderr, "max mmap bytes   = %10lu\n",
           (unsigned long) mp_.max_mmapped_mem);
  stderr-&gt;_flags2 = old_flags2;
  _IO_funlockfile (stderr);
  `}`
```

其实这个我没太看懂，可能是缺少操作系统的知识吧，后期补！

### <a class="reference-link" name="3.#if%20USE_TCACHE"></a>3.#if USE_TCACHE

```
#if USE_TCACHE
/* We want 64 entries.  This is an arbitrary limit, which tunables can reduce.  */
# define TCACHE_MAX_BINS        64  //定义了一共有几种大小的tcache
# define MAX_TCACHE_SIZE    tidx2usize (TCACHE_MAX_BINS-1)

/* Only used to pre-fill the tunables.  */
# define tidx2usize(idx)    (((size_t) idx) * MALLOC_ALIGNMENT + MINSIZE - SIZE_SZ)

/* When "x" is from chunksize().  */
# define csize2tidx(x) (((x) - MINSIZE + MALLOC_ALIGNMENT - 1) / MALLOC_ALIGNMENT)
/* When "x" is a user-provided size.  */
# define usize2tidx(x) csize2tidx (request2size (x))

/* With rounding and alignment, the bins are...
   idx 0   bytes 0..24 (64-bit) or 0..12 (32-bit)
   idx 1   bytes 25..40 or 13..20
   idx 2   bytes 41..56 or 21..28
   etc.  */

/* This is another arbitrary limit, which tunables can change.  Each
   tcache bin will hold at most this number of chunks.  */
# define TCACHE_FILL_COUNT 7   //定义了同大小tcache最多能有多少个chunk
#endif
```



## 三：bin介绍

### <a class="reference-link" name="1.bins%E6%95%B0%E7%BB%84"></a>1.bins数组

```
mchunkptr bins[ NBINS * 2 - 2 ]：
bins[1]: unsorted bin
bins[2]: small bin(1)
...
bins[63]: small bin(62)
bins[64]: large bin(1)
bins[65]: large bin(2)
...
bins[126]: large bin(63)
```

bins数组一共有0~127个，bins[0]和bins[127]都不存在，bins[1]是unsortedbin的头部，有62个smallbin数组，63个largebin数组

### <a class="reference-link" name="2.fastbin"></a>2.fastbin

```
/* offset 2 to use otherwise unindexable first 2 bins */
#define fastbin_index(sz) \
  ((((unsigned int) (sz)) &gt;&gt; (SIZE_SZ == 8 ? 4 : 3)) - 2)   //SIZE_SZ在64位下是8字节，在32位下是4字节


/* The maximum fastbin request size we support */
#define MAX_FAST_SIZE     (80 * SIZE_SZ / 4)       //160和80字节

#define NFASTBINS  (fastbin_index (request2size (MAX_FAST_SIZE)) + 1)
```

### <a class="reference-link" name="3.smallbin"></a>3.smallbin

```
/*
   Indexing

    Bins for sizes &lt; 512 bytes contain chunks of all the same size, spaced
    8 bytes apart. Larger bins are approximately logarithmically spaced:

    64 bins of size       8
    32 bins of size      64
    16 bins of size     512
     8 bins of size    4096
     4 bins of size   32768
     2 bins of size  262144
     1 bin  of size what's left

    There is actually a little bit of slop in the numbers in bin_index
    for the sake of speed. This makes no difference elsewhere.

    The bins top out around 1MB because we expect to service large
    requests via mmap.

    Bin 0 does not exist.  Bin 1 is the unordered list; if that would be
    a valid chunk size the small bins are bumped up one.
 */

#define NBINS             128  //bin的总数
#define NSMALLBINS         64  
#define SMALLBIN_WIDTH    MALLOC_ALIGNMENT
#define SMALLBIN_CORRECTION (MALLOC_ALIGNMENT &gt; 2 * SIZE_SZ)
#define MIN_LARGE_SIZE    ((NSMALLBINS - SMALLBIN_CORRECTION) * SMALLBIN_WIDTH)

#define in_smallbin_range(sz)  \
  ((unsigned long) (sz) &lt; (unsigned long) MIN_LARGE_SIZE)    //如果bin的大小小于largebin的最小值，则进入smallbin

#define smallbin_index(sz) \
  ((SMALLBIN_WIDTH == 16 ? (((unsigned) (sz)) &gt;&gt; 4) : (((unsigned) (sz)) &gt;&gt; 3))\
   + SMALLBIN_CORRECTION)
```

### <a class="reference-link" name="4.largebin"></a>4.largebin

```
#define largebin_index_32(sz)                                                \
  (((((unsigned long) (sz)) &gt;&gt; 6) &lt;= 38) ?  56 + (((unsigned long) (sz)) &gt;&gt; 6) :\
   ((((unsigned long) (sz)) &gt;&gt; 9) &lt;= 20) ?  91 + (((unsigned long) (sz)) &gt;&gt; 9) :\
   ((((unsigned long) (sz)) &gt;&gt; 12) &lt;= 10) ? 110 + (((unsigned long) (sz)) &gt;&gt; 12) :\
   ((((unsigned long) (sz)) &gt;&gt; 15) &lt;= 4) ? 119 + (((unsigned long) (sz)) &gt;&gt; 15) :\
   ((((unsigned long) (sz)) &gt;&gt; 18) &lt;= 2) ? 124 + (((unsigned long) (sz)) &gt;&gt; 18) :\
   126)

#define largebin_index_32_big(sz)                                            \
  (((((unsigned long) (sz)) &gt;&gt; 6) &lt;= 45) ?  49 + (((unsigned long) (sz)) &gt;&gt; 6) :\
   ((((unsigned long) (sz)) &gt;&gt; 9) &lt;= 20) ?  91 + (((unsigned long) (sz)) &gt;&gt; 9) :\
   ((((unsigned long) (sz)) &gt;&gt; 12) &lt;= 10) ? 110 + (((unsigned long) (sz)) &gt;&gt; 12) :\
   ((((unsigned long) (sz)) &gt;&gt; 15) &lt;= 4) ? 119 + (((unsigned long) (sz)) &gt;&gt; 15) :\
   ((((unsigned long) (sz)) &gt;&gt; 18) &lt;= 2) ? 124 + (((unsigned long) (sz)) &gt;&gt; 18) :\
   126)

// XXX It remains to be seen whether it is good to keep the widths of
// XXX the buckets the same or whether it should be scaled by a factor
// XXX of two as well.
#define largebin_index_64(sz)                                                \
  (((((unsigned long) (sz)) &gt;&gt; 6) &lt;= 48) ?  48 + (((unsigned long) (sz)) &gt;&gt; 6) :\
   ((((unsigned long) (sz)) &gt;&gt; 9) &lt;= 20) ?  91 + (((unsigned long) (sz)) &gt;&gt; 9) :\
   ((((unsigned long) (sz)) &gt;&gt; 12) &lt;= 10) ? 110 + (((unsigned long) (sz)) &gt;&gt; 12) :\
   ((((unsigned long) (sz)) &gt;&gt; 15) &lt;= 4) ? 119 + (((unsigned long) (sz)) &gt;&gt; 15) :\
   ((((unsigned long) (sz)) &gt;&gt; 18) &lt;= 2) ? 124 + (((unsigned long) (sz)) &gt;&gt; 18) :\
   126)

#define largebin_index(sz) \
  (SIZE_SZ == 8 ? largebin_index_64 (sz)                                     \
   : MALLOC_ALIGNMENT == 16 ? largebin_index_32_big (sz)                     \
   : largebin_index_32 (sz))
```

largebin中每个bin中含有chunk的大小都可能不一致，63个bin被分为6组，每组之间的公差一致，且链表头的bk指向最小的chunk。

### <a class="reference-link" name="5.tcache"></a>5.tcache

**<a class="reference-link" name="1.tcache_entry"></a>1.tcache_entry**

```
typedef struct tcache_entry  
`{`
  struct tcache_entry *next;     
  /* This field exists to detect double frees.  */
  struct tcache_perthread_struct *key;  //防止double free
`}` tcache_entry;
```

**<a class="reference-link" name="2.tcache_perthread_struct"></a>2.tcache_perthread_struct**

```
typedef struct tcache_perthread_struct
`{`
  char counts[TCACHE_MAX_BINS]; //设置tcache大小的数量，共64个
  tcache_entry *entries[TCACHE_MAX_BINS];  //设置entries为刚进入tcache的地址
`}` tcache_perthread_struct;
```

**<a class="reference-link" name="3.tcache_put(%E6%94%BE%E5%85%A5tcache%E4%B8%AD)"></a>3.tcache_put(放入tcache中)**

```
tcache_put (mchunkptr chunk, size_t tc_idx)
`{`
  tcache_entry *e = (tcache_entry *) chunk2mem (chunk);   //将e设值为chunk2mem(chunk)
  assert (tc_idx &lt; TCACHE_MAX_BINS);    //如果tc_idx小于7，则不报错，继续进行

  /* Mark this chunk as "in the tcache" so the test in _int_free will
     detect a double free.  */
  e-&gt;key = tcache;  //增加的保护

  e-&gt;next = tcache-&gt;entries[tc_idx];  
  tcache-&gt;entries[tc_idx] = e;
  ++(tcache-&gt;counts[tc_idx]);  //counts++
`}`
```

**<a class="reference-link" name="4.tcache_get(%E4%BB%8Etcache%E4%B8%AD%E5%8F%96%E5%87%BA)"></a>4.tcache_get(从tcache中取出)**

```
static __always_inline void *
tcache_get (size_t tc_idx)
`{`
  tcache_entry *e = tcache-&gt;entries[tc_idx]; //首先将e设值为最后进同大小tcache的块
  assert (tc_idx &lt; TCACHE_MAX_BINS);
  assert (tcache-&gt;entries[tc_idx] &gt; 0);
  tcache-&gt;entries[tc_idx] = e-&gt;next;  
  --(tcache-&gt;counts[tc_idx]);
  e-&gt;key = NULL;  
  return (void *) e;  
`}`
```



## 四：主要函数介绍

### <a class="reference-link" name="1.__libc_malloc"></a>1.__libc_malloc

```
void *
__libc_malloc (size_t bytes)
`{`
  mstate ar_ptr;
  void *victim;

  void *(*hook) (size_t, const void *)
    = atomic_forced_read (__malloc_hook);
  if (__builtin_expect (hook != NULL, 0))
    return (*hook)(bytes, RETURN_ADDRESS (0));   //此处可以看出，如果malloc_hook处不为空，就会执行，这就是为什么做pwn题时要覆盖hook的原因。
#if USE_TCACHE
  /* int_free also calls request2size, be careful to not pad twice.  */
  size_t tbytes;
  checked_request2size (bytes, tbytes);  
  size_t tc_idx = csize2tidx (tbytes);   //计算tcache的下标

  MAYBE_INIT_TCACHE ();    //如果tcache内为空，则进行初始化

  DIAG_PUSH_NEEDS_COMMENT;
  if (tc_idx &lt; mp_.tcache_bins
      /*&amp;&amp; tc_idx &lt; TCACHE_MAX_BINS*/ /* to appease gcc */
      &amp;&amp; tcache
      &amp;&amp; tcache-&gt;entries[tc_idx] != NULL)       //如果tc_idx合法并且tcache和其entries存在，则从tcache中返回chunk
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
```

### <a class="reference-link" name="2._int_malloc"></a>2._int_malloc

这段代码较长，大概500行，我们慢慢分析

```
static void *
_int_malloc (mstate av, size_t bytes)
`{`
  INTERNAL_SIZE_T nb;               /* normalized request size */
  unsigned int idx;                 /* associated bin index */
  mbinptr bin;                      /* associated bin */

  mchunkptr victim;                 /* inspected/selected chunk */
  INTERNAL_SIZE_T size;             /* its size */
  int victim_index;                 /* its bin index */

  mchunkptr remainder;              /* remainder from a split */
  unsigned long remainder_size;     /* its size */

  unsigned int block;               /* bit map traverser */
  unsigned int bit;                 /* bit map traverser */
  unsigned int map;                 /* current word of binmap */

  mchunkptr fwd;                    /* misc temp for linking */
  mchunkptr bck;                    /* misc temp for linking */

              //首先是定义一些变量 

#if USE_TCACHE
  size_t tcache_unsorted_count;        /* count of unsorted chunks processed */
#endif

  /*
     Convert request size to internal form by adding SIZE_SZ bytes
     overhead plus possibly more to obtain necessary alignment and/or
     to obtain a size of at least MINSIZE, the smallest allocatable
     size. Also, checked_request2size traps (returning 0) request sizes
     that are so large that they wrap around zero when padded and
     aligned.
   */
  //将用户请求的size大小对齐，并判断传入的参数大小是否符合要求,如果请求的size小于MIN_SIZE,则将请求的size改为MIN_SIZE
  checked_request2size (bytes, nb);

  /* There are no usable arenas.  Fall back to sysmalloc to get a chunk from
     mmap.  */
  if (__glibc_unlikely (av == NULL))   //如果没有可用的分配区，则调用sysmalloc分配
    `{`
      void *p = sysmalloc (nb, av);
      if (p != NULL)
    alloc_perturb (p, bytes);
      return p;
    `}`

  /*
     If the size qualifies as a fastbin, first check corresponding bin.
     This code is safe to execute even if av is not yet initialized, so we
     can try it without checking, which saves some time on this fast path.
   */

#define REMOVE_FB(fb, victim, pp)            \
  do                            \
    `{`                            \
      victim = pp;                    \
      if (victim == NULL)                \
    break;                        \
    `}`                            \
  while ((pp = catomic_compare_and_exchange_val_acq (fb, victim-&gt;fd, victim)) \
     != victim);                    \

  if ((unsigned long) (nb) &lt;= (unsigned long) (get_max_fast ()))   //如果转换后的size小于fastbin最大的size
    `{`
      idx = fastbin_index (nb);   //获取fastbin数组下标
      mfastbinptr *fb = &amp;fastbin (av, idx);  //得到链表头指针fb
      mchunkptr pp;
      victim = *fb;   //将victim赋值为fb

      if (victim != NULL)     //如果头不为空
    `{`
      if (SINGLE_THREAD_P)  
        *fb = victim-&gt;fd;   //将头指针赋值为victim-&gt;fd
      else
        REMOVE_FB (fb, pp, victim); //移除fb
      if (__glibc_likely (victim != NULL))
        `{`
          size_t victim_idx = fastbin_index (chunksize (victim)); 
          if (__builtin_expect (victim_idx != idx, 0))   //如果找到chunk，检查所分配的chunk 的size 与所在链表的size
        malloc_printerr ("malloc(): memory corruption (fast)");
          check_remalloced_chunk (av, victim, nb);  
#if USE_TCACHE     
          /* While we're here, if we see other chunks of the same size,
         stash them in the tcache.  */
          size_t tc_idx = csize2tidx (nb);   //得到申请该大小chunk的在fastbin中的下标
          if (tcache &amp;&amp; tc_idx &lt; mp_.tcache_bins)  //tcache存在并且其下标合法，则进入循环
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
              tcache_put (tc_victim, tc_idx);   //将剩余在fastbin中的chunk都放入相应大小的tcache中去，直到满足if条件
            `}`
        `}`
#endif
          void *p = chunk2mem (victim);
          alloc_perturb (p, bytes);
          return p;
        `}`
    `}`
    `}`

  /*
     If a small request, check regular bin.  Since these "smallbins"
     hold one size each, no searching within bins is necessary.
     (For a large request, we need to wait until unsorted chunks are
     processed to find best fit. But for small ones, fits are exact
     anyway, so we can check now, which is faster.)
   */

  if (in_smallbin_range (nb))    //如果申请的大小在tcach和fastbin中都不存在，就进入smallbin中寻找
    `{`
      idx = smallbin_index (nb);  
      bin = bin_at (av, idx);    //首先获取nb对应大小的smallbin下标和bin头地址

      if ((victim = last (bin)) != bin)   //只要对应nb大小的smallbin中不为空
        `{`
          bck = victim-&gt;bk;    //bck赋值为最后一个chunk即bin-&gt;bk
      if (__glibc_unlikely (bck-&gt;fd != victim))   //检查完整性
        malloc_printerr ("malloc(): smallbin double linked list corrupted");
          set_inuse_bit_at_offset (victim, nb);  //置1
          bin-&gt;bk = bck;  
          bck-&gt;fd = bin;   //解链完成

          if (av != &amp;main_arena)
        set_non_main_arena (victim);
          check_malloced_chunk (av, victim, nb);
#if USE_TCACHE
      /* While we're here, if we see other chunks of the same size,
         stash them in the tcache.  */
      size_t tc_idx = csize2tidx (nb);
      if (tcache &amp;&amp; tc_idx &lt; mp_.tcache_bins)  //又是和fastbin相同的stashing机制，就不多做解释了
        `{`
          mchunkptr tc_victim;

          /* While bin not empty and tcache not full, copy chunks over.  */
          while (tcache-&gt;counts[tc_idx] &lt; mp_.tcache_count
             &amp;&amp; (tc_victim = last (bin)) != bin)
        `{`
          if (tc_victim != 0)
            `{`
              bck = tc_victim-&gt;bk;
              set_inuse_bit_at_offset (tc_victim, nb);
              if (av != &amp;main_arena)
            set_non_main_arena (tc_victim);
              bin-&gt;bk = bck;
              bck-&gt;fd = bin;

              tcache_put (tc_victim, tc_idx);
                `}`
        `}`
        `}`
#endif
          void *p = chunk2mem (victim);
          alloc_perturb (p, bytes);
          return p;
        `}`
    `}`

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

  else   //到了这里，就是unsortedbin喽     
    `{` 
      idx = largebin_index (nb);   //获取下标
      if (atomic_load_relaxed (&amp;av-&gt;have_fastchunks))
        malloc_consolidate (av);   //如果fastbin中有chunk，则都合并进入unsortedbin中
    `}`

  /*
     Process recently freed or remaindered chunks, taking one only if
     it is exact fit, or, if this a small request, the chunk is remainder from
     the most recent non-exact fit.  Place other traversed chunks in
     bins.  Note that this step is the only place in any routine where
     chunks are placed in bins.

     The outer loop here is needed because we might not realize until
     near the end of malloc that we should have consolidated, so must
     do so and retry. This happens at most once, and only when we would
     otherwise need to expand memory to service a "small" request.
   */

#if USE_TCACHE
  INTERNAL_SIZE_T tcache_nb = 0;
  size_t tc_idx = csize2tidx (nb);
  if (tcache &amp;&amp; tc_idx &lt; mp_.tcache_bins)
    tcache_nb = nb;
  int return_cached = 0;

  tcache_unsorted_count = 0;
#endif

  for (;; )
    `{`
      int iters = 0;
      while ((victim = unsorted_chunks (av)-&gt;bk) != unsorted_chunks (av))  //因为之前先进行的malloc_consolidate，所以这里不会先检查largebin，先检查unsortedbin中是否有合适的，当unsortedbin不为空时，进入while循环
        `{`
          bck = victim-&gt;bk;   
          size = chunksize (victim);
          mchunkptr next = chunk_at_offset (victim, size);   //首先进行一些赋值，很好理解

          if (__glibc_unlikely (size &lt;= 2 * SIZE_SZ)     
              || __glibc_unlikely (size &gt; av-&gt;system_mem))    //如果申请的size小于16字节或者大于system_mem，报错
            malloc_printerr ("malloc(): invalid size (unsorted)");
          if (__glibc_unlikely (chunksize_nomask (next) &lt; 2 * SIZE_SZ)
              || __glibc_unlikely (chunksize_nomask (next) &gt; av-&gt;system_mem))  //下一个chunk的size是否在合理
            malloc_printerr ("malloc(): invalid next size (unsorted)");
          if (__glibc_unlikely ((prev_size (next) &amp; ~(SIZE_BITS)) != size))   //检查下一个chunk的prevsize是否与victim相同  
            malloc_printerr ("malloc(): mismatching next-&gt;prev_size (unsorted)");
          if (__glibc_unlikely (bck-&gt;fd != victim)
              || __glibc_unlikely (victim-&gt;fd != unsorted_chunks (av)))    //检查双向链表的完整性，不能进行unsortedbin attack了
            malloc_printerr ("malloc(): unsorted double linked list corrupted");
          if (__glibc_unlikely (prev_inuse (next)))    //下一个chunk的prev_inuse是否为1，为1则报错
            malloc_printerr ("malloc(): invalid next-&gt;prev_inuse (unsorted)");

          /*
             If a small request, try to use last remainder if it is the
             only chunk in unsorted bin.  This helps promote locality for
             runs of consecutive small requests. This is the only
             exception to best-fit, and applies only when there is
             no exact fit for a small chunk.
           */

          if (in_smallbin_range (nb) &amp;&amp;
              bck == unsorted_chunks (av) &amp;&amp;
              victim == av-&gt;last_remainder &amp;&amp;
              (unsigned long) (size) &gt; (unsigned long) (nb + MINSIZE)) //如果申请的大小等于输入small bin的范围，且unsorted bin链表中只有一个chunk并指向 last_remainder,且该chunk的size大小大于用户申请的szie大小
            `{`
              /* split and reattach remainder */
              remainder_size = size - nb;   //对chunk进行拆分，并获取剩下的大小和开始地址
              remainder = chunk_at_offset (victim, nb);
              unsorted_chunks (av)-&gt;bk = unsorted_chunks (av)-&gt;fd = remainder;  //更新av的bk和fd指针
              av-&gt;last_remainder = remainder; 
              remainder-&gt;bk = remainder-&gt;fd = unsorted_chunks (av); //更新remainder的fd和bk
              if (!in_smallbin_range (remainder_size))
                `{`
                  remainder-&gt;fd_nextsize = NULL;
                  remainder-&gt;bk_nextsize = NULL;
                `}`

              set_head (victim, nb | PREV_INUSE |
                        (av != &amp;main_arena ? NON_MAIN_ARENA : 0));
              set_head (remainder, remainder_size | PREV_INUSE);
              set_foot (remainder, remainder_size);

              check_malloced_chunk (av, victim, nb);  //检查分配的chunk
              void *p = chunk2mem (victim);
              alloc_perturb (p, bytes);
              return p;    
            `}`

          /* remove from unsorted list */
          if (__glibc_unlikely (bck-&gt;fd != victim))   
            malloc_printerr ("malloc(): corrupted unsorted chunks 3");
          unsorted_chunks (av)-&gt;bk = bck;
          bck-&gt;fd = unsorted_chunks (av);    //将victim解链

          /* Take now instead of binning if exact fit */
          if (size == nb)           //如果申请大小与victim相同，进入循环
            `{`
              set_inuse_bit_at_offset (victim, size);  
              if (av != &amp;main_arena)
        set_non_main_arena (victim);
#if USE_TCACHE
          /* Fill cache first, return to user only if cache fills.
         We may return one of these chunks later.  */
          if (tcache_nb
          &amp;&amp; tcache-&gt;counts[tc_idx] &lt; mp_.tcache_count)
        `{`
          tcache_put (victim, tc_idx);   //将victim插入tcache
          return_cached = 1;
          continue;
        `}`
          else    //否则，直接返回p
        `{`
#endif
              check_malloced_chunk (av, victim, nb);
              void *p = chunk2mem (victim);
              alloc_perturb (p, bytes);
              return p;
#if USE_TCACHE
        `}`
#endif
            `}`

          /* place chunk in bin */

          if (in_smallbin_range (size))    //如果victim的size是smallbin，且不满足前面的需求(即没有被分配)，将其插入smallbin中
            `{`
              victim_index = smallbin_index (size);
              bck = bin_at (av, victim_index);
              fwd = bck-&gt;fd;
            `}`
          else            //否则插入largebin
            `{`
              victim_index = largebin_index (size);
              bck = bin_at (av, victim_index);     
              fwd = bck-&gt;fd;

              /* maintain large bins in sorted order */
              if (fwd != bck)       //如果largebin非空
                `{`
                  /* Or with inuse bit to speed comparisons */
                  size |= PREV_INUSE;
                  /* if smaller than smallest, bypass loop below */
                  assert (chunk_main_arena (bck-&gt;bk));   
                  if ((unsigned long) (size)
              &lt; (unsigned long) chunksize_nomask (bck-&gt;bk))   //如果size比最小的largebin的堆块还小
                    `{`
                      fwd = bck;
                      bck = bck-&gt;bk;

                      victim-&gt;fd_nextsize = fwd-&gt;fd;
                      victim-&gt;bk_nextsize = fwd-&gt;fd-&gt;bk_nextsize;   //插入到最后一块
                      fwd-&gt;fd-&gt;bk_nextsize = victim-&gt;bk_nextsize-&gt;fd_nextsize = victim; //设置链表第一块chunk的bk_nextsize和原链表最后一个chunk的fd_nextsize设为victim
                    `}`
                  else   //将当前的chunk插入到large bin链表中的合适位置
                    `{`
                      assert (chunk_main_arena (fwd));
                      while ((unsigned long) size &lt; chunksize_nomask (fwd))  //如果size小于fwd也就是第一个chunk的size
                        `{`
                          fwd = fwd-&gt;fd_nextsize;    //则将fwd向前移
              assert (chunk_main_arena (fwd));
                        `}`

                      if ((unsigned long) size
              == (unsigned long) chunksize_nomask (fwd))    //如果size=fwd的size
                        /* Always insert in the second position.只插入第二个位置可能是因为不用再重新设置fd_nextsize和bk_nextsize  */  
                        fwd = fwd-&gt;fd;    //将fwd移到大小相同的最前
                      else                //将victim插入largebin最前面
                        `{`
                          victim-&gt;fd_nextsize = fwd;
                          victim-&gt;bk_nextsize = fwd-&gt;bk_nextsize;
                          fwd-&gt;bk_nextsize = victim;
                          victim-&gt;bk_nextsize-&gt;fd_nextsize = victim;   
                        `}`
                      bck = fwd-&gt;bk;  //重新设置bck
                    `}`
                `}`
              else   //只要largebin为空，直接加入bin中
                victim-&gt;fd_nextsize = victim-&gt;bk_nextsize = victim;
            `}`

          mark_bin (av, victim_index);
          victim-&gt;bk = bck;
          victim-&gt;fd = fwd;
          fwd-&gt;bk = victim;   //这里会有largebin attack
          bck-&gt;fd = victim;

#if USE_TCACHE
      /* If we've processed as many chunks as we're allowed while
     filling the cache, return one of the cached ones.  */
      ++tcache_unsorted_count;
      if (return_cached
      &amp;&amp; mp_.tcache_unsorted_limit &gt; 0
      &amp;&amp; tcache_unsorted_count &gt; mp_.tcache_unsorted_limit)
    `{`
      return tcache_get (tc_idx);
    `}`
#endif

#define MAX_ITERS       10000
          if (++iters &gt;= MAX_ITERS)
            break;
        `}`

#if USE_TCACHE
      /* If all the small chunks we found ended up cached, return one now.  */
      if (return_cached)
    `{`
      return tcache_get (tc_idx);
    `}`
#endif

      /*
         If a large request, scan through the chunks of current bin in
         sorted order to find smallest that fits.  Use the skip list for this.
       */

      if (!in_smallbin_range (nb))    //从largebin中搜寻
        `{`
          bin = bin_at (av, idx);     //首先取得largebin头

          /* skip scan if empty or largest chunk is too small */
          if ((victim = first (bin)) != bin   //不为空
          &amp;&amp; (unsigned long) chunksize_nomask (victim)  //申请的size小于等于victim的size
            &gt;= (unsigned long) (nb))
            `{`
              victim = victim-&gt;bk_nextsize;
              while (((unsigned long) (size = chunksize (victim)) &lt;
                      (unsigned long) (nb)))
                victim = victim-&gt;bk_nextsize;      //获取刚好小于用户请求的size 的large bin


              /* Avoid removing the first entry for a size so that the skip
                 list does not have to be rerouted.  */
              if (victim != last (bin)   
          &amp;&amp; chunksize_nomask (victim)
            == chunksize_nomask (victim-&gt;fd))   //last(bin)=bin-&gt;bk
                victim = victim-&gt;fd;     //获取同一大小chunk的最后的chunk

              remainder_size = size - nb;   //拆分largebin
              unlink_chunk (av, victim);    //解链

              /* Exhaust */
              if (remainder_size &lt; MINSIZE)   //如果被拆分后剩余chunk的size小于
                `{`
                  set_inuse_bit_at_offset (victim, size); //设置victim下一个chunk的prev_inuse，将剩余的chunk与被申请出去的合并(即和返回一个没有切割的chunk)
                  if (av != &amp;main_arena)
            set_non_main_arena (victim);
                `}`
              /* Split */
              else   
                `{`
                  remainder = chunk_at_offset (victim, nb);    //将剩余部分的chunk留在unsortedbin中
                  /* We cannot assume the unsorted list is empty and therefore
                     have to perform a complete insert here.  */
                  bck = unsorted_chunks (av);
                  fwd = bck-&gt;fd;
          if (__glibc_unlikely (fwd-&gt;bk != bck))
            malloc_printerr ("malloc(): corrupted unsorted chunks");
                  remainder-&gt;bk = bck;
                  remainder-&gt;fd = fwd;
                  bck-&gt;fd = remainder;
                  fwd-&gt;bk = remainder;
                  if (!in_smallbin_range (remainder_size))
                    `{`
                      remainder-&gt;fd_nextsize = NULL;
                      remainder-&gt;bk_nextsize = NULL;
                    `}`
                  set_head (victim, nb | PREV_INUSE |
                            (av != &amp;main_arena ? NON_MAIN_ARENA : 0));
                  set_head (remainder, remainder_size | PREV_INUSE);
                  set_foot (remainder, remainder_size);
                `}`
              check_malloced_chunk (av, victim, nb);
              void *p = chunk2mem (victim);
              alloc_perturb (p, bytes);
              return p;
            `}`
        `}`

      /*
         Search for a chunk by scanning bins, starting with next largest
         bin. This search is strictly by best-fit; i.e., the smallest
         (with ties going to approximately the least recently used) chunk
         that fits is selected.

         The bitmap avoids needing to check that most blocks are nonempty.
         The particular case of skipping all bins during warm-up phases
         when no chunks have been returned yet is faster than it might look.
       */
                //如果用户申请的size所对应的largebin中没有相应的chunk，则在其他largebin中进行寻找
      ++idx;
      bin = bin_at (av, idx);
      block = idx2block (idx);
      map = av-&gt;binmap[block];
      bit = idx2bit (idx);

      for (;; )
        `{`
          /* Skip rest of block if there are no more set bits in this block.  */
          if (bit &gt; map || bit == 0)
            `{`
              do
                `{`
                  if (++block &gt;= BINMAPSIZE) /* out of bins */
                    goto use_top;
                `}`
              while ((map = av-&gt;binmap[block]) == 0);

              bin = bin_at (av, (block &lt;&lt; BINMAPSHIFT));
              bit = 1;
            `}`

          /* Advance to bin with set bit. There must be one. */
          while ((bit &amp; map) == 0)
            `{`
              bin = next_bin (bin);
              bit &lt;&lt;= 1;
              assert (bit != 0);
            `}`

          /* Inspect the bin. It is likely to be non-empty */
          victim = last (bin);

          /*  If a false alarm (empty bin), clear the bit. */
          if (victim == bin)    //如果largebin不为空
            `{`
              av-&gt;binmap[block] = map &amp;= ~bit; /* Write through */
              bin = next_bin (bin);
              bit &lt;&lt;= 1;
            `}`

          else    //找到第一个大于申请size的chunk进行堆块划分，与之前的操作一样了，没什么说的
            `{`
              size = chunksize (victim);

              /*  We know the first chunk in this bin is big enough to use. */
              assert ((unsigned long) (size) &gt;= (unsigned long) (nb));

              remainder_size = size - nb;

              /* unlink */
              unlink_chunk (av, victim);

              /* Exhaust */
              if (remainder_size &lt; MINSIZE)
                `{`
                  set_inuse_bit_at_offset (victim, size);
                  if (av != &amp;main_arena)
            set_non_main_arena (victim);
                `}`

              /* Split */
              else
                `{`
                  remainder = chunk_at_offset (victim, nb);

                  /* We cannot assume the unsorted list is empty and therefore
                     have to perform a complete insert here.  */
                  bck = unsorted_chunks (av);
                  fwd = bck-&gt;fd;
          if (__glibc_unlikely (fwd-&gt;bk != bck))
            malloc_printerr ("malloc(): corrupted unsorted chunks 2");
                  remainder-&gt;bk = bck;
                  remainder-&gt;fd = fwd;
                  bck-&gt;fd = remainder;
                  fwd-&gt;bk = remainder;

                  /* advertise as last remainder */
                  if (in_smallbin_range (nb))
                    av-&gt;last_remainder = remainder;
                  if (!in_smallbin_range (remainder_size))
                    `{`
                      remainder-&gt;fd_nextsize = NULL;
                      remainder-&gt;bk_nextsize = NULL;
                    `}`
                  set_head (victim, nb | PREV_INUSE |
                            (av != &amp;main_arena ? NON_MAIN_ARENA : 0));
                  set_head (remainder, remainder_size | PREV_INUSE);
                  set_foot (remainder, remainder_size);
                `}`
              check_malloced_chunk (av, victim, nb);
              void *p = chunk2mem (victim);
              alloc_perturb (p, bytes);
              return p;
            `}`
        `}`

    use_top:
      /*
         If large enough, split off the chunk bordering the end of memory
         (held in av-&gt;top). Note that this is in accord with the best-fit
         search rule.  In effect, av-&gt;top is treated as larger (and thus
         less well fitting) than any other available chunk since it can
         be extended to be as large as necessary (up to system
         limitations).

         We require that av-&gt;top always exists (i.e., has size &gt;=
         MINSIZE) after initialization, so if it would otherwise be
         exhausted by current request, it is replenished. (The main
         reason for ensuring it exists is that we may need MINSIZE space
         to put in fenceposts in sysmalloc.)
       */
                //如果在所有的bin中都没有找到合适的chunk，就去top chunk中取
      victim = av-&gt;top;      //获取top地址
      size = chunksize (victim);   //获取top的size，top没有prev_size

      if (__glibc_unlikely (size &gt; av-&gt;system_mem))   //检查top chunk的合法性，这里导致了house of force不可用了，因为force需要改top size为一个很大的数(常用的是-1)，而-1在计算机中表示是(64位下)FFFFFFFFFFFFFFFF，明显大于system_mem
        malloc_printerr ("malloc(): corrupted top size");

      if ((unsigned long) (size) &gt;= (unsigned long) (nb + MINSIZE))  //如果top chunk的size大于等于nb+0x10,则切割
        `{`
          remainder_size = size - nb;
          remainder = chunk_at_offset (victim, nb);
          av-&gt;top = remainder;
          set_head (victim, nb | PREV_INUSE |
                    (av != &amp;main_arena ? NON_MAIN_ARENA : 0));
          set_head (remainder, remainder_size | PREV_INUSE);

          check_malloced_chunk (av, victim, nb);
          void *p = chunk2mem (victim);
          alloc_perturb (p, bytes);
          return p;
        `}`

      /* When we are using atomic ops to free fast chunks we can get
         here for all block sizes.  */
      else if (atomic_load_relaxed (&amp;av-&gt;have_fastchunks))  //如果top chunk size不够大，则合并fastbin到smallbin或者largebin中
        `{`
          malloc_consolidate (av);
          /* restore original bin index */
          if (in_smallbin_range (nb))
            idx = smallbin_index (nb);
          else
            idx = largebin_index (nb);
        `}`

      /*
         Otherwise, relay to handle system-dependent cases
       */
      else    //如果没有fastbin，直接用sysmalloc进行分配空间
        `{`
          void *p = sysmalloc (nb, av);
          if (p != NULL)
            alloc_perturb (p, bytes);
          return p;
        `}`
    `}`
`}`
```

### <a class="reference-link" name="3.__libc_free"></a>3.__libc_free

```
void
__libc_free (void *mem)
`{`
  mstate ar_ptr;
  mchunkptr p;                          /* chunk corresponding to mem */

  void (*hook) (void *, const void *)
    = atomic_forced_read (__free_hook);  //与malloc_hook同理
  if (__builtin_expect (hook != NULL, 0))
    `{`
      (*hook)(mem, RETURN_ADDRESS (0));
      return;
    `}`

  if (mem == 0)                              /* free(0) has no effect */
    return;

  p = mem2chunk (mem);

  if (chunk_is_mmapped (p))          ////判断chunk是否由mmap分配             
    `{`
      /* See if the dynamic brk/mmap threshold needs adjusting.
     Dumped fake mmapped chunks do not affect the threshold.  */
      if (!mp_.no_dyn_threshold            //如果是mmap，则首先更新mmap分配和收缩阈值
          &amp;&amp; chunksize_nomask (p) &gt; mp_.mmap_threshold
          &amp;&amp; chunksize_nomask (p) &lt;= DEFAULT_MMAP_THRESHOLD_MAX
      &amp;&amp; !DUMPED_MAIN_ARENA_CHUNK (p))
        `{`
          mp_.mmap_threshold = chunksize (p);
          mp_.trim_threshold = 2 * mp_.mmap_threshold;
          LIBC_PROBE (memory_mallopt_free_dyn_thresholds, 2,
                      mp_.mmap_threshold, mp_.trim_threshold);
        `}`
      munmap_chunk (p);   //然后调用 munmap_chunk释放函数
      return;
    `}`

  MAYBE_INIT_TCACHE ();

  ar_ptr = arena_for_chunk (p);//如果不是 mmap创建，则调用 _int_free 函数
  _int_free (ar_ptr, p, 0);
`}`
```

### <a class="reference-link" name="4._int_free"></a>4._int_free

```
static void
_int_free (mstate av, mchunkptr p, int have_lock)
`{`
  INTERNAL_SIZE_T size;        /* its size */
  mfastbinptr *fb;             /* associated fastbin */
  mchunkptr nextchunk;         /* next contiguous chunk */
  INTERNAL_SIZE_T nextsize;    /* its size */
  int nextinuse;               /* true if nextchunk is used */
  INTERNAL_SIZE_T prevsize;    /* size of previous contiguous chunk */
  mchunkptr bck;               /* misc temp for linking */
  mchunkptr fwd;               /* misc temp for linking */

  size = chunksize (p);

  /* Little security check which won't hurt performance: the
     allocator never wrapps around at the end of the address space.
     Therefore we can exclude some size values which might appear
     here by accident or by "design" from some intruder.  */
  if (__builtin_expect ((uintptr_t) p &gt; (uintptr_t) -size, 0)
      || __builtin_expect (misaligned_chunk (p), 0))
    malloc_printerr ("free(): invalid pointer");
  /* We know that each chunk is at least MINSIZE bytes in size or a
     multiple of MALLOC_ALIGNMENT.  */
  if (__glibc_unlikely (size &lt; MINSIZE || !aligned_OK (size)))
    malloc_printerr ("free(): invalid size");

  check_inuse_chunk(av, p);   //检查chunk是否在使用

#if USE_TCACHE
  `{`
    size_t tc_idx = csize2tidx (size);   
    if (tcache != NULL &amp;&amp; tc_idx &lt; mp_.tcache_bins)  
      `{`
    /* Check to see if it's already in the tcache.  */
    tcache_entry *e = (tcache_entry *) chunk2mem (p);

    /* This test succeeds on double free.  However, we don't 100%
       trust it (it also matches random payload data at a 1 in
       2^&lt;size_t&gt; chance), so verify it's not an unlikely
       coincidence before aborting.  */
    if (__glibc_unlikely (e-&gt;key == tcache))   
      `{`
        tcache_entry *tmp;
        LIBC_PROBE (memory_tcache_double_free, 2, e, tc_idx);
        for (tmp = tcache-&gt;entries[tc_idx];
         tmp;
         tmp = tmp-&gt;next)   //遍历同大小的tcache
          if (tmp == e)    //增加了double free的检测，不能向2.26那样无限free同一个chunk喽
        malloc_printerr ("free(): double free detected in tcache 2");
        /* If we get here, it was a coincidence.  We've wasted a
           few cycles, but don't abort.  */
      `}`

    if (tcache-&gt;counts[tc_idx] &lt; mp_.tcache_count)
      `{`
        tcache_put (p, tc_idx);  //若不重复，则将p放入tcache
        return;
      `}`
      `}`
  `}`
#endif

  /*
    If eligible, place chunk on a fastbin so it can be found
    and used quickly in malloc.
  */

  if ((unsigned long)(size) &lt;= (unsigned long)(get_max_fast ())  //检查size是否属于fastbin

#if TRIM_FASTBINS
      /*
    If TRIM_FASTBINS set, don't place chunks
    bordering top into fastbins
      */
      &amp;&amp; (chunk_at_offset(p, size) != av-&gt;top)   //并且下一个chunk不是top chunk
#endif
      ) `{`

    if (__builtin_expect (chunksize_nomask (chunk_at_offset (p, size))  //检查下一个chunk的size是否合法    
              &lt;= 2 * SIZE_SZ, 0)
    || __builtin_expect (chunksize (chunk_at_offset (p, size))
                 &gt;= av-&gt;system_mem, 0))
      `{`
    bool fail = true;
    /* We might not have a lock at this point and concurrent modifications
       of system_mem might result in a false positive.  Redo the test after
       getting the lock.  */ 
    if (!have_lock)
      `{`
        __libc_lock_lock (av-&gt;mutex);
        fail = (chunksize_nomask (chunk_at_offset (p, size)) &lt;= 2 * SIZE_SZ
            || chunksize (chunk_at_offset (p, size)) &gt;= av-&gt;system_mem);
        __libc_lock_unlock (av-&gt;mutex);
      `}`

    if (fail)
      malloc_printerr ("free(): invalid next size (fast)");  
      `}`

    free_perturb (chunk2mem(p), size - 2 * SIZE_SZ);

    atomic_store_relaxed (&amp;av-&gt;have_fastchunks, true);
    unsigned int idx = fastbin_index(size);
    fb = &amp;fastbin (av, idx);  //获得下标为idx的存储fastbin的地址 比如chunk:0x602010，获得的就是存储0x602010的栈地址

    /* Atomically link P to its fastbin: P-&gt;FD = *FB; *FB = P;  */
    mchunkptr old = *fb, old2;

    if (SINGLE_THREAD_P)
      `{`
    /* Check that the top of the bin is not the record we are going to
       add (i.e., double free).  */
    if (__builtin_expect (old == p, 0))  //这里没有遍历fastbin，所以依旧可以用free(a),free(b),free(a)的方式来绕过检测
      malloc_printerr ("double free or corruption (fasttop)");  
    p-&gt;fd = old;
    *fb = p;   //插入p并且更新fb的值
      `}`
    else
      do   
    `{`
      /* Check that the top of the bin is not the record we are going to
         add (i.e., double free).  */
      if (__builtin_expect (old == p, 0))  //如果重复释放的话，报错退出
        malloc_printerr ("double free or corruption (fasttop)");
      p-&gt;fd = old2 = old;   //将要被释放的chunk放入fastbin头部，修改其fd 指针指向Old
    `}`
      while ((old = catomic_compare_and_exchange_val_rel (fb, p, old2))
         != old2);

    /* Check that size of fastbin chunk at the top is the same as
       size of the chunk that we are adding.  We can dereference OLD
       only if we have the lock, otherwise it might have already been
       allocated again.  */
    if (have_lock &amp;&amp; old != NULL
    &amp;&amp; __builtin_expect (fastbin_index (chunksize (old)) != idx, 0))
      malloc_printerr ("invalid fastbin entry (free)");
  `}`

  /*
    Consolidate other non-mmapped chunks as they arrive.
  */

  else if (!chunk_is_mmapped(p)) `{`

    /* If we're single-threaded, don't lock the arena.  */
    if (SINGLE_THREAD_P)  
      have_lock = true;

    if (!have_lock)
      __libc_lock_lock (av-&gt;mutex);

    nextchunk = chunk_at_offset(p, size);   //得到nextchunk的位置

    /* Lightweight tests: check whether the block is already the
       top block.  */
    if (__glibc_unlikely (p == av-&gt;top))     //如果p是top头，报错退出
      malloc_printerr ("double free or corruption (top)");
    /* Or whether the next chunk is beyond the boundaries of the arena.  */
    if (__builtin_expect (contiguous (av)   //判断nextchunk是否超过分配区，如果是的话，退出报错
              &amp;&amp; (char *) nextchunk
              &gt;= ((char *) av-&gt;top + chunksize(av-&gt;top)), 0))
    malloc_printerr ("double free or corruption (out)");
    /* Or whether the block is actually not marked used.  */
    if (__glibc_unlikely (!prev_inuse(nextchunk)))   //如果nextchunk的prev_inuse位是0，说明p已经被释放过了，再释放属于double free
      malloc_printerr ("double free or corruption (!prev)");

    nextsize = chunksize(nextchunk);   //得到nextchunk的size
    if (__builtin_expect (chunksize_nomask (nextchunk) &lt;= 2 * SIZE_SZ, 0)
     || __builtin_expect (nextsize &gt;= av-&gt;system_mem, 0))   //判断nextchunk size的合法性
       malloc_printerr ("free(): invalid next size (normal)");

    free_perturb (chunk2mem(p), size - 2 * SIZE_SZ);   //清楚要被释放的chunk的内容，即置0

    /* consolidate backward */
    if (!prev_inuse(p)) `{`       //若p的inuse位为0，则代表p的前一个chunk属于释放状态，进入循环
      prevsize = prev_size (p);  //获得前一个chunk的size
      size += prevsize;    //重置一下size
      p = chunk_at_offset(p, -((long) prevsize));  //更新p的位置，包含前一个chunk和p
      if (__glibc_unlikely (chunksize(p) != prevsize))   //因为现在更新后p的size位还没有更新，所以现在p的size还是没有更新p之前的size(即p的上一个chunk的size大小)
        malloc_printerr ("corrupted size vs. prev_size while consolidating");
      unlink_chunk (av, p);  //执行解链，这是向后合并
    `}`

    if (nextchunk != av-&gt;top) `{`
      /* get and clear inuse bit */
      nextinuse = inuse_bit_at_offset(nextchunk, nextsize);  //nextchunk的prev_inuse位归0

      /* consolidate forward */
      if (!nextinuse) `{`  //向前合并
    unlink_chunk (av, nextchunk);
    size += nextsize;
      `}` else
    clear_inuse_bit_at_offset(nextchunk, 0);  //如果nextchunk在使用，就讲其prev_inuse位置0

      /*
    Place the chunk in unsorted chunk list. Chunks are
    not placed into regular bins until after they have
    been given one chance to be used in malloc.
      */

      bck = unsorted_chunks(av);    //获得unsortedbin的头
      fwd = bck-&gt;fd;  //获得unsortedbin的第一个chunk                
      if (__glibc_unlikely (fwd-&gt;bk != bck))
    malloc_printerr ("free(): corrupted unsorted chunks");
      p-&gt;fd = fwd;  
      p-&gt;bk = bck;   //插入unsortedbin中
      if (!in_smallbin_range(size))  
    `{`
      p-&gt;fd_nextsize = NULL;
      p-&gt;bk_nextsize = NULL;
    `}`
      bck-&gt;fd = p;  
      fwd-&gt;bk = p;  //重置bck和fwd

      set_head(p, size | PREV_INUSE);
      set_foot(p, size);

      check_free_chunk(av, p);   //检查是否free掉了
    `}`

    /*
      If the chunk borders the current high end of memory,
      consolidate into top
    */

    else `{`     //如果nextchunk是top chunk的话，对top chunk进行更新
      size += nextsize;    
      set_head(p, size | PREV_INUSE);
      av-&gt;top = p;
      check_chunk(av, p);  
    `}`

    /*
      If freeing a large space, consolidate possibly-surrounding
      chunks. Then, if the total unused topmost memory exceeds trim
      threshold, ask malloc_trim to reduce top.

      Unless max_fast is 0, we don't know if there are fastbins
      bordering top, so we cannot tell for sure whether threshold
      has been reached unless fastbins are consolidated.  But we
      don't want to consolidate on each free.  As a compromise,
      consolidation is performed if FASTBIN_CONSOLIDATION_THRESHOLD
      is reached.
    */

    if ((unsigned long)(size) &gt;= FASTBIN_CONSOLIDATION_THRESHOLD) `{` 
      if (atomic_load_relaxed (&amp;av-&gt;have_fastchunks))
    malloc_consolidate(av);

      if (av == &amp;main_arena) `{`
#ifndef MORECORE_CANNOT_TRIM
    if ((unsigned long)(chunksize(av-&gt;top)) &gt;=
        (unsigned long)(mp_.trim_threshold))
      systrim(mp_.top_pad, av);
#endif
      `}` else `{`
    /* Always try heap_trim(), even if the top chunk is not
       large, because the corresponding heap might go away.  */
    heap_info *heap = heap_for_ptr(top(av));

    assert(heap-&gt;ar_ptr == av);
    heap_trim(heap, mp_.top_pad);
      `}`
    `}`

    if (!have_lock)
      __libc_lock_unlock (av-&gt;mutex);
  `}`
  /*
    If the chunk was allocated via mmap, release via munmap().
  */

  else `{`
    munmap_chunk (p);
  `}`
`}`
```

只要属于fastbin大小，free掉都不会与top chunk合并

### <a class="reference-link" name="5.unlink"></a>5.unlink

```
/* Take a chunk off a bin list.  */
static void
unlink_chunk (mstate av, mchunkptr p)   //unlink顾名思义，就是将一个chunk从bin中解链出来，p是将要释放的chunk
`{`
  if (chunksize (p) != prev_size (next_chunk (p)))      //第一个检查
    malloc_printerr ("corrupted size vs. prev_size");

  mchunkptr fd = p-&gt;fd;
  mchunkptr bk = p-&gt;bk;

  if (__builtin_expect (fd-&gt;bk != p || bk-&gt;fd != p, 0))   //第二个检查
    malloc_printerr ("corrupted double-linked list");

  fd-&gt;bk = bk;
  bk-&gt;fd = fd;
  if (!in_smallbin_range (chunksize_nomask (p)) &amp;&amp; p-&gt;fd_nextsize != NULL)
    `{`
      if (p-&gt;fd_nextsize-&gt;bk_nextsize != p
      || p-&gt;bk_nextsize-&gt;fd_nextsize != p)
    malloc_printerr ("corrupted double-linked list (not small)");

      if (fd-&gt;fd_nextsize == NULL)
    `{`
      if (p-&gt;fd_nextsize == p)
        fd-&gt;fd_nextsize = fd-&gt;bk_nextsize = fd;
      else
        `{`
          fd-&gt;fd_nextsize = p-&gt;fd_nextsize;
          fd-&gt;bk_nextsize = p-&gt;bk_nextsize;
          p-&gt;fd_nextsize-&gt;bk_nextsize = fd;
          p-&gt;bk_nextsize-&gt;fd_nextsize = fd;
        `}`
    `}`
      else
    `{`
      p-&gt;fd_nextsize-&gt;bk_nextsize = p-&gt;bk_nextsize;
      p-&gt;bk_nextsize-&gt;fd_nextsize = p-&gt;fd_nextsize;
    `}`
    `}`
`}`
```

在free(p)的时候(大小不是fastbin就行)，如果p的前后是释放状态的话会发生向前合并或者向后合并，其中**向后合并**的时(即unlink_chunk (av, **p**) )，有一项检查，就是检查p的size和nextchunk的prevsize是否一致，这个检查与unlink_chunk中第一个检查一致。然后就要通过伪造来过掉第二个检查。 首先伪造p的prev_inuse和prev_size，然后在prev_chunk中伪造一个假的chunk，使其能通过第一个检查，再伪造prev_chunk的fd和bk指针通过第二个检查。

如果p的下一个chunk属于释放状态，执行向前合并( 即unlink_chunk (av, **nextchunk**) )，向前合并没有单独的检查，就只有在unlink_chunk中的两个检查，可以先修改nextchunk的nextchunk的prev_inuse为0，然后改nextchunk的nextchunk的prev_size为nextchunk的size，最后再修改nextchunk的fd和bk指针就好。

这里多说一点，向前合并不需要伪造一个假chunk是因为在_int_free的源代码中对p的nextchunk做了定义(nextchunk = chunk_at_offset(p, size))，如果我们要伪造一个假chunk也是可以的，就是比较麻烦了。总之，多去看源码就能明白啦！！！

在此之后的分析，就是一些攻击手法了，不过我写的很简略(供自己复习一下)



## 五：常用的攻击手法

### <a class="reference-link" name="1.fastbin%20dup%20into%20consolidate"></a>1.fastbin dup into consolidate

就是利用malloc_consolidate函数将已经放入fastbin中的p送入unsortedbin，然后再释放p，就可以达到p即在fastbin中，又在unsortedbin中

### <a class="reference-link" name="2.fastbin%20dup%20into%20stack"></a>2.fastbin dup into stack

比较简单，就是利用绕过double free来实现可以分配到栈的内存

### <a class="reference-link" name="3.fastbin%20reverse%20into%20tcache"></a>3.fastbin reverse into tcache

注：我们设最先进入bin或者tcache的chunk为最后一个chunk，最后进入的是第一个chunk，这样比较好描述一点(比较符合从左到右的思想)

因为在_int_malloc中的fastbin的stash机制，在malloc从fastbin中取出一个chunk之后，只要在fastbin中还有相同大小的chunk且tcache的个数不足7的话，就会将fastbin中的chunk送入tcache。我们假设有这么一种情况，0x50大小的tcache数量为0，有7个0x50大小的fastbin，能通过溢出或者其他方式使fastbin的最后的chunk的fd为一个栈地址，然后malloc(0x50)，那个栈地址就会进入到tcache的第一的位置。

### <a class="reference-link" name="4.tcache%20poisoning"></a>4.tcache poisoning

直接修改tcache中bin的fd指针

### <a class="reference-link" name="5.tcache%20house%20of%20spirit"></a>5.tcache house of spirit

在栈上伪造一个chunk，只伪造size位即可，并且将其user空间的首地址赋值给一个变量，然后释放这个变量，最后再malloc回来，就可以控制这块区域

### <a class="reference-link" name="6.tcache%20stashing%20unlink(%E8%87%B3%E5%B0%91%E8%A6%81%E6%9C%89%E4%B8%80%E6%AC%A1calloc%E7%9A%84%E6%9C%BA%E4%BC%9A%EF%BC%8C%E5%9B%A0%E4%B8%BAcalloc%E4%B8%8D%E4%BB%8Etcache%E4%B8%AD%E6%8B%BFchunk)"></a>6.tcache stashing unlink(至少要有一次calloc的机会，因为calloc不从tcache中拿chunk)

能达到向任意地址+0x10写一个libc地址和申请一个chunk在任何位置

### <a class="reference-link" name="7.house%20of%20force(&lt;2.29)"></a>7.house of force(&lt;2.29)

扩充top chunk，然后分配到想要分配的地方，进行任意写

### <a class="reference-link" name="8.house%20of%20spirit"></a>8.house of spirit

其和tcache的这个攻击手法不同的地方是，普通的需要伪造nextchunk的size来过检查

```
if (have_lock
    || (`{` assert (locked == 0);
      mutex_lock(&amp;av-&gt;mutex);
      locked = 1;
      chunk_at_offset (p, size)-&gt;size &lt;= 2 * SIZE_SZ
        || chunksize (chunk_at_offset (p, size)) &gt;= av-&gt;system_mem;  //过这个检查哦！！！
      `}`))
  `{`
    errstr = "free(): invalid next size (fast)";
    goto errout;
```

### <a class="reference-link" name="9.house%20of%20orange(%E7%A8%8B%E5%BA%8F%E6%B2%A1%E6%9C%89free%E6%97%B6%E5%8F%AF%E4%BB%A5%E8%80%83%E8%99%91%E8%BF%99%E7%A7%8D%E6%94%BB%E5%87%BB)"></a>9.house of orange(程序没有free时可以考虑这种攻击)

需要泄露libc和heap地址，需要将*_IO_list_all伪造成unsortedbin的头(main_arena+0x58)，然后再伪造 _IO_list_all的chain和mode，write_ptr,write_base，最重要的是伪造vtable[3]为system的地址，”/bin/sh\x00”在头部(因为 _IO_OVERFLOW(fp,EOF))

### <a class="reference-link" name="10.largebin%20attack"></a>10.largebin attack

_int_malloc在对largebin的操作在2.30之后多加入了两项检查。

#### <a class="reference-link" name="1.glibc2.29%E5%8F%8A%E4%B8%80%E4%B8%8B%E7%9A%84largebin%20attack"></a>1.glibc2.29及一下的largebin attack

```
else
            `{`
              victim_index = largebin_index (size);
              bck = bin_at (av, victim_index);  //bck为largebin的头
              fwd = bck-&gt;fd;   //fwd为largebin中第一个chunk

              /* maintain large bins in sorted order */
              if (fwd != bck)   //如果该下标的bin中不为空
                `{`
                  /* Or with inuse bit to speed comparisons */
                  size |= PREV_INUSE;
                  /* if smaller than smallest, bypass loop below */
                  assert (chunk_main_arena (bck-&gt;bk));
                  if ((unsigned long) (size)  
              &lt; (unsigned long) chunksize_nomask (bck-&gt;bk))       //并且从unsortedbin中来的chunk大小小于该下标中chunk中最小的，进入vuln函数
                    `{`
                      fwd = bck;      //更新fwd为largebin头
                      bck = bck-&gt;bk;  //更新bck为largebin中最小的chunk

                      victim-&gt;fd_nextsize = fwd-&gt;fd;  //victim就是即将插入的chunk，设置fd_nextsize为该下标中最大chunk
                      victim-&gt;bk_nextsize = fwd-&gt;fd-&gt;bk_nextsize;  //设置bk_nextsize为最大chunk的bk_nextsize
                      fwd-&gt;fd-&gt;bk_nextsize = victim-&gt;bk_nextsize-&gt;fd_nextsize = victim;   //漏洞点，如果我们能够伪造第一个chunk的bk_nextsize为我们想要写入数据的地方-0x20，就可以赋值为victim
                    `}`
```

#### <a class="reference-link" name="2.glibc2.30%E4%B9%8B%E5%90%8E%E7%9A%84largebin%20attack"></a>2.glibc2.30之后的largebin attack

```
/*  if ((unsigned long) (size)&lt; (unsigned long) chunksize_nomask (bck-&gt;bk))不成立的话，进入下面的循环 */       
                    else
                    `{`
                      assert (chunk_main_arena (fwd));
                      while ((unsigned long) size &lt; chunksize_nomask (fwd))   //如果小于fwd的size，就向后找chunk，直到size&gt;=chunksize_nomask（fwd），我们需要绕过这个循环
                        `{`
                          fwd = fwd-&gt;fd_nextsize;
              assert (chunk_main_arena (fwd));
                        `}`

                      if ((unsigned long) size
              == (unsigned long) chunksize_nomask (fwd))
                        /* Always insert in the second position.  */
                        fwd = fwd-&gt;fd;    
                      else          //主要的利用在这里，当size&gt;chunksize_nomask（fwd）
                        `{`
                          victim-&gt;fd_nextsize = fwd; //
                          victim-&gt;bk_nextsize = fwd-&gt;bk_nextsize;
                          if (__glibc_unlikely (fwd-&gt;bk_nextsize-&gt;fd_nextsize != fwd))
                            malloc_printerr ("malloc(): largebin double linked list corrupted (nextsize)");
                          fwd-&gt;bk_nextsize = victim;  
                          victim-&gt;bk_nextsize-&gt;fd_nextsize = victim;
                        `}`
                      bck = fwd-&gt;bk;             
                      if (bck-&gt;fd != fwd)
                        malloc_printerr ("malloc(): largebin double linked list corrupted (bk)");
                    `}`
                `}`
              else   //空
                victim-&gt;fd_nextsize = victim-&gt;bk_nextsize = victim;
            `}`    

          mark_bin (av, victim_index);
          victim-&gt;bk = bck;
          victim-&gt;fd = fwd;
          fwd-&gt;bk = victim;
          bck-&gt;fd = victim;
```

堆部分就先写这些吧，为了过面试呜呜，还要去复习栈
