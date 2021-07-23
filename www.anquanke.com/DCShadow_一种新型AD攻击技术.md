> 原文链接: https://www.anquanke.com//post/id/96704 


# DCShadow：一种新型AD攻击技术


                                阅读量   
                                **194843**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Luc Delsalle，文章来源：blog.alsid.eu
                                <br>原文地址：[https://blog.alsid.eu/dcshadow-explained-4510f52fc19d](https://blog.alsid.eu/dcshadow-explained-4510f52fc19d)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0135a94ed91e5e888b.jpg)](https://p3.ssl.qhimg.com/t0135a94ed91e5e888b.jpg)

## 一、前言

2018年1月24日，[Benjamin Delpy](https://twitter.com/gentilkiwi)和[Vincent Le Toux](https://twitter.com/mysmartlogon)这两名安全研究人员在[BlueHat IL](http://www.bluehatil.com/)安全会议期间公布了针对活动目录（AD，Active Directory）基础架构的一种新型攻击技术：[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)。利用这种技术，具有适当权限的攻击者可以创建恶意域控制器，将恶意对象复制到正在运行的[Active Directory](https://technet.microsoft.com/en-us/library/cc977985.aspx)基础架构中。

在本文中我们会介绍这种攻击方法所依赖的基础技术，顺便讨论其对现有AD基础架构所造成的安全影响。最后，我们也会分析红蓝对抗中蓝队如何检测这类攻击活动。



## 二、DCShadow的创新点

红队或者攻击者之所以想突破AD基础架构，主要是想在不引起安全检测告警的情况下获取用户及主机凭据。

为了实现这一目标，随着时间的推移，人们开发出了多种攻击技术，如LSASS注入、滥用Shadow Copy功能、解析NTFS卷、ESENT操作、敏感属性操作等。大家可以访问[ADSecurity.org](https://adsecurity.org/?p=2398)了解更多细节，这个网站已经归纳的非常好了。

在这些攻击方法中，有一种方法与[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击有关。[DCSync](https://adsecurity.org/?p=1729)攻击方法于2015年推出，这种攻击需要依靠域管理员（Domain Admins）或者域控制器（Domain Controllers）组中的成员实现对域控制器（DC）的数据复制操作（为了完成这一任务，攻击者需要掌握GetChangeAll权限，默认情况下管理员账户以及DC都具备该权限）。实际上，根据[MS-DRSR规范](https://msdn.microsoft.com/en-us/library/cc228086.aspx)中关于域控制器数据复制的描述，这些组可以通过[GetNCChanges RPC](https://msdn.microsoft.com/en-us/library/dd207691.aspx)向DC请求复制AD对象（包括用户凭据信息）。大家可以阅读ADSecurity.org上的这篇[文章](https://adsecurity.org/?p=1729)了解更多攻击细节。

[![](https://p0.ssl.qhimg.com/t01b11a3b3493d8f2bb.png)](https://p0.ssl.qhimg.com/t01b11a3b3493d8f2bb.png)

图1. 使用mimikatz工具发起DCSync攻击

[DCSync](https://adsecurity.org/?p=1729)攻击也有不足之处，比如攻击者无法在目标AD域中注入新的对象。当然，攻击者依然可以使用Pass-The-Hash（哈希传递）技术接管管理员账户，然后再注入对象，但这个过程更加麻烦、步骤繁琐，因此蓝队很有可能会捕捉到这个攻击行为。[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击方法对[DCSync](https://adsecurity.org/?p=1729)做了些改进，因此能够弥补这些缺点。

在[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击中，攻击者无需复制数据，只需要在目标基础架构中注册新的域控制器，以便注入AD对象或者修改已有的对象（替换该对象的属性内容）。使用恶意域控制器并不是一个新的点子，人们之前已经[多次](https://www.blackhat.com/docs/us-16/materials/us-16-Beery-The-Remote-Malicious-Butler-Did-It-wp.pdf)提到过这种方法，但这些方法需要较“粗鲁”的一些技术的配合（比如安装Windows Server虚拟机），同时还需要登录到正常的域控制器上以便虚拟机能升级为目标域的DC，这些方法并不是特别理想。

[![](https://p2.ssl.qhimg.com/t011758f7c5d652bef5.png)](https://p2.ssl.qhimg.com/t011758f7c5d652bef5.png)

图2. 升级为DC过程中生成的日志事件

为了理解[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)背后的天才想法，我们需要理解DC到底是什么，以及DC在AD基础架构中具体的注册过程。



## 三、域控制器（DC）

根据[MS-ADTS（Active Directory Technical Specification，活动目录技术规范）](https://msdn.microsoft.com/en-us/library/cc223122.aspx)中的描述，AD是依赖于某些专用服务的一种multi-master（多主）架构。其中，DC负责托管与AD对象有关的数据，你可以将DC看成一种服务或者提供该服务的服务器。多个DC之间可以协同工作，以确保在本地对AD对象的修改能正确同步到所有的DC上。

当DC以RW DC角色运行时， DC中包含域配置（Configuration）的完整命名上下文（naming context，NC）副本、schema（架构）、以及该域对应的森林（forest）的一个域名上下文。这样一来，每个RW DC就会拥有域的所有对象，包括凭据数据以及各种秘密数据（如私钥或者会话密钥）。因此在红蓝对抗中，是个人都知道DC是蓝队应重点保护唯一元素（有各种方法可以访问DC，管理员账户或者权限只是其中的两种方式）。



## 四、DC所提供的服务

如果我们从技术原理角度详细描述DC，这个过程可能会比较复杂，对理解[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击而言帮助不大。简单起见，如果某台服务器可以提供如下4个关键组件，那么我们就可以称之为域控制器：

1、能够复制自身信息的一个数据库引擎（也就是说，我们可以通过LDAP协议访问该数据库，并且该数据库实现了符合[MS-DRSR](https://msdn.microsoft.com/en-us/library/cc228086.aspx)以及[MS-ADTS](https://msdn.microsoft.com/en-us/library/cc223122.aspx)规范的几种RPC）。

2、可以通过[Kerberos](https://en.wikipedia.org/wiki/Kerberos_%28protocol%29)、[NTLM](https://msdn.microsoft.com/en-us/library/windows/desktop/aa378749%28v=vs.85%29.aspx)、[Netlogon](https://technet.microsoft.com/fr-fr/library/cc962284.aspx)或者[WDigest](https://technet.microsoft.com/en-us/library/cc778868%28v=ws.10%29.aspx)协议访问的身份认证服务器。

3、依赖于[SMB](https://msdn.microsoft.com/fr-fr/library/hh831795%28v=ws.11%29.aspx)协议以及[LDAP](https://www.ietf.org/rfc/rfc2251.txt)协议的[GPO](https://en.wikipedia.org/wiki/Group_Policy)配置管理系统。

4、支持认证的[DNS服务器](https://msdn.microsoft.com/en-us/library/cc448821.aspx)（可选），客户端可以通过该服务器来定位相关资源。

[![](https://p0.ssl.qhimg.com/t01a0f9e9cf9e243cad.png)](https://p0.ssl.qhimg.com/t01a0f9e9cf9e243cad.png)

图3. DC提供的各种服务



## 五、活动目录复制

除了这些服务外，我们的域控制器必须在目录基础架构中注册，以便另一个DC将其当成支持数据复制的一台源服务器。[NTDS](https://technet.microsoft.com/en-us/library/cc772829%28v=ws.10%29.aspx)服务上运行着名为[Knowledge Consistency Checker（KCC，知识一致性检查）](https://technet.microsoft.com/en-us/library/cc961781.aspx?f=255&amp;MSPPError=-2147217396)的一个进程，可以完成数据复制任务。

KCC的主要功能是生成并维护站点内复制以及站点间复制的拓扑。也就是说，KCC进程可以决定DC之间的链接关系，以创建有效的复制过程。对于站点内复制，每个KCC会生成自己的复制链接。对于站点间复制，每个站点上的KCC会生成所有的复制链接。这两种复制模式如下图所示：

[![](https://p2.ssl.qhimg.com/t013140f5662e32c14c.png)](https://p2.ssl.qhimg.com/t013140f5662e32c14c.png)

图4. 两类复制过程

默认情况下，每隔[15分钟](https://technet.microsoft.com/en-us/library/cc961781.aspx)KCC就会启动AD复制拓扑的绘制过程，以实现一致性和定时传播。KCC通过每个AD对象所关联的USN来识别活动目录中出现的改动，确保复制拓扑中不会出现被孤立的域控制器。有趣的是，在这之前Windows可能已经通过RPC（如DrsAddEntry）或者SMTP（仅适用于Schema以及Configuration）完成AD复制过程。

[![](https://cdn-images-1.medium.com/max/800/1*5GHGhWaGbGeCIm3MNkmtwQ.png)](https://cdn-images-1.medium.com/max/800/1*5GHGhWaGbGeCIm3MNkmtwQ.png)

图5. 注册表中关于复制时间间隔的键值

为了将新的服务器注入复制拓扑中，[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)背后的研究人员做了许多工作，其中最关键的就是成功识别出完成该任务所需的最少改动，这样就可以滥用这一过程，悄悄实现恶意信息的注入。



## 六、DCShadow的工作过程

[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击的目的是注册一个新的域控制器，实现恶意AD对象的注入，以便创建后门或者获取各种类型的非法访问渠道及权限。为了实现这一目标，[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击必须修改目标AD基础架构的数据库，授权恶意服务器成为复制过程中的一员。

### <a class="reference-link" name="6.1%20%E6%B3%A8%E5%86%8C%E6%96%B0%E7%9A%84%E5%9F%9F%E6%8E%A7%E5%88%B6%E5%99%A8"></a>6.1 注册新的域控制器

根据 [MS-ADTS规范](https://msdn.microsoft.com/en-us/library/cc223122.aspx)中的描述，AD数据库中使用nTDSDSA类的对象来表示域控制器，该对象始终位于域的配置（configuration）命名上下文中。更确切地说，每个DC都存储在站点容器内（objectclass为sitesContainer），是server对象的子节点。

[![](https://cdn-images-1.medium.com/max/800/1*9M2s56nPYnPze1x_LHR3WA.png)](https://cdn-images-1.medium.com/max/800/1*9M2s56nPYnPze1x_LHR3WA.png)[![](https://p3.ssl.qhimg.com/t01bfd6c4a877a67358.png)](https://p3.ssl.qhimg.com/t01bfd6c4a877a67358.png)

图6. 蓝色框中为存储NTDS-DSA对象的容器，红色框中为NTDS-DSA对象

经过简单查看，我们发现NTDS-DSA对象只能是server对象的子对象，而server对象只能是organization或者server对象的子对象：

1、server对象只能存储在serversContainer对象中，而后者只能在Configuration NC中找到。

2、organization对象只能存放在locality、country或者domainDNS对象中，这些对象可以在域的NC中找到。

[![](https://p1.ssl.qhimg.com/t018aecd12f9d6ce548.png)](https://p1.ssl.qhimg.com/t018aecd12f9d6ce548.png)

图7. 可以创建ntds-dsa对象的位置

这样一来，域控制器（nTDSDSA对象）只能在Configuration或者Domain NC中创建。在实际环境中，貌似只有站点容器（sitesContainer对象）中会存储nTDSDSA对象。由于KCC依靠站点信息来计算复制拓扑，因此只使用这些对象也符合常理。需要注意的是，我们无法使用LDAP协议来创建nTDSDSA对象。

说到这里你可能已经猜到，[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击的主要步骤是在schema的Configuration区中创建一个新的server及nTDSDSA对象。做到这一点后，攻击者就可以生成恶意复制数据，并将这些数据注入到其他域控制器中。

知道[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击的操作过程后，我们需要理解具备哪种权限才能在Configuration区中创建nTDSDSA对象。快速查看权限方面信息后，我们发现只有BUILTINAdministrators、DOMAINDomain Admins、 DOMAINEnterprise Admins以及NT AUTHORITYSYSTEM具备目标容器的控制权限。

[![](https://p0.ssl.qhimg.com/t01f5986a0a57155994.png)](https://p0.ssl.qhimg.com/t01f5986a0a57155994.png)

图8. Server对象的默认访问权限

因此我们可以得出一个结论：[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击技术并不属于权限提升漏洞范畴，而是滥用活动目录的一种机制。红队无法借此获得特权，但可以将其当成另一种方法，在活动目录中的达成持久化目标或者执行非法操作。因此，我们可以将其归类到[AD持久化技术](https://adsecurity.org/?p=1929)中，而非需要修复的漏洞。

### <a class="reference-link" name="6.2%20%E4%BF%A1%E4%BB%BB%E6%96%B0%E7%9A%84%E5%9F%9F%E6%8E%A7%E5%88%B6%E5%99%A8"></a>6.2 信任新的域控制器

如前文所述，[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击需要在Configuration区中添加新的nTDSDSA对象，以将其注册为复制过程中的新成员。然而，单单添加这个对象并不足以让我们的恶意服务器启动复制过程。实际上，为了成为复制过程的一员，我们需要满足两个前提条件：

1、被其他服务器信任，也就是说我们需要拥有有效的身份认证凭据。

2、支持身份认证，以便需要复制数据时其他DC能够连接到我们的恶意服务器。

恶意服务器可以通过有效的计算机账户成为可信的AD服务器。Kerberos SPN属性可以为其他DC提供身份认证支持。因此，每个nTDSDSA对象会通过serverReference属性链接到computer对象。

[![](https://p3.ssl.qhimg.com/t017131e1497f7df431.png)](https://p3.ssl.qhimg.com/t017131e1497f7df431.png)

图9. serverReference属性可以充当nTDSDSA对象及其对应的computer对象的桥梁

虽然理论上我们有可能使用用户账户完成这个任务，但使用计算机账户貌似更加方便，也更为隐蔽。事实上，利用这种方法我们可以实现服务器在DNS环境中的自动注册（这样其他DC就可以定位到我们的资源）、自动设置所需的属性以及自动管理身份认证秘钥。

这样一来，[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)就可以使用合法的计算机账户通过其他DC的身份认证。虽然computer对象以及nTDSDSA对象同样可以帮我们通过其他DC的身份认证，但我们还是需要让其他DC连接到恶意服务器，从该服务器上复制恶意信息。

我们可以使用Kerveros Service Principal Name（SPN，服务主体名称）来满足最后一个条件。许多文章中已经介绍过SPN方面的内容，Kerberos服务（KDC）需要使用SPN所关联的计算机账户来加密Kerberos票据。对我们而言，[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)可以在合法的computer对象上添加SPN，以通过身份认证。

在这方面工作上，[Benjamin Delpy](https://twitter.com/gentilkiwi)以及[Vincent Le Toux](https://twitter.com/mysmartlogon)发挥了非常关键的作用，他们找到了复制过程中所需的最小SPN集合。根据他们的研究成果，我们只需要两个SPN就可以让其他DC连接到恶意服务器：

1、DRS服务类（非常有名的GUID：E3514235–4B06–11D1-AB04–00C04FC2DCD2）；

2、Global Catalog服务类（包含“GC”字符串）。

比如，我们的恶意服务器（在alsid.corp域中DSA GUID为8515DDE8–1CE8–44E5–9C34–8A187C454208的roguedc）所需的两个SPN如下所示：

```
E3514235–4B06–11D1-AB04–00C04FC2DCD2/8515DDE8–1CE8–44E5–9C34–8A187C454208/alsid.corp
GC/roguedc.alsid.corp/alsid.corp
```

[![](https://p5.ssl.qhimg.com/t01d0f1e62734fb769a.png)](https://p5.ssl.qhimg.com/t01d0f1e62734fb769a.png)

图10. 带有DC SPN的恶意计算机账户

发起攻击时，[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)会将这两个SPN设置为目标计算机账户。更确切地说，DCShadow会使用DRSAddEntry RPC函数来设置这两个SPN（大家可以参考CreateNtdsDsa的[函数文档](https://msdn.microsoft.com/en-us/library/dd207878.aspx)，下文中会进一步介绍MS-DRSR RPC的更多细节）。

现在我们可以将恶意域控制器注册到复制过程中，也能通过其他DC的身份认证。接下来我们需要让DC使用我们提供的恶意数据启动复制过程。

### <a class="reference-link" name="6.3%20%E6%B3%A8%E5%85%A5%E6%81%B6%E6%84%8F%E5%AF%B9%E8%B1%A1"></a>6.3 注入恶意对象

经过前期的准备，我们已经收集到了完成复制过程中注册任务所需的所有信息，接下来我们来看一下[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)如何将恶意信息注入到DNS基础架构中。

根据 [MS-DRSR规范](https://msdn.microsoft.com/en-us/library/cc228086.aspx)中的描述，为了提供恶意数据，恶意域控制器必须实现某些RPC函数，即：IDL_DRSBind、IDL_DRSUnbind、IDL_DRSGetNCChanges以及IDL_DRSUpdateRefs。微软在公开规范文档中提供了这类IDL函数，现在[Benjamin Delpy](https://twitter.com/gentilkiwi)开发的[Mimikatz](https://github.com/gentilkiwi/mimikatz/commit/ab18bd103a5cd7e26fb8d475c5ea0157d6633ca9)工具中已经集成了这些函数。

[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击的最后一个步骤就是启动复制过程。为了完成这一任务，我们可以采用如下两种策略：

1、等待其他DC上的KCC进程来启动复制过程（需要15分钟的延迟）；

2、调用DRSReplicaAdd RPC函数启动复制过程。这样可以修改[repsTo](https://msdn.microsoft.com/en-us/library/cc228410.aspx)属性的内容，马上启动数据复制过程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01986a3f3f6828428a.png)

图11. MS-DRSR规范中有关DRSReplicaAdd IDL的描述

使用IDL_DRSReplicaAdd RPC发起复制过程是[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击的最后一个步骤，这样我们就可以将任意数据注入到目标AD基础架构中。完成该任务后，想在域环境中添加任何后门就易如反掌（比如在管理员组中添加新成员，或者在可控用户账户上设置SID历史记录）。

### <a class="reference-link" name="6.4%20%E6%95%B4%E4%BD%93%E8%BF%87%E7%A8%8B"></a>6.4 整体过程

[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)整体攻击过程如下图所示。

[![](https://p4.ssl.qhimg.com/t0136b17cd3ecc424d6.png)](https://p4.ssl.qhimg.com/t0136b17cd3ecc424d6.png)

图12. DCShadow攻击过程



## 七、DCShadow对蓝队策略的影响

根据有关[研究报告](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)的说法，负责AD安全监管的蓝队通常需要收集相关事件日志，他们可以配置域内主机，将主机的日志推送到中心[SIEM](https://en.wikipedia.org/wiki/Security_information_and_event_management)进行后续分析处理。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01eb0851d459074c76.png)

图13. 通过WinRM事件转发协议实现事件日志推送的SIEM架构

这种方法面临一些问题，第一个问题是只有合法的计算机才会将日志推送到日志收集器上。在[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击中，只有攻击者的主机上才会生成与新数据注入过程有关的事件日志，而这台主机明显不会向[SIEM](https://en.wikipedia.org/wiki/Security_information_and_event_management)发送事件。这样一来，由于合法主机上生成的事件日志非常少，因此[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)能实现静默攻击效果。

实际上，在本文中我们也提到过，攻击者将恶意数据信息注入目标AD之前，需要先执行几个操作。不幸的是，搭建恶意DC过程中涉及到的AD修改动作很少会纳入日志策略中。比如，日志策略中基本上不会考虑Configuration NC修改事件。蓝方可以针对这类改动操作发出警告，但需要区分相关事件是与恶意活动有关，还是与正常的AD操作有关，这个过程需要花费较多时间，实际操作起来并不容易。

蓝队需要全面重新设计已有的防护策略，将重心从日志分析转移到AD配置分析。最直接的方法就是监控复制动作（DrsGetNCChanges RPC更改操作）。实际上，默认情况下域的root（根）对象上的SACL条目会保存除域控制器以外的扩展权限的使用记录。这种情况下，蓝队很容易就能识别出来使用用户账户或者非DC主机的复制操作。然而，我们不觉得这是最为有效的一种方法。从我们的视角来看，为了检测[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击，蓝队需要采用如下3中策略：

1、仔细检查schema中的Configuration区。站点容器中的nTDSDSA对象必须与Domain Controllers组织单元（organizational unit，OU）中的正常域控制器相匹配（更严格条件下，需要与管理团队手动维护的一个DC清单相匹配）。在前者中出现但没有在后者中出现的任何对象都值得怀疑。需要注意的是，恶意nTDSDSA对象会在非法对象发布后立刻被删除。为了有效检测这种攻击手段，蓝队所使用的检测机制需要能够检测到对象创建过程。

2、在前文中我们提到，DC需要提供身份认证服务。为了发布改动信息，恶意DC需要提供能通过Kerberos访问的服务。也就是说，该DC会包含以“GC/”字符串开头的SPN（服务主体名称）。此外，攻击这也会用到著名的RPC 接口（GUID：E3514235–4B06–11D1-AB04–00C04FC2DCD2）。提供该服务但又不在DC OU中的主机也非常可疑。

3、攻击者需要较高权限才能使用[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)技术。蓝队可以分析并监控Configuration区中的权限信息，确保除了管理员之外，没有其他人能够更改这些信息。此外，如果非特权实体获得了DACL权限，这很有可能是出现后门的一种特征。



## 八、总结

再次强调一下，本文介绍的[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)并不是漏洞，而是将非法数据注入AD基础架构的一种新型方法。

不具备高权限的攻击者无法使用该方法来提升权限，也无法获取目标AD的管理访问权限。我们需要明确的一条底线是：如果我们的AD环境已经正确配置过并且处于安全状态，那么我们不需要采取任何紧急行动来进一步防护。

面对[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)技术，我们不需要打上紧急补丁，也不需要应用特殊配置，这一点与[WannaCry](https://en.wikipedia.org/wiki/WannaCry_ransomware_attack)/[NotPetya](https://en.wikipedia.org/wiki/Petya_%28malware%29)事件响应处置过程有所不同。

由于[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)不是漏洞，因此微软也不会发布更新来封堵该方法。如果想对付这种技术则需要改变AD的现有工作方式，这样一来也会给系统运行带来不便。之前公布[DCSync](https://adsecurity.org/?p=1729)攻击方法的研究人员以及微软也没有发布任何补丁来封堵该方法，因为该方法用到的都是合法的API，“修复”该缺陷就意味着禁用DC复制机制。俗话说的好，不要没事找事，何况AD现在仍在正常运行中。

然而，新的攻击方法已经公布，任何人都可以使用，这一点值得大家好好思考。高权限的攻击者可以借助该方法悄悄发起攻击，因此我们应该更新检测策略来检测这种攻击。传统的事件日志分析方法可能无法检测到[DCShadow](https://www.dropbox.com/s/baypdb6glmvp0j9/Buehat%20IL%20v2.3.pdf)攻击活动，为了有效检测这类行为，我们需要持续监视AD数据库，隔离非法的更改操作。这也是Alsid正在做的工作，我们已经可以保护客户免受这类攻击影响。大家可以访问[www.alsid.eu](http://www.alsid.eu./)了解我们如何应对这个安全风险。
