> 原文链接: https://www.anquanke.com//post/id/156078 


# 围观orange大佬在Amazon内部协作系统上实现RCE


                                阅读量   
                                **228828**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者orange，文章来源：orange.tw
                                <br>原文地址：[http://blog.orange.tw/2018/08/how-i-chained-4-bugs-features-into-rce-on-amazon.html ](http://blog.orange.tw/2018/08/how-i-chained-4-bugs-features-into-rce-on-amazon.html%20)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t014ec4383f7516b469.jpg)](https://p5.ssl.qhimg.com/t014ec4383f7516b469.jpg)

（本文作者是orange，以其第一人称叙述。）<br>
这是我在Black Hat USA 2018和DEFCON 26上的案例研究，PPT可在这里下载：<br>
• [Breaking Parser Logic! Take Your Path Normalization Off and Pop 0days Out](http://i.blackhat.com/us-18/Wed-August-8/us-18-Orange-Tsai-Breaking-Parser-Logic-Take-Your-Path-Normalization-Off-And-Pop-0days-Out-2.pdf)<br>
这两年我一直在关注网络安全中的“不一致”的问题。什么叫做“不一致”的问题呢？ 打个比方，就像我去年在Black Hat展示的GitHub的由SSRF导致RCE案例中出现的， URL解析器和URL获取器之间的不一致导致整个SSRF绕过！<br>
这里还推荐一篇文章@ 0x09AL，[Bypassing Web-Application Firewalls by abusing SSL/TLS](https://0x09al.github.io/waf/bypass/ssl/2018/07/02/web-application-firewall-bypass.html) ，从中足以看出“不一致”问题的可怕。<br>
所以今年，我开始关注路径解析器和路径规范化中的“不一致”的问题！<br>
编写一款设计良好的解析器很难。因为不同的实体都有着不同的标准和实施方式。一般为了在不影响业务逻辑的情况下来修复错误，都会增加一个过滤器而不是直接给漏洞打补丁。那如果过滤器和被调用方法之间存在任何不一致，就可以轻松绕过安全机制！<br>
在阅读文档说明的时候，我注意到一个叫URL Path Parameter的功能。 一些研究人员早就指出过这个功能可能会导致安全问题，但是是说它仍然取决于编程是否有问题！ 画个思维导图，然后我发现这个功能可以完美地应用在多层体系结构上，而且是默认情况下就很容易受到攻击。如果你使用反向代理，并且是Java作为后端服务，那么就危险了！<br>
早先在2015年第一次发现这个攻击面是在一次红队测试中。我觉得这个问题很牛x，想看看有多少人知道，然后就在[WCTF 2016](http://ctf.360.com/2016/en/index.html)中出了一道相关的题目。<br>
不过后来事实证明，没人知道这个问题，因为没有参赛队伍做出这个题。<br>
今年我打算分享这个问题。为了说服审查委员会，我要更多的案例证明它有效！然而在寻找案列的过程中发现这个攻击面不仅可以泄漏信息，还可以绕过ACL（例如优步的OneLogin bypass），并在几个赏金计划中导致RCE。 这篇文章介绍的就是其中之一！<br>
（PPT里有以上的案例说明）<br>
↓多层架构的不一致性！[![](https://p4.ssl.qhimg.com/t01c34b2d871337f765.png)](https://p4.ssl.qhimg.com/t01c34b2d871337f765.png)



## 前言

首先，感谢亚马逊的漏洞披露计划。与亚马逊安全团队合作感觉特别好（当然Nuxeo团队也是）。

整个故事始于一个域名collaborate-corp.amazon.com，它貌似是一个内部协作系统。 从网页下面的copyright来看，这个系统是用一个开源项目Nuxeo构建的。 它是一个非常庞大的Java项目，起初我就想提高一下Java审计技能。所以就从它开始了。



## Bugs

我的个人习惯是拿到java源码之后先去看pom.xml,看看有没有引用一些过时的包什么的。在java漏洞里面很多问题都是OWASP Top 10 – A9上列的已知易受攻击的组件，比如Struts2，FastJSON，XStream或具有反序列化问题的组件等等。<br>
Nuxeo的包大部分都是最新的。不过还是有一个“老朋友”——Seam Framework。 Seam是JBoss开发的Web应用程序框架，几年前它是一个相当流行的Web框架，到现在仍有许多基于Seam的应用程序：P

### <a name="1.%E8%B7%AF%E5%BE%84%E8%A7%84%E8%8C%83%E5%8C%96%E9%94%99%E8%AF%AF%E5%AF%BC%E8%87%B4ACL%E7%BB%95%E8%BF%87"></a>1. 路径规范化错误导致ACL绕过

通过WEB-INF / web.xml查看访问控制时，我发现Nuxeo使用自定义的身份验证过滤器NuxeoAuthenticationFilter并映射/ *。 从过滤器来看大多数页面都需要身份验证，但是有一个白名单，例如login.jsp。这些都是在bypassAuth方法中实现的。[![](https://p2.ssl.qhimg.com/t01724522ee8feb8ed3.png)](https://p2.ssl.qhimg.com/t01724522ee8feb8ed3.png)从上面可以看出来，bypassAuth检索当前请求的页面，与unAuthenticatedURLPrefix进行比较。 但bypassAuth如何检索当前请求的页面？ Nuxeo编写了一个从HttpServletRequest.RequestURI中提取请求页面的方法，第一个问题出现在这里！[![](https://p4.ssl.qhimg.com/t01ba4fedbf746cce5c.png)](https://p4.ssl.qhimg.com/t01ba4fedbf746cce5c.png)为了处理URL路径参数，Nuxeo以分号截断所有尾随部分。 但是URL路径参数是多种多样的。 每个Web服务器都有自己的实现。 Nuxeo的方式在WildFly，JBoss和WebLogic等容器中可能是安全的。 但它在Tomcat下就不行了！ 因此getRequestedPage方法和Servlet容器之间的区别会导致安全问题！<br>
根据截断方式，我们可以伪造一个与ACL中的白名单匹配但是到达Servlet中未授权区域的请求！<br>
我们选择login.jsp作为前缀！ ACL绕过可能如下所示：[![](https://p2.ssl.qhimg.com/t01ecbc073416f063df.png)](https://p2.ssl.qhimg.com/t01ecbc073416f063df.png)

如图所示，绕过了重定向进行身份验证，不过大多数页面还是返回500错误。这是因为servlet逻辑无法获得有效的用户原则，因此它会抛出Java NullPointerException。 但这并不影响进一步操作。

附： 虽然有一个更快捷的方式来实现这个目的，不过还是值得写下第一次尝试！

### <a name="2.%E4%BB%A3%E7%A0%81%E9%87%8D%E7%94%A8%E5%8A%9F%E8%83%BD%E5%AF%BC%E8%87%B4%E9%83%A8%E5%88%86EL%E8%B0%83%E7%94%A8"></a>2. 代码重用功能导致部分EL调用

我之前也说到，Seam框架中有许多安全隐患。所以下一步我要做的就是回到第一个问题中去访问未经认证的Seam servlet！

这个部分我将逐一详细解释这些“功能”.<br>
为了控制浏览器应该重定向的位置，Seam引入了一系列HTTP参数，并且在这些HTTP参数中也存在问题… actionOutcome就是其中之一。 2013年，@meder发现了一个远程代码执行漏洞。见[CVE-2010-1871：JBoss Seam Framework remote code execution for details](http://blog.o0o.nu/2010/07/cve-2010-1871-jboss-seam-framework.html)！但今天，我们将讨论另一个 – actionMethod！

actionMethod是一个特殊的参数，可以从查询字符串中调用特定的JBoss EL（Expression Language）。这看起来相当危险，但在调用之前有一些先决条件。详细的实现可以在方法callAction中找到。为了调用EL，必须满足以下前提条件：<br>
1.actionMethod的值必须是一对，例如：FILENAME：EL_CODE<br>
2.FILENAME部分必须是context-root下的真实文件<br>
3.文件FILENAME必须包含内容“＃`{`EL_CODE`}`”（双引号是必需的）

例如：<br>
context-root下有一个名为login.xhtml的文件：<br>[![](https://p5.ssl.qhimg.com/t01d4190c3e705f6719.png)](//)

可以通过URL调用EL user.username<br>[![](https://p1.ssl.qhimg.com/t014352725f7038a581.png)](https://p1.ssl.qhimg.com/t014352725f7038a581.png)

### <a name="3.%E5%8F%8C%E9%87%8D%E8%AF%84%E4%BC%B0%E5%AF%BC%E8%87%B4EL%E6%B3%A8%E5%85%A5"></a>3. 双重评估导致EL注入

之前的功能看起来没啥毛病，你无法控制context-root下的任何文件，因此无法在远程服务器上调用任意EL。 然而，还有一个更疯狂的功能：<br>
如果返回一个字符串，并且该字符串看起来像一个EL就糟糕了， Seam框架将再次调用！<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a0f7abfee7e0700d.png)

请看更细节的调用堆栈信息

1.CallAction(Pages.java)<br>
2.handleOutcome(Pages.java)<br>
3.handleNavigation(SeamNavigationHandler.java)<br>
4.interpolateAndRedirect(FacesManager.java)<br>
5.interpolate(Interpolator.java)<br>
6.interpolateExpressions(Interpolator.java)<br>
7.createValueExpression(Expressions.java)

有了这个功能，如果我们可以控制返回值，我们可以执行任意EL！<br>
这与二进制利用中的ROP（Return-Oriented Programming）非常相似。 所以我们需要找到一个合适的工具！

这里我用的是 [widgets/suggest_add_new_directory_entry_iframe.xhtml](https://github.com/nuxeo/nuxeo/blob/master/nuxeo-features/nuxeo-platform-ui-select2/src/main/resources/web/nuxeo.war/widgets/suggest_add_new_directory_entry_iframe.xhtml#L19)

[![](https://p2.ssl.qhimg.com/t014ea2349d12b79840.png)](https://p2.ssl.qhimg.com/t014ea2349d12b79840.png)

为什么选用这个呢？这是因为request.getParameter返回一个我们可以从查询字符串控制的字符串！ 虽然整个标记是分配变量，但我们可以滥用语义！<br>
现在将第二阶段payload放在directoryNameForPopup中。 对于第一个bug，我们可以将它们链接在一起以执行任意EL而无需任何身份验证！ PoC：[![](https://p5.ssl.qhimg.com/t017284a7f218719dd2.png)](https://p5.ssl.qhimg.com/t017284a7f218719dd2.png)

虽然我们现在可以执行任意EL，但仍然无法反弹shell。 为什么？继续看。

### <a name="4.%20EL%E9%BB%91%E5%90%8D%E5%8D%95%E7%BB%95%E8%BF%87%E5%AF%BC%E8%87%B4RCE"></a>4. EL黑名单绕过导致RCE

Seam也知道EL的问题。 从Seam 2.2.2.Final开始，用一个EL黑名单来阻止危险的调用！ 不幸的是，Nuxeo使用最新版本的Seam（2.3.1.Final），因此必须找到绕过黑名单的方法。 黑名单可以在[resources/org/jboss/seam/blacklist.properties](https://github.com/nuxeo/nuxeo/blob/master/nuxeo-features/nuxeo-platform-ui-select2/src/main/resources/web/nuxeo.war/widgets/suggest_add_new_directory_entry_iframe.xhtml#L19)中找到。[![](https://p2.ssl.qhimg.com/t01a86c2723dd2200fc.png)](https://p2.ssl.qhimg.com/t01a86c2723dd2200fc.png)

研究一下发现黑名单只是一个简单的字符串匹配，我们都知道黑名单一般都是下下策。 我刚看到这个，就想起了Struts2 S2-020。这两个有相似之处。 使用类似数组的运算符来处理黑名单模式：<br>
把

改成

最后，在JBoss EL中编写shellcode。 我们使用Java反射API来获取java.lang.Runtime对象，并列出所有方法。 getRuntime（）返回Runtime实例，exec（String）执行我们的命令！

最后总结一下所有所有步骤并将它们连在一起利用：

1.路径规范化错误导致ACL绕过<br>
2.绕过白名单访问未经授权的Seam servlet<br>
3.使用Seam功能actionMethod调用文件中的小工具suggest_add_new_directory_entry_iframe.xhtml<br>
4.在HTTP参数directoryNameForPopup中准备第二阶段payload<br>
5.使用类似数组的运算符绕过EL黑名单<br>
6.使用Java反射API编写shellcode<br>
7.坐等shell

这是整个漏洞利用：<br>[![](https://p2.ssl.qhimg.com/t01a5e2597a6d2a37d7.png)](https://p2.ssl.qhimg.com/t01a5e2597a6d2a37d7.png)

通过执行perl脚本，成功反弹shell：<br>[![](https://p4.ssl.qhimg.com/t01708cb3b327b171ba.png)](https://p4.ssl.qhimg.com/t01708cb3b327b171ba.png)



## 修复

修复分为三块：

### <a name="1%E3%80%81%20JPBoos"></a>1. JPBoos

最麻烦的是Seam框架。 我已于2016年9月向[security@jboss.org](mailto:security@jboss.org)报告了这些问题。但他们的回复是：<br>[![](https://p3.ssl.qhimg.com/t014ce0fa00a6675a15.png)](https://p3.ssl.qhimg.com/t014ce0fa00a6675a15.png)

由于EOL这些问题似乎没有官方补丁。 但是，许多Seam应用程序仍然被广为使用。 所以如果你使用Seam。 建议你用Nuxeo的方案来缓解这个问题。

### <a name="2.%20Amazon"></a>2. Amazon

亚马逊安全团队隔离了服务器，与报告者讨论了如何解决，并列出了他们采取的方案！ 与他们合作是一个很好的经历:)

### <a name="3.%20Nuxeo"></a>3. Nuxeo

在亚马逊发出通知后，Nuxeo迅速发布了8.10版的补丁。 补丁重写了方法callAction()！ 如果需要Seam的补丁，可以在[这里下载](https://github.com/nuxeo/jboss-seam/commit/f263738af8eac44cda7a41ea088c99e69a4edb48)！<br>
时间线<br>
2018年3月10日01:13 GMT + 8通过aws-[security@amazon.com](mailto:security@amazon.com)向亚马逊安全团队报告<br>
2018年3月10日01:38 GMT + 8收到回复他们正在调查<br>
2018年3月10日03:12 GMT + 8要求我参加安全团队的电话会议<br>
2018年3月10日05:30 GMT + 8与亚马逊召开电话会议，了解他们为此漏洞采取的措施<br>
2018年3月10日16:05 GMT + 8询问是否可以公开披露<br>
2018年3月15日04:58 GMT + 8 Nuxeo发布了新版本8.10，修补了RCE漏洞<br>
2018年3月15日23:00 GMT+8 与亚马逊召开电话会议，了解情况并讨论公开细节<br>
2018年4月 5日05:40 GMT + 8获得亚马逊奖金
