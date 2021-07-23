> 原文链接: https://www.anquanke.com//post/id/101525 


# RDP劫持：如何透明劫持RDS以及RemoteApp会话


                                阅读量   
                                **132355**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Kevin Beaumont，文章来源：medium.com
                                <br>原文地址：[https://medium.com/@networksecurity/rdp-hijacking-how-to-hijack-rds-and-remoteapp-sessions-transparently-to-move-through-an-da2a1e73a5f6](https://medium.com/@networksecurity/rdp-hijacking-how-to-hijack-rds-and-remoteapp-sessions-transparently-to-move-through-an-da2a1e73a5f6)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t015dfd9484c7bfea19.png)](https://p1.ssl.qhimg.com/t015dfd9484c7bfea19.png)



## 一、前言

本文介绍了如何不依赖外部软件，通过远程桌面服务（Remote Desktop Services）在目标网络进行横向渗透，同时也介绍了如何防御这种攻击手段。

[![](https://p0.ssl.qhimg.com/t013d2bc6a10fac654f.gif)](https://p0.ssl.qhimg.com/t013d2bc6a10fac654f.gif)

上图中，Alexander Korznikov向我们展示了如何使用粘滞键（Sticky Keys）以及`tscon`来访问管理员的RDP会话，这种操作并不需要登录到服务器中。



## 二、RDP会话连接简介

在远程桌面服务中（如果你和我一样都是老男孩的话，说不定还记得另一个叫法：Terminal Services（终端服务）），如果我们想连接到另一个用户所在的会话，必须知道该用户的密码。但其实我们也可以在不掌握用户密码的情况下劫持会话，具体方法可以参考下文分析。

我们可以在任务管理器中右键点击某个用户、使用`tsadmin.msc`或者使用`tscon.exe`命令来间接目标会话，此时系统会要求我们输入用户密码，如果认证失败，则弹出错误信息。

[![](https://p3.ssl.qhimg.com/t01fd190735218e9b0d.png)](https://p3.ssl.qhimg.com/t01fd190735218e9b0d.png)



## 三、无凭据时的会话劫持技巧

[Benjamin Delpy](http://blog.gentilkiwi.com/securite/vol-de-session-rdp)（Mimikatz作者）以及[Alexander Korznikov](http://www.korznikov.com/2017/03/0-day-or-feature-privilege-escalation.html)分别在2011年以及周五提到，如果我们以SYSTEM用户身份运行`tscon.exe`，**我们就可以连接到任何会话，无需输入密码信息**。系统不会要求我们输入密码，而会让我们直接连接到用户的桌面。我认为之所以出现这种现象，原因在于Windows对session shadowing（会话重影）的具体实现方式，这种现象已经持续了多年之久。

现在有些人可能会说：“如果我们具备SYSTEM权限，我们就已经是root身份了，可以为所欲为，为何要多此一举呢？”

是的，这种想法没有问题。比如说，我们可以导出服务器的内存，然后再获取用户密码。不过这个攻击路径有点长，相比之下，`tscon.exe`只需要使用目标会话编号，就能立刻获取目标用户的桌面，并且不会留下明显的痕迹，也不需要使用外部工具。这种操作的重点并不是SYSTEM权限，而是如何在该权限下快速且隐蔽地达成目的。攻击者并不喜欢玩游戏，只关心如何在现有技术下迅速完成任务，总而言之这是一项非常有效的技术。

因此，我们只需要使用一条命令就可以劫持RDP会话。

关于这种技巧，我们需要知道如下一些小贴士：

1、我们可以连接到已断开的会话。因此如果某些用户已于3天之前登出，我们可以直接连接并使用他们所在的会话。

2、该方法可以解锁处于锁定状态下的会话。因此如果某个用户离开办公台位，我们可以窃取他们的会话，在不需要任何凭据的前提下解锁“工作站”。

3、该方法对于物理控制台同样适用。因此我们可以远程劫持屏幕，也能解锁物理控制台。

4、我们可以连接到任何会话。因此如果目标是帮助台，我们可以在不掌握任何凭据的情况下成功连接，如果是域管（Domain Admin）那再好不过。由于我们可以连接到已断开的会话，因此通过这种方法我们可以轻松在目标网络中横向渗透。

5、我们可以使用win32k SYSTEM漏洞利用技术（网上可以查到各种途径来获取SYSTEM权限），然后再使用这种方法。也就是说，即使我们是普通用户，如果系统没有打全补丁我们就能见缝插针。条条大路通罗马，只要能搞定SYSTEM权限（比如有各种方法可以获取本地管理员权限）就万事大吉。

6、不需要使用外部工具。因此不用去在意是否存在应用白名单机制，整个过程不会有可执行文件写入磁盘中。

7、除非目标了解需要监控哪些方面（下文会介绍具体方法），不然一切对他们来说都是透明的。

8、这种方法可以远程操作。即使我们没有登录到目标服务器，我们也可以接管远程主机上的会话。



## 四、获取SYSTEM权限下的tscon.exe

如果我们具备管理员权限，就可以根据Alexander介绍的一种方法来创建服务，完成任务：

[![](https://p1.ssl.qhimg.com/t012bbc4d5c0c02e539.png)](https://p1.ssl.qhimg.com/t012bbc4d5c0c02e539.png)

实际上这种方法操作起来非常简单，只需要使用`quser`命令获取待劫持的会话ID以及自己的SESSIONNAME（会话名），然后使用这些信息来运行`tscon`即可。这样操作后我们自己的会话会被替换成目标会话。默认情况下该服务会以SYSTEM权限运行，这样就实现了我们的目标。

如果你的动机不纯，请记得在操作结束后删除该服务。

在Windows Server 2012 R2服务器上的操作过程如下所示：

[http://v.youku.com/v_show/id_XMzQ3NjI3MTkxMg==.html](http://v.youku.com/v_show/id_XMzQ3NjI3MTkxMg==.html)

其他方法：

1、我们可以使用计划任务（Scheduled Tasks）来获取SYSTEM权限然后再运行命令，具体方法是将该命令安排为计划任务，以SYSTEM身份交互式运行即可。

2、也可以使用各种方法（如粘滞键）来获取SYSTEM权限，这种方法甚至不需要登录到系统中，具体见下文介绍。

3、利用漏洞（如前文所述）。



## 五、横向渗透

大多数组织都会在内部网络中开放远程桌面服务，这也是现在Windows的管理方式，此外RemoteApp也会使用RDP服务。正因为如此，这也是在目标网络环境中自由穿梭的绝佳方法，即使没有密码，我们也能横行四方，滥用其他人的访问权限。在目标的日志中，我们会以目标用户的身份出现，不涉及自己的信息。



## 六、如何创建无凭据劫持型后门

暴力破解远程桌面是一个比较严重的问题。只要正确搭建蜜罐，任何人都可以看到失败的RDP登录尝试行为。攻击者首先会进行端口扫描，然后发起数以千计的登录请求。

现在情况变得更加糟糕，我自己也在维护一个蜜罐，当我发现攻击者突破远程桌面后，他们会使用如下技术在系统中植入后门。

根据研究结果，200台被扫描的远程桌面服务器中，就有1台被攻击者使用这些方法成功植入后门。这意味着此时我们就可以使用会话劫持技术来继续渗透，甚至无需登录系统或者进行身份认证，这并不是一种好现象。在Shodan上搜索后，我们可以看到数百万开放RDP端口的服务器，并且随着云服务不断推广，现在这个数目也不断增长，与此同时问题也越来越严重。

### <a class="reference-link" name="%E6%96%B9%E6%B3%95%E4%B8%80%EF%BC%9A%E7%B2%98%E6%BB%9E%E9%94%AE"></a>方法一：粘滞键

这种方法非常简单，Windows提供了名为粘滞键（Sticky Keys）的一种功能，该功能属于系统的辅助功能，没有登录时就可以使用（登录屏幕上可以使用该功能，适用于物理控制台或者远程桌面场景）。粘滞键会以SYSTEM权限运行。

如果我们将`Sethc.exe`（粘滞键程序）替换为`cmd.exe`，那么即使我们被锁在系统之外也能使用后门，这个后门具备SYSTEM访问权限，因此即便没有目标主机账户我们也可以为所欲为。我们可以将`sethc.exe`替换为`cmd.exe`（这种方法需要重启系统并且具备目标主机的物理访问权限），也可以使用如下命令设置注册表实现后门植入：

```
REG ADD "HKLMSOFTWAREMicrosoftWindows NTCurrentVersionImage File Execution Optionssethc.exe" /t REG_SZ /v Debugger /d “C:windowssystem32cmd.exe” /f
```

大功告成，现在目标主机已经被永久植入一个后门。攻击者只需要连接目标主机的远程桌面，然后在登录界面多次按下F5即可。

### <a class="reference-link" name="%E6%96%B9%E6%B3%95%E4%BA%8C%EF%BC%9AUtilman"></a>方法二：Utilman

这种方法与前一种方法一样，只不过这次我们替换的是`utilman.exe`。在登录界面我们可以按下Windows+U键，然后就能获得具备SYSTEM权限的`cmd.exe`。

```
REG ADD "HKLMSOFTWAREMicrosoftWindows NTCurrentVersionImage File Execution Optionsutilman.exe" /t REG_SZ /v Debugger /d “C:windowssystem32cmd.exe” /f
```



## 七、如何判断RDP服务器是否被植入后门

已经有人开发出一款工具：[sticky_keys_hunter](https://github.com/ztgrace/sticky_keys_hunter)，能百分百满足我们的需求，只需运行该工具，就能找到哪些服务器被植入了SYSTEM级别的后门。

根据在线扫描结果，我们发现已经有大量开放RDP端口的服务器被植入了后门。



## 八、Mimikatz模块

在Windows渗透方面，怎么能不提到[Mimikatz](https://github.com/gentilkiwi/mimikatz/releases)。其实Mimikatz有一个模块可以简单完成这个任务，具体操作如下：

[![](https://p5.ssl.qhimg.com/t01b7d04207480965a1.gif)](https://p5.ssl.qhimg.com/t01b7d04207480965a1.gif)



## 九、缓解措施

从**操作系统**角度来看，我原以为Windows Server 2016不受这种攻击影响，然而进一步调查后，我发现事实并非如此。经过测试，这种方法适用于自Windows 2000以来的所有操作系统，包括Windows 10以及2016。

从**组策略**角度来看，强烈建议大家使用组策略来注销已断开的会话（只要用户断开后就应该立即这么做，至少间隔时间不要太久）。通常这种方法在IT环境中并不常用，但现在我们的确面临这类风险，并且只需要一条内置命令，实际环境就会受到影响。我自己也会注销掉空闲的用户会话。

还有，**不要将RDS/RDP接口暴露在互联网中**，如果你已经这么做，那么强烈建议你采用多因素认证机制。多因素认证搭建起来并不复杂，我们可以使用诸如Microsoft RD Gateway或者Azure Multi-Factor Authentication Server之类的解决方案来完成这个任务。如果你将RDP接口直接暴露在互联网中，当某人成功创建了系统上的本地用户、或者域用户的凭据猜测/复用起来非常容易，那么事情会变得非常糟糕。曾经有医院或者其他组织因为RDS服务器缺陷而被勒索攻击，这并不是危言耸听。



## 十、如何监控

事实上想监控会话劫持攻击并非易事，虽然Windows日志中有个事件可以记录下会话连接动作（Microsoft-Windows-TerminalServices-LocalSessionManager/Operational），然而普通用户的连接行为跟攻击者使用`tscon.exe`的攻击行为很难区分开来。我遍历了所有的事件日志，并没有找到与攻击有关的信息。这个问题非常严重，希望微软能尽快添加某种事件日志来解决这个难题。

我给出的建议是，用户应该使用事件日志以及类似Microsoft OMS、Windows Event Forwarding（Windows事件转发）或者Splunk之类的工具来对其他相关行为进行告警，我们要寻找的是滥用SYSTEM权限的那些攻击行为。

比如，我们应该重点关注并记录异常的服务创建行为、异常的计划任务创建行为。此外，我们也应该查找与Mimikatz相关的一些攻击活动。



## 十一、问答时间

Q：这种技术并不新颖也不属于漏洞。

A：Java applets以及宏也不是新技术。不管黑猫白猫，能抓老鼠就是好猫。这种技术可以隐藏在雷达之下，那么我们何乐而不为呢？

Q：如果我们具备SYSTEM权限，就已经控制了目标环境，何必多此一举呢？

A：非常正确。但是你能输入一条命令就解锁某个用户的桌面吗，即使他们一周以前已经离开去度假但并没有注销会话？掌握这种方法后，现在我们就可以做到这一点。
