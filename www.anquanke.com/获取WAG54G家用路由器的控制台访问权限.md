> 原文链接: https://www.anquanke.com//post/id/83156 


# 获取WAG54G家用路由器的控制台访问权限


                                阅读量   
                                **80030**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.elttam.com.au/blog/gaining-console-access-to-the-WAG54G-home-router/](https://www.elttam.com.au/blog/gaining-console-access-to-the-WAG54G-home-router/)

译文仅供参考，具体内容表达以及含义原文为准

获取WAG54G家用路由器的控制台访问权限

向初学者介绍如何焊接以及连接到串行端口

图解如何鉴别以及连接Linksys WAG54G家用路由器的引出线，方便调试和开发。

**简介**

这个博客是讲解如何识别WAG54G家用路由器的串行端口，以及如何连接header pins，和获取设备的控制访问权。虽然这很简单，但却是对这类型设备进行运行分析的重要一步。

最近几年，利用硬件攻击软件安全的领域变得十分热门。原因是：

1.   业余爱好者能承担得起测试设备的成本（示波器、逻辑分析仪、SDR等）

2.   嵌入设备为顾客提供了廉价且足够强大而丰富的功能，而且它们大多相互关联，并且会暴露与安全研究员相关的攻击界面。

3.   大量资料的出现，使得从业人员的门槛降低。

我在这个方面的兴趣始于我想对WAG54G家用路由器做安全评估。我原来的兴趣主要是，研究在留下最少的足迹的同时，对家庭网络进行持续的攻击。目标包括大多数人电脑上运行的Linux系统以及Windows系统，在每次计算机重启时对虚拟计算机进行强化。与对管理程序的漏洞做审查不同的是，我选择对家用路由器做审查，因为这是家用网络的唯一出口，这使得中间人攻击以及负载虚拟计算机成为可能，它也可以直接接入互联网，可以直接连接C&amp;C，为了做这项调查，我需要先获得本地连接。

# Linksys WAG54G-AU

# Linksys WAG54G-AU是一款2.4GHz 802.11g ADSL调制解调器/路由器，有4个10/100的以太网端口，支持DHCP和VPN，以及一些基本的网络安全服务。下面的几张图片将展示设备开箱前与开箱后的样子。

[![](https://p0.ssl.qhimg.com/t01b02a71b5716228b6.png)](https://p0.ssl.qhimg.com/t01b02a71b5716228b6.png)

#  拆解路由器

# 为了找到设备的串行端口，我们要先取下四个橡胶垫，然后我们会看到4个可以拧开的Torx T10螺丝。

[![](https://p4.ssl.qhimg.com/t010e0356c541284b4e.png)](https://p4.ssl.qhimg.com/t010e0356c541284b4e.png)

[![](https://p5.ssl.qhimg.com/t013dc474ac8327ac6e.png)](https://p5.ssl.qhimg.com/t013dc474ac8327ac6e.png)

留心的读者可能会注意到，在其中一个橡胶垫上有一个防篡改标签，当我们取掉它时，外壳上会留有一个印着“VOID”的标识。

[![](https://p1.ssl.qhimg.com/t013f4e8309fd0bab47.png)](https://p1.ssl.qhimg.com/t013f4e8309fd0bab47.png)

[![](https://p5.ssl.qhimg.com/t01e32f79eb64375cc6.png)](https://p5.ssl.qhimg.com/t01e32f79eb64375cc6.png)

在取掉外壳后，我们能看到电路板，以及内存，CPU（SoC）,以及其他一些集成电路，比如WiFi控制器。如果你想很清楚的了解它们如何连接，如何运作，那么这会非常有用。我们可以用每个元器件上的唯一标识符在上网搜索相应的数据表。但是在这个例子中，我们只是要找到串行通信的pin（微处理器的对外引脚），所以找数据并不是我们所需的。

[![](https://p4.ssl.qhimg.com/t010eb4175a9f186e1c.png)](https://p4.ssl.qhimg.com/t010eb4175a9f186e1c.png)

有几个方法可以用来寻找串行接口

1.   识别PCB上的符号，通过参照数据表或者网上资源鉴别。

2.   识别电路板上的UART控制器

3.   寻找一些与要找的有关的4 pin，比如RX、TX、VCC、GND

在我们的例子中，我们采用最后一种方案，在电路板的底面，通过焊点孔以及pin布局可以很好识别。当然也可以通过微量线以及识别元件的接头连接。

[![](https://p0.ssl.qhimg.com/t012bf979e74957c768.png)](https://p0.ssl.qhimg.com/t012bf979e74957c768.png)

在上边的图片中，我们发现左上角有个有趣的组合，下面的图片是放大的底缝连接图，我们可以很容易看到pin1和pin 5是如何连接的。

[![](https://p0.ssl.qhimg.com/t0119cd6399d5e4b89c.png)](https://p0.ssl.qhimg.com/t0119cd6399d5e4b89c.png)

下面的图片是放大的电路板的顶端，我们能看到pin3和pin4间有微量线连接，只有2号pin没有与任何东西进行连接。

[![](https://p0.ssl.qhimg.com/t01c202cf2c269ae0c6.png)](https://p0.ssl.qhimg.com/t01c202cf2c269ae0c6.png)



在这点上，我们可以用万用表测试每个焊接点，验证它们的功能，这可以证明它们在串行通信中起作用：
<li>
pin1：这是一个地线接点。如果要验证此测试，将探针放到一个接地的部件如WiFi控制器上，并将另一个探针对准其他的pin，如果蜂鸣器有响声，这意味着两个路径之间存在很小的电阻。
</li>
<li>
pin2：它没有与任何部件连接。
</li>
<li>
pin3：这个应该是RX，在设备启动过程中，电压从3.28v降到3.27v。通过将一个探针接地，另一个探针放到pin上。我们可以在万用表上看到电压下降。
</li>
<li>
pin4：这应该是TX，在设备的启动过程，电压在3.28v 到2.6V间波动。这应该与启动消息发送到控制台有关，通过将一个探针接地，另一个探针接pin上。在设备的启动过程中，我们可以看到万用表上的电压在波动。
</li>
<li>
pin5：这个应该是VCC，电压一直在3.28v。通过将一个探针接地，另一个探针接pin上。
</li>
 如果没用过万用表或者对这个过程不熟悉，可以看这篇文章[http://www.devttys0.com/2012/11/reverse-engineering-serial-ports/](http://www.devttys0.com/2012/11/reverse-engineering-serial-ports/).

[![](https://p0.ssl.qhimg.com/t011fd053c9fb76a665.png)](https://p0.ssl.qhimg.com/t011fd053c9fb76a665.png)

在了解到这些信息后，我们就足以假设我们找到了正确的串口及其对应的pin配置，然后我们可以开始测试。通过烙铁以及吸除工具，我们可以清除现有的接头的焊料以及连接5号 headerpins。

我们可以通过使用Bus Pirate连接串行端口。其各种协议的文档比较全面详尽，在我们的例子中，我们使用如下方法：

    Bus Pirate IO Pin描述：[http://dangerousprototypes.com/docs/Bus_Pirate_I/O_Pin_Descriptions](http://dangerousprototypes.com/docs/Bus_Pirate_I/O_Pin_Descriptions)

    Bus Pirate UART 配置：[http://dangerousprototypes.com/bus-pirate-manual/bus-pirate-uart-guide/](http://dangerousprototypes.com/bus-pirate-manual/bus-pirate-uart-guide/)

Pin配置如下：
<li>
Bus Pirate (MOSI) -&gt;      Pin 3
</li>
<li>
Bus Pirate (MISO) -&gt;      Pin 2
</li>
<li>
Bus Pirate (GND) -&gt;      Pin 1
</li>
<li>
[![](https://p5.ssl.qhimg.com/t01eda0266129d0d627.png)](https://p5.ssl.qhimg.com/t01eda0266129d0d627.png)
</li>
在将Bus Pirate连接到WAG54G，我们还需要将其通过如下步骤连接到我们的工作站：

1.   通过USB将bus pirate连接到Windows工作站

2.   打开设备管理器，找到与Bus pirate 对应的COM口，在我们的例子中，使用COM4

3.   打开Putty，选择“Serial”单选按钮，在串行输入框键入COM4。

4.   将波特率调整至38400bps

5.   单击打开

将bus pirate连接到工作站后，最后一步是配置串行通信，使用Putty，执行以下命令：



```
m
select UART (3)
select 38400bps (7)
select 8,NONE (1)
select 1 stop bits (1)
select idle 1 receive polarity (1)
select normal (H=3.3V,L=GND) (2)
look at the macro menu (0)
select (3) bridge mode.
```



我们现在已经成功将bus pirate连接到工作站以及WAG54G上，我们可以打开路由器，看到Putty上出现了Linux的启动过程的日志信息。

[![](https://p1.ssl.qhimg.com/t0185c1c1a889980e97.png)](https://p1.ssl.qhimg.com/t0185c1c1a889980e97.png)

# **结论**

# 至此，我们已经成功获得了    WAG54G   的控制台访问权限。这对于在进入设备进行安全研究以及开发是相当有用的，可以成为硬件黑客的一个起始（比如附加的USB驱动程序，或者重新刷新组件）。在以后的博客中，我会介绍审查漏洞以及在开发过程中如何访问控制台的方法。
