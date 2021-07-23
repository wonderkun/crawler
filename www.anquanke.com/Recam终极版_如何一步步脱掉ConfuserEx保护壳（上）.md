> 原文链接: https://www.anquanke.com//post/id/89730 


# Recam终极版：如何一步步脱掉ConfuserEx保护壳（上）


                                阅读量   
                                **186248**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Holger Unterbrink and Christopher Marczewski，文章来源：talosintelligence.com
                                <br>原文地址：[http://blog.talosintelligence.com/2017/12/recam-redux-deconfusing-confuserex.html](http://blog.talosintelligence.com/2017/12/recam-redux-deconfusing-confuserex.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01fdbc85904d4086f2.png)](https://p1.ssl.qhimg.com/t01fdbc85904d4086f2.png)



## 传送门

[Recam终极版：如何一步步脱掉ConfuserEx保护壳（下）](https://www.anquanke.com/post/id/90174)

> 在本文中，我们介绍了如何解密经过.NET ConfuserEx保护的恶意软件。我们通过Advanced Malware Protection （AMP，高级恶意软件防护）感知数据发现了处于活跃期的这款恶意软件。恶意软件借助恶意Word文档来传播，最终会在内存中执行来自Recam恶意软件家族的一个嵌入式载荷（Recam是一款信息窃取恶意软件）。虽然这款恶意软件已活跃数年之久，但出于各种原因，有关该软件内部工作机理的分析文章少之又少。因为恶意软件作者花了许多精力来延缓安全人员对样本的分析研究，使用了包括多层数据加密、字符串混淆、分段置零以及数据缓冲区构造器等技术。这款恶意软件使用了自定义的C2二进制协议，协议本身及相关数据（传输之前）都经过严格加密处理。



## 技术细节

在本篇文章的上部分，将着重介绍释放器部分。

### 释放器

恶意文档使用了常见的恶意软件技术（比如嵌入VB代码）来释放.NET可执行程序。在本文中我们不会介绍这些技术，主要关注的是.NET恶意软件释放器（dropper）的去混淆过程。恶意软件作者使用自定义的[ConfuserEx](https://yck1509.github.io/ConfuserEx/)对释放器做了大量混淆处理（ConfuerEx是一款免费的.NET Framework混淆工具）。如果我们直接使用类似dnSpy之类的.NET反编译器来读取这个文件，结果并不理想（图1）：

[![](https://p2.ssl.qhimg.com/t01f320401d14844698.png)](https://p2.ssl.qhimg.com/t01f320401d14844698.png)

图1

网上有一些免费的反混淆工具可以处理经ConfuserEx保护的程序，然而，这些工具难以解析这款恶意软件。使用这些自动化工具处理后，只能解开其中一部分数据并会中断执行流程，程序中重要的部分仍然保持不变。这意味着我们别无选择，只能手动去混淆，没有捷径可走。网上有些文档介绍了如何手动脱掉ConfuserEx的壳，但我们的运气依然不佳，这些文档不适用于这个版本。

首先，我们使用dnSpy来加载这个程序。我们跳转到`&lt;Module&gt;. cctor`，在最后一个方法上设置断点（如图2所示）。然后，在调试器中运行这个样本，可以看到样本会解开第一个DLL（即“ykMTM…”，如下图2所示）。

[![](https://p3.ssl.qhimg.com/t01ba240b5707b0e2b8.png)](https://p3.ssl.qhimg.com/t01ba240b5707b0e2b8.png)

图2

触发断点后，单步跟进这个方法，如图3所示，我们可以看到程序会解开下一阶段载荷（coral）。

[![](https://p1.ssl.qhimg.com/t01547353c61d67c30d.png)](https://p1.ssl.qhimg.com/t01547353c61d67c30d.png)

图3

分析这阶段载荷后，我们可以在113行的`qMayiwZxj`类上设置另一个断点，如图4所示：

[![](https://p5.ssl.qhimg.com/t01ee630dfea5ccd965.png)](https://p5.ssl.qhimg.com/t01ee630dfea5ccd965.png)

图4

这里会释放下一阶段载荷，我们可以看到新解开的stub.exe的汇编代码（图5）：

[![](https://p4.ssl.qhimg.com/t012323a17809daff73.png)](https://p4.ssl.qhimg.com/t012323a17809daff73.png)

图5

如果你之前分析过经过ConfuserEx处理的程序，你会觉得这个画面非常眼熟。事实上，如果你仔细观察，你会发现10082行有一行非常熟悉的代码：`gchandle.free()`。我们可以在这一行上设置断点。在之前版本中，这行语句是解包过程的最后一行语句。

[![](https://p2.ssl.qhimg.com/t0167177aa97a42069d.png)](https://p2.ssl.qhimg.com/t0167177aa97a42069d.png)

图6

如我们所料，这会解开另一个模块：koi，这也是ConfuerEx中已知的一个模块。

[![](https://p5.ssl.qhimg.com/t014c79b23fd36154d6.png)](https://p5.ssl.qhimg.com/t014c79b23fd36154d6.png)

图7

我们离真相已经非常接近，但koi中的类仍然是空的，没有填充任何代码：

[![](https://p4.ssl.qhimg.com/t01c34a3ab5e232368a.png)](https://p4.ssl.qhimg.com/t01c34a3ab5e232368a.png)

图8

我们可以在koi中cctor调用的最后一个方法上设置断点，继续运行样本。

[![](https://p3.ssl.qhimg.com/t01e9c72c0e2f5bdaf9.png)](https://p3.ssl.qhimg.com/t01e9c72c0e2f5bdaf9.png)

图9

非常好，又解开了一个DLL，不幸的是这个DLL并不重要。我们的Main类以及stub（存根类）中的大多数成员仍然为空。单步跟进后，我们再次回到`&lt;module&gt;`。分析这些方法后，我们可以在第92行设置断点，观察下一阶段的解包过程（图10）。

[![](https://p3.ssl.qhimg.com/t01019081d008497b50.png)](https://p3.ssl.qhimg.com/t01019081d008497b50.png)

图10

如果我们观察这些类的stub，就可以看到各种代码。我们可以在`stub.Run()`上设置断点，观察这个恶意软件加载器除了解包过程以外的真正功能。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018ed9dc455d52a4f9.png)

图11

可以看到，恶意软件试图规避某些反病毒软件，从资源区中读取几个配置参数。未解包之前的配置信息如图12所示，恶意软件将配置信息加密后隐藏在资源区中。

[![](https://p0.ssl.qhimg.com/t0142fd114e09182b92.png)](https://p0.ssl.qhimg.com/t0142fd114e09182b92.png)

图12

恶意软件会检查当前运行路径是否与配置信息中的Startup目录相匹配（如`%AppData%mozilla firefoxfirefox`），如果不匹配，则会将自己复制到Startup目录中，然后通过`cmd.exe`来启动。这意味着我们需要停止调试，从`%AppData%mozilla firefoxfirefox`目录中将`firefox.exe`载入dnSpy，然后再次跟进解包过程，直到到达目前位置。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018f3fcdc73a2066f4.png)

图13

现在我们已进入正确的代码分支（即“从Startup目录执行”条件分支）。从这里开始整个流程变得更加有趣。首先恶意软件会先完成本地持久化任务。如下所示，恶意软件会向`%AppFolder%`目录中写入一个`Update.txt`文件，文件内容如下：

```
C:UsersdexAppDataRoamingmozilla firefoxfirefox.exe
exit
```

[![](https://p4.ssl.qhimg.com/t01d29cd8fa907706bd.png)](https://p4.ssl.qhimg.com/t01d29cd8fa907706bd.png)

图14

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0152367b49e36e2baa.png)

图15

随后，恶意软件会在`cmd.exe`中执行`reg add`命令，将该文件添加到自启动表项中，确保主机启动时会执行`firefox.exe`文件。

[![](https://p4.ssl.qhimg.com/t01450b736ddc3106c7.png)](https://p4.ssl.qhimg.com/t01450b736ddc3106c7.png)

图16a

[![](https://p4.ssl.qhimg.com/t0182030c6a39d3a0ee.png)](https://p4.ssl.qhimg.com/t0182030c6a39d3a0ee.png)

图16b

恶意软件会根据配置信息执行其他一些命令，然后从MainFile区加载并解压经过LZMA压缩的一个恶意软件载荷文件（即Recam）。经过实时修复后，恶意软件会加载`RunPEDLL.dll`，尝试将载荷文件注入用户浏览器进程中。如果注入失败（比如浏览器没有运行），则会将文件注入到自身进程中（firefox.exe）。不论哪种情况，恶意软件都会使用`RunPE.Run()`方法来完成这个过程。

[![](https://p1.ssl.qhimg.com/t01e6273f4aab3cf5d2.png)](https://p1.ssl.qhimg.com/t01e6273f4aab3cf5d2.png)

图17

到这里为止，恶意软件释放器的任务已完成，由Recam程序接管攻击流程。



## 恶意载荷

请持续关注，文章下部分将在近期发布。

## ``
