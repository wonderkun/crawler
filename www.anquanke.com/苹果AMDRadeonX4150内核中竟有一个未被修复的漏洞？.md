> 原文链接: https://www.anquanke.com//post/id/95878 


# 苹果AMDRadeonX4150内核中竟有一个未被修复的漏洞？


                                阅读量   
                                **130862**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者objective-see，文章来源：objective-see.com
                                <br>原文地址：[https://objective-see.com/blog/blog_0x27.html](https://objective-see.com/blog/blog_0x27.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0187b7566436856258.png)](https://p0.ssl.qhimg.com/t0187b7566436856258.png)

> 苹果的AMDRadeonX4150 kext竟然会触发一个内核漏洞？这又是为何？

## 写在前面的话

在2018年的1月21日，我在ShmooCon跟大家演讲了关于“OpenBSM审计”方面的内容，感兴趣的同学可以回顾一下我的演讲文稿【[传送门](http://shmoocon.org/speakers/#theugly)】。

[![](https://p1.ssl.qhimg.com/t01a4805eb44d06b0ee.png)](https://p1.ssl.qhimg.com/t01a4805eb44d06b0ee.png)

我当时在准备演讲内容的过程中，其实也就是期间休息的时候，我对自己的New MacBook进行了一番安全分析。而在几分钟之后，我的苹果笔记本竟然奇迹般地崩溃了。这就非常奇怪了，因为我只是在用户模式下进行的操作。但是这确实让我非常兴奋，因为谁不想发现一个macOS的内核漏洞呢？

那么在这篇文章中，我将会跟大家分析内核panic报告，并尝试找到引发内核panic的直接原因以及错误指令。从表面上看，可能这个漏洞并不能向我们展示出非常有价值的安全问题，从某种程度上来说这还算是幸运的了。但对于某些比较精通内核安全以及显卡kext的人来说，他们也许可以利用这个漏洞来实现更多的东西。无论怎样，我希望在这篇文章中可以通过分析内核panic报告来给大家提供一些有价值的思路。



## 分析内核panic情况

首先，我们一起来了解一下目标设备的系统信息：

##### macOS版本：10.13.2

```
$ uname -a

  Darwin Patricks-MacBook-Pro.local 17.3.0 Darwin Kernel Version 17.3.0:

  root:xnu-4570.31.3~1/RELEASE_X86_64 x86_6
```

##### 内核panic报告：

```
$ /Library/Logs/DiagnosticReports/Kernel_2018-01-15-185538_Patricks-MacBook-Pro.panic
```

 内核panic报告的部分内容如下所示，如需获取完整的内核panic报告，请点击【[这里](https://objective-see.com/downloads/Kernel_%20AMDRadeonX4150.panic)】：

```
$ less Kernel_2018-01-15-185538_Patricks-MacBook-Pro.panic

 

  *** Panic Report ***

  panic(cpu 6 caller 0xffffff8008b6f2e9): Kernel trap at 0xffffff7f8c7ba8b1, type 14=page fault

 

  registers:

  CR0: 0x000000008001003b, CR2: 0xffffff80639b8000, CR3: 0x0000000022202000, CR4: 0x00000000003627e0

  RAX: 0x0000000000000564, RBX: 0x0000000000000564, RCX: 0x0000000000000020, RDX: 0x000000000000002a

  RSP: 0xffffff92354ebc80, RBP: 0xffffff92354ebce0, RSI: 0x00000000000fbeab, RDI: 0xffffff92487b9154

  R8:  0x0000000000000000, R9:  0x0000000000000010, R10: 0x0000000000000010, R11: 0x0000000000000000

  R12: 0xffffff80639b6a70, R13: 0xffffff92354ebdc0, R14: 0xffffff92354ebdd4, R15: 0x0000000000000000

  RFL: 0x0000000000010297, RIP: 0xffffff7f8c7ba8b1, CS:  0x0000000000000008, SS:  0x0000000000000010

  Fault CR2: 0xffffff80639b8000, Error code: 0x0000000000000000, Fault CPU: 0x6, PL: 0, VF: 1

 

  Backtrace (CPU 6), Frame : Return Address

  0xffffff92354eb730 : 0xffffff8008a505f6

  0xffffff92354eb780 : 0xffffff8008b7d604

  0xffffff92354eb7c0 : 0xffffff8008b6f0f9

  0xffffff92354eb840 : 0xffffff8008a02120

  ....

 

  Kernel Extensions in backtrace:

  com.apple.iokit.IOAcceleratorFamily2(376.6) @0xffffff7f8b2b0000-&gt;0xffffff7f8b345fff

  com.apple.kext.AMDRadeonX4150(1.6) @0xffffff7f8c7b4000-&gt;0xffffff7f8cf20fff

 

  BSD process name corresponding to current thread: kernel_task

 

  Mac OS version:

  17C88

 

  Kernel version:

  Darwin Kernel Version 17.3.0: Thu Nov  9 18:09:22 PST 2017; root:xnu-4570.31.3~1/RELEASE_X86_64

  Kernel slide:     0x0000000008600000
```

没错，panic报告中确实包含了很多信息，但是这些信息就是可以帮助我们立刻定位到内核崩溃原因的必要信息。

我们先从报告的第二行内容（第一行是标题）开始分析：

```
panic(cpu 6 caller 0xffffff8008b6f2e9): Kernel trap at 0xffffff7f8c7ba8b1, type 14=page fault
```

内核panic报告的第二行信息告诉我们，系统之所以会出现panic，主要是由一个页面错误（‘type 14=page fault’）所导致的。而这种错误通常代表的是一次无效的读取操作或者是向内存中未映射页面的写入操作，这部分内容我们待会儿再讲。请大家先注意报告中RIP的值，这个寄存器（即程序计数器）中存储的就是错误指令的地址：0xffffff7f8c7ba8b1。

顺着这条信息往下分析，我们就会发现内核panic报告中包含了访问和触发页面错误的内存地址：0xffffff80639b8000。

```
Fault CR2: 0xffffff80639b8000, Error code: 0x0000000000000000, Fault CPU: 0x6 ...
```

除此之外，Panic报告中还包含了回溯信息（backtrace），这样一来我们就可以跟踪方法调用或函数调用的顺序。并进一步确定错误指令的执行情况：

```
Backtrace (CPU 6), Frame : Return Address

  0xffffff92354eb730 : 0xffffff8008a505f6

  0xffffff92354eb780 : 0xffffff8008b7d604

  0xffffff92354eb7c0 : 0xffffff8008b6f0f9

  0xffffff92354eb840 : 0xffffff8008a02120

  0xffffff92354eb860 : 0xffffff8008a5002c

  0xffffff92354eb990 : 0xffffff8008a4fdac

  0xffffff92354eb9f0 : 0xffffff8008b6f2e9

  0xffffff92354ebb70 : 0xffffff8008a02120

  0xffffff92354ebb90 : 0xffffff7f8c7ba8b1

  0xffffff92354ebce0 : 0xffffff7f8c7ba40f

  0xffffff92354ebd60 : 0xffffff7f8c7b85e8

  0xffffff92354ebda0 : 0xffffff7f8c7b9db2

  0xffffff92354ebe00 : 0xffffff7f8b2b3873

  0xffffff92354ebe50 : 0xffffff7f8b2bd473

  0xffffff92354ebe90 : 0xffffff7f8b2bcc7d

  0xffffff92354ebed0 : 0xffffff8009091395

  0xffffff92354ebf30 : 0xffffff800908fba2

  0xffffff92354ebf70 : 0xffffff800908f1dc

  0xffffff92354ebfa0 : 0xffffff8008a014f7
```

一旦我们确定了这些地址所属的kext，我们就能够映射出实际被调用的函数名称。根据回溯信息所提供的内容，panic报告中还包含了内核扩展以及相应的加载地址。这也就意味着，上述地址中的某一条很可能包含了触发页面错误并导致内核panic的指令，大致内容如下：

<!-- [if !supportLists]-->1.    <!--[endif]-->kext: com.apple.iokit.IOAcceleratorFamily2

地址：0xffffff7f8b2b0000

<!-- [if !supportLists]-->2.    <!--[endif]-->kext: com.apple.kext.AMDRadeonX4150

地址：0xffffff7f8c7b4000

在panic报告的结尾部分还包含一些“看似无用“的元数据（对我们来说可能没多大意义），例如内核版本信息等等。但是，其中的Kernel Slide(0x0000000008600000)是比较重要的，因为它包含了内核镜像信息以及转移到内存中的数据。

那么接下来，我们总结一下我们从内核panic报告中收集到的数据：

<!-- [if !supportLists]-->1.    <!--[endif]-->内核panic是由一个页面错误访问内存地址0xffffff80639b8000所导致的。

<!-- [if !supportLists]-->2.    <!--[endif]-->触发页面错误的指令其地址（存储在RIP寄存器中）为：0xffffff7f8c7ba8b1。

<!-- [if !supportLists]-->3.    <!--[endif]-->回溯信息中包含了com.apple.iokit.IOAcceleratorFamily2和com.apple.kext.AMDRadeonX4150这两个kext。

<!-- [if !supportLists]-->4.    <!--[endif]-->Kernel slide：0x0000000008600000。

为了进一步确定触发内核panic的指令，我们需要对kext进行分析。

首先我们从panic报告底部最后那条地址开始着手，将其从/System/Library/Kernels/kernel加载进Hoppe反汇编工具之中。由于kASLR会将内核转移进内存之中，我们需要在Hopper中修改镜像的基地址。

点击“Modify“（修改）按钮，然后点击”Change File Base Address“（修改文件基地址）。输入panic报告中kASLR slide的值（0x0000000008600000），最后再在这个地址值上加0x100000，得到最终的地址(0xffffff8008700000)：

[![](https://p3.ssl.qhimg.com/t01533d4541ec8210e0.png)](https://p3.ssl.qhimg.com/t01533d4541ec8210e0.png)

重新设置好内核镜像的地址之后，按下“G“，并输入回溯信息中的最后一个地址：0xffffff8008a014f7。

[![](https://p5.ssl.qhimg.com/t011a79114c73c98f51.png)](https://p5.ssl.qhimg.com/t011a79114c73c98f51.png)

我们可以从下列反汇编信息中看到，这个地址映射出的指令调用情况如下所示：

[![](https://p2.ssl.qhimg.com/t01b55dad9fcb2f3f41.png)](https://p2.ssl.qhimg.com/t01b55dad9fcb2f3f41.png)

当CPU遇到上述这些调用函数之后，它会在栈中保存下一条指令的地址。这样一来，CPU就可以知道指令的调用情况以及返回值信息。当内核在生成panic报告时，它会通过遍历栈并寻找这些存储的地址来生成回溯信息。

因此，当我们遇到例如0xffffff8008a014f7的回溯地址时，调用指令会立刻处理这个地址，而这个地址指向的就是存在安全问题的指令。比如说，当我们调用rcx（地址0xffffff8008a014f5）时，便会让内核发生崩溃。

接下来，我们继续分析回溯信息，并得到了最终导致内核崩溃的命令调用序列：

<!-- [if !supportLists]-->1.    <!--[endif]-->kernel.call_continuation()

0xffffff8008a014f5 call rcx

<!-- [if !supportLists]-->2.    <!--[endif]-->kernel.IOWorkLoop::threadMain()

0xffffff800908f1d6 call qword [rax+0x1a8]

<!-- [if !supportLists]-->3.    <!--[endif]-->kernel.IOWorkLoop::runEventSources()

0xffffff800908fb9c call qword [rax+0x120]

<!-- [if !supportLists]-->4.    <!--[endif]-->kernel.IOInterruptEventSource::checkForWork()

0xffffff8009091392 call r11

<!-- [if !supportLists]-->5.    <!--[endif]-->com.apple.iokit.IOAcceleratorFamily2.IOAccelEventMachine2::hardwareErrorEvent()

0xffffff7f8b2bcc78 call IOAccelEventMachine2::restart_channel()

<!-- [if !supportLists]-->6.    <!--[endif]-->com.apple.iokit.IOAcceleratorFamily2.IOAccelEventMachine2::restart_channel()

0xffffff7f8b2bd46d call qword [rax+0x160]

<!-- [if !supportLists]-->7.    <!--[endif]-->com.apple.iokit.IOAcceleratorFamily2.IOAccelFIFOChannel2::restart()

0xffffff7f8b2b386d call qword [rax+0x208]

<!-- [if !supportLists]-->8.    <!--[endif]-->com.apple.kext.AMDRadeonX4150.AMDRadeonX4150_AMDAccelChannel::getHardwareDiagnosisReport()

0xffffff7f8c7b9dac call qword [rax+0xb00]

<!-- [if !supportLists]-->9.    <!--[endif]-->com.apple.kext.AMDRadeonX4150.AMDRadeonX4150_AMDGraphicsAccelerator::writeDiagnosisReport()

0xffffff7f8c7b85e2 call qword [rax+0x258]

<!-- [if !supportLists]-->10.  <!--[endif]-->com.apple.kext.AMDRadeonX4150.AMDRadeonX4150_AMDAccelChannel::writeDiagnosisReport()

0xffffff7f8c7ba40a call

AMDRadeonX4150_AMDAccelChannel::writePendingCommandInfo

<!-- [if !supportLists]-->11.  <!--[endif]-->com.apple.kext.AMDRadeonX4150.AMDRadeonX4150_AMDAccelChannel::writePendingCommandInfoDiagnosisReport()

0xffffff7f8c7ba8b1 mov r8d, dword [r12+rax*4]

<!-- [if !supportLists]-->12.  <!--[endif]-->kernel.hndl_alltraps()

0xffffff8008a0211b call _kernel_trap

这样一来，我们就能够更加清楚地了解到导致内核panic的错误指令情况了。

经过了一系列分析之后，我们还发现了一个内核线程，它会调用com.apple.iokit.IOAcceleratorFamily2 kext来处理一个与硬件有关的错误。

这个kext（即com.apple.iokit.IOAcceleratorFamily2）会调用restart_channel方法。而这个方法又会调用一个特定的kext，即com.apple.kext.AMDRadeonX4150。而这个kext就是我笔记本电脑AMD Radeon Pro560显卡的接口：

[![](https://objective-see.com/images/blog/blog_0x27/graphics.png)](https://objective-see.com/images/blog/blog_0x27/graphics.png)

在panic报告生成的过程中，系统还会生成一份硬件诊断报告。说得准确一点，此时com.apple.kext.AMDRadeonX4150会调用它的AMDRadeonX4150_AMDAccelChannel::writeDiagnosisReport方法，而这个方法又会调用writePendingCommandInfoDiagnosisReport方法。

聪明的同学可能已经注意到了回溯信息中的第十一条地址（转移指令）：

```
0xffffff7f8c7ba8b1 mov r8d, dword [r12+rax*4]
```

除此之外，我们还发现这个地址0xffffff7f8c7ba8b1同样存在于苹果的com.apple.kext.AMDRadeonX4150 kext之中，而这个值正好跟内核panic报告中RIP寄存器所存储的值相匹配。需要注意的是，这个转移指令正好就是引起内核panic的指令。

[![](https://p2.ssl.qhimg.com/t012d04a7b6317e9abf.png)](https://p2.ssl.qhimg.com/t012d04a7b6317e9abf.png)

那么现在，我们已经找到了导致页面错误的指令了（以及相应的路径令牌）。在对这个指令进行深入分析之后，我们可以看到指令会通过向基址寄存器添加某些值（RAX*4）来计算出地址（R12）。接下来，R8d会间接引用这个地址。由于内核panic报告中包含了这个错误指令在运行时寄存器中的值，我们就可以重新计算出这个地址：

```
$ less Kernel_2018-01-15-185538_Patricks-MacBook-Pro.panic

 

  registers:

  CR0: 0x000000008001003b, CR2: 0xffffff80639b8000, ...

  RAX: 0x0000000000000564, RBX: 0x0000000000000564, ...

  RSP: 0xffffff92354ebc80, RBP: 0xffffff92354ebce0, ...

  R8:  0x0000000000000000, R9:  0x0000000000000010, ...

  R12: 0xffffff80639b6a70, R13: 0xffffff92354ebdc0, ...

  RFL: 0x0000000000010297, RIP: 0xffffff7f8c7ba8b1, ...



 



mov r8d, dword [r12+rax*4]

 

R12: 0xffffff80639b6a70

RAX: 0x0000000000000564

 

R12 + RAX*4 = 0xffffff80639b6a70 + (0x564 * 4) = 0xffffff80639b8000
```

重新计算出的地址值0xffffff80639b8000是不是看着有些眼熟？没错，这个地址就是当程序访问并触发页面错误时，内核panic报告中内存地址的值：

```
Fault CR2: 0xffffff80639b8000, Error code: 0x0000000000000000, Fault CPU: 0x6 ...
```

根据我们的推测，地址0xffffff80639b8000很可能就是未映射页面的起始地址。因此，当com.apple.kext.AMDRadeonX4150 kext中的mov指令尝试从未映射的地址中读取数据时，就会触发页面错误并导致系统进入panic状态。

所以说，我们现在已经知道了触发内核panic的准确原因以及指令了。但是，我们现在还不知道为什么会出现这样的情况，也就是说，我现在还不确定为什么系统会计算出一个无效的地址。深入研究之后，我总结出了现在需要回答的问题：

<!-- [if !supportLists]-->1.    <!--[endif]-->是因为基地址指针无效还是崩溃了？

<!-- [if !supportLists]-->2.    <!--[endif]-->或者说，是因为偏移量寄存器RAX存储的是一个无效的偏移量（太大）？

<!-- [if !supportLists]-->3.    <!--[endif]-->还是说，这只是一种随机出现的硬件问题（或是其他的某种原因）？

众所周知，图形驱动程序的逆向分析工作极其复杂，需要花费相当多的时间和努力才能够对其“略知一二“。但是我认为，我们也许可以从这里入手来尝试防止这种内核panic出现。比如说，我们也许可以通过确保偏移量寄存器RAX的值在一个合理区间（缓冲区大小）来解决这个问题。

在本文所分析的例子中，内核panic是因为计算出的地址值0xffffff80639b8000指向了内核内存中未映射的页面所导致的。但是，如果这个地址（有效地址）指向的是映射页面呢？首先，内核panic将不会在发生；其次，我们也许能够将内核内存信息泄露到用户模式下，并实现kASLR绕过。

还记得吗？之前存在问题的指令会尝试间接引用R8寄存器中的dword值，而调用了几个函数之后，它还会调用snprintf函数：

```
ffffff7f8c7ba8af   mov        eax, eax

  ffffff7f8c7ba8b1   mov        r8d, dword [r12+rax*4] ;faulting instruction

  ffffff7f8c7ba8b5   xor        eax, eax

  ffffff7f8c7ba8b7   lea        rdx, qword [aC08x]     ; "%c%08x"

  ffffff7f8c7ba8be   call       0xffffff7f198091e8     ;  snprintf
```

snprintf的标准函数形式以及调用参数如下（R8是第五个参数）：

```
int snprintf(char *str, size_t size, const char *format, ...);
```

由于指令会使用格式化字符串“%c%08x”来调用snprintf函数，而第五个参数将会映射到“%08x“。这样一来，R8寄存器中的整形值将会被写入到缓冲区中。因此，浙江有可能导致将随机内存数据泄露到诊断报告之中。



## 总结

在这篇文章中，我们对macOS的一份内核panic报告进行了分析，并研究了导致panic出现的原因。简而言之，当com.apple.kext.AMDRadeonX4150 kext尝试访问一个指向未映射页面的内存地址时，便会触发内存panic。

不过令人沮丧的是，目前为止苹果还没有为macOS推送最新版本的内核扩展补丁。
