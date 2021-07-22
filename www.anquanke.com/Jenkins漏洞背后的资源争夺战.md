> 原文链接: https://www.anquanke.com//post/id/168299 


# Jenkins漏洞背后的资源争夺战


                                阅读量   
                                **212563**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者f5，文章来源：f5.com
                                <br>原文地址：[https://www.f5.com/labs/articles/threat-intelligence/new-jenkins-campaign-hides-malware--kills-competing-crypto-miner](https://www.f5.com/labs/articles/threat-intelligence/new-jenkins-campaign-hides-malware--kills-competing-crypto-miner)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01493d378df5feee97.png)](https://p2.ssl.qhimg.com/t01493d378df5feee97.png)



F5安全研究人员近期发现了利用未经身份验证的代码执行漏洞对Jenkins自动化服务器进行攻击的威胁活动。这是继我们揭露攻击者利用XMRig挖掘门罗币的攻击活动后，他们又对Jenkins服务器发起的一系列攻击。这起活动中使用了具有15年历史的进程隐藏工具——XHide。通过它来隐藏恶意进程，并且中止在失陷服务器上运行的其他挖矿进程，达到抢占服务器资源的目的。



## 序列化Payload

可以看到，攻击者发送带有恶意payload的请求，通过反序列化漏洞对服务器进行控制。

[![](https://p1.ssl.qhimg.com/t01e814660cad9a161f.png)](https://p1.ssl.qhimg.com/t01e814660cad9a161f.png)

图1：带有序列化Java对象的请求包，其中包含base64编码的恶意payload

序列化对象中包含经过base64编码的字符串，解码后内容如下：

[![](https://p5.ssl.qhimg.com/t011b11382b77d8c1b4.png)](https://p5.ssl.qhimg.com/t011b11382b77d8c1b4.png)

图2：字符串解码后为bash命令

对字符串进行base64解码后得到的命令首先会尝试使用wget下载恶意文件，如果失败，则使用curl进行下载。下载完成后，以bash脚本格式运行该文件。下面我们来看看下载的bash脚本。



## Bash脚本分析

该bash脚本是从中国Git网站GitEE下载的。在作者的git仓库中，只有一个具有单个分支的项目。

[![](https://p2.ssl.qhimg.com/t01aa6b25fb324253f1.png)](https://p2.ssl.qhimg.com/t01aa6b25fb324253f1.png)

图3：攻击者在GitEE上的项目

在过去的三个月（自2018年4月22日以来），对于大部分文件，攻击者都未做跟新。但在7月2日那一周，更新了四个文件。

[![](https://p4.ssl.qhimg.com/t01e909fa57aa6a3b11.png)](https://p4.ssl.qhimg.com/t01e909fa57aa6a3b11.png)

图4：2018年7月2日所在这周，作者对四个文件进行了更新

下载的bash脚本中包含各种命令，而将它的后缀改为.jpg是为了使它和目标服务器上其他文件混在一起，对受害者进行混淆。

脚本中的前几个命令，终止了目标服务器上多个进程。进行分析，可以看出其目的似乎是要避免服务器资源竞争。大多数进程名和已知的挖矿程序名一致。例如： kworker34,sourplum以及其他一些在imf-conference.org公布的挖矿程序。

[![](https://p0.ssl.qhimg.com/t019aadc302714001b6.png)](https://p0.ssl.qhimg.com/t019aadc302714001b6.png)

图5：使用pkill命令杀死其他挖矿进程

接下来使用wget和curl在失陷服务器上下载其他恶意文件。

[![](https://p2.ssl.qhimg.com/t014c5e4db4f7e09668.png)](https://p2.ssl.qhimg.com/t014c5e4db4f7e09668.png)

图6：使用wget和curl下载恶意文件

执行完下载命令后，失陷服务器会多出以下文件：
- a
- config.json
- cron.d
- x
- dir.dir
- h32
- h64
- run
- Java
- upd
- x86_64
如果服务器已感染并部署了其他恶意软件，其进程也已经在系统上运行了，则bash.pid文件会使用命令“cat bash.pid | xargs kill“杀死相关进程，从而安装自己的恶意软件。

接下来，logo.jpg中的最后一条命令，将赋予所有已下载的文件执行权限，然后运行’x’文件。

[![](https://p0.ssl.qhimg.com/t01732bab0a6b418b05.png)](https://p0.ssl.qhimg.com/t01732bab0a6b418b05.png)

图7：对下载的文件赋权并运行‘x’文件



## 持久性技术

文件‘x’的唯一目的就是使’a’文件在后台执行。使用“nohup”命令，即使原始的shell会话断开，’a‘进程也能在系统中保持运行。（参见图8和9）

[![](https://p3.ssl.qhimg.com/t01d90d6e07659a7948.png)](https://p3.ssl.qhimg.com/t01d90d6e07659a7948.png)

图8：使用“nohup”命令使’a‘进程持续运行

[![](https://p2.ssl.qhimg.com/t015a573d6463f48bb8.png)](https://p2.ssl.qhimg.com/t015a573d6463f48bb8.png)

图9：’a’文件中设置了定时任务并对upd文件进行赋权运行

上图中的代码与2017年10月26日在Stack Overflow论坛上的一段代码非常相似，如图10，其中的文件名及大部分命令都是相同的，只是无法确认作者。

[![](https://p0.ssl.qhimg.com/t012222035b6fa72480.png)](https://p0.ssl.qhimg.com/t012222035b6fa72480.png)

图10：Stack Overflow上的代码

在文件’udp’中，通过设置定时任务，每分钟都会检测恶意程序bash.pid的进程是否运行。如果没有运行，则启动该程序。通过这种监测的手段，来防止恶意程序崩溃或被中止。

在另一个定时任务中，每隔6小时，会下载hxxp：//3389.space/lx/logo.jpg。在撰写本文时，该文件已无法下载。

[![](https://p0.ssl.qhimg.com/t0109f736adb68732c6.png)](https://p0.ssl.qhimg.com/t0109f736adb68732c6.png)

图11：程序崩溃或中止时将运行’run’文件

脚本将运行进程隐藏程序（h32或h64分别支持x86和x64架构），并将Java文件名作为参数进行传递。而正在运行的进程的进程ID会保存到bash.pid中。



## 进程隐藏

在此次攻击活动中，攻击者使用了Schizoprenic Xnuxer Research在2002年发布的进程隐藏工具XHide.

[![](https://p4.ssl.qhimg.com/t01b475ce77d4589644.png)](https://p4.ssl.qhimg.com/t01b475ce77d4589644.png)

图12：XHide工具菜单栏

通过对h32和h64的分析，我们弄清楚了XHid如何隐藏进程的原始命令：它并不会修改恶意文件的文件名，而是通过覆盖恶意文件的argv [0]，修改恶意文件的cmdline信息（在linux系统中，位于in /proc/$pid/cmdline）。使用’ps -ax’命令将显示虚假的恶意进程信息。只有使用’ps -a’，才能显示恶意进程真正的信息。因为它是从 /proc/$pid/status对进程信息进行读取。

在这种情况下，运行恶意java ELF文件，虽然会启动/usr/sbin/sshd（SSH服务常用），但很难引起怀疑。这种攻击手法比较古老但难得一见，我们以前从未遇到过这种技巧。一般的攻击者会直接对恶意文件名进行修改，然后运行。



## 挖矿功能

java可执行文件的主要目的是挖掘臭名昭著的门罗币。在菜单中我们可以看到XMRig相关选项，这说明在恶意软件中集成了XMRig挖矿功能。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b81c74101c064bac.png)

图13：恶意文件中集成挖矿功能

虽然攻击者使用了独特的技巧来隐藏并驻存恶意程序，但他并没有对程序进行很好的混淆，我们很轻松的就在恶意程序中找到了钱包地址。

[![](https://p4.ssl.qhimg.com/t0171e1b3c35388ebc8.png)](https://p4.ssl.qhimg.com/t0171e1b3c35388ebc8.png)

图14：矿池地址及钱包地址均为明文



## 追踪

通过查看钱包地址，可以看到迄今为止攻击者的收益。

[![](https://p2.ssl.qhimg.com/t01db4a184d91081efd.png)](https://p2.ssl.qhimg.com/t01db4a184d91081efd.png)

图15：钱包信息

如上图，攻击者已经挖到了超过39枚门罗币，在撰写本文时，其价值约为5,100美元。根据交易记录，我们发现该钱包最早的支付记录是在2018年3月11日。

可以看到挖矿的速率介于50~60KH/s，这说明攻击者使用了几十甚至上百台服务器进行挖矿。

[![](https://p1.ssl.qhimg.com/t01a0976f1281f10900.png)](https://p1.ssl.qhimg.com/t01a0976f1281f10900.png)

图16：挖矿速率说明有多台服务器在同时挖矿



## IOCs

```
a
config.json
cron.d
x
dir.dir
h32
h64
run
Java
upd
x86_64
（这些文件很可能在于/tmp/.tmp/文件夹内，但最好对其他文件夹也进行检测）

logo.jpg:如果该文件为可执行文件，那一定要重点关注。系统管理员可以使用这条命令来搜索此文件：find / -name logo.jpg | xargs file | grep executable

Cronjobs:攻击者设置定时任务，使用curl或wget下载logo.jpg

Processses：可以使用以下命令检测Java进程：pid=$(ps -a | grep java | cut -d " " -f 1); ps -ax | grep $pid
```

当然，关注CPU的使用情况，是发现恶意挖矿行为最简单有效的方法。



## 总结

最近，我们发现了越来越多富有技巧的挖矿活动。例如，在6月，我们遇到了使用中文论坛作为C2服务器下载C#程序进行攻击的事件，除此之外，还发现了攻击者使用两个不同的漏洞，利用VBScript发起攻击。在诸多挖矿活动中，杀死竞争对手挖矿进程的行为很普遍。这说明越来越多的攻击者发现了挖矿有利可图，都想来分一杯羹。攻击者们使用各种新技巧，使得自己能在这场“资源争夺战”中处于优势地位。
