> 原文链接: https://www.anquanke.com//post/id/86533 


# 【技术分享】如何不调用PowerShell.exe获得Empire agent


                                阅读量   
                                **120661**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p5.ssl.qhimg.com/t01fe5dacfbd51e73a5.png)](https://p5.ssl.qhimg.com/t01fe5dacfbd51e73a5.png)**

****

译者：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**0x00 前言**

客户端已经使用Applocker来禁用PowerShell.exe，并且我买不起Cobalt Strike。但我又想通过一个钓鱼活动来在工作站中获得一个Empire payload。对于Empire的启动方式，几乎全部都依赖PowerShell.exe的使用。其他的方式（类似msbuild.exe）需要在磁盘释放一个文件，并且我真的很喜欢regsvr32的方式，其可以通过网络来加载我的.sct文件（它也会在磁盘中释放一个文件）或者使用[**ducky**](https://hakshop.com/products/usb-rubber-ducky-deluxe)的方式。我也很喜欢在文档中使用VBA或者HTA的方式的便捷。问题是，Empire是一个PowerShell RAT，因此必须运行PowerShell。

建议使用的方式是调用Empire.dll或者通过网络SMB共享调用Empire.exe。虽然我没有尝试这种方法，但是我确信它是有效的。对于SMB的方式，我不喜欢的地方是会有一个外连的SMB连接，在任何观察流量的防御者眼中这都是非常可疑的。

现在我需要3种payload：

1. 生成一个empire.exe

2. 生成一个empire.dll

3. 生成一个不调用powershell.exe的empire.sct

我将使用的工具和资源如下：

1. [**@sixdub**](https://twitter.com/sixdub)的[**SharpPick**](https://github.com/PowerShellEmpire/PowerTools)代码库

2. James Foreshaw ([**@tiraniddo**](https://twitter.com/tiraniddo?lang=en))的[**DotNetToJS**](https://github.com/tyranid/DotNetToJScript)

3. Casey Smith ([**@subtee**](https://twitter.com/subTee))的[**AllTheThings**](https://github.com/subTee/AllTheThings)

4.Visual Studio。不是必要的。你可以使用csc.exe来生成你的项目，但是我没有测试过。我选择使用Visual Studio 2010来生成PowerPick，尽管2012可能更好。据我所知，那将会下载大量东西。好处是2010/2012中包含了老的.NET库（变得越来越难找到）。

如果没有上述作者的贡献，我将无法完成这个，我非常感谢他们。下面我将将这些伟大的工作组合到一起来实现我之前未能找到过的成果。

注意：在我的研究中，我发现了两个项目也做了几乎同样的事情，他们都是使用DotNetToJScript，但是对我并不适用。

1. StarFighters (@Cn33liz)。首先，我非常喜欢通过网络运行编码过的二进制文件。这个包含了一个编码的powershell.exe，其接收并执行你的启动器的代码。我尝试了下，能得到一个Empire，但是不能执行脚本。

2. CACTUSTORCH (@vysecurity)。我也试用了这个，但是我不想注入shellcode到启动的二进制中，而且我不知道如何使用SharpPick将我的启动器转化为shellcode。它可能是可行的，只是我不知道而已。例子中，@vysecurity 的提供了使用Cobalt Strike或者Meterpreter shellcode的输出的方式。

<br>

**0x01 生成一个Empire.exe**

我经常看到Cobalt Strike使用“updates.exe”，它是一个定期的信号发送器。对于Empire，你能使用这种方式来做到类似的东西。将它添加到邮件内容中去，建议需要安装新的防病毒软件。或者通过WMI/psexec来运行它，或者在Outlook中作为一个内嵌的[**OLE对象**](https://doublepulsar.com/oleoutlook-bypass-almost-every-corporate-security-control-with-a-point-n-click-gui-37f4cbc107d0)（[**@tyler_robinson**](https://twitter.com/tyler_robinson?lang=en)）。

这可能是不调用PowerShell.exe而获得一个agent的最简单的一种方式。

通过git来得到一份[**PowerPick**](https://github.com/PowerShellEmpire/PowerTools)的拷贝，并在Visual Studio中打开项目。

首先，你需要混淆一些项目属性。改变程序和程序集信息的名称。可以通过菜单“项目-SharpPick 属性”来做到。确保修改“输出类型”为“Windows应用程序”，以便当你双击运行或者从CLI执行后，它能在后台运行。

[![](https://p5.ssl.qhimg.com/t01d711db857ed82eda.png)](https://p5.ssl.qhimg.com/t01d711db857ed82eda.png)

点击“程序集信息”按钮，并修改属性。

[![](https://p1.ssl.qhimg.com/t01a1a045382e15eb2f.png)](https://p1.ssl.qhimg.com/t01a1a045382e15eb2f.png)

现在你还要将Program.cs中的代码修改[**如下**](https://gist.github.com/bneg/bf8c05664324e3efeb1fb05902152a20)：

[![](https://p2.ssl.qhimg.com/t014b41394d46456081.png)](https://p2.ssl.qhimg.com/t014b41394d46456081.png)

字符串“stager”只包含base64编码的Empire启动器的信息。它需要解码并传给RunPS()函数，该函数将PowerShell命令发送给System.Management.Automation，这里是PowerShell的魅力所在。将直接进入Windows核心。

现在在菜单中选择“生成-生成解决方案”或者点击“F6”。生成的二进制文件位于“PowerToolsEmpire_SCTPowerPickbinx86Debug”。

你可能会遇到关于ReflectivePick不能生成的错误。你能选择菜单“生成-配置管理器”，并从“项目上下文”中去除“ReflectivePick”。因为我们不需要它。

双击可执行文件来测试下二进制文件，或者在CLI中运行测试。在你启动或执行后它应该是运行于后台的。

<br>

**0x02 生成一个Empire.dll**

有可能你会需要一个DLL，以便你能使用Casey找到的那些绕过Applocker的方法。它也可以通过rundll32.exe运行。为了实现这个，我们稍微改变下我们的项目，在代码中添加一些入口点。下面的代码直接来自于@subtee的AllTheThings。

不像EXE，只要打开项目并改变一些配置。更重要的是你要在项目属性中将“输出类型”修改为“类库”。你还应该设置你的“启动对象”为默认值（基于命名空间和类名）。

[![](https://p0.ssl.qhimg.com/t018c14992023b15ab2.png)](https://p0.ssl.qhimg.com/t018c14992023b15ab2.png)

接下来，安装Visual Studio的nuget包管理器。一旦安装完成，你需要通过下面命令来安装依赖库“UnmanagedExports”：

[![](https://p1.ssl.qhimg.com/t01c5d408242313791c.png)](https://p1.ssl.qhimg.com/t01c5d408242313791c.png)

再次选择“生成-生成解决方案”或者点击“F6”，能在生成目录中生成一个LegitLibrary.dll。

运行下面的命令测试你的DLL：

[![](https://p5.ssl.qhimg.com/t018084d954597fb1d8.png)](https://p5.ssl.qhimg.com/t018084d954597fb1d8.png)

这将返回一个新的agent到你的Empire C2。如果你在Process Explorer中观察，你能看到rundll32进程。

<br>

**0x03 生成一个Empire.sct**

这可能是最复杂的地方，因为它涉及一系列操作。最终的流程应该如下：填充PowerShell到一个.NET应用中，将.NET应用转化为base64编码的二进制并存于JavaScript文件中，然后填充到.sct文件中。你能使用regsvr32来调用sct，其将在你的web或文件服务器上运行.SCT中的JavaScript。

我们的目标是Empire.exe payload（base64编码后的）。项目选项应该和Empire.exe的相同，就是“Windows应用程序”。代码有点不同，因为JavaScript需要公共方法来执行你的代码（[参考](https://gist.github.com/bneg/449612acde4f670b7dafb5a05f0ce88e)）。

[![](https://p0.ssl.qhimg.com/t01db44032a5397cb4c.png)](https://p0.ssl.qhimg.com/t01db44032a5397cb4c.png)

生成解决方案，找到生成的二进制文件，它应该是一个EXE。

接着，下载[**DotNetToJScript**](https://github.com/subTee/DotNetToJScript)，并在Visual Studio中打开项目，在项目选项中将.NET目标改为“.NET 版本 3.5”（或者2.0），并生成它。一旦生成完成，找到DotNetToJScript.exe和NDesk.Options.dll，把他们和LegitScript.exe放在同一个目录中。

运行下面的命令（-c是入口点，改为你选择的命令空间.类）：

[![](https://p5.ssl.qhimg.com/t015caa8919b8bdb96d.png)](https://p5.ssl.qhimg.com/t015caa8919b8bdb96d.png)

将得到一个JavaScript脚本文件legitscript.js。DotNetToJScript输出可以有多种语言格式，包括VBScript和内嵌到Office文档中的VBA，或者其他你需要的。

通过运行下面的命令来测试下脚本：

[![](https://p3.ssl.qhimg.com/t01ac6782a705adc4e9.png)](https://p3.ssl.qhimg.com/t01ac6782a705adc4e9.png)

在你的工作站后台应该启动了一个新的agent。它运行于wscipt进程中。

如果你确认一切就绪，现在就可以包装一个.sct文件，以便我们能使用regsvr32.exe来调用。

将legitscript.js的全部内容放置于CDATA标签中（如下图）。通过下面的命令在Empire中得到XML格式。

[![](https://p3.ssl.qhimg.com/t016905d9d100175c45.png)](https://p3.ssl.qhimg.com/t016905d9d100175c45.png)

这个设置不重要，但是能作为你的监听器来确保“OutFile”被设置为null或“”，因为这将打印内容到屏幕上。如果你从Empire中得到内容，清空CDATA标签中的内容，并用legitscript.js的内容替代。

[![](https://p2.ssl.qhimg.com/t01bea0016371ab6c3f.png)](https://p2.ssl.qhimg.com/t01bea0016371ab6c3f.png)

保存为2legit.sct，使用下面命令测试：

[![](https://p4.ssl.qhimg.com/t01684b249c5f83216f.png)](https://p4.ssl.qhimg.com/t01684b249c5f83216f.png)

<br>

你将再次得到一个新的agent。将这个.sct文件保存到你的web或者文件服务器上，使用“/i:https://example.com/2legit.sct&amp;#8221”能远程调用。这能绕过Applocker，因为regsvr32.exe是微软签名的二进制文件。

<br>

**0x04 总结**

PowerShell非常好用，攻击者已经使用它很多年了。最好的建议是保持客户端环境为PowerShell受限模式，禁用PowerShell v2，并升级PowerShell最新版（支持脚本块日志）。阻止PowerShell在你的环境中运行非常困难且几乎不太实际，因此至少要知道何时和如何使用它。
