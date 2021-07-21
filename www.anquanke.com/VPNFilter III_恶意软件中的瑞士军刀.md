> 原文链接: https://www.anquanke.com//post/id/160861 


# VPNFilter III：恶意软件中的瑞士军刀


                                阅读量   
                                **207242**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Talos，文章来源：talosintelligence.com
                                <br>原文地址：[https://blog.talosintelligence.com/2018/09/vpnfilter-part-3.html](https://blog.talosintelligence.com/2018/09/vpnfilter-part-3.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/dm/1024_325_/t01655fad6faad95a91.jpg)](https://p2.ssl.qhimg.com/dm/1024_325_/t01655fad6faad95a91.jpg)



## 一、前言

[VPNFilter](https://blog.talosintelligence.com/2018/05/VPNFilter.html)是一款多阶段的模块化框架，已经影响全球数十万台网络设备，现在这个框架已经具备更为强大的功能。最近思科Talos发现这款恶意软件中新增了7个模块（第3阶段VPNFilter模块），极大扩展了自身功能，还能以已突破网络设备为据点攻击端点设备，此外还包含数据过滤以及多重加密隧道功能，可以隐蔽命令与控制（C2）及数据传输流量。虽然我们以及合作伙伴的研究成果已经能够抵御来自VPNFilter的大部分威胁，但如果有些设备没有部署针对性防御方案，这款恶意软件依然可以隐蔽于实际环境中。

Talos几个月以来一直在研究VPNFilter，并在5月份发布了最初的[研究报告](https://blog.talosintelligence.com/2018/05/VPNFilter.html)，在6月份介绍了该框架使用的[其他模块](https://blog.talosintelligence.com/2018/06/vpnfilter-update.html)。在后续研究过程中，我们研发了一项技术，能够识别MikroTik网络设备所使用的某个关键协议，以便搜寻攻击者可能利用的攻击方法。

在跟踪VPNFilter的感染情况时，我们发现MikroTik网络设备受到了来自攻击者的严重威胁（特别是在乌克兰境内的设备）。由于这些设备对攻击者的目标来说似乎非常重要，因此我们想进一步理解攻击者对这些设备的具体利用方式，我们还学习了MikroTik的Winbox管理工具所使用的具体协议。在本文中，我们想与大家分享我们研究该协议的出发点和具体方式，以及我们开发的一款解码器工具，安全社区可以使用该工具来分析该协议，寻找潜在的恶意攻击行为。

VPNFilter非常复杂，所有人以及所有组织都应该对此保持高度重视。只有高级的、有组织的防御方才能对抗这类威胁，并且VPNFilter的规模已经非常庞大，我们永远不能忽视这些新发现。



## 二、新增功能

新发现的VPNFilter第三阶段模块大大拓展了我们对已知威胁的理解深度，这些模块新增了如下功能：

1、可以用来映射网络，攻击与VPNFilter控制的设备相连接的端点。

2、通过各种方式混淆以及/或者加密恶意流量，包括C2流量以及数据通信流量。

3、利用多款工具来识别其他受害者，攻击者可以利用已被VPNFilter突破的网络设备为据点来访问这些受害者，实现网内横向渗透，也能用来识别攻击者感兴趣的其他网络的边际设备。

4、支持构建分布式代理网络，可以在未来不相关的攻击活动中使用，用来混淆攻击源的真实流量，让外界误以为攻击来自于先前被VPNFilter控制的设备。

逆向分析这些模块后，我们可以确认恶意软件的具体功能。在此之前，我们只能根据感知数据来分析这些功能，这样难免会出现一些纰漏。

比如，我们之前注意到被VPNFilter控制的设备会扫描一大段IP地址空间，寻找受VPNFilter攻击者利用方法影响的其他设备。现在我们可以讨论负责这类行为的特定第三阶段模块。

在分析这些扩展模块后，我们得以进一步了解VPNFilter相关的全部功能。



## 三、新增模块

如前文所述，Talos识别出了如下7个新增模块，这些模块极大拓展了VPNFilter的功能：

[![](https://p0.ssl.qhimg.com/t01011bd6ab0a334c75.png)](https://p0.ssl.qhimg.com/t01011bd6ab0a334c75.png)

下文我们会逐一介绍这些模块。

### <a name="htpx%EF%BC%88%E7%AB%AF%E7%82%B9%E6%94%BB%E5%87%BB%E6%A8%A1%E5%9D%97%E2%80%94%E5%8F%AF%E6%89%A7%E8%A1%8C%E6%96%87%E4%BB%B6%E6%B3%A8%E5%85%A5%EF%BC%89"></a>htpx（端点攻击模块—可执行文件注入）

htpx是VPNFilter的第三阶段模块。该模块与我们之前[分析](https://blog.talosintelligence.com/2018/06/vpnfilter-update.html)的ssler模块共享部分代码，根据二进制文件中的字符串信息，我们发现该模块主要以开源代码为基础。典型的例子为[lipiptc.c](https://git.netfilter.org/iptables/tree/libiptc/libiptc.c)，该代码为Netfilter中的一部分：

[![](https://p4.ssl.qhimg.com/t01f50bd72dd442ee9d.jpg)](https://p4.ssl.qhimg.com/t01f50bd72dd442ee9d.jpg)

图示：htpx（左侧）与ssler（右侧）中的字符串对比

htpx中的主功能函数负责设置iptables规则，以便将流向TCP 80端口的数据转到到本地服务器的8888端口。恶意软件首先加载能够进行流量管理的内核模块实现流量转发，通过insmod命令完成相关模块（Ip_tables.ko、Iptable_filter.ko以及Iptable_nat.ko）的加载。

随后，htpx模块使用如下命令来隐蔽转发流量：

恶意模块还会定期检查这些规则是否依然存在，定期执行规则删除代码，然后再重新添加这些规则。此外，该模块还会创建一个临时文件：/var/run/htpx.pid。

之后该模块会生成如下HTTP请求：

在我们对htpx模块的分析过程中，我们无法捕获来自C2基础设施的响应数据，因此无法观察其他模块的行为。分信息该模块的二进制文件后，我们发现该模块会检查HTTP通信数据，识别其中是否存在Windows可执行文件。如果满足该条件，则会标记可执行文件并将其加入某个表中。可以肯定的是，攻击者可能会利用该模块来下载二进制载荷，动态修改通过当前控制设备的Windows可执行文件。

### <a name="ndbr%EF%BC%88%E5%A4%9A%E5%8A%9F%E8%83%BDSSH%E5%B7%A5%E5%85%B7%EF%BC%89"></a>ndbr（多功能SSH工具）

ndbr模块具备SSH功能，也能够扫描其他IP地址的端口状态。该模块使用了dropbear SSH服务端以及客户端，是dbmulti（2017.75版）的修改版。我们已确定该模块对标准的dropbear功能做了若干修改。

第一处改动位于dbmulti应用中。这款典型的应用可以充当SSH客户端以及SSH服务端角色，能够使用SCP执行数据传输任务、生成或转换密钥，具体功能由程序名或者传入的首个参数来决定。ndbr模块将生成或转换密钥的功能替换为网络映射功能（比如端口扫描）以及名为ndbr的另一个函数。

与原始的dbmulti应用类似，ndbr模块的具体功能取决于程序名或者传入的第一个参数。ndbr可以接受的参数具体为dropbear、dbclient、ssh、scp、ndbr以及nmap。下面我们给大家具体介绍一下这些参数。

DROPBEAR

dropbear命令可以指示ndbr模块以SSH服务器形态运行。原始的dropbear代码使用了默认的SSH端口（TCP/22）来监听传入连接。然而ndbr模块修改了这部分代码，使用默认的TCP/63914端口进行监听。此外，该模块还修改了负责处理主机密钥文件（keyfile）的dropbear代码。默认的密钥文件路径已经修改为/db_key，但ndbr模块并没有释放该文件，而是修改buf_readfile这个dropbear函数，当文件名参数等于/db_key时，就会从内存中直接加载匹配的密钥。

该模块并没有使用基于密码的认证方式，而是修改dropbear服务端，通过匹配的公钥进行身份认证，该密钥同样内嵌在ndbr可执行文件中。修改过的代码中存在一个bug，无法处理使用不正确公钥的连接请求，此时认证失败会导致ndbr SSH服务端卡死，陷入无限循环中，然而客户端并不知道认证失败结果。此时我们无法获取能够通过ndbr SSH服务器认证的正确密钥，ndbr模块中内嵌的密钥（比如/db_key以及/cli_key）并不是正确密钥，我们也没有在其他VPNFilter相关应用中找到对应的密钥。

DBCLIENT（SSH）

如果传入dbclient或者ssh参数，ndbr模块就会化身为标准的dropbear SSH命令行接口客户端，但修改了默认的选项。与dropbear服务端命令所使用的默认密钥文件参数一样，dbclient/ssh命令同样具有默认的标识文件：/cli_key。此时我们并不知道dbclient（SSH客户端）原本想连接的是哪个目的地址。

NMAP

如果传入nmap参数，ndbr模块就会对某个IP或者某段IP空间进行端口扫描，具体命令为：

NDBR

如果传入ndbr参数，那么ndbr模块就会根据传入的其他参数，执行3种操作中的一种。这种场景中SSH命令使用的是前文提到的默认密钥（即/db_key和/cli_key）。

第三个参数必须以start开头，否则ndbr模块就会执行卸载操作。

如果使用如下参数运行ndbr模块：

那么就会执行如下dropbear SSH命令：

此时dropbear SSH客户端就会连接到某个远程主机，并执行srv_ping命令，该命令很有可能用来在C2服务器上注册受害者信息。

如果使用如下参数运行ndbr模块：

那么就会运行SSH服务端（如前文所述），开始监听特定端口：

如果使用如下参数运行ndbr模块：

那么就会执行如下dropbear命令，开启远程端口转发：

### <a name="nm%EF%BC%88%E7%BD%91%E7%BB%9C%E6%98%A0%E5%B0%84%E5%99%A8%EF%BC%89"></a>nm（网络映射器）

nm模块可以用来扫描和映射本地子网。该模块会遍历所有接口，通过ARP扫描发现该接口对应IP所属子网中的所有主机。一旦收到ARP响应包，nm就会向探测到的主机发送一个ICMP echo请求。如果收到ICMP echo回复，则执行端口扫描操作，尝试连接该主机的如下端口：9、 21、 22、 23、 25、 37、 42、 43、 53、 69、 70、 79、 80、 88、 103、 110、 115、 118、 123、 137、 138、 139、 143、 150、 156、 161、 190、 197、 389、 443、 445、 515、 546、 547、 569、 3306、 8080或者8291端口。

接下来，该模块使用MikroTik网络发现协议（MNDP，MikroTik Network Discovery Protocol）来搜索本地网络中的其他MikroTik设备。一旦某个MikroTik设备回复MNDP ping请求，那么nm模块就会提取出该设备的MAC地址、系统标识、版本号、平台类型、运行时间（以秒为单位）、RouterOS软件ID、RouterBoard模型以及接口名称。

nm模块会检查/proc/net/arp来获取被感染设备的ARP表信息，了解相邻设备的IP地址以及MAC地址，然后获取/proc/net/wireless中的所有数据。

该模块还会执行traceroute操作，首先尝试通过TCP协议连接8.8.8.8:53，确认目的地可达（没有发送任何数据），然后向该IP发送TTL递增的ICMP echo请求报文。

收集到的所有网络信息保存到一个临时文件中：/var/run/repsc_&lt;time stamp&gt;.bin，该文件的内容如下所示：

[![](https://p3.ssl.qhimg.com/t01cc0b03c7c7a2074f.jpg)](https://p3.ssl.qhimg.com/t01cc0b03c7c7a2074f.jpg)

该模块中还存在负责处理SSDP、CDP以及LLDP函数的代码，但我们分析的样本并没有调用这些函数，因此上图文件中并没有包含这部分数据。

nm模块会请求3个命令行参数来正常运行，但实际上只用到了第1个参数。与其他几个模块一样，第1个参数为一个文件夹，用来永久保存数据信息。nm模块所执行的最后一个任务是将包含扫描结果的.bin临时文件移动到第1个参数所指定的目录，为VPNFilter主进程的后续渗透操作提供服务。

### <a name="netfilter%EF%BC%88%E6%8B%92%E7%BB%9D%E6%9C%8D%E5%8A%A1%E5%B7%A5%E5%85%B7%EF%BC%89"></a>netfilter（拒绝服务工具）

netfilter模块需要接受来自命令行的3个参数，前面2个参数并没有使用，第3个参数为带引号的一个字符串，具体格式为&lt;block/unblock&gt; &lt;# of minutes&gt;，其中# of minutes代表netfilter在退出之前所需要运行的时间长度，如果用到了block参数，那么netfilter就会将如下规则加入iptables中：

添加上述规则后，netfilter会等待30秒，然后删除这条规则。如果参数指定的# of minutes值仍有富余时间，那么就会再次执行这个过程。通过这种添加及删除循环操作，即便设备删除了该规则，这个模块仍可以确保该规则被再次添加。

一旦超过参数设定的分钟数，程序就会退出。netfilter程序开头处会安装信号处理程序，一旦程序收到SIGINT或者SIGTERM信号，就会删除iptables规则然后退出。通过这种方式，如果有人手动结束netfilter程序，设备也能正常工作。

最后，unblock参数用来删除先前block参数所添加的iptables规则。

虽然我们没有在程序中找到其他代码路径，但有迹象表明该模块包含（或者可能包含）其他功能。

第一个线索，Talos分析的不同netfilter模块样本（MIPS、PPC以及Tile-GX）都包含同一个CIDR IP地址及范围列表（总共168个元素），这些地址与如下公司/服务有关：

这意味着netfilter模块可能用来拦截对某类加密应用的访问，尝试将受害者的通信数据引到攻击者容易处理其他服务。有趣的是，这份清单中缺少一个非常受欢迎的加密聊天应用：Telegram。

然而，我们无法在代码中找到与这些字符串有关的任何引用。我们分析的所有版本的netfilter样本虽然都包含同样一份IP范围列表，却没有用到这些信息，可能我们收集到的样本并不完整。

netfilter模块所添加的iptables规则会丢弃带有PUSH标志的TCP报文。如果攻击者的目的是使用已控制的设备发起拒绝服务攻击，那么他们可能会使用这条规则来拦截所有报文，而不单单是带有PUSH标志的TCP报文。通常情况下，这类规则对中间人攻击（man-in-the-middle）场景非常有用，可以帮助具备设备访问权限的攻击者拦截中转的流量、修改流量然后再转发流量。这样就可能解释为什么程序中会存在CIDR IP地址范围。在已分析的所有样本中，我们无法找到这类功能存在的任何线索。

我们可以证实攻击者并没有用到这些IP，可能这些IP是旧版本netfilter模块的遗留信息，也有可能是相关功能尚未实现，或者是我们尚未发现的被恶意软件作者修改的iptables静态链接库。VPNFilter作者之前也修改过开源代码（比如ndbr模块），因此他们也有可能会修改netfilter模块中链接的libiptc代码。

### <a name="portforwarding%EF%BC%88%E8%BD%AC%E5%8F%91%E6%B5%81%E9%87%8F%E8%87%B3%E6%94%BB%E5%87%BB%E8%80%85%E7%9A%84%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%EF%BC%89"></a>portforwarding（转发流量至攻击者的基础设施）

portforwarding模块所使用的命令行参数如下所示：

传入这些参数后，portforwarding模块可以安装如下iptables规则，将来自特定端口及IP的流量转发到另一个端口及IP地址：

这些规则会导致流经已感染设备的、目的地为IP1:PORT1的所有流量被重定向到IP2:PORT2地址处。第二条规则会修改重定向流量中的源地址，将其改为已感染设备的地址，确保响应数据可以回到被感染设备。

为了确保规则切实可用，在安装这些iptables规则之前，portforwarding模块首先会检查IP2的确可用，具体操作是创建连接至IP2:PORT2的一个socket连接，然而关闭socket前该模块并不会发送任何数据。

与修改iptables的其他模块类似，portforwarding模块也会进入一个循环过程，不断添加规则、等待一段时间、删除规则然后再重新添加规则，确保这些规则在被手动删除的情况下，依然可以保留在设备上。

### <a name="socks5proxy%EF%BC%88%E5%9C%A8%E8%A2%AB%E6%8E%A7%E8%AE%BE%E5%A4%87%E4%B8%8A%E5%88%9B%E5%BB%BASOCKS5%E4%BB%A3%E7%90%86%EF%BC%89"></a>socks5proxy（在被控设备上创建SOCKS5代理）

socks5proxy模块是一个SOCKS5代理服务器，基于[shadowsocks](https://shadowsocks.org/en/index.html)开源项目开发。服务器没有使用身份认证方案，在硬编码的TCP 5380端口上监听。在服务器运行之前，socks5proxy会执行fork操作，连接至传入参数中指定的某个C2服务器。如果C2服务器在几秒钟内没有响应，则fork进程会结束父进程（原始服务器）然后退出。C2服务器可以返回一些命令，让服务器正常运行或终止运行。

该某块包含如下使用帮助字符串，但这些字符串实际上并非socks5proxy模块所使用的参数，并且无法通过命令行参数来修改这些设置：

实际上socks5proxy模块所使用的命令行参数如下所示：

socks5proxy模块会验证参数数量是否大于1，但如果输入2个参数则会导致该进程收到SIGSEV信号而崩溃，这表明这款恶意软件工具链的某些研发阶段中的代码质量控制并不理想，或者非常有限。

### <a name="tcpvpn%EF%BC%88%E5%9C%A8%E8%A2%AB%E6%8E%A7%E8%AE%BE%E5%A4%87%E4%B8%8A%E5%88%9B%E5%BB%BA%E5%8F%8D%E5%90%91TCP%20VPN%E8%BF%9E%E6%8E%A5%EF%BC%89"></a>tcpvpn（在被控设备上创建反向TCP VPN连接）

tcpvpn模块是一个反向TCP（Reverse-TCP）VPN模块，允许远程攻击者访问已感染设备后面的内部网络。该模块与远程服务器通信，后者可以创建类似TunTap之类的设备，通过TCP连接转发数据包。连接请求由网络设备发出，因此可能帮助该模块绕过某些简单的防火墙或者NAT限制。该模块在概念上类似于Cobalt Strike这款渗透测试软件的[VPN Pivoting](https://www.cobaltstrike.com/help-covert-vpn)功能。

发送的所有数据包都经过RC4加密处理，密钥通过硬编码的字节来生成，如下所示：

密钥两端分别为当前连接的端口号（比如58586!;H*rK|_MwS+E!-!^yC=yJTh.ke:VynEz-~;:-Q;kQ^w^-~S;QEZh6^jgf_4RzsG80）。

tcpvpn模块所使用的命令行语法如下所示：



## 四、MikroTik研究

### <a name="Winbox%E5%8D%8F%E8%AE%AE%E8%A7%A3%E6%9E%90%E5%99%A8"></a>Winbox协议解析器

在研究VPNFilter的过程中，我们需要确定攻击者如何攻破其中某些设备。在检查MikroTik系列设备时，我们注意到设备上开放了一个端口（TCP 8291），而Winbox这款配置工具会使用该端口来通信。

来自这些设备的流量均为大量的二进制数据，因此我们无法在不使用协议解析器的情况下来分析该协议所能触及的访问路径（根据我们先前了解的情况，网上并没有公开相关研究内容）。我们决定自己开发协议解析器，以便与[Wireshark](https://www.wireshark.org/)等数据包分析工具配合使用，进一步了解该协议的更多信息，这样我们就能设计有效的规则，以便未来在发现潜在的攻击向量时能够阻止感染路径。

典型的攻击向量为[CVE-2018-14847](https://arstechnica.com/information-technology/2018/09/unpatched-routers-being-used-to-build-vast-proxy-army-spy-on-networks/)，攻击者可以利用该漏洞在未通过身份认证的情况下执行路径遍历攻击。在编写适配该漏洞的规则时（[Snort SID: 47684](https://www.snort.org/rule-docs/1-31977)），协议解析器发挥了非常关键的作用。虽然官方已发布了修复该漏洞的[更新](https://blog.mikrotik.com/security/winbox-vulnerability.html)，我们认为专业的安全人员必须能够监控这类流量，以识别其他任何潜在的恶意流量。

此时我们依然能够保证用户的隐私，只要用户使用“安全模式（secure mode）”来加密通信，或者下载最新版的Winbox客户端（该客户端只会使用加密通道来传输数据）即可。这款工具不会解密已加密的通信数据。我们测试的最新版的MikroTik CCR固件版本为6.43.2版，该版本会强制使用较新版的Winbox客户端，但这种限制条件只应用于客户端。这意味着我们仍然可以使用自定义的客户端，通过不安全的通道进行通信。因此，我们认为这个Wireshark解析器依然可用，因为攻击者仍然可以投递漏洞利用载荷，无需满足前面提到的安全通信条件。

### <a name="%E4%BD%95%E4%B8%BA%E2%80%9CWinbox%E5%8D%8F%E8%AE%AE%E2%80%9D"></a>何为“Winbox协议”

Winbox这个名词来自于MikroTik提供的Winbox客户端，用来作为Web GUI的替代方案。

根据官方文档，Winbox是一个小型工具，可以使用快速且简单的GUI来管理MikroTik RouterOS。这是一个原生的Win32程序，但也可以通过Wine（一个开源兼容层解决方案）运行在Linux以及MacOS上。所有的Winbox接口函数都尽可能与控制台函数靠拢，这也是为什么手册中不存在Winbox内容的原因所在。Winbox无法修改某些高级以及关键系统配置，比如无法修改某个接口的MAC地址。

据我们所知，“Winbox协议”并非官方名词，因为这个名词与官方客户端匹配，因此我们选择使用这个说法。

### <a name="%E4%BD%BF%E7%94%A8%E8%A7%A3%E6%9E%90%E5%99%A8"></a>使用解析器

解析器安装起来非常简单，由于这是一个基于LUA的解析器，因此无需重新编译。只需要将Winbox_Dissector.lua文件放入/$HOME/.wireshark/plugins目录即可。默认情况下，只要我们安装了这个解析器，就能正确解析来自或者发往TCP 8291端口的所有流量。

来自客户端/服务器的单条消息解析起来更加方便，然而实际环境中总会遇到各种各样的情况。观察实时通信数据后，我们证实Winbox消息可以使用各种格式进行发送。

我们捕获过的Winbox通信数据具备各种属性，比如：

1、在同一个报文中发送多条消息；

2、消息中包含1个或多个2字节的“chunks”数据，我们在解析之前需要删除这些数据；

3、消息过长，无法使用单个报文发送——出现TCP重组情况；

4、包含其他“嵌套”消息的消息。

在安装解析器之前捕获得到数据包如下图所示：

[![](https://p3.ssl.qhimg.com/t0123839589aa9c3132.png)](https://p3.ssl.qhimg.com/t0123839589aa9c3132.png)

安装Winbox协议解析器后，Wireshark可以正确解析通信数据，如下图所示：

[![](https://p4.ssl.qhimg.com/t0137d5660c17ca3e37.png)](https://p4.ssl.qhimg.com/t0137d5660c17ca3e37.png)

### <a name="%E8%8E%B7%E5%8F%96%E8%A7%A3%E6%9E%90%E5%99%A8"></a>获取解析器

为了帮助安全社区分析这类通信数据，也为了监控可能利用Winbox协议的潜在威胁，思科Talos公开了这款解析器，大家可以访问GitHub[页面](https://github.com/Cisco-Talos/Winbox_Protocol_Dissector)下载这款工具。



## 五、总结

结合我们之前发现的VPNFilter功能以及这次的新发现，我们现在可以确认VPNFilter可以为攻击者提供各种功能来利用已攻破的网络以及存储设备，以便进一步渗透及攻击目标网络环境。

攻击者可以利用该框架将攻击范围扩大到敏感系统，如网关或者路由设备上，以执行类似网络映射、端点攻击、网络通信监控以及流量篡改等攻击活动。VPNFilter还提供了另一个危险功能，能够将已感染的设备转化为代理，利用这些代理来混淆未来的攻击源，使将人们误以为攻击流量来自于先前被VPNFilter攻击的网络。该框架非常复杂，进一步说明攻击者可以利用该框架的各种高级功能，也表明我们需要部署更强大的防御架构来应对类似VPNFilter之类的威胁。

进一步了解VPNFilter后，先前我们未解决的大部分问题已经有了答案。然而，时至今日，我们面对该威胁时仍有一些问题尚未澄清：

1、攻击者最开始时如何获取目标设备的访问权限？

虽然我们认为攻击者利用了已知的公开漏洞来攻破受VPNFilter影响的这些设备，但我们仍然没有明确的证据证实这一点。

2、攻击者是否尝试重新获取访问权限？

基于我们的感知数据以及合作伙伴提供的信息，我们发现VPNFilter已经完全处于静默期，因为我们和国际上的合作伙伴（执法部门、情报机构以及网络威胁联盟）已在今年早些时候成功抵御了这个威胁。这款恶意软件所使用的大多数C2通道已经摧毁。第二阶段植入体不具备持久化技术，因此很有可能已从被感染的设备中清除。我们没有发现攻击者尝试重新连接目标设备的任何迹象（这些设备运行第一阶段持久化载荷，会监听接入请求）。

这是否意味着攻击者已经放弃进入小型家庭办公（SOHO）网络设备空间的这个据点？攻击者是否重新开始，重新攻击并释放未知的恶意软件，重新获取了访问权限？攻击者是否放弃针对全球范围的SOHO访问权限，转而采用跟为针对性的方案，只攻击特定的关键目标？

无论答案如何，我们知道VPNFilter背后的攻击者实力很强，会在任务驱动下不断改进，以实现他们的既定目标。攻击者会以某种形式继续开发任务目标所需的各种工具和框架。



## 六、IoC

我们发布了如下特征及规则以便检测VPNFilter使用的附加模块。

检测ndbr的Snort规则

Clam AV规则
