> 原文链接: https://www.anquanke.com//post/id/198127 


# 痛中思痛：大安全时代EOC与SOC酝酿变法


                                阅读量   
                                **879706**
                            
                        |
                        
                                                                                    



面对新冠肺炎的巨大危机，迄今为止拥有绝对流量、话语权和数据规模的互联网和2C科技企业似乎并未（能）充分发挥价值。事实表明，面对紧急公共安全事件，靠2C流量、影响力、自组织、自媒体和大数据是远远不够的，高效的公共安全事件管理，离不开风险治理轴心——高效的数字化应急响应中心体系。

[![](https://p0.ssl.qhimg.com/dm/1024_499_/t01c668fcca50a28799.jpg)](https://p0.ssl.qhimg.com/dm/1024_499_/t01c668fcca50a28799.jpg)



## 急控失能

作为安全媒体，安全牛之前报道过企业安全运维中心 “SOC已经进入疲劳期和更年期，亟需变革”，SOC的失能不仅意味着大笔网络安全投资的失效，而且在“黑天鹅“事件中会让企业蒙受巨大的经济损失。与WannaCry病毒让全球大量SOC颜面扫地类似，新型肺炎也暴露了公众应急响应和指挥系统存在的一些问题。

在新型肺炎开始爆发之前，公共安全领域的焦点是澳洲大火，吃瓜群众最津津乐道的就是澳洲政府在澳洲大火应急响应和指挥中表现出的各种低效率、误判和官僚。然而谁也没想到一场肺炎成了试金石，我们的表现，似乎比澳洲更糟糕：疫情瞒报迟报、信息孤岛、物资供应紊乱、信息不对称、公众和企业获取的可行动疫情信息缺乏一致性和准确性、跨部门协同迟滞、社会经济很多领域难以获取与疫情相关的实时准确的可行动协同信息…

过去一年中，安全圈最热的话题莫过于从被动的合规驱动到主动的能力驱动，而所谓能力驱动，说白了就是提高安全工具和安全管理（在风险管理的大框架下）的有效性，例如应对“护网行动”、突发重大“灰犀牛”“黑天鹅”这样的真刀真枪的事件时，SOC（含CSIRT）安全运营中心的响应和处置能力。而面向公共安全和灾难救援的EOC（应急管理控制中心），也面临几乎同样的问题。

举个例子：

当下的疫情中，除了各互联网公司千篇一律的疫情地图外（承载的功能和信息非常有限），公众甚至有关管理部门都没有一个肉眼可见的、与跨部门灾难应急综合协调指挥系统（MACC）直联的数据分析和分享渠道，尽管类似EOC（应急响应中心）、DOC（部门级运营中心）和MOC（包含CDC疾控中心）在多部门多级别政府机构中存在，但是显然，这些系统与MACC（或者上级疾控中心）没有形成有效协同，也并未发挥预期的效力。此次新型冠状病毒疫情中，2003年SARS之后国家重金打造的四级疾控中心体系和覆盖全国直达乡镇卫生院的传染病与突发公共卫生事件监测信息系统（简称网络直报系统）并未发挥出预期的作用。

基于web技术的开放式EOC跨平台多终端信息共享模式

建议

1. 决策者应基于长期、前瞻和全面的策略来建设和完善EOC和SOC，提高运营效率并支持新的业务目标。

2. 大型组织应该意识到，安全分析和运营管理的本质是大数据应用，这要求EOC和SOC的安全团队具备相当的数据管理技能，能够大规模构建和运营安全数据管道。

3. EOC和SOC需要进行云迁移，构建能够跨IT架构的预防、检测和响应平台。

4. 开发和维护高效EOC的关键是供应商管理。

5. EOC建设需要关注拥有丰富SOC系统和行业经验的供应商。

## 高效EOC与SOC的相同之处
- 主动化（感知预测）
- 可视化（决策支持）
- 实时化（检测响应）
- 自动化（缓解措施）


## 主动化的关键：大数据和AI驱动的态势感知（Situation Awareness）

对于SOC来说，态势感知的“感”可以是内部和外部威胁情报（例如IoC），端点安全、防火墙、流量分析、用户行为分析等工具产生的日志、告警等有价值数据，“知”则强调数据处理深度和可行动分析结果。对于重大公共安全事件，政府需要一个最高等级的MACC（跨部门联合指挥中心），关联协调多个部门多级政府的EOC、DOC、MOC分支，协同作战，最高指挥决策必须根据中央仪表盘进行基于态势感知的、数据驱动的高效决策，这就对下一代EOC和SOC提出的共同核心诉求。

在本次新冠肺炎疫情中，“态势感知”的重要性得以凸显。据奇安信官方微信透露，春节期间，为更好控制新型冠状病毒疫情的传播速度，某部委及全国多个省市的下属机关作为此次疫情防控的重要支撑单位，第一时间向奇安信集团发出数据分析技术的请求，希望利用大数据技术分析辖区内的疫情扩散情况，为精准防控提供数据支撑。

相比其他领域的IT企业，网络安全企业在威胁“态势感知”和“基于大数据分析的事件响应”方面，在技术堆栈和产品经验有着明显的优势。例如2017年在全球范围爆发，导致至少150个国家、30万名用户中招，造成损失达80亿美元的“WannaCry勒索病毒”（下图），比新冠病毒传播速度快得多的。

[![](https://p3.ssl.qhimg.com/t014052d164b5d813df.jpg)](https://p3.ssl.qhimg.com/t014052d164b5d813df.jpg)

网络安全行业“养兵千日”积蓄的能力和价值，就是为了应对网络空间“超级病毒”的爆发，而这种战斗力，也完全可以转换用于对抗现实中的疫情，这也是为什么疾控管理部门会第一时间求助网络安全企业的原因。

除了事后的监测和应急响应，大数据和人工智能未来还将在事件预测方面发挥重大作用。

下图是加拿大人工智能公司Bluedot的人工智能疫情监控产品，该公司使用自然语言处理和机器学习技术，通过全球的新闻报道、航空数据以及动物疾病爆发的报告进行筛选。流行病学家可以查看自动化分析结果，一旦确认，该公司就会向其公共和私营部门的客户发送警报。特别值得注意的是，早在2019年12月31日，该公司就向其公共卫生部门客户发出了武汉肺炎疫情爆发警报。

[![](https://p4.ssl.qhimg.com/t01519f78fd23058e08.jpg)](https://p4.ssl.qhimg.com/t01519f78fd23058e08.jpg)

此外，Bluedot还在官网上宣称，该公司的AI产品还成功在佛罗里达州塞卡病毒爆发前六个月就发出了警报。

通过数据驱动的分析和预测，Bluedot能以超过疾病传播的速度追踪和传播疫情信息，并正确预测了武汉病毒将在中国大陆以外初次出现的地方

——曼谷，首尔，台北，东京。



## 可视化管理：一切围绕仪表盘

这个Web模型仪表板托管在Esri ArcGIS Online。用户可以在模拟的“实时”资源管理仪表板环境中与地图和数据进行交互。交互地图提供有关救援请求、救援完成、救援人员的状况以及医院和庇护所的状况的位置和表格数据，这对于当下的新型肺炎治理来说，有着直接的参考意义（例如有新闻报道部分因封城滞留外地的武汉人被宾馆和交通部门拒绝后，由于缺乏公开统一的资源查询工具，有的去了网吧，有的去了民宿，有的甚至滞留街头，而出现发热症状的，也无法根据医院接待能力和优先级来选择就诊）。

由于缺乏官方统一的EOC终端应用，民间一些技术人员自行开发了一些查询工具，例如在微信上快速传播的“新型肺炎确诊患者相同行程查询工具”。随着这些民间自行开发的工具增多，相关的安全性问题也会凸显，例如这些无法与EOC对接的临时工具缺少数据透明度和可信度以及必要的安全加密和个人隐私保护，而且很容易因为混入一些恶意站点而产生新的安全威胁。



## 实时管理：延误与损失成正比

[![](https://p3.ssl.qhimg.com/t01e1218416a9224ad0.jpg)](https://p3.ssl.qhimg.com/t01e1218416a9224ad0.jpg)

这些操作仪表板使应急管理人员和其他方可以更好地理解复杂、近乎实时的数据源中的数据。这种实时的可视化信息展示方式使紧急情况管理人员能够从数据中获得见解，从而帮助他们在危机期间做出更明智的决策，采取及时精确的行动并制定更全面的战略。



## 下一代SOC的进化方向（EOC可借鉴）

主要变化
<li data-darkmode-bgcolor="rgb(48, 48, 48)" data-darkmode-color="rgb(168, 168, 168)">
从工具到平台化
</li>
<li data-darkmode-bgcolor="rgb(48, 48, 48)" data-darkmode-color="rgb(168, 168, 168)">
从手工到自动化
</li>
<li data-darkmode-bgcolor="rgb(48, 48, 48)" data-darkmode-color="rgb(168, 168, 168)">
基于内部数据到基于开放、实时的威胁情报
</li>
<li data-darkmode-bgcolor="rgb(48, 48, 48)" data-darkmode-color="rgb(168, 168, 168)">
从预防到预测
</li>
<li data-darkmode-bgcolor="rgb(48, 48, 48)" data-darkmode-color="rgb(168, 168, 168)">
从封闭到开放
</li>
<li data-darkmode-bgcolor="rgb(48, 48, 48)" data-darkmode-color="rgb(168, 168, 168)">
从本地到云端
</li>
鉴于EOC与SOC的技术基因高度相似，都在经历成熟度阶段的一次跃迁，安全牛相信在战胜新型肺炎的战役后，政府和大型企业将有更大的热情和预算资源投入下一代智能化、数据化、平台化的EOC和SOC的建设。

近年来，无论是SOC还是EOC，都正在成为应对网络安全和公共安全事件的主流应对方案而进入市场爆发期，根据安全牛《新一代SOC研究报告》，2020年SOC市场规模将达到100亿元。



## 总结：站在大安全角度看安全，用技术变革倒逼规则进化
