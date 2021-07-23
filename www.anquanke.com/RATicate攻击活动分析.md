> 原文链接: https://www.anquanke.com//post/id/206483 


# RATicate攻击活动分析


                                阅读量   
                                **145901**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者sophos，文章来源：news.sophos.com
                                <br>原文地址：[https://news.sophos.com/en-us/2020/05/14/raticate/](https://news.sophos.com/en-us/2020/05/14/raticate/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01003deb0485f2a582.jpg)](https://p3.ssl.qhimg.com/t01003deb0485f2a582.jpg)



## 0x00 概述

在一系列可以追溯到2019年11月的恶意垃圾邮件活动中，某未确认身份的组织发送诸多安装程序，用以投递RAT及窃取受害者计算机信息的恶意软件。

我们已经确定了五次不同的攻击活动，位于2019年11月到2020年1月期间，其payload使用相似代码及指向相同C2。 攻击活动针对的企业位于欧洲，中东和韩国。这使得我们相信它们出于同一组织之手，故称之为**RATicate**。

在新发现的攻击活动中，我们发现其通过新冠肺炎(COVID-19)诱惑受害者打开恶意软件。 虽然其改变了策略，但我们仍怀疑此次攻击活动是该组织所为。

本篇文章中，我们将关注其初始载荷，即每次活动都使用到的 [Nullsoft Scriptable安装系统(NSIS) ](https://nsis.sourceforge.io/Main_Page)。 NSIS是一款开源工具，用以创建Windows安装程序及基于Internet的软件分发。 但它也被滥用了很长一段时间，用来伪装和部署恶意软件。 (在后续报告中，我们将讨论使用其他安装程序的攻击活动，以及该组织钓鱼策略的转变。)



## 0x01 初始载荷分析

NSIS一个有趣的功能是其支持插件，允许安装程序与其他组件（包括Windows操作系统组件）通信 ([可用插件列表](https://nsis.sourceforge.io/Category:Plugins))。 这些插件本质为Windows DLL文件。 如果于安装程序构建期间选择某插件，会被自动添加到最终编译完成的`$PLUGINS`文件夹内。

这些插件可以提供的功能包括:
- [杀掉进程](https://nsis.sourceforge.io/Processes_plug-in)
- [执行基于命令行的程序](https://nsis.sourceforge.io/NsExec_plug-in)
- [解压文件](https://nsis.sourceforge.io/ExtractDLLEx_plug-in)
- [加载DLL及调用其输出函数](https://nsis.sourceforge.io/Docs/System/System.html)
安装程序引起我们注意是因为它们都释放一组相同的`junk file`(这些文件并未被用来安装恶意软件)。过去我们看到过于NSIS安装程序中用`junk file`以隐藏恶意软件；`junk file`旨在迷惑分析人员，及干扰沙箱分析。这种行为引起了我们的兴趣，于是开始对其进行更为详细的分析。

我们发现所有样本都使用了 **System.dll** 插件，它允许使用者加载某DLL以及调用其输出函数。 恶意安装程序调用该DLL以注入payload到内存中(多数情况下经由 `cmd .exe`)。

为了便于说明，本报告主要分析第一次发现的 [NSIS安装程序](https://www.virustotal.com/gui/file/4722dafde634152e42054038c6ab64563a9dd717edfa2e37f245c76f431cecec/detection)：

[![](https://s1.ax1x.com/2020/05/21/YHNhd0.png)](https://s1.ax1x.com/2020/05/21/YHNhd0.png)

NSIS安装包中含压缩内容，其中有可执行程序，由安装包加载到内存中。 这些内容可以通过压缩工具(如7 zip)提取出来。

[![](https://s1.ax1x.com/2020/05/21/YHNRLn.png)](https://s1.ax1x.com/2020/05/21/YHNRLn.png)

样本释放文件类型包括:
- ASCII文本文件
- C源码(ASCII文本格式)
- 数据文件
- 64位ELF
- GIF
- JPEG
- BMP(Windows 3.x 格式，164**314**4)
- 32位可执行文件(DLL)
- 32位可执行文件(GUI)
- POSIX Shell(ASCII文本格式)
<li>
`.pyc`文件</li>
- XML 1.0
安装程序将释放`junk file`到`%TEMP%/careers/katalog/_mem_bin/page1/W3SVC2` 目录：

[![](https://s1.ax1x.com/2020/05/21/YHNfZq.png)](https://s1.ax1x.com/2020/05/21/YHNfZq.png)

安装包释放到临时目录中的文件中仅有两个与恶意软件有关：
- aventailes.dll(Loader)
- Cluck(加密内容)
我们将重点分析这两个文件。

不过我们发现这些安装程序的payload有所不同。 在对发现的样本进行分析的过程中——手动分析以及借助沙盒工具——我们发现了数种不同的RAT及窃密软件，包括Lokibot，Betabot，Formbook与AgentTesla。 但是这些安装程序在执行时都遵循相同的过程。



## 0x02 第一阶段:Loader &amp; Shellcode

在第一阶段，安装程序将部署初始Loader——恶意DLL文件。 然后，DLL文件开始解密payload，并最终将payload注入到内存中(此时NSIS安装包在释放`junk file`)。 下图展示了分析样本如何创建`cmd.exe`进程——注入payload到该进程：

[![](https://s1.ax1x.com/2020/05/21/YHNgMj.png)](https://s1.ax1x.com/2020/05/21/YHNgMj.png)

[![](https://s1.ax1x.com/2020/05/21/YHN2ss.png)](https://s1.ax1x.com/2020/05/21/YHN2ss.png)

样本创建子进程的内存内容如上所示。 payload位于地址`0x400000`处。

RATicate安装包释放的恶意DLL（本例中是**aventailes.dll** ）本质是一 Loader，可能由此次活动策划者开发，存储于临时目录中。 分析的所有Loader都是只有一个输出函数的DLL文件，尽管各样本中Loader的名称和输出函数不尽相同。（本例中是Inquilinity)

[![](https://s1.ax1x.com/2020/05/21/YHNIiT.png)](https://s1.ax1x.com/2020/05/21/YHNIiT.png)

如前文所述，该输出函数会被NSIS的System插件调用。 输出函数会加载并执行shellcode(位于Loader的`.rdata`区块)。 解密shellcode使用了一个简单的算法，该算法于不同Loader中不尽相同。

然后，由Loader加载的shellcode会读取存有其他Loader及payload的加密文件——Cluck。这些Loader（PE文件）和shellcode会在之后两个阶段中按需解密。第一阶段，由Loader调用的shellcode完成解密工作，解密后内容包含异或运算的密钥(用于解密**shellcode2**与**Loader2**)，shellcode[**shellcode 2**]及一PE文件[**Loader 2**]。

[![](https://s1.ax1x.com/2020/05/21/YHNoJU.png)](https://s1.ax1x.com/2020/05/21/YHNoJU.png)

第一阶段的工作流程如下所示：

[![](https://s1.ax1x.com/2020/05/21/YHNTWF.png)](https://s1.ax1x.com/2020/05/21/YHNTWF.png)

第一阶段的工作流程：
1. 执行NSIS exe。
1. System.dll插件加载并调用Loader（aventailes.dll）。
1. Loader的输出函数解密shellcode 1并调用之。
1. shellcode1读取加载到内存中的Cluck文件。
1. shellcode1解密shellcode2和Loader2并映射shellcode2，然后调用之。
1. shellcode2将Loader2映射到内存中。


## 0x03 第二阶段：shellcode 2 &amp; Loader DLL

当Shellcode 2将 Loader 2加载到内存中后，开始第二阶段解密 。Loader 2读取Cluck文件来解密其他内容。 根据包含加密内容的文件名（本例中是Cluck）动态生成异或运算密钥，该密钥用于解密第二阶段的数据。如下图所示，解密完成后，文件的第二部分中存储了另一个异或运算密钥(xor_key 2)，该密钥用于解密其他内容，例如字符串，shellcode和PE文件。

[![](https://s1.ax1x.com/2020/05/21/YHN7z4.png)](https://s1.ax1x.com/2020/05/21/YHN7z4.png)

[![](https://s1.ax1x.com/2020/05/21/YHNbQJ.png)](https://s1.ax1x.com/2020/05/21/YHNbQJ.png)

第二阶段工作流程：
1. Loader 2执行其DllEntryPoint。
1. Loader 2再次读取Cluck文件。
1. Loader 2从Cluck中解密未使用的shellcode。
1. Loader 2从Cluck读取的数据中解密shellcode 3。
1. Loader 2执行shellcode3，该shellcode3解密最终payload（PE文件）。


## 0x04 第三阶段：Injection

解密工作完成之后，shellcode 3将在一子进程中注入最终payload。其使用了[NtCreateSection + NtMapViewOfSection 注入技术](https://ired.team/offensive-security/code-injection-process-injection/ntcreatesection-+-ntmapviewofsection-code-injection)。

以下是分析时提取出来的组件：

[![](https://s1.ax1x.com/2020/05/21/YHUSJO.png)](https://s1.ax1x.com/2020/05/21/YHUSJO.png)



## 0x05 如何确定其为同一组织所为？

我们共发现了38个NSIS安装包，都具有如下相似的特征：

相同的`junk file`。不仅仅是它们的名字，还有其内容。当NSIS脚本生成安装包时，攻击活动的参与者必须将这些文件统统保存在硬盘上。

相同的Loader：所分析NSIS安装包中所有的Loader都是相同的，不是在HASH值方面，而是在功能方面(具体如下)。
- 所有初始Loader都只有一个输出函数，并由NSIS安装包调用
- 初始Loader从加密数据中读取数据，以解密加载Loader 2的shellcode。
- 所有样本的Loader 2从加密数据中提取并解密shellcode 3。
- Shellcode 3负责解密最终payload并将其注入到远程进程中，在所有分析的样本之间都是相同的。
但是，我们分析的每个NSIS安装包释放了不同的恶意软件 。我们认为这出于两种可能的情况：恶意NSIS软件包是暗网论坛上出售的通用打包程序；或者该组织成员使用自行编写的Loader于每次攻击活动中部署不同的payload。

尽管在暗网论坛上有很多打包程序在出售，但我们认为不太可能是这种情况，因为如果是不同组织的成员使用相同的通用打包程序，那么`junk file`应该会随payload变化而变化。因此，我们以攻击活动来自同一组织的假说继续进行调查。

虽然已有掌握的证据，但我们无法证明此组织对所有的攻击活动都负责，但是我们至少可以从相同的打包策略及组件中，找到一种将所有的攻击活动联系起来的方法。我们进行了进一步的分析，以寻找其确定的联系，我们将视线转向提供这些攻击活动的感染链。

我们发现在2019年12月8日至12月13日期间的恶意电子邮件活动中，一组NSIS安装程序投递了相同的`junk file`。（在发现其他的NSIS安装程序之后，我们将这一波攻击活动称为Campaign 3）在我们观察到的攻击活动中，目标似乎都是关键基础设施提供商（或与关键基础设施相关的业务）。我们使用VirusTotal分析了观察到的攻击，并收集了有关其他受害者的开源信息：

[![](https://s1.ax1x.com/2020/05/21/Yqm1dH.png)](https://s1.ax1x.com/2020/05/21/Yqm1dH.png)

上图展示了经分析后的NSIS安装包感染链。它揭示出用于感染受害者的两种常见模式：

[![](https://s1.ax1x.com/2020/05/21/Yqm3od.png)](https://s1.ax1x.com/2020/05/21/Yqm3od.png)

在图表上叠加以上两种方式，可以看出其都用于同一目标企业。其他目标企业也可能采用相同的方法：

[![](https://s1.ax1x.com/2020/05/21/YqmMLD.png)](https://s1.ax1x.com/2020/05/21/YqmMLD.png)

我们能够从VT中检索与此活动相关的一些电子邮件。通过这些电子邮件，我们能够确定一些攻击活动的目标：

[![](https://s1.ax1x.com/2020/05/21/YqmKsO.png)](https://s1.ax1x.com/2020/05/21/YqmKsO.png)

Campaign 3中的一封电子邮件，以“banking confirmation”作为诱饵：

[![](https://s1.ax1x.com/2020/05/21/YqmuQK.png)](https://s1.ax1x.com/2020/05/21/YqmuQK.png)

我们在VirusTotal中发现许多电子邮件没有显示收件人的地址，或者收件人地址填充了发件人字段中的地址。在这种情况下，我们分析了电子邮件标题，因为标题包含与电子邮件相关的许多信息，例如原始收件人：

[![](https://s1.ax1x.com/2020/05/21/YqmGFA.png)](https://s1.ax1x.com/2020/05/21/YqmGFA.png)

在对NSIS安装包分析的过程中，我们发现与原始样本具有相同`junk file`的样本里，确定了至少5个不同的恶意软件家族用作最终payload，它们均是窃密木马或RAT：
- ForeIT/Lokibot
- BetaBot
- Formbook
- AgentTesla
- Netwire
然后，我们分析了用于这些payload的C2，检查它们之间是否存在联系，并检查其是否将窃取到的数据发送到相同或相似的服务器。

以下是此次活动中一些确定的恶意软件家族及其C2：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/05/21/YqmJJI.png)

每种类型的恶意软件都共享相同的C＆C。在某些情况下，甚至不同的家族——例如Lokibot和Betabot也都共享相同的C＆C。



## 0x06 更多的攻击活动

按照这种模式寻找其他NSIS安装包——它们会在相同日期范围内丢弃相同`junk file`——我们发现了在2019年11月16日至2020年1月8日之间发生的5次不同的攻击活动。虽然这些活动中的每一个安装包都与我们的第一个样本不同，但是其行为与Campaign 3中观察到的行为相同（或至少相似）：

[![](https://s1.ax1x.com/2020/05/21/Yqtybn.png)](https://s1.ax1x.com/2020/05/21/Yqtybn.png)

#### <a class="reference-link" name="0x06.1%20CAMPAIGN%201%20(NOVEMBER%2016-20,%202019)"></a>0x06.1 CAMPAIGN 1 (NOVEMBER 16-20, 2019)

此次活动中所有NSIS安装包释放的`junk file`：

[![](https://s1.ax1x.com/2020/05/21/YqtsDs.png)](https://s1.ax1x.com/2020/05/21/YqtsDs.png)

此次活动中的部分payload：

[![](https://s1.ax1x.com/2020/05/21/YqtcEq.png)](https://s1.ax1x.com/2020/05/21/YqtcEq.png)

这是我们从VirusTotal收集到的与Campaign 1相关的电子邮件：

[![](https://s1.ax1x.com/2020/05/21/Yqt25V.png)](https://s1.ax1x.com/2020/05/21/Yqt25V.png)

下图展示了Campaign 1中的相互关系和感染链（基于VT上可用的数据）

[![](https://s1.ax1x.com/2020/05/21/YqtgU0.png)](https://s1.ax1x.com/2020/05/21/YqtgU0.png)

#### <a class="reference-link" name="0x06.2%20Campaign%202%20(November%2025,%202019%20to%20November%2026,%202019)"></a>0x06.2 Campaign 2 (November 25, 2019 to November 26, 2019)

此次活动中所有NSIS安装包释放的`junk file`：

[![](https://s1.ax1x.com/2020/05/21/YqtWCT.png)](https://s1.ax1x.com/2020/05/21/YqtWCT.png)

此次活动中的部分payload：

[![](https://s1.ax1x.com/2020/05/21/Yqtf8U.png)](https://s1.ax1x.com/2020/05/21/Yqtf8U.png)

我们找不到与此次活动有关的电子邮件，因此无法分析其预期目标。下图展示了相似payload之间的关系：

[![](https://s1.ax1x.com/2020/05/21/Yqth2F.png)](https://s1.ax1x.com/2020/05/21/Yqth2F.png)

#### <a class="reference-link" name="0x06.3%20CAMPAIGN%204%20(DECEMBER%2020,%202019%20TO%20DECEMBER%2031,%202019)"></a>0x06.3 CAMPAIGN 4 (DECEMBER 20, 2019 TO DECEMBER 31, 2019)

此次活动中所有NSIS安装包释放的`junk file`：

[![](https://s1.ax1x.com/2020/05/21/Yqt4v4.png)](https://s1.ax1x.com/2020/05/21/Yqt4v4.png)

此次活动中的部分payload：

[![](https://s1.ax1x.com/2020/05/21/YqtIKJ.png)](https://s1.ax1x.com/2020/05/21/YqtIKJ.png)

收集到的与之相关的电子邮件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/05/21/Yqtor9.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/05/21/YqtHV1.png)

#### <a class="reference-link" name="0x06.4%20CAMPAIGN%205%20(JANUARY%203,%202020%20TO%20JANUARY%208,%202020)"></a>0x06.4 CAMPAIGN 5 (JANUARY 3, 2020 TO JANUARY 8, 2020)

此次活动中所有NSIS安装包释放的`junk file`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/05/21/YqtTbR.png)

此次活动中的部分payload：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/05/21/YqtbUx.png)

收集到的与之相关的电子邮件：

[![](https://s1.ax1x.com/2020/05/21/Yqtq56.png)](https://s1.ax1x.com/2020/05/21/Yqtq56.png)

下图展示了Campaign 5中的相互关系和感染链（基于VT上可用的数据）:

[![](https://s1.ax1x.com/2020/05/21/YqtOPK.png)](https://s1.ax1x.com/2020/05/21/YqtOPK.png)



## 0x07 对攻击活动策划者进行分析

分析所有发现的攻击活动，我们发现其C＆C经常出现重复，如下表所示：

[![](https://s1.ax1x.com/2020/05/21/YqNCVI.png)](https://s1.ax1x.com/2020/05/21/YqNCVI.png)

我们还发现，每次攻击活动的某些不同payload（大多数是Betabot，Lokibot，AgentTesla和Formbook）使用相同的C＆C。这表明，同一参与者/组织正在管理这些恶意软件活动背后的Web服务器。

攻击活动时间表也有明显的聚集——但它们之间从来没有任何重叠，这表明它们是由相同的策划者连续进行的（包括我们将在下一次报告中介绍的第六次攻击活动）：

[![](https://s1.ax1x.com/2020/05/21/YqtX8O.jpg)](https://s1.ax1x.com/2020/05/21/YqtX8O.jpg)

在这些攻击活动中，不仅在同一次活动中跨不同payload共享C2，另外一些C2还在多次不同活动中共享，这也表明是同一参与者/组织策划了所有活动。

下表显示了各次活动之间的一些有趣的联系：

[![](https://s1.ax1x.com/2020/05/21/YqtzKH.jpg)](https://s1.ax1x.com/2020/05/21/YqtzKH.jpg)



## 0x08 目标和动机

根据RATicate使用到的payload，很明显，该组织开展的活动旨在获得对目标公司内计算机的访问控制权。从这些活动中收集到的电子邮件确定其目标包括：
- 某罗马尼亚的电气设备制造商；
- 某科威特建筑服务和工程公司；
- 某韩国互联网公司；
- 某韩国投资公司；
- 某英国建筑供应商；
- 某韩国医学新闻刊物；
- 某韩国电信和电缆制造商；
- 某瑞士出版设备制造商；
- 某日本的快递和运输公司。
我们发现其目标至少在两次攻击活动中重叠：Campaign 1和2都针对电气设备制造商。在多个Campaign中可能会有更多共同的目标（我们仅通过查看VirusTotal的公开可用数据，而未分析非公开数据）。而且，许多（但并非不是全部）已针对的公司与关键基础架构有关。

我们已经检测到另外一个使用这些NSIS安装包的近期活动（1月13日至16日）。但是，随着我们深入分析该组织，我们发现其进行了其他的攻击活动——并且我们相信自1月份以来，该组织已开始使用其他Loader和打包程序。

其中一次活动是我们在三月份检测到的，此次活动使用COVID-19来诱使受害者打开payload。最新检测到的样本随各种VB编写的Loader一并投递——其中包括[Proofpoint于2019年12月发现](https://www.proofpoint.com/us/threat-insight/post/guloader-popular-new-vb6-downloader-abuses-cloud-services)的Guloader。

我们认为这些攻击活动是由同一组织进行的，其原因如下：
- 其电子邮件的目标客户与之前Campaign相同。
- 部分检测到的payload是Betabot和Lokibot，它们于先前观察到的活动中出现。
- Betabot的C＆C与之前Campaign中所发现的相似——它与Campaign 3中的Betabot使用相同的域名(**stngpetty [.] ga**)，并且使用类似的路径(`/~zadmin/`{`NAME1`}`/`{`NAME2`}`/logout.php`)：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/05/21/Yqtj2D.png)

根据他们现有的行为，我们不确定RATicate是专注于间谍活动还是仅仅充当其他组织的恶意软件提供商。有可能他们仅仅是向目标公司投递了恶意软件，以向其他组织的提供付费访问权限，或者他们是将InfoStealer与RAT用作更大的恶意软件分发工作的一部分。我们将继续分析新的攻击活动，以对其动机有更深入的了解。



## 0x09 “反沙盒”

在对第一个RATicate样本进行分析的过程中，我们发现安装包删除的Shellcode 3使用了许多有趣的技术来阻碍分析人员分析其API调用，并且使用了许多反调试技巧来进一步阻碍分析。但是我们在这些样本中也发现了一个奇怪的行为：如果以SHA256值作为文件名之后执行样本，程序将崩溃：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/05/21/Yqtvxe.png)

这种行为可以被视为一种反沙盒技巧。由于沙盒通常以样本哈希值作为文件名运行样本，帮该技术可以避免在沙盒环境中执行payload。但是在本例中，该行为实际上是由于代码错误所致。

在执行Shellcode 3期间发生错误：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/05/21/YqNSrd.png)

Shellcode 3使用一种已知技术——通过在PEB中搜索LDR_DATA_TABLE_ENTRY来获取已加载模块的地址（例如库或可执行文件本身）。LDR结构中的信息包括已加载模块的名称和地址。程序代码会根据所需函数名称的哈希值来检查此结构，从而提供一种方式来动态解析要调用函数的地址。

[![](https://s1.ax1x.com/2020/05/21/YqNpqA.png)](https://s1.ax1x.com/2020/05/21/YqNpqA.png)

该功能是在代码的 `get_dll_base_addres_from_ldr_by_hash(dll_hash)`函数中实现的，而崩溃正是在此函数中发生的。该函数遍历LDR结构，计算所加载模块名称的HASH，并检查其是否匹配作为参数传递的HASH。

该函数将`ldr_data_table-&gt; BaseDllName.Buffer`的内容存入`vulnerable_buffer`中，以便将ANSI字符串转换为UNICODE字符串。

但是，由于`vulnerable_buffer`大小仅为104，并且其存储了Unicode字符串，这意味着其实际大小上仅为52个ANSI字符。所以，如果文件名的长度为53个或更多字符，则将发生缓冲区溢出。要使该程序崩溃，只需为样本提供57个字符的文件名（如`this_is_57_length_filename_in_order_to_do_a_crash_PoC.exe`）即可。

经过分析，我们确认这是代码错误，而不是反沙盒技术。



## 0x10 IOC

与RATicate攻击活动相关的HASH可以在SophosLabs的[GitHub](https://github.com/sophoslabs/IoCs/blob/master/malware-Raticate)中找到。
