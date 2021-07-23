> 原文链接: https://www.anquanke.com//post/id/228595 


# 三星手机内核防护技术RKP深度剖析（二）


                                阅读量   
                                **191035**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者longterm，文章来源：longterm.io
                                <br>原文地址：[https://blog.longterm.io/samsung_rkp.html](https://blog.longterm.io/samsung_rkp.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01cfc8691d635a4be5.png)](https://p5.ssl.qhimg.com/t01cfc8691d635a4be5.png)



在本系列文章中，我们将为读者深入讲解三星手机的内核防护技术。在上一篇文章中，我们为读者介绍了内核漏洞的利用流程，三星手机内建的三种防御机制，并简要介绍了管理程序，在本文中，将继续为读者呈现更多精彩内容！



**（接上文）**

## 我们的研究平台

为了更轻松地开展这项研究，我们将使用一个引导加载器来解锁三星A51（SM-A515F），而不是一个完整的漏洞利用链。我们已经在三星开源网站上下载了我们设备的内核源代码，对其进行了修改并已经重新编译。

此外，为了开展这项研究，我们还实现了一些新的系统调用，以完成下列操作：内核内存的分配/释放；内核内存的任意读写；管理程序调用（借助于uh_call函数）。

这些系统调用使得与RKP的交互变得更加方便，这一点可以从后文中看到：我们只需要编写一段在用户空间中运行的C代码（或Python代码），就能随心所欲地执行我们想要的任何操作。



## 提取二进制文件

RKP已经在Exynos和Snapdragon设备上得到了相应的实现，并且这两种实现都涉及大量代码。然而，大多数（如果不是全部的话）现有的研究都是针对Exynos变体进行的，因为它是最容易入手的：RKP可以作为一个独立的二进制文件使用。在Snapdragon设备上，它则被嵌入到Qualcomm Hypervisor Execution Environment（QHEE）映像中，并且该映像非常庞大和复杂。 

### 在Exynos设备上提取二进制文件

在Exynos设备上，RKP曾经被直接嵌入到内核二进制文件中，因此可以在内核源码中找到vmm.elf文件。大约在2017年底/2018年初，vmm被重写成了一个名为uH的新框架，它很可能是“micro-hypervisor”的意思。因此，该二进制文件已经改名为uh.elf，并且仍然可以在少数设备的内核源码中找到。

根据Gal Beniamin提出的第一项设计改进建议，在大多数设备上，RKP已经被从内核二进制文件中移出，并被移到了一个名为uh.elf的分区中。这使得它更容易提取，例如从固件更新中包含的BL_xxx.tar压缩文件中提取（它通常是使用LZ4进行压缩的，并且以一个0x1000字节的头部开始，因此，我们需要将其剥离才能得到真正的ELF文件）。

在S20及更高版本的设备上，架构则略有变化，因为三星引入了另一个框架来支持RKP（称为H-Arx），之所以这样，做很有可能是为了与Snapdragon设备的代码库更加统一，而且它还提供了更多的uH“应用程序”。不过，这里并不打算对其进行介绍。 

### 在Snapdragon设备商提取二进制文件

在Snapdragon设备上，RKP不仅可以从hy分区中找到，也可以从固件更新的BL_xxx.tar压缩文件中提取。它是构成QHEE映像的区段（segments）之一。

与Exynos设备的主要区别在于，设置页表和异常向量的是QHEE。因此，在发生异常（HVC或陷阱系统寄存器）时，QHEE会通知uH；而uH在想要修改页表时，必须调用QHEE。其余代码几乎完全相同。



## 符号/日志字符串

早在2017年，RKP二进制文件还会提供相关的符号和日志字符串。但现在，已经不再提供了。如今，二进制文件进行了剥离处理，日志字符串也被替换为占位符（像高通一样）。尽管如此，我们还是要设法争取尽可能多的二进制文件，希望三星不会像其他OEM厂商那样，对所有的设备都这样做。

通过大量下载各种Exynos设备的固件更新，我们收集了大约300个独特的管理程序二进制文件。但是，这些uh.elf文件都没有提供相关的符号，所以我们不得不通过手动方式从早先的vmm.elf文件中移植过来。不过，一些uh.elf文件倒是提供了完整的日志字符串，最近的一个文件的生成日期是2019年4月9日。

借助于完整的日志字符串及其哈希值版本，我们发现其哈希值只是SHA256输出的截断值。下面是一个Python单行程序，可以用来计算哈希值： 

```
hashlib.sha256(log_string).hexdigest()[:8]
```



## 管理程序框架

uH框架相当于一个微型操作系统，而RKP就像是一个应用程序。这实际上更像是一种组织事物的方式，因为“应用程序”只是一堆命令处理程序，没有任何形式的隔离措施。



## 公用结构体

在深入研究代码之前，我们将先简要介绍uH和RKP应用程序广泛使用的公用结构体。当然，我们不会详细介绍它们的具体实现，但了解它们的作用也是必不可少的。

### 结构体memlist

结构体memlist_t的定义如下所示（这些名字是我们自己起的）： 

```
typedef struct memlist `{`

memlist_entry_t *base;

uint32_t capacity;

uint32_t count;

uint32_t merged;

crit_sec_t cs;

`}` memlist_t;
```

它实际上就是一个地址范围构成的列表，是C++向量的一种特殊版本（它具有一定的容量和大小）。

其中，memlist类型的表项的定义如下所示： 

```
typedef struct memlist_entry `{`

uint64_t addr;

uint64_t size;

uint64_t field_10;

uint64_t extra;

`}` memlist_entry_t;
```

此外，还有一些公用函数，可以用于为memlist添加和删除地址范围，检查某地址是否包含在memlist中，或者某地址范围是否与memlist重叠等。

### 结构体sparsemap

结构体sparsemap_t的定义如下所示（名字是我们自己起的）： 

```
typedef struct sparsemap `{`

char name[8];

uint64_t start_addr;

uint64_t end_addr;

uint64_t count;

uint64_t bit_per_page;

uint64_t mask;

crit_sec_t cs;

memlist_t *list;

sparsemap_entry_t *entries;

uint32_t private;

uint32_t field_54;

`}` sparsemap_t;
```

实际上，sparsemap就是一个将值与地址相关联的映射，它是利用memlist创建的，并将这个memlist中的所有地址映射到一个值。这个值的大小由bit_per_page字段决定。

下面是sparsemap类型表项的定义： 

```
typedef struct sparsemap_entry `{`

uint64_t addr;

uint64_t size;

uint64_t bitmap_size;

uint8_t* bitmap;

`}` sparsemap_entry_t;
```

实际上，有些函数是专门用于获取和设置每个映射条目的值，以及完成其他功能的函数。

### 结构体crit_sec

结构体crit_sec_t用于实现关键区段（这些名字是我们自己起的）： 

```
typedef struct crit_sec `{`

uint32_t cpu;

uint32_t lock;

uint64_t lr;

`}` crit_sec_t;
```

当然，也存在用于进入和退出关键区段的相关函数。



## 小结

在本系列文章中，我们将为读者深入讲解三星手机的内核防护技术。在本文中，我们为读者介绍了本研究所使用的平台，如何在两种平台上面提取二进制文件，如何获取相关的符号/日志字符串，简要介绍了管理程序的框架，最后，详细说明了三种公用的结构体。在后续的文章中，会有更多精彩内容呈现给大家，敬请期待！

**（未完待续）**
