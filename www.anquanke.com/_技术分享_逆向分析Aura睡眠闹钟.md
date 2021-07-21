> 原文链接: https://www.anquanke.com//post/id/86889 


# 【技术分享】逆向分析Aura睡眠闹钟


                                阅读量   
                                **74725**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：courk.fr
                                <br>原文地址：[https://courk.fr/index.php/2017/09/10/reverse-engineering-exploitation-connected-clock/](https://courk.fr/index.php/2017/09/10/reverse-engineering-exploitation-connected-clock/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0181c53b1e6fd9f154.png)](https://p4.ssl.qhimg.com/t0181c53b1e6fd9f154.png)

****

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**写在前面的话**

在前几天，我收到了一款名叫**Aura**的设备。这款设备由Withings设计、生产和销售，根据介绍，Aura是一款联网睡眠闹钟。但是Aura并不单纯是一个闹钟，它的内部设计非常棒，它介入了Sporttify音乐流服务，你可以选择官方推荐的歌单或根据自己的喜好来选择睡眠和起床音乐。

除此之外，Aura的内部还集成了各种**传感器**，并能够对用户周围的环境和睡眠参数进行检测和分析。设备的上方有一个LED等，且整个上半部分都支持触控操作，因此Aura就可以通过这套声光系统来模仿日出的亮度变化，并发出悦耳的音乐来减轻人们起床的痛苦。

[![](https://p2.ssl.qhimg.com/t0113dc8e3eb6549aba.png)](https://p2.ssl.qhimg.com/t0113dc8e3eb6549aba.png)

在了解到这些信息之后，我打算对这款设备进行逆向分析，理由如下:

1.       首先，这肯定会非常有趣，而且这个过程中我还可以学到很多新东西。

2.       我想要真正“控制”这台设备，我想让我自己的代码在这台设备上运行。

这篇文章记录了我对Aura进行逆向分析的完整过程，其中包括固件镜像的获取以及远程缓冲区溢出漏洞的利用方法。

注：我已经与厂商取得了联系，并将本文所要描述的安全问题告知了厂商的安全技术人员。实际上，他们之前就已经知道了本文所要介绍的部分安全漏洞，并且正在努力修复剩下的问题。本文不会给大家提供Aura的固件镜像、完整代码文件以及脚本，本文所介绍的内容纯粹出于教育目的。

**<br>**

**初次分析**

首先，我得先了解更多关于Aura硬件的信息。因为Aura其实并不便宜（1200元人民币左右），所要我现在还不想拆开它。所以我打算先查阅一下网上的公开文档【[FCC验证报告](https://fccid.io/XNAWSD01)】，然后对Aura的硬件情况有一个基本的了解。

从内部电路板的图片来看，Aura是由一块**Freescale处理器**驱动的，并且设备运行的是一种嵌入式的Linux操作系统。

[![](https://p4.ssl.qhimg.com/t01f5563fdbad32c2d7.png)](https://p4.ssl.qhimg.com/t01f5563fdbad32c2d7.png)

由于Aura一直会保持联网状态（WiFi），这也是其配置所要求的，所以我使用nmap对该设备进行了一次扫描，最后得到了以下扫描结果：

[![](https://p2.ssl.qhimg.com/t0130792b2b76b13f4a.png)](https://p2.ssl.qhimg.com/t0130792b2b76b13f4a.png)

端口22貌似是一个过滤端口，但这里的SSH服务器仍然是可响应的。当然了，如果没有有效的密码或SSH密钥的话，这台SSH服务器还是没办法正常访问的。

从蓝牙端来看，Aura是可以通过蓝牙发现的。它运行了一台**SDP**服务器，并且会告知我们下列服务正在运行之中：

[![](https://p0.ssl.qhimg.com/t010ace95d6654f1818.png)](https://p0.ssl.qhimg.com/t010ace95d6654f1818.png)

**<br>**

**固件获取**

为了对Aura进行更深入的分析，我需要拿到设备的固件文件。正如之前所说的，我现在可不想拆开它。为此，在固件的更新过程中，我设置了一个MITM代理来嗅探Aura和其服务器之间的网络通信数据。

随后我便发现，该设备似乎使用了HTTP来下载固件镜像文件：



```
GET /wsd01/wsd01_905.bin HTTP/1.1
Host: XXXXXXXXXXXXXXXXXX
Accept: */*
```

**<br>**

**固件镜像分析**

**文件系统提取**

下载的镜像文件内容如下所示，文件数据的开头部分貌似是一个header，我们之后会将其转换为FPKG文件：

[![](https://p4.ssl.qhimg.com/t01575a9a75fc6d5f4a.png)](https://p4.ssl.qhimg.com/t01575a9a75fc6d5f4a.png)

接下来，我们可以使用binwalk迅速找到有价值的比特位数据：



```
$ binwalk wsd01_905.bin | head
 
DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
28            0x1C            UBIFS filesystem superblock node, CRC: 0xBF63BF7E, flags: 0x0, min I/O unit size: 2048, erase block size: 126976, erase block count: 171, max erase blocks: 1000, format version: 4, compression type: lzo
127004        0x1F01C         UBIFS filesystem master node, CRC: 0x8D8C5434, highest inode: 1265, commit number: 0
253980        0x3E01C         UBIFS filesystem master node, CRC: 0x81BCA129, highest inode: 1265, commit number: 0
1438388       0x15F2B4        Unix path: /var/log/core
1444812       0x160BCC        Executable script, shebang: "/bin/sh"
1445117       0x160CFD        Executable script, shebang: "/bin/sh"
1445941       0x161035        Executable script, shebang: "/bin/sh"
```

由此可以看出，Aura下载的文件中包含一个UBIFS镜像（偏移量为0x1C）。有了jrspruitt的脚本【[下载地址](https://github.com/jrspruitt/ubi_reader)】帮助，从UBIFS镜像中提取出文件相对来说还是比较简单的。

[![](https://p0.ssl.qhimg.com/t010f8fa9cd4309f3a0.png)](https://p0.ssl.qhimg.com/t010f8fa9cd4309f3a0.png)

你会发现，原来这个嵌入式Linux系统中的所有文件我们都可以访问到！我做的第一件事情当然就是检查/etc/shadow文件的内容啦！我首先尝试用John the Ripper来破解密码，但几分钟之后我放弃了，因为我感觉密码十分的复杂。

**FPKG文件格式**

既然所有的文件我都能够访问到，所以我们应该可以了解到FPKG结构。跟固件更行以及FPKG文件有关的函数存在于两个共享库中，即libfpkg.so和libufw.so。在进行了一些反编译工作之后，我得到了如下图所示的文件结构。

[![](https://p5.ssl.qhimg.com/t01111af694df61454e.png)](https://p5.ssl.qhimg.com/t01111af694df61454e.png)

关于此类文件结构的介绍可以参考这份【[ksy文件](https://courk.fr/wp-content/uploads/fpkg.ksy)】。

将这种文件结构应用到之前我所获取到的文件中：

[![](https://p0.ssl.qhimg.com/t0113390ce99e145c82.png)](https://p0.ssl.qhimg.com/t0113390ce99e145c82.png)

这份文件是经过签名的，所以我还无法用它来更新我的固件。

**<br>**

**拿到Root SSH访问权**

在得到固件镜像之后，接下来就是要拿到SSH访问权了。我对代码的运行状态进行了观察，然后尝试从中寻找到安全漏洞。

**目录遍历攻击**

其中有一个名叫seqmand的守护进程引起了我的注意。seqmand负责从远程服务器自动下载音频文件，它的工作机制如下：

1.       设备启动时，seqmand会下载一个csv文件：



```
GET /content/aura/sequences-v3/aura_seq_list.csv HTTP/1.1
Host: XXXXXXXXXXXXXXXXXXX
Accept: */*
```

2.       aura_seq_list.csv文件大致如下所示：

[![](https://p4.ssl.qhimg.com/t01e0c216d701ac05a9.png)](https://p4.ssl.qhimg.com/t01e0c216d701ac05a9.png)

3.       对于csv中的每一行，seqmand都会将相应的文件下载到一个临时目录中：



```
download "http://XXXXXXX/content/aura/sequences-v3/WAKEUP_4/v3_audio_main_part_2.mp3" to "/tmp/sequences/WAKEUP_4/v3_audio_main_part_2.mp3"
download "http://XXXXXXX/content/aura/sequences-v3/WAKEUP_4/v3_audio_main_part_1.mp3" to "/tmp/sequences/WAKEUP_4/v3_audio_main_part_1.mp3"
download "http://XXXXXXX/content/aura/sequences-v3/WAKEUP_3/v3_audio_main_part_2.mp3" to "/tmp/sequences/WAKEUP_3/v3_audio_main_part_2.mp3"
```

4.       临时文件最终会被移动到/usr/share/sequences文件夹中。

我将seqmand的HTTP请求重定向到了我自己搭建的HTTP服务器，然后提供了一个自定义的aura_seq_list.csv文件。接下来，我迅速发现了目录遍历攻击也许是可行的。

比如说，如果我使用下列csv文件，其中包含一个test文件以及有效的MD5值：

[![](https://p1.ssl.qhimg.com/t010d279b3f0cce9998.png)](https://p1.ssl.qhimg.com/t010d279b3f0cce9998.png)

seqmand将会完成以下任务：

```
download "http://XXXXXXX/content/test" to "/tmp/sequences/WAKEUP_42/../../../test"
```

我使用一个静态编译的qemu在笔记本电脑上模拟了一个守护进程，并创建了一个/test文件。首先，我想要用我自己的密码重写/etc/shadow文件：

[![](https://p2.ssl.qhimg.com/t01496a13194153fee9.png)](https://p2.ssl.qhimg.com/t01496a13194153fee9.png)

**目录遍历PoC**

在分析的过程中我发现，操作系统运行在一个只读分区中，但其他的部分还是可写的。下面的代码来自于/etc/init.d/prepare_services脚本：

[![](https://p4.ssl.qhimg.com/t01c3e27d14a62ed71f.png)](https://p4.ssl.qhimg.com/t01c3e27d14a62ed71f.png)

/var/service/sshd/的内容如下所示：

[![](https://p2.ssl.qhimg.com/t01f6023e821146edd6.png)](https://p2.ssl.qhimg.com/t01f6023e821146edd6.png)

运行的文件算是一个启动脚本，当服务启动之后该脚本也会被执行，而supervice/目录下的所有程序都将能够与服务进程交互。接下来，我准备重写/var/service/sshd/run脚本。但是这还远远不够，因为该脚本只会在设备启动时运行，所以我根本来不及重写它。我的想办法强制SSH守护进程重启，比如说这样；



```
$ echo k &gt; /var/service/sshd/supervise/control
$ echo u &gt; /var/service/sshd/supervise/control
```

此时我就可以终止并重启sshd服务，并再次运行脚本了。

接下来，我所使用的csv文件如下：

[![](https://p5.ssl.qhimg.com/t0169a6eeafeecc97ad.png)](https://p5.ssl.qhimg.com/t0169a6eeafeecc97ad.png)

我的服务器托管了下列运行文件:

[![](https://p2.ssl.qhimg.com/t018de5762eea086c43.png)](https://p2.ssl.qhimg.com/t018de5762eea086c43.png)

不出所料，攻击是成功的，我也拿到了root SSH访问权，我所使用的脚本可以点击【[这里](https://courk.fr/wp-content/uploads/MITM_seqmand_release.zip)】获取。

**<br>**

**蓝牙与远程代码执行**

通过进一步的分析之后，我在Aura的蓝牙功能中发现了一个安全漏洞，攻击者将能够通该漏洞并利用Aura的蓝牙协议来触发缓冲区溢出漏洞，并对设备实施攻击。

攻击PoC视频：

视频地址：[https://courk.fr/wp-content/uploads/0x00_packet_replay_demo.webm](https://courk.fr/wp-content/uploads/0x00_packet_replay_demo.webm)

如需了解完整的测试过程以及实验结果，请观看下面的演示视频：

视频地址：[https://asciinema.org/a/44cmj41uh1q7lwkp9lrc9clc5](https://asciinema.org/a/44cmj41uh1q7lwkp9lrc9clc5)

**<br>**

**总结**

多亏了Aura的HTTP流量是明文数据，因此我才可以如此轻松地获取到Aura所使用的系统固件，从而我才有可能获取到Aura的root权限并发现了其中的两个安全漏洞。

首先是第一个漏洞，我通过MITM（中间人攻击）获取到了SSH的root访问权，并成功运行了我自己的代码。另一个漏洞则更加严重，在该漏洞的帮助下，攻击者将能够通过蓝牙直接在目标设备商运行自己的恶意代码。

不过别担心，正如本文前面所说的，这里所介绍的漏洞都已经被成功修复啦！由于篇幅有限，详细的漏洞分析过程请参考原文。

<br>

**附京东购买链接：**

[https://item.jd.hk/1979746955.html](https://item.jd.hk/1979746955.html) 

只要2999，Aura睡眠闹钟带回家！
