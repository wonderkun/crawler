> 原文链接: https://www.anquanke.com//post/id/87188 


# 【木马分析】Silence：攻击金融机构的一款新型木马


                                阅读量   
                                **109871**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securelist.com
                                <br>原文地址：[https://securelist.com/the-silence/83009/](https://securelist.com/the-silence/83009/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01bf9f32b818815756.jpg)](https://p0.ssl.qhimg.com/t01bf9f32b818815756.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

2017年9月，我们发现了针对金融机构的新型攻击活动，受害者大多为俄罗斯银行，但我们发现马拉西亚及亚美尼亚的某些机构同样被攻击者攻陷。攻击者使用了一种已知的但仍行之有效的技术来牟取金钱：他们先是获得银行内部网络的长期访问权限，录制银行员工个人电脑的日常活动轨迹，学习目标银行的工作流程、所使用的软件，一切准备就绪后，就利用这些知识窃取尽可能多的金钱。

之前我们在Carbanak以及其他类似事件中也看过这种技术手法。攻击者凭借带有恶意附件的渔叉式钓鱼邮件成功感染目标。在Silence攻击事件中，有趣的是攻击者事先已经攻陷一些银行机构的基础设施，利用真实银行雇员的地址发送渔叉式钓鱼邮件，最大可能降低受害者对这些邮件的怀疑程度。

目前这类攻击活动仍在持续进行中。



**二、技术细节**

攻击第一步，犯罪分子通过Silence木马发送钓鱼邮件，他们通常会利用已感染的金融机构员工的真实地址，邮件主题是请求在目标银行中开设账户。这种主题看上去非常正常，利用这种社会工程学技巧，收件方很难怀疑邮件的真实目的：

[![](https://p3.ssl.qhimg.com/t0139a8bfebf582795f.png)](https://p3.ssl.qhimg.com/t0139a8bfebf582795f.png)

图1. 使用俄语编写的钓鱼邮件

**2.1 恶意.chm附件**

样本信息如下：

md5：dde658eb388512ee9f4f31f0f027a7df

类型：Windows帮助文件（.chm文件）

在这波攻击浪潮中，我们检测到了一个CHM（Microsoft Compiled HTML Help）文件样本。这种文件是微软专有的在线帮助文件，由许多HTML页面、索引以及其他导航工具组成。这些文件经过压缩后存为二进制格式，使用.CHM（compiled HTML）作为文件扩展名。这些文件具备很高的互动性，支持包括JavaScript在内的一些技术，利用这些技术，受害者在打开CHM文件后就会被重定向到外部URL地址。因此，攻击者会利用CHM文件实现恶意载荷的自动运行。当受害者打开附件后，内嵌的.htm文件（“start.htm”）就会执行。样本文件中包含JavaScript载荷，其目标是从一个硬编码的URL地址处下载并执行其他阶段的载荷。

图2. 内置的start.htm文件的部分内容

[![](https://p5.ssl.qhimg.com/t018f14ab63a5360d8b.png)](https://p5.ssl.qhimg.com/t018f14ab63a5360d8b.png)

这个脚本的功能是下载并执行一个经过混淆的.VBS脚本，后者会继续下载并执行最终的释放器（dropper）。

图3. 经过混淆的VBS脚本，具备二进制程序下载功能

[![](https://p0.ssl.qhimg.com/t019d4ce07964a2b51c.png)](https://p0.ssl.qhimg.com/t019d4ce07964a2b51c.png)

**2.2 释放器**

释放器样本信息如下：

md5：404D69C8B74D375522B9AFE90072A1F4

编译时间：2017年10月12日 02:53:12

文件类型：Win32可执行文件

释放器是一个win32可执行文件，其主要功能是与命令控制（C&amp;C）服务器通信，将被感染主机的ID发送给服务器，同时下载并执行恶意载荷。

释放器运行后会通过GET请求连接C&amp;C，发送已生成的受害者ID，下载恶意载荷，然后使用**CreateProcess**函数执行恶意载荷。

图4. 使用受害者ID连接C&amp;C服务器

[![](https://p5.ssl.qhimg.com/t01cc897d5113c8d6da.png)](https://p5.ssl.qhimg.com/t01cc897d5113c8d6da.png)

图5. C&amp;C连接过程

[![](https://p1.ssl.qhimg.com/t01c88f5ee4abb8f98a.png)](https://p1.ssl.qhimg.com/t01c88f5ee4abb8f98a.png)

**2.3 载荷**

攻击者所使用的载荷包含各种模块，这些模块可以在已感染的主机上执行各种任务，比如**屏幕录制**、**数据上传**等等。

我们识别出的所有载荷都以Windows服务形式运行。

**2.3.1 监控及控制模块**

模块信息：

md5：242b471bae5ef9b4de8019781e553b85

编译时间：2016年7月19日 15:35:17

模块类型：Windows服务可执行文件

该模块的主要任务是监控受害者的活动轨迹。为了完成这一任务，该模块会多次截取受害者的当前屏幕视图，这种伪视频流方式可以让攻击者监控所有受害者的活动轨迹。类似的技术也出现在Carbanak案例中，当时攻击者使用这种监控技术来了解受害者的日常活动。

该模块会注册为Windows服务，以服务方式运行，服务名为“Default monitor”。

图6. 恶意服务模块名

[![](https://p0.ssl.qhimg.com/t01962e31b45d565956.png)](https://p0.ssl.qhimg.com/t01962e31b45d565956.png)

初始启动完成后，该模块会创建一个Windows命名管道，管道名（\.pipe`{`73F7975A-A4A2-4AB6-9121-AECAE68AABBB`}`）已事先硬编码在模块中。不同恶意模块会使用该管道实现进程间通信。

图7. 创建命名管道

[![](https://p2.ssl.qhimg.com/t01ebc9611867651396.png)](https://p2.ssl.qhimg.com/t01ebc9611867651396.png)

恶意软件解密一段数据块，并将解密后的数据保存为二进制文件，文件名为硬编码的“mss.exe”字符串，保存路径为Windows临时目录，随后，恶意软件使用**CreateProcessAsUserA**函数运行该文件。释放出来的这个二进制文件是负责实时捕捉屏幕活动的恶意模块。

随后，该监控模块会等待新释放的模块运行，以便使用命名管道与其他模块共享收集到的数据。

**2.3.2 屏幕活动收集模块**

模块信息：

md5：242b471bae5ef9b4de8019781e553b85

编译时间：2016年7月19日 15:35:17

模块类型：Windows 32位可执行文件

这个模块同时用到了Windows图形设备接口（Graphics Device Interface，GDI）以及Windows API来记录受害者的屏幕活动轨迹，具体使用的是**CreateCompatibleBitmap**以及**GdipCreateBitmapFromHBITMAP**函数。随后，该模块连接到上一个模块创建的命名管道并将数据写入管道中。利用该技术，攻击者可以将收集到的所有位图结合起来，形成受害者活动轨迹的伪视频流。

图8. 将位图数据写入管道中

[![](https://p0.ssl.qhimg.com/t0109ebd46e26a95d6d.png)](https://p0.ssl.qhimg.com/t0109ebd46e26a95d6d.png)

**2.3.3 C&amp;C通信模块**

模块信息：

md5：6A246FA30BC8CD092DE3806AE3D7FC49

编译时间：2017年6月8日 03:28:44

模块类型：Windows服务可执行文件

与其他所有模块一样，C&amp;C通信模块同样以Windows服务形态来运行。该模块的主要功能是建立回连受害主机的访问通道，利用控制台命令执行服务器指令。服务初始化完毕后，恶意模块会解密运行所需的Windows API函数名，使用**LoadLibrary**加载这些函数，然后使用**GetProcAddress**函数解析这些API的具体地址。

图9. 解析WinAPI函数

[![](https://p4.ssl.qhimg.com/t01a4099bb8ee15a035.png)](https://p4.ssl.qhimg.com/t01a4099bb8ee15a035.png)

成功加载WinAPI函数后，恶意软件会尝试连接C&amp;C服务器，服务器地址为硬编码的IP地址（185.161.209[.]81）。



图10. C&amp;C IP地址

[![](https://p4.ssl.qhimg.com/t016c6bffa90e465485.png)](https://p4.ssl.qhimg.com/t016c6bffa90e465485.png)

恶意软件会往命令服务器发送带有ID信息的一个特殊请求，然后等待服务器响应，响应中包含一个字符串，恶意软件会根据该字符串执行具体的操作，这些操作包括：

“htrjyytrn”，音译过来为“reconnect”（俄语中对应“реконнект”）。

“htcnfhn”，音译过来为“restart”（俄语中对应“рестарт”）。

“ytnpflfybq”，音译过来为“нет заданий”，即“no tasks”（无任务）。

最后，恶意软件会收到指令，执行控制台命令。恶意软件以具体命令为参数创建一个新的cmd.exe进程来完成命令执行任务。

图11. 检查指令

[![](https://p1.ssl.qhimg.com/t01ccda0a4ade83bfec.png)](https://p1.ssl.qhimg.com/t01ccda0a4ade83bfec.png)

通过这种方式，攻击者只需要使用“sc create”控制台命令，就可以任意安装其他恶意模块。

**2.3.4 Winexecsvc工具**

工具信息：

md5：0B67E662D2FD348B5360ECAC6943D69C

编译时间：5月18日 03:58:26

类型：Windows 64位可执行文件

此外，在被感染的某些计算机上，我们还发现一款名为Winexesvc tool的工具。这款工具提供的功能与著名的“psexec”工具类似，最主要的区别在于，基于Linux的操作系统可以通过Winexesvc工具执行远程命令。当Linux程序“winexe”以某个Windows服务器为目标运行时，目标服务器上就会生成winexesvc.exe程序，并且该程序会以系统服务形态运行。



**三、总结**

攻击金融机构仍是网络犯罪分子大发横财的一种非常有效的途径。分析这次攻击事件，我们看到了一款新的木马，并且这款木马明显已在多个国家地区中使用过，这表明这个攻击组织的行动范围正在不断扩大。这款木马提供的监控功能与Carbanak组织具备的功能类似。

该组织在后续攻击阶段中会使用合法的管理工具在目标环境中大肆横行，这也使恶意行为的检测及溯源变得更为复杂。最近几年来，这类攻击规模不断增大，这种趋势反应了犯罪分子的攻击卓有成效，令人担忧。我们会继续监视这个新兴组织的犯罪活动。

目前渔叉式钓鱼攻击方法仍是实施针对性攻击的最常见方法。在已被攻陷的基础设施的基础上，结合使用.chm附件，钓鱼攻击的传播效果会更加有效，至少此次金融机构被攻击就是典型的案例。



**四、建议**

我们可以使用预防型高级检测功能来有效保护用户免受针对金融机构的恶意攻击，这种功能可以从更深层次检测用户系统上各种类型的可疑文件。卡巴斯基反针对性攻击解决方案（KATA）可以匹配来自不同级别基础设施的事件，识别并关联其中的异常事件，最终汇聚形成综合安全事件，与此同时也会利用沙箱化技术在安全环境中研究相关部件。与大多数卡巴斯基产品一样，KATA由人工智能（HuMachine Intelligence）提供技术支持，这项技术离不开机器学习、专业知识的实时分析以及我们对威胁情报大数据的深入理解。

想要阻止攻击者发现和利用安全漏洞，最佳方法是彻底消除漏洞，其中也包括因为不当系统配置或者专用应用程序错误导致的安全漏洞。为了实现这个目的，我们可以使用卡巴斯基渗透测试及应用安全评估服务这个方便且高效的解决方案，该方案不仅能够提供已发现漏洞的相关数据，也能给出如何解决这些漏洞的具体方法，进一步加强企业自身安全。



**五、IOC**

卡巴斯基实验室产品将Silence木马标记为如下类别：

**Backdoor.Win32.Agent.dpke**

**Backdoor.Win32.Agent.dpiz**

**Trojan.Win32.Agentb.bwnk**

**Trojan.Win32.Agentb.bwni**

**Trojan-Downloader.JS.Agent.ocr**

**HEUR:Trojan.Win32.Generic**

完整的IOC以及YARA规则会通过私人报告订阅服务提供。

样本MD5值如下：

Dde658eb388512ee9f4f31f0f027a7df

404d69c8b74d375522b9afe90072a1f4

15e1f3ce379c620df129b572e76e273f

D2c7589d9f9ec7a01c10e79362dd400c

1b17531e00cfc7851d9d1400b9db7323

242b471bae5ef9b4de8019781e553b85

324D52A4175722A7850D8D44B559F98D

6a246fa30bc8cd092de3806ae3d7fc49

B43f65492f2f374c86998bd8ed39bfdd

cfffc5a0e5bdc87ab11b75ec8a6715a4
