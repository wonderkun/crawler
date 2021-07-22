> 原文链接: https://www.anquanke.com//post/id/86575 


# 【技术分享】零C++基础，打造Windows事件钩子：对WMI的深入分析


                                阅读量   
                                **145913**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：huntingmalware.com
                                <br>原文地址：[https://blog.huntingmalware.com/notes/WMI](https://blog.huntingmalware.com/notes/WMI)

译文仅供参考，具体内容表达以及含义原文为准

[](http://reactjs.com/)

[![](https://p0.ssl.qhimg.com/t01aaa333d9c9aaf16c.png)](https://p0.ssl.qhimg.com/t01aaa333d9c9aaf16c.png)

译者：[eridanus96](http://bobao.360.cn/member/contribute?uid=2857535356)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

在想要Hook Windows事件时，大家往往会想到rootkits、低级C++代码和Windows API调用。其实还有另一种更简单的方法，无需了解任何关于Windows内部结构的知识，使用预装在Windows中的工具即可实现，那就是WMI。

**<br>**

**关于WMI**

以下是摘自MSDN的官方说明：

**WMI（Windows Management Instrumentation）****是Windows操作系统上管理数据和操作的基础结构。您可以编写WMI脚本或应用程序，以自动化的方式远程管理计算机上的任务。同时，WMI也能够向操作系统和产品的其他部分提供管理数据。**

这个说明让我们知道了WMI的潜力，它可以在远程计算机上去执行管理任务。然而，这只是冰山一角。在近期，一些攻击者（例如CozyDuke和Deep Panda）已经开始使用Windows本地工具来进行攻击活动，这将会成为一种发展趋势。

这种攻击方式对于攻击者而言具有许多优势。首先，攻击者无需再将自己的工具放在目标系统中，有效降低了被检测到的概率。其次，使用WMI在被攻击的系统中留下的痕迹少之又少。

WMI可以通过PowerShell、WMI控制台或使用托管对象格式（MOF）脚本进行调用。

使用PowerShell的WMI，可以打开一个PowerShell终端，并按下述方式执行get-wmiobject（或gwmi）命令：

```
$ get-wmiobject win32_logicaldisk name, freespace, systemname, size -filter drivetype=3   __GENUS: 2 __CLASS: Win32_LogicalDisk __SUPERCLASS: __DYNASTY: __RELPATH: __PROPERTY_COUNT: 4 __DERIVATION: `{``}` __SERVER: __NAMESPACE: __PATH: FreeSpace: 34652438528 Nam: C: Size: 106901270528 SystemName: AI-PINCHEWEEEY-VM PSComputerName:
```

如上所示，我们可以通过使用Win32_LogicalDisk类获得多个系统驱动器属性。这些类中的每一个都有属性和可以执行的方法。可以通过阅读对应的MSDN文档（[https://msdn.microsoft.com/en-us/library/windows/desktop/aa394173%28v=vs.85%29.aspx](https://msdn.microsoft.com/en-us/library/windows/desktop/aa394173%28v=vs.85%29.aspx)），获取其信息。

攻击者可以执行创建C盘卷影副本的WMI命令，并检索其ID，以便后期清理痕迹时删除卷影副本。目前，这种方法已经被用于解密SAM文件并获得Windows凭据。在这种情况下，Win32_ShadowCopy类中的Create()方法被调用：

```
$ Get-WMIObject Win32_ShadowCopy -List).Create("C:", "ClientAccessible").ShadowID
```

如果你想要卷影副本的moar cookie，可以参考这一篇文章：

[https://webcache.googleusercontent.com/search?q=cache:qiIjB9TU0VwJ:blog.szynalski.com/2009/11/volume-shadow-copy-system-restore/](https://webcache.googleusercontent.com/search?q=cache:qiIjB9TU0VwJ:blog.szynalski.com/2009/11/volume-shadow-copy-system-restore/)

另外，也可以从Windows命令行中通过WMI控制台执行WMI命令，其语法类似于：

```
$ wmic logicaldisk where drivetype=3 get name, freespace, systemname, size FreeSpace         Name  Size               SystemName 33230168064  C:   106901270528  AI-PINCHEWEEEY-VM
```



**<br>**

**开始攻击**

我们现在知道，已经有很多可以通过WMI使用的类，并且每一个类都有可以执行的方法。那么攻击者如何利用WMI实现攻击呢？我们举两个例子。

首先是启动进程：

```
$ wmic process call create "notepad.exe" Executing (Win32_Process)-&gt;Create() Method execution successful. Out Parameters: instance of __PARAMETERS `{`
```

接下来是结束进程：

```
$ wmic process where name="notepad.exe" delete Deleting instance \AI-PINCHEWEEEY-VMROOTCIMV2:Win32_Process.Handle="2416" Instance deletion successful.
```

想必大家已经觉得事情有些可怕了吧。甚至，你可以使用很多操作系统类，例如：

Win32_Process (“edit”, query processes)

Win32_Service (“edit”, query services)

Win32_Directory (“edit”, query directories)

Win32_Shares (“edit”, query network shares)

Win32_LocalTime (query time)

更多关于操作系统类的介绍可以参考：[https://msdn.microsoft.com/en-us/library/dn792258](https://msdn.microsoft.com/en-us/library/dn792258)

我们尝试远程运行命令：

```
$ wmic /node: "192.168.1.10" /username:domainuser /password:pwd process call create 'notepad.exe' Executing (Win32_Process)-&gt;Create() Method execution successful. Out Parameters: instance of __PARAMETERS `{`              ProcessId = 5176;
```

当攻击者需要从一台主机横向移动到另一台主机时，这无疑来说是一个简单的方式，因为不需要再像PSExec一样将工具放入目标主机中。

**<br>**

**Hook Windows事件**

接下来，我们来聊一下MOF脚本。简而言之，MOF脚本是通过mofcomp.exe程序编译后产生的文件，通过它可以调用WMI的一些功能。

借助MOF脚本，我们可以定时执行指定的命令，其使用如下：

**__EventConsumer： 执行什么内容**

**__EventFilter： 什么时间执行**

** __FilterToConsumerBinding： 绑定执行内容与执行时间**

特别说明的一点是，Event Consumer可以执行VB脚本，例如：

```
instance of ActiveScriptEventConsumer as $Cons `{`          Name = "ASEC";          ScriptingEngine = "VBScript";          ScriptText =              "Set objShell = CreateObject("WScript.Shell") n"               "objShell.Exec("c:\windows\system32\cmd.exe /c echo MOF Script Output&gt;c:\mof_output.txt")n"; `}`;
```

Event Consumer可以执行Windows命令行，并通过VB脚本输出文件。

下面是一个Event Filter的例子：

```
instance of __EventFilter as $Filt `{`          Name = "EF";          EventNamespace = "root\cimv2";          QueryLanguage = "WQL";          Query = "SELECT * FROM __InstanceCreationEvent "                   "WITHIN 2 WHERE TargetInstance ISA 'Win32_Process' "                  "AND TargetInstance.Name = 'notepad.exe'"; `}`;
```

Event Filter使用了一种名为WQL（WMI查询语言）的语言。这种语言可以用来Hook不同的系统事件。在这种情况下，我们定义了“何时触发”，在发生实例创建事件时，可以被读取。在本例中，我们寻找的是一个名为“notepad.exe”的Wind32_Process类实例创建事件。

这是一个用来Hook Create Process调用的简单方法，攻击者可以查看特定的进程，随后执行某些操作，例如结束进程。

下面，让我们看看如何将执行内容与执行时间相绑定：

```
instance of __FilterToConsumerBinding `{`          Filter = $Filt;          Consumer = $Cons; `}`;
```

最终的MOF脚本是这样的：

```
#pragma namespace ("\\.\root\subscription")   instance of ActiveScriptEventConsumer as $Cons `{`          Name = "ASEC";          ScriptingEngine = "VBScript";          ScriptText =              "Set objShell = CreateObject("WScript.Shell") n"               "objShell.Exec("c:\windows\system32\cmd.exe /c echo MOF Script Output&gt;c:\mof_output.txt")n"; `}`;   instance of __EventFilter as $Filt `{`          Name = "EF";          EventNamespace = "root\cimv2";          QueryLanguage = "WQL";          Query = "SELECT * FROM __InstanceCreationEvent "                   "WITHIN 2 WHERE TargetInstance ISA 'Win32_Process' "                  "AND TargetInstance.Name = 'notepad.exe'"; `}`;   instance of __FilterToConsumerBinding `{`          Filter = $Filt;          Consumer = $Cons; `}`;
```

要执行这一脚本，我们只需以管理员身份执行mofcomp.exe工具来编译它即可：

```
$ mofcomp.exe .mof_script.mof Microsoft (R) MOF Compiler Version 10.0.10586.0 Copyright (c) Microsoft Corp. 1997-2006. All rights reserved. Parsing MOF file: .mof_script.mof MOF file has been successfully parsed Storing data in the repository... WARNING: File .mof_script.mof does not contain #PRAGMA AUTORECOVER. If the WMI repository is rebuilt in the future, the contents of this MOF file will not be included in the new WMI repository. To include this MOF file when the WMI Repository is automatically reconstructed, place the #PRAGMA AUTORECOVER statement on the first line of the MOF file. Done!
```

在此时，如果打开记事本，还可以看到是如何在C:中创建mof_output.txt文件的。

**<br>**

**更深入的分析**

如果需要在某个特定时间执行，同样非常容易，我们只需要将Event Filter更改为如下内容：

```
instance of __EventFilter as $Filt `{`          Name = "EF";          EventNamespace = "root\cimv2";          QueryLanguage = "WQL";          Query = "SELECT * FROM __InstanceModificationEvent WITHIN 20 WHERE "                  "TargetInstance ISA 'Win32_LocalTime' AND "                  "TargetInstance.Hour = 10 AND "                  "TargetInstance.Minute = 34"; `}`;
```

现在，Event Consumer被设定为在上午的10:34触发。我们是通过hook系统时间和其变化来实现的定时。其中，WITHIN子句定义了20秒的轮询间隔。

至此，我们已经了解攻击者是如何使用WMI和MOF脚本来执行想要的操作。可以在特定的时间（用于决定何时从目标系统中获取信息）、进程或服务启动/停止时（用于停用安全产品）、某个文件被写入或删除时、Windows登录时去执行指定的操作。

**<br>**

**如何防范**

我们已经知道WMI攻击有多强大，接下来的问题就是如何去防范此类攻击。最重要的是，管理员需要了解系统中正在运行的内容。具体而言，需要知道在系统中注册了哪些事件，以便监控它们的创建和删除。用户可以使用以下PowerShell命令列出Event Consumers、Event Filters和Filter To Consumer Bindings：

```
gwmi -Namespace "root/subscription" -Class __EventFilter gwmi -Namespace "root/subscription" -Class __EventConsumer gwmi -Namespace "root/subscription" -Class __FilterToConsumerBinding
```

可以使用下列命令删除事件：

```
gwmi -Namespace "root/subscription" -Class __EventConsumer | where name -eq "&lt;NAME&gt;" | Remove-WmiObject gwmi -Namespace "root/subscription" -Class __EventFilter | where name -eq "&lt;NAME&gt;" | Remove-WmiObject
```

我们还可以编写自己的脚本，监视系统事件并删除不应该存在的所有内容。此外，还可以使用Windows的事件跟踪器来跟踪WMI活动。

 

**总结**

众所周知，每一个强大的工具，都有其正反两面。目前，WMI攻击已经被一些恶意软件使用，例如Wiper（在索尼影业泄密事件中被用于横向移动）、Flame（通过一个MOF文件执行使用rundll32的DLL）、Kjw0rm（在法国TV5Monde网络攻击事件中被用于获取系统信息）、PowerWorm（持续感染U盘文件的恶意软件）和Operation Mangal（安装自定义的恶意软件）等。

希望通过本文，能让大家了解到WMI的作用，能充分意识到其潜在的危险，并将其加入到大家的威胁模型之中


