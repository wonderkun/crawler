
# 【技术分享】解析APT29的无文件WMI和PowerShell后门


                                阅读量   
                                **233994**
                            
                        |
                        
                                                                                                                                    ![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2017/03/dissecting_one_ofap.html](https://www.fireeye.com/blog/threat-research/2017/03/dissecting_one_ofap.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85851/t01d3c5d4c3697cd02c.jpg)](./img/85851/t01d3c5d4c3697cd02c.jpg)**

****

翻译：[**興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

安全公司Mandiant观察到APT29使用了一款名为POSHSPY的后门工具。POSHSPY使用了WMI（Windows Management Intrumentation，Windows管理工具）和PowerShell脚本，这也是该组织经常使用的两种工具。在调查过程中，Mandiant发现APT29将POSHSPY作为辅助后门使用，以便在主后门失效后重新夺回目标控制权。

POSHSPY大量使用了Windows系统的内置功能来实现后门功能，它利用WMI实现后门的存储和本地持久化，不熟悉WMI的人难以发现其踪影；利用PowerShell载荷使得目标系统运行的是合法的进程，只有在增强型日志记录或内存中才能发现恶意代码运行痕迹。该后门活动并不频繁，使用了流量混淆、加密处理以及地理上合法的网站作为C2（command and control，命令控制）服务器，使安全人员难以识别其网络流量。总体而言，POSHSPY的每一个方面都是高效且隐蔽的。

Mandiant最初在2015年的一次应急响应处置中发现了POSHSPY后门，早期版本的后门使用的是PowerShell脚本。随后，攻击者更新了后门版本，使用WMI来实现本地存储和持久化。在过去两年中，Mandiant在多个场景中都发现过APT29组织使用POSHSPY的痕迹。

我们最早在一次演讲中讨论了APT29使用该后门的一些情况。读者可以参考[幻灯片](https://www.slideshare.net/MatthewDunwoody1/no-easy-breach-derby-con-2016)或[演讲视频](https://www.youtube.com/watch?v=Ldzr0bfGtHc)来回顾之前的分析内容。

<br>

**二、WMI简介**



WMI是从Windows 2000起，在每个Windows系统版本中都会内置的一个管理框架。WMI以本地和远程方式提供了许多管理功能，包括查询系统信息、启动和停止进程以及设置条件触发器。我们可以使用各种工具（比如Windows的WMI命令行工具wmic.exe）或者脚本编程语言（如PowerShell）提供的API接口来访问WMI。Windows系统的WMI数据存储在WMI公共信息模型（common information model，CMI）仓库中，该仓库由“System32wbemRepository”文件夹中的多个文件组成。

WMI类是WMI的主要结构。WMI类中可以包含方法（代码）以及属性（数据）。具有系统权限的用户可以自定义类或扩展许多默认类的功能。

在满足特定条件时，我们可以使用WMI永久事件订阅（permanent event subscriptions）机制来触发特定操作。攻击者经常利用这个功能，在系统启动时执行后门程序，完成本地持久化。WMI的事件订阅包含三个核心WMI类：Filter（过滤器）类、Consumer（消费者）类以及FilterToConsumerBinding类。WMI Consumer用来指定要执行的具体操作，包括执行命令、运行脚本、添加日志条目或者发送邮件。WMI Filter用来定义触发Consumer的具体条件，包括系统启动、特定程序执行、特定时间间隔以及其他条件。FilterToConsumerBinding用来将Consumer与Filter关联在一起。创建一个WMI永久事件订阅需要系统的管理员权限。

我们观察到APT29使用WMI来完成后门的本地持久化并存储PowerShell后门代码。为了存储后门代码，APT29创建了一个新的WMI类，添加了一个文本属性以存储字符串，并将加密base64编码的PowerShell后门存放在该属性中。

APT29创建了一个WMI事件订阅来运行该后门，其具体内容是通过PowerShell命令，直接从新的WMI属性中读取、加密和执行后门代码。通过这种方法，攻击者可以在系统中安装一个持久性后门，并且不会在系统磁盘上留下任何文件（除了WMI仓库中的文件之外）。这种“无文件”后门技术使得常见的主机分析技术难以识别恶意代码。

<br>

**三、POSHSPY的WMI组件**



POSHSPY后门的WMI组件利用一个Filter来定期执行PowerShell脚本。在某个样本中，APT29创建了一个名为BfeOnServiceStartTypeChange的Filter（如图1所示），过滤条件设为每周一、周二、周四、周五以及周六的当地时间上午11:33时各执行一次。

[![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013f1f13250d8d64ba.png)

图1. “BfeOnServiceStartTypeChange“的 WMI查询语言（WMI Query Language，WQL）

**过滤器条件**

“BfeOnServiceStartTypeChange”过滤器绑定到一个CommandLineEventConsumer消费者：WindowsParentalControlsMigration。APT29配置WindowsParentalControlsMigration消费者来静默执行经过base64编码的PowerShell命令，该命令在执行时会提取、解密并执行存储在RacTask类的HiveUploadTask文本属性中的PowerShell后门载荷。图2显示了WindowsParentalControlsMigration消费者所执行的“CommandLineTemplate”命令。

[![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e152a8f7a36c49e2.png)

图2. WindowsParentalControlsMigration执行的CommandLineTemplate命令

从“CommandLineTemplate”命令中提取的PowerShell命令，解码后如图3所示：

[![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012547392c93958f0f.png)

[![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0126e750048c690879.png)

图3. 从CommandLineTemplate中提取的解码后的PowerShell代码

<br>

**四、POSHSPY的PowerShell组件**

POSHSPY样本的全部代码可以在[这里](https://github.com/matthewdunwoody/POSHSPY/blob/master/poshspy_redacted.txt)找到。

POSHSPY后门可以下载并执行PowerShell代码以及Windows可执行文件，该后门包含几个主要功能，包括：

1、下载PowerShell代码并使用EncodedCommand参数执行该代码。

[![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01763eb261baed7e3d.png)

2、将可执行文件写入到“Program Files”目录下随机选择的一个文件夹中，并将可执行文件名改为与所选文件夹相匹配的名称，如果写入失败，则使用系统生成的临时文件名，扩展名为“.exe”。

[![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0146823daef9381b81.png)

3、修改下载的每个可执行文件的标准信息时间戳（创建时间、修改时间以及访问时间），以匹配System32目录中随机选择的一个文件的时间戳，创建时间被修改为2013年之前。

[![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f5daacb351aae2ee.png)

4、使用AES和RSA公钥加密算法对木马通讯进行加密。

[![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ecf3b5e4f78baa40.png)

5、利用域名生成算法（Domain Generation Algorithm，DGA），通过域名、子域名、顶级域名（top-level domains，TLDs）、统一资源标识符（Uniform Resource Identifiers，URIs）、文件名和文件扩展名列表，生成C2服务器的URL地址。

[![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a713c9d7a56d6ad2.png)

6、使用自定义的User Agent字符串，或者使用从urlmon.dll中提取的系统User Agent字符串。

[![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019479d4715a6b625f.png)

7、在每个网络连接中使用的都是自定义cookie键值或随机生成的cookie键值。

[![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011666fab7d0bc2fcd.png)

8、按2048字节分段上传数据。

[![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01655f7a552266d34a.png)

9、在上传或下载前，在所有的加密数据前附加一个文件签名头部，文件类型从以下几种类型中随机选择：

ICO、GIF、JPG、PNG、MP3、BMP

[![](./img/85851/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fa3cadfcffc2f069.png)

本文分析的这个样本使用了11个合法域名，域名的所有者为同一个机构，其地理位置处于受害者附近。这些域名与DGA算法相结合后，可以生成550个不同的C2服务器URL地址。样本的活跃程度较低，使用DGA算法以生成复杂的C2服务器地址，通信数据中添加其他文件类型头部以绕过基于内容的安全审核，种种行为使得安全人员难以通过常规的网络监控技术识别该后门。

<br>

**五、总结**

POSHSPY是APT29组织技术能力的一个绝佳样例。通过这种无文件后门技术，攻击者可以构造一个非常独立的后门，并与他们之前的普通后门结合使用，确保在普通后门失效后还能实现对目标的持久性渗透。如果你掌握WMI和PowerShell的相关知识，你不难发现这个后门存在的痕迹。通过在系统中启用并监视[增强型PowerShell日志](https://www.fireeye.com/blog/threat-research/2016/02/greater_visibilityt.html)，我们可以捕捉到恶意代码的执行过程，因为使用WMI持久化技术的合法应用非常稀少，我们可以遍历系统环境，快速准确地找到其中的恶意文件。这个后门是我们捕获的几个后门家族中的其中一员，其他的后门包括[域名前移后门](https://www.fireeye.com/blog/threat-research/2017/03/apt29_domain_frontin.html)以及[HAMMERTOSS](https://www.fireeye.com/blog/threat-research/2015/07/hammertoss_stealthy.html)后门。

<br>

**六、相关阅读**

这篇[文章](https://www.fireeye.com/blog/threat-research/2016/02/greater_visibilityt.html)介绍了如何利用PowerShell日志获取更多信息，提高系统中PowerShell活动的可见性。

William Ballenthin、Matt Graeber和Claudiu Teodorescu发表的[白皮书](https://www.fireeye.com/content/dam/fireeye-www/global/en/current-threats/pdfs/wp-windows-management-instrumentation.pdf)介绍了与WMI有关的攻击、防御和取证技巧。

Christopher Glyer和Devon Kerr的[演示文档](https://files.sans.org/summit/Digital_Forensics_and_Incident_Response_Summit_2015/PDFs/TheresSomethingAboutWMIDevonKerr.pdf)介绍了在Mandiant之前调查工作中发现的与WMI技术有关的其他攻击活动信息。

FireEye公司的FLARE团队公布了一个[WMI仓库解析工具](https://github.com/fireeye/flare-wmi/tree/master/python-cim)，以便调查人员能够提取内嵌于WMI仓库中的数据，从而识别使用WMI持久化技术的应用。
