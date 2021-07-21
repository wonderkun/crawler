> 原文链接: https://www.anquanke.com//post/id/86933 


# 【技术分享】深入分析IE地址栏内容泄露漏洞


                                阅读量   
                                **76906**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：brokenbrowser.com
                                <br>原文地址：[https://www.brokenbrowser.com/revealing-the-content-of-the-address-bar-ie/](https://www.brokenbrowser.com/revealing-the-content-of-the-address-bar-ie/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01f8cc35458816eea8.png)](https://p0.ssl.qhimg.com/t01f8cc35458816eea8.png)

译者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：180RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<a></a>

**前言**

在本文中，我们探讨的对象是**IE浏览器**，尽管该浏览器略显老态，但是其用户还是很多的，所以不容忽视。我最近对**MSRC**感到很欣喜，因为他们正在将工作重心移至Edge浏览器、设计漏洞，甚至提高了漏洞赏金，这看起来确实不错。

所有这些都是好消息，但我仍然认为现在就急着抛弃IE还为时尚早。例如，现在所有的IE用户在zombie脚本漏洞（已经公开数月，但是仍然尚未得到修补）面前都可能变成僵尸程序。千万不要忽视这个问题的严重性，请想象一下攻击者可以做什么：他们可以一直潜伏在你的浏览器中，当你浏览其他网站的时候，他们就有足够的时间做一些见不得光的事情，比如挖掘数字货币等。此外，IE的阻止弹出窗口功能已经被完全攻陷了，但是好像并没有引起人们的注意。总之，我认为这些漏洞应该得到修补，或至少给IE用户一个醒目的警告，比如“我们不再支持这个浏览器，请使用Microsoft Edge”。

在我看来，微软正在试图摆脱IE，这个毫无疑问。不过，如果直接告诉用户他们的旧版浏览器没有像Edge那样得到足够的维护会显得更诚实一些。根据Netmarketshare的统计显示，IE仍比Edge更受欢迎，两者用户之比是17％ vs 6％。

我坚信在安全方面IE应该像Edge那样得到同等的对待，否则就应该完全放弃它。但是不管未来怎样，我们现在先来探讨一下IE上的另一个漏洞：允许攻击者知道用户将要浏览的地址。什么，这是读心术吗？不，当然不是，下面让我们来看看IE是如何让攻击者做出魔幻般的事情的。 

**<br>**

**摘要**

当脚本在object-html标签内执行时，位置对象将获得焦点并返回主位置，而不是它自己的位置。 确切地说，它将返回写入地址栏中的文本。如果读者是急性子的话，可以先观看视频，了解一下攻击者是如何读取用户输入到IE地址栏内的内容的！

**<br>**

**对象和文档模式**

对象标签的行为方式取决于documentMode的渲染方式。 例如，如果我们在页面的开头添加兼容性元标记的话，它的外观和行为就像一个iframe，但它会认为这是一个顶层窗口。



```
&lt;head&gt;
  &lt;!-- COMPATIBILITY META TAG --&gt;
  &lt;meta http-equiv="X-UA-Compatible" content="IE=8" /&gt;
&lt;/head&gt;
&lt;object data="obj.html" type="text/html"&gt;&lt;/object&gt;
 
&lt;head&gt;
  &lt;!-- COMPATIBILITY META TAG --&gt;
  &lt;meta http-equiv="X-UA-Compatible" content="IE=8" /&gt;
&lt;/head&gt;
&lt;object data="obj.html" type="text/html"&gt;&lt;/object&gt;
```

在上面的代码中，“obj.html”在对象内部进行渲染，并且其内容被放入与iframe类似的方框中，然而，虽然在窗口对象与顶层对象进行比较时返回值为true，但是它并非顶层窗口。我们可以看一下在对象标签内执行的代码：虽然它认为window == top，但是事实并非如此。

[![](https://p3.ssl.qhimg.com/t01b4780297f5bc3345.png)](https://p3.ssl.qhimg.com/t01b4780297f5bc3345.png)

[在IE上进行测试](https://www.cracking.com.ar/demos/ieaddressbarguess/docmode8.html)<br>

我们的对象认为它是顶层窗口，甚至其他frameElement之类的成员也总是返回null——这种行为只出现在（IE的）顶层窗口中。

下面，让我们尝试相同的代码在没有兼容性标签的情况下会怎样。这时，该对象就能了解它所在的位置了，并且其行为类似于iframe。



```
&lt;!-- COMPATIBILITY META TAG REMOVED --&gt;
&lt;object data="obj.html" type="text/html"&gt;&lt;/object&gt;
 
&lt;!-- COMPATIBILITY META TAG REMOVED --&gt;
&lt;object data="obj.html" type="text/html"&gt;&lt;/object&gt;
```

[![](https://p3.ssl.qhimg.com/t016e4295714b2adab9.png)](https://p3.ssl.qhimg.com/t016e4295714b2adab9.png)

[在IE上进行测试](https://www.cracking.com.ar/demos/ieaddressbarguess/docmode11.html)<br>

本质上，该对象在较旧的文档模式中被渲染为一个独立的实体，但在一个较新的文档模式中将被渲染为一个iframe。无论如何，在内部它们都是WebBrowser控件，所以Trident引擎会暴露相同的成员。

**<br>**

**继承的窗口成员**

让我们重新回到较旧的documentMode，寻找一种利用这个混淆漏洞的方法，不过事情貌似并不那么糟糕，因为跨域限制仍然存在，而且X-FRAME-OPTIONS头部的工作效果非常好。 有一些成员，如window.name，它们是通过对象继承得到的（该对象会继承其父对象的名称），不过这也不是太糟糕——但是某些广告技术会全地使用window.name来跨iframe传递信息，这种做法是很危险的。

话虽如此，至少有一个继承的对象真的会引起麻烦：位置。在对象标签内，location.href将返回主（顶层）窗口的位置。下面的代码将其对象的源指向object_location.html，但是当我们检索它的位置时，它返回的是顶层窗口。

[![](https://p1.ssl.qhimg.com/t011b7a517c78dbfd0c.png)](https://p1.ssl.qhimg.com/t011b7a517c78dbfd0c.png)

[在IE上进行测试](https://www.cracking.com.ar/demos/ieaddressbarguess/top_location.html)<br>

再次重申，这个混淆漏洞本身是没有用的，因为我们仍然在同一个域。即使我们可以找到一个顶层的位置，只要我们在同一个域，那也没有多大意思。为此，我尝试改变对象的位置，但没有成功。如果你想在这个领域进行研究，我建议可以更深入一些，因为我认为会有更多的可能性。无论如何，在尝试实现UXSS（持久性是现实攻击中一切的关键）时，我获得了一个惊喜：当对象被注入到onbeforeunload时，我们得到的不再是顶层窗口的位置，而是浏览器的将要到达的位置或当前写入地址栏的内容。

换句话说，如果我们在用户离开主页面的同时检索对象的location.href，我们将能够知道她在地址栏中输入的内容，或者如果点击链接，我们将会获悉浏览器要链接的地址。

这里，我们只是中断新站点的加载并展示用户的URL。当然，如果是攻击者的话，他们会直接回填地址并加载站点，并且这一切对于用户来说都是透明的。实际上，在用户离开时，我们直接执行document.write就行了。



```
window.onbeforeunload = function()
`{`
  document.write('&lt;object data="loc.html" type="text/html" width="800" height="300"&gt;&lt;/object&gt;');
  document.close();
`}`
 
window.onbeforeunload = function()
`{`
  document.write('&lt;object data="loc.html" type="text/html" width="800" height="300"&gt;&lt;/object&gt;');
  document.close();
`}`
```

并在那个恰当的时刻读取位置（onbeforeunload）。

```
document.write("Let me read your mind. You wanted to go here: " + location.href +);
```

好了，现在我们就能在用户离开时获取对象位置，从而确切地知道她在地址栏中输入的内容。当然，它不一定是一个完整的URL，例如，如果用户在地址栏中输入单词，它将自动被转换为搜索查询URL（IE默认为Bing），这当然可以被完整读取！

[![](https://p2.ssl.qhimg.com/t0158a81787529812ec.png)](https://p2.ssl.qhimg.com/t0158a81787529812ec.png)

[在IE上进行测试](https://www.cracking.com.ar/demos/ieaddressbarguess/)**<br>**

**<br>**

**视频演示**

****

**结束语**

祝阅读愉快，并希望读者针对这个漏洞进行更深入的挖掘，我相信你们会有更多的新发现！

<br>
