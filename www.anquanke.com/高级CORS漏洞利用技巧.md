> 原文链接: https://www.anquanke.com//post/id/150458 


# 高级CORS漏洞利用技巧


                                阅读量   
                                **225280**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：sxcurity.pro
                                <br>原文地址：[https://www.sxcurity.pro/advanced-cors-techniques/](https://www.sxcurity.pro/advanced-cors-techniques/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0181477371ff5b9baa.jpg)](https://p1.ssl.qhimg.com/t0181477371ff5b9baa.jpg)

## 前言

我之前看过linussarud和bo9om对于Safari未能正确处理特殊字符的利用的研究：

[https://labs.detectify.com/2018/04/04/host-headers-safari/](https://labs.detectify.com/2018/04/04/host-headers-safari/) 

[https://lab.wallarm.com/the-good-the-bad-and-the-ugly-of-safari-in-client-side-attacks-56d0cb61275a](https://lab.wallarm.com/the-good-the-bad-and-the-ugly-of-safari-in-client-side-attacks-56d0cb61275a)

上述文章深入的剖析了safari在某些特殊的情况下会导致xss或者是cookie注入。希望本文能在这方面带给大家更多的思考和创造的空间。



## 简介

去年11月份，我写了一篇文章关于如何利用safari未能正确处理特殊字符实现绕过yahoo view同源配置。接下来的一段时间，我发现了有更多的技巧去绕过这些配置策略，在此我决定公开一些我使用的技巧。

在此假设你对于cors有些基础的了解，知道怎么去利用这些错误的配置。这里有一些文档你可以去了解相关知识：

[http://blog.portswigger.net/2016/10/exploiting-cors-misconfigurations-for.html](http://blog.portswigger.net/2016/10/exploiting-cors-misconfigurations-for.html)

[https://www.geekboy.ninja/blog/exploiting-misconfigured-cors-cross-origin-resource-sharing/](https://www.geekboy.ninja/blog/exploiting-misconfigured-cors-cross-origin-resource-sharing/)



## 背景知识：dns和浏览器

### 简介

域名系统就像是一个服务器的地址目录，它实现域名和ip之间的转换，使得互联网使用起来更方便。

当你尝试通过浏览器访问一个url时，dns完成了一次地址转换—&gt;初始化一个tcp链接—-&gt;服务器响应syn+ack—-&gt;浏览器发送http请求—-&gt;渲染响应内容。

DNS服务器会响应任意请求，这样你可以在子域名发送任意字符，只要有响应的dns记录就会响应。

例如：dig A “&lt;@$&amp;(#+_`^%~&gt;.withgoogle.com” @1.1.1.1 | grep -A 1 “ANSWER SECTION”

[![](https://p3.ssl.qhimg.com/t01915a3ddb942a74a5.png)](https://p3.ssl.qhimg.com/t01915a3ddb942a74a5.png)

### 浏览器

我们已经知道dns服务器会响应这些请求，那么浏览器会怎么处理呢？大部分浏览器在发出请求之前会校验域名的有效性，例如：

**Chrome**[![](https://p5.ssl.qhimg.com/t015ed8057b62a5401e.png)](https://p5.ssl.qhimg.com/t015ed8057b62a5401e.png)

**Firefox**[![](https://p3.ssl.qhimg.com/t013ad985c34e3e8119.png)](https://p3.ssl.qhimg.com/t013ad985c34e3e8119.png)

**Safari**

注意我说的是大部分浏览器会校验域名的有效性，而不是全部，safari就是个例，它并不会校验域名的有效性，而是直接发送请求：[![](https://p1.ssl.qhimg.com/t01033c622e34132f73.png)](https://p1.ssl.qhimg.com/t01033c622e34132f73.png)我们可以使用不同字符的任意组合，甚至是不可打印字符：

,&amp;'”;!$^*()+=`~-_=|`{``}`%

// non printable chars

%01-08,%0b,%0c,%0e,%0f,%10-%1f,%7f



## 深入cors配置

大部分cors配置都会包括一个可访问的白名单信息，这个白名单通常用正则表达式来实现。

例如1：^https?://(.*.)?xxe.sh$

目的：匹配到来自xxe.sh和任何子域名的访问

攻击者要想从这里获取数据就必须有一个相关域的xss漏洞。

例如2：^https?://.*.?xxe.sh$

目的：和例1一样，匹配来自xxe.sh和任何子域的请求，但这个正则有个问题，会造成漏洞，问题存在于：.*.?

由于.*.并不是整体,?只对.之后的符号有影响，因此xxe.sh之前可以有任意字符。这也意味着攻击者可以发送任意以xxe.sh结尾的请求，实现跨域。[![](https://p4.ssl.qhimg.com/t01d5c75707a8a5c73f.png)](https://p4.ssl.qhimg.com/t01d5c75707a8a5c73f.png)这是一个非常普通的绕过技术，这里有一个相关案例：h[ttps://hackerone.com/reports/168574](https://hackerone.com/reports/168574)

例如1：^https?://(.*.)?xxe.sh:?.*

目的：匹配到来自xxe.sh和任何子域名的访问

你能发现问题吗？

和第二个例子一样，？仅仅影响：。因此只要我们在xxe.sh后加上任意字符都能被接受。[![](https://p3.ssl.qhimg.com/t01b651bae50ff5ef67.png)](https://p3.ssl.qhimg.com/t01b651bae50ff5ef67.png)



## 关键性问题

怎么利用safari对于特殊字符的不当处理，实现对cors配置不当漏洞的利用呢？

假设以下是apache的配置文件：   [![](https://p2.ssl.qhimg.com/t01a2e65cf8e5c28fef.png)](https://p2.ssl.qhimg.com/t01a2e65cf8e5c28fef.png)目的也是为了接受xxe.sh和子域的访问。

这个案例并不像先前的几个例子能够通过一样的技巧绕过，除非有一个子域的xss，但让我们再思考一下。

我们知道在xxe.sh后的任意字符(. – a-z A-Z 0-9)都不会被信任，那如果是一个空格呢？[![](https://p0.ssl.qhimg.com/t011b22b447d201d015.png)](https://p0.ssl.qhimg.com/t011b22b447d201d015.png)

可以看到我们成功了，但这样一个域名任何浏览器都不会支持。

由于正则表达式仅仅匹配ascii字符还有. –，那任何特殊字符都是可以被接受的。[![](https://p3.ssl.qhimg.com/t016607cc8b92e96694.png)](https://p3.ssl.qhimg.com/t016607cc8b92e96694.png)

这样的域名就能被safari浏览器支持了。



## 漏洞利用

事先准备：1.将dns记录指向你的主机 2.nodejs

和大多数浏览器一样，Apache和nginx也不支持特殊字符，因此用nodejs实现比较容易。

Serve.js  [![](https://p1.ssl.qhimg.com/t012e005cafad4cf5d5.png)](https://p1.ssl.qhimg.com/t012e005cafad4cf5d5.png)

同一目录下的cors.html:[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0177d588df26169369.png)

通过nodejs执行如下命令：node serve.js &amp;

和之前描述的一样，由于正则匹配的是ascii和. –，在xxe.sh后的特殊字符是被信任的。如果我们打开safari，访问[http://x.xxe.sh`{`.&lt;your-domain&gt;/cors-poc](http://x.xxe.sh%7B.%3Cyour-domain%3E/cors-poc)，我们可以看到成功的获取到了数据：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c48e786cab276f8c.png)

令我注意的是不仅仅safari支持_，chrome和firefox也支持因此[http://x.xxe.sh_.&lt;your-domain&gt;/cors-poc](http://x.xxe.sh_.%3Cyour-domain%3E/cors-poc)能被大多数浏览器支持。



## 实践

当记住这些特殊字符后，找出哪些域名会受影响就只是时间问题了。为了节约时间，我写了一个fuzz，用来找出这些问题，这个fuzz可以在我的github上找到—— [https://github.com/sxcurity/theftfuzzer](https://github.com/sxcurity/theftfuzzer)

审核人：yiwang   编辑：边边
