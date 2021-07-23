> 原文链接: https://www.anquanke.com//post/id/205459 


# PrintDemon：详解Print Spooler中的权限提升及持久化技术（Part 1）


                                阅读量   
                                **144458**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者windows-internals，文章来源：windows-internals.com
                                <br>原文地址：[https://windows-internals.com/printdemon-cve-2020-1048/](https://windows-internals.com/printdemon-cve-2020-1048/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01cf96b5206456498d.png)](https://p4.ssl.qhimg.com/t01cf96b5206456498d.png)



## 0x00 前言

前面我们已经与大家分享过FaxHell相关技术细节，随着微软在周二补丁日例行发布安全公告后（包括[`CVE-2020-1048`](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1048)的补丁），现在我们可以与大家继续分享[Windows Print Spooler](https://docs.microsoft.com/en-us/windows/win32/printdocs/print-spooler)的技术细节，以及如何利用Print Spooler来实现权限提升、绕过EDR规则、实现持久化等。Print Spooler目前仍是最古老的Windows组件之一，从Windows NT 4以来基本没有什么变化。即使曾经被Stuxnet（震网）病毒滥用过（使用过我们即将与大家一起分析的一些API），Print Spooler仍然没有经过特别全面的审查。之前有个第三方研究团队首先[分析](http://blog.ismaelvalenzuela.com/wp-content/uploads/2009/11/my_erp_got_hacked_1.pdf)过Print Spooler，发现了微软未发现过的利用点，最终被Stuxnet幕后团队所使用。



## 0x01 背景知识

虽然我们比较喜欢深入分析Windows组件的各种精妙之处，但还是想尽量保证简洁性，只重点关注这些问题的严重性，分析如何简单滥用/利用这些问题，同时也会给防御方提供一些小建议。

首先我们来简单看一下打印过程，这里我们并不会讨论监视器、服务提供程序或者处理器，只讨论最基础的打印流程。

首先，打印机必须至少具备两个元素：

1、打印机端口：之前是`LPT1`，现在是USB口或者`TCP/IP`端口（以及地址）。

> 某些人可能知道还存在`FILE:`形式，这意味着打印机可以将内容打印到文件（Windows 8及以上系统为`PORTPROMPT:`）。

2、打印机驱动：之前这是一个内核模式组件，在新的`V4`模型下，十多年来已改成用户模式下工作。

由于`Spooler`服务（在`Spoolsv.exe`中实现）以`SYSTEM`权限运行，并且网络可达，因此这两个元素成功吸引了许多人的注意，尝试发起所有有趣的攻击，包括：

1、希望`Spooler`能将文件[打印](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-3239)到某个特权位置；

2、[加载](https://docs.microsoft.com/en-us/security-updates/SecurityBulletins/2016/ms16-087?redirectedfrom=MSDN)恶意的“打印机驱动”；

3、通过`Spooler` RPC API远程投放文件；

4、从远程系统注入“打印机驱动”；

5、[滥用](https://www.exploit-db.com/exploits/43465)EMF/XPS spooler文件中的文件解析bug来获得代码执行权限。

以上大多数尝试的确发现过bug，微软也针对某些bug加强了防御措施。即便如此，系统中还是存在不少逻辑问题，有些甚至是设计上的缺陷，会导致出现一些有趣的行为。

回到我们的话题，为了滥用打印机，我们首先必须加载一个打印机驱动。正常情况下，大家都会认为这需要高权限才能执行，并且有些MSDN页面还提示我们需要[`SeLoadDriverPrivilege`](https://docs.microsoft.com/en-us/windows/win32/secauthz/privilege-constants)。然而从Vista开始，为了便于普通用户账户操作（并且现在会在用户模式下运行），因此实际情况会比较复杂。只要目标驱动是预先存在的内置驱动，我们不需要特权就能安装打印机驱动。

我们先来安装最简单的一个驱动：`Generic / Text-Only`驱动。（以普通用户权限）打开PowerShell窗口，然后输入：

```
Add-PrinterDriver -Name "Generic / Text Only"
```

接着枚举已安装的驱动：

```
&gt; Get-PrinterDriver

Name                                PrinterEnvironment MajorVersion    Manufacturer
----                                ------------------ ------------    ------------
Microsoft XPS Document Writer v4    Windows x64        4               Microsoft
Microsoft Print To PDF              Windows x64        4               Microsoft
Microsoft Shared Fax Driver         Windows x64        3               Microsoft
Generic / Text Only                 Windows x64        3               Generic
```

如果想用C语言来完成，也可以使用如下语句：

```
hr = InstallPrinterDriverFromPackage(NULL, NULL, L"Generic / Text Only", NULL, 0);
```

接下来是将新打印机与某个端口绑定。这里比较有趣的是（官方没有详细说明）：端口也可以使用文件，并且这与“打印到文件”有所不同。此时是一个文件端口，这是完全不同的一个概念。我们只需要在PowerShell中使用如下一行命令就可以（这里我们用的是全局可写的一个目录）：

```
Add-PrinterPort -Name "C:\windows\tracing\myport.txt"
```

获取打印机端口：

```
&gt; Get-PrinterPort | ft Name

Name
----
C:\windows\tracing\myport.txt
COM1:
COM2:
COM3:
COM4:
FILE:
LPT1:
LPT2:
LPT3:
PORTPROMPT:
SHRFAX:
```

如果想用C来完成，我们可以有两种选择。我们可以使用[`AddPortW`](https://docs.microsoft.com/en-us/windows/win32/printdocs/addport) API，弹出窗口要求用户输入端口名。我们并不需要设计GUI，可以传入`NULL`作为`hWnd`参数的值，当用户创建端口后，程序才会解除阻塞状态。UI如下所示：

[![](https://p5.ssl.qhimg.com/t01073c3298728d6cfc.png)](https://p5.ssl.qhimg.com/t01073c3298728d6cfc.png)

另一种方法是使用[`XcvData`](https://docs.microsoft.com/en-us/previous-versions/ff564255(v%3Dvs.85)) API来手动复制以上窗口的逻辑，如下所示：

```
PWCHAR g_PortName = L"c:\\windows\\tracing\\myport.txt";
dwNeeded = ((DWORD)wcslen(g_PortName) + 1) * sizeof(WCHAR);
XcvData(hMonitor,
        L"AddPort",
        (LPBYTE)g_PortName,
        dwNeeded,
        NULL,
        0,
        &amp;dwNeeded,
        &amp;dwStatus);
```

这里比较复杂的是获取`hMonitor`，需要一些神秘知识：

```
PRINTER_DEFAULTS printerDefaults;
printerDefaults.pDatatype = NULL;
printerDefaults.pDevMode = NULL;
printerDefaults.DesiredAccess = SERVER_ACCESS_ADMINISTER;
OpenPrinter(L",XcvMonitor Local Port", &amp;hMonitor, &amp;printerDefaults);
```

以上代码中存在`ADMINISTER`字样，因此大家可能会觉得需要`Administrator`权限，但事实并非如此：任何人都可以添加端口。不过如果我们传入不具备访问权限的路径，将会得到“访问被拒绝”错误。稍后我们再讨论这一点。

代码处理完毕后，别忘了调用`ClosePrinter(hMonitor)`。

现在我们已经拿到了一个端口和一个打印机驱动，我们只需要利用这两个元素就能创建并绑定一个打印机。这个过程同样不需要特权用户，只需要如下一行PowerShell命令：

```
Add-Printer -Name "PrintDemon" -DriverName "Generic / Text Only" -PortName "c:\windows\tracing\myport.txt"
```

然后使用如下语句来检查效果：

```
&gt; Get-Printer | ft Name, DriverName, PortName

Name DriverName PortName
---- ---------- --------
PrintDemon Generic / Text Only C:\windows\tracing\myport.txt
```

对应的C代码如下：

```
PRINTER_INFO_2 printerInfo = `{` 0 `}`;
printerInfo.pPortName = L"c:\\windows\\tracing\\myport.txt";
printerInfo.pDriverName = L"Generic / Text Only";
printerInfo.pPrinterName = L"PrintDemon";
printerInfo.pPrintProcessor = L"WinPrint";
printerInfo.pDatatype = L"RAW";
hPrinter = AddPrinter(NULL, 2, (LPBYTE)&amp;printerInfo);
```

拿到打印机句柄后，我们可以开始思考该句柄的用途。此外，知道打印机名称后，我们可以使用[`OpenPrinter`](https://docs.microsoft.com/en-us/windows/win32/printdocs/openprinter)来获取打印机句柄。

最后一步就是执行打印操作，在PowerShell中也只需要一条命令：

```
"Hello, Printer!" | Out-Printer -Name "PrintDemon"
```

然而如果我们查看文件内容，会看到一些奇怪的数据：

```
0D 0A 0A 0A 0A 0A 0A 20 20 20 20 20 20 20 20 20
20 48 65 6C 6C 6F 2C 20 50 72 69 6E 74 65 72 21
0D 0A …
```

如果在Notepad中打开，我们能更直观地了解这些数据：PowerShell认为这是一个真实的打印机，因此会按照Letter或（A4）格式来设定边距，在顶部添加几个新行，然后在字符串左侧留出左边距。

我们可以在C语言中控制具体行为，但通常Win32应用都会以这种方式来打印，因为这些应用都认为这是真实的打印机。

那么在C语言中如何实现相同的效果呢？我们有两种选择，这里我们介绍的是更加简单也更常用的方法：使用[GDI](https://docs.microsoft.com/en-us/windows/win32/printdocs/writeprinter) API，在内部创建一个打印任务，处理我们的payload。

```
DOC_INFO_1 docInfo;
docInfo.pDatatype = L"RAW";
docInfo.pOutputFile = NULL;
docInfo.pDocName = L"Document";
StartDocPrinter(hPrinter, 1, (LPBYTE)&amp;docInfo);

PCHAR printerData = "Hello, printer!\n";
dwNeeded = (DWORD)strlen(printerData);
WritePrinter(hPrinter, printerData, dwNeeded, &amp;dwNeeded);

EndDocPrinter(hPrinter);
```

现在文件内容将会简单存储我们提供的字符串。

总结一下，现在我们了解了一些简单的非特权PowerShell命令以及作用相同的C代码，我们可以假装创建一个打印机，向文件系统中写入数据。下面我们可以使用Process Monitor了解幕后的具体操作。



## 0x02 文件写入

来看一下当运行这些命令后系统会执行哪些操作。我们跳过驱动的“安装”过程（该过程涉及一大堆PnP以及Windows服务栈操作），从添加端口开始观察：

[![](https://p3.ssl.qhimg.com/t016961c13b550c6509.png)](https://p3.ssl.qhimg.com/t016961c13b550c6509.png)

从图中可知：打印机端口实际上是注册表值，路径为`HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Ports`。显然，只有特权用户才能写入该键值，但`Spooler`服务通过RPC帮我们完成该操作，调用栈如下所示：

[![](https://p4.ssl.qhimg.com/t01840468f2ee9ec7c0.png)](https://p4.ssl.qhimg.com/t01840468f2ee9ec7c0.png)

打印机创建过程如下：

[![](https://p0.ssl.qhimg.com/t013022ead911ded059.png)](https://p0.ssl.qhimg.com/t013022ead911ded059.png)

这里主要操作依然涉及到注册表。注册表中的打印机如下所示，注意其中的`Port`值，对应的是我们的文件路径。

[![](https://p3.ssl.qhimg.com/t0196e2e00fcf13209e.png)](https://p3.ssl.qhimg.com/t0196e2e00fcf13209e.png)

接着观察打印文档时PowerShell命令的处理过程。涉及到的文件系统完整活动如下所示（这里不再涉及到注册表），其中我们标出了比较有趣的部分操作：

[![](https://p2.ssl.qhimg.com/t01177071dc8ee8daf6.png)](https://p2.ssl.qhimg.com/t01177071dc8ee8daf6.png)

启用spooling后，打印数据并没有直接发送到打印机。此时任务处于假脱机状态（spooled），最终导致系统创建一个spool文件。默认情况下，该文件位于`c:\windows\system32\spool\PRINTERS`目录中，但实际上对于每个系统和每个打印机，这个值都可以自定义（这是值得深入分析的一个点）。

默认情况下，对于EMF打印操作，文件名为`FPnnnnn.SPL`，对于RAW打印操作，文件名为`nnnnn.SPL`。`SPL`文件本质上是发送给打印机的所有数据的一个副本，换句话说，该文件中只包含`Hello, printer!`字符串。

还有个更有趣的“影子作业文件”（shadow job file）。由于打印作业不一定实时处理，因此系统需要用到该文件。在手动处理或者打印机出问题时，这类文件可以被出错、被调度、被暂停。在此期间，考虑到第三方打印机驱动可能存在bug、打印作业在重启后需要保留，因此作业本身相关的信息不会只保留在`Spoolsv.exe`的内存中。如下所示，`Spooler`会写入该文件，文件的数据结构多年来发生了一些变化，现在采用的是`SHADOWFILE_4`数据结构，详细结构可参考我们的[GitHub页面](https://github.com/ionescu007/PrintDemon)。

[![](https://p1.ssl.qhimg.com/t014fef1760b4bd94e7.png)](https://p1.ssl.qhimg.com/t014fef1760b4bd94e7.png)

在下文的持久化场景中，我们将详细介绍影子作业文件的作用。

随后是创建文件操作。不幸的是，Process Monitor始终显示的是主令牌，如果我们双击该事件，可以看到该操作通过模拟（impersonation）方式来完成：

[![](https://p5.ssl.qhimg.com/t01b364c1c9b72be1a2.png)](https://p5.ssl.qhimg.com/t01b364c1c9b72be1a2.png)

这可能是`Spooler`服务的一项核心安全功能：如果没有该操作，我们就可以在磁盘上的任意特权位置中创建打印机端口，然后让`Spooler`帮我们将数据“打印”到该位置，从而实现任意文件系统读写原语。然而后面我们会提到，实际情况要更为复杂一些。从EDR角度来看，我们可以获取目标用户的**某些**信息。

最后，当完成写操作后，（默认情况下）spool文件和影子作业文件都会被删除，如下`SetDisposition`调用所示：

[![](https://p0.ssl.qhimg.com/t01ece495d177ea2343.png)](https://p0.ssl.qhimg.com/t01ece495d177ea2343.png)

目前我们演示了如何通过打印功能，在`Spooler`服务的帮助下往磁盘上（我们能访问的）位置写入数据。此外，我们也知道文件创建操作通过模拟上下文来完成，可以获取该操作背后的原始用户。如果检查作业本身，我们也能得到用户名和主机名。基于这些信息，从数字取证角度来看，攻击者似乎很难隐藏自身踪迹。

很快我们就能打破上述结论，但首先我们来看一下利用这种行为的一种有趣方式。



## 0x03 IPC

`Spooler`有个最有趣（也是最有用）的一个特性：可以用来作为进程间、跨用户甚至重启后（以及潜在的网络）的通信渠道。我们实际上可以将打印机看成一个安全对象（从技术角度来看，打印机作业也是安全对象，但官方并没有公开该对象），然后可以通过两种方式在其中发起读写操作：

1、使用GDI API，然后发送[`ReadPrinter`](https://docs.microsoft.com/en-us/windows/win32/printdocs/readprinter)和[`WritePrinter`](https://docs.microsoft.com/en-us/windows/win32/printdocs/writeprinter)命令。
- 首先，我们必须成对调用[`StartDocPrinter`](https://docs.microsoft.com/en-us/windows/win32/printdocs/startdocprinter)和[`EndDocPrinter`](https://docs.microsoft.com/en-us/windows/win32/printdocs/enddocprinter)，创建打印机作业和spool数据。
- 使用[`SetJob`](https://docs.microsoft.com/en-us/windows/win32/printdocs/setjob)让作业一开始就处于暂停状态（`JOB_CONTROL_PAUSE`），这样spool文件就会保持在文件系统中。
- 前一个API将会返回一个打印机作业ID，然后客户端可以使用特定语法，添加一个后缀（`,Job n`），将其作为打印机名参数来调用[`OpenPrinter`](https://docs.microsoft.com/en-us/windows/win32/printdocs/openprinter)，这样就能打开打印机作业，而不是打开打印机。
> Client可以使用[`EnumJobs`](https://docs.microsoft.com/en-us/windows/win32/printdocs/enumjobs) API来枚举所有打印机作业，根据某些属性找到希望读取的作业。

2、使用打印作业raw API，在获取spool文件句柄后调用[`WriteFile`](https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-writefile)。
- 一旦完成写操作，调用[`ScheduleJob`](https://docs.microsoft.com/en-us/windows/win32/printdocs/schedulejob)使打印作业可见。
- 客户端继续调用[`ReadPrinter`](https://docs.microsoft.com/en-us/windows/win32/printdocs/readprinter)。
那么这么操作与传统的文件I/O相比有什么优势呢？我们总结了如下几点：

1、如果完全采用GDI方法，那么整个过程不会导入明显的I/O API；

2、采用[`ReadPrinter`](https://docs.microsoft.com/en-us/windows/win32/printdocs/readprinter)和[`WritePrinter`](https://docs.microsoft.com/en-us/windows/win32/printdocs/writeprinter) 时的读写操作并没有在模拟上下文中进行，这意味着这些操作看上去似乎由以`SYSTEM`运行的`Spoolsv.exe`来发起。

> 这也可能意味着我们能够读写某个`spooler`文件，并且该文件位于我们通常不具备访问权限的某个位置。

3、我们怀疑到目前为止，没有多少安全产品检查过`spooler`文件。

> 并且如果采用正确的API/修改注册表，我们可以将为自己的打印机定制`spooler`目录。

4、取消作业后，我们的数据会立即从服务上下文中删除。

5、恢复作业后，我们能拿到目标文件副本。目前据前文分析，该行为并没有通过模拟来完成。

我们在[GitHub](https://github.com/ionescu007/PrintDemon)上发布了一个简单的`printclient`以及`printserver`应用，其中实现了客户端/服务端机制，可以利用前文介绍的知识在两个进程间通信。。

来试着运行服务端，如下图所示：

[![](https://p2.ssl.qhimg.com/t01cc31390f5481fe75.png)](https://p2.ssl.qhimg.com/t01cc31390f5481fe75.png)

与预期相符，我们可以创建spool文件，并且可以在打印队列中看到我们的作业，这显然留下不少线索，可以帮防御方定位。

[![](https://p0.ssl.qhimg.com/t01d4d8729cc6a196b7.png)](https://p0.ssl.qhimg.com/t01d4d8729cc6a196b7.png)

在客户端，我们可以运行程序，观察输出结果，如下图所示：

[![](https://p0.ssl.qhimg.com/t0138b66ee2dc2acef4.png)](https://p0.ssl.qhimg.com/t0138b66ee2dc2acef4.png)

顶部的输出信息来自于打印机API：我们使用[`EnumJob`](https://docs.microsoft.com/en-us/windows/win32/printdocs/enumjobs)和[`GetJob`](https://docs.microsoft.com/en-us/windows/win32/printdocs/getjob)来获取我们希望获取的信息。这里我们将更进一步，查看存储在影子作业中的信息。研究过程中，我们找到了一些有趣的差异点：

1、即使根据MSDN的说明，该API始终会返回`NULL`，但打印作业实际上具有安全描述符。

如果我们在影子作业中将其清零，导致`Spooler`无法恢复/写入数据。

2、有些数据显示的值与实际值不一致。

比如，影子作业中的`Status`字段具有不同的含义，并且包含未通过API公开的内部状态。

另外，API中提示`StartTime`和`UntilTime`的值为`0`，实际上影子文件中的值为`60`。

我们想更进一步澄清影子文件数据的读取方式及读取时机，以及什么时候会使用`Spooler`中的内部状态。大家都知道，Service Control Manager在内存中有一个服务数据库，但也会在注册表中备份了服务信息，我们认为`Spooler`同样采用了这种方式。
