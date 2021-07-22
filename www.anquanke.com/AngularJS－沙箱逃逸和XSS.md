> 原文链接: https://www.anquanke.com//post/id/83408 


# AngularJS－沙箱逃逸和XSS


                                阅读量   
                                **151081**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://spring.io/blog/2016/01/28/angularjs-escaping-the-expression-sandbox-for-xss](https://spring.io/blog/2016/01/28/angularjs-escaping-the-expression-sandbox-for-xss)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p3.ssl.qhimg.com/t0117ab2e0f38cf2885.png)](https://p3.ssl.qhimg.com/t0117ab2e0f38cf2885.png)

**更新信息：这篇文章是对《**[**AngularJS客户端模版注入**](http://bobao.360.cn/learning/detail/2597.html)**》一文的总结和归纳。之前所发表的文章引用了很多文献，而读者很难去搜集到这些相对零散的信息。所以我们将在这篇文章中给大家介绍这一漏洞的具体利用和修复方法。**

**介绍**

[AngularJS](https://angularjs.org/)诞生于2009年，该框架由Misko Hevery 等人创建，之后被谷歌公司所收购。它是一款非常优秀的前端JS框架，目前已经被用于谷歌的多款产品当中。AngularJS有着诸多特性，最为核心的是：MVVM、模块化、自动化双向数据绑定、语义化标签、依赖注入等等。AngularJS是为了克服HTML在构建应用上的不足而设计的。HTML是一门很好的为静态文本展示设计的声明式语言，但要构建WEB应用的话它就显得乏力了。所以AngularJS使用了不同的方法，以尝试去补足HTML本身在构建应用方面的缺陷。AngularJS正在发展成为WEB应用中的一种端对端的解决方案，这意味着它不只是你的WEB应用中的一个小部分，还是一个完整的端对端的解决方案。

这款当前非常流行的JavaScript框架允许开发人员在双花括号内嵌入[程序语句](https://code.angularjs.org/1.4.9/docs/guide/expression)。[比如说](https://code.angularjs.org/1.4.9/docs/guide/expression#example)，表达式1+2=`{``{`1+2`}``}`将会被Angular框架解析为1+2=3。

这也就意味着，用户可以在其输入的数据中嵌入双花括号，而当服务器对这类输入数据进行响应处理时，用户就可以利用这种Angular表达式来对目标主机进行XSS（跨站脚本攻击）攻击了。

服务器端的用户输入数据

现在，我们对一个使用了HTML编码来处理用户输入数据的页面进行分析。在我们下面所给出的例子中，我们使用了Thymeleaf模版来进行HTML编码，然后在页面的div标签中输出了属性username的信息。



```
&lt;html xmlns:th="http://www.thymeleaf.org"&gt;
&lt;head&gt;
&lt;title&gt;AngularJS - Escaping the Expression Sandbox&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
&lt;div th:text="$`{`username`}`"&gt;&lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;
```

如果属性username的值为&lt;script&gt;('Rob')&lt;/script&gt;，那么页面的输出信息应该与下面所给出的代码类似：



```
&lt;html xmlns:th="http://www.thymeleaf.org"&gt;
&lt;head&gt;
&lt;title&gt;AngularJS - Escaping the Expression Sandbox&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
&lt;div&gt;&amp;lt;script&amp;gt;('Rob')&amp;lt;/script&amp;gt;&lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;
```

也许你已经注意到了，页面的输出信息是经过HTML编码处理的。这也就意味着，就目前的情况而言，我们的程序是可以抵御跨站脚本攻击（XSS）的。

**引入AngularJS**

没错，从目前的情况来看，我们的程序的确可以抵御跨站脚本攻击（XSS）。那么接下来，我们就为程序引入AngularJS，看看引入这款框架之后程序会发生什么变化。



```
&lt;html xmlns:th="http://www.thymeleaf.org"&gt;
&lt;head&gt;
&lt;title&gt;Angular Expression - safe&lt;/title&gt;
&lt;script src="angular-1.4.8.min.js"&gt;&lt;/script&gt;
&lt;/head&gt;
&lt;body ng-app&gt;
&lt;div th:text="$`{`username`}`"&gt;&lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;
```

你将看到以下两点变化：

1.     我们将在页面中引入angular-1.4.8.min.js；

2.     我们将在body标签中添加属性ng-app；

现在，攻击者就可以对我们的程序进行跨站脚本攻击（XSS）了，但是具体的实现方法是什么呢？最有用的线索应该是Angular表达式了，而这一部分的内容我们之前就已经讲解过了，有疑问的同学可以再我们之前所发表的文章－《[AngularJS客户端模版注入](http://bobao.360.cn/learning/detail/2597.html)》中找到关于Angular表达式的信息。我们将属性username更改为1+2=`{``{`1+2`}``}`之后会发生什么呢？修改后的代码如下：



```
&lt;html&gt;
&lt;head&gt;
&lt;title&gt;Angular Expression - safe&lt;/title&gt;
&lt;script src="angular-1.4.8.min.js"&gt;&lt;/script&gt;
&lt;/head&gt;
&lt;body ng-app=""&gt;
&lt;div&gt;1+2=`{``{`1+2`}``}`&lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;
```

Angular框架将会更新DOM（Document Object Model，简称DOM，即文档对象模型。DOM是W3C组织推荐的处理可扩展标志语言的标准编程接口），解析之后的代码如下：



```
&lt;html&gt;
&lt;head&gt;
&lt;title&gt;Angular Expression - safe&lt;/title&gt;
&lt;script src="angular-1.4.8.min.js"&gt;&lt;/script&gt;
&lt;/head&gt;
&lt;body ng-app=""&gt;
&lt;div&gt;1+2=3&lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;
```

在得到了上面的处理结果之后，我们打算将属性username更改为`{``{`('Rob')`}``}`来看看会发生什么，但是Angular的[表达式沙箱](https://code.angularjs.org/1.4.9/docs/guide/security#expression-sandboxing)会阻止这种形式的程序语句执行。就目前的情况看来，也许你会认为我们现在仍然是安全的。但是，尽管Angular在其技术文档中提到了这一部分的安全保护机制，但是表达式沙箱并不是用来提供安全保障的。

更具体一点来说，Angular在其技术文档中提到了下列信息，其中包含[客户端模版和服务器端模版的相关信息](https://code.angularjs.org/1.4.9/docs/guide/security#mixing-client-side-and-server-side-templates)：

```
“一般而言，我们不推荐开发人员使用这一功能，因为它有可能给网站和服务器带来跨站脚本攻击的风险。”
```

在了解了这些信息之后，我们认为如果你允许服务器端模版对用户的输入数据进行解析处理，那么你的web程序将有可能受到跨站脚本攻击。现在，让我们来看一个更加具体的例子。

**表达式沙箱的逃逸技术**

如果我们的有效载荷处于Angular的表达式沙箱之中，我们怎么才能利用其中的XSS漏洞呢？

如果我们将username属性改成下面这样，会发生什么呢？



```
`{``{`
'a'.constructor.prototype.charAt=[].join;
eval('x=1) ) );(1)//');
`}``}`
```

在重写了Angular的原生函数“charAt”之后，我们就可以绕过Angular的表达式沙箱，而且还能够执行(1)。大家可以在我们之前所发表的《[AngularJS客户端模版注入](http://bobao.360.cn/learning/detail/2597.html)》一文中获取关于这一部分的详细内容。

请注意：这种攻击方法针对的是谷歌的Chrome浏览器和AngularJS 1.4.8。目前我们还没有发现针对其他浏览器的有效攻击方式。

**总结**

如果你的服务器能够对用户输入Angular模版中的信息进行响应处理，那么你将有可能受到XSS攻击。简而言之，不要在服务器端响应和处理用户的输入数据。你可以点击下面的地址来获取更多的示例。

**《AngularJS客户端模版注入》相关文章是:[http://bobao.360.cn/learning/detail/2597.html](http://bobao.360.cn/learning/detail/2597.html)**

[rwinch/angularjs-escaping-expression-sandbox](https://github.com/rwinch/angularjs-escaping-expression-sandbox)
