> 原文链接: https://www.anquanke.com//post/id/86820 


# 【技术分享】TrickBot银行木马Dropper分析


                                阅读量   
                                **92473**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：ringzerolabs.com
                                <br>原文地址：[https://www.ringzerolabs.com/2017/07/trickbot-banking-trojan-doc00039217doc.html](https://www.ringzerolabs.com/2017/07/trickbot-banking-trojan-doc00039217doc.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t019786d81ca8be0749.png)](https://p3.ssl.qhimg.com/t019786d81ca8be0749.png)

****

译者：[blueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**背景**

今年7月份，安全研究人员捕获到 **TrickBot**银行木马的新样本，通过研究和分析发现，借助于**Necurs**僵尸网络的东风，TrickBot银行木马软件背后的黑客组织正在对包括新加坡、美国、新西兰、加拿大等24个国家的金融机构发起新一轮网络攻击。本文的主要内容是对TrickBot银行木马的**Dropper**（DOC00039217.doc）进行深入的分析和研究。

TrickBot银行木马Dropper-DOC00039217.doc

DOC 00039217.doc（样本示例如下图所示）通过运行恶意的VBA脚本程序来下载第二阶段木马程序，下载到的木马程序可用于下载并安装其他恶意软件。

[![](https://p0.ssl.qhimg.com/t0193f7124df19df266.png)](https://p0.ssl.qhimg.com/t0193f7124df19df266.png)

文件详细信息

[![](https://p0.ssl.qhimg.com/t01294410cd5475adb6.png)](https://p0.ssl.qhimg.com/t01294410cd5475adb6.png)

<br>

**技术细节**

拿到样本之后，我们首先从该DOC文件的首部开始分析，在文件首部里面我们找到了具有XML引用的PK字段，这些发现表示该DOC文件是一个Microsoft Word DOCX和DOCM类型的文件。要检查该DOC文档中都包含了哪些文件，我们只需将DOC扩展名更改为ZIP扩展名即可，并使用归档管理器打开该ZIP文件，解压之后的文件如下图所示。

[![](https://p0.ssl.qhimg.com/t0140602bbd79afd0fd.png)](https://p0.ssl.qhimg.com/t0140602bbd79afd0fd.png)

在压缩包文件中，我们的研究人员找到了一个包含恶意VBA宏代码的vbaProject.bin文件。在文本编辑器中打开该恶意软件，我们发现一旦打开DOC00039217.doc这个原始文件，该VBA恶意脚本就会开始运行。在执行的过程中，该脚本将首先从http://appenzeller.fr/aaaa这个恶意网站上下载一个文件，具体如下图所示：

[![](https://p4.ssl.qhimg.com/t01ec14b07911a9940a.png)](https://p4.ssl.qhimg.com/t01ec14b07911a9940a.png)

下载得到的aaaa文件其实是一个VBScript脚本程序，该脚本程序会去调用Wscript.Shell对象并运行Powershell来下载另一个文件，用于下载此文件的参数变量是由第一个脚本“amphibiousvehicle.eu/0chb7”传递过来的，具体如下图所示：

[![](https://p4.ssl.qhimg.com/t01a43d416da51bd4b6.png)](https://p4.ssl.qhimg.com/t01a43d416da51bd4b6.png)

在分析该Dropper的过程中，我们得到一个重要的发现，那就是上述下载的文件被放到目标机器的％TEMP％文件夹并重命名为petya.exe，但这个petya.exe文件不是最近的Petya 勒索软件，它是一个木马程序。

经过分析我们发现上述我们下载到的木马程序使用PECompact2加壳工具进行了加壳处理，为了能够对加壳程序进行脱壳处理，我们首先将其加载到我们的调试器中，并进入调试器选择的“程序入口点”，具体如下图所示。

[![](https://p2.ssl.qhimg.com/t01c935071c8c9ddaa5.png)](https://p2.ssl.qhimg.com/t01c935071c8c9ddaa5.png)

然后，我们跳转到保存在EAX寄存器中的地址，该地址是0x002440e4，如下图所示：

[![](https://p4.ssl.qhimg.com/t01509a438295fb5306.png)](https://p4.ssl.qhimg.com/t01509a438295fb5306.png)

接下来，我们从0x002440e4地址处的指令开始向下单步执行，一直执行到最后一条指令，该指令应该是一条跳转到其他其他寄存器地址的JMP指令。之后单步执行将使我们进入到程序的Original Entry Point（OEP），此时可以使用传统的导入表重建技术来还原文件。虽然不对木马软件执行脱壳操作该恶意程序也能够正常执行，但是脱壳后将使得静态分析变得更加的容易。

[![](https://p1.ssl.qhimg.com/t01df5b49df599be98a.png)](https://p1.ssl.qhimg.com/t01df5b49df599be98a.png)

恶意软件执行后，petya.exe将自身拷贝到目标机器上的Roamingwinapp文件目录，并将其重命名为odsxa.exe文件。在Roamingwinapp文件目录中，petya.exe程序还生成client_id和group_tag这两个文件，这两个文件中包含了有关受害者机器的标识字符串。同时，petya.exe程序还在Roamingwinapp文件目录中生成一个modules文件夹，该文件夹用于保存稍后下载的其他恶意软件/模块/插件，具体如下图所示。

[![](https://p0.ssl.qhimg.com/t018f6ee43f2bc10bab.png)](https://p0.ssl.qhimg.com/t018f6ee43f2bc10bab.png)

一旦petya.exe程序将所有东西都拷贝到新的文件夹中了，该程序将自动退出，上文中生成的odsxa.exe将会接管继续执行。odsxa.exe程序首先启动SVCHOST.EXE程序并使其处于可唤醒状态，之后在SVCHOST进程内存段中的一个新的代码节中注入木马程序想要执行的恶意代码。这种注入过程是安全的，因为它在SVCHOST.EXE的安全上下文中运行。这样注入后的代码可以在Windows操作系统中安全的执行而不容易被安全检测工具识别到（ps：这种注入手法之前安全客平台上已经有介绍过，详情见[【技术分享】Dll注入新姿势：SetThreadContext注入](http://bobao.360.cn/learning/detail/4376.html)）。

[![](https://p3.ssl.qhimg.com/t01d9a64dff70521c86.png)](https://p3.ssl.qhimg.com/t01d9a64dff70521c86.png)

在注入操作完成之后，SVCHOST.EXE进程将由可唤醒状态转变成执行状态，它首先通过向合法的网站ipinfo.io/ip发出GET请求来获取受害者机器上的公网IP，具体如下图所示。我们在group_tag文件中找到了Mac1，在client_id文件中找到了WIN-FD 。

[![](https://p3.ssl.qhimg.com/t017a35a3497c5befbf.png)](https://p3.ssl.qhimg.com/t017a35a3497c5befbf.png)

恶意软件在运行的过程中将持续与C&amp;C服务器建立链接，直到有新的数据需要它去下载。一旦新文件被下载，它们将被放置在winapp目录的modules文件夹中，如下图所示。

[![](https://p1.ssl.qhimg.com/t01c7a30db5210ca17f.png)](https://p1.ssl.qhimg.com/t01c7a30db5210ca17f.png)

大概30分钟之后，多个其他模块被下载到Modules目录，如下图所示。

[![](https://p0.ssl.qhimg.com/t015eb2c1743fb67fa9.png)](https://p0.ssl.qhimg.com/t015eb2c1743fb67fa9.png)

经过我们的的研究发现，在我们的会话中下载到的所有数据似乎都以某种方式被加密或者混淆了，目前尚不清楚木马程序中的哪些例程被加密或者混淆处理了，但是有一种方法可以尝试一下，那就是他们应该能够在未加壳版本的木马软件中找到。

**<br>**

**如何检测该木马软件？**

由于该木马软件在实现上并没有使用什么“高明”的手法，因此一些主流的防病毒扫描程序通常都能够将初始文档（DOC00039217.doc）作为脚本下载器而检测到。第二阶段的加壳文件也能够被一些主流的反病毒程序作为通用木马下载程序检测到。而且，Symantec公司的安全研究人员也对该银行木马进行了分析，并将该银行木马软件标识为Trojan.Trickybot恶意软件，该公司安全研究人员发布的有关该银行木马软件分析的技术细节似乎与本文档中的分析相似。<br>即使使用适当的BLUECOAT设备来检查HTTPS中的流量，但是GET请求字符串中的可变长度参数会使依靠流量中的特征来检测该银行木马软件变得稍微有些困难，因此最好的缓解策略是直接阻断与该银行木马软件相关的的C＆C服务器的IP地址列表，最好的做法是不启用那些陌生人发来的无法验证的Word文档中的任何宏。<br>**<br>**

**结论**

本文对一款银行木马软件的Dropper程序进行了分析，该Dropper是一个启用了宏的文档，可以下载并执行PECompact2加壳的木马程序。为了扩展其功能，恶意软件似乎有多个模块可以在受害者的机器上下载并执行程序。<br>**<br>**

**后续更新**

经过我们进一步的调查发现，DOC00039217.doc文件是TrickBot银行木马软件网络攻击活动中的一部分，被称为Dyreza的继任者。这是一个多级木马，能够向受害者的机器下载多个模块，以进行凭据窃取，银行欺诈，电子邮件劫持等操作。详情请参阅MalwareBytes和FidelisSecurity两人发布的有关该银行木马软件的深入分析文章。
