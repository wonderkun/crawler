> 原文链接: https://www.anquanke.com//post/id/83155 


# 第二部分：USB设备的研究——MSC与PTP及MTP


                                阅读量   
                                **196859**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://nicoleibrahim.com/part-2-usb-device-research-msc-vs-ptp-vs-mtp/](http://nicoleibrahim.com/part-2-usb-device-research-msc-vs-ptp-vs-mtp/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t016a4bf2a43dd2c025.png)](https://p4.ssl.qhimg.com/t016a4bf2a43dd2c025.png)

**在本系列之前的帖子中，我站在研究USB设备的角度谈到了我们想要研究的目标和论题。今天我主要将内容涵盖三个USB传输协议。重点如下：**

每个内容的基础知识

支持它们的Widnwos版本

支持它们的Windows服务

基础的Windows信息枚举

探讨不同论题之间的相关性

USB海量存储类(USB Mass Storage Class)

对于插入系统的USB设备，我们的大多数论题都建立在MSC设备上。这些设备的经典例子包括：扩展驱动器、大拇指/闪存驱动器、Windows内部的MPS播放器，顺便说一句，Windows2000之后都支持了MSC。

MSC是一个传输协议，它允许将一个设备安装的存储区域当做可移动介质，并且支持直接对扇区数据进行读或写。这些设备大多安装在物理层，你如果用一个十六进制编辑器来打开一个已安装的分区，那么这个文件系统的所有地方你都可以一览无余。

对于嵌入式操作系统的MSC，比如相机、智能手机、平板电脑、MP3播放器等，在他在Windows系统上被安装或枚举之前，它必须首先在设备操作系统的内部卸将其载掉才行。

一个MSC设备在Windows XP上安装后，会在资源管理下面出现一个“可移动存储设备”，并且会给其分配一个可用的驱动器号。

[![](https://p2.ssl.qhimg.com/t01dde3c83f8b5faaf7.png)](https://p2.ssl.qhimg.com/t01dde3c83f8b5faaf7.png)

在Cream Sandwich (冰淇淋三明治系统Android 4.0)发布之前，手机厂商其实更多地喜欢使用MSC作为它们的传输协议。在Cream Sandwich之后，MTP（媒体传输协议）就成为了标准的传输协议了。

对于苹果设备，唯一支持MSC模式的就只有iPod了，当连接到一台运行XP系统的电脑时，设备就会在资源管理器中被分配一个有效的盘符，在底部显示一个“可移动存储设备”，其实就很像扩展设备。然后呢，它就完全支持用户在设备上进行读写了。然而iPhone和iPad就不是与生俱来就支持MSC的了，虽然第三方软件仍然可以启动MSC进行访问，不过我没有测试过。

黑莓手机也是原生支持MSC模式，尽管这个选项在默认状态下貌似是禁用的，不过通过个人测试发现这可以通过设备内部进行自启动，测试期间发现Windows有时候在识别黑莓设备的时候会出问题。这要么是设备在Windows中没有被正确地安装，要么是因为这个设备极可能被当做了PTP(图像传输协议Picture Transfer Protocol)进行安装了。这两种的任意一种情况都会导致数据不能正常地传输到系统中，如果你正在研究黑莓和系统进行连接，请务必要注意这一点哦。Windows XP中的setupapi.log和Win7中的dev.log会记录设备和相关驱动程序是否正确安装。

黑莓或其它智能设备安装失败的原因很可能是缺少原供应商提供的设备驱动导致的，在这种情况下，Windows会给这个设备分配一个普通的驱动程序。我会在后来的介绍中详细介绍为什么会这样做以及如何做到。

扩展连接
<li>
[Wikipedia: Mass Storage Class](http://dage.xqiju.com/browse.php?u=qkcyshgeeExlNNDj6CCYzfmQdeBFY8a6K%2FEJErqRhNWyWgvEIThnaz7hzs8Xytn1w4GffBET&amp;b=13)
</li>
<li>
[Microsoft: Removable and USB Storage Devices](http://dage.xqiju.com/browse.php?u=qkcyugVUYQtjNMP04zqWheLMcaBfJci9KdEpf4mVh9SgdwGfOSNoaDTJ2YUJwsj064OBeE0HlRQiqAicFpdmGpxJ&amp;b=13)
</li>
<li>
[USB.org: USB MSC Overview](http://dage.xqiju.com/browse.php?u=qkcyoAFHIVB9P47p%2Fi7Wh%2FOUd6Ndesihd4s%2BNZOficeydifUISl1Iy7NyPUM0NnP85SWbxQJl1dLqhOdCsljDw%3D%3D&amp;b=13)
</li>
PTP是一个由国际影像工业协会支持的一个标准化协议，它被广泛使用。它支持设备传输图像或视频到计算机而无需任何第三方驱动。Windows ME以后的版本支持PTP。自从PTP仅处理图片，视频和其他相关的一些元数据开始，它就不再支持传输其他文件类型了，比如word文档、Zip，等等。还有一点很重要，请记住PTP仅支持单向文件传输，用户可以在这个设备上复制文件或下载文件到电脑或其它设备，但是却不支持从其他设备或电脑复制或下载文件到该设备上。安装到Windows这些设备是处于逻辑层的，所以你不可能看到这些设备底层的文件系统结构。

在Windows XP或更早版本的Windows系统中，由WIA（Windows图像采集器Windows Image Acquisition）设备管理器处理与PTP相关的功能，它被WIA设备管理器枚举出来，并且会在Windows资源管理器中显示“扫描仪或摄像机（Scanners and Cameras）”。

[![](https://p1.ssl.qhimg.com/t0134be1c96a53118ae.png)](https://p1.ssl.qhimg.com/t0134be1c96a53118ae.png)

在Windows Vista之后，WPD(Windows便携设备：Windows Portable Devices)代替了WIA，当一个PTP设备被识别后，资源管理器下的提示就变成了“移动设备(Portable Devices)”。

[![](https://p5.ssl.qhimg.com/t01ef8ee15a21f08ac7.png)](https://p5.ssl.qhimg.com/t01ef8ee15a21f08ac7.png)

许多类型的设备都支持PTP。它有时也在MTP不被支持的情况下作为备用传输协议。支持这个协议的设备大概有：扫描仪、照相机，一些智能手机和平板。

**扩展连接**

·[USB.org USB Still Image Capture Device](http://dage.xqiju.com/browse.php?u=qkcyoAFHIVB9P47p%2Fi7Wh%2FOUd6Ndesihd4s%2BNZOficeydifUISl1Iy7NyPUS19P88L2acAVRwg5u8k0%3D&amp;b=13)

·[Microsoft: Still Image Connectivity for Windows](http://dage.xqiju.com/browse.php?u=qkcyugVUYQtjNMP04zqWheLMcaBfJci9KdEpf5KVi8KucgufJit0aCzf2M9OxN2kqtHGLVVOk1Nk4w%3D%3D&amp;b=13) (Windows XP and earlier)

·[Microsoft: Guidelines for Picture and Video Import in Windows 7](http://dage.xqiju.com/browse.php?u=qkcyugVUYQtjNMP04zqWheLMcaBfJci9KdEpf5KVi8KucgufJit0aCzf2M9OxN2kqtHGKVQ%3D&amp;b=13)

媒体传输协议（Media Transfer Protocol）

MTP是微软推出的一个传输协议，看起来像是PTP的改进版。MTP支持多种多样的文件类型。该协议强调了与媒体文件相关的元数据的重要性，就相当于PTP和图片的关系一样，有并且有时候是设备供应商用来执行DRM(数字版权管理：Digital Rights Management)的一条途径。个人觉得MTP稍微有点命名用词不当，它远远不限于传输媒体文件——任何文件类型都可以使用支持MTP的设备进行传输。

对于MSC，当一个USB设备的分区安装到Windows之前，它必须先从其内部卸载后才可以。然后对于MTP，对数据存储区域的读和写可以在设备和计算机两者间共享。许多设备，如：MP3播放器，照相机，智能手机和平板都可以启用MTP。

和PTP一样，设备安装在逻辑层，所以它底层的文件系统结构依然无法查看到。

在Windows中，这些类型的设备是由WDP(Windows便携设备：Windows Portable Devices)处理的——带Media Player10 的Windows XP和后来的Windows版本都支持。

在Windows XP中，当一个MTP设备绑定到电脑上时，它将会由WPD枚举出来，并在资源管理器中显示“Other”。

[![](https://p2.ssl.qhimg.com/t019e0a7f37b54e8d8f.png)](https://p2.ssl.qhimg.com/t019e0a7f37b54e8d8f.png)

在Win7中，一个被枚举出来的设备会在“移动设备”中显示。

[![](https://p5.ssl.qhimg.com/t0131c56666e608dd08.png)](https://p5.ssl.qhimg.com/t0131c56666e608dd08.png)

要想查看设备的每个分区内容的话，双击设备图标就可以了。

[![](https://p4.ssl.qhimg.com/t01e0d9c5e0852b7955.png)](https://p4.ssl.qhimg.com/t01e0d9c5e0852b7955.png)

从取证的角度来看，如果有证据表明有MTP设备插入电脑，那么你应该联想到这类设备很可能是数据泄露点。然而，目前并不是所有取证工具都可以正确分析出这类设备的相关信息，所以对于一个检察官来说，很重要的一点就是要大量扩展这方面的知识，比如了解一些设备的注册表项，以及由这些设备产生出来的操作系统等。

### **扩展连接**

·[USB.org: Media Transfer Protocol](http://dage.xqiju.com/browse.php?u=qkcyoAFHIVB9P47p%2Fi7Wh%2FOUd6Ndesihd4s%2BNZOficeydifUISl1Ixbq%2BtxQ%2FIu%2B5ouD&amp;b=13)

·[Microsoft: Introduction to MTP](http://dage.xqiju.com/browse.php?u=qkcyugVUYQtjNMP04zqWheLMcaBfJci9KdEpf4mVh9SgdwGfOSNoaDTJ2YUJwsj064OBeE0HlRUsrgufFpdmGpxJ&amp;b=13)

·[Microsoft: Portable Media Players for Windows Vista](http://dage.xqiju.com/browse.php?u=qkcyugVUYQtjNMP04zqWheLMcaBfJci9KdEpf5KVi8KucgufJit0aCzf2M9OxN2kqtHGKVA%3D&amp;b=13)

**第一部分链接地址：**[**http://bobao.360.cn/news/detail/2508.html**](http://bobao.360.cn/news/detail/2508.html)
