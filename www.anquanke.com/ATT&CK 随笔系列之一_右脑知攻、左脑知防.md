> 原文链接: https://www.anquanke.com//post/id/187485 


# ATT&amp;CK 随笔系列之一：右脑知攻、左脑知防


                                阅读量   
                                **615344**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t014c770637f864ae6e.png)](https://p3.ssl.qhimg.com/t014c770637f864ae6e.png)作者：余凯@瀚思科技副总裁

2019 年相当不太平，除了全球贸易战，安全行业也暗潮涌动。上月底，Gartner WEB 应用防火墙 (WAF) 魔力象限领导者 之一某企业a 承认遭到黑客入侵【1】，该企业 一直宣称其核心能力和使命是保护客户的应用和数据安全，入侵事件的发生貌似尴尬。然而今年 5 月，国外主流媒体报道【2】全球排名前三安全厂商悉数被黑客组织 Fxmsp 攻破，源代码遭到泄漏。时间线向前回溯，谷歌 2018 年因为数据泄漏终止 Google+ 服务【3】，微软于 2017 年承认 Windows 10 源代码泄漏【4】，卡巴斯基 2015 年主动披露内部网络被以色列黑客攻陷【5】。新闻追踪至此，大家可以停止笑话 该企业 了，问题远比想象严重，而且没有人可以袖手旁观。



## 黑铁时代：人与人间的攻防对抗



## 青铜时代：聚焦黑客行为的产品改进

2）真正有效的检测是基于黑客攻击的一系列手法，包括如何与目标系统的互动，这些手法有些是黑客人工试探，有些通过工具自动化完成的。一个类似的比喻是，交警通过摄像头抓取违章是不会主要依赖车牌或者车型。

3）攻击手法不容易改变，正如违章行为相对固定。基于 IoC 的防御是必要的基础能力，但层次越低，效率越低。

4）基于 IoC 或类似特征码的防御性安全设备，因为必须阻断，常常成为黑客试探和绕过的验证工具。同时黑客攻击越来越倾向于以零日攻击和社会工程学开始，以合法帐号和通用工具，甚至系统工具实施。这意味着，阻断类安全产品对抗黑客攻击是不够的，需要有提供嗅探、监测、关联、分析和溯源的旁路型安全产品互补。

[![](https://p0.ssl.qhimg.com/dm/1024_674_/t0153f8fc5bb8437da6.jpg)](https://p0.ssl.qhimg.com/dm/1024_674_/t0153f8fc5bb8437da6.jpg)

以上共识达成，各家安全厂商便各自开始努力，聚焦黑客行为 (TTP) 提升检测能力。例如今年成功上市如日中天的 CrowdStrike 在 2014 年提出了 IoA 【13】(Indicator of Attack)，而我当时服务的公司也提出了 EIoC 对 IoC 做扩充，一批自用的检测恶意行为的经验性规则被提出以 IoA（或其他形式，例如 EIoC）方式描述，并在各自的安全产品中尝试实现。时间给了我们上帝视角，回想当年在公司激烈的讨论，有关 IoA 和 EIoC 的潜力对比，有关如何形成规则，有关如何验证，如今结论都不言自明，水落石出，这些尝试在后续几年的实践中都遭遇到了重大瓶颈，或者步履维艰，甚至停滞不前。

重大瓶颈产生的根本是所有的努力都缺乏一个重要的基础：描述黑客行为 (TTP) 的语言和词库。这一点是高级威胁攻击的独特性决定的：

1）高级威胁攻击自 2013 年起被公开披露，当年只有包括 FireEye，Trend Micro，Kaspersky 等少数安全公司能看到，随着公众重视，国际头部安全公司投入，更多公司也开始加入其中报道。但始终因为事件高度敏感，导致威胁情报无法交换，众多安全公司面对黑客组织全貌如同盲人摸象。

2）即便是在安全公司内部，因为没有一个很好的描述语言和词库，即便是最好的安全人员发现了 APT 事件也无法一致的、直观的将黑客手法完整的描述出来，再提供给核心技术和产品研发去做系统性对抗实现。导致最后产品仍然是基于 IoC 检测，即便是为行为检测而设计的 IoA 等描述也最后落入了各种威胁码的窠臼。

3）黑客行为与正常用户行为往往很难界定，但又有大量交集。安全产品缺乏记录中性行为 (telemetry) 的能力，导致黑客入侵难以发现，这一点是开篇提到代表行业安全能力上限的安全公司集体失陷的直接原因。



## 白银时代：统一语言，重装上阵



## 向黄金时代进军：右脑知攻、左脑知防



## 作者简介

目前就职于瀚思科技担任副总裁，在安全技术、产品、市场具备近 20 年丰富经验，拥有 3 项美国专利。致力于引入世界一流的攻防实践和技术创新将瀚思的核心技术进行国际化升级。他曾在全球最大的独立安全软件厂商趋势科技领导高级威胁攻防核心技术团队，负责零日漏洞研究、攻击检测沙箱、漏洞检测和过滤引擎等多个核心技术产品研发成绩斐然，曾获得公司最具价值员工（2012年度）和领袖（2015年度）奖杯，2015 年荣获 CEO 和 CIO 共同署名颁发的年度优秀团队奖杯。



## 参考文献

[5] The Mystery of Duqu 2.0: a sophisticated cyberespionage actor returns

[https://securelist.com/the-mystery-of-duqu-2-0-a-sophisticated-cyberespionage-actor-returns/70504/](https://securelist.com/the-mystery-of-duqu-2-0-a-sophisticated-cyberespionage-actor-returns/70504/)

[6] Defensible Security Architecture

[https://dfs.se/wp-content/uploads/2019/05/Mattias-Almeflo-Nixu-Defensible.Security.Architecture.pdf](https://dfs.se/wp-content/uploads/2019/05/Mattias-Almeflo-Nixu-Defensible.Security.Architecture.pdf)

[7] NSS LABS ANNOUNCES ANALYST COVERAGE AND NEW GROUP TEST FOR BREACH DETECTION SYSTEMS

[https://www.nsslabs.com/press/2012/11/8/nss-labs-announces-analyst-coverage-and-new-group-test-for-breach-detection-systems/](https://www.nsslabs.com/press/2012/11/8/nss-labs-announces-analyst-coverage-and-new-group-test-for-breach-detection-systems/)

[8] More Details on “Operation Aurora”

[https://securingtomorrow.mcafee.com/other-blogs/mcafee-labs/more-details-on-operation-aurora/](https://securingtomorrow.mcafee.com/other-blogs/mcafee-labs/more-details-on-operation-aurora/)

[9] GandCrab Ransomware Shutting Down After Claiming to Earn $2 Billion

[https://www.bleepingcomputer.com/news/security/gandcrab-ransomware-shutting-down-after-claiming-to-earn-2-billion/](https://www.bleepingcomputer.com/news/security/gandcrab-ransomware-shutting-down-after-claiming-to-earn-2-billion/)

[10] PLANS TO INFECT ‘MILLIONS’ OF COMPUTERS WITH MALWARE

[https://theintercept.com/2014/03/12/nsa-plans-infect-millions-computers-malware/](https://theintercept.com/2014/03/12/nsa-plans-infect-millions-computers-malware/)

[11] What’s in a name? TTPs in Info Sec

[https://posts.specterops.io/whats-in-a-name-ttps-in-info-sec-14f24480ddcc](https://posts.specterops.io/whats-in-a-name-ttps-in-info-sec-14f24480ddcc)

[12] The Pyramid of Pain

[https://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html](https://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html)

[13] IOC Security: Indicators of Attack vs. Indicators of Compromise

[https://www.crowdstrike.com/blog/indicators-attack-vs-indicators-compromise/](https://www.crowdstrike.com/blog/indicators-attack-vs-indicators-compromise/)
