> 原文链接: https://www.anquanke.com//post/id/213422 


# Google Search XSS漏洞分析


                                阅读量   
                                **165497**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者kinugawamasato，文章来源：kinugawamasato
                                <br>原文地址：[https://www.youtube.com/watch?v=lG7U3fuNw3A](https://www.youtube.com/watch?v=lG7U3fuNw3A)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t017b398ed3d23eaef9.png)](https://p2.ssl.qhimg.com/t017b398ed3d23eaef9.png)



前几天，在油管上看到一个Goolge Search XSS的视频，感觉还是非常震惊的。都9102年了，竟然还能在Google首页找到XSS？

开门见山，XSS的payload是`&lt;noscript&gt;&lt;p title="&lt;/noscript&gt;&lt;img src=x onerror=alert(1)&gt;"&gt;`。看似平平无奇的payload，究竟是如何导致XSS的呢？下面，我们就一起来康康。



## HTML Sanitization

为了防止XSS的发生，我们通常会对用户的输入进行sanitize（本意是消毒，净化。在此表示，对于用户输入中可能产生XSS的部分进行编码或过滤。既保证用户输入内容的完整性，同时也防止嵌入的JS脚本被执行）。目前，很多Web框架也能做到这些。但是，针对HTML的过滤，仍然存在一些问题。比如，在某些场景下，我们希望保留一些HTML标签。如下图的Gmail页面所示，b标签表示加粗，i标签表示倾斜。

[![](https://p0.ssl.qhimg.com/t01edd007173b25d4d3.png)](https://p0.ssl.qhimg.com/t01edd007173b25d4d3.png)

### <a class="reference-link" name="%E6%9C%8D%E5%8A%A1%E7%AB%AF%E8%A7%A3%E6%9E%90"></a>服务端解析

针对这种需要过滤掉XSS的同时，保留部分HTML标签的情况。有人可能会想到，我们可以在实现一个HTML Sanitizer在服务端过滤掉可能导致XSS的输入。然而，实现这样的Sanitizer绝非易事。

通过下面这个例子，来康康为何困难？

下面是两个不完整的HTML代码片段，看起来，这两段代码有着相似的结构，`div`和`script`都有结束标签（`&lt;/div&gt;`和`&lt;/script&gt;`），但同时结束标签又是另一个标签的属性（`title`）的值。

```
1. &lt;div&gt;&lt;script title="&lt;/div&gt;"&gt;
2. &lt;script&gt;&lt;div title="&lt;/script&gt;"&gt;
```

大家可以先思考一下，浏览器是如何解析他们的呢？

公布答案！

对于代码片段1，浏览器将其解析为一个`div`，内部包含一个`script`。并且自动补全了`&lt;head&gt;, &lt;body&gt;, &lt;html&gt;`等标签。

[![](https://p5.ssl.qhimg.com/t0106b65c67c7a7a901.png)](https://p5.ssl.qhimg.com/t0106b65c67c7a7a901.png)

看起来挺合理的。浏览器的解析顺序如下：

1.发现`div`开始标签。<br>
2.发现`script`开始标签。<br>
3.`script`标签内部有一个`title`属性，内容是`&lt;/div&gt;`。其实，这里的值是什么都无所谓，浏览器都会把它看做一个字符串，并作为`title`的值。<br>
4.自动补全`script`结束标签。<br>
5.自动补全`div`结束标签。

对于代码片段2，浏览器的解析则完全不同。

[![](https://p3.ssl.qhimg.com/t01930ea39e2e265711.png)](https://p3.ssl.qhimg.com/t01930ea39e2e265711.png)

浏览器使用`title`属性里的`&lt;/script&gt;`进行了闭合，并将`div title="`作为`script`标签的内容插入其中。`&lt;/script&gt;`后面的`"&gt;`则作为普通的字符串插入到了`&lt;body&gt;`元素中。

浏览器在解析`&lt;script&gt;`标签的内容时，使用了JS Parser而不是HTML Parser，其内容`&lt;div title="`被看作是JavaScript代码（当然，这段代码并不符合JavaScript语法规范）。

两段相同结构的HTML代码片段，却被解析成了完全不同的DOM结构。由此可见，浏览器解析HTML的规范非常复杂。而且，不同的浏览器在解析HTML的时候也可能存在不同的规范。所以，在服务器端实现一个HTML Sanitizer，并且兼容不同版本的不同浏览器对于HTML的解析规范是非常困难的。

### <a class="reference-link" name="%E5%AE%A2%E6%88%B7%E7%AB%AF%E8%A7%A3%E6%9E%90"></a>客户端解析

聪明如你，可能已经想到。既然如此，我们不如在客户端对HTML进行sanitize。利用浏览器本身的Parser来解析HTML，然后我们只需要对解析后的结果进行sanitize即可。

浏览器正好提供了`template`标签，可以用来解析HTML，而且在解析过程中不会触发JavaScript脚本执行。

下面，通过对比普通的`div`标签，来说明`template`标签是如何工作的。

在浏览器的Console中执行下面这段代码

```
// 创建一个div元素
div = document.createElement('div');
// &lt;img src=x onerror=alert(1) /&gt; 作为XSS payload插入div
div.innerHTML = "&lt;img src=x onerror=alert(1) /&gt;"
```

如下图所示，毫无疑问，alert弹窗产生。

[![](https://p0.ssl.qhimg.com/t01aa1676d005cb5b70.png)](https://p0.ssl.qhimg.com/t01aa1676d005cb5b70.png)

如果，我们将payload放到`template`元素中呢？

```
// 创建一个template元素
template = document.createElement('template');
// 将同样的payload插入template中
template.innerHTML = "&lt;img src=x onerror=alert(1) /&gt;"
```

没有alert弹窗产生。而且，我们能从`template`中拿到解析后的HTML，并进行sanitize。

```
// 查看解析后的HTML，结果为 &lt;img src="x" onerror="alert(1)"&gt;
template.content.children[0]
// sanitize HTML，删除可能导致XSS的危险属性 onerror
template.content.children[0].removeAttribute("onerror");
// 将安全的HTML插入最终需要渲染的DOM节点上
div.innerHTML = template.content.children[0];
```

[![](https://p5.ssl.qhimg.com/t0111f3936e3e80a062.png)](https://p5.ssl.qhimg.com/t0111f3936e3e80a062.png)

这样，我们就实现了通过浏览器的Parser来解析HTML，然后对解析后的HTML进行sanitize，以保证最终输出安全的HTML。而且，在解析过程中，浏览器也不会执行嵌入的JavaScript脚本。

看起来，似乎大功告成了？！

我们尝试用同样的方法来解析文章开头提供的XSS payload。

```
// 插入payload
template.innerHTML = '&lt;noscript&gt;&lt;p title="&lt;/noscript&gt;&lt;img src=x onerror=alert(1)&gt;"&gt;'
// 查看解析后的HTML
template.content.children[0]
// 返回的结果如下
&lt;noscript&gt;
  &lt;p title="&lt;/noscript&gt;&lt;img src=x onerror=alert(1)"&gt;&lt;/p&gt;
&lt;/noscript&gt;
```

[![](https://p1.ssl.qhimg.com/t01f747d7c19533a0c2.png)](https://p1.ssl.qhimg.com/t01f747d7c19533a0c2.png)

解析后的HTML看起来非常安全，能够执行XSS的`img`标签被解析成了`p`标签的`title`属性的值，以字符串的形式存在。

接下来，我们将这段”安全”的HTML插入到`div`中

```
div.innerHTML = template.innerHTML;
```

[![](https://p0.ssl.qhimg.com/t013cbcc49ccec944fb.png)](https://p0.ssl.qhimg.com/t013cbcc49ccec944fb.png)

竟然，弹窗了？！我们打印一下插入payload的`div`，看看究竟是个什么鬼？

```
div
// 返回的结果如下
&lt;div&gt;
  &lt;noscript&gt;&lt;p title="&lt;/noscript&gt;
    &lt;img src="x" onerror="alert(1)"&gt;
  ""&gt;"
    &lt;p&gt;&lt;/p&gt;
&lt;/div&gt;

```

[![](https://p3.ssl.qhimg.com/t012d6807f3188e091a.png)](https://p3.ssl.qhimg.com/t012d6807f3188e091a.png)

`&lt;/noscript&gt;`闭合了`noscript`标签，后面紧跟的`img`标签变成了一个合法的标签，而不再是`title`属性的值，从而导致了XSS的执行。

这就非常诡异了。同样是`noscript`标签，在`div`和`template`中为什么会出现差异呢？答案其实就在[HTML规范](https://www.w3.org/TR/2011/WD-html5-author-20110809/the-noscript-element.html)中。

> The `noscript` element [represents](http://www.w3.org/TR/2011/WD-html5-20110525/rendering.html#represents) nothing if [scripting is enabled](http://www.w3.org/TR/2011/WD-html5-20110525/webappapis.html#concept-n-script), and [represents](http://www.w3.org/TR/2011/WD-html5-20110525/rendering.html#represents) its children if [scripting is disabled](http://www.w3.org/TR/2011/WD-html5-20110525/webappapis.html#concept-n-noscript). It is used to present different markup to user agents that support scripting and those that don’t support scripting, by affecting how the document is parsed.

所以说，`noscript`在`允许JavaScript`和`禁止JavaScript`环境下的解析是不同的。普通的浏览器环境是允许JavaScript执行的，而`template`中是禁止JavaScript执行的。这也就解释了为什么对于`noscript`标签的解析会出现差异。



## Google Search XSS

其实，Google Search XSS产生的原因，和前文demo中所展示的类似。由于Google早已修复了此问题，无法亲自验证。下文中出现的部分图片来源于油管视频的截图。

我们改动一下payload，在XSS执行处设置断点。

```
&lt;noscript&gt;&lt;p title="&lt;/noscript&gt;&lt;img src=x onerror=debugger;&gt;"&gt;

```

断点后，通过查看调用栈发现，在某处执行了`a.innerHTML = b`。将`b`打印出来，内容为`&lt;noscript&gt;&lt;p title="&lt;/noscript&gt;&lt;img src=x onerror=debugger;alert(1);&gt;"&gt;&lt;/p&gt;&lt;/noscript&gt;`。依据前文中的经验，我们知道这段代码是有危害的。

[![](https://p2.ssl.qhimg.com/t01b00f64296d805bc8.png)](https://p2.ssl.qhimg.com/t01b00f64296d805bc8.png)

通过对比修复前和修复后的JavaScript文件，发现某处的`a.innerHTML`被修改为带有sanitizer的实现。看来问题就出在这里。

[![](https://p0.ssl.qhimg.com/t010fa0fda102ffa965.png)](https://p0.ssl.qhimg.com/t010fa0fda102ffa965.png)

同样，在`a = a.innerHTML`处添加断点，查看调用栈。发现Google的sanitizer也是采用了和前文中demo类似的方式，即`template`标签来解析HTML。

[![](https://p5.ssl.qhimg.com/t0199c0fa36958acae7.png)](https://p5.ssl.qhimg.com/t0199c0fa36958acae7.png)

Google使用的JavaScript Library叫做Google Closure。这是一个开源的JavaScript框架。我找到了[修复XSS的commit](https://github.com/google/closure-library/commit/c79ab48e8e962fee57e68739c00e16b9934c0ffa)，发现这个commit实际上对之前某个commit的rollback。

[![](https://p2.ssl.qhimg.com/t0135ffa60708148d8f.png)](https://p2.ssl.qhimg.com/t0135ffa60708148d8f.png)

然后找到之前[导致XSS的commit](https://github.com/google/closure-library/commit/16201e8c00b98aa4d46a2c6830006ed4608532f4)，发现正是这个commit删除了某些sanitize语句，并且直接使用了innerHTML。

[![](https://p0.ssl.qhimg.com/t01d27a17590f6d3f3c.png)](https://p0.ssl.qhimg.com/t01d27a17590f6d3f3c.png)

[![](https://p3.ssl.qhimg.com/t0168a12b5ab01e8c8f.png)](https://p3.ssl.qhimg.com/t0168a12b5ab01e8c8f.png)

这个commit是2018年9月26日提交的，Google在2019年2月22日rollback。也就是说这个问题在Google Closure里存在了长达5个月之久，而很多Google产品本身也在使用Google Closure。

因吹斯汀！！！



## 总结

1.Google在HTML sanitization时，使用了`template`。`template`是`JavaScript Disabled`环境。<br>
2.`noscript`标签在`JavaScript Enabled`和`JavaScript Disabled`环境中的解析不一致，给XSS创造了可能。<br>
3.Google本身有对输入进行额外的sanitization，但是，在某个修复其他问题的commit中被删掉了。

当前流行的Web框架对XSS防御的支持已经相当完善，XSS漏洞挖掘也变得越来越困难。但是，看完了这位的Google Search XSS漏洞之后，我才发现，挖不到XSS，本质上，菜是原罪！

参考：<br>
Youtube: [https://www.youtube.com/watch?v=lG7U3fuNw3A](https://www.youtube.com/watch?v=lG7U3fuNw3A)<br>
漏洞发现者Twitter：[https://twitter.com/kinugawamasato](https://twitter.com/kinugawamasato)
