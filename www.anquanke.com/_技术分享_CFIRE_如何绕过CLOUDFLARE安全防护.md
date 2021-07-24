> 原文链接: https://www.anquanke.com//post/id/86843 


# 【技术分享】CFIRE：如何绕过CLOUDFLARE安全防护


                                阅读量   
                                **216217**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：rhinosecuritylabs.com
                                <br>原文地址：[https://rhinosecuritylabs.com/cloud-security/cloudflare-bypassing-cloud-security/](https://rhinosecuritylabs.com/cloud-security/cloudflare-bypassing-cloud-security/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p5.ssl.qhimg.com/t0113773c11c5db3edd.png)](https://p5.ssl.qhimg.com/t0113773c11c5db3edd.png)

译者：[**testvul_001**](http://bobao.360.cn/member/contribute?uid=780092473)

预估稿费：170RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

CloudFlare是一家提供DNS服务（包括WAF、DDOS防护）的云安全供应商。如果配置得当的话，安全服务将很好地隐藏网站的真实IP并发挥CloudFlare的安全过滤能力。在得不到服务器真实IP的情况下，攻击者很难直接对目标发起直接攻击。

[![](https://p0.ssl.qhimg.com/t01b2206a2c2db75a58.png)](https://p0.ssl.qhimg.com/t01b2206a2c2db75a58.png)

然而当架构和DNS记录持续增长时，配置就会随之改变，这将是一个大问题。**在本文中，我们将提供几个策略来破坏CloudFlare的安全服务并发现云服务器的真实IP。同时我们也会介绍一个工具-CFire-来帮助安全工程师发现它们自己云架构中的误配置。**

<br>

**CFIRE简介**

CFire将使用多个技术来发现CloudFlare后面的真实IP，并且可以管理相关的数据。尽管这个工具刚刚诞生，我们觉得它在我们自己的渗透测试中还是非常有用的，所以我们将把它介绍给社区，希望它能帮助更多人，并且将来可以发现更多云供应商的误配置（如AWS Cloudfront）。

[![](https://p1.ssl.qhimg.com/t011363ba59aba19d44.png)](https://p1.ssl.qhimg.com/t011363ba59aba19d44.png)

从Rhino Security Labs的github下载好CFire脚本后，我们需要执行一些安装步骤，首先是安装或者更新CrimeFlare数据库。

[![](https://p2.ssl.qhimg.com/t0180101d5e68066e29.png)](https://p2.ssl.qhimg.com/t0180101d5e68066e29.png)

CFire的默认查询方法是查询本地的CrimeFlare sqlite3数据库。

[![](https://p3.ssl.qhimg.com/t010736896bd099cd00.jpg)](https://p3.ssl.qhimg.com/t010736896bd099cd00.jpg)

使用Sublist3r模块作为搜索枚举功能。

[![](https://p2.ssl.qhimg.com/t01238e0b837a8f053e.jpg)](https://p2.ssl.qhimg.com/t01238e0b837a8f053e.jpg)

<br>

**发现真实IP**

现在有很多种大家已经知道的方法来发现CloudFlare后面的真实IP，这些方法有一个共同特征就是：都是利用误配置来发现IP的泄露。

CloudFlare首先提供DNS服务，缓存资源提高网站的访问速度，同时提供安全服务。一旦服务启用，CloudFlare就会拦截恶意的流量。很多公司仅仅使用CloudFlare作为防DDOS的工具，在这种简单情形下是有效的，但是随着公司扩展和实现新的服务或技术，他们无意中打开了IP发现的大门。

**1、普通DNS记录误配置**

寻找真实IP的一个最常用技术是寻找子域名，或者用于后台服务的域名。在一段时间内，CloudFlare会自动配置会泄露web服务器IP的子域名。很多用户都不知道这些DNS记录的存在，这个寻找真实IP的方法存在了几年。目前CloudFlare已经修改了这个问题，所以这个方法只能用在一些老的设置中。

**2、MX记录**

所有的环境各有不同，有的客户喜欢自己搭建邮件服务。根据RFC5321，MX记录是用于优先指定一个域名的邮件服务器的。

如果目标没有使用第三方的邮件服务，那么它的邮件服务器很可能和web服务器在同一个网络内。在这种情况下，发现真实IP就和执行DNS查询一样简单。

[![](https://p5.ssl.qhimg.com/t01e25cfb4aa71c9ddd.png)](https://p5.ssl.qhimg.com/t01e25cfb4aa71c9ddd.png)

**3、FTP/SCP**

和MX记录类似，有很多组织需要将外部资源传输到内部服务器中。事实上，正确的方法是使用VPN来允许远程办公的员工安全的传输文件到内部网络上。不幸的是，很多老的架构里，会使用FTP/SCP服务传输文件，这样就大大增加了攻击者发现真实IP的几率。

**4、WEBSOCK**

尽管最近CloudFlare已经开始提供WebSockets (WS)支持技术，但是很多客户还不知道这个技术或者来不及迁移他们的WS服务。WS可用于发现真实IP是因为WS在开始HTTP(S)握手后需要在客户端和服务端之间保持持续的链接。

2014年以前CloudFlare不提供WS技术支持，因为CloudFlare似乎使用的是NGINX WEB服务器，而NGINX在2013年底才支持WS代理。当浏览一个网站的时候，我发现尽管该站点的主站已经使用CloudFlare防护，但是它的WS服务器完全暴露了了它的真实IP。

[![](https://p5.ssl.qhimg.com/t0124eb3eefb5c50044.jpg)](https://p5.ssl.qhimg.com/t0124eb3eefb5c50044.jpg)

结果表明WS服务器所使用的IP同时也是主站使用的IP。

[![](https://p0.ssl.qhimg.com/t010755424125360d0c.png)](https://p0.ssl.qhimg.com/t010755424125360d0c.png)

**5、旧的DNS记录**

CrimeFlare项目应该是最好的研究数据库之一。尽管项目的主旨是发现服务背后的犯罪行为，但是攻击者也能用它来发现潜在的泄露IP。CrimeFlare没有详细描述它是如何收集数据的，但是我们可以放心开发者每周都会查询大量的域名、相关的域名服务器、IP地址以及SSL证书信息，最后把信息分组存进数据库。

目前CrimeFlare已经将成立来的数据开放，研究者们有机会使用这些数据对CloudFlare的用户趋势进行分析。在开发CFire项目的过程中，我们创建了一个SQLite3数据库和一个查询工具，如下例子：

[![](https://p3.ssl.qhimg.com/t01a87955df62163b66.jpg)](https://p3.ssl.qhimg.com/t01a87955df62163b66.jpg)

**6、SSRF漏洞**

Server-Side Request Forgery (SSRF) 漏洞允许攻击者代理访问任意资源（通常是内部服务）。目前已经有很多关于SSRF的研究了，SSRF不仅可以用于探测应用所处的生产环境，同时也可以用于发现CloudFlare隐藏的真实IP。

我们测试案例使用的是安装了有漏洞的Nelio AB Testing 4.5.8插件的Wordpress。主要是为了模拟SSRF漏洞环境。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f2faf1c858f48957.jpg)

例子中的漏洞不需要身份验证，可以直接通过curl触发。这个漏洞存在于WP插件的/ajax/iesupport.php页面中。

[![](https://p0.ssl.qhimg.com/t016c60845b7769eb4c.png)](https://p0.ssl.qhimg.com/t016c60845b7769eb4c.png)

这个漏洞的问题是没有有效的验证攻击者是否在试着访问敏感资源。由于缺少认证检查，这里存在SSRF漏洞，我们可以用它访问任何站点。即使这里禁止访问内部资源了，我们也可以用它访问我们自己搭建的服务器，这样我们就能获得隐藏在CloudFlare后面的WEB服务器的真实IP 了。

[![](https://p1.ssl.qhimg.com/t01ffc5fd8266f536a4.jpg)](https://p1.ssl.qhimg.com/t01ffc5fd8266f536a4.jpg)



**总结**

同样的，在Amazon Web Services S3 Buckets中，一个小的配置改变也会对安全方面造成大的影响。

1、CloudFlare是很有用的云安全工具，可以保护你的IP和你的资产。

2、CloudFlare在正确的配置下才会发挥作用。

3、如果你从CloudFlare迁移到“direct IP” DNS服务商，IP仍然会暴露。

4、子域名绕过CloudFlare通常会暴露所有的DNS记录。

CFire将会加快安全研究中寻找真实IP过程中的最繁琐的步骤。我们开发这个工具的目的是告诉人们CloudFlare做的不错，但是我们需要做一些正确的配置来保护自己的资产。
