> 原文链接: https://www.anquanke.com//post/id/251939 


# APT29—觊觎全球情报的国家级黑客组织（三）


                                阅读量   
                                **33949**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01bd04e6f791c8bc8b.jpg)](https://p3.ssl.qhimg.com/t01bd04e6f791c8bc8b.jpg)



## 六、关键TTPS剖析

APT29自2008年开始活跃，至今已活跃13年时间，与同属俄罗斯政府背景的Turla组织处于同一历史舞台，其凭借长时间的攻击战术演进以及网络武器库积累在国际情报窃取领域中处于较高地位。鉴于其TTPS指纹的复杂性，本章节仅探讨部分较为独特且“有趣的”指纹特征。

### **6.1 落地环境检测**

在绝大多数的APT攻击活动中，落地攻击载荷会对当前PC环境进行探测，以决定是否进行或调整后续攻击行为，比如杀软检测、虚拟机检测、安全分析工具检测等等。在早期的The Dukes系列工具集中，存在一种应用简单的数理统计思维的检测方式，在环境检测代码中，设置一个初始为0的score变量，然后逐一检测是否存在杀软产品、是否处于虚拟环境、是否存在安全工具、是否包含异常PC用户名称、是否存在异常文件名称，如任一匹配，则score加上对应权值，待检测代码执行之后将score指与给定阈值进行比较，以此判断当前环境是否为目标环境。其代码实现如下图所示：

[![](https://p2.ssl.qhimg.com/t019ed1606a071952ef.png)](https://p2.ssl.qhimg.com/t019ed1606a071952ef.png)

图【36】 The Dukes工具集PC环境检测

### **6.2 木马上线延时**

通过特定算法计算休眠时间实现木马上线延时是核心APT特马隐藏自身行为的一种有效方法。APT29自研的Sunburst木马在初始化之后进行12-14天的休眠。

[![](https://p5.ssl.qhimg.com/t015fdffb9483f934bd.png)](https://p5.ssl.qhimg.com/t015fdffb9483f934bd.png)

图【37】 Sunburst休眠时间计算

### **6.3 网络C&amp;C托管**

在The Dukes系列工具集中，MiniDuke、CozyDuke、OnionDuke、HammerDuke、PolyglotDuke等组件均会使用Twitter社交平台托管攻击C&amp;C地址，以PolyglotDuke下载器组件为例，下载器落地后先解密特定Twitter URL，然后请求该URL获取特定分隔符之间的流数据，对其进行解密处理得到真实的C&amp;C地址。攻击者提前准备的Twitter动态信息如下：

[![](https://p4.ssl.qhimg.com/t01e1058021c8522a66.png)](https://p4.ssl.qhimg.com/t01e1058021c8522a66.png)

图【38】引自ESET报告，使用Twitter托管加密C&amp;C配置信息

### **6.4图像隐写术**

使用图像隐写术进行攻击指令或攻击载荷下发是一种有效对抗流量检测设备的方法。常见的图像隐写术是通过在各个像素（每个像素二进制数据共24bit，红绿蓝三元素依次各占据8bit）的各字节低位填充隐藏数据，解密代码通过提取各隐藏数据进行拼接解密处理得到真实载荷，而对像素中三色素进行小数值范围内改动并不会明显改变图片质量。APT29组件中RegDuke即是通过这种方式实现攻击载荷传递。参考ESET绘制的像素嵌入结构如下：

[![](https://p0.ssl.qhimg.com/t01f899ffbec82c02e2.png)](https://p0.ssl.qhimg.com/t01f899ffbec82c02e2.png)

图【39】引自ESET，RegDuke图像隐写结构

RegDuke历史使用的PNG图像载体及隐藏数据提取代码如下：

[![](https://p3.ssl.qhimg.com/t0155e43b0b5a314ba5.png)](https://p3.ssl.qhimg.com/t0155e43b0b5a314ba5.png)

图【40】引自ESET，PNG图像载体及隐藏数据提取

### **6.5 应用协议加密算法**

在APT29的武器库组件中，自定义加密算法随处可见，特马C&amp;C交互流量加密协议设计往往也是组织归因的重点部分。以APT29的WellMess特马为例，该木马通过HTTP header的Cookie字段传输C&amp;C指令，加密方式选用RC6+Base64+垃圾数据混淆的组合方式进行加密编码，RC6密钥多通过硬编码形式存在于木马二进制文件之中，C&amp;C交互过程中的AES密钥更新也是在新密钥RSA公钥加密后通过Cookie字段进行传输。其算法结构及加密数据如下所示：

[![](https://p2.ssl.qhimg.com/t01422754f7442a67e9.png)](https://p2.ssl.qhimg.com/t01422754f7442a67e9.png)

图【41】 WellMess C&amp;C通信流量加密协议



## 七、黑客画像

基于微步情报局对APT29组织的追踪积累以及国内外友商披露信息，我们对APT29组织进行画像。梳理其组织背景及攻击偏好如下表所示：

Table 4 APT29组织概述
<td class="ql-align-center" data-row="1">名称</td><td class="ql-align-center" data-row="1">APT29、 Dark Halo、StellarParticle、HAMMERTOSS、NOBELIUM、UNC2452、YTTRIUM、The Dukes、Cozy Bear、CozyDuke、Office Monkeys。</td>
<td class="ql-align-center" data-row="2">时间线</td><td class="ql-align-center" data-row="2">2015年由FireEye披露，最早活动时间可追溯至2008年。</td>
<td class="ql-align-center" data-row="3">背景</td><td class="ql-align-center" data-row="3">具有俄罗斯政府支持背景，疑似归属于俄罗斯联邦对外情报局（SVR）。</td>
<td class="ql-align-center" data-row="4">攻击目标</td><td class="ql-align-center" data-row="4">攻击目标覆盖欧洲、北美、亚洲、非洲等全球较多地区和国家，主要攻击目标为包含美国、英国等在内的北约成员国以及欧洲地域邻近国家，具体攻击行业目标为政府实体、科研机构、智囊团、军工单位、高技术企业、教育机构、医疗机构、通信基础设施供应商等。</td>
<td class="ql-align-center" data-row="5">攻击目的</td><td class="ql-align-center" data-row="5">网络监听、高价值情报窃取。</td>
<td class="ql-align-center" data-row="6">攻击方式</td><td class="ql-align-center" data-row="6">Web渗透入侵、鱼叉攻击、供应链攻击、网络中间人攻击。</td>
<td class="ql-align-center" data-row="7">鱼叉载荷类型</td><td class="ql-align-center" data-row="7">漏洞文档、宏文档、伪装安装包、LNK 文件、ISO镜像。</td>
<td class="ql-align-center" data-row="8">曾使用漏洞</td><td class="ql-align-center" data-row="8">CVE-2010-0232、CVE-2013-0640、CVE-2013-0641、CVE-2018-13379、 CVE-2019-1653、 CVE-2019-2725、CVE-2019-9670、CVE-2019-11510、CVE-2019-19781、CVE-2019-7609、CVE-2020-4006、CVE-2020-5902、CVE-2020-14882、CVE-2020-0688、CVE-2021-28310、CVE-2021-21972、CVE-2021-26855、CVE-2021-26857、CVE-2021-26858、CVE-2021-27065</td>
<td class="ql-align-center" data-row="9">武器库木马</td><td class="ql-align-center" data-row="9">包括开源工具、自研特马等，见下表梳理。</td>
<td class="ql-align-center" data-row="10">三句话描述</td><td class="ql-align-center" data-row="10">1、攻击目标广泛，覆盖全球多数国家，用于高价值情报收集。2、供应商软件构建过程投毒的经典供应链攻击案例，具备策划重大攻击活动的能力。3、俄罗斯背景王牌网军队伍。</td>

基于前文组织结构划分部分内容，对APT29三大分支特有的攻击偏好及活跃时间总结如下：

Table 5 APT29三大分支概述
<td class="ql-align-center" data-row="1">**名称**</td><td class="ql-align-center" data-row="1">**活跃时间**</td><td class="ql-align-center" data-row="1">**描述**</td>
<td class="ql-align-center" data-row="2">**The Dukes**</td><td class="ql-align-center" data-row="2">2008年至2019年10月</td><td class="ql-align-center" data-row="2">**攻击目标倾向**：以俄罗斯西、南方向地缘邻国和美国为主，辐射全部欧洲国家、北约成员国、多数中东地区国家、部分亚非国家。以政府实体、国家智库等行业目标为主。**代表性攻击事件**：2016年美国总统大选期间对美国民主党相关机构的攻击。**攻击战术倾向**：鱼叉邮件攻击，windows平台攻击为主。</td>
<td class="ql-align-center" data-row="3">**WellMess**</td><td class="ql-align-center" data-row="3">2018年6月至今</td><td class="ql-align-center" data-row="3">**攻击目标倾向**：以英国、美国、加拿大为主，覆盖政府、医疗、科研机构、高校、高科技企业等行业目标。**代表性攻击事件**：2020年7月针对COVID-19 疫苗研制机构的间谍活动。**攻击战术倾向**：网络渗透攻击，Windows、Linux双平台攻击。</td>
<td class="ql-align-center" data-row="4">**Nobelium**</td><td class="ql-align-center" data-row="4">2018年11月至今</td><td class="ql-align-center" data-row="4">**攻击目标倾向**：以美国、加拿大、英国为主的欧美地区国家，侧重于高政权、高市值机构，覆盖政府、军工、航空航天、能源、高科技企业等行业，用于窃取高价值情报信息。**代表性攻击事件**：Solarwinds供应链攻击。**攻击战术倾向**：鱼叉邮件攻击，供应链攻击，0day漏洞利用。</td>

总结APT29历史攻击活动中投入使用的武器库资产如下：

Table 6 APT29武器库资产梳理:
<td class="ql-align-center" data-row="1">**组件名称**</td><td class="ql-align-center" data-row="1">**功能描述**</td>
<td class="ql-align-center" data-row="2">**PinchDuke**</td><td class="ql-align-center" data-row="2">由多个加载器和一个窃密木马组成，邮箱/浏览器凭证窃取。</td>
<td class="ql-align-center" data-row="3">**GeminiDuke**</td><td class="ql-align-center" data-row="3">由一个窃密模块、一个加载器和多个持久化组件组成。计算机配置信息收集。</td>
<td class="ql-align-center" data-row="4">**CosmicDuke**</td><td class="ql-align-center" data-row="4">窃密木马，多由其他组件释放。</td>
<td class="ql-align-center" data-row="5">**MiniDuke**</td><td class="ql-align-center" data-row="5">由多个下载器和后门模块组成。部分版本采用汇编语言开发，通过Twitter平台获取C&amp;C地址。</td>
<td class="ql-align-center" data-row="6">**CozyDuke**</td><td class="ql-align-center" data-row="6">多功能平台化工具集，支持后门、下载器、域密码窃取、截屏、信息收集等功能。</td>
<td class="ql-align-center" data-row="7">**OnionDuke**</td><td class="ql-align-center" data-row="7">该工具集通过Tor出口节点传播，由多个功能模块组成。</td>
<td class="ql-align-center" data-row="8">**PolyglotDuke**</td><td class="ql-align-center" data-row="8">下载器，使用了来自不同语言的字符集来编码C&amp;C地址。C&amp;C地址通过公开网页加密托管。</td>
<td class="ql-align-center" data-row="9">**LiteDuke**</td><td class="ql-align-center" data-row="9">高阶后门，使用SQLite存储配置信息、图像隐写术。</td>
<td class="ql-align-center" data-row="10">**SeaDuke**</td><td class="ql-align-center" data-row="10">简单后门，文件上传下载、shell，由python开发设计。</td>
<td class="ql-align-center" data-row="11">**HammerDuke**</td><td class="ql-align-center" data-row="11">简单后门，类似SeaDuke，采用.Net开发，通过Twitter平台获取C&amp;C地址。</td>
<td class="ql-align-center" data-row="12">**CloudDuke**</td><td class="ql-align-center" data-row="12">多功能木马组件，一些版本使用Microsoft OneDrive作为C&amp;C。</td>
<td class="ql-align-center" data-row="13">**FatDuke**</td><td class="ql-align-center" data-row="13">定制化后门，功能复杂。</td>
<td class="ql-align-center" data-row="14">**RegDuke**</td><td class="ql-align-center" data-row="14">持久化后门组件，.Net开发，WMI持久化，使用注册表作为进程通信渠道。</td>
<td class="ql-align-center" data-row="15">**WellMess**</td><td class="ql-align-center" data-row="15">自研木马，采用go、.Net，针对Windows、Linux双平台。</td>
<td class="ql-align-center" data-row="16">**WellMail**</td><td class="ql-align-center" data-row="16">自研木马，采用go、.Net，针对Windows、Linux双平台。</td>
<td class="ql-align-center" data-row="17">**SoreFang**</td><td class="ql-align-center" data-row="17">自研后门，信息收集、shell。</td>
<td class="ql-align-center" data-row="18">**Sliver**</td><td class="ql-align-center" data-row="18">开源远控木马。</td>
<td class="ql-align-center" data-row="19">**SunSpot**</td><td class="ql-align-center" data-row="19">Solarwidns供应链攻击中用于劫持Orion构建过程投毒的定制木马。</td>
<td class="ql-align-center" data-row="20">**Sunburst**</td><td class="ql-align-center" data-row="20">Solarwidns供应链攻击中植入的定制后门。</td>
<td class="ql-align-center" data-row="21">**BoomBox**</td><td class="ql-align-center" data-row="21">恶意下载程序。下载器负责下载和执行感染的下一阶段组件。这些组件是从 Dropbox 下载的（使用硬编码的 Dropbox Bearer/Access 令牌）。</td>
<td class="ql-align-center" data-row="22">**VaporRage**</td><td class="ql-align-center" data-row="22">shellcode 加载器，被视为第三阶段的有效载荷。VaporRage 可以完全在内存中下载、解码和执行任意载荷。</td>
<td class="ql-align-center" data-row="23">**EnvyScout**</td><td class="ql-align-center" data-row="23">一种恶意dropper，能够对恶意 ISO 文件进行反混淆并将其写入磁盘。</td>
<td class="ql-align-center" data-row="24">**NativeZone**</td><td class="ql-align-center" data-row="24">加载器。</td>
<td class="ql-align-center" data-row="25">**GoldMax**</td><td class="ql-align-center" data-row="25">Go 编写，远控木马。</td>
<td class="ql-align-center" data-row="26">**Sibot**</td><td class="ql-align-center" data-row="26">一种用VBScript实现的双用途恶意软件。它旨在实现在受感染机器上的持久性，然后从远程 C2 服务器下载并执行有效负载。VBScript 文件被赋予一个模拟合法 Windows 任务的名称，它要么存储在受感染系统的注册表中，要么以混淆格式存储在磁盘上。然后通过计划任务运行 VBScript。</td>
<td class="ql-align-center" data-row="27">**GoldFinder**</td><td class="ql-align-center" data-row="27">Go 编写的工具，最有可能用作自定义 HTTP 跟踪器工具，用于记录数据包到达硬编码 C2 服务器所需的路由或跳数。</td>
<td class="ql-align-center" data-row="28">**TearDrop**</td><td class="ql-align-center" data-row="28">定制加载器，常用于加载 CobaltStrike木马。</td>
<td class="ql-align-center" data-row="29">**Rain**</td><td class="ql-align-center" data-row="29">定制加载器，常用于加载 CobaltStrike木马。</td>
<td class="ql-align-center" data-row="30">**China Chopper**</td><td class="ql-align-center" data-row="30">开源webshell木马。</td>
<td class="ql-align-center" data-row="31">**Cobalt Strike**</td><td class="ql-align-center" data-row="31">高级商业远控木马。</td>
<td class="ql-align-center" data-row="32">**AdFind**</td><td class="ql-align-center" data-row="32">开源工具，域信息收集。</td>
<td class="ql-align-center" data-row="33">**Gost**</td><td class="ql-align-center" data-row="33">开源工具，端口转发。</td>
<td class="ql-align-center" data-row="34">**Mimikatz**</td><td class="ql-align-center" data-row="34">开源内网密码爬取工具。</td>
<td class="ql-align-center" data-row="35">**PsExec**</td><td class="ql-align-center" data-row="35">PsExec是免费的Microsoft工具，可用于在另一台计算机上执行程序。它由IT管理员和攻击者使用。</td>

参考MITRE ATT&amp;CK对APT29的ATT&amp;CK画像如下：

[![](https://p5.ssl.qhimg.com/t01deef4e6485688d1d.png)](https://p5.ssl.qhimg.com/t01deef4e6485688d1d.png)

图【42】引自https://attack.mitre.org/groups/G0016/
