> 原文链接: https://www.anquanke.com//post/id/98392 


# 我对OAuth协议安全性的一点思考


                                阅读量   
                                **267552**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01f58535af46b40cd3.jpg)](https://p2.ssl.qhimg.com/t01f58535af46b40cd3.jpg)



## 前言

近期安全圈内爆出“OAuth2.0协议存在安全缺陷”，可以造成用第三方帐号快捷登录授权劫持，据说可以利用此漏洞横扫全国各大主流网站。在刚看到漏洞利用详情时我也对这个漏洞表示肯定，但这么有名的OAuth2.0协议，几乎全世界的知名网站都在使用，它真的会出这么严重的安全问题吗？调皮的我决定仔细研究一波。



## 协议详解

说起OAuth2.0协议一些小白可能会感觉到很陌生，这个协议到底是用来做什么的？看一下QQ开放平台上的官方解释： OAuth（Open Authorization,开放授权）是一个开放标准，允许用户授权第三方网站访问他们存储在另外的服务提供者上的信息，而不需要将用户名和密码提供给第三方网站或分享他们数据的所有内容。举一个最常见的例子，就是我们在使用第三方业务时使用的“QQ号登录”，我们无需在第三方网站注册账号，可以直接使用QQ登录，登录过程中第三方无法获得我们QQ登录凭证，授权登录成功后第三方可以访问我们QQ的有关信息。

要研究OAuth2.0协议的安全问题，当然要对这个协议的工作原理有详细的理解，OAuth2.0协议正式发布为RFC 6749，我们来看一下官方对这个协议的解释。

**RFC 6749 : [https://tools.ietf.org/html/rfc6749](https://tools.ietf.org/html/rfc6749)**

这是整个协议授权的简化工作流程图：

[![](https://p1.ssl.qhimg.com/t01a5bcb0c2c0bb1af9.png)](https://p1.ssl.qhimg.com/t01a5bcb0c2c0bb1af9.png)



Client：用户

Resource Owner：资源所有者

Resource Server：储存受保护资源的服务器

Authorization Server：授权服务器



整个过程分为 A~F 六个步骤：

A：Client向Resource Owner发出认证请求。

B：Resource Owner对Client的请求给予授权，并给Client颁发一个授权令 牌Authorization Code。

C：Client携带Authorization Code对Authorization Server发起授权请求。

D：Authorization Server对Client的请求给予授权，并给Client颁发一个授权令牌Access Token。

E：Client携带Access Token向Resource Server请求用户信息资源。

F：Resource Server验证Access Token合法后将用户信息资源发回给Client。

到这一步我们对这个协议的工作流程有了大致的了解，但在生成环境下它又是怎么工作的呢？为此我详细研究了QQ开放平台的接入流程，并将其抽象为5个步骤。

具体实现：

我们以QQ登录OAuth2.0为例来具体了解一下QQ对这个协议的具体实现过程。

第1步：开发者在QQ开放平台申请接入并成功获取到appid和appkey。

第2步：构造QQ登录按钮的超链接如下：

[![](https://p2.ssl.qhimg.com/t01133cb20b07a99c04.png)](https://p2.ssl.qhimg.com/t01133cb20b07a99c04.png)

其中client_id参数为开发者在第一步中申请到的appid， redirect_uri为授权成功后的回调地址，在QQ登录成功后会跳转到   这个参数指定的URL，并在URL尾部追加Authorization Code，例如  回调地址是：www.qq.com/my.php，则会跳转到：

[![](https://p4.ssl.qhimg.com/t01418eae4a1472e167.png)](https://p4.ssl.qhimg.com/t01418eae4a1472e167.png)

scope参数为授权应用的权限列表

第3步：通过Authorization Code获取Access Token，服务器端构造如下 请求即可获取Access Token：

[![](https://p0.ssl.qhimg.com/t01b3ab81402dd86aa0.png)](https://p0.ssl.qhimg.com/t01b3ab81402dd86aa0.png)

参数解释如下：
<td width="109">grant_type</td><td width="419">授权类型，此值固定为“authorization_code”。</td>
<td width="109">client_id</td><td width="419">申请QQ登录成功后，分配给网站的appid。</td>
<td width="109">client_secret</td><td width="419">申请QQ登录成功后，分配给网站的appkey。</td>
<td width="109">code</td><td width="419">上一步返回的authorization code。</td>
<td width="109">redirect_uri</td><td width="419">与上面一步中传入的redirect_uri保持一致。</td>

第4步：使用Access Token来获取用户的OpenID

构造如下请求即可返回用户的OpenID：

[![](https://p3.ssl.qhimg.com/t01a55bc90e9f4737de.png)](https://p3.ssl.qhimg.com/t01a55bc90e9f4737de.png)

第5步：使用Access Token以及OpenID来访问用户数据

构造如下请求即可访问用户数据：

[![](https://p5.ssl.qhimg.com/t014bf60f9423ebf87d.png)](https://p5.ssl.qhimg.com/t014bf60f9423ebf87d.png)

其中的参数与前面介绍的相对应

具体的授权过程可以参考这张流程图：

[![](https://p2.ssl.qhimg.com/t01ac770e9e7fc791c1.png)](https://p2.ssl.qhimg.com/t01ac770e9e7fc791c1.png)

理解了OAuth2.0协议的实际实现过程之后我们就可以对攻击模型进行深入的分析了。



## 攻击模型分析

### 模型一：

攻击过程：在上述实现的第二步中将redirect_uri修改为攻击者控制站点，用户在授权登录后将携带authorization code跳转到攻击者控制站点，攻击者从URL参数中即可获得authorization code并实现用户劫持。

其实腾讯在实现第三方登录接入的时候早就考虑过这种老套的攻击方式，于是，开发者在集成QQ登录时必须在QQ开放平台上填写网站的回调地址，在进行登录验证的时候如果redirect_uri中的值与设置好的回调地址不同则会拒绝访问：

[![](https://p3.ssl.qhimg.com/t0177352179cb658eba.png)](https://p3.ssl.qhimg.com/t0177352179cb658eba.png)

这样就防止了攻击者篡改redirect_uri为恶意站点的钓鱼攻击。

但是现在又提出了一种看似合理的绕过方法：

利用合法网站的URL重定向漏洞绕过redirect_uri中的域名白名单限制

假设我有一个合法的网站whitehat.com，攻击者控制一个恶意站点hacker.com

攻击者可以构造这样一个链接来绕过redirect_uri中的域名白名单限制：

http://whitehat.com/index.php?Redirect=http%3a%2f%2fhacker.com%2findex.php

其中Redirect参数指定的为重定向地址

这样的话，把这个URL地址传给redirect_uri即可构造一个恶意链接，实现用户授权QQ登录后跳转到hacker.com

但是用户的授权令牌authorization code真的会被传送到hacker.com吗？

我们把上述URL传给redirect_uri，跳转到的URL地址如下：

[http://whitehat.com/index.php?Redirect=http%3a%2f%2fhacker.com%2f](http://whitehat.com/index.php?Redirect=hacker.com)index.php?code=****

细心的人已经发现了，这个链接还是跳转到http://hacker.com/index.php而不是http://hacker.com/index.php?code=****

这是因为code参数前面的&amp;符号没有URL编码，因此code参数被whitehat.com处理而不是属于Redirect参数的一部分。

因此，第一种攻击模型只能用来构造登录后的钓鱼攻击，通常情况下authorization code不会被传送到攻击者控制的站点中。

### 攻击模型二

将第二步实现的redirect_uri改为可以引入外链的合法URL地址，这样当合法用户登录后加载此页面的外链时，攻击者就可以从其控制的服务器中在referer消息头中获得泄露的authorization code。据说这种攻击方法横扫国内各大站点，但是我在深入研究的时候发现，这个攻击方法在此RFC文档的Security Considerations中已经提到过：

[![](https://p4.ssl.qhimg.com/t01cfbabdef04caa26d.png)](https://p4.ssl.qhimg.com/t01cfbabdef04caa26d.png)

同时也给出了相应的安全建议：

[![](https://p1.ssl.qhimg.com/t01cad5a18e9cf3e24b.png)](https://p1.ssl.qhimg.com/t01cad5a18e9cf3e24b.png)

即authorization code在获取后必须在短时间内失效而且只能被使用一次。这种方法在理论上确实可以有效的阻止上述的攻击方式，情景分析如下：



攻击者构造恶意链接发送给用户，其中redirect_uri=http://bbs.test.com/index.php

用户点击链接登录后，回调地址为：

[http://bbs.test.com/index.php?Code=****](http://bbs.test.com/index.php?Code=****)

用户携带code向服务器发送请求加载此页面

加载的页面中含有攻击者放置的外链（例如头像中的图片链接等）

用户加载外链中的图片，攻击者从referer消息头中获得用户的code



由此可以看出如果authorization code使用一次就失效的话，那么在用户加载页面时就应该失效了，攻击者获得的一定是一个失效的authorization code！这样看来这种攻击方式应该是无效的，但它究竟为什么能扫国内各大站点呢？是因为腾讯实现的OAuth2.0协议没有把authorization code设置成一次有效吗？

但经过多次试验发现QQ登录OAuth2.0中authorization code确实是一次有效。

百思不得其解，不得问某师傅要了一个国内某知名站点OAuth2.0登录劫持的漏洞详情来研究，在仔细研究后终于明白了其中的道理：

我在漏洞利用详情中发现跳转目标的文件名后缀都是.hmtl或者.shtml，而且在页面上都显示未登录[![](https://p1.ssl.qhimg.com/t0182252b21f3a40ece.png)](https://p1.ssl.qhimg.com/t0182252b21f3a40ece.png)，这就表示跳转后的目标地址虽然被追加了authorization code参数但并没有进行登录操作，即在后端并没有用authorization code去获取Access Token，因此从这些页面泄露出去的authorization code都是有效的！攻击者只要获得这些authorization code就可以登录受害者的账户！



## 修复建议

之前听说有的厂商的修复方法是禁止页面包含外链，很明显这个方法不能从根本上解决问题，而且有可能影响用户体验。正确的修复方案应该是:当用户进行登录时，将当前的URL设置为一条cookie或者通过AJAX发送到服务器存储到session中，当用户登录成功后跳转到一个固定的回调地址（唯一且不可更改），在这个回调地址中进行登录操作（使authorization code失效），然后再从cookie或者session中取出登录前的URL进行跳转，这样攻击者就无法获取到用户的authorization code，即使有authorization code泄露也都是已经失效的了！



## 总结

不要听信网络上的言论，第二种攻击模型确实使得国内大部分厂商躺枪，但是OAuth2.0协议没有漏洞，腾讯对OAuth2.0协议的实现安全性也很高，所有的安全问题都出现在使用这些功能的第三方中！
