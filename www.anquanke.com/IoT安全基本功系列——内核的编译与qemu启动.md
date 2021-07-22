> 原文链接: https://www.anquanke.com//post/id/228780 


# IoT安全基本功系列——内核的编译与qemu启动


                                阅读量   
                                **118754**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0123733cd956ea28a7.jpg)](https://p0.ssl.qhimg.com/t0123733cd956ea28a7.jpg)



## 搞IoT安全绕不开的知识

笔者想要完整的整理linux系统从内核的编译，文件系统的制作，bootloader引导内核启动，最终至一个块设备，字符设备，网卡驱动的编写。做这件事的目的是，笔者发现对于IoT设备的固件模拟，在开机时获取root shell，以及驱动作为攻击面的漏洞挖掘等方面的工作，都绕不开这块内容。



## 为什么要写这个系列文章

本篇文章有可能是一个系列的开篇文章，市面上貌似对这块内容的文章资料总让我感觉是破碎不够系统的，而且实操性或者准确性上都有些问题，笔者虽能力有限，将尽力能够让新手读者看了本文就能够实践出来，本文也是笔者在实践过程中的实录，包括自己踩的坑，以及如何解决的这个的思路历程也记录了下来，所以本系列文章非常适合同学们实践参考。



## 系列文章的最终目的

本系列文章的最终目的是能够编写一个真正的驱动程序，而驱动程序的编写本文选择参考ldd3即 **linux设备驱动程序**这本书，由于这本书的内核比较老，现在的内核都已经不再支持书上的例程，如果拿着书上的例程去在当前内核下做实验的话，会出现很多莫名的坑，为了降低学习曲线，但又把一些基本linux启动等流程说清楚，尝试就在ldd3指定的内核linux 2.6.10版本上搭建学习开发环境。



## 本文的目标

由于上述的内容一篇文章是很难讲完，本文先讲第一部分，qemu上运行自己编译的linux 2.6.10内核。其具体包括:

1.构建编译ldd linx 2.6.10内核的环境

2.编译内核，构建文件系统

3.qemu运行系统

### <a class="reference-link" name="1.%20%E6%9E%84%E5%BB%BA%E7%BC%96%E8%AF%91ldd%20linx%202.6.10%E5%86%85%E6%A0%B8%E7%9A%84%E7%8E%AF%E5%A2%83"></a>1. 构建编译ldd linx 2.6.10内核的环境

1.linx 2.6.10内核非常老，我建议使用ubuntu5.0的镜像 镜像地址：[http://old-releases.ubuntu.com/releases/5.04/](http://old-releases.ubuntu.com/releases/5.04/)

2.ubuntu5.0也非常老，我直接使用vmware安装有问题，无法检测到cd-rom 使用老版本的支持workstation

[![](https://p1.ssl.qhimg.com/t01b78f11b160f9408f.png)](https://p1.ssl.qhimg.com/t01b78f11b160f9408f.png)

选择workstation 5.x是可以安装的

3.后来字ubuntu5.0启动界面发现他使用的就是linux2.6.10

4.安装完毕

[![](https://p5.ssl.qhimg.com/t01595f7776c9fd3dfe.png)](https://p5.ssl.qhimg.com/t01595f7776c9fd3dfe.png)

5.还需要安装gcc， gcc deb文件[http://launchpadlibrarian.net/1299681/gcc-3.3_3.3.5-8ubuntu2_i386.deb](http://launchpadlibrarian.net/1299681/gcc-3.3_3.3.5-8ubuntu2_i386.deb) ， 使用dpkg -i安装这个deb文件，然后还需要在/usr/bin中创建 gcc的软链接，因为这个deb是一个gcc3.3命名的

### <a class="reference-link" name="2.%20%E7%BC%96%E8%AF%91%E5%86%85%E6%A0%B8%EF%BC%8C%E6%9E%84%E5%BB%BA%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F"></a>2. 编译内核，构建文件系统

1.找到linux2.6.10内核代码

链接内核代码：[https://mirrors.edge.kernel.org/pub/linux/kernel/v2.6/linux-2.6.10.tar.gz](https://mirrors.edge.kernel.org/pub/linux/kernel/v2.6/linux-2.6.10.tar.gz), 其大小为43.7MB， 可以尝试使用ftp从host宿主机上下载代码，因为安装老版本的vmtools比较麻烦。<br>
make的时候要用`make ARCH=i386 defconfig`，因为menuconfig需要nurses那个库，安装这个库挺麻烦的对于老版本，遂决定放弃好用的`menuconfig`，毕竟我们的目的是编译成功。

2.initramfs根文件系统
- 在挂载磁盘上的文件系统之前，需要先挂载一个initramfs文件系统，因为磁盘上的文件系统需要驱动，而驱动的加载也需要文件系统，这是一个鸡蛋问题，所以不能一开始就加载磁盘上的文件系统。 initramfs这个文件系统的加载不需要驱动，可以在这个文件系统里启动基本的挂载磁盘的驱动，initramfs是由bootload加载到内核中的。具体的，initramfs 就是一些文件的 cpio压缩包，由bootloader将其加载后供kernel使用，只要你往initramfs中添加的文件够多，那么你甚至不需要磁盘上的文件系统这就是为什么大家喜欢用busybox去创建initramfs，当加载driver的时候，喜欢把driver写入到initramfs中，所以以后再更新module的时候，不用重新编译内核，只需要编译一下module，然后把他放到内核中就行了。
3.使用busybox 构建initramfs根文件系统

```
同样的需要下载busybox的源码，我选择的是2004年的busybox-1.00.tar.bz2  ，并且需要在ubuntu5.0上编译，新版本的gcc都是不能用的。  
需要注意的是在由于不能使用menuconfig，只能使用config，要注意在后面可以选择作为一个static 编译
然后正常编译 make
make install得到这个文件目录
```

### <a class="reference-link" name="3.%20qemu%E8%BF%90%E8%A1%8C%E7%B3%BB%E7%BB%9F"></a>3. qemu运行系统

一开始参考的是这篇文章，[https://consen.github.io/2018/01/17/debug-linux-kernel-with-qemu-and-gdb/](https://consen.github.io/2018/01/17/debug-linux-kernel-with-qemu-and-gdb/)

1.在搞这一块的遇到了很多问题，现在罗列

```
qemu是否是起到了bootloader的作用？
内核在和initrd 或者initramfs交互的时候是做了什么？
文件系统是如何被初始化的？
initrd和initramfs在本质上的区别？
真实设备的linux启动的流程是什么？
vmlinux与最终zimage的差别？
qemu运行一个vmlinux没有任何反应，不知道是不是我的vmlinux有问题，还是qemu不能启动vmlinux？
上面那个文档可以生成initramfs文件系统，但是却不能生成initrd， 这个busybox生成很少见
我用qemu启动的时候到底需要些什么？
dtb， dts 设备树又是啥？
ttys0是干啥的？
```

2.解决qemu运行vmlinux没有任何反应的问题

参考: [https://freemandealer.github.io/2015/10/04/debug-kernel-with-qemu-2/](https://freemandealer.github.io/2015/10/04/debug-kernel-with-qemu-2/)

尝试用新的编译好的bzimage和vmlinux.bin,就在arch i386目录下的

结果新生成的bzimage和vmlinux 在qemu下运行同样的没有任何反应，运行的命令`qemu-system-i386 -kernel ./bzImage -nographic`

[![](https://p4.ssl.qhimg.com/t019197bfa17ef8967d.png)](https://p4.ssl.qhimg.com/t019197bfa17ef8967d.png)

只有在运行bziamge的时候才会出现这个界面，而且还是要运行下面这命令 `qemu-system-i386 -kernel ./bzImage -append "console=ttyS0"`

从这个截图可以看出,qemu貌似是使用了seabios这个bootloader去加载内核的

还是卡在启动内核上，从这个图看出内核貌似根本没有任何输出的，我想还是用一个别人编译的例子

后来找到一个帖子说之所出现内核太老不支持ramfs，并不是因为2.6太老，而是因为使用的是vmlinux作为内核启动的，而不是使用的bzimage

直接使用vmlinux作为内核在qemu中启动的结果就是下面这样的

[![](https://p5.ssl.qhimg.com/t0172d209fc1f121379.png)](https://p5.ssl.qhimg.com/t0172d209fc1f121379.png)

所以问题还是出现在为什么我编译的固件就一直卡在boot kernel上面

找到了一个qemu启动linux 2.6.32的老帖子 [https://www.cnblogs.com/senix/archive/2013/02/21/2921221.html](https://www.cnblogs.com/senix/archive/2013/02/21/2921221.html)

我决定按照他的构建initrd的方法再来一遍，以确定只有可能是内核编译的问题

按照这个文档的方法是可以的没有问题的，但是还是报出错误

[![](https://p4.ssl.qhimg.com/t01066656301dd0a336.png)](https://p4.ssl.qhimg.com/t01066656301dd0a336.png)

显示`vfs unable to mount root fs on`

这串输出都是内核的代码输出，我在内核的源代码中搜到了这句话

后来发现之前编译的initramfs.cpio.gz也是可以启动内核的，只不过因为我加了一句console=ttyS0，导致看不到输出，我觉着实际上是由输出的，我觉着`console=ttyS0`的意思就是把显示放到了串口，导致在当前这个console是看不到的，显然在很多串口的地方就是把console给定位到了ttyS0，而由于我的qemu没有这个串口，所以应该就不需要设置这个玩意

目前看来还是这个文档最好用，我是通过搜linux 2.6和qemu关键词搜到的，虽然是很久之前的文章，但是真的还挺有用的，起码这个构建文件系统的是可以的

4.现在的问题是解决为何识别不了这个initrd或者叫做initramfs的东西

目前已经发现内核的启动是很随意的，不要文件系统什么东西的，直接 `qemu-system-i386 -kernel bzImage` 就可以启动

由上面这个无法识别root device ram可以知道，这个文件系统应该是没有起到效果，或者是dev没启动起来

有可能是编译内核的时候没有启用支持ramdisk，根据这篇链接[google 搜索cannot open root device “ram”](https://www.yoctoproject.org/pipermail/yocto/2013-April/012949.html)

> <p>The most obvious question is whether or not the kernel you built has<br>
ramdisk support</p>

```
$ grep BLK_DEV_RAM .config
        CONFIG_BLK_DEV_RAM=y
        CONFIG_BLK_DEV_RAM_COUNT=16
        CONFIG_BLK_DEV_RAM_SIZE=4096
```

我去看了一下发现我的linx 2.6.10版本并没有启用这个dev/ram这个设备，我的一开始并没有设置BLK_DEV_RAM，后来我才加上去了

[![](https://p2.ssl.qhimg.com/t01105d66acfed888a9.png)](https://p2.ssl.qhimg.com/t01105d66acfed888a9.png)

重新编译发现需要的事件很短，看来是之前的已经编译好了，只需要编译新的东西就行了，这就是增量编译吧,重新放入新的bzimage试一下已经发现不再报ram的错误，但是开始报UDF-fs no partition found错误, 而且发现defconfig的UDF-FS也是已经配置的，禁用之后，还是报无法识别block的错误，确定就是没有成功加载提供的initrd文件系统,现在越来越觉着就是cpio这种形式的initrd， 内核是不支持的

> initRamFS is a (compressed) CPIO archive, InitRD is a (compressed) ext2/3/4/jfs/xfs/whatever filesystem

参考自[https://lists.nongnu.org/archive/html/qemu-devel/2013-10/msg01445.html](https://lists.nongnu.org/archive/html/qemu-devel/2013-10/msg01445.html)

5.尝试编译新的内核，完全参照老帖子

参考 [https://www.cnblogs.com/senix/archive/2013/02/21/2921221.html](https://www.cnblogs.com/senix/archive/2013/02/21/2921221.html)

首先下载 linux-2.6.32.60.tar.bz2 [链接](http://ftp.jaist.ac.jp/pub/Linux/kernel.org/linux/kernel/v2.6/longterm/v2.6.32/)

用适配性高的内核启动我编译的各种文件系统，观察是否能起来

rootfs.img.gz这个是按照教程生成的gz格式的文件系统，是可以起来的

rootfs.img 这个是没有压缩的文件系统，也是可以起来的

initd.gz 和 initrd都没起来，这个是仿照 [https://www.cnblogs.com/shineshqw/articles/2336842.html，](https://www.cnblogs.com/shineshqw/articles/2336842.html%EF%BC%8C) 但是新内核的输出貌似是试了ext3 vfat msdos iso9660这几种文件系统，但是都没有成功，而我制作的是ext2的，所以我觉着可以用ext3尝试一下

6.尝试各种创建initrd的办法

参照官方的老帖子，32.60版本的内核可以成功启动，loop device [https://web.archive.org/web/20150402090928/https://www.kernel.org/doc/Documentation/initrd.txt](https://web.archive.org/web/20150402090928/https://www.kernel.org/doc/Documentation/initrd.txt)

7.最终解决了问题

发现是linux 2.6.10 缺少了对initrd的支持,并不是那个ram_dev设置就支持了,还有一个CONFIG_BLK_DEV_INITRD, 这个在i386defconfig默认配置中是根本没有的，需要自己手动加上<br>`CONFIG_BLK_DEV_INITRD=y`



## 结语

本文是笔者在尝试在qemu上运行linux 2.6.10版本内核的实录包括自己在时间时候遇到的各种问题，最终完整编译linux 2.6.10内核，并且通过很多尝试最终发现i386的默认配置是缺少initrd支持的问题的，虽然不是按部就班的给出最优解，但是详细的叙述解决过程，可能对大家更有参考性。
