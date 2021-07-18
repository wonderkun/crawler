
# 【技术分享】漏洞挖掘之利用Broadcom的Wi-Fi栈（二）


                                阅读量   
                                **119003**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：googleprojectzero.blogspot.tw
                                <br>原文地址：[https://googleprojectzero.blogspot.tw/2017/04/over-air-exploiting-broadcoms-wi-fi_11.html](https://googleprojectzero.blogspot.tw/2017/04/over-air-exploiting-broadcoms-wi-fi_11.html)

译文仅供参考，具体内容表达以及含义原文为准



[![](./img/85992/t01791f7b31ee9d194e.jpg)](http://p6.qhimg.com/t01694de71f9a1bf4d2.jpg)



翻译：[华为未然实验室](http://bobao.360.cn/member/contribute?uid=2794169747)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**<font face="微软雅黑, Microsoft YaHei">传送门</font>**

[**【技术分享】漏洞挖掘之利用Broadcom的Wi-Fi栈（一）**](http://bobao.360.cn/learning/detail/3742.html)



本文将继续研究如何仅通过Wi-Fi通信就实现远程内核代码执行。我们在[上文中](http://bobao.360.cn/learning/detail/3742.html)开发了一个远程代码执行利用方法，使我们能控制Broadcom的Wi-Fi SoC（系统级芯片）。现在我们的任务是，利用该优势将我们的权限进一步提升到内核。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e3b47097bd367c9a.png)

图1

在本文中，我们将探讨攻击主机操作系统的两种不同的途径。在第1部分中，我们将发现并利用Wi-Fi固件和主机之间的通信协议中的漏洞，从而在内核中执行代码。期间，我们也将研究一个一直持续到最近的奇特漏洞，攻击者可利用该漏洞直接攻击内部通信协议，而无需先利用Wi-Fi SoC！在第2部分，我们将探讨使当前配置的Wi-Fi SoC无需漏洞即可完全控制主机的硬件设计选择。

在上一篇文章中讨论的漏洞已披露给Broadcom，并已得到修复，但硬件组件的利用依然如故，现在并无相应的缓解措施。我们希望通过发布这项研究来推动移动SoC制造商和驱动程序供应商打造更安全的设计，从而实现Wi-Fi SoC和应用处理器之间更高程度的分离。

<br>

**第1部分——“较难”方式**

**通信通道**

正如我们在[**上一篇博文**](http://bobao.360.cn/learning/detail/3742.html)中所确立的，Broadcom生产的Wi-Fi固件是一个FullMAC实现。因此其负责处理实施802.11标准（包括大多数[**MLME**](https://wireless.wiki.kernel.org/en/developers/documentation/glossary#mlme)层）所需的大部分复杂性。

然而，虽然许多操作是封装在Wi-Fi芯片的固件中，但在主机操作系统中需要对Wi-Fi状态机进行一定程度的控制。某些事件不能单独由Wi-Fi SoC处理，必须传达给主机的操作系统。例如，必须向主机通知Wi-Fi扫描的结果，以便能将该信息呈现给用户。

为了方便主机和Wi-Fi SoC希望彼此通信的情况，需要一个特殊的通信通道。

但是别忘了，Broadcom生产可通过多种不同的接口（包括USB、SDIO甚或PCIe）连接到主机的各种Wi-Fi SoC。这意味着依靠底层通信接口可能需要为每个受支持的通道重新实现共享通信协议——这是一个非常繁琐的任务。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f5e1574b9f606782.png)

图2

或许有一个更简单的方法？我们一直可以确定的一件事是，无论使用哪个通信通道，芯片都必须能够将接收到的帧传送回主机。实际上，或许正是出于该原因，Broadcom选择搭载在该通道之上，以便在SoC和主机之间建立通信通道。

当固件希望通知主机事件时，其只要编码一个“特殊”帧并将其发送到主机即可。这些帧由“唯一的”[EtherType](https://en.wikipedia.org/wiki/EtherType)值[0x886C](https://android.googlesource.com/kernel/common.git/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/include/proto/ethernet.h#84)标记。其不包含实际接收到的数据，而是封装了有关必须由主机驱动程序处理的固件事件的信息。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b6c797c724574e90.png)

图3

**确保通道安全性**

现在，让我们切换到主机侧。在主机上，可在逻辑上将驱动程序分为若干层。较低层处理通信接口本身（比如SDIO、PCIe，等等）和所绑定的任何传输协议。较高层然后处理帧的接收及其后续处理（如果需要）。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016ffd93ef5cd11a92.png)

图4

首先，上层对接收到的帧执行一些初始处理，例如去除可能已经添加到其上的封装数据（比如由PHY模块添加的传输功率指示符）。然后必须作出一个重要的区分——这是一个只需转发到相关网络接口的常规帧，还是实际上是一个主机必须处理的编码事件？

正如我们刚刚看到的，这一区分很容易作出。只需查看ethertype，并检查其是否具有“特殊”值0x886C即可。如果有，则处理封装事件并丢弃帧。

或许是？事实上，不能保证该ethertype不在其他网络和设备中使用。HPNA芯片中使用的LARQ协议碰巧也使用相同的ethertype。

这将我们的第一个问题摆在了面前——Wi-Fi SoC和主机驱动程序如何对外部接收到的具有0x886C ethertype的帧（应该转发到网络接口）和内部生成的事件帧（不应该从外部来源收到）进行区分？

这是一个关键问题，内部事件通道极其强大，提供了一个巨大的、基本不受审查的攻击面。如果攻击者能通过无线方式注入随后可被驱动程序作为事件帧处理的帧，那么其很可能在主机的操作系统中实现代码执行。

直到本研究发表的几个月前（2016年中），固件并不过滤这些帧。作为数据RX路径的一部分接收的任何帧，无论其是何种ethertype，均只是被盲目转发到主机。因此，攻击者能够远程发送包含特殊0x886C ethertype的帧——随后被驱动程序当做固件本身创建的事件帧处理。

那么，这个问题是如何解决的？我们已经明确，仅仅过滤ethertype本身是不够的。观察打补丁前和打补丁后的固件版本可以得到答案：Broadcom采用的是针对Wi-Fi SoC的固件和主机驱动程序的[组合补丁](https://android.googlesource.com/kernel/msm.git/+/android-6.0.1_r0.92%5E!/)。

该补丁给固件的RX路径和驱动程序添加了验证方法([is_wlc_event_frame](https://android.googlesource.com/kernel/msm.git/+/android-6.0.1_r0.92/drivers/net/wireless/bcmdhd/bcmevent.c#209))。在芯片侧，在将接收到的帧发送到主机之前立即调用该验证方法。如果验证方法将该帧视为事件帧，则其被丢弃。否则，该帧被转发到驱动程序。然后，驱动程序对接收到的具有0x886C ethertype的帧调用完全相同的验证方法，并只在其通过相同的验证方法后才对其进行处理。以下是此流程的简短示意图：

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f02e9b76c254ac40.png)

图5

只要驱动程序和固件中的验证方法保持一致，外部接收的帧就不能被驱动程序作为事件处理。到目前为止这没有问题。

然而，由于我们已经在Wi-Fi SoC上实现了代码执行，所以我们可以简单地“还原”补丁。我们要做的仅是撤掉”固件中的验证方法，从而使任何接收到的帧再次被盲目转发给主机。这反过来使我们能将任意消息注入到主机和Wi-Fi芯片之间的通信协议中。此外，由于验证方法是存储在RAM中，所有RAM均被标记为RWX，所以这与将“MOV R0, #0; BX LR”写入函数的序言中一样简单。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016f5855d11648a0a9.png)

图6

**攻击面**

如前所述，内部通信通道暴露的攻击面是巨大的。跟踪来自处理事件帧（[dhd_wl_host_event](https://android.googlesource.com/kernel/common.git/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/dhd_linux.c#7454)）的入口点的控制流，我们可以看到若干事件受到“特殊处理”，并被独立处理（参见[wl_host_event](https://android.googlesource.com/kernel/common.git/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/dhd_common.c#1500)和[wl_show_host_event](https://android.googlesource.com/kernel/common.git/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/dhd_common.c#1162)）。初始处理完成后，帧随即被插入到队列中。事件然后被唯一目的是从队列中读取事件并将其分派到相应的处理程序函数的[内核线程](https://android.googlesource.com/kernel/common.git/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/wl_cfg80211.c#9961)移出队列。这种相关性是通过使用事件的内部“event-type”字段作为名为evt_handler的[处理函数数组](https://android.googlesource.com/kernel/common.git/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/wl_cfg80211.c#9772)的索引来完成的。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f2691250a717b554.png)

图7

虽然支持的事件代码多达144种，但是Android的主机驱动程序bcmdhd只支持其中很小的一部分。尽管如此，驱动程序中支持大约35个事件，每个事件都包含自己精心设计的处理程序。

现在我们已确信攻击面足够大，所以我们可以开始寻找bug了！不巧的是，Wi-Fi芯片似乎被认为是“受信任的”，因此，主机驱动程序中的一些验证是不够的。事实上，通过审查上面列出的相关处理函数和辅助协议处理程序，我们发现了[大量的漏洞](https://bugs.chromium.org/p/project-zero/issues/detail?id=1064)。

**漏洞**

仔细研究我们发现的漏洞，我们可以看到这些漏洞彼此间均略有不同。一些允许较强的原语，一些允许较弱的原语。但是，最重要的是，其中很多有各种先决条件，满足后方可成功触发，一些仅限于某些物理接口，其他的仅在一定的驱动程序配置下有效。不过，有[一个漏洞](https://bugs.chromium.org/p/project-zero/issues/detail?id=1061)似乎在所有版本的bcmdhd和所有的配置中存在——如果能成功利用该漏洞，那就搞定了。

我们来仔细看看讨论中的事件帧。"WLC_E_PFN_SWC"类型的事件用于指示固件中发生了“重要Wi-Fi改动”（SWC），且必须由主机处理。主机的驱动程序不是直接处理这些事件，而只是从固件中收集所有传输的数据，并通过Netlink向[cfg80211](https://wireless.wiki.kernel.org/en/developers/documentation/cfg80211)层广播“供应商事件”数据包。

更具体而言，由固件发送的每个[SWC事件帧](https://android.googlesource.com/kernel/common.git/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/include/wlioctl.h#2653)均包含一个事件数组（类型为[wl_pfn_significant_net_t](https://android.googlesource.com/kernel/common.git/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/include/wlioctl.h#2646)）、总计数（total_count）及数组中的事件数（pkt_count）。由于事件总数可能相当大，所以其可能无法容纳在一个帧中（即其可能大于[最大MSDU](https://en.wikipedia.org/wiki/Maximum_transmission_unit#MTUs_for_common_media)）。在这种情况下，可以连续发送多个SWC事件帧——其内部数据将由驱动程序累积，直到达到总计数，此时，驱动程序将处理整个事件列表。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010bd3316e139eb54e.png)

图8

通读驱动程序的代码，我们可以看到，当接收到此事件代码时，将触发一个初始处理程序来处理该事件。然后处理程序内部调用“[dhd_handle_swc_evt](https://android.googlesource.com/kernel/common.git/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/dhd_pno.c#3569)”函数来处理事件的数据。我们来仔细看看：

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c705f09a50a3a531.png)

图9

（其中“event_data”是封装在从固件传入的事件中的任意数据）

从上面可以看到，如上所述，函数首先分配一个数组来保存事件的总计数（如果之前未分配），然后继续从缓冲区中相应的索引（results_rxed_so_far）开始连接封装的数据。

但是，处理程序无法验证total_count和pkt_count之间的关系！其只是“信任”“total_count足够大，可以保存所有后续传入的事件”之断言。因此，能够注入任意事件帧的攻击者可以指定一个小的total_count和一个较大的pkt_count，从而可触发一个简单的内核堆溢出。

**远程内核堆整形**

一切都没有问题，但是我们如何从远程有利位置来利用该原语？因为我们不在设备的本地位置，所以我们无法收集有关堆的当前状态的任何数据，也没有与地址空间相关的信息（除非我们能以某种方式泄漏此信息）。针对内核堆溢出的许多经典利用依赖于对内核堆进行整形的能力，即确保在触发溢出之前处于某种状态——我们目前也缺乏这一能力。

我们对分配算符本身有什么了解？kmalloc分配算符（[SLAB](https://en.wikipedia.org/wiki/Slab_allocation)、[SLUB](https://en.wikipedia.org/wiki/SLUB_(software))、[SLOB](https://en.wikipedia.org/wiki/SLOB)）有一些可能的底层实现，可在构建内核时配置。但是，在绝大多数设备上，kmalloc使用“SLUB”——一种未队列化的per-CPU高速缓存“[slab分配算符](https://en.wikipedia.org/wiki/Slab_allocation)”。

每个“slab”只是一个小区域——从该区域雕刻相同大小的分配。每个slab中的第一个块包含其元数据（例如slab的freelist），后续块包含分配本身，没有内联元数据。有一些预定义的由kmalloc使用的slab大小类，大小通常小至64字节，大至约8KB。不出所料，分配算符为每个分配使用最适合的slab（足够大的最小slab）。最后，slab的freelist被线性消耗——连续的分配占用连续的内存地址。但是，如果对象在slab中被释放，则其可能变得碎片化——导致后续的分配填入slab中的“孔”中，而非线性进行。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c666747a5688b46f.png)

图10

考虑到这一点，让我们后退一步，分析一下手头的原语。首先，由于我们能够任意指定total_count中的任何值，所以我们可以选择溢出缓冲区的大小作为sizeof（wl_pfn_significant_net）的任何倍数。这意味着我们可以使用我们选择的任何slab缓存大小。因此，我们可以瞄准溢出的对象的大小没有限制。但是，这还不够。我们对slab的目前状态仍然一无所知，也不能触发我们选择的slab中的远程分配。

似乎我们首先需要找到一个方法来对slab进行远程整形。但是回想一下，我们需要克服一些障碍。由于SLUB保持per-CPU高速缓存，所以执行分配的内核线程的亲和性必须与分配溢出缓冲区的内核线程相同。在不同的CPU内核上获取堆整形原语将导致从不同的slab进行分配。解决这个问题的最简单的方法是将我们限制在可以从发生溢出的同一个内核线程中触发的堆整形原语。这是一个相当大的限制，实质上，这强制我们忽略由于事件处理本身外部的进程所导致的分配。

无论如何，有了具体目标后，我们可以开始在每个事件帧的注册处理程序中寻找堆整形原语了。幸运的是，审查过每个处理程序后，我们找到了非常适合的一个。

“WLC_E_PFN_BSSID_NET_FOUND”类型的事件帧由处理函数dhd_handle_hotlist_scan_evt处理。该函数累积扫描结果的链表。每次接收到一个事件时，其数据被附加到列表中。最后，当一个带标记（表明事件是链中的最后一个事件）事件到达时，该函数传递收集的待处理事件列表。我们来仔细看看：

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e0f6cf77f1d03b8d.png)

图11

太棒了——看看上面的函数，似乎我们可以反复导致大小分配{ sizeof(gscan_results_cache_t) + (N-1) * sizeof(wifi_gscan_result_t) | N &gt; 0 } （其中N表示结果-&gt;计数）。此外，这些分配是在同一个内核线程中执行，其生命周期完全由我们控制！只要我们不发送具有PFN_COMPLETE状态的事件，则不会释放任何分配。

在我们继续之前，我们需要选择一个目slab大小。理想情况下，我们要寻找一个相对不活跃的slab。如果同一CPU上的其他线程选择从同一个slab分配（或释放）数据，这将增加该slab的状态的不确定性，并可能使我们无法成功对其进行整形。在查看/proc/slabinfo并跟踪具有与我们的目标内核线程相同的亲和性的每个slab的kmalloc分配后，我们发现似乎kmalloc-1024 slab最不活跃。因此，我们将选择在我们的利用方法中瞄准这一slab大小。

通过使用上面的堆整形原语，我们可以开始使用“gscan”对象填充任何给定大小的slab。每个“gscan”对象都有一个包含与扫描有关的元数据的短header，和一个指向链表中下一个元素的指针。对象的其余部分然后由“扫描结果”的内联数组填充，携带此节点的实际数据。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d9ada23170899877.png)

图12

回到手头的问题——我们如何使用这个原语制作可预测的布局？

通过将堆整形原语与溢出原语相结合，我们应该能够在触发溢出之前对任何大小类的slab进行正确整形。回想一下，最初任何给定的slab均可能是碎片化的，如下所示：

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015a8f89979b50944b.png)

图13

但是，在用我们的堆整形原语触发足够的分配（比如(SLAB_TOTAL_SIZE / SLAB_OBJECT_SIZE) – 1）后，当前slab中的所有孔（若有）应该被填充，导致后续相同大小类的分配连续进行。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0134048411c42c0bec.png)

图14

现在，我们可以发送一个特制的SWC事件帧，指示一个total_count——导致从同一个目标slab进行的分配。但是，我们还不想触发溢出。在我们这样做之前，我们还必须对当前的slab进行整形。为了防止溢出发生，我们将提供一个小的pkt_count，从而仅部分填充缓冲区。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01603981bc466b511d.png)

图15

最后，再次使用堆整形原语，我们可以用更多的“gscan”对象填充slab的其余部分，这使我们获得以下堆状态：

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013ca681ce38d4a553.png)

图16

我们快要到达目的地了！从上面可以看到，如果我们在这一点上选择使用溢出原语，我们就可以用我们自己的任意数据覆盖其中一个“gscan”对象的内容。但是，我们还没有明确确定这会产生什么样的结果。

**分析限制**

为了确定覆盖“gscan”对象的效果，我们来看看处理一连串“gscan”对象的流程（即接收到标记有“完成”的事件之后执行的操作）。该处理由[wl_cfgvendor_send_hotlist_event](https://android.googlesource.com/kernel/common/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/wl_cfgvendor.c#234)处理。该函数检查列表中的每个事件，将事件的数据打包到SKB中，然后通过Netlink将SKB广播到任何潜在的监听器。

但是，该函数确实有一定的障碍需要克服，任何给定的“gscan”节点均可能大于SKB的最大大小。因此，需要将节点分成若干个SKB。为了跟踪该信息，使用了“gscan”结构中的“tot_count”和“tot_consumed”字段。“tot_count”字段表示在节点内联数组中嵌入的扫描结果条目的总数，“tot_consumed”字段表示到目前为止消耗（传输）的条目数。

因此，该函数在处理列表时对其内容进行了略微修改。其实质上执行不变量，每个处理节点的“total_consumed”字段将被修改，以匹配其“tot_count”字段。至于正在传输的数据及其打包方法，为简洁起见，我们将跳过这些细节。然而，重要的是要注意，除了上述副作用之外，该函数的危害似乎微乎其微（也就是说，无法从其“开采”进一步的原语）。在所有事件均被打包到SKB中并被传送到任何监听器后，就可以将其回收了。这可以通过审查列表并在每个条目上调用“kfree”来实现。

总而言之，这使我们在利用方面处于何种位置？假设我们选择使用溢出原语覆盖其中一个“gscan”条目，那我们可以修改其“next”字段（或者说必须，因为其是结构中的第一个字段），并将其指向任意地址。这将导致处理函数将该任意指针视作列表中的一个元素而予以使用。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b0cd47ce867b845c.png)

图17

由于处理函数的不变量——在处理特制的条目之后，其第7个字节（“tot_consumed”）将被修改，以匹配其第6个字节（“tot_count”）。此外，处理链之后，指针将被kfreed。更重要的是，回想一下，处理函数迭代整个条目列表。这意味着，特制条目（其“next”字段）中的前四个字节必须指向包含“有效”列表节点的另一个内存位置（随后必须满足相同的约束），或必须保持值0（ NULL）——表示这是列表中的最后一个元素。

这看起来不容易…有很多限制我们需要考虑。如果我们故意选择忽略kfree一段时间，我们可以尝试搜索前四个字节为零、有利于修改第七个字节（以匹配第六个字节）的内存位置。当然，这只是冰山一角，我们可以反复触发相同的原语，从而将字节反复向左复制一位。或许，如果我们能找到一个有足够的零字节和足够的我们选择的字节的内存地址，我们就可以通过连续使用这两个原语来制作一个目标值。

为了衡量这种方法的可行性，我已经在一个小的SMT实例中对上述限制进行了编码（使用[Z3](https://github.com/Z3Prover/z3)），并提供了来自内核的实际堆数据，以及各种目标值及其对应的位置。此外，由于内核的转换表存储在内核VAS中的一个不变地址，对其进行略微修改也可能导致可利用的条件，所以其内容（以及相应的目标值）也被添加到了SMT实例中。当且仅当任何目标值可在不超过十个“步骤”（每一步都是原语的调用）内占用任何目标位置时，该实例满足条件。不幸的是，结果相当严峻…似乎这种方法不够强大。

此外，虽然这个想法在理论上可能很好，但实际上并不奏效。要知道，在任意地址调用kfree并不是没有其副作用。包含内存地址的页面必须标记为“slab”页面或“compound”。这通常仅适用于slab分配算符实际使用的页面。尝试在没有标记为此的页面中的地址调用kfree会触发内核恐慌（从而会导致设备崩溃）。

也许，相反，我们可以选择忽略其他约束并专注于kfree？实际上，如果我们始终能找到一个其数据可用于利用目的分配，那么我们就可以尝试释放该内存地址，然后使用我们的堆整形原语“重新捕获”它。然而，这又引起了几个其他问题。首先，我们始终能找到一个常驻slab地址吗？其次，即使我们能找到这样一个地址，其肯定与per-CPU缓存相关联，意味着释放它不一定能让我们可以稍后回收。最后，无论我们选择瞄准哪个分配，都必须满足上面的约束——即前四个字节必须为零，第7个字节将被修改为与第6个字节匹配。

然而，这正是我们可以巧妙利用之处。回想一下，kmalloc保持一些固定大小的缓存。然而，当请求更大的分配时会发生什么？事实证明，在这种情况下，kmalloc只返回一连串的空闲页面（使用[__get_free_pages](http://lxr.free-electrons.com/source/mm/page_alloc.c#L3869)）并将其返回给调用者。这是在没有任何per-CPU缓存的情况下完成的。因此，如果我们能够释放一个大的分配，那我们应该能够在不必首先考虑哪个CPU进行的分配的情况下回收它。

这可能解决了亲和性的问题，但它仍然无法帮助我们找到这些分配。不幸的是，slab缓存在内核引导过程中被分配得相当晚，而且其内容非常“嘈杂”。这意味着猜测slab中的一个地址也是非常困难的，对于远程攻击者而言更甚。但是，使用大分配流的早期分配（即使用__get_free_pages创建的）始终驻于相同的内存地址！也就是只要其在内核初始化期间发生得足够早，因此没有非确定性事件同时发生。

结合这两个事实，我们可以搜索一个大的早期分配。在跟踪大型分配路径并重新引导内核后，似乎确实有很多这样的分配。为了帮助导航此大的踪迹，我们还可以使用一个特殊的GCC插件来编译Linux内核，该插件可输出内核中使用的每个结构的大小。使用这两个踪迹，我们可以快速导航早期大分配，并尝试搜索潜在的匹配。

遍历列表后，我们碰到一个看似有趣的条目：

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c3e3b77f88f628ee.png)

图18

**汇总**

在bcmdhd驱动程序初始化期间，其调用[wiphy_new](http://lxr.free-electrons.com/source/net/wireless/core.c?v=2.6.25#L182)函数来分配一个wl_priv实例。该实例用于保存与驱动程序操作相关的大部分元数据。但是，还有一点诡异的数据隐藏在该结构中——用于处理传入的事件帧的事件处理函数指针数组。事实上，我们之前讨论的同一表格(evt_handler)存储在该对象中。这将我们引向了利用的直接路径——只需kfree这个对象，然后发送一个SWC事件帧来回收它，然后用我们自己的任意数据填充它。

然而，在我们这样做之前，我们需要确保该对象满足处理函数所要求的约束。也就是说，前四个字节必须为零，我们必须能够修改第7个字节以匹配第6个字节的值。第二个约束根本不构成任何问题，但第一个约束是个大问题。如前所述，前四个字节不为零，但实际上指向与驱动程序相关的一个函数指针块。这是否意味着我们完全不能使用这个对象？

不是的——碰巧，我们还有一个诀窍！事实证明，当kfree一个大的分配时，kfree的代码路径不需要传入的指针指向分配的起始。相反，其只是提取与分配相对应的页面，然后释放它们。这意味着通过指定位于匹配约束的结构中的地址，我们将既能满足处理函数提出的要求，又可以释放基础对象。太棒了。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0157403123735fe81d.png)

图19

综合起来，我们现在可以发送一个SWC事件帧，以回收evt_handler函数指针数组，并用我们自己的内容填充它。由于没有KASLR，我们可以在内核映像中搜索一个堆栈枢纽小工具，其可以使我们实现代码执行。出于利用目的，我已选择用堆栈枢纽将WLC_E_SET_SSID的事件处理程序替换为事件帧本身（当执行事件处理程序时存储在R2中）。最后，通过替换专门设计的WLC_E_SET_SSID类型的事件帧中的 ROP栈，我们现在可以控制内核线程的执行，从而可完成我们的利用。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c5be8f4857ed800b.png)

图20

你可以在[此处](https://bugs.chromium.org/p/project-zero/issues/detail?id=1061#c4)找到该漏洞的一个利用示例。其包括一个只调用printk的短ROP链。该利用方法针对使用自定义内核版本的Nexus 5构建。要修改该方法以适用于不同的内核版本，你需要填入适当地符合（symbols.py下）。此外，虽然原语仍然存在于64位设备中，但为了针对那些平台调整利用方法，可能还需要额外的工作。

接下来，让我们转到本文的第二部分。

<br>

**第2部分——“较易”方式**

**能有多简单？**

虽然我们已经看到Wi-Fi固件和主机之间的高级别通信协议可能会受到影响，但我们也看到，要编写一个完全有效的利用方法委实不易。实际上，上述利用方法需要有关目标设备的足够信息（比如符号）。此外，利用期间的任何错误都可能导致内核崩溃，这会导致设备重新启动，这要求我们从头再来。这一事实，再加上我们对Wi-Fi SoC的瞬态控制，使这些类型的利用链很难可靠地利用。

也就是说，到目前为止，我们只考虑了固件暴露的高级别攻击面。实际上，我们是将Wi-Fi SoC和应用处理器作为两个彼此完全独立的不同实体。实际上，没有什么可以远离真相。Wi-Fi SoC和主机不仅物理上彼此接近，还共享物理通信接口。

如前所述，Broadcom生产支持各种接口的SoC，包括SDIO、USB及PCIe。虽然SDIO接口过去很受欢迎，但近年来已不再受移动设备青睐。SDIO“消失”的主要原因是其传输速度有限。Broadcom的BCM4339 SoC支持SDIO 3.0，这是一个相当高级的SDIO版本。尽管如此，其理论最大总线速度仅为104 MB/s。另一方面，802.11ac的理论最大速度为166 MB/s——远超SDIO。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01aaf69c9eaf73149b.png)

图21

**BCM4339框图**

传输速率的提高使得PCIe成为用于在现代移动设备中连接Wi-Fi SoC的最流行的接口。与PCI不同，[PCIe](https://en.wikipedia.org/wiki/PCI_Express)是基于点对点拓扑。每个设备都有将自身连接到主机的自己的串行链路。由于这种设计，PCIe的每通道速率远高于PCI上的同等速率（因为总线访问不需要仲裁），PCIe 1.0在单个通道上的吞吐量为250 MB / s（与通道数呈线性关系）。

我们来具体看看现代移动设备中PCIe的采用率。以Nexus手机为例，从Nexus 6开始，所有设备都使用PCIe接口（不再是SDIO）。同样，所有iPhone也从iPhone 6开始使用PCIe。三星旗舰设备Galaxy从 S6开始使用PCIe。

**接口隔离**

那么，为什么该信息与我们的追求有关？PCIe在隔离方面与SDIO和USB显著不同。SDIO在不进入每个接口的内部的情况下就允许串行传输小命令“数据包”（在CMD引脚上），可能伴随数据（在DATA引脚上）。SDIO控制器然后解码命令并相应响应。虽然SDIO可以支持[DMA](https://en.wikipedia.org/wiki/Direct_memory_access)，但该功能不在移动设备上使用，并不是SDIO的固有部分。此外，BCM SoC上的低级SDIO通信由“SDIOD”内核处理。为了制作特殊的SDIO命令，我们很可能需要先获得对该控制器的访问权。

同样，USB（最高3.1版）不包括对DMA的支持。USB协议由主机的USB控制器进行处理，该控制器执行所需的内存访问。当然，可能可以破坏USB控制器本身，然后将其接口用于内存系统，以获得内存访问权。比如，在Intel Hub Architecture上，USB控制器通过能够进行DMA的PCI连接到[PCH](https://en.wikipedia.org/wiki/Platform_Controller_Hub)。但这种攻击也相当复杂，仅限于特定的架构和USB控制器。

与这两个接口相比，PCIe允许通过设计进行DMA。这允许PCIe以极高的速度运行，而不会导致主机的性能下降。一旦数据传输到主机的内存，就会触发一个中断来指示该工作需要完成。

在事务层上，PCIe通过发送小批量的数据（适当命名为“事务层包”（TLP））进行操作。每个TLP可以由交换机网络路由，直到其到达预定外围设备为止。然后外围设备解码数据包并执行请求的内存操作。TLP的header编码这是否是请求的读取或写入操作，其body包含与请求相关的任何伴随数据。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010ba2925cd2f288d7.png)

图22

**事务层包（TLP）的结构**

**IOU一个MMU**

虽然PCIe支持通过设计实现DMA，但这并不意味着连接到外围设备的任何PCIe都应该能够自由访问主机上的任何内存地址。事实上，现代架构在将外设连接到主存储器的IO总线上具有额外的内存映射单元（[IOMMU](https://en.wikipedia.org/wiki/Input%E2%80%93output_memory_management_unit)），因为具有针对支持DMA的外设的防御能力。

ARM指定其自己的IOMMU版本，称为“[系统内存映射单元](https://developer.arm.com/products/system-ip/system-controllers/system-memory-management-unit)”（SMMU）。使用SMMU的其中一个目的是管理暴露于不同SoC组件的内存视图。简而言之，每个内存事务流都与“流ID”相关联。然后，SMMU执行称为“上下文确定”的一个步骤，以便将流ID转换为相应的内存上下文。

使用内存上下文，SMMU便能够将内存操作与包含请求设备的映射的转换表相关联。很像常规的ARM MMU，查询转换表是为了将输入地址（虚拟地址或中间物理地址）转换为相应的物理地址。当然，期间SMMU也确保请求的内存操作实际上被允许。如果这些步骤中的任何一个失败，就会产生故障。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016a61fa4626bcb3cd.png)

图23

虽然这在理论上很好，但并不意味着SMMU实际上在实践中被使用。不幸的是，移动SoC是专有的，因此很难确定SMMU实际上如何和在哪里就位。话虽如此，我们仍然可以从公开的信息中获取一些洞察力。通过查看Linux内核中的IOMMU绑定，我们可以看到，显然，Qualcomm和三星都有自己的SMMU专有实现，有其自己独特的设备树绑定。但是，可疑的是，Broadcom Wi-Fi芯片的设备树条目似乎缺少这些IOMMU绑定…

相反，Broadcom的主机驱动程序（bcmdhd）也许在每个外围存储器访问之前手动配置SMMU？为了回答这个问题，我们需要仔细看看通过PCIe使用的通信协议的驱动程序实现。Broadcom实现其自己的称为“MSGBUF”的专有协议，以便通过PCIe与Wi-Fi芯片进行通信。主机的协议实现和处理PCIe的代码分别可以在[dhd_msgbuf.c](https://android.googlesource.com/kernel/common/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/dhd_msgbuf.c)和[dhd_pcie.c](https://android.googlesource.com/kernel/common/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/dhd_pcie.c)下找到。

查看代码后，我们获得了对通信协议的内部工作机制的一些关键了解。首先，与预期一致，驱动程序扫描PCIe接口，访问PCI[配置空间](https://en.wikipedia.org/wiki/PCI_configuration_space)，并将所有共享资源映射到主机的内存中。接下来，主机分配一组“环”。每个环均由DMA相干内存区域支持。MSGBUF协议将四个环用于数据流，一个环用于控制。每个数据路径（RX或TX）都有两个相应的环——一个用于指示请求的提交，另一个用于指示其完成。然而，到目前为止，仍然没有提到驱动程序中的SMMU。也许我们要更深入的挖掘…

那么Wi-Fi芯片如何了解这些环的位置？毕竟，到目前为止，其只是在驱动程序中分配的一堆物理连续的缓冲区。查看驱动程序的代码后可知，主机和芯片似乎拥有共享的结构，[pciedev_shared_t](https://android.googlesource.com/kernel/common/+/bcmdhd-3.10/drivers/net/wireless/bcmdhd/include/bcmpcie.h#132)，包含所有PCIe相关元数据，包括每个环形缓冲区的位置。主机保持其自己的该结构的副本，但Wi-Fi SoC在何处保持其副本？根据dhdpcie_readshared函数，似乎Wi-Fi芯片在其RAM的最后四个字节中存储了一个指向此结构的指针。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01678422a5469cccec.png)

图24

我们来继续看看结构的内容。为了略微简化这个过程，我写了一个使用固件RAM快照（使用dhdutil生成）[小脚本](https://bugs.chromium.org/p/project-zero/issues/detail?id=1046#c8)，从RAM的末端读取指向PCIe共享结构的指针，并转出相关的信息：

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013394ee32df436281.png)

图25

在rings_info_ptr字段之后，我们还可以转储有关每个环的信息，包括其大小、当前索引及物理内存地址：

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d7c4e4cf2e537dd9.png)

图26

我们可以看到，这些缓冲区中指定的内存地址实际上似乎是主机内存中的物理内存地址。这有点可疑…在SMMU存在的情况下，芯片应该使用完全不同的地址范围（应该由SMMU转换为物理地址）。但是，仅仅是怀疑是不够的，为了检查SMMU是否存在（或活跃），我们需要设置一个小实验！

回想一下，对于RX和TX路径，MSGBUF协议使用上述环形缓冲区来指示事件的提交和完成。实质上，在帧传输期间，主机写入TX提交环。一旦芯片传输帧，其便写入TX完成环，以指示此情况。同样，当接收到帧时，固件写入RX提交环，随后主机在接收到帧时写入RX完成环。

如果是这样，如果我们修改对应于固件的PCIe元数据结构中的TX完成环的环地址，并将其指向任意的内存地址，结果会如何？如果SMMU就位，并且所选的内存地址未映射到Wi-Fi芯片，则SMMU将生成故障，并且不会进行任何修改。但是，如果没有SMMU，我们就应该能够通过从主机转储相应的物理内存范围（例如，通过使用/dev/mem）来观察此修改。这个小型实验还让我们可以暂时不用对Wi-Fi固件的MSGBUF协议的实现进行逆向工程，该逆向工程毫无疑问是相当繁琐的。

为了使事情更有趣，让我们修改TX完成环的地址，以指向Linux内核代码段的起始（Nexus 6P上的0x80000：见/proc/iomem）。在产生一些Wi-Fi流量并检查物理内存的内容之后，我们得到以下结果：

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01271ddc839f9a9d74.png)

图27

哈哈！Wi-Fi芯片成功DMA到包含主机内核的物理地址范围，没有任何干扰！这最终证实了我们的怀疑，要么不存在SMMU，要么其没有被配置为可防止芯片访问主机的RAM。

这种访问不仅不需要漏洞，还可以更可靠地利用。不需要确切的内核符号或任何其他初步信息。Wi-Fi SoC可以使用其DMA访问来扫描物理地址范围，以定位内核。然后，其可以识别RAM中内核的符号表，分析它来定位其所需的任何内核函数，并通过覆盖其代码来劫持该函数（在类似的类DMA攻击中可以看到一个这样的示例）。总而言之，这种攻击风格完全可移植且100％可靠，相比我们看到的以前的利用方法是一个重大的升级。

我们可以到此为止，不过让我们再稍作努力，以便稍微更好地控制这个原语。虽然我们能DMA进主机的内存，但此时我们是相当“盲目地”实现的。我们不控制正在写入的数据，而是依靠Wi-Fi固件的MSGBUF协议的实现来破坏主机的内存。通过进一步研究，我们应该能够弄清Wi-Fi芯片上的DMA引擎是如何工作的，并手动利用它来访问主机的内存（而不是依赖如上所示的副作用）。

那么我们从哪里开始？搜索“MSGBUF”字符串，我们可以看到与协议相关的一些初始化例程，这是特殊“回收”区域的一部分（因此仅在芯片初始化期间使用）。然而，对这些函数进行逆向工程后表明，其引用Wi-Fi芯片RAM中的一组函数。幸运的是，这些函数的一些名称存在于ROM中！其名称似乎很相关：“dma64_txfast”、“dma64_txreset”——看起来我们在正确的轨道上。

我们再一次避免了一些逆向工程的努力。Broadcom的SoftMAC驱动程序[brcmsmac](https://github.com/torvalds/linux/tree/master/drivers/net/wireless/broadcom/brcm80211/brcmsmac)包含这些确切函数的实现。虽然我们可以预期有一些差异，但总体思路应保持不变。

梳理代码后发现，似乎对于每个具有DMA能力的源或接收器，都存在一个相应的DMA元数据结构，称为“[dma_info](http://lxr.free-electrons.com/source/drivers/staging/brcm80211/brcmsmac/hnddma.c?v=3.0#L77)”。该结构包含指向DMA RX和TX寄存器的指针，以及插入DMA源或目标地址的DMA描述符环。另外，每个结构都被分配一个用于标识自身的8字节的名称。更重要的是，每个dma_info结构都以指向包含DMA函数的RAM函数块的指针开始——与我们之前确定的块相同。因此，我们可以通过在Wi-Fi SoC的RAM中搜索这个指针来定位这些DMA元数据结构的所有实例。

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0187f7c001881615a1.png)

图28

现在我们知道了这些元数据结构的格式，并且有办法找到它们，所以我们可以尝试搜索对应于从Wi-Fi芯片到主机的DMA TX路径的实例。

不过，这说易行难。毕竟，我们可以预期找到这些结构的多个实例，因为Wi-Fi芯片可对多个源和接收器进行正向和反向DMA。比如，固件可能使用SoC内部DMA引擎来访问内部RX和TX FIFO。那么我们如何识别正确的DMA描述符？

回想一下，每个描述符都有一个关联的“名称”字段。我们来搜索RAM中的所有DMA描述符（通过搜索DMA函数块指针），并输出每个实例的相应名称：

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016b4f56bd9ee76f53.png)

图29

太好了！虽然有一些可能在内部使用的难以归类的dma_info实例（和怀疑的一样），但也有两个实例似乎对应于主机到设备（H2D）和设备到主机（D2H）DMA访问。由于我们对DMA进主机的内存感兴趣，所以我们来仔细看看D2H的结构：

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fcfbe113a3b50142.png)

图30

注意，RX和TX寄存器指向Wi-Fi固件的ROM和RAM之外的区域。实际上，其指向对应于DMA引擎寄存器的背板地址。相比之下，RX和TX描述符环指针确实指向SoC的RAM中的内存位置。

通过审查brcmsmac中的DMA代码和主机驱动程序中的MSGBUF协议实现，我们最终得以将细节拼凑起来。首先，主机使用MSGBUF协议将物理地址（对应于SKB）发送到芯片。然后由固件的MSGBUF实现将这些地址插入DMA描述符环中。一旦环被填充，Wi-Fi芯片就会写入背板寄存器，以便“启动”DMA引擎。然后，DMA引擎将审查描述符列表，并在DMA访问的当前环索引处消耗描述符。一旦DMA描述符被消耗，其值便被设置为一个特殊的“魔术”值（0xDEADBEEF）。

因此，为了操纵DMA引擎写入我们自己的任意物理地址，我们需要做的就是修改DMA描述符环。由于MSGBUF协议在帧来回发送时始终运行，所以描述符环快速变化。如果我们可以“钩住”DMA TX流程中调用的其中一个函数，那我们就可以用我们自己设计的值快速替换当前的描述符。

幸运的是，dmx64_txfast函数位于ROM中，其序言从指向RAM的分支开始。这使我们可以使用上一篇博文中的[补丁程序](https://bugs.chromium.org/p/project-zero/issues/detail?id=1046#c9)来挂接这个函数，然后执行我们自己的shellcode存根。我们来写一个小存根，以审查D2H DMA描述符，并将每个非消耗的描述符更改为我们自己的指针。通过这样做，对DMA引擎的后续调用应将接收到的帧的内容写入上述地址。在应用补丁并生成Wi-Fi流量后，我们收获了以下结果：

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01dac7382991ed2d4e.png)

图31

我们成功将任意数据DMA到了我们选择的地址。使用该原语，我们终于可以用我们自己制作的数据来劫持任何内核函数。

最后一点，上述实验是在Nexus 6P（基于Qualcomm的Snapdragon 810 SoC）上进行的。这引起了一个问题：也许不同的SoC会展现不同的行为？为了测试这个理论，让我们在Galaxy S7 Edge（基于三星的Exynos 8890 SoC）上重复相同的实验。

使用[先前披露的权限提升](https://googleprojectzero.blogspot.com/2016/12/bitunmap-attacking-android-ashmem.html)将代码注入到system_server中，我们可以直接发出与bcmdhd驱动程序交互所需的ioctl，从而取代了上述实验中由dhdutil提供的芯片内存访问功能。同样，利用[先前披露的内核利用方法](https://googleprojectzero.blogspot.com/2017/02/lifting-hyper-visor-bypassing-samsungs.html)，我们能够在内核中执行代码，使我们能够观察内核代码段的更改。

综合起来，我们可以提取Wi-Fi芯片（BCM43596）的ROM，对其进行检查，并按照上述方法定位DMA函数。然后我们可以插入相同的挂钩，将任何未消耗的DMA RX描述符指向内核代码的物理地址。安装挂钩并产生一些Wi-Fi流量后，我们观察到以下结果：

[![](./img/85992/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011998cdb189a554ce.png)

图32

我们又一次可以自由DMA进内核（期间绕过了RKP保护）。似乎三星的Exynos 8890 SoC和Qualcomm的Snapdragon 810要么缺乏SMMU，要么未能使用SMMU。

<br>

**结束语**

总而言之，我们已经看到，可以而且应该改进主机和Wi-Fi SoC之间的隔离。虽然主机和芯片之间的通信协议存在缺陷，但是经过一定时间最终可以予以解决。然而，目前缺乏对流氓Wi-Fi芯片的保护令人担忧。

由于移动SoC是专有的，因此当前这一代的SoC是否能够促进这种隔离仍然是未知数。我们希望确实有能力实现内存保护（比如通过SMMU方式）的SoC尽快选择这样做。对于不能这样做的SoC，也许这项研究将成为设计下一代硬件的促进因素。

目前的缺乏隔离也可能会产生一些令人惊讶的副作用。例如，能够[与Wi-Fi固件](http://androidxref.com/7.1.1_r6/xref/system/sepolicy/ioctl_macros#15)交互的Android上下文可以利用Wi-Fi SoC的DMA能力来直接劫持内核。因此，这些上下文应该被认为是“具有内核权限”，我认为，目前安卓的安全架构还没有作出这样的假设。

固件日益复杂，Wi-Fi在不断向前迈进，这两者表明固件bug可能还要徘徊很长一段时间。该假设有事实的支持——即使对固件进行相对浅层的检查也可以发现很多bug，且都可以被远程攻击者利用。

虽然内存隔离本身有助于防御流氓Wi-Fi SoC，但固件的防御也可以支持攻击。目前，固件缺乏利用缓解措施（如堆栈cookie），并没有充分利用现有的安全机制（如MPU）。希望未来的版本能通过实施现代利用缓解措施和采用SoC安全机制来更好地防范这种攻击。

<br>



**传送门**

**[【技术分享】漏洞挖掘之利用Broadcom的Wi-Fi栈（一）](http://bobao.360.cn/learning/detail/3742.html)**


