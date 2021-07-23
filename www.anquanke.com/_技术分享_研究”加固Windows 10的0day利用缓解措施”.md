> 原文链接: https://www.anquanke.com//post/id/85434 


# 【技术分享】研究”加固Windows 10的0day利用缓解措施”


                                阅读量   
                                **92750**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：improsec.com
                                <br>原文地址：[https://improsec.com/blog//hardening-windows-10-with-zero-day-exploit-mitigations-under-the-microscope](https://improsec.com/blog//hardening-windows-10-with-zero-day-exploit-mitigations-under-the-microscope)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01579f9438d00427fe.jpg)](https://p5.ssl.qhimg.com/t01579f9438d00427fe.jpg)

翻译：[**myswsun**](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：140RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**0x00 前言**

在两周前，来自Windows攻击安全研究团队（OSR）发布的关于加固Windows 10对抗内核利用：[https://blogs.technet.microsoft.com/mmpc/2017/01/13/hardening-windows-10-with-zero-day-exploit-mitigations/https://blogs.technet.microsoft.com/mmpc/2017/01/13/hardening-windows-10-with-zero-day-exploit-mitigations/](https://blogs.technet.microsoft.com/mmpc/2017/01/13/hardening-windows-10-with-zero-day-exploit-mitigations/https:/blogs.technet.microsoft.com/mmpc/2017/01/13/hardening-windows-10-with-zero-day-exploit-mitigations/)

Windows上的内核利用几乎总是需要原始内核读或写。因此OSR报告了Windows 10周年版更新如何加固来缓解原始操作的使用。问题来自与tagWND对象，在内核中表示一个窗口。读了这个博文，我想起了我去年10月份做的一些研究。大约在Black Hat Europe 2016之前两周，我在Windows10周年版更新上面查找利用tagWND对象来原始读写。但是在我准备写些关于我发现的东西之前，在Black Hat Europe上通过窗口攻击窗口的讨论就发表了：[https://www.blackhat.com/docs/eu-16/materials/eu-16-Liang-Attacking-Windows-By-Windows.pdf](https://www.blackhat.com/docs/eu-16/materials/eu-16-Liang-Attacking-Windows-By-Windows.pdf)

因此我停止了写作的想法，因为我的发现基本上和他们相同。然而在读了OSR发布的博文后，来自Yin Liang 和 Zhou Li的演讲只能在1511版本上面演示，这个版本不存在新的缓解措施。然而我做我的研究时发现了一些烦人的指针验证，但是发现了一个绕过他们的方式，在当时并没有想到它。现在我确认了这个指针验证就是OSR发布的加固措施，并且他们非常容易绕过，重新带回原始读写功能。

本文将浏览加固的过程，和它的问题，且如何绕过它。下面的分析是在2016年更新的Windows 10版本研究的。

<br>

**0x01 原始PoC**

我将复用来自Black Hat Europe的演讲内容，因此如果你还没有阅读，我建议你现在看一下它。这个演讲的本质是一个write-what-where漏洞的情况，结构体tagWND的cbwndExtra字段可能增长并且允许覆盖内存。因此如果两个tagWND对象紧挨着存放，覆盖第一个tagWND对象的cbwndExtra字段可能允许利用来修改下一个tagWND对象的字段。这些当中有strName，包含了一个窗口标题位置的指针，修改这个能被利用来在内核内存中读写。下面的代码片段展示了如何使用SetWindowLongPtr和NtUserDefSetText来做到这点：

[![](https://p2.ssl.qhimg.com/t01ecc28af4e4da4ee6.png)](https://p2.ssl.qhimg.com/t01ecc28af4e4da4ee6.png)

这个创建了一个新的LargeUnicodeString对象和试图在任意地址写入内容。调用SetWindowLongPtr被用来改变窗口名字的指针，并且然后再次恢复它。这个在周年版之前的所有版本可以有效，现在会引起相面的bugcheck：

[![](https://p0.ssl.qhimg.com/t01378269fe605da54f.png)](https://p0.ssl.qhimg.com/t01378269fe605da54f.png)

这个确实在OSR发布的博文中有描述。

<br>

**0x02 深入挖掘**

为了理解为什么会引起bugcheck，我开始调试函数DefSetText的流程。当进入这个函数，我们已经有了RCX存放的tagWND对象的地址和RDX存放的指向新的LargeUnicodeString对象的指针。第一部分的验证如下：

[![](https://p0.ssl.qhimg.com/t011c0d93b492738342.png)](https://p0.ssl.qhimg.com/t011c0d93b492738342.png)

这个仅仅确保tagWND对象和新的LargeUnicodeString对象格式正确。一点点深入函数：

[![](https://p5.ssl.qhimg.com/t01bc4793eecbc1fff2.png)](https://p5.ssl.qhimg.com/t01bc4793eecbc1fff2.png)

DesktopVerifyHeapLargeUnicodeString是新的加固函数。它使用LargeUnicodeString地址为参数，这个包含了我们通过调用SetWindowLongPtr改变的指针。并且针对Desktop的tagWND对象的一个指向tagDESKTOP结构体的指针被使用。新函数的第一部分是验证字符串的长度是不是正确的格式，并且不还有原始长度，因为他们应该是Unicode字符串：

[![](https://p4.ssl.qhimg.com/t01eceb81b81cbae58f.png)](https://p4.ssl.qhimg.com/t01eceb81b81cbae58f.png)

然后校验确保LargeUnicodeString的长度不是负数：

[![](https://p1.ssl.qhimg.com/t012d4f5429bf40df0a.png)](https://p1.ssl.qhimg.com/t012d4f5429bf40df0a.png)

然后以指向tagDESKTOP的指针为参数调用DesktopVerifyHeapPointer，记住RDX已经包含了缓冲区地址。接下来发生的是触发bugcheck。在结构体tagDESKTOP对象的偏移0x78和0x80处解引用了，这是桌面的堆和大小，比较地址我们试图写操作LargeUnicodeString。如果那个地址不在桌面堆中，则会引起bugcheck。OSR说的加固措施如下：

[![](https://p4.ssl.qhimg.com/t01bf58c4a880ad8473.png)](https://p4.ssl.qhimg.com/t01bf58c4a880ad8473.png)

非常清晰，原始写不再有效，除非在桌面堆中使用，但是被限制了。

<br>

**0x03 新的希望**

不是所有的都丢了，桌面堆的地址和它的大小都来自tagDESKTOP对象。然而没有验证指向tagDESKTOP对象的指针是否正确。因此如果我们创建一个假的tagDESKTOP对象，并且替换原始的，然后我们能控制0x78和0x80偏移。因为指向tagDESKTOP的指针被tagWND使用，我们也能使用SetWindowLongPtr修改它。下面是更新的函数：

[![](https://p1.ssl.qhimg.com/t018b196f756046ad56.png)](https://p1.ssl.qhimg.com/t018b196f756046ad56.png)

g_fakeDesktop被分配的用户层地址是0x2a000000。因为Windows10不采用SMAP所以这是可能的，然而如果这么做，我们能将它放到桌面堆上，因为仍然允许在哪里写。运行更新的PoC来确保校验通过了，并且回到下面的代码片段：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017ccbb0c84d4345bd.png)

因此另一个调用来做相同的校验，还是tagDESKTOP作为第一个参数，现在缓冲区指针加上最大字符串的长度减1是第二个参数，而不是字符串缓冲区的开始。校验将通过并执行到DefSetText。

当我们继续执行，我们还会引起一个新的bugcheck：

[![](https://p1.ssl.qhimg.com/t01acf297877fa9dc29.png)](https://p1.ssl.qhimg.com/t01acf297877fa9dc29.png)

这是因为下面的指令：

[![](https://p3.ssl.qhimg.com/t010fa5673bb4440f7a.png)](https://p3.ssl.qhimg.com/t010fa5673bb4440f7a.png)

因为R9包含了0x1111111111111111，非常清楚是由假的tagDESKTOP对象填充的。使用IDA我们发现：

[![](https://p5.ssl.qhimg.com/t01d7212eecd7003a4a.png)](https://p5.ssl.qhimg.com/t01d7212eecd7003a4a.png)

证实了R9的内容确实来自tagDESKTOP指针，并且是第二个QWORD。因此我们能更新代码来设置这个值。如果设置为0，解引用被绕过。运行新的代码不会导致崩溃，任意覆盖如下：

[![](https://p1.ssl.qhimg.com/t019a842c08f70c5498.png)](https://p1.ssl.qhimg.com/t019a842c08f70c5498.png)

<br>

**0x04 总结**

总结下OSR确实做了加固措施，但是还不够。相同的方式也能通过使用InternalGetWindowText来作为原始读。

代码如下：[https://github.com/MortenSchenk/tagWnd-Hardening-Bypass](https://github.com/MortenSchenk/tagWnd-Hardening-Bypass)
