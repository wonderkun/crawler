> 原文链接: https://www.anquanke.com//post/id/85410 


# 【技术分享】针对SOAP的渗透测试与防护


                                阅读量   
                                **279715**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.securelayer7.net
                                <br>原文地址：[http://blog.securelayer7.net/owasp-top-10-penetration-testing-soap-application-mitigation/](http://blog.securelayer7.net/owasp-top-10-penetration-testing-soap-application-mitigation/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t019b9915bde700fe46.jpg)](https://p4.ssl.qhimg.com/t019b9915bde700fe46.jpg)



****

翻译：[shinpachi8](http://bobao.360.cn/member/contribute?uid=2812295712)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**SOAP概述**

简单对象访问协议（SOAP）是连接或Web服务或客户端和Web服务之间的接口。SOAP通过应用层协议（如HTTP，SMTP或甚至TCP）进行操作，用于消息传输。

[![](https://p2.ssl.qhimg.com/t01ad5d757ca90b15b2.jpg)](https://p2.ssl.qhimg.com/t01ad5d757ca90b15b2.jpg)

图1 SOAP操作



它是基于xml语言开发的，它使用Web服务描述语言（WSDL）来生成Web服务之间的接口。如果客户端或用户的独立应用程序想要与Web服务连接，则它需要由应用程序生成的服务端点接口（SEI）。这些接口WSDL和SEI是使用自动化工具或手动生成的，它们具有平台无关性。通用描述，发现和集成（UDDI）是Web服务可以发布关于其服务的一个目录，用户可以提交他们的查询。

一个简单的SOAP消息包含:
<li>
Envelope: 标识XML文档，具有名称空间和编码详细信息。
</li>
<li>
标题：包含标题信息，如内容类型和字符集等。
</li>
<li>
正文：包含请求和响应信息.
</li>
<li>
故障：错误和状态信息。

</li>


[![](https://p1.ssl.qhimg.com/t018f7cf9c753ae9457.jpg)](https://p1.ssl.qhimg.com/t018f7cf9c753ae9457.jpg)

图2 SOAP请求和响应的示例

图2显示了SOAP请求和响应，其中Web服务请求用户的名称并回复消息。SOAP是一组被定义为执行某些操作的标准协议，因此它只传输请求的数据，无论请求是什么，如果它在其机制中被验证，它将有答复。

<br>

**常见SOAP漏洞：**

****

**SQL 注入：**

SOAP请求易受SQL注入攻击，提交参数作为变种 sql查询可以泄露敏感信息。

攻击前:

在执行攻击之前，必须知道Web服务的功能，如图3所示，可以看到以string作为输入的username参数。

[![](https://p4.ssl.qhimg.com/t01b7a4ded3160840d4.jpg)](https://p4.ssl.qhimg.com/t01b7a4ded3160840d4.jpg)

图3请求功能分析

输入随机用户名以检查其操作，此时它回应用户名不存在的消息，这可以帮助执行具有可能性的攻击。

[![](https://p1.ssl.qhimg.com/t01240cffbcb9175de5.jpg)](https://p1.ssl.qhimg.com/t01240cffbcb9175de5.jpg)

图4响应信息分析





攻击后：

下面显示的请求是一个攻击者试图通过在参数的位置传递一个sql查询来访问用户详细信息，数据库的错误消息将有助于猜测查询的内容。

[![](https://p0.ssl.qhimg.com/t01e1e34cc12ec9b742.jpg)](https://p0.ssl.qhimg.com/t01e1e34cc12ec9b742.jpg)

图5数据库错误消息

[![](https://p4.ssl.qhimg.com/t018bdb5a33d3c6c2c4.jpg)](https://p4.ssl.qhimg.com/t018bdb5a33d3c6c2c4.jpg)

图6 SQL注入请求

如果传递的查询成功中断了数据库语句查询，那么它将回应用户的信息。

[![](https://p0.ssl.qhimg.com/t01d71acb5f2171e537.jpg)](https://p0.ssl.qhimg.com/t01d71acb5f2171e537.jpg)

[![](https://p5.ssl.qhimg.com/t017d53bd8ce9a64c34.jpg)](https://p5.ssl.qhimg.com/t017d53bd8ce9a64c34.jpg)

图7 SQL注入响应

payload: SQL注入的payload是简单的变形查询，它使数据库获取详细信息，在上面的例子中，使用的数据库是My SQL（来自Fig.5），它可能包含不同的表，知道所有表中的信息可能是不可能的，但是 在这种情况下可以访问某些字段。在图3中，SOAP消息正在使用结合用户名和1＝1的OR语句请求管理员帐户的详细信息，并且将其他所有内容标记为“– ”注释，这使得数据库显示所有用户的用户名和签名。在SQL注入中，可以有更多的可能性来执行攻击，例如具有“，”，“ – ”，“or””and”，“insert”或满足条件的任何其他组合查询的语句。

补丁**：**这种类型的攻击可以通过两种方式来进行防护与修复:

白名单：虽然列表只允许某些字符通过，但在此列表中添加admin等字符会使应用程序只接收列出的字符。

过滤：其中涉及通过删除不需要的字符（例如admin'OR'1 = 1''）来过滤用户输入 – 将被清理，以便只有admin通过它。

<br>

**命令注入**

命令注入是通常通过传递具有数据的命令以获得诸如目录结构，网站地图或甚至与web应用相关的敏感信息的攻击。

[![](https://p3.ssl.qhimg.com/t010d442f9864a42675.jpg)](https://p3.ssl.qhimg.com/t010d442f9864a42675.jpg)

图8命令注入请求（1）



在上述lookupDNS web服务中，使用IP地址和命令ls进行请求，其列出了如下所示的应用的目录结构

[![](https://p0.ssl.qhimg.com/t0106aef9007a0fdc2b.jpg)](https://p0.ssl.qhimg.com/t0106aef9007a0fdc2b.jpg)

图9命令注入响应（1）

在其他请求ping命令传递与IP地址ping主机，如下所示:

[![](https://p1.ssl.qhimg.com/t01c35c8c2f34384a1f.jpg)](https://p1.ssl.qhimg.com/t01c35c8c2f34384a1f.jpg) 

图10命令注入请求（2）

[![](https://p5.ssl.qhimg.com/t01f230cbcebc546d5f.jpg)](https://p5.ssl.qhimg.com/t01f230cbcebc546d5f.jpg)

图11命令注入响应（2）

payload：对于这种类型的攻击，payload是与用户输入相结合的命令语句，但有些命令是常用的，有些是操作系统特定的，操作系统的类型是可以由HTTP可以看到的简单操作。 诸如ls，adduser，install，kill或join等命令可用于执行操作。

补丁：为了修补命令注入攻击，必须构建严格的验证机制，并且实现其功能，数据库对于包含攻击模式192.168.66.2; ls 和192.168.66.2＆amp; ＆amp; ping c1 localhost 进行验证，以便它只允许字母数字字符。在上述命令中，注入攻击包括特殊字符＆或;这将在服务端执行时分离命令和数据，因此必须开发考虑这些情况的函数功能。

 

**XML ****注入**

在XML注入类型的攻击中，SOAP消息的变形请求可以在数据库中进行更改，并对数据库造成严重损坏。



正常功能：创建用户函数在应用程序中创建新用户，这需要几个参数作为输入，如图12所示 





<br>

**[![](https://p0.ssl.qhimg.com/t017e5f84d239978200.jpg)](https://p0.ssl.qhimg.com/t017e5f84d239978200.jpg)**

图12 XML请求

响应将具有带有插入了用户名帐户的消息的return语句，如图13所示



[![](https://p0.ssl.qhimg.com/t01411e57af531d65ab.jpg)](https://p0.ssl.qhimg.com/t01411e57af531d65ab.jpg)

图13 XML响应

攻击 

在实际的XML注入中，代码的一部分被变形并与请求一起发送，使得代码将在另一侧执行，在图14中，创建用户功能被添加有附加代码以利用服务。

[![](https://p5.ssl.qhimg.com/t01409aa4e6d5a94f81.jpg)](https://p5.ssl.qhimg.com/t01409aa4e6d5a94f81.jpg)

图14 变形的XML请求

从图15可以看出，web服务被执行具有插入了用户名帐户的消息的代码。该功能执行攻击者插入的参数，而不是实际请求。

[![](https://p4.ssl.qhimg.com/t01e8b330ad86a98c2a.jpg)](https://p4.ssl.qhimg.com/t01e8b330ad86a98c2a.jpg)

图15 变形请求的响应

payload：这种类型攻击的有效载荷实际上是在另一端提交的参数，在这种情况下，创建用户XML标签被变形或添加了帐户Alice的详细信息并附加请求，以便它将执行它。

补丁：这种类型的攻击的补丁对createUser的标签字符串进行了严格的限制，它必须使用字符串的长度来定义，并且必须定义wsdl中createUser功能的次数或发生次数。 基于数据和解析器为用户输入开发清理机制，并且还使用文档类型定义（DTD）来验证尝试注入是最佳实践。

<br>

**SOAP****操作欺****骗**

每个HTTP请求都包含一个称为SOAP Action的字段，用于执行在其内容中定义的操作。可能由攻击者改变内容，攻击者在客户端和服务器之间操作，一种绕过或中间人攻击。

下面显示的请求消息包含一个称为create user的功能，它可以在SOAP Action字段和SOAP主体中看到。

[![](https://p2.ssl.qhimg.com/t019b7c8609db56a225.jpg)](https://p2.ssl.qhimg.com/t019b7c8609db56a225.jpg)

图16带有SOAP动作字段的SOAP请求

简单地变形（可能不是一个）可以改变其功能，如图17所示

[![](https://p0.ssl.qhimg.com/t011e84fae1f893b0f4.jpg)](https://p0.ssl.qhimg.com/t011e84fae1f893b0f4.jpg)

图17 变形的SOAP动作的请求

在更改请求并将其传递到服务器后，请求将有一个响应，因为它似乎是合法的，并执行其操作删除帐户，可以在图18

[![](https://p1.ssl.qhimg.com/t01065d5b9534d4be74.jpg)](https://p1.ssl.qhimg.com/t01065d5b9534d4be74.jpg)

图18 SOAP执行变形请求后的响应

payload：对于这种类型的攻击没有特定的有效载荷，SOAP动作字段被认为是目标，对功能的彻底分析可以提供执行攻击的线索。仅改变SOAP字段可能不足以执行攻击，它可能需要根据所执行的动作来改变请求消息。

补丁：为了防止这种类型的攻击，必须在HTTP请求中禁用SOAP Action字段（如createUser或deleteUser），或使用不容易猜到的SOAP Action术语。有时可能需要在这样的事件中强制添加Action字段，开发人员必须考虑SOAPAction：“”（意味着SOAP消息的意图由请求的URI给出）的可能性或SOAP Action：（空字段表示 消息的意图是不指示任何值或URI）。

<br>

**SOAP****参数****DOS****攻****击**

每个SOAP请求包含一个被传递以获取一些数据的参数，有一些请求，攻击者可以利用这些请求来执行拒绝服务攻击。 如果应用程序无法执行输入验证或没有参数的边界，可能导致缓冲区溢出，这将使服务不可用。 下图显示的参数用户名没有任何边界限制，因此任何一个都可以将任意长度的字符串传递给应用程序。

[![](https://p5.ssl.qhimg.com/t011cfdb4970c4059c3.jpg)](https://p5.ssl.qhimg.com/t011cfdb4970c4059c3.jpg)

 图19没有限制条件的SOAP请求

如果用户名有限制，那么它会有一些异常传递正确的字符串，这将使应用程序安全。

<br>

payload：这种类型的攻击的有效载荷是知道在请求中传递的数据类型，因此基于传递最大值或大值的数据类型可以是攻击的方式。

补丁：为了减轻这种类型的攻击，必须使用最小和最大长度或某些边界来定义参数，例如参数用户名包含5个最小值和35个字符串最大长度，可以在处理中轻松验证。

[![](https://p2.ssl.qhimg.com/t01007bcd5ac4d6e56d.jpg)](https://p2.ssl.qhimg.com/t01007bcd5ac4d6e56d.jpg)

图20 带条件的SOAP请求

 

**W****SDL****泄****露**

WSDL泄露不能被视为攻击，而是攻击的一个步骤，就像我们所知道的，所有WSDL都知道的包含Web服务的信息，有一些Web服务需要对诸如支付网关或正在收集敏感信息的服务等攻击者隐藏。 任何攻击者都可以通过在搜索引擎中输入“inurl：？wsdl”来搜索Web服务。

[![](https://p4.ssl.qhimg.com/t011b6ffd0ba32051b2.jpg)](https://p4.ssl.qhimg.com/t011b6ffd0ba32051b2.jpg)

图21 wsdl搜索

[![](https://p1.ssl.qhimg.com/t015084e41398e93882.jpg)](https://p1.ssl.qhimg.com/t015084e41398e93882.jpg)

图22 Web服务WSDL

补丁

用于数据的安全传输的Web应用程序从不依赖于其安全性如使得Web服务的URL,对于搜索引擎和公开内容是隐藏的，并且对诸如机密性，完整性和真实性的特征进行严格保持。



**参考链接：**

[https://www.owasp.org/index.php/Testing_for_Web_Services](https://www.owasp.org/index.php/Testing_for_Web_Services) 


