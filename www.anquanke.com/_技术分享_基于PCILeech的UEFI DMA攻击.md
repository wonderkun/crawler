> 原文链接: https://www.anquanke.com//post/id/86840 


# 【技术分享】基于PCILeech的UEFI DMA攻击


                                阅读量   
                                **161417**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：frizk.net
                                <br>原文地址：[http://blog.frizk.net/2017/08/attacking-uefi.html](http://blog.frizk.net/2017/08/attacking-uefi.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t017eb7edbe2523aaea.jpg)](https://p0.ssl.qhimg.com/t017eb7edbe2523aaea.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

****

与[mac](http://blog.frizk.net/2016/12/filevault-password-retrieval.html)不同的是，许多PC会受到针对UEFI的预启动**直接内存访问**（Direct Memory Access，**DMA**）攻击的影响。如果成功攻击配置了安全启动选项的系统，那么计算机的信任链就会被破坏，安全启动选项也会变得形同虚设。

如果在操作系统启动之前，攻击者已经获得代码执行权限，那么攻击者就有可能进一步攻破尚未加载的操作系统。比如，利用这种方式，攻击者可能攻破启用设备保护（**Device Guard**）以及基于虚拟化的安全特性（Virtualization Based Security，VBS）的Windows 10系统。[Dmytro Oleksiuk](https://twitter.com/d_olex/status/898365202936119296)在这一领域已经开展了相关研究。

本文将重点介绍利用DMA来攻击UEFI的具体方法，不会拓展介绍如何进一步攻破操作系统。

<br>

**二、什么是UEFI**

****

UEFI的全称为**Unified Extensible Firmware Interface**（统一的扩展固件接口）。在操作系统启动之前，UEFI固件就会在计算机上运行。UEFI负责检测操作系统启动所需的内存、磁盘以及其他硬件。UEFI本身就是一个小型的操作系统。有时候，人们也会把UEFI称之为BIOS。

<br>

**三、攻击目标**

****

我们在6月份购买了一台使用“Kaby Lake” i3处理器的全新的Intel NUC主机。这台主机拥有8G内存，搭载了具备安全启动（Secure Boot）功能的Win10 1703系统，同时也启动了Bitlocker+TPM、基于虚拟化的安全（VBS）设备保护（Device Guard）功能。BIOS版本为BNKBL357.86A.0036.2017.0105.1112。我们可以通过内部M.2插槽实现DMA访问。

我们的实验目标还有另一台主机，这是一台较老的联想T430笔记本，拥有8G内存，搭载了具备安全启动的Win10 1703系统，同时也开启了Bitlocker+TPM、基于虚拟化的安全（VBS）设备保护（Device Guard）功能。我们可以通过ExpressCard插槽实现DMA访问。

[![](https://p5.ssl.qhimg.com/t010a9266764ec3fe99.jpg)](https://p5.ssl.qhimg.com/t010a9266764ec3fe99.jpg)

**<br>**

**四、问题根源**

****

最根本的问题在于，许多UEFI仍然没有实现对DMA攻击的防护，尽管多年以来，能够防护此类攻击的硬件（VT-d/IOMMU）已经集成到所有CPU中。如下图所示，[PCILeech](https://github.com/ufrisk/pcileech)尝试通过DMA来搜寻目标主机的内存，寻找UEFI的hook点。一旦找到突破口，PCILeech就能导出内存（如下图所示），进一步执行其他攻击行为，比如无视安全启动功能来执行任意代码。

[![](https://p3.ssl.qhimg.com/t01aac0f855d798b66b.jpg)](https://p3.ssl.qhimg.com/t01aac0f855d798b66b.jpg)



**五、攻击过程**

****

如果主机允许DMA访问，那么攻击者就能找到正确的内存结构，通过覆盖这些内存结构，实现对计算机的完全控制。PCILeech可以自动完成这个过程。我们可以在内存中搜索EFI系统表（System Table）“IBI SYST”的地址，当然把这个任务直接交给PCILeech会更加简单。EFI系统表中包含EFI启动服务表“BOOTSERV”的具体地址，这个表中包含许多有价值的函数指针。我们的攻击植入模块可以调用或hook这些启动服务函数。

如下图所示，我们成功hook了启动服务函数SignalEvent()。一旦我们插入了用于UEFI的PCILeech“内核（kernel）”模块，我们就可能像利用普通的PCILeech内核模块那样，利用该模块来导出内存以及执行代码。在下图中，PCILeech UEFI植入模块uefi_textout被多次调用。输出结果会显示在受害者计算机屏幕中。

[![](https://p3.ssl.qhimg.com/t014f5a2e2f5b96b492.jpg)](https://p3.ssl.qhimg.com/t014f5a2e2f5b96b492.jpg)

一旦攻击完成，我们可以向PCILeech发送kmdexit命令，卸载UEFI植入模块。在这种情况下，Windows的启动过程如下图所示。如果攻击目标是已加载的操作系统，我们最好hook ExitBootServices()这个函数，当操作系统从UEFI处接管计算机的控制权时，基于EFI的操作系统加载程序就会调用这个函数。此时，恶意代码就可以修改操作系统加载程序。

[![](https://p2.ssl.qhimg.com/t018e6f5ad59e6db01b.jpg)](https://p2.ssl.qhimg.com/t018e6f5ad59e6db01b.jpg)



**六、动手尝试**

****

个人可以亲自动手复现这个实验过程吗？答案是肯定的。实验代码已作为[PCILeech直接内存访问攻击工具包](https://github.com/ufrisk/pcileech)的一部分，在Github上开源。

<br>

**七、总结**

****

基于PCILeech的UEFI DMA攻击方法已经公布于众，整个攻击过程执行起来也不会特别麻烦。实现对UEFI的DMA攻击再也不是一个虚无缥缈的理论。

请确保在BIOS中启用VT-d以防护DMA攻击。

攻击者可借此进一步突破操作系统，因为如果UEFI存在漏洞，那么依赖基于虚拟化的安全已经不再是一件可靠的事情。
