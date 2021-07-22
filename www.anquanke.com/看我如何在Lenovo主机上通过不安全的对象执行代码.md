> 原文链接: https://www.anquanke.com//post/id/90172 


# 看我如何在Lenovo主机上通过不安全的对象执行代码


                                阅读量   
                                **67412**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者riscybusiness，文章来源：riscy.business
                                <br>原文地址：[http://riscy.business/2017/12/lenovos-unsecured-objects/](http://riscy.business/2017/12/lenovos-unsecured-objects/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0158ae4cdb399191e8.jpg)](https://p5.ssl.qhimg.com/t0158ae4cdb399191e8.jpg)

## 一、前言

不久之前，Alex Ionescu在一次演讲中介绍了[不安全共享内存对象](http://www.alex-ionescu.com/infiltrate2015.pdf)方面内容。这种方法貌似可以应用于攻击场景，因此我在自己的Lenovo主机上运行[WinObj](https://docs.microsoft.com/en-us/sysinternals/downloads/winobj)工具，查找主机中是否存在不受ACL限制的区段对象（section object）。

> 备注：**Section Object指的是不同应用之间可以共享的内存映射，如果某个section object不安全，那么第三方应用程序就可以读写这个section object，给用户带来安全风险。**
 

## 二、利用过程

我的Lenovo主机中包含名为“SynTPAPIMemMap”的一个内存映射。使用WinObj检查后，我们并没有看到任何ACL限制，因此可以将其作为目标来开始我们的研究。

[![](https://p2.ssl.qhimg.com/t01352ae33606eb3445.png)](https://p2.ssl.qhimg.com/t01352ae33606eb3445.png)

这个内存映射的所有者为`SynTPEnh.exe`，**这是Lenovo的触摸板程序，在系统启动时SynTPEnh服务会启动这个程序**。

[![](https://p2.ssl.qhimg.com/t0136ff282029662d2f.png)](https://p2.ssl.qhimg.com/t0136ff282029662d2f.png)

在IDA中检查`SynTPEnh.exe`的某个`.dll`后，我们发现该程序负责创建并映射这个内存映射。

[![](https://p1.ssl.qhimg.com/t017ffcb8db1e267e8f.png)](https://p1.ssl.qhimg.com/t017ffcb8db1e267e8f.png)

**由于任何应用程序都可以读写这个映射，因此攻击者只需要检查这个内存映射的所有引用，寻找最合适的攻击点即可。**其中，我找到了最有可能被攻击的一处引用，即dll导出函数：`RegisterPluginW`，每当用户“点击”或者接触触摸板时，程序都会调用这个函数。

设置内存断点后，我发现当程序调用`RegisterPluginW`时，该函数会迭代遍历整个内存映射。负责这一过程的为其内部的某个函数（我称之为`RespawnProc`），如下图所示：

[![](https://p4.ssl.qhimg.com/t0120960451e454a304.png)](https://p4.ssl.qhimg.com/t0120960451e454a304.png)

分析`RespawnProc`函数后，我发现该函数有可能会调用`CreateProcess`函数，更令人难以置信的是，`CreateProcess`函数所使用的`cmdLine`参数直接来自于内存映射中（`rbx`寄存器），因此我们可以控制这个参数。

[![](https://p4.ssl.qhimg.com/t015715beff697706f4.png)](https://p4.ssl.qhimg.com/t015715beff697706f4.png)

为了控制程序执行流程，我们需要让`WindowCheck`函数返回0。看一下我们怎么做到这一点。

`WindowCheck`函数内部如下所示：

[![](https://p5.ssl.qhimg.com/t011859c4bc6b8544f6.png)](https://p5.ssl.qhimg.com/t011859c4bc6b8544f6.png)

分析这个函数后，我们发现该函数同样依赖于这个不安全的内存映射。该函数使用了一个缓冲区来存放句柄及进程ID值，我们可以往该缓冲区中写入无效的句柄以及无效的进程ID，使该函数进入运行失败分支。这种机制很可能是一种重启机制，使该窗口进程异常后能够再次启动。然而不幸的是程序使用不安全的内存映射来存放这些数据。为了使程序按照我们设计的路线来运行，我们需要理解该缓冲区的格式及其内容。

稍微逆向分析这个内存映射后，我发现该缓冲区实际上是一个数组，其中至少包含20个TPAPI对象。内存布局如下图所示，红色高亮部分为其中一个TPAPI对象，还有其他一些重要成员也标注在图中。

[![](https://p2.ssl.qhimg.com/t014df814b47933cf79.png)](https://p2.ssl.qhimg.com/t014df814b47933cf79.png)

上图中蓝色部分为cmdline成员，也是`CreateProcess`所使用的一个参数。利用过程应该很简单，把cmdLine指向我希望运行的进程，然后设置无效的PID以及（或者）Windows Handle成员，迫使`WindowCheck`执行失败即可。唯一需要担心的是不要在第一个TPAPI对象上执行这种操作，因为用户每次触摸或点击触摸板时，程序会遍历所有这些对象，而我并不希望主机上弹出27个`calc.exe`窗口。

比如，我们可以使用如下这段代码来触发命令执行场景：

[![](https://p1.ssl.qhimg.com/t01d1a7fb806dc7d0f1.png)](https://p1.ssl.qhimg.com/t01d1a7fb806dc7d0f1.png)

执行这段代码后，一旦我使用触摸板移动鼠标，SynTPEnh进程就会调用`calc.exe`，后者会继承SynTPEnh进程的权限。

[![](https://p0.ssl.qhimg.com/t01f3f9a71678bf388c.png)](https://p0.ssl.qhimg.com/t01f3f9a71678bf388c.png)



## 三、总结

如上文所述，在这种场景下，**任何程序都可以在Lenovo主机上往这个section object写入数据，以当前用户账户权限执行代码**，这种方法可以用于权限提升场景（取决于进程所处的上下文环境），也可以用于执行流程转移场景，比如，如果你不希望程序作为MS Word的子进程来运行，你就可以使用这种方法。
