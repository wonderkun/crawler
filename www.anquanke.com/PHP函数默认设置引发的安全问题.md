> 原文链接: https://www.anquanke.com//post/id/153232 


# PHP函数默认设置引发的安全问题


                                阅读量   
                                **184581**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">9</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t010280844327bffd4e.jpg)](https://p1.ssl.qhimg.com/t010280844327bffd4e.jpg)

## 前言

暑假不学习，和咸鱼并无区别。今天刚好在发掘一下默认配置可能存在问题和一些容易触发漏洞的php函数，这里做一个总结。<br>

## in_array()函数

### <a class="reference-link" name="%E7%9B%B8%E5%85%B3%E7%9F%A5%E8%AF%86"></a>相关知识

查阅PHP手册：<br>
(PHP 4, PHP 5, PHP 7)<br>
in_array() — 检查数组中是否存在某个值<br>
大体用法为：

```
bool in_array ( mixed $needle , array $haystack [, bool $strict = FALSE ] )
```

而官方的解释也很有意思：<br>
大海捞针，在大海（haystack）中搜索针（needle），如果没有设置 strict 则使用宽松的比较。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E9%97%AE%E9%A2%98"></a>漏洞问题

我们注意到

```
bool $strict = FALSE
```

宽松比较如果不设置，默认是FALSE，那么这就会引来安全问题<br>
如果设置`$strict = True`:则 in_array() 函数还会检查 needle 的类型是否和 haystack 中的相同。<br>
那么不难得知，如果不设置，那么就会产生弱类型的问题<br>
例如：

```
&lt;?php
$whitelist = range(1, 24);
$filename='sky';
var_dump(in_array($filename, $whitelist));
?&gt;
```

[![](https://p2.ssl.qhimg.com/t018abb8965f13840d0.png)](https://p2.ssl.qhimg.com/t018abb8965f13840d0.png)

此时运行结果为false<br>
但是如果我们将filename改为1sky<br>[![](https://p1.ssl.qhimg.com/t01424511a642ee1ff2.png)](https://p1.ssl.qhimg.com/t01424511a642ee1ff2.png)成功利用弱比较，而绕过了这里的检测

### <a class="reference-link" name="%E5%85%B8%E5%9E%8B%E6%A1%88%E4%BE%8B"></a>典型案例

上面的实例已说明了问题，其实这个问题是存在于上次文件的检查的<br>
在php-security-calendar-2017-Wish List中

```
class Challenge `{`
    const UPLOAD_DIRECTORY = './solutions/';
    private $file;
    private $whitelist;

    public function __construct($file) `{`
        $this-&gt;file = $file;
        $this-&gt;whitelist = range(1, 24);
    `}`

    public function __destruct() `{`
        if (in_array($this-&gt;file['name'], $this-&gt;whitelist)) `{`
            move_uploaded_file(
                $this-&gt;file['tmp_name'],
                self::UPLOAD_DIRECTORY . $this-&gt;file['name']
            );
        `}`
    `}`
`}`

$challenge = new Challenge($_FILES['solution']);
```

我们不难看出，代码的意图上是想让我们只传数字名称的文件的<br>
而我们却可以用`1skyevil.php`这样的名称去bypass<br>
由于没有修改in_array的默认设置，而导致了安全问题<br>
可能这比较鸡肋，但在后续对文件的处理中，前一步产生了非预期，可能会直接影响后一步的操作

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E4%BF%AE%E5%A4%8D"></a>漏洞修复

将宽松比较设为true即可<br>[![](https://p4.ssl.qhimg.com/t0115f0ad8431fa62fe.png)](https://p4.ssl.qhimg.com/t0115f0ad8431fa62fe.png)可以看到，搜索的时候，直接要求前两个参数均为array<br>[![](https://p0.ssl.qhimg.com/t01dfb3947529464dfa.png)](https://p0.ssl.qhimg.com/t01dfb3947529464dfa.png)此时已经不存在弱比较问题



## filter_var()函数

### <a class="reference-link" name="%E7%9B%B8%E5%85%B3%E7%9F%A5%E8%AF%86"></a>相关知识

(PHP 5 &gt;= 5.2.0, PHP 7)<br>
filter_var — 使用特定的过滤器过滤一个变量

```
mixed filter_var ( mixed $variable [, int $filter = FILTER_DEFAULT [, mixed $options ]] )
```

虽然官方说这是过滤器，但是如果用这个函数进行过滤，并且相信他的结果，是非常愚蠢的

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E9%97%AE%E9%A2%98"></a>漏洞问题

比较常用的当属FILTER_VALIDATE_URL了吧，但是它存在非常多的过滤bypass<br>[![](https://p2.ssl.qhimg.com/t01b08e5038dc6881ae.png)](https://p2.ssl.qhimg.com/t01b08e5038dc6881ae.png)本应该用于check url是否合法的函数，就这样放过了可能导致SSRF的url<br>
类似的bypass还有：

```
0://evil.com:80$skysec.top:80/
0://evil.com:80;skysec.top:80/
```

详细SSRF漏洞触发可参考这篇文章：<br>[http://skysec.top/2018/03/15/Some%20trick%20in%20ssrf%20and%20unserialize()/](http://skysec.top/2018/03/15/Some%20trick%20in%20ssrf%20and%20unserialize()/)<br>
除此之外，还能触发xss

```
javascript://comment%0Aalert(1)
```

### <a class="reference-link" name="%E5%85%B8%E5%9E%8B%E6%A1%88%E4%BE%8B"></a>典型案例

```
// composer require "twig/twig"
require 'vendor/autoload.php';

class Template `{`
    private $twig;

    public function __construct() `{`
        $indexTemplate = '&lt;img ' .
            'src="https://loremflickr.com/320/240"&gt;' .
            '&lt;a href="`{``{`link|escape`}``}`"&gt;Next slide »&lt;/a&gt;';

        // Default twig setup, simulate loading
        // index.html file from disk
        $loader = new TwigLoaderArrayLoader([
            'index.html' =&gt; $indexTemplate
        ]);
        $this-&gt;twig = new TwigEnvironment($loader);
    `}`

    public function getNexSlideUrl() `{`
        $nextSlide = $_GET['nextSlide'];
        return filter_var($nextSlide, FILTER_VALIDATE_URL);
    `}`

    public function render() `{`
        echo $this-&gt;twig-&gt;render(
            'index.html',
            ['link' =&gt; $this-&gt;getNexSlideUrl()]
        );
    `}`
`}`

(new Template())-&gt;render();
```

这里不难看出是有模板渲染的，而模板渲染则有可能触发xss<br>
那么寻找可控点，不难发现

```
public function render() `{`
        echo $this-&gt;twig-&gt;render(
            'index.html',
            ['link' =&gt; $this-&gt;getNexSlideUrl()]
        );
    `}`
```

这里的Link是使用了`getNexSlideUrl()`的结果<br>
我们跟进这个函数

```
public function getNexSlideUrl() `{`
        $nextSlide = $_GET['nextSlide'];
        return filter_var($nextSlide, FILTER_VALIDATE_URL);
    `}`
```

这里的`nextSlide`使用就充分相信了filter_var()的过滤结果<br>
所以导致了XSS：

```
?nextSlide=javascript://comment%250aalert(1)
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E4%BF%AE%E5%A4%8D"></a>漏洞修复

不要轻易的相信filter_var()，它只能当做初步验证函数，结果不能当做是否进入if的后续程序的条件



## class_exists()函数

### <a class="reference-link" name="%E7%9B%B8%E5%85%B3%E7%9F%A5%E8%AF%86"></a>相关知识

(PHP 4, PHP 5, PHP 7)<br>
class_exists — 检查类是否已定义

```
bool class_exists ( string $class_name [, bool $autoload = true ] )
```

检查指定的类是否已定义。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E9%97%AE%E9%A2%98"></a>漏洞问题

上述操作表面上看起来似乎没有什么问题，和函数名一样，检查指定的类是否已定义<br>
但是关键点就在于选项上，可以选择调用或不调用`__autoload`<br>
更值得思考的是，该函数默认调用了`__autoload`<br>
什么是`__autoload`？<br>
PHP手册是这样描述的：<br>
在编写面向对象（OOP） 程序时，很多开发者为每个类新建一个 PHP 文件。 这会带来一个烦恼：每个脚本的开头，都需要包含（include）一个长长的列表（每个类都有个文件）。<br>
在 PHP 5 中，已经不再需要这样了。 spl_autoload_register() 函数可以注册任意数量的自动加载器，当使用尚未被定义的类（class）和接口（interface）时自动去加载。通过注册自动加载器，脚本引擎在 PHP 出错失败前有了最后一个机会加载所需的类。<br>
那么自动调用`__autoload`会产生什么问题呢？<br>
我们从下面的案例来看

### <a class="reference-link" name="%E5%85%B8%E5%9E%8B%E6%A1%88%E4%BE%8B"></a>典型案例

```
function __autoload($className) `{`
    include $className;
`}`

$controllerName = $_GET['c'];
$data = $_GET['d'];

if (class_exists($controllerName)) `{`
    $controller = new $controllerName($data['t'], $data['v']);
    $controller-&gt;render();
`}` else `{`
    echo 'There is no page with this name';
`}`

class HomeController `{`
    private $template;
    private $variables;

    public function __construct($template, $variables) `{`
        $this-&gt;template = $template;
        $this-&gt;variables = $variables;
    `}`

    public function render() `{`
        if ($this-&gt;variables['new']) `{`
            echo 'controller rendering new response';
        `}` else `{`
            echo 'controller rendering old response';
        `}`
    `}`
`}`
```

案例同样来自php-security-calendar-2017<br>
乍一看，这样的代码并不存在什么高危的问题，但实际上因为`class_exists()`的check自动调用了`__autoload()`<br>
所以我们可以调用php的内置类实现攻击，例如`SimpleXMLElement`<br>
正常来说，应该是可以这样触发render():

```
http://localhost/xxe.php?c=HomeController&amp;d[t]=sky&amp;d[v][new]=skrskr
```

可以得到回显

```
controller rendering new response
```

但此时我们可以使用`SimpleXMLElement`或是`simplexml_load_string`对象触发盲打xxe，进行任意文件读取<br>
构造：

```
simplexml_load_file($filename,'SimpleXMLElement')
```

即

```
c=simplexml_load_file&amp;d[t]=filename&amp;d[v]=SimpleXMLElement
```

即可<br>
而这里的$filename使用最常见的盲打XXE的payload即可<br>
这就不再赘述，详细可参看

```
https://blog.csdn.net/u011721501/article/details/43775691
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E4%BF%AE%E5%A4%8D"></a>漏洞修复

对于特点情况，可关闭自动调用

```
bool $autoload = false
```



## htmlentities()函数

### <a class="reference-link" name="%E7%9B%B8%E5%85%B3%E7%9F%A5%E8%AF%86"></a>相关知识

(PHP 4, PHP 5, PHP 7)<br>
htmlentities — 将字符转换为 HTML 转义字符

```
string htmlentities ( string $string [, int $flags = ENT_COMPAT | ENT_HTML401 [, string $encoding = ini_get("default_charset") [, bool $double_encode = true ]]] )
```

本函数各方面都和 htmlspecialchars() 一样， 除了 htmlentities() 会转换所有具有 HTML 实体的字符。<br>
如果要解码（反向操作），可以使用 html_entity_decode()。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E9%97%AE%E9%A2%98"></a>漏洞问题

从上述知识来看，该函数应该是用来预防XSS，进行转义的了<br>
但是不幸的是<br>[![](https://p3.ssl.qhimg.com/t01421c6fd9c0b0fde3.png)](https://p3.ssl.qhimg.com/t01421c6fd9c0b0fde3.png)该函数默认使用的是`ENT_COMPAT`<br>
即不会转义单引号，那么就可能产生非常严重的问题，例如如下案例

### <a class="reference-link" name="%E5%85%B8%E5%9E%8B%E6%A1%88%E4%BE%8B"></a>典型案例

```
$sanitized = [];

foreach ($_GET as $key =&gt; $value) `{`
    $sanitized[$key] = intval($value);
`}`

$queryParts = array_map(function ($key, $value) `{`
    return $key . '=' . $value;
`}`, array_keys($sanitized), array_values($sanitized));

$query = implode('&amp;', $queryParts);

echo "&lt;a href='/images/size.php?" .
    htmlentities($query) . "'&gt;link&lt;/a&gt;";
```

由于不会转义单引号<br>
我们可以随意闭合

```
&lt;a href='/images/size.php?htmlentities($query)'&gt;link&lt;/a&gt;
```

此时我们替换`htmlentities($query)`为

```
' onclick=alert(1) //
```

这样原语句就变成了

```
&lt;a href='/images/size.php?' onclick=alert(1) //'&gt;link&lt;/a&gt;
```

这样就成功的引起了xss<br>
故此最终的payload为

```
/?a'onclick%3dalert(1)%2f%2f=c

```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E4%BF%AE%E5%A4%8D"></a>漏洞修复

必要的时候加上`ENT_QUOTES`选项



## openssl_verify()函数

### <a class="reference-link" name="%E7%9B%B8%E5%85%B3%E7%9F%A5%E8%AF%86"></a>相关知识

(PHP 4 &gt;= 4.0.4, PHP 5, PHP 7)<br>
openssl_verify — 验证签名

```
int openssl_verify ( string $data , string $signature , mixed $pub_key_id [, mixed $signature_alg = OPENSSL_ALGO_SHA1 ] )
```

openssl_verify() 使用与pub_key_id关联的公钥验证指定数据data的签名signature是否正确。这必须是与用于签名的私钥相对应的公钥。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E9%97%AE%E9%A2%98"></a>漏洞问题

这个函数看起来是用于验证签名正确性的，怎么会产生漏洞呢？<br>
我们注意到它的返回值情况<br>[![](https://p4.ssl.qhimg.com/t0192bd3b09104db6b1.png)](https://p4.ssl.qhimg.com/t0192bd3b09104db6b1.png)其中，内部发送错误会返回-1<br>
我们知道if判断中，-1和1同样都可以被当做true<br>[![](https://p0.ssl.qhimg.com/t018a24735d6d00f170.png)](https://p0.ssl.qhimg.com/t018a24735d6d00f170.png)那么假设存在这样的情况<br>`if(openssl_verify())`<br>
那么它出现错误的时候，则同样可以经过check进入后续程序<br>
如何触发错误呢？<br>
实际上只要使用另一个与当前公钥不匹配的算法生成的签名，即可触发错误

### <a class="reference-link" name="%E5%85%B8%E5%9E%8B%E6%A1%88%E4%BE%8B"></a>典型案例

```
class JWT `{`
    public function verifyToken($data, $signature) `{`
        $pub = openssl_pkey_get_public("file://pub_key.pem");
        $signature = base64_decode($signature);
        if (openssl_verify($data, $signature, $pub)) `{`
            $object = json_decode(base64_decode($data));
            $this-&gt;loginAsUser($object);
        `}`
    `}`
`}`

(new JWT())-&gt;verifyToken($_GET['d'], $_GET['s']);
```

此时我们只需要使用一个不同于当前算法的公钥算法，生成一个有效签名，然后传入参数<br>
即可导致openssl_verify()发生内部错误，返回-1，顺利通过验证，达成签名无效依然可以通过的目的

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E4%BF%AE%E5%A4%8D"></a>漏洞修复

if判断中使用

```
if(openssl_verify()===1)
```

[![](https://p3.ssl.qhimg.com/t01372e5a180c19f3b1.png)](https://p3.ssl.qhimg.com/t01372e5a180c19f3b1.png)



## 后记

php作为一种功能强大的语言，它的库中还有许多默认配置会引发安全问题，还等我们一一去探索，由于本人很菜，不能一一枚举，在此抛砖引玉了！
