> 原文链接: https://www.anquanke.com//post/id/86178 


# 【技术分享】Joomla 框架的程序执行流程及目录结构分析


                                阅读量   
                                **222265**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p3.ssl.qhimg.com/t01523efc6f2ddf5fd8.png)](https://p3.ssl.qhimg.com/t01523efc6f2ddf5fd8.png)**

****

作者：[Lucifaer](http://bobao.360.cn/member/contribute?uid=2789273957)

预估稿费：400RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**0x00 文件目录介绍**

**目录**



```
administrator/   # 管理后台目录
bin/             # 该文件夹存放一些基于Joomla框架开发的一些实用的脚本
cache/           # 文件缓存目录
cli/             # 该文件夹存放一些终端使用的命令，用于操作当前的站点
components/      # Joomla组件目录
images/          # 网站内容使用的媒体文件目录，后台有对此文件夹进行管理的功能
includes/        # 运行Joomla需要包含的基础文件
language/        # 语言目录，多语言的翻译都存放在这里
layouts/         # 应该是控制布局的，没有注意过是哪个版本加上的，也没研究过，等有时间了研究一下再写
libraries/       # Joomla使用的库文件
logs/            # 日志目录，一些异常处理都会存放在这个文件夹里，例如后台登录时输入错误的用户名和密码
media/           # Joomla使用到的媒体文件，主要是页面渲染会用到的，存放的内容跟images目录有区别，而且后台是没有对其进行管理的功能的
modules/         # Joomla模块目录
plugins/         # Joomla插件目录
templates/       # Joomla站点模板目录
tmp/             # 临时目录，如安装组件或模块时残留的解压文件等
```

**文件**



```
configuration.php   # Joomla配置文件
htaccess.txt        # 帮助我们生成.htaccess
index.php           # Joomla单入口文件
LICENSE.txt         # 不多叙述
README.txt          # 不多叙述
robots.txt          # 搜索引擎爬行使用的文件
web.config.txt      # 据说是IIS使用的文件
```



**0x01 Joomla的MVC**

在Joomla中并不像国内的一些cms一样，主要功能的实现放在组件中，下面就说一说Joomla中的四个非常重要的东西：组件、模块、控制器、视图。

**1. 组件**

在Joomla中，组件可以说是最大的功能模块。一个组件分为两部分：前台和后台。后台主要用于对对应内容的管理，前台主要用于前台页面的呈现和响应各种操作。其文件目录分别对应于joomla/administrator/components和joomla/components。组件有自己的命名规则，文件夹名须命名为com_组件名，组件的访问也是单文件入口，入口文件为com_组件名/组件名.php。如components/com_content/content.php。

其中**option=com_content&amp;view=article&amp;id=7**，它会先调用**content.php**，再由router.php路由到article视图，再调用相应的Model层取出ID=7的分类信息，渲染之后呈现在模板中的jdoc:include type=”component位置上。

**2. 模块**

与组件（Component）不同的是，模块（Module）是不能通过URL直接访问的，而是通过后台对模块的设置，根据菜单ID（URL中的Itemid）来判断当前页面应该加载哪些模块。所以它主要用于显示内容，而一些表单提交后的处理动作一般是放在组件中去处理的。因此，模块通常都是比较简单的程序，文件结构也很清晰易懂，如modules/mod_login模块中的文件结构如下：



```
modlogin.xml # 模块配置及安装使用的文件
mod_login.php # 模块入口文件，以mod模块名.php命名，可以看作Controller层
helper.php # 辅助文件，通常数据操作会放在这里，可以看作Model层
tmpl/ # 模板文件夹，View层
| default.php # 默认模板
| default_logout.php # 退出登录模板
```

**2.1 模块调用的另外一个参数**

在模板的首页文件中，我们会看到调用模块时有如下代码

```
jdoc:include type="modules" name="position-7" style="well"
```

这里多了一个style参数，这个其实是一个显示前的预处理动作，在当前模板文件夹中的html/modules.php中定义，打开这个文件我们就能看到有一个modChrome_well的函数，程序不是很复杂，只是在显示前对html做了下预处理。

**2.2 模块的另外一种调用方法**

有时候会需要在程序里调用一个模块来显示，可以用以下程序来调用

该程序会显示所有设置在position位置上的模块，当然也会根据菜单ID来判断是否加载



```
$modules = &amp;amp; JModuleHelper::getModules('position');
foreach($modules as $module)`{`
    echo JModuleHelper::renderModule($module, array('style' = 'well'))
`}`
```

**3.模板**

个人理解，模板就相当于输出的一种格式。也就是在后端已经调用了相关的数据，准备在前端以什么样的格式输出。

在Joomla中，一个页面只能有一个主要内容（组件：component），其他均属于模块。如图：

[![](https://p2.ssl.qhimg.com/t01f2f5f6cd94e74d79.png)](https://p2.ssl.qhimg.com/t01f2f5f6cd94e74d79.png)

如果从代码来分析的话，打开index.php（组件下的index.php），除了简单的HTML和php外，还可以看到以下几类语句：



```
jdoc:include type="head"
jdoc:include type="modules" name="position-1" style="none"
jdoc:include type="message"
jdoc:include type="component"
```

这些是Joomla引入内容的方式，Joomla模板引擎会解析这些语句，抓取对应的内容渲染到模板中，组成一个页面。type指明要包含的内容的类型：



```
head        # 页面头文件（包括css/javascript/meta标签），注意这里不是指网站内容的头部
modules     # 模块
message     # 提示消息
component   # 组件
```

从代码中也可以看出，页面里只有一个component，同时有许多个modules。事实上message也是一个module，只是是一个比较特殊的module。

以http://127.0.0.1:9999/index.php?option=com_content&amp;view=article&amp;id=7:article-en-gb&amp;catid=10&amp;lang=en&amp;Itemid=116为例从URL来分析模板内容的话，可以清晰的看出：在Joomla的URL中，重要的信息通常包含两部分：组件信息、菜单ID：



```
option=com_content  # 该页面内要使用的组件，后台对应到Components中，文件使用JOOMLAROOT components中的文件
view=article       # 组件内要使用的view
id=7               # view对应的ID
Itemid=116          # 该页面对应的菜单ID
```

所以上面URL的意思就是告诉Joomla：当前页面是要显示一个文章分类页面，分类ID是7，对应的菜单ID是116。

最后附一张图，帮助理解：

[![](https://p0.ssl.qhimg.com/t012315aa242a0e1fca.png)](https://p0.ssl.qhimg.com/t012315aa242a0e1fca.png)

<br>

**0x02 整体大致运行流程**

**1. 框架核心代码的初始化**

/includes/defines.php定义各个功能模块的目录

/includes/framework.php整个框架调度的核心代码与cms运行的核心代码，框架初始化的入口。

/libraries/import.legacy.php开启自动加载类，并向注册队列注册cms核心类。

调用了JLoader中的setup方法；spl_autoload_register使其进行类的初始定义。

spl_autoload_register()是PHP自带的系统函数，其主要完成的功能就是注册给定的函数作为__autoload的实现。即将函数注册到SPL__autoload函数队列中。如果该队列尚未激活，则激活它们。

/libraries/loader.php定义了JLoader实现类的注册，加载，相关文件的包含等操作。

其中load方法从注册队列中寻找需要被自动加载的类，并包含该注册队列的值。

_autoload方法从注册队列中的prefixes的J中选取需要加载的类目录的前缀。[0]=&gt;/joomla/libraries/joomla，[1]=&gt;/joomla/libraries/legacy

_load方法完成了绝对路径的拼接，及相关文件的包含

/cms.php将PHP Composer生成的加载器autoload_static.php、/autoload_namespaces.php、/autoload_psr4.php、/autoload_classmap.php中的内容全部导入一个$loader的数组，之后将该数组中的前缀及所有类，注册到注册队列中，以方便使用。而这些类，都是针对于cms本身的操作的。接着开始设置异常处理以及一个消息处理器（日志）。最后，将一些注册类的名字规范为autoloader的规则。

configuration.php配置项

之后设置报错的格式

最终的注册队列：

[![](https://p4.ssl.qhimg.com/t011919fe74c7624a9a.png)](https://p4.ssl.qhimg.com/t011919fe74c7624a9a.png)

**2. 设置分析器，记下使用方法并在分析器后加标记对应代码**

对应代码：

```
JDEBUG ? JProfiler::getInstance('Application')-&gt;setStart($startTime, $startMem)-&gt;mark('afterLoad') : null;
```

**3. 实例化应用程序**

对应代码：

```
$app = JFactory::getApplication('site');
```

在这边可能会有疑问，为什么会直接实例化一个之前没有引入的类（同样也没有包含相应的文件）。

还记得我们之前看到过的自动加载类么，在这里，我们首先发现没有在classmap中寻找到，之后在/libraries目录，以/libraries/cms/目录为查找目录，在该目录查找是否存在factory.php文件，若找到，则将该文件包含进来。

在factory.php中，会首先检查我们是否已经创建了一个JApplicationCms对象，如果未创建该对象，则创建该对象。最后创建为JApplicationSite，并将这个对象实例化（对象位于/libraries/cms/application/site.php）。

在该文件中，首先注册了application（这边是site）的名称与ID，之后执行父构造函数和“祖父“构造函数。

为了清晰的说明Joomla web应用的实例化过程，我们列一个树状图来看



```
|-web.php “祖父”
|--cms.php 父
|---site.php 子
web.php
```

完成了应用的最基础功能，包括：

返回对全局JApplicationWeb对象的引用，仅在不存在的情况下创建它

初始化应用程序

运行应用程序

对模板的渲染（文档缓冲区推入模板的过程占位符，从文档中检索数据并将其推入应用程序响应缓冲区。）

检查浏览器的接受编码，并尽可能的将发送给客户端的数据进行压缩。

将应用程序响应发送给客户端

URL的重定向

应用程序配置对象的加载

设置/获取响应的可缓存状态

设置响应头的获取、发送与设置等基本功能

首先在web.php中实例化了JInput对象。并将config指向JoomlaRegistryRegistry。接着，创建了一个应用程序程序的网络客户端，用于进行网络请求的操作。同时将已经指向的config导入，设置执行时间，初始化请求对象，并配置系统的URIs。

在cms.php中实例化了调度器，主要完成对于组件及模块的调度。并对session进行设置和初始化。

完成了以上所有的配置后，将已经配置完毕的应用对象返回到/joomla/libraries/joomla/factory.php中。完成应用对象的初始化。

**4. 执行应用**

调用web.php中的execute()方法完成应用的执行。

<br>

**0x03 说一下我们的关心的路由问题**

那么，我们的路由在框架中到底是怎样解析的呢？

其实在跟实例化应用的时候，当执行/joomla/libraries/joomla/application/web.php构造函数时，我们就可以看到Joomla对于URI的处理了：

```
$this-&gt;loadSystemUris();
```

跟进看一下loadSystemUris方法，不难看到这一句：

[![](https://p0.ssl.qhimg.com/t015736eb74136cf81d.png)](https://p0.ssl.qhimg.com/t015736eb74136cf81d.png)

跟进detectRequestUri，发现首先判断了URI是否是http还是https，之后看到这句：



```
if (!empty($_SERVER['PHP_SELF']) &amp;&amp; !empty($_SERVER['REQUEST_URI']))
        `{`
            // The URI is built from the HTTP_HOST and REQUEST_URI environment variables in an Apache environment.
            $uri = $scheme . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];
        `}`
```

就是在这里将$_SERVER['REQUEST_URI']中的相对路径与$scheme . $_SERVER['HTTP_HOST']拼接成了完整的URI：

[![](https://p2.ssl.qhimg.com/t013a7a4c6f76579d5d.png)](https://p2.ssl.qhimg.com/t013a7a4c6f76579d5d.png)

完成了完整路径获取后，开始修改对象的属性，将新获得的request.uri添加进入配置列表中：

[![](https://p3.ssl.qhimg.com/t01c8bb442c479947c2.png)](https://p3.ssl.qhimg.com/t01c8bb442c479947c2.png)

下一步，就是遍历配置列表，查看是否已经设置了显示URI，在配置列表中键值为site_uri。显然我们现在并没有设置该选项：

[![](https://p4.ssl.qhimg.com/t01a74b2c5c2de6ead9.png)](https://p4.ssl.qhimg.com/t01a74b2c5c2de6ead9.png)

之后完成的操作就是要设置该显示URI。我们继续跟进一下：

[![](https://p0.ssl.qhimg.com/t01b24f03c25798e2b0.png)](https://p0.ssl.qhimg.com/t01b24f03c25798e2b0.png)

跟进到joomla/libraries/vendor/joomla/uri/src/UriHelper.php的时候，我们稍停一下，看到进入了parse_url方法中。在这个方法中，首先对传入的URL进行了双重过滤，之后利用PHP自带方法parse_url，对URL进行了分割处理并保存到一个数组中，接着返回该数组：

[![](https://p0.ssl.qhimg.com/t016e63ad4cc459e708.png)](https://p0.ssl.qhimg.com/t016e63ad4cc459e708.png)

[![](https://p2.ssl.qhimg.com/t0135e315b6fa96e7ed.png)](https://p2.ssl.qhimg.com/t0135e315b6fa96e7ed.png)

最后的处理结果为：

```
option=com_content&amp;view=article&amp;id=7:article-en-gb&amp;catid=10&amp;lang=en&amp;Itemid=116
```

处理完我们的显示URL后，在调用joomla/libraries/cms/application/cms.php中的execute方法时，在调用doExecute方法的时候，会使用joomla/libraries/cms/application/site.php文件中的route方法，这个方法将路由到我们application中。

在joomla/libraries/cms/application/cms.php中的route方法中，我们首先获取了全部的request URI，之后在getRouter方法中初始化并实例化了joomla/libraries/cms/router/router.php中的JRouter类，该类完成了对我们路由参数的识别与划分：

[![](https://p2.ssl.qhimg.com/t017c0acede56cc006a.png)](https://p2.ssl.qhimg.com/t017c0acede56cc006a.png)

最后在joomla/libraries/cms/router/site.php中的parse方法中完成了相关组件的路由：

[![](https://p2.ssl.qhimg.com/t01b56a0de9c2016424.png)](https://p2.ssl.qhimg.com/t01b56a0de9c2016424.png)

可以明显的看到，在

```
$component = $this-&gt;JComponentHelper::getComponents()
```

后，$component的值：

[![](https://p2.ssl.qhimg.com/t011fdec15b24a0da77.png)](https://p2.ssl.qhimg.com/t011fdec15b24a0da77.png)

对比components/目录下的组件，发现已经将所有的组件遍历，并保存在数组中。

接着遍历该数组，对每个组件设置本地路由，并包含响应的文件，从而完成路由控制。

[![](https://p1.ssl.qhimg.com/t01a367b1162dfe5570.png)](https://p1.ssl.qhimg.com/t01a367b1162dfe5570.png)

<br>

**0x04 总结一下**

Joomla整体的运行思路可以简单的归结为一下几点：

**框架核心代码的初始化：**

关键是初始化了类自动加载器与消息处理器，并完成了配置文件的配置与导入。

完成了这一步，就可以通过类的自动加载器来实现核心类的查找与调用。自动加载器成为了cms的一个工具。

**实例化应用程序：**

这一步可以简单的理解为对Joomla接下来要提供的web服务的预加，与定义。

**应用的执行：**

这一步基于上面两步的准备，将执行应用。从代码上来看可以容易的总结出来一个规律：

预加载“执行之前需要做的事件”

执行应用

执行“执行之后要做的事件”

基本上都是以这样的形式来完成调用以及运行的。

以上都是小菜个人看法，可能有不准确或者非常模糊的地方，希望大牛们多给建议…
