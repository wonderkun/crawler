> 原文链接: https://www.anquanke.com//post/id/163348 


# 网站真实IP发现手段浅谈


                                阅读量   
                                **423661**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">17</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01e73d883355b5350e.jpg)](https://p1.ssl.qhimg.com/t01e73d883355b5350e.jpg)

2018年，网络安全事件频发，我司ISEC实验室通过对各安全事件的研究分析，发现很多攻击手段都是通过脆弱的旁站和C段实现的，DDoS亦是如此，它可以导致服务器被占用资源甚至当机。这些攻击得以实施都是由于用户web服务器的真实ip暴露出去了。

**本期“安仔课堂”，ISEC实验室陈老师将为大家揭秘黑客查找真实ip的多种方法。**



## 一、什么是CDN

首先，我们来认识下最寻常的真实ip隐藏的方法“CDN”。

**内容分发网络**(content delivery network或content distribution network，缩写作CDN)指一种通过互联网互相连接的电脑网络系统，利用最靠近每位用户的服务器，更快、更可靠地将音乐、图片、视频、应用程序及其他文件发送给用户，来提供高性能、可扩展性及低成本的网络内容传递给用户。

CDN节点会在多个地点，不同的网络上摆放。这些节点之间会动态的互相传输内容，对用户的下载行为最优化，并借此减少内容供应者所需要的带宽成本，改善用户的下载速度，提高系统的稳定性。国内常见的CDN有ChinanNet Center（网宿科技）、ChinaCache（阿里云）等，国外常见的有Akamai(阿卡迈)、Limelight Networks（简称LLNW）等；如下图，国内外主流的CDN市场格局：<br>[![](https://p4.ssl.qhimg.com/t01531b7e602dd8f4ed.png)](https://p4.ssl.qhimg.com/t01531b7e602dd8f4ed.png)<br>
图1

如图：用户先经由CDN节点，然后再访问web服务器。<br>[![](https://p0.ssl.qhimg.com/t017146975cc9cc526e.png)](https://p0.ssl.qhimg.com/t017146975cc9cc526e.png)<br>
图2



## 二、如何判断ip是否是网站真实ip

### <a class="reference-link" name="1.Nslookup%E6%B3%95"></a>1.Nslookup法

黑客一般nslookup想要查的域名，若是有多个ip就是用了cdn，多半为假ip；如图：<br>[![](https://p5.ssl.qhimg.com/t01974aa79ee7abb5db.png)](https://p5.ssl.qhimg.com/t01974aa79ee7abb5db.png)<br>
图3

### <a class="reference-link" name="2.%E5%A4%9A%E5%9C%B0ping%E5%9F%9F%E5%90%8D%E6%B3%95"></a>2.多地ping域名法

黑客也可以从多个地点ping他们想要确认的域名，若返回的是不同的ip，那么服务器确定使用了cdn，返回的ip也不是服务器的真实ip；<br>
常用的网址有just ping:[http://itools.com/tool/just-ping等等。](http://itools.com/tool/just-ping%E7%AD%89%E7%AD%89%E3%80%82)<br>[![](https://p3.ssl.qhimg.com/t01f8ec1a8e6a11a821.png)](https://p3.ssl.qhimg.com/t01f8ec1a8e6a11a821.png)<br>
图4

### <a class="reference-link" name="3.%E2%80%9C%E5%B8%B8%E8%AF%86%E2%80%9D%E5%88%A4%E6%96%AD%E6%B3%95"></a>3.“常识”判断法

为什么叫“常识”判断法呢?<br>
①在反查网站ip时，如果此网站有1000多个不同域名，那么这个ip多半不是真实ip。常用的ip反查工具有站长工具([http://s.tool.chinaz.com/same)、微步在线(https://x.threatbook.cn/)等等。微步在线支持同服域名查询、子域名查询、服务查询、whois反查等，要注意的是，查询部分信息有次数限制，需先注册账号。](http://s.tool.chinaz.com/same)%E3%80%81%E5%BE%AE%E6%AD%A5%E5%9C%A8%E7%BA%BF(https://x.threatbook.cn/)%E7%AD%89%E7%AD%89%E3%80%82%E5%BE%AE%E6%AD%A5%E5%9C%A8%E7%BA%BF%E6%94%AF%E6%8C%81%E5%90%8C%E6%9C%8D%E5%9F%9F%E5%90%8D%E6%9F%A5%E8%AF%A2%E3%80%81%E5%AD%90%E5%9F%9F%E5%90%8D%E6%9F%A5%E8%AF%A2%E3%80%81%E6%9C%8D%E5%8A%A1%E6%9F%A5%E8%AF%A2%E3%80%81whois%E5%8F%8D%E6%9F%A5%E7%AD%89%EF%BC%8C%E8%A6%81%E6%B3%A8%E6%84%8F%E7%9A%84%E6%98%AF%EF%BC%8C%E6%9F%A5%E8%AF%A2%E9%83%A8%E5%88%86%E4%BF%A1%E6%81%AF%E6%9C%89%E6%AC%A1%E6%95%B0%E9%99%90%E5%88%B6%EF%BC%8C%E9%9C%80%E5%85%88%E6%B3%A8%E5%86%8C%E8%B4%A6%E5%8F%B7%E3%80%82)

②如果一个asp或者asp.net网站返回的头字段的server不是IIS、而是Nginx，那么多半是用了nginx反向代理，而不是真实ip。

③如果ip定位是在常见cdn服务商的服务器上，那么是真实ip的可能性就微乎其微了。



## 三、如何寻找真实ip

### <a class="reference-link" name="1.%E5%AD%90%E5%9F%9F%E5%90%8D%E6%9F%A5%E6%89%BE%E6%B3%95"></a>1.子域名查找法

因为cdn和反向代理是需要成本的，有的网站只在比较常用的域名使用cdn或反向代理，有的时候一些测试子域名和新的子域名都没来得及加入cdn和反向代理，所以有时候是通过查找子域名来查找网站的真实IP。下面介绍些常用的子域名查找的方法和工具：

**[https://x.threatbook.cn/](https://x.threatbook.cn/))**

上文提到的微步在线功能强大，黑客只需输入要查找的域名(如baidu.com)，点击子域名选项就可以查找它的子域名了，但是免费用户每月只有5次免费查询机会。如图：<br>[![](https://p2.ssl.qhimg.com/t01f4229c0efa4e4445.png)](https://p2.ssl.qhimg.com/t01f4229c0efa4e4445.png)<br>
图5

[https://dnsdb.io/zh-cn/](https://dnsdb.io/zh-cn/))</strong>

黑客只需输入baidu.com type:A就能收集百度的子域名和ip了。如图：<br>[![](https://p2.ssl.qhimg.com/t019afbd415edc157ad.png)](https://p2.ssl.qhimg.com/t019afbd415edc157ad.png)<br>
图6

<a class="reference-link" name="%E2%91%A2Google%20%E6%90%9C%E7%B4%A2"></a>**③Google 搜索**

Google site:baidu.com -www就能查看除www外的子域名，如图：<br>[![](https://p2.ssl.qhimg.com/t01a3f3339fe0a1b596.png)](https://p2.ssl.qhimg.com/t01a3f3339fe0a1b596.png)<br>
图7

<a class="reference-link" name="%E2%91%A3%E5%90%84%E7%A7%8D%E5%AD%90%E5%9F%9F%E5%90%8D%E6%89%AB%E6%8F%8F%E5%99%A8"></a>**④各种子域名扫描器**

这里，主要为大家推荐子域名挖掘机和lijiejie的subdomainbrute([https://github.com/lijiejie/subDomainsBrute](https://github.com/lijiejie/subDomainsBrute))<br>
子域名挖掘机仅需输入域名即可基于字典挖掘它的子域名，如图：<br>[![](https://p5.ssl.qhimg.com/t015d80f472f3825a46.png)](https://p5.ssl.qhimg.com/t015d80f472f3825a46.png)<br>
图8

Subdomainbrute以windows为例，黑客仅需打开cmd进入它所在的目录输入Python subdomainbrute.py baidu.com —full即可收集百度的子域名，如图：<br>[![](https://p3.ssl.qhimg.com/t01fbfedc48d0c4a5ac.png)](https://p3.ssl.qhimg.com/t01fbfedc48d0c4a5ac.png)<br>
图9

总结：收集子域名后尝试以解析ip不在CDN上的ip解析主站，真实ip成功被获取到。

### <a class="reference-link" name="2.ip%E5%8E%86%E5%8F%B2%E8%AE%B0%E5%BD%95%E8%A7%A3%E6%9E%90%E6%9F%A5%E8%AF%A2%E6%B3%95"></a>2.ip历史记录解析查询法

有的网站是后来才加入CDN的，所以只需查询它的解析历史即可获取真实ip，这里我们就简单介绍几个网站：微步在线，dnsdb.ionetcraft([http://toolbar.netcraft.com/),Viewdns(http://viewdns.info/)等等。](http://toolbar.netcraft.com/),Viewdns(http://viewdns.info/)%E7%AD%89%E7%AD%89%E3%80%82)

### <a class="reference-link" name="3.%E7%BD%91%E7%AB%99%E6%BC%8F%E6%B4%9E%E6%9F%A5%E6%89%BE%E6%B3%95"></a>3.网站漏洞查找法

通过网站的信息泄露如phpinfo泄露，github信息泄露，命令执行等漏洞获取真实ip。

### <a class="reference-link" name="4.%E7%BD%91%E7%AB%99%E8%AE%A2%E9%98%85%E9%82%AE%E4%BB%B6%E6%B3%95"></a>4.网站订阅邮件法

黑客可以通过网站订阅邮件的功能，让网站给自己发邮件，查看邮件的源代码即可获取网站真实ip。

### <a class="reference-link" name="5.%E7%90%86%E6%83%B3zmap%E6%B3%95"></a>5.理想zmap法

首先从 apnic 网络信息中心获取ip段，然后使用Zmap的 banner-grab 对扫描出来 80 端口开放的主机进行banner抓取，最后在 http-req中的Host写我们需要寻找的域名，然后确认是否有相应的服务器响应。

### <a class="reference-link" name="6.%E7%BD%91%E7%BB%9C%E7%A9%BA%E9%97%B4%E5%BC%95%E6%93%8E%E6%90%9C%E7%B4%A2%E6%B3%95"></a>6.网络空间引擎搜索法

常见的有以前的钟馗之眼，shodan([https://www.shodan.io/)，fofa搜索(https://fofa.so/)。以fofa为例，只需输入：title:“网站的title关键字”或者body：“网站的body特征”就可以找出fofa收录的有这些关键字的ip域名，很多时候能获取网站的真实ip。](https://www.shodan.io/)%EF%BC%8Cfofa%E6%90%9C%E7%B4%A2(https://fofa.so/)%E3%80%82%E4%BB%A5fofa%E4%B8%BA%E4%BE%8B%EF%BC%8C%E5%8F%AA%E9%9C%80%E8%BE%93%E5%85%A5%EF%BC%9Atitle:%E2%80%9C%E7%BD%91%E7%AB%99%E7%9A%84title%E5%85%B3%E9%94%AE%E5%AD%97%E2%80%9D%E6%88%96%E8%80%85body%EF%BC%9A%E2%80%9C%E7%BD%91%E7%AB%99%E7%9A%84body%E7%89%B9%E5%BE%81%E2%80%9D%E5%B0%B1%E5%8F%AF%E4%BB%A5%E6%89%BE%E5%87%BAfofa%E6%94%B6%E5%BD%95%E7%9A%84%E6%9C%89%E8%BF%99%E4%BA%9B%E5%85%B3%E9%94%AE%E5%AD%97%E7%9A%84ip%E5%9F%9F%E5%90%8D%EF%BC%8C%E5%BE%88%E5%A4%9A%E6%97%B6%E5%80%99%E8%83%BD%E8%8E%B7%E5%8F%96%E7%BD%91%E7%AB%99%E7%9A%84%E7%9C%9F%E5%AE%9Eip%E3%80%82)<br>[![](https://p5.ssl.qhimg.com/t01d8cfa919b1a0d983.png)](https://p5.ssl.qhimg.com/t01d8cfa919b1a0d983.png)<br>
图10

### <a class="reference-link" name="7.F5%20LTM%E8%A7%A3%E7%A0%81%E6%B3%95"></a>7.F5 LTM解码法

当服务器使用F5 LTM做负载均衡时，通过对set-cookie关键字的解码真实ip也可被获取，例如：Set-Cookie: BIGipServerpool_8.29_8030=487098378.24095.0000，先把第一小节的十进制数即487098378取出来，然后将其转为十六进制数1d08880a，接着从后至前，以此取四位数出来，也就是0a.88.08.1d，最后依次把他们转为十进制数10.136.8.29，也就是最后的真实ip。

通过以上的方法，被获取到的ip可能是真实的ip、亦可能是真实ip的同c段ip，还需要要对其进行相关测试，如与域名的绑定测试等，最后才能确认它是不是最终ip。

所以，为了保护我们服务器，**我们不好轻易暴露我们的真实ip，**可以使用CDN、WAF等，在使用CDN的同时先确认ip历史记录中，是否存在你的真实ip，记得更换ip后再开启CDN。若网站有订阅邮件或发邮件的需求，可选择独立的服务器发取。子域名的ip记得隐匿，或者采取与主服务不同c段的服务器。

**安胜**作为国内领先的网络安全类产品及服务提供商，秉承**“创新为安，服务致胜”**的经营理念，专注于网络安全类产品的生产与服务；以**“研发+服务+销售”**的经营模式，**“装备+平台+服务”**的产品体系，在技术研究、研发创新、产品化等方面已形成一套完整的流程化体系，为广大用户提供量体裁衣的综合解决方案！

我们拥有独立的技术及产品的预研基地—**ISEC实验室，**专注于网络安全前沿技术研究，提供网络安全培训、应急响应、安全检测等服务。此外，实验室打造独家资讯交流分享平台—**“ISEC安全e站”，**提供原创技术文章、网络安全信息资讯、实时热点独家解析等。


