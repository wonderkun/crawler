> 原文链接: https://www.anquanke.com//post/id/215662 


# 代码审计从0到1 —— Centreon One-click To RCE


                                阅读量   
                                **189947**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01291c19ada56ccc55.png)](https://p5.ssl.qhimg.com/t01291c19ada56ccc55.png)



作者：huha@知道创宇404实验室

## 前言

代码审计的思路往往是多种多样的，可以通过历史漏洞获取思路、黑盒审计快速确定可疑点，本文则侧重于白盒审计思路，对Centreon V20.04[[1](https://github.com/centreon/centreon/releases/tag/20.04.0)]的审计过程进行一次复盘记录，文中提及的漏洞均已提交官方并修复。



## 概述

Centreon（Merethis Centreon）是法国Centreon公司的一套开源的系统监控工具 。该产品主要提供对网络、系统和应用程序等资源的监控功能。



## 网站基本结构

源代码目录组成

[![](https://p1.ssl.qhimg.com/t01e5c9b0a1cac58bb4.png)](https://p1.ssl.qhimg.com/t01e5c9b0a1cac58bb4.png)

`centreon/www/`网站根目录

[![](https://p0.ssl.qhimg.com/t01da055e8d7f05c4ef.png)](https://p0.ssl.qhimg.com/t01da055e8d7f05c4ef.png)

`centreon/www/include/`核心目录结构

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0149036f42f1038423.png)

概述一下
<li>
`centreon/www/index.php`是网站的入口文件，会先进行登录认证，未登录的话跳转进入登录页，登录成功后进入后台</li>
<li>
`centreon/www/main.php`与`centreon/www/main.get.php`，对应PC端与移动端的路由功能，根据不同的参数，可以加载到后台不同的功能页面，在实际调试的过程，发现使用main.php加载对应的功能页时，最终会调用main.get.php，所以路由部分直接看main.get.php即可</li>
<li>
`entreon/www/include/`目录包含核心功能代码、公共类。其中有些功能代码可以直接通过路径访问，有些则需要通过main.get.php页面进行路由访问</li>
<li>
`centreon/www/api/`目录下的index.php是另一处路由功能，可以实例化`centreon/www/api/class/*.class.php`、`centreon/www/modules/`、`centreon/www/widgets/*/webServices/rest/*.class.php`、`centreon/src/`中的类并调用指定方法</li>
在审计代码的时候，有两个要关注点：
- 重点审查`centreon/www/include/`和`centreon/www/api/class`/两个目录，因为这些目录下的功能点可以通过`centreon/www/main.php`或`centreon/www/api/index.php`路由访问
- 重点寻找绕过登录认证或者越权的方式，否则后台漏洞难以利用


## 代码分析

如下简要分析`centreon/www/`目录下的部分脚本

### <a class="reference-link" name="index.php"></a>index.php

index.php会进行登录认证，检查是否定义$_SESSION[“centreon”]变量，这个值在管理员登录后设置。程序登录有两种方式，使用账密或者token，相关逻辑在`/centreon/www/include/core/login/processLogin.php`中。不止index.php，`centreon/www/include/`下大部分功能页都会检查session，没有登录就无法访问

### <a class="reference-link" name="main.get.php"></a>main.get.php

这是主要的路由功能，程序开头对数据进行过滤。$_GET数组使用fiter_var()过滤处理，编码特殊字符，有效地防御了一些XSS，比如可控变量在引号中的情况，无法进行标签闭合，无法逃逸单引号

[![](https://p0.ssl.qhimg.com/t014ed5548001b00299.png)](https://p0.ssl.qhimg.com/t014ed5548001b00299.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e051666598f0d832.png)

对$_GET和 $_POST中的指定参数，进行过滤处理，对数据类型进行限制，对特殊字符进行编码

[![](https://p0.ssl.qhimg.com/t01ee32ec545eb69a5b.png)](https://p0.ssl.qhimg.com/t01ee32ec545eb69a5b.png)

最终$_GET或$_POST数组赋值到$inputs数组中

[![](https://p4.ssl.qhimg.com/t01bd55b304a1f5a5f7.png)](https://p4.ssl.qhimg.com/t01bd55b304a1f5a5f7.png)

全局过滤数据后，程序引入公共类文件和功能代码

[![](https://p0.ssl.qhimg.com/t015d44e40972f0f4ad.png)](https://p0.ssl.qhimg.com/t015d44e40972f0f4ad.png)

99行$contreon变量在header.php中的$session取出，认证是否登录

[![](https://p1.ssl.qhimg.com/t01c516f405e790e7fd.png)](https://p1.ssl.qhimg.com/t01c516f405e790e7fd.png)

通过登录认证后，程序会查询数据库，获取page与url的映射关系，程序通过p参数找到对应的url，进行路由，映射关系如下

[![](https://p0.ssl.qhimg.com/t012760db111a9a834f.png)](https://p0.ssl.qhimg.com/t012760db111a9a834f.png)

接着248行`include_once $url`，引入`centreon/www/include/`下对应的脚本

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01480cf142a3e32f6c.png)

这里将page与url映射关系存储到本地，方便后续查询

[![](https://p3.ssl.qhimg.com/t01a51b99ca8e24879d.png)](https://p3.ssl.qhimg.com/t01a51b99ca8e24879d.png)

### <a class="reference-link" name="api/index.php"></a>api/index.php

这是另外一个路由功能

[![](https://p0.ssl.qhimg.com/t01860f627462bd1e22.png)](https://p0.ssl.qhimg.com/t01860f627462bd1e22.png)

同样需要验证登录，104行$_SERVER[‘HTTP_CENTREON_AUTH_TOKEN’]可以在请求头中伪造，但是并不能绕过登录，可以跟进查看CentreonWebService::router方法

在`\api\class\webService.class.php`，其中$object和$action参数可控

[![](https://p4.ssl.qhimg.com/t019d35870e749925ed.png)](https://p4.ssl.qhimg.com/t019d35870e749925ed.png)

311行判断isService是否为true，如果是，$webService[‘class’]赋值为$dependencyInjector[‘centreon.webservice’]-&gt;get($object)，否则赋值为webservicePath($object)

[![](https://p0.ssl.qhimg.com/t01f4937b90aa47d368.png)](https://p0.ssl.qhimg.com/t01f4937b90aa47d368.png)

313行centreon.webservice属性值如下，对应的是centreon/src目录下的类

[![](https://p4.ssl.qhimg.com/t01c9d0aa9569bfd3fa.png)](https://p4.ssl.qhimg.com/t01c9d0aa9569bfd3fa.png)

$webServicePaths变量包含以下类路径

[![](https://p0.ssl.qhimg.com/t015dbe8326447cc128.png)](https://p0.ssl.qhimg.com/t015dbe8326447cc128.png)

接着346行检查类中是否存在对应方法，在374行处调用，但是在350~369进行了第二次登录认证，所以之前$_SERVER[‘HTTP_CENTREON_AUTH_TOKEN’]伪造并没能绕过登录

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fd13208479b93930.png)

### <a class="reference-link" name="%E8%BF%87%E6%BB%A4%E5%A4%84%E7%90%86"></a>过滤处理

除了main.get.php开头的全局过滤操作，程序的其他过滤都是相对较分散的，对于SQL注入的话，程序的很多查询都使用了PDO进行参数化查询，对于PDO中一些直接拼接的参数，则单独调用某些函数进行过滤处理。比如下边这里进行数据库更新操作时，updateOption()会进行query操作，$ret[“nagios_path_img”]可控，但是这里调用escape()函数进行转义

[![](https://p3.ssl.qhimg.com/t01d9e1ec141f76de19.png)](https://p3.ssl.qhimg.com/t01d9e1ec141f76de19.png)

### <a class="reference-link" name="%E8%B7%AF%E5%BE%84%E9%99%90%E5%88%B6"></a>路径限制

不通过路由功能，直接访问对应路径的功能代码，大部分是不被允许的，比如直接访问generateFiles.php页面

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d65be94e99cfd236.png)

可以看到39行检查$oreon参数是否存在，不存在则直接退出，刚才在分析main.get.php中说，header.php会初始化$oreon参数，这就是为什么要通过main.get.php去访问某些功能点。当然有一些漏网之鱼，比如rename.php页面，这里只是检查session是否存在，在登录状态下，可以通过路径直接访问该页面。

[![](https://p2.ssl.qhimg.com/t01c3cd8f9c534e1e93.png)](https://p2.ssl.qhimg.com/t01c3cd8f9c534e1e93.png)



## One-click To RCE

### <a class="reference-link" name="XSS"></a>XSS

在上一节的最后，为什么要纠结通过路径访问还是路由访问呢？因为通过main.get.php中的路由访问的话，会经过全局过滤处理，直接通过路径访问则没有，这样就有了产生漏洞的可能，通过这个思路可以找到一个XSS漏洞，在rename.php中程序将攻击者可控的内容直接打印输出，并且没有进行编码处理，缺乏Httponly与CSP等的攻击缓存机制，当管理员点击精心构造的链接时，将触发XSS执行任意js代码，导致cookie泄露。

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

漏洞入口

centreon/include/home/customViews/rename.php

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d35f79bca55fa7f4.png)

前边也提到，46行验证session是否存在，所以受害者只要处于登录状态即可，59行echo直接打印$widgetObj-&gt;rename($_REQUEST)返回的值，rename函数中对$params[‘elementId’]进行一些验证，最后返回$params[‘newName’]，因为直接通过路径访问，没有经过任何过滤处理

[![](https://p1.ssl.qhimg.com/t01b43979c53f9d7396.png)](https://p1.ssl.qhimg.com/t01b43979c53f9d7396.png)

所以elementId控制为title_1(任意数字),设置newName为script标签即可

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ea4d2068f3b8dc67.png)

### <a class="reference-link" name="%E6%8E%88%E6%9D%83RCE"></a>授权RCE

程序在使用perl脚本处理mib文件时，没有对反引号的内容进行正确的过滤处理，攻击者利用XSS窃取的凭证登录后，可上传恶意文件导致远程代码执行，即One_click to RCE

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

可以顺着CVE-2020-12688[[2](https://github.com/TheCyberGeek/Centreon-20.04)]的思路，全局搜索”shell_exec(“关键字符串， formMibs.php调用了该函数

[![](https://p5.ssl.qhimg.com/t01a7b751d91a9f9324.png)](https://p5.ssl.qhimg.com/t01a7b751d91a9f9324.png)

查看源码，38行执行了shell_exec($command)，发现$command从$form中取值，在14行添加var_dump($form)，打印$form方便调试

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.anquanke.com/post/id/215662/dfa99a71-a5d6-4fc8-a414-e53ee5ae3b3d/)

之前记录的page与url的映射关系现在就可以派上用场了，设置page为61703，通过main.php或main.get.php可以路由到formMibs.php，也就是下边的文件上传功能

[![](https://p1.ssl.qhimg.com/t012ab318ebb86828df.png)](https://p1.ssl.qhimg.com/t012ab318ebb86828df.png)

调试发现formMibs.php中31行的$values[“tmp_name”]是缓存文件名不可控，$manufacturerId可以通过上传数据包中mnftr字段修改，但是被filter_var()处理，只能为整数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01253dd9d471c27b44.png)

虽然缓存文件名是不可控的，但是上传的mib文件内容可控，shell_exec()中执行的命令实际为（”xxx.mib”代表缓存文件名）

```
/usr/share/centreon/bin/centFillTrapDB -f 'xxx.mib' -m 3 --severity=info 2&gt;&amp;1
```

centFillTrapDB是一个perl脚本，代码在/bin/centFillTrapDB中，用use引入centFillTrapDB模块

[![](https://p2.ssl.qhimg.com/t01465e73aa05b09255.png)](https://p2.ssl.qhimg.com/t01465e73aa05b09255.png)

use命令寻找的路径默认在[@INC](https://github.com/INC)下，但不知道具体在哪里，可以全局搜索一下

[![](https://p0.ssl.qhimg.com/t01d00fb2aa570814df.png)](https://p0.ssl.qhimg.com/t01d00fb2aa570814df.png)

最后在usr/share/perl5/vendor_perl/centreon下找到script目录，有我们想要的文件

[![](https://p5.ssl.qhimg.com/t0149d043e8850f966b.png)](https://p5.ssl.qhimg.com/t0149d043e8850f966b.png)

把centFillTrapDB模块拉出来静态看一下，发现存在命令执行且内容可控的位置，实际调试发现最终分支是进入541行，540行和543行是我添加的调试代码

[![](https://p1.ssl.qhimg.com/t01f8094323ace56e3c.png)](https://p1.ssl.qhimg.com/t01f8094323ace56e3c.png)

在perl中反引号内可以执行系统命令，534行$mib_name可控，所以$trap_lookup可控，对于mib文件来说，$mib_name为DEFINITIONS::=BEGIN前面红框部分，空格会被过滤，但可以用$`{`IFS`}`代替

[![](https://p2.ssl.qhimg.com/t018bb1207840d781f5.png)](https://p2.ssl.qhimg.com/t018bb1207840d781f5.png)

为了方便构造mib文件，打印出反引号中的命令，并在服务器shell中进行测试

[![](https://p0.ssl.qhimg.com/t0199f9d5000d6ef365.png)](https://p0.ssl.qhimg.com/t0199f9d5000d6ef365.png)

构造/tmp/1.mib文件

[![](https://p3.ssl.qhimg.com/t016a34bfeb74476b4b.png)](https://p3.ssl.qhimg.com/t016a34bfeb74476b4b.png)

命令行执行

```
centFillTrapDB -f '/tmp/1.mib' -m 3 --severity=info 2&gt;&amp;1
```

可以清晰的看到command，并且执行了curl命令

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010e7d81f08c8c0f29.png)

修改mib文件中的命令，在浏览器上传进行测试，成功执行whoami并回显

[![](https://p3.ssl.qhimg.com/t0161af5d1b1cf1543b.png)](https://p3.ssl.qhimg.com/t0161af5d1b1cf1543b.png)



## 审计总结

文本主要分享了一些白盒审计思路，但就像之前所说的，审计的思路往往是多种多样的，以下是个人的小小总结：
- 分析历史漏洞，在复现和调试的过程中，可以比较快的了解这个框架的结构，也可以从历史漏洞中获取思路，举一反三
- 黑盒审计，开启抓包工具，测试可疑的功能点并观察数据包，这样可以加快对网站路由的熟悉，也可以快速的验证一些思路，排除一些可能性，仍然存疑的功能点可以在白盒审计时进一步确认；
- 白盒审计，入口脚本，路由方式，核心配置，常用功能模块和数据验证过滤操作，这些都是要留意的，当然最主要还是看入口，路由和数据过滤验证的部分；其他的如核心配置，常用功能模块，可以按需查看，大概了解了网站架构就可以开始看对应的功能代码了，看的时候可以分两个角度：一个就是从刚才黑盒测试遗留的可疑点入手，断点功能代码，审查是否存在漏洞；另一个就是从敏感关键字入手，全局搜索，溯源追踪。
- 注重不同漏洞的组合攻击，无论是这次的Centreon One_click to RCE漏洞，还是通达OA任意删除认证文件导致的未授权RCE、PHPCMS V9 authkey泄露导致的未授权RCE，打的都是一套组合拳，在漏洞挖掘的过程可以多加关注


## 参考链接

[1] Centreon V20.04

[https://github.com/centreon/centreon/releases/tag/20.04.0](https://github.com/centreon/centreon/releases/tag/20.04.0)

[2] CVE-2020-12688漏洞公开细节

[https://github.com/TheCyberGeek/Centreon-20.04](https://github.com/TheCyberGeek/Centreon-20.04)
