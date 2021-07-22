> 原文链接: https://www.anquanke.com//post/id/147105 


# IoT僵尸网络Mirai四大变种


                                阅读量   
                                **157225**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://asert.arbornetworks.com/
                                <br>原文地址：[https://asert.arbornetworks.com/omg-mirai-minions-are-wicked/](https://asert.arbornetworks.com/omg-mirai-minions-are-wicked/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t019bde9494ad202a05.jpg)](https://p0.ssl.qhimg.com/t019bde9494ad202a05.jpg)

[DDoS攻击](https://asert.arbornetworks.com/omg-mirai-minions-are-wicked/#footnote)。自Mirai源代码发布以来，就成了构建新恶意软件的框架，开发者们在原有的Mirai代码的基础上添加了新功能，来对Mirai进行改进。

在这篇博文中，我们将深入研究Mirai的四种变体：Satori、JenX、OMG和Wicked，开发者在Mirai的基础上为它们分别加入了专属的新特性。Satori利用了远程代码注入攻击的EXP来强化Mirai代码，而JenX从代码中删除了几个原有的功能，变成了依赖外部工具来进行扫描和利用。

Mirai的变种OMG，它以HTTP和SOCKS代理的形式增加了一项新功能，代理功能能使受感染的物联网设备变成一个攻击支点。该僵尸网络的攻击者现在可以灵活地针对新漏洞发起新的扫描，或者无需更新原始二进制文件即可进行新的攻击。根据物联网设备的类型和连接方式，攻击者可以利用受感染的物联网设备来构建专用网络。<br>
最后一个变种是Wicked，它被用来针对容易出现远程代码执行（RCE）漏洞的Netgear路由器和CCTV-DVR设备。在RCE漏洞的利用过程中，Wicked会下载Owari bot副本并执行。通常，设备的扫描和利用都是自动化的，这也导致任何易受影响的设备可轻易成为僵尸网络的一部分。



## 关键发现
- Satori将Mirai的扫描功能用于远程代码注入攻击。
- JenX bot由Mirai进化而来，使用相似的代码，但去除了扫描和利用功能。
- OMG bot是最近物联网恶意软件领域的新成员，基于Mirai源代码添加了HTTP和SOCKS代理功能的新扩展。
- Wicked，最新的Mirai变种，利用RCE漏洞感染Netgear路由器和CCTV-DVR设备。当发现存在漏洞的设备时，会下载并执行Owari bot的副本。


## 物联网简介

物联网涵盖各种设备，包括（但不限于）：
- 基于IP的摄像头
- 有线/DSL 调制解调器
- DVR系统
- 医疗设备
任何在操作系统上运行并具有网络功能（通过网络发送/接收数据）的嵌入式设备均可视为物联网设备。物联网设备上市速度快并且成本低廉，这些因素也使得他们面临最基本类型的漏洞影响。漏洞包括：
- 硬编码/默认凭证
- 缓冲区溢出
- 命令注入
大多数物联网设备都包含这些类型的漏洞。虽然厂商也发布了补丁来解决这些问题，但通常补丁的使用率很小。通常情况下，消费者接入物联网设备时从不考虑安全性方面的问题，或者可能并不了解进行常规安全更新和使用补丁程序的必要性。根据IHS Markit2的[最新分析](https://asert.arbornetworks.com/omg-mirai-minions-are-wicked/#footnote)，2030年之前，接入设备的数量将从2017年的将近270亿台增加到1250亿台，这些设备对于恶意软件开发者来说非常具有吸引力。



## 物联网恶意软件

在2016年下半年，我们观查到了一次针对DNS托管方/提供商的高可见性DDoS攻击，这次攻击主要影响了一些重要的在线资产，而对这次袭击负责的恶意软件就是Mirai。

Mirai使用针对IP摄像机和家庭路由器的telnet暴力破解攻击，构建了其庞大的基础网络设施。Mirai利用设备出厂的默认凭证进行攻击，其源码已于2016年9月30日公开，从那时开始，Mirai的源码就成为了最近一批物联网僵尸网络的主要部分（详细解释如下）：
- Satori
- JenX
- OMG
- Wicked
### <a class="reference-link" name="Satori"></a>Satori

从2017年12月到2018年1月，NETSCOUT Arbor在网络中观测到了Satori的几个变种，而这些变种都以Mirai为基础。变种2（977534e59c72dafd0160457d802f693d）使用默认凭证扫描，而变种3（440af2606c5dc475c9a2a780e086d665ca203f01）添加了两个RCE。变种4（9c677dd17279a43325556ec5662feba0）吸引了最多的关注，因为它是第一个瞄准ARC架构的物联网僵尸网络。

在这个例子中，我们将重点介绍Satori变种3. Satori的第三个变体使用与Mirai相同的配置表（**图1**和**图2**）。变种3也使用了与Mirai相同的字符串隐写技术，并简单地将XOR键修改为“0x07”。这些相同的功能也可以在OMG中找到，在OMG中，作者使用了“deadbeef”的XOR键，我们将在后面介绍。“deadbeef”的XOR键是Mirai源码中的原始密钥。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://asert.arbornetworks.com/wp-content/uploads/2018/05/Figure1.png)

**图1.Satori配置表（table_init）函数**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://asert.arbornetworks.com/wp-content/uploads/2018/05/Figure2.png)

**图2.Mirai配置表（table_init）函数**

我们看到恶意软件的开发者使用了不同的EXP，例如华为的Home Gateway的EXP来扩展了Mirai的源码，如图3所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://asert.arbornetworks.com/wp-content/uploads/2018/05/Figure3.png)

**图3.华为Home Gateway EXP**

上面提到的Satori变种3样本的SHA1值是440af2606c5dc475c9a2a780e086d665ca203f01，已于2017/12/05首次提交给Virus Total。



### <a class="reference-link" name="JenX"></a>JenX

JenX是IoT僵尸网络的另一个样本，其底层代码也来自Mirai。JenX包含Mirai的几个DDoS功能，使用相同的配置表，并包含相同的字符串混淆技术。**图4**和**图5**比较了JenX和Mirai中的attack_udp_generic攻击代码。OMG与JenX有一些相似之处，但OMG的一个不同点是其使用了源自Mirai的HTTP DDoS攻击——HTTP DDoS攻击已从JenX中删除，但OMG中仍在使用。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://asert.arbornetworks.com/wp-content/uploads/2018/05/Figure4.png)

**图4：Jenx中的attack_udp_generic DoS攻击代码**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://asert.arbornetworks.com/wp-content/uploads/2018/05/Figure5.png)

**图5：Mirai的attack_udp_generic DoS攻击代码**

如图6中所示，JenX选择了将CNC的IP地址进行硬编码，而不是像Mirai那样将C2存储在配置表中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://asert.arbornetworks.com/wp-content/uploads/2018/05/Figure6.png)

**图6: resolve_cnc_addr 函数**

值得注意的是，JenX移除了扫描和利用函数。有一个单独的系统被用来处理这些函数，这也是Mirai，Satori和OMG的主要组成本分。目前，其他研究人员指出，JenX似乎只专注于对视频游戏“侠盗猎车手圣安地列斯”玩家的DDoS攻击。

上面提到的JenX样本的SHA1值是5008b4a7048ee0a013465803f02cb9c4bffe9b02，已于2018/02/01首次提交给Virus Total。



### <a class="reference-link" name="OMG"></a>OMG

Mirai最有趣的变种之一是OMG僵尸网络。与我们提到的其他僵尸网络一样，OMG将Mirai作为其框架，并支持Mirai的所有功能。而OMG脱颖而出的点是其开发者将代理服务器包含到了Mirai代码的扩展中。OMG整合了3proxy，其允许OMG在受感染的物联网设备上启用SOCKS和HTTP代理服务器。有了这两个功能，僵尸网络攻击者就可以通过受感染的物联网设备来选择代理任何流量，包括针对新漏洞的额外扫描、发起更多攻击、或从受感染的IoT设备进行扩展到它们所连接的其他网络。

OMG使用与Mirai，Satori和JenX相同类型的配置表来启用或禁用iptables防火墙规则，而这正允许了对代理服务器的访问。OMG在其配置表中添加了两个新功能，以处理iptables规则的添加和删除（**图7**）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://asert.arbornetworks.com/wp-content/uploads/2018/05/Figure7.png)

**图7: OMG配置表 (table_init) 函数**

**图8**是上述配置表引用的混淆后的iptables命令的片段。我们可以使用“deadbeef”的XOR键来检索反混淆的iptables命令（**图9**）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://asert.arbornetworks.com/wp-content/uploads/2018/05/Figure8.png)

**图8：OMG XOR后的 iptables命令**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://asert.arbornetworks.com/wp-content/uploads/2018/05/Figure9.png)

**图9：OMG反混淆后的iptables命令**

图10是控制iptables规则的函数。命令检索用于访问配置表的值（图7）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://asert.arbornetworks.com/wp-content/uploads/2018/05/Figure10.png)

**图10：OMG iptables函数**

如上图所示，OMG的开发者扩展了Mirai的源码以处理新的代理功能。

上面引用的OMG样本的SHA1值为0ed366c1af749cbda25ff396f28a6b7342d5dcd9，已于2018/1/15首次提交给Virus Total。



### <a class="reference-link" name="Wicked"></a>Wicked

Wicked是最近的Mirai变种。与Satori变种3类似，Wicked将Mirai的认证扫描功能添加到了自己的RCE扫描器中，而它的RCE扫描器则瞄准了Netgear路由器和CCTV-DVR设备。**图11**是定义RCE有效payload的扫描器函数的截图。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://asert.arbornetworks.com/wp-content/uploads/2018/05/Figure11.png)

**图11 RCE EXP**

Wicked依然使用Mirai的字符串混淆技术。就像之前的变种一样，Wicked也会将XOR键替换为“0xdeadbeef”。**如图12**所示，我们看到以“0x37”结尾的混淆字符串。这是Wicked使用“0x37”作为XOR键的一个很好的样式，因为C字符串应该以null结尾。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://asert.arbornetworks.com/wp-content/uploads/2018/05/Figure12.png)

**图12 Wicked 的混淆字符串**

我们可以使用“0x37”的XOR键来解码混淆的字符串，在解码后的字符串中，发现了以下ASCII“艺术”的话：
- “echo ‘¯_(ツ)_/¯ Oh hey there… Looks like I might of inected your device.’ &gt;&gt; /wicked.txt.“
Wicked将消息写入以下位置：
- /root
- /home
- /temp
- /
此时这些文件似乎还并未被Wicked使用，它们可能被攻击者当作一张电话卡来使用。

上面引用的Wicked样本的SHA1值是b8e8c107d242cc0b7516cf7908b67e108a7d927e，已于2018/5/05首次提交给Virus Total。



## Mirai DDoS 攻击类型

上述所有物联网僵尸网络都使用原始Mirai源码支持的相同攻击类型。Mirai和OMG中存在以下DDoS功能：
- TCP滥用
- UDP滥用
- Valve Source Engine（VSE）查询滥用
- GRE滥用
- pseudo-random DNS label-prepending攻击（也称为DNS’Water Torture’攻击）
- HTTP GET、POST和HEAD攻击
**注意：**除了HTTP攻击，Satori，JenX和Wicked支持相同的DDoS功能。



## Mirai DDoS防护

所有相关的网络基础设施、主机/应用程序/服务器和DNS Best Current Practices（BCP）应由网络运营商采用面向公众的网络基础设施和/或互联网设施来执行。使用NETSCOUT Arbor SP的组织可将流量遥测（例如，NetFlow，IPFIX，s / Flow，cflowd / jflow，Netstream等）接入到设备中，从而提供对DDoS攻击流量的检测、分类和跟踪。

流量遥测用于识别发起物联网攻击的设备的IP地址和所使用的攻击类型。如果攻击者正在发起非欺骗性DDoS攻击，则可以使用NETSCOUT Arbor APS / TMS上的黑白名单来禁止发起IOT攻击的设备IP地址。

除了能够快速检测、分类、追溯和缓解由这些物联网僵尸网络发起的DDoS攻击之外，NETSCOUT Arbor SP / TMS的最新版本还提供了额外的增强功能，其可提供更高水平的自动化和配置。



## 结论

将Mirai作为框架，僵尸网络开发者可以快速添加新的攻击和功能，从而大大缩短僵尸网络的开发时间。Mirai源不仅限于DDoS攻击，Satori的变种就被发现用于[攻击以太坊采矿客户](https://asert.arbornetworks.com/omg-mirai-minions-are-wicked/#footnote)。从上面介绍的四个样本可以看出，僵尸网络作者已经在使用Mirai源码作为其构建模块。由于物联网设备的爆炸式增长并未放缓，我们相信我们将继续看到物联网僵尸网络的增长，我们很可能会在未来的僵尸网络中看到Mirai的新变种。

恶意软件攻击者将继续以自动化方式利用针对IoT的恶意软件，通过类似蠕虫的传播、网络代理功能和面向互联网设备中的漏洞的自动化利用，来快速增大僵尸网络的规模。组织机构必须应用适当的补丁、更新和DDoS缓解策略来保护其自身。
