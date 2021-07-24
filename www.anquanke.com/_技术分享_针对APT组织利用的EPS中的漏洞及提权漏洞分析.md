> 原文链接: https://www.anquanke.com//post/id/86111 


# 【技术分享】针对APT组织利用的EPS中的漏洞及提权漏洞分析


                                阅读量   
                                **113770**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2017/05/eps-processing-zero-days.html](https://www.fireeye.com/blog/threat-research/2017/05/eps-processing-zero-days.html)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p2.ssl.qhimg.com/t0134acf0b0e1f7f800.jpg)](https://p2.ssl.qhimg.com/t0134acf0b0e1f7f800.jpg)

翻译：[**shan66**](http://bobao.360.cn/member/contribute?uid=2522399780)

**稿费：200RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**前言**

**在2015年，FireEye发布了微软Office的EPS（Encapsulated PostScript）中两个漏洞的详细信息。**其中，一个是 0day漏洞，一个在攻击发生前几周打了补丁。**最近，FireEye又在微软Office产品中发现了三个新的 0day漏洞，这些漏洞正在被攻击者所利用。**

在2017年3月底，我们检测到另一个恶意文件，它利用EPS的未知漏洞和Windows图形设备接口（GDI）中最近修补的漏洞来投递恶意软件。 随后，微软公司在2017年4月停用了EPS，但是FireEye在EPS中又发现了第二个未知的漏洞。 

FireEye认为，有两个组织（Turla以及另一个未知的金融犯罪组织）正在利用第一个EPS 0day漏洞（CVE-2017-0261），而APT28则正在使用第二个EPS 0day漏洞（CVE-2017-0262）以及一个新的特权升级（EOP） 0day漏洞（CVE-2017-0263）。 Turla和APT28是俄罗斯的网络间谍组织，他们将这些 0day漏洞应用于欧洲的外交和军事部门。而这个不明身份的金融犯罪组织则专门针对在中东设有办事处的地区银行和全球银行。下面，我们开始介绍EPS 0day漏洞、相关恶意软件和新的EOP 0day漏洞。每个EPS 0day漏洞都提供了相应的EOP漏洞利用代码，为了进行提权，这些代码必须绕过沙盒，以便执行用于处理EPS的FLTLDR.EXE实例。

我们发现的恶意文件被用于投递三种不同的有效载荷。 CVE-2017-0261用于投递SHIRIME（Turla）和NETWIRE（未知的金融犯罪组织），CVE-2017-0262用于投递GAMEFISH（APT28）。 CVE-2017-0263用于在投递GAMEFISH有效载荷期间提升特权。 

FireEye公司的电子邮件和网络产品都检测到了这些恶意文件。

在这些漏洞信息的披露方面，FireEye已经与Microsoft安全响应中心（MSRC）进行了协调。 Microsoft建议所有客户遵循安全咨询ADV170005中的指导，做好相关的安全防御工作。

<br>

**CVE-2017-0261——EPS“还原”UAF漏洞**

打开Office文档时，FLTLDR.EXE将被用于渲染包含该漏洞的嵌入式EPS图像。这里的EPS文件是一个PostScript程序，可以通过“还原”操作利用UAF漏洞。 

根据PostScript的官方说明：“本地VM中的对象分配和对本地VM中的现有对象的修改由称为save和restore的功能完成，在命名相应的操作符后，就可以引用它们了。save和restore可以用来封装位于本地VM中的PostScript语言程序的相关代码。restore能够释放新建的对象，并撤消从相应的save操作后对现有对象的修改。”

如上所述，restore操作将回收从save操作后所分配的内存。对于UAF漏洞来说，当与forall操作相结合的话，那就再好不过了。 图1显示了利用save和restore操作的伪代码。

[![](https://p0.ssl.qhimg.com/t0180eed6e0196a1044.png)](https://p0.ssl.qhimg.com/t0180eed6e0196a1044.png)

图1：漏洞利用伪代码 

以下操作允许伪代码泄漏元数据，从而实现读/写原语：

1.	创建forall_proc数组，只有单个restore proc元素

2.	将EPS状态保存到eps_state

3.	在保存后创建uaf_array

4.	利用forall操作遍历uaf_array的元素，为每个元素调用forall_proc

5.	将uaf_array的第一个元素传递给restore_proc的调用，该过程包含在forall_proc中

6.	restore_proc

恢复初始状态，释放uaf_array

alloc_string过程将回收释放的uaf_array

forall_proc改为调用leak_proc

7.	forall操作的后续调用会为回收的uaf_array的每个元素调用leak_proc，这些元素现在存放alloc_string过程的结果 

图2演示了在回收后使用uaf_array的调试日志。

[![](https://p0.ssl.qhimg.com/t0132f721cae08f74f3.png)](https://p0.ssl.qhimg.com/t0132f721cae08f74f3.png)

图2：uaf_array回收调试日志

通过操作save操作符之后的操作，攻击者能够操纵内存布局，并将UAF漏洞转换为读/写原语。 图3显示了伪造的字符串，长度设置为0x7fffffff，基数为0。

[![](https://p3.ssl.qhimg.com/t01a9c3a8a784e59f63.png)](https://p3.ssl.qhimg.com/t01a9c3a8a784e59f63.png)

图3：伪造的字符串对象 

利用读写任意用户内存的能力，EPS程序可以进一步搜索gadgets来构建ROP链，并创建一个文件对象。 图4显示了内存中伪造的文件对象。

[![](https://p5.ssl.qhimg.com/t01ceef0b50556a421b.png)](https://p5.ssl.qhimg.com/t01ceef0b50556a421b.png)

图4：带有ROP的伪文件对象

通过伪造的文件对象调用closefile，漏洞利用代码可转到ROP并启动shellcode。 图5显示了closefile处理程序的部分反汇编程序。

[![](https://p4.ssl.qhimg.com/t01c326a20fef4f9fd5.png)](https://p4.ssl.qhimg.com/t01c326a20fef4f9fd5.png)

图5：closefile的Stack Pivot反汇编代码 

一旦执行完成，恶意软件就会使用ROP链来修改存放shellcode的内存区域的保护机制。这样，shellcode就能够在执行FLTLDR.EXE的沙盒中运行，同时，为了逃避该沙箱的检测，它还需要进一步提权。

根据FireEye的发现，利用此漏洞的EPS程序有两个不同版本。其中，st07383.en17.docx使用32或64位版本的CVE-2017-0001来提权，然后执行一个含有称为SHIRIME的恶意软件注入器的JavaScript有效载荷。 SHIRIME是Turla常用的特制JavaScript注入器之一，作为第一阶段的有效载荷进入目标系统，并实现了管理和控制功能。自2016年初以来，我们观察到在野外使用的SHIRIME已经多次改版，在这个 0day漏洞攻击中使用的是最新版本（v1.0.1004）

第二个文档Confirmation_letter.docx使用32或64位版本的CVE-2016-7255来提权，然后注入NETWIRE恶意软件的一个新变体。据我们观察，该文件不同版本的文件名非常类似。

这些文档中的EPS程序包含不同的逻辑来完成ROP链的构建以及shellcode的构建。同时，它还利用一个简单的算法对shellcode的部分进行了混淆处理，具体如图6所示。 

[![](https://p4.ssl.qhimg.com/t0138fe518f0f3da57f.png)](https://p4.ssl.qhimg.com/t0138fe518f0f3da57f.png)

图6：Shellcode混淆算法

<br>

**CVE-2017-0262——EPS中的类型混淆**

第二个EPS漏洞是forall操作符的类型混淆过程对象，它可以改变执行流程，允许攻击者控制操作数堆栈上的值。这个漏洞位于名为“Trump's_Attack_on_Syria_English.docx”的文档中。

在触发漏洞之前，EPS程序会使用预定义的数据喷射内存，以占用特定的内存地址，并便于进一步的攻击。 图7展示了利用字符串喷射内存的PostScript代码片段。

[![](https://p4.ssl.qhimg.com/t017c63e195e1f145b4.png)](https://p4.ssl.qhimg.com/t017c63e195e1f145b4.png)

图7：完成喷射的PostScript代码片段 

执行上述代码后，字符串的内容将占用地址为0x0d80d000的内存，形成如图8所示的内存布局。这个漏洞利用代码将利用这个内存布局和相应的内容来伪造过程对象，并操作代码流程，将预定义的值（黄色部分）存储到操作数堆栈。

[![](https://p2.ssl.qhimg.com/t01392b610cbfa0cee2.png)](https://p2.ssl.qhimg.com/t01392b610cbfa0cee2.png)

图8：喷射的数据的内存布局

在进行喷射堆后，漏洞利用代码会调用一个代码语句，具体格式：1 array 16＃D80D020 forall。这将创建一个Array对象，将这个过程设置为十六进制数0xD80D020，并调用forall操作符。 forall操作符中的伪造过程在运行期间，会精确地控制执行流程，将攻击者选择的值存储到操作数堆栈中，具体如图9所示。 

[![](https://p5.ssl.qhimg.com/t01ec6a9e66cddbcab1.png)](https://p5.ssl.qhimg.com/t01ec6a9e66cddbcab1.png)

图9  执行伪造的过程

在执行forall之后，堆栈中的内容就会完全被攻击者所控制，具体如图10所示。

[![](https://p0.ssl.qhimg.com/t012ff59eb5f128f7c4.png)](https://p0.ssl.qhimg.com/t012ff59eb5f128f7c4.png)

图10：代码执行后的堆栈

由于操作数堆栈已经被操纵，所以exch的后面的操作就会根据被操纵的堆栈中的数据来定义对象，如图11所示。

[![](https://p4.ssl.qhimg.com/t01b1b21101ad22769b.png)](https://p4.ssl.qhimg.com/t01b1b21101ad22769b.png)

图12：A18字符串对象

A19是一个数组类型的对象，其成员的值都是精心制作的。这个漏洞利用代码还定义了另一个数组对象，并将其放入伪造的数组A19中。通过执行这些操作，它将新创建的数组对象指针放入A19中。该漏洞利用代码可以直接从可预测地址0xD80D020 + 0x38中读取值，并泄漏EPSIMP32.flt的vftable和infer模块饿基址。图13显示了泄漏EPSIMP32基地址的代码片段。

[![](https://p2.ssl.qhimg.com/t0159ff7fb3c3af7404.png)](https://p2.ssl.qhimg.com/t0159ff7fb3c3af7404.png)

图13：泄漏模块基地址的代码片段

图14显示了调用put操作符的操作数堆栈和完成put操作后的伪造数组A19。

[![](https://p3.ssl.qhimg.com/t010b045d01a03e76a0.png)](https://p3.ssl.qhimg.com/t010b045d01a03e76a0.png)

图14：调用put操作后的数组A19

通过利用RW原始字符串和泄露的EPSIMP32模块基地址，该漏洞利用代码可以搜索ROP gadgets，创建伪造的文件对象，并通过bytesavailable操作符转换为shellcode。图15显示了伪造的文件类型对象，并将其转换为ROP和shellcode。

[![](https://p4.ssl.qhimg.com/t015a3a7588840512c1.png)](https://p4.ssl.qhimg.com/t015a3a7588840512c1.png)

图15：ROP和Shellcode

shellcode继续使用以前未知的EOP CVE-2017-0263升级特权，以通过运行FLTLDR.EXE的沙箱的检测，然后注入并执行GAMEFISH有效载荷。在这个shellcode中只有32位版本的CVE-2017-0263。 

<br>

**CVE-2017-0263——win32k！xxxDestroyWindow的UAF漏洞**

EOP漏洞利用代码首先会挂起当前线程以外的所有线程，并将线程句柄保存到表中，如图16所示。

[![](https://p5.ssl.qhimg.com/t0199dc51f1b58be128.png)](https://p5.ssl.qhimg.com/t0199dc51f1b58be128.png)

图16：挂起线程

然后，这个漏洞利用代码会检测操作系统版本，并使用该信息来填充与版本有关的特定字段，例如令牌偏移量，系统调用号等。然后，会分配可执行内存区域，并填入内核模式shellcode以及所需的地址信息。之后，会创建一个新的线程来触发漏洞并进一步控制该漏洞利用代码。

这个漏洞利用代码创建三个PopupMenus，并添加了相应的菜单，如图17所示。该漏洞利用代码还会创建具有随机的类名称的0x100窗口。 这里，User32！HMValidateHandle技术被用于泄漏tagWnd地址，该地址是整个漏洞利用代码中的内核信息。

[![](https://p2.ssl.qhimg.com/t018e8e802f1fdca451.png)](https://p2.ssl.qhimg.com/t018e8e802f1fdca451.png)

图17：创建Popup菜单 

然后，RegisterClassExW用于注册一个WndProc窗口类“Main_Window_Class”，该窗口类指向一个函数，该函数调用EventHookProc创建的窗口表中的DestroyWindow，这个将在后面介绍。这个函数还显示前面创建的第一个弹出菜单。

此外，还创建了另外两个窗口，其类名称为“Main_Window_Class”。 SetWindowLong用于将第二个窗口WndProc的WndProc更改为shellcode地址。应用程序定义了钩子WindowHookProc和事件钩子EventHookProc，它们分别由SetWindowsHookExW和SetWinEventHook进行安装。 PostMessage用于将0xABCD发送到第一个窗口wnd1。

EventHookProc将等待EVENT_SYSTEM_MENUPOPUPSTART并将窗口的句柄保存到表中。 WindowHookProc查找SysShadow类名，并为相应的窗口设置一个新的WndProc。在这个WndProc内，NtUserMNDragLeave系统调用将被调用，SendMessage用于发送0x9f9f到wnd2，调用如图18所示的shellcode。

[![](https://p0.ssl.qhimg.com/t01881056df2b1e6558.png)](https://p0.ssl.qhimg.com/t01881056df2b1e6558.png)

图18：触发shellcode 

该UAF漏洞出现在内核的WM_NCDESTROY事件中，并会覆盖wnd2的tagWnd结构，它将设置bServerSideWindowProc标志。有了bServerSideWindowProc设置，用户模式WndProc就会视为内核回调函数，所以会从内核上下文中进行调用——在这种情况下，wnd2的WndProc就是shellcode。

shellcode通过检查代码段是否为用户模式代码段来检查是否发生了内存损坏。它还检查发送的消息是否为0x9f9f。完成验证后，shellcode会找到当前进程的TOKEN地址和系统进程的TOKEN（pid 4）。然后，shellcode将系统进程的令牌复制到当前进程，从而将当前进程权限提升到SYSTEM级别。

<br>

**小结**

EPS处理已经成为攻击者熟门熟路的漏洞利用宝地。

FireEye已经发现两个全新的EPS 0day攻击，并进行了全面的分析。我们发现的恶意文档使用了不同的EPS漏洞利用代码、ROP构造、shellcode、EOP漏洞利用代码和最终的有效载荷。虽然这些文档会被FireEye产品检测到，但是由于EMET不会监控FLTLDR.EXE，所以用户应谨慎行事。 
