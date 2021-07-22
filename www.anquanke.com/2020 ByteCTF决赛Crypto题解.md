> 原文链接: https://www.anquanke.com//post/id/225449 


# 2020 ByteCTF决赛Crypto题解


                                阅读量   
                                **232202**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01fe734e0ef79bfb94.jpg)](https://p3.ssl.qhimg.com/t01fe734e0ef79bfb94.jpg)



bytectf决赛线下crypto赛题质量依然很高，在线下赛中实属难得，在此记录一下比赛时8个小时的做题过程。

## impersonation

Alice：

```
from KeyExchange import KeyExchange
from gmssl import func
from flag import FLAG
import socket
import time
import signal
import sys

sys.stderr = open('/dev/null', 'w')
signal.alarm(5)

n = 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123'
public_key_B = 'e52f035c340267a2ee2c57de87db9acf443d1fb98f0b7abbc55d9f332f4f823e' \
               '0f81e7dde971b1e4d02981fc5741eb30f71bf6bcd0c02b06e5c857eedc58cae5'
G = '32c4ae2c1f1981195f9904466a39c9948fe30bbff2660be1715a4589334c74c7' \
    'bc3736a2f4f6779c59bdcee36b692153d0a9877cc62a474002df32e52139f0a0'
print("Hi, Can you tell me bob's address?")
print("I have a message to tell him.")
try:
    addr = input('&gt;&gt;&gt;').strip()
    ip, port = [x.strip() for x in addr.split(':')]
    port = int(port)
except:
    ip, port = 'bob', 1337

print(f"OK! `{`ip`}`:`{`port`}`, I got it!")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    data = s.recv(1024).strip()
    assert data == b'Hi, Alice?'
except:
    print("Oh noooooo! Where did Bob go?")
    exit()
KE = KeyExchange()
r_str = func.random_hex(len(n))
P_a, T_a = KE.send(r_str)
s.sendall(f'`{`P_a.zfill(128)`}``{`T_a`}`\n'.encode())
time.sleep(0.1)
data = s.recv(1024).strip().decode()
P_b, T_b = data[:128],  data[128:]
if P_b != public_key_B:
    print("Oh noooooo! Fake Bob!")
    exit()
msg = KE.transport(P_b, T_b, FLAG)
s.sendall(f'`{`msg`}`\n'.encode())
time.sleep(0.1)
data = s.recv(1024).strip().decode()
msg = KE.decrypt(data)
if FLAG == msg:
    print("My feelings are transmitted, Bye~")
else:
    print("Oh noooooo! Fake Bob!")
exit()
```

中间人攻击

场景大概是Alice想与Bob通信，可以通过本地起一个socket当服务器，给他自己的ip, port后再连接Bob即可拦截与修改信息，进行中间人攻击。这个场景还是有一定现实意义的，由于网站都有证书，所以Alice作为一个用户往往能够判断对方的公钥正确性，而服务器却不行，而若密钥协商协议实现有问题，则很有可能仍然有安全隐患。

Bob的代码：

```
from KeyExchange import KeyExchange
from gmssl import func
import signal
import sys
sys.stderr = open('/dev/null', 'w')
signal.alarm(5)

n = 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123'
private_key = '????????????????????????????????????????????????????????????????'
public_key = 'e52f035c340267a2ee2c57de87db9acf443d1fb98f0b7abbc55d9f332f4f823e' \
             '0f81e7dde971b1e4d02981fc5741eb30f71bf6bcd0c02b06e5c857eedc58cae5'

KE = KeyExchange(public_key, private_key)
print('Hi, Alice?')
data = input().strip()
P_a, T_a = data[:128],  data[128:]
r_str = func.random_hex(len(n))
P_b, T_b = KE.respond(r_str, P_a, T_a)
print(f'`{`P_b.zfill(128)`}``{`T_b`}`')
data = input().strip()
msg = KE.reencrypt(data)
print(msg)
```

keyexchange

```
from gmssl import func, sm3

sm2p256v1_ecc_table = `{`
    'n': 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123',
    'p': 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF',
    'g': '32c4ae2c1f1981195f9904466a39c9948fe30bbff2660be1715a4589334c74c7' +
         'bc3736a2f4f6779c59bdcee36b692153d0a9877cc62a474002df32e52139f0a0',
    'a': 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC',
    'b': '28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93',
`}`


class KeyExchange(object):
    def __init__(self, public_key=None, private_key=None, ecc_table=None):
        if ecc_table is None:
            ecc_table = sm2p256v1_ecc_table
        self.para_len = len(ecc_table['n'])
        self.ecc_a3 = (int(ecc_table['a'], base=16) +
                       3) % int(ecc_table['p'], base=16)
        self.ecc_table = ecc_table
        self.z = None
        self.sk = None
        self.peer_pk = None
        if public_key and private_key:
            self.public_key = public_key
            self.private_key = private_key
        else:
            self.private_key = func.random_hex(len(ecc_table['n']))
            self.public_key = self._kg(
                int(self.private_key, 16), ecc_table['g'])

    def send(self, r_str):
        r = int(r_str, 16) % int(self.ecc_table['n'], base=16)
        T = self._kg(r, self.ecc_table['g'])
        h = int(self.sm3_hash_str(T), 16) % int(self.ecc_table['n'], base=16)
        self.z = (r + h * int(self.private_key, 16)
                  ) % int(self.ecc_table['n'], base=16)        # z = r + hash(rG) *pri
        return self.public_key, T

    def respond(self, r_str, peer_public_key, peer_T):
        self.peer_pk = peer_public_key
        r = int(r_str, 16) % int(self.ecc_table['n'], base=16)
        T = self._kg(r, self.ecc_table['g'])       # T = rG
        h = int(self.sm3_hash_str(T), 16) % int(self.ecc_table['n'], base=16) # hash(rG)
        #self.z = (r + h * int(self.private_key, 16)
        #          ) % int(self.ecc_table['n'], base=16)
        peer_h = int(self.sm3_hash_str(peer_T), 16) % int(
            self.ecc_table['n'], base=16)
        peer_hP = self._kg(peer_h, self.peer_pk)
        peer_ThP = self._add_point(peer_T, peer_hP)
        peer_ThP = self._convert_jacb_to_nor(peer_ThP)      #(hash * pub + rG)*z 
        #K = self._kg(self.z, peer_ThP)
        self.sk = self.sm3_hash_str(K)
        return self.public_key, T

    def transport(self, peer_public_key, peer_T, flag_bytes):
        self.generate(peer_public_key, peer_T)
        sk_bytes = bytes.fromhex(self.sk)
        return bytes(a ^ b for (a, b) in zip(flag_bytes, sk_bytes)).hex()

    def reencrypt(self, xor_cipher):
        msg = bytes(a ^ b for (a, b) in zip(
            bytes.fromhex(xor_cipher), bytes.fromhex(self.sk)))
        return self.encrypt(msg)

    def generate(self, peer_public_key, peer_T):
        peer_h = int(self.sm3_hash_str(peer_T), 16) % int(
            self.ecc_table['n'], base=16)
        peer_hP = self._kg(peer_h, peer_public_key)
        peer_ThP = self._add_point(peer_T, peer_hP)
        peer_ThP = self._convert_jacb_to_nor(peer_ThP)
        K = self._kg(self.z, peer_ThP)
        self.sk = self.sm3_hash_str(K)
        return None

    def encrypt(self, data):
        msg = data.hex()
        k = func.random_hex(self.para_len)
        C1 = self._kg(int(k, 16), self.ecc_table['g'])   
        xy = self._kg(int(k, 16), self.peer_pk)
        x2 = xy[0:self.para_len]
        y2 = xy[self.para_len:2 * self.para_len]
        ml = len(msg)
        t = sm3.sm3_kdf(xy.encode('utf8'), ml / 2)
        if int(t, 16) == 0:
            return None
        else:
            form = '%%0%dx' % ml
            C2 = form % (int(msg, 16) ^ int(t, 16))
            C3 = sm3.sm3_hash([
                i for i in bytes.fromhex('%s%s%s' % (x2, msg, y2))
            ])
            return '%s%s%s' % (C1, C3, C2)
            # kG , hash , msg ^ hash(xy)
    def decrypt(self, data):
        len_2 = 2 * self.para_len
        len_3 = len_2 + 64
        C1 = data[0:len_2]

        C3 = data[len_2:len_3]
        C2 = data[len_3:]

        xy = self._kg(int(self.private_key, 16), C1)
        x2 = xy[0:self.para_len]
        y2 = xy[self.para_len:len_2]
        cl = len(C2)
        t = sm3.sm3_kdf(xy.encode('utf8'), cl / 2)
        if int(t, 16) == 0:
            return None
        else:
            form = '%%0%dx' % cl
            M = form % (int(C2, 16) ^ int(t, 16))
            u = sm3.sm3_hash([
                i for i in bytes.fromhex('%s%s%s' % (x2, M, y2))
            ])
            if u == C3:
                return bytes.fromhex(M)
            else:
                return None

    def sm3_hash_str(self, msg):
        return sm3.sm3_hash(func.bytes_to_list(msg.encode()))

    def _kg(self, k, Point):
        if (k % int(self.ecc_table['n'], base=16)) == 0:
            return '0' * 128
        Point = '%s%s' % (Point, '1')
        mask_str = '8'
        for i in range(self.para_len - 1):
            mask_str += '0'
        mask = int(mask_str, 16)
        Temp = Point
        flag = False
        for n in range(self.para_len * 4):


            if flag:
                Temp = self._double_point(Temp)
            if (k &amp; mask) != 0:
                if flag:
                    Temp = self._add_point(Temp, Point)
                else:
                    flag = True
                    Temp = Point
            k = k &lt;&lt; 1
        return self._convert_jacb_to_nor(Temp)

    def _double_point(self, Point):
        l = len(Point)
        len_2 = 2 * self.para_len
        if l &lt; self.para_len * 2:
            return None
        else:
            x1 = int(Point[0:self.para_len], 16)
            y1 = int(Point[self.para_len:len_2], 16)
            if l == len_2:
                z1 = 1
            else:
                z1 = int(Point[len_2:], 16)

            T6 = (z1 * z1) % int(self.ecc_table['p'], base=16)
            T2 = (y1 * y1) % int(self.ecc_table['p'], base=16)
            T3 = (x1 + T6) % int(self.ecc_table['p'], base=16)
            T4 = (x1 - T6) % int(self.ecc_table['p'], base=16)
            T1 = (T3 * T4) % int(self.ecc_table['p'], base=16)
            T3 = (y1 * z1) % int(self.ecc_table['p'], base=16)
            T4 = (T2 * 8) % int(self.ecc_table['p'], base=16)
            T5 = (x1 * T4) % int(self.ecc_table['p'], base=16)
            T1 = (T1 * 3) % int(self.ecc_table['p'], base=16)
            T6 = (T6 * T6) % int(self.ecc_table['p'], base=16)
            T6 = (self.ecc_a3 * T6) % int(self.ecc_table['p'], base=16)
            T1 = (T1 + T6) % int(self.ecc_table['p'], base=16)
            z3 = (T3 + T3) % int(self.ecc_table['p'], base=16)
            T3 = (T1 * T1) % int(self.ecc_table['p'], base=16)
            T2 = (T2 * T4) % int(self.ecc_table['p'], base=16)
            x3 = (T3 - T5) % int(self.ecc_table['p'], base=16)

            if (T5 % 2) == 1:
                T4 = (T5 + ((T5 + int(self.ecc_table['p'], base=16)) &gt;&gt; 1) - T3) % int(
                    self.ecc_table['p'], base=16)
            else:
                T4 = (T5 + (T5 &gt;&gt; 1) - T3) % int(self.ecc_table['p'], base=16)

            T1 = (T1 * T4) % int(self.ecc_table['p'], base=16)
            y3 = (T1 - T2) % int(self.ecc_table['p'], base=16)

            form = '%%0%dx' % self.para_len
            form = form * 3
            return form % (x3, y3, z3)

    def _add_point(self, P1, P2):
        if P1 == '0' * 128:
            return '%s%s' % (P2, '1')
        if P2 == '0' * 128:
            return '%s%s' % (P1, '1')
        len_2 = 2 * self.para_len
        l1 = len(P1)
        l2 = len(P2)
        if (l1 &lt; len_2) or (l2 &lt; len_2):
            return None
        else:
            X1 = int(P1[0:self.para_len], 16)
            Y1 = int(P1[self.para_len:len_2], 16)
            if l1 == len_2:
                Z1 = 1
            else:
                Z1 = int(P1[len_2:], 16)
            x2 = int(P2[0:self.para_len], 16)
            y2 = int(P2[self.para_len:len_2], 16)

            T1 = (Z1 * Z1) % int(self.ecc_table['p'], base=16)
            T2 = (y2 * Z1) % int(self.ecc_table['p'], base=16)
            T3 = (x2 * T1) % int(self.ecc_table['p'], base=16)
            T1 = (T1 * T2) % int(self.ecc_table['p'], base=16)
            T2 = (T3 - X1) % int(self.ecc_table['p'], base=16)
            T3 = (T3 + X1) % int(self.ecc_table['p'], base=16)
            T4 = (T2 * T2) % int(self.ecc_table['p'], base=16)
            T1 = (T1 - Y1) % int(self.ecc_table['p'], base=16)
            Z3 = (Z1 * T2) % int(self.ecc_table['p'], base=16)
            T2 = (T2 * T4) % int(self.ecc_table['p'], base=16)
            T3 = (T3 * T4) % int(self.ecc_table['p'], base=16)
            T5 = (T1 * T1) % int(self.ecc_table['p'], base=16)
            T4 = (X1 * T4) % int(self.ecc_table['p'], base=16)
            X3 = (T5 - T3) % int(self.ecc_table['p'], base=16)
            T2 = (Y1 * T2) % int(self.ecc_table['p'], base=16)
            T3 = (T4 - X3) % int(self.ecc_table['p'], base=16)
            T1 = (T1 * T3) % int(self.ecc_table['p'], base=16)
            Y3 = (T1 - T2) % int(self.ecc_table['p'], base=16)

            form = '%%0%dx' % self.para_len
            form = form * 3
            return form % (X3, Y3, Z3)

    def _convert_jacb_to_nor(self, Point):
        len_2 = 2 * self.para_len
        x = int(Point[0:self.para_len], 16)
        y = int(Point[self.para_len:len_2], 16)
        z = int(Point[len_2:], 16)
        z_inv = pow(
            z, int(self.ecc_table['p'], base=16) - 2, int(self.ecc_table['p'], base=16))
        z_invSquar = (z_inv * z_inv) % int(self.ecc_table['p'], base=16)
        z_invQube = (z_invSquar * z_inv) % int(self.ecc_table['p'], base=16)
        x_new = (x * z_invSquar) % int(self.ecc_table['p'], base=16)
        y_new = (y * z_invQube) % int(self.ecc_table['p'], base=16)
        z_new = (z * z_inv) % int(self.ecc_table['p'], base=16)
        if z_new == 1:
            form = '%%0%dx' % self.para_len
            form = form * 2
            return form % (x_new, y_new)
        else:
            return None
```

代码很长，不过大部分是sm2的实现，看关键函数可以得知<br>
KeyExchange是一个类似于ecdh的密钥交换，交换后Alice通过OTP发送flag，Bob再通过Alice的公钥发回。

主要的困难（与教科书最基本的中间人攻击的区别）是Alice知道Bob的公钥，无法给她自己的公钥来实现转发。

而可能的漏洞有三个：
- Bob不知道Alice的公钥
- Alice有对flag的decrypt功能，并且有回显
- Alice与Bob均不对点进行检查
对于第二个漏洞，需要能找到一个改flag一位的地方，是初赛中类似题利用的漏洞。但是这次并没有这样的漏洞，加密时用与一个随机数异或，没办法确定对或者错对应的flag位的值。

因此先考虑第一点与第三点的利用

KeyExchange的流程是

```
Alice -&gt; Bob : hash(ra * G) * AlicePublickey + ra * G
Bob -&gt; Alice : hash(rb * G) * BobPublickey + rb * G
```

接着，他们通过下面过程计算一个共同的点

```
(hash(rb * G) * BobPrivatekey + rb) * (hash(ra * G) * AlicePublickey + ra * G)
= (hash(rb * G) * BobPrivatekey + rb) * (hash(ra * G) * AlicePrivatekey + ra) * G
= (hash(rb * G) * BobPublickey + rb * G) * (hash(ra * G) * AlicePrivatekey + ra)
```

而后续加密用的共享密钥是通过这个点经过SM3得到，两个不同的点得到的密钥之间没有任何关系

因此在消息转发时要让Alice与Bob计算的共享密钥需相同，并且由于Alice的密钥每次更换，若不知道给Bob发送的公钥对应的私钥，也不可能解密成功。

我们可控的点为：
- 给Alice的Bob rb
- 给Bob的Alice ra
- 给Bob的Alice publickey
因为Bob的公钥无法改变，给alice发送的消息只有rb可控，但由于还要进行哈希计算，所以改变rb所得到的值难以控制，因此尝试直接将Bob发送的rb转发，试图通过给Bob的ra与publickey来实现共享密钥计算值相等。<br>
即

```
hash(ra * G) * AlicePublickey + ra * G = hash(R) * Publickey + R
```

（以下为我在比赛时第一时间的想法）

将左边看作一个整体点P

若先任意选取R，则

```
Publickey = (P - R) * invert(hash(R) , n) = xG
```

但无法知道x的值，则最后一步Bob发送的flag无法解密。

若先选取Publickey，几乎没法确定R。

所以想到找低阶点，若Publickey的阶低，则x可以通过爆破得到，同时，也可以通过爆破来确定R。

```
R = P - i * Publickey
```

如果hash(R) % order = i，则能得到满足条件的R。

对于选取的一个低阶点，计算order次，碰撞不成功的概率为(1 – 1/order)^order &lt; 1/e = 0.37

所以大概成功率会大于63%

但SM2使用的曲线安全性很高，阶为素数，无法在这条曲线上找低阶点。

但是Bob并不检查点的合法性，可以寻找不在曲线上的低阶点

寻找方法为将b加一个随机数（可以是1）,计算一个点g的阶，若阶order有小质因子k，则计算(order // k)g 则为想要的k阶点<br>
这样，虽然是两个不在一条曲线上的点运算，但是它也一定能算出一个结果R，只不过这个结果R在第三条曲线上，但这里的R仅仅只用到了这一次，因此不会有其他麻烦。<br>
而Publickey还会用于下面对flag的加密，用不在曲线上的点仍能够实现加密，但是解密时就得不到k* Publickey了。<br>
原本解密时，通过privatekey*C1可以得到加密使用的点，但因为我们的Publickey根本就不是从G得到的，因此无法直接得到加密使用的点。但由于Publickey的阶并不大，k * Publickey的可能值仅有order个，爆破order次，即可从中找到明文。

exp：

```
import socketserver
import os, signal
import threading
import string, binascii
from hashlib import sha256
from Crypto.Util import number
from KeyExchange import KeyExchange
from pwn import *
from gmssl import func, sm3
import string
KE = KeyExchange()
def sm3_hash_str(msg):
    return sm3.sm3_hash(func.bytes_to_list(msg.encode()))

def to_point(x , y):
    return hex(x)[2:].rjust(64 , '0') + hex(y)[2:].rjust(64 , '0')
def to_int(g):
    x = int(g[:64] , 16)
    y = int(g[64:] , 16)
    return x , y
def fu(g):
    x ,y = to_int(g)
    y = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF - y
    return to_point(x , y)
class Task(socketserver.BaseRequestHandler):
    index = 0
    times = 0
    _key = None
    _rand_iter = None

    def _recvall(self):
        data = self.request.recv(1024)
        return data.strip()

    def send(self, msg, newline=True):
        if newline:
            msg += b'\n'
        self.request.sendall(msg)

    def get_target(self,peer_pk , peer_T):
        peer_h = int(sm3_hash_str(peer_T), 16) % int(KE.ecc_table['n'], base=16)
        peer_hP = KE._kg(peer_h, peer_pk)
        peer_ThP = KE._add_point(peer_T, peer_hP)
        peer_ThP = KE._convert_jacb_to_nor(peer_ThP)
        return peer_ThP
    def attack(self, tempg):
        tempx = 108369860142849285519512209608941191631731475365137473063138228543102305365193
        tempy = 17711224374516220167029583974392567739229554851195153447898777402617425143845
        temp = to_point(tempx , tempy)
        for i in range(1783):

            tempc = KE._kg(i , temp)
            tempc = fu(tempc)
            r = KE._convert_jacb_to_nor(KE._add_point(tempg , tempc))
            if int(sm3_hash_str(r), 16) % int(KE.ecc_table['n'], base=16) % 1783 == i:
                if KE._kg(int(sm3_hash_str(r), 16) % int(KE.ecc_table['n'], base=16), temp) != None:
                    rg = KE._convert_jacb_to_nor(KE._add_point(r , KE._kg(int(sm3_hash_str(r), 16) % int(KE.ecc_table['n'], base=16), temp)))
                    break
        assert self.get_target(temp , r) == tempg
        return temp , r
    def decrypt(msg):
        tempx = 108369860142849285519512209608941191631731475365137473063138228543102305365193
        tempy = 17711224374516220167029583974392567739229554851195153447898777402617425143845
        temp = to_point(tempx , tempy)
        len_2 = 64 * 2
        len_3 = len_2 + 64
        C2 = msg[len_3:]
        for k in range(1783):
            xy = KE._kg(k, temp)
            if xy != None:
                x2 = xy[0:64]
                y2 = xy[64:2 * 64]
                ml = len(C2)
                t = sm3.sm3_kdf(xy.encode('utf8'), ml / 2)
                temp = number.long_to_bytes(int(C2 , 16) ^ int(t , 16))
                if temp[0] == ord('B'):
                    print(temp)
    def recv(self, prompt=b''):
        self.send(prompt, newline=False)
        return self._recvall()
    def handle(self):
            self.send(b'Hi, Alice?')
            p = remote('172.16.9.45' , 13334)
            data = self._recvall()
            print('Alice-sl' , data)
            P_a, T_a = data[:128].decode(),  data[128:].decode()
            Alice_THP = self.get_target(P_a , T_a)

            P_sl , T_sl = self.attack(Alice_THP)

            p.recvline()
            p.sendline(P_sl + T_sl)
            print('sl-Bob',P_sl + T_sl)


            temp = p.recvline()[:-1]
            print('Bob-sl',temp)


            self.send(temp)
            print('sl-Alice' , temp)


            msg = self._recvall()
            print('Alice-sl' , msg)

            p.sendline(msg)
            print('sl-Bob' , msg)
            temp = p.recvline()
            print('Bob-sl' , temp)
            self.decrypt(temp)

            self.request.close()
            p.close()

class ForkedServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 1118
    server = ForkedServer((HOST, PORT), Task)
    server.allow_reuse_address = True
    server.serve_forever()
```

但这种思路看着过于眼花缭乱，完全不按题目正常的流程走，比赛时打了一整页草稿才写出来。<br>
但是赛后跟杭电的V师傅交流了一下，发现上面有一步出了问题<br>
当先任意选取R时，

```
Publickey = (P - R) * invert(hash(R) , n) = xG
```

这条式子是否真的无法算出x<br>
最初认为P – R是一个未知的值，但是完全可以取R = P – G<br>
则x = invert(hash(R) , n)<br>
接着直接解密即可。

比赛时总会遇到这种一时想不到的小trick，做题时还是得思考步步谨慎。<br>~~当然会的东西多了也许想不到也不是什么大问题~~



## agid

server.py

```
import agid
import re
from gmssl.optimized_field_elements import FQ2, FQ
'''
def check_auth():
    bob = agid.Verifier()
    identity = bob.allow_identity[0]
    alice = agid.Prover(identity)
    Ppub, Qpub, H = bob.setup()
    Rid = bob.keygen(identity)
    V = bob.gpkgen()
    W = bob.gskgen(identity)
    U1, U2, U3, S1, S2, T1, T2, T3 = alice.commit(Rid, W, Ppub, Qpub, H)
    c = bob.challenge(U1, U2, U3, S1, S2, T1, T2, T3)
    s1, s2, s3, s4 = alice.prove(c)
    assert bob.verify(s1, s2, s3, s4)
check_server()
'''
def safe_eval(data):
    data = data.replace(' ', '').strip()
    if re.match(r"^[0-9,()\[\]]+$", data) is None:
        print('This is just for simpler data transmission,\nPlease do not consider attacking here.')
        exit()
    try:
        # This is just for simpler data transmission, please do not consider attacking here
        return eval(data)
    except:
        print('eval fault.')
    exit()
server = agid.Verifier()
Ppub, Qpub, H = server.setup()
V = server.gpkgen()
print((Ppub, Qpub, H, V))
print("Give me your identity")
identity = input("&gt;&gt;&gt;").strip()
Rid = server.keygen(identity)
W = server.gskgen(identity)
print((Rid, W))
print("Give me U1, U2, U3, S1, S2, T1, T2, T3")
try:
    U1, U2, U3, S1, S2, T1, T2, T3 = [[FQ2(y) if type(y) is list else FQ(y) for y in x] for x in safe_eval(input("&gt;&gt;&gt;"))]
except:
    print('eval error.')
    exit()
c = server.challenge(U1, U2, U3, S1, S2, T1, T2, T3)
print(c)
print("Give me s1, s2, s3, s4")
data = input("&gt;&gt;&gt;")
try:
    s1, s2, s3, s4 = safe_eval(data)
except:
    print('format error.')
    exit()
if server.verify(s1, s2, s3, s4):
    print(FLAG)
else:
    print('NoNoNo...')
```

agid.py

```
from random import SystemRandom, sample
from gmssl import func
from gmssl.sm3 import sm3_hash
from string import ascii_letters, digits
import gmssl.optimized_curve as ec
import gmssl.optimized_pairing as ate
def sm3_hash_str(msg):
    return sm3_hash(func.bytes_to_list(msg.encode()))


class Prover(object):
    def __init__(self, identity):
        Hid_str = sm3_hash_str(identity)
        self.Hid = int(Hid_str, 16)
        self.r1 = None
        self.r2 = None
        self.r3 = None
        self.k1 = None
        self.k2 = None
        self.k3 = None
        self.k4 = None

    def commit(self, Rid, W, Ppub, Qpub, H):
        rand_gen = SystemRandom()
        self.r1 = rand_gen.randrange(ec.curve_order)
        self.r2 = rand_gen.randrange(ec.curve_order)
        self.r3 = rand_gen.randrange(ec.curve_order)
        self.k1 = rand_gen.randrange(ec.curve_order)
        self.k2 = rand_gen.randrange(ec.curve_order)
        self.k3 = rand_gen.randrange(ec.curve_order)
        self.k4 = rand_gen.randrange(ec.curve_order)

        U1_left = ec.multiply(ec.G1, (self.r1 * self.Hid) % ec.curve_order)

        U1_right = ec.multiply(Qpub, self.r1)
        U1 = ec.add(U1_left, U1_right)

        r1_inv = pow(self.r1, ec.curve_order - 2,
                     ec.curve_order) % ec.curve_order
        U2 = ec.multiply(Rid, r1_inv)

        U3_left = ec.multiply(U1, self.r2)
        U3_right = ec.multiply(H, self.r3)
        U3 = ec.add(U3_left, U3_right)

        S1_left = ec.multiply(
            ec.G1, (self.r1 * self.r2 * self.Hid) % ec.curve_order)
        S1_right = ec.multiply(Ppub, (self.r1 * self.r2) % ec.curve_order)
        S1 = ec.add(S1_left, S1_right)

        r12_inv = pow((self.r1 * self.r2) % ec.curve_order,
                      ec.curve_order - 2, ec.curve_order) % ec.curve_order
        S2 = ec.multiply(W, r12_inv)

        T1_left = ec.multiply(ec.G1, self.k1)
        T1_mid = ec.multiply(Qpub, self.k2)
        T1_right = ec.multiply(H, self.k3)
        T1 = ec.add(T1_left, T1_mid)
        T1 = ec.add(T1, T1_right)

        T2_left = ec.multiply(U1, self.k4)
        T2_right = ec.multiply(H, self.k3)
        T2 = ec.add(T2_left, T2_right)

        T3_left = ec.multiply(ec.G1, self.k1)
        T3_right = ec.multiply(Ppub, self.k2)
        T3 = ec.add(T3_left, T3_right)

        return U1, U2, U3, S1, S2, T1, T2, T3

    def prove(self, c):
        s1 = (self.k1 + c * self.r1 * self.r2 * self.Hid) % ec.curve_order
        s2 = (self.k2 + c * self.r1 * self.r2) % ec.curve_order
        s3 = (self.k3 + c * self.r3) % ec.curve_order
        s4 = (self.k4 + c * self.r2) % ec.curve_order
        return s1, s2, s3, s4


class Verifier(object):
    def __init__(self):
        self.s = None
        self.sm = None
        self.u = None
        self.Ppub = None
        self.Qpub = None
        self.H = None
        self.V = None
        self.c = None

        self.U1 = None
        self.U3 = None
        self.S1 = None
        self.T1 = None
        self.T2 = None
        self.T3 = None

        self.allow_identity = [''.join(sample(ascii_letters + digits, 10)) for _ in range(3)]

    def setup(self):
        rand_gen = SystemRandom()
        self.s = rand_gen.randrange(ec.curve_order)
        self.sm = rand_gen.randrange(ec.curve_order)
        self.u = rand_gen.randrange(ec.curve_order)

        self.Ppub = ec.multiply(ec.G1, self.s)
        self.Qpub = ec.multiply(ec.G1, self.sm)

        h = rand_gen.randrange(ec.curve_order)
        self.H = ec.multiply(ec.G1, h)
        return self.Ppub, self.Qpub, self.H

    def keygen(self, identity):
        if not identity in self.allow_identity:
            return None
        Hid_str = sm3_hash_str(identity)
        Hid = int(Hid_str, 16)
        Hidsm_inv = pow(Hid + self.sm, ec.curve_order - 2,
                        ec.curve_order) % ec.curve_order
        Rid = ec.multiply(ec.G2, Hidsm_inv)
        HidQ = ec.multiply(ec.G1, Hid)
        HidQQpub = ec.add(HidQ, self.Qpub)

        left = ate.pairing(Rid, HidQQpub)
        right = ate.pairing(ec.G2, ec.G1)
        assert left == right
        return Rid

    def gpkgen(self):
        Hisu = self.u
        for ids in self.allow_identity:
            H_str = sm3_hash_str(ids)
            Hs = int(H_str, 16) + self.s
            Hisu = (Hisu * Hs) % ec.curve_order
        self.V = ec.multiply(ec.G2, Hisu)
        return self.V

    def gskgen(self, identity):
        if not identity in self.allow_identity:
            return None
        Hid_str = sm3_hash_str(identity)
        Hids = int(Hid_str, 16) + self.s
        Hids_inv = pow(Hids, ec.curve_order - 2,
                       ec.curve_order) % ec.curve_order
        W = ec.multiply(self.V, Hids_inv)
        return W

    def challenge(self, U1, U2, U3, S1, S2, T1, T2, T3):
        self.U1 = U1
        self.U3 = U3
        self.S1 = S1
        self.T1 = T1
        self.T2 = T2
        self.T3 = T3

        eq1_left = ate.pairing(U2, U1)
        eq1_right = ate.pairing(ec.G2, ec.G1)
        assert eq1_left == eq1_right

        eq2_left = ate.pairing(S2, S1)
        eq2_right = ate.pairing(self.V, ec.G1)
        assert eq2_left == eq2_right

        if (eq1_left == eq1_right) and (eq2_left == eq2_right):
            rand_gen = SystemRandom()
            self.c = rand_gen.randrange(ec.curve_order)
            return self.c
        else:
            return None

    def verify(self, s1, s2, s3, s4):
        c_neg = (ec.curve_order - self.c) % ec.curve_order

        T1prime_1 = ec.multiply(ec.G1, s1)
        T1prime_2 = ec.multiply(self.Qpub, s2)
        T1prime_3 = ec.multiply(self.H, s3)
        T1prime_4 = ec.multiply(self.U3, c_neg)
        T1prime_left = ec.add(T1prime_1, T1prime_2)
        T1prime_right = ec.add(T1prime_3, T1prime_4)
        T1prime = ec.add(T1prime_left, T1prime_right)

        assert ec.normalize(T1prime) == ec.normalize(self.T1)

        T2prime_left = ec.multiply(self.U1, s4)
        T2prime_mid = ec.multiply(self.H, s3)
        T2prime_right = ec.multiply(self.U3, c_neg)
        T2prime_buffer = ec.add(T2prime_left, T2prime_mid)
        T2prime = ec.add(T2prime_buffer, T2prime_right)
        assert ec.normalize(T2prime) == ec.normalize(self.T2)

        T3prime_left = ec.multiply(ec.G1, s1)
        T3prime_mid = ec.multiply(self.Ppub, s2)
        T3prime_right = ec.multiply(self.S1, c_neg)
        T3prime_buffer = ec.add(T3prime_left, T3prime_mid)
        T3prime = ec.add(T3prime_buffer, T3prime_right)
        assert ec.normalize(T3prime) == ec.normalize(self.T3)

        if (ec.normalize(T1prime) == ec.normalize(self.T1))\
                and (ec.normalize(T2prime) == ec.normalize(self.T2))\
                and (ec.normalize(T3prime) == ec.normalize(self.T3)):
            return True
        else:
            return False
```

这题就不如上一题巧妙。<br>
题目中用的gmssl并不是pip直接下载的那个，需要去github找另一个<br>
题目是一个认证系统，如果有identity即可多得到两个数据<br>
上面check_auth为正常的认证流程<br>
我们需要做的是没有identity的情况下认证成功

看上去两个文件，200多行，需要给12个变量，满足5个方程。十分复杂。

但实际上全写出来，真的很简单

```
eq1_left = ate.pairing(U2, U1)
eq1_right = ate.pairing(ec.G2, ec.G1)
assert eq1_left == eq1_right
```

虽然有双线性对，一开始还以为需要用到双线性对的性质，但是发现后面并没有限制，可以直接U2 = G2 ， U1 = G1

```
eq2_left = ate.pairing(S2, S1)
eq2_right = ate.pairing(self.V, ec.G1)
assert eq2_left == eq2_right
```

第二个同理，S2 = V ， S1 = G1

下面的则是要求

```
T1 = (s1 + s2*sm + h*s3)G1 - c * U3
T2 = (s3 * h)G1 + s4 * U1 - c * U3 = (s3 * h + s4)G1 - c * U3
T3 = (s1 + s * s2)G1 - c * S1 = (s1 + s * s2 - c)G1
```

由于预先不知道c的值，所以在T的构造里必须把c全消掉。

点为0可能出现一些神秘问题（上一道题是这样的，这题用的函数不一样，也不知道会不会）。但是不为0完全也能构造

首先T3处，s未知，需要用s2 * Qpub 得到 s * s2 * G1，取s1 = c抵消c。s2可任意<br>
因此T3 = s2 * Ppub

T2处方便起见U3 = G1，s3 * h *G1 用 s3 * H得到，同样让s4 = c抵消c，s3可任意<br>
因此T2 = s3 * H

T1处几个参数已固定<br>
T1 = s3 ** H + s2 ** Qpub

然后任意取值即可<br>
exp中任意参数全取了1

```
import gmssl.optimized_curve as ec
import gmssl.optimized_pairing as ate
import agid
import re
from gmssl.optimized_field_elements import FQ2, FQ
from pwn import *
p = remote('172.16.9.45' , 18585)
recv = p.recvline()[:-1]
Ppub , Qpub , H , V = [[FQ2(y) if type(y) is list else FQ(y) for y in x] for x in eval(recv)]
p.recvuntil('&gt;&gt;&gt;')
p.sendline('1')
p.recvuntil('&gt;&gt;&gt;')
U1 = ec.G1
U2 = ec.G2
U3 = ec.G1
S1 = ec.G1
S2 = V
s2 = 1
s3 = 1
T3 = ec.multiply(Ppub , s2)
T2 = ec.multiply(H , s3)
T1 = ec.add(ec.multiply(Qpub , s2) , T2)
temp = (U1,U2,U3,S1,S2,T1,T2,T3)
print(str(temp))
p.sendline(str(temp))
c = int(p.recvline()[:-1])
s1 = c
s4 = c
slist = (s1,s2,s3,s4)
p.sendline(str(slist))
p.interactive()
```



## 总结

两道题都有巨大的代码量，光是看懂整个流程就需要花上很长时间。第一道题的中间人攻击可能更容易看懂，却很难找到攻击点。反而是第二题的认证虽然很简单，但一上来十几个变量加上双线性对让人很难一眼看出程序在干嘛，导致最后反而是中间人攻击的解题人数更多，几乎没有人来做agid。<br>
带着自信，静下心看题，才不会被题目吓住。
