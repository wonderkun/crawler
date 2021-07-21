> 原文链接: https://www.anquanke.com//post/id/198068 


# 论代码审计中的SQL注入和预编译中的SQL注入


                                阅读量   
                                **888776**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">8</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t018a2b09f2e29cb428.png)](https://p4.ssl.qhimg.com/t018a2b09f2e29cb428.png)



本文围绕代码审计中的SQL注入进行讲解，以下是几种常见的注入类型：
1. 联合查询注入
1. 布尔盲注
1. 延时注入
1. 报错注入
以上是我们列出的SQL注入的类型，我们主要探讨的主题是SQL注入与预编译中的SQL注入，疑问来了“预编译可能存在SQL注入？好像不存在SQL吧！”，我们继续来看看吧！

本文中的程序是我自己开发的一套不成熟未完成的一个简单的框架

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_558_/t01d582528518d578f3.png)

上图是框架的结构图，框架核心文件在./OW/Lib/Core目录下，还是和普通的程序一样，我们这个框架的应用程序在application目录，我们进入到Controller目录下看看

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f0701500fef6ec38.png)

这个目录下只有一个indexController.class.php文件，我们就来看一下这个文件中的代码：

[![](https://p4.ssl.qhimg.com/dm/1024_602_/t01cfe81d1cba3c3e69.png)](https://p4.ssl.qhimg.com/dm/1024_602_/t01cfe81d1cba3c3e69.png)

因为这里涉及到了框架中的东西，所以普及一下框架中的审计方法，一个框架中涉及到的东西不是类就是函数，反正就是这两个用得频繁的，这里我们简要的概述下函数回溯，很明显函数回溯这玩意说白了就是一个逆向追踪的过程，根据遇到的函数进行函数的定位，定位到某函数后，读这个函数的功能，当然某些函数可以以它的命名就能看出功能，比如上图中的函数input()就可以从字面意思理解为输入，那么我们就可以理解为这个函数可以接收外部所传入的参数无论是get、post还是cookie都可以接收，这个M()函数可以从框架的角度来看，因为框架都是遵从M(model|模型)V(view|视图)C(controller|控制器)，所以这个M函数是获取某个模型的函数，再比如$this-&gt;templet这个，从我们的角度来看就是一个成员属性，说白了其实就是类中的变量，但是这个变量还可以调用函数可见它并非只是一个变量或者字符，更可以说明这个成员属性的类型是一个object，当我们无法确定这到底是变量或者数组的时候可以用var_dump()系统函数或者用框架中的dump()函数打印出来，我们来看看

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_620_/t01f3d31047e208b569.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_554_/t01cd22c88f3fbd1b62.png)

可以看到有一个object关键字，说明这是一个对象，当然或许有人会问“框架中的dump和系统中的var_dump函数不一样吗？”当然是一样的，我们重定义一些函数或许是为了美化输出或许是为了安全考虑，所以需要重新定义，好了，我们言归正传还是回到刚才的代码中

[![](https://p5.ssl.qhimg.com/dm/1024_602_/t01383af76ab3fd2e80.png)](https://p5.ssl.qhimg.com/dm/1024_602_/t01383af76ab3fd2e80.png)我们一行一行的看着走，这里所说的一行一行的看着走并非是从文件的第一行读到最后，因为是框架，所以我们要读取的代码是以函数为单位进行的，从Index()函数看着走，12-18行

首先可以看到调用了input()函数并将该函数的返回值赋值给了变量id，前面已经说了我们可以从函数的字面意思来进行理解该函数的作用，这个函数就是用来接收用户输入的参数，我们跟进一下，因为框架中载入了Global.fun.php文件，这是一个全局函数文件，这里看到的input函数就在其中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_742_/t016dba0ba105c4c4fb.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_578_/t0161bb13bd2c14c75a.png)

[![](https://p5.ssl.qhimg.com/dm/1024_568_/t01e219fe79d3739c15.png)](https://p5.ssl.qhimg.com/dm/1024_568_/t01e219fe79d3739c15.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_307_/t013f61d75c5e80ef52.png)

我们分析一下这个函数，进入函数后，首先将$result、$method、$key、$rex这四个变量赋值为false，接着将$input以.分割为数组，将分割出来的数组传入count函数中再判断这个数组中的元素是否有两个，如果有两个的情况下那么使用list函数将以点分割的$input数组分别赋值给$method、$key，如果不满足判断条件则直接将$input赋值给$key，接着再将$key以空格分割为数组并且分别赋值给$key、$rex，这里$rex的作用是过滤指定的某些字符，接下来判断$rex是否存在，不存在那么将$rex默认赋值为/w，再次判断$method是否存在，不存在默认赋值为get，接下来在30-50行中定义了一个匿名函数，匿名函数其实挺方便的，很实用，我们接着来分析这个匿名函数吧！这个匿名函数中有两个形参，分别为$value,$rex

进入函数后首先赋值$result为false，随后进入switch判断语句中，当$rex为/d的时候将$value中除数字之外的字符全部替换为空，当$rex为/s的时候将$value中除0-9A-Za-z_之外的字符替换为空，当$rex为/c的时候，直接将$value赋值给$result，如果$rex无值的情况下那么直接将$value除0-9A-Za-z之外的字符替换为空，最后匿名函数返回$result，继续往下分析

下边又定义了一个匿名函数，这个函数的作用是判断$_GET,$_COOKIE,$_POST中传入的键是否存在，存在那么就不用赋值为默认值了，不存在就赋值为默认值，还是分析一波吧！

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_320_/t01329f992a64828174.png)

函数定义的时候并定义了4个形参继承了上边的$filter匿名函数

进入这个函数首先判断$key这个数组中是否存在$method这个键，若不存在那么将$value,$rex传入到$filter匿名函数中，并将这个匿名函数的返回值赋值给$method[$key]中，若存在的情况下那么直接将$method[$key],$rex传入到$filter匿名函数中并将返回值赋值给$method[$key]我们接着往下分析

[![](https://p5.ssl.qhimg.com/dm/1024_373_/t01f157fc22acf715b5.png)](https://p5.ssl.qhimg.com/dm/1024_373_/t01f157fc22acf715b5.png)

进入一个switch判断，当$method为get的时候将$_GET,$key,$value,$rex赋值到$by_value中，$method为post的时候将$_POST,$key,$value,$rex赋值到$by_value中，$method为cookie的时候将$_COOKIE$key,$value,$rex赋值到$by_value中，最后将$result返回，将这个函数分析完用了那么长的时间，其实用我们的理解就是将用户可以操作的外部参数进行过滤，好了，我们回到起点

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_603_/t014518234550a44f74.png)经过上边的分析，这里我们可以看到/c是没有过滤的，所以这可能是注入的前奏，我们接着看看13行，这里可以看到这个函数名为M可以理解为Model，这个函数应该是实例化某个模型后返回一个对象，实际看看这个函数吧！

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_436_/t010a0bd41b40be51a1.png)

首先进入函数后定义了一个变量modeldir也就是模型目录，然后将变量modelfile赋值为拼接之后的model文件名，然后判断$modelfile这个文件是否存在，若存在就包含$modelfile这个文件，之后的这个定义或许你们会感到奇怪，其实这是因为框架中使用到了命名空间，所以需要以命名空间的形式来实例化这个对象，若不存在这个文件那么就抛出异常并且传入`{`$model`}` file does not exist 字样，好了，这里我们可以将模型文件定义到./application/index/model/IndexModel.class.php

[![](https://p1.ssl.qhimg.com/dm/1024_567_/t01476e0f99f975de65.png)](https://p1.ssl.qhimg.com/dm/1024_567_/t01476e0f99f975de65.png)

从控制器index中我们了解到它实例化了这个indexmodel类并且调用了index()函数，进入这个函数后首先判断$id中是否包含了,，若存在那么将$id以,分割为数组，若不存在那么直接将$id变化为数组，我们接着进入下一行可以看到这里有一个$this-&gt;link的成员属性，但是他可以调用函数，说明这是一个对象，但是在当前页面中并没有看到定义了成员属性link，我们可以看到第三行定义类的时候有一个关键字为extends的，这个类继承了命名空间\OW\Lib\Core中的Model类，我们跟踪到./OW/Lib/Core/Model.class.php

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_613_/t01df4ab86ee85e9810.png)

进入这个类中我们可以看到有一个构造函数，函数中调用了link方法，link方法中判断了数据库操作类是mysql还是mysqli，从而引入相对应数据库操作类，DATABASE这个常量是在./OW/Lib/Conf/site.conf.php文件中[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_622_/t017bf0937cada49339.png)

这里可以看到database这个键的值为mysql，好了我们返回到indexModel.class.php中

[![](https://p1.ssl.qhimg.com/dm/1024_558_/t01b864cbf92d274c87.png)](https://p1.ssl.qhimg.com/dm/1024_558_/t01b864cbf92d274c87.png)

这里调用了name函数，我们进入./OW/Lib/Core/Mysql_DB.class.php中的name方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_149_/t01f76fce5096f01b01.png)

可以看到这个方法是用来定义表名的，随后类本身。然后调用了where方法，我们接着进入where方法看看

[![](https://p1.ssl.qhimg.com/dm/1024_607_/t01d89cce49521be130.png)](https://p1.ssl.qhimg.com/dm/1024_607_/t01d89cce49521be130.png)

[![](https://p2.ssl.qhimg.com/dm/1024_598_/t01a69efe45da562e6b.png)](https://p2.ssl.qhimg.com/dm/1024_598_/t01a69efe45da562e6b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_137_/t01ccccc46296f9800d.png)

进入该方法后首先用func_get_args()函数获取传递到当前函数的参数并且赋值给变量$args，接着判断是否设置了$args[1]，若设置了那么进入这个判断体中，进入后首先删除掉$args[0]

随后定义一个名为$arg的空数组，在下边用foreach将数组$args中的键和值取出来，循环体中将\$args[`{`$key`}`]赋值到$arg数组的一个元素中，接着我们跳出循环，以,将数组$arg中的每一个元素连接成一个字符串，随后使用一个assert函数将格式化的字符串赋值给$where变量，再然后将我们传入的参数拼接到SQL语句中，并将SQL语句赋值给成员属性sql，若$where是数组的时候则进入该判断体中，进入判断体后定义$column、$in、$value并赋值为空，接着使用foreach循环将数组where中的键和值取出来，进入循环体中，判断键是否为字符串型数据，若是，那么将$col赋值给$column，接着判断$val是否等于IN或者NOT IN，若等于这两个之一那么将$val赋值给$in，若不满足判断条件，那么我将$in赋值为IN，接着往下是判断了$val是否为数组，如果是数组那么就以,将$val中的元素连接成字符串，接着就跳出循环，将获取到的语句拼接到定义好的SQL语句中并赋值给成员属性sql，最后若不满足上述的条件那么就直接将$where拼接到定义好的SQL语句中并赋值给成员属性sql，最后返回当前类，看到这里，咱们的这个方法中几乎没有过滤，就只有那个格式化字符串有点过滤的意思，所以我们返回indexmodel中的index方法

[![](https://p1.ssl.qhimg.com/dm/1024_567_/t01523161bd3e1bdabb.png)](https://p1.ssl.qhimg.com/dm/1024_567_/t01523161bd3e1bdabb.png)

最后这里调用了select方法，我们一起来看看select方法：

[![](https://p0.ssl.qhimg.com/dm/1024_241_/t0115ee38df67a4fcb8.png)](https://p0.ssl.qhimg.com/dm/1024_241_/t0115ee38df67a4fcb8.png)

进入这个select方法后，首先判断是否设置了成员属性sql，若没有设置，那么我们直接将系统定义的sql语句赋值给成员属性sql，再返回类中的方法fetch，我们看看这个方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_237_/t0117862d9c68c332b6.png)

进入这个函数后首先调用类中的方法Excepton，从这个的字面意思来看这是一个异常处理的函数，我们进入这个函数

[![](https://p5.ssl.qhimg.com/dm/1024_238_/t0153074214a69b5cd8.png)](https://p5.ssl.qhimg.com/dm/1024_238_/t0153074214a69b5cd8.png)

进入函数后首先调用mysqli中的query函数查询sql语句，将返回值赋值给$result，接下来判断$result为空的时候抛出异常，并将执行的SQL语句以及mysql执行的错误信息和错误行数传入到这个异常处理类中，最后返回$result，我们回到fetch方法中

[![](https://p3.ssl.qhimg.com/dm/1024_237_/t01ed1b6edf526d0e89.png)](https://p3.ssl.qhimg.com/dm/1024_237_/t01ed1b6edf526d0e89.png)

接着讲成员属性sql赋值给成员属性SQL，然后删除成员属性中的sql，order，limit变量，然后使用mysqli中的fetch_all方法将查询到的所有结果返回。代码分析到这里，我们可以很明显的看到indexmoel中的index方法存在SQL注入，因为从外到内过滤的东西只有那么一点点，最主要的是这个index控制器中的index方法获取值的时候使用的过滤方式不正确

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_287_/t0114d98744bc1edad0.png)

这里我们来看看这个注入。。。。

访问：[http://localhost/?s=index/index/index/id/3’](http://localhost/?s=index/index/index/id/3%E2%80%99)

[![](https://p0.ssl.qhimg.com/dm/1024_557_/t018cedbe6998c1e2fc.png)](https://p0.ssl.qhimg.com/dm/1024_557_/t018cedbe6998c1e2fc.png)

可以从它返回的信息看出来这是一个数字型的SQL注入，注入原因呢！是因为未按照正确的获取方式来接收外部数据导致的，我们将/c改为/d

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_260_/t01829af1ec886f3203.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_552_/t0131e422e64c1a9222.png)

这样就确确实实的将这个SQL注入给过滤掉了，接着我们往下看看字符型的sql注入，当然如果是字符型的注入的情况下并且程序自身有将危险字符转义的时候，那么必须满足先遣条件数据库编码为GBK，这样就存在一个款字节注入，我们将数据库编码改改

[![](https://p4.ssl.qhimg.com/dm/1024_493_/t01be621f2fb676d441.png)](https://p4.ssl.qhimg.com/dm/1024_493_/t01be621f2fb676d441.png)

我们来看看我们的字符型的注入

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_155_/t0188556d5dfe44bd64.png)

[![](https://p1.ssl.qhimg.com/dm/1024_129_/t016bf104dbf57e04de.png)](https://p1.ssl.qhimg.com/dm/1024_129_/t016bf104dbf57e04de.png)

这里呢！还是可以很明显的看到这里存在字符型并且是宽字节的注入，访问下

[http://localhost/?s=index/index/String/title/a%df%27](http://localhost/?s=index/index/String/title/a%25df%2527)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_555_/t01c1c64adf276ee831.png)

只不过现在在代码审计中很难在框架中看到宽字节注入，这里要修复的话直接用/s就好了

[![](https://p3.ssl.qhimg.com/dm/1024_157_/t01649ea0563ff00ba3.png)](https://p3.ssl.qhimg.com/dm/1024_157_/t01649ea0563ff00ba3.png)

[![](https://p5.ssl.qhimg.com/dm/1024_558_/t015d339b71405478c7.png)](https://p5.ssl.qhimg.com/dm/1024_558_/t015d339b71405478c7.png)

可以看到这个宽字节已经被我们给修复了，我们接着往下走，我们来看看验证登陆函数中的注入

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_315_/t01e6b94af4fcb66f22.png)

我们来简单的分析一下这个函数的作用，首先进入函数中将外部获取到的logintoken并将base64字符串解码并且以制表符分割为数组并且用$uid、$password分别接收这个这个数组中的两个元素，然后将$uid传入到get_user这个模型函数中，可见这里对加密字符串很友好，几乎没有过滤，我们来看看get_user方法是否对$uid进行了过滤

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_154_/t017fd4c77c7890bd38.png)

可见都很有善，没有过滤我们构造下payload：

Cookie:logintoken=MScJNjU0ZHM2NWE=

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_576_/t013f93a6163008b063.png)

其实这里验证登陆并非一定是一个SQL注入，当程序没有返回值没有错误信息返回的时候，不管是人乃至工具都不可能测试出SQL注入，所以我们大概的估计一个用户id，随后会将返回的users中的password和我们传入的password进行对比，所以这里还可以进行用户密码的爆破，并且还是无限制爆破，从这个案例我们得知不能对即将解密的加密字符串太过友善，否则反受其害。。。。

我们接着来

[![](https://p5.ssl.qhimg.com/dm/1024_156_/t0186e20424a34cc08c.png)](https://p5.ssl.qhimg.com/dm/1024_156_/t0186e20424a34cc08c.png)

这里由于获取的参数id会传入url解码函数中，所以这也造成了一个注入，只需要对某一个字符或者字符串进行双重url编码即可

访问：[http://localhost/?s=index/index/articles/id/3%2527](http://localhost/?s=index/index/articles/id/3%252527)

[![](https://p3.ssl.qhimg.com/dm/1024_554_/t01f2da603b714696ea.png)](https://p3.ssl.qhimg.com/dm/1024_554_/t01f2da603b714696ea.png)

这里的%25%27是双重编码来着，所以说浏览器请求的时候会将%27编码后的结果解码为%27，然后传入程序中程序再将这%27解析为单引号，所以造成了一些意料之外的漏洞。

我们再来看看预编译中的漏洞，为各位解答一下疑问，预编译这东西存在的SQL注入是由于开发者对于sql语句嵌入了用户所输入的值，预编译这东西只能将用户输入的传到数据中，比如id=?那么这个问号就是应该嵌入用户所输入的值，再来看看select * from $table where id=?那么这条语句呢就出现了一个致命的弱点，也就造成了SQL注入，那么这个$table就不会只将它当作数据来处理而是当作语句来处理，这是这个致命的关键，我们一起来看看

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_239_/t01150f26f7a6ad7f2a.png)

这里从外部分别获取了key和id，分别将这两个元素传入$where数组中，并传入模型data函数中，我们看看data函数

[![](https://p5.ssl.qhimg.com/dm/1024_140_/t01b7b3ae2e38d5d4c3.png)](https://p5.ssl.qhimg.com/dm/1024_140_/t01b7b3ae2e38d5d4c3.png)

这里将传入的值预编译了，我们在这里看看最后执行的SQL语句，使用get_last_sql()函数进行查看

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_288_/t016123a75da4273f2b.png)

我们看看页面中的SQL语句

[![](https://p1.ssl.qhimg.com/dm/1024_558_/t0148b32fcc1101056e.png)](https://p1.ssl.qhimg.com/dm/1024_558_/t0148b32fcc1101056e.png)

操作一下这个id看看有没有反应，访问：[http://localhost/?s=index/index/data&amp;id=3%27](http://localhost/?s=index/index/data&amp;id=3%2527)

[![](https://p2.ssl.qhimg.com/dm/1024_559_/t0175f42c9838cf4559.png)](https://p2.ssl.qhimg.com/dm/1024_559_/t0175f42c9838cf4559.png)

当然在我们获取值的时候就已经将这玩意定义好了，我们改改吧！改成/c

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_295_/t01a625a5010368ff6f.png)

我们再来访问看看

[![](https://p1.ssl.qhimg.com/dm/1024_554_/t011b5555aa8a58285e.png)](https://p1.ssl.qhimg.com/dm/1024_554_/t011b5555aa8a58285e.png)

还是无法操作这个id，那么我们来看看这个key，访问：[http://localhost/?s=index/index/data&amp;id=3%27&amp;key=a](http://localhost/?s=index/index/data&amp;id=3%2527&amp;key=a)

[![](https://p5.ssl.qhimg.com/dm/1024_552_/t017f55acd0c3be9f74.png)](https://p5.ssl.qhimg.com/dm/1024_552_/t017f55acd0c3be9f74.png)

可以看到用户所输入的值不应该用来嵌入到语句中，而是由开发者来定义这些字段等等的，好了，我们再来看看每一个注入点所适用的注入类型，比如这些注入都有返回值和错误信息

所以我们可以用两种最简单的形式来注入一下分别是报错注入和联合查询注入

报错注入：

这里我们使用updatexml函数进行报错注入

访问：[http://localhost/?s=index/index/data&amp;id=3&amp;key=id=3%20and%20(updatexml(1,concat(0x7e,(select%20user()),0x7e),1))%23](http://localhost/?s=index/index/data&amp;id=3&amp;key=id=3%2520and%2520(updatexml(1,concat(0x7e,(select%2520user()),0x7e),1))%2523)

[![](https://p0.ssl.qhimg.com/dm/1024_552_/t0154b7fa78319e2557.png)](https://p0.ssl.qhimg.com/dm/1024_552_/t0154b7fa78319e2557.png)

[http://localhost/?s=index/index/data&amp;id=3&amp;key=id=3%20and%20(updatexml(1,concat(0x7e,(select%20table_name%20from%20information_schema.tables%20where%20table_schema=database()%20limit%200,1),0x7e),1))%23](http://localhost/?s=index/index/data&amp;id=3&amp;key=id=3%2520and%2520(updatexml(1,concat(0x7e,(select%2520table_name%2520from%2520information_schema.tables%2520where%2520table_schema=database()%2520limit%25200,1),0x7e),1))%2523)

[![](https://p1.ssl.qhimg.com/dm/1024_553_/t01a8e47560c393379b.png)](https://p1.ssl.qhimg.com/dm/1024_553_/t01a8e47560c393379b.png)

这样依次改变limit中的值就好了

再来看看联合查询注入：

[http://localhost/?s=index/index/data&amp;id=3&amp;key=id=-3%20union%20select%201,group_concat(table_name),3,4,5,6,7,8,9,10,11%20from%20information_schema.tables%20where%20table_schema=database()%23](http://localhost/?s=index/index/data&amp;id=3&amp;key=id=-3%2520union%2520select%25201,group_concat(table_name),3,4,5,6,7,8,9,10,11%2520from%2520information_schema.tables%2520where%2520table_schema=database()%2523)

[![](https://p0.ssl.qhimg.com/dm/1024_550_/t01e259bd9d36ec4eb1.png)](https://p0.ssl.qhimg.com/dm/1024_550_/t01e259bd9d36ec4eb1.png)

好了，本篇文章就到此了，SQL注入是个奇妙的东西，出现的类型也不止上述中的注入，还有二次注入

关注本团队公众号，获取最新文章

[![](https://p2.ssl.qhimg.com/t0122cb1e668b998a5d.png)](https://p2.ssl.qhimg.com/t0122cb1e668b998a5d.png)
