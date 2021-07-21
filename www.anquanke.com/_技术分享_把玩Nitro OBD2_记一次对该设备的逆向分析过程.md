> 原文链接: https://www.anquanke.com//post/id/87068 


# 【技术分享】把玩Nitro OBD2：记一次对该设备的逆向分析过程


                                阅读量   
                                **290402**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：quarkslab.com
                                <br>原文地址：[https://blog.quarkslab.com/reverse-engineering-of-the-nitro-obd2.html](https://blog.quarkslab.com/reverse-engineering-of-the-nitro-obd2.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0178dde7eb95ad7660.png)](https://p5.ssl.qhimg.com/t0178dde7eb95ad7660.png)

译者：[blueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

 

**前言**

****

本文重点介绍针对Nitro OBD2进行逆向分析的整个过程，NitroOBD2是一个芯片调谐盒，可以插入到我们汽车中的OBD2连接器，以提高汽车的性能。关于该设备的性能，互联网上的网友们众说纷纭，有的人认为该设备不具有提高汽车性能的能力，也有的人认为该设备的确有提升汽车性能的能力，基于上述的事实，我准备通过逆向分析该设备以确定该设备是否具有提升汽车性能的能力。

<br>

**逆向分析的背景**

****

众所周知，汽车安全是一个非常广泛和有趣的领域，由于针对汽车实施攻击的载体众多，因此我们无法真正掌握汽车所能提供的全部能力。在日常工作中，我们使用[https://en.wikipedia.org/wiki/CAN_bus](https://en.wikipedia.org/wiki/CAN_bus)  总线，以不同的方式针对汽车进行了很多好玩的实验。基于之前的工作，我们开始关注CAN设备在世界范围内的应用，以及人们通过CAN总线在做些什么事情。

针对Nitro OBD2的逆向工作源于一位朋友告诉我们该设备能够监控驾驶和对汽车引擎进行重新编程，以节省燃料和使得发动机能够获得更多的动力，他问我们该设备是否真的具有这个性能，为了解答他的疑惑，我们在[http://amzn.eu/6yIOnhE](http://amzn.eu/6yIOnhE)  上买了一个Nitro OBD2设备，并开始着手对该设备的逆向工作，在对该设备逆向分析的过程中我们发现了一些有趣的事情。由于我们无法在Amazon的评论区写下整个分析过程，因此我们写了这篇博文。

<br>

**PCB分析**

****

在把这个东西塞进汽车之前，我们决定检查该设备里面究竟有些什么东西。

打开Nitro OBD2设备后，我们看到了熟悉的OBD2引脚排列。具体如下图所示，下图还标注了该设备中每个引脚的用途。

[![](https://p0.ssl.qhimg.com/t012ab58bb4c472ee00.jpg)](https://p0.ssl.qhimg.com/t012ab58bb4c472ee00.jpg)

首先，我们试图弄清楚CANH和CANL对应的引脚是否连接在一起，如果不是，那么我们是无法对该设备进行逆向工程分析的，连接的引脚对应于CAN总线，J1850总线以及ISO 9141-2协议，具体如下图所示：

[![](https://p5.ssl.qhimg.com/t01164c12b316eaf937.jpg)](https://p5.ssl.qhimg.com/t01164c12b316eaf937.jpg)

从下图中的电路板可以看出，连接到芯片的唯一有用引脚是与CAN有关的引脚，其他引脚都连接到LED，具体如下图所示：

[![](https://p4.ssl.qhimg.com/t0109055e08c94ddc12.jpg)](https://p4.ssl.qhimg.com/t0109055e08c94ddc12.jpg) 

在这一点上，我们可以重新创建电路板的基本布局：

**一个简单的电源电路**

**一个按钮**

**一个芯片**

**3个LED**

电路板似乎没有任何CAN收发器，或者该收发器被直接集成在了小芯片及其软件中。软件部分负责该设备所有的“神奇”功能，诸如：

了解汽车是如何工作的

检查汽车的状态

对汽车的某些设置进行修改

重新编程ECU

<br>

**CAN分析**

****

**设置**

确定这个设备是否真的在做某些事情的一个简单方法是将其插入到汽车的CAN总线上，并检查该设备是否发送任何信息。在我们的实验中，我们选择了Guillaume的汽车（2012年款的柴油铃木Swift），因为他习惯于使用ELM327和Android上的Torque与汽车进行通信，这些设备可以很好地获得有关汽车引擎的各种信息，并重置错误代码（DTC）。

为了看看Nitro OBD2是否在CAN总线上做了一些事情，我们只需要在插入之前和之后记录所有CAN消息，并检查Nitro OBD2是否发送新消息。 因此，我们首先使用RaspberryPi和PiCAN2来记录OBD端口上获取的所有CAN消息，以及使用[https://github.com/P1kachu/python-socketcanmonitor](https://github.com/P1kachu/python-socketcanmonitor)  工具来记录Stan端口上的数据。

以下设置用于直接从OBD2端口记录CAN消息，具体如下图所示：

 [![](https://p2.ssl.qhimg.com/t017ed02727aa4774ff.jpg)](https://p2.ssl.qhimg.com/t017ed02727aa4774ff.jpg)

我们还使用PicoScope检查了CAN信号。正如我们预期的那样，我们可以看到CAN_H和CAN_L信号。

 [![](https://p1.ssl.qhimg.com/t0168c27f1fb3c5e983.png)](https://p1.ssl.qhimg.com/t0168c27f1fb3c5e983.png)

接下来，我们需要在插入Nitro设备时记录CAN消息，由于汽车中只有一个OBD2端口，我们决定将我们的监控工具连接到Nitro设备内。因此，我们打开Nitro OBD2，并在Ground，CAN_High和CAN_Low上焊接了3根线，并将这些线插入到Raspberry的PiCAN2接口上，具体操作如下图所示。通过这种设置，一旦Nitro OBD2插入汽车，我们就可以嗅探到CAN总线流量。

[![](https://p5.ssl.qhimg.com/t0178655d68de0e43b6.jpg)](https://p5.ssl.qhimg.com/t0178655d68de0e43b6.jpg)

[![](https://p1.ssl.qhimg.com/t0144cf4a304d6f47bc.jpg)](https://p1.ssl.qhimg.com/t0144cf4a304d6f47bc.jpg)

  

**实验结果**

****

没有插入Nitro OBD2的CAN总线流量如下图所示：

[![](https://p3.ssl.qhimg.com/t01467e2148cb8282cd.png)](https://p3.ssl.qhimg.com/t01467e2148cb8282cd.png)

下图是插入Nitro OBD2的CAN总线流量：

[![](https://p2.ssl.qhimg.com/t013c3e2a2e3e1c99a9.png)](https://p2.ssl.qhimg.com/t013c3e2a2e3e1c99a9.png) 

通过快速的比较两个图像之间的区别后我们发现，在插入Nitro OBD2时没有记录新的数据信息。因此这个芯片并没有真正在CAN总线上进行通信。 它只是被动地观察CAN_H和CAN_L信号，以检查CAN是否处于活动状态，如果是则闪烁LED灯。

<br>

**分析芯片**

****

通过上面的实验分析，我们已经可以确定这个芯片没有在CAN总线上通信，这一结论是有一定的依据的，因为我们压根在电路板上就没有找到任何的CAN收发器。但是，该设备的单芯片上没有任何的雕刻，因此我们不能对其数据进行分析。 但是，由于我们的好奇心，我们打算看看芯片内部有些什么东西。 在200°C的硫酸快速处理后，下图所示的是Nitro OBD2芯片的内部图片：

 [![](https://p4.ssl.qhimg.com/t01b91427123b7b1aeb.jpg)](https://p4.ssl.qhimg.com/t01b91427123b7b1aeb.jpg)

在上面这张图中，我们可以看到RAM，Flash和CPU，但很少有其他的东西。这看起来像一个标准的微控制器，而且没有特殊的嵌入式设备，这款芯片的设计者有可能在其中嵌入CAN收发器吗？下图左侧是一个最常见的TJA1050 CAN收发器，Nitro的芯片与其并排放着，具体如下图所示：

 [![](https://p5.ssl.qhimg.com/t01b66b28d2c45cfa87.jpg)](https://p5.ssl.qhimg.com/t01b66b28d2c45cfa87.jpg)

正如上图所示的那样，CAN收发器的设计与Nitro OBD2的芯片非常不同。 此外，Nitro OBD2的芯片中没有任何空间可以用来放置一个CAN收发器。由此我们确认Nitro OBD的芯片中没有嵌入任何的CAN收发器并且无法在CAN总线上进行通信。

<br>

**另外一些要说的话**

****

通过我们对Nitro OBD2设备的逆向分析，我们确信该设备除了具有闪烁的LED功能之外，这个工具并没有做任何的事情。但是，有些人可能对这个结论仍然持怀疑态度，所以我们试图找到另一些证据来说服这些持怀疑态度的人。 以下是我们为了力证我们结论正确性所做的一些阐述：

有些人说你必须让汽车行驶200公里该设备才会有效，所以在我们只驾驶15公里就看CAN显示器的时候，怎么能够说Nitro OBD2肯定没用呢？但是我们将设备插入汽车后并没有生成任何新的仲裁ID，这意味着：

该设备使用我们测试车已经使用的仲裁ID与ECU进行通信，这是一个非常糟糕的做法，因为这会使ECU的通信混乱。

它不会查询任何内容，而只依赖于广播的消息。这就要求该工具需要知道任何车上的每个 CAN系统以用于了解每条消息的含义。这似乎比查询标准的OBD2 PID更加愚蠢，通过查询这些PID至少可以轻而易举地了解驾驶员的驾驶习惯（例如，加速器的踩踏速度，平均速度/RPM等）。

最后，我们对我们的分析非常有信心，因此可以得出以下结论。

<br>

**结论**

****

正如一个用户在亚马逊评论区中所说的那样：“节省10美元吧，把节省下来的钱用来给你的汽车加油才是最实际的。”
