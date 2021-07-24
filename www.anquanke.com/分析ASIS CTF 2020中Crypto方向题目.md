> 原文链接: https://www.anquanke.com//post/id/219108 


# 分析ASIS CTF 2020中Crypto方向题目


                                阅读量   
                                **136077**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t0108733a96fffe3104.png)](https://p4.ssl.qhimg.com/t0108733a96fffe3104.png)



## 前言

ASIS CTF 2020中有7道Crypto方向道题目，题目难度适中，在这里对这7道题目进行一下分析。



## Baby RSA

**题目信息**

> All babies love RSA. How about you?
60 pts, 87 solves
[baby_rsa.zip](https://github.com/ichunqiu-resources/anquanke/raw/master/012/baby_rsa.zip)

**解题思路**<br>
本题中的t_p满足：

```
t_p ≡ (s * p + 1)^`{`(d-1)//(2^r)`}` (mod p)
```

根据二项式定理可知，t_p的展开式中仅有1项不包含`s * p`，且该项的值为1，因此有：

```
t_p ≡ 1 (mod p)
```

即`t_p - 1`是p的倍数，又因为N也是p的倍数，因此我们可以通过计算二者的最大公约数来求出p，即：

```
p = gcd(t_p-1, N)
```

**解题脚本**

```
from Crypto.Util.number import *
import math

e = 65537
n = 10594734342063566757448883321293669290587889620265586736339477212834603215495912433611144868846006156969270740855007264519632640641698642134252272607634933572167074297087706060885814882562940246513589425206930711731882822983635474686630558630207534121750609979878270286275038737837128131581881266426871686835017263726047271960106044197708707310947840827099436585066447299264829120559315794262731576114771746189786467883424574016648249716997628251427198814515283524719060137118861718653529700994985114658591731819116128152893001811343820147174516271545881541496467750752863683867477159692651266291345654483269128390649
t_p = 4519048305944870673996667250268978888991017018344606790335970757895844518537213438462551754870798014432500599516098452334333141083371363892434537397146761661356351987492551545141544282333284496356154689853566589087098714992334239545021777497521910627396112225599188792518283722610007089616240235553136331948312118820778466109157166814076918897321333302212037091468294236737664634236652872694643742513694231865411343972158511561161110552791654692064067926570244885476257516034078495033460959374008589773105321047878659565315394819180209475120634087455397672140885519817817257776910144945634993354823069305663576529148
ct = 5548605244436176056181226780712792626658031554693210613227037883659685322461405771085980865371756818537836556724405699867834352918413810459894692455739712787293493925926704951363016528075548052788176859617001319579989667391737106534619373230550539705242471496840327096240228287029720859133747702679648464160040864448646353875953946451194177148020357408296263967558099653116183721335233575474288724063742809047676165474538954797346185329962114447585306058828989433687341976816521575673147671067412234404782485540629504019524293885245673723057009189296634321892220944915880530683285446919795527111871615036653620565630

p = math.gcd(t_p - 1, n)
q = n//p
phi = (p - 1) * (q - 1)
d = inverse(e, phi)
pt = pow(ct, d, n)
flag = long_to_bytes(pt)
print(flag)

# ASIS`{`baby___RSA___f0r_W4rM_uP`}`
```



## Elliptic Curve

**题目信息**

> <p>Are all elliptic curves smooth and projective?<br>
nc 76.74.178.201 9531</p>
122 pts, 35 solves

**解题思路**<br>
nc到服务器上后会得到如下形式的提示信息和一组数据，我们以该组数据为例进行分析：

```
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+ hi! There are three integer points such that (x, y), (x+1, y), and +
+ (x+2, y) lies on the elliptic curve E. You are given one of them!! +
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
| One of such points is: P = (115698361452488238974138338877015059520521276799423896174180366779377621159382, 48211203852207979498593491920521330056163455005850597977840919840771542696861)
| Send the 17056578922004621506165926329396418048448214457100470575439939522285914558570 * P
```

题目告诉我们(x,y)、(x+1,y)和(x+2,y)是某曲线上的3个点，并告诉们了其中某个点的值，但并没说是哪个点，然后让我们提交该点乘一个常数的值，那么实际上就是想考察选手根据这些信息能否唯一确定一条椭圆曲线，由于我们没有源码，我们假定本题为E_p(a,b)形式的曲线，即：

```
y^2 ≡  x^3+a * x+b (mod p)  (1)
```

根据这3个点的特征，我们可以列出如下方程：

```
y^2  ≡  x^3 + a  * x + b  (mod p)               (2)
y^2  ≡  (x + 1)^3 + a  * (x + 1) + b  (mod p)   (3)
y^2  ≡  (x + 2)^3 + a  * (x + 2) + b  (mod p)   (4)
```

联立(2)、(3)式，可得：

```
a = -3x^2-3x-1  (5)
```

联立(2)、(4)式，可得：

```
a = -3x^2-6x-4  (6)
```

联立(5)、(6)式，可得`x = -1`，把`x = -1`带入(5)式，可得`a = -1`。

通过(6)式我们可知，曲线上的3个点为(-1,y)、(0,y)和(1,y)，其中后2个点的横坐标为0和1，显然示例数据中的点P并不符合这两种情况，那么点P只能表示(-1,y)这一点，即有：

```
P_x ≡ -1 (mod p)
```

也即`p = P_x-1`，此时a和p的值我们都已经确定下来了，可以确定b为：

```
b ≡ `{`P_y`}`^2 - `{`P_x`}`^3 - a * P_x (mod p)
```

a、b和p都确定下来后，曲线表达式确定，直接计算即可。

**解题脚本**

```
import hashlib
import string
import random
from Crypto.Util.number import *
from pwn import *

dic = string.ascii_letters + string.digits

def bypass_POW(r):
    st = r.recv().strip().split(b"(X)[-6:] = ")
    hash_type = st[0].split(b"that ")[1].decode()
    suffix = st[1][:6].decode()
    len = int(st[1][-2:])
    while True:
        ans = ''.join(random.choices(dic, k=len))
        h = getattr(hashlib, hash_type)(ans.encode()).hexdigest()
        if h.endswith(suffix):
            return ans

def point_add(p1, p2):
    if (p1 is None):
        return p2
    if (p2 is None):
        return p1
    if (p1[0] == p2[0] and p1[1] != p2[1]):
        return None
    if (p1 == p2):
        l = ((3 * p1[0] * p1[0] + a) * inverse(2 * p1[1], p)) % p
        x3 = (l * l - 2 * p1[0]) % p
        y3 = (l * (p1[0] - x3) - p1[1]) % p
        return (x3, y3)
    else:
        lam = ((p2[1] - p1[1]) * pow(p2[0] - p1[0], p - 2, p)) % p
    x3 = (lam * lam - p1[0] - p2[0]) % p
    return (x3, (lam * (p1[0] - x3) - p1[1]) % p)

def point_mul(p, n):
    r = None
    for i in range(256):
        if ((n &gt;&gt; i) &amp; 1):
            r = point_add(r, p)
        p = point_add(p, p)
    return r

while True:
    try:
        r = remote("76.74.178.201", 9531)
        ans = bypass_POW(r)
        r.sendline(ans)
        st = r.recvuntil("P = (")
        st = r.recvline().strip().replace(b')', b'').split(b',')
        P_x, P_y = int(st[0]), int(st[1])
        P = (P_x, P_y)
        st = r.recvuntil("| Send the ")
        st = r.recvline().strip().replace(b" * P :", b'')
        k = int(st)
        a = -1
        p = P_x + 1
        b = (P_y**2 - P_x**3 - a*P_x) % p
        Q = point_mul(P, k)
        r.sendline(str(Q))
        sleep(1)
        print(r.recv())
        break
    except:
        continue

# ASIS`{`4n_Ellip71c_curve_iZ_A_pl4Ne_al9ebr4iC_cUrv3`}`
```



## Tripolar

**题目信息**

> We all know about magnetic dipoles. Have you ever thought about magnetic tripoles?
156 pts, 26 solves
[tripolar.zip](https://github.com/ichunqiu-resources/anquanke/raw/master/012/tripolar.zip)

**解题思路**<br>
本题实际上就是在考察如何写出crow函数的逆函数，我们设

```
A = x + y + z + 1   (1)
B = x + y + 1       (2)
```

对crow函数的表达式进行配方，得：

```
crow(x,y,z) = (A^3 + 3B^2 + 2B - 6y - z - 6) // 6
```

我们知道对于一个形如：

```
f(x)=x^k+x^`{`k-1`}`+x^`{`k-2`}`+...+x^2+x+1
```

的多项式f(x)来讲，其x^k项的值我们可以用f(x)的值开k次根号来进行有效估计，即：

```
x^k = [\sqrt[k]`{`f(x)`}`]
```

则在本题中我们可以采用类似的方法估计出A和B的值为：

```
A = [\sqrt[3]`{`6 * crow(x,y,z)`}`]               (3)
B = [\sqrt[2]`{`(6 * crow(x,y,z) - A^3) // 3`}`]  (4)
```

联立 (3)、(4)式，可得：

```
z = A - B
```

把z的值同(3)、(4)式代入crow函数的表达式，可得：

```
y = (-6 * crow(x,y,z) + A^3 + 3B^2 + 2B - z - 6) // 6
```

把y同(4)式代入(2)式，可得：

```
x = B - y - 1
```

至此我们恢复出了x、y和z的值，按照恢复过程即可写出crow函数的逆函数。

**解题脚本**

```
import gmpy2
from Crypto.Util.number import *

def crow(x, y, z):
    return (x**3 + 3*(x + 2)*y**2 + y**3 + 3*(x + y + 1)*z**2 + z**3 + 6*x**2 + (3*x**2 + 12*x + 5)*y + (3*x**2 + 6*(x + 1)*y + 3*y**2 + 6*x + 2)*z + 11*x) // 6

def rev_crow(res, alpha):
    A = gmpy2.iroot(6*res, 3)[0]
    B = gmpy2.iroot((6*res - A**3)//3, 2)[0] + alpha
    z = A - B
    y = (-6*res + A**3 + 3*(B**2) + 2*B - z - 6)//6
    x = B - y - 1
    return (x, y, z)

f = open('flag.enc', 'rb').read()
ct = bytes_to_long(f)

x, y, z = rev_crow(ct, 0)
assert crow(x, y, z) == ct

pk = gmpy2.gcd(x, y)
_enc = x//pk

p, q, r = rev_crow(pk, 1)
assert [i for i in map(isPrime, [p, q, r])] == [1] * 3 and crow(p, q, r) == pk

e = 31337
N = p * q * r
phi = (p - 1) * (q - 1) * (r - 1)
d = inverse(e, phi)
pt = pow(_enc, d, N)
flag = long_to_bytes(pt)
print(flag)

# ASIS`{`I7s__Fueter-PoLy4__c0nJ3c7UrE_iN_p4Ir1n9_FuNCT10n`}`
```



## Dead Drop 1

**题目信息**

> <p>Tap, tap, on roof tops.<br>
Tic, toc, the clock tocs.<br>
Inside, what a cold night,<br>
Dead drop on roof tops!</p>
164 pts, 24 solves
[dead_drop_1.zip](https://github.com/ichunqiu-resources/anquanke/raw/master/012/dead_drop_1.zip)

**解题思路**<br>
题目给出了l组数据，对于每组数据`(a_s,(a_0,a_1,...,a_`{`l-1`}`))`，有：

```
a_s ≡ `{`a_0`}`^`{`b_0`}` * `{`a_1`}`^`{`b_1`}` * ...`{`a_`{`l-1`}``}`^`{`b_`{`l-1`}``}` (mod p)
```

其中p是一个合数，我们可以先尝试对其进行分解：

```
sage: p = 22883778425835100065427559392880895775739
sage: p.factor()
19 * 113 * 2657 * 6823 * 587934254364063975369377416367
```

设`p_0 = 587934254364063975369377416367`，那么本题中对模p下的运算可以转换为模p_0下的运算：

```
a_s ≡ `{`a_0`}`^`{`b_0`}` * `{`a_1`}`^`{`b_1`}` * ...`{`a_`{`l-1`}``}`^`{`b_`{`l-1`}``}` (mod p_0)
```

易知3为模p_0的一个原根，即模p_0下的任意一个数均可表示为3的次幂的形式，因此有：

```
3^y ≡ `{`3`}`^`{`x_0`}` * `{`3`}`^`{`x_1`}` * ...`{`3`}`^`{`x_`{`l-1`}``}` (mod p_0)
```

即有：

```
y ≡  x_0+x_1+...+x_`{`l-1`}` (mod `{`p_0-1`}`)
```

这里直接在模p_0-1下计算离散对数去求出y 和x_i是比较困难的，我们可以继续尝试对p_0-1进行分解：

```
sage: p0 = 587934254364063975369377416367
sage: (p0 - 1).factor()
2 * 19 * 157 * 98547478103262483300264401
```

可以看到`p_0 - 1`中包含小素因子，我们以157为例，令`r = 157，t = `{`p_0`}` // r`，此时有：

```
3^`{`y * t`}` ≡ `{`3`}`^`{`x_0 * t`}` * `{`3`}`^`{`x_1 * t`}` * ...`{`3`}`^`{`x_`{`l-1`}` * t`}` (mod p_0)
```

然后我们可以打一张长度为r的表，对于闭区间[0,r-1]内的每一个值i，向表中存储其在模p_0下原根3的`t * i`次幂的值及该i值：

```
p0 = 587934254364063975369377416367
r = 157
t = p0 // r

dic = `{``}`
for i in range(r):
    dic.update(`{`pow(pow(3, t, p0), i, p0) : i`}`)
```

然后对每一个3^y和3^`{`x_i`}`进行查表，这里以对3^y进行查表为例，设得到的值为z，则有：

```
3^`{`y * t`}` ≡ 3^`{`z * t`}` (mod `{`p_0`}`)
```

即有：

```
y * t ≡  z * t (mod `{`p_0-1`}`)
```

即：

```
y ≡ z (mod r)
```

这样我们就直接求出了y在模r下的值，同理，我们可以求出`x_i`在模r下的值，这样我们就列出了一个关于y和`x_i`在模r下的方程，由于我们有l组数据，因此这样的方程我们共可以列出l个，把`b_i`看成未知数，得到的就是关于`b_i`的l元一次模线性方程组，该模线性方程组的解即为`flag`的二进制流，因此直接解该模线性方程组即可。

**解题脚本**

```
from Crypto.Util.number import *

f = open('flag.enc', 'rb').read()
f = f.split(b'\n')[1]
f = f.replace(b'[', b'').replace(b']', b'').replace(b'L', b'').split(b', ')

l = 359

as_list = []
a_list = [[] for _ in range(l)]

for i in range(len(f)):
    if i % (l+1) == l:
        as_list.append(int(f[i]))
        continue
    else:
        a_list[i // (l+1)].append(int(f[i]))

enc = []
for i in range(l):
    enc.append((a_list[i], as_list[i]))

p0 = 587934254364063975369377416367
r = 157
t = (p0 - 1) // r
assert (p0 - 1) % t == 0

dic = `{``}`
for i in range(r):
    dic.update(`{`pow(pow(3, t, p0), i, p0) : i`}`)

M = []
b = []
for i in range(l):
    T = []
    for j in range(l):
        z_a = dic[Mod(pow(enc[i][0][j], t, p0), p0)]
        T.append(Mod(z_a, r))
    z_as = dic[Mod(pow(enc[i][1], t, p0), p0)]
    M.append(T)
    b.append(Mod(z_as, r))

M = Matrix(M)
b = vector(b)
flag_bin = M.solve_right(b)
flag = long_to_bytes(int(''.join([i for i in map(str, flag_bin)]), 2))
print(flag)

# ASIS`{`175_Lik3_Multivariabl3_LiNe4r_3QuA7i0n5`}`
```



## Dead Drop 2

**题目信息**

> <p>I want to taste you again, like a secret or a sin.<br>
Drop it, I’m dead</p>
209 pts, 17 solves
[dead_drop_2.zip](https://github.com/ichunqiu-resources/anquanke/raw/master/012/dead_drop_2.zip)

**解题思路**<br>
本题还是沿用了Dead Drop 1一题的模型，我们直接把本题中的q看作上题中的`p_0`即可，其余思路均和上题一致。

**解题脚本**

```
from Crypto.Util.number import *

f = open('flag.enc', 'rb').read()
f = f.split(b'\n')[1]
f = f.replace(b'[', b'').replace(b']', b'').replace(b'L', b'').split(b', ')

l = 215

as_list = []
a_list = [[] for _ in range(len(f) // (l+1))]

for i in range(len(f)):
    if i % (l+1) == l:
        as_list.append(int(f[i]))
        continue
    else:
        a_list[i // (l+1)].append(int(f[i]))

enc = []
for i in range(len(f) // (l+1)):
    enc.append((a_list[i], as_list[i]))

q = 39485091642302322462443783940079058526663151328744488399920207767
r = 397
t = (q - 1) // r
assert (q - 1) % t == 0

dic = `{``}`
for i in range(r):
    dic.update(`{`pow(pow(3, t, q), i, q) : i`}`)

M = []
b = []
for i in range(l):
    T = []
    for j in range(l):
        z_a = dic[Mod(pow(enc[i][0][j], t, q), q)]
        T.append(Mod(z_a, r))
    z_as = dic[Mod(pow(enc[i][1], t, q), q)]
    M.append(T)
    b.append(Mod(z_as, r))

M = Matrix(M)
b = vector(b)
flag_bin = M.solve_right(b)
flag = b"flag`{`" + long_to_bytes(int(''.join([i for i in map(str, flag_bin)]), 2)) + b'`}`'
print(flag)

# flag`{`Z_q_iZ_n0T_a_DDH_h4rD_9r0uP`}`
```



## Jazzy

**题目信息**

> <p>Jazzy in the real world, but it’s flashy and showy!<br>
nc 76.74.178.201 31337</p>
119 pts, 36 solves

**解题思路**<br>
nc到服务器上后服务器展示给选手菜单如下：

```
------------------------------------------------------------------------
|          ..:: Jazzy semantically secure cryptosystem ::..            |
|           Try to break this cryptosystem and find the flag!          |
------------------------------------------------------------------------
| Options:                                                             |
|       [E]ncryption function                                             |
|       [F]lag (encrypted)!                                               |
|       [P]ublic key                                                      |
|       [D]ecryption oracle                                               |
|       [Q]uit                                                            |
|----------------------------------------------------------------------|
```

输入“E”拿到加密函数源码如下：

```
def encrypt(msg, pubkey):
    h = len(bin(len(bin(pubkey)[2:]))[2:]) - 1    # dirty log :/
    m = bytes_to_long(msg)
    if len(bin(m)[2:]) % h != 0:
        m = '0' * (h - len(bin(m)[2:]) % h) + bin(m)[2:]
    else:
        m = bin(m)[2:]
    t = len(m) // h
    M = [m[h*i:h*i+h] for i in range(t)]
    r = random.randint(1, pubkey)
    s_0 = pow(r, 2, pubkey)
    C = []
    for i in range(t):
        s_i = pow(s_0, 2, pubkey)
        k = bin(s_i)[2:][-h:]
        c = bin(int(M[i], 2) ^ int(k, 2))[2:].zfill(h)
        C.append(c)
        s_0 = s_i
    enc = int(''.join(C), 2)
    return (enc, pow(s_i, 2, pubkey))
```

可以看到题目实现了一个Blum-Goldwasser概率公钥密码体制的加密函数，该加密方式使用Blum-Blum-Shub伪随机数生成算法来产出密钥流。

我们输入“F”可以拿到`flag`的密文：

```
F
encrypt(flag, pubkey) = (104972271242839281756758190817353189671079864957194083204020330124090873093534127488372355616625828743144757887625958045787714737582951019266611928740809907242924589328275033353098515059544694565823799475217633923557357540319210284410150958946855641375942332652505255035655419692822757L, 5883596561316190474382177490418469615572460141194909287402341244582040495460516154208860326457094210637788425831802068523863763449812689218691410964441338070657770209173951613204821054523350043165965943057900603264650015352646204374731854090909433204281420550107029576093895650885787152234634894724494432033747199881699869384874007678945115890136723236776767611754228405596517759873333249232820897258324066360057522710710110600293940928301886981042661513103978117253922400113480988449614362037399326475356109629381023245487694845863268010842940276343784846923442148452647532890584363678308925299220515823196513324699L)
```

输入“P”可以拿到公钥：

```
P
pubkey = 27232296696706977514566448751666084413522639121220581766188898073124742484283380993174091100179428934544646420995742560436515794096254661036806067514034027493697898384019054273649258597568814936998372268617337345061885563425934488908805711719515906851436585430352341990476591339447291521966296125686710775131057300712094532855970243058977132371024512515462220561783900679244435679560234935480978627509174995881061341940458445491296973409417582619357984325474438361836318756381673242703902895535926275985306525593219282056556804164358905234179162754534147391459785627434518845709983884052342074221004036207785840888173
```

输入“D”可以使用服务器提供的解密ORACLE，但是不能解密`flag`的密文（实际上我们提交的要解密的内容中不能含有`flag`的密文这个二元组中的任何一项）：

```
D
| send an pair of integers, like (c, x), that you want to decrypt: 
(104972271242839281756758190817353189671079864957194083204020330124090873093534127488372355616625828743144757887625958045787714737582951019266611928740809907242924589328275033353098515059544694565823799475217633923557357540319210284410150958946855641375942332652505255035655419692822757, 5883596561316190474382177490418469615572460141194909287402341244582040495460516154208860326457094210637788425831802068523863763449812689218691410964441338070657770209173951613204821054523350043165965943057900603264650015352646204374731854090909433204281420550107029576093895650885787152234634894724494432033747199881699869384874007678945115890136723236776767611754228405596517759873333249232820897258324066360057522710710110600293940928301886981042661513103978117253922400113480988449614362037399326475356109629381023245487694845863268010842940276343784846923442148452647532890584363678308925299220515823196513324699)
| this decryption is NOT allowed :P
```

但是我们可以绕过服务器的这一限制，根据Blum-Goldwasser的加密方式，我们可以将`flag`的密文再扩展一轮，设`flag`的密文为`(flag_enc, s)`，则扩展后的密文为`(flag_enc_padded, ss)`，其中：

```
flag_enc_padded = int(bin(flag_enc)[2:] + '0'*h, 2)
ss = pow(s, 2, pubkey)
```

向解密ORACLE提交扩展后的密文来得到其对应的明文，然后去掉明文的二进制比特流的后h位即可得到`flag`的二进制流。

**解题脚本**

```
from pwn import *
from Crypto.Util.number import *

r = remote("76.74.178.201", 31337)
_ = r.recv()

r.sendline('F')
_ = r.recvuntil("encrypt(flag, pubkey) = ")
st = r.recvline().strip().replace(b'(', b'').replace(b')', b'').replace(b'L', b'').split(b',')
flag_enc = int(st[0])
s = int(st[1])

r.sendline('P')
_ = r.recvuntil("pubkey = ")
st = r.recvline().strip()
pubkey = int(st)

h = len(bin(len(bin(pubkey)[2:]))[2:]) - 1
flag_enc_padded = int(bin(flag_enc)[2:] + '0'*h, 2)
ss = pow(s, 2, pubkey)
r.sendline('D')
_ = r.recvuntil("decrypt: \n")
r.sendline(str((flag_enc_padded, ss)))

_ = r.recvuntil("is: ")
st = r.recvline().strip()
pt = int(st)
flag = long_to_bytes(int(bin(pt)[2:-h], 2))
print(flag)

# ASIS`{`BlUM_G0ldwaS53R_cryptOsySt3M_Iz_HI9hlY_vUlNEr4bl3_70_CCA!?`}`
```



## Crazy

**题目信息**

> <p>Look at you kids with your vintage music<br>
Comin’ through satellites while cruisin’<br>
You’re part of the past, but now you’re the future<br>
Signals crossing can get confusing<br>
It’s enough just to make you feel crazy, crazy, crazy<br>
Sometimes, it’s enough just to make you feel crazy…</p>
150 pts, 27 solves
[crazy.zip](https://github.com/ichunqiu-resources/anquanke/raw/master/012/crazy.zip)

**解题思路**<br>
本题还是沿用了Jazzy一题的模型，只不过在Jazzy一题中`encrypt`函数的异或操作的基础上又引入了按位与一个未知的`xorkey`的操作，同时本题不再提供解密ORACLE，而是给出了若干公钥以及使用这些公钥对`flag`加密后的密文。

由于本题没有提供更多信息，我们只能从已有信息中去进行尝试，经过对题目中给出的若干公钥进行分析，发现其中有公钥之间存在公因子，因此可以利用模不互素攻击来求出私钥，求出私钥后按照Blum-Goldwasser体制的解密方式进行解密即可，注意本题虽然还引入了按位与一个未知的`xorkey`的操作，但是在进行按位与时`xorkey`实际上只有低h位参与了运算，而在本题中h=10，即`xorkey`一共只有1024种可能的值，因此直接进行爆破即可。

**解题脚本**

```
import gmpy2
from Crypto.Util.number import *

f = open("output.txt", 'rb').read().split(b'\n')[:-1]

pk_list = []
enc_list = []
for i in f:
    st = i.replace(b'(', b'').replace(b')', b'').replace(b'L', b'').replace(b', ', b' ').split(b' ')
    pk_list.append(int(st[0]))
    enc_list.append((int(st[1]), int(st[2])))

known = 0
for i in pk_list:
    if known == 1:
        break
    for j in pk_list:
        if gmpy2.gcd(i, j) != 1 and i != j:
            p = gmpy2.gcd(i, j)
            q = i//p
            n = p*q
            known = 1
            break

ct = enc_list[pk_list.index(n)]

def decrypt(c, s, pubkey, p, q):
    h = len(bin(len(bin(pubkey)[2:]))[2:]) - 1
    if len(bin(c)[2:]) % h != 0:
        c = '0' * (h - len(bin(c)[2:]) % h) + bin(c)[2:]
    else:
        c = bin(c)[2:]
    t = len(c) // h
    a_1 = (((p + 1) // 4)**(t + 1)) % (p - 1)
    a_2 = (((q + 1) // 4)**(t + 1)) % (q - 1)
    b_1 = pow(s, a_1, p)
    b_2 = pow(s, a_2, q)
    _, a, b = gmpy2.gcdext(p, q)
    C = [c[h*i:h*i+h] for i in range(t)]
    flag_list = []
    for xorkey in range(2**10):
        s_0 = (b_2 * a * p + b_1 * b * q ) % pubkey
        M = []
        for i in range(t):
            s_i = pow(s_0, 2, pubkey)
            k = bin(s_i)[2:][-h:]
            m = bin(int(C[i], 2) ^ int(k, 2) &amp; xorkey)[2:].zfill(h)
            M.append(m)
            s_0 = s_i
        msg = long_to_bytes(int(''.join(M),2))
        if b"ASIS`{`" in msg:
            flag_list.append(msg)
    return flag_list

flag_list = decrypt(ct[0], ct[1], n, p, q)
for i in flag_list:
    print(i)

# ASIS`{`1N_h0nOr_oF__Lenore__C4r0l_Blum`}`
```
