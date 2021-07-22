> 原文链接: https://www.anquanke.com//post/id/149551 


# MOSEC议题解读 | Build your own iOS kernel debugger


                                阅读量   
                                **108005**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t014a4766b2a8ac06d8.jpg)](https://p0.ssl.qhimg.com/t014a4766b2a8ac06d8.jpg)



## 议题概要

Ian Beer在这次议题中介绍了如何针对零售版的iOS设备开发一个内核调试器。议题的内容会涵盖ARM64底层在XNU中的异常处理，KDP远程调试的协议以及如何在不修改内核代码的前提下打造一个支持设置断点的本地内核调试器。



## 作者介绍

Ian Beer在Google的Project Zero团队从事漏洞挖掘与利用的相关研究。



## 议题解析

### 历史与现状

在旧版本的iOS内核中支持KDP，并且通过一些bootrom和kernel的漏洞时设置内核启动时的参数。通过特殊数据线的配合可以实现调试iOS内核的功能。

但是在当前版本中iOS内核已经不支持KDP了，并且异常处理模块也不支持断点功能，同时硬件设备也没有提供真正的串口。这些限制都导致了在当前版本中研究人员无法通过调试器对iOS的内核进行动态调试。

### 设计与实现

Ian beer试图通过硬件断点构造一个可以使用的iOS内核调试器。

通过在源码中搜索“hardware breakpoint”在某一个分支中找到如下这段代码：

[![](https://p4.ssl.qhimg.com/t01bff274780feee157.png)](https://p4.ssl.qhimg.com/t01bff274780feee157.png)<br clear="ALL">根据这一段代码可以知道，如果我们能够构建并使得一个硬件断点生效的话，将导致当前执行代码的那一颗核（core）进入一个死循环。

根据对这个异常处理的分析与研究，Ian Beer给出一个通过硬件断点编写iOS内核调试器的设计思路。

**断点“触发”**

当硬件断点的异常事件被触发后，根据该异常处理的相关代码，程序会陷入一个死循环，给我们进行代码调试的时机。

**断点“释放”**

通过FIQ异常的特性，可以将硬件断点触发后陷入死循环的线程通过调度算法重新执行。

**iOS的异常处理**

在iOS内核中，当exception发生时（无论该异常是由应用层还是内核触发）当前调用栈和寄存器寄存器都会保存在栈上的特殊位置上，在陷入“死循环”便可以根据规律去相应的位置对寄存器和调用栈进行访问，从而实现调试器的具体功能。

[![](https://p3.ssl.qhimg.com/t014b944bec5a6b23e1.png)](https://p3.ssl.qhimg.com/t014b944bec5a6b23e1.png)

**异常处理流程**

**实现中遇到的问题**

在正常情况下硬件断点是没法通过正常的应用层程序设置的。

表示进程状态的PSTATE.D值在进入异常处理后会被设为1，而当PSTATE.D的值为1的时候硬件断点是不会生效的，并且内核不会将这个值清零。

**通过内核任意读写修改硬件断点数据结构**

确切的说硬件断点在应用层其实是可以设置的，但是不能被enable。所以只要我们拥有一个内核任意读写的漏洞，就可以修改相关数据的值，将硬件断点设置为enable的状态。

[![](https://p2.ssl.qhimg.com/t01e82f869520c4e554.png)](https://p2.ssl.qhimg.com/t01e82f869520c4e554.png)

**通过ROP封装一个自己的System Call**

因为在异常处理是会将PSTATE.D设为1，而PSTATE.D的值为1的时候硬件断点是无法生效的。通过ROP自己封装一个system call，先将PSTATE.D设为0之后再去做相应的系统调用，这时就可以触发硬件断点了。

[![](https://p1.ssl.qhimg.com/t016c622da20e673aba.png)](https://p1.ssl.qhimg.com/t016c622da20e673aba.png)

<br clear="ALL">**最终的实现方案**

**LLDB**

最后通过实现一个支持KDP的debugserver，这样用户可以使用lldb进行iOS的内核调试了。

[![](https://p1.ssl.qhimg.com/t017c5674062a93bc1b.png)](https://p1.ssl.qhimg.com/t017c5674062a93bc1b.png)



## 总结

Ian Beer向我们展示了一个实现非常精巧的iOS内核调试器。虽然功能上仍然存在一切缺陷，但是对安全研究人员来说已经完全可以胜任所有的需求了。Ian Beer还提到，如果拥有了对内核线程做调试的能力，那么应用层App的数据安全将无法得到保障。

本议题内容非常硬核，有兴趣的读者可以在Ian Beer公布源码后再做深入的学习和理解。

审核人：Atoo     编辑：少爷
