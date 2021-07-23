> 原文链接: https://www.anquanke.com//post/id/180557 


# Dota威胁活动：挖矿&amp;后门二重奏


                                阅读量   
                                **230221**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者kindredsec，文章来源：kindredsec.com
                                <br>原文地址：[https://kindredsec.com/2019/05/31/dota-campaign-analyzing-a-coin-mining-and-backdoor-malware-hybrid-campaign/](https://kindredsec.com/2019/05/31/dota-campaign-analyzing-a-coin-mining-and-backdoor-malware-hybrid-campaign/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01435c4310ff9a4443.jpg)](https://p2.ssl.qhimg.com/t01435c4310ff9a4443.jpg)



我的个人蜜罐今天中招了，攻击者投递并执行了一个挖矿程序以及两个远控程序。在互联网上，类似的攻击无时无刻都在发生。接下来让我们对这次遇到的挖矿/后门混合攻击一探究竟。本文中所涉及的样本均可在此处[下载](https://github.com/itsKindred/malware-samples/tree/master/20190529sample1_files)，如果有其他问题，可以和我<a>@kindredsec</a>联系。



## 初始攻击

Dota 威胁活动（从文件名中提取的名称，稍后将会看到）会通过SSH口令爆破来获得服务器登录凭证。不幸的是，刚好我的SSH蜜罐包含一个用户名及登录密码均为salvatore的用户。在SSH日志中，可以看到攻击者登录记录：

[![](https://p5.ssl.qhimg.com/t01c637c0d9e3c12e71.png)](https://p5.ssl.qhimg.com/t01c637c0d9e3c12e71.png)

在验证凭证可用后，攻击者会通过SSH执行系统命令。为了避免直接与服务器交互，所有的命令都是通过SSH进行发送的。因为我的蜜罐是带有自定义OpenSSH版本的系统，所以我们可以看到攻击者所执行过的命令，如下图：

[![](https://p5.ssl.qhimg.com/t011f42af3d18cc10f7.png)](https://p5.ssl.qhimg.com/t011f42af3d18cc10f7.png)

首先，攻击者从54.37.70 [。] 249下载了名为**.x15cache**的文件。然后等待了10秒后，执行了此文件。此外，攻击者还将用户密码更改为了随机字符串。

下面让我们看一看**.x15cache**的内容：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a5993ffc3af6171b.png)

**.x15cache**看起来只是一个dropper文件，对环境进行设置后，它会从54.37.70[.]249 下载一个名为dota2.tar.gz（上文提到的命名就是由此而来的）的文件，在这个tar文件的.rsync目录中，似乎包含了大量恶意文件。下图是我的文件检测脚本提取这些文件的过程。

[![](https://p0.ssl.qhimg.com/t0176876c74e6c5ee2e.png)](https://p0.ssl.qhimg.com/t0176876c74e6c5ee2e.png)

继续看.x15cache，接下来它跳转到了.rsync目录，尝试执行./cron和./anacron这两个文件。攻击者在这里使用了“||（或语法）”，所以只有当./cron执行失败时才会执行./anacron。然而./anacron却一直未被执行，这引发了我的思考，我猜测代码应该是这样设计的：

[![](https://p2.ssl.qhimg.com/t010e068d797f3f67d9.png)](https://p2.ssl.qhimg.com/t010e068d797f3f67d9.png)

i686架构对应于32位环境，而x86_64架构则指的是64位环境。因此，看起来cron是64位二进制文件，而anacron是32位二进制文件。使用file命令查看这两个二进制文件的属性，运行结果证实了我的假设：

[![](https://p5.ssl.qhimg.com/t01e00e6b77603100f3.png)](https://p5.ssl.qhimg.com/t01e00e6b77603100f3.png)

知道了这一点，我们就只需要对其中一个文件进行分析即可，因为它们除了架构上的区别，功能是没有什么差异的。



## 二进制文件cron分析

在进行深入的逆向分析之前，让我们来试试看使用strings命令后，是否还能获取一些有用的信息。果然，**“cryptonight”**一下就引起了我的关注。

[![](https://p2.ssl.qhimg.com/t0103e4b1d22f53f3ea.png)](https://p2.ssl.qhimg.com/t0103e4b1d22f53f3ea.png)

根据[wiki](https://en.bitcoin.it/wiki/CryptoNight)可以知道：CryptoNight是一种工作量证明算法，但由于目前还没有专门配套的挖矿设备。因此，目前只能通过普通PC的CPU进行挖矿。

所以，我们知道了这个二进制文件与挖矿有关。让我们看看还有什么其他信息：

[![](https://p0.ssl.qhimg.com/t01ef5706dccfd8a4b6.png)](https://p0.ssl.qhimg.com/t01ef5706dccfd8a4b6.png)

这是门罗币挖矿代理**xmrig**的命令帮助页面。此外，可以看到这个二进制文件的编译时间是2019年5月3日，也就说是不到一个月之前。

目前看来，我们只是在与挖矿打交道。那运行二进制文件，看看是否能从网络流量中找到一些遗漏的信息。

运行二进制文件后，可以看到主机与5.255.86 [。] 129的80端口建立了连接：

[![](https://p2.ssl.qhimg.com/t01b9f8ae15d3787fb2.png)](https://p2.ssl.qhimg.com/t01b9f8ae15d3787fb2.png)

接下里打开tcpdump来捕获这个连接的所有网络流量，然后在Wireshark中对它进行分析，来了解具体情况：

[![](https://p5.ssl.qhimg.com/t01f85f776fd2528a75.png)](https://p5.ssl.qhimg.com/t01f85f776fd2528a75.png)

如上图，主机向服务器发送了一些json数据。可以看到agent(代理)为XMRig，所用的algo（algorithm的简写）为cn(CryptoNight的简写)。看起来我们已经搞清楚了这个挖矿活动的来龙去脉。



## 第二阶段攻击

当然，攻击并未到此为止。在运行完我们刚才分析的命令以及一些各种信息收集指令之后，攻击者在几秒钟之后又发来了新的命令：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016a596271a8a3a1ce.png)

这次，工作路径从/ tmp转到了/ dev / shm目录。切换到该目录后，攻击者会从54.37.70 [。] 249下载文件名分别为rp和.satan的文件。然后，尝试运行sudo以获取root权限，并使用root权限运行dropper文件.satan。接下来，让我们看看.satan文件的内容：

[![](https://p2.ssl.qhimg.com/t016683a01711abd147.png)](https://p2.ssl.qhimg.com/t016683a01711abd147.png)

可以看到，与之前的.x15cache相比，.satan中下载了更多的dropper文件。首先，它创建了一个自启动的systemd配置文件，文件名为srsync。srsync调用了构建在.satan脚本内的/usr/local/bin/srsync.sh。srsync.sh将运行perl脚本rsync.pl及ps.bin（应该是个二进制文件）。rsync.p在/dev/shm/rp目录内（就是上图中与.satan一起被下载的那个目录）。而ps.bin则是通过本脚本（.satan）从托管服务器54.37.70[.]249 上下载的。值得注意的是：在下载挖矿软件时，攻击者将curl命令作为wget命令执行失败时的备用选择，而这里却没有这种操作。这个细节说明可能这两起攻击并非同一人所为。但不管怎样，我们还是先分析一下ps.bin和rsync.pl吧。



## ps.bin分析

运行file命令,可以确认ps.bin确实是二进制文件，准确地说应该是32位二进制文件。

[![](https://p3.ssl.qhimg.com/t017cdee73dfb90ac7d.png)](https://p3.ssl.qhimg.com/t017cdee73dfb90ac7d.png)

和分析cron二进制文件时一样，让我们先运行strings命令，看是否还能获取一些有用的信息

在仔细查看strings命令输出后，我注意到其中提及到了ssh。因此，我决定执行grep for“ssh”，结果如下：

[![](https://p3.ssl.qhimg.com/t01b26b91fd8a236f33.png)](https://p3.ssl.qhimg.com/t01b26b91fd8a236f33.png)

首先可以看到攻击者调用系统命令将一个RSA公钥添加到〜/ authorized_keys文件中（为了便于阅读，截图未将该命令没有截全）。这样就创建了一个SSH后门，此后攻击者就可以使用关联的RSA私钥完成身份验证。此外，我还看到很多对ssh的引用，这些引用看起来似乎是函数名。进一步深挖，我发现更多的线索：

[![](https://p5.ssl.qhimg.com/t010e71c159317dae8f.png)](https://p5.ssl.qhimg.com/t010e71c159317dae8f.png)

首先，请注意对/root/libs/libssh-0.8.2/src/misc.c的调用，这看起来像是经编译后的文件，而且存在于libssh-0.8.2目录下，相当可疑。另外，还要注意对OpenSSH使用的各种文件名的引用。至此，可以判断ps.bin文件似乎是某种可移植的SSH二进制文件，它还将一个密钥注入当前用户的authorized_key文件中。显然，我们发现了一个纯粹的基于SSH的后门。

出于某种原因，虽然此二进制文件可以运行。而且未出现报错信息，但没有产生进程，打开套接字或其他行为。我尝试了64位环境和32位环境，都无济于事。我将进一步分析这个二进制文件，以寻求新的发现，但是，根据它预设的功能进行判断，可以肯定这是一个SSH后门。



## rsync.pl分析

接下来我们来看看srsync中提到的另一个文件rsync.pl。用vim打开它，可以看到文本显示很不友好：

[![](https://p3.ssl.qhimg.com/t01de4177dec0de92fe.png)](https://p3.ssl.qhimg.com/t01de4177dec0de92fe.png)

然而，这很容易解决。eval命令只是要运行这段其实是perl脚本的未封装二进制数据。所以，我们只需要将打印eval ，就可以知道这段代码的实际功能了：

[![](https://p0.ssl.qhimg.com/t01cdefad40b36e62fa.png)](https://p0.ssl.qhimg.com/t01cdefad40b36e62fa.png)

完美，现在我们得到了实际的Perl代码。这个脚本内容非常多，所以我只截取出了最值得注意的部分。如果你想查看整个内容，可以在文章开头提到的github页面上找到它。



## Perl脚本分析

代码一开始，我立即看到了对IP地址的引用，这种操作我以前从未见过：

[![](https://p3.ssl.qhimg.com/t01e0e4a4443de3a43d.png)](https://p3.ssl.qhimg.com/t01e0e4a4443de3a43d.png)

此外，有趣的是，看起来了变量名称似乎是西班牙语，这意味着该恶意软件可能来源于西班牙威胁组织。

接下来，找到程序的主循环：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01744f6d2331883940.png)

总而言之，这段代码的功能是不断地监听来自IRC服务器（我们之前看到的IP）的命令。而parse函数，则用来筛选出服务器端发的命令。功能实现如下：

[![](https://p1.ssl.qhimg.com/t01140d66498f694453.png)](https://p1.ssl.qhimg.com/t01140d66498f694453.png)

我还注意到在向受感染主机发送特定命令时调用了shell函数，我原本可以猜一猜这个函数在这里有什么用，但现在，让我们直接看代码吧：

[![](https://p4.ssl.qhimg.com/t01daa2a53b41e06387.png)](https://p4.ssl.qhimg.com/t01daa2a53b41e06387.png)

实际上，我们看到通过$ comando变量（ comando西班牙语意思为：命令）启动了一条系统命令（开启了反向连接）。因此，看起来我们正在处理的第二个后门是基于IRC实现的。通过netstat命令，我们可以看到通信双方建立的连接：

[![](https://p4.ssl.qhimg.com/t016c5d1b24942fefff.png)](https://p4.ssl.qhimg.com/t016c5d1b24942fefff.png)

让我们来看看是否可以捕获到这个IRC流量。我开启了tcpdump,然后运行perl脚本，通过wireshark对捕获的流量进行了分析。下面是完整的tcp流：

[![](https://p2.ssl.qhimg.com/t0192b05e8789166e1f.png)](https://p2.ssl.qhimg.com/t0192b05e8789166e1f.png)

在IRC流中，可以看到客户端不断地不断尝试获取昵称，一旦成功获取昵称，就将加入一个名为#root的频道。需要注意的是，从服务器banner信息中，我们可以看到这个服务器是在不到一个月前的2019年5月7日创建的，与编译挖矿二进制文件的时间大致吻合。

再回到Perl代码，可以看到其中似乎还有一些“特殊”功能，例如下载和端口扫描：

[![](https://p3.ssl.qhimg.com/t01ef52ba96c4fc0ec1.png)](https://p3.ssl.qhimg.com/t01ef52ba96c4fc0ec1.png)

在最后，好像还有某种DoS攻击代码：

[![](https://p0.ssl.qhimg.com/t0131e698686793ef66.png)](https://p0.ssl.qhimg.com/t0131e698686793ef66.png)

当然，这个脚本还有很多内容，感兴趣的话你可以自行研究; 我就不在此一一分析了。



## 总结

虽然这种攻击已经司空见惯了，但这起Dota威胁活动的特别之处在于用了2种方式来实现持久性，并且丢弃了特别多的文件。虽然看起来挖矿行为和后门/持久性似乎是由不同的攻击者进行的，但最终，经过分析可以看出这两起攻击是出自同一攻击者所为。希望你看完本文有所收获，如果有任何问题，请随时在Twitter<a>@kindredsec</a>上与我联系！



## 哈希（MD5）

```
.satan：36e692c1e58b53f54ae4966d15fdfa84
rsync.pl：52a422722c479d8c5483d2db9267e4cd
ps.bin :04d0658afae3ea7b0fdaf6a519f2e28c
dota2.tar.gz：2cfb1ad304940ae7e3af954d5c1d1363
.x15cache： 6d6fb279bb78b25413a441e4bfd3ded9
cron： fdb085727694e327c8758061a224166b
anacron： 2c15d9bcd208c9446b14452d25d9ca84
```
