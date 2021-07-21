> 原文链接: https://www.anquanke.com//post/id/197713 


# 远程云端执行（RCE）：Azure云架构中的漏洞分析（Part 1）


                                阅读量   
                                **857123**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者checkpoint，文章来源：research.checkpoint.com
                                <br>原文地址：[https://research.checkpoint.com/2020/remote-cloud-execution-critical-vulnerabilities-in-azure-cloud-infrastructure-part-i/](https://research.checkpoint.com/2020/remote-cloud-execution-critical-vulnerabilities-in-azure-cloud-infrastructure-part-i/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01ae67ffea770fb439.png)](https://p1.ssl.qhimg.com/t01ae67ffea770fb439.png)



## 0x00 前言

云安全有点类似于voodoo，客户端会盲目地信任云服务商及其提供的安全性。如果大家了解过常见的云漏洞，会发现大多数漏洞都集中在客户端应用的安全性上（比如错误配置或者存在漏洞的应用），并没有出现在云服务商自身架构中。这里我们想打破常规思维，让大家知道云基础架构本身也并不安全。在这篇文章中，我们演示了各种攻击场景，以及我们在Azure Stack上找到的一些漏洞。

Check Point Research向微软安全响应中心（MSRC）反馈了此次研究中找到的漏洞，官方及时部署了解决方案，确保用户能继续安全使用Azure Stack。



## 0x01 搭建研究环境

云组件研究起来并不简单，大多数时间我们面对的是“黑盒”研究场景。幸运的是，微软提供了名为Azure Stack的一个本地（on-premise）Azure环境，主要用于企业场景。此外，微软还提供了免费版的Azure Stack Development Kit（ASDK）。用户只需要准备好满足安装硬件要求的单台服务器，遵循详细的安装指南即可。当安装完毕后，我们就能看到用户/管理员门户，与Azure Portal非常类似：

[![](https://p1.ssl.qhimg.com/t016341af25defb002c.png)](https://p1.ssl.qhimg.com/t016341af25defb002c.png)

默认情况下，ASDK自带了一些功能（核心组件），可以按需扩展，比如SQL Provider、App Service等。下面我们来比较一下ASDK与Azure，主要的不同点如下：

1、可扩展性：

ASDK运行在资源有限的单个实例上，所有角色都以独立的VM来运行，由Hyper-V处理。这样会导致这两者内部架构存在一些差异。

2、ASDK不像Azure运行最新的软件，会落后几个版本。

3、与Azure相比，ASDK只提供了数量较为有限的一些功能。



## 0x02 Azure Stack概览

> 备注：这里大部分数据均出自[此处](https://www.oreilly.com/library/view/microsoft-hybrid-cloud/9780134301976/)。

[![](https://p4.ssl.qhimg.com/t012aaaf43d01c886ed.png)](https://p4.ssl.qhimg.com/t012aaaf43d01c886ed.png)

让我们按层分解上图。

首先，Azure Stack门户提供简单的可访问UI，包括模板（Templates）、PowerShell等。这些组件用来部署和管理资源，也是Azure Stack中的常用接口。这些组件建立在Azure Resource Manager（ARM）之上并与之交互。ARM决定可以处理的请求类别，判断哪些请求需要转到另一层处理。

Partition Request Broker中包括Azure Stack中的核心资源提供者（provider）。每个资源提供者都包含一个API，方便与ARM层来回交互。资源提供者允许我们与底层交互，也包含可以从门户访问的一个用户/管理员扩展。

下面一层为基础设施控制层（Infrastructure Control Layer ），包含基础设施控制器（controller），这些控制器与Infrastructure Roles层交互。这一层包含一组内部API，没有对用户公开。

Infrastructure Roles负责各种任务，比如计算、网络、存储等。这一层包含Azure Stack的所有管理组件，并与底层硬件层交互，将硬件功能抽象为Azure Stack提供的高级软件服务。

ASDK基于Hyper-V，这意味着所有角色在宿主服务器上以独立的虚拟机形式运行。整个基础架构具有独立的虚拟网络，能将这些虚拟机与宿主网络隔离开来。

默认情况下，Azure Stack部署了多个基础角色，包括（[来源](https://docs.microsoft.com/en-us/azure-stack/asdk/asdk-architecture)）：

|名称|描述
|------
|**AzS-ACS01**|Azure Stack存储服务
|**AzS-ADFS01**|活动目录联合服务（Active Directory Federation Services，ADFS）
|**AzS-CA01**|用于Azure Stack角色服务的证书颁发服务
|**AzS-DC01**|用于Azure Stack的Active Directory、DNS及DHCP服务
|**AzS-ERCS01**|紧急恢复控制台VM
|**AzS-GWY01**|边际网关服务，如tenant（租户）网络的VPN site-to-site连接
|**AzS-NC01**|网络控制器，管理Azure Stack网络服务
|**AzS-SLB01**|Azure Stack中适用于tenant和Azure Stack基础架构服务的负载均衡多路复用服务
|**AzS-SQL01**|用于Azure Stack Infrastructure Roles的内部数据存储
|**AzS-WAS01**|Azure Stack管理门户及Azure Resource Manager服务
|**AzS-WASP01**|Azure Stack用户（tenant）门户及Azure Resource服务
|**AzS-XRP01**|用于Azure Stack的基础架构管理控制器，包括计算、网络、存储资源提供者

我们可以将上表按主要抽象层梳理出比较重要的虚拟机：
- ARM层：AzS-WAS01、AzS-WASP01
- RP层 + 基础结构控制层： AzS-XRP01
下面举个例子，演示一下这些抽象层如何协同工作。

比如说有个tenant希望停止Azure Stack中的某个虚拟机，整个运行过程如下所示：

1、tenant可以使用用户门户/CLI/PowerShell来执行该操作。这些接口最终都会向运行在Azs-WASP01上的ARM（Azure Resource Manager）发送一个HTTP请求，描述用户希望执行的操作。

2、ARM执行必要的检查（比如，检查请求的资源是否存在，该资源是否属于tenant等），然后尝试执行该操作。有些操作ARM自己无法处理（比如计算、存储等），incident会将请求附加其他参数转发给匹配的资源提供者（运行在Azs-XRP01上），以便处理虚拟机计算操作。

3、整个过程涉及到一些内部API请求链，最终Hyper-V集群中的虚拟机会被关闭，Azure Stack会将结果返回给tenant。

在下文中，我们将详细描述我们在内部服务中找到的一个问题，我们可利用该缺陷捕捉tenant及基础主机的屏幕截图。



## 0x03 屏幕截取及信息泄漏

[Service Fabric Explorer](https://docs.microsoft.com/en-us/azure/service-fabric/service-fabric-visualizing-your-cluster)是预装在主机中的一款web工具，充当RP及基础设施控制层（AzS-XRP01）角色。我们可以利用该工具查看以[Service Fabric Applications](https://docs.microsoft.com/en-us/azure/service-fabric/service-fabric-overview)形式构建的内部服务（位于RP层中）。

[![](https://p1.ssl.qhimg.com/t01c71987bb154facbb.png)](https://p1.ssl.qhimg.com/t01c71987bb154facbb.png)

当我们尝试通过Service Fabric Explorer访问服务对应的URL时，我们注意到某些URL并不要求身份认证（通常情况下这里会出现证书认证或者HTTP身份认证）。

这里我们有一些问题：

1、为什么这些服务不需要身份认证？

2、这些服务公开了哪些API？

这些服务采用C#开发，并没有公开源代码，所以我们需要使用反编译器进行研究，这里我们需要理解Service Fabric Applications的整体结构。

其中不需要身份认证的某个服务为“DataService”。我们首要任务是找到该服务在Azs-XRP01主机上的具体位置。我们可以运行如下WMI查询语句，列举出正在运行的进程：

[![](https://p4.ssl.qhimg.com/t018a0cfb5046aa970a.png)](https://p4.ssl.qhimg.com/t018a0cfb5046aa970a.png)

根据运行结果，我们能知道主机上运行的所有Service Fabric服务，其中就包括DataService。在DataService代码目录中执行遍历操作后，我们能找到一堆DLL，并且能根据文件名称猜测这些DLL的功能：

[![](https://p4.ssl.qhimg.com/t0100ab6381a3224b66.png)](https://p4.ssl.qhimg.com/t0100ab6381a3224b66.png)

反编译这些DLL后，我们能浏览内部代码，查找API HTTP路由对应的映射关系：

[![](https://p0.ssl.qhimg.com/t01a8c7c2c4801ecb9c.png)](https://p0.ssl.qhimg.com/t01a8c7c2c4801ecb9c.png)

从代码中可知，如果HTTP URI匹配某个路由模板，则请求会由对应的控制器来处理，这也是常见的REST API实现方式。大多数路由模板都至少需要1个参数，而目前我们并不清楚该参数的具体值。因此，我们首先开始研究不需要其他参数的控制器：
- `QueryVirtualMachineInstanceView`
- `QueryClusterInstanceView`
由于Azure Stack运行在我们的本地主机中，因此我们直接本地浏览这些API，研究响应机制。

当访问`virtualMachines/allocation` API（`QueryVirtualMachineInstanceView`）时，服务端会返回一大段XML/JSON文件（具体格式取决于我们发送的`Accept`头部字段），文件中包含集群Hyper-V节点中基础架构/tenant主机的大量数据。

[![](https://p0.ssl.qhimg.com/t014977ca11965e1d57.png)](https://p0.ssl.qhimg.com/t014977ca11965e1d57.png)

上图为部分返回数据，其中我们可以看到一些有趣的信息，比如虚拟机名称及ID，以及核心数、内存总量等硬件信息。

现在我们已经知道该API能提供关于基础架构/tenant主机的相关信息，我们可以继续分析需要参数的其他API。比如，我们可以研究下`VirtualMachineScreenshot`的工作方式，这个API看上去比较有趣。

根据模板，为了让`VirtualMachineScreenshot`控制器处理请求，我们必须提供若干个参数，如下：
<li>
`virtualMachineId`：我们希望执行操作的主机ID，该ID值由`QueryVirtualMachineInstanceView` API提供。</li>
<li>
`heightPixels`、`widthPixels`：屏幕截图的尺寸。</li>
提供这些参数后，我们可以调用`GetVirtualMachineScreenshot`函数：

[![](https://p2.ssl.qhimg.com/t01ff8f82ce2eb6c3af.png)](https://p2.ssl.qhimg.com/t01ff8f82ce2eb6c3af.png)

如果虚拟机ID存在且有效，服务端就会调用`GetVmScreenshot`，该函数实际上会将请求“代理”至另一个内部服务。

[![](https://p3.ssl.qhimg.com/t01ca2c60638af3b437.png)](https://p3.ssl.qhimg.com/t01ca2c60638af3b437.png)

可以看到代码会使用特定参数创建一个新的请求，并将该请求传递给请求执行器。名为“Compute Cluster Manage”的内部服务（位于基础设施控制层）会继续处理该请求。根据服务名，我们可以猜测该服务用来管理计算机集群，执行相关操作。下面看看该服务如何处理屏幕截图请求：

[![](https://p1.ssl.qhimg.com/t01ad4eafe0876f2e8a.png)](https://p1.ssl.qhimg.com/t01ad4eafe0876f2e8a.png)

我们发现这是一个封装函数，会调用`vmScreenshotCollector`实例上的`GetVmScreenshot`函数。然而我们发现这里有个新的参数，用来标记计算机集群中是否只包含单个主机/节点的标志位。

[![](https://p2.ssl.qhimg.com/t01982c4711686d0cbb.png)](https://p2.ssl.qhimg.com/t01982c4711686d0cbb.png)

当`GetVirtualMachineOwnerNode`确定虚拟主机位于哪个集群节点后，就会调用`GetVmThumbnail`函数：

[![](https://p0.ssl.qhimg.com/t01218f3181fd066c2f.png)](https://p0.ssl.qhimg.com/t01218f3181fd066c2f.png)

该函数似乎会构造一个远程Powershell命令，该命令会在计算节点上执行（这也是大多数计算操作的工作方式）。下面来看一下计算节点，研究`Get-CpiVmThumbnail`的实现方式：

[![](https://p4.ssl.qhimg.com/t017ad6ad7228c86cd3.png)](https://p4.ssl.qhimg.com/t017ad6ad7228c86cd3.png)

以上就是该函数的Powershell实现代码。从代码中可知，函数会执行`GetVirtualSystemthumbnailImage`，后者是一个Hyper-V VMI调用，用来抓取虚拟主机的缩略图。在Hyper-V中，缩略图为主机概览左下方的一个小窗口：

[![](https://p2.ssl.qhimg.com/t0103ae534cd7157dcf.png)](https://p2.ssl.qhimg.com/t0103ae534cd7157dcf.png)

然而，由于我们可以执行缩略图尺寸，因此能获得质量较高的屏幕截图。

现在我们已经基本澄清“DataService”的工作方式，让我们回到第一个问题：为什么该服务不需要身份认证？实际上我们并不知道答案，但显然这里应该加上身份认证机制。因此我们又衍生出另一个问题：在什么场景下，我们可以从外部访问到该服务？答案是SSRF，但我们应该从哪里找起？显然这里我们可以试一下用户门户，tenant可以访问该入口，也能访问ARM之类的服务。在Azure Stack上，该入口甚至可以直接访问内部服务。

Azure Stack及Azure可以使用模板来部署资源。模板可以加载自本地文件或者远程URL。这是非常简单的一个功能，对于SSRF场景而言也非常实用，因为该功能可以向某个URL发送GET请求来获取数据。远程模板加载的实现如下所示：

[![](https://p1.ssl.qhimg.com/t017bc0d24ed9f97a35.png)](https://p1.ssl.qhimg.com/t017bc0d24ed9f97a35.png)

`GetStringAsync`函数会向`templateUri`发送一个HTTP GET请求，以JSON格式返回数据。这里没有验证主机为内部还是外部资源（并且支持IPv6）。因此，该方法是SSRF的绝佳目标。尽管该方法只允许使用GET请求，但足以访问DataService。

我们来看个例子，比如我们想获取某个主机的屏幕截图，主机ID为`f6789665-5e37-45b8-96d9-7d7d55b59be6`，尺寸为800×600：

[![](https://p2.ssl.qhimg.com/t01760062d19cc2c039.png)](https://p2.ssl.qhimg.com/t01760062d19cc2c039.png)

我们得到的响应数据为经过Base64编码的原始图像数据。

现在我们可以处理该数据，将其转换为实际图像。比如，我们可以使用如下powershell代码：

[![](https://p4.ssl.qhimg.com/t01f50fce26232ced15.png)](https://p4.ssl.qhimg.com/t01f50fce26232ced15.png)

得到的图像如下：

[![](https://p4.ssl.qhimg.com/t019087cb37111e091c.png)](https://p4.ssl.qhimg.com/t019087cb37111e091c.png)



## 0x04 总结

在本文中，我们演示了一个小的逻辑错误如何变成较为严重的漏洞。在本例中，由于DataService并不需要身份认证，因此我们可以获取tenant及基础主机的屏幕截图及相关信息。

在第二篇[文章](https://research.checkpoint.com/2020/remote-cloud-execution-critical-vulnerabilities-in-azure-cloud-infrastructure-part-ii)中，我们将深入分析Azure App Service内部原理，检查其体系结构、攻击点，介绍我们在某个组件中找到的一个严重漏洞，该漏洞可以影响Azure云。

微软已经公开并[修复](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1234)了这个SSRF漏洞（CVE-2019-1234），我们从微软的漏洞奖励计划中收获了5,000美元。

此外，微软也独立发现了未授权内部API问题，并在2018年末的Azure Stack 1811更新中修复了该问题。
