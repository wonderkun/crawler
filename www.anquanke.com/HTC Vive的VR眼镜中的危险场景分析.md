> 原文链接: https://www.anquanke.com//post/id/151952 


# HTC Vive的VR眼镜中的危险场景分析


                                阅读量   
                                **148639**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：embedi.com
                                <br>原文地址：[https://embedi.com/blog/dangerous-reality-inside-of-vr-headset-htc-vive/](https://embedi.com/blog/dangerous-reality-inside-of-vr-headset-htc-vive/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01d2256835c0400bc7.jpg)](https://p0.ssl.qhimg.com/t01d2256835c0400bc7.jpg)

## 介绍

VR主题已经成为一种现代化趋势，它使电脑科幻小说转化成的光影图像更接近现实。因此，也毫不奇怪大家对它保持着不变的热情。多年来，VR耳机的价格已经远远低于最开始第一款产品发布时的价格。毫无疑问，未来VR设备在任何家庭中都将会变得像台式电脑一样自然。根据[IDC的数据](https://dazeinfo.com/2017/06/28/the-age-of-vr-is-already-upon-us-could-ar-be-next/)，到2021年，VR耳机的出货量将达到6700万台。

这就是为什么我们决定研究一下VR头戴式设备——也就是VR眼镜，以了解一个网络犯罪分子可以如何玩它，以及可能会对设备主人造成什么伤害。

我们研究了攻击者可能使用的以下攻击场景：
1. 入侵VR眼镜并更改其位置坐标，这可能会导致用户受伤。
1. 入侵VR眼镜并添加一些怪异的视觉效果，导致心理创伤和紊乱。
1. 入侵VR眼镜并使用广告横幅屏蔽其屏幕。
1. 将VR眼镜转变为感染链中的一环，并在它连接到其他设备时传播病毒。
如果您发现本文至少有一半像我们做的那样有趣，欢迎阅读我们对HTC Vive安全性的简短回顾。



## 研究HTC VIVE

HTC Vive是目前市场上最广泛的VR设备之一，同时它也激起了大多数研究者的兴趣。让我们先从分析VR系统的组件及其功能开始，HTC Vive由4个主要部分组成。

### [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/vive-hardware-hmd-1.png)

[Fig 1.](https://www.vive.com/ru/product/)[ HTC](https://www.vive.com/ru/product/)[ Vive](https://www.vive.com/ru/product/)[ 眼镜](https://www.vive.com/ru/product/)

眼镜的主要目的是对用户头部进行位置跟踪并将图像输出到VR眼镜的显示器。它既是系统中最重要也是最有趣的部分，它配备了摄像头和32个位置跟踪传感器，另外还包含四个连接口：
- 两个USB 3.0
- 充电口
- Jack 3.5
- HDMI
最开始将设备连接到PC时就用到了三个连接口，只有一个USB连接口保持空闲状态以供外部设备连接。

在系统工作时，眼镜是唯一一个会始终连接到PC的组件。通过拆解眼镜，我们可以接触到它的主板，以及所有我们感兴趣的部分。

主板的第一面上主要有四个组件：
<li>3个ARM处理器;
<ul>
- NXP 11U35F
- 两个Nordic nRF24LU1P
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/1_board.png)

图2.眼镜主板第一面

第二面还有几个重要组件：
<li>两个ARM处理器;
<ul>
- STM32F072R8;
- AIT8328;
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/2_board.png)

图3.眼镜主板第二面

### [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/vive-hardware-base-stations.jpg)

图4.HTC Vive基台

基台的主要目的是追踪用户的位置，它们以每秒60次的周期发送同步脉冲，然后在房间中从上到下、从左到右投射激光束，传感器收集捕捉到的数据并将其发送给眼镜和控制器手柄里的微控制器处理以追踪用户的位置。

基台配备电源和用于同步的Jack 3.5，其中每一个工作站还带有一个蓝牙模块，用于发送有关设备正在进入或退出睡眠模式的通知。

在基台内部，有NXP 11U37F (ARM Cortex-M0) 芯片，负责基台的主要功能。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/1_station_board.jpg)

[图5.底座主板第一面](https://www.ifixit.com/Guide/Image/meta/SeM3B6DUj2HaoNca)

Broadcom BCM20736 (ARM Cortex-M0) 保证了蓝牙的运行。还有RS-485/RS-422收发器，通过Jack 3.5同步基台的两个工作站。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/2_station_board.jpg)

[图6.底座主板第二面](https://www.ifixit.com/Guide/Image/meta/dQbVNd2bRtHycOh4)

基台和PC之间的交互接近于零（仅限于更新程序），而眼镜会在硬件级别下借助激光束进行通信，如果光束的工作方式发生任何变化，系统都将无法正常运行。

### [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/vive-hardware-controllers-1.jpg)

[图7.HTC Vive 手柄](https://www.vive.com/ru/product/)

很明显，控制器手柄用于追踪用户的手部动作以确保用户获得完整的VR体验。至于连接口，它们仅配备microUSB进行充电和更新。但它里面是什么？好吧，里面有基于Cortex-M0的NXP 11U37F处理器，它维护着控制器的主要功能。另外还有FPGA ICE40HX8K-CB132用于处理响应基台投射的激光束的传感器；和一个4 Mb Micron M25P40芯片。乍一看，很难发现蓝牙芯片，因为它是一个隐藏在金属屏幕下的wall-flower Nordic nRF24LU1P。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/controller_board.png)

图8. HTC Vive控制器手柄主板

### <a class="reference-link" name="%E9%93%BE%E6%8E%A5%E7%9B%92"></a>链接盒

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/link_box.jpg)

[图9. HTC Vive的链接盒](https://www.vive.com/ru/product/)

链接盒是PC和眼镜之间的枢纽，它的一侧有四个连接口：
- 充电口
- USB 3.0用于连接PC
- 显示端口
- HDMI
另一侧，有三个眼镜连接口：
- 出电口
- HDMI
- USB 3.0
我们可以很容易就找到了其所需的蓝牙芯片，以便快速便捷地进行设备更新。



## WATCHMAN更新和控制台

浏览了SteamVR软件文件夹后，我们找到了两个有用的程序：lighthouse_console.exe和lighthouse_watchman_update.exe。第一个是用于处理HTC Vive设备的控制台，后者则可以更新眼镜设备。

通过执行lighthouse_console中的help命令，我们可以看到列出的以下命令：

```
lh&gt; help
associatecontroller     Associated the attached controller to the attached puck
axis    Toggle VRC axis data dumping
battery Print battery status
button  Toggle button data dumping
clear   Clear the record buffer and accumulated statistics.
dump    Toggle all dumping to the console. You must also turn on the individual `{` imu, sync, sample `}` flags.
errors  Dump the lighthouse error/status structure.
event   Toggle lighthouse aux event dumping
eventmask       Select lighthouse aux events to report
isp     Enable In-System Programming
haptic [us]     Trigger haptic pulse
identifycontroller      Trigger haptic pulses on the active serial number to identify it
imu     Toggle IMU data packet dumping
imustats        Print IMU statistics
period  Print sync statistics
dis [&lt;type=auto&gt;]       Toggle disambiguation. types=`{` auto, tdm, framer, synconbeam `}`
syncd   Toggle sw sync detect
pose    Toggle static pose solver. Is 'dis' is not active, it will enable it.
poweroff        Turn off the active controller
record  Toggle event recording. You must also turn on the individual `{` imu, sync, sample `}` flags.
serial  Select a device to open by serial number substring
sensorcheck     Print out hits (and widths) per sensor
save [&lt;filename="lighthouse_console_save.txt"&gt;] Save recorded events to a file on disk
sync    Toggle sync dumping
sample  Toggle sample dumping
trackpadcalibrate       Trigger trackpad recalibration on the active controller
uploadconfig [&lt;filename&gt;]       Upload the config file to the device
downloadconfig [&lt;filename&gt;]     Download the config file
reformatconfig &lt;inputfilename&gt; &lt;outputfilename&gt; Update the config to the latest json format
version Prints the firmware and hardware version on the Watchman board
userdata        Get a directory listing of the stored userdata
userdatadownload &lt;name&gt; Download the specified named userdata
userdatadownloadraw &lt;addr&gt; &lt;size&gt; [&lt;filename&gt;]  Download and store the user data at specified address
userdatasize    Display the size of the user data space (in bytes)
ispdiv &lt;divisor&gt;        Set the camera ISP sync signal divisor
quit    Quit
```

但如果在IDA Pro中打开程序则可以看到更多内容：

```
if ((unsigned __int8)sub_402210(v11, "pair"))`{`
    v173[1] = 0;
    if (*(_DWORD *)(v217 + 16) == 8449)
      sub_42EC30(10000, (char)v173[1]);
    else
      sub_42ED10((char)v173[1]);
    goto LABEL_497;
  `}`
  if ((unsigned __int8)sub_402210(v11, "pairall"))`{`
    sub_40C4C0(15000, 0);
    goto LABEL_497;
  `}`
  if ((unsigned __int8)sub_402210(v11, "forcepairall"))`{`
    sub_40C4C0(15000, 1);
    goto LABEL_497;
  `}`
  if ((unsigned __int8)sub_402210(v11, "unpair"))`{`
    sub_42BA80(v217);
    goto LABEL_497;
  `}`
  if ((unsigned __int8)sub_402210(v11, "unpairall"))`{`
    sub_40FEF0();
    goto LABEL_497;
  `}`
  if ((unsigned __int8)sub_402210(v11, "hmdhidtest") )
```

以下是help命令未列出的命令，但它们仍然在该程序中：
- fpgareset
- fixcalib
- pair
- pairall
- forcepairall
- unpair
- unpairall
- hmdhidtest
- fpgaread
- dongleinfo
- donglereset
- dongleresetall
- eventrate
- wait
- capsensecalibrate
- trackpaddebug
- poweroff
借助此列表，我们可以通过各种方式来测试设备，比如检查按钮的状态。我们也可以下载配置文件，在上传回来，并执行其他特殊操作。

有了lighthouse_watchman_update.exe，攻击者可以轻松更新任何设备的固件，这是上文中每种攻击场景的基础。此外，大多数微控制器的固件可以通过相邻目录访问，尽管它们各自的功能并不十分清晰。

```
Usage: lighthouse_watchman_update [OPTIONS] [args...]
Options:
  -h                       Prints this message
  -m&lt;dev&gt;                  Update main firmware (default)
  -f&lt;dev&gt;                  Update FPGA firmware
  -r&lt;dev&gt;                  Update radio firmware
  -j&lt;dev&gt; k1,f1 k2,f2 ...  Update user data `{`key,filename`}`. Multiple files supported. Erases prior user data.
  -u &lt;dir&gt;                 Update all devices with firmware in the specified directory
  -U &lt;dir&gt;                 Same as '-u' option but forces update
  -x                       Do not reset device after successful update
  -b&lt;dev&gt;                  Reset device into bootloader mode
  -i&lt;dev&gt;                  Reset bootloader device into ISP mode
  -R&lt;dev&gt;                  Reset into main firmware from the bootloader
  -B &lt;num&gt;                 Set board revision
  -l&lt;dev&gt; &lt;num&gt;            Set date/lot code
  -a&lt;dev&gt;                  Print bootloader attributes
  -c                       Print CRC128
  -d                       Update watchman dongle
  -D                       Update watchman dongles and/or convert Steam Controller dongles to watchman
  -g&lt;dev&gt;                  Update fuel gauge firmware
  -t &lt;path&gt;                Reads timestamp information from a watchman firmware image
  -s &lt;serial num&gt;          Update the device with matching serial number
  --via-dongle             Perform watchman firmware updates via a dongle radio connection
  --via-bootloader         (Watchman v3 devices only) Sends the update via the device's bootloader
  --via-application        (Watchman v3 devices only) Sends the update via the device's application interface
  --force-update           (Watchman v3 devices only) Forces an update onto a device
  --target=&lt;target&gt;        (Watchman v3 devices only) Sets the update target.  Available targets:
                               application, bootloader, ice40, max10, nrf52, bq27520, user, default (set by file)

 &lt;dev&gt; device     'w' for watchman 'w3' for watchman v3 'v' for VRC 'n' for NEO_VRC
                   (default is watchman)
```



## 硬件分析

眼镜主板是整个实验中最有趣的部分，许多重要的硬件部分都在它上面，它还有很多调试连接口。幸运的是，大多数微控制器都不属于BGA情况，这也是我们设法找到某些芯片的SWD连接口的原因。图10显示了其中一个NXP LPC11U35F。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/SWD.png)

图10.NXP LPC11U35F的SWD连接口

为了理解每个微控制器执行的功能并重建组件之间的连接，我们使用了焊接器和万用表。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/multimeter.jpg)

图11.万用表和焊台

我们拆开了主板，用我们的万用表测出了路径，并制定了组件之间的连接方案（见图12）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/schematic.png)

图12. HTC Vive组件之间的连接方案

我们之前说过，眼镜有USB-Hub SMSC USB5537B，其可通过1个USB连接多达7个设备，其中6个可用端口被耳机的主要部件占用，而剩余的外部端口保持空闲以提供给附加设备进行连接。该方案说明不可能从眼镜侧面进入视频输出处理，因为它是一个负责程序的PC。FPGA监控32个眼镜传感器的状态，处理它们发出的所有数据，并通过UART传递给NXP LPC11U35F/401微控制器。

我们可以得出什么结论？

我们首先想到的是视频流不会受到任何影响，因为它是由PC处理的，PC将渲染的图像发送到眼镜，因此攻击场景2和3不适用。

其次，我们发现芯片（NXP LPC11U35F/401）负责追踪眼镜的位置并通过USB将它们发送到PC。因此，网络犯罪分子可以修改处理位置数据的系统，以便用户的虚拟位置与真实位置不同，此情况可对应于攻击场景1。

然后，我们必须找出存储在微控制器上的固件，所有微控制器和内存都已经拆焊过，所以，我们需要从中读取数据，在我们的焊台的帮助下，我们将微控制器焊接到TQFP适配器上（参见图13）：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/arm_TQFP.jpg)

图13.连接到TQFP适配器的芯片

不幸的是，我们找不到SPI内存芯片的适配器，因为它有更少的排针。所以我们只是为它们焊接了一个排针。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/SPI_flash.jpg)

图14.带有焊接排针连接口的SPI存储器，用于连接编程器

ChipProg481和一堆电线在提取固件时派上了用场！

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/somewire.jpg)

图15.连接到它的ChipProg481和STM32F072。

我们从控制器中提取数据以进行更改，但是其中的所有组件都没问题，所以我们不必拆除它们。由于连接到SWD的BlackMagick Probe v2，从两个微控制器提取数据的过程是绝对无缝的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/07/BMP_SWD.jpg)

图16. Black Magick Probe v2.1连接到控制器板手柄上的SWD

根据收集的数据，我们建立了一个表格，以清晰地说明使用了哪些固件以及在每个微控制器上执行了哪些功能。

|Dump 源|从SteamVR软件中提取的固件|附加信息
|------
|Micron N25Q032A13ESE40E 32 Mb|Micron N25Q032A13ESE40E 32 Mb|Addresses from 0xF8000 to 0xF9C1DF were not found in the SteamVR firmware.
|STM32F072|DisplayBin tools/lighthouse/firmware/htc/APP_0000000000200160.bin|Addresses from 0x0 to 0x26c8 were not found in the SteamVR firmware.
|Micron M25P40 4 Mb|DisplayBin tools/lighthouse/firmware/htc/APP_0000000000200160.bin|–
|nRF24LU1P|DongleBin tools/lighthouse/firmware/vr_controller/archive/htc_vrc_dongle_1461100729_2016_04_19.bin|–
|NXP 11U35F|WatchmanBin tools/lighthouse/firmware/lighthouse_rx_watchman/archive/htc_watchman_1462663157_2016_05_07.bin|Configuration archive.
|Micron N25Q032A13ESE40E 32 Mb|WatchmanFPGABin tools/lighthouse/firmware/lighthouse_rx_watchman/archive/htc_pre_watchman_262_fpga.bin|PNG_1 Green_4A7A16BB004239_mura_analyzes.mc PNG_2 Green_4A8A16B8004487_mura_analyzes.mc.

表1.提取的固件与存储在SteamVR软件文件夹中的固件之间的比较



## 安全方面

HTC Vive的安全问题很早在更新阶段就出现过，根据微控制器文档记载，所有微控制器都支持通过USB进行更新。从固件文件判断，我们很清楚固件是没有校验和的二进制文件。因此，攻击者可以根据自己的喜好修改固件并将其上传到眼镜中。此外，每个微控制器都有足够的空间（平均45 Kb），以便将修改后的代码放入其中。Change，upload，enjoy！

例如，在NXP LPC11U35文档中，陈述如下：

```
- In-System Programming (ISP) and In-Application Programming (IAP) via on-chip bootloader software.
- ROM-based USB drivers. Flash updates via USB supported.
- ROM-based 32-bit integer division routines
```

STM32F072文档：

```
The boot loader is located in System Memory. It is used to reprogram the Flash memory by using USART on pins PA14/PA15, or PA9/PA10 or I2C on pins PB6/PB7 or through the USB DFU interface.
```

nRF24LU1P：

```
The nRF24LU1+ bootloader allows you to program the nRF24LU1+ through the USB interface. The bootloader is pre-programmed into the nRF24LU1+ flash memory and automatically starts when power is applied.
```

如上所述，有一个特殊的lighthouse_watchman_update.exe控制台工具可用，而恶意代码也可以使用它来进行攻击或实现工具本身的功能。

从HTC_Vive_Tracker_Developer_Guidelines_v1.3可以看出，设备更新的时候用到了以下命令：

```
- Update MCU’s firmware:
  - lighthouse_watchman_update -mnt tracker_mcu_filename.bin
- Update FPGA’s firmware:
  - lighthouse_watchman_update -fnt tracker_fpga_filename.bin
- Update RF’s firmware:
  - lighthouse_watchman_update -rnt tracker_rf_filename.bin
```

如果可以更新HTC Vive的软件，攻击者就可以添加可能影响系统运行的恶意代码，并可能导致设备所有者的身体伤害或造成其他不便。



## HTC VIVE PRO

该设备的更新版本在不久前已经发布。但不幸的是，我们还没有机会研究专业版。尽管如此，有关HTC Vive Pro的可用信息表明基本版本没有发生根本性的变化。虽然一些微控制器确实更新了，但设备的整体操作原理和其组件之间的交互仍然是相同的。他们只是稍微改变了主板的布局（目前改变了两个），以及调整了连接器的放置方式。

还有一项尚未实现的真正的新功能：开发人员宣布他们将发布一款配件，可以将设备从线路中解放出来，并借助WiGig技术通过无线信道来传输数据。然而，除了有用的功能之外，这种新颖性也带来了另一种攻击向量。



## 结论

总而言之，我们列出了关于上述攻击情形的结论清单：
- 攻击场景1：攻击者可以更改眼镜的位置和坐标，用户可能会在他们可以说“Jack Robinson”或软件警告他们这种危险的接近度之前直接装到他们的公寓墙上。
- 攻击场景2和3：由于眼镜并不处理视频流，因此无法使用这些场景。
- 攻击场景4：尽管该场景是可以实现的，但由于HTC Vive是固定设备，很少与其他台式机连接，除了它连接到的PC，所以设备所有者的台式机可能存在被感染的风险。
HTC vive是一种高科技设备，但显然它的安全性并不是开发人员的优先考虑的事项。

攻击者可以轻松访问HTC Vive中使用的每个微控制器的固件，修改并将其上传回眼镜。因此不仅会破坏游戏体验，还会伤害所有者。

多年后，VR和AR技术将变得更先进和发展，技术的安全问题也将如此。不幸的是，该技术的安全问题同时也可能会变得更加严峻和危险。

审核人：yiwang   编辑：边边
