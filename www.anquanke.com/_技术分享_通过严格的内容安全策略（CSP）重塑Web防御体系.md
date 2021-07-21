> 原文链接: https://www.anquanke.com//post/id/84655 


# 【技术分享】通过严格的内容安全策略（CSP）重塑Web防御体系


                                阅读量   
                                **128681**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://security.googleblog.com/2016/09/reshaping-web-defenses-with-strict.html](https://security.googleblog.com/2016/09/reshaping-web-defenses-with-strict.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01cc6436976485b1f6.jpg)](https://p0.ssl.qhimg.com/t01cc6436976485b1f6.jpg)

**<br>**

**写在前面的话**

在过去的十多年里，**跨站脚本（**[**XSS**](https://www.google.com/about/appsecurity/learning/xss/)**）一直都位于十大Web安全漏洞之列**。通过跨站脚本攻击，攻击者可以向一个受信任的Web应用中注入恶意脚本。根据[Google公司的漏洞奖励计划](https://www.google.com/about/appsecurity/reward-program/index.html)，安全研究专家如果在Google的应用程序中发现了跨站脚本漏洞并将其报告给Google，那么Google公司将会根据漏洞的等级提供一定数额的漏洞奖金。仅在过去的两年时间内，Google公司已经向那些报告XSS漏洞的研究人员提供了**超过一百二十万美元的漏洞奖励**。类似“严格的上下文隔离（SCE）”这样的现代Web技术不仅可以帮助开发人员避免Web应用受到跨站脚本攻击，而且还可以防止自动扫描器在测试过程中发现Web应用中的安全漏洞。但是在某些复杂的应用程序中，设计缺陷和安全漏洞都是难以避免的，而这些安全问题最终都将使得Web应用暴露于风险之中。在发现了这些漏洞之后，攻击者既可以进行有针对性的恶意攻击，也可以进行无伤大雅的恶作剧。

**<br>**

**内容安全策略（CSP）**

**内容安全策略（CSP）**是一种安全机制，当Web应用中出现跨站脚本漏洞时，就是内容安全策略该发挥作用的时候了。它可以帮助开发人员限制某些脚本的运行，这样一来，即便是攻击者可以向包含漏洞的页面注入HTML代码，他们也仍然无法加载恶意脚本和其他类型的恶意资源。除此之外，内容安全策略也是一种非常灵活的工具，在它的帮助下，**开发人员还可以设置大量的安全限制策略**。

[![](https://p3.ssl.qhimg.com/t013cb3f14ecdf88270.png)](https://p3.ssl.qhimg.com/t013cb3f14ecdf88270.png)

然而，CSP策略的灵活性是一把**双刃剑**，这种灵活性也有可能引起非常严重的问题：从表面上看，我们可以轻易地设置安全策略，而且这些策略似乎可以正常工作，但是它们却并没有提供应有的安全防护能力。在近期的一次研究中，我们对互联网中的十亿个站点进行了分析，并且发现在那些部署了CSP策略的站点中，**有大约95%的站点其CSP策略是无效的**，因为它们根本无法抵御跨站脚本攻击。其中的一个主要原因就是这些网站中的设置存在问题，开发人员允许网站加载外部脚本，而攻击者将可以绕过CSP策略的保护。所以我们认为现在应该带领大家重新审视一下内容安全策略，这是非常重要的，希望这篇文章可以帮助Web生态系统提升安全性，并让开发人员能够充分利用CSP策略的潜能。

<br>

**更加安全的CSP策略**

为了帮助开发人员设计出能够充分保护Web应用安全的策略，我先给大家介绍一款工具－[CSP Evaluator](https://csp-evaluator.withgoogle.com/)。这款工具可以帮助开发人员可视化地查看到一个策略设置后的运行效果，并且它还可以检测安全策略中存在的一些小问题。Google公司的安全工程师和Web应用开发人员可以使用CSP Evaluator来确保部署的安全策略能够达到预期的目标，并且确保攻击者无法绕过这些安全策略。在此之前，这款工具仅供Google公司的内部人员使用，但是现在我们将其公布出来了，**任何人都可以使用CSP Evaluator来检测自己CSP策略的有效性**。

[![](https://p4.ssl.qhimg.com/t01d0ce152b8319fb75.png)](https://p4.ssl.qhimg.com/t01d0ce152b8319fb75.png)

由于目前很多热门站点中都加载了大量十分复杂的Web应用，而这些资源使得攻击者可以绕过内容安全策略的限制。所以即便我们有这款强大工具的帮助，也仍然难以为复杂的Web应用构建出一个安全的脚本白名单。在这种情况下，安全研究人员就提出了一种**基于随机数（nonce-based）的内容安全策略**。与之前的脚本白名单机制不同，它需要对应用程序进行简单的修改，让Web应用根据一个随机token（令牌）来判断脚本是否可信任。它会为脚本分配一个**不可预测的一次性token**，这个token的值必须与内容安全策略中定义的值相匹配：

```
Content-Security-Policy: script-src 'nonce-random123'
&lt;script nonce='random123'&gt;('This script will run')&lt;/script&gt;
&lt;script&gt;('Will not run: missing nonce')&lt;/script&gt;
&lt;script nonce='bad123'&gt;("Won't run: invalid nonce")&lt;/script&gt;
```

‘**strict-dynamic**’是CSP3规范中定义的一个参数，目前Chrome和Opera浏览器已经开始支持使用‘strict-dynamic’了（火狐浏览器也将支持该参数）。这样一来，在它的帮助下，向复杂的现代Web应用中添加安全策略将会变得更加容易。现在，开发人员可以直接设置一个如下所示的简单策略：

```
script-src 'nonce-random123' 'strict-dynamic'; object-src 'none'
```

这样就可以确保所有的静态&lt;script&gt;元素都**包含有一个相匹配的nonce参数**了。在很多情况下，我们只需要添加这样一行简单的代码，就可以保护Web应用免受XSS攻击的侵害，因为‘strict-dynamic’可以帮助开发人员在Web应用的运行过程中动态加载受信任的脚本。需要注意的是，通过这种方式所设置的策略是**完全向下兼容**的，所有能够识别CSP策略的浏览器都支持这样的设置方式。除此之外，它也能够与Web应用中的传统CSP策略完美兼容。除了功能性的提升之外，这种方式也简化了CSP策略的定义和部署过程。

<br>

**采用严格的内容安全策略**

在过去的几个月内，我们已经在好几个大型的Google应用程序中部署了这种方法，包括[Cloud Console](https://console.developers.google.com/)、[Photos](https://photos.google.com/)、[History](https://myactivity.google.com/myactivity)、[Careers Search](https://www.google.com/about/careers/jobs)、[Maps Timeline](https://www.google.com/maps/timeline)、以及[Cultural Institute](https://www.google.com/culturalinstitute/)等服务，我们目前也正在努力向其他的Google应用中添加这种安全策略。我们相信这种方法同样可以帮助其他的开发人员，所以我们专门发布了一篇文章来详细介绍CSP策略的最佳实践方式。我们在文章中介绍了CSP策略的优势，并且给出了很多设置参考样本［[文章传送门](https://csp.withgoogle.com/docs/strict-csp.html)］。

除此之外，我们还给大家提供了一款名为“**CSP Mitigator**”的Chrome插件，这款插件可以帮助开发人员检查一款Web应用程序是否可以使用基于随机数的内容安全策略。除此之外，这款插件还可以帮助开发人员配置CSP策略，当某一款Web应用需要重构才可以支持CSP策略时，它可以为开发人员提供相应的参考数据。

[![](https://p3.ssl.qhimg.com/t01d4b6001eeacc9615.png)](https://p3.ssl.qhimg.com/t01d4b6001eeacc9615.png)

**如果要采用严格的内容安全策略，大多数Web应用程序都需要进行以下修改：**

1.在所有的&lt;script&gt;元素中添加一个“nonce”属性。某些模版系统可以[自动](https://developers.google.com/closure/templates/docs/security#content_security_policy)完成这一修改操作。

2.对内联处理事件进行重构，例如“onclick”和“”等等。

3.在加载任何一个页面时，生成一个新的nonce（一次性随机数），并将其发送给模版系统，然后在“Content-Security-Policy”响应头中使用这个值。

<br>

**我们鼓励各位开发人员使用严格的内容安全策略**

现在，我们已经将研究人员对CSP策略的优化和提升努力纳入了补丁奖励计划的范畴。如果你可以帮助流行的开源Web框架适配基于随机数的内容安全策略，你将有机会获得奖励。我们希望增加Web开发人员对这一领域的关注，我们也希望安全研究专家能够设计出新的方法来绕过这种CSP策略的限制，并帮助我们提升这种机制的安全度。因为只有大家共同努力，才能最大程度地保护互联网用户的安全。

如果各位读者对这篇文章有任何的疑问，请不要犹豫，赶紧联系我们（[more-csp@google.com](mailto:more-csp@google.com)）。
