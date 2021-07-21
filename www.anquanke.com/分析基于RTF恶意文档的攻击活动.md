> 原文链接: https://www.anquanke.com//post/id/162105 


# 分析基于RTF恶意文档的攻击活动


                                阅读量   
                                **136378**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：talosintelligence.com
                                <br>原文地址：[https://blog.talosintelligence.com/2018/10/old-dog-new-tricks-analysing-new-rtf_15.html](https://blog.talosintelligence.com/2018/10/old-dog-new-tricks-analysing-new-rtf_15.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01371bcfc78f5e8b3a.jpg)](https://p5.ssl.qhimg.com/t01371bcfc78f5e8b3a.jpg)

## 一、前言

思科Talos团队最近发现了一款新的恶意软件，该软件会释放名为“Agent Tesla”的信息窃取木马以及另一款恶意软件Loki（这也是款信息窃取木马）。最开始时Talos的感知系统检测到了一个高度可疑的文档，常见的反病毒解决方案并不会去采集该文档。然而，思科的恶意软件分析及威胁情报一体平台[Threat Grid](https://www.cisco.com/c/en/us/products/security/threat-grid/index.html)成功将这个未知文件识别为恶意软件。该恶意软件的幕后黑手使用了著名的漏洞利用链，但针对性进行了修改，成功规避了反病毒解决方案。在本文中，我们将介绍攻击者做了哪些修改以规避检测软件，也会分析使用复杂软件跟踪这类攻击的重要性。如果攻击行为不被发现，Agent Tesla就可以从许多重要软件（如Google Chrome、Mozilla Firefox、Microsoft Outlook以及其他软件）中窃取用户的登录信息，也能让攻击者在被感染的系统上安装其他恶意软件。



## 二、技术细节

在大多数情况下，此次攻击活动的第一阶段与FormBook恶意软件攻击活动类似，大家可以参考我们今年早些时候对后者的一篇分析[文章](https://blog.talosintelligence.com/2018/06/my-little-formbook.html)。先前FormBook背后的攻击者使用了CVE-2017-0199（多个版本的Microsoft Office中存在的远程代码执行漏洞）来下载某个恶意DOCX文件，并打开文件内的RTF文档。我们已经观察到此次攻击组织使用了CVE-2017-11882来传播Agent Tesla以及Loki，其中某个恶意软件的传播URL地址如下图所示。除了Agent Tesla以及Loki之外，攻击者还使用这个基础设施来传播其他恶意软件家族，如Gamarue，该恶意软件能够完全控制用户主机，也具备与典型的信息窃取后门相同的功能。

我们对FormBook的分析文章中包含该阶段的更多细节。许多用户潜意识中都会认为现在Microsoft Word文档的危险性要比RTF或者DOC文档小。虽然这个观点有一定道理，但攻击者仍然可以找到新的方法，通过新的这些文档格式来利用各种漏洞。

[![](https://p1.ssl.qhimg.com/t01f34dbe67522541b5.jpg)](https://p1.ssl.qhimg.com/t01f34dbe67522541b5.jpg)

图1. 第一阶段利用载荷

对于Agent Tesla这款恶意软件，攻击者下载的文件为RTF文件，其SHA256哈希值为`cf193637626e85b34a7ccaed9e4459b75605af46cedc95325583b879990e0e61`。在分析过程中，VirusTotal多引擎反病毒扫描网站上对该样本的检测结果不容乐观，58个反病毒程序中只有两个能够发现可疑内容。而判断该样本可疑的反病毒程序只是警告用户该样本为格式错误的RTF文件。具体而言，AhnLab-V3将该样本标记为`RTF/Malform-A.Gen`，而Zoner将其标记为`RTFBadVersion`。

然而，思科的Threat Grid给出了不一样的结论，将其标记为恶意软件。

[![](https://p3.ssl.qhimg.com/t01e72b73be47b51cf8.jpg)](https://p3.ssl.qhimg.com/t01e72b73be47b51cf8.jpg)

图2. ThreatGrid的行为指标（BI）

我们通过行为指标（BI）来给恶意行为打分，部分结果如图2所示。根据样本的进程树信息，可以发现该样本执行链的可疑程度非常高，部分结果如下图所示。

[![](https://p2.ssl.qhimg.com/t0117ffaf225bf2b5b4.jpg)](https://p2.ssl.qhimg.com/t0117ffaf225bf2b5b4.jpg)

图3. ThreatGrid进程树信息

在图3中，我们可以看到`Winword.exe`进程启动，随后某个`svchost`进程执行微软公式编辑器（`EQNEDT32.exe`），后者启动了一个`scvhost.exe`。公式编辑器是Microsoft Office的一个辅助工具，可以用来将数学公式嵌入到文档中。在Word中，我们可以使用OLE或者COM函数来启动公式编辑器，这就是我们在上图中看到的进程。公式编辑器应用启动其他可执行文件（如图3中的其他程序）是非常罕见的情况，何况被启动的程序文件名本身就非常可疑（`scvhost.exe`）。注意该文件名，用户可能将其与`svchost.exe`混淆起来。

根据Threat Grid的进程时间线信息，我们可以确认该文件的行为与典型的恶意软件行为一致。

[![](https://p1.ssl.qhimg.com/t016326c263e5a9d789.jpg)](https://p1.ssl.qhimg.com/t016326c263e5a9d789.jpg)

图4. ThreatGrid进程时间线信息

在图4中，我们可以看到公式编辑器首先下载了一个`xyz[1].123`文件，然后创建`scvhost.exe`进程（上图红框1和2），后者会在稍后创建自身的另一个实例`svchost.exe(26)`（蓝框处）。此时，我们已经确认这是一款恶意软件，现在的问题是，为什么反病毒系统无法检测该样本？攻击者通过什么方法能够隐蔽恶意特征？

### <a class="reference-link" name="%E6%81%B6%E6%84%8FRTF%E6%96%87%E4%BB%B6"></a>恶意RTF文件

[RTF标准](https://en.wikipedia.org/wiki/Rich_Text_Format)是微软开发的专有文档文件格式，用于跨平台文档交换。举个例子，一个简单的RTF文件如图5所示，由文本以及控制字（control word，字符串）所组成。下图上半部分为源代码，下半部分为文件在Microsoft Word中的呈现效果。

[![](https://p4.ssl.qhimg.com/t011e9a100b1b707c70.jpg)](https://p4.ssl.qhimg.com/t011e9a100b1b707c70.jpg)

图5. 简单的RTF文档

RTF文件并不支持任何宏语言，但可以通过`\object`控制字支持Microsoft Object Linking and Embedding（OLE）对象以及Macintosh Edition Manager订阅者对象。举个例子，用户可以将由微软公式编辑器创建的数学公式嵌入到RTF文档中，该公式将会以十六进制数据流的形式存储在对象的数据中。如果用户使用Word打开该RTF文件，Word就会通过OLE函数将对象数据交给公式编辑器应用去处理，然后返回Word能够正确显示的数据结果。换句话说，即便Word无法通过外部应用来处理该文档，也会将公式以文档嵌入公式的形式呈现给用户。以上基本上就是`3027748749.rtf`的大致原理，这里唯一的区别在于，该文档增加了许多混淆，如图6所示。RTF标准的主要缺点在于使用了非常多的控制字，而常规的RTF解析器会忽视掉它们无法识别的内容。因此，攻击者有各种选项来混淆RTF文件的内容。

[![](https://p5.ssl.qhimg.com/t017b485d28e632a202.jpg)](https://p5.ssl.qhimg.com/t017b485d28e632a202.jpg)

图6. 3027748749.rtf

虽然RTF文件经过大量混淆，我们还是使用`rtfdump`以及`rtfobj`工具成功验证了文档结构，提取出实际的对象数据载荷。该文件尝试启动Microsoft公式编辑器（类名：`EQuATioN.3`），如图8所示。

[![](https://p2.ssl.qhimg.com/t01701b3063bef58a1d.jpg)](https://p2.ssl.qhimg.com/t01701b3063bef58a1d.jpg)

图7. rtfdump

[![](https://p0.ssl.qhimg.com/t0199712f3fe39f9168.jpg)](https://p0.ssl.qhimg.com/t0199712f3fe39f9168.jpg)

图8. rtfobj

在图6中，我们可以看到攻击者使用了`\objupdate`技巧，这可以[强制](http://latex2rtf.sourceforge.net/rtfspec_7.html)嵌入对象在显示前就进行更新。换句话说，用户不需要点击该对象就能完成对象加载，这对“普通”对象来说问题不大，但通过强制打开文件的方式，恶意软件就可以开启攻击过程。

我们来看一下上图中的`objdata`数据，将其转化为十六进制表示的数据流。如果想了解更多头部标志含义，可以参考[官方链接](https://msdn.microsoft.com/en-us/library/dd942076.aspx)。

[![](https://p4.ssl.qhimg.com/t01de40ba969a97cc31.jpg)](https://p4.ssl.qhimg.com/t01de40ba969a97cc31.jpg)

图9. 头部数据

我们可以找到与之前FormBook分析文章中类似的[MTEF头部数据](http://rtf2latex2e.sourceforge.net/MTEF3.html)，为了避免检测，攻击者修改了头部中的值。唯一的区别在于，除了MTEF版本号字段以外，攻击者往其他头部字段中填充了随机值。MTEF版本号字段的值需设置为2或者3，才能让漏洞利用成功。

[![](https://p3.ssl.qhimg.com/t012c90f1eb63bde506.jpg)](https://p3.ssl.qhimg.com/t012c90f1eb63bde506.jpg)

图10. MTEF V2头部

紧跟在MTEF头部后的是1个2字节的未知MTEF字节流标记（`F1 01`）以及字体标记（`08 E0 7B ...`）。字体标记后的数据（`B9 C3 ...`）看起来并不是正常的字体名称，所以这是一个非常明显的特征，表明我们面临的是一个漏洞利用样本。这段数据的确与我们之前研究的样本非常不同，但我们可以先解码出其中内容。

[![](https://p1.ssl.qhimg.com/t01810b03ecf43cf34c.jpg)](https://p1.ssl.qhimg.com/t01810b03ecf43cf34c.jpg)

图11. Shellcode表明这是一次新的攻击活动

解码后的数据与我们之前看到的非常类似，之前我们碰到的shellcode如图12所示：

[![](https://p1.ssl.qhimg.com/t0106b2c4ad3615ed69.jpg)](https://p1.ssl.qhimg.com/t0106b2c4ad3615ed69.jpg)

图12. 之前攻击活动中使用的Shellcode

攻击者修改了寄存器以及其他一些小地方。此时我们已经非常确认攻击者使用了CVE-2017-11882漏洞，但还是让我们进一步确认这一点。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8PyREBox%E5%BC%95%E6%93%8E%E5%88%86%E6%9E%90"></a>利用PyREBox引擎分析

为了验证恶意RTF文件利用的是CVE-2017-11882，我们使用了Talos开发的动态分析引擎PyREBox。这个工具可以帮助我们检测整个系统的执行情况，监控各种不同的事件，比如指令执行、内存读写、操作系统事件，也能提供交互式分析功能，让我们随时检查模拟系统的状态。如果大家想了解该工具的更多细节，可以参考我们在Hack in the Box 2018会议上[展示](https://github.com/Cisco-Talos/pyrebox/tree/master/docs/pyrebox_hitb_ams.pdf)的[恶意软件监控脚本](https://github.com/Cisco-Talos/pyrebox/tree/master/mw_monitor)。

在本文分析中，我们使用了shadow stack插件，该插件于今年早些时候在[EuskalHack](https://securitycongress.euskalhack.org/) Security Congress III上与其他漏洞利用分析脚本（shellcode检测和stack pivot检测）一同发布（[演示文稿](https://github.com/Cisco-Talos/pyrebox/tree/master/docs/pyrebox_euskalhack.pdf)）。这个脚本可以监控指定进程（这里为公式编辑器进程）上下文中执行的所有调用以及RET指令，同时维护一个shadow stack，用来跟踪所有有效的返回地址（已执行的调用指令后的地址）。

我们要做的唯一一件事就是配置插件来监控公式编辑器进程（插件会等待该进程执行），然后在模拟的环境中打开RTF文档即可。只要RET指令跳转到早于call指令的某个地址，PyREBox会停止系统执行。栈溢出漏洞利用会覆盖存在栈上的返回地址，这种方法可以让我们检测这类漏洞利用过程。一旦执行停止，PyREBox会生成一个交互式IPython shell，让我们检查系统，调试或者跟踪公式编辑器进程的执行状态。

[![](https://p2.ssl.qhimg.com/t0186bcb3c1dac36261.jpg)](https://p2.ssl.qhimg.com/t0186bcb3c1dac36261.jpg)

图13. 检测跳转到无效地址0x44fd22时PyREBox停止执行

PyREBox会在`0x00411874`返回地址处停止执行，该地址属于CVE-2017-11882中提到的存在漏洞的函数。在这个案例中，恶意软件攻击者决定利用这个漏洞来覆盖返回地址，目标地址为公式编辑器主执行模块中包含的一个地址：`0x0044fd22`。如果我们检查这个地址（参考图13），可以发现它指向的是另一个RET指令，该指令将从栈中pop出另一个地址，然后跳转到该地址。shadow stack插件可以再次检测到这种情况，在下一次漏洞利用时停止执行流程。

[![](https://p1.ssl.qhimg.com/t01d0dafbbd46aaa636.jpg)](https://p1.ssl.qhimg.com/t01d0dafbbd46aaa636.jpg)

图14. 第一阶段shellcode

第一阶段的shellcode如图14所示，这段代码会在第二个RET指令后执行。这段shellcode会调用`GlobalLock`函数（`0x18f36e`），然后跳转到包含第二阶段shellcode的第二个缓冲区。

[![](https://p3.ssl.qhimg.com/t015c4f233e0c364a5c.jpg)](https://p3.ssl.qhimg.com/t015c4f233e0c364a5c.jpg)

图15. 开始执行第二阶段shellcode

第二阶段shellcode由一系列`jmp`/`call`指令集合以及一个解密循环所组成。

[![](https://p3.ssl.qhimg.com/t01f7e521c59f33fed6.jpg)](https://p3.ssl.qhimg.com/t01f7e521c59f33fed6.jpg)

图16. 第二阶段shellcode的解密循环

解密循环会解开shellcode的最终载荷，最后跳转到解码后的缓冲区。我们可以使用PyREBox在执行过程中导出包含shellcode的内存缓冲区。有多种方法可以完成这个任务，其中一种选择就是使用volatility框架（可以通过PyREBox shell来使用该工具）来列出进程中的VAD区域，导出可能包含目标代码的缓冲区。导出的缓冲区可以导入IDA Pro以便进一步深入分析。

[![](https://p4.ssl.qhimg.com/t01459f147225615499.jpg)](https://p4.ssl.qhimg.com/t01459f147225615499.jpg)

图17. 第二阶段载荷（最后一阶段shellcode）解密后的缓冲区

最后阶段shellcode的功能非常简单。载荷利用标准技术在PEB中可用的已加载模块链表中查找`kernel32.dll`模块，然后解析其导出表以便定位`LoadLibrary`以及`GetProcAddress`函数。利用这些函数，脚本可以解析出其他几个API函数（`ExpandEnvironmentStrings`、`URLDownloadToFileA`以及`ShellExecute`），从指定的URL处下载并执行`xyz.123`二进制文件（我们从Threat Grid的分析结果中看到过这个文件）。shellcode以`scvhost.exe`来运行这个可执行文件，在前面的Threat Grid报告中我们也能看到这个文件名。

我们也发现有多个攻击活动使用了完全相同的感染链，但会将Loki作为最终载荷，具体信息可参考下文IoC部分。

### <a class="reference-link" name="%E8%BD%BD%E8%8D%B7%E5%88%86%E6%9E%90"></a>载荷分析

接下来我们分析一下最终载荷文件`xyz.123`（`a8ac66acd22d1e194a05c09a3dc3d98a78ebcc2914312cdd647bc209498564d8`），对应的进程名为`scvhost.exe`。

```
$ file xyz123.exe

xyz123.exe: PE32 executable (GUI) Intel 80386 Mono/.Net assembly, for MS Windows
```

将该文件载入[dnSpy](https://github.com/0xd4d/dnSpy)（.NET assemly编辑器、反编译器以及调试器工具），我们可以进一步确认这是经过大量混淆的一个.NET可执行文件。

[![](https://p4.ssl.qhimg.com/t0142bd5f3ee5bb0bcd.jpg)](https://p4.ssl.qhimg.com/t0142bd5f3ee5bb0bcd.jpg)

图18. xyz123.exe

类构造函数（cctor）首先会执行如下方法，将一个大型数组加载到内存中并加以解码。

```
&lt;Module&gt;.ҭъЩӂӬҀУ\u0486\u0489їҒреӱҤЫѝйҹП()
```

cctor还会从该数组中重构`xs.dll`以及其他代码，然后使用其他例程处理入口点。构造函数在最后会调用`P.M()`方法跳转到`xs.dll`中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014ecc8b439cda8a40.jpg)

图19. P.M()方法

这个文件非常有趣，因为我们可以根据其中特征判断这个assembly使用`Agile.Net`混淆器进行混淆。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015c46eba13c6f79ac.jpg)

图20. Agile.Net混淆器特征

由于这里不涉及自定义混淆方法，我们可以执行文件，稍等片刻，然后通过[Megadumper](https://github.com/CodeCracker-Tools/MegaDumper)工具直接从内存中导出.NET可执行文件。导出后的结果看起来就比较清晰。

[![](https://p2.ssl.qhimg.com/t01e2c3a31d6e655b5a.jpg)](https://p2.ssl.qhimg.com/t01e2c3a31d6e655b5a.jpg)

图21. 去混淆后的代码（步骤1）

不幸的是，混淆器使用`H.G()`方法加密了所有字符串，我们无法直接获取这些字符串的内容。

[![](https://p2.ssl.qhimg.com/t01e7bcdbf42982d62b.jpg)](https://p2.ssl.qhimg.com/t01e7bcdbf42982d62b.jpg)

图22. H.G()方法

幸运的是，`de4dot` .NET去混淆工具只需要一条命令就能轻松解决这个问题。这里需输入样本在运行时使用哪个方法来解密字符串，具体方法是输入解密方法对应的令牌（本例中为`0x06000001`）。由于`De4dot`在自动检测Agile .NET混淆器方面有点问题，因此我们需要使用`-p`参数手动传入该信息。

[![](https://p5.ssl.qhimg.com/t019b45f0d40dbc4950.jpg)](https://p5.ssl.qhimg.com/t019b45f0d40dbc4950.jpg)

图23. de4dot .NET去混淆器

即便输出结果貌似表明操作失败，但实际上工具成功替换并恢复了所有的混淆字符串，如下图所示：

[![](https://p4.ssl.qhimg.com/t0162750e5613e2298a.jpg)](https://p4.ssl.qhimg.com/t0162750e5613e2298a.jpg)

图24. 解码后的字符串

检查源码后，我们可以看到攻击者使用的是具备信息窃取/RAT功能的一款灰色软件产品：[Agent Tesla](https://www.agenttesla.com/)。Agent Tesla包含许多可疑的功能，比如密码窃取、屏幕捕捉以及下载其他恶意软件。然而，该产品的销售方表示这款工具适用于密码恢复和儿童监视场景。

[![](https://p1.ssl.qhimg.com/t014fd3d248094e9f0d.jpg)](https://p1.ssl.qhimg.com/t014fd3d248094e9f0d.jpg)

图25. 密码窃取方法摘抄

恶意软件哈包含密码窃取功能，支持超过25款常见应用，也包含其他rootkit功能，比如键盘记录、剪贴板窃取、屏幕截图、网络摄像头访问等。恶意软件可以窃取许多应用中的密码，部分应用列表如下所示：

```
Chrome
Firefox
Internet Explorer
Yandex
Opera
Outlook
Thunderbird
IncrediMail
Eudora
FileZilla
WinSCP
FTP Navigator
Paltalk
Internet Download Manager
JDownloader
Apple keychain
SeaMonkey
Comodo Dragon
Flock
DynDNS
```

该版本恶意软件还支持使用SMTP、FTP以及HTTP协议发送窃取的数据，但仅限于HTTP POST方法，如图26所示。恶意软件在配置数据的一个变量中硬编码了待使用的协议，几乎所有的方法中都会检查这个变量，如下所示：

```
if (Operators.CompareString(_P.Exfil, "webpanel", false) == 0)
...
else if (Operators.CompareString(_P.Exfil, "smtp", false) == 0)
...
else if (Operators.CompareString(_P.Exfil, "ftp", false) == 0)
```

[![](https://p5.ssl.qhimg.com/t013ba3918ea94890ec.jpg)](https://p5.ssl.qhimg.com/t013ba3918ea94890ec.jpg)

图26. HTTP数据发送例程

比如，恶意软件会创建POST请求字符串，如图27所示。

[![](https://p2.ssl.qhimg.com/t0167f5edb766e8b392.jpg)](https://p2.ssl.qhimg.com/t0167f5edb766e8b392.jpg)

图27. POST请求

然后，恶意软件会在发送数据前使用3DES算法加密数据（如图28所示）。图25中的`_P.Y`（`0295A...1618C`）方法可以算出该字符串的MD5哈希值，该哈希值用作3DES加密算法的密钥。

[![](https://p0.ssl.qhimg.com/t017ce70e747f762785.jpg)](https://p0.ssl.qhimg.com/t017ce70e747f762785.jpg)

图28. 3DES加密算法



## 三、总结

这是一个非常高效的恶意软件攻击活动，可以规避大多数反病毒应用程序。因此，我们需要使用类似Threat Grid之类的工具来防御这些安全威胁。

这款恶意软件的幕后攻击者选择了RTF标准，然后使用经过修改的Microsoft Office漏洞利用方法来下载Agent Tesla以及其他恶意软件。我们尚未澄清攻击者是手动修改了漏洞利用方式还是使用工具自动生成shellcode，无论是哪一种情况，都表明攻击者或者他们所使用的工具具备汇编代码修改能力，使得生成的opcode字节看起来完全不同，但仍然可以成功利用漏洞，未来这种技术还可以用来隐蔽部署其他恶意软件。



## 四、IoC

恶意文档

```
cf193637626e85b34a7ccaed9e4459b75605af46cedc95325583b879990e0e61 - 3027748749.rtf
A8ac66acd22d1e194a05c09a3dc3d98a78ebcc2914312cdd647bc209498564d8 - xyz.123
38fa057674b5577e33cee537a0add3e4e26f83bc0806ace1d1021d5d110c8bb2 - Proforma_Invoice_AMC18.docx
4fa7299ba750e4db0a18001679b4a23abb210d4d8e6faf05ce2cbe2586aff23f - Proforma_Invoice_AMC19.docx
1dd34c9e89e5ce7a3740eedf05e74ef9aad1cd6ce7206365f5de78a150aa9398 - HSBC8117695310_doc
```

恶意域名

```
avast[.]dongguanmolds[.]com
avast[.]aandagroupbd[.]website
```

与`hxxp://avast[.]dongguanmolds[.]com`地址有关的Loki样本

```
a8ac66acd22d1e194a05c09a3dc3d98a78ebcc2914312cdd647bc209498564d8 - xyz.123 
5efab642326ea8f738fe1ea3ae129921ecb302ecce81237c44bf7266bc178bff - xyz.123
55607c427c329612e4a3407fca35483b949fc3647f60d083389996d533a77bc7 - xyz.123
992e8aca9966c1d42ff66ecabacde5299566e74ecb9d146c746acc39454af9ae - xyz.123
1dd34c9e89e5ce7a3740eedf05e74ef9aad1cd6ce7206365f5de78a150aa9398 - HSBC8117695310.doc
d9f1d308addfdebaa7183ca180019075c04cd51a96b1693a4ebf6ce98aadf678 - plugin.wbk
```

与Loki有关的URL

```
hxxp://46[.]166[.]133[.]164/0x22/fre.php
hxxp://alphastand[.]top/alien/fre.php
hxxp://alphastand[.]trade/alien/fre.php
hxxp://alphastand[.]win/alien/fre.php
hxxp://kbfvzoboss[.]bid/alien/fre.php
hxxp://logs[.]biznetviigator[.]com/0x22/fre.php
```

其他关联样本

```
1dd34c9e89e5ce7a3740eedf05e74ef9aad1cd6ce7206365f5de78a150aa9398
7c9f8316e52edf16dde86083ee978a929f4c94e3e055eeaef0ad4edc03f4a625
8b779294705a84a34938de7b8041f42b92c2d9bcc6134e5efed567295f57baf9
996c88f99575ab5d784ad3b9fa3fcc75c7450ea4f9de582ce9c7b3d147f7c6d5
dcab4a46f6e62cfaad2b8e7b9d1d8964caaadeca15790c6e19b9a18bc3996e18
```
