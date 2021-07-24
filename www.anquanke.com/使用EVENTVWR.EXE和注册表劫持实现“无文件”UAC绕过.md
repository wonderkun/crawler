> 原文链接: https://www.anquanke.com//post/id/84411 


# 使用EVENTVWR.EXE和注册表劫持实现“无文件”UAC绕过


                                阅读量   
                                **78974**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：enigma0x3
                                <br>原文地址：[https://enigma0x3.net/2016/08/15/fileless-uac-bypass-using-eventvwr-exe-and-registry-hijacking/](https://enigma0x3.net/2016/08/15/fileless-uac-bypass-using-eventvwr-exe-and-registry-hijacking/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t015f7f55a36a93a46d.png)](https://p0.ssl.qhimg.com/t015f7f55a36a93a46d.png)

在对Windows 10进行深入挖掘并发现了一个非常有趣的绕过用户帐户控制（UAC）的方法之后（详细信息请参阅https://enigma0x3.net/2016/07/22/bypassing-uac-on-windows-10-using-disk-cleanup/）,我决定花更多的时间来调查其他潜在的UAC绕过技术。目前,有一些开源的UAC绕过技术,其中大部分需要特权文件副本，然后使用IFileOperation COM对象或WUSA提取(Windows 7) 在一个受保护的系统位置进行DLL劫持。所有这些技术都需要向磁盘中导入一个文件(例如,将一个DLL导入到磁盘上来执行一个DLL劫持)。你可以在下面这个网址查看这些开源技术https://github.com/hfiref0x/UACME。这篇文章中提到的技术不同于其他开源方法，而是提供了一个有用的新技术,它不依赖于特权文件副本,代码注入,或者在磁盘上放置一个传统的文件(如DLL)。这种技术已经在Windows 7和Windows10上进行了测试,但希望以后能够在所有实施UAC的Windows版本上运行。

跟我在上篇文章中提到过的使用磁盘清理绕过UAC技术一样,探查Windows加载方式的一个普遍的技术是使用进程监视器分析进程执行时的行为。然而继续挖掘，在用ProcMon打开Windows事件日志时,我注意到，作为一个高阶进程，eventvwr.exe执行了一些关于HKEY_CURRENT_USER hive的注册表查询。

很早之前,理解HKEY_CLASSES_ROOT(HKCR)和HKEY_CURRENT_USER(HKCU)注册表项以及它们之间是如何相互作用的就是很重要的。HKCR仅仅是HKLM:SoftwareClasses和HKCU:SoftwareClasses的组合（想要了解什么是HKCR以及为什么HKLM和HKCU要进行合并，请点击下面的链接https://msdn.microsoft.com/enus/library/windows/desktop/ms724475(v=vs.85).aspx）。由于这些hive是合并的,通常可以通过在HKCU:SoftwareClasses中创建一些键来劫持HKCR:中的键。因为在这两个hive之间存在的这种关系,所以任何能够作用到HKCU和HKCR的高阶进程都会显得特别有趣,因为它可以篡改HKCU的值。作为一个普通用户,你将访问键写入了HKCU;如果你可以操作一个高阶进程来影响这些键,那么你就可能会干扰一个高度集成的进程试图执行的行为。 

现在,有些人可能知道,有一些微软签署的二进制文件可以根据它们的manifest进行自动提升（更多关于这些二进制文件和manifest的信息请参阅：https://technet.microsoft.com/en-us/magazine/2009.07.uac.aspx）。通过使用系统工具“sigcheck”,我证实了“eventvwr.exe”使用它的manifest进行了自动提升： 

[![](https://p2.ssl.qhimg.com/t015e987e7f719abc2c.png)](https://p2.ssl.qhimg.com/t015e987e7f719abc2c.png)

深入了解ProcMon输出的时候,我注意到“eventvwr.exe”与HKCUSoftwareClassesmscfileshellopencommand进行了交互,这导致了一个“NAME NOT FOUND”的结果。不久,eventvwr.exe又与HKCRmscfileshellopencommand的键进行了交互。当我查看HKCRmscfileshellopencommand时,我注意到默认值被设置为调用mmc.exe(微软管理控制台程序),这个程序负责加载管理Snap-Ins：

[![](https://p2.ssl.qhimg.com/t0184a87a434a0260c1.png)](https://p2.ssl.qhimg.com/t0184a87a434a0260c1.png)

如前所述, 一个高阶进程调用HKEY_CURRENT_USER (or HKCU)是十分有趣的。这通常意味着一个提升的进程与注册表的位置进行交互，而这个地方一个中阶进程就可以进行篡改。在这种情况下,我观察到“eventvwr.exe”在HKCRmscfileshellopencommand之前查询HKCUSoftwareClassesmscfileshellopencommand。由于HKCU返回值为“NAME NOT FOUND”,所以这个提升进程开始查询HKCR的位置：

[![](https://p2.ssl.qhimg.com/t017ac5fcbf976d93b6.png)](https://p2.ssl.qhimg.com/t017ac5fcbf976d93b6.png)

从输出可以看到, 作为一个高阶进程，“eventvwr.exe”在查询了HKCU和HKCR的注册表hive之后调用了mmc.exe。mmc.exe执行之后,它打开了eventvwr.msc,这是一个微软保存控制台文件,导致事件查看器进行显示。这看起来合乎常理，因为微软管理控制台(mmc.exe)装载的是微软保存控制台文件(.msc)。

根据这些信息,我决定创建一个“eventvwr.exe”所需的注册表结构来成功查询HKCU的位置而不是HKCR的位置。既然位于HKCRmscfileshellopencommand的默认值包含一个可执行文件,我决定只是用powershell.exe来替换这个可执行文件:

[![](https://p1.ssl.qhimg.com/t0165ee5fb7e963a2af.png)](https://p1.ssl.qhimg.com/t0165ee5fb7e963a2af.png)

当“eventvwr.exe”运行的时候,我注意到它成功查询/打开了HKCUSoftwareClassesmscfileshellopencommand：

[![](https://p2.ssl.qhimg.com/t01305a3234ebc73f5f.png)](https://p2.ssl.qhimg.com/t01305a3234ebc73f5f.png)

这一行动有效地用我们的新值“powershell.exe”替代了之前的“mmc.exe”值。随着进程的继续,我观察到它最终调用了“powershell.exe”而不是“mmc.exe”:

[![](https://p1.ssl.qhimg.com/t01168c54be7cdbf1a4.png)](https://p1.ssl.qhimg.com/t01168c54be7cdbf1a4.png)

查看进程管理工具,我能够确认powershell.exe确实在以高阶权限运行：

[![](https://p4.ssl.qhimg.com/t01c1cc6aa235323264.png)](https://p4.ssl.qhimg.com/t01c1cc6aa235323264.png)

由于能够劫持进程的启动,所以简单地执行你希望的任何恶意PowerShell脚本/命令都是可行的。这意味着代码可以在一个高阶进程中执行(绕过UAC)，并且没有向文件系统中导入DLL或任何其它文件。这会显著减少攻击者的风险,因为他们不用把传统的文件导入到文件系统中,而这正是最容易被AV/HIPS检测到的。

为了演示这种攻击, Matt Graeber和我构造了一个PowerShell脚本,在系统上执行的时候,会在当前用户的hive中创建所需的注册表项 (HKCUSoftwareClassesmscfileshellopencommand),设置默认值为任何你想通过command参数传递的值,运行“eventvwr.exe”，然后清理注册表条目。

你可以在下面的链接找到这个脚本:[https://github.com/enigma0x3/Misc-PowerShell-Stuff/blob/master/Invoke-EventVwrBypass.ps1](https://github.com/enigma0x3/Misc-PowerShell-Stuff/blob/master/Invoke-EventVwrBypass.ps1)

在这个脚本中,我们提供了一个示例命令。这个特殊的命令使用PowerShell向“C: UACBypassTest”中写入“Is Elevated: True”。这可以证明这个命令是在一个高阶进程中执行的，因为“Is Elevated”等于“True”，并且输出文本文件被写入的目录中阶进程没有写入权限。

**<br>**

**总结及应对措施**

这种方法不同于其他的开源技术，主要是有以下几个非常方便的好处：

1.这种技术不需要导入传统的文件到文件系统。目前大多数开源UAC绕过技术需要引入一个文件(通常是一个DLL)到文件系统，这样做会增加攻击者被抓的风险。由于这种技术不需要导入传统的文件,攻击者的风险得到了显著减轻；

2.这种方法不需要任何进程注入,这意味着攻击不会被监控这种行为的安全解决方案标记；

3.不需要特权文件副本。大多数UAC绕过技术需要某种特权文件的副本来将一个恶意DLL复制到一个安全的位置，从而进行DLL劫持。而这种技术可以替代“eventvwr.exe”运行时启动加载所需的管理单元,可以简单地使用现有的、受信任的微软二进制文件在内存中执行代码。

**应对措施：**

**1.将UAC的级别设置为“总是通知”；**

[![](https://p1.ssl.qhimg.com/t01e0140f7d340ea506.png)](https://p1.ssl.qhimg.com/t01e0140f7d340ea506.png)

2.从本地管理员群组中删除当前用户；

3.可以利用这种方法的特征监测这种攻击：查找HKCUSoftwareClasses中的注册表项，或者在HKCUSoftwareClasses中创建新注册表项。
