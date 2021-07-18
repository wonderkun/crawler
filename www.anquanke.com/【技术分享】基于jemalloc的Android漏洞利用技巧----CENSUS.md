
# 【技术分享】基于jemalloc的Android漏洞利用技巧----CENSUS


                                阅读量   
                                **296383**
                            
                        |
                        
                                                                                                                                    ![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：census-labs.com
                                <br>原文地址：[https://census-labs.com/media/shadow-infiltrate-2017.pdf](https://census-labs.com/media/shadow-infiltrate-2017.pdf)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](./img/85982/t01ef392845ec4a3709.jpg)](./img/85982/t01ef392845ec4a3709.jpg)

翻译：[**arnow117**](http://bobao.360.cn/member/contribute?uid=941579989)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**背景介绍**

**jemalloc的相关研究**

argp与huku在2012年在Phrack上发表的：对jemalloc内存分配器的单独利用(做出了基于FreeBSD上libc的POC)。

argp与huku在2012年BlackHat上发表的：在Firefo中玩坏jemalloc的元数据。

argp在2015年INFILTRATE上的jemalloc漏洞利用方法论。

**Android堆漏洞利用的相关研究**

Hanan Be'er对CVE-2015-3864这个stagefright中整形溢出导致堆破坏的漏洞利用

Aaron Adams的对这个漏洞的又一次利用

Joshua Drake对于stagefright漏洞利用相关工作 向之前的研究者们致谢！（这也是为什么要翻译这一段之必要）

**配合jemalloc使用的插件：Shadow**

**注，因为本文核心是jemalloc与堆漏洞利用，此章节关于对关于插件shadow的历史部分没有翻译。**

shadow是CENSUS开发的的一个基于jemalloc的堆漏洞利用框架，开源在Github([传送门](https://github.com/CENSUS/shadow))上。用来搭配调试器提供jemalloc分配器的内部结构信息。可以作为插件在GDB，WINDBG，以及lldb中使用。

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0102fc88296aac1e1a.png)

这个框架有几个优点：

没有多余的要附加的源文件。

对于Android与Firefox两个平台，使用相同的指令。

简化的调试引擎。

提供堆快照支持。



```
(gdb) jeparse -f
(gdb) jestore /tmp/snapshot1
```

提供单独的脚本，允许进行非运行时的堆排布分析。单独使用时样例：



```
$ python shadow.py /tmp/snapshot1 jeruns -c
listing current runs only
[arena 00 (0x0000007f85680180)] [bins 36]
[run 0x7f6ef81468] [region size 08] [total regions 512] [free regions 250]
[run 0x7f6e480928] [region size 16] [total regions 256] [free regions 051]
[run 0x7f6db81888] [region size 32] [total regions 128] [free regions 114]
...
```

提供对于堆中内存排布的解析脚本。作为Python插件包时的使用样例：



```
//code
import jemalloc
heap = jemalloc.jemalloc("/tmp/snapshot1")
for chunk in heap.chunks:
print "chunk @ 0x%x" % chunk.addr
//run
$ python print_chunks.py
chunk @ 0x7f6d240000
chunk @ 0x7f6db00000
chunk @ 0x7f6db40000
chunk @ 0x7f6db80000
chunk @ 0x7f6dbc0000
...
```



**jemalloc**

**jemalloc的一些特性**

jemalloc使用bitmap管理堆分配，而不是通过内存的利用率，这也可能是jemalloc被广泛使用的主要原因。当下FreeBSD libc，Firefox，Android libc，MySQL，Redis以及Facebook内部都在用。

设计原则

最小化的元数据开销

基于每个线程进行缓存，避免了同步问题。

避免了连续分配内存的碎片化问题。

简洁高效（所以就可以预判了哦呵呵）

**Android中的jemalloc**

在Android 6使用的版本实际上是4.0.0，在Android 7 上使用的版本是4.1.0-4-g33184bf69813087bf1885b0993685f9d03320c69

jemalloc在Android源码中的修改通过宏定义开关控制的代码块来实现，同时辅以/* Android change */的注释



```
#if defined(__ANDROID__)/* ANDROID change */
/* … */                 /* … */
#endif                  /* End ANDROID change */
```

在jemalloc的Android.mk中限制了仅使用两个arenas，并且开启了线程缓存(PS：本文的讨论基于64位的架构)



```
//part of Android.mk
jemalloc_common_cflags += 
-DANDROID_MAX_ARENAS=2 
-DJEMALLOC_TCACHE 
-DANDROID_TCACHE_NSLOTS_SMALL_MAX=8 
-DANDROID_TCACHE_NSLOTS_LARGE=16 
```

**jemalloc内部结构**

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01da12bf0eb6282fa6.png)

**概念：region**

调用malloc返回给用户的实际内存

在内存中连续分布

不包含元数据

根据大小不同，划分为三种类型：

Small，最大0x14336字节

Large，最大0x38000字节(Android 6上)

Huge，大于0x38000

可以使用shadow中的jebininfo列出当前线程所有的region，或者jesize列出满足给定size的region相关信息

```
//jebinfo
(gdb) jebininfo
[bin 00] [region size 008] [run size 04096] [nregs 0512]
[bin 01] [region size 016] [run size 04096] [nregs 0256]
[bin 02] [region size 032] [run size 04096] [nregs 0128]
[bin 03] [region size 048] [run size 12288] [nregs 0256]
[bin 04] [region size 064] [run size 04096] [nregs 0064]
[bin 05] [region size 080] [run size 20480] [nregs 0256]
[bin 06] [region size 096] [run size 12288] [nregs 0128]
[bin 07] [region size 112] [run size 28672] [nregs 0256]
//jesize
(gdb) jesize 24
[bin 02] [region size 032] [run size 04096] [nregs 0128]
```

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012df3d443e81128dc.png)

线程申请memory时，与region的对应关系。

**概念：run**

存放连续的大小相同的region的容器

一系列连续的页集合

内部存放small/large类型的region

没有元数据

查看给定的地址所属的run中的region信息



```
(gdb) jerun 0x7f931c0628
[region 000] [used] [0x0000007f931cc000] [0x0000000070957cf8]
[region 001] [used] [0x0000007f931cc008] [0x0000000070ea78b0]
[region 002] [used] [0x0000007f931cc010] [0x0000000070ec2868]
[region 003] [used] [0x0000007f931cc018] [0x0000000070f0322c]
...
(gdb) x/4gx 0x7f931cc000
0x7f931cc000: 0x0000000070957cf8 0x0000000070ea78b0
0x7f931cc010: 0x0000000070ec2868 0x0000000070f0322c
...
```



[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e1e93aa2da9ed146.png)

线程申请memory时，与run的对应关系。

**概念：chunk**

存放run的容器

大小固定相同

操作系统返回的内存被划分到chunk中管理

存储着关于自身以及它管理的run的元数据

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01dffc6e2ec4f216ce.png)

chunks的结构，与run以及元数据的关系。

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0191c6c09019b00992.png)

chunks中的元数据结构，mapbit[0]与mapmisc[0]指向chunk中的第一个run。

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01daefc49132c0e510.png)

chunks元数据中mapmisc中的bitmap结构管理着run中的region的分配使用。

**变化: 不同Android版本下的jemalloc**

Chunk的大小

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c6fe5456c94fb0b6.png)

元数据的变化

增加了mapbias与mapbits flags

**堆中的jemalloc**



```
root@bullhead/: cat /proc/self/maps | grep libc_malloc
7f81d00000-7f81d80000 rw-p 00000000 00:00 0 [anon:libc_malloc]
7f82600000-7f826c0000 rw-p 00000000 00:00 0 [anon:libc_malloc]
7f827c0000-7f82a80000 rw-p 00000000 00:00 0 [anon:libc_malloc]
7f82dc0000-7f830c0000 rw-p 00000000 00:00 0 [anon:libc_malloc]
(gdb) jechunks
[shadow] [chunk 0x0000007f81d00000] [arena 0x0000007f996800c0]
[shadow] [chunk 0x0000007f81d40000] [arena 0x0000007f996800c0]
[shadow] [chunk 0x0000007f82600000] [arena 0x0000007f996800c0]
[shadow] [chunk 0x0000007f82640000] [arena 0x0000007f996800c0]
[shadow] [chunk 0x0000007f82680000] [arena 0x0000007f996800c0]
[shadow] [chunk 0x0000007f827c0000] [arena 0x0000007f996800c0]
...
```

可以看到maps中0x7f81d00000对应的memory，属于两个chunk，分别位于0x7f81d00000以及0x7f81d40000。

**jemalloc的内存排布**

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012f97cf90ae3c7ae5.png)

jemalloc管理下的内存排布

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a1a7bba36f74962c.png)

溢出了region的示意图

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d402203d2c1c4ed7.png)

如果溢出了run的示意图

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c180a87a54dda326.png)

如果溢出了chunk的示意图，注意到，chunk头部有元数据。

**基于jemalloc的堆喷**

Hanan Be'er, Aaron Adams, Mark Brand, Joshua Drake都讨论过

region与run都没有元数据

堆喷的时候，chunk的第一个与最后一个页是不可喷的

chunk的地址是可以预测的

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0163a6c45334b1f7fc.png)

chunk中可堆喷的区域大小示意图

chunk地址可预测？

Google ProjectZero的Mark Brand曾经有说过

32位上：大chunk，而地址空间较小

mmap()产生多个chunk，而chunk大小固定。

Andorid进程通常加载很多模块

Android 7的chunk更大

同样适用于申请巨大的内存

可预测的chunk地址意味着

可预测的run地址

可预测的region地址

这些可以让我们做更有目的性的，更加精确的堆喷

**jemalloc的内存管理**

arena

arena内存申请器

用来缓解线程间申请memory时的竞争问题

每一个arena彼此独立，管理各自的chunk

每个线程在第一次malloc时，建立起与各自的arena的联系，一个线程只指向一个arena

每个进程中，arena的数量由jemalloc配置决定，在Android上硬编码为两个。

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0172c550faeab623b9.png)

在malloc申请内存中，arena与线程缓存的关系。

申请的memory在jemalloc内部实际是通过arena申请的，且在每一个线程中都有一个缓存。

查看进程的arena



```
//common
(gdb) x/2gx arenas
0x7f99680080: 0x0000007f997c0180 0x0000007f996800c0
//using shadow
(gdb) jearenas
[jemalloc] [arenas 02] [bins 36] [runs 1408]
[arena 00 (0x0000007f997c0180)] [bins 36] [threads: 1, 3, 5]
[arena 01 (0x0000007f996800c0)] [bins 36] [threads: 2, 4]
arena bin
```

每个arena都有一个bin数组

每一个bin对应着一种small类型，大小固定的region。

同时bin数组还肩负着用树存储未满的run的职责，并选一个作为当前指向的run

查看arena bin，runcur为对应region所属run的地址



```
(gdb) jebins
[arena 00 (0x7f997c0180)] [bins 36]
[bin 00 (0x7f997c0688)] [size class 08] [runcur 0x7f83080fe8]
[bin 01 (0x7f997c0768)] [size class 16] [runcur 0x7f82941168]
[bin 02 (0x7f997c0848)] [size class 32] [runcur 0x7f80ac0808]
[bin 03 (0x7f997c0928)] [size class 48] [runcur 0x7f81cc14c8]
[bin 04 (0x7f997c0a08)] [size class 64] [runcur 0x7f80ac0448]
...
```

查看当前run，以及其中region的信息。



```
(gdb) jeruns -c
[arena 00 (0x7f997c0180)] [bins 36]
[run 0x7f83080fe8] [region size 08] [total regions 512] [free regions 158]
[run 0x7f82941168] [region size 16] [total regions 256] [free regions 218]
[run 0x7f80ac0808] [region size 32] [total regions 128] [free regions 041]
[run 0x7f81cc14c8] [region size 48] [total regions 256] [free regions 093]
[run 0x7f80ac0448] [region size 64] [total regions 064] [free regions 007]
...
```

通过arena申请内存流程

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d9b245ccadf592c3.png)

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015ab8f0e6710ead8b.png)

申请size为8字节的memory时，先查bin，发现bin[0]所代表size为8的small region可以装的下，则查找对应存放这个连续region的run，并从中分配一块region返回。

通过arena释放内存流程

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f544e523f67f1645.png)

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e87e645849aabbce.png)

free与申请类似，查找到存放region的run，然后释放这个region。

arena中的线程缓存

什么是线程缓存(tcache)

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01548583e80f3f2ae1.png)

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01388da58d8cc99628.png)

arena与线程缓存的流程关系。

每一个线程维护着一个对small/large内存申请的缓存

对缓存的操作与栈相似

以申请时间为衡量的增长式“垃圾回收”机制

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01993d75858075ff89.png)

线程缓存栈以及其指向的run中region示意图，tbins[0]中存储着对应size的region缓存栈，每一种size的tbin中存储着其size下对应的缓存栈。

线程缓存在申请内存时候的作用

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d1d4006087146fb8.png)

还是刚才malloc的图，加上了tcache，可以看到，没有直接去通过arena要region，而是先去查对应size的tbin缓存栈avail去了。

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01223ab5171f7c66b7.png)

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d00f58c9cfa78640.png)

在缓存栈中，弹出一个最近被free“回收”到缓存栈上的内存地址做新malloc的返回地址。

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01df62201ded620e87.png)

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010b84d63de531fcff.png)

按照如此大小一直申请，最终栈会弹空。之后arena再通过元数据向run中要对应size的region，申请的数量是lg_fill_div，将返回的内存地址再压入缓存栈。

线程缓存在释放内存时的作用

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d4fc867580ac3396.png)

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011032913688f66842.png)

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016282706fc666651c.png)

释放与申请类似，只不过变成了将释放的地址压入缓存栈。

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014fdb27afefeb353c.png)

同样，缓存栈满了后arena也会将对应region还回去，但是每次只还一半。申请时间久的先被归还回去。缓存栈的容量在结构体tcache_bin_info中有定义。

tcache中的数据结构



```
struct tcache_s {
...
tcache_bin_t tbins[];
/* cached allocation
pointers (stacks) */
};
struct tcache_bin_s {
...
unsigned lg_fill_div;
unsigned ncached;
void **avail;
};
//tcache_bin_s 就是 tcache_bin_t
```

以上这些结构体的内存，是通过arenas[0]分配得到的。

每个线程的TSD中也会存着指向这些结构的指针。

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016a7e413e03247346.png)

内存中的tbin与其avail指针

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010dc7cc83ffd48b6e.png)

如何从线程中找到tcache，x0就是线程结构体的地址，其中key_data就是线程特有数据（也叫TSD）的指针，所以这里存放的就包含了tcache的地址。从shadow中可以看到TSD是在size类型为0x80的run中的。

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d3e285460071410d.png)

TSD中存放的tcache与arena的示意。从shadow中可以看到tcache是在size类型为0x1c00的run中的。

如果把tcache溢出了？

这些信息在arenas[0]中存放

tcache在size类型为0x1c00的run里分配，很难去找对并操作

但是这种情况有可能的

需要创建或者销毁线程

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011b1d716ec5633308.png)

那如果吧TSD溢出了呢？

TSD在size类型为0x80的run里分配，很难去找对并操作

这种情况有可能，但是也难达到

需要创建或者破坏线程相关信息

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01007d3ea340454ab1.png)

小结：jemalloc内部结构在堆中的布局

jemalloc中固定的部分有

arena的大小

tcache的大小

arena与线程的关联部分(比如TSD)的大小

结构地址随机化

但是有一点值得注意，线程缓存使得访问相邻的region更加容易



**利用shadow搞事情！**

**基于double free的利用姿势**

为什么要用这个呢，是因为之前我们没有在jemalloc里实践过这样的姿势

而且这个姿势在Android和Firefox都有通用的代码模式

可以很通用的使用

在第一次free对象后，控制之后的两次申请

只要申请相同大小就可以进行利用

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b76f5970e1f814c9.png)

double free的示例代码

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c17abd24dc70291b.png)

申请到了0x7f8fed1000，看看此时的tcache。

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0122bd911669bf7da4.png)

0x7f8fed1000压入tcache

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fb383266e6eda845.png)

受我们控制的第二次申请，又拿到了0x7f8fed1000

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fbded892b44005f6.png)

地址还回去，但是指针你留下来。最后我们用这个函数指针跳向我们想去的地方

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01777a2ca20d7cb877.png)

给函数指针赋值。

**任意地址free的利用前提**

不是简单的原型，通常是有缺陷的清理逻辑（比如对树中节点的移除）。

jemalloc对于free传入的地址没有很好的检查

Android加入的检查可以被绕过

释放后会把地址压入对应的线程缓存栈

释放时候页索引检查代码段：



```
chunk = (arena_chunk_t *)CHUNK_ADDR2BASE(ptr);
if (likely(chunk != ptr)) {
pageind = ((uintptr_t)ptr - (uintptr_t)chunk) &gt;&gt; LG_PAGE;
#if defined(__ANDROID__)
/* Verify the ptr is actually in the chunk. */
if (unlikely(pageind &lt; map_bias || pageind &gt;= chunk_npages)) {
__libc_fatal_no_abort(...)
return;
}
#endif
/* chunksize_mask = chunksize - 1 */
#define LG_PAGE 12
#define CHUNK_ADDR2BASE(a) ((void *)((uintptr_t)(a) &amp; ~chunksize_mask))
```

再来看看chunk的排布 

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0193ad3ab613795189.png)

chunk中对于mapbits的检查



```
mapbits = arena_mapbits_get(chunk, pageind);
assert(arena_mapbits_allocated_get(chunk, pageind) != 0);
#if defined(__ANDROID__)
/* Verify the ptr has been allocated. */
if (unlikely((mapbits &amp; CHUNK_MAP_ALLOCATED) == 0)) {
__libc_fatal(...);
}
#endif
if (likely((mapbits &amp; CHUNK_MAP_LARGE) == 0)) {
/* Small allocation. */
/* ... */
#define CHUNK_MAP_ALLOCATED ((size_t)0x1U)
#define CHUNK_MAP_LARGE ((size_t)0x2U)
```

把这两个检查绕过，就可以任意地址进行free了，当然我们就可以传入一个从run中拿到的地址。也就是说，我们可以释放并往tcache里面压栈一个非对齐的region指针，但是有一个字节会被破坏。最后重新申请被free的region就会导致溢出到下一个region，如下图所示。

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012aec6674ab14ae69.png)

**利用案例**

boot.oat 里面有Android框架层的所有编译的native代码，在启动时候随机化加载。

boot.art 装载着一系列栈初始化类信息，以及相关的对象。

加载地址对每一个设备来说地址固定，由第一次启动时决定

包含着指向boot.oat的指针

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0114e77b86054e122e.png)

在boot.art中我们找到一个函数指针0x713b6c40，我们先来分别计算mapbits，以及pagind，可以看到其绕过了这两个检查，注意64bit下的一些常量。

利用流程

1.	把这个在boot.art中指向boot.oat的地址通过free压入缓存栈

2.	malloc后从缓存栈中弹出这个地址

3.	把想要控制的PC的值写进新申请的memory里面，覆盖某个当前的函数指针

4.	等风来，调用这个函数指针。

如何找boot.art中的地址

用shadow的jefreecheck找到可以被free的地址

确保这个地址中存储的函数指针会被调用



```
(gdb) jefreecheck -b 0 boot.art
searching system@framework@boot.art (0x708ce000 -0x715c2000)
[page 0x712cf000]
+ 0x712cf000
+ 0x712cf028
+ 0x712cf038
+ 0x712cf060
+ 0x712cf070
...
```

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0133d745eeeacd3a8a.png)

为了举例方便，在这里面我们用gdb直接向malloc得到后的问题地址0x713b6c40写入非法值。可以看到0x713b6c40这个地址存储的是一个函数指针。

[![](./img/85982/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019c2d3c132e6d291a.png)

free这个地址后，通过malloc再获得这个地址，然后向这个地址所指向的内存写一些值，比如AAAAA，我们便成功的控制了PC。
