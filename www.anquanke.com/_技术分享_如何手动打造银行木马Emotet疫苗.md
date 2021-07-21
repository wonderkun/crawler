> 原文链接: https://www.anquanke.com//post/id/87282 


# 【技术分享】如何手动打造银行木马Emotet疫苗


                                阅读量   
                                **125697**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://blog.minerva-labs.com/emotet-goes-more-evasiv](https://blog.minerva-labs.com/emotet-goes-more-evasiv)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01b9d50d2b15c814ab.jpg)](https://p1.ssl.qhimg.com/t01b9d50d2b15c814ab.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**



Emotet是一款银行木马，目的是窃取银行信息、电子邮箱账户信息并从受害者的银行账户中自动抽取金钱，这款木马会利用受害者的联系人列表及邮箱账户进行传播。

目前正处于活跃期的Emotet攻击活动气势正盛，研究人员已经识别出数十种不同的核心程序载荷。此时此刻，大约有数百个[域名](https://github.com/MinervaLabsResearch/BlogPosts/blob/master/Emotet/Domains.txt)被用于传播Emotet，**这可能是自2017年以来规模最大的网络钓鱼攻击活动。**

本文分析了Emotet的发展历史，该程序最开始是一款简单的恶意软件，但经过几年的发展，木马开发者在其中添加了越来越多的规避技术。Minerva实验室一直在分析Emotet的活动轨迹，发现最近的攻击载荷变种在绕过反病毒产品方面卓有成效。即便如此，**只要创建三个空白文件，我们就可以完全阻止Emotet，使终端免疫这种安全威胁。**

[![](https://p5.ssl.qhimg.com/t01bf4f86217462fda6.png)](https://p5.ssl.qhimg.com/t01bf4f86217462fda6.png)

图1. Emotet在终端的启动过程

[![](https://p0.ssl.qhimg.com/t01f3dcb54d5e6be672.png)](https://p0.ssl.qhimg.com/t01f3dcb54d5e6be672.png)

图2. 创建空白文件后可阻止Emotet运行

**二、Emotet演变历史**



自[2014](http://blog.trendmicro.com/trendlabs-security-intelligence/new-banking-malware-uses-network-sniffing-for-data-theft/)年起，Emotet就开始给人们带来困扰，这款木马每年都在不断演进及发展，融入新的功能及行为。在早期阶段，Emotet能够将恶意DLL注入敏感进程中，拦截网络行为来窃取信息，这也是该木马能从其他银行木马中脱颖而出的原因。

在2014年晚些时候，人们发现了[新版本的Emotet](https://securelist.com/the-banking-trojan-emotet-detailed-analysis/69560/)，新版木马开始采用新的技术，通过[自动转账（automated transfers，ATS）](https://www.investopedia.com/terms/a/automatic-transfer-service.asp)服务从受害者的银行账户中窃取金钱。这款变种的模块化特点更加明显，包含许多不同的模块，这些模块具备更加恶意的功能。

在这个版本中，Emotet的开发者并没有攻击俄语国家的用户，这么做可能是想避免引起俄罗斯执法机构的注意。

2015年1月，Emotet重出江湖。这一次，恶意软件作者采用多种规避技术来强化原始变种的功能：

1、在内存中解密恶意软件的关键元素。

2、如果Emotet发现自身运行在虚拟机环境中，它会与一组伪造的C2服务器进行通信。这些并不是真正的C2服务器，唯一的作用是用来误导安全分析人员（同时期的AndromedaGamarue恶意软件也采用了相似的[策略](http://0xebfe.net/blog/2013/03/30/fooled-by-andromeda/)）。根据卡巴斯基的[研究结果](https://securelist.com/the-banking-trojan-emotet-detailed-analysis/69560/)，Emotet会分析进程名是否匹配“vboxservice.exe”、“vmacthlp.exe”、“vmtoolsd.exe”以及“vboxtray.exe”等。

对Emotet而言，2017年是非常有趣的一年。自4月下旬以来，Emotet再次卷土重来，这一次它添加了更多的策略及模块，关键的变化包括如下几点：

1、沙箱规避：为了规避沙箱检测机制，木马将URL存放在加密列表中，这样沙箱想分析和解析URL地址会变得更加困难，因此，沙箱无法检测到URL地址，无法下载Emotet样本。

2、通过暴力破解凭据来传播：新的变种采用了更广泛的传播方式，增加了字典爆破活动目录（Active Directory）域账户的功能。

3、利用漏洞来传播：Emotet是“传统”犯罪阵营中第一个投入“**ETERNALBLUEDOUBLEPULSAR**”漏洞利用技术的成员。结合这两个漏洞利用技术，Emotet可以像蠕虫那样感染网络，从单个感染体扩散到整个组织。

4、更新与C2服务器的通信方法：通过base64编码的cookie加密传输受害者的信息，而不是根据受害者信息计算出服务器的某个路径，然后再向该路径发起POST请求。此外，Emotet也采用了一些策略来迷惑安全分析人员，比如服务器会返回“**404: page not found**”页面，但该页面中其实仍然包含加密的响应数据。

5、采用新的模块：新的版本可以窃取浏览器以及邮件客户端的凭据。

6、混淆代码：Emotet添加了“垃圾”数据，加大混淆强度，进一步拖延分析人员的进度。此外，恶意软件将需要加载的函数（导入表）隐藏在哈希数组中，只有在运行时才使用这些函数。

7、收集受害者主机信息：Emotet会收集受害者主机的信息，如进程名等信息， 根据这些信息决定下一步动作。

8、加密机制：Emotet采用了另一种加密算法。在之前的版本中，Emotet使用RC4算法来加密通信数据。在第4版程序中，Emotet选择使用更强大的加密算法，即CBC模式的128位AES算法。

9、C2协议：Emotet采用了“[protobuf](https://developers.google.com/protocol-buffers/)”协议（Google提出的一种通信协议），增加了一个额外的编码类型，使得默认解析器无法解析其协议字段。

<br>

**三、2017年末的攻击浪潮**



上个月出现了一款新的Emotet变种，这个变种通过恶意邮件进行传播，邮件中提示用户打开一个恶意链接，该链接指向一个Word文档，如下所示：

[![](https://p0.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)](https://p0.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)

[![](https://p4.ssl.qhimg.com/t01bb1465762f13c2a7.png)](https://p4.ssl.qhimg.com/t01bb1465762f13c2a7.png)

图3. 钓鱼邮件

与其他攻击活动不同的是，这个文档并没有直接附加到电子邮件中，而是托管在远程服务器上。这么做可能是想**绕过基于恶意邮件附件检测机制的安全解决方案。**

受害者被诱骗下载的[恶意文档](https://www.virustotal.com/#/file/0e0c5b1a666dde75e58d0cbef4e2013cd83d385012747dc3fd392763f25e1e4b/detection)如下所示，与其他许多攻击活动类似，该文档通过基本的社会工程学技巧来诱导用户启用宏执行功能：

[![](https://p5.ssl.qhimg.com/t015a04dbb3aef3f016.png)](https://p5.ssl.qhimg.com/t015a04dbb3aef3f016.png)

图4. 恶意文档

如果受害者启用宏，该文档就会执行一个批处理脚本：

[![](https://p3.ssl.qhimg.com/t012b75daf193e87bc1.png)](https://p3.ssl.qhimg.com/t012b75daf193e87bc1.png)

[![](https://p0.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)](https://p0.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)图5. 批处理脚本

脚本运行后，最后一行会执行一条带有编码载荷的PowerShell命令，达到无文件执行效果。

该载荷经过解码后可以还原成如下字符串：

[![](https://p1.ssl.qhimg.com/t0187b72a7000c11814.png)](https://p1.ssl.qhimg.com/t0187b72a7000c11814.png)

图6. 解码后的载荷

新版Emotet在短短一周内就完成了功能上的改进，可以绕过安全产品：早期版本的变种会使用PowerShell脚本，其中包含了“iex”指令（Invoke-Expression）来执行加密脚本，而新版中会混淆这个指令特征。

第一个变种中会直接包含“iex”特征，如下所示：[![](https://p0.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)](https://p0.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)

[![](https://p5.ssl.qhimg.com/t010910c5b4f5135a18.png)](https://p5.ssl.qhimg.com/t010910c5b4f5135a18.png)

图7. 包含iex特征的变种

后续版本中会修改这个特征以绕过安全产品：[![](https://p0.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)](https://p0.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)

[![](https://p2.ssl.qhimg.com/t013e10c1f7fdfc09db.png)](https://p2.ssl.qhimg.com/t013e10c1f7fdfc09db.png)

图8. 特征混淆后的变种

其中，`env.public`对应的是`C:UseresPublic`。

新变种所用的方法非常巧妙，它提取了第14个字符（"I"）以及第6个字符（“e”），然后将这两个字符与硬编码的“x”字符拼接起来，形成“iex”，这样就无需在脚本中直接包含这个特征。这个解决方案非常简单但也非常有效，这代表Emotet背后的犯罪分子已经意识到他们的工具已被安全产品检测出来。

在感染过程的最后阶段中，Emotet释放器会解密并调用混淆字符串。

[![](https://p2.ssl.qhimg.com/t0186f45c04ccfecba2.png)](https://p2.ssl.qhimg.com/t0186f45c04ccfecba2.png)

图9. 下载可执行载荷

这个脚本会遍历5个已被攻陷的网站，从某个网站上下载[可执行载荷](https://www.virustotal.com/#/file/0dab41c3567f3702a146e94950f82daa6176435fedf157ec203ef16b38eac1af/detection)。一旦载荷成功执行，该脚本就会终止运行。

<br>

**四、通过三个文件阻止Emotet**



最新版的Emotet（2017年10月到11月期间的版本）带有更多规避技术：这个变种会使用一系列新技术，以避免样本被沙箱及反病毒产品检测到。比如，样本会检测环境中是否存在与沙箱有关的如下文件：

1、“C:a”目录下的3个文件：“C:afoobar.bmp”、“C:afoobar.gif”及“C:afoobar.doc”。

2、“C:123”目录及“C:”目录下的4个文件："C:email.doc"、“C:email.htm”、“C:123email.doc”以及“C:123email.docx”。

如果Emotet找到1中的所有3个文件或者2中的所有4个文件，那么就会停止执行，以避免被相应的沙箱环境所分析。

与此同时，Emotet也在寻找与沙箱有关的用户及主机名。如果它发现以下Windows用户名或者主机名中有一个出现，那么也会停止运行：



```
TEQUILABOOMBOOM
Wilbert
admin
SystemIT
KLONE_X64-PC
John Doe
BEA-CHI
John
```

在Joe Sandbox的[分析报告](https://www.joesandbox.com/analysis/33605/0/html)中，我们可以看到该木马的规避逻辑，反编译后整理的代码如下所示：

[![](https://p2.ssl.qhimg.com/t01f3d41d0584c9a5e7.png)](https://p2.ssl.qhimg.com/t01f3d41d0584c9a5e7.png)

图10. 木马规避逻辑

<br>

**五、攻击规模及统计数据**



经统计，超过700个域名与最近的Emotet活动有关。Emotet所使用的这些域名有三种不同的用途：

**1、托管Emotet恶意文档**

（1）当用户点击钓鱼邮件中的链接时，这些网站用来托管恶意文档。

（2）使用被攻陷的WordPress站点提供托管服务。

**2、托管Emotet可执行载荷**

（1）服务器存放恶意软件，由释放器来下载。

（2）使用被攻陷的网站提供托管服务。

**3、承担C2服务器功能。安装Emotet后，这些服务器用来收集信息、发送命令。**

读者可以访问如下网址获取完整的域名清单：

[https://github.com/MinervaLabsResearch/BlogPosts/blob/master/Emotet/Domains.txt](https://github.com/MinervaLabsResearch/BlogPosts/blob/master/Emotet/Domains.txt)



**六、总结**



分析Emotet的演变轨迹后，我们可以了解恶意软件作者在伪装恶意软件方面的良苦用心，以避免恶意软件被反病毒产品、安全研究人员及沙箱检测到。

最早恶意软件会附带本地配置文件以及事先预设好的感染逻辑，后来恶意软件采用模块化设计，根据C2服务器的响应决定下一步操作。此外，在抓取信息方面，Emotet也有不少改变：最早是将窃取的信息存放在端点的文件系统上，后来是采用无文件方式，通过精心构造的报文将数据以加密形式传送到C2服务器上，无需写入本地磁盘。

每一年恶意软件都会变得更加复杂、与时俱进，会采用诸如PowerShell等新的攻击技术，在规避技巧上也愈发成熟。

如果想避免终端被Emotet感染，你可以考虑创建如下文件：



```
C:afoobar.bmp
C:afoobar.gif
C:afoobar.doc
C:email.doc
C:email.htm
C:123email.doc
C:123email.docx
```

如果你发现在工作环境中无法创建这些文件，你可以了解一下Minerva的反检测平台，该平台通过精心模拟这类元素来防御恶意软件。Minerva实验室可以阻止大规模的Emotet及其他规避型感染攻击行为，无需人工参与。
