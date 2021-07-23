> 原文链接: https://www.anquanke.com//post/id/233736 


# 记一次PLC故障恢复经历


                                阅读量   
                                **223771**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01def224475f67b59a.jpg)](https://p5.ssl.qhimg.com/t01def224475f67b59a.jpg)



作者：Nonattack

## 1、前言

近期对Schneider UMAS (Unified Messaging Application Services) 协议做了一些基本研究，关于协议分析的内容详见文章：[https://www.anquanke.com/post/id/231884](https://www.anquanke.com/post/id/231884)，基于对协议的掌握，随后开发了一些简单的Fuzz程序对PLC开展Fuzzing测试，测试过程中很快遇到了棘手问题：PLC罢工了。从安全研究的视角来看，这是一件好事，同时也是一件坏事，好事预示着此处有将有漏洞出没，但前提得先把PLC故障恢复了，然后再精准复现出该故障现象。故障现场如下所示：

<video style="width: 100%; height: auto;" src="https://rs-beijing.oss.yunpan.360.cn/Object.getFile/anquanke1/UExDZXJyb3IubXA0" controls="controls" width="300" height="150">﻿您的浏览器不支持video标签 </video>





## 2、恢复过程

PLC进入故障状态之后的具体情况如下：1、组态软件无法连接PLC；2、上位机无法ping通PLC；3、尝试万能的断电/上电操作，依然无法连接PLC，各状态指示灯不断闪烁（CPU/DIDO/AIAO模块的ERR灯闪烁、CARD ERR灯常亮）。根据经验判断原因基本有两种：1、PLC内部的基础配置/程序已经丢失从而进入异常状态；2、PLC固件运行出错。再次走读了一下测试程序：由于Fuzzing测试序主要是对UMAS功能码进行的，未对固件作删除相关的毁灭性操作，因此测试导致PLC配置出错进而运行异常的概率比较大，固解决问题的方向先集中到恢复PLC配置。

有了方向接下来便是寻求处理方法的过程，通过查找，使用PLC的mini USB接口与PLC建立通信连接，将配置程序重新写入PLC当中是一个常用方法。刚好手头有一根USB线，插入CPU模块上的USB端口，连接上位机：EcoStruxure Contol Expert -&gt; PLC -&gt;设置地址：

[![](https://p2.ssl.qhimg.com/t01ace777c3899fe660.png)](https://p2.ssl.qhimg.com/t01ace777c3899fe660.png)

[![](https://p1.ssl.qhimg.com/t01326b3b60d61b25e0.png)](https://p1.ssl.qhimg.com/t01326b3b60d61b25e0.png)

好事多磨，问题总是没那么容易就解决了：经过反复尝试，软件始终无法与PLC建立连接。继续查阅资料，同时审视一下当前环境：当前组态软件EcoStruxure Contol Expert安装在虚拟机当中，会不会是软件的版本太低了呢？是不是虚拟机识别USB存在问题呢？再或者，是不是USB线是有问题的呢……经过一通操作，发现了组态软件的一个驱动管理组件：

[![](https://p5.ssl.qhimg.com/t01328bfcfa3b7d580d.png)](https://p5.ssl.qhimg.com/t01328bfcfa3b7d580d.png)

[![](https://p0.ssl.qhimg.com/t01851edb07538f1bd4.png)](https://p0.ssl.qhimg.com/t01851edb07538f1bd4.png)

[![](https://p3.ssl.qhimg.com/t01d0807038cd58defe.png)](https://p3.ssl.qhimg.com/t01d0807038cd58defe.png)

经过尝试结果还是仍然无法连接上……但是此处指向了PLC USER Driver,就是说这个驱动对于识别PLC至关重要，于是有了解决问题的方向，为了排除软件版本过低和虚拟机的干扰因素，于是选择了关闭虚拟机，下载新版本的EcoStruxure Contol Expert V14.0软件在物理机中安装，组态软件比较大，下载和安装的过程比较费时，此处需要等待大约1小时……

使用新版软件再次连接PLC USB,却还是无法识别、无法连接……难道这是一个特例的问题？难道PLC USER Driver的版本仍然有问题？继续搜索查找：

[![](https://p0.ssl.qhimg.com/t01125e9481b8af9532.png)](https://p0.ssl.qhimg.com/t01125e9481b8af9532.png)

还好没放弃，找到了一个时间最近的可用PLC USER Driver套件，下载和当前所使用的版本对比一下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010ddeab4824998862.png)

果然PLC USER Driver还不够新版，重新安装单独更新驱动，这一次终于连接成功：

[![](https://p0.ssl.qhimg.com/t01845e2d1f254bf7c0.png)](https://p0.ssl.qhimg.com/t01845e2d1f254bf7c0.png)

[![](https://p2.ssl.qhimg.com/t01ac1f25460398ba9d.png)](https://p2.ssl.qhimg.com/t01ac1f25460398ba9d.png)

成功识别PLC并与组态软件建立连接，从软件底部提示可以看到：PLC中无配置、无上载信息，就是说PLC内部的配置程序被刷掉，因此进入故障模式。连接成功后，上载一个基本程序，PLC恢复正常运行。

对于故障恢复，还有另外一种终极解决方法：将PLC的通信模块拆解下来，使用拨码的方式恢复IP地址，把模块背后下面的拨码开关先拨到E（蓝色十字有一处为箭头，箭头指向E），之后IP地址将变成默认的84.xx.xx.xx，xx是指mac地址的后三位转换成10进制的数。有了IP地址，便可使用组态软件继续连接PLC进行其他配置了：

[![](https://p2.ssl.qhimg.com/t01157b6c938e6d4f70.png)](https://p2.ssl.qhimg.com/t01157b6c938e6d4f70.png)

[![](https://p5.ssl.qhimg.com/t018b209bac5df4d52f.png)](https://p5.ssl.qhimg.com/t018b209bac5df4d52f.png)



## 3、Fuzzing定位

由于运行了多个fuzz程序，发送了大量数据包，不经意的触发了一个问题，如何找到触发问题的那个数据包，这又将是一个费事的问题，努力回忆做过的操作，然后尝试去再做一遍……估计是运气比较好，故障现象再次复现了，最终分析定位找到了可稳定触发现象的数据包，至此成功获取到一个致使目标设备拒绝服务的洞，也掌握了故障恢复的技巧。至于故障的详细技术分析，就留待Schneider安全响应团队去做了。

[![](https://p0.ssl.qhimg.com/t015a79e97db3277ed2.png)](https://p0.ssl.qhimg.com/t015a79e97db3277ed2.png)
