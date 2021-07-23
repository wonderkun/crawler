> 原文链接: https://www.anquanke.com//post/id/241046 


# 美国燃油管道公司Colonial Pipeline遭受勒索攻击事件分析及复盘思考


                                阅读量   
                                **218618**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01d4084c6ee8ae271d.jpg)](https://p4.ssl.qhimg.com/t01d4084c6ee8ae271d.jpg)



2021年5月7日，美国 Colonial Pipeline 公司遭到网络攻击，导致其业务受到严重影响。获悉该事件后，微步情报局快速响应，并第一时间进行了研判分析 《 [“美国进入紧急状态”？Colonial Pipeline 遭受勒索软件攻击事件分析](http://mp.weixin.qq.com/s?__biz=MzI5NjA0NjI5MQ==&amp;mid=2650168491&amp;idx=1&amp;sn=241a4b5e716a91bab31131138086766b&amp;chksm=f448a717c33f2e01e6d04cc9260ca2fe610650898af2a32dee7d771e86f30800fbcc20ac2dff&amp;scene=21#wechat_redirect)》。随后，我们保持对该事件的跟进分析，**目前的关键分析结论如下**：
1. 目前，关于该事件直接相关的攻击细节（包括入侵途径、攻击手法、攻击工具等）尚无法得知，但根据相关安全公司以及美国 FBI 的官方消息，已经确认该事件的始作俑者是 DarkSide 勒索组织及其 RaaS 合作伙伴。
1. 根据微步在线的黑客画像系统收录的数据，DarkSide 团伙至少自2020年8月开始出现，以 RaaS 模型运营，截至目前有近百家企业被该团伙攻击，近 73.8% 的被攻击企业分布在美国，其余分别位于德国、法国、加拿大、摩洛哥等境外国家，国内鲜有相关受害者。因此，目前国内相关行业和企业并不是该团伙的主要攻击目标。
1. 勒索软件这种新型威胁自面世以来，不同家族的勒索软件始终快速增长阶段，且呈现定向化、RaaS 化等特点。与此同时，针对能源、医疗、金融等关键基础设施行业的攻击案例明显增长，造成的经济、社会影响也愈发增大。我们建议相关行业、监管及企业安全部门针对勒索软件攻击的建立专项防护体系、应急响应和业务快速恢复机制，加强对于勒索软件的检测、响应及情报共享能力。
1. 我们认为，企业针对勒索软件的防护应该采取不同于其他类型威胁的方案。对于勒索软件的防护应该重点放在初始入侵阶段，减少被入侵的攻击面，同时应该加强流量层面的漏洞、爆破等攻击行为的识别和攻击成功的自动判定，并快速响应处置。


## 事件回顾

2021年5月8日，美国燃油管道公司 Colonial Pipeline 官网进行通告，声称于7日得知被黑客攻击，同时联系第三方网络安全专家、执法部门和其他联邦机构启动应急响应，确定涉及勒索事件。启动应急响应后停止所有管道运行，并且关闭某些系统以便避免继续遭受攻击。

[![](https://p1.ssl.qhimg.com/t018b8143a99194769e.png)](https://p1.ssl.qhimg.com/t018b8143a99194769e.png)

2021年5月9日，美国联邦调查局（FBI）新闻办公室声明，收到于7日收到 Colonial Pipeline 公司网络中断通知。

2021年5月9日，美国网络安全和基础设施安全局（CISA）表示针对 Colonial Pipeline 公司遭受网络安全攻击事件，正在和 Colonial Pipeline 公司以及其他政府部门进行接触。

2021年5月9日，美国交通运输部门（USDOT）下属子机构，联邦机动车辆安全管理局（FMCSA）发布区域紧急声明，由该部门的东部、南部和西部服务中心相关管理员共同发布，宣布由于 Colonial Pipeline 公司遭受网络攻击导致燃油运输受阻，紧急启动机动车辆进行运输燃油，以解决受影响的美国18个州燃油需求问题。

2021年5月9日，Colonial Pipeline 官网更新通告，声明目前该公司运营人员正在制定系统重启计划，虽然主管道保持离线状态，但终端和交付点之间的较小管道已经可以使用。

2021年5月10日，Colonial Pipeline 官网更新通告，声明将继续恢复管道运输，并且目标在本周末前恢复大部分运营服务，目前已经恢复4号管道处于手动控制状态。同时正在与托运公司合作，将产品移至码头进行本地交付。

2021年5月10日，美国联邦调查局（FBI）新闻办公室更新声明，确认 DarkSide 勒索软件是造成 Colonial Pipeline 公司网络受损的原因。

2021年5月10日，DarkSide 团伙发布证明称，针对 Colonial Pipeline 的攻击是其 RaaS 的合作伙伴发起，且其攻击目的仅仅是为了赚钱，没有任何政治动机。

[![](https://p3.ssl.qhimg.com/t01b7a381dee5ccb696.jpg)](https://p3.ssl.qhimg.com/t01b7a381dee5ccb696.jpg)



## 受害者及事件影响

Colonial Pipeline 公司成立于1961年，管道建设于1962年，总部位于佐治亚州阿尔法利塔，拥有美国目前最大的成品油管道系统，管道长达5500英里（8850公里），管道始于德克萨斯州休斯敦，墨西哥湾沿岸，终止于纽约港和新泽西州，贯穿18个州市。平均每天向美国南部和东部地区输送多达1亿加仑的汽油、家用取暖油、航空燃料和其他精炼石油产品，占到东海岸消耗所有燃料的45％。管道还连接到几个主要机场，包括亚特兰大、纳什维尔、夏洛特、格林斯伯勒、罗利·达勒姆、杜勒斯、巴尔的摩-华盛顿和纽约大都会机场。通过维基百科介绍大致了解到，Colonial Pipeline 公司作为美国关键基础设施也是美国燃油管道的大动脉，由于勒索软件攻击导致系统宕机，无法提供管道运输服务，对美国能源行业影响巨大，可能影响依赖燃油资源的众多行业正常运转。同时此次网络攻击事件公布后导致汽油期货在本周一开盘后一度暴涨，石油价格信息服务（OPIS）能源分析全球主管克罗萨对此表示，油价飙升的幅度将”取决于这条线路中断的天数”。

[![](https://p2.ssl.qhimg.com/t013bb1849e258ef140.jpg)](https://p2.ssl.qhimg.com/t013bb1849e258ef140.jpg)

事件发生后，Colonial Pipeline 公司和美国联邦调查局（FBI）、美国网络安全和基础设施安全局（CISA）、联邦机动车辆安全管理局（FMCSA）等联邦政府部门迅速做出反应。Colonial Pipeline 公司主动关闭了关键系统，积极联系政府部门和第三方安全公司进行合作解决此次事件。联邦机动车辆安全管理局（FMCSA）也发布了一份区域紧急声明。帮助 Colonial Pipeline 公司中断管道运输后进行燃油运输。

[![](https://p3.ssl.qhimg.com/t01f04b631c9245fdf4.png)](https://p3.ssl.qhimg.com/t01f04b631c9245fdf4.png)



## DarkSide 团伙画像

通过参与此次应急响应的第三方安全公司人员和美国 FBI 的声明可以了解到 ，DarkSide 勒索软件才是造成中断管道运输的背后真凶。那么 DarkSide 是一款什么样的勒索软件，有什么攻击特点，运作机制是怎样的，背后的核心团队又是谁？

[![](https://p0.ssl.qhimg.com/t0136e6015544562131.png)](https://p0.ssl.qhimg.com/t0136e6015544562131.png)

### **1、DarkSide 背景**

DarkSide勒索软件于2020年8月出现，并以勒索软件即服务（RaaS）的商业模式运作，分别由勒索软件的开发运营人员和其招募的分发者共同组成，由分发者进行攻击，核心开发运营商则负责勒索软件的开发与受害者谈判收取勒索赎金，抽取 20%-30% 的赎金，其余的收益则归分发者所有。

该勒索软件核心团队声称医疗、教育、非营利组织和政府等领域不在其攻击目标范围内，除了加密受害者系统文件外还会窃取受害者系统数据，通过获取到的受害者信息进行评估，然后再确定需要支付的解密金额，对于没有被盗数据的受害者，赎金要求低至20万美元，而对于被盗数据的受害者，赎金要求高达200万美元。其团队宣称并非”勒索新手”，在其介绍中写到已经通过其它勒索软件合作获利数百万美元，创建 DarkSide 是因为没有找到相对完美的产品。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d70612ecb3f20b4e.jpg)

值得回味的是，该勒索软件核心团队曾声明只会针对大型盈利性公司，并将他们支付的部分赎金用于慈善事业。随后在去年10月13日，DarkSide 团队通过其网站粘贴出两张 0.88BTC 的收据，受捐赠方分别为国际儿童基金会和水项目两个非盈利组织。但是由于两笔捐赠均为勒索赎金所得，而无法使用。

[![](https://p4.ssl.qhimg.com/t013f675b2a749960b4.png)](https://p4.ssl.qhimg.com/t013f675b2a749960b4.png)

### **2、DarkSide 攻击手法**

DarkSide 勒索软件采用 RaaS（勒索即服务）模式运行，目前存在 Windows 和 Linux 双平台版本，可通过可视面板进行定制，定制内容包括加密目录、加密模式、持久化方式、提权操作、网络交互、密币支付种类等等。当前发现针对特定目标会创建定制的可执行软件，使用 SALSA20 密钥来加密文件，通过可执行文件中的 RSA-1024 密钥对该密钥再次加密。使用八个伪随机定义的小写十六进制字符作为加密文件后缀。DarkSide 勒索软件会在受害者机器上留下勒索记录，其中包含了被盗数据量、数据类型、以及数据泄露站点链接。在规定期限内，如果没有收到支付的赎金将会窃取的信息公开。

[![](https://p3.ssl.qhimg.com/t0194eecb28021a4a4c.png)](https://p3.ssl.qhimg.com/t0194eecb28021a4a4c.png)

该勒索软件主要针对非俄语系统，确保不会在独立国家联合体（CIS）的机器中运行，并且曾经在俄语论坛 XSS 上发布相关信息，猜测该运营商为讲俄语的黑客组织，尽管目前没有证据表明俄罗斯可以从勒索软件中获取利益，但俄罗斯黑客已经渗透到美国一些关键部门。

### **3、DarkSide 组织受害者分析**

通过收集到的信息，该勒索软件自2020年8月起，攻击范围贯穿10个国家，超过90家企业被攻击，涉及行业包括 IT、测绘、服务、化工、交通、金融、能源等多个行业，其中受害者占比最多的是美国。而 DarkSide 的分发者似乎对服务业和 IT 行业比较关注，所以涉及到的企业受灾最为严重，同时根据泄露的数据发现，DarkSide 已经不是第一次对石油和天然气能源行业下手。

[![](https://p3.ssl.qhimg.com/t01305d16807c448ad7.png)](https://p3.ssl.qhimg.com/t01305d16807c448ad7.png)

[![](https://p1.ssl.qhimg.com/t01fa7f00b9a4758b1a.png)](https://p1.ssl.qhimg.com/t01fa7f00b9a4758b1a.png)

在发生此次 Colonial Pipeline 公司被攻击事件后，DarkSide 运营商在官方网站上中声明，他们的目标是赚钱而不是给社会制造问题，不参与地缘政治，和任何政府都无关，并且从今天起，将会对分发者攻击目标进行审核，确保避免再次带来影响社会的后果。

### **4、疑似 DarkSide 关联组织**

根据火眼公司当前披露的调查报告，基于 Darkside 勒索事件 TTPS 指纹可关联到 UNC2628、UNC2659、UNC2465 三个未知组织。当然，该关联存在一定程度的概率性，只能说明这些组织可能与 Darkside RaaS 运营机构存在合作关系。在公开报告中，火眼并未透露关于 Colonial Pipeline 公司切实的关联证据。除此之外，这三个组织当前并未公开披露。概述火眼报告中关于这三个组织的描述以及简要的 Darkside 部署流程如下。
<td class="ql-align-justify" data-row="1">**UNC2628**</td><td class="ql-align-justify" data-row="1">该组织至少自2021年2月开始活跃，攻击节奏快，一般两到三天完成勒索软件部署。证据表明 UNC2628 已与部分 RaaS 运营机构（包括 SODINOKIBI、NETWALKER 勒索软件）合作。</td><td class="ql-align-justify" data-row="1">当前发现攻击者对目标 VPN 系统进行密码喷洒类型的登录尝试，成功登录目标主机，然后借助域内主机进行横移、域控操作。最终使用 PsExec 将 Darkside 部署至域内机器。</td>
<td class="ql-align-justify" data-row="2">**UNC2659**</td><td class="ql-align-justify" data-row="2">该组织至少自2021年1月开始活跃，一般攻击周期控制在10天之内，善于使用 SonicWall SMA100 SSL VPN 产品漏洞进行登录权限修改而后远程渗入目标系统。</td><td class="ql-align-justify" data-row="2">攻击者渗入目标系统后，使用 TeamViewer 工具建立持久化，使用 rclone 工具窃取云端海量数据。然后部署 power_encryptor.exe 对文件进行加密并通过 SMB 协议创建赎金记录。</td>
<td class="ql-align-justify" data-row="3">**UNC2465**</td><td class="ql-align-justify" data-row="3">该组织至少可追溯到2019年4月，惯于使用基于 PowerShell 的 .NET 后门 SMOKEDHAM。</td><td class="ql-align-justify" data-row="3">攻击者通过鱼叉邮件投递 SMOKEDHAM 后门，然后通过开源工具进行横移渗透，接着使用 PsExec和cron 部署 Darkside 勒索软件，最后攻击者将会致电受害人的客户支持热线，告诉他们数据被盗，并指示他们遵循赎金记录中的链接。</td>



## 事件思考

Colonial Pipeline 公司作为美国最大的燃油管道商，发生严重网络安全事件后，进行了快速的应急响应处理，通过相应措施避免二次损害，作为美国重要关键基础设施，美国相关联邦政府也表达高度重视，积极参与整个处理响应中。但是仍然可以看出 Colonial Pipeline 公司的 IT 和 OT 并没有将网络绝对隔离，所以目前暂未完全恢复业务。此次事件也是继 SolarWinds 供应链攻击以来对美国造成巨大影响又一次网络攻击事件，势必会引起美国政府对于加强网络安全能力关注。

**勒索软件已经成为目前最具破坏力的网络威胁，且仍然呈爆发式增长。**

根据安全厂商 CheckPoint 收集的数据表明，在过去的9个月中，美国每月勒索攻击次数几乎增加到了两倍，达到了300次，而最近几周，美国每88个公共事业组织中就有一个遭受到勒索软件攻击，较2021年初增长了34%，而美国网络安全和基础设施安全局（CISA）的官方网站专门列出一份勒索软件指南，页面上详细讲解了关于针对勒索软件的介绍和相关缓解措施。

**此次攻击事件也展现出勒索软件攻击已经具备定向攻击的能力。**

纵观勒索病毒发展历史，早期勒索软件运营模式单一且赎金较低，并且大多是针对普通用户。经过近几年的发展，勒索软件已经从 To C 转向 To B，从广撒网模式转变为定向模式，攻击方法也花招不断，除了垃圾邮件、弱口令爆破、网页挂马、漏洞组合利用等常见的方法还出现了 BitPaymer 利用 Apple 0day 漏洞攻击的案例。并且一些 APT 组织已经使用勒索软件作为攻击手段之一，这些 APT 组织表面上是使用勒索软件进行攻击，实际上却是在进行掩盖获取情报数据的目的，又或者是进行关于地缘政治目的的破败数据报复行为。所以勒索软件的攻击手法会更加具备 APT 能力的水准，定向性也更强。

**勒索软件针对关键基础设施的攻击更为频繁，后果也愈发严重。**

在近几年，与勒索软件相关的安全大事件比比皆是，其中不乏一些关键基础设施被攻击。关键基础设施包括能源、金融、交通、教育、科研、水利、工业制造、医疗卫生、公用事业等多个领域，是一个综合实体继续顺利运作至关重要的基本资产，关乎着整个国家的发展，一旦被攻击导致无法运转，造成的损失是无法测量的，同时很有可能波及其他行业。所以针对关键基础设施行业的网络安全防御也格外重要。

**企业应该重点加强威胁的检测和响应能力来针对性防范勒索软件的攻击。**

勒索软件攻击的日益增长与攻击手法的更加精进，都在考验着企业的防御能力。特别在面对具有定向性的勒索攻击时，不能纯粹依靠传统安全软件进行防护和备份文件恢复，重点在于防御并非事后处置。需要加强纵深防御和建立快速应急响应机制与团队，针对不同业务线、网络、设备制定不同防护策略，加强边界防御管理能力，保证安全响应流畅性。



## 参考链接

https://www.colpipe.com/news/press-releases/media-statement-colonial-pipeline-system-disruption

https://www.fbi.gov/news/pressrel/press-releases/fbi-statement-on-network-disruption-at-colonial-pipeline

https://twitter.com/CISAgov/status/1391124273155219459

https://www.fmcsa.dot.gov/emergency/esc-ssc-wsc-regional-emergency-declaration-2021-002-05-09-2021

https://www.colpipe.com/news/press-releases/media-statement-colonial-pipeline-system-disruption

https://www.colpipe.com/news/press-releases/media-statement-colonial-pipeline-system-disruption

https://www.fbi.gov/news/pressrel/press-releases/fbi-statement-on-network-disruption-at-colonial-pipeline

https://www.bleepingcomputer.com/news/security/darkside-new-targeted-ransomware-demands-million-dollar-ransoms/

https://www.fireeye.com/blog/threat-research/2021/05/shining-a-light-on-darkside-ransomware-operations.html
