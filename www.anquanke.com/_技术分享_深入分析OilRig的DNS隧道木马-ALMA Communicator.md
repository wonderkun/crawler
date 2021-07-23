> 原文链接: https://www.anquanke.com//post/id/87228 


# 【技术分享】深入分析OilRig的DNS隧道木马-ALMA Communicator


                                阅读量   
                                **142247**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：paloaltonetworks.com
                                <br>原文地址：[https://researchcenter.paloaltonetworks.com/2017/11/unit42-oilrig-deploys-alma-communicator-dns-tunneling-trojan/](https://researchcenter.paloaltonetworks.com/2017/11/unit42-oilrig-deploys-alma-communicator-dns-tunneling-trojan/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01601012eef6d865e4.jpg)](https://p1.ssl.qhimg.com/t01601012eef6d865e4.jpg)

****

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**写在前面的话**

Unit 42自从[2016年五月份](https://researchcenter.paloaltonetworks.com/2016/05/the-oilrig-campaign-attacks-on-saudi-arabian-organizations-deliver-helminth-backdoor/)开始就一直在密切跟踪[黑客组织**OilRig**](https://researchcenter.paloaltonetworks.com/tag/oilrig/)的一举一动。根据我们研究人员的观察与发现，从2016年五月份开始，这个名叫OilRig的黑客组织在其网络钓鱼攻击活动中开始使用[**Clayslide**文档](https://researchcenter.paloaltonetworks.com/tag/clayside/)来作为钓鱼邮件的附件。在2017年四月份，我们还发布了一篇分析文章专门给大家介绍了OilRig黑客组织是如何开发和优化这种Clayslide文档的，感兴趣的同学可以阅读一下【[文章传送门](https://researchcenter.paloaltonetworks.com/2017/04/unit42-oilrig-actors-provide-glimpse-development-testing-efforts/)】。

近期，我们又观察到了一种新版本的Clayslide文档，它的开发人员将其称之为“**ALMA Communicator**”，而OilRig的攻击者可以使用Clayslide文档在目标用户的主机中安装一种新型的自定义木马。这种恶意文档还可以存储类似Mimikatz之类的后渗透凭证收集工具，而研究人员则认为攻击者引入这种功能的最终目的还包括从目标用户的主机中收集账号凭证信息。虽然我们现在还没有拿到详细的数据，但是我们有理由相信这种攻击活动针对的是中东地区一家公共事业公司的个人用户。

 

**新型的Clayslide文档**

近期出现的最新版本Clayslide文档其运行机制与之前的Clayslide文档非常相似，它一开始会给用户显示一个“不兼容”的Excel工作表，并声称这个Excel文件是使用一个更新版本的Excel创建的，因此用户需要点击“启用内容”来查看该文档的内容。如果用户点击了“启用内容”之后，文件会显示一个隐藏的工作表并触发恶意宏的运行，而这个隐藏的工作表中包含的是攻击者所设置的“诱饵”内容，隐藏工作表中的内容大致如下图所示：

[![](https://p2.ssl.qhimg.com/t01cdc11138d4b9bff4.png)](https://p2.ssl.qhimg.com/t01cdc11138d4b9bff4.png)

当“诱饵”内容显示给用户之后，恶意宏会从这个“不兼容”工作表中的某个特定单元格中开始访问数据，并创建一个**.HTA**文件，然后将其存储至路径%PUBLIC%tmp.hta之中，最后再使用mshta.exe应用程序来打开这个文件。这个.HTA文件中包含HTML代码，而这些代码将运行一个VBScript脚本并在目标用户的主机中运行最终的恶意Payload。

恶意Payload过程描述如下：首先，.HTA会创建一个名叫%PUBLIC%`{`5468973-4973-50726F6A656374-414C4D412E-2`}`的文件夹，然后再向这个文件夹中写入三个文件，这三个文件的文件名分别为：



```
SystemSyncs.exe
m6.e
cfg
```

.HTA文件中包含两个已编码的可执行文件，随后它会对这两个文件进行解码，并将其写入m6.e和SystemSyncs.exe中。.HTA文件还包含一个Base64编码的配置文件，解码之后便会被写入cfg文件之中，而恶意木马之后需要使用这些配置信息来获取C2域名，并使用它来与攻击者进行通信。在该攻击活动之中，保存在cfg文件中的C2域名为prosalar[.]com。<br>

SystemSyncs.exe文件（SHA256: 2fc7810a316863a5a5076bf3078ac6fad246bc8773a5fb835e0993609e5bb62e）是一个由OilRig黑客组织开发出来的自定义木马，这个木马就是“ALMA Communicator”，我们待会儿会在接下来的章节中对其进行详细介绍。

.HTA文件所释放出来的“m6.e”文件其实是Mimikatz工具的变种版本（SHA256: 2d6f06d8ee0da16d2335f26eb18cd1f620c4db3e880efa6a5999eff53b12415c）。在此之前，我们曾见到过OilRig黑客组织在其后渗透活动中使用Mimikatz工具来收集凭证信息。但是，这一次是我们第一次发现OilRig组织在攻击的感染阶段就使用Mimikatz工具。考虑到ALMA Communicator的C2通信功能以及性能限制，我们认为释放这一额外工具（Mimikatz变种）的就是该组织所使用的Clayslide文档，待会儿也会对这部分内容进行详细分析。

.HTA文件中的VBScript负责执行SystemSyncs.exe Payload，并且还会通过创建一个计划任务来实现攻击持久化。之前的Clayslide文档主要通过schtask应用程序（通过命令提示窗）来创建计划任务，而这个.HTA文件中的VBScript使用的是编程的方式（使用Schedule.service对象）来创建计划任务。请大家看下面这张截图，计划任务创建成功之后， ALMA Communicator Payload每两分钟就会执行一次（配合命令行参数“Lock”）：

[![](https://p3.ssl.qhimg.com/t015db27927d7f413dd.png)](https://p3.ssl.qhimg.com/t015db27927d7f413dd.png)

 

**ALMA Communicator木马**

ALMA Communicator木马是一款后门木马，它使用了DNS隧道来从攻击者那里接收控制命令并从目标主机中提取数据。随后，这个木马会从Clayslide文档所创建的cfg文件中读取配置信息。ALMA中并不包含内部配置文件，所以如果没有这个cfg文件的话，该木马就无法正常运行了。

在读取完配置文件之后，该木马会创建两个文件夹，即Download和Upload。ALMA使用Download文件夹来保存C2服务器提供的批处理文件，这些文件之后会运行。ALMA使用Upload文件夹来存储批处理文件执行后的输出，最终这些数据会发送给C2服务器。

ALMA Communicator使用了DNS隧道来作为其C2通信信道，这种DNS隧道使用了一种特殊的协议，并且使用了专门的子域名来给C2服务器传输数据，而服务器使用了专门的IPv4地址来给木马发送数据。

在构建这种专门的子域名时，木马会生成一个随机的四位数字，并连接一个硬编码字符串，最后再在字符串末尾添加一个用于标识受感染系统的唯一标识符。为了生成这个唯一标识符，该木马会从目标系统的注册表中获取ProductId，该参数位于SOFTWAREMicrosoftWindows NTCurrentVersionProductId。如果无法找到这个注册表键，它将会使用硬编码值00000-00000-00000-00000。接下来，它还会获取当前系统的用户名，后面跟上一个下划线并加上ProductId字符串。该木马会计算这个字符串的MD5哈希，然后将其作为受感染系统的唯一标识符。最后，它会添加硬编码的-0-2D-2D字符串来结束子域名（用于C2服务器通信）的构造。下图显示的是域名的结构：

[![](https://p5.ssl.qhimg.com/t0122dcc40afd671b48.png)](https://p5.ssl.qhimg.com/t0122dcc40afd671b48.png)

为了让大家更清楚地了解ALMA生成的唯一标识符，我们假设测试系统的用户名和ProductId创建的字符串为Administrator_00000-00000-00000-00000，其MD5哈希为35ead98470edf86a1c5a1c5fb2f14e02。接下来，该木马会选取MD5哈希中的第1、5、9、13、17、21、25和29个字符，并将其组合生成唯一标识符字符串3d7f11b4。具体如下图所示:

[![](https://p1.ssl.qhimg.com/t01ea10f9a4b3dd7699.png)](https://p1.ssl.qhimg.com/t01ea10f9a4b3dd7699.png)

C2服务器将会使用A记录中的IPv4地址来回应DNS请求，而木马将会从这些请求中解析出两个IP地址，一个用于标识数据传输（C2-&gt;木马）的开始，一个用于标识数据传输（C2-&gt;木马）的结束。这两个特殊的IP地址如下：



```
开始– 36.37.94.33 ($%^!)
结束– 33.33.94.94 (!!^^)
```

在我们的分析过程中，C2服务器发送给我们的分析系统的数据如下所示（“$%^!”和“ !!^^”分别代表数据的起始部分和末尾部分）：



```
$%^!_DnsInit.bat@echo off &amp; chcp 65001rnecho
%userdomain%\%username% 2&gt;&amp;1 &amp; echo %computername% 2&gt;&amp;1 &amp; echo
________________________________Task__________________________________
&amp; schtasks /query /FO List /TN "Google_`{`50726F6A656374-
414C4D41-48747470`}`" /V | findstr /b /n /c:"Repeat: Every:" 2&gt;&amp;1
&amp; schtasks /query /FO List /TN "Micro_`{`50726F6A656374-
414C4D41-446E73-2`}`" /V | findstr /b /n /c:"Repeat: Every:" 2&gt;&amp;1 &amp; echo
______________________________________________________________________   !!^^
```

基于C2服务器传回的数据，该木马会使用数据中的命令来创建一个名叫_DnsInit.bat的文件，然后将其存储在Download文件夹中。接下来，该木马会枚举该文件夹中的文件名，然后使用批处理脚本的路径作为命令行参数来创建一个cmd.exe进程。在进程开始运行之前，该木马还会加上下面这行命令行参数：

```
rnDEL /f /q ”%~0”|exit
```

下面给出的是该木马在向C2服务器发送数据时所使用的DNS查询语句的结构：

```
[random 4 digits]ID[unique identifier]-[number of DNS queries needed]-[string of hexadecimal bytes for sent data]-[string of hexadecimal bytes for filename being sent].prosalar[.]com
```

其中每一次DNS请求一次只能发送10个字节的数据，下面给出的是当测试系统运行了_DnsInit.bat脚本之后所发送的第一条DNS查询：

[![](https://p5.ssl.qhimg.com/t019b4e4134d5604aac.png)](https://p5.ssl.qhimg.com/t019b4e4134d5604aac.png)

由此可以看出，ALMA Communicator的C2信道在数据传输时有一定的性能限制，如果你想使用ALMA Communicator来提取大型文件的话，则会产生大量的出境DNS请求。可能正是因为这个原因，OilRig黑客组织才会选择利用Clayslide文档来携带Mimikatz工具并使用它来从受感染的系统中提取数据（后渗透阶段）。

 

**总结**

目前OilRig黑客组织仍在他们的攻击活动中使用这种Clayslide文档，从我们对当前Clayslide变种的分析中可以看出，该黑客组织现在还在这类文档中尝试新的安装技术以及检测绕过技术。



**入侵威胁指标IoC**

```
f37b1bbf5a07759f10e0298b861b354cee13f325bc76fbddfaacd1ea7505e111 (Clayslide)
2fc7810a316863a5a5076bf3078ac6fad246bc8773a5fb835e0993609e5bb62e (ALMA Communicator)
2d6f06d8ee0da16d2335f26eb18cd1f620c4db3e880efa6a5999eff53b12415c (Mimikatz)
prosalar[.]com
```


