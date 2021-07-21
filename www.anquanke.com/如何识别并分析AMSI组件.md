> 原文链接: https://www.anquanke.com//post/id/187916 


# 如何识别并分析AMSI组件


                                阅读量   
                                **590714**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者specterops，文章来源：posts.specterops.io
                                <br>原文地址：[https://posts.specterops.io/antimalware-scan-inngterface-detection-optics-analysis-methodology-858c37c38383](https://posts.specterops.io/antimalware-scan-inngterface-detection-optics-analysis-methodology-858c37c38383)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t012b19b9d7edb1c584.jpg)](https://p1.ssl.qhimg.com/t012b19b9d7edb1c584.jpg)



## 0x00 前言

AMSI（Antimalware Scan Interface，反恶意软件扫描接口）是微软提供的一个接口，可以方便端点安全厂商获取某些组件的内存缓冲区数据。根据微软[官方文档](https://docs.microsoft.com/en-us/windows/win32/amsi/antimalware-scan-interface-portal#windows-components-that-integrate-with-amsi)，如下组件可以接入AMSI：
- UAC（User Account Control，用户账户控制，安装执行EXE、COM、MSI或者ActiveX时用来提升权限）
- PowerShell（脚本、交互式使用以及动态代码执行）
- Windows Script Host（`wscript.exe`以及`cscript.exe`）
- JavaScript以及VBScript
- Office VBA宏
防御方关心的是检测引擎，攻击方关注的是如何发展规避技术。从这两者的角度出发，我主要思考了如下几个问题：
- 接入AMSI接口的这些组件实际对应的究竟是哪些PE文件？
- 官方提供的文档是否准确，是否还有其他组件没有在列表上？
- 作为端点安全厂商，是否可以在不注册AMSI provider的情况下，使用AMSI服务？


## 0x01 枚举AMSI组件

为了解决前面两个问题，我们需要找到能够自动发现AMSI组件的方法。这里我们的思路是寻找文件中包含`amsi.dll`这个ASCII或者Unicode字符串的EXE或者DLL文件。那么为什么要搜索`amsi.dll`这个字符串？原因有如下两点：
<li>
`amsi.dll`用来提供扫描缓冲区所需的导出函数：[AmsiScanBuffer](https://docs.microsoft.com/en-us/windows/win32/api/amsi/nf-amsi-amsiscanbuffer)、[AmsiScanString](https://docs.microsoft.com/en-us/windows/win32/api/amsi/nf-amsi-amsiscanstring)以及`AmsiUacScan`；</li>
- 如果包含这个字符串，则代表EXE或者DLL会通过静态导入（将其作为ASCII字符串存储在PE中）或者在运行时动态导入（将其作为Unicode字符串存储在PE中）的方式来加载`amsi.dll`。
我们可以通过如下PowerShell命令寻找相关结果：

```
$UserPEs = Get-CimInstance -ClassName CIM_DataFile -Filter 'Drive = "C:" and (Extension = "exe" or Extension = "dll")' -Property 'Name' | Select -ExpandProperty Name
$AMSIReferences1 = $UserPEs | % `{` Select-String -Encoding ascii -LiteralPath $_ -Pattern 'amsi\.dll' `}`
$AMSIReferences2 = $UserPEs | % `{` Select-String -Encoding unicode -LiteralPath $_ -Pattern 'amsi\.dll' `}`
$AMSIReferences1.Path
$AMSIReferences2.Path
```

如上PowerShell代码使用WMI来枚举所有EXE以及DLL。之所以不使用`Get-ChildItem`，是因为这个cmdlet在尝试访问无法访问的文件时，可能会抛出异常结束运行。接下来，代码会使用`Select-String`（PowerShell版的`grep`）扫描每个文件，（以正则表达式）判断是否存在ASCII或者Unicode的`amsi.dll`字符串。

梳理结果，我们找到了如下AMSI组件：

```
%windir%\System32\consent.exe
%windir%\System32\jscript.dll
%windir%\System32\vbscript.dll
%windir%\System32\wbem\fastprox.dll
%windir%\Microsoft.NET\assembly\GAC_MSIL\System.Management.Automation\v4.0_3.0.0.0__31bf3856ad364e35\System.Management.Automation.dll
%windir%\Microsoft.NET\Framework64\v4.0.30319\clr.dll
%ProgramFiles%\WindowsApps\Microsoft.Office.Desktop_16051.11929.20300.0_x86__8wekyb3d8bbwe\VFS\ProgramFilesCommonX86\Microsoft Shared\VBA\VBA7.1\VBE7.DLL
```

经过一番调查研究后，我们根据微软的文档把这些AMSI组件分为如下几类：
<li>UAC：`consent.exe`
</li>
<li>PowerShell：`System.Management.Automation.dll`
</li>
<li>JavaScript以及VBScript：`jscript.dll`及`vbscript.dll`
</li>
<li>Office VBA宏：`VBE7.dll`
</li>
<li>未归类：`clr.dll`、`fastprox.dll`
</li>
在未归类的AMSI组件中，`clr.dll`是通用语言运行时（Common Language Runtime），微软的确提到过从.NET 4.8开始，Windows会扫描加载至内存的assembly。目前已经有一些研究人员研究过如何绕过这种机制，大家可以参考如下资料：
- [g_amsiContext corruption PoC](https://twitter.com/mattifestation/status/1071034781020971009)
- [How Red Teams Bypass AMSI and WLDP for .NET Dynamic Code](https://modexp.wordpress.com/2019/06/03/disable-amsi-wldp-dotnet/)
- [.NET AMSI component hooking](https://twitter.com/_xpn_/status/1069759374984429568)
- [Donut v0.9.1 “Apple Fritter” — Dual-Mode Shellcode, AMSI, and More](https://thewover.github.io/Apple-Fritter/)
还有一个是`fastprox.dll`，下面我们将对这个dll进行分析。



## 0x02 针对WMI的AMSI

由于`fastprox.dll`位于`System32\wbem`目录中，且该文件的描述为“WMI Custom Marshaller”，因此该文件与WMI密切相关。为了进一步验证这一点，我们可以使用PowerShell来确定哪个进程加载了`fastprox.dll`：

```
&gt; Get-Process | Where-Object `{` $_.Modules.ModuleName -contains 'fastprox.dll' `}`
Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
   2196     274   219988     232044  14,573.92   1192   5 chrome
   1162      47    85544      38524     803.86  14580   5 mmc
    692      42   129920      55564   1,081.20   2408   5 powershell
    874      47    77144      87852      73.48   4040   5 powershell
    686      39    71132      42608      42.78  12620   5 powershell
    229      13     2596      10072       0.13   2956   0 svchost
    480      20     3840       6728      69.66   3376   0 svchost
    613      34    26776      17356   4,370.64   3648   0 svchost
    217      43     2572       4148      18.64   6728   0 svchost
    564      33    11276      16544       4.34  11520   0 svchost
    129       7     1496       2196       0.77   5232   0 unsecapp
   1650      67   318004     256536      99.28  16576   5 vmconnect
    898      29    62664      23660   1,267.36   4776   0 vmms
    386      16     8492      13408      21.77  14220   0 WmiPrvSE
    176      10     2684       8592       1.36  15772   0 WmiPrvSE
```

我们可以使用如下一行PowerShell命令，将`svchost.exe`进程解析到对应的服务：

```
&gt; Get-Process | Where-Object `{` $_.Modules.ModuleName -contains 'fastprox.dll' -and $_.ProcessName -eq 'svchost' `}` | ForEach-Object `{` Get-CimInstance -ClassName Win32_Service -Filter "ProcessId = $($_.Id)" `}` | Format-Table -AutoSize
ProcessId Name         StartMode State   Status ExitCode
--------- ----         --------- -----   ------ --------
2956      Netman       Manual    Running OK     0
3376      iphlpsvc     Auto      Running OK     0
3648      Winmgmt      Auto      Running OK     0
6728      SharedAccess Manual    Running OK     0
11520     BITS         Auto      Running OK     0
```

根据输出结果，如果任何进程想与WMI交互，似乎都需要使用这个DLL。现在我们可以直接观察代码，了解`fastprox.dll`如何与`amsi.dll`交互。

我只在`JAmsi::JAmsiInitialize`中找到了对`amsi.dll`的引用，相关的反汇编代码如下所示：

[![](https://p5.ssl.qhimg.com/t0152f41482e798b19d.png)](https://p5.ssl.qhimg.com/t0152f41482e798b19d.png)

首先，只有当前进程不是`%windir%\System32\wbem\wmiprvse.exe`时，该函数才会初始化AMSI。我认为代码想通过这种方式减少没必要的处理逻辑，主要捕捉远程WMI操作，然而我不知道这种猜测是否准确。

接下来代码会调用`LoadLibrary`加载`amsi.dll`，解析所需的相关导出函数，比如`AmsiScanBuffer`。对`AmsiScanBuffer`的唯一一处交叉引用位于`JAmsi::JAmsiRunScanner`函数中：

[![](https://p1.ssl.qhimg.com/t014bbeab77cf3044ac.png)](https://p1.ssl.qhimg.com/t014bbeab77cf3044ac.png)

`JAmsiRunScanner`由`JAmsi::JAmsiProcessor`调用，而如下函数会调用`JAmsiProcessor`：

```
CWbemSvcWrapper::XWbemServices::ExecNotificationQueryAsync
CWbemSvcWrapper::XWbemServices::CreateInstanceEnum
CWbemSvcWrapper::XWbemServices::ExecQueryAsync
CWbemSvcWrapper::XWbemServices::ExecQuery
CWbemSvcWrapper::XWbemServices::CreateInstanceEnumAsync
CWbemSvcWrapper::XWbemServices::GetObjectW
CWbemSvcWrapper::XWbemServices::ExecMethod
CWbemSvcWrapper::XWbemServices::ExecMethodAsync
CWbemSvcWrapper::XWbemServices::ExecNotificationQuery
CWbemSvcWrapper::XWbemServices::GetObjectAsync
JAmsi::JAmsiProcessor（由CWbemInstance::SetPropValue调用）
```

除了最后一个函数，其他都对应[IWbemServices](https://docs.microsoft.com/en-us/windows/win32/api/wbemcli/nn-wbemcli-iwbemservices)接口中实现的方法。最后一个函数很可能对应的是[IWbemClassObject::Put](https://docs.microsoft.com/en-us/windows/win32/api/wbemcli/nf-wbemcli-iwbemclassobject-put)方法。

现在我们需要澄清端点安全产品可能获取哪些WMI事件。我在之前关于ETW的一篇[文章](https://medium.com/palantir/tampering-with-windows-event-tracing-background-offense-and-defense-4be7ac62ac63)中介绍了如何使用`AmsiScanBuffer`将所有事件记录到`Microsoft-Antimalware-Scan-Interface` provider中。使用`AmsiScanBuffer`进行检测有一个优点，那就是可以跟踪调用`AmsiScanBuffer`的任何进程所对应的AMSI缓冲区。如果大家想进一步了解ETW机制以及跟踪技术，可以详细参考那篇文章。这里我们可以使用`logman`来捕捉所有AMSI事件，获取相关的WMI事件：

```
logman start trace AMSITrace -p Microsoft-Antimalware-Scan-Interface (Event1) -o amsi.etl -ets
```

开始跟踪后，我们可以与WMI交互，看一下是否生成了一些事件。我使用了如下测试命令：

```
$CimSession = New-CimSession -ComputerName .
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @`{`CommandLine = 'notepad.exe'`}` -CimSession $CIMSession
$CIMSession | Remove-CimSession
```

这条命令中，我创建了一个本地CIM会话，用来模拟远程WMI连接。在这个过程中，我注意避免在`wmiprvse.exe`上下文中跟踪，前面提到过，该进程会被排除在AMSI处理过程之外。

完成与WMI的交互后，使用如下命令停止跟踪：

```
logman stop AMSITrace -ets
```

然后我使用PowerShell来查找WMI事件，的确发现了一个结果：

```
&gt; $AMSIEvents = Get-WinEvent -Path .\amsi.etl -Oldest
&gt; $AMSIEvents[5] | Format-List *
Message              : AmsiScanBuffer
Id                   : 1101
Version              : 0
Qualifiers           :
Level                : 4
Task                 : 0
Opcode               : 0
Keywords             : -9223372036854775807
RecordId             : 5
ProviderName         : Microsoft-Antimalware-Scan-Interface
ProviderId           : 2a576b87-09a7-520e-c21a-4942f0271d67
LogName              :
ProcessId            : 7184
ThreadId             : 8708
MachineName          : COMPY486
UserId               :
TimeCreated          : 10/3/2019 12:14:51 PM
ActivityId           : 95823c06-72e6-0000-a133-8395e672d501
RelatedActivityId    :
ContainerLog         : c:\users\testuser\desktop\amsi.etl
MatchedQueryIds      : `{``}`
Bookmark             : System.Diagnostics.Eventing.Reader.EventBookmark
LevelDisplayName     : Information
OpcodeDisplayName    : Info
TaskDisplayName      :
KeywordsDisplayNames : `{``}`
Properties           : `{`System.Diagnostics.Eventing.Reader.EventProperty, System.Diagnostics.Eventing.Reader.EventProperty...`}`
&gt; $AMSIEvents[5].Properties
Value
-----
0
1
1
WMI
300
300
`{`67, 0, 73, 0...`}`
`{`131, 136, 119, 209...`}`
False
&gt; [Text.Encoding]::Unicode.GetString($AMSIEvents[5].Properties[7].Value)
CIM_RegisteredSpecification.CreateInstanceEnum();
Win32_Process.GetObjectAsync();
Win32_Process.GetObject();
SetPropValue.CommandLine("notepad.exe");
&gt; Get-CimInstance -ClassName Win32_Service -Filter "ProcessId = $($AMSIEvents[5].ProcessId)"
ProcessId Name  StartMode State   Status ExitCode
--------- ----  --------- -----   ------ --------
7184      WinRM Auto      Running OK     0
```

那么现在我们如何理解目前搜集到的所有信息呢？首先，解析跟踪到的每个事件后，我们发现第6个事件（索引值为5）是唯一一个在第4个`Properties`属性中包含`WMI`的事件。此外，第8个`Properties`值包含一段二进制数据，这些数据看上去由Unicode字符串所构成。解码字符串后，该字符串对应的是我在前面执行的`Win32_Process Create`操作。这里我们还需要注意AMSI事件来源的进程ID：`7184`，对应的是`svchost.exe`进程。使用`Win32_Service` `WMI`类来解析对应的服务，可以发现实际进程对应的是WinRM服务。这一点非常正常，因为CIM cmdlet基于WSMan，而后者是WimRM服务所使用的协议。

作为防御方及端点安全厂商，我们可以将这种上下文信息纳入可疑的WMI操作。现在WMI服务的应用范围非常广泛，系统会在许多合法操作中用到WMI，这种场景会不会影响对AMSI缓冲区的其他使用场景呢？经过测试后，我发现我显式执行的许多WMI操作并没有被记录下来。经过一些逆向分析后，我找到了背后的原因：只有当`JAmsi::JAmsiIsScannerNeeded`返回`True`时，系统才会调用`JAmsi::JAmsiRunScanner`：

[![](https://p2.ssl.qhimg.com/t01ac4d40dd99766f6e.png)](https://p2.ssl.qhimg.com/t01ac4d40dd99766f6e.png)

简单分析`JAmsi::JAmsiIsScannerNeeded`的实现后，我发现系统会计算WMI操作对应的上下文字符串的CRC校验和，只有当校验和满足如下白名单值时才会记录这些操作：

[![](https://p4.ssl.qhimg.com/t0189b3ea56aa6189cb.png)](https://p4.ssl.qhimg.com/t0189b3ea56aa6189cb.png)

在本文撰写时，白名单中的CRC值包括：`0x788C9917`、`0x96B23E8A`、`0xB8DA804E`、`0xC0B29B3D`、`0xD16F4088`、`0xD61D2EA7`、`0xEF726924`、`0x46B9D093`以及`0xF837EFC3`。

我没有专门针对这些校验和进行暴力破解，但考虑到系统会记录下`Win32_Process Create`操作，因此我们可以推测这些校验和对应的是常见的WMI攻击行为。我们可以将计算这些字符串的校验和当成一种安全机制，`vbscript.dll`以及`jscrit.dll`中也会[计算](https://twitter.com/KyleHanslovan/status/1083344377404186625)这些校验和。

通过这部分的分析，我们发现微软一直在向安全厂商以及防御方提供更多安全信息，拓宽安全视角。一旦找到了白名单对应的值，我相信这种安全机制就很容易被绕过。安全攻防领域从来没有万灵膏药，这也是我们往正确方向迈出的重要一步。

大家可能还有个问题：如何解释`Get-WinEvent`返回事件中的`Properties`字段值？下文我们将详细介绍解决该问题的方法。



## 0x03 解析AMSI事件中的字段名

如果想将事件字段名称与`.ETL`日志关联起来，最简单的一种方法就是将日志文件载入Event Viewer，该应用会将跟踪记录转换为`EVTX`文件，在后台解析出AMSI ETW provider对应的manifest信息，并将字段名对应地附加到生成的`.evtx`文件中。比如，我们可以在“Details”窗口中看到如下信息：

[![](https://p1.ssl.qhimg.com/t01a31c7975057f8469.png)](https://p1.ssl.qhimg.com/t01a31c7975057f8469.png)

此外，我们还可以使用`perfview.exe`，将ETW provider信息[恢复](https://twitter.com/mattifestation/status/774321379411955712)成XML格式。恢复出来的字段名顺序对应`Get-WinEvent`返回的`Properties`值顺序。

根据对`AmsiScanBuffer`有限的逆向分析结果，Event ID 1101（AMSI扫描事件）中相应的字段描述如下所示：
<li>
`session`：会话标识符。如果通过[AmsiOpenSession](https://docs.microsoft.com/en-us/windows/win32/api/amsi/nf-amsi-amsiopensession)来建立AMSI扫描会话，就会出现该字段。字段值通过调用[IAmsiStream::GetAttribute](https://docs.microsoft.com/en-us/windows/win32/api/amsi/nf-amsi-iamsistream-getattribute)（指定`AMSI_ATTRIBUTE_SESSION`参数）来获取。如果出现了这个字段，我们可以通过该值关联来自同一会话的多次扫描。比如，如果攻击者执行了经过混淆的PowerShell脚本，那么从理论上讲，与该操作相关的所有脚本块（scriptblock）都会使用相同的会话标识符。</li>
<li>
`scanStatus`：这似乎是个`boolean`值，我没见过除`1`之外的其他值，没有进一步调查。</li>
<li>
`scanResult`：这是端点产品扫描完缓冲区后返回的`AMSI_RESULT`值。在这里`1`对应的是`AMSI_RESULT_NOT_DETECTED`。</li>
<li>
`appname`：通过`AmsiInitialize` `appName`参数传递的应用程序名。对于`fastprox.dll`，`appName`对应的是硬编码的`WMI`。</li>
<li>
`contentname`：如果扫描的内容源自于文件，那么这个字段就包含完整的文件路径。</li>
<li>
`contentsize`：如果内容被过滤，那么该字段代表的是过滤后的内容大小，会比`originalsize`值小。在实际测试中，我没有看到被过滤后的内容。</li>
<li>
`originalsize`：未过滤内容的大小。我们可以通过调用`IAmsiStream::GetAttribute`方法（指定`AMSI_ATTRIBUTE_CONTENT_SIZE`参数）来获取这个值。</li>
<li>
`content`：被扫描的payload对应的原始字节。根据组件的实现方式，该字段可能对应Uincode字符串或者raw字节。比如，对于`clr.dll`，该字段值为加载到内存中需要扫描的assembly对应的完整PE。</li>
<li>
`hash`：被扫描缓冲区对应的SHA256哈希。</li>
<li>
`contentFiltered`：代表内容是否被截断（truncated）/过滤（filtered）。在本文撰写时，`AmsiScanBuffer`将这个字段设置为`false`，目前我没有找到将该值设为`true`的代码逻辑。</li>


## 0x04 总结

本文的目标是介绍能够识别AMSI组件的一种方法，分析这些组件的实现方式（以WMI组件为例），并从AMSI ETW事件中进一步挖掘信息。攻击者可以使用这种方法来规避AMSI检测机制，防御方也能借鉴这种方法来解析ETW事件。目前我们尚不清楚微软是否会正式公布AMSI所有组件的文档，但根据本文分析，微软一直在改进AMSI，完善系统安全性。

在后续研究中，我会将AMSI ETW跟踪功能加入我的恶意软件分析工具中，该功能可以帮我们捕捉被高度混淆的恶意软件样本所使用的脚本、WMI以及.NET assembly。
