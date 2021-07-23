> 原文链接: https://www.anquanke.com//post/id/84366 


# VSRC连载系列之（2）VPN真的安全吗？（记一次EzVPN的测试）


                                阅读量   
                                **89199**
                            
                        |
                        
                                                                                    



**导读：**

继上周机房排错后，A同学又接到公司需求：总部希望有一个更加灵活的上网环境，希望SOHO员工能便捷的接入公司资源，且出于安全考虑，所有数据必须经过严格的加密传输。

于是A同学便想到了EzVPN，EzVPN采用中心站点管理模式，通过动态的分发策略，从而降低远程访问VPN部署的复杂度，在数据加密安全传输的同时还能增加网络的扩展性和灵活性。

那么，这个方案是否可行呢？

**一、简介**

Ezvpn的好处显而易见就是Eazy啦，Cisco设计之初的核心思想便是将配置集中式管理，集中在Server端，从而简化Client端的操作，Ezvpn推出之际广受欢迎，但随着时间的推移，问题也逐渐暴露了出来。  

**（一）、EzVPN在第 1 阶段有2种认证方式：**

**1、数字证书认证（ rsa-sig ）**

使用数字证书认证的EzVPN 第一阶段使用标准的6个数据包交换的主模式

**2、预共享秘钥（pre shared）**

组名+密码：好处是可以为一个公司内的不同部门配置不同的组，并把VPN的相关策略与组进行关联，如部门1用户分配地址池1，部门2分配地址池2

**（二）、EzVPN 的IKE协商有以下三个阶段：**

**1、第一阶段：group2 + key **

一般推荐配置：

Pre-share +DH Group2 +MD5+DES / Pre-share+ DH Group2 +SHA+3DES

**2、第二阶段：XAUTH &amp; MODE-CFG**

XAUTH用户名+密码- Extended Authentication 扩展认证 ，弥补主模式安全性上的问题，MODE-CFG为客户推送VPN策略

**3、第三阶段：快速模式**

快速模式3个包（和普通VPN一样）

注意EzVPN不支持AH封装

一般推荐配置：esp-des esp-md5-hmac / esp-3des esp-md5-hmac

**二、以下为基于EzVPN的Feature测试**

**1、测试：地址获取情况查看：**

[![](https://p5.ssl.qhimg.com/t012175a89cd6b801f6.webp)](https://p5.ssl.qhimg.com/t012175a89cd6b801f6.webp)

**2、测试：查看客户是否存在PAT**

[![](https://p1.ssl.qhimg.com/t011dab9f722f85fe7e.webp)](https://p1.ssl.qhimg.com/t011dab9f722f85fe7e.webp)

[![](https://p2.ssl.qhimg.com/t01c44962260e427d09.webp)](https://p2.ssl.qhimg.com/t01c44962260e427d09.webp)

[![](https://p0.ssl.qhimg.com/t01bb25ef1f71a40b5e.webp)](https://p0.ssl.qhimg.com/t01bb25ef1f71a40b5e.webp)

结论：存在PAT

**3、测试：客户身后网络能否访问互联网**

[![](https://p1.ssl.qhimg.com/t013355dbff21172f8a.webp)](https://p1.ssl.qhimg.com/t013355dbff21172f8a.webp)

 <br>

明显无法访问，这是因为再没有启用隧道分割技术的EzVPN客户模式下，内部网路是无法访问互联网的，属正常现象。

**3.1、 Internet启动debug测试ICMP数据包**

[![](https://p5.ssl.qhimg.com/t01f3b4a410a86325d4.webp)](https://p5.ssl.qhimg.com/t01f3b4a410a86325d4.webp)

**4、测试：中心站点是否可以主动发起访问客户网络**

[![](https://p0.ssl.qhimg.com/t01ff3308f3e6d43443.webp)](https://p0.ssl.qhimg.com/t01ff3308f3e6d43443.webp)

[![](https://p4.ssl.qhimg.com/t01d8be1180c2bd2454.webp)](https://p4.ssl.qhimg.com/t01d8be1180c2bd2454.webp)

结论：客户可以访问中心站点，但是中心站点却无法访问客户网络，因为PAT隐藏了这个网络

**5、客户模式加上隧道分割**

crypto isakmp client configuration group

acl split

ip access-list extended split 

permit ip 10.1.1.0 0.0.0.255 any

**6、在客户端清除EzVPN连接**

Client#clear crypto ipsec client ezvpn 

*April  1 01:12:10.659: %CRYPTO-6-EZVPN_CONNECTION_DOWN: (Client)  User=ipsecuser  Group=ipsecgroup  Client_public_addr=202.100.1.1  Server_public_addr=61.128.1.1  Assigned_client_addr=123.1.1.101  

*April   1 01:12:12.915: %LINK-5-CHANGED: Interface Loopback10000, changed state to administratively down

*April   1 01:12:13.915: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback10000, changed state to down

*April   1 01:12:14.879: %CRYPTO-6-EZVPN_CONNECTION_UP: (Client)  User=ipsecuser  Group=ipsecgroup  Client_public_addr=202.100.1.1  Server_public_addr=61.128.1.1  Assigned_client_addr=123.1.1.102  

*April   1 01:12:16.035: %LINK-3-UPDOWN: Interface Loopback10000, changed state to up

*April   1 01:12:17.035: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback10000, changed state to up

**7、测试：查看客户端EzVPN状态**

Branch#show crypto ipsec client ezvpn 

Easy VPN Remote Phase: 6

Tunnel name : EzVPN

Inside interface list: FastEthernet0/0

Outside interface: FastEthernet0/1 

Current State: IPSEC_ACTIVE

Last Event: MTU_CHANGED

Address: 123.1.1.102 

Mask: 255.255.255.255

Save Password: Allowed

Split Tunnel List: 1  

       Address    : 10.1.1.0

       Mask       : 255.255.255.0

       Protocol   : 0x0

       Source Port: 0

       Dest Port  : 0

Current EzVPN Peer: 61.128.1.1

**8、测试：查看客户端是否存在PAT**

[![](https://p0.ssl.qhimg.com/t01424ae58154f09b09.webp)](https://p0.ssl.qhimg.com/t01424ae58154f09b09.webp)

Branch#show ip nat statistics 

Total active translations: 0 (0 static, 0 dynamic; 0 extended)

Outside interfaces:

  FastEthernet0/1

Inside interfaces: 

  FastEthernet0/0

Hits: 330  Misses: 0

CEF Translated packets: 330, CEF Punted packets: 0

Expired translations: 8

Dynamic mappings:

— Inside Source

[Id: 4] access-list internet-list interface FastEthernet0/1 refcount 0  

第一个用户上网的PAT转换到外部接口fa 0/1地址

[Id: 3] access-list enterprise-list pool EzVPN refcount 0

第二个访问中心内部网络的PAT 转换到地址池地址123.1.1.102

 pool EzVPN: netmask 255.255.255.0

        start 123.1.1.102 end 123.1.1.102

        type generic, total addresses 1, allocated 0 (0%), misses 0

Appl doors: 0

Normal doors: 0

Queued Packets: 0



**9、测试：客户身后内部网络能否访问互联网**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d1b08051992d1d76.webp)

[![](https://p3.ssl.qhimg.com/t01781b308db80517a3.webp)](https://p3.ssl.qhimg.com/t01781b308db80517a3.webp)

 <br>

 由于在客户端Branch上发现了id:4 PAT 所以在Private上使用ping和telnet能够成功的访问互联网路由器Internet 

**10、测试：中心站点能否主动发起连接访问客户身后网络**

[![](https://p3.ssl.qhimg.com/t0131c0b0ff21454161.png)](https://p3.ssl.qhimg.com/t0131c0b0ff21454161.png)

中心站点无法主动发起访问客户身后网络，因为PAT隐藏了这个网络

结论：

经测试总结，发现EzVPN存在以下诸多硬伤：

1、客户端软件兼容性低

2、设备基本配置复杂

3、操作界面缺乏人性化

基于以上分析，A同学终于决定放弃EzVPN….

他是否会选择功能类似的SSL VPN呢？

下一个VPN又会存在哪些问题呢？

**（未完待续….）**
