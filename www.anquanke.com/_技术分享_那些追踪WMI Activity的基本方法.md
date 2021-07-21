> 原文链接: https://www.anquanke.com//post/id/87041 


# 【技术分享】那些追踪WMI Activity的基本方法


                                阅读量   
                                **192872**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：darkoperator.com
                                <br>原文地址：[https://www.darkoperator.com/blog/2017/10/14/basics-of-tracking-wmi-activity](https://www.darkoperator.com/blog/2017/10/14/basics-of-tracking-wmi-activity)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01b085f7d8bf46a793.jpg)](https://p0.ssl.qhimg.com/t01b085f7d8bf46a793.jpg)

译者：[blueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**简介**



WMI（Windows Management Instrumentation）自Windows 2000以来一直是Windows操作系统中的一个功能，该功能对系统管理员来说是非常重要的，它能够获取计算机内部状态的信息，能够对磁盘、进程、和其他 Windows 系统对象进行建模，从而实现“指示”功能。正是由于WMI的这种灵活性，在它早期被引入Windows操作系统时，网络攻击者经常利用WMI来对计算机实施攻击。WMI是微软Windows操作系统中的一个非常重要的技术，但从安全的角度考虑，目前还没有一种行之有效的方法去记录某用户操作WMI功能的行为活动。对于“防守者”而言，他们通常利用第三方工具或自己编写的解决方案来去记录操作WMI的行为活动，但这在一定程度上并不能够阻止“攻击者”操作WMI来执行各种网络攻击的行为。在本文中，我们将看看微软是如何改进记录WMI操作行为功能的。

<br>

**WMI Activity Provider**

****

在2012年之前，Windows系统中的WMI Activity事件日志程序主要用于在WMI启用时记录其跟踪和调试信息，但在Windows新发行版本中扩展了该程序的功能，使用Operational选项可以对WMI的操作行为进行记录。下面我们将使用PowerShell对该新功能进行分析，并使用Get-WinEvent cmdlet来获取信息。

我们首先获得Provider程序的对象：



```
PS C:&gt; $WmiProv = Get-WinEvent-ListProvider "Microsoft-Windows-WMI-Activity"
PS C:&gt; $WmiProv
Name     : Microsoft-Windows-WMI-Activity
LogLinks : `{`Microsoft-Windows-WMI-Activity/Trace, Microsoft-Windows-WMI-Activity/Operational, Microsoft-Windows-WMI-Activity/Debug`}`
Opcodes  : `{``}`
Tasks    : `{``}`
PowerShell对该对象的输出进行了格式化处理，因此我们需要使用Format-List参数来查看所有属性以及属性的值。
 PS C:&gt; $WmiProv | Format-List -Property *
ProviderName      : Microsoft-Windows-WMI-Activity
Name              : Microsoft-Windows-WMI-Activity
Id                : 1418ef04-b0b4-4623-bf7e-d74ab47bbdaa
MessageFilePath   : C:WINDOWSsystem32wbemWinMgmtR.dll
ResourceFilePath  : C:WINDOWSsystem32wbemWinMgmtR.dll
ParameterFilePath :
HelpLink          : https://go.microsoft.com/fwlink/events.asp?CoName=Microsoft Corporation&amp;ProdName=Microsoft@Windows@Operating
                    System&amp;ProdVer=10.0.15063.0&amp;FileName=WinMgmtR.dll&amp;FileVer=10.0.15063.0
DisplayName       : Microsoft-Windows-WMI-Activity
LogLinks          : `{`Microsoft-Windows-WMI-Activity/Trace, Microsoft-Windows-WMI-Activity/Operational, Microsoft-Windows-WMI-Activity/Debug`}`
Levels            : `{`win:Error, win:Informational`}`
Opcodes           : `{``}`
Keywords          : `{``}`
Tasks             : `{``}`
Events            : `{`1, 2, 3, 11...`}`
```

下面让我们看看LogLinks或者Provider程序将事件日志保存在哪里。



```
PS C:&gt; $WmiProv.LogLinks
LogName                                    IsImported DisplayName
-------                                    ---------- -----------
Microsoft-Windows-WMI-Activity/Trace            False
Microsoft-Windows-WMI-Activity/Operational      False
Microsoft-Windows-WMI-Activity/Debug            False
```

上述Powershell的输出中，我们比较感兴趣的是Microsoft-Windows-WMI-Activity/Operational。现在我们已经确定了哪个EventLog会保存我们感兴趣事件的日志，下面我们可以看看Provider程序生成的事件日志。通常情况下，Provider可以从几个事件中生成超过100个事件日志。因此，我们使用Measure-Object cmdlet来查看Provider生成的事件数量。



```
PS C:&gt; $WmiProv.Events | Measure-Object
Count    : 22
Average  :
Sum      :
Maximum  :
Minimum  :
Property :
```

通过上述输出我们看到Provider生成了22个事件，下面我们使用**Get-Member cmdlet**来看看如何组合每个对象。



```
PS C:&gt; $WmiProv.Events | Get-Member
   TypeName: System.Diagnostics.Eventing.Reader.EventMetadata
Name        MemberType Definition
----        ---------- ----------
Equals      Method     bool Equals(System.Object obj)
GetHashCode Method     int GetHashCode()
GetType     Method     type GetType()
ToString    Method     string ToString()
Description Property   string Description `{`get;`}`
Id          Property   long Id `{`get;`}`
Keywords    Property   System.Collections.Generic.IEnumerable[System.Diagnostics.Eventing.Reader.EventKeyword] Keywords `{`get;`}`
Level       Property   System.Diagnostics.Eventing.Reader.EventLevel Level `{`get;`}`
LogLink     Property   System.Diagnostics.Eventing.Reader.EventLogLink LogLink `{`get;`}`
Opcode      Property   System.Diagnostics.Eventing.Reader.EventOpcode Opcode `{`get;`}`
Task        Property   System.Diagnostics.Eventing.Reader.EventTask Task `{`get;`}`
Template    Property   string Template `{`get;`}`
Version     Property   byte Version `{`get;`}`
```

通过上面的输出我们发现每个事件都有一个LogLink属性，且属性值为System.Diagnostics.Eventing.Reader.EventLogLink ，下面我们来看看这些对象的值是如何形成的。



```
PS C:&gt; $WmiProv.Events[0].LogLink
LogName                              IsImported DisplayName
-------                              ---------- -----------
Microsoft-Windows-WMI-Activity/Trace      False
PS C:&gt; $WmiProv.Events[0].LogLink | gm
   TypeName: System.Diagnostics.Eventing.Reader.EventLogLink
Name        MemberType Definition
----        ---------- ----------
Equals      Method     bool Equals(System.Object obj)
GetHashCode Method     int GetHashCode()
GetType     Method     type GetType()
ToString    Method     string ToString()
DisplayName Property   string DisplayName `{`get;`}`
IsImported  Property   bool IsImported `{`get;`}`
LogName     Property   string LogName `{`get;`}`
```

执行下面这个命令可以筛选出我们想要查看的事件。



```
PS C:&gt; $WmiProv.Events | Where-Object `{`$_.LogLink.LogName -eq "Microsoft-Windows-WMI-Activity/Operational"`}`
Id          : 5857
Version     : 0
LogLink     : System.Diagnostics.Eventing.Reader.EventLogLink
Level       : System.Diagnostics.Eventing.Reader.EventLevel
Opcode      : System.Diagnostics.Eventing.Reader.EventOpcode
Task        : System.Diagnostics.Eventing.Reader.EventTask
Keywords    : `{``}`
Template    : &lt;template xmlns="http://schemas.microsoft.com/win/2004/08/events"&gt;
                &lt;data name="ProviderName" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="Code" inType="win:HexInt32" outType="win:HexInt32"/&gt;
                &lt;data name="HostProcess" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="ProcessID" inType="win:UInt32" outType="xs:unsignedInt"/&gt;
                &lt;data name="ProviderPath" inType="win:UnicodeString" outType="xs:string"/&gt;
              &lt;/template&gt;
Description : %1 provider started with result code %2. HostProcess = %3; ProcessID = %4; ProviderPath = %5
Id          : 5858
Version     : 0
LogLink     : System.Diagnostics.Eventing.Reader.EventLogLink
Level       : System.Diagnostics.Eventing.Reader.EventLevel
Opcode      : System.Diagnostics.Eventing.Reader.EventOpcode
Task        : System.Diagnostics.Eventing.Reader.EventTask
Keywords    : `{``}`
Template    : &lt;template xmlns="http://schemas.microsoft.com/win/2004/08/events"&gt;
                &lt;data name="Id" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="ClientMachine" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="User" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="ClientProcessId" inType="win:UInt32" outType="xs:unsignedInt"/&gt;
                &lt;data name="Component" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="Operation" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="ResultCode" inType="win:HexInt32" outType="win:HexInt32"/&gt;
                &lt;data name="PossibleCause" inType="win:UnicodeString" outType="xs:string"/&gt;
              &lt;/template&gt;
Description : Id = %1; ClientMachine = %2; User = %3; ClientProcessId = %4; Component = %5; Operation = %6; ResultCode = %7; PossibleCause = %8
Id          : 5859
Version     : 0
LogLink     : System.Diagnostics.Eventing.Reader.EventLogLink
Level       : System.Diagnostics.Eventing.Reader.EventLevel
Opcode      : System.Diagnostics.Eventing.Reader.EventOpcode
Task        : System.Diagnostics.Eventing.Reader.EventTask
Keywords    : `{``}`
Template    : &lt;template xmlns="http://schemas.microsoft.com/win/2004/08/events"&gt;
                &lt;data name="NamespaceName" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="Query" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="User" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="processid" inType="win:UInt32" outType="xs:unsignedInt"/&gt;
                &lt;data name="providerName" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="queryid" inType="win:UInt32" outType="xs:unsignedInt"/&gt;
                &lt;data name="PossibleCause" inType="win:UnicodeString" outType="xs:string"/&gt;
              &lt;/template&gt;
Description : Namespace = %1; NotificationQuery = %2; OwnerName = %3; HostProcessID = %4;  Provider= %5, queryID = %6; PossibleCause = %7
Id          : 5860
Version     : 0
LogLink     : System.Diagnostics.Eventing.Reader.EventLogLink
Level       : System.Diagnostics.Eventing.Reader.EventLevel
Opcode      : System.Diagnostics.Eventing.Reader.EventOpcode
Task        : System.Diagnostics.Eventing.Reader.EventTask
Keywords    : `{``}`
Template    : &lt;template xmlns="http://schemas.microsoft.com/win/2004/08/events"&gt;
                &lt;data name="NamespaceName" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="Query" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="User" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="processid" inType="win:UInt32" outType="xs:unsignedInt"/&gt;
                &lt;data name="MachineName" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="PossibleCause" inType="win:UnicodeString" outType="xs:string"/&gt;
              &lt;/template&gt;
Description : Namespace = %1; NotificationQuery = %2; UserName = %3; ClientProcessID = %4, ClientMachine = %5; PossibleCause = %6
Id          : 5861
Version     : 0
LogLink     : System.Diagnostics.Eventing.Reader.EventLogLink
Level       : System.Diagnostics.Eventing.Reader.EventLevel
Opcode      : System.Diagnostics.Eventing.Reader.EventOpcode
Task        : System.Diagnostics.Eventing.Reader.EventTask
Keywords    : `{``}`
Template    : &lt;template xmlns="http://schemas.microsoft.com/win/2004/08/events"&gt;
                &lt;data name="Namespace" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="ESS" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="CONSUMER" inType="win:UnicodeString" outType="xs:string"/&gt;
                &lt;data name="PossibleCause" inType="win:UnicodeString" outType="xs:string"/&gt;
              &lt;/template&gt;
Description : Namespace = %1; Eventfilter = %2 (refer to its activate eventid:5859); Consumer = %3; PossibleCause = %4
```

此时，我们可以看到与事件日志相关联的特定事件，而且我们还可以获取到每个事件的细节信息，其中包括消息的XML模板，该信息在我们编写XPath过滤器时是十分有用的。我们可以将它们保存到一个变量中，并从中获取事件的ID，具体操作如下所示：



```
PS C:&gt; $WmiEvents = $WmiProv.Events | Where-Object `{`$_.LogLink.LogName -eq "Microsoft-Windows-WMI-Activity/Operational"`}`
PS C:&gt; $WmiEvents | Select-Object -Property Id
  Id
  --
5857
5858
5859
5860
5861
```



**Provider加载过程**

****

每当WMI被初始化时，它将加载用于构建类的Provider程序，并向外界提供用来访问操作系统和系统组件的功能。这些功能都是在当前用户的SYSTEM上下文环境中执行的，也就是说，它们在Windows中将以非常高的特权执行。 因此，攻击者们通常会把恶意的Provider程序用作后门，以便能够持续的、高权限的对Windows操作系统进行访问。下面是一些恶意的Provider程序示例：

[**https://gist.github.com/subTee/c6bd1401504f9d4d52a0**](https://gist.github.com/subTee/c6bd1401504f9d4d52a0)** SubTee Shellcode Execution WMI Class**

[**https://github.com/jaredcatkinson/EvilNetConnectionWMIProvider**](https://github.com/jaredcatkinson/EvilNetConnectionWMIProvider)** Jared Atkinson Evil WMI Provider Example**

在事件ID列表中，我们注意到一个ID为5857的事件，该事件的结构中有一些非常有价值的信息，具体详情如下所示：

 [![](https://p5.ssl.qhimg.com/t018d6ce0dee7343d64.png)](https://p5.ssl.qhimg.com/t018d6ce0dee7343d64.png)

从上图结构信息中我们可以发现加载Provider程序的ProcessID和Thread信息，而且我们还可以看到主机进程的名称以及加载的DLL路径。如果我们使用Windows事件收集器，我们可以根据已知Provider创建一个XML过滤器，使用该过滤器可以对上述的输出结果执行过滤操作以获取未知的Provider程序，下面我们使用PowerShell生成一个简单的privider文件列表，具体输出如下所示：



```
PS C:&gt; Get-WinEvent -FilterHashtable @`{`logname='Microsoft-Windows-WMI-Activity/Operational';Id=5857`}` | % `{`$_.properties[4].value`}` | select -unique
%SystemRoot%system32wbemwbemcons.dll
%systemroot%system32wbemwmipiprt.dll
%systemroot%system32wbemwmiprov.dll
C:WindowsSystem32wbemkrnlprov.dll
%systemroot%system32wbemwmipcima.dll
C:WindowsSystem32wbemWmiPerfClass.dll
%SystemRoot%system32tscfgwmi.dll
%systemroot%system32wbemcimwin32.dll
%systemroot%system32wbemvdswmi.dll
%SystemRoot%System32sppwmi.dll
%systemroot%system32wbemWMIPICMP.dll
%SystemRoot%System32Win32_DeviceGuard.dll
%SYSTEMROOT%system32PowerWmiProvider.dll
%SystemRoot%System32storagewmi.dll
%systemroot%system32wbemstdprov.dll
%systemroot%system32profprov.dll
C:WindowsSystem32wbemWmiPerfInst.dll
%systemroot%system32wbemDMWmiBridgeProv.dll
C:WindowsSysWOW64wbemWmiPerfClass.dll
我们可以将其转换为XML过滤器，并使用Get-WinEvent或WEC进行事件日志的收集，具体操作如下所示：
&lt;QueryList&gt;
  &lt;Query Id="0" Path="Microsoft-Windows-WMI-Activity/Operational"&gt;
    &lt;Select Path="Microsoft-Windows-WMI-Activity/Operational"&gt;*[System[(EventID=5857)]]
    &lt;/Select&gt;
    &lt;Suppress Path="Microsoft-Windows-WMI-Activity/Operational"&gt;
    (*[UserData/*/ProviderPath='%systemroot%system32wbemwmiprov.dll']) or
    (*[UserData/*/ProviderPath='%systemroot%system32wbemwmipcima.dll']) or
    (*[UserData/*/ProviderPath='%SystemRoot%System32sppwmi.dll']) or
    (*[UserData/*/ProviderPath='%systemroot%system32wbemvdswmi.dll']) or
    (*[UserData/*/ProviderPath='%systemroot%system32wbemDMWmiBridgeProv.dll']) or
    (*[UserData/*/ProviderPath='C:WindowsSystem32wbemWmiPerfClass.dll']) or
    (*[UserData/*/ProviderPath='C:WindowsSystem32wbemkrnlprov.dll']) or
    (*[UserData/*/ProviderPath='%systemroot%system32wbemwmipiprt.dll']) or
    (*[UserData/*/ProviderPath='%systemroot%system32wbemstdprov.dll']) or
    (*[UserData/*/ProviderPath='%systemroot%system32profprov.dll']) or
    (*[UserData/*/ProviderPath='%SystemRoot%System32Win32_DeviceGuard.dll']) or
    (*[UserData/*/ProviderPath='%SystemRoot%System32smbwmiv2.dll']) or
    (*[UserData/*/ProviderPath='%systemroot%system32wbemcimwin32.dll']) or
    (*[UserData/*/ProviderPath='%systemroot%system32wbemwmiprvsd.dll']) or
    (*[UserData/*/ProviderPath='%SystemRoot%system32wbemscrcons.exe']) or
    (*[UserData/*/ProviderPath='%SystemRoot%system32wbemwbemcons.dll']) or
    (*[UserData/*/ProviderPath='%systemroot%system32wbemvsswmi.dll']) or
    (*[UserData/*/ProviderPath='%SystemRoot%system32tscfgwmi.dll']) or
    (*[UserData/*/ProviderPath='%systemroot%system32wbemServerManager.DeploymentProvider.dll']) or
    (*[UserData/*/ProviderPath='%systemroot%system32wbemmgmtprovider.dll']) or
    (*[UserData/*/ProviderPath='%systemroot%system32wbemntevt.dll']) or
    (*[UserData/*/ProviderPath='%SYSTEMROOT%System32wbemDnsServerPsProvider.dll'])
    &lt;/Suppress&gt;
    &lt;Suppress Path="Microsoft-Windows-WMI-Activity/Operational"&gt;
    (*[UserData/*/ProviderPath='%windir%system32wbemservercompprov.dll']) or
    (*[UserData/*/ProviderPath='C:WindowsSystem32wbemWmiPerfInst.dll'])
    &lt;/Suppress&gt;
  &lt;/Query&gt;&lt;/QueryList&gt;
```



**WMI查询错误**

****

Id为5858的EventLog记录了WMI中所有的查询错误信息，这些信息包括错误代码（ResultCode标签）和引起错误的原因（Operation标签），还包括进程Pid，该字段信息位于ClientProcessId标签中，具体信息如下图所示：

 [![](https://p2.ssl.qhimg.com/t016ce122cad7e6abb8.png)](https://p2.ssl.qhimg.com/t016ce122cad7e6abb8.png)

从上图可以看出错误代码是十六进制格式的，不过[微软在MSDN](https://msdn.microsoft.com/en-us/library/aa394559(v=vs.85).aspx)中列出了WMI所有的错误常量，我们可以用它来确定具体的错误信息。 我们可以使用XPathFilter轻松查询特定的结果代码。在以下这个示例中，我们通过搜索ResultCode 0x80041010来查找失败的查询请求 ，该操作可以用来确定攻击者是否正在寻找系统上存在的特定类，具体如下所示：

```
PS C:&gt; Get-WinEvent -FilterXPath "*[UserData/*/ResultCode='0x80041010']" -LogName "Microsoft-Windows-WMI-Activity/Operational"
```

我们还可以搜索由于权限不足而失败的查询，具体搜索如下所示：

```
PS C：&gt; Get-WinEvent -FilterXPath“* [UserData / * / ResultCode ='0x80041003']”-LogName“Microsoft-Windows-WMI-Activity / Operational”
```



**WMI事件**

****

WMI事件定义是当创建特定事件类实例或直接在WMI模型定义的一类事件，可以通过监视Windows中CIM数据库生成的特定事件来完成事件的操作。 大多数事件会创建一个查询请求，该请求中定义了我们需要执行的操作，一旦事件发生就会执行我们定义的操作，目前WMI支持两种类型的事件：

临时事件：只要创建事件的进程处于活动状态，临时事件就会被激活。 （他们在进程的特权下运行）

持久事件：事件存储在CIM数据库中，并且会一直处于活动状态，直到从数据库中将它移除。 （它们总是作为SYSTEM运行）

<br>

**临时事件**

****

由于某些工具在实现上往往使用临时事件，因此一些人认为持久性WMI事件更容易被检测，这些工具通常情况下使用C ++，.Net，WSH或者PowerShell编写，它们允许使用WMI事件过滤器来触发应该由应用程序自己执行的操作。 我们可以使用Id 为5860的事件来跟踪这些操作。一旦应用程序注册事件消费者，事件日志就会被创建。

下面是一个临时事件消费者的一个示例，在示例中它简单地写入已经启动的进程名称。



```
# Query for new process events 
$queryCreate = "SELECT * FROM __InstanceCreationEvent WITHIN 5" + 
    "WHERE TargetInstance ISA 'Win32_Process'" 
# Create an Action
$CrateAction = `{`
    $name = $event.SourceEventArgs.NewEvent.TargetInstance.name
    write-host "Process $($name) was created."
`}`
# Register WMI event 
Register-WMIEvent -Query $queryCreate -Action $CrateAction
```

当事件消费者注册到Register-WmiEvent时，我们会在系统上记录下列事件。

 [![](https://p0.ssl.qhimg.com/t01378e356e4db0c220.png)](https://p0.ssl.qhimg.com/t01378e356e4db0c220.png)

我们可以看到用于监视事件的查询请求被记录在UserData下的Query元素中，而在PlaussibleCause元素中，我们看到它被标记为Temporary。

<br>

**持久事件**

****

当在WMI CIM数据库中创建一个持久事件时，系统同时还会创建Id为5861的事件日志条目，该事件也会在任何组件类实例被修改时被创建，该事件将包含所有与持久性相关的信息，如下图中的“PossibleCause ”子元素所示：

  [![](https://p5.ssl.qhimg.com/t013d479bd7650ce1b5.png)](https://p5.ssl.qhimg.com/t013d479bd7650ce1b5.png)

当修改构成持久事件的__EventFilter或Consumer时，系统会生成相同的一个事件，但数据中并没有字段用来显示此事件是否被修改。也可以通过Id 为5859的事件来查看构成持久事件的__EventFilter类，但是在我所有测试中，我还没有看到使用此Id创建的事件。

<br>

**结论**

****

正如我们本文中所阐述的，在最新版本的Windows中，通过加入一些日志功能，微软已经改进了WMI的一些安全性。但是，这些功能还没有被加入到Windows 7和Windows 2008/2008 R2操作系统中去。 因此，针对这些系统，我们需要去能够跟踪以下信息：

**错误的查询请求；**

**临时事件的创建；**

**持久事件的创建与修改；**

**Provider的加载。**

从“攻击者”的视角来看，这让我们知道我们的行为可以被跟踪，当我们在实施某些恶意的行为操作时，我们应该看看这些事件是否会被收集。从“防守者”的角度来看，我们应该在系统环境中收集和分析上述这些事件的信息以用于分析哪些是可能的恶意行为事件。
