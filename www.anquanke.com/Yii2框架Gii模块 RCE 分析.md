> 原文链接: https://www.anquanke.com//post/id/218190 


# Yii2框架Gii模块 RCE 分析


                                阅读量   
                                **178042**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01a6fe8fe7bbc95ae4.png)](https://p0.ssl.qhimg.com/t01a6fe8fe7bbc95ae4.png)



利用周末时间分析了Yii2框架的一个RCE漏洞，利用了框架可以写PHP模板的功能，控制写入的内容为恶意代码，实现对指定的文件写入php 命令执行语句，调用PHP从而获取系统权限。



## 0x01 Yii 介绍

Yii 是一个高性能，基于组件的 PHP 框架，用于快速开发现代 Web 应用程序。一个通用的 Web 编程框架，即可以用于开发各种用 PHP 构建的 Web 应用。 因为基于组件的框架结构和设计精巧的缓存支持，它特别适合开发大型应用， 如门户网站、社区、内容管理系统（CMS）、 电子商务项目和 RESTful Web 服务等。
- 和其他 PHP 框架类似，Yii 实现了 MVC（Model-View-Controller） 设计模式并基于该模式组织代码。
- Yii 非常易于扩展。
- Yii 的代码简洁优雅。


## 0x02 环境搭建

利用docker 原生ubuntu镜像搭建漏洞调试环境

### <a class="reference-link" name="0x01%20composer%20%E5%AE%89%E8%A3%85"></a>0x01 composer 安装

> Composer 是 PHP 的一个依赖管理工具。它允许你申明项目所依赖的代码库，它会在你的项目中为你安装他们。

你可以将此文件放在任何地方。如果你把它放在系统的 PATH 目录中，你就能在全局访问它。 在类Unix系统中，你甚至可以在使用时不加 php 前缀。<br>
你可以执行这些命令让 composer 在你的系统中进行全局调用：

```
curl -sS https://getcomposer.org/installer | php
mv composer.phar /usr/local/bin/composer
```

### <a class="reference-link" name="0x02%20yii2%20%E5%AE%89%E8%A3%85"></a>0x02 yii2 安装

安装composer过后，需要安装git 以及php插件，composer在安装yii2框架时会从git上clone项目，只不过不保留.git文件夹。

```
apt install apache2 php 
apt install zip unzip git php-mbstring php-curl php-dom -y
composer create-project --prefer-dist yiisoft/yii2-app-basic basic
```

[![](https://p4.ssl.qhimg.com/t017b587a7314c75eab.png)](https://p4.ssl.qhimg.com/t017b587a7314c75eab.png)

至此yii2框架就基本搭建完成了，有了composer 之后确实方便了很多。

### <a class="reference-link" name="0x03%20%E6%95%B0%E6%8D%AE%E5%BA%93%E6%90%AD%E5%BB%BA%E5%8F%8A%E8%BF%9E%E6%8E%A5"></a>0x03 数据库搭建及连接

利用docker搭建数据库，注意在数据库中创建新库和数据表

```
docker run  --name mysql -e MYSQL_ROOT_PASSWORD=123456 -d mysql:5.7
```

```
vim /var/www/html/basic/config/db.php
```

[![](https://p0.ssl.qhimg.com/t01ea597151814c034f.png)](https://p0.ssl.qhimg.com/t01ea597151814c034f.png)

### <a class="reference-link" name="0x04%20Xdebug%20%E5%AE%89%E8%A3%85"></a>0x04 Xdebug 安装

> <p>pecl PHP Extension Community Library的缩写，即PHP 扩展库。[https://pecl.php.net/](https://pecl.php.net/)<br>
PECL是使用C语言开发的，通常用于补充一些用PHP难以完成的底层功能，往往需要重新编译或者在配置文件中设置后才能在用户自己的代码中使用。</p>

利用pecl 安装xdebug 并进行配置

```
apt-get install php-pear 
apt-get install php-phpize
pecl install xdebug
```

将xdebug.so与php相关联，xdebug.ini 配置如下

```
zend_extension=/usr/lib/php/20190902/xdebug.so
xdebug.remote_enable=1
xdebug.remote_connect_back=0
xdebug.remote_host=172.19.0.12
xdebug.remote_port=9000
```

向apache的php配置添加xdebug.ini配置文件，并重启服务

```
cp  /usr/share/php/docs/xdebug/xdebug.ini /etc/php/7.4/apache2/conf.d/


service apache2 restart
```

[![](https://p2.ssl.qhimg.com/t01d99929af22430a2c.png)](https://p2.ssl.qhimg.com/t01d99929af22430a2c.png)

## 0x05 远程调试配置

因为服务在服务器端，本地需要phpstorm调试需要配置端口转发，将本地端口转到服务器上去。又因为服务在服务器docker内部因此也需要把ssh端口转发出来。操作如下

**在服务器执行**

[![](https://p0.ssl.qhimg.com/t01c6d5908509ddcf7b.png)](https://p0.ssl.qhimg.com/t01c6d5908509ddcf7b.png)

**在docker内执行**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019148a65e279aa475.png)

**在本地执行**

[![](https://p5.ssl.qhimg.com/t01f61cc91fb50524cd.jpg)](https://p5.ssl.qhimg.com/t01f61cc91fb50524cd.jpg)

配置phpstorm，进行远程文件关联

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013ec72abf7de65017.png)

配置sftp

[![](https://p0.ssl.qhimg.com/t017bfa45212b950508.png)](https://p0.ssl.qhimg.com/t017bfa45212b950508.png)

### <a class="reference-link" name="0x06%20%E6%B7%BB%E5%8A%A0%E7%99%BD%E5%90%8D%E5%8D%95"></a>0x06 添加白名单

gii 默认添加了白名单访问，这里只需加个`*`就可以了

[![](https://p1.ssl.qhimg.com/t012ffa0cc022de88d0.png)](https://p1.ssl.qhimg.com/t012ffa0cc022de88d0.png)



## 0x04 漏洞利用

### <a class="reference-link" name="0x1%20%E7%94%9F%E6%88%90%E6%81%B6%E6%84%8F%E4%BB%A3%E7%A0%81%E6%96%87%E4%BB%B6"></a>0x1 生成恶意代码文件

所有环境都配置好后，选择创建的数据表并制定类名

[![](https://p2.ssl.qhimg.com/t0164483fe37ac489f2.png)](https://p2.ssl.qhimg.com/t0164483fe37ac489f2.png)

在Message Category字段处填写恶意代码，如下图所示

[![](https://p1.ssl.qhimg.com/t013edeec6fa128dfa7.png)](https://p1.ssl.qhimg.com/t013edeec6fa128dfa7.png)

### <a class="reference-link" name="0x2%20%E8%A7%A6%E5%8F%91%E6%81%B6%E6%84%8F%E6%96%87%E4%BB%B6"></a>0x2 触发恶意文件

### [![](https://p1.ssl.qhimg.com/t013d18ed14ba29d026.png)](https://p1.ssl.qhimg.com/t013d18ed14ba29d026.png)



## 0x03 漏洞原理及调试

### <a class="reference-link" name="0x0%20%E6%BC%8F%E6%B4%9E%E5%8E%9F%E7%90%86"></a>0x0 漏洞原理

yiisoft/yii2-gii/src/Generator.php#L505 存在参数拼接，而且没有检查用户传递的参数。

[![](https://p1.ssl.qhimg.com/t014e03842e9eae77f4.png)](https://p1.ssl.qhimg.com/t014e03842e9eae77f4.png)

### <a class="reference-link" name="0x1%20%E8%B7%AF%E7%94%B1%E4%BB%8B%E7%BB%8D"></a>0x1 路由介绍

yii用了统一的路由分发，路由的工作可以分为两步：
1. 从请求中解析出一个路由和相关参数；
1. 根据路由生成响应的控制器操作，来处理该请求。
### <a class="reference-link" name="1.%20%E8%A7%A3%E6%9E%90%E5%8F%82%E6%95%B0"></a>1. 解析参数

Application.php:103, yii\web\Application-&gt;handleRequest()

[![](https://p5.ssl.qhimg.com/t01c112fce28efdb1a9.png)](https://p5.ssl.qhimg.com/t01c112fce28efdb1a9.png)

从url中获取route 和 参数

[![](https://p4.ssl.qhimg.com/t01dc3c5f8e6f5b5948.png)](https://p4.ssl.qhimg.com/t01dc3c5f8e6f5b5948.png)

调用栈关系

```
Request.php:699, yii\web\Request-&gt;getQueryParam()
UrlManager.php:365, yii\web\UrlManager-&gt;parseRequest()
Request.php:275, yii\web\Request-&gt;resolve()
Application.php:82, yii\web\Application-&gt;handleRequest()
Application.php:386, yii\web\Application-&gt;run()
index.php:12, `{`main`}`()
```

### <a class="reference-link" name="0x2%20%E7%94%9F%E6%88%90%E6%8E%A7%E5%88%B6%E5%99%A8"></a>0x2 生成控制器

[![](https://p0.ssl.qhimg.com/t01863c8387a5a4e5c0.png)](https://p0.ssl.qhimg.com/t01863c8387a5a4e5c0.png)

Module.php:522, yii\web\Application-&gt;runAction()

[![](https://p5.ssl.qhimg.com/t012b637c2f20d728b2.png)](https://p5.ssl.qhimg.com/t012b637c2f20d728b2.png)

具体实现将url get参数分割成id和route，匹配是不是已配置 module

[![](https://p3.ssl.qhimg.com/t01d3b54307fdb6ef8c.png)](https://p3.ssl.qhimg.com/t01d3b54307fdb6ef8c.png)

如果不是已有module那么将会根据id生成controller

[![](https://p1.ssl.qhimg.com/t01c989ff48e5bf3e6e.png)](https://p1.ssl.qhimg.com/t01c989ff48e5bf3e6e.png)

[![](https://p3.ssl.qhimg.com/t01535df09015187b9f.png)](https://p3.ssl.qhimg.com/t01535df09015187b9f.png)

完整调用栈如下

```
Module.php:643, yii\web\Application-&gt;createControllerByID()
Module.php:596, yii\web\Application-&gt;createController()
Module.php:522, yii\web\Application-&gt;runAction()
Application.php:103, yii\web\Application-&gt;handleRequest()
Application.php:386, yii\web\Application-&gt;run()
index.php:12, `{`main`}`()
```

最后在runwithParams函数中完成类函数调用

[![](https://p5.ssl.qhimg.com/t01c6c5354195127a71.png)](https://p5.ssl.qhimg.com/t01c6c5354195127a71.png)

### <a class="reference-link" name="0x2%20%E5%8F%AF%E6%8E%A7%E5%8F%82%E6%95%B0%E4%BC%A0%E9%80%92%E9%93%BE"></a>0x2 可控参数传递链

在生成恶意代码的时候，是将我们传入的post参数写了进去。这个过程还是比较复杂的，调试跟了下归结为几个步骤。
1. actionPreview功能将收到的post参数解析带入到$generator对象中
1. actionPreview将解析好的对象成员保存为json格式在runtime目录下
1. actionView读取json格式数据并解析成对象成员变量
1. 调用到renderFile生成php code并将其写入文件中
**<a class="reference-link" name="1.%20actionPreview%20post%E5%8F%82%E6%95%B0%E8%A7%A3%E6%9E%90"></a>1. actionPreview post参数解析**

在DefaultController类中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f5d5078956815c9a.png)

[![](https://p4.ssl.qhimg.com/t01440b8d7f9a5727bd.png)](https://p4.ssl.qhimg.com/t01440b8d7f9a5727bd.png)

<a class="reference-link" name="2.%20actionPreview%20%E4%BF%9D%E5%AD%98%E4%B8%BAjson"></a>**2. actionPreview 保存为json**

该操作将post包中的参数保存为json格式，并存储到文件中

[![](https://p4.ssl.qhimg.com/t01e39d4b4f5e20cc82.png)](https://p4.ssl.qhimg.com/t01e39d4b4f5e20cc82.png)

<a class="reference-link" name="3.%20actionView%20%E8%AF%BB%E5%8F%96json%E6%96%87%E4%BB%B6"></a>**3. actionView 读取json文件**

从json文件中解析类成员变量

[![](https://p1.ssl.qhimg.com/t01c1ce92c43a325cba.png)](https://p1.ssl.qhimg.com/t01c1ce92c43a325cba.png)

<a class="reference-link" name="4.%20%E6%96%87%E4%BB%B6%E7%94%9F%E6%88%90"></a>**4. 文件生成**

漏洞生成的文件如下

[![](https://p0.ssl.qhimg.com/t01d1ec519e15065c4a.png)](https://p0.ssl.qhimg.com/t01d1ec519e15065c4a.png)

[![](https://p1.ssl.qhimg.com/t01d599ac6da1993995.png)](https://p1.ssl.qhimg.com/t01d599ac6da1993995.png)



## 0x04 补丁分析

简单的加了个过滤

[![](https://p0.ssl.qhimg.com/t011265fcd438a7d5d7.png)](https://p0.ssl.qhimg.com/t011265fcd438a7d5d7.png)



## 0x05 参考链接

[https://github.com/yiisoft/yii2-gii/issues/433](https://github.com/yiisoft/yii2-gii/issues/433)

[https://lab.wallarm.com/yii2-gii-remote-code-execution/](https://lab.wallarm.com/yii2-gii-remote-code-execution/)
