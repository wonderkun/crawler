> 原文链接: https://www.anquanke.com//post/id/181171 


# WiFi探针获取无线网络信息技术简介与测试


                                阅读量   
                                **268998**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t01f6950adab4ab5287.png)](https://p4.ssl.qhimg.com/t01f6950adab4ab5287.png)



随着科学技术的快速发展，WiFi已经逐渐遍布到各个家庭和公共场所，但其中的问题也层出不穷。黑客可将个人热点伪装成免费WiFi吸引他人连接从而获取账号密码，今年曝光的WiFi探针技术，甚至无需用户主动连接WiFi即可捕获个人信息。

本期安仔课堂，ISEC实验室肖老师为大家解密WiFi探针是如何获取无线网络信息的。



## 一、WiFi探针应用场景

首先了解这样一个场景：用户在线下逛了几个楼盘或者某个商场，并未留下个人信息，之后却经常收到相应产品信息的推广电话。<br>
据报道，这些公共场所已部署了WiFi探针设备，在用户进入设备部署范围时，将自动采集个人手机mac地址信息，关联获取用户信息。之后外呼公司利用“机器人”拨打骚扰电话，进行大范围精准推送，取代人工外呼的传统拨打方式。这是当前营销广告公司的一种主流营销方式，与店面合作，成本低廉、效果颇丰，但个人信息的泄露，已让用户成为“透明人”。

## 二、WiFi探针实现原理

### <a name="1.%20WiFi%E4%BF%A1%E9%81%93%E6%89%AB%E6%8F%8F%E5%B7%A5%E5%85%B7"></a>1. WiFi信道扫描工具

这种神秘的Wi-Fi探针，实际是“WiFi信道扫描工具”。目前市面上的WiFi有2.4G、5G两个频段，每个频段有不同的信道划分，Wi-Fi探针设备通过在各个信道被动监测，采集周围的数据帧内容，发现周边手机、笔记本、路由器等无线设备，从而满足客流统计、精准营销等需求。此外，这种“Wi-Fi信道扫描工具”处于被动监测模式，无需用户主动连接某个WiFi，仅需打开手机WiFi功能时即可捕获。

### <a name="2.%20%E6%89%8B%E6%9C%BA%E4%BC%AA%E9%9A%8F%E6%9C%BAmac"></a>2. 手机伪随机mac

某些手机品牌对WiFi探针技术进行了防护，在未连接WiFi的情况下手机广播的是随机mac，即使被WiFi探针设备捕获也无法关联到用户正确信息。这种伪随机mac可避免无任何操作下WiFi探针对当前环境的被动监测，iOS 9.0以上版本也有类似机制。

### <a name="3.%20WiFi%E8%AF%B1%E5%AF%BC"></a>3. WiFi诱导

但伪随机mac机制并不能完全保证用户网络安全，因为WiFi协议默认当用户连接过某个WiFi后，再次发现同名免费WiFi即可自动连接。处于WiFi连接状态的真实手机mac地址即可被捕获，设备厂家则利用协议机制诱导用户连接伪造WiFi，从而捕获到用户手机mac信息。

[![](https://p5.ssl.qhimg.com/t01316573dff7e9c0cc.jpg)](https://p5.ssl.qhimg.com/t01316573dff7e9c0cc.jpg)

图1



## 三、WiFi探针实现原理模拟

现在我们进行WiFi探针实现原理模拟，通过抓包分析手机mac收据是如何被获取到的。

首先准备一张可支持被动监测模式的网卡（Monitor模式），因为一般家用路由器网卡运行在AP模式（master）下，无法支持被动监测周围信道数据帧的功能，所以此次实验使用的是Ralink的RT5370 2.4G频段。

[![](https://p3.ssl.qhimg.com/t013dd1d9114a7cc7d7.jpg)](https://p3.ssl.qhimg.com/t013dd1d9114a7cc7d7.jpg)

图2

将网卡接口设置成Monitor被动监测模式

[![](https://p1.ssl.qhimg.com/t0165e82763a9e7cb90.jpg)](https://p1.ssl.qhimg.com/t0165e82763a9e7cb90.jpg)

图3

ifconfig查看网卡的接口状态时出现一串00-00则表示网卡当前处在Monitor模式，因为此网卡在up状态下不支持网卡工作模式的切换，但部分其它型号网卡可支持模式切换，故先down 再 up。

默认2.4G，若不设置当前网卡信道，则处于1信道，也可修改为6信道。（1、6、11是互不干扰信道，也是主流WiFi所处信道。）

[![](https://p3.ssl.qhimg.com/t013df46060a980cf62.png)](https://p3.ssl.qhimg.com/t013df46060a980cf62.png)

图4

然后使用tcpdump工具，指定接口被动监测周围数据包。

[![](https://p0.ssl.qhimg.com/t016658fd99642b8379.jpg)](https://p0.ssl.qhimg.com/t016658fd99642b8379.jpg)

图5

上图中标红圈的为WiFi热点名称的广播数据包，打钩的是无线终端设备的mac地址。

也可将被动监测模式下网卡的数据包抓取通过wireshark进行分析。

[![](https://p4.ssl.qhimg.com/t01597db5e732a93278.png)](https://p4.ssl.qhimg.com/t01597db5e732a93278.png)

图6

Probe Request协议类型帧即手机探测帧，包含自身mac；beacon帧是WiFi热点广播的信标帧（通过此beacon帧方可在打开手机WiFi界面时显示出当前周围环境的WiFi名称）；Probe Response是WiFi热点响应手机的回复帧。

无论WiFi是否处于连接状态均通过mac进行交互，WiFi探针设备就是在监测模式下被动采集周围的所有数据帧，达到收集用户mac的目的。



## 四、如何避免WiFi信息被窃取？

1.不随意安装非正规商家应用App、及各类广告插件App，使用正规合法App是保护个人信息的第一步；<br>
2.长时间不使用WiFi可关闭网络自动连接，仔细辨别免费WiFi信号，不随意连接公共WiFi，设置家庭网络的WiFi账号密码并定期更换。
