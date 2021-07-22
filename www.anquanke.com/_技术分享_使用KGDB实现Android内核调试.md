> 原文链接: https://www.anquanke.com//post/id/85352 


# 【技术分享】使用KGDB实现Android内核调试


                                阅读量   
                                **174322**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：trendmicro.com
                                <br>原文地址：[http://blog.trendmicro.com/trendlabs-security-intelligence/practical-android-debugging-via-kgdb/](http://blog.trendmicro.com/trendlabs-security-intelligence/practical-android-debugging-via-kgdb/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p3.ssl.qhimg.com/t015437563d7e16dca2.png)](https://p3.ssl.qhimg.com/t015437563d7e16dca2.png)**

****

**翻译：**[**myswsun******](http://bobao.360.cn/member/contribute?uid=2775084127)

**预估稿费：140RMB**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

**<br>**

**前言**

内核调试给了安全研究员在分析时一个监视和控制设备的工具。在桌面平台如Windows、macOS和linux，非常简单实现。然而，在安卓设备，例如谷歌Nexus 6P，上面内核调试很困难。本文，我将描述一种在安卓设备上面内核调试的方法，而且不需要特殊硬件。

<br>

**实现**

Joshua J.Drake和Ryan Smith为了这个目的构建了一个[UART debug cable](https://www.optiv.com/blog/building-a-nexus-4-uart-debug-cable)，能很好的完成内核调试。然而一些人不擅长硬件环境构建，这将变得困难。还好，通过[serial-over-usb通道](http://bootloader.wikidot.com/android:kgdb)也能完成内核调试。

这个方法可以追述到2010年，意味着一部分指令现在已经过时了。我发现仍然使用此方法的一些关键点可以在现代Android设备上使用。研究员用调试来判断CPU执行的状态，能加快分析。但是这个过程如何实现？

Android用的是linux内核，内置了内核调试器[KGDB](https://kgdb.wiki.kernel.org/index.php/Main_Page)，KGDB依赖连接调试设备和目标设备的串口。典型场景如下：

[![](https://p2.ssl.qhimg.com/t01be2c7597cc32f6e7.jpg)](https://p2.ssl.qhimg.com/t01be2c7597cc32f6e7.jpg)

图1. KGDB工作模式

目标设备和调试设备使用串口电缆相连。用户在调试设备上面使用GDB附加到串口（如/dev/ttyS1）目标设备，命令是target remote /dev/ttyS1。之后，GDB能和目标设备上的KGDB通过串口电缆通信。

KGDB的核心组件处理真正的调试任务，例如设置断点和获取内存数据。KGDB的输入输出组件连接KGDB核心组件和底层串口驱动的关键。

然而，Android设备通常没有硬件串口。第一个挑战便是如何找到一个通道，能够用GDB向外发送调试信息。多种通道被使用了，但是最特别的解决方案是USB电缆。

Linux内核USB驱动支持[USB ACM class devices](https://cscott.net/usb_dev/data/devclass/usbcdc11.pdf)，能仿真一个串口设备。简言之，一个Android设备能通过USB电缆连接串口设备。所有这一切都在已经是Linux内核一部分的代码中了，因此我们不比增加代码。下面是激活调试功能的步骤：

1. 构建一个AOSP的版本和相应的linux内核，参考[在此](https://source.android.com/source/building.html)。

2. 用USB电缆将目标设备和调试机器相连。

3. 用fastboot命令将映像写入设备，fastboot flashall –w。

4. 运行adb命令启动网咯服务：adb tcpip 6666。

5. 在调试机器上面，运行adb连接设备：adb connect &lt;device ip&gt; 6666。

6. 运行adb shell：adb shell。

7. 在adb shell中，到USB驱动控制文件夹中/sys/class/android_usb/android0/。

8. 在adb shell中，用下面的命令启动USB ACM功能：



```
echo 0 &gt; enable       //close USB connection
echo tty &gt; f_acm/acm_transports    //specific transport type
echo acm &gt; functions           //enable ACM function on USB gadget driver
echo 1 &gt; enable       //enable USB connection
```

到这里，USB ACM功能应该启用了。两步验证是否生效：首先，在adb shell中，用ls /dev/ttyGS*。一个设备文件应该存在。再者，在调试机器上面，用ls /dev/ttyACM*。也应该存在一个设备文件。调试机器和目标设备用这两个文件通信。

第二个挑战是KGDB需要底层通信驱动（串口驱动或者USB驱动）来提供一个轮询的接口用于读写。为什么？因为KGDB的通信通道需要在KGDB的内核异常处理函数中工作。在那个上下文中，中断被禁用了并且只有一个CPU起作用。底层驱动不依赖中断并且需要轮询改变寄存器或内存I/O空间。不要在这个上下文使用休眠和自旋锁。

这个Nexus 6P使用DWC3控制器来完成USB连接。这个USB驱动不直接提供轮询功能。因此我们需要在DWC3设备驱动中添加这个[特性](https://github.com/jacktang310/KernelDebugOnNexus6P)。代码后面的概念是简单的：我已经移除了中断依赖。相反的是我是用循环去查询相应的寄存器修改和内存空间。为了使事情简单，我做了以下的事情：

1. 我在kgdboc.c文件中的kgdboc_init_jack函数中硬编码了ACM设备文件名/dev/ttyGS0。

2. 我改变了f_acm/acm_transports函数启用了KGDB。这将允许用简单的命令开启KGDB: echo kgdb &gt; f_acm/acm_transports

下图是KGDB的工作模式：

[![](https://p5.ssl.qhimg.com/t017ec20c2d2880095a.jpg)](https://p5.ssl.qhimg.com/t017ec20c2d2880095a.jpg)

图2. 新的KGDB的工作模型

这里是整合代码到内核代码的步骤。虽然你能用任何内核代码，但是我采用[谷歌自身的仓库](https://android.googlesource.com/kernel/msm.git)，指定分支origin/android-msm-angler-3.10-nougat-hwbinder。

1. 用下面的配置编译内核代码：

```
1. CONFIG_KGDB=y
        CONFIG_KGDB_SERIAL_CONSOLE=y
    2. CONFIG_MSM_WATCHDOG_V2 = n，如果这个启动了，内核中轮询循环是一个死循环并重启设备。
    3. CONFIG_FORCE_PAGES=y，如果这个没哟开启，软断点将不能设置。
```

2. 用fastboot命令刷新内核和Android映像到目标设备。

3. 在调试机器上面启动Android系统。运行以下命令启动网络服务：adb tcpip 6666。

4. 在调试机器上，运行以下命令：



```
adb connect &lt;device’s ip address&gt;:6666
adb shell
```

5. 在adb shell中，运行以下命令：



```
echo 0 &gt; enable
echo tty &gt; f_acm/acm_transports
echo acm &gt; functions
echo 1 &gt; enable
echo kgdb &gt; f_acm/acm_transports
```

6. 在调试机器上面，运行gdb。Nexus 6P有一个aarch64的内核，因此需要[aarch64版本的gdb](https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.8)。



```
sudo &lt;path&gt;/aarch64-linux-android-gdb &lt;path&gt;/vmlinux
target remote /dev/ttyACM0
```

7. 在adb shell中，输入以下命令：

```
echo g &gt; /proc/sysrq-trigger
```

注意：在第6步和第7步之间的时间间隔不能太长。越短越好。

8. 如果成功了，GDB会有以下输出：

[![](https://p0.ssl.qhimg.com/t018471353b9fe9a418.jpg)](https://p0.ssl.qhimg.com/t018471353b9fe9a418.jpg)

图3. GDB输出

我已经用这个方法在Nexus 6P上面实现了内核调试。这个方法应该也支持Google Pixel，因为他们也使用DWC3 USB控制器。

<br>

**总结**

我们希望分享这个技术能够帮组到其他Android研究者，使得更好的理解移动恶意软件的行为。调试有助于研究者更好的逆向分析，也能更清楚的理解Android设备上面恶意程序如何作为。
