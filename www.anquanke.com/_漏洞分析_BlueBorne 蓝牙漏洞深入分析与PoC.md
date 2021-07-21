> 原文链接: https://www.anquanke.com//post/id/86949 


# 【漏洞分析】BlueBorne 蓝牙漏洞深入分析与PoC


                                阅读量   
                                **340936**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t013393c12943c04d2f.jpg)](https://p0.ssl.qhimg.com/t013393c12943c04d2f.jpg)

**作者：huahuaisadog @ 360VulpeckerTeam**

<br>

**0x00**

****

前些天，armis爆出了一系列蓝牙的漏洞，**无接触无感知接管系统**的能力有点可怕，而且基本上影响所有的蓝牙设备，危害不可估量，可以看这里（[https://www.armis.com/blueborne/](https://www.armis.com/blueborne/)  ）来了解一下它的逆天能力：只要手机开启了蓝牙，就可能被远程控制。现在手机这么多，利用这个漏洞写出蠕虫化的工具，那么可能又是一个手机版的低配wannacry了。我们360Vulpecker Team在了解到这些相关信息后，快速进行了跟进分析。 armis给出了他们的whitepaper，对蓝牙架构和这几个漏洞的分析可以说非常详尽了，先膜一发。不过他们没有给出这些漏洞的PoC或者是exp，只给了一个针对Android的“BlueBorne检测app"，但是逆向这个发现**仅仅是检测了系统的补丁日期**。于是我来拾一波牙慧，把这几个漏洞再分析一下，然后把poc编写出来： 

* CVE-2017-1000250 Linux bluetoothd进程信息泄露 

* CVE-2017-1000251 Linux 内核栈溢出 

* CVE-2017-0785 Android com.android.bluetooth进程信息泄露 

* CVE-2017-0781 Android com.android.bluetooth进程堆溢出 

* CVE-2017-0782 Android com.android.bluetooth进程堆溢出

**以上PoC代码均在**

**[https://github.com/marsyy/littl_tools/tree/master/bluetooth](https://github.com/marsyy/littl_tools/tree/master/bluetooth) **

由于也是因为这几个漏洞才从零开始搞蓝牙，所以应该有些分析不到位的地方，还请各路大牛斧正。

<br>

**0x01 蓝牙架构及代码分布**

****

这里首先应该祭出armis的paper里的图： 

[![](https://p4.ssl.qhimg.com/t01fa596689092bd57a.png)](https://p4.ssl.qhimg.com/t01fa596689092bd57a.png)

图上把蓝牙的各个层次关系描述得很详尽，不过我们这里暂时只需要关心这么几层：**HCI，L2CAP，BNEP，SDP**。BNEP和SDP是比较上层的服务，HCI在最底层，直接和蓝牙设备打交道。而承载在蓝牙服务和底层设备之间的桥梁，也就是L2CAP层了。每一层都有它协议规定的数据组织结构，所有层的数据包组合在一起，就是一个完整的蓝牙包（一个SDP包为例）： 

[![](https://p3.ssl.qhimg.com/t01e98008068e7ff50b.png)](https://p3.ssl.qhimg.com/t01e98008068e7ff50b.png)

虽然协议规定的架构是图上说的那样，但是具体实现是有不同的，Linux用的**BlueZ**，而现在的Android用的**BlueDroid**，也就针对这两种架构说一说代码的具体分布。

**BlueZ**

在Linux里，用的是BlueZ架构，由**bluetoothd**来提供BNEP,SDP这些比较上层的服务，而L2CAP层则是放在内核里面。对于BlueZ我们对SDP和L2CAP挨个分析。 

1， 实现SDP服务的代码在代码目录的**/src/sdp**，其中**sdp-client.c**是它的客户端，**sdp-server.c**是它的服务端。我们要分析的漏洞都是远程的漏洞，所以**问题是出在服务端里面**，我们重点关注服务端。而服务端最核心的代码，应该是它对接受到的数据包的处理的过程，这个过程由**sdp-request.c**来实现。当L2CAP层有SDP数据后，会触发sdp-server.c的**io_session_event**函数，来获取这个数据包，交由**sdp-request.c**的**handle_request**函数处理(怎么处理的，后续漏洞分析的时候再讲)：

```
static gboolean io_session_event(GIOChannel *chan, GIOCondition cond, gpointer data)
`{`
	...
	len = recv(sk, &amp;hdr, sizeof(sdp_pdu_hdr_t), MSG_PEEK); //获取SDP的头部数据，获得SDP数据大小
	if (len &lt; 0 || (unsigned int) len &lt; sizeof(sdp_pdu_hdr_t)) `{`
		sdp_svcdb_collect_all(sk);
		return FALSE;
	`}`

	size = sizeof(sdp_pdu_hdr_t) + ntohs(hdr.plen);
	buf = malloc(size);
	if (!buf)
		return TRUE;

	len = recv(sk, buf, size, 0);  //获得完整数据包
	...
	handle_request(sk, buf, len);

	return TRUE;
`}`
```

2， L2CAP层的代码在内核里，这里我以Linux 4.2.8这份代码为例。l2cap层主要由** /net/bluetooth/l2capcore.c**和**/net/bluetooth/l2cap_sock.c**来实现。**l2cap_core.c**实现了L2CAP协议的主要内容，l2cap_sock.c通过注册sock协议的方式提供了这一层针对userspace的接口。同样的我们关心一个L2CAP对接受到数据包后的处理过程，L2CAP的数据是由HCI层传过来的，在hci_core.c的hci_rx_work函数里 

```
static void hci_rx_work(struct work_struct *work)
`{`
    
    while ((skb = skb_dequeue(&amp;hdev-&gt;rx_q))) `{`
        /* Send copy to monitor */
        hci_send_to_monitor(hdev, skb);

        ...
        switch (bt_cb(skb)-&gt;pkt_type) `{`
        case HCI_EVENT_PKT:
            BT_DBG("%s Event packet", hdev-&gt;name);
            hci_event_packet(hdev, skb);
            break;

        case HCI_ACLDATA_PKT:
            BT_DBG("%s ACL data packet", hdev-&gt;name);
            hci_acldata_packet(hdev, skb);
            break;

        case HCI_SCODATA_PKT:
            BT_DBG("%s SCO data packet", hdev-&gt;name);
            hci_scodata_packet(hdev, skb);
            break;

        default:
            kfree_skb(skb);
            break;
        `}`
    `}`
`}`
```

收到数据后，会判断pkt_type，符合L2CAP层的type是**HCI_ACLDATA_PKT**，函数会走到**hci_acldata_packet**，这个函数会把HCI的数据剥离之后，把L2CAP数据交给L2CAP层的**l2cap_recv_acldata**：

```
static void hci_acldata_packet(struct hci_dev *hdev, struct sk_buff *skb)
`{`
    ...
    skb_pull(skb, HCI_ACL_HDR_SIZE);
    ...
    if (conn) `{`
        hci_conn_enter_active_mode(conn, BT_POWER_FORCE_ACTIVE_OFF);

        /* Send to upper protocol */
        l2cap_recv_acldata(conn, skb, flags);
        return;
    `}` else `{`
        BT_ERR("%s ACL packet for unknown connection handle %d",
               hdev-&gt;name, handle);
    `}`

    kfree_skb(skb);
`}`
```

同样的，对于L2CAP层对数据的细致处理，我们还是等后续和漏洞来一块进行分析。

**BlueDroid**

在现在的Android里，用的是**BlueDroid**架构。这个和BlueZ架构有很大不同的一点是：**BlueDroid将L2CAP层放在了userspace**。SDP，BNEP，L2CAP统统都由**com.android.bluetooth**这个进程管理。而BlueDroid代码的核心目录在Android源码目录下的 **/sytem/bt** ，这个目录的核心产物是**bluetooth.default.so**，这个so集成所有Android蓝牙相关的服务，而且这个so没有导出任何相关接口函数，只导出了几个协议相关的全局变量供使用，所以想根据so来本地检测本机是否有BlueDrone漏洞，是一件比较困难的事情。对于BlueDroid，由于android的几个漏洞出在BNEP服务和SDP服务，所以也就主要就针对这两块。值得注意的是，在Android里，**不论是64位还是32位的系统，这个bluetooth.default.so都是用的32位的**。文章里这部分代码都基于**Android7.1.2**的源码。 

**1，BlueDroid的SDP服务的代码，在/system/bt/stack/sdp 文件夹里，其中sdp服务端对数据包的处理由sdp-server.c实现**。SDP连接建立起来后，在收到SDP数据包之后呢，会触发回调函数sdp_data_ind，这个函数会把数据包交个**sdp-server.c**的sdp_server_handle_client_req函数进行处理: 

```
static void sdp_data_ind (UINT16 l2cap_cid, BT_HDR *p_msg)
`{`
    tCONN_CB    *p_ccb;
    if ((p_ccb = sdpu_find_ccb_by_cid (l2cap_cid)) != NULL)
    `{`
        if (p_ccb-&gt;con_state == SDP_STATE_CONNECTED)
        `{`
            if (p_ccb-&gt;con_flags &amp; SDP_FLAGS_IS_ORIG)
                sdp_disc_server_rsp (p_ccb, p_msg);
            else
                sdp_server_handle_client_req (p_ccb, p_msg);
        `}`
    ...
`}`
```

**2，BlueDroid的BNEP服务的代码主要在/system/bt/stack/bnep/bnepmain.c**。BNEP连接建立起来后，再收到BNEP的包，和SDP类似，会触发回调函数bnep_data_ind，这个函数包含了所有对BNEP请求的处理，漏洞也是发生在这里，具体的代码我们后续会分析。

<br>

**0x02 漏洞分析以及PoC写法**

****

蓝牙的预备知识差不多了，主要是找数据包的入口。我们再基于漏洞和PoC的编写过程来详细分析其中的处理过程，和相关蓝牙操作的代码该怎么写。

**CVE-2017-1000251**

这个是Linux L2CAP层的漏洞，那么就是内核里面的。先不着急看漏洞，先看L2CAP层如何工作。在一个L2CAP连接的过程中，我们抓取了它的数据包来分析，L2CAP是怎么建立起连接的： 

[![](https://p5.ssl.qhimg.com/t0194b724c02b075871.png)](https://p5.ssl.qhimg.com/t0194b724c02b075871.png)

我们注意这么几个包： sent_infomation_request , send_connection_request, send_configure_request。抓包可以看到，在一次完整的L2CAP连接的建立过程中，发起连接的机器，会主动送出这么几个包。其中infomation_request是为了得到对方机器的名称等信息，connection_request是为了建立L2CAP真正的连接，主要是为了确定双方的CHANNEL ID，后续的数据包传输都要跟着这个channel id 走（图上的SCID, DCID），这个channel也就是我们所说的连接。在connection_request处理完毕之后，连接状态将变成 BT_CONNECT2 。随后机器会发起configure_request,这一步就到了armis的paper第十页所说的configuration  process: 

[![](https://p4.ssl.qhimg.com/t01ea93fbf1848191bd.png)](https://p4.ssl.qhimg.com/t01ea93fbf1848191bd.png)

这个过程完成后，整个L2CAP层的连接也就建立完成。

从上述过程看，可以发现L2CAP层连接的建立，主要是对上述三个请求的发起和处理。而我们的漏洞，也其实就发生在configuration  process。我们先分析接收端收到这三个请求后，处理的逻辑在哪里，也就是我们前文提到的L2CAP对接受到的数据的处理过程： 

1，在l2cap_recv_acldata接收到数据后，数据包会传给l2cap_recv_frame 

2，l2cap_recv_frame会取出检查L2CAP的头部数据，然后检查根据头部里的cid字段，来选择处理逻辑： 

```
static void l2cap_recv_frame(struct l2cap_conn *conn, struct sk_buff *skb)
`{`
    ...
    skb_pull(skb, L2CAP_HDR_SIZE);
    cid = __le16_to_cpu(lh-&gt;cid);
    len = __le16_to_cpu(lh-&gt;len);

    switch (cid) `{`
    case L2CAP_CID_SIGNALING:
        l2cap_sig_channel(conn, skb);
        break;

    case L2CAP_CID_CONN_LESS:
        psm = get_unaligned((__le16 *) skb-&gt;data);
        skb_pull(skb, L2CAP_PSMLEN_SIZE);
        l2cap_conless_channel(conn, psm, skb);
        break;

    case L2CAP_CID_LE_SIGNALING:
        l2cap_le_sig_channel(conn, skb);
        break;

    default:
        l2cap_data_channel(conn, cid, skb);
        break;
    `}`
```

3，底层L2CAP的连接，cid固定是L2CAP_CID_SIGNALING，于是会走l2cap_sig_channel，l2cap_sig_channel得到的是剥离了头部的L2CAP的数据，这一部将把数据里的cmd头部解析并剥离，再传给l2cap_bredr_sig_cmd进行处理：

```
static inline void l2cap_sig_channel(struct l2cap_conn *conn,
                     struct sk_buff *skb)
`{`
    ...
    while (len &gt;= L2CAP_CMD_HDR_SIZE) `{`
        u16 cmd_len;
        memcpy(&amp;cmd, data, L2CAP_CMD_HDR_SIZE);  //取得cmd头部数据
        data += L2CAP_CMD_HDR_SIZE;
        len  -= L2CAP_CMD_HDR_SIZE;

        cmd_len = le16_to_cpu(cmd.len);  //取得cmd的大小
    ...
        err = l2cap_bredr_sig_cmd(conn, &amp;cmd, cmd_len, data); //传给l2cap_bredr_sig_cmd处理
    ...
        data += cmd_len;
        len  -= cmd_len;
    `}`

drop:
    kfree_skb(skb);
`}`
```

到这里，我们应该能得出L2CAP协议的数据结构：

[![](https://p1.ssl.qhimg.com/t013cef5472d84ad03e.png)](https://p1.ssl.qhimg.com/t013cef5472d84ad03e.png)

4， 随后数据进入到了l2cap_bredr_sig_cmd函数进行处理。这里也就是处理L2CAP各种请求的核心函数了： 

```
static inline int l2cap_bredr_sig_cmd(struct l2cap_conn *conn,
                      struct l2cap_cmd_hdr *cmd, u16 cmd_len,
                      u8 *data)
`{`
    int err = 0;

    switch (cmd-&gt;code) `{`
    case L2CAP_CONN_REQ:
        err = l2cap_connect_req(conn, cmd, cmd_len, data);
        break;

    case L2CAP_CONN_RSP:
    case L2CAP_CREATE_CHAN_RSP:
        l2cap_connect_create_rsp(conn, cmd, cmd_len, data);
        break;

    case L2CAP_CONF_REQ:
        err = l2cap_config_req(conn, cmd, cmd_len, data);
        break;

    case L2CAP_CONF_RSP: 
        l2cap_config_rsp(conn, cmd, cmd_len, data);  //漏洞函数
        break;
    ...
    case L2CAP_INFO_REQ:
        err = l2cap_information_req(conn, cmd, cmd_len, data);
        break;

    case L2CAP_INFO_RSP:
        l2cap_information_rsp(conn, cmd, cmd_len, data);
        break;
    ...
    `}`

    return err;
`}`
```

好了，接下来终于可以分析漏洞了。我们的漏洞发生在对**L2CAP_CONFIG_RSP（config response）**这个cmd的处理上。其实漏洞分析armis的paper已经写的很详尽了，我这里也就权当翻译了吧，然后再加点自己的理解。那么来看l2cap_config_rsp: 

```
static inline int l2cap_config_rsp(struct l2cap_conn *conn,
                   struct l2cap_cmd_hdr *cmd, u16 cmd_len,
                   u8 *data)
`{`
    struct l2cap_conf_rsp *rsp = (struct l2cap_conf_rsp *)data;
    ...
    
    scid   = __le16_to_cpu(rsp-&gt;scid);   //从包中剥离出scid
    flags  = __le16_to_cpu(rsp-&gt;flags);  //从包中剥离出flag
    result = __le16_to_cpu(rsp-&gt;result); //从包中剥离出result
    
    switch (result) `{`
    case L2CAP_CONF_SUCCESS:
        l2cap_conf_rfc_get(chan, rsp-&gt;data, len);
        clear_bit(CONF_REM_CONF_PEND, &amp;chan-&gt;conf_state);
        break;

    case L2CAP_CONF_PENDING:
        set_bit(CONF_REM_CONF_PEND, &amp;chan-&gt;conf_state);

        if (test_bit(CONF_LOC_CONF_PEND, &amp;chan-&gt;conf_state)) `{`  //判断conf_state是否是CONF_LOC_CONF_PEND
            char buf[64]; //buf数组大小64字节

            len = l2cap_parse_conf_rsp(chan, rsp-&gt;data, len,
                           buf, &amp;result);   //data仍然是包中数据，len也是包中数据。
            ...
        `}`
        goto done;
    ...
```

当收到的数据包里，满足**result == L2CAP_CONF_PENDING**，且自身的连接状态**conf_state == CONF_LOC_CONF_PEND**的时候，会走到 **l2cap_parse_conf_rsp**函数里，而且传过去的buf是个长度为64的数据，参数len ，参数rsp-&gt;data都是由包中的内容来任意确定。那么在**l2cap_parse_conf_rsp**函数里：

```
static int l2cap_parse_conf_rsp(struct l2cap_chan *chan, void *rsp, int len,
                void *data, u16 *result)
`{`
    struct l2cap_conf_req *req = data;
    void *ptr = req-&gt;data;
    int type, olen;
    unsigned long val;

    while (len &gt;= L2CAP_CONF_OPT_SIZE) `{` //len没有被检查，由接收到的包内容控制
        len -= l2cap_get_conf_opt(&amp;rsp, &amp;type, &amp;olen, &amp;val);

        switch (type) `{`
        case L2CAP_CONF_MTU:
            if (val &lt; L2CAP_DEFAULT_MIN_MTU) `{`
                *result = L2CAP_CONF_UNACCEPT;
                chan-&gt;imtu = L2CAP_DEFAULT_MIN_MTU;
            `}` else
                chan-&gt;imtu = val;
            l2cap_add_conf_opt(&amp;ptr, L2CAP_CONF_MTU, 2, chan-&gt;imtu);
            break;
        case ...
       
        `}`
    `}`
`}`

static void l2cap_add_conf_opt(void **ptr, u8 type, u8 len, unsigned long val)
`{`
    struct l2cap_conf_opt *opt = *ptr;
    opt-&gt;type = type;
    opt-&gt;len  = len;

    switch (len) `{`
    case 1:
        *((u8 *) opt-&gt;val)  = val;
        break;

    case 2:
        put_unaligned_le16(val, opt-&gt;val);
        break;

    case 4:
        put_unaligned_le32(val, opt-&gt;val);
        break;

    default:
        memcpy(opt-&gt;val, (void *) val, len);
        break;
    `}`

    *ptr += L2CAP_CONF_OPT_SIZE + len;
`}`
```

仔细阅读这个函数的代码可以知道，这个函数的功能就是**根据传进来的包，来构造将要发出去的包**。而数据的出口就是传进去的64字节大小的buf。但是对传入的包的数据的长度并没有做检验，那么当len很大时，就会一直往出口buf里写数据，比如有64个**L2CAP_CONF_MTU**类型的opt，那么就会往buf里写上**64*(L2CAP_CONF_OPT_SIZE + 2)**个字节，那么显然这里就发生了溢出。由于buf是栈上定义的数据结构，那么这里就是一个栈溢出。 不过值得注意的是，代码要走进去，需要**conf_state == CONF_LOC_CONF_PEND**，这个状态是在处理**L2CAP_CONF_REQ**数据包的时候设置的：

```
static int l2cap_parse_conf_req(struct l2cap_chan *chan, void *data)
`{`
    ...
    u8 remote_efs = 0;
    u16 result = L2CAP_CONF_SUCCESS;
    ...
    while (len &gt;= L2CAP_CONF_OPT_SIZE) `{`
        len -= l2cap_get_conf_opt(&amp;req, &amp;type, &amp;olen, &amp;val);  
        
        hint  = type &amp; L2CAP_CONF_HINT;
        type &amp;= L2CAP_CONF_MASK;

        switch (type) `{`
        ...
        case L2CAP_CONF_EFS:
            remote_efs = 1;  //【1】
            if (olen == sizeof(efs))
                memcpy(&amp;efs, (void *) val, olen);
            break;
        ...
    `}`

done:
    ...
    if (result == L2CAP_CONF_SUCCESS) `{`
        ...
        if (remote_efs) `{`
            if (chan-&gt;local_stype != L2CAP_SERV_NOTRAFIC &amp;&amp;   
                efs.stype != L2CAP_SERV_NOTRAFIC &amp;&amp;   //【2】
                efs.stype != chan-&gt;local_stype) `{`

                ...
            `}` else `{`
                /* Send PENDING Conf Rsp */
                result = L2CAP_CONF_PENDING;
                set_bit(CONF_LOC_CONF_PEND, &amp;chan-&gt;conf_state);  //这里设置CONF_LOC_CONF_PEND
            `}`
        `}`
`}`
```

当收到L2CAP_CONF_REQ的包中包含有L2CAP_CONF_EFS类型的数据【1】，而且L2CAP_CONF_EFS数据的**stype == L2CAP_SERV_NOTRAFIC**【2】的时候，conf_state会被置CONF_LOC_CONF_PEND

到这里，这个漏洞触发的思路也就清楚了：

 1，建立和目标机器的L2CAP 连接，这里注意sock_type的选择要是SOCK_RAW，如果不是，内核会自动帮我们完成sent_infomation_request, send_connection_request, send_configure_request这些操作，也就无法触发目标机器的漏洞了。 

2，建立SOCK_RAW连接，connect的时候，会自动完成sent_infomation_request的操作，不过这个不影响。 

3，接下来我们需要完成send_connection_request操作，来确定SCID,DCID。完成这个操作的过程是发送合法的 L2CAP_CONN_REQ数据包。 

4，接下来需要发送包含有L2CAP_CONF_EFS类型的数据，而且L2CAP_CONF_EFS数据的stype ==L2CAP_SERV_NOTRAFIC的L2CAP_CONF_REQ包，这一步是为了让目标机器的conf_state变成CONF_LOC_CONF_PEND。 

5，这里就到了发送cmd_len很长的L2CAP_CONN_RSP包了。这个包的result字段需要是L2CAP_CONF_PENDING。那么这个包发过去之后，目标机器就内核栈溢出了，要么重启了，要么死机了。

这个漏洞是这几个漏洞里，触发最难的。

**CVE-2017-1000250**

这个漏洞是BlueZ的SDP服务里的信息泄露漏洞。这个不像L2CAP层的连接那么复杂，主要就是上层服务，收到数据就进行处理。那么我们也只需要关注处理的函数。 之前说过，BlueZ的SDP收到数据是从io_session_event开始。之后，数据的流向是：

```
iosessionevent--&gt;handlerequest--&gt;processrequest
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017b1cfadbce82a807.png)

有必要介绍一下SDP协议的数据结构：  它有一个sdp_pud_hdr的头部，头部数据里定义了PUD命令的类型，tid，以及pdu parameter的长度，然后就是具体的parameter。最后一个字段是continuation state，当一个包发不完所要发送的数据的时候，这个字段就会有效。对与这个字段，BlueZ给了它一个定义：

```
typedef struct `{`
    uint32_t timestamp;
    union `{`
        uint16_t maxBytesSent;
        uint16_t lastIndexSent;
    `}` cStateValue;
`}` sdp_cont_state_t;
```

对于远程的连接，PDU命令类型只能是这三个：SDP_SVC_SEARCH_REQ, SDP_SVC_ATTR_REQ, SDP_SVC_SEARCH_ATTR_REQ。这个漏洞呢，出现在对SDP_SVC_SEARCH_ATTR_REQ命令的处理函数里面 service_search_attr_req 。这个函数有点长，就直接说它干了啥，不贴代码了：

1， extract_des(pdata, data_left, &amp;pattern, &amp;dtd, SDP_TYPE_UUID); 解析service search pattern（对应SDP协议数据结构图） 

2，max = getbe16(pdata); 获得Maximu Attribute Byte 

3，scanned = extract_des(pdata, data_left, &amp;seq, &amp;dtd, SDP_TYPE_ATTRID);解析Attribute ID list 

4，if (sdp_cstate_get(pdata, data_left, &amp;cstate) &lt; 0) ;获取continuation state状态cstate，如果不为0，则将包里的continuation state数据复制给cstate.

漏洞发生在对cstate状态不为0的时候的处理，我们重点看这部分的代码： 

```
sdp_buf_t *pCache = sdp_get_cached_rsp(cstate);
        if (pCache) `{`
            uint16_t sent = MIN(max, pCache-&gt;data_size - cstate-&gt;cStateValue.maxBytesSent);
            pResponse = pCache-&gt;data;
            memcpy(buf-&gt;data, pResponse + cstate-&gt;cStateValue.maxBytesSent, sent); //【1】    
            buf-&gt;data_size += sent;
            cstate-&gt;cStateValue.maxBytesSent += sent;
            if (cstate-&gt;cStateValue.maxBytesSent == pCache-&gt;data_size)
                cstate_size = sdp_set_cstate_pdu(buf, NULL);
            else
                cstate_size = sdp_set_cstate_pdu(buf, cstate);
```

sdp_get_cached_rsp函数其实是对cstate的timestamp值的检验，如何过这个检验之后再说。当代码走到【1】处的memcpy时，由于**cstate-&gt;maxBytesSent**就是由数据包里的数据所控制，而且没有做任何检验，所以这里可以为任意的uint16t值。那么很明显，这里就出现了一个对pResponse的越界读的操作。而越界读的数据还会通过SDP RESPONSE发送给攻击方，那么一个信息泄露就发生了。

写这个poc需要注意sdp_get_cached_rsp的检验的绕过，那么首先需要得到一个timestamp。当一次发送的包不足以发送完所有的数据的时候，会设置cstate状态，所以如果我们发给服务端的包里，max字段非常小，那么服务端就会给我们回应一个带cstate状态的包，这里面会有timestamp: 

```
if (cstate == NULL) `{`
        ...
        if (buf-&gt;data_size &gt; max) `{`  //max 可由接收到的包数据指定
            sdp_cont_state_t newState;

            memset((char *)&amp;newState, 0, sizeof(sdp_cont_state_t));
            newState.timestamp = sdp_cstate_alloc_buf(buf); //这里得到一个timestamp
    
            buf-&gt;data_size = max;
            newState.cStateValue.maxBytesSent = max;
            cstate_size = sdp_set_cstate_pdu(buf, &amp;newState); //回应的包中，写上cstate状态。
        `}` else
            cstate_size = sdp_set_cstate_pdu(buf, NULL);
```

所以，我们的poc应该是这个步骤： 

1，建立SDP连接。这里我们的socket需要是SOCK_STREAM类型，而且connet的时候，addr的psm字段要是0x0001。关于连接的PSM： 

[![](https://p4.ssl.qhimg.com/t01c3673f9acb1068bb.png)](https://p4.ssl.qhimg.com/t01c3673f9acb1068bb.png)

2，发送一个不带cstate状态的数据包，而且指定Maximu Attribute Byte的值非常小。这一步是为了让服务端给我们返回一个带timestamp的包。 

3，接收这个带timestamp的包，并将timestamp提取。 

4，发送一个带cstate状态的数据包，cstate的timestamp是指定为提取出来的值，服务端memcpy的时候，则就会把pResponse+maxBytesSent的内容发送给我们，读取这个数据包，则就获取了泄露的数据。

**CVE-2017-0785**

这个漏洞也是SDP的信息泄露漏洞，不过是BlueDroid的。与BlueZ的那个是有些类似的。我们也从对SDP数据包的处理函数说起。 SDP数据包会通过sdp_data_ind函数送给sdp_server_handle_client_req。与BlueZ一样，这个函数也会根据包中的pud_id来确定具体的处理函数。这个漏洞发生在对SDP_PDU_SERVICE_SEARCH_REQ命令的处理，对包内数据的解析与上文BlueZ中的大同小异，不过注意在BlueDroid中，cstate结构与BlueZ中有些不同： 

```
typedef struct `{`

    uint16_t cont_offset;

`}` sdp_cont_state_t;
```

这里主要看漏洞：

```
①, BE_STREAM_TO_UINT16 (max_replies, p_req);从包中解析出Maximu Attribute Byte

②， for (num_rsp_handles = 0; num_rsp_handles &lt; max_replies; ) 
    `{`
        p_rec = sdp_db_service_search (p_rec, &amp;uid_seq);

        if (p_rec)
            rsp_handles[num_rsp_handles++] = p_rec-&gt;record_handle;
        else
            break;
    `}`

③, /* Check if this is a continuation request */
    if (*p_req)
    `{`
        if (*p_req++ != SDP_CONTINUATION_LEN || (p_req &gt;= p_req_end))
        `{`
            sdpu_build_n_send_error (p_ccb, trans_num, SDP_INVALID_CONT_STATE,
                                     SDP_TEXT_BAD_CONT_LEN);
            return;
        `}`
        BE_STREAM_TO_UINT16 (cont_offset, p_req);  //从包中得到cont_offset

        if (cont_offset != p_ccb-&gt;cont_offset)  //对cont_offset的检验
        `{`
            sdpu_build_n_send_error (p_ccb, trans_num, SDP_INVALID_CONT_STATE,
                                     SDP_TEXT_BAD_CONT_INX);
            return;
        `}`

        rem_handles = num_rsp_handles - cont_offset;    /* extract the remaining handles */
    `}`
   else
    `{` 
        rem_handles = num_rsp_handles;
        cont_offset = 0;
        p_ccb-&gt;cont_offset = 0;
    `}`

④， cur_handles = (UINT16)((p_ccb-&gt;rem_mtu_size - SDP_MAX_SERVICE_RSPHDR_LEN) / 4);

    if (rem_handles &lt;= cur_handles)
        cur_handles = rem_handles;
    else /* Continuation is set */
    `{`
        p_ccb-&gt;cont_offset += cur_handles;
        is_cont = TRUE;
    `}`

⑤， for (xx = cont_offset; xx &lt; cont_offset + cur_handles; xx++)
        UINT32_TO_BE_STREAM (p_rsp, rsp_handles[xx]);
```

①，②中代码可以看出，变量num_rsp_handles的值，一定程度上可以由包中的Maximu Attribute Byte字段控制。 ③中代码是对带cstate的包的处理，第一步是对大小的检查，第二步是获得cont_offset，然后对cont_offset进行检查，第三步就到了 **rem_handles = num_rsp_handles – cont_offset**  可以思考一种情况，如果num_rsp_handles &lt; cont_offset，那么这个代码就会发生整数的下溢，而num_rsp_handles在一定程度上我们可以控制，而且是可以控制它变成０，那么只要cont_offset不为０，这里就会发生整数下溢。发生下溢的结果给了rem_handles，而这个变量代表的是还需要发送的数据数。 在④中，如果rem_handles是发生了下溢的结果，由于它是uint16_t类型，那么它将变成一个很大的数，所以会走到 **pccb-&gt;cont_offset += cur_handles**;,cur_handles是一个固定的值，那么如果这个下溢的过程，发生很多次，pccb-&gt;cont_offset就会变得很大，那么在５处，就会有一个对rsp_handles数组的越界读的产生。

下面的操作可以让这个越界读发生： 

１，发送一个不带cstate的包， 而且Maximu Attribute Byte字段设置的比较大。那么结果就是rem_handles = num_rsp_handles，而由于max_replies比较大，所以**num_rsp_handles**会成为一个比较大的值。只要在④中保证rem_handles &gt; cur_handles，那么pccb-&gt;cont_offset就会成为一个非０值cur_handles。这一步是为了使得pccb-&gt;cont_offset成为一个非０值。 

２，接收服务端的回应包，这个回应包里的cstate字段将会含有刚刚的pccb-&gt;cont_offset值，我们取得这个值。 

３，发送一个带cstate的包，cont_offset指定为刚刚提取的值，而且设置Maximu Attribute Byte字段为０。那么服务端收到这个包后，就会走到**rem_handles = num_rsp_handles – cont_offset**从而发生整数下溢，同时pccb-&gt;cont_offset又递增一个cur_handles大小。 

４，重复２和３的过程，那么pccb-&gt;cont_offset将越来越大，从而在⑤出发生越界读，我们提取服务端返回的数据，就可以获得泄露的信息的内容。

**CVE-2017-0781**

现在我们到了BNEP服务。BNEP的协议格式，下面两张图可以说明的很清楚： 

[![](https://p0.ssl.qhimg.com/t01f1a9caed32a953ab.png)](https://p0.ssl.qhimg.com/t01f1a9caed32a953ab.png)

[![](https://p2.ssl.qhimg.com/t01dba407c6650628cd.png)](https://p2.ssl.qhimg.com/t01dba407c6650628cd.png)

BlueDroid中BNEP服务对于接受到的数据包的处理也不复杂： 

1,解析得到BNEP_TYPE，得到extension位。 

2,检查连接状态，如果已经连接则后续可以处理非**BNEP_FRAME_CONTROL**的包，如果没有建立连接，则后续只处理BNEP_FRAME_CONTROL的包。 

3,去BNEP_TYPE对应的处理函数进行处理。 

4,对于BNEP_TYPE不是BNEP_FRAME_CONTROL而且有extension位的，还需要对extension的数据进行处理。 

5,调用pan层的回调函数。

值得注意的是，BNEP连接真正建立起来，需要先处理一个合法的**BNEP_FRAME_CONTROL**数据包。 CVE-2017-0781正是连接还没建立起来，在处理**BNEP_FRAME_CONTROL**时所发生的问题： 

```
case BNEP_FRAME_CONTROL:
        ctrl_type = *p;
        p = bnep_process_control_packet (p_bcb, p, &amp;rem_len, FALSE);

        if (ctrl_type == BNEP_SETUP_CONNECTION_REQUEST_MSG &amp;&amp;
            p_bcb-&gt;con_state != BNEP_STATE_CONNECTED &amp;&amp;
            extension_present &amp;&amp; p &amp;&amp; rem_len)
        `{`
            p_bcb-&gt;p_pending_data = (BT_HDR *)osi_malloc(rem_len);
            memcpy((UINT8 *)(p_bcb-&gt;p_pending_data + 1), p, rem_len);
            p_bcb-&gt;p_pending_data-&gt;len    = rem_len;
            p_bcb-&gt;p_pending_data-&gt;offset = 0;
        `}`
```

上述代码中，malloc了一个remlen的大小，这个是和收到的数据包的长度相关的。可是memcpy的时候，却是从**pbcb-&gt;p_pending_data＋１**开始拷贝数据，那么这里会直接溢出一个**sizeof(*(pbcb-&gt;p_pending_data))**大小的内容。这个大小是8.所以只要代码走到这，就会有一个8字节大小的堆溢出。而要走到这，只需要过那个if的判断条件，而这个if其实是对**BNEP_SETUP_CONNECTION_REQUEST_MSG**命令处理失败后的错误处理函数。那么只要发送一个错误的**BNEP_SETUP_CONNECTION_REQUEST_MSG**命令包，就可以进入到这段代码了触发堆溢出了。

所以我们得到poc的编写过程： 

１，建立BNEP连接，这个和SDP类似，只是需要指定PSM为BNEP对应的0x000F。 

２，发送一个BNEPTYPE为**BNEP_FRAME_CONTROL**，extension字段为１，ctrl_type为**BNEP_SETUP_CONNECTION_REQUEST_MSG**的错误的BNEP包： 

[![](https://p0.ssl.qhimg.com/t01f234b30e2a95b672.png)](https://p0.ssl.qhimg.com/t01f234b30e2a95b672.png)

**CVE-2017-0782**

这个也是由于BNEP协议引起的漏洞，首先它是个整数溢出，整数溢出导致的后果是堆溢出。 问题出在BNEP对extension字段的处理上： 

```
UINT8 *bnep_process_control_packet (tBNEP_CONN *p_bcb, UINT8 *p, UINT16 *rem_len, BOOLEAN is_ext)
`{`
    UINT8       control_type;
    BOOLEAN     bad_pkt = FALSE;
    UINT16      len, ext_len = 0;

    if (is_ext)
    `{`
        ext_len = *p++; 【１】
        *rem_len = *rem_len - 1;
    `}`

    control_type = *p++;
    *rem_len = *rem_len - 1;

    switch (control_type)
    `{`
    ...
    default :
        bnep_send_command_not_understood (p_bcb, control_type);
        if (is_ext)
        `{`
            p += (ext_len - 1);
            *rem_len -= (ext_len - 1); 【２】
        `}`
        break;
    `}`

    if (bad_pkt)
    `{`
        BNEP_TRACE_ERROR ("BNEP - bad ctl pkt length: %d", *rem_len);
        *rem_len = 0;
        return NULL;
    `}`

    return p;
`}`
```

上述代码中，【１】的ext_len从数据包中获得，没有长度的检查，可为任意值。而当control_type为一个非法值的时候，会走到【２】,那么这里就很有说法了，我们如果设置ext_len比较大，那么这里就会发生一个整数下溢。从而使得rem_len变成一个很大的uint16_t的值。这个值将会影响后续的处理：

```
while (extension_present &amp;&amp; p &amp;&amp; rem_len)
    `{`
        ext_type = *p;
        extension_present = ext_type &gt;&gt; 7;
        ext_type &amp;= 0x7F;
        ...
        p++;
        rem_len--;
        p = bnep_process_control_packet (p_bcb, p, &amp;rem_len, TRUE);　【１】
    `}`

    p_buf-&gt;offset += p_buf-&gt;len - rem_len;　　
    p_buf-&gt;len     = rem_len;　　【２】
    
    ...
    if (bnep_cb.p_data_buf_cb)
    `{`
        (*bnep_cb.p_data_buf_cb)(p_bcb-&gt;handle, p_src_addr, p_dst_addr, protocol, p_buf, 　fw_ext_present);　　【３】
    `}`
　　...
        osi_free(p_buf);
    `}`
```

上面的代码中，【１】处将发生整数下溢出，使得rem_len成为一个很大的值（比如0xfffd），【２】处会将这个值赋值给p_buf-&gt;len。【３】处是回调函数处理这个p_buf，在BlueDroid中这个函数是**pan_data_buf_ind_cb**，这个函数会有一条路径调到**bta_pan_data_buf_ind_cback**，而在这个函数中：

```
static void bta_pan_data_buf_ind_cback(UINT16 handle, BD_ADDR src, BD_ADDR dst, UINT16 protocol, BT_HDR *p_buf,
                                   BOOLEAN ext, BOOLEAN forward)
`{`
    tBTA_PAN_SCB *p_scb;
    BT_HDR *p_new_buf;

    if (sizeof(tBTA_PAN_DATA_PARAMS) &gt; p_buf-&gt;offset) `{`
        /* offset smaller than data structure in front of actual data */
        p_new_buf = (BT_HDR *)osi_malloc(PAN_BUF_SIZE);
        memcpy((UINT8 *)(p_new_buf + 1) + sizeof(tBTA_PAN_DATA_PARAMS),
               (UINT8 *)(p_buf + 1) + p_buf-&gt;offset, p_buf-&gt;len);
        p_new_buf-&gt;len    = p_buf-&gt;len;
        p_new_buf-&gt;offset = sizeof(tBTA_PAN_DATA_PARAMS);
        osi_free(p_buf);
    `}` else `{`
    ...
`}`
```

memcpy用到了我们传进来的pbuf，而**pbuf-&gt;len**是刚刚下溢之后的很大的值，所以主要保证**tBTA_PAN_DATA_PARAMS****&gt; pbuf-&gt;offset**，这里就会发生一次很大字节的堆溢出。

代码首先要走到extension的处理，这个的前提是连接状态是BNEP_STATE_CONNECTED。而这个状态的建立，需要服务端先接收一个正确的**BNEP_SETUP_CONNECTION_REQUEST_MSG**请求包，同时要想pan_data_buf_ind_cb调用到bta_pan_data_buf_ind_cback产生堆溢出，需要在建立连接的时候指定UUID为**UUID_SERV_CLASS_PANU**可以阅读这两个函数来找到这样做的原因，这里就不再贴代码了。清楚这一点之后，我们就可以构造我们的poc了： 

１，建立BNEP连接，这里只是建立起初步的连接，conn_state还不是**BNEP_STATE_CONNECTED**，这一步通过connect实现 

２，发送一个正确的**BNEP_SETUP_CONNECTION_REQUEST_MSG**请求包，同时指定UUID为UUID_SERV_CLASS_PANU。这个包将是这样子：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016ac18cd242578315.png)

3，发送一个extension字段可导致整数下溢的包，而且注意控制pbuf-&gt;offset变得比较小： 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0171ee065bcee0d619.png)

这样PoC就完成了。 **CVE-2017-0781**和**CVE-2017-0782**导致了堆溢出，一般会使得**com.android.bluetooth**崩溃，但是这个进程崩溃系统不会有提醒，需要去logcat来找崩溃的日志。**这是两个很有品质的堆溢出漏洞，结合前面的信息泄露漏洞，是完全可以转化为远程代码执行的。**

<br>

**0x03**

****

这篇分析到这里也就结束了，蓝牙出漏洞是个比较危险的事情，希望没有修补的能尽快修补，补丁链接如下：

[CVE-2017-1000250](https://git.kernel.org/pub/scm/bluetooth/bluez.git/commit/?id=9e009647b14e810e06626dde7f1bb9ea3c375d09)

[CVE-2017-1000251](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e860d2c904d1a9f38a24eb44c9f34b8f915a6ea3)

[CVE-2017-0785](https://android.googlesource.com/platform/system/bt/+/226ea26684d4cd609a5b456d3d2cc762453c2d75)

[CVE-2017-0781](https://android.googlesource.com/platform/system/bt/+/c513a8ff5cfdcc62cc14da354beb1dd22e56be0e)

[CVE-2017-0782](https://android.googlesource.com/platform/system/bt/+/4e47f3db62bab524946c46efe04ed6a2b896b150)

确定自己是否有漏洞可以用我们提供的poc呀，关于蓝牙漏洞的研究，也希望能和各位多多交流。

<br>

**参考文档:**

****

1,[https://www.armis.com/blueborne/](https://www.armis.com/blueborne/) 

2,[http://blog.csdn.net/rain0993/article/details/8533246](http://blog.csdn.net/rain0993/article/details/8533246) 

3,[https://people.csail.mit.edu/albert/bluez-intro/index.html](https://people.csail.mit.edu/albert/bluez-intro/index.html) 

<br>

**0x04**

****

360Vulpecker Team: 隶属于360公司信息安全部，致力于保护公司所有Android App及手机的安全，同时专注于移动安全研究，研究重点为安卓APP安全和安卓OEM手机安全。 团队定制了公司内部安卓产品安全开发规范，自主开发并维护了在线Android应用安全审计系统“360显危镜”，在大大提高工作效率的同时也为开发者提供了便捷的安全自测平台。同时研究发现了多个安卓系统上的通用型漏洞，如通用拒绝服务漏洞、“寄生兽”漏洞等，影响范围几乎包括市面上所有应用。 该团队高度活跃在谷歌、三星、华为等各大手机厂商的致谢名单中，挖掘的漏洞屡次获得CVE编号及致谢，在保证360产品安全的前提下，团队不断对外输出安全技术，为移动互联网安全贡献一份力量。


