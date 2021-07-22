> 原文链接: https://www.anquanke.com//post/id/215349 


# PHP mt_rand 伪随机数安全探讨


                                阅读量   
                                **231617**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t010d602da47108fd87.jpg)](https://p3.ssl.qhimg.com/t010d602da47108fd87.jpg)



## 概念

php中 mt_rand 函数可用于生成伪随机数，但是伪随机数是可被预测的。

mt_rand 是通过撒播随机数种子来生成随机数的，随机数种子范围是 unsigned int，即 0 – 4294967295。

mt_rand 生产的随机数在同一个句柄中，只播撒一次种子，之后生成的随机数都使用同一个种子进行生成。<br>
所以说只要爆破到了正确的种子，即可预测生产的随机数。

种子相同、PHP版本（确切的说是PHP内核中 mt_rand的代码逻辑）相同，生成的随机数都是一样的。理论上来说只要拿到了生成的随机数，我们就可以在本地进行种子的爆破。

备注：本次实验使用的PHP版本为 PHP-5.6



## mt_rand源码翻阅

关于只撒播一次种子这一点我们可以看下 PHP 关于 mt_rand 的源码：

github：[https://github.com/php/php-src](https://github.com/php/php-src)

mt_rand 的源码在 /ext/standard/rand.c 中：

[![](https://p4.ssl.qhimg.com/t01adc178d57d023257.png)](https://p4.ssl.qhimg.com/t01adc178d57d023257.png)

看到一个很明显的调用 `php_mt_srand` 函数的代码段。先判断了 `BG(mt_rand_is_seeded)` 再调用 php_mt_srand函数。

直接从字面意义上看，`mt_rand_is_seeded` 似乎就是一个标志位，用于判断是否已经播过种。而 `php_mt_srand` 似乎就是 php的播种函数 `mt_srand`。



## 只播一次种

验证一下，首先，我们看看BG函数是个什么东西：

找BG函数的直接跳转跳转不过去的话，就直接看 `rand.c` 文件中引入了什么文件：

[![](https://p4.ssl.qhimg.com/t010c6f8f7f081cbb0b.png)](https://p4.ssl.qhimg.com/t010c6f8f7f081cbb0b.png)

引入了4个自定义的头文件，我们再分别去这四个文件中进行搜索关键字 `BG`。最终在 `basic_functions.h` 中找到 `BG`。`BG` 是一个宏定义：

[![](https://p5.ssl.qhimg.com/t01d5e4ba3e10d85ed7.png)](https://p5.ssl.qhimg.com/t01d5e4ba3e10d85ed7.png)

宏定义简单理解就是把 **传入的参数值** 与 **参数名** 进行 **替换** 并返回， `mt_rand` 调用 `BG` 的时候是这样写的：

[![](https://p5.ssl.qhimg.com/t01868522e4e1e63b77.png)](https://p5.ssl.qhimg.com/t01868522e4e1e63b77.png)

传入的参数值就是 `mt_rand_is_seeded`，在宏定义 `BG` 中就变成了

```
宏定义代码：
#define BG(v) (basic_globals.v)
调用BG：
BG(mt_rand_is_seeded)
那么在宏定义代码中，v 就变成了 mt_rand_is_seeded，宏定义将返回：
basic_globals.mt_rand_is_seeded
```

而下面一行是引用在外处的 `php_basic_globals` 类型的变量 `basic_globals`，`basic_globals` 具体在哪个源文件我们可以不用管。我们只需要知道`php_basic_globals` 类型 是一个结构体。结构体就像一个数组，获取结构体中的元素可以使用 “.” 来获取对应名称元素的值。

[![](https://p4.ssl.qhimg.com/t011bf0a8cd668a84a1.png)](https://p4.ssl.qhimg.com/t011bf0a8cd668a84a1.png)

宏定义最终替换成了 `basic_globals.mt_rand_is_seeded` 并返回。

意思是获取 `php_basic_globals` 类型的 `basic_globals` 中 `mt_rand_is_seeded` 元素 的值并返回。

而 `mt_rand_is_seeded` 在 结构体 `php_basic_globals` 有这么一段注释：

[![](https://p5.ssl.qhimg.com/t01a0a044f73f8b385c.png)](https://p5.ssl.qhimg.com/t01a0a044f73f8b385c.png)

```
Whether mt_rand() has been seeded     #mt_rand 是否已经进行播过种
```

`zend_bool` 类型就是一个普通的 `Char` 类型：

ps：在sublime 中鼠标放在代码上面，如果可以跳转的话会列出可跳转的文件哦。

[![](https://p4.ssl.qhimg.com/t019ce1ed71ccb4ed65.png)](https://p4.ssl.qhimg.com/t019ce1ed71ccb4ed65.png)

这样就知道 `BG宏定义` 的作用了：

用来返回在 `php_basic_globals` 类型结构体变量 `basic_globals` 中指定的元素值。

而 `BG(mt_rand_is_seeded)`，返回的是 `mt_rand` 是否已经播过种。如果没有播种，才会调用 `php_mt_srand`

我们继续简单看下 php_mt_srand 的逻辑。

[![](https://p5.ssl.qhimg.com/t011c87d2ba11abd0de.png)](https://p5.ssl.qhimg.com/t011c87d2ba11abd0de.png)

前两行代码猜测就是用来播种的，播完种后，将会将 mt_rand_is_seeded 的值设置为 1

由此可以准确下结论：**mt_rand 只播种一次**。



## PHP cli 中进行 mt_rand 种子爆破

说到PHP mt_rand 种子爆破，就不得不提到专门进行这项工作的神器 php_mt_seed，速度极快。

下载地址：[https://www.openwall.com/php_mt_seed/](https://www.openwall.com/php_mt_seed/)

写个测试的PHP文件：

```
&lt;?php
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
?&gt;
```

使用php cli 运行：

[![](https://p2.ssl.qhimg.com/t01a70163ed44e3b96e.png)](https://p2.ssl.qhimg.com/t01a70163ed44e3b96e.png)

取第一个随机数 2114192623。使用 php_mt_seed 进行爆破：

[![](https://p5.ssl.qhimg.com/t01cec8536f800f42cd.png)](https://p5.ssl.qhimg.com/t01cec8536f800f42cd.png)

进行手动播种测试：

[![](https://p0.ssl.qhimg.com/t019408ed2d0f0667e0.png)](https://p0.ssl.qhimg.com/t019408ed2d0f0667e0.png)

生成的随机数与第一次生成的一样。说明爆破到了正确的种子。



## Web服务器 与 PHP

为什么 PHP使用Web服务器运行 和 PHP cli运行 要分开两个标题呢。不是一样的原理嘛？获取到第一个随机数值进行爆破？<br>
原理是一样的，只不过这里有一个坑。。。。

### <a class="reference-link" name="PHP%E8%BF%9B%E7%A8%8B"></a>PHP进程

当PHP运行在Web服务器上时，服务器与PHP之间是通过进程来进行通信。除了服务器使用 `CGI模式`（每次请求都调用php.exe、解析php.ini）运行PHP。其他方式如`Fast-cgi` 或 `mod_php` 方式，都会创建一个类似 **连接池** 一样的东西，提高效率。

连接池的存在相当于 **反复利用同一个** PHP进程。如果请求量稍微大一点的话，或者说是我们自己请求多了一两次。这样同一个PHP进程就会被反复调用好几次。而 mt_rand 在同一个进程中只播一次种。这种情况下我们就无法拿到第一次请求时的 mt_rand 随机数值，便无法正确爆破种子。

可以使用 PHP 内置函数 `getmypid` 获取到当前PHP进程id，从而判断服务器调用的 PHP进程 是新进程还是旧进程

代码：

```
&lt;?php
echo getmypid();
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
?&gt;
```

重启 apache 服务器（为了把之前可能开的 PHP 进程弄没），再去访问

[![](https://p4.ssl.qhimg.com/t0118b0ba255f268fd8.png)](https://p4.ssl.qhimg.com/t0118b0ba255f268fd8.png)

可以看到第二次访问和第四次访问 pid 都相同。取 pid 1031 中产生的第一个 mt_rand 随机数进行种子爆破：

[![](https://p1.ssl.qhimg.com/t01eb4e7e41cb11d0ff.png)](https://p1.ssl.qhimg.com/t01eb4e7e41cb11d0ff.png)

得到种子之后手动播种验证：

```
&lt;?php
echo getmypid();
mt_srand(2828230886);
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
//两次请求调用同样pid的PHP进程
//其中 第二次请求生成的随机数
//应是 顺着 第一次请求的随机数继续生成
//而非重新播种
echo '================'; 
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
var_dump(mt_rand());
?&gt;
```

[![](https://p0.ssl.qhimg.com/t01901753230dc171ee.png)](https://p0.ssl.qhimg.com/t01901753230dc171ee.png)

正因这样的神奇之处，我们进行随机数种子爆破时，如果运气不好没有取到第一次调用 PHP进程生成的 mt_rand 随机数，那就无法正确爆破出正确的种子。



## PHPCMS auth_key

PHPCMS在9.6.2以及之后修复了由于 `mt_rand` 而导致的 `auth_key` 可爆破。

下一个 9.6.1的进行简单的审计。github：[https://github.com/forget-code/phpcms](https://github.com/forget-code/phpcms)

先重启一下apache回收掉PHP进程

PHPCMS生成 `auth_key` 的逻辑在 `/install/install.php` 中。前面的逻辑都很简单就不一一带入。有兴趣的可自行下载看看。这里讨论生成以及爆破 `auth_key` 的过程

PHPCMS 调用自写的 `random` 函数生成 `cookie_pre` 和 `auth_key`

```
$cookie_pre = random(5, 'abcdefghigklmnopqrstuvwxyzABCDEFGHIGKLMNOPQRSTUVWXYZ').'_';
$auth_key = random(20, '1294567890abcdefghigklmnopqrstuvwxyzABCDEFGHIGKLMNOPQRSTUVWXYZ');
```

random 函数逻辑如下：

```
function random($length, $chars = '0123456789') `{`
    $hash = '';
    $max = strlen($chars) - 1;
    for($i = 0; $i &lt; $length; $i++) `{`
        //生成 $hash原理是从传入的字符串中随机取下标
        $hash .= $chars[mt_rand(0, $max)];
    `}`
    return $hash;
`}`
```

`$cookie_pre` 是在PHPCMS安装完后前台能够获取到的。只有五位。<br>
而 `$auth_key` 是 PHPCMS在鉴权的时候需要使用的关键密钥。这段代码中由于采取了 `mt_rand` 来生成随机数下标。我们可以很简单的通过 `cookie_pre` 爆破得到种子，再通过种子推算 `$auth_key` 的值。

把这段关键代码拷出来写一个 `demo.php`。

```
&lt;?php
function random($length, $chars = '0123456789') `{`
    $hash = '';
    $max = strlen($chars) - 1;
    for($i = 0; $i &lt; $length; $i++) `{`
        $hash .= $chars[mt_rand(0, $max)];//生成 $hash原理是从传入的字符串中随机取下标
    `}`
    return $hash;
`}`
$cookie_pre = random(5, 'abcdefghigklmnopqrstuvwxyzABCDEFGHIGKLMNOPQRSTUVWXYZ').'_';
$auth_key = random(20, '1294567890abcdefghigklmnopqrstuvwxyzABCDEFGHIGKLMNOPQRSTUVWXYZ');
var_dump($cookie_pre);
var_dump($auth_key);
?&gt;
```

[![](https://p5.ssl.qhimg.com/t017ce370e920f89a26.png)](https://p5.ssl.qhimg.com/t017ce370e920f89a26.png)

如果我们想使用 `mt_seed` 进行爆破的话，直接 `./php_mt_seed qoOMZ` 是么得的，我们需要整理成符合 `php_mt_seed` 爆破的格式。

查看 `php_mt_seed` 文档 [https://www.openwall.com/php_mt_seed/README](https://www.openwall.com/php_mt_seed/README)

发现符合整理 `auth_key` 生成规则的PHP脚本：

```
&lt;?php
//需要修改成对应PHPCMS cookie_pre传入的字符串，本次案例为 abcdefghigklmnopqrstuvwxyzABCDEFGHIGKLMNOPQRSTUVWXYZ
$allowable_characters = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789';
$len = strlen($allowable_characters) - 1;
//传入PHPCMS生成好的cookie_pre，本次案例为 qoOMZ
$pass = $argv[1];
for ($i = 0; $i &lt; strlen($pass); $i++) `{`
    //获取对应字符在字符串中的位置，也就相当于逆向推出 mt_rand 生成的值
    $number = strpos($allowable_characters, $pass[$i]);
    //输出php_mt_seed进行种子爆破所需要的格式。
    // 0 $len 应该是在爆破破解的时候，作为 mt_rand 的范围参数
    echo "$number $number 0 $len  ";
`}`
echo "\n";
?&gt;
```

生成符合爆破规则的字符串

[![](https://p5.ssl.qhimg.com/t0108932c35f3a502d0.png)](https://p5.ssl.qhimg.com/t0108932c35f3a502d0.png)

使用 php_mt_seed 进行爆破：

[![](https://p3.ssl.qhimg.com/t0153ca94c6eaaab603.png)](https://p3.ssl.qhimg.com/t0153ca94c6eaaab603.png)

手动播种，测试是否是正确种子：

[![](https://p5.ssl.qhimg.com/t019c3c41ef58130f31.png)](https://p5.ssl.qhimg.com/t019c3c41ef58130f31.png)

种子正确。

[![](https://p3.ssl.qhimg.com/t0109a0bb80092b2a27.png)](https://p3.ssl.qhimg.com/t0109a0bb80092b2a27.png)

### <a class="reference-link" name="%E7%BB%86%E8%8A%82%E6%B3%A8%E6%84%8F%EF%BC%9A"></a>细节注意：

如果 mt_srand 写在了函数 random 里面的话，将无法获取正确值：

[![](https://p0.ssl.qhimg.com/t019e751a7ff6344aaa.png)](https://p0.ssl.qhimg.com/t019e751a7ff6344aaa.png)

[![](https://p3.ssl.qhimg.com/t01cc709d7b7518c49d.png)](https://p3.ssl.qhimg.com/t01cc709d7b7518c49d.png)

生成 `cookie_pre` 是正确的，但 `auth_key` 是错误的。

这是因为，第二次调用 `random` 时，正常情况下 `mt_rand` 应该顺着第一次调用的随机数种子继续生成。但由于 `mt_srand` 写在了函数中。导致重新播种。



## 总结

`mt_rand` 生成的是伪随机数。所以如果想用在类似 token 或者密钥 之类的地方。想要生成一个不会被猜测到的随机数的话，建议可以与时间戳函数相结合，提高不可预测性。

不过也由于服务器与PHP之间交互的微妙关系，爆破种子的时候如果爆出来的不能用的话，也么的办法了。
