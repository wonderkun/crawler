> 原文链接: https://www.anquanke.com//post/id/85209 


# 【技术分享】Burp Suite扩展开发之Shodan扫描器（已开源）


                                阅读量   
                                **163056**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：resources.infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/writing-burp-extensions-shodan-scanner/](http://resources.infosecinstitute.com/writing-burp-extensions-shodan-scanner/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t01a209ceaf6f0d1555.png)](https://p1.ssl.qhimg.com/t01a209ceaf6f0d1555.png)**

****

**翻译：**[**scriptkid******](http://bobao.360.cn/member/contribute?uid=2529059652)

**预估稿费：130RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿**



**前言**

我们将在本文中探讨Burp扩展的编写，在最后，我们将完成一款通过shodan API对任意HTTP请求中的域名进行对应IP地址查询以及获取特殊信息的扩展。

我将本文分为以下几个层次，因此你可以跳过已经了解的部分：

1. Burp扩展接口介绍

2. 环境配置

3. 利用Shodan API编写简单的端口扫描

4. 参考来源

<br>

**Burp扩展接口介绍**

编写Burp扩展的原理围绕着对基础的OOPS概念以及对编程语言的一点点熟悉。Brup提供了大量与其开放接口进行交互的方式，同时提供了许多内置扩展功能，比如Target,Repeater,Scanner等。在此，我们将探究那些接口以及我们如何利用他们来编写我们的第一个扩展。

在本文中，我们将主要用到以下接口：



```
IBurpExtender
IContextMenuFactory
```



除了上述接口，我们还需要用到以下java库：

```
Javax.swing
```

**IBurpExtender**

如所有Burp文档提到的，所有扩展都必须声明该接口。原因很简单，为了创建我们的扩展，我们必须首先对其进行注册。这由扩展registerExtenderCallbacks来实现。其提供了一系列由IBurpExtenderCallbacks 接口实现的功能。

**IContextMenuFactory**

该接口主要处理上下文数据，这有助于我们使用IContextMenuInvocation接口实现的一系列函数。这些函数可以用来取出活添加信息到burp提供的任何上下文中，也就是说，我们可以精确定义我们的上下文菜单应该出现在Burp的哪个位置。

**Javax.swing**

我们将使用java的swing库来创建GUI。

<br>

**环境配置**

我们本文的目标是创建一个名为“Scan with Shodan”的上下文菜单入口，当用户选择该选项时，我们的代码将从选择的请求中取出HTTP的host值，然后发送host对应的IP地址到Shodan API，最后展示出返回结果。

**获取Shodan API key**

为了获得Shodan API key，我们需要在[这里](https://account.shodan.io/login)注册一个账户，然后来到个人页并复制key，将key放置于后续部分中代理里的start_scan函数中。

**获取Jython独立Jar文件**

因为我们将通过python调用java库，我们需要一个能将python代码转换到java接口的转换器，这里我们使用Jython。在[这里](http://www.jython.org/downloads.html)下载Jython的jar文件。

**设置环境**

接下来我们就来配置我们的环境，这样当扩展完成时我们就可以直接加载了。步骤如下：

1. 打开Burp

2. 切到Extender&gt;option

3. 在Python Environment部分，选择下载好的Jython jar文件。

[![](https://p5.ssl.qhimg.com/t01bd49915169244911.png)](https://p5.ssl.qhimg.com/t01bd49915169244911.png)

### <br>

**利用Shodan API编写简单的端口扫描器**

接下来让我们从burp中import前面提到的一些重要的接口，然后通过重载registerExtenderCallbacks函数来注册我们的扩展。我们通过声明类变量self.callbacks来进一步获取IBurpExtenderCallbacks函数的实例。通过callback 实例中的“setExtensionName”可以设置扩展名，通过注册ContextMenuFactory可以创建上下文菜单以及期望的入口。

[![](https://p2.ssl.qhimg.com/t017776c6a89f1850ab.png)](https://p2.ssl.qhimg.com/t017776c6a89f1850ab.png)

接着我们通过重写IBurpContextMenuFactory接口提供的函数来创建上下文菜单。通过portswigger提供的文档，我们可以看到我们可以使用createMenuItems函数来实现，该函数最后返回一个JMenuItem列表。

[![](https://p0.ssl.qhimg.com/t010e24a55bc21b5700.png)](https://p0.ssl.qhimg.com/t010e24a55bc21b5700.png)

接下来我们通过重写函数来添加我们的项目名到菜单项列表中。JMeuItem要求诸如名字、图标等参数。这里我们只关注名字和响应动作。响应动作要求一个函数作为参数，并在菜单项被点击时调用该函数。这里我们用python的匿名函数来传递多个参数到函数中，然后返回到目前为止所添加的菜单项列表。

[![](https://p2.ssl.qhimg.com/t01191c4ac8acafa6be.png)](https://p2.ssl.qhimg.com/t01191c4ac8acafa6be.png)

接着我们分别添加startThreaded和start_scan两个函数。添加startThreaded函数的原因是，所有的鼠标点击事件都是异步的，因此当我们调用我们的扩展时，burp将会完全挂起直到调用事件完成。由于我们设计的任务需要一点时间来完成，因此我们需要将其设置为后台进程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d0a06491c56e9f91.png)

start_scan函数只是简单地获取调用实例，然后使用getSelectedMessages函数来从被调用的地方获取HTTP请求/响应对象。

[![](https://p5.ssl.qhimg.com/t01727cfe58a89441de.png)](https://p5.ssl.qhimg.com/t01727cfe58a89441de.png)

接着我们通过IHttpRequestResponse接口来检索HTTP服务对象并通过getHost函数来获取hostname。因为Shodan API需要IP地址来获取我们需要的信息，因此我们使用python socket模块中的gethostbyname函数来实现。我们通过使用python的urllib2模块来发起http请求并在响应中加载JSON数据。

<br>

**加载并执行Burp扩展的步骤**

1. 切到extender&gt;extensions&gt;add&gt;选择extension type&gt;选择扩展文件&gt;点击next

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bb17a793e9be272b.png)

2. 如果一切都如上述步骤正常完成，那你应该在extensions页面见到你的扩展被加载了

[![](https://p2.ssl.qhimg.com/t01ea1d929157a14332.png)](https://p2.ssl.qhimg.com/t01ea1d929157a14332.png)

3. 在proxy histroy中选择任意请求，然后点击之前创建的上下文菜单入口。

[![](https://p0.ssl.qhimg.com/t0177263078a0d13a7b.png)](https://p0.ssl.qhimg.com/t0177263078a0d13a7b.png)

现在你应该在extension输出页上看到结果。

[![](https://p1.ssl.qhimg.com/t01987b2a5e1257da5d.png)](https://p1.ssl.qhimg.com/t01987b2a5e1257da5d.png)

完整代码可以在[这里下载](https://github.com/hackzsd/BurpExtenderPractise)。

<br>

**参考来源**

[https://portswigger.net/burp/extender/api/index.html](https://portswigger.net/burp/extender/api/index.html)

[https://portswigger.net/burp/extender/](https://portswigger.net/burp/extender/)

[https://www.shodan.io/](https://www.shodan.io/)
