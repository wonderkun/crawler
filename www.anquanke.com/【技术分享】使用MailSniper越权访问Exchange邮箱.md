
# 【技术分享】使用MailSniper越权访问Exchange邮箱


                                阅读量   
                                **246980**
                            
                        |
                        
                                                                                                                                    ![](./img/85984/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blackhillsinfosec.com
                                <br>原文地址：[http://www.blackhillsinfosec.com/?p=5871](http://www.blackhillsinfosec.com/?p=5871)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85984/t011fcf14cb714bee5f.jpg)](./img/85984/t011fcf14cb714bee5f.jpg)



翻译：[**村雨其实没有雨**](http://bobao.360.cn/member/contribute?uid=2671379114)

预估稿费：180RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**前言**

Microsoft Exchange用户能够授权其他用户对他的邮箱文件夹进行各种级别的访问。例如，**用户可以授予其他用户访问其收件箱中电子邮件的权力。如果用户（或Exchange管理员）不小心设置了不当的访问权限，这将导致组织中的任何用户都能够访问其电子邮件。**

使用MailSniper，可以快速枚举任何用户可访问的邮箱。**在这篇文章中，我将说明这种问题是如何产生的，如何确定存在权限问题的邮箱，如何在无需获取邮箱管理员许可的情况下阅读邮箱中的邮件。**

<br>

**使用Outlook设置邮箱权限**

更改邮箱权限是使用Microsoft Outlook客户端能够轻松完成的事。如果用户右键单击文件夹，比如“收件箱”，然后单击“属性”，该文件夹的属性菜单就会打开。

[![](./img/85984/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fd0c7c07652dc139.png)

单击“权限”选项卡能看到当前的设置。这就是事情变得有趣的地方了。单击“添加”按钮，用户可以指定某个账户来授予各种权限。这是非常理想的，因为用户能够限制特定人员的访问。但是您会注意到在权限中已经包含了“默认”和“匿名”选项。“默认”项目实质上已经包含了组织中的每个用户都有访问邮件的权限。

[![](./img/85984/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0124bcd407455c0250.png)

如果用户错误地将权限级别设置为“默认”而非“无”（除Contributor），这就可能让该组织中的每个成员访问该邮件文件夹。

[![](./img/85984/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0178ce854be5f9070f.png)

邮箱文件夹的权限也可以由Exchange管理员设置。直接在Exchange服务器上使用[Set-MailboxFolderPermission cmdlet](https://technet.microsoft.com/en-us/library/ff522363%28v=exchg.160%29.aspx?f=255&amp;MSPPError=-2147217396)，可以修改这些邮箱权限的设置。

<br>

**Invoke-OpenInboxFinder**

作为一名渗透测试人员，找到全世界都能访问的邮箱对我们是非常有价值的。这将成为一系列其他攻击的媒介。一方面，我们可以搜索其他用户的电子邮件来获取某些内容，例如密码或敏感数据，而无需其凭据。另一方面，如果该用户的电子邮件地址与密码重置系统相关联，攻击者可以触发密码重置，然后访问包含密码重置链接的用户电子邮件。

我已经在[MailSniper](https://github.com/dafthack/MailSniper)中添加了一个名为Invoke-OpenInboxFinder的功能，以帮助查找具有设置允许其他用户访问的权限的邮箱。使用它之前，我们首先需要再目标环境中收集一个电子邮件地址列表。MailSniper有一个名为"[Get-GlobalAddressList](http://www.blackhillsinfosec.com/?p=5330)"的模块，可用于从Exchange服务器检索全局地址列表。它将尝试Outlook Web Access（OWA）和Exchange Web服务（EWS）的方法。此命令可用于从Exchange收集电子邮件列表：

```
Get-GlobalAddressList -ExchHostname mail.domain.com -UserName domainusername -Password Spring2017 -OutFile global-address-list.txt
```

[![](./img/85984/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0146c7e00250053778.png)

如果您处于可以与目标组织的内部Active Directory域进行通信的系统上，也可以使用[Harmj0y的PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon)来收集电子邮件列表。将PowerView脚本导入PowerShell会话以获取电子邮件列表：

```
Get-NetUser | Sort-Object mail | ForEach-Object {$_.mail} | Out-File -Encoding ascii emaillist.txt
```

收到邮件列表以后，Invoke-OpenInboxFinder功能可以一次检查一个邮箱，以确认当前用户是否可以访问。它还将检查Exchange中是否存在可能被访问的任何公共文件夹。

要使用Invoke-OpenInboxFinder，需要将MailSniper PowerShell脚本导入到PowerShell中：

```
Import-Module MailSniper.ps1
```

接下来，运行Invoke-OpenInboxFinder函数：

```
Invoke-OpenInboxFinder -EmailList .emaillist.txt
```

Invoke-OpenInboxFinder将尝试自动发现机遇邮件服务器电子邮件列表中的第一个条目。如果失败，您可以使用-ExchHostname标志手动设置Exchange服务器位置。

在下面的示例中，终端以名为"jeclipse"的域用户运行。在从域中的电子邮件列表中运行Invoke-OpenInboxFinder后，发现了两个公用文件夹。此外"jQuery"可以访问"maximillian.veers@galacticempireinc.com"的收件箱。Invoke-OpenInboxFinder将会打印出每个项目的权限级别。在输出中可以看到"Default"项设置为"Reviewer"。

[![](./img/85984/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fabc49e3b4710a7b.png)

<br>

**使用MailSniper搜索其他用户的邮箱**

发现邮箱具有允许用户访问的过多权限之后，MailSniper可以读取并搜索目标邮箱中的邮件。MailSniper的Invoke-SelfSearch功能以前用户主要搜索正在运行它的用户的邮箱，我稍作修改，以便能够检查另一个用户的电子邮件。这里需要指定一个名为"OtherUserMailbox"的新标志来访问其他邮箱。命令如下：

```
Invoke-SelfSearch -Mailbox target-email-address@domain.com -OtherUserMailbox
```

在下面的截图中，我使用"jeclipse"账户搜索maximillian.veers@galactiempireinc.com的邮箱。发现三个结果，其电子邮件的主题或主题中包含了密码或凭证。

[![](./img/85984/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0185c5fcf7f2ac3a7e.png)

<br>

**Office365和对外开放的Exchange服务器**

如果Exchange Web服务（EWS）可访问，Invoke-OpenInboxFinder也可以使用。你可能需要用ExchHostname手动指定主机名，除非它对外设置了自动发现。要连接到Office365，主机名将是"outlook.office365.com"，指定-Remote标志能让Invoke-OpenInboxFinder提示可用于向远程EWS服务进行身份验证的凭据。

用于检查托管在Office365上的邮箱以获得广泛权限的命令如下：

```
Invoke-OpenInboxFinder -EmailList .emaillist.txt -ExchHostname outlook.office365.com -Remote
```

以下是客户使用Office365时，真实的评估截图。我们可以在组织中访问单个用户的凭据。通过使用从全局地址列表收集的电子邮件列表运行Invoke-OpenInboxFinder，我们可以确定组织中的三个单独的账户允许我们的用户阅读他们的电子邮件。

[![](./img/85984/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c589150828fbee52.png)

<br>

**建议**

显然，防止攻击者访问有效的用户账户是防御的第一步。问题是它不会阻止你当前的员工去访问他们有权限访问的邮箱。另外注意，你必须要有一个可用的与邮箱关联的域账户，以检查是否能够访问他人的邮箱。

如果可能的话，限制在Outlook客户端上更改此类权限是非常有帮助的。我已经找到了一些很老的文章(2010年)说明权限选项能够用GPO锁定。我个人没有试过上面说的任何方法，但这值得一试。你能在[这里](https://social.technet.microsoft.com/Forums/office/en-US/3cab4bd5-5cf0-4588-8329-fe077f3f4564/use-gpo-to-prevent-people-from-granting-permissions-to-their-outlook-folders?forum=officeitproprevious)和[这里](https://www.experts-exchange.com/questions/26469721/Remove-permission-tab-in-Outlook.html)找到这些方法。

使用[MailSniper](https://github.com/dafthack/MailSniper)中的[Invoke-OpenInboxFinder](https://github.com/dafthack/MailSniper)功能，或使用Exchange上的[Get-MailboxFolderPermission cmdlet.aspx](https://technet.microsoft.com/en-us/library/dd335061(v=exchg.160)审核组织中所有帐户的设置。

<br>

**结论**

邮箱权限是红蓝双方都应该关注的问题。通过Outlook在文件夹属性中包含“默认”权限项的方式，这使得用户更有可能让组织中的任何人都能够访问其邮箱。在红方角度来看，这提供了在电子邮件中进一步查找网络密码或其他敏感数据的机会。而从蓝方角度看，则应该担心高级账户(C-Suite类型)意外地与整个公司共享了邮箱，或者公司员工窥探其他员工，甚至通过这些渠道修改邮箱等问题。

您可以在Github上下载MailSniper: [https://github.com/dafthack/mailsniper](https://github.com/dafthack/mailsniper)    
