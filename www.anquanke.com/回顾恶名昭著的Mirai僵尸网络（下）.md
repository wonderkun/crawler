> 原文链接: https://www.anquanke.com//post/id/89120 


# 回顾恶名昭著的Mirai僵尸网络（下）


                                阅读量   
                                **109517**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Elie Bursztein，文章来源：elie.net
                                <br>原文地址：[https://www.elie.net/blog/security/inside-mirai-the-infamous-iot-botnet-a-retrospective-analysis](https://www.elie.net/blog/security/inside-mirai-the-infamous-iot-botnet-a-retrospective-analysis)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t016ccce9d1457c00ae.png)](https://p3.ssl.qhimg.com/t016ccce9d1457c00ae.png)



## 传送门

[回顾恶名昭著的Mirai僵尸网络（上）](https://www.anquanke.com/post/id/89119)



## 前言

本文是回顾恶名昭著的Mirai僵尸网络下半部分，包括以下内容：

1、模仿者的兴起：这一部分介绍了Mirai源代码公布事件及众多黑客组织对这个代码的重用过程。源代码发布后，涌现了许多Mirai变种，这一部分也介绍了我们用来追踪这些变种的具体技术。最后，我们也讨论了每个主流变种背后的目标及动机。

2、Mirai致瘫互联网：介绍Dyn攻击事件的内幕，表明主流站点（如Amazon）无法提供服务其实只是此次攻击的附带牺牲品而已。

3、Mirai封闭整个国家？：分析针对Lonestar（利比里亚最大运营商）的多次攻击活动。

4、德国电信陷入黑暗：讨论Mirai某个变种如何借助路由器使德国互联网提供商下跪求饶。

5、Mirai原作者身份澄清？：详细介绍Brian Krebs关于Mirai作者的调查情况，以及FBI相关案件的审讯结果。

6、德国电信攻击始作俑者被捕：介绍攻击德国电信始作俑者被捕过程，以及从案件审理中我们可以获取的信息。



## 一、模仿者的兴起：9月30日

[![](https://p2.ssl.qhimg.com/t014f2c67acd39420a4.png)](https://p2.ssl.qhimg.com/t014f2c67acd39420a4.png)

事件的发展有点出众人所料，在2017年9月30日，作为Mirai的作者，Anna-senpai通过某个臭名昭著的黑客论坛公布了[Mirai源代码](https://krebsonsecurity.com/2016/10/source-code-for-iot-botnet-mirai-released/)。他还在论坛上发表了一个帖子，宣布就此退出舞台，如上图所示。



源代码的公布是一个导火索，使山寨黑客不断涌现，开始运行自己的Mirai僵尸网络。从那一刻起，Mirai攻击已不局限于单一的攻击者或者单一的基础设施，而是与多个团体关联起来，这使得研究人员更加难以追踪溯源这类攻击，无法看清这些团体背后的动机。

### <a class="reference-link" name="%E8%81%9A%E7%B1%BBMirai%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD"></a>聚类Mirai基础设施

为了跟上Mirai变种的扩散速度，跟踪隐藏在这些变种背后的黑客组织，我们开始聚类分析攻击者所使用的基础设施。逆向分析所有的Mirai版本后，我们可以提取出各种黑客组织所使用的C&amp;C服务器的IP地址及域名。我们总共提取出2个IP地址以及66个不同的域名。

[![](https://p0.ssl.qhimg.com/t01688e46cc14d610b7.png)](https://p0.ssl.qhimg.com/t01688e46cc14d610b7.png)

从提取出的域名来拓展DNS信息，将这些信息聚类在一起后，我们可以识别出33个不同的C&amp;C集群（cluster），这些集群所使用的基础设施没有交集。这些集群中，最小的集群使用一个单独的IP地址作为C&amp;C地址。最大的集群拥有112个域名以及92个IP地址。我们发现的集群中，最大的6个集群如上图所示。



这些大型集群所使用的域名格式差别很大。比如，“cluster 23”喜欢与动物有关的域名，如“33kitensspecial.pw”，而“cluster 1”拥有许多与电子货币有关的域名，比如“walletzone.ru”。从结果中，我们发现了许多不同的基础设施以及不同的特征，这也进一步确认在源代码泄露后，有多个组织在独立传播Mirai变种。

### <a class="reference-link" name="%E5%8F%98%E7%A7%8D%E9%9B%86%E7%BE%A4%E6%97%B6%E9%97%B4%E7%BA%BF"></a>变种集群时间线

通过查看集群C&amp;C基础设施的DNS请求次数，我们可以重构每个集群的演进时间线，估计集群的相对规模。之所以能够通过这种方法进行统计，原因在于每个僵尸节点必须定期执行DNS查询任务，以获取C&amp;C域名所对应的IP地址。

[![](https://p1.ssl.qhimg.com/t0180f13185ea9f7b52.png)](https://p1.ssl.qhimg.com/t0180f13185ea9f7b52.png)

某几个大型集群的DNS请求次数如上图所示。从上图可知，同一时间有许多集群处于活跃状态。我们从中可以推测许多攻击者的动机有所不同，因此他们在争相夺取存在漏洞的IoT设备的控制权，根据自己需求发起DDoS攻击。

[![](https://p4.ssl.qhimg.com/t01683de6d02b689013.png)](https://p4.ssl.qhimg.com/t01683de6d02b689013.png)

将所有变种绘制在一张图上后，我们可以清楚地发现不同变种所使用的IoT设备的范围差别很大。如上图所示，虽然全世界有许多Mirai变种，但只有非常少数的几个变种能够拓展自身规模，具备攻陷主流网站的能力。

### <a class="reference-link" name="%E8%83%8C%E5%90%8E%E7%9A%84%E5%8A%A8%E6%9C%BA"></a>背后的动机

|集群|备注
|------
|6|攻击Dyn以及游戏相关目标
|1|原始僵尸网络，攻击Krebs以及OVH
|2|攻击Lonestar Cell运营商

观察大型集群所攻击的目标，我们可以分析这些集群背后的真正动机。比如，如上表所示，原始的Mirai变种（cluster 1）攻击的是OVH以及Krebs，而Mirai的最大变种（cluster 6）攻击的是DYN以及与游戏相关的其他网站。相比之下，Mirai的第三大变种（cluster 2）攻击的是非洲电信运营商，稍后我们会介绍这一点。

|目标|被攻击次数|集群|备注
|------
|Lonestar Cell|616|2|利比里亚电信运营商被反射式攻击102次
|Sky Network|318|15, 26, 6|巴西Minecraft服务器，托管在Psychz Networks数据中心
|104.85.165.1|192|1, 2, 6, 8, 11, 15 …|Akamai网络中的未知路由器
|feseli.com|157|7|俄罗斯烹饪博客
|Minomortaruolo.it|157|7|意大利政客网站
|Voxility hosted C2|106|1, 2, 6, 7, 15 …|从DNS扩展信息中发现的C2域名
|Tuidang websites|100|—|通过HTTP方式攻击中国的两个网站
|execrypt.com|96|-0-|二进制混淆服务网站
|Auktionshilfe.info|85|2, 13|俄罗斯拍卖网站
|houtai.longqikeji.com|85|25|通过SYN方式攻击原游戏商务网站
|Runescape|73|—|世界排名26的在线游戏
|184.84.240.54|72|1, 10, 11, 15 …|托管在Akamai上的未知目标
|antiddos.solutions|71|—|react.su提供的反DDoS服务

检查所有Mirai变种最喜欢攻击的服务后，我们可以得到如下结论：

1、**Mirai受按需攻击服务驱使**：被攻击的目标包含各种类别，表明某些大型集群正在提供按需攻击服务（booter service）。客户支付报酬后，网络犯罪分子会根据客户需求提供定制化的DDoS攻击服务。

2、**攻击者数量比集群数量少**：某些族群之间有高度重合的目标对象，这表明这些集群背后的攻击者应该为同一类人。比如，cluster 15、26以及6的攻击目标都是Minecraft服务器。

**“Mirai并不是由一个单独的组织来操控，而是由一群犯罪分子来操控，这些犯罪分子会因为不同的动机来运行自己的Mirai变种。”**



## 二、Mirai致瘫互联网：10月21日

[![](https://p2.ssl.qhimg.com/t016eb0e6743ed5d0c5.jpg)](https://p2.ssl.qhimg.com/t016eb0e6743ed5d0c5.jpg)

10月21日，Mirai[攻击](http://money.cnn.com/2016/10/21/technology/ddos-attack-popular-sites/index.html)了DYN（DYN是非常流行的一个DNS服务提供商）。这次攻击事件导致互联网用户无法访问许多[主流站点](https://en.wikipedia.org/wiki/2016_Dyn_cyberattack)，比如AirBnB、Amazon、Github、HBO、Netflix、Paypal、Reddit以及Twitter，这些站点都由DYN提供域名解析服务。

之前媒体报道说此次攻击目的是“使整个互联网瘫痪”，但我们认为并非如此，此次攻击的真实目标应该是游戏平台。

之所以得出这个结论，是因为我们查看了攻击DYN的变种（cluster 6）的其他攻击目标，发现这些目标都是与游戏平台有关的一些目标。此外，这个变种也跟OVH攻击事件有关，前面我们提到过该平台也托管了一些游戏服务器。非常不幸的是，DYN攻击事件中受到波及的所有站点只是各方利益争夺中的一些附带牺牲品。

**“针对DYN的大规模DDoS攻击的背后实际上是游戏行业的利益争夺，由此导致了大规模互联网中断事故。”**



## 三、Mirai封闭整个国家？：10月31日

[![](https://p3.ssl.qhimg.com/t01344ad808f85f20ad.jpg)](https://p3.ssl.qhimg.com/t01344ad808f85f20ad.jpg)

作为利比里亚最大的电信运营商之一，Lonestar Cell从10月31日开始就成为Mirai的攻击目标。在接下来的几个月内，该运营商遭受到616次攻击，是所有Mirai受害者中被攻击次数最多的一个。

[![](https://p3.ssl.qhimg.com/t013c68afa12b69b59d.jpg)](https://p3.ssl.qhimg.com/t013c68afa12b69b59d.jpg)

在早期阶段，有[报道](https://thehackernews.com/2016/11/ddos-attack-mirai-botnet.html)称这些攻击导致利比里亚互联网大部分处于瘫痪状态。比如，[Akamai](https://twitter.com/akamai_soti/status/794335101794533377)公布了如上一张图表，显示利比里亚流量处于下跌状态。然而后来证实，这一时期刚好与利比里亚的一个节假日重叠，而攻击事件很有可能只影响了少数几个网路。



与此次攻击有关的Mirai集群所使用的基础设施与原始的Mirai或者DYN变种所使用的基础设施之间没有任何交集，这表明此次攻击的始作俑者并非Mirai原始攻击者，而是由完全不同的攻击者所主导。



我们公布了这个研究成果，几个星期之后，某个Mirai变种的背后指使者在[审判](https://www.bleepingcomputer.com/news/security/hacker-bestbuy-admits-to-hijacking-deutsche-telekom-routers-with-mirai-malware/)过程中承认，他收取了不当利益来攻击Lonestar，这也证实了我们的结论。该犯罪分子承认，利比里亚的一家匿名ISP向他支付了1万美元来攻击其竞争对手。这个事实表明，我们的聚类分析方法能够精确跟踪并溯源Mirai的攻击活动。

**“针对Lonestar互联网服务提供商的DDoS攻击事件表明，IoT僵尸网络已经在行业竞争中成为一把尖兵利器。”**



## 四、德国电信陷入黑暗：11月26日

[![](https://p4.ssl.qhimg.com/t01f8445cf560447b83.jpg)](https://p4.ssl.qhimg.com/t01f8445cf560447b83.jpg)

2016年11月26日，作为德国最大的互联网服务提供商之一，德国电信（Deutsche Telekom）90万台路由器被[恶意入侵](https://www.csoonline.com/article/3144197/security/upgraded-mirai-botnet-disrupts-deutsche-telekom-by-infecting-routers.html)，导致大量用户无法正常使用服务。

[![](https://p5.ssl.qhimg.com/t01b6255f99b3a1919a.jpg)](https://p5.ssl.qhimg.com/t01b6255f99b3a1919a.jpg)

具有讽刺意味的是，此次断网事件并不是由Mirai DDoS攻击所引起，而是由一个错误实现的Mirai定制版变种所导致，该变种在尝试入侵设备时会导致设备离线宕机。这个变种同时也影响了成千上万台[TalkTalk路由器](https://motherboard.vice.com/en_us/article/nz7ky7/hackers-say-knocking-thousands-of-brits-offline-was-an-accident-mirai)。



该变种之所以能影响这么多台路由器，原因在于变种特有的一个复制模块，该模块中增加了路由器漏洞利用功能，攻击的是[CPE WAN管理协议（CPE WAN Management Protocol，CWMP）](https://en.wikipedia.org/wiki/TR-069)。CWMP协议是基于HTTP的一种协议，许多互联网提供商会使用该协议为家庭路由器、调制解调器以及其他客户终端设备（customer-on-premises，CPE）提供自动配置及远程管理功能。



除了攻击规模庞大之外，此次攻击事件也具有重要意义，该事件表明了黑客可以将非常复杂的IoT漏洞武器化，进一步构建强大的僵尸网络。我们希望德国电信事件能够起到警钟作用，推动厂商自动、强制性更新IoT设备。由于互联网用户通常需要手动更新IoT设备，因此IoT厂商如果能自动强制更新设备，这在遏制重大风险方面能起到非常好的效果。

**“IoT设备自动更新应该是一种强制性策略，以阻止攻击者利用未打补丁的IoT设备来构建大型IoT僵尸网络。”**



## 五、Mirai原作者身份澄清？

[![](https://p0.ssl.qhimg.com/t01cb5a2020fcf32507.jpg)](https://p0.ssl.qhimg.com/t01cb5a2020fcf32507.jpg)

在网站被下线的几个月内，Brian Krebs花了数百个小时的时间，来调查Mirai作者：Anna-Senpai。2017年1月初，Brian宣布，Anna-senpai的真实身份实际上是Paras Jha，他是罗格斯大学（Rutgers）的一名学生，之前曾参与过攻击游戏行业的一些黑客事件。身份公布后，FBI调查了Paras Jha。然而，截至2017年11月，官方并没有控告或证实Paras为Mirai的真实开发者。



## 六、德国电信攻击始作俑者被捕

[![](https://p4.ssl.qhimg.com/t016d0c67ee5c935013.jpg)](https://p4.ssl.qhimg.com/t016d0c67ee5c935013.jpg)

2016年11月，Daniel Kaye（又名BestBuy）在[卢顿机场](http://www.bbc.com/news/technology-37510502)被捕。Daniel Kaye是攻击德国电信的Mirai变种的始作俑者。在Mirai事件之前，这名29岁的英国公民曾在各种暗网市场上提供[黑客服务](https://krebsonsecurity.com/2017/07/who-is-the-govrat-author-and-mirai-botmaster-bestbuy/)，他也因此广为人知。



2017年7月，距离Daniel Kaye被引渡到德国后已经过去好几个月的时间，Daniel Kaye终于[承认](https://www.bleepingcomputer.com/news/security/hacker-bestbuy-admits-to-hijacking-deutsche-telekom-routers-with-mirai-malware/)检方对自己的指控，被判处1年6个月的有期徒刑。在审判期间，Daniel承认他并没有想让路由器宕机，只是想悄悄控制这些设备，利用这些设备构建僵尸网络，提升僵尸网络攻击力。前面提到过，Daniel也承认他收取了一些金钱，帮助Lonestar的竞争对手搞垮Lonestar。



2017年8月，Daniel因曾试图勒索Lloyds以及Barclays银行而被[引渡](https://www.theguardian.com/uk-news/2017/aug/30/alleged-mastermind-daniel-kaye-lloyds-bank-cyber-attacks-extradited-uk)回英国，接受勒索罪审判。根据媒体报道，Daniel要求Lloyds银行支付约75,000英镑的比特币，才会取消对该银行的攻击。



## 七、总结

互联网上存在大量不安全的IoT设备，在不久的将来，这些设备将成为DDOS攻击的主要来源。

**“Mirai事件是一个历史转折点，表明IoT设备已经成为DDoS攻击的主力军。”**

如果IoT厂商开始遵循基本的、切实可用的原则规范，那么就能避免Mirai及后续衍生的IoT僵尸网络。具体说来，IoT设备厂商应该遵循如下标准：

1、消除默认凭证：这一点能够阻止黑客构建超级凭据列表，无法像Mirai那样通过该列表危害大量设备。

2、强制使用自动更新策略：IoT设备经常被人遗忘在角落，因此用户通常不会手动更新这些设备。自动修补这些设备是唯一合理的选择，这样才能确保这些设备不存在像德国电信事件中出现的大范围漏洞，使攻击者无法利用这些漏洞控制大规模互联网。

3、采用限速策略：强制限制登录频率，避免针对这些设备的暴力破解攻击，可以减轻使用弱口令时带来的安全风险。另一个方法就是在登录过程中使用验证码或者其他验证机制。

**“如果IoT设备遵循基本的、切实有效的安全策略，就能避免出现IoT僵尸网络。”**
