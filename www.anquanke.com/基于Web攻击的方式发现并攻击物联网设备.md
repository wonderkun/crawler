> 原文链接: https://www.anquanke.com//post/id/169184 


# 基于Web攻击的方式发现并攻击物联网设备


                                阅读量   
                                **191242**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者netsparker，文章来源：netsparker.com
                                <br>原文地址：[https://www.netsparker.com/blog/web-security/discovering-hacking-iot-devices-using-web-based-attacks/](https://www.netsparker.com/blog/web-security/discovering-hacking-iot-devices-using-web-based-attacks/)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p0.ssl.qhimg.com/t0118296b452fdb1dc3.jpg)](https://p0.ssl.qhimg.com/t0118296b452fdb1dc3.jpg)



## 前言

近二十年来，DNS重绑定（DNS rebinding）攻击一直是讨论的话题。尽管浏览器厂商做出了努力，但仍然无法找到一个能稳定抵御这些攻击的防御系统。据说这类问题八年前就已经被修复了。但是这类攻击通过新的攻击向量再次出现。

总的来说，可以肯定未来的黑客活动将通过多个现有攻击组合形成新的攻击向量。这些新攻击向量的一个很好的例子就是攻击加密货币钱包的DNS重绑定攻击。

在本文中，我们讨论了Princeton（普林斯顿大学）和UC Berkeley（加州大学伯克利分校）关于基于web的方式攻击物联网设备的研究，这些攻击会导致设备被黑客发现、攻击和接管。研究于2018年8月发表。



## 设备与黑客发现和攻击物联网设备的方法

研究人员的目标是测试15个物联网设备。这些设备中只有七台有本地HTTP服务器，所以研究的重点放在它们上，它们包括：Google Chromecast、Google Home、一台智能电视、一个智能开关和三个摄像头。

使用的攻击方法是：
- 欺骗受害人，诱导他们访问攻击者控制的网站。
- 在受害者的本地网络上发现物联网设备。
- 通过基于web的攻击控制设备。


## 攻击的持续时间

从技术上讲，这不是新的攻击向量。研究报告引用了之前的研究，发现攻击者使用这些攻击向量平均需要一分钟才能获得结果。奇怪的是，一项著名的研究结果([What You Think You Know About the Web is Wrong](What%20You%20Think%20You%20Know%20About%20the%20Web%20is%20Wrong))显示，55%的用户花在网站上的时间不超过15秒。看来大多数用户不会受到物联网漏洞的影响。

但是在普林斯顿大学和加州大学伯克利分校的研究中，研究人员明显缩短了攻击的持续时间。研究人员表示使用他们发现的方法，可以比之前的研究更快地发现和访问本地网络中的设备。但是Chrome除外，因为它缓存DNS请求，如果TTL低于某个阈值，则忽略TTL。需要注意的是，隔离区(DMZ，防火墙内的内部网络)中的设备通常被认为是安全的，因为用户假设外部是无法访问这些设备的。但是，通过这里描述的攻击，攻击者可以访问受害者内部网络中的浏览器。



## 发现HTTP端点

研究人员通过将这些设备连接到Raspberry Pi的无线接入点来分析这些设备。观察并分析了从设备发送和接收的数据包，以及与每个设备绑定的移动应用发送和接收的数据包。通过分析发现了35个GET请求端点和8个POST请求端点。这些端点用于识别发现阶段中的IP地址。



## 研究的阶段

研究人员通过两个不同的阶段进行研究，即发现阶段和接入阶段：
- 发现阶段的目标是在本地网络上找到浏览器上包含HTML5元素的物联网设备。
- 接入阶段的目标是使用DNS重绑定和已发现的IP地址访问HTTP端点。
### <a class="reference-link" name="%E5%8F%91%E7%8E%B0%E9%98%B6%E6%AE%B5%EF%BC%9A%E8%AF%86%E5%88%AB%E7%89%A9%E8%81%94%E7%BD%91%E8%AE%BE%E5%A4%87"></a>发现阶段：识别物联网设备
- 使用WebRTC获取本地IP地址。
- 通过81端口向IP范围内的所有IP地址发送请求。由于81端口通常不被占用，活动设备将立即响应一个TCP RST数据包。而对于IP范围内的非活动设备，请求数据包将超时。
- 每个活动IP地址都接收到最初阶段使用HTML5为35个GET端点收集的请求。根据返回的错误消息信息，攻击脚本将识别IP地址是否与七个设备中的任意一个匹配。
研究计划使用三种不同的操作系统(Windows 10、MacOS和Ubuntu)和四种不同的浏览器(Chrome、Firefox、Safari、MicrosoftEdge)。然而只有Chrome和Firefox这两个浏览器适合这项研究。因此不使用Safari和Edge浏览器，因为根据([基于Web的方式对本地物联网设备的发现和控制的攻击](https://iot-inspector.princeton.edu/iot-sigcomm-18/SIGCOMM_IoT_S_P_2018__Redacted_.pdf))：

```
在Safari上，所有的FETCH请求都超时了，导致攻击脚本将所有IP地址识别为不活动。而在Edge浏览器上，脚本可以使用FETCH请求正确识别活动IP地址，但Edge没有公开详细的HTML5错误消息，所以攻击脚本无法识别Edge上的任何设备。
```

### <a class="reference-link" name="%E6%8E%A5%E5%85%A5%E9%98%B6%E6%AE%B5%EF%BC%9A%E6%8E%A7%E5%88%B6%E7%89%A9%E8%81%94%E7%BD%91%E8%AE%BE%E5%A4%87"></a>接入阶段：控制物联网设备
1. 受害者访问攻击者控制的域名(domain.tld)，浏览器执行在攻击者站点上找到的恶意JavaScript代码。域名仍然解析为攻击者的服务器IP。
1. 恶意脚本请求domain.tld上的另一个资源，该资源仅存在于攻击者服务器上。
1. 如果受害者的本地DNS缓存仍然解析为攻击者的远程IP，则对/hello.php的请求将返回字符串“hello”，并重复步骤2。
1. 但是如果受害者缓存中的domain.tld过期，则将向攻击者发送新的DNS查询。
1. 最后将返回从发现阶段中获得的本地IP，而不是攻击者的远程IP，/hello.php不会使用字符串“hello”进行响应，而是使用不同的内容，如404错误，它告诉恶意脚本DNS重绑定攻击已经成功。
通过这次攻击，恶意脚本绕过了浏览器同源策略（[Same-Origin Policy](https://www.netsparker.com/blog/web-security/introducing-same-origin-policy-whitepaper/)），并获得了对运行在设备上的Web应用的访问权限。现在攻击者已经可以在Google Chromecast、Google Home、智能电视和智能开关设备上执行重新启动或启动视频/音频文件。



## 如何防止针对物联网设备的DNS重绑定攻击

研究人员称，用户、浏览器厂商、物联网厂商和DNS提供商需要采取预防措施，以避免[DNS重绑定](https://blog.hacker.af/how-your-ethereum-can-be-stolen-using-dns-rebinding)攻击。以下是研究给出的一些措施：
1. 用户可以在浏览器上禁用WebRTC，并防止泄露私有IP。攻击者将能够通过向私有IP范围内的所有*.1地址(路由器地址)发送请求来发现用户的私有IP。
1. 攻击者假设所有物联网设备的IP范围与受害者的PC具有相同的IP范围。用户可以通过配置路由器的DHCP服务器，在另一个子网(如 /16)上分配IP地址。
1. 用户可以安装dnsmasq，通过从DNS响应中删除RFC 1918地址来防止DNS重绑定攻击。用户还可以使用dnsmasq的OpenWRT路由器。
1. 物联网厂商可以在发送到Web接口的请求中控制Host标头。如果没有符合[RFC 1918](https://tools.ietf.org/html/rfc1918)的私有IP，则可以阻止访问。
1. DNS提供商可以使用像dnswall这样的机制从DNS响应中筛选私有IP。
1. 浏览器厂商可以开发限制公网访问私有IP范围的扩展程序。
<li>
</li>
## 更多资料

有关本文中讨论的普林斯顿大学和加州大学伯克利分校的研究的更多信息，请参见[基于Web的发现和控制本地物联网设备的攻击](https://iot-inspector.princeton.edu/iot-sigcomm-18/SIGCOMM_IoT_S_P_2018__Redacted_.pdf)。

要了解关于本地网络中应用和设备上基于Web的攻击向量的更多信息，请参见[开发者计算机上易受攻击的Web应用允许黑客绕过公司防火墙](https://www.netsparker.com/blog/web-security/vulnerable-web-applications-developers-target/)。

作者，NetspkerSecurity研究人员：Ziyahan Albeniz，Sven Morgenroth，Umran Yildirimkaya。
