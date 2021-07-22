> 原文链接: https://www.anquanke.com//post/id/162642 


# 深入分析sLoad Downloader：面向英国和意大利传播Ramnit银行木马


                                阅读量   
                                **168260**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Proofpoint.com，文章来源：proofpoint.com
                                <br>原文地址：[https://www.proofpoint.com/us/threat-insight/post/sload-and-ramnit-pairing-sustained-campaigns-against-uk-and-italy](https://www.proofpoint.com/us/threat-insight/post/sload-and-ramnit-pairing-sustained-campaigns-against-uk-and-italy)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01ee13f7637636489f.png)](https://p2.ssl.qhimg.com/t01ee13f7637636489f.png)



## 一、概述

自2018年5月以来，Proofpoint研究人员观察到使用新型Downloader sLoad的电子邮件恶意活动。sLoad是一个用来下载PowerShell的程序，其最常投递的是Ramnit银行木马，并且其中还包含值得我们关注的侦查功能。该恶意软件收集有关被感染主机的信息，包括：正在运行的进程列表、Outlook相关信息以及Citrix相关文件。此外，sLoad还可以获取屏幕截图，并检查特定域名的DNS缓存（例如目标银行），以及加载外部的二进制文件。在本文中，我们将首先对sLoad进行详细分析，随后介绍长期以来攻击者利用sLoad开展的恶意活动，包括在恶意活动中对电子邮件收件人姓名和地址的个性化。最后，将分析该恶意活动所针对的特定国家范围。



## 二、承载恶意软件

尽管sLoad的版本出现在2018年5月，但至少从2017年初，我们就发现这一恶意活动，并开始进行追踪。我们将该恶意活动内部命名为TA554。此外，也有其他的一些研究者注意到了这一恶意活动。下图展现了该恶意活动近期活动的快照，该记录从sLoad出现之前就已经开始。

[![](https://www.proofpoint.com/sites/default/files/slf1.png)](https://www.proofpoint.com/sites/default/files/slf1.png)

根据历史监测到的信息，该恶意活动主要针对于意大利、加拿大和英国地区，向这些地区的邮箱发送恶意电子邮件。这些电子邮件使用相应国家的语言撰写，通常会针对每个用户进行个性化定制，在电子邮件正文和标题部分包含收件人的姓名与地址。TA554经常使用“快递运送”或“订单通知”主题诱导目标用户点击，邮件中包含压缩LNK文件的URL链接，或是在附件中包含压缩文档。LNK文件或压缩文档将下载下一阶段的恶意软件，通常是一个PowerShell脚本，该脚本用于下载最终PowerShell或其他Downloader（例如sLoad）。

2018年10月14日，针对意大利发出的恶意邮件：

[![](https://www.proofpoint.com/sites/default/files/slf2.png)](https://www.proofpoint.com/sites/default/files/slf2.png)

2018年10月11日，针对英国发出的恶意邮件，该恶意邮件经过个性化定制，包含收件人的姓名和地址：

[![](https://www.proofpoint.com/sites/default/files/slf3.png)](https://www.proofpoint.com/sites/default/files/slf3.png)

该恶意活动经常使用一个或多个中间Downloader，例如尚未命名的PowerShell脚本、sLoad、Snatch或Godzilla。我们同时也监测到了其最终的Payload，包括Ramnit、Gootkit、DarkVNC、Ursnif和PsiXBot。

在感染链的所有步骤中，会通过源IP地址确定用户当前所在国家，并基于此限制对内容的访问。例如，我们观察到在以下位置将会进行检查：

1、下载压缩后的LNK文件；

2、LNK下载PowerShell；

3、PowerShell下载sLoad；

4、sLoad与命令和控制（C&amp;C）服务器进行通信；

5、sLoad接收任务或命令（通过Base64编码的二进制文件）。

其中，步骤2和5中额外加入了“Headers-fenced”，这也就意味着，该请求必须与BITS（后台智能传输服务）的请求相匹配。



## 三、恶意软件分析

### <a class="reference-link" name="3.1%20%E6%A6%82%E8%A6%81"></a>3.1 概要

下图展现了在10月17日一条完整感染链中的网络流量情况，从用户点击恶意电子邮件中链接开始，到PowerShell和sLoad的下载，再到后续sLoad的C&amp;C流量。

[![](https://www.proofpoint.com/sites/default/files/slf4.png)](https://www.proofpoint.com/sites/default/files/slf4.png)

感染链中包含的主要内容如下：

第1行：用户点击电子邮件中的URL，从而导致从invasivespecies[.]us下载一个压缩后的LNK文件（Windows快捷方式文件）。

第3行：用户运行LNK，将从hotline[.]com/otki2/kine下载第二阶段文件（PowerShell）。

第5行：PowerShell下载sLoad（来自lookper[.]eu/userfiles/p2.txt）。

第7行：PowerShell下载包含sLoad C&amp;C主机信息的文件（来自lookper[.]eu/userfiles/h2.txt）。

第8-9行：sLoad初始信标。

第10-11行：sLoad收集被感染的系统信息并发送到C&amp;C，同时向C&amp;C轮询命令。

第13行：sLoad在收到命令后，下载Ramnit。在这里，我们发现sLoad在一天后才收到下载下一阶段的命令。

第14行：sLoad向C&amp;C发送屏幕截图。

### <a class="reference-link" name="3.2%20LNK"></a>3.2 LNK

我们分析用作第一阶段Downloader的LNK文件，发现这些文件都会倾向于指向执行下载操作的PowerShell命令，该命令位于“链接目标”字段内。通过该文件，可以轻松提取并分析执行的PowerShell命令。举例来说，在Windows上，就可以通过右键点击快捷方式文件，然后选择属性，随后即可在“目标”字段中找到该命令的内容。

然而，有一点不寻常的地方，就是数据可以附加到LNK文件的末尾，在终止块（4个NULL字节）之后。原因在于，Windows在读到终止块后，就会停止读取LNK文件中的后续数据，因此攻击者如果将恶意数据添加到文件的末尾，就可以使用PowerShell/Certutil/External工具在外部解析，并执行代码。

在我们所分析的样本中，附加命令在LNK文件结束后的末尾位置附加。因此，快捷方式的“目标”字段中十几只包含一个简短的“缩略脚本”，该脚本会寻找并执行位于LNK文件结束标识符之后的命令。实际的LNK为1528字节，在其末尾处添加了1486字节的PowerShell代码。

样本LNK属性的截图：

[![](https://www.proofpoint.com/sites/default/files/slf5.png)](https://www.proofpoint.com/sites/default/files/slf5.png)

其中，“目标：”字段包含一个经过混淆的命令，该命令使用“findstr”（实际命令为“nwfxdrtsdnif”）来查找附加在LNK文件末尾的恶意代码，该恶意代码标记有“mrkkikaso”字符串。

下图展现了LNK文件末尾附加的PowerShell代码，该代码负责执行下一阶段的下载操作：

[![](https://www.proofpoint.com/sites/default/files/slf6.png)](https://www.proofpoint.com/sites/default/files/slf6.png)

### <a class="reference-link" name="3.3%20sLoad%20Downloader"></a>3.3 sLoad Downloader

LNK将下载一个轻量级的PowerShell脚本（未命名），该脚本本身包含一些值得关注的功能：

1、执行检查，以查看系统上是否正在运行任何安全进程，如果找到则退出。

2、下载sLoad（样本下载自lookper[.]eu/userfiles/p2.txt），并使用硬编码的密钥，将其加密存储为config.ini。

3、下载sLoad C&amp;C主机文件（样本下载自lookper[.]eu/userfiles/h2.txt），并使用硬编码的密钥，将其加密存储为web.ini。

4、通过计划任务，执行sLoad。

[![](https://www.proofpoint.com/sites/default/files/slf7.png)](https://www.proofpoint.com/sites/default/files/slf7.png)

### <a class="reference-link" name="3.4%20sLoad"></a>3.4 sLoad

sLoad同样也是使用PowerShell编写而成。在撰写本文时，最新的sLoad版本为5.07b，我们将以此版本为例重点进行分析。其中包含一些需要重点关注的功能，包括：<br>
1、收集系统信息，并向C&amp;C服务器发送，其中包括：正在运行的进程列表、系统上存在的.ICA文件（可能与Citrix相关）、系统上是否存在Outlook文件、额外的侦查数据。

2、进行截屏。

3、查看特定域名（例如目标银行）的DNS缓存。

4、加载外部二进制文件。

sLoad的网络通信以路径为“/img.php?ch=1”的初始C&amp;C信标开始，这是一个空请求。在收到该请求后，恶意服务器可能会响应“sok”内容。

在发送初始信标之后，sLoad进入一个循环。在该循环中，它会将被感染系统的大量信息推送到C&amp;C服务器上，等待接收并执行来自服务器的命令，并将屏幕截图发送到服务器上。在该循环中，首先执行“captcha.php”请求，并通过URL参数发送有关被感染主机的信息。

在“captcha.php”请求中，URL参数及对应值如下：

（1）g = “pu” 硬编码值。

（2）c = “0” 如果在系统上找到任何带有.ICA扩展名的文件，就从C:users文件夹开始搜索，并且将该值置为1，否则该值为0。根据推断，该文件可能与Citrix相关。

（3）id 使用(Get-WmiObject Win32_ComputerSystemProduct).UUID生成系统的UUID。

（4）v = “Microsoft Windows 7 Ultimate” 使用(gwmi win32_operatingsystem).caption获取的操作系统名称。

（5）c = “GLklWOaPjmVuQiCD” 针对每个请求，都生成16位随机字符串，字符串中同时包含大写和小写字母。

（6）a = “**armsvc**cmd**cmd**conhost” 正在运行的进程列表，使用“**”来进行分隔。**

** （7）d 当前域或网络中的计算机数量。如果没有，该参数可以为空。其值也可以类似于“`{`in network：1`}`”。**

** （8）n = “MARK-PC” 使用$env:ComputerName获取的计算机名称**

** （9）bu = “**nwolb.com**barclays.co.uk” 系统DNS缓存中，与目标银行相匹配的DNS缓存记录，使用“**”来进行分隔。

（10）cpu = “Intel(R) Core(TM) i5-780HQ CPU @ 2.91GHz” 系统处理器信息。

（11）o = “0” 如果”..MicrosoftOutlook”目录存在，该值为1，否则为0。

sLoad读取并保存服务器对“captcha.php”请求的响应。如果返回任何响应，那么sLoad将会对其进行检查，并进行相应操作。响应及对应说明如下：

（1）“run=”：从给定URL进行下载，并执行其PowerShell内容。

（2）“updateps=”：从给定URL进行下载，并保存其PowerShell内容。实际上，这一响应实现了恶意软件的自我更新功能。下载的内容将会替换磁盘上当前存储的sLoad文件内容，并停止当前的sLoad实例

（3）任何其他长度大于3的响应：从给定URL进行下载，使用“certutil”对其进行解码，将其保存为可执行文件，并启动该可执行文件。

在主循环结束后，sLoad会将被感染主机桌面的截图上传到“p.php”URL。sLoad将会执行长达10分钟的休眠，随后再次轮询服务器获取后续命令，并上传更多屏幕截图。

sLoad将其屏幕截图发送到C&amp;C服务器：

[![](https://www.proofpoint.com/sites/default/files/slf8_new.png)](https://www.proofpoint.com/sites/default/files/slf8_new.png)

sLoad中包含一个硬编码保存的银行关键字和主机名列表数组，将被感染主机上的DNS缓存与此列表进行比较，并在“bu”参数中保存匹配项，最后将其发送到C&amp;C。以下是针对意大利银行的样本截图：

[![](https://www.proofpoint.com/sites/default/files/slf8_0.png)](https://www.proofpoint.com/sites/default/files/slf8_0.png)

以下是针对英国银行的样本截图：

[![](https://www.proofpoint.com/sites/default/files/slf9.png)](https://www.proofpoint.com/sites/default/files/slf9.png)

sLoad将从“C:users”文件夹开始，搜索扩展名为.ICA的文件。由于这种格式通常被Citrix应用服务器作为配置文件使用，因此我们假设这一行为很可能与Citrix有关。

[![](https://www.proofpoint.com/sites/default/files/slf10.png)](https://www.proofpoint.com/sites/default/files/slf10.png)



## 四、sLoad版本

自从2018年5月以来，我们监测到sLoad的多个版本，这些升级版本不断添加其功能。

2018年5月1日 0.01b版本

2018年5月9日 2.01b版本

2018年5月12日 2.11b版本

2018年6月6日 2.37b版本

2018年6月26日 3.47b版本

2018年8月23日 4.07b版本

2018年9月20日 5.07b版本

2018年10月3日 5.08b版本

此外，我们还观察到了许多版本的控制面板，如下面截图所示。

0.01b版本C&amp;C面板的屏幕截图：

[![](https://www.proofpoint.com/sites/default/files/slf11.png)](https://www.proofpoint.com/sites/default/files/slf11.png)

2.01b版本C&amp;C面板的屏幕截图：

[![](https://www.proofpoint.com/sites/default/files/slf12.png)](https://www.proofpoint.com/sites/default/files/slf12.png)

2.37b版本C&amp;C面板的屏幕截图：

[![](https://www.proofpoint.com/sites/default/files/slf13.png)](https://www.proofpoint.com/sites/default/files/slf13.png)

4.07b版本C&amp;C面板的屏幕截图：

[![](https://www.proofpoint.com/sites/default/files/slf14.png)](https://www.proofpoint.com/sites/default/files/slf14.png)



## 五、新的TTP（2018年10月23日更新）

在2018年10月22日，该恶意活动在压缩后INK下载文件中添加了一个新的页面。在新的页面，.LNK将会直接下载sLoad，而不经过中间的PowerShell。

面向被感染用户的新登录页面：

[![](https://www.proofpoint.com/sites/default/files/last_image.png)](https://www.proofpoint.com/sites/default/files/last_image.png)



## 六、结论

Proofpoint的研究人员发现了一个隐形的Downloader，该恶意软件结合了个性化电子邮件欺诈和复杂的地理围栏。与我们近期发现的其他Downloader一样，sLoad会收集被感染主机的特征信息，从而允许攻击者更好地选择他们最为感兴趣的目标。最终的Payload是一个银行木马，攻击者借助该木马可以窃取额外数据，同时也可以对被感染主机的用户进行人为攻击。sLoad为攻击者提供了一个灵活的选择，并充分考虑到沙箱逃避、设置特定目标等攻击者的实际需要。



## 七、参考

[1] [https://asert.arbornetworks.com/snatchloader-reloaded/](https://asert.arbornetworks.com/snatchloader-reloaded/)

[2] [https://isc.sans.edu/forums/diary/Malicious+Powershell+Targeting+UK+Bank+Customers/23675/](https://isc.sans.edu/forums/diary/Malicious+Powershell+Targeting+UK+Bank+Customers/23675/)

[3] [https://myonlinesecurity.co.uk/your-order-no-8194788-has-been-processed-malspam-delivers-malware/](https://myonlinesecurity.co.uk/your-order-no-8194788-has-been-processed-malspam-delivers-malware/)

[4] [http://blog.dynamoo.com/2017/02/highly-personalised-malspam-making.html](http://blog.dynamoo.com/2017/02/highly-personalised-malspam-making.html)

[5] [https://msdn.microsoft.com/en-us/library/dd871305.aspx](https://msdn.microsoft.com/en-us/library/dd871305.aspx)

[6] [https://www.uperesia.com/booby-trapped-shortcut-generator](https://www.uperesia.com/booby-trapped-shortcut-generator)

[7] [https://lifeinhex.com/analyzing-malicious-lnk-file/](https://lifeinhex.com/analyzing-malicious-lnk-file/)

[8] [https://twitter.com/ps66uk/status/1054706165878321152](https://twitter.com/ps66uk/status/1054706165878321152)



## 八、IoC

### <a class="reference-link" name="8.1%20URL"></a>8.1 URL

hxxps://invasivespecies[.]us/htmlTicket-access/ticket-T559658356711702

hxxps://davidharvill[.]org/htmlTicket-access/ticket-V081650502356

hxxps://schwerdt[.]org/htmlTicket-access/ticket-823624156690858

hxxps://hotkine[.]com/otki2/kine

hxxps://lookper[.]eu/userfiles/p2.txt

hxxps://lookper[.]eu/userfiles/h2.txt

hxxps://maleass[.]eu/images//img.php?ch=1

hxxps://informanetwork[.]com/update/thrthh.txt

### <a class="reference-link" name="8.2%20SHA256"></a>8.2 SHA256

5ea968cdefd2faabb3b4380a3ff7cb9ad21e03277bcd327d85eb87aaeecda282

a446afb6df85ad7819b90026849a72de495f2beed1da7dcd55c09cd33669d416

79233b83115161065e51c6630634213644f97008c4da28673e7159d1b4f50dc2

245c12a6d3d43420883a688f7e68e7164b3dda16d6b7979b1794cafd58a34d6db1032db65464a1c5a18714ce3541fca3c82d0a47fb2e01c31d7d4c3d5ed60040

### <a class="reference-link" name="8.3%20%E5%9F%9F%E5%90%8D%E4%B8%8EIP"></a>8.3 域名与IP

xohrikvjhiu[.]eu

185.197.75.35
