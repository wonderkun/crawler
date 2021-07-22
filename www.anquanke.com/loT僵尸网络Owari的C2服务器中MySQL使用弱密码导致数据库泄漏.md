> 原文链接: https://www.anquanke.com//post/id/147108 


# loT僵尸网络Owari的C2服务器中MySQL使用弱密码导致数据库泄漏


                                阅读量   
                                **112109**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者NewSky Security，文章来源：blog.newskysecurity.com
                                <br>原文地址：[https://blog.newskysecurity.com/hacker-fail-iot-botnet-command-and-control-server-accessible-via-default-credentials-2ea7cab36f72](https://blog.newskysecurity.com/hacker-fail-iot-botnet-command-and-control-server-accessible-via-default-credentials-2ea7cab36f72)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p2.ssl.qhimg.com/t01fdb523e91f88f960.jpg)](https://p2.ssl.qhimg.com/t01fdb523e91f88f960.jpg)



## 前言

具有史诗般的讽刺意味，我们注意到loT僵尸网络变体Owari依靠默认/弱密码入侵物联网设备，它本身在其命令和控制服务器中使用默认密码，允许对其服务器数据库进行读/写访问。



## Owari的MySQL数据库

Mirai僵尸网络旨在为命令和控制设置一个MySQL服务器，其中包含三个表，即users, history, 和 whitelist。虽然物联网已经进化，而且它们中的许多具有不同的攻击向量，但是它们中的大多数仍然保留了这个久经考验的MySQL服务器结构，Owari也不例外。

我们观察到很少有IP使用默认密码攻击我们的蜜罐，比如执行 /bin/busybox OWARI post successful login等命令。其中有一种情况，试图在80(.)211(.)232(.)43上进行POST下载。

当我们研究IP时，我们观察到MySQL数据库的默认端口3306是打开的。

[![](https://p3.ssl.qhimg.com/t0144c56710d3b952e2.png)](https://p3.ssl.qhimg.com/t0144c56710d3b952e2.png)

我们试图对这个IP进行更多的调查。令我们惊讶的是，它使用的是已知的最薄弱的密码之一连接到攻击者的服务器上。

```
Username: root
Password: root
```



## 调查数据库

User表包含将控制僵尸网络的各种用户的登录密码。他们中的一些人可能是僵尸网络的创建者，也可能有些人只是僵尸网络的客户，也就是黑盒用户，他们为发动DDoS攻击支付了一笔钱。除了密码之外，还可以观察持续时间限制，例如用户执行DDoS的时间、攻击的最大可用机器数(-1表示整个僵尸网络部队都可用)和冷却时间(两个攻击命令之间的时间间隔)。

在特定的Owari案例中，我们观察到一个用户的持续时间限制为3600秒，允许的bot使用设置为-1(最大)。需要指出的是，所有这些僵尸网络用户的密码也很弱。

[![](https://p3.ssl.qhimg.com/t01e1ebc692c5358015.png)](https://p3.ssl.qhimg.com/t01e1ebc692c5358015.png)

在history表中，我们可以看到对各种IP进行的DDoS攻击。这些IP中很少有与物联网设备相关的，这使我们猜测攻击者可能试图攻击他的僵尸网络运营商竞争对手。

[![](https://p2.ssl.qhimg.com/t018cb2a5ff81ea31c7.png)](https://p2.ssl.qhimg.com/t018cb2a5ff81ea31c7.png)

在下一张表中，应该有“不要攻击这些IP”信息的白名单是空的，这意味着机器人不做任何区分，并攻击它所能攻击的每一个设备。

[![](https://p1.ssl.qhimg.com/t010721976cd1b044ba.png)](https://p1.ssl.qhimg.com/t010721976cd1b044ba.png)

这个IP不是一个独立的情况，它的数据库通过弱密码公开。另一个攻击IP(80.211.45.89)的MySQL数据库可通过“root：root”密码访问。



## 了解收入模式

由于一些Owari变体在暗网的论坛中泄露，很难确定参与这些特定攻击的人。然而，为了更多地了解这个用户数据库的工作，我们决定与一个名为“疤面”的已知Owari运营商交谈，他对Owari 僵尸网络的攻击时间、冷却时间和相关价格有以下说明。

> <p>“对于60美元/月，我通常提供大约600秒的启动时间，这与其他人提供的相比是低的。然而，这是我唯一可以保证一个稳定的BOT计数的方法。我无法允许10多人同时进行每次1800秒的攻击。通常在我的位置上没有冷却时间。如果我决定给予冷却时间，大约需要60秒或更少。每月60美元并不算多，但当你每月得到10-15名顾客时，就足以支付我大部分的虚拟费用了。”<br>
-Scarface</p>
 

## 修复

可以假定，一旦他们拥有了对MySQL数据库的写访问权限，就可以通过删除内容来破坏僵尸网络。遗憾的是，对于大多数loT僵尸网络来说，这并不是那么简单，因为这些与网卡相关的IP已经有了很低的保质期(平均一周)。僵尸网络运营商意识到，由于网络流量不好，他们的IP将很快被标记出来。因此，为了躲过扫描，他们经常自己改变攻击IP。博客中提到的两个IP都已经脱机了。
