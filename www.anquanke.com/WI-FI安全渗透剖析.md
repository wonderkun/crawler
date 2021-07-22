> 原文链接: https://www.anquanke.com//post/id/211498 


# WI-FI安全渗透剖析


                                阅读量   
                                **210105**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t016b4b2911021ff4b6.jpg)](https://p0.ssl.qhimg.com/t016b4b2911021ff4b6.jpg)



## 前记

在我们的生活当中，WIFI随处可见，几乎是家家可见的路由器，已经成为了我们生活中不可分割的一部分。但是俗话说得好，有网络的地方就会有安全问题，那么本篇文章作者将对WIFI安全进行深入简出的讲解，旨在从渗透者的角度分析常见的WIFI攻击，分析攻击过程。那么我们现在开始吧！



## 准备工作

首先在测试之前，我们需要把环境进行配置一下。首先我们需要一块可开启监听模式的无线网卡，这样的网卡在淘宝大概是几十块钱。

[![](https://p1.ssl.qhimg.com/t011e4a7fcd869964b1.png)](https://p1.ssl.qhimg.com/t011e4a7fcd869964b1.png)

可以选择的种类还是非常多的，这里就不再赘述了。但是需要注意的是挑选无线网卡频段的问题，我购买的这款无线网卡只能监听2.4G的网络，但是现在家用的路由器基本上都具有两个频段，所以当我们进行比如deauth等攻击时，当2.4G频段信号连接异常时会自动跳转到5G频段导致无法抓取数据包。

这里讲解一下2.4GHz和5GHz的主要区别:<br>
两者总的来说各有优异，2.4GHz的主要优点：信号强、覆盖范围远、衰减小。缺点：带宽窄、速度慢、干扰较大。2.4GHz频段共有14个信道，在中国可以使用1-13信道。5GHz的优点主要是：带宽较宽、速度较快，干扰较少。缺点:覆盖范围小，衰减大，信号小。总的来说就是与2.4Ghz的优点相反。5G频段共有约200个信道，他的干扰可以说非常小。



## 无线网卡配置

在渗透之前需要配置一下我们的网卡，在将网卡连接至虚拟机中后，输入iwconfig命令查看是否识别网卡。

[![](https://p5.ssl.qhimg.com/t012b1d323777e2eec1.png)](https://p5.ssl.qhimg.com/t012b1d323777e2eec1.png)

这里的wlan0就是我们的无线网卡，使用命令开启监听模式:

`airmon start wlan0`

如下图即说明已经开启监听模式

[![](https://p4.ssl.qhimg.com/t01734705bad149ec55.png)](https://p4.ssl.qhimg.com/t01734705bad149ec55.png)

注意事项:为什么要开启监听模式呢？因为默认情况下网卡只会接收发送给自己的数据帧，而丢弃其他数据帧，也就是被管理状态。而开启监听模式后则会监听所有无线通信，从而实现我们的渗透需求。

在开启监听模式后，我们使用airodump-ng进行扫描发现无线网络。

[![](https://p0.ssl.qhimg.com/t0170542e1598e6111c.png)](https://p0.ssl.qhimg.com/t0170542e1598e6111c.png)

为了保护别人的隐私，仅显示需要测试的路由器信息。

BSSID：wifi的mac地址。<br>
PWR：网卡报告的信号水平，数值越低信号越好，忽略前面的负号。<br>
Beacons：无线发出的通告编号<br>
CH：信道<br>
MB：无线所支持的最大速率<br>
ENC：使用的加密算法体系，OPN表示无加密<br>
CIPHER：检测到的加密算法<br>
AUTH：使用的认证协议。<br>
ESSID：wifi名称<br>
STATION：客户端的MAC地址，包括连上的和想要搜索无线来连接的客户端。如果客户端没有连接上，就在BSSID下显示“notassociated”。<br>
Rate：表示传输率。<br>
Lost：在过去10秒钟内丢失的数据分组<br>
Frames：客户端发送的数据分组数量。<br>
Probe：被连接的wifi名



## Deauth攻击

取消验证洪水攻击，通常被简称为Deauth攻击，是无线网络拒绝服务攻击的一种形式，在客户端点击断开连接时会向路由器发送断开帧，而Deauth攻击就是模拟这样一个环节从而断开数据包。

下面这条命令会攻击所有信道的WI-FI信号。<br>`mdk3 wlan0mon d`

在攻击的过程中并没有任何回显，但是攻击正在进行中。

[![](https://p0.ssl.qhimg.com/t0190f1c1cd98a10f4c.png)](https://p0.ssl.qhimg.com/t0190f1c1cd98a10f4c.png)

效果如下

[![](https://p2.ssl.qhimg.com/t011b49f2f655d106dd.jpg)](https://p2.ssl.qhimg.com/t011b49f2f655d106dd.jpg)

我们发现WIFI连接被断开了，再次尝试连接会显示密码错误。

aireplay-ng工具同样可以进行这一操作。<br>
-0为指定攻击方式为取消身份验证攻击，0是循环发送，指定其他数字则为发送离线包的数量，-a指定目标路由器mac地址。

`aireplay-ng -0 0 -a mac wlan0mon`

开始攻击后会不断向目标发送离线包。

[![](https://p5.ssl.qhimg.com/t011902a895abc01ebf.png)](https://p5.ssl.qhimg.com/t011902a895abc01ebf.png)

无论是mdk3还是aireplay-ng他们的效果其实差不多。<br>
目前mdk3的维护已经停止，而国内有团队已经开发出支持5GHz频段的mdk4大家可以注意一下。



## Auth攻击

验证洪水攻击,攻击者将向AP发送大量伪造的身份验证请求帧(伪造的身份验证服务和状态代码)，当收到大量伪造的身份验证请求超过所能承受的能力时，AP将断开其它无线服务连接。

`mdk3 wlan0mon a -a 50:2B:73:6A:18:81`

使用上述命令后会发送大量验证信息给目标AP，不久便会断开其他无线连接，继续攻击路由器会卡死崩溃。

目前大部分主流的路由器都是WPA2的，所以上面的攻击几乎涵盖了目前所有家用路由器，而最新推出的WPA3的安全标准则缓解了如Deauth攻击等。但是目前市面上具有WPA3的路由器价格相比还是有点贵的。



## MAC白名单绕过

在学校中，大家想必都有体会过校园网，对于老师们可以使用校园网而普通用户哪怕知道了密码也无法登录正是因为网管那里过滤了我们设备的MAC地址。那么有没有办法能绕过呢？其实也就只是多出了一步而已。在我们使用airodump-ng扫描时我们可以看到下面有已经连接的客户端。

[![](https://p1.ssl.qhimg.com/t01fae8457d38be1cb0.png)](https://p1.ssl.qhimg.com/t01fae8457d38be1cb0.png)

在STATION这一项中，我们可以看到已经连接的客户端。这里还要从MAC地址随机化说起，我们都知道MAC地址是终端设备网络接口的唯一编码和标识符，在生产分配时无法修改，所以经常会设备跟踪。但是随之出现的随机化这一机制打破了这种现状。在windows10中，是全随机化，也就是说在搜索附近无线网络时是随机的MAC地址，连接后同样是随机的。但是安卓却不是，他是半随机化，也就是搜索无线网时是随机化的，但是连接后不是，这也就让我们有了可乘之机。上图中STATION这一项就是连接的客户端。

我们可以通过修改自己网卡的MAC地址为他们的地址就可以绕过MAC白名单了。<br>
命令如下:

`macchanger -m mac wkan0`

需要注意的是这样修改的话两个设备同时在线，会导致MAC冲突。



## 渗透思路精讲

上面我们简单的讲解了两种常见的无线攻击方式，那么小伙伴一定会问有没有便携的设备呢？

[![](https://p5.ssl.qhimg.com/t011d3052758e72e414.jpg)](https://p5.ssl.qhimg.com/t011d3052758e72e414.jpg)

相信有物联网经验的小伙伴一定能看出这是一块esp8266的板子，我们通过烧录wifi杀手固件就可以随时随地的进行无线攻击了，界面如下图。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01464b0dad5849898e.jpg)

是不是很帅呢？

攻击方式当然不止上面几种，包括无线钓鱼、密码爆破，无人机攻击等。<br>
说起无人机，本来本文还想给大家演示一下无人机的攻击过程分析，但是奈何我的无人机坏掉了所以就没有办法了。但是大体攻击原理也是通过kismet等软件检测无人机信号，进行断开连接，也可以使用射频工具进行GPS欺骗。

这里大家也需要警惕外面的陌生网络，在钓鱼网络中，攻击者甚至可以改变的访问地址，比如我们正常访问百度的域名，域名看起来是没有什么问题的，但是当你通过这个路由器进行访问时，这个域名已经指向的并不是原本的网址了，这样恶意的DNS服务器在实战时几乎是百发百中。

对于上面讲到的auth泛洪攻击，目前部分路由器固件内自带的防火墙能起到很好的防范了，如下图。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019e201bd36f4c9ec2.jpg)

这样的防火墙可以很好防护ddos却对deauth攻击效果并不显著，所以当WPA3标准的路由器普及这一问题大概也就会成为过去吧！



## 钓鱼攻击WIFI Pineapple

关于钓鱼攻击，大家可以看一下我的一篇关于菠萝派WIFI Pineapple的文章。

`https://blog.csdn.net/qq_42804789/article/details/105215524`

钓鱼攻击目前来讲防御的方法并不特别有效，主要还是需要靠大家的自觉。尽量在陌生网络中不要输入自己的账号密码。因为如果你看过上文不难发现，攻击者完全可以获取到你访问的所有信息。



## 后记

这次的文章就讲这么多，因为相关法规，并不能进行更多的攻击过程演示，所以我就挑了几个比较经典的攻击方法进行讲解，希望大家能够有所收获。如果大家对这方面感兴趣，可以找我讨论，欢迎大家提出问题或建议！

祝大家心想事成，生活美满！
