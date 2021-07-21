> 原文链接: https://www.anquanke.com//post/id/99275 


# SAML存在漏洞影响多款产品


                                阅读量   
                                **135113**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Kelby Ludwig，文章来源：duo.com/blog
                                <br>原文地址：[https://duo.com/blog/duo-finds-saml-vulnerabilities-affecting-multiple-implementations](https://duo.com/blog/duo-finds-saml-vulnerabilities-affecting-multiple-implementations)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t015b1053a98868edad.png)](https://p3.ssl.qhimg.com/t015b1053a98868edad.png)



## 一、前言

本文介绍了一个新的漏洞，该漏洞可以影响基于SAML的单点登录（single sign-on，SSO）系统。具备访问认证权限的攻击者可以利用这个漏洞，在不知道受害者密码的前提下，让SAML系统以受害者身份进行认证。

作为Duo Security的高级研究团队，[Duo Labs](https://duo.com/labs)发现有多个厂商受此漏洞影响，如下所示：

```
OneLogin - python-saml - CVE-2017-11427
OneLogin - ruby-saml - CVE-2017-11428
Clever - saml2-js - CVE-2017-11429
OmniAuth-SAML - CVE-2017-11430
Shibboleth - CVE-2018-0489
Duo Network Gateway - CVE-2018-7340
```

如果用户需要使用基于SAML的SSO方案，我们建议用户更新受影响的软件以修补此漏洞。如果你是Duo Security的客户，正在使用Duo Network Gateway（DNG），你可以参考我们的[产品安全公告](https://duo.com/labs/psa/duo-psa-2017-003)了解更多信息。



## 二、SAML Responses简介

SAML的全程是Security Assertion Markup Language（安全声明标记语言），是单点登录系统常用的一种标准。Greg Seador写了一篇很好的教学[指南](https://duo.com/blog/the-beer-drinkers-guide-to-saml)来介绍SAML，如果你对此不甚了解，我强烈建议你阅读这篇指南。

为了理解这个漏洞，我们需要了解SAML `Response`对服务提供商（Service Provider，SP）的意义以及具体处理过程，这是一个重要概念。`Response`处理起来有许多细节之处，但可以简化为如下步骤：

1、用户向身份提供商（Identity Provider，IdP）发起认证请求，IdP（比如Duo或者GSuite）会生成经过签名的SAML `Response`。用户浏览器随后会将response转发给某个SP（如Slack或者Github）；

2、SP验证SAML `Response`的签名；

3、如果签名有效，则通过SAML `Response`中用于身份标识的某个字符串（如`NameID`）来识别出需要对哪个用户进行认证。

一个非常简单的SAML `Response`结构如下所示：

```
&lt;SAMLResponse&gt;
    &lt;Issuer&gt;https://idp.com/&lt;/Issuer&gt;
    &lt;Assertion ID="_id1234"&gt;
        &lt;Subject&gt;
            &lt;NameID&gt;user@user.com&lt;/NameID&gt;
        &lt;/Subject&gt;
    &lt;/Assertion&gt;
    &lt;Signature&gt;
        &lt;SignedInfo&gt;
            &lt;CanonicalizationMethod Algorithm="xml-c14n11"/&gt;
            &lt;Reference URI="#_id1234"/&gt;
        &lt;/SignedInfo&gt;
        &lt;SignatureValue&gt;
            some base64 data that represents the signature of the assertion
        &lt;/SignatureValue&gt;
    &lt;/Signature&gt;
&lt;/SAMLResponse&gt;
```

上面这个示例省略了许多信息，但省略的这些信息对于这个漏洞而言并不重要。上述XML数据中，最重要的两个元素为`Assertion`以及`Signature`。`Assertion`元素表达的意思是：“Hey，我是IdP，认证了`[user@user.com](mailto:user@user.com)`这个用户”。`Assertion`元素会对应一个签名，作为`Signature`元素的一部分存放在XML结构中。

如果`Signature`元素准确无误，应该能阻止对`NameID`的篡改。由于SP很有可能会使用`NameID`来判断需要对哪个用户进行身份认证，因此该签名就能阻止攻击者将他们自己的`NameID`信息从`[attacker@user.com](mailto:attacker@user.com)`修改为`[user@user.com](mailto:user@user.com)`。如果攻击者能够在不破坏签名的前提下修改`NameID`字段，那么这将是非常糟糕的一件事情（敲黑板，划重点）。



## 三、XML规范化

与XML签名有关的另一个方面是XML规范化（canonicalization）。XML规范化可以让逻辑上相等的两个XML文档在字节上拥有相同的表现形式。比如：

```
&lt;A X="1" Y="2"&gt;some text&lt;!-- and a comment --&gt;&lt;/A&gt;
```

以及

```
&lt; A Y="2" X="1" &gt;some text&lt;/ A &gt;
```

这两个XML文档拥有不同的字节表现形式，但传达的是相同的意思（也就是说这两者逻辑上相同）。

XML规范化操作先于签名操作进行，这样可以防止XML文档中一些无意义的差异导致不同的数字签名。这点很重要，所以我在这里强调一下：多个不同但相似的XML文档可以具备相同的签名。大多数情况下这是一件好事，具体哪些差异比较重要由规范化算法所决定。

在上面那个SAML Response中，你可能会注意到`CanonicalizationMethod`这个元素，该元素指定了签名文档之前所使用的规范化算法。[XML签名规范](https://www.w3.org/TR/xmldsig-core1/#sec-c14nAlg)中列出了几种算法，但实际上最常用的算法貌似是`http://www.w3.org/2001/10/xml-exc-c14n#`（我将其缩写为`exc-c14n`）

`exc-c14n`还有另一种变体，即`http://www.w3.org/2001/10/xml-exc-c14n#WithComments`。这款变体并不会忽略注释信息，因此前面我们给出的两个XML文档会得到不同的规范化表示形式。这两种算法的区别也是非常重要的一点。



## 四、XML API

该漏洞之所以存在，原因之一就在于不同的XML库（如Python的`lxml`或者Ruby的`REXML`）存在一些微妙且意料之外的处理方法。比如，考虑如下`NameID` XML元素：

```
&lt;NameID&gt;kludwig&lt;/NameID&gt;
```

如果你想从该元素中提取用户身份信息，在Python语言中，你可能会使用如下代码：

```
from defusedxml.lxml import fromstring
payload = "&lt;NameID&gt;kludwig&lt;/NameID&gt;"
data = fromstring(payload)
return data.text # should return 'kludwig'
```

这段不难理解吧，`.text`方法会提取出`NameID`元素所对应的文本。

现在，如果我稍微修改一下，往该元素中添加一点注释，会出现什么情况呢：

```
from defusedxml.lxml import fromstring
doc = "&lt;NameID&gt;klud&lt;!-- a comment? --&gt;wig&lt;/NameID&gt;"
data = fromstring(payload)
return data.text # should return ‘kludwig’?
```

如果你觉得即使添加了注释我们也能得到一样的结果，那么你和我还有很多人看到结果后都会大吃一惊，事实上`lxml`中的`.text` API返回的是`klud`！这是为什么呢？

我认为这里`lxml`的处理方式在技术层面上是正确的，虽然并不是那么直观。如果我们将XML文档看成一棵树，那么`XML`文档看上去如下所示：

```
element: NameID
|_ text: klud
|_ comment: a comment?
|_ text: wig
```

`lxml`并没有读取第一个`text`节点结束后的`text`节点。而没有添加注释的节点如下所示：

```
element: NameID
|_ text: kludwig
```

这种情况下，程序解析完第一个`text`节点后就不再处理也非常合理。

表现出类似行为的另一个XML解析库为Ruby的`REXML`库。根据`get_text`方法的[文档](https://ruby-doc.org/stdlib-2.2.3/libdoc/rexml/rdoc/REXML/Element.html#method-i-get_text)描述，我们就能理解为何这些XML API会表现出这种行为：

```
[get_text] 会返回第一个子Text节点，如果不存在则返回nil。该方法会返回实际的Text节点，而非String字符串内容。
```

如果所有的XML API都遵循这种处理方式，那么在第一个子节点后就停止提取文本虽然看起来并不直观，但可能不会造成任何问题。不幸的是情况并非如此，某些XML库虽然包含几乎相同的API，但提取文本的方式却并不相同：

```
import xml.etree.ElementTree as et
doc = "&lt;NameID&gt;klud&lt;!-- a comment? --&gt;wig&lt;/NameID&gt;"
data = et.fromstring(payload)
return data.text # returns 'kludwig'
```

我也碰到过一些实现方法，这些方法并没有利用XML API来实现这一功能，而是自己进行文本提取，简单地提取出第一个子节点中的文本，这也是子字符串文本提取的另一种方法。



## 五、漏洞说明

现在已经有3个因素能够触发该漏洞：

1、SAML Response中包含用来标识认证用户的字符串；

2、（大多数情况下）XML规范化处理会删除注释信息，不用于签名验证中，因此往SAML Response中添加注释并不会破坏签名有效性。

3、当包含注释信息时，XML文本提取过程可能只会返回XML元素中文本字符串的子串。

因此，当攻击者具备`[user@user.com.evil](mailto:user@user.com.evil).com`账户的访问权限时，就可以修改自己的SAML断言，在SP处理时将NameID修改为`[user@user.com](mailto:user@user.com)`。现在，只要在之前的SAML Response中添加7个字符，我们就能构造出攻击载荷，如下所示：

```
&lt;SAMLResponse&gt;
    &lt;Issuer&gt;https://idp.com/&lt;/Issuer&gt;
    &lt;Assertion ID="_id1234"&gt;
        &lt;Subject&gt;
            &lt;NameID&gt;user@user.com&lt;!----&gt;.evil.com&lt;/NameID&gt;
        &lt;/Subject&gt;
    &lt;/Assertion&gt;
    &lt;Signature&gt;
        &lt;SignedInfo&gt;
            &lt;CanonicalizationMethod Algorithm="xml-c14n11"/&gt;
            &lt;Reference URI="#_id1234"/&gt;
        &lt;/SignedInfo&gt;
        &lt;SignatureValue&gt;
            some base64 data that represents the signature of the assertion
        &lt;/SignatureValue&gt;
    &lt;/Signature&gt;
&lt;/SAMLResponse&gt;
```



## 六、如何影响

现在说一下具体影响。

出现这种行为并不是一件好事，但也并非总是能被成功利用。SAML IdP以及SP有各种配置选项，因此这一漏洞所能造成的实际影响范围也因人而异。

比如，如果某些SAML SP使用email地址并且验证域名是否位于白名单中，那么这种SP与那些使用任意字符串作为用户标识符的SP相比就更加安全一些。

对于IdP而言，向用户开放账户注册功能可能会使问题变得更加严重。手动管理用户账户注册会多一层安全屏障，使漏洞利用起来更加困难。



## 七、缓解措施

如何缓解这个漏洞在某种程度上取决于用户与SAML的具体关系。

### <a class="reference-link" name="Duo%E8%BD%AF%E4%BB%B6%E7%9A%84%E7%94%A8%E6%88%B7"></a>Duo软件的用户

Duo已经发布了1.2.10版[Duo Network Gateway](https://duo.com/docs/dng)的安全更新。如果你将DNG用作SAML服务提供商，尚未更新到1.2.10或者更新版本（目前1.2.10是最新版本），我们建议您及时升级。

大家可以参考Duo的[产品安全公告（PSA）](https://duo.com/labs/psa/duo-psa-2017-003)了解此漏洞的更多细节。

### <a class="reference-link" name="%E8%BF%90%E8%A1%8C%E6%88%96%E7%BB%B4%E6%8A%A4IdP%E6%88%96%E8%80%85SP%E7%9A%84%E7%94%A8%E6%88%B7"></a>运行或维护IdP或者SP的用户

最好的缓解措施就是确保处理SAML的库不受到此问题影响。我们发现了多个SAML库要么利用了不甚直观的XML API，要么自己错误实现了文本提取功能，但我相信还有更多的库没有很好地处理XML节点中的注释。

另一种可能的缓解措施就是默认采用不会忽略注释的规范化算法，比如`http://www.w3.org/2001/10/xml-exc-c14n#WithComments`。使用这种规范化算法后，攻击者添加的注释会破坏签名的有效性，但我们无法修改具体使用的规范化算法标识，想修改的话需要IdP以及SP的支持，这可能不是一种通用的缓解措施。

此外，如果你的SAML SP强制使用了[双因素身份认证](https://duo.com/resources/glossary/two-factor-authentication)机制，这种情况就比较安全，因为该漏洞只能让攻击者绕过用户的第一层身份认证机制。请注意，如果你的IdP同时负责第一层以及第二层身份认证，那么该漏洞很有可能会同时绕过这两层保护。

### <a class="reference-link" name="%E7%BB%B4%E6%8A%A4SAML%E5%A4%84%E7%90%86%E5%BA%93%E7%9A%84%E7%94%A8%E6%88%B7"></a>维护SAML处理库的用户

此时最显而易见的缓解措施是确保所使用的SAML库在处理带有注释的XML元素时，可以成功提取出该元素的全部文本。我发现大多数SAML库都具备某种形式的单元测试功能，并且想要更新测试也是非常方便的一件事情（比如提取像`NameIDS`之类的属性，在文档签名之前添加注释）。如果测试能够继续通过，那么一切顺利。否则，你可能就受到此漏洞影响。

另一种可能的缓解措施就是更新所使用的库，对于任何处理过程（如文本提取）都要在签名验证之后使用规范化的XML文档，这样就能防护此漏洞以及XML规范化过程所带来的其他漏洞。

### <a class="reference-link" name="%E7%BB%B4%E6%8A%A4XML%E8%A7%A3%E6%9E%90%E5%BA%93%E7%9A%84%E7%94%A8%E6%88%B7"></a>维护XML解析库的用户

从我个人角度来看，这么多程序库受到此漏洞影响表明许多用户认为XML内部文本API能够正常处理注释数据，而这种现象也敦促我们去修改那些API的处理机制。然而，我并不认为XML库开发者需要因此做出太大改动，他们可以采取比较合理措施，比如保持API现状，然后在文档中做出相应说明。

另一种缓解措施就是改进XML的标准。经过研究后，我并没有发现能够规范正确行为的任何标准，我们可能需要指定相关的这些标准如何协同工作。



## 八、时间线

大家可以参考[此处链接](https://www.duo.com/labs/disclosure)了解我们的漏洞披露策略。对于这个漏洞，由于影响多个厂商，我们决定与CERT/CC一起协商披露时间，具体时间线如下：

2017-12-18：联系CERT/CC，提供漏洞信息。

2017-12-20：CERT/CC及时跟进，询问了一些细节。

2017-12-22：回答CERT/CC提出的问题。

2018-01-02至2018-01：通过邮件与CERT/CC进一步讨论该问题。

2018-01-24：CERT/CC完成内部分析流程，通知受影响的厂商。

2018-01-25：厂商确认CERT/CC的报告。我们与CERT/CC以及相关厂商进一步沟通，进一步解释该问题以及其他攻击方法。

2018-01-29：CERT/CC确认了可能受此漏洞影响的其他厂商并与之联系。

2018-02-01：Duo Labs为每个受影响的厂商保留了CVE编号。

2018-02-06：Duo检查并确认了CERT/CC的漏洞技术备注草案。

2018-02-20：最后确认所有受影响的厂商已经做好漏洞披露准备。

2018-02-27：漏洞披露。

感谢CERT/CC帮助我们披露次漏洞，感谢CERT/CC联系的所有相关组织及人员能够快速响应此漏洞。
