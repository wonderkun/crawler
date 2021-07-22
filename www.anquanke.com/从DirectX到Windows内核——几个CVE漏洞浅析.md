> 原文链接: https://www.anquanke.com//post/id/167332 


# 从DirectX到Windows内核——几个CVE漏洞浅析


                                阅读量   
                                **194626**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者zerodayinitiative，文章来源：zerodayinitiative.com
                                <br>原文地址：[https://www.zerodayinitiative.com/blog/2018/12/4/directx-to-the-kernel](https://www.zerodayinitiative.com/blog/2018/12/4/directx-to-the-kernel)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01ae79148fddc84599.jpg)](https://p5.ssl.qhimg.com/t01ae79148fddc84599.jpg)



## 一、前言

操作系统内核是每个漏洞利用链的最终目标，大家可以查看Zero Day Initiative (ZDI) Pwn2Own历年比赛，了解这方面内容。Windows内核一直以来都是攻击者热衷的目标，我最喜欢的就是滥用`DeviceIoControl`调用来与各种驱动打交道，这样就能访问许多厂商编写的各种驱动，其中许多驱动代码写得并不完善，也没有经过完备测试。

多年以来，许多攻击者都借助`win32k.sys`来攻击Windows内核，这是一个内核模式设备驱动，可以控制Windows图形及窗口管理系统。当微软将该功能从CSRSS中迁移到内核时，进入Windows内核的攻击面也增加了1倍或者3倍，从那时起这已经成为许多漏洞的发源地。

在过去十年期间，自从WDDM（Windows Display Driver Model）取代早期的XDDM后，大家又找到了另一个巨大的攻击面。显示系统调用操作首先会经过`win32k.sys`处理，但在此之后，用户进程就可以直接调用`dgxkrnl.sys`，或者通过`GDIPlus`中的入口点直接调用其他驱动。这进一步扩大了攻击面，因此引起了研究人员的浓厚兴趣。

2018年春季，ZDI从腾讯ZhanluLab的ChenNan及RanchoIce手中购买了5个针对DirectX内核接口的漏洞，利用这些漏洞成功从微软获取了4个CVE编号。本文分析了这些漏洞，并且提供了相应的PoC代码（代码已在我们网站上公布）。

此外，Rancho和ChenNan在9月份的44CON会议上介绍过其中一种攻击技术（ZDI-18-946/CVE-2018-8405），强烈建议大家去学习此次演讲的[演示文稿](https://github.com/RanchoIce/44Con2018/blob/master/44Con-Gaining%20Remote%20System%20Subverting%20The%20DirectX%20Kernel.pdf)。



## 二、DirectX概览

在分析漏洞之前，我们首先来简要回顾一下DirectX接口及驱动。

DirectX图形内核子系统由3个内核模式驱动所组成：`dxgkrnl.sys`、`dxgmms1.sys`以及`dxgmms2.sys`。这些驱动会通过`win32k.sys`以及自己的接口来与用户通信。此外，这些驱动也会与`BasicRender.sys`、`BasicDisplay.sys`以及miniport（微型端口）显示驱动通信。

DirectX定义了许多复杂的内核对象，大部分对象名以`DXG`开头。用户通过许多复杂的API接口与DirectX交互，其中许多接口以`D3DKMT`开头，其他接口以`DXGK`开头。

其中比较有趣的部分入口点如下所示：
<li>
`D3DKMTEscape`：这个入口点以用户完全可控的一段数据作为输入。输入数据可能非常大，因此系统很有可能将其存储在用户内存中，而不会在切换到内核处理期间在内核中捕获这段数据。这样一来，如果没有妥善处理，相关内核例程就很容易存在TOC/TOU（ time of check，time of use，基于检验时间/使用时间的一种异步攻击）漏洞。这段数据并不是标准化结构，每个驱动都有自己的定义。</li>
<li>
`D3DKMTRender`：这个入口点是实际渲染图形数据的核心。来自用户地址的命令以及patch缓冲区会交由内核驱动来解释，实际上这些数据会传递给miniport驱动。同样，这也是竞争条件问题的滋生地。此外，渲染过程还会生成worker线程，更容易出现竞争条件漏洞。</li>
<li>
`D3DKMTCreateAllocation`：这个入口点用来分配内存。由于传递给API的不同标志和句柄之间有各种复杂的相互作用，因此可能会出现一些问题（参考下文的ZDI-18-946内容）。</li>
从攻击角度来看，来自IOActive的Ilja van Sprundel曾在2014年的Black Hat会议上做过关于WDDM的一次演讲，题目为“[Windows Kernel Graphics Driver Attack Surface](https://www.blackhat.com/docs/us-14/materials/us-14-vanSprundel-Windows-Kernel-Graphics-Driver-Attack-Surface.pdf)”，这是非常好的概述资料。强烈推荐大家先参考这份材料，其中详细介绍了有关WDDM内核方面的复杂攻击面。



## 三、漏洞分析

大家可以访问[此处](https://github.com/thezdi/PoC/tree/master/DirectX)下载PoC源代码。如果大家想复现崩溃问题，需要安装2018年8月份之前的Windows版本（当时Windows还没打上补丁）。在测试过程中，记得将内核调试器attach目标主机上，并在待攻击的驱动上设置Special Pool（特殊池）。我已在Windows 10 x64位系统上测试过本文分析的这些漏洞。

### <a class="reference-link" name="ZDI-18-946/CVE-2018-8405%EF%BC%9AD3DKMTCreateAllocation%E7%B1%BB%E5%9E%8B%E6%B7%B7%E6%B7%86%E6%BC%8F%E6%B4%9E"></a>ZDI-18-946/CVE-2018-8405：D3DKMTCreateAllocation类型混淆漏洞

我们分析的第一个漏洞位于`dgxkrnl.sys`的`DXGDEVICE::CreateAllocation`方法中，可通过`D3DKMTCreateAllocation`接口触发，本地攻击者可以利用该漏洞将权限提升到`SYSTEM`级别。大家可以访问[此处](https://www.zerodayinitiative.com/advisories/ZDI-18-946/)阅读我们的安全公告，访问[此处](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8405)获取微软补丁。漏洞根源在于驱动没有正确验证用户提供的数据，导致存在类型混淆情况。

为了复现漏洞，我们需要在运行PoC之前在`dxgkrnl.sys`上设置一个Special Pool。类型混淆问题源自于在pool分配中没有正确使用`CrossAdapter`标志。在pool分配过程中，PoC代码将`CrossAdapter`标志设置为`0`，然后将所得句柄传递给第2个分配过程，其中`CrossAdapter`标志被设置为`1`。

[![](https://p2.ssl.qhimg.com/t01adbee3d05dd41f94.png)](https://p2.ssl.qhimg.com/t01adbee3d05dd41f94.png)

蓝屏信息分析如下：

[![](https://p2.ssl.qhimg.com/t01f3b466553a7552c2.png)](https://p2.ssl.qhimg.com/t01f3b466553a7552c2.png)

[![](https://p4.ssl.qhimg.com/t0102ae1e3969514734.png)](https://p4.ssl.qhimg.com/t0102ae1e3969514734.png)

[![](https://p2.ssl.qhimg.com/t01ec23aee34754eda9.png)](https://p2.ssl.qhimg.com/t01ec23aee34754eda9.png)

错误代码位于`DXGDEVICE::CreateAllocation`，这是一个在分配过程结束时的一个典型的类型混淆问题：

[![](https://p0.ssl.qhimg.com/t01602220d7993e1163.png)](https://p0.ssl.qhimg.com/t01602220d7993e1163.png)

### <a class="reference-link" name="ZDI-18-947/CVE-2018-8406%EF%BC%9AD3DKMTRender%E7%B1%BB%E5%9E%8B%E6%B7%B7%E6%B7%86%E6%BC%8F%E6%B4%9E"></a>ZDI-18-947/CVE-2018-8406：D3DKMTRender类型混淆漏洞

下一个漏洞位于`dxgmms2.sys`驱动中，可通过`D3DKMTRender`方法触发。攻击者同样可以利用这个漏洞将权限提升到`SYSTEM`级别。大家可以访问[此处](https://www.zerodayinitiative.com/advisories/ZDI-18-947/)了解我们的安全公告，访问[此处](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8406)获取相应补丁。与第一个漏洞一样，这个bug会导致出现类型混淆情况。虽然本质上相似，但这些bug的根本原因并不相同。

同样，我们需要在`dxgkrnl.sys`和`dxgmms2.sys`上启用Special Pool才能复现bug，当然我们也需要将内核调试器attach到目标主机。这个类型混淆源自于两个不同适配器之间混乱的分配操作。

相关PoC代码如下：

[![](https://p2.ssl.qhimg.com/t01e870278e21156903.png)](https://p2.ssl.qhimg.com/t01e870278e21156903.png)

PoC崩溃细节：

[![](https://p3.ssl.qhimg.com/t01b49390f8fe62623c.png)](https://p3.ssl.qhimg.com/t01b49390f8fe62623c.png)

[![](https://p0.ssl.qhimg.com/t01cfc3df339737074e.png)](https://p0.ssl.qhimg.com/t01cfc3df339737074e.png)

存在漏洞代码如下：

[![](https://p0.ssl.qhimg.com/t0127fa7bb3b5eae739.png)](https://p0.ssl.qhimg.com/t0127fa7bb3b5eae739.png)

### <a class="reference-link" name="ZDI-18-950/CVE-2018-8400%EF%BC%9AD3DKMTRender%E4%B8%8D%E5%8F%AF%E4%BF%A1%E6%8C%87%E9%92%88%E5%BC%95%E7%94%A8%E8%A7%A3%E6%9E%90%E6%BC%8F%E6%B4%9E"></a>ZDI-18-950/CVE-2018-8400：D3DKMTRender不可信指针引用解析漏洞

这个漏洞同样可以由`D3DKMTRender`例程触发。漏洞位于`dxgkrnl.sys`的`DGXCONTEXT::ResizeUserModeBuffers`方法中。大家可以访问[此处](https://www.zerodayinitiative.com/advisories/ZDI-18-950/)了解我们的安全公告，访问[此处](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8400)获取微软补丁。由于驱动在将用户提供的值作为指针解析引用（dereference）时，并没有正确验证这个值，因此导致这个bug出现。出现指针dereference问题，是因为驱动会信任用户设置的一个标志。相关PoC细节如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019c133eb2476945bd.png)

导致出现崩溃现象：

[![](https://p5.ssl.qhimg.com/t01fb30a841fddc84dc.png)](https://p5.ssl.qhimg.com/t01fb30a841fddc84dc.png)

调用栈：

[![](https://p1.ssl.qhimg.com/t01e04990ca806344b5.png)](https://p1.ssl.qhimg.com/t01e04990ca806344b5.png)

存在漏洞的代码：

[![](https://p2.ssl.qhimg.com/t016ce4227fafa2b85e.png)](https://p2.ssl.qhimg.com/t016ce4227fafa2b85e.png)

显然，用户提供的标志本不应该导致内核中出现任意dereference问题。

### <a class="reference-link" name="ZDI-18-951/CVE-2018-8401%EF%BC%9ABasicRender%E7%AB%9E%E4%BA%89%E6%9D%A1%E4%BB%B6%E6%BC%8F%E6%B4%9E"></a>ZDI-18-951/CVE-2018-8401：BasicRender竞争条件漏洞

最后一个漏洞稍微有点复杂，漏洞位于`BasicRender`驱动对`D3DKMTMarkDeviceAsError` API以及`D3DKMTSubmitCommand` API的处理过程中。大家可以访问[此处](https://www.zerodayinitiative.com/advisories/ZDI-18-951/)阅读我们的安全公告，访问[此处](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8401)下载微软补丁。这个漏洞中，共享资源并没有得到适当的保护，可能导致出现内存破坏问题。攻击者可以利用这个漏洞将权限提升为`SYSTEM`级别。恶意软件经常使用这类权限提升方法，在用户不小心点击某些东西的时候将自己安装到目标系统中。需要注意的是，微软为这个bug和[ZDI-18-949](https://www.zerodayinitiative.com/advisories/ZDI-18-949/)分配了同一个CVE编号，表明这两个漏洞的根本原因相同。

这两个漏洞的PoC代码存在相关性，但有所区别。

第一个PoC的关键代码如下：

[![](https://p5.ssl.qhimg.com/t01c717a5e42513816f.png)](https://p5.ssl.qhimg.com/t01c717a5e42513816f.png)

每次调用`SubmitCommand`时都会通过`VidSchiWorkerThread`生成一个线程。调用`MakeDeviceError`会修改相同对象的状态，导致出现竞争条件。

最终会出现崩溃：

[![](https://p2.ssl.qhimg.com/t013c31094abec5e657.png)](https://p2.ssl.qhimg.com/t013c31094abec5e657.png)

对同一个位置有两次修改，出现竞争条件：

[![](https://p1.ssl.qhimg.com/t01a38d9446ca8d2720.png)](https://p1.ssl.qhimg.com/t01a38d9446ca8d2720.png)

对于`ZDI-18-949`，虽然漏洞根源一样，但我们还是可以在PoC代码中看到不同之处。PoC中关键代码如下：

[![](https://p3.ssl.qhimg.com/t01ca252b8d7039b3c4.png)](https://p3.ssl.qhimg.com/t01ca252b8d7039b3c4.png)

执行这个PoC会导致`Run`方法崩溃：

[![](https://p5.ssl.qhimg.com/t01782fdec469964db6.png)](https://p5.ssl.qhimg.com/t01782fdec469964db6.png)

存在漏洞的代码如下：

[![](https://p5.ssl.qhimg.com/t012f377baa8bd92b37.png)](https://p5.ssl.qhimg.com/t012f377baa8bd92b37.png)

存在漏洞的代码会在第二次运行`Run`时崩溃。



## 四、总结

WDDM以及DirectX图形内核代码使用了许多复杂对象、为用户代码创建许多新的复杂接口，从而为Windows提供了非常强大和灵活的图形系统。分析前文提供的PoC后，大家应该对DirectX在对象实现上的复杂度以及未来该领域可以研究的方向有所了解，我认为该领域还有许多尚未挖掘的财富。

通过直接静态分析方法，我们还是可以获取一些攻击信息，然而这肯定是一项艰巨的任务。还有一种可能采取的方法，我们可以部署一个模糊测试框架，在不同的标志上设置不同的值，然后以不同的顺序来调用DirectX方法，查找崩溃点。当然，我们也可以添加多个线程修改及释放数据，来寻找是否存在竞争条件和TOC/TOU问题。另外别忘了在所有相关驱动上设置Special Pool。

老生常谈，Zero Day Initiative对新漏洞非常感兴趣，当大家发现新漏洞时，可以通过推特（[推特](https://twitter.com/thezdi)获取最新漏洞利用技术和安全补丁信息。
