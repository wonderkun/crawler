> 原文链接: https://www.anquanke.com//post/id/226285 


# 应急响应之 Linux 下进程隐藏


                                阅读量   
                                **177884**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t019fd0c593bd6e4ddb.jpg)](https://p1.ssl.qhimg.com/t019fd0c593bd6e4ddb.jpg)



## 概述

当黑客获取系统 root 权限时，为了实现持久化控制往往会创建隐藏恶意进程，这给应急响应人员取证的时候带来了难度，隐藏进程的方法分为两类，一类是用户态隐藏，另一类是内核态隐藏。用户态常使用的方法有很多，例如劫持预加载动态链接库，一般通过设置环境变量 LD_PRELOAD 或者 /etc/ld.so.preload，过滤 /proc/pid 目录、修改进程 PID 等等。内核态隐藏进程一般是加载恶意的内核模块实现进程隐藏，本文抛砖引玉，介绍应急响应场景中遇到过的 Linux 操作系统进程隐藏的手段以及检测方法。



## 劫持预加载动态链接库 LD_PRELOAD

查看 Linux 操作系统正在运行的进程，一般会使用系统命令 ps、top 等，像 ps 这样的命令通常是读取了 /proc/ 目录下文件。Linux 操作系统上的 /proc 目录存储的是当前内核运行状态的一系列特殊文件，用户可以通过这些文件查看有关操作系统硬件和当前正在运行进程的信息，甚至可以通过更改其中某些文件来改变内核的运行状态。/proc 目录中包含许多以数字命名的子目录，这些数字代表操作系统当前正在运行进程的进程号（pid），每个数字文件夹里面包含对应进程的多个信息文件。

[![](https://p3.ssl.qhimg.com/t01e36b135e16782235.png)](https://p3.ssl.qhimg.com/t01e36b135e16782235.png)

LD_PRELOAD 是 Linux 操作系统的一个环境变量，它允许定义在程序运行前优先加载的动态链接库，设置完成后立即生效。劫持预加载动态链接库的进程隐藏方式往往是过滤ps等命令从 /proc/ 获取的结果，而不是针对 /proc/ 文件系统生成本身。在应急的时候一般可以通过 strace 命令调试 ps 命令的所有系统调用以及这个进程所接收到的所有的信号量。当系统未设置了 ld.so.preload，ps 命令读取 /etc/ld.so.preload，返回值为-1，说明文件不存在。

[![](https://p3.ssl.qhimg.com/t0136eb9cf0d09aa096.png)](https://p3.ssl.qhimg.com/t0136eb9cf0d09aa096.png)

当系统设置了 ld.so.preload，ps 命令读取 /etc/ld.so.preload，返回值为 0，说明文件存在。

[![](https://p3.ssl.qhimg.com/t014cf43f706874980a.png)](https://p3.ssl.qhimg.com/t014cf43f706874980a.png)

比如，我们要隐藏进程 threat.py，可以借助 libprocesshider 项目，通过修改 static const char* processtofilter = “threat.py”，隐藏指定进程。

[![](https://p1.ssl.qhimg.com/t01218a9ed86f00000f.png)](https://p1.ssl.qhimg.com/t01218a9ed86f00000f.png)

编译后将生成的 .so 文件路径写入 /etc/ld.so.preload。运行该进程后可以看到 ps 命令未检测到隐藏进程。但是使用 busybox 可以看到隐藏进程的相关信息，那是因为 busybox ps 命令直接读取了 proc 目录的数字，不调用系统预加载库。

[![](https://p3.ssl.qhimg.com/t011cc97af6c2969173.png)](https://p3.ssl.qhimg.com/t011cc97af6c2969173.png)

测试使用的脚本名为 processhider.c，下载地址如下：

https://github.com/gianlucaborello/libprocesshider/。



## 劫持预加载动态链接库 LD_AUDIT

上面介绍了劫持 LDPRELOAD 隐藏进程，黑客往往常用这个技术拦截系统调用执行恶意代码。正如文档 ld.so 中内容，LDPRELOAD 在所有其他对象（附加的、用户指定、ELF 共享对象）之前加载，但实际上 LDPRELOAD 并非真的是首先加载，通过利用 LDAUDIT 环境变量可以实现优先于 LD_PRELOAD 加载。

[![](https://p3.ssl.qhimg.com/t0105c169cb97b996da.png)](https://p3.ssl.qhimg.com/t0105c169cb97b996da.png)

首先我们验证下 LDPRELOAD、LDAUDIT 的加载顺序。

[![](https://p3.ssl.qhimg.com/t010c29218414224107.png)](https://p3.ssl.qhimg.com/t010c29218414224107.png)

编译 preloadlib.c、auditlib.c。

[![](https://p1.ssl.qhimg.com/t017b0a83c4eec45805.png)](https://p1.ssl.qhimg.com/t017b0a83c4eec45805.png)

从执行 whoami 的结果可以看到 LDAUDIT 优先于 LDPRELOAD。

[![](https://p3.ssl.qhimg.com/t012e5633e9ebb29c2d.png)](https://p3.ssl.qhimg.com/t012e5633e9ebb29c2d.png)

还以 libprocesshider 项目为例，我们想要隐藏运行的脚本 threat.py，如果直接编译使用 LD_AUDIT 加载 so 文件，可以发现并没有隐藏进程。

[![](https://p3.ssl.qhimg.com/t0174c7f960c97e64c5.png)](https://p3.ssl.qhimg.com/t0174c7f960c97e64c5.png)

通过查询rtld-audit (https://man7.org/linux/man-pages/man7/rtld-audit.7.html)文档，可以看到调用该库需要两个函数 laobjopen 和 lasymbind64，当加载器找到并加载一个库时，将调用 rtld-audit 中的 laobjopen 函数，struct linkmap 指向要加载的库，cookie 声明一个指针指向该对象标识符，并传给 lasymbind64，lasymbind64 函数不仅可以提供信息，还可以修改程序行为。故可以在 libprocesshider.c 追加以下代码：

[![](https://p4.ssl.qhimg.com/t01b7263ba108c4a91c.png)](https://p4.ssl.qhimg.com/t01b7263ba108c4a91c.png)

重新编译后，可以看已经隐藏进程。

[![](https://p4.ssl.qhimg.com/t0131bef22c0192c54f.png)](https://p4.ssl.qhimg.com/t0131bef22c0192c54f.png)



## 修改进程 pid

通过查看 linux 内核源码，在 include/linux/threads.h 文件中可以看到 pid 最大值的为变量 PIDMAXDEFAULT，相关代码如下：

[![](https://p3.ssl.qhimg.com/t017e3ddd0df7946696.png)](https://p3.ssl.qhimg.com/t017e3ddd0df7946696.png)

如果编译内核时设置了 CONFIGBASESMALL 选项，则pid的最大值是 0x1000，即 4096 个，否则最大值是 0x8000，即 32768 个。pid 的最大值是可以修改的，但是可以修改的最大值是多少，这个是通过 PIDMAXLIMIT 限定的，从代码可知，如果编译内核时设置了 CONFIGBASESMALL 选项，则最大值就是 8 * PAGESIZE 个大小，否则就看 long 的大小，如果大于 4，也就是最大可以设置 4*1024*1024 个，也即是 4194304 个，否则最大只能设置 PIDMAX_DEFAULT 个了。

用户可以通过查看 /proc/sys/kernel/pid_max 文件获取当前操作系统的 pid 的最大值，例如 centos7 默认可以有 131072 个 pid。

[![](https://p5.ssl.qhimg.com/t01eca64969c7793853.png)](https://p5.ssl.qhimg.com/t01eca64969c7793853.png)

当前进程创建后，获取其 pid 注册 proc 目录下，然后遍历 tasklist 以其 pid 作为主键来显示 proc 目录。从上面知道 centos7 下最多有 131072 个 pid 号。故我们通过内核模块修改进程 pid，然后用户空间由于权限的限制无法读取内核配置的 pid 外的数据实现隐藏。代码如下：

[![](https://p5.ssl.qhimg.com/t01cb37607d9c0b6ddd.png)](https://p5.ssl.qhimg.com/t01cb37607d9c0b6ddd.png)

执行恶意进程，获取其进程 pid 为 2895，运行脚本后可以看到进程已经被隐藏了。

[![](https://p4.ssl.qhimg.com/t0103594f748b861cc2.png)](https://p4.ssl.qhimg.com/t0103594f748b861cc2.png)

安装 stap 后默认会在路径 /usr/share/systemtap/examples/ 下存储一些非常实用的脚本。例如 network- 目录下脚本主要查看系统中每个进程的网络传输情况，io 目录下的脚本主要查看进程对磁盘的读写情况。

[![](https://p5.ssl.qhimg.com/t01084b6c2f0fc6e084.png)](https://p5.ssl.qhimg.com/t01084b6c2f0fc6e084.png)

虽然隐藏了进程，但是还存在网络连接。故可以通过 network 目录的脚本从内核层面检测当前操作系统的网络连接获取隐藏进程。

[![](https://p1.ssl.qhimg.com/t01ea44cde620b0637a.png)](https://p1.ssl.qhimg.com/t01ea44cde620b0637a.png)

另外大多数情况下，我们只使用 kill 命令来杀死一个进程，实际上 kill 命令只是向进程发送一个信号，可以到https://github.com/torvalds/linux/blob/master/arch/x86/include/uapi/asm/signal.h查看每个信号对应的功能，信号 20 表示停止进程的运行, 但该信号可以被处理和忽略。在 Linux 下，我们 kill 一个不存在的进程会返 “No such process”，kill 一个存在的进程返回结果为空，故通过信号也可以获取隐藏进程 pid。

[![](https://p1.ssl.qhimg.com/t013d76eafaf8a98b5d.png)](https://p1.ssl.qhimg.com/t013d76eafaf8a98b5d.png)



## 伪造内核模块隐藏进程

在 Linux 上，有许多内核进程被创建来帮助完成系统任务。这些进程可用于调度、磁盘 I/O 等。当使用像 ps 之类的命令显示当前运行的进程时，内核进程的周围有[括号]，普通进程通常不会显示带方括号的进程。Linux 恶意软件使用各种技术来隐藏检测。其中一种为让进程名显示 [] 来模拟内核线程。

(1) /proc/maps 通常用来查看进程的虚拟地址空间是如何使用的。正常的内核进程 maps 内容为空的，伪装的内核进程是有内容标识的。如下 pid 为 2120 为系统正常的内核进程，pid 为 3195 是伪造的内核进程。

[![](https://p1.ssl.qhimg.com/t01001af458c85c99a0.png)](https://p1.ssl.qhimg.com/t01001af458c85c99a0.png)

(2) /proc/exe 指向运行进程的二进制程序链接，正常内核进程没有相应的二进制文件，恶意的内核进程有对应的二进制文件。

[![](https://p4.ssl.qhimg.com/t018bc9143b5da46a6b.png)](https://p4.ssl.qhimg.com/t018bc9143b5da46a6b.png)



## 总结

安全的本质是对抗，只有熟悉了黑灰产常用的攻击方式，才能做到遇事不慌。Linux 下进程隐藏的方式远远不止以上几种，笔者只是介绍了在应急响应场景下遇到的一些情况，想要了解更多，且听下回分解。



## 参考链接

https://github.com/gianlucaborello/libprocesshider

https://github.com/torvalds/linux/blob/master/arch/x86/include/uapi/asm/signal.h



## 关于微步情报局

微步情报局，即微步在线研究响应团队，负责微步在线安全分析与安全服务业务，主要研究内容包括威胁情报自动化研发、高级APT组织&amp;黑产研究与追踪、恶意代码与自动化分析技术、重大事件应急响应等。
