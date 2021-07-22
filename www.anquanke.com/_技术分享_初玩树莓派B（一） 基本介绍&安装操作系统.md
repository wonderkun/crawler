> 原文链接: https://www.anquanke.com//post/id/84695 


# 【技术分享】初玩树莓派B（一） 基本介绍&amp;安装操作系统


                                阅读量   
                                **69256**
                            
                        |
                        
                                                                                    



**[![](https://p3.ssl.qhimg.com/t01acb033645be7f389.jpg)](https://p3.ssl.qhimg.com/t01acb033645be7f389.jpg)**

****

**传送门**

[](http://bobao.360.cn/learning/detail/3051.html)



[****](http://bobao.360.cn/learning/detail/3087.html)

[**【技术分享】初玩树莓派B（二） 实用配置(vnc和串口)&amp;GPIO操作点亮LED灯******](http://bobao.360.cn/learning/detail/3087.html)

[**【技术分享】初玩树莓派B（三） 控制蜂鸣器演奏乐曲******](http://bobao.360.cn/learning/detail/3093.html)

[**【技术分享】初玩树莓派B（四） 人体红外感应报警&amp;物联网温湿度监控******](http://bobao.360.cn/learning/detail/3096.html)



**前言**

之前早就买了一个树莓派B，但是一直没有玩起来。由于以后也准备走嵌入式开发方向。于是先提前把树莓派B玩起来把。

之所以选树莓派是因为国内外玩的人多。中英文资料也很多。为什么不选单片机，单片机可能更多需要了解底层编程，初学者门槛比较高。而对于树莓派来说，不需要对于底层开发或者硬件细节有太多了解，入门门槛较低，可以玩的应用也很多。初玩朋友可以把这个当做一个性能差一点的台式电脑主机，也可以当做性能超强的单片机。<br>特别提示 ：  本人也是刚刚开始玩，不是老手，所以很多情况下也是一知半解，一半测试，一半当做记录做的这个部分，如果资料中有错误或者其他问题，欢迎大家指出。后续会慢慢更新。有些细节的东西可能由于没有用到就部过多讲了。（真的是慢慢更新，因为我也是边玩边学习边记录）。

[![](https://p4.ssl.qhimg.com/t01b35af0a58838b194.png)](https://p4.ssl.qhimg.com/t01b35af0a58838b194.png)

**<br>**

**基本介绍**

树莓派分N多个型号。我买的B型是比较早期的，主频700MHZ（可以超频到1GHZ以上，伤寿命，不建议），512M内存，，VGA，HDMI视频口，以及一个音频口。B版本外接口比较少，USB2个 。GPIO口是26个。目前已经到树莓派3代+，大家要玩可以买最新的，性能更好，接口也更多。具体一些细节可以参看维基 。[https://zh.wikipedia.org/wiki/%E6%A0%91%E8%8E%93%E6%B4%BE](https://zh.wikipedia.org/wiki/%E6%A0%91%E8%8E%93%E6%B4%BE)

[![](https://p2.ssl.qhimg.com/t01e9e2ed176dc17985.png)](https://p2.ssl.qhimg.com/t01e9e2ed176dc17985.png)

图片来源于维基

我初玩购买的设备有：

1 树莓派主机（必备）

2 散热片

3树莓派SD卡和卡套 （其他版本可能不需要卡套，根据需要买卡套）（必备）

4树莓派外壳，保护树莓派

5免驱无线网卡

6 USB转TTL串口调试线 

以下是设备以及当时买的价格（现在买最新的型号也比我的便宜）：

[![](https://p3.ssl.qhimg.com/t010a8dd7ba8818aa21.png)](https://p3.ssl.qhimg.com/t010a8dd7ba8818aa21.png)

[![](https://p5.ssl.qhimg.com/t01a908731fe6adf888.png)](https://p5.ssl.qhimg.com/t01a908731fe6adf888.png)

[![](https://p3.ssl.qhimg.com/t0149b3b9fe76caa174.png)](https://p3.ssl.qhimg.com/t0149b3b9fe76caa174.png)

<br>

**其他类型应用**

树莓派的34个使用（来源 ：[https://linuxtoy.org/archives/cool-ideas-for-raspberry-pi.html](https://linuxtoy.org/archives/cool-ideas-for-raspberry-pi.html)）

如果你手头有一个 Raspberry Pi（树莓派），你会拿它来做什么？或许以下 34 个如何使用 Raspberry Pi 的创意能够给你带来一些启发。

Web 服务器

家庭自动化

BitTorrent 服务器

Web Cam 服务器

天气预报站

BitCoin Wallet

QuadCopter

VoIP PBX

XMBC 多媒体中心

有声书籍播放器

Arduino Shields

NAS 服务器

Apple Time Machine 支持

Tor 中继

家用 VPN 服务器

GPS 跟踪器（带 3G 支持）

Advice Machine（无用但很酷）

模拟输入

超级电脑

Kindle 作为显示屏

PIC Programmer

PenTesting/Hacking

Android 系统

检查网络状态

Solar 数据记录器

把我发到太空

咖啡

制作一个酷坦克

电子相框

添加 WiFi

OpenSource Kiosk

Node JS

流量监视

超频 

<br>

**在官网下载img镜像**

树莓派的官方网址是 [https://www.raspberrypi.org/](https://www.raspberrypi.org/)

树莓派既可以从0开始做系统玩起。也可以基于已有的系统玩。初学这个肯定是基于已有的系统玩。后续可以自己编译内核，调试内核，构建自己的rootfs。我也会介绍介绍基础的一些命令，也是边学边用。顺带讲一些linux自己了解的知识。如果有错误麻烦各位看官指出。为了方便学习树莓派以及linux,同时也方便和树莓派用一些东西沟通。我PC装的是乌班图（不要吐槽为什么不装debian）。我的是Ubuntu 14.04版本，之前装了16.x发现有些东西比如脚本或者python不兼容什么的，所以换回来了。不要装太新的版本。基于已有的系统玩，首先是为树莓派安装官方的系统。不用接触太多的硬件。通过SD卡刷入系统。

SD卡通过USB读卡器接入 PC。

树莓派镜像下载：[https://www.raspberrypi.org/downloads/](https://www.raspberrypi.org/downloads/)

有很多种已经编译好的IMG，正统的noobs和raspbian.下面是第三方的映像

[![](https://p2.ssl.qhimg.com/t0130d3f27cc7b432fe.png)](https://p2.ssl.qhimg.com/t0130d3f27cc7b432fe.png)

我选择的是raspbian.这是亲儿子。系统 和 我的PC ubuntu一样，命令什么的都可以通用。Raspbian 也分为完整版本和轻量级(lite)的版本。

[![](https://p5.ssl.qhimg.com/t01eab992af0e6fd8b5.png)](https://p5.ssl.qhimg.com/t01eab992af0e6fd8b5.png)

我选择完整版本，也就是第一个。压缩前挺小的。解压后映像文件4G多。我下载的版本是2016-03-18-raspbian-jessie的版本，下载完成后记得验证一下sha1，上图下面就带有sha1. 如果映像不对。烧到SD卡很可能起不来验证的是压缩前的文件,也就是下载下来的，不是解压后的。

验证的命令是   

```
#sha1sum filename
```



[![](https://p3.ssl.qhimg.com/t01b6499ac0ec8508a8.png)](https://p3.ssl.qhimg.com/t01b6499ac0ec8508a8.png)

**<br>**

**准备烧入系统** 

先了解一下这个系统

前面的映像解压以后应该是一个img文件。这个img文件主要由两部分组成：

第一部分是boot分区，fat32格式。包含linux内核,设备树，命令行以及配置文件等。这个分区是windows下也可以识别修改的，我们对于树莓派的配置可以操作修改这些文件。

第二部分是 ext4格式的rootfs，也就是根文件系统。

双击这个img文件，ubuntu会帮你识别并且挂载起来

[![](https://p4.ssl.qhimg.com/t017235042edb38122c.png)](https://p4.ssl.qhimg.com/t017235042edb38122c.png)

也可以通过fdisk命令查看

```
#fdisk -l 2016-03-18-raspbian-jessie.img
```



Disk 2016-03-18-raspbian-jessie.img: 4033 MB, 4033871872 bytes 

255 heads, 63 sectors/track, 490 cylinders, total 7878656 sectors 

Units = sectors of 1 * 512 = 512 bytes 

Sector size (logical/physical): 512 bytes / 512 bytes 

I/O size (minimum/optimal): 512 bytes / 512 bytes 

Disk identifier: 0x8f1eafaf 

                         Device Boot      Start         End      Blocks   Id  System 

2016-03-18-raspbian-jessie.img1            8192      131071       61440    c  W95 FAT32 (LBA) 

2016-03-18-raspbian-jessie.img2          131072     7878655     3873792   83  Linux 

树莓派是开源开发板，但并不是完全开源的开发板，初始的启动部分，固化在ROM里面，不能修改，所以一般树莓派除非硬件损坏。否则是不会被你刷坏之类的。

有必要先了解一下树莓派的基本启动过程才能直到各种文件的基本作用：

CPU上电-&gt;初始启动ROM代码-&gt;挂载第一部分fat32 boot分区-&gt;加载bootcode.bin-&gt;调用start.elf

start.elf 读取config.txt初步初始化，比如根据config.txt里面的配置为GPU分配内存等，随后加载kernel.img 也就是linux内核，传入cmdline.txt内核命令参数启动内核。内核根据参数找到rootfs，启动整个系统。其中ROM 里面的代码以及start.elf 这些都不是开源的，在官网提供的firmware里面提供，这也是喜欢纯开源的朋友喷树莓派的地方。

了解了系统启动过程再回头来看第一部分里面的一些文件 ：

overlays是一些扩展设备的设备树文件。

dtb文件是不同版本树莓派板子的设备树。

Bootcode.bin 是启动start.elf的

Start.elf等 是树莓派用来加载内核以及基础初始化的。

Kernel.img是linux内核的映像（zImage+dtb引导文件。暂时没具体看。官方有工具从zImage制作kernel.img）

cmdline.txt 是linux内核启动的参数。

Config.txt是树莓派的配置文件。比如GPU分配多少内存。显示输出采用什么模式。如果配置不当。接入显示器后可能无法正常显示

不同的文件只是为了适应不同的板子，不是所有的文件都需要，比如我的树莓派B型就只需要

bcm2708-rpi-b.dtb

bootcode.bin

cmdline.txt

config.txt

kernel.img

start.elf

就可以启动了。

准备开始烧入系统了。SD卡插入读卡器接入PC ubuntu上，如何找到你的设备呢？

在没插入读卡器之前先使用 ls查看本机设备<br>

```
# ls /dev/sd* 
/dev/sda   /dev/sda2  /dev/sdb   /dev/sdb2  /dev/sdc1  /dev/sdc3  /dev/sdc5  /dev/sdc7 
/dev/sda1  /dev/sda5  /dev/sdb1  /dev/sdc   /dev/sdc2  /dev/sdc4  /dev/sdc6  /dev/sdc8
```

linux磁盘设备用sd[a-z][1-9]        [a-z] 表示磁盘个数  [1-9]表示磁盘的分区个数<br>

这里是/dev/sda /dev/sdb/dev/sdc 说明我有三块硬盘（为啥有三块？ 一块SSD 250G mini ssd 两块1T机械盘，一个硬盘位，一个光驱位 ）<br>接着插入sd卡。再次使用

```
ls /dev/sd* 
/dev/sda   /dev/sda5  /dev/sdb2  /dev/sdc2  /dev/sdc5  /dev/sdc8  /dev/sdd2 
/dev/sda1  /dev/sdb   /dev/sdc   /dev/sdc3  /dev/sdc6  /dev/sdd 
/dev/sda2  /dev/sdb1  /dev/sdc1  /dev/sdc4  /dev/sdc7  /dev/sdd1
```



发现多出来了 /dev/sdd。说明新插入的SD卡就是/dev/sdd。这一步很重要。确定SD卡对应的设备。后续别直接烧入到你其他盘了

接下来使用dd命令将img烧入设备<br>

```
#sudo dd if=2016-03-18-raspbian-jessie.img of=/dev/sdd bs=65536
```

无尽的等待。。。。。。 dd是没有提示的。中途不要拔出设备。等待完毕就好了

if=input filename

of=output filename<br>bs表示一次读取或者写入的字节数。这里不是越高越快，我一般设置为64KB

最后的结果<br>

[![](https://p5.ssl.qhimg.com/t014f146ee3220ef4f5.png)](https://p5.ssl.qhimg.com/t014f146ee3220ef4f5.png)

5.7MB/S很慢了。我这个是拿普通的SD卡演示的。

windows上就简单了，使用win32diskimager 选择你的盘符和 img。点击write就行了，还能看到进度。这点比linux好。<br>如果一切正常。烧入完毕后。将SD卡接入树莓派的卡槽。为树莓派通上电源（一般的手机充电器就行），你的树莓派就可以启动了。

[![](https://p3.ssl.qhimg.com/t01c65119e001051d00.png)](https://p3.ssl.qhimg.com/t01c65119e001051d00.png)

图：电源和SD卡



**检查状态**

目前我们并没有任何显示器能查看启动状况。唯一可以看的是树莓派的指示灯。

[![](https://p2.ssl.qhimg.com/t01a6d455d47f1b16b1.png)](https://p2.ssl.qhimg.com/t01a6d455d47f1b16b1.png)

如果绿灯中途有不停地闪烁，表明在读取SD卡。应该就是OK了。我们这时候再接上网线，或者先接网线再接电源也可以。如果橙色的LNK灯亮了，表明有网络了。等两分钟，运行稳定的时候再查看，状态应该是 ACT灯偶尔闪烁，一般是不亮的。其他四个灯是常亮的。

[![](https://p2.ssl.qhimg.com/t0139cb372f121c6bf9.png)](https://p2.ssl.qhimg.com/t0139cb372f121c6bf9.png)

效果不清楚 还是可以看出四个灯都亮了。此时ACT灯是灭的。我登录上路由器看看分配了IP没有。或者用nmap扫描一下 <br>

```
#nmap 192.168.1/24
```

按照你的局域网扫。我的是192.168.1.x

结果如图：

[![](https://p5.ssl.qhimg.com/t015e80eac2fe2ba4ba.png)](https://p5.ssl.qhimg.com/t015e80eac2fe2ba4ba.png)

192.168.1.1是路由

192.168.1.4是我PC ubuntu<br>

还有一个是 192.168.1.9 肯定就是树莓派了 。直接登陆路由查看ip是最方便的。我这边已经直接识别设备了

[![](https://p5.ssl.qhimg.com/t01bfb605dc53b853c7.png)](https://p5.ssl.qhimg.com/t01bfb605dc53b853c7.png)

nmap可以查看到 默认开了22号ssh端口。我们登陆上去看看 

默认用户名 pi

密码 raspberry

ssh 用户名@ip

```
#ssh pi@192.168.1.9
```

提示信任这个链接。输入yes继续<br>

[![](https://p0.ssl.qhimg.com/t01399830c088b10358.png)](https://p0.ssl.qhimg.com/t01399830c088b10358.png)

输入密码raspberry (注意linux输入密码的时候是看不见有变化的。只管输入按回车确认就行)，OK登陆成功了。

[![](https://p1.ssl.qhimg.com/t0184650e03e07deebf.png)](https://p1.ssl.qhimg.com/t0184650e03e07deebf.png)

配置静态ip，配置wifi、ip和其他登陆方式以及基本的串口连接在下一集哦。

<br>

****

****

**传送门**

[](http://bobao.360.cn/learning/detail/3051.html)



[****](http://bobao.360.cn/learning/detail/3087.html)

[**【技术分享】初玩树莓派B（二） 实用配置(vnc和串口)&amp;GPIO操作点亮LED灯******](http://bobao.360.cn/learning/detail/3087.html)

[**【技术分享】初玩树莓派B（三） 控制蜂鸣器演奏乐曲******](http://bobao.360.cn/learning/detail/3093.html)

[**【技术分享】初玩树莓派B（四） 人体红外感应报警&amp;物联网温湿度监控******](http://bobao.360.cn/learning/detail/3096.html)


