> 原文链接: https://www.anquanke.com//post/id/86345 


# 【技术分享】Pwn2Own2017专题：VMWARE UAF漏洞分析


                                阅读量   
                                **99697**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：zerodayinitiative.com
                                <br>原文地址：[https://www.zerodayinitiative.com/blog/2017/6/26/use-after-silence-exploiting-a-quietly-patched-uaf-in-vmware](https://www.zerodayinitiative.com/blog/2017/6/26/use-after-silence-exploiting-a-quietly-patched-uaf-in-vmware)

译文仅供参考，具体内容表达以及含义原文为准

******[![](https://p2.ssl.qhimg.com/t01fb4e8925a9e85b8e.jpg)](https://p2.ssl.qhimg.com/t01fb4e8925a9e85b8e.jpg)**

译者：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**0x00 前言**



每年春季我们都会在CanSecWest大会上举行Pwn2Own（P2O）比赛，这段时间我们都会忙于建立目标、回复选手问题和检查程序提交。在2016年，我们在P2O上面引入了VMware逃逸，但是没有任何提交者。在2017年我们有些期待，因此当我们收到VMware漏洞时并不惊讶。

我好奇这个漏洞有很多原因。首先我认为它需要些提交技巧，有可能会有重复，因此要避免另一个竞争者完胜。这在过去发生过。其次，也是最重要的，它是一个影响拖拽（DnD）的UAF漏洞，并且能被远程调用触发，之前从来遇到过。

本文覆盖了这个漏洞，并且要利用它。这也是讨论VMware系列的第一篇博文，包括漏洞利用、逆向和模糊测试VMware目标。从虚拟机客户端到执行代码有了个新的视野。

注意：这个漏洞存在于VMware Workstation 12.5.2及早期版本。在12.5.3版本中修复了。下面所有的分析的目标是12.5.1版本。

<br>

**0x01 Bug**



在我解释这个bug的细节之前，下面是展示全部利用的视频：



这个漏洞触发很简单。发送下面的RPCI请求触发这个漏洞：

[![](https://p1.ssl.qhimg.com/t01fa0815b175ebdb39.png)](https://p1.ssl.qhimg.com/t01fa0815b175ebdb39.png)

针对vmware-vmx.exe启用页堆，WinDbg将接收到下面的异常：

[![](https://p5.ssl.qhimg.com/t013a3abc074257c9c8.png)](https://p5.ssl.qhimg.com/t013a3abc074257c9c8.png)

使用!heap得到@RCX的详细信息。首先我知道它是一个UAF，其次我知道哪里发生释放：

[![](https://p0.ssl.qhimg.com/t01ed5e53b191bef0b9.png)](https://p0.ssl.qhimg.com/t01ed5e53b191bef0b9.png)

[![](https://p2.ssl.qhimg.com/t0110a2c024be44ed02.png)](https://p2.ssl.qhimg.com/t0110a2c024be44ed02.png)

下一步是确定对象的大小。通过在释放前设置合适的断点，针对@RCX运行!heaps,得到信息如下：

[![](https://p5.ssl.qhimg.com/t019de35aec242a1f71.png)](https://p5.ssl.qhimg.com/t019de35aec242a1f71.png)

 [![](https://p4.ssl.qhimg.com/t01d910159f8ebb9e8f.png)](https://p4.ssl.qhimg.com/t01d910159f8ebb9e8f.png)

上述反汇编吸纳是了释放的对象的大小是0xb8。通过崩溃附近的指令，我观察到有个大小0x38的对象指针，其是在VM启动是分配的：

[![](https://p0.ssl.qhimg.com/t017a6452aae6ab20e5.png)](https://p0.ssl.qhimg.com/t017a6452aae6ab20e5.png)

 [![](https://p1.ssl.qhimg.com/t011b9544d093877589.png)](https://p1.ssl.qhimg.com/t011b9544d093877589.png)

<br>

**0x02 利用这个Bug**



检查崩溃时的反汇编，很明显我需要一些信息泄漏来利用这个漏洞。为了加速这个过程，我使用了腾讯安全团队的漏洞，能泄漏vmware-vmx.exe的地址。这个特别的信息泄漏的细节在将来讨论，但是它给了我们成功利用的必要条件。

通常，当我尝试利用漏洞时，我会问我自己下面的问题：

1. 我发送什么类型的请求

2. 我控制什么

3. 我怎么控制崩溃

4. 我怎么得到更好的利用原语

此时，我能发送RPCI请求，技术上它能通过后门接口及其他后门请求发送。是的，VMware官方给的名字是Backdoor。

因此，我怎么控制释放对象的内容？我过去习惯浏览器中UAF，但是我不太熟悉这种利用和控制。我开始查看能从普通用户权限的Guest调用的RPC函数，我偶然发现了tools.capability.guest_temp_directory。我认为这很容易来发送特定大小的字符串以覆盖释放的内存块。结果如下：

[![](https://p4.ssl.qhimg.com/t014df5be727a3a8e19.png)](https://p4.ssl.qhimg.com/t014df5be727a3a8e19.png)

技术上，我们能通过发送任意的RPC请求来控制这个漏洞，未必是tools.capability.guest_temp_directory。这解决了最大的问题。

下面的问题是我是否能在指定位置放置一个ROP链和payload。我再次寻找我能在guest中调用的RPC函数。这次有一些选择。其中之一是unity.window.contents.start。看下反汇编的内容，一个全局变量中的一个引用：

[![](https://p1.ssl.qhimg.com/t01ad7c8ea0bfaf1b52.png)](https://p1.ssl.qhimg.com/t01ad7c8ea0bfaf1b52.png)

换句话说，如果我发送了一个unity.window.contents.start请求，我能知道这个请求的存储位置：vmware_vmx+0xb870f8。

因此，我再次使用下面的RPC调用触发崩溃：

[![](https://p0.ssl.qhimg.com/t0135ed9ea9ddf74dd7.png)](https://p0.ssl.qhimg.com/t0135ed9ea9ddf74dd7.png)

[![](https://p2.ssl.qhimg.com/t01a2d6da0a71e3bf59.png)](https://p2.ssl.qhimg.com/t01a2d6da0a71e3bf59.png)

正如你所见，@RDI指向了触发bug的请求。

此时的计划？

1. 发送一个带有设置RSP为RDI的ROP链的a unity.window.contents.start请求。

2. 触发释放

3. 使用另一个覆盖释放的对象。释放的对象应该包含vmware_vmx+0xb870f8的地址。

4. 使用包含ROP链的请求触发重用以得到RCE。

示意图如下，非常简单：

[![](https://p3.ssl.qhimg.com/t01c00d05aeec237f42.png)](https://p3.ssl.qhimg.com/t01c00d05aeec237f42.png)

代码执行的结果导致虚拟机客户端在hypervisor层执行代码：

[![](https://p5.ssl.qhimg.com/t01333d5fa2ba1dd554.png)](https://p5.ssl.qhimg.com/t01333d5fa2ba1dd554.png)

<br>

**0x03 总结**



当在Pwn2Own 2016引入了VMware类别时，我们没指望有提交的人。我们很少看见新类别的提交者，因为需要研究者花大量时间寻找bug并构造利用。然而，我们希望在2017年能看到。两个不同的队成功实现逃逸并执行任意代码。将来我将描述这些利用和技术的细节。不要让VMware中的UAF漏洞吓到你。他们非常有趣。每个RPCI都有它自己的故事和漏洞利用原语。


