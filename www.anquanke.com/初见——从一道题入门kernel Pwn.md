> 原文链接: https://www.anquanke.com//post/id/244149 


# 初见——从一道题入门kernel Pwn


                                阅读量   
                                **156102**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01166c0919f3f66dda.jpg)](https://p0.ssl.qhimg.com/t01166c0919f3f66dda.jpg)



初次做内核相关的题目，也算是为内核学习铺一铺路了，从一个新手的角度来看这道内核题目，简单介绍一下新手眼中的 kernel pwn

## 一、环境搭建

环境搭建始终都是绕不开的话题，其实题目环境相对于依赖较多的内核模块调试来说已经是一个很理想的环境了，但是这里还是要稍微补充一点点小 trick。

### <a class="reference-link" name="1.%20%E8%8E%B7%E5%8F%96%E8%B0%83%E8%AF%95%E4%BF%A1%E6%81%AF"></a>1. 获取调试信息

题目中的 shell 权限通常来说都是低权限账户，当然要是直接是高权限账户也没必要来提权了，此时就会有两个问题
<li>
`cat /proc/kallsyms` 低权限下拿不到具体的内核地址</li>
<li>
`cat /sys/module/[module name]/sections/.text` 低权限无法获取</li>
说到底还是低权限的问题，此时来看仿佛遇到了死锁，题目肯定不会给你高权限shell，没有高权限shell就无法 cat 出对应的信息来进行调试。<br>
解决办法其实就在 `init` 文件中，通常情况下题目都是自己编写的 kernel + filesystem，因此需要有一个将题目ko文件自动加载起来的方式，也就是 `init` 文件。<br>
这里简单介绍一下`init`文件正常的用途：是在自己编译完毕 kernel 后，打包好一个包含 busybox 的小型文件系统，在该文件系统中通过 `init` 文件来 mount 一些基本的目录。<br>
题目中的则是用来 insmod 题目文件了，insmod 是需要高权限才能执行成功的，因此，我们可以在 `init` 文件中 insmod 行之后添加如下两行内容：

```
cat /proc/kallsyms &gt; /tmp/kallsyms
cat /sys/module/sudrv/sections/.text &gt; /tmp/sudrv
```

即可在题目启动后获取对应的信息来进行调试了。



## 二、知识点介绍

这道题目主要是抱着学习的态度来看的，因此在自己做之前就已经看了好几个不同师傅的wp，从wp中可以提炼出来这道题的知识点主要有以下几个
- 内核ROP
- cred提权
- 内核堆结构
- 用户态与内核态切换
下面分别对这些知识点进行一下介绍

### <a class="reference-link" name="1.%20%E5%86%85%E6%A0%B8ROP"></a>1. 内核ROP

该技术主要针对的是 SMEP 技术，即管理模式执行保护，主要作用是禁止内核直接访问用户空间的数据以及内核执行用户空间的代码，SMEP 针对的是 ret2user 的攻击手段（可谓道高一尺魔高一丈，每当一个保护机制的产生总会有绕过手段的出现啊）<br>
检查 SEMP 开启的方法有两个：
- `cat /proc/cpuinfo | grep semp`
<li>查看 qemu 启动脚本，包含如下内容即开启了 semp `-cpu kvm64,+smep`
</li>
内核ROP原理上同普通ROP比较接近，区别在于传参方式的不同，内核中传参通过寄存器而不是栈。<br>
提权 rop 链结构如下：

```
|----------------------|
| pop rdi; ret         |&lt;== low mem
|----------------------|
| NULL                 |
|----------------------|
| addr of              |
| prepare_kernel_cred()|
|----------------------|
| mov rdi, rax; ret    |
|----------------------|
| addr of              |
| commit_creds()       |&lt;== high mem
|----------------------|
```

实际执行的内容是 `commit_creds(prepare_kernel_cred(0))`，在内核中执行完毕上述代码后再用户层直接执行 `system("/bin/sh")` 即可获取 root shell。<br>
寻找 rop gadget 可以从 vmlinux 中获取，可用工具有 ROPgadget 或 ropper 等 。

### <a class="reference-link" name="2.%20cred%20%E6%8F%90%E6%9D%83%E5%8E%9F%E7%90%86"></a>2. cred 提权原理

**<a class="reference-link" name="(1).%20cred%E7%AE%80%E4%BB%8B"></a>(1). cred简介**

在介绍提权原理之前，首先要知道 cred 究竟是什么东西。<br>
每个线程在内核中都有一个描述该线程的 `thread_info` 结构，在 `thread_info` 中包含一个名为 `task_struct` 的结构体，这个结构体中就包含有今天的主角 `cred` 结构体，`cred` 结构体中主要用来保存线程的权限信息。<br>`task_struct` 定义于 `include/linux/sched.h` 文件中

```
struct task_struct `{`
   ...
   ...
       /* Process credentials: */

    /* Tracer's credentials at attach: */
    const struct cred __rcu        *ptracer_cred;

    /* Objective and real subjective task credentials (COW): */
    const struct cred __rcu        *real_cred;

    /* Effective (overridable) subjective task credentials (COW): */
    const struct cred __rcu        *cred;
  ...
  ...
`}`
```

整个 `task_struct` 定义足有700多行，这里仅截取和 `cred` 相关的定义，`cred` 结构体的定义如下

```
/include/linux/cred.h

struct cred `{`
    atomic_t    usage;
#ifdef CONFIG_DEBUG_CREDENTIALS
    atomic_t    subscribers;    /* number of processes subscribed */
    void        *put_addr;
    unsigned    magic;
#define CRED_MAGIC    0x43736564
#define CRED_MAGIC_DEAD    0x44656144
#endif
    kuid_t        uid;        /* real UID of the task */
    kgid_t        gid;        /* real GID of the task */
    kuid_t        suid;        /* saved UID of the task */
    kgid_t        sgid;        /* saved GID of the task */
    kuid_t        euid;        /* effective UID of the task */
    kgid_t        egid;        /* effective GID of the task */
    kuid_t        fsuid;        /* UID for VFS ops */
    kgid_t        fsgid;        /* GID for VFS ops */
    unsigned    securebits;    /* SUID-less security management */
    kernel_cap_t    cap_inheritable; /* caps our children can inherit */
    kernel_cap_t    cap_permitted;    /* caps we're permitted */
    kernel_cap_t    cap_effective;    /* caps we can actually use */
    kernel_cap_t    cap_bset;    /* capability bounding set */
    kernel_cap_t    cap_ambient;    /* Ambient capability set */
#ifdef CONFIG_KEYS
    unsigned char    jit_keyring;    /* default keyring to attach requested
                     * keys to */
    struct key    *session_keyring; /* keyring inherited over fork */
    struct key    *process_keyring; /* keyring private to this process */
    struct key    *thread_keyring; /* keyring private to this thread */
    struct key    *request_key_auth; /* assumed request_key authority */
#endif
#ifdef CONFIG_SECURITY
    void        *security;    /* subjective LSM security */
#endif
    struct user_struct *user;    /* real user ID subscription */
    struct user_namespace *user_ns; /* user_ns the caps and keyrings are relative to. */
    struct group_info *group_info;    /* supplementary groups for euid/fsgid */
    /* RCU deletion */
    union `{`
        int non_rcu;            /* Can we skip RCU deletion? */
        struct rcu_head    rcu;        /* RCU deletion hook */
    `}`;
`}` __randomize_layout;
```

**<a class="reference-link" name="(2).%20%E6%8F%90%E6%9D%83%E5%8E%9F%E7%90%86"></a>(2). 提权原理**

在 cred 结构体中，uid~fsgid 代表了当前进程所属用户、用户组等信息的 id 值，提权操作实际就是将 cred 中的这些字段覆盖为了 root 用户/组 的 id (0)。<br>
通过溢出的方式进行exploit，通过 leak data 等手段定位到 `cred` 结构体之后，将 uid~fsgid 全部覆盖为 0 即实现了提权。<br>
通过 rop 方式可在泄露 commit_creds 以及 prepare_kernel_cred 函数地址的情况下构造 rop 调用函数来完成对 cred 结构的修改。

### <a class="reference-link" name="3.%20%E5%86%85%E6%A0%B8%E5%A0%86%E7%BB%93%E6%9E%84"></a>3. 内核堆结构

内核中存在三种内存分配器分别是 SLAB、SLUB 以及 SLOB。这三种内存分配器并不能同时存在，而是在内核进行编译的时候进行选择。`kmalloc` 请求内存时候就是由这三个内存分配器其中之一进行处理的。<br>
在用户层 ptmalloc 将内存中各种堆块划分为 bins，内核中则为 slabs，当执行 `kmalloc` 函数的时候，内核会对请求的大小做向上对齐，并选取合适的slab进行分配。<br>
需要注意的是在同一条 slab 链中的堆块(slot) 大小是相同的，且这些slot物理相邻，slab具有三种状态，分别是：
- 全部占用
- 全部空闲
- 部分空闲
题目中用到的 slab就属于全部空闲的状态。<br>
通过 `cat /proc/slabinfo` 显示slab相关信息

[![](https://p1.ssl.qhimg.com/t015f1a02a3a0e65ddd.png)](https://p1.ssl.qhimg.com/t015f1a02a3a0e65ddd.png)

`slabtop` 显示 slab 占用情况

[![](https://p4.ssl.qhimg.com/t0102dc2520dc393b5b.png)](https://p4.ssl.qhimg.com/t0102dc2520dc393b5b.png)

题目中根据前后两个 slot 地址的差值可以算出来当前 slab 链为 kmalloc-64。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ab3de0be4dc9dc89.png)

下图可以证实 slab 链中 slot 物理相邻的情况

[![](https://p5.ssl.qhimg.com/t01cfe28bbee0717d95.png)](https://p5.ssl.qhimg.com/t01cfe28bbee0717d95.png)

[![](https://p1.ssl.qhimg.com/t01ec6f274b7a947506.png)](https://p1.ssl.qhimg.com/t01ec6f274b7a947506.png)

为什么是 kmalloc-64 呢？在测试代码中，申请的size 分别是 0x30、0x40，0x30的向上兼容，自然就会都分配到 0x40 的链上了。

[![](https://p3.ssl.qhimg.com/t01594ffae7da96c835.png)](https://p3.ssl.qhimg.com/t01594ffae7da96c835.png)

从调试结果来看，题目用到的 slab，kmalloc返回的指针指向的前8字节即下个堆块的地址，类似于 fastbin 的结构。

### <a class="reference-link" name="4.%20%E7%94%A8%E6%88%B7%E6%80%81%E4%B8%8E%E5%86%85%E6%A0%B8%E6%80%81%E5%88%87%E6%8D%A2"></a>4. 用户态与内核态切换

当编写 poc 所需要的信息都拿到的时候，就该开始着手写代码了，在写代码之前，首先要了解一个很重要的知识，就是用户态与内核态的切换，当发生系统调用、内核处理异常或中断时，会进入内核态，因为进入内核执行完一段代码后会导致寄存器等一些数据并不是用户态进入内核前的数据，因此在进入内核态之前需要保存用户态的现场，等内核代码执行完毕后返回用户态时再恢复现场。<br>
保存用户态现场的代码如下：

```
unsigned long user_cs, user_ss, user_eflags,user_sp ;
void save_status() `{`
    asm(
        "movq %%cs, %0\n"
        "movq %%ss, %1\n"
        "movq %%rsp, %3\n"
        "pushfq\n"
        "popq %2\n"
        :"=r"(user_cs), "=r"(user_ss), "=r"(user_eflags),"=r"(user_sp)
        :
        : "memory"
    );
`}`
```



## 三、题目简介

init 函数中注册了一个名为 `meizijiutql` 的设备，根据 `__register_chrdev` 的描述，需要注意的是最后一个参数 `const struct file _operations * fops`​

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019a3fa0b249a0c26b.png)

[![](https://p0.ssl.qhimg.com/t0156c77deb02a6d106.png)](https://p0.ssl.qhimg.com/t0156c77deb02a6d106.png)

`file_operations` 定义了对该设备各类操作的处理函数

[![](https://p1.ssl.qhimg.com/t01bb7a31fabae03553.png)](https://p1.ssl.qhimg.com/t01bb7a31fabae03553.png)

这里仍存在的疑惑是，exploit的时候是调用了 `sudrv_write` 来进行用户数据到内核拷贝的，但是并没有找到对该函数的引用。<br>
通过对 `sudrv_ioctl` 进行分析可以得到三个功能，分别是内核堆的分配、释放以及输出

[![](https://p5.ssl.qhimg.com/t0180fcf1f3543bc80a.png)](https://p5.ssl.qhimg.com/t0180fcf1f3543bc80a.png)

[![](https://p5.ssl.qhimg.com/t01d16bf7874ee08b73.png)](https://p5.ssl.qhimg.com/t01d16bf7874ee08b73.png)

在加上之前的 `sudrv_write` 即可凑齐完成漏洞的基本读写原语了，在用户层通过 `open` 打开 `/dev/meizijiutql` 后利用 `ioctl` 以及 `write` 来进行与内核模块的交互。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012200556943e79312.png)

这里还存在一个疑问，`copy_user_generic_unrolled` 的定义 `[__must_check](https://elixir.bootlin.com/linux/latest/C/ident/__must_check) unsigned long [copy_user_generic_unrolled](https://elixir.bootlin.com/linux/latest/C/ident/copy_user_generic_unrolled)(void *[to](https://elixir.bootlin.com/linux/latest/C/ident/to), const void *[from](https://elixir.bootlin.com/linux/latest/C/ident/from), unsigned len);` 是有三个参数的，这里的调用仅有一个 `rdi` 作为参数，那么剩下两个参数去哪里了？

[![](https://p2.ssl.qhimg.com/t01d9b88360f706ee68.png)](https://p2.ssl.qhimg.com/t01d9b88360f706ee68.png)



## 四、exploit

### <a class="reference-link" name="1.%20%E6%A0%BC%E5%BC%8F%E5%8C%96%E6%BC%8F%E6%B4%9E%E6%80%8E%E4%B9%88%E7%94%A8%EF%BC%9F"></a>1. 格式化漏洞怎么用？

在调试漏洞的时候可以直接获取到符号信息，以及其在内核中的实际地址，但是在远程环境中是无法获取的，因此需要利用格式化字符串漏洞泄露出两个关键的信息：<br>
内核加载基址<br>
栈地址<br>
其中内核加载基址被用于 rop 链的构造，栈地址则用于控制流的劫持。

需要注意的知识点在于内核中打印地址需要使用 `%llx` 而不是 `%p`​<br>
断点下在执行 printk 之前，打印栈内的内容，单步执行后查看 printk 输出，首先通过 kallsyms 获取到当前内核加载基址

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01dfcae1c37b71d139.png)

[![](https://p1.ssl.qhimg.com/t016f22dd2658f08935.png)](https://p1.ssl.qhimg.com/t016f22dd2658f08935.png)

在 printk 输出具体内容之前查看栈上的内容，可以看到一个栈地址以及一个与内核加载基址相近的地址。

### <a class="reference-link" name="2.%20rop%20%E9%93%BE%E5%88%86%E6%9E%90%EF%BC%8C%E5%A6%82%E4%BD%95%E5%88%86%E9%85%8D%E5%88%B0%E6%A0%88%E4%B8%8A%E3%80%82"></a>2. rop 链分析，如何分配到栈上。

因为内核堆的结构类似于fastbin，那么可以通过溢出覆盖指向下个堆块的指针来完成从堆到栈的变换，此时就可以用上之前泄露出来的栈相关的内容了。<br>
在初始情况下，内核中堆链如下：

[![](https://p0.ssl.qhimg.com/t01493c674184d2cb9a.png)](https://p0.ssl.qhimg.com/t01493c674184d2cb9a.png)

[![](https://p1.ssl.qhimg.com/t0123e3243ec305fd76.png)](https://p1.ssl.qhimg.com/t0123e3243ec305fd76.png)

此时查看内存结果如下，可以看到 `ee40` 的堆块指向的是 `ef00` 的地址，`ef00`堆块的头部为全零，即该堆块为当前链中的最后一个堆块。

[![](https://p0.ssl.qhimg.com/t0184d33a09968c8117.png)](https://p0.ssl.qhimg.com/t0184d33a09968c8117.png)

而当对该堆块调用`sudrv_write`进行写入后，再次查看即可发现，本来 `ef00` 开头处为0的8个字节被覆盖为了指向栈上的指针。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0129cbbb94aaf26f9c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d0765a3ae5c7a9c5.png)

当内核执行完kmalloc后，会将next slot的地址保存在全局变量中，因此第二次kmalloc会分配到`ef00`处的堆块。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018ba67089ce983809.png)

`ef00`堆块处我们需要的仅仅是让其 next pointer 指向栈上，因此此处可以随意填充数据。

[![](https://p0.ssl.qhimg.com/t017b9d25b7cfcf753f.png)](https://p0.ssl.qhimg.com/t017b9d25b7cfcf753f.png)

当第三次kmalloc的时候，就成功将堆块分配到了栈上。

[![](https://p0.ssl.qhimg.com/t0183376b8c040ef47b.png)](https://p0.ssl.qhimg.com/t0183376b8c040ef47b.png)

下图为分配前栈上内容

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01225813c53962aa54.png)

下图为分配后栈上内容

[![](https://p3.ssl.qhimg.com/t01cf4725cb01a564aa.png)](https://p3.ssl.qhimg.com/t01cf4725cb01a564aa.png)

### <a class="reference-link" name="3.%20rop%20%E9%93%BE%E5%88%86%E6%9E%90%EF%BC%8C%E4%B8%80%E4%B8%AA%E5%B0%8F%E5%9D%91%E3%80%82"></a>3. rop 链分析，一个小坑。

在编写rop链的时候，在调用 `commit_creds` 的时候，出了点自己无法理解的问题，直到调了rop链之后才知道还能这么玩。<br>
首先是平平无奇的对着官方wp照猫画虎，找到了这样的一条指令：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d44500755d9c1928.png)

配合着 `pop rbx;` 将 `commit_creds` 放到了 `rbx` 中，跑了一遍发现有问题，遂调试rop，然后就发现了这个有意思的情况：本来应该是 `call rbx` 的指令，变成了一个 `jmp` 加 两个 `call` 的代码串，在两次 `call` 之后，栈指针发生了变化，指向比正常rop地址减8（即rop链中commit_creds的下一个gadgets）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b5082dd00f208862.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0115645516b92861f1.png)

此时就体现出了官方rop中的 `pop rdx` 的作用，将本来应该放入 `rbx` 的 `commit_creds` 变为 `pop rdx`的地址，就完成了栈的平衡，`pop rdx`后的 `ret` 刚好调用到 `commit_creds` 函数。

### <a class="reference-link" name="4.%20rop%20%E9%93%BE"></a>4. rop 链

往栈上写数据的函数为 `sudrv_write` 当栈数据被覆盖后，该函数执行到 `ret` 指令后就会跳到我们所布置的rop链上。这里每次调用 `sudrv_write` 的时候栈位置都是相同的，因此可以直接使用之前泄漏出来的栈地址来进行rop。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0164b707eafe29e151.png)

此处执行完毕`pop rdi`后就进入到了`prepare_kernel_cred`的调用中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f4a4b6f3c7d5f4a5.png)

此处的rop链中并不是直接将 rax 的数据传入到 rdi 中，而是利用 r12 进行了一次中转，这里主要是因为在ropgadgets 中没有这两个寄存器的直接传输指令。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014b29633f35ba2698.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ece9b2e3588066df.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0124836a9b92f7f3b9.png)

调用完毕 `commit_creds()` 后执行 `swapgs` 开始恢复用户空间的寄存器。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f6f2570b7654b875.png)

一切恢复完毕后回到用户空间，此时就又引出了另一个问题，为什么要用 SIGSEGV 信号处理函数来 get shell，当我没有添加处理函数时，返回用户空间后会造成 segment fault，这里主要原因在于没有很好的恢复用户层执行上下文，导致程序崩溃，但是做题过程中不一定非要完美的恢复上下文。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a748ec4bcd93d328.png)

[![](https://p3.ssl.qhimg.com/t01d74fbb5c7f6bff12.png)](https://p3.ssl.qhimg.com/t01d74fbb5c7f6bff12.png)

因此此处只要增加上 `signal(SIGSEGV,[your handler])` 调用即可 get root shell。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0189d43a6c71ba6d0c.png)



## 参考链接

[https://team-su.github.io/passages/2019-08-22-SUCTF/?nsukey=3hbB1nNVK8IOJb1BedTGPG2ZmZsVZwVxyHIoT%2BEaiqr7iGJc9ZxKpkPOIMSxOhBkNTwNVpDNWGQLpvROOeYEjivFGK8y36eLHC4EWM1RB6w0%2Fpe%2Bae%2BPfkEStMCcErpksCMm9FzZmL5no%2FsFtcPnBucUAgZ8f%2B4IMJ2r45IUfrZFUWlCIwxLg2RXbyUds%2FuwJYg8AYKcd%2BY%2ByypJBBB5XA%3D%3D](https://team-su.github.io/passages/2019-08-22-SUCTF/?nsukey=3hbB1nNVK8IOJb1BedTGPG2ZmZsVZwVxyHIoT%2BEaiqr7iGJc9ZxKpkPOIMSxOhBkNTwNVpDNWGQLpvROOeYEjivFGK8y36eLHC4EWM1RB6w0%2Fpe%2Bae%2BPfkEStMCcErpksCMm9FzZmL5no%2FsFtcPnBucUAgZ8f%2B4IMJ2r45IUfrZFUWlCIwxLg2RXbyUds%2FuwJYg8AYKcd%2BY%2ByypJBBB5XA%3D%3D)<br>[https://www.anquanke.com/post/id/204319](https://www.anquanke.com/post/id/204319)​<br>[http://xiaoxin.zone/2020/07/28/2019-suctf-kernel-sudrv/#toc-heading-8](http://xiaoxin.zone/2020/07/28/2019-suctf-kernel-sudrv/#toc-heading-8)​<br>[https://www.jianshu.com/p/9d1fcf0304fa](https://www.jianshu.com/p/9d1fcf0304fa)​<br>[https://xz.aliyun.com/t/2054](https://xz.aliyun.com/t/2054)<br>[https://www.povcfe.site/posts/kernel_rw1/](https://www.povcfe.site/posts/kernel_rw1/)​<br>[https://blog.csdn.net/weixin_43889007/article/details/109499534](https://blog.csdn.net/weixin_43889007/article/details/109499534)​<br>[https://blog.csdn.net/seaaseesa/article/details/104591448](https://blog.csdn.net/seaaseesa/article/details/104591448)​<br>[https://argp.github.io/2012/01/03/linux-kernel-heap-exploitation/](https://argp.github.io/2012/01/03/linux-kernel-heap-exploitation/)
