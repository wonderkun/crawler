> 原文链接: https://www.anquanke.com//post/id/83613 


# SpagoBI的远程代码执行漏洞


                                阅读量   
                                **64714**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://remoteawesomethoughts.blogspot.jp/2016/03/spagobi-remote-code-execution-by.html#!/2016/03/spagobi-remote-code-execution-by.html](https://remoteawesomethoughts.blogspot.jp/2016/03/spagobi-remote-code-execution-by.html#!/2016/03/spagobi-remote-code-execution-by.html)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p5.ssl.qhimg.com/t01f69d627c593b28df.jpg)](https://p5.ssl.qhimg.com/t01f69d627c593b28df.jpg)

**文章摘要**

这是我们的第二篇相关文章了，这也是我们所发现的第二个远程代码执行漏洞。在这篇文章中，我们将会对SpagoBI进行讨论。SpagoBI是一个免费的开源商业智能软件。该平台由SpagoBI实验室进行开发，旨在为商业智能项目提供了一个完整开源的解决方案。这是一个百分之百开源的商业智能套件，并且还有大量热情的开源社区开发人员，集成制造商，企业和用户正在为这一开源软件而共同努力。

首先我们需要声明的是，我们在这篇文章中所讨论的漏洞目前仍然没有修复。我之所以要将这一漏洞的详细信息披露出来，是因为我早在2014年12月份的时候就已经将有关这一漏洞的详细信息提交给了相关的制造商，但是这个漏洞直到现在都没有被修复。这也足以说明相关人员在处理漏洞这一方面存在非常严重的问题。

通常情况下，我是不会对目前没有进行修复的漏洞进行披露的。但是就现在的情况来看，也许只有更多的黑客知道了这个漏洞，相关厂商才会意识到问题的严重性。

**漏洞描述：**

SpagoBI利用Groovy库来在后台执行动态的商业智能操作。所以，在其源代码中应该有部分功能代码可以对平台输入的内容和数据进行解析。Groovy支持系统输入原生的Java对象，所以如果系统中没有设置过滤器的话，那么就很容易会出现远程代码执行漏洞。事实上，在应用程序中并不存在相应的过滤器来对输入数据进行过滤，所以攻击者就可以通过修改代码库中的少数功能函数来执行任意命令了。

为了更好地向大家讲解这个漏洞，我们将会主要对“SpagoBIQbeEngine” Servlet中的一个漏洞进行讲解。在演示这个漏洞的过程中，我们将会使用最新版的虚拟镜像文件（SpagBI 5.1），大家可以在网上下载获取。除此之外，我们还将使用该平台权限最低的“bidemo”用户来进行登录操作。

[![](https://p5.ssl.qhimg.com/t01e3d7d5df513520db.png)](https://p5.ssl.qhimg.com/t01e3d7d5df513520db.png)

然后，我们找到“QbE”功能选项：

[![](https://p3.ssl.qhimg.com/t019903032e51f585ab.png)](https://p3.ssl.qhimg.com/t019903032e51f585ab.png)

在点击了这一选项之后，我们可以在系统后台看到相应的请求信息和系统处理过程：

[![](https://p4.ssl.qhimg.com/t01833b4b858d37b94e.png)](https://p4.ssl.qhimg.com/t01833b4b858d37b94e.png)

然后，服务器端将会为此请求处理过程创建一个相对应的标识符，然后再将响应信息发送回客户端。

[![](https://p4.ssl.qhimg.com/t01ec58efa55e11f15b.png)](https://p4.ssl.qhimg.com/t01ec58efa55e11f15b.png)

这个标识符是十分重要的，我们在利用这个漏洞的过程中会需要使用到这个标识符，因为它是目标函数的其中一个参数。那么现在，我们只需要调用存在漏洞的函数，然后将标识符传递给它，然后我们就可以加载我们的攻击Payload了。

```
http://localhost:8080/SpagoBIQbeEngine/servlet/AdapterHTTP?ACTION_NAME=Validate_Expression_Action&amp;EXPRESSION=java.lang.Runtime.getRuntime().exec('notepad')&amp;fields=[`{`"uniqueName":"test","alias":"test"`}`]&amp;SBI_EXECUTION_ID=XXX
```

[![](https://p1.ssl.qhimg.com/t01da10878bcda2f375.png)](https://p1.ssl.qhimg.com/t01da10878bcda2f375.png)

请求信息的具体内容：

[![](https://p3.ssl.qhimg.com/t01877785acd397a452.png)](https://p3.ssl.qhimg.com/t01877785acd397a452.png)

正如下图所示，请求的响应信息内容为空，这也就意味着我们的漏洞利用过程一切顺利。

[![](https://p3.ssl.qhimg.com/t0122c15979dd7f8725.png)](https://p3.ssl.qhimg.com/t0122c15979dd7f8725.png)

**总结：**

在这篇文章中，我想要警告所有SpagoBI的用户，你们一直都处于安全风险之中，而且已经持续了一年的时间了。除此之外，我还想告诉大家的是，我之所以等待了一年多的时间才将这个漏洞的详细信息公布出来，是因为我也明白修复这个漏洞实际上并不是一件容易的事情，所以我觉得等待也是可以接受的。但是在我向相关厂商提交了漏洞信息之后，却没有得到任何有实际意义的反馈信息，所以我认为我必须要将这个漏洞的信息公布出来，才能引起相关厂商的重视。

**漏洞披露时间轴：**

2014年12月17日：向供应商发送了第一封电子邮件，并在邮件中提供了关于此漏洞的详细内容。

2014年12月22日：向供应商发送了第二封电子邮件，并要求厂商提供反馈信息。

2014年12月22日：供应商承认了这一漏洞。

2015年01月22日：向供应商发送了第三封电子邮件，并要求供应商反馈目前该漏洞的修复状况。

2015年02月19日：向供应商发送了第四封电子邮件，并要求供应商反馈目前该漏洞的修复状况。

2015年02月23日：供应商通过电子邮件回复称，他们打算利用沙箱来解决这一问题。

2015年02月24日：向供应商发送了第五封电子邮件，告诉他们引入沙箱实际上并不能从根本上解决这一问题。

2015年12月03日：向供应商发送了第六封电子邮件，并要求厂商对目前该漏洞的处理情况进行反馈。

2015年12月03日：厂商回应称他们将采用白名单方式来进行处理，并且在邮件中提供了该方法的具体实施细节。

2015年12月07日：向供应商发送了第七封电子邮件，警告称白名单处理方法非常的危险，攻击者将能够利用这一漏洞来向服务器写入任意内容的数据。

2016年03月08日：仍然没有得到厂商回应。我决定将此漏洞的详细信息披露出来。
