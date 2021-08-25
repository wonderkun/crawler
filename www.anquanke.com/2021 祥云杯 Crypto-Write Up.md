> 原文链接: https://www.anquanke.com//post/id/251336 


# 2021 祥云杯 Crypto-Write Up


                                阅读量   
                                **26880**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t012551701b132fd70f.jpg)](https://p1.ssl.qhimg.com/t012551701b132fd70f.jpg)



## 前言

芜湖，这次祥云杯又是神仙打架，密码学一共有四道题，个人觉得最后一道题目有意思一些。



## Random_RSA

```
from Crypto.Util.number import *
import gmpy2
import libnum
import random
import binascii
import os

flag=r'flag`{``}`'

p=getPrime(512)
q=getPrime(512)
e=0x10001
n=p*q
ct=pow(flag,e,n)
print("n="+ n)
print("ct="+ ct)

dp=r''
seeds = []
for i in range(0,len(dp)):
    seeds.append(random.randint(0,10000))

res = [] 
for i in range(0, len(dp)):
    random.seed(seeds[i])
    rands = []
    for j in range(0,4):
        rands.append(random.randint(0,255))

    res.append(ord(dp[i]) ^ rands[i%4])
    del rands[i%4]
    print(str(rands))

print(res) 
print(seeds)
```

题目不长，也意外的简单，值得一提的是题目介绍：**一把梭，好像不行哦**。

然而好像就是一把梭的题目吖，没get到出题人的点喔，而且很奇怪的是，题目用的python2的环境，却直接在给flag字符串做整型pow操作，属实奇怪。

回到题目本身，倒也没有什么好说的，给了seeds，我们利用每个seeds生成四个随机数，用第四个随机数异或res的输出，然后ord一下，就能得到dp的一个数字，最后拼起来就能获得dp了。至于已知e,n,dp三个参数解密c获得明文，这里就不再赘述了，**一把梭**的事。

```
from Crypto.Util.number import *
import gmpy2

import random
import binascii
import os


seeds=[...]
dps=[]
res = [...]

for i in range(0, len(res)):
    random.seed(seeds[i])
    rands = []
    for j in range(0,4):
        rands.append(random.randint(0,255))
    dps.append(res[i]^rands[i%4])


dp = int(''.join(chr(i) for i in dps))
n=...
ct=...
e=0x10001

def rsa_nedp(n,e,dp):
    for i in range(1,e):
        if (dp*e-1)%i == 0:
            if n%(((dp*e-1)/i)+1)==0:
                p=((dp*e-1)/i)+1
                q=n/(((dp*e-1)/i))+1
                return p,q

p,q = rsa_nedp(n,e,dp)
d = inverse(e,p-1)
print(long_to_bytes(pow(ct,d,p)))
```

最后这里解密flag直接用p了，（单纯懒，少写一个字符是一个字符了）



## Guess

```
from Crypto.Util.number import (
    bytes_to_long,
    getPrime,
    long_to_bytes,
    getRandomNBitInteger,
)
import random
import hashlib
from math import gcd
import socketserver


KEYSIZE = 512
WELCOME = "welcome to my funny challenge !!! Can you guess right 32 times in a row? "
String = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz"

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

def lcm(a,b):
    return a*b // gcd(a,b)

def proof_of_work():
    STR = "".join([String[random.randint(0, len(String) - 1)] for _ in range(16)])
    HASH = hashlib.sha256(STR.encode()).hexdigest()
    return STR[:4], STR[4:], HASH


def keygen():
    # part 1
    p, q = getPrime(KEYSIZE), getPrime(KEYSIZE)
    n = p * q
    g = n + 1
    LAMBDA = lcm(p - 1, q - 1)

    # part 2
    _key = open("key", "r").read()
    key = []
    for i in _key.split("\n"):
        for j in i[1:-1].split(" "):
            if int(j) not in key:
                key.append(int(j))
    assert len(key) == 80
    #assert key[0] == 119 and key[1] ==  241 and key[2] ==  718 and key[3] == 647
    return n, g, LAMBDA, key


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


class server(socketserver.BaseRequestHandler):
    def _recv(self):
        data = self.request.recv(1024)
        return data.strip()

    def _send(self, msg, newline=True):
        if isinstance(msg, bytes):
            msg += b"\n"
        else:
            msg += "\n"
            msg = msg.encode()
        self.request.sendall(msg)

    def handle(self):
        # print("Service start.")
        # START, END, HASH = proof_of_work()
        # self._send("SHA-256(?+`{``}`) == `{``}`".format(END, HASH))
        # RCV = self._recv().decode()
        # if RCV != START:
        #     return
        # flag = open("flag", "rb").read()
        # self._send(WELCOME)
        # step 1. keygen
        for _ in range(32):
            self._send("round " + str(_+1))
            n, g, LAM, KEY = keygen()
            self._send("Step 1 - KeyGen. This is my public key.")
            self._send("n = " + str(n))
            self._send("g = " + str(g))
            # step 2. Phase 1
            self._send(
                "Step 2 - Phase 1. Now, you can give me one ciphertexts,I will return the corresponding plaintext."
            )

            self._send("Please give me one decimal ciphertext.")
            cipher = int(self._recv().decode())
            print(cipher)
            plaintext = str(dec(n, g, LAM, cipher))
            self._send("This is the corresponding plaintext.")
            self._send(plaintext)

            # step 3. challenge
            self._send(
                "Step 3 - Challenge. Now, you must give me two decimal plaintexts(m0,m1), I will encry them and return a ciphertext randomly"
            )
            self._send("Give me m0.")
            plaintext1 = int(self._recv().decode())
            self._send("Give me m1.")
            plaintext2 = int(self._recv().decode())

            if (
                plaintext1 &lt;= 2
                or plaintext2 &lt;= 2
                or len(bin(plaintext1)) != len(bin(plaintext2))
            ):
                return
            R = 2 * random.randint(0, 39)
            I = random.randint(0, 1)
            cipher1 = enc(n, g, plaintext1 * plaintext2 * KEY[R])
            cipher2 = enc(n, g, plaintext1 * plaintext2 * KEY[R + 1])
            self._send("This is a ciphertext.")
            self._send(str([cipher1, cipher2][I]))

            # step 4. Phase 2

            self._send(
                "Step 4 - Phase 2. Now, you can give me some ciphertexts,I will return the corresponding plaintext.But you can not give me the ciphertext that I give you in step 3."
            )
            self._send("Please give me one decimal ciphertext ")
            cipher = int(self._recv().decode())
            plaintext = str(dec(n, g, LAM, cipher))
            if int(plaintext) == plaintext1 * plaintext2 * KEY[R] or int(plaintext) == plaintext1 * plaintext2 * KEY[R+1]:
                print(plaintext)
                return
            self._send("This is the corresponding plaintext.")
            self._send(plaintext)

            # step.5 Guess
            self._send(
                "Step 5 - Guess. You must tell me which ciphertext was I give you in step 3, 0 or 1(m0 -&gt; c0 , m1 -&gt; c1)?"
            )
            Guess = int(self._recv().decode())

            if Guess == I:
                self._send("Good! You are right")
            else:
                self._send("Sorry!")
                return
        self._send(flag)

class ForkedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 10001
    server = ForkedServer((HOST, PORT), server)
    server.allow_reuse_address = True
    server.serve_forever()
```

这道题代码还挺长的，不过并不难看懂。

首先server类上面的是定义的enc和dec，其实就是paillier密码系统，不熟悉的读者可以移步我的这一片[文章](https://www.anquanke.com/post/id/204720)。

然后这道题目不知道是不是非预期了，因为题目给的hint我并没有到。step2的交互我也没有利用。（太奇怪了，预期该是啥样呢）

由于题目用的pailliar密码系统，具有同态（竟然说不上是乘法同态还是加法同态，只能说两个明文之和的密文，是两个明文分别的密文之积）

我们看到step4-5

[![](https://p2.ssl.qhimg.com/t01d1f91792b2e3b78a.png)](https://p2.ssl.qhimg.com/t01d1f91792b2e3b78a.png)

题目向我们要两个明文plaintext1和plaintext2，然后加密的内容为

```
cipher1 = enc(n, g, plaintext1 * plaintext2 * KEY[R])
cipher2 = enc(n, g, plaintext1 * plaintext2 * KEY[R + 1])
```

由于plaintext1和plaintext2可控，而两条密文的唯一区别是KEY的内容不一样。然后题目加密后随机返回一条，让我们猜返回的是哪个。

我们可以看到，这加密的明文唯一的区别就是用的是KEY[R]和KEY[R+1]，而R = 2 * random.randint(0, 39)，是一个偶数。

那么这里我们选择“炼丹”：

首先我们可以利用同态获取到实际的KEY：题目在step3发送密文cipher后，在step4会帮我们解密一条数据，但是这条数据不能是服务器加密的那两条密文之一，那么，我们就给他cipher * enc(5)，这样他就会解密后并返回plaintext1 * plaintext2 * KEY[R] + 5 或者 plaintext1 * plaintext2 * KEY[R+1] + 5, 我们再处理一下（不处理问题也不大），减掉5，除掉plaintext1 * plaintext2，就可以获取一个KEY_i 了。

然后我们到step5，我们只知道了一个KEY_i，但是不知道它具体的位置，我们直接发送0，如果返回正确，那么我们知道，这个KEY_i 在偶数位，如果返回错误，服务断掉，那么我们知道，这个KEY_i 在奇数位。那么，由于服务端的KEY序列是固定的，那么我们就开始炼丹咯。

我们构造两个数组，一个存奇数位，一个存偶数位。每次连上去，我们解密得到一个KEY_i，如果这个KEY_i 在我们的数组里，我们就能够直接返回正确答案，如果不在，我们就”炼“，猜对了，放进数组，继续猜，猜错了，放进数组，重新连。（再非不过80次连接）

```
from Crypto.Util.number import (
    bytes_to_long,
    getPrime,
    long_to_bytes,
    getRandomNBitInteger,
)
import random
import hashlib

KEYSIZE = 512
WELCOME = "welcome to my funny challenge !!! Can you guess right 32 times in a row? "
String = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz"
from math import gcd
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

def lcm(a,b):
    return a*b // gcd(a,b)

def proof_of_work():
    STR = "".join([String[random.randint(0, len(String) - 1)] for _ in range(16)])
    HASH = hashlib.sha256(STR.encode()).hexdigest()
    return STR[:4], STR[4:], HASH



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

from pwn import *
from pwnlib.util.iters import mbruteforce
from hashlib import sha256

#context.log_level = 'debug'

def proof_of_work(sh):
    sh.recvuntil("?+")
    suffix = sh.recvuntil(')').decode("utf8")[:-1]
    log.success(suffix)
    sh.recvuntil("== ")
    cipher = sh.recvline().strip().decode("utf8")
    proof = mbruteforce(lambda x: sha256((x + suffix).encode()).hexdigest() ==  cipher, string.ascii_letters + string.digits, length=4, method='fixed')
    sh.sendline(proof)
vanish=[]

#奇
s=[]
#偶
ss=[]


for _ in range(80):
    sh=remote("47.104.85.225","57811")
    proof_of_work(sh)

    while True:
        tmp = sh.recvuntil("n = ")
        n = int(sh.recvuntil("\n")[:-1])
        sh.recvuntil("g = ")
        g = int(sh.recvuntil("\n")[:-1])
        sh.recvuntil("decimal ciphertext.\n")
        sh.sendline("123")
        sh.recvuntil("Give me m0.\n")
        sh.sendline("5")
        sh.recvuntil("Give me m1.\n")
        sh.sendline("5")
        sh.recvuntil("This is a ciphertext.\n")
        c = int(sh.recvuntil("\n")[:-1])
        sh.recvuntil("Please give me one decimal ciphertext \n")
        sh.sendline(str((enc(n,g,5)*c)%(n**2)))
        sh.recvuntil("This is the corresponding plaintext.\n")
        m = (int((sh.recvuntil("\n")[:-1]))-5)//25
        sh.recvuntil("0 or 1(m0 -&gt; c0 , m1 -&gt; c1)?\n")
        if m in s:
            sh.sendline('1')
            tmp = sh.recvuntil("\n")
        elif m in ss:
            sh.sendline('0')
            tmp = sh.recvuntil("\n")
        else:
            sh.sendline('1')
            tmp = sh.recvuntil("\n")
            if b"Good! You are right" in tmp:
                s.append(m)
            elif b"Sorry" in tmp:
                ss.append(m)
                sh.close()
                break
        print(s)
        print(ss)
```



## myRSA

```
# myRSA
from Crypto.Util.number import getPrime,bytes_to_long as b2l
from math import gcd
import hashlib
import random
import socketserver


KEYSIZE = 512
alpha = 2.0314159265358979
WELCOME = 'Welcome to use my better RSA!!!!!!So, what do you want now?'
menu = '1. encry \n2. getflag\n3. exit'
String = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz'

def proof_of_work():
    STR = ''.join([String[random.randint(0,len(String)-1)] for _ in range(16) ])
    HASH = hashlib.sha256(STR.encode()).hexdigest()
    return STR[:4],STR[4:],HASH

def key_gen():
    while True:
        p,q = getPrime(KEYSIZE),getPrime(KEYSIZE)
        e = 0x10001
        if gcd(e,(p-1)*(q-1)):
            break
    key = [getPrime(int(KEYSIZE*alpha)) for _ in range(2)]
    return (p,q,e),key

# encrypto
def encry(message,key,p,q,e):
    k1,k2 = key[0],key[1]
    x = p**2 * (p + 3*q - 1 ) + q**2 * (q + 3*p - 1) 
    y = 2*p*q + p + q
    z = k1 + k2 
    c = pow(b2l(message),e,p*q)
    return x * c + y * c + z


# get flag
def getflag(flag,key,p,q,e):
    return encry(flag,key,p,q,e)



class server(socketserver.BaseRequestHandler):
    def _recv(self):
        data = self.request.recv(1024)
        return data.strip()

    def _send(self, msg, newline=True):
        if isinstance(msg , bytes):
            msg += b'\n'
        else:
            msg += '\n'
            msg = msg.encode()
        self.request.sendall(msg)

    def handle(self):
        START,END,HASH = proof_of_work()
        self._send('SHA-256(?+`{``}`) == `{``}`'.format(END,HASH))
        RCV = self._recv().decode()
        if RCV != START:
            return
        self._send("I'm a CryptoRookie,so my Crypto system take time, please wait a minute XD!")
        (p,q,e),key = key_gen()
        flag  = b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        self._send(WELCOME)
        self._send('This is my public key:\nn = `{``}`\ne = `{``}`'.format(str(p*q),str(e)))
        for _ in range(16):
            self._send(menu)
            COI = int(self._recv().decode())
            if COI == 1 :
                self._send('Give me your message')
                message = self._recv()
                self._send('Your encry message:')
                self._send(str(encry(message,key,p,q,e)))
            elif COI == 2:
                self._send('This is your favourite:\n')
                self._send(str(encry(flag,key,p,q,e)))
            elif COI == 3:
                self._send('Bye~')
                break
class ForkedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 10001
    server = ForkedServer((HOST, PORT), server)
    server.allow_reuse_address = True
    server.serve_forever()
```

这道题，emmm，也是奇怪的加密方式，

```
def encry(message,key,p,q,e):
    k1,k2 = key[0],key[1]
    x = p**2 * (p + 3*q - 1 ) + q**2 * (q + 3*p - 1) 
    y = 2*p*q + p + q
    z = k1 + k2 
    c = pow(b2l(message),e,p*q)
    return x * c + y * c + z
```

题目提供提供十六次交互，它可以帮你加密，但每次加密用的z随机

x * c + y * c + z =( x+y )* c + z

其中( x+y ) = ( p+q )^3 – ( p+q )^2 + ( p+q ) – 4 * n

那么我们发送明文 ’\x01’ 过去，就能得到enc = x + y + z，所以 enc + 4 * n = (p+q)^3 – (p+q)^2 + (p+q) + z

我们可以将其看作关于（p+q）的方程 f(x) ，由于z不知道，没法根据返回值解一个具体的值x。

但是算一下长度，(p+q)^3 有 513 * 3 = 1539 bit，z 才 1024bit左右，相对比较小。那么我们直接不管z，去解方程（这里我是用2分法去逼近的），然后我们可以得到一个大概的值。

有了大概的 x ≈ (p+q)，再利用n，就能得到一个大概的p值，

[![](https://p5.ssl.qhimg.com/t01f43bb53aca2dbee1.png)](https://p5.ssl.qhimg.com/t01f43bb53aca2dbee1.png)

有了大概的p值，我们可以本地起一组数据看看和真正的p值差多少，可以发现就差小几万，那么我们直接一手small_roots恢复p。p，q都恢复了，我们直接交互拿到flag的密文 ( x + y) * pow(flag, e, n) + z

直接整除 (x + y) 得到pow(flag, e, n)，（z太小了，整除就给消没了），后面，rsa解密，得到flag。

P.S.不懂出题人干嘛搞一个genkey浪费时间，有啥必要么，还是说，又又又又又又又又又又又又非预期了？确实没用到16次交互。

```
#交互拿到数据a = x + y + z; c = pow(flag,e,n) * (x + y) + z

from Crypto.Util.number import *

def f(x):
    return x**3 - x**2 + x + 4*n

n = ...
e = 65537

a = ...

c = ...



floor = 0
sky = 2**1041
while floor+1 &lt; sky:
    mid = (floor + sky) // 2
    if f(mid) &lt; a:
        floor = mid
    else:
        sky = mid

import gmpy2 

p_sub_q = gmpy2.iroot(int(mid**2-4*n),int(2))[0]
pw = (mid-p_sub_q)//2

N = n
pbar = pw
ZmodN = Zmod(N)
P.&lt;x&gt; = PolynomialRing(ZmodN)
ff = int(pbar) + x
x0 = ff.small_roots(X=2^40, beta=0.4)[0]
p = int(int(pbar) + x0)
n = int(n)
q = n // p

tmp = f(p+q)
c //= tmp
print(long_to_bytes(pow(c,inverse(e,(p-1)*(q-1)),n)))
```

ok，终于来到最有意思的一题了，也是足足做了我快5个小时（虽然中途思路断了的时候去把XMAN结营赛的密码学赛题AK了下）



## secret_share

```
#! /usr/bin/env python
from libnum import n2s, s2n
from random import getrandbits
from hashlib import sha256
import SocketServer
from secret import flag

p, g = 0xb5655f7c97e8007baaf31716c305cf5950a935d239891c81e671c39b7b5b2544b0198a39fd13fa83830f93afb558321680713d4f6e6d7201d27256567b8f70c3, \
       0x85fd9ae42b57e515b7849b232fcd9575c18131235104d451eeceb991436b646d374086ca751846fdfec1ff7d4e1b9d6812355093a8227742a30361401ccc5577


def h2(m):
    return int(sha256(m).hexdigest(), 16)


def key_gen(nbits):
    s = getrandbits(nbits) % p
    while s.bit_length() &lt; nbits - 2:
        s = getrandbits(nbits) % p
    pk = pow(g, s, p)
    return pk, s


def enc(m, pk):
    m = s2n(m)
    e, v = getrandbits(256), getrandbits(256)
    E, V = pow(g, e, p), pow(g, v, p)
    s = v + e * h2(n2s(E) + n2s(V))
    c = m * pow(pk, e + v, p) % p
    cap = (E, V, s)
    return c, cap


def rk_gen(sk, pki, group=9):
    x, r = getrandbits(512) % p, getrandbits(512) % p
    prefix = n2s(pow(g, x * sk, p)).rjust(64, '\x00')
    encoder = [1, -pow(pki, x * sk, p) % p]
    for i in range(1, group + 1):
        pkj = getrandbits(512)
        new_encoder = [1]
        cur = pow(pkj, x * sk, p)
        for j in range(1, i + 1):
            new_encoder.append((encoder[j] + (-1) * cur * encoder[j - 1]) % p)
        new_encoder.append(encoder[i] * cur * (-1) % p)
        encoder = new_encoder
    encoder[-1] += r
    dd = h2(prefix + n2s(r).rjust(64, '\x00')) | 1
    rk = sk * dd
    return rk, encoder[1:], prefix


def re_enc(rk, cipher):
    c, (E, V, s) = cipher
    E_ = pow(E, rk, p)
    V_ = pow(V, rk, p)
    s_ = s * rk % p
    return c, (E_, V_, s_)


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


class EncHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.request.sendall("Welcome to our netdisk system! Our system store only users' ciphertext\n")
        self.request.sendall("Now you can choose what you wanna do\n")
        self.request.sendall("1. generate your key\n2. start challenge\n2. get the ciphertext")
        pk_of_one_user, sk_of_one_user = key_gen(512)
        cipher = enc(flag, pk_of_one_user)
        pk, sk = key_gen(512)
        while 1:
            mul = 1
            self.request.sendall('Input your choice\n')
            self.request.sendall("choice&gt;")
            choice = self.request.recv(16).strip()
            if choice == '1':
                self.request.sendall('Please take good care of it!\n' + hex(pk) + ',' + hex(sk) + '\n')
            elif choice == '2':
                group_list = [32, 64, 128, 256]
                for group in group_list:
                    m = getrandbits(200)
                    plaintext = n2s(m)
                    cur_cipher = enc(plaintext, pk_of_one_user)
                    rk, encoder, prefix = rk_gen(sk_of_one_user, pk, group=group)
                    mul *= rk
                    mul %= p
                    new_cipher = re_enc(rk, cur_cipher)
                    self.request.sendall('The cipher shared to you\n' + str(new_cipher) + '\n')
                    self.request.sendall('prefix, encoder = ' + str((encoder, prefix.encode('hex'))) + '\n')
                    ans = self.request.recv(1024).strip()
                    if int(ans, 16) != m:
                        exit(1)
                self.request.sendall('You are a clever boy! Now I can share you some other information!\n' + hex(mul) + '\n')
            elif choice == '3':
                self.request.sendall(str(cipher) + '\n')
                exit(1)
            else:
                continue


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 1213
    server = ThreadedTCPServer((HOST, PORT), EncHandler)
    server.serve_forever()
```

还好，也就百来行，代码量不大，

我们以目标驱使，找到获取flag的地方，cipher = enc(flag, pk_of_one_user)

看到这个pk_of_one_user，

```
def key_gen(nbits):
    s = getrandbits(nbits) % p
    while s.bit_length() &lt; nbits - 2:
        s = getrandbits(nbits) % p
    pk = pow(g, s, p)
    return pk, s

pk_of_one_user, sk_of_one_user = key_gen(512)
```

基于离散对数问题的公私钥对 pk ≡ g^`{`sk`}` (mod p)

然乎看到enc的加密方式

```
def enc(m, pk):
    m = s2n(m)
    e, v = getrandbits(256), getrandbits(256)
    E, V = pow(g, e, p), pow(g, v, p)
    s = v + e * h2(n2s(E) + n2s(V))
    c = m * pow(pk, e + v, p) % p
    cap = (E, V, s)
    return c, cap
```

可以化为式子：

[![](https://p3.ssl.qhimg.com/t01d708b7bd22578e1c.png)](https://p3.ssl.qhimg.com/t01d708b7bd22578e1c.png)

那么想获取flag，就要搞到这个私钥sk咯，看看怎么能搞到。

### **第一目标：拿到sk**

可以看到交互提供三个功能，第一个，获取你自己的公私钥对 pk，sk

再看下第三个，返回flag的密文，

然后第二个比较长，核心功能也就在这里了，

```
group_list = [32, 64, 128, 256]
for group in group_list:
    m = getrandbits(200)
    plaintext = n2s(m)
    cur_cipher = enc(plaintext, pk_of_one_user)
    rk, encoder, prefix = rk_gen(sk_of_one_user, pk, group=group)
    mul *= rk
    mul %= p
    new_cipher = re_enc(rk, cur_cipher)
    self.request.sendall('The cipher shared to you\n' + str(new_cipher) + '\n')
    self.request.sendall('prefix, encoder = ' + str((encoder, prefix.encode('hex'))) + '\n')
    ans = self.request.recv(1024).strip()
    if int(ans, 16) != m:
        exit(1)
```

流程描述：

他会生成一个随机数m，

然后它的公钥加密m得到cur_cipher，

然后将它的私钥和我们的公钥放进rk_gen这个函数，会得到 rk, encoder, prefix

然后mul = mul * rk % p，

然后用rk，re_enc这个cur_cipher

然后把re_enc后的密文，encoder, prefix 发送给我们。

然后然我们解密m，对了继续，错了拜拜。

循环四次，都通过返回给你mul。

整理逻辑。如果我们都通过了，就能拿到 mul = rk_1 * sk * rk_2 * sk * rk_3 sk * rk_4 % p

有了这个mul，有啥意义么？这里还看不出来，我们继续往前走先，不过有一个问题很明确，既然出题人就这么布置了，我们当然是需要解密m了。

### **第二目标，解密m**

想要解密m，我们相关信息只有re_enc后的cipher，当前轮次的encoder, prefix

看看这个re_enc

```
def re_enc(rk, cipher):
    c, (E, V, s) = cipher
    E_ = pow(E, rk, p)
    V_ = pow(V, rk, p)
    s_ = s * rk % p
    return c, (E_, V_, s_)
```

可以发现，整个函数都没有操作c，就更新了一下E, V, s

那么更新一下我们手里的信息，

[![](https://p3.ssl.qhimg.com/t019184815196b22996.png)](https://p3.ssl.qhimg.com/t019184815196b22996.png)

就这么多了，我们再去看看返回encoder, prefix 的 rk_gen函数，

```
def rk_gen(sk, pki, group=9):
    x, r = getrandbits(512) % p, getrandbits(512) % p
    prefix = n2s(pow(g, x * sk, p)).rjust(64, '\x00')
    encoder = [1, -pow(pki, x * sk, p) % p]
    for i in range(1, group + 1):
        pkj = getrandbits(512)
        new_encoder = [1]
        cur = pow(pkj, x * sk, p)
        for j in range(1, i + 1):
            new_encoder.append((encoder[j] + (-1) * cur * encoder[j - 1]) % p)
        new_encoder.append(encoder[i] * cur * (-1) % p)
        encoder = new_encoder
    encoder[-1] += r
    dd = h2(prefix + n2s(r).rjust(64, '\x00')) | 1
    rk = sk * dd
    return rk, encoder[1:], prefix
```

先不管其他的，看到最下面，rk = sk * dd

我们回想到 mul = rk_1 * sk * rk_2 * sk * rk_3 sk * rk_4 % p ，

那么可以转化为 mul = sk^4 * dd1 * dd2 * dd3 * dd4 % p ，

有了dd的product，那么我们再在模p下给sk^4开个四次根就能拿到sk了！

而 dd = h2(prefix + n2s(r).rjust(64, ‘\x00’)) | 1，其中prefix已知，所以目标很明确

### <a class="reference-link" name="%E7%AC%AC%E4%B8%89%E7%9B%AE%E6%A0%87%EF%BC%8C%E8%8E%B7%E5%8F%96r"></a>第三目标，获取r

我们能够注意到，返回给我们的encder与r相关， 其中encoder[-1] += r，所以我们需要恢复出原来的encoder，

那就得从头看这个函数了，我们首先看到，prefix = n2s(pow(g, x * sk, p)).rjust(64, ‘\x00’)，其中x是未知随机数，sk是服务端公钥，

然后初始 encoder = [1, -pow(pki, x * sk, p) % p]，**划重点**，需要注意到，这里的pki，用的是再step1中给我们的pk，我们是知道其对应的sk的！我们把自己的sk记为ski，避免搞混，那么式子：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013c85b9523ed2cb29.png)

就只差一个 ski ，而这个ski我们是已知的，所以我们就获得了初始 encoder = [1, -pow(prefix, ski, p) % p]

核心的迭代来了

```
for i in range(1, group + 1):
    pkj = getrandbits(512)
    new_encoder = [1]
    cur = pow(pkj, x * sk, p)
    for j in range(1, i + 1):
        new_encoder.append((encoder[j] + (-1) * cur * encoder[j - 1]) % p)
    new_encoder.append(encoder[i] * cur * (-1) % p)
    encoder = new_encoder
```

cur = pow(pkj, x * sk, p)，pkj是一个随机数，所以cur显然无法直接得到，然后是循环里的 new_encoder.append((encoder[j] + (-1) * cur * encoder[j – 1]) % p)

走出后还来一下 new_encoder.append(encoder[i] * cur * (-1) % p)

这里建议画个美丽的图会稍微清晰一些

[![](https://p5.ssl.qhimg.com/t01148fb16d5d3e296b.png)](https://p5.ssl.qhimg.com/t01148fb16d5d3e296b.png)

可以看到，对于cur2那一行，在我们知道 x 的前提下，我们是能够通过第二项获取到 （cur1 + cur2） 的值的，

在我们知道（cur1 + cur2） 的值的前提下，我们是能够获得第三项中 （cur1 * cur2）的值的。

有了（cur1 * cur2）的值，我们再将他乘以x，我们就获得了encoder最后一项的值了。

芜湖，起飞！（如果觉得就分析这么三轮还不够的化，可以再画第四轮，就很清晰了）

那么我们迎来了处理 encoder的核心解法，基本上可以宣布此题告破了。

我们只需要用题目给的 encoder 和 prefix，进行上述操作

```
encoder,prefix = ...

x = -pow(prefix,sk,p)%p
encoder_i=1
for i in encoder[:-1]:
    encoder_i = (i-encoder_i*x)%p
r = (encoder[-1] - encoder_i*x)%p
```

[![](https://p3.ssl.qhimg.com/t017aff71f6a1d3a0ea.png)](https://p3.ssl.qhimg.com/t017aff71f6a1d3a0ea.png)

```
from pwn import * 

from random import getrandbits
from hashlib import sha256
from Crypto.Util.number import *

def n2s(n):
    return long_to_bytes(n)

def s2n(n):
    return bytes_to_long(n)

def h2(m):
    return int(sha256(m).hexdigest(), 16)


def key_gen(nbits):
    s = getrandbits(nbits) % p
    while s.bit_length() &lt; nbits - 2:
        s = getrandbits(nbits) % p
    pk = pow(g, s, p)
    return pk, s


def enc(m, pk):
    m = s2n(m)
    e, v = getrandbits(256), getrandbits(256)
    E, V = pow(g, e, p), pow(g, v, p)
    s = v + e * h2(n2s(E) + n2s(V))
    c = m * pow(pk, e + v, p) % p
    cap = (E, V, s)
    return c, cap


p, g = ...

#context.log_level = 'debug'
sh = remote("47.104.85.225","62351")
#sh = remote("0.0.0.0","1213")
sh.recvuntil("choice&gt;")
sh.sendline("1")
sh.recvuntil("Please take good care of it!\n")
tmp = sh.recvuntil("\n")[:-1]
#获取自己的pk和sk
pk,sk = eval(tmp)
B=[]
sh.recvuntil("choice&gt;")
sh.sendline("2")
for _ in range(4):
    sh.recvuntil("The cipher shared to you\n")
    tmp = sh.recvuntil("\n")[:-1]

    #获取到 re_enc(m) 后给的 c, (E_, V_, s_)
    c, (E_, V_, s_) = eval(tmp)
    sh.recvuntil("prefix, encoder = ")
    tmp = sh.recvuntil("\n")[:-1]

    #利用 encoder,prefix 获取r，从而得到dd
    encoder,prefix = eval(tmp)
    prefixx = prefix.decode('hex')
    prefix = int(prefix,16)
    x = -pow(prefix,sk,p)%p
    tmp=1
    for i in encoder[:-1]:
        tmp = (i-tmp*x)%p
    r = (encoder[-1] - tmp*x)%p
    prefix = n2s(pow(g, x * sk, p)).rjust(64, '\x00')
    dd = h2(prefixx + n2s(r).rjust(64, '\x00')) | 1
    B.append(dd)
    dd_ = inverse(dd,p-1)

    #有了dd，利用前面得到的c, E_ * V_ 解密m
    m = inverse(pow(E_*V_,dd_,p),p)*c % p
    sh.sendline(hex(m)[2:])

sh.recvuntil("You are a clever boy! Now I can share you some other information!\n")
tmp = sh.recvuntil("\n")[:-1]

#拿着通关后给的mul，待会去开根
mul = eval(tmp)

sh.recvuntil("choice&gt;")
sh.sendline("3")
tmp = sh.recvuntil("\n")[:-1]

#获取flag密文相关的参数
c, (E, V, s) = eval(tmp)

#dd求逆乘以mul，把原来mul里的dd去掉，得到sk^4
for i in B:
    mul = mul * inverse(i,p) % p
sk_4 = mul 

sh.interactive()
```

拿到 sk^4 后要开根，这里我切到sagemath去直接用nth_root了

```
a,b = Mod(sk_4,p).nth_root(4,all=True)

tmp = pow(int(E*V),int(a),int(p))
m = c * inverse_mod(int(tmp),int(p)) % int(p)
print(long_to_bytes(m))

tmp = pow(int(E*V),int(b),int(p))
m = c * inverse_mod(int(tmp),int(p)) % int(p)
print(long_to_bytes(m))

b'flag`{`504d0411-6707-469b-be31-9868200aca95`}`'
b'\x9at\x03O\xbd;.\xb5\x97Tz$t2V\x9b\x92\xa8\x0c.O\x89V\x05\xbf\xb9\x0e\xfb\xfcRC\x8e\x948qB\xee\x92y\x02\xbf|\xf6Sq\x81\xdf;!\xd1\x9fmJ\xfb\x87#\xbb10\xa4t\xfd\xd4\x9a'
```



## 结语

​ 整体来看，这次比赛的题目难度中等叭，第一题一把梭没啥好说的，第二题非预期的炼丹，也还行吧，赛后也没问着hint怎么用，不过第一次交互好像是用来获取lamda的，我直接用同态过check好像也是非预期了。第三题化二元方程为一元，然后二分（哦，求一下导可以知道后面是递增的所以能二分）去求一个大概解，也挺有意思的。不过最喜欢的还是最后一题，初看觉得整个代码的处理流程很冗长，但是一点点去将题目解析，将问题一点点规约下去，这种一点点拨开云雾见天日，守得云开见月明的感觉属实不错，而且难度也刚好在我的level，舒服了。
