> 原文链接: https://www.anquanke.com//post/id/194232 


# 密码学学习笔记：浅析On r-th Root Extraction Algorithm in Fq


                                阅读量   
                                **1189286**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01458109cbd59db885.jpg)](https://p2.ssl.qhimg.com/t01458109cbd59db885.jpg)



## 前言：

在NCTF上遇到了一道出题人用来压轴的RSA，与正常RSA加密不同的是，本题的e是φ(p)和φ(q)的一个因子。在出题人给出hint后，我找到了一篇paper，侥幸用paper中提到的算法拿到了一血~

该算法可以在有限域Fq中开r次根，但需要s，满足r^s整除q-1，即r^s | q-1，并且s要小。



## On r-th Root Extraction Algorithm in Fq

paper： https://eprint.iacr.org/2013/117.pdf

### <a name="header-n209"></a>引言：

我们让r为一个大于1的整数，那么有现存的两种算法用来在有限域Fq中开r^s次根， the Adleman-Manders-Miller algorithm 和 the Cipolla-Lehmer algorithms

假设r&lt;&lt;log q ，由于 the Adleman-Manders-Miller algorithm 要求s满足 r^s | q-1 并且 r^(s+1) 不能整除 q-1，所以它的时间复杂度O(logrlog4 q) 比 the Cipolla-Lehmer algorithms 的时间复杂度O(rlog3 q) 要高。但是，由于Cipolla Lehmer需要繁琐的扩展字段算法，当s比较小时，the Adleman-Manders-Miller algorithm 要比之更为有效。

另一方面，在某些情况下还存在比 Tonelli-Shanks 计算更快的其他方法来做开方运算。例子就是当 q ≡ 3 (mod 4).

当c时Fq中的二次剩余时，c的其中一个根就是[![](https://p1.ssl.qhimg.com/t011db81eafd6408a31.png)](https://p1.ssl.qhimg.com/t011db81eafd6408a31.png)，利用欧拓很容易证明[![](https://p4.ssl.qhimg.com/t01b3f2177e52bc32f4.png)](https://p4.ssl.qhimg.com/t01b3f2177e52bc32f4.png)

当s=2，3时，也有类似的方法， Atkin , Mu¨ller and Kong et al ，他们的方法在这种情况下， 要比Tonelli-Shanks and the Cipolla-Lehmer 表现得更为出色。

[![](https://p1.ssl.qhimg.com/t01906fc951b1289973.png)](https://p1.ssl.qhimg.com/t01906fc951b1289973.png)

但是作者认为这些方法不能很好的解决普遍的情况，所以作者展示了一种，新的开根的方法，只用一个预计算好的基元，一次指数运算，并且在s很小的时候十分高效。

### <a name="header-n16"></a>开二次根算法：

有一些高效的公式，分别当 q ≡ 5 (mod 8) ，或者 q ≡ 9 (mod 16) 。如果q ≡ 5 (mod 8) ，属于 q ≡ 1 (mod 4), 的一种特殊情况， Atkin 有一种只进行一次指数运算的高效的公式。

##### <a name="header-n18"></a>Algorithm 1 Atkin’s algorithm when q ≡ 5 (mod 8)

方程，x^2 = a mod (q)，已知a，求x

[![](https://p1.ssl.qhimg.com/t010ba1ad3d51a34962.png)](https://p1.ssl.qhimg.com/t010ba1ad3d51a34962.png)

##### <a name="header-n21"></a>Algorithm 2 Mu¨ller’s algorithm when q ≡ 9 (mod 16)

方程，x^2 = a mod (q)，已知a，求x

[![](https://p5.ssl.qhimg.com/t0141cb23556448ed06.png)](https://p5.ssl.qhimg.com/t0141cb23556448ed06.png)

其中第二步有个神奇的东西 η(d) ，paper中给的定义是

[![](https://p1.ssl.qhimg.com/t013f7baceaaea901cc.png)](https://p1.ssl.qhimg.com/t013f7baceaaea901cc.png)

，然鹅想不出怎么让它等于-b，（还求大师傅们指点~）

### <a name="header-n27"></a>在有限域中 Fq 开 r^s 根 [ q ≡ lr^s + 1 (mod r^(s+1)) ]

首先我们需要一个质数q，并且有一个r，满足 r | (q-1)，（如果r与q-1互质，那问题就很简单了，r的逆用欧拓很快就能找到）然后会存在一个s，s是满足[![](https://p2.ssl.qhimg.com/t011ec4ae30a0a69848.png)](https://p2.ssl.qhimg.com/t011ec4ae30a0a69848.png)的最大的正整数

即会满足[![](https://p3.ssl.qhimg.com/t0117ac1d4612a11106.png)](https://p3.ssl.qhimg.com/t0117ac1d4612a11106.png)

#### <a name="header-n30"></a>定理1：在域Fq中，给定一个r次幂c，存在一个b，使得c^(r-1)·b^r 具有r^t阶，（t&lt;s）

##### <a name="header-n31"></a>证明：

我们设一个l，满足gcd(l,r)=1,那么存在β (0≤β&lt;l)，满足 rβ+r−1 ≡ 0 (mod l) 即存在α，满足 rβ + r−1 = lα.

然后，我们设一个 ζ 为，[![](https://p2.ssl.qhimg.com/t0174dfb665065d5a9c.png)](https://p2.ssl.qhimg.com/t0174dfb665065d5a9c.png)

则有[![](https://p4.ssl.qhimg.com/t01323fd852fd2da8cc.png)](https://p4.ssl.qhimg.com/t01323fd852fd2da8cc.png)



其中，[![](https://p3.ssl.qhimg.com/t0174a4a9dce462202e.png)](https://p3.ssl.qhimg.com/t0174a4a9dce462202e.png)

因为c是域Fq中的r次幂，故ζ拥有r^t阶，(0≤t&lt;s) （为啥这里t就小于s了，求指点~）

##### <a name="header-n38"></a>利用：

在域Fq中，我们令 ξ 为 一个r^2阶本原单位根，ξ可以通过公式[![](https://p3.ssl.qhimg.com/t014fda793616d46a6c.png)](https://p3.ssl.qhimg.com/t014fda793616d46a6c.png)计算得到，其中d为域Fq中的非r次幂，这样的d可以随机选取，在域Fq中找到它的概率为(r-1)/r

由此，我们设[![](https://p4.ssl.qhimg.com/t01e51b582a465b8d48.png)](https://p4.ssl.qhimg.com/t01e51b582a465b8d48.png)是一个r^t阶的本原单位根，则存在一对唯一确定的i，j满足[![](https://p1.ssl.qhimg.com/t0134eabfc1d19347fb.png)](https://p1.ssl.qhimg.com/t0134eabfc1d19347fb.png)

因为[![](https://p0.ssl.qhimg.com/t014b728e9ee5bfe928.png)](https://p0.ssl.qhimg.com/t014b728e9ee5bfe928.png)

所以我们有[![](https://p1.ssl.qhimg.com/t0190b864f87de0026c.png)](https://p1.ssl.qhimg.com/t0190b864f87de0026c.png)

由此我们将展现一个新的定理，在合适的情况下，我们用一次指数运算可以找到r次剩余的一个r次根，

#### <a name="header-n44"></a>定理2：定义u ≡ j·(r^t −1)·r^(s−t−1 ) ≡−jr^(s−t−1) (mod r^(s−1)). 那么在域Fq中c的一个r次根为 cbξ^u ，其中b在定理1中给出。

##### <a name="header-n45"></a>证明：

[![](https://p0.ssl.qhimg.com/t01a689b7c865d0186e.png)](https://p0.ssl.qhimg.com/t01a689b7c865d0186e.png)

（由于[![](https://p2.ssl.qhimg.com/t01f7b3a38896da2c7f.png)](https://p2.ssl.qhimg.com/t01f7b3a38896da2c7f.png)，由费马小定理，故在域Fq中[![](https://p3.ssl.qhimg.com/t0169855b250cf60e5f.png)](https://p3.ssl.qhimg.com/t0169855b250cf60e5f.png) 易证，）

证毕。

注1： rβ + r −1 = lα 即 r(β + l) + r −1 = l(α + r)。这说明，α （mod r ）是确定的，β（mod l）是确定的，所以对于任意的α 满足[![](https://p3.ssl.qhimg.com/t0147af86893696e692.png)](https://p3.ssl.qhimg.com/t0147af86893696e692.png) ,都有唯一确定的β满足[![](https://p1.ssl.qhimg.com/t015c05424ac7993951.png)](https://p1.ssl.qhimg.com/t015c05424ac7993951.png) 。作者在这里还加了一句，事实上，条件rβ + r−1−lα = 0 可以转化为 rβ + r−1−lα ≡ 0 (mod (q-1)/r） 因为 [![](https://p5.ssl.qhimg.com/t019a62bc7d900c3be8.png)](https://p5.ssl.qhimg.com/t019a62bc7d900c3be8.png)（难道是欧拉判别定理的推广？）

注2：cb的值可以化成

[![](https://p2.ssl.qhimg.com/t01f8eea6b95c9f59d5.png)](https://p2.ssl.qhimg.com/t01f8eea6b95c9f59d5.png)

其中α是一个整数（0&lt;α&lt;r），满足[![](https://p5.ssl.qhimg.com/t010e926fe5198626d2.png)](https://p5.ssl.qhimg.com/t010e926fe5198626d2.png)所以b也可以表示为[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01db721dd7cb11ff28.png)

注3：对于 ij ≡ 1 (mod r^t) ，当r^t很大（t&gt;1 并且在r^t阶循环群中的离散对数很难处理）时，其中的i和j找起来是比较困难的，所以这个方法适合在r和t都比较小的时候，也可以被视作是另一个版本的Adleman-Manders-Miller algorithm。

#### <a name="header-n59"></a>举例与算法

终于到实例环节了~

##### <a name="header-n62"></a>例1 q ≡ lr + 1 (mod r^2) 0 &lt; l &lt; r:

在这种情况下，s=1,所以t=u=0，所以r次根c可以表示为cbξ^u = cb = [![](https://p5.ssl.qhimg.com/t01fa6db78a4b0d7ab9.png)](https://p5.ssl.qhimg.com/t01fa6db78a4b0d7ab9.png)其中α需要满足[![](https://p3.ssl.qhimg.com/t0164ddc975baf71373.png)](https://p3.ssl.qhimg.com/t0164ddc975baf71373.png)

当r = 2，s=1就意味着， q ≡ 3 (mod 4) ，α在这里可以算出是1，带入公式，c的一个二次根就是众所周知的[![](https://p2.ssl.qhimg.com/t01a24f3c1fee00fc8f.png)](https://p2.ssl.qhimg.com/t01a24f3c1fee00fc8f.png) ，（Rabin解密~）

当r = 3，s=1 就意味着 q ≡ 4 (mod 9) 或者 q ≡ 7 (mod 9) ，先算出α，然后带入公式[![](https://p4.ssl.qhimg.com/t0151852b3421c3e54c.png)](https://p4.ssl.qhimg.com/t0151852b3421c3e54c.png)，（当 q ≡ 4 (mod 9）

或是[![](https://p2.ssl.qhimg.com/t0199089bd6b28c0c60.png)](https://p2.ssl.qhimg.com/t0199089bd6b28c0c60.png)（当 q ≡ 7 (mod 9)）

这里有个表

[![](https://p3.ssl.qhimg.com/t01564e804449562213.png)](https://p3.ssl.qhimg.com/t01564e804449562213.png)

最底下一样有例外，此时也就以为着r=0，r=0.还有啥根可开~

可见，当s=1时，在 q ≡ 1 (mod r) 并且 q !≡ 1 (mod r^2) 时，即q的(r-1) 种情况都可以借该公式进行一次指数运算就可开根，得到一个解。（推理过程一知半解的，但是结论用起来是真的香）

##### <a name="header-n75"></a>例2 q ≡ lr^2 + 1 (mod r^3) 0 &lt; l &lt; r:

当s=2.那么[![](https://p5.ssl.qhimg.com/t015ebf267d1c127691.png)](https://p5.ssl.qhimg.com/t015ebf267d1c127691.png)或者 是一个r阶本原单位根 （ζ是r^t阶，t=0 or 1），同时ξ也是一个r^2阶的本原单位根（原根）满足：[![](https://p4.ssl.qhimg.com/t01f11d8e7d12daad57.png)](https://p4.ssl.qhimg.com/t01f11d8e7d12daad57.png)即 [![](https://p2.ssl.qhimg.com/t017218d51881785591.png)](https://p2.ssl.qhimg.com/t017218d51881785591.png)。

因此，r次根可以表示为 cbξ^u ，具体的值上文已给，当t=0，u=0，x=cb是一个r次根，当t=1,u ≡−j (mod r) ，x= cbξ^−j是一个r次根。（所以我们还是希望t=0，这样计算就会极其方便~）

###### <a name="header-n87"></a>Algorithm 3 Our cube root algorithm when q ≡ 1 (mod 9) and q ̸≡ 1 (mod 27)

x^3=c (mod q) （ (q = 9l + 1 (mod 27) with l = 1,2, i.e., q ≡ 10,19 (mod 27)) ）

[![](https://p5.ssl.qhimg.com/t017ecaab6183082708.png)](https://p5.ssl.qhimg.com/t017ecaab6183082708.png)

解读一下：[![](https://p3.ssl.qhimg.com/t0148e488b8c2bf8d04.png)](https://p3.ssl.qhimg.com/t0148e488b8c2bf8d04.png)

，其中d在域Fq种不是一个r次幂（遍历一下，随便取一个就好）。

ζ=c^r−1·b^r = c^2·b^3=X^2b

如果，ζ=1，则说明t=0，那么x=cb=X

如果，ζ=B=ξ^r，那么t=j=1,x=cbξ^-j=cbξ^2=XA^2

否则，j=2,x=cbξ^-j=cbξ^-2=XA

验证：

[![](https://p2.ssl.qhimg.com/t0164918ab2cba46bb9.png)](https://p2.ssl.qhimg.com/t0164918ab2cba46bb9.png)

成功~

以下同

###### <a name="header-n93"></a>Algorithm 4 Our 5-th root algorithm when q ≡ 1 (mod 25) and q ̸≡ 1 (mod 125)

x^5=c (mod q)  (q = 25l + 1 (mod 125) with l = 1,2,3,4, i.e., q ≡ 26,51,76,101 (mod 125))

[![](https://p5.ssl.qhimg.com/t016441034e9f061c06.png)](https://p5.ssl.qhimg.com/t016441034e9f061c06.png)

##### <a name="header-n103"></a>例3 q ≡ lr^3 + 1 (mod r^4) 0 &lt; l &lt; r:

当s=3，[![](https://p3.ssl.qhimg.com/t01c92c2dad8daf1a13.png)](https://p3.ssl.qhimg.com/t01c92c2dad8daf1a13.png)有r^t阶（t=0,1,2），同时 ξ 是一个r^3 阶的原根 ，满足：[![](https://p5.ssl.qhimg.com/t01e1c660f779baa019.png)](https://p5.ssl.qhimg.com/t01e1c660f779baa019.png)

所以，c的r次根可以表示为cbξ^u，当t=0，u=0,x=cb即是c的一个r次根，当t=1，

u ≡ −jr (mod r^2), 当t=2， u ≡ −j (mod r^2),

计算过程类比上文，只是要考虑的（u）的情况增加到了r^2种。

### <a name="header-n136"></a>实战

回到开头说的NCTF crypto全场两解（大佬都去隔壁打D^3了~）的压轴——easyrsa

题目：（数字太大，就省去了）

```
from rsav import * 
 
e = 0x1337 
p =  
q =  
n = p * q 
 
 
''' 
assert(flag.startswith('NCTF')) 
m = int.from_bytes(flag.encode(), 'big') 
assert(m.bit_length() &gt; 1337) 
 
c = pow(m, e, n) 
print(c)''' 
c=
```

解题思路：

很普通的加密手段，然后p,q都给了，其中，e|q-1；e|p-1

唯一难点就在e是φ(n)的一个因子所以根本无法求出私钥d

第一步是类似rabin，先将m^e ≡ c (mod n)分解成同余式组

m^e ≡ c (mod p)

m^e ≡ c (mod q)

求出m1和m2，再用CRT就好了

至于m的求解，本题的条件正好符合上文的例1，

[![](https://p2.ssl.qhimg.com/t011b35c74f5815a78d.png)](https://p2.ssl.qhimg.com/t011b35c74f5815a78d.png)

于是我们先遍历出α，然后就可以求得m1了，

再算出另一个α，得到m2，然后CRT走一波，就可以出明文的一种情况了，

然而一共有e^2种情况

当e=2，rabin解密，有e^2种情况，因为同余方程组里的每一个方程都有两种情况。

当e=3，每个就有三种，CRT后一共就有3^2种

根据hint2，里面有提供当找到一种解后找到其余解的算法

[![](https://p5.ssl.qhimg.com/t018af6ee8adcf346f0.png)](https://p5.ssl.qhimg.com/t018af6ee8adcf346f0.png)

原理在这 https://crypto.stackexchange.com/questions/63614/finding-the-n-th-root-of-unity-in-a-finite-field

在有限域Fq中，乘法子群的阶为q-1，如果n不满足n|q-1，那么n次单位根只有1本身，如果n满足n|q-1，那么就有n个单位根。

由费马小定理[![](https://p5.ssl.qhimg.com/t012f8662cb397b0cf9.png)](https://p5.ssl.qhimg.com/t012f8662cb397b0cf9.png)

所以我们有n次单位根[![](https://p2.ssl.qhimg.com/t01e5b5af727cff287c.png)](https://p2.ssl.qhimg.com/t01e5b5af727cff287c.png)

当我们这个n次单位根不等于1时，我们就可以利用它和我们找到的一个根来生成一个阶为n的循环群，这个群里所有的元素即为我们想要的所有的根。

这样我们构造exp，遍历这0x1337*0x1337=24196561种可能，就能解出真正的密文了

```
import gmpy2 
 
def n2s(x): 
    try: 
        try: 
            flag = hex(x)[2:].decode("hex") 
        except: 
            flag = hex(x)[2:-1].decode("hex") 
    except: 
        flag='' 
    return flag 
 
def onemod(p,r): 
    t=p-2 
    while pow(t,(p-1)/r,p)==1: t-=1 
    return pow(t,(p-1)/r,p) 
 
def solution(p,root):  
    g=onemod(p,0x1337) 
    may=[] 
    for i in range(0x1337): 
        may.append(root*pow(g,i,p)%p) 
    return may 
 
c =  
 
p =  
 
q =  
e = 0x1337 
n = p*q 
 
c_p = pow(c,(1+3307*(p-1)/e)/e,p)  #p对应的α=3307 
print "find one" 
C1=solution(p,c_p)[::-1]   #逆序，问题不大，只是跑过一次，发现答案在两千多万次后 
print "find all" 
c_q = pow(c,(1+(2649*(q-1)/e))/e,q) #q对应的α=2649 
print "find another" 
C2=solution(q,c_q)[::-1] 
print "find all" 
a= gmpy2.invert(p,q) 
b = gmpy2.invert(q,p) 
#x = (b*q*c_p+a*p*c_q)%n 
flag=0 
for i in C1: 
    for j in C2: 
        flag+=1 
        if flag%1000000 == 0: 
            print flag 
        x = (b*q*i+a*p*j)%n 
        if "NCTF" in n2s(x): 
            print n2s(x) 
            exit(0)
```

[![](https://p1.ssl.qhimg.com/t0147db945bb8a9d6d3.png)](https://p1.ssl.qhimg.com/t0147db945bb8a9d6d3.png)



## 总结

这一次借NCTF了解了在域中开根的一种高效方法，这种方法似乎比出题人soreatu师傅的预期解还要高效~

并且有幸拿到了一个一血，不得不说，这公式，真香~

另外感谢这次NCTF，在这次密码学的赛题中学到了很多，另外一道childrsa也很有意思（有意思在我意外的发现了其中一个神奇规律23333）

最后再次感谢soreatu师傅制作的优质赛题以及赛后详细的wp与指点~
