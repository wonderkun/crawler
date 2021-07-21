> 原文链接: https://www.anquanke.com//post/id/212096 


# 挖掘VirtualBox漏洞，以3个CVE为例


                                阅读量   
                                **201484**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者paulch.ru，文章来源：blog.paulch.ru
                                <br>原文地址：[http://blog.paulch.ru/2020-07-26-hunting-for-bugs-in-virtualbox-first-take.html](http://blog.paulch.ru/2020-07-26-hunting-for-bugs-in-virtualbox-first-take.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01ee252c3b26e26e52.png)](https://p3.ssl.qhimg.com/t01ee252c3b26e26e52.png)



## 0x00 绪论

最近，我发现了VirtualBox的几个内存破坏漏洞。我想分享我的经验，包括发现方法以及有关VirtualBox内部的一些信息。

我认为VirtualBox是漏洞研究的不错的目标，因为：
- VirtualBox被很多人经常使用，它是一个影响面很大的系统。但是，你仍然可以在其中找到一些非常小的错误，我将在本文中展示。
- 你可以借此入门虚拟化技术和虚拟机监视器（hypervisor）研究。研究诸如VMWare或Hyper-V之类的项目可能非常困难，因为它们不是开源的，因此VirtualBox是一个很好的起点。
- 你可以学到很多有关设备驱动和OS内部的知识，因为在研究过程中，很可能会阅读很多设备规范，Linux驱动程序和模拟设备的源代码。
这次，我通过fuzzing找到了两个DoS（[2020年4月](https://www.oracle.com/security-alerts/cpuapr2020.html)修补），还通过手动审查代码发现了一个可能导致客户到主机逃逸的double free（[2020年7月](https://www.oracle.com/security-alerts/cpujul2020.html)修补）。

尽管本文有很多对VirtualBox的非官方GitHub镜像的链接和引用，但如果你想自己阅读代码，我还是建议从[官方网站](https://www.virtualbox.org/wiki/Downloads)下载相应版本的源代码。我贴这些链接只是出于可读性的考虑，因为我不想在正文中混入很多代码片段。



## 0x01 背景调研

开始漏洞研究时，每个人都应该做的第一件事就是尝试寻找有关先前发现的bug的资源。对我而言，雷诺·罗伯特（Reno Robert）[撰写的文章](https://www.voidsecurity.in/)的价值极高。从他的博客中可以了解项目的全局架构，源代码树的组织方式，发现有趣类型的bug以及许多其他内容。到目前为止，他个人博客中描述的我个人[最喜欢的bug](https://www.voidsecurity.in/2018/08/from-compiler-optimization-to-code.html)是由编译器优化引入的。

Niklas Baumstark向我们提供了另一些非常有价值的资源。他做了一个非常有趣的演讲（[视频](https://www.youtube.com/watch?v=fFaWE3jt7qU)，[幻灯片](https://github.com/phoenhex/files/raw/master/slides/unboxing_your_virtualboxes.pdf)），其中涵盖了多个攻击面，发现的安全问题以及进一步研究的方向。他还在phoenhex团队博客中写了一篇有关他发现的VirtualBox 3D加速bug的[文章](https://phoenhex.re/2018-07-27/better-slow-than-sorry)。

如果你已经看过Niklas的演讲，那么就应该知道Google Project Zero成员也提供了一些有益的报告（James Forshaw的[博客](https://googleprojectzero.blogspot.com/2017/08/bypassing-virtualbox-process-hardening.html)和Jann Horn的[报告](https://bugs.chromium.org/p/project-zero/issues/detail?id=1091)）。他们告诉我们，VirtualBox漏洞不仅限于通过内存破坏实现逃逸，除此之外，如果能找到一种访问VirtualBox主机驱动程序的方式，则在主机系统上还有提权的可能。我十分建议你观看尼克拉斯的演讲，因为他在演讲中提供了有关此攻击面的有趣细节。

最后，Phạm Hồng Phi对Intel PRO / 1000 MT Desktop（82540EM）设备模拟代码中的bug进行了[研究](https://github.com/hongphipham95/Vulnerabilities/blob/master/VirtualBox/Oracle%20VirtualBox%20Intel%20PRO%201000%20MT%20Desktop%20-%20Integer%20Underflow%20Vulnerability/Oracle%20VirtualBox%20Intel%20PRO%201000%20MT%20Desktop%20-%20Integer%20Underflow%20Vulnerability.md)，该网卡设备也常称为E1000或e1k。在以NAT网卡模式启动VM时，它是默认的网络（模拟）设备。最近，他还发表了一篇有趣的[文章](https://starlabs.sg/blog/2020/04/adventures-in-hypervisor-oracle-virtualbox-research/)，涵盖了fuzz e1k设备代码的过程。

以上信息很多，但是如果通读了这些信息，那么现在你应该可以选择自己的路径，开始着手编写代码了。就个人而言，我决定暂时盯住内存破坏漏洞，并在默认VM设置下的网络模拟代码中寻找虚拟机逃逸。

为了探索这个攻击面，我假设攻击者在客户机中具有足够的特权，能够与模拟设备进行通信，或打开高特权的原始套接字（raw sockets）。在大多数情况下，这意味着攻击者在客户操作系统内具有root特权。



## 0x02 网络部份概述

在模拟环境中发送网络数据包的过程对于客户机操作系统是完全透明的。它通过I/O内存或I/O端口与虚拟化的e1k设备进行通信，其方式和与真实设备进行通信的方式相同。模拟设备将重构网络数据包并将其封装到下一层——也就是NAT。由于客户机和主机在NAT网络中都有自己的IP地址，因此客户机发送到全局网络的每个数据包都必须进行解析和编辑。更新的数据包必须包含源IP和目标IP的更新值以及新的校验和。此过程在TCP/IP模拟库“slirp”中实现。取决于所使用的协议，slirp可以将数据包发送到外界或完全模拟网络通信，和它处理DHCP或ARP协议的做法一样。

从各种文章中我们已经知道，在上述每一层上以前都存在漏洞，也许还剩下一些漏洞没发现。要找到这些bug，我们可能必须使用一些新方法或非常仔细地寻找更隐蔽的bug。



## 0x03 挖掘漏洞

我们将要探索的主要函数之一是`void slirp_input(PNATState pData, struct mbuf *m, size_t cbBuf)`（[代码](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/ea2f8471f3e3982d5a9319045c84a2bb6012ef59/src/VBox/Devices/Network/slirp/slirp.c#L1376)），这个函数是TCP/IP模拟开始的地方。传递给此函数的每个处理后的网络数据包都包裹在一个特殊的`mbuf`结构中，值得特别注意。`struct mbuf`是一个遗留产物，它是大多数TCP/IP堆栈从BSD系统继承下来的。互联网上有数种slirp的实现，其中大多数使用了这种奇怪的产物。例如，QEMU的TCP/IP堆栈基于libslirp公共库，它也使用`mbuf`结构。但是，从VirtualBox源码的版权声明中可以看到，它们的slirp个人版本是基于FreeBSD实现的。因此，我们将必须了解此结构的布局和mbuf管理接口，以便能够阅读代码。如果想了解mbuf接口，建议你通读此[页面](https://www.freebsd.org/cgi/man.cgi?query=mbuf&amp;sektion=9&amp;manpath=freebsd-release-ports)。

我们从Reno Robert的博客中知道，slirp模块以前曾发现多个漏洞，但我没有证据表明有人利用覆盖率指导的fuzzing来尝试在其中寻找漏洞。在这种情况下，只有一种方法可以检验——对slirp进行fuzz，看看会发现什么。目前我个人最喜欢的fuzzer是libfuzzer，用它来fuzz `slirp_input`很容易。要编写最简单的目标函数，我们只需要使用提供给我们的API创建`mbuf`，里面包含我们的数据。目标函数这块非常简单，其实最困难的部分是独立编译slirp而不带VirtualBox的其余部分，并对源代码进行patch，因此我们用clang。

以下是我第一次尝试写的`LLVMFuzzerTestOneInput`函数：

```
int LLVMFuzzerTestOneInput(char *d, size_t s)
`{`
    int rc;
    if (s &lt; 10)
        return 0;

    if (!is_slirp_init) `{`
        rc = slirp_init(&amp;pnatstate, 0x2000a, 0xffffff00,
            true, false, 0, 0x64, NULL);
        is_slirp_init = 1;
    `}`

    char *buf = NULL;
    size_t bufsize;

    struct mbuf *m = slirp_ext_m_get(pnatstate, s, &amp;buf, &amp;bufsize);

    buf = mtod(m, char *);
    memcpy(buf, d, s);

    slirp_input(pnatstate, m, s);
    return 0;
`}`
```

细心的读者会发现这个目标函数还有很多问题：
- 所有fuzzing周期都共享一样的NAT状态，这可能导致崩溃无法重现，因为上一个数据包以特殊的方式改变了全局状态。但是这样可以大大加快fuzzing的速度，所以我决定暂且这样，因为计算资源有限。
- 用这个目标函数不大可能会找到包重组过程中的任何漏洞，原因很明显。
- 我们尚未讨论mbuf分配器的内部细节。假如根本没用到`malloc`函数怎么办？（剧透：确实没用到）那ASan就无法检测到缓冲区溢出了。幸运的是，等我们深入研究mbuf分配器的内部细节后，这个问题就可以通过[手动污染（manual poisoning）](https://github.com/google/sanitizers/wiki/AddressSanitizerManualPoisoning)来解决。
后面我对目标函数进行了大幅改进，但是即便是用这个简单的目标函数（用来测试fuzzing能否工作的），我也找到了两个漏洞。



## 0x04 CVE-2020-2951

发现的第一个bug是在DHCP模块中通过解引用空指针导致的无特权的DoS，这非常直观（[diff](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/commit/12f298a94c546a17fd3b203d169721d96e14ad89)）。在第431行的`dhcp_decode_request`函数（[代码](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/9d9efa9ce07e5368e7a97cbceb13653aea6f9816/src/VBox/Devices/Network/slirp/bootp.c#L429)）中，对我们很重要的`BOOTPClient * bc`变量被初始化。

要触发此漏洞，必须满足以下条件：
<li>find_addr应该返回NULL，这样在第445行调用后，`bc`将继续为`NULL`
</li>
- server_ip应该为`NULL`，这样我们在第447行检查`server_ip！= NULL`条件时进入else分支
- req_ip应该为NULL，这样我们在第467行检查`req_ip！= NULL`条件时进入else分支
<li>
`bp-&gt; bp_flags`应该设置为`DHCP_FLAGS_B`，以便我们通过`bp-&gt;bp_flags &amp; RT_H2N_U16_C(DHCP_FLAGS_B)`检查，并且`dhcp_stat`现在等于`REBINDING`的值（第476行）</li>
由于在switch-case语句中未处理`REBINDING`值，因此我们将进入`default`情况，并`break`跳出语句，来到`dhcp_send_ack`函数调用（第585行），其中`bc`变量将被解引用，而其值仍等于`NULL`。

关于此漏洞的有趣之处在于，无需超级用户特权即可触发该漏洞，只需要有打开UDP套接字的权限即可。我认为，这可能是在正常环境下仍可通过普通用户权限触发的少数漏洞之一。



## 0x05 CVE-2020-2929

下一个bug是我第一次遇到[和别人撞bug](https://twitter.com/__paulch/status/1250157791643385859)，它是通过访问越界值（[diff](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/commit/f79bfc33d907f93ee8daf0137f148c7b3749652d)）获得的特权DoS。这个bug也非常简单。

在VirtualBox slirp模块的更深层，有一个“libalias”库用于管理每个接口的多个IP地址。在某个时间点，函数`ip_input`正在调用`LibAliasIn`（[代码](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/a8586db2afdd45242d645e94679a2682ed2fb57a/src/VBox/Devices/Network/slirp/ip_input.c#L218)），这是在对IP头部进行初始检查之后立即执行的，因此这意味着尚未对TCP/UDP层数据进行任何检查。而LibAlias则错误地假设该头部（在我们的情况下为udp）格式正确。

LibAlias将判断协议并将数据包传递给`UdpAliasIn`函数（[代码](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/a8586db2afdd45242d645e94679a2682ed2fb57a/src/VBox/Devices/Network/slirp/libalias/alias.c#L733)）。之后，它将判断更高级别的协议，并将其传递给适当的协议处理程序（请参见`find_handler`函数）。在我们的案例中，漏洞位于netbios协议（[代码](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/a8586db2afdd45242d645e94679a2682ed2fb57a/src/VBox/Devices/Network/slirp/libalias/alias_nbt.c#L857)）的处理程序中。该函数假定数据包的结尾位于`pmax = (char *)uh + ntohs(uh-&gt;uh_ulen);`（第886行），并且不检查`uh-&gt;uh_ulen`值，因此它可能指向ip数据包之外，同时，`uh-&gt;uh_ulen`是由远程用户控制的`uint16_t`值。由于这个原因，在AliasHandleQuestion或AliasHandleResource（例如[这里](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/a8586db2afdd45242d645e94679a2682ed2fb57a/src/VBox/Devices/Network/slirp/libalias/alias_nbt.c#L502)）中会发生越界读取，从而导致DoS，因为在访问分配给mbufs的区域之外的内存。

要触发此错误，必须能够访问原始套接字，因为我们需要诱使内核将带有无效头的UDP数据包传递给网卡。你可能会问有关此bug的几个问题：
- 这也算bug？一旦可以访问原始套接字，攻击者就可以不用触发内存破坏bug而关闭系统。我能想到的唯一情景就是攻击者在Linux上有CAP_NET_RAW能力，但无法关机。确实，这个情况并不太现实。但是甲骨文还是觉得内存破坏bug也是bug，以积极的态度应对并颁发了CVE。
- 我已经说过这个bug和Vishnu Dev TJ相撞了，他把bug报告给了ZDI。问题是[ZDI为什么把漏洞分类](https://www.zerodayinitiative.com/advisories/ZDI-20-508/)为“远程代码执行”呢？我看来这个bug显然是越界读，导致DoS。调查了一番后，我还是没找到能“远程”执行代码的可能。也许是我错了，所以我很乐意看到关于此bug的利用方式的任何信息。


## 0x06 CVE-2020-14713

这些结果告诉我们，到目前为止，slirp模块还没被fuzz个底朝天。你可以尝试查找一些我和其他研究人员遗漏的棘手漏洞。

我知道我最后的fuzzer也不是很完美，我没有时间完全解决fuzz IP包重组的问题，但是在阅读了几次代码后，我没有发现任何与安全性相关的问题。

接下来是本文主要部分，这正是我决定撰写此博文的原因。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E"></a>漏洞

首先，我要说的是，此漏洞只能在主机非Windows系统的情况下触发，因为ICMP在Windows中的处理方式不同。

在手动检查ICMP模拟的代码时，我偶然发现了`icmp_input`函数（[代码](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/fcab9f5c45c37fc354346a40296e529eba74d6a4/src/VBox/Devices/Network/slirp/ip_icmp.c#L533-L563)）中有趣的代码部分。这部分代码负责处理ICMP回显请求并将其发送到外部网络。首先，让我们花点时间看一下此函数的一些结束时的状态：存在一个名为`end_error_free_m`的错误状态，该状态会释放分配的`mbuf`，还有`done`状态，表示缓冲区已经释放过，不需要再次释放。

仔细研究`sendto`发送失败的情况。在这种情况下，将调用`icmp_error`函数，然后控制流将到达switch-case的末尾，从而导致`end_error_free_m`状态。但是，如果我们查看`icmp_error`函数，就能够看到它实际上总是在结束之后释放第二个参数。甚至该功能上方的注释也表明了这一点。似乎在`icmp_error`调用之后少了一句`goto done;`。结果，`mbuf`第一次在`icmp_error`中释放，在`icmp_input`中到达`m_freem(pData, m);`时再次释放。看起来完全是一个漏洞！但是为了确定这是漏洞，我们必须研究分配算法的代码。

我们从`DrvNAT.cpp`中可以了解到，函数`slirp_ext_m_get`（[代码](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/fcab9f5c45c37fc354346a40296e529eba74d6a4/src/VBox/Devices/Network/DrvNAT.cpp#L527)）负责分配mbuf，稍后将其传递给`slirp_input`。可以从`slirp_ext_m_get`中看到，根据大小，可以为我们分配几种类型的缓冲区。分配过程稍后在`m_getjcl`函数中继续进行，该函数是mbuf接口（[代码](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/fcab9f5c45c37fc354346a40296e529eba74d6a4/src/VBox/Devices/Network/slirp/bsd/sys/mbuf.h#L588)）中的函数。在此函数中，我们可以看到存在多个分配“区域”（zones）。结构`mbuf`是从全局`zone_mbuf`中分配的（第598行），带有原始数据的缓冲区将根据其大小在另一个`zone`中分配（第605-607行）。在`uma_zalloc_arg`[函数](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/fcab9f5c45c37fc354346a40296e529eba74d6a4/src/VBox/Devices/Network/slirp/misc.c#L379)内部，我们可以看到对区域上了一些锁，并调用了`zone-&gt;pfAlloc`和`zone-&gt;pfCtor`。通过动态分析（gdb上场），我知道这些值应等于以下值：

```
pfCtor = &lt;mb_ctor_clust&gt;,
pfDtor = &lt;mb_dtor_clust&gt;,
pfInit = NULL,
pfFini = NULL,
pfAlloc = &lt;slirp_uma_alloc&gt;,
pfFree = &lt;slirp_uma_free&gt;,
```

最后，[函数](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/fcab9f5c45c37fc354346a40296e529eba74d6a4/src/VBox/Devices/Network/slirp/misc.c#L153)`slirp_uma_alloc`包含基于空闲列表的实际分配算法，与现代分配器相比，它看起来非常简单。在大多数情况下，调用此函数将从当前列表（行180）进行脱链（unlink），插入已用列表（行181），仅此而已。空闲列表已在初始化阶段从`mbuf_init`函数调用`uma_zone_set_max`（[代码](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/fcab9f5c45c37fc354346a40296e529eba74d6a4/src/VBox/Devices/Network/slirp/misc.c#L329)）时被填充。

从`slirp_uma_free`[函数](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/fcab9f5c45c37fc354346a40296e529eba74d6a4/src/VBox/Devices/Network/slirp/misc.c#L236)可以看到，取消分配的方式几乎就是反过来。它从当前列表脱链，并将其链接到空闲列表。

这意味着在释放一个mbuf两次之后，我们将不可能连续两次分配相同的缓冲区。在第一次调用`m_freem`时，将把chunk从已用列表放入空闲列表，在第二次调用中，将chunk从空闲列表摘下，然后再次链接回空闲列表。这是设计来防御double free的！游戏到此结束了吗？

### <a class="reference-link" name="%E6%98%AF%EF%BC%8C%E4%B9%9F%E4%B8%8D%E6%98%AF"></a>是，也不是

当然，我第一反应是这里没有bug，因此我放弃了这一点，决定继续回顾一些e1k设备模拟代码。阅读一些代码后，`drvNATNetworkUp_SendBuf`[函数](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/fcab9f5c45c37fc354346a40296e529eba74d6a4/src/VBox/Devices/Network/DrvNAT.cpp#L590)引起了我的注意。当e1k模拟器重建网络数据包并准备将其交给slirp时，将从`e1kTransmitFrame`[调用此函数](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/fcab9f5c45c37fc354346a40296e529eba74d6a4/src/VBox/Devices/Network/DevE1000.cpp#L4110)作为回调。但是此函数实际上并不会调用`slirp_input`或以任何方式处理数据包，而是创建一个函数调用请求，将其放入名为`hSlirpReqQueue`的请求队列中，另一个名为`TaskSet0`的线程将处理该请求。但是[缓冲区分配过程实际上发生](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/fcab9f5c45c37fc354346a40296e529eba74d6a4/src/VBox/Devices/Network/DrvNAT.cpp#L527)在从`e1kXmitAllocBuf`（[代码](https://github.com/mdaniel/virtualbox-org-svn-vbox-trunk/blob/fcab9f5c45c37fc354346a40296e529eba74d6a4/src/VBox/Devices/Network/DevE1000.cpp#L3796)）调用`drvNATNetworkUp_AllocBuf`的过程中，这发生在同一`NAT`线程上，没有任何函数调用请求。这意味着缓冲区分配和对`slirp_input`的调用过程发生在不同的线程上。

这使我们可以在`NAT`和`TaskSet0`线程间利用竞争条件，使得在第一次和第二次调用`m_freem`期间发生新的分配。

[![](https://p1.ssl.qhimg.com/t013837d960538545b8.png)](https://p1.ssl.qhimg.com/t013837d960538545b8.png)

在T2时刻的第一次free期间，mbuf `m`将被放置在空闲列表的顶部，在下一次分配（T3）期间，将从空闲列表的顶部选择相同的mbuf并将其再次放置在已用列表中。然后第二次free将发生在slirp线程（T4）中，这会将`m`再次放入空闲列表，并允许我们在T6时再次分配相同的mbuf。

这意味着，至少在处理过程中，我们能够即时更改网络数据包的数据。我创建了一个伪造的e1k Linux驱动程序，该驱动程序以一种特殊的方式将数据包发送到模拟设备上。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8"></a>利用

利用此漏洞很难，因为我们要在微秒级别上搞定竞争条件。我花了一些时间编写完整利用，但是没能完整构造出泄露+代码执行的利用链。因为利用此漏洞需要竞争条件，所以测试起来很困难，所以最后我决定不花那么多时间写代码执行的利用了，我可以拿这个时间去找些别的安全问题。



## 0x07 总结

希望你喜欢本文，也许你学到了新东西。

很蠢的bug也可能逃过质检过程。可能甲骨文质检程序中不进行太多的fuzzing，所以我预计不久还会有更多用fuzzing发现的bug。我也试过用libfuzzer去fuzz e1k设备，但是因为编译遇到许多问题所以没成功。目前，我认为Phạm Hồng Phi在其[文中](https://starlabs.sg/blog/2020/04/adventures-in-hypervisor-oracle-virtualbox-research/)提出的方法是解决所有问题的最佳方案之一。

在slirp或e1k中仍然存在bug，这一点并不让我惊讶。源码diffing可以让我们看到[几个月前](https://twitter.com/__paulch/status/1250475409700986880)还存在的漏洞。

和甲骨文的沟通非常顺利，十分感谢他们。
