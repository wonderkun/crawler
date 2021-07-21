> 原文链接: https://www.anquanke.com//post/id/215233 


# 七夕—vBulletin 5.x RCE 的前世今生


                                阅读量   
                                **243094**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01bd16a11d74a4a307.png)](https://p0.ssl.qhimg.com/t01bd16a11d74a4a307.png)



8月10日，安全研究人员Amir Etemadieh披露了vBulletin 论坛的严重漏洞，该漏洞绕过了去年vBulletin 论坛 CVE-2019-16759漏洞补丁，能够实现远程命令执行。本文从环境搭建到漏洞调试，详细的分析漏洞产生的过程。



## 0x01 vBulletin简介

vBulletin是美国InternetBrands和vBulletinSolutions公司的一款基于PHP和MySQL的开源Web论坛程序，同时世界上用户非常广泛的PHP论坛，很多大型论坛都选择vBulletin作为自己的社区，因此此次漏洞危害重大。

此次漏洞使用范围vBulletin 5.5.4 ～ 5.6.2 。



## 0x02 调试环境搭建

### <a class="reference-link" name="0x1%20%E7%BD%91%E7%AB%99%E6%90%AD%E5%BB%BA"></a>0x1 网站搭建

vBulletin 代码不开源使得环境搭建异常复杂，之前的p8361/vbulletin-cve-2015-7808 docker 环境为vBulletin v5.1.5版本太老了，数据库中没有widget_tabbedcontainer_tab_panel模板，因此又在其他地方找到了符合漏洞版本的源代码。<br>
具体的搭建细节可以参照<br>[https://www.secshi.com/19016.html](https://www.secshi.com/19016.html)

[![](https://p1.ssl.qhimg.com/t011bde0c11df1d924f.png)](https://p1.ssl.qhimg.com/t011bde0c11df1d924f.png)

### <a class="reference-link" name="0x2%20xdebug%E5%AE%89%E8%A3%85"></a>0x2 xdebug安装

`apt install php-xdebug`<br>
并在apache2/php.ini配置文件中添加如下配置

```
;/etc/php/7.2/apache2/php.ini
[xdebug]
zend_extension="/usr/lib/php/20190902/xdebug.so"
xdebug.remote_enable=1
xdebug.remote_host = "127.0.0.1"
xdebug.idekey="PHPSTORM"
xdebug.remote_handler=dbgp
xdebug.remote_port=9000
```



## 0x03 vBulletin路由分析

由于CVE-2019-16759和 CVE-2020-17496 路由处理相同，我们在这主要分析vBulletin quickroute 部分的路由关系

### <a class="reference-link" name="0x1%20%E8%87%AA%E5%8A%A8%E5%8A%A0%E8%BD%BD"></a>0x1 自动加载

vBulletin 使用vB5_Autoloader实现类的自动加载。相关代码如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b5bf6d59aea6819a.png)

利用spl_autoload_register设置自动加载函数为_autoload，并设置好类搜索路径。将`self::$_paths` 中有的类加载到php中。类名和文件名的对应关系如下代码所示：

```
protected static function _autoload($class)
    `{`
        self::$_autoloadInfo[$class] = array(
            'loader' =&gt; 'frontend',
        );
        if (preg_match('/[^a-z0-9_]/i', $class))
        `{`return;`}`
        $fname = str_replace('_', '/', strtolower($class)) . '.php';
        foreach (self::$_paths AS $path)
        `{`
            if (file_exists($path . $fname))
            `{`
                include($path . $fname);

                self::$_autoloadInfo[$class]['filename'] = $path . $fname;
                self::$_autoloadInfo[$class]['loaded'] = true;
                break;
            `}`
        `}`
    `}`
```

### <a class="reference-link" name="0x2%20quick%E8%B7%AF%E7%94%B1%E6%A3%80%E6%B5%8B"></a>0x2 quick路由检测

这里是vBulletin QuickRoute检测分支，CVE-2019-16759和 CVE-2020-17496都是在此分支中触发。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a6ac8a95f112ed1b.png)

QuickRoute检测函数如下：

[![](https://p4.ssl.qhimg.com/t0187efcc1a6598fd15.png)](https://p4.ssl.qhimg.com/t0187efcc1a6598fd15.png)

主要检测了url中是否为下面开头：

```
ajax/api/options/fetchValues
filedata/fetch
external
ajax/apidetach
ajax/api
ajax/render
```

### <a class="reference-link" name="0x3%20%E8%B7%AF%E7%94%B1%E5%88%86%E5%8F%91"></a>0x3 路由分发

vB5_Frontend_ApplicationLight中的execute函数负责路由分发

[![](https://p4.ssl.qhimg.com/t015d52298b2c3878f0.jpg)](https://p4.ssl.qhimg.com/t015d52298b2c3878f0.jpg)

该函数将POST和GET参数整合了之后赋值给了`$serverData` ，在判断`application[handler]` 是否存在后利用`call_user_func` 调用分发，此时的调用函数为`callRender`。

进入`callRender`函数，该函数将路由路径切割成了路由参数。

[![](https://p4.ssl.qhimg.com/t01dab3a5636fd0a4a0.png)](https://p4.ssl.qhimg.com/t01dab3a5636fd0a4a0.png)

之后设置route信息，并由vB5_Template的staticRenderAjax函数统一处理。

调用处理函数<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0108f22e6fd75a6305.png)

### <a class="reference-link" name="0x4%20%E8%B7%AF%E7%94%B1%E5%A4%84%E7%90%86"></a>0x4 路由处理

最后由staticRenderAjax函数进行路由处理，由参数可以看出将render之后的参数取出，与需要渲染的参数一同传入该函数。

[![](https://p4.ssl.qhimg.com/t01f4b8d3b16b369321.png)](https://p4.ssl.qhimg.com/t01f4b8d3b16b369321.png)



## 0x04 漏洞分析

### <a class="reference-link" name="0x0%20%E6%A8%A1%E6%9D%BF%E6%B8%B2%E6%9F%93%E5%8A%9F%E8%83%BD"></a>0x0 模板渲染功能

<a class="reference-link" name="vB5_Template::staticRender"></a>**vB5_Template::staticRender**

进入到路由处理函数staticRenderAjax之后，又进入了staticRender函数

[![](https://p1.ssl.qhimg.com/t01f99d46aa496bf1ce.jpg)](https://p1.ssl.qhimg.com/t01f99d46aa496bf1ce.jpg)

在该函数中利用templateName当作参数创建vB5_Template对象

[![](https://p3.ssl.qhimg.com/t0113d54ce41e43e90d.jpg)](https://p3.ssl.qhimg.com/t0113d54ce41e43e90d.jpg)

同时将以下参数注册在template模板对象中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c706498676c72c4d.png)

注册新的自动加载路径，之后进入render函数

[![](https://p2.ssl.qhimg.com/t0129aeb1e178554432.jpg)](https://p2.ssl.qhimg.com/t0129aeb1e178554432.jpg)

**<a class="reference-link" name="vB5_Template-&gt;render"></a>vB5_Template-&gt;render**

在render函数的入口处存在一个变量覆盖，将传入的POST和GET参数可直接生成以key为名，以value为值的php变量。如下图所示：

[![](https://p2.ssl.qhimg.com/t012592aec5d2a5ae77.jpg)](https://p2.ssl.qhimg.com/t012592aec5d2a5ae77.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015c2ba94de6327e7f.png)

<a class="reference-link" name="%E6%A8%A1%E6%9D%BF%E8%8E%B7%E5%8F%96"></a>**模板获取**

再之后就是通过getTemplate 函数以及template 名称获取 template 内容

[![](https://p2.ssl.qhimg.com/t0189037326a0af3177.png)](https://p2.ssl.qhimg.com/t0189037326a0af3177.png)

不在缓存中的模板重新获取

[![](https://p1.ssl.qhimg.com/t01a60265823ea01908.png)](https://p1.ssl.qhimg.com/t01a60265823ea01908.png)

获取模板id号，并调用 Api_InterfaceAbstract

[![](https://p3.ssl.qhimg.com/t011ae52b6473e631a6.png)](https://p3.ssl.qhimg.com/t011ae52b6473e631a6.png)

通过一系列调用，到达 template.php:123, vB_Library_Template-&gt;fetchBulk()，并在其中利用sql查询将模板取出。

[![](https://p1.ssl.qhimg.com/t0100a975aed31e8e64.png)](https://p1.ssl.qhimg.com/t0100a975aed31e8e64.png)

对应从数据库中的取模板代码

[![](https://p2.ssl.qhimg.com/t010e85682664c06f82.jpg)](https://p2.ssl.qhimg.com/t010e85682664c06f82.jpg)

查询语句如下

[![](https://p0.ssl.qhimg.com/t01d2fc0e3995972b8a.jpg)](https://p0.ssl.qhimg.com/t01d2fc0e3995972b8a.jpg)

[![](https://p5.ssl.qhimg.com/t015e0b00c5ada3ab1b.jpg)](https://p5.ssl.qhimg.com/t015e0b00c5ada3ab1b.jpg)

执行渲染模板

[![](https://p4.ssl.qhimg.com/t010d9df4896fcfe500.png)](https://p4.ssl.qhimg.com/t010d9df4896fcfe500.png)

### <a class="reference-link" name="0x1%20CVE-2019-16759"></a>0x1 CVE-2019-16759

<a class="reference-link" name="payload"></a>**payload**

分析过模板渲染，该漏洞就一幕了然了，首先看下payload

```
POST /index.php HTTP/1.1
Host: 127.0.0.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 71
Connection: close

routestring=ajax/render/widget_php&amp;widgetConfig[code]=system('whoami');
```

<a class="reference-link" name="%E6%A8%A1%E6%9D%BF%E6%B8%B2%E6%9F%93%E6%BC%8F%E6%B4%9E"></a>**模板渲染漏洞**

该漏洞产生的原因为 widget_php 对应的模板中存在恶意代码执行漏洞，数据库中存储的templateid号为

[![](https://p0.ssl.qhimg.com/t016a09fe65f87557d4.png)](https://p0.ssl.qhimg.com/t016a09fe65f87557d4.png)

主要命令执行点为<br>`vB5_Template_Runtime::parseAction('bbcode', 'evalCode', $widgetConfig['code'])`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01454731d903103e26.jpg)

<a class="reference-link" name="%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E7%82%B9%E5%88%86%E6%9E%90"></a>**命令执行点分析**

vB5_Template_Runtime::parseAction 该函数虽然没有函数参数，但是解析了传递过来的所有参数到$arguments 变量由 vB5_Frontend_Controller_Bbcode类中的evalCode方法执行所有的参数

[![](https://p4.ssl.qhimg.com/t01d16544d25def2d80.png)](https://p4.ssl.qhimg.com/t01d16544d25def2d80.png)

evalCode方法如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a09c837e518e36e0.png)

### <a class="reference-link" name="0x2%20CVE-2020-17496"></a>0x2 CVE-2020-17496

结合前面模板渲染功能分析，可以很快的定位该漏洞。简要来说该漏洞通过二次渲染再次触发了CVE-2019-16759漏洞，具体分析如下。

<a class="reference-link" name="payload"></a>**payload**

```
POST /ajax/render/widget_tabbedcontainer_tab_panel?XDEBUG_SESSION_START=phpstorm HTTP/1.1
Host: localhost
User-Agent: curl/7.54.0
Accept: */*
Content-Length: 100
Content-Type: application/x-www-form-urlencoded

subWidgets[0][template]=widget_php&amp;subWidgets[0][config][code]=echo shell_exec("pwd"); exit;

```

<a class="reference-link" name="%E7%AC%AC%E4%B8%80%E6%AC%A1%E6%B8%B2%E6%9F%93"></a>**第一次渲染**

通过分析该代码得到在eval渲染过模板之后，会调用`$templateCache-&gt;replacePlaceholders($final_rendered)` 该函数会实现第二次模板的获取和渲染，然而通过精心构造第二次渲染的内容，可以完美的触发之前的漏洞。

```
$templateCode = $templateCache-&gt;getTemplate($this-&gt;template);
        if(is_array($templateCode) AND !empty($templateCode['textonly']))
        `{`
            $final_rendered = $templateCode['placeholder'];
        `}`
        else if($templateCache-&gt;isTemplateText())
        `{`
            eval($templateCode);
        `}`
        else
        `{`
            if ($templateCode !== false)
            `{`
                include($templateCode);
            `}`
        `}`
        if ($config-&gt;render_debug)
        `{`
            restore_error_handler();
            restore_exception_handler();
        `}`
        if ($config-&gt;no_template_notices)
        `{`
            error_reporting($oldReporting);
        `}`
        // always replace placeholder for templates, as they are process by levels
        $templateCache-&gt;replacePlaceholders($final_rendered);
```

<a class="reference-link" name="%E7%AC%AC%E4%BA%8C%E6%AC%A1%E6%B8%B2%E6%9F%93"></a>**第二次渲染**

接着第一次渲染看，从当前代码中看出了如果 `$missing`非空，就会再次去调用fetchTemlate函数获取新的模板。

[![](https://p1.ssl.qhimg.com/t01f88528859138e8f6.jpg)](https://p1.ssl.qhimg.com/t01f88528859138e8f6.jpg)

array_diff 这个函数会把第一个数组参数中与其他参数不同的地方记录下来并返回，之后重新去查找并渲染该模板。更有趣的是这个重新加载的模板我们可控，代码如下

[![](https://p4.ssl.qhimg.com/t010da4e83c3d2ce7a8.png)](https://p4.ssl.qhimg.com/t010da4e83c3d2ce7a8.png)

下图为pending被注册的代码，其实该代码为第一次渲染出来的代码中的一部分，然后在第二次渲染时用到了第一次渲染时注册的变量。

[![](https://p3.ssl.qhimg.com/t012dcfb1a3938b015a.png)](https://p3.ssl.qhimg.com/t012dcfb1a3938b015a.png)

[![](https://p1.ssl.qhimg.com/t01e8ad09bebfe62e3a.jpg)](https://p1.ssl.qhimg.com/t01e8ad09bebfe62e3a.jpg)

<a class="reference-link" name="%E8%A7%A6%E5%8F%91%E6%BC%8F%E6%B4%9E"></a>**触发漏洞**

这之后其实跟CVE-2019-16759一毛一样了

[![](https://p1.ssl.qhimg.com/t01969bdd75581d8cde.jpg)](https://p1.ssl.qhimg.com/t01969bdd75581d8cde.jpg)



## 0x05 参考文献

相关源码上传到了github [https://github.com/ctlyz123/CVE-2020-17496](https://github.com/ctlyz123/CVE-2020-17496)

[http://foreversong.cn/archives/1415](http://foreversong.cn/archives/1415)<br>[https://www.seebug.org/vuldb/ssvid-98336](https://www.seebug.org/vuldb/ssvid-98336)<br>[https://xz.aliyun.com/t/6419](https://xz.aliyun.com/t/6419)
