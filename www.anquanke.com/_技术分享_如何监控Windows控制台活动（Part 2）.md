> 原文链接: https://www.anquanke.com//post/id/86795 


# 【技术分享】如何监控Windows控制台活动（Part 2）


                                阅读量   
                                **118854**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2017/08/monitoring-windows-console-activity-part-two.html](https://www.fireeye.com/blog/threat-research/2017/08/monitoring-windows-console-activity-part-two.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01ea37c2865bfd2e2c.jpg)](https://p0.ssl.qhimg.com/t01ea37c2865bfd2e2c.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**传送门**

[**【技术分享】如何监控Windows控制台活动（Part 1）**](http://bobao.360.cn/learning/detail/4371.html)

**<br>**

**一、前言**

在这篇文章中，我们会继续讨论过去几年中Windows在控制台架构方面的具体实现，重点分析了当前Windows版本中控制台的实现机制。读者可以阅读之前一篇[文章](https://www.fireeye.com/blog/threat-research/2017/08/monitoring-windows-console-activity-part-one.html)来了解前文内容。

**<br>**

**二、捕捉相关数据**

在我们研究如何捕捉控制台数据之前，我们可以先来了解一下捕捉进程参数的方法。有人会问，我们为什么不能检查每个进程的**进程环境块**（Process Environment Block ，PEB）来获取命令行参数？当攻击者在目标主机上执行任务时，我们通过这种方式就能获得攻击者所用的命令参数。然而，如果攻击者以交互式方式来运行命令行工具，这种情况下我们就无法通过这种方法获取攻击者发送工具的具体命令参数。

比如，**mimikatz**是一款非常流行的凭据导出工具，攻击者可以使用图1所示的命令来运行这款工具。攻击者可以使用这个工具的所有功能，比如凭据窃取或者哈希导出功能等。此外，我们很难了解攻击者攻击的是哪个用户账户，因为我们看不到mimikatz在运行时的输出结果。从控制台中收集这类信息是非常有必要的一件事情，稍后我们会向大家介绍具体方法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/1.png)[![](https://p2.ssl.qhimg.com/t01dfde89e1a4ff69cd.png)](https://p2.ssl.qhimg.com/t01dfde89e1a4ff69cd.png)

图1. 利用Process Explorer观察运行mimikatz的命令行参数

现在我们已经知道控制台的工作原理，那么我们具体要怎么做才能捕捉到相关数据？想在Windows 7或者更早版本的系统上完成这个任务貌似是非常困难的一件事情。也许我们可以同步前文提到过的**ConsoleEvent**对象，读取包含该数据的共享对象，以便捕捉相关数据（虽然这个想法有点不切实际）。还有另一种方法，我们可以发送必要的ALPC消息来访问命令数据，实际上kernel32.dll中有个导出API可以帮我们完成这个操作。**GetConsoleCommandHistory**函数可以从当前控制台会话中提取相关命令，但前提是我们必须运行在客户端进程的上下文环境中，才能使用这个API。这就需要我们插入进程或者使用其他黑科技方法，但这些方法都不是特别优雅。

Windows 8及更高版本的操作系统使用的控制台驱动大大简化了我们的工作量。由于驱动向外提供了一个设备对象，我们可以附加到这个对象上并使用过滤条件。现在我们需要从细节上理解这种功能的实现机制，也要理解数据所使用的具体格式。

观察驱动的入口点，我们可以看到非常标准的一些驱动初始化代码。其中最为有趣的是Fast I/O设备控制调度函数的初始化。内核会在调用标准的基于IRP的IRPMJDEVICE_CONTROL调度函数之前调用这个函数，然后该函数可以选择将操作标记为已完成状态，或者将其传回并生成IRP数据包。ConDrv的入口点如图2所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/2.png)[![](https://p0.ssl.qhimg.com/t0103d8ca86a50e5cee.png)](https://p0.ssl.qhimg.com/t0103d8ca86a50e5cee.png)

图2. Windows控制台驱动（ConDrv）的入口点

快速检查用户代码后，我们发现我们所关心的所有数据会经过**NtDeviceIoControlFile**传输给ConDrv。此外，**NtReadFile**以及**NtWriteFile**函数也会将这些数据传输给ConDrv设备，然而，当Conhost在发送或请求新数据时，这些数据同样会经过NtDeviceIoControlFile函数的处理。因此，只要过滤FastIoDeviceControl例程，就可以找到我们想要的I/O数据（如图3所示）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/3.png)[![](https://p2.ssl.qhimg.com/t0164d21edaf5385729.png)](https://p2.ssl.qhimg.com/t0164d21edaf5385729.png)

图3.[FastIODeviceControl](http://www.osronline.com/article.cfm?id=166)分发函数的声明

分析该函数后，我们发现一行switch语句，用来处理传入的IOCTL代码，这些代码中包含用户模式可用的大部分功能。IOCTL代码与控制台的数据读取及写入有关，处理IOCTL代码的相关代码如图4所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/4.png)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01aca93443c863005c.png)

ConDrv可以支持许多IOCTL代码，但目前我们只关心其中一部分，具体清单如表1所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/5.png)[![](https://p5.ssl.qhimg.com/t01faf73413ab7e0ba3.png)](https://p5.ssl.qhimg.com/t01faf73413ab7e0ba3.png)

表1. ConDrv支持的部分IOCTL代码

这些IOCTL代码中，有两个最为有趣，这两个代码负责客户端与服务器之间数据的读取与写入（0x50000F以及0x500013）。我们可以在**condrv!CdpFastIoDeviceControl**上设置断点，然后在命令提示符中输入一些文本，这样就能触发conhost.exe进程上下文中的断点。

当Conhost往cmd.exe发送命令字符串时，根据图3的函数声明，我们可以提取出相关参数的地址信息，如输入缓冲区、缓冲区大小以及IOCTL代码。在图5中，我们分别用黄色、蓝色以及绿色将这些参数高亮标出（注意：输入缓冲区是映射到Conhost中的用户模式下的地址）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/6.png)[![](https://p0.ssl.qhimg.com/t01469af649af69fafe.png)](https://p0.ssl.qhimg.com/t01469af649af69fafe.png)

图5. IOCTL正在检查condrv!CdpFastIoDeviceControl函数的参数

还原输入缓冲区后，我们得到一个内容不明的数据结构。我们需要继续分析ConDrv中处理输入缓冲区的相关代码，进一步理解具体的数据格式。这部分结构的数据格式如图6所示。注意：官方并没有公开这个结构，我根据ConDrv还原了这个结构的相关字段。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/7.png)[![](https://p0.ssl.qhimg.com/t010ee36c7772731546.png)](https://p0.ssl.qhimg.com/t010ee36c7772731546.png)

图6. 根据Windows 10中的condrv.sys推断出的消息缓冲区结构

每条I/O消息中都包含命令数据对应的缓冲区以及缓冲区大小。在输出结果时，系统会使用这个结构体来传输命令执行的结果。我们可以在Windbg中将这个结构体应用于相关数据，这样就能得到控制台的命令，如图7所示。从图中，我们可以看到用户正在往命令提示符中输入dir命令。我们也可以使用同样的方法来捕捉命令输出结果。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/8.png)[![](https://p0.ssl.qhimg.com/t013e29140ea5806c2c.png)](https://p0.ssl.qhimg.com/t013e29140ea5806c2c.png)

图7. 在Windbg中显示命令数据

现在我们已经知道I/O数据的具体格式以及系统传输此类数据的方法，接下来我们可以写个过滤驱动的PoC代码，以捕捉I/O数据，并将该数据发送回用户模式中，以便后续处理。我们可以按顺序获取此类数据，因此就能重构主机上的所有控制台会话。我们需要做的就是附加（attach）到DeviceConDrv上，并从系统上的每个Conhost进程的输入缓冲区中复制数据。然后，我们可以使用一个Python脚本来获取从内核驱动中返回的I/O数据。

首先，先来确认一下我们能否完整捕捉到用户运行交互式Python会话时的相关数据。用户使用的Python会话如图8所示。底部的命令行窗口是执行Python代码的普通用户窗口。上面的窗口中显示了从ConDrv过滤驱动中提取的相关数据。我们使用表1中的IOCTL代码来识别数据流（输入数据以及输出数据）。由于数据按一定顺序发往驱动，因此我们可以监控完整的命令执行过程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/9.png)[![](https://p0.ssl.qhimg.com/t015cb2bdea72b4f323.png)](https://p0.ssl.qhimg.com/t015cb2bdea72b4f323.png)

图8. 捕捉Python控制台会话，下图为用户会话，上图为从condrv.sys中提取的对应数据

在本文开头，我们提到过mimikatz这个工具，如果攻击者直接通过交互式命令行来运行mimikatz，我们就无法通过读取进程参数来获取攻击者输入的具体命令。从图1中我们可以看到，通过PEB命令行参数我们只能获取到mimikatz进程的具体路径。利用本文介绍的方法，我们可以得到mimikatz会话所对应的控制台I/O数据，如图9所示。根据结果，我们发现攻击者已经从系统中提取了**NTLM**（NT LAN Manager）的哈希值，我们还可以知道攻击者在什么时候窃取了哪些用户的凭据。这种攻击活动时间线对应急事件响应而言可以起到非常关键的作用，如果我们使用其他方法（比如导出进程内存），就会丢失非常关键的上下文信息。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/10.png)[![](https://p1.ssl.qhimg.com/t0183ceb984fc3a07e4.png)](https://p1.ssl.qhimg.com/t0183ceb984fc3a07e4.png)

图9. 监控mimikatz控制台会话，下图为攻击者会话，上图为从condrv.sys中提取的对应数据

**<br>**

**三、总结**

现在我们可以监控、修改或者彻底拦截Windows 8及更高版本操作系统中的所有控制台输入输出数据。这种技术不仅可以监控系统工具所产生的I/O数据，只要用到控制台，任何程序都是我们的监控目标。我们的监控目标覆盖交互式解释器（如Python、Ruby以及Perl等）以及安全工具（如mimikatz、Metasploit等）。随着攻击者在系统上活动更加肆意妄为，准确识别他们的活动轨迹对我们而言已是迫在眉睫的一件事情。
