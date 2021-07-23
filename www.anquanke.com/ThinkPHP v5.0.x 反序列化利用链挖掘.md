> 原文链接: https://www.anquanke.com//post/id/196364 


# ThinkPHP v5.0.x 反序列化利用链挖掘


                                阅读量   
                                **1508830**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">17</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01d752a82478943c2f.png)](https://p5.ssl.qhimg.com/t01d752a82478943c2f.png)



## 前言

前几天审计某cms基于ThinkPHP5.0.24开发，反序列化没有可以较好的利用链，这里分享下挖掘ThinkPHP5.0.24反序列化利用链过程.该POP实现任意文件内容写入，达到getshell的目的



## 环境搭建

> Debian
apache2+mysql+ThinkPHP5.0.24+php5.6

下载地址：[http://www.thinkphp.cn/donate/download/id/1279.html](http://www.thinkphp.cn/donate/download/id/1279.html)

**文件：application/index/controller/Index.php**

```
&lt;?php
namespace appindexcontroller;


class Index
`{`
    public function index($input='')
    `{`
        echo "Welcome thinkphp 5.0.24";
        echo $input;
        unserialize($input);
    `}`
`}`
```

访问：[http://127.0.0.1/cms/tp50/public/index.php](http://127.0.0.1/cms/tp50/public/index.php)

[![](https://p5.ssl.qhimg.com/t01439e9ee609dd3ad1.png)](https://p5.ssl.qhimg.com/t01439e9ee609dd3ad1.png)



## 简述

Thinkphp 5.0.x反序列化最后触发RCE，要调用的`Request`类`__call`方法.

但是由于这里`self::$hook[$method]`不可控,无法成功利用

[![](https://p4.ssl.qhimg.com/t010031605aaa38dcaf.png)](https://p4.ssl.qhimg.com/t010031605aaa38dcaf.png)

我的思路是在找其他的`__call`，其他魔术方法搜了一圈没有可以进一步利用.

**文件：thinkphp/library/think/console/Output.php**

最后选择**Output类**中的`__call`方法，这里调用`block`方法.后续可以当做跳板

[![](https://p1.ssl.qhimg.com/t01dd1928abd4f549ac.png)](https://p1.ssl.qhimg.com/t01dd1928abd4f549ac.png)



## POP链分析

从头开始分析

**反序列化起点：thinkphp/library/think/process/pipes/Windows.php ** `removeFiles`方法

[![](https://p2.ssl.qhimg.com/t01d862ed8424e80fd5.png)](https://p2.ssl.qhimg.com/t01d862ed8424e80fd5.png)

跟进`removeFiles`方法

**跳板：**`file_exists`方法能够触发`__toString`魔术方法

[![](https://p0.ssl.qhimg.com/t01d689d1b5fe36fd76.png)](https://p0.ssl.qhimg.com/t01d689d1b5fe36fd76.png)

**跳板利用点：thinkphp/library/think/Model.php**

**Model抽象类**的 `__toString`

[![](https://p3.ssl.qhimg.com/t01b987d7712564196c.png)](https://p3.ssl.qhimg.com/t01b987d7712564196c.png)

跟进`toJson`方法至`toArray`方法

如下图**Model抽象类**的`toArray`方法，存在三个地方可以执行`__call`

但是我们目的是调用**Output类**的`__call`且能够继续利用,调试后选择**第三**处当做调板

```
$item[$key] = $value ? $value-&gt;getAttr($attr) : null;
```

[![](https://p4.ssl.qhimg.com/t01f819cef655132505.png)](https://p4.ssl.qhimg.com/t01f819cef655132505.png)

分析下如何达到该行代码

```
$item[$key] = $value ? $value-&gt;getAttr($attr) : null;
```

这里直接看**else分支**

[![](https://p0.ssl.qhimg.com/t01b9a671c924cb4763.png)](https://p0.ssl.qhimg.com/t01b9a671c924cb4763.png)

溯源`$values`变量，比较关键是下面两行

```
$modelRelation = $this-&gt;$relation();
$value         = $this-&gt;getRelationData($modelRelation);
```

`$modelRelation`值可以利用**Model类**中的`getError`方法

[![](https://p4.ssl.qhimg.com/t012f46c609296c6985.png)](https://p4.ssl.qhimg.com/t012f46c609296c6985.png)

跟进`getRelationData`方法，这里最后传入的`$modelRelation`需要`Relation`类型

最后返回值`$values`需要经过`if`语句判断

```
$this-&gt;parent &amp;&amp; !$modelRelation-&gt;isSelfRelation() &amp;&amp; get_class($modelRelation-&gt;getModel()) == get_class($this-&gt;parent)
```

全局搜索下，可以利用**HasOne类**

[![](https://p3.ssl.qhimg.com/t01b4134f7d78980e3a.png)](https://p3.ssl.qhimg.com/t01b4134f7d78980e3a.png)

最后`$attr`值，由`$bindAttr = $modelRelation-&gt;getBindAttr();`执行后的结果.

[![](https://p0.ssl.qhimg.com/t01b829dabd5fd73e72.png)](https://p0.ssl.qhimg.com/t01b829dabd5fd73e72.png)

跟进**OneToOne抽象类**`getBindAttr`方法，`binAttr`类变量可控.

[![](https://p2.ssl.qhimg.com/t01db502ede61e9e2b1.png)](https://p2.ssl.qhimg.com/t01db502ede61e9e2b1.png)

至此代码执行到`$item[$key] = $value ? $value-&gt;getAttr($attr) : null;`就能够执行**Output类**`__call`魔术方法

[![](https://p3.ssl.qhimg.com/t01a23665900a89a3ee.png)](https://p3.ssl.qhimg.com/t01a23665900a89a3ee.png)

跟进Output类`block`方法

[![](https://p0.ssl.qhimg.com/t01261f07b4a1120f53.png)](https://p0.ssl.qhimg.com/t01261f07b4a1120f53.png)

继续跟进`writelin`方法,最后会调用`write`方法

[![](https://p3.ssl.qhimg.com/t01e50584f231bbf8ea.png)](https://p3.ssl.qhimg.com/t01e50584f231bbf8ea.png)

这里`$this-&gt;handle`可控,全局搜索`write`方法，进一步利用

**定位到：thinkphp/library/think/session/driver/Memcached.php**

**类： Memcached**

[![](https://p5.ssl.qhimg.com/t01b8783cd195200abd.png)](https://p5.ssl.qhimg.com/t01b8783cd195200abd.png)

继续搜索可用`set`方法

**定位到：thinkphp/library/think/cache/driver/File.php**

**类：File**

最后可以直接执行`file_put_contents`方法写入shell

[![](https://p5.ssl.qhimg.com/t01317afcf74ccde1fb.png)](https://p5.ssl.qhimg.com/t01317afcf74ccde1fb.png)

`$filename`可控且可以利用伪协议绕过`exit`

[![](https://p2.ssl.qhimg.com/t017a88c29e6bcd8c70.png)](https://p2.ssl.qhimg.com/t017a88c29e6bcd8c70.png)

`$data`值比较棘手,这里有个坑，由于最后调用`set`方法中的参数来自先前调用的`write`方法

只能为`true`，且这里`$expire`只能为数值，这样文件内容就无法写**shell**

[![](https://p2.ssl.qhimg.com/t014fcc03e1afc0aae9.png)](https://p2.ssl.qhimg.com/t014fcc03e1afc0aae9.png)

继续执行,跟进下方的`setTagItem`方法

会再执行一次`set`方法，且这里文件内容`$value`通过`$name`赋值(文件名)

所以可以在文件名上做手脚

```
示例：php://filter/write=string.rot13/resource=./&lt;?cuc cucvasb();?&gt;
```

[![](https://p3.ssl.qhimg.com/t01594c498bc4c8c77d.png)](https://p3.ssl.qhimg.com/t01594c498bc4c8c77d.png)



## POP链(图)

[![](https://p1.ssl.qhimg.com/t01811445c8ddbe04a2.png)](https://p1.ssl.qhimg.com/t01811445c8ddbe04a2.png)



## EXP

```
马赛克
```



## 复现

写入文件

实战是需要找个可写目录

[![](https://p3.ssl.qhimg.com/t01851bfc0b629ec565.png)](https://p3.ssl.qhimg.com/t01851bfc0b629ec565.png)

读取文件

[![](https://p3.ssl.qhimg.com/t0165cb628d7913a149.png)](https://p3.ssl.qhimg.com/t0165cb628d7913a149.png)



## 结语

感谢@水泡泡师傅解答问题

整条POP分析下来挺有趣,希望师傅们喜欢.
