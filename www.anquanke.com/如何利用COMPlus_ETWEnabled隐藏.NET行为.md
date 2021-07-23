> 原文链接: https://www.anquanke.com//post/id/207843 


# 如何利用COMPlus_ETWEnabled隐藏.NET行为


                                阅读量   
                                **132636**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者xpnsec，文章来源：blog.xpnsec.com
                                <br>原文地址：[https://blog.xpnsec.com/hiding-your-dotnet-complus-etwenabled/](https://blog.xpnsec.com/hiding-your-dotnet-complus-etwenabled/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0185c22878ab63b5f3.jpg)](https://p2.ssl.qhimg.com/t0185c22878ab63b5f3.jpg)



## 0x00 前言

之前一段时间，我想澄清防御方如何检测内存中加载的Assembly（程序集），并在3月份发表了一篇[文章](http://blog.xpnsec.com/hiding-your-dotnet-etw/)（[译文](https://www.anquanke.com/post/id/201222)），介绍了禁用ETW的一些思路。随后有多个研究人员（包括[Cneeliz](https://github.com/outflanknl/TamperETW)、[BatSec](https://blog.dylan.codes/evading-sysmon-and-windows-event-logging/)以及[modexp](https://modexp.wordpress.com/2020/04/08/red-teams-etw/)）也提供了一些巧妙的、改进版的方法，可以绕过这类检测机制。这些方法都需要篡改ETW子系统，比如拦截并控制对某些函数的调用行为（如用户模式下的`EtwEventWrite`函数或者`NtTraceEvent`内核函数），或者解析并控制ETW注册表来避免代码patch行为。

然而其实我们还有一种[办法](https://twitter.com/_xpn_/status/1268712093928378368)能够禁用针对.NET的ETW：在环境变量中设置`COMPlus_ETWEnabled=0`。

[![](https://p0.ssl.qhimg.com/t0168af5d03b11e9da7.png)](https://p0.ssl.qhimg.com/t0168af5d03b11e9da7.png)

公布这种方法后，有许多人向我咨询，主要想了解我如何发现这个选项、以及该选项的工作原理。因此在本文中，我想与大家分享关于这方面的一些细节。

在深入分析之前，我们需要澄清一点：ETW本不应该被当成一种安全控制解决方案。达成这个共识后，我们更容易理解本文阐述的一些信息。ETW的主要功能是作为一款调试工具，但随着攻击者不断改进payload执行技术，有些防御方开始利用ETW的功能来获取关于某些事件的信息（如.NET Assembly的加载行为）。在ETW的原始设计场景中，我们发现的`COMPlus_ETWEnabled`有点类似一个安全审核开关，而实际上这只是关闭某些调试功能的一种简单方法。



## 0x01 前缀为COMPlus_的选项

以`COMPlus_`前缀的选项为开发者提供了许多可配置项，开发者可以在运行时进行配置，对CLR造成不同程度的影响，包括：加载替代性JIT、调整性能、转储某个方法的IL等。这些选项可以通过环境变量或者注册表键值来设置，并且其中很多选项没有公开文档。如果想了解每个选项的具体功能，我们可以参考CoreCLR源中的[lrconfigvalues.h](https://github.com/dotnet/coreclr/blob/master/src/inc/clrconfigvalues.h)文件。

如果大家快速分析该文件，会发现其中并不存在`COMPlus_ETWEnabled`，事实上早在2019年5月31日的某次[commit](https://github.com/dotnet/coreclr/commit/b8d5b7b760f64d39e00554189ea0e5c66ed6bd62)中，CoreCLR就已经删除了该选项。

与许多未公开的功能一样，这些选项可以为攻击者提供比较有趣的一些功能。需要注意的是，这些选项名不一定以`COMPlus_`作为前缀，比如2007年公开的一篇[文章](https://seclists.org/fulldisclosure/2017/Jul/11)中就使用了名为`COR_PROFILER`的一个选项，通过`MMC.exe`实现UAC绕过。

现在我们已经基本了解了这些选项的存在意义以及具体列表，下面继续分析`COMPlus_ETWEnabled`的发现过程。



## 0x02 寻找COMPlus_ETWEnabled

尽管CoreCLR源中包含大量设置，但许多设置并不适用于我们较为熟悉的标准.NET Framework。

为了检测哪些`COMPlus_`适用于.NET Framework，我们可以简化思路，在`clr.dll`中寻找这些前缀的蛛丝马迹，比如`clrconfigvalues.h`中列出的`COMPlus_AltJit`选项。

我们可以删除前缀，在IDA中简单搜索字符串，可以发现`clr.dll`中可能引用到了`AltJit`，如下图所示：

[![](https://p0.ssl.qhimg.com/t01f1768c81f7b3bcce.png)](https://p0.ssl.qhimg.com/t01f1768c81f7b3bcce.png)

跟踪引用位置，我们可以找到一个方法`CLRConfig::GetConfigValue`，该方法以选项名为参数，获取具体值：

[![](https://p1.ssl.qhimg.com/t01540598e57c6a6744.png)](https://p1.ssl.qhimg.com/t01540598e57c6a6744.png)

以这个信息为索引，搜索重载方法，我们可以找到其他一些方法，这些方法也可以在运行时访问类似的配置选项：

[![](https://p3.ssl.qhimg.com/t01840d28225761ace9.png)](https://p3.ssl.qhimg.com/t01840d28225761ace9.png)

由于微软为CLR贴心提供了匹配的PDB文件，我们可以逐一分析这些方法，查看Xref，寻找哪些引用是潜在的目标，比如：

[![](https://p4.ssl.qhimg.com/t012d582baf0ca3125f.png)](https://p4.ssl.qhimg.com/t012d582baf0ca3125f.png)

最后我们可以跟踪该引用，查看传递给`CLRConfig::GetConfigValue`的参数，从而发现最终使用的选项：

[![](https://p4.ssl.qhimg.com/t01b2acea3e866784b4.png)](https://p4.ssl.qhimg.com/t01b2acea3e866784b4.png)



## 0x03 COMPlus_ETWEnabled的作用

发现.NET Framework中存在该选项后，我们还需澄清为什么该选项能够禁用事件跟踪。我们可以在IDA中观察CFG，很快就能知道禁用ETW的原理：

[![](https://p0.ssl.qhimg.com/t01668feb2edd957224.png)](https://p0.ssl.qhimg.com/t01668feb2edd957224.png)

从上图我们可以找到2个代码路径，具体执行的路径取决于`CLRConfig::GetConfigValue`所返回的`COMPlus_ETWEnabled`值。如果该选项存在并且返回`0`值，那么CLR就会跳过上图中蓝色的ETW注册代码块（`_McGenEventRegister`是`EventRegister` API的简单封装函数）。

通过这些provider的GUID进一步分析，我们可以看到较为熟悉的代码：

[![](https://p3.ssl.qhimg.com/t01d166fa86bec234cd.png)](https://p3.ssl.qhimg.com/t01d166fa86bec234cd.png)

我们在前一篇[文章](http://blog.xpnsec.com/hiding-your-dotnet-etw/)中unhook ETW时也用到了这个GUID（``{`e13c0d23-ccbc-4e12-931b-d9cc2eee27e4`}``），在微软官方[文档](https://docs.microsoft.com/en-us/dotnet/framework/performance/clr-etw-providers)中，这个GUID对应的是CLR ETW provider：

[![](https://p5.ssl.qhimg.com/t0179ac6de87d9d8ed3.png)](https://p5.ssl.qhimg.com/t0179ac6de87d9d8ed3.png)



## 0x04 总结

希望这篇文章能给大家提供关于该选项的一些启发，从本质上来讲，我们可以通过该选项让CLR跳过.NET ETW provider的注册过程，从而隐蔽相关事件。

为了防御这种攻击，大家可以参考[Roberto Rodriguez](https://twitter.com/Cyb3rWard0g)提供的一些[思路](https://twitter.com/Cyb3rWard0g/status/1268925843105030144?s=20)，其中详细介绍了许多可用的检测及缓解措施。
