> 原文链接: https://www.anquanke.com//post/id/177173 


# 天融信关于ThinkPHP5.1框架结合RCE漏洞的深入分析


                                阅读量   
                                **303229**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01dc4566382aea5da2.png)](https://p3.ssl.qhimg.com/t01dc4566382aea5da2.png)



作者：天融信阿尔法实验室



## 0x00 前言

在前几个月，Thinkphp连续爆发了多个严重漏洞。由于框架应用的广泛性，漏洞影响非常大。为了之后更好地防御和应对此框架漏洞，阿尔法实验室对Thinkphp框架进行了详细地分析，并在此分享给大家共同学习。

本篇文章将从框架的流程讲起，让大家对Thinkphp有个大概的认识，接着讲述一些关于漏洞的相关知识，帮助大家在分析漏洞时能更好地理解漏洞原理，最后结合一个比较好的RCE漏洞(超链接)用一种反推的方式去进行分析，让大家将漏洞和框架知识相融合。体现一个从学习框架到熟悉漏洞原理的过程。



## 0x01 框架介绍

ThinkPHP是一个免费开源的，快速、简单的面向对象的轻量级PHP开发框架，是为了敏捷WEB应用开发和简化企业应用开发而诞生的。ThinkPHP从诞生以来一直秉承简洁实用的设计原则，在保持出色的性能和至简的代码的同时，也注重易用性。



## 0x02 环境搭建

### 2.1 Thinkphp环境搭建

安装环境：Mac Os MAMP集成软件

PHP版本：5.6.10

Thinkphp版本：5.1.20

thinkphp安装包获取（Composer方式）：

首先需要安装composer。

curl -sS https://getcomposer.org/installer | php

下载后，检查Composer是否能正常工作，只需要通过 php 来执行 PHAR：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01764718ad2343686f.jpg)

若返回信息如上图，则证明成功。

然后将composer.phar 移动到bin目录下并改名为composer

mv composer.phar /usr/local/bin/composer

Composer安装好之后，打开命令行，切换到你的web根目录下面并执行下面的命令：

composer create-project topthink/think=5.1.20 tp5.1.20 –prefer-dist

若需要其他版本，可通过修改版本号下载。

验证是否可以正常运行，在浏览器中输入地址：

http://localhost/tp5.1.20/public/

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014038fe6abaefd867.png)

如果出现上图所示，那么恭喜你安装成功。

### 2.2 IDE环境搭建及xdebug配置

PHP IDE工具有很多，我推荐PhpStorm，因为它支持所有PHP语言功能， 提供最优秀的代码补全、重构、实时错误预防、快速导航功能。

PhpStorm下载地址：https://www.jetbrains.com/phpstorm/

Xdebug

Xdebug是一个开放源代码的PHP程序调试器，可以用来跟踪，调试和分析PHP程序的运行状况。在调试分析代码时，xdebug十分好用。

下面我们说一下xdebug怎么配置（MAMP+PHPstrom）

1.下载安装xdebug扩展(MAMP自带 ）。

2.打开php.ini文件，添加xdebug相关配置

[xdebug]

xdebug.remote_enable = 1

xdebug.remote_handler = dbgp

xdebug.remote_host = 127.0.0.1

xdebug.remote_port = 9000 #端口号可以修改，避免冲突

xdebug.idekey = PHPSTROM

然后重启服务器。

### 2.3.客户端phpstorm配置

2.3.1点击左上角phpstorm，选择preferences

[![](https://p5.ssl.qhimg.com/t017c83cb048c5e41ea.jpg)](https://p5.ssl.qhimg.com/t017c83cb048c5e41ea.jpg)

2.3.2 Languages &amp; Frameworks -&gt; PHP，选择PHP版本号，选择PHP执行文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0169d988e1c41ace44.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ffc098b250d6476b.jpg)

在选择PHP执行文件的时候，会显示 “Debugger:Xdebug”，如果没有的话，点击open打开配置文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0133b83216223cd797.png)

将注释去掉即可。

2.3.3配置php下的Debug

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014835beaa1e343daf.jpg)

Port和配置文件中的xdebug.remote_port要一致。

2.3.4配置Debug下的DBGp proxy

[![](https://p2.ssl.qhimg.com/t019a6c4f989bea31be.jpg)](https://p2.ssl.qhimg.com/t019a6c4f989bea31be.jpg)

填写的内容和上面php.ini内的相对应。

2.3.5配置servers

[![](https://p0.ssl.qhimg.com/t01d6a6cd1b3d46ee9a.jpg)](https://p0.ssl.qhimg.com/t01d6a6cd1b3d46ee9a.jpg)

点击+号添加

2.3.6配置debug模式

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fc843a2190bae512.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01701bc7bd3a6b128d.jpg)

在Server下拉框中，选择我们在第4步设置的Server服务名称，Browser选择你要使用的浏览器。所有配置到此结束。

### 2.4.xdebug使用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e25d0869692c14f7.png)

开启xdeubg监听

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f141117c61d78b34.jpg)

下一个断点，然后访问URL，成功在断点处停下。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013106d75a9f291afe.jpg)



## 0x03 框架流程浅析

[![](https://p3.ssl.qhimg.com/t010bcbfa80e583a095.png)](https://p3.ssl.qhimg.com/t010bcbfa80e583a095.png)

我们先看入口文件index.php，入口文件非常简洁，只有三行代码。

可以看到这里首先定义了一下命名空间，然后加载一些基础文件后，就开始执行应用。

第二行引入base.php基础文件，加载了Loader类，然后注册了一些机制–如自动加载功能、错误异常的机制、日志接口、注册类库别名。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e9ae51b5b2461036.jpg)

这些机制中比较重要的一个是自动加载功能，系统会调用 Loader::register()方法注册自动加载，在这一步完成后，所有符合规范的类库（包括Composer依赖加载的第三方类库）都将自动加载。下面我详细介绍下这个自动加载功能。

首先需要注册自动加载功能，注册主要由以下几部分组成:

1. 注册系统的自动加载方法 \think\Loader::autoload

2. 注册系统命名空间定义

3. 加载类库映射文件（如果存在）

4. 如果存在Composer安装，则注册Composer自动加载

5. 注册extend扩展目录

其中2.3.4.5是为自动加载时查找文件路径的时候做准备，提前将一些规则(类库映射、PSR-4、PSR-0)配置好。

然后再说下自动加载流程，看看程序是如何进行自动加载的？

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014e0762cc1ebd4c9e.jpg)

spl_autoload_register()是个自动加载函数，当我们实例化一个未定义的类时就会触发此函数，然后再触发指定的方法，函数第一个参数就代表要触发的方法。

可以看到这里指定了think\Loader::autoload()这个方法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011ef3d19a786b13d2.jpg)

首先会判断要实例化的$class类是否在之前注册的类库别名$classAlias中，如果在就返回,不在就进入findFile()方法查找文件，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0125cac1bdc471d02b.jpg)

这里将用多种方式进行查找，以类库映射、PSR-4自动加载检测、PSR-0自动加载检测的顺序去查找(这些规则方式都是之前注册自动加载时配置好的)，最后会返回类文件的路径，然后include包含，进而成功加载并定义该类。

这就是自动加载方法，按需自动加载类，不需要一一手动加载。在面向对象中这种方法经常使用，可以避免书写过多的引用文件，同时也使整个系统更加灵活。

在加载完这些基础功能之后，程序就会开始执行应用，它首先会通过调用Container类里的静态方法get()去实例化app类，接着去调用app类中的run()方法。

[![](https://p3.ssl.qhimg.com/t010812f1d429e96e95.jpg)](https://p3.ssl.qhimg.com/t010812f1d429e96e95.jpg)

在run()方法中，包含了应用执行的整个流程。

1.$this-&gt;initialize()，首先会初始化一些应用。例如：加载配置文件、设置路径环境变量和注册应用命名空间等等。

2. this-&gt;hook-&gt;listen(‘app_init’); 监听app_init应用初始化标签位。Thinkphp中有很多标签位置，也可以把这些标签位置称为钩子，在每个钩子处我们可以配置行为定义，通俗点讲，就是你可以往钩子里添加自己的业务逻辑，当程序执行到某些钩子位置时将自动触发你的业务逻辑。

3. 模块\入口绑定

[![](https://p0.ssl.qhimg.com/t015dba56d005d85822.jpg)](https://p0.ssl.qhimg.com/t015dba56d005d85822.jpg)

进行一些绑定操作，这个需要配置才会执行。默认情况下，这两个判断条件均为false。

4. $this-&gt;hook-&gt;listen(‘app_dispatch’);监听app_dispatch应用调度标签位。和2中的标签位同理，所有标签位作用都是一样的，都是定义一些行为，只不过位置不同，定义的一些行为的作用也有所区别。

5. $dispatch = $this-&gt;routeCheck()-&gt;init(); 开始路由检测，检测的同时会对路由进行解析，利用array_shift函数一一获取当前请求的相关信息（模块、控制器、操作等）。

6. $this-&gt;request-&gt;dispatch($dispatch);记录当前的调度信息,保存到request对象中。

7.记录路由和请求信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016c02d75e758c2c2a.jpg)

如果配置开启了debug模式，会把当前的路由和请求信息记录到日志中。

8. $this-&gt;hook-&gt;listen(‘app_begin’); 监听app_begin(应用开始标签位)。

9.根据获取的调度信息执行路由调度

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011f21e750f231ed48.jpg)

期间会调用Dispatch类中的exec()方法对获取到的调度信息进行路由调度并最终获取到输出数据$response。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b0221b9b81f4bfbd.jpg)

然后将$response返回，最后调用Response类中send()方法，发送数据到客户端，将数据输出到浏览器页面上。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d4e0ca460dbc5432.png)

[![](https://p4.ssl.qhimg.com/t018bcac4ff215fc94d.jpg)](https://p4.ssl.qhimg.com/t018bcac4ff215fc94d.jpg)

在应用的数据响应输出之后，系统会进行日志保存写入操作，并最终结束程序运行。

[![](https://p4.ssl.qhimg.com/t0112411528a282d84c.jpg)](https://p4.ssl.qhimg.com/t0112411528a282d84c.jpg)



## 0x04 漏洞预备知识

这部分主要讲解与漏洞相关的知识点，有助于大家更好地理解漏洞形成原因。

### 4.1命名空间特性

ThinkPHP5.1遵循PSR-4自动加载规范，只需要给类库正确定义所在的命名空间，并且命名空间的路径与类库文件的目录一致，那么就可以实现类的自动加载。

例如，\think\cache\driver\File类的定义为：



```
namespace think\cache\driver;

class File

`{`

`}`
```

如果我们实例化该类的话，应该是：

```
$class = new \think\cache\driver\File();
```

系统会自动加载该类对应路径的类文件，其所在的路径是 thinkphp/library/think/cache/driver/File.php。

可是为什么路径是在thinkphp/library/think下呢？这就要涉及要另一个概念—根命名空间。

4.1.1 根命名空间

根命名空间是一个关键的概念，以上面的\think\cache\driver\File类为例，think就是一个根命名空间，其对应的初始命名空间目录就是系统的类库目录（thinkphp/library/think），我们可以简单的理解一个根命名空间对应了一个类库包。

系统内置的几个根命名空间（类库包）如下：

名称

描述

类库目录

think

系统核心类库

thinkphp/library/think

traits

系统Trait类库

thinkphp/library/traits

app

应用类库

Application

### 4.2 URL访问

在没有定义路由的情况下典型的URL访问规则（PATHINFO模式）是：

http://serverName/index.php（或者其它应用入口文件）/模块/控制器/操作/[参数名/参数值…]

如果不支持PATHINFO的服务器可以使用兼容模式访问如下

http://serverName/index.php（或者其它应用入口文件）?s=/模块/控制器/操作/[参数名/参数值…]

什么是pathinfo模式?

我们都知道一般正常的访问应该是

http://serverName/index.php?m=module&amp;c=controller&amp;a=action&amp;var1=vaule1&amp;var2=vaule2

而pathinfo模式是这样的

http://serverName/index.php/module/controller/action/var1/vaule1/var2/value2

在php中有一个全局变量$_SERVER[‘PATH_INFO’]，我们可以通过它来获取index.php后面的内容。

什么是$_SERVER[‘PATH_INFO’]?

官方是这样定义它的：包含由客户端提供的、跟在真实脚本名称之后并且在查询语句（query string）之前的路径信息。

什么意思呢？简单来讲就是获得访问的文件和查询?之间的内容。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016e1f54ef754b98f5.jpg)

强调一点，在通过$_SERVER[‘PATH_INFO’]获取值时，系统会把’\’自动转换为’/’（这个特性我在Mac Os(MAMP)、Windows(phpstudy)、Linux(php+apache)环境及php5.x、7.x中进行了测试，都会自动转换，所以系统及版本之间应该不会有所差异）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011d7d9cbbcdc397e2.jpg)

下面再分别介绍下入口文件、模块、控制器、操作、参数名/参数值。

1.入口文件

文件地址：public\index.php

作用：负责处理请求

2.模块（以前台为例）

模块地址：application\index

作用：网站前台的相关部分

3.控制器

控制器目录：application\index\controller

作用：书写业务逻辑

4. 操作（方法）

在控制器中定义的方法

5. 参数名/参数值

方法中的参数及参数值

例如我们要访问index模块下的Test.php控制器文件中的hello()方法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b7de97fe4cd71a34.jpg)

那么可以输入&lt;http://serverName/index.php/index(模块)/Test(控制器)/hello(方法)/name(参数名)/world(参数值)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0150661c00a4650c3c.jpg)

这样就访问到指定文件了。

另外再讲一下Thinkphp的几种传参方式及差别。

PATHINFO: index.php/index/Test/hello/name/world 只能以这种方式传参。

兼容模式:index.php?s=index/Test/hello/name/world

index.php?s=index/Test/hello&amp;name=world

当我们有两个变量$a、$b时，在兼容模式下还可以将两者结合传参：

index.php?s=index/Test/hello/a/1&amp;b=2

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013de03a3fa4237f17.jpg)

这时，我们知道了URL访问规则，当然也要了解下程序是怎样对URL解析处理，最后将结果输出到页面上的。

### 4.3 URL路由解析动态调试分析

URL路由解析及页面输出工作可以分为5部分。

1. 路由定义：完成路由规则的定义和参数设置

2. 路由检测：检查当前的URL请求是否有匹配的路由

3. 路由解析：解析当前路由实际对应的操作。

4. 路由调度：执行路由解析的结果调度。

5. 响应输出及应用结束：将路由调度的结果数据输出至页面并结束程序运行。

我们通过动态调试来分析，这样能清楚明了的看到程序处理的整个流程，由于在Thinkphp中，配置不同其运行流程也会不同，所以我们采用默认配置来进行分析，并且由于在程序运行过程中会出现很多与之无关的流程，我也会将其略过。

4.3.1 路由定义

通过配置route目录下的文件对路由进行定义，这里我们采取默认的路由定义，就是不做任何路由映射。

4.3.2 路由检测

这部分内容主要是对当前的URL请求进行路由匹配。在路由匹配前先会获取URL中的pathinfo，然后再进行匹配，但如果没有定义路由，则会把当前pathinfo当作默认路由。

首先我们设置好IDE环境，并在路由检测功能处下断点。

[![](https://p0.ssl.qhimg.com/t01a9d2d6c299af4331.jpg)](https://p0.ssl.qhimg.com/t01a9d2d6c299af4331.jpg)

然后我们请求上面提到的Test.php文件。

http://127.0.0.1/tp5.1.20/public/index.php/index/test/hello/name/world

我这里是以pathinfo模式请求的，但是其实以不同的方式在请求时，程序处理过程是有稍稍不同的，主要是在获取参数时不同。在后面的分析中，我会进行说明。

[![](https://p5.ssl.qhimg.com/t01a85ce6d77a40851c.jpg)](https://p5.ssl.qhimg.com/t01a85ce6d77a40851c.jpg)

F7跟进routeCheck()方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012a8409c08fe6ab31.jpg)

route_check_cache路由缓存默认是不开启的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018c23e57a6085f1df.png)

然后我们进入path()方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01916a1dbfa045d8a8.jpg)

继续跟进pathinfo()方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c9d0e55eedea5441.jpg)

这里会根据不同的请求方式获取当前URL的pathinfo信息，因为我们的请求方式是pathinfo,所以会调用$this-&gt;server(‘PATH_INFO’)去获取，获取之后会使用ltrim()函数对$pathinfo进行处理去掉左侧的’/’符号。Ps:如果以兼容模式请求，则会用$_GET方法获取。

[![](https://p0.ssl.qhimg.com/t014df1ac08a0346f11.jpg)](https://p0.ssl.qhimg.com/t014df1ac08a0346f11.jpg)

然后返回赋值给$path并将该值带入check()方法对URL路由进行检测

[![](https://p3.ssl.qhimg.com/t019f64b51655efbaef.jpg)](https://p3.ssl.qhimg.com/t019f64b51655efbaef.jpg)

这里主要是对我们定义的路由规则进行匹配，但是我们是以默认配置来运行程序的，没有定义路由规则，所以跳过中间对于路由检测匹配的过程，直接来看默认路由解析过程，使用默认路由对其进行解析。

4.3.3 路由解析

接下来将会对路由地址进行了解析分割、验证、格式处理及赋值进而获取到相应的模块、控制器、操作名。

new UrlDispatch() 对UrlDispatch（实际上是think\route\dispatch\Url这个类）实例化，因为Url没有构造函数，所以会直接跳到它的父类Dispatch的构造函数，把一些信息传递（包括路由）给Url类对象，这么做的目的是为了后面在调用Url类中方法时方便调用其值。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ae4159cbba217a0b.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01aa5681581546a454.jpg)

赋值完成后回到routeCheck()方法，将实例化后的Url对象赋给$dispatch并return返回。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c4f658d8841f65e5.jpg)

返回后会调用Url类中的init()方法，将$dispatch对象中的得到$this-&gt;dispatch(路由)传入parseUrl()方法中，开始解析URL路由地址。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01603fc5a3d8fda046.jpg)

跟进parseUrl()方法

[![](https://p1.ssl.qhimg.com/t013aed9acae334976f.jpg)](https://p1.ssl.qhimg.com/t013aed9acae334976f.jpg)

这里首先会进入parseUrlPath()方法，将路由进行解析分割。

[![](https://p4.ssl.qhimg.com/t01253e02ce62d99db2.jpg)](https://p4.ssl.qhimg.com/t01253e02ce62d99db2.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ec668955e29fd002.png)

使用”/”进行分割，拿到 [模块/控制器/操作/参数/参数值]。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01811939df984c93bd.jpg)

紧接着使用array_shift()函数挨个从$path数组中取值对模块、控制器、操作、参数/参数值进行赋值。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fefa1eefcfe07f05.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01345a5aa7c4a450d9.png)

接着将参数/参数值保存在了Request类中的Route变量中，并进行路由封装将赋值后的$module、$controller、$action存到route数组中，然后将$route返回赋值给$result变量。

[![](https://p2.ssl.qhimg.com/t019474620c076f03e2.jpg)](https://p2.ssl.qhimg.com/t019474620c076f03e2.jpg)

new Module($this-&gt;request, $this-&gt;rule, $result)，实例化Module类。

在Module类中也没有构造方法，会直接调用Dispatch父类的构造方法。

[![](https://p0.ssl.qhimg.com/t013f1dc0c598459d91.jpg)](https://p0.ssl.qhimg.com/t013f1dc0c598459d91.jpg)

然后将传入的值都赋值给Module类对象本身$this。此时，封装好的路由$result赋值给了$this-&gt;dispatch，这么做的目的同样是为了后面在调用Module类中方法时方便调用其值。

实例化赋值后会调用Module类中的init()方法，对封装后的路由(模块、控制器、操作)进行验证及格式处理。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f4797e917d076faf.jpg)

$result = $this-&gt;dispatch，首先将封装好的路由$this-&gt;dispatch数组赋给$result，接着会从$result数组中获取到了模块$module的值并对模块进行大小写转换和html标签处理，接下来会对模块值进行检测是否合规，若不合规，则会直接HttpException报错并结束程序运行。检测合格之后，会再从$result中获取控制器、操作名并处理，同时会将处理后值再次赋值给$this(Module类对象)去替换之前的值。

Ps：从$result中获取值时，程序采用了三元运算符进行判断，如果相关值为空会一律采用默认的值index。这就是为什么我们输入http://127.0.0.1/tp5.1.20/public/index.php在不指定模块、控制器、操作值时会跳到程序默认的index模块的index控制器的index操作中去。

此时调度信息(模块、控制器、操作)都已经保存至Module类对象中，在之后的路由调度工作中会从中直接取出来用。

然后返回Module类对象$this，回到最开始的App类，赋值给$dispatch。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01695cd8da8903ddb8.jpg)

至此，路由解析工作结束，到此我们获得了模块、控制器、操作，这些值将用于接下来的路由调度。

接下来在路由调度前，需要另外说明一些东西：路由解析完成后，如果debug配置为True，则会对路由和请求信息进行记录，这里有个很重要的点param()方法, 该方法的作用是获取变量参数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0154e97a62ee2fdbab.jpg)

在这里，在确定了请求方式(GET)后，会将请求的参数进行合并，分别从$_GET、$_POST(这里为空)和Request类的route变量中进行获取。然后存入Request类的param变量中，接着会对其进行过滤，但是由于没有指定过滤器，所以这里并不会进行过滤操作。

[![](https://p4.ssl.qhimg.com/t01126d3fbf749429fa.png)](https://p4.ssl.qhimg.com/t01126d3fbf749429fa.png)

[![](https://p2.ssl.qhimg.com/t01377bb7960e792a65.png)](https://p2.ssl.qhimg.com/t01377bb7960e792a65.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019ef3b5677c805e9b.jpg)

Ps：这里解释下为什么要分别从$_GET中和Request类的route变量中进行获取合并。上面我们说过传参有三种方法。

1. index/Test/hello/name/world

2. index/Test/hello&amp;name=world

3. index/Test/hello/a/1&amp;b=2

当我们如果选择1进行请求时，在之前的路由检测和解析时，会将参数/参数值存入Request类中的route变量中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c7c34f69912daf1b.png)

而当我们如果选择2进行请求时，程序会将&amp;前面的值剔除，留下&amp;后面的参数/参数值，保存到$_GET中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d11025930eeacf92.jpg)

并且因为Thinkphp很灵活，我们还可以将这两种方式结合利用，如第3个。

这就是上面所说的在请求方式不同时，程序在处理传参时也会不同。

Ps：在debug未开启时,参数并不会获得，只是保存在route变量或$_GET[]中，不过没关系，因为在后面路由调度时还会调用一次param()方法。

继续调试，开始路由调度工作。

4.3.4 路由调度

这一部分将会对路由解析得到的结果(模块、控制器、操作)进行调度，得到数据结果。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e6eaed204e9b0211.jpg)

这里首先创建了一个闭包函数，并作为参数传入了add方法()中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0159fb94483d72e727.jpg)

将闭包函数注册为中间件，然后存入了$this-&gt;queue[‘route’]数组中。

然后会返回到App类， $response = $this-&gt;middleware-&gt;dispatch($this-&gt;request);执行middleware类中的dispatch()方法，开始调度中间件。

[![](https://p0.ssl.qhimg.com/t011cdb7961fa41ad85.jpg)](https://p0.ssl.qhimg.com/t011cdb7961fa41ad85.jpg)

使用call_user_func()回调resolve()方法，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0103be9b14a504b7b0.jpg)

使用array_shift()函数将中间件(闭包函数)赋值给了$middleware，最后赋值给了$call变量。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0172bc30e171871673.png)

当程序运行至call_user_func_array()函数继续回调，这个$call参数是刚刚那个闭包函数，所以这时就会调用之前App类中的闭包函数。

中间件的作用官方介绍说主要是用于拦截或过滤应用的HTTP请求，并进行必要的业务处理。所以可以推测这里是为了调用闭包函数中的run()方法，进行路由调度业务。

然后在闭包函数内调用了Dispatch类中的run()方法，开始执行路由调度。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0191ede0ea690641ff.jpg)

跟进exec()方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cb5a5c0568f33526.jpg)

可以看到，这里对我们要访问的控制器Test进行了实例化，我们来看下它的实例化过程。

[![](https://p5.ssl.qhimg.com/t019b9cad0c3cb709c3.jpg)](https://p5.ssl.qhimg.com/t019b9cad0c3cb709c3.jpg)

将控制器类名$name和控制层$layer传入了parseModuleAndClass()方法，对模块和类名进行解析，获取类的命名空间路径。

[![](https://p4.ssl.qhimg.com/t01ff1258aca2b27e37.jpg)](https://p4.ssl.qhimg.com/t01ff1258aca2b27e37.jpg)

在这里如果$name类中以反斜线\开始时就会直接将其作为类的命名空间路径。此时$name是test，明显不满足，所以会进入到else中，从request封装中获取模块的值$module，然后程序将模块$module、控制器类名$name、控制层$layer再传入parseClass()方法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01186ae2e69544c130.jpg)

对$name进行了一些处理后赋值给$class，然后将$this-&gt;namespace、$module、$layer、$path、$class拼接在一起形成命名空间后返回。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018a15d64beb546193.jpg)

到这我们就得到了控制器Test的命名空间路径，根据Thinkphp命名空间的特性，获取到命名空间路径就可以对其Test类进行加载。

F7继续调试，返回到了刚刚的controller()方法，开始加载Test类。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018c5a0a99bbe010bf.jpg)

加载前，会先使用class_exists()函数检查Test类是否定义过，这时程序会调用自动加载功能去查找该类并加载。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01613447174360e71e.jpg)

加载后调用__get()方法内的make()方法去实例化Test类。

[![](https://p4.ssl.qhimg.com/t01625b5e5bcc18affd.png)](https://p4.ssl.qhimg.com/t01625b5e5bcc18affd.png)

[![](https://p1.ssl.qhimg.com/t0128dc8b0ba2645f7c.jpg)](https://p1.ssl.qhimg.com/t0128dc8b0ba2645f7c.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f5ab6dc60c0bee8f.jpg)

这里使用反射调用的方法对Test类进行了实例化。先用ReflectionClass创建了Test反射类，然后 return $reflect-&gt;newInstanceArgs($args); 返回了Test类的实例化对象。期间顺便判断了类中是否定义了__make方法、获取了构造函数中的绑定参数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d19d4f70e5483965.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e4d755a6faa04e86.jpg)

然后将实例化对象赋值赋给$object变量，接着返回又赋给$instance变量。

继续往下看

这里又创建了一个闭包函数作为中间件，过程和上面一样，最后利用call_user_func_array()回调函数去调用了闭包函数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019f89013aa88fc856.jpg)

在这个闭包函数内，主要做了4步。

1.使用了is_callable()函数对操作方法和实例对象作了验证，验证操作方法是否能用进行调用。

2.new ReflectionMethod()创建了Test的反射类$reflect。

3.紧接着由于url_param_type默认为0，所以会调用param()方法去请求变量，但是前面debug开启时已经获取到了并保存进了Request类对象中的param变量，所以此时只是从中将值取出来赋予$var变量。

4.调用invokeReflectMethod()方法，并将Test实例化对象$instance、反射类$reflect、请求参数$vars传入。

[![](https://p4.ssl.qhimg.com/t01ecd929fbd7d3ed40.jpg)](https://p4.ssl.qhimg.com/t01ecd929fbd7d3ed40.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017d21704de079936e.jpg)

这里调用了bindParams()方法对$var参数数组进行处理，获取了Test反射类的绑定参数，获取到后将$args传入invokeArgs()方法，进行反射执行。

然后程序就成功运行到了我们访问的文件(Test)。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cfa7f07d3faf255b.png)

运行之后返回数据结果，到这里路由调度的任务也就结束了，剩下的任务就是响应输出了，将得到数据结果输出到浏览器页面上。

4.3.5 响应输出及应用结束

这一小节会对之前得到的数据结果进行响应输出并在输出之后进行扫尾工作结束应用程序运行。在响应输出之前首先会构建好响应对象，将相关输出的内容存进Response对象，然后调用Response::send()方法将最终的应用返回的数据输出到页面。

继续调试，来到autoResponse()方法，这个方法程序会来回调用两次，第一次主要是为了创建响应对象，第二次是进行验证。我们先来看第一次，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012b7e11c341e70b61.jpg)

此时$data不是Response类的实例化对象，跳到了elseif分支中，调用Response类中的create()方法去获取响应输出的相关数据，构建Response对象。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0144783df27ffb2056.jpg)

执行new static($data, $code, $header, $options);实例化自身Response类，调用__construct()构造方法。

[![](https://p5.ssl.qhimg.com/t011414b7a9adadcbfd.jpg)](https://p5.ssl.qhimg.com/t011414b7a9adadcbfd.jpg)

可以看到这里将输出内容、页面的输出类型、响应状态码等数据都传递给了Response类对象，然后返回，回到刚才autoResponse()方法中

[![](https://p0.ssl.qhimg.com/t01ec3917241274d5f5.jpg)](https://p0.ssl.qhimg.com/t01ec3917241274d5f5.jpg)

到此确认了具体的输出数据，其中包含了输出的内容、类型、状态码等。

上面主要做的就是构建响应对象，将要输出的数据全部封装到Response对象中，用于接下来的响应输出。

继续调试，会返回到之前Dispatch类中的run()方法中去，并将$response实例对象赋给$data。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01120a0b863b753c6d.jpg)

紧接着会进行autoResponse()方法的第二次调用，同时将$data传入，进行验证。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e86e96537e00eb33.jpg)

这回$data是Response类的实例化对象，所以将$data赋给了$response后返回。

然后就开始调用Response类中send()方法，向浏览器页面输送数据。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014caa0f0850d85a57.jpg)

这里依次向浏览器发送了状态码、header头信息以及得到的内容结果。

[![](https://p5.ssl.qhimg.com/t01c53df7f4bc7af874.jpg)](https://p5.ssl.qhimg.com/t01c53df7f4bc7af874.jpg)

输出完毕后，跳到了appShutdown()方法，保存日志并结束了整个程序运行。

### 4.4 流程总结

上面通过动态调试一步一步地对URL解析的过程进行了分析，现在我们来简单总结下其过程：

首先发起请求-&gt;开始路由检测-&gt;获取pathinfo信息-&gt;路由匹配-&gt;开始路由解析-&gt;获得模块、控制器、操作方法调度信息-&gt;开始路由调度-&gt;解析模块和类名-&gt;组建命名空间&gt;查找并加载类-&gt;实例化控制器并调用操作方法-&gt;构建响应对象-&gt;响应输出-&gt;日志保存-&gt;程序运行结束



## 0x05 漏洞分析及POC构建

相信大家在看了上述内容后，对Thinkphp这个框架应该有所了解了。接下来，我们结合最近一个思路比较好的RCE漏洞再来看下。为了更好地理解漏洞，我通过以POC构造为导引的方式对漏洞进行了分析，同时以下内容也体现了我在分析漏洞时的想法及思路。

在/thinkphp/library/think/Container.php 中340行：

[![](https://p4.ssl.qhimg.com/t018a2d3176b3971073.jpg)](https://p4.ssl.qhimg.com/t018a2d3176b3971073.jpg)

在Container类中有个call_user_func_array()回调函数，经常做代码审计的小伙伴都知道，这个函数非常危险，只要能控制$function和$args，就能造成代码执行漏洞。

如何利用此函数？

通过上面的URL路由分析，我们知道Thinkphp可由外界直接控制模块名、类名和其中的方法名以及参数/参数值，那么我们是不是可以将程序运行的方向引导至这里来。

如何引导呢？

要调用类肯定需要先将类实例化，类的实例化首先需要获取到模块、类名，然后解析模块和类名去组成命名空间，再根据命名空间的特性去自动加载类，然后才会实例化类和调用类中的方法。

我们先对比之前正常的URL试着构建下POC。

http://127.0.0.1/tp5.1.20/public/index.php/index/test/hello/name/world

http://127.0.0.1/tp5.1.20/public/index.php/模块?/Container/invokefunction

构建过程中，会发现几个问题。

1.模块应该指定什么，因为Container类并不在模块内。

2.模块和类没有联系，那么组建的命名空间，程序如何才能加载到类。

先别着急，我们先从最开始的相关值获取来看看（获取到模块、类名），此过程对应上面第四大节中的4.3.3路由解析中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01edf347b3f333c3f9.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01aaeaba267a0e4ce7.png)

app_multi_module为true，所以肯定进入if流程,获取了$module、$bind、$available的值。在红色框处如果不为true，则会直接报错结束运行，所以此处需要$module和$available都为True。而$available的值一开始就被定义为False，只有在后续的3个if条件中才会变为true。

来看下这3个if条件，在默认配置下，由于没有路由绑定，所以$bind为null。而empty_module默认模块也没有定义。所以第三个也不满足，那么只能寄托于第二个了。

[![](https://p5.ssl.qhimg.com/t010f96f19a1292158a.png)](https://p5.ssl.qhimg.com/t010f96f19a1292158a.png)

在第二个中，1是判断$module是否在禁止访问模块的列表中，2是判断是否存在这个模块。

[![](https://p1.ssl.qhimg.com/t01140bd593805ef58c.png)](https://p1.ssl.qhimg.com/t01140bd593805ef58c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017685a04050505cf0.jpg)

所以，这就要求我们在构造POC时，需要保证模块名必须真实存在并且不能在禁用列表中。在默认配置中，我们可以指定index默认模块，但是在实际过程中，index模块并不一定存在，所以就需要大家去猜测或暴力破解了，不过一般模块名一般都很容易猜解。

获取到模块、类名后，就是对其进行解析组成命名空间了。此过程对应上面第四大节中的4.3.4路由调度中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015cf45472c3f14e17.jpg)

这里首先对$name(类名)进行判断，当$name以反斜线\开始时会直接将其作为类的命名空间路径。看到这里然后回想一下之前的分析，我们会发现这种命名空间路径获取的方式和之前获取的方式不一样(之前是进入了parseClass方法对模块、类名等进行拼接)，而且这种获取是不需要和模块有联系的，所以我们想是不是可以直接将类名以命名空间的形式传入，然后再以命名空间的特性去自动加载类？同时这样也脱离了模块这个条件的束缚。

那我们现在再试着构造下POC：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0199a26a5ca562f48e.jpg)

http://127.0.0.1/tp5.1.20/public/index.php/index/think\Container/invokefunction

剩下就是指定$function参数和$var参数值了,根据传参特点，我们来构造下。

http://127.0.0.1/tp5.1.20/public/index.php/index/think\Container/invokefunction/function/call_user_func_array/vars[0]/phpinfo/vars[1][]/1

构造出来应该是这样的，但是由于在pathinfo模式下，$_SERVER[‘PATH_INFO’]会自动将URL中的“\”替换为“/”，导致破坏掉命名空间格式，所以我们采用兼容模式。

默认配置中，var_pathinfo默认为s，所以我们可以用$_GET[‘s’]来传递路由信息。

http://127.0.0.1/tp5.1.20/public/index.php?s=index/think\Container/invokefunction&amp;function=call_user_func_array&amp;vars[0]=phpinfo&amp;vars[1][]=1

另外由于App类继承于Container类，所以POC也可以写成：

http://127.0.0.1/tp5.1.20/public/index.php?s=index/think\App/invokefunction&amp;function=call_user_func_array&amp;vars[0]=phpinfo&amp;vars[1][]=1

漏洞利用扩大化

1.以反斜线\开始时直接将其作为类的命名空间路径。

2.thinkphp命名空间自动加载类的特性。

由于这两点，就会造成我们可以调用thinkphp框架中的任意类。所以在框架中，如果其他类方法中也有类似于invokefunction()方法中这样的危险函数，我们就可以随意利用。

例如：Request类中的input方法中就有一样的危险函数。

[![](https://p3.ssl.qhimg.com/t01e0d5f6a6fa41094e.jpg)](https://p3.ssl.qhimg.com/t01e0d5f6a6fa41094e.jpg)

跟入filterValue()方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0142e185ab6a9c4fa3.jpg)

POC:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0133c2391da30fc2cc.jpg)

http://127.0.0.1/tp5.1.20/public/index.php?s=index/\think\Request/input&amp;filter=phpinfo&amp;data=1



## 0x05 结语

写这篇文章的其中一个目的是想让大家知道，通过框架分析，我们不仅可以在分析漏洞时变得更加容易，同时也可以对漏洞原理有一个更深的理解。所以，当我们在分析一个漏洞时，如果很吃力或者总有点小地方想不通的时候，不如从它的框架着手，一步一步来，或许在你学习完后就会豁然开朗，亦或者在过程中你就会明白为什么。

天融信阿尔法实验室成立于2011年，一直以来，阿尔法实验室秉承“攻防一体”的理念，汇聚众多专业技术研究人员，从事攻防技术研究，在安全领域前瞻性技术研究方向上不断前行。作为天融信的安全产品和服务支撑团队，阿尔法实验室精湛的专业技术水平、丰富的排异经验，为天融信产品的研发和升级、承担国家重大安全项目和客户服务提供强有力的技术支撑。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0164db2d0728f48477.jpg)

天融信阿尔法实验室
