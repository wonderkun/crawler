> 原文链接: https://www.anquanke.com//post/id/99069 


# OMG — 将物联网设备变成代理服务器的Mirai变种


                                阅读量   
                                **184618**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t018d2dae7a4d4bd3f9.png)](https://p3.ssl.qhimg.com/t018d2dae7a4d4bd3f9.png)



## 一、前言

正当FortiGuard实验室在为[RootedCon](https://www.rootedcon.com/speakers)安全会议准备演讲时（该会议将于2018年3月份在西班牙马德里举行，演讲题目为“物联网：机器人之战（IoT: Battle of Bots）”），我们又遇到了另一款新的Mirai变种。

自从Mirai僵尸网络的源代码公布以来，FortiGuard实验室已经发现了多款变种，有多名攻击者改写了代码以适应物联网环境。这些修改版的Mirai僵尸程序除了具备最原始的telnet暴力破解登录功能以外，还添加了一些新的技术，包括[漏洞利用技术](https://blog.fortinet.com/2017/12/12/rise-of-one-more-mirai-worm-variant)，也能针对更多的[系统架构](https://blog.fortinet.com/2018/01/25/iot-botnet-more-targets-in-okirus-cross-hairs)。我们同样观察到许多攻击者修改Mirai的目的是赚取更多的金钱。Mirai最初的设计目标是发起DDoS攻击，但后面经过修改的变种针对的是存在漏洞的[ETH挖矿设备](https://blog.fortinet.com/2018/02/02/satori-adds-known-exploit-chain-to-slave-wireless-ip-cameras)，目标是挖掘加密货币。在本文中，我们将分析名为OMG的一个僵尸程序，该程序也是Mirai僵尸程序的变种，可以将物联网（IoT）设备转变为代理服务器。

2016年10月，Brian Krebs发表了一篇文章，介绍了网络犯罪分子如何将IoT设备转变为代理服务器以谋取金钱。在开展各种肮脏的活动时（如网络盗窃，黑客入侵系统等），网络犯罪分子会使用代理服务器来增加匿名性。利用代理服务器来谋取金钱的一种方法是将这些服务器的访问权限出售给其他网络犯罪分子，我们认为这款最新的Mirai僵尸程序变种的背后动机正是如此。

在本文中，我们也会将该恶意软件与原始的Mirai程序进行对比。



## 二、Mirai vs OMG

我们先来看看OMG的配置表。这个表最开始处于加密状态，需要使用`0xdeadbeef`这个密钥来解密，这个过程与原始的Mirai程序相同。我们首先注意到的是程序中存在`/bin/busybox OOMGA`以及`OOMGA: applet not found`字符串。Mirai僵尸程序之所以得到“Mirai”这个名字，原因在于程序中存在`/bin/busybox MIRAI`以及`MIRAI: applet not found`字符串，这两条命令用来判断恶意软件是否通过暴力破解成功进入目标物联网设备。其他变种也有类似字符串，比如Satori/Okiru、Masuta变种等。

因为这个原因，我们将这款变种命名为OMG。

这款变种同时也增加以及删除了原始Mirai代码中存在的某些配置信息。有两项增量信息值得注意，变种新增了两个字符串，用来添加防火墙规则，以允许通信流量穿透两个随机端口，我们会在后文中讨论这一细节。

[![](https://p4.ssl.qhimg.com/t01ce7567f967617b41.png)](https://p4.ssl.qhimg.com/t01ce7567f967617b41.png)

图1. OMG的配置表

看样子OMG保留了Mirai的原始模块，包括attack模块、killer模块以及scanner模块。这意味着该变种也具备原始Mirai程序所具备的功能，比如杀掉进程（通过检查开放端口来确定与telnet、ssh以及http有关的进程，以及与其他僵尸程序有关的进程）、telnet暴力破解登录以进一步扩散传播以及DOS攻击。

[![](https://p0.ssl.qhimg.com/t013ce8cf7b85f48990.png)](https://p0.ssl.qhimg.com/t013ce8cf7b85f48990.png)

图2. Mirai的主要模块

初始化模块之后，OMG会继续连接到命令与控制（CnC）服务器。如下配置表包含与CnC服务器有关的字符串，即`ccnew.mm.my`，该地址对应的IP地址为`188.138.125.235`。

[![](https://p5.ssl.qhimg.com/t01ecab63f1c28ae3e5.png)](https://p5.ssl.qhimg.com/t01ecab63f1c28ae3e5.png)

图3. CnC域名解析结果

CnC的端口同样包含在配置表中，即50023。

[![](https://p4.ssl.qhimg.com/t0127b586d36c2096be.png)](https://p4.ssl.qhimg.com/t0127b586d36c2096be.png)

图4. CnC端口（50023）

不幸的是，当我们在分析时，这个CnC服务器已经不再响应请求，因此我们的许多研究成果都是静态分析结果。

当成功建连后，OMG会向CnC服务器发送一个自定义消息（`0x00000000`），声明自己为一个新的僵尸节点。

[![](https://p4.ssl.qhimg.com/t018df2aa9b21edbe19.png)](https://p4.ssl.qhimg.com/t018df2aa9b21edbe19.png)

图5. 发送的数据标识新僵尸节点

从代码中我们可知，僵尸程序会从服务端那收到长度为5字节的数据，第一个字节用来表示该IoT设备的具体用途。其中，0代表代理服务器，1用来攻击，大于1的值用来终止连接。

[![](https://p4.ssl.qhimg.com/t01d9f086e0c32d5e9b.png)](https://p4.ssl.qhimg.com/t01d9f086e0c32d5e9b.png)

图6. CnC服务器可能返回的选项



## 三、搭建3proxy

这款Mirai变种会使用3proxy（一款开源软件）来实现代理服务器功能。恶意软件会生成两个随机端口，分别对应于`http_proxy_port`以及`socks_proxy_port`。一旦生成合适的端口，程序就会向CnC报告这一信息。

[![](https://p1.ssl.qhimg.com/t01d61c923ca57ba3b4.png)](https://p1.ssl.qhimg.com/t01d61c923ca57ba3b4.png)

图7. 设置代理

为了使代理服务器能够正常工作，恶意软件必须设置防火墙，使流量能够穿透生成的端口。前面我们提到过，配置表中存在两个字符串，这两个字符串中包含能够添加以及删除防火墙规则的命令，可以完成这一任务。

```
TABLE_IPTABLES1 -&gt; used to INSERT a firewall rule.
iptables -I INPUT -p tcp --dport %d -j ACCEPT;
iptables -I OUTPUT -p tcp --sport %d -j ACCEPT;
iptables -I PREROUTING -t nat -p tcp --dport %d -j ACCEPT;
iptables -I POSTROUTING -t nat -p tcp --sport %d -j ACCEPT

TABLE_IPTABLES2 -&gt; used to DELETE a firewall rule.
iptables -D INPUT -p tcp --dport %d -j ACCEPT;
iptables -D OUTPUT -p tcp --sport %d -j ACCEPT;
iptables -D PREROUTING -t nat -p tcp --dport %d -j ACCEPT;
iptables -D POSTROUTING -t nat -p tcp --sport %d -j ACCEPT
```

[![](https://p0.ssl.qhimg.com/t0179c6f6e111d65256.png)](https://p0.ssl.qhimg.com/t0179c6f6e111d65256.png)

图8. 防火墙启用/禁用函数

启动防火墙规则，使流量能够穿透随机生成的HTTP以及SOCKS端口后，恶意软件开始使用代码中内嵌的预定义配置信息来搭建3proxy。

[![](https://p1.ssl.qhimg.com/t01bfa705e4bb867124.png)](https://p1.ssl.qhimg.com/t01bfa705e4bb867124.png)

图9. 代理配置信息

由于分析过程中服务器已不再活跃，因此我们认为攻击者的目的是出售物联网代理服务器的访问权限，提供访问凭据。



## 四、总结

这是我们首次看到某款Mirai变种在存在漏洞的IoT设备上同时提供DDOS攻击功能以及代理服务功能。伴随着这种趋势，我们相信未来会有越来越多的Mirai变种僵尸程序会具备新的变现方式。

与往常一样，FortiGuard实验室将继续检测Mirai及其衍生品，与大家共享我们的研究成果。



## 五、IOC

所有的样本均标记为`Linux/Mirai.A!tr`。

**哈希值**

```
9110c043a7a6526d527b675b4c50319c3c5f5c60f98ce8426c66a0a103867e4e
a5efdfdf601542770e29022f3646d4393f4de8529b1576fe4e31b4f332f5cd78
d3ed96829df1c240d1a58ea6d6690121a7e684303b115ca8b9ecf92009a8b26a
eabda003179c8499d47509cd30e1d3517e7ef6028ceb347a2f4be47083029bc6
9b2fe793ed900e95a72731b31305ed92f88c2ec95f4b04598d58bd9606f8a01d
2804f6cb611dc54775145b1bb0a51a19404c0b3618b12e41b7ea8deaeb9e357f
```

**CnC服务器**

```
54.234.123.22
ccnew.mm.my
rpnew.mm.my
```
