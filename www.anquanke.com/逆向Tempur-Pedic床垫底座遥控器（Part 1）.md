> 原文链接: https://www.anquanke.com//post/id/169493 


# 逆向Tempur-Pedic床垫底座遥控器（Part 1）


                                阅读量   
                                **224511**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者aplante，文章来源：blog.aplante.io
                                <br>原文地址：[https://blog.laplante.io/2019/01/reverse-engineering-the-tempur-pedic-adjustable-base-remote-control/](https://blog.laplante.io/2019/01/reverse-engineering-the-tempur-pedic-adjustable-base-remote-control/)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p3.ssl.qhimg.com/t01b659d91b5181c695.jpg)](https://p3.ssl.qhimg.com/t01b659d91b5181c695.jpg)



## 前言

这是本系列文章（可能会有三篇）的第一篇。

代码放在BitBucket：[https://bitbucket.org/MostThingsWeb/temper-bridge/src/master/main/](https://bitbucket.org/MostThingsWeb/temper-bridge/src/master/main/)

大约在一年前，我决定把我的spring旧床垫换成TEMPUR-Contour Elite Breeze，它非常好用。我还给它选了一个可调节的底座([这个](https://play.google.com/store/apps/details?id=com.tempur.ergo&amp;hl=en))，这个也很好。它配有一个遥控器，如图所示：

[![](https://p0.ssl.qhimg.com/t01502e227c63cb7d4d.png)](https://p0.ssl.qhimg.com/t01502e227c63cb7d4d.png)

这个底座宣传的另一个功能是可以通过Android和iPhone应用进行控制。不幸的是，它的Android应用自2014年以来就没有再更新过了，所以我无法用我的Google Pixel进行控制，根据评论可知，我不是唯一一个。很明显，这需要DIY。



## 项目目标
1. 创建一个使用自己的RF（Radio Frequency, 射频）协议与底座通信的网关。
1. 开发一个Android应用，可以通过网关控制底座(下次)


## 类似项目

实现类似目标的其他项目可分为两类：
1. 与车载WiFi模块通话((例如：[https://github.com/docwho2/java-alexa-tempurpedic-skill](https://github.com/docwho2/java-alexa-tempurpedic-skill))
1. 将继电器集成到现有的遥控器中来模拟按钮按下的效果(例如：[http://www.quadomated.com/technology/automation/diy-tempurpedic-ergo-adjustable-bed-automation/](http://www.quadomated.com/technology/automation/diy-tempurpedic-ergo-adjustable-bed-automation/) , [https://github.com/tomchapin/tempurpedic-remote-relay](https://github.com/tomchapin/tempurpedic-remote-relay))
改变实际的RF协议的好处是：第一，不依赖于集成的WiFi；第二，不具有破坏性。



## 研究FCC文档

由于遥控器是一种无线设备，所以它是由FCC（<br>
美国联邦通信委员会）规范的。我们可以查找FCC ID([UNQTPTAES](https://fccid.io/UNQTPTAES))来了解有关该设备的一些有用信息。由于制造商的保密要求，我们无法获得BOM、原理图和结构图。在这种情况下，最有用的文档是[测试报告](https://fccid.io/UNQTPTAES/Test-Report/Test-Report-1836264)。

[![](https://p5.ssl.qhimg.com/t01ad8a8436de90c540.png)](https://p5.ssl.qhimg.com/t01ad8a8436de90c540.png)

下面是测试报告中一些有趣的摘录。

在第7页中，我们了解到在信道数和频率之间存在某种映射关系。该遥控器支持很多信道，这对于那些有多个底座的人来说很有用。

[![](https://p1.ssl.qhimg.com/t01c684fd877369e018.png)](https://p1.ssl.qhimg.com/t01c684fd877369e018.png)

在第12页我们可以看到我们即将分析的信号：

[![](https://p4.ssl.qhimg.com/t01e79ebb3e541e269a.png)](https://p4.ssl.qhimg.com/t01e79ebb3e541e269a.png)

第13-14页，遥控器通过无线电传送信息，例如按键信息。这意味着底座和遥控器遥控器之间没有持久的连接，而且通信可能是单向的(遥控器 =&gt; 底座)。这是有意义的，因为底座不需要和遥控器对话。

[![](https://p4.ssl.qhimg.com/t01d8007c9172b264a1.png)](https://p4.ssl.qhimg.com/t01d8007c9172b264a1.png)



## 软件无线电(Software-DefinedRadio,SDR)的初步研究

除了实际使用外，我还打算借这个项目的机会尝试使用SDR。尽管如此，在这里我不打算教授任何概念。

我选择的工具是HackRF One([Amazon链接](https://amzn.to/2FrJhlM))。使用测试报告作为指南，通过[SDR#](https://airspy.com/download/)相对来说很容易就能找到信号：

[![](https://p0.ssl.qhimg.com/t0175ed2d5873973f48.png)](https://p0.ssl.qhimg.com/t0175ed2d5873973f48.png)

右边是测试报告信号图，我们可以看到这两个信号非常接近，说明我们的方法是正确的。

结果表明，这里使用的调制方式是高斯频移键控（Gaussian frequency shift keying）。非常感谢我的朋友Tim让我知道这是FSK（频移键控, Frequency-shift keying）。



## 监听SPI（Serial Peripheral Interface, 串行外设接口）总线

我使用[GNU Radio](https://www.gnuradio.org/)来解调信号(在这里我不讨论这个问题，主要是因为我缺乏就这个问题发言的能力)。最后我厌倦了它，并查找一种更快的方式来逆向分析信号。

为此，我选择了Saleae逻辑分析仪(我用的是旧版；新版：[Amazon](https://amzn.to/2D2sgNb))。拆开遥控器，你会看到一个Si4431射频收发器：

[![](https://p5.ssl.qhimg.com/t01be46616ce71611f1.png)](https://p5.ssl.qhimg.com/t01be46616ce71611f1.png)

还有一个Renesas单片机：

[![](https://p5.ssl.qhimg.com/t019bfa9f6bc8f52248.png)](https://p5.ssl.qhimg.com/t019bfa9f6bc8f52248.png)

尝试dump uC的ROM并逆向分析固件很有吸引力，但是根据FCC早期的测试报告可以知道ROM保护被启用。也许下次我们可以试一试，因为存在这样的PIN绕过技术：[https://github.com/q3k/m16c-interface](https://github.com/q3k/m16c-interface)

但就目前而言，我们只是打算简单地监听连接uC和射频收发器的SPI总线。该总线用于配置射频芯片和传输数据。Si443x的数据表展示了很多可配置的设置：[https://www.silabs.com/documents/public/data-sheets/Si4430-31-32.pdf](https://www.silabs.com/documents/public/data-sheets/Si4430-31-32.pdf)

我们将在初始化期间(即安装电池后)捕获总线上的流量来了解是uC如何配置收发器的。这将揭示调制方法(剧透一下：即GFSK)和其他我们模拟遥控器需要的参数。方便起见，我编写了一小段解析SPI流量的Python脚本(在Saleae logic中导出为CSV文件)，并显示寄存器读写：

[![](https://p1.ssl.qhimg.com/t015d37d2287f9528bd.png)](https://p1.ssl.qhimg.com/t015d37d2287f9528bd.png)

流量展示了关于调制方法的一些细节。请注意，在本例中，我的遥控器被设置为9345信道，这就是它传递的方式。
- GFSK
- 标称载波频率：434.5856250 MHz(同样地，这取决于信道)
- 数据速率：12.8kbps
- 频偏（Frequency deviation）：25 kHz(相当于50 kHz带宽)
标称载波频率是中心频率的别称。所以，9345信道占用了[434.585 MHz-25 kHz，434.585 MHz+25 kHz]频段。



## 计算信道映射

那么遥控器是如何从“9345信道”得到434.5856250 MHz的呢？这个问题困扰了我大约两天。这不是简单的线性关系。我收集了几十个初始化序列，每次都有不同的(随机)信道号，并试着查找其中的联系。

不作进一步说明，最后的答案是下面的分段函数：

[![](https://p2.ssl.qhimg.com/t01fedec5bfbc7eb0a7.png)](https://p2.ssl.qhimg.com/t01fedec5bfbc7eb0a7.png)

它并没有看上去那么糟糕。事实上，我唯一需要弄清楚的是分段的部分：

[![](https://p1.ssl.qhimg.com/t01c294f81a3482c43f.png)](https://p1.ssl.qhimg.com/t01c294f81a3482c43f.png)

红色的部分对应于Si443x中的fc(frequency center，频率中心) 寄存器。因此，当用户改变射频信道时，uC需要做的就是调整收发器，只需改变fc寄存器。

上面的公式是从数据表中的这个公式推导出来的：

[![](https://p4.ssl.qhimg.com/t0124b0c3845e5e04f9.png)](https://p4.ssl.qhimg.com/t0124b0c3845e5e04f9.png)



## 旁注：Si443x跳频

Si443x有一个简单的特性，允许你从单个信道选择寄存器进行信道切换。首先设置标称载波频率，然后设置信道步长(增量&gt;=10 kHz)。它通常用于定时关键应用，如跳频。那么为什么Tempur pedic遥控器不使用它呢？由于该系统支持9999个信道，所以10 kHz的信道步长太大了。遥控器信道方案采用~156.2 Hz信道步长。



## Si443x包结构

回想一下我们如何处理突发通信（burst communication）。这意味着接收方需要随时准备好并侦听数据。像遥控器这样的设备怎样才能以一种高效的方式做到这一点呢？回答：前导码（preamble）(“唤醒”接收者)和同步字（sync-word）组合。

[![](https://p4.ssl.qhimg.com/t01ee00a6171baaff0c.png)](https://p4.ssl.qhimg.com/t01ee00a6171baaff0c.png)



## 前导码（preamble）

前导码被设计为既“容易”发现，又不太可能被随机接收。常见的选择是1和0的交替序列。Tempul-Pedic遥控器使用这个序列，长度为40位。

[![](https://p2.ssl.qhimg.com/t013a226b5e20d53deb.png)](https://p2.ssl.qhimg.com/t013a226b5e20d53deb.png)



## 同步字（sync-word）

前导码检测器可以在前导码中唤醒收发器。它如何知道数据的实际来源？这就是同步字的意义所在。在检测到前导码后，接收机在(可配置)一段时间内搜索同步字。

[![](https://p1.ssl.qhimg.com/t01f4d68686d967ed42.png)](https://p1.ssl.qhimg.com/t01f4d68686d967ed42.png)



## 包长

Si443x可以选择固定或可变长度模式。在这个例子中，遥控器使用可变长度模式，虽然我看到的来自它的所有数据长度都相同。因此，我们需要处理数据包长度报头。

[![](https://p1.ssl.qhimg.com/t01c9a08cfb8059eab7.png)](https://p1.ssl.qhimg.com/t01c9a08cfb8059eab7.png)



## 数据和CRC（Cyclic Redundancy Check, 循环冗余校验）

CRC是一种检测收发器错误的完整性校验。它是由Si443x进行处理的。

[![](https://p4.ssl.qhimg.com/t01d61593069ee907d8.png)](https://p4.ssl.qhimg.com/t01d61593069ee907d8.png)



## 数据

现在终于是时候分析遥控器实际发送的数据了。这是我用来解码协议的摘录表格。我把遥控器调到不同的信道，并按下各个按钮。

[![](https://p0.ssl.qhimg.com/t0115d71d87e3f2c647.png)](https://p0.ssl.qhimg.com/t0115d71d87e3f2c647.png)

很快我们就可以看到，每个传输在0x96开始，与信道和命令：

[![](https://p2.ssl.qhimg.com/t010734836803549409.png)](https://p2.ssl.qhimg.com/t010734836803549409.png)

接下来的三个字节与信道无关，与命令有关。

[![](https://p3.ssl.qhimg.com/t011f8c0237b4924300.png)](https://p3.ssl.qhimg.com/t011f8c0237b4924300.png)

接下来的两个字节是信道号。例如：0x03F2 == 1010(10)

[![](https://p4.ssl.qhimg.com/t015e4a657d5b8e5e8a.png)](https://p4.ssl.qhimg.com/t015e4a657d5b8e5e8a.png)

但最后那部分呢？这显然与命令和信道都不相关。

[![](https://p5.ssl.qhimg.com/t011a99f5d36d8999e6.png)](https://p5.ssl.qhimg.com/t011a99f5d36d8999e6.png)



## 逆向CRC

结果表明，每个传输中的最后一个字节是另一个CRC。但是[哪一个](https://users.ece.cmu.edu/~koopman/crc/crc32.html)呢？没有一个是共同的。值得庆幸的是，有一些逆向CRC的工具。我选择了这个：[http://reveng.sourceforge.net/](http://reveng.sourceforge.net/)

你所需要做的就是给它一个输入(数据)=&gt;输出(CRC)的映射，它将强制执行CRC参数。我得到的输出如下图所示：

[![](https://p2.ssl.qhimg.com/t01611650c59ba67f24.png)](https://p2.ssl.qhimg.com/t01611650c59ba67f24.png)

参数：width=8, poly=0x8D, init=0xFF, refin=false, refout=false, xorout=0x00, check=0xFD, residue=0x00, name=(none)

“name=(none)”部分意味着这组参数不对应于任何熟悉的CRC。

回想一下，Si443x已经有了自己的CRC。为什么遥控器要用另一个呢？我的猜测是，工程师们选择添加这个应用级别的CRC，用来防止uc和收发器之间的数据损坏。例如，假设SPI总线上的一些噪声导致收发器“看到”uC打算发送的不同数据。收发器无法知道这一点，所以它会尽职尽责地传送它。底座的接收器可能识别也可能不识别损坏的命令。应用级别的CRC确保可以检测到SPI总线上的传输错误。



## “突发”命令

遥控器上的大多数按钮似乎没有去抖动（debounce）功能。例如，当按下诸如STOP或FLAT之类的命令时，遥控器实际上会将其发送一至三次(根据我的经验)。这是一件好事，因为它增加了接收方实际接收命令的可能性。这些类型的命令是幂等的，所以即使底座接收到多个相同的命令也没关系。

用来抬高/降低腿部和头部的按钮被按下时，会使相应的命令被重复传送，直到按钮松开为止。



## 按摩按钮

按摩按钮是个有趣的例子。这六个按钮可以增大/减小腿部、腰椎和头部区域的按摩强度。最开始，我猜测它们是通过每个按钮对应一个命令来实现，就像抬高/降低腿部/头部的按钮一样。但事实上它更加复杂。

底座有11个按摩强度，介于0到10之间，0为关闭。遥控器记录每个区域的当前按摩强度。当用户点击“+”或“-”按钮时，遥控器发送一个对区域和新按摩强度进行编码的按摩命令。换句话说，它传递绝对的按摩强度。这意味着它实际上有33个离散命令来实现遥控器的按摩按钮(11个级别*3个区域)。这与抬高/降低腿部/头部的按钮形成对比，后者仅仅传递相对定位命令(“+1”或“-1”)。

那么为什么按摩功能会这么复杂？这是我的理论，在前面的“突发命令”一节中，我们了解到遥控器发送多次命令，以便提高正确接收命令的概率。这对于幂等命令来说很好，比如STOP、FLAT等。对于抬高/降低腿部/头部的按钮来说，这也是很好的，因为它们的位置划分得非常细，用户按下抬高腿部按钮可能不会注意到+1或+3的差别。但由于按摩只有11个级别，如果有一次“增加腰部按摩强度”添加了+1，而下一次添加了+3，用户肯定会注意到差别。



## 自动选择信道

系统的一个有趣的特性是能够自动选择信道。要做到这一点，需要按住FLAT和STOP按钮10秒，然后按下STOP按钮。遥控器的液晶显示器在显示新的射频信道时会闪烁。当它闪烁时，拔掉底座插头然后重新连接。如果操作正确，底座中的继电器会确认新信道。

当遥控器闪烁显示新信道时，实际上它是在内部通过一个特殊的广播信道5568(fc = 25088, frequency = 433.9200000 MHz)发送信道号。根据推测，底座插入电源后会立即收听这个信道。

注：系统的一个限制是，射频信道是完全随机的，尽管有9999个可能的信道，但可能会发生碰撞。



## 制作接收器的原型

理解协议后，我尝试建立一个接收器，它可以解码我的Tempur-Pedic遥控器命令。我选择了下面的Si443x收发器作为原型：[https://www.tindie.com/products/modtronicsaustralia/rfm22b-wireless-breakout-board-800m-range/($22.95](https://www.tindie.com/products/modtronicsaustralia/rfm22b-wireless-breakout-board-800m-range/(%2422.95)). 最后，我实际上将选择Si446x([示例](https://www.tindie.com/products/nifteecircuits/low-current-transceiver-with-antenna-si4463/))，因为Si443x已经停产。

我使用的单片机（Microcontroller）是ESP32(21.95美元)：[https://www.sparkfun.com/products/13907。这是一个完美的选择，因为它支持蓝牙、低功耗和WiFi，我计划在这个项目的下一部分使用这两种功能，在这个项目中，我会开发自己的Android应用来控制我的底座。](https://www.sparkfun.com/products/13907%E3%80%82%E8%BF%99%E6%98%AF%E4%B8%80%E4%B8%AA%E5%AE%8C%E7%BE%8E%E7%9A%84%E9%80%89%E6%8B%A9%EF%BC%8C%E5%9B%A0%E4%B8%BA%E5%AE%83%E6%94%AF%E6%8C%81%E8%93%9D%E7%89%99%E3%80%81%E4%BD%8E%E5%8A%9F%E8%80%97%E5%92%8CWiFi%EF%BC%8C%E6%88%91%E8%AE%A1%E5%88%92%E5%9C%A8%E8%BF%99%E4%B8%AA%E9%A1%B9%E7%9B%AE%E7%9A%84%E4%B8%8B%E4%B8%80%E9%83%A8%E5%88%86%E4%BD%BF%E7%94%A8%E8%BF%99%E4%B8%A4%E7%A7%8D%E5%8A%9F%E8%83%BD%EF%BC%8C%E5%9C%A8%E8%BF%99%E4%B8%AA%E9%A1%B9%E7%9B%AE%E4%B8%AD%EF%BC%8C%E6%88%91%E4%BC%9A%E5%BC%80%E5%8F%91%E8%87%AA%E5%B7%B1%E7%9A%84Android%E5%BA%94%E7%94%A8%E6%9D%A5%E6%8E%A7%E5%88%B6%E6%88%91%E7%9A%84%E5%BA%95%E5%BA%A7%E3%80%82)

可以在这里找到(还在开发中)代码：[https://bitbucket.org/MostThingsWeb/temper-bridge/src/master/main/](https://bitbucket.org/MostThingsWeb/temper-bridge/src/master/main/)

我很快就会发布更多的细节(希望如此)。



## 下一步

接收端代码已基本完成，所以接下来我将处理的发射器部分。然后，我将开发蓝牙低功耗（Bluetooth Low Energy）接口和一个Android应用。
