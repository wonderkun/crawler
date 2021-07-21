> 原文链接: https://www.anquanke.com//post/id/220329 


# Windows横向移动全攻略（三）：DLL劫持


                                阅读量   
                                **267814**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者mdsec，文章来源：mdsec.co.uk
                                <br>原文地址：[https://www.mdsec.co.uk/2020/10/i-live-to-move-it-windows-lateral-movement-part-3-dll-hijacking/](https://www.mdsec.co.uk/2020/10/i-live-to-move-it-windows-lateral-movement-part-3-dll-hijacking/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01c2c8d6e7093d16dd.jpg)](https://p2.ssl.qhimg.com/t01c2c8d6e7093d16dd.jpg)



## 一、概述

在这一系列的前两篇文章中，我们详细分析了通过WMI事件订阅和DCOM实现横向移动的方法，并介绍了如何改进我们的工具。

在本系列的最后一篇文章中，我们将讨论如何将DLL劫持用于横向移动。从经验上来看，DLL劫持通常与创建持久性、特权提升等攻击方法相关。但是，在某些情况下，它也可以用于横向移动，正如SpectreOps的Dwight Hohnstein在[这篇](https://posts.specterops.io/lateral-movement-scm-and-dll-hijacking-primer-d2f61e8ab992)文章中所描述的那样，他使用了服务控制管理器实际演示了劫持过程。在这篇文章中，我们会展现出DLL劫持在横向移动方面更多的应用场景，并举例说明如何在其他服务（例如WMI和DCOM）中实现。



## DLL劫持的条件

我们在这里不再讨论什么是DLL劫持，假设大家已经熟悉模块加载搜索顺序的劫持方式，网上已经有很多资源对这种劫持方法做了详细介绍，包括：

[https://pentestlab.blog/2017/03/27/dll-hijacking/](https://pentestlab.blog/2017/03/27/dll-hijacking/)<br>[https://itm4n.github.io/windows-dll-hijacking-clarified/](https://itm4n.github.io/windows-dll-hijacking-clarified/)<br>[https://liberty-shell.com/sec/2019/03/12/dll-hijacking/](https://liberty-shell.com/sec/2019/03/12/dll-hijacking/)



## 二、定位DLL劫持

发现DLL劫持是一个相对简单的过程，因为可能会有很多可以利用的位置。在识别DLL劫持攻击点时，我通常使用procmon进行以下筛选：

1、路径以“.dll”结尾；<br>
2、搜索结果是“NAME NOT FOUND”。

如果我们在寻找横向移动的机会，这只是与远程系统进行交互并获取结果的一种情况。<br>
要与远程系统进行交互，还可以使用多种方式，包括：

1、WMI；<br>
2、DCOM；<br>
3、PowerShell远程；<br>
4、SMB；<br>
5、服务控制管理器和其他正在运行的服务。

但是，并不是所有这些都可能实现DLL劫持。

如果我们不急于实现横向移动，随着时间的流逝，远程系统上可能会发生各种事件，这些事件自然会指向缺失的DLL。例如，在这台Windows 10主机上，我们可以看到，在没有进行任何交互的情况下，几分钟后，多个进程都在寻找“C:\Windows\System32\edgegdi.dll”。这些进程中包括gpupdate.exe，它的运行周期与组策略刷新周期一致，默认情况下是90分钟运行一次。

[![](https://p0.ssl.qhimg.com/t010a1fe159cb02f4af.png)](https://p0.ssl.qhimg.com/t010a1fe159cb02f4af.png)

各种默认的应用程序也是不错的选择，例如OneDrive，它会定期执行，从而产生一些DLL劫持的机会。我们可以看到，它每分钟运行一次FileCoAuth.exe中显示的文件。

[![](https://p0.ssl.qhimg.com/t01bd1c11b9df30fb13.png)](https://p0.ssl.qhimg.com/t01bd1c11b9df30fb13.png)

另外，DiagTrack服务会定期查找“C:\Windows\System32\windowscoredeviceinfo.dll”。

[![](https://p2.ssl.qhimg.com/t011584af0fee80d314.png)](https://p2.ssl.qhimg.com/t011584af0fee80d314.png)

现在，我们已经研究了寻找DLL劫持的方法，接下来看看该如何利用。



## 三、利用DLL劫持

在找到适合劫持、用于横向移动的DLL后，我们需要利用SMB将DLL植入远程系统。

在加载植入的DLL时，有多种方法可以劫持执行程序，但我们更希望DLL作为真实DLL的代理，从而最大程度减少中断正常操作的可能性。有许多技术都可以实现这一目标，我们强烈建议阅读Silent Break Security的Nick Landers撰写的“[Adaptive DLL Hijacking](https://silentbreaksecurity.com/adaptive-dll-hijacking/)”这篇文章。

DLL代理的最简单方法可能是到处转发。这种技术仅仅是告诉加载程序将所有导出转发到真实的DLL，而我们的加载程序DLL如果要劫持对version.dll的调用，可能仅包含类似以下内容：

```
#pragma comment(linker,"/export:GetFileVersionInfoA=C:/Windows/System32/version.GetFileVersionInfoA,@1")
#pragma comment(linker,"/export:GetFileVersionInfoByHandle=C:/Windows/System32/version.GetFileVersionInfoByHandle,@2")
#pragma comment(linker,"/export:GetFileVersionInfoExA=C:/Windows/System32/version.GetFileVersionInfoExA,@3")
#pragma comment(linker,"/export:GetFileVersionInfoExW=C:/Windows/System32/version.GetFileVersionInfoExW,@4")
#pragma comment(linker,"/export:GetFileVersionInfoSizeA=C:/Windows/System32/version.GetFileVersionInfoSizeA,@5")
#pragma comment(linker,"/export:GetFileVersionInfoSizeExA=C:/Windows/System32/version.GetFileVersionInfoSizeExA,@6")
#pragma comment(linker,"/export:GetFileVersionInfoSizeExW=C:/Windows/System32/version.GetFileVersionInfoSizeExW,@7")
```

除了上面那篇文章之外，Nick还发布过一个工具包[Koppeling](https://github.com/monoxgas/Koppeling)，使用这个工具包可以将某个DLL的导出表克隆到另一个DLL，这样我们就不再需要从源代码手动编译代理DLL。

接下来，我们来看一些DLL劫持用于横向移动的实际案例。



## 四、案例研究：WMI劫持

如前所述，我们可以利用DLL劫持进行横向移动的一种方法是劫持我们可以实现远程交互的目标。比如wmiprvse.exe，这是WMI提供程序，会在启动WMI连接时生成。

无需执行任何查询就会生成wmiprvse.exe，可以使用类似于以下C#代码进行简单的认证：

```
ConnectionOptions cOption = new ConnectionOptions();
ManagementScope scope = null;
scope = new ManagementScope(NAMESPACE, cOption);
if (!String.IsNullOrEmpty(ACTIVE_DIRECTORY_USERNAME) &amp;&amp; !String.IsNullOrEmpty(ACTIVE_DIRECTORY_PASSWORD))
`{`
    scope.Options.Username = ACTIVE_DIRECTORY_USERNAME;
    scope.Options.Password = ACTIVE_DIRECTORY_PASSWORD;
    scope.Options.Authority = string.Format("ntlmdomain:`{`0`}`", ACTIVE_DIRECTORY_DOMAIN);
`}`
scope.Options.EnablePrivileges = true;
scope.Options.Authentication = AuthenticationLevel.PacketPrivacy;
scope.Options.Impersonation = ImpersonationLevel.Impersonate;
try `{`
    Console.WriteLine("[*] Attempting to connect to host " + Config.REMOTE_HOST);
    scope.Connect();
`}`
```

在启动这个WMI连接时，使用procmon监视wmiprvse.exe，我们发现了几个潜在目标DLL，这些也许可以被我们劫持。

[![](https://p5.ssl.qhimg.com/t01c5fa0eb825bd91e9.png)](https://p5.ssl.qhimg.com/t01c5fa0eb825bd91e9.png)

经过仔细观察后，可以看到该进程以NETWORK SERVICE用户的身份运行。

[![](https://p4.ssl.qhimg.com/t01cb1ca350d368ae2a.png)](https://p4.ssl.qhimg.com/t01cb1ca350d368ae2a.png)

在wmiprvse.exe生成时，使用SMB在其中一个位置植入代理DLL，这样就导致代码以NETWORK SERVICE特权执行，这只是其中的一个提权步骤，我们可以利用[@EthicalChaos](https://github.com/EthicalChaos)的SweetPotato来逐步实现权限提升。

为了利用这个漏洞，我们只需要制作武器化的DLL，然后使用[@monoxga](https://github.com/monoxga)的NetClone.exe实现导出的转发。

[![](https://p1.ssl.qhimg.com/t01367924c0f09bf0a9.png)](https://p1.ssl.qhimg.com/t01367924c0f09bf0a9.png)

随后，可以将DLL植入到远程系统上，只需要在wmiprvse.exe正在搜索的正确位置使用SMB，随后进行触发，或等待WMI连接进行。下面的视频中，展示了实际尝试的情况。

视频地址：[https://vimeo.com/465122250](https://vimeo.com/465122250)



## 五、案例研究：DCOM劫持

不仅仅是只有WMI这一种方式可以与远程系统实现交互。在[此前的文章](https://www.anquanke.com/post/id/217928)中，我们讨论了使用DCOM进行横向移动的一些方式，以及防御者如何监控这些已知类的使用。但是，如果几乎所有通过DCOM公开的类都可能导致横向移动呢？我们来看一下DLL劫持。

识别容易受到DLL劫持的DCOM暴露类的方法，与先前讨论的方法类似。在对选定的类进行实例化时，可以使用procmon监控相关进程，以识别出不存在的DLL。在这里，就不一定需要调用任何方法。

以InternetExplorer.Application类为例，我们可以实例化该对象：

[![](https://p2.ssl.qhimg.com/t019fbe32007fe92516.png)](https://p2.ssl.qhimg.com/t019fbe32007fe92516.png)

在监控iexplorer.exe时，将显示出缺少几个DLL：

[![](https://p5.ssl.qhimg.com/t01a3e7a400a194f9db.png)](https://p5.ssl.qhimg.com/t01a3e7a400a194f9db.png)

可以通过与WMI类似的方式来利用这个漏洞，方法是首先将DLL植入（在本例中位于C:\Program Files\Internet Explorer\iertutil.dll），然后远程实例化InternetExplorer.Application对象。

[![](https://p5.ssl.qhimg.com/t019587795487eb54c2.png)](https://p5.ssl.qhimg.com/t019587795487eb54c2.png)



## 六、检测

要检测通过DLL劫持实现的横向移动并不容易，可能需要关联多个事件才能可靠地识别这些攻击。其中的一种检测方式是聚焦于DLL植入，有一些事件可以作为指标。

其中，事件11（文件创建）和事件3（网络连接）非常重要。

[![](https://p3.ssl.qhimg.com/t019d16ead4f64885e1.png)](https://p3.ssl.qhimg.com/t019d16ead4f64885e1.png)

如果监测事件11，我们会在TargetFilename字段发现一个DLL，表明已经在文件系统上创建了一个DLL，如下所示：

[![](https://p3.ssl.qhimg.com/t01d69b9ada80fef137.png)](https://p3.ssl.qhimg.com/t01d69b9ada80fef137.png)

将对应的ProcessGuid与其他近期事件相关联，就指向了事件3：

[![](https://p4.ssl.qhimg.com/t016bb9e881c2ccdb3b.png)](https://p4.ssl.qhimg.com/t016bb9e881c2ccdb3b.png)

这个事件表明，在文件创建事件前不久，同一进程（系统）在445端口（SMB）上接收到了网络连接。

对这两个事件进行进一步解析，我们就得到了一种有效的方法，可以检测通过SMB的DLL写入。

当然，可以通过尝试检测触发过程，进一步完善这个方法，但是考虑到攻击者可能有多种方式来触发，这种检测方式的可靠性相对较差。

WMI wbemcomn.dll劫持事件ID的过程可以总结如下（由[@Cyb3rWard0g](https://github.com/Cyb3rWard0g)提供）：

[![](https://p5.ssl.qhimg.com/t010f11375c62ea3b29.png)](https://p5.ssl.qhimg.com/t010f11375c62ea3b29.png)

InternetExplorer.Application iertutil.dll劫持的过程可以归纳如下：

[![](https://p1.ssl.qhimg.com/t01c4d66961e76289b7.png)](https://p1.ssl.qhimg.com/t01c4d66961e76289b7.png)

如果大家有兴趣为这些技术建立检测功能，我们可以再次与[@Cyb3rWard0g](https://github.com/Cyb3rWard0g)合作，生成Mordor数据集，补充完善威胁狩猎剧本中的详细信息：

[DCOM IertUtil劫持Mordor数据集](https://mordordatasets.com/notebooks/small/windows/08_lateral_movement/SDWIN-201009183000.html)<br>[WMI wbemcomn劫持Mordor数据集](https://mordordatasets.com/notebooks/small/windows/08_lateral_movement/SDWIN-201009173318.html)<br>[DCOM lertUtil手册](https://threathunterplaybook.com/notebooks/windows/08_lateral_movement/WIN-201009183000.html)<br>[WMI Wbemcomn手册](https://threathunterplaybook.com/notebooks/windows/08_lateral_movement/WIN-201009173318.html)

这是一些基本的[Sigma规则](https://github.com/OTRF/ThreatHunter-Playbook/commit/33d2146d867611dd37958f2aacd8aa6ab0189c8c)，也可以用于检测这些特定的用例。

最后，非常感谢Roberto在帮助制定检测策略和数据方面的投入。

本文由Dominic Chell撰写。
