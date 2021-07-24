> 原文链接: https://www.anquanke.com//post/id/85010 


# 【技术分享】滥用协议载入本地文件，绕过HTML5沙盒


                                阅读量   
                                **103063**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：brokenbrowser
                                <br>原文地址：[https://www.brokenbrowser.com/abusing-of-protocols/](https://www.brokenbrowser.com/abusing-of-protocols/)

译文仅供参考，具体内容表达以及含义原文为准



**翻译：**[**Ox9A82**](http://bobao.360.cn/member/contribute?uid=2676915949)

**预估稿费：250RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



10月25日，@MSEdgeDev研究员在twitter上发出了一个链接，它引起了我的注意。因为当我用Chrome浏览器点击这个链接时Windows应用商店被打开了。这可能不会让你感到惊讶，但它确实是让我吃了一惊！

因为据我所知，Chrome具有这样一个良好的特性：在打开外部程序之前会首先询问用户。但是点击这个链接之后却并没有询问用户就直接打开了。

这一点是与众不同的，它引起了我的注意，因为我从来没有允许过在Chrome中打开Windows应用商店。的确是有一些扩展和协议可以自动打开，但是我却从来没有批准过Windows应用商店自动打开。

[![](https://p2.ssl.qhimg.com/t01d1a9dc1577292ea5.png)](https://p2.ssl.qhimg.com/t01d1a9dc1577292ea5.png)

这个Twitter短链接首先会重定向到

[https://aka.ms/extensions-storecollection](https://aka.ms/extensions-storecollection)

然后它又重定向到另一个有趣的链接：

ms-windows-store://collection/?CollectionId=edgeExtensions

这是一个我不知道的协议，所以我立即尝试在注册表中搜索它，因为大多数协议的关联信息都储存在注册表中。 搜索“ms-windows-store”立即返回了PackageId中的字符串结果，这似乎是Windows应用商店程序。 

[![](https://p1.ssl.qhimg.com/t016e390b6c83a87d45.png)](https://p1.ssl.qhimg.com/t016e390b6c83a87d45.png)

请注意我们是处在一个名为“Windows.Protocol”的注册表键中，我上下滚动了一下，看看是否存在其他应用程序。结果发现，许多的程序（包括MS Edge）都注册有自己的协议。这是一个好消息，因为它直接从浏览器开辟了一个全新的攻击面。但先让我们按F3看看是否可以找到其他的搜索匹配。 

[![](https://p1.ssl.qhimg.com/t01a992077b1a55a590.png)](https://p1.ssl.qhimg.com/t01a992077b1a55a590.png)

(从上图可以看出)ms-windows-store：协议似乎可以接受搜索参数，所以我们可以尝试直接从Google Chrome浏览器来打开我们的自定义搜索。并且在事实上，Windows应用商店似乎是使用Edge引擎来渲染HTML的，这就很有趣了，因为我们可以尝试对它进行XSS或者如果是本地的应用可以尝试发送大量的数据，看看会发生什么事情。 

[![](https://p1.ssl.qhimg.com/t014ff25ea490d972d7.png)](https://p1.ssl.qhimg.com/t014ff25ea490d972d7.png)

但我们暂时不去尝试这些，让我们先回到注册表编辑器中，继续按F3看看还能找到什么。 

[![](https://p3.ssl.qhimg.com/t01b8a66d960624a481.png)](https://p3.ssl.qhimg.com/t01b8a66d960624a481.png)

这个东西也很有趣，因为它给了我们如何快速的找到更多协议的线索，如果他们都是用字符串“URL：”作为开头的。让我们来重新搜索一下“URL：”，看看我们能找到什么。按[Home]键可以使我们返回到注册表顶部（译注：因为注册表编辑器默认从当前打开的路径开始搜索，所以作者要先回到根目录去），搜索“URL：”立即就返回了第一个匹配：“URL：about：blank”，这证实了我们的猜测。

再按一次F3，我们找到了bingnews（译注：必应新闻的App？？？）的协议，但这次Chrome需要经过我们同意才能打开它。没关系，让我们在Edge上试试看会发生什么。它成功的打开了！下一个匹配的注册表项是计算器的协议。这能成功的工作吗？ 

[![](https://p4.ssl.qhimg.com/t010e95e477c6c15b9d.png)](https://p4.ssl.qhimg.com/t010e95e477c6c15b9d.png)

Wow!我想这会伤害到一些exp作者的感情。他们现在还要弹点什么程序出来呢？（译注:因为漏洞POC一般都是弹计算器）calc和notepad不需要任何内存破坏漏洞就可以被打开，而cmd.exe现在又已经弃用了取而代之的是powershell。微软毁掉了你们这些人的乐趣。

这可能是一个很好的机会来枚举所有可加载的协议，来找出哪些应用程序可以接受参数。所以我们可以尝试注入代码。代码可能是二进制的也可能是纯JavaScript，这取决于应用程序是怎么编写（译注：coded，也有可能是指编码？）的以及它是如何处理参数的。这里有很多有趣的东西可以去搞，如果我们继续寻找协议，我们会发现可以打开大量的应用程序，甚至包括糖果大爆险（译注：国外的一个消消乐游戏？），我甚至都不知道我的电脑上安装过它。

通过这几次F3我学到了很多。例如，有一个microsoft-edge：协议，它会在新标签页中加载URL。它看起来似乎意义不大，直到我们想起了HTML页面应该有一个打开上限。弹出窗口屏蔽器(Pop-up Blocker)会阻止我们打开20个

microsoft-edge:http://www.google.com

标签页吗？ 

测试链接在这里：[http://unsafe.cracking.com.ar/demos/edgeprotocols/popups.html](http://unsafe.cracking.com.ar/demos/edgeprotocols/popups.html)

[![](https://p1.ssl.qhimg.com/t01512687f9a5cb4a27.png)](https://p1.ssl.qhimg.com/t01512687f9a5cb4a27.png)

我们来看看HTML5沙箱怎么样？如果你不是很熟悉它，那么它只是一种使用sandbox iframe属性和sandbox http头对网页施加的限制。例如，如果我们想在一个iframe中渲染内容，并且要确保它不运行javascript（甚至不能打开新标签页），那么我们只需使用此标签：

```
&lt;iframe src =“sandboxed.html”sandbox&gt; &lt;/ iframe&gt;
```

之后渲染的页面会被完全限制住。基本上它就只会渲染HTML和CSS了，就没有javascript或像访问cookie这样的东西了。事实上，如果我们控制沙盒粒度，并允许新建窗口或标签页，那么所有的这些新建的窗口和标签页以及打开的链接都会继承沙盒属性。然而，使用microsoft-edge协议可以完完全全的绕过这一点。 

测试链接：[http://unsafe.cracking.com.ar/demos/sandboxedge/](http://unsafe.cracking.com.ar/demos/sandboxedge/)

<br>

[![](https://p1.ssl.qhimg.com/t01d786190f197b47c6.png)](https://p1.ssl.qhimg.com/t01d786190f197b47c6.png)

很高兴可以看到microsoft-edge协议允许我们bypass不同的限制。我没有进一步的进行尝试，但是你可以试试看！这是一趟发现之旅，记住只是一个tweet（推文）触发了我进一步探索的动机，并且最终带给了我们一些真正值得研究的东西。

我继续在注册表编辑器中按F3，并且发现了read：协议，它引起了我的注意。因为当阅读它的javascript源代码时我发现它有UXSS的潜力，但是在我尝试的时候Edge浏览器不断的崩溃。它崩溃的次数实在是太多了。 例如，将iframe的位置设置为“read：”就足以崩溃掉浏览器，甚至包括所有的选项卡。你想要试试看看吗？ 

测试链接：[http://unsafe.cracking.com.ar/demos/edgeprotocols/readiframecrash.html](http://unsafe.cracking.com.ar/demos/edgeprotocols/readiframecrash.html)

好吧。。我很好奇到底是发生了什么，所以我在read：协议后面附加了几个字节，并使用WinDbg看看崩溃是否与无效的数据有关。为了实现起来简单又方便，我没有进行fuzzing或其它特殊的操作，只是诸如：

```
read:xncbmx,qwieiwqeiu;asjdiw!@#$%^&amp;*
```

哦，是的，我真的只是随便打了些这样的东西。我发现唯一的不会导致崩溃的读协议是加载了来自http[s]的内容的。其它的任何东西都会导致崩溃。

所以我们把WinDbg附加到Edge进程上。首先杀掉Edge进程和它的所有子进程，然后重新打开Edge进程并附加到使用EdgeHtml.dll模块的最新进程上进行调试。当然有更简单的方法，但是…是的，我就是这么做的。 打开命令行然后…



```
taskkill /f /t /im MicrosoftEdge.exe
** Open Edge and load the webpage but make sure it doesn't crash yet **
tasklist /m EdgeHtml.dll
```

这就足够了。现在打开WinDbg并附加到使用EdgeHtml模块的最新列出的Edge进程上。然后别忘了在WinDbg中挂上调试符号。 

[![](https://p0.ssl.qhimg.com/t0196dca7c6448bedfd.png)](https://p0.ssl.qhimg.com/t0196dca7c6448bedfd.png)

一旦附加成功，只需要按F5或者输入g，就可以让Edge进程继续运行。这是我的屏幕现在看起来的样子。在左边，有我用来测试的页面，在右边，是WinDbg附加到的特定的Edge进程。 

[![](https://p5.ssl.qhimg.com/t01015efb12b6b72526.png)](https://p5.ssl.qhimg.com/t01015efb12b6b72526.png)

我们将使用一个window.open与read：协议配合，来取代iframe。因为它更舒服。想想看，无论它们是哪种框架，协议/网址都可能会最终改变顶部的位置。

如果我们开始在iframe中使用协议，有可能我们自己的页面会被卸载，这会丢失我们刚刚输入的代码。我的特定测试页保存了我输入的内容，如果浏览器崩溃，它很可能会被恢复。但即使一切都已经保存，当我测试代码时，也可以改变我的测试页URL，我在一个新的窗口中打开它只是一个个人习惯。

在左侧屏幕上，我们可以快速的输入和执行JavaScript代码，右侧我们有WinDbg准备揭示这个崩溃后面发生了什么。让我们运行JavaScript代码并且等待在WinDbg里中断下来。



```
ModLoad: ce960000 ce996000 C:WindowsSYSTEM32XmlLite.dll
ModLoad: c4110000 c4161000 C:WindowsSystem32OneCoreCommonProxyStub.dll
ModLoad: d6a20000 d6ab8000 C:WindowsSYSTEM32sxs.dll
(2c90.33f0): Security check failure or stack buffer overrun - code c0000409 (!!! second chance !!!)
EdgeContent!wil::details::ReportFailure+0x120:
84347de0 cd29 int 29h
```

OK，看起来Edge知道出现了问题，因为它处于一个名为“ReportFailure”的函数中对不对？来吧，我知道我们可以立即假设，如果Edge中断在这里，它只是崩溃的“优雅”了一点。因此，让我们看看栈回溯，来看看我们是从哪里调用过来的。在WinDbg中输入“k”。



```
0:030&gt; k
# Child-SP RetAddr Call Site
00 af248b30 88087f80 EdgeContent!wil::details::ReportFailure+0x120
01 af24a070 880659a5 EdgeContent!wil::details::ReportFailure_Hr+0x44
02 af24a0d0 8810695c EdgeContent!wil::details::in1diag3::FailFast_Hr+0x29
03 af24a120 88101bcb EdgeContent!CReadingModeViewerEdge::_LoadRMHTML+0x7c
04 af24a170 880da669 EdgeContent!CReadingModeViewer::Load+0x6b
05 af24a1b0 880da5ab EdgeContent!CBrowserTab::_ReadingModeViewerLoadViaPersistMoniker+0x85
06 af24a200 880da882 EdgeContent!CBrowserTab::_ReadingModeViewerLoad+0x3f
07 af24a240 880da278 EdgeContent!CBrowserTab::_ShowReadingModeViewer+0xb2
08 af24a280 88079a9e EdgeContent!CBrowserTab::_EnterReadingMode+0x224
09 af24a320 d9e4b1d9 EdgeContent!BrowserTelemetry::Instance::2::dynamic
0a af24a3c0 8810053e shlwapi!IUnknown_Exec+0x79
0b af24a440 880fee33 EdgeContent!CReadingModeController::_NavigateToUrl+0x52
0c af24a4a0 88074f98 EdgeContent!CReadingModeController::Open+0x1d3
0d af24a500 b07df508 EdgeContent!BrowserTelemetry::Instance'::2::dynamic
0e af24a5d0 b0768c47 edgehtml!FireEvent_BeforeNavigate+0x118
```

先看看前两行，函数名字都叫XXX ReportFailure，你不觉得Edge是因为出了问题才会执行到这里的吗？那当然了！让我们继续找下去，直到我们找到一个有意义的函数名。下一个叫XXX FailFast，它看起来也像是一个Edge知道出了问题之后调用的函数。但是我们想找的是导致Edge出问题的代码，所以继续往下读。

下一个是XXX _LoadRMHTML。这个看起来好多了，你不同意吗？事实上，它的名字让我觉得它是用于加载HTML的。在崩溃之前断下会很有趣，所以为什么不在_LoadRMHTML上面设置断点呢？我们检查了栈回溯，现在来看看代码。

让我们先从那个点开始反汇编。这很容易，在WinDbg中使用“ub”命令。



```
0:030&gt; ub EdgeContent!CReadingModeViewerEdge::_LoadRMHTML+0x7c
EdgeContent!CReadingModeViewerEdge::_LoadRMHTML+0x5a:
8810693a call qword ptr [EdgeContent!_imp_SHCreateStreamOnFileEx (882562a8)]
88106940 test eax,eax
88106942 jns EdgeContent!CReadingModeViewerEdge::_LoadRMHTML+0x7d (8810695d)
88106944 mov rcx,qword ptr [rbp+18h]
88106948 lea r8,[EdgeContent!`string (88261320)]
8810694f mov r9d,eax
88106952 mov edx,1Fh
88106957 call EdgeContent!wil::details::in1diag3::FailFast_Hr (8806597c)
```

我们将专注于函数名，并且忽略其它的一切，怎么样？就像我们在《trying to find a variation for the mimeType bug》里做的一样（译注：作者的另一篇文章），如果我们失败了，我们就会继续深入分析。但有时在调试器上进行快速查看可以说明很多事情。

我们知道如果Edge执行到这个片段的最后一条指令时（地址88106957，FailFast_Hr）就会崩溃。我们的目的是想看看为什么我们会执行到那个地方，是谁导致了我们执行到那个地方。上面代码段的第一条指令似乎是调用了一个名字复杂的函数，这个函数显示了大量的信息。

```
EdgeContent！_imp_SHCreateStreamOnFileEx
```

在！号前面的部分是该指令所处模块的名称（译注：其实这只是个符号，跟指令搭不上边）。在这种情况下，它是EdgeContent，我们甚至不关心它的扩展名，只当它是代码。！之后有一个有趣的名字imp，然后SHCreateStreamOnFileEx似乎是一个表示“创建文件流”的函数名称。你觉得呢？事实上，imp让我想到，也许这是从不同的二进制文件中导入的函数。让我们google下它的名字，看看我们是否找到有趣的东西。 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0155751dea7d18368f.png)

这很不错,第一个结果就是我们搜索的准确名称。让我们点开看看。 

[![](https://p0.ssl.qhimg.com/t012e4f482be60ad684.png)](https://p0.ssl.qhimg.com/t012e4f482be60ad684.png)

好。这个函数接收的第一个参数是“指向以空字符结尾的字符串指针，该字符串指定文件名”。有趣！如果这段代码正在执行，那么它应该接收一个指向文件名的指针作为第一个参数。但是我们怎么能看到第一个参数呢？很容易，因为我们正在调试Win x64程序，函数调用约定规定“前4个参数是RCX，RDX，R8，R9”。这意味着第一个参数（指向文件名的指针）将被装入寄存器RCX中。

有了这些信息，我们可以在Edge调用这个函数之前设置一个断点，看看RCX在那个时刻的值是什么。但是首先我们需要重新启动进程，因为这个时候已经有点迟了：Edge进程已经崩溃了。请重新做上面描述的那些操作（杀死Edge进程，重新打开它，加载页面，找到进程并附加）。

这次，我们不再直接运行进程（F5），而是先设置一个断点。WinDbg显示了当我们执行“ub”命令时的准确偏移量。



```
0:030&gt; ub EdgeContent!CReadingModeViewerEdge::_LoadRMHTML+0x7c
EdgeContent!CReadingModeViewerEdge::_LoadRMHTML+0x5a:
8810693a ff1568f91400 call qword ptr [EdgeContent!_imp_SHCreateStreamOnFileEx (882562a8)]
88106940 85c0 test eax,eax
```

所以断点应该设置在EdgeContent！CReadingModeViewerEdge :: _ LoadRMHTML + 0x5a上。 

我们输入“bp”命令跟上函数名+offset，再按[ENTER]就可以成功设置断点。然后输入“g”让Edge继续运行。



```
0:029&gt; bp EdgeContent!CReadingModeViewerEdge::_LoadRMHTML+0x5a
0:029&gt; g
```

这很令人兴奋，我们想要在SHCreateStreamOnFileEx函数执行之前看到RCX指向的文件名（或字符串）。 让我们运行javascript代码并等待它中断下来。Windbg中断之后的信息如下所示：



```
Breakpoint 0 hit
EdgeContent!CReadingModeViewerEdge::_LoadRMHTML+0x5a:
8820693a ff1568f91400 call qword ptr [EdgeContent!_imp_SHCreateStreamOnFileEx (883562a8)]
```

这太棒了，现在我们可以检查RCX寄存器指向的内容。为此，我们将使用“d”命令（显示内存内容）跟上寄存器名称，我们输入如下所示的命令：



```
0:030&gt; d @rcx
02fac908 71 00 77 00 69 00 65 00-69 00 77 00 71 00 65 00 q.w.i.e.i.w.q.e.
02fac918 69 00 75 00 3b 00 61 00-73 00 6a 00 64 00 69 00 i.u.;.a.s.j.d.i.
02fac928 77 00 21 00 40 00 23 00-24 00 25 00 5e 00 26 00 w.!.@.#.$.%.^.&amp;.
02fac938 2a 00 00 00 00 00 08 00-60 9e f8 02 db 01 00 00 *.......`.......
02fac948 10 a9 70 02 db 01 00 00-01 00 00 00 00 00 00 00 ..p.............
02fac958 05 00 00 00 00 00 00 00-00 00 00 00 19 6c 01 00 .............l..
02fac968 44 14 00 37 62 de 77 46-9d 68 27 f3 e0 92 00 00 D..7b.wF.h'.....
02fac978 00 00 00 00 00 00 08 00-00 00 00 00 00 00 00 00 ................
```

虽然这看起来不是很友好，但在第一行的右边我看到了一些类似于unicode字符串的东西。我使用du命令来让它显示为unicode字符串。



```
0:030&gt; du @rcx
02fac908 "qwieiwqeiu;asjdiw!@#$%^&amp;*"
```

Nice!回头看看我们刚刚运行的JavaScript代码 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a990ad06b4c37ee0.png)

看来，传递给这个函数的参数值就是在逗号后面输入的内容。当我们知道了这一点再加上知道它期望获得一个文件名之后，我们就可以尝试构造一个完整的路径来指向我的磁盘中的东西。因为Edge在AppContainer内部运行，我们尝试的是一个可访问的文件。例如windows/system32目录里的内容。 

```
read:,c:windowssystem32driversetchosts
```

我们同时删除了逗号之前的垃圾数据，因为它似乎没什么作用（虽然它值得去做更多的研究！）。让我们快速的分离进程，并重新启动Edge来运行我们的新代码。 



```
url = "read:,c:\windows\system32\drivers\etc\hosts";
w = window.open(url, "", "width=300,height=300");
```

正如预期，本地文件在新窗口中被加载并且没有发生崩溃。 

[![](https://p0.ssl.qhimg.com/t0115c38c65d85e36c1.png)](https://p0.ssl.qhimg.com/t0115c38c65d85e36c1.png)

测试链接:[http://unsafe.cracking.com.ar/demos/edgeprotocols/localfile.html](http://unsafe.cracking.com.ar/demos/edgeprotocols/localfile.html)

我的研究在这里就告一段落了，但我相信这些东西值得去进一步研究，当然这取决于你个人的兴趣：

A）枚举所有可加载的协议，并通过查询字符串来攻击那些应用程序。

B）测试microsoft-edge：这可以绕过HTML5沙箱、弹出窗口拦截器（popup blocker）和谁知道是什么鬼东西。

C）继续研究read：协议。我们找到了一种方法来阻止它崩溃，但是请记住我们可以控制SHCreateStreamOnFileEx函数期望的值！这值得我们进行更多的尝试。此外，我们可以研究一下传入的参数，看看是否使用逗号分割参数等等。如果你认为调试二进制文件是很无聊的，那么你可以尝试使用XSS阅读视图。

我希望你找到成吨的漏洞！如果你有问题，请通过@magicmac2000来找我。

祝你今天愉快！
