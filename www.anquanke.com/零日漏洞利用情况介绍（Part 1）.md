> 原文链接: https://www.anquanke.com//post/id/202662 


# 零日漏洞利用情况介绍（Part 1）


                                阅读量   
                                **506754**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者fireeye，文章来源：fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2020/04/zero-day-exploitation-demonstrates-access-to-money-not-skill.html](https://www.fireeye.com/blog/threat-research/2020/04/zero-day-exploitation-demonstrates-access-to-money-not-skill.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01fdd09fe0363e0cfe.jpg)](https://p0.ssl.qhimg.com/t01fdd09fe0363e0cfe.jpg)

## 零日漏洞利用情况介绍（Part 1）

## 0x00 前言

在关键战略及战术方面，网络威胁情报（CTI）扮演的一个角色就是跟踪、分析以及确认软件漏洞的等级，这些漏洞可能会给组织、员工以及客户的数据带来安全风险。[FireEye Mandiant Threat Intelligence](https://www.fireeye.com/solutions/cyber-threat-intelligence.html)撰写了4篇文章，介绍了CTI在漏洞管理方面的重要性，也提供了关于最新威胁、趋势以及安全建议方面的相关信息。

根据研究结果，与前3年相比，我们发现2019年被利用的零日（0-day）漏洞数量更多。虽然并非每次0-day利用都能溯源到特定的攻击组织，但我们发现越来越多的攻击组织已经逐步具备这类能力。此外，有些攻击组织会购买商业公司提供的进攻性网络产品及服务，所利用的0-day数量也越来越多，并且随着时间的推移，针对中东的0-day攻击事件也越来越多。现在有许多组织/个人在提供攻击性网络武器服务，展望未来，我们认为会有更多攻击者开始使用0-day。



## 0x01 0-day利用情况

现在有许多私营企业会提供攻击性网络工具及服务，我们发现（或者怀疑）有一些组织是这些企业的客户。从2017年年底以来，FireEye Mandiant Threat Intelligence注意到这类组织所使用的0-day数量大幅提升。此外我们也观察到，针对中东地区或者与该地区有关的组织所使用的0-day数量也越来越多。

[![](https://p1.ssl.qhimg.com/t0116ab982b46cddccf.png)](https://p1.ssl.qhimg.com/t0116ab982b46cddccf.png)

比如：

1、研究人员[Stealth Falcon](https://citizenlab.ca/2016/05/stealth-falcon/)及[FruityArmor](https://www.securityweek.com/windows-zero-day-exploited-fruityarmor-sandcat-threat-groups)曾公开过代号为“[Stealth Falcon](https://citizenlab.ca/2016/05/stealth-falcon/)”的一个组织，该间谍组织主要针对的是[中东地区](https://www.welivesecurity.com/2019/09/09/backdoor-stealth-falcon-group/)的记者以及活动人士。2016年，该组织使用了由NSO提供的恶意软件，其中利用到了3个iOS 0-day漏洞。在2016年到2019年期间，该组织与其他组织相比所使用的0-day数量更多。

2、许多公开源曾提到过SandCat组织，该组织可能与[乌克兰国家情报机构](https://www.vice.com/en_us/article/3kx5y3/uzbekistan-hacking-operations-uncovered-due-to-spectacularly-bad-opsec)有关，并且在针对中东的攻击活动中也使用了0-day。由于SandCat所使用的0-day同样也被Stealth Falcon所使用，考虑到完全相同的3个0-day被独立发现的可能性比较低，因此该组织可能也是从私营企业（比如以色列软件公司NSO）手中购买了0-day技术。

3、2016年到2017年期间，公开源情报曾报道过[BlackOasis](https://www.securityweek.com/middle-east-group-uses-flash-zero-day-deliver-spyware)组织，该组织主要针对的是中东区域，很有可能曾经从私营企业[Gamma Group](https://www.cyberscoop.com/middle-eastern-hacking-group-using-finfisher-malware-conduct-international-espionage/)手中购买了至少一个0-day。研究表明该组织同样频繁使用过0-day漏洞。

此外我们还注意到，虽然有些0-day利用行为还未溯源到特定攻击组织，但我们可以在私营安全企业提供的某些攻击性工具中看到这些0-day，比如：

1、2019年，有[报道](https://www.itpro.co.uk/spyware/33632/whatsapp-call-hack-installs-spyware-on-users-phones)称攻击者使用了WhatsApp中的一个0-day（CVE-2019-3568）来传播NSO组织开发的间谍软件。

2、FireEye分析了针对俄罗斯医疗保健组织的一次攻击活动，攻击者使用了2018年曝光的Adobe Flash 0-day（CVE-2018-15982），该漏洞可能与Hacking Team泄露的源码有关。

3、2019年10月，有报道称攻击者利用了NSO组织提供的工具，其中涉及到Android平台的一个0-day（CVE-2019-2215）。



### <a class="reference-link" name="%E5%9B%BD%E5%AE%B6%E7%BA%A7%E5%88%AB%E7%BB%84%E7%BB%87"></a>国家级别组织

在0-day利用中，我们不能忽视国家级别的攻击组织，比如：

1、根据研究报道，APT3曾在[2016年](https://www.symantec.com/blogs/threat-intelligence/buckeye-windows-zero-day-exploit)利用CVE-2019-0703开展针对性攻击活动。

2、FireEye观察到APT37曾在2017年利用Adobe Flash漏洞（CVE-2018-4878）开展攻击活动，该组织与朝鲜方面有关。APT37能够在该漏洞被曝光后迅速改造并利用，这表明该组织的漏洞利用能力不断增强。

3、从2017年12月到2018年1月，我们观察到有多个攻击组织曾利用CVE-2018-0802来攻击欧洲、俄罗斯、东南亚以及台湾的目标。在漏洞补丁发布前，捕捉到的6个样本中至少有3个样本使用到了该漏洞。

4、2017年，俄罗斯攻击组织APT28及Turla利用了微软Office产品中的多个[漏洞](https://www.fireeye.com/blog/threat-research/2017/05/eps-processing-zero-days.html)。

此外我们认为，国家级别的攻击组织在公开漏洞利用方面的能力越来越强。在许多情况下，与这些国家有关的组织已经能够武器化漏洞，将这些漏洞纳入攻击活动中，充分利用漏洞漏洞公开与补丁发布间的窗口期。



### <a class="reference-link" name="%E5%88%A9%E7%9B%8A%E9%A9%B1%E5%8A%A8%E7%BB%84%E7%BB%87"></a>利益驱动组织

受利益驱动的攻击组织也在持续[利用0-day](https://www.fireeye.com/blog/threat-research/2016/05/windows-zero-day-payment-cards.html)，但频率上没有间谍组织那么高。

2019年5月，我们报道过FIN6曾在2019年2月使用Windows Server 2019系统的一个UAF（释放后重用）漏洞（CVE-2019-0859）来开展针对性攻击行为。根据收集到一些证据，我们发现该组织可能从2018年8月起已经开始利用该漏洞。虽然有公开源情报称该组织可能从代号为[BuggiCorp](https://www.ibtimes.com/hacker-selling-windows-zero-days-worlds-most-dangerous-hacker-groups-2789374)的地下组织手中购买了该漏洞，但我们仍然没有找到直接证据，能够将该攻击者与这个漏洞开发或销售组织关联起来。



## 0x02 总结

根据私营企业潜在客户对0-day的利用情况及比例，我们推测现在攻击者对0-day的利用趋势已经越来越商品化。之所以会出现这种情况，可能有如下原因：

1、与过去相比，私营企业对0-day的挖掘及服务提供能力可能更强，这将导致0-day资源被逐渐集中到实力强劲的组织手中。

2、私营企业可能逐渐向整体实力较差的组织以及（或者）对操作安全性关注较少的组织提供攻击性服务，这也将导致0-day利用活动越来越频繁。

国家级别的组织内部可能会继续在漏洞挖掘及研发方面投入精力，然而，相对单纯依赖国内解决方案或者地下市场，使用私营企业提供的0-day服务可能更具吸引力。因此我们认为，如果攻击者有能力且愿意投入金钱，那么能够获取这类漏洞的攻击者数量将不断上升，并且增长速度将比其自身的整体网络攻击能力增长速度要快。
