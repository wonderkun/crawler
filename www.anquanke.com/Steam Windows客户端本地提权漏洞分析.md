> 原文链接: https://www.anquanke.com//post/id/184950 


# Steam Windows客户端本地提权漏洞分析


                                阅读量   
                                **307646**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者amonitoring，文章来源：amonitoring.ru
                                <br>原文地址：[https://amonitoring.ru/article/onemore_steam_eop_0day/](https://amonitoring.ru/article/onemore_steam_eop_0day/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/dm/1024_360_/t015b7610e39b61afac.jpg)](https://p4.ssl.qhimg.com/dm/1024_360_/t015b7610e39b61afac.jpg)



## 0x00 前言

不久之前，我刚发表过关于Steam漏洞的一篇研究[文章](https://amonitoring.ru/article/steamclient-0day/)。我收到了许多反馈，但Valve并没有发表任何看法，HackerOne给我发了一封内容颇多的信，但后面也没有任何进展。最终这个事件升级，Valve拒绝在HackerOne上接收我的报告，我无法再继续参与他们的漏洞拒绝计划（但H1剩余部分仍然可以参与）。

[![](https://p4.ssl.qhimg.com/t012d2c763ff8d8e47d.png)](https://p4.ssl.qhimg.com/t012d2c763ff8d8e47d.png)

大家可以阅读之前的文章了解详细信息。

Valve新推出一个补丁想解决这个问题，然而该补丁可以轻松被[绕过](https://twitter.com/general_nfs/status/1162067274443833344)，因此这个漏洞依然存在。

然而本文并不想讨论之前的老漏洞，会介绍一个全新的漏洞。由于Valve更喜欢看到直接公开的漏洞报告，而不是通过私下的沟通渠道解决问题，因此我决定满足他们的愿望。



## 0x01 简要描述

漏洞利用非常简单，主要包括3个步骤：

1、准备利用环境；

2、让Steam复制并运行我们自己的DLL；

3、DLL必须满足某些条件。

系统上任何用户（或者更明确地说，是主机上任何程序）都可以执行以上步骤，利用该漏洞最终可以以最高权限执行任意代码，因此该漏洞属于权限提升（EOP）或者本地提权（LPE）漏洞。尽管应用程序本身可能可能有潜在风险，但提升至最高权限后可以造成更严重后果，比如可以禁用防火墙及杀毒软件、安装rootkit、隐藏挖矿进程、窃取用户隐私数据等。



## 0x02 背景知识

上一篇文章的评论有些非常有趣，有人提到“用户不能往HKLM注册表中写入数据”或者“我们需要管理员权限才能创建符号链接”。想要核实这些言论其实很简单，大家也能猜到，这些结论都不正确。这里我想稍微提一下这方面内容，顺便介绍漏洞利用过程中稍微困难的几个点。

1）“用户不能往HKLM注册表中写入数据”。

实际上并没有这种规则，特定注册表项可以对应特定的安全规则。Valve向所有用户开放了`HKLM\SOFTWARE\Wow6432Node\Valve\steam`的完整控制权限，因此任意用户都可以随意操纵该表项。

2）“如果不具备管理员权限就不能开始或停止服务”。

也没有这种规则，特定服务可以对应特定的安全规则。Valve向任意用户开放了Steam Client Service的开始或停止权限。

3）“我们需要管理员权限才能创建符号链接”。

这个表述本身就比较有趣。在Windows系统中总共有5种常见的链接，但只有一半需要管理员权限。这5种链接分别为：文件符号链接、对象目录符号链接、硬链接、NTFS重解析点以及`reg_link`。只有在创建文件符号链接以及永久对象目录符号链接时才需要管理员权限（临时对象目录符号链接的生存周期与会话保持一致，在大多数情况下，一旦创建成功可以维持到重启之前，并且不需要特殊权限）。

4）“从目录到目录的符号链接”。

实际上这是NTFS重解析点（reparse point）或者是NTF挂载点（mount point）。名字本身并不关键，我们可以利用重解析点将一个目录作为另一个目录的链接。如果用户具备写入权限，就可以通过空目录创建这种链接。我们可以使用[symboliclink testing tools](https://github.com/googleprojectzero/symboliclink-testing-tools/)中的`CreateMountPoint.exe`来创建该链接。

5）OpLock

[OpLock](https://docs.microsoft.com/ru-ru/windows/win32/fileio/opportunistic-locks)（或者Opportunistic Lock，机会锁）是一种特殊机制，可以用来临时阻止对特定文件的访问。大家可以参考官网了解关于OpLock的更多细节，比如在文件处理以及不同访问类型时的功能等。简而言之，程序可以通过该功能“捕捉到”访问某个文件的事件，然后临时阻止该操作。我们可以使用[symboliclink testing tools](https://github.com/googleprojectzero/symboliclink-testing-tools/)工具包中的`SetOpLock.exe`工具来设置OpLocks。设置所需的OpLock后，当访问被锁定的文件时，该工具就会打印一条消息，如果我们按下回车键，就可以释放OpLock。

6）BaitAndSwitch

这是一种技术手法，将链接创建以及OpLock结合起来，以赢得TOCTOU（time of check/time of use）竞争条件。这里我们举个例子来描述这种技术：

设想某个程序会执行如下操作：

```
ReadContentFromFile(“C:\test\myfile.txt”);
ReadContentFromFile(“C:\test\myfile.txt”);
```

程序只是简单地连续两次读取同一个文件，那么这样是不是总是会读取到相同的内容？答案是并不一定。

首先，我们创建两个目录，其中分别包含`C:\test1\myfile.txt`以及`C:\test2\myfile.txt`。接下来，我们清空`C:\test`目录，然后创建目标为`C:\test1`的一个重解析点。然后我们在第一个目录的文件上设置OpLock并运行程序。一旦程序打开文件，就会触发OpLock。此时我们修改重解析点，将`C:\test`链接至`C:\test2`。现在，当释放OpLock后，第二次读取时该程序就会从另一个文件读取出内容。

这种方法的应用场景在哪？其实很容易想到，比如我们可以让目标检查第一个文件（第一次读取）然后执行第二个文件（第二次读取）。这样我们就实现一个文件用来检查，另一个文件用来执行的应用场景。

以上就是我们在漏洞利用中所涉及到的一些背景知识。



## 0x03 漏洞利用

### <a class="reference-link" name="%E7%8E%AF%E5%A2%83%E5%87%86%E5%A4%87"></a>环境准备

环境准备非常重要。首先，我们需要准备好`CreateMountPoint.exe`以及`SetOpLock.exe`这两个工具。

现在需要稍微改变一下Steam的文件结构。我们的目标是修改目录，使得其中包含`Steam.exe`以及`steamclient.dll`，不包含`bin`目录。我们可以通过两种方法完成该任务：

**方法1**

在Steam根目录中重命名/移动`bin`目录，就这么简单（Steam为所有账户都开放了该目录权限）。

**方法2**

在`HKLM\SOFTWARE\Wow6432Node\Valve\steam`注册表项中，将`InstallPath`的值修改为我们的目录路径，然后从原始的Steam目录中将`Steam.exe`以及`steamclient.dll`拷贝到该目录中。

我们通过任意一种方法构造出`C:\Steam`目录（这里可以选择任意路径）。现在我们需要在其中创建`b1`、`b2`、`b3`以及`b4`目录。我们将`steamservice.dll`拷贝到前3个目录（该dll位于Steam安装目录的`bin`目录中），然后使用相同名称构造出一个dll（`steamservice.dll`），拷贝到`b4`目录中。DLL的构造方法可以参考下文。

启动两个Windows控制台，现在我们的利用环境已准备就绪。

### <a class="reference-link" name="%E4%BA%A4%E6%8D%A2%E6%96%87%E4%BB%B6"></a>交换文件

根据前面的环境准备要点，大家应该能猜到我们准备使用前文提到的BaitAndSwitch技术。

ProcMon的输出结果如下所示：

[![](https://p3.ssl.qhimg.com/t01b12eceaf5cf8f60e.png)](https://p3.ssl.qhimg.com/t01b12eceaf5cf8f60e.png)

当Steam Client Service启动时，我们通常可以在ProcMon中看到上图所示日志。这里简单描述一下，首先目标服务会将dll拷贝到`C:\Program Files (x86)\Common Files\Steam`目录中，然后加载该dll。我们可以让Steam从`C:\Steam\b4`拷贝我们的dll，不幸的是，Steam首先会执行检查操作，判断程序库的是特征否正常，避免dll劫持攻击。

这里我准备逐个步骤描述漏洞利用过程，相同操作的步骤会归在一个组中。在每个步骤中，我们要注意需要执行的程序、执行的位置以及执行后的结果（前面启动的两个Windows控制台分别为“cmd1”以及“cmd2”）.

具体步骤如下：

1）创建`C:\Steam\bin`目录，在cmd1中执行如下命令：

```
CreateMountPoint.exe С:\Steam\bin C:\Steam\b1
```

2）在cmd1中设置OpLock：

```
SetOpLock.exe C:\Steam\b1\steamservice.dll
```

3）运行Steam Client Service。在cmd1中，可以看到我们捕捉到了对目标文件的访问。

4）删除`C:\Steam\bin`，在原位置创建`C:\Steam\bin`目录，然后在cmd2中执行如下命令：

```
CreateMountPoint.exe С:\Steam\bin C:\Steam\b2
```

5）在cmd2中设置OpLock：

```
SetOpLock.exe C:\Steam\b2\steamservice.dll
```

6）在cmd1中释放OpLock。在cmd2中我们可以捕捉到对该文件的访问。

7）删除`C:\Steam\bin`，在原位置创建`C:\Steam\bin`，在cmd1中执行如下命令：

```
CreateMountPoint.exe С:\Steam\bin C:\Steam\b3
```

8）在cmd1中设置OpLock：

```
SetOpLock.exe C:\Steam\b3\steamservice.dll
```

9）在cmd2中释放OpLock。可以在cmd1中捕捉到对该文件的访问。

10）删除`C:\Steam\bin`，在原位置创建`C:\Steam\bin`，然后在cmd2中执行如下命令：

```
CreateMountPoint.exe С:\Steam\bin C:\Steam\b2
```

11）在cmd2中设置OpLock：

```
SetOpLock.exe C:\Steam\b2\steamservice.dll
```

12）在cmd1中释放OpLock。可以在cmd2中捕捉到对该文件的访问。

13）删除`C:\Steam\bin`，在原位置创建`C:\Steam\bin`，然后在cmd1中执行如下命令：

```
CreateMountPoint.exe С:\Steam\bin C:\Steam\b3
```

14）在cmd1中设置OpLock：

```
SetOpLock.exe C:\Steam\b3\steamservice.dll
```

15）在cmd2中释放OpLock。在cmd1中可以捕获到对该文件的访问。

16）删除`C:\Steam\bin`，在原位置创建`C:\Steam\bin`，然后在cmd2中执行如下命令：

```
CreateMountPoint.exe С:\Steam\bin C:\Steam\b4
```

17）在cmd1中释放OpLock。

虽然整个过程看起来比较复杂，但核心思想其实很简单：我们要将目标服务对`C:\Steam\bin\steamservice.dll`的前5次访问（总共6次）重定向到不同的目录中（访问顺序分别为：`b1`、`b2`、`b3`、`b2`、`b3`），在第6次访问时重定向到我们自己的payload。

流程图如下所示：

[![](https://p0.ssl.qhimg.com/t0137a4833224ebd9d6.png)](https://p0.ssl.qhimg.com/t0137a4833224ebd9d6.png)

上图中左图是应用程序正常的访问行为，右图是漏洞利用过程中被我们改造过的行为。

### <a class="reference-link" name="%E6%9E%84%E9%80%A0payload"></a>构造payload

在payload构造中，我首先尝试最常用的dll，在`DllEntry`中创建一个交互式控制台。由于dll代码会在Steam Client Service上下文中执行，因此能够拿到服务对应的权限，即`NT AUTHORITY\SYSTEM`。然后执行完利用步骤后，我并没有看到想要的控制台。

在dll加载后，Steam服务会发现程序流程存在异常，因此会在执行dll中的payload前关闭服务。

这里我只能稍微逆向分析一波，发现目标服务会在加载dll后，检查dll中是否存在如下函数：

```
int WINAPI SteamService_RunMainLoop()
void WINAPI SteamService_Stop()

```

此外，目标服务还会调用第一个函数，因此我决定将payload放在这个函数中（这样就能以`NT AUTHORITY\SYSTEM`权限运行交互式控制台）。就这么简单，准备就绪后我就可以重复利用步骤，拿到最高权限的控制台。



## 0x04 总结

其实这些利用过程都可以封装在一个exe中，但我懒得去处理了，大家可以自己尝试一下。大家可以观看[此处视频](https://www.youtube.com/watch?v=ZCHrjP0cMew)了解通过注册表的利用方式，观看[此处视频](https://www.youtube.com/watch?v=I93aH86BUaE)了解通过文件系统的利用方式。

Valve在Beta版客户端中[修复](https://steamcommunity.com/groups/SteamClientBeta#announcements/detail/1599262071399843693)了这个漏洞，当正式版客户端安装更新后，我也会检查漏洞是否修复。

此外，Valve在[HackerOne](https://hackerone.com/valve/policy_versions)上修改了关于LPE的策略，这也是非常不错的一个消息。
