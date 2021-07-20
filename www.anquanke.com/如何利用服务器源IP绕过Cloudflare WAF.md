> 原文链接: https://www.anquanke.com//post/id/183238 


# 如何利用服务器源IP绕过Cloudflare WAF


                                阅读量   
                                **385289**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者detectify，文章来源：blog.detectify.com
                                <br>原文地址：[https://blog.detectify.com/2019/07/31/bypassing-cloudflare-waf-with-the-origin-server-ip-address/](https://blog.detectify.com/2019/07/31/bypassing-cloudflare-waf-with-the-origin-server-ip-address/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t018a62abcb831a503a.png)](https://p5.ssl.qhimg.com/t018a62abcb831a503a.png)



## 0x00 前言

Cloudflare是广泛使用的一款Web应用防火墙（WAF）服务商，如果我们可以在一秒内绕过这类防护，使防守方功亏一篑，那显然是非常有趣的一件事。在本文中，我们将介绍如何使用源服务器IP地址绕过Cloudflare WAF。

需要注意的是，这里提到的方法并不局限于Cloudflare WAF，其他类型的WAF可能也会受到影响。



## 0x01 Cloudflare简介

Cloudflare支持超过[1600万项](https://www.cloudflare.com/case-studies/)因特网属性，现在是最受欢迎的WAF之一。在一年以前，Cloudflare发布了快速DNS解析服务，并且很快成为最热门的一项服务。作为反向代理，WAF不仅仅提供了针对DDOS的一种防护方案，还会在检测到攻击行为时触发警报。对于付费订阅用户而言，他们还可以选择针对常见漏洞的防护服务（如SQLi、XSS以及CSRF），但这些服务必须手动启用，此外免费用户无法享受这些服务。

虽然WAF在阻止基础payload方面非常有效，但人们不断开发绕过Cloudflare WAF的许多方法，并且每天都会出现新的绕过技术，因此我们需要时刻测试Cloudflare的安全性。在我撰写本文时，Cloudflare WAF的拦截状态如下图所示：

[![](https://p3.ssl.qhimg.com/t016e07f895b38e6dff.png)](https://p3.ssl.qhimg.com/t016e07f895b38e6dff.png)

也有研究人员在[推特](https://twitter.com/le4rner/status/1146453980400082945?ref_src=twsrc%5Etfw)上提供了一些绕过思路：

[![](https://p4.ssl.qhimg.com/t010323d0fb9c8840ed.png)](https://p4.ssl.qhimg.com/t010323d0fb9c8840ed.png)

作为一名bug猎人（黑客），绕过防火墙显然是非常有吸引力的一个任务。为了完成该任务，我们基本上可以有3种选择：

1、自定义payload以绕过目标部署的规则。虽然提高自身的防火墙绕过技术可能是非常有趣的一个过程，但这也可能是非常繁琐且费时的一项任务。作为bug猎人，我们可能无法承受这一点，毕竟时间因素最为重要。如果我们选择这个方向，那么可以尝试[PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)中列出的各种payload，或者在推特上搜索是否有解决方案。

2、以适当的方式更改请求，扰乱服务器逻辑。与上一个选项相同，这可能也是非常耗时的一种方式，需要充足的耐心以及掌握fuzz技能。[Soroush Dalili](https://twitter.com/irsdl)之前提供过一种思路，可以使用[HTTP协议以及Web服务器行为](https://www.slideshare.net/SoroushDalili/waf-bypass-techniques-using-http-standard-and-web-servers-behaviour)来构造这类请求。

3、查找Web服务器原始IP来绕过Cloudflare。可能这是最简单的一种方法，不需要掌握特别的技能，也是信息收集过程中的一个环节，因此也不会浪费时间。一旦获取该地址，我们再也不用担心WAF或者其他DDOS防护方案（比如限制请求速率）。

在本文中，我将重点关注最后一种方案，介绍如何提取原始服务器IP地址。

> 注意：Cloudflare也是需要（通常由开发者或者系统管理员）设置的一种工具，因此如果出现错误配置情况，可能会受到本文描述的攻击技术影响。



## 0x02 信息收集

首先我们可以进行正常的信息收集过程，尽可能抓取各种IP地址（通过host、nslookup、whois、[地址段](https://bgp.he.net/)等），然后检查哪些服务器启用了Web服务（通过netcat、nmap、masscan等）。一旦获取到Web服务器IP地址，下一步就是检查目标域名是否以[虚拟主机](https://httpd.apache.org/docs/2.4/en/vhosts/examples.html)方式托管在某个平台上。如果不采用这种方式，我们就可以看到默认的服务器页面或者默认配置的站点页面，否则我们就找到了切入点。这里我们可以使用Burp：

1、正确的子域名对应错误的IP地址：

[![](https://p1.ssl.qhimg.com/t014940220681f7792a.jpg)](https://p1.ssl.qhimg.com/t014940220681f7792a.jpg)

2、错误的子域名对应正确的IP地址：

[![](https://p2.ssl.qhimg.com/t01379627e027370ca2.jpg)](https://p2.ssl.qhimg.com/t01379627e027370ca2.jpg)

3、正确的子域名对应正确的IP地址，完美：

[![](https://p0.ssl.qhimg.com/t01527b65e37d748163.jpg)](https://p0.ssl.qhimg.com/t01527b65e37d748163.jpg)

当然有些工具可以帮我们自动化完成这个过程：

[https://pentest-tools.com/information-gathering/find-virtual-hosts](https://pentest-tools.com/information-gathering/find-virtual-hosts)<br>[https://github.com/jobertabma/virtual-host-discovery](https://github.com/jobertabma/virtual-host-discovery)<br>[https://github.com/gwen001/vhost-brute](https://github.com/gwen001/vhost-brute)



## 0x03 Censys

如果我们的目标部署了SSL证书（非常正常的情况），那么我们就可以使用[Censys](https://censys.io/certificates)数据库（强烈建议大家订阅该服务）。在输入框中选择“Certificates”，输入目标域名，然后回车。

我们应该能看到与目标对应的证书列表：

[![](https://p4.ssl.qhimg.com/t01a2f374e053d86a5f.png)](https://p4.ssl.qhimg.com/t01a2f374e053d86a5f.png)

我们可以点击每条结果，查看详细信息。在右侧的“Explore”菜单中选择“IPv4 Hosts”：

[![](https://p4.ssl.qhimg.com/t011eb2a823037403bd.png)](https://p4.ssl.qhimg.com/t011eb2a823037403bd.png)

这样就能看到使用该证书的服务器的IP地址：

[![](https://p1.ssl.qhimg.com/t0141a4fccf98b0f6e9.png)](https://p1.ssl.qhimg.com/t0141a4fccf98b0f6e9.png)

我们可以从这出发，获取能搜到的所有IP，然后利用前面的方法尝试访问目标资源。



## 0x04 邮件头

下一步就是提取目标邮件中的头部信息，比如我们可以订阅目标服务，创建账户，使用“忘记密码”功能，或者订购某些产品……总之，我们要想办法让目标给我们发送一封邮件（这种场景下我们可以使用Burp Collaborator）。

收到邮件后，我们可以查看源代码，特别是其中的邮件头，记录下其中的所有IP地址，包括子域名，这些信息很可能与托管服务有关。然后，我们可以尝试通过这些地址访问目标。

这里我通常会使用`Return-Path`头部字段，屡试不爽：

[![](https://p0.ssl.qhimg.com/t01fd772f34fb3debb1.png)](https://p0.ssl.qhimg.com/t01fd772f34fb3debb1.png)

使用Curl来测试：

[![](https://p0.ssl.qhimg.com/t011d55aaae14cfe541.png)](https://p0.ssl.qhimg.com/t011d55aaae14cfe541.png)

另一个技巧就是从自己邮箱向目标不存在的某个邮箱地址发送一封邮件。如果投递失败，我们应该能收到服务端反馈的通知（这里感谢<a>@_3P1C</a>小伙伴提供的思路）。



## 0x05 XML-RPC Pingback

这是WordPress中非常知名的一款工具，XML-RPC（Remote Procedure Call）允许管理员使用XML请求来远程管理博客，而pingback是ping请求的响应。当站点A链接站点B时就会执行ping请求，然后站点B会通知站点A已收到请求，这就是pingback机制。

我们可以调用`https://www.target.com/xmlrpc.php`来确认该功能是否处于启用状态，应该能收到一条信息：“XML-RPC server accepts POST requests only”。

根据WordPress的[XML-PRC Pingback API](https://codex.wordpress.org/XML-RPC_Pingback_API)，该函数接收两个参数：`sourceUri`以及`targetUri`。在Burp Suite中的测试过程如下图所示：

[![](https://p3.ssl.qhimg.com/t01953b4f35abc63135.jpg)](https://p3.ssl.qhimg.com/t01953b4f35abc63135.jpg)

这里要感谢<a>@Rivitheadz</a>提供的思路。



## 0x06 其他研究成果

如果我们无法使用这些方法找到原始IP，或者在进行信息收集时，目标站点没有部署防护措施，但最后却部署完毕，这种情况下我们要记住一点：有时候目标本身就可以告诉我们许多有价值的信息。

这里基本的原理就是想办法让目标Web服务器向我们自己的服务器/Collaborator发起请求。我们也可以采用其他方式，比如SSRF、XXE、XSS或者我们找到的其他突破口，注入包含我们自己服务器地址的payload，然后在服务器上检查对应的日志。如果找到任何蛛丝马迹，可以进一步检查虚拟主机信息。

这种情况下，如果目标Web服务器支持，那么即使最简单的漏洞（比如Open Redirect或者HTML/CSS注入）都能发挥重要作用。



## 0x07 相关工具

前面我们讨论了如何手动查找并检查IP地址，幸运的是，整个社区中有许多热心的开发者，帮我们开发了许多有用的工具，可以极大节省我们的工作时间。当发现目标部署Cloudflare防护措施后，我们就可以在信息收集过程中使用这些工具。

需要提一下，这些方法并不能保证100%有效，因为每个目标的实际情况都有所不同，适用于某个目标的方法可能不适用于其他目标，我的建议是大家可以都尝试一下。

这些工具包括：

[Cloudsnare.py](http://10degres.net/4IV34V5IC/)：censys证书信息（需要API密钥）<br>[HatCloud](https://github.com/HatBashBR/HatCloud)：crimeflare、ipinfo.io<br>[CrimeFlare](http://www.crimeflare.org:82/cfs.html)：crimeflare、ipinfo.io<br>[bypass-firewalls-by-DNS-history](https://github.com/vincentcox/bypass-firewalls-by-DNS-history)：securitytrails、crimeflare

[CloudFail](https://github.com/m0rtem/CloudFail)：dnsdumpster、crimeflare、子域名暴力破解<br>[CloudFlair](https://github.com/christophetd/CloudFlair)：需要censys API密钥<br>[CloudIP](https://github.com/Top-Hat-Sec/thsosrtl/blob/master/CloudIP/cloudip.sh)：通过nslookup查询某些子域名（如**ftp、cpanel、mail、direct、direct-connect、webmail、portal**等）

[![](https://p4.ssl.qhimg.com/t0107f2b8486810e2e9.jpg)](https://p4.ssl.qhimg.com/t0107f2b8486810e2e9.jpg)

[![](https://p5.ssl.qhimg.com/t01a719701299b782fc.jpg)](https://p5.ssl.qhimg.com/t01a719701299b782fc.jpg)



## 0x08 DNS资源

通过前面分析，我们已经知道最重要的一点就是尽可能多地获取相关IP地址，不论采用什么方式。DNS服务器显然是最值得关注的重点，并且历史DNS记录永远无法从互联网上抹去。这种情况下，我们可以考虑使用如下资源来查找所需信息：

Netcraft：[https://toolbar.netcraft.com/site_report?url=](https://toolbar.netcraft.com/site_report?url=)<br>
dns-trails：[https://securitytrails.com/dns-trails](https://securitytrails.com/dns-trails)<br>
DNSQueries：[https://www.dnsqueries.com/en/domain_check.php](https://www.dnsqueries.com/en/domain_check.php)<br>
DNSdumpster：[https://dnsdumpster.com/](https://dnsdumpster.com/)<br>
Shodan：[https://www.shodan.io/search?query=](https://www.shodan.io/search?query=)

也可以在HackerOne上找到一些历史案例：

[https://hackerone.com/reports/255978](https://hackerone.com/reports/255978)<br>[https://hackerone.com/reports/360825](https://hackerone.com/reports/360825)<br>[https://hackerone.com/reports/315838](https://hackerone.com/reports/315838)



## 0x09 总结

在安全行业中我们经常提到一句话：“一只水桶能装多少水取决于它最短的那块木板”。不论我们在配置Cloudflare上花了多少时间及精力，如果Cloudflare被绕过、或者Web应用可以通过服务器IP直接访问，那么Cloudflare提供的所有防护措施都将形同虚设。

可能还有其他许多方法能达到相同目的，如果大家有更好的意见或者建议，欢迎随时联系我。

虽然我个人认为这方面技术并不值得专门反馈给厂商，但根据[Soroush Dalili](https://twitter.com/irsdl/status/1043650208301830144)小伙伴的建议，绕过Cloudflare应该属于安全方面的错误配置，因此还是需要关注这方面风险。



## 0x0A 拓展阅读
- [Introducing CFire – Evading CloudFlare Security Protections](https://rhinosecuritylabs.com/cloud-security/cloudflare-bypassing-cloud-security/)
- [Cloudflare Bypass Security](http://www.securityidiots.com/Web-Pentest/Information-Gathering/Cloudflare-Bypass/Part-2-Cloudflare-Security-Bypass.html)
- [Exposing Server IPs Behind CloudFlare](http://www.chokepoint.net/2017/10/exposing-server-ips-behind-cloudflare.html)
- [CloudFlair – Bypassing Cloudflare using Internet-wide scan data](https://blog.christophetd.fr/bypassing-cloudflare-using-internet-wide-scan-data/)
- [Cloudflare IP ranges](https://www.cloudflare.com/ips/)
- [相关推文A](https://twitter.com/gwendallecoguic/status/1043484797799223297)
- [相关推文B](https://twitter.com/gwendallecoguic/status/1113777240876228609)