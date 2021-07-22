> 原文链接: https://www.anquanke.com//post/id/85924 


# 【技术分享】针对AIX系统的渗透测试技巧分享


                                阅读量   
                                **130503**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：thevivi.net
                                <br>原文地址：[https://thevivi.net/2017/03/19/aix-for-penetration-testers/](https://thevivi.net/2017/03/19/aix-for-penetration-testers/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p5.ssl.qhimg.com/t01533818ff90cdded2.png)](https://p5.ssl.qhimg.com/t01533818ff90cdded2.png)**

****

翻译：[77caikiki](http://bobao.360.cn/member/contribute?uid=2846452071)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**背景**

在最近了一次内部渗透测试中，我在我客户的服务器上拿到了一个低权限的shell。这是一个关键业务的服务器，所以下一步要做的就是对这台服务器进行信息枚举，进而获取root权限。

通常我开始信息枚举的时候都是先uname -a，先得到一些基本的系统信息；然而有趣的是，这次我对一些输出并不明白是什么意思。

这是我第一次在AIX系统上尝试提权，然后我在网上居然没有找到多少与AIX系统提权相关的信息，这点我很吃惊。

我读到的大部分后渗透教程都只提到AIX系统的用户的密码hash文件存放位置与一般的系统(/etc/shadows)不同，它存放在/etc/security/passwd。我漫无目的地花了一些时间运行一些命令，然而总是不成功。于是我马上意识到AIX系统和其他Unix系统的区别并不仅仅在这里。然后我花了一点儿时间浏览了各种AIX系统的管理员手册，命令说明(链接在文章底部)，然后把这些知识整合成了一个包含各种后渗透技巧的清单。我决定发布这篇博客，希望以后可以给那些找不到什么线索的渗透测试人员(红军)带来一定的帮助。

<br>

**AIX**

AIX(Advanced Interactive eXecutive)系统是由[IBM](https://en.wikipedia.org/wiki/IBM)为它的几种计算机平台开发并销售的一系列专有的Unix操作系统。

AIX是一个企业级的操作系统，所以像银行、政府、保险公司、发电站和大学这样的大型组织会对它比较青睐。

AIX在version 3之前的的默认shell是[Bourne shell](https://en.wikipedia.org/wiki/Bourne_shell)(/bin/sh)。

在version 3之后就变成了[Korn shell](https://en.wikipedia.org/wiki/KornShell)(/bin/ksh)。

在写这篇博客的时候，AIX的最新版本是AIX 7.2。

我得说清楚其实大部分基本的Unix命令都适用于AIX系统，比如导航，目录列表，进程列表，文件处理，搜索以及grep等等。

所以你并不需要从头开始学习Unix命令。但是如果你以后要经常对AIX服务器进行信息枚举的话，那么就有一些小技巧你得注意了。

<br>

**AIX信息枚举**

其实网上已经有很多很好的Linux系统的后渗透教程了(链接都在文章底部)，很多信息枚举技术都适用于AIX系统。

所以我就尽量不要重复造轮子了。虽然会有一些重复的基本常见命令，但是我会尽量避免出现这种情况。

我把我系统信息枚举分成了7个部分，

**1. 系统信息**

**2. 用户和组**

**3. 驱动和共享**

**4. 网络信息**

**5. 进程信息**

**6. 软件/包**

**7. 配置和杂项**

**1. 系统信息**

[![](https://p3.ssl.qhimg.com/t010d51624d0e67f2a6.png)](https://p3.ssl.qhimg.com/t010d51624d0e67f2a6.png)

**2. 用户和组**

[![](https://p1.ssl.qhimg.com/t0186d06419b068331e.png)](https://p1.ssl.qhimg.com/t0186d06419b068331e.png)

**AIX用户管理**

如果你拿到了一个有用户管理权限的账号，那这部分可能会派上用场： 

[![](https://p1.ssl.qhimg.com/t01d16329545d059ec3.png)](https://p1.ssl.qhimg.com/t01d16329545d059ec3.png)

**3. 驱动和共享**

[![](https://p3.ssl.qhimg.com/t017973f4731b8546c4.png)](https://p3.ssl.qhimg.com/t017973f4731b8546c4.png)

**4. 网络信息**

[![](https://p4.ssl.qhimg.com/t01b067486e2c74e84c.png)](https://p4.ssl.qhimg.com/t01b067486e2c74e84c.png)

**5. 进程信息**

[![](https://p0.ssl.qhimg.com/t0175fcc2e4703db67a.png)](https://p0.ssl.qhimg.com/t0175fcc2e4703db67a.png)

**6. 软件/包**

[![](https://p5.ssl.qhimg.com/t017506c5a4686ac413.png)](https://p5.ssl.qhimg.com/t017506c5a4686ac413.png)

**7. 配置和杂项**

在我说这部分之前，我得提一下，并没有对每个服务器配置的详细指南，因为这种配置信息完全是变化的，而且取决于环境和各个系统的用途。

在这篇文章最后的后渗透指南中有一长串可以在这个阶段帮你走出困境的技巧。我会总结一些常用的有用的策略。 

[![](https://p5.ssl.qhimg.com/t01787655102a674e83.png)](https://p5.ssl.qhimg.com/t01787655102a674e83.png)

<br>

**其他**

这部分可以算是后来又考虑到的吧，但我还是决定把这部分放出来。其实基本上就是一些涉及到默认AIX包/服务的技巧，这可能会在你对这个系统评估的各种阶段发挥用途。

**1. 利用——得到你的初始立足之地**

可用的攻击向量将完全取决于服务器的配置和运行的服务。你可能在AIX服务器上找到一些下面列出来的服务。 

[![](https://p5.ssl.qhimg.com/t01ab0297866c84b751.png)](https://p5.ssl.qhimg.com/t01ab0297866c84b751.png)

**2. 反弹shell**

然后你找到了命令执行漏洞，想要反弹一个shell过来？设置一下监听器，然后试一下下面的命令： 

[![](https://p0.ssl.qhimg.com/t01ef0ffdd80c63734b.png)](https://p0.ssl.qhimg.com/t01ef0ffdd80c63734b.png)

注意：记住一定要在80和443端口都监听。

**3. TTY shells**

通常情况下，你可能会发现你自己处在一个限制的非TTY shell的环境中。当你在与服务器交互的时候这种非TTY shell会限制你的选项。下面是一些可以生成TTY shell的命令。

[![](https://p2.ssl.qhimg.com/t01a314be59d486fef0.png)](https://p2.ssl.qhimg.com/t01a314be59d486fef0.png)

**4. 文件下载**

在你后渗透的过程中，你可能想往这个服务器上下载一个文件，比如用于提权的exploit。由于默认的AIX系统会缺少一些在其他Unix系统中具备的工具。比如我所在的系统就没有

安装wget, curl, 和nc。管理员可能会安装一些作为额外的用途，但是这里我还是假设你无法在服务器上找到这些命令。

幸运的是，AIX上已经安装了一些默认的程序以供你下载文件之用。 

[![](https://p5.ssl.qhimg.com/t0131c0774570ce9b4b.png)](https://p5.ssl.qhimg.com/t0131c0774570ce9b4b.png)

**5. 权限提升**

IBM对AIX系统的安全美誉十分自豪，当然这也是有原因的；并没有很多exploits可以利用他们的产品。但是好消息是，Offensive Security的漏洞利用数据库确实有各种AIX版本的权限提升利用脚本。你会发现这些都很有用。

[![](https://p5.ssl.qhimg.com/t01f4c90c7cf663367a.png)](https://p5.ssl.qhimg.com/t01f4c90c7cf663367a.png)

**6. 破解AIX密码**

AIX的用户密码文件都存放在/etc/security/passwd文件中。前面我已经提到了，这些hash值的存储格式与其他Unix系统不同。Hashcat支持各种AIX系统上的hash机制，

你可以在[这里](https://hashcat.net/wiki/doku.php?id=example_hashes)找到一些例子(搜索AIX)。 

我还找到一个Metasploit模块(auxiliary/analyze/jtr_aix)使用John the Ripper识别从AIX系统得到的弱密码，但是我还没试。我试了之后就来更新这篇文章。

<br>

**总结**

正如我在前面说的，我写这篇博客的原因是因为当我对AIX系统进行后渗透测试的时候，找这种信息的感到很无助。当然，这篇博客也并不是一个非常全面的AIX/Unix系统的

信息枚举指南，但是如果幸运的话，这会给之后的信息收集者更多信息参考。即便只帮助到了一个人，那也是值得的，这篇文章也达到了它的目的。Happy hunting。

<br>

**参考**

我找到了一些信息非常丰富的资料，它们不仅在我的渗透测试任务中帮助了我(是的，我确实获得了服务器的root权限)，也帮我完成了这篇文章。

**1. Linux后渗透测试**

[https://github.com/mubix/post-exploitation/wiki/Linux-Post-Exploitation-Command-List](https://github.com/mubix/post-exploitation/wiki/Linux-Post-Exploitation-Command-List) 

[http://blog.g0tmi1k.com/2011/08/basic-linux-privilege-escalation/](http://blog.g0tmi1k.com/2011/08/basic-linux-privilege-escalation/) 

[https://n0where.net/linux-post-exploitation/](https://n0where.net/linux-post-exploitation/) 

**2. AIX系统管理员指南和备忘录**

[https://aix4admins.blogspot.com](https://aix4admins.blogspot.com) 

[http://www.systemscanaix.com/aix-commands/](http://www.systemscanaix.com/aix-commands/)  

[http://www.linux-france.org/~mdecore/aix/AIX_COMMANDES.PDF](http://www.linux-france.org/~mdecore/aix/AIX_COMMANDES.PDF) 

[http://www.tablespace.net/quicksheet/aix-quicksheet.pdf](http://www.tablespace.net/quicksheet/aix-quicksheet.pdf) 

[http://bigcalm.tripod.com/aix/handycommands.htm](http://bigcalm.tripod.com/aix/handycommands.htm)  

[https://www.ibm.com/developerworks/aix/library/au-aix_cmds/](https://www.ibm.com/developerworks/aix/library/au-aix_cmds/)  

[http://visual.ly/ibm-aix-command-cheat-sheet](http://visual.ly/ibm-aix-command-cheat-sheet) 

**3. 破解AIX**

[https://www.sans.org/reading-room/whitepapers/testing/aix-penetration-testers-35672](https://www.sans.org/reading-room/whitepapers/testing/aix-penetration-testers-35672)  

[https://rhinosecuritylabs.com/2016/11/03/unix-nostalgia-hunting-zeroday-vulnerabilities-ibm-aix/](https://rhinosecuritylabs.com/2016/11/03/unix-nostalgia-hunting-zeroday-vulnerabilities-ibm-aix/) 

**4. 保护AIX——因为我喜欢蓝军们 **

[https://www.ibm.com/support/knowledgecenter/ssw_aix_72/com.ibm.aix.security/security-kickoff.htm](https://www.ibm.com/support/knowledgecenter/ssw_aix_72/com.ibm.aix.security/security-kickoff.htm) 

[https://www.ibm.com/support/knowledgecenter/en/ssw_aix_72/com.ibm.aix.security/security_checklist.htm](https://www.ibm.com/support/knowledgecenter/en/ssw_aix_72/com.ibm.aix.security/security_checklist.htm) 

[https://netseczone.blogspot.com/2008/10/aix-security-checklist.html](https://netseczone.blogspot.com/2008/10/aix-security-checklist.html) 
