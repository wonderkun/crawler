> 原文链接: https://www.anquanke.com//post/id/156704 


# 微软轻量级系统监控工具sysmon原理与实现完全分析（上篇）


                                阅读量   
                                **516349**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">14</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p4.ssl.qhimg.com/t019bf5494829582e5e.jpg)](https://p4.ssl.qhimg.com/t019bf5494829582e5e.jpg)**

作者：浪子_三少

Sysmon是微软的一款轻量级的系统监控工具，最开始是由Sysinternals开发的，后来Sysinternals被微软收购，现在属于Sysinternals系列工具。它通过系统服务和驱动程序实现记录进程创建、文件访问以及网络信息的记录，并把相关的信息写入并展示在windows的日志事件里。经常有安全人员使用这款工具去记录并分析系统进程的活动来识别恶意或者异常活动。而本文讨论不是如何去使用该工具，而是讲解该软件的原理与实现。

本文对Sysmon分两部分

1.ring3层的exe，

2. Flt的minifilter

下面开始上篇的讲解，ring3实现对网络数据记录以及对驱动返回的数据进行解析，而驱动部分则返回进程相关的信息以及进程访问文件注册表的数据给ring3，我们首选讲解ring3的实现原理。

Sysmon的ring3执行原理
1. 判断当前操作系统是否是64位，如果是就执行64位的sysmon
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016e59c1fed8cf1196.png)

动态获取IsWow64Process的函数地址，然后调用IsWow64Process函数，判断当前是否是wow64，如果是就执行SysmonLunchIsAmd64(),进入SysmonLunchIsAmd64函数

[![](https://p3.ssl.qhimg.com/t0114d6e537c26d18d9.png)](https://p3.ssl.qhimg.com/t0114d6e537c26d18d9.png)

通过GetNativeSystemInfo函数判断当前SystemInfo.wProcessorArchitecture != PROCESSOR_ARCHITECTURE_AMD64的值

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f0ae5d4737f9c5be.png)

如果是PROCESSOR_ARCHITECTURE_AMD64则释放资源节中id = 1001的资源到当前进程的所在目录，这是一个内嵌在资源里的64位版本的sysmon的exe，释放完毕后，就开始执行这个64的Sysmon。下面就是Symon的64位资源图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011ae2a4829dda7f5e.png)

[![](https://p1.ssl.qhimg.com/t01a62899fd86661514.png)](https://p1.ssl.qhimg.com/t01a62899fd86661514.png)

本文还是主要以32位的sysmon来讲解，我们继续往下讲解
1. 参数的检查
[![](https://p5.ssl.qhimg.com/t012e57c1a86312ea62.png)](https://p5.ssl.qhimg.com/t012e57c1a86312ea62.png)

接下来sysmon会对参数进行检查，检查是否config、configuration、h、–nologon、？、help，非这些参数后，然后会接着解析具体的参数，根据参数是否加载规则。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018ee273fde3fd481d.png)

我们看SysmonAnalyzeInitArgv函数具体看看sysmon有哪些参数，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012aa2451f14159b60.png)

g_commandLine里固定存贮所有的sysmon参数，这里大概只列举出一部分，Install、i、Uninstall、Configuration、c、u、Manifest、m、DebugMode、nologo、AcceptEula、ConfigDefault、HashAlgorithms、NetworkConnect、ImageLoad、l、DriverName、ProcessAccess、CheckRevocation、PipeMonitoring等等。

[![](https://p1.ssl.qhimg.com/t014fbe392418463cb1.png)](https://p1.ssl.qhimg.com/t014fbe392418463cb1.png)

如果是相应的参数就继续往下执行相应的动作。

[![](https://p1.ssl.qhimg.com/t0120b2eac55824ac18.png)](https://p1.ssl.qhimg.com/t0120b2eac55824ac18.png)

通过检测参数sha、sha-1、md5、md-5、sha、sha256、imphash、imp-hash计算当前使用何种hash算法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019c935832581b0b1a.png)

Sha：  1算法 、Md5： 2算法、sha：3算法、imphash：4算法

接下来会加载内置在exe 内的Sysmonschema.xml

[![](https://p3.ssl.qhimg.com/t01bc2c1995d1f76260.png)](https://p3.ssl.qhimg.com/t01bc2c1995d1f76260.png)

[![](https://p2.ssl.qhimg.com/t01dfcb29ae78ab0fec.png)](https://p2.ssl.qhimg.com/t01dfcb29ae78ab0fec.png)

Sysmonschema.xml的configuration规定了一些进程参数的说明，而events描述说明一些记录信息事件，比如

```
&lt;event name="SYSMON_CREATE_PROCESS" value="1" level="Informational" template="Process Create" rulename="ProcessCreate" ruledefault="include" version="5"&gt;

      &lt;data name="UtcTime" inType="win:UnicodeString" outType="xs:string" /&gt;

      &lt;data name="ProcessGuid" inType="win:GUID" /&gt;

      &lt;data name="ProcessId" inType="win:UInt32" outType="win:PID" /&gt;

      &lt;data name="Image" inType="win:UnicodeString" outType="xs:string" /&gt;

      &lt;data name="FileVersion" inType="win:UnicodeString" outType="xs:string" /&gt;

      &lt;data name="Description" inType="win:UnicodeString" outType="xs:string" /&gt;

      &lt;data name="Product" inType="win:UnicodeString" outType="xs:string" /&gt;

      &lt;data name="Company" inType="win:UnicodeString" outType="xs:string" /&gt;

      &lt;data name="CommandLine" inType="win:UnicodeString" outType="xs:string" /&gt;

      &lt;data name="CurrentDirectory" inType="win:UnicodeString" outType="xs:string" /&gt;

      &lt;data name="User" inType="win:UnicodeString" outType="xs:string" /&gt;

      &lt;data name="LogonGuid" inType="win:GUID" /&gt;

      &lt;data name="LogonId" inType="win:HexInt64" /&gt;

      &lt;data name="TerminalSessionId" inType="win:UInt32" /&gt;

      &lt;data name="IntegrityLevel" inType="win:UnicodeString" outType="xs:string" /&gt;

      &lt;data name="Hashes" inType="win:UnicodeString" outType="xs:string" /&gt;

      &lt;data name="ParentProcessGuid" inType="win:GUID" /&gt;

      &lt;data name="ParentProcessId" inType="win:UInt32" outType="win:PID" /&gt;

      &lt;data name="ParentImage" inType="win:UnicodeString" outType="xs:string" /&gt;

      &lt;data name="ParentCommandLine" inType="win:UnicodeString" outType="xs:string" /&gt;

&lt;/event&gt;
```

就说明了SYSMON_CREATE_PROCESS创建进程上报信息的一些数据内容及说明。

如果参数是PrintSchema [![](https://p2.ssl.qhimg.com/t01b68368dfe9b022d7.png)](https://p2.ssl.qhimg.com/t01b68368dfe9b022d7.png)

则解析并获取Sysmonschema的version，然后打印Sysmonschema的信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d8d3102671e69b3d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015eb3dbcb7830342e.png)
1. 注册日志记录事件
[![](https://p1.ssl.qhimg.com/t01c14b4d9566706309.png)](https://p1.ssl.qhimg.com/t01c14b4d9566706309.png)

[![](https://p3.ssl.qhimg.com/t01bba82555bf233e26.png)](https://p3.ssl.qhimg.com/t01bba82555bf233e26.png)

Sysmon接着会通过EventRegister()函数注册一个GUID为`{`**5770385F**-C22A-43E0-BF4C-06F5698FFBD9`}`的日志事件。然后sysmon会通过系统的wevtutil.exe的程序去注册该GUID的系统日志trace类。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d23f7186242dc078.jpg)

获取系统是否存在Microsoft-Windows-Sysmon的trace类，如果没有就加载exe资源中“SYSMONMAN”的资源到内存，然后释放写入系统临时目录下的文件名MANXXXX.tmp文件里

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c99d90eb9c9478d6.png)

该文件是定义`{`5770385F-C22A-43E0-BF4C-06F5698FFBD9`}`的Microsoft-Windows-Sysmon的trace事件的provider，用于sysmon的后续数据解析。

[![](https://p2.ssl.qhimg.com/t0162e9315e4a47ce26.jpg)](https://p2.ssl.qhimg.com/t0162e9315e4a47ce26.jpg)

[![](https://p0.ssl.qhimg.com/t01541cd404cdd64a13.jpg)](https://p0.ssl.qhimg.com/t01541cd404cdd64a13.jpg)

最后调用系统的”wevtutil.exe im MANXXXX.tmp”去注册安装事件类

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011891fd21c029fd7c.jpg)
1. 安装minifilter驱动
[![](https://p3.ssl.qhimg.com/t012bf24f9a80dc1750.png)](https://p3.ssl.qhimg.com/t012bf24f9a80dc1750.png)

释放资源文件为1002的到系统目录Tmp/Sysmon.sys，资源1002文件是个pe文件，实际上是sysmon的文件注册表监控驱动。

[![](https://p1.ssl.qhimg.com/t01a338f46b78296350.png)](https://p1.ssl.qhimg.com/t01a338f46b78296350.png)

接下来继续就是安装这个驱动

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fdf4ced3e0ca68be.png)

[![](https://p2.ssl.qhimg.com/t019f8285a1a2d27016.png)](https://p2.ssl.qhimg.com/t019f8285a1a2d27016.png)

Sysmon还会设置minifilter驱动的Altitude值为385201

[![](https://p4.ssl.qhimg.com/t0115d9e973451841a0.png)](https://p4.ssl.qhimg.com/t0115d9e973451841a0.png)

最后开启驱动服务

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01dc8d92d43344415d.png)

往驱动发送IO控制码： 0x8340008（该控制码是给驱动更新配置规则）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017aea96c14e0a749b.png)

以上过程是大致的安装与启动的过程，接下来就是执行Sysmon服务的SysmonServiceMain例程。

[![](https://p0.ssl.qhimg.com/t01563fd590a939b036.png)](https://p0.ssl.qhimg.com/t01563fd590a939b036.png)

[![](https://p2.ssl.qhimg.com/t0178ebcc7f7379dc49.png)](https://p2.ssl.qhimg.com/t0178ebcc7f7379dc49.png)

下面开始执行取数据的工作了。

第一步： 文件进程注册表的事件监控[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0172a064b4e0b76db3.png)

通过发送IO控制码: 0x83400000，打开文件驱动功能，接着sysmon会开启一个线程从驱动获取监控数据，通过发送IO控制码 ：0x83400004，去反复获取

[![](https://p0.ssl.qhimg.com/t013511588c1cf4b520.png)](https://p0.ssl.qhimg.com/t013511588c1cf4b520.png)

每隔500毫秒发送一次获取数据，堆大小0x400000,获取了数据后，则开始解析这raw data，这个raw数据的首四个字节是表示数据类型

```
Typedef struct _Sysmon_Raw_Data

`{`

  ULONG DataType;

`}` Sysmon_Raw_Data;
```

Case 1: 上报进程创建

```
ReportEventWriteEvent((int)&amp;v147, (unsigned __int16 *)&amp;g_CreateProcess, (int)v1, v17);
```

Case 2: 文件时间改变

```
ReportEventWriteEvent((int)&amp;v147, (unsigned __int16 *)&amp;g_CreateFileTime, (int)v1, v30);
```

Case 3：进程关闭

```
ReportEventWriteEvent((int)&amp;v147, (unsigned __int16 *)&amp;g_TerminateProcess, (int)v1, 0);
```

Case 5： 加载镜像

```
ReportEventWriteEvent((int)&amp;v146, &amp; g_ImageLoad, (int)v1, v50);
```

Case 7：创建远程线程

```
ReportEventWriteEvent((int)&amp;v146, (unsigned __int16 *)&amp;g_CreateRemoteThread, (int)v1, 0);
```

Case 8：文件读

```
ReportEventWriteEvent((int)&amp;v146, (unsigned __int16 *)&amp;g_FileRead, (int)v1, 0);
```

Case 9：访问进程

```
ReportEventWriteEvent((int)&amp;v146, (unsigned __int16 *)&amp;g_ProcessAccess, (int)v1, 0);
```

Case 10： 文件创建

```
ReportEventWriteEvent((int)&amp;v146, (unsigned __int16 *)&amp;g_FileCreate, (int)v1, v32);
```

Case 11：文件流事件

```
ReportEventWriteEvent((int)&amp;v146, (unsigned __int16 *)&amp;g_FileStreamCreate, (int)v1, v35);
```

Case 12：注册表相关的事件

[![](https://p4.ssl.qhimg.com/t0165ba4f9cff3283cf.png)](https://p4.ssl.qhimg.com/t0165ba4f9cff3283cf.png)

Case 13：管道类事件

[![](https://p5.ssl.qhimg.com/t01b4e4c7d0bb514362.png)](https://p5.ssl.qhimg.com/t01b4e4c7d0bb514362.png)

第二步：网络链接事件的监控

Sysmon还会创建一个ETW事件去监控网络连接的访问事件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018fe053f00b538019.png)

Net Trace 名：L”SYSMON TRACE”; 或者使用系统的L”NT Kernel Logger”;

方法参考微软官方实例：[https://docs.microsoft.com/en-us/windows/desktop/etw/configuring-and-starting-the-nt-kernel-logger-session](https://docs.microsoft.com/en-us/windows/desktop/etw/configuring-and-starting-the-nt-kernel-logger-session)

[![](https://p2.ssl.qhimg.com/t010329b4a1d8b8c594.png)](https://p2.ssl.qhimg.com/t010329b4a1d8b8c594.png)

事件回调EventCallBack()接受数据

[![](https://p4.ssl.qhimg.com/t015f4248b59ea8f4ed.png)](https://p4.ssl.qhimg.com/t015f4248b59ea8f4ed.png)

在解析数据时使用的是WMI Mof的方法来解析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015552459344d47b61.png)

[![](https://p4.ssl.qhimg.com/t018bb513231109333d.png)](https://p4.ssl.qhimg.com/t018bb513231109333d.png)

可以参考微软的官方例子：

[https://docs.microsoft.com/en-us/windows/desktop/etw/retrieving-event-data-using-mof](https://docs.microsoft.com/en-us/windows/desktop/etw/retrieving-event-data-using-mof)

第三步：接受上报数据写入windows的Application日志

在第二部中我们可以看到通过ReportEventWriteEvent函数上报信息，在ReportEventWriteEvent函数里分两种情况系统API上报

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0139f8c2a823f9e974.png)

通过ReportEvent或者EventWrite 两个其中一个API上报，而上报的事件IDD 类都是前面我们看到的Sysmon自己注册到系统的里&lt;provider name=”Microsoft-Windows-Sysmon” guid=”`{`5770385F-C22A-43E0-BF4C-06F5698FFBD9`}`” symbol=”SYSMON_PROVIDER” resourceFileName=”%filename%” messageFileName=”%filename%”&gt;

&lt;events&gt;的Microsoft-Windows-Sysmon事件代理，这个会生成到windows日志的Application项目下，具体会使用哪个API是根据windows的版本来选择的

[![](https://p5.ssl.qhimg.com/t01edf27918bf366fe3.png)](https://p5.ssl.qhimg.com/t01edf27918bf366fe3.png)

这里可以看到如果操作系统主版本，如果是vista之前的操作系统使用ReportEvent，如果是vista以及以上操作系统则使用EventWrite函数。

Sysmon记录上报了数据源通过注册的WMIEvent的wmi数据持久化过滤事件去过滤不会被记录的事件，我们下面看它如何实现的。

[![](https://p5.ssl.qhimg.com/t01c749708f71f7ca5e.png)](https://p5.ssl.qhimg.com/t01c749708f71f7ca5e.png)

在之前的服务启动入口有一个函数RegisterWmiEvent，该函数就是注册过滤WmiEvent的函数，我们继续往下看

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ebad2a5c2c955f5e.png)

函数开头会创建实例IDD_WebCImv，class Id: IID_IWbemLocatorGUID2

&lt;**0dc12a687h**,**0737**fh,011cfh,088h,04dh,000h,0aah,000h,04bh,02eh,024h&gt;

链接”ROOT\\Subscription”的服务

接着创建Stub插口

[![](https://p2.ssl.qhimg.com/t017d8ca9751e3711d0.png)](https://p2.ssl.qhimg.com/t017d8ca9751e3711d0.png)

g_WMIListenerEvent接口类型是IWbemObjectSink,其定义如下

```
MIDL_INTERFACE("7c857801-7381-11cf-884d-00aa004b2e24")

    IWbemObjectSink : public IUnknown

    `{`

    public:

        virtual HRESULT STDMETHODCALLTYPE Indicate(

            /* [in] */ long lObjectCount,

            /* [size_is][in] */ __RPC__in_ecount_full(lObjectCount) IWbemClassObject **apObjArray) = 0;

        virtual HRESULT STDMETHODCALLTYPE SetStatus(

            /* [in] */ long lFlags,

            /* [in] */ HRESULT hResult,

            /* [unique][in] */ __RPC__in_opt BSTR strParam,

            /* [unique][in] */ __RPC__in_opt IWbemClassObject *pObjParam) = 0;

    `}`;
```

[![](https://p3.ssl.qhimg.com/t010b4bb9b53751dc2e.png)](https://p3.ssl.qhimg.com/t010b4bb9b53751dc2e.png)

然后执行

```
"SELECT * FROM __InstanceOperationEvent WITHIN  5  WHERE TargetInstance ISA '__EventConsumer' OR Tar"

                        "getInstance ISA '__EventFilter' OR TargetInstance ISA '__FilterToConsumerBinding'"

g_WmiSubscriptProxy-&gt;lpVtbl-&gt;ExecNotificationQueryAsync(

           g_WmiSubscriptProxy,

           strQueryLanguage,

           strQuery,

           128,

           0,

           (IWbemObjectSink *)g_pIWebmObjectSink);
```

去设置WMiEvent的过滤事件，操作类型是所有操作InstanceOperationEvent，设置三种事件

EventConsumer’、EventFilter’、FilterToConsumerBinding’，查询时间是5秒一次，这样就注册了。

下面我们看g_WMIListenerEvent结构

[![](https://p5.ssl.qhimg.com/t019468180ebc661d5b.png)](https://p5.ssl.qhimg.com/t019468180ebc661d5b.png)

过滤事件就是在Indicate函数中实现，会通过IWbemClassObject** 数组的形式输入，函数内会枚举数据，如果是要过滤的数据则循环枚举否则中断枚举。

[![](https://p3.ssl.qhimg.com/t01e2dde211b6efa5ad.png)](https://p3.ssl.qhimg.com/t01e2dde211b6efa5ad.png)

至此第一篇对sysmon的ring3的大致原理流程我们分析完毕，通过对它分析，学习它的实现过程，可以自己完成实现一个sysmon（还有驱动部分第二篇讲解），当然也可以绕过sysmon的监控，这就需要读者自己去研究与发现，第二篇我会讲解驱动部分的分析。
