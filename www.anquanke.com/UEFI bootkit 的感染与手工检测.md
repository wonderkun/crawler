> 原文链接: https://www.anquanke.com//post/id/229257 


# UEFI bootkit 的感染与手工检测


                                阅读量   
                                **188865**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t01c613822c011908fe.jpg)](https://p4.ssl.qhimg.com/t01c613822c011908fe.jpg)



## 概要

BIOS，全称基本输入输出系统，其诞生之初也曾是门先进的技术，但得益于软硬件的飞速发展，传统 BIOS 由于其开发效率低下（主要使用汇编开发）、安全性差、性能低下等原因，已经逐渐退出历史舞台。取而代之的是 UEFI（个人认为称之为 UEFI BIOS 也可以）。

UEFI (Unified Extensible Firmware Interface)，全称统一可扩展固件接口。UEFI 只是一个标准，其实现主要还是其它厂商或者开源组织。例如，Intel开源的 TinaoCore，就是一个典型的与硬件无关的框架。

相比传统 BIOS，UEFI 有诸多优点，如开发效率更高（可用 C/C++ 开发），系统性能强（可以加载图片，甚至可以实现基于事件的异步操作）以及良好的可扩展性。可扩展性体现在模块化设计和动态加载上，UEFI 驱动（非 Windows 驱动）模块每个都是独立模块，可以放在固件里，也可以放在磁盘上，根据需要进行加载。

由于计算机安全技术的快速发展，目前计算机受到的攻击不仅是操作系统层面的攻击，针对固件层面的攻击也原来更为普遍。UEFI 由于其模块化设计，动态加载，使用硬盘存储扩展模块等，都导致了 UEFI BIOS 面临着更多的安全问题。

对于 UEFI BIOS 的攻击，从感染方式上来讲，个人认为可以分为两种：一种是针对 BIOS 固件的攻击，一种是磁盘上扩展模块的攻击。本文着重介绍第二种。



## UEFI 引导启动过程与感染原理

### **1. UEFI 引导启动的 7 个阶段**

要了解 UEFI 的感染原理，必须了解 UEFI 的执行流程。UEFI 标准规定，其引导启动过程分为 7 个阶段。大致过程如下：

[![](https://p2.ssl.qhimg.com/t01b304f792bf4a387e.png)](https://p2.ssl.qhimg.com/t01b304f792bf4a387e.png)

（图片源自网络，侵删）

**SEC（Security Phase）:**

1）计算机加电后的首个阶段，接收并处理启动、重启、严重异常信号；

2）初始化临时 RAM（区别于通常所说的内存），通常为 CPU 的 Cache；

3）传递参数给下一阶段（PEI 阶段）;

**PEI (Pre-EFI Initialization):**

1）为 DXE 阶段准备执行环境（完成内存初始化）；

2）将需要的信息传递给 DXE 阶段；

**DXE (Driver Execution Environment，驱动执行环境):**

加载 UEFI 驱动，完成大部分初始化工作。

**BDS (Boot Device Selection):**

执行启动策略，主要为：

1）初始化设备控制台；

2）加载相关 UEFI 驱动设备；

3）加载并执行启动项；

**TSL (Trainsient System Load):**

该阶段正式准备加载操作系统

1）加载并运行 OS Loader（OS Loader 作为 UEFI 应用）;

2）调用 ExitBootServices 后进入 RT 阶段；

**RT (Run Time):**

1）控制权由 UEFI 内核转交到 OS Loader 中；

2）清理回收 UEFI 之前占用的资源；

**AL (After Life):**

用于系统灾难恢复。

以上就是 UEFI 从加电到关机的 7 个阶段。

从设计上来讲，SEC 阶段被默认为是可信和安全的，想要对 SEC 阶段进行感染必须进行固件刷写（刷固件理论上可以对各阶段进行感染，而不仅仅是 SEC 阶段代码），这就是我们常见的 UEFI bootkit 实现方式之一。而另一种常见的实现 UEFI bootkit 感染的技术就是通过硬盘上存在的 UEFI 模块进行劫持或篡改，此种攻击方式主要是在 DXE/BSD/TSL 阶段进行。

### **2. UEFI 的感染方式**

**2.1 ESP 分区和引导**

在 Windows 环境下，借助硬盘的 ESP 分区也能实现 UEFI 感染。

如果 Windows 是通过 UEFI+GPT 方式引导启动，则在硬盘上，Windows 安装文件会在磁盘上开辟一个隐藏分区，称为 ESP 分区，如下图所示：

[![](https://p0.ssl.qhimg.com/t01ad6774fab31434eb.png)](https://p0.ssl.qhimg.com/t01ad6774fab31434eb.png)

ESP 分区本质上是 FAT 格式的分区，因为 UEFI 本身只支持 FAT 格式的文件系统。该分区中，有两个用于引导的模块，bootx64.efi（32 位下为 bootia32.efi）和 bootmgfw.efi。

bootx64.efi:\EFI\Boot\bootx64.efi;

bootmgfw.efi:\EFI\Microsoft\Boot\bootmgfw.efi;

这两个文件中，bootx64.efi 是用于磁盘引导，而 bootmgfw.efi 是进行操作系统加载的（OS Loader）。如果一定要和传统 BIOS 引导类比的话，bootx64.efi 相当于 MBR，而 bootmgfw.efi 则类似于(NTLDR/Winload.exe)。

不同的是，UEFI 下的 Windows，启动时不一定需要使用 bootx64.efi，而可以直接选择使用 bootmgfw.efi 作为 Windows 启动管理器 (Windows Boot Manager，一般默认情况下使用 bootmgfw.efi)。但如果一定要使用 bootx64.efi 进行启动，也可以进入 BIOS 进行手工设置，典型场景就是 U 盘 WinPE 进行启动，通过 U 盘内的 bootx64.efi 进行磁盘引导。

以下是笔者的 UEFI 启动设置，Windows Boot Manager 为 UEFI 系统默认，bootkit_test 是笔者手动添加的基于磁盘引导的启动方式。

[![](https://p1.ssl.qhimg.com/t01f7a6e9db393d0ad6.png)](https://p1.ssl.qhimg.com/t01f7a6e9db393d0ad6.png)

[![](https://p3.ssl.qhimg.com/t017c8f506b6db1c1eb.png)](https://p3.ssl.qhimg.com/t017c8f506b6db1c1eb.png)

需要说明的是，如果系统通过 bootx64.efi 进行启动，其最终还是会调用 bootmgfw.efi。

**2.2 EFI 模块及其本质**

对于 UEFI 开发来说，其程序一般分为两大类，一种是 UEFI 应用程序，一种是 UEFI 驱动程序，其后缀名都是 .efi 格式。但其实这并不是一种新的文件格式，而是符合 PE/COFF 规范的 PE 文件，更准确的说无论是 UEFI 应用程序还是 UEFI 驱动程序都是符合 E/COFF 的 dll 文件。EFI 文件的识别可以通过 Exeinfo PE 进行查看，如下图：

[![](https://p0.ssl.qhimg.com/t016659b6fb6d8e151c.png)](https://p0.ssl.qhimg.com/t016659b6fb6d8e151c.png)

### **2.3 bootx64.efi 与 bootmgfw.efi 的关系**

先说结论：bootx64 就是 bootmgfw，两者是同一个文件，只是放在不同路径下会调用其不同功能。

[![](https://p2.ssl.qhimg.com/t01f3fb40ea1117bdb6.png)](https://p2.ssl.qhimg.com/t01f3fb40ea1117bdb6.png)

笔者将自己电脑上的两个文件提取出来并进行了 hash 对比，发现两者 hash 完全一致。也就是说，该文件至少具备磁盘引导、Windows 启动管理以及 OS Loader 的功能。

**2.4 UEFI bootkit 代码分析与感染复现**

**2.4.1 源码流程分析**

本次采用的代码为开源 UEFI bootkit 代码，github 地址：https://github.com/ajkhoury/UEFI-Bootkit

该工程文件分为两部分，UEFIApplication 为 loader 程序（编译后重命名为 bootx64.efi），UefiDriver 为真正实现内核感染的文件（编译后重命名为 rtdriver.efi）

[![](https://p5.ssl.qhimg.com/t016092226db57931f2.png)](https://p5.ssl.qhimg.com/t016092226db57931f2.png)

先来看 bootx64.efi 的代码：

[![](https://p0.ssl.qhimg.com/t01f0af6979551e5066.png)](https://p0.ssl.qhimg.com/t01f0af6979551e5066.png)

可以看到，其代码流程非常简单，通过 `LocateFile`函数遍历所有分区，查找 rtdriver.efi，找不到就直接退出，然后通过 `ImageLoad`函数将驱动加载至内存（不运行），最后调用函数 `ImageStart `运行 bootkit 驱动，代码完成，程序退出。

rtdriver.efi 的主要代码如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014e73b89645e68d29.png)

定位 Windows Boot Manager，即 bootmgfw.efi，然后加载至内存，对函数 PatchWindowsBootManager 对bootmgfw.efi 进行 patch，然后运行 bootmgfw.efi。

进入 PatchWindowsBootManager 函数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012af5df842eecf0cc.png)

该函数对 bootmgfw.efi 的 ImgArchEfiStartBootApplication函数进行 hook 从而获得控制权，然后在自己的 hook 函数中又对 winload.efi 的 OslArchTransferToKernel 进行 hook，从而使得在加载 OS 内核镜像（ntoskrnl.exe）的时候 patch 掉 Windows 的 PatchGuard 代码，实现任意 rootkit 行为，代码如下：

[![](https://p3.ssl.qhimg.com/t0160d5bf9a22b86930.png)](https://p3.ssl.qhimg.com/t0160d5bf9a22b86930.png)

整体流程大致如下：

[![](https://p1.ssl.qhimg.com/t0159e01dfcbaa7b90c.png)](https://p1.ssl.qhimg.com/t0159e01dfcbaa7b90c.png)

**2.4.2 感染复现**

在了解了 UEFI 引导过程以及 bootkit 代码的分析后，复现就变得很容易了。

a）将编译出来的 bootx64.efi 以及 rtdriver.efi 放到 ESP 分区的 \EFI\Boot 目录下（原始 bootx64.efi 将会被替换），笔者这边是使用 Diskgenus 来操作的；

b）重启主机，进入 BIOS，关闭 Security Boot；

c）在 BIOS 中增加磁盘启动的引导项。

复现成功后如下图所示：

[![](https://p0.ssl.qhimg.com/t019af34a2ffcb33293.png)](https://p0.ssl.qhimg.com/t019af34a2ffcb33293.png)

[![](https://p0.ssl.qhimg.com/t01f3aa67858d6b7b5d.png)](https://p0.ssl.qhimg.com/t01f3aa67858d6b7b5d.png)



## UEFI 感染的手工检测方法

### **1. efi 文件检测**

使用磁盘工具将 ESP 分区盘符显示出来，然后查看 bootx64.efi（32 位 bootia32.efi）以及 bootmgfw.efi 的文件签名是否为微软的，并查看 ESP 分区下是否有多余的 EFI 模块。

### **2. 内核检测**

bootkit 通常会对 ntoskrnl 进行 patch，检测内核回调（Dreamboot）是否异常，或者对 PatchGuard 代码进行检测（关键 API KeInitAmd64SpecificState）。



## 引用
1. 《UEFI 原理与编程》
1. https://blog.csdn.net/leochen_lc/article/details/103541984
1. https://www.zhihu.com/question/36313402?sort=created
1. https://www.cnblogs.com/liuzhenbo/p/10825136.html
1. https://github.com/cursesun/UEFI-Bootkit
1. 《统一可扩展固件接口攻击方法研究》
1. 《efibios: EFI/UEFI BIOS 入门》


## 关于微步情报局

微步情报局，即微步在线研究响应团队，负责微步在线安全分析与安全服务业务，主要研究内容包括威胁情报自动化研发、高级 APT 组织&amp;黑产研究与追踪、恶意代码与自动化分析技术、重大事件应急响应等。
