> 原文链接: https://www.anquanke.com//post/id/150521 


# RIG EK的PROPagate注入技术分析


                                阅读量   
                                **109095**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2018/06/rig-ek-delivering-monero-miner-via-propagate-injection-technique.html](https://www.fireeye.com/blog/threat-research/2018/06/rig-ek-delivering-monero-miner-via-propagate-injection-technique.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t015e22ca91a5c202d1.png)](https://p5.ssl.qhimg.com/t015e22ca91a5c202d1.png)

## 介绍

通过FireEye动态威胁情报（DTI）检测，我们观察到RIG Exploit Kit（EK）提供了一个dropper，以利用[PROPagate注入技术](http://www.hexacorn.com/blog/2017/10/26/propagate-a-new-code-injection-trick/)注入用来下载并执行Monero挖矿软件的代码（[趋势科技](https://blog.trendmicro.com/trendlabs-security-intelligence/rig-exploit-kit-now-using-cve-2018-8174-to-deliver-monero-miner/)也曾报告过类似的活动）。除了利用了一些知名度相对较小的注入技术之外，该攻击链中还有一些其他有趣的东西，让我们在这篇博文中一一道来。



## 攻击链

当用户访问一个在iframe中加载RIG EK登录页面的被入侵网站时，攻击链就会启动，RIG EK使用各种技术来传递NSIS（Nullsoft Scriptable Install System）加载器，该加载器会利用PROPagate注入技术来将shellcode注入到explorer.exe中，而这个shellcode则负责执行下一个payload，以下载并执行Monero挖矿软件。攻击链的流程图如图1所示。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig1a.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig1a.png)

图1. 攻击链流程图



## Exploit Kit 分析

当用户访问一个被使用iframe注入入侵的受感染网站时，iframe就会加载登陆页面。注入到受感染网站的iframe如图2所示。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig2.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig2.png)图2：被注入的iframe

登录页面包含三个不同的JavaScripts片段，每个片段使用不同的技术来传递payload。这些也都不是一些新技术，因此我们在本文中会对每一种做一个简要介绍。



## JavaScript 1

第一个JS有一个函数——fa——用来返回一个使用execScript函数执行的VBScript，如图3中的代码所示。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig3.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig3.png)图3：JavaScript 1代码片段

这个VBScript利用了[CVE-2016-0189](https://www.fireeye.com/blog/threat-research/2016/07/exploit_kits_quickly.html)漏洞，这个CVE漏洞可让它下载payload并使用图4中所示的代码来执行它。[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig4.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig4.png)

图4：VBScript代码片段



## JavaScript 2

第二个JavaScript包含了一个用来检索其他JavaScript代码的函数，其使用图5中所示的代码片段将此脚本代码添加到HTML页面中。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig5.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig5.png)图5：JavaScript 2代码片段

这一段新添加的JavaScript代码利用了[CVE-2015-2419](https://www.fireeye.com/blog/threat-research/2015/08/cve-2015-2419_inte.html)漏洞，而此漏洞又利用了一个[JSON.stringify](https://www.fireeye.com/blog/threat-research/2015/08/cve-2015-2419_inte.html)中的漏洞。该脚本会通过在图6所示的变量中存储漏洞的EXP部分来混淆其对JSON.stringify的调用。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig6.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig6.png)图6：利用变量来进行混淆

依靠这些变量，这个JavaScript会调用带有错误格式的参数的JSON.stringify以触发CVE-2015-2419漏洞，这反过来则可以导致本机代码执行，如图7所示。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig7.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig7.png)图7：调用JSON.Stringify



## JavaScript 3

第三个JavaScript中包含了添加一个额外JS脚本所需的代码，类似于第二个JavaScript。这个额外的JavaScript会添加了一个利用[CVE-2018-4878](https://www.fireeye.com/blog/threat-research/2018/02/attacks-leveraging-adobe-zero-day.html)漏洞的flash对象，如图8所示。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig8.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig8.png)图8：JavaScript 3代码片段

一旦漏洞利用成功，shellcode就会调用命令行来创建一个文件名为u32.tmp的JavaScript文件，如图9所示。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig9.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig9.png)图9：WScript命令行

这个JavaScript文件由WScript启动，它可以下载下一阶段的payload并使用图10中的命令行执行它。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig10.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig10.png)图10：WScript中的恶意命令行



## payload分析

在此攻击过程中，攻击者使用了多个payload和反分析技术来绕过分析环境。图11显示了该恶意软件的完整活动流程图。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig11a.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig11a.png)图11：恶意软件活动流程图



## NSIS加载器（SmokeLoader）分析

RIG EK丢弃的第一阶段的payload是一个已编译的NSIS可执行文件，俗称SmokeLoader。除了NSIS文件之外，payload还有两个组成部分：一个DLL和一个数据文件（在这一次的分析案例中名为’kumar.dll’和’abaram.dat’），此DLL具有一个由NSIS可执行文件调用的导出函数，而此导出函数可以读取和解密数据文件的代码，从而生成第二阶段payload（一个可移植的可执行文件）。

然后该DLL在SUSPENDED_MODE中生成自己（dropper）并使用process hollowing技术来注入解密后的PE。



## 注入代码（第二阶段payload）分析

第二阶段的payload是一个高度混淆的可执行文件，它由一个可以解密代码、执行它并对它进行重新加密的例行程序组成。

在可执行文件的入口处，包含了一段通过从进程环境块（PEB）中提取信息来检查操作系统主要版本号的代码，如果操作系统版本值小于6（在Windows Vista之前），则可执行文件将会自行终止。它还包含一段从PEB的偏移量0x2中提取信息来检查可执行文件是否处于调试模式的代码，如果设置了`BeingDebugged`标志，则可执行文件也将自行终止。

恶意软件还会通过打开值为0的注册表项**HKLM SYSTEM ControlSet001 Services Disk Enum**来进行Anti-VM检查。它会检查注册表值数据是否包含以下字符串：vmware、virtual、qemu或xen，而这些字符串都意味着目标是一台虚拟机。

在进行了反分析和环境检查后，恶意软件才开始执行核心代码。

恶意软件使用来[PROPagate注入技术](http://www.hexacorn.com/blog/2017/10/26/propagate-a-new-code-injection-trick/)来在目标进程中注入并执行代码。PROPagate方法类似于SetWindowLong注入技术。在此方法中，恶意软件使用SetPropA函数修改UxSubclassInfo的回调，并使远程进程执行它的恶意代码。

这种代码注入技术仅适用于具有相对自身较低或相等的完整性级别的进程，恶意软件首先会检查当前正在运行的进程的完整性是否为中等完整性级别（2000，SECURITY_MANDATORY_MEDIUM_RID）。下图显示了代码片段。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig12.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig12.png)图12：检查当前进程的完整性级别的代码片段

如果进程高于中等完整性级别，则恶意软件会继续进行，而如果该进程低于了中等完整性级别，则恶意软件将以中等完整性重新生成。

恶意软件创建文件映射对象并将dropper文件路径写入其中，然后通过注入的代码访问相同的映射对象，以读取dropper文件路径并删除dropper文件。映射对象的名称源自系统驱动器的卷序列号和带有硬编码值的XOR操作（如图13）。

**文件映射对象名称=“卷序列号”+“卷序列号”XOR 0x7E766791**

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig13.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig13.png)图13：创建文件映射对象名称

然后，恶意软件利用XOR来解密第三阶段的payload，并使用RTLDecompressBuffer对其进行解压缩。第三阶段payload也是一个PE可执行文件，但作者已修改文件头以避免在内存扫描中将其检测为PE文件。如图14，在解密数据开始时修改了几个头字段后，我们得到了正确的可执行头。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig14.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig14.png)图14：没有头（左）和有头（右）的注入可执行文件

解密payload后，恶意软件将shell进程explorer.exe作为恶意代码的注入目标。它使用GetShellWindow和GetWindowThreadProcessId API来获取shell窗口的线程ID（图15）。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig15.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig15.png)图15：获取shell窗口线程ID

恶意软件会在远程进程（explorer.exe）中注入并映射解密的PE，同时它还会注入一个在SetPropA中配置为回调函数的shellcode。

将payload注入到目标进程之后，它会使用EnumChild和EnumProps函数来枚举shell窗口属性列表中的所有条目，并将其与UxSubclassInfo进行比较，找到shell窗口的UxSubclassInfo属性后，它会保存句柄信息并通过SetPropA用其设置回调函数。

SetPropA有三个参数，第三个是数据。回调程序地址存储在距数据开头的偏移量0x14处。恶意软件使用注入的shellcode地址来修改回调地址（图16）。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig16.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig16.png)图16：修改回调函数

然后，恶意软件将特定消息发送到窗口以执行与UxSubclassInfo属性相对应的回调程序，这一步则可以导致shellcode的执行。

shellcode包含使用CreateThread执行注入的第三阶段payload的入口点地址的代码，然后它会重置SetPropA的回调，该回调在PROPagate注入期间会被恶意软件修改。图17显示了注入的shellcode的代码片段。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig17.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig17.png)图17：注入的shellcode的组装视图



## 第三阶段payload分析

在执行恶意代码之前，恶意软件会执行反分析检查，以确保系统中没有运行任何分析工具。它创建了两个永久运行的线程，其中就包含来用于实现反分析检查的代码。

第一个线程使用CreateToolhelp32Snapshot来枚举进程，并检查在分析中通常会使用的进程名称。它使用自定义操作从进程名称生成DWORD哈希值，并将其与硬编码的DWORD值数组进行比较，如果生成的值与数组中的任一值相匹配，则将相应的进程终止。

第二个线程使用EnumWindows来枚举窗口。它使用GetClassNameA函数来提取与相应窗口关联的类名。与第一个线程一样，它使用自定义操作从类名生成DWORD哈希值，并将其与硬编码的DWORD值数组进行比较，如果生成的值与数组中的任何值匹配，则终止与相应窗口相关的进程。

除了以上这两种反分析技术之外，它还具有通过尝试访问URL来检查互联网连接的代码：www.msftncsi[.]com/ncsi.txt。

为了在系统中保持持久性，恶意软件在％startup％文件夹中创建计划任务和快捷方式。计划任务名为“Opera Scheduled Autoupdate `{`GetTickCount()的十进制`}`”。

然后恶意软件会与恶意URL进行通信以下载最终的payload，即Monero挖矿软件。它使用Microsoft CryptoAPIs从计算机名称和卷信息创建MD5哈希值，并在POST请求中将哈希值发送到服务器。图18显示了这一网络通信过程。

[![](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig18.png)](https://www.fireeye.com/content/dam/fireeye-www/blog/images/RigEkMonero/Fig18.png)图18：网络通信过程

最后，恶意软件从服务器下载最终payload：Monero挖矿软件，并将其安装到系统中。



## 结论

虽然我们一直在观察到Exploit Kit活动呈减少趋势，但攻击者并没有完全放弃它们。在本文中，我们探讨了RIG EK如何与各种漏洞EXP来进行端点破坏，还展示了NSIS Loader如何利用鲜为人知的PROPagate流程注入技术，其目的很有可能是为了逃避安全产品。

FireEye MVX和FireEye Endpoint Security（HX）平台在攻击链的几个阶段都检测到了此攻击。

审核人：yiwang   编辑：边边
