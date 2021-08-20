> 原文链接: https://www.anquanke.com//post/id/248900 


# NetGear 夜鹰 RAX40V2 设备与固件分析


                                阅读量   
                                **17721**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t019cfd0226d3abb3c0.png)](https://p2.ssl.qhimg.com/t019cfd0226d3abb3c0.png)



## 0x01 前言

NetGear 厂商的路由器设备中，拆解开经常会带有UART 调试串口，并且以往的NetGear 设备UART调试口往往只需要正确的检测出UART引脚的类型，设置波特率为115200，然后直接用串口调试软件配合FT232就可以直接获取设备内部的shell。但是Nightawk 夜鹰 RAX40V2 路由器在接入UART调试串口时，却有所不同。本篇文章，将带来对NetGear RAX40v2 在路由器开发板上的UART 获取shell的过程中遇到的一些问题，如何进行解决，循序渐进的开启设备的telnet，让我们拭目以待。



## 0x02 设备分析

产品名称：Nighthawk AX4 4-Stream WiFi Router

固件版本：V1.0.2.82_2.0.50

发布日期：2020年

首先我们从设备侧入手，拆解的过程以及设备硬件的配置，这不属于本片文章的重点，这里就不做过多的讲解。



## 0x03 设备串口分析

引脚分析，这款设备的引脚已经给了针脚，也免去了另外焊接针脚的工作，根据万用表和逻辑分析仪的识别（其实没用到逻辑分析仪）

从上到下依次是 VCC 引脚、GND引脚 (红线)、TXD引脚（黄线）、RXD引脚（橙线）

[![](https://p2.ssl.qhimg.com/t0167d54fecdc5f069e.png)](https://p2.ssl.qhimg.com/t0167d54fecdc5f069e.png)

**波特率识别**

首先识别FTD 232 USB “ls -ll /dev/tty**“**

**[![](https://p0.ssl.qhimg.com/t016b96b16362e93c59.png)](https://p0.ssl.qhimg.com/t016b96b16362e93c59.png)**

**接下来使用devttys0 的小工具baudrate.py 来识别波特率，只需要简单的使用上下键，就可以识别不同的波特率。如下图所示，设备识别为115200。 这也是NetGear 常用的波特率，其他的厂商的波特率也很多使用这个波特率。**

**[![](https://p4.ssl.qhimg.com/t01c468a38edf6e418d.png)](https://p4.ssl.qhimg.com/t01c468a38edf6e418d.png)**

**tip： 这里顺带提一下，baudrate.py 识别的波特率是设置好的常见波特率，但是里面只设置了几个可以识别的波特率，如果需要增加识别广度，需要在脚本内部的BAUDRATES 参数中增加想要识别的波特率值。**

**[![](https://p5.ssl.qhimg.com/t01b1030046a1c87a37.png)](https://p5.ssl.qhimg.com/t01b1030046a1c87a37.png)**

**<em>获取启动log**</em>

现在我们已经知道了波特率，接下来获取设备在启动的时候的log 信息，分析这些log 对设备分析有的时候会非常有用。但是常常 UART 的log 信息会非常多并且启动比较快。因此需要想办法将这些log 保存下来，以便后续分析。

我们使用minicom 打开，选择 “Serial port setup” —&gt; 设置 ”A—-Serial Device“ 和 ”E “的波特率，minicom 使用的方法搜索一下有详细的使用说明。

[![](https://p4.ssl.qhimg.com/t014f94dc85263c23b6.png)](https://p4.ssl.qhimg.com/t014f94dc85263c23b6.png)

保存串口log 为文件，关闭也是一样的。最终可以看到生成的文件，文本编辑器打开生成的文件。

[![](https://p2.ssl.qhimg.com/t01859e3d8b930b0f0e.png)](https://p2.ssl.qhimg.com/t01859e3d8b930b0f0e.png)

tips: 非正常关闭minicom，会在/var/lock下创建几个文件LCK*，这几个文件阻止了minicom的运行，将它们删除后即可恢复。

查看设备启动的log ，log 很多，这里截选了部分的log信息。

squashfs: version 4.0 (2009/01/31) Phillip Lougher<br>
jffs2: version 2.2. (NAND) (SUMMARY) © 2001-2006 Red Hat, Inc.<br>
fuse init (API version 7.23)<br>
SGI XFS with security attributes, no debug enabled<br>
io scheduler noop registered (default)<br>
brd: module loaded<br>
loop: module loaded<br>
nand: device found, Manufacturer ID: 0xef, Chip ID: 0xda<br>
nand: Unknown W29N02GV<br>
nand: 256 MiB, SLC, erase size: 128 KiB, page size: 2048, OOB size: 64<br>
bcm63xx_nand ff801800.nand: Adjust timing_1 to 0x6532845b timing_2 to 0x00091e94<br>
bcm63xx_nand ff801800.nand: detected 256MiB total, 128KiB blocks, 2KiB pages, 16B OOB, 8-bit, BCH-4<br>
Bad block table found at page 131008, version 0x01<br>
Bad block table found at page 130944, version 0x01<br>
&gt;&gt;&gt;&gt;&gt; For primary mtd partition rootfs, cferam/vmlinux.lz UBI volume, vmlinux fs mounted as squash fs on UBI &lt;&lt;&lt;&lt;&lt;<br>
Secondary mtd partition rootfs_update detected as UBI for cferam/vmlinux source and UBIFS for vmlinux filesystem<br>
Creating 11 MTD partitions on “brcmnand.0”:<br>
0x000000100000-0x000006900000 : “rootfs”<br>
0x000006900000-0x000006d00000 : “rootfs_update”<br>
0x000007f00000-0x00000ff00000 : “data”<br>
0x000000000000-0x000000100000 : “nvram”<br>
0x000000100000-0x000006900000 : “image”<br>
0x000006900000-0x000006d00000 : “image_update”<br>
0x000000000000-0x000010000000 : “dummy1”<br>
0x000000000000-0x000010000000 : “dummy2”<br>
0x000007a00000-0x000007f00000 : “misc3”<br>
0x000007500000-0x000007a00000 : “misc2”<br>
0x000006d00000-0x000007500000 : “misc1”<br>
tun: Universal TUN/TAP device driver, 1.6<br>
tun: (C) 1999-2004 Max Krasnyansky [maxk@qualcomm.com](mailto:maxk@qualcomm.com)<br>
PPP generic driver version 2.4.2<br>
PPP BSD Compression module registered<br>
PPP Deflate Compression module registered<br>
NET: Registered protocol family 24<br>
i2c /dev entries driver<br>
bcm96xxx-wdt ff800480.watchdog: Broadcom BCM96xxx watchdog timer<br>
brcmboard registered<br>
brcmboard: brcm_board_init entry<br>
print_rst_status: Last RESET due to HW reset<br>
print_rst_status: RESET reason: 0x00000000<br>
DYING GASP IRQ Initialized and Enabled<br>
map_hw_timer_interrupt,130: interrupt_id 22<br>
map_hw_timer_interrupt,130: interrupt_id 23<br>
map_hw_timer_interrupt,130: interrupt_id 24<br>
map_hw_timer_interrupt,130: interrupt_id 25<br>
Allocated EXT_TIMER number 3<br>
Broadcom Timer Initialized

**接入UART调试口shell**

UART 接入，设置好波特率，重启设备，待设备系统启动完成，启动日志输出完之后，连接shell ，但是需要登录口令。

[![](https://p3.ssl.qhimg.com/t0164258a9cbd21d358.png)](https://p3.ssl.qhimg.com/t0164258a9cbd21d358.png)

遇到这种方法，本打算尝试调整uboot在引导linux kernel时使用的启动参数(bootargs) 直接访问跟文件系统。但是我很幸运的使用弱口令进去之后，但是发现这是一个低权限的shell，并且支持的可执行的命令非常有限.

[![](https://p1.ssl.qhimg.com/t01fbe37289f2991f2d.png)](https://p1.ssl.qhimg.com/t01fbe37289f2991f2d.png)

[![](https://p0.ssl.qhimg.com/t01df9e829335257576.png)](https://p0.ssl.qhimg.com/t01df9e829335257576.png)

正当我一筹莫展的时候，想起了曾经看到的一款思科的设备的shell 也是类似这种低权限的shell，但是输入 “sh”、”\bin\sh” 、”bash” 等命令可以获取完整版的shell。很幸运，在我输入”sh” 之后，成功的获取了设备完整的shell，并且支持的可执行的命令也变多了。

[![](https://p1.ssl.qhimg.com/t01b4488f5d89da4a07.png)](https://p1.ssl.qhimg.com/t01b4488f5d89da4a07.png)

[![](https://p1.ssl.qhimg.com/t0188a823a0d240dd88.png)](https://p1.ssl.qhimg.com/t0188a823a0d240dd88.png)

busybox

[![](https://p5.ssl.qhimg.com/t01b35fa4677a4ad31d.png)](https://p5.ssl.qhimg.com/t01b35fa4677a4ad31d.png)



## 0x04 开启设备telnet

到这里我已经能通过UART串口获取设备的shell了，但是进入设备shell 过于复杂，并且我也不满足于UART的shell， 于是接着我尝试开启设备的ssh 、 telnet 的shell。我在测试的过程中，执行/bin/文件中的telnetd 毫无反应，并且执行busyBox 中的telnetd 也同样显示错误，我开始猜测开发者可能将telnetd做了更改，导致无法正常使用，但是我在 /usr/sbin/文件目录中找到了 utelnetd 可执行文件，并且执行后很明显的开启了23端口进行监听连接。然而一切都不如我所愿，进行登录的时候又显示需要登录口令，我尝试使用UART的弱口令和一些常见的口令也无法进入shell。

[![](https://p2.ssl.qhimg.com/t01eaeae95a6b84b5b3.png)](https://p2.ssl.qhimg.com/t01eaeae95a6b84b5b3.png)

并且我使用google 搜索 NetGear 有没有历史的telnet 口令，在一个论坛中看到了一些信息，但是也依旧没有任何效果。[https://openwrt.org/toh/netgear/telnet.console](https://openwrt.org/toh/netgear/telnet.console)

[![](https://p3.ssl.qhimg.com/t01a37c315aa6bc2007.png)](https://p3.ssl.qhimg.com/t01a37c315aa6bc2007.png)

于是我打算通过UART提供的调试接口直接修改passwd 文件，因为是root 的权限，因此直接更改admin 用户的密码为空。

# cat /etc/passwd<br>
nobody:$1$hFVKPORB$llSaVGwuSWo.CTxU5.Qk30:0:0:nobody:/:/bin/sh<br>
admin:x:0:0:admin:/:/bin/sh<br>
# chmod 777 /etc/passwd<br>
# vi /etc/passwd<br>
# /usr/sbin/utelnetd<br>
telnetd: starting<br>
port: 23; interface: any; login program: /bin/login<br>
更改为如下图所示

[![](https://p0.ssl.qhimg.com/t010ce65df465dc3ff2.png)](https://p0.ssl.qhimg.com/t010ce65df465dc3ff2.png)

然后重新启动utelnetd 服务，使用telnet 连接在输入用户名admin 之后就可以直接获取到shell 。

[![](https://p1.ssl.qhimg.com/t011988e80622f72aa6.png)](https://p1.ssl.qhimg.com/t011988e80622f72aa6.png)



## 0x05 固件提取

由于这款设备的是NetGear 的产品，设备固件都是可以直接下载来的，对这部分不感兴趣的直接跳过。

接下来开始提取设备内部的文件系统，根据前面的查看设备启动时的系统信息，并且配合设备内部的mtd信息分别，确定设备的文件系统是mtd11

[![](https://p4.ssl.qhimg.com/t01913a34aede57ce0a.png)](https://p4.ssl.qhimg.com/t01913a34aede57ce0a.png)

使用dd 命令进行提取，在提取之前要确定空间使用的情况，以免文件太大，文件夹中放不下，如果文件太大，可以考虑将bin 文件进行压缩一下。<br>`dd if=/dev/mtd11 of=/tmp/rootfs_ubifs.bin`

[![](https://p5.ssl.qhimg.com/t010810f39fcdcbbb31.png)](https://p5.ssl.qhimg.com/t010810f39fcdcbbb31.png)

由于设备内有 tftp ，尝试使用tftp 来进行提取dd 转储的bin 文件，但是遗憾的是，tftp 上传文件到本地tftpd server 的文件是设备内部的配置信息。其他的命令也无法正常将文件提取到设备外部。所幸文件系统内部有可以使用的wget 命令，直接上传上传一个对应架构的完整版busybox 到其中，使用完整版的tftp 将文件传出来即可。<br>`tftp -p -t -f rootfs_ubifs.bin 172.15.0.2`

[![](https://p3.ssl.qhimg.com/t014442276fcec2e352.png)](https://p3.ssl.qhimg.com/t014442276fcec2e352.png)

再接下来我们提取设备的非易失性存储器NVRAM（断电之后，所存储的数据不丢失的随机访问存储器）。先将nvram的信息保存，然后使用buybox 的ftp 上传到本地中。<br>
# nvram show &gt; nvram.bin<br>
# strings nvram.bin &gt; nvram.html<br>
成功提取，这里的 WiFi密码和web 管理界面的口令都没有加密，但是路由器忘记密码更改密码的答案给加密了。

[![](https://p5.ssl.qhimg.com/t01a7351339a33a6146.png)](https://p5.ssl.qhimg.com/t01a7351339a33a6146.png)

[![](https://p1.ssl.qhimg.com/t01014adde6d91f4e88.png)](https://p1.ssl.qhimg.com/t01014adde6d91f4e88.png)



## 0x06 固件解包

上面讲述了如何提取设备的固件，但是NetGear 设备固件是开放了，直接去NetGear 官网下载即可。

下载完成之后，这是一个用 .chk 拓展名为结尾的NetGear 固件镜像，那么使用binwalk 查看一下固件包

[![](https://p2.ssl.qhimg.com/t013b4d8fab529ef651.png)](https://p2.ssl.qhimg.com/t013b4d8fab529ef651.png)

使用binwalk -Me 解开固件包,解开固件包之后,可以看到有两个东西, 3A.ubi 文件和 ubifs-root 文件夹, 本以为固件中的文件系统提取到了ubifs-root 中，可以 ubifs-root 文件内没有任何东西。把关注点放在3A.ubi 文件上。

[![](https://p4.ssl.qhimg.com/t01d6870e0029f474da.png)](https://p4.ssl.qhimg.com/t01d6870e0029f474da.png)

解开ubi 文件有两种方法,一个是通过挂载的方式, 一个是使用 ubi_reader 套件来解开，挂载的话过于麻烦，这里使用 ubi_reader 套件来解开. 我们需要[https://github.com/jrspruitt/ubi_reader，可以通过PIP进行安装：](https://github.com/jrspruitt/ubi_reader%EF%BC%8C%E5%8F%AF%E4%BB%A5%E9%80%9A%E8%BF%87PIP%E8%BF%9B%E8%A1%8C%E5%AE%89%E8%A3%85%EF%BC%9A)<br>`sudo pip install ubi_reader`，<br>
使用 ubireader_extract_images 来进行解开ubi 的文件。<br>`ubireader_extract_images 3A.ubi`

[![](https://p3.ssl.qhimg.com/t010f0dd6d6d1a62394.png)](https://p3.ssl.qhimg.com/t010f0dd6d6d1a62394.png)

解开之后 ubifs-root 文件内会生成四个ubifs 的文件

[![](https://p2.ssl.qhimg.com/t01bafed06e9e711345.png)](https://p2.ssl.qhimg.com/t01bafed06e9e711345.png)

根据前面对设备启动时的系统信息分析，rootfs_ubifs.ubifs 就是固件的文件系统。

使用binwalk 进行分析, 识别出来是squashfs 文件系统, 看样子是可以使用binwalk 解开固件

[![](https://p5.ssl.qhimg.com/t0171b6b1b991a2f38a.png)](https://p5.ssl.qhimg.com/t0171b6b1b991a2f38a.png)

成功解开

[![](https://p0.ssl.qhimg.com/t0182604b35a4847fc1.png)](https://p0.ssl.qhimg.com/t0182604b35a4847fc1.png)

[![](https://p2.ssl.qhimg.com/t01371f97798fe4e415.png)](https://p2.ssl.qhimg.com/t01371f97798fe4e415.png)



## 0x07 总结

本片文章主要从设备侧和固件侧，分别讲解了如何通过UART获取设备的shell， 并且通过开启设备telnet , 在有密码的情况下，如何进行处理。以及对 .chk 和ubi 的固件如何进行分析与解包，接下来在漏洞挖掘和分析固件的方面，应该着重于经常产生漏洞的httpd 组件开始，以及比对更新的固件，使用bindiff 进行更新后的固件的比对，找出漏洞点。
