> 原文链接: https://www.anquanke.com//post/id/97242 


# IoT Reaper：物联网世界的新威胁


                                阅读量   
                                **127611**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者embedi，文章来源：embedi.com/blog
                                <br>原文地址：[https://embedi.com/blog/grim-iot-reaper-1-and-0-day-vulnerabilities-at-the-service-of-botnets/](https://embedi.com/blog/grim-iot-reaper-1-and-0-day-vulnerabilities-at-the-service-of-botnets/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0105a56e419c570205.png)](https://p0.ssl.qhimg.com/t0105a56e419c570205.png)



## 写在前面的话

在2017年10月19日，整个物联网世界都颤抖了，因为现在出现了一种新型的大规模僵尸网络，而研究人员将这个物联网世界的新威胁称为“Reaper”。



## IoT Reaper

研究人员表示，Reaper是非常恐怖的，甚至比之前臭名昭著的Mirai僵尸网络还要可怕。根据360 Netlab提供的数据，Reaper已经成功感染了大约三万台智能设备，而现在仍然有两百多万台设备可能会受到攻击。<br>
可能很多人都知道，Mirai在感染目标设备时利用的是安全漏洞以及弱密码。而Reaper饥渴难耐的“大刀”则更加锋利，因为Reaper僵尸网络可以利用多款物联网设备中的数十种安全漏洞，其中受影响的产品包括D-Link、Wi-Fi CAM、JAWS、Netgear、Linksys和AVTECH等厂商旗下的路由器和摄像头。而且随着时间的推移，这把“大刀”也变得更加锋利了：由于目标物联网设备长期不更新，该僵尸网络的规模也正在急速扩张。<br>
Reaper所能利用的安全漏洞来源于开发人员在设备研发过程中的粗心大意，即使Reaper攻击者懒得对物联网设备以及相关漏洞进行深入研究，他们同样可以轻松利用这些漏洞。虽然Reaper的攻击链主要由一系列不重要的低危漏洞组成，但如果设计有效的话，这些漏洞将允许攻击者获取目标设备的完整访问权限。<br>
其中，Reaper所能利用的绝大多数安全漏洞都是Web应用程序以及Web资源中常见的漏洞，而且这些类型的安全漏洞都是物联网设备安全研究专家、漏洞赏金猎人以及安全分析人员最关注的漏洞。<br>
虽然Web资源的管理员能够轻松快速地修复漏洞并更新自己的资源，但如果场景转移到物联网设备的身上，那问题就没那么简单了。即使物联网设备的开发者发布了一个特定的安全补丁，物联网设备的用户也不会及时更新自己的设备。而调查数据显示，只有少部分用户会在更新补丁发布之后的很长一段时间里安装更新补丁。<br>
Reaper可以利用的漏洞种类是非常广的，而且有部分漏洞早在2013年就已经被公之于众了，比如说：
- [Linksys E1500/E2500中的多个安全漏洞；](http://www.s3cur1ty.de/m1adv2013-004)
- [D-Link DIR-600和DIR-300（rev B）的多个安全漏洞；](http://www.s3cur1ty.de/m1adv2013-003)
下图显示的是恶意软件中用于检测D-link路由器（95b448bdf6b6c97a33e1d1dbe41678eb）型号的部分代码：<br>[![](https://p2.ssl.qhimg.com/t01b1a6e7fb7e8e3282.png)](https://p2.ssl.qhimg.com/t01b1a6e7fb7e8e3282.png)<br>
然后相关型号设备中的安全漏洞都已经被研究人员修复了，但是由于很多设备的固件版本并没有更新，因此Reaper目前仍然可以对这些设备进行攻击。<br>
经过研究之后我们还发现，Reaper还可以利用无线IP摄像头（P2P）WiFi Cam中的安全漏洞（在2017年3月份被检测出的漏洞）。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://embedi.com/wp-content/uploads/2018/01/reaper_infection.gif)<br>
根据Embedi的研究报告显示，Reaper所能利用的安全漏洞此前都已经分配了CWE编号。下图显示的是这些CWE漏洞以及存在相同类型漏洞设备之间的相关性：<br>[![](https://p2.ssl.qhimg.com/t019c1809f4e16059b0.png)](https://p2.ssl.qhimg.com/t019c1809f4e16059b0.png)<br>
根据上图中所显示的漏洞类型，很明显，这些漏洞都属于应用安全的范畴。换句话来说，要么是开发人员在设备研发过程中所采用的安全开发生命周期措施不够有效，要么就是他们压根就没有采用任何的安全检测措施，而这样就导致了现在僵尸网络如雨后春笋般涌现了出来。更加重要的是，即便是开发人员拼尽全力去编写安全可靠的代码并采取多重加密机制，现存的这些安全问题也不是那么容易能够解决的。<br>
这些安全漏洞很少会出现在桌面端应用程序的身上，而且就算有也不会那么容易被利用，因为桌面操作系统采取了更多系统级的安全保护措施。原因是显而易见的：一般来说，物联网设备的开发人员并不会过多地去参考同行现有的经验和资源，但对于恶意软件的开发者来说，情况就恰恰相反了。比如说，Reaper僵尸网络就配备了Lua解释器，这样就可以迅速扩展Reaper恶意软件的功能了。<br>
Reaper样本（ca92a3b74a65ce06035fcc280740daf6）中的Lua脚本代码片段（for SMPT）：<br>[![](https://p1.ssl.qhimg.com/t01cf15e7419323aae4.png)](https://p1.ssl.qhimg.com/t01cf15e7419323aae4.png)<br>
另一个例子就是Satori，Satori这个僵尸网络是基于Mirai的源代码开发出来的。而这两个僵尸网络最大的不同之处就在于，Satori使用了一种改进版的传播方法，并且还增加了针对华为HG532型号路由器的0 day漏洞利用代码。根据The Hacker News的报道，目前大约有二十多万台设备已经被成功感染了，除此之外，漏洞利用代码以及Mirai僵尸网络的源代码都是可以直接从网络上公开获取的。<br>
因此，如果有人想要创建一个僵尸网络的话，他只需要去网上搜索目前使用范围最广的设备，然后再寻找设备中相应漏洞的利用代码，最后再配合上开源的僵尸网络代码，他们就能够开发出一个适用于当前网络环境并且功能强大的僵尸网络了。考虑到目前绝大多数设备的应用安全性都十分脆弱，所以攻击者寻找0 day漏洞利用代码并将其整合进现有僵尸网络中难度就跟炒一碗蛋炒饭一样简单（好像也不简单）。如果开发人员无法提升物联网设备的应用安全等级，那么“数百万设备被感染”的新闻将会更加频繁地出现在媒体头条。<br>
就此看来，未来针对物联网设备的僵尸网络开发环境可能就会是这样的了：<br>[![](https://p3.ssl.qhimg.com/t0173cbb7b1eaee9271.png)](https://p3.ssl.qhimg.com/t0173cbb7b1eaee9271.png)<br>
这里需要提醒大家一下：在早期版本的Mirai僵尸网络中，其目的是为了对商业竞争对手的服务器进行分布式拒绝服务攻击（DDoS）。因此我们可以认为，这个僵尸网络的背后很可能有一个熟练且经验丰富的开发团队。<br>
终端用户如何保护自己的安全？
1. 购买那种能够自动更新固件的设备；
1. 定期更新自己设备的系统固件以及软件；
1. 经常关注最新出现的物联网安全威胁；
## IoT Reaper所能利用的安全漏洞

漏洞介绍图如下所示：<br>[![](https://p5.ssl.qhimg.com/t01bf0015395c2c5ff2.png)](https://p5.ssl.qhimg.com/t01bf0015395c2c5ff2.png)

### <a class="reference-link" name="D-Link%20850L%E6%BC%8F%E6%B4%9E%EF%BC%9A"></a>D-Link 850L漏洞：
1. 通过WAN和LAN实现远程代码执行（CWE-284）；
1. 通过WAN和LAN在未经身份验证的情况下远程获取信息（CWE-200）；
1. 通过LAN以管理员权限在未经授权的情况下远程运行任意软件（CWE-284）；
### <a class="reference-link" name="%E6%97%A0%E7%BA%BFIP%E6%91%84%E5%83%8F%E5%A4%B4%EF%BC%88P2P%EF%BC%89%20WIFICAM%E6%BC%8F%E6%B4%9E%EF%BC%9A"></a>无线IP摄像头（P2P） WIFICAM漏洞：
1. 通过Telnet访问管理员账号 （CWE-798）；
1. 获取存储在固件中的RSA证书以及私钥（CWE-321）；
1. 使用管理员权限实现远程代码执行（CWE-78）；
1. 在未经RTSP服务器验证的情况下对数据流进行监控（CWE-287）；
1. 在tcpdump工具的帮助下对流量数据继续监控（CWE-200）；
### <a class="reference-link" name="DVR%E6%BC%8F%E6%B4%9E"></a>DVR漏洞
1. 默认用户名和密码均为空 （CWE-521）；
1. 未对cookie内容进行验证，将允许攻击者绕过Web认证（CWE-565）；
1. 攻击者可以打开uboot控制台，并将设备切换到单用户模式，并在未经认证的情况下执行任意命令（CWE-284）；
1. 通过使用内置的Shell，未经认证的攻击者可以使用Telnet （CWE-553）；
### <a class="reference-link" name="Netgear%E8%B7%AF%E7%94%B1%E5%99%A8%E6%BC%8F%E6%B4%9E"></a>Netgear路由器漏洞
1. 在未经认证的情况下，利用命令行工具实现远程代码执行（CWE-78）；
<li>
<a class="reference-link" name="Vacron%E7%9B%91%E6%8E%A7%E6%91%84%E5%83%8F%E5%A4%B4%E6%BC%8F%E6%B4%9E"></a>Vacron监控摄像头漏洞</li>
1. board.cgi中没有对输入命令进行过滤，将允许攻击者运行cmd并执行任意命令（CWE-78）；
<li>
<a class="reference-link" name="Netgear%20DGN1000%E5%92%8CDGN2200%20v1%E8%B7%AF%E7%94%B1%E5%99%A8%E6%BC%8F%E6%B4%9E"></a>Netgear DGN1000和DGN2200 v1路由器漏洞</li>
1. 内置Web服务器不会对包含了«currentsetting.htm» 的URL进行验证，攻击者可以利用该漏洞绕过服务器的验证机制并在设备上使用管理员权限执行任意代码（CWE-20）；
<li>
<a class="reference-link" name="Linksys%20E1500/E2500%E8%B7%AF%E7%94%B1%E5%99%A8%E6%BC%8F%E6%B4%9E"></a>Linksys E1500/E2500路由器漏洞</li>
1. ping_size参数没有被检测，攻击者可以输入并执行任意Shell命令 （CWE-78）；
1. 攻击者可以直接修改当前账户的密码 （CWE-620）；
### <a class="reference-link" name="D-Link%20DIR-600%E5%92%8CDIR-300%E6%BC%8F%E6%B4%9E"></a>D-Link DIR-600和DIR-300漏洞
1. 命令行工具既没有访问限制，也没有输入验证，这将允许攻击者输入并执行任意命令。比如说，运行telnetd （CWE-78）；
1. 攻击者可以直接修改账户密码（CWE-620）；
1. 密码直接以明文形式存储 （CWE-256）；
1. 未经授权的攻击者可直接访问设备的型号、固件版本、语言配置、MAC地址以及Linux内核 （CWE-200）；
1. 访问操作系统信息 （CWE-200）；