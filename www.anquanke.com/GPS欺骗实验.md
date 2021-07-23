> 原文链接: https://www.anquanke.com//post/id/204316 


# GPS欺骗实验


                                阅读量   
                                **391717**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01e264ebbc3aa2b0fa.png)](https://p4.ssl.qhimg.com/t01e264ebbc3aa2b0fa.png)



## 0x00前言

之前也没接触过无线电相关内容，前段时间入手了块HackRF One板子，本文是对GPS欺骗实验进行复现，此外文中有关GPS信号原理等内容仅仅作为简介，有关GPS涉及的内容维度较大，如感兴趣可自行查阅。<br>
首先说下实验环境:

```
硬件平台--HackRF One、GPS外部时钟、700-2700MHz天线
软件环境--Ubuntu 16.04运行HackRF环境
GPS终端--iphone7，飞行模式下仅GPS、开启WIFI辅助均测试成功。
```



## 0x01GPS简介

GPS 系统本身非常复杂, 涉及到卫星通信等各个领域. 这里只是简单介绍一下。我们通常所说的 GPS 全球定位系统是由美国国防部建造完成。目前在太空中共有31颗卫星在同时运作。一般我们需要至少4颗卫星来完成三角定位。GPS卫星同时发送民用L1和军用L2两种无线信号。我们通常使用的是没有加密的L1民用 1575.42MHz 的超高频波段。

[![](https://p5.ssl.qhimg.com/t01f87bc4ecb263f9cc.jpg)](https://p5.ssl.qhimg.com/t01f87bc4ecb263f9cc.jpg)



## 0x02GPS定位原理

GPS导航系统的基本原理是测量出已知位置的卫星到用户接收机之间的距离，然后综合多颗卫星的数据来确定接收机的具体位置。要达到这一目的，卫星的位置根据星载时钟所记录的时间在卫星星历中查出，用户到卫星的距离则通过记录卫星信号传播到用户所经历的时间，再将其乘以光速得到。

当GPS卫星正常工作时，会不断地用1和0二进制码元组成的伪随机码发射导航电文。导航电文从卫星信号中调制出来，包括卫星星历、工作状况、时钟改正、电离层时延修正、大气折射修正等信息。其中最重要的为星历数据。当用户接受到导航电文时，提取出卫星时间并将其与自己的时钟作对比获知卫星与用户的距离，再利用导航电文中的卫星星历数据推算出卫星发射电文时所处位置，从而获知用户在WGS-84大地坐标系中的位置、速度信息。

GPS定位的基本原理是根据高速运动的卫星瞬间位置作为已知的起算数据，采用空间距离后方交会的方法，确定待测点的位置。完整的GPS定位包括三部分：

**1.空间部分**

GPS的空间部分是由24颗卫星组成(21颗工作卫星，3颗备用卫星）

**2.地面控制系统**

地面控制系统由监测站(Monitor Station)、主控制站(Master Monitor Station)、地面天线(Ground Antenna)所组成。

**3.用户设备部分**

用户设备部分即GPS信号接收机。其主要功能是能够捕获到按一定卫星截止角所选择的待测卫星，并跟踪这些卫星的运行。



## 0x03卫星星历

卫星星历可以在nasa官网下载到最新的信息文件，项目源码中已经包括了一个旧的信息文件brdc3540.14n也可以使用。<br>
卫星星历，又称为两行轨道数据（TLE，Two-Line Orbital Element），由美国celestrak发明创立。<br>
卫星星历是用于描述太空飞行体位置和速度的表达式——两行式轨道数据系统。

```
ftp://cddis.gsfc.nasa.gov/pub/gps/data/daily/2020/brdc)
```

星历文件命名格式：

[![](https://p2.ssl.qhimg.com/t01a1098d6ef49f67b9.jpg)](https://p2.ssl.qhimg.com/t01a1098d6ef49f67b9.jpg)

星历文件命名规则：

[![](https://p5.ssl.qhimg.com/t01663389a79e2023ff.jpg)](https://p5.ssl.qhimg.com/t01663389a79e2023ff.jpg)



## 0x04实验准备

#### <a class="reference-link" name="1%E3%80%81gps-sdr-sim%E9%A1%B9%E7%9B%AE"></a>1、gps-sdr-sim项目

这个项目的原理是gps-sdr-sim能根据指定的卫星信息文件、坐标信息、采样频率等参数输出二进制的信号文件，将这个二进制文件导入到USRP或者bladeRF之类的无线电射频设备上就可以实现GPS的伪造。<br>
(1)下载GPS仿真器代码

`git clone https://github.com/osqzss/gps-sdr-sim.git`

(2)gcc编译：

`gcc gpssim.c -lm -O3 -o gps-sdr-sim`

编译完成后路径下会出现可执行程序gps-sdr-sim:

[![](https://p1.ssl.qhimg.com/t01ee1a4afa59b3544c.jpg)](https://p1.ssl.qhimg.com/t01ee1a4afa59b3544c.jpg)

#### <a class="reference-link" name="2%E3%80%81%E8%8E%B7%E5%8F%96%E5%9D%90%E6%A0%87"></a>2、获取坐标

项目页面上给了三种不同的输入坐标信息的方式：

gps-sdr-sim -e brdc0910.20n -l 29.6562801500,91.1257504400

gps-sdr-sim -e brdc0910.20n -u circle.csv

gps-sdr-sim -e brdc0910.20n -g triumphv3.txt

因为我们使用的是固定坐标,所以我从[在线地图](http://www.gpsspg.com/)中随机获取了一个地址并记录其经纬度。（例如，拉萨布达拉宫附近，记录其经纬度，如下图所示）

[![](https://p3.ssl.qhimg.com/t01fb8fcb8664187e07.jpg)](https://p3.ssl.qhimg.com/t01fb8fcb8664187e07.jpg)

#### <a class="reference-link" name="3%E3%80%81%E8%BF%9E%E6%8E%A5hackrf%E8%AE%BE%E5%A4%87"></a>3、连接hackrf设备

GPS外部时钟如下图所示安装在HackRF板上

[![](https://p1.ssl.qhimg.com/t01a9638ad9ec2da4e8.jpg)](https://p1.ssl.qhimg.com/t01a9638ad9ec2da4e8.jpg)

查看设备是否被识别，成功识别输入`hackrf_info`会打印出hackrf的信息:

[![](https://p3.ssl.qhimg.com/t01036d93df39796f86.jpg)](https://p3.ssl.qhimg.com/t01036d93df39796f86.jpg)



## 0×05生成GPS数据

使用-l参数指定之前获取的坐标29.6562801500,91.1257504400，-b参数指定二进制文件格式，执行文件后默认会生成300秒GPS仿真数据。

`./gps-sdr-sim -e brdc0910.20n -l 【坐标】 -b 8`

[![](https://p2.ssl.qhimg.com/t019be25ac37ab817fd.jpg)](https://p2.ssl.qhimg.com/t019be25ac37ab817fd.jpg)

等待命令执行结束，文件夹中多了一个`gpssim.bin`文件，这个文件内容就是模拟生成的GPS数据。

[![](https://p1.ssl.qhimg.com/t01fd7f66d99b4040ff.jpg)](https://p1.ssl.qhimg.com/t01fd7f66d99b4040ff.jpg)



## 0×06发射GPS数据

hackrf_transfer 将生成的基带信号重新生成为GPS信号。<br>
指定GPS数据，-f指定发射频率，指定频率为1575420000 即民用GPS L1波段频率，-s指定采样速率,指定采样速率2.6Msps，-x指定发射功率,开启天线增益，指定TX VGA(IF)为0、10、20不等(为了限制影响范围，最大为47，尽量不要使用)，最后开启重复发射数据功能。

`hackrf_transfer -t gpssim.bin -f 1575420000 -s 2600000 -a 1 -x 40`

[![](https://p5.ssl.qhimg.com/t019148322d6619e756.jpg)](https://p5.ssl.qhimg.com/t019148322d6619e756.jpg)

#### <a class="reference-link" name="%E5%91%BD%E4%BB%A4%E5%8F%82%E6%95%B0%E7%AE%80%E4%BB%8B"></a>命令参数简介

**采样频率：**<br>
采样频率相当于二进制文件每个坐标产生的频率，默认的是2600000Hz，这个采样率过大或者过估计都会有问题，过小可能导致信号不稳定，过大可能在传输过程中会出现传输速度跟不上采样率，这样发出来的信号也是不稳定的。

**二进制文件格式：**

输出的二进制文件有三种格式，分别有1-bit、8-bit、16-bit，默认使用的是16-bit的。但是Hackrf中，支持的是8-bit的二进制文件，所以一定要把这个参数改成8-bit。

**发射频率：**

这个是输出的信号的中心频率，默认是美国官方的GPS L1信号频段1575420000Hz，按照默认即可，如果不是默认的可能通用的GPS客户端设备不能收到信号。

**二进制信号持续时间：**

这个参数决定了信号的持续时间，但是其实输出的时候是循环输出的，所以如果使用固定坐标的话不用太长。默认的是300s，这个时间越大生成的二进制文件也会越大，经过测试，固定坐标情况下一分钟到三分钟就可以完成定位，使用默认的300s就可，如需加大再自行指定。

##### <a class="reference-link" name="gps-sdr-sim%E5%8F%82%E6%95%B0%EF%BC%9A"></a>gps-sdr-sim参数：

通过查看参数发现还可以对时间、动态坐标等进行欺骗~

```
Usage: gps-sdr-sim [options]
Options:
  -e &lt;gps_nav&gt;     卫星信息文件(必须)
  -u &lt;user_motion&gt; 用户定义的坐标文件 (动态的位置信息)
  -g &lt;nmea_gga&gt;    NMEA坐标文件 (动态的位置信息)
  -l &lt;location&gt;    坐标，维度-经度-海拔，例如： 30.286502,120.032669,100
  -t &lt;date,time&gt;   模拟的开始时间 YYYY/MM/DD,hh:mm:ss
  -d &lt;duration&gt;    持续时间 [秒] (最大: 300)
  -o &lt;output&gt;      二进制文件的输出位置 (默认: gpssim.bin)
  -s &lt;frequency&gt;   采样频率 [Hz] (默认: 2600000)
  -b &lt;iq_bits&gt;     二进制文件格式 [1/8/16] (默认: 16)
  -v               更多细节信息
```

#### <a class="reference-link" name="%E5%AE%9E%E9%AA%8C%E7%BB%93%E6%9E%9C%EF%BC%9A"></a>实验结果：

首先使用了手机高德地图测试了仅GPS定位，在等待了一分钟左右即可欺骗成功，位置已定位到拉萨。

[![](https://p5.ssl.qhimg.com/t011b1c66f8f9dabc57.png)](https://p5.ssl.qhimg.com/t011b1c66f8f9dabc57.png)

随后开启了wifi热点发现均可测试成功

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01abcce5bbcced8884.png)



## 0x07 GPS欺骗防御

关于GPS欺骗防御方面我对参考的文章做了简单的总结:
1. 根据GPS信号的强度区分。如果GPS的欺骗信号是从单一的设备中发出的，那么其信号的强度很可能是一直的，而在正常的通讯环境下，不同GPS信号不会有如此相似的信号强度。
1. 根据GPS信号数目区分。因为GPS信号是伪造出来的，而且需要至少伪造出来三个，而一般地来说，为了使得欺骗成功，伪造的GPS信号数目是越多越好的，所以如果GPS信号的数目突然增加了很多，那么很可能遭到了GPS欺骗。
1. 根据时间区分。GPS信号具有卫星授时的功能。而GPS信号的伪造一般需要获取到某一天GPS卫星的运行报文，在这个基础上进行伪造。所以这样的伪造出来的卫星授时的时间一定是所采用报文的时间而不是正常时间，所以在联网设备中只需要对卫星授时时间进行比对，就可以知道是否遭到了GPS欺骗。
1. GPS加密为使用者提供了空中认证信号。举个例子，就像民用GPS接收器获取了加密的军用PRN码后，将不能完全可知或解码，当然，GPS欺骗系统也不可能做到提前伪造合成加密信号。如果要认证每个信号，那么每台民用GPS接收器将要携带类似于军用接收器上的加密密钥，而且要保证攻击者不能轻易获取到这些密钥。
1. 信号失真检测:当GPS信号正在被欺骗攻击时，这种方法可以根据一个短暂可观测的峰值信号来警告用户。通常，GPS接收器会使用不同策略来追踪接入信号的振幅强度，当一个模拟信号被传输发送时，接收器上显示的是原始信号和假信号的合成，而这种合成将会在Drag-off期间的振幅中出现一个峰值信号。


## 0x08参考资料：

[https://www.zhihu.com/question/20903715/answer/199560675](https://www.zhihu.com/question/20903715/answer/199560675)<br>[http://www.mwrf.net/tech/sdr/2017/22021.html](http://www.mwrf.net/tech/sdr/2017/22021.html)<br>[http://www.mwrf.net/tech/sdr/2018/22779.html](http://www.mwrf.net/tech/sdr/2018/22779.html)<br>[https://blog.csdn.net/sinat_26599509/article/details/52022199](https://blog.csdn.net/sinat_26599509/article/details/52022199)<br>[http://www.witimes.com/hackrf/](http://www.witimes.com/hackrf/)<br>[https://www.cnblogs.com/k1two2/p/5164172.html](https://www.cnblogs.com/k1two2/p/5164172.html)<br>[https://blog.csdn.net/OpenSourceSDR/article/details/52033069](https://blog.csdn.net/OpenSourceSDR/article/details/52033069)<br>[http://wooyun.jozxing.cc/static/drops/tips-11155.html](http://wooyun.jozxing.cc/static/drops/tips-11155.html)<br>[http://www.2cto.com/Article/201512/453013.html](http://www.2cto.com/Article/201512/453013.html)
