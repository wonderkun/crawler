> 原文链接: https://www.anquanke.com//post/id/86601 


# 【技术分享】浅析无线Wifi-Honeypot思路


                                阅读量   
                                **159755**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01d8ed4bd9e025360d.jpg)](https://p1.ssl.qhimg.com/t01d8ed4bd9e025360d.jpg)



作者：[icecolor](http://bobao.360.cn/member/contribute?uid=775238387)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

在网络安全里面无论是IPS，IDS都跟蜜罐有着紧密联系，蜜罐可以算是防火墙中的一个重要分支。

蜜罐最基本的作用是来捕获攻击者的行为并且进行追踪取证和反入侵，首先你要有一个脆弱点来诱惑攻击者。

我之前看过一个老外最原始的蜜罐。其实那并不是一个蜜罐，只能说是一个迷惑攻击者的方法。他建立很多与真实SSID相同的无用接入点，来进行干扰，下面是我复现的效果。

[![](https://p4.ssl.qhimg.com/t01abefcb2ee058c6a3.png)](https://p4.ssl.qhimg.com/t01abefcb2ee058c6a3.png)

[![](https://p3.ssl.qhimg.com/t01ee039520f4ad21bd.png)](https://p3.ssl.qhimg.com/t01ee039520f4ad21bd.png)

这样虽说可以在某种程度上短暂的让攻击者找不到目标。但却不是一个真正意义上的蜜罐。



**关于蜜罐的功能与设计**

****

众所周知，Fake AP的攻击方式在无线攻击中算的上威胁最大的之一了。那我们可以变攻为防，自己创建一个Fake AP，来诱捕攻击者.

[![](https://p3.ssl.qhimg.com/t01e1cb255f5e4fe8bf.png)](https://p3.ssl.qhimg.com/t01e1cb255f5e4fe8bf.png)

关于蜜罐服务器与热点的配置，它必须要具备以下功能：

关于服务器与监控信息：

1.数据截获：对捕获到的攻击者信息进行数据分析、取证、定位。

首先察觉到有攻击者中招时要记录其信息。

例：

确定其MAC地址与内网地址：

[![](https://p3.ssl.qhimg.com/t01a1fcb82c06c7b5d7.png)](https://p3.ssl.qhimg.com/t01a1fcb82c06c7b5d7.png)

2.对数据截获和保存，可以把每次有蜜罐告警的数据包全部保存下来，手工分析进行取证。

例：

入侵者QQ号码：

[![](https://p3.ssl.qhimg.com/t01805e7451a828e304.png)](https://p3.ssl.qhimg.com/t01805e7451a828e304.png)

入侵者连接设备（网卡或终端）名称：

 [![](https://p2.ssl.qhimg.com/t01f2ff8edecc7b3d3c.png)](https://p2.ssl.qhimg.com/t01f2ff8edecc7b3d3c.png)

……….以及其他有必要提取的数据

2.服务器要配置一些内网的扫描工具（如Nmap）与劫持工具，方便反追踪与取证。

例：

 [![](https://p0.ssl.qhimg.com/t01917dfac07ecf007b.png)](https://p0.ssl.qhimg.com/t01917dfac07ecf007b.png)

3.要对攻击者进行监控，如DNS、Url，photo之类.

[![](https://p4.ssl.qhimg.com/t01919a21a8ba511293.png)](https://p4.ssl.qhimg.com/t01919a21a8ba511293.png)



** 关于热点：**

****

1.可以选择隐藏真实的热点，并且真实热点隐藏，SSID也不要用跟公司或者很敏感的字符。而蜜罐系统的热点一定要敏感。

例：

公司为Goole.那AP热点名称可用任何与Google无关的SSID，就算找到隐藏SSID，攻击者也难以相信。而蜜罐SSID为Google-office。

2.蜜罐系统的加密方式不要选择最弱加密和无加密，加密要正常，密码可以稍弱。为了防止蜜罐暴露。若要启用加密热点，需用Hostapd。

3.蜜罐AP部署不要单一一个，要多建立几个，部署整个要保护的环境。

 [![](https://p2.ssl.qhimg.com/t01ce1855f90ba8fe5b.png)](https://p2.ssl.qhimg.com/t01ce1855f90ba8fe5b.png)

4.配合内网蜜罐使用将会有意想不到的效果，让攻击者陷网更深

<br>

**基于Probe Req的新思路**

玩过wifi菠萝的同学肯定知道karma了。Karma里面有个很厉害的功能就是能伪造你之前客户端连接过的wifi。

它的原理是基于设备发出的Probe req请求。

可以在服务器中部署嗅探脚本，客户端的Probe Req将会成为收集效信息的一部分 。   



[![](https://p2.ssl.qhimg.com/t01438f8da410c5c7ae.png)](https://p2.ssl.qhimg.com/t01438f8da410c5c7ae.png)

  

[![](https://p1.ssl.qhimg.com/t011ddf624c4379c33b.png)](https://p1.ssl.qhimg.com/t011ddf624c4379c33b.png)

在今天嗅探的时候，也发现了一个有意思的东西，我在嗅探中发现了有个终端曾请求SSID：“GreenHotel”这个热点。这是个格林豪泰的酒店热点。换个思路来说，你可以用此方法来检查你女（男）朋……….

如果你对的蜜罐要求不高的话，wifipineapple就可以完成一些要求，大的比较浪费，小的比较实惠。固件升级到最新就可以了，开启Karm+Dwall功能。

 [![](https://p3.ssl.qhimg.com/t01e195ee1f2f2590a2.png)](https://p3.ssl.qhimg.com/t01e195ee1f2f2590a2.png)

以上只是提供了一个简单思路，后期应该会实体化加入新功能，这种蜜罐可以对Wardriving和非法蹭网者吃点亏，可能就是没有定位功能，其实定位功能也蛮简单，成本也比不太高。方便的可以用这个菠萝，想自定义功能的可以用树莓派玩玩.

开了个无线安全的小博客:[www.wiattack.net](http://www.wiattack.net)。里面文章很少，正在添加，无特殊情况都是原创。希望多多交流。
