> 原文链接: https://www.anquanke.com//post/id/190307 


# 基于ATT&amp;CK框架的红蓝对抗，有效提升检测能力


                                阅读量   
                                **957509**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01ff9bb506f6fc7203.jpg)](https://p0.ssl.qhimg.com/t01ff9bb506f6fc7203.jpg)



在继前面两篇有关MITRE ATT&amp;CK的文章——《一文看懂ATT&amp;CK框架以及使用场景实例》和《细述MITRE ATT&amp;CK框架的实施和使用方式》之后，相信大家对于ATT&amp;CK框架有了一个整体的了解。今天，我们将主要介绍如何基于ATT&amp;CK框架来制定红蓝对抗方案，提升企业检测能力。

在此之前，先让我们通过下文一个真实的攻击场景来了解一下攻击者是如何进行攻击的。



## 一个真实的攻击场景

攻击者首先是对其最近感兴趣的一个事件发送了一个钓鱼邮件。攻击载荷（payload）是一个.zip文件，其中包含了一个诱饵PDF文件和一个恶意可执行文件，该恶意文件使用系统上已经安装的Acrobat Reader来进行伪装。

运行时，可执行文件将下载第二阶段使用的远程访问工具（RAT）有效负荷，让远程操作员可以访问受害计算机，并可让远程操作员在网络中获得一个初始访问点。然后，攻击者会生成用于“命令控制”的新域名，并通过定期更改自己的网络用户名，将这些域发送到受感染网络上的远程访问工具（RAT）。用于“命令控制”的域和IP地址是临时的，并且攻击者每隔几天就会对此进行更改。攻击者通过安装Windows服务——其名称很容易被计算机所有者认为是合法的系统服务名称，从而看似合法地保留在受害计算机上。在部署该恶意软件之前，攻击者可能已经在各种防病毒（AV）产品上进行了测试，以确保它与任何现有或已知的恶意软件签名都不匹配。

为了与受害主机进行交互，攻击者使用RAT启动Windows命令提示符，例如cmd.exe。然后，攻击者使用受感染计算机上已有的工具来了解有关受害者系统和周围网络的更多信息，以便提高其在其它系统上的访问级别，并朝着实现其目标进一步迈进。

更具体地说，攻击者使用内置的Windows工具或合法的第三方管理工具来发现内部主机和网络资源，并发现诸如帐户、权限组、进程、服务、网络配置和周围的网络资源之类的信息。然后，远程操作员可以使用Invoke-Mimikatz来批量捕获缓存的身份验证凭据。在收集到足够的信息之后，攻击者可能会进行横向移动，从一台计算机移动到另一台计算机，这通常可以使用映射的Windows管理员共享和远程Windows（服务器消息块[SMB]）文件副本以及远程计划任务来实现。随着访问权限的增加，攻击者会在网络中找到感兴趣的文档。然后，攻击者会将这些文档存储在一个中央位置，使用RAR等程序通过远程命令行shell对文件进行压缩和加密，最后，通过HTTP会话，将文件从受害者主机中渗出，然后在其方便使用的远程计算机上分析和使用这些信息。



## 传统检测方案无法解决上述攻击场景

现有的检测方案难以检测到上述情景中所介绍的APT攻击。大多数防病毒应用程序可能无法可靠地检测到自定义工具，因为攻击者在使用这些工具之前，已经对其进行了测试，甚至可能包含一些混淆技术，以便绕开其它类型的恶意软件检测。此外，恶意远程操作员还能够在他们所攻击的系统上使用合法功能，逃避检测。而且许多检测工具无法收集到足够的数据，来发现此类恶意使用合法系统的行为。

当前其它的网络安全方法，例如威胁情报信息共享，可能对于检测攻击者基础设施也无济于事，因为攻击者指标可能变化太快。典型的网络流量检查也将于事无补，因为APT的流量（例如上述示例中所述的流量）已通过有效的SSL加密。SSL拦截可能有用，但是要将恶意行为从善意网络行为中区分出来，实在太困难了。



## 基于ATT&amp;CK的红蓝对抗是如何提升检测能力的？

自2012年MITRE进行网络竞赛以来，MITRE主要通过研究对抗行为、构建传感器来获取数据以及分析数据来检测对抗行为。该过程包含三个重要角色：“白队”、“红队”和“蓝队”，如下所示：

白队——开发用于测试防御的威胁场景。白队与红队和蓝队合作，解决网络竞赛期间出现的问题，并确保达到测试目标。白队与网络管理员对接，确保维护网络资产。

红队——扮演网络竞赛中的攻击者。执行计划好的威胁场景，重点是对抗行为模拟，并根据需要与白队进行对接。在网络竞赛中出现的任何系统或网络漏洞都将报告给白队。

蓝队——在网络竞赛中担任网络防御者，通过分析来检测红队的活动。他们也被认为是一支狩猎队。

基于ATT&amp;CK框架，开发网络对抗赛主要包含以下七个步骤：

下面，我们将对这七个步骤进行详细介绍。

[![](https://p1.ssl.qhimg.com/t019186dfc7b2cd005f.png)](https://p1.ssl.qhimg.com/t019186dfc7b2cd005f.png)



## 开发网络对抗赛的七个步骤

### 第1步：确定目标

第一步是确定要检测的对抗行为的目标和优先级。在决定优先检测哪些对抗行为时，需要考虑以下几个因素：

1.哪种行为最常见？

优先检测攻击者最常使用的TTP，并解决最常见的、最常遇到的威胁技术，这会对组织机构的安全态势产生最广泛的影响。拥有强大的威胁情报能力后，组织机构就可以了解需要关注哪些ATT&amp;CK战术和技术。

2.哪种行为产生的负面影响最大？

组织机构必须考虑哪些TTP会对组织机构产生最大的潜在不利影响。这些影响可能包括物理破坏、信息丢失、系统受损或其它负面后果。

3.容易获得哪些行为的相关数据？

与那些需要开发和部署新传感器或数据源的行为相比，对于已拥有必要数据的行为进行分析要容易得多。

4.哪种行为最有可能表示是恶意行为？

只是由攻击者产生的行为而不是合法用户产生的行为，对于防御者来说用处最大，因为这些数据产生误报的可能性较小。

### 第2步：收集数据

在创建分析方案时，组织机构必须确定、收集和存储制定分析方案所需的数据。为了确定分析人员需要收集哪些数据来制定分析方案，首先要了解现有传感器和日志记录机制已经收集了哪些数据。在某些情况下，这些数据可能满足给定分析的数据要求。但是，在许多情况下，可能需要修改现有传感器和工具的设置或规则，以便收集所需的数据。在其它情况下，可能需要安装新工具或功能来收集所需的数据。在确定了创建分析所需的数据之后，必须将其收集并存储在将要编写分析的平台上。例如，可以使用Splunk的体系结构。

由于企业通常在网络入口和出口点部署传感器，因此，许多企业都依赖边界处收集的数据。但是，这就限制了企业只能看到进出网络的网络流量，而不利于防御者看到网络中及系统之间发生了什么情况。如果攻击者能够成功访问受监视边界范围内的系统并建立规避网络保护的命令和控制，则防御者可能会忽略攻击者在其网络内的活动。正如上文的攻击示例所述，攻击者使用合法的Web服务和通常允许穿越网络边界的加密通信，这让防御者很难识别其网络内的恶意活动。

由于使用基于边界的方法无法检测到很多攻击行为，因此，很有必要通过终端（主机端）数据来识别渗透后的操作。下图展示的是企业边界网络传感器在ATT&amp;CK框架中的覆盖范围。红色表示未能检测到攻击行为，黄色表示有一定检测能力。如果在终端上没有传感器来收集相关数据，比如进程日志，就很难检测到ATT&amp;CK模型描述的许多入侵。目前，国内外一些新一代主机安全厂商，都是采用在主机端部署Agent方式，比如青藤云安全，通过Agent提供主机端高价值数据，包括操作审计日志、进程启动日志、网络连接日志、DNS解析日志等。

[![](https://p4.ssl.qhimg.com/t015e9ff3a2c1ffaea5.png)](https://p4.ssl.qhimg.com/t015e9ff3a2c1ffaea5.png)

涵盖边界防御在内的ATT&amp;CK矩阵

此外，仅仅依赖于通过间歇性扫描端点来收集端点数据或获取数据快照，这可能无法检测到已入侵网络边界并在网络内部进行操作的攻击者。间歇性地收集数据可能会导致错过检测快照之间发生的行为。例如，攻击者可以使用技术将未知的RAT加载到合法的进程（例如explorer.exe）中，然后使用cmd.exe命令行界面通过远程Shell与系统进行交互。攻击者可能会在很短的时间内采取一系列行动，并且几乎不会在任何部件中留下痕迹让网络防御者发现。如果在加载RAT时执行了扫描，则收集信息（例如正在运行的进程、进程树、已加载的DLL、Autoruns的位置、打开的网络连接以及文件中的已知恶意软件签名）的快照可能只会看到在explorer.exe中运行的DLL。但是，快照会错过将RAT实际注入到explorer.exe、cmd.exe启动、生成的进程树以及攻击者通过shell命令执行的其它行为，因为数据不是持续收集的。

### 第3步：过程分析

组织机构拥有了必要的传感器和数据后，就可以进行分析了。进行分析需要一个硬件和软件平台，在平台上进行设计和运行分析方案，并能够让数据科学家设计分析方案。尽管通常是通过SIEM来完成的，但这并不是唯一的方法，也可以使用Splunk查询语言来进行分析，相关的分析分为四大类：

行为分析——旨在检测某种特定对抗行为，例如创建新的Windows服务。该行为本身可能是恶意的，也可能不是恶意的。并将这类行为映射到ATT&amp;CK模型中那些确定的技术上。

情景感知——旨在全面了解在给定时间，网络环境中正在发生什么事情。并非所有分析都需要针对恶意行为生成警报。相反，分析也可以通过提供有关环境状态的一般信息，证明对组织机构有价值。诸如登录时间之类的信息并不表示恶意活动，但是当与其它指标一起使用时，这种类型的数据也可以提供有关对抗行为的必要信息。情景感知分析还可以有助于监视网络环境的健康状况（例如，确定哪些主机上的传感器运行出错）。

异常值分析——旨在分析检测到非恶意行为，这类行为表现异常，令人怀疑，包括检测之前从未运行过的可执行文件，或者标识网络上通常没有运行过的进程。和情景感知分析一样，分析出异常值，不一定表示发生了攻击。

取证——这类分析在进行事件调查时最为有用。通常，取证分析需要某种输入才能发挥其作用。例如，如果分析人员发现主机上使用了凭据转储工具，进行此类分析会告诉你，哪些用户的凭据受到了损坏。

防御团队在网络竞赛演习期间或制定实际应用中的分析时，可以结合使用这四种类型的分析。下文将介绍如何综合使用这四种类型的分析：
1. 首先，通过在分析中寻找远程创建的计划任务，向安全运营中心（SOC）的分析人员发出警报，警告正在发生攻击行为（行为分析）。
1. 在从受感染的计算机中看到此警报后，分析人员将运行分析方案，查找预计执行计划任务的主机上是否存在任何异常服务。通过该分析，可以发现，攻击者在安排好远程任务之后不久，就已在原始主机上创建了一个新服务（异常值分析）。
1. 在确定了新的可疑服务后，分析人员将进行进一步调查。通过分析，确定可疑服务的所有子进程。这种调查可能会显示一些指标，说明主机上正在执行哪些活动，从而发现RAT行为。再次运行相同的分析方案，寻找RAT子进程的子进程，就会找到RAT对PowerShell的执行情况（取证）。
如果怀疑受感染机器可以远程访问其它主机，分析人员会决定调查可能从该机器尝试过的任何其它远程连接。为此，分析人员会运行分析方案，详细分析相关计算机环境中所有已发生的远程登录，并发现与之建立连接的其它主机（情景感知）。

### 第4步：构建场景

传统的渗透测试侧重于突出攻击者可能在某个时间段会利用不同类型系统上的哪些漏洞。MITRE的对抗模拟方法不同于这些传统方法。其目标是让红队成员执行基于特定或许多已知攻击者的行为和技术，以测试特定系统或网络的防御效果。对抗模拟演习由小型的重复性活动组成，这些活动旨在通过系统地将各种新的恶意行为引入环境，来改善和测试网络上的防御能力。进行威胁模拟的红队与蓝队紧密合作（通常称为紫队），以确保进行深入沟通交流，这对于快速磨练组织机构的防御能力至关重要。因此，与全范围的渗透测试或以任务目标为重点的红队相比，对抗模拟测试测试速度更快、测试内容更集中。

随着检测技术的不断发展成熟，攻击者也会不断调整其攻击方法，红蓝对抗的模拟方案也应该围绕这种思想展开。大多数真正的攻击者都有特定的目标，例如获得对敏感信息的访问权限。因此，在模拟对抗期间，也可以给红队指定特定的目标，以便蓝队能够针对最可能的对抗技术对网络防御和功能进行详细测试。

1.场景规划

为了更好地执行对抗模拟方案，需要白队传达作战目标，而又不向红队或蓝队泄露测试方案的详细信息。白队应该利用其对蓝队的了解情况以及针对威胁行为的分析来检测差距，并根据蓝队所做的更改或需要重新评估的内容来制定对抗模拟计划。白队还应确定红队是否有能力充分测试对抗行为。如果没有，白队应该与红队合作解决存在的差距，包括可能需要的任何工具开发、采购和测试。对抗模拟场景可对抗计划为基础，传达要求并与资产所有者和其它利益相关者进行协调。

模拟场景可以是详细的命令脚本，也可以不是。场景规划应该足够详细，足以指导红队验证防御能力，但也应该足够灵活，可以让红队在演习期间根据需要调整其行动，以测试蓝军可能未曾考虑过的行为变化。由于蓝队的防御方案也可能已经很成熟，可以涵盖已知的威胁行为，因此红队还必须能够自由扩展，不仅仅局限于单纯的模拟。通过由白队决定应该测试哪些新行为，蓝队可能不知道要进行哪些特定活动，而红队可以不受对蓝队功能假设的影响，因为这可能会影响红队做出决策。白队还要继续向红队通报有关环境的详细信息，以便通过对抗行为全面测试检测能力。

2.场景示例

举个例子，假设在Windows操作系统环境中，红队采用的工具提供了一个访问点和C2通道，攻击者通过交互式shell命令与系统进行交互。蓝队已部署了Sysmon作为探针，对过程进行持续监控并收集相关数据。此场景的目标是基于Sysmon从网络端点中收集数据来检测红队的入侵行为。

场景详情：

1) 为红队确定一个特定的最终目标。例如，获得对特定系统、域帐户的访问权，或收集要渗透的特定信息。

2) 假设已经入侵成功，让红队访问内部系统，以便于观察渗透后的行为。红队可以在环境中的一个系统上执行加载程序或RAT，模拟预渗透行为，并获得初始立足点，而不考虑先前的了解、访问、漏洞利用或社会工程学等因素。

3) 红队必须使用ATT&amp;CK模型中的“发现”技术来了解环境并收集数据，以便进一步行动。

4) 红队将凭证转储到初始系统上，并尝试定位周围还有哪些系统的凭证可以利用。

5) 红队横向移动，直到获得目标系统、账户、信息为止。

使用ATT&amp;CK作为对抗模拟指南，为红队制定一个明确的计划。技术选择的重点是基于在已知的入侵活动中通常使用的技术，来实现测试目标，但是允许红队在技术使用方面进行一些更改，采用一些其它行为。

3.场景实现

上述场景示例的具体实现步骤如下所示：

1) 模拟攻击者通过白队提供的初始访问权限后，获得了“执行”权限。以下内容可以表示攻击者可以使用通用的、标准化的应用层协议（如HTTP、HTTPS、SMTP或DNS）进行通信，以免被发现。例如远程连接命令，会被嵌入到这些通信协议中。

[![](https://p1.ssl.qhimg.com/t01d3d033b38a60838a.png)](https://p1.ssl.qhimg.com/t01d3d033b38a60838a.png)

2) 建立连接后，通过远程访问工具启动反弹shell命令界面：

[![](https://p3.ssl.qhimg.com/t018ae1622917e23b99.png)](https://p3.ssl.qhimg.com/t018ae1622917e23b99.png)

3) 通过命令行界面执行“执行”技术：

[![](https://p2.ssl.qhimg.com/t01cc9892db209242f8.png)](https://p2.ssl.qhimg.com/t01cc9892db209242f8.png)

4) 获得了足够的信息后，可以根据需要，自由执行其它战术和技术。以下技术是基于ATT&amp;CK的建议措施，以建立持久性或通过提升权限来建立持久性。获得足够的权限后，使用Mimikatz转储凭据，或尝试使用键盘记录器获取凭据，捕获的用户输入信息。

[![](https://p5.ssl.qhimg.com/t0143d89ae38ac5c495.png)](https://p5.ssl.qhimg.com/t0143d89ae38ac5c495.png)

5) 如果获得了凭据并且通过“发现”技术对系统有了全面的了解，就可以尝试横向移动来实现该方案的主要目标了。

[![](https://p1.ssl.qhimg.com/t01e696a71e75d2533b.png)](https://p1.ssl.qhimg.com/t01e696a71e75d2533b.png)

6) 根据需要使用上文提到的技术，继续横向移动，获取并渗透目标敏感信息。建议使用以下ATT&amp;CK技术来收集和提取文件：

[![](https://p5.ssl.qhimg.com/t01a3d72f3cbb4c228c.png)](https://p5.ssl.qhimg.com/t01a3d72f3cbb4c228c.png)

### 第5步：模拟威胁

在制定好对抗模拟方案和分析方案之后，就该使用情景来模拟攻击者了。首先，让红队模拟威胁行为并执行由白队确定的技术。在对抗模拟作战中，可以让场景的开发人员来验证其网络防御的有效性。红队则需要专注于红队入侵后的攻击行为，通过给定网络环境中特定系统上的远程访问工具访问企业网络。白队预先给红队访问权限可以加快评估速度，并确保充分测试入侵后的防御措施。然后，红队按照白队规定的计划和准则行动。

白队应与组织机构的网络资产所有者和安全组织协调任何对抗模拟活动，确保及时了解网络问题、用户担忧、安全事件或其它可能发生的问题。

### 第6步：调查攻击

一旦在给定的网络竞赛中红队发起了攻击，蓝队要尽可能发现红队的所作所为。在MITRE的许多网络竞赛中，蓝队中有负责创建场景的开发人员。这样做的好处是，场景开发者人员可以亲身体验他们的分析方案在现实模拟情况下表现如何，并从中汲取经验教训，推动未来的发展和完善。

在网络竞赛中，蓝队最开始有一套高度可信的过程分析方案，如果执行成功，就会了解一些初步指标红队，例如，红队时何时何地活跃起来的。这很重要，因为除了模糊的时间范围（通常是一个月左右）之外，没有向蓝队提供任何有关红队活动的信息。有时，蓝队的过程分析属于“行为”分析类别，而有些分析可能属于“异常”类别。应用这些高可信度的分析方案会促使蓝队使用先前描述的其它类型的分析（情景感知、异常情况和取证）进一步调查单个主机。当然，这个分析过程是反复迭代进行的，随着收集到新信息，在整个练习过程中，这一过程会反复进行。

最终，当确定某个事件是红队所为时，蓝队就开始形成自身的时间表。了解时间表很重要，可以帮助分析人员推断出只靠分析方案无法获得的信息。时间表上的活动差距可以确定需要进一步调查的时间窗口期。另外，通过以这种方式查看数据，即便没有关于红队活动的任何证据，蓝队成员也可以推断出在哪些位置能够发现红队的活动。例如，看到一个新的可执行文件运行，但没有证据表明它是如何放置在机器上的，这可能会提醒分析人员有可能存在红队行为，并可以提供有关红队如何完成其横向移动的详细信息。通过这些线索，还可以形成一些关于创建新分析的想法，以便用于基于ATT&amp;CK的分析开发方法的下一次迭代。

在调查红队的攻击时，蓝队会随着自身演习的进行而制定出几大类信息。这些信息是他们希望发现的信息，例如：

受到影响的主机——在演习时，这通常表示为主机列表以及每个主机视为可疑主机的原因。在尝试补救措施时，这些信息至关重要。

帐户遭到入侵——蓝队能够识别网络上已被入侵的帐户，这一点非常重要。如果不这样做，则红队或现实生活中的攻击者就可以从其它媒介重新获得对网络的访问权限，以前所有的补救措施也就化为泡影了。

目标——蓝队还需要努力确定红队的目标以及他们是否实现了目标。这通常是最难发现的一个内容，因为这需要大量的数据来确定。

使用的TTP——在演习结束时，要特别注意红队的TTP，这是确定未来工作的一种方式。红队可能已经利用了网络中需要解决的错误配置，或者红队可能发现了蓝队当前无法识别而无法进一步感知的技术。蓝队确定的TTP应该与红队所声称的TTP进行比较，识别任何防御差距。

### 第7步：评估表现

蓝队和红队活动均完成后，白队将协助团队成员进行分析，将红队活动与蓝队报告的活动进行比较。这可以进行全面的比较，蓝队可以从中了解他们在发现红队行动方面取得了多大程度上的成功。蓝队可以使用这些信息来完善现有分析，并确定对于哪些对抗行为，他们需要开发或安装新传感器、收集新数据集或制定新分析方案。



## 写在最后

ATT&amp;CK是MITRE提供的“对抗战术、技术和常识”框架，是由攻击者在攻击企业时会利用的12种战术和300多种技术组成的精选知识库，对于企业识别差距，提高防御能力有重大意义。青藤云安全四毛抒写的本文则通过详细介绍如何基于ATT&amp;CK框架制定分析方案，如何根据分析方案检测入侵行为从而发现黑客，为防御者提供了一款强大的工具，可以有效提高检测能力，从而增强企业的防御能力。
