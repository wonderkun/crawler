> 原文链接: https://www.anquanke.com//post/id/231483 


# 浅析SM4中的DFA attack


                                阅读量   
                                **118643**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01e030c199b9626e14.png)](https://p3.ssl.qhimg.com/t01e030c199b9626e14.png)



## 简介

本文将简单介绍一下[SM4](https://zh.wikipedia.org/wiki/SM4)中的[DFA](https://en.wikipedia.org/wiki/Differential_fault_analysis)攻击。



## SM4

SM4是我国采用的一种分组密码标准，由国家密码管理局于2012年3月21日发布，其是国密算法中的一种。与DES和AES算法类似，SM4算法是一种迭代分组密码算法，其分组长度为128bit，密钥长度也为128bit。加密算法与密钥扩展算法均采用32轮非线性迭代结构，以字(32位)为单位进行加密运算，每一次迭代运算均为一轮变换函数F。SM4算法加/解密算法的结构相同，只是使用轮密钥相反，其中解密轮密钥是加密轮密钥的逆序。

SM4中的大概结构如下图所示，有32轮：

[![](https://p0.ssl.qhimg.com/t01e790a0d6ec7f0646.png)](https://p0.ssl.qhimg.com/t01e790a0d6ec7f0646.png)

其中的轮函数F如下图所示：

[![](https://p1.ssl.qhimg.com/t01f468dbf1b0767785.png)](https://p1.ssl.qhimg.com/t01f468dbf1b0767785.png)

S为非线性变换的S-box（单字节），L为线性变换，设L的输入为B，输出为C，则有：

[![](https://p5.ssl.qhimg.com/t016e8e822c9302bae4.png)](https://p5.ssl.qhimg.com/t016e8e822c9302bae4.png)

非线性变换S和线性变换L复合而成的可逆变换称为T，即：

[![](https://p5.ssl.qhimg.com/t0102ef0ac54e241803.png)](https://p5.ssl.qhimg.com/t0102ef0ac54e241803.png)

在最后一轮中，SM4会在后面加一道反序变换R，设R的输入为X，输出为Y，则有：

[![](https://p3.ssl.qhimg.com/t010f76658302a94c72.png)](https://p3.ssl.qhimg.com/t010f76658302a94c72.png)

最后再来看看轮密钥的生成过程，设加密密钥为MK：

[![](https://p1.ssl.qhimg.com/t01f6fed2d45e0ff5d6.png)](https://p1.ssl.qhimg.com/t01f6fed2d45e0ff5d6.png)

轮密钥rk生成方法为：

[![](https://p0.ssl.qhimg.com/t010a5f92b6131d026d.png)](https://p0.ssl.qhimg.com/t010a5f92b6131d026d.png)

其中：

[![](https://p4.ssl.qhimg.com/t01397972fc73bd925d.png)](https://p4.ssl.qhimg.com/t01397972fc73bd925d.png)

T’是将上文中的T中的线性变换L替换为了下面的L’：

[![](https://p3.ssl.qhimg.com/t01dc423ada9e2da333.png)](https://p3.ssl.qhimg.com/t01dc423ada9e2da333.png)

其他的参数（FK，CK）的取值固定，这里不再描述。



## DFA攻击

### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E6%8F%8F%E8%BF%B0"></a>攻击描述

DFA （Differential fault analysis）攻击是一种侧信道攻击的方式。这类攻击通常会将故障注入到密码学算法的某一轮中，并根据正确-错误的密文对来取得对应的差分值，然后再进行差分攻击。本节将简单描述一下SM4中的单字节DFA攻击。

设SM4最开始的输入为X，最后的输出为Y，则有：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f8b842fca27ca047.png)

其中每一轮所产生的输出也会作为下一轮的输入，第i轮的输出表示为：

[![](https://p4.ssl.qhimg.com/t01146ed8f3ded7736e.png)](https://p4.ssl.qhimg.com/t01146ed8f3ded7736e.png)

不难得到：

[![](https://p2.ssl.qhimg.com/t01bd0ddb9ef1cfa4d9.png)](https://p2.ssl.qhimg.com/t01bd0ddb9ef1cfa4d9.png)

假设我们进行故障注入后的某一轮的输入/输出为X’，则：

[![](https://p0.ssl.qhimg.com/t010dea2e42bd8be1b1.png)](https://p0.ssl.qhimg.com/t010dea2e42bd8be1b1.png)

那么我们先来看看针对第32轮的DFA攻击（忽略反序变换R）。

假设我们首先进行了正常的加密，然后再将故障注入到了第32轮中输入的某一个地方，则有：

[![](https://p5.ssl.qhimg.com/t016887b2a26eb6cc51.png)](https://p5.ssl.qhimg.com/t016887b2a26eb6cc51.png)

其中S-box之前的输入差分InputDiff为：

[![](https://p2.ssl.qhimg.com/t01f5816dcf5e3ade29.png)](https://p2.ssl.qhimg.com/t01f5816dcf5e3ade29.png)

输出差分OutputDiff为：

[![](https://p2.ssl.qhimg.com/t01671dd5d7c9fa746f.png)](https://p2.ssl.qhimg.com/t01671dd5d7c9fa746f.png)

由于L是线性变换，所以它并不会影响到差分性质。

那么假设我们注入的是X32的某一个字节，如果我们用红色表示其值不为0的部分，则有：

[![](https://p1.ssl.qhimg.com/t01f4cc6ad85cbab627.png)](https://p1.ssl.qhimg.com/t01f4cc6ad85cbab627.png)

这时候的输入差分InputDiff为：

[![](https://p2.ssl.qhimg.com/t01b43f3c8301160630.png)](https://p2.ssl.qhimg.com/t01b43f3c8301160630.png)

输出差分OutputDiff为：

[![](https://p1.ssl.qhimg.com/t01dd6a693b4d067a55.png)](https://p1.ssl.qhimg.com/t01dd6a693b4d067a55.png)

那么我们就可以利用这一组输入输出差分值来对rk31的某一个字节（设为i）进行遍历求解，即当满足如下条件时rk31正确：

[![](https://p0.ssl.qhimg.com/t015ccc9161fa516995.png)](https://p0.ssl.qhimg.com/t015ccc9161fa516995.png)

由于每个S-box处理一个字节，而我们的差分值也只注入到了一个字节中，所以我们可以很快速地求出rk31的某一个字节。但由于多解的情况，我们需要使用不止一组的输入输出差分值来得到唯一的答案，通常来说两组足以。如果我们注入的是X33或X34的某一字节（或者同时注入X32和X33等等情况），也可以达到相同的效果。但是如果我们注入的是X31的某一个字节，则只是简单地对输出进行了异或，并没有什么用，无法进行攻击。

在求出了rk31的某一个字节后，我们也可以用同样的思路求出rk31的别的字节，并恢复出rk31。之后我们可以利用rk31来解密第32轮的输出并得到第31轮的输出，然后再对第31轮进行相同的攻击即可得到rk30。这样一步一步下去，直到我们获得了四个轮密钥，我们就可以根据轮密钥的生成过程恢复出SM4的加密密钥，这样便攻破了SM4。

当然也可以不用单一字节注入，而是同时注入多个字节，这也是可行和高效的。



## 2020强网杯-fault

题目的主要代码如下：

```
# task.py
from sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
...
    def encrypt1(self, key, pt):
        cipher = CryptSM4()
        cipher.set_key(key, SM4_ENCRYPT)
        ct = cipher.crypt_ecb(pt)
        return ct

    def encrypt2(self, key, pt, r, f, p):
        cipher = CryptSM4()
        cipher.set_key(key, SM4_ENCRYPT)
        ct = cipher.crypt_ecb(pt, r, f, p)
        return ct

    def decrypt(self, key, ct):
        cipher = CryptSM4()
        cipher.set_key(key, SM4_DECRYPT)
        pt = cipher.crypt_ecb(ct)
        return pt

    def handle(self):
        signal.alarm(600)
        try:
            if not self.proof_of_work():
                self.send(b"wrong!")
                self.request.close()

            key = urandom(16)
            self.send(b"your flag is")
            self.send(hexlify(self.encrypt1(key, flag.encode())))
            while True:
                self.send(b"1.encrypt1\n2.encrypt2\n3.decrypt\n")
                choice = self.recv()
                if choice == b'1' or choice == b'encrypt1':
                    self.send(b"your plaintext in hex", False)
                    pt = self.recv(prompt=b":")
                    ct = self.encrypt1(key, unhexlify(pt))
                    self.send(b"your ciphertext in hex:" + hexlify(ct))
                elif choice == b'2' or choice == b'encrypt2':
                    self.send(b"your plaintext in hex", False)
                    pt = self.recv(prompt=b":")
                    self.send(b"give me the value of r f p", False)
                    tmp = self.recv(prompt=b":")
                    r, f, p = tmp.split(b" ")
                    r = int(r) % 0x20
                    f = int(f) % 0xff
                    p = int(p) % 16
                    ct = self.encrypt2(key, unhexlify(pt), r, f, p)
                    self.send(b"your ciphertext in hex:" + hexlify(ct))
                elif choice == b'3' or choice == b'decrypt':
                    self.send(b"your key in hex", False)
                    key = self.recv(prompt=b":")
                    self.send(b"your ciphertext in hex", False)
                    ct = self.recv(prompt=b":")
                    pt = self.decrypt(unhexlify(key), unhexlify(ct))
                    self.send(b"your plaintext in hex:" + hexlify(pt))
                else:
                    self.send(b"choose another command.")
        except:
            pass
...
```

```
# sm4.py
#-*-coding:utf-8-*-
...
from func import xor, rotl, get_uint32_be, put_uint32_be, \
        bytes_to_list, list_to_bytes, padding, unpadding
...
class CryptSM4(object):
...

    def one_round(self, sk, in_put, round=-2, f=0x00, p=None):
        out_put = []
        ulbuf = [0]*36
        ulbuf[0] = get_uint32_be(in_put[0:4])
        ulbuf[1] = get_uint32_be(in_put[4:8])
        ulbuf[2] = get_uint32_be(in_put[8:12])
        ulbuf[3] = get_uint32_be(in_put[12:16])
        for idx in range(32):
            if round == idx+1:
                tmp = []
                tmp += put_uint32_be(ulbuf[idx])
                tmp += put_uint32_be(ulbuf[idx + 1])
                tmp += put_uint32_be(ulbuf[idx + 2])
                tmp += put_uint32_be(ulbuf[idx + 3])
                if p is not None:
                    #print("round",round+1,"f",f,"p",p)
                    tmp[p] ^= f
                ulbuf[idx] = get_uint32_be(tmp[0:4])
                ulbuf[idx + 1] = get_uint32_be(tmp[4:8])
                ulbuf[idx + 2] = get_uint32_be(tmp[8:12])
                ulbuf[idx + 3] = get_uint32_be(tmp[12:16])
                ulbuf[idx + 4] = self._f(ulbuf[idx], ulbuf[idx + 1], ulbuf[idx + 2], ulbuf[idx + 3], sk[idx])
            else:
                ulbuf[idx + 4] = self._f(ulbuf[idx], ulbuf[idx + 1], ulbuf[idx + 2], ulbuf[idx + 3], sk[idx])

        out_put += put_uint32_be(ulbuf[35])
        out_put += put_uint32_be(ulbuf[34])
        out_put += put_uint32_be(ulbuf[33])
        out_put += put_uint32_be(ulbuf[32])
        return out_put

    def crypt_ecb(self, input_data, round=-2, f=0x00, p=None):
        # SM4-ECB block encryption/decryption
        input_data = bytes_to_list(input_data)
        if self.mode == SM4_ENCRYPT:
            input_data = padding(input_data)
        length = len(input_data)
        i = 0
        output_data = []
        while length &gt; 0:
            output_data += self.one_round(self.sk, input_data[i:i+16], round, f, p)
            i += 16
            length -= 16
        if self.mode == SM4_DECRYPT:
            return list_to_bytes(unpadding(output_data))
        return list_to_bytes(output_data)
...
```

在每次连接的时候，服务端会随机生成一个key，并提供给我们用SM4算法和key加密的flag密文，然后我们可以进行三种操作：

第一个是encrypt1，我们可以提供明文，服务端会返回正常的SM4加密的密文

第二个是encrypt2，我们可以提供明文和故障注入的轮数、故障值和字节索引，服务端会返回故障注入后的SM4加密的密文

第三个是decrypt，我们可以提供密文和key，服务端会返回正常的SM4解密的明文

但是由于encrypt2中的r会模一个0x20，所以我们无法将错误注入到第32轮。但是这也没关系，我们可以将错误注入到第31轮来恢复rk31，例如（忽略反序变换R）：

[![](https://p4.ssl.qhimg.com/t01ce1698b1c6d7e89a.png)](https://p4.ssl.qhimg.com/t01ce1698b1c6d7e89a.png)

当我们注入到了X30中，我们对于第32轮的影响就和前面所提到的例子一样了，那么我们同样可以按照之前提到的攻击方式恢复出key，并解密得到flag

```
# exp.py
#!/usr/bin/env python
from pwn import *
from os import urandom
from Crypto.Util.number import long_to_bytes, getRandomNBitInteger, bytes_to_long
from collections import Counter
from hashlib import sha256
import itertools, random, string
# context.log_level = "debug"

dic = string.ascii_letters + string.digits

r = remote("127.0.0.1",8006)

def solve_pow(suffix,target):
    print("[+] Solving pow")
    for i in dic:
        for j in dic:
            for k in dic:
                head = i + j + k
                h = head.encode() + suffix
                sha256 = hashlib.sha256()
                sha256.update(h)
                res = sha256.hexdigest().encode()
                if res == target:
                    print("[+] Find pow")
                    return head

def get_enc_flag():
    r.recvuntil("your flag is\n")
    enc = r.recvuntil("\n")[:-1]
    return enc

def cmd(idx):
    r.recvuntil("&gt; ")
    r.sendline(str(idx))

def encrypt1(pt):
    cmd(1)
    r.recvuntil("your plaintext in hex")
    r.sendline(pt)
    r.recvuntil("your ciphertext in hex:")
    enc = r.recvuntil("\n")[:-1]
    return enc

def encrypt2(pt,round,f,p):
    cmd(2)
    r.recvuntil("your plaintext in hex")
    r.sendline(pt)
    r.recvuntil("give me the value of r f p")
    payload = str(round) + " " + str(f) + " " + str(p)
    r.sendline(payload)
    r.recvuntil("your ciphertext in hex:")
    enc = r.recvuntil("\n")[:-1]
    return enc

def decrypt(ct,key):
    cmd(3)
    r.recvuntil("your key in hex")
    r.sendline(key)
    r.recvuntil("your ciphertext in hex")
    r.sendline(ct)
    r.recvuntil("your plaintext in hex:")
    dec = r.recvuntil("\n")[:-1]
    return dec


xor = lambda a, b:list(map(lambda x, y: x ^ y, a, b))
rotl = lambda x, n:((x &lt;&lt; n) &amp; 0xffffffff) | ((x &gt;&gt; (32 - n)) &amp; 0xffffffff)
get_uint32_be = lambda key_data:((key_data[0] &lt;&lt; 24) | (key_data[1] &lt;&lt; 16) | (key_data[2] &lt;&lt; 8) | (key_data[3]))
put_uint32_be = lambda n:[((n&gt;&gt;24)&amp;0xff), ((n&gt;&gt;16)&amp;0xff), ((n&gt;&gt;8)&amp;0xff), ((n)&amp;0xff)]
padding = lambda data, block=16: data + [(16 - len(data) % block)for _ in range(16 - len(data) % block)]
unpadding = lambda data: data[:-data[-1]]
list_to_bytes = lambda data: b''.join([bytes((i,)) for i in data])
bytes_to_list = lambda data: [i for i in data]

#Expanded SM4 box table
SM4_BOXES_TABLE = [
    0xd6,0x90,0xe9,0xfe,0xcc,0xe1,0x3d,0xb7,0x16,0xb6,0x14,0xc2,0x28,0xfb,0x2c,
    0x05,0x2b,0x67,0x9a,0x76,0x2a,0xbe,0x04,0xc3,0xaa,0x44,0x13,0x26,0x49,0x86,
    0x06,0x99,0x9c,0x42,0x50,0xf4,0x91,0xef,0x98,0x7a,0x33,0x54,0x0b,0x43,0xed,
    0xcf,0xac,0x62,0xe4,0xb3,0x1c,0xa9,0xc9,0x08,0xe8,0x95,0x80,0xdf,0x94,0xfa,
    0x75,0x8f,0x3f,0xa6,0x47,0x07,0xa7,0xfc,0xf3,0x73,0x17,0xba,0x83,0x59,0x3c,
    0x19,0xe6,0x85,0x4f,0xa8,0x68,0x6b,0x81,0xb2,0x71,0x64,0xda,0x8b,0xf8,0xeb,
    0x0f,0x4b,0x70,0x56,0x9d,0x35,0x1e,0x24,0x0e,0x5e,0x63,0x58,0xd1,0xa2,0x25,
    0x22,0x7c,0x3b,0x01,0x21,0x78,0x87,0xd4,0x00,0x46,0x57,0x9f,0xd3,0x27,0x52,
    0x4c,0x36,0x02,0xe7,0xa0,0xc4,0xc8,0x9e,0xea,0xbf,0x8a,0xd2,0x40,0xc7,0x38,
    0xb5,0xa3,0xf7,0xf2,0xce,0xf9,0x61,0x15,0xa1,0xe0,0xae,0x5d,0xa4,0x9b,0x34,
    0x1a,0x55,0xad,0x93,0x32,0x30,0xf5,0x8c,0xb1,0xe3,0x1d,0xf6,0xe2,0x2e,0x82,
    0x66,0xca,0x60,0xc0,0x29,0x23,0xab,0x0d,0x53,0x4e,0x6f,0xd5,0xdb,0x37,0x45,
    0xde,0xfd,0x8e,0x2f,0x03,0xff,0x6a,0x72,0x6d,0x6c,0x5b,0x51,0x8d,0x1b,0xaf,
    0x92,0xbb,0xdd,0xbc,0x7f,0x11,0xd9,0x5c,0x41,0x1f,0x10,0x5a,0xd8,0x0a,0xc1,
    0x31,0x88,0xa5,0xcd,0x7b,0xbd,0x2d,0x74,0xd0,0x12,0xb8,0xe5,0xb4,0xb0,0x89,
    0x69,0x97,0x4a,0x0c,0x96,0x77,0x7e,0x65,0xb9,0xf1,0x09,0xc5,0x6e,0xc6,0x84,
    0x18,0xf0,0x7d,0xec,0x3a,0xdc,0x4d,0x20,0x79,0xee,0x5f,0x3e,0xd7,0xcb,0x39,
    0x48,
]

# System parameter
SM4_FK = [0xa3b1bac6,0x56aa3350,0x677d9197,0xb27022dc]

# fixed parameter
SM4_CK = [
    0x00070e15,0x1c232a31,0x383f464d,0x545b6269,
    0x70777e85,0x8c939aa1,0xa8afb6bd,0xc4cbd2d9,
    0xe0e7eef5,0xfc030a11,0x181f262d,0x343b4249,
    0x50575e65,0x6c737a81,0x888f969d,0xa4abb2b9,
    0xc0c7ced5,0xdce3eaf1,0xf8ff060d,0x141b2229,
    0x30373e45,0x4c535a61,0x686f767d,0x848b9299,
    0xa0a7aeb5,0xbcc3cad1,0xd8dfe6ed,0xf4fb0209,
    0x10171e25,0x2c333a41,0x484f565d,0x646b7279
]

def invL(A):
    tmp = A ^ rotl(A,2) ^ rotl(A,4) ^ rotl(A,8) ^ rotl(A,12) ^ rotl(A,14) ^ rotl(A,16) ^ rotl(A,18) ^  rotl(A,22) ^ rotl(A,24) ^ rotl(A,30)
    return tmp

def invR(l):
    tmp = [l[3],l[2],l[1],l[0]]
    return tmp

def L(bb):
    c = bb ^ (rotl(bb, 2)) ^ (rotl(bb, 10)) ^ (rotl(bb, 18)) ^ (rotl(bb, 24))
    return c

def int2list(x):
    a0 = x &amp; 0xffffffff
    a1 = (x &gt;&gt; 32) &amp; 0xffffffff
    a2 = (x &gt;&gt; 64) &amp; 0xffffffff
    a3 = (x &gt;&gt; 96) &amp; 0xffffffff
    return [a3,a2,a1,a0]

def fault_attak(ct1s,ct2s,target,round):
    assert len(ct1s) == len(ct2s)
    keys = []
    for guess_key in range(256):
        for i in range(len(ct1s)):
            ct1 = ct1s[i]
            ct1 = invR(int2list(bytes_to_long(ct1)))

            ct2 = ct2s[i]
            ct2 = invR(int2list(bytes_to_long(ct2)))

            if round &lt; 32:
                for r in range(32-round):
                    ct1 = rev_round(ct1,32-r)
                    ct2 = rev_round(ct2,32-r)

            x1,x2,x3,x4 = ct1
            xx1,xx2,xx3,xx4 = ct2

            out_diff = invL(xx4 ^ x4)
            in_diff = (x1^xx1)^(x2^xx2)^(x3^xx3)
            Sa = [(out_diff &gt;&gt; (i*8)) &amp; 0xff for i in range(4)]
            Sa = Sa[3-target]
            Sb = SM4_BOXES_TABLE[((xx3 ^ xx2 ^ xx1) &gt;&gt; (3-target)*8) &amp; 0xff ^ guess_key]
            Sc = SM4_BOXES_TABLE[((xx3 ^ xx2 ^ xx1 ^ in_diff) &gt;&gt; (3-target)*8) &amp; 0xff ^ guess_key]
            if Sa == Sb ^ Sc:
                if guess_key not in keys:
                    keys.append(guess_key)   
                    break
    return keys

def int2hex(x):
    tmp = hex(x)[2:].rjust(32,"0")
    return tmp

def attack_round_key_byte(target,round,num):
    pts = []
    ct1s = []
    ct2s = []
    p = 4 + target
    FLAG = False
    if round == 32:
        p = target
        round = 31
        FLAG = True

    f = random.randint(1,0xf)
    for i in range(num):
        pt = getRandomNBitInteger(32 * 4)
        pt = int2hex(pt)
        ct1 = long_to_bytes(int(encrypt1(pt),16))[:16]
        ct2 = long_to_bytes(int(encrypt2(pt,round,f,p),16))[:16]
        pts.append(pt)
        ct1s.append(ct1)
        ct2s.append(ct2)
    if FLAG == True:
        res1 = set(fault_attak(ct1s,ct2s,target,32))
    else:
        res1 = set(fault_attak(ct1s,ct2s,target,round))

    pts = []
    ct1s = []
    ct2s = []
    f = random.randint(1,0xff)
    for i in range(num):
        pt = getRandomNBitInteger(32 * 4)
        pt = int2hex(pt)
        ct1 = long_to_bytes(int(encrypt1(pt),16))[:16]
        ct2 = long_to_bytes(int(encrypt2(pt,round,f,p),16))[:16]
        pts.append(pt)
        ct1s.append(ct1)
        ct2s.append(ct2)
    if FLAG == True:
        res2 = set(fault_attak(ct1s,ct2s,target,32))
    else:
        res2 = set(fault_attak(ct1s,ct2s,target,round))
    res = list(res1&amp;res2)
    return res[0]

def attack_round_keys(round):
    keys = []
    for i in range(4):
        key = attack_round_key_byte(i,round,5)
        keys.append(key)
    return keys

def rev_round(ct,round):
    global subkeys
    X1,X2,X3,X4 = ct
    sub_key = get_uint32_be(subkeys[32-round])
    sbox_in = X1 ^ X2 ^ X3 ^ sub_key
    b = [0, 0, 0, 0]
    a = put_uint32_be(sbox_in)
    b[0] = SM4_BOXES_TABLE[a[0]]
    b[1] = SM4_BOXES_TABLE[a[1]]
    b[2] = SM4_BOXES_TABLE[a[2]]
    b[3] = SM4_BOXES_TABLE[a[3]]
    bb = get_uint32_be(b[0:4])
    c = bb ^ (rotl(bb, 2)) ^ (rotl(bb, 10)) ^ (rotl(bb, 18)) ^ (rotl(bb, 24))
    X0 = X4 ^ c
    ct = X0,X1,X2,X3
    return ct

def int_list_to_bytes(x):
    tmp = 0
    for i in x:
        tmp &lt;&lt;= 32
        tmp |= i
    tmp = long_to_bytes(tmp)
    return tmp

def round_key(ka):
    b = [0, 0, 0, 0]
    a = put_uint32_be(ka)
    b[0] = SM4_BOXES_TABLE[a[0]]
    b[1] = SM4_BOXES_TABLE[a[1]]
    b[2] = SM4_BOXES_TABLE[a[2]]
    b[3] = SM4_BOXES_TABLE[a[3]]
    bb = get_uint32_be(b[0:4])
    rk = bb ^ (rotl(bb, 13)) ^ (rotl(bb, 23))
    return rk

def rev_key(subkeys):
    tmp_keys = [i for i in subkeys]
    for i in range(32):
        tmp_keys.append(0)
    for i in range(32):
        tmp_keys[i+4] = tmp_keys[i] ^ round_key(tmp_keys[i+1] ^ tmp_keys[i+2] ^ tmp_keys[i+3] ^ SM4_CK[31-i])
    tmp_keys = tmp_keys[::-1]
    MK = xor(SM4_FK[0:4], tmp_keys[0:4])
    MK = int_list_to_bytes(MK)
    return MK

r.recvuntil("sha256(XXX+")
suffix = r.recvuntil(") == ",drop = True)
target = r.recvuntil("\n")[:-1]
s = solve_pow(suffix,target)
r.sendline(s)

enc_flag = get_enc_flag()

subkeys = []
t = [32,31,30,29]
for i in t:
    print("[+] Crack Round " + str(i) + " subkey")
    keys = attack_round_keys(i)
    print("[+] Find Round " + str(i) + " subkey")
    print(keys)
    subkeys.append(keys)

subkeys = [get_uint32_be(i) for i in subkeys]
attack_key = rev_key(subkeys)
attack_key = int2hex(bytes_to_long(attack_key))
print("[+] Find keys :")
print(attack_key)

enc_flag = enc_flag.decode("utf-8")
print("[+] Enc flag is :")
print(enc_flag)

flag = decrypt(enc_flag,attack_key)
flag = long_to_bytes(int(flag.decode("utf-8"),16))
print("[+] Get flag :")
print(flag)

r.interactive()
```



## Reference

[https://zh.wikipedia.org/wiki/SM4](https://zh.wikipedia.org/wiki/SM4)

[https://en.wikipedia.org/wiki/Differential_fault_analysis](https://en.wikipedia.org/wiki/Differential_fault_analysis)

[https://eprint.iacr.org/2010/063.pdf](https://eprint.iacr.org/2010/063.pdf)

[http://www.sicris.cn/CN/abstract/abstract192.shtml](http://www.sicris.cn/CN/abstract/abstract192.shtml)

[https://0xdktb.top/2020/08/24/WriteUp-强网杯2020-Crypto/](https://0xdktb.top/2020/08/24/WriteUp-%E5%BC%BA%E7%BD%91%E6%9D%AF2020-Crypto/)
