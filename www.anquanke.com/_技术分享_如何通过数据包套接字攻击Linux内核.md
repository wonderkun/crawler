> 原文链接: https://www.anquanke.com//post/id/86139 


# 【技术分享】如何通过数据包套接字攻击Linux内核


                                阅读量   
                                **166867**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：googleprojectzero.blogspot.hk
                                <br>原文地址：[https://googleprojectzero.blogspot.hk/2017/05/exploiting-linux-kernel-via-packet.html](https://googleprojectzero.blogspot.hk/2017/05/exploiting-linux-kernel-via-packet.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t010aa213fe2fb80481.jpg)](https://p1.ssl.qhimg.com/t010aa213fe2fb80481.jpg)**

****

翻译：[**興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

**稿费：200RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

最近我花了一些时间使用[**syzkaller**](https://github.com/google/syzkaller)工具对Linux内核中与网络有关的接口进行了模糊测试（fuzz）。除了最近发现的[**DCCP套接字漏洞**](http://seclists.org/oss-sec/2017/q1/471)之外，我还发现了另一个漏洞，该漏洞位于数据包套接字（packet sockets）中。在这篇文章中，我会向大家介绍这个漏洞的发现过程，以及我们如何[**利用这个漏洞**](https://github.com/xairy/kernel-exploits/tree/master/CVE-2017-7308)来提升权限。

该漏洞本身（[**CVE-2017-7308**](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-7308)）是一个符号类型漏洞，会导致堆越界（heap-out-of-bounds）写入问题。在启用TPACKET_V3版本的环形缓冲区（ring buffer）条件下，我们可以通过为AF_PACKET套接字的PACKET_RX_RING选项提供特定的参数来触发这个漏洞。漏洞触发成功后，在“net/packet/af_packet.c”源码中，“packet_set_ring()”函数中的完整性检查过程就会被绕过，最终导致越界访问。“packet_set_ring()”函数中的完整性检查过程如下所示：



```
4207                 if (po-&gt;tp_version &gt;= TPACKET_V3 &amp;&amp;
4208                     (int)(req-&gt;tp_block_size -
4209                           BLK_PLUS_PRIV(req_u-&gt;req3.tp_sizeof_priv)) &lt;= 0)
4210                         goto out;
```

2011年8月19日，这个bug与TPACKET_V3的实现一起提交到Github上编号为[**f6fb8f10**](https://github.com/torvalds/linux/commit/f6fb8f100b807378fda19e83e5ac6828b638603a)的commit（“af-packet：TPACKET_V3灵活缓冲区的实现”）。2014年8月15日，在编号为[**dc808110**](https://github.com/torvalds/linux/commit/dc808110bb62b64a448696ecac3938902c92e1ab)的commit中，人们尝试通过添加额外的检查流程来修复这个bug，但根据本文的分析，我们发现这个修复过程并不完美。这个bug最终于2017年3月29日在编号为2b6867c2的[**commit**](https://github.com/torvalds/linux/commit/2b6867c2ce76c596676bec7d2d525af525fdc6e2)中被修复。

如果Linux内核启用了AF_PACKET套接字选项（CONFIG_PACKET=y），那么它就会受到这个漏洞影响，而大多数Linux分发版内核都启用了该选项。漏洞利用需要具备CAP_NET_RAW权限，才能创建这类套接字。然而，如果启用了用户命名空间（user namespace，通过CONFIG_USER_NS=y实现），我们就可能在用户命名空间中使用非特权用户来利用这个漏洞。

由于数据包套接字是Linux内核中广泛应用的一个功能，因此这个漏洞会影响包括Ubuntu、Android在内的许多流行的Linux发行版。需要注意的是，Android中除了某些特权组件之外，明确禁止任何未受信代码访问AF_PACKET套接字。新版的Ubuntu内核已经发布，此外Android也计划在7月份推出更新。

<br>

**二、Syzkaller简介**

我使用syzkaller以及KASAN工具发现了这个bug。Syzkaller是一款针对Linux系统调用的覆盖型模糊测试器，KASAN是一款动态内存错误检测器。我会向大家介绍syzkaller的工作原理，以及如何使用该工具对某些内核接口进行模糊测试，方便大家掌握这个工具。

让我们先来看看syzkaller模糊测试器如何工作。在为每个系统调用（syscall）手动编写描述模板的基础上，syzkaller可以（按照syscall的调用顺序）生成随机的程序。这个模糊测试器会运行这些程序，收集每个程序的代码覆盖情况。通过代码覆盖信息，syzkaller会保存一个程序语料库，触发内核中的不同代码路径。每当新的程序触发了一条新的代码路径（也就是说给出了新的覆盖信息），syzkaller就会将其添加到语料库中。除了生成全新的程序之外，syzkaller也可以更改语料库中的已有程序。

Syzkaller最好搭配动态错误检测器一起使用，如KASAN（从4.0版开始就可以检测诸如越界访问（out-of-bounds）以及释放后重用（use-after-free）之类的内存错误）、KMSAN（可以检查未初始化内存使用错误，原型版本刚刚发布）或者KTSAN（可以检测数据冲突（data race）错误，原型版本已发布）之类的动态错误检测器都可以。Syzkaller可以对内核进行压力测试，执行各种有趣的代码路径，然后错误检测器就能检测并报告对应的错误。

使用syzkaller查找错误的通常流程如下：

1、确保已正确安装syzkaller。可以参考使用说明以及wiki中的详细安装步骤。

2、为待测试的特定内核接口编写模板描述。

3、在syzkaller选项中，指定该接口具体使用的系统调用。

4、运行syzkaller，直到它发现错误为止。通常情况下，如果该接口之前尚未使用syzkaller进行测试，那么这个过程会比较快。

Syzkaller自己有一套声明语言，用来描述系统调用模板。我们可以参考sys/sys.txt中给出的样例，也可以参考sys/README.md给出的语法信息。以下内容截取自我所使用的syzkaller描述信息，用来发现AF_PACKET套接字上的错误：



```
resource sock_packet[sock]
define ETH_P_ALL_BE htons(ETH_P_ALL)
socket$packet(domain const[AF_PACKET], type flags[packet_socket_type], proto const[ETH_P_ALL_BE]) sock_packet
packet_socket_type = SOCK_RAW, SOCK_DGRAM
setsockopt$packet_rx_ring(fd sock_packet, level const[SOL_PACKET], optname const[PACKET_RX_RING], optval ptr[in, tpacket_req_u], optlen len[optval])
setsockopt$packet_tx_ring(fd sock_packet, level const[SOL_PACKET], optname const[PACKET_TX_RING], optval ptr[in, tpacket_req_u], optlen len[optval])
tpacket_req `{`
 tp_block_size  int32
 tp_block_nr  int32
 tp_frame_size  int32
 tp_frame_nr  int32
`}`
tpacket_req3 `{`
 tp_block_size  int32
 tp_block_nr  int32
 tp_frame_size  int32
 tp_frame_nr  int32
 tp_retire_blk_tov int32
 tp_sizeof_priv int32
 tp_feature_req_word int32
`}`
tpacket_req_u [
 req  tpacket_req
 req3  tpacket_req3
] [varlen]
```

大多数语法我们一看就能明白。首先，我们声明了一个新的sock_packet类型。这种类型继承自现有的sock类型。这样一来，对于使用sock类型作为参数的系统调用而言，syzkaller也会在sock_packet类型的套接字上使用这种系统调用。

在这之后，我们声明了一个新的系统调用：socket$packet。“$”符号之前的部分作用是告诉syzkaller应该使用哪种系统调用，而“$”符号之后的部分用来区分同一种系统调用的不同类型。这种方式在处理类似ioctl的系统调用时非常有用。“socket$packet”系统调用会返回一个sock_packet套接字。

然后我们声明了setsockopt$packet_rx_ring以及setsockopt$packet_tx_ring。这些系统调用会在sock_packet套接字上设置PACKET_RX_RING以及PACKET_TX_RING套接字选项。我会在下文讨论这两个选项的具体细节。这两者都使用了tpacket_req_u联合体（union）作为套接字选项的值。tpacket_req_u联合体包含两个结构体成员，分别为tpacket_req以及tpacket_req3。

一旦描述信息添加完毕，我们就可以使用syzkaller对与数据包相关的系统调用进行模糊测试。我在syzkaller管理配置选项中的设置信息如下所示：



```
"enable_syscalls": [
  "socket$packet", "socketpair$packet", "accept$packet", "accept4$packet", "bind$packet", "connect$packet", "sendto$packet", "recvfrom$packet", "getsockname$packet", "getpeername$packet", "listen", "setsockopt", "getsockopt", "syz_emit_ethernet"
 ],
```

使用这些描述信息运行syzkaller一段时间之后，我开始观察到内核崩溃现象。某个syzkaller应用所触发的bug如下所示：



```
mmap(&amp;(0x7f0000000000/0xc8f000)=nil, (0xc8f000), 0x3, 0x32, 0xffffffffffffffff, 0x0)
r0 = socket$packet(0x11, 0x3, 0x300)
setsockopt$packet_int(r0, 0x107, 0xa, &amp;(0x7f000061f000)=0x2, 0x4)
setsockopt$packet_rx_ring(r0, 0x107, 0x5, &amp;(0x7f0000c8b000)=@req3=`{`0x10000, 0x3, 0x10000, 0x3, 0x4, 0xfffffffffffffffe, 0x5`}`, 0x1c)
```

KASAN的某个报告如下所示。需要注意的是，由于访问点距离数据块边界非常远，因此分配和释放栈没有对应溢出（overflown）对象。



```
==================================================================
BUG: KASAN: slab-out-of-bounds in prb_close_block net/packet/af_packet.c:808
Write of size 4 at addr ffff880054b70010 by task syz-executor0/30839
CPU: 0 PID: 30839 Comm: syz-executor0 Not tainted 4.11.0-rc2+ #94
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS Bochs 01/01/2011
Call Trace:
 __dump_stack lib/dump_stack.c:16 [inline]
 dump_stack+0x292/0x398 lib/dump_stack.c:52
 print_address_description+0x73/0x280 mm/kasan/report.c:246
 kasan_report_error mm/kasan/report.c:345 [inline]
 kasan_report.part.3+0x21f/0x310 mm/kasan/report.c:368
 kasan_report mm/kasan/report.c:393 [inline]
 __asan_report_store4_noabort+0x2c/0x30 mm/kasan/report.c:393
 prb_close_block net/packet/af_packet.c:808 [inline]
 prb_retire_current_block+0x6ed/0x820 net/packet/af_packet.c:970
 __packet_lookup_frame_in_block net/packet/af_packet.c:1093 [inline]
 packet_current_rx_frame net/packet/af_packet.c:1122 [inline]
 tpacket_rcv+0x9c1/0x3750 net/packet/af_packet.c:2236
 packet_rcv_fanout+0x527/0x810 net/packet/af_packet.c:1493
 deliver_skb net/core/dev.c:1834 [inline]
 __netif_receive_skb_core+0x1cff/0x3400 net/core/dev.c:4117
 __netif_receive_skb+0x2a/0x170 net/core/dev.c:4244
 netif_receive_skb_internal+0x1d6/0x430 net/core/dev.c:4272
 netif_receive_skb+0xae/0x3b0 net/core/dev.c:4296
 tun_rx_batched.isra.39+0x5e5/0x8c0 drivers/net/tun.c:1155
 tun_get_user+0x100d/0x2e20 drivers/net/tun.c:1327
 tun_chr_write_iter+0xd8/0x190 drivers/net/tun.c:1353
 call_write_iter include/linux/fs.h:1733 [inline]
 new_sync_write fs/read_write.c:497 [inline]
 __vfs_write+0x483/0x760 fs/read_write.c:510
 vfs_write+0x187/0x530 fs/read_write.c:558
 SYSC_write fs/read_write.c:605 [inline]
 SyS_write+0xfb/0x230 fs/read_write.c:597
 entry_SYSCALL_64_fastpath+0x1f/0xc2
RIP: 0033:0x40b031
RSP: 002b:00007faacbc3cb50 EFLAGS: 00000293 ORIG_RAX: 0000000000000001
RAX: ffffffffffffffda RBX: 000000000000002a RCX: 000000000040b031
RDX: 000000000000002a RSI: 0000000020002fd6 RDI: 0000000000000015
RBP: 00000000006e2960 R08: 0000000000000000 R09: 0000000000000000
R10: 0000000000000000 R11: 0000000000000293 R12: 0000000000708000
R13: 000000000000002a R14: 0000000020002fd6 R15: 0000000000000000
Allocated by task 30534:
 save_stack_trace+0x16/0x20 arch/x86/kernel/stacktrace.c:59
 save_stack+0x43/0xd0 mm/kasan/kasan.c:513
 set_track mm/kasan/kasan.c:525 [inline]
 kasan_kmalloc+0xad/0xe0 mm/kasan/kasan.c:617
 kasan_slab_alloc+0x12/0x20 mm/kasan/kasan.c:555
 slab_post_alloc_hook mm/slab.h:456 [inline]
 slab_alloc_node mm/slub.c:2720 [inline]
 slab_alloc mm/slub.c:2728 [inline]
 kmem_cache_alloc+0x1af/0x250 mm/slub.c:2733
 getname_flags+0xcb/0x580 fs/namei.c:137
 getname+0x19/0x20 fs/namei.c:208
 do_sys_open+0x2ff/0x720 fs/open.c:1045
 SYSC_open fs/open.c:1069 [inline]
 SyS_open+0x2d/0x40 fs/open.c:1064
 entry_SYSCALL_64_fastpath+0x1f/0xc2
Freed by task 30534:
 save_stack_trace+0x16/0x20 arch/x86/kernel/stacktrace.c:59
 save_stack+0x43/0xd0 mm/kasan/kasan.c:513
 set_track mm/kasan/kasan.c:525 [inline]
 kasan_slab_free+0x72/0xc0 mm/kasan/kasan.c:590
 slab_free_hook mm/slub.c:1358 [inline]
 slab_free_freelist_hook mm/slub.c:1381 [inline]
 slab_free mm/slub.c:2963 [inline]
 kmem_cache_free+0xb5/0x2d0 mm/slub.c:2985
 putname+0xee/0x130 fs/namei.c:257
 do_sys_open+0x336/0x720 fs/open.c:1060
 SYSC_open fs/open.c:1069 [inline]
 SyS_open+0x2d/0x40 fs/open.c:1064
 entry_SYSCALL_64_fastpath+0x1f/0xc2
Object at ffff880054b70040 belongs to cache names_cache of size 4096
The buggy address belongs to the page:
page:ffffea000152dc00 count:1 mapcount:0 mapping:          (null) index:0x0 compound_mapcount: 0
flags: 0x500000000008100(slab|head)
raw: 0500000000008100 0000000000000000 0000000000000000 0000000100070007
raw: ffffea0001549a20 ffffea0001b3cc20 ffff88003eb44f40 0000000000000000
page dumped because: kasan: bad access detected
Memory state around the buggy address:
 ffff880054b6ff00: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
 ffff880054b6ff80: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
&gt;ffff880054b70000: fc fc fc fc fc fc fc fc fb fb fb fb fb fb fb fb
                         ^
 ffff880054b70080: fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb
 ffff880054b70100: fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb
==================================================================
```

你可以参考syzkaller的代码仓库以了解更多细节，也可以参考KASAN的内核文档部分了解更多细节。如果你在使用syzkaller或者KASAN的过程中遇到任何问题，可以发邮件到syzkaller@googlegroups.com以及kasan-dev@googlegroups.com进行咨询。

<br>

**三、AF_PACKET套接字简介**

为了更好了解这个bug、bug所引发的漏洞以及如何利用这个漏洞，我们需要了解AF_PACKET套接字的相关内容，理解它们在内核中的具体实现方式。

**3.1 概要**

用户可以使用AF_PACKET在设备驱动层发送或者接受数据包。这样一来，用户就可以在物理层之上实现自己的协议，也可以嗅探包含以太网和更高层协议头部的数据包。为了创建一个AF_PACKET套接字，进程必须在用户命名空间中具备CAP_NET_RAW权限，以便管理进程的网络命名空间（network namespace）。你可以参考数据包套接字文档了解更多细节。需要注意的是，如果内核启用了非特权用户命名空间，那么非特权用户就能创建数据包套接字。

进程可以使用send和recv这两个系统调用在数据包套接字上发送和接受数据包。然而，数据包套接字提供了一个环形缓冲区（ring buffer）方式使数据包的发送和接受更为高效，这个环形缓冲区可以在内核和用户空间之间共享使用。我们可以使用PACKET_TX_RING以及PACKET_RX_RING套接字选项创建环形缓冲区。之后，用户可以使用内存映射方式（mmap）映射这个缓冲区，这样包数据就能直接读取和写入到这个缓冲区中。

内核在处理环形缓冲区时有几种不同的处理方式。用户可以使用PACKET_VERSION这个套接字选项选择具体使用的方式。我们可以参考内核文档（搜索“TPACKET versions”关键字），了解不同版本的环形缓冲区之间的区别。

人们熟知的AF_PACKET套接字的一个应用就是tcpdump工具。使用tcpdump嗅探某个接口上的所有数据包时，处理流程如下所示：



```
# strace tcpdump -i eth0
...
socket(PF_PACKET, SOCK_RAW, 768)        = 3
...
bind(3, `{`sa_family=AF_PACKET, proto=0x03, if2, pkttype=PACKET_HOST, addr(0)=`{`0, `}`, 20) = 0
...
setsockopt(3, SOL_PACKET, PACKET_VERSION, [1], 4) = 0
...
setsockopt(3, SOL_PACKET, PACKET_RX_RING, `{`block_size=131072, block_nr=31, frame_size=65616, frame_nr=31`}`, 16) = 0
...
mmap(NULL, 4063232, PROT_READ|PROT_WRITE, MAP_SHARED, 3, 0) = 0x7f73a6817000
...
```

以上系统调用的顺序对应如下操作：

1、创建一个套接字：socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))；

2、套接字绑定到eth0接口；

3、通过PACKET_VERSION套接字选项，将环形缓冲区版本设置为TPACKET_V2；

4、使用PACKET_RX_RING套接字选项，创建一个环形缓冲区；

5、将环形缓冲区映射到用户空间。

在这之后，内核开始将来自于eth0接口的所有数据包存入环形缓冲区中，然后tcpdump会从用户空间中对应的映射区域读取这些数据包。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0182e1539a24452ec9.png)

**3.2 环形缓冲区（ring buffers）**

让我们了解一下如何在数据包套接字上使用环形缓冲区。出于一致性考虑，我们在下文引用的代码片段全部来自于4.8版Linux内核。这个内核也是最新的Ubuntu 16.04.2所使用的内核。

现有的文档主要关注的是TPACKET_V1以及TPACKET_V2版的环形缓冲区。由于本文提到的bug只影响TPACKET_V3版，因此我在下文假设我们处理的都是TPACKET_V3版。另外，我主要关注的是PACKET_RX_RING选项，会忽略另一个PACKET_TX_RING选项。

一个环形缓冲区就是一块存放数据包的内存区域。每个数据包会存放在一个单独的帧（frame）中，多个帧会被分组形成内存块。在TPACKET_V3环形缓冲区中，帧的大小是不固定的，只要帧能够存放到内存块中，它的大小就可以取任意值。

为了使用PACKET_RX_RING套接字选项创建TPACKET_V3环形缓冲区，用户必须为环形缓冲区提供准确的参数值。这些参数会通过一个指向tpacket_req3结构体的指针传递给setsockopt调用，该结构体的定义如下所示：



```
274 struct tpacket_req3 `{`
275         unsigned int    tp_block_size;  /* Minimal size of contiguous block */
276         unsigned int    tp_block_nr;    /* Number of blocks */
277         unsigned int    tp_frame_size;  /* Size of frame */
278         unsigned int    tp_frame_nr;    /* Total number of frames */
279         unsigned int    tp_retire_blk_tov; /* timeout in msecs */
280         unsigned int    tp_sizeof_priv; /* offset to private data area */
281         unsigned int    tp_feature_req_word;
282 `}`;
```

tpacket_req3结构体中每个字段的含义如下所示：

1、tp_block_size：每个内存块的大小；

2、tp_block_nr：内存块的个数；

3、tp_frame_size：每个帧的大小，TPACKET_V3会忽视这个字段；

4、tp_frame_nr：帧的个数，TPACKET_V3会忽视这个字段；

5、tp_retire_blk_tov：超时时间（毫秒），超时后即使内存块没有被数据完全填满也会被内核停用（参考下文）；

6、tp_sizeof_priv：每个内存块中私有区域的大小。用户可以使用这个区域存放与每个内存块有关的任何信息；

7、tp_feature_req_word：一组标志（目前实际上只有一个标志），可以用来启动某些附加功能。

每个内存块都有一个头部与之相关，该头部存放在为这个内存块所分配的内存空间的开头部位。内存块的头部结构为tpacket_block_desc，这个结构中有一个block_status字段，该字段用来标识内存块目前是否正在被内核使用，还是可以提供给用户使用。在通常的工作流程中，内核会将数据包存储在某个内存块中，直到该内存块被填满，之后内核会将block_status字段设置为TP_STATUS_USER。之后用户就可以从内存块中读取所需的数据，读取完毕后，会将block_status设置为TP_STATUS_KERNEL，以便释放内存块，归还给内核使用。



```
186 struct tpacket_hdr_v1 `{`
187         __u32   block_status;
188         __u32   num_pkts;
189         __u32   offset_to_first_pkt;
...
233 `}`;
234 
235 union tpacket_bd_header_u `{`
236         struct tpacket_hdr_v1 bh1;
237 `}`;
238 
239 struct tpacket_block_desc `{`
240         __u32 version;
241         __u32 offset_to_priv;
242         union tpacket_bd_header_u hdr;
243 `}`;
```

同样，每个帧也有一个与之关联的头部，头部结构为tpacket3_hdr，其中tp_next_offset字段指向同一个内存块中的下一个帧。



```
162 struct tpacket3_hdr `{`
163         __u32  tp_next_offset;
...
176 `}`;
```

当某个内存块完全被数据填满时（即新的数据包不会填充到剩余的空间中），内存块就会被关闭然后释放到用户空间中（也就是说被内核停用）。由于通常情况下，用户希望尽可能快地看到数据包，因此内核有可能会提前释放某个内存块，即使该内存块还没有被数据完全填满。内核会维护一个计时器，使用tp_retire_blk_tov参数控制超时时间，当超时发生时就会停用当前的内存块。

还有一种方式，那就是指定每个块的私有区域，内核不会触碰这个私有区域，用户可以使用该区域存储与内存块有关的任何信息。这个区域的大小通过tp_sizeof_priv参数进行传递。

如果你想更加详细了解用户空间程序如何使用TPACKET_V3环形缓冲区，你可以阅读官方文档中提供的具体示例（搜索“TPACKET_V3 example”关键词）。

[![](https://p3.ssl.qhimg.com/t01b8aff0acd687b259.png)](https://p3.ssl.qhimg.com/t01b8aff0acd687b259.png)

<br>

**四、AF_PACKET套接字的具体实现**

我们来快速了解一下AF_PACKET在内核中的具体实现。

**4.1 结构体定义**

每当创建一个数据包套接字时，内核中就会分配与之对应的一个packet_sock结构体对象，如下所示：



```
103 struct packet_sock `{`
...
105         struct sock             sk;
...
108         struct packet_ring_buffer       rx_ring;
109         struct packet_ring_buffer       tx_ring;
...
123         enum tpacket_versions   tp_version;
...
130         int                     (*xmit)(struct sk_buff *skb);
...
132 `}`;
```

这个结构体中，tp_version字段保存了环形缓冲区的版本，在本文案例中，我们通过setsockopt调用，传入PACKET_VERSION参数，将环形缓冲区的版本设置为TPACKET_V3。rx_ring以及tx_ring字段代表接收（receive）和传输（transmit）环形缓冲区，这类缓冲区使用设置了PACKET_RX_RING和PACKET_TX_RING选项的setsockopt调用来创建。这两个字段的类型为packet_ring_buffer，此类型的定义如下：



```
56 struct packet_ring_buffer `{`
57         struct pgv              *pg_vec;
...
70         struct tpacket_kbdq_core        prb_bdqc;
71 `}`;
```

其中pg_vec字段为指向pgv结构体数组的一个指针，数组中的每个元素都保存了对某个内存块的引用。每个内存块实际上都是单独分配的，没有位于一个连续的内存区域中。

```
52 struct pgv `{`
53         char *buffer;
54 `}`;
```

[![](https://p5.ssl.qhimg.com/t01220ffa8904f8b9bc.png)](https://p5.ssl.qhimg.com/t01220ffa8904f8b9bc.png)

prb_bdqc字段的类型为tpacket_kbdq_core结构体，这个结构体的字段描述了环形缓冲区的当前状态，如下所示：



```
14 struct tpacket_kbdq_core `{`
...
21         unsigned short  blk_sizeof_priv;
...
36         char            *nxt_offset;
...
49         struct timer_list retire_blk_timer;
50 `}`;
```

其中blk_sizeof_priv字段包含每个内存块所属的私有区域的大小。nxt_offset字段指向当前活跃的内存块的内部区域，表明下一个数据包的存放位置。retire_blk_timer字段的类型为timer_list结构体，用来描述超时发生后停用当前内存块的那个计时器，如下所示：



```
12 struct timer_list `{`
...
17         struct hlist_node       entry;
18         unsigned long           expires;
19         void                    (*function)(unsigned long);
20         unsigned long           data;
...
31 `}`;
```

**4.2 设置环形缓冲区**

内核使用packet_setsockopt()函数处理数据包套接字的选项设置操作。当使用PACKET_VERSION套接字选项时，内核就会将po-&gt;tp_version参数的值设置为对应的值。

在这之后，内核会使用PACKET_RX_RING套接字选项，创建一个用于数据包接收的环形缓冲区。内核使用packet_set_ring()函数完成这一过程。这个函数做了很多工作，因此我只是摘抄其中比较重要的那部分代码。首先，packet_set_ring()函数会对给定的环形缓冲区参数执行一系列完整性检查操作，如下所示：



```
4202                 err = -EINVAL;
4203                 if (unlikely((int)req-&gt;tp_block_size &lt;= 0))
4204                         goto out;
4205                 if (unlikely(!PAGE_ALIGNED(req-&gt;tp_block_size)))
4206                         goto out;
4207                 if (po-&gt;tp_version &gt;= TPACKET_V3 &amp;&amp;
4208                     (int)(req-&gt;tp_block_size -
4209                           BLK_PLUS_PRIV(req_u-&gt;req3.tp_sizeof_priv)) &lt;= 0)
4210                         goto out;
4211                 if (unlikely(req-&gt;tp_frame_size &lt; po-&gt;tp_hdrlen +
4212                                         po-&gt;tp_reserve))
4213                         goto out;
4214                 if (unlikely(req-&gt;tp_frame_size &amp; (TPACKET_ALIGNMENT - 1)))
4215                         goto out;
4216 
4217                 rb-&gt;frames_per_block = req-&gt;tp_block_size / req-&gt;tp_frame_size;
4218                 if (unlikely(rb-&gt;frames_per_block == 0))
4219                         goto out;
4220                 if (unlikely((rb-&gt;frames_per_block * req-&gt;tp_block_nr) !=
4221                                         req-&gt;tp_frame_nr))
4222                         goto out;
```

之后，函数会分配环形缓冲区的内存块空间：



```
4224                 err = -ENOMEM;
4225                 order = get_order(req-&gt;tp_block_size);
4226                 pg_vec = alloc_pg_vec(req, order);
4227                 if (unlikely(!pg_vec))
4228                         goto out;
```

我们应该注意到，alloc_pg_vec()函数使用了内核页分配器来分配内存块（我们会在漏洞利用中使用这个方法）：



```
4104 static char *alloc_one_pg_vec_page(unsigned long order)
4105 `{`
...
4110         buffer = (char *) __get_free_pages(gfp_flags, order);
4111         if (buffer)
4112                 return buffer;
...
4127 `}`
4128 
4129 static struct pgv *alloc_pg_vec(struct tpacket_req *req, int order)
4130 `{`
...
4139         for (i = 0; i &lt; block_nr; i++) `{`
4140                 pg_vec[i].buffer = alloc_one_pg_vec_page(order);
...
4143         `}`
...
4152 `}`
```

最后，packet_set_ring()函数会调用init_prb_bdqc()函数，后者会通过一些额外的操作，创建一个接收数据包的TPACKET_V3环形缓冲区：



```
4229                 switch (po-&gt;tp_version) `{`
4230                 case TPACKET_V3:
...
4234                         if (!tx_ring)
4235                                 init_prb_bdqc(po, rb, pg_vec, req_u);
4236                         break;
4237                 default:
4238                         break;
4239                 `}`
```

init_prb_bdqc()函数会将环形缓冲区参数拷贝到环形缓冲区结构体中的prb_bdqc字段，在这些参数的基础上计算其他一些参数值，设置停用内存块的计时器，然后调用prb_open_block()函数初始化第一个内存块：



```
604 static void init_prb_bdqc(struct packet_sock *po,
605                         struct packet_ring_buffer *rb,
606                         struct pgv *pg_vec,
607                         union tpacket_req_u *req_u)
608 `{`
609         struct tpacket_kbdq_core *p1 = GET_PBDQC_FROM_RB(rb);
610         struct tpacket_block_desc *pbd;
...
616         pbd = (struct tpacket_block_desc *)pg_vec[0].buffer;
617         p1-&gt;pkblk_start = pg_vec[0].buffer;
618         p1-&gt;kblk_size = req_u-&gt;req3.tp_block_size;
...
630         p1-&gt;blk_sizeof_priv = req_u-&gt;req3.tp_sizeof_priv;
631 
632         p1-&gt;max_frame_len = p1-&gt;kblk_size - BLK_PLUS_PRIV(p1-&gt;blk_sizeof_priv);
633         prb_init_ft_ops(p1, req_u);
634         prb_setup_retire_blk_timer(po);
635         prb_open_block(p1, pbd);
636 `}`
```

prb_open_block()函数做了一些事情，比如它会设置tpacket_kbdq_core结构体中的nxt_offset字段，将其指向紧挨着每个内存块私有区域的那个地址。



```
841 static void prb_open_block(struct tpacket_kbdq_core *pkc1,
842         struct tpacket_block_desc *pbd1)
843 `{`
...
862         pkc1-&gt;pkblk_start = (char *)pbd1;
863         pkc1-&gt;nxt_offset = pkc1-&gt;pkblk_start + BLK_PLUS_PRIV(pkc1-&gt;blk_sizeof_priv);
...
876 `}`
```

**4.3 数据包接收**

每当内核收到一个新的数据包时，内核应该会把它保存到环形缓冲区中。内核所使用的关键函数为__packet_lookup_frame_in_block()，这个函数的主要工作为：

1、检查当前活跃的内存块是否有充足的空间存放数据包；

2、如果空间足够，保存数据包到当前的内存块，然后返回；

3、如果空间不够，就调度下一个内存块，将数据包保存到下一个内存块。



```
1041 static void *__packet_lookup_frame_in_block(struct packet_sock *po,
1042                                             struct sk_buff *skb,
1043                                                 int status,
1044                                             unsigned int len
1045                                             )
1046 `{`
1047         struct tpacket_kbdq_core *pkc;
1048         struct tpacket_block_desc *pbd;
1049         char *curr, *end;
1050 
1051         pkc = GET_PBDQC_FROM_RB(&amp;po-&gt;rx_ring);
1052         pbd = GET_CURR_PBLOCK_DESC_FROM_CORE(pkc);
...
1075         curr = pkc-&gt;nxt_offset;
1076         pkc-&gt;skb = skb;
1077         end = (char *)pbd + pkc-&gt;kblk_size;
1078 
1079         /* first try the current block */
1080         if (curr+TOTAL_PKT_LEN_INCL_ALIGN(len) &lt; end) `{`
1081                 prb_fill_curr_block(curr, pkc, pbd, len);
1082                 return (void *)curr;
1083         `}`
1084 
1085         /* Ok, close the current block */
1086         prb_retire_current_block(pkc, po, 0);
1087 
1088         /* Now, try to dispatch the next block */
1089         curr = (char *)prb_dispatch_next_block(pkc, po);
1090         if (curr) `{`
1091                 pbd = GET_CURR_PBLOCK_DESC_FROM_CORE(pkc);
1092                 prb_fill_curr_block(curr, pkc, pbd, len);
1093                 return (void *)curr;
1094         `}`
...
1101 `}`
```



**五、漏洞分析**

**5.1 Bug分析**

让我们仔细分析一下packet_set_ring()函数中的检查过程，如下所示：



```
4207                 if (po-&gt;tp_version &gt;= TPACKET_V3 &amp;&amp;
4208                     (int)(req-&gt;tp_block_size -
4209                           BLK_PLUS_PRIV(req_u-&gt;req3.tp_sizeof_priv)) &lt;= 0)
4210                         goto out;
```

这个检查过程的目的是确保内存块头部加上每个内存块私有数据的大小不超过内存块自身的大小。这个检查非常有必要，否则我们在内存块中就不会有足够的空间，更不用说能够预留空间存放数据包了。

然而，事实证明这个检查过程可以被绕过。如果我们设置了req_u-&gt;req3.tp_sizeof_priv的高位字节，那么将这个赋值表达式转换为整数（int）则会导致一个非常大的正整数值（而不是负值）。如下所示：



```
A = req-&gt;tp_block_size = 4096 = 0x1000
B = req_u-&gt;req3.tp_sizeof_priv = (1 &lt;&lt; 31) + 4096 = 0x80001000
BLK_PLUS_PRIV(B) = (1 &lt;&lt; 31) + 4096 + 48 = 0x80001030
A - BLK_PLUS_PRIV(B) = 0x1000 - 0x80001030 = 0x7fffffd0
(int)0x7fffffd0 = 0x7fffffd0 &gt; 0
```

之后，在init_prb_bdqc()函数中，当req_u-&gt;req3.tp_sizeof_priv被复制到p1-&gt;blk_sizeof_priv时（参考前文提到的代码片段），它会被分割成两个低位字节，而后者的类型是unsigned short。因此我们可以利用这个bug，将tpacket_kbdq_core结构体中的blk_sizeof_priv设置为任意值，以绕过所有的完整性检查过程。

**5.2 漏洞后果**

如果我们遍历net/packet/af_packet.c的源码，搜索blk_sizeof_priv的用法，我们会发现源码中有两处使用了这个函数。

第一个调用位于init_prb_bdqc()函数中，此时blk_sizeof_priv刚被赋值，用来设置max_frame_len变量的值。p1-&gt;max_frame_len的值代表可以保存到内存块中的某个帧大小的最大值。由于我们可以控制p1-&gt;blk_sizeof_priv，我们可以使BLK_PLUS_PRIV(p1-&gt;blk_sizeof_priv)的值大于p1-&gt;kblk_size的值。这样会导致p1-&gt;max_frame_len取的一个非常大的值，比内存块的大小更大。这样当某个帧被拷贝到内存块中时，我们就可以绕过对它的大小检测过程，最终导致内核堆越界写入问题。

问题还不仅限于此，blk_sizeof_priv的另一个调用位于prb_open_block()函数中，这个函数用来初始化一个内存块（参考上文的代码片段）。在这个函数中，当内核收到新的数据包时，数据包的写入地址存放在pkc1-&gt;nxt_offset中。内核不想覆盖内存块头部以及内存块对应的私有数据，因此它会将这个地址指向紧挨着头部和私有数据之后的那个地址。由于我们可以控制blk_sizeof_priv，因此我们也可以控制nxt_offset的最低的两个字节。这样我们就能够控制越界写入的偏移量。

总而言之，这个bug会导致内核堆越界写入，我们能控制的大小和偏移量最多可达64k字节。

<br>

**六、漏洞利用**

现在让我们研究下如何利用这个漏洞。我的目标系统是x86-64架构的Ubuntu 16.04.2，内核版本为4.8.0-41-generic，内核启用了KASLR、SMEP以及SMAP选项。Ubuntu内核为非特权用户启用了用户命名空间（CONFIG_USER_NS=y，且没有对空间的使用做出限制），因此非特权用户可以利用这个漏洞获取root权限。以下所有的漏洞利用步骤都在用户命名空间中完成。

Linux内核支持某些增强功能，会导致漏洞利用更加困难。KASLR（Kernel Address Space Layout Randomization，内核地址空间布局随机化）机制会将内核文本（kernel text）存放到一个随机的偏移地址，使得攻击者无法通过跳转到特定的固定地址完成攻击；每当内核试图从用户空间内存执行代码时，SMEP（Supervisor Mode Execution Protection，监督模式执行保护）机制就会触发内核的oops错误；每当内核试图直接访问用户空间的内存时，SMAP（Supervisor Mode Access Prevention，监督模式访问防护）机制也能起到同样效果。

**6.1 堆操作**

漏洞的利用思路是利用堆越界写入bug，覆盖内存中与溢出内存块临近的那个函数指针。因此我们需要对堆进行精确处理，使得某些带有可触发函数指针的对象被精确放置在某个环形缓冲区之后。我选择前文提到的packet_sock结构体对象作为这类对象。我们需要找到一种办法，使得内核将一个环形缓冲区内存块和一个packet_sock对象紧紧分配在一起。

正如我前文提到的那样，环形缓冲区内存块通过内核页面分配器进行分配。内核页面分配器可以为内存块分配2^n个连续的内存页面。对于每个n值，分配器会为这类内存块维护一个freelist表，并在请求内存块时返回freelist表头。如果某个n值对应的freelist为空，分配器就会查找第一个满足m&gt;n且其freelist不为空的值，然后将freelist分为两半，直到所需的大小得到满足。因此，如果我们开始以2^n大小重复分配内存块，那么在某些时候，这些内存块会由某个高位内存块分裂所得，且这些内存块会彼此相邻。

packet_sock对象通过slab分配器使用kmalloc()函数进行分配。slab分配器主要用于分配比单内存页还小的那些对象。它使用页面分配器分配一大块内存，然后切割这块内存，生成较小的对象。大的内存块称之为slabs，这也就是slab分配器的名称来源。一组slabs与它们的当前状态以及一组操作(如“分配对象”操作，以及“释放对象”操作)一起，统称为一个缓存（cache）。slab分配器会按照2^n大小，为对象创建一组通用的缓存。每当kmalloc(size)函数被调用时，slab分配器会将size调整到与2的幂最为接近的一个值，使用这个size作为缓存的大小。

由于内核一直使用的都是kmalloc()函数，如果我们试图分配一个对象，那么这个对象很大的可能会来自于之前已经创建的一个slab中。然而，如果我们开始分配同样大小的对象，那么在某些时候，slab分配器将会将同样大小的slab全部用光，然后不得不使用页面分配器分配另一个slab。

新创建的slab的大小取决于这个slab所用的对象大小。packet_sock结构体的大小大约为1920，而1024 &lt; 1920 &lt;= 2048，这意味着对象的大小会调整到2048，并且会使用kmalloc-2048缓存。对于这个特定的缓存，SLUB分配器（这个分配器是Ubuntu所使用的slab分配器）会使用大小为0x8000的slabs。因此每当分配器用光kmalloc-2048缓存的slab时，它就会使用页面分配器分配0x8000字节的空间。

了解这些知识后，我们就可以将一个kmalloc-2048的slab和一个环形缓冲区内存块分配在一起，使用如下步骤：

1、分配许多大小为2048的对象（对我来说512个就可以），填充当前kmalloc-2048缓存中存在的slabs。我们可以创建一堆数据包套接字来分配packet_sock对象，最终达到这个目的。

2、分配许多大小为0x8000的页面内存块（对我来说1024个就可以），挤掉页面分配器的freelists，使得某些高位页面内存块被拆分。我们可以创建另一个数据包套接字，将具有1024个大小为0x8000的内存块的环形缓冲区附加在其后，最终达到这个目的。

3、创建一个数据包套接字，并附加一个内存块大小为0x8000的环形缓冲区。最后一个内存块（我总共使用了2个内存块，原因在下面解释）就是我们需要溢出的那个内存块。

4、创建一堆数据包套接字来分配packet_sock结构体对象，最终导致至少有一个新的slab被分配。

这样我们就可以对堆进行精确操作，如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01603ddd49d5af2c30.png)

为了排挤freelists、按照上述方法精确操作堆，我们需要分配的具体数量会根据设置的不同以及内存使用情况的不同而有所不同。对于一个大部分时间处于空闲状态的Ubuntu主机来说，使用我上面提到的个数就以足够。

**6.2 控制覆盖操作**

上面我提到过，这个bug会导致某个环形缓冲区内存块的越界写入，我们可以控制越界的偏移量，也可以控制写入数据的最大值。事实证明，我们不仅能够控制最大值和偏移量，我们实际上也能控制正在写入的精确数据（及其大小）。由于当前正在存放到环形缓冲区中的数据为正在通过特定网络接口的数据包，我们可以通过回环接口，使用原始套接字手动发送具有任意内容的数据包。如果我们在一个隔离的网络命名空间中执行这个操作，我们就不会受到外部网络流量干扰。

此外我们还需要注意其他一些事项。

首先，数据包的大小至少必须为14字节（两个mac地址占了12字节，而EtherType占了2个字节），以便传递到数据包套接字层。这意味着我们必须覆盖至少14字节的数据，而数据包本身的内容可以取任意值。

其次，出于对齐目的，nxt_offset的最低3个比特必须取值为2。这意味着我们不能在8字节对齐的偏移处开始执行覆盖操作。

再者，当数据包被接收然后保存到内存块中时，内核会更新内存块和帧头中的某些字段。如果我们将nxt_offset指向我们希望覆盖的某些特定偏移处，那么内存块和帧头结束部位的某些数据很有可能会被破坏。

另一个问题就是，如果我们将nxt_offset指向内存块的尾部，那么当第一个数据包正在接收时，第一个内存块会马上被关闭，这是因为内核会认为第一个内存块中没有任何空余的空间（这是正确的处理流程，可以参考__packet_lookup_frame_in_block()函数中的代码片段）。这不是一个真正的问题，因为我们可以创建一个具备2个内存块的环形缓冲区。在第一个内存块被关闭时，我们可以覆盖第二个内存块。

**6.3 执行代码**

现在，我们需要弄清楚我们需要覆盖哪个函数指针。在packet_sock结构体中，有一些函数指针字段，我最终使用了如下两个字段：

1、packet_sock-&gt;xmit；

2、packet_sock-&gt;rx_ring-&gt;prb_bdqc-&gt;retire_blk_timer-&gt;func

每当用户尝试使用数据包套接字发送数据包时，就会调用第一个函数。提升到root权限的通常方法是在某个进程上下文中执行commit_creds(prepare_kernel_cred(0))载荷。对于第一个函数，进程上下文中会调用xmit指针，这意味着我们可以简单地将其指向一个包含载荷的可执行内存区域就能达到目的。

因此，我使用的是retire_blk_timer字段（Philip Pettersson在他发现的CVE-2016-8655漏洞中也利用了这个字段）。这个字段包含一个函数指针，每当计时器超时时就会触发这个指针。在正常的数据包套接字操作过程中，retire_blk_timer-&gt;func指向的是prb_retire_rx_blk_timer_expired()，调用这个函数时会使用retire_blk_timer-&gt;data作为参数，这个参数中包含了packet_sock结构体对象的地址。由于我们可以一起覆盖函数字段和数据字段，因此我们可以获得一个非常完美的func(data)覆盖结果。

当前CPU核心的SMEP和SMAP状态由CR4寄存器的第20和21个比特位所控制。为了禁用这两个机制，我们应该将这两个比特位清零。为了做到这一点，我们可以使用前面获得的func(data)结果调用native_write_cr4(X)函数，其中X的第20和21个比特位设置为0。具体的X值可能取决于还有哪些CPU功能被启用。在我测试漏洞利用的那台机器上，CR4寄存器的值为0x10407f0（因为CPU不支持SMAP功能，因此只有SMEP比特被启用），因此我使用的X值为0x407f0。我们可以使用sched_setaffinity系统调用，强迫漏洞利用程序在某个CPU核心上运行，由于这个我们禁用了这个核心的SMAP和SMEP功能，这样一来就能确保用户空间载荷会在同一个核心上执行。

综合这些背景知识，我给出了如下的漏洞利用步骤：

1、找到内核文本地址，以绕过KASLR（具体方法参考下文描述）。

2、根据上文描述，操纵内核堆。

3、禁用SMEP和SMAP：

a) 在某个环形缓冲区内存块之后分配一个packet_sock对象；

b) 将一个接收环形缓冲区附加到packet_sock对象之后，以设置一个内存块停用计时器；

c) 溢出这个内存块，覆盖retire_blk_timer字段。使得retire_blk_timer-&gt;func指向native_write_cr4，并且使得retire_blk_timer-&gt;data的值与所需的CR4寄存器值相等；

d) 等待计时器执行，现在我们就可以在当前的CPU核心上禁用SMEP和SMAP了。

4、获取root权限。

a) 分配另一对packet_sock对象和环形缓冲区内存块。

b) 溢出这个内存块，覆盖xmit字段。使得xmit指向用户空间中分配的一个commit_creds(prepare_kernel_cred(0))函数。

c) 在对应的数据包套接字上发送一个数据包，xmit就会被触发，然后当前的进程就会获得root权限。

相应的漏洞利用代码可以在这个链接中找到。

需要注意的是，当我们覆盖packet_sock结构体中的这两个字段时，我们最终会破坏在这两个字段之前的某些字段（因为内核会将某些值写入内存块和帧头中），这可能会导致内核崩溃。然而，如果其他这些字段没有被内核使用，那么一切都还好。我发现当我们在漏洞利用结束后，尝试关闭所有的数据包套接字时，mclist这个字段会导致内核崩溃，但我们只要将其清零即可。

[![](https://p5.ssl.qhimg.com/t01bf1b9618c4568065.png)](https://p5.ssl.qhimg.com/t01bf1b9618c4568065.png)

**6.4 绕过KASLR**

在这里我会介绍某些精心构造的技术，来绕过KASLR机制。由于Ubuntu默认情况下不会限制dmesg，我们可以使用grep命令，查找内核syslog日志中的“Freeing SMP“关键词，我们可以在结果中找到一个内核指针，看起来与内核文本地址非常相似，如下所示：



```
# Boot #1
$ dmesg | grep 'Freeing SMP'
[    0.012520] Freeing SMP alternatives memory: 32K (ffffffffa58ee000 - ffffffffa58f6000)
$ sudo cat /proc/kallsyms | grep 'T _text'
ffffffffa4800000 T _text
# Boot #2
$ dmesg | grep 'Freeing SMP'
[    0.017487] Freeing SMP alternatives memory: 32K (ffffffff85aee000 - ffffffff85af6000)
$ sudo cat /proc/kallsyms | grep 'T _text'
ffffffff84a00000 T _text
```

在dmesg中暴露的地址的基础上，通过简单的数学运算，我们可以计算出内核文本地址。使用这种方式计算出来的内核文本地址只有在启动之后的一段时间内有效，因为syslog只存储固定行数的这类日志，然后在某些时候抹掉这些日志。

我们可以使用几个Linux内核加固功能来避免这类信息泄露。第一个功能是dmesg_restrict，它可以限制非特权用户读取内核syslog日志。需要注意的是，即使在受限dmesg下，Ubuntu的第一个用户还是可以从“/var/log/kern.log”以及“/var/log/syslog”处读取syslog日志，因为该用户隶属于adm用户组。

另一个功能是[**kptr_restrict**](http://bits-please.blogspot.de/2015/08/effectively-bypassing-kptrrestrict-on.html)，这个功能不允许非特权用户查阅内核使用“%pK”格式说明符打印的指针。然而，在4.8版内核中，free_reserved_area()函数使用的是[**“%p”格式符**](http://lxr.free-electrons.com/source/mm/page_alloc.c?v=4.8#L6433)，因此这种情况下kptr_restrict不会发挥作用。4.10版内核中[**修复**](https://github.com/torvalds/linux/commit/adb1fe9ae2ee6ef6bc10f3d5a588020e7664dfa7)了free_reserved_area()函数，这个函数根本就不会打印地址范围，但这个修改没有做到向前兼容。

<br>

**七、修复措施**

我们来看看补丁原理。修复前的漏洞代码如下所示。请记住，用户可以完全控制tp_block_size和tp_sizeof_priv字段：



```
4207                 if (po-&gt;tp_version &gt;= TPACKET_V3 &amp;&amp;
4208                     (int)(req-&gt;tp_block_size -
4209                           BLK_PLUS_PRIV(req_u-&gt;req3.tp_sizeof_priv)) &lt;= 0)
4210                         goto out;
```

在考虑如何修复这个漏洞时，我们想到的第一个思路就是，我们可以比较这两个值，避免这些值被转化为非预期的整数（int）：



```
4207                 if (po-&gt;tp_version &gt;= TPACKET_V3 &amp;&amp;
4208                     req-&gt;tp_block_size &lt;=
4209                           BLK_PLUS_PRIV(req_u-&gt;req3.tp_sizeof_priv))
4210                         goto out;
```

有趣的是，这个修复措施并不会奏效。原因在于当tp_sizeof_priv接近于unsigned int的最大值时，在处理[**BLK_PLUS_PRIV**](http://lxr.free-electrons.com/source/net/packet/af_packet.c?v=4.8#L177)时还是会出现溢出问题。



```
177 #define BLK_PLUS_PRIV(sz_of_priv) 
178         (BLK_HDR_LEN + ALIGN((sz_of_priv), V3_ALIGNMENT))
```

修改这个溢出问题的一种办法就是在将tp_sizeof_priv传递给BLK_PLUS_PRIV之前，将其转化为uint64类型值。这就是我在上游代码中做的修复措施：



```
4207                 if (po-&gt;tp_version &gt;= TPACKET_V3 &amp;&amp;
4208                     req-&gt;tp_block_size &lt;=
4209                           BLK_PLUS_PRIV((u64)req_u-&gt;req3.tp_sizeof_priv))
4210                         goto out;
```



**八、缓解措施**

我们需要CAP_NET_RAW权限才能创建数据包套接字，非特权用户可以在用户命名空间中获取这个权限。非特权用户命名空间暴露了许多内核攻击面，这最终导致了许多可利用的漏洞（如[**CVE-2017-7184**](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-7184)、[**CVE-2016-8655**](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-8655)等）。我们可以通过完全禁用用户命名空间或者禁止非特权用户使用这类空间来缓解这类内核漏洞。

要彻底禁用用户命名空间，你可以在禁用CONFIG_USER_NS的条件下，重新编译自己的内核。在基于Debian的内核中，我们可以将/proc/sys/kernel/unprivileged_userns_clone的值设为0，以限制只有特权用户才能使用用户命名空间。从4.9版内核起，上游内核中就具有类似的“/proc/sys/user/max_user_namespaces”设置。

<br>

**九、总结**

就目前而言，（从安全角度来看）Linux内核中存在大量没有经过完善测试的接口，其中很多接口在诸如Ubuntu等流行的Linux发行版中处于启用状态，并且向非特权用户开放。这种现象显然是不好的，我们需要好好测试或者进一步限制这些接口。

Syzkaller是个令人惊奇的工具，允许我们对内核接口进行模糊测试。我们甚至可以为其他系统调用添加准系统（barebone）描述信息，这样通常也能发现许多bug。由于内核中还有许多地方没有覆盖到（可能会有一大堆安全漏洞存在于内核中），我们因此也需要大家一起协作，编写系统调用描述信息，对已有的问题进行修复。我们非常乐意看到读者通过发起代码的pull请求，贡献自己的一份力。

<br>

**十、参考链接**

相应的参考链接为：

利用代码：

[https://github.com/xairy/kernel-exploits/tree/master/CVE-2017-7308](https://github.com/xairy/kernel-exploits/tree/master/CVE-2017-7308) 

修复代码：

[https://github.com/torvalds/linux/commit/2b6867c2ce76c596676bec7d2d525af525fdc6e2](https://github.com/torvalds/linux/commit/2b6867c2ce76c596676bec7d2d525af525fdc6e2) 

CVE编号：

[https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-7308](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-7308) 

我们用来查找Linux内核错误的工具为：

syzkaller：[https://github.com/google/syzkaller](https://github.com/google/syzkaller) 

KASAN：[https://www.kernel.org/doc/html/latest/dev-tools/kasan.html](https://www.kernel.org/doc/html/latest/dev-tools/kasan.html) 

KTSAN：[https://github.com/google/ktsan/wiki](https://github.com/google/ktsan/wiki) 

KMSAN：https://github.com/google/kmsan

已整理的Linux内核漏洞利用资料： 

[https://github.com/xairy/linux-kernel-exploitation](https://github.com/xairy/linux-kernel-exploitation) 
