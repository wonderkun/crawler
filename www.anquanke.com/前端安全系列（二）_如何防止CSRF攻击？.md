> 原文链接: https://www.anquanke.com//post/id/161724 


# 前端安全系列（二）：如何防止CSRF攻击？


                                阅读量   
                                **183294**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01b5504c51fd8fb575.jpg)](https://p1.ssl.qhimg.com/t01b5504c51fd8fb575.jpg)

## 背景

随着互联网的高速发展，信息安全问题已经成为企业最为关注的焦点之一，而前端又是引发企业安全问题的高危据点。在移动互联网时代，前端人员除了传统的 XSS、CSRF 等安全问题之外，又时常遭遇网络劫持、非法调用 Hybrid API 等新型安全问题。当然，浏览器自身也在不断在进化和发展，不断引入 CSP、Same-Site Cookies 等新技术来增强安全性，但是仍存在很多潜在的威胁，这需要前端技术人员不断进行“查漏补缺”。



## 前端安全

近几年，美团业务高速发展，前端随之面临很多安全挑战，因此积累了大量的实践经验。我们梳理了常见的前端安全问题以及对应的解决方案，将会做成一个系列，希望可以帮助前端同学在日常开发中不断预防和修复安全漏洞。此前我们已经发布过《[前端安全系列之一：如何防止XSS攻击？](http://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&amp;mid=2651748921&amp;idx=2&amp;sn=04ee8977545923ad9b485ba236d7a126&amp;chksm=bd12a3748a652a628ecb841f78e00ccf5eb002117236e18a7d947ae824c2cc75841c1f7c0455&amp;scene=21#wechat_redirect)》，本文是该系列的第二篇。

今天我们讲解一下 CSRF，其实相比XSS，CSRF的名气似乎并不是那么大，很多人都认为“CSRF不具备那么大的破坏性”。真的是这样吗？接下来，我们还是有请小明同学再次“闪亮”登场。



## CSRF攻击

### CSRF漏洞的发生

相比XSS，CSRF的名气似乎并不是那么大，很多人都认为CSRF“不那么有破坏性”。真的是这样吗？

接下来有请小明出场~~

**小明的悲惨遭遇**

这一天，小明同学百无聊赖地刷着Gmail邮件。大部分都是没营养的通知、验证码、聊天记录之类。但有一封邮件引起了小明的注意：

> 甩卖比特币，一个只要998！！

聪明的小明当然知道这种肯定是骗子，但还是抱着好奇的态度点了进去（请勿模仿）。果然，这只是一个什么都没有的空白页面，小明失望的关闭了页面。一切似乎什么都没有发生……

在这平静的外表之下，黑客的攻击已然得手。小明的Gmail中，被偷偷设置了一个过滤规则，这个规则使得所有的邮件都会被自动转发到hacker@hackermail.com。小明还在继续刷着邮件，殊不知他的邮件正在一封封地，如脱缰的野马一般地，持续不断地向着黑客的邮箱转发而去。

不久之后的一天，小明发现自己的域名已经被转让了。懵懂的小明以为是域名到期自己忘了续费，直到有一天，对方开出了 $650 的赎回价码，小明才开始觉得不太对劲。

小明仔细查了下域名的转让，对方是拥有自己的验证码的，而域名的验证码只存在于自己的邮箱里面。小明回想起那天奇怪的链接，打开后重新查看了“空白页”的源码：

```
&lt;form method="POST" action="https://mail.google.com/mail/h/ewt1jmuj4ddv/?v=prf" enctype="multipart/form-data"&gt; 
    &lt;input type="hidden" name="cf2_emc" value="true"/&gt; 
    &lt;input type="hidden" name="cf2_email" value="hacker@hakermail.com"/&gt; 
    .....
    &lt;input type="hidden" name="irf" value="on"/&gt; 
    &lt;input type="hidden" name="nvp_bu_cftb" value="Create Filter"/&gt; 
&lt;/form&gt; 
&lt;script&gt; 
    document.forms[0].submit();
&lt;/script&gt;
```

> 这个页面只要打开，就会向Gmail发送一个post请求。请求中，执行了“Create Filter”命令，将所有的邮件，转发到“hacker@hackermail.com”。
小明由于刚刚就登陆了Gmail，所以这个请求发送时，携带着小明的登录凭证（Cookie），Gmail的后台接收到请求，验证了确实有小明的登录凭证，于是成功给小明配置了过滤器。
黑客可以查看小明的所有邮件，包括邮件里的域名验证码等隐私信息。拿到验证码之后，黑客就可以要求域名服务商把域名重置给自己。

小明很快打开Gmail，找到了那条过滤器，将其删除。然而，已经泄露的邮件，已经被转让的域名，再也无法挽回了……

以上就是小明的悲惨遭遇。而“点开一个黑客的链接，所有邮件都被窃取”这种事情并不是杜撰的，此事件原型是2007年Gmail的CSRF漏洞：

[https://www.davidairey.com/google-gmail-security-hijack/](https://www.davidairey.com/google-gmail-security-hijack/)

当然，目前此漏洞已被Gmail修复，请使用Gmail的同学不要慌张。

**什么是CSRF**

CSRF（Cross-site request forgery）跨站请求伪造：攻击者诱导受害者进入第三方网站，在第三方网站中，向被攻击网站发送跨站请求。利用受害者在被攻击网站已经获取的注册凭证，绕过后台的用户验证，达到冒充用户对被攻击的网站执行某项操作的目的。

一个典型的CSRF攻击有着如下的流程：
- 受害者登录a.com，并保留了登录凭证（Cookie）。
- 攻击者引诱受害者访问了b.com。
- b.com 向 a.com 发送了一个请求：a.com/act=xx。浏览器会默认携带a.com的Cookie。
- a.com接收到请求后，对请求进行验证，并确认是受害者的凭证，误以为是受害者自己发送的请求。
- a.com以受害者的名义执行了act=xx。
- 攻击完成，攻击者在受害者不知情的情况下，冒充受害者，让a.com执行了自己定义的操作。
**几种常见的攻击类型**
- GET类型的CSRF
GET类型的CSRF利用非常简单，只需要一个HTTP请求，一般会这样利用：

```
&lt;img src="http://bank.example/withdraw?amount=10000&amp;for=hacker" &gt;
```

在受害者访问含有这个img的页面后，浏览器会自动向[http://bank.example/withdraw?account=xiaoming&amp;amount=10000&amp;for=hacker](http://bank.example/withdraw?account=xiaoming&amp;amount=10000&amp;for=hacker)发出一次HTTP请求。bank.example就会收到包含受害者登录信息的一次跨域请求。
- POST类型的CSRF
这种类型的CSRF利用起来通常使用的是一个自动提交的表单，如：

```
&lt;form action="http://bank.example/withdraw" method=POST&gt;
    &lt;input type="hidden" name="account" value="xiaoming" /&gt;
    &lt;input type="hidden" name="amount" value="10000" /&gt;
    &lt;input type="hidden" name="for" value="hacker" /&gt;
&lt;/form&gt;
&lt;script&gt; document.forms[0].submit(); &lt;/script&gt;
```

访问该页面后，表单会自动提交，相当于模拟用户完成了一次POST操作。

POST类型的攻击通常比GET要求更加严格一点，但仍并不复杂。任何个人网站、博客，被黑客上传页面的网站都有可能是发起攻击的来源，后端接口不能将安全寄托在仅允许POST上面。
- 链接类型的CSRF
链接类型的CSRF并不常见，比起其他两种用户打开页面就中招的情况，这种需要用户点击链接才会触发。这种类型通常是在论坛中发布的图片中嵌入恶意链接，或者以广告的形式诱导用户中招，攻击者通常会以比较夸张的词语诱骗用户点击，例如：

```
&lt;a href="http://test.com/csrf/withdraw.php?amount=1000&amp;for=hacker" taget="_blank"&gt;
  重磅消息！！
  &lt;a/&gt;
```

由于之前用户登录了信任的网站A，并且保存登录状态，只要用户主动访问上面的这个PHP页面，则表示攻击成功。

**CSRF的特点**
- 攻击一般发起在第三方网站，而不是被攻击的网站。被攻击的网站无法防止攻击发生。
- 攻击利用受害者在被攻击网站的登录凭证，冒充受害者提交操作；而不是直接窃取数据。
- 整个过程攻击者并不能获取到受害者的登录凭证，仅仅是“冒用”。
- 跨站请求可以用各种方式：图片URL、超链接、CORS、Form提交等等。部分请求方式可以直接嵌入在第三方论坛、文章中，难以进行追踪。
CSRF通常是跨域的，因为外域通常更容易被攻击者掌控。但是如果本域下有容易被利用的功能，比如可以发图和链接的论坛和评论区，攻击可以直接在本域下进行，而且这种攻击更加危险。



## 防护策略

CSRF通常从第三方网站发起，被攻击的网站无法防止攻击发生，只能通过增强自己网站针对CSRF的防护能力来提升安全性。

上文中讲了CSRF的两个特点：
- CSRF（通常）发生在第三方域名。
- CSRF攻击者不能获取到Cookie等信息，只是使用。
针对这两点，我们可以专门制定防护策略，如下：
<li>阻止不明外域的访问
<ul>
- 同源检测
- Samesite Cookie- CSRF Token
- 双重Cookie验证
以下我们对各种防护方法做详细说明：

**同源检测**

既然CSRF大多来自第三方网站，那么我们就直接禁止外域（或者不受信任的域名）对我们发起请求。

那么问题来了，我们如何判断请求是否来自外域呢？

在HTTP协议中，每一个异步请求都会携带两个Header，用于标记来源域名：
- Origin Header
- Referer Header
这两个Header在浏览器发起请求时，大多数情况会自动带上，并且不能由前端自定义内容。

服务器可以通过解析这两个Header中的域名，确定请求的来源域。

使用Origin Header确定来源域名

在部分与CSRF有关的请求中，请求的Header中会携带Origin字段。字段内包含请求的域名（不包含path及query）。

如果Origin存在，那么直接使用Origin中的字段确认来源域名就可以。

但是Origin在以下两种情况下并不存在：
<li>IE11同源策略： IE 11 不会在跨站CORS请求上添加Origin标头，Referer头将仍然是唯一的标识。最根本原因是因为IE 11对同源的定义和其他浏览器有不同，有两个主要的区别，可以参考[MDN Same-origin_policy#IE_Exceptions](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy#IE_Exceptions)
</li>
- 302重定向： 在302重定向之后Origin不包含在重定向的请求中，因为Origin可能会被认为是其他来源的敏感信息。对于302重定向的情况来说都是定向到新的服务器上的URL，因此浏览器不想将Origin泄漏到新的服务器上。
使用Referer Header确定来源域名

根据HTTP协议，在HTTP头中有一个字段叫Referer，记录了该HTTP请求的来源地址。

对于Ajax请求，图片和script等资源请求，Referer为发起请求的页面地址。对于页面跳转，Referer为打开页面历史记录的前一个页面地址。因此我们使用Referer中链接的Origin部分可以得知请求的来源域名。

这种方法并非万无一失，Referer的值是由浏览器提供的，虽然HTTP协议上有明确的要求，但是每个浏览器对于Referer的具体实现可能有差别，并不能保证浏览器自身没有安全漏洞。使用验证 Referer 值的方法，就是把安全性都依赖于第三方（即浏览器）来保障，从理论上来讲，这样并不是很安全。在部分情况下，攻击者可以隐藏，甚至修改自己请求的Referer。

2014年，W3C的Web应用安全工作组发布了Referrer Policy草案，对浏览器该如何发送Referer做了详细的规定。截止现在新版浏览器大部分已经支持了这份草案，我们终于可以灵活地控制自己网站的Referer策略了。新版的Referrer Policy规定了五种Referer策略：No Referrer、No Referrer When Downgrade、Origin Only、Origin When Cross-origin、和 Unsafe URL。之前就存在的三种策略：never、default和always，在新标准里换了个名称。他们的对应关系如下：

[![](https://p5.ssl.qhimg.com/t01afb0cf01bebcb50c.png)](https://p5.ssl.qhimg.com/t01afb0cf01bebcb50c.png)

根据上面的表格因此需要把Referrer Policy的策略设置成same-origin，对于同源的链接和引用，会发送Referer，referer值为Host不带Path；跨域访问则不携带Referer。例如：aaa.com引用bbb.com的资源，不会发送Referer。

设置Referrer Policy的方法有三种：
1. 在CSP设置
1. 页面头部增加meta标签
1. a标签增加referrerpolicy属性
上面说的这些比较多，但我们可以知道一个问题：攻击者可以在自己的请求中隐藏Referer。如果攻击者将自己的请求这样填写：

```
&lt;img src="http://bank.example/withdraw?amount=10000&amp;for=hacker" referrerpolicy="no-referrer"&gt;
```

那么这个请求发起的攻击将不携带Referer。

另外在以下情况下Referer没有或者不可信：

1. IE6、7下使用window.location.href=url进行界面的跳转，会丢失Referer。

2. IE6、7下使用window.open，也会缺失Referer。

3. HTTPS页面跳转到HTTP页面，所有浏览器Referer都丢失。

4. 点击Flash上到达另外一个网站的时候，Referer的情况就比较杂乱，不太可信。

无法确认来源域名情况

当Origin和Referer头文件不存在时该怎么办？如果Origin和Referer都不存在，建议直接进行阻止，特别是如果您没有使用随机CSRF Token（参考下方）作为第二次检查。

如何阻止外域请求

通过Header的验证，我们可以知道发起请求的来源域名，这些来源域名可能是网站本域，或者子域名，或者有授权的第三方域名，又或者来自不可信的未知域名。

我们已经知道了请求域名是否是来自不可信的域名，我们直接阻止掉这些的请求，就能防御CSRF攻击了吗？

且慢！当一个请求是页面请求（比如网站的主页），而来源是搜索引擎的链接（例如百度的搜索结果），也会被当成疑似CSRF攻击。所以在判断的时候需要过滤掉页面请求情况，通常Header符合以下情况：

```
Accept: text/html
Method: GET
```

但相应的，页面请求就暴露在了CSRF的攻击范围之中。如果你的网站中，在页面的GET请求中对当前用户做了什么操作的话，防范就失效了。

例如，下面的页面请求：

```
GET https://example.com/addComment?comment=XXX&amp;dest=orderId
```

注：这种严格来说并不一定存在CSRF攻击的风险，但仍然有很多网站经常把主文档GET请求挂上参数来实现产品功能，但是这样做对于自身来说是存在安全风险的。

另外，前面说过，CSRF大多数情况下来自第三方域名，但并不能排除本域发起。如果攻击者有权限在本域发布评论（含链接、图片等，统称UGC），那么它可以直接在本域发起攻击，这种情况下同源策略无法达到防护的作用。

综上所述：同源验证是一个相对简单的防范方法，能够防范绝大多数的CSRF攻击。但这并不是万无一失的，对于安全性要求较高，或者有较多用户输入内容的网站，我们就要对关键的接口做额外的防护措施。

**CSRF Token**

前面讲到CSRF的另一个特征是，攻击者无法直接窃取到用户的信息（Cookie，Header，网站内容等），仅仅是冒用Cookie中的信息。

而CSRF攻击之所以能够成功，是因为服务器误把攻击者发送的请求当成了用户自己的请求。那么我们可以要求所有的用户请求都携带一个CSRF攻击者无法获取到的Token。服务器通过校验请求是否携带正确的Token，来把正常的请求和攻击的请求区分开，也可以防范CSRF的攻击。

原理

CSRF Token的防护策略分为三个步骤：

1. 将CSRF Token输出到页面中

首先，用户打开页面的时候，服务器需要给这个用户生成一个Token，该Token通过加密算法对数据进行加密，一般Token都包括随机字符串和时间戳的组合，显然在提交时Token不能再放在Cookie中了，否则又会被攻击者冒用。因此，为了安全起见Token最好还是存在服务器的Session中，之后在每次页面加载时，使用JS遍历整个DOM树，对于DOM中所有的a和form标签后加入Token。这样可以解决大部分的请求，但是对于在页面加载之后动态生成的HTML代码，这种方法就没有作用，还需要程序员在编码时手动添加Token。

2. 页面提交的请求携带这个Token

对于GET请求，Token将附在请求地址之后，这样URL 就变成 [http://url?csrftoken=tokenvalue](http://url?csrftoken=tokenvalue)。 而对于 POST 请求来说，要在 form 的最后加上：<br>
&lt;input type=”hidden” name=”csrftoken” value=”tokenvalue”/&gt;<br>
这样，就把Token以参数的形式加入请求了。

3. 服务器验证Token是否正确

当用户从客户端得到了Token，再次提交给服务器的时候，服务器需要判断Token的有效性，验证过程是先解密Token，对比加密字符串以及时间戳，如果加密字符串一致且时间未过期，那么这个Token就是有效的。

这种方法要比之前检查Referer或者Origin要安全一些，Token可以在产生并放于Session之中，然后在每次请求时把Token从Session中拿出，与请求中的Token进行比对，但这种方法的比较麻烦的在于如何把Token以参数的形式加入请求。<br>
下面将以Java为例，介绍一些CSRF Token的服务端校验逻辑，代码如下：

```
HttpServletRequest req = (HttpServletRequest)request; 
HttpSession s = req.getSession(); 

// 从 session 中得到 csrftoken 属性
String sToken = (String)s.getAttribute(“csrftoken”); 
if(sToken == null)`{` 
   // 产生新的 token 放入 session 中
   sToken = generateToken(); 
   s.setAttribute(“csrftoken”,sToken); 
   chain.doFilter(request, response); 
`}` else`{` 
   // 从 HTTP 头中取得 csrftoken 
   String xhrToken = req.getHeader(“csrftoken”); 
   // 从请求参数中取得 csrftoken 
   String pToken = req.getParameter(“csrftoken”); 
   if(sToken != null &amp;&amp; xhrToken != null &amp;&amp; sToken.equals(xhrToken))`{` 
       chain.doFilter(request, response); 
   `}`else if(sToken != null &amp;&amp; pToken != null &amp;&amp; sToken.equals(pToken))`{` 
       chain.doFilter(request, response); 
   `}`else`{` 
       request.getRequestDispatcher(“error.jsp”).forward(request,response); 
   `}` 
`}`
```

代码源自：[IBM developerworks CSRF](https://www.ibm.com/developerworks/cn/web/1102_niugang_csrf/)

这个Token的值必须是随机生成的，这样它就不会被攻击者猜到，考虑利用Java应用程序的java.security.SecureRandom类来生成足够长的随机标记，替代生成算法包括使用256位BASE64编码哈希，选择这种生成算法的开发人员必须确保在散列数据中使用随机性和唯一性来生成随机标识。通常，开发人员只需为当前会话生成一次Token。在初始生成此Token之后，该值将存储在会话中，并用于每个后续请求，直到会话过期。当最终用户发出请求时，服务器端必须验证请求中Token的存在性和有效性，与会话中找到的Token相比较。如果在请求中找不到Token，或者提供的值与会话中的值不匹配，则应中止请求，应重置Token并将事件记录为正在进行的潜在CSRF攻击。

**分布式校验**

在大型网站中，使用Session存储CSRF Token会带来很大的压力。访问单台服务器session是同一个。但是现在的大型网站中，我们的服务器通常不止一台，可能是几十台甚至几百台之多，甚至多个机房都可能在不同的省份，用户发起的HTTP请求通常要经过像Ngnix之类的负载均衡器之后，再路由到具体的服务器上，由于Session默认存储在单机服务器内存中，因此在分布式环境下同一个用户发送的多次HTTP请求可能会先后落到不同的服务器上，导致后面发起的HTTP请求无法拿到之前的HTTP请求存储在服务器中的Session数据，从而使得Session机制在分布式环境下失效，因此在分布式集群中CSRF Token需要存储在Redis之类的公共存储空间。

由于使用Session存储，读取和验证CSRF Token会引起比较大的复杂度和性能问题，目前很多网站采用Encrypted Token Pattern方式。这种方法的Token是一个计算出来的结果，而非随机生成的字符串。这样在校验时无需再去读取存储的Token，只用再次计算一次即可。

这种Token的值通常是使用UserID、时间戳和随机数，通过加密的方法生成。这样既可以保证分布式服务的Token一致，又能保证Token不容易被破解。

在token解密成功之后，服务器可以访问解析值，Token中包含的UserID和时间戳将会被拿来被验证有效性，将UserID与当前登录的UserID进行比较，并将时间戳与当前时间进行比较。

总结

Token是一个比较有效的CSRF防护方法，只要页面没有XSS漏洞泄露Token，那么接口的CSRF攻击就无法成功。

但是此方法的实现比较复杂，需要给每一个页面都写入Token（前端无法使用纯静态页面），每一个Form及Ajax请求都携带这个Token，后端对每一个接口都进行校验，并保证页面Token及请求Token一致。这就使得这个防护策略不能在通用的拦截上统一拦截处理，而需要每一个页面和接口都添加对应的输出和校验。这种方法工作量巨大，且有可能遗漏。

> 验证码和密码其实也可以起到CSRF Token的作用哦，而且更安全。
为什么很多银行等网站会要求已经登录的用户在转账时再次输入密码，现在是不是有一定道理了？

**双重Cookie验证**

在会话中存储CSRF Token比较繁琐，而且不能在通用的拦截上统一处理所有的接口。

那么另一种防御措施是使用双重提交Cookie。利用CSRF攻击不能获取到用户Cookie的特点，我们可以要求Ajax和表单请求携带一个Cookie中的值。

双重Cookie采用以下流程：
- 在用户访问网站页面时，向请求域名注入一个Cookie，内容为随机字符串（例如csrfcookie=v8g9e4ksfhw）。
- 在前端向后端发起请求时，取出Cookie，并添加到URL的参数中（接上例POST [https://www.a.com/comment?csrfcookie=v8g9e4ksfhw](https://www.a.com/comment?csrfcookie=v8g9e4ksfhw)）。
- 后端接口验证Cookie中的字段与URL参数中的字段是否一致，不一致则拒绝。
此方法相对于CSRF Token就简单了许多。可以直接通过前后端拦截的的方法自动化实现。后端校验也更加方便，只需进行请求中字段的对比，而不需要再进行查询和存储Token。

当然，此方法并没有大规模应用，其在大型网站上的安全性还是没有CSRF Token高，原因我们举例进行说明。

由于任何跨域都会导致前端无法获取Cookie中的字段（包括子域名之间），于是发生了如下情况：
- 如果用户访问的网站为[www.a.com](www.a.com)，而后端的api域名为api.a.com。那么在[www.a.com](www.a.com)下，前端拿不到api.a.com的Cookie，也就无法完成双重Cookie认证。
- 于是这个认证Cookie必须被种在a.com下，这样每个子域都可以访问。
- 任何一个子域都可以修改a.com下的Cookie。
- 某个子域名存在漏洞被XSS攻击（例如upload.a.com）。虽然这个子域下并没有什么值得窃取的信息。但攻击者修改了a.com下的Cookie。
- 攻击者可以直接使用自己配置的Cookie，对XSS中招的用户再向[www.a.com](www.a.com)下，发起CSRF攻击。
总结

用双重Cookie防御CSRF的优点：
- 无需使用Session，适用面更广，易于实施。
- Token储存于客户端中，不会给服务器带来压力。
- 相对于Token，实施成本更低，可以在前后端统一拦截校验，而不需要一个个接口和页面添加。
缺点
- Cookie中增加了额外的字段。
- 如果有其他漏洞（例如XSS），攻击者可以注入Cookie，那么该防御方式失效。
- 难以做到子域名的隔离。
- 为了确保Cookie传输安全，采用这种防御方式的最好确保用整站HTTPS的方式，如果还没切HTTPS的使用这种方式也会有风险。
**Samesite Cookie属性**

防止CSRF攻击的办法已经有上面的预防措施。为了从源头上解决这个问题，Google起草了一份草案来改进HTTP协议，那就是为Set-Cookie响应头新增Samesite属性，它用来标明这个 Cookie是个“同站 Cookie”，同站Cookie只能作为第一方Cookie，不能作为第三方Cookie，Samesite 有两个属性值，分别是 Strict 和 Lax，下面分别讲解：

Samesite=Strict

这种称为严格模式，表明这个 Cookie 在任何情况下都不可能作为第三方 Cookie，绝无例外。比如说 b.com 设置了如下 Cookie：

```
Set-Cookie: foo=1; Samesite=Strict
Set-Cookie: bar=2; Samesite=Lax
Set-Cookie: baz=3
```

我们在 a.com 下发起对 b.com 的任意请求，foo 这个 Cookie 都不会被包含在 Cookie 请求头中，但 bar 会。举个实际的例子就是，假如淘宝网站用来识别用户登录与否的 Cookie 被设置成了 Samesite=Strict，那么用户从百度搜索页面甚至天猫页面的链接点击进入淘宝后，淘宝都不会是登录状态，因为淘宝的服务器不会接受到那个 Cookie，其它网站发起的对淘宝的任意请求都不会带上那个 Cookie。

Samesite=Lax

这种称为宽松模式，比 Strict 放宽了点限制：假如这个请求是这种请求（改变了当前页面或者打开了新页面）且同时是个GET请求，则这个Cookie可以作为第三方Cookie。比如说 b.com设置了如下Cookie：

```
Set-Cookie: foo=1; Samesite=Strict
Set-Cookie: bar=2; Samesite=Lax
Set-Cookie: baz=3
```

当用户从 a.com 点击链接进入 b.com 时，foo 这个 Cookie 不会被包含在 Cookie 请求头中，但 bar 和 baz 会，也就是说用户在不同网站之间通过链接跳转是不受影响了。但假如这个请求是从 a.com 发起的对 b.com 的异步请求，或者页面跳转是通过表单的 post 提交触发的，则bar也不会发送。

生成Token放到Cookie中并且设置Cookie的Samesite，Java代码如下：

```
private void addTokenCookieAndHeader(HttpServletRequest httpRequest, HttpServletResponse httpResponse) `{`
        //生成token
        String sToken = this.generateToken();
        //手动添加Cookie实现支持“Samesite=strict”
        //Cookie添加双重验证
        String CookieSpec = String.format("%s=%s; Path=%s; HttpOnly; Samesite=Strict", this.determineCookieName(httpRequest), sToken, httpRequest.getRequestURI());
        httpResponse.addHeader("Set-Cookie", CookieSpec);
        httpResponse.setHeader(CSRF_TOKEN_NAME, token);
    `}`
```

代码源自[OWASP Cross-Site_Request_Forgery #Implementation example](https://www.owasp.org/index.php/Cross-Site_Request_Forgery_%28CSRF%29_Prevention_Cheat_Sheet#Implementation_example)

我们应该如何使用SamesiteCookie

如果SamesiteCookie被设置为Strict，浏览器在任何跨域请求中都不会携带Cookie，新标签重新打开也不携带，所以说CSRF攻击基本没有机会。

但是跳转子域名或者是新标签重新打开刚登陆的网站，之前的Cookie都不会存在。尤其是有登录的网站，那么我们新打开一个标签进入，或者跳转到子域名的网站，都需要重新登录。对于用户来讲，可能体验不会很好。

如果SamesiteCookie被设置为Lax，那么其他网站通过页面跳转过来的时候可以使用Cookie，可以保障外域连接打开页面时用户的登录状态。但相应的，其安全性也比较低。

另外一个问题是Samesite的兼容性不是很好，现阶段除了从新版Chrome和Firefox支持以外，Safari以及iOS Safari都还不支持，现阶段看来暂时还不能普及。

而且，SamesiteCookie目前有一个致命的缺陷：不支持子域。例如，种在topic.a.com下的Cookie，并不能使用a.com下种植的SamesiteCookie。这就导致了当我们网站有多个子域名时，不能使用SamesiteCookie在主域名存储用户登录信息。每个子域名都需要用户重新登录一次。

总之，SamesiteCookie是一个可能替代同源验证的方案，但目前还并不成熟，其应用场景有待观望。

### 防止网站被利用

前面所说的，都是被攻击的网站如何做好防护。而非防止攻击的发生，CSRF的攻击可以来自：
- 攻击者自己的网站。
- 有文件上传漏洞的网站。
- 第三方论坛等用户内容。
- 被攻击网站自己的评论功能等。
对于来自黑客自己的网站，我们无法防护。但对其他情况，那么如何防止自己的网站被利用成为攻击的源头呢？
- 严格管理所有的上传接口，防止任何预期之外的上传内容（例如HTML）。
- 添加Header X-Content-Type-Options: nosniff 防止黑客上传HTML内容的资源（例如图片）被解析为网页。
- 对于用户上传的图片，进行转存或者校验。不要直接使用用户填写的图片链接。
- 当前用户打开其他用户填写的链接时，需告知风险（这也是很多论坛不允许直接在内容中发布外域链接的原因之一，不仅仅是为了用户留存，也有安全考虑）。
## CSRF其他防范措施

对于一线的程序员同学，我们可以通过各种防护策略来防御CSRF，对于QA、SRE、安全负责人等同学，我们可以做哪些事情来提升安全性呢？

**CSRF测试**

CSRFTester是一款CSRF漏洞的测试工具，CSRFTester工具的测试原理大概是这样的，使用代理抓取我们在浏览器中访问过的所有的连接以及所有的表单等信息，通过在CSRFTester中修改相应的表单等信息，重新提交，相当于一次伪造客户端请求，如果修改后的测试请求成功被网站服务器接受，则说明存在CSRF漏洞，当然此款工具也可以被用来进行CSRF攻击。

CSRFTester使用方法大致分下面几个步骤：
- 步骤1：设置浏览器代理
CSRFTester默认使用Localhost上的端口8008作为其代理，如果代理配置成功，CSRFTester将为您的浏览器生成的所有后续HTTP请求生成调试消息。
- 步骤2：使用合法账户访问网站开始测试
我们需要找到一个我们想要为CSRF测试的特定业务Web页面。找到此页面后，选择CSRFTester中的“开始录制”按钮并执行业务功能；完成后，点击CSRFTester中的“停止录制”按钮；正常情况下，该软件会全部遍历一遍当前页面的所有请求。
- 步骤3：通过CSRF修改并伪造请求
之后，我们会发现软件上有一系列跑出来的记录请求，这些都是我们的浏览器在执行业务功能时生成的所有GET或者POST请求。通过选择列表中的某一行，我们现在可以修改用于执行业务功能的参数，可以通过点击对应的请求修改query和form的参数。当修改完所有我们希望诱导用户form最终的提交值，可以选择开始生成HTML报告。
- 步骤4：拿到结果如有漏洞进行修复
首先必须选择“报告类型”。报告类型决定了我们希望受害者浏览器如何提交先前记录的请求。目前有5种可能的报告：表单、iFrame、IMG、XHR和链接。一旦选择了报告类型，我们可以选择在浏览器中启动新生成的报告，最后根据报告的情况进行对应的排查和修复。

**CSRF监控**

对于一个比较复杂的网站系统，某些项目、页面、接口漏掉了CSRF防护措施是很可能的。

一旦发生了CSRF攻击，我们如何及时的发现这些攻击呢？

CSRF攻击有着比较明显的特征：
- 跨域请求。
- GET类型请求Header的MIME类型大概率为图片，而实际返回Header的MIME类型为Text、JSON、HTML。
我们可以在网站的代理层监控所有的接口请求，如果请求符合上面的特征，就可以认为请求有CSRF攻击嫌疑。我们可以提醒对应的页面和项目负责人，检查或者 Review其CSRF防护策略。

### 个人用户CSRF安全的建议

经常上网的个人用户，可以采用以下方法来保护自己：
- 使用网页版邮件的浏览邮件或者新闻也会带来额外的风险，因为查看邮件或者新闻消息有可能导致恶意代码的攻击。
- 尽量不要打开可疑的链接，一定要打开时，使用不常用的浏览器。
### 总结

简单总结一下上文的防护策略：
- CSRF自动防御策略：同源检测（Origin 和 Referer 验证）。
- CSRF主动防御措施：Token验证 或者 双重Cookie验证 以及配合Samesite Cookie。
- 保证页面的幂等性，后端接口不要在GET页面中做用户操作。
为了更好的防御CSRF，最佳实践应该是结合上面总结的防御措施方式中的优缺点来综合考虑，结合当前Web应用程序自身的情况做合适的选择，才能更好的预防CSRF的发生。



## 历史案例

### WordPress的CSRF漏洞

2012年3月份，WordPress发现了一个CSRF漏洞，影响了WordPress 3.3.1版本，WordPress是众所周知的博客平台，该漏洞可以允许攻击者修改某个Post的标题，添加管理权限用户以及操作用户账户，包括但不限于删除评论、修改头像等等。具体的列表如下:
- Add Admin/User
- Delete Admin/User
- Approve comment
- Unapprove comment
- Delete comment
- Change background image
- Insert custom header image
- Change site title
- Change administrator’s email
- Change WordPress Address
- Change Site Address
那么这个漏洞实际上就是攻击者引导用户先进入目标的WordPress，然后点击其钓鱼站点上的某个按钮，该按钮实际上是表单提交按钮，其会触发表单的提交工作，添加某个具有管理员权限的用户，实现的码如下：

```
&lt;html&gt; 
&lt;body onload="javascript:document.forms[0].submit()"&gt; 
&lt;H2&gt;CSRF Exploit to add Administrator&lt;/H2&gt; 
&lt;form method="POST" name="form0" action="http://&lt;wordpress_ip&gt;:80/wp-admin/user-new.php"&gt; 
&lt;input type="hidden" name="action" value="createuser"/&gt; 
&lt;input type="hidden" name="_wpnonce_create-user" value="&lt;sniffed_value&gt;"/&gt; 
&lt;input type="hidden" name="_wp_http_referer" value="%2Fwordpress%2Fwp-admin%2Fuser-new.php"/&gt; 
&lt;input type="hidden" name="user_login" value="admin2"/&gt; 
&lt;input type="hidden" name="email" value="admin2@admin.com"/&gt; 
&lt;input type="hidden" name="first_name" value="admin2@admin.com"/&gt; 
&lt;input type="hidden" name="last_name" value=""/&gt; 
&lt;input type="hidden" name="url" value=""/&gt; 
&lt;input type="hidden" name="pass1" value="password"/&gt; 
&lt;input type="hidden" name="pass2" value="password"/&gt; 
&lt;input type="hidden" name="role" value="administrator"/&gt; 
&lt;input type="hidden" name="createuser" value="Add+New+User+"/&gt; 
&lt;/form&gt; 
&lt;/body&gt; 
&lt;/html&gt;
```

### YouTube的CSRF漏洞

2008年，有安全研究人员发现，YouTube上几乎所有用户可以操作的动作都存在CSRF漏洞。如果攻击者已经将视频添加到用户的“Favorites”，那么他就能将他自己添加到用户的“Friend”或者“Family”列表，以用户的身份发送任意的消息，将视频标记为不宜的，自动通过用户的联系人来共享一个视频。例如，要把视频添加到用户的“Favorites”，攻击者只需在任何站点上嵌入如下所示的IMG标签：

```
&lt;img src="http://youtube.com/watch_ajax?action_add_favorite_playlist=1&amp;video_
id=[VIDEO ID]&amp;playlist_id=&amp;add_to_favorite=1&amp;show=1&amp;button=AddvideoasFavorite"/&gt;
```

攻击者也许已经利用了该漏洞来提高视频的流行度。例如，将一个视频添加到足够多用户的“Favorites”，YouTube就会把该视频作为“Top Favorites”来显示。除提高一个视频的流行度之外，攻击者还可以导致用户在毫不知情的情况下将一个视频标记为“不宜的”，从而导致YouTube删除该视频。

这些攻击还可能已被用于侵犯用户隐私。YouTube允许用户只让朋友或亲属观看某些视频。这些攻击会导致攻击者将其添加为一个用户的“Friend”或“Family”列表，这样他们就能够访问所有原本只限于好友和亲属表中的用户观看的私人的视频。

攻击者还可以通过用户的所有联系人名单（“Friends”、“Family”等等）来共享一个视频，“共享”就意味着发送一个视频的链接给他们，当然还可以选择附加消息。这条消息中的链接已经并不是真正意义上的视频链接，而是一个具有攻击性的网站链接，用户很有可能会点击这个链接，这便使得该种攻击能够进行病毒式的传播。



## 参考文献
- Mozilla wiki. [Security-Origin](https://wiki.mozilla.org/Security/Origin).
- OWASP. [Cross-Site_Request_Forgery_(CSRF)_Prevention_Cheat_Sheet](https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)_Prevention_Cheat_Sheet).
- Gmail Security Hijack Case. [Google-Gmail-Security-Hijack](https://www.davidairey.com/google-gmail-security-hijack/).
- Netsparker Blog. [Same-Site-Cookie-Attribute-Prevent-Cross-site-Request-Forgery](https://www.netsparker.com/blog/web-security/same-site-cookie-attribute-prevent-cross-site-request-forgery/).
- MDN. [Same-origin_policy#IE_Exceptions](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy#IE_Exceptions).

