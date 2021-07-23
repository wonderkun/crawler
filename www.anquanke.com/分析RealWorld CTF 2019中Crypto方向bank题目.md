> 原文链接: https://www.anquanke.com//post/id/188174 


# 分析RealWorld CTF 2019中Crypto方向bank题目


                                阅读量   
                                **728636**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01325779038165c4a7.jpg)](https://p4.ssl.qhimg.com/t01325779038165c4a7.jpg)



## 前言

bank是RealWorld CTF 2019中唯一的一道crypto题，题目涉及到了schnorr比特币签名算法，在此记录一下分析和解题过程以及针对schnorr的一些攻击技巧。



## 题目信息

You’ve earned a lot of cash from investing bitcoins! Why not try our coolest multi-signature bank?<br>
nc tcp.realworldctf.com 20014<br>[bank.zip](https://github.com/ichunqiu-resources/anquanke/raw/master/004/bank.zip)



## 初步分析

源码+服务器交互题，bypass掉POW后，服务器端首先打印如下信息：

```
Generating keys...
Please tell us your public key:
```

可以看到，服务器预期我们提供一个public key，那么我们直接使用题目当中给出的`schnorr.py`随机生成一个公钥，通过阅读源码可以发现本题中所有交互均是以base64编码后的结果来进行的，生成过程如下：

```
&gt;&gt;&gt; from schnorr import *
&gt;&gt;&gt; sk, pk = generate_keys()
&gt;&gt;&gt; pk
(64646428988419328348098910455943469703858360262896251929535045073512200095812L, 8827897429209231856466904238695535359213319466247516611187411915515480433077L)
&gt;&gt;&gt; from base64 import *
&gt;&gt;&gt; strpk = "64646428988419328348098910455943469703858360262896251929535045073512200095812, 8827897429209231856466904238695535359213319466247516611187411915515480433077"
&gt;&gt;&gt; b64encode(strpk)
'NjQ2NDY0Mjg5ODg0MTkzMjgzNDgwOTg5MTA0NTU5NDM0Njk3MDM4NTgzNjAyNjI4OTYyNTE5Mjk1MzUwNDUwNzM1MTIyMDAwOTU4MTIsIDg4Mjc4OTc0MjkyMDkyMzE4NTY0NjY5MDQyMzg2OTU1MzUzNTkyMTMzMTk0NjYyNDc1MTY2MTExODc0MTE5MTU1MTU0ODA0MzMwNzc='
```

将base64编码后的结果提交至服务器，进入到本题的主菜单界面：

```
Generating keys...
Please tell us your public key:NjQ2NDY0Mjg5ODg0MTkzMjgzNDgwOTg5MTA0NTU5NDM0Njk3MDM4NTgzNjAyNjI4OTYyNTE5Mjk1MzUwNDUwNzM1MTIyMDAwOTU4MTIsIDg4Mjc4OTc0MjkyMDkyMzE4NTY0NjY5MDQyMzg2OTU1MzUzNTkyMTMzMTk0NjYyNDc1MTY2MTExODc0MTE5MTU1MTU0ODA0MzMwNzc=
User logged in.

                [Beep]

    Please select your options:

    1. Deposit a coin into your account, you can sign a message 'DEPOSIT' and send us the signature.
    2. Withdraw a coin from your account, you need to provide us a message 'WITHDRAW' signed by both of you and our RESPECTED BANK MANAGER.
    3. Find one of our customer support representative to assist you.


    Our working hour is 9:00 am to 5:00 pm every Saturday!
    Thank you for being our loyal customer and your satisfaction is our first priority!
```

根据源码和提示信息，我们可以得知以下信息：

```
1.要求用户给出"DEPOSIT"字符串的签名，并使用用户自己提供的`用户公钥`对签名结果进行校验，校验通过的话，比特币+1。
2.要求用户给出"WITHDRAW"字符串的签名，并使用`mul_add(用户公钥,系统公钥)`对签名结果进行校验，校验通过且比特币数量&gt;0的话，打印flag。
3.打印`系统公钥`。
```

其中，每执行完一个选项，系统都会重新从要求用户提供公钥那一步开始，不停循环这些操作，而系统公钥是在这些循环操作之前生成的，也就是说在一次nc过程中，系统公钥是始终保持不变的。

那么接下来整理一下我们的任务，我们要想满足选项2的check，得到flag，基本上只有3种可能的思路：

```
1. 想办法**求出**系统私钥，然后直接用我们的私钥和系统私钥计算出"WITHDRAW"字符串的签名。
2. 想办法**泄露**系统私钥，然后直接用我们的私钥和系统私钥计算出"WITHDRAW"字符串的签名。
2. 想办法在不知道系统私钥的情况下，直接**伪造**出我们所需要的签名。
```

第一种思路需要我们解决一个ECDLP问题，根据on_curve函数可知：

```
#即y^2 - x^3 ≡ 7 (mod p)，a = 0，b = 7
def on_curve(point):
    return (pow(point[1], 2, p) - pow(point[0], 3, p)) % p == 7
```

曲线参数已知，我们可以check一下是否可以应用[Smart’s attack](https://wstein.org/edu/2010/414/projects/novotney.pdf)来求出私钥：

```
sage: a = 0
sage: b = 7
sage: p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
sage: E = EllipticCurve(GF(p), [a, b])
sage: E.order() == p
False
```

可以看到这里`E.order()`和`p`是不相同的，所以我们没有办法很好的展开Smart’s attack，那么我们接下来看一下第二种思路。

第二种思路需要我们泄露私钥，通过查阅资料&amp;论文，我们可以找到[《Simple Schnorr Multi-Signatures with Applications to Bitcoin》](https://eprint.iacr.org/2018/068.pdf)这篇论文，在这篇论文中介绍了一类攻击场景，**当使用相同的k签名两个不同的msg**的时候，我们可以按照如下思路恢复私钥：

[![](https://raw.githubusercontent.com/ichunqiu-resources/anquanke/master/004/1.png)](https://raw.githubusercontent.com/ichunqiu-resources/anquanke/master/004/1.png)

将其写成代码的形式，即：

```
# 随机生成一对私钥和公钥
secret_key = random.SystemRandom().randrange(1, n)
public_key = point_mul(G, secret_key)

# 用相同的k对两个不同的消息进行签名
signing_k = random.SystemRandom().randrange(1, n)
sig1_r, sig1_s = schnorr_sign('first_message', secret_key, signing_k)
sig2_r, sig2_s = schnorr_sign('second_message', secret_key, signing_k)
assert sig1_r == sig2_r
print('+ R used   = `{`:x`}`'.format(sig1_r))

# 根据签名和哈希重构私钥
e1 = sha256(sig1_r.to_bytes(32, byteorder="big") + bytes_point(public_key) + 'first_message'.encode())
e2 = sha256(sig2_r.to_bytes(32, byteorder="big") + bytes_point(public_key) + 'second_message'.encode())
d = ((sig1_s - sig2_s) * inv(e1 - e2, n)) % n
```

但是如果采用这种方法的话，我们的k应该是作为一个独立可控的参数出现的，这样我们才能传入相同的k实施这一攻击，即我们的`schnorr_sign`函数应该这么写：

```
def schnorr_sign(msg, seckey, k):
    R = point_mul(G, k)
    if jacobi(R[1]) != 1:
        k = n - k
    e = sha256(R[0].to_bytes(32, byteorder="big") + bytes_point(point_mul(G, seckey)) + msg.encode())
    return (R[0], (k + e * seckey) % n)
```

但是我们本题中的`schnorr_sign`函数是这么写的：

```
def schnorr_sign(msg, seckey):
    k = sha256(to_bytes(seckey, 32, byteorder="big") + msg)
    R = point_mul(G, k)
    if jacobi(R[1]) != 1:
        k = n - k
    e = sha256(to_bytes(R[0], 32, byteorder="big") + bytes_point(point_mul(G, seckey)) + msg)
    return to_bytes(R[0], 32, byteorder="big") + to_bytes(((k + e * seckey) % n), 32, byteorder="big")
```

按照我们本题的这种写法，**在生产k的时候本身就引入了msg，因此不可能在msg不同的情况下产生相同的k**。所以说这一思路又行不通了，那么我们就只剩下第三种思路。

第三种思路需要我们在不知道私钥的情况下伪造出签名，我们分析一下不难发现，由于系统每次都允许用户先提交一次公钥再进行后续的操作，而且操作3还可以得到系统的公钥，那么如果我们提交`(用户公钥 - 系统公钥)`作为用户公钥来提交，系统再在操作2进行校验时，就会使用`(用户公钥 - 系统公钥) + 系统公钥`来进行校验，`系统公钥`被消去，即系统将使用`用户公钥`来进行校验，而`用户公钥`是我们自己生成的，显然我们知道其对应的`用户私钥`，那么我们很容易就可以计算出`'WITHDRAW'`的签名了。

整理一下上述思路，即我们的操作顺序为：

```
1. 随机生成一对usr_sk,usr_pk
2. 连接服务器，提交usr_pk
3. 使用usr_sk对'DEPOSIT'字符串进行签名，并将其提交至菜单选项1当中（这一步是为了比特币+1）。
4. 再次提交usr_pk
5. 选择菜单选项3，得到sys_pk
6. 计算point_sub(usr_pk,sys_pk)并提交
7. 使用usr_sk对'WITHDRAW'字符串进行签名，并将其提交至菜单选项2当中
8. 得到flag
```

将上述操作步骤写成exp如下：

```
import hashlib
import string
from base64 import *
from pwn import *
from schnorr import *

m1 = 'DEPOSIT'
m2 = 'WITHDRAW'
usr_pk = (114327674085560363590993327163840066309500593894278650456892267846105105547989, 109500385706600046295187892243946732955158496133501036041122596162143636261984)
usr_sk = 74314251512198093380740058910780830895178188526210019598065364316962239197930
str_usr_pk = str(usr_pk).replace("(",'').replace(")",'').replace("L",'')
str_usr_sk = str(usr_sk).replace("L",'')
str_m1_sig = schnorr_sign(m1,usr_sk)
str_m2_sig = schnorr_sign(m2,usr_sk)

r = remote('tcp.realworldctf.com',20014)
r.recvuntil('starting with ')
prefix = r.recvline().replace('n','')
dic = string.printable

def bypassPOW(prefix):
    for a in dic:
        for b in dic:
            for c in dic:
                for d in dic:
                    for e in dic:
                        x = prefix + a + b + c + d + e
                        assert len(x)==21
                        if hashlib.sha1(x).hexdigest()[::-1][:4]=='0000':
                            return x

payload = bypassPOW(prefix)
r.send(payload)       
r.recv()
r.recv()
r.sendline(b64encode(str_usr_pk))
r.recv()
r.sendline(b64encode('1'))
r.recv()
r.sendline(b64encode(str_m1_sig))
r.recv()
r.sendline(b64encode(str_usr_pk))
r.recv()
r.sendline(b64encode('3'))
r.recvuntil("us: ")
sys_pk = tuple(map(int,r.recvline().replace("(",'').replace(")",'').replace("L",'').replace("n",'').split(',')))
neg_sys_pk = tuple([sys_pk[0]] + [(-sys_pk[1])%p])
rogue_pk = point_add(usr_pk, neg_sys_pk)
str_rogue_pk = str(rogue_pk).replace("(",'').replace(")",'').replace("L",'')
r.recv()
r.sendline(b64encode(str_rogue_pk))
r.recv()
r.sendline(b64encode('2'))
r.recv()
r.sendline(b64encode(str_m2_sig))
r.interactive()
```

执行exp即可拿到flag：

```
rwctf`{`P1Ain_SChNorr_n33Ds_m0re_5ecur1ty!`}`
```

如果查阅资料&amp;论文，我们也可以找到一篇名为[《Key Aggregation for Schnorr Signatures》](https://blockstream.com/2018/01/23/en-musig-key-aggregation-schnorr-signatures/)的关于密钥聚合的报告，在这份报告中介绍了一种名为rogue-key attack的攻击方式，和我们本题的攻击思路是一致的，说明了在本题中的这种针对key aggregation scheme的攻击方式是真实存在的，也和我们本次比赛的realworld的风格相契合:)。



## 参考

[https://wstein.org/edu/2010/414/projects/novotney.pdf](https://wstein.org/edu/2010/414/projects/novotney.pdf)<br>[https://eprint.iacr.org/2018/068.pdf](https://eprint.iacr.org/2018/068.pdf)<br>[https://github.com/mvrcrypto/bitp0wn/blob/8431c7f8802ba60041385f20265be6d9c87f5525/signatures/r_exploit_schnorr.py](https://github.com/mvrcrypto/bitp0wn/blob/8431c7f8802ba60041385f20265be6d9c87f5525/signatures/r_exploit_schnorr.py)<br>[https://blockstream.com/2018/01/23/en-musig-key-aggregation-schnorr-signatures/](https://blockstream.com/2018/01/23/en-musig-key-aggregation-schnorr-signatures/)
