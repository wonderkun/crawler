> 原文链接: https://www.anquanke.com//post/id/234936 


# DuckDuckGo Privacy Essentials漏洞分析：不安全的通信和通用XSS


                                阅读量   
                                **83835**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者palant，文章来源：palant.info
                                <br>原文地址：[https://palant.info/2021/03/15/duckduckgo-privacy-essentials-vulnerabilities-insecure-communication-and-universal-xss/﻿](https://palant.info/2021/03/15/duckduckgo-privacy-essentials-vulnerabilities-insecure-communication-and-universal-xss/%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t011c037d38f6626785.png)](https://p1.ssl.qhimg.com/t011c037d38f6626785.png)



## 写在前面的话

几个月前，我研究了DuckDuckGo Privacy Essentials组件的内部工作原理，这是一种流行的浏览器扩展，旨在保护其用户的隐私。我在其中发现了一些普遍存在的安全问题，但也发现了两个实际的安全漏洞。首先，扩展使用了不安全的通信信道来进行内部通信，这将导致出现越界数据泄漏。而第二个漏洞将使DuckDuckGo服务器的权限比预期的要多：扩展中的跨站点脚本（XSS）漏洞允许此服务器在任何域上执行任意JavaScript代码。

这两个问题都在DuckDuckGo Privacy Essentials 2021.2.3及更新版本中得到了解决。在撰写本文时，此技术仅适用于Google Chrome。由于某些原因，Mozilla Firefox和Microsoft Edge跳过了两个版本，因此此处提供的最新版本只修复了第一个问题，即不安全的内部通信。

更新（2021-03-16）：现在Firefox和Edge都可以使用带有修复程序的扩展版本。

[![](https://p4.ssl.qhimg.com/t01ee2aa4da3e1b7f20.jpg)](https://p4.ssl.qhimg.com/t01ee2aa4da3e1b7f20.jpg)

这些漏洞基本上算是很常见的了，我在其他扩展中也见过类似的错误，而这并不仅仅是扩展开发人员技术上的不成熟所导致的，Google Chrome引入的扩展平台根本没有提供安全和方便的替代方案，所以大多数扩展开发人员在第一次尝试时肯定会出错。



## 关于DuckDuckGo

DuckDuckGo是一个互联网搜寻引擎，其总部位于美国宾州Valley Forge市。DuckDuckGo强调在传统搜寻引擎的基础上引入各大Web 2.0站点 的内容。其办站哲学主张维护使用者的隐私权，并承诺不监控、不记录使用者的搜寻内容。

DuckDuckGo主要基于各大型搜索服务商（比如Yahoo! Search BOSS）的APIs，因此，TechCrunch 认为DuckDuckGo是一个“混合”搜索引擎在使用别的搜索引擎的API时，DuckDuckGo也会提供自己的内容页，就像Mahalo，Kosmix 和 SearchMe这些网站一样。

传统搜索引擎为了优化搜索结果，必须对用户数据进行尽量全面的收集和分析，这是对用户隐私的一种侵犯。而 DuckDuckGo 则成功地避开了这样的缺陷。在 DuckDuckGo 的隐私政策中非常明确的声明网站不会记录用户的浏览器 UA、IP 地址、搜索行为等任何相关数据，默认情况下也不会使用 Cookie 来记录数据。此外，DuckDuckGo 还对用户点击搜索结果后跳转到目标网页的过程进行了重定向处理，目标网站无法获知用户是通过输入哪些搜索词跳转到自己的网站。这进一步保护了用户的隐私安全。同时，DuckDuckGo 鼓励用户使用 Firefox 浏览器的强制 https 扩展和 Tor 匿名网络等方式来保护自己的隐私，而 DuckDuckGo 自身也运营着一个 Tor 的跳出节点，以便用户在使用相对速度较慢的 Tor 匿名网络时也能够快速而安全地访问 DuckDuckGo 进行搜索。

越来越多的用户最终会选择 DuckDuckGo，不仅是因为它对隐私的全面保护，更是因为它拥有更好的体验。



## 另一个关于window.postMessage被滥用的例子

如果你在浏览器扩展的内容脚本中看到了代码调用window.postMessage()的话，这就非常危险了，因为大多数开发人员都很难以安全的方式去调用它。这样一来，任何通信都将在网页上可见，并且无法区分合法消息和网页发送的消息。当然，这并不能阻止扩展的开发人员去努力尝试，因为与安全扩展API相比，这个API非常方便。

如果是DuckDuckGo Privacy Essentials，内容脚本element-hiding.js使用了这个方法来跟标签中不同的frame进行协同交互。当一个新的frame被加载时，它会向顶层frame发送一个frameIdRequest消息。此时的内容脚本将会回复下列信息：

```
if (event.data.type === 'frameIdRequest') `{`
    document.querySelectorAll('iframe').forEach((frame) = &gt;`{`
        if (frame.id &amp;&amp; !frame.className.includes('ddg-hidden') &amp;&amp; frame.src) `{`
            frame.contentWindow.postMessage(`{`
                frameId: frame.id,
                mainFrameUrl: document.location.href,
                type: 'setFrameId'
            `}`,
            '*')
        `}`
    `}`)
`}`
```

虽然这种通信是为了在frame中加载的内容脚本而设计的，而且我们也可以在网页中看到这部分内容。如果该网页属于另一个域，则会泄漏两条它本不应该知道的数据：其父frame的完整地址和加载它的&lt;iframe&gt;标记的id属性。

另一段代码负责隐藏屏蔽的frame以减少视觉上的混乱。这是通过发送hideFrame消息完成的，处理它的代码如下所示：

```
if (event.data.type === 'hideFrame') `{`
    let frame = document.getElementById(event.data.frameId) this.collapseDomNode(frame)
`}`
```

别忘了，这可不是一条隐私通信信道。如果没有任何信息源检查，任何网站都可能发送此消息。它可能是同一个标签页中的不同frame，甚至可能是打开此弹出窗口的页面。这个代码只接受消息并隐藏一些文档元素，甚至没有验证它是否是iframe标签，这将导致点击劫持攻击的实现变得更加简单。

DuckDuckGo通过完全删除此内容脚本来解决这个问题，这个方案可还行！



## 为什么在编写JavaScript时一定要小心？

当扩展动态加载内容脚本时，tabs.executeScript() API允许他们将JavaScript代码指定为字符串。遗憾的是，由于这个API没有其他方式将配置数据传递给静态脚本文件，所以使用这个特性有时是不可避免的。但是，需要特别注意的是，如果你将不受信任源中的数据嵌入到代码中的话，那么这里将没有内容安全策略来保护你的安全。

DuckDuckGo Privacy Essentials中存在安全问题的代码如下所示：

```
var variableScript = `{`
    'runAt': 'document_start',
    'allFrames': true,
    'matchAboutBlank': true,
    'code': try `{`
        var ddg_ext_ua = ’$ `{`
            agentSpoofer.getAgent()
        `}`’
    `}` catch(e) `{``}`
`}`;
chrome.tabs.executeScript(details.tabId, variableScript);
```

需要注意的是，agentSpoofer.getAgent()被插入在该脚本中时，并没有任何的转义或者数据清洗。这些数据可信吗？某种程度上，用于判断欺骗用户代理的数据是从staticcdn.duckduckgo.com下载的。因此好消息就是，你访问的网站并不能去篡改它。但坏消息就是，这些数据可能被DuckDuckGo、微软（托管提供商）或其他任何访问该服务器的人（黑客或政府机构）所操纵。

如果有人设法破坏了这些数据（对单个用户或所有用户而言），其影响将是巨大的。首先，这将允许在用户访问的任何网站的上下文中执行任意JavaScript代码，即通用跨站脚本攻击。但是内容脚本也可以将消息发送到扩展的后台页面。在这里，后台页面将对`{`getTab:1`}`（检索有关用户标签页的信息）和`{`updateset:`{`name:“activeexperience”、value:“2”`}`（更改扩展设置）等消息作出反应。

在我的建议之下，存在安全问题的代码已经改为使用JSON.stringify()了：

```
'code': try `{`
    var ddg_ext_ua = $ `{`
        JSON.stringify(agentSpoofer.getAgent())
    `}`
`}` catch(e) `{``}`
```

这个调用将正确地编码任何数据，这样就可以安全地插入JavaScript代码了。这里唯一的问题就在于，如果将JSON编码的数据插入到&lt;script&gt;标记中，则需要注意数据中的&lt;/script&gt;。您可以通过在调用JSON.stringify()后转义前斜杠以避免此问题。



## 对扩展平台有何影响？

我听说Google正在研发Manivest v3以使他们的扩展平台更加安全。虽然这些变化肯定会有所帮助，但如果没有更加方便的安全API，那么扩展开发人员将不可避免地去继续使用不安全的替代方案。

比如说，扩展开发人员将不断去使用window.postMessage() 来进行内部沟通。我也清楚为了保证所有内容都是安全的，那么runtime.sendMessage()就是其中必须的。但是当你想给另一个frame发送消息时，浏览后台页面是非常不方便的，正确地执行它需要大量的样板代码。因此，也许可以在扩展平台中添加一个API来在同一个标签页中的内容脚本之间进行通信，即使它只是一个runtime.sendMessage()的封装器？

另一个问题在于tabs.executeScript()中的代码参数，从安全角度看，这是一把真正不应该存在的“武器”。它只有一个合法的用例，即将配置数据传递给内容脚本。那么，如何扩展API以将配置对象与脚本文件一起传递呢？是的，同样的效果也可以通过消息交换来实现，但这会使事情复杂化，并引入时间问题，这就是为什么扩展开发人员经常选择捷径的原因。

[![](https://p0.ssl.qhimg.com/t015a79e97db3277ed2.png)](https://p0.ssl.qhimg.com/t015a79e97db3277ed2.png)
