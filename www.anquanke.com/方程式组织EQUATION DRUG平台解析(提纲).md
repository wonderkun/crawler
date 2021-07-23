> 原文链接: https://www.anquanke.com//post/id/85354 


# 方程式组织EQUATION DRUG平台解析(提纲)


                                阅读量   
                                **149311**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01a833123b0c2c9a6b.jpg)](https://p3.ssl.qhimg.com/t01a833123b0c2c9a6b.jpg)

**PDF 报告下载：链接：**[**http://pan.baidu.com/s/1nvdirzz**](http://pan.baidu.com/s/1nvdirzz)**   密码：wsvo**

**<br>**

**1.  背景**

对于“方程式组织”，在过去的两年中，安天已经连续发布了三篇分析报告：在《修改硬盘固件的木马——探索方程式（EQUATION）组织的攻击组件》[1] 中，安天对多个模块进行了分析，并对其写入硬盘固件的机理进行了分析验证；在《方程式（EQUATION）部分组件中的加密技巧分析》[2]报告中，对攻击组件中使用的加密方式实现了破解；在《从“方程式”到“方程组”——EQUATION攻击组织高级恶意代码的全平台能力解析》[3]报告中，安天独家提供了方程式Linux和Solaris系统的样本分析，这也是业内首次正式证实这些“恶灵”真实存在的公开分析。

APT的分析成果，与研发反APT产品一样，都要基于充分的基础积累，而不可能“一夜之间建成罗马”，对于方程式这样大至无形的超级攻击组织来说，我们过去所做的具体的分析工作都是盲人摸象的过程，一旦飘忽的线索落入我们已经摸索过的范围之内，就可以迅速发布储备成果，而如果面对的是一个未曾充分探查的区域，则需要更长的时间展开分析工作，因此与安天此前已经发布的3篇方程式的长篇报告相比，本篇报告的当前版本是比较仓促的，因此我们称之为“提纲”，我们旨在能抛砖引玉，邀请更多兄弟团队共同加入分析工作，以便进一步呈现出其全貌。

本篇分析是围绕2017年1月12日，“影子经纪人”放出Equation Group 组件中的61个文件[4] 展开的。经分析，本次放出的61个文件中，其中含有Equation Group 组件和DanderSpritZ（RAT）工具中的一些插件。DanderSpritZ是NSA（National Security Agency）的间谍工具之一，在1月7号“影子经纪人”放出的Windows攻击工具[5]中也包含了大量DanderSpritZ的插件名称。

组件EquationDrug是一个很复杂的模块。其存活时间有近10年，后来被GrayFish升级替代。EquationDrug到GrayFish是攻击平台级别的恶意代码体系，它具有安装与卸载插件功能。本次“影子经纪人”放出的文件中，我们看到了更多的EquationDrug组件中的插件。通过分析比对发现，这些插件比之前安天分析过的插件版本低，但相对更为全面。

至今，安天已经完成了对插件功能列表和部分插件的关联分析，先将此部分的分析工作对外分享，后续会将更多的信息分享。

<br>

**2. 方程式线索曝光和分析成果时间链梳理**

2013年起，安天从样本分析中，逐步发现存在一个拥有全平台载荷攻击能力的攻击组织，并逐步关联分析了其多个平台的样本。在这个过程中，我们感到一个大至无形的超级攻击组织存在，但我们并未找到其攻击背景。

2015年2月，卡巴斯基实验室曝光了一个名为方程式（Equation Group）[6]的攻击组织，卡巴斯基认为该组织活跃近20年，可能是目前世界上存在的最复杂的APT攻击组织之一，并认为该组织是震网（Stuxnet）和火焰（Flame）病毒幕后的操纵者。经过线索比对，安天发现这正是此前一直跟踪的超级攻击组织，决定通过报告公开其针对硬盘固件作业的原理[1]和所破解的其部分加密算法[2],形成了安天对于方程式系列分析的前两篇报告。,

2015年3月，卡巴斯基实验室发布了基于Equation Drug组件或平台的剖析[7]，Equation Drug是“方程式组织”所用的主要间谍组件或平台之一，最早追溯到2001年，并且一直沿用至今。该组件或平台的架构类似于一个具有内核模式和用户模式的微型操作系统，通过自定义接口进行交互，该组件或平台包括驱动程序、平台内核（协调器）和若干插件，其中一些插件配备独特的ID和版本号，用于定义相关功能等。

2016年8月，一个自称“影子经纪人”（The Shadow Brokers）的个人（或组织）声称入侵了网络间谍组织“方程式”（Equation）[8]，并以100万比特币（当时约价值5.6亿美元）的价格，公开“拍卖”所掌握的方程式组织的攻击工具。“方程式组织”被认为与NSA存在联系。为证明成功入侵的真实性，影子经纪人于当月13日在开源项目托管平台GitHub加密发布了这些攻击工具，并有意将其中的少量攻击工具以明文形式发布。

2016年8月，卡巴斯基实验室通过对“方程式组织”与“影子经纪人”曝光的数据进行对比验证[9]，确认了曝光的数据与“方程式组织”有关。2016年10月，影子经纪人对攻击工具再度发起拍卖[10]，并称在GitHub发布的方程式攻击工具只占其掌握的60%。

11月，影子经纪人公开了一份遭受入侵的服务器清单[11]，并称攻击方与NSA有关。清单的日期显示，各系统遭受入侵的时间在2000年到2010年之间，受控IP及域名分布在49个国家，主要集中在亚太地区，受影响的国家包括中国、日本、韩国、西班牙、德国、印度等。 安天将这些数据导入到安天态势感知和预警平台，形成了下图的可视化展现。

[![](https://p2.ssl.qhimg.com/t01b44e81ee9b0fead8.jpg)](https://p2.ssl.qhimg.com/t01b44e81ee9b0fead8.jpg)

图 1 安天态势感知与监控预警平台：“方程式”组织对全球互联网节点的入侵可视化复现

在影子经纪人的爆料中，提及相关服务器可能是Linux、FreeBSD和Solaris。而在2016年上半年的两次技术会议中，安天则明确说明，方程式有针对多个系统平台的样本，其中包括Linux和Solaris。安天最终于11月5日公开了方程式组织针对Linux和Solaris的部分样本载荷的分析报告（安天方程式系列报告之三）。

安天分析团队对小组“方程式”上述信息进行了梳理，整理出方程式事件曝光和相关分析的时间链。

[![](https://p3.ssl.qhimg.com/t0178cf9235ba3de35b.png)](https://p3.ssl.qhimg.com/t0178cf9235ba3de35b.png)

图 2 方程式事件相关信息曝光和厂商分析的时间链

<br>

**3. DanderSpritz攻击平台**

安天通过对本次泄露的文件以及对以往方程式资料的分析发现，“方程式组织的“EquationDrug”平台与泄露文件中提到的“DanderSpritz”具有一定内在联系：

1. 本次泄露的msgkd.ex_、msgki.ex_、msgks.ex_、msgku.ex_为GROK插件，是“DanderSpritz”的插件或模块，该插件在“EquationDrug”平台中也曾出现，通过分析发现本次泄露的GROK为低版本GROK插件。

2. 本次曝光的各类DLL插件中一处数据为插件ID，插件ID都是以0x79开头，如：0x79A4、0x79D8，同样，“EquationDrug”平台的插件也设有内置ID，“EquationDrug”平台的插件ID为0x80开头。且两个平台的插件导出函数参数的数据结构也存在相似之处。

因此，基本可以认为方程式组织使用的“EquationDrug”攻击平台与“DanderSpritz” 使用了相同的架构设计， 两者可能是不同的版本代号，或至少来自同一开发团队，或资源高度共享的团队。

[![](https://p5.ssl.qhimg.com/t01a566554d7489df23.png)](https://p5.ssl.qhimg.com/t01a566554d7489df23.png)

图 3 方程式组织的DanderSpritz攻击平台

[![](https://p5.ssl.qhimg.com/t016d632d5af9e7571e.png)](https://p5.ssl.qhimg.com/t016d632d5af9e7571e.png)

图 4 “影子经纪人”泄露的“DanderSpritz”攻击平台截图

本次“影子经纪人”曝光的文件中多数为“DanderSpritz”平台的攻击插件，从放出的文件列表HASH和截图来看，攻击工具和插件非常丰富且标准化，具体包括远控、漏洞利用、后门、插件等，DanderSpritz_All_Find.txt文件内容多达7千余行，其中插件有数百个之多，我们将泄露出来的61个文件进行梳理，分析出了部分插件的功能，如下表（后续版本会持续更新插件确认结果）：

[![](https://p2.ssl.qhimg.com/t01e53d2c4a3639fd76.png)](https://p2.ssl.qhimg.com/t01e53d2c4a3639fd76.png)

[![](https://p1.ssl.qhimg.com/t01f491a7e15bb2b49e.png)](https://p1.ssl.qhimg.com/t01f491a7e15bb2b49e.png)

[![](https://p4.ssl.qhimg.com/t0196d4949c1f1fe6e9.png)](https://p4.ssl.qhimg.com/t0196d4949c1f1fe6e9.png)

图 5 曝光的“DanderSpritz”平台的攻击插件截图

 “DanderSpritz”一词在“棱镜”事件中曾被曝光，文件指出该平台是NSA用于全球监控的网络武器，可被用于多种作业场景，如下图中“FIREWALK”[12]工具用于网络流量采集和注入，其说明中提及到了DNT的“DanderSpritz”，DNT与ANT同属于NSA的网络组织，“方程式”与NSA再一次被联系到一起。

[![](https://p2.ssl.qhimg.com/t01e837d5263a9edd35.png)](https://p2.ssl.qhimg.com/t01e837d5263a9edd35.png)

图 6 斯诺登曝光的NSA-ANT网络武器FIREWALK

NSA-ANT网络武器最早在2013年从斯诺登事件中曝光，共包含48个攻击武器，随着事件的发酵，不断有媒体和组织对其进行曝光，安天分析工程师根据目前曝光的全部资料尝试初步绘制了相关攻击装备的图谱，其相关映射关联还在进一步的维护中。

[![](https://p2.ssl.qhimg.com/t0191c9d5453599aae2.jpg)](https://p2.ssl.qhimg.com/t0191c9d5453599aae2.jpg)

<br>

**4. 部分组件与插件分析（继续完善中）**

**4.1 GROK键盘与剪贴版记录器驱动**

本次泄露的恶意代码中包含四个功能相似的GROK组件，它们都是PE文件，版本为1.2.0.1，均可以从资源段中解密并释放键盘与剪贴版记录器驱动msrtdv.sys。

**4.1.1 样本标签**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011a9fdfffd2c1f7aa.png)

该恶意代码样本是键盘记录器及剪贴版监视工具，在之前友商报告中曾经提到过有相似功能的恶意代码，下面对其相似之处进行对比。

**4.1.2 版本信息**

样本包含版本信息，文件版本为5.1.1364.6430，源文件名为msrtdv.sys，文件描述为MSRTdv interface driver。其中文件版本低于之前已经曝光的版本5.3.1365.2180，源文件名与文件描述的不同在于将两个字母“d”和“v”的位置互换，一个是“mstrdv.sys”，另一个是“msrtvd.sys”。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018544b38d59d65a58.png)

图 8 本次泄露版本与之前曝光版本的版本信息

**4.1.3 主要功能**

两个不同版本的样本其主要功能相同，通过给转储程序建立专用的进程来汇集所收集的数据，每隔30分钟，将结果压缩到文件"%TEMP%tm154o.da"。之前曝光的版本中，包含多个IoControlCode，分别对应不同的功能。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0104b6ca26aa7c825b.png)

图 9 之前曝光版本的主要功能代码

而本次泄露的样本中，IoControlCode虽然只有0x22002C，但一些主要功能仍然存在，可以通过反编译后的代码看出它们的相同之处。

[![](https://p4.ssl.qhimg.com/t01866f0abfc5a065ce.png)](https://p4.ssl.qhimg.com/t01866f0abfc5a065ce.png)

图 10 本次泄露版本的主要功能代码

从以上分析比较中可以发现，本次泄露的恶意代码样本应为较低版本，无论从版本信息还是功能上，都要低于之前曝光的版本。在影子经纪人泄露出的文件DanderSpritz_All_Find.txt中，GROK的版本号也清楚的说明了这个问题，影子经纪人所释放出的只是GROK组件的低版本部分文件，高版本仍然被其掌握在手中。

[![](https://p1.ssl.qhimg.com/t019ac3eea5b610a15b.png)](https://p1.ssl.qhimg.com/t019ac3eea5b610a15b.png)

图 11 GROK组件的不同版本号

**4.2 Processinfo插件遍历进程模块**

本插件用于实现对指定进程的模块遍历，并调用上层模块预设的回调函数。

**4.2.1 样本标签**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011d6b9e2e49908f4f.png)

**4.2.2 主要功能**

本插件提供四个基于序号导出的函数。

[![](https://p2.ssl.qhimg.com/t0137c22671c7a4b5e9.png)](https://p2.ssl.qhimg.com/t0137c22671c7a4b5e9.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011ad44e40c64b4059.png)

图 12 1号导出函数 设置上层模块回调函数

[![](https://p0.ssl.qhimg.com/t01c5f9fdc599ca4d51.png)](https://p0.ssl.qhimg.com/t01c5f9fdc599ca4d51.png)

图 13 3号导出函数 返回核心功能函数地址

[![](https://p1.ssl.qhimg.com/t01a9ce9abb49bfe82f.png)](https://p1.ssl.qhimg.com/t01a9ce9abb49bfe82f.png)

图 14 4号导出函数 获取插件版本信息

[![](https://p4.ssl.qhimg.com/t01b2d937de5a47c89f.png)](https://p4.ssl.qhimg.com/t01b2d937de5a47c89f.png)

图 15 遍历指定进程，默认为当前进程

[![](https://p0.ssl.qhimg.com/t019363a83788f119d0.png)](https://p0.ssl.qhimg.com/t019363a83788f119d0.png)

图 16 遍历指定进程模块，计算模块对应文件HASH（SHA1）

**4.3 kill_Implant插件杀进程模块**

**4.3.1 样本标签**

[![](https://p1.ssl.qhimg.com/t0104616cf31a96dfc5.png)](https://p1.ssl.qhimg.com/t0104616cf31a96dfc5.png)

**4.3.2 主要功能**

模块调用者传递进来进程ID，该模块利用函数OpenProcess获取句柄，再利用函数TerminateProcess结束对应进程。

[![](https://p0.ssl.qhimg.com/t013b058645f7a717aa.png)](https://p0.ssl.qhimg.com/t013b058645f7a717aa.png)

图 17 结束进程

<br>

**5. 小结**

此次“影子经纪人”释放的Equation Group中的61个文件，对于全球网络安全研究者分析厘清EQUATION相关攻击平台的组成和架构有很大帮助，而经过打通分析相关曝光信息，我们看到了该攻击平台的更多的信息，如数百个攻击插件以及“DanderSpritz”攻击平台。

通过对相关文件分析后，安天分析小组可以判断其中部分组件与之前卡巴斯基所曝光的GROK组件为同类样本，而这些组件为早期的低版本。另外，我们的分析结果也表明了“DanderSpritz”与Equation Drug使用相同的组件和架构设计，“DanderSpritz”可能就是方程式组织使用的Equation Drug攻击平台。

由于时间仓促，我们目前只披露了部分文件和泄露信息的相关分析成果，后续我们的分析工作还会继续进行下去。

五年前，在安天展开针对Flame（火焰）蠕虫的马拉松分析中，有专家曾提醒我们不要“只见树叶，不见森林”，这让我们深刻的反思了传统分析工程师“视野从入口点开始”的局限性，而开始尝试建立起从微观见宏观的分析视野。

对安天来说，这四年以来，对方程式组织的持续跟踪分析，对安天是极为难得的了解最高级别攻击者（即我们所谓A2PT，‘高级的APT’）的经历。深入研究这种具有超级成本支撑和先进理念引领的超级攻击者，对于改善安天探海、智甲、追影等高级威胁检测防御产品的防御能力也非常关键。但对于应对A2PT攻击者来说，无论是有效改善防御，还是进行更为全面深入系统的分析，都不是一家安全企业能够独立承载的。此中还需要更多协同，更多的接力式分析，而不是反复重复的发明轮子。正是基于这种共同认知，在不久之前第四届安天网络安全冬训营上，安天和360企业安全等安全企业向部分与会专家介绍了能力型安全厂商分析成果互认的部分尝试。只有中国的机构用户和能力型安全厂商形成一个积极互动的体系，才能更好的防御来自各方面的危险。

我们警惕，但并不恐惧，对于一场防御战来说，除了扎实的架构、防御、分析工作之外，必胜的信念是一个前提。

无形者未必无影， 安天追影，画影图形！

<br>

**附录一：参考资料**

[1] 安天：修改硬盘固件的木马 探索方程式（EQUATION）组织的攻击组件

[http://www.antiy.com/response/EQUATION_ANTIY_REPORT.html](http://www.antiy.com/response/EQUATION_ANTIY_REPORT.html)

[2] 安天：方程式（EQUATION）部分组件中的加密技巧分析

[http://www.antiy.com/response/Equation_part_of_the_component_analysis_of_cryptographic_techniques.html](http://www.antiy.com/response/Equation_part_of_the_component_analysis_of_cryptographic_techniques.html)

[3] 安天：从“方程式”到“方程组”EQUATION攻击组织高级恶意代码的全平台能力解析

[http://www.antiy.com/response/EQUATIONS/EQUATIONS.html](http://www.antiy.com/response/EQUATIONS/EQUATIONS.html)

[4] THESHADOWBROKERS CLOSED, GOING DARK

[https://onlyzero.net/theshadowbrokers.bit/post/messagefinale/](https://onlyzero.net/theshadowbrokers.bit/post/messagefinale/)

[5] Stolen NSA "Windows Hacking Tools" Now Up For Sale!

[http://thehackernews.com/2017/01/nsa-windows-hacking-tools.html](http://thehackernews.com/2017/01/nsa-windows-hacking-tools.html)

[6] Kaspersky：Equation: The Death Star of Malware Galaxy

[http://securelist.com/blog/research/68750/equation-the-death-star-of-malware-galaxy/](http://securelist.com/blog/research/68750/equation-the-death-star-of-malware-galaxy/)

[7]Kaspersky：Inside the EquationDrug Espionage Platform

[https://securelist.com/blog/research/69203/inside-the-equationdrug-espionage-platform/](https://securelist.com/blog/research/69203/inside-the-equationdrug-espionage-platform/)

[8] Equation Group Cyber Weapons Auction – Invitation

[https://github.com/theshadowbrokers/EQGRP-AUCTION](https://github.com/theshadowbrokers/EQGRP-AUCTION) 

[9] The Equation giveaway

[https://securelist.com/blog/incidents/75812/the-equation-giveaway/](https://securelist.com/blog/incidents/75812/the-equation-giveaway/)

[10] I just published “TheShadowBrokers Message #3”

[https://medium.com/@shadowbrokerss/theshadowbrokers-message-3-af1b181b481](https://medium.com/@shadowbrokerss/theshadowbrokers-message-3-af1b181b481)

[11] Shadow Brokers reveals list of Servers Hacked by the NSA

[http://thehackernews.com/2016/10/nsa-shadow-brokers-hacking.html](http://thehackernews.com/2016/10/nsa-shadow-brokers-hacking.html)

[12] ANTProductData2013

[https://search.edwardsnowden.com/docs/ANTProductData2013-12-30nsadocs](https://search.edwardsnowden.com/docs/ANTProductData2013-12-30nsadocs)

[13] Kaspersky：A Fanny Equation: "I am your father, Stuxnet"

[http://securelist.com/blog/research/68787/a-fanny-equation-i-am-your-father-stuxnet/](http://securelist.com/blog/research/68787/a-fanny-equation-i-am-your-father-stuxnet/) 

[14] Kaspersky：Equation Group: from Houston with love

[http://securelist.com/blog/research/68877/equation-group-from-houston-with-love/](http://securelist.com/blog/research/68877/equation-group-from-houston-with-love/) 

[15] Kaspersky：Equation_group_questions_and_answers

[https://securelist.com/files/2015/02/Equation_group_questions_and_answers.pdf](https://securelist.com/files/2015/02/Equation_group_questions_and_answers.pdf) 

[16] Kaspersky：The Equation giveaway

[https://securelist.com/blog/incidents/75812/the-equation-giveaway/](https://securelist.com/blog/incidents/75812/the-equation-giveaway/) 

<br>

**附录二：关于安天**

安天从反病毒引擎研发团队起步，目前已发展成为以安天实验室为总部，以企业安全公司、移动安全公司为两翼的集团化安全企业。安天始终坚持以安全保障用户价值为企业信仰，崇尚自主研发创新，在安全检测引擎、移动安全、网络协议分析还原、动态分析、终端防护、虚拟化安全等方面形成了全能力链布局。安天的监控预警能力覆盖全国、产品与服务辐射多个国家。安天将大数据分析、安全可视化等方面的技术与产品体系有效结合，以海量样本自动化分析平台延展工程师团队作业能力、缩短产品响应周期。结合多年积累的海量安全威胁知识库，综合应用大数据分析、安全可视化等方面经验，推出了应对高级持续性威胁（APT）和面向大规模网络与关键基础设施的态势感知与监控预警解决方案。

全球超过三十家以上的著名安全厂商、IT厂商选择安天作为检测能力合作伙伴，安天的反病毒引擎得以为全球近十万台网络设备和网络安全设备、超过五亿部手机提供安全防护。安天移动检测引擎是全球首个获得AV-TEST年度奖项的中国产品。安天技术实力得到行业管理机构、客户和伙伴的认可，安天已连续四届蝉联国家级安全应急支撑单位资质，亦是中国国家信息安全漏洞库六家首批一级支撑单位之一。安天是中国应急响应体系中重要的企业节点，在红色代码、口令蠕虫、震网、破壳、沙虫、方程式等重大安全事件中，安天提供了先发预警、深度分析或系统的解决方案。
