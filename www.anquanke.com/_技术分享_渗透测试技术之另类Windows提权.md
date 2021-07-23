> 原文链接: https://www.anquanke.com//post/id/85377 


# 【技术分享】渗透测试技术之另类Windows提权


                                阅读量   
                                **145935**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pentest.blog
                                <br>原文地址：[https://pentest.blog/windows-privilege-escalation-methods-for-pentesters/](https://pentest.blog/windows-privilege-escalation-methods-for-pentesters/)

译文仅供参考，具体内容表达以及含义原文为准

****

**[![](https://p3.ssl.qhimg.com/t016227e514259fc14e.jpg)](https://p3.ssl.qhimg.com/t016227e514259fc14e.jpg)**

**翻译：**[**pwn_361******](http://bobao.360.cn/member/contribute?uid=2798962642)

**预估稿费：200RMB**

**投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿**

**<br>**

**前言**

如果你获得了一台机器的低权限Meterpreter会话，并且当你尝试了一些常用方法，仍然提权失败时，是不是就意味着没法提权呢？不必着急，你仍然可以试试很多其它的技术。下面我们就来列举出几种提权方法。

<br>

**一、Windows服务路径没加双引号**

通常，如果一个服务的可执行文件的路径没有用双引号封闭，并且包含空格，那么这个服务就是有漏洞的。

如果你想验证这个漏洞，你可以在你的试验环境中增加一个有漏洞的服务，自己测试一下，下面咱们添加名为“Vulnerable Service”的服务，可执行文件放在“C:Program Files (x86)Program FolderA Subfolder”目录中。

[![](https://p1.ssl.qhimg.com/t0131190eddf38545d7.png)](https://p1.ssl.qhimg.com/t0131190eddf38545d7.png)

为了识别出没有加双引号的服务，你可以在Windows命令行中运行以下命令：

[![](https://p5.ssl.qhimg.com/t01a0097bddc8152f0b.png)](https://p5.ssl.qhimg.com/t01a0097bddc8152f0b.png)

运行上面的命令后，所有没有加双引号的服务将会被列出来：

[![](https://p4.ssl.qhimg.com/t01d19ffdacafecec7e.png)](https://p4.ssl.qhimg.com/t01d19ffdacafecec7e.png)

如果你从注册表中查看注册的服务，你会看到“ImagePath”的值是：

[![](https://p1.ssl.qhimg.com/t0129fde8552cb4dc3a.png)](https://p1.ssl.qhimg.com/t0129fde8552cb4dc3a.png)

安全的值应该是：

[![](https://p3.ssl.qhimg.com/t0128522f6e65912027.png)](https://p3.ssl.qhimg.com/t0128522f6e65912027.png)

[![](https://p5.ssl.qhimg.com/t01a134b36904af147c.png)](https://p5.ssl.qhimg.com/t01a134b36904af147c.png)

当Windows尝试启动这个服务时，它会按照下面的顺序寻找可执行文件，并运行第一个找到的：

[![](https://p3.ssl.qhimg.com/t01ac7684e33a0aca93.png)](https://p3.ssl.qhimg.com/t01ac7684e33a0aca93.png)

这个漏洞是由系统中的“CreateProcess”函数引起的，更多信息[请看这里](https://msdn.microsoft.com/en-us/library/windows/desktop/ms682425(v=vs.85).aspx)。

如果我们能成功的把恶意EXE程序放在这些路径下，当服务重新启动时，Windows就会以SYSTEM权限运行我们的EXE。当然，我们需要有进入其中一个目录的权限。

为了检查一个目录的权限，我们可以使用Windows内建的一个工具，icals，下面我们用这个工具检查“C:Program Files (x86)Program Folder”目录的权限。

[![](https://p2.ssl.qhimg.com/t018d8f5e424ce1f89a.png)](https://p2.ssl.qhimg.com/t018d8f5e424ce1f89a.png)

好幸运呐，你可以看到，“Everyone”用户对这个文件有完全控制权。

“F”代表完全控制。“CI”代表从属容器将继承访问控制项。“OI”代表从属文件将继承访问控制项。

这意味着我们可以随意将文件写入这个文件夹。

从现在开始，你要做什么取决于你的想象力。我比较倾向于生成一个反弹shell载荷，并用SYSTEM权限运行。

这个工作可以使用msfvenom来完成：

[![](https://p3.ssl.qhimg.com/t01982508b6223b882a.png)](https://p3.ssl.qhimg.com/t01982508b6223b882a.png)

然后将生成的载荷放到“C:Program Files (x86)Program Folder”文件夹：

[![](https://p3.ssl.qhimg.com/t01cdb16faadf052f17.png)](https://p3.ssl.qhimg.com/t01cdb16faadf052f17.png)

然后，在下一步启动这个服务时，A.exe就会以SYSTEM权限运行，下面我们试着停止，并重启这个服务：

[![](https://p2.ssl.qhimg.com/t01b7036051d18a21fd.png)](https://p2.ssl.qhimg.com/t01b7036051d18a21fd.png)

访问被拒绝了，因为我们没有停止或启动服务的权限。不过，这不是一个大问题，我们可以等，直到有人重启机器，或者我们自己用“shutdown”命令重启：

[![](https://p0.ssl.qhimg.com/t017fea1c0eacfd6a18.png)](https://p0.ssl.qhimg.com/t017fea1c0eacfd6a18.png)

正如你看到的，低权限的会话中断了，说明命令执行了。

我们的机器正在重启，现在，我们的载荷将会以SYSTEM权限运行，我们需要立即在本地建立监听：

[![](https://p5.ssl.qhimg.com/t01126bc911df5fe0f7.png)](https://p5.ssl.qhimg.com/t01126bc911df5fe0f7.png)

现在，我们获得了一个SYSTEM权限的meterpreter shell。

但是，我们新得到的会话很快就中断了，为什么呢？

不必担心，当一个服务在Windows系统中启动后，它必须和服务控制管理器通信。如果没有通信，服务控制管理器会认为出现了错误，并会终止这个进程。

我们所有需要做的就是在终止载荷进程之前，将它迁移到其它进程，你也可以使用自动迁移。

顺便说一句，有一个检查和利用这个漏洞的Metasploit模块：[exploit/windows/local/trusted_service_path](https://www.rapid7.com/db/modules/exploit/windows/local/trusted_service_path)。

在运行这个模块前，需要将它和一个已经存在的meterpreter会话(实际上就是你的低权限会话)关联起来，如下图：

[![](https://p2.ssl.qhimg.com/t01c2537990ab1f4b3f.png)](https://p2.ssl.qhimg.com/t01c2537990ab1f4b3f.png)

具体过程可以看[这里](http://www.zeroscience.mk/codes/msfsession.txt)。

<br>

**二、Windows服务带有易受攻击的权限**

大家知道，Windows服务是以SYSTEM权限运行的。因此，它们的文件夹、文件和注册的键值，必须受到强访问控制保护。在某些情况下，我们能遇到没有受到有效保护的服务。

**不安全的注册表权限**

在Windows中，和Windows服务有关的信息存储在“HKEY_LOCAL_MACHINESYSTEMCurrentControlSetServices”注册表项中，根据我们上面的测试实例，我们可以找到“HKEY_LOCAL_MACHINESYSTEMControlSet001ServicesVulnerable Service”键值。

[![](https://p3.ssl.qhimg.com/t010b86356417074314.png)](https://p3.ssl.qhimg.com/t010b86356417074314.png)

当然，我们建的“Vulnerable Service”服务存在漏洞。

[![](https://p3.ssl.qhimg.com/t014b44be071399f6cc.png)](https://p3.ssl.qhimg.com/t014b44be071399f6cc.png)

但问题是，我们怎样才能从命令行检查这些权限？让我们从头开始演示。

你已经得到了一个低权限的Meterpreter会话，并且你想检查一个服务的权限。

[![](https://p0.ssl.qhimg.com/t01c2fcd31409463746.png)](https://p0.ssl.qhimg.com/t01c2fcd31409463746.png)

你可以使用[SubInACL](https://www.microsoft.com/en-us/download/details.aspx?id=23510)工具去检查注册表项的权限。你可以从这里下载它，但是你要意识到这个程序是一个msi文件。如果目标机器上的AlwaysInstallElevated策略设置没有启用，那么你没法以低权限安装msi文件，当然，您可能也不想在目标机器上安装新的软件。

我建议你在一个虚拟机中安装这个软件，并在它的安装目录中找到“subinacl.exe”文件。它能顺利工作，并且无需安装msi文件。然后将SubInACL上传到目标机器。

[![](https://p3.ssl.qhimg.com/t01debe91e483c3182a.png)](https://p3.ssl.qhimg.com/t01debe91e483c3182a.png)

现在SubInACL工具可以用了，下面我们来检查“HKEY_LOCAL_MACHINESYSTEMControlSet001ServicesVulnerable Service”的权限。

[![](https://p4.ssl.qhimg.com/t01414d8986f7bb19ea.png)](https://p4.ssl.qhimg.com/t01414d8986f7bb19ea.png)

请看第22、23行，“Everyone”在这个注册表项上有完全的控制权。意味着我们可以通过编辑ImagePath的值，更改该服务的可执行文件路径。 这是一个巨大的安全漏洞。

我们生成一个反弹shell载荷，并将它上传到目标机器中，然后把服务的可执行文件路径修改为反弹shell载荷的路径。

首先，生成一个载荷：

[![](https://p5.ssl.qhimg.com/t01300d22789b0e24d1.png)](https://p5.ssl.qhimg.com/t01300d22789b0e24d1.png)

上传到目标机器中：

[![](https://p0.ssl.qhimg.com/t01848636a57da352f4.png)](https://p0.ssl.qhimg.com/t01848636a57da352f4.png)

将ImagePath的值改成我们载荷的路径：

[![](https://p1.ssl.qhimg.com/t011b4488419007e9cc.png)](https://p1.ssl.qhimg.com/t011b4488419007e9cc.png)

在下一次启动该服务时，payload.exe将会以SYSTEM权限运行。但是请记住，我们必须重新启动电脑才能做到这一点。

[![](https://p1.ssl.qhimg.com/t01d1a45ce0bc670106.png)](https://p1.ssl.qhimg.com/t01d1a45ce0bc670106.png)

如上图，我们的目标机正在重启，请将监听进程准备好，我们的载荷将会以SYSTEM权限运行。

[![](https://p3.ssl.qhimg.com/t01dc48ab354e5ad529.png)](https://p3.ssl.qhimg.com/t01dc48ab354e5ad529.png)

但是不是忘了，我们利用服务的方式和前面讲的方式(服务路径没加双引号)原理上实际是一样的,返回的高权限很快会断掉(可以使用自动迁移，如AutoRunScript)。

**不安全的服务权限**

这和前面讲的不安全的注册表权限很相似，只是这次我们没有修改ImagePath的值，我们直接修改了服务的属性。

为了检查哪个服务有易受攻击的权限，我们可以使用[AccessChk](https://technet.microsoft.com/en-us/sysinternals/accesschk.aspx)工具，它来源于[SysInternals Suite](https://technet.microsoft.com/en-us/sysinternals/bb842062.aspx)工具集。

将AccessChk工具上传到目标机器中：

[![](https://p2.ssl.qhimg.com/t010e7047ec8042dd51.png)](https://p2.ssl.qhimg.com/t010e7047ec8042dd51.png)

为了检查易受攻击的服务，我们运行以下命令：

[![](https://p4.ssl.qhimg.com/t0197d5b1399f22e12f.png)](https://p4.ssl.qhimg.com/t0197d5b1399f22e12f.png)

如图，通过上面的命令，所有“testuser”用户可以修改的服务都被列出来了。SERVICE_ALL_ACCESS的意思是我们对“Vulnerable Service”的属性拥有完全控制权。

让我们看一下“Vulnerable Service”服务的属性：

[![](https://p0.ssl.qhimg.com/t017cf4bb867f47a3be.png)](https://p0.ssl.qhimg.com/t017cf4bb867f47a3be.png)

BINARY_PATH_NAME参数指向了该服务的可执行程序(Executable.exe)路径。如果我们将这个值修改成任何命令，那意味着这个命令在该服务下一次启动时，将会以SYSTEM权限运行。如果我们愿意，我们可以添加一个本地管理员。

首先要做的是添加一个用户：

[![](https://p3.ssl.qhimg.com/t0155c4534bb7c4829c.png)](https://p3.ssl.qhimg.com/t0155c4534bb7c4829c.png)

在修改了binpath的值后，用“sc stop”和“sc start”命令重启服务：

[![](https://p1.ssl.qhimg.com/t01dcc8c0f81ae6bb60.png)](https://p1.ssl.qhimg.com/t01dcc8c0f81ae6bb60.png)

当你尝试启动服务时，它会返回一个错误。这一点我们之前已经讨论过了，在Windows系统中，当一个服务在Windows系统中启动后，它必须和服务控制管理器通信。如果没有通信，服务控制管理器会认为出现了错误，并会终止这个进程。上面的“net user”肯定是无法和服务管理器通信的，但是不用担心，我们的命令已经以SYSTEM权限运行了，并且成功添加了一个用户。

现在我们以同样的方式，再将刚才添加的用户，添加到本地管理员组(需要再次停止服务，不过此时服务不在运行状态，因为刚才发生了错误，进程被终止了)。

[![](https://p0.ssl.qhimg.com/t01ad931fd1d3b9e7e9.png)](https://p0.ssl.qhimg.com/t01ad931fd1d3b9e7e9.png)

下面可以享受你的新本地管理帐户了！

[![](https://p0.ssl.qhimg.com/t01ca11779fbffb4431.png)](https://p0.ssl.qhimg.com/t01ca11779fbffb4431.png)

同样，你也可以将一个反弹shell载荷上传到目标机器中，并将binpath的值改成载荷的路径。

只是这次不用再手动使用这个方法了，有现成的metasploit模块：[exploit/windows/local/service_permissions](https://www.rapid7.com/db/modules/exploit/windows/local/service_permissions)。

你需要将这个模块和一个已经存在的Meterpreter会话(已经得到的低权限会话)关联起来：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017a36e343de7a7219.png)

<br>

**三、不安全的文件/文件夹权限**

和前面我们讲过的“服务路径没加双引号”很相似，“服务路径没加双引号”利用了“CreateProcess”函数的弱点，结合了文件夹权限与服务可执行文件路径。但是在这部分，我们转换思路，试着直接替换可执行文件本身。

例如，如果对测试环境中“Vulnerable Service”服务的可执行文件路径的权限进行检查，我们可以看到它没有被保护好：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0133d77054dde084a5.png)

仅仅需要将“Executable.exe”文件替换成一个反弹shell载荷，并且当服务重启时，会给我们返回一个SYSTEM权限的meterpreter 会话。

<br>

**四、AlwaysInstallElevated设置**

AlwaysInstallElevated是一个策略设置，当在系统中使用Windows Installer安装任何程序时，该参数允许非特权用户以system权限运行MSI文件。如果启用此策略设置，会将权限扩展到所有程序。

实际上，启用这个值，就相当于给非特权用户授予了管理员权限。但是有一点我理解不了，有时候系统管理员会启用这个设置：

[![](https://p4.ssl.qhimg.com/t010ad0171664eb8ab5.png)](https://p4.ssl.qhimg.com/t010ad0171664eb8ab5.png)

你需要检查下面这两个注册表键值，来了解这个策略是否被启用：

[![](https://p4.ssl.qhimg.com/t013277fe2b41ede609.png)](https://p4.ssl.qhimg.com/t013277fe2b41ede609.png)

如果你获得了一个低权限的Meterpreter会话，reg内建命令可以帮你检查这些值：

[![](https://p3.ssl.qhimg.com/t0138c2491855d989e8.png)](https://p3.ssl.qhimg.com/t0138c2491855d989e8.png)

如果，你得到了一个错误，就像是“ERROR: The system was unable to find the specified registry key or value.”，它的意思是这个注册表值没有被创建，也就是说这个策略没有启用。但是如果你看到了下面的输出结果，那意味着该策略设置是启用的，你可以利用它。

[![](https://p4.ssl.qhimg.com/t010c096db10ed9d5bb.png)](https://p4.ssl.qhimg.com/t010c096db10ed9d5bb.png)

正如我前面说过的，在这种情况下，Windows Installer会使用高权限来安装任何程序。因此，我们需要生成一个恶意的“.msi”文件，并运行它。Msfvenom工具可以完成这个工作。

如果你想生成一个“.msi”文件，并向目标机器中添加一个本地管理帐户，你可以使用“windows/adduser”作为载荷:

[![](https://p1.ssl.qhimg.com/t01c8fe6275a239d1b4.png)](https://p1.ssl.qhimg.com/t01c8fe6275a239d1b4.png)

但是在这个例子中，我要生成一个反弹shell载荷(Payload.exe)，并使用一个msi文件执行这个载荷，首先，产生Payload.exe：

[![](https://p5.ssl.qhimg.com/t01cbe450915fe93c34.png)](https://p5.ssl.qhimg.com/t01cbe450915fe93c34.png)

然后使用“windows/exec”生成一个malicious.msi。请确定你填写了Payload.exe的正确路径：

[![](https://p1.ssl.qhimg.com/t0148bd7772a5baf35a.png)](https://p1.ssl.qhimg.com/t0148bd7772a5baf35a.png)

然后我们将这两个可执行文件上传到目标机器中。

[![](https://p5.ssl.qhimg.com/t0125ba55b2be1a836c.png)](https://p5.ssl.qhimg.com/t0125ba55b2be1a836c.png)

在执行“.msi”文件前，在另一个窗口中开启一个新的监听，等待高权限的shell连接：

[![](https://p2.ssl.qhimg.com/t01711a593ca351a985.png)](https://p2.ssl.qhimg.com/t01711a593ca351a985.png)

现在，我们准备执行！

[![](https://p2.ssl.qhimg.com/t012e0fe531b17df623.png)](https://p2.ssl.qhimg.com/t012e0fe531b17df623.png)

“/quiet”表示安静模式，无用户交互。“/qn”表示没有GUI。“/i”表示安装或配置产品。

如下图，成功返回：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019d06d360ed821de3.png)

除了手动使用这个技术，你也可以使用现成的metasploit模块：[exploit/windows/local/always_install_elevated](https://www.rapid7.com/db/modules/exploit/windows/local/always_install_elevated)。

该模块SESSION参数需要设置为一个已经存在的Meterpreter会话： 

[![](https://p4.ssl.qhimg.com/t017ef7c0cd7a7beaee.png)](https://p4.ssl.qhimg.com/t017ef7c0cd7a7beaee.png)

<br>

**五、DLL劫持**

假如上面的方法都没成功，不要放弃。我们开始研究一下正在运行的进程。

[![](https://p5.ssl.qhimg.com/t010d075a18deb99b10.png)](https://p5.ssl.qhimg.com/t010d075a18deb99b10.png)

如上图，如果我们的shell是以低权限运行的，我们不会看到进程的详细信息(运行在高权限上的进程)，如用户、路径、结构。但是我们可以了解到有哪些进程运行在高权限上。如果其中的一个进程存在漏洞，我们就可以利用它来提升我们的权限。

在对进程研究过程中，Vulnerable.exe进程引起了我的注意，让我们来找一找它的位置，并下载它：

[![](https://p2.ssl.qhimg.com/t01c48183fe06329b10.png)](https://p2.ssl.qhimg.com/t01c48183fe06329b10.png)

当我对它进行检查后，我意识到它试图加载一个名为“hijackable.dll”的DLL。

[![](https://p5.ssl.qhimg.com/t0164c9e587d77bad52.png)](https://p5.ssl.qhimg.com/t0164c9e587d77bad52.png)

在这个例子中，Vulnerable.exe进程存在DLL劫持漏洞。当然，实际上这个Vulnerable.exe只是一段简单的代码，在没有做检查的情况下加载了一个DLL：

[![](https://p2.ssl.qhimg.com/t01db6057b839790b34.png)](https://p2.ssl.qhimg.com/t01db6057b839790b34.png)

回到我们的话题，什么是DLL劫持呢？微软的[一篇文章](https://msdn.microsoft.com/en-us/library/windows/desktop/ff919712(v=vs.85).aspx)是这样解释的：

当应用程序动态加载动态链接库而不指定完整的路径名时，Windows会尝试通过一个特定的目录顺序，来搜索定位DLL，在这里有[目录的搜索顺序](https://msdn.microsoft.com/en-us/library/windows/desktop/ms682586(v=vs.85).aspx)。如果攻击者得到了其中一个目录的控制权限，他可以用一个恶意软件来替代DLL。这种方法有时被称为DLL预加载攻击或二进制移植攻击。如果系统在搜索到受感染的目录前，没有找到合法的DLL，那它将会加载恶意的DLL。如果这个应用程序是以管理员权限运行的，那么攻击者就可以成功的得到本地权限提升。

当一个进程尝试加载DLL时，系统会按以下顺序搜索目录：

1.应用程序加载的目录。

2.系统目录。

3.16比特系统目录。

4.Windows目录。

5.当前目录。

6.PATH 环境变量中列出的目录。

因此，为利用这个漏洞，我们按以下步骤：

1.检查进程加载的DLL是否存在于磁盘中。

2.如果不存在，将恶意DLL放在我刚才提到的其中一个目录中。当进程执行时，它可能会找到该DLL，并加载DLL。

3.如果DLL在上述其中一个目录中存在，那么将恶意DLL放在比当前目录的搜索优先级更高的目录中，例如，如果源DLL在Windows目录中，并且我们获得了应用程序加载目录的权限时，我们可以将恶意DLL放到应用程序加载目录，当应用程序加载DLL时，它会首先加载该目录的DLL。最终，我们的恶意代码会以高权限执行。

下面，让我们在目标机器中搜索一下hijackable.dll的位置：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012e7b5657db05aa3f.png)

貌似在机器上不存在，但是我们实际上无法确定这一点，也许它被放在了一个我们没有权限查看的目录中，不要忘了，我们目前的权限仍然是低权限。

下一步是检查可能的弱权限文件夹。我通常检查一个软件是否被安装在根目录中，如Python。因为如果一个文件夹被创建在根目录中，通常对于所有认证的用户(authenticated users:Windows系统中所有使用用户名、密码登录并通过身份验证的账户，不包括来宾账户Guest)，默认情况下它是可写的。像Python、Ruby、Perl等等。通常会添加到PATH环境变量中。

记着，Windows会检查PATH环境变量中的目录。

[![](https://p5.ssl.qhimg.com/t014095dcb3190a8716.png)](https://p5.ssl.qhimg.com/t014095dcb3190a8716.png)

正如我想的，目标机器上安装了Python，让我们检查一下它的权限：

[![](https://p3.ssl.qhimg.com/t0173d02f2b86663007.png)](https://p3.ssl.qhimg.com/t0173d02f2b86663007.png)

太好了，认证的用户有修改的权限。

剩下最后一项检查了，我们需要确定“C:Python27”目录是否已经被添加到PATH环境变量中，检查这个很容易，在shell中试一下“python -h”就知道了，如果帮助页面成功显示，意味着环境变量已经添加了：

[![](https://p1.ssl.qhimg.com/t016240f9f1f32249b1.png)](https://p1.ssl.qhimg.com/t016240f9f1f32249b1.png)

结果非常好，下面我们创建一个DLL版本的反弹shell载荷：

[![](https://p0.ssl.qhimg.com/t01de48823ef7ca11a8.png)](https://p0.ssl.qhimg.com/t01de48823ef7ca11a8.png)

将这个DLL上传到“C:Python27”目录：

[![](https://p0.ssl.qhimg.com/t01ffcf695b0d3bbd4d.png)](https://p0.ssl.qhimg.com/t01ffcf695b0d3bbd4d.png)

现在，我们重启“Vulnerable.exe”进程，进程会加载恶意DLL，我们可以尝试杀死进程，如果我们足够幸运，它将会自动启动：

[![](https://p4.ssl.qhimg.com/t01836a24600cec422b.png)](https://p4.ssl.qhimg.com/t01836a24600cec422b.png)

好吧，我们今天运气不好，没有杀死。不过至少，我们可以重启机器。如果“Vulnerable.exe”进程是一个开机启动应用，或一个服务、一个计划任务，那它将会再次启动。最坏的情况是，我们得等待有人来启动它。

[![](https://p4.ssl.qhimg.com/t01729cda14f62204c9.png)](https://p4.ssl.qhimg.com/t01729cda14f62204c9.png)

机器正在重启，让我们开启一个监听，希望有好运：

[![](https://p0.ssl.qhimg.com/t01e7e98f274a73d1b1.png)](https://p0.ssl.qhimg.com/t01e7e98f274a73d1b1.png)

成功了！

<br>

**六、存储的凭证**

如果上面的方法中，有任何方法管用了，拉下来你可以试着找一些存储的凭证。你可能想检查这些目录：C:unattend.xml、C:sysprep.inf、C:sysprepsysprep.xml。

你可以使用下面的查询方法：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f30898a25ab539c7.png)

<br>

**七、内核漏洞**

在我们这篇文章中，我们主要讲了不依赖内核漏洞的提权方法，但是如果你想利用一个内核漏洞来提升权限的话，也许你能用到下面的命令，它可以帮你选择利用哪一个漏洞：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01402d7ac8542614c2.png)

它会列出机器中的更新。

<br>

**八、对有效载荷的说明**

在这篇文章中，我们使用了由msfvenom生成的载荷，但是在今天，这些载荷已经[被各种反病毒软件标记了](https://www.virustotal.com/tr/file/c904c6a47434e67fe10064964619d2d0568b1976e6e3ccacccf87d8e7d7d1732/analysis/1484771308/)，因为它非常受欢迎，并被反病毒厂商所熟知。不过，在创建可执行文件时，使用绕过AV的技术，将会给你带来好的结果。你可以考虑读一下这些文章：

[Art of Anti Detection 1 – Introduction to AV &amp; Detection Techniques](https://pentest.blog/art-of-anti-detection-1-introduction-to-av-detection-techniques/)

[Art of Anti Detection 2 – PE Backdoor Manufacturing](https://pentest.blog/art-of-anti-detection-2-pe-backdoor-manufacturing/)

[反侦测的艺术part1：介绍AV和检测的技术](http://bobao.360.cn/learning/detail/3420.html)

[反侦测的艺术part2：精心打造PE后门](http://bobao.360.cn/learning/detail/3407.html)
