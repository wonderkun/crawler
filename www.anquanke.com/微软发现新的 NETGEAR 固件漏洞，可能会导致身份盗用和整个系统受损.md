> 原文链接: https://www.anquanke.com//post/id/246028 


# 微软发现新的 NETGEAR 固件漏洞，可能会导致身份盗用和整个系统受损


                                阅读量   
                                **26668**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者microsoft，文章来源：microsoft.com
                                <br>原文地址：[https://www.microsoft.com/security/blog/2021/06/30/microsoft-finds-new-netgear-firmware-vulnerabilities-that-could-lead-to-identity-theft-and-full-system-compromise/](https://www.microsoft.com/security/blog/2021/06/30/microsoft-finds-new-netgear-firmware-vulnerabilities-that-could-lead-to-identity-theft-and-full-system-compromise/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01d92e67790a840f68.jpg)](https://p2.ssl.qhimg.com/t01d92e67790a840f68.jpg)



安全解决方案的不断改进迫使攻击者探索危及系统的替代方法。在操作系统以内或者之外的通过VPN设备和其他面向互联网的系统发起固件攻击和勒索软件攻击数量在不断增加案例，这些攻击会变得越来越常见，用户必须确保运行硬件类路由器中固件的安全，我们最近在 NetGear DGN2200v1系列路由器中发现了可能危及网络安全的漏洞。<br>
在我们的研究中，我们解开了路由器的固件，发现了三个可以被利用的漏洞，我们通过微软安全漏洞研究中心(MSVR)的协同漏洞披露给NetGear我们的发现，并且与NetGear安全团队密切合作，在保持向后兼容性的同时提供缓解这些问题的建议。关键的安全问题(CVSS评分:7.1 – 9.4)已被NETGEAR修复。关于DGN2200v1上的多个HTTPd认证漏洞，请参阅NETGEAR的安全咨询。



## 获取和解压固件

固件可从供应商的网站上获得，这使我们更容易获得副本进行检查。它是一个简单的 .zip 文件，包含发行说明 (.html) 和固件映像本身（.chk 文件）。在 .chk 文件上运行binwalk最终提取了文件系统 ( squashfs)。

[![](https://p4.ssl.qhimg.com/t017155319a44e6a90b.png)](https://p4.ssl.qhimg.com/t017155319a44e6a90b.png)

路由器固件文件系统本身是一个标准的 Linux 根文件系统，并添加了一些小功能。我们关心和研究有以下几点
1. /www — 包含html页面和.gif图片
1. /usr/sbin – 包含 NETGEAR 的各种自定义二进制文件，包括 HTTPd、FTPC 等
由于我们看到异常通信使用 httpd 服务的标准端口，因此我们将重点放在 httpd 上。httpd 本身是一个 32 位大端 MIPS ELF，针对 uClibc (嵌入式设备的标准 libc）编译，似乎整个服务器端逻辑 (CGI) 都被编译到 httpd 中。

[![](https://p0.ssl.qhimg.com/t0179aa2331ed43b057.png)](https://p0.ssl.qhimg.com/t0179aa2331ed43b057.png)



## 探索

在探索嵌入式web服务时，首先要考虑以下几个问题
1. Web 服务是否显示一些未经身份验证的页面？如果是这样，他们是如何治理的？
1. Web 服务如何执行身份验证？
1. Web服务是否正确处理请求（即是否存在内存损坏错误）？
1. Web 服务是否实施了某些安全措施，例如（反）跨站点请求伪造令牌或内容安全策略？
为了回答这些问题，我们对 httpd 二进制文件进行了静态分析，并通过运行 QEMU（一个开源模拟器）对固件进行仿真模拟，另外使用了hook（例如 NVRAM getter 和 setter）进行了一些动态分析。



## DGN 2200V1路由器中存在的漏洞

### <a class="reference-link" name="%E7%BB%95%E8%BF%87%E8%BA%AB%E4%BB%BD%E9%AA%8C%E8%AF%81%E8%AE%BF%E9%97%AE%E8%B7%AF%E7%94%B1%E5%99%A8%E7%AE%A1%E7%90%86%E7%95%8C%E9%9D%A2"></a>绕过身份验证访问路由器管理界面

在检查 httpd 如何规定哪些页面应该在没有身份验证的情况下提供时，我们发现了以下伪代码：

[![](https://p2.ssl.qhimg.com/t01d2bce37a46c94bad.png)](https://p2.ssl.qhimg.com/t01d2bce37a46c94bad.png)

这些代码是httpd中的第一个页面处理代码，它会自动允许一些页面，例如form.css或者func.js，正常来说，这些设置并没有问题，但是异常点在于NetGear使用strstr函数来检查是否有“.jpg”“.gif”或者“ess_“字符串，用来匹配整个 url 。<br>
因此我们可以使用GET 方式在URL中带有strstr检查的字符串（如 “?.gif” ）来访问设备的任意界面，其中包括身份验证的界面，使用如下

`https://ip/WAN_wan.htm?pic.gif`

就可以成功绕过身份验证访问路由器管理界面了。

### <a class="reference-link" name="%E9%80%9A%E8%BF%87%E5%8A%A0%E5%AF%86%E4%BE%A7%E4%BF%A1%E9%81%93%E6%94%BB%E5%87%BB%E6%8E%A8%E6%96%AD%E8%B7%AF%E7%94%B1%E5%99%A8%E5%87%AD%E8%AF%81"></a>通过加密侧信道攻击推断路由器凭证

在这个阶段，我们已经完全控制了路由器管理界面，但是我们继续研究身份验证本身是如何实现的。<br>
我们注意到httpd 组件对http界面进行基础认证，需要将username和password 使用base64来进行编译，然后在http header中发送，最后在路由器内存中保存的用户名和密码进行验证，路由器将这些信息存储在NVRAM中。<br>
在我们检查身份验证的过程中，我们发现了一种可以让攻击者获取正确凭据的旁道攻击：

[![](https://p0.ssl.qhimg.com/t015a053b11d303d91a.png)](https://p0.ssl.qhimg.com/t015a053b11d303d91a.png)

这里要注意，username 和 password 是使用strcmp来进行比较的，strcmp 在 libc 中的实现是通过逐个字符比较直到观察到 NUL 终止符或直到发生不匹配来工作。

攻击者可以通过测量失败所需的时间来利用后者。例如，在测量第一个字符的次数时，我们得到如下图：

[![](https://p0.ssl.qhimg.com/t0169d609fd96f73667.png)](https://p0.ssl.qhimg.com/t0169d609fd96f73667.png)

这表示第一个字符是“n”。攻击者可以重复此过程（“na”、“nb”、“nc”等）以获取第二个字符，直到泄露整个用户名和密码。

我们向 NETGEAR 建议他们可以通过执行基于 XOR 的内存比较来避免此类攻击，例如：

[![](https://p1.ssl.qhimg.com/t01a5e40db0f3841526.png)](https://p1.ssl.qhimg.com/t01a5e40db0f3841526.png)

即使字节不匹配，该功能也会继续。类似的方法可以在加密安全库中看到，例如OpenSSL 的 CRYPTO_memcmp。

### <a class="reference-link" name="%E6%A3%80%E7%B4%A2%E5%AD%98%E5%82%A8%E5%9C%A8%E8%AE%BE%E5%A4%87%E4%B8%AD%E7%9A%84%E5%AF%86%E9%92%A5"></a>检索存储在设备中的密钥

当完成身份验证绕过漏洞之后，我们仍然想看看是否可以利用其他现有的漏洞来恢复路由器使用的username和密码，因为我们决定使用路由器的配置备份\恢复功能。<br>
我们可以使用身份绕过获取文件：<br>`hxxp://router_addr:8080/NETGEAR_DGN2200[.]cfg?pic[.]gif.`<br>
这个文件具有高熵，这表明它已被加密，我们无法直接读取内容，并且binwalk也没有任何结果。

[![](https://p4.ssl.qhimg.com/t0113a0e1fde52a0e11.png)](https://p4.ssl.qhimg.com/t0113a0e1fde52a0e11.png)

当我们对“备份\恢复“的功能进行逆向后，我们的问题被解决了。

[![](https://p1.ssl.qhimg.com/t01868c478bef77adc1.png)](https://p1.ssl.qhimg.com/t01868c478bef77adc1.png)

可以看到文件内容是使用 “NtgrBak”的密钥进行DES加密。因此也可以通过这种方式来获取存储在NVRAM中的密码。



## 拓展

### <a class="reference-link" name="Ex6100v2%20%E5%9B%BA%E4%BB%B6%E5%88%86%E6%9E%90"></a>Ex6100v2 固件分析

看完这边漏洞分析文章之后，根据以往对Netgear固件分析中，发现这种情况存在许多版本的固件中，于是我翻出了实验室的NetGear Ex6100v2 路由设备，下载到对应版本的固件，然后对固件进行解包分析。<br>
根据/etc/init.d/rcS文件中的内容,找到uhttpd 的组件（uHTTPd 是一个 OpenWrt/LUCI 开发者从头编写的 Web 服务器），可以看到这个固件是使用NX的保护措施。

[![](https://p3.ssl.qhimg.com/t0130ead20ef44d88f9.png)](https://p3.ssl.qhimg.com/t0130ead20ef44d88f9.png)

在我分析/etc/boot文件中，看到如下内容，也可以证明这是一个OpenWRT类型的web组件。

[![](https://p2.ssl.qhimg.com/t01a15909844cafc3be.png)](https://p2.ssl.qhimg.com/t01a15909844cafc3be.png)

在uhttpd组件的逆向中，看到了如下的伪代码

[![](https://p5.ssl.qhimg.com/t0100e5b6bb8191d971.png)](https://p5.ssl.qhimg.com/t0100e5b6bb8191d971.png)

本来以为这也是一个存在身份验证绕过的固件，但是继续查看引用，看到这个函数需要在用户认证之后才会触发。

[![](https://p0.ssl.qhimg.com/t012f675ee9d7d2bca3.png)](https://p0.ssl.qhimg.com/t012f675ee9d7d2bca3.png)

于是在经过实际的测试，确实是需要在经过认证后才能触发漏洞（鸡肋）
