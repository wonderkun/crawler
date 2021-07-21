> 原文链接: https://www.anquanke.com//post/id/85587 


# 【技术分享】带有加载保护机制的新型Neutrino僵尸程序


                                阅读量   
                                **86701**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01b49ef20d8254ebb5.jpg)](https://p0.ssl.qhimg.com/t01b49ef20d8254ebb5.jpg)

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB（不服你也来投稿啊！）

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



本文将分析多功能Neutrino僵尸程序（也叫Kasidet）的一个最新版本，该程序通过以它命名的利用工具包（Neutrino Exploit Kit）进行分发。今年一月份时，我们已经大概描述了利用垃圾邮件传播的[Neutrino僵尸程序](https://blog.malwarebytes.com/cybercrime/2017/01/post-holiday-spam-campaign-delivers-neutrino-bot/)，因此我们不会过多讨论这些细节，而会将重点放在它的程序加载部分。

程序使用多层虚拟机检测技术对其关键核心进行了隐藏，导致我们对其最终载荷的提取工作遇到了些许挑战。

**<br>**

**一、分发机制**



程序样本从美国的恶意广告活动中捕获，这些活动使用了Neutrino Exploit Kit进行恶意程序分发。恶意程序在受害主机上首先会进行指纹检测，探测虚拟化环境，捕获网络流量以及检查反病毒软件。如果程序发现所处环境异常（即不是典型的受害主机），则放弃感染过程。程序使用落地前页面中的大量混淆的JavaScript代码完成这一检查过程，而不是使用以往的[Flash检测方法](https://blog.malwarebytes.com/cybercrime/exploits/2016/06/neutrino-ek-fingerprinting-in-a-flash/)。

[![](https://p4.ssl.qhimg.com/t011915d57c2d1c9017.png)](https://p4.ssl.qhimg.com/t011915d57c2d1c9017.png)

程序初始检查通过后，下一步骤是启动一个特制的Flash文件，其中包含一系列的Internet Explorer和Flash Player漏洞利用工具（参考[这里](http://malware.dontneedcoffee.com/2017/01/CVE-2016-7200-7201.html)的相关介绍）。最后一步是使用wscript.exe下载和执行经过RC4编码的载荷，以绕过代理网络限制。<br style="text-align: left">

总体感染流程如下所示：

[![](https://p0.ssl.qhimg.com/t010545e3b4dfef224a.png)](https://p0.ssl.qhimg.com/t010545e3b4dfef224a.png)

Maciej Kotowicz写了一个[脚本](https://github.com/mak/ekdeco/tree/master/neutrino)，可以提取Flash文件中的功能组件。

**<br>**

**二、分析的样本及哈希值**



Neutrino Exploit Kit释放的原始样本：[b2be7836cd3edf838ca9c409ab92b36d](https://www.virustotal.com/en/file/3ab39c77bde831dc734139685cada88ef7f17a6881f4ea7525a522c323562b3c/analysis/)

加载器：[349f5eb7c421ed49f9a260d17d4205d3](https://www.virustotal.com/en/file/2919dad5f685e7c14343c2eb4ba8a28d6d145c776f58168edb42efd61334c3de/analysis/)

载荷（即Neutrino僵尸程序）：[6239963eeda5df72995ad83dd4dedb18](https://www.virustotal.com/en/file/45abc50e837a3e0c4df842fe8c3aa54e103d690d67f89d78059878bd3acc67ab/analysis/)

**<br>**

**三、行为分析**<br style="text-align: left">



样本采取了保护机制以防止在受控环境中投放。当样本探测到其运行在虚拟机或沙箱中时会进行自删除操作。

[![](https://p5.ssl.qhimg.com/t012d0f5c3a5f67385b.png)](https://p5.ssl.qhimg.com/t012d0f5c3a5f67385b.png)

环境检测通过后，程序将副本拷贝到%APPDATA%/Y1ViUVZZXQxx/&lt;random_name&gt;.exe（本文中为abgrcnq.exe，uu.exe）：

[![](https://p3.ssl.qhimg.com/t0106c88bb0b5c3bf49.png)](https://p3.ssl.qhimg.com/t0106c88bb0b5c3bf49.png)

同时对释放的文件夹及文件进行隐藏。

样本通过计划任务完成本地持久化。

[![](https://p1.ssl.qhimg.com/t012a0621d982b033a7.png)](https://p1.ssl.qhimg.com/t012a0621d982b033a7.png)

样本修改添加了几个注册表键值，如安装日期等基本设置信息：

[![](https://p1.ssl.qhimg.com/t012409268f29b92099.png)](https://p1.ssl.qhimg.com/t012409268f29b92099.png)

对几个键值进行修改，以在系统里保持隐藏性。注册表中的Hidden及[SuperHidden](http://www.msfn.org/board/topic/9950-whats-superhidden-for-exactly/)功能可以使程序副本对用户保持隐藏。样本通过修改以下注册表项达到文件的隐藏性：

```
SoftwareMicrosoftWindowsCurrentVersionExplorerAdvancedHidden
SoftwareMicrosoftWindowsCurrentVersionExplorerAdvancedShowSuperHidden
```

样本利用命令将自身添加到防火墙白名单中：

```
cmd.exe " /a /c netsh advfirewall firewall add rule name="Y1ViUVZZXQxx" dir=in action=allow program=[full_executable_path]
```

与此类似，样本也将自身路径添加到Windows Defender的例外文件列表中：

[![](https://p4.ssl.qhimg.com/t01a85b45fb947bb44a.png)](https://p4.ssl.qhimg.com/t01a85b45fb947bb44a.png)

样本对终端服务设置表项进行修改，将MaxDisconnectionTime及MaxIdleTime值设为0，受影响表项为：

```
HKLMSOFTWAREPoliciesMicrosoftWindows NTTerminal ServicesMaxDisconnectionTimeHKLMSOFTWAREPoliciesMicrosoftWindows NTTerminal ServicesMaxIdleTime
```

如果安装过程一切顺利，样本将加载其核心部件，我们也可以观察到典型的Neutrino僵尸网络流量特征，比如下图中，经过base64编码的“enter”请求报文及“success”响应报文特征。响应包以注释形式嵌入到空白html页面中，避免引起用户警觉。

[![](https://p2.ssl.qhimg.com/t01de8d82fd77d4573e.png)](https://p2.ssl.qhimg.com/t01de8d82fd77d4573e.png)

程序发送自身信息作为下一个请求，而C2C服务器则会返回程序下一步要执行的命令。请求及响应报文也经过base64进行编码。解码后的一个示例为：

请求报文：

```
cmd&amp;9bc67713-9390-4bcd-9811-36457b704c9c&amp;TESTMACHINE&amp;Windows%207%20(32-bit)&amp;0&amp;N%2FA&amp;5.2&amp;22.02.2017&amp;NONE
```

响应报文：

```
1463020066516169#screenshot#1469100096882000#botkiller#1481642022438251#rate 15#
```

响应报文中，第一个命令是截屏命令，之后我们的确看到程序发送了一张JPG格式的屏幕截图：

[![](https://p3.ssl.qhimg.com/t0190be3cd03e6b8ed6.png)](https://p3.ssl.qhimg.com/t0190be3cd03e6b8ed6.png)

从发送报文中我们可知程序版本为5.2版（与这篇文章分析的类似：https://blog.malwarebytes.com/cybercrime/2017/01/post-holiday-spam-campaign-delivers-neutrino-bot/）

**<br>**

**四、深入分析**<br style="text-align: left">



程序使用的第一层是加密器层，用于覆盖内存中加载器映像的初始PE结构，可参考这里的相关[解密视频](https://www.youtube.com/watch?v=m_xh33M_CRo)。

第二层是个加载器层，防止核心程序在受控环境中（如虚拟机或调试器环境）运行。这可能是它新使用的一个功能（我们从未在之前的Neturino僵尸网中观察到）。我们发现这一层非常有效，测试期间大多数沙箱和虚拟机环境无法提供该样本的任何有用信息。

最后一层是Neutrino僵尸家族的典型功能载荷层。<br style="text-align: left">

从加载器代码中可知，它并非依附于独立加密器的一层，而是完整Neutrino僵尸包中的一个集成部分。载荷层和加载器层都采用C++进行开发，使用类似的函数，包含重叠的字符串，本文后半部分将就此进行详细分析。这两层的编译时间戳非常接近，分别为2017-02-16 17:15:43和2017-02-16 17:15:52。

可以在[这里](https://www.hybrid-analysis.com/sample/6f22f22ea510f35d3b6f9edd610e6ba3e6499ff6867f52a3361709c48d886c41?environmentId=100)找到禁用环境检查功能的加载器修复版。

**<br>**

**五、加载器分析**



**5.1 混淆技术<br>**

代码包含了基层混淆技术，几个可见的字符串如下所示：

[![](https://p4.ssl.qhimg.com/t01c84d36a8a83e8587.png)](https://p4.ssl.qhimg.com/t01c84d36a8a83e8587.png)

字符串中包含目录名、一些函数名、准备禁用的与Windows安全功能相关的注册表键值、计划任务中要添加的字符串。

大多数字符串在运行时进行解密，以下是一个加密字符串的加载过程：

[![](https://p5.ssl.qhimg.com/t018fd7122be8b5030b.png)](https://p5.ssl.qhimg.com/t018fd7122be8b5030b.png)

程序首先使用专用函数将混淆字符串写入动态加载的内存中，然后使用简单的异或方法进行解密：

```
def decode(data):
    maxlen = len(data)
    decoded = bytearray()
    for i in range(0, maxlen):
        dec = data[i] ^ 1
        decoded.append(dec) 
    return decoded
```

解密后的字符串为：

[![](https://p2.ssl.qhimg.com/t0139db5915401ecd8e.png)](https://p2.ssl.qhimg.com/t0139db5915401ecd8e.png)

大多数API调用同样也经过了动态解析处理，如：

[![](https://p2.ssl.qhimg.com/t01d3234c427a7a3662.png)](https://p2.ssl.qhimg.com/t01d3234c427a7a3662.png)

跟踪API调用可以理解程序的功能，因此样本的作者不使用某些API，而是自己实现了这些函数功能。比如，作者通过读取[底层线程环境块](http://www.geoffchappell.com/studies/windows/win32/ntdll/structs/teb/index.htm)（Thread Envioroment Block，TEB）结构实现了GetLastError()的功能：

[![](https://p4.ssl.qhimg.com/t011e8ba8060b4d76a1.png)](https://p4.ssl.qhimg.com/t011e8ba8060b4d76a1.png)

**5.2 功能分析**

加载器创建了一个互斥量（mutex）以避免重复执行，mutex名为1ViUVZZXQxx，硬编码在样本文件中。

加载器的主要任务是环境检查，以确保软件运行不受监视。与大多数恶意软件不同，环境检查工作不是只执行一次，而是有一个专门线程负责这项工作：

[![](https://p4.ssl.qhimg.com/t0122f7781c0be2b5fe.png)](https://p4.ssl.qhimg.com/t0122f7781c0be2b5fe.png)

它在死循环中不断重复这一工作：

[![](https://p0.ssl.qhimg.com/t014adbfdc939f88a79.png)](https://p0.ssl.qhimg.com/t014adbfdc939f88a79.png)

如果程序在任一时刻检测到某些位于黑名单中的进程，则会终止自身执行。

**典型的检查过程如下：<br style="text-align: left">**

1. 枚举当前运行的进程列表（使用动态加载CreateToolhelp32Snapshot、Process32First、Process32Next函数完成）。计算每个进程名的校验和，与内置的进程黑名单进行比较。

[![](https://p3.ssl.qhimg.com/t01fcee5c27ff172b42.png)](https://p3.ssl.qhimg.com/t01fcee5c27ff172b42.png)

校验和黑名单如下：

```
0x6169078A
0x47000343
0xC608982D
0x46EE4F10
0xF6EC4B30
0xB1CBC652 ; vboxservice.exe
0x6D3E6FDD ; vboxtray.exe
0x583EB7E8
0xC03EAA65
```

黑名单进程的枚举实现代码如下图所示。从中可知每个函数都在对应校验和下动态加载执行：

[![](https://p0.ssl.qhimg.com/t016b34243cd1697e16.png)](https://p0.ssl.qhimg.com/t016b34243cd1697e16.png)

2. 在当前进程中搜索黑名单中的模块（使用动态加载CreateToolhelp32Snapshot、Module32First、Module32Next函数完成）。类似地，程序计算每个进程名的校验和并与内置黑名单进行比较。

校验和计算算法为（详细的实现[在此](https://gist.github.com/hasherezade/aefabdb9a67193ef05c93228a78c20c6#file-checksum-cpp)）：

[![](https://p3.ssl.qhimg.com/t01df080e508712f9c4.png)](https://p3.ssl.qhimg.com/t01df080e508712f9c4.png)

校验和黑名单为：

```
0x1C669D6A
0xC2F56A18
0xC106E17B
0x5608BCC4
0x6512F9D0
0xC604D52A
0x4D0651A5
0xAC12B9FB ; sbiedll.dll
0x5B747561
0x53309C85
0xE53ED522
```

3. 使用IsDebuggerPresent、CheckRemoteDebuggerPresent判断程序是否正被调试。

4. 使用GetTickCount、Sleep、GetTickCount进行单步执行时间检测。

5. 使用QueryDosDevices（如VBoxGuest）检测黑名单设备，判断是否处于虚拟环境中。

6. 使用EnumWindows、GetClassName（如procexpl）检查并隐藏黑名单程序窗口。

[![](https://p4.ssl.qhimg.com/t01ff5f32ccb1defb2c.png)](https://p4.ssl.qhimg.com/t01ff5f32ccb1defb2c.png)

校验和黑名单为：

```
0xFE9EA0D5
0x6689BB92
0x3C5FF312 ; procexpl
0x9B5A88D9 ; procmon_window_class
0x4B4576B5
0xAED304FC
0x225FD98F
0x6D3FA1CA
0xCF388E01
0xD486D951
0x39177889
```

另一个线程中，样本执行与bot安装的相关操作，如在计划任务中添加任务、往防火墙中添加例外等。

最后，样本释放并使用PE运行方法启动最终载荷。首先，它创建自身的另一个实例：

[![](https://p4.ssl.qhimg.com/t014e1c45dd744532e2.png)](https://p4.ssl.qhimg.com/t014e1c45dd744532e2.png)

其次，在同一位置映射一个新的PE文件：

[![](https://p2.ssl.qhimg.com/t0144cadffa382fdf65.png)](https://p2.ssl.qhimg.com/t0144cadffa382fdf65.png)

**5.3 载荷分析**

有效载荷就是一个Neutrino僵尸程序，其功能与我们[先前文章](https://blog.malwarebytes.com/cybercrime/2017/01/post-holiday-spam-campaign-delivers-neutrino-bot/)中分析的非常类似，我们可以在加载器中找到某些类似的元素，比如下图中的字符串：

[![](https://p2.ssl.qhimg.com/t01e53c61490ff75e78.png)](https://p2.ssl.qhimg.com/t01e53c61490ff75e78.png)

**<br>**

**六、结论**



Neutrino僵尸程序已经风行好几年，它功能丰富，但内部结构则让人印象平平。本文分析的Neutrino僵尸程序同样如此，恶意软件作者没有对程序的结构做任何显著的改进，但他们为程序添加了一个保护层，可以对运行环境做极其严格的指纹检测，避免程序被轻易探测到。

<br style="text-align: left">
