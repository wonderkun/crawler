> 原文链接: https://www.anquanke.com//post/id/97671 


# JSONP与CORS漏洞挖掘


                                阅读量   
                                **452231**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t019d033475da7e56ba.jpg)](https://p0.ssl.qhimg.com/t019d033475da7e56ba.jpg)



## 前言

本文从笔者自己对同源策略的理解来谈谈与之相关的JSONP劫持和CORS错误配置这两类安全问题。



## 同源策略(SOP)

同源策略限制从一个源加载的文档或脚本与来自另一个源的资源进行交互,这是一个用于隔离潜在恶意文件的关键的安全机制.简单说就是浏览器的一种安全策略。

“同源”包括三个条件:
- 同协议
- 同域名
- 同端口
同源策略的具体表现举例:当attacker.me试图获取victim.me下的资源,浏览器会阻止**返回**该资源。

[![](https://p1.ssl.qhimg.com/t016a0650fbbf8fdfc8.png)](https://p1.ssl.qhimg.com/t016a0650fbbf8fdfc8.png)

[![](https://p1.ssl.qhimg.com/t015b27ad74982dad05.png)](https://p1.ssl.qhimg.com/t015b27ad74982dad05.png)

(该请求虽然发出去了,但浏览器拒绝返回响应内容)[![](https://p0.ssl.qhimg.com/t01d8f8c89a2642e938.png)](https://p0.ssl.qhimg.com/t01d8f8c89a2642e938.png)



## 跨域

虽然同源策略在安全方面起到了很好的防护作用,但也在一定程度上限制了一些前端功能的实现,所以就有了许多跨域的手段。



### 可跨域的标签

所有带src或href属性的标签以及部分其他标签可以跨域:

@font-face可以引入跨域字体。

我为什么要说这些标签呢,因为下文的JSONP跨域就是利用script标签来实现的。

### document.domain

同一主域的不同子域可以设置document.domain为主域来让他们同域,并且子域的协议和端口都要一致。

document.domain只能设置往上设置域名,需要载入iframe来相互操作。

举例:将a.victim.me和b.victim.me的域设置为victim.me,实现跨域。

[![](https://p3.ssl.qhimg.com/t012412220381e8f58a.png)](https://p3.ssl.qhimg.com/t012412220381e8f58a.png)

### JSONP

JSONP跨域巧妙的利用了script标签能跨域的特点,实现了json的跨域传输。

实例,例如这样一个获取客户端IP的接口,

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d973d4324b888852.png)

callback参数从客户端传入,返回的`hack(`{`"ip": "***.***.159.159"`}`);`,形式正好是在调用hack()函数。

所以只要我们在调用该接口处事先定义好这个hack()函数,就能获取到传入的参数``{`"ip": "***.***.159.159"`}``,从而实现了json的跨域传输。

[![](https://p4.ssl.qhimg.com/t013a303f05d3cf8375.png)](https://p4.ssl.qhimg.com/t013a303f05d3cf8375.png)

当这个接口没有验证Referer头的时候,就存在JSONP劫持漏洞,即在任何域下都能窃取到传输的数据。

当接口返回的是一些敏感数据时(如CSRF TOKEN,用户个人信息等),危害是很大的。

具体案例可以看:

[新浪微博之点击我的链接就登录你的微博(JSONP劫持)](http://cb.drops.wiki/bugs/wooyun-2016-0204941.html)

[苏宁易购多接口问题可泄露用户姓名、地址、订单商品（jsonp案例）](http://cb.drops.wiki/bugs/wooyun-2015-0118712.html)

防御策略就是检查referer头是否在白名单内。

### 跨源资源共享(CORS)

跨源资源共享 (CORS) 定义了在一个域中加载的客户端 Web 应用程序与另一个域中的资源交互的方式,需要浏览器和服务器共同支持才能实现

浏览器将CORS请求分成两类：简单请求（simple request）和非简单请求（not-so-simple request)

具体可以参考[CORS通信](http://javascript.ruanyifeng.com/bom/cors.html)

CORS的配置很简单,以PHP为例,

这里在victim.me下设置了一个白名单:attacker.me,于是attacker.me就能跨域到victim.me

[![](https://p5.ssl.qhimg.com/t014c5eb66d4351e5fd.png)](https://p5.ssl.qhimg.com/t014c5eb66d4351e5fd.png)

此时这个xhr是没有携带cookie的,如果需要支持cookie,还需要服务端配置:

同时在客户端把withCredentials设置为true

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012d23fdccaaf30c6d.png)

还有一种特殊情况,就是Access-Control-Allow-Origin设置成通配符”*”时,表示允许任何域名跨源。

如果再把Access-Control-Allow-Credentials设置为true,允许客户端带上cookie的话,无疑此时是非常危险的.因为攻击者很容易就能窃取到用户个人的数据。

所以浏览器加上了最后一道防线,当

这种配置出现时,浏览器会拒接呈现服务端返回的资源.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013bdae8331ec31eea.png)

客户端不带cookie请求的话还是会正常呈现的,因为cookie是一种身份标识,一旦浏览器标识了用户身份,那么返回的数据必然属于用户个人,所以浏览器设计了这种措施来保护用户数据不被泄露。

尽管CORS在设计上考虑到了安全问题,但是用户在配置时还是常出现很多错误。

例如设置”Access-Control-Allow-Origin”的白名单时,正则写的不正确,导致预期外的域名可以跨域。

笔者在不久前就遇到了这样一个案例。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015d25d9d27e8dea63.png)

这个接口用于返回用户的地址等数据,但正则没写对。

程序员想匹配domain.com及其任意子域,我推测他可能写的是`.*domain\.com`

结果导致了使用evildomain.com或者domain.com.evil.me也能匹配上,从而被绕过。

POC:

[![](https://p0.ssl.qhimg.com/t01d51ee5219bf306c6.png)](https://p0.ssl.qhimg.com/t01d51ee5219bf306c6.png)

国内这方面的案例太少,很多人觉得这些不痛不痒的洞没什么危害,国外可以看到一些案例:

[Tricky CORS Bypass in Yahoo! View](http://www.freebuf.com/articles/web/158529.html)

[Security impact of a misconfigured CORS implementation](https://yassineaboukir.com/blog/security-impact-of-a-misconfigured-cors-implementation/)

这类问题的防御措施是正确的配置Access-Control-Allow-Origin,尤其是配置为具有”通配”效果的域名时,一定要谨慎。



## 总结

只要理解了同源策略,JSONP和CORS就很容易理解了。

我以前接触同源策略最大的一个误区就是:认为同源策略阻止了请求的发送。

其实,无论是同源策略还是CORS,都是浏览器阻止了响应的呈现,而非请求。

最后,JSONP劫持和CORS错误配置这两类问题已经出现多年,但是现在还是大量出现,相当重要的一个原因是厂商不够重视.认为传输的数据并不重要,但是一旦因为这些小问题,击溃你的CSRF防御甚至账户认证体系时,可能就为时已晚了。



## 参考

[CORS通信](http://javascript.ruanyifeng.com/bom/cors.html)

[Exploiting CORS Misconfigurations for Bitcoins and Bounties](blog.portswigger.net/2016/10/exploiting-cors-misconfigurations-for.html)
