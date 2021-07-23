> 原文链接: https://www.anquanke.com//post/id/190495 


# Snort入侵检测系统的应用


                                阅读量   
                                **989272**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01e73e03a2e327cc43.jpg)](https://p3.ssl.qhimg.com/t01e73e03a2e327cc43.jpg)



## 引言

随着工业信息化建设不断发展及“中国制造2025”等国家战略的推出，以及云计算、大数据、人工智能、物联网等新一代信息技术与制造技术的加速融合，工业控制系统由从原始的封闭独立走向开放、由单机走向互联、由自动化走向智能化。因此，工业控制网络面临的传统安全威胁和工控网络特有安全威胁也在不断增加。

工业控制网络互连程度的大大提升使传统安全威胁可以渗透到工业控制网络中，原本封闭的工业控制网络早期并没有考虑相应其安全问题，在数据窃取、身份认证、无线连接、安全追溯等多方面都存在严重的安全风险。同时由于国内外各厂商及协会公布了大量有关工控协议的标准和实现细节，因此攻击者可以通过深入挖掘工业标准的漏洞，并借此展开针对特定工业协议发起专用的攻击。

由此可见，工业控制网络目前存在极大的安全隐患，提供全面、纵深的安全防御策略进行有效的保护迫在眉睫。而边界安全防护便是首当其冲的重要关键环节，工业防火墙自然也就成为了工业控制网络边界安全建设的首选安全设备。

利用工业防火墙隔离OT网内各安全区域，全面提升工控网络的安全性，可有效降低网络被入侵，有效防止安全威胁迁移扩散，可有效解决工业系统间因缺少隔离引起的安全问题，如因配置错误、硬件故障、病毒等引发的安全威胁。因此，本文将介绍PfSense防火墙的基本概念、功能特点以及应用场景等。



## 基本概念

PfSense是一个基于FreeBSD，专为防火墙和路由器功能定制的开源版本。它被安装在计算机上作为网络中的防火墙和路由器存在，并以可靠性著称，且提供往往只存在于昂贵商业防火墙才具有的特性。它可以通过WEB页面进行配置，升级和管理而不需要使用者具备FreeBSD底层知识。pfSense通常被部署作为边界防火墙、路由器、无线接入点、DHCP服务器、DNS服务器和VPN端点。



## 功能特点
- 基于稳定可靠的FreeBSD操作系统，能适应全天候运行的要求。
- 具有用户认证功能，使用Web网页的认证方式，配合RADIUS可以实现记费功能。
- 完善的防火墙，流量控制和数据包过滤功能，保证了网络的安全，稳定和高速运行。
- 支持多条WAN线路和负载均衡功能，可大幅度提高网络出口带宽，在带宽拥塞时自动分配负载。
- 内置了Ipsec和PPTP VPN功能，实现不同分支机构的远程互联或远程用户安全地访问内部网。
- 支持802.1Q VLAN标准，可以通过软件模拟的方式使得普通的网卡能识别802.1Q的标记，同时为多个VLAN的用户提供服务。
- 支持使用额外的软件包来扩展pfSense功能，为用户提供更多的功能(如FTP和透明代理)。
- 详细的日志功能，方便用户对网络出现的事件分析，统计和处理。
- 使用Web管理界面进行配置(支持SSL)，支持远程管理和软件版本自动在线升级。


## 应用场景

1、部署于隔离管理网与控制网之间

工业防火墙控制跨层访问并深度过滤层级间的数据交换，阻止攻击者基于管理网向控制网发起攻击。

2、部署于控制网的不同安全区域间

工业防火墙可将控制网分成不同的安全区域，控制安全区域之间的访问，并深度过滤各区域间的流量数据，以阻止区域间安全风险的扩散。

3、部署于关键设备与控制网之间

工业防火墙检测访问关键设备的IP，阻止非业务端口的访问与非法操作指令，记录关键设备的所有访问与操作记录，实现对关键设备的安全防护与流量审计。

[![](https://p1.ssl.qhimg.com/t0176e7c163c6220620.png)](https://p1.ssl.qhimg.com/t0176e7c163c6220620.png)



## 部署过程

1、下载PsSense开源防火墙

2、使用虚拟机安装PfSense开源防火墙

默认用户名密码：admin/pfsense

安装方法可参考：[https://www.jianshu.com/p/b6f4290a88fa](https://www.jianshu.com/p/b6f4290a88fa)

3、防火墙默认为英文版，如果需要设置简体中文，请按照以下步骤进行。

4、安装Snort插件

Snort入侵检测系统详细参考：[https://www.cnblogs.com/HacTF/p/7992787.html](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.cnblogs.com%2FHacTF%2Fp%2F7992787.html)

5、Xp环境中开启Modbus协议仿真软件

6、在PfSense中配置防火墙策略

添加网络接口并配置防火策略

策略注释：IP：10.211.55.3的任意端口连接192.168.163.137的502端口都会报警“有人异常连接Modbus设备”，并设置该报警事件id为12345。

保存设置，启用防火策略。

在Win7（IP:10.211.55.3）中使用Modbusscan软件连接Modbus仿真器。

从PfSense防火墙中可以看见报警信息。

针对更多协议的详细检测规则，请参考：

[http://plcscan.org/blog/2015/10/ids-rules-for-scada-systems/](https://links.jianshu.com/go?to=http%3A%2F%2Fplcscan.org%2Fblog%2F2015%2F10%2Fids-rules-for-scada-systems%2F)

```
#
#
# $Id: myicsrules.rules,v 0.1,
#----------
# myicsrules RULES
# ICS protocal/ICS Software communication identification/Filter
# Siemens S7 TCP 102
# Modbus TCP 502
#
#
# 
# 
#
#----------
# Siemens S7 Filter rules
#----------
#设置S7 PLC内部时钟的时间
alert tcp any any -&gt; any 102 (msg:"Request Time functions Set clock";content:"|03 00|";offset:0;depth:2;content:"|32 07 00|";offset:7;depth:3;content:"|00 01 12 04 11 47 02 00|";offset:17;depth:8;sid:8999907;)
#设置与S7 PLC会话的密码
alert tcp any any -&gt; any 102 (msg:"Request Security functions Set PLC session password";content:"|03 00|";offset:0;depth:2;content:"|00 01 12 04 11 45 01 00|";offset:17;depth:8;sid:8999908;)
#设置S7 PLC的CPU到STOP状态
alert tcp any any -&gt; any 102 (msg:"Request CPU functions Set PLC CPU STOP";content:"|29 00 00 00 00 00 09 50 5f 50 52 4f 47 52 41 4d|";sid:8999909;)
#暖启动S7 PLC的CPU到RUN状态
alert tcp any any -&gt; any 102 (msg:"Request CPU functions Set PLC CPU Hot Restart";content:"|28 00 00 00 00 00 00 fd 00 00 09 50 5f 50 52 4f|";sid:8999910;)
#冷启动S7 PLC的CPU到RUN状态
alert tcp any any -&gt; any 102 (msg:"Request CPU functions Set PLC CPU Cold Restart";content:"|28 00 00 00 00 00 00 fd 00 02 43 20 09 50 5f 50 52 4f 47 52 41 4d|";sid:8999911;)
#正在写S7 PLC内部的内存变量
alert tcp any any -&gt; any 102 (msg:"Write Var";content:"|03 00|";offset:0;depth:2;content:"|32 01|";offset:7;depth:2;content:"|05|";offset:17;depth:1;sid:8999912;)
#正在请求下载程序块
alert tcp any any -&gt; any 102 (msg:"Request download";content:"|03 00|";offset:0;depth:2;content:"|32 01|";offset:7;depth:2;content:"|1a|";offset:17;depth:1;sid:8999913;)
#开始请求下载程序块
alert tcp any any -&gt; any 102 (msg:"Download block";content:"|03 00|";offset:0;depth:2;content:"|32 01|";offset:7;depth:2;content:"|1b|";offset:17;depth:1;sid:8999914;)
#程序块下载结束
alert tcp any any -&gt; any 102 (msg:"Download ended";content:"|03 00|";offset:0;depth:2;content:"|32 01|";offset:7;depth:2;content:"|1c|";offset:17;depth:1;sid:8999915;)
#正在请求上载程序块
alert tcp any any -&gt; any 102 (msg:"Start upload";content:"|03 00|";offset:0;depth:2;content:"|32 01|";offset:7;depth:2;content:"|1d|";offset:17;depth:1;sid:8999916;)
#开始上载程序块
alert tcp any any -&gt; any 102 (msg:"Upload";content:"|03 00|";offset:0;depth:2;content:"|32 01|";offset:7;depth:2;content:"|1e|";offset:17;depth:1;sid:8999917;)
#结束上载程序块
alert tcp any any -&gt; any 102 (msg:"End upload";content:"|03 00|";offset:0;depth:2;content:"|32 01|";offset:7;depth:2;content:"|1f|";offset:17;depth:1;sid:8999918;)
#删除S7 PLC内部程序块操作
alert tcp any any -&gt; any 102 (msg:"Delet block";content:"|03 00|";offset:0;depth:2content:"|05 5f 44 45 4c 45|";sid:8999919;)

#
#----------
# Modbus Filter rules
#----------
#正在写单线圈寄存器
alert tcp any any -&gt; any 502 (msg:"Modbus TCP/Write Single Coil";content:"|00 00|";offset:2; depth:2; content:"|05|";offset:7;depth:1;sid:8999100;)
#正在写单个保持寄存器
alert tcp any any -&gt; any 502 (msg:"Modbus TCP/Write Single Register";content:"|00 00|";offset:2; depth:2; content:"|06|";offset:7;depth:1;sid:8999101;)
#正在读从站状态
alert tcp any any -&gt; any 502 (msg:"Modbus TCP/Read Exception Status";content:"|00 00|";offset:2; depth:2; content:"|07|";offset:7;depth:1;sid:8999102;)
#诊断设备命令
alert tcp any any -&gt; any 502 (msg:"Modbus TCP/Diagnostics Device";content:"|00 00|";offset:2; depth:2; content:"|08|";offset:7;depth:1;sid:8999103;)
#正在写多个线圈寄存器
alert tcp any any -&gt; any 502 (msg:"Modbus TCP/Write Multiple Coils";content:"|00 00|";offset:2; depth:2; content:"|0f|";offset:7;depth:1;sid:8999104;)
#正在写多个保持寄存器
alert tcp any any -&gt; any 502 (msg:"Modbus TCP/Write Multiple registers";content:"|00 00|";offset:2; depth:2; content:"|10|";offset:7;depth:1;sid:8999105;)
#正在写文件参数
alert tcp any any -&gt; any 502 (msg:"Modbus TCP/Write File Record";content:"|00 00|";offset:2; depth:2; content:"|15|";offset:7;depth:1;sid:8999106;)
#屏蔽写寄存器
alert tcp any any -&gt; any 502 (msg:"Modbus TCP/Mask Write Register";content:"|00 00|";offset:2; depth:2; content:"|16|";offset:7;depth:1;sid:8999107;)
#读写多个寄存器
lert tcp any any -&gt; any 502 (msg:"Modbus TCP/Read/Write Multiple registers";content:"|00 00|";offset:2; depth:2; content:"|17|";offset:7;depth:1;sid:8999108;)
#正在枚举设备信息
alert tcp any any -&gt; any 502 (msg:"Modbus TCP/Read Device Identification";content:"|00 00|";offset:2; depth:2; content:"|2B|";offset:7;depth:1;sid:8999109;)
#正在枚举施耐德昆腾PLC的内存串号
alert tcp any any -&gt; any 502 (msg:"Schneider PLC(Quantumn) uses function code 90 for communications the Unity pro software Request Memory Card ID";content:"|00 00|";offset:2;depth:2;content:"|5a|";offset:7;depth:1;content:"|00 06 06|";offset:8;depth:3;sid:8999110;)
#正在枚举施耐德昆腾PLC的CPU模块信息
alert tcp any any -&gt; any 502 (msg:"Schneider PLC(Quantumn) uses function code 90 for communications the Unity pro software Request CPU Module info";content:"|00 00|";offset:2;depth:2;content:"|5a|";offset:7;depth:1;content:"|00 02|";offset:8;depth:2;dsize:10;sid:8999111;)
#正在枚举施耐德昆腾PLC内部的工程名称
alert tcp any any -&gt; any 502 (msg:"Schneider PLC(Quantumn) uses function code 90 for communications the Unity pro software Request Project Project file name";content:"|00 00|";offset:2;depth:2;content:"|5a|";offset:7;depth:1;content:"|f6 00|";offset:17;depth:2;sid:8999112;)
#正在枚举施耐德昆腾PLC内部的工程上次修改时间
alert tcp any any -&gt; any 502 (msg:"Schneider PLC(Quantumn) uses function code 90 for communications the Unity pro software Request Project Information(Revision and Last Modified)";content:"|00 00|";offset:2;depth:2;content:"|5a|";offset:7;depth:1;content:"|03 00|";offset:17;depth:2;sid:8999113;)
#正在将施耐德昆腾PLC的CPU设置到STOP状态
alert tcp any any -&gt; any 502 (msg:"Schneider PLC(Quantumn) uses function code 90 for communications the Unity pro software Set PLC CPU STOP";content:"|00 00|";offset:2;depth:2;content:"|5a|";offset:7;depth:1;content:"|40|";offset:9;depth:1;sid:8999114;)
#正在将施耐德昆腾PLC的CPU设置到RUN状态
alert tcp any any -&gt; any 502 (msg:"Schneider PLC(Quantumn) uses function code 90 for communications the Unity pro software Set PLC CPU Restart";content:"|00 00|";offset:2;depth:2;content:"|5a|";offset:7;depth:1;content:"|41|";offset:9;depth:1;sid:8999115;)
```

下面举例说明（以写单线圈寄存器为例）

```
alert tcp any any -&gt; any 502 (msg:"Modbus TCP/Write Single Coil";content:"|00 00|";offset:2; depth:2; content:"|05|";offset:7;depth:1;sid:8999100;)
```

其中content:”|05|”表示功能码为05

在Win7中连接Modbus协议仿真器并进行写线圈操作。

查看防火墙报警信息。

[![](https://p3.ssl.qhimg.com/dm/1024_469_/t010f5abf1275963354.png)](https://p3.ssl.qhimg.com/dm/1024_469_/t010f5abf1275963354.png)



## 总结

伴随着工业互联网的蓬勃发展，IT和OT的融合不断深入，工业网络所面临的安全威胁与日俱增。而解决工业网络面临的诸多安全问题，提供从网络边界、区域到设备终端的完整防护体系也是企业所必需的。

PS：本文中所用到的开源防火墙PfSense镜像以及软件，可以关注“TideSec安全团队”公众号回复”工业防火墙”获取。



## 关注我们-TideSec安全团队

Tide安全团队正式成立于2019年1月，是以互联网攻防技术研究为目标的安全团队，目前聚集了十多位专业的安全攻防技术研究人员，专注于网络攻防、Web安全、移动终端、安全开发、IoT/物联网/工控安全等方向。

想了解更多Tide安全团队，请关注团队官网: [http://www.TideSec.net](https://links.jianshu.com/go?to=http%3A%2F%2Fwww.TideSec.net) 或关注公众号：

[![](https://p0.ssl.qhimg.com/t01170ef78001753d04.png)](https://p0.ssl.qhimg.com/t01170ef78001753d04.png)
