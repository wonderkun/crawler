> 原文链接: https://www.anquanke.com//post/id/85382 


# 【技术分享】JSONP注入实战指南


                                阅读量   
                                **199958**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securitycafe.ro
                                <br>原文地址：[https://securitycafe.ro/2017/01/18/practical-jsonp-injection/](https://securitycafe.ro/2017/01/18/practical-jsonp-injection/)

译文仅供参考，具体内容表达以及含义原文为准



**[![](https://p5.ssl.qhimg.com/t0153f707c3acaec94b.gif)](https://p5.ssl.qhimg.com/t0153f707c3acaec94b.gif)**

**翻译：**[**shan66**](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：200RMB**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

<br>

JSONP注入是一种鲜为人知却又相当普遍和危险的漏洞。JSONP是随着最近几年JSON、Web API的迅速崛起和对跨域通信的迫切需要而应运而生的。

<br>

**什么是JSONP？**

这里我们假设大家都已经了解JSON了，所以下面直接开始讨论JSONP。JSONP(JSON with Padding)是JSON的一种“使用模式”，可用于解决主流浏览器的跨域数据访问的问题。

让我们举个例子。 我们的网上银行应用程序，http://verysecurebank.ro，已实现一个API调用，可以用来返回当前用户的交易数据。

这样，通过向[http://verysecurebank.ro/getAccountTransactions](http://verysecurebank.ro/getAccountTransactions)  端点发送HTTP请求，我们就能得到JSON格式的交易数据： 

[![](https://p3.ssl.qhimg.com/t01a2f01a0a42660619.png)](https://p3.ssl.qhimg.com/t01a2f01a0a42660619.png)

如果我们的报表应用程序（[http://reports.verysecurebank.ro](http://reports.verysecurebank.ro)  ）希望获取交易的详细信息的话，由于同源策略（不同主机）的原因，所以是无法通过AJAX对该页面进行调用的。 

[![](https://p0.ssl.qhimg.com/t01d1c8e828b2adbcf3.png)](https://p0.ssl.qhimg.com/t01d1c8e828b2adbcf3.png)

为了解决这个问题，JSONP便应运而生了。 由于跨域脚本包含（主要用于加载JavaScript库，如jQuery，AngularJS等）是允许的，但不推荐，所以，我们可以这样来解决这个问题：在响应中预填回调函数。

需要注意的是，当跨域包含脚本时，脚本将在包含应用程序的上下文中运行，而不是在脚本的源上下文中运行。

通过为API响应添加一个回调函数，并封装JSON格式的数据，就允许我们加载脚本标签之间的API响应，并允许通过定义我们自己的回调函数来处理它的内容。 

<br>

**漏洞利用**

下面列出一些最常见的情形：

回调函数被硬编码到响应中

基本函数调用

对象方法调用

回调函数是动态的

通过URL（GET变量）可以实现完全控制

通过URL（GET变量）可以实现部分控制，但需要附加一个数字

通过URL（GET变量）可以实现控制，但最初不显示在请求中 

<br>

**基本函数调用**

一个非常常见的例子，就是将回调函数myCallback硬编码到响应的JSON格式的数据中：

[![](https://p3.ssl.qhimg.com/t012119fd28f4d7ad3b.png)](https://p3.ssl.qhimg.com/t012119fd28f4d7ad3b.png)

我们首先需要定义myCallback函数，然后在脚本标签中引用API调用就可以轻松利用这一点：

[![](https://p4.ssl.qhimg.com/t01452cc2b6d9f62523.png)](https://p4.ssl.qhimg.com/t01452cc2b6d9f62523.png)

注意：一定要在包含该响应之前定义这个函数，否则将会调用未定义的函数，导致无法获取任何数据。

当登录的受害者访问我们的恶意页面时，我们就能得到他的数据。 为了简洁起见，我们在当前页面中显示数据。 

[![](https://p1.ssl.qhimg.com/t01576d071f3e4eebac.png)](https://p1.ssl.qhimg.com/t01576d071f3e4eebac.png)

<br>

**对象方法调用**

这跟第一个例子几乎完全相同，并且您可能会在ASP或ASP.NET Web应用程序中遇到它。 在我们的示例中，System.TransactionData.Fetch作为回调函数添加到JSON格式的数据中：

[![](https://p4.ssl.qhimg.com/t01ab2b9560a31a19e9.png)](https://p4.ssl.qhimg.com/t01ab2b9560a31a19e9.png)

我们只需为TransactionData对象创建Fetch方法，该对象是System对象的一部分。

[![](https://p0.ssl.qhimg.com/t015c2f57e6c11b5ee5.png)](https://p0.ssl.qhimg.com/t015c2f57e6c11b5ee5.png)

由于结果都是一样的，所以从现在开始不再提供相关的截图。 

<br>

**通过URL（GET变量）实现完全控制**

这是最常见的情况：回调函数在URL中指定，并且我们可以完全控制它。 通过URL中的callback参数，我们可以修改回调函数的名称，因此我们将其设置为testing，并在响应中检查它的变化情况：

[![](https://p3.ssl.qhimg.com/t01971b396c1e80492d.png)](https://p3.ssl.qhimg.com/t01971b396c1e80492d.png)

我们基本上可以使用跟前面完全相同的漏洞利用代码，只是利用script标签包含响应时不要忘了添加参数callback。 

[![](https://p5.ssl.qhimg.com/t0106332e1b3b5b7b7d.png)](https://p5.ssl.qhimg.com/t0106332e1b3b5b7b7d.png)

<br>

**通过URL（GET变量）实现部分控制，但需要附加一个数字**

在这种情况下，回调函数名称需要附加一些东西，通常是一个数字。在大多数情况下，我们得到的东西类似于附加短数（如12345）的jQuery，例如回调函数名称将变成jQuery12345。

[![](https://p1.ssl.qhimg.com/t014527248f22131888.png)](https://p1.ssl.qhimg.com/t014527248f22131888.png)

逻辑上，漏洞利用代码保持不变，我们只需要将12345添加到我们的回调函数名称后面，而不是在包含脚本时添加。

[![](https://p2.ssl.qhimg.com/t0150a5d0b763d3c48b.png)](https://p2.ssl.qhimg.com/t0150a5d0b763d3c48b.png)

但如果数字不是硬编码怎么办？如果数字是动态的，并且对于每个会话都不相同，那怎么办呢？如果它是一个相对较短的数字，我们可以通过编程的方式来预定义每个可能的函数。我们假设附加的数字最大值为99.999。我们可以以编程方式创建所有这些函数，因为我们已经知道了回调函数的名称，所以只要附加相应的数字即可。下面给出了一个示例代码，这里使用了一个更简单的回调函数来演示结果：

[![](https://p2.ssl.qhimg.com/t016ce3f270a7d1b810.png)](https://p2.ssl.qhimg.com/t016ce3f270a7d1b810.png)

简单介绍一下代码：我们硬编码了一个回调函数，名为jQuery，我们为函数的数字设置了一个上限。在第一个循环中，我们在callbackNames数组中生成回调函数名。然后我们循环遍历数组，并将每个回调函数名称转换为全局函数。请注意，为了减少代码，我只提醒第一笔交易中发送的金额。让我们看看它是如何工作的：

[![](https://p3.ssl.qhimg.com/t01a372c4e3cde52cfe.png)](https://p3.ssl.qhimg.com/t01a372c4e3cde52cfe.png)

在我的机器上，花了大约5秒钟时间来显示警报，回调函数名称为jQuery12345。这意味着Chrome在5秒内创建了超过10.000个函数，所以我可以很大胆地说，这是一个非常可行的漏洞利用方法。 

通过URL（GET变量）可以实现控制，但最初不会显示在请求中

最后一个场景涉及一个API调用，由于它没有使用回调函数，因此没有可见的JSONP。当开发人员遗留下来的与其他软件的“隐式”向后兼容性，或在重构时没有删相关代码，那么就可能出现这种情况。因此，当看到没有回调函数的API调用时，特别是JSON格式的数据已经被放入括号之间时，可以手动添加回调函数到请求中。

如果我们有API调用[http://verysecurebank.ro/getAccountTransactions](http://verysecurebank.ro/getAccountTransactions)  ，就可以设法猜测回调变量：

[http://verysecurebank.ro/getAccountTransactions?callback=test](http://verysecurebank.ro/getAccountTransactions?callback=test) 

[http://verysecurebank.ro/getAccountTransactions?cb=test](http://verysecurebank.ro/getAccountTransactions?cb=test) 

[http://verysecurebank.ro/getAccountTransactions?jsonp=test](http://verysecurebank.ro/getAccountTransactions?jsonp=test) 

[http://verysecurebank.ro/getAccountTransactions?jsonpcallback=test](http://verysecurebank.ro/getAccountTransactions?jsonpcallback=test) 

[http://verysecurebank.ro/getAccountTransactions?jcb=test](http://verysecurebank.ro/getAccountTransactions?jcb=test) 

[http://verysecurebank.ro/getAccountTransactions?call=test](http://verysecurebank.ro/getAccountTransactions?call=test) 

虽然这些是最常见的回调函数名称，但是您还可以继续猜测其他名称。如果我们的回调函数名称被添加到了响应中，自然就能获取到一些数据。

<br>

**简单的数据采集技术**

到目前为止，我们只是在显示数据，下面开始介绍如何将数据发送回来。这是JSONP数据抓取的一个最简单的示例，您可以将其用于概念验证。

[![](https://p4.ssl.qhimg.com/t01ffbb05ac7b8d01dd.png)](https://p4.ssl.qhimg.com/t01ffbb05ac7b8d01dd.png)

我们使用data参数中的应用程序响应（交易数据）向我们的数据采集器发出GET请求。

注意：确保对数据使用了JSON.stringify()，因为它是一个对象，我们不希望在我们的文件中只有[object Object]。

注意：如果响应很大，请确保切换到POST，因为由于HTTP GET大小的限制，您可能无法接收完整的数据。

这里是我们的grabData.php代码，我们将接收到的数据追加到data.txt文件中： 

[![](https://p2.ssl.qhimg.com/t01a4aacdb9f681e389.png)](https://p2.ssl.qhimg.com/t01a4aacdb9f681e389.png)

<br>

**常见问题**

在寻找具有JSONP漏洞的Web应用程序时，我们可能会遇到一些问题。在这里，我们将介绍解决这些问题的方法。

**Content-Type和X-Content-Type-Options**

如果在API请求的响应头部中，X-Content-Type-Options设置为nosniff，则必须将Content-Type设置为JavaScript（text / javascript，application / javascript，text / ecmascript等）。这是因为通过在响应中包含回调函数的话，响应就不再是JSON，而是JavaScript。

如果您想知道自己的浏览器将哪些内容类型解释为JavaScript的话，请将浏览器导航至https://mathiasbynens.be/demo/javascript-mime-type。

在此示例中，Content-Type设置为application / json，X-Content-Type-Options设置为nosniff。

[![](https://p5.ssl.qhimg.com/t01911847b1384b1fa5.png)](https://p5.ssl.qhimg.com/t01911847b1384b1fa5.png)

最新版本的Google Chrome、Microsoft Edge和Internet Explorer 11可以成功阻止脚本执行。但是，Firefox 50.1.0（目前是最新版本）却没有这么做。

注意：如果X-Content-Type-Options：nosniff头部未设置的话，它将适用于所有上述浏览器。

注意：旧版本的浏览器没有进行严格的MIME类型检查，因为X-Content-Type-Options是最近才实现的。 

[![](https://p3.ssl.qhimg.com/t01ff1c4e5e5fcfa123.png)](https://p3.ssl.qhimg.com/t01ff1c4e5e5fcfa123.png)

<br>

**响应代码**

有时我们可能会得到200之外的一些响应代码。我对下列浏览器进行了相关的测试： 

Microsoft Edge 38.14393.0.0

Internet Explorer 11.0.38

Google Chrome 55.0.2883.87

Mozilla Firefox 50.1.0

下面将测试结果总结如下：



```
响应代码                相关浏览器 
100 Continue          Internet Explorer, Microsoft Edge, Google Chrome
101 Switching Protocols Google Chrome
301 Moved Permanently Google Chrome
302 Found             Google Chrome
304 Not Modified         Microsoft Edge
```

因此，即使我们没有得到200 HTTP代码，该漏洞仍然可以在其他浏览器中使用。

<br>

**绕过Referrer检查**

**1.使用数据URI方案**

如果有HTTP Referer检查，我们可以设法不发送它，以绕过验证。 我们怎么才能做到这一点内？引入数据URI。

我们可以滥用数据URI方案，以便在没有HTTP Referer的情况下发出请求。 因为我们要处理的是代码，其中包括引号、双引号和其他语法断开字符，所以我们需要对我们的payload（回调函数定义和脚本包含）进行base64编码。

下面是具体的语法：

```
data：text/plain; base64，our_base64_encoded_code
```

[![](https://p3.ssl.qhimg.com/t01a2d367f2bccab562.png)](https://p3.ssl.qhimg.com/t01a2d367f2bccab562.png)

以下是允许我们使用数据URI方案的三个主要HTML标签：

iframe（在src属性中）——它在Internet Explorer中不起作用

embed（在src属性中）——它在Internet Explorer和Microsoft Edge中不起作用

object（在data属性中）—— 它在Internet Explorer和Microsoft edge中不起作用

通过下图我们可以看到，API请求中没有发送HTTP Referer。 

[![](https://p4.ssl.qhimg.com/t018a3ffe3e68aeb7bf.png)](https://p4.ssl.qhimg.com/t018a3ffe3e68aeb7bf.png)

**2.从HTTPS页面发送HTTP请求**

如果我们的目标网站可以通过HTTP访问，我们还可以通过在HTTPS页面上托管我们的代码来避免发送HTTP Referer。如果我们从HTTPS页面发出HTTP请求，浏览器就不会发送Referer头部，以防止信息泄露。

我们要做的就是在启用HTTPS的网站上托管我们的恶意代码。

注意：由于混合内容安全机制的关系，这种方法不适用于启用了默认设置的现代Web浏览器。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016e1a36c23dfd2ee5.png)

但是，它在旧版本的浏览器中是可行的，并且不发送HTTP Referer头部，我们可以看到：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b49b4ae37e66e651.png)

<br>

**如何解决这个安全问题**

最后，让我们看看我们如何预防这种安全攻击的发生。最直接和最现代的方法是CORS（跨源资源共享）。

1.完全删除JSONP功能

2.请将Access-Control-Allow-Origin头部添加到API响应中

3.使用跨网域AJAX请求

因此，[http://reports.verysecurebank.ro](http://reports.verysecurebank.ro) 将以下跨网域AJAX请求嵌入到[http://verysecurebank.ro/getAccountTransactions](http://verysecurebank.ro/getAccountTransactions) ：

[![](https://p1.ssl.qhimg.com/t0179cd213811519824.png)](https://p1.ssl.qhimg.com/t0179cd213811519824.png)

API响应包括Access-Control-Allow-Origin：[http://reports.verysecurebank.ro：](http://reports.verysecurebank.ro%EF%BC%9A)

[![](https://p3.ssl.qhimg.com/t0166ef84a5dd82d950.png)](https://p3.ssl.qhimg.com/t0166ef84a5dd82d950.png)

我们将获得[http://verysecurebank.ro/getAccountTransactions](http://verysecurebank.ro/getAccountTransactions)  的内容： 

[![](https://p5.ssl.qhimg.com/t01922994f5c421edb7.png)](https://p5.ssl.qhimg.com/t01922994f5c421edb7.png)

<br>

**小结**

虽然JSONP的使用率在逐渐降低，但仍然有大量的网站还在使用或支持它。最后提醒一下，当处理JSONP时，别忘了顺便检查一下反射式文件下载和反射式跨站脚本漏洞。阅读愉快！ 
