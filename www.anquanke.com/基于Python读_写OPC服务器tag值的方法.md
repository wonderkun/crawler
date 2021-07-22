> 原文链接: https://www.anquanke.com//post/id/242697 


# 基于Python读/写OPC服务器tag值的方法


                                阅读量   
                                **58827**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01b092b6b2ec79f049.png)](https://p3.ssl.qhimg.com/t01b092b6b2ec79f049.png)



作者：thx

## 01.前言

最近在研究这样一个需求，通过OPC服务器的方式把多个PLC的数据集成到一个监控画面，OPC服务器通过硬件驱动获取设备的数据，上位监控再获取OPC服务器的数据，数据获取的方式可以是第三方成熟的OPCClient，也可以基于python开发来读/写数据，本文介绍了一种基于python开发的思路，当然这里要借助OpenOPC这样的python插件。



## 02.实验环境

### OPC原理

OPC是工业控制和生产自动化领域中使用的硬件和软件的接口标准，以便有效地在应用和过程控制设备之间读写数据。O代表OLE(对象链接和嵌入)，P (process过程)，C (control控制)。

OPC标准采用C／S模式，OPC服务器负责向OPC客户端不断的提供数据。OPC服务器包括3类对象(Object)：服务器对象(Server)、组对象(Group)和项对象(Item)。

[![](https://p1.ssl.qhimg.com/t01bf3f8d12e066fb52.png)](https://p1.ssl.qhimg.com/t01bf3f8d12e066fb52.png)

1）OPC服务器对象维护有关服务器信息，并作为OPC组对象的包容器，它提供了对数据源进行读／写和通信的接口方法，可以动态地创建或释放组对象。

2）OPC组对象由客户端定义和维护，它维护有关其自身的信息，提供包容OPC项对象的机制，从逻辑上实现对OPC项的管理。

3）OPC项对象包含在OPC组中，可由客户端定义和维护。项代表了与数据源的连接，所有的OPC项的操作都是通过包容此项的OPC组对象完成的。

### KEPServerEX

KEPServerEX是第三方的OPC服务器，各不同厂家多种设备下位PLC与上位机之间通讯。

真实实验环境的搭建如下图：

[![](https://p1.ssl.qhimg.com/t0168d40f727b5ecfc6.png)](https://p1.ssl.qhimg.com/t0168d40f727b5ecfc6.png)

工具：python、OpenOPC、

工控设备：博智工控安全实验箱，提供s71200、omron 2个PLC，运行了5种工艺场景，本实验中以锅炉热水系统为实验的工艺场景。s71200、omron PLC的IP地址分别为172.16.28.112、172.16.28.111.

opc服务器：KEPServerEX V5，IP地址为172.16.28.252

上位监控：IP地址为172.16.28.197

PC操作系统：opc服务器及上位机都采用windows XP SP3



## 03.服务端KEPServer搭建

新建通道：New Channel

1）在OPC服务器中打开“KEPServerEX 5 Configuration”软件，新建一个工程，再单击软件界面“Click to add a channel.”或者工具栏上的“New Channel”，新建一个通道，修改通道名“Channel name”或不作修改：

[![](https://p0.ssl.qhimg.com/t01ed82fbfbc9c60148.png)](https://p0.ssl.qhimg.com/t01ed82fbfbc9c60148.png)

2）选择你想分配给本通道的设备驱动“Device driver”，这里选择“Siemens TCP/IP Ethernet”，另外的omron PLC可以选择“Omron FINS Ethernet”：

[![](https://p5.ssl.qhimg.com/t01600de13616781fb8.png)](https://p5.ssl.qhimg.com/t01600de13616781fb8.png)

3）完成通道的建立

新建设备：New Device

1）单击软件界面“Click to add a device”或者工具栏上的“New Device”，进行设备设置，修改设备名称为”s71200”。

[![](https://p4.ssl.qhimg.com/t01d41ed1b3d7304804.png)](https://p4.ssl.qhimg.com/t01d41ed1b3d7304804.png)

2）选择设备模型“Device model”, 这里我们选择“S7-1200”，如果是omron PLC则选择“CS1”。

[![](https://p5.ssl.qhimg.com/t016f3250bfe2460b27.png)](https://p5.ssl.qhimg.com/t016f3250bfe2460b27.png)

3）选择设备ID“Device ID”, 这里指的是所要连接的PLC设备的IP地址。假如IP地址为：172.16.28.112，则设置如下：

[![](https://p1.ssl.qhimg.com/t01aae9b1b229f073f7.png)](https://p1.ssl.qhimg.com/t01aae9b1b229f073f7.png)

4）完成新设备的添加。

新建标签：New Tag

1）单击软件界面“Click to add a static tag”，或者工具栏“New Tag”增加一个标签。设置Tag属性，定义名称，和地址。这里的地址要与PLC中定义的变量地址对应，例如，在博智工控安全实验箱中的S71200PLC中定义了一个如下的变量，在本通讯实例中我们只应用红框中的3个变量。

[![](https://p4.ssl.qhimg.com/t0107ba572a03556d04.png)](https://p4.ssl.qhimg.com/t0107ba572a03556d04.png)

2）在KEPServer中创建3个tag与上面的s71200 PLC的3个变量对应，如下图。Omron PLC的创建方法类似。

[![](https://p5.ssl.qhimg.com/t01e32a40cb7114376b.png)](https://p5.ssl.qhimg.com/t01e32a40cb7114376b.png)

[![](https://p0.ssl.qhimg.com/t014b1292f9e6ecfb48.png)](https://p0.ssl.qhimg.com/t014b1292f9e6ecfb48.png)

[![](https://p4.ssl.qhimg.com/t01b20619f37f5cdec3.png)](https://p4.ssl.qhimg.com/t01b20619f37f5cdec3.png)

[![](https://p1.ssl.qhimg.com/t012d8caf11c5dfed8e.png)](https://p1.ssl.qhimg.com/t012d8caf11c5dfed8e.png)

4）最小化KEPServer。



## 04.DCOM配置

在这里需要针对客户端（上位机）和服务端（OPC服务器）都要进行DCOM的配置，DCOM的配置资料网上较多，可以自行参考。



## 05.OPC客户端开发工具配置

1）在需安装pyhton工具，实验中使用的版本为V2.7.17。另外还要准备OpenOPC，OpcOpen是一个开源的软件，通过安装一个服务，允许远程的TCP/IP链接传输OPC数据，从而越过DCOM来访问远程OPC服务器。

2）运行[OpenOPC-1.3.1.win32-py2.7.exe](https://sourceforge.net/projects/openopc/files/)安装文件，默认安装选择，如下图：

[![](https://p5.ssl.qhimg.com/t01a1d29cccfa1b62aa.png)](https://p5.ssl.qhimg.com/t01a1d29cccfa1b62aa.png)

[![](https://p3.ssl.qhimg.com/t01a20e9c83c1c90f22.png)](https://p3.ssl.qhimg.com/t01a20e9c83c1c90f22.png)

2）再运行pywin32-221.win32-py2.7.exe文件，点击“下一步”如下图：

[![](https://p1.ssl.qhimg.com/t01e12a921dbdf433d1.png)](https://p1.ssl.qhimg.com/t01e12a921dbdf433d1.png)

3）完成客户端的配置。

06.pyhton运行环境读取OPC服务的值

1）根据05章节的建立的3个tag：

[![](https://p0.ssl.qhimg.com/t019312dac7c8a1c520.png)](https://p0.ssl.qhimg.com/t019312dac7c8a1c520.png)

2）在OPC客户端编写读/写tag name为sp的值脚本如下：

[![](https://p2.ssl.qhimg.com/t013c740613555b37db.png)](https://p2.ssl.qhimg.com/t013c740613555b37db.png)

3）逐行运行后，先写入tag值再获取tag位号的当前值：

[![](https://p2.ssl.qhimg.com/t0155986b1872fd767f.png)](https://p2.ssl.qhimg.com/t0155986b1872fd767f.png)

4）操作时，用wireshark获取的流量，如下：

[![](https://p3.ssl.qhimg.com/t01d7f530b3adf8e0b2.png)](https://p3.ssl.qhimg.com/t01d7f530b3adf8e0b2.png)

5）同时我们可以观察博智工控安全实验箱中锅炉热水系统场景中，频率设定值已被修改为40，原来值为30。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01099b3117deb66a3b.png)

6）获取tag name为start的值脚本如下：

[![](https://p3.ssl.qhimg.com/t01ea6236aadec4926a.png)](https://p3.ssl.qhimg.com/t01ea6236aadec4926a.png)

7）最后我们也可以第三方OPCClient的获取，方式如下：

[![](https://p4.ssl.qhimg.com/t014b35711e5f8fe238.png)](https://p4.ssl.qhimg.com/t014b35711e5f8fe238.png)

[![](https://p0.ssl.qhimg.com/t01c10c6d01885af003.png)](https://p0.ssl.qhimg.com/t01c10c6d01885af003.png)



## 05.总结

本文只是以Python作为开发平台，利用Python的第三方OPC支持组件，逐步构建OPCClient的一种方式，更多的工作量还需前端显示界面的开发等。
