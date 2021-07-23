> 原文链接: https://www.anquanke.com//post/id/86640 


# 【木马分析】TrickBot 和 Nitol 的联袂分析


                                阅读量   
                                **81328**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://www.trustwave.com/Resources/SpiderLabs-Blog/Tale-of-the-Two-Payloads-%E2%80%93-TrickBot-and-Nitol/](https://www.trustwave.com/Resources/SpiderLabs-Blog/Tale-of-the-Two-Payloads-%E2%80%93-TrickBot-and-Nitol/)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p5.ssl.qhimg.com/t018cf34a20af55cfb5.jpg)](https://p5.ssl.qhimg.com/t018cf34a20af55cfb5.jpg)

译者：[ngrepme](http://bobao.360.cn/member/contribute?uid=2941418194)

预估稿费：150RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**



几周前，Trustwave发现[Necurs botnet](https://www.trustwave.com/Resources/SpiderLabs-Blog/Necurs-%E2%80%93-the-Heavyweight-Malware-Spammer/)正在传播一种新型的垃圾邮件，其中包含Trickbot和Nitol的恶意payload。Trickbot是一种银行木马，去年年底首次出现在欧洲，英国，澳大利亚等国家。该木马将恶意代码注入Web浏览器进程，并在受害者访问目标银行网站时偷取敏感数据。 Nitol家族则以其分布式拒绝服务（DDOS）和后门功能臭名昭著。

 [![](https://p3.ssl.qhimg.com/t0172b7ff02f593f699.png)](https://p3.ssl.qhimg.com/t0172b7ff02f593f699.png)

图1. 2017年7月19日至20日，Necurs每小时传播的恶意垃圾邮件数量

 

**感染载体**

****

7月19日，trustwave发现了一个伪装成Apple Store UK收据的恶意邮件，其附件是一个包含DOCM对象的PDF。

[![](https://p5.ssl.qhimg.com/t0120fc6e4d5793e88d.png)](https://p5.ssl.qhimg.com/t0120fc6e4d5793e88d.png)

图2. 通过恶意PDF附件冒充Apple Store UK的邮件

 [![](https://p0.ssl.qhimg.com/t01b1935d3fb7d0ab44.png)](https://p0.ssl.qhimg.com/t01b1935d3fb7d0ab44.png)

图3. 包含的DOCM对象

PDF文件会释放.DOCM文件（一种包含宏的文档）至**％temp％**文件夹中，而且当用户打开文档后，其会提示用户启用宏。仔细分析宏代码可知，该脚本会从硬编码的域名自动下载一个加密的可执行二进制文件：

```
hxxp://cabbonentertainments.com83b7bf3
hxxp://dabar.name83b7bf3
hxxp://nasusystems.com83b7bf3
```

随后，该二进制文件被宏代码解密并执行。 

[![](https://p1.ssl.qhimg.com/t0188649997ba8a090a.png)](https://p1.ssl.qhimg.com/t0188649997ba8a090a.png)

图4. VBA宏解密程序

另一个被发现的恶意邮件则伪装成“采购订单”，其附件是被压缩过两次的二进制可执行文件。

[![](https://p0.ssl.qhimg.com/t0180df1e590e515201.png)](https://p0.ssl.qhimg.com/t0180df1e590e515201.png)

图5. 带有ZIP附件的虚假采购订单

[![](https://p0.ssl.qhimg.com/t018d4bb1349cc2c72f.png)](https://p0.ssl.qhimg.com/t018d4bb1349cc2c72f.png)

图6. 被两次压缩的二进制可执行文件

这两种垃圾邮件中都包含同样的payload：

[![](https://p2.ssl.qhimg.com/t011569c1272beb752c.png)](https://p2.ssl.qhimg.com/t011569c1272beb752c.png) 

<br>

**Payloads – Nitol and Trickbot Packages**



[![](https://p4.ssl.qhimg.com/t012bd9cdd09e6bf2cc.png)](https://p4.ssl.qhimg.com/t012bd9cdd09e6bf2cc.png)

图7. 攻击流程图

主要的可执行文件表现为一个加载器，会分别执行其资源节中的Nitol 和 Trickbot木马。而且加载器中还含有**anti-VM**机制，用于检查VirtualBox和VMware，以防止在沙箱设备中被执行分析。

**Payload 1: Trickbot**

Trickbot会在暂停模式（suspended mode）下创建一个自身的新进程，然后使用**VirtualAllocEx**和**WriteProcessMemory **API将其代码分配并写入新进程。

[![](https://p3.ssl.qhimg.com/t0141ba7b22d464dbf2.png)](https://p3.ssl.qhimg.com/t0141ba7b22d464dbf2.png)

图8. Trickbot在执行时产生了一个新的进程

所有内容都被加载到新进程的地址空间后，恶意软件就可以使用**ResumeThread**恢复挂起的进程。

其会在**%AppData%winapp**文件夹下释放出自身的副本，其中也包括其他的配置文件和插件：

[![](https://p1.ssl.qhimg.com/t01b88bdf255fa90641.png)](https://p1.ssl.qhimg.com/t01b88bdf255fa90641.png)

图9. 释放文件的树视图

[![](https://p3.ssl.qhimg.com/t01ba60418285e94643.png)](https://p3.ssl.qhimg.com/t01ba60418285e94643.png)

 其还创建了计划任务以增强持久性，每当用户登录或者是每过3分钟都会触发恶意软件的执行。

[![](https://p2.ssl.qhimg.com/t01b943dd416bf434b6.png)](https://p2.ssl.qhimg.com/t01b943dd416bf434b6.png)

图10. 持续性计划任务

该恶意软件通过使用一个查找算法来编码其字符串，想以此躲过静态分析，以下代码可对其进行解码：

```
def trickbot_decode(text):
	ts = "aZbwIiWO39SuApBFcPC/RGYomVxUNL01nr56le47Hv8DJsjQgEkKy+fT2dXtzhMq"
	alphabet = [n for n in ts]
	bit_str = ""
	text_str = ""

	for char in text:
		if char in alphabet:
			bin_char = bin(alphabet.index(char)).lstrip("0b")
			bin_char = bin_char.zfill(6)
			bit_str += bin_char

	brackets = [bit_str[x:x+8] for x in range(0,len(bit_str),8)]

	for bracket in brackets:
		text_str += chr(int(bracket,2))

	return text_str.encode("UTF-8")
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c0e46a3535be263e.png)

图11. 恶意软件中被混淆后的字符串

该恶意软件还会释放出一个名为"config.conf"的加密配置文件，其中包含了C2服务器的信息和其他模块的设置。

[![](https://p1.ssl.qhimg.com/t01d44e9f57b97aa20e.png)](https://p1.ssl.qhimg.com/t01d44e9f57b97aa20e.png)

图12. 解密后的C2信息

**TrickBot Modules**

TrickBot会产生多个Svchost.exe进程，其中注入了多个模块：

** 浏览器表单抓取模块**

**Outlook凭证抓住模块**

**系统信息抓取模块**

**InjectDLL32模块则会hook浏览器进程，并监控受害者的浏览器活动。**

[![](https://p0.ssl.qhimg.com/t017a8cd2f391ebf49a.png)](https://p0.ssl.qhimg.com/t017a8cd2f391ebf49a.png)

图13. 投毒svchost.exe hooking chrome.exe进程

Trickbot监控包括Chrome，IExplore，Firefox和Microsoft Edge在内的浏览器。它还hook了作为MS Edge父进程的Runtimebroker.exe进程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0122bdf5f5df2d498a.png)

图14. 目标浏览器进程

存储在%AppData%winappinjectDll32_configsdinj和%AppData%winappinjectDll32_configssinj中的加密配置文件，包含了一个目标网上银行URL的列表。

[![](https://p3.ssl.qhimg.com/t017a14dd7bb44d87e4.png)](https://p3.ssl.qhimg.com/t017a14dd7bb44d87e4.png)

图15. 存储在dinj文件中的目标网上银行

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010b3d8b3cf295db5a.png)

图16. 存储在sinj文件中的目标网上银行

[![](https://p4.ssl.qhimg.com/t01c4bdf1dd771aae17.png)](https://p4.ssl.qhimg.com/t01c4bdf1dd771aae17.png)

图17. 被窃取数据的IP地址

另一个模块被注入到一个单独的SVCHOST.EXE实例中，是用来负责抓取Outlook凭据。

下面显示的是恶意软件尝试查询的Outlook注册表项：

[![](https://p0.ssl.qhimg.com/t01cb48d033b889ddaf.png)](https://p0.ssl.qhimg.com/t01cb48d033b889ddaf.png)

图18. 查询的注册表项

从这些注册表项中，其会尝试收集Outlook帐户和凭据信息，如电子邮件，用户，服务器，端口和密码

[![](https://p5.ssl.qhimg.com/t018415204b33ddc949.png)](https://p5.ssl.qhimg.com/t018415204b33ddc949.png)

图19. 窃取Outlook的profile 和 credential

将窃取的Outlook信息传输的IP地址被加密存储在mailsearcher32_configs文件中

[![](https://p5.ssl.qhimg.com/t015fd0aab8517ef2c9.png)](https://p5.ssl.qhimg.com/t015fd0aab8517ef2c9.png)

图20. 解密后的外泄IP地址

最后，另一个名为“systeminfo”的模块负责收集受害者的系统信息，包括用户名，CPU类型，RAM，操作系统架构，安装的程序和服务。

[![](https://p2.ssl.qhimg.com/t013ab73c7db95fde3c.png)](https://p2.ssl.qhimg.com/t013ab73c7db95fde3c.png)

图21. 系统信息抓取的字符串

<br>

**Payload 2: Nitol DDOS bot**



 Nitol二进制文件存储在加载器的资源节部分。其使用UPX进行压缩，并在执行时创建一个名为“qazwsxedc”的互斥体，以避免运行多个自身实例。

[![](https://p2.ssl.qhimg.com/t01d7383effa55181de.png)](https://p2.ssl.qhimg.com/t01d7383effa55181de.png)

图22. Nitol的主体函数

一旦Nitol解密了C2服务器，其就会连接到服务器并等待进一步的指令。该后门主要有两个功能，一个是执行DDOS另一个是“下载并执行”任意文件。

[![](https://p0.ssl.qhimg.com/t011dacf9dc854a61b0.png)](https://p0.ssl.qhimg.com/t011dacf9dc854a61b0.png) 

[![](https://p3.ssl.qhimg.com/t0148ad64beee80ee21.png)](https://p3.ssl.qhimg.com/t0148ad64beee80ee21.png) 

图23. Nitol 后门的DDOS功能

[![](https://p4.ssl.qhimg.com/t0128edd740f9e5e7a7.png)](https://p4.ssl.qhimg.com/t0128edd740f9e5e7a7.png)

图24. Nitol 后门的下载并执行”任意文件功能

Nitol会对目标系统进行DOS攻击的类型如下：

SYN Flood

TCP Flood

UDP Flood

HTTP Flood

ICMP Flood

 

**总结**

****

Necurs botnet一直在主动使用资源传播Trickbot和Nitol恶意软件。该僵尸网络使用了两个模板。第一个垃圾邮件模板是附加主要可执行文件的经典电子邮件，而第二个模板使用了在PDF文件中嵌入DOCM的新生技术。无论用户收到哪个模板，都会导致执行相同的恶意软件加载程序。该加载器会在您的系统中执行Trickbot和Nito木马。Bot loader同时提供两个或多个恶意软件的现象似乎越来越普遍。通过避免为每个不同的恶意软件传播创建单独的模板，这基本上节省了botmaster的时间。 而且一些安全产品可能需要时间来反应并阻止两个不同的恶意软件，而不是原来的一个，这就允许botmasters“趁热打铁”“趁火打劫”了。
