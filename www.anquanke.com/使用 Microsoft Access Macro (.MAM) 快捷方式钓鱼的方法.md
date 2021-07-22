> 原文链接: https://www.anquanke.com//post/id/150714 


# 使用 Microsoft Access Macro (.MAM) 快捷方式钓鱼的方法


                                阅读量   
                                **104587**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Steve Borosh，文章来源：posts.specterops.io
                                <br>原文地址：[https://posts.specterops.io/phishing-tales-microsoft-access-macro-mam-shortcuts-c0bc3f90ed62](https://posts.specterops.io/phishing-tales-microsoft-access-macro-mam-shortcuts-c0bc3f90ed62)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t017fb70df1dbbe6d06.png)](https://p0.ssl.qhimg.com/t017fb70df1dbbe6d06.png)

## 前言

在此之前，我在[博客](https://medium.com/rvrsh3ll/phishing-for-access-554105b0901e)中提到了创建恶意的.ACCDE Microsoft Access Database文件并将其用作网络钓鱼载体的方法。这篇文章详细介绍了使用ACCDE格式，并介绍Microsoft Access Macro（MAM）快捷方式实现通过网络钓鱼访问。MAM文件基本上是一个直接链接到Microsoft Access Macro的快捷方式。至少从Office 97开始就有了。



## 创建MAM

对于这个练习，我们将创建一个简单的弹出calc.exe的Microsoft Access Database。然而我们可以嵌入任何东西，从简单的宏payload到成熟的[DOTNET2JSCRIPT](https://github.com/tyranid/DotNetToJScript) payload。首先，打开MS Access并创建一个空白数据库，然后应该有这样的东西：

[![](https://p1.ssl.qhimg.com/t0152ff3d633ee29f3e.png)](https://p1.ssl.qhimg.com/t0152ff3d633ee29f3e.png)

现在，定位到Create并选择Module。这将打开Microsoft Visual Basic for Applications编辑器。

在Microsoft Access中，我们的模块将包含我们的代码库，而宏将告诉Access运行VB代码。你很快就会明白我的意思了。

好的，我们需要一些代码。一个简单的“pop calc”就行了。我将把这个问题留给读者，或者参考我以前的博客文章。

[![](https://p5.ssl.qhimg.com/t01b6706f9ef2d9c18f.png)](https://p5.ssl.qhimg.com/t01b6706f9ef2d9c18f.png)

注意我是如何将函数调用添加到代码中的。当我们创建宏时，它将查找函数调用而不是子调用。

现在，保存模块并退出代码编辑器。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015472a0f896ec1eda.png)

保存了模块之后，就可以创建宏来调用模块了。打开“Create”并选择“Macro”。使用下拉框选择“Run Code”并选择你的宏函数。

[![](https://p1.ssl.qhimg.com/t0127446b266cf28e02.png)](https://p1.ssl.qhimg.com/t0127446b266cf28e02.png)

接下来，通过单击Run选项来测试宏，Access将提示你保存宏。如果希望宏在文档打开时自动运行，请务必将其保存为Autoexec。

[![](https://p3.ssl.qhimg.com/t01ceeb4934c931bc28.png)](https://p3.ssl.qhimg.com/t01ceeb4934c931bc28.png)

数据库完成后，我们就可以保存项目了。需要先保存为.accdb格式，以便以后可以修改项目。

[![](https://p5.ssl.qhimg.com/t01d8488d03d414bba0.png)](https://p5.ssl.qhimg.com/t01d8488d03d414bba0.png)

然后，我们将再次保存我们的项目。这一次，选择Make ACCDE 选项。这将创建数据库的“execute only/只执行”版本。

[![](https://p0.ssl.qhimg.com/t01bfc580ab35043cd9.png)](https://p0.ssl.qhimg.com/t01bfc580ab35043cd9.png)

[![](https://p2.ssl.qhimg.com/t015f0f7909221eb9ba.gif)](https://p2.ssl.qhimg.com/t015f0f7909221eb9ba.gif)

如果我们想要的话可以把ACCDE作为附件添加到电子邮件或链接到它，作为我们钓鱼时payload的选项。然而，除了发送文件之外，还有更多的事情要做。我们可以创建MAM快捷方式，这个快捷方式将远程链接到ACCDE文件并在Internet上运行内容。

确保打开ACCDE文件，单击鼠标左键，将宏拖到桌面上。这将创建你可以修改的初始.MAM文件。用你最喜欢的编辑器或记事本打开它，看看我们能修改什么。

[![](https://p3.ssl.qhimg.com/t01e993c3e10121672f.png)](https://p3.ssl.qhimg.com/t01e993c3e10121672f.png)

[![](https://p4.ssl.qhimg.com/t01ecce65fcdf77be74.png)](https://p4.ssl.qhimg.com/t01ecce65fcdf77be74.png)<br>
可以看到，这个快捷方式本身并没有太大的意义。我们主要关心的是更改DatabasePath变量，因为我们将远程托管EXECUTE数据库。有了这个变量，我们有几个选项。我们可以在SMB或Web上托管ACCDE文件。通过SMB承载可能具有双重用途，因为我们可以捕获凭据，并且只要允许445端口不是你的目标网络。在这本文中，我将演示如何在http上做到这一点。让我们远程托管我们的ACCDE文件并修改我们的.MAM文件。



## Phish

在远程主机上，使用你首选的web宿主方法提供ACCDE文件。

[![](https://p3.ssl.qhimg.com/t0163dc95e983ae0988.png)](https://p3.ssl.qhimg.com/t0163dc95e983ae0988.png)

编辑.MAM文件以指向Web服务器上的ACCDE。

[![](https://p5.ssl.qhimg.com/t01455c48cbf6bb9777.png)](https://p5.ssl.qhimg.com/t01455c48cbf6bb9777.png)

现在，我们的任务是交付我们的MAM payload到我们的目标。一些提供程序阻止MAM文件，Outlook在默认情况下会阻止MAM文件，因此，在这个场景中，我们将发送一个钓鱼链接到我们的目标，并将我们的MAM文件简单地托管在我们的Web服务器上，或者可以使用Apache mod_rewrite进行一些奇怪的重定向，如[详述](https://bluescreenofjeff.com/2016-12-23-apache_mod_rewrite_grab_bag/)的那样。

一旦我们的用户点击我们的网络钓鱼链接(在这种情况下使用边缘浏览器)，他们将被提示打开或保存文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01df6df5f39da8d044.png)

接下来，系统会提示他们使用安全警告再次打开该文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010cf2f30ef4945dbb.png)

最后，向目标用户提示最后一个安全警告，并向用户显示远程托管IP地址或域名。这里要注意的关键点是，在此之后，没有显示宏或[受保护的视图警告](https://support.office.com/en-us/article/what-is-protected-view-d6f09ac7-e6b9-4495-8e43-2bbcdbcb6653)，也没有阻止此宏运行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01296c7b470640d164.png)

一旦用户单击“打开”，我们的代码将运行。

[![](https://p3.ssl.qhimg.com/t01d731f3af4eb329a3.gif)](https://p3.ssl.qhimg.com/t01d731f3af4eb329a3.gif)

虽然有几个安全提示，但我们还是进入了我们的目标网络。



## OPSEC

这个payload很好，因为它是一个简单的快捷文件，并且可以远程调用我们的payload。但是，运行后还剩下什么呢？让我们使用promon检查流程和文件系统活动。

[![](https://p0.ssl.qhimg.com/t01176f52a07b51ab88.png)](https://p0.ssl.qhimg.com/t01176f52a07b51ab88.png)

第一个有趣的条目是“CreateFile”调用，它执行上面图片中的命令行。命令行审核要查找的东西是“ShellOpenMacro”字符串。

接下来，我们观察从本地机器保存并执行远程ACCDE文件。虽然我们的payload似乎是远程调用的，但它被下载到了“%APPDATA%LocalMicrosoftWindowsINetCacheContent.MSO95E62AFE.accdePopCalc.accde”。对于进攻性的交战，这个文件应该注意清理。

[![](https://p1.ssl.qhimg.com/t015b3f57ea8d649592.png)](https://p1.ssl.qhimg.com/t015b3f57ea8d649592.png)

[![](https://p0.ssl.qhimg.com/t01d376e988a8e6aa7c.png)](https://p0.ssl.qhimg.com/t01d376e988a8e6aa7c.png)



## 缓解措施

在Microsoft Office 2016中，你可以让GPO阻止从Internet执行宏，或者为每个Office产品设置以下注册表项。

ComputerHKEY_CURRENT_USERSoftwareMicrosoftOffice16.0AccessSecurityblockcontentexecutionfrominternet = 1

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012275bb2de8a8c3cc.png)

如果用户在执行该设置时被钓鱼，他们将被拒绝执行该程序。应该注意的是，即使宏被阻塞，MAM文件仍然伸出手来拉下访问文件。因此，仍然有机会知道你的phish是否被接收和执行，或者通过SMB窃取凭据。

[![](https://p4.ssl.qhimg.com/t01ceed075aa9085a83.png)](https://p4.ssl.qhimg.com/t01ceed075aa9085a83.png)



## 结论

在本文中，我介绍了将Microsoft Access Macro快捷方式武器化以通过HTTP调用payload所需的步骤。虽然这个文件类型通常被Microsoft Outlook阻止，但在Gmail中允许使用，也可以通过HTTP或SMB提供。我还展示了在哪里可以找到工具并启用宏阻塞，以防止这种类型的攻击。

更重要的是，防御者要熟悉各种网络钓鱼的payload和他们留下的工具。我希望这篇文章能帮助人们了解这一特定的攻击向量，以及与之相关的IoC。

审核人：yiwang   编辑：边边
