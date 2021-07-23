> 原文链接: https://www.anquanke.com//post/id/147013 


# GhostSecret事件分析：在全球范围内发动攻击窃取数据


                                阅读量   
                                **111437**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://securingtomorrow.mcafee.com/
                                <br>原文地址：[https://securingtomorrow.mcafee.com/mcafee-labs/analyzing-operation-ghostsecret-attack-seeks-to-steal-data-worldwide/](https://securingtomorrow.mcafee.com/mcafee-labs/analyzing-operation-ghostsecret-attack-seeks-to-steal-data-worldwide/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01d6fbcef5e4d2c8c3.jpg)](https://p0.ssl.qhimg.com/t01d6fbcef5e4d2c8c3.jpg)

## 一、概述

近期，McAfee高级威胁研究分析师发现了一起针对全球范围的数据窃取恶意事件，该恶意事件以许多行业为目标，其中包括关键基础设施、娱乐行业、金融业、医疗保健领域和电信业。该恶意事件名为GhostSecret，利用了多种植入物和工具，同时还利用了与具有国家背景的恶意组织Hidden Cobra相关的恶意软件变种。目前，该事件仍在基础设施领域保持活跃。在本文中，我们深入研究这一恶意事件。有关此威胁的简要概述，请参阅《Global Malware Campaign Pilfers Data from Critical Infrastructure, Entertainment, Finance, Health Care, and Other Industries》（ [https://securingtomorrow.mcafee.com/mcafee-labs/global-malware-campaign-pilfers-data-from-critical-infrastructure-entertainment-finance-health-care-and-other-industries](https://securingtomorrow.mcafee.com/mcafee-labs/global-malware-campaign-pilfers-data-from-critical-infrastructure-entertainment-finance-health-care-and-other-industries) ）<br>
通过我们对此次恶意事件的分析，我们发现该组织使用了多种恶意软件，其中包括具有类似于Bankshot（针对土耳其财政部门的远程访问恶意软件）功能的植入物。从3月18日至26日，我们已经发现该恶意软件在世界多个地区出现。新变种的一部分类似于2014年在索尼影业攻击中所使用的Destover恶意软件。<br>
此外，高级威胁研究团队发现了Proxysvc，这似乎是一种无文件的植入方式。我们还发现了其他的C&amp;C服务器，这些服务器仍然处于活动状态，并且与这些植入内容相关联。根据我们对目前已有的公开信息的分析，加上对于恶意软件样本的分析，我们发现Proxysvc似乎与2017年的Destover变种共同使用，并且自2017年年中至今以来一直未被发现。<br>
GhostSecret背后的攻击者在早期使用了与其他攻击相似的方式，包括FakeTLS在植入物中使用SSL证书，该证书被用于索尼影业攻击中所使用的名为Escad的Destover后门变种之中。根据我们的技术分析，我们具有足够证据表明该恶意事件由Hidden Cobra团体进行。高级威胁研究团队在2018年3月发现了与此次恶意事件相关的动作，其威胁的目标是土耳其银行。这些动作似乎是GhostSecret恶意事件的第一阶段。



## 二、深入分析

McAfee高级威胁研究团队首次发现了数据收集植入物，该植入物于2018年2月中旬出现，似乎是Hidden Cobra之前开发的植入物的变化版本，其功能类似于Bankshot，其部分代码与Hidden Cobra的植入物相似。然而，该变种并不是基于Bankshot。通过我们对可移植可执行文件的Rich-header数据分析表明，这两种植入物都是在不同的开发环境中编译的。（PE Rich Header是Windows可执行文件中一个未公开的部分，它提供了用于识别Microsoft编译器和链接器的唯一信息，有助于识别恶意软件变种之间的相似性。）根据代码内容和PE Rich Header表明，Bankshot、Proxysvc和Destover的植入物是不同的系列，但同时也包含与Hidden Cobra当前工具相同的代码和功能。<br>
2018年发现的Bankshot植入物的PE Rich Header数据：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-1.png)2018年2月新发现植入物的PE Rich Header数据：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-2.png)Proxysvc.dll的PE Rich Header数据：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-3.png)我们将2018年2月新样本的PE Rich Header数据与2014年索尼影业攻击发生前不久发现的Backdoor.Escad（Destover）变种进行比较，发现二者的签名是相同的。Destover变种与2015年的变种具有83%的相似度，并且包含与Backdoor.Escad变种相同的Rich PE Header签名。由此可以判断，新植入物可能是Destover组件的一个衍生版本。此外我们还确定，植入物并不是直接复制了Destover的样本，而是由Hidden Cobra根据早期版本中的功能创建了一个新的混合变种。<br>
2014年Backdoor.Escad（Hash：8a7621dba2e88e32c02fe0889d2796a0c7cb5144）：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-4.png)2015年Destover变种（Hash：7fe373376e0357624a1d21cd803ce62aa86738b6）：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-5.png)2018年2月发现的植入物（fe887fcab66d7d7f79f05e0266c0649f0114ba7c）是在编译后两天（2月14日）从美国的未知提交者处获得的。该文件使用韩文语言，C&amp;C服务器IP为203[.]131.222[.]83。除了C&amp;C服务器地址不同外，该植入物与2017年的未知样本（8f2918c721511536d8c72144eabaf685ddc21a35）几乎相同。2017年的未知样本使用14[.]140.116[.]172地址作为C&amp;C服务器。这两个植入物都使用了FakeTLS和PolarSSL，我们在此前Hidden Cobra的植入物中也发现了这一特性。自索尼影业事件发生以来，PolarSSL库就经常出现在植入物中，并且专门用于后门恶意软件Backdoor.Destover的植入。该植入物包含了一个通过443端口发送流量的自定义C&amp;C服务器协议。它并不会以标准的SSL格式数据包进行传输，而是通过自定义的格式以SSL方式进行传输，因此称为FakeSSL。与Backdoor.Escad进行比较，其C&amp;C服务器的流量几乎相同。<br>
Backdoor.Destover中的TLS流量，来自于2018年发现的Destover变种：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-6.png)Backdoor.Escad中的TLS流量：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-7.png)通过对14[.]140.116[.]172的进一步研究，我们获得了整个恶意软件的额外隐藏组件。在Proxysvc.dll中，包含所有位于印度的IP地址列表，是以硬编码的方式存储的，包括上述提及的IP地址。尽管名称不同，但该组件并不是SSL代理，而是一个数据收集和植入物安装组件，它在443端口的入站方向监听C&amp;C服务器的连接请求。<br>
Proxysvc样本是在3月22日于美国捕获，3月19日曾经从韩国发现过该组件的可执行投放程序。根据McAfee的分析显示，3月16日至21日之间Proxysvc组件在野外十分活跃。我们的研究表明，这一监听组件主要出现在高等教育机构。因此，我们怀疑这个组件与核心C&amp;C服务器的基础架构相关。我们判断，攻击者是针对这些目标有意选择运行Proxysvc的，因为他们需要知道有哪些系统受到感染，才能实现对目标的连接。同时，数据还表明，该恶意软件在被发现之前已经运行了一年多。高级威胁研究团队发现这个组件已经在11个国家的系统上运行。鉴于Proxysvc作为SSL监听器的一部分，其功能有限，因此这些网络还允许攻击者收集数据，并安装更复杂的植入物或其他恶意软件。SSL监听器支持连接多个C&amp;C服务器，这些连接目标不一定来自硬编码的IP地址列表。在结束与硬编码地址建立的连接之后，该样本可以仅接受入站连接，从而可以保证灵活地更换C&amp;C服务器。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-8.png)在2018年3月14日至18日期间，该样本在17个国家的组织中被发现，其中涉及电信、健康、金融、核心基础设施和娱乐等领域。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-9.png)



## 三、C&amp;C服务器

通过我们对C&amp;C服务器的进一步调查，我们发现了与2018年2月新变种所使用的C&amp;C服务器203[.]131.222[.]83相关的SSL证书d0cb9b2d4809575e1bc1f4657e0eb56f307c7a76。该服务器位于泰国曼谷的Thammasat大学，与索尼影业事件中使用的C&amp;C服务器相同。自索尼影业攻击事件以来，该SSL证书已经被Hidden Cobra长期使用。通过对这一证书的分析，我们发现其他的C&amp;C服务器也使用相同的PolarSSL证书。根据我们的进一步分析，发现了几个活跃的IP地址，其中还有两个IP与该C&amp;C服务器处于同一网段内。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-10.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-11.png)



## 四、植入物溯源

我们确定，此次分析的Destover变种源于2015年开发的代码。该代码在2017年和2018年出现的变种中再次被使用，几乎具有相同的功能，同时对命令部分进行了部分修改，同时根据Rich PE Header信息判断使用了相同的开发环境开发而成。<br>
新发现的两种植入物（fe887fcab66d7d7f79f05e0266c0649f0114ba7c和8f2918c721511536d8c72144eabaf685ddc21a35）都基于2015年的代码。在与2015年8月8日编译的植入物进行比较时，我们发现它与2018年的植入物有83%的相似。其中关键的异同点如下。

### <a class="reference-link" name="4.1%20%E7%9B%B8%E5%90%8C%E7%82%B9"></a>4.1 相同点

1、二者都使用GetProcAddress动态构建其API导入，其中包括用于为任何活动远程会话收集用户名和域名的wtsapi32.dll；<br>
2、二者都包含一系列功能，根据C&amp;C服务器发出的命令ID来执行，其相同的功能如下：<br>
（1）列出目录中的文件；<br>
（2）创建任意进程；<br>
（3）将从C&amp;C服务器收到的数据写入磁盘上的文件；<br>
（4）收集所有驱动器的信息；<br>
（5）针对所有进程收集进程时间；<br>
（6）将特定文件的内容发送到C&amp;C服务器；<br>
（7）擦除和删除磁盘上的文件；<br>
（8）设置植入物的当前工作目录；<br>
（9）将磁盘空间信息发送到C&amp;C服务器；<br>
3、二者都使用批处理文件机制从系统中删除其二进制文件；<br>
4、二者都在系统上运行命令，将输出记录到临时文件，并将文件的内容发送到其C&amp;C服务器。

### <a class="reference-link" name="4.2%20%E4%B8%8D%E5%90%8C%E7%82%B9"></a>4.2 不同点

在2018年版本中，不包含2015年原始版本的以下功能：<br>
（1）以一个特定用户身份创建进程；<br>
（2）终止一个特定进程；<br>
（3）删除特定文件；<br>
（4）为特定文件设置文件时间；<br>
（5）获取当前系统时间并将其发送到C&amp;C服务器；<br>
（6）读取磁盘上文件的内容（如果指定的文件路径是目录，则列出目录中的文件）；<br>
（7）在文件上设置属性。<br>
而在2015年的原始版本中，不包含必须连接的IP地址的硬编码值。相反，其中包含被connect() API用于指定端口（443）和C&amp;C服务器IP地址（193.248.247.59、196.4.67.45）所需的硬编码sockaddr_in数据结构，其位于二进制文件末尾前的0x270字节处。这两个C&amp;C服务器都使用PolarSSL证书d0cb9b2d4809575e1bc1f4657e0eb56f307c7a76。



## 五、对Proxysvc的分析

在最初，我们认为SSL监听器Proxysvc是一个代理设置工具，用于执行中间人流量的拦截。但通过对样本更深入的分析，我们发现这是基于SSL的HTTP从C&amp;C服务器接收命令的另一个植入物。<br>
Proxysvc看似是一个下载器，其主要功能是在不泄露攻击者的控制IP的情况下，向终端发送额外的Payload。这种植入物具有有限的侦查能力和持续的Payload安装能力。该植入物是一个服务DLL，也可以作为独立进程运行。<br>
Proxysvc的ServiceMain()子函数：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-12.png)植入物无法连接到C&amp;C服务器IP地址或URL，相反，它只接收来自C&amp;C服务器的命令。植入物将与端口进行绑定，并持续监听443端口，从而可以接收到任何传入的连接。<br>
Proxysvc绑定到指定端口：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-14.png)Proxysvc开始接收传入的请求，并进行处理：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-15.png)此外，Proxysvc在接收到来自潜在C&amp;C服务器的连接时，还会进行一项有趣的检查。它会检查该IP是否与一个黑名单IP地址列表匹配，以确保传入的连接不是来自于以下地址。如果IP地址匹配，植入物将进行零响应（响应ASCII码的“0”）并关闭连接。<br>
黑名单IP地址如下：<br>
121.240.155.74<br>
121.240.155.76<br>
121.240.155.77<br>
121.240.155.78<br>
223.30.98.169<br>
223.30.98.170<br>
14.140.116.172



## 六、对SSL监听器的分析

植入物从C&amp;C服务器接收基于HTTP协议的命令，并会从HTTP头解析HTTP Content-Type和Content-Length。如果HTTP Content-Type值为8U7y3Ju387mVp49A，则会执行由C&amp;C服务器指定的命令：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-16.png)该植入物具有如下功能：<br>
1、将从C&amp;C服务器接收到的可执行文件写入到临时文件并执行。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-17.png)2、收集系统信息并将其发送到C&amp;C服务器。<br>
从终端收集的系统信息包括：<br>
（1）终端的MAC地址；<br>
（2）计算机名称；<br>
（3）产品名称（来源于HKLMSoftwareMicrosoftWindows NTCurrentVersion ProductName）；<br>
这些信息被组合成一个格式为“MAC地址|计算机名称|产品名称”的字符串，并发送到C&amp;C服务器。<br>
3、使用当前的系统时间戳，将来自C&amp;C服务器的HTTP请求记录到植入物安装目录下的临时文件prx中。



## 七、对主要植入物的分析

2018年2月发现的植入物样本具有多种功能，包括信息泄露和被感染系统的任意命令执行。考虑到植入物可以从C&amp;C服务器收到各种类型的指令，因此该植入物也具有非常强大的数据侦查功能框架，并且可以被有效利用。例如，该植入物可以擦除或删除文件、执行另外的植入物、从文件中读取数据。<br>
通过动态加载API来执行恶意事件，主要植入物开始执行。用于加载API的库包括：<br>
Kernel32.dll<br>
Apvapi32.dll<br>
Oleaut32.dll<br>
Iphlpapi.dll<br>
Ws2_32.dll<br>
Wtsapi32.dll<br>
Userenv.dll<br>
Ntdll.dll<br>
主要植入物动态加载API：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-18.png)在初始化过程中，植入物会收集系统基本信息，并使用443端口上的SSL将其发送到硬编码写入的C&amp;C服务器203[.]131.222[.]83：<br>
1、系统区域中设置的国家、地区名称；<br>
2、操作系统版本；<br>
3、处理器描述，来源于<br>
HKLMHARDWAREDESCRIPTIONSystemCentralProcessor ProcessorNameString位置；<br>
4、计算机名称和网络适配器信息；<br>
5、本地磁盘C:到Z:的磁盘空间信息，包括总物理空间大小、总可用空间大小，以字节为单位；<br>
6、当前内存状态，包括总物理内存大小、总可用内存大小，以字节为单位；<br>
7、基于当前远程会话的域名和用户名。<br>
使用Win32 WTS API提取域名和用户名：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-19.png)



## 八、数据侦查过程

植入物通过SSL接收编码后的数据，该数据会被解码，从而确定有效的命令ID。有效的命令ID位于0和0x1D之间。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-20.png)根据不同的命令ID，植入物可以执行以下功能：<br>
1、收集系统信息并将其发送到C&amp;C服务器（与前文中介绍的基本数据收集功能相同）。<br>
2、获取系统中所有驱动器的卷信息（从A：到Z:）并发送到C&amp;C服务器。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-21.png)3、列出目录中包含的文件，该目录路径由C&amp;C服务器指定。<br>
4、读取文件的内容，并将其发送到C&amp;C服务器。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-22.png)5、将C&amp;C服务器发送的数据写入指定的文件路径。<br>
打开文件的句柄，以执行写入，但不具有共享权限：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-24.png)将从C&amp;C服务器接收到的数据写入到文件：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-24.png)6、根据C&amp;C服务器指定的文件路径，创建新进程：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-25.png)7、擦除和删除C&amp;C服务器指定的文件。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-26.png)8、使用cmd.exe在系统上执行二进制文件，并将结果记录到临时文件中，然后读取并将记录结果发送到C&amp;C服务器。<br>
命令行：cmd.exe /c “&lt;file_path&gt; &gt; %temp%PM*.tmp 2&gt;&amp;1”<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-27.png)9、获取所有当前运行进程的信息。<br>
获取系统中所有进程的进程时间：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-28.png)从与正在运行进程相关联的账户获取用户名和域名：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-29.png)10、使用批处理文件从磁盘删除其自身。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-30.png)11、将从C&amp;C服务器收到的编码后数据，作为注册表值，存储在<br>
HKLMSoftwareMicrosoftWindowsCurrentVersionTowConfigs的Description中。<br>
12、设置并获取植入物的当前工作目录。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-31.png)在植入物中的命令处理程序索引表如下所示：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securingtomorrow.mcafee.com/wp-content/uploads/2018/04/20180412-GhostSecret-32.png)



## 九、总结

根据McAfee高级威胁研究团队的分析，我们认定该组件源于Hidden Cobra团体，同时继续针对全球各地的组织发动攻击。自2015年以来，这些用于数据收集的植入物不断发生变化，这也侧面证明了该攻击者团队具有较强的开发能力。在我们的调查中，发现了一个未知的恶意软件工具，与近期源于印度服务器发动的一些攻击相关，这些位于印度的服务器使用了先进的植入物，建立一个隐蔽的网络，用于收集数据和发起进一步的攻击。<br>
我们将持续进行相关调查和研究，并根据进展实时发布更新。<br>
打击网络犯罪需要全球范围内国家组织和私营组织的一同努力，McAfee也正在与泰国政府当局合作，取缔GhostSecret控制的C&amp;C服务器，同时保留相应系统中的证据以供执法机关进行进一步分析。



## 十、IoC

### <a class="reference-link" name="10.1%20MITRE%20ATT&amp;CK"></a>10.1 MITRE ATT&amp;CK

通过C&amp;C服务器通道进行渗透：使用自定义协议在C&amp;C服务器通道上泄漏数据。<br>
常用端口：攻击者使用公共端口（443端口）进行C&amp;C服务器通信。<br>
服务执行：将植入物注册为被感染主机上的服务。<br>
自动收集：植入物自动收集有关被感染用户的数据，并将其发送到C&amp;C服务器。<br>
来自本地系统的数据：搜寻本地系统，并收集数据。<br>
发现进程：植入物可以列出在系统上运行的进程。<br>
发现系统时间：在部分数据侦察活动中采用的方法，将系统时间发送到C&amp;C服务器。<br>
删除文件：恶意软件可以删除攻击者指定的文件。

### <a class="reference-link" name="10.2%20IP%E5%9C%B0%E5%9D%80"></a>10.2 IP地址

203.131.222.83<br>
14.140.116.172<br>
203.131.222.109

### <a class="reference-link" name="10.3%20Hash"></a>10.3 Hash

fe887fcab66d7d7f79f05e0266c0649f0114ba7c<br>
8f2918c721511536d8c72144eabaf685ddc21a35<br>
33ffbc8d6850794fa3b7bccb7b1aa1289e6eaa45
