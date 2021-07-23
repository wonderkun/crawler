> 原文链接: https://www.anquanke.com//post/id/225794 


# TP诸多限制条件下如何getshell


                                阅读量   
                                **112912**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01add45b14847b29f5.jpg)](https://p0.ssl.qhimg.com/t01add45b14847b29f5.jpg)



## 前言

先说说2020_n1CTF的web题Easy_tp5复现问题。

这个题在保留thinkphp的RCE点的同时，并且RCE中ban掉许多危险函数，只能允许单参数的函数执行。对于现在在网络中流传的文件包含的点也增加了限制。

smile yyds!

先说一下这个题限制条件：
- thinkphp版本：5.0.0
- php版本：7
- 对于包含文件增加了限制
[![](https://p5.ssl.qhimg.com/t01bb7f311f5f08a060.png)](https://p5.ssl.qhimg.com/t01bb7f311f5f08a060.png)
- ban掉所有的单参数危险函数
[![](https://p4.ssl.qhimg.com/t0170cc50a633bea306.png)](https://p4.ssl.qhimg.com/t0170cc50a633bea306.png)
- 设置open_basedir为web目录
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01597b83f027d7714a.png)
- 设置仅在public目录下可写
[![](https://p3.ssl.qhimg.com/t014ee26a4bb7718dd8.png)](https://p3.ssl.qhimg.com/t014ee26a4bb7718dd8.png)

在TP5.0.0的中，目前公布的只是存在利用Request类其中变量被覆盖导致RCE。如果ban掉单参数可利用函数那么只能用文件包含，但是文件包含做了限制不能包含log文件，所以只能从别的方面入手。

这些限制都太大了，所以需要想办法去上传一个shell来完成后续绕disable_function。

首先TP5.0.0目前只存在通过覆盖Request中的某些变量导致RCE，其余细节不再赘述，我们看看大概代码执行点在哪里。

[![](https://p3.ssl.qhimg.com/t01099ebc02f307fd5a.jpg)](https://p3.ssl.qhimg.com/t01099ebc02f307fd5a.jpg)

call_user_func是代码执行点，我们基本上所有PHP自带的可利用函数基本被ban掉，所以我们需要从自写的函数调用来入手，首先我们需要看下这个点。可回调函数不仅仅指的是简单函数，还可以是一些对象的方法，包括静态方法。

[![](https://p5.ssl.qhimg.com/t0199ef121fc4e5a54e.png)](https://p5.ssl.qhimg.com/t0199ef121fc4e5a54e.png)



## 方法一 thinkphplibrarythinkBuild::module

我们可以这样通过调用这个类的静态方法module，来实现写文件的操作。

[![](https://p3.ssl.qhimg.com/t01e7fcf925a0dac586.png)](https://p3.ssl.qhimg.com/t01e7fcf925a0dac586.png)

我们先看看这个该怎么走，我们看到这个mkdir是在application创建目录，但是由于权限问题肯定无法创建。根据TP报错即退出的机制从而中断执行。那么我们可以通过../public/test来创建目录。

我们会进入到buildhello函数中。

[![](https://p0.ssl.qhimg.com/t01dc74d7bb28261b31.jpg)](https://p0.ssl.qhimg.com/t01dc74d7bb28261b31.jpg)

走完流程发现我们可以在public创建了一个test模块，同样看到test/controller/Index.php中我们所写的../public/test保存了下来那么我们就绕过，但是执行完之后会发现一些语法错误导致代码不能执行。

[![](https://p0.ssl.qhimg.com/t0142f097ba2149e802.jpg)](https://p0.ssl.qhimg.com/t0142f097ba2149e802.jpg)

由于这部分内容可控那我们就把他变得符合语法执行，我们可以这么做test;eval($_POST[a]);#/../../public/test;，这样就符合语法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0124dd608b86cc6750.png)

但是还有一个问题需要解决，就是我们这样的payload会设置一个不存在目录从而可以符合语法并且加入eval函数。但是现在还存在一个跨越不存在目录的问题。

[![](https://p1.ssl.qhimg.com/t01c7b25ecf6e57122e.png)](https://p1.ssl.qhimg.com/t01c7b25ecf6e57122e.png)
- linux环境
[![](https://p3.ssl.qhimg.com/t0168321cfd43c90a5d.png)](https://p3.ssl.qhimg.com/t0168321cfd43c90a5d.png)
- win环境
[![](https://p1.ssl.qhimg.com/t012c20b9e9e54a1313.jpg)](https://p1.ssl.qhimg.com/t012c20b9e9e54a1313.jpg)

在Linux中不能创建不存在的目录，但是在win下就可以。但是报错是warning，并不会中断执行，并且在bindhello函数中我们会看到：

[![](https://p3.ssl.qhimg.com/t01d942582e1b15b621.jpg)](https://p3.ssl.qhimg.com/t01d942582e1b15b621.jpg)

其中mkdir函数存在recursive参数为true，允许递归创建多级嵌套的目录。这样就可以使mkdir中使用不存在的目录就可以进行绕过。但是现在有个问题：前面的mkdir中的warning报错被TP捕获到直接会退出无法执行后面的内容，那么我们就需要使用一些办法进行抑制报错。我们经常做题会用到一个函数error_reporting，我们可以使用error_reporting(0)抑制报错。

我们再回到代码执行点，我们发现call_user_func函数执行完的值会执行循环再次回到call_user_func()中当回调函数的参数进行使用。因此需要考虑一下怎么调整才能让我们执行并且抑制报错。

payload如下可示：

[![](https://p3.ssl.qhimg.com/t01403f35056b3250de.png)](https://p3.ssl.qhimg.com/t01403f35056b3250de.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c08ea3e183fb464a.png)



## 方法二 使用注释符绕过语法产生的错误

payload如下：

[![](https://p1.ssl.qhimg.com/t01a0ce54775220c8f2.jpg)](https://p1.ssl.qhimg.com/t01a0ce54775220c8f2.jpg)

这样就会使用注释符注释掉后面的语法错误，然后使用?&gt;包裹住，后面跟上自己用的payload即可。但是这样会产生一个问题，无法在win环境下使用，win下文件夹中不能带这些字符/  : * ? ” &lt; &gt; |



## 方法三 文件包含&amp;php伪协议

这种操作就是，我们通过之前的thinkBuild::module写文件进去，写入的内容是我们rot13编码过的。然后通过think__include_file调用我们写入文件的内容，因为这个过滤不够完全，可以让我们包含我们所写的内容。

[![](https://p1.ssl.qhimg.com/t0186c4521f6d6ff702.jpg)](https://p1.ssl.qhimg.com/t0186c4521f6d6ff702.jpg)

[![](https://p4.ssl.qhimg.com/t01ff2997364cef7b6d.png)](https://p4.ssl.qhimg.com/t01ff2997364cef7b6d.png)



## 方法四 覆盖日志路径写入

因为题目将error_log函数ban掉了，所以这个非预期解是在不ban掉error_log函数的情况下所实现的。

payload具体如下：

[![](https://p5.ssl.qhimg.com/t01488f9833fdc00a03.png)](https://p5.ssl.qhimg.com/t01488f9833fdc00a03.png)

1.通过json_decode使得我们传入的`{`“type”:”File”, “path”:”/var/www/html/null/public/logs”`}`转换成内置类stdClass的一个对象。

2.再通过get_object_vars将其转换成数组传入到thinkLog::init中。

3.在其中会new了一个thinklogdriverFile，并且传入的参数是我们的’path’=&gt;/var/www/html/null/public/logs，那么会触发类中的__construct，将其默认的path给覆盖掉。

[![](https://p1.ssl.qhimg.com/t01c9783cc16a4e84aa.jpg)](https://p1.ssl.qhimg.com/t01c9783cc16a4e84aa.jpg)

[![](https://p3.ssl.qhimg.com/t01b3ef0446f24e1fc4.jpg)](https://p3.ssl.qhimg.com/t01b3ef0446f24e1fc4.jpg)

4.最后因为我们触发漏洞点的特殊性，肯定会报错使得报错信息可以被计入到log文件里。

[![](https://p4.ssl.qhimg.com/t01c51810ea85df0b6f.png)](https://p4.ssl.qhimg.com/t01c51810ea85df0b6f.png)

[![](https://p5.ssl.qhimg.com/t013557616ba79e2902.png)](https://p5.ssl.qhimg.com/t013557616ba79e2902.png)

5.之后再通过thinkLang::load包含。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013c7259791b75e191.png)

[![](https://p2.ssl.qhimg.com/t01d9977a6d0f5e8812.jpg)](https://p2.ssl.qhimg.com/t01d9977a6d0f5e8812.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fa1469a07057d4ab.jpg)



## 方法五  ::竟然可以调用非静态方法

下面是个简单的例子。

我们看看会怎么执行。

[![](https://p1.ssl.qhimg.com/t012a859282085607ec.jpg)](https://p1.ssl.qhimg.com/t012a859282085607ec.jpg)

会发现使用::调用了public类的方法并且能够成功执行，但是会报错。并且::仅仅适合在方法中没有写$this的情况，因为$this指代的是这个对象，找不到对象自然会报错。那么我们看一下下面的payload就会一眼明白，payload其实用了跟上面预期解抑制错误的另一种方法，然后抑制报错让TP不会遇错停止执行。

这个题解的payload如下：

[![](https://p1.ssl.qhimg.com/t019b96cf0673794473.jpg)](https://p1.ssl.qhimg.com/t019b96cf0673794473.jpg)

1.因为PHP本身的错误处理被thinkphp所替代进行处理，所以上面就是将thinkphp所替代错误进行处理的方法给覆盖掉导致没有办法正常执行。

2.调用self::path方法，可以抛弃掉我们上一个执行的返回值，并且返回我们所输入的path。为什么会返回path，path为什么是我们输入的值，这个就是之前提到的代码执行点他是覆盖了Request类的参数，所以方法返回的是$this-&gt;path，这个我们可以控制。

[![](https://p2.ssl.qhimg.com/t0157eb2a68430e8067.jpg)](https://p2.ssl.qhimg.com/t0157eb2a68430e8067.jpg)

3.之后调用base64_decode，返回值就是我们base64解码的内容。

4.解码后的返回值就会进入thinkviewdriverPhp::Display中，然后进入eval执行代码。

[![](https://p2.ssl.qhimg.com/t0138596b016310b184.jpg)](https://p2.ssl.qhimg.com/t0138596b016310b184.jpg)

[![](https://p5.ssl.qhimg.com/t01b1c08ee1a2515c0e.jpg)](https://p5.ssl.qhimg.com/t01b1c08ee1a2515c0e.jpg)
