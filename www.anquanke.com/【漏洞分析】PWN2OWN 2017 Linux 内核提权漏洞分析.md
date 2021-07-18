
# 【漏洞分析】PWN2OWN 2017 Linux 内核提权漏洞分析


                                阅读量   
                                **89969**
                            
                        |
                        
                                                                                    



[![](./img/86008/t01a995396db4e93cd7.jpg)](./img/86008/t01a995396db4e93cd7.jpg)

**0.前言**

**在2017年PWN2OWN大赛中，长亭安全研究实验室（Chaitin Security Research Lab）成功演示了Ubuntu 16.10 Desktop的本地提权。本次攻击主要利用了linux内核IPSEC框架(自linux2.6开始支持)中的一个内存越界漏洞，CVE编号为CVE-2017-7184。**

众所周知，Linux的应用范围甚广,我们经常使用的Android、Redhat、CentOS、Ubuntu、Fedora等都使用了Linux操作系统。在PWN2OWN之后，Google、Redhat也针对相应的产品发出了漏洞公告或补丁(见参考资料)。并表示了对长亭安全研究实验室的致谢，在此也建议还没有升级服务器内核的小伙伴们及时更新内核到最新版本:P

不同于通常的情况，为了增加比赛难度，本次PWN2OWN大赛使用的Linux版本开启了诸多漏洞缓解措施，kASLR、SMEP、SMAP都默认开启，在这种情况下，漏洞变得极难利用，很多漏洞可能仅仅在这些缓解措施面前就会败下阵来。

另外值得一提的是，本次利用的漏洞隐蔽性极高，在linux内核中存在的时间也非常长。因为触发这个漏洞不仅需要排布内核数据结构，而且需要使内核处理攻击者精心构造的数据包，使用传统的fuzz方式几乎是不可能发现此漏洞的。

最终，长亭安全研究实验室成功利用这个漏洞在PWN2OWN的赛场上弹出了PWN2OWN历史上的第一个xcalc, ZDI的工作人员们看到了之后也表示惊喜不已。

[![](./img/86008/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f70888feb0a3cbe8.png)

下面一起来看一下整个漏洞的发现和利用过程。

<br>

**1.IPSEC协议简介**

IPSEC是一个协议组合，它包含AH、ESP、IKE协议，提供对数据包的认证和加密功能。

为了帮助更好的理解漏洞成因，下面有几个概念需要简单介绍一下

**(1) SA(Security Associstion)**

SA由spi、ip、安全协议标识(AH或ESP)这三个参数唯一确定。SA定义了ipsec双方的ip地址、ipsec协议、加密算法、密钥、模式、抗重放窗口等。

**(2) AH(Authentication Header)**

AH为ip包提供数据完整性校验和身份认证功能，提供抗重放能力，验证算法由SA指定。

**(3) ESP(Encapsulating security payload)**

ESP为ip数据包提供完整性检查、认证和加密。

<br>

**2.Linux内核的IPSEC实现**

在linux内核中的IPSEC实现即是xfrm这个框架，关于xfrm的代码主要在net/xfrm以及net/ipv4下。

以下是/net/xfrm下的代码的大概功能



```
xfrm_state.c     状态管理
xfrm_policy.c    xfrm策略管理
xfrm_algo.c      算法管理
xfrm_hash.c      哈希计算函数
xfrm_input.c     安全路径(sec_path)处理， 用于处理进入的ipsec包
xfrm_user.c      netlink接口的SA和SP(安全策略)管理
```

其中xfrm_user.c中的代码允许我们向内核发送netlink消息来调用相关handler实现对SA和SP的配置，其中涉及处理函数如下。



```
xfrm_dispatch[XFRM_NR_MSGTYPES] = {
[XFRM_MSG_NEWSA       - XFRM_MSG_BASE] = { .doit = xfrm_add_sa        },
[XFRM_MSG_DELSA       - XFRM_MSG_BASE] = { .doit = xfrm_del_sa        },
[XFRM_MSG_GETSA       - XFRM_MSG_BASE] = { .doit = xfrm_get_sa,
.dump = xfrm_dump_sa,
.done = xfrm_dump_sa_done  },
[XFRM_MSG_NEWPOLICY   - XFRM_MSG_BASE] = { .doit = xfrm_add_policy    },
[XFRM_MSG_DELPOLICY   - XFRM_MSG_BASE] = { .doit = xfrm_get_policy    },
[XFRM_MSG_GETPOLICY   - XFRM_MSG_BASE] = { .doit = xfrm_get_policy,
                                   .dump = xfrm_dump_policy,
                                   .done = xfrm_dump_policy_done },
[XFRM_MSG_ALLOCSPI    - XFRM_MSG_BASE] = { .doit = xfrm_alloc_userspi },
[XFRM_MSG_ACQUIRE     - XFRM_MSG_BASE] = { .doit = xfrm_add_acquire   },
[XFRM_MSG_EXPIRE      - XFRM_MSG_BASE] = { .doit = xfrm_add_sa_expire },
[XFRM_MSG_UPDPOLICY   - XFRM_MSG_BASE] = { .doit = xfrm_add_policy    },
[XFRM_MSG_UPDSA       - XFRM_MSG_BASE] = { .doit = xfrm_add_sa        },
[XFRM_MSG_POLEXPIRE   - XFRM_MSG_BASE] = { .doit = xfrm_add_pol_expire},
[XFRM_MSG_FLUSHSA     - XFRM_MSG_BASE] = { .doit = xfrm_flush_sa      },
[XFRM_MSG_FLUSHPOLICY - XFRM_MSG_BASE] = { .doit = xfrm_flush_policy  },
[XFRM_MSG_NEWAE       - XFRM_MSG_BASE] = { .doit = xfrm_new_ae  },
[XFRM_MSG_GETAE       - XFRM_MSG_BASE] = { .doit = xfrm_get_ae  },
[XFRM_MSG_MIGRATE     - XFRM_MSG_BASE] = { .doit = xfrm_do_migrate    },
[XFRM_MSG_GETSADINFO  - XFRM_MSG_BASE] = { .doit = xfrm_get_sadinfo   },
[XFRM_MSG_NEWSPDINFO  - XFRM_MSG_BASE] = { .doit = xfrm_set_spdinfo,
                           .nla_pol = xfrma_spd_policy,
           .nla_max = XFRMA_SPD_MAX },
[XFRM_MSG_GETSPDINFO  - XFRM_MSG_BASE] = { .doit = xfrm_get_spdinfo   },
};
```

下面简单介绍一下其中几个函数的功能:

**xfrm_add_sa**

创建一个新的SA，并可以指定相关attr，在内核中，是用一个xfrm_state结构来表示一个SA的。

**xfrm_del_sa**

删除一个SA，也即删除一个指定的xfrm_state。

**xfrm_new_ae**

根据传入参数，更新指定xfrm_state结构中的内容。

**xfrm_get_ae**

根据传入参数，查询指定xfrm_state结构中的内容(包括attr)。

<br>

**3.漏洞成因**

当我们发送一个XFRM_MSG_NEWSA类型的消息时，即可调用xfrm_add_sa函数来创建一个新的SA，一个新的xfrm_state也会被创建。在内核中，其实SA就是使用xfrm_state这个结构来表示的。

若在netlink消息里面使用XFRMA_REPLAY_ESN_VAL这个attr，一个replay_state_esn结构也会被创建。它的结构如下所示，可以看到它包含了一个bitmap，这个bitmap的长度是由bmp_len这个成员变量动态标识的。



```
struct xfrm_replay_state_esn {
    unsigned int bmp_len;
    __u32   oseq;
    __u32   seq;
    __u32   oseq_hi;
    __u32   seq_hi;
    __u32   replay_window;
    __u32   bmp[0];
};
```

内核对这个结构的检查主要有以下几种情况:

首先，xfrm_add_sa函数在调用verify_newsa_info检查从用户态传入的数据时，会调用verify_replay来检查传入的replay_state_esn结构。



```
static inline int verify_replay(struct xfrm_usersa_info *p,
struct nlattr **attrs)
{
struct nlattr *rt = attrs[XFRMA_REPLAY_ESN_VAL];
struct xfrm_replay_state_esn *rs;
if (p-&gt;flags &amp; XFRM_STATE_ESN) {
if (!rt)
return -EINVAL;
rs = nla_data(rt);
if (rs-&gt;bmp_len &gt; XFRMA_REPLAY_ESN_MAX / sizeof(rs-&gt;bmp[0]) / 8)
return -EINVAL;
if (nla_len(rt) &lt; xfrm_replay_state_esn_len(rs) &amp;&amp;
    nla_len(rt) != sizeof(*rs))
return -EINVAL;
}
if (!rt)
return 0;
/* As only ESP and AH support ESN feature. */
if ((p-&gt;id.proto != IPPROTO_ESP) &amp;&amp; (p-&gt;id.proto != IPPROTO_AH))
return -EINVAL;
if (p-&gt;replay_window != 0)
return -EINVAL;
return 0;
}
```

这个函数要求replay_state_esn结构的bmp_len不可以超过最大限制XFRMA_REPLAY_ESN_MAX。

另外，在这个创建xfrm_state的过程中，如果检查到成员中有xfrm_replay_state_esn结构，如下函数中的检查便会被执行。



```
int xfrm_init_replay(struct xfrm_state *x)
{
struct xfrm_replay_state_esn *replay_esn = x-&gt;replay_esn;
if (replay_esn) {
if (replay_esn-&gt;replay_window &gt;
    replay_esn-&gt;bmp_len * sizeof(__u32) * 8) &lt;-----检查replay_window
return -EINVAL;
if (x-&gt;props.flags &amp; XFRM_STATE_ESN) {
if (replay_esn-&gt;replay_window == 0)
return -EINVAL;
x-&gt;repl = &amp;xfrm_replay_esn;
} else
x-&gt;repl = &amp;xfrm_replay_bmp;
} else
x-&gt;repl = &amp;xfrm_replay_legacy;
return 0;
}
```

这个函数确保了replay_window不会比bitmap的长度大，否则函数会直接退出。

下面再来看一下xfrm_new_ae这个函数,它首先会解析用户态传入的几个attr，然后根据spi的哈希值以及ip找到指定的xfrm_state，之后xfrm_replay_verify_len中会对传入的replay_state_esn结构做一个检查，通过后即会调用xfrm_update_ae_params函数来更新对应的xfrm_state结构。下面我们来看一下xfrm_replay_verify_len这个函数。



```
static inline int xfrm_replay_verify_len(struct xfrm_replay_state_esn *replay_esn,
 struct nlattr *rp)
{
struct xfrm_replay_state_esn *up;
int ulen;
if (!replay_esn || !rp)
return 0;
up = nla_data(rp);
ulen = xfrm_replay_state_esn_len(up);
if (nla_len(rp) &lt; ulen || xfrm_replay_state_esn_len(replay_esn) != ulen)
return -EINVAL;
return 0;
}
```

我们可以看到这个函数没有对replay_window做任何的检查，只需要提供的bmp_len与xfrm_state中原来的bmp_len一致就可以通过检查。所以此时我们可以控制replay_window超过bmp_len。之后内核在处理相关IPSEC数据包进行重放检测相关的操作时，对这个bitmap结构的读写操作都可能会越界。

<br>

**4.漏洞利用**

**(1).权限不满足**



```
/* All operations require privileges, even GET */
if (!netlink_net_capable(skb, CAP_NET_ADMIN))
return -EPERM;
```

在xfrm_user_rcv_msg函数中，我们可以看到，对于相关的操作，其实都是需要CAP_NET_ADMIN权限的。那是不是我们就无法触发这个漏洞了呢？

答案是否定的，在这里我们可以利用好linux的命名空间机制，在ubuntu，Fedora等发行版，User namespace是默认开启的。非特权用户可以创建用户命名空间、网络命名空间。在命名空间内部，我们就可以有相应的capability来触发漏洞了。

**(2).越界写**

当内核在收到ipsec的数据包时，最终会在xfrm_input解包并进行相关的一些操作。在xfrm_input中，找到对应的xfrm_state之后，根据数据包内容进行重放检测的时候会执行x-&gt;repl-&gt;advance(x, seq);，即xfrm_replay_advance_esn这个函数。

这个函数会对bitmap进行如下操作

**1.清除[last seq, current seq)的bit**

**2.设置bmp[current seq] = 1**

我们可以指定好spi、seq等参数(内核是根据spi的哈希值以及ip地址来确定SA的)，并让内核来处理我们发出的ESP数据包，多次进行这个操作即可达到对越界任意长度进行写入任意值。

**(3).越界读**

我们的思路是使用越界写，改大下一个replay_state_esn的结构中的bmp_len。之后我们就可以利用下一个bitmap结构进行越界读。所以我们需要两个相邻的replay_state结构。我们可以使用defragment技巧来达到这个效果。即首先分配足够多的同样大小的replay_state结构把堆上原来的坑填满，之后便可大概率保证连续分配的replay_state结构是相邻的。

如上所述，使用越界写的能力将下一个bitmap长度改大，即可使用这个bitmap结构做越界读了。

图中所示为被改掉bmp_len的bitmap结构。

[![](./img/86008/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0188423e5130febc98.png)

**(4).绕过kASLR**

我们通过xfrm_del_sa接口把没用的xfrm_state都给删掉。这样就可以在堆上留下很多的坑。之后我们可以向内核喷射很多struct file结构体填在这些坑里。

如下，利用上面已经构造出的越界读能力，我们可以泄露一些内核里的指针来算出内核的加载地址和bitmap的位置。

[![](./img/86008/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010ebaed594ada719d.png)

<br>

**5.内核任意地址读写及代码执行**

因为已经绕过了内核地址随机化,这时我们可以进行内核ROP构造了。

1.在这个漏洞的利用当中，我们可以在bitmap中伪造一个file_operations结构。

2.之后通过越界写可以改写掉我们刚刚在内核中喷射的struct file结构体的file_operations指针，使其指向合适的ROPgadget。

3.调用llseek函数(实际上已经是rop gadget)来执行我们事先已经准备好的ROP链。

4.通过多次改写file_operations结构中的llseek函数指针来实现多次执行ROPgadget实现提权。

[![](./img/86008/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fb0b5a576e8a08a4.png)

如上所述，因为我们的数据都是伪造在内核里面，所以这种利用方式其实是可以同时绕过SMEP和SMAP的。

<br>

**6.权限提升**

下面是长亭安全研究实验室在pwn2own2017上弹出xcalc的瞬间。

[![](./img/86008/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ae1d434a0ac7e150.png)

<br>

**5.后记**

非常感谢slipper老师的指导和讲解 😛

感谢长亭安全研究实验室的所有小伙伴:P

<br>

**6.参考资料**

IPSEC协议: [IPsec – Wikipedia](http://link.zhihu.com/?target=https%3A//en.wikipedia.org/wiki/IPsec)

linux命名空间机制: [Namespaces in operation, part 1: namespaces overview](http://link.zhihu.com/?target=https%3A//lwn.net/Articles/531114/)

CVE-2017-7184: [CVE-2017-7184: kernel: Local privilege escalation in XFRM framework](http://link.zhihu.com/?target=http%3A//www.openwall.com/lists/oss-security/2017/03/29/2)

@thezdi: [https://twitter.com/thezdi/status/842132539330375684](http://link.zhihu.com/?target=https%3A//twitter.com/thezdi/status/842132539330375684)

Android漏洞公告:[https://source.android.com/security/bulletin/2017-05-01](http://link.zhihu.com/?target=https%3A//source.android.com/security/bulletin/2017-05-01)

Redhat:[Red Hat Customer Portal](http://link.zhihu.com/?target=https%3A//access.redhat.com/security/cve/cve-2017-7184)
