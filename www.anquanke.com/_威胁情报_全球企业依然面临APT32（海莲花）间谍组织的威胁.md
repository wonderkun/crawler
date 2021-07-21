> 原文链接: https://www.anquanke.com//post/id/86101 


# 【威胁情报】全球企业依然面临APT32（海莲花）间谍组织的威胁


                                阅读量   
                                **129902**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2017/05/cyber-espionage-apt32.html](https://www.fireeye.com/blog/threat-research/2017/05/cyber-espionage-apt32.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p3.ssl.qhimg.com/t019d63caef1addc8bb.jpg)](https://p3.ssl.qhimg.com/t019d63caef1addc8bb.jpg)**

****

作者：[**興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

**稿费：200RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

**作为网络间谍组织的一员，APT32组织（海莲花组织，OceanLotus Group）正在对横跨多个行业的企业展开入侵活动，同时他们也将外国政府、政客人士以及记者当作攻击目标。**FireEye经过分析研究，认为APT32在攻击活动中使用了一个独特的全功能版的恶意软件工具集以及公开的商业工具，所涉及的网络攻击活动都与越南的国家利益相符合。

<br>

**二、APT32与FireEye的响应机制**

FireEye的Mandiant应急响应小组对几家被入侵的公司进行了调查（这几家公司都在越南国内存在商业利益），在调查过程中，我们发现了许多攻击痕迹以及攻击者控制的基础设施，这些信息反应攻击活动由一个大型的组织所主导。为了实时保护FireEye的客户，我们于2017年3月成立了一个社区保护事件（Community Protection Event，CPE）机制。

在之后的几周时间内，FireEye发布了威胁感知产品，向客户推送了更新版的恶意软件库，同时也在研发针对APT32所用工具和钓鱼文件的最新检测技术。经过这些努力，我们新发现了其他一些受害者，同时拥有了足够的技术证据，可以将之前的12个入侵活动联系在一起，将之前认为毫无关系的4个攻击活动整合到我们最新命名的高级持续威胁组织中：即APT32组织。

<br>

**三、APT32针对东南亚的私营公司发起攻击**

至少从2014年起，FireEye就已经观察到APT32的目标中包括那些涉及越南制造业、消费品行业以及酒店行业的外资公司。此外，有迹象表明，APT32组织正在瞄准与外国投资者有联系的那些公司，包括外围网络安全公司、技术型基础设施运维公司以及其他咨询类公司。

FireEye之前调查到的与APT32有关的入侵活动包括：

1、2014年，一家欧洲公司准备在越南建厂，厂房尚未建成便被攻陷。

2、2016年，涉及网络安全、技术型基础设施、银行、媒体行业的越南公司和外资公司均遭受到攻击。

3、2016年年中，APT32专用的一款恶意软件在某家全球酒店行业开发商的网络中被检测到，这家开发商正准备将业务扩张到越南。

4、从2016年到2017年，APT32盯上了美国和菲律宾的两家从事消费品行业的子公司，这两家子公司都位于越南国内。

5、2017年，某家全球咨询公司在越南的办事处被APT32攻陷。

表1描述了APT32的详细攻击活动，每次活动所使用的恶意软件也包含在内：

[![](https://p5.ssl.qhimg.com/t0106a96488dd2176d0.png)](https://p5.ssl.qhimg.com/t0106a96488dd2176d0.png)

[![](https://p0.ssl.qhimg.com/t01947d6f7544579301.png)](https://p0.ssl.qhimg.com/t01947d6f7544579301.png)

表1. APT32瞄准私营企业

<br>

**四、APT32针对有政治影响力的个人、组织和外国政府发起攻击**

除了关注与越南有关的私营企业之外，至少从2013年起，APT32也关注外国政府、越南籍的政治异见人士和记者。相关的攻击活动如下：

1、电子前沿基金会（Electronic Frontier Foundation）公布的一篇[博客](https://www.eff.org/deeplinks/2014/01/vietnamese-malware-gets-personal)表明，记者、活动家、政客人士和博客作者在2013年遭受过APT32的攻击。

2、2014年，APT32以散落在东南亚的越南籍异见人士为目标，发送了钓鱼邮件，附件名为“对越南大使馆抗议者的打击计划.exe”。此外，同样是在2014年，APT32也针对西方国家的立法机构发起过攻击。

3、2015年，奇虎360公司的安全研究部门，天眼实验室发布了一份[安全报告](http://blogs.360.cn/blog/oceanlotus-apt)，详细介绍了海莲花组织专门针对中国政府、科研院所、海事机构、海域建设、航运企业等相关重要领域发起攻击。报告中的资料表明，攻击者使用了与APT32相同的恶意软件、重叠的基础设施以及类似的目标。

4、2015年和2016年，两个越南媒体机构遭受攻击，所涉及的恶意软件与FireEye识别的APT32专用软件一致。

5、2017年，攻击者使用了社会工程学方式，相关证据反应攻击者的目标是移居到澳大利亚的越南籍人士以及菲律宾政府雇员。

<br>

**五、APT32的攻击手段**

在目前的攻击活动中，APT32会通过社会工程学手段，诱骗用户启用ActiveMime文件的宏功能。一旦宏启用并执行后，就会从远程服务器上下载多个恶意载荷。APT32攻击者会通过钓鱼邮件继续投放恶意附件。

针对不同的受害者，APT32定制了不同的诱骗文件。虽然这些文件都具有“.doc”扩展名，但恢复钓鱼文件后，我们发现这些文件实际上是ActiveMine类型的“.mht”格式的Web页面，页面中包含文本以及图片。这些文件很有可能是通过将Word文档导出为单个网页来创建的。

部分已还原的APT32钓鱼附件如表2所示，附件覆盖多种语言：

[![](https://p1.ssl.qhimg.com/t01bc8127511fd06a43.png)](https://p1.ssl.qhimg.com/t01bc8127511fd06a43.png)

[![](https://p0.ssl.qhimg.com/t01675420960f834c80.png)](https://p0.ssl.qhimg.com/t01675420960f834c80.png)

表2. APT32钓鱼文件样例

经过base64编码的ActiveMine数据中还包含了一个带有恶意宏的OLE文件。打开这个文件时，许多钓鱼文件会向用户显示错误信息，试图诱骗用户启用恶意宏。如图1所示，攻击者使用某个虚假的Gmail主题，配合16进制错误代码，试图诱骗收件人启用文档内容以解决这个错误。如图2所示，另一个APT32钓鱼文件使用虚假的Windows错误信息，诱骗收件人启用宏以正确显示文档字体。

[![](https://p2.ssl.qhimg.com/t0121440825c417726c.png)](https://p2.ssl.qhimg.com/t0121440825c417726c.png)

图1. 虚假的Gmail错误信息

[![](https://p2.ssl.qhimg.com/t01058af20c434ea0a8.png)](https://p2.ssl.qhimg.com/t01058af20c434ea0a8.png)

图2. 虚假的文本编码错误信息

APT32攻击者使用了几种新颖的技术，以跟踪他们钓鱼行动的成果、监控他们恶意文档的分发情况、建立驻留机制以便动态更新注入到内存中的后门。

为了实时跟踪谁打开了钓鱼邮件、查看了链接以及下载了附件，APT32使用了针对销售行业的基于云的邮件分析软件。在某些情况下，APT32放弃了直接的邮件附件方式，将ActiveMime钓鱼文件托管在外部的合法云存储服务上，并且完全依赖这种跟踪技术开展攻击。

APT32使用了ActiveMime文档中的原生Web页面功能，其中链接指向托管于APT32基础设施上的外部图片，以进一步掌握钓鱼文件的动向。

如图3所示，APT32在某个钓鱼文件中，使用了HTML图片标签，用来进一步跟踪钓鱼文件动向。

[![](https://p0.ssl.qhimg.com/t01bd85f62b89c0065a.png)](https://p0.ssl.qhimg.com/t01bd85f62b89c0065a.png)

图3. 包含HTML图片标签的钓鱼文件

当打开此类文档时，即便宏功能被禁用，微软Word也会尝试下载外部图片。在我们所分析的所有钓鱼文档中，文档所链接的外部图片均不存在。Mandiant怀疑APT32是根据Web日志来跟踪远程图片所指向的公共IP地址。结合电子邮件跟踪软件，APT32能够密切跟踪钓鱼文件的分发情况、成功率，同时也能够监控安全公司的关注点，进一步分析受害者组织。

一旦目标系统启用了宏功能，恶意宏就会在已感染系统上为两个后门创建两个计划任务，以实现后门的本地驻留。第一个计划任务会启动某个应用白名单脚本保护绕过程序，执行一个COM脚本，以便从APT32的基础设施上动态下载第一个后门，并将该后门注入到内存中。第二个计划任务通过XML文件形式加载，以伪造任务的属性，然后运行某个JavaScript代码片段，下载并启动第二个后门，该后门为多阶段的PowerShell脚本。在大多数钓鱼文件中，这两个后门一个为APT32专有的后门，另一个为备份的商用后门。

为了分析这类钓鱼文件的复杂性，我们以某个钓鱼文件为例。我们恢复了APT32的某个钓鱼文件，该文件所创建的两个计划任务如图4所示。

[![](https://p5.ssl.qhimg.com/t011ec40dfda777ef09.png)](https://p5.ssl.qhimg.com/t011ec40dfda777ef09.png)

图4. APT32 ActiveMime钓鱼文件创建两个计划任务

对于这个案例，该恶意文件创建了一个名为“Windows Scheduled Maintenance”的计划任务，每隔30分钟运行一次Casey Smith写的[“Squiblydoo”应用白名单绕过程序](http://subt0x10.blogspot.com/2016/04/bypass-application-whitelisting-script.html)。所有的载荷都可以动态更新，在载荷投放时，该计划任务会启动一个COM小程序（scriptlet）,下载并执行托管在“images.chinabytes[.]info”上的Meterpreter载荷。Meterpreter载荷会加载并配置Cobalt Strike BEACON工具，使用[可扩展的Safebrowing配置文件](https://github.com/rsmudge/Malleable-C2-Profiles/blob/master/normal/safebrowsing.profile)与80.255.3[.]87地址进行通信，以进一步将恶意网络流量融入正常流量中。第二个计划任务名为“Scheduled Defrags”，APT32通过加载原始的任务XML文件创建该任务，任务的创建时间被伪造为2016年6月2日。第二个计划任务会每隔50分钟运行一次“mshta.exe”，启动APT32专有的一个后门，该后门为PowerShell脚本中的shellcode，用来与“blog.panggin[.]org”、“ share.codehao[.]net”以及“yii.yiihao126[.]net”进行通信。

如图5显示了某个APT32钓鱼文件感染成功后的执行流程，钓鱼文件会将两个多阶段的恶意软件框架动态注入到内存中。

[![](https://p0.ssl.qhimg.com/t016f5db06473e78e58.png)](https://p0.ssl.qhimg.com/t016f5db06473e78e58.png)

图5. APT32钓鱼文件执行流程

在受害者环境中站稳脚跟后，APT32并不会停止攻击过程。Mandiant的多次调查结果表明，APT32在获取访问权限之后，会定期清除某些事件日志条目，并且使用Daniel Bohannon的[Invoke-Obfuscation](https://github.com/danielbohannon/Invoke-Obfuscation)框架对基于PowerShell的工具和shellcode加载器进行高度混淆处理。

APT32经常使用隐身技术将攻击行为隐藏在合法的用户活动中：

1、在某次调查中，我们发现APT32使用了伪装为Windows更新包的一个权限提升漏洞（CVE-2016-7255）利用工具。

2、在另一次调查中，我们发现APT32控制并利用了McAfee ePO软件，以ePO的软件部署任务形式分发他们的恶意软件，所有部署该软件的系统都会使用ePO专用的协议从ePO服务器上提取载荷，从而实现恶意软件的投递。

3、APT32还使用了隐藏的或不可打印的字符以便在系统中隐藏他们的恶意软件。比如，APT32在系统中安装了某个服务以实现后门的驻留，该服务名末尾包含一个Unicode的不可中断的（no-break，即宽度不能被压缩）空格字符。另一个后门使用了某个合法的DLL文件名，文件名中包含不可打印的系统命令控制代码。

<br>

**六、APT32的恶意软件及基础架构**

APT32貌似具备强大的研发能力，使用了一套定制的跨协议的后门套件。我们可以通过恶意软件载荷特征识别APT32，这些恶意载荷包括WINDSHIELD、KOMPROGO、SOUNDBITE以及PHOREAL。APT32经常将这些后门与商用的Cobalt Strike BEACON后门一起部署。APT32对macOS也具备[后门部署](https://www.alienvault.com/blogs/labs-research/oceanlotus-for-os-x-an-application-bundle-pretending-to-be-an-adobe-flash-update)能力。

APT32专用的恶意软件族群如表3所示：

[![](https://p2.ssl.qhimg.com/t01e91717475fdbd1c2.png)](https://p2.ssl.qhimg.com/t01e91717475fdbd1c2.png)

[![](https://p4.ssl.qhimg.com/t0140f41289c7bc5714.png)](https://p4.ssl.qhimg.com/t0140f41289c7bc5714.png)

[![](https://p3.ssl.qhimg.com/t0174e0e937bd19ae27.png)](https://p3.ssl.qhimg.com/t0174e0e937bd19ae27.png)

表3. APT32的恶意软件及功能

APT32组织貌似获得了充足的资源保障及支持，他们拥有大量的域名和IP地址，使用这些资源作为命令控制的基础设施。在Mandiant对APT32入侵活动调查的基础上，FireEye的[iSIGHT](https://www.fireeye.com/products/isight-intelligence.html)服务收集整理了这些后门族群的更多信息。

在整个攻击生命周期的各个阶段中，APT32使用了不同的攻击工具，如图6所示。

[![](https://p2.ssl.qhimg.com/t01e7db3d816c4104e7.png)](https://p2.ssl.qhimg.com/t01e7db3d816c4104e7.png)

图6. APT32攻击周期

<br>

**七、展望及启示**

综合应急响应调查结果、产品检测结果、对同一攻击组织的其他公开情报整理结果，FireEye认为APT32这个网络间谍组织与越南政府的利益密切相关。APT32对私营企业的攻击意图值得我们注意，FireEye认为这个组织对拟在越南开展业务或准备投资的公司构成重大威胁。虽然APT32攻击各个目标的意图有所不同，并且在某些情况下其意图尚未明确，但这类未授权访问可以作为一个平台，作为强制执法、知识产权窃取以及反腐败手段来发挥作用，最终削弱目标组织的竞争优势。此外，APT32还威胁到东南亚和全球公共部门的政治活动和言论自由，各国政府、记者以及越南移民也是该组织的攻击目标。

虽然FireEye依然将来自中国、伊朗、俄罗斯和朝鲜的黑客组织作为密切关注的网络威胁对象，但APT32反映出越来越多的新兴国家也具备了这种动态威胁能力。APT32向我们展示了如何使用适当的工具以获取可靠及可怕的攻击实力，以及如何使用新兴工具及技术以获取灵活的攻击能力。随着越来越多的国家开始使用廉价且高效的网络攻击手段，公众也需要提高对这类威胁的认识，重新审视这类新兴的国家级入侵活动。

<br>

**八、如何检测APT32**

我们可以使用图7所示的Yara规则检测与APT32钓鱼文件有关的恶意宏：

[![](https://p2.ssl.qhimg.com/t01a8f2517dfd894d4c.png)](https://p2.ssl.qhimg.com/t01a8f2517dfd894d4c.png)

图7. 检测APT32恶意宏的Yara规则

FireEye整理了与APT32的C2服务器有关的一份表格，如表4所示：

[![](https://p0.ssl.qhimg.com/t01974c92a1aeb4b697.png)](https://p0.ssl.qhimg.com/t01974c92a1aeb4b697.png)

表4. APT32的C2服务器基础设施样例
