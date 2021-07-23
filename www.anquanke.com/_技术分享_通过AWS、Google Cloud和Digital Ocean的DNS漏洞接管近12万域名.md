> 原文链接: https://www.anquanke.com//post/id/85068 


# 【技术分享】通过AWS、Google Cloud和Digital Ocean的DNS漏洞接管近12万域名


                                阅读量   
                                **84305**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://thehackerblog.com/the-orphaned-internet-taking-over-120k-domains-via-a-dns-vulnerability-in-aws-google-cloud-rackspace-and-digital-ocean/](https://thehackerblog.com/the-orphaned-internet-taking-over-120k-domains-via-a-dns-vulnerability-in-aws-google-cloud-rackspace-and-digital-ocean/)

译文仅供参考，具体内容表达以及含义原文为准

<br style="text-align: left">

[![](https://p4.ssl.qhimg.com/t011617f3abac2a6395.png)](https://p4.ssl.qhimg.com/t011617f3abac2a6395.png)



翻译：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB（不服你也来投稿啊！）

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

<br>

**前言**



不久之前，我在云主机提供商Digital Ocean的域名导入系统中发现了一个安全漏洞，攻击者或可利用这个漏洞接管两万多个域名【[报告传送门](https://thehackerblog.com/floating-domains-taking-over-20k-digitalocean-domains-via-a-lax-domain-import-system/index.html)】。如果你还没有阅读这篇报告的话，我去建议你在阅读本篇文章之前先大致看一看这份报告。在此之前，我还以为只有Digital Ocean的域名系统中才存在这个问题。但是我在进一步分析后发现，目前很多主流的DNS服务提供商其系统中都存在这个漏洞。如果你也在使用第三方的DNS服务，那么你也会受到该漏洞的影响。

**<br>**

**漏洞分析**



很多DNS服务提供商都允许用户向自己的账号中添加域名，但是在添加域名的过程中系统并没有对域名所有者的身份进行验证，这也是导致该漏洞的根本原因。实际上，这也是目前的云服务提供商普遍采用的一种处理流程，包括AWS、Google Cloud、Rackspace和Digital Ocean在内。

当用户在这些云服务中使用域名时，Zone文件在被删除之后并没有修改域名的域名服务器。这也就意味着，云服务仍然可以正常使用这些域名，但是用户账号中却没有相应的Zone文件来控制这些域名。所以，任何人此时都可以创建一个DNS Zone（DNS区域）来控制这些域名。攻击者可以利用这些被控制的域名来搭建网站、颁发SSL/TLS证书或者托管邮件服务器等等。更糟糕的是，目前已经有超过十二万个域名会受到该漏洞的影响，而受影响的域名数量还在增加。

<br>

**通过DNS来检测受影响的域名**



检测这个漏洞的过程相对来说还是比较有趣的，我们可以通过对目标域名服务器进行简单的DNS查询（[NS查询](https://en.wikipedia.org/wiki/List_of_DNS_record_types#Resource_records)）来枚举出受影响的域名。如果域名存在问题的话，域名服务器将会返回一个[SERVFAIL错误或REFUSED DNS错误](https://support.opendns.com/entries/60827730-FAQ-What-are-common-DNS-return-or-response-codes-)。在这里我们使用了[DNS工具（dig）](https://en.wikipedia.org/wiki/Dig_(command))来进行一次简单的查询请求，具体如下所示：



```
ubuntu@ip-172-30-0-49:~/$ dig NS zz[REDACTED].net
; &lt;&lt;&gt;&gt; DiG 9.9.5-3ubuntu0.8-Ubuntu &lt;&lt;&gt;&gt; NS zz[REDACTED].net
;; global options: +cmd
;; Got answer:
;; -&gt;&gt;HEADER&lt;&lt;- opcode: QUERY, status: SERVFAIL, id: 62335
;; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1
;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;zz[REDACTED].net.                 IN      NS
;; Query time: 73 msec
;; SERVER: 172.30.0.2#53(172.30.0.2)
;; WHEN: Sat Sep 17 16:46:30 PDT 2016
;; MSG SIZE  rcvd: 42
```



从上面这段响应信息中可以看到，我们收到了一个DNS SERVFAIL错误，说明这个域名已经受到漏洞影响了。

如果我们收到的是一个SERVFAIL响应，那么我们如何才能知道这个域名的域名服务器呢？实际上，dig命令已经帮我们找到了这个域名的域名服务器了，只不过还没有显示给我们而已。

首先，直接查询关于.net顶级域名的信息（本例中为.net）：



```
ubuntu@ip-172-30-0-49:~$ dig NS net.
; &lt;&lt;&gt;&gt; DiG 9.9.5-3ubuntu0.8-Ubuntu &lt;&lt;&gt;&gt; NS net.
;; global options: +cmd
;; Got answer:
;; -&gt;&gt;HEADER&lt;&lt;- opcode: QUERY, status: NOERROR, id: 624
;; flags: qr rd ra; QUERY: 1, ANSWER: 13, AUTHORITY: 0, ADDITIONAL: 1
;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;net.                           IN      NS
;; ANSWER SECTION:
net.                    2597    IN      NS      b.gtld-servers.net.
net.                    2597    IN      NS      c.gtld-servers.net.
net.                    2597    IN      NS      d.gtld-servers.net.
net.                    2597    IN      NS      e.gtld-servers.net.
net.                    2597    IN      NS      f.gtld-servers.net.
net.                    2597    IN      NS      g.gtld-servers.net.
net.                    2597    IN      NS      h.gtld-servers.net.
net.                    2597    IN      NS      i.gtld-servers.net.
net.                    2597    IN      NS      j.gtld-servers.net.
net.                    2597    IN      NS      k.gtld-servers.net.
net.                    2597    IN      NS      l.gtld-servers.net.
net.                    2597    IN      NS      m.gtld-servers.net.
net.                    2597    IN      NS      a.gtld-servers.net.
;; Query time: 7 msec
;; SERVER: 172.30.0.2#53(172.30.0.2)
;; WHEN: Sat Sep 17 16:53:54 PDT 2016
;; MSG SIZE  rcvd: 253
```

现在，我们可以查询列表中的域名服务器，并找出目标域名的域名服务器：



```
ubuntu@ip-172-30-0-49:~$ dig NS zz[REDACTED].net @a.gtld-servers.net.
; &lt;&lt;&gt;&gt; DiG 9.9.5-3ubuntu0.8-Ubuntu &lt;&lt;&gt;&gt; NS zz[REDACTED].net @a.gtld-servers.net.
;; global options: +cmd
;; Got answer:
;; -&gt;&gt;HEADER&lt;&lt;- opcode: QUERY, status: NOERROR, id: 3529
;; flags: qr rd; QUERY: 1, ANSWER: 0, AUTHORITY: 2, ADDITIONAL: 3
;; WARNING: recursion requested but not available
;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;zz[REDACTED].net.                 IN      NS
;; AUTHORITY SECTION:
zz[REDACTED].net.          172800  IN      NS      dns1.stabletransit.com.
zz[REDACTED].net.          172800  IN      NS      dns2.stabletransit.com.
;; ADDITIONAL SECTION:
dns1.stabletransit.com. 172800  IN      A       69.20.95.4
dns2.stabletransit.com. 172800  IN      A       65.61.188.4
;; Query time: 9 msec
;; SERVER: 192.5.6.30#53(192.5.6.30)
;; WHEN: Sat Sep 17 16:54:48 PDT 2016
;; MSG SIZE  rcvd: 129
```



我们可以看到，这个域名的域名服务器为dns1.stabletransit.com和dns2.stabletransit.com，接下来我们就可以针对这两个域名服务器来进行操作了。

为了找出受该漏洞影响的域名，在这里我使用了我自己的[Zone文件](https://www.verisign.com/en_US/channel-resources/domain-registry-products/zone-file/index.xhtml)（适用于顶级域名.com和.net）。这些Zone文件中记录了每一个.com和.net域名所对应的域名服务器，通过这些数据我们就可以找出某一特定的云服务商所托管的全部域名了，因为这些域名服务器肯定属于这些云服务提供商。接下来，我们就可以使用一个Python脚本来向每一个域名发送请求，并检查SERVFAIL或REFUSED DNS错误。最后，我们需要使用云服务管理面板来查看是否可以将这些域名添加至我们的账号中，以确认漏洞的存在。

<br>

**Google Cloud DNS（约2.5K个域名受到影响，状态：已修复）**



Google Cloud提供了DNS管理服务，用户只需简单的操作便可以在其中添加新的域名。点击【[这里](https://cloud.google.com/dns/quickstart#create_a_managed_zone_and_a_record)】获取详细的操作步骤。一般情况下的操作步骤如下所示：

1. 进入Google Cloud账号的DNS管理面板：

[     https://console.cloud.google.com/networking/dns](https://console.cloud.google.com/networking/dns)

2. 点击“+ Create Zone”按钮；

3. 创建一个新的Zone并为Zone和域名命名；

4. 点击“Create”按钮创建这个新的Zone；

    注意，域名服务器列表已经返回给你了，在本例中我所收到的信息如下图所示：

[![](https://p5.ssl.qhimg.com/t012785b31228df74d2.png)](https://p5.ssl.qhimg.com/t012785b31228df74d2.png)

5. 检查我们的域名服务器与列表中显示的域名服务器地址是否相匹配，如果不匹配的话，删除这个Zone文件然后再试一次；

6. 当你最终获取到了相匹配的域名服务器列表之后，你也就获取到了目标域名DNS的完整控制权了；

<br>

**AWS（约54K个域名受到影响，状态：已部署多个缓解措施）**



亚马逊的DNS管理服务名叫Route53。他们拥有大量的域名服务器，这些域名服务器覆盖了多个域名和顶级域名。当用户发出请求时，系统会随机返回某个域名服务器的地址。一开始我还以为这是为了预防某种类型的漏洞而设计的，但是由于他们也会受到该漏洞的影响，所以我认为这种处理方式应该是为了确保顶级域名的DNS查询效率而设计的。

下面给出的这些操作步骤可以让你在几分钟之内接管目标域名：

1. 使用AWS Route53的API为目标域名创建一个新的Zone；

2. 检查返回的域名服务器信息是否正确，如果返回的域名服务器地址与目标域名服务器不匹配，则移除列表中的Zone。下图所示的是系统针对某一域名所返回的域名服务器：

[![](https://p0.ssl.qhimg.com/t014fcfb634bfbc3193.png)](https://p0.ssl.qhimg.com/t014fcfb634bfbc3193.png)

3. 如果返回的域名服务器与目标域名服务器不匹配，则删除Zone；

4. 不断重复这个步骤，直到你获取到所有受影响的域名服务器；

5. 现在，创建相应的DNS记录；

   在下面这个示例中，我们为一个目标域名创建了四个Zone，每一个Zone包含有一个目标域名服务器：

[![](https://p5.ssl.qhimg.com/t01217cabadf3d638ad.png)](https://p5.ssl.qhimg.com/t01217cabadf3d638ad.png)

使用这种方法，我们就可以成功接管大约五万四千多个域名了。

<br>

**Digital Ocean（约20K个域名受到影响）**



如果各位想要了解Digital Ocean的受影响情况，请参阅这份报告【[传送门](https://thehackerblog.com/floating-domains-taking-over-20k-digitalocean-domains-via-a-lax-domain-import-system/index.html)】。

**<br>**

**攻击者能做什么？**



这个漏洞的攻击场景主要分为两种情况，及有针对性的和无针对性的。根据攻击者目标的不同，具体情况需要具体分析。

**针对性攻击**

在这种攻击场景下，攻击者的目标是某一特定的域名或者是属于攻击目标的多个域名。此时，攻击者可以创建一个脚本来对目标域名的域名服务器自动执行NS查询。脚本可以检测其是否接收到了SERVFAIL或REFUSED DNS错误，如果目标域名不存在相应的DNS Zone，那么脚本便会立即尝试分配目标域名的域名服务器。

[![](https://p4.ssl.qhimg.com/t012538a57a62fa9f19.png)](https://p4.ssl.qhimg.com/t012538a57a62fa9f19.png)

**无针对性的攻击**



这种攻击场景发生的可能性更高，在我看来，攻击者感兴趣的只是利用这些域名来传播恶意软件或者进行与垃圾邮件有关的活动。由于很多威胁情报服务在对域名进行评估时，会根据域名的使用时间、注册时长、以及注册成本来分析域名的安全性。因此，劫持一个已存在的域名远比注册一个新域名要划算得多。除此之外，攻击者还可以利用这些被劫持的域名来隐藏自己的身份，因为这些域名的WHOIS信息指向的并非是真正发动攻击的人。这样一来，即便是恶意攻击活动被发现了，其背后的始作俑者也可以全身而退。

**<br>**

**总结**



这个漏洞是一个系统问题，目前主流的DNS服务提供商都会受到该漏洞的影响。除了本文中专门列出的提供商之外，还有很多其他受影响的DNS域名服务提供商没有提及到。因此，我们建议所有的DNS域名服务提供商尽快检查自己的域名系统中是否存在这个安全问题，如果存在的话，请尽快修复相应的漏洞。

<br style="text-align: left">
