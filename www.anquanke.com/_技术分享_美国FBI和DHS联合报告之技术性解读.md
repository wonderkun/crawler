> 原文链接: https://www.anquanke.com//post/id/85273 


# 【技术分享】美国FBI和DHS联合报告之技术性解读


                                阅读量   
                                **78781**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：wordfence.com
                                <br>原文地址：[https://www.wordfence.com/blog/2016/12/russia-malware-ip-hack/](https://www.wordfence.com/blog/2016/12/russia-malware-ip-hack/)

译文仅供参考，具体内容表达以及含义原文为准



**[![](https://p4.ssl.qhimg.com/t0121fc522c0182beda.jpg)](https://p4.ssl.qhimg.com/t0121fc522c0182beda.jpg)**

**翻译：**[**pwn_361******](http://bobao.360.cn/member/contribute?uid=2798962642)

**预估稿费：200RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**前言**

美国政府近几个月正式[指责俄罗斯](https://www.washingtonpost.com/world/national-security/us-government-officially-accuses-russia-of-hacking-campaign-to-influence-elections/2016/10/07/4e0b9654-8cbf-11e6-875e-2c1bfe943b66_story.html?utm_term=.cfc384b87313)干涉美国大选，去年10月7日，国土安全部和国家情报局[发布联合声明](https://www.dhs.gov/news/2016/10/07/joint-statement-department-homeland-security-and-office-director-national)：美国情报界（USIC）相信，俄罗斯政府用电子邮件攻击美国的个人和机构，包括美国的政治组织。

12月29日，[奥巴马政府](https://www.washingtonpost.com/world/national-security/obama-administration-announces-measures-to-punish-russia-for-2016-election-interference/2016/12/29/311db9d6-cdde-11e6-a87f-b917067331bb_story.html?utm_term=.34642a8f19d3)宣布将驱逐35名俄罗斯外交官，并关闭两个俄罗斯在美国的设施，作为俄罗斯干预美国2016年大选的惩罚。

<br>

**DHS和DNI联合发布分析报告**

此外，12月29日美国国土安全部（DHS）和美国国家情报局（DNI）[联合发布了一份分析报告](https://www.us-cert.gov/security-publications/GRIZZLY-STEPPE-Russian-Malicious-Cyber-Activity)。该报告由DHS和FBI编制，他们声称俄罗斯代号为“草原灰熊”的黑客组织干扰了美国大选。

在这份报告中有这样一段：“本文档提供俄罗斯非军事和军事情报机构(RIS)所使用的工具和基础设施的技术细节，及攻击美国大选的网络和节点、政府、政党和私营部门等情况，这个报告包含明确的攻陷标志，包括IP地址和一个PHP恶意样本。”

因为Wordfence公司主要从事WordPress相关安全工作，因为WordPress是用PHP写的，因此，我们的安全分析师花了大量时间对这个PHP恶意样本进行了分析。

作为一个有趣的小项目，我们分析了美国政府提供PHP恶意样本，及公布的IP地址[[Source]](https://www.us-cert.gov/security-publications/GRIZZLY-STEPPE-Russian-Malicious-Cyber-Activity)。

我们分析DHS提供的PHP恶意样本数据。同时，我们也试图找到完整的恶意样本。我们发现攻击者试图用它来感染WordPress网站，还好，我们成功发现了完整的恶意样本，并过滤出来了。下面就是。

[![](https://p2.ssl.qhimg.com/t01f445e37a57d36b20.png)](https://p2.ssl.qhimg.com/t01f445e37a57d36b20.png)

上图是头部，下图是尾部。中间包含了一个加密的文本块。

[![](https://p4.ssl.qhimg.com/t016ffcc74be43f2112.png)](https://p4.ssl.qhimg.com/t016ffcc74be43f2112.png)

这是上传到一个服务器上的PHP恶意软件。攻击者可以通过浏览器访问、并需要输入一个密码。这个密码同时也是一个解密密钥，这个密钥会解密中间的加密块，然后执行解密的块。一旦攻击者输入了他们的密码，会自动存储一个cookie，以后攻击者再访问PHP恶意软件时，就不用再输入密码了。

我们对一个攻击者的HTTP请求进行了嗅探，成功抓到了他们的密码，密码是“avto”。我们使用这个密码对加密块进行解密。

下面是解密的文本，看起来像是PHP代码。这是一大块PHP代码，是一个WEBSHELL。

[![](https://p5.ssl.qhimg.com/t0184a9536347f367ff.png)](https://p5.ssl.qhimg.com/t0184a9536347f367ff.png)

我们将这个WEBSHELL安装到了沙盒环境中，下面是它的界面：

[![](https://p2.ssl.qhimg.com/t01b49ebff2a8660013.png)](https://p2.ssl.qhimg.com/t01b49ebff2a8660013.png)

这种类型的WEBSHELL，我们经常能看到，它包含了以下几个基本功能：

1.文件浏览器/资源管理器。

2.文件搜索功能。

3.一个能下载数据库内容的黑客数据库客户端。

4.端口扫描工具，及将某服务绑定到特定端口的功能。

5.对FTP和POP3服务进行暴力破解的功能。

6.运行任意操作系统命令的命令行客户端。

7.查看服务器配置信息的功能。

通过查看源代码，我们可以找到恶意软件的名称和版本，它是“P.A.S. 3.1.0”。

我们在GOOGLE上搜索了该恶意软件，发现有一个网站可以在线生成这个恶意软件(目前已经无法访问到)。

[![](https://p2.ssl.qhimg.com/t012df842d193281a55.png)](https://p2.ssl.qhimg.com/t012df842d193281a55.png)

你可以在网页中输入一个密码，这个密码就是生成的PHP恶意软件的密码。然后点击“download”按键，可以下载一个ZIP文件。文件中包含了一个TXT文件和该PHP恶意软件。

[![](https://p3.ssl.qhimg.com/t018ad5fc2a2be1cde5.png)](https://p3.ssl.qhimg.com/t018ad5fc2a2be1cde5.png)

这个网站声称该PHP恶意软件是乌克兰人制作的，同时，PHP恶意代码的底部有乌克兰的国家代码“UA”。

不过，在网站上生成的PHP恶意软件版本是3.1.7，这比DHS声称的版本(3.1.0)要新，不过，这两个版本的PHP恶意软件代码相差不多，下图是3.1.7版本的头部：

[![](https://p2.ssl.qhimg.com/t013f96f3122e08d289.png)](https://p2.ssl.qhimg.com/t013f96f3122e08d289.png)

下图是尾部：

[![](https://p0.ssl.qhimg.com/t0101b7b9d8cbac8361.png)](https://p0.ssl.qhimg.com/t0101b7b9d8cbac8361.png)

但是这个PAS恶意软件从3.1.7以后有了更深的发展，新版本是4.1.1b，可以从相同的网站中得到：

[![](https://p0.ssl.qhimg.com/t019b84810acd4b43a5.png)](https://p0.ssl.qhimg.com/t019b84810acd4b43a5.png)

下面是4.1.1b版本的info.txt文件的内容：

[![](https://p2.ssl.qhimg.com/t01f4a1f13d64a0bde9.png)](https://p2.ssl.qhimg.com/t01f4a1f13d64a0bde9.png)

并且，4.1.1b版本的代码变化相当大，下图是它的头部：

[![](https://p2.ssl.qhimg.com/t01084fb72f14ef9aab.png)](https://p2.ssl.qhimg.com/t01084fb72f14ef9aab.png)

<br>

**PAS怎么感染WordPress网站？**

下面是DHS的PAS 3.1.0样本的一个典型感染过程：

[![](https://p4.ssl.qhimg.com/t01243529c6e3acd745.png)](https://p4.ssl.qhimg.com/t01243529c6e3acd745.png)

上面是一个HTTP请求，包含了需要上传的PAS 3.1.0恶意软件，利用了WordPress正常插件更新机制。让我们感到惊奇的是这个请求有完整的cookies，表明这个帐号或机器已经是登录的，且这很有可能是一个实际的WEB浏览器。

还包含了WordPress的“nonce”功能(Nonce是WordPressr的一个安全功能，可以防止受到CSRF的攻击)，这是一个安全功能，这也表明这可能是一个合法的登录帐号。我们看到只有25%的攻击者请求中包含了WordPress的“nonce”，这也说明有很多这样的尝试是失败的。

我们看到：大部分攻击者尝试用PAS 3.1.0攻击目标时都用的这种请求方法，但是发这样的请求包是需要登录进去的，那么攻击者到底是怎么实现的呢？在这里我们假想一下可能性：

1.WordPress网站拥有者将恶意软件安装到了自己的工作站，该恶意软件试图在自己的WordPress网站安装PAS 3.1.0。

2.这是CSRF，跨站请求伪造攻击，并安装了恶意软件。这不太可能，因为在许多请求中包含了“nonce”，而nonce的功能就是防御CSRF攻击。

3.用户从一个他认为安全的恶意网站上下载了恶意软件，然后自愿安装在自己的网站上。不太像，因为上传的是明文的PHP文件，如果用户检查文件的内容是很容易发现的。

4.攻击者通过其他的手段攻破了网站，然后在正常浏览器下，使用登录凭证登录到网站中，并安装了PAS 3.1.0。这些登录可以部分或完全自动化。

<br>

**关于恶意软件的总结**

DHST和DNI发布的联合声明是这样说的：

“本文档提供俄罗斯非军事和军事情报机构(RIS)所使用的工具和基础设施的技术细节，及攻击美国大选网络和节点、政府、政党和私营部门等情况，这个报告包含明确的攻击指标，包括IP地址和一个PHP恶意样本。”

声明中提供的PHP恶意软件样本似乎是P.A.S 3.1.0，这是一个通用的恶意软件，并且该恶意软件的作者在他们的网站上声明自己是乌克兰人，并且该恶意软件版本比较多，最新的是P.A.S 4.1.1b。人们可能会期望‘俄罗斯’情报局开发他们自己的工具，或者至少使用外部来源的最新恶意软件。

<br>

**分析DHS和DNI提供的IP地址**

DNS提供了876个IP地址，作为攻陷标志的一部分。让我们看一看这些IP地址位于哪里，下图显示了IP地址按国家排列的分布情况：

[![](https://p2.ssl.qhimg.com/t0103dbba5e35f11667.png)](https://p2.ssl.qhimg.com/t0103dbba5e35f11667.png)

正如你看到的，它们分布在全球范围内，美国占了很大一部分。

下图是按ISP排列的部分结果：

[![](https://p2.ssl.qhimg.com/t018e37221e83bf3be6.png)](https://p2.ssl.qhimg.com/t018e37221e83bf3be6.png)

还有几个托管公司，如[OVH SAS](https://www.ovh.com/us/)，[Digital Ocean](https://www.digitalocean.com/)，[Linode](https://www.linode.com/)和[Hetzner](https://www.hetzner.de/fi/)。这些托管公司给WordPress用户和其他PHP应用软件用户提供低成本的托管服务。我们在业内可以看到一个黑客攻击的常见模式，就是托管主机上的帐户被攻破，然后被用于在网上发动攻击。

在876个IP地址之外，DHS还提供了134个其他IP，占15%，全是是TOR的出口节点IP。这些是匿名网关，可以为任何人提供匿名浏览服务。

[![](https://p5.ssl.qhimg.com/t01ca2f1be86159d643.png)](https://p5.ssl.qhimg.com/t01ca2f1be86159d643.png)

我们检查了我们的攻击数据库，想看一看DHS提供的IP有哪些同时在攻击 Wordfence用户的网站。我们在过去60天内总共发现了385个活跃的IP地址。这些IP地址在60天内发起了21095492次复杂的攻击，这些攻击都被[Wordfence](https://www.wordfence.com/)防火墙拦截了。我们认为攻击者的每一次复杂的攻击，都有可能是在尝试利用一个漏洞，用于获取目标的权限。

同时在这一时期，我们也记录到了14463133次针对WordPress的暴力破解攻击。

下面的图表显示了每个IP地址的攻击次数分布。这只考虑了复杂的攻击。正如你看到的，根据我们的监测，一小部分DHS提供的IP需要对这一时间被攻击的大部分WordPress网站负责。

[![](https://p5.ssl.qhimg.com/t01005fe69cde7707a6.png)](https://p5.ssl.qhimg.com/t01005fe69cde7707a6.png)

下面是过去60天内，DHS报告提供的IP地址中，按复杂攻击次数排序的前50个IP地址。

[![](https://p1.ssl.qhimg.com/t01fa1fa76eb593b21b.png)](https://p1.ssl.qhimg.com/t01fa1fa76eb593b21b.png)

正如你看到的，有很多排名靠前的IP址是TOR的出口节点IP。根据我们的监测，还有一此相对较少的IP地址，发动了大多数对网站的攻击。

<br>

**关于IP地址数据的总结**

我们看到的IP地址来自于广泛的国家和托管服务提供商。15%的IP地址是TOR的出口节点。这些出口节点可以被任何匿名用户使用，包括恶意行为。

<br>

**总体总结**

DHS提供的IP地址可以被一个国家背景的攻击者用于攻击活动中，比如俄罗斯。但是他们似乎并没有提供明显的东西，来证明与俄罗斯有关联。这些IP地址可以被很多其它恶意行为利用，特别是15%的IP地址是TOR出口节点。

同时，报告中的PHP恶意样本的版本比较旧，该PHP恶意软件似乎是乌克兰人做的，并且被广泛使用。与俄罗斯情报机构似乎没有明显的关系，它可以是任何网站被攻陷的标志。

你可以在[github](https://github.com/wordfence/grizzly)里找到这个报告中用到的数据。

<br>

**相关说明**

需要说明的是，上面这篇报告发表以后，被世界广泛报道，很多人对我们的文章标题有一定的误解，对于这篇报告有很多疑问，针对这个问题，我们又发布了一篇FAQ，来解答各种疑问。它包含了我们研究结果的总结，回答了一些读者关心的问题。并提供了我们研究方法的背景。你可以在阅读这份报告之前或之后阅读它。

<br>

**国内相关报道**

[http://www.freebuf.com/news/124373.html](http://www.freebuf.com/news/124373.html)

<br>

**参考**

[https://www.wordfence.com/blog/2017/01/election-hack-faq/](https://www.wordfence.com/blog/2017/01/election-hack-faq/)

[http://www.aqniu.com/news-views/22113.html](http://www.aqniu.com/news-views/22113.html?utm_source=tuicool&amp;utm_medium=referral)
