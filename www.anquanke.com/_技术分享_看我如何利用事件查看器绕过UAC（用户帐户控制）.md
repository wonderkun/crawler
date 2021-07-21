> 原文链接: https://www.anquanke.com//post/id/86006 


# 【技术分享】看我如何利用事件查看器绕过UAC（用户帐户控制）


                                阅读量   
                                **124726**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pentestlab.blog
                                <br>原文地址：[https://pentestlab.blog/2017/05/02/uac-bypass-event-viewer/](https://pentestlab.blog/2017/05/02/uac-bypass-event-viewer/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01731aea16ecbbbdf7.png)](https://p0.ssl.qhimg.com/t01731aea16ecbbbdf7.png)

****

翻译：[**WisFree**](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**写在前面的话**

用户账户控制（UAC）是微软开发出的一套安全控制机制，其目的是为了限制未经授权的应用程序以管理员等级的权限执行，但是当管理员提供了密码并允许该程序执行的话，那么这个非特权应用仍然能够以管理员权限运行。这也就意味着，由于用户账户控制机制的存在，渗透测试人员就可以通过Meterpreter来阻止这种提权方法。

下图即为UAC阻止应用程序提权的演示样例：

[![](https://p0.ssl.qhimg.com/t01b07f9409bbc78975.png)](https://p0.ssl.qhimg.com/t01b07f9409bbc78975.png)

**Matt Nelson在其发布的技术博客中解释称，通过劫持注册表键，我们是有可能利用类似Event Viewer（事件查看器）这样的原生Windows服务来绕过用户账户控制（UAC）的。**首先，Event Viewer（事件查看器）的进程（eventvwr.exe）是以高级完整权限运行的；其次，Event Viewer（事件查看器）是Microsoft Management Console（微软管理控制台）通过注册表进行加载的，因此我们的这个假设完全是可以实现的。

<br>

**手动实现**

在新版本的Windows（包括Vista及其之后版本）平台中，进程是以三种不同的权限等级运行的。系统可以通过这三个不同的等级来确定进程最终以哪一种权限来运行：

-高级：管理员权限

-中级：标准用户权限

-低级：受限制权限

我们可以根据Process Explorer（进程查看器）来确定一个进程所分配到的权限等级。当事件查看器出于运行过程中时，我们可以通过下面这两个因素来检查Windows进程的权限：

1. 系统通过微软管理控制台（mmc.exe）加载事件查看器；

2. 事件查看器以高级完整权限运行；

从下图中可以看到，事件查看器进程是以高级权限运行的：

[![](https://p4.ssl.qhimg.com/t01fef79b40d3628950.png)](https://p4.ssl.qhimg.com/t01fef79b40d3628950.png)

这里需要注意的是，当eventvwr.exe被执行之后，它会尝试在下面这两个注册表地址中搜索mmc.exe：

```
-HKCUSoftwareClassesmscfileshellopencommand
-HKCRmscfileshellopencommand
```

由于第一个注册表地址并不存在，因此mmc.exe会以第二个注册表地址运行，随后该地址便会加载文件eventvwr.msc并将相关信息显示给用户。

下图即为MMC以及事件查看器的相关信息：

[![](https://p2.ssl.qhimg.com/t01d480a372278c5b1e.png)](https://p2.ssl.qhimg.com/t01d480a372278c5b1e.png)

这样一来，攻击者就有可能创建一个压根不存在的注册表地址来以高级权限运行某个进程了，而这样就可以允许攻击者绕过目标系统的用户账户控制（UAC）。

下图显示的是攻击者通过事件查看器来提升命令控制台（CMD）权限的操作界面：

[![](https://p4.ssl.qhimg.com/t0152355b9151d49427.png)](https://p4.ssl.qhimg.com/t0152355b9151d49427.png)

当eventvwr.exe得到执行之后，它将会直接打开命令控制台窗口，而且在整个过程中系统既不会弹出用户账户控制窗口，也不会请求高级权限。如下图所示：

[![](https://p3.ssl.qhimg.com/t01678fdc4b8cc8a435.png)](https://p3.ssl.qhimg.com/t01678fdc4b8cc8a435.png)

这项攻击技术的隐蔽性非常高，因为整个过程根本无需触及硬盘，而且也不需要进行任何的进程注入，这样就可以防止被那些基于进程行为监控的反病毒产品或安全解决方案所检测到。

<br>

**自动化实现**

需要注意的是，我们还可以通过一个不可检测的恶意Payload来代替之前所弹出的命令控制台窗口，这样不仅可以允许我们通过Meterpreter会话来实现自动化提权，而且还可以执行很多其他的系统级指令。我们可以在注册表中加载自定义Payload：

[![](https://p2.ssl.qhimg.com/t013a6ddfc4ec86909c.png)](https://p2.ssl.qhimg.com/t013a6ddfc4ec86909c.png)

我们可以在进程查看器中看到，进程pentestlab3.exe再一次以高级权限运行了：

[![](https://p2.ssl.qhimg.com/t012761d5066e267607.png)](https://p2.ssl.qhimg.com/t012761d5066e267607.png)

Metasploit的handler模块可以捕获到提权的Meterpreter会话，而此时我们就可以给目标应用进行提权了，因为我们现在已经绕过了目标系统的用户账户控制。

[![](https://p5.ssl.qhimg.com/t01a2645816f9e41675.png)](https://p5.ssl.qhimg.com/t01a2645816f9e41675.png)

<br>

**Metasploit**

除了上面所描述的技术方法之外，我们也可以使用Metasploit提供的模块来实现整个攻击过程的自动化，并自动返回一个高权限的Meterpreter会话。命令如下：

```
exploit/windows/local/bypassuac_eventvwr
```

通过事件查看器绕过用户账户控制（Metasploit版）：

[![](https://p3.ssl.qhimg.com/t0129b5a33727c7f908.png)](https://p3.ssl.qhimg.com/t0129b5a33727c7f908.png)

<br>

**参考资料**

1. [https://enigma0x3.net/2016/08/15/fileless-uac-bypass-using-eventvwr-exe-and-registry-hijacking/](https://enigma0x3.net/2016/08/15/fileless-uac-bypass-using-eventvwr-exe-and-registry-hijacking/)

2. [https://github.com/enigma0x3/Misc-PowerShell-Stuff/blob/master/Invoke-EventVwrBypass.ps1](https://github.com/enigma0x3/Misc-PowerShell-Stuff/blob/master/Invoke-EventVwrBypass.ps1)

3. [https://www.rapid7.com/db/modules/exploit/windows/local/bypassuac_eventvwr](https://www.rapid7.com/db/modules/exploit/windows/local/bypassuac_eventvwr)

4. [https://www.mdsec.co.uk/2016/12/cna-eventvwr-uac-bypass/](https://www.mdsec.co.uk/2016/12/cna-eventvwr-uac-bypass/)

5. [https://github.com/mdsecresearch/Publications/blob/master/tools/redteam/cna/eventvwr.cna](https://github.com/mdsecresearch/Publications/blob/master/tools/redteam/cna/eventvwr.cna)
