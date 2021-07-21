> 原文链接: https://www.anquanke.com//post/id/185423 


# Avira Optimizer本地提权漏洞分析


                                阅读量   
                                **334799**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者enigma0x3，文章来源：enigma0x3.net
                                <br>原文地址：[https://enigma0x3.net/2019/08/29/avira-optimizer-local-privilege-escalation/](https://enigma0x3.net/2019/08/29/avira-optimizer-local-privilege-escalation/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01220421d8bc61afe6.jpg)](https://p1.ssl.qhimg.com/t01220421d8bc61afe6.jpg)



## 0x00 前言

当用户安装最新版Avira反病毒软件时，也会附加安装一些组件，其中一个组件为Avira Optimizer。[Avira.OptimizerHost.exe](https://www.virustotal.com/gui/file/1b16d74643382c88ad133bc274740472a7e58b0a1428225e192789af5a37fada/detection)这个程序运行在`NT AUTHORITY\SYSTEM`权限，接收通过`AviraOptimizerHost`命名管道（`\\.\pipe\AviraOptimizerHost`）发送的命令。该服务没有对调用客户端执行有效的校验操作，也没有检查启动程序的有效性，导致恶意代码可以向`Avira.OptimizerHost.exe`发起进程创建调用请求，实现本地权限提升。

**测试版本：**Avira Optimizer &lt; 1.2.0.367

**测试系统：**Windows 10 1803 （x64）

**漏洞描述：**Avira Optimizer通过不安全命名管道导致本地提权（LPE）漏洞



## 0x01 漏洞分析及利用

在分析目标软件是否存在权限提升漏洞时，想寻找合适的切入点往往并不容易，因为其中涉及到大量原语以及漏洞类别。我通常会从基础开始着手，然后逐步探索复杂方向。这个过程通常涉及到许多工具，比如[PowerUp](https://github.com/PowerShellMafia/PowerSploit/blob/dev/Privesc/PowerUp.ps1)，该工具可以帮我们识别各种琐碎（但又常见）的错误配置情况。

如果没有找到有趣的信息，那么下一步通常是寻找逻辑漏洞。这些漏洞可能更难通过自动化方式识别，需要更多手动操作环节。我的做法通常是分析通用可写目录、可写注册表位置、通过[NTObjectManager](https://github.com/googleprojectzero/sandbox-attacksurface-analysis-tools/tree/master/NtObjectManager)对外公开的命名管道以及RPC接口。在分析已有命名管道时，我发现有些Avira进程会创建一个命名管道，并且带有[NULL DACL](https://docs.microsoft.com/en-us/windows/win32/secauthz/null-dacls-and-empty-dacls)，这意味着任何用户都具备完整访问权限：

[![](https://p1.ssl.qhimg.com/t010e835058c3ad4a44.png)](https://p1.ssl.qhimg.com/t010e835058c3ad4a44.png)

有趣的是，如果高权限Avira进程没有使用这个管道，那么这个切入点并不是特别有用。检查使用该管道的进程ID后，我们发现的确有`SYSTEM`权限的Avira进程的身影：

[![](https://p5.ssl.qhimg.com/t01fdefd1268bca0540.png)](https://p5.ssl.qhimg.com/t01fdefd1268bca0540.png)

下一步就是澄清`Avira.OptimizerHost.exe`对该命名管道的处理方式。这个问题非常值得研究，因为此处高权限进程正与低权限用户可控的一个资源进行交互。由于`Avira.OptimizerHost.exe`使用了该管道对应的句柄，因此很有可能该进程正通过管道来传输某些数据。为了验证这一点，接下来我们可以在IDA中打开`Avira.OptimizerHost.exe`。经过一番研究后，我们发现目标服务会处理连接到`AviraOptimizerHost`命名管道的任何客户端，验证这些客户端是否为有效的Avira文件。

为了滥用这个命名管道，我们需要绕过这个检查机制，以便成功通过命名管道将数据发送给目标服务。目标服务会通过[GetNamedPipeClientProcessID()](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getnamedpipeclientprocessid)获取连接的客户端，然后通过[QueryFullProcessImageNameW()](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-queryfullprocessimagenamew)提取客户端的完整映像路径。

[![](https://p0.ssl.qhimg.com/t01af17fe744ebe1ac9.png)](https://p0.ssl.qhimg.com/t01af17fe744ebe1ac9.png)

获取到路径后，目标服务会提取调用客户端的证书，确保证书由Avira签发，没有被篡改。这里厂商是想确保只有有效的Avira进程才能向目标服务发送命令。为了绕过这一点，我们可以将自己的代码注入正在运行的Avira进程（或者只是简单地[克隆已有证书](https://github.com/xorrior/Random-CSharpTools/tree/master/SigPirate)）。

接下来就是澄清我们可以通过命名管道向目标服务发送哪些数据。在这种情况下，我通常会去以潜在的合法客户端为目标，研究正常操作期间这些客户端的处理逻辑。由于这个命名管道属于Avira Optimizer的一部分，因此我开始寻找已安装的Avira组件。走过不少死胡同后，我找到了Avira的System Speedup应用。之所以选择该应用，是因为从字面上理解，“优化”（optimization）和“加速”（speedup）本来就是同义词。在Avira的“System Speedup”目录中一番搜索后，我还是困在Avira System Speedup的程序库中。于是我将System Speedup目录中的所有文件载入DnSpy中，开始搜索对命名管道的引用。此时线索指向了`Avira.SystemSpeedup.Core.Client.Services.dll`中的`StartServiceHost()`方法。

[![](https://p0.ssl.qhimg.com/t01ca2f71b987cf8cad.png)](https://p0.ssl.qhimg.com/t01ca2f71b987cf8cad.png)

与我猜想的一样，这正是连接到`AviraOptimizerHost`命名管道的代码。该函数会进一步调用`Avira.Optimizer.Common.Tools.OptimizerHostClient`类中的`OptimizerHostCommandsClient.Connect()`函数，这看上去非常有趣。观察该函数时，我们发现该函数只是调用[WaitNamedPipe()](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-waitnamedpipea)，等待命名管道就绪。一旦满足条件，就使用`CreateFile`来获取绑定到命名管道的一个句柄。

[![](https://p0.ssl.qhimg.com/t014c26c50b96d9cab0.png)](https://p0.ssl.qhimg.com/t014c26c50b96d9cab0.png)

回过来看`StartServiceHost`方法。该方法会初始化`Avira.Optimizer.Common.Tools.OptimizerHostClient`类的一个实例，连接到`AviraOptimizerHost`命名管道，然后继续调用`StartParentProcess()`这个有趣的方法。

[![](https://p1.ssl.qhimg.com/t01d3ba6753864ea941.png)](https://p1.ssl.qhimg.com/t01d3ba6753864ea941.png)

查看这个实例化类时，我们可以找到许多有趣的方法，比如`StartProcess`、`StartParentProcess`、`StopProcess`、`AddTask`以及`RemoveTask`。这些方法接收各种参数，将任务转化为JSON格式数据后继续调用`SendMessage`：

[![](https://p5.ssl.qhimg.com/t0154bdc15565aefb30.png)](https://p5.ssl.qhimg.com/t0154bdc15565aefb30.png)

`SendMessage()`方法接收JSON格式的命令，将其发送给`AviraOptimizerHost`命名管道，交由`SYSTEM`权限的`Avira.OptimizerHost.exe`进程提取处理。

[![](https://p1.ssl.qhimg.com/t01438a2db4c5be3f71.png)](https://p1.ssl.qhimg.com/t01438a2db4c5be3f71.png)

分析`Avira.OptimizerHost.exe`，可以看到服务会读取JSON数据，解析相关参数：

[![](https://p5.ssl.qhimg.com/t01eb4102cb787f57ad.png)](https://p5.ssl.qhimg.com/t01eb4102cb787f57ad.png)

这种情况下，如果我们向命名管道发送`StartProcess()`方法，那么目标服务就会从管道发送过来的JSON数据中提取`procid`、`exec`（可执行文件路径）、`args`（参数）等。随后，目标服务会遵循客户端验证命名管道有效性的逻辑，通过`exec`参数提取可执行文件路径，检查文件证书确保该文件属于Avira。该服务会检查证书主题（subject）以及序列号（攻击者可以控制这两个字段），因此我们有可能使用[SigPirate](https://github.com/xorrior/Random-CSharpTools/tree/master/SigPirate)之类的工具克隆合法Avira可执行文件的证书，然后将证书应用到自定义payload上。

为了利用这一点，我们需要执行如下操作：

1、准备payload。这里我们使用名为`Avira.SystemSpeedup.RealTime.Client.exe`的一个.NET程序，用来启动`cmd.exe`；

2、克隆合法Avira文件的证书信息，应用到我们的payload上；

3、编写代码注入正常的Avira进程，加载`Avira.Optimizer.Common.Tools.dll`，实例化`OptimizerHostClient`类；

4、使用实例化对象的公开方法来连接到`AviraOptimizerHost`命名管道，向目标服务发送命令。

payload创建和证书克隆方面的任务交给大家来完成。为了连接到命名管道并发送命令，我们可以复用已有Avira库，添加对`Avira.Optimizer.Common.Tools.dll`的引用，然后导入`Avira.Optimizer.Common.Tools.OptimizerHostClient`命名空间。完成这些操作后，我们可以创建`OptimizerHostCommandsClient`类的实例，调用各种有趣的方法，比如`StartProcess`。

[![](https://p1.ssl.qhimg.com/t01466101b4b0fc2017.png)](https://p1.ssl.qhimg.com/t01466101b4b0fc2017.png)

为了实现LPE，我们只需要将这个程序集（assembly）注入Avira进程中，调用我们的入口点即可，这个任务也留给大家来完成，网上已经有各种公开项目能帮助我们完成该操作，比如[SharpNeedle](https://github.com/ChadSki/SharpNeedle)。

注入Avira进程并执行上述C#代码后，当程序集连接到`AviraOptimizerHost`命名管道发送`StartProcess()`方法，并且`exec`参数指向带有克隆证书的payload时（这里的payload为`Avira.SystemSpeedup.RealTime.Client.exe`），目标服务就会帮我们以`SYSTEM`权限启动`cmd.exe`。

[![](https://p4.ssl.qhimg.com/t011998bc2d1888fb97.png)](https://p4.ssl.qhimg.com/t011998bc2d1888fb97.png)

Avira Optimizer在1.2.0.367版中修复了这个漏洞。分析补丁后，我们发现Avira现在会使用`WinVerifyTrust()`配合路径白名单机制来确保进程启动过程不受影响。



## 0x02 时间线
- 2019年7月23日：向Avira安全团队发送漏洞报告
- 2019年7月24日：Avira确认报告，指出PoC存在一些编译问题
- 2019年7月26日：Avira通过我们提供的PoC重现漏洞
- 2019年8月6日：Avira表示开发人员已解决该问题，询问我们是否要测试补丁
- 2019年8月6日：我们表示可以绕过补丁，并提供新版的PoC及详细信息
- 2019年8月16日：Avira回复开发人员已完成了一个新的补丁，询问我们是否进行测试
- 2019年8月16日：测试了新的补丁，确认已修复问题并向Avira反馈
- 2019年8月27日：官方实时推送补丁
- 2019年8月29日：披露漏洞详细信息