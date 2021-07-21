> 原文链接: https://www.anquanke.com//post/id/84953 


# 【技术分享】仅使用5美元设备，在锁定的计算机中植入Web后门（含演示视频）


                                阅读量   
                                **69783**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：samy
                                <br>原文地址：[https://samy.pl/poisontap/](https://samy.pl/poisontap/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t018dfb55a0fdef0b64.png)](https://p5.ssl.qhimg.com/t018dfb55a0fdef0b64.png)

****

**翻译：**[**WisFree**](http://bobao.360.cn/member/contribute?uid=2606963099)

**稿费：160RMB（不服你也来投稿啊！）**

******投稿方式：发送邮件至**[**linwei#360.cn******](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿******



**PoisonTap**

PoisonTap是一款制作成本仅为5美元的设备，它主要使用的是极客圈著名的[Raspberry Pi Zero](http://amzn.to/2eMr2WY)（树莓派）。只需要一根[USB数据线](https://amzn.to/2fUMdah)和一张[SD存储卡](https://amzn.to/2fWgKsd)，我们就可以将其当作[USB Armory](https://inversepath.com/usbarmory)和[LAN Turtle](https://lanturtle.com/)这样的USB设备来使用了。

[![](https://p1.ssl.qhimg.com/t0170dc1a3c3554abf0.gif)](https://p1.ssl.qhimg.com/t0170dc1a3c3554abf0.gif)

**发布时间：**2016年11月16日

**源代码下载地址：**[https://github.com/samyk/poisontap](https://github.com/samyk/poisontap)

**联系方式：**[@SamyKamkar](https://twitter.com/samykamkar) // [https://samy.pl](https://samy.pl/)

当PoisonTap（Raspberry Pi Zero + Node.js）插入一台受密码保护的计算机（锁定状态）之后，它将会进行以下操作：

1. 模拟一个USB接口的以太网设备（或Thunderbolt接口）；

2. 劫持设备上的所有网络通信流量；

3. 利用Web浏览器嗅探并存储Alexa网站排名前十万的网站HTTP cookie和session（会话）；

4. 将网络内部路由暴露给攻击者，攻击者将可以通过WebSocket和DNS rebinding技术远程访问目标路由；

5. 在大量网站的HTTP cache中安装持久化的Web后门；

6. 允许攻击者远程控制用户发送HTTP请求，并强行将用户cookies信息发送至攻击者所控制的服务器；

7. 所有操作可以在一台锁定的计算机中运行，无需进行解锁操作；

8. 移除PoisonTap设备之后，后门和远程访问权限仍然存在；

PoisonTap可以绕过以下安全机制：

1. 计算机锁屏密码；

2. 路由表优先级和网络接口服务次序；

3. 同源策略；

4. X-Frame-Options；

5. HttpOnly Cookies；

6. SameSite cookie属性；

7.  双因素/多因素身份验证（2FA/MFA）；

8. DNS Pinning；

9. 跨域资源共享（CORS）

10. HTTPS cookie的安全保护功能；

<br>

**演示视频**





**PoisonTap的工作机制**

PoisonTap可以利用目标设备或网络中现有的可信机制（例如USB、Thunderbolt、DHCP、DNS和HTTP）来引起一系列滚雪球式的连锁反应。它可以获取到目标网络的访问权，安装半持久化的恶意后门，并从目标系统中提取数据。

[![](https://p4.ssl.qhimg.com/t01fa197424851706e3.gif)](https://p4.ssl.qhimg.com/t01fa197424851706e3.gif)

简而言之，PoisonTap可以执行下列操作：

**网络劫持**

1. 将PoisonTap插入一台处于锁定状态的计算机；

2. PoisonTap会模拟出一个以太网设备。默认配置下，Windows、macOS和Linux都可以识别以太网设备，然后自动将该设备加载为低优先级的网络设备并向其发送DHCP请求，即使计算机当前处于锁定状态。

3. PoisonTap会响应DHCP请求，然后向计算机提供一个IP地址。但是这个DHCP响应会告诉计算机整个IPv4地址空间都属于PoisonTap本地网络，而不仅仅只是其中的一部分子网，例如192.168.0.0-192.168.0.255。

-一般来说，插入其他的网络设备之后是不会影响计算机的网络通信的，因为新插入的设备优先级会比之前可信任的网络设备优先级低，因此新设备无法取代当前网络流量的网关。但是…

-由于“局域网流量”的优先级高于“互联网流量”的优先级，因此路由表、网关优先级和网络接口服务顺序之类的安全机制都将会被绕过。

-PoisonTap正是利用了这种机制，因为“低优先级网络设备的子网”其优先级要高于“高优先级网络设备的网关”。

-这也就意味着，如果流量的目标地址为1.2.3.4，那么PoisonTap就可以捕获到这个流量，因为PoisonTap的本地网络的子网中包含1.2.3.4。

-正因如此，即便计算机中使用了其他高优先级的网络设备，即使网关设置正确，所有的互联网流量仍然会经过PoisonTap。

[![](https://p5.ssl.qhimg.com/t019257e42afbdc2a45.gif)](https://p5.ssl.qhimg.com/t019257e42afbdc2a45.gif)

**Cookie嗅探**

1. 只要Web浏览器能够在后台运行，其中的一个Web页面就可以在后台通过AJAX或动态脚本/iframe标签发送HTTP请求。

2. 此时，因为所有的流量都会流经PoisonTap设备，PoisonTap就可以利用DNS欺骗来返回它自身的地址，从而让所有的HTTP请求都发送至PoisonTap的Web服务器中（[Node.js](https://nodejs.org/)）。

3. 当Web服务器接收到HTTP请求之后，PoisonTap将会返回一段可以被解析为HTML或JavaScript的响应数据，大多数浏览器都可以正确地解析这类返回数据。

4. 返回的HTML或JS将会生成很多带有“hidden”属性的iframe，每一个iframe都与Alexa排名前一百万的网站域名有关。

-网站的“X-Frame-Options”安全机制都会被绕过，因为PoisonTap现在就是HTTP服务器，它可以选择发送至客户端的HTTP header。

-此时，HTTP cookie会被浏览器发送至已被PoisonTap劫持的“公共IP地址”，而PoisonTap就可以记录下用户的cookie和身份验证信息了。

-“HttpOnly”（cookie安全保护机制）已经被绕过了。

-跨域资源共享和同源策略也已经被绕过了。

-因为我们捕捉到的是cookie，而不是用户的凭证数据，因此网站所采用的双因素或多因素身份验证也会被绕过，因为攻击者可以使用cookie来进行登录。这是因为我们并没有调用网站的登录功能，我们只是继续进行着一个已经存在的登录会话，这是不会触发双因素身份验证的。

-如果服务器使用的是HTTPS，但cookie没有设置[Secure标签](https://www.owasp.org/index.php/SecureFlag)的话，HTTPS保护机制仍然会被绕过，而cookie数据依然会被发送至PoisonTap。

[![](https://p0.ssl.qhimg.com/t015c1d2d4909f75f3f.gif)](https://p0.ssl.qhimg.com/t015c1d2d4909f75f3f.gif)

**远程访问Web后门**

1. 当PoisonTap生成了大量iframe之后，它会迫使浏览器加载这些iframe。此时它们就不是空白页面了，而是HTML+JavaScript的Web后门。

2. 因为PoisonTap可以对这些后门进行缓存，此时这些后门也就相当于跟网站进行了绑定。这样一来，攻击者就可以使用这些网站cookie来发起“同源”请求了。

-比如说，当http://nfl.com/PoisonTap这个iframe被加载之后，Poisontap将会接收到这个网络流量，然后通过Node服务器对这个请求进行响应。

3. 此时，用户收到的响应数据其实就是HTML与JavaScript的组合数据，它们将会生成一个持久化的WebSocket。

[![](https://p3.ssl.qhimg.com/t0149d0d58084129a73.png)](https://p3.ssl.qhimg.com/t0149d0d58084129a73.png)

**内部路由后门&amp;远程访问**

1. PoisonTap无法劫持的一种网络就是真实网络接口中的局域网子网。比如说，如果用户WiFi的子网为192.168.0.x，那么这个网络就不会受PoisonTap影响。但是…

2. Poisontap可以强迫主机缓存一个Web后门，尤其是当目标路由的IP地址后面加上“.ip.samy.pl”之后（例如“192.168.0.1.ip.samy.pl”），此时将会产生持久化的DNS rebinding攻击。

3. DNS pinning和DNS rebinding将会被绕过。

4. 现在后门已经被缓存至了http://192.168.0.1.ip.samy.pl/PoisonTap。这也就意味着，如果我们通过Web后门在一个iframe中远程加载http://192.168.0.1.ip.samy.pl/PoisonTap的话，我们就可以在内部路由中执行任意的AJAX GET/POST请求了。

[![](https://p2.ssl.qhimg.com/t01f9cad24820dba077.png)](https://p2.ssl.qhimg.com/t01f9cad24820dba077.png)

**其他功能**

1. 除此之外，PoisonTap还可以修改大量常见的CDN文件，它会在正确的代码后面添加一个后门。这样一来，当目标网站加载了受感染的CDN文件之后，攻击者就可以获取到目标的远程访问权了。

2. 因为后门会被安装在每一个域中，所以攻击者就可以让浏览器来发送“同源”请求了（AJAX GET/POST）。

[![](https://p4.ssl.qhimg.com/t013a0941ab993f31bc.png)](https://p4.ssl.qhimg.com/t013a0941ab993f31bc.png)

<br>

**针对PoisonTap的缓解方案**

**服务器端的安全建议**

如果你运行着一台Web服务器，那么你可以采用以下几种简单的方法来保证服务器的安全：

1. 使用HTTPS，至少要在处理身份验证数据的时候使用HTTPS；

2. 确保开启了cookie的Secure标签，以防止HTTPS cookie的数据发生泄漏；

3. 当你需要加载远程JavaScript资源时，使用[Subresource Integrity](https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity%E2%80%98)（子资源完整性）标签。

4. 使用[HSTS](https://www.wikiwand.com/en/HTTP_Strict_Transport_Security)来防止HTTPS遭到攻击

**桌面端的安全建议**

1. 在你每次离开电脑时，关闭你的浏览器；

2. 禁用你的USB或Thunderbolt接口；

3. 经常清理浏览器的缓存数据；

4. 对于数据存储介质采用全盘加密，如果它具备休眠模式，则应该开启该模式；

5. 在不使用电脑时，让电脑进入休眠状态而不是睡眠状态，在休眠状态中，电脑中所有的进程都将停止工作，安全性更高；
