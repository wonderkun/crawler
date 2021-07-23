> 原文链接: https://www.anquanke.com//post/id/85009 


# 【漏洞分析】iPhone 播放视频自动关机“奇葩”漏洞成因分析


                                阅读量   
                                **131894**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01f0ed4782e43bfd93.jpg)](https://p1.ssl.qhimg.com/t01f0ed4782e43bfd93.jpg)





**作者：**[**Proteas@****360 Nirvan Team**](http://bobao.360.cn/member/contribute?uid=2577449118)

**预估稿费：500RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



**传送门**

[**iOS又曝新漏洞，播放特定视频导致自动关机（含演示视频）**](http://bobao.360.cn/news/detail/3774.html)



**一、说明**

23号早上主要的网络媒体都发了一条新闻[[iOS又曝新漏洞，播放特定视频导致自动关机（含演示视频））]](http://bobao.360.cn/news/detail/3774.html)，主要内容是：苹果iOS设备又被爆出新漏洞，播放一段特定的MP4视频，将导致设备重启。我们团队在第一时间拿到了视频样本（a92aaf9dc6307e5387cb3206e6faed48），并在设备上做了验证，发现播放视频确实会引起设备重启，并做了简单的技术层面的分析，本文主要介绍了我们分析的步骤与结论。



**二、分析步骤**

**1、观察现象**

首先以某种方式播放问题视频，我们采用的方式是写一个小程序。同时，我们知道 mediaserverd 进程是负责视频播放的后台服务。因此，在播放视频的过程中我们观察 mediaserverd 进程的 CPU 及内存的使用情况：

[![](https://p5.ssl.qhimg.com/t016670fab02f202c9f.png)](https://p5.ssl.qhimg.com/t016670fab02f202c9f.png)

如上图，我们观察到在播放问题视频时，mediaserverd 的内存占用比较稳定，因此排除内存泄露。但是，CPU 占用非常高，初步猜测：问题视频会造成 mediaserverd 进程死循环。

另外，我们观察到在 CPU 接近 100% 的情况下，过一段时间 iOS 会崩溃，重启后我们可以拿到 Panic Log，主要内容如下：



```
`{`
  "build" : "iPhone OS 9.0.2 (13A452)",
  "product" : "iPhone7,1",
  …
  "date" : "2016-11-23 10:29:22.22 +0800",
  "panicString" : "Debugger message: WDT timeout",
```

iOS 崩溃的原因是 Watchdog 超时，基本验证了我们之前的猜测。

**2、确定畸形视频范围**

问题视频的总时长为5.01秒，每秒 26 帧，但是在播放前面几秒的视频时并不会造成 iOS 崩溃。为了便于后期分析，我们首先需要确认视频中哪些部分是畸形的。结合之前的观察我们知道：视频中畸形的数据在视频中的位置比较靠后，因此我们从后往前对视频进行裁剪，即：首先取出 [4.01, 5.01] 范围内的视频，然后播放、测试。我们发现 [4.01, 5.01] 这个范围内的视频就会造成 iOS 崩溃。之后，我们又取出 [0.00, 4.01] 这个范围内的视频进行播放、测试，发现这段范围内的视频并不会造成 iOS 崩溃。

最后，我们确认视频中的畸形数据存在于原始视频的最后 1 秒是中，即“秒拍”添加的片尾中：

[![](https://p2.ssl.qhimg.com/t01c0dbd9636ba6c12b.png)](https://p2.ssl.qhimg.com/t01c0dbd9636ba6c12b.png)

注：不代表“秒拍”添加的所有片尾都有问题。

**3、分析 iOS 崩溃日志**

mediaserverd 进程 CPU 占用率 100%，问题代码可能在用户空间，也可能存在于内核空间。如果用户空间的代码存在问题，那么 mediaserverd 进程会被杀掉，但是我们观察到直至设备重启前 mediaserverd 进程一直存在。因此，问题代码很可能出在内核空间。

分析内核空间的问题，目前我们手里最直接的信息就是内核的崩溃日志，而内核的崩溃日志中的最有价值的部分就是崩溃线程的调用栈：



```
Kernel slide:     0x000000000ec00000
Kernel text base: 0xffffff8012c04000
Frame-01: lr: 0xffffff8012d04714  fp: 0xffffff8013120a70
Frame-02: lr: 0xffffff801328b474  fp: 0xffffff8013120f40
Frame-03: lr: 0xffffff80142c308c  fp: 0xffffff8013120fd0
Frame-04: lr: 0xffffff8013055f80  fp: 0xffffff8013120fe0
Frame-05: lr: 0xffffff8012cfb26c  fp: 0xffffff8013120ff0
Frame-06: lr: 0xffffff8012c3576c  fp: 0xffffff80008ab2a0
Frame-07: lr: 0xffffff8012f79d50  fp: 0xffffff80008ab2c0
Frame-08: lr: 0xffffff80143d69c4  fp: 0xffffff80008ab3f0
Frame-09: lr: 0xffffff80143e7cfc  fp: 0xffffff80008ab420
Frame-10: lr: 0xffffff80143e8070  fp: 0xffffff80008ab450
Frame-11: lr: 0xffffff80143e9044  fp: 0xffffff80008ab480
Frame-12: lr: 0xffffff80143e71fc  fp: 0xffffff80008ab4c0
Frame-13: lr: 0xffffff80143e7448  fp: 0xffffff80008ab520
Frame-14: lr: 0xffffff80143f1348  fp: 0xffffff80008ab550
Frame-15: lr: 0xffffff80143dec50  fp: 0xffffff80008ab680
Frame-16: lr: 0xffffff80143dd59c  fp: 0xffffff80008ab690
Frame-17: lr: 0xffffff8013061ee0  fp: 0xffffff80008ab820
Frame-18: lr: 0xffffff8012cdaa64  fp: 0xffffff80008ab950
Frame-19: lr: 0xffffff8012c18460  fp: 0xffffff80008aba30
Frame-20: lr: 0xffffff8012c2634c  fp: 0xffffff80008abad0
Frame-21: lr: 0xffffff8012cfd80c  fp: 0xffffff80008abba0
Frame-22: lr: 0xffffff8012cfc0f4  fp: 0xffffff80008abc90
Frame-23: lr: 0xffffff8012cfb1f0  fp: 0xffffff80008abca0
Frame-24: lr: 0x0000000198d34c30  fp: 0x0000000000000000
```

调用栈信息如上，我们首先需要把 lr 的地址映射到具体的内核中。由于，调用栈比较长，这里我们只是给出几个主要的栈帧信息：

Frame-1：保存崩溃信息并重启设备

[![](https://p2.ssl.qhimg.com/t0129b71494796604fe.png)](https://p2.ssl.qhimg.com/t0129b71494796604fe.png)

Frame-8: 输出错误信息，同时可以确定出问题的内核模块为 AppleVXD393

[![](https://p4.ssl.qhimg.com/t01c596e7ba96de0a52.png)](https://p4.ssl.qhimg.com/t01c596e7ba96de0a52.png)

**4、寻找死循环**

我们之前猜测内核中可能存在死循环，现在我们遍历崩溃时的调用栈，寻找死循环具体在什么位置。最后我们发现死循环应该在 Frame-14 中，其主要的伪代码如下：



```
__int64 __fastcall PRTS_AppleVXD393_Panic_Frame_14(__int64 a1, __int64 a2, int a3)
`{`
  ...
  for ( i = 1; ; ++i )
  `{`
    ...
    v17 = PRTS_AppleVXD393_Panic_Frame_13(v10);
    ...
    if ( !((unsigned __int8)(v21 ^ v22) | v20) )
      break;
    v12 = *(_QWORD *)(v10 + 12528);
  `}`
  ...
`}`
```

为了确认是这个函数出问题了，我们首先在 Frame-14 的上层函数中将对 Frame-14 的调用 Patch 调：

[![](https://p4.ssl.qhimg.com/t01c3d07dbd84700ee0.png)](https://p4.ssl.qhimg.com/t01c3d07dbd84700ee0.png)

Patch日志：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d8c52d9dcd7071b2.png)

在 Patch 了相关代码之后，我们播放视频发现 iOS 不会崩溃。

同时，为了排除 Frame-14 的下层函数出现问题，我们在 Frame-14 中对下层函数的调用 Patch掉，如下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019b582305a8935642.png)

在 Patch 调对下层函数调用后，播放视频还是会造成 iOS 崩溃。总结起来，我们这里使用了注释代码的手段来确定问题代码的范围，最后我们确定：出问题的代码在崩溃时的调用栈的第 14 帧函数中，畸形的视频数据造成该函数死循环。



**三、结论**

由于时间有限，经过简单分析，目前的结论是：播放含有畸形数据的样本视频，会造成 iOS 内核中负责视频解码的模块进入死循环，进而引起内核 WatchDog 超时，造成内核重启。针对该样本，目前没发现更多危害。





**传送门**

[**iOS又曝新漏洞，播放特定视频导致自动关机（含演示视频）**](http://bobao.360.cn/news/detail/3774.html)


