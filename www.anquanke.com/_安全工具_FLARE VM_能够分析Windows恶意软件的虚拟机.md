> 原文链接: https://www.anquanke.com//post/id/86523 


# 【安全工具】FLARE VM：能够分析Windows恶意软件的虚拟机


                                阅读量   
                                **176585**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：www.fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2017/07/flare-vm-the-windows-malware.html](https://www.fireeye.com/blog/threat-research/2017/07/flare-vm-the-windows-malware.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01906f4074abe77c03.png)](https://p5.ssl.qhimg.com/t01906f4074abe77c03.png)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**一、前言**

****

作为FLARE团队的一名逆向分析工程师，我需要使用定制的虚拟机（VM）来分析恶意软件。这种虚拟机使用的是Windows系统，里面内置了许多小工具，可以辅助恶意软件分析过程。不幸的是，为了维护这样一个定制版虚拟机我们需要付出许多精力：里面的工具经常会过期，并且我们很难改变或添加新的东西。还有一个问题，如果虚拟机不小心损坏了，想要完全复制我费尽多年心思调整的设置及收集的工具是一个非常烦人的过程。为了解决这些难题，我研发了一种标准化的（同时定制起来也非常简单的）、基于Windows的用于安全研究的虚拟机，即FLARE VM。

FLARE VM是一款以Windows为基础的免费开源的虚拟机，专为逆向分析工程师、恶意软件分析研究员、事件响应人员、安全取证人员以及渗透测试者设计。FLARE VM借鉴了基于Linux的安全开源发行版的思想（如Kali Linux、REMnux以及其他Linux发行版），提供了经过全面配置的一个平台，全面集成了Windows安全工具，包括调试器、反汇编器、反编译器、静态及动态分析工具、网络分析及网络操作工具、Web资产评估工具、漏洞利用工具、漏洞评估等应用程序。

FLARE VM中还包含FLARE团队研发的公开版恶意软件分析工具，如FLOSS以及FakeNet-NG等。

<br>

**二、如何获取**



首先你需要安装Windows 7或更高版本的操作系统，这样你就能自己选择所需的Windows版本、补丁级别、系统架构以及虚拟化环境。

完成上述步骤后，你可以在IE浏览器中访问如下链接快速部署FLARE VM环境（不能使用其他浏览器）：

[http://boxstarter.org/package/url?https://raw.githubusercontent.com/fireeye/flare-vm/master/flarevm_malware.ps1](http://boxstarter.org/package/url?https://raw.githubusercontent.com/fireeye/flare-vm/master/flarevm_malware.ps1)

在IE浏览器中访问该URL后，浏览器会弹出一个Boxstarter WebLauncher对话框。点击“Run”按钮，继续安装过程，如图1所示。 

[![](https://p0.ssl.qhimg.com/t01a6606b131b112488.png)](https://p0.ssl.qhimg.com/t01a6606b131b112488.png)

图1. 安装FLARE VM

成功安装完Boxstarter WebLauncher后，你会看到一个控制台窗口，提示你输入Windows密码，如图2所示。安装过程中会多次重启系统，为了实现自动登录，你需要在此提供Windows密码。

 [![](https://p0.ssl.qhimg.com/t01fc3b8c257f18a92f.png)](https://p0.ssl.qhimg.com/t01fc3b8c257f18a92f.png)

图2. Boxstarter密码提示窗口

接下来所有的安装过程是完全自动化的，你可以倒上一杯咖啡或茶，休息一下。初始安装大概需要30-40分钟，具体时间取决于你的网络连接速度。由于这个过程需要安装多种软件，因此系统会重启若干次。在部署过程中，你可以从安装日志中找到具体安装的软件包。

安装完成后，强烈建议你将虚拟机网络切换到仅主机（Host-Only）模式，防止恶意软件样本自动连接到互联网或本地网络。另外，我们也建议你将新安装的状态保存为虚拟机快照。FLARE VM安装完后的界面如图3所示。

[![](https://p3.ssl.qhimg.com/t01b94add83470cb498.png)](https://p3.ssl.qhimg.com/t01b94add83470cb498.png)

图3. FLARE VM安装

注意：如果在安装过程中碰到大量错误信息，你可以尝试重新安装。重新安装时会保留已安装的软件包，安装新的软件包。

<br>

**三、新手上路**

****

虚拟机的配置以及内置工具的选择都经过FLARE团队的研发或精心挑选，团队成员在恶意软件逆向分析、漏洞分析及利用、恶意软件分析教学方面有十多年的资深经验。这些工具在本地磁盘中的目录结构如图4所示。

 [![](https://p1.ssl.qhimg.com/t01f2fe8af0e9e9a189.png)](https://p1.ssl.qhimg.com/t01f2fe8af0e9e9a189.png)

图4. FLARE VM工具集

我们尝试在FLARE文件夹中以快捷方式提供所有工具的使用接口，但某些工具只能通过命令行来使用。大家可以参考在线文档，了解最新的工具列表。

<br>

**四、样本分析**

****

为了向大家展示FLARE VM在恶意软件分析方面的优秀表现，我们可以利用它来分析某个示例样本，该样本也是我们在恶意软件分析课程中使用的一个示例样本。

首先，我们可以搜索样本文件中的字符串，提取一些基本信息。在本次实验中，我们准备使用FLARE自己研发的FLOSS工具来完成这一任务，该工具是一个字符串分析工具，大家可以访问该网址了解该工具的更多信息。你可以点击任务栏中的FLOSS图标运行此工具，使用它来分析样本，如图5所示。 

[![](https://p1.ssl.qhimg.com/t010c1184873d290e0d.png)](https://p1.ssl.qhimg.com/t010c1184873d290e0d.png)

图5. 运行FLOSS

不幸的是，工具的输出结果中只有一个字符串比较特别，并且我们现在还不知道该字符串的具体用途，如图6所示。

[![](https://p4.ssl.qhimg.com/t01a615493baea25b65.png)](https://p4.ssl.qhimg.com/t01a615493baea25b65.png)

图6. 字符串分析

我们需要深入分析这个样本，打开CFF Explorer，分析样本的导入表、资源以及PE头部结构。我们可以从桌面或者开始菜单中找到FLARE文件夹，里面包含CFF Explorer以及其他许多工具，如图7所示。

[![](https://p5.ssl.qhimg.com/t015c3b0dad51350300.png)](https://p5.ssl.qhimg.com/t015c3b0dad51350300.png)

图7. 可以使用的工具集

分析PE头部时，我们通过几条线索发现该样本文件中包含一个具有附加载荷的资源对象。比如，导入地址表（Import Address Table）中包含与资源对象有关的Windows API调用，如LoadResource、FindResource以及WinExec。不幸的是，样本内置的“BIN”载荷中包含垃圾数据，因此这些信息可能经过加密处理，如图8所示。 

[![](https://p4.ssl.qhimg.com/t0112deba99b329feb4.png)](https://p4.ssl.qhimg.com/t0112deba99b329feb4.png)

图8. PE资源

此时此刻，我们可以继续进行静态分析，或者我们可以使用稍微“骗人”的方法，也就是采用基本的动态分析技术。 我们可以尝试使用另一款FLARE工具——FakeNet-NG¬——来收集基本线索。FakeNet-NG是一款动态网络仿真工具，可以为恶意软件提供伪造的服务（如DNS、HTTP、FTP、IRC以及其他工具），欺骗恶意软件，使恶意软件暴露其网络功能。大家可以访问此网址了解该工具的更多信息。

此外，我们还需运行Sysinternals Suite中的Procmon工具，以便监控样本的文件、注册表以及Windows API行为。你可以在任务栏中找到这类常用工具，如图9所示。 

[![](https://p0.ssl.qhimg.com/t0141f1fcaa98e04445.png)](https://p0.ssl.qhimg.com/t0141f1fcaa98e04445.png)

图9. 动态分析

以管理员权限运行恶意软件样本后，我们很快就找到了样本的网络及主机特征。FakeNet-NG响应了恶意软件的请求，如图10所示，恶意软件试图使用HTTP协议与evil.mandiant.com通信。这里我们捕捉到一些有价值的特征，如完整的HTTP头部信息、URL以及可能是独一无二的User-Agent字符串。此外，FakeNet-NG识别出负责通信的具体进程为level1_payload.exe。这个进程名与我们在静态分析中提取到的独特字符串相符，当时我们还不知道这个字符串所代表的具体含义。

 [![](https://p4.ssl.qhimg.com/t01070b536ed62a864e.png)](https://p4.ssl.qhimg.com/t01070b536ed62a864e.png)

图10. FakeNet-NG

Procmon的输出结果如图11所示，将该结果与我们已掌握的信息进行对比，我们可以确定恶意软件的确会在system32目录中生成level1_payload.exe可执行程序。 

[![](https://p3.ssl.qhimg.com/t01a05db19a19863da9.png)](https://p3.ssl.qhimg.com/t01a05db19a19863da9.png)

图11. Procmon

作为恶意软件分析过程中的一个环节，我们可以继续深入分析，在反汇编器中加载恶意样本，然后在调试器中继续分析样本。然而，我不想在这里就把所有答案揭晓，这样就会失去恶意软件分析教学中的乐趣。能够完成此类分析任务的相关工具都已集成到该虚拟机中，如IDA Pro、Binary Ninja反汇编器、许多优秀的调试器以及插件，还有其他一些工具等，这些工具能够让我们的逆向分析任务事半功倍。

<br>

**五、如何定制**

****

FLARE VM是一个不断发展和改变的项目。虽然我们想尽可能覆盖所有使用场景，然而项目的内在特性决定了这是无法完成的任务。幸运的是，由于FLARE VM建立在Chocolatey项目的基础上，因此定制起来非常简单。Chocolatey是一个基于Windows的软件包管理系统，包含上千个软件包，你可以在该网页中找到项目支持的软件包列表。除了使用公开的Chocolatey仓库之外，FLARE VM也使用了自己的FLARE仓库，这个仓库的规模会随着时间的推进不断增长，目前已包含40个软件包。

这样一来，如果你想快速添加某些软件包（比如Firefox），你再也不需要去访问软件开发者的网站，只需要打开控制台，输入命令就能自动下载及安装任何软件包，如图12所示。

[![](https://p1.ssl.qhimg.com/t01a652cdf1f73dda16.png)](https://p1.ssl.qhimg.com/t01a652cdf1f73dda16.png) 

图12. 安装软件包

经过短暂的等待，无需用户交互，Firefox就会自动安装完毕，你可以在桌面上找到Firefox图标。

<br>

**六、保持更新**

****

我们在本文开头就提到过，非托管型虚拟机最大的一个难题就是如何保持所有工具处于最新版状态，FLARE VM完美解决了这个问题。通过一条命令，我们就能完全更新整个系统，如图13所示。

 [![](https://p3.ssl.qhimg.com/t015baa97068d1857bb.png)](https://p3.ssl.qhimg.com/t015baa97068d1857bb.png)

图13. 保持更新

如果已安装的软件包存在更新的版本，那么新版本就会被自动下载及安装。

注意：更新系统后别忘了做个纯净版的快照，同时将网络切换为仅主机模式。

<br>

**七、总结**

****

希望大家喜欢这个新的免费工具，信任这个工具，在逆向工程及恶意软件分析任务中充分发挥它的能力。下一次如果我们需要创建一个新的恶意软件分析环境，可以尝试FLARE VM。

受本文篇幅所限，我们只是稍微介绍了FLARE VM所具备的能力，如果大家在使用过程中有任何意见或建议，可以到Github页面或者相关页面进行反馈。


