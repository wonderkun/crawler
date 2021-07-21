> 原文链接: https://www.anquanke.com//post/id/213821 


# 密码学学习笔记之Coppersmith’s Method （三）


                                阅读量   
                                **138057**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0110d6ccbdc9cef92e.jpg)](https://p2.ssl.qhimg.com/t0110d6ccbdc9cef92e.jpg)



单元coppersmith’s method 学习最终章，详解 第三届强网杯 之copper study，【这一波，这一波是首尾呼应。】

### <a class="reference-link" name="%E7%AC%AC%E4%B8%80%E5%85%B3%EF%BC%9AStereotyped%20messages"></a>第一关：Stereotyped messages

已知n,e=3,c，m共512bit但是低72bit未知，原理可参考[Mathematics of Public Key Cryptography ch19](https://www.math.auckland.ac.nz/~sgal018/crypto-book/ch19.pdf)。也即前文所述。

```
[+]Generating challenge 1
[+]n=0x44e360ce873d18d33eecc0829eb0801e71950e26576963c470f91f4c5e7f3e951f65404c6a87f4328495c9c64d39271f3317081aeab34bdf350c5f9bf0c5a49668f763cbf404e66f210336042c6a6e43eed6c6eaca69287ed91b2841148668fd3881b241317574cc8b307fb41593ff7caaa6f09e32f657399c63fe5f68995c5dL
[+]e=3
[+]m=random.getrandbits(512)
[+]c=pow(m,e,n)=0x20d40eecc8108d6c57b0ea2e1d7d165fb342813764f3760baf71e7929e3c22476de15b5e665ff8b869b5ed3a672aad4e9ef330bb7e18329ce2d0cccae369e244002882a273d3bf5a13b8936974768a920f5cbee52d0bb0323f867ff6305c5aa7ceb99453172332cd9837fdb05d6ea2d7eac39fd0d39960dc9ddbdd40f82b444bL
[+]((m&gt;&gt;72)&lt;&lt;72)=0x5377a12cada023e2714b4a9e80f1da87ca567f084e2862e704b813cd7f69b8dbbf67d60e73610fabb7896eeb3cc5a2c0915d03f9f8d44d000000000000000000L
[-]long_to_bytes(m).encode('hex')=
```

这道题我们完全可以将题面转化为在求方程f(x) = (m+x)^3 在模N下的解

所以可以直接套我们前面所描述的方法

exp:

```
# 展示格的样式
def matrix_overview(B, bound):
    for ii in range(B.dimensions()[0]):
        a = ('%02d ' % ii)
        for jj in range(B.dimensions()[1]):
            a += '0' if B[ii,jj] == 0 else 'X'
            a += ' '
        if B[ii, ii] &gt;= bound:
            a += '~'
        print (a)

def coppersmith(pol, modulus, h, X):
    # 计算矩阵维度
    n = d * h

    # 将多项式转到整数环上
    polZ = pol.change_ring(ZZ)
    x = polZ.parent().gen()

    # 构造上文所述lattice，polZ(x * X) 就是环上的多项式f(X * x)，所以这里与上文不同的点就在于引入了变量x，但变量x在后面的矩阵构造中会被抹掉。
    g = []
    for i in range(h):
        for j in range(d):
            g.append((x * X)**j * modulus**(h - 1 - i) * polZ(x * X)**i)

    B = Matrix(ZZ, n)
    for i in range(n):
        for j in range(i+1):
            B[i, j] = g[i][j]

    # 展示格的样式
    matrix_overview(B,modulus^h)
    # LLL算法
    B = B.LLL()

    # 将最短向量转化为多项式，并且去除相应的X
    new_pol = 0
    for i in range(n):
        new_pol += x**i * B[0, i] / X**i

    # 解方程
    potential_roots = new_pol.roots()
    return potential_roots


N =
e =
c =
m =
ZmodN = Zmod(N)
P.&lt;x&gt; = PolynomialRing(ZmodN)
f = (m + x)^e - c
epsilon = 1 / 7

# 根据公式计算参数d、h、X
d = f.degree()
h = ceil(1 / (d * epsilon)) 
X = ceil(N**((1/d) - epsilon))

roots = (coppersmith(f, N, d, h, X))[0]
for root in roots:
    if (m + root)^e %N  == c %N :
        print(m + root)
```

构造的格的样式

[![](https://i.loli.net/2020/08/09/ItTcgQlP9pSw3Jo.png)](https://i.loli.net/2020/08/09/ItTcgQlP9pSw3Jo.png)

与example3 构造的格是类似的

[![](https://i.loli.net/2020/08/12/cbHeKPhiruBNAO4.png)](https://i.loli.net/2020/08/12/cbHeKPhiruBNAO4.png)

但其实sage已经集成了coppersmith的求根方法，因此简单调用一下函数就可以解决这个问题。这里之所以这样做其实是想映照前文，展示一下利用coppersmith来解决此类问题的整个过程。

利用现成方法版exp

```
N =
e =
c =
m =

ZmodN = Zmod(N)
P.&lt;x&gt; = PolynomialRing(ZmodN)
f = (m + x)^e - c
x0 = f.small_roots(X=2^kbits, beta=1)[0]  # 这里的X选取不像上文用的是临界值，而是选了一个我们未知的x的最大可能值。X的选取并非严格，但至少得保证比临界值小。
print("m:", m + x0)
```

BTW，这里泄露的是明文的高位，其实还有泄露低位、泄露高低位的情况。但换汤不换药，无非是由m+x变成了 m_high +x * 2^k + m_low。

### <a class="reference-link" name="%E7%AC%AC%E4%BA%8C%E5%85%B3%EF%BC%9AFactoring%20with%20high%20bits%20known"></a>第二关：Factoring with high bits known

已知n,e,c，n=pq且已知p的高位

```
[+]Generating challenge 2
[+]n=0x5fe2743ec99568d645943147498849643932486590fb101f41c93ad7247161bc035d75dfb9e4b25209e26913098ecc1b7c4a92a47fb28452465d8b94e31844c4624da870140a48a28a0e6a3c6d9731b8488a63fd8ab9f5fe1ae86513c7444bb0aa39d44416b9cfa83c370f50c7a5a148a36823f0ddeed66ecf99117378c0640fL
[+]e=65537
[+]m=random.getrandbits(512)
[+]c=pow(m,e,n)=0x2639582bf7b22fd52a7a519673574e1212b675c9c10763ffcbcf5a86b61f07c4ea536e48dfbd4f3201cb2e18f2a0946959223b3f32bd5b3166d6cdd185ad946e543504dcc42ac9a24c03343bc8e4379997c722b12c66acaed6ad64d35f2fbcc8f4d899c1081d4211987841d1be082801a07014de89050b71e584827020934755L
[+]((p&gt;&gt;128)&lt;&lt;128)=0xe4f16417011e6cc5ced2aad00d5865a0530f37c078dd22d942d0d0811c7053d973b621c4768a2a87a6d233be10db8e1a00000000000000000000000000000000L
[-]long_to_bytes(m).encode('hex')=
```

这一关我们需要引入一个新的定理

#### <a class="reference-link" name="Theorem%203"></a>Theorem 3

[![](https://i.loli.net/2020/08/12/P2kHyAOTtYg1rFu.png)](https://i.loli.net/2020/08/12/P2kHyAOTtYg1rFu.png)

这里我就不再给出令人头大的证明了。直接给出一个例子，但是显然，由于条件的改变，这个格子的构造也会与之前的格子不同。

#### <a class="reference-link" name="example%204"></a>example 4

设N=16803551，p’=2830 ， X=10

我们设F(x)=(x+p’)，并且考虑多项式：N, F(x)，xF(x)=(x^2 + p’x)，x^2F(x)。然后构造格

[![](https://i.loli.net/2020/08/12/hxAuOgyf7UiXzam.png)](https://i.loli.net/2020/08/12/hxAuOgyf7UiXzam.png)

LLL规约后得到第一行的SVP为（105，-1200，800，1000），去除X可以得到

G(x) = x^3 + 8x^2 – 120*x + 105；解方程可以得到x = 7，检查一下确实 2387|N

【这里的N也许显得突兀，把它看作是k * p也许会好理解些：所选取的多项式带入正解x时均在模p下与0同余。】

除了这样构造格子，通过查阅网上关于这道题的题解可以发现另一种格子的构造。我们这里是“x-shift”了三次，另外那种是先提升次数，然后再“x-shift”，具体用了这八个多项式：

[![](https://i.loli.net/2020/08/12/j97RCwdiBr48P2z.png)](https://i.loli.net/2020/08/12/j97RCwdiBr48P2z.png)

格子的样式：

[![](https://i.loli.net/2020/08/11/voZQpe9TkdKnRNm.png)](https://i.loli.net/2020/08/11/voZQpe9TkdKnRNm.png)

之所以这么选也是这里新引入了两个参数，一个是beta，一个是t，beta是未知p与已知N指数关系，这里就是0.4，因为p ≈ N^0.4，【其实可以是0.5，但我们并不确定p, q的大小关系，保险起见用0.4】t的具体取值与beta相关，另外这里的h的取值也与beta有关，X的取值也与上面的定理所述不同。

exp

```
# 展示格的样式
def matrix_overview(B, bound):
    for ii in range(B.dimensions()[0]):
        a = ('%02d ' % ii)
        for jj in range(B.dimensions()[1]):
            a += '0' if B[ii,jj] == 0 else 'X'
            a += ' '
        if B[ii, ii] &gt;= bound:
            a += '~'
        print (a)

def coppersmith(pol, modulus, beta, h, t, X):
    # 计算矩阵维度
    n = d * h + t

    # 将多项式转到整数环上
    polZ = pol.change_ring(ZZ)
    x = polZ.parent().gen()

    # 构造上文所述lattice，polZ(x * X) 就是环上的多项式f(X * x)，所以这里与上文不同的点就在于引入了变量x，但变量x在后面的矩阵构造中会被抹掉。
    g = []
    for i in range(h):
        for j in range(d):
            g.append((x * X)**j * modulus**(h - i) * polZ(x * X)**i)
    for i in range(t):
        g.append((x * X)**i * polZ(x * X)**h)
    # 构造格B
    B = Matrix(ZZ, n)

    for i in range(n):
        for j in range(i+1):
            B[i, j] = g[i][j]
    # 展示格的样式
    matrix_overview(B, modulus^h)

    # LLL
    B = B.LLL()

    # 将最短向量转化为多项式，并且去除相应的X 
    new_pol = 0
    for i in range(n):
        new_pol += x**i * B[0, i] / X**i

    # 解方程
    potential_roots = new_pol.roots()

    # 检查根
    roots = []
    for root in potential_roots:
        if root[0].is_integer():
            result = polZ(ZZ(root[0]))
            if gcd(modulus, result) &gt;= modulus^beta:
                print("p: ",(gcd(modulus, result)))
                roots.append(ZZ(root[0]))

    return roots

N = 
ZmodN = Zmod(N)
P.&lt;x&gt; = PolynomialRing(ZmodN)
pbar = 
f = pbar + x
beta = 0.4
d = f.degree()
epsilon = beta / 7
h = ceil(beta**2 / (d * epsilon))
t = floor(d * h * ((1/beta) - 1))
X = ceil(N**((beta**2/d) - epsilon)) 
roots = coppersmith(f, N, beta, h, t, X)
```

这个脚本其实也可以用在第一关，只要将beta改成1，再带入相应的多项式和数据就可以了。

相关的paper和原脚本在[github](https://github.com/mimoo/RSA-and-LLL-attacks/)，有兴趣的师傅可以研究研究。

同样，利用现成函数版exp

```
N = 
pbar = 
ZmodN = Zmod(N)
P.&lt;x&gt; = PolynomialRing(ZmodN)
f = pbar + x
x0 = f.small_roots(X=2^kbits, beta=0.4)
p =  pbar + x0
print("p: ", p)
```

BTW，同第一关一样，这里的p泄露了高位，但与p泄露了低位的情况，无差。

### <a class="reference-link" name="%E7%AC%AC%E4%B8%89%E5%85%B3%EF%BC%9APartial%20Key%20Exposure%20Attack"></a>第三关：Partial Key Exposure Attack

已知n,e=3,c，d的低512bit已知 【n的长度为1023】

```
[+]Generating challenge 3
[+]n=0x6f209521a941ddde2294745f53711ae6a7a59aa4d0735f47328ac03e26a4e092bb1c4c885029950f52b1e071597dc6e6d5129afbdb4688ad0479d6f9655dafef915da0a3f5114989cb474a13a9a4a4293fd447739b3cc2b0a3966f21617f057e6c199c5fd4d11ce78fdf9112f53446578b6cfd2c405eb0d3389cd3965636f719L
[+]e=3
[+]m=random.getrandbits(512)
[+]c=pow(m,e,n)=0x6126eaf34233341016966d50c54c6f7401e98f2015bcbdc4d56f93f0c48590fcd8ee784521c503be322c0848f998dc3a6d630bc1043a4162467c4b069b6c0e186061ed2187d0b2d44e9797ce62569d2dab58d183d69b9d110369a8d690361b22223e34e65e51868646d0ebf697b10e21a97d028833719e87c1584d2564f21167L
[+]d=invmod(e,(p-1)*(q-1))
[+]d&amp;((1&lt;&lt;512)-1)=0x1d8f1499c4f6d90716d89f76833823e8fca4dd4034f17157e4fd9f6f070e1526f3b4fa3fe507d645ec848e4d7ff3728eb8df04b72849feabaa3425f9fc510ec3L
[-]long_to_bytes(m).encode('hex')=
```

[![](https://i.loli.net/2020/08/12/MufOqcXlogCQsDk.png)](https://i.loli.net/2020/08/12/MufOqcXlogCQsDk.png)

exp

```
def recover_p(p0, n):
    PR.&lt;x&gt; = PolynomialRing(Zmod(n))
    nbits = n.nbits()
    p0bits = p0.nbits()
    f = 2^p0bits*x + p0
    f = f.monic()
    roots = f.small_roots(X=2^(nbits//2-p0bits), beta=0.4)  
    if roots:
        x0 = roots[0]
        p = gcd(2^d0bits*x0 + p0, n)
        return ZZ(p)


def find_p0(d0, e, n):
    X = var('X')
    for k in range(1, e+1):
        results = solve_mod([e*d0*X == k*n*X + k*X + X-k*X**2 - k*n], 2^d0.nbits())
        for x in results:
            p0 = ZZ(x[0])
            p = recover_p(p0, n)
            if p and p != 1:
                return p


n =
e = 
c =
d0 =
p = int(find_p0(d0, e, n))
print("found p: ", p)
q = n//int(p)
print("found d: ", inverse_mod(e, (p-1)*(q-1)))
```

### <a class="reference-link" name="%E7%AC%AC%E5%9B%9B%E5%85%B3%EF%BC%9AHastad%E2%80%99s%20Broadcast%20Attack"></a>第四关：Hastad’s Broadcast Attack

已知n1,c1,n2,c2,n3,c3,e=3

```
[+]Generating challenge 4
[+]e=3
[+]m=random.getrandbits(512)
[+]n1=0x1819da5abb8b8158ad6c834cb8fd6bc3ed9a3bd3e33b976344173f1766bf909bda253f18c9d9640570152707e493e3d3d461becc7197367ab702af33d67805e938321915f439e33f616b41781c54c101f05db0760cc8ca0f09063f3142b5b31f6aa062f1e60bba1a45e3720ab462ebd31e1228f5c49ae3de8172bad77b2d5b57L
[+]c1=pow(m,e,n1)=0x7841e1b22f4d571b722807007dc1d550a1970a32801c4649e83f4b99a01f70815b3952a34eadc1ec8ba112be840e81822f1c464b1bb4b24b168e5cb38016469548c5afd8c1bdb55402d1208f3201a2a4098aef305a8380b8c5b6b5b17d9fb65a6bdfdcf21abc063924a6512f18f1dc22332dfc87f4a00925daf1988d43aaecdL
[+]n2=0x6d1164ffa8cb2b7818b5ac90ef121b94e38fd5f93636b212184717779c45581f13c596631b23781de82417f9c8126be4a04ab52a508397f9318c713e65d08961d172f24f877f48ef9e468e52e3b5b17cbbe81646903d650f703c51f2ad0928dd958700b939e1fd7f590f26a6d637bd9ef265d027e7364c4e5e40a172ce970021L
[+]c2=pow(m,e,n2)=0x58f26614932924c81d30ef2389d00cf2115652ced08d59e51619207a7836fd3908b3179fc0df03fe610059c1fe001ca421e01e96afc47147d77bbbe6a3f51c5c06f1baeab8dc245c2567a603f87dea0a053b8f5df4e68f28896d7d1ba3dd3dcd7c4652d59404fa237f4868e1bbc9ae529196739486d86bd1723a78dfac781fe5L
[+]n3=0xde53be1db600264b0c3511ae4939c82164ea1166aadfd8dd0af6e15eb9df79a5d1a2757d3d15630441790ecf834098a1cf4b5858003f0b7f3a72823de014ac0a7c827ed1ca4185b245774f442a05dee3fe6bf846e5b035caf3b3c574b88911b7e5b81fc2c638729240f949e09a25a3a4a762c31005684791577d5e9fc8221abdL
[+]c3=pow(m,e,n3)=0x89f9fabc7e8d6f0e92d31109ea4c024446b323d9f441d72db4eb296eba3011abe2a58e68ec21a663e6493981e21835a826f28d1bc28d3476273ff733ef69c152e7fbfebc826132266f6eb65c86b242417c06eb31453f99ed7e075ababbfc208d042a2436a766f24eb9af0f45b60eea2c4405edfabd87584806bc0a1a51f9ca7aL
[-]long_to_bytes(m).encode('hex')=
```

对于这一关，由于我们知道m是512bit的，而用于加密的e=3，因此三个c即为m^3 在不同模下的剩余。由于m^3为512 * 3=1536bit，而可以知道的是三个模n的bit长度分别为1021，1023，1024。所以利用中国剩余定理【具体原理可以看俺这一篇[文章](https://www.anquanke.com/post/id/194137)】我们是可以还原长度为1536bit的m^3的，最后我们再开个三次根就好得到m了。

exp

```
from gmpy2 import *

def CRT(mi, ai):
    assert (reduce(gcd,mi)==1)
    assert (isinstance(mi, list) and isinstance(ai, list))
    M = reduce(lambda x, y: x * y, mi)
    ai_ti_Mi = [a * (M / m) * invert(M / m, m) for (m, a) in zip(mi, ai)]
    return reduce(lambda x, y: x + y, ai_ti_Mi) % M

print iroot(CRT([n1,n2,n3],[c1,c2,c3]),3)
```

[![](https://i.loli.net/2020/08/12/IlJmynB1Cqjho5t.png)](https://i.loli.net/2020/08/12/IlJmynB1Cqjho5t.png)

exp来自[食兔人的博客——CTF中的RSA基本套路](https://ycdxsb.cn/2decc525.html)

```
Cs = []
Ns =  []
A=  [1, 1, 2]
B= [0, 1, 2]
e= 3

# solve
cnt = e
PR.&lt;x&gt; = PolynomialRing(ZZ)
x = PR.gen()
Fs = []
for i in range(cnt):
    f =  (A[i]*x + B[i])**e - Cs[i]
    ff = f.change_ring(Zmod(Ns[i]))
    ff = ff.monic()
    f = ff.change_ring(ZZ)
    Fs.append(f)

F = crt(Fs, Ns)
M = reduce( lambda x, y: x * y, Ns )
FF = F.change_ring(Zmod(M))
m = FF.small_roots()
print("m: ",m)
```

### <a class="reference-link" name="%E7%AC%AC%E4%BA%94%E5%85%B3%EF%BC%9ARelated%20Message%20Attack"></a>第五关：Related Message Attack

已知n,e=3，m对应的密文c1，(m+1)对应的密文c2

```
[+]Generating challenge 5
[+]n=0xf2e5339236455e2bc1b1bd12e45b9341a3b223ddb02dec11c880fa4aa8835df9e463e4c446292cd5a2fe19b10017856654b6d6c3f3a94a95807712329f7dae2e1e6506094d5d2f9c8a05c35cbf3366330996db9bff930fe566016d5e850e232057d419292ce30df9c135d56ef1bb72c38838d4b127aa577ceb4aba94d4e0d55L
[+]e=3
[+]m=random.getrandbits(512)
[+]c=pow(m,e,n)=0x7175f2614b8d1a27b43f7c3873b3422658af28291ddc88b15f97f499e00cd4c5c4fd980f062376a61e5dd4c15d52d73262d3c066f1e8f46a04af6fead7c3960d2768a0d214bbc3e05d2f6e56aee158071574e55753624a19e094590fc3f9918a2065cd5ff7693e0d34517bc0072e6c9e444e66c4ece88d657f99e44bee48924L
[+]x=pow(m+1,e,n)=0xd5f4af36b5391bd731cfa4313466024ab1bc3b455024a5d8b218faba0e956252f01c4d01bd36765035c33d73e5af7f178aeb2606edf86814d74082c64828fa4c1666b69d05fab69dd1ef47b243356290fdb74e001f54edec70681cf52319c73bce9acda4803a9e97597ca21d60072c2d2b516f161bec1f6a91baa2e24c7655bL
[-]long_to_bytes(m).encode('hex')=
```

同第四关一样，这一题也有多解，一种是像一叶飘零师傅[这篇文章](https://www.anquanke.com/post/id/158944)所述，直接硬化公式

exp

```
import gmpy
def getM2(a,b,c1,c2,n):
    a3 = pow(a,3,n)
    b3 = pow(b,3,n)
    first = c1-a3*c2+2*b3
    first = first % n
    second = 3*b*(a3*c2-b3)
    second = second % n
    third = second*gmpy.invert(first,n)
    third = third % n
    fourth = (third+b)*gmpy.invert(a,n)
    return fourth % n

a = 1
b = -1
c1 =
c2 =
n =
m = a*getM2(a,b,c1,c2,n) + b
print hex(m)
```

[![](https://i.loli.net/2020/08/12/loLPRnbDa7MuwmG.png)](https://i.loli.net/2020/08/12/loLPRnbDa7MuwmG.png)

exp

```
def franklinReiter(n,e,b,c1,c2):
    R.&lt;X&gt; = Zmod(n)[]
    f1 = X^e - c1
    f2 = (X + b)^e - c2
    m_ = GCD(f1,f2).coefficients()[0] # 返回的是首一多项式，coefficients()返回多项式各项式的系数，项式次数递增，所以第0项是常数 
    return Integer(n - m_) # 由于tmp其实是 -m % n,所以这里给他转换回去。

def GCD(a, b):
    if(b == 0):
        return a.monic()        # 返回首一多项式，即多项式最高次的项式系数为1
    else:
        return GCD(b, a % b)
e = 
n = 
b = 
c1 = 
c2 = 
M = franklinReiter(n,e,b,c1,c2)
print(M)
```

### <a class="reference-link" name="%E7%AC%AC%E5%85%AD%E5%85%B3%EF%BC%9ABoneh%20Durfee%20Attack"></a>第六关：Boneh Durfee Attack

已知n,e,c，d只有1024 * 0.27bit

```
[+]Generating challenge 6
[+]n=0xbadd260d14ea665b62e7d2e634f20a6382ac369cd44017305b69cf3a2694667ee651acded7085e0757d169b090f29f3f86fec255746674ffa8a6a3e1c9e1861003eb39f82cf74d84cc18e345f60865f998b33fc182a1a4ffa71f5ae48a1b5cb4c5f154b0997dc9b001e441815ce59c6c825f064fdca678858758dc2cebbc4d27L
[+]d=random.getrandbits(1024*0.270)
[+]e=invmod(d,phin)
[+]hex(e)=0x11722b54dd6f3ad9ce81da6f6ecb0acaf2cbc3885841d08b32abc0672d1a7293f9856db8f9407dc05f6f373a2d9246752a7cc7b1b6923f1827adfaeefc811e6e5989cce9f00897cfc1fc57987cce4862b5343bc8e91ddf2bd9e23aea9316a69f28f407cfe324d546a7dde13eb0bd052f694aefe8ec0f5298800277dbab4a33bbL
[+]m=random.getrandbits(512)
[+]c=pow(m,e,n)=0xe3505f41ec936cf6bd8ae344bfec85746dc7d87a5943b3a7136482dd7b980f68f52c887585d1c7ca099310c4da2f70d4d5345d3641428797030177da6cc0d41e7b28d0abce694157c611697df8d0add3d900c00f778ac3428f341f47ecc4d868c6c5de0724b0c3403296d84f26736aa66f7905d498fa1862ca59e97f8f866cL
[-]long_to_bytes(m).encode('hex')=
```

[![](https://i.loli.net/2020/08/12/HmEQruygD9Ia1ks.png)](https://i.loli.net/2020/08/12/HmEQruygD9Ia1ks.png)

但具体怎么去求解这个方程呢？这就涉及多元coppersmith’s method了，超纲了吖，所以这里先用了github上的一个脚本[boneh_durfee.sage](https://github.com/mimoo/RSA-and-LLL-attacks/blob/master/boneh_durfee.sage)。这里的适用条件是d &lt; N^0.292​



# <a class="reference-link" name="%E6%80%9D%E8%80%83&amp;%E6%80%BB%E7%BB%93"></a>思考&amp;总结

在coppersmith’s method的边界计算中，由于推理中存在的不等式，格基规约算法在不同情况有不同的表现等问题，导致coppersmith’s method的边界其实比较模糊，而构造不同的格也会计算出不同的边界值，有不同的效果。所以，在考虑时间和空间复杂度的情况下，是否会存在某种最优的构造方法呢？

好了，这里大概是大部分的对单元coppersmith’s method的应用实例了。最后一手Boneh Durfee Attack利用了多元coppersmith‘s method，这算是埋了一手伏笔么？
