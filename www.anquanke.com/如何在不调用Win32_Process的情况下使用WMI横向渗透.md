> 原文链接: https://www.anquanke.com//post/id/144671 


# 如何在不调用Win32_Process的情况下使用WMI横向渗透


                                阅读量   
                                **105905**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://www.cybereason.com
                                <br>原文地址：[https://www.cybereason.com/blog/wmi-lateral-movement-win32](https://www.cybereason.com/blog/wmi-lateral-movement-win32)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t019df1d0d5095b6f06.jpg)](https://p0.ssl.qhimg.com/t019df1d0d5095b6f06.jpg)

## 引言

对攻击者来说，如果需要对某个网络中的多台计算机进行攻击，那么横向移动是至关重要的一个步骤。假如攻击者已经拥有正确的证书，他们往往会滥用允许远程执行代码的现有机制，从而实现横向移动。虽然这些机制大多数都被合法使用，但仍然有许多环境会对它们进行监控，以防止其被非法使用。如果使用了很少在特定环境中使用的向量，远程执行代码可能会被检测为异常，并标记为恶意代码。例如，在网络的远程服务创建过程中使用了PSExec工具，这就是非常少见的，从而可能引发告警。<br>
一个更专业的攻击者更愿意使用远程执行技术，随着这种技术不断发展，其过程越来越趋近于正常合法的行为，此外，这些技术还滥用了容易被防护方遗漏掉得的执行通道。基于此，如果能够改进出一套可用的横向移动技术，就可以让攻击者在不被检测到的前提下实现攻击。<br>
在本文中，我们主要讲解由Cybereason发现的通过对WMI（Windows Management Infrastructure）滥用实现的一种新型横向移动技术（ [https://conference.hitb.org/hitbsecconf2018ams/materials/D2T1%20-%20Philip%20Tsukerman%20-%20Expanding%20Your%20WMI%20Lateral%20Movement%20Arsenal.pdf](https://conference.hitb.org/hitbsecconf2018ams/materials/D2T1%20-%20Philip%20Tsukerman%20-%20Expanding%20Your%20WMI%20Lateral%20Movement%20Arsenal.pdf) ）。另外，我们也会对已经公开披露的横向移动方法进行详细分析。由于这些新型技术目前还没有普遍流行，所以许多安全工具无法对它们进行检测。然而，Cybereason编写了一个工具，这是该技术的一个概念验证（PoC），可以具体展现攻击者借助这种攻击方式具体都可以做什么。PowerShell脚本请参考： [https://github.com/Cybereason/Invoke-WMILM](https://github.com/Cybereason/Invoke-WMILM) 。<br>
如果大家想了解更多关于哪些合法功能正在被滥用以进行横向移动的内容，请阅读这篇文章（ [https://www.cybereason.com/blog/dcom-lateral-movement-techniques](https://www.cybereason.com/blog/dcom-lateral-movement-techniques) ），其中讨论了攻击者如何使用分布式组件对象模型（DCOM）。



## 关于WMI的简要介绍

WMI是Windows操作系统上WBEM和CIM标准的实现，允许用户、管理员和开发人员（包括攻击者）在操作系统中对各种托管组件进行遍历、操作和交互。具体而言，WMI提供了一个抽象的、统一的面向对象模型，从而不再需要直接与许多不相关的API进行交互，当然也无需再研究这些不相关API的文档。<br>[![](https://www.cybereason.com/hs-fs/hubfs/philipwin.png?t=1525984608115&amp;width=368&amp;height=430&amp;name=philipwin.png)](https://www.cybereason.com/hs-fs/hubfs/philipwin.png?t=1525984608115&amp;width=368&amp;height=430&amp;name=philipwin.png)<br>
WMI包含表示元素的类，例如系统注册表、进程、线程和硬件组件。<br>
我们可以通过发出WQL查询来列举出由类表示的组件实例，这些查询是使用WQL（类似SQL）语言编写的，也可以通过诸如PowerShell CIM / WMI cmdlet的抽象。此外，也可以在类和实例上调用方法，从而使用WMI接口来操纵底层的托管组件。<br>
WMI的一个重要特性是能够使用DCOM或WinRM协议与远程机器的WMI模块进行交互。这样一来，就使得攻击者可以远程操作主机上的WMI类，而无需事先运行任何代码。



## WMI的主要组件

WMI由三个主要组件组成：<br>
1、WMI服务（winmgmt）充当客户端与WMI模型本身之间的中间人，负责处理来自客户端进程的所有请求（方法调用、查询等）。虽然其自身不能处理大部分请求，但它能够将请求转发给其他组件，并将其响应转发回客户端。<br>
2、WMI提供程序（WMI Providers）是用于实现代码实现类、实例和方法。提供程序大多是作为进程内COM对象来实现的。<br>
3、WMI存储库是模型的中央存储区域，其中包含类定义和需要持久化的对象实例（与提供程序动态生成的实例相对）。<br>
在了解WMI主要的组件之后，我们来考虑经典WMI横向移动技术的场景。当一个本地或远程客户端试图调用Win32_Process的Create方法时，会向WMI服务发送这个行为的请求，然后查询存储库，确定其提供程序为CIMWin32。然后，WMI服务将请求转发给提供程序，该提供程序创建一个新进程并将表示该进程的Win32_Process实例返回给该服务，并将该实例发送回客户端。如果想了解更多关于WMI安全性的内容，建议阅读这篇文章： [https://www.fireeye.com/content/dam/fireeye-www/global/en/current-threats/pdfs/wp-windows-management-instrumentation.pdf](https://www.fireeye.com/content/dam/fireeye-www/global/en/current-threats/pdfs/wp-windows-management-instrumentation.pdf) 。<br>
由于这种横向移动的方法是非常经典的，所以目前很多安全产品都会对这种方式进行检测。因此，攻击者也在基于这种最经典的技术不断改进，研究出其他利用WMI进行横向移动的方法。



## WMI横向移动的其他方案

### <a class="reference-link" name="%E6%B4%BE%E7%94%9F%E7%B1%BB"></a>派生类

尽管从严格意义上来说，这不是一种新的横向移动方法，但这种技术不需要攻击者与常常会被监控的Win32_Process::Create方法直接进行交互。攻击者可以远程创建一个新类，从已有的类（例如Win32_Process）继承，并调用新类中的方法（或者创建实例），而不直接调用可能会引起怀疑的方法，具体如下所述：<br>
1、创建Win32_Process的子类Win32_NotEvilAtAll，该过程可以通过WMI远程进行；<br>
2、新类继承父类的所有方法；<br>
3、调用新定义类中的“Create”方法。<br>
下图是我们编写的Invoke-WmiLm脚本中的部分内容，我们使用Derive和Put方法，在远程主机上创建了Win32_Process的子类，并调用了新定义类的Create方法。<br>[![](https://www.cybereason.com/hs-fs/hubfs/excerptfrom.png?t=1525984608115&amp;width=805&amp;height=167&amp;name=excerptfrom.png)](https://www.cybereason.com/hs-fs/hubfs/excerptfrom.png?t=1525984608115&amp;width=805&amp;height=167&amp;name=excerptfrom.png)<br>
现在，让我们看看WMI-Activity ETW提供程序的事件，初步看来我们已经避免了直接使用Win32_Process：<br>[![](https://www.cybereason.com/hs-fs/hubfs/notevil.png?t=1525984608115&amp;width=821&amp;height=106&amp;name=notevil.png)](https://www.cybereason.com/hs-fs/hubfs/notevil.png?t=1525984608115&amp;width=821&amp;height=106&amp;name=notevil.png)<br>
实际上，事件11的所有实例都体现了向WMI服务发出的请求，但其中并没有Win32_Process类的痕迹。我们在这里看到了希望，但经过仔细观察，我们发现这种规避方法还存在不完美之处：<br>[![](https://www.cybereason.com/hs-fs/hubfs/notevil2.png?t=1525984608115&amp;width=884&amp;height=81&amp;name=notevil2.png)](https://www.cybereason.com/hs-fs/hubfs/notevil2.png?t=1525984608115&amp;width=884&amp;height=81&amp;name=notevil2.png)<br>
为什么在这里仍然会显示Win32_Process::Create呢？<br>
其原因在于，尽管我们用相同的“Create”方法创建了一个新类，但我们实际上没有向目标主机引入任何新代码。这也就意味着该方法会在相同提供程序的环境中执行。WMI-Activity提供程序的事件12体现了WMI服务与WMI提供程序之间的通信，并且展示了谁是真正实现了方法执行请求的提供程序。<br>
其中，有一种非常不一样的检测方法，就是WMI自检。WMI提供了一个全面的事件管理系统，同时也有一些非常有用的事件来对自己实现监控。在这样的事件中，会描述主机上的所有WMI方法调用。<br>[![](https://www.cybereason.com/hs-fs/hubfs/wmi.png?t=1525984608115&amp;width=775&amp;height=424&amp;name=wmi.png)](https://www.cybereason.com/hs-fs/hubfs/wmi.png?t=1525984608115&amp;width=775&amp;height=424&amp;name=wmi.png)<br>
从上图中可以看出，MSFT_WmiProvider_ExecMethodAsyncEvent_Pre并不描述客户端请求的方法，而是再次描述了提供程序实现的真实方法，我们采用的逃避技术并没有对其奏效。<br>
尽管这种技术并不像我们所希望的那样，能实现对WMI方法调用的混淆，但该方法仍然适用于不需要使用方法（例如事件订阅）的情况下，这样在所有事件中显示的就是派生类的名称，而不是原始名称。<br>
另外，我们还尝试了“类克隆”的方式，通过滥用WMI类的层次结构来逃避被记录。该方法需要选定一个目标类，并且定义了一个新的目标类，与目标共享所有成员和层次结构。根据我们的推测，这种方法的逃避监测效果更好，因为我们的新类并不是目标的子类。然而，在WMI服务中，我们无法找到克隆类中定义的方法的实现，因此该方案就变得不太可行。



## WMI修改经典技术

如果我们能使用WMI执行常见的横向移动任务（例如替换PSEXEC），那么就会改变攻击者的行为，从而足以逃避相关的监控。下面是该技术的几个示例。

### <a class="reference-link" name="%E6%9C%8D%E5%8A%A1%E5%88%9B%E5%BB%BA"></a>服务创建

远程服务创建（通常使用PSEXEC工具）大概是Windows环境中最常见的横向移动方法，该方法也可以在WMI中实现。<br>
Win32_Service类表示一台主机上的单个服务，并且公开了Windows服务管理器（sc.exe工具）几乎所有的功能。<br>
我们快速了解一下Win32_Service方法，该方法让类可以轻松地在目标主机上对服务进行操作。这样就足以实现攻击者通常借助服务进行横向移动的全过程：创建、启动、停止、删除。<br>
Win32_Service并不是唯一能够执行这些操作的WMI类，还有以下几个类可以替代使用：<br>
Win32_Service<br>
Win32_BaseService<br>
Win32_TerminalService<br>
Win32_SystemDriver<br>
当我们使用PSEXEC、sc.exe或其他常用的远程服务管理工具时，是通过DCERPC借助于MS-SCMR协议进行的通信。即使在该协议中使用了最强的加密级别，也还是可以通过对网络流量的监控来确定出执行了哪些类型的操作（例如服务创建、服务启动等）。<br>[![](https://www.cybereason.com/hs-fs/hubfs/wiresharkcapture.png?t=1525984608115&amp;width=756&amp;height=232&amp;name=wiresharkcapture.png)](https://www.cybereason.com/hs-fs/hubfs/wiresharkcapture.png?t=1525984608115&amp;width=756&amp;height=232&amp;name=wiresharkcapture.png)<br>
另一方面，如果使用WMI进行相同的动作，其监控结果完全不同：<br>[![](https://www.cybereason.com/hs-fs/hubfs/different%20WMI.png?t=1525984608115&amp;width=772&amp;height=324&amp;name=different%20WMI.png)](https://www.cybereason.com/hs-fs/hubfs/different%20WMI.png?t=1525984608115&amp;width=772&amp;height=324&amp;name=different%20WMI.png)<br>
尽管仍然基于DCERPC，但所有WMI DCOM方法调用都是通过一个接口完成的，并且在与“数据包隐私”级加密结合使用时，只能监控到某些WMI方法被调用。当通过WINRM协议执行时，WMI流量看起来像是HTTP流量，并且与经过SVCCTL接口时完全不同。这就意味着，WMI技术有效逃避了所有通过网络流量签名来检测横向移动的防范方式。

### <a class="reference-link" name="%E6%97%A7%E7%89%88%E6%9C%AC%E7%9A%84%E8%AE%A1%E5%88%92%E4%BB%BB%E5%8A%A1%E5%88%9B%E5%BB%BA"></a>旧版本的计划任务创建

WMI还提供了一种与旧版本的（at.exe）Windows任务调度机制进行交互的方法。具体是通过Win32_ScheduledJob类完成的。<br>
这个类允许创建、删除和枚举（通过枚举类实例，而不是使用专门的方法）计划任务。而at.exe实用程序以及这个类的功能在Windows 8及更高版本中都已不再使用。无法强制执行某项任务的问题在这里迎刃而解（就像使用经典技术一样），我们只需将任务安排在注册后几秒钟运行即可。

### <a class="reference-link" name="%E6%96%B0%E7%89%88%E6%9C%AC%E7%9A%84%E8%AE%A1%E5%88%92%E4%BB%BB%E5%8A%A1%E5%88%9B%E5%BB%BA"></a>新版本的计划任务创建

我们可以利用的另一种机制就是新版本的Windows任务调度程序（Windows Task Scheduler），通常使用schtasks.exe实用程序进行交互。用这种方式创建的计划任务由ScheduledTaskProv提供程序下的PS_ScheduledTask及其相关类表示。<br>
PS_ScheduledTask类允许客户端使用自定义操作创建、删除和运行任何的计划任务。实际上，在Windows 8及更高版本系统中，允许使用计划任务命令行，并可以在后台使用这些WMI类。这样一来，攻击者可以滥用这些命令，以逃避各种IDS检测。需要注意的是，尽管新的任务调度程序在Windows 7中就已经出现，但ScheduledTaskProv提供程序只适用于Windows 8系统以上。

### <a class="reference-link" name="%E6%BB%A5%E7%94%A8Windows%20Installer"></a>滥用Windows Installer

Windows Installer提供程序公开了一个名为Win32_Product的类，该类表示由Windows Installer（msiexec）安装的应用程序。这个类可能允许攻击者在目标计算机上运行恶意msi包。<br>
Win32_Product中的Install方法允许从路径或URL安装msi包。并且，很可能其中的Admin和Upgrade方法也同样可以。攻击者可以使用Metasploit制作包含恶意Payload的软件包：<br>[![](https://www.cybereason.com/hs-fs/hubfs/INSTALL%20MSI%20PACKAGE.png?t=1525984608115&amp;width=789&amp;height=222&amp;name=INSTALL%20MSI%20PACKAGE.png)](https://www.cybereason.com/hs-fs/hubfs/INSTALL%20MSI%20PACKAGE.png?t=1525984608115&amp;width=789&amp;height=222&amp;name=INSTALL%20MSI%20PACKAGE.png)<br>
虽然Metasploit允许将可执行文件打包为msi文件，但包格式还允许嵌入vbscript和jscript有效内容，使得msi成为一个相当通用的有效载荷容器。<br>
我们尝试了通过“msiexec /y”命令，想要从命令行注册一个dll文件，希望借此实现对Win32_Product的滥用，但这次尝试并不成功，似乎这种方法不适用于WMI。此外，我们还尝试劫持注册表中的uninstaller命令行字段，然后使用Win32_Product中的Uninstall方法运行这些命令，但结果也宣告失败。<br>[![](https://www.cybereason.com/hs-fs/hubfs/UNINSTALL%20STRING.png?t=1525984608115&amp;width=785&amp;height=164&amp;name=UNINSTALL%20STRING.png)](https://www.cybereason.com/hs-fs/hubfs/UNINSTALL%20STRING.png?t=1525984608115&amp;width=785&amp;height=164&amp;name=UNINSTALL%20STRING.png)<br>
将UninstallString值更改为任意命令行并调用Uninstall方法，同样也不起作用。

### <a class="reference-link" name="%E6%81%B6%E6%84%8FWMI%E6%8F%90%E4%BE%9B%E7%A8%8B%E5%BA%8F%E5%8A%A0%E8%BD%BD"></a>恶意WMI提供程序加载

如上所述，大多数类实例和方法都是在WMI提供程序中实现的。这意味着，可以通过加载自定义提供程序来实现代码执行。在Alexander Leary最近的一次演讲中，他讲解了一种在远程计算机上注册WMI提供程序的方法，该方法仅使用WMI函数，无需事先运行任何命令行。这种技术的缺点之一是需要真正实现，并且需要将真正（恶意）WMI提供程序DLL传到目标主机上。在本文中，我们不重点关注成功用作WMI提供程序的代码，只关注对其的加载过程。下面是将任意命令行作为WMI提供程序运行所需的步骤：<br>
首先，创建一个COM对象。WMI提供程序大多是作为进程内COM对象来实现的，但是我们现在想运行一个任意命令行，所以要编写一个进程外COM对象并注册，将其作为我们的基础提供程序。<br>
接下来，我们需要对提供程序本身进行注册。为此，需要在远程主机上创建一个用于注册WMI提供程序的<strong>Win32Provider类的实例。<br>[![](https://www.cybereason.com/hs-fs/hubfs/WIN32PROVIDERCLASS.png?t=1525984608115&amp;width=757&amp;height=425&amp;name=WIN32PROVIDERCLASS.png)](https://www.cybereason.com/hs-fs/hubfs/WIN32PROVIDERCLASS.png?t=1525984608115&amp;width=757&amp;height=425&amp;name=WIN32PROVIDERCLASS.png)<br>
在我们想要创建的</strong>Win32Provider实例中，有三个重要的字段：<br>
1、Name，提供程序的可读名称，这将允许我们后续对其进行引用；<br>
2、CLSID，我们新创建的COM对象的类ID；<br>
3、HostingModel，此字段表示如何加载COM对象。其中，“NetworkServiceHost”表示将COM对象作为库加载到“Network Service”用户下的特殊主进程中；“LocalSystemHost”表示将作为库加载到在System用户下的主进程中运行；“SelfHost”表示将尝试在System用户下作为独立的可执行文件加载。<br>
在这里，由于我们想要执行任意命令行，所以希望将提供程序作为可执行文件运行。<br>
通常情况下，提供程序都是当其实现的某个类和方法被调用或查询时，按需进行加载的。方法和实例提供程序的注册是通过**MethodProviderRegistration和**InstanceProviderRegistration类完成的。但我们的任意可执行文件显然不能实现这样的功能。幸运的是，MSFT_Providers类（用于列举已加载的WMI提供程序）有一个名为“Load”的方法，它允许我们加载任何WMI提供程序，不管是否真正需要。<br>
此外，当操作系统在命令运行后第一次对我们的COM对象实际上是否实现WMI提供程序进行检查时，似乎允许我们执行明显假冒的提供程序。在这里，需要注意一点，如果使用SelfHost主机模型注册WMI提供程序，会向事件日志中写入警报，其描述为“创建敏感提供程序”，其原因在于它使用了System权限运行。该日志写入可以通过使用NetworkServiceHostOrSelfHost模型来避免，该过程首先会尝试将提供程序加载为一个库（从而可以跳过注册过程），并且当加载失败时（因为实际上并没有要加载的库），尝试将提供程序作为可执行文件加载，而在其中就包括我们提供的命令行。<br>
回顾一下，我们可以使用以下步骤，将恶意命令行加载为WMI提供程序：<br>
1、在HKLM/SOFTWARE/Classes/CLSID/`{`SOMEGUID`}`下创建一个新密钥（注册表操作可以通过StdRegProv WMI提供程序完成）。<br>
2、添加一个LocalServer32的子项，其中包含任何你想运行的命令行的“默认”值（例如一些不错的PowerShell编码命令）。<br>
3、创建__Win32Provider类的新实例，将我们的CLSID作为CLSID字段，并将NetworkServiceHostOrSelfHost作为HostingModel。<br>
4、使用我们新创建的提供程序的名称调用MSFT_Providers类的Load方法<br>
5、成功实现不被监测到的远程执行。



## 检测方式与结论

虽然这些技术相对未知，并且通常不会被大多数安全产品检测到，但Windows提供了有关WMI功能的充分信息，可以实现上述每种技术的检测。 WMI-Activity ETW提供程序和WMI事件处理系统都能够深入了解所有WMI方法调用及实例创建和查询，这些信息足以确定是否调用了任何敏感的WMI功能。<br>
尽管我们讨论的这些技术，实际上都有相应的记录机制，但由于相关事件发生的频率较低，监控机制没有办法详细记录其中的每个操作。为了防止采用这种攻击方式的横向移动，我们建议防护者综合考虑上述所有技术，制定防范策略，同时建议防护者深入了解WMI，以此来防范攻击者利用上述技术以及其他许多滥用这一特性的技术。
