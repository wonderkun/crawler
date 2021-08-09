> 原文链接: https://www.anquanke.com//post/id/249211 


# 从零开始的内核eBPF之旅（1）


                                阅读量   
                                **41426**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t0156ce4ffa5fd81122.png)](https://p4.ssl.qhimg.com/t0156ce4ffa5fd81122.png)



## 引言

内核研究与开发是计算机底层处于与硬件打交道的部位，ebpf可以理解为是内核开发的一个模块。在研究ebpf开发之前需要对计算机的一些基础知识学习了解，懂得计算机的基本组成和操作系统的基本原理和运行机制，了解Linux内核设计的机制和相关源码的阅读与理解，再深入内核模块观察ebpf的设计思路，进而做到对ebpf的开发与实现。

在此之前，首先需要储备一些基本的计算机知识。



## 基础知识储备

### **计算机组成原理**

学习计算机组成原理可以对计算机的基础架构有所理解，了解计算机中常见的术语和概念。

### **操作系统**

操作系统作为人和计算机交互的桥梁，理解其工作原理对后续内核开发有很好的帮助，对操作系统的术语了解知道其背后的道理是开发的基础。

### **C语言**

C语言是Linux内核开发主要使用的编程语言和开发工具，需要熟悉其基本语法和结构。



## Linux基础

了解Linux基本组成和常用的shell命令，熟悉Linux的文件架构。

### **FHS(Filesystem Hierarchy Standard):**

FHS依据文件系统使用的频繁与否与是否允许使用者随意更动， 而将目录定义成为四种交互作用的形态,用表格来说有点像底下这样：

[![](https://p0.ssl.qhimg.com/t01c0dfd180b9270c9e.jpg)](https://p0.ssl.qhimg.com/t01c0dfd180b9270c9e.jpg)

• 可分享的：可以分享给其他系统挂载使用的目录，所以包括执行文件与用户的邮件等数据，是能够分享给网络上其他主机挂载用的目录；

• 不可分享的：自己机器上面运作的装置文件或者是与程序有关的socket文件等， 由于仅与自身机器有关，所以当然就不适合分享给其他主机了。

• 不变的：有些数据是不会经常变动的,跟随着distribution而不变动。例如函式库、文件说明文件、系统管理员所管理的主机服务配置文件等等；

• 可变动的：经常改变的数据,例如登录文件、一般用户可自行收受的新闻组等。

事实上,FHS针对目录树架构仅定义出三层目录底下应该放置什么数据而已，分别是底下这三个目录的定义：

1. / (root, 根目录)：与开机系统有关；

2. /usr (unix software resource)：与软件安装/执行有关；

3. /var (variable)：与系统运作过程有关.

### 根目录 (/)的意义与内容：

### 概要:

4. 所有的目录都是由根目录衍生出来的(根目录是整个系统最重要的一个目录)

5. 与开机/还原/系统修复等动作有关。(由于系统开机时需要特定的开机软件、核心文件、开机所需程序、 函式库等等文件数据,若系统出现错误时，根目录也必须要包含有能够修复文件系统的程序才行)

6. FHS标准建议：根目录(/)所在分割槽应该越小越好，且应用程序所安装的软件最好不要与根目录放在同一个分割槽内，保持根目录越小越好。(因为越大的分割槽妳会放入越多的数据，如此一来根目录所在分割槽就可能会有较多发生错误的机会,如此不但效能较佳,根目录所在的文件系统也较不容易发生问题。)

### **根目录(/)底下目录FHS定义的说明：**

[![](https://p5.ssl.qhimg.com/t01c6dd64342d35a22d.png)](https://p5.ssl.qhimg.com/t01c6dd64342d35a22d.png)

[![](https://p2.ssl.qhimg.com/t0139cae68ea3086d5a.png)](https://p2.ssl.qhimg.com/t0139cae68ea3086d5a.png)

除上FHS中定义的目录说明外,底下是几个在Linux当中非常重要的目录：

[![](https://p5.ssl.qhimg.com/t012fca0e2fbdbc9a1e.png)](https://p5.ssl.qhimg.com/t012fca0e2fbdbc9a1e.png)

不可与根目录分开的目录(与开机过程有关)：

根目录与开机有关，**开机过程中仅有根目录会被挂载**，其他分割槽则是在开机完成之后才会持续的进行挂载的行为。就是因为如此，因此根目录下与开机过程有关的目录，就不能够与根目录放到不同的分割槽去！

• /etc：配置文件

• /bin：重要执行档

• /dev：所需要的装置文件

• /lib：执行档所需的函式库与核心所需的模块

• /sbin：重要的系统执行文件

### **/usr的意义与内容：**

### **概要:**

7. 依据FHS的基本定义，/usr里面放置的数据属于可分享的与不可变动的(shareable, static)，如果你知道如何透过网络进行分割槽的挂载，那么/usr确实可以分享给局域网络内的其他主机来使用！

8. usr(Unix Software Resource即Unix操作系统软件资源) FHS建议所有软件开发者,应该将他们的数据合理的分别放置到这个目录下的次目录，而不要自行建立该软件自己独立的目录。

9. 所有系统默认的软件(distribution发布者提供的软件)都会放置到/usr底下，因此这个目录有点类似Windows系统的『C:\Windows\ + C:\Program files\』这两个目录的综合体，系统刚安装完毕时,这个目录会占用最多的硬盘容量。

一般来说,/usr的次目录建议有底下这些：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018a284d353c8d114a.png)

### **/var的意义与内容：**

### **概要:**

/var目录主要针对常态性变动的文件，包括缓存(cache)、登录档(log file)以及某些软件运作所产生的文件，包括程序文件(lock file, run file)，或者例如MySQL数据库的文件等等。所以/var在系统运作后才会渐渐占用硬盘容量的目录

常见的次目录有：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0151defd32cfed6c11.png)

针对FHS，各家distributions的异同:

由于FHS仅是定义出最上层(/)及次层(/usr, /var)的目录内容应该要放置的文件或目录数据,，因此，在其他次目录层级内，就可以随开发者自行来配置了。举例来说,CentOS的网络设定数据放在/etc/sysconfig/network-scripts/目录下，但是SuSE则是将网络放置在/etc/sysconfig/network/目录下，目录名称可是不同的呢！不过只要记住大致的FHS标准，差异性其实有限啦！

### **Linux 命令大全查询表**

[![](https://p5.ssl.qhimg.com/t01b1802d90ed9590fa.png)](https://p5.ssl.qhimg.com/t01b1802d90ed9590fa.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01413e56ff2ed37bca.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011241d25227db566f.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013b4d6b4677783305.png)

[![](https://p5.ssl.qhimg.com/t01e0351a234e6a5e2d.png)](https://p5.ssl.qhimg.com/t01e0351a234e6a5e2d.png)



## Linux内核

### **Linux内核学习策略**

Linux学习建议配套远古版本的Linux内核源码学习，有助于帮助理解内核设计的思路，下载并阅读Linux内核1.0版本的源码去学习，该版本基本包含了内核基本部件，后续的版本都是在此基础上扩充功能，但是基本的内在没有变化。

内核源码不同版本间的阅读与对比可参考Bootlin，其中1.0源码目录结构如下，其中对主要文件目录进行解释：

[![](https://p2.ssl.qhimg.com/t01efad6d5174cbc8c9.png)](https://p2.ssl.qhimg.com/t01efad6d5174cbc8c9.png)

对照着内核设计的源代码进行学习，会从根源上思考这样设计的目的是什么。

### **Linux内核开发环境配置**

内核开发环境和源码安装配置：Linux内核开发环境配置

### **Linux内核简介**

### **Linux 内核的用途是什么？**

Linux 内核有 4 项工作：

10. 内存管理：追踪记录有多少内存存储了什么以及存储在哪里

11. 进程管理：确定哪些进程可以使用中央处理器（CPU）、何时使用以及持续多长时间

12. 设备驱动程序：充当硬件与进程之间的调解程序/解释程序

13. 系统调用和安全防护：从流程接受服务请求

在正确实施的情况下，内核对于用户是不可见的，它在自己的小世界（称为内核空间）中工作，并从中分配内存和跟踪所有内容的存储位置。用户所看到的内容（例如 Web 浏览器和文件）则被称为用户空间。这些应用通过系统调用接口（SCI）与内核进行交互。

举例来说，内核就像是一个为高管（硬件）服务的忙碌的个人助理。助理的工作就是将员工和公众（用户）的消息和请求（进程）转交给高管，记住存放的内容和位置（内存），并确定在任何特定的时间谁可以拜访高管、会面时间有多长。

### **Linux内核学习路线和框架图**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01daf66eed34f998e9.jpg)

### **Linux Security Coachin**

[![](https://p5.ssl.qhimg.com/t01cdfe4f12b75362f5.jpg)](https://p5.ssl.qhimg.com/t01cdfe4f12b75362f5.jpg)

### **Linux内核基础学习资料**

Linux内核与系统驱动保护入口

该视频资料详细介绍了Linux内核的知识点及其在内核中的实现进行比对，很有参考价值。

### **MakeFile详解**

Makefile 可以简单的认为是一个工程文件的编译规则，描述了整个工程的编译和链接等规则。详细介绍如下：

MakeFile详解

Makefile文件负责编写程序的编译与运行规则，免去命令行使用Clang去逐步编译分析。

### **GDB详解**

GDB是一个强大的调试工具，通过它可以实现C程序代码bug的调试。

GDB详解

### **Linux崩溃调试**

Linux内核Crash下的问题解决方案：

Linux调试之崩溃

### EBPF基础

### **什么是ebpf？**

Linux 内核一直是实现监控/可观测性、网络和安全功能的理想地方。不过很多情况下这并非易事，因为这些工作需要修改内核源码或加载内核模块， 最终实现形式是在已有的层层抽象之上叠加新的抽象。

eBPF 是一项革命性技术，它能在内核中运行沙箱程序（sandbox programs）， 而无需修改内核源码或者加载内核模块。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d638b2dc4889047b.jpg)

eBPF 催生了一种全新的软件开发方式。基于这种方式，我们不仅能对内核行为进行 编程，甚至还能编写跨多个子系统的处理逻辑，而传统上这些子系统是完全独立、 无法用一套逻辑来处理的。

### **安全：**

观测和理解所有的系统调用的能力，以及在 packet 层和 socket 层审视所有的网络操作的能力， 这两者相结合，为系统安全提供了革命性的新方法。以前，系统调用过滤、网络层过滤和进程上下文跟踪是在完全独立的系统中完成的；eBPF 的出现统一了可观测性和各层面的控制能力，使我们有更加丰富的上下文和更精细的控制能力， 因而能创建更加安全的系统。

### **网络：**

eBPF 的两大特色 —— 可编程和高性能 —— 使它能满足所有的网络包处理需求。可编程意味着无需离开内核中的包处理上下文，就能添加额外的协议解析器或任何转发逻辑， 以满足不断变化的需求。高性能的 JIT 编译器使 eBPF 程序能达到几乎与原生编译的内核态代码一样的执行性能。

跟踪 &amp; 性能分析：

eBPF 程序能够加载到 trace points、内核及用户空间应用程序中的 probe points， 这种能力使我们对应用程序的运行时行为（runtime behavior）和系统本身 （system itself）提供了史无前例的可观测性。应用端和系统端的这种观测能力相结合， 能在排查系统性能问题时提供强大的能力和独特的信息。BPF 使用了很多高级数据结构， 因此能非常高效地导出有意义的可观测数据，而不是像很多同类系统一样导出海量的原始采样数据。

### **观测 &amp; 监控：**

相比于操作系统提供的静态计数器（counters、gauges），eBPF 能在内核中收集和聚合自定义 metric， 并能从不同数据源来生成可观测数据。这既扩展了可观测性的深度，也显著减少了整体系统开销， 因为现在可以选择只收集需要的数据，并且后者是直方图或类似的格式，而非原始采样数据。

### **Linux驱动模块开发**

### **简介**

Linux 内核的整体结构已经非常庞大,而其包含的组件也非常多。这会导致两个问题,一是生成的内核会很大,二是如果我们要在现有的内核中新增或删除功能,将不得不重新编译内核。Linux 提供了这样的一种机制,这种机制被称为模块(Module)。使得编译出的内核本身并不需要包含所有功能,而在这些功能需要被使用的时候,其对应的代码被动态地加载到内核中。

### **举例**

先来看一个最简单的内核模块“Hello World”，代码如下：

```
#include &lt;linux/init.h&gt;
#include &lt;linux/module.h&gt;
static int hello_init(void) /初始化函数/
`{`
printk(KERN_INFO " Hello World enter\n");
return 0;
`}`
static void hello_exit(void) /卸载函数/
`{`
printk(KERN_INFO " Hello World exit\n ");
`}`
module_init(hello_init); /模块初始化/
module_exit(hello_exit); /卸载模块/
MODULE_LICENSE("Dual BSD/GPL"); /许可声明/
MODULE_AUTHOR("Linux");
MODULE_DESCRIPTION("A simple Hello World Module");
MODULE_ALIAS("a simplest module");
```

这个模块定义了两个函数, 一个在模块加载到内核时被调用( hello_init )以及一个在模块被去除时被调用( hello_exit ). moudle_init 和 module_exit 这几行使用了特别的内核宏来指出这两个函数的角色. 另一个特别的宏 (MODULE_LICENSE) 是用来告知内核, 该模块带有一个自由的许可证.

注：内核模块中用于输出的函数是内核空间的 printk()而非用户空间的 printf()，具体用法参考附件 printk函数介绍。

### **几个常用命令**

### **加载模块**

通过“insmod ./hello.ko”命令可以加载，加载时输出“Hello World enter”。

### **卸载模块**

通过“rmmod hello”命令可以卸载，卸载时输出“Hello World exit”。

### **查看系统中已经加载的模块列表**

在Linux中，使用lsmod命令可以获得系统中加载了的所有模块以及模块间的依赖关系，例如：

```
root@imx6:~$ lsmod
Module Size Used by
hello 1568 0
ohci1394 32716 0
ide_scsi 16708 0
ide_cd 39392 0
cdrom 36960 1 ide_cd
```

### **查看某个具体模块的详细信息**

使用modinfo &lt;模块名&gt;命令可以获得模块的信息,包括模块作者、模块的说明、模块所支持 的参数以及 vermagic:

```
root@imx6:~$ modinfo hello.ko
filename: hello.ko
license: Dual BSD/GPL
author: Song Baohua
description: A simple Hello World Module
alias: a simplest module
vermagic: 2.6.15.5 686 gcc-3.2
depends:
```

### **Linux 内核模块程序的结构**

一个Linux内核模块主要由如下几个部分组成：

1、模块加载函数（一般需要） 当通过insmod或modprobe命令加载内核模块时，模块的加载函数会自动被内核执行，完成本模块的相关初始化工作。

2、模块卸载函数（一般需要） 当通过rmmod命令卸载某模块时，模块的卸载函数会自动被内核执行，完成与模块卸载函数相反的功能。

3、模块许可证声明（必须） 许可证（LICENSE）声明描述内核模块的许可权限，如果不声明LICENSE，模块被加载时，将收到内核被污染 （kernel tainted）的警告。在Linux 2.6内核中，可接受的LICENSE包括“GPL”、“GPL v2”、“GPL and additional rights”、“Dual BSD/GPL”、“Dual MPL/GPL”和“Proprietary”。大多数情况下，内核模块应遵循GPL兼容许可权。Linux 2.6内核模块最常见的是以

MODULE_LICENSE( “Dual BSD/GPL” )语句声明模块采BSD/GPL双LICENSE。

4、模块参数（可选）模块参数是模块被加载的时候可以被传递给它的值，它本身对应模块内部的全局变量。

5、模块导出符号（可选）内核模块可以导出符号（symbol，对应于函数或变量），这样其它模块可以使用本模块中的变量或函数。

6、模块作者等信息声明（可选）用于申明模块作者的相关信息，一般用于备注作者姓名、邮箱等。

### **模块加载函数**

Linux 内核模块加载函数一般以_ _init 标识声明,典型的模块加载函数如下：

```
static int _ _init initialization_function(void)
`{`
/* 初始化代码 */
`}`
module_init(initialization_function);
```

模块加载函数必须以“module_init(函数名)”的形式被指定。它返回整型值,若初始化成功,应返回 0。而在初始化失败时,应该返回错误编码。在 Linux 内核里,错误编码是一个负值。

在 Linux 2.6 内核中,可以使用 request_module(const char *fmt, …)函数加载内核模块,驱动开发人员可以通过调用。

```
request_module(module_name);
/**** 或者 ****/
request_module("char-major-%d-%d", MAJOR(dev), MINOR(dev));
```

注意：在 Linux 中,所有标识为_ init 的函数在连接的时候都放在.init.text 这个区段内,此外,所有的 init 函数在区段.initcall.init 中还保存了一份函数指针,在初始化时内核会通过这些函数指针调用这些 _init 函数,并在初始化完成后,释放 init 区段(包括.init.text、.initcall.init 等)。

### **模块卸载函数**

```
static void _ _exit cleanup_function(void)
`{`
/* 释放代码 */
`}`
module_exit(cleanup_function);
```

模块卸载函数在模块卸载的时候执行,不返回任何值,必须以“module_exit(函数名)”的形式来指定。通常来说,模块卸载函数要完成与模块加载函数相反的功能,如下所示。

若模块加载函数注册了 XXX,则模块卸载函数应该注销 XXX。

若模块加载函数动态申请了内存,则模块卸载函数应释放该内存。

若模块加载函数申请了硬件资源(中断、DMA 通道、I/O 端口和 I/O 内存等)的占用,则模块卸载函数应释放这些硬件资源。

若模块加载函数开启了硬件,则卸载函数中一般要关闭之。

### **模块参数**

用“module_param(参数名,参数类型,参数读/写权限)”为模块定义一个参数,例如下列代码定义了 1 个整型参数和 1 个字符指针参数:

```
static char *book_name = " dissecting Linux Device Driver ";
static int num = 4 000;
module_param(num, int, S_IRUGO);
module_param(book_name, charp, S_IRUGO);
```

参数类型可以是 byte、short、ushort、int、uint、long、ulong、charp(字符指针)、bool 或 invbool(布尔的反)，在模块被编译时会将 module_param 中声明的类型与变量定义的类型进行比较，判断是否一致。

在装载内核模块时，用户可以向模块传递参数，形式为“insmode(或 modprobe)模块名 参数名=参数值”，如果不传递，参数将使用模块内定义的缺省值。

### **内核模块的符号导出**

模块可以使用如下宏导出符号到内核符号表：

导出的符号将可以被其他模块使用，使用前声明一下即可。EXPORT_SYMBOL_GPL()只适用于包含 GPL 许可权的模块。

### **模块声明与描述**

在Linux内核模块中，我们可以用MODULE_AUTHOR、MODULE_DESCRIPTION、MODULE_VERSION、MODULE_DEVICE_TABLE、MODULE_ALIAS分别声明模块的作者、描述、版本、设备表和别名，

例如：

```
MODULE_AUTHOR(author);
MODULE_DESCRIPTION(description);
MODULE_VERSION(version_string);
MODULE_DEVICE_TABLE(table_info);
MODULE_ALIAS(alternate_name);
```

对于USB、PCI等设备驱动，通常会创建一个MODULE_DEVICE_TABLE。

### **MakeFile**

### **Kernel modules**

```
obj-m += hello.o
```

### **Specify flags for the module compilation.**

```
#EXTRA_CFLAGS=-g -O0
build: kernel_modules
kernel_modules:
make -C /lib/modules/$(KVERS)/build M=$(CURDIR) modules #modules表示编译成模块的意思
#CURDIR是make的内嵌变量，自动设置为当前目录
clean:
make -C /lib/modules/$(KVERS)/build M=$(CURDIR) clean
```

注：uname 的更多用法详见附件

如果一个模块包括多个.c 文件(如 file1.c、file2.c),则应该以如下方式编写 Makefile：

```
obj-m := modulename.o
modulename-objs := file1.o file2.o
```

obj-m是个makefile变量，它的值可以是一串.o文件的表列



## EBPF详解（未完待续）

本篇主要叙述了ebpf的学习过程，后面我们还将继续分享ebpf详细学习笔记和记录。
