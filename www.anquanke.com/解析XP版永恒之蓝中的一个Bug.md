> 原文链接: https://www.anquanke.com//post/id/166943 


# 解析XP版永恒之蓝中的一个Bug


                                阅读量   
                                **258223**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者zerosum0x0，文章来源：zerosum0x0.blogspot.com
                                <br>原文地址：[https://zerosum0x0.blogspot.com/2018/11/dissecting-bug-in-eternalblue-client.html](https://zerosum0x0.blogspot.com/2018/11/dissecting-bug-in-eternalblue-client.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/dm/1024_512_/t018bf6de156faf7575.png)](https://p1.ssl.qhimg.com/dm/1024_512_/t018bf6de156faf7575.png)



## 0x00 背景

永恒之蓝漏洞刚出来时，我可以顺利搞定Windows 7，但在攻击Windows XP时我一直没有成功。我尝试了各种补丁和Service Pack的组合，但利用程序要么无法成功，要么会导致系统蓝屏。当时我没有深入研究，因为FuzzBunch（NSA泄露工具集）还有待探索许多点。

直到有一天，我在互联网上找到了一个Windows XP节点，我想尝试一下FuzzBunch。令人惊讶的是，在第一次尝试时，漏洞利用竟然成功了。

那么问题来了，为什么在我的“实验”环境中，漏洞利用无法成功，而实际环境中却可以？

这里先揭晓答案：在单核/多核/PAE CPU上NT/HAL的实现有所区别，因此导致FuzzBunch的XP系统攻击载荷无法在单核环境中使用。



## 0x01 多条利用链

大家需要知道一点，EternalBlue（永恒之蓝）有多个版本。网上已经有人详细分析了Windows 7内核的利用原理，我和[JennaMagius](https://zerosum0x0.blogspot.com/2017/06/eternalblue-exploit-analysis-and-port.html)以及[sleepya_](https://github.com/worawit/MS17-010)也研究过如何将其移植到Windows 10系统上。

然而对于Windows XP而言，FuzzBunch包含一个完全不同的利用链，不能使用完全相同的基本原语（比如该系统中并不存在SMB2以及SrvNet.sys）。我在DerbyCon 8.0演讲中深入讨论过这方面内容（参考[演示文稿](https://drive.google.com/file/d/1evqBqqNCTha7LxKNC9P85ql49qLbWZ_i/view)及[演讲视频](https://www.youtube.com/watch?v=ZHWidYrEgNM)）。

在Windows XP上，[KPCR](https://www.geoffchappell.com/studies/windows/km/ntoskrnl/structs/kpcr.htm)（Kernel Processor Control Region）启动处理器为静态结构，为了执行shellcode，我们需要覆盖[KPRCB](https://www.geoffchappell.com/studies/windows/km/ntoskrnl/structs/kprcb/index.htm).[PROCESSOR_POWER_STATE](https://www.geoffchappell.com/studies/windows/km/ntoskrnl/structs/processor_power_state.htm).IdleFunction的值。



## 0x02 载荷工作方式

事实证明，漏洞利用在实验环境中没有问题，出现问题的是FuzzBunch的攻击载荷。

ring 0 shellcode主要会执行如下几个步骤：

1、使用现在已弃用的 [KdVersionBlock](https://web.archive.org/web/20061110120809/http://www.rootkit.com/newsread.php?newsid=153)技巧获得`nt`及`hal`地址；

2、解析利用过程中需要用到的一些函数指针，如`hal!HalInitializeProcessor`；

3、恢复在漏洞利用过程中被破坏的KPCR/KPRCB启动处理器结构体；

4、运行[DoublePulsar](https://zerosum0x0.blogspot.com/2017/04/doublepulsar-initial-smb-backdoor-ring.html)，利用SMB服务安装后门；

5、恢复正常状态执行流程（`nt!PopProcessorIdle`）。

### <a class="reference-link" name="%E5%8D%95%E6%A0%B8%E5%88%86%E6%94%AF%E5%BC%82%E5%B8%B8"></a>单核分支异常

在`IdleFunction`分支以及`+0x170`进入shellcode处（经过XOR/Base64 shellcode解码器初始处理之后）设置硬件断点（hardware breakpoint）后，我们可以看到搭载多核处理器主机的执行分支与单核主机有所不同。

```
kd&gt; ba w 1 ffdffc50 "ba e 1 poi(ffdffc50)+0x170;g;"
```

多核主机上能找到指向`hal!HalInitializeProcessor`的一个函数指针。

[![](https://p5.ssl.qhimg.com/t01be7cefdd2ffacc93.png)](https://p5.ssl.qhimg.com/t01be7cefdd2ffacc93.png)

该函数可能用来清理处于半损坏状态的KPRCB。

单核主机上并没有找到`hal!HalInitializeProcessor`，`sub_547`返回的是`NULL`。攻击载荷无法继续运行，会尽可能将自身置零来清理现场，并且会设置ROP链来释放某些内存，恢复执行流程。

[![](https://p1.ssl.qhimg.com/t014fb8d90a4f419533.png)](https://p1.ssl.qhimg.com/t014fb8d90a4f419533.png)

注意：shellcode成功执行后，也会在首次安装DoublePulsar后执行此操作。



## 0x03 根源分析

shellcode函数`sub_547`无法在单核CPU主机上正确找到`hal!HalInitializeProcessor`的地址，因此会强制终止整个载荷执行过程。我们需要逆向分析shellcode函数，找到攻击载荷失败的确切原因。

这里内核shellcode中存在一个问题，没有考虑到Windows XP上所有可用的不同类型的NT内核可执行文件。更具体一点，多核处理器版的NT程序（比如`ntkrnlamp.exe`）可以正常工作，而单核版的（如`ntoskrnl.exe`）会出现问题。同样，`halmacpi.dll`与`halacpi.dll`之间也存在类似情况。

### <a class="reference-link" name="NT%E8%BF%B7%E5%B1%80"></a>NT迷局

`sub_547`所执行的第一个操作是获取NT程序所使用的HAL导入函数。 攻击载荷首先会读取NT程序中`0x1040`偏移地址来查找HAL函数。

在多核主机的Windows XP系统中，读取这个偏移地址能达到预期效果，shellcode能正确找到`hal!HalQueryRealTimeClock`函数：

[![](https://p2.ssl.qhimg.com/t01df37bfd781cfe803.png)](https://p2.ssl.qhimg.com/t01df37bfd781cfe803.png)

然而在单核主机上，程序中并没有HAL导入表，使用的是字符表：

[![](https://p5.ssl.qhimg.com/t01d3d1d4b895faf1a9.png)](https://p5.ssl.qhimg.com/t01d3d1d4b895faf1a9.png)

一开始我认为这应该是问题的根本原因，但实际上这只是一个幌子，因为这里存在修正码（correction code）的问题。shellcode会检查`0x1040`处的值是否是位于HAL范围内的一个地址。如果不满足条件，则会将该值减去`0xc40`，然后以`0x40`增量值在HAL范围内开始搜索相关地址，直到搜索地址再次到达`0x1040`为止。

[![](https://p4.ssl.qhimg.com/t017375fc3269929742.png)](https://p4.ssl.qhimg.com/t017375fc3269929742.png)

最终，单核版载荷会找到一个HAL函数，即`hal!HalCalibratePerformanceCounter`：

[![](https://p0.ssl.qhimg.com/t01e08217b2a42c95db.png)](https://p0.ssl.qhimg.com/t01e08217b2a42c95db.png)

目前一切操作都没有问题，可以看到Equation Group（方程式组织）在能够检测不同类型的XP NT程序。

### <a class="reference-link" name="HAL%E5%8F%AF%E5%8F%98%E5%AD%97%E8%8A%82%E8%A1%A8"></a>HAL可变字节表

现在shellcode已经找到了HAL中的一个函数，会尝试定位`hal!HalInitializeProcessor`。shellcode内置了一张表（位于`0x5e7`偏移处），表中包含1字节的长度字段，随后为预期的字节序列。shellcode会递增最开始发现的HAL函数地址，将新函数的前`0x20`字节与表中字节进行对比。

我们可以在多核版的HAL中找到待定位的5字节数据：

[![](https://p1.ssl.qhimg.com/t01ca5eb7a6c23aa51f.png)](https://p1.ssl.qhimg.com/t01ca5eb7a6c23aa51f.png)

然而，单核版的HAL情况有所不同：

[![](https://p1.ssl.qhimg.com/t018563e2757b943a4a.png)](https://p1.ssl.qhimg.com/t018563e2757b943a4a.png)

这里有一个类似的`mov`指令，但该指令并不是[movzx](https://stackoverflow.com/questions/43491737/compiler-generates-costly-movzx-instruction)指令。这个函数中并没有shellcode搜索的字节序列，因此shellcode发现不了这个函数。



## 0x04 总结

大家都知道，在Windows的不同版本和Service Pack中，想通过搜索字节序列来识别函数并不是一件靠谱的事情（这一点我们可以从Windows内核开发邮件列表上的各种争论一窥究竟）。从这个bug中，我们学到了一个教训：漏洞利用开发者必须考虑周全，注意NTOSKRNL和HAL在单核/多核/PAE上存在的差异。

非常奇怪的是，漏洞利用开发者会在攻击载荷中使用`KdVersionBlock`技巧和字节序列搜索技术来查找函数。在Windows 7载荷中，开发者会从KPCR IDT开始向前搜索内存，然后解析PE头，最终找到NT程序及其导出表，这是一种更可靠的处理方式。

我们也可以通过其他方法来找到这个HAL函数（比如通过HAL导出方式），也可以通过其他方法来清理被破坏的KPCR结构，这些工作留待读者来完成。

有间接证据表明，漏洞开发人员在2001年末开始开发FuzzBunch的主要框架。开发人员似乎只在多核处理器上编写并测试攻击载荷？也许这可能是一个线索，表明攻击者开发XP版漏洞利用程序的时间段。Windows XP于2001年10月25日发布，虽然在同一年IBM发明了第一款双核处理器（POWER4），但英特尔和AMD直到2004年和2005年才开始提供类似产品。

这也是ETERNAL系列漏洞利用演进过程的一个例子。方程式组织可能会重复使用相同的漏洞利用和攻击载荷原语，但会使用不同的方法来开发漏洞，这样如果一种方法无法成功，也可以通过漏洞利用多样化特点来最终完成攻击任务。研究这些漏洞利用样本后，我们可以从中学到许多深奥的Windows内核内部原理。
