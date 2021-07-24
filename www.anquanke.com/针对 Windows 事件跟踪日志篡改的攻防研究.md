> 原文链接: https://www.anquanke.com//post/id/168733 


# 针对 Windows 事件跟踪日志篡改的攻防研究


                                阅读量   
                                **282516**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者palantir，文章来源：medium.com
                                <br>原文地址：[https://medium.com/palantir/tampering-with-windows-event-tracing-background-offense-and-defense-4be7ac62ac63](https://medium.com/palantir/tampering-with-windows-event-tracing-background-offense-and-defense-4be7ac62ac63)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p5.ssl.qhimg.com/t014101cb4359ed9426.png)](https://p5.ssl.qhimg.com/t014101cb4359ed9426.png)



## 前言

[Windows事件跟踪](https://blogs.msdn.microsoft.com/ntdebugging/2009/08/27/part-1-etw-introduction-and-overview/)(Event Tracing for Windows,ETW)是Windows用于跟踪和记录系统事件的机制。攻击者经常通过清除事件日志来掩盖他们的踪迹。虽然清除事件日志会生成事件，但熟悉ETW的攻击者可能会利用篡改技术暂时中止甚至永久停止日志记录，并且整个过程不会生成任何事件日志。

Windows事件日志是Palantir应急小组的[警报和检测策略](https://medium.com/palantir/alerting-and-detection-strategy-framework-52dc33722df2)的数据源，因此熟悉事件日志篡改操作对我们至关重要。我们不断地评估关于事件数据源完整性的假设，记录盲点，并调整实现。这篇文章的目的是与社区分享ETW背景和基础知识、事件日志篡改技术和检测策略。



## ETW和事件日志

[ETW结构](https://docs.microsoft.com/en-us/windows/desktop/etw/about-event-tracing)分为三个部分：事件提供者(provider)、事件消费者(consumers)和事件跟踪会话(tracing session)。跟踪会话负责从提供者收集事件，并传送到日志文件和消费者。会话由控制者(controller)创建和配置，比如内置的logman.exe命令行工具。下面是一些常用的命令，用于搜索现有的跟踪会话和各自的ETW提供者；请注意，这些命令通常需要足够的权限才能运行。

### <a class="reference-link" name="%E5%88%97%E5%87%BA%E6%89%80%E6%9C%89%E6%AD%A3%E5%9C%A8%E8%BF%90%E8%A1%8C%E7%9A%84%E8%B7%9F%E8%B8%AA%E4%BC%9A%E8%AF%9D"></a>列出所有正在运行的跟踪会话

```
&gt; logman query -ets
Data Collector Set                Type    Status
-------------------------------------------------
Circular Kernel Context Logger    Trace   Running
AppModel                          Trace   Running
ScreenOnPowerStudyTraceSession    Trace   Running
DiagLog                           Trace   Running
EventLog-Application              Trace   Running
EventLog-System                   Trace   Running
LwtNetLog                         Trace   Running
NtfsLog                           Trace   Running
TileStore                         Trace   Running
UBPM                              Trace   Running
WdiContextLog                     Trace   Running
WiFiSession                       Trace   Running
UserNotPresentTraceSession        Trace   Running
Diagtrack-Listener                Trace   Running
MSDTC_TRACE_SESSION               Trace   Running
WindowsUpdate_trace_log           Trace   Running
```

### <a class="reference-link" name="%E5%88%97%E5%87%BA%E6%89%80%E6%9C%89%E8%AE%A2%E9%98%85%E8%B7%9F%E8%B8%AA%E4%BC%9A%E8%AF%9D%E7%9A%84%E6%8F%90%E4%BE%9B%E8%80%85"></a>列出所有订阅跟踪会话的提供者

```
&gt; logman query "EventLog-Application" -ets
Name:                 EventLog-Application
Status:               Running
Root Path:            %systemdrive%PerfLogsAdmin
Segment:              Off
Schedules:            On
Segment Max Size:     100 MB

Name:                 EventLog-ApplicationEventLog-Application
Type:                 Trace
Append:               Off
Circular:             Off
Overwrite:            Off
Buffer Size:          64
Buffers Lost:         0
Buffers Written:      242
Buffer Flush Timer:   1
Clock Type:           System
File Mode:            Real-time

Provider:
Name:                 Microsoft-Windows-SenseIR
Provider Guid:        `{`B6D775EF-1436-4FE6-BAD3-9E436319E218`}`
Level:                255
KeywordsAll:          0x0
KeywordsAny:          0x8000000000000000 (Microsoft-Windows-SenseIR/Operational)
Properties:           65
Filter Type:          0

Provider:
Name:                 Microsoft-Windows-WDAG-Service
Provider Guid:        `{`728B02D9-BF21-49F6-BE3F-91BC06F7467E`}`
Level:                255
KeywordsAll:          0x0
KeywordsAny:          0x8000000000000000
Properties:           65
Filter Type:          0

...

Provider:
Name:                 Microsoft-Windows-PowerShell
Provider Guid:        `{`A0C1853B-5C40-4B15-8766-3CF1C58F985A`}`
Level:                255
KeywordsAll:          0x0
KeywordsAny:          0x9000000000000000 (Microsoft-Windows-PowerShell/Operational,Microsoft-Windows-PowerShell/Admin)
Properties:           65
Filter Type:          0
```

该命令详细说明了跟踪会话的配置，还有每个订阅会话的提供者的配置，包括以下参数：
- Name: 提供者的名称。提供者只有在有已注册的manifest的情况下才有名称，但它始终具有唯一的GUID。
- Provider GUID: 提供者的GUID。在对特定提供者进行分析或操作时，GUID和（或）提供者的名称非常有用。
- Level: 指定日志记录级别。标准的日志记录级别是：0-Log Always；1- Critical；2-Error；3-Warning；4- Informational；5-Verbose。也可以自定义日志记录级别，但级别6-15是保留的。每个ORing级别可以捕获多个日志记录级别；通常使用255(0xFF)捕获所有支持的日志记录级别。
- KeywordsAll: 关键字用于筛选特定类别的事件。日志记录级别用于按事件详细/重要性进行筛选，而关键字允许按事件类别进行筛选。关键字对应于特定的位值。所有这些都表明，对于由KeywordsAny匹配的给定关键字，应该根据KeywordsAll中的特定位掩码进行进一步的筛选。这个字段通常设置为零。在[这里](https://docs.microsoft.com/en-us/windows/desktop/wes/defining-keywords-used-to-classify-types-of-events)可以找到更多信息。
<li>KeywordsAny：基于指定的任意关键字组合启用筛选。这可以看作是逻辑或，而KeywordsAll是逻辑和。低位的6个字节指定特定提供者的关键字。高位的两个字节是在Windows SDK中的WinMeta.xml中保留和定义的。例如，在与事件日志相关的跟踪会话中，可以看到设置为特定值的高位字节。这对应于下面的一个或多个事件通道：
<pre><code class="hljs">  0x01 - Admin channel
  0x02 - Debug channel
  0x04 - Analytic channel
  0x08 - Operational channel
</code></pre>
</li>
<li>Properties: 在写入事件时可以指定的可选ETW属性。目前支持的值(更多信息查看[这里](https://docs.microsoft.com/en-us/windows/desktop/ETW/enable-trace-parameters))：
<pre><code class="hljs">  0x001 - EVENT_ENABLE_PROPERTY_SID
  0x002 - EVENT_ENABLE_PROPERTY_TS_ID
  0x004 - EVENT_ENABLE_PROPERTY_STACK_TRACE
  0x008 - EVENT_ENABLE_PROPERTY_PSM_KEY
  0x010 - EVENT_ENABLE_PROPERTY_IGNORE_KEYWORD_0
  0x020 - EVENT_ENABLE_PROPERTY_PROVIDER_GROUP
  0x040 - EVENT_ENABLE_PROPERTY_ENABLE_KEYWORD_0
  0x080 - EVENT_ENABLE_PROPERTY_PROCESS_START_KEY
  0x100 - EVENT_ENABLE_PROPERTY_EVENT_KEY
  0x200 - EVENT_ENABLE_PROPERTY_EXCLUDE_INPRIVATE
</code></pre>
从检测的角度来看，`EVENT_ENABLE_PROPERTY_SID`、`EVENT_ENABLE_PROPERTY_TS_ID`、`EVENT_ENABLE_PROPERTY_PROCESS_START_KEY`是值得收集的字段。例如，`EVENT_ENABLE_PROPERTY_PROCESS_START_KEY`生成唯一标识进程的值。注意，Process ID不是进程实例的唯一标识符。
</li>
- 筛选器（Filter Type）：提供者可以选择其他筛选；支持的筛选器是在提供者manifest中定义的。实际上在所有注册的提供者上运行[TdhEnumerateProviderFilters](https://docs.microsoft.com/en-us/windows/desktop/api/tdh/nf-tdh-tdhenumerateproviderfilters)时，内置提供者都没有运行过滤器。eventprov.h(在Windows SDK中)中的一些预定义的筛选器类型：
```
0x00000000 - EVENT_FILTER_TYPE_NONE
0x80000000 - EVENT_FILTER_TYPE_SCHEMATIZED
0x80000001 - EVENT_FILTER_TYPE_SYSTEM_FLAGS
0x80000002 - EVENT_FILTER_TYPE_TRACEHANDLE
0x80000004 - EVENT_FILTER_TYPE_PID
0x80000008 - EVENT_FILTER_TYPE_EXECUTABLE_NAME
0x80000010 - EVENT_FILTER_TYPE_PACKAGE_ID
0x80000020 - EVENT_FILTER_TYPE_PACKAGE_APP_ID
0x80000100 - EVENT_FILTER_TYPE_PAYLOAD
0x80000200 - EVENT_FILTER_TYPE_EVENT_ID
0x80000400 - EVENT_FILTER_TYPE_EVENT_NAME
0x80001000 - EVENT_FILTER_TYPE_STACKWALK
0x80002000 - EVENT_FILTER_TYPE_STACKWALK_NAME
0x80004000 - EVENT_FILTER_TYPE_STACKWALK_LEVEL_KW
```

### <a class="reference-link" name="%E5%88%97%E5%87%BA%E6%89%80%E6%9C%89%E5%B7%B2%E6%B3%A8%E5%86%8C%E7%9A%84ETW%E6%8F%90%E4%BE%9B%E8%80%85"></a>列出所有已注册的ETW提供者

`logman query providers`命令列出所有已注册的ETW提供者，还有它们的名称和GUID。如果将二进制manifest保存在`HKLMSOFTWAREMicrosoftWindowsCurrentVersionWINEVTPublishers`{`PROVIDER_GUID`}``注册表项中，则将注册ETW提供者。例如，`Microsoft-Windows-PowerShell`提供者具有以下注册表值：

[![](https://p5.ssl.qhimg.com/t01c62fc127b2b04094.png)](https://p5.ssl.qhimg.com/t01c62fc127b2b04094.png)

ETW和事件日志知道如何根据在`ResourceFileName`注册表值中列出的二进制文件中的`WEVT_TEMPLATE`的序列化二进制信息正确地解析事件信息并向用户显示事件信息。该资源是[工具清单(instrumentation manifest)](https://docs.microsoft.com/en-us/windows/desktop/wes/writing-an-instrumentation-manifest)的二进制表示。我们没有关于`WEVT_Template`二进制结构的说明文档，但至少有两个工具可用于帮助解析和恢复事件模式(event schema)：[WEPExplorer](https://github.com/lallousx86/WEPExplorer)和[Perfview](https://github.com/Microsoft/perfview)。

### <a class="reference-link" name="%E5%8D%95%E7%8B%AC%E6%9F%A5%E7%9C%8B%E6%8F%90%E4%BE%9B%E8%80%85"></a>单独查看提供者

logman打印提供者的基本信息。例如：

```
&gt; logman query providers Microsoft-Windows-PowerShell
Provider                        GUID
----------------------------------------------------------------------
Microsoft-Windows-PowerShell    `{`A0C1853B-5C40-4B15-8766-3CF1C58F985A`}`

Value               Keyword              Description
----------------------------------------------------------------------
0x0000000000000001  Runspace             PowerShell Runspace
0x0000000000000002  Pipeline             Pipeline of Commands
0x0000000000000004  Protocol             PowerShell remoting protocol
0x0000000000000008  Transport            PowerShell remoting transport
0x0000000000000010  Host                 PowerShell remoting host proxy calls
0x0000000000000020  Cmdlets              All remoting cmdlets
0x0000000000000040  Serializer           The serialization layer
0x0000000000000080  Session              All session layer
0x0000000000000100  Plugin               The managed PowerShell plugin worker
0x0000000000000200  PSWorkflow           PSWorkflow Hosting And Execution Layer
0x0001000000000000  win:ResponseTime     Response Time
0x8000000000000000  Microsoft-Windows-PowerShell/Operational Microsoft-Windows-PowerShell/Operational
0x4000000000000000  Microsoft-Windows-PowerShell/Analytic Microsoft-Windows-PowerShell/Analytic
0x2000000000000000  Microsoft-Windows-PowerShell/Debug Microsoft-Windows-PowerShell/Debug
0x1000000000000000  Microsoft-Windows-PowerShell/Admin Microsoft-Windows-PowerShell/Admin

Value        Level                Description
--------------------------------------------------------------------
0x02         win:Error            Error
0x03         win:Warning          Warning
0x04         win:Informational    Information
0x05         win:Verbose          Verbose
0x14         Debug                Debug level defined by PowerShell (which is above Informational defined by system)

PID          Image
----------------------------------------------------------------------
0x00000730   C:WindowsSystem32WindowsPowerShellv1.0powershell.exe
0x0000100c   C:WindowsSystem32WindowsPowerShellv1.0powershell.exe
```

结果显示了可用的关键字和日志记录值，以及通过该提供者注册发出事件的所有进程。这些输出对于了解现有跟踪会话如何在提供者上筛选非常有用，还有助于初步发现其他有趣的信息，这些信息可以通过ETW跟踪收集。

特别要注意的是，PowerShell提供者似乎支持基于在定义的关键字中的保留关键字进行日志记录。并不是所有的ETW提供者都用于事件日志；相反，许多ETW提供者只是用于低级别的跟踪、调试和最近应用的安全测试。例如，Windows Defender Advanced Threat Protection严重依赖ETW作为补充的检测数据源。

### <a class="reference-link" name="%E6%9F%A5%E7%9C%8B%E6%89%80%E6%9C%89%E6%8E%A5%E6%94%B6%E7%89%B9%E5%AE%9A%E8%BF%9B%E7%A8%8B%E4%BA%8B%E4%BB%B6%E7%9A%84%E6%8F%90%E4%BE%9B%E8%80%85"></a>查看所有接收特定进程事件的提供者

另一种发现目标提供者的方法是查看所有接收特定进程事件的提供者。例如，下面显示了与`MsMpEng.exe`(Windows Defender服务，在本例中通过PID 5244运行)相关的所有提供者：

```
&gt; logman query providers -pid 5244
Provider                                 GUID
-------------------------------------------------------------------------------
FWPUCLNT Trace Provider                  `{`5A1600D2-68E5-4DE7-BCF4-1C2D215FE0FE`}`
Microsoft-Antimalware-Protection         `{`E4B70372-261F-4C54-8FA6-A5A7914D73DA`}`
Microsoft-Antimalware-RTP                `{`8E92DEEF-5E17-413B-B927-59B2F06A3CFC`}`
Microsoft-Antimalware-Service            `{`751EF305-6C6E-4FED-B847-02EF79D26AEF`}`
Microsoft-IEFRAME                        `{`5C8BB950-959E-4309-8908-67961A1205D5`}`
Microsoft-Windows-AppXDeployment         `{`8127F6D4-59F9-4ABF-8952-3E3A02073D5F`}`
Microsoft-Windows-ASN1                   `{`D92EF8AC-99DD-4AB8-B91D-C6EBA85F3755`}`
Microsoft-Windows-AsynchronousCausality  `{`19A4C69A-28EB-4D4B-8D94-5F19055A1B5C`}`
Microsoft-Windows-CAPI2                  `{`5BBCA4A8-B209-48DC-A8C7-B23D3E5216FB`}`
Microsoft-Windows-COM-Perf               `{`B8D6861B-D20F-4EEC-BBAE-87E0DD80602B`}`
Microsoft-Windows-COM-RundownInstrumentation `{`2957313D-FCAA-5D4A-2F69-32CE5F0AC44E`}`
Microsoft-Windows-COMRuntime             `{`BF406804-6AFA-46E7-8A48-6C357E1D6D61`}`
Microsoft-Windows-Crypto-BCrypt          `{`C7E089AC-BA2A-11E0-9AF7-68384824019B`}`
Microsoft-Windows-Crypto-NCrypt          `{`E8ED09DC-100C-45E2-9FC8-B53399EC1F70`}`
Microsoft-Windows-Crypto-RSAEnh          `{`152FDB2B-6E9D-4B60-B317-815D5F174C4A`}`
Microsoft-Windows-Deplorch               `{`B9DA9FE6-AE5F-4F3E-B2FA-8E623C11DC75`}`
Microsoft-Windows-DNS-Client             `{`1C95126E-7EEA-49A9-A3FE-A378B03DDB4D`}`
Microsoft-Windows-Heap-Snapshot          `{`901D2AFA-4FF6-46D7-8D0E-53645E1A47F5`}`
Microsoft-Windows-Immersive-Shell-API    `{`5F0E257F-C224-43E5-9555-2ADCB8540A58`}`
Microsoft-Windows-Kernel-AppCompat       `{`16A1ADC1-9B7F-4CD9-94B3-D8296AB1B130`}`
Microsoft-Windows-KnownFolders           `{`8939299F-2315-4C5C-9B91-ABB86AA0627D`}`
Microsoft-Windows-MPS-CLNT               `{`37945DC2-899B-44D1-B79C-DD4A9E57FF98`}`
Microsoft-Windows-Networking-Correlation `{`83ED54F0-4D48-4E45-B16E-726FFD1FA4AF`}`
Microsoft-Windows-NetworkProfile         `{`FBCFAC3F-8459-419F-8E48-1F0B49CDB85E`}`
Microsoft-Windows-RPC                    `{`6AD52B32-D609-4BE9-AE07-CE8DAE937E39`}`
Microsoft-Windows-RPC-Events             `{`F4AED7C7-A898-4627-B053-44A7CAA12FCD`}`
Microsoft-Windows-Schannel-Events        `{`91CC1150-71AA-47E2-AE18-C96E61736B6F`}`
Microsoft-Windows-Shell-Core             `{`30336ED4-E327-447C-9DE0-51B652C86108`}`
Microsoft-Windows-URLMon                 `{`245F975D-909D-49ED-B8F9-9A75691D6B6B`}`
Microsoft-Windows-User Profiles General  `{`DB00DFB6-29F9-4A9C-9B3B-1F4F9E7D9770`}`
Microsoft-Windows-User-Diagnostic        `{`305FC87B-002A-5E26-D297-60223012CA9C`}`
Microsoft-Windows-WebIO                  `{`50B3E73C-9370-461D-BB9F-26F32D68887D`}`
Microsoft-Windows-Windows Defender       `{`11CD958A-C507-4EF3-B3F2-5FD9DFBD2C78`}`
Microsoft-Windows-WinHttp                `{`7D44233D-3055-4B9C-BA64-0D47CA40A232`}`
Microsoft-Windows-WinRT-Error            `{`A86F8471-C31D-4FBC-A035-665D06047B03`}`
Microsoft-Windows-Winsock-NameResolution `{`55404E71-4DB9-4DEB-A5F5-8F86E46DDE56`}`
Network Profile Manager                  `{`D9131565-E1DD-4C9E-A728-951999C2ADB5`}`
Security: SChannel                       `{`37D2C3CD-C5D4-4587-8531-4696C44244C8`}`
Windows Defender Firewall API            `{`28C9F48F-D244-45A8-842F-DC9FBC9B6E92`}`
WMI_Tracing                              `{`1FF6B227-2CA7-40F9-9A66-980EADAA602E`}`
WMI_Tracing_Client_Operations            `{`8E6B6962-AB54-4335-8229-3255B919DD0E`}`
`{`05F95EFE-7F75-49C7-A994-60A55CC09571`}`   `{`05F95EFE-7F75-49C7-A994-60A55CC09571`}`
`{`072665FB-8953-5A85-931D-D06AEAB3D109`}`   `{`072665FB-8953-5A85-931D-D06AEAB3D109`}`
`{`7AF898D7-7E0E-518D-5F96-B1E79239484C`}`   `{`7AF898D7-7E0E-518D-5F96-B1E79239484C`}`
... output truncated ...
```

带有GUID的是缺少manifest的提供者。它们通常与[WPP](https://docs.microsoft.com/en-us/windows-hardware/drivers/devtest/wpp-software-tracing)或[TraceLogging](https://docs.microsoft.com/en-us/windows/desktop/tracelogging/trace-logging-portal)有关，这些都超出了本文的范围。可以检索这些提供者类型的名称和事件元数据。例如，下面是解析后一些上面未命名提供者的名称：
- 05F95EFE-7F75–49C7-A994–60A55CC09571 Microsoft.Windows.Kernel.KernelBase
- 072665FB-8953–5A85–931D-D06AEAB3D109 Microsoft.Windows.ProcessLifetimeManage
- 7AF898D7–7E0E-518D-5F96-B1E79239484C Microsoft.Windows.Defender


## 事件提供者的内部

查看内置Windows二进制文件中的ETW相关代码，可以帮助你了解ETW事件是如何构造的，以及它们是如何在事件日志中显示的。下面是两个示例，`System.Management.Automation.dll`(PowerShell程序集核心)和`amsi.dll`。

### <a class="reference-link" name="System.Management.Automation.dll%E4%BA%8B%E4%BB%B6%E8%B7%9F%E8%B8%AA"></a>System.Management.Automation.dll事件跟踪

PowerShell v.5最大的安全特性之一是[scriptblock autologging](https://blogs.msdn.microsoft.com/powershell/2015/06/09/powershell-the-blue-team/)；启用后，如果脚本包含任何可疑代码，则在`Microsoft-Windows-PowerShell/Operational`事件日志中自动记录脚本内容和事件ID 4104(警告级别)。执行以下C#代码以生成事件日志：

```
if (scriptBlock._scriptBlockData.HasSuspiciousContent)
`{`
  PSEtwLog.LogOperationalWarning(PSEventId.ScriptBlock_Compile_Detail, PSOpcode.Create, PSTask.ExecuteCommand, PSKeyword.UseAlwaysAnalytic, new object[]
  `{`
    segment + 1,
    segments,
    textToLog,
    scriptBlock.Id.ToString(),
    scriptBlock.File ?? string.Empty
  `}`);
`}`
```

LogOperationalWarning方法实现如下：

```
internal static void LogOperationalInformation(PSEventId id, PSOpcode opcode, PSTask task, PSKeyword keyword, params object[] args)
`{`
  PSEtwLog.provider.WriteEvent(id, PSChannel.Operational, opcode, PSLevel.Informational, task, keyword, args);
`}`
```

WriteEvent方法实现如下：

```
internal void WriteEvent(PSEventId id, PSChannel channel, PSOpcode opcode, PSLevel level, PSTask task, PSKeyword keyword, params object[] args)
`{`
  long keywords;
  if (keyword == PSKeyword.UseAlwaysAnalytic || keyword == PSKeyword.UseAlwaysOperational) `{`
    keywords = 0L;
  `}` else `{`
    keywords = (long)keyword;
  `}`

  EventDescriptor eventDescriptor = new EventDescriptor((int)id, 1, (byte)channel, (byte)level, (byte)opcode, (int)task, keywords);
  PSEtwLogProvider.etwProvider.WriteEvent(ref eventDescriptor, args);
`}`
```

最后整理事件信息，并调用[EventWriteTransfer](https://docs.microsoft.com/en-us/windows/desktop/api/evntprov/nf-evntprov-eventwritetransfer)，将事件数据发送给Microsoft-Windows-PowerShell提供者。

发送<br>
给`EventWriteTransfer`的相关数据如下：
<li>Microsoft-Windows-PowerShell提供者的GUID: ``{`A0C1853B-5C40-4b15-8766-3CF1C58F985A`}``
</li>
<li>Event ID: `PSEventId.ScriptBlock_Compile_Detail - 4104`
</li>
- 通道值（Channel value）：`PSChannel.Operational - 16`，使用通道值表明提供者将被事件日志一起使用。[这里](https://github.com/PowerShell/PowerShell-Native/blob/master/src/PowerShell.Core.Instrumentation/PowerShell.Core.Instrumentation.man#L2194-L2202)可以查看PowerShell ETW manifest的通道定义。当未提供显式通道值时，[Message Compiler](https://docs.microsoft.com/en-us/windows/desktop/wes/message-compiler--mc-exe-)(mc.exe)将分配从16开始的默认值。由于首先定义了操作通道，因此分配了16条。
<li>Opcode值（Opcode value）: `PSOpcode.Create - 15`
</li>
<li>日志记录级别（Logging Level）: `PSLevel.Warning - 3`
</li>
<li>任务值（Task value）: `PSTask.CommandStart-102`
</li>
- 关键字值（Keyword value）:`PSKeyword.UseAlwaysAnalytic-0x40000000000000`。如上面的代码块所示，这个值之后被转换为0。通常情况下，不会记录这个事件，但是因为应用程序事件日志跟踪会话为其所有提供者设置了`EVENT_ENABLE_PROPERTY_ENABLE_KEYWORD_0 Enable`，尽管未指定关键字值，但所有提供者都将记录该事件。
- 事件数据（Event data）：代码内容和事件字段
PowerShell ETW提供者接收到事件后，事件日志服务将解析二进制`WEVT_TEMPLATE` schema([原始XML schema](https://github.com/PowerShell/PowerShell-Native/blob/master/src/PowerShell.Core.Instrumentation/PowerShell.Core.Instrumentation.man))，并显示可读的、已解析的事件属性/字段：

[![](https://p0.ssl.qhimg.com/t01312c24efc36f29b4.png)](https://p0.ssl.qhimg.com/t01312c24efc36f29b4.png)

### <a class="reference-link" name="amsi.dll%E4%BA%8B%E4%BB%B6%E8%B7%9F%E8%B8%AA"></a>amsi.dll事件跟踪

你可能已经注意到Windows 10有一个通常为空的AMSI/Operational事件日志。要理解为什么没有将事件记录到该事件日志，必须首先检查数据如何被输入AMSI ETW提供者(`Microsoft-Antimalware-Scan-Interface - `{`2A576B87-09A7-520E-C21A-4942F0271D67`}``)，然后观察事件日志跟踪会话(`EventLog-Application`)如何订阅AMSI ETW提供者。我们首先查看事件日志中的提供者注册情况。使用以下PowerShell命令查看：

```
&gt; Get-EtwTraceProvider -SessionName EventLog-Application -Guid '`{`2A576B87-09A7-520E-C21A-4942F0271D67`}`'
SessionName     : EventLog-Application
Guid            : `{`2A576B87-09A7-520E-C21A-4942F0271D67`}`
Level           : 255
MatchAnyKeyword : 0x8000000000000000
MatchAllKeyword : 0x0
EnableProperty  : `{`EVENT_ENABLE_PROPERTY_ENABLE_KEYWORD_0, EVENT_ENABLE_PROPERTY_SID`}`
```

注意下面的信息：
- 捕获操作通道事件(由MatchAnyKeyword值的0x8000000000000000设置)
- 捕获所有日志记录级别
- 即使事件关键字值为零，也应该捕获事件，通过`EVENT_ENABLE_PROPERTY_ENABLE_KEYWORD_0`设置。
这些信息本身并不说明为什么AMSI事件不被记录，但它提供了在检查amsi.dll如何将事件写入ETW时所需的上下文信息。把amsi.dl加载到IDA中，我们可以看到`CAmsiAntimalware::GenerateEtwEvent`函数中有一个对`EventWrite`函数的调用：

[![](https://p3.ssl.qhimg.com/t01814b522366f5bb91.png)](https://p3.ssl.qhimg.com/t01814b522366f5bb91.png)

调用`EventWrite`的相关部分是`EventDescriptor`参数。以下是一些关于将`EVENT_DESCRIPTOR`结构类型应用于`_AMSI_SCANBUFFER`的信息：

[![](https://p0.ssl.qhimg.com/t013d195b3005847acd.png)](https://p0.ssl.qhimg.com/t013d195b3005847acd.png)

EventDescriptor上下文提供了相关信息：
- 事件ID（Event ID）：1101(0x44D)，事件的详细信息可以从提取的manifest中获取，[这里](https://gist.github.com/mattifestation/6b3bbbea56cfc01bbfed9f74d94db618#file-microsoft-antimalware-scan-interface-manifest-xml-L12-L25)。
- 通道（Channel）：16(0x10)，操作事件日志通道
- 级别（Level）：4(Informational)
- 关键词（Keyword）：0x80000000000001(AMSI/Operationor Event1)。这些值是通过运行`logman query providers Microsoft-Antimalware-Scan-Interface`命令得到的。
现在我们了解到，1101事件没有被记录到`ApplicationEvent`日志，因为它只考虑关键字值与`0x8000000000000000`匹配的事件。为了解决这个问题并将事件写入事件日志，需要修改事件日志跟踪会话(不建议使用，并且需要SYSTEM权限)，也可以创建自己的持久跟踪会话(例如[autologger](https://docs.microsoft.com/en-us/windows/desktop/etw/configuring-and-starting-an-autologger-session))，以便在事件日志中捕获AMSI事件。下面的PowerShell脚本创建这样一个跟踪会话：

```
$AutoLoggerGuid = "`{`$((New-Guid).Guid)`}`"
New-AutologgerConfig -Name MyCustomAutoLogger -Guid $AutoLoggerGuid -Start Enabled
Add-EtwTraceProvider -AutologgerName MyCustomAutoLogger -Guid '`{`2A576B87-09A7-520E-C21A-4942F0271D67`}`' -Level 0xff -MatchAnyKeyword 0x80000000000001 -Property 0x41
```

运行上述命令后，重新启动，将开始写入AMSI事件日志。

[![](https://p4.ssl.qhimg.com/t01a87dee9f0602bf52.png)](https://p4.ssl.qhimg.com/t01a87dee9f0602bf52.png)

逆向分析显示，`scanResult`字段引用的是`AMSI_RESULT` enum，在本例中，32768映射到`AMSI_RESULT_DETECTED`，这表明缓冲区(内容字段中的Unicode编码缓冲区)被确定为是恶意的。

如果不了解ETW的内部结构，防御者就无法确定是否可以将额外的数据源(在本例中为AMSI日志)输入到事件日志中。同时不得不猜测AMSI事件是如何被错误配置的，以及错误配置是否是故意的。



## ETW篡改技术

如果攻击者的目标是破坏事件日志记录，那么ETW提供了一种隐蔽的机制来保护日志记录，而不会生成事件日志跟踪。下面是部分篡改技术，攻击者可以使用这些技术来切断特定事件日志的事件来源。
1. 持久性——需要重新启动。也就是说，在攻击生效之前必须重新启动。更改可以恢复，但需要重新启动。这些攻击涉及更改[autologger](https://docs.microsoft.com/en-us/windows/desktop/etw/configuring-and-starting-an-autologger-session)，持久化ETW跟踪会话和注册表中的设置。与暂时的攻击相比，持久性攻击的类型更多，而且它们通常更容易被检测到。
1. 暂时的——也就是说，可以在不重新启动的情况下攻击。


## 删除autologger提供者

**篡改类别：** 持久性, 需要重启

**最低权限：** Administrator

**检测方法：** 删除注册表项:<br>
HKLMSYSTEMCurrentControlSetControlWMIAutologgerAUTOLOGGER_NAME`{`PROVIDER_GUID`}`

**描述：** 这项技术涉及从配置的autologger中删除提供者条目。从autologger中删除提供者注册将导致事件停止传输相应的跟踪会话。

**示例：** 下面的PowerShell代码禁用Microsoft-WindowsPowerShell事件日志记录：

```
Remove-EtwTraceProvider -AutologgerName EventLog-Application -Guid '`{`A0C1853B-5C40-4B15-8766-3CF1C58F985A`}`'
```

在上面的例子中，`A0C1853B-5C40-4B15-8766-3CF1C58F985A`引用了MicrosoftWindows-PowerShell ETW提供者。该命令最终会删除`HKLMSystemCurrentControlSetControlWMIAutologgerEventLog-Application`{`a0c1853b-5c40-4b15-8766-3cf1c58f985a`}``注册表项。



## 修改提供者“Enable”属性

**篡改类别：** 持久性, 需要重启

**最低权限：** Administrator

**检测方法：** 删除注册表项：`HKLMSYSTEMCurrentControlSetControlWMIAutologgerAUTOLOGGER_NAME`{`PROVIDER_GUID`}`-EnableProperty(REG_DWORD)`

**描述：** 这种技术涉及autologger的Enable关键字。例如，默认情况下，`EventLog-Application` autoologger会话中的所有ETW提供者项都设置为0x41，这将转换为`EVENT_ENABLE_PROPERTY_SID`和`EVENT_ENABLE_PROPERTY_ENABLE_KEYWORD_0`。`事件_Enable_Property_Enable_关键字_0`没有文档说明；它指定即使关键字值设置为0，也应该记录为提供者生成的任何事件。攻击者可以将`EVENT_ENABLE_PROPERTY_ENABLE_KEYWORD_0`替换为`Event_Enable_Property_NORE_KEKEY_0`，结果值为0x11，这将导致所有关键字为0的事件不启用日志记录。例如，PowerShell事件在其事件中提供了一个0关键字值，导致禁用了PowerShell事件日志。

**示例：** 下面的PowerShell代码禁用Microsoft-WindowsPowerShell事件日志记录：

```
Set-EtwTraceProvider -Guid '`{`A0C1853B-5C40-4B15-8766-3CF1C58F985A`}`' -AutologgerName 'EventLog-Application' -Property 0x11
```

在上面的例子中，`A0C1853B-5C40-4B15-8766-3CF1C58F985A`引用了Microsoft Windows-PowerShell ETW提供者。该命令将最终将`HKLMSystemCurrentControlSetControlWMIAutologgerEventLog-Application`{`a0c1853b-5c40-4b15-8766-3cf1c58f985a`}`EnableProperty`设置为0x11。重新启动后，将停用PowerShell事件日志。

攻击者不受限制，仅使用`[Set-EtwTraceProvider](https://docs.microsoft.com/en-us/powershell/module/eventtracmancmdlets/set-etwtraceprovider?view=win10-ps)`就能执行该攻击。攻击者可以直接修改注册表中的值。`Set-EtwTraceProvider`提供了一个抽象的 autologger。

**其他检测方法：** 如果可能，建议检测`HKLMSYSTEMCurrentControlSetControlWMIAutologgerAUTOLOGGER_NAME`{`PROVIDER_GUID`}``注册表项中值的改动。请注意，修改`EnableProperty`只是一个特定的例子，攻击者也可以通过其他方式更改ETW提供者。



## 从跟踪会话中删除ETW提供者

**篡改类别：** 暂时

**最低权限：** SYSTEM

**检测方法：** 不幸的是，没有任何文件、注册表或事件日志与该事件相关联。虽然下面的技术示例表明logman.exe用于执行攻击，但攻击者可以直接使用Win32 API、WMI、DCOM、PowerShell等进行混淆。

**描述：** 该技术涉及从跟踪会话中移除ETW提供者，切断事件日志记录，直到遇到重新启动，或直到攻击者恢复提供者。虽然攻击者必须拥有执行该攻击的系统权限，但如果攻击者依赖事件日志进行威胁检测，则不太可能注意到这种攻击。

**示例：** 下面的PowerShell代码会禁用Windows-PowerShell事件日志记录，直到重新启动或攻击者恢复ETW提供者：

```
logman update trace EventLog-Application --p Microsoft-Windows-PowerShell -ets
```

**其他方法：**
- Microsoft-Windows-Kernel-EventTracing/Analytic日志中的事件ID 12指定何时修改跟踪会话，但它没有提供已删除的提供者名称或GUID，因此使用该事件很难确定是否发生可疑事件。
<li>到目前为止，已经有几个引用包含在`EventTracingManagement`模块中的ETW PowerShell命令，这个模块本身就是一个基于CDXML的模块。这意味着`EventTracingManagement`中的所有命令都由WMI类支持。例如，`Get-EtwTraceProvider`命令由`ROOT/Microsoft/Windows/EventTracingManagement:MSFT_EtwTraceProvider`类支持。考虑到ETW提供者可以WMI类实例的形式表示，可以创建一个永久WMI事件订阅，记录所有从特定跟踪会话到事件日志删除提供者的操作。[这段代码](https://gist.github.com/mattifestation/9f07e4ab0df84cfd176fe40db2d60aa8)创建一个`NtEventLogEventConsumer`实例，用于在事件日志跟踪会话`EventLog-Application`中删除提供者时将事件ID 8记录到事件日志(Source：WSH)。记录的事件如下所示：[![](https://p0.ssl.qhimg.com/t013c89a31547e5f9cc.png)](https://p0.ssl.qhimg.com/t013c89a31547e5f9cc.png)
</li>
- 目前尚不清楚在大型环境中从事件日志中移除提供者的频率。但我们仍然建议环境中记录logman.exe、wpr.exe和PowerShell的执行情况。


## 结论

识别警报和检测策略中的盲点和假设是确保检测弹性的关键步骤。因为ETW是事件日志的核心，所以深入了解ETW篡改攻击是提高安全相关的数据源完整性的一种重要的方法。



## 深入学习

[ETW — Overview](https://blogs.msdn.microsoft.com/dcook/2015/09/30/etw-overview/)

[Instrumenting Your Code with ETW](https://docs.microsoft.com/en-us/windows-hardware/test/weg/instrumenting-your-code-with-etw)

[Event Tracing for Windows: Reducing Everest to Pike’s Peak](https://www.codeproject.com/Articles/1190759/Event-Tracing-for-Windows-Reducing-Everest-to-Pike)

[Use this not this: Logging / Event Tracing](https://blogs.msdn.microsoft.com/seealso/2011/06/08/use-this-not-this-logging-event-tracing/)

[Writing an Instrumentation Manifest](https://docs.microsoft.com/en-us/windows/desktop/wes/writing-an-instrumentation-manifest)

[Event Tracing Functions](https://docs.microsoft.com/en-us/windows/desktop/etw/event-tracing-functions)

[Configuring and Starting an AutoLogger Session](https://docs.microsoft.com/en-us/windows/desktop/ETW/configuring-and-starting-an-autologger-session)

[Event Tracing](https://docs.microsoft.com/en-us/windows/desktop/etw/event-tracing-portal)

[TraceLogging](https://docs.microsoft.com/en-us/windows/desktop/tracelogging/trace-logging-portal)
