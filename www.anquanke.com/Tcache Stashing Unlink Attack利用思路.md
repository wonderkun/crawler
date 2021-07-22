> 原文链接: https://www.anquanke.com//post/id/198173 


# Tcache Stashing Unlink Attack利用思路


                                阅读量   
                                **918846**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01f0e8ebb8128ab9f0.jpg)](https://p0.ssl.qhimg.com/t01f0e8ebb8128ab9f0.jpg)

## 0x00 写在前面

`Tcache Stashing Unlink Attack`这个攻击名词是我第一次见到的，因此写一篇文章以记录思路。

2020/03/13 更新：`Tcache Stashing Unlink Attack`有了更深的利用方式，从本来的任意地址写一个指定值或可扩大到任意地址分配chunk进而做到任意地址读写。

## 0x01 前置知识

### House of Lore Attack

`Tcache Stashing Unlink Attack`也是利用了`Smallbin`的相关分配机制进行的攻击，因此此处先对`House of Lore`这一攻击技术做一个简要的介绍。

#### 攻击目标

分配任意指定位置的 chunk，从而修改任意地址的内存。（任意地址写）

#### 攻击前提

能控制 Small Bin Chunk 的 bk 指针，并且控制指定位置 chunk 的 fd 指针。

#### 攻击原理

##### 漏洞源码（Glibc2.29 malloc.c line3639）

⚠️：代码中的英文注释为源代码自带，中文注释为分析，Tcache部分不做分析。

```
Small Bin</code>的`malloc`做更多的保护~</p>
<h5 class="md-end-block md-heading" style="box-sizing: border-box; break-after: avoid-page; break-inside: avoid; font-size: 1em; margin-top: 1rem; margin-bottom: 1rem; line-height: 1.4; cursor: text; white-space: pre-wrap; color: #333333; font-family: 'Open Sans', 'Clear Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;">漏洞分析</h5>
<pre class="md-fences md-end-block ty-contain-cm modeLoaded" style="box-sizing: border-box; overflow: visible; font-family: var(--monospace); font-size: 0.9em; display: block; break-inside: avoid; text-align: left; background-image: inherit; background-position: inherit; background-size: inherit; background-repeat: inherit; background-attachment: inherit; background-origin: inherit; background-clip: inherit; background-color: #f8f8f8; border-radius: 3px; padding: 8px 4px 6px; margin-bottom: 15px; margin-top: 15px; width: inherit; color: #333333; border: 1px solid #e7eaed;" spellcheck="false">// 获取 small bin 中倒数第二个 chunk 。
bck = victim-&gt;bk;
// 检查 bck-&gt;fd 是不是 victim，防止伪造
if ( __glibc_unlikely( bck-&gt;fd != victim ) )
    malloc_printerr ("malloc(): smallbin double linked list corrupted");
// 设置 victim 对应的 inuse 位
set_inuse_bit_at_offset (victim, nb);
// 修改 small bin 链表，将 small bin 的最后一个 chunk 取出来
bin-&gt;bk = bck;
bck-&gt;fd = bin;</pre>
也就是说，如果此处我们能够控制 small bin 的最后一个 chunk 的 bk 为我们想要写入的内存地址，并且保证`__glibc_unlikely( bck-&gt;fd != victim )`检查通过就可以在small bin中加入我们想加入的Chunk，进而在内存的任意地址分配一个Chunk！
<h3 name="h3-3" id="h3-3">Tcache Stashing Unlink Attack</h3>
<h4 class="md-end-block md-heading" style="box-sizing: border-box; break-after: avoid-page; break-inside: avoid; font-size: 1.25em; margin-top: 1rem; margin-bottom: 1rem; line-height: 1.4; cursor: text; white-space: pre-wrap; color: #333333; font-family: 'Open Sans', 'Clear Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;">攻击目标</h4>
<ol class="ol-list" style="box-sizing: border-box; margin: 0.8em 0px; padding-left: 30px; color: #333333; font-family: 'Open Sans', 'Clear Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 16px;" start="">
<li class="md-list-item" style="box-sizing: border-box; margin: 0px; position: relative;">
向任意指定位置写入指定值。
</li>
<li class="md-list-item" style="box-sizing: border-box; margin: 0px; position: relative;">
向任意地址分配一个Chunk。
</li>
</ol>
<h4 class="md-end-block md-heading" style="box-sizing: border-box; break-after: avoid-page; break-inside: avoid; font-size: 1.25em; margin-top: 1rem; margin-bottom: 1rem; line-height: 1.4; cursor: text; white-space: pre-wrap; color: #333333; font-family: 'Open Sans', 'Clear Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;">攻击前提</h4>
<ol class="ol-list" style="box-sizing: border-box; margin: 0.8em 0px; padding-left: 30px; color: #333333; font-family: 'Open Sans', 'Clear Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 16px;" start="">
<li class="md-list-item" style="box-sizing: border-box; margin: 0px; position: relative;">
能控制 Small Bin Chunk 的 bk 指针。
</li>
<li class="md-list-item" style="box-sizing: border-box; margin: 0px; position: relative;">
程序可以越过Tache取Chunk。(使用calloc即可做到)
</li>
<li class="md-list-item" style="box-sizing: border-box; margin: 0px; position: relative;">
程序至少可以分配两种不同大小且大小为unsorted bin的Chunk。
</li>
</ol>
<h4 class="md-end-block md-heading" style="box-sizing: border-box; break-after: avoid-page; break-inside: avoid; font-size: 1.25em; margin-top: 1rem; margin-bottom: 1rem; line-height: 1.4; cursor: text; white-space: pre-wrap; color: #333333; font-family: 'Open Sans', 'Clear Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;">攻击原理</h4>
我们首先分析`House of Lore Attack`中所忽视的Tcache相关代码。
<pre class="md-fences md-end-block ty-contain-cm modeLoaded" style="box-sizing: border-box; overflow: visible; font-family: var(--monospace); font-size: 0.9em; display: block; break-inside: avoid; text-align: left; background-image: inherit; background-position: inherit; background-size: inherit; background-repeat: inherit; background-attachment: inherit; background-origin: inherit; background-clip: inherit; background-color: #f8f8f8; border-radius: 3px; padding: 8px 4px 6px; margin-bottom: 15px; margin-top: 15px; width: inherit; color: #333333; border: 1px solid #e7eaed;" spellcheck="false">#if USE_TCACHE //如果程序启用了Tcache
        /* While we're here, if we see other chunks of the same size,
        stash them in the tcache.  */
        //遍历整个smallbin，获取相同size的free chunk
        size_t tc_idx = csize2tidx (nb);
        if (tcache &amp;&amp; tc_idx &lt; mp_.tcache_bins)
        `{`
            mchunkptr tc_victim;
            /* While bin not empty and tcache not full, copy chunks over.  */
            //判定Tcache的size链表是否已满，并且取出smallbin的末尾Chunk。
            //验证取出的Chunk是否为Bin本身（Smallbin是否已空）
            while ( tcache-&gt;counts[tc_idx] &lt; mp_.tcache_count
                   &amp;&amp; (tc_victim = last (bin) ) != bin)
            `{`
                //如果成功获取了Chunk
                if (tc_victim != 0)
                `{`
                    // 获取 small bin 中倒数第二个 chunk 。
                    bck = tc_victim-&gt;bk;
                    //设置标志位
                    set_inuse_bit_at_offset (tc_victim, nb);
                    // 如果不是 main_arena，设置对应的标志
                    if (av != &amp;main_arena)
                        set_non_main_arena (tc_victim);
                    //取出最后一个Chunk
                    bin-&gt;bk = bck;
                    bck-&gt;fd = bin;
                    //将其放入到Tcache中
                    tcache_put (tc_victim, tc_idx);
                `}`
            `}`
        `}`
#endif</pre>
此处我们发现了一个很关键的情况！我们在此处没有经过`House of Lore`中必须经过的检查：
<pre class="md-fences md-end-block ty-contain-cm modeLoaded" style="box-sizing: border-box; overflow: visible; font-family: var(--monospace); font-size: 0.9em; display: block; break-inside: avoid; text-align: left; background-image: inherit; background-position: inherit; background-size: inherit; background-repeat: inherit; background-attachment: inherit; background-origin: inherit; background-clip: inherit; background-color: #f8f8f8; border-radius: 3px; padding: 8px 4px 6px; margin-bottom: 15px; margin-top: 15px; width: inherit; color: #333333; border: 1px solid #e7eaed;" spellcheck="false">// 检查 bck-&gt;fd 是不是 victim，防止伪造
if ( __glibc_unlikely( bck-&gt;fd != victim ) )
    malloc_printerr ("malloc(): smallbin double linked list corrupted");</pre>
但是此处又有了矛盾的地方！
**首先，在引入Tcache后，Tcache中的Chunk拥有绝对优先权，我们不能越过Tcache向SmallBin中填入Chunk，也不能越过Tcache从SmallBin中取出Chunk。（除非Tcache已经处于FULL状态）**
然后，我们如果要在这里启动攻击，那么要求`SmallBin`中至少有两个Chunk(否则无法进入While中的if语句块)，**同时要求Tcache处于非空状态。**
那样就产生了矛盾，导致这个漏洞看似无法利用。
但是`calloc`函数有一个很有趣的特性，它不会从`Tcache`拿`Chunk`，因此可以越过第一条矛盾“不能越过`Tcache`从`SmallBin`中取出`Chunk`”。
然后是`Unsorted Bin`的**`last remainder`**基址，当申请的Chunk大于`Unsorted Bin`中Chunk的大小且其为`Unsorted Bin`中的唯一`Chunk`时，该`Chunk`不会进入`Tcache`。
同时，我们来分析`tcache_put`函数
<pre class="md-fences md-end-block ty-contain-cm modeLoaded" style="box-sizing: border-box; overflow: visible; font-family: var(--monospace); font-size: 0.9em; display: block; break-inside: avoid; text-align: left; background-image: inherit; background-position: inherit; background-size: inherit; background-repeat: inherit; background-attachment: inherit; background-origin: inherit; background-clip: inherit; background-color: #f8f8f8; border-radius: 3px; padding: 8px 4px 6px; margin-bottom: 15px; margin-top: 15px; width: inherit; color: #333333; border: 1px solid #e7eaed;" spellcheck="false">static __always_inline void tcache_put (mchunkptr chunk, size_t tc_idx)
`{`
  tcache_entry *e = (tcache_entry *) chunk2mem (chunk);
  assert (tc_idx &lt; TCACHE_MAX_BINS);
​
  /* Mark this chunk as "in the tcache" so the test in _int_free will
     detect a double free.  */
  e-&gt;key = tcache;
​
  e-&gt;next = tcache-&gt;entries[tc_idx];
  tcache-&gt;entries[tc_idx] = e;
  ++(tcache-&gt;counts[tc_idx]);
`}`</pre>
可以发现，`tcache_put`函数没有做任何的安全检查。
那么，当Tcache存在两个以上的空位时，程序会将我们的fake chunk置入Tcache。
 
<h2 name="h2-4" id="h2-4">0x02 以BUUOJ-2020 新春红包题-3为例</h2>
<h3 name="h3-5" id="h3-5">题目分析</h3>
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-01-132130.png)
除了Canary保护外，保护全部开启。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-01-132240.png)
题目很明显，**在free后没有将指针置零，存在Use-After-Free漏洞**，并且因为程序开启了Edit功能和Show功能，导致漏洞十分严重。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-01-132739.png)
题目在分配`Chunk`时规定了大小，因此限制了我们对于`Large Bin Attack`的使用。
另外题目的分配函数使用了`calloc()`，`calloc()`会在申请`Chunk`后对其内部进行清零操作，并且`calloc()`不会从`Tcache Bin`中取出堆块，那么我们直接将`Tcache Bin`填满就可以进行正常利用了。
程序在最后预留了后门函数，以供我们执行ROP链。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-01-133018.png)
但是后门的启用需要满足三个条件
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-01-133236.png)
而`Back_door_heck`变量是一个大小为0x1000的Chunk。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-01-133351.png)
<a class="reference-link" name="Tcache%20Bin%E7%9A%84%E5%A1%AB%E5%85%85"></a>
<h3 name="h3-6" id="h3-6">Tcache Bin的填充</h3>
首先，需要循环释放7个Chunk到Tcache Bin区域以填满Tcache以防止其干扰我们后续的利用。
<pre class="md-fences md-end-block ty-contain-cm modeLoaded" style="box-sizing: border-box; overflow: visible; font-family: var(--monospace); font-size: 0.9em; display: block; break-inside: avoid; text-align: left; background-image: inherit; background-position: inherit; background-size: inherit; background-repeat: inherit; background-attachment: inherit; background-origin: inherit; background-clip: inherit; background-color: #f8f8f8; border-radius: 3px; padding: 8px 4px 6px; margin-bottom: 15px; margin-top: 15px; width: inherit; color: #333333; border: 1px solid #e7eaed;" spellcheck="false">for i in range(7):
    creat(sh,15,4,'Chunk_15')
    delete(sh,15)</pre>
**同时为了之后我们使用`Tcache Stashing Unlink Attack`，我们需要先向0x100大小的Tcache Bin释放6个Chunk，这样，在将我们伪造的Fake_chunk放入Tcache Bin区域时，Tcache Bin区域将会填满，程序不会继续通过我们伪造的bk指针向后继续遍历。**
<pre class="md-fences md-end-block ty-contain-cm modeLoaded" style="box-sizing: border-box; overflow: visible; font-family: var(--monospace); font-size: 0.9em; display: block; break-inside: avoid; text-align: left; background-image: inherit; background-position: inherit; background-size: inherit; background-repeat: inherit; background-attachment: inherit; background-origin: inherit; background-clip: inherit; background-color: #f8f8f8; border-radius: 3px; padding: 8px 4px 6px; margin-bottom: 15px; margin-top: 15px; width: inherit; color: #333333; border: 1px solid #e7eaed;" spellcheck="false">for i in range(6):
    creat(sh,14,2,'Chunk_14')
    delete(sh,14)</pre>
 
<h3 name="h3-7" id="h3-7">泄露Heap地址及Libc地址</h3>
因为UAF漏洞的存在，我们只需要打印已经释放过的Tcache即可计算出Heap区域的首地址。
<pre class="md-fences md-end-block ty-contain-cm modeLoaded" style="box-sizing: border-box; overflow: visible; font-family: var(--monospace); font-size: 0.9em; display: block; break-inside: avoid; text-align: left; background-image: inherit; background-position: inherit; background-size: inherit; background-repeat: inherit; background-attachment: inherit; background-origin: inherit; background-clip: inherit; background-color: #f8f8f8; border-radius: 3px; padding: 8px 4px 6px; margin-bottom: 15px; margin-top: 15px; width: inherit; color: #333333; border: 1px solid #e7eaed;" spellcheck="false">show(sh,15)
last_chunk_addr = get_address(sh,'We get last chunk address is ','','\x0A')
heap_addr = last_chunk_addr - 0x26C0
log.success('We get heap address is ' + str(hex(heap_addr)))</pre>
接下来继续分配一个`0x300`大小的Chunk，释放后它将进入`Unsorted Bin`,此时打印它的内容，将泄漏`Libc`基址。
⚠️：为防止`Top Chunk`合并，需要在最后额外申请一个Chunk。
<pre class="md-fences md-end-block ty-contain-cm modeLoaded" style="box-sizing: border-box; overflow: visible; font-family: var(--monospace); font-size: 0.9em; display: block; break-inside: avoid; text-align: left; background-image: inherit; background-position: inherit; background-size: inherit; background-repeat: inherit; background-attachment: inherit; background-origin: inherit; background-clip: inherit; background-color: #f8f8f8; border-radius: 3px; padding: 8px 4px 6px; margin-bottom: 15px; margin-top: 15px; width: inherit; color: #333333; border: 1px solid #e7eaed;" spellcheck="false">creat(sh,1,4,'Chunk_1')
creat(sh,13,3,'Chunk_13')
delete(sh,1)
show(sh,1)
libc_base = get_address(sh,'We leak main arena address is ','','\x0A') - 0x1E4CA0
log.success('We get libc base address is ' + str(hex(libc_base)))</pre>
 
<h3 name="h3-8" id="h3-8">向Small Bin中加入两个Chunk</h3>
此时在`Unsorted Bin`中已经有一个0x410大小的Chunk了，现在我们申请两个0x300大小的Chunk，程序会将0x100大小的Chunk放入`Small Bin`中。
<pre class="md-fences md-end-block ty-contain-cm modeLoaded" style="box-sizing: border-box; overflow: visible; font-family: var(--monospace); font-size: 0.9em; display: block; break-inside: avoid; text-align: left; background-image: inherit; background-position: inherit; background-size: inherit; background-repeat: inherit; background-attachment: inherit; background-origin: inherit; background-clip: inherit; background-color: #f8f8f8; border-radius: 3px; padding: 8px 4px 6px; margin-bottom: 15px; margin-top: 15px; width: inherit; color: #333333; border: 1px solid #e7eaed;" spellcheck="false">creat(sh,13,3,'Chunk_13')
creat(sh,13,3,'Chunk_13')<code class="lang-python hljs">
```
<li class="md-list-item" style="box-sizing: border-box; margin: 0px; position: relative;">
向任意指定位置写入指定值。
</li>
<li class="md-list-item" style="box-sizing: border-box; margin: 0px; position: relative;">
向任意地址分配一个Chunk。
</li>
#### 攻击前提

### 题目分析

### 泄露Heap地址及Libc地址

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-02-123511.png)

然后我们再次申请一个0x400的Chunk，释放，再申请一个0x300的Chunk，在Small Bin中再次加入一个大小为0x100的`Chunk`。

⚠️：为防止`Top Chunk`合并，需要在最后额外申请一个Chunk。

```
creat(sh,2,4,'Chunk_2')
creat(sh,13,4,'Chunk_13')
delete(sh,2)
creat(sh,13,3,'Chunk_13')
creat(sh,13,3,'Chunk_13')
```

[![](https://img.lhyerror404.cn/error404/2020-02-02-123610.png)](https://img.lhyerror404.cn/error404/2020-02-02-123610.png)

### <a class="reference-link" name="%E6%89%A7%E8%A1%8C%20Tcache%20Stashing%20Unlink%20Attack"></a>

### 执行 Tcache Stashing Unlink Attack<a class="reference-link" name="%E6%89%A7%E8%A1%8C%20Tcache%20Stashing%20Unlink%20Attack"></a>

现在SmallBin中的情况为：<a class="reference-link" name="%E6%89%A7%E8%A1%8C%20Tcache%20Stashing%20Unlink%20Attack"></a>

那么我们接下来若申请一个大小为`0xF0`的`Chunk`，程序仅会检查`Chunk2`的`fd`指针是否指向`Chunk1`。<a class="reference-link" name="%E6%89%A7%E8%A1%8C%20Tcache%20Stashing%20Unlink%20Attack"></a>

在取出Chunk1后，**因为0x100的Tcache Bin还有1个空位，程序会遍历发现Chunk2满足大小条件并将其放入Tcache Bin中！**<a class="reference-link" name="%E6%89%A7%E8%A1%8C%20Tcache%20Stashing%20Unlink%20Attack"></a>

我们若此时篡改`Chunk2`的`bk`指针指向`heap_addr+0x250+0x10+0x800-0x10`，程序就会在`heap_addr+0x250+0x10+0x800`的位置写入`main_arena`的地址，进而可以让我们进入后门函数。<a class="reference-link" name="%E6%89%A7%E8%A1%8C%20Tcache%20Stashing%20Unlink%20Attack"></a>

触发攻击<a class="reference-link" name="%E6%89%A7%E8%A1%8C%20Tcache%20Stashing%20Unlink%20Attack"></a>

### <a class="reference-link" name="%E6%89%A7%E8%A1%8C%20Tcache%20Stashing%20Unlink%20Attack"></a>

### 构造ROP链<a class="reference-link" name="%E6%89%A7%E8%A1%8C%20Tcache%20Stashing%20Unlink%20Attack"></a>

经过检测，发现程序开启了SandBox。<a class="reference-link" name="%E6%89%A7%E8%A1%8C%20Tcache%20Stashing%20Unlink%20Attack"></a>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-05-083749.png)

那么我们采取`Open-Read-Write`的利用方式。

⚠️：Read函数的第一个参数文件描述符从0开始累加，程序进行时内核会自动打开3个文件描述符，0，1，2，分别对应，标准输入、输出和出错，这样在程序中，每打开一个文件，文件描述符值从3开始累加。

因为我们无法获取PIE的值，于是选择从libc中寻找gadget。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-02-05-093304.png)

至此，我们可以顺利的构造ROP链。

### Final Exploit



## 0x04 以2020-XCTF-高校战疫赛 two_chunk为例

### 题目分析

[![](https://p0.ssl.qhimg.com/t01f2b2d8651a6e1953.png)](https://p0.ssl.qhimg.com/t01f2b2d8651a6e1953.png)

程序使用了2.30的Libc，但是本题的相关利用与2.30新增的保护机制无关，因此我们使用libc2.29完成利用。

[![](https://p0.ssl.qhimg.com/t01186b134ab312e021.png)](https://p0.ssl.qhimg.com/t01186b134ab312e021.png)

保护全部开启。

程序使用`Calloc`进行`Chunk`的分配，编辑函数仅能编辑一次，且编辑时可以溢出0x20字节。



### 向Small Bin中加入两个Chunk

首先`Creat(sh,0,0x188)`然后再`Creat(sh,1,0x300)`，这个`0x300`大小的`Chunk`是为了防止`Chunk`被`Top Chunk`合并，这里我们将这个`Chunk`视为`Chunk 2`。堆内存情况如下：

紧接着释放`Chunk 0`，这个`Chunk`会被加入`Unsorted Bin`，再`Creat(sh,0,0xF0)`，程序会从`Chunk 0`中切割走`0x100`大小，这里我们将剩余的大小视为`Chunk 1`。堆内存情况如下：

之后我们释放`Chunk 0`,再次`Creat(sh,0,0x100)`，`Chunk 1`会被加入`Small Bin`。然后我们释放`Chunk 0`、`Chunk 1`。堆内存情况如下：

之后我们`Creat(sh,0,0x188)`然后再`Creat(sh,1,0x300)`，这个`0x300`大小的`Chunk`是为了防止`Chunk`被`Top Chunk`合并，这里我们将这个`Chunk`视为`Chunk 6`。堆内存情况如下：

紧接着释放`Chunk 4`，这个`Chunk`会被加入`Unsorted Bin`，再`Creat(sh,0,0xF0)`，程序会从`Chunk 4`中切割走`0x100`大小，这里我们将剩余的大小视为`Chunk 5`。堆内存情况如下：

之后我们释放`Chunk 6`,再次`Creat(sh,0,0x100)`，`Chunk 5`会被加入`Small Bin`。堆内存情况如下：

⚠️：此处我们不使用释放`Chunk 4`的原因是，此时`Chunk 0`恰好指向`Chunk 4`，而`edit`存在一个溢出写，那么我们就可以篡改`Chunk5`的`Size`域了。

至此，我们向`Small Bin`中加入了两个`0x90`大小的Chunk。



### 执行 Tcache Stashing Unlink Attack

现在SmallBin中的情况为：

那么我们接下来若申请一个大小为`0x88`的`Chunk`，程序仅会检查`Chunk5`的`fd`指针是否指向`Chunk1`。

在取出`Chunk 1`后，**因为0x90的Tcache Bin还有2个空位，程序会首先遍历发现Chunk5满足大小条件并将其作为参数调用`tcache_put`。**

若此时，我们篡改了`Chunk 5`的`bk`指针为`Fake_Chunk`的地址(假设为0x12345678)，那么程序接下来会将`Small bin`的`bk`指针置为`0x12345678`，并且在`0x12345678 -&gt; fd`的位置写入`bin`的地址，也就是`main_arena`的地址。接下来，由于**因为0x90的Tcache Bin仍有1个空位，程序会发现`Fake_Chunk`满足大小条件并将其作为参数调用`tcache_put`。**

此时！程序就会将我们的`Fake_Chunk`也置入`Tcache Bin`，我们只要能将其从`Tcache Bin`取回，就可以做任意地址写了。

⚠️：此处我们仍要注意一点，在将`Fake_Chunk`也置入`Tcache Bin`之前，程序会将`bin`的地址，也就是`main_arena`的地址写入`Fake_Chunk-&gt;bk-&gt;fd`的位置，这里我们一定要确保`Fake_Chunk-&gt;bk-&gt;fd`是可写的！那么此处我们使用我们索性将buf的前部统一置为buf的位置+0x20。

那么我们对`Chunk 4`进行edit操作，注意，此处的`Chunk 4`的`index`为0。这里我们选择将chunk分配到buf的位置，以便我们能执行任意命令。

[![](https://p0.ssl.qhimg.com/t01e93759bd8b5c586c.png)](https://p0.ssl.qhimg.com/t01e93759bd8b5c586c.png)

[![](https://p4.ssl.qhimg.com/t0155fb1f2d9c6ccc6d.png)](https://p4.ssl.qhimg.com/t0155fb1f2d9c6ccc6d.png)

接下来我们使用`Leave_end_message`功能即可取回`Fake_chunk`。



### 泄露Libc Address &amp; 获取Shell

首先我们先泄露Libc地址，还记得之前说过的吗，在将`Fake_Chunk`也置入`Tcache Bin`之前，程序会将`bin`的地址，也就是`main_arena`的地址写入`Fake_Chunk-&gt;bk-&gt;fd`的位置，我们已经将`Fake_Chunk-&gt;bk`篡改为了`buf的位置+0x20`,此时，`Fake_Chunk-&gt;bk-&gt;fd`恰好为`buf的位置+0x30`，也就是message的位置！

[![](https://p0.ssl.qhimg.com/t015893e97ba2c474c4.png)](https://p0.ssl.qhimg.com/t015893e97ba2c474c4.png)

那么我们只要使用`Show_name_message`功能即可泄露`main_arena`的地址，进而计算libc基址。

然后我们使用`Leave_end_message`功能取回`Fake_chunk`即可执行任意libc函数。

### Final Exploit



## 0x05 参考链接

[CTF-wiki House of Lore](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/house_of_lore-zh/)

[HITCON CTF 2019 Quals — One Punch Man – berming](https://medium.com/@ktecv2000/hitcon-ctf-2019-quals-one-punch-man-pwn-292pts-3e94eb3fd312)
