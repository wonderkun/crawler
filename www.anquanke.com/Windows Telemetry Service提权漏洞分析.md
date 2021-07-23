> 原文链接: https://www.anquanke.com//post/id/209775 


# Windows Telemetry Service提权漏洞分析


                                阅读量   
                                **115939**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者secret，文章来源：secret.club
                                <br>原文地址：[https://secret.club/2020/07/01/diagtrack.html](https://secret.club/2020/07/01/diagtrack.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0177c15fc06cb67686.png)](https://p1.ssl.qhimg.com/t0177c15fc06cb67686.png)



## 0x00 前言

在本文中，我们将分析“Connected User Experiences and Telemetry Service”（互联用户体验和遥测服务），也就是`diagtrack`服务。本文涉及到与NTFS相关的一些术语，因此大家需要对相关背景有所了解。

我在Feedback Hub中观察到一个有趣的“Advanced Diagnostics”（高级诊断）功能，所有用户都可以触发该功能，触发在`C:\Windows\Temp`目录中的文件活动，而所有用户具备该目录的写权限。

[![](https://p5.ssl.qhimg.com/t013dc17c9c74b63758.png)](https://p5.ssl.qhimg.com/t013dc17c9c74b63758.png)

逆向分析该功能比较复杂，如果想复现所需的交互过程也颇具挑战，因为该服务使用的是WinRT IPC，而不是COM。我对WinRT不是特别熟悉，因此需要先做些背景工作。

在`C:\Program Files\WindowsApps\Microsoft.WindowsFeedbackHub_1.2003.1312.0_x64__8wekyb3d8bbwe\Helper.dll`中，我找到了一个比较有趣的函数：

```
WINRT_IMPL_AUTO(void) StartCustomTrace(param::hstring const&amp; customTraceProfile) const;
```

该函数将在Diagtrack Service的安全上下文中执行`WindowsPerformanceRecorder`配置，该配置在XML文件中定义，而文件路径通过参数传递给该函数。

文件路径采用基于`System32`目录的相对路径解析方式，因此我在所有用户都具备写权限的目录（`System32\Spool\Drivers\Color`）中存放了一个XML文件，然后传递这个相对文件路径，随后`Diagtrack`成功开始跟踪相关事件。

典型的`WindowsPerformanceRecorder`配置文件至少应该满足如下格式：

```
&lt;WindowsPerformanceRecorder Version="1"&gt;
 &lt;Profiles&gt;
  &lt;SystemCollector Id="SystemCollector"&gt;
   &lt;BufferSize Value="256" /&gt;
   &lt;Buffers Value="4" PercentageOfTotalMemory="true" MaximumBufferSpace="128" /&gt;
  &lt;/SystemCollector&gt;  
  &lt;EventCollector Id="EventCollector_DiagTrack_1e6a" Name="DiagTrack_1e6a_0"&gt;
   &lt;BufferSize Value="256" /&gt;
   &lt;Buffers Value="0.9" PercentageOfTotalMemory="true" MaximumBufferSpace="4" /&gt;
  &lt;/EventCollector&gt;
   &lt;SystemProvider Id="SystemProvider" /&gt; 
  &lt;Profile Id="Performance_Desktop.Verbose.Memory" Name="Performance_Desktop"
     Description="exploit" LoggingMode="File" DetailLevel="Verbose"&gt;
   &lt;Collectors&gt;
    &lt;SystemCollectorId Value="SystemCollector"&gt;
     &lt;SystemProviderId Value="SystemProvider" /&gt;
    &lt;/SystemCollectorId&gt; 
    &lt;EventCollectorId Value="EventCollector_DiagTrack_1e6a"&gt;
     &lt;EventProviders&gt;
      &lt;EventProviderId Value="EventProvider_d1d93ef7" /&gt;
     &lt;/EventProviders&gt;
    &lt;/EventCollectorId&gt;    
    &lt;/Collectors&gt;
  &lt;/Profile&gt;
 &lt;/Profiles&gt;
&lt;/WindowsPerformanceRecorder&gt;
```



## 0x01 信息泄露

由于我们具备该文件的完整控制权限，因此可能有一些攻击机会。该文件中`EventCollector`元素的`Name`属性用来创建跟踪事件的文件名，配置文件对应的文件路径为：

```
C:\Windows\Temp\DiagTrack_alternativeTrace\WPR_initiated_DiagTrackAlternativeLogger_DiagTrack_XXXXXX.etl
```

其中`XXXXXX`为`Name`属性的值。

由于我们可以控制文件名及路径，因此可以将名字设置为`\..\..\file.txt`，对应的路径为：

```
C:\Windows\Temp\DiagTrack_alternativeTrace\WPR_initiated_DiagTrackAlternativeLogger_DiagTrack\..\..\file.txt:.etl
```

这将导致目标服务使用的是`C:\Windows\Temp\file.txt`文件。

目标服务会使用`SYSTEM`权限，通过**[FILE_OVERWRITE_IF](https://docs.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntcreatefile)**参数来打开事件记录文件，因此我们有可能使用`SYSTEM`权限覆盖可写的任何文件。如果在`SYSTEM`可写的路径中附加`::$INDEX_ALLOCATION`，那么也有可能创建文件及目录。

从信息泄露角度来看，能够选择目标服务所执行的ETW Provider本身就是非常有趣的一个攻击点。

如果某个服务在某个目录中创建了一个文件，而我们不具备该目录的权限，导致无法列出相关的文件，此时这种技术就能派上用场。

如下图所示，我们可以借助`Microsoft-Windows-Kernel-File` Provider，从`etl`文件中获取这些文件名，具体方式是在`WindowsPerformanceRecorder`配置文件中添加`22FB2CD6-0E7B-422B-A0C7-2FAD1FD0E716`信息：

```
&lt;EventData&gt;
 &lt;Data Name="Irp"&gt;0xFFFF81828C6AC858&lt;/Data&gt;
 &lt;Data Name="FileObject"&gt;0xFFFF81828C85E760&lt;/Data&gt;
 &lt;Data Name="IssuingThreadId"&gt;  10096&lt;/Data&gt;
 &lt;Data Name="CreateOptions"&gt;0x1000020&lt;/Data&gt;
 &lt;Data Name="CreateAttributes"&gt;0x0&lt;/Data&gt;
 &lt;Data Name="ShareAccess"&gt;0x3&lt;/Data&gt;
 &lt;Data Name="FileName"&gt;\Device\HarddiskVolume2\Users\jonas\OneDrive\Dokumenter\FeedbackHub\DiagnosticLogs\Install and Update-Post-update app experience\2019-12-13T05.42.15-SingleEscalations_132206860759206518\file_14_ProgramData_USOShared_Logs__&lt;/Data&gt;
&lt;/EventData&gt;
```

这样我们就可以在貌似无法利用的场景中，通过这种信息泄露营造出利用场景。

其他可以绕过安全设置的Provider包括：
- `Microsoft-Windows-USB-UCX `{`36DA592D-E43A-4E28-AF6F-4BC57C5A11E8`}``
<li>
`Microsoft-Windows-USB-USBPORT `{`C88A4EF5-D048-4013-9408-E04B7DB2814A`}``（捕捉Raw USB数据，实现键盘记录）</li>
- `Microsoft-Windows-WinINet `{`43D1A55C-76D6-4F7E-995C-64C711E5CAFE`}``
<li>
`Microsoft-Windows-WinINet-Capture `{`A70FF94F-570B-4979-BA5C-E59C9FEAB61B`}``（从iexplore、Microsoft Store等中捕捉Raw HTTP流量，这样就能在SSL流未加密前捕捉明文数据）</li>
<li>
`Microsoft-PEF-WFP-MessageProvider`（未加密的IPSEC VPN数据）</li>


## 0x02 代码执行

那么如何将信息泄露漏洞变成代码执行漏洞呢？

尽管我们能控制`.etl`文件的目的路径，但很有可能无法轻松实现代码执行，我们需要找到其他切入点。我们只能部分控制文件内容，导致漏洞利用起来很难。虽然有可能构造可执行的PowerShell脚本或者bat文件，但在执行这些文件时会存在一些问题。

于是我选择另一条路，将活跃的事件记录行为与调用如下函数结合起来：

```
WINRT_IMPL_AUTO(Windows::Foundation::IAsyncAction) SnapCustomTraceAsync(param::hstring const&amp; outputDirectory)
```

当我们将`outputDirectory`参数值设置为`%WINDIR%\temp\DiagTrack_alternativeTrace`中的目录时（正在运行的记录事件保存在该目录的`.etl`文件中），我们可以看到一种有趣的行为：

Diagtrack Service会将`DiagTrack_alternativeTrace`中创建的所有`.etl`文件重命名为`SnapCustomTraceAsync`函数`outputDirectory`参数所指定的目录值。由于文件命名操作导致非特权用户具备源文件创建的目录写权限，因此我们就能实现目的地址的控制权。更具体的原因在于，当执行重命名操作时，DACL并没有发生改动，因此文件和父目录权限会得到继承。这意味着如果我们可以将目的目录设置为`%WINDIR%\System32`，并且以某种方式移动文件，那么我们将仍然具备该文件的写权限。现在我们已经可以控制`SnapCustomTraceAsync`函数的`outputDirectory`参数，但仍然存在一些限制。

如果我们选择的`outputDirectory`并不是`%WINDIR%\temp\DiagTrack_alternativeTrace`的子目录，那么并不会出现重命名操作。`outputDirectory`之所以无效，是因为Diagtrack Service必须先创建该目录。而在创建该目录时，服务所使用的权限为`SYSTEM`，导致目录所有者也为`Diagtrack Service`，用户只有`READ`权限。

这里存在问题，因为我们无法将目录变成一个挂载点。即使我们具备所需的权限，由于`Diagtrack`会将输出的`etl`文件放在该目录中，因此我们无法清空该目录，导致无法继续利用。幸运的是，我们可以在目标`outputDirectory`以及`DiagTrack_alternativeTrace`间创建2级间接关系来绕过该问题。

我们可以创建`DiagTrack_alternativeTrace\extra\indirections`目录，将`%WINDIR%\temp\DiagTrack_alternativeTrace\extra\indirections\snap`作为`outputDirectory`参数值，以便让`Diagtrack`使用有限的权限来创建`snap`目录（因为我们位于`DiagTrack_alternativeTrace`目录中）。通过这种方式，我们可以重命名`extra`目录（因为该目录由我们所创建）。由于`Diagtrack`会打开目录中的文件，因此这种2级间接关系非常有必要，可以绕过目录锁定。当重命名`extra`后，我们可以重新创建`%WINDIR%\temp\DiagTrack_alternativeTrace\extra\indirections\snap`（现在为空目录）。并且由于我们是所有者，因此具备完整权限。

现在我们可以将`DiagTrack_alternativeTrace\extra\indirections\snap`变成挂载点，指向`%WINDIR%\system32`，然后`Diagtrack`会将匹配`WPR_initiated_DiagTrack*.etl*`的所有文件移动到`%WINDIR%\system32`。由于这些文件在用户具备`WRITE`权限的目录中创建，因此仍然处于可写状态。不幸的是，具备`System32`中某个目录的完整控制权限并不足以实现代码执行，除非我们找到用户能够控制文件名的方法（比如**[James Forshaw](https://twitter.com/tiraniddo)**提供的DiagnosticHub插件方法）。然而情况稍微有点不同，`DiagnosticHub`现在要求加载的DLL必须经过微软签名，但如果文件名满足某些特殊条件，我们还是可以在`SYSTEM`安全上下文中执行DLL文件。这里还有另一个问题：文件名不可控，我们如何克服该困难呢？

我们可以不将挂载点指向`System32`目标，而是指向NT命名空间中的Object Directory（对象目录），并且创建于重命名目标文件同名的符号链接，这样我们就可以控制文件名，此时符号链接目标将会变成重命名操作的目标。比如，如果我们将其设置为`\??\%WINDIR%\system32\phoneinfo.dll`，那么我们将具备某个文件的写权限，而当错误报告在进程外提交时，Error Reporting服务将会加载并执行这个文件。在设置挂载点目标时，我选择的是`\RPC Control`，因为所有用户都可以在其中创建符号链接。

让我们来试一下。

我们原以为`Diagtrack`会完成重命名操作，然而什么事情都没有发生。这是因为在重命名操作完成前，目标处于被打开状态，但现在已经变成一个对象目录。这意味着该目录无法通过文件/目录API调用来打开。我们可以设置创建挂载点的时机，使其晚于目录打开操作，但早于重命名操作前。通常在这种情况下，我会在目标目录中创建一个文件，文件名与重命名的目标文件名相同。然后我会在文件上设置一个OPLOCK，当锁被触发时，代表目录检查已完成，即将执行重命名操作。在释放锁之前，我将文件移动到另一个目录，将挂载点设置为现在这个空目录。但这种方法并不适用于这个场景，因为重命名操作无法覆盖已经存在的文件。这也意味着重命名操作由于文件的存在会被中断，不会触发OPLOCK。

在即将放弃时，我突然想到一件事：

如果我每隔1毫秒来回切换指向有效目录与对象目录的连接点，那么在完成目录检查时，有50%的机会能指向正常的有效目录。而在重命名操作发生时，有50%的机会能够指向对象目录。这样重命名操作就有25%的机会成功完成，最终变成`System32`中的`phoneinfo.dll`文件。我尝试过尽可能避免这种竞争条件，但在这种场景下，我的确没有找到其他可用的方法。我可以通过不断重复该过程，从而弥补各种失败的操作。为了调整失败的可能性，我决定触发任意数量的重命名操作。幸运的是，这里我们的确可以在同一个记录行为中触发尽可能多的重命名操作。重命名操作并不会链接到`Diagtrack`服务已创建的文件，因此唯一要满足的要求是这些文件位于`%WINDIR%\temp\DiagTrack_alternativeTrace`中，并且匹配`WPR_initiated_DiagTrack*.etl*`。

由于我们能够在目标目录中创建文件，因此现在可以创建`WPR_initiated_DiagTrack0.etl`、`WPR_initiated_DiagTrack1.etl`等，这些文件都会被重命名。

由于我们的目标是让其中有个文件变成`System32`中的`phoneinfo.dll`，那么为什么不将这些文件创建成指向特定payload的硬链接呢？通过这种方式，我们不需要在文件被移动后，使用`WRITE`权限来覆盖目标文件。

经过一些实验后，我找到了如下解决方案：

1、创建`%WINDIR%\temp\DiagTrack_alternativeTrace\extra\indirections`文件夹。

2、开始诊断跟踪，服务创建`%WINDIR%\temp\DiagTrack_alternativeTrace\WPR_initiated_DiagTrackAlternativeLogger_WPR System Collector.etl`。

3、创建`%WINDIR%\temp\DiagTrack_alternativeTrace\WPR_initiated_DiagTrack[0-100].etl`硬链接，指向payload。

4、创建符号链接`\RPC Control\WPR_initiated_DiagTrack[0-100.]etl`，指向`%WINDIR%\system32\phoneinfo.dll`。

5、在`WPR_initiated_DiagTrack100.etl`上设置OPLOCK，当触发时，检查`%WINDIR%\system32\phoneinfo.dll`是否存在。如果不存在，则重复创建`WPR_initiated_DiagTrack[].etl`文件，匹配符号链接。

6、在`WPR_initiated_DiagTrack0.etl`上设置OPLOCK，当触发时，我们知道重命名流程已开始，但第一个重命名操作尚未发生。

此时，我们执行如下操作：

1、将`%WINDIR%\temp\DiagTrack_alternativeTrace\extra`重命名为`%WINDIR%\temp\DiagTrack_alternativeTrace\`{`RANDOM-GUID`}``。

2、创建`%WINDIR%\temp\DiagTrack_alternativeTrace\extra\indirections\snap`目录。

3、开启循环线程，来回切换`%WINDIR%\temp\DiagTrack_alternativeTrace\extra\indirections\snap`挂载点，使其指向`%WINDIR%\temp\DiagTrack_alternativeTrace\extra`以及NT对象命名空间中的`\RPC Control`。

4、开始快照跟踪，将`outputDirectory`的值设置为`%WINDIR%\temp\DiagTrack_alternativeTrace\extra\indirections\snap`。

在执行上述操作时，有100个文件被重命名。如果这些文件都没有变成`System32`中的`phoneinfo.dll`，则重复攻击流程，直到成功为止。

然后我在切换连接点的线程中添加了检查逻辑，检查系统中是否存在`%WINDIR%\system32\phoneinfo.dll`。如果增加切换挂载点的时间间隔，似乎也能增加创建`phoneinfo.dll`的成功机会。经过测试后，前100次迭代就能成功重命名该文件。

当检查到`%WINDIR%\system32\phoneinfo.dll`时，会有一个空白的错误报告被提交至Windows Error Reporting服务，并且报告被配置为进程外提交，从而导致`wermgmr.exe`加载我们在`SYSTEM`安全上下文中刚创建的`phoneinfo.dll`。

我选择的payload为一个DLL，在`DLL_PROCESS_ATTACH`时，payload会检查`SeImpersonatePrivilege`特权。如果启用了该特权，就会在当前活动的桌面中生成一个`cmd.exe`。如果没有具备该特权，那么也会生成其他命令提示符，因为启动错误报告的进程也会尝试加载`phoneinfo.dll。`

此外，我还使用`WTSSendMessage`来发送消息，这样即使命令提示符无法在正确的会话/桌面中生成，我们也能得到操作成功的提示消息。

[![](https://p2.ssl.qhimg.com/t0107de43a168144300.png)](https://p2.ssl.qhimg.com/t0107de43a168144300.png)

上图中命令提示符之所以为红色背景，是因为我的命令提示符会自动执行``echo test&gt; C:\windows:stream &amp;&amp; color 4E`;`，这样所有通过UAC提升的命令提示符背景都会变成红色，便于我更好地识别。

虽然我公布的[代码](https://github.com/thesecretclub/diagtrack/blob/master/example.cpp)中包含一些私有库，但应该能帮助大家从整体层面理解相关原理。
