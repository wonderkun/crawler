> 原文链接: https://www.anquanke.com//post/id/83255 


# Blackphone的漏洞允许攻击者获取手机的控制权


                                阅读量   
                                **58798**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.sentinelone.com/blog/vulnerability-in-blackphone-puts-devices-at-risk-for-takeover/](https://www.sentinelone.com/blog/vulnerability-in-blackphone-puts-devices-at-risk-for-takeover/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01312bdb0d6be2e858.png)](https://p2.ssl.qhimg.com/t01312bdb0d6be2e858.png)

        研究人员发现，[Blackphone](https://en.wikipedia.org/wiki/Blackphone)的调制解调器中存在安全漏洞，这将使得这一加密设备有可能受到黑客的攻击。

        Blackphone被誉为是当今安全性最高的智能手机。不幸的是，无论一款系统在设计时采用了多么安全的机制，它仍然是存在安全漏洞的。最近，我们在Blackphone中发现了一个漏洞，这个漏洞将允许攻击者远程控制手机的调制解调器。

        随着SGP技术的发展，再加上Blackphone可以向用户提供应用程序的完整控制权限，SilentCircle旗下的全资子公司还为Blackphone的用户提供了Silent Phone以及Silent Text等隐私保护服务，这些服务能够对通信信息进行加密，以保证没有人可以窃听用户的语音通话信息、视频数据，以及文字消息。

        在进行了一系列逆向工程分析之后，我们发现在Blackphone（BP1）中有一个socket是开放的，而且是可以进行外部访问的。

```
shell@blackphone:/dev/socket $ ls -l at_pal
srw-rw-rw- radio system 2015-07-31 17:51 at_pal
```



        在互联网中，几乎没有关于这个socket的任何信息－除了关于SELinux在安卓操作系统上所使用的file_contexts的相关信息。它似乎是为Nvidia Shield平板电脑所设计的，因为只有这一款配备了Icera调制解调器的安卓设备目前还在广泛使用中，而且Nvidia公司也已经停止生产这种设备了。在进行了进一步的分析和研究之后，我们发现了几款应用程序，这几款应用程序能够跟这个socket进行交互，尤其是其中的agps_daemon，它可以将一个普通shell/app用户的权限提升成system/radio用户才有的权限。

        在我们进行逆向分析之前，我们查看了系统日志，从中我们发现agps_daemon给我们提供了很多非常有趣的信息：

```
I/AGPSD ( 219): agps_PortParseArgs: Getting property (agpsd.dev_path=/dev/ttySHM3) from environment 
I/AGPSD ( 219): agps_PortParseArgs: Getting property (agpsd.socket_path=/dev/socket/at_pal) from environment 
D/AGPSD ( 219): Kernel time: [9.408745] 
D/AGPSD ( 219): vendor/nvidia/tegra/prebuilt/ceres/../../icera/ril/agpsd/agps_daemon.c Version : 1.12 
D/AGPSD ( 219): vendor/nvidia/tegra/prebuilt/ceres/../../icera/ril/agpsd/agps_daemon.c Built Dec 2 2014 12:00:30 
D/AGPSD ( 219): agps_uplinkThread: Entering 
I/AGPSD ( 219): open_tty_port: Opening /dev/ttySHM3 
I/AGPSD ( 219): agps_downlinkThread: Entering
```



        根据系统日志所显示的信息，这很明显就是关于Nvidia Icera调制解调器的二进制功能代码，它会监听“socket_path”( /dev/socket/at_pal),并且还会打开一个tty_port端口。我们在IDA Pro中打开这个agps_daemon之后，这些信息很快便能够得到确认。我们可以看到，这种特权进程不仅能够监听at_pal socket，而且还能够将socket接收到的数据写入ttySHM3端口。在我们对这段二进制代码进行了分析之后，我们还发现调制解调器的无线电信号一致都在监听ttySHM3端口。这也就意味着，我们发现了一种能够直接与调制解调器进行通信的方法！而且我们也证实了，我们可以直接在shell命令行中运行agps_daemon来完成通信操作。你可以从下图看到，我们在代码中开启了一个名为“test”的线程：

[![](https://p5.ssl.qhimg.com/t0182a1602ebe035542.png)](https://p5.ssl.qhimg.com/t0182a1602ebe035542.png)

        在命令行中运行这段二进制代码之后，可以看到我们所输入的“虚假“命令已经被发送至了调制解调器之中。这样一来，攻击者不仅能够以shell用户的身份进行操作，而且还可以通过无线电向调制解调器发送命令。更加可怕的是，攻击者很有可能通过一个拥有网络访问权的安卓应用程序来向调制解调器发送命令。

        因为命令起始于“AT”，而且这段命令看起来像是一段经过修改的Hayes命令，所以我们决定使用谷歌来搜索代码组合，因为我们希望发现更多有趣的使用方法。与此同时，我们还将设备中的所有文件全部提取了出来，并且在这些文件中搜索带有“AT”风格的代码。在这一步骤的操作中，我们发现/system/bin/fild中的二进制代码似乎可以打开socket的/dev/ttySHM3端口，而且还可以加载/system/lib/libicera-ril.so中的共享代码库文件。在我们对这两个二进制代码进行了分析之后，我们很轻松地找到了一些可用的代码，包括下列非常有意思的“AT”代码：

```
AT+CMUT – 将调制解调器设为静音(或开启提醒)(防止提示音)
ATD – 启用或禁用拨出电话的ID
AT+CMGT + AT+CMGS – 发送安卓设备不可见的文字短信
AT+CCFC – 设置设备的呼叫转移,以防止来电信息在设备上显示
AT+CSCS + AT+CUSD – 发送USSD代码
```



        除了上述列出的代码之外，还有很多看似不规范的代码，而且这些代码还可以执行很多设备不可见的任务。在进行了进一步的分析和研究之后，我们还发现了很多代码路径，攻击者可以利用这些信息来进行下列操作：

        －发送和接受文字消息（这一操作既不会在安卓的主界面中显示出来，而且也不会给用户任何的通知和提示）

        －进行拨号或连接（在这一操作中，安卓的UI界面会弹出拨号对话框，但此时的安卓系统将处于假死状态，而且通话无法直接挂断，必须通过与调制解调器的交互才可以将电话挂断）

        －检测手机的电话呼叫状态（检测当前呼叫的电话号码，以及当前通话是呼入还是呼出）

        －重置APN／短信中心／电源选项等设置

        －强制设备与其它号码进行会议电话

        －将调制解调器设置为静音

        －强制设置caller ID<br>                 －“攻击”调制解调器（硬重启后需要对调制解调器进行恢复操作）

        －找到最近的基站进行连接

        －注册呼叫转移号码（在有电话呼入时，Blackphone将不会给予用户任何的提示，来电者也不会被告知他们的通话被转接了）

        当然了，还有很多其他的攻击方法，而且还有某些部分的代码是可以进行利用的，在这里我们就不一一列举了。

        当我们验证了这些分析结果之后，我们就申请了相应的CVE漏洞编号，并与SilentCircle公司进行了联系。他们要求我们向Bugcrowd社区提交这些发现。这一漏洞的编号为CVE-2015-6841，在Bugcrowd社区漏洞奖励计划的帮助下，这些问题已经得到了解决，相应的漏洞也得到了修复。

        这个漏洞告诉我们，针对现代智能设备的攻击面是非常广而深的。这也对安全专家们提出了更高的要求。首先，即便是最“安全”的系统，也是会存在漏洞的，是有可能遭受黑客攻击的。其次，如今的设备都在不断引入第三方厂商所提供的技术（例如硬件，驱动程序，软件库等等），这就使得漏洞的检测和修复过程变的更加的困难。最后一点，几乎所有的漏洞都需要某些恶意软件以进行远程利用。所以，当一个异常源通过一个看似合法的请求来执行系统函数时，如果能够对设备的处理过程进行监视，那么我们将能够更快地检测到非法操作，而且也能够提升我们的应急反应速度。

        事件时间轴

            2015-08-25 – 联系供应商，供应商要求通过Bugcrowd提交漏洞信息，我们向Bugcrowd提交了漏洞信息，并申请了CVE编号。

            2015-09-04 – Bugcrowd对问题进行了分析和分类

            2015-09-10 – MITRE CERT将这个漏洞定为CVE-2015-6841

            2015-09-30 – 供应商确认并同意提交漏洞信息

            2015-11-02 – 问题得到了解决, 并给予了美元奖励，供应商修复了相应漏洞

            2015-12-07 – 用于修复这一漏洞的RC3 1.1.13补丁正式发布

**        特别鸣谢**

        感谢Caleb Fenton, Jacob Soo以及Jon Sawyer所提供的帮助。感谢SilentCircle的CSO @netsecrex对漏洞披露过程的持续关注。感谢Bugcrowd社区在我们披露漏洞信息的过程中所提供的帮助。
