> 原文链接: https://www.anquanke.com//post/id/233827 


# 2021 AntCTF x D^3CTF 中Crypto方向题解


                                阅读量   
                                **165900**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01b4dbc3f2fff1f7ac.jpg)](https://p2.ssl.qhimg.com/t01b4dbc3f2fff1f7ac.jpg)



## 简介

2021 AntCTF x D^3CTF 中共有四道Crypto方向的题目，题目难度适中，本文对这四道题目及本人的解题思路进行介绍，如有错误还请各位师傅指教。



## babyLattice

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

这道题的题目如下

```
from collections import namedtuple

PublicKey = namedtuple('PublicKey', ['n', 'b'])
SecretKey = namedtuple('SecretKey', ['p', 'q', 'A'])


def gen_key():
    p = random_prime(2^512, lbound=2^511)
    q = random_prime(2^512, lbound=2^511)
    n = p * q

    a11, a12, a21 = [random_prime(2^100) for _ in range(3)]
    a22 = random_prime(2^100)
    while a11 * a22 == a12 * a21:
        a22 = random_prime(2^100)
    A = Matrix(ZZ, [[a11, a12], [a21, a22]])

    a1 = crt([a11, a21], [p, q])
    a2 = crt([a12, a22], [p, q])
    b = a1 * inverse_mod(a2, n) % n

    PK = PublicKey(n, b)
    SK = SecretKey(p, q, A)

    return (PK, SK)

def encrypt(m, pk):
    assert 0 &lt; m &lt; 2^400
    r = randint(0, 2^400-1)
    c = (pk.b*m + r) % pk.n
    return c

def decrypt(c, sk):
    a2 = crt([sk.A[0,1], sk.A[1,1]], [sk.p, sk.q])
    s1 = a2 * c % sk.p
    s2 = a2 * c % sk.q
    m, r = sk.A.solve_right(vector([s1, s2]))
    return m

def test(pk, sk, num=3):
    for _ in range(num):
        m = randint(0, 2^400-1)
        c = encrypt(m, pk)
        mm = decrypt(c, sk)
        assert m == mm


if __name__ == '__main__':
    from hashlib import sha256
    from secret import m, FLAG

    assert FLAG == 'd3ctf`{`%s`}`' % sha256(int(m).to_bytes(50, 'big')).hexdigest()

    PK, SK = gen_key()
    test(PK, SK)

    c = encrypt(m, PK)

    print(f"PK = `{`PK`}`")
    print(f"c = `{`c`}`")
```

我们重点看看加密函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d9e10873c2c29883.png)

也就是

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0184488fd05302f218.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01584cb03a9efa06fa.png)

这样就可以通过`LLL`算法还原出`m`了

### <a class="reference-link" name="EXP"></a>EXP

```
from hashlib import sha256
n = 69804507328197961654128697510310109608046244030437362639637009184945533884294737870524186521509776189989451383438084507903660182212556466321058025788319193059894825570785105388123718921480698851551024108844782091117408753782599961943040695892323702361910107399806150571836786642746371968124465646209366215361
b = 65473938578022920848984901484624361251869406821863616908777213906525858437236185832214198627510663632409869363143982594947164139220013904654196960829350642413348771918422220404777505345053202159200378935309593802916875681436442734667249049535670986673774487031873808527230023029662915806344014429627710399196
c = 64666354938466194052720591810783769030566504653409465121173331362654665231573809234913985758725048071311571549777481776826624728742086174609897160897118750243192791021577348181130302572185911750797457793921069473730039225991755755340927506766395262125949939309337338656431876690470938261261164556850871338570

A = Matrix(ZZ,[[1,0,b],[0,2^400,c],[0,0,n]])
A = A.LLL()
m = int(A[0][0])
flag = 'd3ctf`{`%s`}`' % sha256(int(m).to_bytes(50, 'big')).hexdigest()
print(flag)
```



## simpleGroup

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

这道题的题目如下

```
from random import randint
from secret import FLAG


# A gift for key recovery in challenge [babyLattice]
n = 69804507328197961654128697510310109608046244030437362639637009184945533884294737870524186521509776189989451383438084507903660182212556466321058025788319193059894825570785105388123718921480698851551024108844782091117408753782599961943040695892323702361910107399806150571836786642746371968124465646209366215361
y = 12064801545723347322936991186738560311049061235541031580807549422258814170771738262264930441670708308259694588963224372530498305648578520552038029773849342206125074212912788823834152785756697757209804475031974445963691941515756901268376267360542656449669715367587909233618109269372332127072063171947435639328
e = 1928983487

M = int.from_bytes(FLAG, 'big')
C = []
while M != 0:
    m = M % e
    M //= e
    r = randint(0, n-1)
    c = power_mod(y, m, n) * power_mod(r, e, n)
    C.append(c % n)

print(f"C = `{`C`}`")
```

通过注释我们可以大概猜测`babyLattice`本来是需要分解`n`的，但是因为被非预期了所以又出了这道题目

那么我们回到`babyLattice`题目里面，我们知道的参数实际上只有`b,c,n`，分解`n`应该和`b`有关，通过阅读`b`的生成代码我们可以得到

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0171c5a2a0fc57e8a0.png)

我们展开后两个式子

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01726dd64e2c27cd6c.png)

也就是

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013847b039226ba9e6.png)

两边相乘得到

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01240d7bc397c64ff0.png)

展开并变形得到

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fb817e9efea9b5eb.png)

也就是

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019fb34cbfc6df8174.png)

由于

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0116814e877a172c25.png)

所以我们同样可以用`LLL`还原出目标向量，然后使用`factor`进行分解（`a11,a12,a21,a22`它们都是素数）

当分解完毕后，通过猜测它们对应的值来分解`n`，即

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0175cc67e3c791b2b8.png)

得到`p,q`后，我们回来看题目里面的加密，其会对`FLAG`进行取模并分段加密余数，其中`c`的生成公式如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c7cb6a1b6d37d312.png)

`r`是随机生成的数字，而`e`可以被分解为`e1`和`e2`两个素数，这两个素数又分别是`p-1`和`q-1`的因子

那么我们可以得到

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b7f7bbc609af8da3.png)

通过遍历`j`并判断得到的`c'`是不是为模`p`的`e1次剩余`，我们就可以得到`m`模`e1`的值

同样我们也可以用`q`得到`m`模`e2`的值，然后使用`中国剩余定理`即可还原`m`并最终得到`flag`

### <a class="reference-link" name="EXP"></a>EXP

```
n = 69804507328197961654128697510310109608046244030437362639637009184945533884294737870524186521509776189989451383438084507903660182212556466321058025788319193059894825570785105388123718921480698851551024108844782091117408753782599961943040695892323702361910107399806150571836786642746371968124465646209366215361
b = 65473938578022920848984901484624361251869406821863616908777213906525858437236185832214198627510663632409869363143982594947164139220013904654196960829350642413348771918422220404777505345053202159200378935309593802916875681436442734667249049535670986673774487031873808527230023029662915806344014429627710399196
c = 64666354938466194052720591810783769030566504653409465121173331362654665231573809234913985758725048071311571549777481776826624728742086174609897160897118750243192791021577348181130302572185911750797457793921069473730039225991755755340927506766395262125949939309337338656431876690470938261261164556850871338570

A = Matrix(ZZ,[[1,0,b^2],[0,1,b],[0,0,n]])
A = A.LLL()

x1 = -A[0][0]
x3 = A[0][2]
print(factor(x1))
print(factor(x3))

a12 = 1018979931854255696816714991181
a22 = 1151291153120610849180830073509
a11 = 1017199123798810531137951821909
a21 = 207806651167586080788016046729
print(gcd(b * a12 - a11,n))
print(gcd(b * a22 - a21,n))

p = 7669036313101194621345265255994200133006921565596653797956940811601516306410232120057637504305295677357422367597831138570269733177579895994340511712373309
q = 9102122415165681824420871673621781250311822805618731863628192549895693024247220594372897360668046264863189831887100676431439200352775676467952192600956629
assert(p * q == n)
```

```
#!/usr/bin/env python
from Crypto.Util.number import *
import gmpy2

p = 7669036313101194621345265255994200133006921565596653797956940811601516306410232120057637504305295677357422367597831138570269733177579895994340511712373309
q = 9102122415165681824420871673621781250311822805618731863628192549895693024247220594372897360668046264863189831887100676431439200352775676467952192600956629
n = 69804507328197961654128697510310109608046244030437362639637009184945533884294737870524186521509776189989451383438084507903660182212556466321058025788319193059894825570785105388123718921480698851551024108844782091117408753782599961943040695892323702361910107399806150571836786642746371968124465646209366215361
y = 12064801545723347322936991186738560311049061235541031580807549422258814170771738262264930441670708308259694588963224372530498305648578520552038029773849342206125074212912788823834152785756697757209804475031974445963691941515756901268376267360542656449669715367587909233618109269372332127072063171947435639328
e = 1928983487
e1 = 36493
e2 = 52859

def GCRT(mi, ai):
    assert (isinstance(mi, list) and isinstance(ai, list))
    curm, cura = mi[0], ai[0]
    for (m, a) in zip(mi[1:], ai[1:]):
        d = gmpy2.gcd(curm, m)
        c = a - cura
        assert (c % d == 0)
        K = c // d * gmpy2.invert(curm // d, m // d)
        cura += curm * K
        curm = curm * m // d
        cura %= curm
    return (cura % curm, curm) 

def check(d,p,n):
    if((p - 1) % n == 0):
        return pow(d,(p - 1) // n,p) == 1
    else:
        k = gmpy2.gcd(n, p - 1)
        return pow(d,(p - 1) // k,p) == 1

def getM(c,e,p):
    for i in range(2,e):
        tmpc = (c * gmpy2.invert(pow(y,i,p),p)) % p
        if check(tmpc,p,e):
            return i
    exit(0)

C = [63173987757788284988620600191109581820396865828379773315280703314093571300861961873159324234626635582246705378908610341772657840682572386153960342976445563045427986000105931341168525422286612417662391801508953619857648844420751306271090777865836201978470895906780036112804110135446130976275516908136806153488, 9763526786754236516067080717710975805995955013877681492195771779269768465872108434027813610978940562101906769209984501196515248675767910499405415921162131390513502065270491854965819776080041506584540996447044249409209699608342257964093713589580983775580171905489797513718769578177025063630080394722500351718, 37602000735227732258462226884765737048138920479521815995321941033382094711120810035265327876995207117707635304728511052367297062940325564085193593024741832905771507189762521426736369667607865137900432117426385504101413622851293642219573920971637080154905579082646915297543490131171875075081464735374022745371, 1072671768043618032698040622345664216689606325179075270470875647188092538287671951027561894188700732117175202207361845034630743422559130952899064461493359903596018309221581071025635286144053941851624510600383725195476917014535032481197737938329722082022363122585603600777143850326268988298415885565240343957, 27796821408982345007197248748277202310092789604135169328103109167649193262824176309353412519763498156841477483757818317945381469765077400076181689745139555466187324921460327576193198145058918081061285618767976454153221256648341316332169223400180283361166887912012807743326710962143011946929516083281306203120, 27578857139265869760149251280906035333246393024444009493717159606257881466594628022512140403127178174789296810502616834123420723261733024810610501421455454191654733275226507268803879479462533730695515454997186867769363797096196096976825300792616487723840475500246639213793315097434400920355043141319680299224, 29771574667682104634602808909981269404867338382394257360936831559517858873826664867201410081659799334286847985842898792091629138292008512383903137248343194156307703071975381090326280520578349920827357328925184297610245746674712939135025013001878893129144027068837197196517160934998930493581708256039240833145, 33576194603243117173665354646070700520263517823066685882273435337247665798346350495639466826097821472152582124503891668755684596123245873216775681469053052037610568862670212856073776960384038120245095140019195900547005026888186973915360493993404372991791346105083429461661784366706770467146420310246467262823, 5843375768465467361166168452576092245582688894123491517095586796557653258335684018047406320846455642101431751502161722135934408574660609773328141061123577914919960794180555848119813522996120885320995386856042271846703291295871836092712205058173403525430851695443361660808933971009396237274706384697230238104, 61258574367240969784057122450219123953816453759807167817741267194076389100252707986788076240792732730306129067314036402554937862139293741371969020708475839483175856346263848768229357814022084723576192520349994310793246498385086373753553311071932502861084141758640546428958475211765697766922596613007928849964, 13558124437758868592198924133563305430225927636261069774349770018130041045454468021737709434182703704611453555980636131119350668691330635012675418568518296882257236341035371057355328669188453984172750580977924222375208440790994249194313841200024395796760938258751149376135149958855550611392962977597279393428]
m = 0
for c in C[::-1]:
    cp = c % p
    cq = c % q
    m1 = getM(cp,e1,p)
    m2 = getM(cq,e2,q)
    mm,lcm = GCRT([e1,e2],[m1,m2])
    print("Get mm: " + hex(mm))
    m *= e
    m += mm

flag = long_to_bytes(m)
print(flag)
```



## EasyCurve

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

这道题目的主要部分如下

```
import socketserver
from Crypto.PublicKey import RSA
from Crypto.Util.number import getPrime , bytes_to_long
from Curve import MyCurve
from hashlib import sha256
import os
import string
import random
import signal
from secret import flag

BIT = 2048
p = 9688074905643914060390149833064012354277254244638141162997888145741631958242340092013958501673928921327767591959476890238698855704376126231923819603296257

class Task(socketserver.BaseRequestHandler):

    def proof_of_work(self):
        random.seed(os.urandom(8))
        proof = ''.join([random.choice(string.ascii_letters+string.digits) for _ in range(20)])
        _hexdigest = sha256(proof.encode()).hexdigest()
        self.send(f"sha256(XXXX+`{`proof[4:]`}`) == `{`_hexdigest`}`".encode())
        self.send(b'Give me XXXX: ')
        x = self.recv()
        if len(x) != 4 or sha256(x+proof[4:].encode()).hexdigest() != _hexdigest:
            self.send('wrong')
            return False
        return True

    def recv(self):
        data = self.request.recv(1024)
        return data.strip()

    def send(self, msg, newline=True):
        if isinstance(msg , bytes):
            msg += b'\n'
        else:
            msg += '\n'
            msg = msg.encode()
        self.request.sendall(msg)

    def key_gen(self , bit):
        key = RSA.generate(bit)
        return key

    def ot(self , point):
        x , y = point
        random.seed(os.urandom(8))

        key = self.key_gen(BIT)
        self.send('n = ' + str(key.n))
        self.send('e = ' + str(key.e))
        x0 = random.randint(1 , key.n)
        x1 = random.randint(1 , key.n)
        self.send("x0 = " + str(x0))
        self.send("x1 = " + str(x1))

        self.send("v = ")
        v = int(self.recv())
        m0_ = (x + pow(v - x0, key.d, key.n)) % key.n
        m1_ = (y + pow(v - x1, key.d, key.n)) % key.n
        self.send("m0_ = " + str(m0_))
        self.send("m1_ = " + str(m1_))

    def handle(self):
        signal.alarm(180)
        if not self.proof_of_work():
            return 0
        e = bytes_to_long(os.urandom(32))
        u = random.randint(1 , p)
        D = random.randint(1 , p)
        curve = MyCurve(p , D , u)
        self.send('p = ' + str(p))
        self.send('D = ' + str(D))
        for i in range(3):
            G = curve.getPoint()
            self.ot(G)
            P = curve.mul(e , G)
            self.ot(P)
            self.send("do you know my e?")
            guess = int(self.recv())
            if guess == e:
                self.send("oh no!")
                self.send(flag)
                return 0
            else:
                self.send("Ha, I know you can't get it.")

class ForkedServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 10000
    server = ForkedServer((HOST, PORT), Task)
    server.allow_reuse_address = True
    server.serve_forever()
```

其使用了一个随机生成参数的`MyCurve`并生成了随机的`e`，给我们三次交互的机会，每次交互会随机生成点`G`和点`P`并使用`OT`将这两个点的信息传递给我们，点`P`是`e`倍的点`G`，当我们给服务器正确的`e`的时候我们可以得到`flag`

这其实就是一个`离散对数问题`，我们首先关注服务器的参数，`MyCurve`所使用的`p`是`512`比特的，而`OT`中`RSA`的`n`是`2048`比特的，这样生成的点的`x`和`y`乘起来也没有`n`的大。那么可以参考2020hackergame的[不经意传输](https://github.com/USTC-Hackergame/hackergame2020-writeups/blob/master/official/%E4%B8%8D%E7%BB%8F%E6%84%8F%E4%BC%A0%E8%BE%93/README.md)中的攻击方式来同时获取点的`x`和`y`坐标

之后便是如何通过点`G`和点`P`来获取`e`了，我们可以注意到`p-1`是光滑的

```
sage: factor(p-1)
2^21 * 3^10 * 7^4 * 11 * 13^2 * 17 * 19 * 29 * 31 * 37 * 43^3 * 47 * 71 * 83 * 89 * 97 * 223 * 293 * 587 * 631 * 709 * 761 * 1327 * 1433 * 1733 * 1889 * 2503 * 3121 * 6043 * 6301 * 49523 * 98429 * 140683 * 205589 * 1277369 * 1635649 * 5062909 * 45698189 * 67111151 * 226584089 * 342469397
```

那么我们可以通过[Pohlig-Hellman algorithm](https://ctf-wiki.org/crypto/asymmetric/discrete-log/discrete-log/#pohlig-hellman-algorithm)来解决`离散对数问题`并最终得到flag

### <a class="reference-link" name="EXP"></a>EXP

`exp`有概率成功，如果报错或者答案错误多跑几次即可

```
#!/usr/bin/env python
import string, gmpy2
from hashlib import sha256
from pwn import *
context.log_level = "debug"

dic = string.ascii_letters + string.digits

def solvePow(prefix,h):
    for a1 in dic:
        for a2 in dic:
            for a3 in dic:
                for a4 in dic:
                    x = a1 + a2 + a3 + a4
                    proof = x + prefix.decode("utf-8")
                    _hexdigest = sha256(proof.encode()).hexdigest()
                    if _hexdigest == h.decode("utf-8"):
                        return x

def getData():
    r.recvuntil("n = ")
    n = int(r.recvuntil("\n", drop = True))
    r.recvuntil("e = ")
    e = int(r.recvuntil("\n", drop = True))
    r.recvuntil("x0 = ")
    x0 = int(r.recvuntil("\n", drop = True))
    r.recvuntil("x1 = ")
    x1 = int(r.recvuntil("\n", drop = True))
    offset = 2 &lt;&lt; 1024
    offset_e = int(pow(offset, e, n))
    v = ((offset_e * x0 - x1) * gmpy2.invert(offset_e - 1, n)) % n
    r.sendlineafter("v = ",str(v))
    r.recvuntil("m0_ = ")
    m0 = int(r.recvuntil("\n", drop = True))
    r.recvuntil("m1_ = ")
    m1 = int(r.recvuntil("\n", drop = True))
    m = (m0 * offset - m1) % n
    x = m // offset + 1
    y = x * offset - m
    return x,y

r = remote("47.100.50.252",10000)
r.recvuntil("sha256(XXXX+")
prefix = r.recvuntil(") == ", drop = True)
h = r.recvuntil("\n", drop = True)
result = solvePow(prefix,h)
r.sendlineafter("Give me XXXX: \n",result)

r.recvuntil("p = ")
r.recvuntil("\n", drop = True)
r.recvuntil("D = ")
D = int(r.recvuntil("\n", drop = True))

Gx,Gy = getData()
Px,Py = getData()

with open("data.txt","wb") as f:
    f.write(str(D).encode() + b"\n")
    f.write(str(Gx).encode() + b"\n")
    f.write(str(Gy).encode() + b"\n")
    f.write(str(Px).encode() + b"\n")
    f.write(str(Py).encode() + b"\n")

s = process(argv=["sage", "exp.sage"])
e = int(s.recv())
s.close()
r.sendline(str(e))

r.interactive()
```

```
# exp.sage
load("Curve.sage")

p = 9688074905643914060390149833064012354277254244638141162997888145741631958242340092013958501673928921327767591959476890238698855704376126231923819603296257
F = GF(p)
fac = [2^21,3^10,7^4,11,13^2,17,19,29,31,37,43^3,47,71,83,89,97,223,293,587,631,709,761,1327,1433,1733,1889,2503,3121,6043,6301,49523,98429,140683,205589,1277369,1635649,5062909,45698189,67111151,226584089,342469397]

def bsgs(g, y, p):
    m = int(ceil(sqrt(p - 1)))
    S = `{``}`
    point = (u,0)
    for i in range(m):
        point = curve.add(point,g)
        pointg = point[0] &lt;&lt; 800 | point[1]
        S[pointg] = i

    gs = curve.mul(m,g)
    for i in range(m):
        pointy = y[0] &lt;&lt; 800 | y[1]
        if pointy in S:
            return S[pointy] - i * m + 1
        y = curve.add(y,gs)
    return None

def Pohlig_Hellman(G,P):
    ea = []
    na = []
    for i in range(len(fac)):
        c = fac[i]
        n = (p - 1) // c
        gi = curve.mul(n, G)
        yi = curve.mul(n, P)
        ei = bsgs(gi,yi,c)
        ea.append(ei%c)
        na.append(c)
    ee = crt(ea,na)
    return ee

data = open("data.txt","rb").read().decode("utf-8")
data = data.split("\n")

D = int(data[0])
Gx = int(data[1])
Gy = int(data[2])
Px = int(data[3])
Py = int(data[4])

G = (F(Gx),F(Gy))
P = (F(Px),F(Py))

u2 = (Gx ^ 2 - D * Gy ^ 2)
u2 = F(u2)
u = int(u2.sqrt())
curve = MyCurve(p , D , u)
e = Pohlig_Hellman(G,P)
e %= p - 1
print(e)
```



## AliceWantFlag

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

这道题目分为`server`端和`Alice`端，其中`server`端的代码如下

```
from elgamal import elgamal
import socketserver
from prikey import server_prikey , AlicePasswd
from pubkey import Alice_pubkey
from secret import Alice_flag , ctfer_flag
import random
import signal
from os import urandom
from Crypto.Util.number import long_to_bytes , bytes_to_long
from Crypto.Cipher import AES

MENU = "1. signup  2.signin"
XOR = lambda s1,s2 :bytes([x1^x2 for x1 , x2 in zip(s1,s2)])
def pad(m):
    m += bytes([16 - len(m) % 16] * (16 - len(m) % 16))
    return m

def unpad(m):
    padlen = m[-1]
    for i in range(1 , padlen + 1):
        if m[-i] != m[-1]:
            return b''
    return m[:-m[-1]]

class server(socketserver.BaseRequestHandler):

    def setup(self):
        self.pubkey = `{``}`
        self.passwd = `{``}`
        self.prikey = elgamal(server_prikey)
        self.pubkey[b'Alice'] = elgamal(Alice_pubkey)
        self.passwd[b'Alice'] = AlicePasswd

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

    def enc_send(self, msg , usrid , enc_key = b''):
        if enc_key == b'':
            pubenc = self.pubkey[usrid]
            y1 , y2 = pubenc.encrypt(bytes_to_long(msg))
            self._send(str(y1) + ', ' + str(y2))
        else:
            assert len(enc_key) == 16
            aes = AES.new(enc_key , AES.MODE_ECB)
            self._send(aes.encrypt(pad(msg)))

    def dec_recv(self,  enc_key = b''):
        msg = self._recv()
        if enc_key == b'':
            c = [int(i) for i in msg.split(b', ')]
            m = self.prikey.decrypt(c)
            print(long_to_bytes(m))
            return long_to_bytes(m)
        else:
            assert len(enc_key) == 16
            aes = AES.new(enc_key , AES.MODE_ECB)
            return unpad(aes.decrypt(msg))

    def signup(self):
        if len(self.passwd) &gt; 5:
            self._send('sorry, the number of users is out of limit')
            return 0
        self._send('please give me your name')
        userid = self._recv()
        if len(userid) &gt; 20:
            self._send('your id can\'t be too long')
            return 0
        elif userid in self.passwd:
            self._send('the name has been used')
            return 0
        else:
            self._send('please give me your passwd(encrypted)')
            userpasswd = self.dec_recv()
            if len(userpasswd) &gt; 11:
                self._send('your password can\'t be too long')
                return 0
            else:
                self.passwd[userid] = userpasswd
            self._send('please give me your publickey')
            userpubkey = self._recv()
            try:
                userpubkey = [int(i) for i in userpubkey[1:-1].split(', ')]
            except:
                self._send('publickey format error')
                self.passwd.pop(userid)
                return 0
            self.pubkey[userid] = elgamal(userpubkey)
            self._send('sign up success')
            return 1

    def signin(self):
        self._send('please give me your name')
        userid = self._recv()
        if userid not in self.passwd:
            self._send('sorry the userid is not existed')
            return 0
        while 1:
            random.seed(urandom(8))
            r = random.getrandbits(8 * 11)
            self._send('please give me your passwd(encrypted and xored by r)')
            self._send(str(r))
            userdata = self.dec_recv()
            if bytes_to_long(userdata) == r ^ bytes_to_long(self.passwd[userid]):
                self._send('signin success')
                break
            else:
                self._send('password error')
        endkey = urandom(5)
        key = userdata + endkey
        self._send('now let\'s communicate with this key')
        self.enc_send(endkey , userid)
        return userid , key

    def handle(self):
        signal.alarm(240)
        key = b''
        userid = ''
        while 1:
            self._send(MENU)
            choice = self._recv()
            if choice == b'1':
                self.signup()
            elif choice == b'2':
                temp = self.signin()
                if temp != 0:
                    userid , key = temp
                    break
            else:
                self._send('error')
        msg = self.dec_recv(enc_key = key)
        if msg == b'I am a ctfer.Please give me flag':
            self.enc_send(b'ok, your flag is here ' + ctfer_flag , userid , enc_key= key)
        elif msg == b'I am Alice, Please give me true flag' and userid == b'Alice':
            self.enc_send(b'Hi Alice, your flag is ' + Alice_flag , userid , enc_key= key)
        return 0

    def finish(self):
        self.request.close()

class ForkedServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 10001
    server = ForkedServer((HOST, PORT), server)
    server.allow_reuse_address = True
    server.serve_forever()
```

`Alice`端的代码如下

```
import socket
from elgamal import elgamal
from pubkey import server_pubkey
from prikey import Alice_prikey , AlicePasswd
from Crypto.Util.number import long_to_bytes , bytes_to_long
from Crypto.Cipher import AES
import socketserver , signal
def pad(m):
    m += bytes([16 - len(m) % 16] * (16 - len(m) % 16))
    return m

def unpad(m):
    return m[:-m[-1]]

class Alice:
    def __init__(self , ip , port):
        self.pridec = elgamal(Alice_prikey)
        self.pubenc = elgamal(server_pubkey)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((ip, port))

    def _recv(self):
        data = self.s.recv(1024)
        return data.strip()

    def _send(self, msg):
        if isinstance(msg , str):
            msg = msg.encode()
        self.s.send(msg)

    def enc_send(self, msg , enc_key = b''):
        if enc_key == b'':
            y1 , y2 = self.pubenc.encrypt(bytes_to_long(msg))

            self._send(str(y1) + ', ' + str(y2))
        else:
            assert len(enc_key) == 16
            aes = AES.new(enc_key , AES.MODE_ECB)
            self._send(aes.encrypt(pad(msg)))

    def dec_recv(self,  enc_key = b''):
        msg = self._recv()
        if enc_key == b'':
            c = [int(i) for i in msg.split(b', ')]
            m = self.pridec.decrypt(c)
            return long_to_bytes(m)
        else:
            assert len(enc_key) == 16
            aes = AES.new(enc_key , AES.MODE_ECB)
            return unpad(aes.decrypt(msg))

    def main(self):
        firstmsg = self._recv()
        if firstmsg != b'1. signup  2.signin':
            return 0
        self._send('2')
        self._recv()
        self._send('Alice')
        self._recv()
        r = int(self._recv())
        userdata = long_to_bytes(bytes_to_long(AlicePasswd) ^ r)
        self.enc_send(userdata)
        self._recv()
        self._recv()
        endkey = self.dec_recv()
        key = userdata + endkey
        self.enc_send(b'I am a ctfer.Please give me flag' , enc_key = key)
        return self.dec_recv(enc_key = key)

class Task(socketserver.BaseRequestHandler):
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
        signal.alarm(60)
        self._send('Hello, I am Alice, can you tell me the address of the server?\nIn return, I will give you the ctf_flag')
        try:
            addr = self._recv()
            ip, port = [x.strip() for x in addr.split(b':')]

            port = int(port)
        except:
            ip, port = '0.0.0.0', 10001
        a = Alice(ip , port)
        msg = a.main()
        self._send(b'Thanks, here is your flag')
        self._send(msg)

class ForkedServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 10003
    server = ForkedServer((HOST, PORT), Task)
    server.allow_reuse_address = True
    server.serve_forever()
```

`server`和`Alice`的密钥生成和使用都和`elgamal算法`一致，这里不再阐述

服务端的大概逻辑如下

```
U: User
S: Server
UserPasswd = UserPublicKey

Sign Up:
S -&gt; U : 'please give me your name'
U -&gt; S : userid
S : assert len(userid) &lt;= 20 and userid not in passwd
S -&gt; U : 'please give me your passwd(encrypted)'
U -&gt; S : c = elgamal.enc(UserPasswd,ServerPublicKey)
S : userpasswd = elgamal.dec(c,ServerPrivateKey
S : assert len(userpasswd) &lt;= 11
S : passwd[userid] = userpasswd
S -&gt; U : 'sign up success'

Sign In:
S -&gt; U : 'please give me your name'
U -&gt; S : userid
S : assert userid in passwd
S -&gt; U : 'please give me your passwd(encrypted and xored by r)'
S -&gt; U : r = random.getrandbits(8 * 11)
U -&gt; S : c = elgamal.enc(UserPasswd ^ r,ServerPublicKey)
S : assert elgamal.dec(c,ServerPrivateKey) == passwd[userid] ^ r
S : key = userdata + endkey, userdata = passwd[userid] ^ r, endkey = urandom(5)
S -&gt; U : 'now let\'s communicate with this key'
S -&gt; U : k = elgamal.enc(key,UserPasswd)
U -&gt; S : m = AES.enc(key,msg)
S : dm = AES.dec(key,m)
S : if dm == 'I am a ctfer.Please give me flag':
    S -&gt; U : r1 = AES.enc(key,ctfer_flag)
S : if dm == 'I am Alice, Please give me true flag' and userid == 'Alice'
    S -&gt; U : r2 = AES.enc(key,Alice_flag)
```

大概理解下来就是一个利用`elgamal`进行密钥交换然后加密通信的逻辑

由于这里我们需要以`Alice`的身份登陆并使用交换的`AES通信密钥`进行密文的加密，所以我们需要知道`AlicePasswd`和`key`

这道题目中由于也有`Alice`端的服务，所以我们可以伪装成服务端来和`Alice`端进行通信，也就是进行`中间人攻击`

首先来看看如何获得`AlicePasswd`，观察`Alice`端的如下代码

```
def main(self):
    firstmsg = self._recv()
    if firstmsg != b'1. signup  2.signin':
        return 0
    self._send('2')
    self._recv()
    self._send('Alice')
    self._recv()
    r = int(self._recv())
    userdata = long_to_bytes(bytes_to_long(AlicePasswd) ^ r)
    self.enc_send(userdata)
    self._recv()
    self._recv()
    endkey = self.dec_recv()
    key = userdata + endkey
    self.enc_send(b'I am a ctfer.Please give me flag' , enc_key = key)
    return self.dec_recv(enc_key = key)

def dec_recv(self,  enc_key = b''):
    msg = self._recv()
    if enc_key == b'':
        c = [int(i) for i in msg.split(b', ')]
        m = self.pridec.decrypt(c)
        return long_to_bytes(m)
    else:
        assert len(enc_key) == 16
        aes = AES.new(enc_key , AES.MODE_ECB)
        return unpad(aes.decrypt(msg))
```

由于`endkey`长度为`5`，而`key`的长度是`16`，那么可以自然推断出`userdata`的长度为`11`

但是如果我们控制`r`使得`userdata`的第一个字节异或为了`\x00`，那么`userdata`的长度就变成了`10`，如果`endkey`的长度不变，再使用`userdata + endkey`作为`AES`的`key`，那么会通不过`assert len(enc_key) == 16`，即连接会断开

这样我们可以通过单字节爆破`AlicePasswd`的值使得`key`的长度从`16`变成`15`，这样就能获得`AlicePasswd`的第一个字节，然后重复该过程便可以获得`AlicePasswd`（每爆破出一个字节，在爆破下一个字节的时候将`endkey`的长度变长一位即可连续爆破）

PS：实际上的操作过程中`AlicePasswd`的最后一个字节爆破不出来，我们使用服务端的`Sign In`功能来爆破最后一个字节即可

在拿到了`AlicePasswd`之后，我们便可以伪造成`Alice`登陆服务端，但是由于`endkey`是使用`AlicePublicKey`来进行加密的，所以我们还需要拿到`endkey`的值才能获得`AES`的`key`并进行`任意文本加解密`

前面我们提过，`endkey`长度为`5`，但是实际上`elgamal`的`p`是`512`比特的，也就是说`endkey`远比`p`小

如果我们将`elgamal`加密后的`endkey`的`y2`乘以一个倍数`k`，那么`elgamal`解密后的`endkey`就会变大`k`倍，这个值如果特别大，则`userdata + endkey`就也会变大，这样便会通不过`assert len(enc_key) == 16`，即连接会断开

那么我们就可以通过遍历`k`并查看连接是否断开来得到`endkey`的大致范围，然后通过控制`r`让`userdata`的长度变小来使得我们的`k`可以不断变大，进而将`endkey`的取值范围不断缩小来得到`endkey`

最后我们便可以进行`任意文本加解密`来获取`flag`

### <a class="reference-link" name="EXP"></a>EXP

爆破`AlicePasswd`的脚本（除了最后一个字节）

```
#!/usr/bin/env python
from elgamal import elgamal
from os import urandom
from Crypto.Util.number import *
from pwn import *
from time import *
import random
#context.log_level = 'debug'

Alice_pubkey = (10701440058624032601015137538928332495339102166449611910023158626004456760436930147541475696463030881833656888220652983522600176918743749340172660134163173, 1564399668655593150166497641453625075939863931648697579307, 7485644640971189066076867813504769638089749022750276585841131549227880841063823940682209946365975810625990180843110530957715179877761206203179636693608929, 10399272689500457356753299445284422908920074489727610618928888372268024186959263604721857776550008093778901180936272708522371781846820901338928077050396521)
pubenc = elgamal(Alice_pubkey)

def enc(msg):
    y1 , y2 = pubenc.encrypt(bytes_to_long(msg))
    return [y1,y2]

def attackAlice(rr,m):
    try:
        middle_shell = listen(8888)
        alice_shell = remote("47.100.0.15",10003)
        alice_shell.recvuntil(b"Hello, I am Alice, can you tell me the address of the server?\nIn return, I will give you the ctf_flag\n")
        alice_shell.sendline("xxxx:8888") # xxxx -&gt; your vps's ip
        middle_shell.sendline(b'1. signup  2.signin')
        middle_shell.recv()
        middle_shell.sendline(b'please give me your name')
        middle_shell.recv()
        middle_shell.sendline(b'please give me your passwd(encrypted and xored by r)')
        middle_shell.sendline(str(rr))
        middle_shell.recv()
        middle_shell.sendline(b'signin success')
        middle_shell.sendline(b'now let\'s communicate with this key')
        middle_shell.sendline(str(m[0]) + ', ' + str(m[1]))
        sleep(0.3)
        result = middle_shell.recv()
        if result != b"":
            middle_shell.close()
            alice_shell.close()
            return True
    except:
        if middle_shell:
            middle_shell.close()
        if alice_shell:
            alice_shell.close()
    return False

known_pwd = b""

# 0x35343764643163636333xx
for i in range(11):
    for r in range(0,256):
        rr = ((bytes_to_long(known_pwd) &lt;&lt; 8) + r) &lt;&lt; ((11 - i - 1) * 8)
        print("try:" + hex(rr))
        msg = b"A" * (5 + i)
        c = enc(msg)
        if not attackAlice(rr,c):
            known_pwd += long_to_bytes(r)
            print(known_pwd.hex())
            break
```

爆破`AlicePasswd`的最后一个字节的脚本

```
#!/usr/bin/env python
from elgamal import elgamal
from os import urandom
from Crypto.Util.number import *
from pwn import *
from time import *
import random
#context.log_level = 'debug'

dic = "0123456789abced"
server_pubkey = (8299337325013713958100496214277076548352330213422739951900206795659160881192662528217175848727001874097369338994314737585158671248737646741717255122339339, 1168114014665994438995759247944846107956060291607878556427, 6500863983405565947154848535503122330952083500341721347265599161478330537510643776384164499549064061675517930495094496645911948535824156417648599603482256, 1567838365897620258270310904624368598290758028096181970817619626094906443214320401208038763050717813632540079799097716376430981907783174222429828480377116)
pubenc = elgamal(server_pubkey)


known_pwd = "547dd1ccc3"
server_shell = remote("47.100.0.15",10001)
server_shell.sendlineafter("\n","2")
server_shell.recvuntil("please give me your name\n")
server_shell.sendline("Alice")
for c in dic:
    server_shell.recvuntil("please give me your passwd(encrypted and xored by r)\n")
    rr = int(server_shell.recvline())
    pwd = bytes_to_long((known_pwd + c).encode())
    prefix = long_to_bytes(pwd ^ rr)
    assert(len(prefix) == 11)
    y1 , y2 = pubenc.encrypt(pwd ^ rr)
    server_shell.sendline(str(y1) + ', ' + str(y2))
    result = server_shell.recv()
    if b"success" in result:
        print(known_pwd + c)
        break

server_shell.interactive()
```

获取`endkey`并进行`中间人攻击`的脚本

```
#!/usr/bin/env python
from pwn import *
from Crypto.Util.number import *
from Crypto.Cipher import AES
from elgamal import elgamal
#context.log_level = "debug"

pwd = "547dd1ccc38".encode()
pwd = bytes_to_long(pwd)
server_pubkey = (8299337325013713958100496214277076548352330213422739951900206795659160881192662528217175848727001874097369338994314737585158671248737646741717255122339339, 1168114014665994438995759247944846107956060291607878556427, 6500863983405565947154848535503122330952083500341721347265599161478330537510643776384164499549064061675517930495094496645911948535824156417648599603482256, 1567838365897620258270310904624368598290758028096181970817619626094906443214320401208038763050717813632540079799097716376430981907783174222429828480377116)
pubenc = elgamal(server_pubkey)
p = 10701440058624032601015137538928332495339102166449611910023158626004456760436930147541475696463030881833656888220652983522600176918743749340172660134163173

def pad(m):
    m += bytes([16 - len(m) % 16] * (16 - len(m) % 16))
    return m

def unpad(m):
    padlen = m[-1]
    for i in range(1 , padlen + 1):
        if m[-i] != m[-1]:
            return b''
    return m[:-m[-1]]

def oracle(m,n,p):
    y1 = m[0]
    y2 = m[1]
    y2 = (y2 * n) % p
    return [y1,y2]


def combineKey(m,rr):
    for i in range(3):
        sleep(0.3)
        try:
            middle_shell = listen(8888)
            alice_shell = remote("47.100.0.15",10003)
            alice_shell.recvuntil(b"Hello, I am Alice, can you tell me the address of the server?\nIn return, I will give you the ctf_flag\n")
            alice_shell.sendline("xxxx:8888") # xxxx -&gt; your vps's ip
            middle_shell.sendline(b'1. signup  2.signin')
            middle_shell.recv()
            middle_shell.sendline(b'please give me your name')
            middle_shell.recv()
            middle_shell.sendline(b'please give me your passwd(encrypted and xored by r)')
            middle_shell.sendline(str(rr))
            middle_shell.recv()
            middle_shell.sendline(b'signin success')
            middle_shell.sendline(b'now let\'s communicate with this key')
            middle_shell.sendline(str(m[0]) + ', ' + str(m[1]))
            sleep(0.5)
            result = middle_shell.recv()
            print(result)
            if result != b"":
                middle_shell.close()
                alice_shell.close()
                return True
        except:
            if middle_shell:
                middle_shell.close()
            if alice_shell:
                alice_shell.close()
    return False

server_shell = remote("47.100.0.15",10001)
server_shell.sendlineafter("\n","2")
server_shell.recvuntil("please give me your name\n")
server_shell.sendline("Alice")
server_shell.recvuntil("please give me your passwd(encrypted and xored by r)\n")
rr = int(server_shell.recvline())
prefix = long_to_bytes(pwd ^ rr)
assert(len(prefix) == 11)
y1 , y2 = pubenc.encrypt(pwd ^ rr)
server_shell.sendline(str(y1) + ', ' + str(y2))
server_shell.recvuntil("now let's communicate with this key\n")
y1,y2 = [int(i) for i in server_shell.recvuntil("\n", drop = True).decode("utf-8").split(", ")]
print(y1,y2)
success("Get communicate key:" + str(y1) + "," + str(y2))

l = 0
h = 2**40
idx = 0
prefix_length = 0
bound = 2**40
count = 0
flag = False


for _ in range(11):
    if flag:
        break
    binary_ptr = 0x80
    diff = binary_ptr // 2
    assert_arr = [-1] * 256
    for i in range(10):
        count += 1
        if binary_ptr != 0 and assert_arr[binary_ptr-1] ^ assert_arr[binary_ptr] == 1:
            prefix_length += 1
            l = bound // multiple
            h = bound // (multiple - 1)
            idx = multiple - 1
            print(hex(l),hex(h),count)
            bound *= 0x100
            if abs(h - l) &lt; 2:
                flag = True
            break
        if binary_ptr != 255 and assert_arr[binary_ptr] ^ assert_arr[binary_ptr+1] == 1:
            prefix_length += 1
            l = bound // (multiple + 1)
            h = bound // multiple
            idx = multiple
            print(hex(l),hex(h),count)
            bound *= 0x100
            if abs(h - l) &lt; 2:
                flag = True
            break
        rr = bytes_to_long(long_to_bytes(pwd)[:prefix_length]) * 2**(8*(11 - prefix_length))
        multiple = idx * 0x100 + binary_ptr
        m = oracle([y1,y2],multiple,p)
        if combineKey(m,rr):
            if binary_ptr == 255:
                prefix_length += 1
                h = bound // (multiple + 1)
                idx = multiple + 1
                print(hex(l),hex(h),count)
                bound *= 0x100
                if abs(h - l) &lt; 2:
                    exit(0)
                break
            assert_arr[binary_ptr] = 0
            binary_ptr += diff
            diff //= 2
        else:
            assert_arr[binary_ptr] = 1
            binary_ptr -= diff
            diff //= 2

context.log_level = "debug"
endkey = long_to_bytes(h)
key = prefix + endkey
success("get key:" + key.hex())
data = b'I am Alice, Please give me true flag'
cipher = AES.new(key , AES.MODE_ECB)
data = cipher.encrypt(pad(data))
server_shell.sendline(data)
msg = server_shell.recvuntil("\n",drop = True)
print(cipher.decrypt(msg))
```



## 参考

[https://github.com/USTC-Hackergame/hackergame2020-writeups/blob/master/official/不经意传输/README.md](https://github.com/USTC-Hackergame/hackergame2020-writeups/blob/master/official/%E4%B8%8D%E7%BB%8F%E6%84%8F%E4%BC%A0%E8%BE%93/README.md)

[https://ctf-wiki.org/crypto/asymmetric/discrete-log/discrete-log/#pohlig-hellman-algorithm](https://ctf-wiki.org/crypto/asymmetric/discrete-log/discrete-log/#pohlig-hellman-algorithm)
