> 原文链接: https://www.anquanke.com//post/id/86054 


# 【技术分享】如何检测Windows中的横向渗透攻击


                                阅读量   
                                **324154**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：europa.eu
                                <br>原文地址：[http://cert.europa.eu/static/WhitePapers/CERT-EU_SWP_17-002_Lateral_Movements.pdf](http://cert.europa.eu/static/WhitePapers/CERT-EU_SWP_17-002_Lateral_Movements.pdf)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p5.ssl.qhimg.com/t0139d8ec6cafdbfd26.jpg)](https://p5.ssl.qhimg.com/t0139d8ec6cafdbfd26.jpg)**



翻译：[**興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

**预估稿费：300RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

**横向渗透攻击技术是复杂网络攻击中广泛使用的一种技术，特别是在高级持续威胁（Advanced Persistent Threats，APT）中更加热衷于使用这种攻击方法。**攻击者可以利用这些技术，以被攻陷的系统为跳板，访问其他主机，获取包括邮箱、共享文件夹或者凭证信息在内的敏感资源。攻击者可以利用这些敏感信息，进一步控制其他系统、提升权限或窃取更多有价值的凭证。借助此类攻击，攻击者最终可能获取域控的访问权限，完全控制基于Windows系统的基础设施或与业务相关的关键账户。

在这份白皮书中，我们向大家介绍了如何在Windows Vista/7以及Server 2008系统中检测基于NTLM和Kerberos协议的横向渗透攻击。Windows 10引入了许多额外的安全机制，因此我们准备单独发布另一份白皮书，介绍如何检测Windows 10中的横向渗透攻击。

微软发布过一篇文章，文中介绍了凭证窃取攻击的相关资料以及如何防范这类攻击。除了本文介绍的防御措施之外，我们强烈建议大家根据微软给出的建议对系统进行加固。需要注意的是，这类攻击不仅仅针对Windows系统，其他的基础设施（如使用Kerberos的UNIX环境或单点登录环境）也会受到类似攻击的影响。虽然本文仅仅针对Windows系统提出了检测横向渗透攻击的方法，大家可以举一反三，在保存适当日志的其他环境中使用类似方式检测横向渗透攻击。

此外，感谢微软MSRC（Microsoft Security Response Center，微软安全响应中心）对本文内容的校对和细节验证。

<br>

**二、背景**

**2.1 什么是Windows横向渗透攻击**

在本文中，横向渗透攻击指的是攻击者以某台Windows主机为跳板，利用已窃取的某个账户（如普通用户或服务账户）的有效凭证，建立到目标Windows主机的连接。

源主机通常是目标Windows环境中的一台已被攻陷的主机。在大多数情况下，攻击者会通过包含恶意附件的钓鱼邮件或恶意网站链接，攻陷第一台主机作为跳板。一旦攻击成功，攻击者通常会通过命令控制（Command-and-Control，C2）服务器以及反弹的shell控制目标主机。权限提升成功后，攻击者可以提取存储在源主机中的凭证信息，开展后续的横向渗透攻击，其中包括：

**1、获取源主机的凭证信息**

攻击者可以通过定制工具，访问Windows凭证存储区或内存，以获取任何有效的凭证信息（键盘记录器也可以完成相同任务，但这不在本文的讨论范围内）。本文只讨论与NT哈希和Kerberos凭证有关的内容。

攻击者可能会获取到被攻陷源主机中保存的任何凭证，比如那些正在使用的凭证、曾经使用过的凭证（比如已缓存的凭证）以及内存中尚未清除的凭证（未安装更新时）。攻击者最感兴趣的是目标环境中的高权限账户凭证，比如帮助台（help-desk）账户、域管、高权限服务账户以及本地管理员账户，如果密码被重复使用或者密码生成算法是可预测的，那么攻击环境就更加理想。

**2、通过窃取的凭证访问其他主机或资源**

成功窃取凭证后，攻击者可以使用这些凭证访问其他资源，比如其他主机或服务器（例如Exchange邮箱账户）。攻击者所使用的技术包括基于NT哈希的哈希传递（pass-the-hash，以下简称PtH）攻击以及基于Kerberos票据的票据传递攻击（pass-the-ticket，以下简称PtT）。读者可以参考附录B中的[1][2][3]，了解这些攻击的更多细节。

以下是有关凭证窃取和重放攻击的一些说明：

1、任何用户访问被攻陷的主机后，都可能在其内存中留下凭证信息，在未及时安装补丁时，相关凭证会被攻击者导出。Windows之所以在内存中缓存这些凭证，主要是为了提供诸如单点登录（single-sign-on）的功能，在这种场景下：

（1）在受限管理模式下使用Network Logon或RDP方式登录被控主机时，用户账户凭证不会被泄露。

（2）其他登录方式会暴露账户凭证，包括本地账户、域账户以及服务账户在内的凭证都会受到影响。读者可以参考本文2.3节内容了解更多细节。

2、受影响的凭证不仅仅包括明文的用户名和密码，还包括NT哈希、Kerberos票据以及Kerberos密钥，这些凭证可以被攻击者用来请求Kerberos TGTs（Ticket Granting Ticket），作为有效凭证开展横向渗透攻击。

3、攻击者需要管理员权限以访问本地Windows凭证存储区或内存中的凭证信息（例如Windows安全账户管理器、凭证管理器或者本地安全授权子系统服务进程（及LSASS.exe）中存储的凭证）。如果当前账户权限较低，攻击者可以通过本地提权漏洞获取高权限。

4、横向渗透攻击的目标不单单是另一个工作站，也可以是其他资源，比如Exchange服务器上的邮箱或业务系统。

5、横向渗透攻击使用的是标准的协议，比如Kerberos和NTLM协议，这样一来我们无法通过创建单条Windows事件或网络入侵检测系统（IDS）规则来检测这类攻击。

6、横向渗透攻击的一个优点就是攻击者可以抓取凭证信息并在后续攻击中使用。

7、不仅仅只有Windows会受到横向渗透攻击影响，其他使用单点登录的身份认证协议都会面临相同问题。任何单点登录解决方案都需要以某种有效的方式保存凭证信息，以便在其他服务的认证过程中可以重复使用这些凭证。

**2.2 使用横向渗透攻击的典型APT场景**

通常情况下，APT攻击会不断从某个工作站连接到另一个工作站，以获取越来越高的账户权限，直到他们得到域管账户的凭证为止。接下来攻击者通常会访问域控，导出Windows域中的所有凭证。

APT中使用横向渗透攻击的典型场景如下图所示：

[![](https://p0.ssl.qhimg.com/t01ba52b83f0ed34cec.png)](https://p0.ssl.qhimg.com/t01ba52b83f0ed34cec.png)

图1. APT攻击中使用横向渗透攻击的典型场景

**2.3 凭证缓存**

就如上文所述，当用户使用RDP方式连接工作站（RestrictedAdmin模式除外），或者在工作站中使用runas命令时，包括域用户或者域管在内的凭证信息都会缓存在工作站的内存中。

以某个典型场景为例，当前有某个user1账户已经登录到某台主机中，此时另一个user2账户（管理员）正在登陆同一台主机。在这种情况下，user2在主机中缓存的票据不仅对user1而言是可见的，对已经掌握该主机控制权的攻击者而言也是可见的。user2在当前主机中缓存的Kerberos TGT票据情况如下表所示：

[![](https://p0.ssl.qhimg.com/t01daefbb75c0455db4.png)](https://p0.ssl.qhimg.com/t01daefbb75c0455db4.png)

注：

[1] 如果user2正确注销，则远程主机上不会保存票据信息。

[2] 如果远程会话没有被正确关闭，那么user2的票据就会保留在远程主机中。

[3] 右键菜单中以管理员身份（user2）运行cmd.exe.

[4] 使用的是已缓存的域密码，比如没有接入域环境的笔记本电脑就属于这种场景。

[5] 在以user2身份运行的命令提示符中，使用“net use”命令。

[6] 使用“net use \targetc$”命令，在弹出的对话框中输入user2凭证信息。

[7] 在域控的日志中会包含4768事件，但有趣的是user2的TGT票据并不会被缓存，相反的是，本地主机内存中会保存user1的一个CIFS服务票据，以便访问共享文件夹。

需要注意的是，我们并没有测试所有的登录类型，但在某些场景下，高权限用户（如user2）还是可以访问工作站主机。微软给出了一份更详尽的资料，梳理了哪些可复用的凭证信息会暴露在目标主机中。

上表中，在Windows系统中，右键使用的“以管理员身份运行”功能时（会弹出UAC窗口），用户会得到管理员所有的访问令牌。如果管理员使用runas命令运行某个应用程序（如cmd.exe），情况会有所不同，具体情况如下：

1、右键使用“以管理员身份运行”运行应用程序时，程序退出后，已缓存的NT哈希以及票据仍然会保留在内存中；

2、使用“runas /user:\domuser2”命令时，程序退出后，内存中的凭证会被清除。

有趣的是，在最后一种场景中（即交互式登录后，以管理员身份运行），netlogon服务并不需要重新输入密码！

对于上表的测试用例，有几点情况需要说明：

1、所有的测试都基于非特权的交互式会话（即使用user1的控制台登录）。

2、网络登录状态没有永久保持。

3、委派功能打开和关闭的情况下，我们都做了测试。

4、在注销测试中，不管注销过程中目标账户会话是被正确关闭还是被保留，测试结果都不变。

**2.4 哈希传递与票据传递**

横向渗透测试中，使用哈希传递（Pass-the-Hash，以下简称PtH）或者票据传递（Pass-the-Ticket，以下简称PtT）时，情况会有所不同，具体如下表所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0132ff40c6f7c0ef69.png)

有几个结论比较有趣，如：

1、攻击者需要管理员权限以窃取凭证，但不需要管理员权限就能使用Kerberos票据。

2、密码更改并不会导致Kerberos票据失效。

<br>

**三、检测Windows中的横向渗透攻击**

**3.1 通用法则**

合法的SMB连接与使用PtH和PtT攻击建立的连接并没有什么不同。事实上，攻击者发动这类攻击时并没有利用协议的漏洞，因此，我们没有预先定义的规则来检测此类攻击。

然而，攻击者的攻击行为会存在某些异常特征。例如，如果某个域管账户（如my-admin）只能在某台特定的工作站中使用，那么在其他工作站中使用这个域管账户就显得非常可疑，意味着域环境中可能存在横向渗透攻击。

因此，我们有可能能通过监控Windows事件检测横向渗透攻击。

我们用来检测攻击的主要法则为：

“如果检测到用户账户来自于不正常或非授权系统，或者在不正常或非授权系统中使用，我们判断这种情况下存在横向渗透攻击”。

我们需要注意以下几点：

1、这条法则并不能覆盖所有的横向渗透攻击（某些特权账户的使用检测起来比较困难）。因此，我们需要维护一张包含合法的“用户/工作站/IP地址”三元组的列表，检测不在此表中的账户使用情况。此外，单独使用三元组列表并不能检测所有的攻击场景（比如，攻击者发起的来自合法的用户/工作站的资源访问请求）。

2、这些法则能否有效应用，主要由已有的策略、活动目录结构以及网络隔离机制共同决定。我们需要制定策略，监控专用主机（如专用OU、管理员工作站）上账户的使用情况。我们手头上必须维护一份包含这类工作站的清单。如果这些账户和工作站所使用的策略非常明确，那么我们在检测横向渗透攻击时的效率也会越高，也能避免误报。网络隔离机制将有助于识别横向渗透攻击，特别是对于Kerberos而言，这种隔离机制更加有效，因为Kerberos并没有在相关日志事件中提供具体的主机名信息。

3、为了检测使用本地账户（如本地管理员）的横向渗透攻击，我们需要收集所有可能成为目标的工作站中的日志（4624/4625事件），在某些情况下这个任务很难完成。但这对域账户来说不成问题，因为主要的Windows事件都存储在域控上。微软引入了两个SID，通过设置GPO（Group Policy Object，组策略对象）规则，可以限制本地管理员账户在横向渗透攻击中的使用。

在本文后半部分中，我们会向读者介绍使用PtH和PtT进行横向渗透攻击时所产生的日志事件，以及我们可以设定哪些规则来检测这些攻击。

**3.2 约定及假设**

在本文重点关注的横向渗透攻击场景中，攻击者使用了某个管理员账户（如ADMIN），从其他工作站（而不是ADMIN所属的ADMIN-WS工作站）开始横向渗透。所使用的规则可以稍微调整，以检测其他攻击场景（如使用服务账户或者其他特权账户进行攻击）。

在本文的案例中，我们有几个假设条件，如：

1、我们可以通过查询活动目录识别域管账户（命令为：net group “Domain Admins” /domain）；

2、ADMIN属于管理员组，熟悉环境的攻击者可以挑选其他合适的命名约定；

3、管理员工作站可以通过以下方式识别：

（1）通过工作站的主机名识别。比如通过域中维护的OU（Organizational Unit，组织单元）或主机列表，或者通过命名约定（如admin-ws-1、admin-ws-2等）加以识别。

（2）通过IP地址识别。比如这些工作站具有专用的(V)LAN地址，或这些工作站为跳转服务器，管理员在连接到其他系统前必须登录这些工作站。

4、ADMIN-WS为ADMIN所属的工作站或跳转服务器。

**3.3 检测NTLM横向渗透攻击（PtH）**

**3.3.1 日志中的相关事件**

使用NTLM凭证时，本地以及域控（如果使用的是域用户的话）上生成的所有日志条目如图2所示。详细的日志事件可参考6.1节内容。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01181e4bd4351d2c6c.png)

图2. 与NTLM凭证有关的事件

被攻陷的工作站（infected-ws）中会生成4648事件：“试图使用显式凭据登录（A logon was attempted usingexplicit credentials）”。

所生成的日志事件与攻击者的具体操作有关。在这种场景中，攻击者已经事先将NT哈希注入到目标主机中，之后通过“psexec.exe \Target cmd.exe”命令，打开目标主机上的命令提示符。读者可以参考附录C查看更多细节。

被攻陷的工作站的日志对安全取证来说非常有用，但对主动检测PtH攻击来说用处不大。在这种场景中，我们可以从日志中得知横向渗透攻击的目标主机（clean-ws）。

域控上的日志中会生成两个4776事件：“域控试图验证某个用户凭证的有效性（The domain controller attempted to validate the credentials for an account）”。

第一个4776事件与域控对目标主机（clean-ws$）的验证过程有关。这个事件对检测PtH来说用处不大。

第二个4776事件表明，域控正在验证某个账户（my-admin）的有效性，此时该账户正在访问目标工作站（clean-ws$）。这个事件可以用作检测横向渗透攻击是否存在的指示器，也是监控整个环境的关键要素。

目标主机（clean-ws）的日志中会记录4624事件：“成功登录帐户（An account was successfully logged on）”。

这个事件表明，目标账户（my-admin）已经成功登录到目标工作站（clean-ws）。这个事件也可以用来检测横向渗透攻击，但我们需要收集所有工作站上的所有特定日志。如果工作站或服务器的数量不多，这个事件还是能发挥作用的。

无论如何，该事件与登录失败事件（4625事件）对于安全取证来说非常有用，因为我们可以通过这些事件了解登录的类型（本例中为网络登录，Network logon），以及攻击者从哪台主机（本例中为infected-ws）发起连接。

目标主机的日志中会记录4634/4647事件：“账户被注销/用户启动注销过程（An account was/initiated logged off）”。

这个事件表明攻击者的注销登录动作。对于安全取证来说，这个事件非常有用，安全人员可以结合登录ID值、4624事件以及这个事件，检测攻击行动的会话全流程。

**3.3.2 通用检测方法**

这部分的内容是介绍我们在检测NTLM型横向渗透攻击时，需要在各个主机中收集的事件，以及所需要关心的具体值。正如上文所述，我们需要重点关注域控（DC）上的4776事件，其他关键系统中的4624（登录成功）以及4625（登录失败）事件也值得关注。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013c58b6900b28186e.png)

注意：不要忽视工作站事件日志的重要性，特别是与敏感账户或者特权账户有关的那些事件日志。

**3.4 检测Kerberos横向渗透攻击（PtT）**

**3.4.1 日志中的相关事件**

在Kerberos认证过程中，本地主机以及域控（如果使用的是域用户的话）上生成的所有日志条目如图3所示，详细的事件信息可以参考6.2节内容。

与PtH攻击不同，PtT攻击场景中并没有生成4648事件。

域控的日志中会记录4768事件，即：Kerberos身份验证票证请求（A Kerberos authentication ticket (TGT) was requested）事件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0126c42d73bd194bb5.png)

图3. 与NTLM凭证使用有关的事件

攻击者向域控申请Kerberos TGT票据时就会生成4768事件。在PtT攻击中，我们可能不会在日志中找到这个事件，因为攻击者在这之前已经窃取了TGT票据，不需要向Kerberos分发中心或者域控申请新的TGT票据，只需要利用已窃取的票据即可完成PtH攻击。

域控的日志中会记录4769事件，即：Kerberos 服务票证请求（A Kerberos service ticket was requested）事件。

攻击者请求访问目标系统或资源时（本例中为clean-ws$）会生成该事件。

这个事件可以用作检测横向渗透攻击是否存在的指示器，也是在整个环境中需要监控的主要事件。

目标主机（clean-ws）的日志中会记录4624事件，即：成功登录帐户（An account was successfully logged on）事件。

这个事件表明某个账户（my-admin）已成功登录到目标主机（clean-ws）。我们有可能利用这个事件主动检测横向渗透攻击，但前提是需要收集所有工作站上的相关日志。如果工作站或服务器的数量不多，这个事件也能够发挥作用。

无论如何，这个事件和登录失败（4625）事件对安全取证来说非常有用，因为它提供了具体的登录类型（本例中为网络登录）以及发起登录连接的来源主机（本例中为infected-ws）。

4634/4647事件的含义分别为：帐户被注销/用户启动注销过程。

这两个事件与攻击者的注销过程有关。安全取证工作中，可以利用这两个事件，结合4624事件中的登录ID值，检测攻击行动的会话全流程。

**3.4.2 通用检测方法**

这部分的内容是介绍我们在检测PtT型横向渗透攻击时，需要在各个主机中收集的事件，以及需要关心的具体值。

正如上文所述，我们需要重点关注域控（DC）上的4769以及4768事件。需要注意的是，这一次我们只能检查其中的IP地址信息，因为Kerberos事件中并没有提供具体的主机名。在启用DHCP的环境中，这个限制条件给我们带来了不小的挑战，如果DHCP租用时间较短，我们面临的将会是一个动态变化的网络环境。

关键系统中的4624事件以及4625（登录失败）事件也值得我们关注。

[![](https://p1.ssl.qhimg.com/t01930a8c3eeb4d0cc1.png)](https://p1.ssl.qhimg.com/t01930a8c3eeb4d0cc1.png)

我们使用这种方法可能会检测出假阳性结果：

比如某个管理员（例如help desk）正在打开远程主机上的应用（例如，在远程访问中，通过cmd.exe运行”runas administrator”命令），这种情况下有可能会生成4768事件。

**3.4.3 检测黄金票据（Golden Ticket）**

我们发表了一份白皮书，介绍了Kerberos黄金票据的相关知识，读者可以查阅参考资料了解更多细节。

**3.5 需要监控的主要账户**

本文中描述的监控规则主要是基于域管账户，我们也可以监控其他重要账户，以快速检测横向渗透攻击是否存在，这些账户包括：

1、服务账户（比如，备份账户）；

2、很少使用的账户；

3、应急使用的账户；

4、关键业务账户。

**3.6 需要注意的其他事件**

我们建议大家可以参考NSA发表的一份参考资料，其中介绍了检测潜在攻击时可能有用的其他一些事件。这个参考资料不单单针对横向渗透攻击，同时也覆盖了许多日志事件以及攻击类型。

<br>

**四、附录A-相关定义**

哈希传递攻击（Pass-the-hash，PtH）：PtH是一种黑客技术，攻击者可以利用该技术，使用事先窃取的用户密码的NTLM以及LM哈希，完成对远程服务器或者服务的身份验证，而常规的验证流程中需要输入明文密码。

票据传递攻击（Pass-the-ticket，PtT）：与PtH情况类似，但PtT使用的是Kerberos票据，而不是NT哈希。

凭证（Credential）：可以用来证实某人身份的标识以及相关密钥。根据此定义，凭证的类型不仅仅局限于明文密码，同样也包括Windows的NTLM哈希或者Kerberos票据（与实际使用的Windows认证协议有关）。在某些情况下，Windows会缓存凭证信息，以提供单点登录功能。这篇文章主要关注的是Kerberos票据凭证（Ticket-Granting-Tickets，TGT）。读者可以阅读参考资料[1]，了解与Windows凭证类型（表4）以及凭证缓存有关的更多细节信息。

TGT以及ST Kerberos票据：Ticket-Granting-Tickets（TGT）以及Service Tickets（ST，服务票据）是Kerberos协议的一部分，读者可以阅读参考资料[2]，了解Kerberos以及相关的票据细节信息。

KDC：密钥分发中心（Key distribution Center）。

<br>

**五、附录B-参考资料**

[[1] 如何防御哈希传递攻击以及其他凭证窃取技术](http://www.%20microsoft.com/pth)

[[2] Kerberos认证技术细节](http://technet.microsoft.com/en-us/library/cc739058(v=ws.10).aspx)

[[3] 遭受攻击后如何恢复活动目录](http://technet.microsoft.com/en-us/library/bb727066.aspx#ECAA)

[[4] 凭证保护及管理](http://technet.microsoft.com/en-us/library/dn408190.aspx)

[[5] Windows事件说明](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/Default.aspx)

[[6] Windows 7以及2008中的安全事件](http://www.microsoft.com/download/details.aspx?id=50034)

[[7] 如何发现攻击活动](https://www.iad.gov/iad/library/reports/spotting-the-adversary-with-windows-event-log-monitoring.cfm)

[[8] 如何防御Kerberos黄金票据攻击](http://cert.europa.eu/static/WhitePapers/UPDATED%20-%20CERT-EU_Security_Whitepaper_2014-007_Kerberos_Golden_Ticket_Protection_v1_4.pdf)

<br>

**六、附录C-具体事件说明**

这部分内容主要是介绍Windows日志以及log2timeline日志中与PtH以及PtT攻击有关的具体事件，具体场景为：

1、被攻陷的工作站：USER-WS（IP地址为192.168.89.101）

2、目标用户：my-admin

3、目标主机：admin-ws（IP地址为192.168.89.102）

4、域名：corp.pass.thehash

**6.1 网络登录（Network Logon）以及PtH事件**

**6.1.1 域控中的相关事件**



```
Time: 06:32:56
Event: 4776
Event content:
- PackageName = MICROSOFT_AUTHENTICATION_PACKAGE_V1_0
- TargetUserName = my-admin
- Workstation = USER-WS
- Status = 0x00000000
Command: `psexec.exe \admin-ws cmd.exe`
Comment: The domain controller attempted to validate the credentials for an account
Time: 06:33:37
Event: 4776
Event content:
- PackageName = MICROSOFT_AUTHENTICATION_PACKAGE_V1_0
- TargetUserName = my-admin
- Workstation = USER-WS
- Status = 0x00000000
Command: robocopy.exe c:goodiessch \admin-wsc$
Comment: The domain controller attempted to validate the credentials for an account
Time: 06:34:16
Event: 4776
Event content:
- PackageName = MICROSOFT_AUTHENTICATION_PACKAGE_V1_0
- TargetUserName = my-admin
- Workstation = USER-WS
- Status = 0x00000000
Command: at.exe \admin-ws 06:35 c:schedule.bat
Comment: The domain controller attempted to validate the credentials for an account
```

**6.1.2 来源主机中的相关事件（user-ws）**



```
Time: 06:32:44
Event: 4624
Event content:
- SubjectUserSid = S-1-5-18 SubjectUserName = USER-WS$
- SubjectDomainName = CORP
- SubjectLogonId = 0x00000000000003e7 TargetUserSid = S-1-5-18 TargetUserName = SYSTEM
TargetDomainName = NT AUTHORITY TargetLogonId = 0x00000000001046e9
- LogonType = 9
- LogonProcessName = seclogo
- AuthenticationPackageName = Negotiate
- WorkstationName = LogonGuid = `{`00000000-0000-0000-0000-000000000000`}`
- TransmittedServices = - LmPackageName = - KeyLength = 0 ProcessId = 0x00000000000003b4
- ProcessName = C:/Windows/System32/svchost.exe IpAddress = ::1 IpPort = 0
Command: sekurlsa::pth /user:my-admin /domain:corp /ntlm:[nt hash] /run:cmd.exe
Comment: Succesful logon, TargetLogonId = 0x00000000001046e9
Time: 06:32:44
Event: 4672
Event content:
- SubjectUserSid = S-1-5-18 SubjectUserName = SYSTEM SubjectDomainName = NT AUTHORITY
- SubjectLogonId = 0x00000000001046e9
- PrivilegeList = SeCreateTokenPrivilege SeAssignPrimaryTokenPrivilege SeTcbPrivilege
SeSecurityPrivilege SeTakeOwnershipPrivilege SeLoadDriverPrivilege SeBackupPrivilege
SeRestorePrivilege SeDebugPrivilege SeAuditPrivilege SeSystemEnvironmentPrivilege
SeImpersonatePrivilege
Comment: Special privileges assigned to new logon, as above. LogonId = 0x00000000001046e9
Time: 06:32:55
Event: 4648
Event content:
- SubjectUserSid = S-1-5-18 SubjectUserName = SYSTEM SubjectDomainName = NT AUTHORITY
- SubjectLogonId = 0x00000000001046e9 LogonGuid = `{`00000000-0000-0000-0000-000000000000`}`
- TargetUserName = -------- TargetDomainName = ---- TargetLogonGuid =
`{`00000000-0000-0000-0000-000000000000`}`
- TargetServerName = admin-ws.corp.pass.thehash TargetInfo = admin-ws.corp.pass.thehash
- ProcessId = 0x0000000000000004 ProcessName =
- IpAddress = - IpPort = -
Command: psexec.exe \admin-ws cmd.exe
Comment: A logon was attempted using explicit credentials. This event is generated when a
process attempts to log on an account by explicitly specifying that accounts credentials.
This most commonly occurs in batch-type configurations such as scheduled tasks, or when
using the RUNAS command. SubjectLogonId = 0x00000000001046e9
Time: 06:32:55
Event: 4648
Event content:
- SubjectUserSid = S-1-5-18 SubjectUserName = SYSTEM SubjectDomainName = NT AUTHORITY
- SubjectLogonId = 0x00000000001046e9 LogonGuid = `{`00000000-0000-0000-0000-000000000000`}`
- TargetUserName = -------- TargetDomainName = ---- TargetLogonGuid =
`{`00000000-0000-0000-0000-000000000000`}`
- TargetServerName = admin-ws.corp.pass.thehash TargetInfo = admin-ws.corp.pass.thehash
ProcessId = 0x0000000000000998
- ProcessName = C:/goodies/PsExec.exe
- IpAddress = - IpPort = -
Comment: LogonId = 0x00000000001046e9
Time: 06:33:35
Event: 4648
Event content:
- SubjectUserSid = S-1-5-18 SubjectUserName = SYSTEM SubjectDomainName = NT AUTHORITY
- SubjectLogonId = 0x00000000001046e9 LogonGuid = `{`00000000-0000-0000-0000-000000000000`}`
- TargetUserName = -------- TargetDomainName = ---- TargetLogonGuid =
`{`00000000-0000-0000-0000-000000000000`}`
- TargetServerName = admin-ws.corp.pass.thehash TargetInfo = admin-ws.corp.pass.thehash
- ProcessId = 0x0000000000000004 ProcessName =
- IpAddress = - IpPort = -
Command: robocopy.exe c:goodiessch \admin-wsc$
Comment: A logon was attempted using explicit credentials. LogonId = 0x00000000001046e9
Time: 06:34:15
Event: 4648
Event content:
- SubjectUserSid = S-1-5-18 SubjectUserName = SYSTEM SubjectDomainName = NT AUTHORITY
- SubjectLogonId = 0x00000000001046e9 LogonGuid = `{`00000000-0000-0000-0000-000000000000`}`
- TargetUserName = -------- TargetDomainName = ---- TargetLogonGuid =
`{`00000000-0000-0000-0000-000000000000`}`
- TargetServerName = admin-ws.corp.pass.thehash TargetInfo = admin-ws.corp.pass.thehash
- ProcessId = 0x0000000000000004 ProcessName =
- IpAddress = - IpPort = -
Command: at.exe \admin-ws 08:00 c:schedule.bat
Comment: A logon was attempted using explicit credentials.LogonId = 0x00000000001046e9
```

**6.1.3 目标主机中的相关事件（admin-ws）**



```
Time: 06:32:55
Event: 4672
Event content:
- SubjectUserSid = S-1-5-21-2976932740-3244455291-537790045-1105
- SubjectUserName = my-admin
- SubjectDomainName = CORP SubjectLogonId = 0x00000000000f133c PrivilegeList =
SeSecurityPrivilege SeBackupPrivilege SeRestorePrivilege SeTakeOwnershipPrivilege
SeDebugPrivilege SeSystemEnvironmentPrivilege SeLoadDriverPrivilege
SeImpersonatePrivilege
Comment: Special privileges assigned to new logon.
Time: 06:32:55
Event: 4624
Event content:
- SubjectUserSid = S-1-0-0 SubjectUserName = - SubjectDomainName = - SubjectLogonId =
0x0000000000000000 TargetUserSid = S-1-5-21-2976932740-3244455291-537790045-1105
- TargetUserName = my-admin
- TargetDomainName = CORP
- TargetLogonId = 0x00000000000f133c
- LogonType = 3
- LogonProcessName = NtLmSsp
- AuthenticationPackageName = NTLM WorkstationName = USER-WS
- LogonGuid = `{`00000000-0000-0000-0000-000000000000`}` TransmittedServices = - LmPackageName =
NTLM V1 KeyLength = 128 ProcessId = 0x0000000000000000 ProcessName = - IpAddress =
192.168.89.101 IpPort = 49286
Command: psexec.exe \admin-ws cmd.exe
Comment: Succesful logon. TargetLogonId = 0x00000000000f133c
Time: 06:33:32
Event: 4634
Event content:
- TargetUserSid = S-1-5-21-2976932740-3244455291-537790045-1105
- TargetUserName = my-admin
- TargetDomainName = CORP
- TargetLogonId = 0x00000000000f133c
- LogonType = 3
Comment: TargetLogonId = 0x00000000000f133c
Time: 06:33:35
Event: 4672
Event content:
- SubjectUserSid = S-1-5-21-2976932740-3244455291-537790045-1105
- SubjectUserName = my-admin
- SubjectDomainName = CORP
- SubjectLogonId = 0x00000000000f2736
- PrivilegeList = SeSecurityPrivilege SeBackupPrivilege SeRestorePrivilege
SeTakeOwnershipPrivilege SeDebugPrivilege SeSystemEnvironmentPrivilege
SeLoadDriverPrivilege SeImpersonatePrivilege
Time: 06:33:35
Event: 4624
Event content:
- SubjectUserSid = S-1-0-0 SubjectUserName = - SubjectDomainName = - SubjectLogonId =
0x0000000000000000 TargetUserSid = S-1-5-21-2976932740-3244455291-537790045-1105
- TargetUserName = my-admin
- TargetDomainName = CORP
- TargetLogonId = 0x00000000000f2736
- LogonType = 3
- LogonProcessName = NtLmSsp
- AuthenticationPackageName = NTLM
- WorkstationName = USER-WS
- LogonGuid = `{`00000000-0000-0000-0000-000000000000`}` TransmittedServices = - LmPackageName =
NTLM V1 KeyLength = 128 ProcessId = 0x0000000000000000 ProcessName = -
- IpAddress = 192.168.89.101 IpPort = 49298
Command: robocopy.exe c:goodiessch \admin-wsc$
Time: 06:34:02
Event: 4634
Event content:
- TargetUserSid = S-1-5-21-2976932740-3244455291-537790045-1105
- TargetUserName = my-admin
- TargetDomainName = CORP
- TargetLogonId = 0x00000000000f2736
- LogonType = 3
Time: 06:34:15
Event: 4672
Event content:
- SubjectUserSid = S-1-5-21-2976932740-3244455291-537790045-1105
- SubjectUserName = my-admin SubjectDomainName = CORP
- SubjectLogonId = 0x00000000000f309b
- PrivilegeList = SeSecurityPrivilege SeBackupPrivilege SeRestorePrivilege
SeTakeOwnershipPrivilege SeDebugPrivilege SeSystemEnvironmentPrivilege
SeLoadDriverPrivilege SeImpersonatePrivilege LogonId = 0x00000000000f309b
Time: 06:34:15
Event: 4624
Event content:
- SubjectUserSid = S-1-0-0 SubjectUserName = - SubjectDomainName = - SubjectLogonId =
0x0000000000000000 TargetUserSid = S-1-5-21-2976932740-3244455291-537790045-1105
- TargetUserName = my-admin
- TargetDomainName = CORP
- TargetLogonId = 0x00000000000f309b
- LogonType = 3
- LogonProcessName = NtLmSsp
- AuthenticationPackageName = NTLM
- WorkstationName = USER-WS
- LogonGuid = `{`00000000-0000-0000-0000-000000000000`}` TransmittedServices = - LmPackageName =
NTLM V1 KeyLength = 128 ProcessId = 0x0000000000000000 ProcessName = -
- IpAddress = 192.168.89.101 IpPort = 49299
Command: at.exe \admin-ws 08:00 c:schedule.bat
Comment: LogonId = 0x00000000000f309b
Time: 06:34:26
Event: 4634
Event content:
- TargetUserSid = S-1-5-21-2976932740-3244455291-537790045-1105
- TargetUserName = my-admin
- TargetDomainName = CORP
- TargetLogonId = 0x00000000000f309b
- LogonType = 3
Comment: LogonId = 0x00000000000f309b
```

**6.2 Kerberos认证和PtT事件**

**6.2.1 域控中的相关事件**

我们可以在域控中看到4769事件：来自于user-ws主机的IP地址（192.168.86.101）请求了Kerberos服务票据，以便访问admin-ws主机。

需要注意的是，我们在域控中没有找到4768事件（Kerberos TGT请求事件），因为攻击者已经事先窃取了票据，然后重新注入该票据发起攻击。



```
Time: 14:11:12
Event: 4769
Event content:
- TargetUserName = myadmin@corp
- TargetDomainName = corp
- ServiceName = ADMIN-WS$
- ServiceSid = S-1-5-21-2976932740-3244455291-537790045-1107
- TicketOptions = 0x40810000
- TicketEncryptionType = 0x00000012
- IpAddress = ::ffff:192.168.89.101 IpPort = 49407
- Status = 0x00000000
- LogonGuid = `{`B757831E-D810-CDCC-C1C2-804BB3A2FB2C`}`
- TransmittedServices = -
Command: net use \admin-ws
```

**6.2.2 目标主机（admin-ws）中的事件**

我们在目标主机中可以找到与账户成功登陆有关的两个事件（4624事件）。与域控上的情况类似，这些事件都与黄金票据攻击无关。



```
Time: 14:11:12
Event: 4624
Event content:
- SubjectUserSid = S-1-0-0 SubjectUserName = - SubjectDomainName = - SubjectLogonId =
0x0000000000000000
- TargetUserSid = S-1-5-21-2976932740-3244455291-537790045-500 TargetUserName = myadmin
TargetDomainName = corp
- TargetLogonId = 0x000000000051f916
- LogonType = 3 LogonProcessName = Kerberos AuthenticationPackageName = Kerberos
- WorkstationName =
- LogonGuid = `{`A0706C8D-9BC6-F4D5-1226-FA2A48BB58D9`}` TransmittedServices = - LmPackageName = -
KeyLength = 0 ProcessId = 0x0000000000000000 ProcessName = -
- IpAddress = 192.168.89.101 IpPort = 49406
Command: net use \admin-ws
Time: 14:11:12
Event: 4672
Event content:
- SubjectUserSid = S-1-5-21-2976932740-3244455291-537790045-500 SubjectUserName = myadmin
- SubjectDomainName =
- SubjectLogonId = 0x000000000051f916
- PrivilegeList = SeSecurityPrivilege SeBackupPrivilege SeRestorePrivilege
SeTakeOwnershipPrivilege SeDebugPrivilege SeSystemEnvironmentPrivilege SeLoadDriverPrivilege
SeImpersonatePrivilege
Command: net use \admin-ws
Time: 14:11:39
Event: 4624
Event content:
- SubjectUserSid = S-1-0-0 SubjectUserName = - SubjectDomainName = - SubjectLogonId =
0x0000000000000000
- TargetUserSid = S-1-5-21-2976932740-3244455291-537790045-500 TargetUserName = myadmin
TargetDomainName = corp
- TargetLogonId = 0x00000000005204ad
- LogonType = 3 LogonProcessName = Kerberos AuthenticationPackageName = Kerberos
- WorkstationName =
- LogonGuid = `{`B504E2E8-3007-1C03-F480-011559C08D34`}` TransmittedServices = - LmPackageName = -
KeyLength = 0 ProcessId = 0x0000000000000000 ProcessName = -
- IpAddress = 192.168.89.101 IpPort = 49409
Command: psexec.exe \admin-ws cmd.exe
Time: 14:11:39
Event: 4672
Event content:
- SubjectUserSid = S-1-5-21-2976932740-3244455291-537790045-500 SubjectUserName = myadmin
SubjectDomainName =
- SubjectLogonId = 0x00000000005204ad
- PrivilegeList = SeSecurityPrivilege SeBackupPrivilege SeRestorePrivilege
SeTakeOwnershipPrivilege SeDebugPrivilege SeSystemEnvironmentPrivilege SeLoadDriverPrivilege
SeImpersonatePrivilege
Command: psexec.exe \admin-ws cmd.exe
```

**6.3 附录D-Windows安全（Security）事件**

这部分主要介绍了本文中所提到的安全事件细节，参考了微软的官方定义[5][6]。

4624事件：成功登录帐户。



```
Subject:
Security ID: %1
Account Name: %2
Account Domain: %3
Logon ID: %4
Logon Type: %9
New Logon:
Security ID: %5
Account Name: %6
Account Domain: %7
Logon ID: %8
Logon GUID: %13
Process Information:
Process ID: %17
Process Name: %18
Network Information:
Workstation Name: %12
Source Network Address: %19
Source Port: %20
Detailed Authentication Information:
Logon Process: %10
Authentication Package: %11
Transited Services: %14
Package Name (NTLM only): %15
Key Length: %16
This event is generated when a logon session is created. It is generated on the computer that was accessed.
The subject fields indicate the account on the local system which requested the logon. This is most commonly a service such as the Server service, or a local process such as Winlogon.exe
or Services.exe.
The logon type field indicates the kind of logon that occurred. The most common types are 2 (interactive) and 3 (network).
The New Logon fields indicate the account for whom the new logon was created, i.e. the account that was logged on.
The network fields indicate where a remote logon request originated. Workstation name is not always available and may be left blank in some cases.
The authentication information fields provide detailed information about this specific logon request.
- Logon GUID is a unique identifier that can be used to correlate this event with a KDC event.
- Transited services indicate which intermediate services have participated in this logon request.
- Package name indicates which sub-protocol was used among the NTLM protocols.
- Key length indicates the length of the generated session key. This will be 0 if no session key was requested.
```

4625事件：帐户登录失败。



```
Subject:
Security ID: %1
Account Name: %2
Account Domain: %3
Logon ID: %4
Logon Type: %11
Account For Which Logon Failed:
Security ID: %5
Account Name: %6
Account Domain: %7
Failure Information:
Failure Reason: %9
Status: %8
Sub Status: %10
Process Information:
Caller Process ID: %18
Caller Process Name: %19
Network Information:
Workstation Name: %14
Source Network Address: %20
Source Port: %21
Detailed Authentication Information:
Logon Process: %12
Authentication Package: %13
Transited Services: %15
Package Name (NTLM only): %16
Key Length: %17
This event is generated when a logon request fails. It is generated on the computer where access was attempted.
The Subject fields indicate the account on the local system which requested the logon. This is most commonly a service such as the Server service, or a local process such as Winlogon.exe
or Services.exe.
The Logon Type field indicates the kind of logon that was requested. The most common types are 2 (interactive) and 3 (network).
The Process Information fields indicate which account and process on the system requested the logon.
The Network Information fields indicate where a remote logon request originated. Workstation name is not always available and may be left blank in some cases.
The authentication information fields provide detailed information about this specific logon request.
- Transited services indicate which intermediate services have participated in this logon request.
- Package name indicates which sub-protocol was used among the NTLM protocols.
- Key length indicates the length of the generated session key. This will be 0 if no session key was requested.
```

4634事件：帐户被注销。



```
Subject:
Security ID: %1
Account Name: %2
Account Domain: %3
Logon ID: %4
Logon Type: %5
This event is generated when a logon session is destroyed. It may be positively correlated with a logon event using the Logon ID value. Logon IDs are only unique between reboots on the same computer.
Event ID: 4647
User initiated logoff.
Subject:
Security ID: %1
Account Name: %2
Account Domain: %3
Logon ID: %4
This event is generated when a logoff is initiated but the token reference count is not zero and the logon session cannot be destroyed. No further user-initiated activity can occur. This event can be interpreted as a logoff event.
```

4648事件：试图使用显式凭据登录。



```
Subject:
Security ID: %1
Account Name: %2
Account Domain: %3
Logon ID: %4
Logon GUID: %5
Account Whose Credentials Were Used:
Account Name: %6
Account Domain: %7
Logon GUID: %8
Target Server:
Target Server Name: %9
Additional Information: %10
Process Information:
Process ID: %11
Process Name: %12
Network Information:
Network Address: %13
Port: %14
This event is generated when a process attempts to log on an account by explicitly specifying that accounts credentials. This most commonly occurs in batch-type configurations such as scheduled tasks, or when using the RUNAS command.
```

4672事件：分配给新的登录特权。



```
Subject:
Security ID: %1
Account Name: %2
Account Domain: %3
Logon ID: %4
Privileges: %5
```

4768事件：Kerberos 身份验证票证 (TGT) 请求。



```
Account Information:
Account Name: %1
Supplied Realm Name: %2
User ID: %3
Service Information:
Service Name: %4
Service ID: %5
Network Information:
Client Address: %10
Client Port: %11
Additional Information:
Ticket Options: %6
Result Code: %7
Ticket Encryption Type: %8
Pre-Authentication Type: %9
Certificate Information:
Certificate Issuer Name: %12
Certificate Serial Number: %13
Certificate Thumbprint: %14
Certificate information is only provided if a certificate was used for pre-authentication.
Pre-authentication types, ticket options, encryption types and result codes are defined in RFC 4120.
```

4769事件：Kerberos 服务票证请求。



```
Account Information:
Account Name: %1
Account Domain: %2
Logon GUID: %10
Service Information:
Service Name: %3
Service ID: %4
Network Information:
Client Address: %7
Client Port: %8
Additional Information:
Ticket Options: %5
Ticket Encryption Type: %6
Failure Code: %9
Transited Services: %11
This event is generated every time access is requested to a resource such as a computer or a Windows service. The service name indicates the resource to which access was requested.
This event can be correlated with Windows logon events by comparing the Logon GUID fields in each event. The logon event occurs on the machine that was accessed, which is often a different machine than the domain controller which issued the service ticket.
Ticket options, encryption types, and failure codes are defined in RFC 4120.
```

4776事件：域控试图验证帐户凭据



```
Authentication Package: %1
Logon Account: %2
Source Workstation: %3
Error Code: %4
```
