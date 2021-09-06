> 原文链接: https://www.anquanke.com//post/id/246515 


# 梨子带你刷burpsuite靶场之高级漏洞篇 - HTTP Host头攻击专题


                                阅读量   
                                **21462**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01d5f54a27f9529062.jpg)](https://p3.ssl.qhimg.com/t01d5f54a27f9529062.jpg)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 高级漏洞篇介绍

> 相对于服务器端漏洞篇和客户端漏洞篇，高级漏洞篇需要更深入的知识以及更复杂的利用手段，该篇也是梨子的全程学习记录，力求把漏洞原理及利用等讲的通俗易懂。



## 高级漏洞篇 – HTTP Host头攻击专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFHTTP%20Host%E5%A4%B4%EF%BC%9F"></a>什么是HTTP Host头？

从HTTP/1.1开始，HTTP Host头是强制性的请求头。它指定客户端要访问的域名或IP。例如

```
GET /web-security HTTP/1.1
Host: portswigger.net
```

我们在前面的专题有讲过我们可以通过一些其他HTTP请求头覆盖Host的值以向指定的新的域名或IP发出该请求。

### <a class="reference-link" name="%E8%AE%BE%E7%BD%AEHTTP%20Host%E5%A4%B4%E6%9C%89%E4%BB%80%E4%B9%88%E4%BD%9C%E7%94%A8%EF%BC%9F"></a>设置HTTP Host头有什么作用？

现在的互联网规模这么大，为了节约资源，会选择将多个应用程序部署在同一个IP上。HTTP Host头就是用来区分用户欲请求的是哪个应用程序。目前有以下几种情况是需要使用这种办法的。

### <a class="reference-link" name="%E8%99%9A%E6%8B%9F%E4%B8%BB%E6%9C%BA"></a>虚拟主机

虚拟主机就是将一台物理服务器虚拟成多台服务器用于部署不同的应用程序。这种情况有时会出现在SaaS中。对于访问应用程序的用户来说，他们可能并不能察觉到这些应用程序是部署在同一个IP上的。

### <a class="reference-link" name="%E9%80%9A%E8%BF%87%E4%B8%AD%E8%BD%AC%E8%B7%AF%E7%94%B1%E6%B5%81%E9%87%8F"></a>通过中转路由流量

另一种情况是不同的应用程序部署在不同的物理服务器上，但是所有的流量都会经过一个中转进行流量路由，一般通过负载均衡或反向代理的技术实现的。这种技术一般应用于CDN中。



## 什么是HTTP Host头攻击？

应用程序有时会将Host值拼接到某些地方，但是由于Host的值是可以通过burp手动修改的，所以就可能会导致一些恶意的拼接，HTTP Host头攻击可以发动这些攻击
- Web缓存投毒
- 特定功能点的商业逻辑漏洞
- 基于路由的SSRF
- 经典服务器端漏洞，如Sql注入等


## 如何测试使用HTTP Host头的漏洞？

### <a class="reference-link" name="%E6%8F%90%E4%BE%9B%E4%BB%BB%E6%84%8F%E7%9A%84HTTP%20Host%E5%A4%B4"></a>提供任意的HTTP Host头

这一步很明显，就是我们尝试将Host头修改成任意域名或IP，比如我们常用的度度，然后观察响应是否会有变化，以此来检测是否存在HTTP Host头攻击。

### <a class="reference-link" name="%E6%A3%80%E6%9F%A5%E6%9C%89%E7%BC%BA%E9%99%B7%E7%9A%84%E9%AA%8C%E8%AF%81%E7%82%B9"></a>检查有缺陷的验证点

有的是否应用程序并不会直接返回Invalid Host header，而是有一些其他的处理措施。有些对Host头的验证点的解析规则是有缺陷的，比如仅会验证域名而不验证端口号。这个知识点其实我们在Web缓存投毒专题中介绍过，通过把payload附在端口号中从而将其反馈到响应中。例如

```
GET /example HTTP/1.1
Host: vulnerable-website.com:bad-stuff-here
```

有的应用程序只会验证是否以允许的子域结尾，但是我们让Host以它结尾即可，例如

```
GET /example HTTP/1.1
Host: notvulnerable-website.com
```

也可以直接这样

```
GET /example HTTP/1.1
Host: hacked-subdomain.vulnerable-website.com
```

还有一些其他的利用解析的缺陷的，可以回去翻看SSRF和Origin头解析错误方面的内容。

### <a class="reference-link" name="%E5%8F%91%E9%80%81%E6%A8%A1%E6%A3%B1%E4%B8%A4%E5%8F%AF%E7%9A%84%E8%AF%B7%E6%B1%82"></a>发送模棱两可的请求

有的时候你不知道目标应用程序有没有做了负载均衡或反向代理之类的，我们可以发送一些模棱两可的请求，这样可以通过响应的差异判断我们的请求被发送到后面的哪一台目标了。我们大概可以从下面几种方式尝试构造这样的请求。

**<a class="reference-link" name="%E6%B3%A8%E5%85%A5%E5%A4%9A%E4%B8%AAHost%E5%A4%B4"></a>注入多个Host头**

有的时候我们可以添加多个Host头，而且一般开发者并没有预料到这种情况而没有设置任何处理措施，这就可能导致某个Host头会覆盖掉另一个Host头的值，例如

```
GET /example HTTP/1.1
Host: vulnerable-website.com
Host: bad-stuff-here
```

如果服务器端会将第二个Host头优先于第一个Host头，就会覆盖掉它的值，然后中转组件会因为第一个Host头指定了正确的目标而照常转发这个请求包，这样就能保证它可以顺利到达服务器。

**<a class="reference-link" name="%E6%8F%90%E4%BE%9B%E7%BB%9D%E5%AF%B9URL"></a>提供绝对URL**

正常情况下请求行采用的是相对地址，但是也是允许使用绝对地址的，就是将原本的Host值拼接到相对地址前面构成绝对地址，这时我们将Host头值替换为payload就可能会发生不可思议的事，例如

```
GET https://vulnerable-website.com/ HTTP/1.1
Host: bad-stuff-here
```

有时还可以修改一下URL的协议观察一下有没有什么差异，比如把HTTPS换成HTTP等。

**<a class="reference-link" name="%E6%B7%BB%E5%8A%A0%E6%8D%A2%E8%A1%8C"></a>添加换行**

有的时候我们还可以通过添加空格缩进来触发某种解析差异，它们会把空格缩进解析成换行从而忽略该Host头，例如

```
GET /example HTTP/1.1
 Host: bad-stuff-here
Host: vulnerable-website.com
```

虽然有的应用程序不会接受多个Host头的请求，但是因为会忽略掉一个而成功发出请求。该请求到达后端后还是会正常处理第一个Host头，这样就可以利用这种差异注入payload。

**<a class="reference-link" name="%E5%85%B6%E4%BB%96%E6%8A%80%E6%9C%AF"></a>其他技术**

还有一种比较高级的技术，就是HTTP请求走私，关于这个我们将在下一个专题专门讲解它

### <a class="reference-link" name="%E6%B3%A8%E5%85%A5%E5%8F%AF%E8%A6%86%E7%9B%96Host%E7%9A%84%E8%AF%B7%E6%B1%82%E5%A4%B4"></a>注入可覆盖Host的请求头

前面的专题中也有介绍过，有一些请求头的值是可以覆盖Host的值的，比如X-Forwarded-Host，当我们发出这样的请求时就会触发覆盖

```
GET /example HTTP/1.1
Host: vulnerable-website.com
X-Forwarded-Host: bad-stuff-here
```

可以达到相同目的的还有这些头
- X-Host
- X-Forwarded-Server
- X-HTTP-Host-Override
- Forwarded
我们可以通过前面介绍过的Param Miner插件的Guess headers功能发现这些奇奇怪怪的头



## HTTP Host头有哪些利用？

### <a class="reference-link" name="%E5%AF%86%E7%A0%81%E9%87%8D%E7%BD%AE%E6%8A%95%E6%AF%92"></a>密码重置投毒

**<a class="reference-link" name="%E5%AF%86%E7%A0%81%E9%87%8D%E7%BD%AE%E6%98%AF%E6%80%8E%E4%B9%88%E6%A0%B7%E7%9A%84%E8%BF%87%E7%A8%8B%EF%BC%9F"></a>密码重置是怎么样的过程？**

大部分的应用程序都提供了密码重置功能。比较常见的密码重置流程是这样的
- 用户输入他们的用户名或电子邮件地址并提交密码重置请求
- 如果用户名或电子邮件地址存在的话就会将其与一个Token绑定
- 然后用户接收到一个附有这个Token的重置密码链接
- 用户点击以后就可以修改与该Token绑定的用户的密码，修改完密码以后Token就会随之销毁。
理论上只有用户本人会接收到这个链接，但是通过密码重置投毒可以窃取到这个链接。

**<a class="reference-link" name="%E5%A6%82%E4%BD%95%E6%9E%84%E9%80%A0%E5%AF%86%E7%A0%81%E9%87%8D%E7%BD%AE%E6%8A%95%E6%AF%92%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何构造密码重置投毒攻击？**

如果应用程序根据Host头记录接收密码重置链接的地址，则可以通过密码重置投毒攻击获取到指定用户的密码重置链接，下面我们介绍一下构造过程。
- 我们修改提交密码重置请求中的Host为目标的域
- 这时候该用户会收到一封密码重置链接的邮件，但是这条链接会请求刚才Host设置的域，而不是真正用于密码重置的域
- 如果受害者点击该链接，攻击者就能获得与用户绑定的密码重置操作的Token
- 攻击者向真正密码重置的域发出请求并附上刚才获取到的Token即可成功重置受害者用户的密码了
为了增加受害者点击链接的可能性，我们可以利用一些暗示。如果这种攻击方式不成功还可以尝试使用悬挂标记攻击窃取Token。

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E5%9F%BA%E7%A1%80%E5%AF%86%E7%A0%81%E9%87%8D%E7%BD%AE%E6%8A%95%E6%AF%92"></a>配套靶场1：基础密码重置投毒**

首先我们找到密码重置点

[![](https://p3.ssl.qhimg.com/t01b101b1e40706d538.png)](https://p3.ssl.qhimg.com/t01b101b1e40706d538.png)

然后我们点到重置密码的页面

[![](https://p3.ssl.qhimg.com/t012d45825737e168ab.png)](https://p3.ssl.qhimg.com/t012d45825737e168ab.png)

我们输入要伪造的用户名carlos然后抓包

[![](https://p5.ssl.qhimg.com/t01f6222fd67b384254.png)](https://p5.ssl.qhimg.com/t01f6222fd67b384254.png)

然后我们进到Exploit Server查看我们要伪造的邮件服务器域名

[![](https://p4.ssl.qhimg.com/t01ac90fb21d4c72bc1.png)](https://p4.ssl.qhimg.com/t01ac90fb21d4c72bc1.png)

然后把Host字段改成这个，然后放包，再进到Exploit Server的Access Log里面看获取到的重置密码Token

[![](https://p3.ssl.qhimg.com/t0147f4f15e2847b8c5.png)](https://p3.ssl.qhimg.com/t0147f4f15e2847b8c5.png)

然后把这个Token构造进重置密码链接里面进行密码重置

[![](https://p1.ssl.qhimg.com/t0148f4183e5cdc9b6a.png)](https://p1.ssl.qhimg.com/t0148f4183e5cdc9b6a.png)

重置密码成功后成功登录carlos的账户

[![](https://p4.ssl.qhimg.com/t01c5292d45fa8801bc.png)](https://p4.ssl.qhimg.com/t01c5292d45fa8801bc.png)

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E9%80%9A%E8%BF%87%E6%82%AC%E6%8C%82%E6%A0%87%E8%AE%B0%E7%9A%84%E5%AF%86%E7%A0%81%E9%87%8D%E7%BD%AE%E6%8A%95%E6%AF%92"></a>配套靶场2：通过悬挂标记的密码重置投毒**

这一关我们发现Host没有对端口号进行鉴别，导致我们可以把任意字符串拼接到端口号后面，这样应该算是一种HTTP走私攻击了，术语里面叫HTTP头部污染，因为这一关是系统那边给我们分配密码，所以只能通过这种方法把分配的密码带出来，于是我们这么伪造Host

[![](https://p4.ssl.qhimg.com/t01c4eaaf15783a16bc.png)](https://p4.ssl.qhimg.com/t01c4eaaf15783a16bc.png)

[![](https://p5.ssl.qhimg.com/t01e7856681215a65bb.png)](https://p5.ssl.qhimg.com/t01e7856681215a65bb.png)<br>
成功登录carlos用户

[![](https://p0.ssl.qhimg.com/t018db3114eb469c00c.png)](https://p0.ssl.qhimg.com/t018db3114eb469c00c.png)

### <a class="reference-link" name="%E9%80%9A%E8%BF%87Host%E5%A4%B4%E7%9A%84Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92"></a>通过Host头的Web缓存投毒

在上一个专题Web缓存投毒中我们其实也讲了这种攻击手段，当时是利用Web缓存投毒发动XSS攻击。这种攻击手段可以让本来无法通过Host让目标用户遭受攻击的情况重新可以让目标用户接收到恶意响应缓存。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E9%80%9A%E8%BF%87%E6%A8%A1%E6%A3%B1%E4%B8%A4%E5%8F%AF%E7%9A%84%E8%AF%B7%E6%B1%82%E7%9A%84Web%E7%BC%93%E5%AD%98%E6%8A%95%E6%AF%92"></a>配套靶场：通过模棱两可的请求的Web缓存投毒

这里我们可以再加一个Host字段覆盖掉原来的Host字段

[![](https://p1.ssl.qhimg.com/t012f0dcca63ee5b62d.png)](https://p1.ssl.qhimg.com/t012f0dcca63ee5b62d.png)

然后我们到Exploit Server伪造一个我们的/resources/js/tracking.js

[![](https://p0.ssl.qhimg.com/t016f8919bb6a0d2526.png)](https://p0.ssl.qhimg.com/t016f8919bb6a0d2526.png)

然后产生Web缓存，访问主页的人就会接收到投毒缓存了

[![](https://p1.ssl.qhimg.com/t01dcbbc678fb1286c6.png)](https://p1.ssl.qhimg.com/t01dcbbc678fb1286c6.png)

### <a class="reference-link" name="%E8%A7%A6%E5%8F%91%E7%BB%8F%E5%85%B8%E7%9A%84%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%AB%AF%E6%BC%8F%E6%B4%9E"></a>触发经典的服务器端漏洞

经典的服务器端漏洞大部分都是由于含有payload的请求头导致的，当然，Host头也是，有时候可以通过向Host注入payload触发如Sql注入之类的漏洞。

### <a class="reference-link" name="%E8%AE%BF%E9%97%AE%E5%8F%97%E9%99%90%E7%9A%84%E5%8A%9F%E8%83%BD"></a>访问受限的功能

有的功能点被限制为只允许内部用户访问，但是有时候通过简单修改Host头就可以绕过这种限制。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9AHost%E5%A4%B4%E9%AA%8C%E8%AF%81%E7%BB%95%E8%BF%87"></a>配套靶场：Host头验证绕过

打开robots.txt找到了管理页面

[![](https://p5.ssl.qhimg.com/t013d56eb38ea6ab886.png)](https://p5.ssl.qhimg.com/t013d56eb38ea6ab886.png)

然后进到管理页面发现以下提示

[![](https://p5.ssl.qhimg.com/t01f1d3805b2f4dfaf5.png)](https://p5.ssl.qhimg.com/t01f1d3805b2f4dfaf5.png)

这里提示我们只有本地用户才能访问，那么我们就在Host字段中伪造我们是本地用户

[![](https://p3.ssl.qhimg.com/t019f17c3ab5dabbb29.png)](https://p3.ssl.qhimg.com/t019f17c3ab5dabbb29.png)

然后我们成功访问到管理页面，然后成功删除Carlos用户

[![](https://p3.ssl.qhimg.com/t01211ac444846deebf.png)](https://p3.ssl.qhimg.com/t01211ac444846deebf.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E7%88%86%E7%A0%B4%E8%99%9A%E6%8B%9F%E4%B8%BB%E6%9C%BA%E8%AE%BF%E9%97%AE%E5%86%85%E9%83%A8%E7%BD%91%E7%AB%99"></a>利用爆破虚拟主机访问内部网站

有的网站运营者会把对外和对内的网站部署在同一台服务器上，但是内部网站往往无法通过DNS查询到内部IP，但是可以通过如信息泄漏、暴力破解的方式知道其内部IP。

### <a class="reference-link" name="%E5%9F%BA%E4%BA%8E%E8%B7%AF%E7%94%B1%E7%9A%84SSRF"></a>基于路由的SSRF

基于路由的SSRF是利用负载均衡或者反向代理的特性发动的攻击。因为负载均衡和反向代理的作用都是中转流量，会根据Host去路由，但是如果没有进行严格的限制，可能会仅仅通过修改Host就让它们将请求包转发到其他域。并且它们既可以接收来自外部网络的请求，还能请求大部分的内部网络，所以经常它们会被当成攻击目标。我们可以通过先将请求转发到burp collaborator来探测是否存在该漏洞。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E5%9F%BA%E4%BA%8E%E8%B7%AF%E7%94%B1%E7%9A%84SSRF"></a>配套靶场1：基于路由的SSRF

基于路由的SSRF典型利用点是修改Host，首先我们先测试一下能不能向外发请求，打开我们的burp collaborator client，把Host替换为生成的地址，然后发包

[![](https://p5.ssl.qhimg.com/t01997c62f99b9a30f9.png)](https://p5.ssl.qhimg.com/t01997c62f99b9a30f9.png)

然后我们在burp collaborator client点poll now等着接收

[![](https://p5.ssl.qhimg.com/t0196eca58f3e499fc5.png)](https://p5.ssl.qhimg.com/t0196eca58f3e499fc5.png)

成功接收，说明服务器是可以向任意地址发出请求的，然后我们爆破一下admin在哪台主机下，把Host改成192.168.0.0然后发到Intruder里面将最后一个0设置为变量，Payload type改成numbers，设置从0到255，递进1

[![](https://p0.ssl.qhimg.com/t01234d34ac2495f677.png)](https://p0.ssl.qhimg.com/t01234d34ac2495f677.png)

[![](https://p4.ssl.qhimg.com/t01702dbe427f2239ca.png)](https://p4.ssl.qhimg.com/t01702dbe427f2239ca.png)

然后Start Attack，然后按状态码排序得到admin在192.168.0.3

[![](https://p2.ssl.qhimg.com/t01e5bb23f741c8d5d7.png)](https://p2.ssl.qhimg.com/t01e5bb23f741c8d5d7.png)

然后把包传到Repeater里，跳转以后把Host手动改成192.168.0.3(不然会返回404)

[![](https://p1.ssl.qhimg.com/t016c809c79310480c9.png)](https://p1.ssl.qhimg.com/t016c809c79310480c9.png)

然后我们找到了提交删除用户表单的地方，需要构造两个参数

[![](https://p4.ssl.qhimg.com/t01e1ae2fb92bcedf3b.png)](https://p4.ssl.qhimg.com/t01e1ae2fb92bcedf3b.png)

然后在request栏右键change request method以后将两个参数csrf和username及它们的值写在body里，发包

[![](https://p2.ssl.qhimg.com/t01feb4e7334100261c.png)](https://p2.ssl.qhimg.com/t01feb4e7334100261c.png)

成功删除用户

[![](https://p3.ssl.qhimg.com/t016402311a286beb99.png)](https://p3.ssl.qhimg.com/t016402311a286beb99.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E5%88%A9%E7%94%A8%E8%AF%B7%E6%B1%82%E8%A7%A3%E6%9E%90%E7%BC%BA%E9%99%B7%E7%9A%84SSRF"></a>配套靶场2：利用请求解析缺陷的SSRF

首先我们试一下修改Host为burp collaborator的地址看看服务端允不允许访问

[![](https://p5.ssl.qhimg.com/t01abd55a4a94c9326f.png)](https://p5.ssl.qhimg.com/t01abd55a4a94c9326f.png)

发现修改Host会被禁止，那我们试试把URL换成靶机的绝对地址试试

[![](https://p1.ssl.qhimg.com/t01321fcd16c8719e0b.png)](https://p1.ssl.qhimg.com/t01321fcd16c8719e0b.png)

[![](https://p0.ssl.qhimg.com/t0188372469d92624b2.png)](https://p0.ssl.qhimg.com/t0188372469d92624b2.png)

从图中发现URL换成绝对地址就可以让服务端向外根据Host发出请求，然后把Host改成192.168.0.0，然后发到Intruder里面爆破一下，还是numbers类型

[![](https://p2.ssl.qhimg.com/t010c8161b05c6a87f1.png)](https://p2.ssl.qhimg.com/t010c8161b05c6a87f1.png)

爆破出来192.168.0.26是后台地址，发到repeater里追踪一下重定向

[![](https://p3.ssl.qhimg.com/t01017a24a34ec82b9d.png)](https://p3.ssl.qhimg.com/t01017a24a34ec82b9d.png)

跳转到管理后台的时候别忘了URL用绝对地址，Host改成192.168.0.26，然后根据页面信息构造删除请求

[![](https://p0.ssl.qhimg.com/t014abfd6e4a55c8d0f.png)](https://p0.ssl.qhimg.com/t014abfd6e4a55c8d0f.png)

最好是先把参数写在URL里然后再右键转换请求方法，这样会自动计算Content-Length，成功删除角色

[![](https://p2.ssl.qhimg.com/t01e7dae7962eb15866.png)](https://p2.ssl.qhimg.com/t01e7dae7962eb15866.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E9%94%99%E8%AF%AF%E6%A0%BC%E5%BC%8F%E7%9A%84%E8%AF%B7%E6%B1%82%E8%A1%8C%E7%9A%84SSRF"></a>利用错误格式的请求行的SSRF

反向代理会将请求行的路径与后端主机名拼接进行路由。但是如果我们提交一个错误格式的请求行呢，例如

```
GET @private-intranet/example HTTP/1.1
```

这次拼接后可能会变成如&lt;a href=”http://backend-server@private-intranet/example””&gt;http://backend-server@private-intranet/example 的形式，就可能会被某些HTTP库解释为使用用户名backend-server访问内部网站。



## 如何缓解HTTP Host头攻击？
- 限制使用绝对地址
- 验证Host头
- 限制覆盖Host头
- 设置白名单域
- 留意仅限内部访问的虚拟主机


## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之高级漏洞篇 – HTTP Host头攻击专题的全部内容啦，本专题主要讲了HTTP Host头攻击的原理、识别方法、利用及防护等，感兴趣的同学可以在评论区进行讨论，嘻嘻嘻。
