> 原文链接: https://www.anquanke.com//post/id/85119 


# 【技术分享】Microsoft Edge UXSS ——冒险在无尽的世界


                                阅读量   
                                **100841**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：brokenbrowser.com
                                <br>原文地址：[https://www.brokenbrowser.com/uxss-edge-domainless-world/](https://www.brokenbrowser.com/uxss-edge-domainless-world/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p3.ssl.qhimg.com/t0103dce6a99a52f888.png)](https://p3.ssl.qhimg.com/t0103dce6a99a52f888.png)

翻译：[scriptkid](http://bobao.360.cn/member/contribute?uid=2529059652)

预估稿费：260RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**前言**



今天我们将一起来围观下Microsoft Edge存在的一些设计上的问题——当这些问题组合在一起时就会形成通用跨站脚本攻击（UXSS）。如果你想弄明白这个漏洞，但你又恰好不是安全研究员的话，你可以尝试这么理解：当你访问一个恶意站点时，攻击者可以获取你的cookie、更改你所看见的页面内容以及窃取你的个人信息等。除此之外，因为Microsoft Edge使用受保护的[内部资源](https://www.brokenbrowser.com/spoof-addressbar-malware/)来实现某些特殊功能，攻击者也有获取这些资源和更改Edge配置的潜在可能。

此处提供两个演示视频：[导出bing的cookies](http://player.youku.com/embed/XMTg2NDYxMjgzMg==)和[篡改nature.com显示内容](http://player.youku.com/embed/XMTg2NDYxNjc4OA==)。需要注意的是，这两个网站本身是不存在问题的，漏洞纯粹是由Microsoft Edge浏览器导致的。接下来我们一起看看这是怎么做到的。



导出bing的cookies

<br>



篡改nature.com显示内容

<br>

<br>

**Domainless World**



about:blank是一条很特殊的URL——经常让人为其所属域名感到困惑。我们来思考下以下问题：假如我们当前URL地址是www.magicmac.com/dom/index.html，那么毫无疑问document.domain的值应该为www.magicmac.com，但是如果把地址换成了about:blank呢？这就要看情况了。理论上来说，document.domain应该是取决于其referer的值。举个例子：我们在www.magicmac.com下点击了about:blank的链接，这时about:blank将使用www.magicmac.com作为其域名。

[![](https://p0.ssl.qhimg.com/t0158ab709cc2f7ecb0.png)](https://p0.ssl.qhimg.com/t0158ab709cc2f7ecb0.png)

接着再举个iframe的src值显示指向about:blank或者为空时的例子：

[![](https://p4.ssl.qhimg.com/t01e456553c4ce52ef3.png)](https://p4.ssl.qhimg.com/t01e456553c4ce52ef3.png)

因此，虽然从goodfellas.com加载的about:blank跟从evil.com加载的看起来很像（URL是一样的），但是它们却无法互相访问，因为它们的document.domain是不一样的。

那么问题来了，我们直接在地址栏中输入的about:blank的对应域名是啥？这是个很关键的问题，所以我将在DevTools中放大一点让你看得更清楚。

[![](https://p5.ssl.qhimg.com/t0137ecb3d2aac36884.png)](https://p5.ssl.qhimg.com/t0137ecb3d2aac36884.png)

从图片可以看出，document.domain值是一个特殊的值——空值，接下来我们姑且称document.domain是空值的为"domainless"，同时，称不是空值的为"domained"，接下来的部分将是本文最重要的部分。

<br>

**domainless的about:blank将可以访问任意domained的about:blank**



换句话说就是，domainless的about:blank可以无视任何限制对domained的about:blank进行访问，下面我们通过控制台快速添加个指向bing.com的iframe进行简单演示。

```
document.body.innerHTML = '&lt;iframe src="http://www.bing.com/images/search?q=microsoft+edge"&gt;&lt;/iframe&gt;'
```

[![](https://p1.ssl.qhimg.com/t011740182be7135211.png)](https://p1.ssl.qhimg.com/t011740182be7135211.png)

现在我们成功在顶层的domainless blank中嵌入了一个指向bing.com的frame，不过我们的目标是找到一个bing内部的blank iframe，因为我们说的是domainless blank（这里是主窗口）能够对domained blank（这里是bing.com中的指向blank的iframe）进行存取。当然，在这个例子中我们很容易就能做到，因为bing.com中已经存在了blank iframes。不管怎样，我们都动手尝试下。正常情况下，下面的命令即使是在debugger中依旧会抛出access denied的错误，但是因为这里的top是domainless，所以我们这里成功执行了，见下图。

```
window[0][0].location.href = "javascript:alert(parent.document.domain)";
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01dd8fd9d8f77840b4.png)

当然，你可能会觉得这没什么，因为我们是在DevTools中做到的。但是，我却认为这是最重要的，因为如果我们抓住了这个要点，那么寻找新的UXSS漏洞将在一定程度上变得简单。现在，我们只要找到能够对domainless blank（通常是about:blank，但我们也可以使用其他方式）进行存取的方式，我们就找到了UXSS漏洞。前面之所以会在DevTools下进行是因为要确保能够完全理解我们所做的一切，而事实上我们并不需要DevTools!

<br>

**无需DevTools的独立POC**



接下来我们就开始吧！我们需要找到一种创建在常规web页面中创建可访问的domainless站点，最简单的就是通过data:URI来取代about:blank。这里需要注意的是，当我们在iframe里面加载data:URI时，它的domain值将与referer的一致（跟我们前面提到的about:blank一样），而如果我们尝试在最顶层加载data:URI，Edge将会拒绝访问并扔给我们一个错误页。

不过，我们有一些小技巧可以用来获取domainless的data:URI，这里我们将通过一个非常简单的Flash来实现。事实上，我从2005年开始就在使用这个Flash，所做的仅仅是通过请求字符串来设置URL。

```
&lt;iframe src="geturl.swf?target=_top&amp;redir=data:,[html/script goes here]"&gt;&lt;/iframe&gt;
```

看，就是这么简单！只需要将你需要加载的URL添加到参数redir后面就行了。在这个例子中，我们使用的是data:URI，当然，为了欺骗Edge，我们需要在iframe内部加载swf文件，否则会出现错误。顺便提一下，我们还可以使用其他方式来达到同样的目的，我们之所以使用这个方法纯粹是因为这是我们发现的第一种方式。Adobe的小伙伴多半会通过[将data:uri加入黑名单来帮助Edge的小伙伴解决这个bug](https://www.brokenbrowser.com/on-patching-security-bugs/)，然而，我们还可以通过不需要flash文件的其他多种途径来达到同样的目的。

由于我们现在处于domainless窗口下，我们可以注入一个指向bing.com的iframe，而Edge却无法正确渲染页面元素。如果我们尝试使用createElement/insertAdjacentHtml等方法，Edge将生成一个无法使用的iframe，就如一辆汽车没有发动机一样。为了解决这个问题，我们将使用document.write重写来强制使浏览器重新渲染整个页面。由于我们是处于domainless状态的URL下，document.write将会使我们保持在相同的domain下。

```
document.write('&lt;iframe src="http://www.bing.com/images"&gt;&lt;/iframe&gt;');
```

Perfect！现在我们可以对bing的blank iframe进行访问了，但是要记住我们是非常幸运的，因为不是所有的站点都会自带blank iframe。

```
window[0][0].location.href = "javascript:alert(parent.document.cookie)";
```

[![](https://p1.ssl.qhimg.com/t01caa05a4ce841131c.png)](https://p1.ssl.qhimg.com/t01caa05a4ce841131c.png)

<br>

**Owning non-cooperative sites**



你可能会觉得是因为bing为我们提供了许多的blank iframe所以才能那么轻松地取得成功，好吧，没错，大部分网站正常情况下是不会为我们放置好blank iframe的，所以我们需要再进一步深入。回头再看下我们前面提到的第二步，假设我们的iframe正确渲染但是指向了nature.com（nature不存在blank iframe），这时如果我们尝试去修改iframe的location，Edge将会拒绝访问并新开一个窗口来代替，也就是说，执行以下内容是没有什么卵用的。

```
// We are inside a domainless data: so Edge will open a new// window instead of changing nature-iframe's locationwindow[0][0].location.href = "about:blank";
```

上述代码并不起作用，也许存在一些方式可以绕过，但是我已经懒得再去尝试了。这确实是一个问题，但是我们可以通过新开一个带正常URL的窗口来解决，以下为具体步骤：

1、打开一个带指向nature.com的frame的新窗口

2、修改nature的内部iframe的location为about:blank，这样我们就可以对其命名，没错，就是要给iframe命名

3、为指向about:blank的iframe命名，这样我们的新开窗口就可以通过window.open来对其进行访问。不要忘了，我们现在处于一个正常的URL内部的窗口中，真正能做到的是我们的新开页。我们将通过如window.name=“DAVID_COPPERFIELD”来对iframe进行命名

4、现在我们应该修改nature的location为about:blank了。我们将通过meta-refresh来修改location，这个小技巧用于确保父层的domain被修改为about:blank

5、最后就是告诉新开页一切准备就绪可以行动了，就像这样：

```
window.open(“javascript:alert(document.domain)”, “DAVID_COPPERFIELD”);
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01dd3aa60004da43b6.png)

**总结**



我们又一次成功了！POC都是交互性的因此我们可以很清楚自己每一步都做了什么。但是，请认真阅读并理解代码中的一些细节部分，我相信还有很多可以提升的地方。最后附上所有你可能需要的[文件](https://goo.gl/a1cvXI)。


