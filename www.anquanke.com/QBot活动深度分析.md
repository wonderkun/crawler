> 原文链接: https://www.anquanke.com//post/id/208427 


# QBot活动深度分析


                                阅读量   
                                **142299**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：
                                <br>原文地址：[https://www.fortinet.com/blog/threat-research/deep-analysis-of-a-qbot-campaign-part-1](https://www.fortinet.com/blog/threat-research/deep-analysis-of-a-qbot-campaign-part-1)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t018b5a2a958d8f1fdc.jpg)](https://p4.ssl.qhimg.com/t018b5a2a958d8f1fdc.jpg)



QBot,又名QakBot,是一款活跃多年的木马程序。它最初被认为是金融恶意软件，用来窃取用户凭证和击键，针对政府和企业进行金融欺诈。据威胁研究人员当时观察，它是通过网络钓鱼活动或者另一个恶意软件（如Emotet）传播的。

FortiGuard实验室最近捕获了一个MS Office Word文档，该文档正在传播的QBot的变种。通常情况下，这类Word文档只会以钓鱼邮件的形式发送，欺骗受害者打开它。不幸的是，我们只捕获了Word文件，不知道它是如何传递的。

我对这个样本文件进行了深入分析。QBot使用了复杂的技术和框架，使其能够在受害者的系统上秘密运行。在这篇文章中，我将解释它如何在受害者的机器上工作，以及它使用了哪些技术。



## 打开包含QBot的Word文档

正如所预料的那样，Word文档中包含了一个恶意的宏。一旦在Word程序中打开该文件，它就会要求受害者点击一个黄色按钮，如图1.1（左侧）所示。右边部分的图片显示了 “启用内容 “按钮被点击后的样子。它欺骗了受害者，使其以为正在加载数据。

[![](https://p4.ssl.qhimg.com/t01b3eaed6f94c0514e.png)](https://p4.ssl.qhimg.com/t01b3eaed6f94c0514e.png)

然而，实际发生的情况是，恶意的Macro（VBA代码）正在后台执行。它有一个名为Document_Open()的函数，在文件打开时自动调用。

该宏在 “C:UsersPublic”中创建了一个名为 “tmpdir “的文件夹。 然后它试图将QBot的payload下载到这个文件夹中。攻击者将QBot的payload放在五个地方。这五个地方是

`hxxp://pickap[.]io/wpcontent/uploads/2020/04/evolving/888888[.]png.`

`hxxp://decons[.]vn/wp-content/uploads/2020/04/evolving/888888[.]png.`

`hxxp://econspiracy[.]se/evolving/888888[.]png.`

`hxxp://enlightenededucation[.]com/wpcontent/uploads/2020/04/evolving/888888[.]png.`

`hxxp://kslanrung[.]com/evolving/888888[.]png.`

这些URL由5个Base64编码的字符串与PowerShell代码解码而成。在执行过程中，恶意软件会向受害者展示图1.1所示的信息（右图）。

PowerShell代码在一个循环内重复选取五个URL中的一个，将有效载荷文件888888.png（EXE文件）下载到 “C:UsersPublictmpdir”中。然后它将其重命名为 “file.exe”，最后被执行。当第一个有效载荷文件被下载后，它就会停止循环。(注意：这里使用的 ““符号可以是1、2、3、4或5。因此，在本分析中，下载的有效载荷文件将被称为 “file1.exe”）。)

[![](https://p0.ssl.qhimg.com/t0123dc8fc4e6b2f229.png)](https://p0.ssl.qhimg.com/t0123dc8fc4e6b2f229.png)

观察这5个URL，你可能会发现它们可能是用同一个网站建设者建立的，它可能存在漏洞，允许将PNG扩展名的EXE文件上传到上面。



## 执行下载的payload

“file1.exe “是下载的payload，在打包器中受到保护。当它启动时，打包器将受保护的QBot提取到内存中，然后覆盖打包器的代码。一旦完成这些，它的入口点就会被调用。

QBot提供了一些命令行参数，如”/C”、”/W”、”/I”、”/P”、”/Q “等，用于执行不同的功能。当它被PowerShell代码启动时，没有提供任何参数。它进入一个非参数分支，首先用命令行参数”/C “为自己生成一个正常的子进程。图2.1显示了它即将用该命令行参数创建一个子进程。

[![](https://p2.ssl.qhimg.com/t0130f9efb2a343cf1c.png)](https://p2.ssl.qhimg.com/t0130f9efb2a343cf1c.png)

“/C “功能是用来检查它是否在分析环境中运行。以下是它执行该检测的方式。

它执行带有关键字 “VMXh “的ASM代码，如果它在虚拟机中，它将触发一个异常。异 常处理程序可以捕获异常并返回1，否则返回0。 下面是ASM代码片段。

```
[…]
.text:00403452                 push    ebx
.text:00403453                 push    ecx
.text:00403454                 push    edx
.text:00403455                 mov     dx, 5658h
.text:00403459                 mov     ecx, 564D5868h  ;; "VMXh".
.text:0040345E                 mov     eax, ecx
.text:00403460                 mov     ecx, 14h
.text:00403465                 in      eax, dx
.text:00403466                 mov     [ebp+var_1C], eax
.text:00403469                 pop     edx
.text:0040346A                 pop     ecx
[…]
```

它通过调用API函数SetupDiEnumDeviceInfo()来枚举设备信息，检查是否运行在 虚 拟机环境中，然后检查该设备信息是否包含以下文字，这些文字是虚拟机软件的关键词，如 “VMware”、”VirtualBox”、”CwSandbox”、”Red Hat Virtualization”、”Quality “等。然后它检查该设备信息是否包含以下虚拟机软件的关键字文本，如 “VMware”、”VirtualBox”、”CwSandbox”、”Red Hat Virtualization”、”QEMU “等。

```
"VMware Pointing"、"VMware Accelerated"、"VMware SCSI"、"VMware SVGA"、"VMware Replay"、"VMware server memory"、"CWSandbox"、"Virtual HD"、"QEMU"、"Red Hat VirtIO"。"srootkit"，"VMware VMaudio"，"VMware Vista"，"VBoxVideo"，"VBoxGuest"，"vmxnet"，"vmscsi"，"VMAUDIO"，"vmdebug"，"vm3dmp"，"vmrawdsk"，"vmx_svga"，"ansfltr"，"sbtisht"
检查是否有任何分析工具在运行，如 "VMware Tools Service"、"VMware Activation Helper"、"Metasploit Metsvc Backdoor "和 "Windump"，它们的进程名分别为 "vmtoolsd.exe"、"vmacthlp.exe"、"metsvc-server.exe "和 "windump.exe"。
```

它通过判断是否加载了特殊的Dll文件来确定当前进程是否在 “Sandboxie “中运行，同时判断当前进程名是否包含 “sample”、”mlwr_smpl “或 “artifact.exe “等字符串。之所以这样做，是因为一些沙盒工具可能会把样本文件名改成它们。

除了上述方法，它还通过调用ASM指令cpuid来检查CPU信息。

对检测中出现的常量字符串进行解密。事实上，不仅是这些字符串，所有的常量字符串都是默认加密的，在引用之前都会进行解密。

在完成所有检测后，如果上述任何一个参数被触发，子进程就会退出，退出代码为1，如果没有触发，退出代码为0。



## 返回父进程

父进程可以调用API GetExitCodeProcess()来获取退出代码。当它检测到QBot在分析设备中运行时，它不会立即退出进程，而是秘密地设置一个全局变量。结果，它进入另一个代码分支，在那里做一些无关的事情，但加载核心模块，最后退出进程。当我们到达核心模块时，我将在后面解释这个问题。

如果它没有在分析设备中运行，它就会继续在”%AppData%Microsoft/“文件夹下创建一个主文件夹，用于保存QBot的进程和数据。主文件夹的名称是随机生成的。在我的设备上，它是 “Vhdktrbeex”。在不同的设备上，它可能会有所不同。它检查当前QBot进程是否来自其主文件夹。当然，这不是第一次，因为它在 “C:UsersPublictmpdir”文件夹中。

然后，它将file1.exe复制到主文件夹中，并重命名为 “mavrihvu.exe”。文件名是由受害者的用户名生成的。在下面的图2.2中，你可以看到ASM代码片段来比较这两个文件夹名称。

[![](https://p5.ssl.qhimg.com/t01a52c1d0ad7950651.png)](https://p5.ssl.qhimg.com/t01a52c1d0ad7950651.png)

在这个代码分支中，它继续从当前进程中加载一个名为 “307 “的资源。这是QBot的核心模块。对字符串 “307 “进行解密。如果它检测到正在分析设备中，根据用参数”/C “调用的子进程的退出代码，那么 “307 “字符串解密将失败，没有错误提示。它什么也不做，很快就会退出进程。可以把它作为一种反分析技术。

“307 “的内容是一个加密的PE文件。然而，它并没有真正加载核心模块 “307 “在这里执行工作。相反，它从解密后的 “307 “模块中加载另一个资源，名为 “308”。

[![](https://p5.ssl.qhimg.com/t0148887412e0eb6cd5.png)](https://p5.ssl.qhimg.com/t0148887412e0eb6cd5.png)

从 “308 “的解密数据来看，如图2.3所示，”spx97 “中的 “10=spx97 “是QBot的变种标识，3=1586971769，是unix的纪元时间，是资源 “307 “的创建时间。它们在与C2服务器通信时，用来表明其版本。根据这些信息，C2服务器确定是否需要升级。

然后，它就会创建一个名为 “mavrihvu.dat “的文件来保存加密后的配置数据。以下是其加密前的内容。

```
01AFFB60 D8 88 6C 71 57 93 A7 1D D2 B8 97 4F 1B FC C1 E3 ??lqW"§ò?-Oüá?
01AFFB70 A2 D0 F7 C0 31 31 3D 32 0D 0A 31 3D 32 32 2E 34 ￠D÷à11=2...1=22.4。
01AFFB80 31 2E 35 37 2D 31 35 2F 30 35 2F 32 30 32 30 0D 1.57-15/05/2020.
01AFFB90 0A 32 3D 31 35 38 39 36 30 37 37 31 37 0D 0A .2=1589607717。
```

它包含几个基本信息。前14H字节是休息内容的SHA1值，11=2记录了硬盘的类型，1=22.41.57-15/05/2020是QBot安装在受害者设备上的时间和日期，2=1589607717是安装时间的Unix时间。这个 “mavrihvu.dat “文件以后会经常用来加载和保存QBot的其他配置数据。

同时，它还创建了一个WMI（Windows管理工具）对象来执行”%AppData%/Microsoft/Vhdktrbeex/mavrihvu.exe “这个没有参数的过程。为此，它调用了带有WMI命名空间 “ROOT/CIMV2 “的ConnectServer()API、CoSetProxyBlanket()和带有 “Win32_Process “的GetObject()。最后，它以命令行”%AppData%/Microsoft/Vhdktrbeex/mavrihvu.exe “和ExecMethod()调用Put()来运行。

图2.4显示了ASM代码片段如何调用Put()和ExecMethod()。

[![](https://p3.ssl.qhimg.com/t012b7a387210f0c054.png)](https://p3.ssl.qhimg.com/t012b7a387210f0c054.png)

我认为使用WMI对象来运行QBot比直接调用CreateProcess来保护进程更好。我们知道，WMI对象由Windows进程 “wmiprvse.exe “处理，然后执行mavrihvu.exe进程。下面，图2.5显示了一个截图，显示进程树开始运行 “file1.exe”，”mavrihvu.exe “是由 “wmiprvse.exe”（WMI提供者主机）启动的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0148ca45e35620daf6.png)

我将在下一节博客中详细介绍 “mavrihvu.exe “是如何被 “wmiprvse.exe “启动的。

“file1.exe “就会继续在任务计划中创建一个一次性运行任务。它使用的命令是 “C:Windowssystem32/schtasks.exe /Create /RU ”NT AUTHORITYSYSTEM/“ /tn qyuoeflyq /tr ”C:Users/Public/tmpdir/file1.exe/“/I qyuoeflyq /SC ONCE /Z /ST 22:48 /ET 23:00”。创建的任务名称为 “qyuoeflyq”，执行命令 “C:UsersPublictmpdirfile1.exe /I qyuoeflyq”。”/I qyuoeflyq “是命令行参数。然后，该代码分支用 “calc.exe “替换 “file1.exe “的内容，销毁 “file.exe”，然后删除这个以”/I “传递的其名称为 “qyuoeflyq “的一次性运行任务。

图2.6所示，它调用”/I “处理代码分支中的API CreateProcessW()执行命令，替换 “file1.exe “的内容。

[![](https://p4.ssl.qhimg.com/t01e16aabb06ab84bfb.png)](https://p4.ssl.qhimg.com/t01e16aabb06ab84bfb.png)

此时，”file1.exe “的任务已经完成。然后它调用API ExitProcess()来退出进程。



## WMI提供者主机执行QBot

在图2.5中，你可以看到QBot（”mavrihvu.exe”）是由WMI提供者主机（”wmiprvse.exe”）启动的，没有任何参数。它执行 “file1.exe “所做的所有工作，比如检查它是否在分析设备中（参数”/C”），这一点我在前面已经解释过了，然后检查它是否来自它的主文件夹”%AppData%/microsoft/Vhdktrbeex/“。这次的结果显然是 “是”，因此，它将转到与 “file1.exe “不同的分支。

接下来，它会从一些常见的进程中创建一个暂停的进程，包括 “C:Windowsexplorer.exe”、”C:WindowsSystem32mobsync.exe “和 “C:Program FilesInternet Exploreriexplore.exe”。使用哪一个取决于哪一个先工作。然后，QBot会转移到选定的普通进程上执行其恶意代码，以保护它不被受害者识别。 这三个普通进程的字符串默认是加密的。

[![](https://p1.ssl.qhimg.com/t01fef2f02d41e1e47c.png)](https://p1.ssl.qhimg.com/t01fef2f02d41e1e47c.png)

图3.1是它创建 “explorer.exe “时的截图，标志是CREATE_SUSPENDED。这样，QBot就可以修改 “explorer.exe “的内存数据，然后恢复其运行。

QBot将其内存中的全部数据复制到explorer.exe的内存中。为此，它调用API ZwCreateSection()、ZwMapViewOfSection()和memcpy()来复制数据。然后，它从PE结构中读取重定位数据，并在 “explorer.exe “中调整复制的代码中的重定位偏移。最后，它调用API GetThreadContext()来获取 “explorer.exe “的当前入口点，然后修改它，使其能够跳转到复制的QBot的代码（入口点）。然后它调用ResumeThread()来恢复 “explorer.exe “从它的入口点运行。现在，”mavrihvu.exe “的所有工作都已完成，它调用API ExitProcess()，因为退出是它要做的最后一件事。现在，QBot在explorer.exe进程中完美运行。



## QBot在explorer.exe进程中执行

“explorer.exe “中运行的代码有一个新的入口点，首先被调用。它的主要任务是加载和解密资源 “307”。它调用API FindResourceA()、SizeofResource()和LoadResource()将资源 “307 “载入内存。接下来，它通过调用RC4函数得到解密后的 “307 “数据。 下图4.1是刚刚解密后的 “307 “数据，这是一个PE文件。

[![](https://p0.ssl.qhimg.com/t0168ecf0c875eee110.png)](https://p0.ssl.qhimg.com/t0168ecf0c875eee110.png)

我转储并分析了PE文件。这是一个Dll文件，它将是QBot的核心模块。它包含三个资源，”308”、”310”、”311”，这三个资源是核心模块所使用的；”308 “的内容我之前已经解释过了。对于其他的资源，我在解密后会带大家了解它们的内容。图4.2是PE分析工具中转储资源 “307 “的三个资源。

[![](https://p3.ssl.qhimg.com/t01473a46a12e6ab59b.png)](https://p3.ssl.qhimg.com/t01473a46a12e6ab59b.png)

它通过调用API VirtualAllocate()继续将 “307 “PE结构中的每个部分加载到新分配的内存中。然后它去修复重定位数据，并导入必要的API，使核心模块准备好在 “explorer.exe “中执行，这与PE Loader创建进程时的方法相同。

当以上步骤完成后，核心模块的Entry Point被调用。图4.3显示了一段调用Entry Point的ASM代码，它保存在var_10中。

[![](https://p5.ssl.qhimg.com/t01ca2a27c94ea25557.png)](https://p5.ssl.qhimg.com/t01ca2a27c94ea25557.png)

在接下来的分析中，我将继续分析核心模块在explorer.exe中的作用。例如，我将看看QBot是如何连接到它的C2服务器的，以及它从受害者的设备中窃取了哪些数据并发送给它的C2服务器。 敬请期待。



## 结束语

在本报告的第一部分，我详细解释了这个变种的QBot是如何通过使用恶意的Macro来下载Office Word文档的，以及它是如何使用复杂的技术来隐藏和保护自己不被受害者识别的。

在我分析的过程中，QBot不断升级它的payload文件，几乎每天升级一次。我会继续跟踪它的行动，当它增加了一些新的功能后，我会为它发布更多的分析。



## IOCs

### <a class="reference-link" name="%E9%93%BE%E6%8E%A5"></a>链接

hxxp://pickap[.]io/wp-content/uploads/2020/04/evolving/888888.png<br>
hxxp://decons[.]vn/wp-content/uploads/2020/04/evolving/888888.png<br>
hxxp://econspiracy[.]se/evolving/888888.png<br>
hxxp://enlightened-education[.]com/wp-content/uploads/2020/04/evolving/888888.png<br>
hxxp://kslanrung[.]com/evolving/888888.png

### <a class="reference-link" name="Sample%20SHA-256"></a>Sample SHA-256

[Original Word Document]<br>
432B6D767539FD5065593B160128AA7DCE271799AD2088A82A16542E37AD92B0

[file1.exe or 888888.png]<br>
D3B38681DBC87049022A3F33C9888D53713E144A277A7B825CF8D9628B9CA898

### <a class="reference-link" name="%E5%8F%82%E8%80%83:"></a>参考:

[https://malware.wikia.org/wiki/Qakbot](https://malware.wikia.org/wiki/Qakbot)

[https://docs.microsoft.com/en-us/powershell/scripting/samples/getting-wmi-objects–get-ciminstance-?view=powershell-7](https://docs.microsoft.com/en-us/powershell/scripting/samples/getting-wmi-objects--get-ciminstance-?view=powershell-7)
