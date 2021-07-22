> 原文链接: https://www.anquanke.com//post/id/85264 


# 【技术分享】诡异的DNS，流量都去哪儿了？


                                阅读量   
                                **78593**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.sucuri.net
                                <br>原文地址：[https://blog.sucuri.net/2016/07/fake-freedns-used-to-redirect-traffic-to-malicious-sites.html](https://blog.sucuri.net/2016/07/fake-freedns-used-to-redirect-traffic-to-malicious-sites.html)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p2.ssl.qhimg.com/t01466eb7f6b11acad5.png)](https://p2.ssl.qhimg.com/t01466eb7f6b11acad5.png)

 

翻译：[wushen2017](http://bobao.360.cn/member/contribute?uid=2812174527)

预估稿费：150RMB（不服你也来投稿啊！）

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**前言**

近来几天，我们收到了一些类似的协助清理请求，用户的网站时不时被重定向到广告、垃圾邮件、恶意下载相关的网站。<br>

我们的安全分析师, Andrey Kucherov, 同研究团队一起做了初步跟踪。发现所涉及的原始网站，都是因为解析到IP地址213.184.126.163 而发生了重定向。重定向发生后，受害者实际访问到的是原网站的仿冒版——如www.example.com被重定向到ww2.example.com。

跟踪过程中，我们并没有发现这些原始网站存在什么问题，所以开始朝着DNS方向检查。

在全世界范围内检查这些原始网站的域名解析情况时，我们注意到有些探测服务器确实解析到了原始网站的正确IP，而还有一些则解析到了218.184.126.163：

[![](https://p3.ssl.qhimg.com/t0194bef866c801664f.png)](https://p3.ssl.qhimg.com/t0194bef866c801664f.png)

再来看这些原始网站的域名服务器，发现它们都用了NameCheap的FreeDNS服务。然而，不同的探测服务器针对同一个域名所查看到的域名服务器还不一样：

[![](https://p2.ssl.qhimg.com/t01393144b9f2e8e3fc.png)](https://p2.ssl.qhimg.com/t01393144b9f2e8e3fc.png)

如图所示，有些是看起来很常规的域名服务器，如freedns1.registrar-servers.com ～ freedns5.registrar-servers.com。而其他则是看起来比较诡异的.biz域名——起始部分跟常规域名服务器部分相同，而中间部分则是随机填充值了。

[![](https://p2.ssl.qhimg.com/t01f546c0638a026086.png)](https://p2.ssl.qhimg.com/t01f546c0638a026086.png)

我们觉得这很可疑，决定继续跟踪，想确认这些域名是否真的属于NameCheap。从whois信息来看，它们确实是本周刚被NameCheap所注册的：

[![](https://p2.ssl.qhimg.com/t016bf1bc416e95c4cb.png)](https://p2.ssl.qhimg.com/t016bf1bc416e95c4cb.png)

[![](https://p3.ssl.qhimg.com/t017a23ad1cfbf8714e.png)](https://p3.ssl.qhimg.com/t017a23ad1cfbf8714e.png)

而且它们也指向跟常规registrar-servers.com一样的IP。其中，有个例外——freedns1.registrar-serversv67eds0q.biz。



**freedns1.registrar-serversv67eds0q.biz**

它是两天前刚被上海的一个人注册的：<br>

[![](https://p1.ssl.qhimg.com/t011325e48c950294bd.png)](https://p1.ssl.qhimg.com/t011325e48c950294bd.png)

而它解析到的，正是跟重定向相关的IP：213.184.126.163。

我们无法知晓NameCheap注册这些怪异的.biz域名作为域名服务器的原因，同时凑巧地几天后又有人注册了一个很类似的域名。其意图也很明显，准备更改那些使用FreeDNS的原始网站的DNS设置。

这事还没完。以下是一些曾经指向213.184.126.163的域名：

[![](https://p3.ssl.qhimg.com/t016ff876023d6052f5.png)](https://p3.ssl.qhimg.com/t016ff876023d6052f5.png)

从名字来看，它们正是被注册用作域名服务器的，与前面的情况类似。

到目前为止，我们并不清楚这究竟是怎么发生的。是有人入侵了域名注册商的账户，更改了域名解析服务器，还是NameCheap的FreeDNS服务被入侵，替换了其中一个域名服务器。（译者注：这个诡异的freedns1.registrar-serversv67eds0q.biz 到底是否为namecheap所属？如果是其所属，则可能是被入侵进行了修改，将其指向恶意的213.184.126.163；如果不是namecheap所属，则可能是原始网站的域名解析服务器由原来的NameCheap提供的FreeDSN，被更改成了现在只是跟FreeDNS长得很像的freedns1.registrar-serversv67eds0q.biz。）

现在，已经观察到213.184.126.163已失活,域名服务器也恢复正常。 然而,因为dns解析缓存的存在,有些地区仍然可观察到受影响网站会被重定向到恶意网站.



**DomainersChoice**

在检查解析到213.184.126.163的域名时，我们注意到大部分域名是跟中国的DomainersChoice.com有关联的：要么是被它注册的，要么是使用了它的域名解析服务器（888DNS.NET）（前面提到的freedns1.registrar-serversv67eds0q[.]biz 也是有使用该解析服务器）<br>



**Conficker Sinkholed Domains**

关于IP 218.184.126.163，还有一点比较有意思。查看下该IP在[VirusTotal](https://www.virustotal.com/en/ip-address/213.184.126.163/information/)上的记录情况，你会看到诸如acawarkfegq[.]info, ahpamj[.]org, amfcsbetu[.]info 这样的域名也曾指向它。而这些域名都是被微软或者Afilias注册，用以应对飞客蠕虫的。<br>

Conficker曾在2008～2009感染了全世界范围内数百万的电脑。为制止其感染，包括微软及顶级域名提供商、ISP在内Conficker 应对联盟，对Conficker涉及的千万个域名进行了阻拦。

不清楚为何这些已经被sinkholed的域名指向了213.184.126.163。

**<br>**

**验证你的DNS设置和域名账户安全**

如果你使用了NameCheap提供的FreeDNS服务，或者在它们那注册了域名，强烈建议您：<br>

1. 到域名注册商那里检查你的域名服务器

2. 在你的DNS服务提供商那里检查你的DNS设置（通常这两个是一样的，但并不全是如此）

3. 更改你的域名注册商、DNS提供商那的账号、密码。

即便你没有用到这里提及的服务，也最好还是检查下域名的DNS设置，更换下密码。我们也曾见到其他更改网站DNS设置的案例：例如，他们会在合法下创建子域名，将其指向恶意服务器。

这也正是我们为客户提供DNS和WHOIS监控服务的原因。如果有人更改了配置（如域名所有者、联系信息或者域名服务器发生了变更），我们就会自动地将这些信息推送给客户，以便让他们进行确认，尽快采取措施，避免不必要的损失。

如果有以下情况，都请及时联系我们：你的域名受此类DNS攻击影响，或者你知道这里涉及的域名解析服务器是如何被更改的，以及NameCheap 为何使用如此诡异的域名作为解析服务器。


