> 原文链接: https://www.anquanke.com//post/id/101681 


# 测试你的DFIR工具： Sysmon事件日志中的安全问题剖析


                                阅读量   
                                **90884**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者@danielhbohannon，文章来源：www.danielbohannon.com
                                <br>原文地址：[http://www.danielbohannon.com/blog-1/2018/3/19/test-your-dfir-tools-sysmon-edition](http://www.danielbohannon.com/blog-1/2018/3/19/test-your-dfir-tools-sysmon-edition)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t013faee6c423c58187.jpg)](https://p4.ssl.qhimg.com/t013faee6c423c58187.jpg)



## 写在前面的话

作为一名站在网络安全防御端的研究人员，我需要不断地对各种安全监测框架进行测试和调整，然后再对重构的框架进行重新测试以确定安全防御思想是否正确。但是对于一名经验丰富的DFIR（数据取证与事件应急响应）从业人员来说，他们需要对类似安全工具所生成的检测结果进行交叉验证，并根据输出结果来进行下一步操作。在过去的九个月时间里，我花了大量的时间去研究新型的混淆技术和规避技术，而且在那一段时间里，我还花了很多时间去验证各种检测工具的检测效率和效果。在这篇文章中，我将跟大家分享我在Sysmon的事件日志系统中发现的一个安全漏洞，这个漏洞会影响相应的命令行参数以及至少两款不同的工具，攻击者还可以利用该漏洞查看目标主机中的Windows事件日志。<br>
首先我要声明的是，从2014年第一代Sysmon版本发布之后，我就开始在我个人的测试实验室搭建中使用Sysmon了，所以我可以算是Sysmon的“脑残粉”了。Sysmon（System Monitor）是微软Sysinternals Suite的其中一个组件，由Mark Russinovich（[@markrussinovich](https://github.com/markrussinovich)）主管开发。Sysmon驱动器会以应用服务的形式进行安装，并保持常驻性。网络安全检测人员可以利用Sysmon来监视和记录系统活动，而Sysmon不仅可以提供有关进程创建，网络链接和文件创建时间更改的详细信息，而且还可以将Windows主机中的事件情况记录在Microsoft-Windows-Sysmon/Operational事件日志中。Sysmon最近一次的更新日期为2018年1月5日，版本号为v7.01，并且支持二十二中不同的事件ID（Event ID），其中包括进程执行事件(EID 1 &amp; 5)、网络连接事件(EID 3)、图像加载事件(EID 7)、命名管道事件(EID 17 &amp; 18)、WMI事件(EID 19, 20 &amp; 21)以及各种注册表事件等等。<br>
在过去几年时间里，网上有很多关于使用Sysmon作为终端威胁分析的数据收集源的技术文章。除此之外，关于Sysmon的开源配置项目（例如[@SwiftOnSecurity](https://github.com/SwiftOnSecurity)的sysmon-config项目- [https://github.com/SwiftOnSecurity/sysmon-config）也越来越多，这样让更多的人开始使用Sysmon来进行数据收集和过滤了。而且微软近期还专门发布了一篇Sysinternals](https://github.com/SwiftOnSecurity/sysmon-config%EF%BC%89%E4%B9%9F%E8%B6%8A%E6%9D%A5%E8%B6%8A%E5%A4%9A%EF%BC%8C%E8%BF%99%E6%A0%B7%E8%AE%A9%E6%9B%B4%E5%A4%9A%E7%9A%84%E4%BA%BA%E5%BC%80%E5%A7%8B%E4%BD%BF%E7%94%A8Sysmon%E6%9D%A5%E8%BF%9B%E8%A1%8C%E6%95%B0%E6%8D%AE%E6%94%B6%E9%9B%86%E5%92%8C%E8%BF%87%E6%BB%A4%E4%BA%86%E3%80%82%E8%80%8C%E4%B8%94%E5%BE%AE%E8%BD%AF%E8%BF%91%E6%9C%9F%E8%BF%98%E4%B8%93%E9%97%A8%E5%8F%91%E5%B8%83%E4%BA%86%E4%B8%80%E7%AF%87Sysinternals) Sysmon可疑活动检测指南：[https://blogs.technet.microsoft.com/motiba/2017/12/07/sysinternals-sysmon-suspicious-activity-guide/，感兴趣的同学可以阅读以了解更多详细信息。](https://blogs.technet.microsoft.com/motiba/2017/12/07/sysinternals-sysmon-suspicious-activity-guide/%EF%BC%8C%E6%84%9F%E5%85%B4%E8%B6%A3%E7%9A%84%E5%90%8C%E5%AD%A6%E5%8F%AF%E4%BB%A5%E9%98%85%E8%AF%BB%E4%BB%A5%E4%BA%86%E8%A7%A3%E6%9B%B4%E5%A4%9A%E8%AF%A6%E7%BB%86%E4%BF%A1%E6%81%AF%E3%80%82)<br>
接下来，我们一起进入今天的主题。



## Sysmon安全分析

我们先看一看下面这个例子，这段代码会在环境变量envVar中设置一条命令，然后在一个子进程中执行这个环境变量中的代码内容：

```
cmd.exe /c "set envVar=echo TESTING&amp;&amp;cmd.exe /c %envVar%"
```

当我们在EventVwr.exe中查看这个Sysmon EID 1事件时，你就会发现其中的CommandLine参数已经被替换掉了，原来的%envVar%外面又多了一层百分号：

[![](https://p4.ssl.qhimg.com/t019bd18ed708cccab5.png)](https://p4.ssl.qhimg.com/t019bd18ed708cccab5.png)<br>
虽然我发现了这个问题，但我当时也没有太在意，直到我在日志中看到了使用随机命名环境变量（尤其是以整形数字开头的变量名称，如下面代码所示，使用1337直接替换掉了环境变量名envVar）的Payload信息时，这个情况才引起了我的注意：

```
cmd.exe /c "set 1337=echo TESTING&amp;&amp;cmd.exe /c %1337%"
```

接下来，我们可以在EventVwr.exe中查看这条命令的运行结果，这确实挺令人惊讶的：

[![](https://p5.ssl.qhimg.com/t0102945de6ed336d96.png)](https://p5.ssl.qhimg.com/t0102945de6ed336d96.png)<br>
这似乎是一个存在于Sysmon EID 1的CommandLine域中的溢出漏洞，因为我们在使用EventVwr.exe查看相关数据时，系统显示的是不正确的数据。<br>
接下来，我就需要使用其他工具来验证这个数据源了，我直接选择了PowerShell以及它的Get-WinEvent脚本来查询这个Sysmon事件。结果证明，它返回的也是同样的错误值。<br>
于是乎，我开始测试cmd.exe /c “echo %1”、cmd.exe /c “echo %2”和cmd.exe /c “echo %3”之类的语句，并看看系统显示的事件信息中是否同样会包含额外的值。实验结果表明，有些时候这些值会出现在其他的事件日志条目中，例如%2 —&gt; ProcessGuid和%3 —&gt; ProcessId等等，但有的时候这些值似乎显示的是一些随机的系统信息。<br>
提醒大家一下，cmd.exe的命令行参数长度限制为8191个字符，于是我就想：Sysmon事件日志中的CommandLine域也会遵循这样的字符长度限制吗？<br>
为了证实我的猜想，我使用cmd.exe的||操作符（跟&amp;&amp;的作用相反，如果操作符前面的命令返回值为FLASE，那么代码将会执行操作符后面的命令）执行了下列测试命令，所以我们可以直接在一条命令的后面接上一堆垃圾文本，而这些文本按理来说是不会得到执行的：

```
cmd.exe /c "echo PUT_EVIL_COMMANDS_HERE||%1"
```

从下面的图片中你可以看到EventVwr.exe和PowerShell的Get-WinEvent脚本所生成的不正确的CommandLine值：

[![](https://p0.ssl.qhimg.com/t016c4c05825d0b8384.png)](https://p0.ssl.qhimg.com/t016c4c05825d0b8384.png)[![](https://p0.ssl.qhimg.com/t01e885d9499bbbf0f0.png)](https://p0.ssl.qhimg.com/t01e885d9499bbbf0f0.png)<br>
所以说，“%1”（2个字符）这个由用户控制的输入值将会在事件日志中生成“Incorrect function.”（19个字符）错误信息。那么运行55个”%1”实例：

```
cmd.exe /c "echo PUT_EVIL_COMMANDS_HERE||%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1%1"
```

将会生成如下图所示的输出结果：

[![](https://p1.ssl.qhimg.com/t0180af4cd5ad2113c6.png)](https://p1.ssl.qhimg.com/t0180af4cd5ad2113c6.png)<br>
如果再加到50-85个”%1”实例的话，你将会从EventVwr.exe中的每一个Sysmon EID 1事件中看到一堆乱码，有的时候甚至还会显示其他事件日志源的完整日志信息（类似PowerShell EID 800事件）：

[![](https://p3.ssl.qhimg.com/t0120c831e55c7fc2be.png)](https://p3.ssl.qhimg.com/t0120c831e55c7fc2be.png)<br>
在使用PowerShell的Get-WinEvent脚本查询这些事件时，我们得到了如下所示的事件错误信息：

[![](https://p5.ssl.qhimg.com/t01d5cfac22c271dac6.png)](https://p5.ssl.qhimg.com/t01d5cfac22c271dac6.png)<br>
我们所发现的漏洞可以在Windows 7到Windows 10的所有版本系统（以及PowerShell v2到v5）中成功复现。



## 可能的解决方案

但是，在接下来的验证测试过程中，我又发现了其他的工具可以对.evt/.evtx解析并正确显示出百分号+整形填充值。比如说，微软的Log Parser以及FireEye的Redline取证分析工具（这两款工具都是免费的！）都不会被Sysmon中CommandLine域的溢出问题所影响，并且能够显示出”%1”和”%1337”等字符的正确值。<br>
那么重点是什么？很好，在这个漏洞的帮助下，如果网络管理员使用的是类似EventVwr.exe 或PowerShell的Get-WinEvent脚本来查询事件日志信息的话，攻击者就可以通过在命令中填充足够多的百分号+整形字符串，然后有效地在Sysmon EID 1中隐藏恶意进程执行事件了。<br>
如果你是一名网络安全管理员的话，并且喜欢使用EventVwr.exe 或PowerShell的Get-WinEvent脚本来查询Sysmon EID 1事件，那么在系统出现异常时，你可能需要使用一款不受该漏洞影响的工具来处理这些异常事件了（友情提示：在PowerShell攻击场景下，try/catch语句也许是你的最佳选择）。当然了，你也可以通过官方支持的安全事件日志EID 4688来获取并分析进程命令行参数。<br>
除此之外，建议大家对自己手头上现有的工具进行测试，以确保自己的工具没有受到这个漏洞的影响。



## 总结

如果你现在问我：“你仍然觉得Sysmon是一款非常优秀的工具吗？“我会毫不犹豫地点头！但如果你要问我：”我仍然会把Sysmon当作唯一的进程执行事件源吗？“我肯定不会，因为我可能会使用安全EID 4688或其他官方所支持的机制来实时捕获命令行参数。但是，如果我必须要使用Sysmon EID 1的话（直到这个漏洞被成功修复），我可能会选择使用其他的一些不受该漏洞影响的工具来解析Sysmon中包含在百分号内的字符，这样就可以确保我们所编写的检测规则不会被这个溢出漏洞所影响。<br>
作为一名负责任的防御端研究人员，我们需要不断地进行测试、调整、验证和再验证，然后不断地打破我们原有的假设，这样才能不断地优化我们的安全检测机制，并更好地利用手上的工具来实现我们的目标。
