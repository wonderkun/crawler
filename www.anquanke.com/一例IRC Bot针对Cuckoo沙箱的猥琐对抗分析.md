> 原文链接: https://www.anquanke.com//post/id/152631 


# 一例IRC Bot针对Cuckoo沙箱的猥琐对抗分析


                                阅读量   
                                **153611**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t010ed20ea4c978b9f3.jpg)](https://p4.ssl.qhimg.com/t010ed20ea4c978b9f3.jpg)

**作者：ManchurianClassmate**

最近我们通过蜜罐捕获到一例Windows平台的恶意样本，该样本是通过IRC服务器和C2进行通讯的一种IRC Bot。这种C2通讯方式的恶意程序已经屡见不鲜，但这次这个样本的特别之处在于它包含了非常猥琐的沙箱对抗机制，当样本正常运行的时候和普通的IRC Bot并没有什么-两样，但是当将它放在沙箱里面的时候会发现沙箱根本捕获不到任何恶意行为，从而逃过检测。



## 0x00 简单介绍一下Cuckoo

Cuckoo是目前使用得非常广泛的一种动态分析系统，其主要功能就是把恶意程序放到Cuckoo系统的虚拟机中，Cuckoo负责运行这些样本程序，并记录它们在虚拟环境中的行为，然后根据捕获到的行为去匹配一个指纹集（Signature），这个指纹集内定义了很多恶意程序的特征行为，比如在关键的位置写入注册表、或者在敏感目录有读写文件的行为等等，最后根据匹配到的指纹对该样本程序进行打分，以评估其危害等级。相比于静态文件特征，行为特征某些情况下更能反应真实的危害情况，而且在没有静态特征的情况下动态特征可能是唯一可行的检测方法。

因为Cuckoo是开源产品，所以被应用得非常广泛，也难免会有恶意程序专门针对Cuckoo设计对抗机制。



## 0x01 通常情况下如何对抗沙箱

### 针对虚拟机

因为反病毒沙箱大多都是基于虚拟机的，所以如果能保证样本在虚拟机环境中不执行那么就能大概率保证其在沙箱中不执行，针对沙箱的检测主要有如下几类：1）虚拟机的特殊进程/注册表信息，比如像VBoxTray.exe、VMwareTray.exe等；2）特殊的驱动程序，比如Virtualbox或VMware在Guest机器里面安装的驱动；3）硬件信息，比如网卡的mac地址，特定品牌虚拟机的网卡mac地址默认情况下大多都在一个特定范围内；4）指令执行环境，比如像LDT、GDT的地址范围等等。

### 针对检测时间

沙箱每一轮分析一个样本的时间是有限的，通常就几分钟，所以如果能让样本在这几分钟内不进入任何核心逻辑那么就可以避免被检测到。通常采取的做法有：1）利用Sleep函数，或和Sleep同等功能的延时函数；2）检测系统时间，通过系统的时间来延时；3）运行一些非常耗时的操作，比如一些特殊的数学算法以达到消耗时间的目的。

### 针对交互

这种做法是为了确保样本是在有人操作的计算机中启动的，比如可以检测鼠标的移动、故意弹窗让用户点击等等。

更详细的一些对抗姿势可以参考网上的一些文章：[https://www.52pojie.cn/thread-377352-1-1.html](https://www.52pojie.cn/thread-377352-1-1.html)



## 0x02 这个样本是怎么做的

而本文涉及的这个样本的沙箱对抗方式和以往已知的方式都不一样。这个在蜜罐中被发现的样本在Cuckoo中检测的分数只有3分，也就是在一个低危害等级上，和很多的正常程序的分值相当。

[![](https://p1.ssl.qhimg.com/t016e16f40cb032fe52.png)](https://p1.ssl.qhimg.com/t016e16f40cb032fe52.png)

而且Cuckoo也没有检测到该样本存在网络行为或其他敏感行为。但是当我们手动在虚拟机内运行该样本时发现该样本是存在网络行为的，也就是说该样本在沙箱中没有执行它真正的业务逻辑。首先来梳理一下这个样本在执行业务逻辑之前的流程：[![](https://p4.ssl.qhimg.com/t012140ed36fdb518a3.png)](https://p4.ssl.qhimg.com/t012140ed36fdb518a3.png)

让我们比较感兴趣的是拷贝自身然后重起新进程的过程：[![](https://p4.ssl.qhimg.com/t0160e149bb699f24f7.png)](https://p4.ssl.qhimg.com/t0160e149bb699f24f7.png)

首先是调用`GetModuleFileNameA`获取当前可执行文件的完整路径。

[![](https://p4.ssl.qhimg.com/t016c3dd15311135598.png)](https://p4.ssl.qhimg.com/t016c3dd15311135598.png)

然后又调用了`GetSystemDirectoryA`来获取系统目录（`C:\\Windows\system32`），然后比对是判断当前可执行文件是否在系统目录下，如果不在系统目录下则复制自身到系统目录，启动新文件，自身退出。当新进程启动，这个判断当前路径的逻辑就会走向另一个分支，开始真正的核心业务逻辑，比如发送上线包：

[![](https://p3.ssl.qhimg.com/t013d306ec7c3c9ce10.png)](https://p3.ssl.qhimg.com/t013d306ec7c3c9ce10.png)

在虚拟机中运行时实际行为也是如此，在第一次运行后复制自身创建新进程，开始执行业务逻辑，但在沙箱中捕获到行为就有点不一样了：[![](https://p2.ssl.qhimg.com/t01b6467cfe25034d15.png)](https://p2.ssl.qhimg.com/t01b6467cfe25034d15.png)

创建的子进程也是干了和父进程一样的事情，然后退出。并没有运行后面的核心业务逻辑，自然沙箱捕获不到后续的恶意行为。



## 0x03 细节原理

为啥相同的代码在不同的环境中会有完全不同的执行逻辑呢，看一下实际调试的情况就会发现运行到`strstr`函数时参数里面有一些猫腻：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0185e90a66f4caa341.jpg)

这个函数用来判断系统目录是否是当前可执行文件路径的子串。当前可执行文件路径里面System32的S是大写的，而通过`GetSystemDirectoryA`获取到的system32的s是小写的，这样即使当前样本是存在于系统目录下，比对结果也是否，从而无法进入核心逻辑。因为Windows系统不区分文件路径的大小写，所以System32和system32都是有效路径。但是Windows 的不同API对于路径大小写的处理策略并不统一，最坑的是微软官方文档里面并没有对这些细节的描述。`GetSystemDirectoryA`函数始终会返回小写的system32，但是`GetModuleFileNameA`返回值则取决于进程的命令行参数，通常情况下通过资源管理器启动时是大写的System32，但通过`CreateProcess`函数启动的话如果命令行是小写则获取到的路径也是小写。

在这个样本的例子里面母体通过`CreateProcess`启动新进程的时候传入的是小写的命令行参数，在正常运行的情况下这个比对路径的`strstr`函数没有任何问题，但是在沙箱中这个`strstr`的参数里面其中一个的system32的s变成了大写，从而导致了运行逻辑的不同。

为啥在沙箱里面这个system32的s就变成大写了呢？刨一下Cuckoo的代码就可以看到真正的原因了。首先简单介绍一下Cuckoo的工作原理，Cuckoo对样本行为的捕获依靠API Inline Hook，被测样本会被注入加载一个监控模块，当样本调用某个API函数时会被劫持到Cuckoo的模块内，这个模块除了常规的做log操作然后返回原函数外还会对某些API的上下文进行篡改，目的在于劫持某些API的执行逻辑。

本次案例的场景就是如此，当恶意样本释放了另外一个文件并创建新进程时Cuckoo需要把监控模块放入新进程的内存空间中才能继续捕获新进程的行为。于是对于`CreateProcess`等相关API有必要在hook中加入额外逻辑，Cuckoo在`CreateProcessInternalW`的hook中加入了如下的一些逻辑：

[![](https://p0.ssl.qhimg.com/t0136a1af7a80afb924.jpg)](https://p0.ssl.qhimg.com/t0136a1af7a80afb924.jpg)

监控模块会把新加入的代码会把新创建的进程的pid通过一个命名管道传给Cuckoo并且把新进程挂起，Cuckoo再向新创建的进程注入监控模块并解除挂起：

[![](https://p1.ssl.qhimg.com/t0134a3fa89e9f6d544.jpg)](https://p1.ssl.qhimg.com/t0134a3fa89e9f6d544.jpg)

在对`CreateProcessInternalW`的hook中Cuckoo的监控模块会调用`path_get_full_pathw`函数，这个函数在Cuckoo Monitor的src/misc.c中有定义（[https://github.com/cuckoosandbox/monitor/blob/master/src/misc.c#L503](https://github.com/cuckoosandbox/monitor/blob/master/src/misc.c#L503)）：[![](https://p1.ssl.qhimg.com/t01e65cbfdfa7cf8cec.jpg)](https://p1.ssl.qhimg.com/t01e65cbfdfa7cf8cec.jpg)

[![](https://p2.ssl.qhimg.com/t0131838893aa83ae3d.jpg)](https://p2.ssl.qhimg.com/t0131838893aa83ae3d.jpg)

其中又调用了`GetLongPathW`这个API，而这个API的特性恰好是永远会返回一个大写的路径（也就是System32）。从而在沙箱中虽然通过`CreateProcessA`传入了小写的命令行参数，但经过Cuckoo这么一处理，参数中的路径就又变成大写的了，这样一来对于这个样本而言那个对执行路径的判断就是一个永假的结果，自然在沙箱中就走不到后续的核心逻辑里面去：

[![](https://p2.ssl.qhimg.com/t01d6b5284187a8c46b.png)](https://p2.ssl.qhimg.com/t01d6b5284187a8c46b.png)

如此一来靠一个API在有hook和没有hook的情况下不同的行为表现来让样本在沙箱中有另外一套行为逻辑，从而逃避检测。



## 0x04 结论

以往的很多样本用来对抗沙箱采取的方式都是检测硬件信息，以此来判断是否是在虚拟机中运行，比如判断是否有Vmware、VirtualBox的驱动模块，或者硬盘大小，亦或者IDT、LDT、GDT所在的地址范围等。而本例所利用的特征是某些API在沙箱中所表现出的不同于正常环境的行为，当通过`CreateProcess`创建进程时，命令行中的路径的大小写会被沙箱的hook替换掉。某种意义上来说这也算是一种新颖的检测方式，同时也暴露了反病毒沙箱可能存在的另一类容易被人忽略的弱点。
