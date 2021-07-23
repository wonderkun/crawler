> 原文链接: https://www.anquanke.com//post/id/215312 


# 美国网络安全 | MITRE Shield 积极防御知识库


                                阅读量   
                                **176590**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t016a354e51ef29ede2.png)](https://p2.ssl.qhimg.com/t016a354e51ef29ede2.png)



转载： [网络安全观 ](https://mp.weixin.qq.com/s/cljI9AFVNEb4YkglzYayDg)

提到MITRE，安全人员最先想到的可能是引领全球网络安全攻防潮流的对手战术和技术知识库框架ATT&amp;CK。ATT&amp;CK知识库被用作私营部门、政府、网络安全产品和服务社区开发特定威胁模型和方法的基础。而本文要介绍的MITRE Shield，则是一个MITRE正在开发的积极防御知识库，用于捕获和组织关于积极防御和对手交战的知识，旨在为防御者提供用于对抗网络对手的工具。Shield知识库描述了积极防御、网络欺骗、对手交战行动中的一些基本活动，可用于私营部门、政府、网络安全产品和服务社区的防御性利益。MITRE特别强调了Shield与ATT&amp;CK的联系，认为从ATT&amp;CK到Shield是一个自然而然的过程，认为同时使用ATT&amp;CK和Shield可以帮助防御者有效增强防御能力。MITRE Shield创建于2019年，是一个非常新的知识库，目前只是Shield知识库的第一个版本。MITRE表示，Shield的下一个版本将有改进的结构和更多的内容。2020年8月，MITRE发布了《MITRE Shield 介绍》。笔者获悉后，第一时间整理此文，以引起业内重视。笔者愿意相信：Shield积极防御知识库将成为网络安全行业重要的发展方向之一，将成为各组织机构实施积极防御的指导框架和重要资源。笔者在整理本文过程中，主要参考了Shield网站和《MITRE Shield 介绍》的内容：
- Shield网站地址：[http://shield.mitre.org](http://shield.mitre.org)；
<li>《MITRE Shield 介绍》下载地址：[https://shield.mitre.org/resources/downloads/Introduction_to_MITRE_Shield.pdf](https://shield.mitre.org/resources/downloads/Introduction_to_MITRE_Shield.pdf)
</li>
关键词：MITRE；Shield（护盾、盾牌、防护）；对手交战（adversary engagement）；积极防御（active defense）；战术（Tactics）；技术（Techniques）；过程（Procedures）；机会空间（Opportunity Space）；用例（Use Cases）；注：这些关键词在本文中频繁出现，对于理解Shield积极防御知识库非常必要，务必熟悉之。



## 一、Shield背景介绍

### Shield简介

Shield积极防御知识库由MITRE的交战团队（engagement team）于2019年创建，用于改进作战行动计划。2020年8月，MITRE发布了《MITRE Shield 介绍》，封面如下：

[![](https://p3.ssl.qhimg.com/t0131a328a4070e2b3b.png)](https://p3.ssl.qhimg.com/t0131a328a4070e2b3b.png)

图1-《MITRE Shield 介绍》的封面

Shield包括防御者可以用于开展积极防御的技术的数据库，还描述了防御计划中常见的一些战术，然后将战术映射到可能有助于实现这些目标的活动。该知识库包括一个MITRE ATT&amp;CK和Shield 技术之间的映射，以说明对手战术、技术和过程（TTP）引入的防御可能性。目前Shield知识库的第一个版本，侧重于基本的安全技术，因为这些是建立良好的欺骗和对手交战的基石。MITRE认为在积极防御空间中有太多可能的活动无法列举完整，因此Shield是不完整的。尽管如此，Shield对于那些寻求理解或实施积极防御的组织来说，是一个很好的资源，并且可以促进整个防御社区的讨论和技术交流。

### 为何创建Shield

1）创造Shield的动机是什么？这个项目源于MITRE团队记录了在对手交战行动中可能有用的技术。MITRE在网络欺骗和对手交战方面有着丰富的工作历史，因此对于团队来说，创建这个知识库也成为一个自然而然的过程。2）为什么知识库命名为Shield？Shield既是动词，意思是防御危险或风险；也是名词，意思是保护或防御。就像这个词一样，MITRE的Shield知识库可以根据防守者的具体需要，以多种方式使用。

### Shield术语

Shield的目标之一是使用足够的结构和严格性，而又不必过于僵化或复杂。MITRE从《国防部军事及相关术语词典》以及《美国政府跨机构及相关术语汇编》中找到的术语开始：
- 积极防御（Active Defense）：利用受限的进攻性行动和反击，来拒止对手进入一个有争议的地区或位置。
- 战略（Strategy）：以同步和集成的方式运用国家力量手段实现战区、国家和/或多国目标的审慎想法或想法集。
- 战术（Tactics）：在考虑相互关系的情况下对兵力的运用和有序安排。
- 技术（Techniques）：用于执行使命、功能、任务的非规定性的方式或方法。
- 过程（Procedures）：规定如何执行特定任务的标准的详细步骤。
为适合网络积极防御领域，MITRE修改了这些术语。MITRE的定义如下：
- 战术：是抽象的防御者的目的。MITRE发现，有一个能够描述知识库中其他各种元素的效用或用途的分类系统，是很有用的。例如，“引导”战术可以与特定的技术、计划的技术集的一部分，甚至是整个长期交战战略的一部分相关联。
- 技术：是防御者可以执行的一般行动（actions ）。一个技术可能有几种不同的战术效果，这取决于它们是如何实现的。
- 过程：是一个技术的实现。在这个版本中，只包含一些简单的过程来激发更多的思考。其目的不是提倡特定的产品、解决方案或结果，而是促使组织广泛考虑现存的选择。Shield中包含的数据集，必然是不完整的，因为存在太多可能的变化，无法可靠地记录。
MITRE还添加了一些新术语：
- 机会空间（Opportunity Spaces）：描述当攻击者运用他们的技术时引入的高级别积极防御可能性。
- 用例（Use Cases）：是对防御者如何利用攻击者的行为所呈现的机会（opportunity ）的高级别描述。用例有助于进行特定的实现讨论。注意：在知识库的下一个版本中，可以看到用例的自然演化正在发挥作用。
### 何谓积极防御

美国国防部将积极防御定义为“利用受限的进攻性行动和反击，以拒止敌手进入有争议的地区或阵地。”积极防御的范围从基本的网络防御能力到网络欺骗和对手交战行动。这些防御措施的组合，使一个组织不仅能够抵制当前的攻击，而且能够更多地了解对手，更好地为将来的新攻击做好准备。1）通用网络防御（General Cyber Defense）Shield包括了MITRE认为适用于所有防御计划的基本防御技术。要想在欺骗和对手交战中取得成功，必须使用基本的网络防御技术，如收集系统和网络日志、PCAP、执行数据备份等。尤其是当通过对组织所面临的威胁进行评估并确定其优先级时，许多Shield技术可在企业网络中应用，特别是用于检测和阻止对手。所以，虽然Shield似乎面向欺骗和对手交战，但也包括了基本的防御技术。2）网络欺骗（Cyber Deception）有越来越多的想法、工具和产品使用“绊索”（tripwire）方法来进行网络防御，这被广泛地称为“欺骗”。与通用网络防御中的强化和检测活动相比，欺骗更加主动，防御者会故意引入目标和“面包屑”（目标位置的线索）。精心构建的欺骗系统，通常难以与真实生产系统区分开来，可以用作高保真的检测系统。Shield的技术可以包括检测、威慑或其他预期效果的欺骗。3）对手交战（Adversary Engagement）Shield中的许多技术都是为防御者设计的，他们想观察、收集和理解对手针对防御系统的活动。可部署在生产环境或综合环境中，Shield对手交战技术可促进有效、高效的交战。Shield知识库可用于分析已知的对手信息（在ATT&amp;CK的帮助下）、计划防御措施、获取对未来有用的知识。



## 二、Shield矩阵模型

### 战术和技术的关系

Shield模型主要由技术和战术构成。战术和技术之间的关系，可以用矩阵来说明。矩阵包括：
- 战术：表示防御者试图完成的任务（列）；
- 技术：描述防御如何实现战术（单个单元格）；
关于技术和战术的关系，可以打个比方：战术比作容器（containers），技术比作积木（building blocks）。每个容器（战术）都装着积木（技术）。防御者运用Shield的方法是：防御者可以浏览知识库中提供的战术（容器），并选择最适合积极防御需求的战术（如收集（collection））。然后防御者可以查看在该战术目标中分组的技术（积木），并选择允许他们构建最佳积极防御解决方案的技术。Shield网站有一个矩阵视图，它提供了对积极防御战术和技术的快速可视化描述。

[![](https://p0.ssl.qhimg.com/t017dbce9c7de3a33b7.png)](https://p0.ssl.qhimg.com/t017dbce9c7de3a33b7.png)

图2-Shield积极防御矩阵

战术和技术之间的关系可以是多对多的，一种技术可以支持多种不同的战术，任何战术都有多种技术可以使用。例如，可以加强安全控制以干扰对手的活动，也可以放松安全控制以促进进一步的交战。在实际行动（operation）中，一个单独的行动（action）或技术可以同时支撑多个战术，而完成一个战术可能需要多种技术。

### 积极防御的战术

[![](https://p1.ssl.qhimg.com/t01622a39724cea70f0.png)](https://p1.ssl.qhimg.com/t01622a39724cea70f0.png)

表3-积极防御的战术

由上图可知，积极防御的战术的数量并不多，目前就8个。点击ID列的任何一个，比如第一个DTA0001，则进入了“引导（Channel）”战术的页面：

[![](https://p3.ssl.qhimg.com/t01c6adc3ef80b14547.png)](https://p3.ssl.qhimg.com/t01c6adc3ef80b14547.png)

图4-引导（Channel）战术包含的技术

上表中第1列所引用的技术，均来自后文的表5。如果点击上表中第1列的特定技术，比如第一个DTE0001-Admin Access（管理员访问）技术，则会访问到该项具体技术的页面，即下一节的表6~表10。

### 积极防御的技术

技术描述了防御者在积极防御中可以做的事情。防御者通过执行一个或多个行动（actions），来达到战术目标。例如，防御者可以在对手交战系统上播种诱饵凭证，以查看对手是否将凭证转储并使用它们来访问交战网络中的其他系统。

Shield技术从基本到高级都有：
- 基础技术：如备份和恢复、网络监控、系统活动监视，可以在许多组织中广泛应用。这些技术作为组织的积极防御组合的一部分是必要的。
- 高级技术：类似操纵网络和软件的高级技术，可能只对那些寻求在更深层次研究对手或与对手交战的欺骗型供应商和组织有用。
Shield的所有技术如下表所示：

[![](https://p1.ssl.qhimg.com/t0183f805df59dc62a8.png)](https://p1.ssl.qhimg.com/t0183f805df59dc62a8.png)

表5-积极防御的技术

有上表可见，积极防御的技术目前总共有34项。

如果点击第1列中的具体技术，则可以访问技术的详细信息页面，该页面提供了多个表格信息：
- 该技术支持的战术；
- 基于对手TTP的可用机会；
- 用于促进实施讨论的用例；
- 用于促进实施讨论的过程。过程是技术的实现的高级别描述；
- 与该技术相关的ATT&amp;CK技术；
笔者以第一项技术为例，即管理员访问（Admin Access）。

该技术的支持的战术如下：

[![](https://p1.ssl.qhimg.com/t016b62881f15d885bb.png)](https://p1.ssl.qhimg.com/t016b62881f15d885bb.png)

表6-技术支持的战术

该技术的可用机会如下：

[![](https://p5.ssl.qhimg.com/t01496bf7cec641d790.png)](https://p5.ssl.qhimg.com/t01496bf7cec641d790.png)

表7-机会（Opportunities）

该技术的用例如下：

[![](https://p3.ssl.qhimg.com/t01aa3d2e3da45a269f.png)](https://p3.ssl.qhimg.com/t01aa3d2e3da45a269f.png)

表8-用例（Use Cases）

该技术的过程如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d1e53d3d53fcd069.png)

表9-过程（Procedures）

该技术相关的ATT&amp;CK技术如下：

[![](https://p1.ssl.qhimg.com/t0199d1fc5f87ea5651.png)](https://p1.ssl.qhimg.com/t0199d1fc5f87ea5651.png)

表10-ATT&amp;CK技术

点击上图中ID列中的T1014链接，则可以打开ATT&amp;CK的Rootkit技术的页面。

点击上图中ATT&amp;CK战术列中的Defense Evasion（防御规避）链接，则可以打开到Defense Evasion（防御规避）战术的映射页面，参见后文的表13。



## 三、Shield与ATT&amp;CK的映射

在MITRE ATT&amp;CK中发现的对手行动，经常能为防御者提供反制的机会。所以，MITRE把Shield的技术映射到MITRE ATT&amp;CK上，使其能够制定计划以利用这些机会为防御者创造优势。Shield的ATT&amp;CK映射部分，包含了ATT&amp;CK框架中的对手战术列表。如下所示：

[![](https://p3.ssl.qhimg.com/t014a6f916a61a0abb8.png)](https://p3.ssl.qhimg.com/t014a6f916a61a0abb8.png)

表11-ATT&amp;CK战术映射

通过对比上表与下图（ATT&amp;CK 矩阵）的第一行列标题可知，上面列出的12项ATT&amp;CK战术与ATT&amp;CK矩阵是严格对应的。

[![](https://p4.ssl.qhimg.com/t0103245e20f898941a.png)](https://p4.ssl.qhimg.com/t0103245e20f898941a.png)

图12-MITRE ATT&amp;CK 矩阵-企业版

进一步，每个ATT&amp;CK战术都有一个详细映射页面，列出了结合ATT&amp;CK和Shield的信息：
- 来自ATT&amp;CK：与该战术相关的对手技术；
- 来自Shield：针对对手技术的适用的积极防御信息，包括呈现的机会空间、要实施的积极防御技术、该实施的用例。
关于机会空间：详细信息页面上显示的信息，旨在说明积极防御应对ATT&amp;CK技术的可能性。在ATT&amp;CK映射表的机会空间列中，描述了对手技术呈现的高级别可能性。许多对手技术呈现出不止一个机会，多个机会在表格中各占一行。关于用例：用例是对防御者如何运用列出的积极防御技术来利用所呈现的机会的适度详细的描述。许多列出的机会允许使用基本的积极防御技术，来检测和破坏企业网络中的对手。而其他列出的机会表明了更具交战性的积极防御，这些机会可能会邀请管理层讨论如何在组织的网络防御组合中添加积极防御和对手交战技术。每个ATT&amp;CK战术的详细映射页面（本例为Defense Evasion），展示了4方面信息：
- ATT&amp;CK技术：该战术所使用的对手技术，包含ATT&amp;CK技术的ID和名称；
- 机会空间：当攻击者运用其技术时，引入的高层级积极防御的可能性或机会；
- AD技术（积极防御技术）：可应用的特定的积极防御技术；
- 用例：可能应用的用例，是对防御者如何利用对手行动所呈现的机会的高层级描述。
点击表10中ATT&amp;CK战术列中的“TA0005-防御规避”战术的链接，就可以访问“防御规避”战术的详细映射表（如下表所示）。而上面列出的4个方面，恰恰是下表的4列的标题名称：

[![](https://p2.ssl.qhimg.com/t0169e8288b262a2e9c.png)](https://p2.ssl.qhimg.com/t0169e8288b262a2e9c.png)

表13-到ATT&amp;CK“防御规避”战术的详细映射（截图不全）

进一步，点击ATT&amp;CK技术列（第1列）中的链接，可以访问ATT&amp;CK网站的特定技术；点击AD技术列（第3列）中的链接，可以访问Shield网站的特定技术。

需要强调的是，MITRE认为同时使用ATT&amp;CK和Shield，可以帮助防御者加深对对手行为和交战的理解，并建议防御者可以采取更加主动的防御方式。



## 四、小结与展望

1）小结MITRE Shield是一个知识库，为防御者提供用来对付网络对手的工具。MITRE的目标是防御者能够利用Shield中包含的战术和技术，来更好地创建、使用、操作他们的积极防御解决方案。MITRE也希望通过展示Shield的防御侧如何与MITRE ATT&amp;CK保持一致，可以帮助组织利用这两种解决方案，来最大限度地提高他们的防御能力。

2）未来设想MITRE团队设想对当前数据模型进行改进，以适应更加复杂的积极防御解决方案。这将允许MITRE组合多种技术和过程，来创建复杂的剧本。利用ATT&amp;CK的分组信息，有可能创建适用于特定对手的积极防御剧本。
