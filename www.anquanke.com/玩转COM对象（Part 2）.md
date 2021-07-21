> 原文链接: https://www.anquanke.com//post/id/180185 


# 玩转COM对象（Part 2）


                                阅读量   
                                **200500**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者fireeye，文章来源：fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2019/06/hunting-com-objects-part-two.html](https://www.fireeye.com/blog/threat-research/2019/06/hunting-com-objects-part-two.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01f0899b994dc70747.jpg)](https://p2.ssl.qhimg.com/t01f0899b994dc70747.jpg)



## 0x00 前言

紧跟前一篇文章（[原文](https://www.fireeye.com/blog/threat-research/2019/06/hunting-com-objects.html)，[译文](https://www.anquanke.com/post/id/179927)），本文将进一步研究COM对象搜索方法，通过COM对象公开的属性以及子属性来寻找比较有趣的COM对象方法。



## 0x01 什么是COM对象

根据微软的[描述](https://docs.microsoft.com/en-us/windows/desktop/com/the-component-object-model)，“微软组件对象模型（Component Object Model，COM）是平台无关、分布式、面向对象的一种系统，可以用来创建可交互的二进制软件组件”。COM是微软OLE（复合文档）、ActiveX（互联网支持组件）以及其他组件的技术基础。

COM对象服务基本上都可以适用于基于任何语言的许多进程，甚至可以远程使用。我们通常会通过`CLISID`（GUID标识符）或者`ProgID`（程序标识符）来获取COM对象。这些COM对象在Windows注册表中发布，可以轻松提取。



## 0x02 COM对象枚举

FireEye对Windows 10、Windows 7以及微软Office中的COM对象进行了研究。在前一篇文章中，我们介绍了如何[枚举](https://www.fireeye.com/blog/threat-research/2019/06/hunting-com-objects.html)系统上的所有COM对象、实例化这些对象并搜索其中有趣的方法及属性。然而，我们对这些COM对象的研究还不够深入，这些对象还可能会返回无法直接创建的其他对象。

与前一篇文章相比，本文新增了用来搜索COM对象的递归方法，这些对象只能通过被枚举的COM对象的方法及属性来定位。之前我们介绍的搜索方法会搜索每个对象直接公开的方法，并没有递归搜索属性，这些属性可能也是具备有趣方法的COM对象。对搜索方法进行改进后，我们能发现用于代码执行的新的COM对象，也能找到新方法来调用支持代码执行的COM对象方法。



## 0x03 递归搜索COM对象

现在人们经常利用COM对象子属性中公开的方法来执行代码，比如`MMC20.Application` COM对象。为了利用该COM对象实现代码执行，我们需要使用`Document.ActiveView`属性返回的`View`对象中的`ExecuteShellCommand`方法（参考Matt Nelson之前的一篇[文章](https://enigma0x3.net/2017/01/23/lateral-movement-via-dcom-round-2/)）。如图1所示，我们只能通过`Document.ActiveView`返回的对象才能发现这个方法，不能直接通过`MMC20.Application` COM对象找到这个方法。

[![](https://p4.ssl.qhimg.com/t01b8e01b244c5dec28.png)](https://p4.ssl.qhimg.com/t01b8e01b244c5dec28.png)

图1. 列出`MMC20.Application` COM对象中的`ExecuteShellCommand`方法

另一个例子是`ShellBrowserWindow` COM对象，这也是Matt Nelson在一篇[文章](https://enigma0x3.net/2017/01/23/lateral-movement-via-dcom-round-2/)中提到的方法。如图2所示，这个COM对象中并没有直接对外公开`ShellExecute`方法。然而`Document.Application`属性会返回[Shell](https://docs.microsoft.com/en-us/windows/desktop/shell/shell)对象的一个实例，该实例会公开[ShellExecute](https://docs.microsoft.com/en-us/windows/desktop/shell/ishelldispatch2-shellexecute)方法。

[![](https://p2.ssl.qhimg.com/t0177d09765e0099cbc.png)](https://p2.ssl.qhimg.com/t0177d09765e0099cbc.png)

根据前面这两个示例，我们可知在分析COM对象时，不要单单只看对象直接对外公开的方法，还需要递归查找作为COM对象属性的、同时又对外公开我们感兴趣方法的那些对象。这个例子也告诉我们，简单静态分析COM对象的Type Library对我们来说可能还远远不够。只有动态枚举通用型`IDispatch`对象才能访问到相关函数。这种递归方法可以用来查找能够用于代码执行的新COM对象，也可以作为常见COM对象的另一种利用方法。

这种递归方法能够以不同的方式来调用已知的COM对象方法，比如前面提到过的`ShellBrowserWindow` COM对象中的`ShellExecute`方法。之前大家会使用`Document.Application`属性来调用这个方法。利用这种递归COM对象查找方法，我们其实也可以在`Document.Application.Parent`属性返回的对象上调用`ShellExecute`方法，如图3所示。这种方法可能在某些场景中能够实现较好的规避效果。

[![](https://p4.ssl.qhimg.com/t01a2e53eb8efd8f6d5.png)](https://p4.ssl.qhimg.com/t01a2e53eb8efd8f6d5.png)

图3. 利用`ShellBrowserWindow` COM对象调用`ShellExecute`的另一种方法



## 0x04 命令执行

利用这种递归COM对象发现方法，FireEye发现了一个COM对象，其`ProgID`为`Excel.ChartApplication`，这个COM对象可以通过[DDEInitiate](https://docs.microsoft.com/en-us/office/vba/api/excel.application.ddeinitiate)方法来实现代码执行。滥用`Excel.Application` COM对象来启动可执行程序并不是一种新颖技术，大家可以参考Cybereason之前发表过的[文章](https://www.cybereason.com/blog/leveraging-excel-dde-for-lateral-movement-via-dcom)。`Excel.ChartApplication` COM对象中存在多个属性，这些属性会返回能够用来执行`DDEInitiate`方法的一些对象，如图4所示。虽然这个COM对象直接对外公开`DDEInitiate`方法，但我们最开始之所以能找到这个方法，还是因为想澄清通过该对象可访问的其他对象对外公开了哪些方法。

[![](https://p0.ssl.qhimg.com/t016646d7e52d808d25.png)](https://p0.ssl.qhimg.com/t016646d7e52d808d25.png)

图4. 使用`Excel.ChartApplication` COM对象调用`DDEInitiate`的不同方法

如图5所示，这个对象同样可以被实例化，远程用于Office 2013，但对于Office 2016，这个COM对象只能在本地实例化。当我们尝试对Office 2016远程实例化这个COM对象时，就会看到一个错误代码，提示COM对象类并没有注册远程实例化应用场景。

[![](https://p3.ssl.qhimg.com/t0115e2803a725d2094.png)](https://p3.ssl.qhimg.com/t0115e2803a725d2094.png)

图5. 针对Office 2013远程使用`Excel.ChartApplication`



## 0x05 总结

使用这种COM对象递归搜索方法，我们可以发现能用于代码执行的COM对象，这也是调用已知COM对象方法的新方法。这些COM对象方法可以用来绕过不同的检测机制，也可以用于横向渗透任务中。
