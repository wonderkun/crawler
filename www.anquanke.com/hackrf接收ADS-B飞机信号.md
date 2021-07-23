> 原文链接: https://www.anquanke.com//post/id/212522 


# hackrf接收ADS-B飞机信号


                                阅读量   
                                **182549**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t017bf06904b233458f.jpg)](https://p0.ssl.qhimg.com/t017bf06904b233458f.jpg)



## 前记

本次讲解的是使用hackrf接收ADS-B飞机广播信号，通过接收ADS-B信号可以获取附近范围内，飞机的航班号，飞行高度，经纬度，轨迹等信息。本文将使用hackrf进行接收ADS-B信号，并对其原理以及实验复现进行讲解。希望大家能从中有所收获！

广播式自动相关监视（英语：Automatic dependent surveillance – broadcast，缩写ADS–B）是一种飞机监视技术，飞机通过卫星导航系统确定其位置，并进行定期广播，使其可被追踪。空中交通管制地面站可以接收这些信息并作为二次雷达的一个替代品，从而不需要从地面发送问询信号。其他飞机也可接收这些信息以提供姿态感知和进行自主规避。

ADS–B是一种“自动”系统，它不需要飞行员或其他外部信息输入，而是依赖飞机导航系统的数据。



## 实验过程

ADS-B信号在1090MHZ频率中接收信号，由于航空CNS系统中存在大量的古老的无线标准，所以飞机航空有着一套标准协议，如果想要修改一点，那么想要广泛应用是非常困难的，这也致使了现在的无线标准仍然比较老旧。而不同飞机之间通过接收ADS-B信号，可以获取到其他飞机的信息，从而进行感知或规避，ADS-B是自动广播的系统，所以我们在地面也可以接收它的信号。

**安装环境**

$ apt update

$ apt install build-essential debhelper rtl-sdr libusb-1.0-0-dev librtlsdr-dev pkg-config dh-systemd libncurses5-dev libbladerf-dev git lighttpd -y

**下载dump1090**

$ git clone [https://github.com/itemir/dump1090_sdrplus.git](https://github.com/itemir/dump1090_sdrplus.git)<br>
$ make

需要注意的是在安装完dump1090后，进入文件夹执行make进行安装，然后再目录内执行以下命令：

`./dump1090 --aggressive --net --interactive`

执行后当有飞机经过我们的时候终端就会输出信息，在接收过程中将天线尽可能的靠近窗口或者室外，并且hackrf选择的天线最好使用能够接收1090MHZ的，以保证实验正常进行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ac6a7d4be24f913f.png)

<strong>Flight：航班号<br>
Altitude：飞行高度<br>
Speed：速度<br>
lat：经度<br>
lon：维度<br>
Track：轨道<br>
sec：通信时间</strong>

开启如上dump1090命令后，会自动开启一个http服务，在浏览器中输入url地址127.0.0.1:8080,会自动打开一个地图，里面显示了飞机可视化的航向信息。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0102a2f49f4dacd7de.png)

可以看到地图上不断在刷新飞机的坐标，并且在左边显示了飞行信息，是不是看起来更加人性化了呢？

但是这里大家需要注意的是dump1090默认的地图是使用的google map，是需要挂代理才能够访问的，这里我们可以替换dump1090文件夹下的gamp.html文件，替换成国内的地图来使用。gmap.html的源码我已经上传至github有需要的小伙伴可以自行下载。

`https://github.com/wikiZ/dump1090`



## modes_rx实验及环境搭建

说起mades_rx的搭建还是抹了一把伤心泪，在环境搭建的过程也着实踩了不少坑。这个工具相比于dump1090可以把抓取到的信息保存为kml文件并导入google earth或者gpsprune中使用。

**环境搭建**

$ git clone [https://github.com/bistromath/gr-air-modes.git](https://github.com/bistromath/gr-air-modes.git)

$ cd gr-air-modes

$ mkdir build

$ cd build

$ cmake ../

$ make

$ sudo make install

$ sudo ldconfig

当执行到cmake ../时，需要注意的一点是如果你的gnuradio是3.7.x版本的那么就有可能报下图中的错误。

[![](https://p3.ssl.qhimg.com/t01ec761de58296e2c3.jpg)](https://p3.ssl.qhimg.com/t01ec761de58296e2c3.jpg)

会提示需要安装gnuradio3.8从而无法正常进行cmake操作。那么这时怎么办呢？不要着急，我们可以使用mades_rx的分支版本，在文件夹内输入git tag可以看到有gr37的分支，然后我们继续输入git checkout gr37切换过去然后正常安装就可以啦！

[![](https://p0.ssl.qhimg.com/t0133c17fc62e0e0740.png)](https://p0.ssl.qhimg.com/t0133c17fc62e0e0740.png)

安装完成后在终端输入以下命令:

`modes_rx -g 60 -k air.kml`

当飞机经过将信息保存至air.kml就可以啦。然后导入google earth中即可。

[![](https://p4.ssl.qhimg.com/t01e44448ae447cfb97.png)](https://p4.ssl.qhimg.com/t01e44448ae447cfb97.png)



## tag1090

相比于dump1090，个人感觉tar1090是一款界面更加人性化的软件，他清晰的标注了飞行的运行轨迹，效果如下图：

[![](https://p0.ssl.qhimg.com/t01ae397463a5d5c280.png)](https://p0.ssl.qhimg.com/t01ae397463a5d5c280.png)

感兴趣的小伙伴门可以自行在github中下载，这里就不再赘述配置过程了。

`https://github.com/wiedehopf/tar1090`



## 后记

本文就讲到这里，其实接收ADS-B并没有具体法规约束，但是大家还是需要注意，接收到的信息最好不要发到国外，那样就很有可能去喝茶了。写完这篇文章后，应该最近几周不会再写，因为需要准备等天线到货后，准备研究一下接收气象云图，当然会写成文章发表出来。大家敬请期待吧。

最后祝大家学业有成，工作顺利！
