> 原文链接: https://www.anquanke.com//post/id/86807 


# 【技术分享】Windows内核Pool溢出漏洞：组合对象的Spray利用


                                阅读量   
                                **116425**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：srcincite.io
                                <br>原文地址：[http://srcincite.io/blog/2017/09/06/sharks-in-the-pool-mixed-object-exploitation-in-the-windows-kernel-pool.html](http://srcincite.io/blog/2017/09/06/sharks-in-the-pool-mixed-object-exploitation-in-the-windows-kernel-pool.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01e9702c1655feae0f.jpg)](https://p3.ssl.qhimg.com/t01e9702c1655feae0f.jpg)

译者：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**0x00前言**

本文，我将介绍一种基础的Windows内核pool的溢出漏洞，并如何使用混合内核对象喷射内核pool后，通过覆盖**TypeIndex**从而实现漏洞利用。

**<br>**

**0x01介绍**

在参加完BlackHat的[AWE课程](https://www.offensive-security.com/information-security-training/advanced-windows-exploitation/)之后，我想要学习发现并利用一些内核漏洞。尽管我想到了[HackSys Extreme Vulnerable Driver (HEVD)](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver) 是一个非常好的学习工具，但是对于我来说，它不合适。我一直都乐于在实际应用程序中发现并实现漏洞利用。

自参加那个课程后，我开始慢慢地开发了一个Windows内核设备驱动的fuzzer。使用这个私人的fuzzer，我发现了本文中将要介绍的漏洞。这种漏洞利用的技术不是新的，但是稍微改变下使得攻击者几乎可以利用任意大小的pool。本文主要是我自身的学习参考，希望能帮助其他人尝试pool漏洞利用。

**<br>**

**0x02漏洞介绍**

在测试了一些SCADA产品后，我遇到了一个第三方组件（名为**WinDriver**）。简单调查后，我发现这是[Jungo的DriverWizard WinDriver](http://www.jungo.com/st/products/windriver/)。这个产品捆绑在多个SCADA产品中，而且通常是老版本的。

在安装后，它在标准windows驱动目录中安装了一个名为wndrvr1240.sys的设备驱动。简单的逆向之后，我发现了几个IOCTL码，我将这些IOCTL值插入到我的fuzzer的配置文件中。

[![](https://p4.ssl.qhimg.com/t01dacfc11e830f28d8.png)](https://p4.ssl.qhimg.com/t01dacfc11e830f28d8.png)

然后，我使用命令行verifier /volatile /flags 0x1 /adddriver windrvr1240.sys启用了special pool，并运行我的fuzzer。最终，我发现了几个可利用的漏洞，尤其是下面这个：

[![](https://p1.ssl.qhimg.com/t01fd78591a1e72c5c7.png)](https://p1.ssl.qhimg.com/t01fd78591a1e72c5c7.png)

用户可控制的数据存储在**[esi+ecx]**中，它正在越界写一个内核pool。非常完美！进一步检查，我注意到这确实是个pool溢出，它是通过loc_4199D8中的内联复制操作触发的。

[![](https://p0.ssl.qhimg.com/t01ff53a8d88a435a7b.png)](https://p0.ssl.qhimg.com/t01ff53a8d88a435a7b.png)

这个拷贝循环每次循环拷贝8个字节（一个QWORD）， 且溢出了一个大小0x460（0x458+0x8字节的头）的缓冲区。拷贝的大小直接由攻击者的输入缓冲区控制。不需要整数溢出，数据没有存储在隐蔽的地方。我们可以在0x004199E8直接看见，大小是由攻击者控制的，来自于提供的缓冲区的+0x18偏移。太容易了！

**<br>**

**0x03漏洞利用**

现在，到了有趣的地方。通用的技术是对象TypeIndex覆盖，这种技术已经在很多场合被介绍过，它至少是6年前了，因此我不想深入太多细节。基本上就是使用任何内核对象，使你能覆盖存储在_OBJECT_HEADER中的TypeIndex。

过去使用的常见的对象是**Event**对象（大小是0x40）和IoCompletionReserve对象（大小是0x60）。典型的漏洞利用如下：

1.使用大小为X的对象**喷射**pool，填充内存页

2.通过释放附近的对象在内存页中“**打洞**”，触发合并（coalescing）来满足目标块的大小（我们的例子中是0x460）。

3.分配并**溢出**缓冲区，希望命中一个“洞”，破环下一个对象的_OBJECT_HEADER，最终破环TypeIndex。

举个例子，如果你溢出的缓冲区的大小是0x200，你应该分配一堆Event对象，并释放他们中0x8个对象（0x40*0x8==0x200）。这样你就有了“洞”，在其中你能分配并溢出。因此，我们需要的内核对象的大小是我们的pool大小的模数（取模余数为0）。

问题是某些大小不能满足。举个例子，假设我们的pool大小是0x460，那么：

[![](https://p1.ssl.qhimg.com/t01337d0c91a007d358.png)](https://p1.ssl.qhimg.com/t01337d0c91a007d358.png)

我们总是有余数。这意味着我们不能构造一个适合我们块的“洞”，我们能实现吗？有一些方法可以解决这个问题。一种方法是搜索一个内核对象，它能是我们目标缓冲区大小的模数。我花了一点时间来完成这个，并找到了2个其他的内核对象：

[![](https://p3.ssl.qhimg.com/t0183aba2766dc5416f.png)](https://p3.ssl.qhimg.com/t0183aba2766dc5416f.png)

然而，这些大小是无用的，因为它们不是0x460的模数。又花了一点时间测试修改，我确定如下的模数可以满足：

[![](https://p1.ssl.qhimg.com/t01f5b9b2e38944fcf1.png)](https://p1.ssl.qhimg.com/t01f5b9b2e38944fcf1.png)

太好了！0xa0可以均分0x460，但是我们怎么才能得到大小为0xa0的内核对象呢？如果我们将Event和IoCompletionReserve对象组合起来（0x40+0x60=0xa0）就能实现。

<a></a>**喷射**

[![](https://p5.ssl.qhimg.com/t01f52514831458382c.png)](https://p5.ssl.qhimg.com/t01f52514831458382c.png)

上述函数喷射了50000个对象。25000个Event对象和25000个IoCompletionReserve对象。在windbg中看起来非常完美：

[![](https://p3.ssl.qhimg.com/t01ffb292f5fb08e7e2.png)](https://p3.ssl.qhimg.com/t01ffb292f5fb08e7e2.png)

**“打洞”**

‘IoCo’标记表示一个IoCompletionReserve对象，同时“Even”标记表示一个Event对象。注意我们首个块偏移是0x60，这是我们将要释放的起始偏移。因此我们释放几组对象，计算如下：

[![](https://p0.ssl.qhimg.com/t0104bbd99ef23b0d14.png)](https://p0.ssl.qhimg.com/t0104bbd99ef23b0d14.png)

最终，我们会得到正确的大小。让我们快速浏览下如果只释放下7个IoCompletionReserve会是怎样。

[![](https://p1.ssl.qhimg.com/t0176ea20a9425fad10.png)](https://p1.ssl.qhimg.com/t0176ea20a9425fad10.png)

因此，我们能看到有分隔开的被释放的内存块。但是我们想将它们合并为一个0x460的被释放的内存块。为了实现这个，我们需要设置我们块的offset为0x60（指向0xXXXXY060）。

[![](https://p3.ssl.qhimg.com/t017245c8131c449b6a.png)](https://p3.ssl.qhimg.com/t017245c8131c449b6a.png)

现在，当我们运行释放函数时，我们在pool中打洞，并最终得到一个满足我们目标大小的被释放的内存块。

[![](https://p2.ssl.qhimg.com/t01bc92ebeace116c5d.png)](https://p2.ssl.qhimg.com/t01bc92ebeace116c5d.png)

我们可以看到，被释放的内存块已经合并了，现在我们有个完美大小的“洞”。我们还需要做的就是分配并覆盖内存。

[![](https://p5.ssl.qhimg.com/t01bb687116260cce85.png)](https://p5.ssl.qhimg.com/t01bb687116260cce85.png)

**溢出并“存活”**

你可能注意到了缓冲区偏移0x90处的利用中的NULL dword。

[![](https://p1.ssl.qhimg.com/t01e94696e28fd91c49.png)](https://p1.ssl.qhimg.com/t01e94696e28fd91c49.png)

这就是需要在溢出中“存活”下来，且避免任何进一步的处理。下面的代码在拷贝循环后直接执行。

[![](https://p1.ssl.qhimg.com/t016ecba846d1054733.png)](https://p1.ssl.qhimg.com/t016ecba846d1054733.png)

重点是代码将调用sub_4196CA。还要注意到@eax为我们的缓冲区+0x90（0x004199FA）。我们看下这个函数调用。

[![](https://p2.ssl.qhimg.com/t01f7e7e78d0ed157f1.png)](https://p2.ssl.qhimg.com/t01f7e7e78d0ed157f1.png)

代码从我们的SystemBuffer+0x90中得到一个dword值，写入到被溢出的缓冲区中，然后检查它是否为null，我们能在这个函数中避免进一步处理，然后返回。

[![](https://p4.ssl.qhimg.com/t01a2127c2ddda90433.png)](https://p4.ssl.qhimg.com/t01a2127c2ddda90433.png)

如果我们不做这个，当我们试图访问不存在的指针时将会BSOD。

现在，我们能干净的返回并无错的触发eop。关于shellcode清理，我们的溢出缓冲区存储在@esi中，因此我们能计算到TypeIndex的偏移并patch它。最后，使用NULL破坏ObjectCreateInfo，因为系统将避免使用那个指针。

**构造我们的缓冲区**

因为在每次循环中会拷贝0x8个字节，且起始索引是0x1c:

[![](https://p4.ssl.qhimg.com/t012ccdf5e47b3ae319.png)](https://p4.ssl.qhimg.com/t012ccdf5e47b3ae319.png)

我们可以像这样做些溢出计算。假设我们想要通过44字节（0x2c）溢出缓冲区。我们将缓冲区的大小减去头，再减去起始索引偏移，加上我们想要溢出的字节数，并将它们按0x8字节分割（因为每次循环是一个qword拷贝）。

```
(0x460 - 0x8 - 0x1c + 0x2c) / 0x8 = 0x8d
```

因此，通过0x2c字节溢出缓冲区的大小是0x8d。这将破坏了pool头、quota和对象头。

[![](https://p1.ssl.qhimg.com/t01feb987fc07283998.png)](https://p1.ssl.qhimg.com/t01feb987fc07283998.png)

我们能看到设置了TypeIndex为0x00080000。这意味着函数表将指向0x0且我们能方便的映射NULL页。

[![](https://p0.ssl.qhimg.com/t01a30ed6a0c667a34b.png)](https://p0.ssl.qhimg.com/t01a30ed6a0c667a34b.png)

注意第二个索引是0xbad0b0b0。我觉得很开心，我能在x64上面使用相同的技术。

**在内核中触发代码执行**

在触发溢出后我们能成功执行，但是为了得到eop，我们需要设置一个指针指向0x00000074来利用OkayToCloseProcedure函数指针。

[![](https://p3.ssl.qhimg.com/t01d28dc6ef5ceb5a36.png)](https://p3.ssl.qhimg.com/t01d28dc6ef5ceb5a36.png)

因此，0x28+0x4c = 0x74，它是我们指针需要的位置。但是怎么调用OkayToCloseProcedure？它是一个注册的aexit处理函数。因此为了触发代码执行，只需要释放“损坏”的IoCompletionReserve。我们不知道哪个句柄关联着溢出块，因此我们将它们全部释放。

[![](https://p0.ssl.qhimg.com/t01150fe4aa6f0224fe.png)](https://p0.ssl.qhimg.com/t01150fe4aa6f0224fe.png)

运行截图如下：

[![](https://p5.ssl.qhimg.com/t01301958e329863143.png)](https://p5.ssl.qhimg.com/t01301958e329863143.png)

**<br>**

<a></a>**0x04时间线**

2017-08-22 – 验证并通过邮件`{`sales,first,security,info`}`@jungo.com.发送给Jungo 。

2017-08-25 – Jungo没有回应。

2017-08-26 – 试图通过网站联系供应商

2017-08-26 – 通过网站联系无回应

2017-09-03 – 收到Jungo的邮件，表明他们正在调查

2017-09-03 – 请求补丁开发时间并发布可能的0day警告

2017-09-06 – 没有回应

2017-09-06 – 发布0day安全公告

<br>

<a></a>**0x05总结**

使用这个方式的利用的块大小是 &lt; 0x1000。正如上文所述，这不是新的技术，只是针对已有技术稍微变化，如果我坚持使用HEVD来学习，我将不会发现这种技术。话虽如此，使用已经存在漏洞的驱动并从中开发漏洞利用技术也是非常有价值的。

<br>

<a></a>**0x06参考**

[https://github.com/hacksysteam/HackSysExtremeVulnerableDriver](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver)

[http://www.fuzzysecurity.com/tutorials/expDev/20.html](http://www.fuzzysecurity.com/tutorials/expDev/20.html)

[https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-Slides.pdf](https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-Slides.pdf)

[https://msdn.microsoft.com/en-us/library/windows/desktop/ms724485(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms724485(v=vs.85).aspx)

[https://www.exploit-db.com/exploits/34272](https://www.exploit-db.com/exploits/34272)
