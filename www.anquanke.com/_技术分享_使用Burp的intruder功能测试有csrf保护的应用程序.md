> 原文链接: https://www.anquanke.com//post/id/85289 


# 【技术分享】使用Burp的intruder功能测试有csrf保护的应用程序


                                阅读量   
                                **137294**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：nvisium.com
                                <br>原文地址：[https://nvisium.com/blog/2014/02/14/using-burp-intruder-to-test-csrf/](https://nvisium.com/blog/2014/02/14/using-burp-intruder-to-test-csrf/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01a6fd06521f3252e1.png)](https://p4.ssl.qhimg.com/t01a6fd06521f3252e1.png)



**作者：****王松_Striker &amp; Jess_喵******

**预估稿费：170RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**前言**

很多Web应用会有防止跨站请求伪造的策略，比如通过request请求传一个当前页面有效或者当前会话有效的参数（如果他们没有，那就很值得研究）。这些参数用来证明这个请求是从预定用户发出的，而不是攻击者那里。

这些参数，用来防止用户因为被劫持而发出伪造的请求。企业的安全顾问来评估这些参数，过程非常繁琐。传统的扫描器和其他自动化工具不能够准确的提交这些参数，也因此变得不那么理想。

这篇文章将展示如何使用Burp的intruder的Recursive Grep  payload功能来自动提交有csrf保护的token的方法。

<br>

**使用场景**

我们使用一个自己开发的程序来展示这个例子。这个程序是一个带有防御csrf的token的简单搜索表单。

我们的目的是通过这个搜索功能来查看是否有XSS漏洞。

当我们第一次加载这个页面，我们看到这个页面的源代码有一个hidden的输入框，name是csrf_token。每次刷新这个页面时，这个token都会改变。

[![](https://p0.ssl.qhimg.com/t01b88d2feb70c63676.jpg)](https://p0.ssl.qhimg.com/t01b88d2feb70c63676.jpg)

为了自动测试，我们需要一种在每次发送request请求时都能提交正确的csrf_token的方法。提交任何不匹配的数据都会导致报错或者在服务器端显示错误日志。

<br>

**Recursive Grep功能**

Burp工具提供了一个名叫recursive grep的payload，能够让你从攻击的前一个请求的返回包中提取出每个payload，我们可以利用这个功能从html中提取出csrf_token,重放到下一次请求中，以便进行自动化的fuzz攻击。

我们安装了一个burp的扩展，我们叫它xssValidator，用来自动测试xss漏洞。

我们可以使用burp的Recursive grep payload去提取csrf_token的值，结合使用xssvalidator payloads去自动发现应用中的有csrf保护的xss漏洞。



**操作示范**

像平时使用的一样，向intruder发送一个请求，定义这个你想要fuzz的插入点，定义了所有你需要的插入点后，找到http请求中发送csrf token的地方，然后也定义为一个payload。请记住这个payload的位置（position number），因为对于下一步来讲这很重要。

[![](https://p4.ssl.qhimg.com/t01283f90f57ac01d2b.jpg)](https://p4.ssl.qhimg.com/t01283f90f57ac01d2b.jpg)

定义了所有payload之后，我们需要设置攻击方式，这个例子中，我们使用pitchfork方式。

我们从给cookie头配置csrf_token参数这个payload开始，在这个例子中，它在第一个位置。定义这个payload的类型为Recursive grep，如下图：

[![](https://p5.ssl.qhimg.com/t01151d802ba09914b5.jpg)](https://p5.ssl.qhimg.com/t01151d802ba09914b5.jpg)

下一步，我们需要定义这个payload需要从http返回包中提取的参数的位置，切换到options tab，浏览 grep-extract面板。

[![](https://p1.ssl.qhimg.com/t013ed9a9a296930b06.jpg)](https://p1.ssl.qhimg.com/t013ed9a9a296930b06.jpg)

点击添加按钮，会展示出一个可以用来定义需要提取grep item的面板，有一些可选参数：用来定义开始和结束位置，或者使用正则来提取。这个例子中我们使用定义开始和结束位置的方法。

为了定义这个位置，只要简单的在http返回包中高亮选择这个区域即可。这个区域可以在header和body中。

[![](https://p1.ssl.qhimg.com/t01418537c89d4d7dfe.jpg)](https://p1.ssl.qhimg.com/t01418537c89d4d7dfe.jpg)

在高亮显示这个所需区域后，你可以看到这个态势和结束选择被自动填写了，点击OK，现在你可以在grep-extract面板看到一个条目。

[![](https://p0.ssl.qhimg.com/t01f27950520b384028.jpg)](https://p0.ssl.qhimg.com/t01f27950520b384028.jpg)

注意：burp默认的抓取长度是100个字符。在很多情况下太少了，别忘了配置一下。

Recursive grep payload 要求intruder 进行单线程攻击。以确保payload被正确重放，切换导航到request engine面板，设置线程为1。

[![](https://p0.ssl.qhimg.com/t017dd7929e1af73918.jpg)](https://p0.ssl.qhimg.com/t017dd7929e1af73918.jpg)

这个时候，我们需要完成配置这个payload。切换回payload tab，到Recursive grep payload设置。在payload选项中，你现在可以看到一个列表中有一个extract  grep  条目可以选择，确定这个被选择了。在这个例子中，你将看到我们提供了一个初始的payload值。很多时候，我们当测试csrf防御的应用时，第一次请求需要是一个有效的token，来确保不会由于发送非法token而触发任何反csrf的功能。

到这里我们已经完成了对Recursive grep payload的定义可以继续定义其他的payloads了。

例子中的应用有两个位置：search和csrf_token。我们试图注入搜索参数。这个csrf_token参数则是需要从其他地方获取的token。

我们测试这个应用的xss漏洞，因此我们安装了xssValidator扩展去测试position number 2.这个扩展需要利用外部phantomJs服务器通过burp intruder 准确的寻找xss漏洞。 欲了解更多信息，请访问我们的博客文章：使用BurpSuite和PhantomJS精确检测xss漏洞（[http://blog.nvisium.com/2014/01/accurate-xss-detection-with-burpsuite.html](http://blog.nvisium.com/2014/01/accurate-xss-detection-with-burpsuite.html)）。

在位置3 我们需要再次提供csrf_token。我们已经在位置1使用burp的Recursive grep获取了token，我们现在可以使用burp的copy other payload 去复制前一个payload定义的值。在我们的例子中，我们让payload的位置1和3有相同时值。

[![](https://p3.ssl.qhimg.com/t017544bf294ef35f76.jpg)](https://p3.ssl.qhimg.com/t017544bf294ef35f76.jpg)

<br>

**执行攻击**

现在我们定义了所有的payload，我们已经为发动这个攻击做好准备。来吧，快活吧~ 在执行过程中，你将会看到burp自动的从前一次的请求中获取csrf_tokenm并把它作为下一次请求的payload中的值。同样，你会注意到我们例子中使用的payload1和payload3具有相同的值。因为我们使用了burp的copy other payload的功能在多个位置传递csrf_token 。

[![](https://p3.ssl.qhimg.com/t015e991db84957050d.jpg)](https://p3.ssl.qhimg.com/t015e991db84957050d.jpg)

这个案例中，我们看到有一列名字是fy7sdu…，这列来自xssValidator扩展，当选中的时候，表示这里可能会有xss漏洞。

<br>

**总结**

我们已经证明，仅仅因为一个应用程序有防御csrf的 token, 视图对象或者其他相似的场景，并不意味着无法自动测试。Burp的recursive grep payload是对于测试web应用是非常有用的功能。

如果你想测试一个重定向的页面，定义extract grep item的面板目前不提供跟踪重定向，尽管设置了重定向选项。如果你手动添加这个值，intruder将会在执行payload的过程中按照期望跟踪重定向。PortSwigger发现了这个问题并将会推出相关的修复。

最后，如果你对示例的应用程序有兴趣，你可以访问github上的源代码：[https://github.com/mccabe615/sinny](https://github.com/mccabe615/sinny)。如果对代码不感兴趣，只是想测试，您可以免费使用我们部署的版本：[http://sleepy-tor-8086.herokuapp.com/](http://sleepy-tor-8086.herokuapp.com/)。

<br>

**参考文献**

 [1] [http://portswigger.net/burp/help/intruder_payloads_types.html#recursivegrep](http://portswigger.net/burp/help/intruder_payloads_types.html#recursivegrep)
