> 原文链接: https://www.anquanke.com//post/id/246929 


# musl-1.2.x堆部分源码分析


                                阅读量   
                                **128760**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t017f3d8904ecedfe33.jpg)](https://p2.ssl.qhimg.com/t017f3d8904ecedfe33.jpg)



## 简介

[musl libc](https://musl.libc.org/) 是一个专门为嵌入式系统开发的轻量级 libc 库，以简单、轻量和高效率为特色。有不少 Linux 发行版将其设为默认的 libc 库，用来代替体积臃肿的 glibc ，如 [Alpine Linux](https://zh.wikipedia.org/zh-cn/Alpine_Linux)（做过 Docker 镜像的应该很熟悉）、[OpenWrt](https://zh.wikipedia.org/wiki/OpenWrt)（常用于路由器）和 Gentoo 等<br>
1.2.x采用src/malloc/mallocng内的代码，其堆管理结构与早期版本几乎完全不同，而早期的堆管理器则放入了src/malloc/oldmalloc中。



## 数据结构
<li>chunk: 最基础的管理单位, 关于0x10B对齐, 存在空间复用, musl里面没有专门的struct, 比较坑, 假设p指向用户数据开头
<ul>
<li>如果是group中第一个chunk,
<ul>
- 那么p-0x10到p均为元数据, 作为group的头, 定义可以看struct group- p[-2], p[-1]这2B数据组成的uint_16, 代表offset, 表示与group中第一个地址的偏移
- p[-3]&amp;31组成的5bit代表idx, 表示这是group中第几个slot
```
struct chunk`{`
 char prev_user_data[];
    uint8_t idx;  //第5bit作为idx表示这是group中第几个chunk, 高3bit作为reserved
    uint16_t offset; //与第一个chunk的偏移
    char user_data[];
`}`;
```

[![](https://p0.ssl.qhimg.com/t01e36259daf6648b2f.png)](https://p0.ssl.qhimg.com/t01e36259daf6648b2f.png)
<li>group: 多个相同size的chunk的集合, 这些chunk是物理相邻的
<ul>
- 一片内存中, storage用来保存多个chunk, 元数据放在这片内存开头
- 一个group中第一个chunk的data为一个指针, 指向这个group的meta元数据, 对应meta结构体
<li>其余chunk使用offset表示与所属group中第一个chunk的偏移, 通过offset找到第一个chunk后, 再找到这个group对应的meta
<ul>
- offset = slot_n[-2]
- group = chunk_first = slot_n – offset*0x10
- meta = group-&gt;meta
```
#define UNIT 16
#define IB 4

struct group
`{`
    //以下是group中第一个slot的头0x10B
 struct meta *meta;       //0x80B指针
 unsigned char active_idx : 5;    //5bit idx
 char pad[UNIT - sizeof(struct meta *) - 1]; //padding为0x10B

    //以下为第一个chunk的用户数据区域+剩余所有chunk
 unsigned char storage[];     //chunk
`}`;
```

[![](https://p1.ssl.qhimg.com/t01c6260c3fe2230b80.png)](https://p1.ssl.qhimg.com/t01c6260c3fe2230b80.png)
<li>meta: meta通过bitmap来管理group中的chunk
<ul>
- meta之间以双向链表的形式形成一个队列结构, 如果说group是一纬的话, 那么meta队列就是二维的结构
- 一个meta对应一个group,
- 通过mem找到管理的group
- 通过sizeclass来追踪group中chunk的size
- freed_mask是已经被释放的chunk的bitmap, 4B
- avail_mask是目前可用的bitmap, 4B
- 由于bitmap的限制, 因此一个group中最多只能有32个chunk
- meta可以是brk分配的, 可以是mmap映射的, 但是group只能是mmap映射的, 原因在后面
[![](https://p1.ssl.qhimg.com/t01248e971dcd8f7092.png)](https://p1.ssl.qhimg.com/t01248e971dcd8f7092.png)

```
struct meta
`{`
 struct meta *prev, *next; //双向链表
 struct group *mem;    //管理的内存
 volatile int avail_mask, freed_mask;
 uintptr_t last_idx : 5;
 uintptr_t freeable : 1;
 uintptr_t sizeclass : 6;
 uintptr_t maplen : 8 * sizeof(uintptr_t) - 12;
`}`;
```
<li>meta_area: 是多个meta的集合,
<ul>
- mallocng分配meta时, 总是先分配一页的内存, 然后划分为多个带分配的meta区域
- meta_arena描述就是一页内存的最开始部分, slots可视为struct meta的集合
- 由于meta_arena位于一页内存的开头, 当meta被使用时, 通过清空12bit指针就可以找到meta_arena结构体
- 为了保证meta结构体是有效的, 并且不会被伪造, mallocng实现了一个验证机制, 保证meta是被meta_arena保护的
- 检查: 把一个arena指针的低12bit清空, 当做meta_arena结构体, 然后检查其中的check与__malloc_context中的secret是否一致
```
struct meta_area
`{`
 uint64_t check;   //校验值
 struct meta_area *next; //下一个分配区
 int nslots;    //多少个槽
 struct meta slots[]; //留给剩余的meta的槽
`}`;

/*
- 逻辑视图
__malloc_context.avtive[sc]
|
meta-&gt;|group头 | chunk | chunk| ...|
|
meta-&gt;|group头 | chunk | chunk| ...|
|
meta-&gt;|group头 | chunk | chunk| ...|
|

一个group视为一纬的, 是一个线性的结构, 包含多个chunk
一个meta通过bitmap来管理一个group中的chunk
一个avtive则是多个meta形成的循环队列头, 是一个二维的结构, 里面包含多个meta
active就是多个队列头组成的数组, 是一个三纬结构, 保护各个大小的meta队列
*/
```
<li>__malloc_context
<ul>
- 所有运行时信息都记录再ctx中, ctx是一个malloc_context结构体, 定义在so的data段
```
//malloc状态
struct malloc_context
`{`
 uint64_t secret;
#ifndef PAGESIZE
 size_t pagesize;
#endif
 int init_done;     //有无完成初始化
 unsigned mmap_counter;   //mmap内存总数
 struct meta *free_meta_head; //释放的meta组成的队列
 struct meta *avail_meta;  //指向可用meta数组
 size_t avail_meta_count, avail_meta_area_count, meta_alloc_shift;
 struct meta_area *meta_area_head, *meta_area_tail; //分配区头尾指针
 unsigned char *avail_meta_areas;
 struct meta *active[48];   //活动的meta
 size_t usage_by_class[48]; //这个大小级别使用了多少内存
 uint8_t unmap_seq[32], bounces[32];
 uint8_t seq;
 uintptr_t brk;
`}`;

struct malloc_context ctx = `{`0`}`;
```



## 基础操作
- meta形成的队列相关操作
```
//入队: meta组成一个双向链表的队列, queue(phead, m)会在phead指向的meta队列尾部插入m
static inline void queue(struct meta **phead, struct meta *m)
`{`
 //要求m-&gt;next m-&gt;prev都是NULL
 assert(!m-&gt;next);
 assert(!m-&gt;prev);
 if (*phead)
 `{` //把m插入到head前面, 属于队列的尾部插入, *phead仍然指向head
  struct meta *head = *phead;
  m-&gt;next = head;
  m-&gt;prev = head-&gt;prev;
  m-&gt;next-&gt;prev = m-&gt;prev-&gt;next = m;
 `}`
 else //队列式空的, 就只有m自己
 `{`
  m-&gt;prev = m-&gt;next = m;
  *phead = m;
 `}`
`}`

//出队: 从队列中删除m节点
static inline void dequeue(struct meta **phead, struct meta *m)
`{`
 if (m-&gt;next != m) //队列不只m自己
 `{`
  //队列中删除m
  m-&gt;prev-&gt;next = m-&gt;next;
  m-&gt;next-&gt;prev = m-&gt;prev;

  //如果删除的是头, 那么就把队列头设置为下一个
  if (*phead == m)
   *phead = m-&gt;next;
 `}`
 else //如果只有m自己, 那么队列就空了
 `{`
  *phead = 0;
 `}`

 //清理m中的prev和next指针
 m-&gt;prev = m-&gt;next = 0;
`}`

//获取队列头元素
static inline struct meta *dequeue_head(struct meta **phead)
`{`
 struct meta *m = *phead;
 if (m)
  dequeue(phead, m);
 return m;
`}`
```
- 内存指针转meta对象
<li>原理:
<ul>
- p – 固定偏移 =&gt; group结构体
- group-&gt;meta指针, 得到所属的meta对象
- meta地址与4K向下对齐, 就可找到位于一页开头的meta_area结构体, 但是检查多
```
static inline struct meta *get_meta(const unsigned char *p)
`{`
 assert(!((uintptr_t)p &amp; 15));    //地址关于0x10对齐
 int offset = *(const uint16_t *)(p - 2); //偏移
 int index = get_slot_index(p);    //获取slot的下标
 if (p[-4])         //如果offset不为0，表示不是group里的首个chunk，抛出异常
 `{`
  assert(!offset);
  offset = *(uint32_t *)(p - 8);
  assert(offset &gt; 0xffff);
 `}`
 const struct group *base = (const void *)(p - UNIT * offset - UNIT); //根据内存地址获得group结构地址
 const struct meta *meta = base-&gt;meta;         //根据meta指针获取管理这个group的meta对象

 //检查
 assert(meta-&gt;mem == base);      //自闭检查: meta-&gt;mem==base, base-&gt;meta==meta
 assert(index &lt;= meta-&gt;last_idx);    //?
 assert(!(meta-&gt;avail_mask &amp; (1u &lt;&lt; index))); //?
 assert(!(meta-&gt;freed_mask &amp; (1u &lt;&lt; index))); //?

 const struct meta_area *area = (void *)((uintptr_t)meta &amp; -4096); //一个arena放在4K的开头

 //canary检查
 assert(area-&gt;check == ctx.secret);

 //检查sizeclass
 if (meta-&gt;sizeclass &lt; 48)
 `{`
  assert(offset &gt;= size_classes[meta-&gt;sizeclass] * index);
  assert(offset &lt; size_classes[meta-&gt;sizeclass] * (index + 1));
 `}`
 else
 `{`
  assert(meta-&gt;sizeclass == 63);
 `}`

 if (meta-&gt;maplen)
 `{`
  assert(offset &lt;= meta-&gt;maplen * 4096UL / UNIT - 1);
 `}`
 return (struct meta *)meta;
`}`
```
<li>根据size找到对应的size类别, 这部分和larege bin的机制类似
<pre><code class="lang-C hljs">//size转对应类别
static inline int size_to_class(size_t n)
`{`
n = (n + IB - 1) &gt;&gt; 4;
if (n &lt; 10)
return n;
n++;
int i = (28 - a_clz_32(n)) * 4 + 8;
if (n &gt; size_classes[i + 1])
i += 2;
if (n &gt; size_classes[i])
i++;
return i;
`}`
</code></pre>
</li>


## malloc()
<li>先判断有无超过mmap的阈值, 如果超过就mmap分配
<ul>
- 如果没有超过, size转sc之后, 通过ctx.active[sc]找到对应的meta队列, 尝试从队列中首个meta里分配chunk
- 如果这个队列为空, 或者这个meta的avail里面没有合适的chunk, 那就调用alloc_slot()获取chunk
- 找到group与idx之后通过enframe()分配出这个chunk
```
void *malloc(size_t n)
`{`
 if (size_overflows(n)) //是否溢出
  return 0;
 struct meta *g;
 uint32_t mask, first;
 int sc;
 int idx;
 int ctr;

 if (n &gt;= MMAP_THRESHOLD) //太大了, 直接MMAP分配内存
 `{`
  size_t needed = n + IB + UNIT;
  void *p = mmap(0, needed, PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANON, -1, 0);
  if (p == MAP_FAILED)
   return 0;
  wrlock();
  step_seq();
  g = alloc_meta(); //获取一个meta
  if (!g)
  `{`
   unlock();
   munmap(p, needed);
   return 0;
  `}`

  //mmap得到的内存相关信息记录在这个meta对象中
  g-&gt;mem = p;    //内存指针
  g-&gt;mem-&gt;meta = g; //meta指针
  g-&gt;last_idx = 0;
  g-&gt;freeable = 1;
  g-&gt;sizeclass = 63;     //63表示mmap的
  g-&gt;maplen = (needed + 4095) / 4096; //映射内存的长度
  g-&gt;avail_mask = g-&gt;freed_mask = 0;
  // use a global counter to cycle offset in
  // individually-mmapped allocations.
  ctx.mmap_counter++;
  idx = 0;
  goto success;
 `}`

 //先从ctx中找meta

 sc = size_to_class(n); //计算size类别
 rdlock();      //对malloc上锁
 g = ctx.active[sc];    //根据size类别找到对应的meta

 // use coarse size classes initially when there are not yet
 // any groups of desired size. this allows counts of 2 or 3
 // to be allocated at first rather than having to start with
 // 7 or 5, the min counts for even size classes.
 /*
  当没有任何合适的size的group时使用更粗粒度的size classes
 */
 //对应meta为空 AND 4&lt;=sc&lt;32 AND sc!=6 AND sc是偶数 AND 这个sc没使用过内存
 if (!g &amp;&amp; sc &gt;= 4 &amp;&amp; sc &lt; 32 &amp;&amp; sc != 6 &amp;&amp; !(sc &amp; 1) &amp;&amp; !ctx.usage_by_class[sc])
 `{`
  size_t usage = ctx.usage_by_class[sc | 1];
  // if a new group may be allocated, count it toward
  // usage in deciding if we can use coarse class.
  //下面大概意思就是如果这个sc是空的, 那么就是使用更大的sc中的meta
  if (!ctx.active[sc | 1] || (!ctx.active[sc | 1]-&gt;avail_mask &amp;&amp; !ctx.active[sc | 1]-&gt;freed_mask))
   usage += 3;
  if (usage &lt;= 12)
   sc |= 1;
  g = ctx.active[sc];
 `}`

 //在此meta中寻找一个chunk
 for (;;)
 `{`
  mask = g ? g-&gt;avail_mask : 0; //meta中的可用内存的bitmap, 如果g为0那么就设为0, 表示没有可用chunk
  first = mask &amp; -mask;    //一个小技巧, 作用是找到mask的bit中第一个为1的bit
  if (!first)       //如果没找到就停止
   break;

  //设置avail_mask中first对应的bit为0
  if (RDLOCK_IS_EXCLUSIVE || !MT) //如果是排它锁, 那么下面保证成功
   g-&gt;avail_mask = mask - first;
  else if (a_cas(&amp;g-&gt;avail_mask, mask, mask - first) != mask) //如果是cas原子操作则需要for(;;)来自旋
   continue;

  //成功找到并设置avail_mask之后转为idx, 结束
  idx = a_ctz_32(first);
  goto success;
 `}`
 upgradelock();

 /*
  - 如果这个group没法满足, 那就尝试从别的地方获取: 
   - 使用group中被free的chunk
   - 使用队列中别的group
   - 分配一个group
 */
 idx = alloc_slot(sc, n);
 if (idx &lt; 0)
 `{`
  unlock();
  return 0;
 `}`
 g = ctx.active[sc]; //然后找到对应meta

success:
 ctr = ctx.mmap_counter;
 unlock();
 //从g中分配第idx个chunk, 大小为n
 return enframe(g, idx, n, ctr);
`}`
```
<li>alloc_slot()
<ul>
<li>首先会通过try_avail()在以下位置寻找可用的chunk,
<ul>
- freed_mask中
- 这个队列别的meta中
```
static int alloc_slot(int sc, size_t req)
`{`
 uint32_t first = try_avail(&amp;ctx.active[sc]); //尝试正在active[sc]队列内部分配chunk: 使用别的group, 移出freed_mask
 if (first)          //分配成功
  return a_ctz_32(first);

 struct meta *g = alloc_group(sc, req); //如果还不行, 那就只能为这个sc分配一个group
 if (!g)
  return -1;

 g-&gt;avail_mask--;
 queue(&amp;ctx.active[sc], g); //新分配的g入队
 return 0;
`}`
```
<li>try_avail()
<ul>
- 首先会再次尝试从avail_mask分配
- 然后查看这个meta中freed_mask中有无chunk,
- 如果freed_mask为空, 说明这个meta全部分配出去了, 就从队列中取出
- 如果有的话就会通过active_group()把freed_mask中的chunk转移到avail_mask中
```
static uint32_t try_avail(struct meta **pm)
`{`
 struct meta *m = *pm;
 uint32_t first;
 if (!m) //如果ctx.active[sc]==NULL, 那么就无法尝试使用avail
  return 0;
 uint32_t mask = m-&gt;avail_mask;
 if (!mask) //如果avail中没有可用的, 有可能其他线程释放了chunk
 `{`
  if (!m) //同上
   return 0;
  if (!m-&gt;freed_mask) //如果freed_mask也为空
  `{`
   dequeue(pm, m); //那么就从队列中弹出
   m = *pm;
   if (!m)
    return 0;
  `}`
  else
  `{`
   m = m-&gt;next; //否则pm使用m的下一个作为队列开头, 应该是为了每次malloc与free的时间均衡
   *pm = m;
  `}`

  mask = m-&gt;freed_mask; //看一下group中被free的chunk

  // skip fully-free group unless it's the only one
  // or it's a permanently non-freeable group
  //如果这个group所有的chunk都被释放了, 那么就尝试使用下一个group, 应该是为了每次malloc与free的时间均衡
  if (mask == (2u &lt;&lt; m-&gt;last_idx) - 1 &amp;&amp; m-&gt;freeable)
  `{`
   m = m-&gt;next;
   *pm = m;
   mask = m-&gt;freed_mask;
  `}`

  //((2u &lt;&lt; m-&gt;mem-&gt;active_idx) - 1)建立一个掩码, 如果acctive_idx为3, 那么就是0b1111
  if (!(mask &amp; ((2u &lt;&lt; m-&gt;mem-&gt;active_idx) - 1))) //如果这个group中有free的chunk, 但是不满足avtive_idx的要求
  `{`
   //如果meta后面还有meta, 那么就切换到后一个meta, 由于avail与free都为0的group已经在上一步出队了, 因此后一个group一定有满足要求的chunk
   if (m-&gt;next != m)
   `{`
    m = m-&gt;next;
    *pm = m;
   `}`
   else
   `{`
    int cnt = m-&gt;mem-&gt;active_idx + 2;
    int size = size_classes[m-&gt;sizeclass] * UNIT;
    int span = UNIT + size * cnt;
    // activate up to next 4k boundary
    while ((span ^ (span + size - 1)) &lt; 4096)
    `{`
     cnt++;
     span += size;
    `}`
    if (cnt &gt; m-&gt;last_idx + 1)
     cnt = m-&gt;last_idx + 1;
    m-&gt;mem-&gt;active_idx = cnt - 1;
   `}`
  `}`
  mask = activate_group(m);  //激活这个group, 把free的chunk转移到avail中,其实就是交换下bitmap的事
  assert(mask);     //由于group中freed_mask非空, 因此一定会找到可用的chunk, 所以返回的avail_mask一定非0
  decay_bounces(m-&gt;sizeclass); //?
 `}`
 //经过上面的操作, 已经使得m的group中有可用的mask, 因此取出就好
 first = mask &amp; -mask;
 m-&gt;avail_mask = mask - first;
 return first;
`}`
```
<li>alloc_group()
<ul>
- 首先会通过alloc_meta()分配一个meta, 用来管理后面分配的group
- 计算好需要的长度后通过mmap()匿名映射一片内存作为group
- 然后初始化meta中相关信息
```
//新分配一个size_class为sc的group
static struct meta *alloc_group(int sc, size_t req)
`{`
 size_t size = UNIT * size_classes[sc]; //大小
 int i = 0, cnt;
 unsigned char *p;
 struct meta *m = alloc_meta(); //分配group前先分配一个meta用来管理group
 if (!m)
  return 0;
 size_t usage = ctx.usage_by_class[sc];
 size_t pagesize = PGSZ;
 int active_idx;
 if (sc &lt; 9)
 `{`
  while (i &lt; 2 &amp;&amp; 4 * small_cnt_tab[sc][i] &gt; usage)
   i++;
  cnt = small_cnt_tab[sc][i];
 `}`
 else
 `{`
  ...
 `}`

 // If we selected a count of 1 above but it's not sufficient to use
 // mmap, increase to 2. Then it might be; if not it will nest.
 if (cnt == 1 &amp;&amp; size * cnt + UNIT &lt;= pagesize / 2)
  cnt = 2;

 // All choices of size*cnt are "just below" a power of two, so anything
 // larger than half the page size should be allocated as whole pages.
 if (size * cnt + UNIT &gt; pagesize / 2)
 `{`
  // check/update bounce counter to start/increase retention
  // of freed maps, and inhibit use of low-count, odd-size
  // small mappings and single-slot groups if activated.
  int nosmall = is_bouncing(sc);
  account_bounce(sc);
  step_seq();

  // since the following count reduction opportunities have
  // an absolute memory usage cost, don't overdo them. count
  // coarse usage as part of usage.
  if (!(sc &amp; 1) &amp;&amp; sc &lt; 32)
   usage += ctx.usage_by_class[sc + 1];

  // try to drop to a lower count if the one found above
  // increases usage by more than 25%. these reduced counts
  // roughly fill an integral number of pages, just not a
  // power of two, limiting amount of unusable space.
  if (4 * cnt &gt; usage &amp;&amp; !nosmall)
  `{`
   ...
  `}`
  size_t needed = size * cnt + UNIT;
  needed += -needed &amp; (pagesize - 1);

  // produce an individually-mmapped allocation if usage is low,
  // bounce counter hasn't triggered, and either it saves memory
  // or it avoids eagar slot allocation without wasting too much.
  if (!nosmall &amp;&amp; cnt &lt;= 7)
  `{`
   req += IB + UNIT;
   req += -req &amp; (pagesize - 1);
   if (req &lt; size + UNIT || (req &gt;= 4 * pagesize &amp;&amp; 2 * cnt &gt; usage))
   `{`
    cnt = 1;
    needed = req;
   `}`
  `}`

  //映射一片内存作为group, 被一开始分配的meta管理
  p = mmap(0, needed, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0);
  if (p == MAP_FAILED)
  `{`
   free_meta(m);
   return 0;
  `}`
  m-&gt;maplen = needed &gt;&gt; 12;
  ctx.mmap_counter++;
  active_idx = (4096 - UNIT) / size - 1;
  if (active_idx &gt; cnt - 1)
   active_idx = cnt - 1;
  if (active_idx &lt; 0)
   active_idx = 0;
 `}`
 else
 `{`
  int j = size_to_class(UNIT + cnt * size - IB);
  int idx = alloc_slot(j, UNIT + cnt * size - IB);
  if (idx &lt; 0)
  `{`
   free_meta(m);
   return 0;
  `}`
  struct meta *g = ctx.active[j];
  p = enframe(g, idx, UNIT * size_classes[j] - IB, ctx.mmap_counter);
  m-&gt;maplen = 0;
  p[-3] = (p[-3] &amp; 31) | (6 &lt;&lt; 5);
  for (int i = 0; i &lt;= cnt; i++)
   p[UNIT + i * size - 4] = 0;
  active_idx = cnt - 1;
 `}`
 ctx.usage_by_class[sc] += cnt; //这个sc又增加了cnt个chunk
 m-&gt;avail_mask = (2u &lt;&lt; active_idx) - 1;
 m-&gt;freed_mask = (2u &lt;&lt; (cnt - 1)) - 1 - m-&gt;avail_mask;
 m-&gt;mem = (void *)p;
 m-&gt;mem-&gt;meta = m;
 m-&gt;mem-&gt;active_idx = active_idx;
 m-&gt;last_idx = cnt - 1;
 m-&gt;freeable = 1;
 m-&gt;sizeclass = sc;
 return m;
`}`
```
<li>alloc_meta()
<ul>
- 先看有无初始化设置ctx的随机数
- 如果ctx的free_meta_head链表中有空闲的meta, 那么直接从这里分配一个meta
<li>如果没有可用的, 那么就说明需要向OS申请内存存放meta
<ul>
- 先通过brk分配1页,
- 如果brk失败的话则会通过mmap()分配许多页内存, 但是这些内存都是PROT_NONE的, 属于guard page, 堆溢出到这些页面会引发SIGV, 而meta不使用开头与结尾的一页, 防止被溢出
```
//分配一个meta对象, 有可能是用的空闲的meta, 也可能是新分配一页划分的
struct meta *alloc_meta(void)
`{`
 struct meta *m;
 unsigned char *p;

 //如果还没初始化, 就设置secret
 if (!ctx.init_done)
 `{`
#ifndef PAGESIZE
  ctx.pagesize = get_page_size();
#endif
  ctx.secret = get_random_secret(); //设置secret为随机数
  ctx.init_done = 1;
 `}`

 //设置pagesize
 size_t pagesize = PGSZ;
 if (pagesize &lt; 4096)
  pagesize = 4096;

 //如果能从空闲meta队列free_meta_head中得到一个meta, 就可直接返回
 if ((m = dequeue_head(&amp;ctx.free_meta_head)))
  return m;

 //如果没有空闲的, 并且ctx中也没有可用的, 就通过mmap映射一页作为meta数组
 if (!ctx.avail_meta_count)
 `{`
  int need_unprotect = 1;

  //如果ctx中没有可用的meta, 并且brk不为-1
  if (!ctx.avail_meta_area_count &amp;&amp; ctx.brk != -1)
  `{`
   uintptr_t new = ctx.brk + pagesize; //新分配一页
   int need_guard = 0;
   if (!ctx.brk) //如果cnt中brk为0
   `{`
    need_guard = 1;
    ctx.brk = brk(0); //那就调用brk()获取当前的heap地址
    // some ancient kernels returned _ebss
    // instead of next page as initial brk.
    ctx.brk += -ctx.brk &amp; (pagesize - 1); //设置ctx.brk与new
    new = ctx.brk + 2 * pagesize;
   `}`
   if (brk(new) != new) //brk()分配heap到new地址失败
   `{`
    ctx.brk = -1;
   `}`
   else //如果brk()分批额成功
   `{`
    if (need_guard) //保护页, 在brk后面映射一个不可用的页(PROT_NONE), 如果堆溢出到这里就会发送SIGV
     mmap((void *)ctx.brk, pagesize, PROT_NONE, MAP_ANON | MAP_PRIVATE | MAP_FIXED, -1, 0);
    ctx.brk = new;
    ctx.avail_meta_areas = (void *)(new - pagesize); //把这一页全划分为meta
    ctx.avail_meta_area_count = pagesize &gt;&gt; 12;
    need_unprotect = 0;
   `}`
  `}`

  if (!ctx.avail_meta_area_count) //如果前面brk()分配失败了, 直接mmap匿名映射一片PROT_NONE的内存再划分
  `{`
   size_t n = 2UL &lt;&lt; ctx.meta_alloc_shift;
   p = mmap(0, n * pagesize, PROT_NONE, MAP_PRIVATE | MAP_ANON, -1, 0);
   if (p == MAP_FAILED)
    return 0;
   ctx.avail_meta_areas = p + pagesize;
   ctx.avail_meta_area_count = (n - 1) * (pagesize &gt;&gt; 12);
   ctx.meta_alloc_shift++;
  `}`

  //如果avail_meta_areas与4K对齐, 那么就说明这片区域是刚刚申请的一页, 所以需要修改内存的权限
  p = ctx.avail_meta_areas;
  if ((uintptr_t)p &amp; (pagesize - 1))
   need_unprotect = 0;
  if (need_unprotect)
   if (mprotect(p, pagesize, PROT_READ | PROT_WRITE) &amp;&amp; errno != ENOSYS)
    return 0;
  ctx.avail_meta_area_count--;
  ctx.avail_meta_areas = p + 4096;
  if (ctx.meta_area_tail)
  `{`
   ctx.meta_area_tail-&gt;next = (void *)p;
  `}`
  else
  `{`
   ctx.meta_area_head = (void *)p;
  `}`

  //ctx中记录下相关信息
  ctx.meta_area_tail = (void *)p;
  ctx.meta_area_tail-&gt;check = ctx.secret;
  ctx.avail_meta_count = ctx.meta_area_tail-&gt;nslots = (4096 - sizeof(struct meta_area)) / sizeof *m;
  ctx.avail_meta = ctx.meta_area_tail-&gt;slots;
 `}`

 //ctx的可用meta数组中有能用的, 就直接分配一个出来
 ctx.avail_meta_count--;
 m = ctx.avail_meta++;  //取出一个meta
 m-&gt;prev = m-&gt;next = 0; //这俩指针初始化为0
 return m;
`}`
```
<li>enframe()
<ul>
- 先找到g中第idx个chunk的开始地址与结束地址
- 然后设置idx与offset等信息
```
static inline void *enframe(struct meta *g, int idx, size_t n, int ctr)
`{`
 size_t stride = get_stride(g);        //g负责多大的内存
 size_t slack = (stride - IB - n) / UNIT;     //chunk分配后的剩余内存: (0x30 - 4 - 0x20)/0x10 = 0
 unsigned char *p = g-&gt;mem-&gt;storage + stride * idx; //使用这个meta管理的内存中第idx个chunk,
 unsigned char *end = p + stride - IB;      //这个chunk结束的地方

 // cycle offset within slot to increase interval to address
 // reuse, facilitate trapping double-free.
 //slot内循环偏移增加地址复用之间的间隔
 //如果idx!=0, 那么就用chunk-&gt;offset设置off, 否则就用ctr
 int off = (p[-3] ? *(uint16_t *)(p - 2) + 1 : ctr) &amp; 255;
 assert(!p[-4]);
 if (off &gt; slack)
 `{`
  size_t m = slack;
  m |= m &gt;&gt; 1;
  m |= m &gt;&gt; 2;
  m |= m &gt;&gt; 4;
  off &amp;= m;
  if (off &gt; slack)
   off -= slack + 1;
  assert(off &lt;= slack);
 `}`
 if (off)
 `{`
  // store offset in unused header at offset zero
  // if enframing at non-zero offset.
  *(uint16_t *)(p - 2) = off;
  p[-3] = 7 &lt;&lt; 5;
  p += UNIT * off;
  // for nonzero offset there is no permanent check
  // byte, so make one.
  p[-4] = 0;
 `}`
 *(uint16_t *)(p - 2) = (size_t)(p - g-&gt;mem-&gt;storage) / UNIT; //设置与group中第一个chunk的偏移
 p[-3] = idx;             //设置idx
 set_size(p, end, n);
 return p;
`}`
```
<li>总结, mallocng有如下特性
<ul>
- chunk按照bitmap从低到高依次分配
- 被free掉的内存会先进入freed_mask, 当avail_mask耗尽时才会使用freed_mask中的
- mallocng把meta与group隔离开来, 来减缓堆溢出的危害


## free()
- 先通过get_meta()找到chunk对应的meta
- 然后重置idx与offset
- 然后再meta的freed_mask中标记一下就算释放完毕了
- 然后调用nontrivial_free()处理meta相关操作
```
void free(void *p)
`{`
 if (!p)
  return;

 struct meta *g = get_meta(p);  //获取chunk所属的meta
 int idx = get_slot_index(p);   //这是group中第几个chunk
 size_t stride = get_stride(g); //这个group负责的大小
 unsigned char *start = g-&gt;mem-&gt;storage + stride * idx;
 unsigned char *end = start + stride - IB;
 get_nominal_size(p, end);          // 根据reserved来算真实大小
 uint32_t self = 1u &lt;&lt; idx, all = (2u &lt;&lt; g-&gt;last_idx) - 1; //计算这个chunk的bitmap
 ((unsigned char *)p)[-3] = 255;         //idx与offset都无效
 // invalidate offset to group header, and cycle offset of
 // used region within slot if current offset is zero.
 *(uint16_t *)((char *)p - 2) = 0;

 // release any whole pages contained in the slot to be freed
 // unless it's a single-slot group that will be unmapped.
 //释放slot中的一整页
 if (((uintptr_t)(start - 1) ^ (uintptr_t)end) &gt;= 2 * PGSZ &amp;&amp; g-&gt;last_idx)
 `{`
  unsigned char *base = start + (-(uintptr_t)start &amp; (PGSZ - 1));
  size_t len = (end - base) &amp; -PGSZ;
  if (len)
   madvise(base, len, MADV_FREE);
 `}`

 // atomic free without locking if this is neither first or last slot
 //在meta-&gt;freed_mask中标记一下, 表示这个chunk已经被释放了
 //如果既不是中间的slot也不是末尾的slot, 那么释放时不需要锁
 for (;;)
 `{`
  uint32_t freed = g-&gt;freed_mask;
  uint32_t avail = g-&gt;avail_mask;
  uint32_t mask = freed | avail; //mask = 所有被释放的chunk + 现在可用的chunk
  assert(!(mask &amp; self));     //要释放的chunk应该既不在freed中, 也不在avail中

  /*
   - 两种不能只设置meta的mask的情况, 这两种情况不设置mask, break后调用nontrivial_free()处理
    - 如果!freed, 就说明meta中没有被释放的chunk, 有可能这个group全部被分配出去了, 这样group是会弹出avtive队列的, 
     而现在释放了一个其中的chunk, 需要条用nontrivial_free()把这个group重新加入队列
    - 如果mask+self==all, 那就说明释放了这个chunk, 那么这个group中所有的chunk都被回收了, 
     因此这个meta需要调用nontrivial_free()回收这个group
  */
  if (!freed || mask + self == all)
   break;

  //设置freed_mask, 表示这个chunk被释放了
  if (!MT) //如果是单线程,直接写就好了
   g-&gt;freed_mask = freed + self;
  else if (a_cas(&amp;g-&gt;freed_mask, freed, freed + self) != freed) //如遇多线程使用原子操作, 一直循环到g-&gt;freed_mask为freed+self为止
   continue;
  return;
 `}`

 wrlock();
 struct mapinfo mi = nontrivial_free(g, idx); //处理涉及到meta之间的操作
 unlock();
 if (mi.len)
  munmap(mi.base, mi.len);
`}`
```
<li>nontrivial_free()
<ul>
- 根据free()进入这个函数的方式可以知道, 此时还没有设置freed_mask
<li>如果发现这个group中所有的chunk要么被free, 要么是可用的, 那么就会回收掉这个group
<ul>
- 先调用dequeue从队列中出队
- 如果队里中后面还有meta的话, 就会激活后一个meta
- 然后调用free_group()释放整个group- 那么说明malloc分配出最后一个chunk的时候已经把这个meta给弹出队列了
- 但是现在里面有一个chunk被释放了, 这个meta就应该再次回归队列, 因此调用queue()再次入队
```
static struct mapinfo nontrivial_free(struct meta *g, int i)
`{`
 uint32_t self = 1u &lt;&lt; i;
 int sc = g-&gt;sizeclass;
 uint32_t mask = g-&gt;freed_mask | g-&gt;avail_mask;

 //如果group中所有chunk要么被释放要么可使用, 并且g可以被释放, 那么就要回收掉整个meta
 if (mask + self == (2u &lt;&lt; g-&gt;last_idx) - 1 &amp;&amp; okay_to_free(g))
 `{`
  // any multi-slot group is necessarily on an active list
  // here, but single-slot groups might or might not be.
  if (g-&gt;next) //如果g有下一个
  `{`
   assert(sc &lt; 48);        //检查: sc合法, 不是mmap的
   int activate_new = (ctx.active[sc] == g); //如果g是队列中开头的meta, 那么弹出队列后, 要激活后一个
   dequeue(&amp;ctx.active[sc], g);     //这个meta出队

   //如果队列存在后一个meta, 那么就激活他, 因为之前为了free的快速, 只是用freed_mask标记了一下而已, 现在要转移到avail_mask中了
   if (activate_new &amp;&amp; ctx.active[sc])
    activate_group(ctx.active[sc]);
  `}`
  return free_group(g); //meta已经取出, 现在要释放这个meta
 `}`
 else if (!mask) //如果mask==0, 也就是这个group中所有的chunk都被分配出去了
 `{`    //那么这个meta在malloc()=&gt;alloc_slot()=&gt;try_avail()最终就被弹出队列了, 目的取出队列中不可能再被分配的, 提高效率
     //现在这个全部chunk被分配出去的group中有一个chunk被释放了, 因此这个meta要重新入队
  assert(sc &lt; 48);
  // might still be active if there were no allocations
  // after last available slot was taken.
  if (ctx.active[sc] != g)
  `{`
   queue(&amp;ctx.active[sc], g); //重新入队
  `}`
 `}`
 a_or(&amp;g-&gt;freed_mask, self);
 return (struct mapinfo)`{`0`}`;
`}`
```



## 可利用的点
- mallocng防御堆溢出的方法是meta与分配chunk的group在地址上分离, 并且在meta所在页的前后设置一个NON_PROT的guard page, 来防止发生在group上的堆溢出影响到meta, 产生arbitrary alloc, 因此无法从溢出meta队列
<li>但是队列操作中并没有对mete的prev与next指针进行检查, 属于unsafe unlink, 原因可以能是作者认为, 既然meta无法被修改, 那么meta中的指针一定是正确的<br>[![](https://p4.ssl.qhimg.com/t01703f7f88cece164c.png)](https://p4.ssl.qhimg.com/t01703f7f88cece164c.png)
</li>
- 其实不然, 我们确实无法直接溢出meta, 但是这不代表这我们无法伪造meta结构体
<li>思路
<ul>
- 我们可以溢出一个chunk, 伪造他的offset与next, 使其指向我们伪造的group,
- 然后伪造group中的meta指针, 使其指向我们伪造的meta
- 然后伪造meta中的prev next指针, 并且伪造freed_mask与avail_mask, 做出一副这个meta中的chunk已经全部被释放了的样子, 这样就会调用: free()=&gt;nontrivial_free()=&gt;dequeue()完成攻击