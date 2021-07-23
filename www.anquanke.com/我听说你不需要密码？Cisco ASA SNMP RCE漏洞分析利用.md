> 原文链接: https://www.anquanke.com//post/id/84501 


# 我听说你不需要密码？Cisco ASA SNMP RCE漏洞分析利用


                                阅读量   
                                **135712**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01d1194a6a554d6c37.png)](https://p0.ssl.qhimg.com/t01d1194a6a554d6c37.png)

在这个似乎人人都在致力于HAPPY WEEKEND的年代，有什么办法可以让WEEKEND BE MORE HAPPY呢？复（利）现（用）一个漏洞如何？！    <br>

此前在Twitter看到：

[![](https://p4.ssl.qhimg.com/t01bb7713315b64f021.webp)](https://p4.ssl.qhimg.com/t01bb7713315b64f021.webp)

接着又是

[![](https://p0.ssl.qhimg.com/t0118074cd76f60d1bc.webp)](https://p0.ssl.qhimg.com/t0118074cd76f60d1bc.webp)

似乎很有趣，那就来试试咯。

**免责声明：**

本文中的一切资料仅供参考，并仅限于实验环境，并不构成任何具体的法律或其他问题。

任何人不得以任何形式或通过任何途径将文中内容用作非法途径。

**<br>**

**一、搭建实验环境**

**1.  创建ASA虚拟机**

 

[![](https://p0.ssl.qhimg.com/t011daf2b846f3fa80a.webp)](https://p0.ssl.qhimg.com/t011daf2b846f3fa80a.webp)

为了将SNMP服务器与ASA可以互相通信，这里我们选择host only 模式

[![](https://p4.ssl.qhimg.com/t019f8fbafe68eb20b6.webp)](https://p4.ssl.qhimg.com/t019f8fbafe68eb20b6.webp)

Pipe命名规则需要注意格式

[![](https://p1.ssl.qhimg.com/t01c97f9ac9b0cccca7.webp)](https://p1.ssl.qhimg.com/t01c97f9ac9b0cccca7.webp)

于是打开虚拟机选择第一个镜像进入开始界面

[![](https://p4.ssl.qhimg.com/t0157eff49992fce94e.webp)](https://p4.ssl.qhimg.com/t0157eff49992fce94e.webp)

ASA启动完毕

**2.  配置pipe tcp proxy**

[![](https://p0.ssl.qhimg.com/t01d7549e94a555f909.webp)](https://p0.ssl.qhimg.com/t01d7549e94a555f909.webp)

我们准备pipe管道配置连接，这里的888端口任意

**3.  使用CRT连接ASA**

 

[![](https://p5.ssl.qhimg.com/t01b0870a9f81df2a1f.webp)](https://p5.ssl.qhimg.com/t01b0870a9f81df2a1f.webp)

打开Secure CRT的Telnet连接

[![](https://p3.ssl.qhimg.com/t018ce6a8ff4d8306d6.webp)](https://p3.ssl.qhimg.com/t018ce6a8ff4d8306d6.webp)

需与之前的888端口对应

[![](https://p1.ssl.qhimg.com/t01e56f87518514f050.webp)](https://p1.ssl.qhimg.com/t01e56f87518514f050.webp)

最后创建CRT连接完毕

**4.  确认ASA 版本**

[![](https://p5.ssl.qhimg.com/t01cf35ee038d0bfde1.webp)](https://p5.ssl.qhimg.com/t01cf35ee038d0bfde1.webp)

成功连接ASA之后进入查看ASA的版本信息，这里是8.4(2)

**5.  确认SNMP_SERVER的网卡信息**

[![](https://p4.ssl.qhimg.com/t017ad4d0d6b931df44.webp)](https://p4.ssl.qhimg.com/t017ad4d0d6b931df44.webp)

检查SNMP服务器的网卡配置信息 注意是host only

**6.  配置ASA基本信息**

ciscoasa(config)#hostname MILSASA

MILSASA(config)#enable password 123

MILSASA(config)#interface GigabitEthernet 0

MILSASA(config-if)#nameif inside

INFO:Security level for "inside" set to 100 by default.

MILSASA(config-if)#ip address 192.168.120.10 255.255.255.0

MILSASA(config-if)#no shutdown

**7.  启用本地Vmnet1网卡**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01056a0c18d455ddf8.webp)

[![](https://p1.ssl.qhimg.com/t018e726fd51c232bc0.webp)](https://p1.ssl.qhimg.com/t018e726fd51c232bc0.webp)

为了远程管理，本地配置同网段IP地址即可

**8.  确认本地到ASA链路正常**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b629866457a76f48.webp)

9.  确认本地到SNMP_SERVER链路正常

[![](https://p1.ssl.qhimg.com/t018b325c26f70784a1.webp)](https://p1.ssl.qhimg.com/t018b325c26f70784a1.webp)

10.     确认SNMP到ASA链路正常：

[![](https://p3.ssl.qhimg.com/t01a30aa4416bd96501.webp)](https://p3.ssl.qhimg.com/t01a30aa4416bd96501.webp)

11.     确认ASA到SNMP链路正常：

[![](https://p5.ssl.qhimg.com/t0199a817b002ae11b2.webp)](https://p5.ssl.qhimg.com/t0199a817b002ae11b2.webp)

12.     创建ASA用户名和密码

MILSASA(config)#username MILS password 123

MILSASA(config)#aaa authentication ssh console LOCAL

表示SSH与CONSOLE均使用本地认证

13.     配置ASA 的SSH服务

MILSASA(config)# crypto key generate rsamodulus 1024

INFO: The name for the keys will be:&lt;Default-RSA-Key&gt;

Keypair generation process begin. Pleasewait…

配置1024位的RSA秘钥（为了安全起见建议一般为1024位）

MILSASA(config)# ssh 192.168.120.3255.255.255.255 inside

这里我只指定一个IP，指定只有SNMP_SERVER服务器可以使用SSH连接这台ASA

14.     确认这台SNMP_SERVER可管理ASA

[![](https://p2.ssl.qhimg.com/t0173889edf392315d3.webp)](https://p2.ssl.qhimg.com/t0173889edf392315d3.webp)

 <br>

15.     配置SNMP服务

MILSASA(config)#snmp-server community vipshop，由于SNMP是通过团体名进行通信所以需配置一个团体名这里我自定义为“vipshop”，也就是vipshop，才可以进行后续操作，而大多数情况下，用户往往会保留默认的“public”或者“private”命名，那么，你是不是又想到了什么？MILSASA(config)#snmp-server host inside 192.168.120.3，配置inside内部端口的白名单，即指定SNMP_SERVER地址IP address of SNMP notification host。

16.     上传eqgrp-free-file-master

[![](https://p0.ssl.qhimg.com/t01ae3770b5683abfbf.webp)](https://p0.ssl.qhimg.com/t01ae3770b5683abfbf.webp)

17.     解压缩eqgrp-free-file-master

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013b96b7085f090b23.webp)

18.  查看eqgrp-free-file-master

[![](https://p1.ssl.qhimg.com/t014071f65437bf4a29.webp)](https://p1.ssl.qhimg.com/t014071f65437bf4a29.webp)

[![](https://p3.ssl.qhimg.com/t01e2430215418f8dc2.webp)](https://p3.ssl.qhimg.com/t01e2430215418f8dc2.webp)

[![](https://p1.ssl.qhimg.com/t0162295e4f7f673508.webp)](https://p1.ssl.qhimg.com/t0162295e4f7f673508.webp)

19.     利用Info搜集信息

[![](https://p5.ssl.qhimg.com/t017d80e0d2aba15824.webp)](https://p5.ssl.qhimg.com/t017d80e0d2aba15824.webp)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016fda37dd46568105.webp)

[![](https://p0.ssl.qhimg.com/t01b65fc3fabc8e05d9.webp)](https://p0.ssl.qhimg.com/t01b65fc3fabc8e05d9.webp)

[![](https://p2.ssl.qhimg.com/t0176cb9b6e4191f099.webp)](https://p2.ssl.qhimg.com/t0176cb9b6e4191f099.webp)

利用SNMP发现了ASA的版本号

同时也识别出了Community名以及特征字符 kell60等关键信息

20.     开启攻击脚本

[![](https://p2.ssl.qhimg.com/t017638a7781c18c750.webp)](https://p2.ssl.qhimg.com/t017638a7781c18c750.webp)

[![](https://p5.ssl.qhimg.com/t012a14ad24d3996b42.webp)](https://p5.ssl.qhimg.com/t012a14ad24d3996b42.webp)

[![](https://p3.ssl.qhimg.com/t013629837bdfd6f713.webp)](https://p3.ssl.qhimg.com/t013629837bdfd6f713.webp)

[![](https://p1.ssl.qhimg.com/t01338381915a4efedf.webp)](https://p1.ssl.qhimg.com/t01338381915a4efedf.webp)

显示success字样，表示该脚本执行有效

<br>

**二、验证试验结果**

**验证（1）用户名+空密码 –&gt;成功进入ASA**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011488f96c3b643674.webp)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011011d8c7c9bc4379.png)

当我使用MILS作为用户名登录的时候，没有要求输入密码，并且直接进入Enable模式！

**验证（2）非法用户名+空密码 –&gt;成功进入ASA**

[![](https://p0.ssl.qhimg.com/t01f4bc9efb72925090.webp)](https://p0.ssl.qhimg.com/t01f4bc9efb72925090.webp)

[![](https://p1.ssl.qhimg.com/t01ffad22aa1329e231.webp)](https://p1.ssl.qhimg.com/t01ffad22aa1329e231.webp)

还记得我们刚才创建的ASA的用户只有MILS吗？

MILSASA(config)#username MILS password 123

这里使用一个不存在的用户名TEST登录，同样的，回车直接进入ASA的Enable模式



**三、利用场景分析：**

1.需与受影响的ASA处于路由可达状态；

2.受影响的ASA必须处于路由模式、单模或多模模式下；

3.该漏洞可被Ipv4路由协议触发；

4.在SNMP v1与v2下攻击者必须知道SNMP的Community

<br>

**四、影响范围分析：**

Cisco ASA 5500 Series Adaptive SecurityAppliances

Cisco ASA 5500-X Series Next-GenerationFirewalls

Cisco ASA Services Module for Catalyst 6500 Series Switches 

Cisco 7600 Series Routers

Cisco ASA 1000V Cloud Firewall

Cisco Adaptive Security Virtual Appliance(ASAv)

Cisco Firepower 4100 Series

Cisco Firepower 9300 ASA Security Module

Cisco Firepower Threat Defense Software

Cisco Firewall Services Module (FWSM)*

Cisco Industrial Security Appliance 3000 

Cisco PIX Firewalls*

<br>

**五、解决办法（官方）：**

Administrators are advised to allow onlytrusted users to have SNMP access and to monitor affected systems using thesnmp-server host command.

The SNMP chapter of the Cisco ASA SeriesGeneral Operations CLI Configuration Guide explains how SNMP is configured inthe Cisco ASA.

The attacker must know the communitystrings to successfully launch an attack against an affected device. Communitystrings are passwords that are applied to an ASA device to restrict bothread-only and read-write access to the SNMP data on the device. These communitystrings, as with all passwords, should be carefully chosen to ensure they arenot trivial. Community strings should be changed at regular intervals and inaccordance with network security policies. For example, the strings should bechanged when a network administrator changes roles or leaves the company.

[![](https://p2.ssl.qhimg.com/t01f8ae10adae074dfc.webp)](https://p2.ssl.qhimg.com/t01f8ae10adae074dfc.webp)
