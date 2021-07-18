
# Kernel Pwn 学习之路（三）


                                阅读量   
                                **464243**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/202371/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/202371/t012b90699683ce2270.jpg)](./img/202371/t012b90699683ce2270.jpg)



## 0x01 前言

由于关于Kernel安全的文章实在过于繁杂，本文有部分内容大篇幅或全文引用了参考文献，若出现此情况的，将在相关内容的开头予以说明，部分引用参考文献的将在文件结尾的参考链接中注明。

Kernel的相关知识以及一些实例在Kernel中的利用已经在Kernel Pwn 学习之路(一)(二)给予了说明，本文主要介绍了Kernel中`slub`分配器的相关知识。

【传送门】：[Kernel Pwn 学习之路(一)](https://www.anquanke.com/post/id/201043)

【传送门】：[Kernel Pwn 学习之路(二)](https://www.anquanke.com/post/id/201454)

⚠️：本文中的所有源码分析以`Linux Kernel 4.15.15`为例。



## 0x02 buddy system (伙伴系统)

Linux内核内存管理的一项重要工作就是如何在频繁申请释放内存的情况下，避免碎片的产生。Linux采用伙伴系统解决外部碎片的问题，采用slab解决内部碎片的问题，在这里我们先讨论外部碎片问题。避免外部碎片的方法有两种：一种是之前介绍过的利用非连续内存的分配；另外一种则是用一种有效的方法来监视内存，保证在内核只要申请一小块内存的情况下，不会从大块的连续空闲内存中截取一段过来，从而保证了大块内存的连续性和完整性。显然，前者不能成为解决问题的普遍方法，一来用来映射非连续内存线性地址空间有限，二来每次映射都要改写内核的页表，进而就要刷新TLB，这使得分配的速度大打折扣，这对于要频繁申请内存的内核显然是无法忍受的。因此Linux采用后者来解决外部碎片的问题，也就是著名的伙伴系统。

伙伴系统的宗旨就是用最小的内存块来满足内核的对于内存的请求。在最初，只有一个块，也就是整个内存，假如为1M大小，而允许的最小块为64K，那么当我们申请一块200K大小的内存时，就要先将1M的块分裂成两等分，各为512K，这两分之间的关系就称为伙伴，然后再将第一个512K的内存块分裂成两等分，各位256K，将第一个256K的内存块分配给内存，这样就是一个分配的过程。



## 0x02 Kernel slub 分配器

`Linux`的物理内存管理采用了以页为单位的`buddy system`(伙伴系统)，但是很多情况下，内核仅仅需要一个较小的对象空间，而且这些小块的空间对于不同对象又是变化的、不可预测的，所以需要一种类似用户空间堆内存的管理机制(`malloc/free`)。然而内核对对象的管理又有一定的特殊性，有些对象的访问非常频繁，需要采用缓冲机制；对象的组织需要考虑硬件`cache`的影响；需要考虑多处理器以及`NUMA`架构的影响。90年代初期，在`Solaris 2.4`操作系统中，采用了一种称为`slab`（原意是大块的混凝土）的缓冲区分配和管理方法，在相当程度上满足了内核的特殊需求。

多年以来，`SLAB`成为`linux kernel`对象缓冲区管理的主流算法，甚至长时间没有人愿意去修改，因为它实在是非常复杂，而且在大多数情况下，它的工作完成的相当不错。

但是，随着大规模多处理器系统和 `NUMA`系统的广泛应用，`SLAB`分配器逐渐暴露出自身的严重不足：
1. 缓存队列管理复杂；
1. 管理数据存储开销大；
1. 对NUMA支持复杂；
1. 调试调优困难；
1. 摒弃了效果不太明显的slab着色机制；
针对这些`SLAB`不足，内核开发人员`Christoph Lameter`在`Linux`内核`2.6.22`版本中引入一种新的解决方案：`SLUB`分配器。`SLUB`分配器特点是简化设计理念，同时保留`SLAB`分配器的基本思想：每个缓冲区由多个小的`slab`组成，每个 `slab`包含固定数目的对象。`SLUB`分配器简化`kmem_cache`，`slab`等相关的管理数据结构，摒弃了`SLAB`分配器中众多的队列概念，并针对多处理器、`NUMA`系统进行优化，从而提高了性能和可扩展性并降低了内存的浪费。为了保证内核其它模块能够无缝迁移到`SLUB`分配器，`SLUB`还保留了原有`SLAB`分配器所有的接口`API`函数。



## 0x02 Kernel slub 内存管理数据结构

首先给出一张经典的结构图

[![](./img/202371/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-03-22-144151.png)

可以看到，slub分配器首先会管理若干个`kmem_cache`，这些`kmem_cache`将构成一个大的**双向循环列表**，这个列表的头为`slab_caches`，其中`kmalloc_caches`管理着若干定长的`kmem_cache`，分别是`kmalloc-8`到`kmalloc-0x2004`，以步长为8递增。(此处事实上非常类似于`GLibc`内存管理中`Fastbin`的管理方式)

每一个固定程度的`kmem_cache`都有以下数据结构：(`/source/include/linux/slub_def.h#L82`)

```
/*
 * Slab cache management.
 */
struct kmem_cache {
    struct kmem_cache_cpu __percpu *cpu_slab;
    /* Used for retriving partial slabs etc */
    slab_flags_t flags;
    unsigned long min_partial;
    int size;        /* The size of an object including meta data */
    int object_size;    /* The size of an object without meta data */
    int offset;        /* Free pointer offset. */
#ifdef CONFIG_SLUB_CPU_PARTIAL
    int cpu_partial;    /* Number of per cpu partial objects to keep around */
#endif
    struct kmem_cache_order_objects oo;

    /* Allocation and freeing of slabs */
    struct kmem_cache_order_objects max;
    struct kmem_cache_order_objects min;
    gfp_t allocflags;    /* gfp flags to use on each alloc */
    int refcount;        /* Refcount for slab cache destroy */
    void (*ctor)(void *);
    int inuse;        /* Offset to metadata */
    int align;        /* Alignment */
    int reserved;        /* Reserved bytes at the end of slabs */
    int red_left_pad;    /* Left redzone padding size */
    const char *name;    /* Name (only for display!) */
    struct list_head list;    /* List of slab caches */
#ifdef CONFIG_SYSFS
    struct kobject kobj;    /* For sysfs */
    struct work_struct kobj_remove_work;
#endif
#ifdef CONFIG_MEMCG
    struct memcg_cache_params memcg_params;
    int max_attr_size; /* for propagation, maximum size of a stored attr */
#ifdef CONFIG_SYSFS
    struct kset *memcg_kset;
#endif
#endif

#ifdef CONFIG_SLAB_FREELIST_HARDENED
    unsigned long random;
#endif

#ifdef CONFIG_NUMA
    /*
     * Defragmentation by allocating from a remote node.
     */
    int remote_node_defrag_ratio;
#endif

#ifdef CONFIG_SLAB_FREELIST_RANDOM
    unsigned int *random_seq;
#endif

#ifdef CONFIG_KASAN
    struct kasan_cache kasan_info;
#endif

    struct kmem_cache_node *node[MAX_NUMNODES];
};
```

此处我们暂且不关心其他的成员变量，首先关注`struct kmem_cache_cpu __percpu *cpu_slab;`和`struct kmem_cache_node *node[MAX_NUMNODES];`

那么我们首先来看`struct kmem_cache_node *node[MAX_NUMNODES];`：(`/source/mm/slab.h#L453`)

```
struct kmem_cache_node {
    spinlock_t list_lock;

#ifdef CONFIG_SLAB
    struct list_head slabs_partial;    /* partial list first, better asm code */
    struct list_head slabs_full;
    struct list_head slabs_free;
    unsigned long total_slabs;    /* length of all slab lists */
    unsigned long free_slabs;    /* length of free slab list only */
    unsigned long free_objects;
    unsigned int free_limit;
    unsigned int colour_next;    /* Per-node cache coloring */
    struct array_cache *shared;    /* shared per node */
    struct alien_cache **alien;    /* on other nodes */
    unsigned long next_reap;    /* updated without locking */
    int free_touched;        /* updated without locking */
#endif

#ifdef CONFIG_SLUB
    unsigned long nr_partial;
    struct list_head partial;
#ifdef CONFIG_SLUB_DEBUG
    atomic_long_t nr_slabs;
    atomic_long_t total_objects;
    struct list_head full;
#endif
#endif

};
```

这个结构体我们称之为节点，值得注意的是`struct list_head`这个结构体，正如他们的名字所示，这三个结构体的成员变量分别表示部分使用的`slab`、全部使用的`slab`、全部空闲的`slab`，这个结构体的实现也很简单，就是一个前导指针和一个后向指针而已：(`/source/include/linux/types.h#L186`)

```
struct list_head {
    struct list_head *next, *prev;
};
```



## 0x03 slub分配器的初始化

### `kmem_cache_init()`源码分析

`kmem_cache_init()`是`slub`分配算法的入口函数：(在`/source/include/linux/slab.c#L4172`处实现)

那么我们来看这个结构体：(“)

```
void __init kmem_cache_init(void)
{
    static __initdata struct kmem_cache boot_kmem_cache,boot_kmem_cache_node;

    if (debug_guardpage_minorder())
        slub_max_order = 0;

    kmem_cache_node = &amp;boot_kmem_cache_node;
    kmem_cache = &amp;boot_kmem_cache;

    // 调用 create_boot_cache 创建 kmem_cache_node 对象缓冲区
    create_boot_cache(kmem_cache_node, "kmem_cache_node",
        sizeof(struct kmem_cache_node), SLAB_HWCACHE_ALIGN);

    // 用于注册内核通知链回调
    register_hotmemory_notifier(&amp;slab_memory_callback_nb);

    /* Able to allocate the per node structures */
    slab_state = PARTIAL;

    // 调用 create_boot_cache 创建 kmem_cache 对象缓冲区
    create_boot_cache(kmem_cache, "kmem_cache",
            offsetof(struct kmem_cache, node) +
                nr_node_ids * sizeof(struct kmem_cache_node *),
               SLAB_HWCACHE_ALIGN);

    // 将临时kmem_cache向最终kmem_cache迁移，并修正相关指针，使其指向最终的kmem_cache
    kmem_cache = bootstrap(&amp;boot_kmem_cache);

    /*
     * Allocate kmem_cache_node properly from the kmem_cache slab.
     * kmem_cache_node is separately allocated so no need to
     * update any list pointers.
     */
    kmem_cache_node = bootstrap(&amp;boot_kmem_cache_node);

    /* Now we can use the kmem_cache to allocate kmalloc slabs */
    setup_kmalloc_cache_index_table();
    create_kmalloc_caches(0);

    /* Setup random freelists for each cache */
    init_freelist_randomization();

    cpuhp_setup_state_nocalls(CPUHP_SLUB_DEAD, "slub:dead", NULL, slub_cpu_dead);

    pr_info("SLUB: HWalign=%d, Order=%d-%d, MinObjects=%d, CPUs=%u, Nodes=%dn",
        cache_line_size(),
        slub_min_order, slub_max_order, slub_min_objects,
        nr_cpu_ids, nr_node_ids);
}
```

### `create_boot_cache()`源码分析

`create_boot_cache()`用于创建分配算法缓存，主要是用于初始化`boot_kmem_cache_node`结构：(`create_boot_cache()`在`/source/mm/slab_common.c#L881`处实现)

```
/* Create a cache during boot when no slab services are available yet */
void __init create_boot_cache(struct kmem_cache *s, const char *name, size_t size,
        slab_flags_t flags)
{
    int err;

    s-&gt;name = name;
    s-&gt;size = s-&gt;object_size = size;
    // calculate_alignment() 用于计算内存对齐值
    s-&gt;align = calculate_alignment(flags, ARCH_KMALLOC_MINALIGN, size);
    // 初始化 kmem_cache 结构的 memcg 参数
    slab_init_memcg_params(s);
    // 创建 slab 核心函数
    err = __kmem_cache_create(s, flags);

    if (err)
        panic("Creation of kmalloc slab %s size=%zu failed. Reason %dn",
                    name, size, err);

    // 暂时不合并 kmem_cache
    s-&gt;refcount = -1;    /* Exempt from merging for now */
}
```

### `bootstrap()`源码分析

`bootstrap()`用于将临时`kmem_cache`向最终`kmem_cache`迁移，并修正相关指针，使其指向最终的`kmem_cache`：(`bootstrap()`在`/source/mm/slub.c#L4141`处实现)

```
/********************************************************************
 *            Basic setup of slabs
 *******************************************************************/

/*
 * Used for early kmem_cache structures that were allocated using
 * the page allocator. Allocate them properly then fix up the pointers
 * that may be pointing to the wrong kmem_cache structure.
 */

static struct kmem_cache * __init bootstrap(struct kmem_cache *static_cache)
{
    int node;
    // 通过 kmem_cache_zalloc() 申请 kmem_cache 空间
    // 注意，存在以下函数调用链 kmem_cache_zalloc()-&gt;kmem_cache_alloc()-&gt;slab_alloc()
    // 其最终将会通过 create_boot_cache() 初始化创建的 kmem_cache 来申请 slub 空间来使用
    struct kmem_cache *s = kmem_cache_zalloc(kmem_cache, GFP_NOWAIT);
    struct kmem_cache_node *n;

    // 将作为参数的的 kmem_cache 结构数据通过 memcpy() 拷贝至申请的空间中
    memcpy(s, static_cache, kmem_cache-&gt;object_size);

    /*
     * This runs very early, and only the boot processor is supposed to be
     * up.  Even if it weren't true, IRQs are not up so we couldn't fire
     * IPIs around.
     */
    // 调用 __flush_cpu_slab() 刷新 cpu 的 slab 信息
    __flush_cpu_slab(s, smp_processor_id());
    // 遍历各个内存管理节点node
    for_each_kmem_cache_node(s, node, n) {
        struct page *p;

        // 遍历 partial slab ，修正每个 slab 指向 kmem_cache 的指针
        list_for_each_entry(p, &amp;n-&gt;partial, lru)
            p-&gt;slab_cache = s;

// 若开启CONFIG_SLUB_DEBUG
#ifdef CONFIG_SLUB_DEBUG
        // 遍历 full slab ，修正每个 slab 指向 kmem_cache 的指针
        list_for_each_entry(p, &amp;n-&gt;full, lru)
            p-&gt;slab_cache = s;
#endif
    }
    slab_init_memcg_params(s);
    // 将 kmem_cache 添加到全局 slab_caches 链表中
    list_add(&amp;s-&gt;list, &amp;slab_caches);
    memcg_link_cache(s);
    return s;
}
```

### `create_kmalloc_caches()`源码分析

`create_kmalloc_caches()`用于创建`kmalloc`数组：(`create_kmalloc_caches()`在`/source/mm/slab_common.c#L1071`处实现)

```
/*
 * Create the kmalloc array. Some of the regular kmalloc arrays
 * may already have been created because they were needed to
 * enable allocations for slab creation.
 */
/*
 * 创建 kmalloc 数组。
 * 某些常规 kmalloc 数组可能已经创建，因为需要它们才能启用分配以创建 slab 。
 */
void __init create_kmalloc_caches(slab_flags_t flags)
{
    int i;

    // 检查下标合法性
    for (i = KMALLOC_SHIFT_LOW; i &lt;= KMALLOC_SHIFT_HIGH; i++) {
        // 若对应的 kmalloc_caches 不存在
        if (!kmalloc_caches[i])
            // 调用 new_kmalloc_cache 分配 kmalloc_caches。
            new_kmalloc_cache(i, flags);

        /*
         * Caches that are not of the two-to-the-power-of size.
         * These have to be created immediately after the
         * earlier power of two caches
         */
        if (KMALLOC_MIN_SIZE &lt;= 32 &amp;&amp; !kmalloc_caches[1] &amp;&amp; i == 6)
            new_kmalloc_cache(1, flags);
        if (KMALLOC_MIN_SIZE &lt;= 64 &amp;&amp; !kmalloc_caches[2] &amp;&amp; i == 7)
            new_kmalloc_cache(2, flags);
    }

    /* Kmalloc array is now usable */
    // 设置标志位，表示 slab 分配器已经可以使用了。
    slab_state = UP;

// 若开启CONFIG_ZONE_DMA
#ifdef CONFIG_ZONE_DMA
    for (i = 0; i &lt;= KMALLOC_SHIFT_HIGH; i++) {
        struct kmem_cache *s = kmalloc_caches[i];

        if (s) {
            int size = kmalloc_size(i);
            char *n = kasprintf(GFP_NOWAIT, "dma-kmalloc-%d", size);

            BUG_ON(!n);
            // 调用 create_kmalloc_cache 分配 kmalloc_dma_caches。
            kmalloc_dma_caches[i] = create_kmalloc_cache(n, size, SLAB_CACHE_DMA | flags);
        }
    }
#endif
}
```

### `new_kmalloc_cache()`源码分析

`new_kmalloc_cache()`用于转化传入的`index`：(`new_kmalloc_cache()`在`/source/mm/slab_common.c#L1060`处实现)

```
static void __init new_kmalloc_cache(int idx, slab_flags_t flags)
{
    // 将传入的 idx 最终转化为 name 和 size ，调用 create_kmalloc_cache 来分配 kmalloc_cache
    kmalloc_caches[idx] = create_kmalloc_cache(kmalloc_info[idx].name,
                    kmalloc_info[idx].size, flags);
}
```

```
/*
 * kmalloc_info[] is to make slub_debug=,kmalloc-xx option work at boot time.
 * kmalloc_index() supports up to 2^26=64MB, so the final entry of the table is
 * kmalloc-67108864.
 */
// kmem_cache的名称以及大小使用struct kmalloc_info_struct管理。
// 所有管理不同大小对象的kmem_cache的名称如下： 
const struct kmalloc_info_struct kmalloc_info[] __initconst = {
    {NULL,                      0},        {"kmalloc-96",             96},
    {"kmalloc-192",           192},        {"kmalloc-8",               8},
    {"kmalloc-16",             16},        {"kmalloc-32",             32},
    {"kmalloc-64",             64},        {"kmalloc-128",           128},
    {"kmalloc-256",           256},        {"kmalloc-512",           512},
    {"kmalloc-1024",         1024},        {"kmalloc-2048",         2048},
    {"kmalloc-4096",         4096},        {"kmalloc-8192",         8192},
    {"kmalloc-16384",       16384},        {"kmalloc-32768",       32768},
    {"kmalloc-65536",       65536},        {"kmalloc-131072",     131072},
    {"kmalloc-262144",     262144},        {"kmalloc-524288",     524288},
    {"kmalloc-1048576",   1048576},        {"kmalloc-2097152",   2097152},
    {"kmalloc-4194304",   4194304},        {"kmalloc-8388608",   8388608},
    {"kmalloc-16777216", 16777216},        {"kmalloc-33554432", 33554432},
    {"kmalloc-67108864", 67108864}
};
```

### `create_kmalloc_cache()`源码分析

`create_kmalloc_cache()`用于创建`kmem_cache`对象：(`create_kmalloc_cache()`在`/source/mm/slab_common.c#L901`处实现)

```
struct kmem_cache *__init create_kmalloc_cache(const char *name, size_t size,
                slab_flags_t flags)
{
    // 经kmem_cache_zalloc()申请一个kmem_cache对象
    struct kmem_cache *s = kmem_cache_zalloc(kmem_cache, GFP_NOWAIT);

    if (!s)
        panic("Out of memory when creating slab %sn", name);

    // 使用create_boot_cache()创建slab
    create_boot_cache(s, name, size, flags);
    // 将其添加到slab_caches列表中
    list_add(&amp;s-&gt;list, &amp;slab_caches);
    memcg_link_cache(s);
    s-&gt;refcount = 1;
    return s;
}
```



## 0x04 slab的创建

### `__kmem_cache_create()`源码分析

`__kmem_cache_create()`用于创建`kmem_cache`对象：(`create_kmalloc_cache()`在`/source/mm/slub.c#L4257`处实现)

```
int __kmem_cache_create(struct kmem_cache *s, slab_flags_t flags)
{
    int err;

    // 调用 kmem_cache_open() 初始化 slub 结构
    err = kmem_cache_open(s, flags);
    if (err)
        return err;

    /* Mutex is not taken during early boot */
    if (slab_state &lt;= UP)
        return 0;

    memcg_propagate_slab_attrs(s);
    // 将 kmem_cache 添加到 sysfs
    err = sysfs_slab_add(s);
    if (err)
        // 如果出错，通过 __kmem_cache_releas 将 slub 销毁。
        __kmem_cache_release(s);

    return err;
}
```

### `kmem_cache_open()`源码分析

`kmem_cache_open()`用于初始化`slub`结构：(`kmem_cache_open()`在`/source/mm/slub.c#L3575`处实现)

```
static int kmem_cache_open(struct kmem_cache *s, slab_flags_t flags)
{
    // 获取设置缓存描述的标识，用于区分 slub 是否开启了调试
    s-&gt;flags = kmem_cache_flags(s-&gt;size, flags, s-&gt;name, s-&gt;ctor);
    s-&gt;reserved = 0;

// 如果设置了 CONFIG_SLAB_FREELIST_HARDENED 保护，获取一个随机数。
#ifdef CONFIG_SLAB_FREELIST_HARDENED
    s-&gt;random = get_random_long();
#endif

    if (need_reserve_slab_rcu &amp;&amp; (s-&gt;flags &amp; SLAB_TYPESAFE_BY_RCU))
        s-&gt;reserved = sizeof(struct rcu_head);

    /* 
     * 调用 calculate_sizes() 计算并初始化 kmem_cache 结构的各项数据
     * 这个函数将 kmem_cache -&gt; offset 成员计算出来
     * 这个成员之后会是一个指针，该指针指向何处存放下一个空闲对象
     * 此对象一般紧接着就是这个指针，但在需要对齐的情况下，会往后移一些
     * 该函数同时还计算出 kmem_cache -&gt; size 成员
     * 该成员表明一个对象实际在内存里面需要的长度，这个长度包括了对象本身的长度
     * 其后指向下一个空闲对象的指针长度
     * 开启了SLUB Debug 的情况下，要加入一个空区域用于越界监管的长度，对齐所需长度等
     * 然后，该函数再根据该 kmem_cache 的单个 SLAB 所包含的物理页面的数目
     * (这个数目被放在了 kmem_cache-&gt;order 成员里，也是根据 kmem_cache -&gt; size 算出来的)
     * 及单个对象的实际长度 kmem_cache -&gt; size ，计算出来单个 SLAB 所能容纳的对象的个数
     * 并将其放在了 kmem_cache -&gt;objects 成员里。
     */
    if (!calculate_sizes(s, -1))
        goto error;
    if (disable_higher_order_debug) {
        /*
         * 如果最小slub顺序增加，则禁用存储元数据的调试标志。
         */
        if (get_order(s-&gt;size) &gt; get_order(s-&gt;object_size)) {
            s-&gt;flags &amp;= ~DEBUG_METADATA_FLAGS; // 禁用存储元数据的调试标志
            s-&gt;offset = 0;
            if (!calculate_sizes(s, -1))
                goto error;
        }
    }

#if defined(CONFIG_HAVE_CMPXCHG_DOUBLE) &amp;&amp; defined(CONFIG_HAVE_ALIGNED_STRUCT_PAGE)
    if (system_has_cmpxchg_double() &amp;&amp; (s-&gt;flags &amp; SLAB_NO_CMPXCHG) == 0)
        /* Enable fast mode */
        s-&gt;flags |= __CMPXCHG_DOUBLE;
#endif

    /*
     * The larger the object size is, the more pages we want on the partial
     * list to avoid pounding the page allocator excessively.
     */
    // 调用 set_min_partial() 来设置partial链表的最小值
    // 由于对象的大小越大，则需挂入的partial链表的页面则越多，设置最小值是为了避免过度使用页面分配器造成冲击
    set_min_partial(s, ilog2(s-&gt;size) / 2);

    // 调用 set_cpu_partial() 根据对象的大小以及配置的情况，对 cpu_partial 进行设置
    // cpu_partial 表示的是每个 CPU 在 partial 链表中的最多对象个数，该数据决定了：
    // 1）当使用到了极限时，每个 CPU 的 partial slab 释放到每个管理节点链表的个数；
    // 2）当使用完每个 CPU 的对象数时， CPU 的 partial slab 来自每个管理节点的对象数。
    set_cpu_partial(s);

#ifdef CONFIG_NUMA
    s-&gt;remote_node_defrag_ratio = 1000;
#endif

    /* Initialize the pre-computed randomized freelist if slab is up */
    if (slab_state &gt;= UP) {
        if (init_cache_random_seq(s))
            goto error;
    }

    /* 初始化 kmem_cache-&gt;local_node 成员，比如给 nr_partial 赋 0 ，表示没有 Partial SLAB 在其上 */
    if (!init_kmem_cache_nodes(s))
        goto error;

    /* 初始化 kmem_cache-&gt;kmem_cache_cpu 成员，比如给其赋 NULL ，表示没有当前 SLAB */
    if (alloc_kmem_cache_cpus(s))
        return 0;

    // 若初始化 kmem_cache-&gt;kmem_cache_cpu 成员失败，释放这个节点。
    free_kmem_cache_nodes(s);
error:
    if (flags &amp; SLAB_PANIC)
        panic("Cannot create slab %s size=%lu realsize=%u order=%u offset=%u flags=%lxn",
              s-&gt;name, (unsigned long)s-&gt;size, s-&gt;size,
              oo_order(s-&gt;oo), s-&gt;offset, (unsigned long)flags);
    return -EINVAL;
}
```

### `calculate_sizes()`源码分析

`calculate_sizes()`用于计算并初始化`kmem_cache`结构的各项数据：(`calculate_sizes()`在`/source/mm/slub.c#L3457`处实现)

```
/*
 * calculate_sizes() determines the order and the distribution of data within
 * a slab object.
 */
static int calculate_sizes(struct kmem_cache *s, int forced_order)
{
    slab_flags_t flags = s-&gt;flags;
    size_t size = s-&gt;object_size;
    int order;

    /*
     * Round up object size to the next word boundary. We can only
     * place the free pointer at word boundaries and this determines
     * the possible location of the free pointer.
     */
    // 将 slab 对象的大小舍入对与 sizeof(void *) 指针大小对齐，其为了能够将空闲指针存放至对象的边界中
    size = ALIGN(size, sizeof(void *));

// 若 CONFIG_SLUB_DEBUG 选项被开启
#ifdef CONFIG_SLUB_DEBUG
    /*
     * Determine if we can poison the object itself. If the user of
     * the slab may touch the object after free or before allocation
     * then we should never poison the object itself.
     */
    // 判断用户是否会在对象释放后或者申请前访问对象
    // 设定SLUB的调试功能是否被启用，也就是决定了对poison对象是否进行修改操作
    // 其主要是为了通过将对象填充入特定的字符数据以实现对内存写越界进行检测
    if ((flags &amp; SLAB_POISON) &amp;&amp; !(flags &amp; SLAB_TYPESAFE_BY_RCU) &amp;&amp; !s-&gt;ctor)
        s-&gt;flags |= __OBJECT_POISON;
    else
        s-&gt;flags &amp;= ~__OBJECT_POISON;


    /*
     * If we are Redzoning then check if there is some space between the
     * end of the object and the free pointer. If not then add an
     * additional word to have some bytes to store Redzone information.
     */
    // 在对象前后设置RedZone信息，通过检查该信息以捕捉Buffer溢出的问题
    if ((flags &amp; SLAB_RED_ZONE) &amp;&amp; size == s-&gt;object_size)
        size += sizeof(void *);
#endif

    /*
     * With that we have determined the number of bytes in actual use
     * by the object. This is the potential offset to the free pointer.
     */
    // 设置 kmem_cache 的 inuse 成员以表示元数据的偏移量
    // 这也同时表示对象实际使用的大小，也意味着对象与空闲对象指针之间的可能偏移量
    s-&gt;inuse = size;

    // 判断是否允许对象写越界，如果不允许则重定位空闲对象指针到对象的末尾。
    if (((flags &amp; (SLAB_TYPESAFE_BY_RCU | SLAB_POISON)) || s-&gt;ctor)) {
        /*
         * Relocate free pointer after the object if it is not
         * permitted to overwrite the first word of the object on
         * kmem_cache_free.
         *
         * This is the case if we do RCU, have a constructor or
         * destructor or are poisoning the objects.
         */
        // 设置 kmem_cache 结构的 offset（即对象指针的偏移）
        s-&gt;offset = size;
        // 调整size为包含空闲对象指针
        size += sizeof(void *);
    }

// 若已开启 CONFIG_SLUB_DEBUG 配置
#ifdef CONFIG_SLUB_DEBUG
    // 若已设置 SLAB_STORE_USER 标识
    if (flags &amp; SLAB_STORE_USER)
        /*
         * Need to store information about allocs and frees after
         * the object.
         */
        // 在对象末尾加上两个track的空间大小，用于记录该对象的使用轨迹信息（分别是申请和释放的信息）
        size += 2 * sizeof(struct track);
#endif

    kasan_cache_create(s, &amp;size, &amp;s-&gt;flags);

#ifdef CONFIG_SLUB_DEBUG
    // 若已设置 SLAB_RED_ZONE
    if (flags &amp; SLAB_RED_ZONE) {
        /*
         * Add some empty padding so that we can catch
         * overwrites from earlier objects rather than let
         * tracking information or the free pointer be
         * corrupted if a user writes before the start
         * of the object.
         */
        // 新增空白边界,主要是用于捕捉内存写越界信息
        // 目的是与其任由其越界破坏了空闲对象指针或者内存申请释放轨迹信息，倒不如捕获内存写越界信息。
        size += sizeof(void *);

        s-&gt;red_left_pad = sizeof(void *);
        s-&gt;red_left_pad = ALIGN(s-&gt;red_left_pad, s-&gt;align);
        size += s-&gt;red_left_pad;
    }
#endif

    /*
     * SLUB stores one object immediately after another beginning from
     * offset 0. In order to align the objects we have to simply size
     * each object to conform to the alignment.
     */
    // 根据前面统计的size做对齐操作
    size = ALIGN(size, s-&gt;align);
    // 更新到kmem_cache结构中
    s-&gt;size = size;
    if (forced_order &gt;= 0)
        order = forced_order;
    else
        // 通过 calculate_order() 计算单 slab 的页框阶数
        order = calculate_order(size, s-&gt;reserved);

    if (order &lt; 0)
        return 0;

    s-&gt;allocflags = 0;
    if (order)
        s-&gt;allocflags |= __GFP_COMP;

    if (s-&gt;flags &amp; SLAB_CACHE_DMA)
        s-&gt;allocflags |= GFP_DMA;

    if (s-&gt;flags &amp; SLAB_RECLAIM_ACCOUNT)
        s-&gt;allocflags |= __GFP_RECLAIMABLE;

    /*
     * Determine the number of objects per slab
     */
    // 调用 oo_make 计算 kmem_cache 结构的 oo、min、max 等相关信息
    s-&gt;oo = oo_make(order, size, s-&gt;reserved);
    s-&gt;min = oo_make(get_order(size), size, s-&gt;reserved);
    if (oo_objects(s-&gt;oo) &gt; oo_objects(s-&gt;max))
        s-&gt;max = s-&gt;oo;

    return !!oo_objects(s-&gt;oo);
}
```

### `calculate_order()`源码分析

`calculate_order()`用于计算单`slab`的页框阶数：(`calculate_order()`在`/source/mm/slub.c#L3237`处实现)

```
static inline int calculate_order(int size, int reserved)
{
    int order;
    int min_objects;
    int fraction;
    int max_objects;

    /*
     * Attempt to find best configuration for a slab. This
     * works by first attempting to generate a layout with
     * the best configuration and backing off gradually.
     *
     * First we increase the acceptable waste in a slab. Then
     * we reduce the minimum objects required in a slab.
     */
    // 判断来自系统参数的最少对象数 slub_min_objects 是否已经配置
    min_objects = slub_min_objects;
    if (!min_objects)
        // 通过处理器数 nr_cpu_ids 计算最小对象数
        min_objects = 4 * (fls(nr_cpu_ids) + 1);
    // 通过 order_objects() 计算最高阶下，slab 对象最多个数
    max_objects = order_objects(slub_max_order, size, reserved);
    // 取得最小值min_objects
    min_objects = min(min_objects, max_objects);

    // 调整 min_objects 及 fraction
    while (min_objects &gt; 1) {
        fraction = 16;
        while (fraction &gt;= 4) {
            // 通过 slab_order() 计算找出最佳的阶数
            // 其中fraction用来表示slab内存未使用率的指标，值越大表示允许的未使用内存越少
            // 不断调整单个slab的对象数以及降低碎片指标，由此找到一个最佳值
            order = slab_order(size, min_objects, slub_max_order, fraction, reserved);
            if (order &lt;= slub_max_order)
                return order;
            fraction /= 2;
        }
        min_objects--;
    }

    /*
     * We were unable to place multiple objects in a slab. Now
     * lets see if we can place a single object there.
     */
    // 如果对象个数及内存未使用率指标都调整到最低了仍得不到最佳阶值时，将尝试一个slab仅放入单个对象
    order = slab_order(size, 1, slub_max_order, 1, reserved);
    // 由此计算出的order不大于slub_max_order，则将该值返回
    if (order &lt;= slub_max_order)
        return order;

    /*
     * Doh this slab cannot be placed using slub_max_order.
     */
    // 否则，将不得不尝试将阶数值调整至最大值MAX_ORDER，以期得到结果
    order = slab_order(size, 1, MAX_ORDER, 1, reserved);
    if (order &lt; MAX_ORDER)
        return order;
    // 如果仍未得结果，那么将返回失败
    return -ENOSYS;
}
```

### `slab_order()`源码分析

`slab_order()`用于找出最佳的阶数：(`slab_order()`在`/source/mm/slub.c#L3213`处实现)

```
/*
 * Calculate the order of allocation given an slab object size.
 *
 * The order of allocation has significant impact on performance and other
 * system components. Generally order 0 allocations should be preferred since
 * order 0 does not cause fragmentation in the page allocator. Larger objects
 * be problematic to put into order 0 slabs because there may be too much
 * unused space left. We go to a higher order if more than 1/16th of the slab
 * would be wasted.
 *
 * In order to reach satisfactory performance we must ensure that a minimum
 * number of objects is in one slab. Otherwise we may generate too much
 * activity on the partial lists which requires taking the list_lock. This is
 * less a concern for large slabs though which are rarely used.
 *
 * slub_max_order specifies the order where we begin to stop considering the
 * number of objects in a slab as critical. If we reach slub_max_order then
 * we try to keep the page order as low as possible. So we accept more waste
 * of space in favor of a small page order.
 *
 * Higher order allocations also allow the placement of more objects in a
 * slab and thereby reduce object handling overhead. If the user has
 * requested a higher mininum order then we start with that one instead of
 * the smallest order which will fit the object.
 */
// 该函数的参数中：
// size表示对象大小
// min_objects为最小对象量
// max_order为最高阶
// fract_leftover表示slab的内存未使用率
// reserved则表示slab的保留空间大小
// 内存页面存储对象个数使用的objects是u15的长度，故其最多可存储个数为MAX_OBJS_PER_PAGE，即32767。
static inline int slab_order(int size, int min_objects,
                int max_order, int fract_leftover, int reserved)
{
    int order;
    int rem;
    int min_order = slub_min_order;

    // 如果 order_objects() 以 min_order 换算内存大小剔除 reserved 后，通过 size 求得的对象
    // 个数大于MAX_OBJS_PER_PAGE，则改为MAX_OBJS_PER_PAGE进行求阶
    if (order_objects(min_order, size, reserved) &gt; MAX_OBJS_PER_PAGE)
        return get_order(size * MAX_OBJS_PER_PAGE) - 1;

    // 调整阶数以期找到一个能够容纳该大小最少对象数量及其保留空间的并且内存的使用率满足条件的阶数
    for (order = max(min_order, get_order(min_objects * size + reserved));
            order &lt;= max_order; order++) {

        unsigned long slab_size = PAGE_SIZE &lt;&lt; order;

        rem = (slab_size - reserved) % size;

        if (rem &lt;= slab_size / fract_leftover)
            break;
    }

    return order;
}
```

### `init_kmem_cache_nodes()`源码分析

`init_kmem_cache_nodes()`用于分配并初始化节点对象：(`init_kmem_cache_nodes()`在`/source/mm/slub.c#L3386`处实现)

```
static int init_kmem_cache_nodes(struct kmem_cache *s)
{
    int node;

    // 遍历每个管理节点
    for_each_node_state(node, N_NORMAL_MEMORY) {
        struct kmem_cache_node *n;

        // slab_state如果是DOWN状态，表示slub分配器还没有初始化完毕
        // 意味着kmem_cache_node结构空间对象的cache还没建立，暂时无法进行对象分配
        if (slab_state == DOWN) {
            // 申请一个node结构空间对象
            early_kmem_cache_node_alloc(node);
            continue;
        }
        // 申请一个 kmem_cache_node 结构空间对象
        n = kmem_cache_alloc_node(kmem_cache_node, GFP_KERNEL, node);

        // 若申请失败，销毁整个 kmem_cache 结构体
        if (!n) {
            free_kmem_cache_nodes(s);
            return 0;
        }

        // 初始化一个kmem_cache_node结构空间对象
        init_kmem_cache_node(n);
        // 链入 kmem_cache 结构体
        s-&gt;node[node] = n;
    }
    return 1;
}
```

### `early_kmem_cache_node_alloc()`源码分析

`early_kmem_cache_node_alloc()`用于分配并初始化节点对象：(`early_kmem_cache_node_alloc()`在`/source/mm/slub.c#L3331`处实现)

```
/*
 * No kmalloc_node yet so do it by hand. We know that this is the first
 * slab on the node for this slabcache. There are no concurrent accesses
 * possible.
 *
 * Note that this function only works on the kmem_cache_node
 * when allocating for the kmem_cache_node. This is used for bootstrapping
 * memory on a fresh node that has no slab structures yet.
 */
static void early_kmem_cache_node_alloc(int node)
{
    struct page *page;
    struct kmem_cache_node *n;

    BUG_ON(kmem_cache_node-&gt;size &lt; sizeof(struct kmem_cache_node));

    // 通过new_slab()创建kmem_cache_node结构空间对象的slab
    page = new_slab(kmem_cache_node, GFP_NOWAIT, node);

    BUG_ON(!page);
    // 如果创建的slab不在对应的内存节点中，则通过printk输出调试信息
    if (page_to_nid(page) != node) {
        pr_err("SLUB: Unable to allocate memory from node %dn", node);
        pr_err("SLUB: Allocating a useless per node structure in order to be able to continuen");
    }

    // 初始化 page 的相关成员
    n = page-&gt;freelist;
    BUG_ON(!n);
    page-&gt;freelist = get_freepointer(kmem_cache_node, n);
    page-&gt;inuse = 1;
    page-&gt;frozen = 0;
    kmem_cache_node-&gt;node[node] = n;
#ifdef CONFIG_SLUB_DEBUG
    // 调用 init_object() 标识数据区和 RedZone
    init_object(kmem_cache_node, n, SLUB_RED_ACTIVE);
    // 调用 init_tracking() 记录轨迹信息
    init_tracking(kmem_cache_node, n);
#endif
    kasan_kmalloc(kmem_cache_node, n, sizeof(struct kmem_cache_node),GFP_KERNEL);
    // 初始化取出的对象
    init_kmem_cache_node(n);
    // 调用 inc_slabs_node() 更新统计信息
    inc_slabs_node(kmem_cache_node, node, page-&gt;objects);

    /*
     * No locks need to be taken here as it has just been
     * initialized and there is no concurrent access.
     */
    // 将 slab 添加到 partial 链表中
    __add_partial(n, page, DEACTIVATE_TO_HEAD);
}
```

### `new_slab()`源码分析

`new_slab()`用于创建`slab`：(`new_slab()`在`/source/mm/slub.c#L1643`处实现)

```
static struct page *new_slab(struct kmem_cache *s, gfp_t flags, int node)
{
    if (unlikely(flags &amp; GFP_SLAB_BUG_MASK)) {
        gfp_t invalid_mask = flags &amp; GFP_SLAB_BUG_MASK;
        flags &amp;= ~GFP_SLAB_BUG_MASK;
        pr_warn("Unexpected gfp: %#x (%pGg). Fixing up to gfp: %#x (%pGg). Fix your code!n",
                invalid_mask, &amp;invalid_mask, flags, &amp;flags);
        dump_stack();
    }
    return allocate_slab(s, flags &amp; (GFP_RECLAIM_MASK | GFP_CONSTRAINT_MASK), node);
}
```

可以发现这个函数的核心就是去调用`allocate_slab`函数实现的。

### `allocate_slab()`源码分析

`allocate_slab()`用于创建`slab`：(`allocate_slab()`在`/source/mm/slub.c#L1558`处实现）

```
static struct page *allocate_slab(struct kmem_cache *s, gfp_t flags, int node)
{
    struct page *page;
    struct kmem_cache_order_objects oo = s-&gt;oo;
    gfp_t alloc_gfp;
    void *start, *p;
    int idx, order;
    bool shuffle;

    flags &amp;= gfp_allowed_mask;

    // 如果申请 slab 所需页面设置 __GFP_WAIT 标志，表示运行等待
    if (gfpflags_allow_blocking(flags))
        // 启用中断
        local_irq_enable();

    flags |= s-&gt;allocflags;

    /*
     * Let the initial higher-order allocation fail under memory pressure
     * so we fall-back to the minimum order allocation.
     */
    alloc_gfp = (flags | __GFP_NOWARN | __GFP_NORETRY) &amp; ~__GFP_NOFAIL;
    if ((alloc_gfp &amp; __GFP_DIRECT_RECLAIM) &amp;&amp; oo_order(oo) &gt; oo_order(s-&gt;min))
        alloc_gfp = (alloc_gfp | __GFP_NOMEMALLOC) &amp; ~(__GFP_RECLAIM|__GFP_NOFAIL);

    // 尝试使用 alloc_slab_page() 进行内存页面申请
    page = alloc_slab_page(s, alloc_gfp, node, oo);
    if (unlikely(!page)) {
        // 如果申请失败，则将其调至s-&gt;min进行降阶再次尝试申请
        oo = s-&gt;min;
        alloc_gfp = flags;
        /*
         * Allocation may have failed due to fragmentation.
         * Try a lower order alloc if possible
         */
        page = alloc_slab_page(s, alloc_gfp, node, oo);
        if (unlikely(!page))
            // 再次失败则执行退出流程
            goto out;
        stat(s, ORDER_FALLBACK);
    }

    // 设置 page 的 object 成员为从 oo 获取到的 object。
    page-&gt;objects = oo_objects(oo);
    // 通过 compound_order() 从该 slab 的首个 page 结构中获取其占用页面的 order 信息
    order = compound_order(page);
    // 设置 page 的 slab_cache 成员为它所属的 slab_cache
    page-&gt;slab_cache = s;
    // 将 page 链入 slab 中
    __SetPageSlab(page);
    // 判断 page 的 index 是否为 -1
    if (page_is_pfmemalloc(page))
        // 激活这个内存页
        SetPageSlabPfmemalloc(page);

    // page_address() 获取页面的虚拟地址
    start = page_address(page);

    // 根据 SLAB_POISON 标识以确定是否 memset() 该 slab 的空间
    if (unlikely(s-&gt;flags &amp; SLAB_POISON))
        memset(start, POISON_INUSE, PAGE_SIZE &lt;&lt; order);

    kasan_poison_slab(page);

    shuffle = shuffle_freelist(s, page);

    if (!shuffle) {
        //遍历每一个对象
        for_each_object_idx(p, idx, s, start, page-&gt;objects) {
            // 通过 setup_object() 初始化对象信息
            setup_object(s, page, p);
            // 通过 set_freepointer() 设置空闲页面指针，最终将 slab 初始完毕。
            if (likely(idx &lt; page-&gt;objects))
                set_freepointer(s, p, p + s-&gt;size);
            else
                set_freepointer(s, p, NULL);
        }
        page-&gt;freelist = fixup_red_left(s, start);
    }

    page-&gt;inuse = page-&gt;objects;
    page-&gt;frozen = 1;

out:
    // 禁用中断
    if (gfpflags_allow_blocking(flags))
        local_irq_disable();
    // 分配内存失败，返回NULL
    if (!page)
        return NULL;

    // 通过 mod_zone_page_state 计算更新内存管理区的状态统计
    mod_lruvec_page_state(page,
        (s-&gt;flags &amp; SLAB_RECLAIM_ACCOUNT) ? NR_SLAB_RECLAIMABLE : NR_SLAB_UNRECLAIMABLE,
        1 &lt;&lt; oo_order(oo));

    inc_slabs_node(s, page_to_nid(page), page-&gt;objects);

    return page;
}
```

### `alloc_kmem_cache_cpus()`源码分析

`alloc_kmem_cache_cpus()`用于进一步的初始化工作：(`alloc_kmem_cache_cpus()`在`/source/mm/slub.c#L3300`处实现）

```
static inline int alloc_kmem_cache_cpus(struct kmem_cache *s)
{
    BUILD_BUG_ON(PERCPU_DYNAMIC_EARLY_SIZE &lt; 
                 KMALLOC_SHIFT_HIGH * sizeof(struct kmem_cache_cpu));

    /*
     * Must align to double word boundary for the double cmpxchg
     * instructions to work; see __pcpu_double_call_return_bool().
     */
    s-&gt;cpu_slab = __alloc_percpu(sizeof(struct kmem_cache_cpu), 2 * sizeof(void *));

    if (!s-&gt;cpu_slab)
        return 0;

    init_kmem_cache_cpus(s);

    return 1;
}
```

### `kmem_cache_alloc_node()`源码分析

`kmem_cache_alloc_node()`用于在`slub`分配器已全部或部分初始化完毕后分配`node`结构：(`kmem_cache_alloc_node()`在`/source/mm/slub.c#L2759`处实现）

```
void *kmem_cache_alloc_node(struct kmem_cache *s, gfp_t gfpflags, int node)
{
    void *ret = slab_alloc_node(s, gfpflags, node, _RET_IP_);

    trace_kmem_cache_alloc_node(_RET_IP_, ret, s-&gt;object_size, s-&gt;size, gfpflags, node);

    return ret;
}
```

### `slab_alloc_node()`源码分析

`slab_alloc_node()`用于对象的取出：(`slab_alloc_node()`在`/source/mm/slub.c#L2643`处实现）

```
/*
 * Inlined fastpath so that allocation functions (kmalloc, kmem_cache_alloc)
 * have the fastpath folded into their functions. So no function call
 * overhead for requests that can be satisfied on the fastpath.
 *
 * The fastpath works by first checking if the lockless freelist can be used.
 * If not then __slab_alloc is called for slow processing.
 *
 * Otherwise we can simply pick the next object from the lockless free list.
 */
static __always_inline void *slab_alloc_node(struct kmem_cache *s,
        gfp_t gfpflags, int node, unsigned long addr)
{
    void *object;
    struct kmem_cache_cpu *c;
    struct page *page;
    unsigned long tid;

    // 主要负责对 slub 对象分配的预处理，返回用于分配 slub 对象的 kmem_cache
    s = slab_pre_alloc_hook(s, gfpflags);
    if (!s)
        return NULL;
redo:
    /*
     * Must read kmem_cache cpu data via this cpu ptr. Preemption is
     * enabled. We may switch back and forth between cpus while
     * reading from one cpu area. That does not matter as long
     * as we end up on the original cpu again when doing the cmpxchg.
     *
     * We should guarantee that tid and kmem_cache are retrieved on
     * the same cpu. It could be different if CONFIG_PREEMPT so we need
     * to check if it is matched or not.
     */
    // 检查 flag 标志位中时候启用了抢占功能
    do {
        // 取得 kmem_cache_cpu 的 tid 值
        tid = this_cpu_read(s-&gt;cpu_slab-&gt;tid);
        // 获取当前 CPU 的 kmem_cache_cpu 结构
        c = raw_cpu_ptr(s-&gt;cpu_slab);
    } while (IS_ENABLED(CONFIG_PREEMPT) &amp;&amp; unlikely(tid != READ_ONCE(c-&gt;tid)));

    /*
     * Irqless object alloc/free algorithm used here depends on sequence
     * of fetching cpu_slab's data. tid should be fetched before anything
     * on c to guarantee that object and page associated with previous tid
     * won't be used with current tid. If we fetch tid first, object and
     * page could be one associated with next tid and our alloc/free
     * request will be failed. In this case, we will retry. So, no problem.
     * 
     * barrier 是一种保证内存访问顺序的一种方法
     * 让系统中的 HW block (各个cpu、DMA controler、device等)对内存有一致性的视角。
     * barrier 就象是c代码中的一个栅栏，将代码逻辑分成两段
     * barrier 之前的代码和 barrier 之后的代码在经过编译器编译后顺序不能乱掉
     * 也就是说，barrier 之后的c代码对应的汇编，不能跑到 barrier 之前去，反之亦然
     */
    barrier();

    /*
     * The transaction ids are globally unique per cpu and per operation on
     * a per cpu queue. Thus they can be guarantee that the cmpxchg_double
     * occurs on the right processor and that there was no operation on the
     * linked list in between.
     */

    // 获得当前cpu的空闲对象列表
    object = c-&gt;freelist;
    // 获取当前cpu使用的页面
    page = c-&gt;page;
    // 当前 CPU 的 slub 空闲列表为空或者当前 slub 使用内存页面与管理节点不匹配时，需要重新分配 slub 对象。
    if (unlikely(!object || !node_match(page, node))) {
        // 分配slub对象
        object = __slab_alloc(s, gfpflags, node, addr, c);
        // 设置kmem_cache_cpu的状态位（相应位加1）
        // 此操作表示从当前cpu获得新的cpu slub来分配对象(慢路径分配)
        stat(s, ALLOC_SLOWPATH);
    } else {
        // 获取空闲对象地址(object + s-&gt;offset)
        void *next_object = get_freepointer_safe(s, object);

        /*
         * The cmpxchg will only match if there was no additional
         * operation and if we are on the right processor.
         *
         * The cmpxchg does the following atomically (without lock
         * semantics!)
         * 1. Relocate first pointer to the current per cpu area.
         * 2. Verify that tid and freelist have not been changed
         * 3. If they were not changed replace tid and freelist
         *
         * Since this is without lock semantics the protection is only
         * against code executing on this cpu *not* from access by
         * other cpus.
         */
        // 通过一个原子操作取出对象
        if (unlikely(!this_cpu_cmpxchg_double(
                s-&gt;cpu_slab-&gt;freelist, s-&gt;cpu_slab-&gt;tid,
                object, tid,
                next_object, next_tid(tid)))) {

            // 获取失败，回到redo，尝试重新分配
            note_cmpxchg_failure("slab_alloc", s, tid);
            goto redo;
        }
        // 若获取成功，则使用此函数更新数据
        prefetch_freepointer(s, next_object);
        // 设置 kmem_cache_cpu 的状态位,表示通过当前cpu的cpu slub分配对象(快路径分配)
        stat(s, ALLOC_FASTPATH);
    }

    // 初始化我们刚刚获取的对象
    if (unlikely(gfpflags &amp; __GFP_ZERO) &amp;&amp; object)
        memset(object, 0, s-&gt;object_size);

    // 进行分配后处理
    slab_post_alloc_hook(s, gfpflags, 1, &amp;object);

    return object;
}
```

### `__slab_alloc()`源码分析

`__slab_alloc()`用于分配一个新的slab并从中取出一个对象：(`__slab_alloc()`在`/source/mm/slub.c#L2612`处实现）

```
/*
 * Another one that disabled interrupt and compensates for possible
 * cpu changes by refetching the per cpu area pointer.
 */
static void *__slab_alloc(struct kmem_cache *s, gfp_t gfpflags, int node,
              unsigned long addr, struct kmem_cache_cpu *c)
{
    void *p;
    unsigned long flags;

    // 禁用系统中断
    local_irq_save(flags);
#ifdef CONFIG_PREEMPT
    /*
     * We may have been preempted and rescheduled on a different
     * cpu before disabling interrupts. Need to reload cpu area
     * pointer.
     * 由于在关中断之前，可能被抢占或者重新调度（迁移到其余cpu），因此需要重新获取每cpu变量
     */
    c = this_cpu_ptr(s-&gt;cpu_slab);
#endif

    // 核心函数
    p = ___slab_alloc(s, gfpflags, node, addr, c);
    // 恢复使用系统中断
    local_irq_restore(flags);
    return p;
}
```

### `___slab_alloc()`源码分析

`___slab_alloc()`是`__slab_alloc()`的核心方法：(`___slab_alloc()`在`/source/mm/slub.c#L2519`处实现）

```
/*
 * Slow path. The lockless freelist is empty or we need to perform
 * debugging duties.
 *
 * Processing is still very fast if new objects have been freed to the
 * regular freelist. In that case we simply take over the regular freelist
 * as the lockless freelist and zap the regular freelist.
 *
 * If that is not working then we fall back to the partial lists. We take the
 * first element of the freelist as the object to allocate now and move the
 * rest of the freelist to the lockless freelist.
 *
 * And if we were unable to get a new slab from the partial slab lists then
 * we need to allocate a new slab. This is the slowest path since it involves
 * a call to the page allocator and the setup of a new slab.
 *
 * Version of __slab_alloc to use when we know that interrupts are
 * already disabled (which is the case for bulk allocation).
 */
static void *___slab_alloc(struct kmem_cache *s, gfp_t gfpflags, int node,
              unsigned long addr, struct kmem_cache_cpu *c)
{
    void *freelist;
    struct page *page;

    page = c-&gt;page;
    // 如果没有本地活动 slab，转到 new_slab 步骤获取 slab
    if (!page)
        goto new_slab;
redo:
    if (unlikely(!node_match(page, node))) {
        // 如果本处理器所在节点与指定节点不一致
        int searchnode = node;

        if (node != NUMA_NO_NODE &amp;&amp; !node_present_pages(node))
            // 获取指定节点的node
            searchnode = node_to_mem_node(node);

        if (unlikely(!node_match(page, searchnode))) {
            // 如果node还是不匹配，则移除cpu slab，进入new_slab流程
            stat(s, ALLOC_NODE_MISMATCH);
            // 移除cpu slab(释放每cpu变量的所有freelist对象指针)
            deactivate_slab(s, page, c-&gt;freelist, c);
            goto new_slab;
        }
    }

    /*
     * By rights, we should be searching for a slab page that was
     * PFMEMALLOC but right now, we are losing the pfmemalloc
     * information when the page leaves the per-cpu allocator
     */
    // 判断当前页面属性是否为pfmemalloc，如果不是则同样移除cpu slab。
    if (unlikely(!pfmemalloc_match(page, gfpflags))) {
        deactivate_slab(s, page, c-&gt;freelist, c);
        goto new_slab;
    }

    /* must check again c-&gt;freelist in case of cpu migration or IRQ */
    // 再次检查空闲对象指针freelist是否为空
    // 避免在禁止本地处理器中断前因发生了CPU迁移或者中断，导致本地的空闲对象指针不为空；
    freelist = c-&gt;freelist;
    if (freelist)
        // 如果不为空的情况下，将会跳转至load_freelist
        goto load_freelist;

    // 如果为空，将会更新慢路径申请对象的统计信息
    // 并通过 get_freelist() 从非冻结页面（未在cpu缓存中）中获取空闲队列
    freelist = get_freelist(s, page);

    // 若获取空闲队列失败则需要创建新的 slab
    if (!freelist) {
        c-&gt;page = NULL;
        stat(s, DEACTIVATE_BYPASS);
        goto new_slab;
    }

    // 否则更新统计信息进入 load_freelist 分支取得对象并返回
    stat(s, ALLOC_REFILL);

load_freelist:
    /*
     * freelist is pointing to the list of objects to be used.
     * page is pointing to the page from which the objects are obtained.
     * That page must be frozen for per cpu allocations to work.
     * freelist 指向将要被使用的空闲列表
     * page 指向包含对象的页
     * page 应处于冻结状态，即在cpu缓存中
     */
    VM_BUG_ON(!c-&gt;page-&gt;frozen);
    // 获取空闲对象并返回空闲对象
    c-&gt;freelist = get_freepointer(s, freelist);
    c-&gt;tid = next_tid(c-&gt;tid);
    return freelist;

new_slab:

    // 首先会判断 partial 是否为空，不为空则从 partial 中取出 page ，然后跳转回 redo 重试分配
    if (slub_percpu_partial(c)) {
        page = c-&gt;page = slub_percpu_partial(c);
        slub_set_percpu_partial(c, page);
        stat(s, CPU_PARTIAL_ALLOC);
        goto redo;
    }

    //如果partial为空，意味着当前所有的slab都已经满负荷使用，那么则需使用new_slab_objects()创建新的slab
    freelist = new_slab_objects(s, gfpflags, node, &amp;c);

    if (unlikely(!freelist)) {
        // 如果创建失败，调用slab_out_of_memory()记录日志后返回NULL表示申请失败
        slab_out_of_memory(s, gfpflags, node);
        return NULL;
    }

    page = c-&gt;page;
    if (likely(!kmem_cache_debug(s) &amp;&amp; pfmemalloc_match(page, gfpflags)))
        goto load_freelist;

    /* Only entered in the debug case */
    if (kmem_cache_debug(s) &amp;&amp;
            !alloc_debug_processing(s, page, freelist, addr))
        goto new_slab;    /* Slab failed checks. Next slab needed */

    deactivate_slab(s, page, get_freepointer(s, freelist), c);
    return freelist;
}
```



## 0x05 整体分配流程总结

那么，我们可以总结出整个`slub`分配器的初始化以及创建流程：
<li>首先，内核调用`kmem_cache_init`，创建两个结构体`boot_kmem_cache`和`boot_kmem_cache_node`，这两个结构体将作为`kmem_cache`和`kmem_cache_node`的管理结构体。
<ol>
<li>然后，内核调用`create_boot_cache()`初始化`boot_kmem_cache_node`结构体的部分成员变量，被初始化的成员变量如下：`name`、`size`、`object_size`、`align`、`memcg`。
<ol>
<li>紧接着，内核继续调用`__kmem_cache_create`继续初始化`boot_kmem_cache_node`结构体，而进入`__kmem_cache_create`后又会直接进入`kmem_cache_open`，最终的初始化工作将会在`kmem_cache_open`中完成。
<ol>
1. 在`kmem_cache_open`中，内核首先初始化结构体的`flag`成员，注意，内核将在这一步来判断是否开启了内核调试模式，若开启，`flag`则为空值。
1. 接下来如果内核开启了`CONFIG_SLAB_FREELIST_HARDENED`保护，内核将获取一个随机数存放在结构体的`random`成员变量中。
1. 若开启了`SLAB_TYPESAFE_BY_RCU`选项(`RCU`是自`Kernel 2.5.43`其`Linux`官方加入的锁机制)，则设置结构体的`random`成员变量`reserved`为`rcu_head`结构体的大小。
<li>接下来调用`calculate_sizes()`计算并设置结构体内其他成员变量的值，首先会从结构体的`object_size`和`flag`中取值。
<ol>
1. 在`calculate_sizes()`中，内核首先将取到的`size`与`sizeof(void *)`指针大小对齐，这是为了能够将空闲指针存放至对象的边界中。
1. 接下来，若内核的调试模式(`CONFIG_SLUB_DEBUG`)被启用且`flag`中申明了用户会在对象释放后或者申请前访问对象，则需要调整`size`，以期能够在对象的前方和后方插入一些数据用来在调试时检测是否存在越界写。
1. 接下来设置结构体的`inuse`成员以表示元数据的偏移量，这也同时表示对象实际使用的大小，也意味着对象与空闲对象指针之间的可能偏移量。
1. 接下来判断是否允许用户越界写，若允许越界写，则对象末尾和空闲对象之间可能会存在其余数据，若不允许，则直接重定位空闲对象指针到对象末尾，并且设置`offset`成员的值。
1. 接下来，若内核的调试模式(`CONFIG_SLUB_DEBUG`)被启用且`flag`中申明了用户需要内核追踪该对象的使用轨迹信息，则需要调整`size`，在对象末尾加上两个`track`的空间大小，用于记录该对象的使用轨迹信息（分别是申请和释放的信息。
1. 接下来，内核将创建一个`kasan`缓存(`kasan`是`Kernel Address Sanitizer`的缩写，它是一个动态检测内存错误的工具，主要功能是检查内存越界访问和使用已释放的内存等问题。它在`Kernel 4.0`被正式引入内核中。
1. 接下来，若内核的调试模式(`CONFIG_SLUB_DEBUG`)被启用且`flag`中申明了用户可能会有越界写操作时，则需要调整`size`，以期能够在对象的后方插入空白边界用来捕获越界写的详细信息。
1. 由于出现了多次`size`调整的情况，那么很有可能现在的`size`已经被破坏了对齐关系，因此需要再做一次对齐操作，并将最终的`size`更新到结构体的`size`中。
1. 接下来通过`calculate_order()`计算单`slab`的页框阶数。
1. 最后调用到`oo_make`计算`kmem_cache`结构的`oo`、`min`、`max`等相关信息后，内核回到`kmem_cache_open`继续执行。1. 接下来内核会建立管理节点列表，并遍历每一个管理节点，遍历时，首先建立一个`struct kmem_cache_node`，然后内核会尝试使用`slab`分配器建立整个`slab_cache`(**当且仅当slab分配器部分或完全初始化时才可以使用这个分配器进行分配**)，那么显然，我们此时的`slab`分配器状态为`DOWN`。
<li>接下来程序将调用`early_kmem_cache_node_alloc()`尝试建立第一个节点对象。
<ol>
<li>在`early_kmem_cache_node_alloc()`中，内核会首先通过`new_slab()`创建`kmem_cache_node`结构空间对象的`slab`，它将会检查传入的`flag`是否合法，若合法，将会进入主分配函数`allocate_slab()`。
<ol>
1. 在主分配函数`allocate_slab()`中，内核会首先建立一个`page`结构体，此时若传入的`flag`带有`GFP`标志，程序将会启用内部中断。
1. 尝试使用`alloc_slab_page()`进行内存页面申请，若申请失败，则会将`oo`调至`s-&gt;min`进行降阶再次尝试申请，**再次失败则返回错误**！
1. 若申请成功，则开始初始化`page`结构体，设置`page`的`object`成员为从`oo`获取到的`object`，设置`page`的`slab_cache`成员为它所属的`slab_cache`，并将`page`链入节点中。
1. 接下来内核会对申请下来的页面的值利用 memset 进行初始化。
1. 接下来就是经过`kasan`的内存检查和调用`shuffle_freelist` 函数，`shuffle_freelist` 函数会根据`random_seq` 来把 `freelist` 链表的顺序打乱，这样内存申请的`object`后，下一个可以申请的`object`的地址也就变的不可预测。<li>进入`kmem_cache_alloc_node`后又会直接进入`slab_alloc_node`，最终的初始化工作将会在`slab_alloc_node`中完成。
<ol>
1. 进入`slab_alloc_node`后，调用`slab_pre_alloc_hook`进行预处理，返回一个用于分配`slub`对象的 `kmem_cache`。
1. 接下来如果`flag`标志位中启用了抢占功能，重新获取当前 CPU 的`kmem_cache_cpu`结构以及结构中的`tid`值。
1. 接下来加入一个`barrier`栅栏，然后获得当前cpu的空闲对象列表以及其使用的页面。
<li>当前`CPU`的`slub`空闲列表为空或者当前`slub`使用内存页面与管理节点不匹配时，需要重新分配`slub`对象，我们此时的空闲列表必定为空，因为我们之前仅仅在`early_kmem_cache_node_alloc()`将一个`slub`对象放在了`partial`链表中。那么，内核将会调用`__slab_alloc()`进行`slub`对象的分配。
<ol>
1. 在`__slab_alloc()`中，内核会首先禁用系统中断，并在那之后检查`flag`中是否允许抢占，若允许，则需要再次获取`CPU`。
<li>在那之后，调用`__slab_alloc()`的核心函数`___slab_alloc()`进行对象的分配。
<ol>
1. 在`___slab_alloc()`中，内核会首先检查有无活动的`slub`，此时必定没有，于是跳转到`new slab`处获取一个新的`slab`。
1. 然后内核会检查`partial`是否为空，不为空则从`partial`中取出`page`，然后跳转回`redo`重试分配。此处我们的`partial`显然不为空，那么取出`page`继续执行`redo`流程。
1. 首先检查本处理器所在节点是否指定节点一致，若不一致，则重新获取指定节点。
1. 如果节点还是不匹配，则移除`cpu slab`(释放每cpu变量的所有freelist对象指针)，进入`new_slab`流程。
1. 若一致，判断当前页面属性是否为`pfmemalloc`，如果不是则同样移除`cpu slab`，进入`new_slab`流程。
1. 再次检查空闲对象指针`freelist`是否为空，这是为了避免在禁止本地处理器中断前因发生了`CPU`迁移或者中断，导致本地的空闲对象指针不为空。
1. 如果不为空的情况下，将会跳转至`load_freelist`。
1. 如果为空，将会更新慢路径申请对象的统计信息，通过`get_freelist()`从非冻结页面（未在`cpu`缓存中）中获取空闲队列。
1. 若获取空闲队列失败则需要创建新的`slab`。
1. 此处我们之前是有初始化空闲队列操作的，因此直接跳转到`load_freelist`执行。
1. 从此列表中取出一个空闲对象，返回。


## 0x06 参考链接

[linux内核内存管理学习之一(基本概念，分页及初始化) – goodluckwhh](https://blog.csdn.net/goodluckwhh/article/details/9970845)

[【Linux内存源码分析】SLUB分配算法（4）- JeanLeo](https://www.jeanleo.com/2018/09/07/%5Blinux%E5%86%85%E5%AD%98%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%5Dslub%E5%88%86%E9%85%8D%E7%AE%97%E6%B3%95%EF%BC%884%EF%BC%89/)

[kmem_cache_alloc核心函数slab_alloc_node的实现详解 – 菜鸟别浪](https://blog.csdn.net/hzj_001/article/details/99706159)

[slub分配器 – itrocker](http://www.wowotech.net/memory_management/247.html)

[Linux伙伴系统(一)—伙伴系统的概述 – 橙色逆流](https://blog.csdn.net/vanbreaker/article/details/7605367)
