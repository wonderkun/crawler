> 原文链接: https://www.anquanke.com//post/id/87194 


# 【技术分享】CTF中带来的IO_FILE新思路


                                阅读量   
                                **272269**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            





[![](https://p1.ssl.qhimg.com/t015aa6f888222001d5.jpg)](https://p1.ssl.qhimg.com/t015aa6f888222001d5.jpg)

作者：[FlappyPi](http://bobao.360.cn/member/contribute?uid=1184812799)g

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

之前一直打算写一份有关**IO_FILE**的文章，但是由于自己太忙，所以一直都没有写。最初接触到IO_FILE是在pwnable.tw网站上做题时，碰到的题目能够通过对stdin进行伪造的话，能够把伪造虚表的地址以及虚表中的函数。从而造成任意代码执行。

之后再次遇见IO_FILE的时候是在2016的hitcon上面的house of orange，这个题目将IO_FILE和堆中的**unsorted bin attack**结合了起来。通过unsorted bin attack修改了IO_list_all，在flush io的时候造成了任意代码的执行。这样的攻击方法都是通过伪造IO_FILE的结构体，修改虚表的位置来利用的。

但是之后，由于ubuntu17.04的发布，libc-2.24.so中增加了对vtable的check，所以之前通过修改虚表来进行漏洞利用的方法现在已经用不了了。

**<br>**

**新的思路**

之后在参加WCTF 2016的时候，hitcon给出了challenge wannaheap。这个题目当时所有参赛的队伍没有一个做出来。之后在赛后分享的时候，根据它们的讲述，才发现这个题目为什么当时没有人解出来……它将IO_FILE的利用带上了一个新的层面。我们下面对这个题目详细分析一下来进一步加深对IO_FILE利用的理解，本文中对wannaheap的解题思路完全是根据当时hitcon在WCTF上分享的来的。

**<br>**

**Wannaheap**

题目的结构体只有两个，chunk和node



```
struct __attribute__((packed)) __attribute__((aligned(4))) node
`{`
  _QWORD left;
  _QWORD right;
  __int64 key;
  __int64 data;
  _DWORD random;
`}`;
struct __attribute__((aligned(8))) chunk
`{`
  _QWORD real_addr;
  _QWORD addr;
`}`;
```

首先它实现了一个前后都有随机数据和随机大小的堆分配结构，这样的话，堆的分配就变得难以预测。

[![](https://p0.ssl.qhimg.com/t016c6da89484ee2048.png)](https://p0.ssl.qhimg.com/t016c6da89484ee2048.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://publish.adlab.corp.qihoo.net:8360/ueditor/themes/default/images/spacer.gif)分配的大小是rand1 + size + rand2，其中size是想要分配的大小。

所以这中间的这个堆块的位置是很难找到的，calloc设置的size大小也是很难控制的。

[![](https://p0.ssl.qhimg.com/t01d370f8e353bacef6.png)](https://p0.ssl.qhimg.com/t01d370f8e353bacef6.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://publish.adlab.corp.qihoo.net:8360/ueditor/themes/default/images/spacer.gif)[![](https://p2.ssl.qhimg.com/t011e6870988eec86d7.png)](https://p2.ssl.qhimg.com/t011e6870988eec86d7.png)

分配的chunk就像上面这样，后面会把这里的地址存到一个global的数组里面去。

chunk的存储方式像是一个存在key值的红黑树，左子树的key值小于根节点，右子树的key值大于根节点。

[![](https://p4.ssl.qhimg.com/t015d491fed20175f38.png)](https://p4.ssl.qhimg.com/t015d491fed20175f38.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://publish.adlab.corp.qihoo.net:8360/ueditor/themes/default/images/spacer.gif)另外还增加了一个random的操作来对树进行rotate，但是这里有点没有弄懂，这样的操作貌似会破坏树的结构…不过这个存储对后面做exploit不是很重要，可以先放在一边。

**<br>**

**vuln**

这个题目存在两个漏洞，第一个漏洞在**set_data_area**这个函数里面，是一个libc任意地址写一个x00的字节，malloc的时候如果size比较大的时候会调用mmap，当malloc的size在0x30000之上的时候就会mmap在libc和bin之间

[![](https://p5.ssl.qhimg.com/t0150b2596c43d5ed19.png)](https://p5.ssl.qhimg.com/t0150b2596c43d5ed19.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://publish.adlab.corp.qihoo.net:8360/ueditor/themes/default/images/spacer.gif)所以之后的g_buf_ptr[len_1] = 0会在libc的任意地址写上x00[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://publish.adlab.corp.qihoo.net:8360/ueditor/themes/default/images/spacer.gif)

[![](https://p4.ssl.qhimg.com/t01c6908a7728468457.png)](https://p4.ssl.qhimg.com/t01c6908a7728468457.png)

另外一个漏洞是在Allocate函数里面，在设置data的时候read了0x18个字节到栈上面，但是栈上面并没有被清干净，所以strdup之后data会被存到Nosql里面去。之后在Read函数里面就可以泄漏这个地址了。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://publish.adlab.corp.qihoo.net:8360/ueditor/themes/default/images/spacer.gif)

[![](https://p2.ssl.qhimg.com/t01993e1d5e3a203ed4.png)](https://p2.ssl.qhimg.com/t01993e1d5e3a203ed4.png)

**<br>**

**利用**

因为只能够往libc里面写一个x00，这就很难去利用了…

但是在ubuntu 17.04里面这个利用是可能的，也只能够在ubuntu 17.04里面进行利用，只有在libc.so.2.14版本中才可以。

首先必须要认识的是stdin这个结构体。

[![](https://p1.ssl.qhimg.com/t01c6065f67161c48e9.png)](https://p1.ssl.qhimg.com/t01c6065f67161c48e9.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://publish.adlab.corp.qihoo.net:8360/ueditor/themes/default/images/spacer.gif)这个结构体里面比较关键的就是IO_read_ptr, IO_read_end, IO_read_base, IO_write_base …这些指针。他们是用来作为输入和输出的缓冲区的。从阅读源码中可以知道。

所以这里我们可以往IO_buf_base的最后一个字节写上x00，这样IO_buf_base就正好指向_IO_buf_end的开头了，但是由于libc-2.24.so中的vtable check，我们无法伪造整个的vtable。

所以之后我们就往下覆盖直到main_arena，其中会经过malloc_hook，可以把malloc_hook覆盖成任意数值，但是这里用了seccomp，所以我们没有办法把它覆盖成onegadget的地址。

往下是main_arena的位置，我们可以覆盖到unsortedbin[1]的地址，覆盖成伪堆块的地址，然后在伪堆块的bk上面写上_dl_open_hook – 0x10的地址来做unsorted bin attack。这样的话unsortedbin attack 之后dl_open_hook的位置就会被写上main_arena + 88的地址，让dl_open_hook指向了main_arena+88。

[![](https://p5.ssl.qhimg.com/t016d1793d7d28d04c6.png)](https://p5.ssl.qhimg.com/t016d1793d7d28d04c6.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://publish.adlab.corp.qihoo.net:8360/ueditor/themes/default/images/spacer.gif)dl_open_hook是一个结构体，这个结构体里面是三个函数的指针，当dl_open_hook不是空的时候会对vtable进行check，然后能够跳到dl_open_hook的dlopen_mode上面，具体什么原因我也不太清楚。

[![](https://p3.ssl.qhimg.com/t0151cb0d800d86eca9.png)](https://p3.ssl.qhimg.com/t0151cb0d800d86eca9.png)

所以这样我们就能够得到执行一次gadget的机会了。但是这里要怎么控制rip跳转到我们的rop上面呢？

通过 mov rdi, rax; call [rax + 0x20];这个gadget就能够控制rdi和rip。

然后通过setcontext+52[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://publish.adlab.corp.qihoo.net:8360/ueditor/themes/default/images/spacer.gif)

[![](https://p3.ssl.qhimg.com/t019b70fe501c42f61f.png)](https://p3.ssl.qhimg.com/t019b70fe501c42f61f.png)

能够控制rsp跳到我们的libc area里面，这样的话就能够继续执行rop了。

这个题目的巧妙之处就在于它利用了libc-2.24.so中_IO_buf_end的偏移最后一个字节是x00。所以这个x00的写入才能够控制整个IO_FILE结构体。

**<br>**

**另一种思路**

在此之后，我在WHCTF 2017的线上赛中出了一道名叫stackoverflow的题目。不过很显然这个题目不会是一个简单的stackoverflow。

这个题目的思路与预期解法都是和wannaheap一样的，通过一个x00字节的任意写，控制整个IO_FILE，然后得到任意代码执行的能了。

但是在比赛之后我审查他们提交的writeup的时候发现AAA的大佬们提供了另外一种不同的思路，同样是由于libc-2.24.so的vtable check的限制，他们给出了另外一种不同的绕过思路。

**<br>**

**_IO_vtable_check到底做了什么**

[https://code.woboq.org/userspace/glibc/libio/vtables.c.html#39](https://code.woboq.org/userspace/glibc/libio/vtables.c.html#39)

主要检查了三种情况，如果这三种情况都不满足的话，那么就说明vtable已经被改变过了。所以之后就会跳到

```
__libc_fatal ("Fatal error: glibc detected an invalid stdio handlen");
```

**<br>**

**how to bypass the _IO_vtable_check**

其实还是利用在



```
int 
_IO_flush_all_lockp(int do_lock)
`{`
  int result = 0;
  struct _IO_FILE *fp;
  int last_stamp;
#ifdef _IO_MTSAFE_IO
  __libc_cleanup_region_start (do_lock, flush_cleanup, NULL);
  if (do_lock)
    _IO_lock_lock (list_all_lock);
#endif
  last_stamp = _IO_list_all_stamp;
  fp = (_IO_FILE *) _IO_list_all;
  while (fp != NULL)
    `{`
      run_fp = fp;
      if (do_lock)
        _IO_flockfile (fp);
      if (((fp-&gt;_mode &lt;= 0 &amp;&amp; fp-&gt;_IO_write_ptr &gt; fp-&gt;_IO_write_base)
#if defined _LIBC || defined _GLIBCPP_USE_WCHAR_T
           || (_IO_vtable_offset (fp) == 0
               &amp;&amp; fp-&gt;_mode &gt; 0 &amp;&amp; (fp-&gt;_wide_data-&gt;_IO_write_ptr
                                    &gt; fp-&gt;_wide_data-&gt;_IO_write_base))
#endif
           )
          &amp;&amp; _IO_OVERFLOW (fp, EOF) == EOF)
        result = EOF;
      if (do_lock)
        _IO_funlockfile (fp);
      run_fp = NULL;
      if (last_stamp != _IO_list_all_stamp)
        `{`
          /* Something was added to the list.  Start all over again.  */
          fp = (_IO_FILE *) _IO_list_all;
          last_stamp = _IO_list_all_stamp;
        `}`
      else
        fp = fp-&gt;_chain;
    `}`
#ifdef _IO_MTSAFE_IO
  if (do_lock)
    _IO_lock_unlock (list_all_lock);
  __libc_cleanup_region_end (0);
#endif
  return result;
`}`
```

中的chain字段，伪造一个file结构体，然后修改chain为这个结构体的地址。之后在调用IO_flush_all_lockp函数的时候，这个结构体就会被调用。

但是因为check了vtables，所以不能够任意提供一个伪造的vtable的地址，但是可以使用io_str_jumps 这个vtable。<br>

正常的IO_FILE_jumps的IO_OVERFLOW就是直接跳到虚表中这个偏移位置的地址

```
#define JUMP1(FUNC, THIS, X1) (_IO_JUMPS_FUNC(THIS)-&gt;FUNC) (THIS, X1)
```

但是在io_str_jumps的虚表中 overflow 对应的处理函数是不一样的，我们可以利用这里不一样的地方直接执行system('/bin/sh')

[https://code.woboq.org/userspace/glibc/libio/strops.c.html#81](https://code.woboq.org/userspace/glibc/libio/strops.c.html#81)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://publish.adlab.corp.qihoo.net:8360/ueditor/themes/default/images/spacer.gif)

[![](https://p0.ssl.qhimg.com/t016d8dd4c860f4356e.png)](https://p0.ssl.qhimg.com/t016d8dd4c860f4356e.png)

最终通过

```
(*((_IO_strfile *) fp)-&gt;_s._allocate_buffer) (new_size);
```

跳到system('/bin/sh')上面

**<br>**

**总结**

文章介绍了通过IO_FILE来造成任意代码执行的方法。IO_FILE从开始的没有任何保护，到现在有了对结构体关键位置的check。漏洞的利用方式也开始变的越来越复杂，对利用的要求也会越来越高。不过在我看来，只要能够做到对IO_FILE的改写，就能够做到任意代码执行。

如果文章中有什么说的不对的地方，还请大家多多批评指正。
