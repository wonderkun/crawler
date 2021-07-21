> 原文链接: https://www.anquanke.com//post/id/179186 


# 滥用jQuery导致CSS时序攻击


                                阅读量   
                                **195489**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者portswigger，文章来源：portswigger.net
                                <br>原文地址：[https://portswigger.net/blog/abusing-jquery-for-css-powered-timing-attacks](https://portswigger.net/blog/abusing-jquery-for-css-powered-timing-attacks)

译文仅供参考，具体内容表达以及含义原文为准

vector illustrations of busy concepts, running out of time.



[亚瑟·萨夫尼斯（Arthur Saftnes）](https://twitter.com/ArthurSaftnes)去年发表了一篇非常棒的文章，介绍了他在[利用CSS选择器和Javascript进行时序攻击](https://blog.sheddow.xyz/css-timing-attack/)方面的研究成果。说实话，它可能是我去年最喜欢的一篇文章。

注：如果你是第一次接触这类攻击，为方便理解本文，请先阅读上面这篇博文。

网站通常会使用下面这个方法将`location.hash`传递给[jQuery $ function](https://api.jquery.com/jQuery/)：

```
$(location.hash);
```

攻击者有时可以控制hash值，并通常用来造成[XSS](https://portswigger.net/web-security/cross-site-scripting)，但jQuery在许多年已修复该漏洞。亚瑟发现该模块理论上仍可以被利用，从而导致时序攻击。你可以通过重复调用jQuery [:has selector](https://api.jquery.com/has-selector/)，然后注意目标页面中的内容的变化，判定对性能的影响。通过这点，攻击者可以把不可能造成XSS的情况转化为解析任意输入的端点。

于是我决定跟进这个研究，想要在外部网络中利用此技术找出一些漏洞。首先我把Burp Scaner修改为[动态分析](https://portswigger.net/blog/dynamic-analysis-of-javascript)，以寻找`hashchange`事件中正在执行的jQuery选择器，然后扫描了一堆网站。我选择`hashchange`这个事件的原因是该攻击的局限性；为判定对性能的影响你需要重复更改hash值，导入所有可能的字符进行二进制搜索，而这只有`hashchange`事件触发时才能运行。原先那篇博文的一个局限是：目前主流浏览器都会对站点hash进行URL-encode处理，所以你先要解码它——但我找到了解决该问题的方法。

我通过`hashchange`事件发现了一些使用`location.hash`和`jquery $ fuction`的Bug赏金项目站点，但找到的大部分站点没有令我感兴趣的数据，我没怎么窃取它们。Red Hat站点例外，它在`hashchange`事件中使用了jQuery选择器，并且站点启用了账户功能。查看Red Hat站点，找不到可以窃取数据的端点，但你会发现当你登入后确实会显示你的全名。亚瑟在攻击时使用了[CSS属性选择器](https://developer.mozilla.org/en-US/docs/Web/CSS/Attribute_selectors)但全名不会出现在任何输入的元素中，因此我不能套用他的方法。

我查看了所有jQuery CSS选择器，发现选择器[:contains](https://api.jquery.com/contains-selector/)可以找出包含指定字符的元素。不幸的是使用`:contains`看不到字符串的开头和末尾，所有我只能找别的方法提取。起初我想利用空格作为锚点来提取出姓名，但问题是Firefox会对空格进行URL编码。幸运的是，反斜杠不会进行URL-encode，所以我可以尝试CSS hex转义。刚开始我使用的是`20`，后来发现后续的字符也要进行hex转义，否则将破坏选择器，但如果我填充进字符`0`可以解决这个问题。我对亚瑟的利用代码稍加修改，添加了`make_selector`函数来解决空格的问题：

```
function make_selector(prefix, characters, firstNameFlag, firstName) `{`
 return characters.split("").map(c =&gt; !firstNameFlag ? SLOW_SELECTOR +
 SELECTOR_TEMPLATE.replace('`{``}`',  c + prefix + '\000020') : SLOW_SELECTOR +
 SELECTOR_TEMPLATE.replace("`{``}`",  prefix.replace(/ /, '\000020') + c))
                    .join(",");
`}`
```

这段代码通过hex编码了空格，帮助扫描出网页背后的名称。我使用了`firstNameFlag`，以区分出姓名和名字，找到姓名的大写字母后会设置标志，然后使用第一个名称作为前缀和空格继续扫描第二个字母，依次扫描出完整名称。

```
if(!firstNameFlag &amp;&amp; /[A-Z]/.test(name)) `{`
   firstNameFlag = true;
   name += ' ';
   backtracks = 0;
   continue;
`}`
```

我遇到了另一个问题，由于URL-encode的问题，我无法在选择器里使用空格，而且使用hex转义也不能解决问题。我想了很久，构建出下面这个没有空格仍可以判定对性能的影响的选择器：

```
const SLOW_SELECTOR="*:has(*:has(*):parent:has(*):parent:has(*):parent:has(*):parent:has(*)):parent:has(";
const SELECTOR_TEMPLATE=".account-user:contains('`{``}`'))";
```

这仍会导致性能问题，但比使用带有空格的[CSS descendant选择器](https://developer.mozilla.org/en-US/docs/Web/CSS/Descendant_combinator)要快一些。我面临的下一个问题是如何确定已经递归到名字的末尾。正如我前面提到的那样，我不能看到字符尾端。目前我想到的唯一方法是连续寻找6个回溯。

目前这个漏洞已经完全修复，所以我分享出我的原始Poc：

[Firefox access.redhat.com jQuery selector PoC](http://portswigger-labs.net/redhat_ZnF5463PdXj/poc.html)

我录制了一段Video，你可以通过视频详细地查看时序攻击的详情。

[Here is The Video.](https://portswigger.net/cms/videos/83/c2/64c9bfa331ce-video.mp4)
