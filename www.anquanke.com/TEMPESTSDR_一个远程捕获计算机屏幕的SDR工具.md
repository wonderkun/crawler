> 原文链接: https://www.anquanke.com//post/id/88436 


# TEMPESTSDR：一个远程捕获计算机屏幕的SDR工具


                                阅读量   
                                **146632**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者admin，文章来源：rtl-sdr.com
                                <br>原文地址：[https://www.rtl-sdr.com/tempestsdr-a-sdr-tool-for-eavesdropping-on-computer-screens-via-unintentionally-radiated-rf/](https://www.rtl-sdr.com/tempestsdr-a-sdr-tool-for-eavesdropping-on-computer-screens-via-unintentionally-radiated-rf/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0137e2cb26a8527801.png)](https://p4.ssl.qhimg.com/t0137e2cb26a8527801.png)



## 工具概述

TEMPEST是指一些间谍机构通过捕获无线电发射信号（包括声音、震动等）以窃听电子设备的技术。所有的电子产品都会在工作过程中发出射频信号，而通过捕获和处理这些信号就可以恢复一些数据。感谢RTL-SDR.com的flatflyfish发表的文章，其中详细说明了如何在Windows系统上使用TempestSDR工具。

TempestSDR是一个开源的间谍软件工具包，它允许我们使用任何支持ExtIO的SDR（例如RTL-SDR、Airspy、SDRplay、HackRF等）来接收源自计算机屏幕的射频信号，并将该信号还原后显示出来。通过这种方式，我们可以在没有任何物理连接的情况下看到屏幕上显示的内容。如果再使用高增益定向天线，那么甚至可以在几米之外的距离捕获到电脑屏幕的内容。

[![](https://www.rtl-sdr.com/wp-content/uploads/2017/11/TEMPEST_sdr_gui.png)](https://www.rtl-sdr.com/wp-content/uploads/2017/11/TEMPEST_sdr_gui.png)



## 重编译步骤

尽管TempestSDR已经发布了数年之久，但其中的ExtIO接口却始终不能在Windows中正常工作。本文中，flatflyfish向我们说明了如何编译一个可以工作的新版本，其具体步骤如下：

1. 首先，需要安装32位版本的Java运行环境（64位版本不支持ExtIO接口），并安装JDK。

2. 安装Mingw32和MSYS，将它们的bin文件夹添加到Windows路径中。

3. 在编译时，我们会遇到大量CC命令的未知错误，我们要在所有makefiles文件的顶部添加“CC=gcc”。由于没有使用到Mirics SDR，我们从JavaGUI makefile中删除Mirics相关行，这样可以简化我们的程序。

4. 原始的JDK文件夹存放在Program Files目录下，但makefile并不支持带有空格的文件夹名，我们需要解决这一问题，将其移动到另一个名字中没有空格的文件夹中。

5. 最后，在编译前，还需要指定ARCHNAME为x86，例如：“make all JAVA_HOME=F:/Java/jdk1.7.0_45 ARCHNAME=X86”。

在完成编译之后，就得到一个可以正常工作的JAR文件。现在的ExtIO，可以与HDSDR配合正常工作，我们可以通过rtlsdr，从测试显示器上获得一些图像。

经过测试，经过修改后的程序可以成功运行。为了帮助大家也能运行，我们将其上传到了 [https://github.com/rtlsdrblog/TempestSDR](https://github.com/rtlsdrblog/TempestSDR) ，并且在发布页面上提供了一个预编译的ZIP文件，这样大家无需编译就可以直接使用。

请注意，如果要使用这个预编译的JAR，仍然需要安装MingW32，同时还需要在Windows路径中添加MingW的/bin文件夹和msys的/1.0/bin文件夹。此外，还需要确保使用的是32位Java运行环境，64位版本将无法正常运行。如果是在Win10系统上运行，还需要手动将“Prefs”（偏好）文件夹添加到注册表中的Java路径下。



## 使用及调试

实际测试中，我们使用了老式的戴尔显示器，其中使用的DVI图像可以完整地接收到，尽管接收到的图像有一点点模糊。我们还另外尝试使用了Airspy和SDRplay设备，由于其具有更大的带宽，图像的质量有了明显提升。具体而言，屏幕上显示的相对较大的文字都可以显示并辨别。

如果使用Airspy，可以参考官方手册： [http://www.montefusco.com/airspy/](http://www.montefusco.com/airspy/)

如果使用SDRPlay，请参考官网上面的操作说明： [http://www.sdrplay.com/](http://www.sdrplay.com/)

请注意，SDRplay的频率无法超过6MHz，RTL-SDR的频率无法超过2.8MHz，一旦超出上述频率，可能会造成丢失样本，从而导致图像无法正常显示。

要使用该软件，最好能首先了解目标显示器的分辨率和刷新率。但如果不清楚，也有自动检测的功能，我们可以选择软件中给出的峰值。此外，我们还需要知道显示器射频信号的频率。假如不知道，可以通过SDR#寻找干扰峰值，该值取决于屏幕上显示的图像变化的频率。举例来说，下图展示了其中一种干扰的模式。有一个诀窍，就是我们可以通过增加“Lpass”选项值来改善图像。并且需要留意自动FPS搜索不能与预期的帧速率相差太多，一旦相差过多，我们可以通过重新设置屏幕分辨率来重置这一数值。

[![](https://www.rtl-sdr.com/wp-content/uploads/2017/11/SDRSharp_Tempest_small-1024x316.png)](https://www.rtl-sdr.com/wp-content/uploads/2017/11/SDRSharp_Tempest_small-1024x316.png)

关于显示器和图像制式，我们进行了多次尝试。在一台使用DVI制式的19寸戴尔老式显示器上得到了最佳效果的图像。在HDMI制式的飞利浦1080P显示器上得到的效果一般，但还是能成功接收到。但在一台AOC 1080P显示器上尝试，则无法收到任何可以辨别的图像。

关于位置，我们发现放置在同一房间的显示器，如果使用天线，可以得到最为清晰的图像。但是在相隔房间的两台戴尔显示器，图像仍可以接收到，但非常模糊，无法辨别出显示的内容。我们认为可以使用一个更高的增益定向天线，以改善这一问题。

[![](https://www.rtl-sdr.com/wp-content/uploads/2017/11/examplesetup2.jpg)](https://www.rtl-sdr.com/wp-content/uploads/2017/11/examplesetup2.jpg)

我们将本次实验成果拍摄了视频，并上传到了Youtube上（[优酷链接](http://v.youku.com/v_show/id_XMzE4NTk3Njg0NA==.html)）：

如果你还想了解更多关于TEMPEST和TempestSDR的内容，我建议可以阅读这一篇Martin Marinovs写的[文档](https://github.com/martinmarinov/TempestSDR/blob/master/documentation/acs-dissertation.pdf)：
