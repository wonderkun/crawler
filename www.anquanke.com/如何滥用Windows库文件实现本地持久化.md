> 原文链接: https://www.anquanke.com//post/id/161492 


# 如何滥用Windows库文件实现本地持久化


                                阅读量   
                                **181273**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：countercept.com
                                <br>原文地址：[https://www.countercept.com/blog/abusing-windows-library-files-for-persistence/](https://www.countercept.com/blog/abusing-windows-library-files-for-persistence/)

译文仅供参考，具体内容表达以及含义原文为准

![](https://p0.ssl.qhimg.com/t0110522207cee715c9.png)

## 一、前言

想象一个，如果有个攻击者在我们的电脑上释放了一个恶意文件，每当我们访问系统中最喜欢的目录（如`Documents`目录）时就会执行恶意文件，并且我们对此一无所知，这是多么恐怖的一件事。攻击者可以利用鲜为人知的一种持久化技术：Windows库文件（Library File）来完成这个任务。

Windows系统中的库文件可以帮助用户在单个视图中查看多个目录的内容。Windows库可以包含存在本地或者远程存储位置中的[文件及目录](https://docs.microsoft.com/en-us/windows/client-management/windows-libraries)。

对这些文件的恶意使用最早可以追溯到维基解密公布的[Vault 7](https://wikileaks.org/ciav7p1/cms/page_13763381.html)相关材料，该方法与[滥用Junction目录](https://www.countercept.com/our-thinking/hunting-for-junction-folder-persistence/)的方法有许多相似之处。这两种技术检测起来较为困难，因此攻击者可以选择这些方案，即便是最好的检测团队也会面临巨大的挑战。

本文以较短的篇幅介绍了如何滥用库文件实现本地持久化，也介绍了如何针对性寻找这类攻击特征。



## 二、何为库文件

默认情况下，Windows库文件的具体路径为`%APPDATA%\Microsoft\Windows\Libraries`，文件扩展名为`library-ms`。这些文件采用XML格式，遵循公开可用的schema。

举个例子，我们来分析`Documents`库文件（即`Documents.library-ms`），该文件对应的是`Documents`目录。观察该文件，其中最有趣的部分是`SimpleLocation`元素的[URL值](https://docs.microsoft.com/en-us/windows/desktop/search/search-schema-sconn-simplelocation)。这个元素定义了基于文件系统或者协议处理程序的“search connectors”（搜索连接器）的具体位置。

在这个例子中，该库文件中的URL元素使用GUID（global unique identifiers，全局唯一标识符）指向了两个不同的目录，具体的[GUID](https://docs.microsoft.com/en-gb/windows/desktop/shell/knownfolderid)及文档目录如下所示：

|GUID|目录
|------
|`{`FDD39AD0-238F-46AF-ADB4-6C85480369C7`}`|%USERPROFILE%Documents
|`{`ED4824AF-DCE4-45A8-81E2-FC7965083634`}`|%PUBLIC%Documents

![](https://p4.ssl.qhimg.com/t01c50e7866c1527c2b.jpg)

由于使用了这两个位置，因此打开这个库时，用户可以在一个视图中查看两个不同目录的内容。这两个目录各自的内容如下图所示：

![](https://p4.ssl.qhimg.com/t01508297a55bf04f31.jpg)

然而，如果我们以库方式来查看时，这些子元素都会在同一个目录中列出：

![](https://p2.ssl.qhimg.com/t015fba63e65bd6330b.jpg)



## 三、创建恶意库文件

那么我们如何利用这一功能实现本地持久化呢？

最简单的技术是添加另一个URL元素，用来加载恶意的COM对象，这样每当用户访问该目录或者系统呈现该目录时，我们的COM对象就会被执行。

在如下例子中，我们创建了一个COM对象，该对象引用了名为`beacon.dll`的一个载荷。

![](https://p5.ssl.qhimg.com/t0142072eb664385a78.jpg)

然后在库文件中添加一个`searchConnector`，其URL元素引用的是我们创建的`CLSID`。

![](https://p4.ssl.qhimg.com/t01d6c51d38cc2e6022.jpg)

最后，将库文件保存到用户桌面，这样看起来像是一个人畜无害的`Documents`目录。如果用户打开该目录，则会显示正常`Documents`目录的内容。然而在后台我们的COM对象同样会被执行，利用`rundll32.exe`运行我们的载荷，进程的PID值为5392.

![](https://p4.ssl.qhimg.com/t0150c657d65d4643b1.jpg)

![](https://p1.ssl.qhimg.com/t014dbf459742e93bd6.jpg)

有趣的是，`rundll32`看上去似乎没有父进程。这是因为父进程`dllhost.exe`（COM Surrogate进程）会在运行COM对象后退出。在Sysmon中，我们可以看到如下图所示的类似事件，显示`dllhost.exe`为父进程，`rundll32.exe`为子进程。

![](https://p2.ssl.qhimg.com/t013610527fed25da44.jpg)

观察Process Monitor，我们可以看到`dllhost.exe`会查询我们创建的`CLSID`，然后加载我们的`beacon.dll`，最后执行`rundll32.exe`。

![](https://p5.ssl.qhimg.com/t0129abae607ddf1976.jpg)

![](https://p2.ssl.qhimg.com/t01c1e8da2aa0c64ba7.jpg)

![](https://p3.ssl.qhimg.com/t01fcfd862505c2cfae.jpg)

虽然这个过程中使用的这些数据点可作为检测特征，但合法的活动也会用到这种方式，因此很可能出现误报，然而，通过数据点关联我们可以得出更为准确的结果。



## 四、本地持久化

为了实现本地持久化，我们需要系统在启动时能够执行我们的`library-ms`文件，那么怎样才能达到这个目的呢？

除了常见的本地持久化技术以外，还有更为隐蔽的一种方法，那就是利用Windows Explorer，在用户查看包含该文件的目录时就会自动执行该文件。因此用户无需实际点击文件，只需要简单查看某个目录就足以达到同样的效果。比如，我们可以将库文件放在桌面上，这样当系统启动时，Explorer会自动呈现桌面，我们的COM对象就得以执行。

从检测角度来看，在启动时执行和在用户点击时执行的区别在于，启动执行的父进程为`explorer.exe`，因为Explorer是呈现库文件的根本原因。

![](https://p5.ssl.qhimg.com/t013352b125b85a0843.jpg)

![](https://p4.ssl.qhimg.com/t01ad650ca12635818d.jpg)

![](https://p4.ssl.qhimg.com/t01806eef96d78d2af0.jpg)



## 五、寻找library-ms文件

我们可以使用PowerShell来寻找恶意库文件，检查是否存在扩展名为`library-ms`的文件，然后过滤URL标签，获取CLSID值，提取相关的注册表键值以便进一步分析。

![](https://p4.ssl.qhimg.com/t01767a1cd7637d2e8f.jpg)

这种场景只考虑到了URL元素的滥用情况，我们可能需要寻找其他元素，以便发现更多的异常特征。

我们提供了一个脚本，用来检查满足如上条件、位于`%USERPROFILE%`目录中的任意`library-ms`文件，我们可以使用该脚本来检测与该技术有关的注册表键值是否存在异常。

![](https://p4.ssl.qhimg.com/t01559f5bb36709c5d3.jpg)

大家可以访问[Github](https://gist.github.com/countercept/6890be67e09ba3daed38fa7aa6298fdf)下载该脚本。

此外，监控`library-ms`文件的创建操作也非常有用，这是一个非常准确的特征，因为带有这些扩展名的文件很少会被创建。比如我们可以使用类似Sysmon之类的工具来监控这类事件，简单将如下信息添加到Sysmon配置文件的`FileCreate`标签中即可：

![](https://p5.ssl.qhimg.com/t0148c2fa5471766cce.jpg)

当创建`library-ms`文件时，我们可以看到如下文件创建事件：

![](https://p4.ssl.qhimg.com/t0137373c9b01fc9f26.jpg)



## 六、总结

Windows系统中有许多“传统可用的”持久化技术，如注册表、服务、计划任务等等，许多防御方会重点关注这些位置。在本文中，我们介绍了利用`library-ms`文件的一种独特技巧，可以隐藏在正常视图中，通过COM引用来执行恶意代码，给检测和分析过程带来更多的挑战。

蓝队应该重点关注`.library-ms`文件的创建及修改操作，也需要关注COM元素。此外，由`explorer.exe`或者`dllhost.exe`执行的可疑进程也能用来进一步确认恶意活动行为。
