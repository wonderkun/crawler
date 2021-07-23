> 原文链接: https://www.anquanke.com//post/id/149698 


# MOSEC议题解读 | PWN2OWN shannon基带破解之旅


                                阅读量   
                                **159852**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01478edd3f0acbb5b3.jpg)](https://p5.ssl.qhimg.com/t01478edd3f0acbb5b3.jpg)



## 一、关于基带漏洞

基带漏洞最大的威胁是可以通过OTA(空中接口)利用，即通过发射加载漏洞利用代码的无线电波，从空中接口利用漏洞，在受害者无任何感知的情况下，远距离对受害者进行攻击。

[![](https://p3.ssl.qhimg.com/t0118f005a43534a33b.png)](https://p3.ssl.qhimg.com/t0118f005a43534a33b.png)

如上图，自从第一个移动通信系统面世至今，移动通信系统经过近四十年发展，到现在通信标准已经迭代了五代，在一次次迭代过程中，安全问题尤其是来自于无线电波层面的空中接口威胁，已经引起了通信和安全专家们的极度关注。每一代移动通信标准制定时，专家们对协议都进行了非常严密的论证和验证工作。

针对于空中接口，从2G系统开始，引入加密，3G系统开始引入强制完整性保护，4G系统除了RRC完整性保护和加密之外，还引入了NAS层完整性保护和加密以及AS的加密，5G则额外引入了IMSI加密。

自从3G引入强制完整性保护之后，移动通信系统协议层面很少发现空口高危漏洞，纵观国际黑客会议，能从空口利用的影响4G用户的协议层面高危漏洞也就360独角兽安全团队发现的‘Ghost Telephonist’漏洞[1]，LTE 重定向漏洞[3]，以及IMSI catcher。

因此在协议层面发现高危漏洞的可能性已经降低，然而协议本身由代码实现，这些代码又是由人工编写，难免存在疏漏的可能，因此在空口层面的高危漏洞主要存在于基带实现过程中。对于移动终端而言，每个人都可以获取到基带的二进制固件代码进行分析，近年来也成为安全研究的热点。



## 二、手机处理器架构

手机终端发展至今，已经由早期的功能机的单处理器架构（基带协议栈与应用程序共用一个处理器），发展为现在智能手机的modem+ap结构，某些高级终端SOC甚至包含十几个处理器，分别作为modem，音频，视频，传感器等用途。而对于Amat破解的shannon处理器，则可以简单的看成是CP(modem) + AP 结构。

[![](https://p1.ssl.qhimg.com/t01995c71a2db37778d.png)](https://p1.ssl.qhimg.com/t01995c71a2db37778d.png)

如图所示，在shannon处理器中，CP部分由一个Cortex-R7 ARM 核构成，AP部分则可能是Cortex-A53, Cortex-A72等，CP 和 AP 共用RAM。

对于安全研究员而言，CP使用ARM 处理器是一个好消息，意味着可以使用IDA Pro强大的F5功能，不至于像逆向高通modem一样，要和头痛的Hexagon DSP 指令集打交道。



## 三、攻击路径

[![](https://p3.ssl.qhimg.com/t01f7a79309d0cc5e38.png)](https://p3.ssl.qhimg.com/t01f7a79309d0cc5e38.png)

根据PWN2OWN的规则，攻击路径需要满足从空口攻破CP， 再以CP为跳板，攻破AP。



## 四、固件提取

虽然Shannon基带固件在可以在三星手机firmware中找到，但升级包中的固件是加密的，Amat Cama挖掘shannon基带漏洞的目的主要是满足pwn2own的要求，即找到能从OTA远程利用的基带漏洞，因此，在这里，Amat没有去挑战如何解密基带固件，而是想办法直奔主题，通过ramdump将已经解密的基带固件从内存中直接dump出来，具体流程如下。

在拨号盘上输入*#9900#调出工程模式的SYSDUMP菜单

[![](https://p2.ssl.qhimg.com/t01b3a61e89bbfd9901.png)](https://p2.ssl.qhimg.com/t01b3a61e89bbfd9901.png)

选中  ‘DEBUG LEVEL ENABLED’按钮，将debug level设定为’HIGH’,之后手机将重新启动。

手机启动后，在拨号盘键入‘*#9900#’重新调出SYSDUM菜单，将’ CP RAM LOGGING‘设定为ON，手机将会再次重启。

[![](https://p4.ssl.qhimg.com/t018b902eca36911612.png)](https://p4.ssl.qhimg.com/t018b902eca36911612.png)

手机启动后，调出SYSDUMP菜单，下滑找到‘RUN FORCED CP CRASH DUMP‘，并点击，手机将再次重启，并进入RAM加载模式。

[![](https://p4.ssl.qhimg.com/t01d6e9b85c5b78b70d.png)](https://p4.ssl.qhimg.com/t01d6e9b85c5b78b70d.png)

同时按住POWER键和VOLUME DOWN键超过10秒将手机关闭并再次开机，开始dump过程。

[![](https://p4.ssl.qhimg.com/t01f7bd943dd3d1c042.png)](https://p4.ssl.qhimg.com/t01f7bd943dd3d1c042.png)

重新打开SYSDUMP菜单，并点击‘COPY TO SDCARD(INCLUDE CP RAMDUMP)‘按钮，将dump文件拷贝到SDCARD。这时在/sdcard/log下将有一个名为‘pcrash_dump_YYYYMMDD_HHSS.log’的文件。



## 五、固件分析

Dump文件是并不包含elf文件格式的定位加载信息，因此在利用IDA 加载dump文件逆向分析之前，还需要分析dump文件的内存映射信息。

Shannon modem上电及ramdump由CP BOOT DAEMON(/sbin/cbd) 负责，而modem加密固件的开始部分还有一个modem的boot loader。

分析cbd及modem的boot代码可以得知dump文件偏移与虚拟地址的对应关系，下图的表格是另一篇破解shannon基带的议题分析的映射关系[2]，由于基带版本号的关系，可能与pwn2own  Amat分析的偏移不一样，笔者手里也没有相应型号的手机，此处没有验证。

[![](https://p1.ssl.qhimg.com/t013191e723c67baf92.png)](https://p1.ssl.qhimg.com/t013191e723c67baf92.png)

有这个映射信息，可以编写一个IDA 加载器来加载这个ramdump文件。



## 六、分析TASKs

Samsung的shannon 基带处理器上运行有一个实时操作系统(RTOS), 首先我们需要在dump文件中定位到在RTOS上运行的这些TASKs。

我们知道CPU的入口是中断向量表，中断向量表位于固件的开始处，中断向量表里有一系列的终端向量，其中也包含‘RESET HANDLER’，这是处理器复位后开始执行的第一条指令所在，对RTOS固件的逆向分析通常会从RESET HANDLER入手。

在其中定位到一个链表，该链表中包含有所有各个task的信息，其中包括task名称，以及dump相应task的堆栈布局。通过一个脚本可以将这些task 信息提取出来。

[![](https://p1.ssl.qhimg.com/t01359a695aef3c683d.png)](https://p1.ssl.qhimg.com/t01359a695aef3c683d.png)

其中一些task的名称很友好，可以从中猜出该task的功能，而另外一些task 命名则很有误导性。下面是Amat分析的一些Task名称。

MM (Mobility Management (移动性管理)?)

LLC(Logic Link Control(逻辑链路控制) ？)

SMS_SAP

GRR

SS

SAEL3

SNDCP

CC (Call Control ?)

SM (Session Management ?)

…

不同的task对应了协议栈中不同的分层

[![](https://p1.ssl.qhimg.com/t01dcbe1e76833477d5.png)](https://p1.ssl.qhimg.com/t01dcbe1e76833477d5.png)

在实时操作系统中，Task之间的通信机制很多，在shannon处理器的RTOS中使用的是信箱机制(Mail box)，具体机制可以去翻翻《操作系统原理》。

如下图所示，每个Task的流程大致如此，检查Mailbox中是否有自己的消息，处理消息，必要时还需要向其他Task发送消息，很多个Task协同完成整个基带协议栈的功能。

[![](https://p1.ssl.qhimg.com/t0145bfccc028a391f0.png)](https://p1.ssl.qhimg.com/t0145bfccc028a391f0.png)

后面的工作，就是挑选一个Task开始逆向分析，task实现代码中包含很多有用信息。



## 七、漏洞挖掘及利用

### 7.1 环境搭建

对基带漏洞进行利用，需要满足可以从OTA(即通信中的空中接口)发送特定数据给手机基带的目的，这就要搭建一个自己完全控制的蜂窝网络，可以通过软件无线电实现，网络端的协议栈可以运行在电脑上，SDR硬件则工作在相应频率作为收发器使用。

关于基站的搭建过程，Amat也没有详细阐述，不过可以参考独角兽安全团队的著作《无线电安全攻防大揭秘》。

### 7.2 调试基带

由于每一次modem crash都可以得到一个ramdump文件，并且dump文件中包含有每一crash时的寄存器状态上下文，这会对逆向分析很有用。可以写一个脚本去分析这些dump文件获取一些有效信息，包括寄存器状态，内存信息等等。这些不同场景的dump文件，其实可以达到类似于调试器的效果。

### 7.3 深入分析

Layer 3的信令按照一种称为Information Elements的风格组织，具体有三种，V,LV,TLV,分别代表value, length + value, tag + length + value. 每条信令都可能包含一个或者多个V, LV, TLV 的区段，3GPP标准中有这些区段的定义，阅读相关的定义，并通过对task代码进行逆向分析，找到处理这些区段的代码。一些漏洞在这个过程中会被发现。

这里举一个例子, CC task 看起来是处理 呼叫控制( call control)的代码，呼叫控制（Call control）负责 GSM 协议中呼叫连接管理。

下面这个表格中是Call control的不同的信令消息。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01face2ec36aa0a300.png)

下面是Call control各区段的定义。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b9046624c474ca2a.png)

如果想熟悉一下call control信令，也可以搭个osmocomBB，将mobile功能跑起来，用wireshark抓一下信令，具体请参阅《无线电安全攻防大揭秘》，下图是我抓的一个电话呼叫信令。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b2e7a140ab1be6a5.png)

通过逆向分析CC task发现了一些漏洞，但是根据Amat参加几次pwn2own的经验历，这类漏洞对于pwn2own而言，基本毫无用处。而且简单漏洞，在比赛中撞洞的风险很大，因此需要更深入的分析以便找到更复杂的漏洞。

### 7.4 Pwn2own漏洞

Amat决定分析更为复杂的GPRS，开始阅读GPRS标准并分析GPRS的会话管理相关信令。下图是GPRS信令协议分层。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0192d1a20f78f7d92a.png)

通过对标准的阅读，发现‘ACTIVATE PDP CONTEXT ACCEPT‘这条信令比较复杂，看起来很适合深入分析，下图是该信令各区段的详细定义

[![](https://p2.ssl.qhimg.com/t015c77eda5f99c9971.png)](https://p2.ssl.qhimg.com/t015c77eda5f99c9971.png)

Amat通过对SM task的逆向，找到了处理这些信令的代码，其中也包括‘ACTIVATE PDP CONTEXT ACCEPT ‘信令。

在这里PDP 指的是‘Packet Data Protocol‘， GPRS 建立连接时，终端会发送’ ACTIVATE PDP CONTEXT ’信令，如果基站允许，则会回复’ACTIVATE PDP CONTEXT ACCEPT’。

下面代码片断是处理’Protocol configuration options’的，后面后详细说明（不要吃惊，这是从IDA 中逆向分析而来，F5反编译转化为C代码，其中有Amat做的注释和函数名还原）。

[![](https://p2.ssl.qhimg.com/t0104243d896c5f8c2b.png)](https://p2.ssl.qhimg.com/t0104243d896c5f8c2b.png)

’Protocol configuration options’的功能包括：

发送与PDP上下文激活关联的外部网络协议选项，以及发送与外部协议或应用程序相关联的附加（协议）数据（例如配置参数，错误代码或消息/事件等）。

代码片段处理的是 IPCP (Internet Protocol Control Protocol)， 具体内容如下

[![](https://p5.ssl.qhimg.com/t01eba977cef161f26a.png)](https://p5.ssl.qhimg.com/t01eba977cef161f26a.png)

下面从前面逆向分析的代码中截取的片段

[![](https://p2.ssl.qhimg.com/t01e66ca890a0c83c58.png)](https://p2.ssl.qhimg.com/t01e66ca890a0c83c58.png)

### 7.5 漏洞利用

设计的利用场景如下图，基站发送ACTIVE PDP CONTEXT ACCEPT给手机，从而触发漏洞，并利用漏洞。

[![](https://p1.ssl.qhimg.com/t01b75adc05ae5c5a1a.png)](https://p1.ssl.qhimg.com/t01b75adc05ae5c5a1a.png)

然而理想很丰满，现实却很骨感，遇到的问题是手机仅仅在特定的状态下，即手机向基站发送’ ACTIVATE PDP CONTEXT REQUEST’之后，才接收‘ACTIVE PDP CONTEXT ACCEPT’信令。

所以现在问题变为怎么让手机发送‘ACTIVATE PDP CONTEXT REQUEST‘信令。当手机的APN设置中包含伪基站网络配置的信息时，手机会发送’ACTIVATE PDP CONTEXT REQUEST‘信令，但这在pwn2own规则中是个问题，不允许人工介入操作。

阅读3GPP标准更多的内容之后，发现通过给手机发送‘REQUEST PDP CONTEXT ACTIVATION ‘信令可以之后，可以强制手机发送’ ACTIVATE PDP CONTEXT REQUEST ‘。

[![](https://p2.ssl.qhimg.com/t01da488b0a9870da4b.png)](https://p2.ssl.qhimg.com/t01da488b0a9870da4b.png)

于是攻击流程变为下图所示。

[![](https://p5.ssl.qhimg.com/t01ecfe81261dd98363.png)](https://p5.ssl.qhimg.com/t01ecfe81261dd98363.png)

为了实施攻击，需要修改YateBTS的代码，添加实现发送‘REQUEST PDP CONTEXT ACTIVATION‘的代码。需要改动的是 mbts/SGSNGGSN/Ggsn.cpp文件。

由于arm cache-fu的限制，在payload的一阶段需要ROP，之后将相应的shellcode拷贝到特定的可读写执行(RWX)内存区域，然后做一次cache刷新，包括i-cache(指令cache)，d-cache(数据cache)。后面的事情就是跳转去执行shellcode了。

Shellcode可以做任何事情，但为了更好的演示效果，Amat挑选的是通过在RFS（Remote file system， 用于给基带存储NV 信息，在Android上可以访问）写入一个文件。

当然payload也可以做别的事情，比如插入一个调试器，以便更好的分析其他漏洞。

### 7.6 漏洞演示

通过空口远程攻击基带，实现在RFS中写入一个文件，并在Android端查看文件，下面的图片显示漏洞利用成功。

[![](https://p3.ssl.qhimg.com/t0167e6bcc8e0cafbb8.png)](https://p3.ssl.qhimg.com/t0167e6bcc8e0cafbb8.png)



## 八、总结

基带漏洞挖掘虽然对安全研究员的基本功要求很高，需要熟练掌握处理器原理，操作系统原理相关知识，以及熟练的二进制分析及漏洞利用技巧，但是并不需要过多的通信专业知识。如果阅读此文的小伙伴们，有坚实的二进制分析功底，也对基带漏洞挖掘有浓厚兴趣，可以发简历至unicornteam@360.cn。



## 九、参考文献

[1] Yuwei Zheng , Lin Huang, Ghost telephonist’ link hijack exploitations in 4g lte cs fallback [https://www.blackhat.com/docs/us-17/thursday/us-17-Yuwei-Ghost-Telephonist-Link-Hijack-Exploitations-In-4G-LTE-CS-Fallback.pdf](https://www.blackhat.com/docs/us-17/thursday/us-17-Yuwei-Ghost-Telephonist-Link-Hijack-Exploitations-In-4G-LTE-CS-Fallback.pdf)

[2] Nico Golde ,Breaking Band–reverse engineering and exploiting the shannon baseband [https://comsecuris.com/slides/recon2016-breaking_band.pdf](https://comsecuris.com/slides/recon2016-breaking_band.pdf)

[3] Lin Huang, Forcing Targeted **LTE** Cellphone into Unsafe Network, [https://conference.hitb.org/hitbsecconf2016ams/materials/D1T1%20-%20Lin%20Huang%20-%20Forcing%20a%20Targeted%20LTE%20Cellphone%20into%20an%20Eavesdropping%20Network.pdf](https://conference.hitb.org/hitbsecconf2016ams/materials/D1T1%20-%20Lin%20Huang%20-%20Forcing%20a%20Targeted%20LTE%20Cellphone%20into%20an%20Eavesdropping%20Network.pdf)

审核人：Atoo      编辑：少爷
