> 原文链接: https://www.anquanke.com//post/id/86838 


# 【技术分享】如何绕过Edge、Chrome和Safari的内容安全策略


                                阅读量   
                                **155591**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：talosintelligence.com
                                <br>原文地址：[http://blog.talosintelligence.com/2017/09/vulnerability-spotlight-content.html](http://blog.talosintelligence.com/2017/09/vulnerability-spotlight-content.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0122a9629af9fc1731.jpg)](https://p5.ssl.qhimg.com/t0122a9629af9fc1731.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：180RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**一、前言**

****

2017年9月6日，Talos公布了一个浏览器漏洞细节，这个漏洞存在于Microsoft Edge浏览器、老版本的Google Chrome浏览器（[CVE-2017-5033](https://chromereleases.googleblog.com/2017/03/stable-channel-update-for-desktop.html)）以及基于Webkit的浏览器（如Apple Safari，[CVE-2017-2419](https://support.apple.com/en-ca/HT207600)）中。利用这个漏洞，攻击者可以绕过服务器设置的内容安全策略（Content Security Policy，CSP），最终可能会导致隐私信息泄露。微软表示这属于设计理念的问题，拒绝修复这个漏洞。

<br>

**二、概述**

****

Web应用中有许多基本的安全机制，其中一个是同源（same-origin）策略机制，该机制规定了应用程序代码可以访问的资源范围。同源策略的基本思想是，源自于某台服务器上的代码只能访问同一台服务器上的web资源。

比如，在Web浏览器上下文中执行的某个脚本，如果其来源服务器为**good.example.com**，那么它就可以访问同一台服务器上的数据资源。另一方面，根据同源策略的思想，来自**evil.example.com**的另一个脚本不能访问**good.example.com**上的任何数据。

然而，web应用中存在许多漏洞，利用这些漏洞，攻击者可以绕过同源策略的限制，这一点已经被许多事实证明。其中最为典型也最为有效的一种攻击技术是[跨站脚本（Cross Site Scripting，XSS）](https://www.owasp.org/index.php/Cross-site_Scripting_(XSS))技术。利用XSS技术，攻击者可以在浏览器正在执行的原始服务器代码的上下文中插入远程代码。从浏览器角度来看，插入的代码看起来与合法应用一样，都源自同一个服务器，因此就会允许这些代码访问本地资源，最终将隐私数据泄露给攻击者，甚至会出现应用会话劫持现象。

[内容安全策略（Content Security Policy，CSP）](https://www.w3.org/TR/2012/CR-CSP-20121115/)是防御XSS攻击的一种安全机制，其思想是以服务器白名单的形式来配置可信的内容来源，客户端Web应用代码可以使用这些安全来源。Cisco研究人员找到了绕过CSP的一种方法，攻击者可以利用这种方法，注入被禁止的代码，从而窃取隐私数据。

<br>

**三、技术细节：Talos-2017-0306（CVE-2017-2419, CVE-2017-5033）**

****

CSP定义了一个HTTP头部：Content-Security-Policy，这个头部可以创建一个白名单源，使浏览器只会从策略指定的可信源来执行资源。即使攻击者找到某种方法完成恶意脚本注入，通过在远程脚本源中插入一段**&lt;script&gt;**标签成功发起XSS攻击，在CSP的限制下，远程源仍然不会与可信源清单匹配，因此也不会被浏览器执行。

Content-Security-Policy头中定义了一条“script-src”指令，这条指令用来配置脚本代码所对应的CSP。举个例子，头部中某一行如下所示：

```
Content-Security-Policy: script-src 'self' https://good.example.com
```

根据这一行，浏览器只能从当前访问的服务器或者good.example.com这个服务器才能加载脚本资源。

然而，我们发现Microsoft Edge浏览器（40.15063版仍未修复）、Google Chrome浏览器（已修复）以及Safari浏览器（已修复）中存在一个信息泄露漏洞。利用这个漏洞，攻击者可能绕过Content-Security-Policy头指定的策略，导致信息泄露问题。

漏洞利用由三个主要模块构成：（a）在Content-Security-Policy中使用“unsafe-inline”指令，使浏览器支持内联（inline）脚本代码；（b）使用window.open()打开一个空白的新窗口；（3）调用document.write函数将代码写入新创建的空白窗口对象中，以绕过文档上的CSP限制策略。

这个问题会影响Microsoft Edge浏览器、老版本的Google Chrome浏览器以及Firefox浏览器，原因在于“about:blank”页面与加载该页面的文档属于同一个源，但不受CSP策略限制，基于这些事实，攻击者就可以完成漏洞利用。

想了解更多信息的话，读者可以参考TALOS的漏洞报告：[TALOS-2017-0306](http://www.talosintelligence.com/reports/TALOS-2017-0306/)。该报告部分内容摘抄如下：

“ 攻击者可以使用**window.open("","_blank")**创建一个新页面，然后使用**document.write**将恶意脚本写入该页面，由于攻击者处于**about:blank**页面中，因此可以绕过原始页面上的CSP限制策略，成功访问其他站点。有人可能会说，这是因为CSP头中使用了不安全内联方式来加载代码才导致这个问题，但即便如此，浏览器也应该阻止任何形式的跨站通信行为（比如使用1×1像素大小的跟踪图片等行为）。

about:blank页面与其加载文档属于同一个源，但却不受CSP限制策略影响。在CSP规范文档中，早已明确指出CSP限制策略应该被页面所继承。大家可以参考此[规范文档](https://w3c.github.io/webappsec-csp/#initialize-document-csp)。”

<br>

**四、相关讨论**

****

攻击者可以利用某些漏洞执行远程代码、逃逸浏览器沙箱实现对目标系统的访问及控制，与这些漏洞比起来，信息泄露漏洞可能没那么严重。

然而，攻击者可以利用XSS攻击窃取隐私数据甚至最终控制用户账户，这样问题就会变得非常严重。内容安全策略正是为了防御XSS攻击而设计的，可以让服务器将可信资源添加到白名单中，使浏览器能安全执行这些资源。

许多开发者依赖CSP来使自己免受XSS以及其他信息泄露攻击影响，他们非常信任浏览器能支持这种安全标准。然而，我们发现不同浏览器所对CSP的具体实现有所不同，这样一来，攻击者可以针对特定的浏览器编写特定的代码，以绕过内容安全策略的限制，执行白名单之外的恶意代码。

我们建议用户使用对CSP机制提供更完整支持的那些浏览器，也建议用户保持浏览器处于最新版本，以防御新发现的所有安全漏洞（比如本文描述的信息泄露等漏洞）。

<br>

**五、受影响版本**

****

Microsoft Edge浏览器（40.15063版仍未修复）

57.0.2987.98版本之前Google Chrome浏览器（CVE-2017-5033）

10.3版本之前的iOS系统（CVE-2017-2419）

10.1版本之前的Apple Safari浏览器（CVE-2017-2419）



**六、如何检测**

****

我们可以使用如下Snort规则来检测该漏洞的利用行为。需要注意的是，未来我们可能会发布新的规则，漏洞信息进一步披露后，当前规则可能会发生变化。读者可以参考FireSIGHT管理中心或者Snort.org了解当前规则的更多内容。

Snort规则：42112
