> 原文链接: https://www.anquanke.com//post/id/260832 


# 边界设备SNMP服务攻击思考


                                阅读量   
                                **116709**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01b7f16db81c2fc845.png)](https://p1.ssl.qhimg.com/t01b7f16db81c2fc845.png)



## 0x01 SNMP协议分析

### <a class="reference-link" name="1.%20%E6%A6%82%E8%BF%B0"></a>1. 概述

网络设备越来越大，就需要实时去管理如此诸多的设备，SNMP应运而生。

SNMP协议，可以用来接收网络节点的通知消息和警告时间报告等，从而获知网络出现的问题。

**SNMP协议版本**
- SNMP V1: SNMP协议最初版本(1998年)
- SNMP V2: SNMP协议第二个版本，对比第一版，再性能、安全、机密性和管理者之间通信等方面进行了大量改进
- SNMP V3: SNMP协议目前最新的版本(2004年)，提升协议的安全性，增加了认证和密文传输功能。
代理在UDP的161端口接收NMS的读写请求消息

管理站在UDP的162端口接收代理的事件通告消息

### <a class="reference-link" name="2.%20SNMP%E6%9E%B6%E6%9E%84%E7%BB%84%E6%88%90"></a>2. SNMP架构组成
1. 社区:同一个管理框架下的网络管理站和所有的节点的集合
1. 网络管理站:一个管理控制台，也称为网络管理系统(NMS)
1. 节点:网络上的设备(被管理的设备)
### <a class="reference-link" name="3.%20%E5%B7%A5%E4%BD%9C%E5%8E%9F%E7%90%86"></a>3. 工作原理

发现、查询和监视网络中其他设备的状态信息。

[![](https://p0.ssl.qhimg.com/t011c0776792e63da7c.png)](https://p0.ssl.qhimg.com/t011c0776792e63da7c.png)

管理员通过**NMS获取网关监控数据**的工作流程，其中涉及了一些SNMP协议的关键信息
- MIB(管理信息库): 任何一个被管理设备都表示成一个对象，并称为被管理对象。而MIB就是被管理对象的集合。定义了被管理对象的一系列属性，如对象的名称、对象的访问权限和对象的数据类型等。
- SNMP代理: 是一种嵌入再设备中的网络管理软件模块，主要来控制本地机器的管理信息，负责将管理信息转换成SNMP兼容的格式，传递给NMS
工作流程步骤:
1. 管理员查询被管理设备中的对象相关值时，通过网络管理站NMS中的MIB找到相关对象
1. 网络管理站NMS向SNMP代理申请MIB中定义对象的相关值
1. SNMP代理在自己的MIB库中进行查找
1. SNMP代理将找到的对象相关值返回给网络管理站NMS
### <a class="reference-link" name="4.%20%E9%80%9A%E4%BF%A1%E6%96%B9%E5%BC%8F"></a>4. 通信方式

SNMP采用特殊的客户机/服务器模式进行通信。

客户端 —— 网络管理站NMS

服务器 —— SNMP代理
- 网络管理站NMS向SNMP代理发出请求，询问一个MIB定义的信息的参数值
- SNMP代理收到请求后，返回关于MIB定义信息的各种查询
### <a class="reference-link" name="5.%20%E6%93%8D%E4%BD%9C%E7%B1%BB%E5%9E%8B%E5%8F%8A%E5%91%BD%E4%BB%A4"></a>5. 操作类型及命令

操作类型
- get-request: NMS从SNMP Agent处提取一个或多个参数值
- get-response：返回一个或多个参数的值
- get-next-request: 网络管理站NMS从SNMP代理处提取一个或者多个参数的下一个参数值
- set-request: 网络管理站NMS设置SNMP代理处获取MIB的相关参数值
- trap: SNMP代理主动向网络管理站NMS发送报文消息
- informRequest： SNMP代理主动向网络管理站NMS发送报文消息，NMS进行响应
操作命令

Get:管理站读取代理者处对象的值

Set:管理站设置代理者处对象的值

Trap:代理者主动向管理站通报重要事件

### <a class="reference-link" name="6.%20%E6%8A%A5%E6%96%87%E5%88%86%E6%9E%90"></a>6. 报文分析

利用wireshark抓取报文

[![](https://p4.ssl.qhimg.com/t016e079b493180be2e.png)](https://p4.ssl.qhimg.com/t016e079b493180be2e.png)



## 0x02 SNMP服务攻击

Cisco、H3C、华为等厂商生产的网络设备大多支持SNMP网管协议，可以通过SNMP设置设备的某个参数对设备配置进行备份或者更新。

### <a class="reference-link" name="1.%20MIB%E6%96%87%E4%BB%B6"></a>1. MIB文件

鉴于每种设备MIB是不一样的，所对应能执行的操作也是不一样。

### <a class="reference-link" name="2.%20%E6%95%8F%E6%84%9F%E4%BF%A1%E6%81%AF"></a>2. 敏感信息

GNS3 构造一个思科路由器环境

[![](https://p2.ssl.qhimg.com/t01f244832711b1059f.png)](https://p2.ssl.qhimg.com/t01f244832711b1059f.png)

#### <a class="reference-link" name="2.1%20%E4%BF%AE%E6%94%B9%E8%AE%BE%E5%A4%87%E4%BF%A1%E6%81%AF"></a>2.1 修改设备信息

修改思科路由器名字

条件: 获得SNMP可读写团体名

修改之前的名字

[![](https://p5.ssl.qhimg.com/t018aba8c07d6af94d6.png)](https://p5.ssl.qhimg.com/t018aba8c07d6af94d6.png)

修改之后

[![](https://p5.ssl.qhimg.com/t013e42e4a467dd7eba.png)](https://p5.ssl.qhimg.com/t013e42e4a467dd7eba.png)

查看命令

[![](https://p4.ssl.qhimg.com/t01dd093537279a311e.png)](https://p4.ssl.qhimg.com/t01dd093537279a311e.png)

#### <a class="reference-link" name="2.2%20%E8%8E%B7%E5%8F%96%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6"></a>2.2 获取配置文件

获取思科路由器配置文件(模拟测试)

配置开启路由器snmp服务

```
Router&gt;enable 
Router# configure terminal 
Router(config)# snmp-server community public RO //读
Router(config)# snmp-server community private RW //写
Router(config)# snmp-server host 192.168.32.2 host //指定客户端，可以设置任意主机
Router(config)# snmp-server enable traps snmp
```

检测是否开启

[![](https://p4.ssl.qhimg.com/t019a35629fc37102c5.png)](https://p4.ssl.qhimg.com/t019a35629fc37102c5.png)

下载路由器配置

使用msfconsole内置模块

[![](https://p5.ssl.qhimg.com/t014c9765dc0bfe1e66.png)](https://p5.ssl.qhimg.com/t014c9765dc0bfe1e66.png)

攻击流程

[![](https://p4.ssl.qhimg.com/t012037493e10b41b6e.png)](https://p4.ssl.qhimg.com/t012037493e10b41b6e.png)

查看配置文件(可以查看路由器的配置信息，如telnet密码、特权密码、路由、mac地址表等关键信息)

[![](https://p2.ssl.qhimg.com/t0141f7d3229e88d168.png)](https://p2.ssl.qhimg.com/t0141f7d3229e88d168.png)

#### <a class="reference-link" name="2.3%20%E5%88%A9%E7%94%A8%E6%95%8F%E6%84%9F%E4%BF%A1%E6%81%AF%E8%8E%B7%E5%8F%96%E8%AE%BE%E5%A4%87%E6%9D%83%E9%99%90"></a>2.3 利用敏感信息获取设备权限

**强网拟态的实战题—(如何获取设备权限)**

1.端口扫描发现设备开启(161端口、22端口)

获取设备名称以及型号

[![](https://p1.ssl.qhimg.com/t016269fba73558be8a.png)](https://p1.ssl.qhimg.com/t016269fba73558be8a.png)

确定设备为一台huawei路由器

2.是否能够获取ssh用户名

查询该设备MIB，定位到查询用户名的OID

[![](https://p5.ssl.qhimg.com/t01c4256afcb2011215.png)](https://p5.ssl.qhimg.com/t01c4256afcb2011215.png)

查询该路由器用户名

[![](https://p3.ssl.qhimg.com/t0195a2e39a36210b6b.png)](https://p3.ssl.qhimg.com/t0195a2e39a36210b6b.png)

3.尝试暴力破解(是否存在弱口令)

[![](https://p4.ssl.qhimg.com/t0168533a0e8dd541dc.png)](https://p4.ssl.qhimg.com/t0168533a0e8dd541dc.png)

破解得到密码123456

4.登录设备

[![](https://p0.ssl.qhimg.com/t0170d20d88df76f54c.png)](https://p0.ssl.qhimg.com/t0170d20d88df76f54c.png)

Huawei的命令行提供了诸如ping、traceroute、telnet等工具，这就意味着你可以对内网的其它主机进行探测，进行进一步的内网渗透。



## 总结

一旦获取网络边界设备的SNMP可读写团体名，就可以直入企业内网之中，获取大量的内网资源，企业内网就不在安全。



## 参考

[https://support.huawei.com/hedex/hdx.do?lib=EDOC1100168845AEJ12147&amp;docid=EDOC1100168845&amp;lang=en&amp;v=05&amp;tocLib=EDOC1100168845AEJ12147&amp;tocV=05&amp;id=EN-US_LOGREF_0313365874&amp;tocURL=resources%2525252Flog%2525252FSSH_USER_LOGIN_5.html&amp;p=t&amp;fe=1&amp;ui=3&amp;keyword=ssh](https://support.huawei.com/hedex/hdx.do?lib=EDOC1100168845AEJ12147&amp;docid=EDOC1100168845&amp;lang=en&amp;v=05&amp;tocLib=EDOC1100168845AEJ12147&amp;tocV=05&amp;id=EN-US_LOGREF_0313365874&amp;tocURL=resources%2525252Flog%2525252FSSH_USER_LOGIN_5.html&amp;p=t&amp;fe=1&amp;ui=3&amp;keyword=ssh)
