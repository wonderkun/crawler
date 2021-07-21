> 原文链接: https://www.anquanke.com//post/id/86396 


# 【技术分享】利用一个堆溢出漏洞实现VMware虚拟机逃逸


                                阅读量   
                                **132599**
                            
                        |
                        
                                                                                    



**[![](https://p5.ssl.qhimg.com/t013f784f6f77863a74.png)](https://p5.ssl.qhimg.com/t013f784f6f77863a74.png)**



作者：李小龙（acez）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**1. 介绍**



2017年3月，长亭安全研究实验室（[Chaitin](http://link.zhihu.com/?target=https%3A//chaitin.cn/) Security Research Lab）参加了Pwn2Own黑客大赛，我作为团队的一员，一直专注于VMware Workstation Pro的破解，并成功在赛前完成了一个虚拟机逃逸的漏洞利用。（很不）幸运的是，就在Pwn2Own比赛的前一天（3月14日），VMware发布了一个新的版本，其中修复了我们所利用的漏洞。在本文中，我会介绍我们从发现漏洞到完成利用的整个过程。感谢[@kelwin](http://link.zhihu.com/?target=http%3A//weibo.com/kelwinyang)在实现漏洞利用过程中给予的帮助，也感谢ZDI的朋友，他们近期也发布了一篇相关[博客](http://link.zhihu.com/?target=https%3A//www.zerodayinitiative.com/blog/2017/6/26/use-after-silence-exploiting-a-quietly-patched-uaf-in-vmware)，正是这篇博文促使我们完成本篇writeup。

本文主要由三部分组成：首先我们会简要介绍VMware中的RPCI机制，其次我们会描述本文使用的漏洞，最后讲解我们是如何利用这一个漏洞来绕过ASLR并实现代码执行的。

<br>

**2. VMware RPCI机制**



VMware实现了多种虚拟机（下文称为guest）与宿主机（下文称文host）之间的通信方式。其中一种方式是通过一个叫做Backdoor的接口，这种方式的设计很有趣，guest只需在用户态就可以通过该接口发送命令。VMware Tools也部分使用了这种接口来和host通信。我们来看部分相关代码（摘自[open-vm-tools](http://link.zhihu.com/?target=https%3A//github.com/vmware/open-vm-tools)中的lib/backdoor/backdoorGcc64.c）：

```
void  Backdoor_InOut(Backdoor_proto *myBp) // IN/OUT  `{`
   uint64 dummy;
   __asm__ __volatile__(#ifdef __APPLE__
        /*         * Save %rbx on the stack because the Mac OS GCC doesn't want us to         * clobber it - it erroneously thinks %rbx is the PIC register.         * (Radar bug 7304232)         */
        "pushq %%rbx"           "nt"#endif
        "pushq %%rax"           "nt"
        "movq 40(%%rax), %%rdi" "nt"
        "movq 32(%%rax), %%rsi" "nt"
        "movq 24(%%rax), %%rdx" "nt"
        "movq 16(%%rax), %%rcx" "nt"
        "movq  8(%%rax), %%rbx" "nt"
        "movq   (%%rax), %%rax" "nt"
        "inl %%dx, %%eax"       "nt"  /* NB: There is no inq instruction */
        "xchgq %%rax, (%%rsp)"  "nt"
        "movq %%rdi, 40(%%rax)" "nt"
        "movq %%rsi, 32(%%rax)" "nt"
        "movq %%rdx, 24(%%rax)" "nt"
        "movq %%rcx, 16(%%rax)" "nt"
        "movq %%rbx,  8(%%rax)" "nt"
        "popq          (%%rax)" "nt"#ifdef __APPLE__
        "popq %%rbx"            "nt"#endif
      : "=a" (dummy)
      : "0" (myBp)
      /*       * vmware can modify the whole VM state without the compiler knowing       * it. So far it does not modify EFLAGS. --hpreg       */
      :#ifndef __APPLE__
      /* %rbx is unchanged at the end of the function on Mac OS. */
      "rbx",#endif
      "rcx", "rdx", "rsi", "rdi", "memory"
   );`}`
```

上面的代码中出现了一个很奇怪的指令inl。在通常环境下（例如Linux下默认的I/O权限设置），用户态程序是无法执行I/O指令的，因为这条指令只会让用户态程序出错并产生崩溃。而此处这条指令产生的权限错误会被host上的hypervisor捕捉，从而实现通信。Backdoor所引入的这种从guest上的用户态程序直接和host通信的能力，带来了一个有趣的攻击面，这个攻击面正好满足Pwn2Own的要求：“在这个类型（指虚拟机逃逸这一类挑战）中，攻击必须从guest的非管理员帐号发起，并实现在host操作系统中执行任意代码”。guest将0x564D5868存入$eax，I/O端口号0x5658或0x5659存储在$dx中，分别对应低带宽和高带宽通信。其它寄存器被用于传递参数，例如$ecx的低16位被用来存储命令号。对于RPCI通信，命令号会被设为BDOOR_CMD_MESSAGE（=30）。文件lib/include/backdoor_def.h中包含了一些支持的backdoor命令列表。host捕捉到错误后，会读取命令号并分发至相应的处理函数。此处我省略了很多细节，如果你有兴趣可以阅读相关源码。

2.1 RPCI

远程过程调用接口RPCI（Remote Procedure Call Interface）是基于前面提到的Backdoor机制实现的。依赖这个机制，guest能够向host发送请求来完成某些操作，例如，拖放（Drag n Drop）/复制粘贴（Copy Paste）操作、发送或获取信息等等。RPCI请求的格式非常简单：&lt;命令&gt; &lt;参数&gt;。例如RPCI请求info-get guestinfo.ip可以用来获取guest的IP地址。对于每个RPCI命令，在vmware-vmx进程中都有相关注册和处理操作。

需要注意的是有些RPCI命令是基于VMCI套接字实现的，但此内容已超出本文讨论的范畴。

<br>

**3. 漏洞**



花了一些时间逆向各种不同的RPCI处理函数之后，我决定专注于分析拖放（Drag n Drop，下面简称为DnD）和复制粘贴（Copy Paste，下面简称为CP）功能。这部分可能是最复杂的RPCI命令，也是最可能找到漏洞的地方。在深入理解的DnD/CP内部工作机理后，可以很容易发现，在没有用户交互的情况下，这些处理函数中的许多功能是无法调用的。DnD/CP的核心功能维护了一个状态机，在无用户交互（例如拖动鼠标从host到guest中）情况下，许多状态是无法达到的。

我决定看一看Pwnfest 2016上被利用的漏洞，该漏洞在[这个](http://link.zhihu.com/?target=https%3A//www.vmware.com/security/advisories/VMSA-2016-0019.html)VMware安全公告中有所提及。此时我的idb已经标上了很多符号，所以很容易就通过bindiff找到了补丁的位置。下面的代码是修补之前存在漏洞的函数（可以看出services/plugins/dndcp/dnddndCPMsgV4.c中有对应源码，漏洞依然存在于[open-vm-tools](http://link.zhihu.com/?target=https%3A//github.com/vmware/open-vm-tools)的git仓库的master分支当中）：

```
static Bool  DnDCPMsgV4IsPacketValid(const uint8 *packet,  
                        size_t packetSize)`{`
   DnDCPMsgHdrV4 *msgHdr = NULL;
   ASSERT(packet);
   if (packetSize &lt; DND_CP_MSG_HEADERSIZE_V4) `{`
      return FALSE;
   `}`
   msgHdr = (DnDCPMsgHdrV4 *)packet;
   /* Payload size is not valid. */
   if (msgHdr-&gt;payloadSize &gt; DND_CP_PACKET_MAX_PAYLOAD_SIZE_V4) `{`
      return FALSE;
   `}`
   /* Binary size is not valid. */
   if (msgHdr-&gt;binarySize &gt; DND_CP_MSG_MAX_BINARY_SIZE_V4) `{`
      return FALSE;
   `}`
   /* Payload size is more than binary size. */
   if (msgHdr-&gt;payloadOffset + msgHdr-&gt;payloadSize &gt; msgHdr-&gt;binarySize) `{` // [1]
      return FALSE;
   `}`
   return TRUE;`}`Bool  DnDCPMsgV4_UnserializeMultiple(DnDCPMsgV4 *msg,  
                               const uint8 *packet,
                               size_t packetSize)`{`
   DnDCPMsgHdrV4 *msgHdr = NULL;
   ASSERT(msg);
   ASSERT(packet);
   if (!DnDCPMsgV4IsPacketValid(packet, packetSize)) `{`
      return FALSE;
   `}`
   msgHdr = (DnDCPMsgHdrV4 *)packet;
   /*    * For each session, there is at most 1 big message. If the received    * sessionId is different with buffered one, the received packet is for    * another another new message. Destroy old buffered message.    */
   if (msg-&gt;binary &amp;&amp;
       msg-&gt;hdr.sessionId != msgHdr-&gt;sessionId) `{`
      DnDCPMsgV4_Destroy(msg);
   `}`
   /* Offset should be 0 for new message. */
   if (NULL == msg-&gt;binary &amp;&amp; msgHdr-&gt;payloadOffset != 0) `{`
      return FALSE;
   `}`
   /* For existing buffered message, the payload offset should match. */
   if (msg-&gt;binary &amp;&amp;
       msg-&gt;hdr.sessionId == msgHdr-&gt;sessionId &amp;&amp;
       msg-&gt;hdr.payloadOffset != msgHdr-&gt;payloadOffset) `{`
      return FALSE;
   `}`
   if (NULL == msg-&gt;binary) `{`
      memcpy(msg, msgHdr, DND_CP_MSG_HEADERSIZE_V4);
      msg-&gt;binary = Util_SafeMalloc(msg-&gt;hdr.binarySize);
   `}`
   /* msg-&gt;hdr.payloadOffset is used as received binary size. */
   memcpy(msg-&gt;binary + msg-&gt;hdr.payloadOffset,
          packet + DND_CP_MSG_HEADERSIZE_V4,
          msgHdr-&gt;payloadSize); // [2]
   msg-&gt;hdr.payloadOffset += msgHdr-&gt;payloadSize;
   return TRUE;`}`
```

对于Version 4的DnD/CP功能，当guest发送分片DnD/CP命令数据包时，host会调用上面的函数来重组guest发送的DnD/CP消息。接收的第一个包必须满足payloadOffset为0，binarySize代表堆上分配的buffer长度。[1]处的检查比较了包头中的binarySize，用来确保payloadOffset和payloadSize不会越界。在[2]处，数据会被拷入分配的buffer中。但是[1]处的检查存在问题，它只对接收的第一个包有效，对于后续的数据包，这个检查是无效的，因为代码预期包头中的binarySize和分片流中的第一个包相同，但实际上你可以在后续的包中指定更大的binarySize来满足检查，并触发堆溢出。

所以，该漏洞可以通过发送下面的两个分片来触发：

```
packet 1`{`  
 ...
 binarySize = 0x100
 payloadOffset = 0
 payloadSize = 0x50
 sessionId = 0x41414141
 ...
 #...0x50 bytes...#`}`packet 2`{`  
 ...
 binarySize = 0x1000
 payloadOffset = 0x50
 payloadSize = 0x100
 sessionId = 0x41414141
 ...
 #...0x100 bytes...#`}`
```

有了以上的知识，我决定看看Version 3中的DnD/CP功能中是不是也存在类似的问题。令人惊讶的是，几乎相同的漏洞存在于Version 3的代码中（这个漏洞最初通过逆向分析来发现，但是我们后来意识到v3的代码也在open-vm-tools的git仓库中）：

```
Bool  DnD_TransportBufAppendPacket(DnDTransportBuffer *buf,          // IN/OUT  
                             DnDTransportPacketHeader *packet, // IN
                             size_t packetSize)                // IN`{`
   ASSERT(buf);
   ASSERT(packetSize == (packet-&gt;payloadSize + DND_TRANSPORT_PACKET_HEADER_SIZE) &amp;&amp;
          packetSize &lt;= DND_MAX_TRANSPORT_PACKET_SIZE &amp;&amp;
          (packet-&gt;payloadSize + packet-&gt;offset) &lt;= packet-&gt;totalSize &amp;&amp;
          packet-&gt;totalSize &lt;= DNDMSG_MAX_ARGSZ);
   if (packetSize != (packet-&gt;payloadSize + DND_TRANSPORT_PACKET_HEADER_SIZE) ||
       packetSize &gt; DND_MAX_TRANSPORT_PACKET_SIZE ||
       (packet-&gt;payloadSize + packet-&gt;offset) &gt; packet-&gt;totalSize || //[1]
       packet-&gt;totalSize &gt; DNDMSG_MAX_ARGSZ) `{`
      goto error;
   `}`
   /*    * If seqNum does not match, it means either this is the first packet, or there    * is a timeout in another side. Reset the buffer in all cases.    */
   if (buf-&gt;seqNum != packet-&gt;seqNum) `{`
      DnD_TransportBufReset(buf);
   `}`
   if (!buf-&gt;buffer) `{`
      ASSERT(!packet-&gt;offset);
      if (packet-&gt;offset) `{`
         goto error;
      `}`
      buf-&gt;buffer = Util_SafeMalloc(packet-&gt;totalSize);
      buf-&gt;totalSize = packet-&gt;totalSize;
      buf-&gt;seqNum = packet-&gt;seqNum;
      buf-&gt;offset = 0;
   `}`
   if (buf-&gt;offset != packet-&gt;offset) `{`
      goto error;
   `}`
   memcpy(buf-&gt;buffer + buf-&gt;offset,
          packet-&gt;payload,
          packet-&gt;payloadSize);
   buf-&gt;offset += packet-&gt;payloadSize;
   return TRUE;error:  
   DnD_TransportBufReset(buf);
   return FALSE;`}`
```

Version 3的DnD/CP在分片重组时，上面的函数会被调用。此处我们可以在[1]处看到与之前相同的情形，代码依然假设后续分片中的totalSize会和第一个分片一致。因此这个漏洞可以用和之前相同的方法触发：

```
packet 1`{`  
 ...
 totalSize = 0x100
 payloadOffset = 0
 payloadSize = 0x50
 seqNum = 0x41414141
 ...
 #...0x50 bytes...#`}`packet 2`{`  
 ...
 totalSize = 0x1000
 payloadOffset = 0x50
 payloadSize = 0x100
 seqNum = 0x41414141
 ...
 #...0x100 bytes...#`}`
```

在Pwn2Own这样的比赛中，这个漏洞是很弱的，因为它只是受到之前漏洞的启发，而且甚至可以说是同一个。因此，这样的漏洞在赛前被修补并不惊讶（好吧，也许我们并不希望这个漏洞在比赛前一天被修复）。对应的VMware安全公告在[这里](http://link.zhihu.com/?target=https%3A//www.vmware.com/security/advisories/VMSA-2017-0005.html)。受到这个漏洞影响的VMWare Workstation Pro最新版本是12.5.3。

接下来，让我们看一看这个漏洞是如何被用来完成从guest到host的逃逸的！

<br>

**4. 漏洞利用**



为了实现代码执行，我们需要在堆上覆盖一个函数指针，或者破坏C++对象的虚表指针。

首先让我们看一看如何将DnD/CP协议的设置为version 3，依次发送下列RPCI命令即可：

```
tools.capability.dnd_version 3  
tools.capability.copypaste_version 3  
vmx.capability.dnd_version  
vmx.capability.copypaste_version
```

前两行消息分别设置了DnD和Copy/Paste的版本，后续两行用来查询版本，这是必须的，因为只有查询版本才会真正触发版本切换。RPCI命令vmx.capability.dnd_version会检查DnD/CP协议的版本是否已被修改，如果是，就会创建一个对应版本的C++对象。对于version 3，2个大小为0xA8的C++对象会被创建，一个用于DnD命令，另一个用于Copy/Paste命令。

这个漏洞不仅可以让我们控制分配的大小和溢出的大小，而且能够让我们进行多次越界写。理想的话，我们可以用它分配大小为0xA8的内存块，并让它分配在C++对象之前，然后利用堆溢出改写C++对象的vtable指针，使其指向可控内存，从而实现代码执行。

这并非易事，在此之前我们必须解决一些其他问题。首先我们需要找到一个方法来绕过ASLR，同时处理好Windows Low Fragmented Heap。

4.1 绕过ASLR

一般来说，我们需要找到一个对象，通过溢出来影响它，然后实现信息泄露。例如破坏一个带有长度或者数据指针的对象，并且可以从guest读取，然而我们没有找到这种对象。于是我们逆向了更多的RPCI命令处理函数，来寻找可用的东西。那些成对的命令特别引人关注，例如你能用一个命令来设置一些数据，同时又能用相关命令来取回数据，最终我们找到的是一对命令info-set和info-get：

```
info-set guestinfo.KEY VALUE  
info-get guestinfo.KEY
```

VALUE是一个字符串，字符串的长度可以控制堆上buffer的分配长度，而且我们可以分配任意多的字符串。但是如何用这些字符串来泄露数据呢？我们可以通过溢出来覆盖结尾的null字节，让字符串连接上相邻的内存块。如果我们能够在发生溢出的内存块和DnD或CP对象之间分配一个字符串，那么我们就能泄露对象的vtable地址，从而我们就可以知道vmware-vmx的地址。尽管Windows的LFH堆分配存在随机化，但我们能够分配任意多的字符串，因此可以增加实现上述堆布局的可能性，但是我们仍然无法控制溢出buffer后面分配的是DnD还是CP对象。经过我们的测试，通过调整一些参数，例如分配和释放不同数量的字符串，我们可以实现60%到80%的成功率。

下图总结了我们构建的堆布局情况（Ov代表溢出内存块，S代表String，T代表目标对象）。

[![](https://p3.ssl.qhimg.com/t01730ffcb03bb4bcfb.png)](https://p3.ssl.qhimg.com/t01730ffcb03bb4bcfb.png)

我们的策略是：首先分配一些填满“A”的字符串，然后通过溢出写入一些“B”，接下来读取所有分配的字符串，其中含有“B”的就是被溢出的字符串。这样我们就找到了一个字符串可以被用来读取泄露的数据，然后以bucket的内存块大小0xA8的粒度继续溢出，每次溢出后都检查泄露的数据。由于DnD和CP对象的vtable距离vmware-vmx基地址的偏移是固定的，每次溢出后只需要检查最低一些数据位，就能够判断溢出是否到达了目标对象。

4.2 获取代码执行

现在我们实现了信息泄露，也能知道溢出的是哪个C++对象，接下来要实现代码执行。我们需要处理两种情形：溢出CopyPaste和DnD。需要指出的是能利用的代码路径有很多，我们只是选择了其中一个。

4.2.1 覆盖CopyPaste对象

对于CopyPaste对象，我们可以覆盖虚表指针，让它指向我们可控的其他数据。我们需要找到一个指针，指针指向的数据是可控并被用做对象的虚表。为此我们使用了另一个RPCI命令unity.window.contents.start。这个命令主要用于Unity模式下，在host上绘制一些图像。这个操作可以让我们往相对vmware-vmx偏移已知的位置写入一些数据。该命令接收的参数是图像的宽度和高度，二者都是32位，合并起来我们就在已知位置获得了一个64位的数据。我们用它来作为虚表中的一个指针，通过发送一个CopyPast命令即可触发该虚函数调用，步骤如下：

1. 发送unity.window.contents.start命令，通过指定参数宽度和高度，往全局变量处写入一个64位的栈迁移gadget地址

2. 覆盖对象虚表指针，指向伪造的虚表（调整虚表地址偏移）

3. 发送CopyPaste命令，触发虚函数调用

4. ROP

4.2.2 覆盖DnD对象

对于DnD对象，我们不能只覆盖vtable指针，因为在发生溢出之后vtable会立马被访问，另一个虚函数会被调用，而目前我们只能通过unity图像的宽度和高度控制一个qword，所以无法控制更大的虚表。

让我们看一看DnD和CP对象的结构，总结如下（一些类似的结构可以在open-vm-tools中找到，但是在vmware-vmx中会略有区别）：

```
DnD_CopyPaste_RpcV3`{`  
    void * vtable;
    ...
    uint64_t ifacetype;
    RpcUtil`{`
        void * vtable;
        RpcBase * mRpc;
        DnDTransportBuffer`{`
            uint64_t seqNum;
            uint8_t * buffer;
            uint64_t totalSize;
            uint64_t offset;
            ...
        `}`
        ...
    `}``}`RpcBase`{`  
    void * vtable;
    ...`}`
```

我们在此省略了结构中很多与本文无关的属性。对象中有个指针指向另一个C++对象RpcBase，如果我们能用一个可控数据的指针的指针覆盖mRpc这个域，那我们就控制了RpcBase的vtable。对此我们可以继续使用unity.window.contents.start命令来来控制mRpc，该命令的另一个参数是imgsize，这个参数代表分配的图像buffer的大小。这个buffer分配出来后，它的地址会存在vmware-vmx的固定偏移处。我们可以使用命令unity.window.contents.chunk来填充buffer的内容。步骤如下：

1. 发送unity.window.contents.start命令来分配一个buffer，后续我们用它来存储一个伪造的vtable。

2. 发送unity.window.contents.chunk命令来填充伪造的vtable，其中填入一个栈迁移的gadget

3. 通过溢出覆盖DnD对象的mRpc域，让它指向存储buffer地址的地方（某全局变量处），即写入一个指针的指针

4. 通过发送DnD命令来触发mRpc域的虚函数调用

5. ROP

P.S：vmware-vmx进程中有一个可读可写可执行的内存页（至少在版本12.5.3中存在）。

4.3 稳定性讨论

正如前面提及的，因为Windows LFH堆的随机化，当前的exploit无法做到100%成功率。不过可以尝试下列方法来提高成功率：

观察0xA8大小的内存分配，考虑是否可以通过一些malloc和free的调用来实现确定性的LFH分配，参考[这里](http://link.zhihu.com/?target=http%3A//illmatics.com/Understanding_the_LFH.pdf)和[这里](http://link.zhihu.com/?target=https%3A//www.blackhat.com/docs/us-16/materials/us-16-Yason-Windows-10-Segment-Heap-Internals-wp.pdf)。

寻找堆上的其他C++对象，尤其是那些可以在堆上喷射的

寻找堆上其他带有函数指针的对象，尤其是那些可以在堆上喷射的

找到一个独立的信息泄漏漏洞

打开更多脑洞

4.4 演示效果

[![](https://p2.ssl.qhimg.com/t0197c7a0196d0abf6b.png)](https://p2.ssl.qhimg.com/t0197c7a0196d0abf6b.png)

演示视频：





**5. 感想与总结**



“No pwn no fun”，如果你想参加Pwn2Own这样的比赛，你就需要准备多个漏洞，或者找到高质量的漏洞。

<br>

**6. 我是广告**



对安全研究、安全研发感兴趣的朋友欢迎投简历到hr@chaitin.com。


