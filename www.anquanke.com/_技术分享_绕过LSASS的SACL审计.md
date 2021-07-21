> 原文链接: https://www.anquanke.com//post/id/87107 


# 【技术分享】绕过LSASS的SACL审计


                                阅读量   
                                **90164**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：tyranidslair.blogspot.co.uk
                                <br>原文地址：[https://tyranidslair.blogspot.co.uk/2017/10/bypassing-sacl-auditing-on-lsass.html](https://tyranidslair.blogspot.co.uk/2017/10/bypassing-sacl-auditing-on-lsass.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0133c3453c6f224ee3.jpg)](https://p1.ssl.qhimg.com/t0133c3453c6f224ee3.jpg)

译者：[牧野之鹰](http://bobao.360.cn/member/contribute?uid=877906634)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**<br>**

**前言**

**LSASS**：本地安全权威子系统，是Windows平台上一个用户模式进程，它负责本地系统安全策略（比如允许哪些用户登录到本地机器上、密码策略、授予用户和用户组的特权、以及系统安全审计设置）、用户认证，以及发送安全审计消息到事件日志中。著名的**Mimikatz**密码抓取工具就是从LSASS进程的内存中获取明文密码的。

**<br>**

**正文**

Windows NT从第一天开始就支持资源访问审计。任何审计事件最终都会记录到安全事件日志中（**Security event log**）。要启用审计功能，管理员需要在本地或者组安全策略中配置哪些类型的资源的访问需要被审计，包括是否审计成功和失败。每个要审计的资源都需要添加到系统访问控制列表（**SACL**）中，该系统访问控制列表决定了哪些类型的访问将被审计。ACL还可以指定将审计限制在特定组中。

最近一条推特激起了我的兴趣，这条推特指出在Windows 10 中的一个改动——为LSASS进程配置了一个SACL。这条推特中还有一张截图，截自一个描述Windows 10 RTM改动的网页。从中我们可知该SACL的引入是为了检测一些工具的使用，比如Mimikatz，它需要打开LSASS进程。但是对于这个目的，它能不能很好的工作呢？

让我们来分析这个LSASS的SACL，先从审计的角度来看看这样做的意义，然后再谈谈为什么这不是检测Mimikatz或者试图访问LSASS内存的类似程序的一个很好的机制。

我们首先设置一个测试系统，以便我们可以验证SACL是否存在，然后启用审计来检查打开LSASS时是否收到审计事件。 我更新了我的一个Windows 10 1703虚拟机，然后安装了NtObjectManager PowerShell模块。

[![](https://p5.ssl.qhimg.com/t016ee1b9d9b786abb3.png)](https://p5.ssl.qhimg.com/t016ee1b9d9b786abb3.png)

在这里需要注意的几件事情，您必须在打开该进程时请求ACCESS_SYSTEM_SECURITY访问权限，否则您无法访问SACL。 您还必须在访问进程的安全描述符时明确请求SACL。 我们可以将SACL看作是一个SDDL（Security Descriptor Definition Language）字符串，它与来自tweet / Microsoft网页的SDDL字符串相匹配。 但SDDL的表示方法并不能让我们很好的理解SACL ACE（Access Control Entry），所以我会在文中将其扩展。 扩展后的形式表明ACE就是我们所希望的用于审计的ACE，主体用户是Everyone组，对成功和失败事件都启用了审计，并且掩码设置为0x10。

好的，我们来配置这个事件的审计。 我在系统的本地安全策略中启用了对象审计（例如运行gpedit.msc），如下所示：

[![](https://p3.ssl.qhimg.com/t0103590fb36aaadafd.png)](https://p3.ssl.qhimg.com/t0103590fb36aaadafd.png)

您不需要重新启动以更改审计配置，因此只需重新打开LSASS进程，就像我们之前在PowerShell中所做的那样，我们应该可以看到在安全事件日志中生成的审计事件，如下所示：

[![](https://p3.ssl.qhimg.com/t01244c3906bd26770a.png)](https://p3.ssl.qhimg.com/t01244c3906bd26770a.png)

我们可以看到包含目标进程和源进程的事件已经被记录了。那么我们如何绕过这个呢？我们回过头来看一下SACL ACE的意义。内核用来确定是否生成一个基于SACL的审计日志的过程其实和用DACL来进行访问检查的过程没有多大区别。内核尝试找到具有当前令牌组中的主体的ACE，并且掩码表示已授予打开的句柄的一个或多个访问权限。 所以回顾一下SACL ACE，我们可以得出结论，如果当前的令牌具有Everyone组并且句柄被授予访问权限0x10，则会生成审计事件。那么0x10应用到进程上意味着什么呢？我们可以利用powershell中的Get-NtAccessMask来看一下。

[![](https://p3.ssl.qhimg.com/t01bb69359c16594fd6.png)](https://p3.ssl.qhimg.com/t01bb69359c16594fd6.png)

这表明访问进程内存需要你有PROCESS_VM_READ权限，这是有道理的。 如果你想要阻止一个进程抓取LSASS的内容，则你可以让该进程必须获取到了访问权限，然后才能调用ReadProcessMemory()。

绕过的第一个思路是将Everyong 组从你的令牌中移除，然后再打开目标进程，这时候审计规则应该是不匹配的。但是操作起来很不容易，从令牌中移除组的唯一个简单的方法是用CreateRestrictedToken()将其转换为仅拒绝（Deny Only）组。然而，内核为了审计访问检查，将仅拒绝组视为已启用。或者如果你有SeCreateToken特权的话，你可以创建一个没有该组的令牌，但是根据测试，Everyone组是一个特殊的存在，而且不管你的令牌里有哪些组，它依然会进行审计匹配。

那么访问掩码呢？ 如果不请求PROCESS_VM_READ权限，也就是不在OpenProcess()函数中指定该权限，则不会触发审计事件。 当然，我们实际上希望能够拥有访问权限以便进行内存访问，那么我们怎么能解决这个问题呢？ 一种方法是你可以以ACCESS_SYSTEM_SECURITY权限打开进程，然后修改SACL以删除审计条目。 当然，更改SACL会生成一个审计事件，该事件ID和对象访问生成的不一样，如果你没有捕获那些事件，你可能不会注意到它。 但是这些方法都太麻烦了，事实证明，至少存在一种更容易的方法——滥用句柄复制。

正如我在P0博客文章中解释的那样，当使用伪当前进程句柄时，DuplicateHandle系统调用有一个有趣的行为，其返回值为-1。 具体来说，如果你尝试从另一个进程复制伪句柄，那么你就可以获取源进程的完整访问句柄。 因此，为了绕过SACL，我们可以在OpenProcess()函数中指定PROCESS_DUP_HANDLE参数来访问LSASS，复制其伪句柄并获取PROCESS_VM_READ权限访问句柄。 你可能会认为这仍然会记录在审计日志中，但其实不会。 句柄复制并不会触发访问检查，因此审计功能不会运行。 你可以自己尝试一下，看其是否有效。

[![](https://p0.ssl.qhimg.com/t01578c4ad79f83355a.png)](https://p0.ssl.qhimg.com/t01578c4ad79f83355a.png)

当然这只是绕过审计的简单方法。 您可以轻松地将任意代码和线程注入到进程中，也不会触发审计。 这使得审计SACL相当无用，因为恶意代码可以很方便地绕过它。 如以前一样，如果你的计算机上运行了管理员级代码，那么你将会很不幸。

那么从中我们应该注意什么呢？我们不应该依赖配置好的SACL来检测那些尝试访问，利用LSASS内存的恶意代码。SACL太脆弱，要绕过它太简单了。使用像Sysmon那样的工具可能会有更好的效果（尽管我没有试过），或者是启用Credential Guard应该可以从一开始就阻止恶意代码打开LSASS。
