> 原文链接: https://www.anquanke.com//post/id/184194 


# 蓝牙BLE设备追踪漏洞分析


                                阅读量   
                                **271134**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01cc97f1d70c4212e7.png)](https://p4.ssl.qhimg.com/t01cc97f1d70c4212e7.png)

作者：殷文旭 秦明闯 黄琳

## 发生了什么？

2019年7月17日，在瑞典斯德哥尔摩举行的第19届Privacy Enhancing Technologies Symposium上，波士顿大学的研究员David Starobinski和Johannes K Becker展示了一个蓝牙低功耗BLE设备普遍存在的新漏洞。该漏洞使得攻击者可以追踪安装了Windows 10系统的设备，包括Windows 10平板和笔记本，全部iOS和macOS设备，包括iPhone, iPad, Apple Watch, MacBook等。

[![](https://p4.ssl.qhimg.com/t015c677ce91a5ce2c0.png)](https://p4.ssl.qhimg.com/t015c677ce91a5ce2c0.png)

（论文网址：[http://people.bu.edu/staro/publications.html](http://people.bu.edu/staro/publications.html)）

根据标准，每个蓝牙设备都被分配一个独一无二的MAC(Media Access Control)地址。BLE设备会使用公开的（非加密）广播信道向其他设备广播自己的存在。为了保护用户隐私，Windows 10, Android, iOS, macOS等操作系统在广播时使用周期性变化的随机的MAC地址取代设备本身固定的MAC地址。

上述漏洞源于操作系统在实现MAC地址随机化时，实现得不够完美，广播信息的负载和MAC地址随机化不同步。利用该漏洞，攻击者可以突破Windows 10等系统引入的MAC地址随机化保护，持续追踪某台蓝牙设备，对用户隐私保护造成影响。

接下来，我们首先分析该漏洞产生的协议及实现背景，然后基于捕获的数据具体分析漏洞的产生原理及威胁。



## BLE协议背景

蓝牙Bluetooth是一种无线通信协议，工作在ISM (Industrial Scientific Medical) 2.400至2.485 GHz频段，主要用在设备间短距离传输数据。低功耗蓝牙Bluetooth Low Energy是2010年随蓝牙4.0引入的一个标准，顾名思义，该标准主要用在功耗严格受限的小型设备中，如可穿戴设备。较新的蓝牙5.0标准主要是增加了传输距离，目前尚未广泛使用。

BLE设备工作在40个物理信道上，每个物理信道的中心频点相隔2 MHz，最低中心频点和最高中心频点分别是2402 MHz和2480 MHz。其中三个物理信道被称为广播信道，中心频点分别是：2402 MHz, 2426 MHz和2480 MHz。选择这三个频点做广播信道是为了尽可能降低2.4 GHz频段内以Wi-Fi为主的其他协议的干扰。

[![](https://p1.ssl.qhimg.com/t010547a429719bcf55.png)](https://p1.ssl.qhimg.com/t010547a429719bcf55.png)

广播信道主要用来广播“advertising messages”，包括周期性的宣告存在的信息，对其他设备的扫描请求等。其余37个信道用来在配对的蓝牙设备间传输信息，并采用一种随机跳频的方式来降低干扰。

每台蓝牙设备都有一个独特的设备地址，和以太网、Wi-Fi的设备地址类似，都是同一个注册机构IEEE Registration Authority分配的。蓝牙标准5.0的第一卷中提到：“Each Bluetooth device shall be allocated a unique 48-bit Bluetooth device address (BD_ADDR). The address shall be a 48-bit extended unique identifier (EUI-48) created in accordance with section 8.2 (“Universal addresses”) of the IEEE 802-2014 standard.” 理论上，BD_ADDR在设备的生命周期中是固定的，而且设备在工作时会使用公开的广播信道向其他设备广播自己的存在，如果使用的MAC地址是BD_ADDR，设备则可能被追踪。

Windows 10, Android, iOS, macOS等系统在广播时可以使用周期性变化的随机的MAC地址取代设备本身固定的MAC地址，理论上可以避免设备被追踪。但Windows 10, iOS, macOS三类系统在实现MAC地址随机化时，没有确保广播信息负载的某些内容与MAC地址同步变化，攻击者同时追踪负载和MAC地址，就能将二者关联起来，绕过MAC地址随机化的防御。



## 漏洞分析与利用

BLE广播信道的格式如下所示：

[![](https://p5.ssl.qhimg.com/t015a7cb356d80d39c5.png)](https://p5.ssl.qhimg.com/t015a7cb356d80d39c5.png)

不同广播类型的PDU结构不同。例如：“Indirected advertising allows any device receiving the PDU to respond with a Scan Request (requesting information about available features) or a Connect Request.”其PDU结构如下：

[![](https://p1.ssl.qhimg.com/t01f79dafc89c09ed68.png)](https://p1.ssl.qhimg.com/t01f79dafc89c09ed68.png)

其中，AdvA，即Advertising Address，就是蓝牙设备的MAC地址。Windows 10, iOS, macOS等系统在发广播信息时，PDU中的AdvA是随机化的，AdvData也是随机化的，但二者的随机化周期不同步，导致攻击者可以持续追踪某台设备。

例如，安装Windows 10系统的设备，蓝牙广播信息的格式通常如下：

[![](https://p3.ssl.qhimg.com/t01c1e27d7b7749ca5a.png)](https://p3.ssl.qhimg.com/t01c1e27d7b7749ca5a.png)

Data的前4个字节在每个设备上都相同，但剩余的23字节是随机生成的，并且每台设备都不同。安装Windows 10的设备发出的BLE广播中，AdvA的变化周期大概是960秒，Data的后23字节变化周期大概是1小时，而且不同厂商设备的广播特性类似，意味着上述特性由操作系统决定。

[![](https://p4.ssl.qhimg.com/t0169a609476fb5a02e.png)](https://p4.ssl.qhimg.com/t0169a609476fb5a02e.png)

利用该特性，攻击者可以绕过MAC AdvA地址和AdvData随机化的防御，实现对特定设备的持久追踪，直到AdvA和AdvData随时发生变化。

iOS和macOS的追踪也与之类似，都是利用广播信息的PDU中AdvData包含设备独特的信息，但AdvA和AdvData随机化周期不同步，两种独特信息可以超越各自时间周期的限制被关联起来。

论文还提到了Fitbit手环这类BLE设备，这些设备发广播信息的时间间隔由厂商自行决定，随机化更新的周期也由厂商决定。

论文称Fitbit手环的BLE MAC地址是固定不变的。我们对国内某品牌A的手环的BLE广播包进行了分析，发现也是长期不变的。但另一品牌B的手环广播包却难以追踪，它没有发射普通的广播包。可见对于穿戴类设备来说，MAC地址的随机化实现取决于厂商。



## 协议中的规定

蓝牙协议的国际标准，设计地址随机化的特性。但是，我们注意到蓝牙协议对地址随机化的要求其实是比较宽松的。

[![](https://p1.ssl.qhimg.com/t014ec4064583317d48.png)](https://p1.ssl.qhimg.com/t014ec4064583317d48.png)

蓝牙协议允许使用静态地址（static address），目的大概是为了方便配对的设备在分开之后再次连接。例如手环跟手机之间的连接需要保持，如果手环的MAC地址经常变，再次靠近手机同步数据的时候，如何让手机认识手环，协议就会比较复杂。

标准建议可以在设备每次重启的时候改变静态地址。在我们对前述的品牌A手环强制重置之后，可以观察到MAC地址确实改变了。



## 漏洞修复情况

对Windows等操作系统来说，漏洞很快被修复了。比如最新的Win10系统，已经无法复现这个漏洞。但对于手环这类更新比较慢的IoT设备，漏洞还将存在一段时间。

很多无线通信协议都有追踪类的隐私安全风险，比如WiFi MAC地址追踪、移动通信的IMSI追踪等等。现在蓝牙、WiFi、移动网络5G，都有了相应的临时身份随机化的技术，就是为了防止追踪。但协议设计与产品实现之间还有差别，有些技术没有得到完美的实现，因此产生了漏洞。



## Reference
1. Tracking Anonymized Bluetooth Devices Johannes K Becker, David Li, and David Starobinski
1. [https://networkengineering.stackexchange.com/questions/36843/do-bluetooth-devices-have-mac-address-with-the-same-specification-as-the-mac-add/46262](https://networkengineering.stackexchange.com/questions/36843/do-bluetooth-devices-have-mac-address-with-the-same-specification-as-the-mac-add/46262)
1. [https://www.zdnet.com/article/bluetooth-vulnerability-can-be-exploited-to-track-and-id-iphone-smartwatch-microsoft-tablet-users/](https://www.zdnet.com/article/bluetooth-vulnerability-can-be-exploited-to-track-and-id-iphone-smartwatch-microsoft-tablet-users/)
1. [https://www.argenox.com/library/bluetooth-low-energy/ble-advertising-primer/](https://www.argenox.com/library/bluetooth-low-energy/ble-advertising-primer/)