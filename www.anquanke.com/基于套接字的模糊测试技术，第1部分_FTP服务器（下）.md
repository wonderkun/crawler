> 原文链接: https://www.anquanke.com//post/id/227121 


# 基于套接字的模糊测试技术，第1部分：FTP服务器（下）


                                阅读量   
                                **140994**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Antonio Morales，文章来源：securitylab.github.com
                                <br>原文地址：[https://securitylab.github.com/research/fuzzing-sockets-FTP](https://securitylab.github.com/research/fuzzing-sockets-FTP)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01d7019a86ea5383c8.jpg)](https://p1.ssl.qhimg.com/t01d7019a86ea5383c8.jpg)



在上一篇文章中，我们为读者介绍了在基于套接字的模糊测试过程中，修改源代码中与套接字、文件系统调用、事件处理以及fork函数相关的代码的各种技巧，在下一篇文章中，我们将继续为读者介绍更多的精彩内容。



## chroot与权限

大多数FTP服务器的攻击面只有在身份验证后才可用。为此，我们必须确保Fuzzer能够顺利通过目标FTP服务器的身份验证。为此，我在系统中添加了一个用户fuzzing，用于对目标FTP服务器进程进行身份验证，并将此用户身份验证添加到我的输入语料库（input corpus）和模糊测试字典（fuzzing dictionary）中。

一旦用户登录，FTP服务器通常会调用chroot(2)来改变进程的有效根目录。这给我们带来了一些障碍，因为它可能会阻止我们的目标进程访问我们希望它能够访问的数据。

例如，子进程路径可能会降低权限，从而导致我们可能无法再访问AFL .cur_input文件。对于下面的例子来说，为了解决这个问题，我们只需将文件设置为可读/可写/可执行即可：

[![](https://p2.ssl.qhimg.com/t014d859584c771e689.png)](https://p2.ssl.qhimg.com/t014d859584c771e689.png)



## 降低随机性

为了提高AFL的稳定性，我们需要尽量减少程序中的随机性。这样一来，对于相同的输入，Fuzzer将始终覆盖相同的执行代码路径。

在下面的例子中，我们废掉了随机数生成的随机性，使其返回一个可重复的RNG状态。

[![](https://p4.ssl.qhimg.com/t0147c1518e62b954c0.png)](https://p4.ssl.qhimg.com/t0147c1518e62b954c0.png)

[![](https://p2.ssl.qhimg.com/t0193a5622343bb6d22.png)](https://p2.ssl.qhimg.com/t0193a5622343bb6d22.png)



## 信号

许多应用程序都提供了自己的信号处理程序，以取代默认的Linux信号处理程序。这可能会使AFL无法捕获特定的信号，从而导致错误。但是，我们通常不会删除所有的信号处理程序，因为这可能会导致应用程序的意外行为，所以，我们必须识别任何可能导致AFL执行错误的信号。

[![](https://p0.ssl.qhimg.com/t018cf5e32ad579fc8e.png)](https://p0.ssl.qhimg.com/t018cf5e32ad579fc8e.png)

注释掉对alarm(2)函数的调用也是有帮助的：

[![](https://p1.ssl.qhimg.com/t01f5f7000d96a20900.png)](https://p1.ssl.qhimg.com/t01f5f7000d96a20900.png)



## 避免延迟和优化

时序是至关重要的，当我们谈论模糊测试时更是如此。在应用中必须尽量减少任何不必要的延迟，以提高模糊测试的速度。在下面的例子中，我们尽可能地缩小定时间隔，并删除对sleep(3)或usleep(3)的不必要的调用。

[![](https://p1.ssl.qhimg.com/t014d25fa0524a5ad20.png)](https://p1.ssl.qhimg.com/t014d25fa0524a5ad20.png)

[![](https://p5.ssl.qhimg.com/t01ff1695ce9e14cedb.png)](https://p5.ssl.qhimg.com/t01ff1695ce9e14cedb.png)

同样，在进行模糊测试时，我们往往会发现，逻辑流程的微小变化会极大地加快模糊处理的速度。例如，随着生成文件数量的增加，listdir命令的执行时间越来越长，所以，我选择每生成N个文件只执行一次listdir命令：

[![](https://p0.ssl.qhimg.com/t0113d93b2536ac69d9.png)](https://p0.ssl.qhimg.com/t0113d93b2536ac69d9.png)



## 最后一点

最后，我想强调一个经常被忽视的事情：模糊测试不是一个完全自动化的过程。

有效的模糊测试需要对目标软件的内部结构有详细的了解，以及在所有可能的执行情况下实现良好的代码覆盖率的有效策略。

例如，为了有效地对本案例研究中的FTP服务器进行模糊测试，我们必须修改近1500行的代码： 

[![](https://p5.ssl.qhimg.com/t0100435ffef5378cef.png)](https://p5.ssl.qhimg.com/t0100435ffef5378cef.png)

目标代码和Fuzzer的整合，是一项需要付出巨大努力的任务，也是获得成功的关键之所在。这在模糊测试社区是一个备受追捧的目标，这一点从高额的奖金中就可以看出，比如Google为将安全关键项目与OSS-Fuzz整合在一起提供了高达20,000美元的奖励。

这应该会激励开发者促进模糊测试技术的发展，并促进相关模糊测试工具的创建，以简化与AFL和LibFuzzer的集成。正如我的同事Kevin最近写的那样，“反模糊测试的概念实在是太荒谬了”。



## 输入语料库

就本项目的模糊输入语料而言，我的主要目标是实现所有FTP命令的全边缘覆盖，以及实现多样化的执行场景组合，以获得合理完整的路径覆盖。 

[![](https://p0.ssl.qhimg.com/t01564f4c05918a6d5f.png)](https://p0.ssl.qhimg.com/t01564f4c05918a6d5f.png)

读者可以从这里找到在PureFTPd中使用的输入语料。同时，大家还可以在这里找到一个简单的FTP模糊测试字典的例子。



## 漏洞详情

在本节中，我将为大家详细介绍在这次模糊测试过程中发现的一些比较有趣的漏洞。

### CVE-2020-9273

这个漏洞允许您在数据通道处于工作状态时，通过向命令通道发送特定数据来破坏ProFTPd内存池。最简单的例子就是发送中断字符Ctrl+c。这将触发ProFTPd内存池中的Use-After-Free漏洞。

ProFTPd内存池的实现是基于Apache HTTP Server的，并采用了分层结构。

[![](https://p5.ssl.qhimg.com/t0154243826171b3462.png)](https://p5.ssl.qhimg.com/t0154243826171b3462.png)

在内部，每个池的结构其实就是一个资源的链接列表，当池被销毁时，这些资源会自动释放。

[![](https://p1.ssl.qhimg.com/t01c56a684200e401fb.png)](https://p1.ssl.qhimg.com/t01c56a684200e401fb.png)

每次调用pcalloc(ProFTPd的动态分配器)时，它都会尝试使用链表中最后一个元素的可用内存来满足需求。如果需要的内存比可用的多，pcalloc会通过调用new_block函数在链表的尾部添加一个新的内存块。

[![](https://p1.ssl.qhimg.com/t01fdac0defd434b4fd.png)](https://p1.ssl.qhimg.com/t01fdac0defd434b4fd.png)

问题是，new_block函数在并发场景中使用时并不安全，在某些情况下，new_block函数可能会获取池中已存在内存块，并将其视为空闲块，从而导致池列表损坏。

[![](https://p4.ssl.qhimg.com/t012553b75ee900ded9.png)](https://p4.ssl.qhimg.com/t012553b75ee900ded9.png)

在下面的例子中，我们可以看到内存池已经被破坏，因为圈出的内存值并不是有效的内存地址。

[![](https://p2.ssl.qhimg.com/t0103e9777419bab88f.png)](https://p2.ssl.qhimg.com/t0103e9777419bab88f.png)

考虑到以下情况，这个漏洞的严重性相当大：
1. 由于可以从Use-After-Free中获取写原语，因此该漏洞有可能被充分利用；
1. 内存池破坏可能导致其他的漏洞，如OOB-Write或OOB-Read漏洞。
### CVE-2020-9365

这其实是一个OOB读取漏洞，会影响Pure-FTPd中的pure_strcmp函数。如下面的代码所示，该漏洞是由于s1和s2字符串的大小不同而引起的。

[![](https://p1.ssl.qhimg.com/t01dd3774aad5953918.jpg)](https://p1.ssl.qhimg.com/t01dd3774aad5953918.jpg)

因此，如果s1的长度大于s2，则for循环将执行len-1次迭代，其中len-1 &gt; strlen(s2)。结果，导致程序访问了s2数组边界之外的内存。

攻击者可以利用这个漏洞从PureFTPd进程内存中泄漏敏感信息或使PureFTPD进程本身崩溃。

### CVE-2020-9274

在这个案例中，我们发现了一个未初始化的指针漏洞，该漏洞也可能导致越界读取。

问题的根源来自diraliases.c中的init_aliases函数。在这个函数中，链表中最后一个元素的下一个元素未设置为NULL。

[![](https://p5.ssl.qhimg.com/t010aa4e2ef8aa602bb.png)](https://p5.ssl.qhimg.com/t010aa4e2ef8aa602bb.png)

如此一来，当调用lookup_alias(const char *alias)或print_aliases(void)函数时，它们将无法正确检测到链表的结束，并尝试访问不存在的列表成员。

[![](https://p0.ssl.qhimg.com/t0160874ae02e656387.png)](https://p0.ssl.qhimg.com/t0160874ae02e656387.png)

这个漏洞的严重性取决于操作系统以及默认情况下是否将后备内存清零，因为这会影响curr变量的默认值。



## 致谢

再次，我们要感谢PureFTPd、BFTPd和ProFTPD的开发人员在解决这些漏洞的过程中的密切配合。他们以创纪录的时间解决了这些问题，非常高兴有机会与他们合作！

下面是本文中涉及的工具和参考资料： 
1. PureFTPd
1. Bftpd
1. ProFTPD
1. AFL++