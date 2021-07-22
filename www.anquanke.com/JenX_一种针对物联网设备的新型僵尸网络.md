> 原文链接: https://www.anquanke.com//post/id/97516 


# JenX：一种针对物联网设备的新型僵尸网络


                                阅读量   
                                **116027**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Pascal Geenens，文章来源：blog.radware.com
                                <br>原文地址：[https://blog.radware.com/security/2018/02/jenx-los-calvos-de-san-calvicie/](https://blog.radware.com/security/2018/02/jenx-los-calvos-de-san-calvicie/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01e31194e18cd54104.jpg)](https://p3.ssl.qhimg.com/t01e31194e18cd54104.jpg)<br>
近期，又有一款新型的僵尸网络开始攻击物联网设备了。这种僵尸网络名叫JenX，它能够利用托管服务器来寻找并感染新的目标用户。在攻击过程中，它会利用物联网僵尸网络中近期比较热门的已知安全漏洞，比如说下面这两个：
- -CVE-2014-8361：“Realtek SDK Miniigd UPnP SOAP命令执行”漏洞以及相关利用；
- -CVE-2017–17215：“华为HG532路由器-任意命令执行”漏洞以及相关利用；
这两种漏洞利用向量早在Satori僵尸网络被曝光时就已经被人们所知晓了，而其中的相关漏洞利用代码基于的是“Janit0r”（BrickerBot的开发者）近期在Pastebin帖子中公开的代码。除此之外，这款恶意软件还使用了跟PureMasuta类似的技术，而PureMasuta恶意软件的源代码已经公开在了暗网中一个需要邀请码才可访问的地下论坛。<br>
在对JenX进行研究和分析的过程中，我们发现了一个托管在域名‘sancalvicie.com’之下的C2服务器，而这个服务器是一台托管了游戏《侠盗猎车手之圣安地列斯》的多玩家mod服务器，并且它在服务器端还部署了DDoS（分布式拒绝服务攻击）服务。下面给出的截图就是托管在SanCalvicie.com上的“DDoS即服务”的详细信息以及价格：

[![](https://p2.ssl.qhimg.com/t0153ad0611e1899032.png)](https://p2.ssl.qhimg.com/t0153ad0611e1899032.png)<br>
SAMP选项可以给《侠盗猎车手之圣安地列斯》提供多用户游戏服务，并且还明确提到了针对Source游戏引擎查询以及其他类型DDoS攻击的保护服务。<br>
Corriente Divina选项被描述为“上帝的愤怒会降临到你所提供的IP地址身上”。也就是说，该服务可以对客户所提供的IP地址进行DDoS攻击，攻击带宽约为90-100Gbps，攻击向量包括Source引擎查询以及32字节泛洪攻击。TS3脚本以及“Down OVH”选项很可能指的是针对托管服务OVH（OVH是一家云托管服务提供商，并且从2016年9月份开始，这家服务商就一直受到了原始Mirai僵尸网络的攻击困扰）的攻击服务。需要注意的是，OVH同样可以给客户提供多游戏玩家服务器的托管服务（Minecraft），而它也是Mirai攻击的主要目标。<br>
上面这些信息是我初次调查时所收集到的，当我准备编写这篇文章并再次访问该网站以收集材料时，我发现该网站的DDoS攻击服务描述竟然修改了。说得更准确一点，他们升级了自己的DDoS服务。下图显示的是SanCalvicie.com网站升级后的DDoS攻击服务描述信息：

[![](https://p4.ssl.qhimg.com/t01d0c38b4658bfa7eb.png)](https://p4.ssl.qhimg.com/t01d0c38b4658bfa7eb.png)<br>
需要注意的是上图中用红色框框标注的部分：“BOTS”以及增加后的DDoS攻击流量290-300Gbps。由此看来，攻击者似乎对他们新上线的僵尸网络非常有信心，而这个新型的僵尸网络只部署上线了两天左右的时间。



## 漏洞利用

在2018年1月30号，我们的物联网蜜罐记录下了多个来自不同服务器的漏洞利用尝试，而这些服务器均位于欧洲地区多个不同的主机托管中心。其中，基于CVE-2014-8361的漏洞利用代码会尝试通过向目标主机端口52869发送三种不同的SOAP POST请求（使用URL/picsdesc.xml）来实现远程代码执行。

[![](https://p2.ssl.qhimg.com/t01c4b778e02994497e.png)](https://p2.ssl.qhimg.com/t01c4b778e02994497e.png)<br>
CVE-2017–17215所基于的漏洞利用代码会对目标主机端口37215发送POST请求（/ctrlt/DeviceUpgrade_），并使用一系列不同的命令序列在目标主机中下载并运行恶意软件。首先，它会尝试除掉当前主机中驻留的任何bot（如果有的话），这样可以避免出现资源竞争：

[![](https://p1.ssl.qhimg.com/t0131894d4ee3206272.png)](https://p1.ssl.qhimg.com/t0131894d4ee3206272.png)

该恶意软件的代码名叫“jennifer”，恶意代码都是从相同的服务器（5.39.22.8）下载的，但是托管恶意代码的服务器跟托管漏洞利用代码的服务器供应商是不同的。<br>
下载服务器托管了针对MIPS、ARM和x86的恶意代码样本，而且这些代码近期都被大量用户下载过：

[![](https://p3.ssl.qhimg.com/t01d841e5871e6a4531.png)](https://p3.ssl.qhimg.com/t01d841e5871e6a4531.png)<br>
经过分析之后，我们得到的恶意代码IoC如下所示：

[![](https://p0.ssl.qhimg.com/t01263582e5b2949aa1.png)](https://p0.ssl.qhimg.com/t01263582e5b2949aa1.png)

JenX跟我们在去年所见到的很多物联网僵尸网络有些不同，这个僵尸网络使用了服务器来进行主机扫描以及漏洞利用。但是包括Mirai、Hajime、Persirai、Reaper、Satori和Masuta在内的几乎所有僵尸网络进行的都是分布式扫描和漏洞利用。也就是说，每一台受感染主机都会各自单独寻找新的目标主机，而这种分布式扫描机制可以让僵尸网络内的受感染主机数量呈指数式增长，但这需要牺牲恶意软件的灵活性和复杂性作为代价。<br>
如果没有扫描和漏洞利用Payload的话，bot代码本身会变得非常简单，而且体积也会很小（易于传播）。与此同时，“中心化”的扫描和漏洞利用功能可以给维护人员更加方便地增添或更新功能模块。而且这些功能都可以使用类似Python或Go这种更高级的语言来开发，因为这些语言的模块和代码库生态系统比较丰富，而且现成的东西也很多。但如果涉及到扫描功能和漏洞利用功能的话，还是需要使用C语言或者其他的编译语言来实现。<br>
研究人员表示，如果无法访问命令控制服务器的话，那么这种“中心化”的结构会让研究人员难以估计这个僵尸网络的规模大小。除此之外，跟分布式的僵尸网络相比，JenX的缺点就是感染主机数量增长得比较慢，甚至比线性增长速度还要慢。<br>
下图显示的是其中一台托管了Realtek漏洞利用代码的服务器状态信息：

[![](https://p5.ssl.qhimg.com/t0191f936a9e35726bf.png)](https://p5.ssl.qhimg.com/t0191f936a9e35726bf.png)

## 恶意软件分析

运行之后，Jennifer代码将会启用三个进程，并在退出之前将下列信息写入到终端：

[![](https://p2.ssl.qhimg.com/t01169fc1c578d40ac1.png)](https://p2.ssl.qhimg.com/t01169fc1c578d40ac1.png)<br>
跟Mirai一样，这三个进程名称经过了混淆处理，而且恶意软件还采用了一些反调试检测方法来防止恶意代码在调试器中被分析。进程信息以及相对应的端口+协议如下所示：

[![](https://p1.ssl.qhimg.com/t012496f9056a5381fe.png)](https://p1.ssl.qhimg.com/t012496f9056a5381fe.png)<br>
代码中经过混淆处理的字符串如下所示：<br>[![](https://p1.ssl.qhimg.com/t0117c73aa2e6e162e1.png)](https://p1.ssl.qhimg.com/t0117c73aa2e6e162e1.png)<br>
为了在不需要进行逆向分析的情况下，找到混淆算法和密钥，我们准备从上面这个有58个字符的字符串入手，具体请参考下图所示的C语言伪代码：

[![](https://p2.ssl.qhimg.com/t01d5f6cd3c932352b6.png)](https://p2.ssl.qhimg.com/t01d5f6cd3c932352b6.png)<br>
使用Python进行一些非常基本的密码学分析之后，我们发现这里的混淆算法其实就是简单的异或计算（固定密钥为0x45）：

[![](https://p3.ssl.qhimg.com/t010fed576590587f6d.png)](https://p3.ssl.qhimg.com/t010fed576590587f6d.png)<br>
因此，反混淆处理之后的字符串明文信息如下所示：

[![](https://p5.ssl.qhimg.com/t019b6cdc052af30f7e.png)](https://p5.ssl.qhimg.com/t019b6cdc052af30f7e.png)<br>
但现在的问题是怎么才能得到IP地址80.82.70.202背后的C2服务器主机名，我们所得到的僵尸网络属性信息如下：

[![](https://p5.ssl.qhimg.com/t0180bc472237f92683.png)](https://p5.ssl.qhimg.com/t0180bc472237f92683.png)<br>
包含了主机名的字符串可以从下图所示的伪代码中获取到：

[![](https://p5.ssl.qhimg.com/t0193e7a8eff4a90595.png)](https://p5.ssl.qhimg.com/t0193e7a8eff4a90595.png)<br>
这里使用之前得到的0x45固定密钥并不能计算出我们所期望的结果，但是经过暴力破解攻击之后我们发现密钥0x22可以计算出C2服务器的主机名，即‘skids.sancalvicie.com’：

[![](https://p4.ssl.qhimg.com/t01382747af8f7f47b4.png)](https://p4.ssl.qhimg.com/t01382747af8f7f47b4.png)<br>
验证主机名：<br>[![](https://p3.ssl.qhimg.com/t0149a25cada07d1c0e.png)](https://p3.ssl.qhimg.com/t0149a25cada07d1c0e.png)<br>
由此可以看出，这个域名是一个名叫‘Calvos S.L.’的组织注册的。



## C2协议

在运行过程中，恶意软件会跟硬编码的C2服务器建立TCP会话（端口127，主机名为‘skids.sancalvicie.com’），然后向命令行发送二进制初始序列“0x00 0x00 0x00 0x01 0x07”以及相应参数来运行恶意代码。在“Realtek漏洞利用”场景下，相应参数就是“realtek”了。下图显示的是bot跟C2服务器之间的TCP会话信息（红色部分为bot）：

[![](https://p4.ssl.qhimg.com/t012a17ad8ebabcc98a.png)](https://p4.ssl.qhimg.com/t012a17ad8ebabcc98a.png)<br>
C2服务器端同样提供了命令行接口，并且同样监听的是端口127。当会话成功建立后的出事字节不是0x00时，服务器会要求输出登录凭证：

[![](https://p5.ssl.qhimg.com/t017b6bfa995d538acb.png)](https://p5.ssl.qhimg.com/t017b6bfa995d538acb.png)



## 总结

目前为止，两个欧洲地区的服务器提供商已经下线了托管在他们数据中心的漏洞利用服务器，但是该恶意软件其他的服务器仍处于活动中。因此，这个僵尸网络仍在运作中，部分服务器的下线只会影响它的规模扩张速度而已。<br>
由于JenX选择使用中心化的主机扫描以及漏洞利用模式，因此攻击者的灵活性将大大提升。如果服务器被转移到了暗网中的话，我们就更难去追踪JenX攻击者的活动行踪了。在去年，我们只发现了BrickerBot这一种采用了跟JenX相似技术的僵尸网络，但这有可能是物联网僵尸网络的一种发展趋势，所以我们今后可能会看到越来越多的僵尸网络采用这种技术。
