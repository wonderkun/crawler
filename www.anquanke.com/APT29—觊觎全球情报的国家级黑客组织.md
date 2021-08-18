> 原文链接: https://www.anquanke.com//post/id/250535 


# APT29—觊觎全球情报的国家级黑客组织


                                阅读量   
                                **31728**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01bd04e6f791c8bc8b.jpg)](https://p3.ssl.qhimg.com/t01bd04e6f791c8bc8b.jpg)



## 一、概述

依托国家情报机构发动的网络战日益频繁。在各国的网络战博弈中，俄美等国家凭借其长期的情报机构建设积累以及强大的武器库资源储备在公众眼中暂处第一梯队。国内情报分析人员接触到的有关这类高度复杂的APT组织相关情报信息大多数来源于国外安全机构。拥有俄罗斯联邦对外情报局（SVR）背景的APT29组织即是如此，近半年时间内，随着SolarWinds供应链攻击的曝光以及后续多家安全机构的调查分析，疑似幕后黑手的APT29开始回归大众视野中。

当前针对APT29的公开披露情报信息因为国家政治公关、敏感信息阉割等因素显得繁琐混杂、可信度高低不一。微步情报局基于已积累的情报信息以及网络公开情报信息甄别研判结果，对APT29的重大攻击事件、组织关联归因、攻击技战法等进行了深度复盘分析，致力于客观、全面地向大众解读APT29的真实面貌。

本文主要输出以下内容：
1. 梳理当前公开情报信息，APT29组织结构分析及各分支机构经典攻击事件分析。
1. 探究The Dukes、WellMess、Nobelium（Solarwinds）归因点及可信度。
1. APT29关键TTPS剖析。
1. 微步视角下的APT29组织画像。


## 二、背景

据维基百科记载，俄罗斯联邦对外情报局（俄语：Служба Внешней Разведки，英语：Foreign Intelligence Service of the Russian Federation，简称SVR）是俄罗斯的情报机关之一，专门负责俄罗斯境外的情报活动。对外情报局的前身是苏联国家安全委员会第一总局，即克格勃第一总局，是1954年3月13日–1991年11月6日期间苏联的情报机构，在当时被认为是全球效率最高的情报收集机构。

[![](https://p1.ssl.qhimg.com/t01f577dec26267605e.png)](https://p1.ssl.qhimg.com/t01f577dec26267605e.png)[![](https://p0.ssl.qhimg.com/t01f597f09431b9061d.png)](https://p0.ssl.qhimg.com/t01f597f09431b9061d.png)

图【1】克格勃第一总局&amp;SVR标志性徽章

1991年苏联解体后，俄罗斯境内的原克格勃机关改制为俄罗斯联邦安全局（FSB），其第一总局改制为俄罗斯对外情报局（SVR）。白俄罗斯则完整保留境内克格勃机关的建制及原有名称。其总部位于俄罗斯莫斯科亚先捏沃，有一万三千名员工，特工会化身为外交人员或记者进行情报活动。

APT29隶属于俄罗斯联邦对外情报局，国内外安全机构曾命名Dark Halo、StellarParticle、Nobelium、UNC2452、YTTRIUM、The Dukes、Cozy Bear、CozyDuke、Office Monkeys等。其攻击目标覆盖欧洲、北美、亚洲、非洲的多个地区和国家，主要攻击目标为包含美国、英国等在内的北约成员国以及欧洲地域邻近国家，具体攻击行业目标为政府实体、科研机构、智囊团、高技术企业、通信基础设施供应商等。

[![](https://p0.ssl.qhimg.com/t01998c1524cd095c14.png)](https://p0.ssl.qhimg.com/t01998c1524cd095c14.png)

图【2】 引自爱沙尼亚外国情报局报告

APT29至少自2008年开始活跃，其最初映入公众眼帘是在2009年Dukes早期工具集曝光，木马的新颖之处在于使用Twitter社交平台存放恶意网络资产、以此为跳板进行后续网络交互行为。“Duke”的命名源于卡巴斯基安全研究人员，由臭名昭著的Duqu蠕虫（与Stuxnet震网蠕虫存在关联）联想而来，此后一直延用至今。值得注意的是Duke系列木马组件与Duqu蠕虫无任何实质性关联，切勿混为一谈。自此至2019年10余年时间内，公开披露的APT29活动中均可看到Dukes工具集的使用，只是后续的Dukes工具集已经扩充成包含PolyglotDuke、RegDuke、MiniDuke、FatDuke、SeaDuke等在内的复杂武器库工具集。在此期间，最让人印象深度的是2016年美国总统大选期间APT29针对美国民主党全国委员会（Democratic National Committee，简称DNC）的间谍活动（据NCCIC、FBI披露，该活动由APT28、APT29协同参与，于2015年夏季开始对目标系统渗入）。

如果说2020年之前所披露的APT29的一系列攻击活动只是让公众广泛意识到存在这么一个实力雄厚、背景强大的APT组织，那么自2020年6月之后的攻击活动将会使绝大多数独立政权国家开始思考自身的网络环境安危。2020年7月，全球新冠肺炎疫情局势紧张，一波使用WellMess\WellMail等攻击组件对全球COVID-19 疫苗研制机构的定向攻击活动被关联归因至APT29，同年12月份曝光的Solarwinds供应链攻击活动同样指向APT29，受害者覆盖欧美亚地区4700余个实体机构。

本文后续将逐步梳理已掌握情报信息，客观地去分析APT29关联归因证据，对已披露的重点攻击事件进行复盘分析，最后将结合微步积累情报数据给出APT29的团伙画像。



## 三、组织结构划分

我们整合了自2015年至今关于APT29的公开披露报告，披露来源为权威的国家情报部门机构和安全研究机构，披露内容包括武器库特马组件、特定攻击事件、阶段性总结报告、取证溯源调查报告等内容。对其进行时间先后排序，整理如下表所示。

Table 1 APT29公开披露报告

[![](https://p0.ssl.qhimg.com/t01b764c75a1ccbaa4a.png)](https://p0.ssl.qhimg.com/t01b764c75a1ccbaa4a.png)

在历史披露报告中，各安全机构对某一时间节点的攻击组件、攻击活动、幕后攻击团伙（有些攻击事件在披露时未能关联至已知组织，产生了一系列全新的命名）存在多种不同的命名，其中部分命名是由特马组件指纹演变而来。为了便于整合这些信息，我们可以依据特定的木马工具集（主要指初始投递到PC端的前阶段载荷）对其进行分类，总共可以分成三块：The Dukes系列、WellMess系列、Nobelium系列。其中各个系列除了前期攻击载荷中使用的特马工具存在较大差异之外，在攻击目标、参与攻击事件、攻击活跃时间区段等均会存在一些重合。各系列分支简要说明如下：

Table 2 APT29分支结构：
<td data-row="1">**The Dukes系列**</td><td data-row="1">2008—2019.10，使用时间跨度最长，包括多个复杂的命名含“Duke”的工具集，包括2016年对美国民主党DNC攻击中使用。</td>
<td data-row="2">**WellMess系列**</td><td data-row="2">2018.06—至今，针对Windows、Linux双平台，由JPCERT披露，攻击了包括美国、英国在内的多个国家的医疗、政府、科研、高校、高科技企业等机构。WellMess、WellMail、SoreFang恶意软件。COVID-19 疫苗研制机构间谍活动。</td>
<td data-row="3">**Nobelium系列**</td><td data-row="3">2018.11—至今，MSTIC命名，包含Solarwinds供应链攻击中的构建过程劫持木马、嵌入后门以及后续多阶攻击组件。该系列工具集最早于2018年11月火眼披露的对美国智库、公共部门等的定向攻击中出现。</td>

The Dukes、Well Mess、Nobelium系列工具集活跃时间轴线图如下：

[![](https://p1.ssl.qhimg.com/t0172b4a31a73f080fd.png)](https://p1.ssl.qhimg.com/t0172b4a31a73f080fd.png)

图【3】 APT29三大系列分支活跃时间示意

接下来，我们针对The Dukes系列、WellMess系列以及Nobelium系列分开总结梳理APT29特有的攻击活动特点。



## 四、攻击战术剖析

基于上述对APT29的组织结构分类，我们分开探讨The Dukes、WellMess、Nobelium三大分支特有的攻击偏好、攻击战术、代表性攻击事件。

### **4.1 The Dukes系列**

The Dukes系列是最早公开披露的APT29组织，同期别名包括HamMertos、Cozy Bear、CozyDuke等，活动时间从2008年到2018年，攻击目标包括全部欧洲国家、多数中东地区国家、部分亚非国家、以美国为主的北美国家，具体行业目标包括政府实体、政府智库、车臣极端主义机构等。2015年9月，F-Secure团队对Dukes的攻击活动、攻击组件进行总结披露；随后ESET团队在2019年10月对Dukes的后续攻击活动及武器库进行扩充披露。

在Dukes一系列的攻击活动中，除了2015年夏季至2016年末美国总统大选期间对民主党派为主政府机构的定向攻击活动之外，Dukes攻击目标主要集中在俄罗斯西南方向的欧洲邻国。其攻击方式主要为鱼叉网络攻击，通过伪造特定时政话题内容、携带恶意钓鱼外链或恶意附件投递初始攻击载荷。其历史攻击活动中使用过的部分诱饵素材展示如下。

[![](https://p2.ssl.qhimg.com/t013e0ed6aa4dfd0d6d.png)](https://p2.ssl.qhimg.com/t013e0ed6aa4dfd0d6d.png)

图【4】 2014.07使用的“Office Monkeys”视频诱饵截图

[![](https://p2.ssl.qhimg.com/t01683f4a1ef388114b.png)](https://p2.ssl.qhimg.com/t01683f4a1ef388114b.png)

图【5】 2015.08鱼叉邮件“选举结果可能会被修改”

除了发现这类常见的鱼叉网络攻击之外，Dukes也存在一些“异常”的攻击行为。2014年10月，Levithan安全团队披露Dukes通过控制部分Tor网络出口节点进行中间人攻击，劫持用户流量后投递Dukes特马，此种发散式的攻击迅速组建了一个超过千余台PC主机的僵尸网络（肉机主要分布在蒙古和印度）。对于这种一反常态的发散式攻击行为，攻击动机存在较大争议，其中一种观点是Dukes攻击目标为与俄罗斯相关的毒贩等犯罪团伙。除此之外，2015年1月至2016年年底，Dukes发动了多起针对美国政府机关、智库、非政府单位的鱼叉邮件钓鱼攻击，具体攻击目标达到数千数量级别。在该系列鱼叉邮件攻击活动的早期，Dukes向超过一千个目标邮箱发送了同一封钓鱼邮件，邮件内容并未像之前那样伪装时政热点这类诱骗性更高的话题内容，反而采用了勒索团伙常用的“电子传真”这类具备垃圾邮件特点的话题，这种对千余个目标采用完全相同的钓鱼邮件而且内容粗糙的行为特点在APT攻击案件中较为罕见。当然，从攻击者角度来看，这种大批量的攻击只是用于前期甄别有价值目标，服务于前期社攻阶段。

我们以2016年9月份Dukes对哈佛大学的一次鱼叉邮件攻击为例介绍Dukes时期的常见攻击形式。攻击者伪造“克林顿基金”话题内容诱使用户点击外链下载攻击者准备的攻击载荷，其中下载文件为ZIP压缩格式，压缩密码在邮件正文中给出（6190）。

[![](https://p4.ssl.qhimg.com/t01b416f98c39a39a7d.png)](https://p4.ssl.qhimg.com/t01b416f98c39a39a7d.png)

图【6】 引自volexity，“克林顿基金会”诱饵

附件解压后是一个名为“37486-the-shocking-truth-about-election-rigging-in-america.rtf”的LNK文件，命令行语句启动powershell进程执行base64编码的ps1脚本，ps1脚本进行当前PC机器环境检测之后按照既定文件偏移提取LNK文件中数据，然后进行异或解密，写入落地文件。落地文件包括：

%TEMP%\37486-the-shocking-truth-about-election-rigging-in-america.rtf（诱饵文件）、

%APPDATA%\Skype\hqwhbr.lck（PowerDuke特马加载器）、%APPDATA%\Skype\hqwhbr.lck: schemas（PNG格式的文件流数据，携带加密PowerDuke载荷，以图片格式打开将正常显示装酒的高脚杯）。内存态的PowerDuke特马与攻击者交互实现常见的窃密、监控、后门等行为。

[![](https://p3.ssl.qhimg.com/t012e1e30a5c505f217.png)](https://p3.ssl.qhimg.com/t012e1e30a5c505f217.png)

图【7】 PowerDuke鱼叉邮件攻击流程示意图

LNK 文件在真实用户环境中打开后将展示释放的诱饵文档。

[![](https://p1.ssl.qhimg.com/t01b9423e7137eb24a7.png)](https://p1.ssl.qhimg.com/t01b9423e7137eb24a7.png)

图【8】 美国选举操纵的“令人震惊”的真相

上述鱼叉邮件攻击活动中投入使用的PowerDuke组件是The Dukes在美国总统大选期间使用频率较高的一款特马，自2008年至2019年期间，Dukes组件经过一系列扩充改进已形成一套功能齐全的工具集，实现功能包括简单的下载器、加载器、窃密木马、高级远控木马、提权组件（曾披露投入使用0day漏洞）、加密组件、横移组件等。在实际攻击活动中，投递载荷会根据实际情况选择多阶Dukes特马渗入。参考ESET披露的“Ghost行动”中的Dukes工具集使用流程如下。

[![](https://p4.ssl.qhimg.com/t01f95688355cbcbb23.png)](https://p4.ssl.qhimg.com/t01f95688355cbcbb23.png)

图【9】 引自ESET Dukes “GHOST”行动披露报告

基于F-Secure在2015年总结的Dukes各攻击组件活跃时间区间轴线图，我们整合后续系列的Dukes组件，绘制完整的Dukes组件使用时间区间图如下所示：

[![](https://p3.ssl.qhimg.com/t011857da15e9ae797b.png)](https://p3.ssl.qhimg.com/t011857da15e9ae797b.png)

图【10】 The Dukes工具集各组件投入使用时间区间

### **4.2 WellMess系列**

WellMess系列攻击组件最早于2018年7月由JPCERT在“针对Linux和Windows的恶意软件WellMess”一文中披露，该木马采用golang和.Net环境进行开发设计，实现基础的窃密监听恶意功能，并存在针对Windows、Linux平台的攻击样本。当时只是作为恶意软件进行披露，并未关联归因，所以并未引起公众关注，直到两年后的2020年7月，正值全球新冠疫情紧张时期，英国国家网络安全中心（National Cyber Security Centre（United Kingdom），简称NCSC）联合NSA（美国国家安全局）、CISA（美国网络安全和基础设施安全局）、CSE（加拿大通信安全机构）披露了APT29使用WellMess组件（还包括新命名的WellMail同源组件）攻击全球COVID-19疫苗研制机构（主要国家为英国、美国、加拿大），随后英国普华永道公司披露了WellMess组件归因至APT29的部分细节。

区别于The Dukes时期的攻击活动，WellMess系列攻击活动主要通过远程网络渗透形式发起攻击，期间使用了多个Nday漏洞，其中包括国内某安全厂商的VPN升级包未验证漏洞。随着WellMess的曝光度增加，国内外的调查行动显示WellMess的攻击目标覆盖医疗、政府、科研、高校、高科技企业等行业，除了欧美地区国家之外，部分亚洲国家也是WellMess的主要攻击目标。WellMess活动的基本渗透流程如下图所示，攻击者通过网络渗透手段成功实现单点登录之后，会下发WellMess系列木马组件建立C&amp;C通信通道，随后会结合第三方工具（如网络代理、端口转发、密码爬取、信息收集等工具）辅助进行深层的域环境渗透攻击，最终目的为寻找高价值主机窃取情报。

[![](https://p1.ssl.qhimg.com/t01d53b291210838cc2.png)](https://p1.ssl.qhimg.com/t01d53b291210838cc2.png)

图【11】 WellMess攻击流程示意图

WellMess组件使用的C&amp;C通信协议包括HTTP、HTTPS、DNS，其中HTTP协议通信最为常见。WellMess木马上线之后会立即与C&amp;C端交互协商用于后续通信数据加密的AES key，更新的AES key采用RSA算法加密传输。木马与C&amp;C端的交互数据加密协议可分为两部分：HTTP Header部分的Cookie字段、Body data部分。其中头部的Cookie数据用于传输C&amp;C下发指令，Body部分为具体功能指令对应的上传数据。其HTTP通信数据加密协议结构如下:

[![](https://p1.ssl.qhimg.com/t01526856c8f86a8305.png)](https://p1.ssl.qhimg.com/t01526856c8f86a8305.png)

图【12】 WellMess HTTP通信流量加密协议

截取WellMess木马 HTTP通信加密流量如下:

[![](https://p1.ssl.qhimg.com/t0166b422fb9970eb50.png)](https://p1.ssl.qhimg.com/t0166b422fb9970eb50.png)

图【13】 WellMess木马HTTP通信加密流量

### **4.3 Nobelium（SolarWinds）系列**

2020年12月13日，FireEye安全公司披露了Solarwinds供应链攻击事件，攻击者通过攻击SolarWinds软件供应商实现SolarWinds Orion管理软件构建编译过程中投毒。该供应链攻击事件至少可追溯到2020年春季，受害者至少包括北美、欧洲、亚洲和中东的政府、咨询、技术、电信和采掘等行业机构，全球超过18000多个具体单位可能受到此起供应链攻击活动影响。英美政府将Solarwinds供应链攻击事件归因至APT29，但是并未提供具体归因证据。2021年3月，瑞士安全公司PRODAFT发布对SilverFish（PRODAFT命名的组织名称，可关联到Solarwinds供应链攻击事件）进行为期近三个月的调查报告，该调查报告为Solarwinds供应链攻击事件归因至APT29提供了较为有力的佐证（本文后续的Nobelium关联归因部分将展开介绍）。

MSTIC在2021年一二季度持续披露了Solarwinds供应链攻击事件中Sunburst木马之后的其他组件，基于Microsoft Defender提供的PC端数据支持，MSTIC关联到2021年多起鱼叉式网络攻击活动，该系列活动最早可以追溯到2018年12月份。MSTIC将包括Solarwinds供应链攻击在内的一系列攻击活动的幕后组织命名为Nobelium（译为锘’一种放射性金属元素’，采用微软系的化学元素命名法命名）。鉴于Nobelium特有武器库组件及关联攻击事件可以较好的与APT29早期的Dukes以及WellMess区分开来，我们采用Nobelium的命名对APT29的这一特有分支部分进行梳理总结。

Nobelium参与的Solarwinds供应链攻击事件属于极具代表性的软件构建平台失陷（即下图中的Compromise build platform（D），参考Google安全团队发布的供应链攻击类型总结报告）类型的攻击。攻击者通过攻击Solarwinds供应商，渗入其Orion产品构建平台，监控劫持Orion的构建过程，动态替换源代码文件实现投毒。

[![](https://p1.ssl.qhimg.com/t01ee81c83459f865f6.png)](https://p1.ssl.qhimg.com/t01ee81c83459f865f6.png)

图【14】 Google供应链攻击面总结

据CrowdStrike团队和Volexity团队披露信息，Nobelium疑似采用Microsoft Exchange 0day（根据Sunspot木马编译时间为2020年2月推测）漏洞渗入Solarwinds供应商产品构建系统，植入Sunspot木马。该木马劫持Orion软件编译过程、植入恶意代码，导致恶意的Sunburst后门被编译到Orion产品发布版本中。此后该携带后门的Orion软件将通过供应链渠道合法下发到用户环境，Nobelium借助Sunburst后门模块筛选有价值目标实施后续攻击行为。该供应链攻击流程图如下：

[![](https://p2.ssl.qhimg.com/t01e5ad98e88448b7f3.png)](https://p2.ssl.qhimg.com/t01e5ad98e88448b7f3.png)

图【15】 Solarwinds供应链攻击流程示意图

Solarwinds Orion产品构建过程中替换的恶意源代码SolarWinds.Orion.Core.BusinessLayer\BackgroundInventory\InventoryManager.cs在Sunburst后门组件中的反编译表现如下：

[![](https://p3.ssl.qhimg.com/t017a3df61bbc11ca2e.png)](https://p3.ssl.qhimg.com/t017a3df61bbc11ca2e.png)

图【16】 Sunburst InventoryManager.cs反编译

Sunburst后门检测真实用户环境之后，动态解密ZIP+Base64存储的配置信息后，使用DGA域名算法组合多级域名前段部分生成C&amp;C回连域名，然后进入RAT分发函数进行C&amp;C交互。

[![](https://p5.ssl.qhimg.com/t01a5fd7d45c7d8b3cf.png)](https://p5.ssl.qhimg.com/t01a5fd7d45c7d8b3cf.png)

图【17】 Sunburst ZIP+Base64编码C&amp;C配置信息

[![](https://p3.ssl.qhimg.com/t01fed173fea9d93252.png)](https://p3.ssl.qhimg.com/t01fed173fea9d93252.png)

图【18】 Sunburst RAT分发

Solarwinds供应链攻击事件披露之后，MSTIC、FireEye以及其他安全机构陆续披露了多个Nobelium攻击组件，包括Teardrop、Raindrop自定义的Cobalt Strike加载器，Goldmax后门，GoldFinder HTTP跟踪器工具，Sibot下载器以及早期的EnvyScout、BoomBox等dropper组件。对该系列组件的调查发现Nobelium发起的一系列鱼叉邮件攻击事件，攻击目标为美国智库、非营利组织、公共部门、石油和天然气、化学和酒店行业的教育机构和私营部门公司。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0191f6d1bf6d0c3b95.png)

图【19】 引自MSTIC、Fire Eye，Nobelium鱼叉邮件

关注“微步在线研究响应中心”可及时了解《APT29—觊觎全球情报的国家级黑客组织》中、下篇精彩内容。
