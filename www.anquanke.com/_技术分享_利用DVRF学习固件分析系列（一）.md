> 原文链接: https://www.anquanke.com//post/id/84580 


# 【技术分享】利用DVRF学习固件分析系列（一）


                                阅读量   
                                **174202**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p4.ssl.qhimg.com/t01128307867dd4ad1e.jpg)](https://p4.ssl.qhimg.com/t01128307867dd4ad1e.jpg)**

**作者：**[**赏金流浪客**** **](http://bobao.360.cn/member/contribute?uid=1350341956)

**稿费：500RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿**

**<br>**

**前言**

随着各种硬件设备漏洞越来越被人们关注，以及被恶意攻击者大量利用。作为一个安全研究员，学习分析固件漏洞，及时预警修补漏洞变得越来越重要。这个系列文章将通过利用DVRF来一步一步的深入固件分析，笔者也是一位初学者，记录在学习的过程中遇到的一些问题，希望与大家一起进步。

DVRF是一个非常好的项目，这个项目的目的是来帮助人们学习X86_64之外其他架构环境，同时还帮助人们探索路由器固件里面的奥秘。

<br>

**前期环境准备**

由于此步骤非常简单，相信有点基础的同学都能够搞定，因此我就不细说这个过程，只要你按照我给的环境配置和命令就不会出问题，如有问题，请在文章评论中留言或者给我发邮件。

**1.虚拟机配置**

windows 8.1

VMware 12.1.0 build-3272444(其他版本也可以)

内存 2G

硬盘 30G

**2.系统配置**

做为墙内用户首先修改软件源，科大源，[详细步骤](https://lug.ustc.edu.cn/wiki/mirrors/help/ubuntu)

安装[qemu](http://www.qemu.org/)

```
sudo apt-get install qemu-user-static
```

安装[Binwalk](http://binwalk.org/) 

```
mkdir binwalk
       cd binwalk
       wget https://github.com/devttys0/binwalk/archive/master.zip
       unzip master.zip
       cd binwalk-master
       sudo python setup.py install
       sudo add-apt-repository ppa:openjdk-r/ppa
       sudo apt-get update
       sudo apt-get install openjdk-7-jdk
       sudo ./deps.sh[object Object]
```

安装vmware-tools

如图中步骤解压vmware-tools到home目录

[![](https://p2.ssl.qhimg.com/t0181e148cda00fe3dd.png)](https://p2.ssl.qhimg.com/t0181e148cda00fe3dd.png)

```
cd ~/vmware-tools-distrib/
       sudo ./vmware-install.pl
```

然后一直yes或者enter，最后重启系统。

安装DVRF

下载DVRF [https://github.com/praetorian-inc/DVRF](https://github.com/praetorian-inc/DVRF)

       [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010f2bb9f8a5a5bd82.png)

 <br>

拷贝下载好的压缩包到虚拟机home目录下



```
cd ~
       unzip DVRF-master.zip
```

[![](https://p3.ssl.qhimg.com/t01e209b12912371da1.png)](https://p3.ssl.qhimg.com/t01e209b12912371da1.png)

安装buildroot（2016.05版本）



```
cd ~
       mkdir buildroot
       cd buildroot
       wget https://buildroot.org/downloads/buildroot-2016.05.tar.gz
       tar zxf buildroot-2016.05.tar.gz
       cd buildroot-2016.05
       sudo apt-get install ncurses-dev
       make menuconfig
```

[![](https://p5.ssl.qhimg.com/t016adfe6171003b4bd.png)](https://p5.ssl.qhimg.com/t016adfe6171003b4bd.png)

[![](https://p2.ssl.qhimg.com/t01d1713b74d10540e5.png)](https://p2.ssl.qhimg.com/t01d1713b74d10540e5.png)

[![](https://p5.ssl.qhimg.com/t014e87d30396ad78bf.png)](https://p5.ssl.qhimg.com/t014e87d30396ad78bf.png)

打开gdb远程调试功能       

[![](https://p5.ssl.qhimg.com/t017ff31fbd015fac1d.png)](https://p5.ssl.qhimg.com/t017ff31fbd015fac1d.png)

修改gdb版本为7.10.x，并保存配置。       

[![](https://p5.ssl.qhimg.com/t017ada05be0fb6614a.png)](https://p5.ssl.qhimg.com/t017ada05be0fb6614a.png)

make，等候下载，大约半小时。



**<br>**

**牛刀小试**

**1.binwalk使用**

分析出固件镜像为linux 的小端系统，文件系统是squashfs文件系统   

[![](https://p1.ssl.qhimg.com/t01f4c103e469b81a2e.png)](https://p1.ssl.qhimg.com/t01f4c103e469b81a2e.png)

解压提取固件文件系统

```
binwalk -Me DVRF_v03.bin
```

[![](https://p4.ssl.qhimg.com/t01b0446af692fab8a0.png)](https://p4.ssl.qhimg.com/t01b0446af692fab8a0.png)

[![](https://p1.ssl.qhimg.com/t01c1bc2d5efd54ab6e.png)](https://p1.ssl.qhimg.com/t01c1bc2d5efd54ab6e.png)

通过file命令查看文件信息，发现文件格式为mips32小端文件。

[![](https://p5.ssl.qhimg.com/t01a3d71e279ea25071.png)](https://p5.ssl.qhimg.com/t01a3d71e279ea25071.png)

**2.qemu模拟运行mips程序**

复制相应的qemu模拟程序到指定目录 

[![](https://p2.ssl.qhimg.com/t014a80fd11faae23ce.png)](https://p2.ssl.qhimg.com/t014a80fd11faae23ce.png)

使用qemu运行mips程序

```
sudo chroot ../qemu-mipsel-static ./pwnable/Intro/stack_bof_01 test123
```

[![](https://p5.ssl.qhimg.com/t012ff2f76b3fbe2236.png)](https://p5.ssl.qhimg.com/t012ff2f76b3fbe2236.png)

**3.使用qemu和gdb调试mips程序**

运行程序并打开1122端口用于gdb调试

```
sudo chroot . ./qemu-mipsel-static -g 1122 ./pwnable/Intro/stack_bof_01 test123
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0159dc7f49eb952811.png)

新窗口中使用buildroot中的mipsel-linux-gdb连接1122开始调试



```
cd ~
    cd buildroot/buildroot-2016.05/output/host/usr/bin/
    ./mipsel-linux-gdb
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01802c4a4e888dd55c.png)

当窗口2中gdb使用c命令让程序继续运行的时候，窗口1中程序继续执行。



**总结**

本文简单讲解了DVRF的测试环境安装与使用，分别包括DVRF、binwalk、qemu、buildroot、gdb等相关工具。这个系列第二篇将讲述mips 程序的相关知识，有点基础的同学都知道mips程序在固件中被广泛运用。
