> 原文链接: https://www.anquanke.com//post/id/84810 


# 【技术分享】关于mirai僵尸网络控制主机的数据分析


                                阅读量   
                                **145652**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0136c829cc88c4a3e2.png)](https://p5.ssl.qhimg.com/t0136c829cc88c4a3e2.png)

之前的文章中已经提及，我们的僵尸网络跟踪系统对mirai僵尸网络控制主机做了持续跟踪，并且在文章的结尾处，依据跟踪结果排除了僵尸网络操作者位于北京时区的可能。在这篇文章中，我们将进一步分析mirai僵尸网络的控制主机的行为和特征。之前文章链接如下：

[http://blog.netlab.360.com/a-dyn-twitter-ddos-event-report-and-mirai-botnet-review/](http://blog.netlab.360.com/a-dyn-twitter-ddos-event-report-and-mirai-botnet-review/)

目前为止，我们与安全社区合作共享了两位数域名上的超过50个mirai僵尸网络主控。但本文后面的分析仅针对360网络安全研究院独立发现的主控，即13个域名上的16个主控主机名，其中8个在持续对外发起攻击。

在时间线上，我们可以看到各主控随时间变化的注册、在DNS中首次出现、持续保持IP地址变化、首次被监控到发起攻击等事件。地理分布方面，主控的IP地理分布主要在欧洲和美国，尤以欧洲为甚，亚洲很少，这从侧面增强了之前“mirai控制者不在北京时区”的判断。

域名注册信息方面，绝大多数主控在域名注册时在TLD、注册局、注册邮箱方面设置了多重障碍阻滞安全社区的进一步分析。

主控中一个特例是santasbigcandycane.cx，这个域名随着mirai源码泄漏而暴露在大众视野中。KrebsOnSecurity 对这个域名做了深入而有趣的探索。感兴趣的读者可在读完本篇文档后阅读： [https://krebsonsecurity.com/2016/10/spreading-the-ddos-disease-and-selling-the-cure/#more-36538](https://krebsonsecurity.com/2016/10/spreading-the-ddos-disease-and-selling-the-cure/#more-36538)



**所分析的mirai控制端列表**

到目前为止，我们独立发现了16个僵尸网络主机名，分布在13个域名上，如下表所示。出于安全考虑，我们掩去了关键信息。

[![](https://p5.ssl.qhimg.com/t01b71209d9bbfeed19.png)](https://p5.ssl.qhimg.com/t01b71209d9bbfeed19.png)

除了少数两个特例以外，绝大多数主机名所属域名下的所有其他主机名也都完全为 mirai 服务，可据此判定绝大多数域名是专门为了mirai而申请注册的。

特例之一是santasbigcandycane.cx，前文已述；特例之二是 contabo.host ，这个域名属于 Contabo.com，是一家提供低成本虚拟主机和Web空间的网络提供商。合理推测这是一台被攻破的虚拟主机，攻破后被用作mirai的控制端。

注：域名指在注册局注册的域名，主机名指域名所有者获得域名控制权后分配的子域名。

<br>

**mirai主控的时间变化情况**

回溯Mirai控制端的活动历史，可以绘制mirai控制端的活动时间线如下图。考虑到大家主要关注mirai近期活动，我们缩放了下图时间轴，主要显示9月1日至今（10月27日）。

[![](https://p2.ssl.qhimg.com/t0197c49f3422761eba.png)](https://p2.ssl.qhimg.com/t0197c49f3422761eba.png)

图中，四个图标分别表示域名注册、主机名在DNS系统中活跃的时间、主机名在DNS系统中发生IP地址变化、跟踪到该主机名发起攻击。其中最后一个主控，我们无法追踪到最初显示的注册时间，目前查到的注册时间在其DNS首次出现时间之后。

从上图中可以看出域名一旦启用（观察到参与攻击）会快速更换IP地址，一般可以判定这是攻击者在逃避安全社区的分析。以某个被认为发起了针对本次 dyn / twitter 攻击的mirai主控为例，下表是该主控的IP变化历史：

[![](https://p4.ssl.qhimg.com/t011f1d698ccc0a1b5e.png)](https://p4.ssl.qhimg.com/t011f1d698ccc0a1b5e.png)

图中还可以看到我们累积监控到8个主控对外发起攻击。时间可以回溯到2016年10月18日，并一直持续到当前。另外由于mirai僵尸网络规模特别大，单个主控要应对的bot较多（合理推测数目在万级），我们有理由相信mirai主控与bot之间的通讯模型与既往其他僵尸网络都有所不同。

<br>

**mirai主控的IP地理分布**

之前社区里关于这些域名的IP地址变化有一种说法，认为 “某个mirai主控变换IP地址后，原先的IP地址上会出现一个新的域名，仍然是mirai主控”，即不同主控之间共享IP地址。在我们的数据中，上述情况完全没有出现。 前文已经提到这些域名在快速的变换IP，我们持续跟踪的16个主控目前为止一共使用了98个IP地址，其中活跃的8个主控一共使用了57个IP地址。这些IP地址的国家和地区分布如下：

[![](https://p1.ssl.qhimg.com/t012b9dc065458b19d4.png)](https://p1.ssl.qhimg.com/t012b9dc065458b19d4.png)

可以看出绝大部分IP分布在欧洲和北美（巴尔及利亚，加拿大，丹麦，法国，德国，匈牙利，意大利，荷兰，罗马尼亚，俄罗斯，苏伊士，英国，美国），其中又以欧洲为甚，分布在亚洲区的只有3个。这从侧面增强了之前“mirai控制者不在北京时区”的判断。

<br>

**mirai主控的域名注册信息**

Mirai的控制者在域名注册方面非常小心，以避免被跟踪。一方面选择很少见的新Top Level Domain（TLD），另一方面所使用的注册邮箱、注册局也都强调隐私保护或者很难继续追踪。

TLD的分布上，较少用常见的 .net .org 。 .xyz .work这样的TLD就已经少见，而 .racing 这样就 是更加罕见了。全部域名在常见 TLD (.net .org)上只有23%（=3/13），即使加上上.ru也不超过50%，如下图所示： 

[![](https://p3.ssl.qhimg.com/t014b3c3c3a472823a5.png)](https://p3.ssl.qhimg.com/t014b3c3c3a472823a5.png)

注册邮箱和注册局方面情况如下。同样出于安全考虑，我们掩去了关键信息。

[![](https://p3.ssl.qhimg.com/t0121b79f1f09a9a0bc.png)](https://p3.ssl.qhimg.com/t0121b79f1f09a9a0bc.png)

这些注册邮箱都比较难以继续追溯下去：Protonmail 是专门强调数据安全的邮件服务商，reg.ru, r01.ru,whoisguard.com 是专门做域名隐私保护的公司，contabo是VPS提供商，freenom运营了大量免费域名。

特别要提及，info@namecentral.com 这个注册局很特殊，在上文提到的krebsonSecurity 连接中，Krebs提到这个注册局上注册的30+域名中大多含有 boot/stress/dos 这样的字眼，通常这暗示域名从事ddos出租服务；Krebs提到的另一个疑点是这个注册局注册的域名太少，无法做到收支平衡。Krebs与注册局的所有者取得联系，对方对Krebs的疑问有所回答，这更进一步加强了Krebs的疑虑。如果您已经读到这里，我们强烈建议您去阅读此文[[点击此处]](https://krebsonsecurity.com/2016/10/spreading-the-ddos-disease-and-selling-the-cure/#more-36538)。


