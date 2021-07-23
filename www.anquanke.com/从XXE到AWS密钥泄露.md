> 原文链接: https://www.anquanke.com//post/id/222679 


# 从XXE到AWS密钥泄露


                                阅读量   
                                **123322**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者estebancano，文章来源：medium.com
                                <br>原文地址：[https://medium.com/@estebancano/unique-xxe-to-aws-keys-journey-afe678989b2b](https://medium.com/@estebancano/unique-xxe-to-aws-keys-journey-afe678989b2b)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t019c9912e864bb0c3c.png)](https://p5.ssl.qhimg.com/t019c9912e864bb0c3c.png)



​ 事情起源于我被邀请去做一次授权渗透测试，由于这是第一个给我报酬的项目，因此我想做到最好。目标客户是一家在15多个国家拥有业务的公司，在全球有120多个子公司和1200多万用户。

​ 他们给了我一个域名和用户名、密码，现在直接开始吧。第一眼我觉得这个网站很大，而且防护的很不错。它有很多功能需要测试，也有很多配置文件，所以我直接开始进行目录扫描(dirsearch)来看看背后有什么。

​ 一些xml配置文件出现了，标志着这可能有tomcat。读了一些xml文件，我发现了`&lt;url-pattern&gt;`的标签，所以灵感告诉我应该试试用burp来GET请求，看看服务端的响应。

[![](https://p4.ssl.qhimg.com/t0105ad24b2d90c5d59.png)](https://p4.ssl.qhimg.com/t0105ad24b2d90c5d59.png)

服务端响应里有nginx，所以网站的架构大概是什么样子？ 应该是这样：

[![](https://p3.ssl.qhimg.com/t01940cdfacb798678e.png)](https://p3.ssl.qhimg.com/t01940cdfacb798678e.png)

因此可以看出后端不喜欢GET请求，那么我试试POST请求吧。

[![](https://p0.ssl.qhimg.com/t01826920b097cbbd37.png)](https://p0.ssl.qhimg.com/t01826920b097cbbd37.png)

在响应里面你可以看到一个Content-Type的HTTP header头的值是text/xml，所以响应应该是一个有效的xml文档，但是这里我只得到了一个“Could not access envelope: Unable to create…”的错误。

> 所以，如果是你，你应该怎么办？

我直接想到了最坏的情况就是存在XXE漏洞，因此我直接去搜索了几个XXE的payloads，我在请求里面也加上了Content-Type: text/xml (这正好是服务端想要的而且也相当于告诉了它我发送给了它什么)

我直接把获取/etc/passwd文件的payload复制过去了，试着读这个文件。然后就出现了这样的情况：

[![](https://p2.ssl.qhimg.com/t01451db8730ff30d99.png)](https://p2.ssl.qhimg.com/t01451db8730ff30d99.png)

响应码是200没错，似乎服务端想要读取/etc/passwd的内容然后形成一个xml文档作为响应，但是这个文件的第33行不太符合，可能是有什么东西阻碍了解析。

现在我们知道了，/etc/passwd文件大约有33行，我问了一下客户，客户确认了这个文件确实是有33行的。

所以下一个事情就是获得其中的内容然后就完事了。直到现在，在一个漏洞挖掘项目里面这个可能不会认为是poc，因为我们用这个无法造成损害。所以你现在必须继续挖掘直到你发现了新的东西。

所以我生成了一个SSRF请求，然后它确实有效！我知道了tomcat的默认端口就是8080，然后从谷歌浏览器的控制台我发现，在第一个payload请求后返回了405错误，显示出这样：

[![](https://p0.ssl.qhimg.com/t01b6b027461e7e1d64.png)](https://p0.ssl.qhimg.com/t01b6b027461e7e1d64.png)

所以我试了下面这个请求：

[![](https://p2.ssl.qhimg.com/t0149c7344c48425d91.png)](https://p2.ssl.qhimg.com/t0149c7344c48425d91.png)

服务端请求了它自己，然后去获取DTD，回应给了我们一个错误：它试着解析我让他请求的html文档，但是产生了一个错误，后来我发现html代码是这样的：

[![](https://p1.ssl.qhimg.com/t013d1cf19c51b18371.png)](https://p1.ssl.qhimg.com/t013d1cf19c51b18371.png)

所以我试了一下另一个端口来看看是怎么个样子：

[![](https://p2.ssl.qhimg.com/t013d6550d846cf8819.png)](https://p2.ssl.qhimg.com/t013d6550d846cf8819.png)

所以8081端口是关闭的，我们现在可以用burp intruder检测每个端口，然后看看请求的响应（就类似于http版的nmap）来看看某端口是不是开放，直到现在，我们只知道8080开放。

> 尝试完nmap的top 1000端口，我发现至少开了8个端口。

所以我希望获得一些有趣的文件的内容，这是需要继续努力的部分。试了非常多的payloads（除了Dos），用我能想到的各种方式修改这些payloads，试了协议类似：file:// php:// dict:// expect:// 等等，但是都被禁用了。我也读了很多的writeup，然后什么都没发现。

机制就像下面的图一样：

[![](https://p5.ssl.qhimg.com/t01ae2a4b626c4c2384.png)](https://p5.ssl.qhimg.com/t01ae2a4b626c4c2384.png)

所以我这次不把所有的xml都放在请求里面，而是把一部分放到我的服务器上（加载外部DTD），所以这个网站会去加载xml的所有部分来解析，然后来响应我（我们已经可以用SSRF访问本地资源了，那么访问远程因特网的资源会怎么样？）

[![](https://p0.ssl.qhimg.com/t01aba3f308ad859282.png)](https://p0.ssl.qhimg.com/t01aba3f308ad859282.png)

[![](https://p4.ssl.qhimg.com/t01c0648b366ae42fa2.png)](https://p4.ssl.qhimg.com/t01c0648b366ae42fa2.png)

其中`&amp;#x25`是%的url编码，不编码会导致解析错误。

> 在外部DTD中你发现了什么奇怪的东西？

我在我的服务器上挂在了这个外部DTD文件（a.dtd）,奇怪的是我没有请求/etc/passwd文件（其实我以前试过，但是还是得到了同样的提示）。

我请求的是 /

然后是响应：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f4b63650be8e10d4.png)

> 看看我发现了什么？

没错，非常有趣的现象，没有出错，反而列出了目录。我从来没在任何的wp中见过这样的奇怪的现象，但这非常宝贵！你知道为什么发生吗？我以前不知道，直到我在某一天后看到了这个: [this](https://honoki.net/2018/12/12/from-blind-xxe-to-root-level-file-read-access/) 这似乎是java的问题，当请求目录而不是文件的时候列出目录内容。

所以现在我不再猜目录和猜文件，而是花时间手动浏览许多文件夹以获得更大的影响。

最终我发现了很多私钥，配置文件，敏感数据，第三方服务密码和客户信息等等。。。

但是最重要的发现是：AWS 认证秘钥，我试图通过AWS元数据获取一些数据，但是发现我没有权限。

在一个目录类似于/xxx/xxx/xxx/xxx/credentials有这样的内容:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b15b15e31795e9eb.png)

我去看了看分别在[PACU](https://github.com/RhinoSecurityLabs/pacu)和[AWS CLI](https://aws.amazon.com/en/cli/)有什么权限：

发现他们有root权限，所以我还能得到什么有趣的？

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014d2f6d506c0432f2.png)

> 所以如果是你，你会用这些权限做什么？

例如，一个黑客可以：
1. 改变服务器实例状态： 他能够停掉、开启、创建所有服务
1. 利用服务器挖矿、放后门、放脚本，想象一下哗哗的钞票~
1. 窃取数据（信用卡和个人信息）
1. 拒绝服务
1. 其他等等….
所以现在看看网站是建立在AWS EC2主机上的，我试着通过以前的ssrf访问数据，它也有效（利用外部dtd，而不是普通的基础payload），请求[http://169.254.169.254/latest/meta-data/iam](https://jsproxy.jesen.workers.dev/-----http://169.254.169.254/latest/meta-data/iam) 而不是 file:///

[![](https://p0.ssl.qhimg.com/t01d85bf4e9c14b6342.png)](https://p0.ssl.qhimg.com/t01d85bf4e9c14b6342.png)
