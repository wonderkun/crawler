> 原文链接: https://www.anquanke.com//post/id/237319 


# 赏金$35000的GitHub漏洞：攻破GitHub私有页面


                                阅读量   
                                **345579**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者RobertChen，文章来源：robertchen.cc
                                <br>原文地址：[https://robertchen.cc/blog/2021/04/03/github-pages-xss﻿](https://robertchen.cc/blog/2021/04/03/github-pages-xss%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0184a8aa1be0153761.png)](https://p2.ssl.qhimg.com/t0184a8aa1be0153761.png)



## 0x00 前言

这个漏洞是我和<a>@ginkoid</a>合作发现的，同时也是我在HackerOne上获得的第一笔漏洞赏金（35,000美元），也是迄今为止我从HackerOne获得的最高赏金，我相信也可能是GitHub迄今为止支付的最高赏金。

由于新冠疫情，**高三线上学习课程之余**，我将更多精力放在漏洞挖掘上。这个漏洞是作为GitHub私有页面的赏金项目中的一部分被提交的，这笔巨额赏金还有包括其他两个CTF奖金：
- $10000 : 在无需用户交互的条件下读取 “flag.private-org.github.io “上的flag。如果从`private-org`之外的账户读取flag，则额外奖励5k美元
- $5000 : 在有用户交互的条件下读取`flag.private-org.github.io`上的flag
在这篇文章中，我将详细说明挖掘思路。



## 0x01 认证流程

由于GitHub 私有页面是单独在域`github.io`上托管，`github.com`认证cookie不会被发送到私有页面服务器上。因此，如果不与`github.com`进行额外的整合，私有页面认证就无法确定用户的身份。因此，GitHub创建了一个自定义的身份验证流程，这期间就可能引入错误。在提交漏洞报告时，GitHub私有页面的认证流程如下：

[![](https://p3.ssl.qhimg.com/t0160a43041e0e74f49.jpg)](https://p3.ssl.qhimg.com/t0160a43041e0e74f49.jpg)

在访问私有页面时，服务器会检查是否存在`__Host-gh_pages_token`cookie，如果该cookie不存在或设置错误，私有页面服务器将重定向到`https://github.com/login`。这个初始重定向会设置一个“nonce”存储在`__Host-gh_pages_session`的cookie中。需要注意的是，这个cookie使用了[__Host- cookie前缀](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#attributes)，作为一种额外的防御措施，理论上可以防止JavaScript对非主机式父域进行设置。

`/login`将重定向到`/pages/auth?nonce=&amp;page_id=&amp;path=`。这个端点会生成一个临时的认证cookie，并将其传递给`token`参数中的`https://pages-auth.github.com/redirect`，`nonce`、`page_id`和`path`也同样被转发。

`/redirect`只转发到`https://repo.org.github.io/__/auth`。最后一个端点设置了`repo.org.github.io`域的认证cookie、`__Host-gh_pages_token`和`__Host-gh_pages_id`，也会根据之前设置的`__Host-gh_pages_session`验证`nonce`。

在整个认证流程中，原始请求路径和页面ID等信息分别存储在查询参数`path`和`page_id`中，“nonce” 也会通过`nonce`参数传递。



## 0x02 漏洞挖掘思路

### <a class="reference-link" name="CRLF"></a>CRLF

第一个漏洞是在`https://repo.org.github.io/__/auth`的`page_id`参数中注入CRLF。在对认证流程研究的过程中，我注意到`page_id`的解析似乎忽略了空格，同时还将参数直接解析到`Set-Cookie`头中。

举个例子，如果传递`page_id=12345%20`：

```
Set-Cookie: __Host-gh_pages_id=13212257 ; Secure; HttpOnly; path=/
```

伪代码逻辑如下：

```
page_id = query.page_id

do_page_lookup(to_int(page_id))
set_page_id_cookie(page_id)
```

这里，`page_id`被转换为一个整数，并直接解析到 `Set-Cookie`头中。问题是我们不能直接解析任何文本。虽然有一个经典的CRLF注入，但放置任何非空格字符都会导致整数解析中断。我们可以通过发送`page_id=12345%0d%0a%0d%0a`来打破认证流程，但没有任何直接影响，除了以下这个响应：

```
; Secure; HttpOnly; path=/
Cache-Control: private
Location: https://83e02b43.near-dimension.github.io/
X-GLB-L

```

因为`Location:`头被附加在`Set-Cookie`头之后，响应会将把`Location`排除到已发送的HTTP头之外。即使是302重定向，也会忽略`Location`头并解析正文内容。

### <a class="reference-link" name="%E6%9B%B4%E8%BF%9B%E4%B8%80%E6%AD%A5"></a>更进一步

翻看了一下GitHub企业版源码（提供了访问源码的权限），我怀疑私有页面服务器为openresty nginx，可能它存在空字节的问题？

当我们附加一个空字节，就会导致整数解析结束。换句话说，我们可以使用这样的有效payload：

```
"?page_id=" + encodeURIComponent("\r\n\r\n\x00&lt;script&gt;alert(origin)&lt;/script&gt;")
```

这里，我们获得一个XSS漏洞：

[![](https://p1.ssl.qhimg.com/t01a8093137e65d6c1e.jpg)](https://p1.ssl.qhimg.com/t01a8093137e65d6c1e.jpg)

这里需要注意的是，如果头中有一个空字节，响应就会被拒绝，因此，空字节必须出现在正文的开头，这意味着我们不能进行请求头注入攻击。

至此，我们已经实现了在私有页面域上执行任意的JavaScript，但还需要一种绕过nonce的方法。虽然`page_id`和`path`参数已知，但“nonce”阻止我们用污染的`page_id`向受害者发送认证流程。

### <a class="reference-link" name="%E7%BB%95%E8%BF%87Nonce"></a>绕过Nonce

通过观察发现，同一组织中的同级私有页面可以互相设置cookie，这是因为`*.github.io`不在[公共后缀列表](https://publicsuffix.org/)中。因此，在`private-org.github.io`上设置的cookie会传到`private-page.private-org.github.io`上。因此，如果我们绕过`__Host-`前缀保护，就能获得”nonce”绕过，因为另一个同级页面中设置一个假的“nonce”，会被传递下去。幸运的是，这个前缀并不是在所有的浏览器上都被强制执行：

[![](https://p4.ssl.qhimg.com/t01f789e768e3742d49.jpg)](https://p4.ssl.qhimg.com/t01f789e768e3742d49.jpg)

从上图可以看出只有 IE会受到这种绕过的影响，这显然威胁程度不够高。那攻击“nonce”本身呢? 它似乎是安全生成的，而密码学并不是我的强项，也没有办法绕过加密。

于是我调整思路，通过阅读[RFCs](https://datatracker.ietf.org/doc/html/draft-ietf-httpbis-rfc6265bis-05)，我发现了一个有趣的想法——Cookie进行标准化？具体来说，应该如何处理cookie的大写，`__HOST-`和`__Host-`一样吗？在浏览器上，很容易确认它们的处理方式是不同的。

```
document.cookie = "__HOST-Test=1"; // works
document.cookie = "__Host-Test=1"; // fails
```

可见，GitHub私有页面服务器在解析Cookie时忽略了大写，这样前缀绕过得以实现! 于是，可以使用一个简单的POC来达成完整的XSS!

```
&lt;script&gt;
const id = location.search.substring("?id=".length)

document.cookie = "__HOST-gh_pages_session=dea8c624-468f-4c5b-a4e6-9a32fe6b9b15; domain=.private-org.github.io";
location = "https://github.com/pages/auth?nonce=dea8c624-468f-4c5b-a4e6-9a32fe6b9b15&amp;page_id=" + id + "%0d%0a%0d%0a%00&lt;script&gt;alert(origin)%3c%2fscript&gt;&amp;path=Lw";
&lt;/script&gt;
```

这个漏洞就足以获得 $5000 的奖金，但我还想更深一步挖掘。

### <a class="reference-link" name="%E7%BC%93%E5%AD%98%E4%B8%AD%E6%AF%92"></a>缓存中毒

`/__/auth?`端点上的响应仅缓存已解析的整数`page_id`，这本身在技术上是无害的，因为该端点设置的令牌仅限于私人页面，没有其他权限，但如果以后包含其他权限的token，这就可能引发潜在的安全问题。

这种缓存行为升级攻击的威胁提供了一个途径。因为缓存已解析的整数值，一个带有XSS的缓存中毒可能会影响没有与恶意payload交互的其他用户，演示视频地址：[https://robertchen.cc/blog/gh-xss/cache-xss.mp4：](https://robertchen.cc/blog/gh-xss/cache-xss.mp4%EF%BC%9A)

[![](https://p4.ssl.qhimg.com/t01ba4981ae19c78b23.png)](https://p4.ssl.qhimg.com/t01ba4981ae19c78b23.png)

如果，攻击者控制了`unprivileged.org.github.io`，并想获得`privileged.org.github.io`的访问权，他可以首先污染`unprivileged.org.github.io`的认证流，使得XSS payload被缓存。当特权用户访问`unprivileged.org.github.io`时，就会在`unprivileged.org.github.io`域上遭遇XSS攻击。由于可以在共享的父域`org.github.io`上设置cookie，攻击者现在可以对`privileged.org.github.io`进行攻击。这将允许对私有页面拥有读权限的攻击者永久破坏该页面的身份验证流。



## 0x03 公有——私有页面

为了获得15000美元的奖金，我们需要从一个不在组织中的用户账户执行这次攻击。我们可以利用另一个看似不相关的错误配置，进入 “Public-Private 页面”。私有页面中可能存在的错误配置使得公共存储库也有自己的 “私有”页面。这些 “私有”页面虽然经过正常的认证周期，但对每个人都是公开的。如果一个组织有这样的“公有——私有页面”，任何拥有GitHub账户的用户都对其用有 “读权限”。

例如，当一个私有页面存储库被改成公共的时候，这种情况情况就会发生。这种场景是合理的，因为一个组织最初可能会创建一个私有版本库和相应的私有页面。后来，该组织可能会决定对项目进行开源，将存储库状态改为公开。这是一个例子，演示视频地址：[https://robertchen.cc/blog/gh-xss/public-private.mp4](https://robertchen.cc/blog/gh-xss/public-private.mp4)

[![](https://p4.ssl.qhimg.com/t0109d161d0d98ffae4.png)](https://p4.ssl.qhimg.com/t0109d161d0d98ffae4.png)

[![](https://p2.ssl.qhimg.com/t01335b36af7060f827.png)](https://p2.ssl.qhimg.com/t01335b36af7060f827.png)

[![](https://p3.ssl.qhimg.com/t0182d0120ffa83a78c.png)](https://p3.ssl.qhimg.com/t0182d0120ffa83a78c.png)

[![](https://p3.ssl.qhimg.com/t0175d3fb6a011aed07.png)](https://p3.ssl.qhimg.com/t0175d3fb6a011aed07.png)

结合上述情况，一个无权限的外部用户可以利用 “公有——私有页面”为中转，从而损害内部私有页面的认证流。

将上面的攻击思路整合，就能形成一个好棒的POC，它展示了外部攻击者如何利用内部员工中转攻破其他私有页面，演示视频地址：[https://robertchen.cc/blog/gh-xss/pivot.mp4](https://robertchen.cc/blog/gh-xss/pivot.mp4)

[![](https://p3.ssl.qhimg.com/t01a6fa4fd194d47773.png)](https://p3.ssl.qhimg.com/t01a6fa4fd194d47773.png)

[![](https://p5.ssl.qhimg.com/t01bc2a50c51a48053c.png)](https://p5.ssl.qhimg.com/t01bc2a50c51a48053c.png)

[![](https://p2.ssl.qhimg.com/t01d68bf5ef1609a7ba.png)](https://p2.ssl.qhimg.com/t01d68bf5ef1609a7ba.png)

[![](https://p2.ssl.qhimg.com/t01ad0dcbba40d1de81.png)](https://p2.ssl.qhimg.com/t01ad0dcbba40d1de81.png)

[![](https://p0.ssl.qhimg.com/t01b5c1b9b80f3a90ee.png)](https://p0.ssl.qhimg.com/t01b5c1b9b80f3a90ee.png)

[![](https://p5.ssl.qhimg.com/t018a5694bc33f3708e.png)](https://p5.ssl.qhimg.com/t018a5694bc33f3708e.png)

[![](https://p3.ssl.qhimg.com/t018864a1308b2b6604.png)](https://p3.ssl.qhimg.com/t018864a1308b2b6604.png)

[![](https://p4.ssl.qhimg.com/t01b5c17662231abb78.png)](https://p4.ssl.qhimg.com/t01b5c17662231abb78.png)

后续的持久性可以可能通过AppCache或其他技术来实现。



## 0x04 尾声

总结来说，这样的漏洞真是万里挑一，许多组件必须以正确的方式排列，最终能影响到GitHub的所有用户，真是太酷了。最后，这个漏洞的严重程度被评为“高危”，漏洞赏金 $20000，加上前面的CTF奖金，共获得 $35000 的巨额奖励。

**时间线：**<br>
2020.05.21 – 在HackerOne上向GitHub私有漏洞赏金项目提交报告<br>
2020.06.20 – GitHub 修复漏洞并支付漏洞赏金<br>
2021.04.03 – 该漏洞的细节被本文披露
