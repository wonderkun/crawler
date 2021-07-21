> 原文链接: https://www.anquanke.com//post/id/197749 


# 分析TetCTF 2020中Crypto方向题目


                                阅读量   
                                **833869**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0112068f10f195ca56.jpg)](https://p0.ssl.qhimg.com/t0112068f10f195ca56.jpg)



## 前言

在TetCTF 2020中有5道Crypto方向的题目，题目难度适中，在这里对题目进行一下分析。



## 2019rearrange

题目描述如下：

Rearrange your 2019, keep your joy, throw all your sorrow away!

Files:[2019rearrange.zip](https://github.com/ichunqiu-resources/anquanke/blob/master/008/2019rearrange.zip)

分析一下源码，发现我们的任务是已知`n, e1, noise1, c1, e2, noise2, c2`参数的值，求m的值。其中：

```
c1 ≡ (m+noise1)^e1 (mod n)
c2 ≡ (m+noise2)^e2 (mod n)
```

我们考虑采用多项式的思想来解题，将上述两个方程看成多项式的形式，有：

```
f1(x) = (x+noise1)^e1 - c1
f2(x) = (x+noise2)^e2 - c2
```

显然，当`x=m`时，有：

```
f1(x) = f2(x) = 0
```

即`x = m`是多项式f1和f2的一个公共解，也即`f3 = gcd(f1,f2)`的一个公共解，因此我们只需要计算`gcd(f1,f2)`，即可得到关于m在模n意义下的多项式方程，从而求出m。

将上述推导写成SageMath代码形式如下：

```
from binascii import *

n = 99432613480939068351562426450736079548256649399824074125897023718511347184177748762719404609118999419018534660223144728190056735099787907299980625300234355248546050583144387977927309463501291854876892509630938617460690481497010165530214494306444999151252999850250583288798888278770654238342967653191171473013
e1, noise1, c1 = (9102, 42926763857648808452080305910241720054908809667539630194138718908195450776152522239791644645043372458139920503040529361726409749150633609223017012694569617522037971161448894459262110250322393703607247036022683527543284339763718964451482238661494995313111724858075982045508601405376724544741352142401794693054, 48276023282567629527195243870327301962656940680898728928903255577939008086657887592958073923577657060463242759606506812938152312008130198252498457257386413883443843887507528097024367788094619479032221547513746486475136282357337951126122694205225292004957793882304453164618423156810792171305978347365910972343)
e2, noise2, c2 = (2109, 51208643076502294588477225830948052764402322839126847164816681682357946991156728371602766970288519802146987999203830056494899211501025949997165558057140744445002699137286162872658309250096136525032077525028373299701055357023079519776378532002052890676446838318133048612893135724217301724754396467377231356425, 30644829500627448217295366947497931474953886995151259599263428251525601964766004111974074015504963773615137800165460045351514062357500899618814273135292073698096477339942069685331462828432407501524816375109607227118357281435280158409804228556720158131377342049528810546024786899763038442784789928604641662412)

def Pgcd(a, b):
    while b != 0:
        a, b = b, a%b
    return a

P.&lt;x&gt; = PolynomialRing(Zmod(n))
f1 = (x+noise1)^e1 - c1
f2 = (x+noise2)^e2 - c2
f3 = Pgcd(f1,f2)
a, b = f3.coefficients()[::-1]
x = inverse_mod(ZZ(a),n)*(-b)
print unhexlify(hex(int(x))[2:-1])
```

执行脚本即可得到flag：

```
TetCTF`{`1t_1s_4ll_4b0ut_GCD_0v3r_p0lyn0m14ls`}`
```



## 2020th

题目描述如下：

Now, I bet you wish you were a prophet. Happy new year 2020th!<br>
nc 207.148.119.58 6666

Files:[2020th.zip](https://github.com/ichunqiu-resources/anquanke/blob/master/008/2020th.zip)

分析一下源码，可知程序使用python的random模块连续生成了2019个随机数，我们可以选择查看这2019个随机数中任意2个随机数的值，我们的任务是预测出接下来要产生的第2020个随机数的值，如果预测成功即可获得flag。

通过查阅python的random模块，可以得知其在生成随机数时使用了[梅森旋转算法](https://en.wikipedia.org/wiki/Mersenne_Twister)，且其版本为MT19937，即该PRNG采用32位的state和32位的输出，我们可以找一版python的MT19937 Mersenne Twister PRNG来看一下（p.s. 维基百科上提供了梅森旋转算法的伪代码，有兴趣的读者可以自己实现一版，这同样也是[cryptopals](https://cryptopals.com/sets/3/challenges/21)当中的一个任务）：

```
class MT19937RNG:
    def __init__(self, seed):
        self.MT = [0] * 624
        self.index = 0
        self.MT[0] = seed &amp; 0xffffffff
        for i in range(1, 623+1):
            self.MT[i] = ((0x6c078965 * (self.MT[i-1] ^ (self.MT[i-1] &gt;&gt; 30))) + i) &amp; 0xffffffff

    def generate_numbers(self):
        for i in range(0, 623+1):
            y = (self.MT[i] &amp; 0x80000000) + (self.MT[(i+1) % 624] &amp; 0x7fffffff)  
            self.MT[i] = self.MT[(i + 397) % 624] ^ (y &gt;&gt; 1)
            if (y % 2) != 0:
                self.MT[i] = self.MT[i] ^ (2567483615)

    def extract_number(self):
            if self.index == 0:
                self.generate_numbers()
            y = self.MT[self.index]
            y = y ^ (y &gt;&gt; 11)
            y = y ^ ((y &lt;&lt; 7) &amp; (0x9d2c5680))
            y = y ^ ((y &lt;&lt; 15) &amp; (0xefc60000))
            y = y ^ (y &gt;&gt; 18)
            self.index = (self.index + 1) % 624
            return y
```

审计代码可知，该PRNG在初始化时会建立一个长度为624的数组MT，使用extract_number函数来生成随机数，第一次生成随机数时会调用generate_numbers函数来更新MT数组的值，之后每连续生成624个随机数，都会使用generate_numbers函数来更新MT数组的值。而extract_number函数的过程是可逆的，这意味着如果我们知道一个`randomnum[i]`，我们是可以求出其对应的`MT[i]`的。另外，如果我们知道了MT[2019]，可以很容易的根据extract_number计算出`randomnum[2019]`（即第2020个随机数），因此我们的重点只需放在generate_numbers函数，来想办法计算出`MT[2019]`即可。

观察generate_numbers函数可以发现，由于generate_numbers函数是每生成624个随机数调用一次，即`MT[i+624]`的值是由`MT[i],MT[i+1]和MT[i+397]`生成的，我们令`i=1395`，此时即`MT[2019]`可以由`MT[1395],MT[1396],MT[1792]`这3个数计算而来，但是我们只能获取最多2个数的值，还缺少一个数的值无法获取。

继续观察generate_numbers函数的运算流程，发现在关于`MT[i]`参数的运算为`(self.MT[i] &amp; 0x80000000)`，其运算结果不是0（当0&lt;=MT[i]&lt;0x80000000时）就是0x80000000（当0x80000000=&lt;MT[i]&lt;=0xffffffff时），即我们可以遍历所需要的3个参数中第一个参数的值，另外两个MT的值采用程序提供的接口来获取，这样就有50%的概率可以计算出正确的MT[2019]的值，然后再计算出randomnum[2019]的值尝试提交。由于正确的概率想到高，因此尝试几次即可获得flag。

将上述推导写成python代码形式如下：

```
import random
from pwn import *

def USR(x, shift):
    res = x
    for i in range(32):
        res = x ^ res &gt;&gt; shift
    return res

def USL(x, shift, mask):
    res = x
    for i in range(32):
        res = x ^ (res &lt;&lt; shift &amp; mask)
    return res

def randomnum_to_MT(v):
    v = USR(v, 18)
    v = USL(v, 15, 0xefc60000)
    v = USL(v, 7, 0x9d2c5680)
    v = USR(v, 11)
    return v

def MT_to_randomnum(y):
    y = y ^ (y &gt;&gt; 11)
    y = y ^ ((y &lt;&lt; 7) &amp; (0x9d2c5680))
    y = y ^ ((y &lt;&lt; 15) &amp; (0xefc60000))
    y = y ^ (y &gt;&gt; 18)
    return y

def solve(a, b):
    res = []
    MT_iadd1, MT_iadd397 = randomnum_to_MT(a), randomnum_to_MT(b)
    for msb in range(2):
        y = (msb * 0x80000000) + (MT_iadd1 &amp; 0x7fffffff)
        MT_i = MT_iadd397 ^ (y &gt;&gt; 1)
        if (y % 2) != 0:
            MT_i = MT_i ^ 0x9908b0df
        res.append(MT_to_randomnum(MT_i))
    return res

while True:
    s = remote("207.148.119.58", 6666)
    s.sendline("1396")
    s.sendline("1792")
    guess = []
    for _ in range(2019):
        a = s.recvline().strip()
        if "Nope" not in a:
            guess.append(int(a))

    res = solve(*guess)
    s.sendline(str(res[0]))
    resp = s.recvline().strip()
    if "TetCTF" in resp:
        print resp
        exit(0)
```

执行脚本即可得到flag：

```
TetCTF`{`y0u_4r3_1nd33d_4_pr0ph3t`}`
```



## commonfactor

题目描述如下：

What if each modulus has a prime factor that close to each other?

Files:[commonfactor.zip](https://github.com/ichunqiu-resources/anquanke/blob/master/008/commonfactor.zip)

分析一下源码，发现我们的任务是已知`e, n1, n2, n3, n4, c1, c2, c3, c4`的值，满足：

```
c1 ≡ flag^e (mod n1)
c2 ≡ flag^e (mod n2)
c3 ≡ flag^e (mod n3)
c4 ≡ flag^e (mod n4)
```

其中`ni`可以写为：

```
ni = (p0+ai)*qi
```

`p0,ai,qi`均为未知数，但是我们知道这几个参数的比特数（分别为2048 bit、512 bit和1024 bit）。

根据`ni`的表达式，我们有：

```
q1*n2 - q2*n1 
= q1*(p0+a2)*q2 - q2*(p0+a1)*q1
= q1*p0*q2 + q1*a2*q2 - q2*p0*q1 - q2*a1*q1
= q1*q2*(a2 - a1)
```

根据该表达式，我们可以建立如下方程组：

```
q1*n2 - q2*n1 = q1*q2*(a2 - a1)
q1*n3 - q3*n1 = q1*q3*(a3 - a1)
q1*n4 - q4*n1 = q1*q4*(a4 - a1)
q2*n3 - q3*n2 = q2*q3*(a3 - a2)
q2*n4 - q4*n2 = q2*q4*(a4 - a2)
q3*n4 - q4*n3 = q3*q4*(a4 - a3)
```

设`s[i,j] = qi*qj*(ai - aj)`，整理得：

```
n2*q1 - n1*q2 - s[1,2] = 0
n3*q1 - n1*q3 - s[1,3] = 0
n4*q1 - n1*q4 - s[1,4] = 0
n3*q2 - n2*q3 - s[2,3] = 0
n4*q2 - n2*q4 - s[2,4] = 0
n4*q3 - n3*q4 - s[3,4] = 0
```

该方程组共`q1,q2,q3,q4,s[1,2],s[1,3],s[1,4],s[2,3],s[2,4],s[3,4]`这10个未知数，通过观察发现，`s[i,j]`大约为2560比特（1024+1024+512），而`ni`大约为3072比特（2048+1024），即`s[i,j]`同`ni`相比较小，因此我们可以考虑采用[LLL算法](https://en.wikipedia.org/wiki/Lenstra%E2%80%93Lenstra%E2%80%93Lov%C3%A1sz_lattice_basis_reduction_algorithm)，利用格基规约的思想来计算出格中向量（即`q1,q2,q3,q4,s[1,2],s[1,3],s[1,4],s[2,3],s[2,4],s[3,4]`），将上推导过程写成SageMath代码如下（注意，矩阵中前4列K设为2**1536是鉴于qi约为1024比特，而s[i,j]约为2560比特，因此计算得K约为2560-1024=1536比特）：

```
from Crypto.Util.number import *

data = [((65537, 1569550063055353702062251622140405741164543885895263716006311290669305518774643620241669255260173008709010777432822095605109572129277181116066934393938913194634071173571789450658930352812799017920168864490575696448185577689815549941469079131071103077726355198947488827984628323233221969365714243695334163539732217581013202447968200349694743372108785700167811700154461822011593758838103682584293207390265904896690779335861085789680612320987714538790079517857825517341064238474276090581570268680801110977426713251313985654692074627771968221263628566577663292273864788031693728920793663002764518270439846047430644492176906880059059757415785299265568994209893143584242526018633538624991827790348379585727698363216989988605329417015614749367997396020210490795394806634640415760285432494176804052664955540791844765635239921663181473515232520585476564852497075855687754109417808350181599443473343426564161709223282835203442809017719), '2a3635ef543e23b8890c3c7fb9dc0035cb76e72fbcd4388b1362ae47c66a2f84a19895d769fb32a43aca96059c03cfa0ddee1285ae53f6e3cd3abfaa2b2d4efe025f02b0a2ed9ab69801b53f1f78c631ddd5b3a50c696132af348b988ba055bb1506555e1a9b64f7ef9725addabca6b2cff4fe9622a0f22710f2c3bb7a0b5975fe5bba6576b5a5a47261d149fc8450aa548d70873480cfdc760574593b7fccd2e0d4a3aa862b731c2042a2353f974e7602106117de91949c755bb1b2ebfde0c7ecc33f78fd7ad3c4174b85f50ada6e56caf9a84761489fddbfcb9920cd500d3c2bf99b80cb3339f609659763ff90cd98fa4e4b76059316d69300ff581b1b7339e33784665fdc32d471a45bcc9e64b52308fd610356f1f7845dca3cf8ca50415e3b355a31f8e6e28c6f55ea48afc64518366ee37374ad0de07ae0dd72a9777f99fa38fed2efaf5a1adb8347753aded0c63495ec5645286814f6fb65e80b388028be91948e8fcc3e9725f59ef6c3aa3347b1114f50b6f246c409d7345a95e27c9a'), ((65537, 2730283999793749264071994226279314691204895377404209565102825207699012231964571371393565413047501757446096028236098715505064861045733353396025801293513027886331405786693625981806024261090773960211723151228583932366854870779329338093342110116239823692446625908148569295349026098714317035693497738564674630046858940758268904883253130893434520330702974774740936668070921709593901397140514831064190173236110424772839521534745874746094149570949799151876580658630054731546971832113713586531173316705765487046247502189588416101732562581007651101065666702695240388669899916625981732500919162710884254165127397187535845159165998232131583784946310754662937729402163425101195112360330284894990617298955741961418495852029683443729778504126937607369357318043051374289892542351932602544495709781266606022658359744825356895011618431466585793664964295808363804430145778026353089508091611151785476160457795461698721421465059644656840014600041), '026d719accd581bf22171ac26ea1f7cbe8e260cd24450ff59f85b8421d9a779fbaf36e1acbd67d41280ccf439de5b5f8027a9d18b1e938156682f3bf9f761cafbecfc23c39abc82f6d5e7a4c66e6f435e7d42a5e1ed77fddcbb3a239bba506f23a92f6f57a2657b4b2deb1fef1c1058ba823786679e2e9c3ed7f59c1a6caf7a9fb21c3ab85f09c18dc2ae70676c73e75db6db3b92f5ac60f500582977d3ed496ef0453c5af849c553b7fe19aee6b93d1ca2e8476b53a6b97a03d499b58a2f1b93d4517d703cebba82ddc716410d973bc5321c10d2a8c7303218a2c74bec545b17c13a82deea95b23d691b34f48660e2d870da8db94be02f648f1659cd498d6fd3e3045aa4dd95edbceb401d4a91c135ddfa3d4663e2ebebc4e95f4e9c2b35abfe8b6b602ad6c325f7683e999573cfbe207e0eb8c03d8e36c6f05aa830b3a7ebd9ed8bdd398684187df412ce314954fb5dafe70968dd4f8ae5013853748154c4d3da3d98f9a38f0861bbf17901335771ccb20d5459a24d9d3c79fb6c1e476e255'), ((65537, 1657924959258427226307055128056402549049658652459789576664039012048766540305618951414934786898658966332588809718413923122757875484373037540477722388638858840553898318448626423532633906716310030105130220972278335649446578557159040826543453673941238724891568284827700166830419306376245310916788207429484546008057506662687383202131145958184896298361743446184460904711938203945290001030935479432306677809636841024967980503938216612051167394878501381482352098157599786486983098492823924154622607669864184134461471518206144965857276719217971497293243585472164850309399795206985218997770181188717957316358992357240612579079388186461595164275424746021207041500591749112264695684877167817330714551838424537679384766153692744343813935326599234507761125601864336402749915632919491226732249503422131540162743886991909428277721627830367633020694730720233889895699382127886525607643971481037152168998649018674269175967386808314905895314197), '0f468c7cb9bd432f3646babfa669613b83d6bf2db8ec905f10ad1b9c5f7fd75d842036235b714f86a1b7198f8f973f12c270728ae8591687627525c1e54acf9382c13db98892ec7050dd099527e84835e9890122ef22e1b879236c2f0e26efe1589436d12554fce271ea91e11edbe4c2357eca55c63ecc8e2b23e6d66d9f4a841810d633bf3e4ccb988ceffacedfacb7901f6dab2efcacd95044b0e4e217949c84438310808afa1dfface3adf1dd266e7d9381878227c6040c266d69e71283c23f7864b48bdcf7a964744581575b1cb97213fee4e4071b9b1d0c58611a8934dec1e03f3a9ed981be5403b464e8f4419b823e38bf91f11b023ccc2e01a73def95b990c19c5d2eae9b687f9ab6a704591b3bd9e72addacbefc88fe05ae2c752ebb02895ee105fe74911352ed7bee2a7fb228f1d54fdaef84bd35a67f2f2304017cb83552b2907378ad7c66c7deafb99b0f9d2ce773e1356740844a9911a1e6f253b37cfe6ee16cbae039cfb6749e37bfded30d9baf59b8885d90417c377a147ee0'), ((65537, 3110983727661077937376483862188516844290042596812999305612957161800816904909443569902815766791831716284243968496162996466265930191168784893609334033188775609333281859333753210203804896424511597949940464238543873038000953406791059640295024235321865958267828973182348676239507210900448468842637639173505565493171932934892943628388379309785199843742769621576222396095887453166229610793369913897213948204383648981616627432221090548043925906077201237965560335631118150165890050551079019918702281461877104615212668635883055429384473604595031546202824294553045455954363988428330149396318900050555119058365566287024446487265976507415428817694045660559396737370223118169785779836592977584710981448734152325507656805905400453259442794406092886306392902382083271202964538178390354974828834963375811565387903407912909084458524154107388099011117741856972886184901943539374501035824626968500926567510870331630818145831137375610941414399811), '7f1c2ef0982ee47fea224465ac11c723ed16cd05b204119276e9f2a62eda32f997f47ce0dc7561a7d0d9c6552ecceb8d4b6c85644dfe543553168b4642affbcdd43efb8e9dfe2edeb47f16404cca166386eb4e335c69eaafc81b45993ce177c608f9dbaa8b68278a9288ba8cf98dbca111daa5271bd47dac3edf29d04331dc65a3b5a131b582b4be1410bd6145211225f8ff51bbcfd131fb8698233cd9d92d63adc6dcdb1a7e27e6064f5c6275476832ef57564425057ae72e84cf718a91cbe47c6d2c14ca4bd6b9595e003cf4f3cbbe65af93ad6acee5e8ef31f07bd801831089cdc34593c1fd3bef4a04ffc3024d06b674effa25af9a540897fcf02ff94caab41a4cb7eaa40cc111b72d5e361e51b9b583571cfd051468887f1a9cf264fa6fdc7f342e0d146650fdb96b8a9085fc4493af877fb6ff886dc36b8bd1b02b72fdde03aa02a92b5ec921e51fe379d76103b845e12630639d3f542e65a105924c83f8cc58c3f15c477be6d36433ad8bcb6897189b8f9b95a71f8ef674c7e8a9e9a8')]

e = 65537
c1 = int(data[0][1], 16)

nlist = [x[1] for x, _ in data]
n1, n2, n3, n4 = nlist

n = 3072
t = 2048 - 512 - 1
K = 2^1536
M = Matrix(ZZ, [[K, 0, 0, 0, n2, n3, n4, 0, 0, 0],
                [0, K, 0, 0, -n1, 0, 0, n3, n4, 0],
                [0, 0, K, 0, 0, -n1, 0, -n2, 0, n4],
                [0, 0, 0, K, 0, 0, -n1, 0, -n2, -n3]])

q1 = M.LLL()[0][0] / K
p1 = n1 / q1
phi = (p1-1)*(q1-1)
d1 = inverse_mod(e, phi)

print long_to_bytes(pow(c1, d1, n1))
```

执行脚本即可得到flag：

```
TetCTF`{`_0oops____th3_tw0_pr1m3_f4ct0rs_sh0uld_b3_0f_th3_s4m3_s1z3____4r3n't_th3y_?`}`
```



## padwith2019

题目描述如下：

Pad with 2019 in 2020! Let your past go!<br>
nc 207.148.119.58 5555

Files:[padwith2019.zip](https://github.com/ichunqiu-resources/anquanke/blob/master/008/padwith2019.zip)

审计源码可知，本题需要我们连续完成2个任务，一个是解密token，从而拿到flag的前半部分；另一个是伪造token，从而拿到flag的后半部分。

在计算token时，先对msg进行pad，再进行AES-CBC加密；解密时先解密，再进行unpad，另外服务器端充当了一个padding oracle，可以告诉我们解密后的消息是否padding正确，根据这些特征很容易联想到CBC字节翻转攻击，关于CBC字节翻转攻击的细节可以参考[这里](https://resources.infosecinstitute.com/cbc-byte-flipping-attack-101-approach/#gref)。对于flag的前半部分，我们可以一字节一字节的恢复，从`x00`开始不断试错，如果收到报错提示，则尝试发送下一字节，否则就存储该字节；对于flag的后半部分，我们想要使得`obj['admin'] == True`，只需翻转`fals`为`tru`。将上述攻击过程写成python代码形式如下（flag前半部分）：

```
import json
from os import urandom
from pwn import remote, process
from string import ascii_letters, digits
from itertools import product

PAD = (("2019") * 8).decode('hex')

def get_paddings_dict(n):
    ans = `{``}`
    for i in range(n):
        ans[i] = pad(i+1)
    return ans

def pad(n):
    pad_length = n
    return chr(pad_length) + PAD[:pad_length - 1]

def crack_byte(token, pos, i):
    token[pos] = i
    return ''.join('`{`:02x`}`'.format(x) for x in token)

def find_pad(r, token, pos, last_x):
    token = bytearray(token)
    padings = get_paddings_dict(pos+1)
    if pos:
        token[0] = last_x[0] ^ ord(padings[0][0]) ^ ord(padings[pos][0])
        for j in range(1, pos):
            token[j] = last_x[j]
    for i in range(256):
        payload = crack_byte(token, pos, i)
        r.sendline(payload)
        ans = r.recvline()
        if i % 64 == 0:
            print("current step: ", pos, i, ans)
        if 'padding' in ans:
            continue
        else:
            return i
    raise Exception("All padings are incorrect")

if __name__ == '__main__':
    r = remote("207.148.119.58", 5555)
    token_hex = r.recvline(False)
    print(token_hex)
    token = token_hex.decode('hex')
    parts = [token[i:i+16] for i in range(0, len(token), 16)]
    known = "TF`{`***********"
    flag = ''
    exp_pad = pad(1)
    c1 = parts[2]
    c2 = parts[3]
    last_x = []
    for i in range(len(known)):
        exp_pad = pad(i+1)
        x = find_pad(r, c1+c2, i, last_x)
        i2 = x ^ ord(exp_pad[i])
        ch = chr(i2 ^ ord(c1[i]))
        if i &lt; len(known) and ch == known[i]:
            flag += ch
            print("Horay!", flag)
            last_x.append(x)
        else:
            flag += ch
            print("Is it right?", flag)
            last_x.append(x)
    print('TetC' + flag[:-2])
```

执行脚本即可得到前半部分flag：

```
TetC`{`p4dd1ng_4t_
```

flag后半部分脚本如下：

```
import json
from os import urandom
from pwn import remote, process
from string import ascii_letters, digits
from itertools import product

def crack(token):
    test_token = bytearray(token)
    test = b'x02 `{`"admin": fals'
    for i, (x, y) in enumerate(zip(test, b'x01`{`"admin": true`}`')):
        test_token[i] ^= ord(x) ^ ord(y)
    return ''.join('`{`:02x`}`'.format(x) for x in test_token[:32])

if __name__ == '__main__':
    r = remote("207.148.119.58", 5555)
    token = r.recvline(False).decode('hex')
    new_token = crack(token)
    r.sendline(new_token)
    r.interactive()
```

执行脚本即可得到后半部分flag：

```
th3_b3g1nn1ng_d03s_n0t_h3lp`}`
```

拼接前后两部分即可得到完整flag：

```
TetCTF`{`p4dd1ng_4t_th3_b3g1nn1ng_d03s_n0t_h3lp`}`
```



## yaecc

题目描述如下：

Who knows the backdoor wins!<br>
nc 207.148.119.58 7777

Files:[yaecc.zip](https://github.com/ichunqiu-resources/anquanke/blob/master/008/yaecc.zip)

审计代码可知，题目模拟了一版[ECDSA](https://en.wikipedia.org/wiki/ECDSA)（NIST-p256 曲线）的实现，我们的任务是根据若干消息/签名对来求私钥，为了便于描述我们先描述一下本题用到的符号系统：

```
(R,S):签名
a:私钥
k:nonce
H:msg的哈希值
N:曲线的点群阶
```

在ECDSA中，有如下表达式成立：

```
R*a − S*k + H ≡ 0 (mod N)
```

根据ECDSA算法，当对消息进行签名时，nonce应当随机均匀的从区间[0,N)当中进行选择，以p256为例，N的大小应当为256比特，但是在本题当中，nonce只有240比特，因此我们可以考虑将我们本题当中的问题（根据消息/签名对求私钥）转化为格上的[CVP问题](https://en.wikipedia.org/wiki/Closest_vector_problem)。

假设我们已经收集了D对消息/签名对，此时有：

```
Ri*a − Si*ki + Hi ≡ 0 (mod N) i=1,2,3,...,D
```

等式两边乘上`Si`的逆，得：

```
(Si^(-1))*Ri*a − ki + (Si^(-1))*Hi ≡ 0 (mod N)
```

设`Ai = (Si^(-1))*Ri`，`Bi = -(Si^(-1))*Hi`，整理得：

```
Ai*a ≡ Bi + ki (mod N)
```

即：

```
Ai*a - li*N = Bi + ki （li为整数）
```

将方程用向量形式表示如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/ichunqiu-resources/anquanke/master/008/1.png)

其中(1/2**16)是根据256（a的比特数）-240（k的比特数）= 16计算而来。

对于每一个表达式`Ri*a − Si*ki + Hi ≡ 0 (mod N)`来讲，一对消息/签名对就可以提供私钥的16比特的信息，因此理论上来讲D（即消息/签名对的对数）= 256/16 = 16即可，在写脚本时我们收集的数量比这一理论值略多一些即可。

将上述推导写成SageMath代码形式如下：

```
from sage.all import *
from pwn import *
from hashlib import sha256
import os
from Crypto.Util.number import bytes_to_long

EC = EllipticCurve(
    GF(0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff),
    [-3, 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b]
)
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
Zn = Zmod(n)
G = EC((0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
        0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5))
P = G
Q = EC((0xc97445f45cdef9f0d3e05e1e585fc297235b82b5be8ff3efca67c59852018192,
        0xb28ef557ba31dfcbdd21ac46e2a91e3c304f44cb87058ada2cb815151e610046))
pubkey = EC((50590195252452518804028762265927043036734617153869060607666882619539230027822,
        36611353725619757431858072740028832533174535444901899686884685372270344860185))

class DualEcDrbg(object):
    def __init__(self, seed):
        self.s = ZZ(bytes_to_long(seed))

    def next_bits(self):
        self.s = ZZ((self.s * P)[0])
        return ZZ((self.s * Q)[0]) &amp; (2 ** 240 - 1)

def sign(private_key, message, rand):
    z = Zn(ZZ(sha256(message).hexdigest(), 16))
    k = Zn(rand.next_bits())
    assert k != 0
    K = ZZ(k) * G
    r = Zn(K[0])
    assert r != 0
    s = (z + r * private_key) / k
    assert s != 0
    return r, s

data = []
for _ in range(50):
    s = remote("207.148.119.58", 7777)
    m = eval(s.recvline())
    sig = eval(s.recvline())
    data.append((m, sig))
    s.close()
print len(data)
print data[0]
with open("data.txt", "w") as f:
    f.write(str(data))

size = 20
m = []
Ai = [-1]
Bi = [0]
r0, s0 = map(Zn, data[0][1])
z0 = Zn(ZZ(sha256(str(data[0][0])).hexdigest(), 16))
for i in range(size):
    message, sig = data[i+1]
    ri, si = map(Zn, sig)
    zi = z = Zn(ZZ(sha256(str(message)).hexdigest(), 16))
    A = - (s0 * ri) / (r0 * si)
    B = (z0 * ri) / (si * r0) - zi / si
    Ai.append(A)
    Bi.append(B)

Ai.append(0)
Bi.append(n//2^16)
m.append(Ai)
for i in range(size):
    m.append([0]*(i+1) + [n] + [0]*(size-i))

m.append(Bi)
m = Matrix(ZZ, m)

mLLL = m.LLL()

for irow, row in enumerate(mLLL):
    k0 = Zn(row[0])
    d = (s0*k0-z0)/r0
    if pubkey == ZZ(d)*G:
        print d
        break
    k0 = Zn(-row[0])
    d = (s0*k0-z0)/r0
    if pubkey == ZZ(d)*G:
        print d
        break

msg2 = b"I am admin"
rand = DualEcDrbg(os.urandom(16))
sig = sign(ZZ(d), msg2, rand)
s = remote("207.148.119.58", 7777)
s.sendline(str(sig))
ret = s.recvline()
print ret
```

执行脚本即可得到flag：

```
TetCTF`{`_0oops____Sm4ll_k_ru1n3d_th3_p4rty_`}`
```



## 参考

[https://en.wikipedia.org/wiki/Mersenne_Twister](https://en.wikipedia.org/wiki/Mersenne_Twister)<br>[https://en.wikipedia.org/wiki/Lenstra%E2%80%93Lenstra%E2%80%93Lov%C3%A1sz_lattice_basis_reduction_algorithm](https://en.wikipedia.org/wiki/Lenstra%E2%80%93Lenstra%E2%80%93Lov%C3%A1sz_lattice_basis_reduction_algorithm)<br>[https://en.wikipedia.org/wiki/Closest_vector_problem](https://en.wikipedia.org/wiki/Closest_vector_problem)<br>[https://en.wikipedia.org/wiki/ECDSA](https://en.wikipedia.org/wiki/ECDSA)<br>[https://resources.infosecinstitute.com/cbc-byte-flipping-attack-101-approach/#gref](https://resources.infosecinstitute.com/cbc-byte-flipping-attack-101-approach/#gref)<br>[https://colab.research.google.com/github/nguyenduyhieukma/CTF-Writeups/blob/master/TetCTF/2020/tetctf.ipynb#scrollTo=ag8wJh58Jbyg](https://colab.research.google.com/github/nguyenduyhieukma/CTF-Writeups/blob/master/TetCTF/2020/tetctf.ipynb#scrollTo=ag8wJh58Jbyg)<br>[https://github.com/QyNh/TetCTF-2020](https://github.com/QyNh/TetCTF-2020)<br>[https://github.com/amoniaka-knabino/CTF-writeups/tree/master/CTFs%202020/TetCTF/padwith2019](https://github.com/amoniaka-knabino/CTF-writeups/tree/master/CTFs%202020/TetCTF/padwith2019)
