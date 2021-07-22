> 原文链接: https://www.anquanke.com//post/id/83403 


# AngularJS客户端模板注入


                                阅读量   
                                **206946**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://blog.portswigger.net/2016/01/xss-without-html-client-side-template.html](http://blog.portswigger.net/2016/01/xss-without-html-client-side-template.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0128ccabe35bd7817a.jpg)](https://p5.ssl.qhimg.com/t0128ccabe35bd7817a.jpg)

**摘要**

[AngularJS](https://angularjs.org/)是时下非常流行的一款JavaScript框架。研究人员发现，攻击者可以利用Angular模版注入来攻击大量使用了AngularJS框架的网站。相较于[服务器端的模版注入](http://blog.portswigger.net/2015/08/server-side-template-injection.html)，AngularJS客户端模版注入则显得更加的低调，如果攻击者将AngularJS客户端模版注入与Angular沙盒逃逸这两种技术方法结合使用，那么攻击者就可以对目标网站发动跨站脚本（XSS）攻击了。直到目前为止，还没有发现任何有关 1.3.1+以及1.4.0＋版本的Angular框架受到沙盒逃逸影响的信息公布出来。在这篇文章中，我们将对Angular模版注入的核心概念进行介绍，并且还会给大家演示一种能够影响所有Angular版本的新型沙箱逃逸技术。

**介绍**

AngularJS诞生于2009年，该框架由Misko Hevery 等人创建，之后被谷歌公司所收购。它是一款非常优秀的前端JS框架，目前已经被用于谷歌的多款产品当中。AngularJS有着诸多特性，最为核心的是：MVVM、模块化、自动化双向数据绑定、语义化标签、依赖注入等等。AngularJS是为了克服HTML在构建应用上的不足而设计的。HTML是一门很好的为静态文本展示设计的声明式语言，但要构建WEB应用的话它就显得乏力了。所以AngularJS使用了不同的方法，以尝试去补足HTML本身在构建应用方面的缺陷。AngularJS正在发展成为WEB应用中的一种端对端的解决方案，这意味着它不只是你的WEB应用中的一个小部分，还是一个完整的端对端的解决方案。

Angular模版可以在双花括号内包含类似JavaScript代码的[表达式](https://docs.angularjs.org/guide/expression)代码段。大家可以点击下列地址来了解其具体的工作机制：

[http://jsfiddle.net/2zs2yv7o/](http://jsfiddle.net/2zs2yv7o/)

例如，用户输入`{``{`1+1`}``}`，在Angular中这是一个求值表达式，在经过处理之后，系统会输出：2。

这也就意味着，只要可以注入双花括号，任何人都可以执行Angular语句。

Angular表达式本身并不会引起非常严重的影响，但是当我们配合沙箱逃逸技术一起使用时，我们就可以在目标主机中执行任意的JavaScript代码了，而这样一来，我们也就可以在破坏目标网站系统了。

下面给出的两个代码段显示了这一漏洞的关键部分。第一个代码段能够动态嵌入用户的输入信息，但是攻击者并不能利用这个来进行XSS攻击，因为这段代码在HTML代码中使用了html特殊字符来对用户的输入数据进行编码：



```
&lt;html&gt;
&lt;body&gt;
&lt;p&gt;
&lt;?php
$q = $_GET['q'];
echo htmlspecialchars($q,ENT_QUOTES);
?&gt;
&lt;/p&gt;
&lt;/body&gt;
&lt;/html&gt;
```

第二个代码段几乎与第一个代码段是完全相同的，但是导入Angular的操作意味着攻击者可以利用Angular表达式来进行任意代码注入，再配合使用沙箱逃逸技术，我们就可以对目标进行XSS跨站脚本攻击了。



```
&lt;html ng-app&gt;
&lt;head&gt;
&lt;script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.4.7/angular.js"&gt;&lt;/script&gt;
&lt;/head&gt;
&lt;body&gt;
&lt;p&gt;
&lt;?php
$q = $_GET['q'];
echo htmlspecialchars($q,ENT_QUOTES);?&gt;
&lt;/p&gt;   
&lt;/body&gt;
&lt;/html&gt;
```

请注意，你需要在代码头部的HTML标签中加入“ng-app”。通常情况下，Angular网站将会在html标签或者body标签中使用这一参数。

换而言之，如果某一页面使用了Angular模版进行开发，那么我们对其进行XSS攻击的过程也将变得非常的简单。幸运的是，我们已经找到了解决这一问题的方法。

**沙箱**

Angular框架有其自身的沙盒机制，目的就是保证整个框架中的各个组件能够负责相应的操作。如果我们要对目标用户进行攻击，那么首先我们就得打破这一沙盒机制，然后才能执行任意的JavaScript代码。

现在，我们使用Chrome浏览器打开angular.js文件，并在第13275行代码加入一个[中断点](https://developers.google.com/web/tools/javascript/breakpoints/add-breakpoints?hl=en)。在Chrome的调试窗口中，添加一个新的表达式“fnString”。浏览器将会把已转换的输出结果显示给我们。表达式1+1的转换结果为：



```
"use strict";
var fn = function(s, l, a, i) `{`
    return plus(1, 1);
`}`;
return fn;
```

所以，系统会对表达式进行解析和重写，然后Angular才会执行相应的语句。如果大家想了解相关函数的构造函数，请点击下列地址获取：

[http://jsfiddle.net/2zs2yv7o/1/](http://jsfiddle.net/2zs2yv7o/1/)

从这里开始，可能一切将变得更加有趣了。下列代码段显示的是重写后的输出结果：



```
"use strict";
var fn = function(s, l, a, i) `{`
    var v0, v1, v2, v3, v4 = l &amp;&amp; ('constructor' in l),
        v5;
    if (!(v4)) `{`
        if (s) `{`
            v3 = s.constructor;
        `}`
    `}` else `{`
        v3 = l.constructor;
    `}`
    ensureSafeObject(v3, text);
    if (v3 != null) `{`
        v2 = ensureSafeObject(v3.constructor, text);
    `}` else `{`
        v2 = undefined;
    `}`
    if (v2 != null) `{`
        ensureSafeFunction(v2, text);
        v5 = 'u00281u0029';
        ensureSafeObject(v3, text);
        v1 = ensureSafeObject(v3.constructor(ensureSafeObject('u00281u0029', text)), text);
    `}` else `{`
        v1 = undefined;
    `}`
    if (v1 != null) `{`
        ensureSafeFunction(v1, text);
        v0 = ensureSafeObject(v1(), text);
    `}` else `{`
        v0 = undefined;
    `}`
    return v0;
`}`;
return fn;
```

正如你所见到的那样，Angular会使用ensureSafeObject函数来依次对每一个对象进行检测。[ensureSafeObject函数](https://github.com/angular/angular.js/blob/v1.4.6/src/ng/parse.js#L60-L85)能够检测某一对象是否为一个函数的构造方法，窗口对象，DOM参数，或者对象构造方法。上述检测中只要有一个参数为真（true），系统将会挂起当前正在执行的语句，同时还会防止该语句访问全局变量。

除此之外，Angular还有一些其他可以进行安全检测的函数，例如[ensureSafeMemberName](https://github.com/angular/angular.js/blob/v1.4.6/src/ng/parse.js#L40-L58)和[ensureSafeFunction](https://github.com/angular/angular.js/blob/v1.4.6/src/ng/parse.js#L91-L103)。ensureSafeMemberName会对JavaScript文件的属性进行检测，并且确保其中不包含__proto__ etc。ensureSafeFunction会对函数的调用信息进行检测，以确保函数不会调用，应用，或者绑定函数构造方法。

**sanitizer崩溃**

Angular sanitizer使用JavaScript进行开发，它是Angular客户端的过滤器，它可以增强Angular框架的安全性能，并且允许在HTML代码中绑定名为ng-bing-html的属性，我们可以在这个属性中添加需要过滤的参数。

当我对Angular sanitizer进行检测时，我打算使用Angular语句来重写框架中原生的JavaScript函数。但问题就是Angular表达式既不支持函数声明，也不支持函数表达式，所以我无法重写框架中的功能函数。在思考片刻之后，我想到了String.fromCharCode。因为函数是由字符串构造方法调用的，而不是通过字符串调用的，函数中的“this”应该是字符串的构造方法。也许我可以找到fromCharCode函数的后门！

如何在无法创建函数的情况下，在fromCharCode函数中创建一个后门呢？

很简单：重用一个已有的函数！唯一的问题就是，如何才能控制fromCharCode函数每次调用的值呢？如果我们使用数组，那么我们就可以向字符串的构造方法提供一个伪造的数组。我们要做的就是提供一个长度值和一个数组第一个索引的相应参数。幸运的是，数组已经有长度参数了，因为在创建它时我们就将长度设定为1了。我们只需要为数组的第一个索引提供值。具体操作如下所示：



```
'a'.constructor.fromCharCode=[].join;
'a'.constructor[0]='u003ciframe onload=(/Backdoored/)u003e';
```

当String.formCharCode被调用时，你将会得到字符串

&lt;iframe onload=(/Backdoored/)&gt;。在Angular沙盒中，这种方法非常实用。如果大家想要了解更多详细信息，请点击下列地址获取：

[http://jsfiddle.net/2zs2yv7o/2/](http://jsfiddle.net/2zs2yv7o/2/)

我继续对Angular sanitizer的代码进行审查，但我找不到任何与String.fromCharcode有关的函数调用。然后我又对其他的原生函数进行了检查，并且找到了一个非常有趣的函数：charCodeAt。如果我可以重写这个值，那么它就可以在不被过滤的情况下注入函数之中了。但是，现在仍然有一个问题：这一次，“this”值将会是一个字符串，而不是字符串的构造方法。这也就意味着，我不能使用同样的方法来重写函数了，因为我无法对字符串的索引和长度进行修改，因为这不是一个可写的字符串。

然后，我打算使用[].concat；这个函数可以将字符串和参数等相关信息一起返回。如果你想要了解这一操作中的相关技术细节和输出信息，请点击下列地址获取：

[http://jsfiddle.net/2zs2yv7o/3/](http://jsfiddle.net/2zs2yv7o/3/) 

这样一来，我们就可以破解Angular Sanitizer了，因为现在我可以向其注入任意的恶意参数。sanitizer代码如下：



```
if (validAttrs[lkey] === true &amp;&amp; (uriAttrs[lkey] !== true || uriValidator(value, isImage))) `{`
  out(' ');
  out(key);
  out('="');
  out(encodeEntities(value));
  out('"');
`}`
encodeEntities函数代码如下：
function encodeEntities(value) `{`
  return value.
    replace(/&amp;/g, '&amp;').
    replace(SURROGATE_PAIR_REGEXP, function(value) `{`
      var hi = value.charCodeAt(0);
      var low = value.charCodeAt(1);
      return '&amp;#' + (((hi - 0xD800) * 0x400) + (low - 0xDC00) + 0x10000) + ';';
    `}`).
    replace(NON_ALPHANUMERIC_REGEXP, function(value) `{`
      return '&amp;#' + value.charCodeAt(0) + ';';
    `}`).
  replace(/&amp;lt;/g, '&amp;lt;').
  replace(/&amp;gt;/g, '&amp;gt;');
`}`
```

**沙箱逃逸**

我对Angular的源代码进行了检测，并且在我寻找String.fromCharCode函数调用的过程中，我发现了一个非常有趣的实例。具体信息可以从下列地址中获取：

[http://jsfiddle.net/2zs2yv7o/4/](http://jsfiddle.net/2zs2yv7o/4/)

由于篇幅有限，有关沙箱逃逸部分的技术信息请大家阅读原文获取。

**总结**

如果你正在使用Angular，那么你就得对花括号中的用户输入信息进行严格的处理，在阅读完这篇文章之后，你也知道了这类信息能够产生多大的影响。除此之外，你也应该避免服务器端对用户的输入数据进行完整的响应。其他大多数的JavaScript框架都会采取各种机制来避免这种危险，例如有的框架不支持在HTML文件中的任意位置执行语句。

谷歌公司肯定知道这个问题存在，但是我们并不知道他们就这个问题到底了解多少。在Angular文档的中，谷歌就明确表示建议开发人员不要在模版中动态嵌入用户的输入数据，但这也让人们误以为Angular的源代码中不存在任何的XSS漏洞。这个问题不只存在与客户端模版之中，Angular服务器端模版也会受到这个问题的影响。

我认为这个问题将会引起更广泛的关注，因为这个问题涉及到最新版本Angular框架的沙盒逃逸。所以，你现在应该考虑的是如何在你引入JavaScript文件的过程中，保证你网站的安全。
