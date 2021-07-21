> 原文链接: https://www.anquanke.com//post/id/242443 


# ptmalloc malloc部分源码分析


                                阅读量   
                                **96942**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t016e5651f3d525516e.png)](https://p4.ssl.qhimg.com/t016e5651f3d525516e.png)



ptmalloc是glibc的默认管理器，我们常用的malloc和free就是由ptmalloc提供的内存分配函数，对malloc部分的代码进行分析。在分配器中，为了解决多线程锁的争夺问题，分为了主分配区和非主分配区，每个进程有一个主分配区，还可以有多个非主分配区。主分配区用brk和mmap来分配，但是非主分配区使用mmap来映射内存。接下来我们对院代码进行分析。调用malloc函数的时候，又调用了__libc_malloc函数，接下来看下该函数的源码

```
void *
__libc_malloc( size_t bytes )
`{`
    mstate    ar_ptr;
    void    *victim;

    void( hook ) ( size_t, const void )
        = atomic_forced_read( malloc_hook );
    if ( builtin_expect( hook != NULL, 0 ) )
        return( (hook) (bytes, RETURN_ADDRESS( 0 ) ) );

    arena_lookup( ar_ptr );

    arena_lock( ar_ptr, bytes );
    if ( !ar_ptr )
        return(0);

    victim = _int_malloc( ar_ptr, bytes );
    if ( !victim )
    `{`
        LIBC_PROBE( memory_malloc_retry, 1, bytes );
        ar_ptr = arena_get_retry( ar_ptr, bytes );
        if ( __builtin_expect( ar_ptr != NULL, 1 ) )
        `{`
            victim = _int_malloc( ar_ptr, bytes );
            (void) mutex_unlock( &amp;ar_ptr-&gt;mutex );
        `}`
    `}`else
        (void) mutex_unlock( &amp;ar_ptr-&gt;mutex );
    assert( !victim || chunk_is_mmapped( mem2chunk( victim ) ) ||
        ar_ptr == arena_for_chunk( mem2chunk( victim ) ) );
    return(victim);
`}`
```

其次，再看这个之前，需要先补充一点概念，先看下面这结构体

```
struct malloc_state
`{`
  /* Serialize access.  */
  mutex_t mutex;

  /* Flags (formerly in max_fast).  */
  int flags;

  /* Fastbins */
  mfastbinptr fastbinsY[NFASTBINS];

  /* Base of the topmost chunk -- not otherwise kept in a bin */
  mchunkptr top;

  /* The remainder from the most recent split of a small request */
  mchunkptr last_remainder;

  /* Normal bins packed as described above */
  mchunkptr bins[NBINS * 2 - 2];

  /* Bitmap of bins */
  unsigned int binmap[BINMAPSIZE];

  /* Linked list */
  struct malloc_state *next;

  /* Linked list for free arenas.  */
  struct malloc_state *next_free;

  /* Memory allocated from the system in this arena.  */
  INTERNAL_SIZE_T system_mem;
  INTERNAL_SIZE_T max_system_mem;
`}`;
```

在这个里面，我们需要先知道是如何对这些东西进行管理的，这里需要知道的是arena，heap，chunk三个。
1. arena在开始说过，该结构主要存储的是一些较高层次的信息。arena的数量是有限的，满了以后就不再创建而是与其他的进行共享。如果该arena没有线程使用，就上锁，防止冲突，可以用来保证多线程堆空间的分配的高效。
1. heap的话就是存储着堆的相关信息。
1. chunk的话则是分配的内存单位，当我们进行申请的时候，就会得到一个chunk。
有了这个概念以后，再看上面的结构体，加上注释就可能好理解一点上面的结构体成员作如下理解。<br>
mutex是互斥锁，前面说到的arena为了解决多线程冲突的问题，所以如果使用了该arena，会进行上锁。<br>
后面的flags是标志位标志着一些特征，这里不做深入只需要有个概念。fastbins是一个链表后面再做解释，top指的是top chunk，bins也是一个chunk的链表数组，next指针指向的是下一个malloc_state的位置。而后面那个*next_free指针是指向下一个未使用的malloc_state的位置。最后两个结构体成员则是和系统目前分配的内存总量有关。回到__libc_malloc的源码,声明了一个结构体一个指针。然后

```
void *(*hook) (size_t, const void *)
= atomic_forced_read (__malloc_hook);
```

这个地方我们可以看一下宏定义

```
#define atomic_forced_read( x )    \

(`{` typeof(x)x; asm ("" : "=r" (x) : "0" (x) ); __x; `}`)
```

typeof是返回类型，后面的是一段汇编代码，此处看内联汇编。该宏定义操作就是原子读，源代码处就是把malloc_hook函数地址放入任意寄存器再取出。而__malloc_hook函数的定义如下

```
void *weak_variable (*__malloc_hook)(size_t __size, const void *) = malloc_hook_ini;
```

__malloc_hook_ini的定义如下

```
static void * malloc_hook_ini (size_t sz, const void *caller)`{`
__malloc_hook = NULL;
ptmalloc_init ();
return __libc_malloc (sz);
`}`
```

在ptmalloc中定义了一个hook，如果我们需要自定义堆分配函数，就可以把malloc_hook设置成我们自定义的函数，申请完成直接返回。如果我们没有自定义分配函数，那就会进入ptmalloc_init函数，该函数进行初始化，然后调用libc_malloc函数。<br>
回到_libc_malloc的代码，关于arena_get函数，其作用就是获取当前的arena。然后调用int_malloc函数，后面如果我们ini_malloc函数分配失败，并且我们可以找到一个可用的arena，那就用尝试另一个arena。接下来分析int_malloc函数<br>
函数开头声明了变量，根据注释可以理解。后面会慢慢解释

```
INTERNAL_SIZE_T nb;              normalized request size * /

unsigned int idx;                       /* associated bin index /
                                         * mbinptr bin;                      / associated bin */

mchunkptr victim;                       /* inspected/selected chunk /
                                         * INTERNAL_SIZE_T size;             / its size /
                                         * int victim_index;                 / its bin index */

mchunkptr remainder;                    /* remainder from a split /
                                         * unsigned long remainder_size;     / its size */

unsigned int block;                     /* bit map traverser /
                                         * unsigned int bit;                 / bit map traverser /
                                         * unsigned int map;                 / current word of binmap */

mchunkptr fwd;                          /* misc temp for linking /
                                         * mchunkptr bck;                    / misc temp for linking */

const char *errstr = NULL;
```

接下来，有一个宏，这个宏定义如下

```
#define request2size( req )                        \

( ( (req) + SIZE_SZ + MALLOC_ALIGN_MASK &lt; MINSIZE)  ?          \
    MINSIZE :                               \
    ( (req) + SIZE_SZ + MALLOC_ALIGN_MASK) &amp; ~MALLOC_ALIGN_MASK)
```

在这里先引入chunk的定义，

```
struct malloc_chunk `{`

INTERNAL_SIZE_T prev_size;
INTERNAL_SIZE_T size;

struct malloc_chunk* fd; 
struct malloc_chunk* bk;

struct malloc_chunk* fd_nextsize; /* double links -- used only if free. */
struct malloc_chunk* bk_nextsize;
`}`;
```

这是chunk的结构体，下面是具体的结构，可以看出来，当一个chunk不被使用的时候，我们为了管理，至少需要prev_size，size，fd，bk这四个结构，所以一个chunk的最小大小，必须要有这几个结构，在request2size的宏定义里面的MINSIZE就是指最小大小。

```
chunk-&gt; +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |             Size of previous chunk                            |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
`head:' |             Size of chunk, in bytes                         |P|
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
```

当一个chunk在被使用的时候结构如下。所以这时候至少需要req+SIZE_SZ大小的内存，MALLOC_ALIGN_MASK用于对齐。

```
chunk-&gt; +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |             Size of previous chunk, if allocated            | |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |             Size of chunk, in bytes                       |M|P|
  mem-&gt; +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |             User data starts here...                          .
    .                                                               .
    .             (malloc_usable_size() bytes)                      .
    .                                                               |
nextchunk-&gt; +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |             Size of chunk                                     |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

到这里，这个宏定义的作用就是将请求的size转换成对应chunk的大小。

```
if ((unsigned long) (nb) &lt;= (unsigned long) (get_max_fast ()))
`{`
  idx = fastbin_index (nb);
  mfastbinptr *fb = &amp;fastbin (av, idx);
  mchunkptr pp = *fb;
  do
    `{`
      victim = pp;
      if (victim == NULL)
        break;
    `}`
  while ((pp = catomic_compare_and_exchange_val_acq (fb, victim-&gt;fd, victim))
         != victim);
  if (victim != 0)
    `{`
      if (__builtin_expect (fastbin_index (chunksize (victim)) != idx, 0))
        `{`
          errstr = "malloc(): memory corruption (fast)";
        errout:
          malloc_printerr (check_action, errstr, chunk2mem (victim));
          return NULL;
        `}`
      check_remalloced_chunk (av, victim, nb);
      void *p = chunk2mem (victim);
      alloc_perturb (p, bytes);
      return p;
    `}`
`}`
```

进入了一个if判断，后面的get_max_fast返回的是fastbin里面存储的最大值，经过request2size转换后的nb小于fastbin存储的最大值，那就先调用fastbin_index获取对应的索引，然后通过fastbin宏获得链表指针。这里的两个宏定义如下

```
#define fastbin_index( sz ) \

( ( ( (unsigned int) (sz) ) &gt;&gt; (SIZE_SZ == 8 ? 4 : 3) ) - 2)

#define fastbin( ar_ptr, idx ) ( (ar_ptr)-&gt;fastbinsY[idx])
```

下面进入了一个 do while 循环。此处是通过单链表的fd指针，指向下一个空闲chunk（victim -&gt; fd），直到fd指针指向的地方为 NULL ，再下面的代码进行了检查，用 fastbin_index 宏对该 chunk 的 size 进行检查，判断是否属于该 idx 对应的索引。获得空闲的 chunk 后，就用 chunk2mem 得到内存指针，然后调用 alloc_perturb 进行初始化，返回该内存指针。假设 fastbin 中寻找失败，就进入下一步，这时候从 smallbin 中尝试。

```
if (in_smallbin_range (nb))
`{`
  idx = smallbin_index (nb);
  bin = bin_at (av, idx);

  if ((victim = last (bin)) != bin)
    `{`
      if (victim == 0) /* initialization check */
        malloc_consolidate (av);
      else
        `{`
          bck = victim-&gt;bk;
if (__glibc_unlikely (bck-&gt;fd != victim))
            `{`
              errstr = "malloc(): smallbin double linked list corrupted";
              goto errout;
            `}`
          set_inuse_bit_at_offset (victim, nb);
          bin-&gt;bk = bck;
          bck-&gt;fd = bin;

          if (av != &amp;main_arena)
            victim-&gt;size |= NON_MAIN_ARENA;
          check_malloced_chunk (av, victim, nb);
          void *p = chunk2mem (victim);
          alloc_perturb (p, bytes);
          return p;
        `}`
    `}`
`}`
```

首先，if里面的判断，该宏定义如下

```
#define in_smallbin_range( sz )     \

( (unsigned long) (sz) &lt; (unsigned long) MIN_LARGE_SIZE)
```

该处基于我的本地计算后，512字节，也就是说，当nb的大小小于512字节时候，就满足该if判断，bin_at的宏定义如下

```
#define bin_at( m, i ) \

(mbinptr) ( ( (char *) &amp;( (m)-&gt;bins[( (i) - 1) * 2]) )             \
        - offsetof( struct malloc_chunk, fd ) )
```

根据smallbin_index获取索引，通过bin_at获得链表指针。

```
#define last(b)      ((b)-&gt;bk)
```

此时的bin是smallbin的链表头，那么last(bin)实际上就是获得链表的最后一个chunk，而这里的检查也是判断该链表是否为空，如果不空，则进入到下面的代码。假设链表不为空，再进行一次判断，如果victim为0，则代表smallbin还没有初始化，调用malloc_consolidate进行初始化。如果不为0，说明已经初始化完成，那么后面接着往下走进入else，再对链表的完整性进行检查。此时因为smallbin的检查都通过了，那么根据大小索引出的链表，我们可以从中取出一个chunk，设置下一个chunk的PREV_INUSE的bit位，然后解链，取出该链表的最后一个chunk，在设置取出chunk的bit位，进行检查后返回内存指针。到此时。那么，如果不属于smallbin的大小的话，那就是属于largebin的大小，进入到else处的代码

```
if ( in_smallbin_range( nb ) )
`{`
    ... ...
`}`else   `{`
    idx = largebin_index( nb );
    if ( have_fastchunks( av ) )
        malloc_consolidate( av );
`}`
```

这里则是通过largebin_index获取idx后，首先检查了fastbin里是否有空闲的chunk，有的话先对fastbin里面的chunk进行合并。做完这些后，进入一个大的for循环

```
int iters = 0;
while ( (victim = unsorted_chunks( av )-&gt;bk) != unsorted_chunks( av ) )
`{`
    bck = victim-&gt;bk;
    if ( __builtin_expect( victim-&gt;size &lt;= 2 * SIZE_SZ, 0 )
         || __builtin_expect( victim-&gt;size &gt; av-&gt;system_mem, 0 ) )
        malloc_printerr( check_action, "malloc(): memory corruption",
                 chunk2mem( victim ) );
    size = chunksize( victim );
    if ( in_smallbin_range( nb ) &amp;&amp;
         bck == unsorted_chunks( av ) &amp;&amp;
         victim == av-&gt;last_remainder &amp;&amp;
         (unsigned long) (size) &gt; (unsigned long) (nb + MINSIZE) )
    `{`
        /* split and reattach remainder */
        remainder_size            = size - nb;
        remainder            = chunk_at_offset( victim, nb );
        unsorted_chunks( av )-&gt;bk    = unsorted_chunks( av )-&gt;fd = remainder;
        av-&gt;last_remainder        = remainder;
        remainder-&gt;bk            = remainder-&gt;fd = unsorted_chunks( av );
        if ( !in_smallbin_range( remainder_size ) )
        `{`
            remainder-&gt;fd_nextsize    = NULL;
            remainder-&gt;bk_nextsize    = NULL;
        `}`

        set_head( victim, nb | PREV_INUSE |
              (av != &amp;main_arena ? NON_MAIN_ARENA : 0) );
        set_head( remainder, remainder_size | PREV_INUSE );
        set_foot( remainder, remainder_size );

        check_malloced_chunk( av, victim, nb );
        void *p = chunk2mem( victim );
        alloc_perturb( p, bytes );
        return(p);
    `}`

    /* remove from unsorted list */
    unsorted_chunks( av )-&gt;bk    = bck;
    bck-&gt;fd                = unsorted_chunks( av );

    /* Take now instead of binning if exact fit */

    if ( size == nb )
    `{`
        set_inuse_bit_at_offset( victim, size );
        if ( av != &amp;main_arena )
            victim-&gt;size |= NON_MAIN_ARENA;
        check_malloced_chunk( av, victim, nb );
        void *p = chunk2mem( victim );
        alloc_perturb( p, bytes );
        return(p);
    `}`
```

这段的话就进入到了遍历unsortedbin的阶段（注：该出代码省略了最外圈的for循环，这里依然是一个遍历过程），从unsortedbin的最后面的chunk开始往前遍历，通过检查以后，获得当前chunk的size，如果大小是在smallbin的范围内，并且unsortedbin里面只有一个chunk，还为last_reamainder的话，而且他的大小可以满足要求，那就对该chunk进行切割，并且设置好bit位，再把剩余的部分作为新的last_remainder链接到unsortedbin，如果剩下的部分超过了512字节也就是属于largebin部分，把fd_nextsize和bk_nextsize进行置空，然后把切割下来的那部分作为chunk返回，同时设置好相关的bit位，进行检查。当然，如果不满足条件则进行跳过该部分，将我们得到的unsortedbin的chunk进行解链，如果我们进行解链的chunk的size刚好符合nb，那就设置标志位，直接返回该victim。所以这里是一边寻找一边整理chunk。

```
int iters = 0;
  while ((victim = unsorted_chunks (av)-&gt;bk) != unsorted_chunks (av))
    `{`
      bck = victim-&gt;bk;
      if (__builtin_expect (victim-&gt;size &lt;= 2 * SIZE_SZ, 0)
          || __builtin_expect (victim-&gt;size &gt; av-&gt;system_mem, 0))
        malloc_printerr (check_action, "malloc(): memory corruption",
                         chunk2mem (victim));
      size = chunksize (victim);
            ......
            ......
            ......

      /* place chunk in bin */

      if (in_smallbin_range (size))
        `{`
          victim_index = smallbin_index (size);
          bck = bin_at (av, victim_index);
          fwd = bck-&gt;fd;
        `}`
      else
        `{`
          victim_index = largebin_index (size);
          bck = bin_at (av, victim_index);
          fwd = bck-&gt;fd;

          /* maintain large bins in sorted order */
          if (fwd != bck)
            `{`
              /* Or with inuse bit to speed comparisons */
              size |= PREV_INUSE;
              /* if smaller than smallest, bypass loop below */
              assert ((bck-&gt;bk-&gt;size &amp; NON_MAIN_ARENA) == 0);
              if ((unsigned long) (size) &lt; (unsigned long) (bck-&gt;bk-&gt;size))
                `{`
                  fwd = bck;
                  bck = bck-&gt;bk;

                  victim-&gt;fd_nextsize = fwd-&gt;fd;
                  victim-&gt;bk_nextsize = fwd-&gt;fd-&gt;bk_nextsize;
                  fwd-&gt;fd-&gt;bk_nextsize = victim-&gt;bk_nextsize-&gt;fd_nextsize = victim;
                `}`
              else
                `{`
                  assert ((fwd-&gt;size &amp; NON_MAIN_ARENA) == 0);
                  while ((unsigned long) size &lt; fwd-&gt;size)
                    `{`
                      fwd = fwd-&gt;fd_nextsize;
                      assert ((fwd-&gt;size &amp; NON_MAIN_ARENA) == 0);
                    `}`

                  if ((unsigned long) size == (unsigned long) fwd-&gt;size)
                    /* Always insert in the second position.  */
                    fwd = fwd-&gt;fd;
                  else
                    `{`
                      victim-&gt;fd_nextsize = fwd;
                      victim-&gt;bk_nextsize = fwd-&gt;bk_nextsize;
                      fwd-&gt;bk_nextsize = victim;
                      victim-&gt;bk_nextsize-&gt;fd_nextsize = victim;
                    `}`
                  bck = fwd-&gt;bk;
                `}`
            `}`
          else
            victim-&gt;fd_nextsize = victim-&gt;bk_nextsize = victim;
        `}`

      mark_bin (av, victim_index);
      victim-&gt;bk = bck;
      victim-&gt;fd = fwd;
      fwd-&gt;bk = victim;
      bck-&gt;fd = victim;

#define MAX_ITERS       10000
      if (++iters &gt;= MAX_ITERS)
        break;
    `}`
```

如果我们取出来的chunk大小不符合要求，就进行合并，那么进行合并，我们就需要判断其大小属于哪个范围，首先判断如果是属于smallbin的范围，一样的，获取索引，将链表指针赋值给bck、fwd为该链表的第一个chunk跳过else部分，看后面的插入操作，也就是

```
mark_bin (av, victim_index);
  victim-&gt;bk = bck;
  victim-&gt;fd = fwd;
  fwd-&gt;bk = victim;
  bck-&gt;fd = victim;

#define MAX_ITERS       10000
  if (++iters &gt;= MAX_ITERS)
    break;
```

这部分代码，此处的mak_bin是用来标识chunk的，在binmap中，用bit位来标识该chunk是否空闲。这里的插入操作根据代码来看，首先把我们从unsortedbin中获得的chunk的bk指向链表指针，fd指向原本的第一个chunk，再把链表指针的fd和原本第一个chunk的bk指针指向victim，这里是插入到了链表的头部。到这是属于smallbin的，那么如果是属于largebin的呢？我们回到else的代码部分，在这个部分里，用largebin_index获取对应的索引，然后通过索引获得对应的链表指针，如果fwd和bck相等了，则说明此时的链表为空，直接进入到后面的插入操作。并且将fd_nextsize和bk_nextsize指向自己。如果不为空，则直接获得最小size的chunk，也就是从bck-&gt; bk指向最后面的chunk，如果该chunk的size比最小的还要小，就不用遍历，直接更新fwd和bck，把链表指针赋值给fwd，bck指向最小的chunk，下面就是将chunk链接进去的操作，将fd_nextsize指向最大的chunk，再把最大chunk的bk_nextsize指向该chunk，形成循环。如果比最小的chunk大的话，用while循环，找到应该插入的位置，在largebin中，如果大小相同的chunk，用最先释放进去的chunk作为堆头，通过fd_nextsisze和bk_nextsize和其他堆头进行链接，后续还有大小一致的chunk的话，就插入到堆头的后面，不去修改堆头。所以该处有个大小的判断，如果找到了，那就总是插入到第二个chunk的位置处。如果没有一样大小的话，那就是把这个chunk作为新的堆头，下面的else里面就是对fd_nextsize和bk_nextsize进行设置。同时最后是由插入操作的，所以需要更新下bck的值。注意，这里的链表是有顺序的，也就是除了头部和尾部的chunk，fd_nextsize要永远指向比自己小的chunk，bk_nextsize要永远指向比自己大的chunk。此时关于我们从unsortedbin中取出的chunk的整理完了。接下来继续我们的分配

```
if (!in_smallbin_range (nb))
    `{`
      bin = bin_at (av, idx);

      /* skip scan if empty or largest chunk is too small */
      if ((victim = first (bin)) != bin &amp;&amp;
          (unsigned long) (victim-&gt;size) &gt;= (unsigned long) (nb))
        `{`
          victim = victim-&gt;bk_nextsize;
          while (((unsigned long) (size = chunksize (victim)) &lt;
                  (unsigned long) (nb)))
            victim = victim-&gt;bk_nextsize;

          /* Avoid removing the first entry for a size so that the skip
             list does not have to be rerouted.  */
          if (victim != last (bin) &amp;&amp; victim-&gt;size == victim-&gt;fd-&gt;size)
            victim = victim-&gt;fd;

          remainder_size = size - nb;
          unlink (victim, bck, fwd);

          /* Exhaust */
          if (remainder_size &lt; MINSIZE)
            `{`
              set_inuse_bit_at_offset (victim, size);
              if (av != &amp;main_arena)
                victim-&gt;size |= NON_MAIN_ARENA;
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
                `{`
                  errstr = "malloc(): corrupted unsorted chunks";
                  goto errout;
                `}`
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
```

这里的话就是要从largebin中取出chunk了，一样的，用idx获得索引，用索引获得对应的链表指针，看这个if的判断条件，first的宏定义

```
#define first(b)     ((b)-&gt;fd)
```

判断这里的是否为空，或者最大的chunk都不能满足请求的size，那就进入else的部分，而这里的一样的使用了remainder这个chunk，区别就是不能断定此时的unsortedbin里面是否是空的，插入操作需要注意一下。回到if哪里，如果条件可以满足，那就获得最小的那个chunk，然后往前遍历，找到size大于nb的第一个chunk，同样，避免修改堆头的指针，找到以后，因为不是恰好满足，所以需要分割，第一部分返回给用户，第二部分分两种情况，如果size小于MINSIZE，就不能当做最小的chunk了，那就一整个的返回给用户，如果可以，那就把剩余的部分当做remainder插入进去unsortedbin中。再继续往下看

```
++idx;
bin    = bin_at( av, idx );
block    = idx2block( idx );
map    = av-&gt;binmap[block];
bit    = idx2bit( idx );

for (;; )
`{`
    /* Skip rest of block if there are no more set bits in this block.  */
    if ( bit &gt; map || bit == 0 )
    `{`
        do
        `{`
            if ( ++block &gt;= BINMAPSIZE ) /* out of bins */
                goto use_top;
        `}`
        while ( (map = av-&gt;binmap[block]) == 0 );

        bin    = bin_at( av, (block &lt;&lt; BINMAPSHIFT) );
        bit    = 1;
    `}`

    /* Advance to bin with set bit. There must be one. */
    while ( (bit &amp; map) == 0 )
    `{`
        bin    = next_bin( bin );
        bit    &lt;&lt;= 1;
        assert( bit != 0 );
    `}`

    /* Inspect the bin. It is likely to be non-empty */
    victim = last( bin );
    if ( victim == bin )
    `{`
        av-&gt;binmap[block]    = map &amp;= ~bit; /* Write through */
        bin            = next_bin( bin );
        bit            &lt;&lt;= 1;
    `}`else    `{`
        size = chunksize( victim );

        /*  We know the first chunk in this bin is big enough to use. */
        assert( (unsigned long) (size) &gt;= (unsigned long) (nb) );

        remainder_size = size - nb;

        /* unlink */
        unlink( victim, bck, fwd );

        /* Exhaust */
        if ( remainder_size &lt; MINSIZE )
        `{`
            set_inuse_bit_at_offset( victim, size );
            if ( av != &amp;main_arena )
                victim-&gt;size |= NON_MAIN_ARENA;
        `}`
        /* Split */
        else`{`
            remainder = chunk_at_offset( victim, nb );


            /* We cannot assume the unsorted list is empty and therefore
             * have to perform a complete insert here.  */
            bck    = unsorted_chunks( av );
            fwd    = bck-&gt;fd;
            if ( __glibc_unlikely( fwd-&gt;bk != bck ) )
            `{`
                errstr = "malloc(): corrupted unsorted chunks 2";
                goto errout;
            `}`
            remainder-&gt;bk    = bck;
            remainder-&gt;fd    = fwd;
            bck-&gt;fd        = remainder;
            fwd-&gt;bk        = remainder;

            /* advertise as last remainder */
            if ( in_smallbin_range( nb ) )
                av-&gt;last_remainder = remainder;
            if ( !in_smallbin_range( remainder_size ) )
            `{`
                remainder-&gt;fd_nextsize    = NULL;
                remainder-&gt;bk_nextsize    = NULL;
            `}`
            set_head( victim, nb | PREV_INUSE |
                  (av != &amp;main_arena ? NON_MAIN_ARENA : 0) );
            set_head( remainder, remainder_size | PREV_INUSE );
            set_foot( remainder, remainder_size );
        `}`
        check_malloced_chunk( av, victim, nb );
        void *p = chunk2mem( victim );
        alloc_perturb( p, bytes );
        return(p);
    `}`
`}`
```

通过前面的部分，还没有找到满足要求的chunk的话，就改变idx，++idx就是代表着从下一个更大的链表里面进行寻找，之前说过binmap，现在详解说下，一个bit位表示对应位置是否有空闲chunk，1为真，0为假，然后

```
/* Conservatively use 32 bits per map word, even if on 64bit system */
#define BINMAPSHIFT      5
#define BITSPERMAP       (1U &lt;&lt; BINMAPSHIFT)
#define BINMAPSIZE       (NBINS / BITSPERMAP)//128 100000

#define idx2block(i)     ((i) &gt;&gt; BINMAPSHIFT)
#define idx2bit(i)       ((1U &lt;&lt; ((i) &amp; ((1U &lt;&lt; BINMAPSHIFT) - 1))))

#define mark_bin(m, i)    ((m)-&gt;binmap[idx2block (i)] |= idx2bit (i))
#define unmark_bin(m, i)  ((m)-&gt;binmap[idx2block (i)] &amp;= ~(idx2bit (i)))
#define get_binmap(m, i)  ((m)-&gt;binmap[idx2block (i)] &amp; idx2bit (i))
```

相关的宏定义在这，一共有4个block，也就是4*4个字节，共128个bit管理bin数组，所以这里的计算就是获取所属block，然后获取map，进入循环，如果bit大于map，则说明没有满足的空闲的chunk，所以需要找下一个block。如果找到了，则获得对应的链表指针，并且满足对应链表不为空，就是和上面的largebin一样的操作。此处的话补充一下，bins的长度为127，前面6个为smallbin，后64个为largebin，下标为1的第一个bin为unsortedbin。如果遍历完没有的话，就轮到topchunk了

```
use_top:

  victim = av-&gt;top;
  size = chunksize (victim);

  if ((unsigned long) (size) &gt;= (unsigned long) (nb + MINSIZE))
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
  else if (have_fastchunks (av))
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
  else
    `{`
      void *p = sysmalloc (nb, av);
      if (p != NULL)
        alloc_perturb (p, bytes);
      return p;
    `}`
```

这里的话，首先比较下topchunk的size是否满足nb+MINSIZE，然后 满足的话，就是一样的切割，设置标志位，进行检查，然后返回切割下来的部分给用户。更新topchunk。还没找到合适的chunk，检查fastbin，如果有空闲chunk，进行合并整理，回到for循环。最后没找到，就用sysmalloc函数进行分配。代码里可以看到，在else if的代码里。有malloc_co函数，那么这里就对补上malloc_consolidate的分析

```
static void malloc_consolidate( mstate av )
`{`
    mfastbinptr* fb;               /* current fastbin being consolidated /
                                    * mfastbinptr    maxfb;              /* last fastbin (for loop control) /
                                    * mchunkptr       p;                  / current chunk being consolidated /
                                    * mchunkptr       nextp;              / next chunk to consolidate /
                                    * mchunkptr       unsorted_bin;       / bin header /
                                    * mchunkptr       first_unsorted;     / chunk to link to */

    /* These have same use as in free() */
    mchunkptr    nextchunk;
    INTERNAL_SIZE_T size;
    INTERNAL_SIZE_T nextsize;
    INTERNAL_SIZE_T prevsize;
    int        nextinuse;
    mchunkptr    bck;
    mchunkptr    fwd;

    if ( get_max_fast() != 0 )
    `{`
        clear_fastchunks( av );


        unsorted_bin = unsorted_chunks( av );


        maxfb    = &amp;fastbin( av, NFASTBINS - 1 );
        fb    = &amp;fastbin( av, 0 );
        do
        `{`
            p = atomic_exchange_acq( fb, 0 );
            if ( p != 0 )
            `{`
                do
                `{`
                    check_inuse_chunk( av, p );
                    nextp = p-&gt;fd;

                    /* Slightly streamlined version of consolidation code in free() */
                    size        = p-&gt;size &amp; ~(PREV_INUSE | NON_MAIN_ARENA);
                    nextchunk    = chunk_at_offset( p, size );
                    nextsize    = chunksize( nextchunk );

                    if ( !prev_inuse( p ) )
                    `{`
                        prevsize    = p-&gt;prev_size;
                        size        += prevsize;
                        p        = chunk_at_offset( p, -( (long) prevsize) );
                        unlink( p, bck, fwd );
                    `}`

                    if ( nextchunk != av-&gt;top )
                    `{`
                        nextinuse = inuse_bit_at_offset( nextchunk, nextsize );

                        if ( !nextinuse )
                        `{`
                            size += nextsize;
                            unlink( nextchunk, bck, fwd );
                        `}` else
                            clear_inuse_bit_at_offset( nextchunk, 0 );

                        first_unsorted        = unsorted_bin-&gt;fd;
                        unsorted_bin-&gt;fd    = p;
                        first_unsorted-&gt;bk    = p;

                        if ( !in_smallbin_range( size ) )
                        `{`
                            p-&gt;fd_nextsize    = NULL;
                            p-&gt;bk_nextsize    = NULL;
                        `}`

                        set_head( p, size | PREV_INUSE );
                        p-&gt;bk    = unsorted_bin;
                        p-&gt;fd    = first_unsorted;
                        set_foot( p, size );
                    `}`else  `{`
                        size += nextsize;
                        set_head( p, size | PREV_INUSE );
                        av-&gt;top = p;
                    `}`
                `}`
                while ( (p = nextp) != 0 );
            `}`
        `}`
        while ( fb++ != maxfb );
    `}`else   `{`
        malloc_init_state( av );
        check_malloc_state( av );
    `}`
`}`
```

先判断是否进行了初始化，初始化了以后进入到if里面，然后使用clear_fastchunks进行标志位设置，

```
#define clear_fastchunks(M)    catomic_or (&amp;(M)-&gt;flags, FASTCHUNKS_BIT)
```

然后通过unsorted_chunks获得链表指针，获得fastbin中的最大和最小的chunk。进入到do while循环遍历fastbin中的链表。然后将fb指针取出，并且将链表头设置为0，再次进入do while循环，通过fd指针进行该链表的chunk的遍历，清除bit位。首先判断前面的chunk有没有在使用，如果没有，就把她进行合并，并把指针更新，unlink取出前一个chunk。再往下，如果下一个chunk不是topchunk，那就判断下一个chunk，如果下一个chunk也是空闲，一起合并，unlink取出下一个chunk。如果没有空闲，更新prev_inuse位，表示前一个chunk未使用。然后把合并后的chunk放入到unsortedbin里面，如果合并后的chunk的size属于smallbin的话，需要清除fd_nextsize和bk_nextsize；然后设置头部完善双链。设置脚部。如果下一个chunk是topchunk，那就直接并入topchunk中，然后更新topchunk的size和内存指针。

最后，整个流程为
1. 先看请求的大小，先判断是否属于fastbin，从fastbin中进行查找。
1. 进入到判断smallbin的流程，如果smallbin为空，也就是没有初始化，进行整合初始化；如果是一个largebin大小的请求，并且fastbin里面有chunk，进行整合。
1. 遍历unsortedbin中的chunk，一边查找一边将里面的chunk按照大小进行插入。当我们的请求属于smallbin并且unsortedbin中有且只有一个last_remainder的时候，切割last_remainder；或者找到大小刚好适合的chunk返回。
1. 整理完unsortedbin后，从largebin中进行查找，此时如果largebin为空或者最大的chunk的size小于请求的大小，切割remainder。
1. 从largebin中大于指定的大小的链表进行查找，找到的话，和在largebin中的操作大致一致。
1. 从topchunk中进行分配，topchunk不行，如果fastbin中有空闲的chunk的话，合并fastbin中的chunk加入到unsortedbin中，再从3开始进行；如果fastbin中没有，sysmalloc进行分配