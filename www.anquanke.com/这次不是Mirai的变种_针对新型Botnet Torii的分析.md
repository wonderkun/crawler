> 原文链接: https://www.anquanke.com//post/id/160921 


# 这次不是Mirai的变种：针对新型Botnet Torii的分析


                                阅读量   
                                **218562**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Avast，文章来源：avast.com
                                <br>原文地址：[https://blog.avast.com/new-torii-botnet-threat-research](https://blog.avast.com/new-torii-botnet-threat-research)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0127187da0d4e3fda5.jpg)](https://p5.ssl.qhimg.com/t0127187da0d4e3fda5.jpg)



## 概述

2018年是Mirai和QBot变种不断涌现的一年。任何一个脚本小子，都可以对Mirai源代码稍作修改，给它起上一个新名称，然后将其作为新的僵尸网络发布。

在过去的一周里，我们一直在监测一个新型的恶意软件，我们称之为Torii。与Mirai和其他目前已知的僵尸网络不同，它使用了一些比较高级的技术。

与绝大多数IoT僵尸网络不同，这一新型的僵尸网络在成功入侵设备之后，会增强其隐蔽性和持久性。它不会像一般的僵尸网络那样，攻击网络中的其他设备，也不会挖掘加密货币。相反，它具有一系列非常全面的功能，可以用于泄露敏感信息。其具有的模块化架构，能使用多层加密通信，获取命令或可执行文件并执行。

此外，Torii可以感染多种架构的设备，并具有良好的兼容性，包括MIPS、ARM、x86、x64、PowerPC、SuperH等，是目前为止我们所见过的兼容范围最广的恶意软件。

由于我们在持续监测这种威胁，根据监测结果，我们发现其自2017年12月以来就开始活动，甚至活动时间可能更早。

最后，我们对[@VessOnSecurity](https://github.com/VessOnSecurity)的研究成果表示感谢，他在Twitter上发表了一篇关于该样本的分析，他是从自己的蜜罐上获取到的这一样本。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.avast.com/hs-fs/hubfs/Vess-on-security-tweet.png?t=1538013373318&amp;width=400&amp;name=Vess-on-security-tweet.png)

根据这位安全研究人员的说法，这一僵尸网络从Tor出口节点对他的蜜罐进行了Telnet攻击，因此我们决定将这个僵尸网络命名为Torii。

在本文中，我们重点说明迄今为止对这一僵尸网络的了解，分析其传播过程、各个阶段以及一些重要特征。

目前，针对该僵尸网络的分析仍在进行中，如果有更进一步的调查结果，我们也会及时更新。

接下来，让我们从感染向量开始。



## 对初始Shell脚本的分析

在感染链的开始阶段，首先针对目标设备的弱口令进行Telnet攻击，然后执行初始Shell脚本。这一脚本与IoT恶意软件所经常使用的脚本完全不同，因为它更为复杂。

脚本首先尝试检测目标设备的体系结构，然后尝试下载相应的Payload。Torii支持的体系结构非常多，包括基于x86_64、x86、ARM、MIPS、Motorola 68k、SuperH、PPC的设备，支持多种位宽和字节顺序。这样一来，Torii的感染范围就非常广泛，能够在众多常见的设备上运行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.avast.com/hs-fs/hubfs/torii-2.png?t=1538013373318&amp;width=826&amp;name=torii-2.png)

恶意软件使用多个命令下载二进制Payload，其执行的命令包括：wget、ftpget、ftp、busybox wget和busybox ftpget。它还同时使用多个命令，使其传递Payload的可能性达到最大。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.avast.com/hs-fs/hubfs/torii-3.png?t=1538013373318&amp;width=826&amp;name=torii-3.png)

如果无法使用wget或busybox wget命令通过HTTP协议下载二进制文件，那么它将会采用FTP协议。使用FTP协议时，需要经过身份验证。在脚本中提供了身份验证信息：

用户名：u=”&lt;redacted&gt;“

密码：p=”&lt;redacted&gt;“

FTP端口：po=404

FTP/HTTP服务器IP地址：104.237.218.85（在本文撰写时，该IP地址仍然存在）

通过连接到FTP服务器，恶意软件能实现大量工作：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.avast.com/hs-fs/hubfs/torii-4.png?t=1538013373318&amp;width=520&amp;name=torii-4.png)

完整文件请点击： [https://cdn2.hubspot.net/hubfs/486579/torii_directory_structure.txt?t=1538013373318](https://cdn2.hubspot.net/hubfs/486579/torii_directory_structure.txt?t=1538013373318)

在服务器中，有来自NGINX和FTP服务器的日志、Payload样本、将被感染设备定向到恶意软件所在主机的Bash脚本等。我们将在本文的最后，讨论从日志中发现的内容。首先，先让我们来分析一下在服务器托管的脚本。



## 第一阶段Payload分析（Dropper）

在脚本确定目标设备的架构之后，就会从服务器下载并执行对应的二进制文件。所有这些二进制文件都是ELF格式。在分析这些Payload时，我们发现它们都非常相似，并且仅仅是第二阶段Payload的Dropper。值得注意的是，它们使用了多种方法使第二阶段能在目标设备上尽可能持久化。我们来深入了解其中的细节。

针对本文，我们分析的是x86的样本，其SHA256哈希值为：

0ff70de135cee727eca5780621ba05a6ce215ad4c759b3a096dd5ece1ac3d378

### <a name="%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%B7%B7%E6%B7%86"></a>字符串混淆

由于样本经过混淆，我们首先需要尝试对其进行反混淆。因此，我们深入研究了一些文本字符串，以尝试找到该恶意软件的工作方式。第一和第二阶段中的绝大多数文本字符串都是通过简单的XOR方式进行加密的，并且在运行时需要特定字符串对它们进行解密。我们使用以下IDA Python脚本进行解密：

### <a name="%E5%AE%89%E8%A3%85%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%AE%B5ELF%E6%96%87%E4%BB%B6"></a>安装第二阶段ELF文件

第一阶段的核心功能是安装另一个ELF文件，也就是第二阶段的可执行文件，它包含在第一阶段的ELF文件中。

该文件将会安装在一个伪随机的位置，这个位置是通过组合预先定义好的列表中的内容来生成的，目录列表如下：

文件名列表如下：

通过上面的两个列表，就能生成目标文件的路径。



## 确保第二阶段持久化

然后，Dropper需要确保能够执行第二阶段Payload，并会保证其持久化。该恶意软件的独特之处在于它实现持久化的方式非常强大，至少采用了6种方法来确保文件能够保留在设备上，并且持续运行。恶意软件不是从6种方法中选择一种，而是全部都会执行：

（1）通过向~.bashrc中注入代码，实现自动执行；

（2）通过向crontab中添加“[@reboot](https://github.com/reboot)”子句，实现自动执行；

（3）通过systemd自动执行“System Daemon”服务，实现自动执行；

（4）通过/etc/init和PATH实现自动执行，将自身伪装成“System Daemon”服务；

（5）通过修改SELinux策略管理，实现自动执行；

（6）通过/etc/inittab实现自动执行。

完成后，它会投放自身内部的ELF，也就是第二阶段的Payload。



## 第二阶段Payload分析（Bot）

第二阶段Payload是一个完整的Bot，能够从其C&amp;C服务器执行命令。在Payload中还包含起其他功能，例如简单的反调试技术、数据泄露、多层通信加密等。

此外，第二阶段中发现的许多功能都与第一阶段Payload相同，这样看来很可能二者都是由同一作者创建的。

针对所有版本，第一阶段Payload中的代码几乎是相同的。然而我们在第二阶段中发现，不同硬件架构的二进制文件之间存在差异。为了能够对大多数版本中的核心功能进行分析，我们选取了x86架构版本的Payload，其SHA256哈希值为：

5c74bd2e20ef97e39e3c027f130c62f0cfdd6f6e008250b3c5c35ff9647f2abe

### <a name="%E5%8F%8D%E5%88%86%E6%9E%90%E6%96%B9%E6%B3%95"></a>反分析方法

该恶意软件所使用的反分析方法，不如我们在Windows或移动端恶意软件中看到的方法那么先进，但恶意软件作者仍在持续改进这一部分。

（1）在执行后，将会运行60秒的sleep()函数，可能会绕过简单的沙箱；

（2）通过prctl(PR_SET_NAME)调用，将进程名随机化为“[[a-z]`{`12,17`}`]”（正则表达式），以避免通过进程名称黑名单检测到该恶意软件；

（3）通过从可执行文件中删除符号，加大分析的难度。

当我们首次从恶意服务器104[.]237.218[.]85下载样本时，所下载的样本都包含符号，这样使得分析过程更为建安。但有趣的是，在几天之后，我们下载的版本中已经不包含符号。除此之外，这两个版本之间没有任何差异。这样一来，我们能够判断，恶意软件作者还在持续改进恶意软件，以保护可执行文件难以被分析。

### <a name="C&amp;C%E6%9C%8D%E5%8A%A1%E5%99%A8"></a>C&amp;C服务器

如前文所述，这个组件是一个与C&amp;C服务器通信的Bot。我们使用此前发现用于XOR的密码，对C&amp;C地址再次执行XOR操作，发现似乎每个版本的Torii都包含3个C&amp;C地址。我们所分析的恶意软件，会尝试从以下C&amp;C服务器获取命令：

它尝试与列表中的第一个域名进行通信，如果失败将会转到下一个域名。此外，如果出现失败的情况，它还会尝试通过Google的DNS 8.8.8.8进行域名解析。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.avast.com/hs-fs/hubfs/resolve-cnc-5.png?t=1538013373318&amp;width=1600&amp;name=resolve-cnc-5.png)

自2018年9月15日以来，这三个域名都解析到同一个IP 66[.]85.157[.]90。此外，在同一个IP上托管的其他一些域名也非常可疑：

在同一个IP地址，托管了这么多看起来很奇怪的域名，这一点非常可疑。另外，在此之前，C&amp;C域名是解析到另一个不同的IP地址（184[.]95.48[.]12）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.avast.com/hs-fs/hubfs/cnc-domain-names-6.png?t=1538013373318&amp;width=1411&amp;name=cnc-domain-names-6.png)

通过更深入的挖掘，我们还发现了另一组属于Torii的ELF样本，其中包括3个不同的C&amp;C地址：

它们在此前都解析到相同的IP地址（184[.]95.48[.]12）。并且，press[.]eonhep[.]com自2017年12月8日就开始解析到这一地址。因此，我们认为该恶意软件至少自2017年12月就开始存在，或者可能存在的时间更长。

### <a name="C&amp;C%E9%80%9A%E4%BF%A1"></a>C&amp;C通信

第二阶段通过TCP协议443端口，与这些C&amp;C服务器以及其他加密层进行通信。有趣的是，它使用443端口来迷惑分析人员，因为443是HTTPS端口，而这一恶意软件实际上并没有使用TLS协议进行通信。针对每条消息（包括回复的内容），都会生成一个我们称之为“消息信封”的结构，每个信封都经过AES-128加密，并且其中包含一个MD5校验和，以确保其中的内容没有被修改或损坏。此外，每个信封都包含一条消息流，其中每条消息都通过简单的XOR方法进行加密，这与混淆字符串的加密方式不同。它看起来没有那么强大，因为通信中包含了解密的密钥。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.avast.com/hs-fs/hubfs/torii-7.png?t=1538013373318&amp;width=357&amp;name=torii-7.png)

Torii在连接到C&amp;C服务器时，还会发出以下隐私信息：

（1）主机名；

（2）进程ID；

（3）第二阶段可执行文件的路径；

（4）在/sys/class/net/%interface_name%/address中找到的所有MAC地址及其哈希值，这部分内容形成了被感染用户的独有ID，允许恶意软件作者更容易地进行指纹识别和设备标记，这些内容也会同时存储在本地，其文件名诸如：

GfmVZfJKWnCheFxEVAzvAMiZZGjfFoumtiJtntFkiJTmoSsLtSIvEtufBgkgugUOogJebQojzhYNaqyVKJqRcnWDtJlNPIdeOMKP、VFgKRiHQQcLhUZfvuRUqPKCtcrjmhtKcYQorAWhqAuZuWfQqymGnWiiZAsljnyNlocePAOHaKHvGoNXMZfByomZqEMbtkOEzQkQq、XAgHrWKSKyJktzLCMcEqYqfoeUBtgodeOjLgfvArTLeOkPSyRxqrpvFWRhRYvVcLeNtMKTdgFhwrypsRoIiDeObVxTTuOVfSkzgx等；

（5）uname()调用后获得的详细信息，包括sysname、version、release和machine；

（6）特定命令的输出结果，目的是获取目标设备相关的更多信息。

特定命令如下：

### <a name="C&amp;C%E5%91%BD%E4%BB%A4"></a>C&amp;C命令

在分析代码的过程中，我们发现Bot组件正在与C&amp;C进行通信，并且会在无限循环中不断轮询，询问C&amp;C服务器是否有任何命令需要执行。在收到命令后，它会回复命令执行的结果。每个消息信封中都包含一个特定值，用于指定其命令的类型，在回复内容中也会附带相同的值。目前，我们发现了如下命令类型：

（1）0xBB32：将文件从C&amp;C存储到本地驱动器

接收：从C&amp;C接收的文件存储到本地的位置、文件、MD5校验和

回复：存储文件的文件路径、错误代码

（2）0xA16D：接收C&amp;C轮询的间隔时间

接收：DWORD与C&amp;C通信之间的暂停（Sleep）时间

回复：代码为66的消息

（3）0xAE35：在Shell解释器中执行特定命令，并将输出结果发回C&amp;C

接收：在Shell中要执行的命令（sh -c “exec COMMAND”）、间隔时间（以秒为单位，最大为60）、带有Shell解释器路径的字符串（可选）

回复：包含命令执行内容的输出结果（stdoout+stderr）

（4）0xA863：将文件从C&amp;C存储到特定路径，并将其标志更改为“rwxr-xr-x”使其可执行，然后执行

接收：从C&amp;C接收的文件存储到本地的位置、文件、MD5校验和

回复：存储文件的文件路径、执行该文件后的返回代码

（5）0xE04B：检查本地系统上是否存在特定文件，并返回其大小

接收：要检查的文件路径

回复：文件路径、文件大小

（6）0xF28C：从所选文件F的偏移量O处读取N个字节，并将其发送到C&amp;C服务器

接收：要读取文件（F）的文件路径、QWORD偏移量（O）、DWORD要读取的字节数（N）

回复：文件内容、偏移量、读取的字节大小、读取内容的MD5校验和

（7）0xDEB7：删除指定的文件

接收：要删除的文件名

回复：错误代码

（8）0xC221：从特定URL下载文件

接收：存储文件的路径、URL

回复：存储文件的路径、URL

（9）0xF76F：获取新C&amp;C服务器地址，并开始与其进行通信

接收：？、新域名、新端口号、？

回复：？、新域名、新端口号、？

（10）0x5B77/0x73BF/0xEBF0（可能还有其他代码）：在目标设备上执行Ping或者获取心跳包

接收：特定内容

回复：重复收到的信息



## 对二进制文件sm_packed_agent的分析

在我们对服务器进行分析时，还发现了另一个有趣的二进制文件，我们设法从FTP服务器杉获取了名为“sm_packed_agent”的二进制文件。我们目前没有在服务器上发现这一二进制文件已经被使用的证据，但通过对其功能进行分析，发现它可以用于向目标设备发送任何远程命令。该二进制文件中包含一个使用UPX加壳的GO语言应用程序，其中包含一些有趣的字符串，表明它具有类似于副武器的功能：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.avast.com/hs-fs/hubfs/torii-10.png?t=1538013373318&amp;width=1024&amp;name=torii-10.png)

### <a name="%E4%BD%BF%E7%94%A8%E7%9A%84%E7%AC%AC%E4%B8%89%E6%96%B9%E5%BA%93"></a>使用的第三方库

该二进制文件，使用了以下第三方库：

[https://github.com/shirou/gopsutil/host](https://github.com/shirou/gopsutil/host)

[https://github.com/shirou/gopsutil/cpu](https://github.com/shirou/gopsutil/cpu)

[https://github.com/shirou/gopsutil/mem](https://github.com/shirou/gopsutil/mem)

[https://github.com/shirou/gopsutil/net](https://github.com/shirou/gopsutil/net)

### <a name="%E5%8F%AF%E8%83%BD%E7%9A%84%E6%BA%90%E4%BB%A3%E7%A0%81%E5%90%8D%E7%A7%B0"></a>可能的源代码名称

其可能的源代码名称如下：

/go/src/Monitor_GO/agent/agent.go

/go/src/Monitor_GO/sm_agent.go

其中，可能有一些库滥用了BSD许可证。显然，Torii的作者并不关注侵权问题。

### <a name="%E5%8A%9F%E8%83%BD"></a>功能

sm_agent的功能如下：

（1）在cmdline –p上使用一个带有端口号的参数；

（2）初始化加密，加载TLS、密钥和证书；

（3）创建服务器，并监听TLS连接；

（4）等待以BSON格式编码的命令；

（5）使用命令处理程序，对命令进行处理：

TLS加密、证书和密钥：

（1）Agent使用ChaCha20-Poly1305流密码进行TLS加密；

（2）同一目录下的密钥和证书；

（3）自签名的授权证书ca.crt，签名为Mayola Mednick；

（4）由ca.crt为Dorothea Gladding发布的client.crt；

（5）由ca.crt为Graham Tudisco发布的server.crt和server.key。

由于证书是自签名的，所以使用的名称也显然是虚假的。

Start-agent.sh：

该脚本将会首先终止任何先前启动的sm_packed_agent实例，然后在TCP协议45709端口上运行sm_packed_agent，当出现运行失败的情况会尝试重新运行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.avast.com/hs-fs/hubfs/torii-9.png?t=1538013373318&amp;width=520&amp;name=torii-9.png)

目前，还暂时不清楚Torii作者是如何使用的这项服务，但它非常通用，可以在设备上运行几乎任何命令。因为这应用程序是使用GO语言编写的，所以可以非常容易地重新编译，从而在几乎任何架构上使用。考虑到该文件是在恶意软件分发的主机上运行，说明它很可能是后门，或者是用于组织多台机器的服务。



## 恶意服务器日志分析

最后，我们分析了从Nginx服务器和FTP服务器（104[.]237.218[.]85）上发现的日志。通过这些访问日志，我们可以推断出Torii实际感染了多少客户端，或者有多少客户端试图下载该恶意软件。

在我们撰写此文章时，Torii的作者已经禁用了FTP和Nginx日志记录，但是根据已有的日志，我们可以生成一些简单的统计信息。

根据服务器上面的日志，在9月7日、8日、19日和20日，共有206个IP连接到服务器。

其中，有一个IP地址38[.]124.61[.]111连接该服务器的次数达到了1056393次。

通过查看日志，似乎有人使用了DirBuster-1.0-RC1，尝试分析该服务器的内部结构。事实上，DirBuster通常用于猜测Web服务器的目录和文件名，并且会生成大量请求。其实，这次扫描是完全没有必要的，因为针对Torii这样复杂的恶意软件，有更加有效的方法。

通过扫描38[.]124.61[.]111的端口，我们可以发现有下面几个端口是开启的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.avast.com/hs-fs/hubfs/torii-ports.png?t=1538013373318&amp;width=502&amp;name=torii-ports.png)

在27655端口上，有一个SSH Banner，其内容为：

看上去，这个盒子正在运行Raspbian。

除此之外，我们还可以对FTP服务器日志进行分析。

分析发现，有几个客户端曾连接，并下载了一些没有位于FTP服务器上的文件：

根据我们分析的日志内容，总共有592个不同的客户端，在几天时间之内从该服务器下载文件。需要提醒大家的是，一旦目标设备收到Payload，就会停止连接到下载服务器，转为连接到C&amp;C服务器。因此，我们通过该日志，就可以看到这些日志记录的时间段范围内，有多少网络中的新设备感染了这一恶意软件。

此外，有8个客户端同时使用了HTTP服务器和FTP服务器，这可能是由于HTTP方式下载失败，或是Torii作者在测试Bash脚本和服务器的功能。

由于没有证据，我们无法做出更多的推测。这台服务器可能只是众多感染目标连接的服务器之一，要揭示这个僵尸网络的真实规模，还需要进一步的调查。考虑到所分析的恶意软件的复杂程度，我们认为它可能是为了控制大量不同类型的设备而设计的。



## 结论

尽管我们的研究仍在继续，但目前的结论已经表明，Torii是物联网恶意软件发展过程中的一个重要样本，它的复杂程度已经高于我们此前看到的水平。一旦它感染了某个设备，不仅会泄露设备自身的一些敏感信息，还会通过与C&amp;C的通信允许Torii作者执行任意代码或传递任何Payload。这样一来，Torii就成为了一个可供今后持续使用的模块化平台。此外，由于Payload自身不会扫描其他目标，因此它在网络上非常隐蔽。

我们还将持续进行研究，并及时披露新发现的成果。
