> 原文链接: https://www.anquanke.com//post/id/87209 


# 【技术分享】深入分析REDBALDKNIGHT组织具备隐写功能的Daserf后门


                                阅读量   
                                **107505**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：trendmicro.com
                                <br>原文地址：[http://blog.trendmicro.com/trendlabs-security-intelligence/redbaldknight-bronze-butler-daserf-backdoor-now-using-steganography/](http://blog.trendmicro.com/trendlabs-security-intelligence/redbaldknight-bronze-butler-daserf-backdoor-now-using-steganography/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t012ebd5246795fd69d.jpg)](https://p3.ssl.qhimg.com/t012ebd5246795fd69d.jpg)

译者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**简介**

****

**REDBALDKNIGHT**，又名[BRONZE BUTLER](http://securityaffairs.co/wordpress/64311/apt/bronze-butler-ttps.html)和[Tick](https://www.scmagazine.com/tick-cyberespionage-group-targets-japanese-firms-using-custom-malware/article/528602/)，是一个专门针对日本组织（如政府机构（包括国防机构）以及生物技术、电子制造和工业化学等行业公司）的**网络间谍组织**。他们在从事间谍活动过程中采用的Daserf后门（趋势科技将其标识为BKDR_DASERF，也称为Muirim和Nioupale）具有四个主要功能：**执行shell命令、下载和上载数据、截图以及键盘记录。**

然而，我们最近的遥测数据显示，**Daserf的变种不仅用来执行针对日本和韩国的目标组织的监视和窃取工作，同时还用于对付俄罗斯、新加坡和中国的企业。**此外，我们还发现了Daserf的多种版本，它们不仅采用了不同的技术，而且为了更好地隐藏自己，还通过**隐写术**将代码嵌入到了一些出其不意的媒介或位置（如图像）中。

像多数网络间谍活动一样，REDBALDKNIGHT组织的攻击行为也是间歇性的，只不过它的持续时间要更为久远一些。实际上，**REDBALDKNIGHT**组织早在2008年就已经盯上了日本的相关机构，至少从他们发送给目标的诱饵文档的文件属性来看是这样的。该组织攻击目标的专一性主要反映在其使用的社会工程学策略方面：他们在攻击链中的诱饵文件内容是用流利的日文编写的，尤其是，该文件是通过日文字处理软件Ichitaro创建的。 例如，其中一个诱饵文件是关于“平成20年防灾计划”（平成是日本现今的纪元）的。

 [![](https://p3.ssl.qhimg.com/t018195f3bf70565cf6.jpg)](https://p3.ssl.qhimg.com/t018195f3bf70565cf6.jpg)

图1：REDBALDKNIGHT发送给日本目标机构的一个诱饵文档的文件属性

 [![](https://p0.ssl.qhimg.com/t015653c07a0bce6192.jpg)](https://p0.ssl.qhimg.com/t015653c07a0bce6192.jpg)

图2：REDBALDKNIGHT使用的诱饵文档样本，他们在鱼叉式钓鱼邮件中使用了社会工程类型的标题，如“防灾”

<br>

**攻击链**

REDBALDKNIGHT的攻击活动通常使用鱼叉式钓鱼邮件作为切入点，而这些邮件的附件通常都是夹带了利用Ichitaro漏洞的代码（见后文 ）的文件，也就是所谓的诱饵文件，网络间谍组织通常用它们来引起受害者的注意，具体来说，为了达到执行恶意软件的目的，首先利用“CPR”和“防灾”等诱饵来引受害者上钩。

一旦受害者打开文档，Daserf就会植入目标机器，并开始运行。直到去年安全研究人员公开[曝光](http://blog.jpcert.or.jp/2017/01/2016-in-review-top-cyber-security-trends-in-japan.html)了Daserf之后，该恶意软件才广为人知，但是早在2011年的时候，“江湖”中就有了它们的踪迹。根据他们透露的硬编码版本号（Version：1.15.11.26TB Mini），我们可以找到这个后门的其他版本（见附录）。

 

**不断改进的Daserf**

****

我们的分析显示，Daserf会经常进行技术改进，以绕过传统的反病毒（AV）检测。例如，Daserf的1.50Z、1.50F、1.50D、1.50C、1.50A、1.40D和1.40C版本就使用了加密的Windows应用程序编程接口（API）。 **而该软件的v1.40 Mini版本则使用了MPRESS加壳器，可以在一定程度上绕过AV检测，并能起到对抗逆向分析的作用。** Daserf的1.72及更高版本利用base64+RC4的替代技术来加密反馈数据，而另外一些版本则采用了不同的加密方式，例如1.50Z版本，它使用的是凯撒加密法（它根据字母表将明文中的每个字母移动常量位k，可以向上移动，也可以向下移动。举例来说，如果偏移量k等于3，则在编码后的消息中，可以让每个字母都会向前移动3位：a会被替换为d；b会被替换成e；依此类推。字母表末尾将回卷到字母表开头。于是，w会被替换为z，x会被替换为a。）。

更值得注意的是，REDBALDKNIGHT已经在攻击的第二个阶段中集成了隐写技术，即用于C＆C通信和获取后门。在Daserf的v1.72 Mini和更高版本中，我们就观察到这种技术。Daserf采用隐写术后，不仅可以帮助后门程序绕过防火墙（即Web应用防火墙），同时还使得攻击者能够更快、更方便地更换第二阶段的C＆C通信或后门程序。

 

**REDBALDKNIGHT****如何使用隐写术**

****

如下图所示，在引入隐写术之后，Daserf的感染链也得到了相应发展。当感染感兴趣的目标的时候，方法有许多：鱼叉式钓鱼电子邮件、[水坑攻击](https://www.trendmicro.com/vinfo/us/threat-encyclopedia/web-attack/137/watering-hole-101)以及利用SKYSEA客户端视图（一种在日本广泛使用的IT资产管理软件）中的远程代码执行漏洞（[CVE-2016-7836](https://www.jpcert.or.jp/english/at/2016/at160051.html)，于2017年3月修复）。

 [![](https://p1.ssl.qhimg.com/t01cff9adfd6e63e8c8.jpg)](https://p1.ssl.qhimg.com/t01cff9adfd6e63e8c8.jpg)

图3：Daserf最新的执行和感染流程图

**downloader将被安装到受害者的机器上，并从受感染的站点下载安装Daserf。然后，Daserf会访问另一个被攻陷的站点，并下载一个图像文件（例如.JPG或.GIF格式的文件）。而这个图像中，不是嵌入了加密的后门配置，就是嵌入了加密的黑客工具。解密后，Daserf将连接C＆C，并等待进一步的命令。**Daserf的1.72和更高版本都采用了隐写术。

REDBALDKNIGHT对隐写术的应用并不仅仅限于Daserf后门，除此之外，他们的另外两个工具包-xxmm2_builder和xxmm2_steganography也采用了相同的技术。根据他们的pdb字符串分析，它们都是REDBALDKNIGHT另一个攻击程序（即XXMM（TROJ_KVNDM），一种下载器类型的木马）的组成部分，也可以作为第一阶段的后门程序，因为其具有打开shell的能力。xxmm2_builder使得REDBALDKNIGHT可以自定义XXMM的设置，而xxmm2_ steganography则可以将恶意代码隐藏到图像文件中。

REDBALDKNIGHT的工具可以通过隐写术对字符串进行加密，然后将其嵌入图像文件的标记中，从而实现了在图像文件中创建、嵌入和隐藏可执行文件或配置文件的功能。**这里所说的加密字符串既可以是可执行文件，也可以是URL。**攻击者可以利用隐写术将相关的代码注入现有的图像，然后上传至相应的网站即可。此外，我们还发现，XXMM和Daserf采用的隐写术算法(替代base64+RC4)是一样的。

 [![](https://p0.ssl.qhimg.com/t017c822d36b8cc2b3c.jpg)](https://p0.ssl.qhimg.com/t017c822d36b8cc2b3c.jpg)

图4：Daserf解码函数的代码片段，与XXMM相同

 [![](https://p1.ssl.qhimg.com/t013de8c2a554b1d085.jpg)](https://p1.ssl.qhimg.com/t013de8c2a554b1d085.jpg)

图5：REDBALDKNIGHT在XXMM中使用的Steganography工具包

 [![](https://p5.ssl.qhimg.com/t016e06f34f1d9e95c9.png)](https://p5.ssl.qhimg.com/t016e06f34f1d9e95c9.png)

图6：由Steganography工具包为Daserf生成的隐写式代码的截图

 

**应对措施**

****

在具有针对性的网络攻击中，隐写术是一种特别有用的技术：他们的恶意活动隐蔽的时间越长，他们就越有可能窃取和泄露数据。事实上，人们的日常工作正在面临越来越多的网络恶意软件的影响，这些软件的范围从[exploit工具包](http://blog.trendmicro.com/trendlabs-security-intelligence/updated-sundown-exploit-kit-uses-steganography/)、[恶意广告活动](http://blog.trendmicro.com/trendlabs-security-intelligence/microsoft-patches-ieedge-zeroday-used-in-adgholas-malvertising-campaign/)、[银行木马](http://blog.trendmicro.com/trendlabs-security-intelligence/sunsets-and-cats-can-be-hazardous-to-your-online-bank-account/)、[C＆C通信](http://blog.trendmicro.com/trendlabs-security-intelligence/malware-campaign-targets-south-korean-banks-uses-pinterest-as-cc-channel/)直到[勒索软件](http://blog.trendmicro.com/trendlabs-security-intelligence/picture-perfect-crylocker-ransomware-sends-user-information-as-png-files/)。就REDBALDKNIGHT的网络攻击来看，采用隐写术之后，可以使得恶意软件更加难以检测和分析。

透过REDBALDKNIGHT攻击活动的连绵不绝、多样性和活动范围，可以帮我们充分了解[深度防御](https://www.trendmicro.com/vinfo/us/security/news/cyber-attacks/form-strategies-based-on-these-targeted-attack-stages)是有多么的重要。组织可以通过实施最小特权原则来[防御](http://blog.trendmicro.com/trendlabs-security-intelligence/7-places-to-check-for-signs-of-a-targeted-attack-in-your-network/)这些攻击，从而显著减少他们的横向渗透机会。此外，[网络分段](https://www.trendmicro.com/vinfo/us/security/news/cyber-attacks/protecting-data-through-network-segmentation)和[数据分类](https://www.trendmicro.com/vinfo/us/security/news/cyber-attacks/keeping-digital-assets-safe-need-for-data-classification)在这方面也有所帮助。[访问控制](https://www.trendmicro.com/vinfo/us/security/definition/application-control)和黑名单以及[入侵检测和防御系统](https://www.trendmicro.com/en_us/business/products/network/integrated-atp/next-gen-intrusion-prevention-system.html)等机制也有助于进一步确保网络安全，而白名单(如应用程序控制)和行为监控则有助于检测和阻止可疑或未知文件的异常活动。同时，我们也要加强[电子邮件网关](https://www.trendmicro.com/vinfo/us/security/news/cybercrime-and-digital-threats/infosec-guide-email-threats)的保护措施，以抵御REDBALDKNIGHT的鱼叉式网络钓鱼攻击。禁用不必要和过时的组件或插件，并确保[系统管理工具](https://www.trendmicro.com/vinfo/us/security/news/cybercrime-and-digital-threats/best-practices-securing-sysadmin-tools)以安全的方式加以使用，因为它们有可能被攻击者所利用。更重要的是，要对基础设施和应用程序及时进行更新，以减少从[网关](http://www.trendmicro.com/us/business/complete-user-protection/index.html)和[网络](http://www.trendmicro.com/us/enterprise/security-risk-management/deep-discovery/#network-protection)到[端点](http://www.trendmicro.com/us/enterprise/product-security/vulnerability-protection/)和[服务器](http://www.trendmicro.com/us/enterprise/cloud-solutions/deep-security/software/)的各种攻击。

<br>

**IOC**

****

[https://documents.trendmicro.com/assets/appendix-redbaldknight-bronze-butler-daserf-backdoor-steganography.pdf](https://documents.trendmicro.com/assets/appendix-redbaldknight-bronze-butler-daserf-backdoor-steganography.pdf)
