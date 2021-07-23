> 原文链接: https://www.anquanke.com//post/id/85147 


# 【技术分享】恶意文档分析：从宏指令到Shellcode


                                阅读量   
                                **97003**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：bittherapy.net
                                <br>原文地址：[https://bittherapy.net/malicious-document-analysis-macro-to-shellcode/](https://bittherapy.net/malicious-document-analysis-macro-to-shellcode/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01e0bb3d12b39e93ad.jpg)](https://p1.ssl.qhimg.com/t01e0bb3d12b39e93ad.jpg)

作者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：180RMB（不服你也来投稿啊！）

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**前言 **



最近，遇到的一个Word文档引起了我的注意，因为它一看就是一个恶意文档。它奇葩的地方在于，注释内容五花八门，从随机的变量名称到流行歌词，应有尽有。最重要的是，在从宏指令向机器码转移控制权的时候，它使用了一种非常罕见同时也非常酷的方法。

**<br>**

**分析宏指令 **



宏指令的开头部分，创建许多指向已被Word载入内存中的DLL导出函数的指针： 



```
'Run from the noise of the street and the loaded gun  
Public Declare Function whitworth Lib "kernel32.dll" Alias "VirtualAllocEx" (castroism As Long, accidence As Long, ByVal graze As Long, ByVal footstool As Long, ByVal vicariate As Long) As Long  
'Life can be so cruel  
Public Declare Sub intermission Lib "ntdll.dll" Alias "RtlMoveMemory" (septentrional As Any, ByVal ploy As Any, ByVal cinders As Long)  
'Every time you give yourself away  
Public Declare Function bruckenthalia Lib "kernel32.dll" Alias "EnumTimeFormatsW" (ByVal khartoum As Any, ByVal grinding As Any, ByVal fie As Any) As Long  
'So run my baby run my baby run  
Public Declare Function briefcase Lib "user32" Alias "SetParent" (ByVal anomalousness As Long, ByVal chewink As Long, advert As Long) As Long  
'Run my baby run my baby run  
Public Declare Function ex Lib "user32" Alias "GetUpdateRect" (drakes As Long, lubricitate As Long, pelham As Long) As Boolean  
'You can keep it pure on the inside  
Public Declare Function charioteer Lib "user32" Alias "EndPaint" (guttling As Long, cervical As Long) As Long  
'You can keep it pure on the inside  
Public Declare Function gigartinaceae Lib "user32" Alias "OpenClipboard" (enliven As Long) As Boolean  
'You can keep it pure on the inside  
Public Declare Function malnourished Lib "kernel32.dll" Alias "Sleep" (subsequent As Long)
```

这里要特别注意函数指针whitworth和bruckenthalia，因为它们允许宏指令以相应的权限分配内存（VirtualAllocEx），然后跳转到分配的内存区并执行任意代码。

VirtualAllocEx的作用是显而易见的，因为宏代码使用它返回一个指向设置为RWX（读写执行权限）的内存块的指针。

EnumTimeFormatsW更加让人感兴趣，其代码如下所示： 



```
BOOL EnumTimeFormats(  
  _In_ TIMEFMT_ENUMPROC lpTimeFmtEnumProc,
  _In_ LCID             Locale,
  _In_ DWORD            dwFlags
);
```

这个宏代码可以通过第一个参数来传递指向内存中的任意函数的指针，并在返回时执行它。根据MSDN的介绍： 

```
lpTimeFmtEnumProc [in]
```

指向应用程序定义的回调函数的指针。有关更多信息，请参阅EnumTimeFormatsProc。

通过跟踪宏代码的执行，我发现whitworth的返回值是一个表示内存位置的长整数，具体来说，是VirtualAllocEx返回的地址：

[![](https://p0.ssl.qhimg.com/t01a966e46b435faa71.png)](https://p0.ssl.qhimg.com/t01a966e46b435faa71.png)

 当然，这个地址可能会有所变化，但这里whitworth返回的是115212288，转换为地址的话就是0x06DE0000。

 在调用EnumTimeFormatsW并最终将控制权转移到shellcode之前，这个宏会给该地址加上一个偏移量0xE5D：



[![](https://p1.ssl.qhimg.com/t01fbad89001b9f185b.png)](https://p1.ssl.qhimg.com/t01fbad89001b9f185b.png)

在本例中，作为回调函数传递的最终值是115215965，也就是0x6DE0E5D。

下图中突出显示的是已经分配的具有RWX权限的内存段：

[![](https://p2.ssl.qhimg.com/t01536089678473ccbb.png)](https://p2.ssl.qhimg.com/t01536089678473ccbb.png)

这个内存块中的内容是一些看似随机的数据：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d9a3a757b9cdc823.png)

 由于该回调函数使用了一个0xE5D的偏移量，所以我认为这个位置肯定有代码，那就反汇编看看吧：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01025326e853a095c3.png)



这里的断点能够帮我们弄清楚控制权从这个宏那里传过来时会发生什么情况。

<br>

**Shellcode Harness**



为了简化调试工作，可以将这部分内存保存到磁盘，并将其添加到shellcode harness。所谓shellcode harness，就是一个任意的可执行文件，只要它有一个节能够容下这个shellcode（大约12kb）就行了： 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0127a8e5bea819372a.png)

这个可执行文件（sc.exe）有一个足以容纳shellcode的.data节。所以，我们可以安全地将shellcode写入到.data节中，然后使用OllyDumpEx插件转储所做的修改，即从内存中导出程序到文件里。

最后得到的harness可执行文件的.data节如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017feb317bd89ed0a3.png)

 通过对.data节进行反汇编，可以查看哪部分会变成这个shellcode harness可执行文件的新入口点（转移控制权时，宏指令将跳转到这个位置）：

[![](https://p3.ssl.qhimg.com/t0161e6f26f080937fb.png)](https://p3.ssl.qhimg.com/t0161e6f26f080937fb.png)

 最后一步是修改harness可执行文件的PE头部，并确保入口点偏移量设置为0x0000CE5D。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019ded6d7d870b5c6c.png)

这样的话，我们就可以用IDA来反汇编shellcode了，以便进一步考察。

<br>

**分析Shellcode** 



为了隐匿地加载所需的DLL并下载后续代码，shellcode代码需要解决许多棘手的问题。

这里最好将Access Violation异常从调试器传递给应用程序，因为它们会影响我们的逆向分析工作。

shellcode首先会检查进程内存空间中某处是否出现BULLSHIT。由于原始文档已经做好了相应的准备，所以这项检查自然会通过的。

它首先在ESI = 0x00001000处检查BULL，然后在ESI + 0x4处检查SHIT。

我们可以在内存空间中添加相应的内容，或者在每个CMP指令（EFL = 0x00000040）后设置零标志：



[![](https://p1.ssl.qhimg.com/t011e9bdda6ef66da88.png)](https://p1.ssl.qhimg.com/t011e9bdda6ef66da88.png)

此后，shellcode会加载DLL，其中包括urlmon.dll。该库中的URLDownloadToCacheFileA（）函数用于下载后续代码：

[![](https://p2.ssl.qhimg.com/t0146e2c02ca059e2ce.png)](https://p2.ssl.qhimg.com/t0146e2c02ca059e2ce.png)

 此外，它还会检查操作系统的架构：

[![](https://p3.ssl.qhimg.com/t01c8a1cf3bd0687037.png)](https://p3.ssl.qhimg.com/t01c8a1cf3bd0687037.png)

在x64系统上，它会从％windir％ SysWow64文件夹（32位）执行svchost.exe。在x86系统上，它将启动％windir％ explorer.exe。

该进程看起来是用CREATE_SUSPENDED（0x00000004）标志启动的，然后调用NtUnmapViewOfSection（）：

[![](https://p4.ssl.qhimg.com/t01f421635e32740e56.png)](https://p4.ssl.qhimg.com/t01f421635e32740e56.png)

这里貌似使用了一种称为Process Hollowing的技术。在使用这种技术的时候，会在挂起模式下启动一个普通的进程，不过该进程的代码实际上已经被攻击者的代码所替换了：

[![](https://p5.ssl.qhimg.com/t012652d8cf11dd56a6.png)](https://p5.ssl.qhimg.com/t012652d8cf11dd56a6.png)

在本例中，shellcode将被注入到“已经掏空的”svchost.exe进程中。然后，对该线程上的下文进行相应的调整，然后唤醒该线程，这样就会执行恶意代码了：

[![](https://p3.ssl.qhimg.com/t014fe27a85ac8802a1.png)](https://p3.ssl.qhimg.com/t014fe27a85ac8802a1.png)

我们可以将调试器附加到正在运行但被挂起的svchost.exe进程上面来查找所有具有RWX权限的节。

[![](https://p5.ssl.qhimg.com/t0145ade90bff5dc930.png)](https://p5.ssl.qhimg.com/t0145ade90bff5dc930.png)

如果我们在被掏空的进程的这个节上设置一个break-on-access断点，那么就可以分析这个shellcode的后续代码，并捕获更多的IOC了。一旦WINWORD.exe的shellcode执行完成，svchost.exe中的访问断点将在0x004020D0处被触发： 

[![](https://p4.ssl.qhimg.com/t0151765e5e5ce05add.png)](https://p4.ssl.qhimg.com/t0151765e5e5ce05add.png)

…然后，该进程将重新启动:)

在svchost.exe中还有许多其他有趣的东西，包括一些反调试花招和更多的C2主机。

 

**IOC**



家族（行为类似）： 

```
Hancitor / Chanitor
```

C2:



```
// from WINWORD.exe
hxxp://hoentoftfa.com/blt/path1.php?v=[1-9]`{`2`}`
 
// from svchost.exe
hxxp://hoentoftfa.com/ls5/gate.php  
hxxp://gonynamo.ru/ls5/gate.php  
hxxp://forpartinsa.ru/ls5/gate.php
```

用来获取外部IP的Callout ：

```
hxxp://api.ipify.org
```

动态解析和加载的DLL：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fe052da5c0e54dbc.png)

值得注意字符串︰ 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0194eaee65945dcd52.png)

[![](https://p0.ssl.qhimg.com/t01807df2a0aa84f1e7.png)](https://p0.ssl.qhimg.com/t01807df2a0aa84f1e7.png)

usps85902802.doc的哈希值：

```
MD5: 03FD8CFB582F4AE09C2BC4E9D2172AC0  
SHA-1: 91C36066241D1C0D4574FDB9C6AA035EA486929B  
SHA-256: 45289367EA1DDC0F33E77E2499FDE0A3577A5137037F9208ED1CDDED92EE2DC2  
SSDeep: 3072:q2RxSO8YmDd3RJticBrsOmqHQvZ2YftJ+:JxoYmIO9JYF
```


