> 原文链接: https://www.anquanke.com//post/id/173088 


# AES加密的安全问题


                                阅读量   
                                **329524**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01feada693a7c3ab9f.jpg)](https://p1.ssl.qhimg.com/t01feada693a7c3ab9f.jpg)



## aes加密简介

AES算法全称Advanced Encryption Standard,是DES算法的替代者，旨在取代DES成为广泛使用的标准，于2001年11月26日发布于FIPS PUB 197，并在2002年5月26日成为有效的标准。2006年，高级加密标准已然成为对称密钥加密中最流行的算法之一。

AES是典型的对称加密算法，对称加密不同于md5 sha的哈希摘要算法，对称加密是可逆的，通常是明文+密钥，再利用算法来加密成密文，如果要还原也很简单，只要根据密钥+密文+生成算法的逆运算，即可解出，对称加密特点为可逆，并且加密解密都是使用同一个密钥，而非对称加密则是公钥私钥加解密模式这里不做讨论。



## aes加密五种模式

aes加密的方式有五种工作体制。

1.电码本模式（Electronic Codebook Book (ECB)）

这种模式主要是将明文划分为几个明文段，分块加密，但是加密密钥是相同的。

2.密码分组链接模式（Cipher Block Chaining (CBC)）

这种模式是先将明文切分成若干小段，然后每一小段与初始块或者上一段的密文段进行异或运算后，再与密钥进行加密。

3.计算器模式（Counter (CTR)）<br>
4.密码反馈模式（Cipher FeedBack (CFB)）<br>
5.输出反馈模式（Output FeedBack (OFB)）

其中分组如，aes-128-ecb即为16字节为一组，16字节即为128位。

其他三种模式较为复杂，本文仅讨论前两种加密的安全性。



## aes-ecb加密

[![](https://s2.ax1x.com/2019/03/10/A9pPu6.jpg)](https://s2.ax1x.com/2019/03/10/A9pPu6.jpg)

aes-ecb加密是将一段明文，按照固定长度分组，然后对每一个分组，按照算法使用固定的密钥进行加密。假设123456加密。那么123为一组加密，456为一组加密，然后两段明文加密后的密文拼在一起，就算完整的密文。

注意：这里每一组的加密都是使用相同的密钥，相同的算法，所以在这种机制下，很可能出现安全问题。

比如：在身份认证中，查询用户是否是管理员还是普通用户，如果is_root=1则为管理员，如果不为1则为普通用户，如果采用aes-ecb加密，对原文进行分组加密。

```
明文：user_id:1.000000 is_root:0（其中is_root来判断是否为管理员。）  然后用一段密钥加算法进行加密。
```

这种提交的加密数据是在cookie中提交，明文不可控，但是密文是可控的，但由于是进行分组进行，所以我们可以推算出每一分组明文对应的密文，假设明文八个一组来进行加密，分组后变为 （提示：仅仅是假设理想情况八位，实际并不是）

```
第一组：is_user 
第二组：1.000000 
第三组: is_root: 
第四组： 0（不够的八位自动填充）

其中user_id 通常情况下我们前端可以修改，进行修改为1.000000，此时原文被加密之后为四组 每组为八个数字的密文

假设加密后密文为  

c4ca4238a0b923820dcc509a6f75849b 在cookie中被提交，将密文分为四组

c4ca4238
a0b92382
0dcc509a
6f75849b
```

此时密文我们是可控的，如果正常提交，服务器解密之后为user_id:1.000000 is_root:0，很显然我们不是管理员，但是如果将第二组密文和第四组密文替换呢，那么user_id就是0，is_root就是1.000000。服务器就解析为user_id:0xxxxxxx(xx为填充字符) is_root:1.000000，显然我们不需要知道密钥，同样可以进行绕过。

还有一则在转账中，如果采用aes-128-ecb加密，在cookie中使用ecb分组加密，比如

付款人账户：<br>
XXX //假设密文abc<br>
收款人账户：<br>
XXX //假设密文efg

试想一下，一旦这个分组是刚好分为四组，我们仅仅将abc与efg交换，那不就造成了支付收款反转，几乎不需要什么技术就可以造成严重的攻击。

### <a class="reference-link" name="ctf-%E6%A1%88%E4%BE%8B"></a>ctf-案例

接下来以真实题目来进行详解。

ctf address：[https://mixer-f3834380.challenges.bsidessf.net/（国外的一道ctf）](https://mixer-f3834380.challenges.bsidessf.net/%EF%BC%88%E5%9B%BD%E5%A4%96%E7%9A%84%E4%B8%80%E9%81%93ctf%EF%BC%89)

[![](https://s2.ax1x.com/2019/03/10/ApRepR.png)](https://s2.ax1x.com/2019/03/10/ApRepR.png)

首先尝试输入admin admin 登陆。

[![](https://s2.ax1x.com/2019/03/10/Apg2Ps.png)](https://s2.ax1x.com/2019/03/10/Apg2Ps.png)

返回内容重点为红色框内的东西，需要使得第三个参数 is_admin=1即可获得flag，但是session cookie并不是这个题关注的点，接下来就是抓包分析参数。修改参数。

[![](https://s2.ax1x.com/2019/03/10/ApgXxx.png)](https://s2.ax1x.com/2019/03/10/ApgXxx.png)

经测试修改url，get cookie post传参都不能改变is_admin的值，所以只有一种可能，是在cookie里的user参数里加密了，然后传递给服务器，我们get参数传入的账号密码被服务器端加密，然后服务器返回来加密后的user信息。

接下来测试是何种加密，测试为aes-ecb加密，那么是如何确定的呢，

由于ecb是分组加密，所以一旦一组的密文我们修改了，其他组的密文解密之后是正常的，而被我们修改了的密文解密会是乱码，所以我们随便修改下user参数。

[![](https://s2.ax1x.com/2019/03/10/Ap2GQ0.png)](https://s2.ax1x.com/2019/03/10/Ap2GQ0.png)

可以看到报错，并且第一组的密文解密后是乱码，而其他组的加密解密后为正常，所以猜测这一定是aes-ecb的分组加密的方式，

此时，我们应该先确定分组，几个为一组，先破坏第一组加密然后破坏第二组加密，然后确定解密后json数据为，

```
`{`"first_name":"admin","last_name":"admin","is_admin":0`}`
```

总共为55个字符，

```
服务器密文为：d37c125ab4eae2ed02428d6d619016b06500bafffbeebe0c011977ad06c6946a45ba82569e93332195a36e61ae1fe26b325f7afd1eaa5ee8bb11efe6eebc5b54
```

为128个字符，五十五个字符补位为64个字符，分组测试破坏每一组，测试到一组明文16个字符，加密密文为32个字符。

明文分为四组，一组16个字符，密文分为四组，一组32个字符。

```
d37c125ab4eae2ed
02428d6d619016b0
6500bafffbeebe0c
011977ad06c6946a
45ba82569e933321
95a36e61ae1fe26b
325f7afd1eaa5ee8
bb11efe6eebc5b54
```

可控的范围是我们输入的账号密码 admin admin。

`{`“first_name”:” 为十五个字符，我们首先构造账号为 a1.0000000000000`}`

其中a是为了填充第一组，这样第一组就是`{`“first_name”:”a,这样剩下的1.0000000000000`}`就是十六个字符为一组，第二组就是1.0000000000000`}`，这样服务器加密后返回的第33-64位加密就是1.0000000000000`}`，我们让服务器帮我们加密，这样我们就不需要知道密钥和算法，让服务器帮我们加密任何我们想要的东西，提交数据。

[![](https://s2.ax1x.com/2019/03/10/Apfii4.md.png)](https://s2.ax1x.com/2019/03/10/Apfii4.md.png)

可以看到服务器返回了加密后的内容。我们截取第33位-64位字符。即为1.0000000000000`}`的密文。

```
3af6e4a9e05c702b02f9f4288c1c605c
```

接下来就是需要填充位数。我们让服务器解密的json数据最后的0｝为第65 66位，因为如果这样的话，前64位刚好是四组，65 66为一组，正好将它32位的密文替换成我们构造的密文。

`{`“first_name”:”admin”,”last_name”:”admin”,”is_admin”:0`}`

五十五位的字符串，我们让好账号变为admin12345678900,那么字符串就是66位，正好符合多余出来的两位是0｝，最后这两位被填充之后的密文同样是32位，这样就可以替换我们构造的32位密文。

[![](https://s2.ax1x.com/2019/03/10/AphF78.png)](https://s2.ax1x.com/2019/03/10/AphF78.png)

可以看到服务器构造成功得到flag。

总结一下上面思路，我们根据每一组的加密密文长度固定明文长度固定，所以填充位数，然后让我们想要的数据成为单独的一组，让服务器进行加密，这样我们就可控制任意明文加密，然后修改cookie里提交的密文，填充字节，让我们需要的密文位置成为单独的一组，然后替换我们之前构造的一组数据，这样就可以绕过。

此题值得一题的是双引号单引号反斜线等被过滤了，所以师傅们其他需要引入双引号等的不用尝试了。



## aes-cbc加密

这种模式是先将明文切分成若干小段，然后每一小段与初始块或者上一段的密文段进行异或运算后，再与密钥进行加密。aes-

[![](https://s2.ax1x.com/2019/03/10/Ap5bmq.png)](https://s2.ax1x.com/2019/03/10/Ap5bmq.png)

IV：用于随机化加密的比特块，保证即使对相同明文多次加密，也可以得到不同的密文。

秘钥：用于加密。

密文块0：第一组密文被加密后的内容。（同样也是第二组明文加密过程中的IV）

cbc加密方式不难理解，将一串明文进行分组，举例 123456789

123为第一组，456为第二组，789为第三组，将123与IV异或加密（加密中IV只在第一次异或有用），得到的异或后的密文与密钥加密，假设此时第一组加密的最终密文为abc，那么456先于第一组的密文abc异或加密，得到的异或密文在与密钥加密，假设第二组最终密文为def，往复循环，def与第三组明文异或，然后和密钥加密，假设密文ghi，那么最终密文就是

```
abcdefghi并且将iv发送。
```

其中值得一提的是初始始化向量IV每次随即初始化，所以即使相同的字符串也不会有相同的密文。

### <a class="reference-link" name="cbc%E5%AD%97%E8%8A%82%E5%8F%8D%E8%BD%AC%E6%94%BB%E5%87%BB"></a>cbc字节反转攻击

那么这种在这种加密的方式下，并不安全，问题出在异或加密这里，在讲解字节反转攻击前先了解下异或加密。

异或 xor 符号表示为 ^ ，计算机中 两个数字异或，相同为0，不同为1。 1^1=0 0^1=1

如果是字母异或加密，a^b，那么首先转化为ascii编码，然后二进制，对每一位进行异或得到的结果转为十进制，在ascii编码出来。

[![](https://s2.ax1x.com/2019/03/10/A9SRHS.png)](https://s2.ax1x.com/2019/03/10/A9SRHS.png)

异或有一个特性，任意值与自己本身做异或运算的结果都是0，任意值与0做异或运算的结果都是自己。本身a^b=乱七八糟，a^a则为空，但是a^a^任意字母=任意字母。

[![](https://s2.ax1x.com/2019/03/10/A93FN4.png)](https://s2.ax1x.com/2019/03/10/A93FN4.png)

[![](https://s2.ax1x.com/2019/03/10/A99MW9.png)](https://s2.ax1x.com/2019/03/10/A99MW9.png)

在CBC解密中，如图A是第一组的密文，B是第二组被解密的密文（未异或），C是明文。C=A^B。那么B=C^A，且A^B^C=0。如果我们更改A，A为我们可控的密文，C=A^B,如果我们使A=B^X，B=C^A,所以A=C^A^X,C=C^A^X^B=B^X^B=X。这里X是我们需要的任意字符，这便是CBC字节反转攻击的核心，这样一来C的明文就完全可控了。

### <a class="reference-link" name="%E7%AE%80%E5%8D%95%E7%9A%84%E7%99%BB%E5%BD%95-cbc%E5%AD%97%E8%8A%82%E5%8F%8D%E8%BD%AC"></a>简单的登录-cbc字节反转

原理说了很多，那么接下来实战一下。

实验吧题目：[http://ctf5.shiyanbar.com/web/jiandan/index.php](http://ctf5.shiyanbar.com/web/jiandan/index.php)

[![](https://s2.ax1x.com/2019/03/11/ACS5W9.md.png)](https://s2.ax1x.com/2019/03/11/ACS5W9.md.png)

首先，输入框随便输入，然后发送请求抓包，看到返回包的头请求有tips，test.php。访问test.php即可看到源码。

```
&lt;?php
define("SECRET_KEY", '***********');
define("METHOD", "aes-128-cbc");
error_reporting(0);
include('conn.php');
function sqliCheck($str)`{`
    if(preg_match("/\|,|-|#|=|~|union|like|procedure/i",$str))`{`
        return 1;
    `}`
    return 0;
`}`
function get_random_iv()`{`
    $random_iv='';
    for($i=0;$i&lt;16;$i++)`{`
        $random_iv.=chr(rand(1,255));
    `}`
    return $random_iv;
`}`
function login($info)`{`
    $iv = get_random_iv();
    $plain = serialize($info);
    $cipher = openssl_encrypt($plain, METHOD, SECRET_KEY, OPENSSL_RAW_DATA, $iv);//$plain为要加密的明文，METHOD加密方法，SECRET_KEY是秘钥，OPENSSL_RAW_DATA为数据格式，$iv随机生成的初始化向量。
    setcookie("iv", base64_encode($iv));
    setcookie("cipher", base64_encode($cipher));
`}`
function show_homepage()
`{`
    global $link;
    if(isset($_COOKIE['cipher']) &amp;&amp; isset($_COOKIE['iv']))
    `{`
        $cipher = base64_decode($_COOKIE['cipher']);
        $iv = base64_decode($_COOKIE["iv"]);

        if($plain = openssl_decrypt($cipher, METHOD, SECRET_KEY, OPENSSL_RAW_DATA, $iv))
        `{`
            $info = unserialize($plain) or die("&lt;p&gt;base64_decode('".base64_encode($plain)."') can't unserialize&lt;/p&gt;");
            $sql="select * from users limit ".$info['id'].",0";
            $result=mysqli_query($link,$sql);

            if(mysqli_num_rows($result)&gt;0  or die(mysqli_error($link)))`{`
                $rows=mysqli_fetch_array($result);
                echo '&lt;h1&gt;&lt;center&gt;Hello!'.$rows['username'].'&lt;/center&gt;&lt;/h1&gt;';
            `}`

            else`{`
                echo '&lt;h1&gt;&lt;center&gt;Hello!&lt;/center&gt;&lt;/h1&gt;';
            `}`
        `}`
        else
        `{`
            die("ERROR!");
        `}`
    `}`
`}`
if(isset($_POST['id']))`{`
    $id = (string)$_POST['id'];
    if(sqliCheck($id))
        die("&lt;h1 style='color:red'&gt;&lt;center&gt;sql inject detected!&lt;/center&gt;&lt;/h1&gt;");
    $info = array('id'=&gt;$id);
    login($info);
    echo '&lt;h1&gt;&lt;center&gt;Hello!&lt;/center&gt;&lt;/h1&gt;';
`}`else`{`
    if(isset($_COOKIE["iv"])&amp;&amp;isset($_COOKIE['cipher']))`{`
        show_homepage();
    `}`else`{`
        echo '&lt;body class="login-body" style="margin:0 auto"&gt;
                &lt;div id="wrapper" style="margin:0 auto;width:800px;"&gt;
                    &lt;form name="login-form" class="login-form" action="" method="post"&gt;
                        &lt;div class="header"&gt;
                        &lt;h1&gt;Login Form&lt;/h1&gt;
                        &lt;span&gt;input id to login&lt;/span&gt;
                        &lt;/div&gt;
                        &lt;div class="content"&gt;
                        &lt;input name="id" type="text" class="input id" value="id" onfocus="this.value=''" /&gt;
                        &lt;/div&gt;
                        &lt;div class="footer"&gt;
                        &lt;p&gt;&lt;input type="submit" name="submit" value="Login" class="button" /&gt;&lt;/p&gt;
                        &lt;/div&gt;
                    &lt;/form&gt;
                &lt;/div&gt;
            &lt;/body&gt;';
    `}`
`}`
?&gt;
```

前提：这一关不是单纯注入饶过的，肯定要利用cbc字节反转攻击。

1.首先直接看在哪里可以得到flag，没传入ID参数的时候，如果cookie建立了iv 和 cipher参数，那么就可以调用show_homepage，执行sql查询，flag在数据库里查询。

2.但是肯定要传参id，先生成iv 和 cipher，将id=X该数组进行序列化之后，以序列化结果和一个bs64编码随机数iv进行cbc加密生成密文cipher,加密算法为aes-128-cbc，此时就要考虑cbc字节反转了，128位，按十六字节分组。生成iv和cipher之后url编码返回请求头，生成细节参考自定义login函数。

3.sql查询语句拼接了一个0，所以我们只要注释掉0便可进行我们的查询。所以可以利用cbc字节翻转攻击更改密文，更改解密后的id，从而绕过进行sqlwaf，cookie传入参数 cipher和iv,base64解码然后aes解密，php反序列化，如果不能反序列化，则输出base64编码，否则就sql语句拼接查询。如果有结果回显，否则输出hello。

综上，只要我们能够CBC进行字节反转就可以执行sql查询，就可以进行查询flag。

接下来第一步首先要cbc字节反转，修改密文中的id。不妨先测试下位数，如果传入id=12（因为我们要修改为1#），则序列化后内容为

```
a:1:`{`s:2:"id";s:2:"12";`}`
```

由于我们需要分组，aes-128-cbc，128位16字节分组

```
第一组： a:1:`{`s:2:"id";s:
第二组： 2:"12";`}`
```

10中的0是第二组的第五个字符，所以需要更改第5个字符，右偏移四个字符，第一组也要向右偏移四个字符。接下来就是cbc字节反转脚本。

```
# -*- coding:utf8 -*-
from base64 import *
import urllib

cipher='fn060OBP%2FyLIGYrD9bi%2FlWWAS9RIWvEtALaV26kuB%2F8%3D'#加密后的密文

cipher_raw=b64decode(urllib.unquote(cipher))#首先urldecode解码，然后base64解码

cipher_raw_list=list(cipher_raw)#将解码的密文分组

py=4#偏移量为4
A=cipher_raw_list[py]#要异或第二组密文的位置
C='2'#第二组被替换的明文
X='#'#将第二组替换掉的明文

cipher_raw_list[py]=chr(ord(A)^ord(C)^ord(X))#将偏移量为4的替换。

cipher_new=''.join(cipher_raw_list)#使用''将每一个字符连接起来，
cipher_new=urllib.quote(b64encode(cipher_new))#将替换完的密文base64编码，urlencode编码。
print cipher_new#打印出最终密文
```

其中特意将ACX等变量对应上文所讲的参数。可参考上面cbc字节反转配合图来理解。然后生成反转后的密文：

```
fn060PFP/yLIGYrD9bi/lWWAS9RIWvEtALaV26kuB/8%3D
```

此时提交密文发送服务器会返回base64编码字符串无法反序列化。

[![](https://s2.ax1x.com/2019/03/12/APrM9I.png)](https://s2.ax1x.com/2019/03/12/APrM9I.png)

原因为下面这句。

[![](https://s2.ax1x.com/2019/03/11/ACeARf.md.png)](https://s2.ax1x.com/2019/03/11/ACeARf.md.png)

接下来我们需要修改IV，原理很简单，我们分为两组来进行加解密，第一组密文只参与第二组的异或，第一组修改完成后，第二组的解密是完全没有问题的，但是第一组被我们修改了一个字符，但是异或的IV还是原来的IV，必须要修改IV才能使第一组正常异或，得到结果。还是上述原理，三次异或，控制想要的结果。

这里在看图，

[![](https://s2.ax1x.com/2019/03/11/ACKCX8.md.png)](https://s2.ax1x.com/2019/03/11/ACKCX8.md.png)

A：这里特别要说明注意，A是我们第一次字节反转之后的明文（序列化状态）<br>
B：原来的IV<br>
C：字节反转后解密后的第一组（未被异或）<br>
D: 正常的序列化字符串 ‘a:1:`{`s:2:”id”;s:’<br>
E：新的IV

A=B^C,因为我们A是字节反转这里我们可以看到，IV是原来的IV，但是A和C都是字节反转后的，所以A必然是个无法反序列化的明文，我们修改B也就是IV，使得异或得到正常的序列化字符串。

B=A^C,我们需要得到的结果是D=E^C，而C=B^A，所以D=E^B^A,那么E=B^A^D。 //建议初学者自己多分析下逻辑，多写写，干想很头疼。

接下来是IV修改的脚本。

```
# -*- coding:utf8 -*-
__author__='pcat@chamd5.org'

from base64 import *
import urllib
iv='erUDGVSvM4Kab3ztg8vT8Q%3D%3D'
B=b64decode(urllib.unquote(iv))
D='a:1:`{`s:2:"id";s:'
A=b64decode('eFoXA0j/x2Em/bhfgeLzXjI6IjEjIjt9')
iv_new=''
for i in range(16):
    iv_new+=chr(ord(A[i])^ord(D[i])^ord(B[i]))
iv_new=urllib.quote(b64encode(iv_new))
print iv_new
```

替换掉原来的IV，即可正常sql查询。

[![](https://s2.ax1x.com/2019/03/12/APsMa4.md.png)](https://s2.ax1x.com/2019/03/12/APsMa4.md.png)

至此，此题的cbc反转我们已经完成了，剩下的注入原理一样，注入不是本题的目的，也就不再发剩下的脚本了。CBC还是要自己写一下用图理解一下。

其余加密问题，后续我会补充到本文。

参考：[https://www.yourhome.ren/index.php/sec/366.html](https://www.yourhome.ren/index.php/sec/366.html)<br>
参考：实验吧pcat师傅的writeup
