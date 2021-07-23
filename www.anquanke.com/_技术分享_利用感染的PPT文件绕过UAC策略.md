> 原文链接: https://www.anquanke.com//post/id/86903 


# 【技术分享】利用感染的PPT文件绕过UAC策略


                                阅读量   
                                **80173**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：hackersgrid.com
                                <br>原文地址：[http://hackersgrid.com/2017/09/ppt-exploiting-cve-2017-0199.html](http://hackersgrid.com/2017/09/ppt-exploiting-cve-2017-0199.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t013b75296fa5aef5c6.jpg)](https://p5.ssl.qhimg.com/t013b75296fa5aef5c6.jpg)

译者：[an0nym0u5](http://bobao.360.cn/member/contribute?uid=578844650)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**新式PPT攻击流程**

FortiGuard 实验室最近发现了一种新的恶意PPT文件，名为**ADVANCED DIPLOMATIC PROTOCOL AND ETIQUETTE SUMMIT.ppsx**，浏览幻灯片可以发现该恶意文件针对的目标为联合国机构、外交使馆、国际组织及与他国政府有交往的人，我们将会分析此恶意PPT文件会如何控制你的系统，以下是大概的攻击流程。

[![](https://p4.ssl.qhimg.com/t01b12f681998f67dd0.png)](https://p4.ssl.qhimg.com/t01b12f681998f67dd0.png)

图1 攻击流程图

**<br>**

**CVE-2017-0199**

攻击利用了**CVE-2017-0199**漏洞，该漏洞于2017年4月公布并修复，当在微软Office或WordPad下解析特殊构造的文件时会触发远程代码执行，在微软Office的OLE接口下成功利用此漏洞的攻击者可以控制感染的计算机系统，WayneLow[1]很好地分析过该漏洞。

这已经不是第一次遇到攻击者利用该漏洞了，之前我们见过此漏洞被用在传播**REMCOS RAT**恶意软件的PPT幻灯片中，不过这次攻击区别于基于鼠标移动的PPT文件攻击，利用ppaction://protocol发起PowerShell指令，打开感染的PPT文件时会触发ppt/slides/_rels/slide1.xml.rels中的脚本，然后从hxxp://www[.]narrowbabwe[.]net:3345/exp[.]doc下载远程代码，利用PPT动画播放特性执行代码，恶意构造的文件在Target后有大量的空格来逃避YARA检测（YARA是唯一软件分析检测工具）。

[![](https://p2.ssl.qhimg.com/t0150f27de7ebbe9055.png)](https://p2.ssl.qhimg.com/t0150f27de7ebbe9055.png)

图2 利用CVE-2017-0199的PPSX文件

观察文件执行时的网络流量可以看到特意构造的文件成功利用了漏洞并下载执行了exp.doc文件，这不是doc文件而是一个包含javascriot代码的XML文件。

[![](https://p2.ssl.qhimg.com/t01e3bf3a3fb84622ed.png)](https://p2.ssl.qhimg.com/t01e3bf3a3fb84622ed.png)

图3 PPTX文件的网络流量

**<br>**

**UAC绕过提权**

从XML文件中提取出JavaScript代码后可以看到它会在%Temp%Microsoft_Office_Patch_KB2817430.jse中写入一个文件，文件名模仿了微软Office的补丁名来降低可疑度并试图展现合法文件的行为，但显然并非如此。

[![](https://p2.ssl.qhimg.com/t01aa7e69ce90497f8a.png)](https://p2.ssl.qhimg.com/t01aa7e69ce90497f8a.png)

图4 嵌入JavaScript代码的XML文件

此样本除了利用CVE漏洞外还利用了绕过WindowsUAC安全策略的技术来以高权限执行代码，更高的权限等同于更多的授权和更多被允许的行为。UAC绕过技术包括劫持HKCUsoftwareclassesmscfileshellopencommand中的注册表并执行eventvwr.exe，你可以在这里[2]更深入的了解UAC绕过和权限提升相关的技术。

[![](https://p5.ssl.qhimg.com/t01b1d9c5de4b9b90c9.png)](https://p5.ssl.qhimg.com/t01b1d9c5de4b9b90c9.png)

图5 绕过UAC策略的注册表增加项

**<br>**

**分析JavaScript**

以高权限运行的Microsoft_Office_Patch_KB2817430.jse恶意软件包含以下代码：

[![](https://p4.ssl.qhimg.com/t01a9b0903ef292ff1c.png)](https://p4.ssl.qhimg.com/t01a9b0903ef292ff1c.png)

图6 Microsoft_Office_Patch_KB2817430.jse文件

在以上代码中，**WMI ActiveScriptConsumers**得到了持久利用，创建定时器事件使得脚本每12秒执行一次，运行它的脚本编码存储在注释中。

[![](https://p4.ssl.qhimg.com/t016778fe0dd44dbf7b.png)](https://p4.ssl.qhimg.com/t016778fe0dd44dbf7b.png)

图7 解码后的脚本

**<br>**

**从JPG文件中获取C&amp;C服务器信息**

解码注释中的代码后，脚本读取下列注册项，如果不存在就创建它们。



```
HKLMSOFTWAREMicrosoftWindowsCurrentVersionInternet SettingsUser AgentSeed0
HKLMSOFTWAREMicrosoftWindowsCurrentVersionInternet SettingsUser AgentFeed0
```

[![](https://p4.ssl.qhimg.com/t0136e5fcfb721b2204.png)](https://p4.ssl.qhimg.com/t0136e5fcfb721b2204.png)

图8 名为Feed0和Seed0的注册表向项

写入到注册表项中的值经过了Microsoft_Office_Patch_KB2817430.jse文件的硬编码，解码后值为hxxp://narrowbabwe[.]net/comsary/logo[.]jpg，脚本发起对此URL的请求，但是不会有任何回应，借助VirusTotal可以获取到/logo.jpg文件。

[![](https://p1.ssl.qhimg.com/t015b540b1b5d45d86a.png)](https://p1.ssl.qhimg.com/t015b540b1b5d45d86a.png)

图9 篡改的jpg文件

有了/logo.jpg后可以继续分析样本，jpg文件有一损坏部分，这意味着攻击者篡改了图片以隐藏一些数据，隐藏信息/数据这是非常有效的技术因为jpg文件一般被认为是非恶意文件。

[![](https://p5.ssl.qhimg.com/t018de5d165c2d50117.png)](https://p5.ssl.qhimg.com/t018de5d165c2d50117.png)

图10 获取隐藏数据的代码

代码获取了Response_Text长度或者文件结尾并截取0x80h长度，作为编码数据的开始部分，if语句比较jpg文件中硬编码的值为95,2,7的标记。如果不满足if条件则无返回值，如果匹配到标记，则会从i偏移处获取44字符长度的substr，作为编码的URL。

[![](https://p5.ssl.qhimg.com/t01e26eceae95c359bb.png)](https://p5.ssl.qhimg.com/t01e26eceae95c359bb.png)

图11 篡改的数据

编码后的URL会被写入到名为/Seed0的注册表，解码后的值为hxxp://www[.]narrowbabwe[.]net/comsary/index[.]php。

[![](https://p0.ssl.qhimg.com/t0109edd21ae3e86db5.png)](https://p0.ssl.qhimg.com/t0109edd21ae3e86db5.png)

图12 Seed0注册表项

**<br>**

**C&amp;C通信**

下一步通过获取网络适配器配置来辨别代码是否在虚拟环境中运行并搜索是否存在**Virtual值**。

[![](https://p0.ssl.qhimg.com/t014b90f5be6cc801b8.png)](https://p0.ssl.qhimg.com/t014b90f5be6cc801b8.png)

图13 检查虚拟环境

有意思的是，要发送的数据取决于是否找到了Virtual字符串，如果没找到，收集的数据会包含受感染机器的&amp;ipaddr（IP地址）和&amp;macaddr（MAC地址）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012b4f105b5a4a1171.png)

图14 从感染机器收集的信息

收集到需要的信息后进行编码并利用HTTP POST请求发送到hxxp://www[.]narrowbabwe[.]net/comsary/index[.]php

[![](https://p2.ssl.qhimg.com/t0144e4d9b8beeca98a.png)](https://p2.ssl.qhimg.com/t0144e4d9b8beeca98a.png)

图15 向C&amp;C发起的HTTP POST请求

要发送的数据格式如下：

[![](https://p1.ssl.qhimg.com/t0156b897c37c2a6d60.png)](https://p1.ssl.qhimg.com/t0156b897c37c2a6d60.png)

图16 编码后要发送的数据

不幸的是，在我们分析的时候C&amp;C服务器已经下线所以没收到任何响应，不过仍然可以从下面的代码确认C&amp;C的响应包含通过eval()函数执行的任意指令，这些指令可以是传送数据的下载函数，最常用的恶意间谍软件是RATs（Remote Access Trojans）。

[![](https://p2.ssl.qhimg.com/t017faab55db5d6ad7b.png)](https://p2.ssl.qhimg.com/t017faab55db5d6ad7b.png)

图17 命令和结果执行

一旦来自C&amp;C服务器的指令执行完成，会利用下面的HTTP POST请求字符串格式向服务器发回一个通知。

[![](https://p3.ssl.qhimg.com/t0177d513dc68ce3315.png)](https://p3.ssl.qhimg.com/t0177d513dc68ce3315.png)

图18 命令执行结果POST通知

**<br>**

**总结**

分析揭示出，该恶意代码用到了多重技术手段来躲避检测并保持有效性，这些技术包括利用CVE-2017-0199、UAC绕过技术、权限提升技术、多层嵌入式编码脚本、分阶段URL连接、嵌入C&amp;C信息到jpg文件等，这展示了攻击者可以利用他们的恶意文件实现持久攻击。

**<br>**

**解决办法**

1、 升级微软更新的漏洞修复补丁

2、 FortiGuard反病毒服务检测这种威胁MSOffice/Downloader!exploit.CVE20170199

3、 FortiGuard Web拦截服务可以阻断所有C&amp;C和相关URLs

4、 FortiSandbox视PPSX文件为高危级别

**IOCs：**

8e89ae80ea50110244f2293f14615a7699b1c5d2a70415a676aa4588117ad9a7 – PPSX

**CC:**

hxxp://www[.]narrowbabwe[.]net/comsary/logo[.]jpg

hxxp://www[.]narrowbabwe[.]net:3345/exp[.]doc

hxxp://www[.]narrowbabwe[.]net/comsary/index[.]php

**<br>**

**参考文献**

[1]https://blog.fortinet.com/2017/06/04/an-inside-look-at-cve-2017-0199-hta-and-scriptlet-file-handler-vulnerability

[2]https://blog.fortinet.com/2016/12/16/malicious-macro-bypasses-uac-to-elevate-privilege-for-fareit-malware
