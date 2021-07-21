> 原文链接: https://www.anquanke.com//post/id/205460 


# PrintDemon：详解Print Spooler中的权限提升及持久化技术（Part 2）


                                阅读量   
                                **129413**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者windows-internals，文章来源：windows-internals.com
                                <br>原文地址：[https://windows-internals.com/printdemon-cve-2020-1048/](https://windows-internals.com/printdemon-cve-2020-1048/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01cf96b5206456498d.png)](https://p4.ssl.qhimg.com/t01cf96b5206456498d.png)



## 0x04 Spooler取证

由于`Spooler`采用C++编写（具有丰富的类型信息），我们发现`Spooler`会采用`INIJOB`数据结构来跟踪打印作业。

我们分析了在跟踪`Spooler`信息中设计到的各种数据结构，找到了如下一些数据结构，这些结构都具有可读性较好的特征，可以帮助逆向分析：

[![](https://p0.ssl.qhimg.com/t018309ad4a026eb3ff.png)](https://p0.ssl.qhimg.com/t018309ad4a026eb3ff.png)

进一步研究后，我们发现[GitHub](https://github.com/ZoloZiak/WinNT4)上有`NT4`的源代码，在搜索其中某些类型时，我们发现[`Spltypes.h`](https://github.com/TurboPack/AsyncPro/blob/master/source/PrnDrv/NT4/Mon/SPLTYPES.h)头文件会反复出现。我们从这个文件开始入手，然后根据逆向分析结果手动更新了结构。

首先我们需要在`Localspl.dll`中找到`pLocalIniSpooler`指针，其中包含指向[`INISPOOLER`](https://github.com/Paolo-Maffei/OpenNT/blob/master/printscan/print/spooler/localspl/spltypes.h)的一个指针，部分字段如下：

[![](https://p4.ssl.qhimg.com/t01a9d7b6ec7a2673d2.png)](https://p4.ssl.qhimg.com/t01a9d7b6ec7a2673d2.png)

内存中的布局如下：

[![](https://p3.ssl.qhimg.com/t01964e11447c14d242.png)](https://p3.ssl.qhimg.com/t01964e11447c14d242.png)

从中可知，这个关键数据结构指向第一个[`INIPRINTER`](https://github.com/Paolo-Maffei/OpenNT/blob/master/printscan/print/spooler/localspl/spltypes.h#L123)、[`INIMONITOR`](https://github.com/Paolo-Maffei/OpenNT/blob/master/printscan/print/spooler/localspl/spltypes.h#L269)、[`INIENVIRONMENT`](https://github.com/Paolo-Maffei/OpenNT/blob/master/printscan/print/spooler/localspl/spltypes.h#L110)、[`INIPORT`](https://github.com/Paolo-Maffei/OpenNT/blob/master/printscan/print/spooler/localspl/spltypes.h#L284)、[`INIFORM`](https://github.com/Paolo-Maffei/OpenNT/blob/master/printscan/print/spooler/localspl/spltypes.h#L339)以及[`SPOOL`](https://github.com/Paolo-Maffei/OpenNT/blob/master/printscan/print/spooler/localspl/spltypes.h#L506)。从此处开始，我们可以dump打印机，该打印机开头处为如下数据结构：

[![](https://p1.ssl.qhimg.com/t014811e2c87533ce9d.png)](https://p1.ssl.qhimg.com/t014811e2c87533ce9d.png)

而如果使用我们PoC中`printserver`创建的打印机，在内存中我们可以看到如下布局：

[![](https://p2.ssl.qhimg.com/t01211ee7d68949a3aa.png)](https://p2.ssl.qhimg.com/t01211ee7d68949a3aa.png)

我们可以观察由前面[`INISPOOLER`](https://github.com/Paolo-Maffei/OpenNT/blob/master/printscan/print/spooler/localspl/spltypes.h#L354)链接的`INIPORT`结构，或者直接抓取上图中`INIPRINTER`关联的结构，每个结构都包含如下字段：

[![](https://p4.ssl.qhimg.com/t01067beb3af1916aaa.png)](https://p4.ssl.qhimg.com/t01067beb3af1916aaa.png)

我们PoC创建的端口在内存中也满足该结构，在作业处于假脱机状态时，对应的内存布局如下所示：

[![](https://p5.ssl.qhimg.com/t01017ee0203d8ef169.png)](https://p5.ssl.qhimg.com/t01017ee0203d8ef169.png)

最后，`INIPORT`和`INIPRINTER`都会指向我们创建的[`INIJOB`](https://github.com/Paolo-Maffei/OpenNT/blob/master/printscan/print/spooler/localspl/spltypes.h#L394)。该结构如下所示：

[![](https://p5.ssl.qhimg.com/t012fdf6bbc6e180cf2.png)](https://p5.ssl.qhimg.com/t012fdf6bbc6e180cf2.png)

这个结构大家看起来应该非常熟悉，这是影子作业文件中许多相同数据的不同表现形式，也是`EnumJob`和`GetJob`所返回的内容。我们创建的作业在内存中的布局如下：

[![](https://p5.ssl.qhimg.com/t015bf3291e04a3a1bb.png)](https://p5.ssl.qhimg.com/t015bf3291e04a3a1bb.png)

通过定位并枚举这些结构，我们就可以了解`Spooler`的大致流程，只要`Spoolsv.exe`仍在运行，没有被人篡改过。

然而，正如我们下文分析的，我们并不能真正依赖这些信息。



## 0x05 持久化

由于我们知道`Spooler`可以在重启后（以及服务因为各种原因被退出时）打印作业，因此我们认为系统中存在一些逻辑，可以存储影子作业文件、从中创建`INIJOB`结构。

载入IDA后，我们发现函数名较为直白的一个函数以及循环逻辑，该函数会在本地`Spooler`初始化阶段被调用：

[![](https://p0.ssl.qhimg.com/t0177a6816557f7bb32.png)](https://p0.ssl.qhimg.com/t0177a6816557f7bb32.png)

该过程会处理与`Spooler`自身有关的影子作业文件（服务端作业），然后枚举每个`INIPRINTER`，获取其spooler目录（通常是默认值），然后处理其对应的影子作业文件数据。

该过程由`ProcessShadowJobs`完成，主要执行如下循环：

[![](https://p2.ssl.qhimg.com/t0126cc0327552d4dc2.png)](https://p2.ssl.qhimg.com/t0126cc0327552d4dc2.png)

其实上述代码在使用`FindFirstFile` API时，会用到`*.SHD`通配符，因此匹配该扩展名的每个文件会被发送到`ReadShadowJob`。这样一来就打破了我们原先的假设：这些文件并不需要遵循我们前面描述的命名约定。考虑到打印机可以拥有自己的spooler目录，这意味着这些文件可以存放在各个位置。

观察`ReadShadowJob`，可以看到系统似乎只对头部中存在的信息做了基本的验证，而许多字段为可选字段。我们通过十六进制编辑器手动构造了一个自定义影子作业文件，只满足关联到打印机的最小数据需求，然后重启`Spooler`，使用Process Monitor来观察。我们还创建了具有相同名称的匹配`.SPL`文件，其中写入了一个简单的字符串。

我们首先注意到`Spooler`会扫描`FPnnnnn SPL`文件，这些文件通常与EMF作业有关（`FP`的全称为“File Pool”）。然后，`Spooler`会扫描`SHD`文件，找到我们提供的文件，打开匹配的`SPL`文件，然后继续寻找更多文件，直到返回`NO MORE FILES`结果。

[![](https://p2.ssl.qhimg.com/t0197c2db798eb2abef.png)](https://p2.ssl.qhimg.com/t0197c2db798eb2abef.png)

在如下调用栈中，我们可以看到系统会调用`DeleteOrphanFiles` API来清理`FP`文件：

[![](https://p3.ssl.qhimg.com/t014f0e48748cf38f49.png)](https://p3.ssl.qhimg.com/t014f0e48748cf38f49.png)

对于`SHD`文件，从如下调用栈我们可知，`ProcessShadowJobs`会调用`ReadShadowJob`，这与我们在IDA中分析的结果一样。

[![](https://p2.ssl.qhimg.com/t018df1144563ca1708.png)](https://p2.ssl.qhimg.com/t018df1144563ca1708.png)

那么我们设置的SHD文件有什么效果呢？我们可以来观察前面创造的打印机的打印队列：

[![](https://p5.ssl.qhimg.com/t0108e56241b414e18c.png)](https://p5.ssl.qhimg.com/t0108e56241b414e18c.png)

看上去是不是不太妙？双击打印作业，我们得到的基本上是无用的信息：

[![](https://p3.ssl.qhimg.com/t01aba47975af88abe8.png)](https://p3.ssl.qhimg.com/t01aba47975af88abe8.png)

由于作业看上去似乎处于不正常状态，数据大小为`0`字节，大家可能会认为恢复该作业后，打印任务会以某种方式中断或者崩溃，我们也这么认为，然而实际发生的操作如下所示：

[![](https://p1.ssl.qhimg.com/t01d5d9b3db75ab1517.png)](https://p1.ssl.qhimg.com/t01d5d9b3db75ab1517.png)

这里一切顺利，系统会将整个spool文件写入我们的打印机端口，无视`SHADOWFILE_4`中的实际大小值。更有趣的是，如果我们手动调用`ReadPrinter`，那么并不会看到有任何数据写入，这是因为即使`PortThread`没有检查该值，RPC API也会检查这个值。

根据目前的分析，我们只需要对文件系统做非常细微的修改，就可以实现不属于任何进程的文件复制/写入行为（即使重启后也能完成），除非某些EDR/DFIR软件会出于某些原因来监控`SHD`文件的创建操作，并且意识到了该文件的重要性。通过精心构造的端口名，我们可以让`Spooler`帮我们将PE文件释放到磁盘上的任意位置（假设我们具备该该位置的访问权限）。

但当我们思考一个问题后，事情开始变得奇妙起来：“在重启后，`Spooler`怎么还能模拟原始的用户呢（特别是当SHD文件中的数据被设为`NULL`时）？”



## 0x06 自模拟权限提升（SIPE）

由于Process Monitor可以显示模拟令牌，因此我们选择双击`CreateFile`事件查看。前面我们也执行过这个操作，当时`PortThread`正在模拟某个用户，但现在呢？如下图所示：

[![](https://p3.ssl.qhimg.com/t0120afc1d00d39097e.png)](https://p3.ssl.qhimg.com/t0120afc1d00d39097e.png)

`Spooler`正在模拟的是`SYSTEM`！看来代码中没有考虑到用户可能会注销、重新启动，或者`Spooler`崩溃的情况，现在我们可以写入`SYSTEM`能够写入的任何位置。通过查看`NT4`源码，我们发现[`PrintDocumentThruPrintProcessor`](https://github.com/Mooliecool/windows/blob/9e211d0cd5cacbd62c9c6ac764a6731985d60e26/nt-4.0/private/windows/spooler/localspl/port.c#L867)函数的确会直接写入目标端口。

但我们毕竟不能信任GitHub上已有30个年头的源码，因此我们打开熟悉的IDA，看到了在震网时期添加的如下代码：

[![](https://p1.ssl.qhimg.com/t01fc5ab4a7d8d8bec3.png)](https://p1.ssl.qhimg.com/t01fc5ab4a7d8d8bec3.png)

`CanUserAccessTargetFile`会立即检查`hToken`是否为`NULL`，如果满足该条件，则会返回`FALSE`，并将`LastError`设置为`ERROR_ACCESS_DENIED`。

游戏结束了，代码看上去是安全的。但显然有些不对劲，因为我们的确看到写入操作会通过“模拟”`SYSTEM`来完成。

这里有个非常隐蔽的微妙之处。注意`CreateJobEntry`中的如下代码，该代码最终将初始化`INIJOB`，并且会在需要的时候设置`JOB_PRINT_TO_FILE`。

[![](https://p2.ssl.qhimg.com/t0122366702bf8abef3.png)](https://p2.ssl.qhimg.com/t0122366702bf8abef3.png)

在典型的打印对话框中，当用户选择“打印到文件”复选框时，打印作业才会以文件为目标。另一方面，打印端口这类文件则会完全跳过这个检查。

现在我们可以试着不去管`C:\Windows\Tracing\`，而是选择`C:\Windows\System32\Ualapi.dll`作为打印端口（之所以选择该路径，大家可以参考我们之前的一篇研究[文章](https://windows-internals.com/faxing-your-way-to-system/)）。

[![](https://p0.ssl.qhimg.com/t01c1d2bbab31d42854.png)](https://p0.ssl.qhimg.com/t01c1d2bbab31d42854.png)

并没有尝试成功，可以在Process Monitor中观察到如下输出：

[![](https://p1.ssl.qhimg.com/t014545b91755b24901.png)](https://p1.ssl.qhimg.com/t014545b91755b24901.png)

使用`PortIsValid`命令时对`XcvData`的调用栈如下图所示。根据“Event”标签页提供的信息，`Spooler`现在正在模拟用户，而用户并不具备`c:\Windows\System32`的写入权限。

[![](https://p1.ssl.qhimg.com/t01c5c3d246fd8a3229.png)](https://p1.ssl.qhimg.com/t01c5c3d246fd8a3229.png)

因此，虽然根据前面分析，我们可以让`Spooler`在重启或者服务启动后，没有通过模拟操作将文件写入磁盘中，但由于我们首先要创建指向特权目录的端口，因此目前我们还不清楚这个技巧有什么作用。作为`Administrator`，这是一种很好的规避及持久化技巧，但似乎也仅此为止。

在各种尝试如何滥用这个行为时（我们的确找到了一些方法），最终我们发现了一种非常简单的利用方式，但来自SafeBreach实验室的小伙伴们已捷足先登，并且拿到了一个编号：CVE-2020-1048。



## 0x07 CVE-2020-1048：客户端端口检查漏洞

这个bug实在太简单，只需要一条PowerShell命令就能利用。

如果大家翻一翻上文，观察[`Add-PrinterPort`](https://docs.microsoft.com/en-us/powershell/module/printmanagement/add-printerport?view=win10-ps)后`Spoolsv.exe`对注册表的操作，我们可以看到一个熟悉的`XcvData`调用栈，其中会直接跳到`XcvAddPort`/`DoAddPort`，并不涉及到`DoPortIsValid`。一开始我们认为访问注册表的操作会在访问文件后完成（我们在Process Monitor中屏蔽了该类型），并且认为端口验证已经完成。然而，当我们启用监控系统事件功能后，却没有发现`CreateFile`。

然而如果通过UI来操作，我们会看到这个调用栈、文件系统访问，然后继续添加端口。

事实就是这么简单，UI对话框具有客户端检查步骤，而服务端没有，并且PowerShell的WMI Print Provider模块也没有。

这并不是因为PowerShell/WMI有什么特殊访问权限。我们PoC中的代码通过`AddPort`命令来使用`XcvData`，可以直接让`Spooler`添加端口，没有经过检查步骤。

正常情况下，这并不是什么大问题，因为后续的所有打印作业操作都将使用用户的令牌，导致文件访问操作失败。

然而，如果我们重启主机，或者以某种方式kill掉`Spooler`，那情况就有所不同。考虑到`Spooler`的复杂性以及悠久历史（并且拥有许多第三方驱动），普通用户想完成该任务也不会太困难。

现在我们可以使用未打补丁的系统，在PowerShell窗口中输入`Add-PrinterPort -Name c:\windows\system32\ualapi.dll`，随后我们就能在系统上留下一个持久化后门。现在我们只需要将一个`MZ`文件“打印”到刚刚创建的打印机，就能大功告成。

当打上补丁后，微软现在将`PortIsValid`检查逻辑移到了`LcmXcvDataPort`中，这种利用方式将不再起作用。即便如此，如果攻击者已经创建了恶意端口，那么用户仍然可以执行这种“打印”操作。这是因为`CanUserAccessTargetFile`的检查逻辑并不适用于“指向文件的端口”，只适用于“打印到文件”的场景。



## 0x08 总结

由于这个bug比较简单，历史久远，因此可以纳入我们最喜欢的Windows历史漏洞之一，至少可以排名前五。这个bug比较有戏剧性：存在于原始版本的Windows中，虽然在震网事件后安全性被强化，但仍然留下被攻击的口子。当我们提交与其他一些相关的bug后（根据漏洞披露规则，这里我们不再提供更多信息），我们认为系统底层的模拟问题应当需要解决，但看上去这似乎是系统正常的一个设计理念。

安装针对`PortIsValid`的补丁后，我们无法滥用原先的模拟行为，但已存在的端口仍然可以被利用，希望这篇文章能帮助业界提高警觉。随着官方补丁的公布，攻击者可能很快就会发现问题所在：只要在[Diaphora](https://github.com/joxeankoret/diaphora)中载入`Localspl.dll`，那么针对`PortIsValid`的两行调用很快就会浮出水面，毕竟这是文件中的唯一一处更改。

我们建议大家马上执行如下操作：

1、打补丁。不管是交互式用户还是有限的远程&lt;-&gt;本地上下文环境中，这个bug都很容易利用。

2、扫描基于文件的端口。可以在PowerShell中使用[`Get-PrinterPorts`](https://docs.microsoft.com/en-us/powershell/module/printmanagement/get-printerport?view=win10-ps)，或者访问注册表中的`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Ports`。如果端口中包含文件路径（特别是以`.DLL`或者`.EXE`扩展名结尾的路径），那么更应该引起警觉。
