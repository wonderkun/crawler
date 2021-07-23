> 原文链接: https://www.anquanke.com//post/id/230470 


# 从CPU到内核/到用户态全景分析异常分发机制——内核接管(番外篇)[2]


                                阅读量   
                                **170997**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01fd8b5a3784db1246.jpg)](https://p4.ssl.qhimg.com/t01fd8b5a3784db1246.jpg)



## 0、引言

继前一篇《从CPU到内核/到用户态全景分析异常分发机制——硬件基础及Hook》讲完硬件部分的内容之后，现在来看看OS如何和CPU“相亲相爱”合谋完成这一伟大壮举的。别高兴太早，这才是软件层面着手开始处理的万里长城第一步。好在第一步还是迈出去了，本篇将详细分析OS如何接管，如何管理异常的。注意我们这里分析的是基于Win10 16299版本，IA64架构的CPU。

整个系列涉及到的知识：

0、内核栈与用户栈隔离机制；

1、权限切换时，栈顶位置提供方式【有点拗口。。。】

2、CPU异常与中断概念与区别；

3、Intel架构中的IDT表与ISR；

4、Windows内核中内核异常分发；

5、Windows内核中用户态异常分发；

6、在调试器里查看PIC中断和APIC中断；

7、KPCR,KPRCB,KTRAP_FRAME；

 

## 1、关于KTRAP_FRAME的故事——系统调用/异常/中断的CONTEXT备份者

其实上一篇《 从CPU到内核/到用户态全景分析异常分发机制——内核接管[1]》中，关于KTRAP_FRAME的讲解很少，本不打算牵扯关于它的前因后果，但不写的话，有些内容又确实写不透。这里花点篇幅讲一下关于它的故事。KTRAP_FRAME可以分解为三个部分来看:

KTRAP_FRAME=K+TRAP+FRAME

1、K：Kernel;内核的意思;

2、TRAP:陷阱的意思，为啥叫陷阱呢？其实换个译法是“自陷“，这个名字的由来与Intel 的CPU有关，老的CPU从Ring3进入Ring0的方式中有一种称之为“陷阱门”的方式，即int xx,其中xx就是IDT表中的索引号，借助此，进入内核中。当然，IDT表中除了陷阱门之外还有中断门。其他门也可以存在，但CPU硬件解析的时候，回报告异常，因为存在并不意味着合法。

3、FRAME：帧，框架的意思，这个就是常规的调用帧的意思。在Ring3那，一个调用帧无非就是保存上写文的，这里也是一样，备份的是Ring3过来时，那边的CONTEXT。注意，不单单是Ring3进Ring0，也可以是Ring2进Ring0，只是Windows和Linux没有用罢了，但硬件却是有这个能力的。

耳听为许眼见为实，下边给大家简单看一下，一个常规的系统调用所涉及的底层逻辑：

[![](https://p4.ssl.qhimg.com/t015bacdc8eea23fe54.png)](https://p4.ssl.qhimg.com/t015bacdc8eea23fe54.png)

关于这个SharedUserData我也想说两句，其实这个结构在整个系统中只有一份——Ring3和Ring0的两份虚拟地址映射到同一个物理页上，但映射的时候，内核页表项中是可读可写的，而用户态是只读的，里边记录了一些常规的数据，其结构如下，只罗列了部分字段，框框里的这几个是在RTC时钟中断触发时，更新的，大家可以去逆向分析下，挺简单。可能需要点CMOS中端口操作的知识。【题外话，五六年前，做全局监控项目的时候，就需要这么一块内存，在所有进程中都要有，而且都要映射到同一块物理内存，而这块内存余下的部分正好满足我这个需要，我要榨干它，哈哈】

[![](https://p5.ssl.qhimg.com/t01b72612fa378b8001.png)](https://p5.ssl.qhimg.com/t01b72612fa378b8001.png)

好了回到第一张图。test指令就是用来判断0x308这个字段的值，该字段的含义如下：

[![](https://p4.ssl.qhimg.com/t01c429ed23364ca755.png)](https://p4.ssl.qhimg.com/t01c429ed23364ca755.png)

即判断当前CPU是否支持快速系统调用。支持的话直接走syscall完成系统调用，不支持的话就走老式的int 2e这种方式进内核。0x308处的这个值是在OS初始化时，通过CPUID指令获取到的。再继续拓展下，所谓的快速系统调用与常规的系统调用的区别在哪？

快速体现在什么地方？要理解这个问题，需要考虑这个问题：

int 2e进内核，CPU必然需要去寻址IDT表中的2e项，然后还要判断是不是合法的，DPL和CPL的规则是否满足，万一这个被置换到硬盘上去了，那是不是又要触发缺页异常，是不是又要涉及到异常的又一轮分发，再者OS又要读硬盘，此外，内核栈的栈顶指针有放在哪了。。。。。好多问题需要解决，这个过程及其漫长。而对于如此高频的内核调用来说，显然这是个可以被优化的点。SO，Intel就搞出来了个快速系统调用，当然AMD也不甘示弱，人间也搞了个Sysenter指令。Syscall配合上MSR寄存器，可谓牛逼哄哄。无人能敌。

eax中存放的时SSDT表的索引号，这个是很简单的东西，不是还有所谓的SSDT HOOK嘛，哈哈。弱智的玩意。到此打住。

前奏算是铺垫完了，下边正式进入内核中看看内核时如何配合ntdll!NtReadVirtualMemory来搞出这个nt!_KTRAP_FRAME的呢？接着看。大家可千万别以为Syscall进入内核直接就跑nt!NtReadVirtualMemory了，这是不可能的，理由很简单，CPU从来都不知道 nt!NtReadVirtualMemory的内核地址，那他又是如何执行的呢？那么意味着Syscall进入内核时执行的必然不是 nt!NtReadVirtualMemory了，那执行的是啥？好问题，问问CPU是怎么取得这个地址的吧，看下边操作：

[![](https://p1.ssl.qhimg.com/t01a8178f68278a6547.png)](https://p1.ssl.qhimg.com/t01a8178f68278a6547.png)

[![](https://p4.ssl.qhimg.com/t01e1407c2ef294319a.png)](https://p4.ssl.qhimg.com/t01e1407c2ef294319a.png)

先看下nt!KTRAP_FRAME的大小，如下：

[![](https://p0.ssl.qhimg.com/t01435fa1abc97f68e4.png)](https://p0.ssl.qhimg.com/t01435fa1abc97f68e4.png)

[![](https://p5.ssl.qhimg.com/t01597041b186951b8f.png)](https://p5.ssl.qhimg.com/t01597041b186951b8f.png)

被减去的0x158是上图中这个sub指令的操作，那还剩下0x38个大小的空间，哪里来补充呢？大家再仔细看看上图，sub rsp,158之前有6个push和一个sub rsp,8；6*8+8=56=0x38;对上了；无误了。

原来是在nt!KiSystemCall64ShadowCommon这个哥们中把这个nt!KTRAP_FRAME给构造好了。

 

## 2、关于APC的故事

写着写着发现既然都讲到这了，顺便就多讲点吧。先把系统调用的再收个尾，来看下下图：

[![](https://p1.ssl.qhimg.com/t01232b390e1115f0ce.png)](https://p1.ssl.qhimg.com/t01232b390e1115f0ce.png)

前边那两个je忽略掉即可，关键是jmp nt!KiSystemCall64ShadowCommon+0x218 (fffff802`30722245)这行指令，转过去看看都干了啥。

其他的我都不关心，我只关心nt!KiSystemServiceUser和最后一个jmp，如下图所示：

[![](https://p4.ssl.qhimg.com/t01efe73f844c0737cb.png)](https://p4.ssl.qhimg.com/t01efe73f844c0737cb.png)

nt!KiSystemServiceUser这个函数有点历史的味道，int 2e进来就是调用的它nt!KiSystemServiceUser，扯远了。现在关心最后一个jmp，继续跟进去看看。现在就不在Windbg里看了，转到IDA，更清爽。

[![](https://p5.ssl.qhimg.com/t01d2382f4ac2b7acf0.png)](https://p5.ssl.qhimg.com/t01d2382f4ac2b7acf0.png)

啥也不说了，所谓的用户态APC队列在这个地方就被处理了。所谓的异步过程调用的一个执行点就是系统调用结束的时候。

 

## 3、下篇再继续讲异常分发吧。

        丢！
