> 原文链接: https://www.anquanke.com//post/id/85152 


# 【技术分享】LuaBot： 以电缆调制解调器为目标的恶意程序分析


                                阅读量   
                                **91530**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：w00tsec
                                <br>原文地址：[https://w00tsec.blogspot.com/2016/09/luabot-malware-targeting-cable-modems.html](https://w00tsec.blogspot.com/2016/09/luabot-malware-targeting-cable-modems.html)

译文仅供参考，具体内容表达以及含义原文为准

****

**[![](https://p1.ssl.qhimg.com/t011e2b1bd44755af61.jpg)](https://p1.ssl.qhimg.com/t011e2b1bd44755af61.jpg)**

**翻译：**[**poi******](http://bobao.360.cn/member/contribute?uid=2799685960)

**预估稿费：260RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**前言**

在2015年中期，我发现一些影响ARRIS公司的电缆调制解调器的漏洞。我为此写了篇博客[blogpost about ARRIS' nested backdoor ](https://w00tsec.blogspot.com/2015/11/arris-cable-modem-has-backdoor-in.html)，详细的讲述了我对于电缆调制解调器的一些研究（相比于在2015年的[NullByte Security Conference](https://www.nullbyte-con.org/)的演讲更加详细）。

CERT/CC（美国计算机安全事件响应小组）发布了漏洞记录 [VU#419568](https://www.kb.cert.org/vuls/id/419568),受到了大量媒体报道。我那个时候没有提供任何Poc，因为我确定那些漏洞很容易做成蠕虫。猜猜发生了什么？从2016年5月开始，有人攻破了那些设备。

恶意程序以[Puma 5电缆调制解调器](https://www-ssl.intel.com/content/www/us/en/cable-modems/puma5-product-brief.html)为目标，包括了ARRIS公司的TG862系列。传染发生在众多平台，[Dropper](https://en.wikipedia.org/wiki/Dropper_(malware)类似于很多[普通蠕虫](https://www.protectwise.com/blog/observing-large-scale-router-exploit-attempts/)，以[多个架构](https://isc.sans.edu/diary/19999)的[嵌入式设备为目标](https://quantumfilament.co/2015/08/17/chapter-2-the-binary/)。 最终版本为来自[LuaBot Malware](https://www.symantec.com/security_response/writeup.jsp?docid=2016-090915-3236-99)的ARMEB(endian big)版本。

[![](https://p2.ssl.qhimg.com/t01785a398d6c7a1bfd.png)](https://p2.ssl.qhimg.com/t01785a398d6c7a1bfd.png)

来自LuaBot恶意程序的ARMEL版本已经在[blogpost from Mslware Must Die](http://blog.malwaremustdie.org/2016/09/mmd-0057-2016-new-elf-botnet-linuxluabot.html)中进行了剖析，但是这个ARMEB目前任然未知。这个恶意程序起初在2016-05-26的时候发送给了 VirusTotal，但是并没有检测出问题。<br>

[![](https://p4.ssl.qhimg.com/t013c3b2d037e40441d.png)](https://p4.ssl.qhimg.com/t013c3b2d037e40441d.png)

## <br>

**电缆调制解调器的安全和ARRID的后门**

在进一步操作前， 如果你希望了解电缆调制解调器的安全，请看我去年进行的讨论 “Hacking Cable Modems: The Later Years”的幻灯片。 会谈囊括了用来管理电缆调制解调器的技术的很多方面：数据是如何保护的，ISP是如何更新固件的等等。

[https://github.com/bmaia/slides/raw/master/nullbyte_2015-hacking_cable_modems_the_later_years.pdf](https://github.com/bmaia/slides/raw/master/nullbyte_2015-hacking_cable_modems_the_later_years.pdf)

特别要关注第86页：

[![](https://p1.ssl.qhimg.com/t01de7b28bf2a0303b4.png)](https://p1.ssl.qhimg.com/t01de7b28bf2a0303b4.png)

我收到了很多报告：为了转存配置文件和偷窃私人认证证书，恶意程序的创立者们远程攻破了这些设备。还有一些用户表示个人认证信息被出售给全球各地的调制解调器克隆商以获取比特币。 [[Malware Nust Die!]](http://blog.malwaremustdie.org/2016/09/mmd-0057-2016-new-elf-botnet-linuxluabot.html)上的报告也表明了 LuaBot也在进行 flooding/DDoS攻击。

<br>

**漏洞利用和传染**

Luabot恶意程序是一个更大的僵尸网络的一部分，以各种架构的嵌入式设备为目标。 验证了一些感染的设备后，我注意到大多数的电缆调制解调器是通过使用ARRIS的后门口令对受限的CLI进行命令行注入破解的。  

Telnet蜜罐（比如[ [nothink.org]](http://www.nothink.org/honeypot_telnet.php)）已经记录了一段时间关于尝试利用漏洞的情况。记录了很多尝试使用用户名 “system”和口令”ping ;sh”的暴力破解。但其实，命令是用来逃避受限制的ARRIS的Telnet shell。

[![](https://p5.ssl.qhimg.com/t013718c3c6345b11ab.png)](https://p5.ssl.qhimg.com/t013718c3c6345b11ab.png)

最初创建的dropper程序通过显示shell命令创建一个标准的ARM ELF文件。

[![](https://p1.ssl.qhimg.com/t0132363c41bcc7a04e.png)](https://p1.ssl.qhimg.com/t0132363c41bcc7a04e.png)

[![](https://p5.ssl.qhimg.com/t010caf068d3b679693.png)](https://p5.ssl.qhimg.com/t010caf068d3b679693.png)

我交叉编译，上传了一些调试工具到我的[cross-utils](https://github.com/bmaia/cross-utils/tree/master/armeb)仓库，包括gdbserver、strace和tcpdump。我也碰巧有一个ARRIS TG862设备，所以准备在受控环境下进行动态调试。

如果使用strace运行dropper监控网络调用，你会看到首次连接尝试：

```
./strace -v -s 9999 -e poll,select,connect,recvfrom,sendto -o network.txt ./mw/drop
```

```
connect(6, `{`sa_family=AF_INET, sin_port=htons(4446), sin_addr=inet_addr("46.148.18.122")`}`, 16) = -1 ENODEV (No such device)
```

命令为简单的下载和执行ARMEB的shellcode，恶意ip : 46.148.18.122 在 [bruteforcing SSH servers and trying to exploit Linksys router command injections](https://www.abuseipdb.com/check/46.148.18.122)中已经知晓。 下载第二阶段的恶意程序之后，脚本会显示以下字符：

```
echo -e 61\\\x30ck3r
```

样式特别有趣，因为和ProtectWise 公司报告的 [Observing Large-Scale Router Exploit Attempts](https://www.protectwise.com/blog/observing-large-scale-router-exploit-attempts/)很相似：

```
cmd=cd /var/tmp &amp;&amp; echo -ne \x3610cker &gt; 610cker.txt &amp;&amp; cat 610cker.txt
```

第二阶段的二进制文件 “.nttd”(MD5 : c867d00e4ed65a4ae91ee65ee00271c7) 进行了一些内部检测并创建了一些iptable规则（允许来自特殊子网的连接，阻止了来自端口8080，80，433，23和22的外部访问）。

[![](https://p2.ssl.qhimg.com/t0137d3b80c5f44fb79.png)](https://p2.ssl.qhimg.com/t0137d3b80c5f44fb79.png)

这些规则阻止对ARRIS服务/后门的外部漏洞尝试，限制攻击者进入被控制的网络。

设置完规则后，攻击者会传输/运行两个额外的二进制文件，第一个 ：.sox.rslv（MD5 ： 889100a188a42369fd93e7010f7c654b）是个基于[udns 0.4](https://github.com/wongsyrone/shadowsocks-libev-libsodium-for-server/tree/master/libudns)的简单的DNS查询工具

[![](https://p1.ssl.qhimg.com/t011ad7ad4dd6055577.png)](https://p1.ssl.qhimg.com/t011ad7ad4dd6055577.png)

另一个二进制文件 .sox（MD5 ： 4b8c0ec8b36c6bf679b3afcc6f54442a），将DNS服务器设置为 8.8.8.8和8.8.4.4 并提供多个隧道功能（包括SOCKS/proxy , DNS和IPv6）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0113dc612bf18de8d0.png)

部分代码类似 [shadowsocks-libev](http://code.taobao.org/p/sss-libev/src/trunk/shadowsocks-libev-master/) ，并且暴露了一个有趣的域名 [whrq[.]net domain](https://www.threatcrowd.org/domain.php?domain=whrq.net)， 看起来像是作为dnscrypt网关

[![](https://p4.ssl.qhimg.com/t01f8109febe09a3770.png)](https://p4.ssl.qhimg.com/t01f8109febe09a3770.png)

这些工具都是作为辅助工具来完成LuaBot的最终形态 arm_puma5(MD ：061b03f8911c41ad18f417223840bce0)，似乎是有选择性的安装在部分存在漏洞的电缆调制解调器上。

更新 ： 根据这个[采访](https://medium.com/@x0rz/interview-with-the-luabot-malware-author-731b0646fc8f)假定的恶意程序作者所说，“逆向人员搞错了，说这些模块来自我的程序，但是其实是别人的，一些路由器同时感染了多个程序,我的从来没有任何二进制模块，是一个大elf文件，有时dropper小于1kb”。

<br>

**最终形态 ： LuaBot**

恶意程序的最终形态为 716KB的ARMEB 的elf二进制文件，静态链接，精简的（没有调试信息），并使用Puma5的工具链进行编译，可以在我的仓库[cross-utils](https://github.com/bmaia/cross-utils/tree/master/armeb/puma5_toolchain)中获取

[![](https://p0.ssl.qhimg.com/t01819ef7cfcf9ae0bf.png)](https://p0.ssl.qhimg.com/t01819ef7cfcf9ae0bf.png)

如果使用strace进行动态分析， 我们可以看到bot作者的问候和mutx(bbot_mutex_202613)的创建，然后bot开始监听11833(TCP)端口并尝试联系命令和控制服务器（80.87.205.92）

```
1078  write(1&lt;socket:[4448]&gt;, "Hi. Mail me if u want: routerbots@_____.__n", 44) = 44
1078  socket(AF_LOCAL, SOCK_STREAM, 0)  = 7&lt;socket:[22218]&gt;
1078  bind(7&lt;socket:[22218]&gt;, `{`sa_family=AF_LOCAL, sun_path=@"bbot_mutex_202613"`}`, 110) = 0
1078  clone(child_stack=0, flags=CLONE_CHILD_CLEARTID|CLONE_CHILD_SETTID|SIGCHLD, child_tidptr=0xc6048) = 1079
1078  exit_group(0)                     = ?
1078  +++ exited with 0 +++
1079  setsid()                          = 1079
1079  clone( &lt;unfinished ...&gt;
(...)
1080  gettimeofday(`{`500, 278384`}`, NULL) = 0
1080  socket(AF_INET, SOCK_STREAM, IPPROTO_TCP) = 10&lt;socket:[22231]&gt;
1080  ioctl(10&lt;socket:[22231]&gt;, FIONBIO, [1]) = 0
1080  setsockopt(10&lt;socket:[22231]&gt;, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0
1080  bind(10&lt;socket:[22231]&gt;, `{`sa_family=AF_INET, sin_port=htons(11833), sin_addr=inet_addr("0.0.0.0")`}`, 16) = 0
1080  listen(10&lt;socket:[22231]&gt;, 1024)  = 0
1080  open("/proc/net/route", O_RDONLY|O_LARGEFILE) = 11&lt;/proc/net/route&gt;
(...)
1080  gettimeofday(`{`500, 318385`}`, NULL) = 0
1080  _newselect(32, [8&lt;pipe:[22229]&gt; 10&lt;socket:[22231]&gt;], [], NULL, `{`0, 959999`}`) = 0 (Timeout)
1080  gettimeofday(`{`501, 278401`}`, NULL) = 0
1080  socket(AF_INET, SOCK_STREAM, IPPROTO_TCP) = 11&lt;socket:[22282]&gt;
1080  ioctl(11&lt;socket:[22282]&gt;, FIONBIO, [1]) = 0
1080  connect(11&lt;socket:[22282]&gt;, `{`sa_family=AF_INET, sin_port=htons(1055), sin_addr=inet_addr("80.87.205.92")`}`, 16) = -1 ENETUNREACH (Network is unreachable)
1080  close(11&lt;socket:[22282]&gt;)         = 0
1080  write(0&lt;socket:[4448]&gt;, "GET /getcmds?bid=notgenerated HTTP/1.1rnConnectio
```

为了理解恶意程序是怎么工作的，我们把人工和动态分析进行结合。是时候使用IDA pro进行分析二进制文件了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01107f8ab18b7e2ee8.gif)

二进制文件是精简的， IDA pro 一开始没有分析出ARMEB的常用函数调用。我们可以使用 [@matalaz](https://github.com/joxeankoret/diaphora)'s [diaphora](https://github.com/joxeankoret/diaphora) 的diffing插件来得到所有的符号而不是话费数小时进行手工检查。

首先导出 uClibc的Puma5工具链的符号。 从[这里](https://github.com/bmaia/cross-utils/blob/master/armeb/puma5_toolchain/armeb-linux.tar.xz)下载预编译的工具链，使用IDA pro打开 “armeb-linuxti-puma5liblibuClibc-0.9.29.so”库文件。 选择 FIle/Script(ALT+F7), 加载diaphora.py， 选择一个位置将IDA数据库导出成SQLite格式， 选择Export only non-IDA generated functions然后点击 OK。

当完成后，关闭当前IDA 数据库， 打开arm_puma5二进制文件。再次运行diaphora.py脚本，选择SQLite数据库进行比较

[![](https://p5.ssl.qhimg.com/t01daf4367341635d78.png)](https://p5.ssl.qhimg.com/t01daf4367341635d78.png)

过一会后，会显示连个数据库中各种不能匹配的函数的选项，比如“Best”“Partial”和“ Unreliable”匹配项。

浏览“Best matches”项，右击列表然后选择“Import *all* functions”，然后结束后选择不重新启动比较进程。前往“Partial matches”项，删除所有比例比较低的(我把低于0.8的都删掉了)，右击列表选择”Import all data for sub_* function"。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0187f1141c3946df06.png)

IDA的 string窗口显示很多和Lua脚本语言相关的信息。 因此，我也交叉编译了一份[Lua的ARMEB版本](https://github.com/bmaia/cross-utils/tree/master/armeb/lua),将 lua二进制载入IDA pro，重复和[diaphora](https://github.com/joxeankoret/diaphora)的比较过程。

[![](https://p5.ssl.qhimg.com/t01c2bd35b4560b108d.png)](https://p5.ssl.qhimg.com/t01c2bd35b4560b108d.png)

差不多完成了，如果你google一些调试信息的话，你会找到一份删除的粘贴内容的快照。

[![](https://p0.ssl.qhimg.com/t01ea78802a42687fe0.png)](https://p0.ssl.qhimg.com/t01ea78802a42687fe0.png)

我下载了C代码 evsocketlib.c，为所有这里没有包括的内容建立虚拟结构，并交叉编译出ARMEB版本。然后呢？ 再次比较。

[![](https://p0.ssl.qhimg.com/t011981e8b4af6a0a04.png)](https://p0.ssl.qhimg.com/t011981e8b4af6a0a04.png)

[![](https://p1.ssl.qhimg.com/t0145b9a95684b3fe01.png)](https://p1.ssl.qhimg.com/t0145b9a95684b3fe01.png)

现在再对恶意程序进行逆向就清晰多了。有内置的Lua解释器，一些套接字相关的本地代码。僵尸网络的命令列表存储在 0x8274中： bot_daemonize, rsa_verify, sha1, fork, exec, wait_pid, pipe, evsocket, ed25519, dnsparser, struct, lpeg, evserver, evtimer and lfs：

[![](https://p1.ssl.qhimg.com/t01ed01c9407830a423.png)](https://p1.ssl.qhimg.com/t01ed01c9407830a423.png)

bot一开始进行Lua环境的设置，解压缩代码，建立子进程，等待来自CnC控制伺服器的指令。恶意程序作者将Lua的源代码亚作为GZIP blob，使得整个逆向工作更加容易(不用再处理Lua的字节码了)。

[![](https://p2.ssl.qhimg.com/t01057aac8edb729ee9.png)](https://p2.ssl.qhimg.com/t01057aac8edb729ee9.png)

在0xA40B8的blob中 包含了GZip的头，以及最后修改的时间戳。

[![](https://p0.ssl.qhimg.com/t01f2eb69fc662f5111.png)](https://p0.ssl.qhimg.com/t01f2eb69fc662f5111.png)

另一个简单的解压lua代码的方式为： 将二进制文件attach到喜欢的调试器上(当然是 [gef](https://github.com/hugsy/gef)),然后将进程内存转存出来。

首先 将 [gdbserver](https://github.com/bmaia/cross-utils/tree/master/armeb/gdb)拷贝到电缆调制解调器上， 运行恶意程序(arm_ppuma5)并attach到调试器到对应的pid上。

```
./gdbserver --multi localhost:12345 --attach 1058
```

[![](https://p2.ssl.qhimg.com/t01ebd3c8855a742b65.png)](https://p2.ssl.qhimg.com/t01ebd3c8855a742b65.png)

```
./gdbserver --multi localhost:12345 --attach 1058
gdb-multiarch -q
set architecture arm
set endian big
set follow-fork-mode child
gef-remote 192.168.100.1:12345
```

[![](https://p0.ssl.qhimg.com/t01b77ec09280a5ae3e.png)](https://p0.ssl.qhimg.com/t01b77ec09280a5ae3e.png)

最后 列出内存部分，转存出堆中的内容

```
vmmap
dump memory arm_puma5-heap.mem 0x000c3000 0x000df000
```

[![](https://p2.ssl.qhimg.com/t0198605cecdf17ec50.png)](https://p2.ssl.qhimg.com/t0198605cecdf17ec50.png)

现在就有了LuaBot的所有源代码了

[![](https://p0.ssl.qhimg.com/t01a8f1e76c23a5f6be.png)](https://p0.ssl.qhimg.com/t01a8f1e76c23a5f6be.png)

LuaBot源码由几个模块组成

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cb320d67c165fad5.png)

bot的设置，DNS递归器和CnC设置是硬编码了的

[![](https://p3.ssl.qhimg.com/t01f74ad18964d42bb5.png)](https://p3.ssl.qhimg.com/t01f74ad18964d42bb5.png)

代码注释的很好，包括代理的检验函数和  mssscan的日志解析 ：

[![](https://p4.ssl.qhimg.com/t018f986eb012af1b73.png)](https://p4.ssl.qhimg.com/t018f986eb012af1b73.png)

使用 /dev/urandom 作为随机数种子：

[![](https://p4.ssl.qhimg.com/t01011f146880a65d99.png)](https://p4.ssl.qhimg.com/t01011f146880a65d99.png)

LuaBot集成了嵌入式的JavaScript引擎,并且执行使用作者的RSA公钥签名的脚本

[![](https://p5.ssl.qhimg.com/t0121c477c27e1e31e1.png)](https://p5.ssl.qhimg.com/t0121c477c27e1e31e1.png)

LuaBot集成了嵌入式的JavaScript引擎,并且执行使用作者的RSA公钥签名的脚本

[![](https://p0.ssl.qhimg.com/t010a3f2b1a18d480f3.png)](https://p0.ssl.qhimg.com/t010a3f2b1a18d480f3.png)

存在函数 ： checkanus.penetrate_sucuri， 大概用来绕过 Sucuri 的DDoS（拒绝服务攻击）保护的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01bc554387e0c6e359.png)

[![](https://p4.ssl.qhimg.com/t012ecbb68a9c6e2d0b.png)](https://p4.ssl.qhimg.com/t012ecbb68a9c6e2d0b.png)

有一个函数 ： checkanus.penetrate_sucuri， 大概用来绕过 Sucuri 的DDoS（拒绝服务攻击）保护的

[![](https://p1.ssl.qhimg.com/t01ccc261b901908e74.png)](https://p1.ssl.qhimg.com/t01ccc261b901908e74.png)

大多数bot的功能都和[Malware Must Die! blogpost](http://blog.malwaremustdie.org/2016/09/mmd-0057-2016-new-elf-botnet-linuxluabot.html)中的相吻合。 有趣的是 CnC服务的IP和iptable规则中的IP没有相同的部分，可能妒忌不同的bot种类采用了不同的环境，（也可能只是因为升级了）。

我没有分析远程僵尸网络的结构，但是模块化的方式和恶意程序的互操作性表示这会是个专业的持续的行为。

<br>

**总结**

恶意程序并没有持久机制来存活，它不会尝试刷新固件或者修改易失区(比如NVRAM)，但是第一版本的payload使用iptables规则来限制设备的远程连接。

这是个很有趣的处理方式，因为它可以循序的扫描网络，限制IoT设备的额外的连接，并有选择的使用最终形态的payload进行感染。

2015年，我首次报告ARRIS的后门的时候，有超过[60万的ARRIS设备存在漏洞](https://twitter.com/bernardomr/status/667643475358318592)， 49万的设备的telnet服务是开启的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bc592a3c2f173fda.png)

在2016年9月进行同样的查询，可以看到暴露的设备减少到3万5了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e95c8b03c920ffad.png)

我知道新闻媒体报道，[安全报道](https://www.kb.cert.org/vuls/id/419568)对此出了很多力，但我想知道这些设备中已经有多少被感染了，又有多少设备因为各种恶意程序而限制了额外的连接。

大量 存在面向互联网的管理接口的Linux设备， 后门的利用， 缺乏固件升级，容易完成对LoT设备的破解，使得它们成为网络犯罪的目标

IoT 僵尸网络正在成为这中存在 ： 厂商必须建立安全可靠的产品， ISP服务商需要提供 升级的设备/固件， 用户需要给家用设备打补丁，保证安全 。

我们需要找到更好的方式去发现，阻止，抑制这种新出现的趋势， 比如 [SENRIO](http://senr.io/) 的方式 可以帮助ISP服务商和企业对IoT生态环境更加关注。大规模的固件分析可以继续，并提供设备安全问题的更好的理解.

<br>

**攻击指示器**

LuaBot ARMEB 二进制文件：

drop (5deb17c660de9d449675ab32048756ed)

.nttpd (c867d00e4ed65a4ae91ee65ee00271c7)

.sox (4b8c0ec8b36c6bf679b3afcc6f54442a)

.sox.rslv (889100a188a42369fd93e7010f7c654b)

.arm_puma5 (061b03f8911c41ad18f417223840bce0)

GCC交叉编译工具

GCC: (Buildroot 2015.02-git-00879-g9ff11e0) 4.8.4

GCC: (GNU) 4.2.0 TI-Puma5 20100224

Dropper and CnC IPs:

46.148.18.122

80.87.205.92

攻击者的IP白名单

46.148.18.0/24

185.56.30.0/24

217.79.182.0/24

85.114.135.0/24

95.213.143.0/24

185.53.8.0/24
