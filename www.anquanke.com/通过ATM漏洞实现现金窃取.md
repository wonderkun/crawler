> 原文链接: https://www.anquanke.com//post/id/248738 


# 通过ATM漏洞实现现金窃取


                                阅读量   
                                **38570**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者defcon，文章来源：media.defcon.org
                                <br>原文地址：[https://media.defcon.org/DEF%20CON%2028/DEF%20CON%20Safe%20Mode%20presentations/DEF%20CON%20Safe%20Mode%20-%20Trey%20Keown%20and%20Brenda%20So%20-%20Applied%20Cash%20Eviction%20through%20ATM%20Exploitation%20-%20WP.pdf](https://media.defcon.org/DEF%20CON%2028/DEF%20CON%20Safe%20Mode%20presentations/DEF%20CON%20Safe%20Mode%20-%20Trey%20Keown%20and%20Brenda%20So%20-%20Applied%20Cash%20Eviction%20through%20ATM%20Exploitation%20-%20WP.pdf)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01aadd7410fc542c0a.jpg)](https://p3.ssl.qhimg.com/t01aadd7410fc542c0a.jpg)



****摘要****

自动柜员机（Automated Teller Machines，ATM）是最古老的联网设备之一。尽管如此，高门槛的合法逆向工程工作导致大规模的ATM在部署过程中并未进行应有的机器测试，其妥协成本可以通过已提取的钞票数量计算。我们的研究从逆向工程师的角度研究了零售ATM，并详细介绍了我们发现的两个网络可访问（network-accessible）漏洞——远程管理系统（Remote Management System，RMS）中的缓冲区溢出漏洞，以及利用金融服务扩展（the eXtensions for Financial Services，XFS）接口的远程命令注入漏洞。这些漏洞分别可能导致任意代码执行，以及ATM Jackpotting(从ATM中非法获取现金)。



## 1.引言

银行拥有并运营的ATM，即金融ATM，往往有更明显的需要保证机器安全可靠的理由，但是分布在各个加油站和便利店的零售ATM通常更需要注重机器的性价比。Nautilus Hyosung HALO II[1]就是这样一种具有成本效益高的ATM。

我们最初对ATM感兴趣的原因是，作为一台可以取出钱的电脑，它是一个可用作信息安全挑战基础的极具吸引力的平台[2]。最初的工作涉及创建一个处理ATM事务的付款处理器——为此，我们开发了一台支持Triton Standard[3]（零售ATM的实际通用标准）的服务器。进一步的工作涉及ATM自身的逆向工程。此外还有固件更新的可用性、硬件修改后可访问的JTAG端口，以及应用完整固件更新前缺少签名验证的问题。



## 2.初步逆向工程

我们的目标ATM基于一种在多个Nautilus Hyosung的价格敏感的ATM上重用的框架——Windows CE 6.0 (官方于2018年4月10日宣布终止该产品的生命周期)，运行于800MHz ARM Cortex-A8。此上运行的库和应用的平台被称为MoniPlus CE。

[![](https://p5.ssl.qhimg.com/t0102234041e70a4bf4.png)](https://p5.ssl.qhimg.com/t0102234041e70a4bf4.png)

为了使ATM能够正常工作，它需要一个用于连接的付款处理器。如图1所示，对于零售ATM来说，付款处理器通常是一个处理与银行的上层交互的第三方供应商。这种交互通信可以通过TCP或拨号连接来实现。许多协议均可在该链接上使用，但我们发现最易于实施访问的是Triton Standard。该标准的草案副本[3]可在线获取。虽然当前的（标准）实现与该（标准）草案不完全匹配，但它仍然提供了如何实现一个可处理ATM交易的服务器的初步指南。

虽然不具备开箱即用的功能，但是主板上有一个未充填的端口，类似所谓的JTAG连接器。它的旁边有一个标记应有电阻器的未填充的焊盘。使用任意低电阻值充填并使用JTAGulator[4]映射之后，我们获取了一个功能齐全的调试接口。

ATM固件可以公开在线获取[5]。它包含启动（boot）加载（二进制）文件、内核（二进制）文件，以及一个包含所有软件应用程序和库的压缩包（zip）文件。



## 3.远程管理系统（RMS）

对于ATM来说，远程管理系统（RMS）是一个基于网络的供所有者和管理员管理ATM的网络的管理接口。在本文检测的ATM中，其RMS的功能包括转储ATM的版本和配置信息、搜集事务历史记录，以及远程更新ATM固件等等。

通常，ATM管理员需要使用名为MoniView[6]的客户端向ATM上运行的RMS服务器发送指令。为了对这些指令进行身份验证，ATM的序列号和RMS密码将会跟指令一同放入数据包并发出。但是，未经身份验证的攻击者可以通过发送精心构造的恶意数据包至远程RMS端点，使得缓冲区溢出或用于清理RMS控件库RMSCtrl.dll的结构损坏。这种破坏可能导致ATM的任意代码执行和持久化（内存修改），详细描述见后续小节。

### <a class="reference-link" name="A.%E5%8D%8F%E8%AE%AE%E8%AF%B4%E6%98%8E"></a>A.协议说明

客户端和ATM之间RMS通信的混淆是通过把消息明文和查找表中的值进行异或运算来实现的。RMS数据包的格式如表1所示。加密数据（Encoded data）包含RMS请求类型以及用于验证RMS数据包的ATM序列号和密码。

[![](https://p0.ssl.qhimg.com/t01c3816e3ffad6e8d9.png)](https://p0.ssl.qhimg.com/t01c3816e3ffad6e8d9.png)

### <a class="reference-link" name="B.RMS%E7%BC%93%E5%86%B2%E5%8C%BA%E6%BA%A2%E5%87%BA"></a>B.RMS缓冲区溢出

这个漏洞是由于CRmsCtrl::RMS_Proc_Tcp()调用的函数缓冲区溢出导致的。该溢出最终是由于调用memcpy却未进行适当的边界检查，从而导致RMS控件库RMSCtrl.dll的静态缓冲区溢出所导致的。ATM发送给RMS服务器的任意一个数据包都将启动列表1中的函数调用，进而执行以下操作：

[![](https://p2.ssl.qhimg.com/t01d35d48780f9b25e2.png)](https://p2.ssl.qhimg.com/t01d35d48780f9b25e2.png)

1）fnNET_RMSConnectAccept在默认端口5555上建立ATM和RMS客户端之间的TCP连接。

2）RMS_Recv调用fnNET_RMSRecvData，将接收到的RMS数据包中的数据复制到一个全局接收缓冲区。如果数据包是格式正确的，则继续解密被异或加密的数据。

3）RMS_VerifyMsg验证已解密数据中的ATM序列号和RMS密码。

4）如果消息通过了验证，函数将继续分析数据包并生成对RMS客户端的响应。

步骤2中函数fnNET_RMSRecvData没有检查其接收数据的边界或证书 ****（凭证？）****。此外，还会在数据包复制到recv_buffer内存所在位置之后进行数据包验证。因此，只要数据包符合表1中的结构，其数据就会被无差别地复制。任意大于0x2800字节的数据包都会造成缓冲区溢出。

### <a class="reference-link" name="C.%E4%BB%BB%E6%84%8F%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C"></a>C.任意代码执行

上述的溢出最终重写了一个在ATM关闭时被调用的函数。我们还发现RMSCtrl.dll的.data部分是可执行的，因此，我们可以写一个当DLL退出时执行的shellcode。因为溢出的缓冲区之后的内存区域永远不会被重写，并且对系统操作而言并不关键，所以shellcode可以一直保留在内存中直至设备电源关闭。当ATM主程序完全退出时，例如当技术人员在ATM上更新固件时，shellcode将会被执行。

### <a class="reference-link" name="D.%E6%8C%81%E4%B9%85%E5%86%85%E5%AD%98%E4%BF%AE%E6%94%B9"></a>D.持久内存修改

通过任意代码执行，我们修改了ATM的非易失性随机访问存储器（Nonvolatile Random-Access Memory，NVRAM）芯片的内存，实现了持久化（内存修改）。NVRAM用于存储ATM的网络和配置信息，例如启用或禁用SSL、指定付款处理器的IP地址、密码。可以通过两对API函数访问NVRAM——MemGetStr和MemGetInt从NVRAM获取（检索）信息，MENSetStr和MemSetInt更新NVRAM上的信息。攻击者可以通过上文提及的shellcode来更新ATM的配置以禁用SSL、重定向事务至恶意付款处理器、将密码修改为攻击者已知的值，以达成对自身有用的目标。由于该配置信息即便经过重启仍持续存在，因此对NVRAM的修改为攻击者提供了一种实现持续恶意修改的简单方法



## 4.中央金融服务扩展（XFS）

欧洲标准化委员会（the European Committee for Standardization，CEN）是ATM标准——金融服务扩展（eXtensions for Financial Services），即XFS的维护者。起初，Microsoft试图为金融设备创建一个运行在Windows上的通用平台<br>
XFS源自于最初Microsoft创建的标准，该标准旨在为金融设备创建一个在Windows上运行的通用平台，该标准至今仍在发挥这一作用。XFS在ATM行业中扮演着重要的角色，它既是ATM上运行的高级软件的目标平台，也充当着ATM上运行的低级软件的目标平台。XFS公开了一个同质化的接口，它可以用于处理ATM（和其他金融设备）中的不同组件，例如密码键盘、自动提款机、读卡器。

### <a class="reference-link" name="A.%E7%AE%80%E4%BB%8BXFS"></a>A.简介XFS

XFS定义了一组接口，旨在统一Microsoft Windows上金融应用与相关硬件的交互方式。如图2所示，这可以通过client/server架构实现。财务前端与XFS API进行交互，同时，处理硬件交互的服务提供商使用相应的XFS服务提供商接口（Service Provider Interface，SPI）进行交互。这些消息的转换和分发由XFS管理器处理。为了便于我们描述，我们将所有由供应商创建的XFS组件称为XFS中间件。与MoniPlus CE一起使用的XFS中间件称为Nextware[8]。

[![](https://p2.ssl.qhimg.com/t019ece75ab11c9a0fa.png)](https://p2.ssl.qhimg.com/t019ece75ab11c9a0fa.png)

多类设备被定义为该标准的一部分。表2列出了上述设备类别及其缩写。

[![](https://p1.ssl.qhimg.com/t016b8ef78ee64f3509.png)](https://p1.ssl.qhimg.com/t016b8ef78ee64f3509.png)

与各类设备相关的大量操作同样被定义为XFS标准的一部分。例如，标准定义负责处理信用卡和借记卡的设备为Identification Card units<br>
(IDCs)。IDC标准定义了可执行命令的常量，例如READ_TRACK、EJECT_CARD、CHIP_IO[10]。当主应用程序（在本例中，是WinAtm.exe）需要控制或查询设备时，将会调用这些命令。

由于XFS公开了一个不同于金融设备接口的同质化接口，因此，无论是对ATM行业而言，还是对恶意软件开发者而言，它都是一个具有吸引力的目标。许多与ATM相关的恶意软件，例如GreenDispenser[11]、RIPPER[12]，都通过XFS与读卡器、密码键盘、自动提款机进行交互。这些交互是在通过某种其他方式（通常是利用对设备的物理访问）投放到ATM上之后在payload中执行的。

### <a class="reference-link" name="B.Nextware%E2%80%94%E2%80%94XFS%E4%B8%AD%E9%97%B4%E4%BB%B6%E5%AE%9E%E7%8E%B0"></a>B.Nextware——XFS中间件实现

为了便于组成XFS中间件的不同组件之间的XFS消息传递，Nextware使用了基于TCP socket的进程间通信（Inter-Process Communication，IPC）机制。考虑到Windows CE[13]上缺少多个Windows IPC标准功能，这是一个相对合理的选择。但是，当这些socket配置错误时，会出现一个问题。创建socket的时候，如果监听的地址是0.0.0.0而非127.0.0.1，则本地服务器将不仅仅监听回环设备上的IPC消息，还将监听来自任何网络设备的消息。该错误配置反映在端口扫描中的情况如表3所示。

[![](https://p4.ssl.qhimg.com/t01d509a897e45f672b.png)](https://p4.ssl.qhimg.com/t01d509a897e45f672b.png)

尽管这些端口的用途在一开始尚不明晰，但对注册表的扫描提供了一个强有力的线索。多个XFS配置项存储在注册表的HKEY_USERS中。如列表2所示是摘录的自动提款机设备类的配置。

[![](https://p5.ssl.qhimg.com/t018d81a2705121bd8b.png)](https://p5.ssl.qhimg.com/t018d81a2705121bd8b.png)

一开始，我们企图从这些端口获取输出，但并未成功——任何位置信息都会导致端口拒绝后续输入的内容。进一步的分析显示，非预期格式的消息会导致IPC机制处于未知状态。目前，以上述方式与socket集成的复杂工作还没有相应的消息格式（说明）文档。在回环接口上捕获网络流量有助于破译成功发送XFS消息所需的消息格式，但这种数据包并不能直接捕捉到。

### <a class="reference-link" name="C.%E8%BD%AC%E5%82%A8%E7%BD%91%E7%BB%9C%E6%B5%81%E9%87%8F%E2%80%94%E2%80%94%E7%AC%A8%E5%8A%9E%E6%B3%95%EF%BC%9F"></a>C.转储网络流量——笨办法？

使用Windows CE 6.0工作是一件很复杂的事情。截至2019年，该版本首次发布是在13年前，然而它的最近一次主版本发布是在10年前。因此，该版本所需的任何工具都非常难以获得。由于该设备出厂时没有任何键盘或鼠标驱动，ATM的接口总体上让人非常沮丧，尽管这对安全来说是积极的。理论上在设备上捕获网络流量是可行的[14]，但由于（Windows CE 6.0）使用上的复杂性以及（ATM）设备设计并不支持图像传送，实际捕获流量障碍重重。因此，最直接的推进方法是确定IPC机制调用WInsock2的socket、recv、send函数的位置。由于地址空间分布随机化（Address Space Layout Randomization，ASLR）在该平台上是不起作用的，已知的上述函数的加载地址在设备重启之后仍有效。

追踪对socket函数的调用将会披露哪些底层服务有用于recv和send函数的给定socket handle（句柄），进而显示出每个服务正在发送和接收哪些消息。进一步的分析显示，每条消息都包含XFS标准格式的命令数据，且以header（标头）封装。如表4所示是部分已破译的格式。

[![](https://p4.ssl.qhimg.com/t01310132213adb29dd.png)](https://p4.ssl.qhimg.com/t01310132213adb29dd.png)

例如，设置自动提款机快速闪灯。使用SIU规范[16]作为指南，XFS命令字段将设置为WFS_CMD_SIU_SET_GUIDLIGHT，命令相关数据将填入相应结构，WFSSIUSETGUIDLIGHT。WFS_SIU_NOTESDISPENSER和WFS_SIU_QUICK_FLASH值将被用于表示自动提款机已被设置为快速闪灯。列表3复制了被引用的值和结构。

利用已知的数据包结构，以及通过JTAG获得的IPC socket发送的所有消息的转储，可以找到感兴趣的命令(例如，通过WFS_CMD_CDM_DISPENSE的现金提取)，修复数据包的超时和时间戳字段，并重放它来触发（现金提取）操作。

[![](https://p0.ssl.qhimg.com/t0164f7cd7f39a7d632.png)](https://p0.ssl.qhimg.com/t0164f7cd7f39a7d632.png)

### <a class="reference-link" name="D.XFS%E6%94%BB%E5%87%BB%E5%BD%B1%E5%93%8D"></a>D.XFS攻击影响

该攻击允许通过XFS消息socket执行命令注入，（XFS消息socket）对同一本地网络上的任何设备都可见。虽然这并不一定会导致任意代码执行，但它确实会导致其无验证的XFS API暴露在网络中，而其暴露面（XFS API）中包含立即让攻击者感兴趣的命令（如：分发现金）。



## 5.结论

尽管有坚固的物理外壳，但本文中提及的ATM很容易受到两个网络可访问的攻击：一个是预身份验证缓冲区溢出，允许使用用户交互执行任意代码（以及持久化（内存修改）），另一个是未经身份验证的XFS命令注入。虽然本文主要只针对一种常见ATM进行了研究，但在这里发现的问题很可能并不是这种ATM特有的。对这些设备进行合法渗透测试的高成本门槛仍然是这些设备最令人信服的防御之一。



## 6.致谢

我们要感谢 Red Balloon Security为我们提供的研究资源及用于逆向工程的ATM机。我们还要感谢Nautilus Hyosung积极主动配合漏洞披露、响应漏洞修复。



## 7.引文

[1] HALO II – Hyosung America. Hyosung America. [Online]. Available:<br>[https://hyosungamericas.com/atms/halo-ii/](https://hyosungamericas.com/atms/halo-ii/)

[2] Happy save banking corporation and laundry service. Red Balloon Security. [Online]. Available:<br>[http://happysavebankingcorporation.com/index.html](http://happysavebankingcorporation.com/index.html)

[3] “Triton terminal and communication protocol,” Triton. [Online].<br>
Available: [https://www.completeatmservices.com.au/assets/files/tritoncomms-msg%20format-pec](https://www.completeatmservices.com.au/assets/files/tritoncomms-msg%20format-pec) 5.22.pdf

[4] Joe Grand. Jtagulator — grand idea studio. Grand Idea Studio. [Online].<br>
Available: [http://www.grandideastudio.com/jtagulator/](http://www.grandideastudio.com/jtagulator/)

[5] Software updates — atm parts pro. ATM Parts Pro. [Online]. Available:<br>[https://www.atmpartspro.com/software](https://www.atmpartspro.com/software)

[6] Terminal management – hyosung america. Hyosung America.<br>
[Online]. Available: [https://hyosungamericas.com/softwares/terminalmanagement/](https://hyosungamericas.com/softwares/terminalmanagement/)

[7] Barnaby Jack, “IOActive Security Advisory – Authentication<br>
Bypass In Tranax Remote Management Software.” [Online]. Available: [https://ioactive.com/wp-content/uploads/2018/05/Tranax](https://ioactive.com/wp-content/uploads/2018/05/Tranax) Mgmt<br>
Software Authentication Bypass.pdf

[8] Cen/xfs. Wikipedia. [Online]. Available:<br>[https://en.wikipedia.org/wiki/CEN/XFS#XFS](https://en.wikipedia.org/wiki/CEN/XFS#XFS) middleware

[9] Extensions for financial services (xfs) interface specification release<br>
3.30 – part 1: Application programming interface (api) -service provider<br>
interface (spi) – programmer’s reference. European Committee for<br>
Standardization. [Online]. Available: ftp://ftp.cen.eu/CWA/CEN/WSXFS/CWA16926/CWA%2016926-1.pdf

[10] Extensions for financial services (xfs) interface specification<br>
release 3.30 – part 10: Sensors and indicators unit device class<br>
interface – programmer’s reference. European Committee for Standardization. [Online]. Available: ftp://ftp.cenorm.be/CWA/CEN/WSXFS/CWA16926/CWA%2016926-4.pdf

[11] Meet greendispenser: A new breed of atm malware.<br>
Proofpoint. [Online]. Available: [https://www.proofpoint.com/us/threatinsight/post/Meet-GreenDispenser](https://www.proofpoint.com/us/threatinsight/post/Meet-GreenDispenser)

[12] Ripper atm malware and the 12 million baht jackpot.<br>
FireEye. [Online]. Available: [https://www.fireeye.com/blog/threatresearch/2016/08/ripper](https://www.fireeye.com/blog/threatresearch/2016/08/ripper) atm malwarea.html

[13] A study on ipc options on wince and windows. Few of my technology ideas. [Online]. Available: [https://blogs.technet.microsoft.com/vanih/2006/05/01/a-study-on-ipc-options-on-wince-and-windows/](https://blogs.technet.microsoft.com/vanih/2006/05/01/a-study-on-ipc-options-on-wince-and-windows/)

[14] How to capture network traffic on windows embedded ce 6.0. Windows Developer 101. [Online].<br>
Available: [https://blogs.msdn.microsoft.com/dswl/2010/03/02/how-tocapture-network-traffic-on-windows-embedded-ce-6-0/](https://blogs.msdn.microsoft.com/dswl/2010/03/02/how-tocapture-network-traffic-on-windows-embedded-ce-6-0/)

[15] Winsock functions. Windows Dev Center. [Online]. Available:<br>[https://docs.microsoft.com/en-us/windows/win32/winsock/winsock-functions](https://docs.microsoft.com/en-us/windows/win32/winsock/winsock-functions)

[16] Extensions for financial services (xfs) interface specification<br>
release 3.30 – part 10: Sensors and indicators unit device class<br>
interface – programmer’s reference. European Committee for Standardization. [Online]. Available: ftp://ftp.cenorm.be/CWA/CEN/WSXFS/CWA16926/CWA%2016926-10.pdf
