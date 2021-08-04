> 原文链接: https://www.anquanke.com//post/id/246005 


# 梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之客户端漏洞篇 - 跨站请求伪造(CSRF)专题


                                阅读量   
                                **48145**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t0102b91d5e65628830.png)](https://p2.ssl.qhimg.com/t0102b91d5e65628830.png)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 客户端漏洞篇介绍

> 相对于服务器端漏洞篇，客户端漏洞篇会更加复杂，需要在我们之前学过的服务器篇的基础上去利用。



## 客户端漏洞篇 – 跨站请求伪造(CSRF)专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFCSRF%EF%BC%9F"></a>什么是CSRF？

CSRF全称为cross-site request forgery，译为跨站请求伪造。有的站点会采用同源策略，如果想要利用受害者身份去执行恶意操作需要攻击者诱使受害者提交那个恶意请求，也就是借刀杀人。

### <a class="reference-link" name="CSRF%E6%98%AF%E5%A6%82%E4%BD%95%E8%BF%90%E4%BD%9C%E7%9A%84%EF%BC%9F"></a>CSRF是如何运作的？

成功发动CSRF攻击有三个因素
- 一个相关的操作，即你想利用CSRF让受害者干什么，比如权限操作、修改数据等
- 基于cookie的会话处理，cookie是唯一能够通过document.cookie()函数直接获取到的可以用来进行会话处理的字段，所以要想成功发动CSRF需要那个应用程序仅通过cookie进行会话处理。
- 没有不可预测的参数，因为CSRF攻击是要提前构造请求的，所以如果需要填写一些不可预测的参数，如密码，就不能成功发动CSRF
假如某个应用程序存在一个功能点可以修改邮箱地址，会发出这样的请求

```
POST /email/change HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 30
Cookie: session=yvthwsztyeQkAPzeQ5gHgTvlyxHfsAfE

email=wiener@normal-user.com

```

根据上面讲的三个要素，这个功能点是可以成功发动CSRF的，因为它可以执行攻击者感兴趣的操作(修改邮箱)，然后仅通过cookie来进行会话处理，而且参数只有一个email，所以是可以成功发动CSRF的。这样我们就可以构造这样的CSRF页面去触发它。

```
&lt;html&gt;
  &lt;body&gt;
    &lt;form action="https://vulnerable-website.com/email/change" method="POST"&gt;
      &lt;input type="hidden" name="email" value="pwned@evil-user.net" /&gt;
    &lt;/form&gt;
    &lt;script&gt;
      document.forms[0].submit();
    &lt;/script&gt;
  &lt;/body&gt;
&lt;/html&gt;
```

当我们把这个CSRF页面投放到受害者那里时会因为document.forms[0].submit()自动提交一个POST表单请求，同时会自动使用受害者的Cookie发送，即表示由受害者自主提交的修改邮箱请求。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E6%9E%84%E9%80%A0%E4%B8%80%E4%B8%AACSRF%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何构造一个CSRF攻击？

首先我们找到想要用来构造CSRF的请求，然后在burp中右键Engagement tools / Generate CSRF PoC，然后就会自动生成一个CSRF页面了。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E6%97%A0%E9%98%B2%E6%8A%A4%E7%9A%84CSRF%E6%BC%8F%E6%B4%9E"></a>配套靶场：无防护的CSRF漏洞

前面介绍过，我们需要先登录给定的用户抓取修改邮箱的请求包

[![](https://p4.ssl.qhimg.com/t015371dac67733d63a.png)](https://p4.ssl.qhimg.com/t015371dac67733d63a.png)

我们看到这个功能还是很好用的，可以自动生成CSRF页面，然后我们将其复制到Exploit Server投放给受害者，就能成功修改其邮箱地址了。

[![](https://p1.ssl.qhimg.com/t01c2f62361e9da17a8.png)](https://p1.ssl.qhimg.com/t01c2f62361e9da17a8.png)

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E5%88%A9%E7%94%A8CSRF%EF%BC%9F"></a>如何利用CSRF？

在XSS专题中其实我们已经有所提及了，img会自动向src属性指定的域名发出请求，有的应用程序允许通过发送GET请求修改邮箱地址，所以我们可以将src设置为带有GET参数的CSRF URL，当加载该img时即会触发CSRF。

### <a class="reference-link" name="XSS%E5%92%8CCSRF%E6%9C%89%E4%BB%80%E4%B9%88%E5%8C%BA%E5%88%AB%EF%BC%9F"></a>XSS和CSRF有什么区别？

XSS是可以允许攻击者在受害者浏览器执行任意JS脚本，而CSRF是允许攻击者诱使受害者执行他们本不打算执行的操作。相比之下，XSS的危害更大，因为XSS能够执行任意JS脚本，包括发送一些请求，而CSRF只能执行没有实施CSRF防护的功能。XSS可以将结果发送到远程服务器接收，而CSRF只能发出请求而已。

### <a class="reference-link" name="CSRF%20Token%E5%8F%AF%E4%BB%A5%E7%94%A8%E6%9D%A5%E7%BC%93%E8%A7%A3XSS%E5%90%97%EF%BC%9F"></a>CSRF Token可以用来缓解XSS吗？

CSRF Token确实可以缓解一些XSS攻击，比如考虑这样的一个XSS payload

```
https://insecure-website.com/status?message=&lt;script&gt;/*+Bad+stuff+here...+*/&lt;/script&gt;
```

我们在引入了CSRF Token之后就可以用来缓解这样的XSS攻击

```
https://insecure-website.com/status?csrf-token=CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz&amp;message=&lt;script&gt;/*+Bad+stuff+here...+*/&lt;/script&gt;
```

应用程序会验证CSRF Token，如果是无效的就会拒绝这个请求。但是CSRF Token不能缓解存储型XSS攻击。

### <a class="reference-link" name="CSRF%20Token"></a>CSRF Token

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFCSRF%20Token%EF%BC%9F"></a>什么是CSRF Token？

CSRF Token是一个唯一的、保密的、不可预测的字符串，它由服务器端生成然后包含在后续的请求中。当服务器端接收到请求后会验证CSRF Token，如果其已经失效则会拒绝该请求。这就打破了可以成功构造CSRF的三个因素了，即参数不可预测，所以可以用来缓解CSRF攻击。

### <a class="reference-link" name="CSRF%20Token%E5%BA%94%E8%AF%A5%E6%80%8E%E6%A0%B7%E7%94%9F%E6%88%90%EF%BC%9F"></a>CSRF Token应该怎样生成？

CSRF Token应该具有高度地不可预测性，可以使用高强度的伪随机数生成器(PRNG)，并且以时间戳加上静态密钥作为其种子。如果想要更高的不可预测性，我们可以将随机数与用户的个人标识信息组合，然后再整体做一个哈希处理。

### <a class="reference-link" name="CSRF%20Token%E5%BA%94%E8%AF%A5%E6%80%8E%E6%A0%B7%E4%BC%A0%E8%BE%93%EF%BC%9F"></a>CSRF Token应该怎样传输？

一般情况，服务器会通过隐藏字段传输给客户端，然后在提交表单的时候自动加进去。在XSS专题中我们介绍了利用悬挂标记攻击获取CSRF Token的攻击手段，所以我们应该把该字段放在表单最前面。并且尽量不要以GET请求参数和请求标头的方式传输。

### <a class="reference-link" name="CSRF%20Token%E5%BA%94%E8%AF%A5%E6%80%8E%E6%A0%B7%E9%AA%8C%E8%AF%81%EF%BC%9F"></a>CSRF Token应该怎样验证？

应该在服务器端建立CSRF Token与用户会话的绑定关系，当接收到某个请求时，验证请求中的CSRF Token是否与所绑定的用户会话匹配，不匹配则拒绝该请求。

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8SameSite%20cookie%E7%BC%93%E8%A7%A3CSRF%E6%94%BB%E5%87%BB"></a>使用SameSite cookie缓解CSRF攻击

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFSameSite%20cookie%EF%BC%9F"></a>什么是SameSite cookie？

SameSite是cookie字段的一个属性，用于定义跨站请求的提交方式，以防止浏览器对于任意来源的请求都自动填充cookie

### <a class="reference-link" name="SameSite%E6%9C%89%E5%93%AA%E4%BA%9B%E4%B8%8D%E5%90%8C%E7%9A%84%E5%80%BC%EF%BC%8C%E4%BD%9C%E7%94%A8%E6%98%AF%E4%BB%80%E4%B9%88%EF%BC%9F"></a>SameSite有哪些不同的值，作用是什么？

**<a class="reference-link" name="SameSite=Strict"></a>SameSite=Strict**

当SameSite被设置为这个值时，浏览器将不会对第三方网站自动填充cookie，但是有一个缺点就是普通用户需要重新登录一次

**<a class="reference-link" name="SameSite=Lax"></a>SameSite=Lax**

当SameSite被设置成这个值时，浏览器虽然会自动填充cookie，但是有两个条件
- 请求方法为GET(**除此之外的方法不会自动填充**)
- 请求来自顶级框架(**除此之外的请求不会自动填充**)
但是有的网站也会通过GET请求方法去进行一些敏感操作，所以不太建议仅利用SameSite来进行防御CSRF攻击，一般会搭配CSRF Token组合防御

### <a class="reference-link" name="%E5%B8%B8%E8%A7%81%E7%9A%84CSRF%E6%BC%8F%E6%B4%9E"></a>常见的CSRF漏洞

### <a class="reference-link" name="%E4%BE%9D%E8%B5%96%E8%AF%B7%E6%B1%82%E6%96%B9%E6%B3%95%E7%9A%84CSRF%E9%AA%8C%E8%AF%81"></a>依赖请求方法的CSRF验证

有的应用系统仅会验证POST请求中的CSRF Token，但是不会验证GET请求下的，这时候会跳过验证

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BE%9D%E8%B5%96%E8%AF%B7%E6%B1%82%E6%96%B9%E6%B3%95%E7%9A%84CSRF%20Token%E9%AA%8C%E8%AF%81"></a>配套靶场：依赖请求方法的CSRF Token验证

首先我们将正常修改邮箱请求中的CSRF Token去掉观察一下会发生什么

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0167d3ad0a25482588.png)

看到会提示缺少参数，但是如果我们右键change request method将POST请求转换成GET请求再观察一下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018b342ea8fa28ce7a.png)

发现居然不需要CSRF Token参数就可以，说明我们成功发动了CSRF

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0195d334e5ebc22ad1.png)

### <a class="reference-link" name="%E4%BE%9D%E8%B5%96CSRF%20Token%E6%98%AF%E5%90%A6%E5%AD%98%E5%9C%A8%E7%9A%84CSRF%E9%AA%8C%E8%AF%81"></a>依赖CSRF Token是否存在的CSRF验证

有的应用系统仅会在请求中存在CSRF Token的情况下对其进行验证，如果不存在该参数则不会进行验证

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BE%9D%E8%B5%96CSRF%20Token%E6%98%AF%E5%90%A6%E5%AD%98%E5%9C%A8%E7%9A%84CSRF%E9%AA%8C%E8%AF%81"></a>配套靶场：依赖CSRF Token是否存在的CSRF验证

知识点讲的很清楚，当我们去掉请求中的CSRF Token参数时即不会验证该字段

[![](https://p4.ssl.qhimg.com/t01fd685ffb5977d56a.png)](https://p4.ssl.qhimg.com/t01fd685ffb5977d56a.png)

发现可以成功发动CSRF

[![](https://p0.ssl.qhimg.com/t01b275da401171ccd1.png)](https://p0.ssl.qhimg.com/t01b275da401171ccd1.png)

### <a class="reference-link" name="CSRF%20Token%E6%9C%AA%E4%B8%8E%E7%94%A8%E6%88%B7%E4%BC%9A%E8%AF%9D%E7%BB%91%E5%AE%9A"></a>CSRF Token未与用户会话绑定

有的应用系统仅会验证CSRF Token的有效性，而不会验证该Token是否属于当前用户，即不会与用户会话绑定

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9ACSRF%20Token%E6%9C%AA%E4%B8%8E%E7%94%A8%E6%88%B7%E4%BC%9A%E8%AF%9D%E7%BB%91%E5%AE%9A"></a>配套靶场：CSRF Token未与用户会话绑定

因为CSRF Token未与用户会话绑定，所以我们只需要一个有效的CSRF Token就可以，于是我们登录测试用户，然后抓取修改邮箱的请求包，制作成CSRF页面，再将这个包丢掉，将这个页面利用Exploit Server投放给受害者。

[![](https://p5.ssl.qhimg.com/t0150f8232aa7738e91.png)](https://p5.ssl.qhimg.com/t0150f8232aa7738e91.png)

因为CSRF Token是有效的，所以是可以成功发动CSRF的

[![](https://p2.ssl.qhimg.com/t01b87a05ae16b0e437.png)](https://p2.ssl.qhimg.com/t01b87a05ae16b0e437.png)

### <a class="reference-link" name="CSRF%20Token%E4%B8%8E%E9%9D%9E%E4%BC%9A%E8%AF%9Dcookie%E7%BB%91%E5%AE%9A"></a>CSRF Token与非会话cookie绑定

有的应用系统虽然将CSRF Token与Cookie中某个参数值绑定了，但是并没有与session这个Cookie参数绑定，这样还是会导致CSRF Token与绑定的参数组合可以被任意用户用于请求。<br>
在构造CSRF POC有一个比较有趣的操作，需要在用burp生成CSRF链接的时候将自动提交标签改成img标签，将提交表单事件设置在onerror属性中，将利用CLRF注入Cookie的页面设置在src属性中。(注：应用Set-Cookie参数值注入Cookie)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9ACSRF%20Token%E4%B8%8E%E9%9D%9E%E4%BC%9A%E8%AF%9Dcookie%E7%BB%91%E5%AE%9A"></a>配套靶场：CSRF Token与非会话cookie绑定

首先我们修改一下cookie中的session，观察一下

[![](https://p5.ssl.qhimg.com/t012208c13843c284e1.png)](https://p5.ssl.qhimg.com/t012208c13843c284e1.png)

发现修改了session以后只是会提示未登录，那么我们修改一下csrfKey参数的值呢

[![](https://p2.ssl.qhimg.com/t01a14bb456de642d90.png)](https://p2.ssl.qhimg.com/t01a14bb456de642d90.png)

说明CSRF Token并未与session绑定，而是与csrfKey绑定的，根据cookie的传递性，我们可以在其他页面提前把csrfKey注入进去，这里我们利用img与onerror组合的XSS以及CLRF技术来构造CSRF

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014584644442cc92da.png)

当受害者点击CSRF链接时会先触发CLRF注入Set-Cookie参数值将csrfKey值添加到Cookie中，然后再用附有与csrfKey对应的CSRF Token的请求去提交修改邮箱请求

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e7138228a3dc2036.png)

### <a class="reference-link" name="CSRF%20Token%E8%A2%AB%E7%AE%80%E5%8D%95%E5%A4%8D%E5%88%B6%E5%88%B0cookie%E4%B8%AD"></a>CSRF Token被简单复制到cookie中

有的应用程序偷工减料，仅将CSRF Token简单复制到cookie头中，然后仅验证两者是否一致，这样很容易通过验证

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9ACSRF%20Token%E8%A2%AB%E7%AE%80%E5%8D%95%E5%A4%8D%E5%88%B6%E5%88%B0cookie%E4%B8%AD"></a>配套靶场：CSRF Token被简单复制到cookie中

经过测试，使用测试用户提交的修改邮箱请求中的CSRF Token可以无限次使用，所以我们直接由此构造CSRF页面

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b8fdad8b645a5253.png)

将该页面投放到受害者之后即可触发CSRF

[![](https://p3.ssl.qhimg.com/t01b685f74a706e4f52.png)](https://p3.ssl.qhimg.com/t01b685f74a706e4f52.png)

### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EReferer%E6%8A%B5%E5%BE%A1CSRF%E6%94%BB%E5%87%BB"></a>基于Referer抵御CSRF攻击

基于Referer头的防护原理就是检查请求的来源是不是属于该应用程序的域，不过防护效果较差

### <a class="reference-link" name="%E4%BE%9D%E8%B5%96%E5%A4%B4%E9%83%A8%E6%98%AF%E5%90%A6%E5%AD%98%E5%9C%A8%E7%9A%84Referer%E9%AA%8C%E8%AF%81"></a>依赖头部是否存在的Referer验证

这种验证手段与之前的类似，即Referer存在即验证，不存在即不验证，通过以下模板来构造CSRF页面

```
&lt;meta name="referrer" content="no-referrer"&gt;
```

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BE%9D%E8%B5%96%E5%A4%B4%E9%83%A8%E6%98%AF%E5%90%A6%E5%AD%98%E5%9C%A8%E7%9A%84Referer%E9%AA%8C%E8%AF%81"></a>配套靶场：依赖头部是否存在的Referer验证

与前面的CSRF验证类似，只不过CSRF页面语句不太一样

[![](https://p5.ssl.qhimg.com/t01013b620a81e60b51.png)](https://p5.ssl.qhimg.com/t01013b620a81e60b51.png)

这样就不会自动在请求中加入referer字段，从而绕过验证

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fc8528a8ec05c906.png)

### <a class="reference-link" name="%E9%94%99%E8%AF%AF%E5%9C%B0%E9%AA%8C%E8%AF%81Referer"></a>错误地验证Referer

有的时候仅验证Referer头中是否包含预期域名，而不验证是否有其他不可信域名在里面，所以我们可以构造这样奇葩的URL

```
http://vulnerable-website.com.attacker-website.com/csrf-attack
http://attacker-website.com/csrf-attack?vulnerable-website.com
```

有的浏览器会将Referer中的查询字符串拆出来，所以我们可以添加Referrer-Policy: unsafe-url这样的头部字段以保证不会被拆出来

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E9%94%99%E8%AF%AF%E5%9C%B0%E9%AA%8C%E8%AF%81Referer"></a>配套靶场：错误地验证Referer

这里我们需要介绍一下history.pushState，这个函数顾名思义，就是插入历史记录的，所以这也就是为什么第三个参数的值修改为与攻击链接同源后即可绕过错误地Referer头验证机制，所以我们这样构造CSRF页面

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011c7799cceeeb1a80.png)

这样我们就可以绕过验证Referer来发动CSRF了

[![](https://p2.ssl.qhimg.com/t014064a13b0f5625bf.png)](https://p2.ssl.qhimg.com/t014064a13b0f5625bf.png)



## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之客户端漏洞篇 – 跨站请求伪造(CSRF)专题的全部内容啦，本专题主要讲了CSRF的形成原理、常见的利用、防护、防护的绕过等，感兴趣的同学可以在评论区进行讨论，嘻嘻嘻。
