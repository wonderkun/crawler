> 原文链接: https://www.anquanke.com//post/id/86737 


# 【木马分析】金融木马：银行木马软件Zeus Panda 的Webinjects分析（part 1）


                                阅读量   
                                **129140**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：cyber.wtf
                                <br>原文地址：[https://cyber.wtf/2017/02/03/zeus-panda-webinjects-a-case-study/](https://cyber.wtf/2017/02/03/zeus-panda-webinjects-a-case-study/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t017bfd536169c937ae.jpg)](https://p4.ssl.qhimg.com/t017bfd536169c937ae.jpg)



译者：[blueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**简介**

****

我们的母公司**G DATA**（歌德塔杀毒软件）拥有强大的恶意软件样本自动化处理的基础设施，以用来向AV客户提供最新的安全保护措施。在**G DATA** 高级恶意软件分析中，我们已经将这些自动化分析流程整合到我们自己的系统中了，以便向我们的银行客户提供欺诈检测的解决方案。

最近我们观察到感染**Zeus Panda**银行木马的用户越来越多，经过一周对**Zeus Panda**银行木马样本加密配置文件的分析，我们决定对解密后的配置文件进行详细的研究和分析。由于之前已经有[文章](https://www.proofpoint.com/us/threat-insight/post/panda-banker-new-banking-trojan-hits-the-market)对Zeus Panda银行木马的基本功能做了详细的分析，所以我们将集中精力分析该银行木马的**webinjects**文件(该文件中包含更多代码指令用来指明其攻击目标和如何进一步实施攻击操作)，通过对Webinjects的分析让我们发现了一些很有趣的事情，跟其他的恶意软件一样，webinject文件中的JavaScript代码使用了**混淆技术**以躲避安全软件的分析，混淆后的内容如下所示：



```
var _0x2f90 = ["", "x64x6Fx6Ex65", "x63x61x6Cx6Cx65x65", "x73x63x72x69x70x74", "x63x72x65x61x74x65x45x6Cx65x6Dx65x6Ex74", "x74x79x70x65", "x74x65x78x74x2Fx6Ax61x76x61x73x63x72x69x70x74", "x73x72x63", "x3Fx74x69x6Dx65x3D", "x61x70x70x65x6Ex64x43x68x69x6Cx64", "x68x65x61x64", "x67x65x74x45x6Cx65x6Dx65x6Ex74x73x42x79x54x61x67x4Ex61x6Dx65", "x76x65x72", "x46x46", "x61x64x64x45x76x65x6Ex74x4Cx69x73x74x65x6Ex65x72", "x44x4Fx4Dx43x6Fx6Ex74x65x6Ex74x4Cx6Fx61x64x65x64", "x72x65x61x64x79x53x74x61x74x65", "x63x6Fx6Dx70x6Cx65x74x65", "x6Dx73x69x65x20x36", "x69x6Ex64x65x78x4Fx66", "x74x6Fx4Cx6Fx77x65x72x43x61x73x65", "x75x73x65x72x41x67x65x6Ex74", "x49x45x36", "x6Dx73x69x65x20x37", "x49x45x37", "x6Dx73x69x65x20x38", "x49x45x38", "x6Dx73x69x65x20x39", "x49x45x39", "x6Dx73x69x65x20x31x30", "x49x45x31x30", "x66x69x72x65x66x6Fx78", "x4Fx54x48x45x52", "x5Fx62x72x6Fx77x73x2Ex63x61x70", "x67x65x74x45x6Cx65x6Dx65x6Ex74x42x79x49x64", "x64x69x73x70x6Cx61x79", "x73x74x79x6Cx65", "x6Ex6Fx6Ex65", "x68x74x6Dx6C", "x70x6Fx73x69x74x69x6Fx6E", "x66x69x78x65x64", "x74x6Fx70", "x30x70x78", "x6Cx65x66x74", "x77x69x64x74x68", "x31x30x30x25", "x68x65x69x67x68x74", "x7Ax49x6Ex64x65x78", "x39x39x39x39x39x39", "x62x61x63x6Bx67x72x6Fx75x6Ex64", "x23x46x46x46x46x46x46"];
// ... further script code ...
```

解密这个脚本后，结果如下所示：



```
var vars = ["", "done", "callee", "script", "createElement", "type", "text/javascript", "src", "?time=", "appendChild", "head", "getElementsByTagName", "ver", "FF", "addEventListener", "DOMContentLoaded", "readyState", "complete", "msie 6", "indexOf", "toLowerCase", "userAgent", "IE6", "msie 7", "IE7", "msie 8", "IE8", "msie 9", "IE9", "msie 10", "IE10", "firefox", "OTHER", "_brows.cap", "getElementById", "display", "style", "none", "html", "position", "fixed", "top", "0px", "left", "width", "100%", "height", "zIndex", "999999", "background", "#FFFFFF"];
// ... further script code ...
```

仔细观察这个解密后的脚本，我们可以确定该恶意软件具有以下功能：

1. 首先检查浏览器版本，以添加针对某浏览器的特定事件侦听器（例如对于Firefox使用**DOMContentLoaded**事件）

2. 设置一些木马软件所需的参数变量，如：

a) botid：受害者系统的唯一标识符

b) inject：加载下一个攻击阶段的URL

3. 进一步加载并执行针对特定目标（银行）的JavaScript代码，如注入变量中定义的代码等。

事实证明，webinject初始阶段是用一个通用加载器从Web服务器下载针对特定目标的攻击代码。在这种情况下，“目标”是指银行和提供支付服务的提供商。这个推断可能需要进一步的分析，因为当前的webinjects会在多个阶段加载最终的攻击，或许这些webinjects中还包括更多的Zeus Panda组件。

**<br>**

**代码分析和示例展示**

****

在下载得到第二阶段的webinject后，我们对文件的实际大小感到很惊讶：**该文件的大小足足有91.8 KB**。简要分析之后我们发现该webinject包含了很多功能，一些功能是通用的，可以在每个网站上实施攻击操作，其他包括了一些针对具体目标的代码，如特定的HTML属性。例如，webinject使用唯一的id属性来标识目标网上银行的网站信息。在撰写本文时，我们仍在分析该webinject包含的大量功能。现在，我们将要对其基本功能做个简要的概述。

 [![](https://p4.ssl.qhimg.com/t012052303d35b0c4d6.png)](https://p4.ssl.qhimg.com/t012052303d35b0c4d6.png)

如上图所示，加载针对具体目标的JavaScript后，将调用图1所示的**init**函数。首先，该函数会检查是否位于页面顶部，如果没有，则调用**showpage()**函数，搜索标识符**_brows.cap**并删除此DOM元素（如果存在）。否则调用下一个检查函数**are()**，它搜索“登录”，“密码”和“按键”这三个字符串。如果没有找到这些字符串，则调用**get()**函数来检查当前用户是否处于登录状态。这是通过检查注销元素是否存在来完成的，只有当用户当前登录时才可用，如果没有，showpage()函数将被调用以完成清理操作。否则，status()函数用于将状态变量设置为字符串“CP”。之后收集的数据通过**send()**函数进行过滤。

如果恶意软件找到所有的目标字符串（“登录”，“密码”和“按键”），则会调用下一个函数**preventDefault()**和**stopPropagation()**（图1的左侧分支）。这将覆盖目标网站默认的表单操作，以收集用户在表单中输入的数据。另外，处理输入按钮的事件被hook，使得无论目标网站的提交方法是如何实现的，用户在表单中输入的数据都会被捕获。

由于此实现在Internet Explorer中不起作用，脚本将检查是否存在cancelBubble事件。如果存在，则调用针对Internet Explorer的特定代码，其提供与**stopPropagation()**函数相同的功能。

收集到用户在表单中输入的数据后，恶意软件会调用**status()**函数来设置分支变量。分支变量定义了一旦某个条件满足应该触发哪个动作。在我们的例子（左分支）中，该值被设置为字符串“SL”，该操作伪造假冒的网站，并提示用户该站点存在技术问题已不能再提供网络服务，下图展示了两种伪造站点的示例，图2是德语网站的伪造示例，图3是英语的伪造示例。

 [![](https://p0.ssl.qhimg.com/t01171c35ae07730605.png)](https://p0.ssl.qhimg.com/t01171c35ae07730605.png)

图2：德语网站的伪造

 [![](https://p1.ssl.qhimg.com/t018c48d9a60d332109.png)](https://p1.ssl.qhimg.com/t018c48d9a60d332109.png)

图3 英语网站的伪造

然后触发**send()**函数以发送收集到的用户数据。

<br>

**数据窃取**

****

这个攻击阶段另一个有趣的事情是代码中的“渗出”数据的函数，收集的用户信息被传递给send()函数，此函数将所有收集的数据作为HTTP GET的参数，并以HTTPS的方式发送到变量**link.gate**中定义的PHP服务器。根据我们的分析，针对不同的目标网站，send函数在传输数据的时候可能有不同的参数或者参数的结构有微小的差异。以下列表中列举出了我们目前为止标记到的参数，此列表并不完整，某些参数是可选的。所有参数都以纯文本格式发送到C&amp;C服务器端。

[![](https://p5.ssl.qhimg.com/t01484ea3151276eb5b.png)](https://p5.ssl.qhimg.com/t01484ea3151276eb5b.png)

我们打算在后续文章中对发送数据这部分内容做详细的分析，在下面的内容中我们将分析一下Zeus Panda木马软件的管理后台界面。

<br>

**详细的管理后台**

****

通过分析webinject代码，我们找到了C&amp;C服务器的后台管理地址。经过更仔细的分析，我们找到了我们正在调查的一个服务器的管理后台界面，如下图所示：

 [![](https://p1.ssl.qhimg.com/t0141d8b8587f049d95.png)](https://p1.ssl.qhimg.com/t0141d8b8587f049d95.png)

图4 木马软件管理后台

图4显示了木马软件管理员后台的初始画面，一行代表一个受害者的机器，每行包含以下信息：

1.BotId：受攻击系统的唯一标识符

2.活动模块类型

3.条目的工作状态

4.登录凭证（用户名/密码）

5.帐户状态

6.受害者IP地址

7.感染时间戳

8.浏览器版本

9.目标网址（银行）

顶部导航栏列出了一些可用的过滤器，如格式设置，放置区域和进一步的配置设置。

攻击者使用该面板查看新的受害者机器和可用的操作。通过点击条目，攻击者可以查看有关被入侵用户的详细信息。例如，可以显示诸如受害者的帐户余额，可用于转移的金额甚至交易限额的细节。

 [![](https://p2.ssl.qhimg.com/t0152c7372ed3a5125c.png)](https://p2.ssl.qhimg.com/t0152c7372ed3a5125c.png)

图5：管理员 – 面板详细视图

**结论**

****

银行木马仍然是网络犯罪分子最有价值的收入来源之一。鉴于这种恶意软件已经被开发和优化了很多年，恶意代码执行过程中遇到的任何错误都会发送到恶意软件作者那里，作者可以根据金融机构实施的任何新的防御措施进行相应的调整。注入的脚步也可以模仿用户的行为，增加填写表单和提交表单动作的延迟，使得其操作更加逼真，更有欺骗性。木马后台管理系统可以使攻击者将全部精力放到操控网络攻击上，而不需要知道详细的技术实现细节，在后续的博客文章中，我们将对webinject脚本攻击的其他功能进行详细的分析。

<br>

**Indicators of compromise(IOCs)**

****

[![](https://p0.ssl.qhimg.com/t014612fabf63c11a48.png)](https://p0.ssl.qhimg.com/t014612fabf63c11a48.png)


