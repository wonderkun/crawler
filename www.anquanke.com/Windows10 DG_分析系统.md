> 原文链接: https://www.anquanke.com//post/id/152143 


# Windows10 DG：分析系统


                                阅读量   
                                **141289**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：tyranidslair.blogspot.com
                                <br>原文地址：[https://tyranidslair.blogspot.com/2017/08/copy-of-device-guard-on-windows-10-s.html](https://tyranidslair.blogspot.com/2017/08/copy-of-device-guard-on-windows-10-s.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0123d556cdabb3f37c.png)](https://p2.ssl.qhimg.com/t0123d556cdabb3f37c.png)

在[上一篇文章](https://tyranidslair.blogspot.com/2017/07/dg-on-windows-10-s-executing-arbitrary.html)中，我们介绍了不需要Office副本或者升级到Windows10 Pro版本就可以在Win10S上执行任意.NET代码，然而当UMCI被启用时，我们并没有实现运行任意应用程序的终极目标。我们可以用任意代码来运行一些分析工具帮助我们更好的理解Win10S，以便对系统的进一步修改。 

这篇文章主要介绍如何尽可能以简单的方式实现加载更复杂的.NET内容，包括在不需要运行powershell.exe（许多列入黑名单的应用程序之一）的情况下获得完整的PowerShell环境（合理范围内）。



## 处理程序集加载

我们在上一篇文章中使用的简单.NET程序集只依赖于内置的系统程序集。这些系统程序集由操作系统提供，而且使用了Microsoft Windows Publisher证书进行签名认证。这意味着系统组件可以通过完整的系统策略加载为映像文件。当然，我们自己构建的任何东西都不允许从文件中加载。

SI策略不适用于我们从字节数组加载程序集。对于具有系统依赖性的简单程序集，这不一定是个问题。但是如果我们要加载引用了其他不可信程序及的更复杂的程序集，我们会遇到更多困难。由于.NET使用后期绑定，所以你不会立即发现程序集加载的问题，只有当你尝试从这个程序集中访问方法或者类型时候，Framework才会尝试加载它，从而导致异常。

当程序集被加载时，Framework将解析程序集的名称。我们是否可以不先从字节数组中预加载需要依赖的程序集，而是等到我们需要时候再加载它？让我们尝试从字节数组加载程序集，然后按照名称重新加载。如果预加载有效，则按照名称加载也应该成功。编译下面简单的c#应用程序，然后尝试再次按照全名加载它：

```
using System;
 using System.IO;
 using System.Reflection;
```

```
class Program
 `{`
    static void Main(string[] args)
    `{`
        try
        `{`
            Assembly asm = Assembly.Load(File.ReadAllBytes(args[0]));
            Console.WriteLine(asm.FullName);
            Console.WriteLine(Assembly.Load(asm.FullName));
        `}`
        catch (Exception ex)
        `{`
            Console.WriteLine(ex.Message);
        `}`
    `}`
 `}`
```

现在运行这个程序并将其路径传递给要加载的程序集（确保程序集在你编译的上述代码的目录之外）。你将看到类似于下面的输出：

C:buildLoadAssemblyTest&gt; LoadAssemblyTest.exe ..test.dll test,Version=1.0.0.0, Culture=neutral, PublicKeyToken=null

Couldnot load file or assembly ‘test, Version=1.0.0.0, Culture=neutral,PublicKeyToken=null’ or one of its dependencies. 

The system cannot find the file specified.

我猜不会起作用，因为按名称加载程序集时候会抛出异常。这是.net从字节数组加载程序集的一种限制。被加载的程序集的名字没有在任何全局程序集表中注册。一方面这点很好，它允许在一个进程中同时共存许多名字相同的程序集。另一方面又不好，因为这样如果我们不直接引用程序集实例，我们不能访问到这个程序及里的任何东西。由于引用的程序集始终按照名称加载，这意味着不会有预加载去帮助更复杂的程序集工作。

.NET框架针对这个问题提供了一个解决方案，你可以指定Assembly Resolver事件处理程序。Assembly Resolver 事件是指只要运行时发生无法从加载的程序集列表或者磁盘的文件中找到程序集，就会调用此事件。这种情况通常发生在程序集位于应用程序的目录之外。然而需要注意的是如果运行时发现磁盘上的一个文件符合它的规范它会尝试加载它。如果SI策略不允许此文件，则加载失败。但是运行时不认为解析失败，这种情况下Assembly Resolver就不会调用事件处理程序。

事件处理程序是通过名称来解析。这个名称可以是部分的，也可以是带有附加信息的完整程序集名称（比如PublicKeyToken 和Version）。因此我们只需要将这个名字的字符串传递给[AssemblyName](https://msdn.microsoft.com/en-us/library/system.reflection.assemblyname(v=vs.110).aspx)类，并用它来提取字符集的名称。 我们就可以用这个名字来搜索具有该名称的DLL或者EXE扩展名的文件。在我[GitHub](https://github.com/tyranid/DeviceGuardBypasses/tree/master/Bootstrap)上创建的示例程序中，默认要么在用户文档的反汇编目录中搜索，要么就在ASSEMBLY_PATH环境变量中指定任意路径列表中搜索。最后，如果我们发现了这个程序集文件，我们将从字节数组中加载它并将它返回给事件的调用者，确保缓存程序集文件以供后续查询使用。

```
AssemblyName name = new AssemblyName(args.Name);
string path = FindAssemblyPath(name.Name, ".exe") ?? 
              FindAssemblyPath(name.Name, ".dll");
if (path != null) `{`
    Assembly asm = Assembly.Load(File.ReadAllBytes(path));
    _resolved_asms[args.Name] = asm;
    _resolved_asms[asm.FullName] = asm;
 `}`
 else `{`
    _resolved_asms[args.Name] = null;
 `}`
```

最后一步就是用[ExecuteAssemblyByName](https://msdn.microsoft.com/en-us/library/system.appdomain.executeassemblybyname(v=vs.110).aspx)方法加载一个程序集。这个程序集包含一个Main函数入口，被称为startasm.exe。你可以将所有的分析代码放在一个单独的程序集里，但是这会很快就变得很大，并且将序列化数据发送到命名为AddInProcess的管道不会很有效率。此外通过启动新的可执行文件，可能会快速替换要运行的方法，而且不需要在每次更改程序集时候重新生成scriptlet 。

需要注意的是，如果要加载的程序集包含native代码（比如混合模式CIL和C++）那么上面说的就不能工作了。如果要运行native代码就需要将程序集作为映像加载，它不能从字节数组中运行。当然，纯托管的CIL可以完成本机代码可执行的所有操作，不过要使用.NET编写你的工具。



## 构建Powershell控制台

因为已经有了能够按名称执行任意.NET程序集（包括依赖项）的能力，因此我们可以开始运行交互环境了。还有什么比PowerShell更好的交互环境呢？由于PowerShell是用.NET编写的，因此powershell.exe作为一个.NET程序集是一个完美应用场景。

[![](https://p0.ssl.qhimg.com/t01daffedbf140095f6.png)](https://p0.ssl.qhimg.com/t01daffedbf140095f6.png)

虽然PowerShell ISE是一个完整的.NET程序集，而且我们可以加载它，但是大多数情况下我更喜欢使用命令行操作。虽然可以在没有PowerShell.exe的情况下获取PowerShell的研究，但是在我知道的例子中比如[https://github.com/p3nt4/PowerShdll](https://github.com/p3nt4/PowerShdll)，它们并不倾向于以一种简单易行的方式进行。通常，它们实现自己的shell并将PS脚本通过命令行传到PowerShell空间运行。幸运的是，我们不必去猜测PowerShell.exe是如何工作的，我们可以对二进制文件进行逆向，但现在已经开源的。比如这是用于启动控制台的[非托管代码](https://github.com/PowerShell/PowerShell/blob/6afb8998e79b424cc36ba77d6f7618bc3ebedecf/src/powershell-native/nativemsh/pwrshexe/MainEntry.cpp)。

Native入口函数创建了一个[UnmanagedPSEntry](https://msdn.microsoft.com/en-us/library/microsoft.powershell.unmanagedpsentry(v=vs.85).aspx)类的实例并调用了Start方法。只要存在该进程的控制台，调用Start方法就会提供一个完全可用的PowerShell交互环境。虽然AddInProcess已经是一个控制台应用程序，但是你可以调用[AllocConsole](https://msdn.microsoft.com/en-us/library/windows/desktop/ms681944(v=vs.85).aspx)或者[AllocConsole](https://msdn.microsoft.com/en-us/library/windows/desktop/ms681944(v=vs.85).aspx)创建一个新的控制台，或者需要时利用现存的控制台。我们甚至可以设定一个控制台标题和图标，以便为我们运行PowerShell时提供方便。

```
AllocConsole();
SetConsoleTitle("Windows Powershell");
UnmanagedPSEntry ps = new UnmanagedPSEntry();
ps.Start(null, new string[0]);
```

我们已经开始运行PowerShell，至少在开始使用控制台前一切都好。这个时候你可能会遇到下面这个错误：

[![](https://p3.ssl.qhimg.com/t01a466bd357385c269.png)](https://p3.ssl.qhimg.com/t01a466bd357385c269.png)

看上去我们成功绕过了UMCI的对映像加载的检查，但PowerShell仍然尝试执行约束语言模式。显而易见，我们所做的只是为了不加载powershell.exe，而不是PowerShell UMCI锁定策略的其余部分。运行的模式的检查是SystemPolicy类中的GetSystemLockdownPolicy方法做的。这将调用Windows Lockdown Policy DLL（WLDP）中的WldpGetLockdownPolicy函数来查询PowerShell的操作。传递空路径给这个函数会返回通用的系统策略。这个函数也是检测不合法文件的策略的入口函数，通过传递一个路径给签名的脚本，策略将被强制选择到这个脚本上。这就是微软模块以完整语言模式运行，而主shell以Constrained方式运行。看完之后可以很清楚知道SystemPolicy类缓存了策略查找的结果在私有的systemLockdownPolicy静态变量中。因此，如果在调用任何其他PS代码之前，我们使用反射将SystemEnforcementMode值设置为None，就可以关闭掉这个lockdown策略检查了。

```
var fi = typeof(SystemPolicy).GetField("systemLockdownPolicy", 
        BindingFlags.NonPublic | BindingFlags.Static);
 fi.SetValue(null, SystemEnforcementMode.None);
```

这样做我们所需的PowerShell就没有锁定限制。

[![](https://p1.ssl.qhimg.com/t0164d0ac29d06dd977.png)](https://p1.ssl.qhimg.com/t0164d0ac29d06dd977.png)

我已经将[RunPowershell](https://github.com/tyranid/DeviceGuardBypasses/tree/master/RunPowershell)的实现代码上传到GitHub。构建可执行文件并将其复制到%USERPROFILEDocumentsassemblystartasm.exe  然后使用以前的DG bypass执行代码。



## 系统觅踪

启动PowerShell并运行后，我们可以对系统做一些检查。我要做的第一件事就是安装我的NtObjectManager模块。安装模块的cmdlet在尝试安装NuGet模块不能很好的工作，因为NuGet模块在lockdown策略下不允许加载。其实你可以只下载模块的文件，如果你指定模块的目录在实例的程序集路径列表中进行编译，则只需导入PSD1文件即可成功加载。

我在NtApiDotNet程序集中加载了几个方法来dump系统信息中的SI策略。比如这个[NtSystemInfo.CodeIntegrityOptions](https://github.com/google/sandbox-attacksurface-analysis-tools/blob/72591e17b8076ad807e85ac9c6878ed010fcb494/NtApiDotNet/NtSystemInfo.cs#L924) 是dump当前CI启用标记，[NtSystemInfo.CodeIntegrityFullPolicy](https://github.com/google/sandbox-attacksurface-analysis-tools/blob/72591e17b8076ad807e85ac9c6878ed010fcb494/NtApiDotNet/NtSystemInfo.cs#L972)是Windows Creator Update（Win10S支持）中一个新选择来dump所有配置的CI策略。有趣的是Win10S中运行时实际由两个策略启用，SI策略和某种似乎是一些排序的撤销策略。通过这种方式提取了策略之后，我们就能够保证系统强制的正确的策略信息，而不仅仅我们认为的文件是策略。

[![](https://p5.ssl.qhimg.com/t01ec2ae1a533ad0d75.png)](https://p5.ssl.qhimg.com/t01ec2ae1a533ad0d75.png)

最后我添加了一个PowerShell cmdlet [New-NtKernelCrashDump](https://github.com/google/sandbox-attacksurface-analysis-tools/blob/72591e17b8076ad807e85ac9c6878ed010fcb494/NtObjectManager/NtObjectManager.psm1#L174)来创建内核崩溃转储（不要担心它不会导致系统崩溃），只要你有了SeDebugPrivilege ，你就可以以管理员的身份来运行AddInProcess。虽然这样你不能修改系统，但是你至少可以查看内部数据结构。当然你需要将内核转储复制到另个一系统才能运行WinDBG。

[![](https://p3.ssl.qhimg.com/t014085354b53f84128.png)](https://p3.ssl.qhimg.com/t014085354b53f84128.png)



## 总结

这篇文章只是简单介绍了如何在Win10S上运行复杂的.NET程序。我提议你尽可能在.NET中编写分析工具，因为这样可以让他们更容易在锁定的系统上运行。当然你也可以使用反射式DLL加载器，但是当.NET已经为你写好了这些，你何必再做呢？

审核人：yiwang   编辑：边边
