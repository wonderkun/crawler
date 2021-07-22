> 原文链接: https://www.anquanke.com//post/id/163280 


# 如何滥用PowerShell DSC进行横向渗透


                                阅读量   
                                **190329**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Specterops，文章来源：posts.specterops.io
                                <br>原文地址：[https://posts.specterops.io/abusing-powershell-desired-state-configuration-for-lateral-movement-ca42ddbe6f06](https://posts.specterops.io/abusing-powershell-desired-state-configuration-for-lateral-movement-ca42ddbe6f06)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0131f8ce73bc173397.jpg)](https://p3.ssl.qhimg.com/t0131f8ce73bc173397.jpg)



## 一、基本描述

PowerShell的[期望状态配置（Desired State Configuration，DSC）](https://docs.microsoft.com/en-us/powershell/dsc/overview)可以让我们[使用WMI](https://blogs.msdn.microsoft.com/powershell/2015/02/27/invoking-powershell-dsc-resources-directly/)来直接执行[资源](https://docs.microsoft.com/en-us/powershell/dsc/resources)。通过DSC WMI类，我们可以滥用[内置](https://docs.microsoft.com/en-us/powershell/dsc/builtinresource)的[脚本资源](https://docs.microsoft.com/en-us/powershell/dsc/scriptresource)来实现PowerShell代码的远程执行。这种横向渗透技术有如下几个有点：

1、PowerShell会在WMIC服务程序wmiprvse.exe的上下文环境中执行。传统的调用Win32_Process的Create方法会通过wmiprvse.exe创建子进程且带有命令行特征，因此从规避检测的角度来看，这种方法具备一定的优势（至少在本文发表以前）。

2、载荷的所有组件都仅依赖于WMI。

3、我们并不需要使用DSC服务的配置（甚至无需了解相关知识）。



## 二、具体需求

1、MSFT_DSCLocalConfigurationManager这个WMI类中必须存在ResourceTest方法，该类位于root/Microsoft/Windows/DesiredStateConfiguration命名空间中。注意：攻击者也可以选择调用ResourceGet或者ResourceSet方法。PowerShell DSC从PowerShell v4中开始引入，因此并非所有主机都可以使用这种技术。

2、默认情况下，我们必须具备管理员凭据才能远程调用WMI方法。在远程调用时，WMI受[DCOM](https://docs.microsoft.com/en-us/windows/desktop/wmisdk/securing-a-remote-wmi-connection)或者[WSMan](https://docs.microsoft.com/en-us/powershell/module/microsoft.wsman.management/providers/wsman-provider?view=powershell-6)安全设置的保护。建立远程连接后，WMI本身通过与特定[命名空间](https://docs.microsoft.com/en-us/windows/desktop/wmisdk/securing-wmi-namespaces)对应的安全描述符进行保护，在这种场景中，该命名空间为root/Microsoft/Windows/DesiredStateConfiguration。



## 三、PoC

第一个步骤是准备待执行的载荷。我们想在目标上执行的PowerShell代码必须采用[MOF](https://docs.microsoft.com/en-us/windows/desktop/wmisdk/managed-object-format--mof-)格式。在目标上执行的某个示例载荷如下所示：

实际上，这里我们所需修改的唯一特征就是PowerShell载荷。在我们的示例中，我们将调用ResourceTest方法，该方法对应的是TestScript属性中的载荷。需要注意的是我们需要转义处理特殊字符。MOF自动化生成及载荷转义处理是可以自动化完成的操作。

下一个步骤是将MOF转化为二进制形式（ResourceTest方法所期望的数据格式）：

在上述代码中需要注意的是，如果我们在本地测试载荷，则无需将载荷长度添加到byte数组中。现在我们已经正确编码载荷，接下来只需要在目标上执行载荷即可。

在上述例子中，请注意我在执行之前首先验证了远程类以及方法是否存在。在使用WMI技术时，我建议大家在最终执行之前首先验证目标类和方法是否存在。

以上就是主要内容。我刻意介绍了个大概，在其他内容或者具体操作方面给大家留下较大空间。在这个例子中，载荷执行结果会在本地落盘。如果我们想通过WMI远程获取文件内容，可以参考[此处](https://twitter.com/mattifestation/status/899475316929736704)介绍的方法。此外，在上述例子中，我使用了PSv3中才引入的CMI cmdlets，如果想兼容v2，大家也可以改造代码以适配老版WMI cmdlets。



## 四、发现过程

我是在学习DSC的基础知识时偶然发现了这种技术。我在网上找到了一篇[文章](https://blogs.msdn.microsoft.com/powershell/2015/02/27/invoking-powershell-dsc-resources-directly/)，文中讨论了如何使用WMI来直接调用DSC资源。我对WMI有所了解，因此这篇文章一下子引燃了我对这方面内容的兴趣。该文章演示了如何调用内置的文件资源，因此我只需要澄清如何调整细节，以便适用于脚本资源即可。



## 五、检测方法

幸运的是，如果我们能够获取事件日志，那么就有很多机会可以检测到这类技术。

### <a name="Microsoft-Windows-PowerShell/Operational%E4%BA%8B%E4%BB%B6%E6%97%A5%E5%BF%97"></a>Microsoft-Windows-PowerShell/Operational事件日志

53504事件

PowerShell Named Pipe IPC事件将告诉我们已启动的PowerShell AppDomain的名称。当DSC执行脚本资源时，该事件会自动捕捉DscPsPluginWkr_AppDomain AppDomain，顾名思义，这是DSC执行所特有的名称。典型事件如下：

4104事件

该事件与PowerShell v5脚本块（ScriptBlock）日志有关。攻击者可以轻松规避ScriptBlock的自动日志机制，但如果启用了全局ScriptBlock日志，那么攻击者的载荷操作基本上都会被记录在案。ScriptBlock日志不仅会记录下执行的载荷，也会捕捉与执行内置脚本资源有关的帮助程序代码。

调用脚本资源时被捕捉到的一些ScriptBlock数据样例如下所示：

### <a name="Windows%20PowerShell%E4%BA%8B%E4%BB%B6%E6%97%A5%E5%BF%97"></a>Windows PowerShell事件日志

400事件

在典型的PowerShell日志中，ID为400的事件表明系统中启动了一个新的PowerShell宿主进程。当DSC脚本资源执行时，会生成独特的事件日志条目，我们可以轻松定位。典型例子如下：

Engine状态从None变为Available。

PowerShell宿主进程在wmiprvse.exe上下文中启动（参考HostApplication字段），这可能是环境中（特别是工作站上）非常独特的一个特征。

### <a name="Microsoft-Windows-DSC/Operational%E4%BA%8B%E4%BB%B6%E6%97%A5%E5%BF%97"></a>Microsoft-Windows-DSC/Operational事件日志

4102事件

该事件表明某个DSC资源被发送到某个表上。该事件可以为我们提供执行DSC资源的用户SID以及来源主机信息（如果主机位于域环境中）。典型事件如下所示：



## 六、总结

我录制了一个[视频](https://youtu.be/FURl9oNjO5E)，演示了如何使用DSC进行横向渗透，以及如何仅依赖WMI来远程获取文件内容。

大家可以访问[此处](https://gist.github.com/mattifestation/89bfacc2435bd9d2f82a8205ea984d1d)下载演示代码，祝大家玩得开心。
