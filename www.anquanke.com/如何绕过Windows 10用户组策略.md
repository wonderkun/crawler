> 原文链接: https://www.anquanke.com//post/id/199216 


# 如何绕过Windows 10用户组策略


                                阅读量   
                                **751209**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者medium，文章来源：medium.com
                                <br>原文地址：[https://medium.com/tenable-techblog/bypass-windows-10-user-group-policy-and-more-with-this-one-weird-trick-552d4bc5cc1b](https://medium.com/tenable-techblog/bypass-windows-10-user-group-policy-and-more-with-this-one-weird-trick-552d4bc5cc1b)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t012f3a9ba2fc7ef355.png)](https://p3.ssl.qhimg.com/t012f3a9ba2fc7ef355.png)



## 0x00 前言

在本文中，我将分享如何滥用Windows的一个功能来绕过用户组策略（User Group Policy）。用户组策略被绕过并不意味着世界末日，但毕竟存在潜在风险，根据用户组策略的具体设置，这种行为可能对安全环境造成极大影响。我在Windows 7及Windows 10 Enterprise x64 （10.18363 1909）上测试了这种技术，利用过程不需要管理员权限。这种技术与系统在用户登录时对用户账户注册表的加载过程有关，因此我们首先要了解用户登录Windows账户的过程。



## 0x01 用户登录过程

当登录Windows账户时，系统会加载与账户有关的用户设置。这些设置加载自用户的“Registry Hive”（注册表配置单元），也就是我们打开注册表（`regedit`）时看到的`HKEY_CURRENT_USER`子项，其中包含用户相关的一些设置，涉及到操作系统以及已安装的各类应用程序。这个Hive实际上是一个文件，具体路径为`%USERPROFILE%\ntuser.dat`。当用户登录时，`ProfSvc`（用户配置文件服务）会定位该文件，然后调用[`NtLoadKeyEx`](http://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented%20Functions%2FNT%20Objects%2FKey%2FNtLoadKey.html)以加载Registry Hive。如果用户想在登录会话期间修改注册表键值，必须调用适当的Microsoft API，后者会检查用户是否具备这些键值的修改权限。



## 0x02 问题描述

如果我们运行ProcMon，启用”boot logging”功能，可以看到用户登录主机时`ProfSvc`服务会执行比较有趣的一个操作。

[![](https://p4.ssl.qhimg.com/t01a33177767f1f2de1.png)](https://p4.ssl.qhimg.com/t01a33177767f1f2de1.png)

图1. 用户登录时`ProfSvc`的操作

`ProfSvc`在加载`%USERPROFILE%\ntuser.dat`之前，会先检查`%USERPROFILE%\ntuser.man`文件是否存在。`ntuser.man`与`ntuser.dat`完全一致，但适用于“强制配置文件”场景。由于非管理员用户具备`%USERPROFILE%`的写权限，因此我们可以释放自己构造的`ntuser.man`，获得一些有趣的结果。



## 0x03 绕过用户组策略

组策略（Group Policy）是Windows提供的一种功能，允许域管理员在主机级别以及/或者用户级别配置组策略设置。对于用户策略，相关设置会被在登录时推送到用户账户中，存放在`%USERPROFILE%\ntuser.dat`中。这些用户策略对域用户只读，避免被任意篡改。

[![](https://p0.ssl.qhimg.com/t01de2e0ce1a27e4d0c.png)](https://p0.ssl.qhimg.com/t01de2e0ce1a27e4d0c.png)

图2. 域用户具备`Policies`注册表键值的只读权限

由于我们可以使用一个全新的Hive，因此能够绕过或者修改“被保护的”强制型用户组策略。

我们只需要执行如下操作：

1、构造名为`ntuser.man`的用户Registry Hive；

2、删除或者修改我们希望保存在Hive中的策略键值；

3、将该文件释放到目标主机的`%USERPROFILE%`目录中；

4、注销并重新登录。



## 0x04 同步问题

熟悉用户组策略的小伙伴都知道，系统会在用户登录时（以及登录后定期间隔内）重新同步并重新应用组策略，因此会覆盖可能被修改过的任何策略。即便我们为了避免这种覆盖操作，在构造的键值的ACL中移除`SYSTEM`，但`GpSvc`（Windows组策略客户端）会检测到这种行为，在登录时更正ACL，以便再次获得写入权限，然后重写组策略设置。

但其实我们有办法能绕过这个限制。我观察了`GpSvc`内部对这种ACL的处理过程，发现当`GpSvc`碰到我们的“策略”子键时，会调用内部函数`ForceRegCreateKeyEx`，该函数会尝试以写权限打开我们的“策略”子键，如果打开失败，则会调用`AddPolicyPermissionOnKey`来获取该表项所有权，恢复`SYSTEM`在该表项上的写入权限，然后重新执行打开操作，覆盖组策略项目。

[![](https://p2.ssl.qhimg.com/t01e019a2dc40ad362c.png)](https://p2.ssl.qhimg.com/t01e019a2dc40ad362c.png)

图3. `GpSvc.dll`中的`ForceRegCreateKeyEx`例程

查看`AddPolicyPermissionOnKey`例程，我注意到该函数会修改子项的ACL，添加`SYSTEM`，但并不会移除已有的任何ACL项目。这意味着如果我们显式设置`SYSTEM`权限，设置为不可写，那么就能阻止`SYSTEM`获得相应的写入权限，因为我们设置的`DENY`规则优先级将大于系统尝试添加的`ALLOW`规则。

了解这一点后，整个利用过程就比较简单，如下图所示：

[![](https://miro.medium.com/max/1600/1*YQ2UybTil9tqCyTN-n2nFg.gif)](https://miro.medium.com/max/1600/1*YQ2UybTil9tqCyTN-n2nFg.gif)

图4. 操作过程

在上图中，左侧为域控制器，右侧为连接域控的主机。从图中可知，域控在用户组策略中设置了“Remove Task Manager”规则，在域用户的主机上右键单击任务栏，我们就能看到灰色的“任务管理器”。然而在`%USERPROFILE%`目录中释放我们精心构造的`NTUSER.man`文件后，当用户注销/登录后，这个规则将不再生效。

该问题的影响程度很大程度上取决于具体的“策略设置”，尽管从恶意软件角度来看，这种方法可能存在安全隐患，但这类威胁可能更适用于策略规避场景，其中恶意域用户希望通过该方法规避域管设置的限制策略。



## 0x05 其他应用场景

需要注意的是，除了绕过用户组策略之外，这种方法还可能导致其他后果：

1、单个文件代码执行。攻击者可能会利用[某些漏洞](https://www.tenable.com/security/research/tra-2020-07)，以非管理员权限将文件释放到Windows文件系统中。如果漏洞利用程序释放的是`%USERPROFILE\ntuser.man`，配合自启动注册表键值来执行远程SMB共享中的文件，那么就能通过释放单个不可执行的文件，最终获得可靠的代码执行环境。

2、绕过反病毒/EDR解决方案。有些反病毒/EDR产品可能只会通过拦截注册表API或者内核回调函数来监控注册表修改操作，在这种情况下，我们可以通过替换整个Hive来完成注册表修改，从而规避监控及检测机制。

3、拒绝服务。如果我们在`%userprofile%`释放一个空白的`ntuser.man`文件，`ProfSvc`将无法加载注册表，因此用户将无法登录，需要以安全模式启动，或者使用备份的管理员账户来删除有问题的`ntuser.man`文件。



## 0x06 PoC

> 警告：以下操作可能会破坏Windows账户，不要在不具备管理员权限的域主机上尝试。我建议大家在个人主机上尝试，不要使用`Administrator`账户，因为执行攻击步骤后，我们需要`Administrator`账户来登录系统，删除`ntuser.man`文件。

**1、构造`ntuser.man`**

准备完全独立（且相同版本）的Windows主机，我们具备该主机的管理员访问权限，然后将任意用户对应的`%USERPROFILE%\ntuser.dat`文件拷贝到另一个目录。注意，我们需要确保该用户没有登录，这样才能执行拷贝操作。

在`Administrator`账户中，运行`regedit.exe`，选择`HKEY_LOCAL_MACHINE`表项，然后点击“File -&gt; “Load Hive”菜单加载拷贝的Registry Hive。

在新加载的注册表中，在适当的策略注册表路径下清除或者添加任意策略。比如，许多用户策略会存放在`\Software\Microsoft\Windows\CurrentVersion\Policies\`路径下。

在注册表加载的Hive根节点中，修改权限，设置`Everyone`具备完整控制权限（读、写等），将这些权限应用到所有子项中。

根据我们希望覆盖或添加的“策略”，我们需要找到与之相关的子键，这些子键可能不会都存放在用户注册表的同一个表项下。比如，在“Remove Task Manager”场景中，定义该策略的值位于`\Software\Microsoft\Windows\CurrentVersion\Policies\System`键中，因此我们需要在`System`子键上添加一个`DENY`规则，阻止`SYSTEM`获取该键的“写入/创建”权限，确保`GpSvc`无法执行覆盖操作。

**2、释放`ntuser.man`**

在继续操作前，我们要确保在测试主机上拥有具备管理员权限的备份账户，并且与测试所用的账户不同。如果不满足该条件，请立即创建该账户，以便后续删除PoC文件。

将我们构造的Registry Hive拷贝至目标主机的`%USERPROFILE%\ntuser.man`，覆盖用户组策略。

注销并重新登录，此时我们能看到Windows的欢迎界面，等待欢迎界面结束后，现在所有用户组策略已经被我们`ntuser.man`中设置的策略所替代。

**3、删除`ntuser.man`**

测试完PoC后，我们需要注销当前账户，然后使用`Administrator`账户登录，从用户配置目录中删除`ntuser.man`文件。



## 0x07 总结

我们根据[90天披露策略](https://static.tenable.com/research/tenable-vulnerability-disclosure-policy.pdf)向微软反馈了该[问题](https://www.tenable.com/security/research/tra-2020-08)，虽然官方能够完整复现该问题，但认为这种行为符合预期，不属于安全问题范畴。我知道这并不是一个大问题，但我相信，如果我们能根据这种方式修改被保护的组策略（无论具体的执行过程），应该已经超过了预期的安全边界。
