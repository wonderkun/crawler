> 原文链接: https://www.anquanke.com//post/id/197750 


# 车联网安全系列——特斯拉iBeacon隐私泄露


                                阅读量   
                                **953698**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01db791f76c2e72936.jpg)](https://p2.ssl.qhimg.com/t01db791f76c2e72936.jpg)



## 0x00 前言

大家好, 我是来自银基车联网安全实验室的 KEVIN2600. 今天我想跟大家分享下研究Tesla过程中的一个有趣案例. 希望抛砖引玉, 一起为中国车联网安全做出贡献.

Tesla电动汽车通过颠覆性的创新能力, 使其迅速成为新能源汽车的领导者. 而作为毫无根基的后来者, Tesla电动汽车将安全性、智能化、可靠性完美融为一体. 甚至公司创始人Elon Musk自信地称其为 “A sophisticated computer on wheels”.

当然作为业界的翘楚, 自然会吸引很多人的兴趣, 其中也包括黑客群体. 在刚刚落幕的德国黑客大会36C3上, 安全研究员 Martin Herfur就对 Tesla Model 3提出了隐私泄露隐患的质疑.

Martin研究发现Tesla Model 3 通过蓝牙频道不断对外明文广播一组特殊的ID号. Tesla将这组ID号作为实现手机APP门禁系统的重要参数. 然而用户并没有权限改变或者关闭这组特殊ID号, 这就给有心人士造成了可趁之机. 只要通过扫描捕捉这组ID号, 就可实现对Tesla Model3车主的跟踪, 从而对车主的个人隐私造成困扰. Martin还特意写了一个测试APP (特斯拉雷达). 并搭建了全球特斯拉监测平台. 感兴趣的读者可以到teslaradar.com去了解更多的信息.

[![](https://p2.ssl.qhimg.com/t013f703b811ea1225f.png)](https://p2.ssl.qhimg.com/t013f703b811ea1225f.png)

个人隐私问题在资讯发达的今天显得尤为突出. 商家在个人隐私保护方面是否足够重视, 也成为人们评价一款产品优秀与否的标准之一. 美国加州立法委员会甚至将其列在了《加州物联网网络安全法案》中. 而各类车联网产品是否存在隐私泄露问题, 也是非常重要的检测环节. 因此当听说了这个Tesla Model 3隐患后, 立刻引起重视并作了深入的研究.

[![](https://p3.ssl.qhimg.com/t0198caa2baebbf1712.jpg)](https://p3.ssl.qhimg.com/t0198caa2baebbf1712.jpg)<br>
(图为研究人员在对Model3蓝牙信号进行跟踪测试)



## 0x01 街头实战测试

在做了大量测试后, 发现Tesla Model 3 确实存在通过广播特殊ID, 造成隐私泄漏的问题. 通过APP特斯拉雷达我们很快就发现了不少Tesla Model 3. 并且成功定位了几辆经常出现在附近小区的车主.

[![](https://p2.ssl.qhimg.com/t015ffd115c8d50c1df.png)](https://p2.ssl.qhimg.com/t015ffd115c8d50c1df.png)

[![](https://p4.ssl.qhimg.com/t01f69564bfa873c71c.png)](https://p4.ssl.qhimg.com/t01f69564bfa873c71c.png)



## 0x02 iBeacon简介

那么究竟这个特殊的ID号是什么呢? 这就需要我们首先了解下什么是iBeacon. 它是最早由苹果公司发明的一项通过蓝牙广播, 专门用于跟物理世界进行交互的技术. 主要应用场景为室内定位等.

[![](https://p4.ssl.qhimg.com/t01e3e04fae6db69855.png)](https://p4.ssl.qhimg.com/t01e3e04fae6db69855.png)

苹果公司同时定义了iBeacon广播的数据格式. 其中包含了UUID, Major, Minor, TX Power 这几个重要参数. 首先UUID 为16字节的字符串,这组字符串主要是用来区分各个不同的厂家. 比如TESLA的UUID 为 (74278bda-b644-4520-8f0c-720eaf059935). 这组UUID可以从逆向特斯拉雷达 APK 文件中找到.

[![](https://p5.ssl.qhimg.com/t013708ef76004ba595.png)](https://p5.ssl.qhimg.com/t013708ef76004ba595.png)

接下来的Major为2字节的字符串, 通常用来定位发送方的区域或类型. 随后的2字节字符串Minor主要用来区域中具体定位. 而TX Power顾名思义则是通过信号强弱来识别与车主的距离. 当然厂家可以根据实际需求重新定义具体用途. 而Tesla Model3 的特殊ID号则在蓝牙设备名字项出现, 如下图中的 S7120a62f34cd8018C.

[![](https://p3.ssl.qhimg.com/t0143e36df62dce7f81.png)](https://p3.ssl.qhimg.com/t0143e36df62dce7f81.png)

这里我们使用专业蓝牙分析仪 Frontline 对Tesla的广播包进行捕捉及分析. 也同样发现了相同的数据串.

[![](https://p5.ssl.qhimg.com/t014625be497c998e91.png)](https://p5.ssl.qhimg.com/t014625be497c998e91.png)

[![](https://p4.ssl.qhimg.com/t016ef67e89f9a3abb6.jpg)](https://p4.ssl.qhimg.com/t016ef67e89f9a3abb6.jpg)



## 0x03 iBeacon数据伪造

这项技术的设计初衷是为了让商家可以更加方便的与客户互动. 然而iBeacon的设计者们似乎没有过多考虑安全隐私的问题. 其通过蓝牙广播明文发送的特性, 让任何人可以通过手机或蓝牙设备对其进行数据捕获与伪造. 如下图所示我们可以轻易通过开源软件创建一个简单的iBeacon的数据包.

[![](https://p0.ssl.qhimg.com/t01061d19cddf3b0c97.png)](https://p0.ssl.qhimg.com/t01061d19cddf3b0c97.png)

熟悉软件无线电的朋友, 也可以选择硬核无线大神JXJ的开源项目 ([https://github.com/JiaoXianjun/BTLE](https://github.com/JiaoXianjun/BTLE)). 在配合HackRF 或 BladeRF 使用. 比如我们可以在短时间内伪造大量iBeacon数据, 对目标设备造成困扰.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019ed712e6e7bde9b5.png)

[![](https://p5.ssl.qhimg.com/t01fae7ccf985aa6e93.png)](https://p5.ssl.qhimg.com/t01fae7ccf985aa6e93.png)



## 0x04 参考文献

[https://www.teslaradar.com/faq/](https://www.teslaradar.com/faq/)<br>[https://github.com/JiaoXianjun/BTLE](https://github.com/JiaoXianjun/BTLE)<br>[http://www.warski.org/blog/2014/01/how-ibeacons-work/](http://www.warski.org/blog/2014/01/how-ibeacons-work/)<br>[https://the-parallax.com/2019/11/14/tesla-radar-model-3-phone-key-ibeacon/](https://the-parallax.com/2019/11/14/tesla-radar-model-3-phone-key-ibeacon/)
