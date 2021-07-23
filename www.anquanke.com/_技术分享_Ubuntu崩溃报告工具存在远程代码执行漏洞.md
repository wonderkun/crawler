> 原文链接: https://www.anquanke.com//post/id/85143 


# 【技术分享】Ubuntu崩溃报告工具存在远程代码执行漏洞


                                阅读量   
                                **94237**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：donncha.is
                                <br>原文地址：[https://donncha.is/2016/12/compromising-ubuntu-desktop/](https://donncha.is/2016/12/compromising-ubuntu-desktop/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t014878b1bccbec8bf9.jpg)](https://p3.ssl.qhimg.com/t014878b1bccbec8bf9.jpg)



翻译：[pwn_361](http://bobao.360.cn/member/contribute?uid=2798962642)

预估稿费：260RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

安全研究人员发现Ubuntu崩溃报告工具存在远程代码执行漏洞，攻击者可能只需要一个恶意文件就能攻陷一个系统。<br>

该漏洞影响所有默认安装的Ubuntu Linux 12.10 (Quantal)及其之后版本的操作系统。

根据Donncha O’Cearbhaill的研究，这个漏洞在用户打开一个特制的恶意文件时，允许命令执行。

该漏洞与Ubuntu默认文件格式所对应的文件处理程序有关。O'Cearbhaill私自在12月9日披露了这个漏洞，该漏洞的补丁已于14日提供。

完整的漏洞利用源代码可以从GitHub([https://github.com/DonnchaC/ubuntu-apport-exploitation](https://github.com/DonnchaC/ubuntu-apport-exploitation))上下载。

这篇文章的灵感来源于Chris Evan的杰出工作exploiting client-side file format parsing bugs in the gstreamer media library。我们将寻找Ubuntu上其它默认文件处理程序可能存在的利用漏洞。我不是一个像Chris 一样的二进制开发大师。所以我只能找那些不需要利用内存损坏的其它漏洞。

**<br>**

**Linux桌面环境中的文件和URL处理程序配置**



类似于GNOME 或KDE一样的桌面环境，包含一系列已知的文件格式和默认的处理程序。当我们打开一个文件时，桌面环境首先会确定这个文件的格式，从而打开一个相符合的应用程序。Ubuntu中“/usr/share/applications/”文件夹下的.desktop文件中，存储着文件处理的默认应用程序列表。我们能看到对于一个特定的文件格式（MIME类型），哪一个应用程序会默认处理它，并将文件名作为传入参数。

列表中的很多软件是那些频繁使用的文件查看软件，如：image viewers, media players, LibreOffice 和Firefox。我们不研究这些常用软件，我们将寻找列表中那些不常用的默认处理软件来进行研究。

GNOME打开所有文件时，会用apport-gtk工具匹配text/x-apport 中的MIME类型。Ubuntu会根据/usr/share/mime/文件夹中对MIME的描述来确定文件的MIME类型。通常文件的扩展名被用于确定文件类型。但是当一个文件扩展名无法识别时，桌面环境可以退回到匹配模式（一组魔法字节串）。

在这个案例中，Apport程序有两个文件扩展，一个是.crash，另一个是一组特殊的魔法字节串。在匹配魔法字节串前，桌面环境首先会试着匹配文件的扩展名。由于Apport程序的崩溃文件描述符有一个字节模式（也就是说这个文件格式是一定的，类型于WORD文件的前多少字节是什么格式，分别代表什么意思），我们在没用.crash文件扩展名的情况下，有可能可以创建一个漏洞利用文件。

一个快速的实验表明，Ubuntu通过apport-gtk可以打开任何不知道文件扩展名的文件，仅仅需要文件以“ProblemType: ”开始。

 [![](https://p3.ssl.qhimg.com/t018eaa5a38399b5734.png)](https://p3.ssl.qhimg.com/t018eaa5a38399b5734.png)

Apport程序看起来是一个不错的研究条件，它默认会被系统安装，并且它是一个文件处理的默认程序。让我们看看利用Apport能做什么。

**<br>**

**对Apport进行审计**



Ubuntu将Apport崩溃处理软件默认安装到了所有的桌面版本中。它包含了一些不同的组件，用于捕捉崩溃报告，显示给用户，并将报告上传给Ubuntu的问题跟踪服务器。在Ubuntu wiki中提供了这些组件的概述。

当系统探测到一个软件发生崩溃时，会调用/usr/share/apport/apport 程序。为了将对系统性能的影响降到最低，在发生崩溃时，Apport只会记录最小的一组信息，比如程序执行路径和一个核心文件的镜像存储。这个最小的崩溃报告会存储到/var/crash/[executable_path].[uid].crash文件中。

GNOME中的“update-notifier”守护程序会利用inotify保持对/var/crash 文件夹的监控。一旦有新的文件，会马上调用/usr/share/apport/apport-checkreports，如果发现这是一个报告文件，apport-checkreports会调用/usr/share/apport/apport-gtk程序将崩溃报告用图形化界面显示给用户。apport-gtk同时也是.crash文件在桌面环境下的处理程序。

apport-gtk会对崩溃文件进行解释，并给用户显示一个最小的崩溃报告。任何使用过Ubunt桌面环境的用户，可能对这个Apport的报告提示信息都很熟悉。

 [![](https://p0.ssl.qhimg.com/t012e4fa6cec3f16fcc.png)](https://p0.ssl.qhimg.com/t012e4fa6cec3f16fcc.png)

**<br>**

**Apport崩溃报告格式**



Apport软件的崩溃报告有它自定义的文件格式，Apport wiki 页面中有这个文件格式的描述。

在这个格式中，可以用来存储相关崩溃信息和当前系统状态的字段有很多。在崩溃发生时，最小的崩溃文件会仅仅存储那些重要的条目，比如ProblemType, ExecutablePath 和 CoreDump。

**<br>**

**向crash文件中注入pytho代码**



Apport会根据不同软件生成的不同报告，提交给不同的Ubuntu Launchpad 项目(Launchpad 是一个提供维护、支持或连络 Ubuntu 开发者的网站平台，由 Ubuntu 的母公司 Canonical 有限公司所架设，用户可以利用该网站的汇报机制来汇报相关软件的 Bugs)。特殊的hook脚本软件包(从/usr/share/apport/package-hooks/文件夹中加载)可以自定义文件内容和崩溃报告的发送目的地。目标项目也可以由崩溃报告中的CrashDB 字段指定。

CrashDB 的配置存储在/etc/apport/crashdb.conf.d文件中。Crash文件中的CrashDB字段可以用于从指定的文件夹中加载这个配置文件。

注意，这里的代码存在问题，些处的代码可以直接从CrashDB 字段中加载CrashDB 配置，而不是从一个本地文件，什么意思呢，注意，意思是CrashDB 字段中存储的可以不是文件路径，而是配置信息本身。此处的代码会首先检查CrashDB 字段中是不是以“｛”开始，如果是，则意味着这里存储的是一个Python程序段，Apport将会调用Python的eval()内建函数，来处理CrashDB 字段中的信息。eval()会将字段中的信息作为传入参数，当成python表达式来处理，这就直接导致了可靠的代码执行。

这段有漏洞的代码是在2012-08-22引进到Apport revision 2464中的。第一个有这个漏洞的Apport是 2.6.1版本，所有ubuntu 12.10和以后的版本中都包含这个漏洞。

**<br>**

**开发漏洞利用程序**



以下是一个最小的崩溃报告文件，并利用上面的crashdb漏洞来执行任意代码，最后打开了一个Gnome计算器：

这段代码可以用.crash 扩展名来存储，或任何ubuntu无法识别的其它扩展名。

Apport 在给用户用图形界面显示一个需要提交的bug报告时，通常会先读取崩溃文件的子字段，但是CrashDB 字段只有在用户确认提交这个bug报告后，才会被解释和执行。然而，当崩溃报告中设置了“ProblemType: Bug”时，apport-gtk会转换到“streamlined Bug”图形化界面，这会直接引起CrashDB 字段的解释和执行，并且是在没有任何用户交互的情况下。

如果崩溃报告中没有Stracktrace 字段的信息，Apport 会花一些时间，试着去收集崩溃进程的信息。这会延迟CrashDB 字段的执行。在利用代码中，我们可以用一个空的Stracktrace 字段绕过去。

Apport 中有很多CrashDB的实施办法， 我选择了“memory”方法，因为这种方法不用将崩溃报告上传到公共错误跟踪服务器。

 [![](https://p0.ssl.qhimg.com/t01342dcc6e6b4699bd.png)](https://p0.ssl.qhimg.com/t01342dcc6e6b4699bd.png)

**<br>**

**加载脚本时的路径遍历**



在ubuntu中，Apport 的hook脚本软件包会安装到/usr/share/apport/package-hooks文件夹下。这些python hook 脚本的加载基于软件包名称。他们允许软件包的维护者从用户的电脑上收集有用的特定软件包的崩溃信息。然而当建立一个软件包hook文件时，崩溃文件中的package字段并没有经过过滤。

这里的代码允许攻击者遍历文件路径，并在系统hook_dirs(/usr/share/apport/general-hooks/ or/usr/share/apport/package-hooks/)文件夹外,执行任意python脚本。_run_hook 函数会将一个hook文件的内容当作python代码来执行。攻击者可以向用户下载的文件中，植入恶意的一个.py文件和一个崩溃文件，来执行攻击代码。这个方案通过Chromium 会非常容易，它会自动下载文件而没有提示。

 [![](https://p5.ssl.qhimg.com/t018249bf4730f052a2.png)](https://p5.ssl.qhimg.com/t018249bf4730f052a2.png)

这个路径遍历漏洞在2007-01-24被引入到了Apport 0.44中，这个版本在ubuntu 7.04中被首次使用。

**<br>**

**利用CrashDB和hook注入漏洞来提权(需要用户交互)**



所有UID小于500的崩溃文件被认为是系统崩溃文件，当打开系统崩溃文件时，“apport-crashreports”会使用PolicyKit 给用户进行提示，并使用root权限。

提示信息通常是“System program problem detected”信息，并没有给用户提供其他崩溃信息。

如果一个使用了UID小于500的崩溃文件，利用这两个漏洞，并会崩溃文件放入到/var/crash文件夹中，并且用户接受了这个提示，代码就会以ROOT权限执行。当然需要用户交互，在产生一个随机的崩溃之后，在任何时间使用Ubuntu的人都会看到这个能将代码提权的提示信息。

 [![](https://p3.ssl.qhimg.com/t01ec786dbfbf5006be.png)](https://p3.ssl.qhimg.com/t01ec786dbfbf5006be.png)

这样的bug允许一个低特权应用程序跨越权限的边界。比如，可以利用一个SQL 注入漏洞，通过 "INTO OUTFILE"语句向/var/crash目录中写入一个恶意崩溃文件，当一个桌面用户登录后，这个恶意的崩溃文件会自动执行。

**<br>**

**结论**



上面的所有漏洞已经通知了Apport 的维护人员，他们在2016年12月14日已经提供了漏洞的补丁。CrashDB 代码注入漏洞被编号为CVE-2016-9949，路径遍历漏洞为CVE-2016-9950，另外一个问题，“重新启动”行为下的任意代码执行漏洞为CVE-2016-9951。

**<br>**

**参考原文**



[https://donncha.is/2016/12/compromising-ubuntu-desktop/](https://donncha.is/2016/12/compromising-ubuntu-desktop/)  

[https://threatpost.com/remote-code-execution-bug-found-in-ubuntu-quantal/122561/](https://threatpost.com/remote-code-execution-bug-found-in-ubuntu-quantal/122561/) 
