> 原文链接: https://www.anquanke.com//post/id/250713 


# APT29—觊觎全球情报的国家级黑客组织（二）


                                阅读量   
                                **22872**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01bd04e6f791c8bc8b.jpg)](https://p3.ssl.qhimg.com/t01bd04e6f791c8bc8b.jpg)

> 注：本篇报告内容较长，将分为上、中、下三篇发布，本文为**中**篇。

## 五、关联归因

攻击事件关联归因是APT组织追踪溯源过程中非常重要的环节，同时也是高级威胁事件调查的最终目的。当前复杂多变的网络战环境以及各安全机构情报信息差异问题均给归因工作提出挑战。所谓的归因只是站在独立立场尽可能客观地去描述攻击者背景。出于多数APT攻击事件中特有的国际政治局势下的攻击倾向，对被攻击目标国家的政治敌对（或外交不友好）国家尝试关联验证往往是比较有用的初步关联归因思路。此外，基于恶意代码指纹、网络资产特征、攻击TTPS等维度向已知背景组织挂靠是比较常见有效的归因办法。

在对APT29组织的研究过程中，其归因结论主要由美国、英国、加拿大、瑞士等国家情报机构以及其本土安全公司提供，然后其他媒体机构对归因结论进行传播扩散。在公开披露的调查报告中，因为信息涉密问题，多数归因证据进行了阉割脱敏处理。我们在研究梳理APT29关联归因证据过程中，过滤掉以媒体机构为主的主观性较强并且缺乏切实证据的新闻信息，侧重于总结第三方安全机构调查报告中披露的具有指向性的客观线索。

接下来，我们按照本文前部分划分的APT29组织结构分开梳理其关联归因证据。

### **5.1 The Dukes归因**

The Dukes系列是APT29最早的组织代号，早期的Dukes特马工具是在2013年由卡巴斯基安全团队作为未知类型攻击组件进行命名披露的。对于The Dukes系列的归因，我们重点探讨如何将The Dukes归因至俄罗斯政府背景黑客组织，而对于如何将APT29关联到俄罗斯联邦对外情报局（SVR）不在本文讨论范围内。

**5.1.1 受害者分析**

2013年2月，卡巴斯基在“The MiniDuke Mystery: PDF 0-day Government Spy Assembler 0x29A Micro Backdoor”一文中对MiniDuke木马组件以及其参与的攻击事件进行详细披露。该系列攻击活动中，被攻击目标主要为欧洲西部、中部国家。鱼叉网络攻击活动中投入使用的诱饵素材如下。

[![](https://p1.ssl.qhimg.com/t01dcee176121037a08.png)](https://p1.ssl.qhimg.com/t01dcee176121037a08.png)

图【20】引自Kaspersky，2013年Dukes攻击诱饵

在对Dukes 2013年攻击活动的深入调查中，卡巴斯基团队通过分析大量C&amp;C服务器日志，发现该系列攻击活动受害者包括分散在23个国家的59个独立机构，这些国家为：比利时、巴西、保加利亚、捷克共和国、格鲁吉亚、德国、匈牙利、爱尔兰、以色列、日本、拉脱维亚、黎巴嫩、立陶宛、黑山、葡萄牙、罗马尼亚、俄罗斯联邦、斯洛文尼亚、西班牙、土耳其、乌克兰、英国和美国。

2015年9月，F-Secure安全公司在“THE DUKES 7 YEARS OF RUSSIAN CYBERESPIONAGE”（译为：The Dukes 7年的俄罗斯网络间谍活动）报告中继续披露了格鲁吉亚、乌干达、波兰、哈萨克斯坦、吉尔吉斯斯坦、阿塞拜疆、乌兹别克斯坦等国家。

[![](https://p1.ssl.qhimg.com/t01ea8865603721aac2.png)](https://p1.ssl.qhimg.com/t01ea8865603721aac2.png)

图【21】 2008-2009年，Dukes针对波兰、捷克、国美智库攻击活动中诱饵文件

此后的2016年夏季，美国总统大选期间，The Dukes对美国民主党相关机构发起大规模间谍活动。

至此，我们梳理自2008年-2016年期间The Dukes的攻击目标包括几乎全体欧洲国家、部分美洲国家、少数亚非国家，其中主要目标国家为以美国为主的北约成员国和以乌克兰、格鲁吉亚、哈萨克斯坦、阿塞拜疆为代表的欧洲中部国家。结合当时世界各国的情报间谍能力、美俄之间的政治局势以及俄罗斯西南方向敏感的地缘政治关系，The Dukes极有可能具有俄罗斯政府背景。

**5.1.2 特马编译时间时区分析**

F-Secure披露报告中指出，根据The Dukes特马的编译时间戳，恶意软件的作者似乎主要在周一至周五UTC+0时间早上6点到下午4点之间工作。这相当于UTC+3时区（也称为莫斯科标准时间）上午9点到晚上7点之间的工作时间，包括莫斯科和圣彼得堡在内的俄罗斯西部大部分地区。此种基于特马编译时间进行的时区分析为The Dukes归因至俄罗斯提供了佐证。

[![](https://p3.ssl.qhimg.com/t01ba6187def6e048fa.png)](https://p3.ssl.qhimg.com/t01ba6187def6e048fa.png)

图【22】引自F-Secure，UTC+3时区中的莫斯科

**5.1.3  vcaz情报机构调查**

在2016年以干预美国总统大选为目的一系列间谍活动之后，美国国会组织各情报机构及第三方安全公司对该事件进行调查。后续披露的归因至俄罗斯政府的多个报告中，包含了美俄政治局势分析、国家机密泄密事件分析、网络供应商调查分析等。美方提供一系列的调查报告及事件相关人员证词，通过国际司法程序指控俄罗斯组织的这一系列间谍活动。在美方的披露信息中，关于The Dukes的确切归因证据并未展示。我们仅从美国参议院情报特别委员会披露的一份名为“Report of the select committee on intelligence United States senate on Russian active measures campaigns and interference in the 2016 U.S. Election volume 1: Russian efforts against election infrastructure with additional views”的调查报告中找到了一条疑似指向俄罗斯的归因证据。报告中提到：2016年8月18日FLASH（美国联邦安全家园联盟）间谍事件相关的IP地址提供了一些指向俄罗斯政府的迹象，尤其是GRU（俄罗斯总参谋部情报部，简称“格鲁乌”）。

[![](https://p1.ssl.qhimg.com/t018f90d0d86f00f2c5.png)](https://p1.ssl.qhimg.com/t018f90d0d86f00f2c5.png)

图【23】引自美国参议院情报特别委员会调查报告Report_Volume1.pdf，13/67页

上述关联点是当前可公开收集的可初步将The Dukes关联到俄罗斯的论据，虽然美国各情报部门并未披露过多调查细节，但结合国际政治局势及美方提供的众多国际司法指控证据来看，将The Dukes归因至俄罗斯应该是较为合理的。

### **5.2 WellMess归因**

WellMess系列木马在2018年由JPCERT作为一款独立的新型木马披露。2020年，在对英美在内的全球COVID-19疫苗研制机构的网络间谍活动中出现了WellMess的身影，英国、美国、加拿大三国的国家情报机构（NCSC、NSA、CISA、CSE）联合发文将该系列攻击事件归因至具有俄罗斯联邦对外情报局背景的APT29，具体归因点并未披露。外界至今对于将WellMess归因至APT29仍然存在少许争议。

2020年8月，英国普华永道安全咨询公司在“WellMess malware: analysis of its Command and Control (C2) server”一文中给出了部分归因证据，即WellMess与已知APT29 SeaDuke组件在关联，二者均存在使用攻击失陷的第三方网站作为C&amp;C服务器，以及二者在网络通信中使用的数据加密协议较为相似。我们重点注意通信数据加密协议，二者在HTTP协议通信过程中，均会使用header部分的Cookie字段来传输C&amp;C指令，并且在C&amp;C指令的加密逻辑上较为相似。

Table 3 加密协议比较
<td class="ql-align-center" data-row="1">木马组件</td><td class="ql-align-center" data-row="1">HTTP　Header　Cookie字段加密协议</td>
<td class="ql-align-center" data-row="2">**SeaDuke**</td><td class="ql-align-center" data-row="2">C&amp;C指令与临时的前缀hash进行RC4加密，然后Base64编码，填充字符混淆</td>
<td class="ql-align-center" data-row="3">**WellMess**</td><td class="ql-align-center" data-row="3">C&amp;C指令与硬编码密钥进行RC6加密，然后Base64编码，填充字符混淆</td>

分析对比二者HTTP通信中传输的自定义加密数据表现如下，二者非常相似。

[![](https://p3.ssl.qhimg.com/t013bb3a3f197566a43.png)](https://p3.ssl.qhimg.com/t013bb3a3f197566a43.png)

图【24】 SeaDuke与WellMess通信流量

综上，考虑到SeaDuke和WellMess特有的应用层数据加密协议以及使用HTTP header部分Cookie字段传输加密数据的共同偏好，可将该关联点作为将WellMess归因至SeaDuke所属的APT29的强关联论据。

### **5.3 Nobelium归因**

划分Nobelium分支的一个标志性事件是2020年12月曝光的Solarwinds供应链攻击活动，该攻击活动的主要受害者为美国和欧洲国家的政府实体、科研、能源等机构。攻击活动发现之后，美方情报机构联合FireEye、Volexity等第三方安全公司对攻击活动进行深入调查分析。在已披露的调查报告中，其实并没有提供将Solarwinds事件归因至APT29的确切证据，各安全公司多采用私有命名对幕后攻击者进行归类，随后美方政府基于受害者立场下的国际政治局势因素将该事件归因至APT29。准确来讲，是将Solarwinds供应链攻击事件定性为俄罗斯政府背景支持的间谍活动。

微步情报局在深入总结已有情报信息之后，梳理了两条可用于归因的佐证线索：卡巴斯基披露的Sunburst木马（Solarwinds供应链攻击活动中植入的特马）与Kazaur木马（归属于俄罗斯背景的Turla组织的特马）的代码相似性，瑞士安全公司Prodaft在SilverFish组织的调查报告中攻击者背景分析。下面我们分别来论述：

**5.3.1 Sunburst与Kazaur的代码相似性**

Kazuar木马是PaloAltoNetworks 安全公司在2017 年首次报道的 .NET 后门，并将该特马归因至Turla APT组织。两款木马在C&amp;C上线时均采用特定休眠算法实现数周时间的上线延时。二者计算休眠时间算法高度相似，均遵循下述逻辑。

Sunburst木马计算C&amp;C上线延时的休眠时间算法实现如下，延时12到14天。

[![](https://p1.ssl.qhimg.com/t0192dd445e088ac5d6.png)](https://p1.ssl.qhimg.com/t0192dd445e088ac5d6.png)

图【25】 Sunburst休眠时间算法

Kazuar木马计算C&amp;C上线延时的休眠时间算法实现如下，延时14到28天。

[![](https://p0.ssl.qhimg.com/t0130ab2629154f65e7.png)](https://p0.ssl.qhimg.com/t0130ab2629154f65e7.png)

图【26】 Kazuar休眠时间算法

其次，Sunburst和Kazuar特马运行过程中都采用动态方式获取核心函数，通过计算遍历获取的Windows API名称摘要与硬编码值比较来判定，二者均采用自定义修改的FNV-1a哈希算法。FNV哈希算法全名为Fowler-Noll-Vo算法，是以三位发明人Glenn Fowler、Landon Curt Noll、Phong Vo的名字来命名的，最早在1991年提出。FNV-1a摘要算法的标准实现逻辑如下，算法中包含两个初始向量：初始哈希种子offset_basis，迭代相乘的种子FNV_prime。简单描述其逻辑为：从待计算字符串中取出指定步长数据，将取出数据先与初始哈希向量做异或运算，然后将结果与初始乘法种子做乘法运算，将计算结果赋值为初始哈希向量，然后取待计算字符串后续单位数据迭代上述过程，最终得到计算结果。

Sunburst和Kazuar在使用FNV-1a算法时均进行了相同的修改：增加一个新的硬编码key，将标准FNV-1a计算后的哈希最后与该key进行异或运算。

二者在代码层实现如下:

[![](https://p4.ssl.qhimg.com/t012b889cdfe7c8c7fe.png)](https://p4.ssl.qhimg.com/t012b889cdfe7c8c7fe.png)

图【27】 Sunburst改变后的FNV-1a算法

[![](https://p5.ssl.qhimg.com/t01dff0011418f0a73b.png)](https://p5.ssl.qhimg.com/t01dff0011418f0a73b.png)

图【28】 Kazuar改变后的FNV-1a算法

在计算当前PC机器UID标识序列时，Sunburst和Kazuar均采用相同算法（MD5+XOR），即通过既定字符串计算MD5摘要，然后将该散列值与出初始四字节逐字节异或得到最终UID序列。

Sunburst中UID生成算法如下:

[![](https://p0.ssl.qhimg.com/t0188aa6bc84f1f5cfd.png)](https://p0.ssl.qhimg.com/t0188aa6bc84f1f5cfd.png)

图【29】 Sunburst GUID生成算法

Kazuar中GUID生成算法如下:

[![](https://p1.ssl.qhimg.com/t0151f9c51fe2007ffb.png)](https://p1.ssl.qhimg.com/t0151f9c51fe2007ffb.png)

图【30】Kazuar GUID生成算法

客观来看待上述几种加密算法的相似性，其实并不能作为强有力的关联证据，尤其是FNV-1a算法的改编和UID生成算法，因为上述算法相对较为简单，而且对于标准算法的微调存在较大的偶然性。对此，卡巴斯基在披露文章中表述了一个客观的论证前提：基于已有的海量恶意样本库，满足上述算法指纹的样本主要出现在Sunburst和Kazuar特马中，特别是使用NextDouble函数的自定义休眠时间算法。

**5.3.2 SilverFish调查报告**

SilverFish是瑞士安全公司Prodaft对包括Solarwinds供应链攻击事件在内的一系列攻击活动的背后组织的私有命名。在“SilverFish GroupThreat Actor Report”一文中，Prodaft公司PTI威胁情报团队基于成功反制木马主控端后台对Solarwinds供应链攻击活动中的受害者、攻击组织背景、主控端后台资产、攻击者操作日志等进行深入分析披露。该报告也是迄今为止将Solarwinds事件归因至俄罗斯政府的最直接论据来源。本节我们侧重于梳理总结报告中提及的Solarwinds事件归因点。

总结归因点之前，先回顾一下Prodaft成功渗入Solarwinds事件木马主控端后台的流程，这一步也是调查过程中最为关键的一步，虽然过程存在非常大的运气成分。Prodaft团队调查之初，重点分析当时还处于存活状态的攻击者资产“databasegalore.com”，该域名解析至5.252.177.21，在该主机上的2304端口存在PowerMTA邮件服务，同时通过URL路径暴力访问发现存在名为“example.php”的资源文件，基于2304端口的PowerMTA服务和IP:2304/ example.php特征进行网络空间搜索并排除掉无关站点，发现新的攻击者资产81.4.122.203，继续进行同C段的子网调查，分析人员发现81.4.122.101站点存在疑似木马控制端登录页面信息，爆破登录该主机后，经分析验证为Solarwinds事件控制端后台。其流程图绘制如下：

[![](https://p2.ssl.qhimg.com/t01ef6cd4626ebd1612.png)](https://p2.ssl.qhimg.com/t01ef6cd4626ebd1612.png)

图【31】Prodaft渗入Solarwinds事件木马主控端后台的流程

接下来我们将逐一梳理该调查报告中将Solarwinds事件归因至俄罗斯黑客组织的细节：

**5.3.2.1 C&amp;C后台源代码中携带的开发者ID**

在C&amp;C后台的PHP源代码中静态包含14个人的昵称和ID，多数ID曾在俄语地下论团中活跃。该线索可以初步证明攻击者拥有浏览俄语黑客团队的习惯。

[![](https://p1.ssl.qhimg.com/t01de96a955ff86748f.png)](https://p1.ssl.qhimg.com/t01de96a955ff86748f.png)

图【32】摘自Prodaft报告，含黑客ID的PHP代码

**5.3.2.2 C&amp;C后台关于中马机器的俄语信息备注**

C&amp;C后台面板中上线机器一栏均存在名为“Comment”的信息单元格，此位置用于后台操作人员填写关于受控机器信息，当前已存在的备注信息多采用俄语俚语或白话，如“dno”、“pidori”、“poeben”、“poebotina”、“psihi”、“hernya”、“xyeta”、“gavno”。该线索说明C&amp;C后台操作人员具有俄语背景。

[![](https://p0.ssl.qhimg.com/t010e0987eca8febab7.png)](https://p0.ssl.qhimg.com/t010e0987eca8febab7.png)

图【33】摘自Prodaft报告，Comment中的俄语俚语描述信息

**5.3.2.3 流量重定向代码过滤CIS独联体国家受害者**

基于当前C&amp;C后台拓线的其他失陷类型C&amp;C站点上存在用于流量重定向的PHP代码，该代码会过滤掉包含阿塞拜疆、亚美尼亚、白俄罗斯、哈萨克斯坦、吉尔吉斯斯坦、摩尔多瓦、俄罗斯、塔吉克斯坦、土库曼斯坦、乌兹别克斯坦、乌克兰、格鲁吉亚在内的CIS独联体国家的受害者机器回连流量，其中还设置了俄语、乌克兰语等在内的语种过滤条件，对于美国和加拿大不予过滤。代码中使用注释语句为俄语。考虑到Solarwinds供应链攻击事件受害者遍布全球，攻击者在受害者回连流量重定向代码中主动过滤掉非目标的俄语系国家，该行为可作为将Solarwinds供应链攻击事件归因至俄罗斯背景黑客组织的强归因论据。

[![](https://p3.ssl.qhimg.com/t01e3c5f28e4e382fc6.png)](https://p3.ssl.qhimg.com/t01e3c5f28e4e382fc6.png)

图【34】摘自Prodaft报告，重定向流量过滤代码

**5.3.2.4 C&amp;C后台操作行为活跃时间区段**

基于C&amp;C后台操作日志信息，其操作人员的活跃时间集中在周一至周五08：00到20：00（UTC）之间，按照一般的工作时间可大致推测攻击者所处地理位置为0时区至东4区之间，这一点与前文中The Dukes归因部分提到的时区推测基本吻合，可作为将Solarwinds归因至俄罗斯政府黑客的佐证。

[![](https://p2.ssl.qhimg.com/t01979f1c7e0c613f1d.png)](https://p2.ssl.qhimg.com/t01979f1c7e0c613f1d.png)

图【35】 摘自 Prodaft报告，C&amp;C后台操作行为活跃时间区段
