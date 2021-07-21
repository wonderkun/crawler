> 原文链接: https://www.anquanke.com//post/id/178627 


# HITB议题解读 | Binder: The Bridge to Root


                                阅读量   
                                **247842**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t018023170b9af68cfe.jpg)](https://p1.ssl.qhimg.com/t018023170b9af68cfe.jpg)



## 议题概要：

Binder驱动是Android系统进程间通信的枢纽，可被包括运行在沙箱中的进程访问，是Android系统的灵魂驱动之一。去年，我们对Binder驱动进行了安全研究，并发现了多个问题。令人惊奇的是，其中的部分漏洞威力惊人，如2019年3月Android安全公告公开的CVE-2019-2025，我们将它命名为“水滴”漏洞。

“水滴”漏洞有以下三个典型的特点：
- 能够用于做出通用的ROOT方案
- 任意地址读写
- 可能用于沙箱逃逸
这个漏洞影响了近两年来绝大多数Android设备，对应的Linux内核版本为3.18~4.20。这个漏洞可用于攻击Android Pie及Android Oreo等。目前国内外的主流安卓厂商基本都会受到影响。本议题中我们将会介绍我们是如何利用“水滴”漏洞来ROOT最新的Pixel 3Xl。就目前所知，这也是Pixel 3Xl在全球范围内首次被公开ROOT。



## 作者简介：

韩洪立是奇虎360 C0RE Team的一名安全研究员，他专注于安卓操作系统以及Linux内核的安全研究。在过去的几年里，他向谷歌、高通、英伟达、华为等厂商上报了数十个致命/高危漏洞，并得到了公开的致谢。

周明建是奇虎360 C0RE Team的负责人。他主要专注于移动安全漏洞挖掘、系统攻防等领域，带领C0RE Team多次发现安卓0Day通杀漏洞，并率先做出漏洞利用。2017年C0RE Team被Android VRP选为Top Android Research Team。



## 议题解析：

[![](https://p4.ssl.qhimg.com/t011d3d17944a301236.png)](https://p4.ssl.qhimg.com/t011d3d17944a301236.png)

(图片来自网络)

Binder驱动本是进程间通信的桥梁，却也可以被用于攻击内核并拿到最高权限，成为通往ROOT的桥梁。Binder驱动承担了Android系统繁重的进程间通信工作，在设计的时候需要在性能和安全性之间做诸多的权衡，也会引入很多机制来处理并发及竞争问题。这些机制的引入，代码量的增加以及业务场景的丰富都将带来潜在的安全问题。

“水滴”漏洞的威力在被真正的证实之前都只是停留于理论层面的。实际上，我们用它来实际攻击系统所花的精力和克服的困难也远比当初发现它要大的多。此次在HITB上讲述的议题《Binder: The Bridge to Root》是将漏洞利用过程中用到的具体技术细节公开，也包括其中用到的一些具有通用价值的漏洞利用技术。

[![](https://p0.ssl.qhimg.com/t01a274cc009d3de740.png)](https://p0.ssl.qhimg.com/t01a274cc009d3de740.png)

在创建Binder对象的时候，用户空间和内核空间会映射一片相同的物理内存，主要用于将交互过程中的数据写入其中。而对于这片物理内存，用户态空间和内核空间的虚拟地址之间是线性的关系，即“user_ptr=kernel_ptr+alloc-&gt;user_buffer_offset”，其中的“alloc-&gt;user_buffer_offset”在内核初次建立完成针对这片物理内存的映射后便会被保存下来，并且在该用户态进程的整个生命周期内都不会再发生改变。Binder驱动通过这一机制也实现了通信进程双方高效的数据交互，仅需拷贝一次数据便可以实现从通信进程一方到另一方的数据传递。所以在申请释放内核中reply数据所用内存时候通过发送用户态reply数据的地址便可以在内核中完成查找和释放。

在通过Binder驱动进行交互时会频繁使用“strcut binder_buffer”这个结构体对象，程序设计者为了提高对象的分配使用效率引入了维护申请&amp;释放的红黑树，针对“strcut binder_buffer”这个结构体对象实现一个类似于缓存效果的机制。并在“strcut binder_buffer”中定义了“free_in_progress”及“allow_user_free”这样两个成员变量来保护其使用和释放。这种类型的保护机制一旦设计不严格经常会出现问题，不幸的是Binder驱动也没能幸免。

[![](https://p2.ssl.qhimg.com/t01e8f9b51414d45251.png)](https://p2.ssl.qhimg.com/t01e8f9b51414d45251.png)

从”binder_alloc_new_buf()”申请结束到其保护标记位”t-&gt;buffer-&gt;alloc_user_free”被赋值之前，有一个非常窄的条件竞争窗口，而这个条件竞争窗口所做的事情仅仅是检查一下返回值的合法性。设计者应该也不会觉着申请对象结束后立刻对其保护标记位进行赋值会出现什么问题。而的确，他的判断也基本准确，由于时间窗口窄到不可能在这个竞争窗口内完成对这个对象的释放，触发这一条件竞争内核最多也就是输出一些错误日志或触发BUG_ON()引起内核崩溃，更不要奢求能够在其释放后完成堆喷。

其实内核中多数漏洞即便造成了问题，也只是一些BUG，基本没有实际的利用价值。而“水滴”漏洞如果解决不了条件竞争时间窗口问题，也将成为这些BUG中的一个。

[![](https://p4.ssl.qhimg.com/t019c91eb66082681a3.png)](https://p4.ssl.qhimg.com/t019c91eb66082681a3.png)

我们研究了mutex lock的具体实现，发现其会影响调度器，因此可以将client进程和server进程绑定到同一个CPU，这样便能构造出非常稳定的漏洞触发场景。由于我们无法直接调用sched_setaffinity()来绑定server端的CPU，可通过将其余的CPU占满来间接实现。

[![](https://p5.ssl.qhimg.com/t0108cc43adfe5201e1.png)](https://p5.ssl.qhimg.com/t0108cc43adfe5201e1.png)

漏洞的触发流程需要精心设计，它需要client进程和server进程之间的巧妙配合。我们研究了“struct binder_buffer”对象的申请和释放规律，通过连续请求server进程来布局一片连续的reply data数据，之后再按照特定的流程逆向释放内核中与之对应的结构体对象来生成“诱饵”并触发漏洞。

[![](https://p1.ssl.qhimg.com/t01874d619ff36f0a8a.png)](https://p1.ssl.qhimg.com/t01874d619ff36f0a8a.png)

利用这个漏洞来泄露内核符号地址需要满足苛刻的条件。我们将通过绕过“copy_from_user()”对目标地址的检查，之后再通过在kmalloc()及kfree()放置过滤器，运行fuzzer工具来找到合适的堆喷函数，并通过泄露内核的符号地址来绕过内核地址随机化的保护。

[![](https://p0.ssl.qhimg.com/t013344a92c074ceff7.png)](https://p0.ssl.qhimg.com/t013344a92c074ceff7.png)

为了解决堆喷结构体对象生命周期不可控的问题，我们研究了kmalloc()及kzalloc()申请buffer时候的特点，提出了守护式堆喷的方法。第一次堆喷用于写入/保护数据，第二次借助生命周期可控的堆喷结对象来实现目标数据的常驻。

[![](https://p1.ssl.qhimg.com/t01f4765e3cff504c34.png)](https://p1.ssl.qhimg.com/t01f4765e3cff504c34.png)

并在最后会介绍我们在ROOT Pixel系列手机的时候用到的两种提权方案。其中一种会介绍我们如何直接泄露进程的“cred”地址，并通过任意地址写来实现ROOT。以及另外一种，通过此前阿里安全潘多拉实验室王勇在BlackHat 2018上提出的镜像攻击的方法来实现提权。

[![](https://p2.ssl.qhimg.com/t01de9cf5374c59a6e2.png)](https://p2.ssl.qhimg.com/t01de9cf5374c59a6e2.png)
