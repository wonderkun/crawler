> 原文链接: https://www.anquanke.com//post/id/89119 


# 回顾恶名昭著的Mirai僵尸网络（上）


                                阅读量   
                                **204301**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Elie Bursztein，文章来源：elie.net
                                <br>原文地址：[https://www.elie.net/blog/security/inside-mirai-the-infamous-iot-botnet-a-retrospective-analysis](https://www.elie.net/blog/security/inside-mirai-the-infamous-iot-botnet-a-retrospective-analysis)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t016ccce9d1457c00ae.png)](https://p4.ssl.qhimg.com/t016ccce9d1457c00ae.png)



## 传送门

[回顾恶名昭著的Mirai僵尸网络（下）](https://www.anquanke.com/post/id/89120)



## 一、前言

作为恶名昭著的僵尸网络，Mirai攻陷了成千上万的物联网（IoT，Internet-Of-Things）设备，以这些设备作为节点发起大规模分布式拒绝服务攻击，破坏大量主流站点。随着Mirai攻击浪潮暂时告一段落，本次再次分析了这一僵尸网络的各种细节。本文是此次回顾的上半部分。

[![](https://p1.ssl.qhimg.com/t01ff2534ea8b17294e.jpg)](https://p1.ssl.qhimg.com/t01ff2534ea8b17294e.jpg)

Mirai的攻击浪潮在2016年9月达到峰值，当时该僵尸网络发起大规模[分布式拒绝服务（DDoS）攻击](https://en.wikipedia.org/wiki/Denial-of-service_attack#Distributed_DoS)，导致[OVH](https://www.ovh.com/)、[Dyn](https://dyn.com/)以及[Krebs on Security](https://krebsonsecurity.com/)等主流站点出现暂时瘫痪现象，无法正常提供服务。据OVH以及Dyn的报告，这些攻击的流量峰值超过了1Tbps，这是已知攻击中规模最大的攻击流量。



此次创纪录的攻击流量事件中，最引人注目的在于这些流量由家用路由器、空气质量检测仪以及个人监控摄像头等小型物联网（Internet-of-Things，IoT）设备所发起。根据我们的测量结果，在巅峰时期，Mirai控制了超过60万个存在漏洞的IoT设备。

**“Mirai的横空出世表明DDoS攻击活动出现了新的转折点：IoT僵尸网络已经成为此类攻击的主力军。”**

[![](https://p3.ssl.qhimg.com/t01ece018c78d1bd068.png)](https://p3.ssl.qhimg.com/t01ece018c78d1bd068.png)

Mirai的时间线如上图所示，从中我们可知，这是非常曲折的一个过程。在攻击活动幕后，许多攻击组织在控制、利用IoT设备方面的动机截然不同，也使整个演进过程充满变数。为了理清整个攻击活动，我与Akamai、Cloudflare、乔治亚理工学院、Google、伊利诺伊大学、密歇根大学以及Merit Network的研究人员合作，结合我们的感知技术及专业知识，我们共同发现了隐藏在Mirai背后的真相。

这篇文章中，我们从头到尾完整研究了Mirai的相关信息。本文主要源自于今年早些时候我们在USENIX Security发表的一篇[联合论文](https://www.elie.net/publication/understanding-the-mirai-botnet)，主要包括以下几点内容：

1、Mirai创世纪：讨论Mirai早期情况，从技术角度简要总结了Mirai的工作原理及传播方式。

2、Krebs on Security攻击事件：回顾Mirai如何搞定Brian Krebs的网站。

3、OVH攻击事件：OVH是世界上最大的托管服务商之一，我们分析了Mirai开发者在尝试攻陷OVH方面所做的工作。



## 二、Mirai创世纪

[![](https://p2.ssl.qhimg.com/t01f1bb401a84227fa7.png)](https://p2.ssl.qhimg.com/t01f1bb401a84227fa7.png)

关于Mirai最早的公开报告出现在2016年8月，当时该报告并没有引起人们太多关注，Mirai大部分时间也潜伏在暗处，直至9月中旬才开始兴起。随着Mirai开始大规模DDoS攻击Krebs on Security（知名安全记者的博客网站）以及OVH（世界上最大的虚拟主机提供商之一）站点后，公众才注意到这个新兴事物。

[![](https://p0.ssl.qhimg.com/t0187e7a2a5536d0094.png)](https://p0.ssl.qhimg.com/t0187e7a2a5536d0094.png)

虽然全世界直到8月底才发现Mirai，但我们的感知系统表明，Mirai自8月1日起已开始活跃，整个感染过程从某个防弹主机（bulletproof hosting）IP开始。从那时起，Mirai以非常快的速度开始传播，在早期传播阶段，大概每76分钟其网络规模就增大一倍。



在第一天结束时，Mirai已经感染了超过65,000个IoT设备。在第二天，在我们部署的蜜罐集群所观察到的telnet扫描行为中，Mirai已经占据了半壁江山，如上图所示。Mirai在2016年11月达到峰值，当时它已控制了超过600,000个IoT设备。

[![](https://p1.ssl.qhimg.com/t01e5d4154e7ceeb3ae.png)](https://p1.ssl.qhimg.com/t01e5d4154e7ceeb3ae.png)

[Censys](https://censys.io/)会定期扫描整个互联网，收集指纹信息，根据该项目的研究成果，我们定期观察被感染设备的服务指纹信息（banner），发现大多数设备为路由器或摄像头，如上图所示。每种类型指纹的识别过程有所不同，因此上图中我们分开表示每种类型的指纹，其中可能存在多次计数现象。Mirai会主动删除指纹识别信息，这也能部分解释为什么我们无法识别其中许多设备。

在进一步深入分析Mirai故事之前，我们先来简单看一下Mirai的工作原理，别特是Mirai的传播方法及其具体功能。

### <a class="reference-link" name="Mirai%E5%B7%A5%E4%BD%9C%E5%8E%9F%E7%90%86"></a>Mirai工作原理

从核心功能上来看，Mirai是一款能自我传播的蠕虫，也就是说，它是一款恶意程序，通过发现、攻击并感染存在漏洞的IoT设备实现自我复制。Mirai也是一种僵尸网络，因为它会通过一组中央命令控制（command and control，C&amp;C）服务器来控制被感染的设备。这些服务器会告诉已感染设备下一步要攻击哪些站点。总体而言，Mirai由两个核心组件所构成：复制模块以及攻击模块。

#### <a class="reference-link" name="%E5%A4%8D%E5%88%B6%E6%A8%A1%E5%9D%97"></a>复制模块

[![](https://p2.ssl.qhimg.com/t01592661dfb106f3cc.png)](https://p2.ssl.qhimg.com/t01592661dfb106f3cc.png)

复制模块负责扩大僵尸网络规模，具体方法是尽可能多地感染存在漏洞的IoT设备。该模块通过（随机）扫描整个互联网来寻找可用的目标并发起攻击。一旦搞定某个存在漏洞的设备，该模块会向C&amp;C服务器报告这款设备，以便使用最新的Mirai载荷来感染此设备，如上图所示。



为了感染目标设备，最初版本的Mirai使用的是一组固定的默认登录名及密码组合凭据，其中包含64个凭据组合，这些凭据是IoT设备的常用凭据。虽然这种攻击方式比较低级，但事实证明该方法效率极高，Mirai通过这种方法搞定了超过600,000个设备。

**“仅凭64个众所周知的默认登录名及密码，Mirai就能够感染600,000个IoT设备。”**

#### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E6%A8%A1%E5%9D%97"></a>攻击模块

[![](https://p4.ssl.qhimg.com/t016793b685f3ad8daf.png)](https://p4.ssl.qhimg.com/t016793b685f3ad8daf.png)

C&amp;C服务器负责指定攻击目标，而攻击模块负责向这些目标发起DDoS攻击。该模块实现了大部分DDoS技术，比如HTTP洪泛攻击、UDP洪泛攻击，以及所有的TCP洪泛攻击技术。Mirai具备多种模式的攻击方法，使其能够发起容量耗尽攻击（volumetric attack）、应用层攻击（application-layer attack）以及TCP状态表耗尽攻击（TCP state-exhaustion attack）。大家可以阅读Arbor Network发表的这篇[文章](https://www.arbornetworks.com/research/what-is-ddos)来了解关于DDoS攻击的更多信息。



## 三、Krebs攻击事件

[![](https://p4.ssl.qhimg.com/t01ef38679c7ccc8218.png)](https://p4.ssl.qhimg.com/t01ef38679c7ccc8218.png)

[Krebs on Security](https://krebsonsecurity.com/)是Brian Krebs的博客网站。Krebs是一位广为人知的独立记者，专门报导网络犯罪方面内容。由于Brian的工作方向，许多犯罪分子经常向其博客发起DDoS攻击。根据Krebs的感知数据，该博客从2012年7月到2016年9月期间遭受了269次DDOS攻击，而Mirai攻击是目前为止规模最大的一次攻击，攻击流量达到了623Gbps。

[![](https://p1.ssl.qhimg.com/t01621f0888b09526ee.png)](https://p1.ssl.qhimg.com/t01621f0888b09526ee.png)

从攻击Brian网站的IP地理分布情况来看，攻击活动中涉及的许多设备来自于南美洲以及东南亚地区，占了非常大的比重。如上图所示，巴西、越南以及哥伦比亚是被感染设备的主要分布区域。

[![](https://p1.ssl.qhimg.com/t016bcb5829c859b22b.png)](https://p1.ssl.qhimg.com/t016bcb5829c859b22b.png)

大规模攻击Krebs后，该网站的CDN服务商（即Akamai）不得不撤销为其提供的DDoS防护服务。这样一来，Brian不得不将站点迁移至Project Shield。正如Brian在博客中谈到的那样，这个事件突出表明DDoS攻击已经成为审查个人的一种常见并且廉价的攻击方式。<br>**“IoT僵尸网络的兴起进一步促进了DDoS攻击作为网络审查工具的商品化进程。”**



## 四、OVH攻击事件

[![](https://p0.ssl.qhimg.com/t01a756d959de7a05e9.jpg)](https://p0.ssl.qhimg.com/t01a756d959de7a05e9.jpg)

Brian并不是Mirai的第一个受害者。在Brian被攻击的前几天，Mirai攻击了欧洲最大的托管服务商之一：[OVH](https://en.wikipedia.org/wiki/OVH)。根据[官方统计数据](https://www.ovh.com/us/news/articles/a2367.the-ddos-that-didnt-break-the-camels-vac)，OVH为超过100万个客户的大约1800万个应用提供托管服务，[维基解密（Wikileaks）](https://wikileaks.org/)正是他们最为出名且最有[争议](http://www.datacenterdynamics.com/content-tracks/security-risk/british-spies-monitored-ceo-of-ovh/97461.fullarticle)的一个客户。



对此次攻击我们了解的并不多，因为OVH并没有参与我们的联合研究过程中。因此，我们得到的信息主要来自于OVH在攻击事件后发布的博文。从这篇文章来看，此次攻击持续了大约一周时间，攻击对象为OVH某个未公开的客户，攻击流量巨大且有一定间歇性。

[![](https://p0.ssl.qhimg.com/t0108ef472e404c58b8.jpg)](https://p0.ssl.qhimg.com/t0108ef472e404c58b8.jpg)

作为OVH的创始人，Octave Klaba在[推特](https://twitter.com/olesovhcom/status/778832013503631360)上说这些攻击针对的是Minecraft服务器。根据本文的分析，我们可以在游戏行业利益争夺中广泛看到Mirai的身影，这可能也是为什么Mirai首次现身在这种场景的原因所在。



根据OVH的感应结果，此次攻击峰值流量为1TBs，由145,000个IoT设备共同发起。虽然IoT设备的数量与我们的观测结果一致，但报告中公布的攻击流量明显高于我们在其他攻击事件中看到的数据。比如，前面介绍过，Brian被攻击的峰值流量为623Gbps。

[![](https://p0.ssl.qhimg.com/t01033c5f1b7a0c153b.png)](https://p0.ssl.qhimg.com/t01033c5f1b7a0c153b.png)

无论具体规模有多大，Mirai攻击肯定是有史以来规模最大的攻击活动。之前的“纪录”大约为300Gpbs，Mirai流量已经远远超过这一数值，甚至超过了Arbor Network观察到的最大流量值（Arbor年度报告中认为攻击流量最高可达~800Gbps）。

**“社区应该将Mirai的庞大规模视为警钟：存在漏洞的IoT设备已成攻击主力军，会对互联网稳定性造成重大且迫切的威胁。”**
