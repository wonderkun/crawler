> 原文链接: https://www.anquanke.com//post/id/86149 


# 【技术分享】如何通过修改注册表绕过AppLocker


                                阅读量   
                                **98817**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：contextis.com
                                <br>原文地址：[https://www.contextis.com//resources/blog/applocker-bypass-registry-key-manipulation/](https://www.contextis.com//resources/blog/applocker-bypass-registry-key-manipulation/)

译文仅供参考，具体内容表达以及含义原文为准

 [![](https://p5.ssl.qhimg.com/t0193e3f81a60ff4580.jpg)](https://p5.ssl.qhimg.com/t0193e3f81a60ff4580.jpg)

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：150RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

 <br>

**一、前言**



AppLocker（应用程序控制策略）已经成为限制Windows主机的事实上的标准。AppLocker是Windows 7及Windows Server 2008 R2开始引入的一项新功能，是软件限制策略（Software Restriction Policies，SRP）的后继者。管理员可以使用AppLocker允许特定用户或用户组运行特定程序，同时也可以拒绝访问其他程序。

在本文中，我们将向读者介绍一种通过修改注册表键值以绕过AppLocker的简单方法。

我们的目标是在默认安装的Windows主机上，利用AppLocker默认规则中信任的任何程序运行任意代码。同时我们不会使用某些常用的可疑程序来实现这一目标，如regsvr32、 rundll32、InstallUtil、regsvsc、regasm、powershell、powershell_ise以及cmd。

**<br>**

**二、环境配置**



Windows 10实验主机上的AppLocker规则如下所示：

[![](https://p1.ssl.qhimg.com/t01fab478461976e190.png)](https://p1.ssl.qhimg.com/t01fab478461976e190.png)

细心的读者可能会注意到，我们可以使用几种方法绕过上述规则。比如，某人可以在“ftp.exe”程序中，在任意命令前加上“!”符号，就可以执行任意命令，也可以将任何受限程序拷贝到“C:Windows”目录中的任何一个可写目录（如“C:WindowsTask”，“授权用户（Authenticated Users）”组的成员默认情况下都可以写这些目录）完成执行目的。这些AppLocker规则并不意味着系统对攻击者来说是坚不可摧的，其目的在于确保攻击者不能使用规则所禁止应用程序来绕过AppLocker。

此外，虽然上述策略是基于路径条件的规则，但本文描述的方法也能绕过基于程序发布者（Publisher）以及文件哈希（File Hash）的AppLocker限制策略。

**<br>**

**三、技术细节**



这项技术最开始的出发点是基于CPL的绕过思路。CPL本质上就是.dll文件，这些文件的导出函数为CPIApplet回调函数。控制面板通过CPL将所有选项在同一个位置呈现给用户。

我创建了一个dll文件，将其扩展名改为.cpl，双击该文件。这种方式与在命令行中运行“control.exe &lt;path_to_cpl&gt;”的效果一致，最终会执行MainDLL函数中的代码。不幸的是，在我们的实验环境中，这样做会导致rundll32弹出AppLocker错误窗口：

[![](https://p5.ssl.qhimg.com/t012a573f36b678f1c7.png)](https://p5.ssl.qhimg.com/t012a573f36b678f1c7.png)

然而，使用rundll32运行控制面板自带的CPL却是可行的。这样我们就会有两个疑问：

1、控制面板如何加载默认的CPL？

2、控制面板从何处获取CPL列表？

第一个问题跟我们最终的目标关系不大，因为我们知道，在此时此刻，控制面板并没有使用rundll32或者其他黑名单程序来加载默认的CPL。如果你想进一步了解这个问题，你可以在shell32.dll中找到COpenControlPanel COM对象(06622D85-6856-4460-8DE1-A81921B41C4B)的函数：

[![](https://p2.ssl.qhimg.com/t01b7e1fee90db180b2.png)](https://p2.ssl.qhimg.com/t01b7e1fee90db180b2.png)

有趣的是，观察control.exe程序的字符串，我们发现某些CPL（比如joy.cpl）仍然是通过rundll32启动的。为了证实这一点，我们可以在控制面板中，点击“设置USB游戏控制器（Set up USB game controllers）”，此时会再次弹出rundll32的AppLocker错误窗口。

接着看下一个问题，控制面板从何处获取CPL列表？通过Procmon我们可以快速找到问题的答案：

[![](https://p2.ssl.qhimg.com/t0142e715cd2f18277f.png)](https://p2.ssl.qhimg.com/t0142e715cd2f18277f.png)

注册表中的“HKLMSoftwareMicrosoftWindowsCurrentVersionControl PanelCPLs”包含一个CPL列表，这些CPL会在控制面板启动时加载：

[![](https://p4.ssl.qhimg.com/t0164d09a48f58cc55a.png)](https://p4.ssl.qhimg.com/t0164d09a48f58cc55a.png)

我们发现系统也会检查HKCU中相同的路径！默认情况下，每个用户对他们自己的hive文件都具有写权限。MSDN有一篇非常有趣的[文章](https://msdn.microsoft.com/en-us/library/windows/desktop/hh127454%28v=vs.85%29.aspx?f=255&amp;MSPPError=-2147217396)，其中介绍了如何注册dll控制面板选项。我们只关心如何加载我们自己的CPL，因此文章介绍的第一个步骤就能满足我们需求。

我们可以使用多种方法，来修改我们自己的注册表：

**1、使用“reg”命令：**

[![](https://p0.ssl.qhimg.com/t01a12c6b2f55afc9c5.png)](https://p0.ssl.qhimg.com/t01a12c6b2f55afc9c5.png)

**2、使用“regedit”或者“regedt32”程序：**

[![](https://p3.ssl.qhimg.com/t015cd857e6f35cd030.png)](https://p3.ssl.qhimg.com/t015cd857e6f35cd030.png)

**3、使用VBScript脚本：**

[![](https://p2.ssl.qhimg.com/t0166e3a947cb92ef36.png)](https://p2.ssl.qhimg.com/t0166e3a947cb92ef36.png)

**4、使用Jscript脚本：**

[![](https://p3.ssl.qhimg.com/t01ea7f4f4cbd1d4bab.png)](https://p3.ssl.qhimg.com/t01ea7f4f4cbd1d4bab.png)

“reg“和”regedit“都是微软签名的程序，都位于可信的目录中，因此默认情况下不会被AppLocker拦截：

[![](https://p0.ssl.qhimg.com/t013dabdc218dfa540d.png)](https://p0.ssl.qhimg.com/t013dabdc218dfa540d.png)

如果这两个程序被组策略所阻止，那么JScript以及VBScript应该也能奏效。

此外我们还可以通过各种方法启动控制面板：

1、运行C:windowssystem32control.exe

2、使用%APPDATA%MicrosoftWindowsStart MenuProgramsSystem ToolsControl Panel.lnk快捷方式

3、直接使用CLSID：    

```
shell:::`{`5399E694-6CE5-4D6C-8FCE-1D8870FDCBA0`}`
shell:::`{`26EE0668-A00A-44D7-9371-BEB064C98683`}`
shell:::`{`ED7BA470-8E54-465E-825C-99712043E01C`}`
```

4、使用映射文件夹（Junction Folder）：

My Control Panel.`{`ED7BA470-8E54-465E-825C-99712043E01C`}`

因此，绕过AppLocker并不难。首先，我们可以创建一个启动命令提示符的DLL文件，当然使用其他载荷也可以，为了演示方便，我们还是使用这种简单示例。将DLL拷贝到某个可写的目录中，比如桌面或者临时文件夹中，根据需要将其重命名为CPL文件，然后使用前文描述的方法将这个CPL的路径写入HKCU注册表中，使用前面提到的任何一种方法启动控制面板。这样控制面板就会加载这个DLL文件，最终弹出一个命令提示符：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016bb09cc7634492b4.png)

**<br>**

**四、总结**



本文介绍的方法可能不是绕过AppLocker的最简单或者最直接的方法，然而它的确提出了另一种可行的攻击方法，攻击者可以利用该方法在受限的计算机上运行任意代码。

如果不考虑性能影响，我们可以在AppLocker属性窗口的“Advanced“选项卡中，启用”DLL Rule Collection“选项避免这种攻击方式：

[![](https://p2.ssl.qhimg.com/t016880d5da5bcc1138.png)](https://p2.ssl.qhimg.com/t016880d5da5bcc1138.png)


