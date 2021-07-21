> 原文链接: https://www.anquanke.com//post/id/224001 


# Virtio：一种Linux I/O虚拟化框架


                                阅读量   
                                **183970**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ibm，文章来源：developer.ibm.com
                                <br>原文地址：[https://developer.ibm.com/articles/l-virtio/](https://developer.ibm.com/articles/l-virtio/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01c3d23f37f50805d1.jpg)](https://p1.ssl.qhimg.com/t01c3d23f37f50805d1.jpg)

> 当前QEMU的PWN题目和安全研究比较热门，且其中安全问题多出在设备模拟方面，不可以避免的需要学习设备半虚拟化框架Virtio。学习Virtio推荐先看这一篇，国内许多文章写的有点乱了，看来看去不能明白整体的架构，给人很模糊的感觉。这篇文章从整体上概括了Virtio框架，可以更好地理解。
**受限于个人水平，翻译肯定有不妥之处，译注根据自己的理解加入，也不一定准确。如有错误，还请不吝指出。**

简言之，`virtio`是设备和半虚拟化管理程序(paravirtualized hypervisor)之间的一个抽象层。`virtio`是Rusty Russell为了支持他自己的虚拟化方案`lguest`而开发的。这篇文章以对半虚拟化和设备仿真的介绍开始，然后探寻`virtio`中的一些细节。采用kernel 2.6.30版本的`virtio`框架进行讲解。

Linux是hypervisor的“游乐场”。正如我在文章[使用Linux作为hypervisor](https://developer.ibm.com/tutorials/l-hypervisor/)中所展现的，Linux提供了许多具有不同特性和优势的虚拟化解决方案。例如KVM(Kernel-based Virtual Machine)，`lguest`、和用户态的Linux。在Linux使用这些虚拟化解决方案给操作系统造成了重担，因为它们各自都有独立的需求。其中一个问题就是设备的虚拟化。`virtio`为各种各样设备（如：网络设备、块设备等等）的虚拟提供了通用的标准化前端接口，增加了各个虚拟化平台的代码复用。而不是各自为政般的使用繁杂的设备虚拟机制。



## 全虚拟化 vs. 半虚拟化

我们先来讨论两种完全不同的虚拟化方案：全虚拟化和半虚拟化。在全虚拟化中，客户操作系统在hypervisor上运行，相当于运行于裸机一般。客户机不知道它在虚拟机还是物理机中运行，不需要修改操作系统就可以直接运行。与此相反的是，在半虚拟化中，客户机操作系统不仅能够知道其运行于虚拟机之上，也必须包含与hypervisor进行交互的代码。但是能够在客户机和hypervisor的切换中，带来更高的效率（图1）。

**译注：客户机与hypervisor的切换举例：客户机请求I/O，需要hypervisor中所虚拟的设备来响应请求，此时就会发生切换。**

在全虚拟化中，hypervisor必须仿真设备硬件，也就是说模仿硬件最底层的会话（如：网卡驱动）。尽管这种仿真看起来方便，但代价是极低的效率和高度的复杂性。在半虚拟化中，客户机与hypervisor可以共同合作让这种仿真具有更高的效率。半虚拟化不足就是客户机操作系统会意识到它运行于虚拟机之中，而且需要对客户机操作系统做出一定的修改。

**图1. 全虚拟化和半虚拟化中的设备仿真**

[![](https://p2.ssl.qhimg.com/t01145a2011cccff117.jpg)](https://p2.ssl.qhimg.com/t01145a2011cccff117.jpg)

硬件也随着虚拟化不断地发展着。新处理器加入了高级指令，使客户机操作系统和hypervisor的切换更加高效。硬件也随着I/O虚拟化不断地发生改变（参照Resource了解PCI passthrough和单/多根I/O虚拟化）。

在传统的全虚拟化环境中，hypervisor必须陷入(trap)请求，然后模仿真实硬件的行为。尽管这样提供了很大的灵活性（指可以运行不必修改的操作系统），但却造成了低效率（图1左侧）。图1右侧展示了半虚拟化。客户机操作系统知道运行于虚拟机之中，加入了驱动作为前端。hypervisor为特定设备仿真实现了后端驱动。这里的前端后端就是`virtio`的构件，提供了标准化接口，提高了设备仿真开发的代码复用程度和仿真设备运行的效率。

**作者注：`virtio`并不是半虚拟化领域的唯一存在。Xen提供了半虚拟化的设备驱动，VMware也提供了名为`Guest Tools`的半虚拟化支持。**



## Linux客户机中的一种抽象

如前节所述，`virtio`为半虚拟化提供了一系列通用设备仿真的接口。这种设计允许hypervisor导出一套通用的设备仿真操作，只要使用这一套接口就能够工作。图2解释了为什么这很重要。通过半虚拟化，客户机实现了通用的接口，同时虚拟化管理程序提供设备仿真的后端驱动。后端驱动并不一定要一致，只要它实现了前端所需的各种操作就可以。

**图2. 使用virtio的驱动抽象**

[![](https://p1.ssl.qhimg.com/t018bf55ec258153dc2.jpg)](https://p1.ssl.qhimg.com/t018bf55ec258153dc2.jpg)

注意在实际中，使用用户空间的QEMU程序来进行设备仿真，所以后端驱动通过QEMU的I/O来与用户空间的hypervisor通信。QEMU是系统模拟器，包括提供客户机操作系统虚拟化平台，提供整个系统的仿真（PCI host controller, disk, network, video hardware, USB controller等）。

`virtio`依靠于简单的缓存管理，用来存储客户机的命令与客户机所需的数据。我们继续来看`virtio`的API及其构件。



## Virtio 架构

除了前端驱动（在客户机操作系统中实现）和后端驱动（在hypervisor中实现）之外，`virtio`还定义了两层来支持客户机与hypervisor进行通讯。虚拟队列(Virtual Queue)接口将前端驱动和后端驱动结合在一起。驱动可以有0个或多个队列，依赖于它们的需要。例如，`virtio`网络驱动使用了两个虚拟队列（一个用于接收一个用于发送），而`virtio`块设备驱动只需要一个。虚拟队列，通常使用环形缓冲，在客户机与虚拟机管理器之间传输。可以使用任意方式实现，只要客户机与虚拟机管理器相统一。

**图3. virtio框架的架构**

[![](https://p4.ssl.qhimg.com/t0129a029bd2c9e39bd.jpg)](https://p4.ssl.qhimg.com/t0129a029bd2c9e39bd.jpg)

如图3，包含了五种前端驱动：块设备（如硬盘）、网络设备、PCI仿真、balloon驱动（用于动态的管理客户机内存使用）和一个终端驱动。每一个前端驱动，在hypervisor中都有一个相匹配的后端驱动。



## 概念层级

在客户机的视角来看，对象层级如图4所示。顶端是`virtio_driver`，表示客户机中的前端驱动。与驱动相匹配的设备被封装在`virtio_device`（在客户机中表示设备），其中有成员`config`指向`virtio_config_ops`结构（其中定义了配置`virtio`设备的操作）。`virtqueue`中有成员`vdev`指向`virtio_device`（也就是指向它所服务的某一设备`virtio_device`）。最下面，每个`virtio_queue`中有个类型为`virtqueue_ops`的对象，其中定义了与hypervisor交互的虚拟队列操作。

**图4. virtio前端的对象层级**

[![](https://p3.ssl.qhimg.com/t01149bdbb4a8a3118d.jpg)](https://p3.ssl.qhimg.com/t01149bdbb4a8a3118d.jpg)

这一过程起始于`virtio_driver`的创建和后续的使用`register_virtio_driver`将驱动进行注册。`virtio_driver`结构定义了设备驱动的上层结构，包含了它所支持的设备的设备ID，特性表（根据设备的类型有所不同），和一系列回调函数。当hypervisor发现新设备，并且匹配到了设备ID，就会以`virtio_device`为参数调用`probe`函数（于`virtio_driver`中提供）。这一结构与管理数据一起被缓存（以独立于驱动的方式）。根据设备的类型，`virtio_config_ops`中的可能会被调用，以获取或设置设备相关的选项（例如，获取硬盘块设备的读/写状态或者设置块设备的块大小）。

注意，`virtio_device`中没有包含指向所对应`virtqueue`的成员（`virtqueue`有指向`virtio_device`的成员）。为了得到与`virtio_device`相关联的`virtqueue`，需要使用`virtio_config_ops`结构中的`find_vq`函数。这个函数返回与该`virtqueue`相关联的设备实例。`find_vq`还允许为`virtqueue`指定回调函数，用于在hypervisor准备好数据时，通知客户机。

`virtqueue`结构包含可选的回调函数（用于在hypervisor填充缓冲后，通知客户机）、一个指向`virtio_device`、一个指向`virtqueue`操作和一个特别的`priv`用于底层实现使用。`callback`是可选的，也可以动态的启用或禁用。

这个层级的核心是`virtqueue_ops`，其中定义了如何在客户机和hypervisor之间传输命令与数据。我们先来探索`virtqueue`中对象的添加和删除操作。



## Virtio缓冲

客户机驱动（前端）与hypervisor（后端）通过缓冲区进行通信。对于一次I/O，客户机提供一个或多个缓冲区表示请求。例如，你可以使用三个缓冲区，其中一个用来存储读请求，其他两个用来存储回复数据。内部这个配置被表示为分散/聚集(scatter-gather)列表（列表中的每个元素存储有缓冲区地址与长度）。



## 核心API

将客户机驱动与hypervisor驱动链接起来，偶尔是通过`virtio_device`，大多数情况下都是通过`virtqueue`。`virtqueue`支持五个API函数。使用第一个函数`add_buf`向hypervisor添加请求，这种请求以分散/聚集列表的形式，正如先前讨论的。为了提交请求，客户机必须提供请求命令，分散/聚集列表（以缓冲区地址和长度为元素的数组），向外提供请求的缓冲区的数量（也就是发送请求信息给hypervisor），向内传递数据的缓冲区的数量（hypervisor用来填充数据，返回给客户机）。当客户机通过`add_buf`向hypervisor提交一条请求后，客户机就可以使用`kick`通知hypervisor新请求已递送。但为了更好地性能，客户机应该在`kick`通知hypervisor之前，提交尽可能多的请求。

客户机使用`get_buf`接收从hypervisor中返回的数据。客户机可以简单地使用`get_buf`轮询或者等待由`virtqueue callback`函数的通知。当客户机知道了缓冲区数据可用，就会使用`get_buf`获取数据。

最后两个`virtqueue`的API是`enable_cb`和`disable_cb`，可用使用这两个函数启用和禁用回调函数（`callback`函数使用`find_vq`初始化设置）。注意回调函数与hypervisor在不同的地址空间，所以调用需要间接调用(indirect hypervisor call)（例如：`kvm_hypercall`）。

缓冲区的格式、顺序与内容支队前端和后端驱动有意义。内部传送（现在使用环形缓冲区实现）只传输缓冲区，并不知道内部表达的意义。



## Virtio驱动例子

对于各种各样前端驱动，可以在Linux内核源码的`./drivers`子目录下找到。`virtio`网络驱动在`./driver/net/virtio_net.c`，`virtio`块驱动在`./driver/block/virtio_blk.c`。`./driver/virtio`子目录下提供了`virtio`接口的实现(`virtio`设备、驱动、`virtqueue`和环形缓冲区)。`virtio`也被用在了高性能计算(High-Performance Computing, HPC)研究之中，使用共享内存传递内部虚拟机的信息。特别的，这使用了`virtio`来实现虚拟化PCI接口。可以再resources中找到相关工作。

你可以在Linux内核中练习半虚拟化基础工作。你所需要的就是一个作为hypervisor的内核，客户机内核和用来仿真设备的QEMU。你可以使用KVM(一个存在于宿主机内核中的模块)或者Rusty Russell的lguest（一个修改过的Linux内核）。两种方案都支持`virtio`（配合以QEMU进行系统模拟和`libvirt`进行虚拟化管理）。

Rusty的成果是简化了半虚拟化驱动的开发，并且设备仿真性能更高。最重要的还是，`virtio`能够提供更好地性能（两三倍的网络I/O）比现有的商业解决方案。虽说有一定的代价，但如果你的hypervisor和客户机系统是Linux，还是非常值得的。



## 进一步

尽管你可以永远不会为`virtio`开发前端或者后端驱动，但它实现了一个有趣的架构，值得更加细致的理解它。与先前的Xen相比，`virtio`为了半虚拟化提高性能提供了新的可能。在作为投入使用的hypervisor和新虚拟技术的实验平台中，Linux不断地证明了它自己。`virtio`再一次证明了Linux作为hypervisor的优势和开放性。



## Resources
1. [Virtio: towards a de factor standard for virtual I/O devices](http://portal.acm.org/citation.cfm?id=1400097.1400108)
1. [Anatomy of a Linux hypervisor](https://www.ibm.com/developerworks/linux/library/l-hypervisor/index.html)
1. [Linux virtualization and PCI passthrough](http://www.ibm.com/developerworks/linux/library/l-pci-passthrough/index.html)
1. [performance advantage of virtio using KVM](http://blog.loftninjas.org/2008/10/22/kvm-virtio-network-performance/)
1. [libvirt wiki](http://wiki.libvirt.org/page/Virtio)
1. [lguest](http://lguest.ozlabs.org/)
1. [KVM](http://www.linux-kvm.org/page/Main_Page)
1. [shared-memory message passing](http://www.springerlink.com/content/b1676363881h5662/)