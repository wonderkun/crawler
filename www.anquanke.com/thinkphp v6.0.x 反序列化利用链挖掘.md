> 原文链接: https://www.anquanke.com//post/id/187393 


# thinkphp v6.0.x 反序列化利用链挖掘


                                阅读量   
                                **668066**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01a996657b114f626d.jpg)](https://p5.ssl.qhimg.com/t01a996657b114f626d.jpg)



## 0x00 前言

上一篇分析了tp 5.2.x的反序列化利用链挖掘，顺着思路，把tp6.0.x也挖了。有类似的地方，也有需要重新挖掘的地方。



## 0x01 环境准备

采用composer安装6.0.*-dev版本

composer create-project topthink/think=6.0.x-dev v6.0



## 0x02 利用链分析

### <a name="header-n8"></a>背景回顾

拿到v6.0.x版本，简单的看了一下，有一个好消息和一个坏消息。

好消息是5.2.x版本函数动态调用的反序列化链后半部分，还可以利用。

坏消息是前面5.1.x，5.2.x版本都基于触发点Windows类的__destruct,好巧不巧的是6.0.x版本取消了Windows类。这意味着我们得重新找一个合适的起始触发点，才能继续使用上面的好消息。

### <a name="header-n12"></a>vendor/topthink/think-orm/src/Model.php 新起始触发点

为了节省篇幅，后文不再重复介绍触发__toString函数后的利用链，这部分同5.2.x版本相同(不过wonderkun师傅的利用链已失效，动态函数调用的利用链还能用)。

通常最好的反序列化起始点为__destruct、__wakeup，因为这两个函数的调用在反序列化过程中都会自动调用，所以我们先来找此类函数。这里我找了vendor/topthink/think-orm/src/Model.php的__destruct函数。

```
public function __destruct()
`{`
    if ($this-&gt;lazySave) `{`// 构造lazySave为true，进入save函数
        $this-&gt;save();
    `}`
`}`

public function save(array $data = [], string $sequence = null): bool
`{`
  // ...
  if ($this-&gt;isEmpty() || false === $this-&gt;trigger('BeforeWrite')) `{`
    return false;
  `}`
  
  $result = $this-&gt;exists ? $this-&gt;updateData() : $this-&gt;insertData($sequence);
  // ...
`}`
```

首先构造lazySave的值为true,从而进入save函数。

这次触发点位于updateData函数内，为了防止前面的条件符合，而直接return，我们首先需要构造相关参数

```
public function isEmpty(): bool
`{`
    return empty($this-&gt;data);
`}`

protected function trigger(string $event): bool
`{`
  if (!$this-&gt;withEvent) `{`
    return true;
  `}`
  // ...
```

其中需保证isEmpty返回false，以及$this-&gt;trigger(‘BeforeWrite’)返回true
1. 构造$this-&gt;data为非空数组
1. 构造$this-&gt;withEvent为false
1. 构造$this-&gt;exists为true
从而进入我们需要的updateData函数，来看一下该函数内容

```
protected function updateData(): bool
`{`
    // 事件回调
    if (false === $this-&gt;trigger('BeforeUpdate')) `{`// 此处前面已符合条件
        return false;
    `}`

    // ...

    // 获取有更新的数据
    $data = $this-&gt;getChangedData();

    if (empty($data)) `{`
        // 关联更新
        if (!empty($this-&gt;relationWrite)) `{`
            $this-&gt;autoRelationUpdate();
        `}`
        return true;
    `}`
       // ...
    // 检查允许字段
    $allowFields = $this-&gt;checkAllowFields(); // 触发__toString
```

同样的，为了防止提前return，需要符合$data非空，来看一下getChangedData

```
public function getChangedData(): array
`{`
    $data = $this-&gt;force ? $this-&gt;data : array_udiff_assoc($this-&gt;data, $this-&gt;origin, function ($a, $b) `{`
        if ((empty($a) || empty($b)) &amp;&amp; $a !== $b) `{`
            return 1;
        `}`

        return is_object($a) || $a != $b ? 1 : 0;
    `}`);

    // ...

    return $data;
`}`
```

这里我们可以强行置$this-&gt;force为true，直接返回我们前面构造的非空$this-&gt;data

这样，我们就成功到了调用checkAllowFields的位置

```
protected function checkAllowFields(): array
`{`
    // 检测字段
    if (empty($this-&gt;field)) `{`
        if (!empty($this-&gt;schema)) `{`
            $this-&gt;field = array_keys(array_merge($this-&gt;schema, $this-&gt;jsonType));
        `}` else `{`
            $query = $this-&gt;db();// 最终的触发__toString的函数
            $table = $this-&gt;table ? $this-&gt;table . $this-&gt;suffix : $query-&gt;getTable();

            $this-&gt;field = $query-&gt;getConnection()-&gt;getTableFields($table);
        `}`

        return $this-&gt;field;
    `}`
       // ...
`}`
```

同样，为了到$this-&gt;db()函数的调用，需要
1. 构造$this-&gt;field为空
1. 构造$this-&gt;schema为空
其实这两个地方不需要构造，默认都为空

最终，我们终于到了可以触发__toString的位置

```
public function db($scope = []): Query
`{`
    /** @var Query $query */
    $query = self::$db-&gt;connect($this-&gt;connection) 
        -&gt;name($this-&gt;name . $this-&gt;suffix)// toString
        -&gt;pk($this-&gt;pk);
```

看到熟悉的字符串拼接了嘛！！！

不过为了达到该出拼接，我们还是得首先满足connect函数的调用。此处代码就不说了，置$this-&gt;connection为mysql即可。接下来，不管是设$this-&gt;name还是$this-&gt;suffix为最终的触发__toString的对象，都会有同样的效果。

后续的思路，就是原来vendor/topthink/think-orm/src/model/concern/Conversion.php的__toString开始的利用链，不在叙述。

我把exp集成到了[phpggc](https://github.com/wh1t3p1g/phpggc)上，使用如下命令即可生成

```
./phpggc -u ThinkPHP/RCE2 'phpinfo();'
```

这里由于用到了SerializableClosure，需要使用编码器编码，不可直接输出拷贝利用。
