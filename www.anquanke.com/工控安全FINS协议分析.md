> 原文链接: https://www.anquanke.com//post/id/188455 


# 工控安全FINS协议分析


                                阅读量   
                                **629750**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t0170f06de6d0dc220d.jpg)](https://p4.ssl.qhimg.com/t0170f06de6d0dc220d.jpg)



## 前言

PLC（Programmable Logic Controller)可编程逻辑控制器，早期的PLC只是一种具有微处理器的进行自动化控制的数字逻辑控制器，随着可编程逻辑程序的发展，现在PLC已经共犯应用在工业控制领域，发展成一种接近于一台轻巧型计算机的可编程自动化设备，用来代替代替由数量众多的继电器和计数器组成的自动化控制系统，PLC控制技术现在早已成为工业界不可或缺的一部分。日本OMRON公司生产的小型PLC作为一种功能完善的紧凑型PLC，以其结构灵活、传输质量高、速度快、范围广、低成本、适用面广等优点，成功使其小型PLC在国内的市场上有了较高的占有率。今天我们就来介绍一下 由OMRON公司开发的私有公开协议（只有厂商自身设备支持并提供官方文档）-FINS协议。



## FINS简介

FINS（factory interface network service）协议是由日本OMRON公司开发的一种工业自动化控制网络指令控制系统，用于在PLC和计算机之间进行通信的一种网络协议，通过使用FINS指令可以实现在以太网、控制网络的Controller Link和RS232C／485串行通信三种网络之间的无缝通信。关于这三种通信方式的主要参数如下

网络 | RS232C /485 | Controller Link | 以太网

传输速率 | 最高19.2kb/s | 最高2MB/S | 10~100MB/s

传输距离 | 15m | 传输速率最高时为500m | 100m/段

最大节点数 | 32 | 32 | 254

从上面的数据我们不难看出，如果我们使用RS232C/485，以它最高19.2kb/s的速率来看已经满足不了现代网络数据量大，距离远，实时要求高的控制系统特点。

而Controller Link的设计方案可以达到2MB/S和500m的传输距离比RC232C/485要强一些但是它依靠上位机安装CLK支撑卡，所以在可扩展性上面不如以太网方案。

最后我们来看一下以太网方案，10~100MB/S的传输速率已经可以满足现代工业所需求的实时性传输数据，而100m/段的传输距离使得可以进行灵活组网，最高254个节点可以实现pc和plc之间一对一、一对多、多对多等多种控制方案。而且 现在工业设备的上位机都配有网卡，不需要再额外添加硬件，在实际操作上具有了巨大的便捷性。这就使得工业以太网满足了良好的可扩展性、实用性、实时性等需求。所以OMRON通过提供Omron FINS Ethernet 驱动程序将包括HMI、SCADA、Historian、MES、ERP和无数自定义应用程序在内的客户端应用程序和控制器连接。



## FINS与TCP/IP和UDP/IP协议

我们都知道TCP/IP模型中从底层开始分别是物理层、数据链路层、网络层、传输层和应用层。FINS协议就工作在应用层上。上文中我们也曾经说过FINS采用以太网方案进行信息传输，在以太网FINS通信时候，数据通过作用在数据传输层的TCP/IP或者UDP/IP包来收发。以下我们以OMRON公司的ETN11以太网单元举例来给大家看一下FINS和TCP/IP之间的关系。

[![](https://i.loli.net/2019/10/10/gyxE4nIAUs6GTV8.png)](https://i.loli.net/2019/10/10/gyxE4nIAUs6GTV8.png)

如图所示，在我们实际通信过程中，远程设备在网络层使用IP地址，传输层定义了本地TCP或UDP的端口号用来为下面FINS通信提供端口，而在应用层则使用FINS节点地址（节点号），这里简单的给大家介绍一下节点号，节点这个概念类似于我们linux里面的inode,作为一个有着定长字节的表，表里面包含着文件大小，所有者等一些信息，而节点号就相当是这个节点的身份证号，在使用到对应节点内容时只需要通过节点号相对应就可以使用相关节点内容。

回到正题， 通常我们在以太网通信时使用IP地址，而在FINS通信中使用网络号、节点号和单元号来对应不同的设备，使用节点号可以让设备在IP地址和节点号之间转换，节点号提供了在Control Link网和以太网之间统一的寻址方式，这种方法使不同网络之间的设备可以有一种统一的通信方式，设备可以通过自动转换、IP地址表和复合地址表三种方法进行节点号和IP地址的转换。确定使用哪种转换方法这一步是我们使用FINS首先要做的工作。接下来给大家简单说一下这三种方式的区别。

自动转换（Automatic Generation）：顾名思义自动转换为FINS节点号

IP地址表（IP Address Table）：从INS节点之间的对应表转换而来数字和IP地址。

复合地址表（Combined Method）：引用IP地址表，如果IP地址未注册接下来就从FINS转换为节点号。

详情见下图

[![](https://i.loli.net/2019/10/11/QLND8ksBFiWHV9T.png)](https://i.loli.net/2019/10/11/QLND8ksBFiWHV9T.png)

一般来说FINS的默认端口号是9600，如果不是就需要自行设置端口号，无论怎样都要将所有以太网单元的设成相同的值。

一般来说，我们认为FINS帧属于链路层，欧姆龙所有产品都支持FINS/UDP方式传输，这种方式有着较快的传输速度，这是因为UDP协议是一种无连接协议，两个节点之间传输的时候节点间没有明确连接的对等关系。还有一种方式是FINS/TCP，这种方式适用于CS1W-ETN21和CJ1W- ETN21两种，我们通过将FINS作为UDP的数据区来利用TCP/IP协议进行传输，这种方式的好处是可靠性高。



## FINS帧格式分析

FINS通信是通过交换FINS命令帧和其响应帧（有的没有响应）进行的，命令帧和响应帧的都为FINS头组成，用于存储传输控制信息，分别存储命令和响应信息。

下面我们来分别看一下命令帧和响应帧。

### <a class="reference-link" name="%E5%91%BD%E4%BB%A4%E5%B8%A7"></a>命令帧

首先来看一下命令帧的组成，如下图

[![](https://i.loli.net/2019/10/11/iah4J9fL25pBFYU.png)](https://i.loli.net/2019/10/11/iah4J9fL25pBFYU.png)

接下来就带着大家一个个的来简单分析一下。

FINS header：

ICF: 1字节，用来显示框架信息。

RSV: 1字节，由系统保留，设置为00（十六进制）

GCT: 1字节，网关允许数量，设置为02（十六进制）

DNA: 1字节，目的网络地址，用来指定目标节点网络号，0为本地，01~7F是目标网络

DA1: 1字节，目的节点地址，指定发送命令节点号，00为本地，01~7E是目标节点号，当 安装多个网络单元时，FF为广播编号。

DA2：1字节，目的单位地址，指定目标节点的单元编号，00本地，10~1F是CPU总线单元，E1内板，FE已联网

SNA：1字节，源网络地址，指定源节点所在网络号，00本地，01~7F，网络号

SA1：1字节，源节点地址,同上

SA2：1字节，源单元地址，同上

SID：1字节，服务编号，标识生成传输过程，设置00~FF所需数字，响应中返回相同数字来匹配命令和响应。

FINS command:

MRC: 1字节，主要请求代码

SRC：1字节，子请求代码

FINS parameter/data

data field: 最大2000字节，命令参数和数据，长度取决于MRC和SRC。

### <a class="reference-link" name="%E5%93%8D%E5%BA%94%E5%B8%A7"></a>响应帧

还是先看一下组成图

[![](https://i.loli.net/2019/10/11/3miUedb9Q8vXfEq.png)](https://i.loli.net/2019/10/11/3miUedb9Q8vXfEq.png)

我们可以发现，命令帧和响应帧的区别不大，在于FINScommand以下部分，我们来看一下。

MRES：1字节，主响应代码

SRES：1字节，子响应代码

Data:最大1998字节，有些数据长度为0。

为什么响应帧的最大值要比命令帧少两个字节呢，原因在于响应帧的MRES、SRES和data合一起组成了FINS数据域，而命令帧的FINS数据域是由Data值独自组成的。

下面是我找到的FINS功能码供大家查询。

[![](https://i.loli.net/2019/10/11/Rzh4qyFDn5u8GMN.png)](https://i.loli.net/2019/10/11/Rzh4qyFDn5u8GMN.png)

[![](https://i.loli.net/2019/10/11/BSofcPdmbeQwjsI.png)](https://i.loli.net/2019/10/11/BSofcPdmbeQwjsI.png)



## FINS数据包分析

前面关于FINS协议的基本知识和组成介绍完毕了，下面带大家一起来就FINS数据包来分析一下。

我们来看这个数据包，是由多种FINS命令组成的包。

[![](https://i.loli.net/2019/10/11/oK4i2TP6fLFzrsl.png)](https://i.loli.net/2019/10/11/oK4i2TP6fLFzrsl.png)

我们随便点开几个数据包，发现他们的组成除了Command code和Data部分都是一样的。接下来我们就具体看一下。

[![](https://i.loli.net/2019/10/11/8QfKVJBtn5kIcPX.png)](https://i.loli.net/2019/10/11/8QfKVJBtn5kIcPX.png)

### <a class="reference-link" name="Omron%20header"></a>Omron header

[![](https://i.loli.net/2019/10/11/MNCsyaGx2JcKt1P.png)](https://i.loli.net/2019/10/11/MNCsyaGx2JcKt1P.png)

我们从上面开始一步步往下分析

OMRON ICF Field:上面我们已经介绍过ICF的作用了，介绍框架信息，这个只占一个字节80，但里面有着网关位，数据类型位，响应设置位，

1 … …. =网关位：使用网关（0x01）

0 .. …. =数据类型位：不响应（0x00）

.0。…. =保留位0：0x00

..0 …. =保留位1：0x00

… 0 … =保留位2：0x00

…. 0 .. =保留的位3：0x00

….. 0 =保留的位4：0x00

… … 0 =响应设置位：需要响应（0x00）

我们看上面第一个1就代表着网关位使用网关（0x01),下面的0代表数据类型位不响应，后面跟着5个保留位，最后一位0代表着响应设置为响应。

保留位可以做的有如下几条：0x00 网关计数：0x02 目标网络地址：本地网络（0x00） 目标节点号：SYSMAC NET / LINK（0x00） 目标单元地址：

PC（CPU）（0x00） 源网络地址：本地网络（0x00） 源节点号：SYSMAC NET / LINK（0x00） 源单元地址：PC（CPU）（0x00） 服务编号：0x7a 命令代码：名称删除（0x2602）。

接下来Reserved和Gateway Count都是固定保留位就不仔细说了。

Destination network address:后面是Local network代表着本地网络间，上文也提到过这里在不同网络上的变化。

Destination node number:目标节点号，SYSMAC NET/LINK代表着光纤网，用集散控制SYMAC LINKT中型网。这里在命令帧的时候标记的是SYSMAC NET/LINK(0x00),但在响应帧的时候就是SYSMAC NET（0x63），但是在另一个数据包响应帧内容就和命令帧一样，这点我也没有找到答案，如果有了解的大佬希望能解答一下

[![](https://i.loli.net/2019/10/11/o63KnwDPaAIFgfX.png)](https://i.loli.net/2019/10/11/o63KnwDPaAIFgfX.png)

Destination unit address:目的单位地址，由于这里都是本机模拟实验，所以地址都是PC（CPU)

Service ID: 服务标识，由命令帧生成，在响应帧回应相同的值。

[![](https://i.loli.net/2019/10/11/wAXglIF5iPTpK9U.png)](https://i.loli.net/2019/10/11/wAXglIF5iPTpK9U.png)

[![](https://i.loli.net/2019/10/11/EJGr2S7FPwVoLDu.png)](https://i.loli.net/2019/10/11/EJGr2S7FPwVoLDu.png)

最后是Command CODE，这个是一个命令和响应包的最关键内容，有着内容和命令代码。

### <a class="reference-link" name="Command%20Data"></a>Command Data

这部分就很好说了，就是命令或响应的内容。



## 安全状况

根据灯塔实验室2015年对全球Omron设备的一次扫描，全网暴露最多的像美国、意大利、西班牙、法国等，几乎大部分都在欧美国家，但是作为Omron公司所在的日本反而不多，像是这种PLC的端口一旦暴露在公网上，就可以通过软件或协议直接操作设备，所以在实际配置上建议设置密码，架设防火墙。

而在15年FINS协议暴露出利用PLC的强制功能（强制设置的内存变量不受程序影响，脱离用户逻辑程序控制，在状态不更换下变量值不变)来控制PLC设备。截止到2019年7月，全国OMRON设备暴露排名第五，CP1型号设备出现3个高危漏洞，PLC的安全问题已经刻不容缓。建议是通过武力隔离、加强日志监控、增加安全评估和渗透测试采用更安全的操作系统等方法来加强PLC的安全控制
