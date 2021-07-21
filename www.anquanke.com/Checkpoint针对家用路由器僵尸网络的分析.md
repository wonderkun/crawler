> 原文链接: https://www.anquanke.com//post/id/92151 


# Checkpoint针对家用路由器僵尸网络的分析


                                阅读量   
                                **99787**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Checkpoint，文章来源：checkpoint.com
                                <br>原文地址：[https://research.checkpoint.com/good-zero-day-skiddie/](https://research.checkpoint.com/good-zero-day-skiddie/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t014cabbc007aa9d895.jpg)](https://p0.ssl.qhimg.com/t014cabbc007aa9d895.jpg)



## 一、概述

Check Point研究人员发现了某款家用路由器（HG532）的0Day漏洞（CVE-2017-17215），同时也发现了利用该漏洞的数十万次在野攻击行为。我们将攻击活动中使用的载荷标识为OKIRU/SATORI，这款攻击载荷为Mirai的新型变种，并且我们也发现了此次攻击活动幕后嫌犯的相关线索，根据其昵称，我们称之为“Nexus Zeta”。



## 二、简介

在过去的十年中，具备网络连接功能的设备数量已增长到两百多亿，并且随着时间的推移，这类设备也变得越来越智能。然而，虽然这些设备在便利性方面令人满意，但Check Point研究团队的最新研究成果表明，这些设备想要达到足够好的安全标准仍然有很长一段距离。



## 三、攻击活动

11月23日，Check Point研究人员注意到Check Point部署的一些传感器及蜜罐反馈了若干可疑的安全警告。进一步分析后，我们发现攻击者利用某家用路由器的未知漏洞，针对该设备的37215端口发起规模庞大的攻击。我们在全世界各地部署了多个传感器，这些传感器都检测到了同样的攻击模式，其中受攻击影响较大的国家分别为：美国、意大利、德国以及埃及等。

[![](https://p2.ssl.qhimg.com/t01ab767e60f7554a5d.png)](https://p2.ssl.qhimg.com/t01ab767e60f7554a5d.png)

我们的分析人员确认这一情况后，第一时间将漏洞信息[报告](http://www.huawei.com/en/psirt/security-notices/huawei-sn-20171130-01-hg532-en)给了相关厂商，以阻止攻击规模进一步扩张。

该厂商安全团队的沟通非常迅速也十分畅通，他们快速修复了这一漏洞，并向客户发布了更新补丁。与此同时，我们的团队也研发并公布了一种[IPS防护方案](https://www.checkpoint.com/defense/advisories/public/2017/cpai-2017-1016.html)，以确保Check Point的客户可以第一时间得到保护。

[![](https://p4.ssl.qhimg.com/t01fdf9fdd651d5ef5a.png)](https://p4.ssl.qhimg.com/t01fdf9fdd651d5ef5a.png)

图1. 全球攻击分布情况



## 四、0Day漏洞（CVE-2017-17215）

该家用网关设备采用了通用即插即用（Universal Plug and Play，UPnP）协议。根据TR-064技术报告标准，嵌入式设备中广泛使用该协议来实现无缝连接，可以简化家庭及企业环境中网络的搭建及部署工作流程。

TR-064的设计理念是服务于本地网络配置场景。比如，工程师可以通过TR-064在内部网络中实现基本的设备配置、固件升级等功能。

这款路由器实现了TR-064协议，并通过WAN口上的37215端口（UPnP）提供正常功能。

查看该设备的UPnP描述信息后，我们发现该设备支持名为`DeviceUpgrade`的一种服务类型。设备可以通过这种服务更新固件，具体过程是向“/ctrlt/DeviceUpgrade_1”这个地址提交请求（我们将该地址称之为controlURL），请求中包含`NewStatusURL`及`NewDownloadURL`两个元素。

远程管理员可以通过该漏洞在设备上执行任意命令，具体方法是将shell元字符“$()”注入`NewStatusURL`以及`NewDownloadURL`元素中，如下所示：

[![](https://p5.ssl.qhimg.com/t01d005b3d437dd16ef.png)](https://p5.ssl.qhimg.com/t01d005b3d437dd16ef.png)

图2. 攻击方法

执行这个操作后，设备会返回默认的UPNP消息，启动“升级”过程。

[![](https://p2.ssl.qhimg.com/t01921cd36c21de7607.png)](https://p2.ssl.qhimg.com/t01921cd36c21de7607.png)

图3. 攻击者注入命令，在存在漏洞的设备上下载并执行恶意载荷

[![](https://p3.ssl.qhimg.com/t013b6acb253c13ac96.png)](https://p3.ssl.qhimg.com/t013b6acb253c13ac96.png)

[![](https://p3.ssl.qhimg.com/t01eab5344e629c60a7.png)](https://p3.ssl.qhimg.com/t01eab5344e629c60a7.png)

图4. VirusTotal上该载荷之前（上图）及现在（下图）的检测情况



## 五、载荷工作过程

攻击载荷的功能非常简单。该僵尸程序（bot）的主要功能是使用自制的UDP或者TCP数据包来泛洪攻击目标。

开始执行时，僵尸程序会读取硬编码的域名信息，发起DNS请求来解析C&amp;C服务器的IP地址。随后，僵尸程序从DNS响应数据中提取相关地址信息，使用TCP协议尝试连接目标服务器的特定端口（7645端口，端口值已硬编码在样本程序中）。

与Mirai僵尸网络一样，该程序使用简单的异或（XOR）算法来解密DNS名称以及其他字符串，解密密钥为0x07。

此外，程序中还包含一个没有经过编码处理的字符串，这个字符串对应一个虚假的C&amp;C域名，永远不会被程序所使用：

[![](https://p1.ssl.qhimg.com/t019c915c0061453d3a.jpg)](https://p1.ssl.qhimg.com/t019c915c0061453d3a.jpg)

图5. 经过加密的真实域名及虚假的C&amp;C域名

C&amp;C服务器会返回泛洪攻击中使用的数据包数量及相应的参数信息：

[![](https://p3.ssl.qhimg.com/t0132d64af16c5901c5.png)](https://p3.ssl.qhimg.com/t0132d64af16c5901c5.png)

图6. 解析C&amp;C服务器返回的数据

此外，C&amp;C服务器还可以通过单个IP地址或者子网地址及掩码值来指定攻击目标范围，对应的C语言伪代码如下所示：

[![](https://p5.ssl.qhimg.com/t014ec63a164bf83be7.png)](https://p5.ssl.qhimg.com/t014ec63a164bf83be7.png)

图7. 针对某子网的随机IP地址生成过程

发送数据包后，僵尸程序不会等待被攻击目标的任何响应数据。

此外，僵尸程序文件中还包含大量未使用的字符串，其中既有经过混淆处理的字符串，也有明文字符串，然而这些字符串从来都不会被程序所使用。这些字符串很有可能是另一个僵尸程序或者先前版本的历史遗留数据。



## 六、C&amp;C通信

僵尸程序使用自定义的协议来与C&amp;C服务器通信。程序使用了两个硬编码的请求来接入服务器（这两个请求也可以用于僵尸节点标识）：

[![](https://p2.ssl.qhimg.com/t01c3e03bc08fb36a9f.jpg)](https://p2.ssl.qhimg.com/t01c3e03bc08fb36a9f.jpg)

图8. 硬编码的C&amp;C请求

[![](https://p4.ssl.qhimg.com/t01f89dbb34a693eba7.jpg)](https://p4.ssl.qhimg.com/t01f89dbb34a693eba7.jpg)

图9. C&amp;C请求样例

C&amp;C服务器的响应数据中包含DDoS攻击的相关参数。只有响应数据的前两个字节为`00 00`或者`01 07`，僵尸程序才会执行DDoS攻击，否则就不会采取任何行动。如下所示：

[![](https://p3.ssl.qhimg.com/t01257b16ba7c1c3ec2.jpg)](https://p3.ssl.qhimg.com/t01257b16ba7c1c3ec2.jpg)

图10. C&amp;C响应数据样例



## 七、IoC

**攻击服务器地址及域名：**

```
93.97.219
211.123.69
7.59.177
106.110.90
nexusiotsolutions[.]net.
nexuszeta1337@gmail[.]com
```

**攻击载荷**：

```
7a38ee6ee15bd89d50161b3061b763ea mips
f8130e86dc0fcdbcfa0d3b2425d3fcbf okiru.x86
fd2bd0bf25fc306cc391bdcde1fcaeda okiru.arm
```



## 八、幕后黑手

在分析这款恶意软件的过程中，就幕后黑手的专业水平方面我们提出过一些问题，但最后的答案并没有与我们预期的相符。

由于此次攻击流量据大，用到了未知的0Day漏洞，也使用了多个攻击服务器，因此一开始攻击者的真实身份是个不解之迷，人们猜测这种攻击可能与高级的国家行为有关，也可能与某些臭名昭著的网络犯罪团伙有关。

经过细致分析后，我们最终归纳出一个首要嫌疑犯：即昵称为“Nexxus Zeta”的一个犯罪分子，我们之所以使用这个昵称，原因在于攻击者在注册僵尸网络的某个C&amp;C域名（**nexusiotsolutions[.]net**）时，所使用的邮箱地址包含相关信息。

该邮件地址（**nexuszeta1337[@gmail](https://github.com/gmail)[.]com**）与C&amp;C域名有一些交集，因此我们怀疑这个地址并不是一次性邮件地址，可以根据该地址来揭晓攻击者的真实身份。当搜索Nexus Zeta 1337时，我们在HackForums上找到了一个活跃的成员，该成员的用户昵称为“Nexus Zeta”，自2015年8月起已经是HackForums的一份子。虽然这个人在这种论坛上活跃度很低，但他发表了几篇帖子，从这些帖子中我们并没有发现他的专业水平有多高。不过有趣的是，他最近关注的是如何建立起类似Mirai的IoT僵尸网络。

[![](https://p1.ssl.qhimg.com/t0115cad9912a874b0e.png)](https://p1.ssl.qhimg.com/t0115cad9912a874b0e.png)

图11. Nexus Zeta在HackForums上的某个帖子

“NexusZeta”在社交媒体上也颇为活跃，主要是在Twitter以及Github上，他在这两个平台上都公布了自己的IoT僵尸网络项目。实际上，这个人还将其Github账户关联到我们前面提到的某个恶意域名（**nexusiotsolutions[.]net**）。我们也找到了他所使用的Skype以及SoundCloud账户，使用人名为Caleb Wilson（caleb.wilson37 / Caleb Wilson 37），然而我们无法确定这个名字是否就是其真实姓名。

[![](https://p4.ssl.qhimg.com/t01f1f616ccc19f4f2b.png)](https://p4.ssl.qhimg.com/t01f1f616ccc19f4f2b.png)

图12. Nexus Zeta的Twitter账户

[![](https://p0.ssl.qhimg.com/t01c179d63095be04c3.png)](https://p0.ssl.qhimg.com/t01c179d63095be04c3.png)

图13. Nexus Zeta的Github账户

根据Nexus Zeta在HackForums上的活动轨迹，我们可以通过攻击者的视角找到一些有趣的信息。在11月23日至26日期间，当时我们的传感器已经检测到攻击者的恶意活动，与此同时，他也活跃在Hackforums上，发表了一个非常有趣的帖子（11月23日）：

[![](https://p1.ssl.qhimg.com/t0193630b87049c26aa.png)](https://p1.ssl.qhimg.com/t0193630b87049c26aa.png)

图14. Nexus Zeta在攻击之前发表的帖子

帖子内容为：

**“大家好，我想找人帮我编译mirai僵尸网络程序，听说成功编译后，就能达到每秒1Tb的攻击流量规模，所以请帮我搭建mirai telnet僵尸网络。”**

根据我们的调查结果，Nexus Zeta看起来似乎不像是我们最初设想的那样，是一个非常厉害的攻击者，而只是带有各种动机的业余爱好者，正在寻求他人的帮助。值得一提的是，我们并不清楚他如何找到利用这个0Day漏洞的具体方法。

尽管如此，在过去一年中，包括本次案例在内的多个攻击事件表明，当恶意软件源代码的泄露与IoT设备的脆弱性结合在一起时，技术并不娴熟的攻击者也可以借此造成灾难性的后果。



## 九、IPS以及反僵尸程序保护措施

我们的IPS以及反僵尸程序保护措施已经成功阻止了这次攻击活动，尽管其利用的是0Day漏洞。我们将继续监控并研究其他在野的任何攻击行为。

**IPS 0Day保护措施：**

HG532路由器远程代码执行

**反僵尸程序保护措施：**

Linux.OKIRU.A<br>
Linux.OKIRU.B



## 十、参考资料

[https://www.checkpoint.com/defense/advisories/public/2017/cpai-2017-1016.html](https://www.checkpoint.com/defense/advisories/public/2017/cpai-2017-1016.html)<br>[http://www.huawei.com/en/psirt/security-notices/huawei-sn-20171130-01-hg532-en](http://www.huawei.com/en/psirt/security-notices/huawei-sn-20171130-01-hg532-en)
