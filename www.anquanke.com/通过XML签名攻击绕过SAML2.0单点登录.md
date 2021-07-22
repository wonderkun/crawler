> 原文链接: https://www.anquanke.com//post/id/87572 


# 通过XML签名攻击绕过SAML2.0单点登录


                                阅读量   
                                **91769**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者eridunas96，文章来源：aurainfosec.io
                                <br>原文地址：[http://research.aurainfosec.io/bypassing-saml20-SSO/](http://research.aurainfosec.io/bypassing-saml20-SSO/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01981d4b501a029bcb.png)](https://p0.ssl.qhimg.com/t01981d4b501a029bcb.png)

## 

## 0. 前言

近期我们发现，有很多新西兰网站都采用了单点登录（SSO）的方式，这其中包括很多政府网站。实现单点登录，最常见的一个标准就是SAML 2.0（安全声明标记语言），该标准对多种框架和语言都拥有良好的适配性。通常我们使用签名，来防止用于验证用户身份的SAML响应被篡改。然而，还是有许多SAML使用者没有正确地验证响应，这就带来了攻击认证过程和完全绕过认证的潜在风险。

## 

## 1. SAML 2.0单点登录

我们在通过SAML2.0登陆到网站时，会涉及到三种角色：服务提供者（SP，我们要访问的Web应用程序）、使用者（正在登录的用户）和身份提供者（IdP，认证管理）。我们的目的是，要让身份提供者以可靠的方式告诉服务提供者，谁才是使用者。



由此，我们需要让服务提供者，将使用者重定向到带有SAML请求的身份提供者的系统之中。一旦身份提供者确认使用者的身份，就会将SAML响应发送回服务提供者。对于Web单点登录来说，主要有三种通信方式，官方标准中将其称为“绑定”：



HTTP重定向绑定，是将SAML消息直接包含在URL中。

HTTP POST绑定，将SAML消息包含在POST请求之中。

HTTP工件绑定，我们发送一个随机的token，它将作为标识符，通过一个反向信道来获取文档。

前两种绑定方式，在实现的过程中可能会产生一些严重的问题。

## 

## 2. 识别SAML响应

如上所述，SAML响应通常会在URL中传递，就像是这样：

[![](https://p1.ssl.qhimg.com/t01bc7ff7e3daac8c31.png)](https://p1.ssl.qhimg.com/t01bc7ff7e3daac8c31.png)

或者是在POST请求中传递，像这样：

[![](https://p2.ssl.qhimg.com/t018d34c80595ec6207.png)](https://p2.ssl.qhimg.com/t018d34c80595ec6207.png)

这两种传递方式，都可以由攻击者控制直接进行。但假如你看到的是像这样的SAML工件：

[![](https://research.aurainfosec.io/images/bypassing-saml20-SSO/artifact-binding.png)](https://research.aurainfosec.io/images/bypassing-saml20-SSO/artifact-binding.png)

那么攻击者可能就真的无能为力了。因为这些token会被解析为原始消息，随后通过一个反向信道获取，除非攻击者有权访问攻击目标的私有网络（可以借助SSL/TLS漏洞），否则这些token对于攻击者来说毫无用处。

## 

## 3. 在传输过程中对消息进行保护

这里的安全问题，就在于HTTP重定向绑定和HTTP POST绑定这两种方式。从身份提供者获取到文档，将会通过用户的浏览器传递，从而验证身份。而正是在这一消息传输过程中，有可能被篡改。HTTP工具绑定就不存在这一安全问题。



如果这些消息缺少保护，攻击者可能会通过简单地修改返回的响应数据来伪装身份。例如，我以Tim的身份登录到身份提供者，随后我可以对响应文档进行修改，伪装成Emmanuel。更进一步，我们甚至可以伪造整个响应，真正意义上假装自己是Emmanuel。



显然，SMAL标准制定者也不会放任这个漏洞的存在，他们已经做了很大努力去解决这一问题。他们的解决方案是，为每一条消息附加一个XML签名，以防止消息被篡改。

## 

## 4. XML签名标准

XML签名标准是一个庞然大物，由一个大神云集的工作小组设计而成，其目标是成为一个完美适配所有场景的XML文档抗篡改解决方案。但事实并不如愿，现实的情况是，它并没能适配上任何场景。



在通常情况下，使用数字签名时，我们将文档签名，然后运行一个密码散列函数来计算出其哈希值，随后对该哈希值使用数字签名算法。如果收到的文档和原文档完全相同，那么签名有效。否则，即使只有一位，签名都存在改动，签名都会变为无效，并且文档也不会被承认。



不幸的是，XML签名有一个致命的特性：该标准允许我们可以对文档的一部分进行签名，而不是必须对整个文档进行签名，并将这个签名嵌入到应该验证的文档之中，即所谓的内联签名。该签名会引用文档的一部分，通常是XML元素的ID属性，但理论上允许将符合XPath标准的任意内容作为表达式。理论上，我可以在文档的任意位置写入指向“third to last &lt;foo&gt; element”的签名，或者类似的模糊表达式。



在对XML签名进行验证时，假如只确认“该签名是否来源于签名者”还远远不够。我们必须还要确认“签名是否存在”、“签名是否指向了文档的正确位置”“是否正确地应用了标准”、“签名是否有效”。而普遍来说，很少有对以上所说的每一项都进行检查的。



## 5. SAML Raider插件的使用方法

尽管有很多攻击都可以不借助工具进行，但我们还是需要介绍一个Burp Suite的插件，SAML Raider。借助该插件，就能对SAML的安全性进行全面的测试。

## 

## 6. 测试过程

如上文所说，签名可能会出现在SAML消息中的不同位置，并且覆盖消息的各个部分。如果我们保留原有消息内容，再增加新的内容，同时修改剩余部分的结构，我们就能构造出一个带有合法签名的新消息。这一消息，会被SAML库解析为含有签名的关键内容的消息，但事实并非如此。



每一次服务提供者的验证，都有可能是在进行不正确的验证，这就给了我们绕过签名验证的机会。打开Burp的拦截功能，捕获SAML请求，然后尝试对这些请求内容进行转换。每一次尝试转换，都要根据一个新的、有效的登录动作来完成，因为它有一个Nonce来防范重播攻击。



针对需要多次尝试的情况，建议按照以下方式设置Burp的Proxy： [![](https://research.aurainfosec.io/images/bypassing-saml20-SSO/intercept-single-endpoint.png)](https://research.aurainfosec.io/images/bypassing-saml20-SSO/intercept-single-endpoint.png)

### 

### 6.1 签名是否必须？

SAML标准要求，通过非安全信道（如用户的浏览器）传输的所有消息都必须进行数字签名。然而，如果消息是通过安全信道（如SSL/TLS反向通道）进行传输，那就可以不进行签名。由此我们发现，SAML的使用者会在签名存在时对其进行验证，并在签名被删除的情况下跳过验证。这一设计，是建立在我们已经检查了来自非安全信道的消息是否签名的前提之下，然而事实并非如此。

这一问题所产生的漏洞是，我们可以直接删除消息中的签名，并篡改SAML响应，伪造成未经签名的消息。SAML Raider插件可以轻松完成该项的测试：

[![](https://research.aurainfosec.io/images/bypassing-saml20-SSO/remove-signatures.png)](https://research.aurainfosec.io/images/bypassing-saml20-SSO/remove-signatures.png)

### 

### 6.2 签名是否已验证？

要验证一个XML签名是非常复杂的，根据标准，首先需要进行一系列的转换和规范化步骤（例如：忽略空字符）。这就使得一些没有完备功能的XML签名库在验证签名方面实现起来十分困难，也产生了一些影响：



1. 开发人员通常不了解签名验证的内部原理；

2. 一些中间组件（如WAF）无法获知签名是否有效；

3. 签名库可能存在一些配置选项，如允许的规范化方法列表，对开发人员来说毫无意义。

签名标准的实现本来就很困难，再加上该标准难以理解，就直接导致了我们现在遇到的这些问题。

不过，要测试一个签名是否有效，方法很简单。我们可以在已签名的内容中修改一些地方，并观察是否会导致中断。

### 6.3 签名是否来自正确的签署人？

另一个重要的问题，就是接收方是否验证了签名者的身份。我们不清楚是否对这一部分进行了正确的判断，但SAML Raider插件可以轻松地测试这一方面。

将签名证书复制到SAML Raider的证书存储区：

[![](https://research.aurainfosec.io/images/bypassing-saml20-SSO/import-certificate.png)](https://research.aurainfosec.io/images/bypassing-saml20-SSO/import-certificate.png)

保存之后对此证书进行自签名，所以现在我们便有了一个相同证书的自签名副本。

[![](https://research.aurainfosec.io/images/bypassing-saml20-SSO/self-sign-cert.png)](https://research.aurainfosec.io/images/bypassing-saml20-SSO/self-sign-cert.png)

这时，我们就可以使用这个自签名证书，对原始请求再次进行签名。我们可以选择对整个消息进行签名，也可以选择只对声明的部分进行签名。

[![](https://research.aurainfosec.io/images/bypassing-saml20-SSO/re-sign-messages.png)](https://research.aurainfosec.io/images/bypassing-saml20-SSO/re-sign-messages.png)

我们可以根据实际情况选择其中的一种方式，或者两种方式都进行尝试。

### 

### 6.4 是否已经对响应中正确的部分进行签名？

首先，我们来看看XSW攻击原理。

SAML标准所允许的签名存在的位置仅有两处：

1. 签名位于响应（Response）标签中，对响应标签及其子节点进行签名；

2. 签名位于声明（Assertion）标签中，对声明标签及其子节点进行签名。

SAML标准对允许签名存在的位置以及允许被签名的内容都有具体的描述。

然而，没有人仅仅为了使用SAML，就完整地实现复杂的XML签名机制。这一标准是通用的，标准的实现及其软件库也是如此。因此，就有了如下的“职责分离”：

1. XML签名库根据XML验证标准验证签名，它允许从任何地方签名任何内容；

2. SAML库期望XML签名库告诉它响应消息是否有效。

在两个组件之间，往往会缺少对于必要规则的判断机制。因此，我们就可以将签名引用到文档的不同位置，并且让接受者认为签名是有效的。

通过复制文档的签名部分，同时确保签名数据指向副本，我们可以将XML签名库的验证内容和SAML库的所需内容分开。

针对绝大多数常见的攻击，SAML Raider插件都可以自动进行。

[![](https://research.aurainfosec.io/images/bypassing-saml20-SSO/xsw-transforms.png)](https://research.aurainfosec.io/images/bypassing-saml20-SSO/xsw-transforms.png)

我们可以尝试下拉菜单中的每一个选项，点击“Apply XSW”发送请求数据。如果没有产生错误，我们可以修改SAML XML中的用户名或其他用户标识符，并再次尝试执行该操作。

## 

## 7. 使用限制及手动测试方法

虽然SAML Raider能测试常见的绝大多数情况，但我们还需要对一些攻击有更深入的理解：

1. 生成一个会对XML Schema进行验证的响应（需要在可能包含xs:any的元素中隐藏影子副本）；

2. 当Response和Assertion都被签名和验证时，如何绕过验证；

3. 在非SAML上下文中绕过XML签名，例如：在使用WS-Security扩展的SOAP Endpoints中。

如果SAML Raider插件现有的选项都不起作用，我们可以尝试手动测试：

1. 对Base64编码后内容进行解码，以获取SAML响应XML。

2. 检查签名的Reference标签是否包含被签名元素的ID。

3. 将签名的内容复制到文档中的其他位置（通常可以放在Response标签的末尾；如需验证XML Schema，则要放在不会破坏XML Schema的位置）。

4. 从副本中删除XML签名，并在原始版本中保留。这是有必要的，因为XML封装签名标准会删除将要被验证的签名。在原始文档中，这就是所包含的签名，所以我们必须将其从副本中删除。

5. 将原始签名元素的ID改为其他值（可以通过更改其中1个字母）；

6. 修改原始声明的内容；

7. 对以上内容重新进行Base64编码，将其放回请求中并提交。

如果签名验证指向该副本，那么它将忽略我们所做的更改。在实际中，如果对请求有着严格的时间限制，我们应该可以很快地完成这一过程。

## 

## 8. SAML渗透测试检查清单

1. SAML响应是否通过Web浏览器？

2. 响应内容是否签名？如果没有签名，尝试修改内容。

3. 如果删除签名，响应内容是否会被接受？

4. 如使用其他证书重新签名，响应内容是否会被接受？

5. 使用SAML Raider自带的8种转换方式生成的结果是否会被接受？

6. 如果我们更改响应，更改后的响应是否会被接受？

7. 是否遇到了上文所述的SAML Raider的局限性？如果是，则需要尝试手动测试方法。
