
# 【技术分享】基于BLE的IoT智能灯泡的安全漏洞利用


                                阅读量   
                                **111646**
                            
                        |
                        
                                                                                                                                    ![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：attify.com
                                <br>原文地址：[http://blog.attify.com/2017/01/17/exploiting-iot-enabled-ble-smart-bulb-security/](http://blog.attify.com/2017/01/17/exploiting-iot-enabled-ble-smart-bulb-security/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85863/t0184e54ad7b4cb7130.png)](./img/85863/t0184e54ad7b4cb7130.png)**

****

翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：170RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

目前物联网和智能设备已经日益普及，并且当我们谈论物联网时，首先想到的往往是智能家居。智能家居通常涉及各种设备，包括智能冰箱、智能灯泡、电源适配器、水壶、烤面包机、蛋盘，等等。

在这篇文章中，我们将讨论如何接管基于BLE的IoT智能灯泡，与之进行交互，改变颜色，并在这个过程中考察BLE的安全机制。

在这篇文章中，我们将要向读者介绍的主题包括：

使用Ubertooth嗅探BLE

主动嗅探流量

修改BLE的处理程序和特征值

控制设备

为了顺利阅读本文，您需要做好以下准备：

硬件

笔记本电脑

Ubertooth

软件

hcitool

ubertooth-utils

Gatttool

<br>

**基于BLE的IoT智能灯泡的漏洞利用**

将灯泡连接到电源。然后，试着使用智能手机来打开和关闭灯泡，以确保它工作正常。接下来，我们首先要做的是找到目标设备的蓝牙地址。

第1步：我们使用hcitool查找主机附近存在的所有可用的BLE设备。

```
hcitool lescan
```

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016bcd7bc24ab1b2b6.png)

在上图中，我们能够看到自己周围的多个设备的蓝牙地址。通过检查后发现，我们的灯泡的蓝牙地址看起来像是88：C2：55：CA：E9：4A，该设备的蓝牙名称是cnligh。

第2步：现在，我们已经知道了目标设备的BD_ADDR（蓝牙地址），接下来就可以使用gatttool来查看目标设备中运行的各种服务了。使用gatttool -I切换到交互模式，然后通过给定的BD_ADDR连接到目标设备。



```
gatttool -I
connect 88:C2:55:CA:E9:4A
primary
```

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018cecba603d3ccaf9.png)

在上图中，有三个主要的服务在运行，对应于三个UUID。其中，00001800和00001801是Bluetooth SIG定义的服务，而UUID 0000f371则并非由蓝牙SIG定义的服务。

第3步：现在我们可以使用char-desc列出特定UUID（0000f371）中的所有句柄。最好指定attr和end group句柄，就本例而言为0x0010 0xffff 

```
char-desc 0x0010 0xffff
```

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0180790579319d429a.png)

在上图中，我们给出了特定的UUID 0xffff的句柄列表。

通过观察，我们发现服务0xfff1到0xfff9是由制造商定义的，其他的则是由蓝牙技术联盟采用的服务，如主要服务、特征、特征用户描述。如果您想进一步了解服务及其具体的UUID值的话，请参考[https://www.bluetooth.com/specifications/gatt/services](https://www.bluetooth.com/specifications/gatt/services) 。

第4步：这里有很多句柄同时我们不知道可以向哪些句柄写数据，所以我们尝试用句柄值来读取句柄 

```
char-read-hnd 0x0012
```

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f3fec5797597e58d.png)

当我们尝试读取句柄时，会收到如上图所示的错误信息。当然，这里有点难度，因为我们不知道哪些句柄可以读取/写入数据，甚至连数据包的格式都不知道。

为了了解数据包格式和句柄，我们可以嗅探BLE数据包。这方面，Ubertooth是一种有效的工具，可用于BLE流量的主动嗅探。

第5步：利用ubertooth-btle嗅探BLE数据包。为此，我们可以直接使用ubertooth-btle -f命令。如果您有多个设备，可以使用ubertooth-btle -f -t &lt;BD_ADDR&gt;与目标设备的蓝牙地址。在本例中，BD_ADDR是88：C2：55：CA：E9：4A 

```
ubertooth-btle -f -t88:C2:55:CA:E9:4A
```

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019fa445d45f0951fc.png)

第6步：为了捕获数据包，可以使用以下命令 

```
ubertooth-btle -f -t88:C2:55:CA:E9:4A -c smartbulb_dump.pcap
```

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fec0266bb10be5e1.png)

-c用于捕获由文件名指定的pcap中的数据包。

现在打开您的灯泡手机应用程序并连接灯泡。连接成功后，请执行一个动作，如改变灯泡的颜色，ubertooth将捕获所有的数据包。

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01bdbf63236a3c3223.png)

上图展示的是灯泡的广告包，并且需要注意以下几点

访问地址（AA）为0x8e89bed6，用于管理链路层，它是一个随机数。

它是37频道，专们用于广告的频道之一。

数据包PDU是ADV_IND，意味着它是可连接的，单向的和可扫描的。

AdvA id是88：c2：55：ca：e9：4a，这只是广告设备的BD_ADDR

Type 01标志表示AdvA地址是随机的。

如果仔细观察上图，我们将注意到这里有两个值——来自目标设备的扫描响应（SCAN_RSP）和来自应用程序的扫描请求（SCAN_REQ） 

**SCAN_REQ**

ScanA是一个6字节的扫描地址，TxAdd指示它是随机值还是公共地址

AdvA是一个6字节的广告地址，PDU中的RxAdd表示地址是公共的还是随机的 

**SCAN_RES**

AdvA是一个6字节的广告地址，TxAdd表示地址的类型，是随机的还是公开的

ScanRspData是来自广告客户的可选广告数据 

**Connec_REQ**

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01def570e073b339d7.png)

下图展示的是嗅探到的数据

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016975f296930cef58.png)

第7步：下面使用wireshark分析捕获的数据包，首先启动wirehark，然后打开捕获的pcap文件。

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0139d4ac855c2c6501.png)

这时，它将显示所有捕获的数据包。

第8步：现在我们需要在这些捕获的数据包中查找ATT数据包。其中，最简单的方法就是使用wireshark中的过滤器选项，即键入btl2cap.cid == 0x004

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014f3066ebd58d03ba.png)

如果我们观察上图，会发现这里只有ATT数据包和数据包方面的信息。

第9步：这里，我们在改变灯泡的颜色的同时已经捕获了数据包，所以让我们来研究一下写请求数据包。

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0185d3e03ad620cd42.png)

现在我们知道数据将被写入句柄0x0012，该句柄属于我们需要弄清楚的某个UUID。

第10步：如果我们分析特定的写请求包，我们可以发现相应的访问地址、CRC值、操作码、句柄和UUID 

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014eea64e4e55adb25.png)

在上图中我们可以看到

访问地址：0xaf9a9515

主从地址

CRC：0x6dcb5

句柄：0x0012

UUID：0xfff1

值：03c90006000a03000101000024ff000000006 

[![](./img/85863/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01258c9c83b367a379.jpg)

报头长度为2字节，它紧随PDU之后

模式选择是硬编码的，用于控制灯的颜色

0024ff是RGB值，如果改变这6个字节的内容，就可以获得所需的颜色

第11步：我们可以使用gatttool将值写入特定句柄或UUID， 



```
char-write-req 0x0012 03c90006000a03000101000024ff00000000 //bluish green
char-write-req 0x0012 03c90006000a0300010100ff000000000000 // Red
char-write-req 0x0012 03c90006000a030001010000ff0000000000 //Green
char-write-req 0x0012 03c90006000a03000101000000ff00000000 // Blue
char-write-req 0x0012 03c90006000a03000101000024ff00000000 //bluish green
char-write-req 0x0012 03c90006000a0300010100ff000000000000 // Red
char-write-req 0x0012 03c90006000a030001010000ff0000000000 //Green
char-write-req 0x0012 03c90006000a03000101000000ff00000000 // Blue
```

第12步：若要打开和关闭灯泡，可以更改数据中的开/关位 



```
char-write-req 0x0012 03c90006000a030101010000000000000000 //Off
char-write-req 0x0012 03c90006000a0300010100ff000000000000 //On
char-write-req 0x0012 03c90006000a030101010000000000000000 //Off
char-write-req 0x0012 03c90006000a0300010100ff000000000000 //On
```



03c90006000a030101010000000000000000将关闭灯泡，RGB值应为零，否则灯泡不会关闭

03c90006000a0300010100ff0000000000000将打开灯泡，这里RGB值是强制性的。

<br>

**总结**

本文介绍了如何利用基于BLE的智能灯泡的安全漏洞，在将来的文章中，我们将继续研究其他BLE的漏洞利用技术、Zigbee漏洞利用技术等，敬请期待。
