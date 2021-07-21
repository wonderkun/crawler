> 原文链接: https://www.anquanke.com//post/id/84597 


# 【技术分享】Use MSBuild To Do More（渗透中MSBuild的应用技巧）


                                阅读量   
                                **166757**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



****

**作者：三好学生**

**稿费：500RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿**

**[![](https://p4.ssl.qhimg.com/t01587c6dc736b8f906.jpg)](https://p4.ssl.qhimg.com/t01587c6dc736b8f906.jpg)**

**0x00 前言**

最近Casey Smith@subTee更新了一系列关于”MSBuild”的研究进展，对我有很大启发。

本文将基于他公开的POC，并结合我的研究心得，介绍以下MSBuild的应用技巧：

Execute PowerShell Commands

Execute PE file

Execute Shellcode

VisualStudio Persistence

<br>

**0x01 简介**

MSBuild是Microsoft Build Engine的缩写，代表Microsoft和Visual Studio的新的生成平台

MSBuild可在未安装Visual Studio的环境中编译.net的工程文件

MSBuild可编译特定格式的xml文件

更多基本知识可参照以下链接：

[https://msdn.microsoft.com/en-us/library/dd393574.aspx](https://msdn.microsoft.com/en-us/library/dd393574.aspx)

<br>

**0x02 常规用法**

**1. 编译xml文件并执行代码**



```
&lt;?xml version="1.0" encoding="utf-8" ?&gt;
&lt;Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003"&gt;
  &lt;Target Name="PrintCurrentDateTime"&gt;
    &lt;Message Text="The current date and time is: $([System.DateTime]::Now)." /&gt;
  &lt;/Target&gt;
&lt;/Project&gt;
```

保存为test.csproj

cmd下执行：

```
C:WindowsMicrosoft.NetFrameworkv4.0.30319msbuild.exe test.csproj
```

在cmd下会输出显示当前时间，如图

[![](https://p0.ssl.qhimg.com/t016b939828d2809106.jpg)](https://p0.ssl.qhimg.com/t016b939828d2809106.jpg)

**2. 编译xml文件生成exe**



```
using System;
class Test
`{`
    static void Main()
    `{`
        Console.WriteLine("Hello world");
    `}`
`}`
```

保存为hello.cs



```
&lt;Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003"&gt;
    &lt;Target Name="Compile"&gt;
        &lt;CSC Sources="hello.cs" OutputAssembly="hello.exe" /&gt;
    &lt;/Target&gt;
&lt;/Project&gt;
```

保存为hello.csproj

hello.cs和hello.csproj放于同一目录

cmd下执行：

```
C:WindowsMicrosoft.NetFrameworkv4.0.30319msbuild.exe hello.csproj
```

可以编译生成hello.exe，如图

[![](https://p3.ssl.qhimg.com/t01b0760b2b4ea2dbf9.jpg)](https://p3.ssl.qhimg.com/t01b0760b2b4ea2dbf9.jpg)

**注：编译文件满足xml文件格式即可，后缀名任意**

<br>

**0x03 扩展用法**

在.NET Framework 4.0中支持了一项新功能”Inline Tasks”，被包含在元素UsingTask中，可用来在xml文件中执行c#代码

详细介绍可参考如下链接：

[https://msdn.microsoft.com/en-us/library/dd722601.aspx?f=255&amp;MSPPError=-2147217396](https://msdn.microsoft.com/en-us/library/dd722601.aspx?f=255&amp;MSPPError=-2147217396)

**<br>**

**1. HelloWorld示例**

以下代码保存为helloworld:



```
&lt;Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003"&gt;
  &lt;Target Name="Hello"&gt;
   &lt;HelloWorld /&gt;
  &lt;/Target&gt;
  &lt;UsingTask
    TaskName="HelloWorld"
    TaskFactory="CodeTaskFactory"
    AssemblyFile="C:WindowsMicrosoft.NetFrameworkv4.0.30319Microsoft.Build.Tasks.v4.0.dll" &gt;
    &lt;ParameterGroup/&gt;
    &lt;Task&gt;
      &lt;Using Namespace="System" /&gt;  
      &lt;Code Type="Fragment" Language="cs"&gt;
        &lt;![CDATA[
                Console.WriteLine("Hello World");       
        ]]&gt;
      &lt;/Code&gt;
    &lt;/Task&gt;
    &lt;/UsingTask&gt;
&lt;/Project&gt;
```

注：保存的文件名任意

cmd下执行：

```
C:WindowsMicrosoft.NETFrameworkv4.0.30319msbuild.exe helloworld
```

cmd输出helloworld，如图

[![](https://p2.ssl.qhimg.com/t013d055eab699398bb.png)](https://p2.ssl.qhimg.com/t013d055eab699398bb.png)

**<br>**

**2. 执行powershell命令**

可参照Casey分享的POC，地址如下：

[https://gist.github.com/subTee/6b236083da2fd6ddff216e434f257614](https://gist.github.com/subTee/6b236083da2fd6ddff216e434f257614)

该POC已将c#代码转换成xml文件的格式，编写需要注意的部分如下：

[![](https://p5.ssl.qhimg.com/t01c83ae765d7313a33.png)](https://p5.ssl.qhimg.com/t01c83ae765d7313a33.png)

**标记1**TaskName可修改，但两个位置的名称需要对应

**<br>**

**标记2**为固定格式:TaskFactory="CodeTaskFactory"

**<br>**

**标记3**的路径在不同系统可能会有区别，准确的为：

"$(MSBuildToolsPath)Microsoft.Build.Tasks.v4.0.dll"

系统默认安装路径为:

```
"C:WindowsMicrosoft.NetFrameworkv4.0.30319Microsoft.Build.Tasks.v4.0.dll"
```

**<br>**

**标记4**为一个简单的输出helloworld实例

[![](https://p0.ssl.qhimg.com/t0159b17c22d0c30d15.png)](https://p0.ssl.qhimg.com/t0159b17c22d0c30d15.png)

**标记5**为固定格式，定义为public class ClassExample : Task, ITask

实际测试POC如图,成功执行powershell命令

[![](https://p1.ssl.qhimg.com/t010fc23bfe87ef03aa.png)](https://p1.ssl.qhimg.com/t010fc23bfe87ef03aa.png)

**<br>**

**3. 执行PE文件**

Casey分享的POC地址如下： 

[https://gist.github.com/subTee/ca477b4d19c885bec05ce238cbad6371](https://gist.github.com/subTee/ca477b4d19c885bec05ce238cbad6371)

但是上传的文件被截断，导致部分代码无法查看，于是尝试自己实现

结合之前研究过的代码，地址如下：

[https://gist.github.com/subTee/00cdac8990584bd2c2fe](https://gist.github.com/subTee/00cdac8990584bd2c2fe)

对照上文提到的xml格式，编写代码实现在Inline Tasks中内存加载64位的mimikatz.exe，实现代码的下载地址为：

[https://github.com/3gstudent/msbuild-inline-task/blob/master/executes%20mimikatz.xml](https://github.com/3gstudent/msbuild-inline-task/blob/master/executes%20mimikatz.xml)

cmd下执行：

```
C:WindowsMicrosoft.NETFrameworkv4.0.30319msbuild.exe aa
```

报错，如图

[![](https://p1.ssl.qhimg.com/t0107f5cd7f789f9011.png)](https://p1.ssl.qhimg.com/t0107f5cd7f789f9011.png)

**解决方法：**

需要换用64位的.net Framework，原代码无需修改，只需要使用64位的.net Framework加载就好

cmd下执行：

```
C:WindowsMicrosoft.NETFramework64v4.0.30319msbuild.exe aa
```

加载成功，如图

[![](https://p2.ssl.qhimg.com/t0163630c3c0eb45961.png)](https://p2.ssl.qhimg.com/t0163630c3c0eb45961.png)

**<br>**

**4. 执行shellcode**

参考自[https://gist.github.com/subTee/a06d4ae23e2517566c52](https://gist.github.com/subTee/a06d4ae23e2517566c52)

使用msf生成32位shellcode：



```
use windows/exec
set CMD calc.exe
set EXITFUNC thread
generate -t csharp
```

同样结合上文提到的xml格式，编写代码实现在Inline Tasks中执行shellcode，实现代码的下载地址为：

[https://github.com/3gstudent/msbuild-inline-task/blob/master/executes%20shellcode.xml](https://github.com/3gstudent/msbuild-inline-task/blob/master/executes%20shellcode.xml)

保存为SimpleTasks.csproj，在cmd下执行：

```
C:WindowsMicrosoft.NETFrameworkv4.0.30319msbuild.exe SimpleTasks.csproj
```

如图，成功执行shellcode弹出计算器

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e54f7d3c3c90abdd.png)

在64位系统下，先将shellcode替换为64位，然后换用64位的.net Framework执行即可，代码下载地址为：

[https://github.com/3gstudent/msbuild-inline-task/blob/master/executes%20×64%20shellcode.xml](https://github.com/3gstudent/msbuild-inline-task/blob/master/executes%20x64%20shellcode.xml)

如图，成功执行64位shellcode

[![](https://p1.ssl.qhimg.com/t01da67f5ad0a2560a0.png)](https://p1.ssl.qhimg.com/t01da67f5ad0a2560a0.png)

**<br>**

**5. VisualStudio Persistence**

在《Pay close attention to your download code——Visual Studio trick to run code when building》中介绍过利用VisualStudio的.csproj文件实现的代码执行，同样Inline Tasks也可用到此处，实现代码已上传，地址为：

[https://github.com/3gstudent/msbuild-inline-task/blob/master/executes%20shellcode%20when%20visual%20studio%20is%20afterBuild.csproj](https://github.com/3gstudent/msbuild-inline-task/blob/master/executes%20shellcode%20when%20visual%20studio%20is%20afterBuild.csproj)

修改vs工程中的.csproj文件，添加上述代码，能够实现在vs工程编译过程中执行shellcode，如图

[![](https://p3.ssl.qhimg.com/t0109e0fdb7f6eaac77.png)](https://p3.ssl.qhimg.com/t0109e0fdb7f6eaac77.png)

**<br>**

**0x04 小结**

利用MSBuild实现的代码执行，有如下特点：

1、可绕过应用程序白名单

2、提供一种直接执行shellcode的方法

3、在内存中执行PE文件

4、结合VisualStudio实现的钓鱼和后门

所以建议对系统中的msbuild.exe进行更多的监控和限制。

**注： 文中相关POC代码已上传至github，地址为： **[**https://github.com/3gstudent/msbuild-inline-task**](https://github.com/3gstudent/msbuild-inline-task)
