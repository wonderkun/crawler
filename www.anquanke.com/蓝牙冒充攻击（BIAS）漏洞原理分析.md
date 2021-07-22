> 原文链接: https://www.anquanke.com//post/id/206624 


# 蓝牙冒充攻击（BIAS）漏洞原理分析


                                阅读量   
                                **185970**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01fece8e756ae2d575.jpg)](https://p2.ssl.qhimg.com/t01fece8e756ae2d575.jpg)

> **sourcell.xu@海特实验室**

Boffins 披露了一个被称为 BIAS 的蓝牙安全漏洞 (CVE-2020-10135)，攻击者可利用该漏洞欺骗远程配对设备。海特实验室研究员针对于该漏洞进行了详细分析。

在经典蓝牙（Bluetooth Classic）的世界中，link key 是安全的基石。根据蓝牙核心规范 5.2，我们有三种类型的 link key，它们分别为：
1. combination key
1. temporary key
1. initialization key
本文中，我们关注的是 combination key。该 link key 由两个已经配对的 BR/EDR 设备共享。它主要有如下两个作用：

1、已配对设备再次连接对方时，会使用 link key 鉴权：

[![](https://p3.ssl.qhimg.com/dm/1024_673_/t016f82b78ff70789d3.png)](https://p3.ssl.qhimg.com/dm/1024_673_/t016f82b78ff70789d3.png)

2、鉴权通过后，连接双方可以使用 link key 导出用于加密后续通信数据的 encryption key。

[![](https://p5.ssl.qhimg.com/dm/1024_411_/t011f61e3662c44cf86.png)](https://p5.ssl.qhimg.com/dm/1024_411_/t011f61e3662c44cf86.png)

本文分析的 BIAS (Bluetooth Impersonation AttackS) 漏洞影响了前者，而后者也曝出过 KNOB (Key Negotiation Of Bluetooth) 漏洞。概括的说，BIAS 利用如下三点绕过了 BR/EDR 设备的鉴权机制：
1. Legacy authentication 允许单边鉴权
1. Secure authentication 可协商降级为 legacy authentication
1. 经典蓝牙允许 master 与 slave 角色转换
下面将分别分析这三个弱点。



## Legacy Authenticationd 单边鉴权

Legacy authentication 定义了两个角色 verifier 与 claimant。鉴权的具体流程如下：

[![](https://p3.ssl.qhimg.com/dm/1024_406_/t01556a6b18a31d13fe.png)](https://p3.ssl.qhimg.com/dm/1024_406_/t01556a6b18a31d13fe.png)

首先 verifier 把一个随机数 RAND 发送给 claimant，向它发起挑战。之后 verifier 与 claimant 会各自在本地使用固定的算法 `E1` 计算 SRES (Signed RESponse)：

`SRES ``=`` E1``(``link_key``,`` claimant_bd_addr``,`` RAND``)`

同时 claimant 会将计算得到的 SRES 回传给 verifier。Verifier 则比较该 SRES 与自己计算的 SRES’ 是否相同。如果相同则鉴权通过。

可见 legacy authentication 并未强制要求 claimant 反过来验证 verifier 的身份。那么攻击者可以伪装成 verifier，在不知道 link key 的情况下，略过 SRES’ 与 SRES 的比对，直接让 claimant 通过鉴权。



## Secure Authentication 降级

在 2020 年，绝大多数 BD/EDR 设备都支持 secure authentication，且默认启用。具体的鉴权流程如下：

[![](https://p3.ssl.qhimg.com/dm/1024_350_/t014a71294946c51044.png)](https://p3.ssl.qhimg.com/dm/1024_350_/t014a71294946c51044.png)

从上图可知这种鉴权方法是双向的，因此 legacy Authenticationd 单边鉴权的弱点不能被直接利用。不过，为了兼容较老的仅支持 legacy authentication 的设备，经典蓝牙允许设备间协商鉴权方法。如果一方设备仅支持 legacy authentication，那么 secure authentication 将不被启用。

具体的，当两个设备的 controller 与 host 都支持 secure connection 特征时，secure authentication 才会被启用。于是攻击者可以伪造不支持 secure connection 特征的设备，即可降级 secure Authentication 为 legacy authentication，从而继续利用旧鉴权方法单边认证的弱点：

[![](https://p0.ssl.qhimg.com/dm/1024_579_/t01fc5babde0c740e87.png)](https://p0.ssl.qhimg.com/dm/1024_579_/t01fc5babde0c740e87.png)



## Master 与 Slave 角色转换

攻击者在利用 legacy authentication 的单边鉴权弱点攻击目标时，可能并不知道目标的上层应用要求 master 鉴权 slave 还是 slave 鉴权 master，即不确定自己应该扮演 slave 还是 master。

不过，经典蓝牙允许 master 与 slave 的角色转换，具体流程如下：

[![](https://p4.ssl.qhimg.com/t011218daf02943f677.png)](https://p4.ssl.qhimg.com/t011218daf02943f677.png)

这样攻击者就可以灵活切换自己的角色，让自己成为 verifier，始终掌握主动权。



## 总结

需要明确的是，虽然 BIAS 可以绕过鉴权，但它仍不能获取 link key，即无法在鉴权后与目标进行加密数据的交互。不过该限制正好可以被 KNOB 突破，所以 BIAS + KNOB 这套组合拳威力巨大，动摇了经典蓝牙安全的根基。

另外 BIAS 攻击的前提是获取已经与目标设备配对的其他设备地址，这个地址用于发起连接后，跳过配对过程，直接进入存在漏洞的鉴权过程。



## References
1. BIAS
1. BLUETOOTH CORE SPECIFICATION Version 5.2 | Vol 2, Part F page 723, 4.1 AUTHENTICATION REQUESTED
1. BLUETOOTH CORE SPECIFICATION Version 5.2 | Vol 2, Part H page 972, 5 AUTHENTICATION
1. BLUETOOTH CORE SPECIFICATION Version 5.2 | Vol 2, Part H page 982, 6.4 E3-KEY GENERATION FUNCTION FOR ENCRYPTION