> 原文链接: https://www.anquanke.com//post/id/84706 


# 【技术分享】初玩树莓派B（二） 实用配置(vnc和串口)&amp;GPIO操作点亮LED灯


                                阅读量   
                                **69085**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t0183b42607412c8041.jpg)](https://p4.ssl.qhimg.com/t0183b42607412c8041.jpg)



**传送门**

[](http://bobao.360.cn/learning/detail/3051.html)

[**【技术分享】初玩树莓派B（一） 基本介绍&amp;安装操作系统**](http://bobao.360.cn/learning/detail/3085.html)

[**【技术分享】初玩树莓派B（三） 控制蜂鸣器演奏乐曲**](http://bobao.360.cn/learning/detail/3093.html)

[**【技术分享】初玩树莓派B（四） 人体红外感应报警&amp;物联网温湿度监控**](http://bobao.360.cn/learning/detail/3096.html)

**<br>**

这一节讲的实用应用配置，并不是前面提到的配置/boot分区下面的那些config.txt配置显示器啊，GPU什么的。因为这个叫初玩，主要走实用的路线。所以讲的都是实用性配置。

<br>

**串口调试接入树莓派**

使用的线有USB转TTL线

[![](https://p3.ssl.qhimg.com/t0189f442e04a25a854.png)](https://p3.ssl.qhimg.com/t0189f442e04a25a854.png)

一般是红、黑、白、绿四色。

红色 电源线是不需要使用的。只需要使用其他三根线。

白色 是TX 表示传输线

绿色 是RX 表示接收线

黑色 是GND 地线

对照树莓派的默认模式的P1方式就是 

黑色GND=6号

白色TX= 8号

绿色 RX=10号

接上后图片上看起来是

[![](https://p1.ssl.qhimg.com/t017713c4a636a86180.png)](https://p1.ssl.qhimg.com/t017713c4a636a86180.png)

[![](https://p3.ssl.qhimg.com/t011901cb8bf9e531fd.png)](https://p3.ssl.qhimg.com/t011901cb8bf9e531fd.png)

P1排序方式，板子上也能看到P1标记。那里就是1号开头，另一端接ubuntu PC 。一般在pc 设备中体现为/dev/ttyUSB0。

使用 <br>

```
#ls /dev/ttyUSB*
```

/dev/ttyUSB0<br>

查到了这个设备

我们使用putty来连接设备<br>

```
#sudo putty
```



[![](https://p2.ssl.qhimg.com/t018f0e46cb5687db4e.png)](https://p2.ssl.qhimg.com/t018f0e46cb5687db4e.png)

先选择serial,再填写serialline  /dev/ttyUSB0 speed填写115200 open打开，弹出黑框等待数据。这时候我们将树莓派J接电重新启动。就可以从界面看到串口大量打印的信息了，信息有很多。

[![](https://p2.ssl.qhimg.com/t01c7e8f11cdd2ab56c.png)](https://p2.ssl.qhimg.com/t01c7e8f11cdd2ab56c.png)

由于树莓派还开启了串口登陆。所以最终串口状态是等待登陆状态

[![](https://p2.ssl.qhimg.com/t013ae206be71cbb9e0.png)](https://p2.ssl.qhimg.com/t013ae206be71cbb9e0.png)

输入pi密码raspberry登陆，也可以对pi控制

[![](https://p1.ssl.qhimg.com/t01384e46a7be38ce05.png)](https://p1.ssl.qhimg.com/t01384e46a7be38ce05.png)

后续的操作尽量从串口内操作。因为使用ssh 登陆进行一些安装操作会把PC的一些环境，比如语言配置带入到PI上，导致各种问题发生。所以我们后续的操作都在串口下进行。有些图片是以前保存的。并不是直接操作串口的。样子略有不同。



**为树莓派配置静态IP**

前一节用nmap或者路由找到了树莓派的登陆ip。但是IP是DHCP的 ，这样每次启动IP不是固定的。所以我们要配置静态ip。

前面我们通过默认的ssh连接上了 树莓派。因此可以通过修改/etc/network/interfaces来修改

```
#cd /etc/network
```

删除

```
#sudo rm interfaces
```

新建<br>

```
#sudo nano interfaces
```

直接操作输入内容 (eth后面是零 ，不是'O')

auto eth0

iface eth0 inet static

address 192.168.1.9

netmask 255.255.255.0

gateway 192.168.1.1

具体ip根据你的局域网填写

[![](https://p3.ssl.qhimg.com/t0182103c19b9f734ef.png)](https://p3.ssl.qhimg.com/t0182103c19b9f734ef.png)

按ctrl+o 

[![](https://p4.ssl.qhimg.com/t0197f03c1927991978.png)](https://p4.ssl.qhimg.com/t0197f03c1927991978.png)

此时再按回车保存

再按ctrl + x退出

基本的nano操作就是这样。vi编辑器初学比较难使用。rpi提供了nano就简化一点吧。

证明我们写入成功了可以用cat看一看<br>

```
#cat interfaces
```

重启试试有没有配置成功<br>

```
#sudo reboot
```

重启以后过一分钟尝试ping ip。发现已经OK了

[![](https://p1.ssl.qhimg.com/t01b366a56deac56354.png)](https://p1.ssl.qhimg.com/t01b366a56deac56354.png)

说明已经配置成功了。

<br>

**无线配置**

这是有线的配置。要一直连接有线玩树莓派不方便。所以最好用无线。

首先要确认树莓派识别了你插入的USB无线网卡。前面已经提供了一个型号，免驱动的，我们先来查看一下是否识别了<br>

```
#lsusb
```

Bus 001 Device 004: ID 0bda:8176 Realtek Semiconductor Corp. RTL8188CUS 802.11n WLAN Adapter 

Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. SMSC9512/9514 Fast Ethernet Adapter 

Bus 001 Device 002: ID 0424:9514 Standard Microsystems Corp. 

Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

第1个Realtek Semiconductor Corp. RTL8188CUS 802.11n WLAN Adapter 已经识别了我们的无线设备。无需自己编译任何驱动。同样是修改/etc/network/interfaces。只是里面的内容变成了

auto wlan0 

allow-hotplug

iface wlan0  inet static

wpa-ssid "wifissid"

wpa-psk "password" 

address 192.168.1.9

netmask 255.255.255.0

gateway 192.168.1.1

mynetwork 是你的ssid名字。 wpa-psk里面是你的无线的密码。你的无线也要是用psk加密的。

[![](https://p5.ssl.qhimg.com/t01cca82ff853d7a67b.png)](https://p5.ssl.qhimg.com/t01cca82ff853d7a67b.png)

<br>

**扩展树莓派的空间**

使用#df -h查看空间发现 /目录下占用了100%<br>

```
#df -h
```

Filesystem      Size  Used Avail Use% Mounted on 

/dev/root       3.6G  3.4G     0 100% / 

不扩展就没有其他空间装软件了。实际我们的SD卡可能有16G或者32G，所以要用树莓派的配置命令扩展空间。

输入<br>

```
#sudo raspi-config
```

弹出配置界面

[![](https://p2.ssl.qhimg.com/t01c15b170e9acf59b8.png)](https://p2.ssl.qhimg.com/t01c15b170e9acf59b8.png)

第一项 直接按回车。开始扩展，提示扩展完毕。下次重启空间变大了

[![](https://p0.ssl.qhimg.com/t01ad7c1878a952b297.png)](https://p0.ssl.qhimg.com/t01ad7c1878a952b297.png)

后续选择finish。提示你重启。重启就好了，再次

```
#df -h
```

Filesystem      Size  Used Avail Use% Mounted on 

/dev/root        15G  3.4G   11G  25% /

现在我的/目录只用了25%.本来就是16 G的。可以安装更多软件了。

<br>

**为树莓派安装vnc可视化界面**

到现在我们都只用命令行登陆。从没看过树莓派的UI界面。串口登陆以后



```
#sudo apt-get update
#sudo apt-get install tightvncserver
```

<br>

等待tightvncserver安装完毕

安装完毕以后开始配置

手工启动vncserver 端口号为1，这个端口号和TCP UDP不是一个意思

执行<br>

```
#vncserver    :1
```



[![](https://p1.ssl.qhimg.com/t01298a7734899b9fc0.png)](https://p1.ssl.qhimg.com/t01298a7734899b9fc0.png)

首次需要设置密码。密码小于等于8位，需要填写和验证填写多次。

[![](https://p3.ssl.qhimg.com/t01071f86c23bca9e04.png)](https://p3.ssl.qhimg.com/t01071f86c23bca9e04.png)

接下来可以PC机器上用vncview连接了。测试UBUNTU用vncviewer连接

执行vncviewer ip:1<br>

```
#vncviewer 192.168.1.202:1
```



[![](https://p5.ssl.qhimg.com/t019c1abe7593b011e4.png)](https://p5.ssl.qhimg.com/t019c1abe7593b011e4.png)

输入之前设置的密码；登陆成功

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019a364ed949d2f9f5.png)

这个就是树莓派的界面啦。

有条件的可以自己接外接的VGA或者HDMI显示器。同时注意，如果显示有问题，请参考树莓派官方教程对于/boot/config.txt的配置。我们初学没必要再买一个显示器，用本机PC vnc view 玩一玩比较方便实惠.<br>最后  我们需要将vnc服务设置为自动启动。这样，每次树莓派启动以后，都可以用vncviewer登陆查看了。<br>

```
#cd /etc/init.d/
#sudo nano autostartvnc
```

在里面写入内容（这个内容不是标准的启动脚本，标准的有start 和stop等等控制机制，不过我们这是实用简便的方式。关于启动脚本就不多说了）<br>

```
#!/bin/sh
su pi -c "/usr/bin/tightvncserver  :1"
```

保存

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b35051b6518ea79c.png)

设置脚本科执行  并且执行自动启动脚本<br>

```
#sudo chmod +x  autostartvnc
```

需要进入/etc/init.d执行这个目录<br>

```
#sudo update-rc.d  autostartvnc defaults
```



[![](https://p2.ssl.qhimg.com/t018a11b98b6f1ae2cf.png)](https://p2.ssl.qhimg.com/t018a11b98b6f1ae2cf.png)

这样就可以自动启动了，我重启时发现一个错误。VNC没有起来，手工执行可以起来实在是奇怪。串口通过检查.(这时候串口调试作用就很明显了)/home/pi/.vnc/raspberrypi :1.log发现两个错误，一个是 没有75dpi这个字体文件，一个是找不到/home/pi/.Xresources

[![](https://p4.ssl.qhimg.com/t01d249508d422343ff.png)](https://p4.ssl.qhimg.com/t01d249508d422343ff.png)

所以我们解决一下<br>

```
#sudo apt-get install xfonts-75dpi
#touch /home/pi/.Xresources
#cd /etc/init.d
#sudo update-rc.d  autostartvnc defaults
```

再次reboot重启 #vncviewer ip:1 这次可以直接登陆。后续可以用主机直接操作哦。 

最后还可以实用手机登陆并且操作：主要用于查看工作状态。比如树莓派正在一个很长的下载或者编译工作。PC关闭了。我们可以用手机偶尔看看。

手机APP下载： 特别注意。别下国内的那种VNC,。下载vncview官网的。也就是google play的。全称 vnc viewer 。国内有些VNC viewer冒用这个图标，还说是什么加强版，千万别用。这个是全英文的。

[![](https://p5.ssl.qhimg.com/t012bf4fa696bc2d874.png)](https://p5.ssl.qhimg.com/t012bf4fa696bc2d874.png)

创建新的vnc链接点击绿色+号 填入ip 名字。注意ip后面的冒号 和1 别忘了

[![](https://p0.ssl.qhimg.com/t013f183caa8dabbcc7.png)](https://p0.ssl.qhimg.com/t013f183caa8dabbcc7.png)

点击connect

[![](https://p5.ssl.qhimg.com/t0131ce36532ba88748.png)](https://p5.ssl.qhimg.com/t0131ce36532ba88748.png)

输入密码 可以记住密码。点击continue

[![](https://p5.ssl.qhimg.com/t0178a2810774407fbf.png)](https://p5.ssl.qhimg.com/t0178a2810774407fbf.png)

提示警告可以忽略。点击继续

[![](https://p0.ssl.qhimg.com/t01d6fd02ff63ce6230.png)](https://p0.ssl.qhimg.com/t01d6fd02ff63ce6230.png)

可爱的树莓派界面就出来了

[![](https://p4.ssl.qhimg.com/t015a463a2150a52ee4.png)](https://p4.ssl.qhimg.com/t015a463a2150a52ee4.png)

以后只要树莓派接通电源。我们都可以通过操作手机随时登陆看看状态。以后外接硬盘，100M速度整天下小电影。是不是想看看下载了多少了。不用打开PC 登陆。手机就行哦。

最后如果有需要可以为树莓派修改软件源，平时用到安装软件的时候 默认是去树莓派的源下载。速度非常慢。软件更新和下载要等待很久。幸好阿里云提供了这样的国内镜像。有些地区可能阿里云的也不好用。可以搜索其他的源。

先备份一份原有的源.源位置保存在/etc/apt/source.list 里面<br>

```
#cd /etc/apt
#sudo cp sources.list sources.list.bak
```

开始编辑 <br>

```
#sudo nano source.list
```

将里面原来的内容删除。填入阿里云的源

deb http://mirrors.aliyun.com/raspbian/raspbian wheezy main non-free contrib rpi 

开始更新 数据<br>

```
#sudo apt-get update
```

如果无法更新或者失败。将原来的备份还原老老实实从官方源更新。



**了解树莓派B的GPIO**

相信学ardunio或者其他单片机的第一个工作绝对是点亮一个LED灯，就跟C语言的hello world是一个意思，那么这次我们也要尝试用树莓派的GPIO点亮一个LED等。

首先了解GPIO

GPIO（英语：General-purpose input/output），通用型之输入输出的简称，功能类似8051的P0—P3，其接脚可以供使用者由程控自由使用，PIN脚依现实考量可作为通用输入（GPI）或通用输出（GPO）或通用输入与输出（GPIO），如当clk generator, chip select等。

既然一个引脚可以用于输入、输出或其他特殊功能，那么一定有寄存器用来选择这些功能。对于输入，一定可以通过读取某个寄存器来确定引脚电位的高低；对于输出，一定可以通过写入某个寄存器来让这个引脚输出高电位或者低电位；对于其他特殊功能，则有另外的寄存器来控制它们。（来自维基百科的GPIO解释）

初学来说了解GPIO可以理解成由芯片引出的一些外部针脚，至少有两个功能（输入和输出）。输出怎么解释？比如我们外接了一个LED灯，需要CPU控制某个针脚变成高电平为LED提供+电源，这就是输出。输入怎么解释？比如我们外接了一个红外人体感应器。需要CPU从某个针脚检测状态，如果感应到人体，那么某个针脚会变成高电平，这就是输入了。

GPIO的复用指的是某些引脚除了用作普通的输入输出，还有非普通IO的功能性作用。比如用做JATG调试，串口的TX，RX等,但是一个针脚每次只能作为一个功能使用，复用不是说一个针脚同一时间既可以做输入又可以做输出。

也就是说每次使用GPIO之前 需要对要使用的针脚设置对应的模式，才有对应的作用，重启以后又恢复到初始的MODE状态。每个PIN设置为不同的模式有不同的作用。有些针脚是固定的。比如 3.3V 5.5V和GND都是固定的作用，不能作为可以操作的GPIO使用。

首先来看看树莓派B的GPIO 我的PI  B是26针脚的。

树莓派的PIN有很多的编号方式：实质其实没有太多区别，只是不同的编号方式对应的PIN有不同的号码。

假设我们使用的是P1编号的15号PIN（Header一栏中15号） 名字叫GPIO3（名字也可能叫法不同），如果用BCM的标号方式就是22号。如果是WiringPi来操作的话就是3号。使用不同编号方式，PIN的号码可能是不相同的。只要对照了准确的表操作就没有任何问题。

实际图中板子上标号就是P1的编号方式。在python的gpio中就是BOARD模式。后续如果不特别指明。就默认是P1标号方式。从上到下从左到右（我贴的图请你你顺时针转90度再数 QAQ） 编号1-26.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0186738976f722c938.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b52812bae866699a.png)

通过执行

```
 #gpio readall
```

可以准确得到你的主板的GPIO信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01654375df55b5d133.png)

我们先看一看初始的每个PIN模式是什么。这里先看结果。后续会有使用python的读取的源码。

[![](https://p3.ssl.qhimg.com/t016611513a2c323a7b.png)](https://p3.ssl.qhimg.com/t016611513a2c323a7b.png)



这里可以看到 PIN8 和PIN10默认就是串口模式。前面一节调试串口的时候我们并没有设置模式。也可以正常工作就是因为板子启动后，默认 8 10 就是串口模式。其中还有1,2,4,6,9,14,17,20,25号是电源，3.3V 5.5V或者GND。其他的默认是GPIO.IN全部是输入模式，我们点亮LED灯肯定要设置某个针脚为OUT模式。

<br>

**直接点亮一个LED灯**

对照表中可以看到PIN1是3.3V电源正极。PIN6是0V也就是GND 负极。是不是接上一个LED自动就亮了呢？真聪明啊。就是这么接的,但是为了安全起见，还是接一个300左右的电阻吧。3.3/300=0.011A=11ma .这样比较安全。 高中物理这里就不再多说了

需要的材料

1.面包板 （方便插线，不用手动接线）

[![](https://p0.ssl.qhimg.com/t01215f2204f12ad0d6.png)](https://p0.ssl.qhimg.com/t01215f2204f12ad0d6.png)



面包板中间的插孔竖向是相通的，两两不互通。边缘的插孔横向是相通的，两两不互通。

2.公对母杜邦线2条 

[![](https://p2.ssl.qhimg.com/t0184f5b1f36ffb6fec.png)](https://p2.ssl.qhimg.com/t0184f5b1f36ffb6fec.png)

<br>

公母很好分。公的是插别人的。母的是被插的。（自觉面壁两分钟）当然杜邦线还有 公-公 母-母的。因为便宜。买的时候多买一些没关系。

3.LED灯一个（参考电压3.0-3.2V）电流5-20 ma

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011fe8f2022426d45b.png)

<br>

注意LED的正负。如何区分？

第一种：引脚较长的是正，引脚较短为负，图中可以看出负极较短。

第二种：看灯头里面分为两部分，较大的一部分连着负极。较小的一部分连着正极

4.300欧姆左右的电阻一个

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013e371729beedbbff.png)



这个没啥好说的。接线PIN1 （3.3V正极）——–电阻——LED正极——–LED负极———PIN6（GND负极）LED灯就会亮起来了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fc04fcb5727fbb68.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e3319dc989966369.png)





**编程来控制LED**

常用来操作树莓派GPIO的库有两个:

一个是python的 rpi.gpio (https://pypi.python.org/pypi/RPi.GPIO)

一个是C语言的wiringpi   (http://wiringpi.com/)

A： 使用RPI.GPIO

默认安装的完整版本的IMG是自带RPI.GPIO库和python环境的。不用我们安装

如果需要安装的话

```
#sudo apt-get update
```

安装python

```
#sudo apt-get install python
```

安装pip 用pip安装 rpig.pio

```
#sudo pip install rpi.gpio
```



这次我们需要修改上面的布线方案。因为我们要编程操作一个PIN了，是不能操作电源针脚。我们选择PIN3连接方式其余的不变。将原来接PIN1的线接PIN3就好了。这里就不上图了，PIN3正极——–电阻——LED正极——–LED负极———PIN6负极，python的语法就不说了，这个简单易学。请自学。编辑一个文本文件。写入代码。



```
#导入操作GPIO的库
import RPi.GPIO as GPIO
#导入time库，我们需要用到sleep
import time
#设置引脚的编码模式为P1.等同于这里的BOARD
GPIO.setmode(GPIO.BOARD)
#设置PIN3的操作模式为输出
GPIO.setup(3,GPIO.OUT)
#循环执行
while True:
     #给PIN3一个高电平，此时LED亮了
     GPIO.output(3,GPIO.HIGH)
    #休眠一秒
     time.sleep(1)
    #再给PIN3一个低电平。此时LED灭了
     GPIO.output(3,GPIO.LOW)
     time.sleep(1)
```



上面的效果你就看到你的LED一秒闪烁一次。（这个脚本没有退出，也没有退出时清理资源）。尝试修改sleep时间什么的也都是可以的哦，time.sleep(0.2) 闪烁频率就变快了 。同时我们再查看一下PIN3针脚的模式

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016546ffa0c5047297.png)



发现已经变成GPIO.OUT了。这就是我们脚本内GPIO.setup(3,GPIO.OUT)的作用。Getmode.py脚本如下。就不再解释了。（电源PIN是不能操作的，会出异常。）

代码:





```
import RPi.GPIO as GPIO 
import time 
strmap=`{` 
GPIO.IN:"GPIO.IN", 
GPIO.OUT:"GPIO.OUT", 
GPIO.SPI:"GPIO.SPI", 
GPIO.I2C:"GPIO.I2C", 
GPIO.HARD_PWM:"GPIO.HARD_PWM", 
GPIO.SERIAL:"GPIO.SERIAL", 
GPIO.UNKNOWN:"GPIO.UNKNOWN" 
`}` 
GPIO.setmode(GPIO.BOARD) 
for x in range(1,26): 
 if x not in [1,2,4,6,9,14,17,20,25]: 
   print ("PIN"+str(x)+" :"+strmap[GPIO.gpio_function(x)]) 
 else: 
   print ("PIN"+str(x)+" : POWER")
```



B使用wiringpi操作

同样是上面的工作。这次我们用C语言的wiringpi来操作，下载wiringpi库。（git的安装就不讲了，默认完整的img也带了）。去git上clone

```
#git clone git://git.drogon.net/wiringPi
#cd wiringPi
#./build
```

等待编译完成，树莓派的B CPU 700MHZ相对来说还是比较慢。需要稍微等待

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0162d754387e60f22d.png)

编译好以后会自动给你安装到/usr/local/lib目录中。只需要直接用头文件和lib就行，如果你的系统没有这个目录。参看wiringPi目录下的INSTALL解决。我们新建一个led.c

代码:



```
#include &lt;wiringPi.h&gt; 
#include &lt;unistd.h&gt; 
#include &lt;stdbool.h&gt; 
int main() 
`{` 
//初始化环境
 wiringPiSetup(); 
//设置PIN3为输出模式 对应于，wiringpi由之前的图标号应该是8.这里特别注意
 pinMode(8,OUTPUT); 
 while(true) 
 `{` 
  sleep(1); 
//写入高电平
  digitalWrite(8,HIGH); 
  sleep(1); 
//写入低电平
  digitalWrite(8,LOW); 
 `}` 
 
`}`
```

这里需要特别注意的是编号不再是3.而是8了。因为我们用的是wiringPi。

[![](https://p3.ssl.qhimg.com/t01198879234572796e.png)](https://p3.ssl.qhimg.com/t01198879234572796e.png)

开始编译这个文件

```
#gcc -o led led.c -lwiringPi
```

意思是通过led.c产生 led 这个bin文件，链接的时候使用wiringPi开发库（基础库是默认链接的，不要明显指出）。如果不使用-lwiringPi会提示链接错误。未定义的引用。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0111d0e72ac8ca0015.png)

编译完毕后使用管理员权限执行

```
#sudo ./led
```

这样就又能看到led一秒闪烁一次了



**<br>**

**下一次我们玩什么设备呢？**

是蜂鸣器？还是人体红外感应？还是摄像头？还是人体红外感应以后，蜂鸣器发出报警？又或者是互联网摄像头，树莓派当客户端，通过互联网传输家里的视频到你的手机，让你在手机上也能看到家里的状况？继续为摄像头添加一个移动检测。监测到异常移动蜂鸣器报警。并且报警到外网云端？

组合蜂鸣器，人体感应，摄像头 ，互联网云终端，手机移动端 就是一个小小的安防监控系统。

再取个响亮的名字，找两个销售，脚踩*华，拳打*康，我的口水已经流出来了。我已经快要走向人生巅峰了，随后迎娶一群白富美，然后嘿嘿嘿。

<br>

**花絮**

砰砰砰

一阵敲门声，惊醒我，我从容地扔掉手中的卫生纸。

“谁啊”

“我是房东。这个月房租加水电费一共1276，打我支付宝啊”

“哦，过两天打给你，我还没发工资呢”

“你又要拖？还有啊，租房合同要到期了，附近人都涨了几次了，再签这次房租怎么也要涨一点的，不行就准备搬走。”

“……………..”

**<br>**

****

**传送门**

[](http://bobao.360.cn/learning/detail/3051.html)

[**【技术分享】初玩树莓派B（一） 基本介绍&amp;安装操作系统**](http://bobao.360.cn/learning/detail/3085.html)

[**【技术分享】初玩树莓派B（三） 控制蜂鸣器演奏乐曲**](http://bobao.360.cn/learning/detail/3093.html)

[**【技术分享】初玩树莓派B（四） 人体红外感应报警&amp;物联网温湿度监控**](http://bobao.360.cn/learning/detail/3096.html)


