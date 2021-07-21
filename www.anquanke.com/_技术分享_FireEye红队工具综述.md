> 原文链接: https://www.anquanke.com//post/id/84998 


# 【技术分享】FireEye红队工具综述


                                阅读量   
                                **132131**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fireeye
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2016/07/red_team_tool_roundup.html](https://www.fireeye.com/blog/threat-research/2016/07/red_team_tool_roundup.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t012eef6f710ad897d5.jpg)](https://p0.ssl.qhimg.com/t012eef6f710ad897d5.jpg)



**翻译：**[**Titan_Avenger******](http://bobao.360.cn/member/contribute?uid=2553709124)

**稿费：200RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



很多情况下，红队的工具都没有完成作品的一天，因为总是会有人想写一个新功能，或者某天某人早上被某个天才的想法唤醒又准备着手编写新工具。红队的队员通常会找出那些繁琐的任务，然后创建一个能够自动完成当前甚至未来评估任务的工具。正如我们老板说的：“懒惰让人才华横溢！”。 

在 Mandiant 公司，我们开发了相当多的工具和脚本来让我们的工作变得更加轻松。为了确保安全社区清楚这些工具可以从哪里下载，我们在半正规的基础上开始构建一个“工具综合报道”的博客栏目。这些博文的主要目的是介绍新开发的工具，或者对现有工具的重大更新的介绍。我们也尽量使用一些案例来证明我们的工具可用，让阅读更加有趣。 

我们[红队](https://www.fireeye.com/services/red-team-operations.html)经常面临各种不同的网络、技术、防御手段和组织结构。每次我们都面临不得不解决的新挑战，而所有客户的基础设施和配置都多少有所重叠。现存的公开工具也许不能被顺利地应用到大范围网络的情况下，或者可能无法帮助红队完成攻击[生命周期](https://www2.fireeye.com/rs/848-DID-242/images/Mtrends2016.pdf)。下面提到的工具都被修改过或是在过去的几个月内以某种形式被重新开发过。我们希望它们可以帮助你更轻松的完成工作任务。

<br>

**域枚举**

工具：[ADEnumerator](https://github.com/chango77747/AdEnumerator) 

域枚举是攻击生命周期中侦查阶段的一项重要任务。当你进入了一个域系统内，使用 ADSI（Active Directory Service Interfaces）或者 Windows 的 net 命令可以很简单的枚举域内的对象。ADSI 不在域内时也可以使用，通过 runas 命令以及 netonly 选项就可以完成，如图所示。在 ADSI 执行域枚举时构造详细的 LDAP 请求是非常麻烦的，所以我们编写了工具 ADEnumerator 来自动处理原生 LDAP 请求。 

[![](https://p3.ssl.qhimg.com/t0154ad23fffefe5a89.png)](https://p3.ssl.qhimg.com/t0154ad23fffefe5a89.png)

ADEnumerator 是一个被设计用来从非域内系统发起对 Active Directory 服务器请求的 PowerShell 模块。下面是应用 ADEnumerator 的案例：

你通过 NBNB 欺骗等方式从一台打印机上得到了域凭据，并且想开始域枚举。注：任何域用户凭据都可以使用 LDAP 请求进行查询。

你试图收集关于你得到的账户的更多信息，分组命名约定经常会显示出你可以在哪里使用这些凭据。（例如，组名为 `{`systemName`}`_localAdmin）。

你可以在一个已知的落脚点来发起一次内部渗透测试，而不是在域内系统处。

你想要在命令行中执行 Active Directory 枚举以便你可以把命令都连在一起

下图显示了导入 ADEnumerator.psm1 模块，与域控制建立 LDAP 连接并且执行各种域枚举的方法，ADEnumerator 中有许多中额外的方法。 

[![](https://p0.ssl.qhimg.com/t01265ae7adf192883a.png)](https://p0.ssl.qhimg.com/t01265ae7adf192883a.png)

另外，你也可以在你的攻击平台上安装[远程服务器管理工具](https://www.microsoft.com/en-us/download/details.aspx?id=7887)，使用 runas 和 mmc 命令来增加 Active Directory 的管理单元。然后你就可以改变域到目标域内，并且通过图形化方式看到整个的 Active Directory 结构。 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01af53437c2b6c835e.png)

<br>

**权限提升与横向平移**

工具：[CredNinja](https://github.com/Raikia/CredNinja) 与 [WMIOps](https://github.com/ChrisTruncer/WMIOps)

当你有超过一百张凭据的时候，你可能都不能确定一个凭据是否还可用，或者不能确定某个凭据是否拥有目标系统的管理员权限。CredNinja 就是为此而做的，通常可以完成以下功能：

利用 SMB 访问（TCP 端口 445）

尝试挂载 C$，返回： 

登录失败（错误的凭据，也可能是账户被锁定）

访问被拒绝（不是本地管理员）

文件清单（本地管理员）

多线程，可以在大范围主机时正常使用

目标操作系统版本和域成员的指纹

如果使用了 -users 参数，会得到 C:Users 的目录清单（如果是 XP 就是 C:Documents and Settings）并且带有主文件夹的时间戳，可以打印出一百天内一个文件夹的修改时间戳（时间可以定制，默认为100天） 

提供一个快速的用户狩猎功能，快速识别目标系统的活跃用户

CredNinja 在执行特权提升和横向平移时非常有用，你可以用它来辨别你的凭据可以在哪些系统上提权，以及从这些系统上继续得到其他凭据。下图可以看出， CredNinja 可以辨别出哪些域凭证拥有本地管理员权限，以及这些凭据是否仍然可用，同时 CredNinja 也可以移除那些不可用的凭据来清理你的凭据列表。 

[![](https://p4.ssl.qhimg.com/t01027d750ce8e2c85b.png)](https://p4.ssl.qhimg.com/t01027d750ce8e2c85b.png)

WMI（Windows Management Instrumentation）是在进攻能力上的新尝试，WMIOps 是一个使用 WMI 来执行多种基于主机的活动的 PowerShell 脚本，在 Windows 环境下不限本地还是远程。主要设计用于渗透测试或红队任务。现有一些使用 WMI 执行进攻任务的工具， WMIOps 将这些技术都整合到一个工具中，来完成攻击生命周期的不同任务。 

下图显示，通过 WMIOps 的 Get-ProcessOwnersWMI 方法可以得到目标主机 Win7-Client02 的用户列表。用户 Dick.Grayson 拥有本地管理员权限，并且可以在 Win7-Client02 上执行任意 WMI 命令。用户 Bruce.Wayne 在 Win7-Client02 上可以运行进程，这意味着这个用户也许将明文凭据存在了 LSASS（Local Security Authority Subsystem Service）中。 

[![](https://p1.ssl.qhimg.com/t01bd7b9f90d4f339fb.png)](https://p1.ssl.qhimg.com/t01bd7b9f90d4f339fb.png)

为了获得用户 Bruce.Wayne 的凭据，WMIOps 使用 Invoke-RemoteScriptWithOutput 方法来执行一个远端的 PowerShell 进程，使用 Invoke-Expression 命令通过 HTTPS 来下载并执行 Invoke-Mimikatz 脚本。这个命令也将输出送到 Web 服务器 10.181.73.210，服务器监听 HTTPS 流量。Mimikatz 的输出也送到 Web 服务器中。 

[![](https://p4.ssl.qhimg.com/t014544c97687ed1a9f.png)](https://p4.ssl.qhimg.com/t014544c97687ed1a9f.png)

[![](https://p2.ssl.qhimg.com/t013f5663b9cc4353c5.png)](https://p2.ssl.qhimg.com/t013f5663b9cc4353c5.png)

<br>

**初始向量**

工具：[EyeWitness](https://github.com/ChrisTruncer/EyeWitness) 

网络中最常见的初始向量就是知名 Web 管理门户（像 Jboss、Apache Tomcat、Jenkins 等）的默认凭据。我们为 EyeWitness 增加了一个“主动扫描”的模块，该模块提供以下功能：

签名认证，如果一个主机有一个已知的缺省凭证签名，并尝试使用存储在数据文件中的默认凭据来登录

登录检查，检查跟路径是不是一个 Web 登录表单，或者是 HTTP 基本身份认证，并尝试使用存储在数据文件中的用户名和密码的组合来进行身份验证

添加 URL 来检查登录，添加常见的登录页面路径到数据文件的清单中，例如 admin 和 login.php 等。定制化非常容易，轻松添加或删除数据列表。 

如果收到一个 200 状态码的页面，将会检查其是否是登录页面

EyeWitness 将会使用存储在数据文件中的用户名和密码组合来登录表单

关于主动扫描如下列图所示，如果 EyeWitness 检测到了登录页面，就会将判断登录章节增加到输出的报告中，但无法验证它。如果你想了解更多关于这个模块的信息，可以查看[这篇博文](https://www.christophertruncer.com/eyewitness-and-active-account-enumeration/)。 

[![](https://p1.ssl.qhimg.com/t01e1087d1cc51de5f1.png)](https://p1.ssl.qhimg.com/t01e1087d1cc51de5f1.png)

[![](https://p2.ssl.qhimg.com/t0170d229212ff73690.png)](https://p2.ssl.qhimg.com/t0170d229212ff73690.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011e8229c5f6e1f152.png)

<br>

**攻击者模拟**

工具：[Egress-Assess](https://github.com/ChrisTruncer/Egress-Assess) 

美国 Mandiant 网络安全公司，FireEye 和 合作伙伴 iSIGHT 一同带来无与伦比的威胁情报技术。客户经常会要求我们，识别针对他们特定资产的威胁攻击者，模拟他们的 TTP 来评估当前组织的威胁检测能力。Egress-Assess 就是这样一个 Python 工具，它可以模拟已知攻击者的 TTP，比如 IP 地址和 FQDNs（Fully Qualified Domain Names）连接到互联网。Egress-Assess 是公开的，但是 Mandiant 公司保留了包含那些可以代替真实威胁组织的知名 NBIs 的专有版本。 

Egress-Assess 会修改在 HTTP/HTTPS 中请求头的主机值为已知恶意的 IP 地址或者 FQDN，并且生成已知恶意的 URI。此外，该工具也可以生成虚假的 PII、PHI 或者 PCI 数据来模拟数据窃取。我们使用 Egress-Assess 来评估我们客户对真实威胁组织攻击或数据窃取的防御能力。受支持的威胁组织清单如图所示，如果你想了解更多关于 Egress-Assess 的信息，可以查看[这篇博文](https://www.christophertruncer.com/egress-assess-testing-egress-data-detection-capabilities/)。 

[![](https://p1.ssl.qhimg.com/t019fa1c33cc9d11ad3.png)](https://p1.ssl.qhimg.com/t019fa1c33cc9d11ad3.png)

<br>

**结论**

这些都只是辅助性的工具和一些实际应用的例子。我们鼓励您使用这些工具并在您的实验室评估使用。 

我们需要再次强调，每个工具被创造或者被修改都是随着我们的需要变化的。发现一个需求并为之开发出一个工具来自动化完成这个任务或达到目标是一件令人兴奋的事情。有些工具用了新的技术方案来实现一个目标，有些工具只是简单自动化便于刚好的完成任务。无论你的动机是什么，引入新的工具和技术都是提高行业知名度和提供更高质量保障的最佳方式。
